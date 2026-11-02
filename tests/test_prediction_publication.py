import json
import tempfile
import unittest
from pathlib import Path

from src.build_match_pages import _summary_sentence
from src.build_season_fixture_predictions import (
    DEFAULT_PUBLICATION_POLICY,
    load_publication_policy,
    publication_metadata,
)


def prediction(home: float, draw: float, away: float) -> dict:
    return {
        "home_win_probability": home,
        "draw_probability": draw,
        "away_win_probability": away,
    }


class PredictionPublicationTests(unittest.TestCase):
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
        self.assertEqual(result["publication_label"], "Net seçim yok")
        self.assertIn("kararsız", result["publication_reason"])
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

    def test_no_pick_summary_explains_model_tendency_without_claiming_favorite(self):
        match = {
            "home_team": "BEŞİKTAŞ A.Ş.",
            "away_team": "GÖZTEPE A.Ş.",
            "home_win_probability": 0.44,
            "draw_probability": 0.29,
            "away_win_probability": 0.27,
            "recommended_scoreline": {"score": "1-1"},
        }
        summary = _summary_sentence(match, None)
        self.assertIn("güçlü bir seçim yok", summary)
        self.assertIn("Model eğilimi", summary)
        self.assertNotIn("favori", summary)


if __name__ == "__main__":
    unittest.main()
