"""Transfermarkt kadro snapshot karşılaştırması ile transfer dedektörü.

Her çalışmada mevcut kadro verisini arşivler ve önceki snapshot ile karşılaştırır.
Takımlar arası oyuncu geçişlerini (varış/ayrılış) otomatik tespit eder.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from src.config import PROCESSED_DIR, RAW_DIR, SEASON

SQUAD_FILE = PROCESSED_DIR / f"transfermarkt_super_lig_squads_{SEASON}.json"
SNAPSHOT_DIR = RAW_DIR / "transfermarkt" / "squad_snapshots"
OUTPUT_JSON = PROCESSED_DIR / f"tm_squad_changes_{SEASON}.json"


def _mv(eur: int | None) -> str:
    if not eur:
        return "—"
    if eur >= 1_000_000:
        return f"€{eur / 1_000_000:.1f}M"
    return f"€{eur // 1000}K"


def _load_squads(path: Path) -> dict[str, dict]:
    """Club name → {player_id → player_dict}."""
    data = json.loads(path.read_text(encoding="utf-8"))
    result: dict[str, dict] = {}
    for club in data.get("clubs", []):
        team = club.get("team_name", "?")
        result[team] = {
            p["transfermarkt_id"]: p
            for p in club.get("players", [])
            if p.get("transfermarkt_id")
        }
    return result


def _save_snapshot(current_data: dict) -> Path:
    """Bugünün snapshot'ını arşivle; aynı gün varsa üzerine yaz."""
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    snap_path = SNAPSHOT_DIR / f"{today}.json"
    snap_path.write_text(json.dumps(current_data, ensure_ascii=False), encoding="utf-8")
    return snap_path


def _latest_previous_snapshot(today_str: str) -> Path | None:
    snaps = sorted(SNAPSHOT_DIR.glob("*.json"))
    for s in reversed(snaps):
        if s.stem < today_str:
            return s
    return None


def _compare(prev: dict[str, dict], curr: dict[str, dict]) -> tuple[list, list]:
    """(arrivals, departures) listesi döndür."""
    # Tüm oyuncu ID → takım eşlemesi
    prev_all: dict[str, str] = {pid: team for team, players in prev.items() for pid in players}
    curr_all: dict[str, str] = {pid: team for team, players in curr.items() for pid in players}

    arrivals = []
    departures = []

    prev_ids = set(prev_all)
    curr_ids = set(curr_all)

    # Yeni gelen: şu an var, önceden yoktu
    for pid in curr_ids - prev_ids:
        team = curr_all[pid]
        player = curr.get(team, {}).get(pid, {})
        arrivals.append({
            "transfermarkt_id": pid,
            "player_name": player.get("name", "?"),
            "to_team": team,
            "from_team": None,
            "market_value_eur": player.get("market_value_eur"),
            "market_value_text": _mv(player.get("market_value_eur")),
            "contract_until": player.get("contract_until"),
            "position_group": player.get("position_group"),
            "profile_url": player.get("profile_url"),
            "signal_type": "tm_squad_new_player",
            "confidence": "MEDIUM",
        })

    # Ayrılan: önceden vardı, şimdi yok
    for pid in prev_ids - curr_ids:
        old_team = prev_all[pid]
        player = prev.get(old_team, {}).get(pid, {})
        departures.append({
            "transfermarkt_id": pid,
            "player_name": player.get("name", "?"),
            "from_team": old_team,
            "to_team": None,
            "market_value_eur": player.get("market_value_eur"),
            "market_value_text": _mv(player.get("market_value_eur")),
            "signal_type": "tm_squad_removed",
            "confidence": "MEDIUM",
        })

    # Takım değiştiren: hem eski hem yeni listelerde var ama farklı takımda
    for pid in prev_ids & curr_ids:
        if prev_all[pid] != curr_all[pid]:
            old_team = prev_all[pid]
            new_team = curr_all[pid]
            player = curr.get(new_team, {}).get(pid, {})
            arrivals.append({
                "transfermarkt_id": pid,
                "player_name": player.get("name", "?"),
                "to_team": new_team,
                "from_team": old_team,
                "market_value_eur": player.get("market_value_eur"),
                "market_value_text": _mv(player.get("market_value_eur")),
                "contract_until": player.get("contract_until"),
                "position_group": player.get("position_group"),
                "profile_url": player.get("profile_url"),
                "signal_type": "tm_squad_transfer",
                "confidence": "HIGH",
            })

    # Değere göre sırala
    arrivals.sort(key=lambda x: -(x.get("market_value_eur") or 0))
    departures.sort(key=lambda x: -(x.get("market_value_eur") or 0))
    return arrivals, departures


def main() -> None:
    if not SQUAD_FILE.exists():
        print(f"Kadro dosyası bulunamadı: {SQUAD_FILE}")
        return

    current_data = json.loads(SQUAD_FILE.read_text(encoding="utf-8"))
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    snap_path = _save_snapshot(current_data)
    prev_snap = _latest_previous_snapshot(today_str)

    if prev_snap is None:
        print(f"İlk snapshot kaydedildi: {snap_path.name} — karşılaştırmak için bir sonraki çalışmayı bekle.")
        payload = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "season": SEASON,
            "status": "baseline_only",
            "snapshots_compared": [today_str, None],
            "arrivals": [],
            "departures": [],
            "summary": {"arrivals": 0, "departures": 0, "transfers": 0},
        }
        OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return

    prev_data = json.loads(prev_snap.read_text(encoding="utf-8"))
    prev_squads = _load_squads(Path(prev_snap))
    curr_squads = _load_squads(SQUAD_FILE)

    arrivals, departures = _compare(prev_squads, curr_squads)
    transfers = [a for a in arrivals if a.get("from_team")]

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "season": SEASON,
        "status": "compared",
        "snapshots_compared": [prev_snap.stem, today_str],
        "arrivals": arrivals,
        "departures": departures,
        "summary": {
            "arrivals": len(arrivals),
            "departures": len(departures),
            "transfers": len(transfers),
            "high_value_moves": len([a for a in arrivals if (a.get("market_value_eur") or 0) >= 5_000_000]),
        },
    }
    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(
        f"✓ Karşılaştırma: {prev_snap.stem} → {today_str} | "
        f"{len(arrivals)} varış · {len(departures)} ayrılış · {len(transfers)} takım değişimi"
    )


if __name__ == "__main__":
    main()
