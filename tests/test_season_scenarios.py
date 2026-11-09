import unittest

from src.build_season_simulation import _match_key, _tr_int, simulate


class SeasonScenarioTests(unittest.TestCase):
    def setUp(self):
        self.weeks = [
            {
                "week": 1,
                "matches": [
                    {
                        "match_id": 99,
                        "home_team": "EV",
                        "away_team": "DEP",
                        "is_played": False,
                        "home_win_probability": 0.4,
                        "draw_probability": 0.3,
                        "away_win_probability": 0.3,
                    }
                ],
            }
        ]
        self.table = {
            "EV": {"pts": 0, "gf": 0, "ga": 0},
            "DEP": {"pts": 0, "gf": 0, "ga": 0},
        }

    def test_forced_home_win_is_applied_to_every_simulation(self):
        result = simulate(
            self.weeks,
            self.table,
            forced_results={"99": "home"},
            n_sims=20,
        )
        self.assertEqual(result["EV"]["avg_points"], 3.0)
        self.assertEqual(result["DEP"]["avg_points"], 0.0)

    def test_forced_draw_is_applied_to_every_simulation(self):
        result = simulate(
            self.weeks,
            self.table,
            forced_results={"99": "draw"},
            n_sims=20,
        )
        self.assertEqual(result["EV"]["avg_points"], 1.0)
        self.assertEqual(result["DEP"]["avg_points"], 1.0)

    def test_match_key_has_stable_fallback_without_provider_id(self):
        match = {"home_team": "EV", "away_team": "DEP"}

        self.assertEqual(_match_key(7, match), "7:EV:DEP")

    def test_turkish_integer_format_does_not_touch_surrounding_prose(self):
        self.assertEqual(_tr_int(20_000), "20.000")


if __name__ == "__main__":
    unittest.main()
