from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from src.config import PROCESSED_DIR
from src.html_utils import md_to_html, page_html


def main() -> None:
    parser = argparse.ArgumentParser(description="Besiktas buyuk mac/derbi tahmin denetim raporu uretir.")
    parser.add_argument(
        "--preview-dir",
        default=str(PROCESSED_DIR / "previews_besiktas_2025_2026_chronological"),
    )
    parser.add_argument("--output-prefix", default="big_match_report_2025_2026")
    args = parser.parse_args()

    payload = build_report(Path(args.preview_dir))
    json_path = PROCESSED_DIR / f"{args.output_prefix}.json"
    md_path = PROCESSED_DIR / f"{args.output_prefix}.md"
    md = build_markdown(payload)
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(md, encoding="utf-8")
    html_path = PROCESSED_DIR / f"{args.output_prefix}.html"
    html_path.write_text(page_html("Büyük Maç Denetim Raporu (2025-26 Arşiv)", md_to_html(md), description="Süper Lig derbi ve büyük maçlarında beraberlik riski, gol adayı kalitesi ve taraf tahmin tutarlılığı — tamamlanmış 2025-26 sezonu, Beşiktaş maçları — metric11.", canonical_path=html_path.name), encoding="utf-8")
    print(md)


def build_report(preview_dir: Path) -> dict:
    rows = []
    risk_counter = Counter()
    miss_counter = Counter()
    for path in sorted(preview_dir.glob("week_*.json")):
        preview = json.loads(path.read_text(encoding="utf-8"))
        match = preview["match"]
        if not match.get("is_big_match"):
            continue

        home_score, away_score = [int(part) for part in match["actual_score"].split("-")]
        target_side = match["home_away"]
        target_score = home_score if target_side == "home" else away_score
        opponent_score = away_score if target_side == "home" else home_score
        actual = "target_win" if target_score > opponent_score else "draw" if target_score == opponent_score else "opponent_win"
        probabilities = preview["probabilities"]
        probability_map = {
            "target_win": probabilities["target_win_probability"],
            "draw": probabilities["draw_probability"],
            "opponent_win": probabilities["opponent_win_probability"],
        }
        predicted = max(probability_map, key=probability_map.get)
        correct = predicted == actual
        profile = probabilities.get("big_match_profile", {})
        draw_signal = probabilities.get("draw_calibration", {})
        risk_counter[profile.get("risk_level", "UNKNOWN")] += 1
        if not correct:
            if actual == "draw":
                miss_counter["missed_draw"] += 1
            elif predicted == "target_win":
                miss_counter["overrated_besiktas"] += 1
            elif predicted == "opponent_win":
                miss_counter["overrated_opponent"] += 1

        rows.append(
            {
                "match_id": match["match_id"],
                "date": match["date"],
                "fixture": f"{match['home_team']} - {match['away_team']}",
                "actual_score": match["actual_score"],
                "predicted": predicted,
                "actual": actual,
                "correct": correct,
                "target_win_probability": probability_map["target_win"],
                "draw_probability": probability_map["draw"],
                "opponent_win_probability": probability_map["opponent_win"],
                "recommended_action": probabilities.get("recommended_call", {}).get("action"),
                "card_signal": probabilities.get("card_signal"),
                "big_match_risk": profile.get("risk_level"),
                "big_match_volatility": profile.get("volatility_score"),
                "big_match_adjustment": profile.get("adjustment"),
                "big_match_notes": profile.get("notes", []),
                "draw_risk": draw_signal.get("risk_level"),
                "draw_reasons": draw_signal.get("reasons", []),
                "top_goal_candidates": [
                    {
                        "name": candidate["name"],
                        "score": candidate.get("goal_candidate_score", candidate.get("goal_threat_score")),
                        "type": candidate.get("candidate_type"),
                    }
                    for candidate in preview.get("goal_candidates", {}).get("candidates", [])[:8]
                ],
            }
        )

    correct_count = sum(1 for row in rows if row["correct"])
    high_or_medium = sum(1 for row in rows if row["big_match_risk"] in {"HIGH", "MEDIUM"})
    summary = {
        "big_match_count": len(rows),
        "correct": correct_count,
        "accuracy": round(correct_count / len(rows), 3) if rows else 0,
        "high_or_medium_risk_count": high_or_medium,
        "risk_distribution": dict(risk_counter),
        "miss_distribution": dict(miss_counter),
        "key_learning": (
            "Büyük maçlar normal maç gibi okunmamalı; model taraf tahmini verse bile beraberlik, kart ve düşük fark senaryosu "
            "ayrı risk katmanı olarak gösterilmeli."
        ),
    }
    return {"summary": summary, "rows": rows}


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    labels = {"target_win": "BJK", "draw": "X", "opponent_win": "Rakip"}
    lines = [
        "# Büyük Maç / Derbi Denetim Raporu (2025-26 Arşiv, Beşiktaş)",
        "",
        f"- Büyük maç sayısı: {summary['big_match_count']}",
        f"- Doğru tahmin: {summary['correct']} (%{round(summary['accuracy'] * 100)})",
        f"- MEDIUM/HIGH risk işaretlenen maç: {summary['high_or_medium_risk_count']}",
        f"- Risk dağılımı: {summary['risk_distribution']}",
        f"- Hata dağılımı: {summary['miss_distribution']}",
        f"- Öğrenim: {summary['key_learning']}",
        "",
        "## Maçlar",
        "",
    ]
    for row in payload["rows"]:
        candidates = ", ".join(candidate["name"] for candidate in row["top_goal_candidates"][:5])
        lines.extend(
            [
                f"### {row['date']} | {row['fixture']}",
                "",
                f"- Skor: {row['actual_score']} | tahmin={labels[row['predicted']]} gerçek={labels[row['actual']]} | doğru={row['correct']}",
                f"- Olasılıklar: BJK %{round(row['target_win_probability'] * 100)}, X %{round(row['draw_probability'] * 100)}, Rakip %{round(row['opponent_win_probability'] * 100)}",
                f"- Büyük maç profili: {row['big_match_risk']} ({row['big_match_adjustment']})",
                f"- Beraberlik riski: {row['draw_risk']} | Kart sinyali: {row['card_signal']}",
                f"- Gol adayları: {candidates}",
                "",
            ]
        )
    return "\n".join(lines)


if __name__ == "__main__":
    main()
