"""Avrupa kupalarındaki kulüplerin GÜNCEL sezon iç lig formunu toplar (football-data.org).

Avrupa tahmin modeli (`analyze_european_predictions.py`) şu ana kadar yalnızca statik,
2024-25 sezonuna dayalı bir UEFA katsayı tablosu (`_CLUB_STRENGTH`) kullanıyordu — bu
sezon transfer olan/güçlenen/zayıflayan takımları hiç yansıtmıyordu ve turnuvanın
kendi maçları oynanana kadar (3+ maç, ağırlık max 10+ maçta) tamamen donuk kalıyordu.

Bu script, football-data.org'un ÜCRETSİZ planında zaten erişilebilen 7 büyük iç ligin
(PL, PD, BL1, SA, FL1, DED, PPL — Avrupa kupalarındaki kulüplerin büyük çoğunluğunu
kapsar) GÜNCEL sezon puan durumunu çeker. API-Football hesabına (2026-09-04 itibariyle
suspended) BAĞIMLI DEĞİLDİR — tamamen ayrı, zaten çalışan bir anahtar kullanır.

Çıktı: data/processed/domestic_league_form_2026_2027.json
"""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

from src.config import PROCESSED_DIR, ensure_data_dirs, load_settings

BASE_URL = "https://api.football-data.org/v4"
SEASON = 2026

# TIER_ONE (ücretsiz) planda yer alan, Avrupa kupalarındaki kulüplerin büyük
# çoğunluğunu barındıran iç ligler. Süper Lig zaten ayrı (TFF) toplanıyor.
LEAGUE_CODES = ["PL", "PD", "BL1", "SA", "FL1", "DED", "PPL"]

OUTPUT_PATH = PROCESSED_DIR / "domestic_league_form_2026_2027.json"


def _fetch_standings(code: str, key: str) -> dict | None:
    headers = {"X-Auth-Token": key}
    for attempt in range(3):
        try:
            resp = requests.get(
                f"{BASE_URL}/competitions/{code}/standings",
                headers=headers, params={"season": SEASON}, timeout=30,
            )
        except requests.RequestException as exc:
            print(f"  {code}: istek hatası ({exc})", flush=True)
            if attempt < 2:
                time.sleep(3)
                continue
            return None
        if resp.status_code == 429:
            print(f"  {code}: rate limited, 60s bekleniyor…", flush=True)
            time.sleep(60)
            continue
        if resp.status_code != 200:
            print(f"  {code}: HTTP {resp.status_code}", flush=True)
            return None
        return resp.json()
    return None


def main() -> None:
    ensure_data_dirs()
    key = load_settings().football_data_key
    if not key:
        print("UYARI: FOOTBALL_DATA_KEY eksik — iç lig formu atlandı.")
        return

    teams: dict[str, dict] = {}
    for code in LEAGUE_CODES:
        print(f"{code} puan durumu çekiliyor…", flush=True)
        data = _fetch_standings(code, key)
        time.sleep(2)
        if not data:
            continue
        standings = data.get("standings") or []
        total_table = next((s.get("table", []) for s in standings if s.get("type") == "TOTAL"), [])
        for row in total_table:
            team = row.get("team") or {}
            name = team.get("name")
            played = row.get("playedGames") or 0
            if not name or played < 1:
                continue
            teams[name] = {
                "league": code,
                "played": played,
                "points": row.get("points", 0),
                "points_per_game": round(row.get("points", 0) / played, 3),
                "goals_for_per_match": round((row.get("goalsFor") or 0) / played, 3),
                "goals_against_per_match": round((row.get("goalsAgainst") or 0) / played, 3),
                "position": row.get("position"),
            }
        print(f"  {len(total_table)} takım", flush=True)

    payload = {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "season": f"{SEASON}-{SEASON + 1}",
        "leagues": LEAGUE_CODES,
        "teams": teams,
    }
    OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nKaydedildi: {OUTPUT_PATH} ({len(teams)} takım)")


if __name__ == "__main__":
    main()
