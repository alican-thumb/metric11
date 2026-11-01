"""Canlı sezon tahminleri için kalibrasyon ve seçici yayın denetimi üretir.

Bu rapor yeni bir tahmin kuralı seçmez. Aynı sezon sonuçlarından türetilen eşik
taramaları yalnız tanı amaçlıdır; üretim kuralına dönüşmeden önce ileriye dönük
veya ayrılmış veri üzerinde doğrulanmalıdır.
"""
from __future__ import annotations

import json
import math
from datetime import datetime

from src.build_weekly_evaluation import build_evaluation
from src.config import PROCESSED_DIR
from src.html_utils import md_to_html, page_html

OUTPUT_JSON = PROCESSED_DIR / "prediction_calibration_audit_2026_2027.json"
OUTPUT_MD = PROCESSED_DIR / "prediction_calibration_audit_2026_2027.md"
OUTPUT_HTML = PROCESSED_DIR / "prediction_calibration_audit_2026_2027.html"

PROBABILITY_BINS = ((0.0, 0.4), (0.4, 0.45), (0.45, 0.5), (0.5, 0.6), (0.6, 1.01))
SELECTIVE_THRESHOLDS = (0.4, 0.45, 0.5, 0.55, 0.6)
DRAW_THRESHOLDS = (0.22, 0.25, 0.28, 0.3, 0.32, 0.35)


def _all_evaluations(payload: dict) -> list[dict]:
    return [match for week in payload.get("weeks", []) for match in week.get("matches", [])]


def _top_probability(row: dict) -> float:
    return max(
        float(row.get("home_win_probability") or 0),
        float(row.get("draw_probability") or 0),
        float(row.get("away_win_probability") or 0),
    )


def _wilson_interval(successes: int, total: int, z: float = 1.96) -> tuple[float | None, float | None]:
    if total == 0:
        return None, None
    p = successes / total
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    margin = z * math.sqrt((p * (1 - p) + z * z / (4 * total)) / total) / denominator
    return round(max(0.0, center - margin), 4), round(min(1.0, center + margin), 4)


def _summarize_rows(rows: list[dict]) -> dict:
    total = len(rows)
    correct = sum(1 for row in rows if row.get("correct"))
    avg_probability = sum(_top_probability(row) for row in rows) / total if total else None
    accuracy = correct / total if total else None
    low, high = _wilson_interval(correct, total)
    return {
        "matches": total,
        "correct": correct,
        "accuracy": round(accuracy, 4) if accuracy is not None else None,
        "avg_top_probability": round(avg_probability, 4) if avg_probability is not None else None,
        "calibration_gap": round(accuracy - avg_probability, 4) if total else None,
        "accuracy_ci_95": [low, high],
    }


def probability_bins(rows: list[dict]) -> list[dict]:
    output = []
    for lower, upper in PROBABILITY_BINS:
        selected = [row for row in rows if lower <= _top_probability(row) < upper]
        output.append({"lower": lower, "upper": min(upper, 1.0), **_summarize_rows(selected)})
    return output


def selective_policies(rows: list[dict]) -> list[dict]:
    total = len(rows)
    output = []
    for threshold in SELECTIVE_THRESHOLDS:
        selected = [row for row in rows if _top_probability(row) >= threshold]
        summary = _summarize_rows(selected)
        summary.update({"minimum_probability": threshold, "coverage": round(len(selected) / total, 4) if total else 0.0})
        output.append(summary)
    return output


def draw_thresholds(rows: list[dict]) -> list[dict]:
    actual_draws = sum(1 for row in rows if row.get("actual") == "draw")
    output = []
    for threshold in DRAW_THRESHOLDS:
        selected = [row for row in rows if float(row.get("draw_probability") or 0) >= threshold]
        hits = sum(1 for row in selected if row.get("actual") == "draw")
        precision = hits / len(selected) if selected else 0.0
        recall = hits / actual_draws if actual_draws else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        output.append(
            {
                "minimum_draw_probability": threshold,
                "flagged_matches": len(selected),
                "draw_hits": hits,
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "f1": round(f1, 4),
            }
        )
    return output


