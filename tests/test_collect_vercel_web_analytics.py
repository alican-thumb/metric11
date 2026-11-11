import unittest

from src.collect_vercel_web_analytics import normalize_project


class VercelAnalyticsCollectorTests(unittest.TestCase):
    def test_normalizes_official_count_response(self):
        row = normalize_project(
            {"key": "main", "domain": "metric11.com", "project_id": "project"},
            {
                "query": {"since": "2026-05-25T00:00:00.000Z", "until": "2026-11-12T00:00:00.000Z"},
                "data": {"visitors": 1318, "pageviews": 2873},
            },
        )

        self.assertEqual(row["status"], "connected")
        self.assertEqual(row["visitors"], 1318)
        self.assertEqual(row["pageviews"], 2873)
        self.assertEqual(row["measurement"]["since"], "2026-05-25T00:00:00.000Z")
        self.assertNotIn("project_id", row)


if __name__ == "__main__":
    unittest.main()
