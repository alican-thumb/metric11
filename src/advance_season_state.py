"""2026-27 sezonunda oynanan maçları algılar, tahmin motorunun state'ini ilerletir.

`collect_tff_season_fixture.py` her gün 2026-27 fikstürünü tazeler (hafta/tarih/skor
metni) ama zengin şemayı (kart, hakem, sofascore xG) toplamaz. Bu script, fikstürde
skoru artık "-" olmayan (oynanmış) ama henüz birikim dosyasına eklenmemiş maçları
tespit edip `collect_tff_league_season.py` ile aynı `probe_match` mekanizmasıyla
zengin şemayla çeker ve `tff_super_lig_matches_2026_2027.json` birikim dosyasına ekler.

`build_season_fixture_predictions.py` bu birikim dosyasını 2025-26 tam sezon geçmişiyle
birleştirip `compute_final_state`'e vererek tahmin motorunun state'ini oynanan her
2026-27 maçıyla ilerletir.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from src.collectors.tff import probe_match
from src.config import PROCESSED_DIR, ensure_data_dirs

FIXTURE_PATH = PROCESSED_DIR / "tff_super_lig_fixtures_2026_2027.json"
MATCHES_PATH = PROCESSED_DIR / "tff_super_lig_matches_2026_2027.json"


def _load_existing_matches() -> list[dict]:
    if not MATCHES_PATH.exists():
        return []
    try:
        return json.loads(MATCHES_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def _played_unprocessed_matches(fixture_payload: dict, processed_ids: set[str]) -> list[dict]:
    candidates = []
    for week in fixture_payload.get("weeks", []):
        for m in week.get("matches", []):
            score = (m.get("score") or "").strip()
            if not score or score == "-":
                continue
            if m["match_id"] in processed_ids:
                continue
            candidates.append(m)
    return candidates


def main() -> None:
    ensure_data_dirs()
    if not FIXTURE_PATH.exists():
        print(f"HATA: {FIXTURE_PATH} bulunamadı. Önce collect_tff_season_fixture çalıştırın.")
        return

    fixture_payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    matches = _load_existing_matches()
    processed_ids = {m["external_id"] for m in matches if m.get("external_id")}

    candidates = _played_unprocessed_matches(fixture_payload, processed_ids)

    added = 0
    failed = 0
    for m in candidates:
        probe = probe_match(m["match_id"])
        if not probe.ok or not probe.parsed_path:
            failed += 1
            time.sleep(0.25)
            continue
        parsed = json.loads(Path(probe.parsed_path).read_text(encoding="utf-8"))
        parsed["fixture_week"] = m["week"]
        parsed["fixture_date_time"] = m["date_time"]
        parsed["fixture_score"] = m["score"]
        matches.append(parsed)
        processed_ids.add(m["match_id"])
        added += 1
        time.sleep(0.25)

    MATCHES_PATH.write_text(json.dumps(matches, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"2026-27 state ilerletme: {len(candidates)} oynanmış maç adayı, "
        f"{added} başarıyla eklendi, {failed} başarısız, toplam birikim {len(matches)}."
    )


if __name__ == "__main__":
    main()
