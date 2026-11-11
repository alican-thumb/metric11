import unittest

from src.build_growth_measurement_report import build_report


def snapshot(clicks=10, impressions=100, indexed=20, captured_at="2026-11-01T00:00:00+03:00"):
    return {
        "captured_at": captured_at,
        "performance": {"clicks": clicks, "impressions": impressions, "ctr": clicks / impressions, "average_position": 9.5},
        "indexing": {
            "indexed": indexed,
            "not_indexed": 30,
            "reasons": {"discovered_not_indexed": 25, "crawled_not_indexed": 5},
        },
        "queries": [{"query": "tahmini kadro", "clicks": 0, "impressions": 6}],
        "pages": [{"url": "https://metric11.com/kadro", "clicks": 0, "impressions": 12}],
        "vercel_analytics": {"status": "confirmation_required"},
    }


class GrowthMeasurementReportTests(unittest.TestCase):
    def test_builds_diagnosis_without_inventing_vercel_metrics(self):
        report = build_report([snapshot()])

        self.assertEqual(report["status"], "ready")
        self.assertIsNone(report["vercel_analytics"].get("pageviews"))
        self.assertIn("tahmini kadro", report["actions"][3])
        self.assertTrue(any("interaktif" in action for action in report["actions"]))

    def test_calculates_snapshot_delta(self):
        earlier = snapshot(clicks=10, impressions=100, indexed=20)
        current = snapshot(clicks=14, impressions=130, indexed=28, captured_at="2026-11-08T00:00:00+03:00")
        report = build_report([earlier, current])

        self.assertTrue(report["delta"]["available"])
        self.assertEqual(report["delta"]["clicks"], 4)
        self.assertEqual(report["delta"]["impressions"], 30)
        self.assertEqual(report["delta"]["indexed"], 8)

    def test_handles_missing_snapshot(self):
        report = build_report([])

        self.assertEqual(report["status"], "missing_snapshot")


if __name__ == "__main__":
    unittest.main()