def confidence_policy(summary: dict) -> dict:
    bands = summary.get("confidence_breakdown", {})
    medium = bands.get("MEDIUM", {})
    high = bands.get("HIGH", {})
    draw_recall = summary.get("draw_recall") or 0.0
    medium_unreliable = (
        medium.get("matches", 0) >= 15
        and (medium.get("accuracy", 1.0) < 0.4 or medium.get("calibration_gap", 0.0) < -0.1)
    )
    high_publishable = (
        high.get("matches", 0) >= 20
        and high.get("accuracy", 0.0) >= 0.55
        and high.get("calibration_gap", -1.0) >= -0.1
    )
    return {
        "high": {
            "status": "PUBLISH" if high_publishable else "CAUTION",
            "label": "Yayınlanabilir güçlü seçim" if high_publishable else "Temkinli güçlü seçim",
        },
        "medium": {
            "status": "NO_STRONG_PICK" if medium_unreliable else "CAUTION",
            "label": "Net seçim yok / kararsız maç" if medium_unreliable else "Temkinli seçim",
        },
        "low": {"status": "NO_STRONG_PICK", "label": "Net seçim yok"},
        "draw": {
            "status": "WEAK" if draw_recall < 0.35 else "MONITOR",
            "label": "Beraberlik modeli zayıf; senaryo olarak göster" if draw_recall < 0.35 else "Beraberlik sinyalini izle",
        },
    }


def build_audit() -> dict:
    evaluation = build_evaluation()
    rows = _all_evaluations(evaluation)
    return {
        "generated_at": datetime.now().isoformat(),
        "season": evaluation.get("season"),
        "sample_size": len(rows),
        "diagnostic_only": True,
        "summary": evaluation.get("summary", {}),
        "confidence_policy": confidence_policy(evaluation.get("summary", {})),
        "probability_bins": probability_bins(rows),
        "selective_policies": selective_policies(rows),
        "draw_thresholds": draw_thresholds(rows),
        "method_note": (
            "Eşik taramaları aynı sezon sonuçlarında hesaplanır; üretim kuralı seçmek için değil, "
            "ileri dönük challenger deneyini tasarlamak için kullanılır."
        ),
    }


def _pct(value: float | None) -> str:
    return "—" if value is None else f"%{value * 100:.1f}"


def build_markdown(payload: dict) -> str:
    policy = payload["confidence_policy"]
    lines = [
        "# 2026-27 Tahmin Kalibrasyon Denetimi",
        "",
        f"- Örneklem: **{payload['sample_size']} maç**",
        f"- Yüksek güven politikası: **{policy['high']['label']}**",
        f"- Orta güven politikası: **{policy['medium']['label']}**",
        f"- Beraberlik politikası: **{policy['draw']['label']}**",
        "",
        "> Bu sayfa tanı raporudur. Aynı sezon üzerinde en iyi görünen eşik otomatik olarak üretime alınmaz.",
        "",
        "## Olasılık Kovaları",
        "",
        "| Model olasılığı | Maç | İsabet | Ortalama olasılık | Kalibrasyon farkı | %95 güven aralığı |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in payload["probability_bins"]:
        ci = row["accuracy_ci_95"]
        lines.append(
            f"| %{row['lower'] * 100:.0f}–%{row['upper'] * 100:.0f} | {row['matches']} | "
            f"{_pct(row['accuracy'])} | {_pct(row['avg_top_probability'])} | "
            f"{_pct(row['calibration_gap'])} | {_pct(ci[0])}–{_pct(ci[1])} |"
        )
    lines += [
        "",
        "## Seçici Yayın Senaryoları",
        "",
        "| Minimum olasılık | Kapsam | Maç | İsabet | %95 güven aralığı |",
        "| ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in payload["selective_policies"]:
        ci = row["accuracy_ci_95"]
        lines.append(
            f"| {_pct(row['minimum_probability'])} | {_pct(row['coverage'])} | {row['matches']} | "
            f"{_pct(row['accuracy'])} | {_pct(ci[0])}–{_pct(ci[1])} |"
        )
    lines += [
        "",
        "## Beraberlik Eşik Taraması",
        "",
        "| Minimum X olasılığı | İşaretlenen maç | Yakalanan X | Uyarı isabeti | Beraberlik yakalama | Denge puanı (F1) |",
        "| ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in payload["draw_thresholds"]:
        lines.append(
            f"| {_pct(row['minimum_draw_probability'])} | {row['flagged_matches']} | {row['draw_hits']} | "
            f"{_pct(row['precision'])} | {_pct(row['recall'])} | {row['f1']:.3f} |"
        )
    lines += ["", payload["method_note"], ""]
    return "\n".join(lines)


def build_html(payload: dict) -> str:
    return page_html(
        "Tahmin Kalibrasyon Denetimi",
        md_to_html(build_markdown(payload)),
        description="Süper Lig tahminlerinin olasılık kalibrasyonu, seçici yayın kapsamı ve beraberlik eşik denetimi.",
        active_nav="Haftalık Karne",
        canonical_path="prediction_calibration_audit_2026_2027.html",
    )


def main() -> None:
    payload = build_audit()
    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    OUTPUT_MD.write_text(build_markdown(payload), encoding="utf-8")
    OUTPUT_HTML.write_text(build_html(payload), encoding="utf-8")
    print(f"Kalibrasyon denetimi: {payload['sample_size']} maç")


if __name__ == "__main__":
    main()
