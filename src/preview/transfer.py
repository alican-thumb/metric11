from __future__ import annotations

import json
from pathlib import Path

from src.preview.probability import poisson_outcome_probabilities, scoreline_probabilities


def impact_label(edge_delta: float) -> str:
    if edge_delta >= 0.45:
        return "HIGH_IMPACT"
    if edge_delta >= 0.25:
        return "MEDIUM_IMPACT"
    if edge_delta >= 0.1:
        return "LOW_POSITIVE"
    return "MARGINAL"


def transfer_xg_delta(role_key: str, candidate: dict) -> tuple[float, float]:
    fit = min(150, candidate.get("role_fit_score", 0))
    fit_unit = fit / 150
    goals = candidate.get("goals", 0)
    starts = candidate.get("starts", 0)
    load_max = candidate.get("estimated_physical_load_km_max") or 9.5
    economy = candidate.get("economy_score") or 0
    confidence = candidate.get("position_confidence", "VERY_LOW")
    confidence_factor = {"MEDIUM_EXTERNAL": 1.0, "LOW_DERIVED": 0.72, "VERY_LOW": 0.45}.get(confidence, 0.6)
    availability_factor = min(1.0, max(0.55, starts / 24))
    if role_key == "ST_SCORER":
        xg_for = 0.10 + min(0.42, goals * 0.012 + fit_unit * 0.25)
        xg_against = 0.0
    elif role_key == "LW_CREATOR":
        xg_for = 0.08 + min(0.32, goals * 0.007 + max(0, load_max - 9.8) * 0.045 + fit_unit * 0.18)
        xg_against = min(0.08, max(0, load_max - 10.4) * 0.025)
    elif role_key == "CM_ENGINE":
        xg_for = 0.04 + min(0.16, fit_unit * 0.12)
        xg_against = 0.06 + min(0.18, max(0, load_max - 10.0) * 0.045)
    elif role_key == "DM_SECURITY":
        xg_for = 0.02 + min(0.08, fit_unit * 0.06)
        xg_against = 0.10 + min(0.22, fit_unit * 0.16)
    elif role_key == "FB_TWO_WAY":
        xg_for = 0.04 + min(0.15, fit_unit * 0.1 + max(0, load_max - 10.0) * 0.03)
        xg_against = 0.05 + min(0.14, fit_unit * 0.09)
    elif role_key == "CB_DOMINANT":
        xg_for = min(0.08, candidate.get("header_goals", 0) * 0.012)
        xg_against = 0.09 + min(0.2, fit_unit * 0.14)
    else:
        xg_for = min(0.1, fit_unit * 0.08)
        xg_against = 0.0
    economy_factor = 1.0 + min(0.08, max(-0.08, economy / 300))
    return round(xg_for * confidence_factor * availability_factor * economy_factor, 3), round(
        xg_against * confidence_factor * availability_factor,
        3,
    )


def simulate_transfer_candidate(probability: dict, role: dict, candidate: dict) -> dict | None:
    role_key = role.get("role_key")
    current_for = probability.get("expected_goals_for", 0)
    current_against = probability.get("expected_goals_against", 0)
    fit = candidate.get("role_fit_score", 0)
    if fit <= 0:
        return None
    xg_for_delta, xg_against_delta = transfer_xg_delta(role_key, candidate)
    simulated_for = round(max(0.25, current_for + xg_for_delta), 2)
    simulated_against = round(max(0.15, current_against - xg_against_delta), 2)
    outcome = poisson_outcome_probabilities(simulated_for, simulated_against)
    scorelines = scoreline_probabilities(simulated_for, simulated_against)
    current_edge = current_for - current_against
    simulated_edge = simulated_for - simulated_against
    return {
        "player_name": candidate.get("name"),
        "current_team": candidate.get("team"),
        "target_role": role.get("label"),
        "role_key": role_key,
        "role_fit_score": fit,
        "position_confidence": candidate.get("position_confidence"),
        "age": candidate.get("age"),
        "economy_score": candidate.get("economy_score"),
        "current_expected_goals_for": current_for,
        "current_expected_goals_against": current_against,
        "simulated_expected_goals_for": simulated_for,
        "simulated_expected_goals_against": simulated_against,
        "xg_for_delta": round(xg_for_delta, 2),
        "xg_against_delta": round(xg_against_delta, 2),
        "goal_edge_delta": round(simulated_edge - current_edge, 2),
        "simulated_target_win_probability": round(outcome["target"], 3),
        "simulated_draw_probability": round(outcome["draw"], 3),
        "simulated_opponent_win_probability": round(outcome["opponent"], 3),
        "simulated_scoreline": scorelines[0],
        "impact_label": impact_label(simulated_edge - current_edge),
        "why": candidate.get("why_fit"),
        "commercial_note": candidate.get("commercial_note"),
    }


def build_transfer_impact_simulations(probability: dict, target_team: str, limit: int = 6, processed_dir: Path | None = None) -> dict:
    from src.config import PROCESSED_DIR
    matrix_path = (processed_dir or PROCESSED_DIR) / "position_scout_matrix_2025_2026.json"
    if not matrix_path.exists():
        return {
            "available": False,
            "note": "Pozisyon scout matrisi yok; transfer etki simülasyonu üretilemedi.",
            "candidates": [],
        }
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    seen = set()
    candidates = []
    role_priority = ["LW_CREATOR", "ST_SCORER", "CM_ENGINE", "DM_SECURITY", "FB_TWO_WAY", "CB_DOMINANT"]
    roles = sorted(
        matrix.get("roles", []),
        key=lambda role: role_priority.index(role.get("role_key")) if role.get("role_key") in role_priority else 99,
    )
    for role in roles:
        for candidate in role.get("top_candidates", []):
            name = candidate.get("name")
            if not name or name in seen or candidate.get("team") == target_team:
                continue
            simulation = simulate_transfer_candidate(probability, role, candidate)
            if simulation:
                candidates.append(simulation)
                seen.add(name)
            if len(candidates) >= limit:
                break
        if len(candidates) >= limit:
            break
    return {
        "available": bool(candidates),
        "source": "position_scout_matrix_2025_2026",
        "note": "Bu senaryo oyuncunun gerçekten oynayacağı, uyum sağlayacağı veya transfer edilebileceği anlamına gelmez; rol-fit skorundan türetilmiş düşük/orta güvenli etki simülasyonudur.",
        "candidates": candidates,
    }
