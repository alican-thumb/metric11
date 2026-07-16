from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from src.config import PROCESSED_DIR, ROOT_DIR


DEFAULT_COMMANDS = [
    ["python", "-m", "src.enrich_tff_with_sofascore"],
    ["python", "-m", "src.build_player_availability"],
    ["python", "-m", "src.build_tff_league_profile_pool"],
    ["python", "-m", "src.enrich_players_with_transfermarkt"],
    ["python", "-m", "src.analyze_league_scouting", "--output-prefix", "league_scouting_2025_2026_normalized"],
    ["python", "-m", "src.analyze_team_needs"],
    ["python", "-m", "src.analyze_enriched_scouting"],
    ["python", "-m", "src.generate_fm_attributes_from_stats"],
    ["python", "-m", "src.build_fm_style_scout_program"],
    ["python", "-m", "src.build_position_scout_matrix"],
    ["python", "-m", "src.build_league_intelligence_report"],
    ["python", "-m", "src.build_team_scout_blueprints"],
    ["python", "-m", "src.build_scout_quality_report"],
    ["python", "-m", "src.build_transfermarkt_match_review_queue"],
    ["python", "-m", "src.build_alias_quality_report"],
    ["python", "-m", "src.build_player_profile_enrichment_queue"],
    ["python", "-m", "src.model_league_predictions"],
    ["python", "-m", "src.build_league_market_value_audit"],
    ["python", "-m", "src.build_model_baseline_comparison"],
    ["python", "-m", "src.build_draw_risk_audit"],
    ["python", "-m", "src.generate_preview_batch", "--all-teams"],
    ["python", "-m", "src.build_all_teams_preview_dashboard"],
    ["python", "-m", "src.backtest_goal_candidates"],
    ["python", "-m", "src.backtest_match_predictions"],
    ["python", "-m", "src.build_prediction_validation_report"],
    ["python", "-m", "src.build_oos_validation"],
    ["python", "-m", "src.build_protected_action_audit"],
    ["python", "-m", "src.build_side_flip_audit"],
    ["python", "-m", "src.analyze_prediction_errors"],
    ["python", "-m", "src.build_big_match_report"],
    ["python", "-m", "src.build_source_watchlist"],
    ["python", "-m", "src.build_sqlite_warehouse"],
    ["python", "-m", "src.build_goal_candidate_segment_backtest"],
    ["python", "-m", "src.build_data_quality_scorecard"],
    ["python", "-m", "src.build_data_catalog"],
    ["python", "-m", "src.build_dashboard", "--all-teams"],
    ["python", "-m", "src.build_backtest_dashboard"],
    ["python", "-m", "src.build_team_needs_dashboard"],
    ["python", "-m", "src.build_enriched_scout_dashboard"],
    ["python", "-m", "src.build_transfer_recommendation_report"],
    ["python", "-m", "src.build_transfer_season_context"],
    ["python", "-m", "src.build_news_intelligence_report"],
    ["python", "-m", "src.build_source_performance_report"],
    ["python", "-m", "src.build_transfer_tracker"],
    ["python", "-m", "src.build_og_images"],
    ["python", "-m", "src.build_live_feed"],
    ["python", "-m", "src.build_command_center"],
    ["python", "-m", "src.analyze_worldcup_predictions"],
    ["python", "-m", "src.build_worldcup_predictions"],
    ["python", "-m", "src.build_european_news_pulse"],
    ["python", "-m", "src.analyze_european_predictions"],
    ["python", "-m", "src.build_european_predictions"],
    ["python", "-m", "src.build_season_fixture_predictions"],
    ["python", "-m", "src.build_product_home"],
    ["python", "-m", "src.build_sitemap"],
    ["python", "-m", "src.build_status_page"],
    ["python", "-m", "src.build_admin_page"],
]

