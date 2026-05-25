from __future__ import annotations


def summarize_opponent_vs_besiktas_history(matches: list[dict], target_team: str, opponent: str) -> dict:
    history = []
    for match in matches:
        teams = {match["home_team"]["name"], match["away_team"]["name"]}
        if target_team not in teams or opponent not in teams:
            continue
        side = "home" if match["home_team"]["name"] == target_team else "away"
        opp_side = "away" if side == "home" else "home"
        history.append(
            {
                "match_id": match["external_id"],
                "date": match["match_date"],
                "score_for": match[f"{side}_team"]["score"] or 0,
                "score_against": match[f"{opp_side}_team"]["score"] or 0,
                "cards_for": len(match["cards"][side]),
                "cards_against": len(match["cards"][opp_side]),
            }
        )
    if not history:
        return {"matches": 0, "note": "Bu sezon onceki eslesme yok."}

    return {
        "matches": len(history),
        "goals_for_per_match": round(sum(item["score_for"] for item in history) / len(history), 2),
        "goals_against_per_match": round(sum(item["score_against"] for item in history) / len(history), 2),
        "cards_for_per_match": round(sum(item["cards_for"] for item in history) / len(history), 2),
        "history": history,
    }


def summarize_opponent_defense(matches: list[dict], opponent: str, last_n: int = 8) -> dict:
    opponent_matches = [
        match
        for match in matches
        if match["home_team"]["name"] == opponent or match["away_team"]["name"] == opponent
    ]
    recent = opponent_matches[-last_n:]
    if not recent:
        return {
            "available": False,
            "last_n": 0,
            "goals_against_per_match": None,
            "clean_sheet_rate": None,
            "conceded_2_plus_rate": None,
            "goal_candidate_multiplier": 1.0,
            "note": "Rakip savunma formu icin yeterli veri yok.",
        }

    goals_against = 0
    clean_sheets = 0
    conceded_2_plus = 0
    for match in recent:
        side = "home" if match["home_team"]["name"] == opponent else "away"
        opp_side = "away" if side == "home" else "home"
        ga = match[f"{opp_side}_team"]["score"] or 0
        goals_against += ga
        clean_sheets += int(ga == 0)
        conceded_2_plus += int(ga >= 2)

    ga_per_match = goals_against / len(recent)
    clean_sheet_rate = clean_sheets / len(recent)
    conceded_2_plus_rate = conceded_2_plus / len(recent)
    multiplier = 1.0
    if ga_per_match >= 1.6:
        multiplier += 0.14
    elif ga_per_match <= 0.8:
        multiplier -= 0.1
    if conceded_2_plus_rate >= 0.38:
        multiplier += 0.08
    if clean_sheet_rate >= 0.38:
        multiplier -= 0.07

    return {
        "available": True,
        "last_n": len(recent),
        "goals_against_per_match": round(ga_per_match, 2),
        "clean_sheet_rate": round(clean_sheet_rate, 3),
        "conceded_2_plus_rate": round(conceded_2_plus_rate, 3),
        "goal_candidate_multiplier": round(max(0.82, min(1.22, multiplier)), 2),
    }
