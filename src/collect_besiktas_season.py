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
    parser = argparse.ArgumentParser(description="TFF sezon fiksturunden Besiktas maclarini ceker.")
    parser.add_argument("--season", default="2025-2026")
    parser.add_argument("--seed-match-id", default="283783")
    parser.add_argument("--weeks", type=int, default=34)
    parser.add_argument("--team", default="BEŞİKTAŞ A.Ş.")
    parser.add_argument("--sleep", type=float, default=0.35)
    args = parser.parse_args()

    ensure_data_dirs()

    all_fixtures = []
    team_fixtures = []
    for week in range(1, args.weeks + 1):
        week_matches = fetch_week_matches(args.seed_match_id, week)
        all_fixtures.extend(week_matches)
        team_fixtures.extend(
            match
            for match in week_matches
            if args.team in match.home_team or args.team in match.away_team
        )
        time.sleep(args.sleep)

    unique_team_fixtures = []
    seen_match_ids: set[str] = set()
    for match in team_fixtures:
        if match.match_id in seen_match_ids:
            continue
        seen_match_ids.add(match.match_id)
        unique_team_fixtures.append(match)

    parsed_matches = []
    probe_reports = []
    for fixture in unique_team_fixtures:
        probe = probe_match(fixture.match_id)
        probe_reports.append(asdict(probe))
        if probe.parsed_path:
            parsed_matches.append(json.loads(Path(probe.parsed_path).read_text(encoding="utf-8")))
        time.sleep(args.sleep)

    prefix = f"tff_besiktas_{args.season.replace('-', '_')}"
    fixtures_path = PROCESSED_DIR / f"{prefix}_fixtures.json"
    matches_path = PROCESSED_DIR / f"{prefix}_matches.json"
    report_path = PROCESSED_DIR / f"{prefix}_report.md"

    fixtures_payload = {
        "season": args.season,
        "team": args.team,
        "seed_match_id": args.seed_match_id,
        "all_fixture_count": len({match.match_id for match in all_fixtures}),
        "team_fixture_count": len(unique_team_fixtures),
        "fixtures": [fixture_to_dict(match) for match in unique_team_fixtures],
    }
    fixtures_path.write_text(json.dumps(fixtures_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    matches_path.write_text(json.dumps(parsed_matches, ensure_ascii=False, indent=2), encoding="utf-8")
    report_path.write_text(build_report(fixtures_payload, probe_reports, matches_path), encoding="utf-8")

    print(report_path.read_text(encoding="utf-8"))


def build_report(fixtures_payload: dict, probe_reports: list[dict], matches_path: Path) -> str:
    successful = [item for item in probe_reports if item["ok"]]
    total_cards = sum(item["parsed_card_count"] for item in successful)
    total_starters = sum(item["starting_player_count"] for item in successful)
    total_bench = sum(item["bench_player_count"] for item in successful)

    lines = [
        f"# TFF Beşiktaş {fixtures_payload['season']} Sezon Veri Toplama Raporu",
        "",
        f"- Takım: {fixtures_payload['team']}",
        f"- Fikstürdeki toplam tekil maç sayısı: {fixtures_payload['all_fixture_count']}",
        f"- Beşiktaş tekil maç sayısı: {fixtures_payload['team_fixture_count']}",
        f"- Başarıyla parse edilen maç sayısı: {len(successful)}",
        f"- Parse edilen ilk 11 oyuncu kaydı: {total_starters}",
        f"- Parse edilen yedek oyuncu kaydı: {total_bench}",
        f"- Parse edilen kart olayı: {total_cards}",
        f"- İşlenmiş maç detayları: `{matches_path}`",
        "",
        "## Maçlar",
        "",
    ]
    by_id = {item["match_id"]: item for item in probe_reports}
    for fixture in fixtures_payload["fixtures"]:
        probe = by_id.get(fixture["match_id"], {})
        lines.append(
            f"- {fixture['week']}. hafta | {fixture['date_time']} | "
            f"{fixture['home_team']} {fixture['score']} {fixture['away_team']} | "
            f"TFF ID `{fixture['match_id']}` | parse={probe.get('ok')}"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    main()

