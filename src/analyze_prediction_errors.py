from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from src.config import PROCESSED_DIR


def main() -> None:
    parser = argparse.ArgumentParser(description="Tahmin ve gol adayi hatalarini urun/model gelistirme raporuna cevirir.")
    parser.add_argument("--match-backtest", default=str(PROCESSED_DIR / "match_prediction_backtest_2025_2026.json"))
    parser.add_argument("--goal-backtest", default=str(PROCESSED_DIR / "goal_candidate_backtest_2025_2026.json"))
    parser.add_argument("--preview-index", default=str(PROCESSED_DIR / "previews_besiktas_2025_2026_chronological" / "index.json"))
    parser.add_argument("--output-prefix", default="prediction_error_analysis_2025_2026")
    args = parser.parse_args()

    match_backtest = load_json(Path(args.match_backtest), {})
    goal_backtest = load_json(Path(args.goal_backtest), {})
    preview_index = load_json(Path(args.preview_index), {})
    payload = build_payload(match_backtest, goal_backtest, preview_index)

    json_path = PROCESSED_DIR / f"{args.output_prefix}.json"
    md_path = PROCESSED_DIR / f"{args.output_prefix}.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(build_markdown(payload), encoding="utf-8")
    print(md_path.read_text(encoding="utf-8"))


def build_payload(match_backtest: dict, goal_backtest: dict, preview_index: dict) -> dict:
    rows = match_backtest.get("rows", [])
    goal_rows = goal_backtest.get("rows", [])
    reports = {item["match_id"]: item for item in preview_index.get("reports", [])}
    misses = [row for row in rows if not row.get("correct")]
    correct = [row for row in rows if row.get("correct")]
    miss_types = Counter()
    for row in misses:
        if row["actual"] == "draw":
            miss_types["missed_draw"] += 1
        if row.get("is_big_match"):
            miss_types["big_match_miss"] += 1
        if row.get("confidence_probability", 0) >= 0.5:
            miss_types["overconfident_miss"] += 1
        if row["predicted"] == "target_win" and row["actual"] != "target_win":
            miss_types["overrated_besiktas"] += 1
        if row["predicted"] == "opponent_win" and row["actual"] != "opponent_win":
            miss_types["overrated_opponent"] += 1

    scored_goal_rows = [row for row in goal_rows if row.get("has_besiktas_goal", True)]
    goal_misses = [row for row in scored_goal_rows if not row.get("hit_top_5")]
    goal_top8_misses = [row for row in scored_goal_rows if not row.get("hit_top_8")]
    goal_top10_misses = [row for row in scored_goal_rows if not row.get("hit_top_10")]
    goal_top3_misses = [row for row in scored_goal_rows if not row.get("hit_top_3")]
    recommendations = build_recommendations(miss_types, misses, goal_misses)
    return {
        "summary": {
            "match_rows": len(rows),
            "match_correct": len(correct),
            "match_accuracy": round(len(correct) / len(rows), 3) if rows else 0,
            "match_misses": len(misses),
            "goal_rows": len(scored_goal_rows),
            "goal_top3_misses": len(goal_top3_misses),
            "goal_top5_misses": len(goal_misses),
            "goal_top8_misses": len(goal_top8_misses),
            "goal_top10_misses": len(goal_top10_misses),
            "miss_types": dict(miss_types),
        },
        "critical_misses": enrich_misses(misses, reports),
        "goal_misses": goal_misses,
        "recommendations": recommendations,
    }


def enrich_misses(misses: list[dict], reports: dict[str, dict]) -> list[dict]:
    enriched = []
    for row in misses:
        report = reports.get(row["match_id"], {})
        probability_gap = row.get("confidence_probability", 0)
        enriched.append(
            {
                **row,
                "week": report.get("week"),
                "confidence_bucket": "OVERCONFIDENT" if probability_gap >= 0.5 else "LOW_MARGIN",
                "diagnosis": diagnose(row),
            }
        )
    return enriched


def diagnose(row: dict) -> str:
    if row["actual"] == "draw":
        return "Beraberlik riski ana tahminin gerisinde kalmış."
    if row.get("is_big_match"):
        return "Büyük maç oynaklığı ve kadro/duygu etkisi modele eksik yansımış."
    if row["predicted"] == "target_win":
        return "Beşiktaş form veya güç sinyali fazla pozitif ağırlık almış."
    if row["predicted"] == "opponent_win":
        return "Rakip güç/form sinyali fazla pozitif ağırlık almış."
    return "Düşük marjlı hata."


def build_recommendations(miss_types: Counter, misses: list[dict], goal_misses: list[dict]) -> list[dict]:
    recommendations = []
    if miss_types["missed_draw"]:
        recommendations.append(
            {
                "priority": "HIGH",
                "area": "Beraberlik riski",
                "action": "Ana olasılığı bozmadan beraberlik risk katmanını UI'da daha görünür yap; xG farkı dar ve güç farkı düşük maçları 'korumalı senaryo' diye etiketle.",
            }
        )
    if miss_types["big_match_miss"]:
        recommendations.append(
            {
                "priority": "HIGH",
                "area": "Büyük maç modeli",
                "action": "Derbi/büyük maçlar için ayrı katsayı eğit; hakem kart profili, önceki büyük maç oyuncu kart/gol sinyali ve kadro denetimi etkisini ayrı ölç.",
            }
        )
    if miss_types["overconfident_miss"]:
        recommendations.append(
            {
                "priority": "MEDIUM",
                "area": "Güven kalibrasyonu",
                "action": "Yüksek olasılık verilen ama yanlış çıkan maçlarda confidence seviyesini düşüren risk bayrakları ekle.",
            }
        )
    if goal_misses:
        recommendations.append(
            {
                "priority": "MEDIUM",
                "area": "Gol adayı",
                "action": "Defans, duran top ve sonradan giren oyuncu gol olasılığı için ayrı aday havuzu üret; mevcut model ilk 11/gol formuna fazla bağlı.",
            }
        )
    if not recommendations:
        recommendations.append(
            {
                "priority": "LOW",
                "area": "Genel",
                "action": "Mevcut sinyalleri koru, daha fazla sezon verisiyle katsayıları yeniden test et.",
            }
        )
    return recommendations


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# Tahmin Hata Analizi",
        "",
        f"- Maç tahmini: {summary['match_correct']}/{summary['match_rows']} (%{round(summary['match_accuracy'] * 100)})",
        f"- Hatalı maç: {summary['match_misses']}",
        f"- Gol adayı Top 3 kaçan: {summary['goal_top3_misses']}",
        f"- Gol adayı Top 5 kaçan: {summary['goal_top5_misses']}",
        f"- Gol adayı Top 8 kaçan: {summary['goal_top8_misses']}",
        f"- Gol adayı Top 10 kaçan: {summary['goal_top10_misses']}",
        "",
        "## Hata Tipleri",
        "",
    ]
    for key, value in summary["miss_types"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Öncelikli İyileştirmeler", ""])
    for item in payload["recommendations"]:
        lines.append(f"- {item['priority']} | {item['area']}: {item['action']}")
    lines.extend(["", "## Kritik Kaçan Maçlar", ""])
    for row in payload["critical_misses"][:15]:
        lines.append(
            f"- {row['date']} | {row['fixture']} | skor {row['actual_score']} | "
            f"tahmin={row['predicted']} gerçek={row['actual']} | {row['diagnosis']}"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    main()
