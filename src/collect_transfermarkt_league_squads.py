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
    parser.add_argument("--cache-only", action="store_true", help="Ağ çağrısı yapmadan mevcut raw HTML cache dosyalarından üretir.")
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
        raw_path = RAW_DIR / "transfermarkt" / args.output_prefix / f"{club['club_id']}.html"
        if args.cache_only:
            players = parse_cached_squad(raw_path)
            if players:
                source_mode = "cache_only"
            else:
                skipped.append({**club, "url": url, "reason": "cache_missing_or_empty"})
                continue
        else:
            try:
                html = fetch(url)
                players = parse_squad(html)
                if players:
                    raw_path.parent.mkdir(parents=True, exist_ok=True)
                    raw_path.write_text(html, encoding="utf-8")
                    source_mode = "live"
                else:
                    cached_players = parse_cached_squad(raw_path)
                    if cached_players:
                        players = cached_players
                        source_mode = "cache_after_empty_live"
                    else:
                        skipped.append({**club, "url": url, "reason": "empty_squad"})
                        continue
            except Exception as exc:  # noqa: BLE001 - collector must keep partial progress
                players = parse_cached_squad(raw_path)
                if players:
                    source_mode = "cache_after_fetch_failed"
                else:
                    skipped.append({**club, "url": url, "reason": f"fetch_failed: {exc}"})
                    continue
        collected.append(
            {
                "team_name": club.get("team_name"),
                "club_slug": club["club_slug"],
                "club_id": club["club_id"],
                "verified": club.get("verified", False),
                "url": url,
                "source_mode": source_mode,
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
    if not collected:
        previous = load_previous_nonempty(PROCESSED_DIR / f"{args.output_prefix}.json")
        if previous:
            previous["stale_reason"] = "collector_produced_no_nonempty_clubs"
            previous["skipped_latest"] = skipped
            payload = previous

    json_path = PROCESSED_DIR / f"{args.output_prefix}.json"
    md_path = PROCESSED_DIR / f"{args.output_prefix}.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(build_league_markdown(payload), encoding="utf-8")
    print(md_path.read_text(encoding="utf-8"))


def parse_cached_squad(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        players = parse_squad(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001 - corrupt cache should not stop collection
        return []
    return players


def load_previous_nonempty(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if payload.get("summary", {}).get("players", 0) > 0:
        return payload
    return None


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
            f"değer=€{club['summary']['market_value_total_eur']:,}, verified={club.get('verified')}, "
            f"mode={club.get('source_mode', 'unknown')}, url={club['url']}"
        )
    if payload.get("stale_reason"):
        lines.extend(["", "## Stale Koruma", ""])
        lines.append(f"- Sebep: {payload['stale_reason']}")
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
