import unittest
from unittest.mock import Mock, patch

from src.collect_official_club_news import collect_sources, extract_candidate_links, fetch_article


class OfficialClubNewsCollectorTests(unittest.TestCase):
    def test_extract_candidate_links_keeps_only_official_signal_links(self):
        html = """
        <a href="/haber/transfer-imza">Yeni transferimiz imzayı attı</a>
        <a href="/haber/antrenman">Takım antrenmanı tamamladı</a>
        <a href="https://other.test/haber/transfer">Transfer haberi</a>
        """

        result = extract_candidate_links(html, "https://club.test/haberler")

        self.assertEqual(result, [("Yeni transferimiz imzayı attı", "https://club.test/haber/transfer-imza")])

    @patch("src.collect_official_club_news.requests.get")
    def test_official_article_has_verified_source_metadata(self, request_get):
        response = Mock()
        response.text = """
        <html><h1>Ali Ornek kulubumuze transfer oldu</h1>
        <time datetime="2026-05-25T10:00:00+03:00"></time>
        <p>Profesyonel futbolcu Ali Ornek ile sozlesme imzalandi.</p></html>
        """
        response.raise_for_status.return_value = None
        request_get.return_value = response

        article = fetch_article(
            {"team": "BEŞİKTAŞ A.Ş.", "name": "Beşiktaş Resmi Web", "url": "https://club.test"},
            "",
            "https://club.test/haber/ali-ornek-transfer",
        )

        self.assertEqual(article["source_type"], "official_club")
        self.assertEqual(article["account_type"], "official")
        self.assertEqual(article["related_team"], "BEŞİKTAŞ A.Ş.")
        self.assertEqual(article["published_at"], "2026-05-25T10:00:00+03:00")
        self.assertIn("transfer", article["categories"])

    @patch("src.collect_official_club_news.fetch_source")
    def test_source_failure_is_kept_in_coverage_snapshot(self, fetch_source):
        fetch_source.side_effect = [([], []), RuntimeError("site unavailable")]
        sources = [
            {"team": "A", "name": "A Resmi", "url": "https://a.test"},
            {"team": "B", "name": "B Resmi", "url": "https://b.test"},
        ]

        payload = collect_sources(sources, max_items=10, delay_seconds=0)

        self.assertEqual(payload["collection_status"], "PARTIAL_SUCCESS")
        self.assertEqual(payload["successful_sources"], 1)
        self.assertIn("site unavailable", payload["sources"][1]["error"])


if __name__ == "__main__":
    unittest.main()
