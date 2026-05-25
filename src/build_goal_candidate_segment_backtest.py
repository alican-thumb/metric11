from __future__ import annotations

import argparse
import json
import sqlite3
from collections import defaultdict
from pathlib import Path
from typing import Any

from src.config import PROCESSED_DIR


DEFAULT_WAREHOUSE = PROCESSED_DIR / "metric11_warehouse.sqlite"


def main() -> None:
    parser = argparse.ArgumentParser(description="Gol adayi segmentleri icin backtest raporu uretir.")
    parser.add_argument("--warehouse", default=str(DEFAULT_WAREHOUSE))
    parser.add_argument("--goal-backtest", default=str(PROCESSED_DIR / "goal_candidate_backtest_2025_2026.json"))
    parser.add_argument("--output-prefix", default="goal_candidate_segment_backtest_2025_2026")
    args = parser.parse_args()

    warehouse = Path(args.warehouse)
    if not warehouse.exists():
        raise SystemExit(f"Warehouse bulunamadi: {warehouse}")

    conn = sqlite3.connect(warehouse)
    conn.row_factory = sqlite3.Row
    try:
        rows = [dict(row) for row in conn.execute("SELECT * FROM goal_candidates ORDER BY match_external_id, rank")]
    finally:
        conn.close()

    goal_backtest = load_json(Path(args.goal_backtest), {})
    payload = build_payload(rows, goal_backtest)

    json_path = PROCESSED_DIR / f"{args.output_prefix}.json"
    md_path = PROCESSED_DIR / f"{args.output_prefix}.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(build_markdown(payload), encoding="utf-8")
    print(md_path.read_text(encoding="utf-8"))


def build_payload(rows: list[dict[str, Any]], goal_backtest: dict[str, Any]) -> dict[str, Any]:
    segments = defaultdict(list)
    for row in rows:
        for segment in split_segments(row.get("candidate_type")):
            segments[segment].append(row)

    segment_summaries = [summarize_segment(segment, items) for segment, items in segments.items()]
    segment_summaries.sort(key=lambda item: (item["match_hit_rate"], item["row_hit_rate"], -item["avg_rank"]), reverse=True)

    rank_buckets = {
        "top_3": summarize_rank_bucket(rows, 3),
        "top_5": summarize_rank_bucket(rows, 5),
        "top_8": summarize_rank_bucket(rows, 8),
        "top_10": summarize_rank_bucket(rows, 10),
    }
    backtest_summary = goal_backtest.get("summary", {}) if isinstance(goal_backtest, dict) else {}
    recommendations = build_recommendations(segment_summaries, rank_buckets)
    return {
        "summary": {
            "candidate_rows": len(rows),
            "matches": len({row["match_external_id"] for row in rows}),
            "segments": len(segment_summaries),
            "backtest_summary": backtest_summary,
            "rank_buckets": rank_buckets,
        },
        "segments": segment_summaries,
        "recommendations": recommendations,
        "weak_candidates": build_weak_candidate_queue(rows),
    }


def split_segments(candidate_type: str | None) -> list[str]:
    if not candidate_type:
        return ["unknown"]
    return [part.strip() for part in candidate_type.split("+") if part.strip()] or ["unknown"]