NETWORK_COMMANDS = [
    ["python", "-m", "src.collect_tff_league_season"],
    ["python", "-m", "src.collect_tff_season_fixture"],
    ["python", "-m", "src.advance_season_state"],
    ["python", "-m", "src.collect_sofascore_stats", "--skip-existing"],
    ["python", "-m", "src.collect_besiktas_season"],
    [
        "python",
        "-m",
        "src.collect_tff_player_profiles",
        "--team",
        "BEŞİKTAŞ A.Ş.",
        "--limit",
        "0",
        "--output",
        "data/processed/tff_player_profiles_besiktas_2025_2026.json",
    ],
    [
        "python",
        "-m",
        "src.collect_tff_player_profiles",
        "--limit",
        "0",
        "--output",
        "data/processed/tff_player_profiles_league_all_2025_2026.json",
    ],
    ["python", "-m", "src.collect_transfermarkt_squad"],
    [
        "python", "-m", "src.collect_transfermarkt_league_squads",
        "--clubs", "data/manual/transfermarkt_super_lig_clubs_2025_2026.json",
        "--season-id", "2025",
        "--output-prefix", "transfermarkt_super_lig_squads_2025_2026",
        "--delay-seconds", "6",
    ],
    [
        "python", "-m", "src.collect_transfermarkt_player_profiles",
        "--skip-existing",
        "--delay-seconds", "1",
    ],
    [
        "python", "-m", "src.detect_squad_changes",
        "--squad-file", "data/processed/transfermarkt_super_lig_squads_2025_2026.json",
        "--snapshot-dir", "data/raw/transfermarkt/squad_snapshots_2025_2026",
        "--output", "data/processed/tm_squad_changes_2025_2026.json",
        "--season", "2025_2026",
    ],
    ["python", "-m", "src.collect_worldcup_fixtures"],
    ["python", "-m", "src.collect_european_fixtures"],
    ["python", "-m", "src.collect_national_team_form"],
    ["python", "-m", "src.collect_head_to_head_history", "--limit", "30"],
    ["python", "-m", "src.collect_news_context"],
    ["python", "-m", "src.collect_news_rss"],
    ["python", "-m", "src.collect_news_google"],
    ["python", "-m", "src.collect_news_telegram"],
    ["python", "-m", "src.collect_official_club_news"],
    ["python", "-m", "src.analyze_news_with_claude", "--only-relevant"],
]


def main() -> None:
    parser = argparse.ArgumentParser(description="metric11 günlük veri/analiz pipeline runner.")
    parser.add_argument("--include-network", action="store_true", help="Scraper/API collector komutlarını da çalıştırır.")
    parser.add_argument("--stop-on-error", action="store_true")
    parser.add_argument("--output", default=str(PROCESSED_DIR / "daily_pipeline_run_latest.json"))
    args = parser.parse_args()

    commands = []
    if args.include_network:
        commands.extend(NETWORK_COMMANDS)
        # 1 Haziran 2026'dan itibaren 2026/27 sezonu TM koleksiyonu devreye girer
        today = datetime.now(timezone.utc).date()
        if today >= datetime(2026, 6, 1, tzinfo=timezone.utc).date():
            commands.extend([
                [
                    "python", "-m", "src.collect_transfermarkt_league_squads",
                    "--clubs", "data/manual/transfermarkt_super_lig_clubs.json",
                    "--season-id", "2026",
                    "--output-prefix", "transfermarkt_super_lig_squads_2026_2027",
                    "--delay-seconds", "6",
                ],
                [
                    "python", "-m", "src.detect_squad_changes",
                    "--squad-file", "data/processed/transfermarkt_super_lig_squads_2026_2027.json",
                    "--snapshot-dir", "data/raw/transfermarkt/squad_snapshots_2026_2027",
                    "--output", "data/processed/tm_squad_changes_2026_2027.json",
                    "--season", "2026_2027",
                ],
            ])
    commands.extend(DEFAULT_COMMANDS)

    rows = []
    for command in commands:
        rows.append(run_command(command, stop_on_error=args.stop_on_error))
        if rows[-1]["returncode"] != 0 and args.stop_on_error:
            break

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "include_network": args.include_network,
        "command_count": len(commands),
        "ok_count": sum(1 for row in rows if row["returncode"] == 0),
        "failed_count": sum(1 for row in rows if row["returncode"] != 0),
        "rows": rows,
    }
    output = Path(args.output)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path = output.with_suffix(".md")
    md_path.write_text(build_markdown(payload), encoding="utf-8")
    print(md_path.read_text(encoding="utf-8"))
    if payload["failed_count"]:
        raise SystemExit(1)


def run_command(command: list[str], stop_on_error: bool = False) -> dict:
    resolved = [sys.executable if part == "python" else part for part in command]
    completed = subprocess.run(
        resolved,
        cwd=ROOT_DIR,
        text=True,
        capture_output=True,
        check=False,
        timeout=900,
    )
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout_tail": completed.stdout[-4000:],
        "stderr_tail": completed.stderr[-4000:],
        "stop_on_error": stop_on_error,
    }


def build_markdown(payload: dict) -> str:
    lines = [
        "# Günlük Pipeline Çalıştırma Raporu",
        "",
        f"- Zaman: {payload['generated_at']}",
        f"- Network dahil: {payload['include_network']}",
        f"- Komut: {payload['command_count']}",
        f"- Başarılı: {payload['ok_count']}",
        f"- Hatalı: {payload['failed_count']}",
        "",
        "## Komutlar",
        "",
    ]
    for row in payload["rows"]:
        status = "OK" if row["returncode"] == 0 else "FAIL"
        lines.append(f"- {status}: `{' '.join(row['command'])}`")
        if row["returncode"] != 0 and row.get("stderr_tail"):
            lines.append(f"  - stderr: `{row['stderr_tail'][-500:]}`")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
