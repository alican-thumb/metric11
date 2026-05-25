from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

from src.config import PROCESSED_DIR


BIG_MATCH_OPPONENTS = {
    "GALATASARAY A.Ş.",
    "FENERBAHÇE A.Ş.",
    "TRABZONSPOR A.Ş.",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Besiktas sezon detayli metrik raporu uretir.")
    parser.add_argument("--input", default=str(PROCESSED_DIR / "tff_besiktas_2025_2026_matches.json"))
    parser.add_argument("--team", default="BEŞİKTAŞ A.Ş.")
    parser.add_argument("--output-prefix", default="besiktas_2025_2026_deep_metrics")
    args = parser.parse_args()

    matches_path = Path(args.input)
    matches = json.loads(matches_path.read_text(encoding="utf-8"))
    metrics = build_metrics(matches, args.team)

    json_path = PROCESSED_DIR / f"{args.output_prefix}.json"
    md_path = PROCESSED_DIR / f"{args.output_prefix}.md"
    json_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(build_markdown(metrics, args.team), encoding="utf-8")
    print(md_path.read_text(encoding="utf-8"))


def build_metrics(matches: list[dict], target_team: str) -> dict:
    player_usage = defaultdict(
        lambda: {
            "name": None,
            "player_id": None,
            "appearances": 0,
            "starts": 0,
            "bench_selections": 0,
            "cards": 0,
            "big_match_appearances": 0,
            "big_match_starts": 0,
            "big_match_cards": 0,
            "home_starts": 0,
            "away_starts": 0,
            "matches": [],
        }
    )
    referee_records = defaultdict(lambda: {"matches": 0, "cards": 0, "bjk_cards": 0, "opponent_cards": 0, "big_matches": 0})
    opponent_records = defaultdict(lambda: {"matches": 0, "goals_for": 0, "goals_against": 0, "cards_for": 0, "cards_against": 0})
    team_totals = Counter()
    match_summaries = []

    for match in matches:
        side = "home" if match["home_team"]["name"] == target_team else "away"
        opp_side = "away" if side == "home" else "home"
        opponent = match[f"{opp_side}_team"]["name"]
        is_big_match = opponent in BIG_MATCH_OPPONENTS

        target_score = match[f"{side}_team"]["score"] or 0
        opponent_score = match[f"{opp_side}_team"]["score"] or 0
        target_cards = match["cards"][side]
        opponent_cards = match["cards"][opp_side]
        total_cards = len(target_cards) + len(opponent_cards)

        team_totals["matches"] += 1
        team_totals["goals_for"] += target_score
        team_totals["goals_against"] += opponent_score
        team_totals["cards"] += len(target_cards)
        team_totals["opponent_cards"] += len(opponent_cards)
        team_totals["big_matches"] += int(is_big_match)
        team_totals["big_match_cards"] += len(target_cards) if is_big_match else 0

        if target_score > opponent_score:
            team_totals["wins"] += 1
        elif target_score == opponent_score:
            team_totals["draws"] += 1
        else:
            team_totals["losses"] += 1

        opponent_records[opponent]["matches"] += 1
        opponent_records[opponent]["goals_for"] += target_score
        opponent_records[opponent]["goals_against"] += opponent_score
        opponent_records[opponent]["cards_for"] += len(target_cards)
        opponent_records[opponent]["cards_against"] += len(opponent_cards)

        main_referee = next((official for official in match["officials"] if official["role"] == "Hakem"), None)
        if main_referee:
            ref = referee_records[main_referee["name"]]
            ref["matches"] += 1
            ref["cards"] += total_cards
            ref["bjk_cards"] += len(target_cards)
            ref["opponent_cards"] += len(opponent_cards)
            ref["big_matches"] += int(is_big_match)

        carded_ids = Counter(card["player_external_id"] for card in target_cards if card.get("player_external_id"))
        carded_names = Counter(card["player_name"] for card in target_cards if card.get("player_name"))

        for lineup_type, field in (("starting", "starts"), ("bench", "bench_selections")):
            for player in match["lineups"][side][lineup_type]:
                key = player["external_id"] or player["name"]
                record = player_usage[key]
                record["name"] = player["name"]
                record["player_id"] = player["external_id"]
                record[field] += 1
                if lineup_type == "starting":
                    record["appearances"] += 1
                    record["home_starts"] += int(side == "home")
                    record["away_starts"] += int(side == "away")
                    record["big_match_appearances"] += int(is_big_match)
                    record["big_match_starts"] += int(is_big_match)
                record["cards"] += carded_ids.get(player["external_id"], 0) or carded_names.get(player["name"], 0)
                record["big_match_cards"] += (
                    carded_ids.get(player["external_id"], 0) or carded_names.get(player["name"], 0)
                ) if is_big_match else 0
                record["matches"].append(
                    {
                        "match_id": match["external_id"],
                        "date": match["match_date"],
                        "opponent": opponent,
                        "lineup_type": lineup_type,
                        "cards": carded_ids.get(player["external_id"], 0) or carded_names.get(player["name"], 0),
                        "big_match": is_big_match,
                    }
                )

        match_summaries.append(
            {
                "match_id": match["external_id"],
                "date": match["match_date"],
                "opponent": opponent,
                "home_away": side,
                "score_for": target_score,
                "score_against": opponent_score,
                "cards_for": len(target_cards),
                "cards_against": len(opponent_cards),
                "total_cards": total_cards,
                "main_referee": main_referee["name"] if main_referee else None,
                "big_match": is_big_match,
            }
        )

    player_metrics = []
    for record in player_usage.values():
        starts = record["starts"]
        cards = record["cards"]
        player_metrics.append(
            {
                "name": record["name"],
                "player_id": record["player_id"],
                "starts": starts,
                "bench_selections": record["bench_selections"],
                "cards": cards,
                "cards_per_start": round(cards / starts, 3) if starts else 0,
                "start_share": round(starts / team_totals["matches"], 3) if team_totals["matches"] else 0,
                "big_match_starts": record["big_match_starts"],
                "big_match_cards": record["big_match_cards"],
                "home_starts": record["home_starts"],
                "away_starts": record["away_starts"],
                "risk_level": risk_level(cards / starts if starts else 0, starts),
            }
        )

    player_metrics.sort(key=lambda item: (item["risk_level"], item["cards"], item["starts"]), reverse=True)

    return {
        "team": target_team,
        "season_match_count": team_totals["matches"],
        "team_summary": {
            "wins": team_totals["wins"],
            "draws": team_totals["draws"],
            "losses": team_totals["losses"],
            "goals_for": team_totals["goals_for"],
            "goals_against": team_totals["goals_against"],
            "cards": team_totals["cards"],
            "cards_per_match": round(team_totals["cards"] / team_totals["matches"], 2),
            "opponent_cards_per_match": round(team_totals["opponent_cards"] / team_totals["matches"], 2),
            "big_matches": team_totals["big_matches"],
            "big_match_cards_per_match": round(team_totals["big_match_cards"] / team_totals["big_matches"], 2)
            if team_totals["big_matches"]
            else 0,
        },
        "top_card_risk_players": player_metrics[:15],
        "most_used_players": sorted(player_metrics, key=lambda item: item["starts"], reverse=True)[:15],
        "referee_profiles": {
            referee: {
                **record,
                "cards_per_match": round(record["cards"] / record["matches"], 2),
                "bjk_cards_per_match": round(record["bjk_cards"] / record["matches"], 2),
            }
            for referee, record in sorted(referee_records.items())
        },
        "opponent_records": {
            opponent: {
                **record,
                "cards_for_per_match": round(record["cards_for"] / record["matches"], 2),
            }
            for opponent, record in sorted(opponent_records.items())
        },
        "match_summaries": match_summaries,
    }


def risk_level(cards_per_start: float, starts: int) -> str:
    if starts < 5:
        return "LOW_SAMPLE"
    if cards_per_start >= 0.35:
        return "HIGH"
    if cards_per_start >= 0.2:
        return "MEDIUM"
    return "LOW"


def build_markdown(metrics: dict, team: str) -> str:
    summary = metrics["team_summary"]
    lines = [
        f"# {team} Detayli Sezon Metrikleri",
        "",
        f"- Mac sayisi: {metrics['season_match_count']}",
        f"- Derece: {summary['wins']}G / {summary['draws']}B / {summary['losses']}M",
        f"- Gol: {summary['goals_for']}-{summary['goals_against']}",
        f"- Kart: {summary['cards']} toplam, mac basi {summary['cards_per_match']}",
        f"- Rakip kart ortalamasi: {summary['opponent_cards_per_match']}",
        f"- Buyuk mac sayisi: {summary['big_matches']}, buyuk maclarda BJK kart ortalamasi: {summary['big_match_cards_per_match']}",
        "",
        "## Kart Riski Yuksek Oyuncular",
        "",
    ]
    for player in metrics["top_card_risk_players"][:10]:
        lines.append(
            f"- {player['name']}: ilk 11={player['starts']}, kart={player['cards']}, "
            f"kart/ilk 11={player['cards_per_start']}, risk={player['risk_level']}, "
            f"buyuk mac kart={player['big_match_cards']}"
        )

    lines.extend(["", "## En Cok Ilk 11 Baslayanlar", ""])
    for player in metrics["most_used_players"][:10]:
        lines.append(
            f"- {player['name']}: ilk 11={player['starts']}, kadro yedek={player['bench_selections']}, "
            f"baslama payi={player['start_share']}"
        )

    lines.extend(["", "## Hakem Profilleri", ""])
    for referee, record in sorted(
        metrics["referee_profiles"].items(),
        key=lambda item: item[1]["cards_per_match"],
        reverse=True,
    )[:12]:
        lines.append(
            f"- {referee}: mac={record['matches']}, toplam kart/mac={record['cards_per_match']}, "
            f"BJK kart/mac={record['bjk_cards_per_match']}"
        )

    lines.extend(["", "## Buyuk Maclar", ""])
    for match in [item for item in metrics["match_summaries"] if item["big_match"]]:
        lines.append(
            f"- {match['date']} | {match['opponent']} | {match['score_for']}-{match['score_against']} | "
            f"kart {match['cards_for']}-{match['cards_against']} | hakem {match['main_referee']}"
        )

    return "\n".join(lines)


if __name__ == "__main__":
    main()

