import unittest

from src.build_alias_quality_report import compare_enriched_profiles
from src.build_transfermarkt_match_review_queue import build_markdown, build_queue


class TransfermarktMatchReviewQueueTests(unittest.TestCase):
    def test_manual_alias_is_mapped_but_stays_pending_network_verification(self):
        profiles = [
            {"external_id": "1", "name": "Verified Player", "club": "TAKIM A", "tm_id": "tm-1"},
            {
                "external_id": "2",
                "name": "Manual Player",
                "club": "TAKIM A",
                "tm_id": None,
                "tm_name": "Manual TM Name",
                "tm_team_name": "TAKIM A",
                "tm_match_method": "manual_alias",
                "tm_requires_network_verify": True,
            },
            {"external_id": "3", "name": "Open Player", "club": "TAKIM A", "tm_id": None},
        ]
        tm_payload = {
            "summary": {"players": 1},
            "clubs": [{"team_name": "TAKIM A", "players": [{"name": "Other Name"}]}],
        }
        league_intelligence = {
            "player_profiles": [
                {"player_id": "2", "starts": 15, "goals": 4, "squad_inclusions": 16},
                {"player_id": "3", "starts": 12, "goals": 0, "squad_inclusions": 13},
            ]
        }

        payload = build_queue(profiles, tm_payload, {}, league_intelligence)
        summary = payload["summary"]

        self.assertEqual(summary["verified_matched_profiles"], 1)
        self.assertEqual(summary["manual_alias_mapped_profiles"], 1)
        self.assertEqual(summary["manual_alias_pending_network_verification"], 1)
        self.assertEqual(summary["operationally_mapped_profiles"], 2)
        self.assertEqual(summary["operational_in_scope_mapped_profiles"], 2)
        self.assertEqual(summary["unmatched_profiles"], 1)
        self.assertEqual(summary["review_tier_counts"]["HIGH_USAGE_UNRESOLVED"], 1)
        self.assertEqual(
            payload["manual_verification_queue"][0]["review_tier"],
            "MANUAL_VERIFY_HIGH_USAGE",
        )
        markdown = build_markdown(payload)
        self.assertIn("Ağ teyidi bekleyen manuel eşleme: 1", markdown)
        self.assertIn("Manuel eşleme dahil kullanılabilir snapshot içi kapsama: %66.7", markdown)

    def test_alias_quality_excludes_manual_mapping_from_unmatched_list(self):
        comparison = compare_enriched_profiles(
            [
                {"name": "Verified", "club": "TAKIM A", "tm_id": "tm-1", "tm_name": "Verified"},
                {
                    "name": "Manual",
                    "club": "TAKIM A",
                    "tm_match_method": "manual_alias",
                    "tm_name": "Manual",
                    "tm_requires_network_verify": True,
                },
                {"name": "Open", "club": "TAKIM A"},
            ]
        )

        self.assertEqual(comparison["matched"], 1)
        self.assertEqual(comparison["manual_mapped"], 1)
        self.assertEqual(comparison["manual_pending_network_verification"], 1)
        self.assertEqual(comparison["operationally_mapped"], 2)
        self.assertEqual([row["name"] for row in comparison["unmatched_left"]], ["Open"])

    def test_verified_manual_origin_is_not_counted_as_pending_manual_mapping(self):
        profile = {
            "external_id": "1",
            "name": "Verified Manual Origin",
            "club": "TAKIM A",
            "tm_id": "tm-1",
            "tm_name": "Verified Manual Origin",
            "tm_match_method": "manual_alias",
            "tm_requires_network_verify": False,
        }
        tm_payload = {
            "summary": {"players": 1},
            "clubs": [{"team_name": "TAKIM A", "players": [{"name": "Verified Manual Origin"}]}],
        }

        payload = build_queue([profile], tm_payload, {}, {})
        comparison = compare_enriched_profiles([profile])

        self.assertEqual(payload["summary"]["verified_matched_profiles"], 1)
        self.assertEqual(payload["summary"]["manual_alias_mapped_profiles"], 0)
        self.assertEqual(payload["summary"]["operationally_mapped_profiles"], 1)
        self.assertEqual(comparison["matched"], 1)
        self.assertEqual(comparison["manual_mapped"], 0)
        self.assertEqual(comparison["operationally_mapped"], 1)


if __name__ == "__main__":
    unittest.main()
