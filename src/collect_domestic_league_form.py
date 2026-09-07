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
# `tff_super_lig_matches_2026_2027.json` (tam kadro/11 verisi) skoru geç yakalıyor —
# 2026-09-07'de Fenerbahçe'nin en güncel (ve en anlamlı) sonucu olan Beşiktaş
# maçının skoru o dosyada hâlâ boştu. Fikstür dosyası skoru çok daha erken alıyor
# (bkz. `advance_season_state.py`), o yüzden puan durumu BUNDAN türetilir.
TURKISH_FIXTURES_PATH = PROCESSED_DIR / "tff_super_lig_fixtures_2026_2027.json"

# 2026-09-07 bulgusu: docstring "Süper Lig zaten ayrı (TFF) toplanıyor" diyordu ama hiçbir
# yerde gerçekten `teams`'e eklenmiyordu — Avrupa kupasındaki Galatasaray/Fenerbahçe/
# Beşiktaş/Trabzonspor `analyze_european_predictions.py`'de SADECE statik 2024-25 UEFA
# katsayı tablosuyla değerlendiriliyordu, güncel sezon Süper Lig formu hiç yansımıyordu.
# `_CLUB_STRENGTH` tablosundaki aynı kısa adlarla eşleşsin diye (substring eşleşme,
# bkz. `_domestic_form_for`) TFF'nin resmi uzun adlarını kısa görünen ada çeviriyoruz.
_TURKISH_DISPLAY_NAME: dict[str, str] = {
    "GALATASARAY A.Ş.": "Galatasaray",
    "FENERBAHÇE A.Ş.": "Fenerbahçe",
    "BEŞİKTAŞ A.Ş.": "Beşiktaş",
    "TRABZONSPOR A.Ş.": "Trabzonspor",
    "İSTANBUL BAŞAKŞEHİR FK": "Başakşehir",
    "RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ": "Başakşehir",
    "KASIMPAŞA A.Ş.": "Kasımpaşa",
}


def _load_turkish_standings() -> dict[str, dict]:
    """TFF fikstür dosyasından (zaten toplanmış, ağ çağrısı YOK) güncel Süper Lig
    puan/gol formunu, football-data.org standings ile aynı şekle çevirir."""
    try:
        fixtures = json.loads(TURKISH_FIXTURES_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

    agg: dict[str, dict] = {}
    for week in fixtures.get("weeks", []):
        for m in week.get("matches", []):
            score = (m.get("score") or "").strip()
            if not score or score == "-":
                continue
            try:
                hs_str, as_str = [part.strip() for part in score.split("-")]
                hs, as_ = int(hs_str), int(as_str)
            except ValueError:
                continue
            for name, gf, ga in (
                (m.get("home_team"), hs, as_),
                (m.get("away_team"), as_, hs),
            ):
                if not name:
                    continue
                row = agg.setdefault(name, {"played": 0, "points": 0, "gf": 0, "ga": 0})
                row["played"] += 1
                row["gf"] += gf
                row["ga"] += ga
                row["points"] += 3 if gf > ga else 1 if gf == ga else 0

    out: dict[str, dict] = {}
    for tff_name, row in agg.items():
        display = _TURKISH_DISPLAY_NAME.get(tff_name)
        if not display or row["played"] < 1:
            continue
        played = row["played"]
        out[display] = {
            "league": "TR1",
            "played": played,
            "points": row["points"],
            "points_per_game": round(row["points"] / played, 3),
            "goals_for_per_match": round(row["gf"] / played, 3),
            "goals_against_per_match": round(row["ga"] / played, 3),
            "position": None,
        }
    return out


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


def _load_existing_teams() -> dict[str, dict]:
    try:
        payload = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    return payload.get("teams", {})


def main() -> None:
    ensure_data_dirs()
    key = load_settings().football_data_key
    teams: dict[str, dict] = {}
    if not key:
        # Anahtar yoksa (ör. bu makinede FOOTBALL_DATA_KEY tanımlı değil) yabancı kulüp
        # formunu yeniden çekemeyiz — dosyayı BOŞ yabancı-takım listesiyle EZMEK yerine
        # önceki (muhtemelen CI'da anahtarla üretilmiş) çekimi koru, yalnız Süper Lig
        # kısmını üstüne güncelle. (2026-09-07 — bu koruma olmadan yerel bir çalıştırma
        # 126 yabancı takımı sessizce sıfıra indirmişti.)
        teams = _load_existing_teams()
        print(f"UYARI: FOOTBALL_DATA_KEY eksik — yabancı kulüp formu atlanıyor, önceki çekim korunuyor ({len(teams)} takım).")
    for code in ([] if not key else LEAGUE_CODES):
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

    turkish_teams = _load_turkish_standings()
    teams.update(turkish_teams)
    print(f"Süper Lig (TFF, ağ çağrısı yok): {len(turkish_teams)} takım", flush=True)

    payload = {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "season": f"{SEASON}-{SEASON + 1}",
        "leagues": LEAGUE_CODES + ["TR1"],
        "teams": teams,
    }
    OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nKaydedildi: {OUTPUT_PATH} ({len(teams)} takım)")


if __name__ == "__main__":
    main()
