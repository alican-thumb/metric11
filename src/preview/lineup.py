from __future__ import annotations

from src.preview.probability import scoreline_probabilities


def build_lineup_recommendation(player_signals: dict, goal_candidates: dict, availability_signal: dict, probability: dict) -> dict:
    likely = player_signals.get("likely_starters", [])
    card_risks = player_signals.get("card_risk_players", [])
    scorers = goal_candidates.get("candidates", [])
    unavailable_names = {
        item.get("player_name")
        for item in availability_signal.get("unavailable", [])
        if item.get("player_name")
    }
    lock_names = []
    for player in scorers[:5]:
        if player["name"] not in unavailable_names and player["recent_starts"] >= 3:
            lock_names.append(player["name"])
    for player in likely:
        if len(lock_names) >= 8:
            break
        if player["name"] not in lock_names and player["name"] not in unavailable_names:
            lock_names.append(player["name"])

    caution = [
        player
        for player in card_risks
        if player.get("cards_per_recent_start", 0) >= 0.45
    ][:4]
    attacking = probability["expected_goals_for"] >= probability["expected_goals_against"] + 0.25
    plan = "Önde baskı ve skor arama" if attacking else "Dengeli başlangıç, ikinci yarı hamle"
    return {
        "plan": plan,
        "core_starters": lock_names[:11],
        "attacking_priority": [player["name"] for player in scorers[:3]],
        "card_caution": [
            {
                "name": player["name"],
                "cards_per_recent_start": player["cards_per_recent_start"],
                "recommendation": "Erken kart görürse tempo düşür veya değişiklik planla.",
            }
            for player in caution
        ],
        "unavailable_removed": sorted(name for name in unavailable_names if name),
    }


def lineup_score(
    names: set[str],
    core_names: list[str],
    attack_names: list[str],
    goal_by_name: dict[str, dict],
    card_by_name: dict[str, dict],
) -> float:
    score = 0.0
    for name in names:
        if name in core_names:
            score += 8
        if name in attack_names:
            score += 7
        score += min(9, (goal_by_name.get(name, {}).get("goal_threat_score") or 0) * 0.45)
        score -= min(5, (card_by_name.get(name, {}).get("cards_per_recent_start") or 0) * 2.0)
    return max(1.0, score)


def build_coach_lineup_audit(
    target_match: dict,
    side: str,
    player_signals: dict,
    goal_candidates: dict,
    lineup_recommendation: dict,
    probability: dict,
) -> dict:
    actual_starters = [
        {
            "player_id": player.get("external_id"),
            "name": player.get("name"),
        }
        for player in target_match.get("lineups", {}).get(side, {}).get("starting", [])
    ]
    actual_names = {player["name"] for player in actual_starters if player.get("name")}
    core_names = lineup_recommendation.get("core_starters", [])
    attack_names = lineup_recommendation.get("attacking_priority", [])
    goal_by_name = {candidate["name"]: candidate for candidate in goal_candidates.get("candidates", [])}
    recent_by_name = {player["name"]: player for player in player_signals.get("likely_starters", [])}
    card_by_name = {player["name"]: player for player in player_signals.get("card_risk_players", [])}

    omitted_core = [name for name in core_names if name and name not in actual_names]
    omitted_attack = [name for name in attack_names if name and name not in actual_names]
    questionable = []
    for player in actual_starters:
        name = player.get("name")
        if not name:
            continue
        recent = recent_by_name.get(name, {})
        goal = goal_by_name.get(name, {})
        card = card_by_name.get(name, {})
        if name not in core_names and recent.get("recent_starts", 0) < 4 and goal.get("goal_threat_score", 0) < 6:
            questionable.append(
                {
                    "name": name,
                    "reason": "Model çekirdek 11 veya hücum önceliğinde değil; son pencere ilk 11/gol tehdidi düşük.",
                    "recent_starts": recent.get("recent_starts", 0),
                    "goal_threat_score": goal.get("goal_threat_score", 0),
                }
            )
        elif card.get("cards_per_recent_start", 0) >= 0.75:
            questionable.append(
                {
                    "name": name,
                    "reason": "Yüksek kart riskiyle başladı; erken kart oyunu bozabilir.",
                    "recent_starts": recent.get("recent_starts", 0),
                    "goal_threat_score": goal.get("goal_threat_score", 0),
                }
            )

    actual_score = lineup_score(actual_names, core_names, attack_names, goal_by_name, card_by_name)
    recommended_score = lineup_score(set(core_names[:11]), core_names, attack_names, goal_by_name, card_by_name)
    alignment = actual_score / recommended_score if recommended_score else 1.0
    possible_xg_gain = max(0.0, (recommended_score - actual_score) / 100)
    simulated_for = round(probability["expected_goals_for"] + min(0.35, possible_xg_gain), 2)
    simulated_against = round(probability["expected_goals_against"], 2)
    scorelines = scoreline_probabilities(simulated_for, simulated_against)
    verdict = "UYUMLU"
    if alignment < 0.72 or len(omitted_attack) >= 2:
        verdict = "TARTIŞMALI"
    elif alignment < 0.86 or omitted_core:
        verdict = "KISMEN_TARTIŞMALI"
    return {
        "verdict": verdict,
        "actual_lineup_score": round(actual_score, 2),
        "recommended_lineup_score": round(recommended_score, 2),
        "alignment_rate": round(alignment, 3),
        "actual_starters": [player["name"] for player in actual_starters if player.get("name")],
        "model_core_starters": core_names[:11],
        "omitted_core_players": omitted_core[:8],
        "omitted_attacking_priority": omitted_attack[:5],
        "questionable_starters": questionable[:8],
        "alternative_xg_for": simulated_for,
        "alternative_xg_against": simulated_against,
        "alternative_scoreline": scorelines[0] if scorelines else None,
        "note": "Bu denetim gerçek maçtan önceki kullanım/gol/kart sinyaliyle çalışır; teknik direktörün antrenman, sakatlık ve taktik bilgisine sahip değildir.",
    }
