from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from src.config import PROCESSED_DIR


def main() -> None:
    parser = argparse.ArgumentParser(description="Lig tahminleri icin beraberlik risk denetimi uretir.")
    parser.add_argument("--input", default=str(PROCESSED_DIR / "league_prediction_model_2025_2026.json"))
    parser.add_argument("--output-prefix", default="draw_risk_audit_2025_2026")
    args = parser.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    audit = build_audit(payload.get("rows", []))

    json_path = PROCESSED_DIR / f"{args.output_prefix}.json"
    md_path = PROCESSED_DIR / f"{args.output_prefix}.md"
    json_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(build_markdown(audit), encoding="utf-8")
    print(md_path.read_text(encoding="utf-8"))


def build_audit(rows: list[dict[str, Any]]) -> dict[str, Any]:
    scored = [score_row(row) for row in rows]
    actual_draws = [row for row in scored if row["actual"] == "draw"]
    medium_plus = [row for row in scored if row["draw_risk_level"] in {"MEDIUM", "HIGH"}]
    high = [row for row in scored if row["draw_risk_level"] == "HIGH"]
    missed_draws = [row for row in actual_draws if row["draw_risk_level"] == "LOW"]

    return {
        "summary": {
            "matches": len(scored),
            "actual_draws": len(actual_draws),
            "actual_draw_rate": pct(len(actual_draws), len(scored)),
            "medium_plus_flags": len(medium_plus),
            "medium_plus_draw_hits": count_draws(medium_plus),
            "medium_plus_recall": pct(count_draws(medium_plus), len(actual_draws)),
            "medium_plus_precision": pct(count_draws(medium_plus), len(medium_plus)),
            "high_flags": len(high),
            "high_draw_hits": count_draws(high),
            "high_recall": pct(count_draws(high), len(actual_draws)),
            "high_precision": pct(count_draws(high), len(high)),
            "missed_draws_after_risk": len(missed_draws),
            "risk_distribution": dict(Counter(row["draw_risk_level"] for row in scored)),
            "action_distribution": dict(Counter(row["recommended_model_action"] for row in scored)),
        },
        "rows": scored,
        "high_risk_matches": high,
        "missed_draws": missed_draws,
        "top_false_alarms": [
            row for row in sorted(medium_plus, key=lambda item: item["draw_risk_score"], reverse=True) if row["actual"] != "draw"
        ][:20],
    }


def score_row(row: dict[str, Any]) -> dict[str, Any]:
    score = 0
    reasons: list[str] = []
    draw_probability = row.get("draw_probability", 0) or 0
    xg_margin = abs((row.get("expected_home_goals") or 0) - (row.get("expected_away_goals") or 0))
    probabilities = sorted(
        [
            row.get("home_win_probability", 0) or 0,
            row.get("draw_probability", 0) or 0,
            row.get("away_win_probability", 0) or 0,
        ],
        reverse=True,
    )
    probability_margin = probabilities[0] - probabilities[1] if len(probabilities) >= 2 else 0
    side_probability = max(row.get("home_win_probability", 0) or 0, row.get("away_win_probability", 0) or 0)
    strength_edge = abs(row.get("strength_edge", 0) or 0)

    if draw_probability >= 0.28:
        score += 24
        reasons.append("draw_probability_high")
    elif draw_probability >= 0.265:
        score += 18
        reasons.append("draw_probability_live")
    elif draw_probability >= 0.25:
        score += 10
        reasons.append("draw_probability_watch")

    if xg_margin < 0.15:
        score += 24
        reasons.append("xg_margin_very_narrow")
    elif xg_margin < 0.30:
        score += 17
        reasons.append("xg_margin_narrow")
    elif xg_margin < 0.50:
        score += 9
        reasons.append("xg_margin_watch")

    scoreline_reason = draw_scoreline_reason(row)
    if scoreline_reason == "top_draw_scoreline":
        score += 16
        reasons.append(scoreline_reason)
    elif scoreline_reason == "draw_scoreline_top_two":
        score += 9
        reasons.append(scoreline_reason)

    if probability_margin < 0.06:
        score += 20
        reasons.append("probability_margin_very_narrow")
    elif probability_margin < 0.12:
        score += 12
        reasons.append("probability_margin_narrow")
    elif probability_margin < 0.18:
        score += 6
        reasons.append("probability_margin_watch")

    if strength_edge < 0.12:
        score += 10
        reasons.append("strength_edge_very_narrow")
    elif strength_edge < 0.25:
        score += 6
        reasons.append("strength_edge_narrow")

    if row.get("confidence") == "LOW":
        score += 10
        reasons.append("low_confidence_side_pick")
    elif row.get("confidence") == "MEDIUM":
        score += 5
        reasons.append("medium_confidence_side_pick")

    flags = set(row.get("risk_flags", []))
    if "beraberlik olasılığı canlı" in flags:
        score += 6
        reasons.append("existing_draw_flag")
    if "xG farkı dar" in flags:
        score += 5
        reasons.append("existing_narrow_xg_flag")
    if "favori xG israfı" in flags:
        score += 10
        reasons.append("favori_xg_wasteful")
    if side_probability >= 0.52:
        score -= 10
        reasons.append("strong_side_probability_penalty")

    score = max(0, min(100, score))
    level = risk_level(score)
    return {
        **row,
        "draw_risk_score": score,
        "draw_risk_level": level,
        "draw_risk_reasons": reasons,
        "protected_prediction": level in {"MEDIUM", "HIGH"},
        "recommended_model_action": recommended_action(level),
    }


