from __future__ import annotations

import argparse

from src.collectors.api_football import collect_super_lig_snapshot
from src.config import load_settings


def main() -> None:
    parser = argparse.ArgumentParser(description="Dış API kaynaklarından Süper Lig snapshot verisi toplar.")
    parser.add_argument("--season", type=int, default=2025)
    parser.add_argument("--league-id", type=int, default=203)
    args = parser.parse_args()

    settings = load_settings()
    snapshot = collect_super_lig_snapshot(settings.api_football_key, season=args.season, league_id=args.league_id)
    summary = snapshot["summary"]
    print(
        f"API-Football snapshot: ok={summary['ok']} "
        f"successful_endpoints={summary.get('successful_endpoints', 0)} season={summary['season']}"
    )


if __name__ == "__main__":
    main()
