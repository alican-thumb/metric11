"""UEFA Şampiyonlar Ligi, Avrupa Ligi ve Konferans Ligi 2026-27 fixture verisi toplar.

football-data.org API kullanır (FOOTBALL_DATA_KEY).
Çıktı: data/processed/european_fixtures_2026_2027.json
"""
from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from src.config import PROCESSED_DIR, ensure_data_dirs, load_settings

BASE_URL = "https://api.football-data.org/v4"
SEASON = 2026

# (kod, kısa_ad, tam_ad)
COMPETITIONS = [
    ("CL",  "UCL",  "UEFA Şampiyonlar Ligi"),
    ("EL",  "UEL",  "UEFA Avrupa Ligi"),
    ("ECL", "UECL", "UEFA Konferans Ligi"),
]

# İzlenen Türk kulüpler (football-data.org takım adlarıyla eşleşme için)
TURKISH_CLUBS = {
    "Fenerbahçe",
    "Galatasaray",
    "Beşiktaş",
    "Trabzonspor",
    "Başakşehir",
}


def _fetch(url: str, key: str, params: dict | None = None, retries: int = 3) -> dict:
    import requests

    headers = {"X-Auth-Token": key}
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=30)
            if resp.status_code == 429:
                print("  Rate limited. 60s bekleniyor…", flush=True)
                time.sleep(60)
                continue
            if resp.status_code == 404:
                print(f"  {url} — sezon henüz mevcut değil (404)", flush=True)
                return {}
            if not (200 <= resp.status_code < 300):
                print(f"  HTTP {resp.status_code}: {url}", flush=True)
                if attempt < retries - 1:
                    time.sleep(3)
                    continue
                return {}
            return resp.json()
        except Exception as exc:
            print(f"  Hata (deneme {attempt+1}): {exc}", flush=True)
            if attempt < retries - 1:
                time.sleep(3)
    return {}


def _build_match(match: dict) -> dict:
    home = match.get("homeTeam") or {}
    away = match.get("awayTeam") or {}
    score = (match.get("score") or {})
    ft = score.get("fullTime") or {}
    pen = score.get("penalties") or {}
    et = score.get("extraTime") or {}
    return {
        "id": match.get("id"),
        "matchday": match.get("matchday"),
        "stage": match.get("stage", ""),
        "group": match.get("group") or "",
        "utc_date": match.get("utcDate", ""),
        "status": match.get("status", ""),
        "home": {
            "id": home.get("id"),
            "name": home.get("name", ""),
            "short": home.get("tla", ""),
            "crest": home.get("crest", ""),
        },
        "away": {
            "id": away.get("id"),
            "name": away.get("name", ""),
            "short": away.get("tla", ""),
            "crest": away.get("crest", ""),
        },
        "score": {
            "home": ft.get("home"),
            "away": ft.get("away"),
            "extra_time_home": et.get("home"),
            "extra_time_away": et.get("away"),
            "penalties_home": pen.get("home"),
            "penalties_away": pen.get("away"),
            "winner": score.get("winner"),
        },
    }


def fetch_competition(key: str, code: str, short: str, name: str) -> dict:
    print(f"\n{name} ({code}) çekiliyor…", flush=True)

    # Maçlar
    url = f"{BASE_URL}/competitions/{code}/matches"
    data = _fetch(url, key, params={"season": SEASON})
    raw_matches = data.get("matches") or []
    matches = [_build_match(m) for m in raw_matches]

    # Takımlar
    time.sleep(1)
    url_teams = f"{BASE_URL}/competitions/{code}/teams"
    tdata = _fetch(url_teams, key, params={"season": SEASON})
    teams_raw = tdata.get("teams") or []
    teams = {
        str(t.get("id")): {
            "id": t.get("id"),
            "name": t.get("name", ""),
            "short": t.get("tla", ""),
            "crest": t.get("crest", ""),
            "country": t.get("area", {}).get("name", ""),
        }
        for t in teams_raw
    }

    turkish_ids = {
        tid for tid, t in teams.items()
        if any(tc.lower() in t.get("name", "").lower() for tc in TURKISH_CLUBS)
    }

    print(f"  {len(matches)} maç, {len(teams)} takım "
          f"({len(turkish_ids)} Türk kulüp)", flush=True)

    return {
        "code": code,
        "short": short,
        "name": name,
        "season": SEASON,
        "matches": matches,
        "teams": teams,
        "turkish_team_ids": list(turkish_ids),
    }


def main() -> None:
    ensure_data_dirs()

    settings = load_settings()
    key = settings.football_data_key
    if not key:
        print("UYARI: FOOTBALL_DATA_KEY eksik — European fixtures atlandı.", file=sys.stderr)
        sys.exit(0)

    results: dict[str, dict] = {}
    for code, short, name in COMPETITIONS:
        comp_data = fetch_competition(key, code, short, name)
        results[code] = comp_data
        time.sleep(2)

    total_matches = sum(len(c["matches"]) for c in results.values())

    payload = {
        "season": f"{SEASON}-{SEASON + 1}",
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "competitions": results,
        "total_matches": total_matches,
    }

    out_path = PROCESSED_DIR / f"european_fixtures_{SEASON}_{SEASON + 1}.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nKaydedildi: {out_path}")
    print(f"Toplam: {total_matches} maç")


if __name__ == "__main__":
    main()
