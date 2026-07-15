"""Süper Lig takım çiftleri için API-Football kafa kafaya (head-to-head) geçmiş sonuç verisi toplar.

Beraberlik tahmini uzun süredir bu projede zayıf kaldı (bkz. PROJECT_STATE.md); kök neden
olarak "kafa kafaya tarihsel beraberlik oranı veya bahis piyasası verisi gerekir" tespit
edilmişti. Bu modül o eksik sinyali üretir: iki takımın API-Football'da kayıtlı geçmiş
maçlarından beraberlik oranını hesaplar ve `src/preview/probability.py` içindeki
`draw_calibration_signal`'a gerçek bir ek girdi olarak bağlanır.

Ücretsiz API-Football planının günlük kota sınırı düşük olduğundan bu koleksiyon
`--limit` ile sınırlanır ve `--skip-existing` ile birden fazla gece boyunca kademeli
tamamlanır (tıpkı TFF oyuncu profili toplama kuyruğu gibi).
"""
from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from src.config import PROCESSED_DIR, SEASON, ensure_data_dirs, load_settings
from src.http_client import get_url

BASE_URL = "https://v3.football.api-sports.io"
TEAM_IDS_PATH = Path("data/manual/api_football_team_ids.json")
OUTPUT_JSON = PROCESSED_DIR / f"head_to_head_history_{SEASON}.json"
OUTPUT_MD = PROCESSED_DIR / f"head_to_head_history_{SEASON}.md"

MIN_MATCHES_FOR_SIGNAL = 3


def _pair_key(team_a: str, team_b: str) -> str:
    return "|".join(sorted([team_a, team_b]))


def _load_team_ids() -> dict:
    payload = json.loads(TEAM_IDS_PATH.read_text(encoding="utf-8"))
    return {item["team_name"]: item for item in payload["teams"]}


def _save_team_ids(teams_by_name: dict) -> None:
    payload = {
        "note": (
            "TFF takım adı -> API-Football (v3.football.api-sports.io) takım id eşlemesi. "
            "Kafa kafaya (head-to-head) tarihsel beraberlik oranı toplamak için kullanılır. "
            "id=null olan takımlar collect_head_to_head_history.py tarafından 'search' adıyla "
            "otomatik çözülüp bu dosyaya geri yazılır."
        ),
        "teams": list(teams_by_name.values()),
    }
    TEAM_IDS_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _resolve_team_id(search_name: str, key: str) -> int | None:
    result = get_url(f"{BASE_URL}/teams?search={search_name}", headers={"x-apisports-key": key})
    if not result.ok or not isinstance(result.json_data, dict):
        return None
    for item in result.json_data.get("response") or []:
        team = item.get("team", {})
        if team.get("country") == "Turkey":
            return team.get("id")
    return None


def _fetch_h2h(id_a: int, id_b: int, key: str) -> list[dict]:
    # Not: "last" parametresi ücretsiz planda desteklenmiyor ("Free plans do not have
    # access to the Last parameter."); parametresiz çağrı tüm geçmişi (~2010'lardan bu
    # yana Süper Lig eşleşmeleri) tek seferde döndürüyor.
    url = f"{BASE_URL}/fixtures/headtohead?h2h={id_a}-{id_b}"
    for attempt in range(3):
        result = get_url(url, headers={"x-apisports-key": key})
        if result.status_code == 429:
            print("  Rate limit, 65s bekleniyor…", flush=True)
            time.sleep(65)
            continue
        if not result.ok:
            return []
        data = result.json_data if isinstance(result.json_data, dict) else {}
        return data.get("response") or []
    return []


def _summarize(fixtures: list[dict], id_a: int) -> dict:
    matches = draws = a_wins = b_wins = 0
    last_date = None
    for fixture in fixtures:
        status = (fixture.get("fixture") or {}).get("status", {}).get("short")
        if status != "FT":
            continue
        goals = fixture.get("goals") or {}
        home_goals, away_goals = goals.get("home"), goals.get("away")
        if home_goals is None or away_goals is None:
            continue
        teams = fixture.get("teams") or {}
        home_is_a = (teams.get("home") or {}).get("id") == id_a
        a_goals = home_goals if home_is_a else away_goals
        b_goals = away_goals if home_is_a else home_goals
        matches += 1
        if a_goals > b_goals:
            a_wins += 1
        elif a_goals < b_goals:
            b_wins += 1
        else:
            draws += 1
        date = (fixture.get("fixture") or {}).get("date")
        if date and (last_date is None or date > last_date):
            last_date = date
    return {
        "matches": matches,
        "draws": draws,
        "draw_rate": round(draws / matches, 3) if matches else None,
        "last_meeting_date": last_date,
    }


