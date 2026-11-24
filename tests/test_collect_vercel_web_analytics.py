import unittest
from unittest.mock import patch
import urllib.error

from src.collect_vercel_web_analytics import collect, normalize_project


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

    @patch("src.collect_vercel_web_analytics.fetch_with_token")
    def test_preserves_last_valid_metrics_when_project_token_loses_access(self, fetch):
        fetch.side_effect = [
            {"query": {"since": "a", "until": "b"}, "data": {"visitors": 10, "pageviews": 20}},
            urllib.error.HTTPError("url", 404, "Not Found", {}, None),
        ]
        previous = {
            "generated_at": "2026-11-23T00:00:00+00:00",
            "projects": [
                {
                    "key": "prediction_game",
                    "domain": "tahmin.metric11.com",
                    "status": "connected",
                    "measurement": {"since": "a", "until": "old"},
                    "visitors": 3,
                    "pageviews": 8,
                }
            ],
        }

        payload = collect("team", token="token", previous=previous)
        prediction = payload["projects"][1]

        self.assertEqual(payload["status"], "partial")
        self.assertEqual(prediction["status"], "stale")
        self.assertEqual(prediction["visitors"], 3)
        self.assertEqual(prediction["error_code"], 404)
        self.assertNotIn("project_id", prediction)

    @patch("src.collect_vercel_web_analytics.fetch_with_token")
    def test_uses_project_specific_token_when_configured(self, fetch):
        fetch.return_value = {"query": {}, "data": {}}

        collect("team", token="main-token", project_tokens={"prediction_game": "prediction-token"})

        self.assertEqual(fetch.call_args_list[0].args[1], "main-token")
        self.assertEqual(fetch.call_args_list[1].args[1], "prediction-token")


if __name__ == "__main__":
    unittest.main()
