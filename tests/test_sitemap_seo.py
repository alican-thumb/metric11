import unittest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from src import build_sitemap


class SitemapSeoTests(unittest.TestCase):
    @patch.object(build_sitemap, "_match_page_urls", return_value=[])
    def test_scenario_page_is_in_sitemap(self, _match_urls):
        sitemap = build_sitemap.build_sitemap()

        self.assertIn(
            "https://metric11.com/super-lig-sampiyonluk-senaryolari-2026-27.html",
            sitemap,
        )

    @patch.object(build_sitemap, "_match_page_urls", return_value=[])
    def test_frozen_archive_does_not_claim_fresh_lastmod(self, _match_urls):
        sitemap = build_sitemap.build_sitemap()
        archive_block = sitemap.split(
            "https://metric11.com/prediction_backtest_dashboard_2025_2026.html",
            maxsplit=1,
        )[1].split("</url>", maxsplit=1)[0]

        self.assertNotIn("<lastmod>", archive_block)
        self.assertIn("<changefreq>yearly</changefreq>", archive_block)

    @patch.object(build_sitemap, "_match_page_urls", return_value=[])
    def test_live_page_has_current_lastmod(self, _match_urls):
        sitemap = build_sitemap.build_sitemap()
        live_block = sitemap.split(
            "https://metric11.com/super-lig-sampiyonluk-senaryolari-2026-27.html",
            maxsplit=1,
        )[1].split("</url>", maxsplit=1)[0]

        self.assertIn("<lastmod>", live_block)
        self.assertIn("<changefreq>daily</changefreq>", live_block)

    def test_undated_future_pages_are_excluded_from_sitemap(self):
        index = {
            "weeks": [
                {"path": "week-live.html", "played": False, "indexable": True},
                {"path": "week-undated.html", "played": False, "indexable": False},
            ],
            "matches": [
                {"path": "match-live.html", "played": False, "indexable": True, "date_time": "21.11.2026 16:00"},
                {"path": "match-undated.html", "played": False, "indexable": False, "date_time": None},
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "match_pages_index_2026_2027.json").write_text(json.dumps(index), encoding="utf-8")
            with patch.object(build_sitemap, "PROCESSED_DIR", root):
                urls = "\n".join(build_sitemap._match_page_urls("2026-11-11"))

        self.assertIn("week-live.html", urls)
        self.assertIn("match-live.html", urls)
        self.assertNotIn("week-undated.html", urls)
        self.assertNotIn("match-undated.html", urls)


if __name__ == "__main__":
    unittest.main()
