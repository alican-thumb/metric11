from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

from src.config import PROCESSED_DIR
from src.normalization import normalize_matches


def main() -> None:
    parser = argparse.ArgumentParser(description="TFF lig verisinden takim, oyuncu ve scout metrikleri uretir.")
    parser.add_argument("--input", default=str(PROCESSED_DIR / "tff_super_lig_enriched_2025_2026.json"))
    parser.add_argument("--output-prefix", default="league_scouting_2025_2026")
    args = parser.parse_args()

    matches = normalize_matches(json.loads(Path(args.input).read_text(encoding="utf-8")))
    metrics = build_metrics(matches)

    json_path = PROCESSED_DIR / f"{args.output_prefix}.json"
    md_path = PROCESSED_DIR / f"{args.output_prefix}.md"
    json_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(build_markdown(metrics), encoding="utf-8")
    print(md_path.read_text(encoding="utf-8"))


def build_metrics(matches: list[dict]) -> dict:
    team = defaultdict(lambda: Counter())
    players = defaultdict(lambda: Counter())
    player_names = {}
    player_teams = defaultdict(Counter)
    referee = defaultdict(lambda: Counter())

    for match in matches:
        for side, opp_side in (("home", "away"), ("away", "home")):
            team_name = match[f"{side}_team"]["name"]
            opp_name = match[f"{opp_side}_team"]["name"]
            gf = match[f"{side}_team"]["score"] or 0
            ga = match[f"{opp_side}_team"]["score"] or 0
            cards = len(match["cards"][side])

            team[team_name]["matches"] += 1
            team[team_name]["goals_for"] += gf
            team[team_name]["goals_against"] += ga
            team[team_name]["cards"] += cards
            team[team_name]["wins"] += int(gf > ga)
            team[team_name]["draws"] += int(gf == ga)
            team[team_name]["losses"] += int(gf < ga)
            team[team_name]["clean_sheets"] += int(ga == 0)
            team[team_name]["failed_to_score"] += int(gf == 0)

            for player in match["lineups"][side]["starting"]:
                key = player["external_id"] or player["name"]
                player_names[key] = player["name"]
                player_teams[key][team_name] += 1
                players[key]["starts"] += 1
                players[key]["squad_inclusions"] += 1
            for player in match["lineups"][side]["bench"]:
                key = player["external_id"] or player["name"]
                player_names[key] = player["name"]
                player_teams[key][team_name] += 1
                players[key]["bench"] += 1
                players[key]["squad_inclusions"] += 1
            for goal in match.get("goals", {}).get(side, []):
                key = goal.get("player_external_id") or goal.get("player_name")
                if not key:
                    continue
                player_names[key] = goal.get("player_name") or player_names.get(key, key)
                player_teams[key][team_name] += 1
                players[key]["goals"] += 1
                if goal.get("type") == "P":
                    players[key]["penalty_goals"] += 1
                if goal.get("type") == "H":
                    players[key]["header_goals"] += 1
            for card in match["cards"][side]:
                key = card.get("player_external_id") or card.get("player_name")
                if not key:
                    continue
                player_names[key] = card.get("player_name") or player_names.get(key, key)
                player_teams[key][team_name] += 1
                players[key]["cards"] += 1

        main_referee = next((official for official in match["officials"] if official["role"] == "Hakem"), None)
        if main_referee:
            total_cards = len(match["cards"]["home"]) + len(match["cards"]["away"])
            referee[main_referee["name"]]["matches"] += 1
            referee[main_referee["name"]]["cards"] += total_cards
            referee[main_referee["name"]]["goals"] += (match["home_team"]["score"] or 0) + (match["away_team"]["score"] or 0)

    team_metrics = {}
    for name, rec in team.items():
        matches_count = rec["matches"]
        team_metrics[name] = {
            **rec,
            "points": rec["wins"] * 3 + rec["draws"],
            "goals_for_per_match": round(rec["goals_for"] / matches_count, 2),
            "goals_against_per_match": round(rec["goals_against"] / matches_count, 2),
            "cards_per_match": round(rec["cards"] / matches_count, 2),
            "clean_sheet_rate": round(rec["clean_sheets"] / matches_count, 3),
            "failed_to_score_rate": round(rec["failed_to_score"] / matches_count, 3),
        }

    player_metrics = []
    for pid, rec in players.items():
        starts = rec["starts"]
        goals = rec["goals"]
        cards = rec["cards"]
        primary_team = player_teams[pid].most_common(1)[0][0] if player_teams[pid] else None
        goals_per_start = goals / starts if starts else 0
        cards_per_start = cards / starts if starts else 0
        player_metrics.append(
            {
                "player_id": pid,
                "name": player_names.get(pid, pid),
                "team": primary_team,
                "starts": starts,
                "bench": rec["bench"],
                "squad_inclusions": rec["squad_inclusions"],
                "goals": goals,
                "penalty_goals": rec["penalty_goals"],
                "header_goals": rec["header_goals"],
                "cards": cards,
                "goals_per_start": round(goals_per_start, 3),
                "cards_per_start": round(cards_per_start, 3),
                "availability_score": round(min(100, rec["squad_inclusions"] / 34 * 100), 1),
                "finishing_signal": score_finishing(goals, starts, rec["penalty_goals"]),
                "discipline_risk": score_discipline(cards, starts),
                "scout_value_score": score_scout_value(goals, starts, cards, rec["bench"]),
            }
        )

    player_metrics.sort(key=lambda item: item["scout_value_score"], reverse=True)
    referee_metrics = {
        name: {
            **rec,
            "cards_per_match": round(rec["cards"] / rec["matches"], 2),
            "goals_per_match": round(rec["goals"] / rec["matches"], 2),
        }
        for name, rec in referee.items()
    }

    return {
        "team_metrics": dict(sorted(team_metrics.items(), key=lambda item: item[1]["points"], reverse=True)),
        "top_scorers": sorted(player_metrics, key=lambda item: (item["goals"], item["goals_per_start"]), reverse=True)[:30],
        "player_pool": player_metrics,
        "scout_shortlist": player_metrics[:40],
        "discipline_risks": sorted(player_metrics, key=lambda item: (item["cards_per_start"], item["cards"]), reverse=True)[:30],
        "referee_metrics": dict(sorted(referee_metrics.items(), key=lambda item: item[1]["cards_per_match"], reverse=True)),
    }


