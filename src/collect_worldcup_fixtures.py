"""Collect FIFA World Cup 2026 fixture and team data from football-data.org API."""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from src.config import PROCESSED_DIR, ensure_data_dirs, load_settings

BASE_URL = "https://api.football-data.org/v4"


def _get_headers(key: str) -> dict[str, str]:
    return {"X-Auth-Token": key}


def _fetch(url: str, key: str, retries: int = 3) -> dict:
    import requests

    headers = _get_headers(key)
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=headers, timeout=30)
            if resp.status_code == 429:
                wait = 60
                print(f"  Rate limited. {wait}s bekleniyor…", flush=True)
                time.sleep(wait)
                continue
            if not (200 <= resp.status_code < 300):
                print(f"  HTTP {resp.status_code}: {url}", flush=True)
                if attempt < retries - 1:
                    time.sleep(2)
                    continue
                return {}
            return resp.json()
        except Exception as exc:
            print(f"  Hata (deneme {attempt+1}): {exc}", flush=True)
            if attempt < retries - 1:
                time.sleep(2)
    return {}


def _build_team_entry(team: dict) -> dict:
    return {
        "name": team.get("name", ""),
        "short": team.get("tla", ""),
        "crest": team.get("crest", ""),
    }


def _build_match_entry(match: dict, teams_map: dict) -> dict:
    home_team = match.get("homeTeam") or {}
    away_team = match.get("awayTeam") or {}
    score_data = match.get("score") or {}
    full_time = score_data.get("fullTime") or {}

    home_id = str(home_team.get("id", ""))
    away_id = str(away_team.get("id", ""))

    home_info = teams_map.get(home_id, {})
    away_info = teams_map.get(away_id, {})

    home_entry = {
        "id": home_team.get("id"),
        "name": home_team.get("name") or home_info.get("name", ""),
        "short": home_team.get("tla") or home_info.get("short", ""),
        "crest": home_team.get("crest") or home_info.get("crest", ""),
    }
    away_entry = {
        "id": away_team.get("id"),
        "name": away_team.get("name") or away_info.get("name", ""),
        "short": away_team.get("tla") or away_info.get("short", ""),
        "crest": away_team.get("crest") or away_info.get("crest", ""),
    }

    score_home = full_time.get("home")
    score_away = full_time.get("away")

    return {
        "id": match.get("id"),
        "matchday": match.get("matchday"),
        "stage": match.get("stage", ""),
        "group": match.get("group") or "",
        "utc_date": match.get("utcDate", ""),
        "status": match.get("status", ""),
        "home": home_entry,
        "away": away_entry,
        "score": {
            "home": score_home,
            "away": score_away,
            "winner": score_data.get("winner"),
        },
    }


def fetch_teams(key: str) -> dict[str, dict]:
    """Fetch WC 2026 teams and return a map of id -> team entry."""
    print("Takımlar çekiliyor…", flush=True)
    url = f"{BASE_URL}/competitions/WC/teams"
    data = _fetch(url, key)
    teams_map: dict[str, dict] = {}
    teams_list = data.get("teams") or []
    for team in teams_list:
        tid = str(team.get("id", ""))
        if tid:
            teams_map[tid] = _build_team_entry(team)
    print(f"  {len(teams_map)} takım bulundu.", flush=True)
    return teams_map


def fetch_matches(key: str, teams_map: dict[str, dict]) -> list[dict]:
    """Fetch all WC 2026 matches."""
    print("Maçlar çekiliyor…", flush=True)
    url = f"{BASE_URL}/competitions/WC/matches"
    data = _fetch(url, key)
    raw_matches = data.get("matches") or []
    matches = []
    for match in raw_matches:
        entry = _build_match_entry(match, teams_map)
        matches.append(entry)
    print(f"  {len(matches)} maç bulundu.", flush=True)
    return matches


def main() -> None:
    parser = argparse.ArgumentParser(
        description="FIFA Dünya Kupası 2026 fixture verisi çeker (football-data.org)."
    )
    parser.add_argument(
        "--output",
        default=str(PROCESSED_DIR / "worldcup_2026_fixtures.json"),
        help="Çıktı JSON dosyası",
    )
    args = parser.parse_args()

    ensure_data_dirs()

    settings = load_settings()
    key = settings.football_data_key
    if not key:
        print("UYARI: FOOTBALL_DATA_KEY eksik, worldcup fixture toplama atlandı.", file=sys.stderr)
        sys.exit(0)

    teams_map = fetch_teams(key)
    time.sleep(1)
    matches = fetch_matches(key, teams_map)

    payload = {
        "season": "2026",
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "matches": matches,
        "teams": teams_map,
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nKaydedildi: {out_path}", flush=True)
    print(f"Toplam maç: {len(matches)}, takım: {len(teams_map)}", flush=True)


if __name__ == "__main__":
    main()
