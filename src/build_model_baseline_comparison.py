from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any

from src.config import PROCESSED_DIR
from src.model_league_predictions import (
    actual_result,
    parse_tff_datetime,
    poisson_result_probs,
    predict_match,
    update_elo,
    update_history,
)
from src.normalization import normalize_matches


def main() -> None:
    parser = argparse.ArgumentParser(description="Lig tahmin modeli icin baseline karsilastirma raporu uretir.")
    parser.add_argument("--input", default=str(PROCESSED_DIR / "tff_super_lig_enriched_2025_2026.json"))
    parser.add_argument("--output-prefix", default="model_baseline_comparison_2025_2026")
    parser.add_argument("--min-team-history", type=int, default=5)
    args = parser.parse_args()

    matches = normalize_matches(json.loads(Path(args.input).read_text(encoding="utf-8")))
    matches.sort(key=lambda match: parse_tff_datetime(match["match_date"]))
    payload = build_comparison(matches, args.min_team_history)

    json_path = PROCESSED_DIR / f"{args.output_prefix}.json"
    md_path = PROCESSED_DIR / f"{args.output_prefix}.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(build_markdown(payload), encoding="utf-8")
    print(md_path.read_text(encoding="utf-8"))


def build_comparison(matches: list[dict], min_team_history: int) -> dict[str, Any]:
    team_history = defaultdict(lambda: deque(maxlen=8))
    elo = defaultdict(lambda: 1500.0)
    rows = []
    baseline_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for match in matches:
        home = match["home_team"]["name"]
        away = match["away_team"]["name"]
        home_goals = match["home_team"]["score"] or 0
        away_goals = match["away_team"]["score"] or 0
        home_history = list(team_history[home])
        away_history = list(team_history[away])

        if len(home_history) >= min_team_history and len(away_history) >= min_team_history:
            actual = actual_result(home_goals, away_goals)
            context = {
                "match_id": match["external_id"],
                "date": match["match_date"],
                "home": home,
                "away": away,
                "score": f"{home_goals}-{away_goals}",
                "actual": actual,
            }
            predictions = build_predictions(home, away, home_history, away_history, elo[home], elo[away])
            rows.append({**context, "predictions": predictions})
            for model_name, prediction in predictions.items():
                baseline_rows[model_name].append(evaluate_prediction(context, model_name, prediction))

        update_history(team_history, home, home_goals, away_goals, len(match["cards"]["home"]), is_home=True)
        update_history(team_history, away, away_goals, home_goals, len(match["cards"]["away"]), is_home=False)
        update_elo(elo, home, away, home_goals, away_goals)

    summaries = {model_name: summarize_model(items) for model_name, items in baseline_rows.items()}
    ranking = sorted(summaries.values(), key=lambda item: (item["accuracy"], -item["log_loss"]), reverse=True)
    return {
        "summary": {
            "matches": len(rows),
            "models": summaries,
            "ranking": [item["model"] for item in ranking],
            "best_accuracy_model": ranking[0]["model"] if ranking else None,
            "best_log_loss_model": min(summaries.values(), key=lambda item: item["log_loss"])["model"] if summaries else None,
            "draw_actual_count": sum(1 for row in rows if row["actual"] == "draw"),
        },
        "rows": rows,
    }


def build_predictions(
    home: str,
    away: str,
    home_history: list[dict],
    away_history: list[dict],
    home_elo: float,
    away_elo: float,
) -> dict[str, dict[str, Any]]:
    hybrid = predict_match(home, away, home_history, away_history, home_elo, away_elo)
    ppg_edge = avg(item["points"] for item in home_history) - avg(item["points"] for item in away_history)
    form_edge = avg(item["points"] for item in home_history[-5:]) - avg(item["points"] for item in away_history[-5:])
    elo_edge = home_elo + 60 - away_elo
    poisson = poisson_only_prediction(home_history, away_history)

    return {
        "always_home": fixed_prediction("home"),
        "points_per_match_edge": edge_prediction(ppg_edge, draw_band=0.18, scale=1.2),
        "recent_form_edge": edge_prediction(form_edge, draw_band=0.2, scale=1.35),
        "elo_only": edge_prediction(elo_edge / 100, draw_band=0.2, scale=1.45),
        "poisson_only": poisson,
        "current_hybrid": {
            "predicted": top_label(hybrid),
            "home_probability": hybrid["home_win_probability"],
            "draw_probability": hybrid["draw_probability"],
            "away_probability": hybrid["away_win_probability"],
        },
    }


