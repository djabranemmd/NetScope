
import threading
import time

from collections import deque
from datetime import datetime, timezone

from app.services.packet_capture import capture_engine


class TrafficHistoryService:
    """
    Collect periodic traffic measurements from real capture statistics.

    Bandwidth is calculated using counter differences between samples.
    """

    def __init__(
        self,
        interval_seconds=1,
        max_samples=3600,
    ):
        self.interval_seconds = interval_seconds

        self.history = deque(maxlen=max_samples)

        self.lock = threading.RLock()

        self.stop_event = threading.Event()
        self.worker = None

        self.is_running = False

        self.previous_stats = None
        self.previous_time = None

    def _get_counters(self):
        """Read cumulative counters from the capture engine."""

        status = capture_engine.get_status()
        stats = status["stats"]

        return {
            "total_packets": stats["total_packets"],
            "total_bytes": stats["total_bytes"],

            "incoming_packets": stats["incoming_packets"],
            "incoming_bytes": stats["incoming_bytes"],

            "outgoing_packets": stats["outgoing_packets"],
            "outgoing_bytes": stats["outgoing_bytes"],

            "unknown_direction_packets": (
                stats["unknown_direction_packets"]
            ),

            "unknown_direction_bytes": (
                stats["unknown_direction_bytes"]
            ),
        }

    def start(self):
        """Start periodic traffic history collection."""

        with self.lock:
            if self.is_running:
                return self.get_status()

            self.history.clear()

            self.previous_stats = self._get_counters()
            self.previous_time = time.monotonic()

            self.stop_event.clear()

            self.is_running = True

            self.worker = threading.Thread(
                target=self._collection_loop,
                daemon=True,
                name="NetScope-Traffic-History",
            )

            self.worker.start()

            return self.get_status()

    def _collection_loop(self):
        """Collect traffic measurements periodically."""

        while not self.stop_event.wait(
            self.interval_seconds
        ):
            try:
                self.record_sample()

            except Exception:
                # Keep the collector alive if one sample fails.
                continue

    def record_sample(self):
        """Calculate traffic rates from cumulative counter differences."""

        current_stats = self._get_counters()
        current_time = time.monotonic()

        with self.lock:
            if self.previous_stats is None:
                self.previous_stats = current_stats
                self.previous_time = current_time
                return None

            elapsed = current_time - self.previous_time

            if elapsed <= 0:
                return None

            previous = self.previous_stats

            # Protect against counter resets.
            def calculate_delta(current, old):
                return max(0, current - old)

            total_bytes = calculate_delta(
                current_stats["total_bytes"],
                previous["total_bytes"],
            )

            incoming_bytes = calculate_delta(
                current_stats["incoming_bytes"],
                previous["incoming_bytes"],
            )

            outgoing_bytes = calculate_delta(
                current_stats["outgoing_bytes"],
                previous["outgoing_bytes"],
            )

            total_packets = calculate_delta(
                current_stats["total_packets"],
                previous["total_packets"],
            )

            incoming_packets = calculate_delta(
                current_stats["incoming_packets"],
                previous["incoming_packets"],
            )

            outgoing_packets = calculate_delta(
                current_stats["outgoing_packets"],
                previous["outgoing_packets"],
            )

            unknown_packets = calculate_delta(
                current_stats["unknown_direction_packets"],
                previous["unknown_direction_packets"],
            )

            unknown_bytes = calculate_delta(
                current_stats["unknown_direction_bytes"],
                previous["unknown_direction_bytes"],
            )

            sample = {
                "timestamp": datetime.now(
                    timezone.utc
                ).isoformat(),

                "interval_seconds": round(elapsed, 3),

                "traffic": {
                    "total_bytes": total_bytes,
                    "total_packets": total_packets,

                    "packets_per_second": round(
                        total_packets / elapsed,
                        2,
                    ),
                },

                "bandwidth": {
                    "total_mbps": round(
                        (total_bytes * 8)
                        / elapsed
                        / 1_000_000,
                        6,
                    ),

                    "incoming_mbps": round(
                        (incoming_bytes * 8)
                        / elapsed
                        / 1_000_000,
                        6,
                    ),

                    "outgoing_mbps": round(
                        (outgoing_bytes * 8)
                        / elapsed
                        / 1_000_000,
                        6,
                    ),

                    "unknown_mbps": round(
                        (unknown_bytes * 8)
                        / elapsed
                        / 1_000_000,
                        6,
                    ),
                },

                "directions": {
                    "incoming_packets": incoming_packets,
                    "outgoing_packets": outgoing_packets,
                    "unknown_packets": unknown_packets,
                },
            }

            self.history.append(sample)

            self.previous_stats = current_stats
            self.previous_time = current_time

            return sample

    def stop(self):
        """Stop periodic collection."""

        with self.lock:
            if not self.is_running:
                return self.get_status()

            self.is_running = False
            self.stop_event.set()

            worker = self.worker

        if worker and worker.is_alive():
            worker.join(timeout=3)

        with self.lock:
            self.worker = None

        return self.get_status()

    def get_history(self, limit=60):
        """Return the latest recorded traffic samples."""

        with self.lock:
            return list(self.history)[-limit:]

    def get_status(self):
        """Return history collector status."""

        with self.lock:
            return {
                "is_running": self.is_running,
                "interval_seconds": self.interval_seconds,
                "total_samples": len(self.history),
                "max_samples": self.history.maxlen,
            }


traffic_history = TrafficHistoryService()
