import unittest

from src.analyze_news_with_claude import build_intelligence, rule_based_analyze


def article(article_id, source, transfer, source_type="rss", account_type=None):
    return {
        "article_id": article_id,
        "title": f"{transfer['player_name']} transfer haberi",
        "link": f"https://example.test/{article_id}",
        "source_name": source,
        "source_type": source_type,
        "account_type": account_type,
        "published_at": "2026-05-25T10:00:00+00:00",
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
            "published_at": "2026-05-20T10:00:00+03:00",
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
            "published_at": "2026-01-07T10:00:00+03:00",
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


if __name__ == "__main__":
    unittest.main()
