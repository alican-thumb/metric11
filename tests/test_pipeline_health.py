import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src import run_daily_pipeline


def payload(timestamp: str, include_network: bool, failed: int = 0) -> dict:
    return {
        "generated_at": timestamp,
        "include_network": include_network,
        "command_count": 2,
        "ok_count": 2 - failed,
        "failed_count": failed,
        "rows": [],
    }


class PipelineHealthTests(unittest.TestCase):
    def test_derived_refresh_preserves_last_network_success(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            health_path = Path(temp_dir) / "pipeline_health.json"
            with patch.object(run_daily_pipeline, "PIPELINE_HEALTH_PATH", health_path):
                run_daily_pipeline.write_pipeline_health(payload("2026-11-01T04:00:00+00:00", True))
                health = run_daily_pipeline.write_pipeline_health(payload("2026-11-01T12:00:00+00:00", False))

        self.assertEqual(health["last_network_success_at"], "2026-11-01T04:00:00+00:00")
        self.assertEqual(health["last_derived_success_at"], "2026-11-01T12:00:00+00:00")
        self.assertEqual(health["run_kind"], "DERIVED_REFRESH")

    def test_failed_run_keeps_previous_success_timestamp(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            health_path = Path(temp_dir) / "pipeline_health.json"
            health_path.write_text(
                json.dumps({"last_success_at": "2026-11-01T04:00:00+00:00", "last_network_success_at": None}),
                encoding="utf-8",
            )
            with patch.object(run_daily_pipeline, "PIPELINE_HEALTH_PATH", health_path):
                health = run_daily_pipeline.write_pipeline_health(payload("2026-11-02T04:00:00+00:00", True, failed=1))

        self.assertEqual(health["status"], "FAILED")
        self.assertEqual(health["last_success_at"], "2026-11-01T04:00:00+00:00")
        self.assertIsNone(health["last_network_success_at"])


if __name__ == "__main__":
    unittest.main()
