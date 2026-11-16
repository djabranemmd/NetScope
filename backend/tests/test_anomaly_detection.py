
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from app.services.anomaly_detection import TrafficAnomalyDetector
from app.services.traffic_history import traffic_history


class TestTrafficAnomalyDetector(unittest.TestCase):

    def setUp(self):
        self.detector = TrafficAnomalyDetector(
            baseline_window=60,
            min_baseline_samples=10,
            standard_deviation_factor=3.0,
            minimum_peak_factor=2.5,
            minimum_threshold_mbps=1.0,
            cooldown_seconds=30,
        )

    def create_samples(
        self,
        sample_count=11,
        peak=False,
    ):
        """
        Generate isolated synthetic history samples.

        These samples are only for unit testing.
        They are not real network traffic.
        """

        base_time = datetime.now(timezone.utc)

        samples = []

        for index in range(sample_count):
            incoming = 0.1
            outgoing = 0.05
            total = incoming + outgoing

            if peak and index == sample_count - 1:
                incoming = 2.0
                outgoing = 0.1
                total = incoming + outgoing

            samples.append({
                "timestamp": (
                    base_time + timedelta(seconds=index)
                ).isoformat(),
                "bandwidth": {
                    "total_mbps": total,
                    "incoming_mbps": incoming,
                    "outgoing_mbps": outgoing,
                },
            })

        return samples

    def test_detect_bandwidth_peak(self):
        samples = self.create_samples(peak=True)

        with patch.object(
            traffic_history,
            "get_history",
            return_value=samples,
        ):
            result = self.detector.analyze_latest_sample()

        self.assertTrue(result["analyzed"])
        self.assertGreater(
            len(result["new_alerts"]),
            0,
        )

        detected_metrics = {
            alert["metric"]
            for alert in result["new_alerts"]
        }

        self.assertIn("incoming_mbps", detected_metrics)

    def test_normal_traffic_creates_no_alerts(self):
        samples = self.create_samples(peak=False)

        with patch.object(
            traffic_history,
            "get_history",
            return_value=samples,
        ):
            result = self.detector.analyze_latest_sample()

        self.assertTrue(result["analyzed"])
        self.assertEqual(result["new_alerts"], [])

    def test_same_sample_is_not_processed_twice(self):
        samples = self.create_samples(peak=True)

        with patch.object(
            traffic_history,
            "get_history",
            return_value=samples,
        ):
            first_result = (
                self.detector.analyze_latest_sample()
            )

            second_result = (
                self.detector.analyze_latest_sample()
            )

        self.assertTrue(first_result["analyzed"])
        self.assertFalse(second_result["analyzed"])

        self.assertEqual(
            second_result["reason"],
            "Latest sample was already processed.",
        )

    def test_cooldown_prevents_repeated_alerts(self):
        timestamp = datetime.now(
            timezone.utc
        ).isoformat()

        first_alert = self.detector._create_alert(
            metric="incoming_mbps",
            observed_value=2.0,
            baseline_value=0.1,
            threshold=1.0,
            timestamp=timestamp,
        )

        second_alert = self.detector._create_alert(
            metric="incoming_mbps",
            observed_value=2.5,
            baseline_value=0.1,
            threshold=1.0,
            timestamp=timestamp,
        )

        self.assertIsNotNone(first_alert)
        self.assertIsNone(second_alert)

        self.assertEqual(
            len(self.detector.get_alerts()),
            1,
        )


if __name__ == "__main__":
    unittest.main()