def summarize_segment(segment: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    matches = {row["match_external_id"] for row in rows}
    hit_rows = [row for row in rows if row.get("actual_scorer")]
    hit_matches = {row["match_external_id"] for row in hit_rows}
    top5_rows = [row for row in rows if row["rank"] <= 5]
    top5_hit_matches = {row["match_external_id"] for row in top5_rows if row.get("actual_scorer")}
    return {
        "segment": segment,
        "candidate_rows": len(rows),
        "matches": len(matches),
        "hit_rows": len(hit_rows),
        "hit_matches": len(hit_matches),
        "row_hit_rate": pct(len(hit_rows), len(rows)),
        "match_hit_rate": pct(len(hit_matches), len(matches)),
        "top5_candidate_rows": len(top5_rows),
        "top5_hit_matches": len(top5_hit_matches),
        "top5_match_hit_rate": pct(len(top5_hit_matches), len(matches)),
        "avg_rank": round(sum(row["rank"] for row in rows) / len(rows), 2) if rows else 0,
        "example_hits": [
            {
                "match_external_id": row["match_external_id"],
                "rank": row["rank"],
                "player_name": row["player_name"],
                "team_name": row.get("team_name"),
            }
            for row in hit_rows[:8]
        ],
    }


def summarize_rank_bucket(rows: list[dict[str, Any]], top_n: int) -> dict[str, Any]:
    matches = {row["match_external_id"] for row in rows}
    bucket_rows = [row for row in rows if row["rank"] <= top_n]
    hit_matches = {row["match_external_id"] for row in bucket_rows if row.get("actual_scorer")}
    hit_rows = [row for row in bucket_rows if row.get("actual_scorer")]
    return {
        "top_n": top_n,
        "candidate_rows": len(bucket_rows),
        "hit_rows": len(hit_rows),
        "hit_matches": len(hit_matches),
        "match_hit_rate": pct(len(hit_matches), len(matches)),
        "row_hit_rate": pct(len(hit_rows), len(bucket_rows)),
    }


def build_recommendations(segments: list[dict[str, Any]], rank_buckets: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
    recommendations = []
    by_name = {item["segment"]: item for item in segments}
    set_piece = by_name.get("set_piece_defender")
    penalty = by_name.get("penalty_profile")
    impact = by_name.get("impact_sub")
    primary = by_name.get("primary")

    if set_piece and set_piece["row_hit_rate"] < 0.04:
        recommendations.append(
            {
                "priority": "HIGH",
                "area": "Duran top/defans adayları",
                "action": "Defans adaylarını ilk 5'e taşımadan önce takım korner/duran top verisi veya oyuncu boy/hava topu sinyaliyle doğrula.",
            }
        )
    if penalty and penalty["hit_rows"] == 0:
        recommendations.append(
            {
                "priority": "HIGH",
                "area": "Penaltı profili",
                "action": "Penaltı adayını ayrı skor bonusu olarak tut; gerçek penaltıcı doğrulanana kadar tek başına üst sıra etkisini sınırlı kullan.",
            }
        )
    if impact and primary and impact["row_hit_rate"] >= primary["row_hit_rate"]:
        recommendations.append(
            {
                "priority": "MEDIUM",
                "area": "Yedek etki",
                "action": "Impact-sub segmenti primary kadar verimli; maç önü ekranda ilk 5 dışında ayrı 'sonradan gol' alanı olarak göster.",
            }
        )
    if rank_buckets["top_5"]["match_hit_rate"] < 0.75:
        recommendations.append(
            {
                "priority": "MEDIUM",
                "area": "Top 5 sıralama",
                "action": "Top 5'i güçlendirmek için düşük isabetli segmentleri ilk 5 yerine 6-10 bandına indir.",
            }
        )
    return recommendations or [
        {
            "priority": "LOW",
            "area": "Genel",
            "action": "Segment dağılımı kabul edilebilir; daha fazla maç ve oyuncu aksiyon verisiyle yeniden ölç.",
        }
    ]


def build_weak_candidate_queue(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped = defaultdict(lambda: {"rows": 0, "hits": 0, "top5_rows": 0})
    for row in rows:
        key = (row["player_name"], row.get("candidate_type") or "unknown")
        grouped[key]["rows"] += 1
        grouped[key]["hits"] += 1 if row.get("actual_scorer") else 0
        grouped[key]["top5_rows"] += 1 if row["rank"] <= 5 else 0
    queue = []
    for (player_name, candidate_type), stats in grouped.items():
        if stats["top5_rows"] >= 3 and stats["hits"] == 0:
            queue.append(
                {
                    "player_name": player_name,
                    "candidate_type": candidate_type,
                    **stats,
                    "recommendation": "Top 5 sıralama etkisini düşür veya aday tipini yeniden kontrol et.",
                }
            )
    return sorted(queue, key=lambda item: (item["top5_rows"], item["rows"]), reverse=True)[:30]


def build_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Gol Adayı Segment Backtest",
        "",
        f"- Aday satırı: {summary['candidate_rows']}",
        f"- Maç: {summary['matches']}",
        f"- Segment: {summary['segments']}",
        f"- Genel backtest: {summary.get('backtest_summary', {})}",
        "",
        "## Rank Kırılımı",
        "",
        "| Bucket | Aday satırı | İsabet satırı | İsabetli maç | Maç hit rate | Satır hit rate |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for name, item in summary["rank_buckets"].items():
        lines.append(
            f"| {name} | {item['candidate_rows']} | {item['hit_rows']} | {item['hit_matches']} | "
            f"%{round(item['match_hit_rate'] * 100, 1)} | %{round(item['row_hit_rate'] * 100, 1)} |"
        )

    lines.extend(
        [
            "",
            "## Segment Tablosu",
            "",
            "| Segment | Aday satırı | Maç | İsabet satırı | İsabetli maç | Maç hit rate | Satır hit rate | Top 5 maç hit rate | Ortalama sıra |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for item in payload["segments"]:
        lines.append(
            f"| {item['segment']} | {item['candidate_rows']} | {item['matches']} | {item['hit_rows']} | "
            f"{item['hit_matches']} | %{round(item['match_hit_rate'] * 100, 1)} | "
            f"%{round(item['row_hit_rate'] * 100, 1)} | %{round(item['top5_match_hit_rate'] * 100, 1)} | {item['avg_rank']} |"
        )

    lines.extend(["", "## Öncelikli Aksiyonlar", ""])
    for item in payload["recommendations"]:
        lines.append(f"- {item['priority']} | {item['area']}: {item['action']}")

    lines.extend(["", "## Top 5 Zayıf Aday Kuyruğu", ""])
    if payload["weak_candidates"]:
        for item in payload["weak_candidates"]:
            lines.append(
                f"- {item['player_name']} | {item['candidate_type']} | top5={item['top5_rows']} | "
                f"satır={item['rows']} | isabet={item['hits']} | {item['recommendation']}"
            )
    else:
        lines.append("- Top 5 içinde tekrar eden sıfır isabetli aday yok.")
    return "\n".join(lines)


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def pct(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 3) if denominator else 0


if __name__ == "__main__":
    main()
