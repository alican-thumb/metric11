from __future__ import annotations

import json
import argparse
from collections import Counter, defaultdict
from pathlib import Path

from src.config import PROCESSED_DIR


def main() -> None:
    parser = argparse.ArgumentParser(description="TFF parse edilmis mac JSON dosyasindan metrik uretir.")
    parser.add_argument("--input", default=str(PROCESSED_DIR / "tff_matches.json"))
    parser.add_argument("--output-prefix", default="tff_sample_metrics")
    args = parser.parse_args()

    source_path = Path(args.input)
    if not source_path.exists():
        raise SystemExit(f"{source_path} bulunamadi. Once veri toplama scriptini calistir.")

    matches = json.loads(source_path.read_text(encoding="utf-8"))
    card_counter = Counter()
    player_card_counter = Counter()
    referee_cards = defaultdict(lambda: {"matches": 0, "cards": 0})
    team_records = defaultdict(lambda: {"matches": 0, "goals_for": 0, "goals_against": 0, "cards": 0})

    for match in matches:
        home = match["home_team"]["name"]
        away = match["away_team"]["name"]
        home_score = match["home_team"]["score"] or 0
        away_score = match["away_team"]["score"] or 0
        home_cards = len(match["cards"]["home"])
        away_cards = len(match["cards"]["away"])
        total_cards = home_cards + away_cards

        team_records[home]["matches"] += 1
        team_records[home]["goals_for"] += home_score
        team_records[home]["goals_against"] += away_score
        team_records[home]["cards"] += home_cards

        team_records[away]["matches"] += 1
        team_records[away]["goals_for"] += away_score
        team_records[away]["goals_against"] += home_score
        team_records[away]["cards"] += away_cards

        card_counter["total_cards"] += total_cards
        card_counter["matches"] += 1

        main_referee = next((official for official in match["officials"] if official["role"] == "Hakem"), None)
        if main_referee:
            referee_cards[main_referee["name"]]["matches"] += 1
            referee_cards[main_referee["name"]]["cards"] += total_cards

        for side in ("home", "away"):
            for card in match["cards"][side]:
                if card["player_name"]:
                    player_card_counter[card["player_name"]] += 1

    metrics = {
        "match_count": len(matches),
        "cards_per_match": round(card_counter["total_cards"] / card_counter["matches"], 2)
        if card_counter["matches"]
        else 0,
        "team_records": {
            team: {
                **record,
                "goals_for_per_match": round(record["goals_for"] / record["matches"], 2),
                "goals_against_per_match": round(record["goals_against"] / record["matches"], 2),
                "cards_per_match": round(record["cards"] / record["matches"], 2),
            }
            for team, record in sorted(team_records.items())
        },
        "referee_cards": {
            referee: {
                **record,
                "cards_per_match": round(record["cards"] / record["matches"], 2),
            }
            for referee, record in sorted(referee_cards.items())
        },
        "top_carded_players": player_card_counter.most_common(10),
    }

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    json_path = PROCESSED_DIR / f"{args.output_prefix}.json"
    md_path = PROCESSED_DIR / f"{args.output_prefix}.md"
    json_path.write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    md_path.write_text(build_markdown(metrics), encoding="utf-8")
    print(build_markdown(metrics))


def build_markdown(metrics: dict) -> str:
    lines = [
        "# TFF Ornek Veri Metrikleri",
        "",
        f"- Mac sayisi: {metrics['match_count']}",
        f"- Mac basi kart: {metrics['cards_per_match']}",
        "",
        "## Takim Ozetleri",
        "",
    ]
    for team, record in metrics["team_records"].items():
        lines.append(
            f"- {team}: mac={record['matches']}, gol={record['goals_for']}-{record['goals_against']}, "
            f"mac basi kart={record['cards_per_match']}"
        )

    lines.extend(["", "## Hakem Kart Profili", ""])
    for referee, record in metrics["referee_cards"].items():
        lines.append(f"- {referee}: mac={record['matches']}, mac basi kart={record['cards_per_match']}")

    lines.extend(["", "## En Cok Kart Goren Oyuncular", ""])
    for player, count in metrics["top_carded_players"]:
        lines.append(f"- {player}: {count}")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