def poisson_only_prediction(home_history: list[dict], away_history: list[dict]) -> dict[str, Any]:
    home_gf = avg(item["goals_for"] for item in home_history)
    home_ga = avg(item["goals_against"] for item in home_history)
    away_gf = avg(item["goals_for"] for item in away_history)
    away_ga = avg(item["goals_against"] for item in away_history)
    expected_home = max(0.15, home_gf * 0.58 + away_ga * 0.42 + 0.18)
    expected_away = max(0.15, away_gf * 0.58 + home_ga * 0.42)
    probs = poisson_result_probs(expected_home, expected_away)
    return {
        "predicted": max(probs, key=probs.get),
        "home_probability": round(probs["home"], 3),
        "draw_probability": round(probs["draw"], 3),
        "away_probability": round(probs["away"], 3),
        "expected_home_goals": round(expected_home, 2),
        "expected_away_goals": round(expected_away, 2),
    }


def fixed_prediction(label: str) -> dict[str, Any]:
    probs = {"home": 0.46, "draw": 0.28, "away": 0.26}
    return {
        "predicted": label,
        "home_probability": probs["home"],
        "draw_probability": probs["draw"],
        "away_probability": probs["away"],
    }


def edge_prediction(edge: float, draw_band: float, scale: float) -> dict[str, Any]:
    if abs(edge) <= draw_band:
        predicted = "draw"
    else:
        predicted = "home" if edge > 0 else "away"

    side_strength = min(0.18, abs(edge) / max(scale, 0.001) * 0.18)
    draw_probability = max(0.22, min(0.34, 0.31 - abs(edge) * 0.035))
    remaining = 1 - draw_probability
    if edge >= 0:
        home_probability = remaining / 2 + side_strength
        away_probability = remaining - home_probability
    else:
        away_probability = remaining / 2 + side_strength
        home_probability = remaining - away_probability
    probs = normalize_probs(home_probability, draw_probability, away_probability)
    return {
        "predicted": predicted,
        "home_probability": round(probs["home"], 3),
        "draw_probability": round(probs["draw"], 3),
        "away_probability": round(probs["away"], 3),
    }


def normalize_probs(home: float, draw: float, away: float) -> dict[str, float]:
    home = max(0.05, home)
    draw = max(0.05, draw)
    away = max(0.05, away)
    total = home + draw + away
    return {"home": home / total, "draw": draw / total, "away": away / total}


def top_label(prediction: dict[str, Any]) -> str:
    probs = {
        "home": prediction["home_win_probability"],
        "draw": prediction["draw_probability"],
        "away": prediction["away_win_probability"],
    }
    return max(probs, key=probs.get)


def evaluate_prediction(context: dict[str, Any], model_name: str, prediction: dict[str, Any]) -> dict[str, Any]:
    row = {
        **context,
        "model": model_name,
        "predicted": prediction["predicted"],
        "home_probability": prediction["home_probability"],
        "draw_probability": prediction["draw_probability"],
        "away_probability": prediction["away_probability"],
    }
    row["correct"] = row["predicted"] == row["actual"]
    row["brier_score"] = brier_score(row)
    row["log_loss"] = log_loss(row)
    return row


