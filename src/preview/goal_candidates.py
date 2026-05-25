from __future__ import annotations

import json
from collections import Counter
from functools import lru_cache

from src.config import PROCESSED_DIR
from src.preview.constants import BIG_MATCH_OPPONENTS, SPECIALIST_SCORE_MULTIPLIERS


def summarize_goal_candidates(
    prior_matches: list[dict],
    target_match: dict,
    target_team: str,
    is_big_match: bool,
    opponent_defense: dict,
    unavailable_ids: set[str] | None = None,
) -> dict:
    unavailable_ids = unavailable_ids or set()
    team_matches = [
        match
        for match in prior_matches
        if match["home_team"]["name"] == target_team or match["away_team"]["name"] == target_team
    ]
    recent_matches = team_matches[-8:]
    starts = Counter()
    goals = Counter()
    recent_goals = Counter()
    big_match_goals = Counter()
    player_names = {}

    for idx, match in enumerate(team_matches):
        side = "home" if match["home_team"]["name"] == target_team else "away"
        opp_side = "away" if side == "home" else "home"
        opponent = match[f"{opp_side}_team"]["name"]
        match_is_big = opponent in BIG_MATCH_OPPONENTS

        for player in match["lineups"][side]["starting"]:
            key = player["external_id"] or player["name"]
            player_names[key] = player["name"]
            if match in recent_matches:
                starts[key] += 1

        for goal in match.get("goals", {}).get(side, []):
            key = goal.get("player_external_id") or goal.get("player_name")
            if not key:
                continue
            player_names[key] = goal.get("player_name") or player_names.get(key, key)
            goals[key] += 1
            if match in recent_matches:
                recent_goals[key] += 1
            if match_is_big:
                big_match_goals[key] += 1

    target_side = "home" if target_match["home_team"]["name"] == target_team else "away"
    actual_scorers = [
        {
            "player_id": goal.get("player_external_id"),
            "name": goal.get("player_name"),
            "minute": goal.get("minute"),
            "type": goal.get("type"),
        }
        for goal in target_match.get("goals", {}).get(target_side, [])
    ]
    actual_scorer_ids = {goal["player_id"] for goal in actual_scorers if goal.get("player_id")}

    candidates = []
    specialist_candidates = []
    for player_id, start_count in starts.items():
        if player_id in unavailable_ids:
            continue
        total_goal_count = goals[player_id]
        recent_goal_count = recent_goals[player_id]
        big_goal_count = big_match_goals[player_id]
        opponent_multiplier = opponent_defense.get("goal_candidate_multiplier", 1.0)
        score = (recent_goal_count * 3.5 + total_goal_count * 1.15 + start_count * 0.32) * opponent_multiplier
        if is_big_match:
            score += big_goal_count * 1.0
        candidates.append(
            {
                "player_id": player_id,
                "name": player_names.get(player_id, player_id),
                "goal_threat_score": round(score, 2),
                "candidate_type": "primary",
                "recent_starts": start_count,
                "season_goals_before_match": total_goal_count,
                "recent_goals": recent_goal_count,
                "big_match_goals_before_match": big_goal_count,
                "opponent_defense_multiplier": round(opponent_multiplier, 2),
                "actual_scorer": player_id in actual_scorer_ids,
            }
        )

    specialist_candidates.extend(
        build_goal_specialists(
            team_matches=team_matches,
            recent_matches=recent_matches,
            target_team=target_team,
            player_names=player_names,
            starts=starts,
            goals=goals,
            recent_goals=recent_goals,
            big_match_goals=big_match_goals,
            actual_scorer_ids=actual_scorer_ids,
            unavailable_ids=unavailable_ids,
            is_big_match=is_big_match,
            opponent_multiplier=opponent_defense.get("goal_candidate_multiplier", 1.0),
        )
    )

    candidates = merge_goal_candidates(candidates, specialist_candidates)
    quality_penalties = load_goal_candidate_quality_penalties()
    candidates = apply_goal_candidate_quality_penalties(candidates, quality_penalties)
    candidates.sort(
        key=lambda item: (
            item["goal_threat_score"],
            item["recent_goals"],
            item["season_goals_before_match"],
            item["recent_starts"],
        ),
        reverse=True,
    )
    top_candidates = candidates[:10]
    hit_top_3 = any(candidate["actual_scorer"] for candidate in top_candidates[:3])
    hit_top_5 = any(candidate["actual_scorer"] for candidate in top_candidates[:5])
    hit_top_8 = any(candidate["actual_scorer"] for candidate in top_candidates[:8])
    hit_top_10 = any(candidate["actual_scorer"] for candidate in top_candidates[:10])
    return {
        "window_matches": len(recent_matches),
        "candidates": top_candidates,
        "specialist_candidate_count": len(specialist_candidates),
        "actual_scorers": actual_scorers,
        "hit_top_3": hit_top_3,
        "hit_top_5": hit_top_5,
        "hit_top_8": hit_top_8,
        "hit_top_10": hit_top_10,
        "opponent_defense": opponent_defense,
        "note": "Gol adayi skoru TFF gol/ilk 11 gecmisi, son form, rakip savunma, duran top/defans, yedek etki ve segment backtest kalite sinyallerinden turetilen MVP sinyalidir.",
    }


