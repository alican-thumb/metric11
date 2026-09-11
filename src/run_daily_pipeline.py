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
    ["python", "-m", "src.build_player_availability", "--all-teams"],
    ["python", "-m", "src.build_tff_league_profile_pool"],
    ["python", "-m", "src.enrich_players_with_transfermarkt"],
    ["python", "-m", "src.analyze_league_scouting", "--output-prefix", "league_scouting_2025_2026_normalized"],
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
    ["python", "-m", "src.build_enriched_scout_dashboard"],
    ["python", "-m", "src.build_transfer_recommendation_report"],
    ["python", "-m", "src.build_transfer_season_context"],
    ["python", "-m", "src.build_news_intelligence_report"],
    ["python", "-m", "src.build_source_performance_report"],
    ["python", "-m", "src.build_transfer_tracker"],
    ["python", "-m", "src.build_og_images"],
    # 2026-27 maç/tahmin zinciri: fikstür tahminleri → haftalık karne → "Bu Hafta".
    # build_live_feed/build_command_center/build_product_home bu çıktıları okuduğu için
    # ANA SAYFADAN ÖNCE üretilir (aksi halde ana sayfa bayat tahmin gösterir).
    ["python", "-m", "src.build_season_fixture_predictions"],
    ["python", "-m", "src.build_weekly_evaluation"],
    ["python", "-m", "src.build_match_week"],
    ["python", "-m", "src.build_live_feed"],
    ["python", "-m", "src.build_command_center"],
    ["python", "-m", "src.analyze_worldcup_predictions"],
    ["python", "-m", "src.build_worldcup_predictions"],
    ["python", "-m", "src.build_european_news_pulse"],
    ["python", "-m", "src.analyze_european_predictions"],
    ["python", "-m", "src.build_european_predictions"],
    ["python", "-m", "src.build_product_home"],
    ["python", "-m", "src.build_sitemap"],
    ["python", "-m", "src.build_status_page"],
    ["python", "-m", "src.build_admin_page"],
]

NETWORK_COMMANDS = [
    # collect_tff_league_season / collect_besiktas_season / collect_sofascore_stats
    # (with --skip-existing) all default to the finished 2025-2026 season. Once a
    # season is over, TFF/Sofascore's own site navigation from the hardcoded
    # seed match/season id starts resolving into the *next* season instead, so a
    # re-run silently overwrites the final, complete results with an empty/stub
    # fixture list. This happened twice in production (2026-05-27 wiped
    # sofascore_match_stats_2025_2026.json to 0 matches, 2026-07-16 wiped both
    # tff_trendyol_super_lig_2025_2026_matches.json and
    # tff_besiktas_2025_2026_matches.json to 0 scores) before anyone noticed,
    # because most downstream reports read from cached derived files rather than
    # re-deriving from these on every run. The 2025-2026 season is final
    # (306/306 league matches + 34/34 Beşiktaş matches all scored as of
    # 2026-05-25) — there is nothing left for these three collectors to gain, so
    # they are intentionally left out of the automated network pipeline.
    ["python", "-m", "src.collect_tff_season_fixture"],
    ["python", "-m", "src.advance_season_state"],
    ["python", "-m", "src.collect_live_lineups"],
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
    # 2026-09-08 bulgusu: yukarıdaki komut yalnızca TAMAMLANMIŞ 2025-26 sezonu maç
    # kadrolarından (--matches varsayılanı) oyuncu topluyor — bu yaz Süper Lig'e ilk
    # kez gelen (Vlahović/Greenwood gibi) 168 oyuncu hiç TFF profiline sahip değildi,
    # bu yüzden Scout/FM/transfer sayfalarında tamamen YOK sayılıyorlardı (bkz.
    # PROJECT_STATE). Bu ayrı komut, GÜNCEL 2026-27 maç kadrolarından (advance_
    # season_state.py'nin doldurduğu dosya) oyuncu toplar — mevcut/işlenmiş ID'ler
    # otomatik atlanır (collect_tff_player_profiles.py'nin kendi merge mantığı), yani
    # sezon ilerledikçe yeni debut yapan oyuncuları da otomatik yakalamaya devam eder.
    [
        "python",
        "-m",
        "src.collect_tff_player_profiles",
        "--matches",
        "data/processed/tff_super_lig_matches_2026_2027.json",
        "--limit",
        "0",
        "--output",
        "data/processed/tff_player_profiles_new_2026_2027.json",
    ],
    ["python", "-m", "src.collect_transfermarkt_squad"],
    [
        "python", "-m", "src.collect_transfermarkt_league_squads",
        "--clubs", "data/manual/transfermarkt_super_lig_clubs.json",
        "--season-id", "2026",
        "--output-prefix", "transfermarkt_super_lig_squads_2026_2027",
        "--delay-seconds", "6",
    ],
    [
        "python", "-m", "src.collect_transfermarkt_player_profiles",
        "--skip-existing",
        "--delay-seconds", "1",
    ],
    [
        "python", "-m", "src.detect_squad_changes",
        "--squad-file", "data/processed/transfermarkt_super_lig_squads_2026_2027.json",
        "--snapshot-dir", "data/raw/transfermarkt/squad_snapshots_2026_2027",
        "--output", "data/processed/tm_squad_changes_2026_2027.json",
        "--season", "2026_2027",
    ],
    ["python", "-m", "src.collect_worldcup_fixtures"],
    ["python", "-m", "src.collect_european_fixtures"],
    ["python", "-m", "src.collect_domestic_league_form"],
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
    post_report_rows = refresh_post_report_health_pages()
    if post_report_rows:
        payload["post_report_refresh"] = post_report_rows
        output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(md_path.read_text(encoding="utf-8"))
    post_report_failed = sum(1 for row in post_report_rows if row["returncode"] != 0)
    if payload["failed_count"] or post_report_failed:
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


def refresh_post_report_health_pages() -> list[dict]:
    # These pages read daily_pipeline_run_latest.json. They need one final pass
    # after the latest pipeline report is written, otherwise they can display
    # the previous run's freshness/failure state.
    return [
        run_command(["python", "-m", "src.build_data_quality_scorecard"]),
        run_command(["python", "-m", "src.build_status_page"]),
    ]


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