def summarize_model(rows: list[dict[str, Any]]) -> dict[str, Any]:
    correct = sum(1 for row in rows if row["correct"])
    actual_draws = sum(1 for row in rows if row["actual"] == "draw")
    predicted_draws = sum(1 for row in rows if row["predicted"] == "draw")
    correct_draws = sum(1 for row in rows if row["actual"] == "draw" and row["predicted"] == "draw")
    high_confidence_wrong = sum(
        1
        for row in rows
        if not row["correct"]
        and max(row["home_probability"], row["draw_probability"], row["away_probability"]) >= 0.52
    )
    return {
        "model": rows[0]["model"] if rows else "",
        "matches": len(rows),
        "correct": correct,
        "accuracy": round(correct / max(len(rows), 1), 3),
        "draw_recall": round(correct_draws / max(actual_draws, 1), 3),
        "draw_precision": round(correct_draws / max(predicted_draws, 1), 3),
        "predicted_distribution": dict(Counter(row["predicted"] for row in rows)),
        "actual_distribution": dict(Counter(row["actual"] for row in rows)),
        "brier_score": round(avg(row["brier_score"] for row in rows), 3),
        "log_loss": round(avg(row["log_loss"] for row in rows), 3),
        "high_confidence_wrong": high_confidence_wrong,
    }


def build_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    models = summary["models"]
    lines = [
        "# Model Baseline Karşılaştırması",
        "",
        f"- Test edilen maç: {summary['matches']}",
        f"- Gerçek beraberlik sayısı: {summary['draw_actual_count']}",
        f"- En iyi accuracy: {summary['best_accuracy_model']}",
        f"- En iyi log loss: {summary['best_log_loss_model']}",
        "",
        "## Model Tablosu",
        "",
        "| Model | Accuracy | Doğru | Draw recall | Draw precision | Brier | Log loss | Yüksek güvenli hata | Tahmin dağılımı |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for model_name in summary["ranking"]:
        item = models[model_name]
        lines.append(
            f"| {model_name} | %{round(item['accuracy'] * 100, 1)} | {item['correct']}/{item['matches']} | "
            f"%{round(item['draw_recall'] * 100, 1)} | %{round(item['draw_precision'] * 100, 1)} | "
            f"{item['brier_score']} | {item['log_loss']} | {item['high_confidence_wrong']} | {item['predicted_distribution']} |"
        )

    lines.extend(["", "## Okuma", ""])
    current = models.get("current_hybrid", {})
    always_home = models.get("always_home", {})
    best = models.get(summary["best_accuracy_model"], {})
    lines.append(
        f"- Mevcut hybrid model %{round(current.get('accuracy', 0) * 100, 1)} accuracy ile "
        f"basit ev sahibi baseline'ının %{round(always_home.get('accuracy', 0) * 100, 1)} seviyesine karşı ölçüldü."
    )
    lines.append(
        f"- En yüksek accuracy {summary['best_accuracy_model']} modelinde: %{round(best.get('accuracy', 0) * 100, 1)}."
    )
    lines.append(
        "- Draw recall düşük kalan modeller beraberlikleri ana tahmine çevirmeden risk etiketi olarak güçlendirmeli."
    )

    lines.extend(["", "## Son 30 Maç Karşılaştırması", ""])
    labels = {"home": "Ev", "draw": "X", "away": "Dep"}
    for row in payload["rows"][-30:]:
        preds = row["predictions"]
        compact = ", ".join(
            f"{name}={labels[prediction['predicted']]}"
            for name, prediction in preds.items()
        )
        lines.append(
            f"- {row['date']} | {row['home']} - {row['away']} | skor {row['score']} | "
            f"gerçek={labels[row['actual']]} | {compact}"
        )
    return "\n".join(lines)


def brier_score(row: dict[str, Any]) -> float:
    probs = {
        "home": row["home_probability"],
        "draw": row["draw_probability"],
        "away": row["away_probability"],
    }
    return sum((probs[key] - (1 if row["actual"] == key else 0)) ** 2 for key in probs)


def log_loss(row: dict[str, Any]) -> float:
    probs = {
        "home": row["home_probability"],
        "draw": row["draw_probability"],
        "away": row["away_probability"],
    }
    probability = max(0.001, min(0.999, probs[row["actual"]]))
    return -math.log(probability)


def avg(values) -> float:
    values = list(values)
    return sum(values) / len(values) if values else 0.0


if __name__ == "__main__":
    main()
