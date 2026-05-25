from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict
from pathlib import Path

from src.collectors.tff import probe_match
from src.collectors.tff_fixture import fetch_week_matches, fixture_to_dict
from src.config import PROCESSED_DIR, ensure_data_dirs


def main() -> None:
    parser = argparse.ArgumentParser(description="TFF lig sezonundaki tum mac detaylarini ceker.")
    parser.add_argument("--season", default="2025-2026")
    parser.add_argument("--competition", default="trendyol_super_lig")
    parser.add_argument("--seed-match-id", default="283783")
    parser.add_argument("--weeks", type=int, default=34)
    parser.add_argument("--sleep", type=float, default=0.25)
    args = parser.parse_args()

    ensure_data_dirs()

    all_fixtures = []
    seen_fixture_ids: set[str] = set()
    for week in range(1, args.weeks + 1):
        for match in fetch_week_matches(args.seed_match_id, week):
            if match.match_id in seen_fixture_ids:
                continue
            seen_fixture_ids.add(match.match_id)
            all_fixtures.append(match)
        time.sleep(args.sleep)

    parsed_matches = []
    probe_reports = []
    for idx, fixture in enumerate(all_fixtures, 1):
        probe = probe_match(fixture.match_id)
        probe_reports.append(asdict(probe))
        if probe.parsed_path:
            parsed = json.loads(Path(probe.parsed_path).read_text(encoding="utf-8"))
            parsed["fixture_week"] = fixture.week
            parsed["fixture_date_time"] = fixture.date_time
            parsed["fixture_score"] = fixture.score
            parsed_matches.append(parsed)
        if idx % 25 == 0:
            print(f"Fetched {idx}/{len(all_fixtures)} match details...")
        time.sleep(args.sleep)

    prefix = f"tff_{args.competition}_{args.season.replace('-', '_')}"
    fixtures_path = PROCESSED_DIR / f"{prefix}_fixtures.json"
    matches_path = PROCESSED_DIR / f"{prefix}_matches.json"
    report_path = PROCESSED_DIR / f"{prefix}_report.md"

    fixtures_payload = {
        "season": args.season,
        "competition": args.competition,
        "seed_match_id": args.seed_match_id,
        "fixture_count": len(all_fixtures),
        "fixtures": [fixture_to_dict(match) for match in all_fixtures],
    }
    fixtures_path.write_text(json.dumps(fixtures_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    matches_path.write_text(json.dumps(parsed_matches, ensure_ascii=False, indent=2), encoding="utf-8")
    report_path.write_text(build_report(fixtures_payload, probe_reports, matches_path), encoding="utf-8")
    print(report_path.read_text(encoding="utf-8"))


def build_report(fixtures_payload: dict, probe_reports: list[dict], matches_path: Path) -> str:
    successful = [item for item in probe_reports if item["ok"]]
    total_cards = sum(item["parsed_card_count"] for item in successful)
    total_goals = sum(item.get("parsed_goal_count", 0) for item in successful)
    total_starters = sum(item["starting_player_count"] for item in successful)
    total_bench = sum(item["bench_player_count"] for item in successful)

    lines = [
        f"# TFF {fixtures_payload['competition']} {fixtures_payload['season']} Lig Veri Toplama Raporu",
        "",
        f"- Fikstur tekil mac sayisi: {fixtures_payload['fixture_count']}",
        f"- Basariyla parse edilen mac sayisi: {len(successful)}",
        f"- Parse edilen ilk 11 oyuncu kaydi: {total_starters}",
        f"- Parse edilen yedek oyuncu kaydi: {total_bench}",
        f"- Parse edilen kart olayi: {total_cards}",
        f"- Parse edilen gol olayi: {total_goals}",
        f"- Islenmis mac detaylari: `{matches_path}`",
        "",
        "## Hata Olanlar",
        "",
    ]
    failures = [item for item in probe_reports if not item["ok"]]
    if not failures:
        lines.append("- Yok")
    else:
        for item in failures:
            lines.append(f"- `{item['match_id']}` status={item['status_code']} error={item['error']}")
    return "\n".join(lines)


if __name__ == "__main__":
    main()