def build_goal_specialists(
    team_matches: list[dict],
    recent_matches: list[dict],
    target_team: str,
    player_names: dict,
    starts: Counter,
    goals: Counter,
    recent_goals: Counter,
    big_match_goals: Counter,
    actual_scorer_ids: set[str],
    unavailable_ids: set[str],
    is_big_match: bool,
    opponent_multiplier: float,
) -> list[dict]:
    bench = Counter()
    cards = Counter()
    header_goals = Counter()
    penalty_goals = Counter()
    recent_bench = Counter()
    recent_cards = Counter()
    for match in team_matches:
        side = "home" if match["home_team"]["name"] == target_team else "away"
        is_recent = match in recent_matches
        for player in match["lineups"][side]["bench"]:
            key = player["external_id"] or player["name"]
            player_names[key] = player["name"]
            bench[key] += 1
            if is_recent:
                recent_bench[key] += 1
        for card in match["cards"][side]:
            key = card.get("player_external_id") or card.get("player_name")
            if not key:
                continue
            cards[key] += 1
            if is_recent:
                recent_cards[key] += 1
        for goal in match.get("goals", {}).get(side, []):
            key = goal.get("player_external_id") or goal.get("player_name")
            if not key:
                continue
            if goal.get("type") == "H":
                header_goals[key] += 1
            if goal.get("type") == "P":
                penalty_goals[key] += 1

    specialists = []
    player_ids = set(bench) | set(cards) | set(header_goals) | set(penalty_goals) | set(goals)
    for player_id in player_ids:
        if player_id in unavailable_ids:
            continue
        total_goals = goals[player_id]
        start_count = starts[player_id]
        bench_count = bench[player_id]
        recent_bench_count = recent_bench[player_id]
        aerial_score = header_goals[player_id] * 5.0 + cards[player_id] * 0.55 + start_count * 0.12
        bench_score = 0.0
        if total_goals or recent_goals[player_id]:
            bench_score = recent_bench_count * 0.75 + recent_goals[player_id] * 3.2 + total_goals * 0.85
        penalty_score = penalty_goals[player_id] * 4.5 + total_goals * 0.55
        big_match_score = big_match_goals[player_id] * 3.0 if is_big_match else 0

        typed_scores = [
            ("set_piece_defender", aerial_score),
            ("impact_sub", bench_score),
            ("penalty_profile", penalty_score),
            ("big_match_scorer", big_match_score),
        ]
        candidate_type, score = max(typed_scores, key=lambda item: item[1])
        if score < 3.4:
            continue
        score = (score + total_goals * 0.35) * opponent_multiplier
        score *= SPECIALIST_SCORE_MULTIPLIERS.get(candidate_type, 1.0)
        specialists.append(
            {
                "player_id": player_id,
                "name": player_names.get(player_id, player_id),
                "goal_threat_score": round(score, 2),
                "candidate_type": candidate_type,
                "recent_starts": start_count,
                "recent_bench": recent_bench_count,
                "season_goals_before_match": total_goals,
                "recent_goals": recent_goals[player_id],
                "big_match_goals_before_match": big_match_goals[player_id],
                "header_goals_before_match": header_goals[player_id],
                "penalty_goals_before_match": penalty_goals[player_id],
                "cards_before_match": cards[player_id],
                "recent_cards": recent_cards[player_id],
                "opponent_defense_multiplier": round(opponent_multiplier, 2),
                "actual_scorer": player_id in actual_scorer_ids,
            }
        )
    return specialists


