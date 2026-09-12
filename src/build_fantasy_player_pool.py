"""Kadro Kur (Fantasy Manager) oyunu için oyuncu havuzu.

Transfermarkt 2026-27 kadrolarındaki (`transfermarkt_super_lig_squads_2026_2027.json`)
pozisyon (GK/DEF/MID/FWD) ve piyasa değerini, TFF'nin gerçek 2026-27 maç verisindeki
(`tff_super_lig_matches_2026_2027.json`) ilk 11/gol/kart olaylarıyla birleştirir.

Kimlik stratejisi: her oyuncunun KALICI kimliği `transfermarkt_id`'dir (kadro seçim
ekranında ve veritabanında bu kullanılır) — TFF eşleşmesi sezon ilerledikçe iyileşebilir/
değişebilir, oyuncunun uygulamadaki kimliğini etkilememesi için ayrı tutulur. Eşleşme
`canonical_player_name` (normalize + `data/manual/player_aliases.json`) ile yapılır;
takım adı sadece aynı isimli birden fazla adayda çakışma çözücü olarak kullanılır.

Fiyat: piyasa değerinin karekök ölçeklemesiyle 4.0-15.0 (fantezi bütçe birimi) aralığına
sıkıştırılır. KRİTİK (2026-09-12 kullanıcı bulgusu): ölçekleme ligin TEK EN YÜKSEK
piyasa değerine (bu sezon Osimhen ~€75M — yaz penceresindeki gerçek ama uç bir transfer
ücreti) göre normalize edilirse, geri kalan 528 oyuncunun neredeyse tamamı bu tek uç
değere oranlandığı için 4.0-5.5 bandına sıkışıyordu (529 oyuncunun %69'u yalnızca 4
fiyat noktasında toplanıyordu — ölçüm: median değer €1.2M, 97. persentil €20M, max
€75M). Bunun yerine 97. persentili "tavan" alıp onun ÜZERİNDEKİLERİ tavana kırpıyoruz
(clamp) — tek bir aşırı transfer artık tüm ölçeği ezmiyor, ~50 benzersiz fiyat noktasına
yayılıyor. En ucuz yasal kadro (60.0) ile en pahalı yasal kadro (~194.0) arasında 100.0
bütçe gerçekçi bir gerilim yaratıyor — tam yıldız kadrosu imkansız (gerçek FPL'de de
öyle), ama 1-2 yıldız + değerli oyunculardan oluşan bir kadro rahatça kurulabiliyor.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path

from src.config import PROCESSED_DIR
from src.normalization import canonical_player_name, normalize_team_name

TM_SQUADS_PATH = PROCESSED_DIR / "transfermarkt_super_lig_squads_2026_2027.json"
TFF_MATCHES_PATH = PROCESSED_DIR / "tff_super_lig_matches_2026_2027.json"
OUTPUT_JSON = PROCESSED_DIR / "fantasy_player_pool_2026_2027.json"
OUTPUT_MD = PROCESSED_DIR / "fantasy_player_pool_2026_2027.md"

MIN_PRICE = 4.0
MAX_PRICE = 15.0
PRICE_CAP_PERCENTILE = 0.97
OWN_GOAL_TYPE = "K"


def main() -> None:
    tm_payload = json.loads(TM_SQUADS_PATH.read_text(encoding="utf-8"))
    tff_matches = json.loads(TFF_MATCHES_PATH.read_text(encoding="utf-8")) if TFF_MATCHES_PATH.exists() else []

    tff_index = _build_tff_player_index(tff_matches)
    players = _build_player_pool(tm_payload, tff_index)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "season": "2026-2027",
        "player_count": len(players),
        "matched_with_tff_count": sum(1 for p in players if p["tff_external_id"]),
        "budget_default": 100.0,
        "squad_rules": {
            "squad_size": 15,
            "positions": {"GK": 2, "DEF": 5, "MID": 5, "FWD": 3},
            "max_players_per_team": 3,
            "starting_xi": {
                "GK": [1, 1],
                "DEF": [3, 5],
                "MID": [2, 5],
                "FWD": [1, 3],
            },
        },
        "players": players,
    }

    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    OUTPUT_MD.write_text(_build_report(payload), encoding="utf-8")
    print(_build_report(payload))


def _build_tff_player_index(matches: list[dict]) -> dict[str, dict]:
    """canonical_name -> {external_id, team_name, starts, bench, goals, own_goals,
    yellow_cards, red_cards, appearances (match_ids)} — tüm maçlar taranarak birikimli."""
    index: dict[str, dict] = {}

    def entry(name: str, external_id: str | None, team_name: str | None) -> dict:
        canon = canonical_player_name(name)
        if canon not in index:
            index[canon] = {
                "name": name,
                "external_id": external_id,
                "team_name": team_name,
                "starts": 0,
                "bench": 0,
                "goals": 0,
                "own_goals": 0,
                "yellow_cards": 0,
                "red_cards": 0,
                "matches_played": set(),
            }
        rec = index[canon]
        # En son görülen takım/external_id ile güncel tut (transfer olmuşsa güncel takımı yansıtır).
        if external_id:
            rec["external_id"] = external_id
        if team_name:
            rec["team_name"] = team_name
        return rec

    for match in matches:
        lineups = match.get("lineups") or {}
        for side in ("home", "away"):
            side_team = ((match.get(f"{side}_team") or {}).get("name"))
            side_lineup = lineups.get(side) or {}
            for p in side_lineup.get("starting") or []:
                rec = entry(p.get("name"), p.get("external_id"), side_team)
                rec["starts"] += 1
                rec["matches_played"].add(match.get("external_id"))
            for p in side_lineup.get("bench") or []:
                rec = entry(p.get("name"), p.get("external_id"), side_team)
                rec["bench"] += 1

        for side in ("home", "away"):
            for g in (match.get("goals") or {}).get(side) or []:
                if not g.get("player_name"):
                    continue
                rec = entry(g["player_name"], g.get("player_external_id"), None)
                if g.get("type") == OWN_GOAL_TYPE:
                    rec["own_goals"] += 1
                else:
                    rec["goals"] += 1

        for side in ("home", "away"):
            for c in (match.get("cards") or {}).get(side) or []:
                if not c.get("player_name"):
                    continue
                rec = entry(c["player_name"], c.get("player_external_id"), None)
                if c.get("type") == "Sarı Kart":
                    rec["yellow_cards"] += 1
                elif c.get("type") in ("Kırmızı Kart", "Çift Sarı Kart"):
                    rec["red_cards"] += 1

    for rec in index.values():
        rec["matches_played"] = len(rec["matches_played"])
    return index


def _build_player_pool(tm_payload: dict, tff_index: dict[str, dict]) -> list[dict]:
    values = sorted(
        p["market_value_eur"]
        for club in tm_payload["clubs"]
        for p in club["players"]
        if p.get("market_value_eur")
    )
    # Tavan = 97. persentil, tek en yüksek değer DEĞİL — bkz. modül docstring'i:
    # o sezonun tek bir uç transferi (ör. Osimhen) tüm ölçeği ezmesin diye.
    price_cap = values[min(int(len(values) * PRICE_CAP_PERCENTILE), len(values) - 1)] if values else 1

    players = []
    for club in tm_payload["clubs"]:
        team_name = normalize_team_name(club["team_name"])
        for p in club["players"]:
            canon = canonical_player_name(p.get("name"))
            tff = tff_index.get(canon)
            # İsim eşleşmesi başka bir takımdaysa (aynı isim iki farklı takımda — nadir),
            # takım adı da örtüşmüyorsa güvenme.
            if tff and tff.get("team_name") and normalize_team_name(tff["team_name"]) != team_name:
                tff = None

            market_value = p.get("market_value_eur") or 0
            price = _price_from_value(market_value, price_cap)

            players.append(
                {
                    "transfermarkt_id": p.get("transfermarkt_id"),
                    "name": p.get("name"),
                    "team": team_name,
                    "shirt_number": p.get("shirt_number"),
                    "position": p.get("position"),
                    "position_group": p.get("position_group") or "MID",
                    "age": p.get("age"),
                    "market_value_eur": market_value,
                    "price": price,
                    "tff_external_id": tff["external_id"] if tff else None,
                    "season_stats": {
                        "starts": tff["starts"] if tff else 0,
                        "bench": tff["bench"] if tff else 0,
                        "goals": tff["goals"] if tff else 0,
                        "own_goals": tff["own_goals"] if tff else 0,
                        "yellow_cards": tff["yellow_cards"] if tff else 0,
                        "red_cards": tff["red_cards"] if tff else 0,
                        "matches_played": tff["matches_played"] if tff else 0,
                    },
                }
            )
    return players


def _price_from_value(market_value_eur: int, price_cap: int) -> float:
    if market_value_eur <= 0 or price_cap <= 0:
        raw = MIN_PRICE
    else:
        # Tavanın üzerindeki (o sezonun uç transferleri) değerler MAX_PRICE'a kırpılır —
        # tek bir oyuncu ölçeği geri kalanının aleyhine ezmesin.
        norm = min(market_value_eur / price_cap, 1.0)
        raw = MIN_PRICE + (MAX_PRICE - MIN_PRICE) * math.sqrt(norm)
    return round(raw * 10) / 10  # en yakın 0.1'e yuvarla (gerçek FPL'deki gibi ince ayar)


def _build_report(payload: dict) -> str:
    by_pos: dict[str, int] = {}
    for p in payload["players"]:
        by_pos[p["position_group"]] = by_pos.get(p["position_group"], 0) + 1
    lines = [
        "# Kadro Kur — Oyuncu Havuzu",
        "",
        f"- Toplam oyuncu: {payload['player_count']}",
        f"- TFF (gerçek maç verisi) ile eşleşen: {payload['matched_with_tff_count']}",
        f"- Pozisyon dağılımı: {by_pos}",
        f"- Varsayılan bütçe: {payload['budget_default']}",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
