"""Oyuncu önem skoru: tarihsel ilk 11 verisiyle her oyuncunun takım performansına etkisini hesaplar."""
from __future__ import annotations

from collections import defaultdict
from typing import TypedDict


class PlayerImportance(TypedDict):
    player_id: str
    name: str
    starts: int
    total_matches: int
    start_rate: float
    team_gf_when_starts: float
    team_gf_when_absent: float
    goal_lift: float        # team_gf_when_starts - team_gf_when_absent
    xg_penalty: float       # expected goals reduction when player is absent
    is_key: bool            # start_rate >= KEY_START_RATE
    is_rotation: bool       # start_rate >= ROTATION_START_RATE (but < KEY)


KEY_START_RATE = 0.55       # ≥55% startta → key oyuncu
ROTATION_START_RATE = 0.25  # ≥25% startta → rotasyon oyuncusu
N_WINDOW = 30               # tüm sezon boyunca veya bu kadar maç — önem skoru stabil özelliktir
MIN_ABSENCE_FOR_LIFT = 2    # lift sinyaline güvenmek için minimum eksik maç sayısı
FLAT_KEY_PENALTY = 0.05     # eksik veri durumunda key non-GK oyuncunun flat cezası


def build_player_importance(
    matches: list[dict],
    team: str,
    n_window: int = N_WINDOW,
    gk_ids: set[str] | None = None,
) -> dict[str, PlayerImportance]:
    """
    Son n_window maçtan her oyuncunun önem skorunu hesaplar.
    gk_ids: bilinen kaleci external_id'leri — bunlara xg_for cezası uygulanmaz.
    """
    """Son n_window maçtan her oyuncunun önem skorunu hesaplar."""
    team_matches = [
        m for m in matches
        if m["home_team"]["name"] == team or m["away_team"]["name"] == team
    ]
    # Only use completed matches with lineup data
    team_matches = [
        m for m in team_matches
        if m.get("lineups") and _score(m, team) is not None
    ]
    recent = team_matches[-n_window:]

    player_names: dict[str, str] = {}
    player_shirt: dict[str, int | None] = {}      # to detect GK via shirt_number=1
    player_matches_started: dict[str, list[int]] = defaultdict(list)  # gf when starting
    player_matches_absent: dict[str, list[int]] = defaultdict(list)   # gf when NOT starting

    all_pids_ever: set[str] = set()

    for m in recent:
        side = "home" if m["home_team"]["name"] == team else "away"
        gf = _score(m, team)
        if gf is None:
            continue
        starters = {
            p["external_id"] or p["name"]
            for p in m["lineups"][side]["starting"]
        }
        for p in m["lineups"][side]["starting"]:
            pid = p["external_id"] or p["name"]
            player_names[pid] = p["name"]
            player_shirt[pid] = p.get("shirt_number")
            all_pids_ever.add(pid)
        for p in m["lineups"][side].get("bench", []):
            pid = p["external_id"] or p["name"]
            player_names[pid] = p["name"]
            player_shirt.setdefault(pid, p.get("shirt_number"))
            all_pids_ever.add(pid)

        for pid in starters:
            player_matches_started[pid].append(gf)
        for pid in all_pids_ever - starters:
            # Only count absence for players who appeared at least once
            if pid in player_matches_started or pid in player_matches_absent:
                player_matches_absent[pid].append(gf)

    result: dict[str, PlayerImportance] = {}
    total_matches = len(recent)
    for pid in all_pids_ever:
        started = player_matches_started.get(pid, [])
        absent = player_matches_absent.get(pid, [])
        if not started:
            continue
        start_rate = len(started) / total_matches if total_matches else 0
        gf_starts = _mean(started)
        gf_absent = _mean(absent) if absent else gf_starts  # no absence data → assume same
        goal_lift = gf_starts - gf_absent
        is_key = start_rate >= KEY_START_RATE
        is_rotation = (not is_key) and start_rate >= ROTATION_START_RATE
        # Goalkeeper absence affects defense not attack → no xg_for penalty
        is_gk = (gk_ids and pid in gk_ids) or player_shirt.get(pid) == 1
        absence_reliable = len(absent) >= MIN_ABSENCE_FOR_LIFT
        if is_gk:
            xg_penalty = 0.0
        elif absence_reliable and goal_lift > 0.1:
            # Lift signal reliable enough; cap conservatively
            xg_penalty = min(0.12, goal_lift * 0.55)
        elif is_key:
            # Insufficient absence data but clearly a key player → flat minimum
            xg_penalty = FLAT_KEY_PENALTY
        else:
            xg_penalty = 0.0
        result[pid] = PlayerImportance(
            player_id=pid,
            name=player_names.get(pid, pid),
            starts=len(started),
            total_matches=total_matches,
            start_rate=round(start_rate, 3),
            team_gf_when_starts=round(gf_starts, 3),
            team_gf_when_absent=round(gf_absent, 3),
            goal_lift=round(goal_lift, 3),
            xg_penalty=round(xg_penalty, 3),
            is_key=is_key,
            is_rotation=is_rotation,
        )
    return result


def squad_xg_adjustment(
    player_importance: dict[str, PlayerImportance],
    unavailable_ids: set[str],
) -> tuple[float, list[dict]]:
    """
    Returns (total_penalty, breakdown_list).
    total_penalty is negative (reduces expected goals).
    """
    breakdown = []
    total = 0.0
    for pid in unavailable_ids:
        imp = player_importance.get(pid)
        if imp is None or not imp["is_key"]:
            continue
        penalty = imp["xg_penalty"]
        total += penalty
        breakdown.append({
            "player_id": pid,
            "name": imp["name"],
            "xg_penalty": penalty,
            "start_rate": imp["start_rate"],
        })
    # Hard cap: total missing can't drop expected goals by more than 0.35
    total = min(0.35, total)
    return round(-total, 3), breakdown


def _score(match: dict, team: str) -> int | None:
    side = "home" if match["home_team"]["name"] == team else "away"
    score = match[f"{side}_team"]["score"]
    return score if score is not None else None


def _mean(vals: list[int]) -> float:
    return sum(vals) / len(vals) if vals else 0.0
