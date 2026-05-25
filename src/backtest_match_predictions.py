from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.config import PROCESSED_DIR


def main() -> None:
    parser = argparse.ArgumentParser(description="Mac sonucu preview sinyalleri icin basit backtest uretir.")
    parser.add_argument("--index", default=str(PROCESSED_DIR / "previews_besiktas_2025_2026_chronological" / "index.json"))
    parser.add_argument("--output-prefix", default="match_prediction_backtest_2025_2026")
    args = parser.parse_args()

    index_payload = json.loads(Path(args.index).read_text(encoding="utf-8"))
    rows = []
    for report in index_payload["reports"]:
        home_score, away_score = [int(part) for part in report["actual_score"].split("-")]
        target_side = "home" if report["home_team"] == "BEŞİKTAŞ A.Ş." else "away"
        target_score = home_score if target_side == "home" else away_score
        opponent_score = away_score if target_side == "home" else home_score
        actual = "target_win" if target_score > opponent_score else "draw" if target_score == opponent_score else "opponent_win"
        probabilities = {
            "target_win": report["target_win_probability"],
            "draw": report["draw_probability"],
            "opponent_win": report["opponent_win_probability"],
        }
        raw_predicted = max(probabilities, key=probabilities.get)
        predicted = report.get("final_prediction") or raw_predicted
        action = report.get("recommended_action") or "unknown"
        rows.append(
            {
                "match_id": report["match_id"],
                "fixture": f"{report['home_team']} - {report['away_team']}",
                "date": report["date"],
                "actual_score": report["actual_score"],
                "raw_predicted": raw_predicted,
                "predicted": predicted,
                "actual": actual,
                "correct": predicted == actual,
                "raw_correct": raw_predicted == actual,
                "recommended_action": action,
                "prediction_adjustment": report.get("prediction_adjustment") or "none",
                "actionable": action == "taraf_eğilimi",
                "confidence_probability": probabilities[predicted],
                "card_signal": report["card_signal"],
                "is_big_match": report["is_big_match"],
            }
        )

    correct = sum(1 for row in rows if row["correct"])
    raw_correct = sum(1 for row in rows if row["raw_correct"])
    big = [row for row in rows if row["is_big_match"]]
    actionable = [row for row in rows if row["actionable"]]
    summary = {
        "report_count": len(rows),
        "raw_correct": raw_correct,
        "raw_accuracy": round(raw_correct / len(rows), 3) if rows else 0,
        "correct": correct,
        "accuracy": round(correct / len(rows), 3) if rows else 0,
        "actionable_count": len(actionable),
        "actionable_correct": sum(1 for row in actionable if row["correct"]),
        "actionable_accuracy": round(sum(1 for row in actionable if row["correct"]) / len(actionable), 3) if actionable else 0,
        "big_match_count": len(big),
        "big_match_correct": sum(1 for row in big if row["correct"]),
        "big_match_accuracy": round(sum(1 for row in big if row["correct"]) / len(big), 3) if big else 0,
    }
    payload = {"summary": summary, "rows": rows}
    json_path = PROCESSED_DIR / f"{args.output_prefix}.json"
    md_path = PROCESSED_DIR / f"{args.output_prefix}.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(build_markdown(payload), encoding="utf-8")
    print(md_path.read_text(encoding="utf-8"))


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    labels = {"target_win": "BJK", "draw": "X", "opponent_win": "Rakip"}
    lines = [
        "# Maç Sonucu Backtest Raporu",
        "",
        f"- Rapor sayısı: {summary['report_count']}",
        f"- Ekran tahmini doğru: {summary['correct']} (%{round(summary['accuracy'] * 100)})",
        f"- Ham olasılık doğru: {summary['raw_correct']} (%{round(summary['raw_accuracy'] * 100)})",
        f"- Taraf eğilimi verilen maç: {summary['actionable_correct']}/{summary['actionable_count']} (%{round(summary['actionable_accuracy'] * 100)})",
        f"- Büyük maç doğruluk: {summary['big_match_correct']}/{summary['big_match_count']} (%{round(summary['big_match_accuracy'] * 100)})",
        "",
        "## Maç Bazlı",
        "",
    ]
    for row in payload["rows"]:
        lines.append(
            f"- {row['date']} | {row['fixture']} | skor {row['actual_score']} | "
            f"ekran={labels[row['predicted']]} ham={labels[row['raw_predicted']]} gerçek={labels[row['actual']]} | "
            f"ayar={row['prediction_adjustment']} | aksiyon={row['recommended_action']} | doğru={row['correct']}"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    main()
