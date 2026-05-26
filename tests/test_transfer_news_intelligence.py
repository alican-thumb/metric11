import unittest
from datetime import datetime, timezone

from src.analyze_news_with_claude import _is_recent_live_item, build_intelligence, rule_based_analyze


def article(article_id, source, transfer, source_type="rss", account_type=None):
    return {
        "article_id": article_id,
        "title": f"{transfer['player_name']} transfer haberi",
        "link": f"https://example.test/{article_id}",
        "source_name": source,
        "source_type": source_type,
        "account_type": account_type,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "summary": "",
        "categories": ["transfer"],
        "super_lig_relevant": True,
        "analyzed": True,
        "claude_analysis": {"transfer_rumors": [transfer]},
    }


class TransferIntelligenceTests(unittest.TestCase):
    def test_tags_keep_stable_input_order_without_duplicates(self):
        result = rule_based_analyze(
            {"title": "Özel haber", "summary": "", "categories": ["second", "first", "second"]},
            {},
        )

        self.assertEqual(result["news_types"], ["second", "first"])
        self.assertEqual(result["tags"], ["second", "first"])

    def test_transfer_does_not_assign_player_only_seen_in_summary(self):
        source = {
            "title": "Galatasaray yeni yıldız için transfer görüşmesinde",
            "summary": "Başka haber: Ali Örnek ayrılabilir.",
            "categories": ["transfer"],
        }
        player_index = {
            "ALI ORNEK": {"name": "Ali Örnek", "club": "ALANYASPOR"},
        }

        result = rule_based_analyze(source, player_index)

        self.assertEqual(result["transfer_rumors"][0]["player_name"], None)

    def test_consistent_independent_sources_are_corroborated(self):
        transfer = {
            "player_name": "Ali Örnek",
            "from_club": "ALANYASPOR",
            "to_club": "BEŞİKTAŞ A.Ş.",
            "signal_type": "offer",
            "confidence": "HIGH",
        }
        result = build_intelligence(
            [article("a", "Hürriyet Spor", transfer), article("b", "Takvim Spor", transfer)],
            {},
        )

        self.assertEqual(result["raw_transfer_mentions"], 2)
        self.assertEqual(result["transfer_signals"], 1)
        self.assertEqual(result["transfers"][0]["verification_status"], "CORROBORATED")
        self.assertEqual(result["transfers"][0]["source_count"], 2)

    def test_official_club_source_is_official_when_direction_exists(self):
        transfer = {
            "player_name": "Ali Örnek",
            "from_club": "ALANYASPOR",
            "to_club": "BEŞİKTAŞ A.Ş.",
            "signal_type": "signing",
            "confidence": "HIGH",
        }
        result = build_intelligence(
            [article("official", "@Besiktas", transfer, source_type="twitter", account_type="official")],
            {},
        )

        self.assertEqual(result["transfers"][0]["verification_status"], "OFFICIAL")
        self.assertTrue(result["transfers"][0]["model_use"])

    def test_official_club_website_announcement_is_official(self):
        transfer = {
            "player_name": "Ali Örnek",
            "from_club": "ALANYASPOR",
            "to_club": "BEŞİKTAŞ A.Ş.",
            "signal_type": "signing",
            "confidence": "HIGH",
        }
        result = build_intelligence(
            [article("club-web", "Beşiktaş Resmi Web", transfer, source_type="official_club", account_type="official")],
            {},
        )

        self.assertEqual(result["transfers"][0]["verification_status"], "OFFICIAL")
        self.assertTrue(result["transfers"][0]["model_use"])

    def test_stale_official_announcement_is_archived_but_not_a_live_signal(self):
        transfer = {
            "player_name": "Laszlo Benes",
            "from_club": None,
            "to_club": "KAYSERİSPOR",
            "signal_type": "signing",
            "confidence": "HIGH",
        }
        stale = article("old-club-web", "Kayserispor Resmi Web", transfer, source_type="official_club", account_type="official")
        stale["published_at"] = "2025-08-16T20:51:53+03:00"

        result = build_intelligence([stale], {})

        self.assertEqual(result["transfer_signals"], 0)
        self.assertEqual(result["stale_transfer_mentions_excluded"], 1)
        self.assertEqual(result["transfers"], [])
        self.assertEqual(result["historical_transfer_claims"][0]["verification_status"], "OFFICIAL")

    def test_turkish_formatted_recent_timestamp_is_kept_live(self):
        self.assertTrue(
            _is_recent_live_item(
                {"published_at": "18.5.2026 13:24:07"},
                now=datetime(2026, 5, 26, tzinfo=timezone.utc),
            )
        )

    def test_two_unscored_telegram_signals_remain_rumors(self):
        transfer = {
            "player_name": "Ali Örnek",
            "from_club": "ALANYASPOR",
            "to_club": "BEŞİKTAŞ A.Ş.",
            "signal_type": "offer",
            "confidence": "HIGH",
        }
        result = build_intelligence(
            [
                article("tg-a", "Transfer Haber", transfer, source_type="telegram", account_type="secondary_signal"),
                article("tg-b", "Kulüp Haberleri", transfer, source_type="telegram", account_type="secondary_signal"),
            ],
            {},
        )

        self.assertEqual(result["transfers"][0]["verification_status"], "RUMOR")
        self.assertFalse(result["transfers"][0]["model_use"])

    def test_official_outbound_web_announcement_extracts_destination(self):
        source = {
            "article_id": "bjk-muci",
            "title": "Ernest Muçi, Trabzonspor'a Transfer Oldu",
            "summary": "",
            "source_name": "Beşiktaş Resmi Web",
            "source_type": "official_club",
            "account_type": "official",
            "related_team": "BEŞİKTAŞ A.Ş.",
            "link": "https://bjk.test/ernest-muci",
            "published_at": datetime.now(timezone.utc).isoformat(),
            "categories": ["transfer"],
            "super_lig_relevant": True,
            "analyzed": True,
        }
        player_index = {
            "ERNEST MUCI": {"name": "ERNEST MUÇİ", "club": "TRABZONSPOR A.Ş."},
        }
        source["claude_analysis"] = rule_based_analyze(source, player_index)

        result = build_intelligence([source], player_index)
        row = result["transfers"][0]

        self.assertEqual(row["from_club"], "BEŞİKTAŞ A.Ş.")
        self.assertEqual(row["to_club"], "Trabzonspor")
        self.assertEqual(row["verification_status"], "OFFICIAL")
        self.assertTrue(row["model_use"])

    def test_transfermarkt_short_name_matches_official_announcement(self):
        source = {
            "title": "Büyük camiamıza hoş geldin Dan Agyei!",
            "summary": "",
            "source_type": "official_club",
            "account_type": "official",
            "related_team": "KOCAELİSPOR",
            "categories": ["transfer"],
        }
        player_index = {
            "DANIEL EBENEZER KWASI AGYEI": {
                "name": "DANIEL EBENEZER KWASI AGYEI",
                "tm_name": "Dan Agyei",
                "club": "KOCAELİSPOR",
            },
        }

        result = rule_based_analyze(source, player_index)

        self.assertEqual(result["transfer_rumors"][0]["player_name"], "DANIEL EBENEZER KWASI AGYEI")
        self.assertEqual(result["transfer_rumors"][0]["to_club"], "KOCAELİSPOR")

    def test_official_departure_without_destination_remains_review_required(self):
        source = {
            "article_id": "thanks",
            "title": "TEŞEKKÜRLER SİNAN OSMANOĞLU",
            "summary": "",
            "source_name": "Gençlerbirliği Resmi Web",
            "source_type": "official_club",
            "account_type": "official",
            "related_team": "GENÇLERBİRLİĞİ S.K.",
            "link": "https://club.test/thanks",
            "published_at": datetime.now(timezone.utc).isoformat(),
            "categories": ["transfer"],
            "super_lig_relevant": True,
            "analyzed": True,
        }
        player_index = {
            "SINAN OSMANOGLU": {"name": "SİNAN OSMANOĞLU", "club": "ARCA ÇORUM FK"},
        }
        source["claude_analysis"] = rule_based_analyze(source, player_index)

        row = build_intelligence([source], player_index)["transfers"][0]

        self.assertEqual(row["from_club"], "GENÇLERBİRLİĞİ S.K.")
        self.assertIsNone(row["to_club"])
        self.assertEqual(row["verification_status"], "REVIEW_REQUIRED")
        self.assertFalse(row["model_use"])

    def test_same_current_and_target_team_requires_review(self):
        transfer = {
            "player_name": "Ali Örnek",
            "from_club": "TRABZONSPOR A.Ş.",
            "to_club": "Trabzonspor",
            "signal_type": "departure",
            "confidence": "HIGH",
        }
        result = build_intelligence([article("bad-direction", "Takvim Spor", transfer)], {})
        row = result["transfers"][0]

        self.assertEqual(row["verification_status"], "REVIEW_REQUIRED")
        self.assertIsNone(row["to_club"])
        self.assertFalse(row["model_use"])

    def test_sponsored_and_short_club_names_are_the_same_destination(self):
        cases = [
            ("ÇAYKUR RİZESPOR A.Ş.", "Rizespor"),
            ("RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ", "Başakşehir"),
            ("İKAS EYÜPSPOR", "Eyüpspor"),
        ]
        for current_club, destination in cases:
            with self.subTest(current_club=current_club):
                transfer = {
                    "player_name": "Ali Örnek",
                    "from_club": current_club,
                    "to_club": destination,
                    "signal_type": "offer",
                    "confidence": "HIGH",
                }
                row = build_intelligence([article("same-club", "Hürriyet Spor", transfer)], {})["transfers"][0]

                self.assertEqual(row["verification_status"], "REVIEW_REQUIRED")
                self.assertIsNone(row["to_club"])

    def test_media_signing_headline_keeps_explicit_destination_despite_current_squad(self):
        source = {
            "title": "Sabuncuoğlu: Fenerbahçe Matteo Guendouzi transferinde anlaşmaya vardı",
            "summary": "",
            "categories": ["transfer"],
        }
        player_index = {
            "MATTEO GUENDOUZI": {"name": "Matteo Guendouzi", "club": "FENERBAHÇE A.Ş."},
        }

        row = rule_based_analyze(source, player_index)["transfer_rumors"][0]

        self.assertEqual(row["to_club"], "Fenerbahçe")
        self.assertIsNone(row["from_club"])

    def test_explicit_external_player_transfer_headline_builds_directional_rumor(self):
        source = {
            "title": "Eldar Şomurodov Başakşehir'e transfer oldu - Turkmenportal.com",
            "summary": "",
            "categories": ["transfer"],
        }

        rumor = rule_based_analyze(source, {})["transfer_rumors"][0]

        self.assertEqual(rumor["player_name"], "Eldar Şomurodov")
        self.assertEqual(rumor["to_club"], "Başakşehir")
        self.assertEqual(rumor["direction_quality"], "HEADLINE_EXPLICIT_DIRECTION")

    def test_targeted_operation_headline_extracts_external_player_and_target(self):
        source = {
            "title": "Galatasaray'da Can Uzun operasyonu başladı! Milli futbolcunun transferi için dev bütçe ayrıldı",
            "summary": "",
            "categories": ["transfer"],
        }

        rumor = rule_based_analyze(source, {})["transfer_rumors"][0]

        self.assertEqual(rumor["player_name"], "Can Uzun")
        self.assertEqual(rumor["to_club"], "Galatasaray")
        self.assertEqual(rumor["signal_type"], "interest")

    def test_allocated_budget_is_not_a_departure_signal(self):
        source = {
            "title": "Galatasaray Can Uzun için dev bütçe ayrıldı",
            "summary": "",
            "categories": ["transfer"],
        }

        result = rule_based_analyze(source, {})

        self.assertEqual(result["transfer_rumors"], [])

    def test_targeted_bomb_headline_extracts_external_player_and_target(self):
        source = {
            "title": "Fenerbahçe'den Mohamed Salah bombası! Prensipte anlaşma sağlandı",
            "summary": "",
            "categories": ["transfer"],
        }

        rumor = rule_based_analyze(source, {})["transfer_rumors"][0]

        self.assertEqual(rumor["player_name"], "Mohamed Salah")
        self.assertEqual(rumor["to_club"], "Fenerbahçe")

    def test_fee_headline_extracts_external_player_and_target(self):
        source = {
            "title": "Parayı veren Alexander Sörloth'u alır! Fenerbahçe'ye bonservis müjdesi",
            "summary": "",
            "categories": ["transfer"],
        }

        rumor = rule_based_analyze(source, {})["transfer_rumors"][0]

        self.assertEqual(rumor["player_name"], "Alexander Sörloth")
        self.assertEqual(rumor["to_club"], "Fenerbahçe")

    def test_anonymous_outbound_headline_does_not_claim_arrival_to_departing_club(self):
        source = {
            "article_id": "unnamed-departure",
            "title": "Galatasaray'da ayrılık! Trendyol 1. Lig ekibine transfer oldu",
            "summary": "",
            "source_name": "Haber Kaynağı",
            "source_type": "rss",
            "link": "https://example.test/unnamed-departure",
            "published_at": datetime.now(timezone.utc).isoformat(),
            "categories": ["transfer"],
            "super_lig_relevant": True,
            "analyzed": True,
        }

        source["claude_analysis"] = rule_based_analyze(source, {})
        rumor = source["claude_analysis"]["transfer_rumors"][0]
        claim = build_intelligence([source], {})["transfers"][0]

        self.assertEqual(rumor["from_club"], "Galatasaray")
        self.assertIsNone(rumor["to_club"])
        self.assertEqual(claim["from_club"], "Galatasaray")
        self.assertEqual(claim["verification_status"], "REVIEW_REQUIRED")

    def test_same_publisher_republication_does_not_create_corroboration(self):
        transfer_a = {
            "player_name": "Ali Örnek",
            "from_club": "ALANYASPOR",
            "to_club": "GALATASARAY A.Ş.",
            "signal_type": "offer",
            "confidence": "HIGH",
        }
        transfer_b = {**transfer_a, "signal_type": "transfer_fee"}

        result = build_intelligence(
            [
                article("rss-copy", "Hürriyet Spor", transfer_a, source_type="rss"),
                article("google-copy", "Hürriyet", transfer_b, source_type="google_news"),
            ],
            {},
        )

        self.assertEqual(result["transfer_signals"], 1)
        self.assertEqual(result["transfers"][0]["verification_status"], "RUMOR")
        self.assertEqual(result["transfers"][0]["source_count"], 1)
        self.assertEqual(len(result["transfers"][0]["evidence"]), 2)

    def test_anonymous_same_headline_republication_collapses_to_one_claim(self):
        transfer_a = {
            "player_name": None,
            "from_club": None,
            "to_club": "GALATASARAY A.Ş.",
            "signal_type": "transfer_fee",
            "confidence": "LOW",
        }
        transfer_b = {**transfer_a, "signal_type": "departure"}
        rss = article("rss-story", "Hürriyet Spor", transfer_a, source_type="rss")
        google = article("google-story", "Hürriyet", transfer_b, source_type="google_news")
        rss["title"] = "Galatasaray'da Can Uzun operasyonu başladı! Milli futbolcunun transferi için dev bütçe ayrıldı"
        google["title"] = f"{rss['title']} - Hürriyet"

        result = build_intelligence([rss, google], {})

        self.assertEqual(result["transfer_signals"], 1)
        self.assertEqual(result["transfers"][0]["source_count"], 1)
        self.assertEqual(len(result["transfers"][0]["evidence"]), 2)


if __name__ == "__main__":
    unittest.main()
