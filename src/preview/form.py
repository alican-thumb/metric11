from __future__ import annotations

from collections import Counter
from datetime import datetime

from src.preview.constants import BIG_MATCH_OPPONENTS


def parse_tff_datetime(value: str) -> datetime:
    normalized = value.replace(" - ", " ").strip()
    return datetime.strptime(normalized, "%d.%m.%Y %H:%M")


def summarize_team_form(matches: list[dict], target_team: str, last_n: int = 5) -> dict:
    team_matches = [
        match
        for match in matches
        if match["home_team"]["name"] == target_team or match["away_team"]["name"] == target_team
    ]
    recent = team_matches[-last_n:]
    totals = Counter()
    results = []
    for match in recent:
        side = "home" if match["home_team"]["name"] == target_team else "away"
        opp_side = "away" if side == "home" else "home"
        gf = match[f"{side}_team"]["score"] or 0
        ga = match[f"{opp_side}_team"]["score"] or 0
        cards = len(match["cards"][side])
        opponent_cards = len(match["cards"][opp_side])
        totals["goals_for"] += gf
        totals["goals_against"] += ga
        totals["cards"] += cards
        totals["opponent_cards"] += opponent_cards
        totals["wins"] += int(gf > ga)
        totals["draws"] += int(gf == ga)
        totals["losses"] += int(gf < ga)
        ss = match.get("sofascore_stats") or {}
        sot_key = f"shots_on_target_{side}"
        xg_key = f"xg_{side}"
        xga_key = f"xg_{opp_side}"
        if ss.get(sot_key) is not None:
            totals["sot_for"] += ss[sot_key]
            totals["sot_matches"] += 1
        if ss.get(xg_key) is not None:
            totals["xg_for"] += ss[xg_key]
            totals["xg_matches"] += 1
        if ss.get(xga_key) is not None:
            totals["xg_against"] += ss[xga_key]
        results.append(
            {
                "match_id": match["external_id"],
                "date": match["match_date"],
                "opponent": match[f"{opp_side}_team"]["name"],
                "score": f"{gf}-{ga}",
                "cards": cards,
                "xg_for": ss.get(xg_key),
                "xg_against": ss.get(xga_key),
                "shots_on_target": ss.get(sot_key),
            }
        )
    count = len(recent)
    if count == 0:
        return {
            "last_n": 0,
            "total_prior_team_matches": 0,
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "goals_for_per_match": 0,
            "goals_against_per_match": 0,
            "cards_per_match": 0,
            "xg_for_per_match": None,
            "xg_against_per_match": None,
            "sot_per_match": None,
            "results": [],
        }
    xg_matches = totals["xg_matches"]
    sot_matches = totals["sot_matches"]
    return {
        "last_n": count,
        "total_prior_team_matches": len(team_matches),
        "wins": totals["wins"],
        "draws": totals["draws"],
        "losses": totals["losses"],
        "goals_for_per_match": round(totals["goals_for"] / count, 2),
        "goals_against_per_match": round(totals["goals_against"] / count, 2),
        "cards_per_match": round(totals["cards"] / count, 2),
        "xg_for_per_match": round(totals["xg_for"] / xg_matches, 3) if xg_matches else None,
        "xg_against_per_match": round(totals["xg_against"] / xg_matches, 3) if xg_matches else None,
        "sot_per_match": round(totals["sot_for"] / sot_matches, 2) if sot_matches else None,
        "xg_data_matches": xg_matches,
        "results": results,
    }


def clamp_score(value: float, minimum: float = 20.0, maximum: float = 86.0) -> float:
    return max(minimum, min(maximum, value))


def summarize_team_strength(matches: list[dict], target_team: str, target_side: str, last_n: int = 8) -> dict:
    team_matches = [
        match
        for match in matches
        if match["home_team"]["name"] == target_team or match["away_team"]["name"] == target_team
    ]
    if not team_matches:
        return {
            "available": False,
            "matches": 0,
            "strength_score": 50.0,
            "attack_score": 50.0,
            "defense_score": 50.0,
            "continuity_score": 50.0,
            "note": "Takım gücü için önceki maç verisi yok.",
        }

    totals = Counter()
    recent_points = []
    venue_points = []
    starters = Counter()
    player_names = {}
    recent = team_matches[-last_n:]
    for match in team_matches:
        side = "home" if match["home_team"]["name"] == target_team else "away"
        opp_side = "away" if side == "home" else "home"
        gf = match[f"{side}_team"]["score"] or 0
        ga = match[f"{opp_side}_team"]["score"] or 0
        points = 3 if gf > ga else 1 if gf == ga else 0
        totals["matches"] += 1
        totals["points"] += points
        totals["goals_for"] += gf
        totals["goals_against"] += ga
        totals["clean_sheets"] += int(ga == 0)
        totals["failed_to_score"] += int(gf == 0)
        if match in recent:
            recent_points.append(points)
            for player in match["lineups"][side]["starting"]:
                key = player.get("external_id") or player.get("name")
                if key:
                    starters[key] += 1
                    player_names[key] = player.get("name")
        if side == target_side:
            venue_points.append(points)

    match_count = totals["matches"]
    ppg = totals["points"] / match_count
    gf_pm = totals["goals_for"] / match_count
    ga_pm = totals["goals_against"] / match_count
    gd_pm = gf_pm - ga_pm
    recent_ppg = sum(recent_points) / len(recent_points) if recent_points else ppg
    venue_ppg = sum(venue_points) / len(venue_points) if venue_points else ppg
    core_players = [item for item in starters.most_common(11) if item[1] >= max(2, len(recent) * 0.45)]
    continuity = len(core_players) / 11 if core_players else 0.45

    attack_score = clamp_score(50 + (gf_pm - 1.25) * 18 + max(0, recent_ppg - 1.35) * 5)
    defense_score = clamp_score(50 + (1.25 - ga_pm) * 18 + totals["clean_sheets"] / match_count * 10)
    form_score = clamp_score(50 + (recent_ppg - 1.35) * 16)
    venue_score = clamp_score(50 + (venue_ppg - 1.35) * 10)
    continuity_score = clamp_score(35 + continuity * 65)
    strength_score = clamp_score(
        attack_score * 0.26 + defense_score * 0.24 + form_score * 0.24 + venue_score * 0.12 + continuity_score * 0.14
    )

    return {
        "available": True,
        "matches": match_count,
        "recent_window": len(recent),
        "points_per_match": round(ppg, 2),
        "recent_points_per_match": round(recent_ppg, 2),
        "venue_points_per_match": round(venue_ppg, 2),
        "goals_for_per_match": round(gf_pm, 2),
        "goals_against_per_match": round(ga_pm, 2),
        "goal_difference_per_match": round(gd_pm, 2),
        "clean_sheet_rate": round(totals["clean_sheets"] / match_count, 3),
        "failed_to_score_rate": round(totals["failed_to_score"] / match_count, 3),
        "core_player_count": len(core_players),
        "core_players": [{"player_id": pid, "name": player_names.get(pid, pid), "recent_starts": count} for pid, count in core_players[:11]],
        "attack_score": round(attack_score, 1),
        "defense_score": round(defense_score, 1),
        "form_score": round(form_score, 1),
        "venue_score": round(venue_score, 1),
        "continuity_score": round(continuity_score, 1),
        "strength_score": round(strength_score, 1),
        "note": "Puan, gol farkı, son form, iç/dış saha ve kadro sürekliliğinden türetilmiş takım gücü sinyalidir.",
    }
