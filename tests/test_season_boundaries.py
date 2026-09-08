import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src import build_transfer_tracker
from src.config import TRANSFER_WATCH_SEASON
from src.generate_preview_batch import ALL_TEAMS
from src.run_daily_pipeline import NETWORK_COMMANDS


class SeasonBoundaryTests(unittest.TestCase):
    def test_historical_preview_roster_remains_on_match_data_season(self):
        self.assertIn("MISIRLI.COM.TR FATİH KARAGÜMRÜK", ALL_TEAMS)
        self.assertIn("HESAP.COM ANTALYASPOR", ALL_TEAMS)
        self.assertIn("ZECORNER KAYSERİSPOR", ALL_TEAMS)
        # 2026/27'ye yükselen takımlar artık gerçek maç verisine sahip
        # (bkz. tff_super_lig_matches_2026_2027.json), bu yüzden preview
        # rosterına dahil edilmeleri doğru davranış.
        self.assertIn("ÇORUM FK", ALL_TEAMS)
        self.assertIn("ERZURUMSPOR FK", ALL_TEAMS)
        self.assertIn("AMED SFK", ALL_TEAMS)

    def test_network_tm_collection_writes_active_transfer_season_separately(self):
        collector = next(command for command in NETWORK_COMMANDS if "src.collect_transfermarkt_league_squads" in command)
        detector = next(command for command in NETWORK_COMMANDS if "src.detect_squad_changes" in command)
        collector_text = " ".join(collector)
        detector_text = " ".join(detector)

        self.assertIn("transfermarkt_super_lig_squads_2026_2027", collector_text)
        self.assertNotIn("transfermarkt_super_lig_squads_2025_2026", collector_text)
        self.assertIn("tm_squad_changes_2026_2027.json", detector_text)
        self.assertIn("squad_snapshots_2026_2027", detector_text)

    def test_transfer_tracker_prefers_active_transfer_watch_snapshot(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            processed_dir = Path(temp_dir)
            historical = processed_dir / "tm_squad_changes_2025_2026.json"
            active = processed_dir / f"tm_squad_changes_{TRANSFER_WATCH_SEASON}.json"
            historical.write_text(json.dumps({"arrivals": [{"player_name": "Historical"}]}), encoding="utf-8")
            active.write_text(json.dumps({"arrivals": [{"player_name": "Active"}]}), encoding="utf-8")

            with patch.object(build_transfer_tracker, "PROCESSED_DIR", processed_dir):
                signals = build_transfer_tracker._load_tm_signals()

        self.assertEqual(signals[0]["player_name"], "Active")

    def test_daily_network_pipeline_does_not_require_x_credentials(self):
        command_modules = {" ".join(command) for command in NETWORK_COMMANDS}
        self.assertFalse(any("src.collect_news_twitter" in command for command in command_modules))

    def test_live_transfer_tracker_labels_active_season(self):
        html = build_transfer_tracker.build_html([], build_transfer_tracker._build_summary([]))

        self.assertIn("Transfer Takip — 2026-2027", html)
        self.assertNotIn("Transfer Takip — 2025-2026", html)


if __name__ == "__main__":
    unittest.main()
