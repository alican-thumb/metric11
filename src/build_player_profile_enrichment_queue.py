from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.config import PROCESSED_DIR


DEFAULT_PROFILE_FILES = [
    PROCESSED_DIR / "tff_player_profiles_besiktas_2025_2026.json",
    PROCESSED_DIR / "tff_player_profiles_scout_shortlist_2025_2026.json",
    PROCESSED_DIR / "tff_player_profiles_all_priority_2025_2026.json",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Eksik TFF oyuncu profilleri icin onceliklendirilmis toplama kuyrugu uretir.")
    parser.add_argument("--league-intelligence", default=str(PROCESSED_DIR / "league_intelligence_2025_2026.json"))
    parser.add_argument("--limit", type=int, default=180)
    parser.add_argument("--output-prefix", default="player_profile_enrichment_queue_2025_2026")
    args = parser.parse_args()

    league = json.loads(Path(args.league_intelligence).read_text(encoding="utf-8"))
    payload = build_queue(league, args.limit)
    json_path = PROCESSED_DIR / f"{args.output_prefix}.json"
    md_path = PROCESSED_DIR / f"{args.output_prefix}.md"
    ids_path = PROCESSED_DIR / f"{args.output_prefix}_ids.txt"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(build_markdown(payload), encoding="utf-8")
    ids_path.write_text("\n".join(item["player_id"] for item in payload["queue"]) + "\n", encoding="utf-8")
    print(md_path.read_text(encoding="utf-8"))


def build_queue(league: dict, limit: int) -> dict:
    existing = load_existing_profile_ids()
    candidates = []
    for player in league.get("player_profiles", []):
        player_id = str(player.get("player_id") or "")
        if not player_id or player_id in existing:
            continue
        priority_score = (
            player.get("starts", 0) * 2.4
            + player.get("goals", 0) * 4.0
            + player.get("cards", 0) * 1.3
            + player.get("estimated_load_score", 0) * 0.55
        )
        if player.get("profile_tag") in {"skor lideri", "omurga oyuncu", "yüksek yük/kart riski"}:
            priority_score += 18
        candidates.append(
            {
                "player_id": player_id,
                "name": player.get("name"),
                "team": player.get("team"),
                "starts": player.get("starts", 0),
                "goals": player.get("goals", 0),
                "cards": player.get("cards", 0),
                "estimated_load_score": player.get("estimated_load_score", 0),
                "profile_tag": player.get("profile_tag"),
                "priority_score": round(priority_score, 2),
            }
        )
    candidates.sort(key=lambda item: item["priority_score"], reverse=True)
    queue = candidates[:limit]
    return {
        "summary": {
            "existing_profile_ids": len(existing),
            "missing_candidates": len(candidates),
            "queued": len(queue),
            "limit": limit,
            "strategy": "İlk 11, gol, kart, tahmini yük ve profil etiketi yüksek oyuncular önce toplanır.",
        },
        "queue": queue,
    }


def load_existing_profile_ids() -> set[str]:
    ids = set()
    for path in DEFAULT_PROFILE_FILES:
        if not path.exists():
            continue
        for item in json.loads(path.read_text(encoding="utf-8")):
            if item.get("external_id"):
                ids.add(str(item["external_id"]))
    return ids


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# Oyuncu Profil Zenginleştirme Kuyruğu",
        "",
        f"- Mevcut profil ID: {summary['existing_profile_ids']}",
        f"- Eksik aday: {summary['missing_candidates']}",
        f"- Kuyruğa alınan: {summary['queued']}",
        f"- Strateji: {summary['strategy']}",
        "",
        "## İlk 50",
        "",
    ]
    for item in payload["queue"][:50]:
        lines.append(
            f"- {item['name']} ({item['team']}): skor={item['priority_score']}, "
            f"ilk11={item['starts']}, gol={item['goals']}, kart={item['cards']}, yük={item['estimated_load_score']}, etiket={item['profile_tag']}"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    main()
