import json
import tempfile
import unittest
from pathlib import Path

import src.build_data_catalog as data_catalog


class DataCatalogNewsSourceTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.processed = self.root / "data" / "processed"
        self.manual = self.root / "data" / "manual"
        self.processed.mkdir(parents=True)
        self.manual.mkdir(parents=True)
        self.original_processed_dir = data_catalog.PROCESSED_DIR
        self.original_root_dir = data_catalog.ROOT_DIR
        data_catalog.PROCESSED_DIR = self.processed
        data_catalog.ROOT_DIR = self.root

        self.write_processed("news_rss_latest_2025_2026.json", {"total_articles": 210})
        self.write_processed(
            "news_intelligence_2025_2026.json",
            {
                "analyzed_articles": 58,
                "transfer_signals": 8,
                "transfer_status_counts": {
                    "OFFICIAL": 0,
                    "CORROBORATED": 0,
                    "RUMOR": 0,
                    "REVIEW_REQUIRED": 8,
                },
            },
        )
        self.write_processed(
            "news_official_clubs_latest_2025_2026.json",
            {
                "collection_status": "PARTIAL_SUCCESS",
                "configured_sources": 18,
                "successful_sources": 10,
                "total_articles": 22,
            },
        )

    def tearDown(self):
        data_catalog.PROCESSED_DIR = self.original_processed_dir
        data_catalog.ROOT_DIR = self.original_root_dir
        self.temp_dir.cleanup()

    def write_processed(self, filename, payload):
        (self.processed / filename).write_text(
            json.dumps(payload, ensure_ascii=False),
            encoding="utf-8",
        )

    def test_news_sources_and_verification_state_are_exposed(self):
        catalog = data_catalog.build_catalog()
        sources = {source["type"]: source for source in catalog["sources"]}
        markdown = data_catalog.build_markdown(catalog)

        self.assertIn("210 ham haber; 58 ilgili analiz; 8 transfer iddiası", sources["RSS_NEWS"]["coverage"])
        self.assertEqual(
            sources["OFFICIAL_CLUB_NEWS"]["coverage"],
            "22 duyuru; 10/18 kulüp sitesi erişilebilir; durum=PARTIAL_SUCCESS",
        )
        self.assertEqual(catalog["coverage"]["news_official_articles"], 22)
        self.assertIn("başarılı snapshot henüz yok", sources["X_SOCIAL_SIGNAL"]["coverage"])
        self.assertEqual(catalog["coverage"]["news_twitter_posts"], 0)
        self.assertIn(
            "Transfer haber iddiası: 8 | resmi=0, çoklu kaynak=0, söylenti=0, inceleme gerekli=8",
            markdown,
        )
        self.assertIn("Resmi kulüp web duyurusu: 22 | erişilebilir site=10/18 | durum=PARTIAL_SUCCESS", markdown)

    def test_empty_twitter_collection_does_not_imply_confirmation_data(self):
        self.write_processed(
            "news_twitter_latest_2025_2026.json",
            {
                "provider": "x_api",
                "collection_status": "FAILED",
                "total_tweets": 0,
                "accounts": [{"handle": "Besiktas", "error": "unavailable"}],
            },
        )

        catalog = data_catalog.build_catalog()
        sources = {source["type"]: source for source in catalog["sources"]}

        self.assertEqual(
            sources["X_SOCIAL_SIGNAL"]["coverage"],
            "Collector çalıştı (x_api/FAILED); kullanılabilir gönderi snapshot'ı yok",
        )
        self.assertEqual(catalog["coverage"]["news_twitter_successful_accounts"], 0)
        self.assertEqual(catalog["coverage"]["news_twitter_status"], "FAILED")


if __name__ == "__main__":
    unittest.main()
