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


if __name__ == "__main__":
    unittest.main()
