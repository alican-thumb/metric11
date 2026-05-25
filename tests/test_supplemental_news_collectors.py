import unittest
from types import SimpleNamespace

from src.collect_news_google import SEARCH_QUERIES
from src.collect_news_telegram import _parse_message


class SupplementalNewsCollectorTests(unittest.TestCase):
    def test_google_queries_cover_all_active_league_clubs(self):
        club_queries = {query for query, category in SEARCH_QUERIES if category == "transfer"}

        self.assertIn("Çorum FK transfer", club_queries)
        self.assertIn("Erzurumspor FK transfer", club_queries)
        self.assertIn("Amedspor transfer", club_queries)
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


class _Node:
    def __init__(self, text: str, attrs: dict | None = None):
        self.text = text
        self.attrs = attrs or {}

    def get_text(self, _separator: str, strip: bool = False) -> str:
        return self.text.strip() if strip else self.text

    def get(self, name: str):
        return self.attrs.get(name)


if __name__ == "__main__":
    unittest.main()
