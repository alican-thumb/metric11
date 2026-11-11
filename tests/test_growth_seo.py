import unittest

from src.build_growth_share_pack import build_payload
from src.build_match_pages import build_match_page, build_week_page
from src.html_utils import page_html


def match(date_time=None):
    return {
        "match_id": "m1",
        "date_time": date_time,
        "home_team": "GALATASARAY A.Ş.",
        "away_team": "SAMSUNSPOR A.Ş.",
        "is_played": False,
        "predicted": "home",
        "published_pick": "home",
        "home_win_probability": 0.69,
        "draw_probability": 0.20,
        "away_win_probability": 0.11,
        "recommended_scoreline": {"score": "1-0"},
        "expected_home_goals": 1.9,
        "expected_away_goals": 0.6,
        "home_points_per_match": 2.1,
        "away_points_per_match": 0.6,
        "home_elo": 1669,
        "away_elo": 1481,
    }


class GrowthSeoTests(unittest.TestCase):
    def test_noindex_pages_keep_links_followable(self):
        html = page_html("Test", "<p>Test</p>", noindex=True)

        self.assertIn('content="noindex,follow"', html)
        self.assertNotIn("noindex,nofollow", html)

    def test_undated_match_and_week_are_noindex(self):
        _, match_html, meta = build_match_page(match(), 28, {}, {}, [match()])
        _, week_html, week_indexable = build_week_page(28, [match()])

        self.assertFalse(meta["indexable"])
        self.assertEqual(meta["indexing_reason"], "date_not_announced")
        self.assertIn('content="noindex,follow"', match_html)
        self.assertFalse(week_indexable)
        self.assertIn('content="noindex,follow"', week_html)

    def test_scheduled_match_and_week_are_indexable(self):
        scheduled = match("21.11.2026 16:00")
        _, match_html, meta = build_match_page(scheduled, 12, {}, {}, [scheduled])
        _, week_html, week_indexable = build_week_page(12, [scheduled])

        self.assertTrue(meta["indexable"])
        self.assertNotIn('content="noindex,follow"', match_html)
        self.assertTrue(week_indexable)
        self.assertNotIn('content="noindex,follow"', week_html)

    def test_share_pack_contains_measurable_campaigns(self):
        fixtures = {"season": "2026-2027", "weeks": [{"week": 12, "matches": [match("21.11.2026 16:00")]}]}
        simulation = {
            "after_week": 11,
            "teams": [
                {"team": "GALATASARAY A.Ş.", "name": "Galatasaray", "sim": {"champion": 0.48}},
                {"team": "TRABZONSPOR A.Ş.", "name": "Trabzonspor", "sim": {"champion": 0.42}},
            ],
        }
        history = [
            {"after_week": 10, "teams": {"GALATASARAY A.Ş.": {"champion": 0.40}, "TRABZONSPOR A.Ş.": {"champion": 0.45}}}
        ]
        scenarios = {
            "page_path": "super-lig-sampiyonluk-senaryolari-2026-27.html",
            "scenarios": [{
                "team": "GALATASARAY A.Ş.",
                "outcomes": {"win": {"champion": 0.55}, "loss": {"champion": 0.35}},
            }],
        }
        weekly = {"last_week": {"week": 11, "summary": {"evaluated_matches": 9, "correct": 4, "accuracy": 4 / 9}}}

        payload = build_payload(fixtures, simulation, history, scenarios, weekly)
        ids = {item["id"] for item in payload["campaigns"]}

        self.assertEqual(ids, {"championship_race", "strongest_match", "transparent_scorecard"})
        self.assertTrue(all("utm_source=x" in item["x"] for item in payload["campaigns"]))
        self.assertTrue(all("utm_source=telegram" in item["telegram"] for item in payload["campaigns"]))
        self.assertEqual(payload["publication_mode"], "manual_review_required")


if __name__ == "__main__":
    unittest.main()
