"""
Sofascore'dan Süper Lig 2025/26 maç istatistiklerini toplar.
Kaynak: api.sofascore.com (ücretsiz, kamusal API)
Çekilen veriler: xG, şut, şuta isabet, korner, faul, possession, pas, hava topu
"""
from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

from src.config import PROCESSED_DIR, RAW_DIR

SOFASCORE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "application/json",
    "Referer": "https://www.sofascore.com/",
}

TOURNAMENT_ID = 52
SEASON_ID = 77805  # Super Lig 25/26

SOFASCORE_TO_TFF = {
    "Alanyaspor": "CORENDON ALANYASPOR",
    "Antalyaspor": "HESAP.COM ANTALYASPOR",
    "Başakşehir FK": "RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ",
    "Beşiktaş JK": "BEŞİKTAŞ A.Ş.",
    "Eyüpspor": "İKAS EYÜPSPOR",
    "Fatih Karagümrük": "MISIRLI.COM.TR FATİH KARAGÜMRÜK",
    "Fenerbahçe": "FENERBAHÇE A.Ş.",
    "Galatasaray": "GALATASARAY A.Ş.",
    "Gaziantep FK": "GAZİANTEP FUTBOL KULÜBÜ A.Ş.",
    "Gençlerbirliği": "GENÇLERBİRLİĞİ",
    "Göztepe": "GÖZTEPE A.Ş.",
    "Kasımpaşa": "KASIMPAŞA A.Ş.",
    "Kayserispor": "ZECORNER KAYSERİSPOR",
    "Kocaelispor": "KOCAELİSPOR",
    "Konyaspor": "TÜMOSAN KONYASPOR",
    "Samsunspor": "SAMSUNSPOR A.Ş.",
    "Trabzonspor": "TRABZONSPOR A.Ş.",
    "Çaykur Rizespor": "ÇAYKUR RİZESPOR A.Ş.",
}

STAT_KEYS = {
    "Expected goals": ("xg_home", "xg_away"),
    "Total shots": ("shots_home", "shots_away"),
    "Shots on target": ("shots_on_target_home", "shots_on_target_away"),
    "Shots inside box": ("shots_inside_box_home", "shots_inside_box_away"),
    "Big chances": ("big_chances_home", "big_chances_away"),
    "Ball possession": ("possession_home", "possession_away"),
    "Corner kicks": ("corners_home", "corners_away"),
    "Fouls": ("fouls_home", "fouls_away"),
    "Passes": ("passes_home", "passes_away"),
    "Accurate passes": ("accurate_passes_home", "accurate_passes_away"),
    "Aerial duels": ("aerial_duels_home", "aerial_duels_away"),
    "Goals prevented": ("goals_prevented_home", "goals_prevented_away"),
}


def _get(url: str, delay: float = 0.4) -> dict | None:
    time.sleep(delay)
    try:
        r = requests.get(url, headers=SOFASCORE_HEADERS, timeout=15)
        if r.status_code == 200:
            return r.json()
        return None
    except Exception:
        return None


def collect_all_events(season_id: int = SEASON_ID) -> list[dict]:
    events = []
    page = 0
    while True:
        url = f"https://api.sofascore.com/api/v1/unique-tournament/{TOURNAMENT_ID}/season/{season_id}/events/last/{page}"
        data = _get(url)
        if not data:
            break
        batch = data.get("events", [])
        events.extend(batch)
        if not data.get("hasNextPage", False) or not batch:
            break
        page += 1
    return events


def parse_stat_value(val: str | None) -> float | None:
    if val is None:
        return None
    s = str(val).strip().replace("%", "").replace(",", ".")
    try:
        return float(s.split("/")[0].strip())
    except (ValueError, IndexError):
        return None


def collect_match_statistics(event_id: int) -> dict:
    url = f"https://api.sofascore.com/api/v1/event/{event_id}/statistics"
    data = _get(url, delay=0.35)
    result: dict[str, float | None] = {}
    if not data:
        return result
    for period_block in data.get("statistics", []):
        if period_block.get("period") != "ALL":
            continue
        for group in period_block.get("groups", []):
            for item in group.get("statisticsItems", []):
                name = item.get("name")
                if name not in STAT_KEYS:
                    continue
                home_key, away_key = STAT_KEYS[name]
                result[home_key] = parse_stat_value(item.get("home"))
                result[away_key] = parse_stat_value(item.get("away"))
    return result


def build_match_record(event: dict, stats: dict) -> dict:
    ts = event.get("startTimestamp", 0)
    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    home_name = event.get("homeTeam", {}).get("name", "")
    away_name = event.get("awayTeam", {}).get("name", "")
    return {
        "sofascore_id": event.get("id"),
        "date": dt.strftime("%Y-%m-%d"),
        "round": event.get("roundInfo", {}).get("round"),
        "home_team_sofascore": home_name,
        "away_team_sofascore": away_name,
        "home_team_tff": SOFASCORE_TO_TFF.get(home_name),
        "away_team_tff": SOFASCORE_TO_TFF.get(away_name),
        "home_score": event.get("homeScore", {}).get("normaltime"),
        "away_score": event.get("awayScore", {}).get("normaltime"),
        "has_xg": event.get("hasXg", False),
        "stats": stats,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Sofascore Suer Lig 2025/26 mac istatistiklerini toplar.")
    parser.add_argument("--season-id", type=int, default=SEASON_ID)
    parser.add_argument("--output", default=str(PROCESSED_DIR / "sofascore_match_stats_2025_2026.json"))
    parser.add_argument("--delay", type=float, default=0.4, help="API istekleri arasi gecikme (saniye)")
    parser.add_argument("--skip-existing", action="store_true", help="Mevcut dosyada kayitli macları atla")
    args = parser.parse_args()

    output_path = Path(args.output)
    existing: dict[int, dict] = {}
    if args.skip_existing and output_path.exists():
        for rec in json.loads(output_path.read_text(encoding="utf-8")).get("matches", []):
            existing[rec["sofascore_id"]] = rec

    print("Sofascore etkinlikleri cekiliyor...")
    events = collect_all_events(args.season_id)
    finished = [e for e in events if e.get("status", {}).get("type") == "finished"]
    print(f"Toplam biten mac: {len(finished)}")

    records = []
    for i, event in enumerate(finished):
        eid = event.get("id")
        if eid in existing:
            records.append(existing[eid])
            continue
        stats = collect_match_statistics(eid)
        record = build_match_record(event, stats)
        records.append(record)
        if (i + 1) % 20 == 0:
            print(f"  {i+1}/{len(finished)} islendi...")

    with_stats = sum(1 for r in records if r["stats"])
    with_xg = sum(1 for r in records if r["stats"].get("xg_home") is not None)
    output = {
        "season": "2025/26",
        "tournament_id": TOURNAMENT_ID,
        "season_id": args.season_id,
        "total_matches": len(records),
        "matches_with_stats": with_stats,
        "matches_with_xg": with_xg,
        "matches": records,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nKaydedildi: {output_path}")
    print(f"Toplam mac: {len(records)} | Statsli: {with_stats} | xGli: {with_xg}")


if __name__ == "__main__":
    main()
