"""Maç günü, henüz oynanmamış ama kadrosu TFF tarafından yayınlanmış olabilecek maçlar
için kadro (lineup) verisini erkenden yakalar.

`advance_season_state.py` yalnızca skor girildikten SONRA (maç bitince) zengin şemayı
çeker — bu yüzden `players_with_2026_27_appearance()`/`squad_transition_edge()` gibi
"bu sezon gerçekten oynadı mı" kontrolleri, o gün oynanan bir maçın kadrosunu ancak
maç bittikten SONRA görebiliyordu (kullanıcı isteği 2026-09-04: maç günü kadro
bilgisine göre tahminler ANINDA yenilenmeli).

TFF'nin maç sayfası (aynı `probe_match`/`parse_match_page` mekanizması) kadroyu
genellikle kickoff'tan ~1 saat önce yayınlıyor — skordan bağımsız. Bu script, kickoff'a
`WINDOW_HOURS_BEFORE` saatten az kalmış ve henüz oynanmamış (is_played=False) her maç
için TFF sayfasını dener; kadro varsa (`starting` dolu) `live_lineups_2026_2027.json`'a
kaydeder. Bu dosya iki yerde tüketilir:
  - `src/preview/probability.py::_players_appeared_this_season()` (canlı kadroya
    girmiş ama sezon boyunca hiç FINISHED maça girmemiş oyuncuyu da "oynadı" sayar —
    ör. bir yeni transferin SEZON DEBUT'ü olduğu maçın kendisi)
  - `build_goal_scorer_predictions.py` (o maça özel: sadece o günkü kadroda olan
    oyunculara tahmin üretir — yalnızca season-genelinde "oynamış mı" değil, O MAÇ
    kadrosunda mı diye bakar; en kesin sinyal)

ÖNEMLİ — çalışma sıklığı: Bu script kendi başına "canlı" değildir; ne sıklıkla
çalıştığı onu çağıran zamanlayıcıya bağlıdır. GitHub Actions workflow dosyalarına
(refresh.yml/daily-pipeline.yml) bu oturumdan yeni bir adım EKLENEMEDİ (workflow
OAuth scope kısıtı — bkz. PROJECT_STATE 2026-09-02/04) — yalnız mevcut 6 saatlik
döngüde çalışır, ki bu çoğu zaman kickoff'tan 1 saat önceki pencereyi KAÇIRIR. Gerçek
"maç başlamadan hemen önce" tazelik için kullanıcının ya bu script'i çalıştıran daha
sık (ör. 15 dakikada bir, yalnız maç günleri) yeni bir workflow adımı eklemesi ya da
bu repoya `workflow` scope'lu bir token vermesi gerekiyor.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from bs4 import BeautifulSoup

from src.collectors.tff import TFF_MATCH_URL, parse_match_page
from src.config import PROCESSED_DIR, ensure_data_dirs
from src.http_client import get_url
from src.model_league_predictions import parse_tff_datetime

FIXTURE_PRED_PATH = PROCESSED_DIR / "season_fixture_predictions_2026_2027.json"
OUTPUT_PATH = PROCESSED_DIR / "live_lineups_2026_2027.json"

WINDOW_HOURS_BEFORE = 5.0   # kickoff'a bu kadar saatten az kalan maçlar denenir
WINDOW_HOURS_AFTER = 3.0    # kickoff'tan sonra da bir süre denenmeye devam (geç yayın ihtimaline karşı)
TR_UTC_OFFSET_HOURS = 3     # Türkiye UTC+3, DST yok (2016'dan beri)


def _now_tr_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=TR_UTC_OFFSET_HOURS)


def _candidate_matches() -> list[dict]:
    if not FIXTURE_PRED_PATH.exists():
        return []
    payload = json.loads(FIXTURE_PRED_PATH.read_text(encoding="utf-8"))
    now = _now_tr_naive()
    out = []
    for week in payload.get("weeks", []):
        for m in week.get("matches", []):
            if m.get("is_played"):
                continue
            try:
                kickoff = parse_tff_datetime(m["date_time"])
            except (ValueError, KeyError):
                continue
            delta_hours = (kickoff - now).total_seconds() / 3600
            if -WINDOW_HOURS_AFTER <= delta_hours <= WINDOW_HOURS_BEFORE:
                out.append(m)
    return out


def _fetch_lineup(match_id: str) -> dict | None:
    url = TFF_MATCH_URL.format(match_id=match_id)
    result = get_url(url)
    if not result.ok:
        return None
    soup = BeautifulSoup(result.text, "html.parser")
    parsed = parse_match_page(match_id, soup)
    starting = len(parsed["lineups"]["home"]["starting"]) + len(parsed["lineups"]["away"]["starting"])
    if starting == 0:
        return None
    return parsed


def main() -> None:
    ensure_data_dirs()
    candidates = _candidate_matches()
    existing = {}
    if OUTPUT_PATH.exists():
        try:
            existing = json.loads(OUTPUT_PATH.read_text(encoding="utf-8")).get("matches", {})
        except json.JSONDecodeError:
            existing = {}

    checked = 0
    found = 0
    for m in candidates:
        match_id = str(m["match_id"])
        checked += 1
        parsed = _fetch_lineup(match_id)
        if parsed:
            existing[match_id] = {
                "home_team": m["home_team"],
                "away_team": m["away_team"],
                "date_time": m["date_time"],
                "detected_at": datetime.now(timezone.utc).isoformat(),
                "lineups": parsed["lineups"],
            }
            found += 1
            print(f"  KADRO BULUNDU: {m['home_team']} vs {m['away_team']} ({m['date_time']})", flush=True)

    payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "candidates_checked": checked,
        "matches": existing,
    }
    OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Kaydedildi: {OUTPUT_PATH} — {checked} maç denendi, {found} yeni kadro bulundu, toplam {len(existing)} kayıtlı.")


if __name__ == "__main__":
    main()
