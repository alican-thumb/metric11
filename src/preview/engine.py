from __future__ import annotations

import json
from pathlib import Path

from src.config import PROCESSED_DIR, SEASON
from src.normalization import normalize_matches
from src.preview.constants import BIG_MATCH_OPPONENTS
from src.preview.form import parse_tff_datetime, summarize_team_form, summarize_team_strength
from src.preview.goal_candidates import summarize_goal_candidates
from src.preview.lineup import build_coach_lineup_audit, build_lineup_recommendation
from src.preview.markdown import build_markdown
from src.preview.narrative import build_narrative
from src.preview.opponent import summarize_opponent_defense, summarize_opponent_vs_besiktas_history
from src.preview.players import availability_for_match, summarize_players, summarize_referee
from src.preview.probability import estimate_probabilities
from src.preview.squad import build_player_importance, squad_xg_adjustment
from src.preview.transfer import build_transfer_impact_simulations


def build_preview(matches: list[dict], target_team: str, match_id: str, availability: dict | None = None) -> dict:
    matches = normalize_matches(matches)
    indexed = {match["external_id"]: match for match in matches}
    if match_id not in indexed:
        raise SystemExit(f"Mac ID bulunamadi: {match_id}")

    target_match = indexed[match_id]
    target_date = parse_tff_datetime(target_match["match_date"])
    prior_matches = [
        match
        for match in matches
        if match["external_id"] != match_id and parse_tff_datetime(match["match_date"]) < target_date
    ]
    prior_matches.sort(key=lambda match: parse_tff_datetime(match["match_date"]))
    if not prior_matches:
        raise SystemExit("Bu mac icin onceki veri yok; daha ileri haftadan bir mac sec.")

    side = "home" if target_match["home_team"]["name"] == target_team else "away"
    opp_side = "away" if side == "home" else "home"
    opponent = target_match[f"{opp_side}_team"]["name"]
    is_big_match = opponent in BIG_MATCH_OPPONENTS

    # Build player importance using all matches (not just prior) for stable importance scores
    gk_ids = _load_gk_ids(target_team)
    player_importance = build_player_importance(matches, target_team, gk_ids=gk_ids)
    availability_signal = availability_for_match(availability, match_id, player_importance)
    unavailable_ids = {
        item.get("player_external_id")
        for item in availability_signal.get("unavailable", [])
        if item.get("player_external_id")
    }
    squad_adj, squad_adj_breakdown = squad_xg_adjustment(player_importance, unavailable_ids)
    availability_signal["squad_xg_adjustment"] = squad_adj
    availability_signal["squad_adjustment_breakdown"] = squad_adj_breakdown

    team_form = summarize_team_form(prior_matches, target_team, last_n=5)
    if team_form["last_n"] == 0:
        raise SystemExit("Bu mac icin hedef takimin onceki kronolojik mac verisi yok.")
    opponent_recent_form = summarize_team_form(prior_matches, opponent, last_n=5)
    team_strength = summarize_team_strength(prior_matches, target_team, side)
    opponent_strength = summarize_team_strength(prior_matches, opponent, opp_side)
    opponent_form = summarize_opponent_vs_besiktas_history(prior_matches, target_team, opponent)
    player_signals = summarize_players(prior_matches, target_team, is_big_match, unavailable_ids)
    opponent_defense = summarize_opponent_defense(prior_matches, opponent)
    goal_candidates = summarize_goal_candidates(prior_matches, target_match, target_team, is_big_match, opponent_defense, unavailable_ids)
    referee = next((official for official in target_match["officials"] if official["role"] == "Hakem"), None)
    referee_signal = summarize_referee(prior_matches, target_team, referee["name"] if referee else None)
    probability = estimate_probabilities(
        team_form,
        opponent_recent_form,
        opponent_form,
        referee_signal,
        is_big_match,
        availability_signal,
        side,
        team_strength,
        opponent_strength,
        target_team=target_team,
        opponent_name=opponent,
        enable_display_calibration=target_team == "BEŞİKTAŞ A.Ş.",
    )
    lineup_recommendation = build_lineup_recommendation(player_signals, goal_candidates, availability_signal, probability)
    coach_lineup_audit = build_coach_lineup_audit(target_match, side, player_signals, goal_candidates, lineup_recommendation, probability)
    transfer_impact = build_transfer_impact_simulations(probability, target_team)

    return {
        "match": {
            "match_id": target_match["external_id"],
            "date": target_match["match_date"],
            "home_team": target_match["home_team"]["name"],
            "away_team": target_match["away_team"]["name"],
            "actual_score": f"{target_match['home_team']['score']}-{target_match['away_team']['score']}",
            "target_team": target_team,
            "opponent": opponent,
            "home_away": side,
            "is_big_match": is_big_match,
            "main_referee": referee["name"] if referee else None,
        },
        "data_window": {
            "prior_match_count": team_form["total_prior_team_matches"],
            "prior_league_match_count": len(prior_matches),
            "target_date": target_date.isoformat(),
            "note": "Bu rapor yalnizca secili mac tarihinden once oynanmis TFF sezon verisini kullanir.",
        },
        "team_form": team_form,
        "team_strength_signal": team_strength,
        "opponent_history": opponent_form,
        "opponent_recent_form": opponent_recent_form,
        "opponent_strength_signal": opponent_strength,
        "opponent_defense": opponent_defense,
        "availability_signal": availability_signal,
        "referee_signal": referee_signal,
        "player_signals": player_signals,
        "goal_candidates": goal_candidates,
        "probabilities": probability,
        "lineup_recommendation": lineup_recommendation,
        "coach_lineup_audit": coach_lineup_audit,
        "transfer_impact_simulations": transfer_impact,
        "narrative": build_narrative(
            target_team,
            opponent,
            team_form,
            team_strength,
            opponent_recent_form,
            opponent_strength,
            opponent_form,
            opponent_defense,
            availability_signal,
            referee_signal,
            player_signals,
            goal_candidates,
            probability,
            lineup_recommendation,
            coach_lineup_audit,
            transfer_impact,
            is_big_match,
        ),
    }


def _load_gk_ids(team: str) -> set[str]:
    """Load external_ids of known goalkeepers for the team from enriched player profiles."""
    enriched_path = PROCESSED_DIR / f"tff_player_profiles_enriched_{SEASON}.json"
    if not enriched_path.exists():
        return set()
    try:
        players = json.loads(enriched_path.read_text(encoding="utf-8"))
        team_lower = team.casefold()
        return {
            str(p.get("external_id") or p.get("tff_external_id") or "")
            for p in players
            if p.get("tm_position_group") == "GK"
            and (p.get("club") or p.get("tm_team_name") or "").casefold() == team_lower
        } - {""}
    except Exception:
        return set()


def write_preview(preview: dict, output_prefix: str, output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{output_prefix}.json"
    md_path = output_dir / f"{output_prefix}.md"
    json_path.write_text(json.dumps(preview, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(build_markdown(preview), encoding="utf-8")
    return json_path, md_path