def build_markdown(payload: dict) -> str:
    pairs = payload.get("pairs", {})
    with_data = [p for p in pairs.values() if p.get("matches")]
    lines = [
        "# Kafa Kafaya (Head-to-Head) Beraberlik Geçmişi",
        "",
        f"Üretim zamanı: {payload.get('generated_at')}",
        f"Toplanan takım çifti: {len(pairs)}",
        f"Veri bulunan çift: {len(with_data)}",
        "",
        "## Beraberlik Oranı En Yüksek Çiftler",
        "",
    ]
    ranked = sorted(
        (p for p in with_data if p["matches"] >= MIN_MATCHES_FOR_SIGNAL),
        key=lambda p: p["draw_rate"],
        reverse=True,
    )
    for pair in ranked[:20]:
        lines.append(
            f"- {pair['team_a']} vs {pair['team_b']}: {pair['matches']} maç, "
            f"beraberlik oranı %{round(pair['draw_rate'] * 100)} ({pair['draws']} beraberlik)"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    ensure_data_dirs()
    parser = argparse.ArgumentParser(description="API-Football kafa kafaya (h2h) tarihsel beraberlik oranı toplar.")
    parser.add_argument("--limit", type=int, default=60, help="Bu çalıştırmada en fazla kaç yeni takım çifti çekilsin.")
    parser.add_argument("--delay-seconds", type=float, default=1.5)
    args = parser.parse_args()

    settings = load_settings()
    key = settings.api_football_key
    if not key:
        print("API_FOOTBALL_KEY bulunamadı; h2h toplama atlandı (.env veya secrets içine eklenirse çalışır).")
        return

    team_ids = _load_team_ids()
    payload = (
        json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
        if OUTPUT_JSON.exists()
        else {"pairs": {}}
    )
    pairs_out = payload.get("pairs", {})

    names = sorted(team_ids.keys())
    fetched_this_run = 0
    resolved_any = False
    skipped_no_id = []

    for i, name_a in enumerate(names):
        if fetched_this_run >= args.limit:
            break
        for name_b in names[i + 1:]:
            if fetched_this_run >= args.limit:
                break
            key_pair = _pair_key(name_a, name_b)
            if key_pair in pairs_out:
                continue

            for name in (name_a, name_b):
                if team_ids[name].get("id") is None:
                    resolved = _resolve_team_id(team_ids[name]["search"], key)
                    if resolved:
                        team_ids[name]["id"] = resolved
                        resolved_any = True
                        time.sleep(args.delay_seconds)

            id_a, id_b = team_ids[name_a].get("id"), team_ids[name_b].get("id")
            if id_a is None or id_b is None:
                skipped_no_id.append(key_pair)
                continue

            fixtures = _fetch_h2h(id_a, id_b, key)
            summary = _summarize(fixtures, id_a)
            summary["team_a"] = name_a
            summary["team_b"] = name_b
            pairs_out[key_pair] = summary
            fetched_this_run += 1
            print(f"  {name_a} vs {name_b}: {summary['matches']} maç, draw_rate={summary['draw_rate']}", flush=True)
            time.sleep(args.delay_seconds)

    if resolved_any:
        _save_team_ids(team_ids)

    total_pairs_possible = len(names) * (len(names) - 1) // 2
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "season": SEASON,
        "total_pairs_possible": total_pairs_possible,
        "collected_pairs": len(pairs_out),
        "fetched_this_run": fetched_this_run,
        "skipped_missing_team_id": skipped_no_id,
        "pairs": pairs_out,
    }
    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    OUTPUT_MD.write_text(build_markdown(payload), encoding="utf-8")
    print(f"Toplam: {len(pairs_out)}/{total_pairs_possible} çift; bu çalıştırmada {fetched_this_run} yeni çift çekildi.")


if __name__ == "__main__":
    main()
