import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import src.collect_news_twitter as twitter_collector
from src.collect_news_twitter import _parse_api_post, _parse_entry


class TwitterCollectorTests(unittest.TestCase):
    def test_official_team_post_is_relevant_without_team_name_in_text(self):
        entry = SimpleNamespace(
            title="Yeni transferimiz kulubumuze hos geldi",
            link="https://nitter.poast.org/Besiktas/status/1",
        )
        account = {
            "handle": "Besiktas",
            "team": "BEŞİKTAŞ A.Ş.",
            "type": "official",
        }

        result = _parse_entry(entry, account)

        self.assertTrue(result["super_lig_relevant"])
        self.assertEqual(result["link"], "https://x.com/Besiktas/status/1")

    def test_x_api_official_post_is_normalized_for_analysis(self):
        account = {
            "handle": "GalatasaraySK",
            "team": "GALATASARAY A.Ş.",
            "type": "official",
        }

        result = _parse_api_post(
            {
                "id": "42",
                "text": "Yeni transferimiz ile anlaşma sağlandı.",
                "created_at": "2026-05-25T12:00:00.000Z",
            },
            account,
        )

        self.assertEqual(result["link"], "https://x.com/GalatasaraySK/status/42")
        self.assertEqual(result["source_type"], "twitter")
        self.assertTrue(result["super_lig_relevant"])
        self.assertIn("transfer", result["categories"])

    def test_missing_x_credentials_still_writes_status_snapshot(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            original_raw = twitter_collector.RAW_DIR
            original_processed = twitter_collector.PROCESSED_DIR
            twitter_collector.RAW_DIR = root / "raw"
            twitter_collector.PROCESSED_DIR = root / "processed"
            twitter_collector.PROCESSED_DIR.mkdir()
            try:
                with (
                    patch.object(twitter_collector, "load_settings", return_value=SimpleNamespace(x_bearer_token=None)),
                    patch(
                        "sys.argv",
                        ["collect_news_twitter", "--provider", "x_api", "--output-prefix", "twitter_unit"],
                    ),
                ):
                    twitter_collector.main()
                payload = json.loads((twitter_collector.PROCESSED_DIR / "twitter_unit.json").read_text(encoding="utf-8"))
            finally:
                twitter_collector.RAW_DIR = original_raw
                twitter_collector.PROCESSED_DIR = original_processed

        self.assertEqual(payload["collection_status"], "MISSING_CREDENTIALS")
        self.assertEqual(payload["provider"], "x_api")
        self.assertEqual(payload["official_club_accounts"], 18)
        self.assertEqual(payload["total_tweets"], 0)


if __name__ == "__main__":
    unittest.main()