def score_finishing(goals: int, starts: int, penalties: int) -> float:
    non_penalty_goals = max(0, goals - penalties)
    return round(non_penalty_goals * 4 + goals * 1.5 + starts * 0.15, 2)


def score_discipline(cards: int, starts: int) -> str:
    if starts < 5:
        return "LOW_SAMPLE"
    rate = cards / starts
    if rate >= 0.35:
        return "HIGH"
    if rate >= 0.2:
        return "MEDIUM"
    return "LOW"


def score_scout_value(goals: int, starts: int, cards: int, bench: int) -> float:
    # MVP proxy: production and availability, penalized for card risk and low-start noise.
    start_bonus = min(starts, 25) * 0.5
    goal_bonus = goals * 5.0
    rotation_bonus = min(bench, 12) * 0.15
    card_penalty = cards * 0.7
    sample_penalty = 5 if starts < 5 else 0
    return round(goal_bonus + start_bonus + rotation_bonus - card_penalty - sample_penalty, 2)


def build_markdown(metrics: dict) -> str:
    lines = [
        "# Süper Lig 2025-2026 Scout ve Lig Metrikleri",
        "",
        "## Takım Güçleri",
        "",
    ]
    for name, rec in list(metrics["team_metrics"].items())[:20]:
        lines.append(
            f"- {name}: puan={rec['points']}, gol={rec['goals_for']}-{rec['goals_against']}, "
            f"GF/M={rec['goals_for_per_match']}, GA/M={rec['goals_against_per_match']}, kart/M={rec['cards_per_match']}"
        )

    lines.extend(["", "## Golcü Listesi", ""])
    for player in metrics["top_scorers"][:20]:
        lines.append(
            f"- {player['name']} ({player['team']}): gol={player['goals']}, ilk 11={player['starts']}, "
            f"gol/ilk 11={player['goals_per_start']}, bitiricilik={player['finishing_signal']}"
        )

    lines.extend(["", f"## Scout Kısa Liste (Lig Havuzu: {len(metrics.get('player_pool', metrics['scout_shortlist']))} Oyuncu)", ""])
    for player in metrics["scout_shortlist"][:20]:
        lines.append(
            f"- {player['name']} ({player['team']}): scout={player['scout_value_score']}, gol={player['goals']}, "
            f"ilk 11={player['starts']}, disiplin={player['discipline_risk']}, uygunluk={player['availability_score']}"
        )

    lines.extend(["", "## Sert Hakemler", ""])
    for ref, rec in list(metrics["referee_metrics"].items())[:12]:
        lines.append(f"- {ref}: maç={rec['matches']}, kart/M={rec['cards_per_match']}, gol/M={rec['goals_per_match']}")

    return "\n".join(lines)


if __name__ == "__main__":
    main()
