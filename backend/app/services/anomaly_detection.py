
import threading
from collections import deque
from datetime import datetime, timezone
from statistics import mean, pstdev
from threading import RLock
from uuid import uuid4

from app.services.traffic_history import traffic_history


class TrafficAnomalyDetector:
    """
    Detect unusual bandwidth peaks using historical traffic samples.

    The detector analyzes total, incoming, and outgoing bandwidth.
    It does not classify an anomaly as a DDoS attack.
    """

    def __init__(
        self,
        baseline_window: int = 60,
        min_baseline_samples: int = 10,
        standard_deviation_factor: float = 3.0,
        minimum_peak_factor: float = 2.5,
        minimum_threshold_mbps: float = 1.0,
        cooldown_seconds: int = 30,
        max_alerts: int = 500,
    ):
        self.baseline_window = baseline_window
        self.min_baseline_samples = min_baseline_samples
        self.standard_deviation_factor = standard_deviation_factor
        self.minimum_peak_factor = minimum_peak_factor
        self.minimum_threshold_mbps = minimum_threshold_mbps
        self.cooldown_seconds = cooldown_seconds

        self._alerts = deque(maxlen=max_alerts)
        self._last_alert_times = {}
        self._last_processed_timestamp = None

        self._lock = RLock()

        self._worker_thread = None
        self._stop_event = threading.Event()
        self._is_running = False
        self._last_error = None

    @staticmethod
    def _parse_timestamp(value):
        if isinstance(value, datetime):
            return value

        if not isinstance(value, str):
            return None

        try:
            return datetime.fromisoformat(
                value.replace("Z", "+00:00")
            )
        except ValueError:
            return None

    def _calculate_threshold(self, baseline_values):
        baseline_mean = mean(baseline_values)

        standard_deviation = (
            pstdev(baseline_values)
            if len(baseline_values) > 1
            else 0.0
        )

        statistical_threshold = (
            baseline_mean
            + self.standard_deviation_factor
            * standard_deviation
        )

        relative_threshold = (
            baseline_mean * self.minimum_peak_factor
        )

        threshold = max(
            statistical_threshold,
            relative_threshold,
            self.minimum_threshold_mbps,
        )

        return baseline_mean, threshold

    def _is_in_cooldown(self, metric, now):
        last_alert = self._last_alert_times.get(metric)

        if last_alert is None:
            return False

        elapsed = (now - last_alert).total_seconds()

        return elapsed < self.cooldown_seconds

    def _create_alert(
        self,
        metric,
        observed_value,
        baseline_value,
        threshold,
        timestamp,
    ):
        now = datetime.now(timezone.utc)

        if self._is_in_cooldown(metric, now):
            return None

        severity = (
            "high"
            if observed_value >= threshold * 2
            else "medium"
        )

        alert = {
            "id": str(uuid4()),
            "type": "bandwidth_peak",
            "metric": metric,
            "severity": severity,
            "message": (
                f"Unusual {metric} bandwidth peak detected."
            ),
            "timestamp": timestamp,
            "observed_mbps": round(observed_value, 6),
            "baseline_mbps": round(baseline_value, 6),
            "threshold_mbps": round(threshold, 6),
        }

        self._alerts.append(alert)
        self._last_alert_times[metric] = now

        return alert

    def analyze_latest_sample(self):
        samples = traffic_history.get_history(
            limit=self.baseline_window + 1
        )

        if len(samples) < self.min_baseline_samples + 1:
            return {
                "analyzed": False,
                "reason": "Not enough historical samples.",
                "new_alerts": [],
            }

        valid_samples = []

        for sample in samples:
            timestamp = self._parse_timestamp(
                sample.get("timestamp")
            )

            bandwidth = sample.get("bandwidth", {})

            if timestamp is None or not isinstance(bandwidth, dict):
                continue

            valid_samples.append((timestamp, sample))

        valid_samples.sort(key=lambda item: item[0])

        if len(valid_samples) < self.min_baseline_samples + 1:
            return {
                "analyzed": False,
                "reason": "Not enough valid historical samples.",
                "new_alerts": [],
            }

        latest_timestamp, latest_sample = valid_samples[-1]

        with self._lock:
            if (
                self._last_processed_timestamp is not None
                and latest_timestamp <= self._last_processed_timestamp
            ):
                return {
                    "analyzed": False,
                    "reason": "Latest sample was already processed.",
                    "new_alerts": [],
                }

            self._last_processed_timestamp = latest_timestamp

            previous_samples = valid_samples[:-1]
            previous_samples = previous_samples[
                -self.baseline_window:
            ]

            metrics = [
                "total_mbps",
                "incoming_mbps",
                "outgoing_mbps",
            ]

            new_alerts = []

            for metric in metrics:
                baseline_values = []

                for _, sample in previous_samples:
                    value = sample.get(
                        "bandwidth", {}
                    ).get(metric)

                    if (
                        isinstance(value, (int, float))
                        and value >= 0
                    ):
                        baseline_values.append(float(value))

                if len(baseline_values) < self.min_baseline_samples:
                    continue

                observed_value = latest_sample.get(
                    "bandwidth", {}
                ).get(metric)

                if not isinstance(observed_value, (int, float)):
                    continue

                baseline_mean, threshold = (
                    self._calculate_threshold(baseline_values)
                )

                if observed_value <= threshold:
                    continue

                alert = self._create_alert(
                    metric=metric,
                    observed_value=float(observed_value),
                    baseline_value=baseline_mean,
                    threshold=threshold,
                    timestamp=latest_timestamp.isoformat(),
                )

                if alert is not None:
                    new_alerts.append(alert)

            return {
                "analyzed": True,
                "timestamp": latest_timestamp.isoformat(),
                "new_alerts": new_alerts,
            }

    def start(self):
        with self._lock:
            if self._is_running:
                return self.get_status()

            self._stop_event.clear()
            self._is_running = True
            self._last_error = None

            self._worker_thread = threading.Thread(
                target=self._worker_loop,
                name="NetScope-Anomaly-Worker",
                daemon=True,
            )

            self._worker_thread.start()

            return self.get_status()

    def _worker_loop(self):
        while not self._stop_event.is_set():
            try:
                self.analyze_latest_sample()
                self._last_error = None

            except Exception as error:
                self._last_error = str(error)

            self._stop_event.wait(1)

    def stop(self):
        with self._lock:
            if not self._is_running:
                return self.get_status()

            self._stop_event.set()
            worker = self._worker_thread

        if worker and worker.is_alive():
            worker.join(timeout=3)

        with self._lock:
            self._is_running = False
            self._worker_thread = None

            return self.get_status()

    def get_alerts(self, limit=50):
        with self._lock:
            return list(self._alerts)[-limit:][::-1]

    def get_status(self):
        with self._lock:
            return {
                "is_running": self._is_running,
                "total_alerts": len(self._alerts),
                "baseline_window": self.baseline_window,
                "min_baseline_samples": self.min_baseline_samples,
                "cooldown_seconds": self.cooldown_seconds,
                "last_processed_timestamp": (
                    self._last_processed_timestamp.isoformat()
                    if self._last_processed_timestamp
                    else None
                ),
                "last_error": self._last_error,
            }


anomaly_detector = TrafficAnomalyDetector()
