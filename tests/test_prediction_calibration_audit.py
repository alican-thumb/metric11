import unittest

from src.build_prediction_calibration_audit import (
    _wilson_interval,
    confidence_policy,
    draw_thresholds,
    probability_bins,
    selective_policies,
)


def row(top: float, actual: str, predicted: str = "home") -> dict:
    remainder = (1 - top) / 2
    probabilities = {
        "home_win_probability": top if predicted == "home" else remainder,
        "draw_probability": top if predicted == "draw" else remainder,
        "away_win_probability": top if predicted == "away" else remainder,
    }
    return {**probabilities, "actual": actual, "predicted": predicted, "correct": actual == predicted}


class PredictionCalibrationAuditTests(unittest.TestCase):
    def test_wilson_interval_contains_observed_accuracy(self):
        low, high = _wilson_interval(6, 10)
        self.assertLess(low, 0.6)
        self.assertGreater(high, 0.6)

    def test_probability_bins_do_not_drop_matches(self):
        rows = [row(0.38, "home"), row(0.44, "away"), row(0.57, "home")]
        self.assertEqual(sum(item["matches"] for item in probability_bins(rows)), len(rows))

    def test_selective_policy_trades_coverage_for_threshold(self):
        rows = [row(0.41, "home"), row(0.51, "home"), row(0.62, "away", "away")]
        policies = selective_policies(rows)
        self.assertGreater(policies[0]["coverage"], policies[-1]["coverage"])

    def test_draw_threshold_reports_precision_and_recall(self):
        rows = [row(0.34, "draw", "draw"), row(0.31, "home", "draw"), row(0.6, "home")]
        threshold = next(item for item in draw_thresholds(rows) if item["minimum_draw_probability"] == 0.3)
        self.assertEqual(threshold["flagged_matches"], 2)
        self.assertEqual(threshold["draw_hits"], 1)
        self.assertEqual(threshold["precision"], 0.5)

    def test_medium_band_can_be_downgraded_without_changing_prediction(self):
        summary = {
            "draw_recall": 0.2,
            "confidence_breakdown": {
                "HIGH": {"matches": 30, "accuracy": 0.63, "calibration_gap": 0.02},
                "MEDIUM": {"matches": 25, "accuracy": 0.29, "calibration_gap": -0.17},
            },
        }
        policy = confidence_policy(summary)
        self.assertEqual(policy["high"]["status"], "PUBLISH")
        self.assertEqual(policy["medium"]["status"], "NO_STRONG_PICK")
        self.assertEqual(policy["draw"]["status"], "WEAK")


if __name__ == "__main__":
    unittest.main()
