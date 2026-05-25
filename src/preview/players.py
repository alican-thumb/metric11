from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from src.preview.constants import BIG_MATCH_OPPONENTS


def load_availability(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def availability_for_match(
    availability: dict | None,
    match_id: str,
    player_importance: dict | None = None,
) -> dict:
    if not availability:
        return {"available": False, "unavailable": [], "note": "Availability verisi yok."}
    match = next((item for item in availability.get("matches", []) if item["match_id"] == match_id), None)
    if not match:
        return {"available": True, "unavailable": [], "note": "Bu maç için eksik sinyali yok."}
    unavailable = []
    for item in match.get("unavailable", []):
        impact = _player_impact(item.get("player_external_id"), player_importance)
        unavailable.append({**item, "impact": impact})
    return {
        "available": True,
        "unavailable": unavailable,
        "suspended_count": len(match.get("suspended", [])),
        "injured_count": len(match.get("injured", [])),
    }


def _player_impact(player_id: str | None, player_importance: dict | None) -> str:
    if not player_id or not player_importance:
        return "UNKNOWN"
    imp = player_importance.get(player_id)
    if imp is None:
        return "UNKNOWN"
    if imp["is_key"]:
        return "REGULAR"
    if imp["is_rotation"]:
        return "ROTATION"
    return "FRINGE"


def summarize_players(matches: list[dict], target_team: str, is_big_match: bool, unavailable_ids: set[str] | None = None) -> dict:
    unavailable_ids = unavailable_ids or set()
    starts = Counter()
    bench = Counter()
    cards = Counter()
    big_match_cards = Counter()
    player_names = {}

    team_matches = [
        match
        for match in matches
        if match["home_team"]["name"] == target_team or match["away_team"]["name"] == target_team
    ]
    recent_matches = team_matches[-8:]
    for match in recent_matches:
        side = "home" if match["home_team"]["name"] == target_team else "away"
        opp_side = "away" if side == "home" else "home"
        opponent = match[f"{opp_side}_team"]["name"]
        match_is_big = opponent in BIG_MATCH_OPPONENTS
        carded_ids = Counter(card["player_external_id"] for card in match["cards"][side] if card.get("player_external_id"))

        for lineup_type, counter in (("starting", starts), ("bench", bench)):
            for player in match["lineups"][side][lineup_type]:
                key = player["external_id"] or player["name"]
                player_names[key] = player["name"]
                counter[key] += 1

        for player_id, count in carded_ids.items():
            cards[player_id] += count
            if match_is_big:
                big_match_cards[player_id] += count

    min_start_count = 4 if len(recent_matches) >= 5 else max(1, len(recent_matches) - 1)
    likely_starters = [
        {"player_id": pid, "name": player_names[pid], "recent_starts": count, "recent_bench": bench[pid]}
        for pid, count in starts.most_common()
        if count >= min_start_count and pid not in unavailable_ids
    ][:12]

    card_risks = []
    for pid, count in cards.most_common():
        start_count = starts[pid]
        if start_count == 0:
            continue
        card_risks.append(
            {
                "player_id": pid,
                "name": player_names.get(pid, pid),
                "recent_cards": count,
                "recent_starts": start_count,
                "cards_per_recent_start": round(count / start_count, 2),
                "big_match_cards": big_match_cards[pid],
            }
        )

    card_risks.sort(key=lambda item: (item["cards_per_recent_start"], item["recent_cards"]), reverse=True)
    return {
        "window_matches": len(recent_matches),
        "likely_starters": likely_starters,
        "card_risk_players": card_risks[:8],
        "big_match_context_applied": is_big_match,
    }


def summarize_referee(matches: list[dict], target_team: str, referee_name: str | None) -> dict:
    if not referee_name:
        return {"available": False, "note": "Hakem bilgisi yok."}

    ref_matches = []
    for match in matches:
        main_referee = next((official for official in match["officials"] if official["role"] == "Hakem"), None)
        if not main_referee or main_referee["name"] != referee_name:
            continue
        side = "home" if match["home_team"]["name"] == target_team else "away"
        opp_side = "away" if side == "home" else "home"
        ref_matches.append(
            {
                "match_id": match["external_id"],
                "total_cards": len(match["cards"][side]) + len(match["cards"][opp_side]),
                "target_cards": len(match["cards"][side]),
            }
        )

    if not ref_matches:
        return {
            "available": True,
            "referee": referee_name,
            "prior_matches": 0,
            "note": "Bu sezon secili mactan once Besiktas icin bu hakemle veri yok.",
        }

    return {
        "available": True,
        "referee": referee_name,
        "prior_matches": len(ref_matches),
        "cards_per_match": round(sum(item["total_cards"] for item in ref_matches) / len(ref_matches), 2),
        "target_cards_per_match": round(sum(item["target_cards"] for item in ref_matches) / len(ref_matches), 2),
    }
