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


def _has_empty_lineup(match: dict) -> bool:
    lineups = match.get("lineups") or {}
    home_starting = (lineups.get("home") or {}).get("starting") or []
    away_starting = (lineups.get("away") or {}).get("starting") or []
    return not home_starting or not away_starting


def _played_unprocessed_matches(fixture_payload: dict, processed_ids: set[str], incomplete_ids: set[str]) -> list[dict]:
    """Oynanmış ama hiç işlenmemiş VEYA daha önce işlenip kadrosu hâlâ boş kalmış
    (bkz. `incomplete_ids` — TFF box score'u ilk denemede henüz yayınlamamış olabilir,
    2026-09-08 bulgusu: 34 maçın 8'i bu yüzden kalıcı olarak boş kadroyla kilitli
    kalmıştı, hiç yeniden denenmiyordu) maçları döner."""
    candidates = []
    for week in fixture_payload.get("weeks", []):
        for m in week.get("matches", []):
            score = (m.get("score") or "").strip()
            if not score or score == "-":
                continue
            if m["match_id"] in processed_ids and m["match_id"] not in incomplete_ids:
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
    matches_by_id = {m["external_id"]: idx for idx, m in enumerate(matches) if m.get("external_id")}
    processed_ids = set(matches_by_id)
    incomplete_ids = {mid for mid, idx in matches_by_id.items() if _has_empty_lineup(matches[idx])}

    candidates = _played_unprocessed_matches(fixture_payload, processed_ids, incomplete_ids)

    added = 0
    retried = 0
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
        if m["match_id"] in matches_by_id:
            if _has_empty_lineup(parsed):
                # TFF hâlâ kadroyu yayınlamamış — bir sonraki koşuda tekrar denenecek
                # şekilde eski (boş) kaydı koru, en azından skoru güncel tut.
                matches[matches_by_id[m["match_id"]]]["fixture_score"] = m["score"]
                time.sleep(0.25)
                continue
            matches[matches_by_id[m["match_id"]]] = parsed
            retried += 1
        else:
            matches.append(parsed)
            matches_by_id[m["match_id"]] = len(matches) - 1
            added += 1
        processed_ids.add(m["match_id"])
        time.sleep(0.25)

    MATCHES_PATH.write_text(json.dumps(matches, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        f"2026-27 state ilerletme: {len(candidates)} oynanmış maç adayı, "
        f"{added} yeni eklendi, {retried} eksik kadro tamamlanarak güncellendi, "
        f"{failed} başarısız, toplam birikim {len(matches)}."
    )


if __name__ == "__main__":
    main()
