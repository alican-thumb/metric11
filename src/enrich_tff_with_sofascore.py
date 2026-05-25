"""
TFF maç verilerini Sofascore istatistikleriyle zenginleştirir.
Birleştirme anahtarı: tarih + ev sahibi takım TFF canonical adı.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from src.config import PROCESSED_DIR
from src.normalization import normalize_matches
from src.preview.form import parse_tff_datetime


def load_sofascore(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    index: dict[str, dict] = {}
    for rec in data.get("matches", []):
        home_tff = rec.get("home_team_tff")
        date = rec.get("date")
        if home_tff and date:
            key = f"{date}|{home_tff}"
            index[key] = rec
    return index


def tff_date_to_iso(value: str) -> str:
    try:
        dt = parse_tff_datetime(value)
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return ""


def enrich(matches: list[dict], sofascore_index: dict[str, dict]) -> tuple[list[dict], dict]:
    enriched = []
    stats = {"total": len(matches), "matched": 0, "with_xg": 0, "no_match": []}
    for match in matches:
        iso = tff_date_to_iso(match.get("match_date", ""))
        home = match.get("home_team", {}).get("name", "")
        key = f"{iso}|{home}"
        ss = sofascore_index.get(key)
        copy = dict(match)
        if ss and ss.get("stats"):
            copy["sofascore_stats"] = ss["stats"]
            copy["sofascore_id"] = ss.get("sofascore_id")
            stats["matched"] += 1
            if ss["stats"].get("xg_home") is not None:
                stats["with_xg"] += 1
        else:
            copy["sofascore_stats"] = None
            stats["no_match"].append(f"{iso} {home}")
        enriched.append(copy)
    return enriched, stats


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="TFF maclarini Sofascore statslerle zenginlestirir.")
    parser.add_argument("--tff-input", default=str(PROCESSED_DIR / "tff_trendyol_super_lig_2025_2026_matches.json"))
    parser.add_argument("--sofascore-input", default=str(PROCESSED_DIR / "sofascore_match_stats_2025_2026.json"))
    parser.add_argument("--output", default=str(PROCESSED_DIR / "tff_super_lig_enriched_2025_2026.json"))
    args = parser.parse_args()

    matches = normalize_matches(json.loads(Path(args.tff_input).read_text(encoding="utf-8")))
    ss_index = load_sofascore(Path(args.sofascore_input))
    enriched, stats = enrich(matches, ss_index)

    Path(args.output).write_text(json.dumps(enriched, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Kaydedildi: {args.output}")
    print(f"Toplam: {stats['total']} | Eslesen: {stats['matched']} | xGli: {stats['with_xg']}")
    if stats["no_match"]:
        print(f"Eslesmeyen {len(stats['no_match'])} mac (ilk 5): {stats['no_match'][:5]}")


if __name__ == "__main__":
    main()
