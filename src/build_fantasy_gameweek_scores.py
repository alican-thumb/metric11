"""Kadro Kur (Fantasy Manager) oyunu için haftalık gerçek maç puanları.

`tff_super_lig_matches_2026_2027.json`'daki GERÇEK ilk 11/gol/kart olaylarından, her
oynanmış hafta için oyuncu başına fantezi puanı hesaplar. Puanlama (klasik FPL mantığı,
asist verisi kaynakta yok — dahil edilmedi, bkz. PROJECT_STATE):

  - İlk 11'de başladı:            +2
  - Gol (pozisyona göre):          FWD +4 · MID +5 · DEF +6 · GK +6
  - Kendi kalesine gol:            -2 (gerçek takımı o maçın kadrosundan bulunur, golün
                                        listelendiği taraftan değil — TFF kendi kalesi
                                        gollerini bazen rakip takımın gol listesinde
                                        gösterir)
  - Sarı kart:                     -1
  - Kırmızı kart / çift sarı:      -3
  - Temiz sayfa (GK/DEF, başladı,
    takım o maçta gol yemedi):     +4
  - Yedekte kalıp girmeyen:         0 (kaçıncı dakika oyuna girdiği veri kaynağında yok)

Kaptan çarpanı (2x) burada UYGULANMAZ — bu yalnızca ham maç puanı, kaptan seçimi
kullanıcıya özel olduğu için uygulama katmanında (predict-app) hesaplanır.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

from src.config import PROCESSED_DIR
from src.normalization import canonical_player_name

TFF_MATCHES_PATH = PROCESSED_DIR / "tff_super_lig_matches_2026_2027.json"
PLAYER_POOL_PATH = PROCESSED_DIR / "fantasy_player_pool_2026_2027.json"
OUTPUT_JSON = PROCESSED_DIR / "fantasy_gameweek_scores_2026_2027.json"
OUTPUT_MD = PROCESSED_DIR / "fantasy_gameweek_scores_2026_2027.md"

OWN_GOAL_TYPE = "K"
GOAL_POINTS = {"GK": 6, "DEF": 6, "MID": 5, "FWD": 4}
DEFAULT_GOAL_POINTS = 5
APPEARANCE_POINTS = 2
YELLOW_CARD_POINTS = -1
RED_CARD_POINTS = -3
CLEAN_SHEET_POINTS = 4
OWN_GOAL_POINTS = -2


def main() -> None:
    matches = json.loads(TFF_MATCHES_PATH.read_text(encoding="utf-8")) if TFF_MATCHES_PATH.exists() else []
    pool_payload = json.loads(PLAYER_POOL_PATH.read_text(encoding="utf-8")) if PLAYER_POOL_PATH.exists() else {"players": []}

    tm_by_tff_id = {p["tff_external_id"]: p for p in pool_payload["players"] if p.get("tff_external_id")}
    position_by_canon = {canonical_player_name(p["name"]): p["position_group"] for p in pool_payload["players"]}

    by_week: dict[int, list[dict]] = {}
    for match in matches:
        week = match.get("fixture_week")
        if week is None:
            continue
        rows = _score_match(match, tm_by_tff_id, position_by_canon)
        by_week.setdefault(week, []).append({"match_id": match.get("external_id"), "players": rows})

    weeks_payload = []
    totals: dict[str, dict] = {}
    for week in sorted(by_week):
        week_matches = by_week[week]
        for wm in week_matches:
            for row in wm["players"]:
                key = row["transfermarkt_id"] or f"tff:{row['tff_external_id']}"
                agg = totals.setdefault(
                    key,
                    {
                        "transfermarkt_id": row["transfermarkt_id"],
                        "tff_external_id": row["tff_external_id"],
                        "name": row["name"],
                        "team": row["team"],
                        "position_group": row["position_group"],
                        "total_points": 0,
                        "gameweeks_played": 0,
                    },
                )
                agg["total_points"] += row["points"]
                if row["started"]:
                    agg["gameweeks_played"] += 1
        weeks_payload.append({"week": week, "matches": week_matches})

    player_totals = sorted(totals.values(), key=lambda r: r["total_points"], reverse=True)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "season": "2026-2027",
        "weeks_scored": len(weeks_payload),
        "weeks": weeks_payload,
        "player_totals": player_totals,
    }
    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    OUTPUT_MD.write_text(_build_report(payload), encoding="utf-8")
    print(_build_report(payload))


def _score_match(match: dict, tm_by_tff_id: dict, position_by_canon: dict) -> list[dict]:
    lineups = match.get("lineups") or {}
    goals = match.get("goals") or {}
    cards = match.get("cards") or {}
    home_score = (match.get("home_team") or {}).get("score")
    away_score = (match.get("away_team") or {}).get("score")

    # external_id -> {team_side, started, name}
    roster: dict[str, dict] = {}
    for side, opposite_conceded in (("home", away_score), ("away", home_score)):
        team_name = (match.get(f"{side}_team") or {}).get("name")
        side_lineup = lineups.get(side) or {}
        for p in side_lineup.get("starting") or []:
            if not p.get("external_id"):
                continue
            roster[p["external_id"]] = {
                "name": p["name"],
                "team": team_name,
                "started": True,
                "conceded": opposite_conceded,
                "points": APPEARANCE_POINTS,
                "goals": 0,
                "own_goals": 0,
                "yellow_cards": 0,
                "red_cards": 0,
            }
        for p in side_lineup.get("bench") or []:
            if not p.get("external_id") or p["external_id"] in roster:
                continue
            roster[p["external_id"]] = {
                "name": p["name"],
                "team": team_name,
                "started": False,
                "conceded": opposite_conceded,
                "points": 0,
                "goals": 0,
                "own_goals": 0,
                "yellow_cards": 0,
                "red_cards": 0,
            }

    for side in ("home", "away"):
        for g in goals.get(side) or []:
            ext_id = g.get("player_external_id")
            if not ext_id or ext_id not in roster:
                continue
            if g.get("type") == OWN_GOAL_TYPE:
                roster[ext_id]["own_goals"] += 1
            else:
                roster[ext_id]["goals"] += 1

    for side in ("home", "away"):
        for c in cards.get(side) or []:
            ext_id = c.get("player_external_id")
            if not ext_id or ext_id not in roster:
                continue
            if c.get("type") == "Sarı Kart":
                roster[ext_id]["yellow_cards"] += 1
            elif c.get("type") in ("Kırmızı Kart", "Çift Sarı Kart"):
                roster[ext_id]["red_cards"] += 1

    rows = []
    for ext_id, rec in roster.items():
        tm = tm_by_tff_id.get(ext_id)
        position_group = tm["position_group"] if tm else position_by_canon.get(canonical_player_name(rec["name"]), "MID")

        points = rec["points"]
        points += rec["goals"] * GOAL_POINTS.get(position_group, DEFAULT_GOAL_POINTS)
        points += rec["own_goals"] * OWN_GOAL_POINTS
        points += rec["yellow_cards"] * YELLOW_CARD_POINTS
        points += rec["red_cards"] * RED_CARD_POINTS
        clean_sheet = bool(rec["started"] and rec["conceded"] == 0 and position_group in ("GK", "DEF"))
        if clean_sheet:
            points += CLEAN_SHEET_POINTS

        rows.append(
            {
                "transfermarkt_id": tm["transfermarkt_id"] if tm else None,
                "tff_external_id": ext_id,
                "name": rec["name"],
                "team": rec["team"],
                "position_group": position_group,
                "started": rec["started"],
                "goals": rec["goals"],
                "own_goals": rec["own_goals"],
                "yellow_cards": rec["yellow_cards"],
                "red_cards": rec["red_cards"],
                "clean_sheet": clean_sheet,
                "points": points,
            }
        )
    return rows


def _build_report(payload: dict) -> str:
    lines = [
        "# Kadro Kur — Haftalık Puanlar",
        "",
        f"- Puanlanan hafta sayısı: {payload['weeks_scored']}",
        f"- Toplamda puan alan oyuncu: {len(payload['player_totals'])}",
    ]
    top5 = payload["player_totals"][:5]
    if top5:
        lines.append("- En yüksek puanlı 5 oyuncu:")
        for p in top5:
            lines.append(f"  - {p['name']} ({p['team']}): {p['total_points']} puan")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
