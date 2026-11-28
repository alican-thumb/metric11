import json
import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from src import build_season_fixture_predictions as fixtures

from src.build_match_pages import _summary_sentence
from src.build_season_fixture_predictions import (
    DEFAULT_PUBLICATION_POLICY,
    load_publication_policy,
    publication_metadata,
)
from src.build_weekly_evaluation import _evaluate_match, _selective_publication_summary, _summarize


def prediction(home: float, draw: float, away: float) -> dict:
    return {
        "home_win_probability": home,
        "draw_probability": draw,
        "away_win_probability": away,
    }


class PredictionPublicationTests(unittest.TestCase):
    def test_result_hit_is_not_an_exact_score_hit(self):
        match = {"actual_score": "1 - 0", "predicted": "home", "is_played": True, **prediction(.6, .2, .2)}
        rows = [_evaluate_match({**match, "recommended_scoreline": {"score": score}})
                for score in ("2-1", "1-0", "")]
        summary = _summarize(rows)
        self.assertEqual(summary["correct"], 3)
        self.assertEqual(summary["exact_score"], {"evaluated": 2, "correct": 1, "missing": 1, "accuracy": .5})

    def test_prematch_lock_lifecycle(self):
        now = datetime(2026, 11, 28, 12, tzinfo=timezone.utc)
        match = {"match_id": 1, "home_team": "A", "away_team": "B", "score": "-", "date_time": "28.11.2026 - 17:00"}
        with tempfile.TemporaryDirectory() as folder, patch.object(fixtures, "_utc_now") as clock:
            folder = Path(folder)
            history = folder / "history"
            history.write_text("[]")
            schedule = folder / "fixture"
            clock.return_value = now
            with patch.multiple(fixtures, FIXTURE_PATH=schedule, SNAPSHOT_PATH=folder / "locks",
                                HISTORY_INPUT_PATH=history, PLAYED_2026_2027_PATH=folder / "none"), \
                 patch.object(fixtures, "predict_match", return_value=prediction(.60, .20, .20)) as model:
                def run():
                    schedule.write_text(json.dumps({"weeks": [{"week": 1, "matches": [match]}]}))
                    return fixtures.build_predictions()["weeks"][0]["matches"][0]

                self.assertTrue(run()["publication_is_prospective"])
                self.assertTrue(run()["publication_is_prospective"])
                self.assertEqual(model.call_count, 1)
                match["score"] = "1-0"
                clock.return_value = now + timedelta(hours=4)
                self.assertTrue(run()["publication_is_prospective"])
                self.assertEqual(model.call_count, 1)
                match["score"] = "-"
                match["date_time"] = "30.11.2026 - 17:00"
                self.assertFalse(run()["publication_is_prospective"])
                clock.return_value = now + timedelta(days=2, hours=2)
                self.assertFalse(run()["publication_is_prospective"])  # kickoff, even with no score
                match["score"] = "1-0"
                self.assertFalse(run()["publication_is_prospective"])
                self.assertFalse(run()["publication_is_prospective"])

    def test_prospective_publication_metric_excludes_retrospective_rows(self):
        rows = [
            {
                "actual": "home", "published_pick": "home", "publication_decision": "PUBLISH",
                "publication_is_prospective": True,
            },
            {
                "actual": "away", "published_pick": "home", "publication_decision": "PUBLISH",
                "publication_is_prospective": False,
            },
        ]

        result = _selective_publication_summary(rows, prospective_only=True)

        self.assertEqual(result["population_matches"], 1)
        self.assertEqual(result["published_matches"], 1)
        self.assertEqual(result["accuracy"], 1.0)

    def test_high_confidence_pick_is_published(self):
        result = publication_metadata(
            prediction(0.62, 0.22, 0.16),
            "home",
            is_new_team=False,
            policy=DEFAULT_PUBLICATION_POLICY,
        )
        self.assertEqual(result["prediction_confidence"], "HIGH")
        self.assertEqual(result["publication_decision"], "PUBLISH")
        self.assertEqual(result["published_pick"], "home")

    def test_medium_pick_keeps_model_output_but_hides_strong_selection(self):
        result = publication_metadata(
            prediction(0.47, 0.28, 0.25),
            "home",
            is_new_team=False,
            policy=DEFAULT_PUBLICATION_POLICY,
        )
        self.assertEqual(result["prediction_confidence"], "MEDIUM")
        self.assertEqual(result["publication_decision"], "NO_STRONG_PICK")
        self.assertEqual(result["publication_label"], "Düşük güvenli tahmin")
        self.assertIn("orta güven bandındaki", result["publication_reason"])
        self.assertIsNone(result["published_pick"])

    def test_draw_policy_overrides_high_confidence_band(self):
        result = publication_metadata(
            prediction(0.18, 0.62, 0.20),
            "draw",
            is_new_team=False,
            policy=DEFAULT_PUBLICATION_POLICY,
        )
        self.assertEqual(result["prediction_confidence"], "HIGH")
        self.assertEqual(result["publication_decision"], "WEAK")
        self.assertIsNone(result["published_pick"])

    def test_new_team_is_never_published_as_strong_pick(self):
        result = publication_metadata(
            prediction(0.68, 0.18, 0.14),
            "home",
            is_new_team=True,
            policy=DEFAULT_PUBLICATION_POLICY,
        )
        self.assertEqual(result["publication_decision"], "NO_STRONG_PICK")
        self.assertIn("Yeni yükselen takım", result["publication_reason"])
        self.assertIsNone(result["published_pick"])

    def test_stored_policy_is_loaded_with_safe_fallbacks(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "audit.json"
            path.write_text(
                json.dumps({"confidence_policy": {"medium": {"status": "PUBLISH", "label": "Orta seçim"}}}),
                encoding="utf-8",
            )
            policy = load_publication_policy(path)
        self.assertEqual(policy["medium"]["status"], "PUBLISH")
        self.assertEqual(policy["high"]["status"], "PUBLISH")
        self.assertEqual(policy["low"]["status"], "NO_STRONG_PICK")

    def test_low_confidence_summary_still_states_model_prediction(self):
        match = {
            "home_team": "BEŞİKTAŞ A.Ş.",
            "away_team": "GÖZTEPE A.Ş.",
            "home_win_probability": 0.44,
            "draw_probability": 0.29,
            "away_win_probability": 0.27,
            "recommended_scoreline": {"score": "1-1"},
        }
        summary = _summary_sentence(match, "home")
        self.assertIn("favori ev sahibi", summary)
        self.assertIn("%44", summary)


if __name__ == "__main__":
    unittest.main()
