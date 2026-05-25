import unittest
from types import SimpleNamespace

from src.collect_news_twitter import _parse_entry


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


if __name__ == "__main__":
    unittest.main()
