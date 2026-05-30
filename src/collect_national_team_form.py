"""Milli takım form verisi toplar: Euro 2024, Copa América, AFCON, Asian Cup, WC 2022."""
from __future__ import annotations

import json
import os
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from src.config import PROCESSED_DIR

BASE_URL = "https://v3.football.api-sports.io"

# (league_id, season, label, ağırlık) — en yakın tarih en ağırlıklı
TOURNAMENTS = [
    (4,  2024, "UEFA Euro 2024",          1.0),
    (9,  2024, "Copa América 2024",        1.0),
    (3,  2024, "AFCON 2024",               1.0),
    (17, 2024, "Asian Cup 2023/24",        1.0),
    (1,  2022, "WC 2022",                  0.7),
]

# API-Football takım adı → football-data.org takım adı (WC fixture'larında kullanılan)
NAME_MAP: dict[str, str] = {
    "United States":             "United States",
    "USA":                       "United States",
    "IR Iran":                   "Iran",
    "Korea Republic":            "South Korea",
    "Republic of Ireland":       "Republic of Ireland",
    "Ivory Coast":               "Ivory Coast",
    "Cote d'Ivoire":             "Ivory Coast",
    "DR Congo":                  "Congo DR",
    "Cape Verde":                "Cape Verde Islands",
    "Czech Republic":            "Czechia",
    "Bosnia":                    "Bosnia-Herzegovina",
    "Bosnia and Herzegovina":    "Bosnia-Herzegovina",
    "New Zealand":               "New Zealand",
    "Saudi Arabia":              "Saudi Arabia",
    "South Africa":              "South Africa",
}


def _normalize(name: str) -> str:
    return NAME_MAP.get(name, name)


def _fetch(endpoint: str, key: str) -> list[dict]:
    import requests
    headers = {"x-apisports-key": key}
    url = f"{BASE_URL}/{endpoint}"
    for attempt in range(3):
        try:
            r = requests.get(url, headers=headers, timeout=30)
            if r.status_code == 429:
                print("  Rate limit, 65s bekleniyor…", flush=True)
                time.sleep(65)
                continue
            r.raise_for_status()
            return r.json().get("response", [])
        except Exception as exc:
            if attempt == 2:
                print(f"  HATA {url}: {exc}", flush=True)
                return []
            time.sleep(5)
    return []


def collect(key: str) -> dict:
    # team_name → istatistik toplayıcı
    stats: dict[str, dict] = defaultdict(lambda: {
        "matches": 0, "wins": 0, "draws": 0, "losses": 0,
        "gf": 0.0, "ga": 0.0, "weighted_matches": 0.0,
        "weighted_gf": 0.0, "weighted_ga": 0.0,
        "tournaments": [],
    })

    for lid, season, label, weight in TOURNAMENTS:
        print(f"  {label} çekiliyor…", flush=True)
        fixtures = _fetch(f"fixtures?league={lid}&season={season}&status=FT", key)
        print(f"    {len(fixtures)} maç bulundu.", flush=True)

        teams_in_tournament: set[str] = set()
        for fix in fixtures:
            home_raw = fix["teams"]["home"]["name"]
            away_raw = fix["teams"]["away"]["name"]
            home = _normalize(home_raw)
            away = _normalize(away_raw)
            gf_h = fix["goals"]["home"] or 0
            gf_a = fix["goals"]["away"] or 0

            # Penaltı (seri) gollerini sayma — düz skor kullan
            score_ft = fix.get("score", {}).get("fulltime", {})
            if score_ft.get("home") is not None:
                gf_h = score_ft["home"] or 0
                gf_a = score_ft["away"] or 0

            for team, gf, ga in [(home, gf_h, gf_a), (away, gf_a, gf_h)]:
                s = stats[team]
                s["matches"] += 1
                s["gf"] += gf
                s["ga"] += ga
                s["weighted_matches"] += weight
                s["weighted_gf"] += gf * weight
                s["weighted_ga"] += ga * weight
                if gf > ga:
                    s["wins"] += 1
                elif gf == ga:
                    s["draws"] += 1
                else:
                    s["losses"] += 1
                teams_in_tournament.add(team)

        for team in teams_in_tournament:
            if label not in stats[team]["tournaments"]:
                stats[team]["tournaments"].append(label)

        time.sleep(1)

    result: dict[str, dict] = {}
    for team, s in stats.items():
        m = s["matches"]
        wm = s["weighted_matches"]
        if m == 0:
            continue
        result[team] = {
            "matches": m,
            "wins": s["wins"],
            "draws": s["draws"],
            "losses": s["losses"],
            "gf_per_match": round(s["gf"] / m, 3),
            "ga_per_match": round(s["ga"] / m, 3),
            "win_rate": round(s["wins"] / m, 3),
            # Ağırlıklı (yakın tarih daha önemli)
            "w_gf_per_match": round(s["weighted_gf"] / wm, 3) if wm else 0,
            "w_ga_per_match": round(s["weighted_ga"] / wm, 3) if wm else 0,
            "tournaments": s["tournaments"],
        }

    return result


def main() -> None:
    key = os.getenv("API_FOOTBALL_KEY") or ""
    if not key:
        # config'den dene
        try:
            from src.config import load_settings
            key = load_settings().api_football_key or ""
        except Exception:
            pass
    if not key:
        print("UYARI: API_FOOTBALL_KEY eksik, form toplama atlandı.", flush=True)
        raise SystemExit(0)

    print("Milli takım form verisi toplanıyor…", flush=True)
    form = collect(key)

    output = PROCESSED_DIR / "national_team_form.json"
    payload = {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "team_count": len(form),
        "tournaments": [t[2] for t in TOURNAMENTS],
        "teams": form,
    }
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Kaydedildi: {output} ({len(form)} takım)", flush=True)


if __name__ == "__main__":
    main()
