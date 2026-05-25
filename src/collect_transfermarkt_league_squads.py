from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from src.collect_transfermarkt_squad import TRANSFERMARKT_BASE, build_markdown, fetch, parse_squad, summarize
from src.config import PROCESSED_DIR, RAW_DIR, ROOT_DIR


def main() -> None:
    parser = argparse.ArgumentParser(description="Transfermarkt lig kadrolarını kontrollü şekilde toplar.")
    parser.add_argument("--clubs", default=str(ROOT_DIR / "data/manual/transfermarkt_super_lig_clubs.example.json"))
    parser.add_argument("--season-id", default=None)
    parser.add_argument("--output-prefix", default="transfermarkt_super_lig_squads_2025_2026")
    parser.add_argument("--delay-seconds", type=float, default=8.0)
    parser.add_argument("--only-verified", action="store_true", help="Sadece verified=true kulüpleri toplar.")
    args = parser.parse_args()

    club_payload = json.loads(Path(args.clubs).read_text(encoding="utf-8"))
    season_id = args.season_id or club_payload.get("season_id") or "2025"
    collected = []
    skipped = []
    for club in club_payload.get("clubs", []):
        if args.only_verified and not club.get("verified"):
            skipped.append({**club, "reason": "not_verified"})
            continue
        if not club.get("club_slug") or not club.get("club_id"):
            skipped.append({**club, "reason": "missing_slug_or_id"})
            continue
        url = f"{TRANSFERMARKT_BASE}/{club['club_slug']}/kader/verein/{club['club_id']}/saison_id/{season_id}"
        try:
            html = fetch(url)
        except Exception as exc:  # noqa: BLE001 - collector must keep partial progress
            skipped.append({**club, "url": url, "reason": f"fetch_failed: {exc}"})
            continue
        raw_path = RAW_DIR / "transfermarkt" / args.output_prefix / f"{club['club_id']}.html"
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        raw_path.write_text(html, encoding="utf-8")
        players = parse_squad(html)
        collected.append(
            {
                "team_name": club.get("team_name"),
                "club_slug": club["club_slug"],
                "club_id": club["club_id"],
                "verified": club.get("verified", False),
                "url": url,
                "players": players,
                "summary": summarize(players),
            }
        )
        time.sleep(args.delay_seconds)

    payload = {
        "source": "Transfermarkt",
        "source_type": "SCRAPING",
        "risk_level": "HIGH",
        "license_status": "VERIFY_TERMS_BEFORE_COMMERCIAL_USE",
        "season_id": season_id,
        "clubs_collected": len(collected),
        "clubs_skipped": len(skipped),
        "clubs": collected,
        "skipped": skipped,
        "summary": summarize_league(collected),
    }
    json_path = PROCESSED_DIR / f"{args.output_prefix}.json"
    md_path = PROCESSED_DIR / f"{args.output_prefix}.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(build_league_markdown(payload), encoding="utf-8")
    print(md_path.read_text(encoding="utf-8"))


def summarize_league(clubs: list[dict]) -> dict:
    players = [player for club in clubs for player in club.get("players", [])]
    values = [player.get("market_value_eur") for player in players if player.get("market_value_eur") is not None]
    return {
        "clubs": len(clubs),
        "players": len(players),
        "market_value_total_eur": sum(values),
        "market_value_avg_eur": round(sum(values) / len(values)) if values else None,
        "position_groups": {
            group: sum(1 for player in players if player.get("position_group") == group)
            for group in ("GK", "DEF", "MID", "FWD", "UNKNOWN")
        },
    }


def build_league_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# Transfermarkt Süper Lig Kadro Snapshot",
        "",
        f"- Risk: {payload['risk_level']}",
        f"- Lisans durumu: {payload['license_status']}",
        f"- Toplanan kulüp: {payload['clubs_collected']}",
        f"- Atlanan kulüp: {payload['clubs_skipped']}",
        f"- Oyuncu: {summary['players']}",
        f"- Toplam piyasa değeri: €{summary['market_value_total_eur']:,}",
        f"- Ortalama piyasa değeri: €{summary['market_value_avg_eur']:,}" if summary["market_value_avg_eur"] else "- Ortalama piyasa değeri: Yok",
        f"- Pozisyon grupları: {summary['position_groups']}",
        "",
        "## Kulüpler",
        "",
    ]
    for club in payload["clubs"]:
        lines.append(
            f"- {club['team_name']}: oyuncu={club['summary']['players']}, "
            f"değer=€{club['summary']['market_value_total_eur']:,}, verified={club.get('verified')}, url={club['url']}"
        )
    if payload["skipped"]:
        lines.extend(["", "## Atlananlar", ""])
        for item in payload["skipped"]:
            lines.append(f"- {item.get('team_name')}: {item.get('reason')}")
    lines.extend(["", "## Beşiktaş Tekil Rapor Formatı", ""])
    if payload["clubs"]:
        sample = {
            "url": payload["clubs"][0]["url"],
            "risk_level": payload["risk_level"],
            "players": payload["clubs"][0]["players"],
            "summary": payload["clubs"][0]["summary"],
        }
        lines.append(build_markdown(sample))
    return "\n".join(lines)


if __name__ == "__main__":
    main()
