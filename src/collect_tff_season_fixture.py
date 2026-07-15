"""TFF Trendyol Süper Lig gelecek sezon resmi fikstürünü toplar (henüz oynanmamış maçlar).

`collect_tff_league_season.py`'den farklı olarak maç detayına inmez (maçlar henüz
oynanmadı, kart/gol/kadro verisi yok) — yalnızca hafta/tarih/ev-deplasman listesini
toplar. Bu fikstür `build_season_fixture_predictions.py` tarafından tahmine çevrilir.
"""
from __future__ import annotations

import argparse
import json
import time

from src.collectors.tff_fixture import fetch_week_matches, fixture_to_dict
from src.config import PROCESSED_DIR, ensure_data_dirs


def main() -> None:
    parser = argparse.ArgumentParser(description="TFF gelecek sezon resmi fikstürünü toplar.")
    parser.add_argument("--season", default="2026-2027")
    parser.add_argument("--seed-match-id", default="317784", help="Hedef sezona ait bilinen bir macId (hafta/tarih context'i için gerekli).")
    parser.add_argument("--weeks", type=int, default=34)
    parser.add_argument("--sleep", type=float, default=0.3)
    parser.add_argument("--output-prefix", default=None)
    args = parser.parse_args()

    ensure_data_dirs()
    prefix = args.output_prefix or f"tff_super_lig_fixtures_{args.season.replace('-', '_')}"

    weeks_payload = []
    empty_streak = 0
    for week in range(1, args.weeks + 1):
        try:
            matches = fetch_week_matches(args.seed_match_id, week)
        except RuntimeError as exc:
            print(f"  Hafta {week}: HATA {exc}")
            break
        if not matches:
            empty_streak += 1
            if empty_streak >= 2:
                print(f"  Hafta {week}: art arda boş, fikstür burada bitiyor kabul edildi.")
                break
            time.sleep(args.sleep)
            continue
        empty_streak = 0
        weeks_payload.append({"week": week, "matches": [fixture_to_dict(m) for m in matches]})
        print(f"  Hafta {week}: {len(matches)} maç, ilk tarih={matches[0].date_time}")
        time.sleep(args.sleep)

    total_matches = sum(len(w["matches"]) for w in weeks_payload)
    payload = {
        "season": args.season,
        "seed_match_id": args.seed_match_id,
        "weeks_collected": len(weeks_payload),
        "total_matches": total_matches,
        "weeks": weeks_payload,
    }
    json_path = PROCESSED_DIR / f"{prefix}.json"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Kaydedildi: {json_path} ({len(weeks_payload)} hafta, {total_matches} maç)")


if __name__ == "__main__":
    main()
