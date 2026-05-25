from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from src.config import PROCESSED_DIR


PROTECTED_ACTIONS = {
    "PROTECT_SIDE_PICK_SHOW_DRAW_SCENARIO",
    "KEEP_PICK_WITH_DRAW_WARNING",
}

ACTION_LABELS = {
    "PROTECT_SIDE_PICK_SHOW_DRAW_SCENARIO": "Korumalı taraf tahmini",
    "KEEP_PICK_WITH_DRAW_WARNING": "Beraberlik uyarılı tahmin",
    "KEEP_MAIN_PICK": "Ana tahmini koru",
    "taraf_eğilimi": "Taraf eğilimi",
    "unknown": "Bilinmiyor",
}

RESULT_LABELS = {
    "target_win": "Beşiktaş",
    "draw": "Beraberlik",
    "opponent_win": "Rakip",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Korumali tahmin aksiyonlarinin backtest etkisini denetler.")
    parser.add_argument(
        "--index",
        default=str(PROCESSED_DIR / "previews_besiktas_2025_2026_chronological" / "index.json"),
    )
    parser.add_argument(
        "--backtest",
        default=str(PROCESSED_DIR / "match_prediction_backtest_2025_2026.json"),
    )
    parser.add_argument("--output-prefix", default="protected_action_audit_2025_2026")
    args = parser.parse_args()

    index_payload = json.loads(Path(args.index).read_text(encoding="utf-8"))
    backtest_payload = json.loads(Path(args.backtest).read_text(encoding="utf-8"))
    audit = build_audit(index_payload.get("reports", []), backtest_payload.get("rows", []))

    json_path = PROCESSED_DIR / f"{args.output_prefix}.json"
    md_path = PROCESSED_DIR / f"{args.output_prefix}.md"
    json_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(build_markdown(audit), encoding="utf-8")
    print(md_path.read_text(encoding="utf-8"))


def build_audit(index_reports: list[dict[str, Any]], backtest_rows: list[dict[str, Any]]) -> dict[str, Any]:
    backtest_by_match = {str(row["match_id"]): row for row in backtest_rows}
    rows = []
    for report in index_reports:
        match_id = str(report["match_id"])
        backtest = backtest_by_match.get(match_id)
        if not backtest:
            continue

        preview_payload = load_preview_json(report.get("json_path"))
        probabilities = preview_payload.get("probabilities", {}) if preview_payload else {}
        draw_risk = probabilities.get("draw_risk", {})
        recommended_call = probabilities.get("recommended_call", {})
        action = (
            draw_risk.get("recommended_model_action")
            or recommended_call.get("action")
            or report.get("recommended_action")
            or backtest.get("recommended_action")
            or "unknown"
        )
        predicted = backtest["predicted"]
        actual = backtest["actual"]
        protected = action in PROTECTED_ACTIONS
        actual_draw = actual == "draw"
        side_pick_correct = predicted == actual and actual != "draw"
        side_pick_wrong = predicted != actual and actual != "draw"
        draw_risk_reasons = draw_risk.get("reasons", [])

        rows.append(
            {
                "match_id": match_id,
                "week": report.get("week"),
                "date": report["date"],
                "fixture": f"{report['home_team']} - {report['away_team']}",
                "actual_score": report["actual_score"],
                "predicted": predicted,
                "actual": actual,
                "correct": backtest["correct"],
                "action": action,
                "action_label": action_label(action),
                "protected": protected,
                "actual_draw": actual_draw,
                "side_pick_correct": side_pick_correct,
                "side_pick_wrong": side_pick_wrong,
                "draw_probability": report.get("draw_probability"),
                "confidence_probability": backtest.get("confidence_probability"),
                "confidence": report.get("confidence"),
                "is_big_match": report.get("is_big_match", False),
                "draw_risk_score": draw_risk.get("score"),
                "draw_risk_level": draw_risk.get("risk_level"),
                "draw_risk_reasons": draw_risk_reasons,
                "failure_tags": failure_tags(
                    predicted=predicted,
                    actual=actual,
                    is_big_match=report.get("is_big_match", False),
                    draw_risk_level=draw_risk.get("risk_level"),
                    draw_risk_reasons=draw_risk_reasons,
                    side_pick_wrong=side_pick_wrong,
                ),
            }
        )

    protected_rows = [row for row in rows if row["protected"]]
    unprotected_rows = [row for row in rows if not row["protected"]]
    protected_draws = [row for row in protected_rows if row["actual_draw"]]
    protected_side_correct = [row for row in protected_rows if row["side_pick_correct"]]
    protected_side_wrong = [row for row in protected_rows if row["side_pick_wrong"]]
    high_risk = [row for row in protected_rows if row.get("draw_risk_level") == "HIGH"]
    side_wrong_tag_counts = Counter(tag for row in protected_side_wrong for tag in row["failure_tags"])

    return {
        "summary": {
            "matches": len(rows),
            "protected_count": len(protected_rows),
            "protected_share": pct(len(protected_rows), len(rows)),
            "protected_draw_hits": len(protected_draws),
            "protected_draw_precision": pct(len(protected_draws), len(protected_rows)),
            "protected_side_correct": len(protected_side_correct),
            "protected_side_wrong": len(protected_side_wrong),
            "protected_side_correct_rate": pct(len(protected_side_correct), len(protected_rows)),
            "unprotected_accuracy": pct(sum(1 for row in unprotected_rows if row["correct"]), len(unprotected_rows)),
            "high_risk_count": len(high_risk),
            "high_risk_draw_hits": sum(1 for row in high_risk if row["actual_draw"]),
            "action_distribution": dict(Counter(row["action"] for row in rows)),
            "protected_actual_distribution": dict(Counter(row["actual"] for row in protected_rows)),
            "protected_side_wrong_tag_counts": dict(side_wrong_tag_counts),
        },
        "rows": rows,
        "protected_rows": protected_rows,
        "protected_draws": protected_draws,
        "protected_side_wrong": protected_side_wrong,
    }


def failure_tags(
    *,
    predicted: str,
    actual: str,
    is_big_match: bool,
    draw_risk_level: str | None,
    draw_risk_reasons: list[str],
    side_pick_wrong: bool,
) -> list[str]:
    if not side_pick_wrong:
        return []
    tags: list[str] = []
    if predicted == "target_win" and actual == "opponent_win":
        tags.append("target_side_overrated")
    elif predicted == "opponent_win" and actual == "target_win":
        tags.append("opponent_side_overrated")
    if is_big_match:
        tags.append("big_match_side_flip")
    if draw_risk_level == "HIGH":
        tags.append("high_draw_risk_but_decisive_result")
    if "xg_margin_very_narrow" in draw_risk_reasons or "xg_margin_narrow" in draw_risk_reasons:
        tags.append("narrow_xg_decisive_result")
    if "low_confidence_side_pick" in draw_risk_reasons:
        tags.append("low_confidence_wrong_side")
    return tags or ["unclassified_side_flip"]


def load_preview_json(path_value: str | None) -> dict[str, Any]:
    if not path_value:
        return {}
    path = Path(path_value)
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def action_label(action: str) -> str:
    return ACTION_LABELS.get(action, action)


def pct(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 3) if denominator else 0


def build_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Korumalı Tahmin Aksiyonu Denetimi",
        "",
        f"- Test edilen Beşiktaş maçı: {summary['matches']}",
        f"- Korumalı aksiyon verilen maç: {summary['protected_count']} (%{round(summary['protected_share'] * 100, 1)})",
        f"- Korumalı aksiyonda gerçek beraberlik: {summary['protected_draw_hits']}/{summary['protected_count']} (%{round(summary['protected_draw_precision'] * 100, 1)})",
        f"- Korumalı aksiyonda taraf tahmini doğru kalan maç: {summary['protected_side_correct']}/{summary['protected_count']} (%{round(summary['protected_side_correct_rate'] * 100, 1)})",
        f"- Korumalı aksiyonda taraf tahmini yanlış/beraberlik dışı maç: {summary['protected_side_wrong']}",
        f"- HIGH risk korumalı maç: {summary['high_risk_count']} | gerçek beraberlik: {summary['high_risk_draw_hits']}",
        f"- Aksiyon dağılımı: {summary['action_distribution']}",
        f"- Korumalı aksiyon gerçek sonuç dağılımı: {summary['protected_actual_distribution']}",
        f"- Beraberlik dışı yanlış taraf etiketleri: {summary['protected_side_wrong_tag_counts']}",
        "",
        "## Okuma",
        "",
        "- Bu rapor ana 1X2 doğruluğunu yeniden skorlamaz; aksiyon katmanının kullanıcıya ne kadar temkinli dil kazandırdığını ölçer.",
        "- Korumalı aksiyonun amacı beraberliği kesin tahmin etmek değil, taraf tahmininde beraberlik senaryosunu görünür yapmaktır.",
        "- Beraberlik dışı yanlışlar, yeni veri ihtiyacını gösterir: odds, sakatlık, kadro değeri, oyun akışı ve derbi tempo verisi.",
        "",
        "## Korumalı Aksiyon Verilen Maçlar",
        "",
    ]
    for row in payload["protected_rows"]:
        reasons = ", ".join(row.get("draw_risk_reasons") or []) or "-"
        lines.append(
            f"- Hafta {row['week']} | {row['date']} | {row['fixture']} | skor {row['actual_score']} | "
            f"tahmin={RESULT_LABELS[row['predicted']]} gerçek={RESULT_LABELS[row['actual']]} | "
            f"aksiyon={row['action_label']} | risk={row.get('draw_risk_level') or '-'} "
            f"{row.get('draw_risk_score') or '-'} | neden={reasons}"
        )
    if payload["protected_side_wrong"]:
        lines.extend(
            [
                "",
                "## Beraberlik Dışı Yanlış Taraf Vakaları",
                "",
            ]
        )
        for row in payload["protected_side_wrong"]:
            tags = ", ".join(row["failure_tags"]) or "-"
            lines.append(
                f"- Hafta {row['week']} | {row['fixture']} | skor {row['actual_score']} | "
                f"tahmin={RESULT_LABELS[row['predicted']]} gerçek={RESULT_LABELS[row['actual']]} | "
                f"risk={row.get('draw_risk_level') or '-'} {row.get('draw_risk_score') or '-'} | etiket={tags}"
            )
    return "\n".join(lines)


if __name__ == "__main__":
    main()