def merge_goal_candidates(primary: list[dict], specialists: list[dict]) -> list[dict]:
    by_player = {item["player_id"]: item for item in primary}
    for item in specialists:
        existing = by_player.get(item["player_id"])
        if not existing:
            by_player[item["player_id"]] = item
            continue
        if item["goal_threat_score"] > existing["goal_threat_score"] * 0.82:
            existing["goal_threat_score"] = round(max(existing["goal_threat_score"], item["goal_threat_score"] * 0.92), 2)
            existing["candidate_type"] = f"{existing.get('candidate_type', 'primary')}+{item['candidate_type']}"
            for key in ("header_goals_before_match", "penalty_goals_before_match", "recent_bench", "cards_before_match", "recent_cards"):
                if key in item:
                    existing[key] = item[key]
    return list(by_player.values())


def apply_goal_candidate_quality_penalties(candidates: list[dict], penalties: dict[tuple[str, str], dict]) -> list[dict]:
    if not penalties:
        return candidates
    for candidate in candidates:
        penalty = find_goal_candidate_penalty(candidate, penalties)
        if not penalty:
            continue
        multiplier = penalty.get("multiplier", 1.0)
        candidate["goal_threat_score"] = round(candidate["goal_threat_score"] * multiplier, 2)
        candidate["quality_adjustment"] = {
            "multiplier": multiplier,
            "reason": penalty.get("reason", "Segment backtest zayif Top 5 performansi."),
            "source": "goal_candidate_segment_backtest",
        }
    return candidates


def find_goal_candidate_penalty(candidate: dict, penalties: dict[tuple[str, str], dict]) -> dict | None:
    name = normalize_name(candidate.get("name", ""))
    candidate_types = split_candidate_type(candidate.get("candidate_type"))
    exact = penalties.get((name, candidate.get("candidate_type", "")))
    if exact:
        return exact
    for candidate_type in candidate_types:
        penalty = penalties.get((name, candidate_type))
        if penalty:
            return penalty
    return penalties.get((name, "*"))


@lru_cache(maxsize=1)
def load_goal_candidate_quality_penalties() -> dict[tuple[str, str], dict]:
    path = PROCESSED_DIR / "goal_candidate_segment_backtest_2025_2026.json"
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    penalties = {}
    for row in payload.get("weak_candidates", []):
        player_name = normalize_name(row.get("player_name", ""))
        if not player_name:
            continue
        top5_rows = row.get("top5_rows", 0) or 0
        hits = row.get("hits", 0) or 0
        if top5_rows < 3 or hits:
            continue
        multiplier = 0.68 if top5_rows >= 5 else 0.78
        penalty = {
            "multiplier": multiplier,
            "reason": row.get("recommendation") or "Top 5 siralama etkisini dusur.",
        }
        candidate_type = row.get("candidate_type") or "*"
        penalties[(player_name, candidate_type)] = penalty
        for part in split_candidate_type(candidate_type):
            penalties[(player_name, part)] = penalty
    return penalties


def split_candidate_type(candidate_type: str | None) -> list[str]:
    if not candidate_type:
        return []
    return [part.strip() for part in candidate_type.split("+") if part.strip()]


def normalize_name(name: str) -> str:
    return " ".join(str(name).casefold().split())