def draw_scoreline_reason(row: dict[str, Any]) -> str | None:
    recommended = row.get("recommended_scoreline") or {}
    if is_draw_scoreline(recommended):
        return "top_draw_scoreline"
    for scoreline in (row.get("top_scorelines") or [])[:2]:
        if is_draw_scoreline(scoreline):
            return "draw_scoreline_top_two"
    return None


def is_draw_scoreline(scoreline: dict[str, Any]) -> bool:
    if not scoreline:
        return False
    if "home_goals" in scoreline and "away_goals" in scoreline:
        return scoreline["home_goals"] == scoreline["away_goals"]
    value = scoreline.get("score")
    if not value or "-" not in value:
        return False
    left, right = value.split("-", 1)
    return left == right


def risk_level(score: int) -> str:
    if score >= 35:
        return "HIGH"
    if score >= 25:
        return "MEDIUM"
    return "LOW"


def recommended_action(level: str) -> str:
    if level == "HIGH":
        return "PROTECT_SIDE_PICK_SHOW_DRAW_SCENARIO"
    if level == "MEDIUM":
        return "KEEP_PICK_WITH_DRAW_WARNING"
    return "KEEP_MAIN_PICK"


def count_draws(rows: list[dict[str, Any]]) -> int:
    return sum(1 for row in rows if row.get("actual") == "draw")


def pct(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 3) if denominator else 0


def build_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Beraberlik Risk Denetimi",
        "",
        f"- Test edilen maç: {summary['matches']}",
        f"- Gerçek beraberlik: {summary['actual_draws']} (%{round(summary['actual_draw_rate'] * 100, 1)})",
        f"- MEDIUM/HIGH risk bayrağı: {summary['medium_plus_flags']}",
        f"- MEDIUM/HIGH beraberlik yakalama: {summary['medium_plus_draw_hits']}/{summary['actual_draws']} (%{round(summary['medium_plus_recall'] * 100, 1)} recall, %{round(summary['medium_plus_precision'] * 100, 1)} precision)",
        f"- HIGH risk beraberlik yakalama: {summary['high_draw_hits']}/{summary['actual_draws']} (%{round(summary['high_recall'] * 100, 1)} recall, %{round(summary['high_precision'] * 100, 1)} precision)",
        f"- Risk sonrası kaçan beraberlik: {summary['missed_draws_after_risk']}",
        f"- Risk dağılımı: {summary['risk_distribution']}",
        f"- Aksiyon dağılımı: {summary['action_distribution']}",
        "",
        "## Okuma",
        "",
        "- Bu katman ana 1X2 tahmini değiştirmez; taraf tahminini korumaya alır ve beraberlik senaryosunu görünür yapar.",
        "- Precision gerçek beraberlik baz oranının üstündeyse risk etiketi ürün dili için değerlidir; kesin X tahmini olarak kullanılmamalıdır.",
        "- MEDIUM/HIGH bayraklı maçlarda UI tarafında skor senaryoları ve güven dili daha temkinli gösterilmeli.",
        "",
        "## HIGH Risk Maçlar",
        "",
    ]
    labels = {"home": "Ev", "draw": "X", "away": "Dep"}
    for row in payload["high_risk_matches"][:30]:
        lines.append(
            f"- {row['date']} | {row['home']} - {row['away']} | skor {row['score']} | "
            f"tahmin={labels[row['predicted']]} gerçek={labels[row['actual']]} | "
            f"risk={row['draw_risk_score']} | neden={', '.join(row['draw_risk_reasons'][:4])}"
        )

    lines.extend(["", "## Hâlâ Kaçan Beraberlikler", ""])
    for row in payload["missed_draws"][:30]:
        lines.append(
            f"- {row['date']} | {row['home']} - {row['away']} | skor {row['score']} | "
            f"tahmin={labels[row['predicted']]} | risk={row['draw_risk_score']} | "
            f"xG={row['expected_home_goals']}-{row['expected_away_goals']} | draw_p={row['draw_probability']}"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    main()
