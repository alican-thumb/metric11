import unittest
from datetime import datetime, timezone
from types import SimpleNamespace

from src.collect_news_google import SEARCH_QUERIES
from src.collect_news_rss import _is_recent as rss_is_recent
from src.collect_news_telegram import _parse_message


class SupplementalNewsCollectorTests(unittest.TestCase):
    def test_google_queries_cover_all_active_league_clubs(self):
        club_queries = {query for query, category in SEARCH_QUERIES if category == "transfer"}

        self.assertIn("Çorum FK transfer", club_queries)
        self.assertIn("Erzurumspor FK transfer", club_queries)
        self.assertIn("Amedspor transfer", club_queries)
        self.assertIn("Yusuf Günaydın transfer", club_queries)
        self.assertNotIn("Yakın Takip transfer", club_queries)
        self.assertGreaterEqual(len(club_queries), 18)

    def test_telegram_team_channel_is_secondary_signal(self):
        message = SimpleNamespace()
        message.select_one = lambda selector: {
            ".tgme_widget_message_text": _Node("Ali Ornek transferi icin anlasma saglandi."),
            "time": _Node("", {"datetime": "2026-05-25T10:00:00+00:00"}),
            ".tgme_widget_message_date": _Node("", {"href": "https://t.me/channel/1"}),
        }.get(selector)
        message.get = lambda key: None

        result = _parse_message(
            message,
            {
                "handle": "kuluphaberleri",
                "name": "Kulup Haberleri",
                "team": "BEŞİKTAŞ A.Ş.",
                "type": "secondary_signal",
            },
        )

        self.assertEqual(result["account_type"], "secondary_signal")
        self.assertEqual(result["source_type"], "telegram")

    def test_rss_freshness_filter_rejects_old_articles(self):
        now = datetime(2026, 5, 26, tzinfo=timezone.utc)

        self.assertFalse(rss_is_recent("2025-08-16T20:51:53+03:00", now=now))
        self.assertTrue(rss_is_recent("2026-05-25T10:00:00+03:00", now=now))


class _Node:
    def __init__(self, text: str, attrs: dict | None = None):
        self.text = text
        self.attrs = attrs or {}

    def get_text(self, _separator: str, strip: bool = False) -> str:
        return self.text.strip() if strip else self.text

    def get(self, name: str):
        return self.attrs.get(name)

    def __getitem__(self, name: str):
        return self.attrs[name]


if __name__ == "__main__":
    unittest.main()
