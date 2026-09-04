"""UEFA Şampiyonlar Ligi, Avrupa Ligi ve Konferans Ligi 2026-27 fixture verisi toplar.

football-data.org API kullanır (FOOTBALL_DATA_KEY). 2026-09-04'te tespit edildi: bu API'nin
mevcut plan/anahtarı UEL'i vermiyor (HTTP 403 — plan kısıtı) ve UECL'i hiç tanımıyor
(HTTP 404 "sezon henüz mevcut değil" — muhtemelen bu API bu turnuvayı hiç kapsamıyor). CL
sorunsuz çalışıyor. Bu yüzden EL/ECL için API-Football'a (zaten mevcut bir GH secret,
Süper Lig kadro/derin-snapshot toplamada kullanılıyor) düşülür — o API'nin plan kapsamı
daha geniş ve bu iki turnuvayı da içeriyor.
Çıktı: data/processed/european_fixtures_2026_2027.json
"""
from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from src.config import PROCESSED_DIR, ensure_data_dirs, load_settings
from src.http_client import get_url

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

API_FOOTBALL_BASE = "https://v3.football.api-sports.io"
# API-Football'ın sabit lig ID'leri (kamuya açık, uzun süredir değişmeyen kimlikler).
API_FOOTBALL_LEAGUE_IDS = {"EL": 3, "ECL": 848}
# Dönen `league.name` bu anahtar kelimeyi içermezse (yanlış ID/yanlış turnuva ihtimaline
# karşı) sonuç KULLANILMAZ — sessizce boş kadro döner, yanlış veri asla enjekte edilmez.
API_FOOTBALL_NAME_CHECK = {"EL": "europa", "ECL": "conference"}
API_FOOTBALL_FINISHED_STATUSES = {"FT", "AET", "PEN"}

# API-Football'ın `league.round` serbest metnini football-data.org'un kullandığı ve
# build_european_predictions.py'nin `_STAGE_TR`/`stage_order`'ının beklediği sabit
# kodlara çevirir — aksi halde EL/ECL maçları yanlış sırada/çevirisiz görünür.
_ROUND_TO_STAGE_CODE = [
    ("league stage", "LEAGUE_STAGE"),
    ("group", "GROUP_STAGE"),
    ("1st qualifying", "1ST_QUALIFYING_ROUND"),
    ("2nd qualifying", "2ND_QUALIFYING_ROUND"),
    ("3rd qualifying", "3RD_QUALIFYING_ROUND"),
    ("4th qualifying", "4TH_QUALIFYING_ROUND"),
    ("qualifying", "QUALIFYING"),
    ("play-off", "PLAY_OFF_ROUND"),
    ("playoff", "PLAY_OFF_ROUND"),
    ("round of 32", "LAST_32"),
    ("round of 16", "LAST_16"),
    ("quarter", "QUARTER_FINALS"),
    ("semi", "SEMI_FINALS"),
    ("3rd place", "THIRD_PLACE"),
    ("third place", "THIRD_PLACE"),
    ("final", "FINAL"),
]


def _normalize_stage(round_label: str) -> str:
    lowered = (round_label or "").lower()
    for needle, code in _ROUND_TO_STAGE_CODE:
        if needle in lowered:
            return code
    return round_label


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


def _build_match_from_api_football(fx: dict) -> dict:
    fixture = fx.get("fixture") or {}
    teams = fx.get("teams") or {}
    home = teams.get("home") or {}
    away = teams.get("away") or {}
    score = fx.get("score") or {}
    ft = score.get("fulltime") or {}
    et = score.get("extratime") or {}
    pen = score.get("penalty") or {}
    status_short = (fixture.get("status") or {}).get("short", "")
    utc_date = (fixture.get("date") or "").replace("+00:00", "Z")
    round_label = (fx.get("league") or {}).get("round", "") or ""
    matchday = None
    for token in round_label.split():
        if token.isdigit():
            matchday = int(token)
            break
    winner = None
    if home.get("winner") is True:
        winner = "HOME_TEAM"
    elif away.get("winner") is True:
        winner = "AWAY_TEAM"
    elif ft.get("home") is not None and ft.get("home") == ft.get("away"):
        winner = "DRAW"
    return {
        "id": fixture.get("id"),
        "matchday": matchday,
        "stage": _normalize_stage(round_label),
        "group": "",
        "utc_date": utc_date,
        "status": "FINISHED" if status_short in API_FOOTBALL_FINISHED_STATUSES else "TIMED",
        "home": {
            "id": home.get("id"),
            "name": home.get("name", ""),
            "short": (home.get("name") or "")[:3].upper(),
            "crest": home.get("logo", ""),
        },
        "away": {
            "id": away.get("id"),
            "name": away.get("name", ""),
            "short": (away.get("name") or "")[:3].upper(),
            "crest": away.get("logo", ""),
        },
        "score": {
            "home": ft.get("home"),
            "away": ft.get("away"),
            "extra_time_home": et.get("home"),
            "extra_time_away": et.get("away"),
            "penalties_home": pen.get("home"),
            "penalties_away": pen.get("away"),
            "winner": winner,
        },
    }


def fetch_competition_from_api_football(code: str) -> dict | None:
    """football-data.org bu kod için veri veremediğinde (bkz. modül docstring'i) son çare.

    Yanlış lig ID'sine karşı: dönen `league.name` beklenen anahtar kelimeyi içermiyorsa
    (`API_FOOTBALL_NAME_CHECK`) SONUÇ KULLANILMAZ — None döner, çağıran taraf boş kadroya
    düşer (mevcut davranış), asla yanlış turnuva verisi enjekte edilmez.
    """
    league_id = API_FOOTBALL_LEAGUE_IDS.get(code)
    if not league_id:
        return None
    api_key = load_settings().api_football_key
    if not api_key:
        return None
    headers = {"x-apisports-key": api_key}
    result = get_url(f"{API_FOOTBALL_BASE}/fixtures?league={league_id}&season={SEASON}", headers=headers)
    if not result.ok or not isinstance(result.json_data, dict):
        print(f"  API-Football fallback başarısız: {result.error}", flush=True)
        return None
    fixtures = result.json_data.get("response") or []
    if not fixtures:
        return None
    league_name = ((fixtures[0].get("league") or {}).get("name") or "").lower()
    expected = API_FOOTBALL_NAME_CHECK.get(code, "")
    if expected not in league_name:
        print(f"  API-Football fallback reddedildi: beklenen '{expected}', gelen lig adı '{league_name}'", flush=True)
        return None

    matches = [_build_match_from_api_football(fx) for fx in fixtures]
    teams: dict[str, dict] = {}
    for fx in fixtures:
        for side in ("home", "away"):
            t = (fx.get("teams") or {}).get(side) or {}
            tid = t.get("id")
            if tid is None:
                continue
            teams[str(tid)] = {
                "id": tid,
                "name": t.get("name", ""),
                "short": (t.get("name") or "")[:3].upper(),
                "crest": t.get("logo", ""),
                "country": "",
            }
    print(f"  (API-Football fallback) {len(matches)} maç, {len(teams)} takım", flush=True)
    return {"matches": matches, "teams": teams}


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

    if not matches and code in API_FOOTBALL_LEAGUE_IDS:
        fallback = fetch_competition_from_api_football(code)
        if fallback:
            matches = fallback["matches"]
            teams = fallback["teams"] or teams

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
