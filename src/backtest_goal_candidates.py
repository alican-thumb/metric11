from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.config import PROCESSED_DIR


def main() -> None:
    parser = argparse.ArgumentParser(description="Gol adayi sinyali icin basit backtest raporu uretir.")
    parser.add_argument("--index", default=str(PROCESSED_DIR / "previews_besiktas_2025_2026_chronological" / "index.json"))
    parser.add_argument("--output-prefix", default="goal_candidate_backtest_2025_2026")
    args = parser.parse_args()

    index_payload = json.loads(Path(args.index).read_text(encoding="utf-8"))
    rows = []
    eligible = []
    for report in index_payload["reports"]:
        preview = json.loads(Path(report["json_path"]).read_text(encoding="utf-8"))
        goals = preview["goal_candidates"]
        actual_scorers = goals["actual_scorers"]
        row = {
            "match_id": report["match_id"],
            "fixture": f"{report['home_team']} - {report['away_team']}",
            "date": report["date"],
            "actual_score": report["actual_score"],
            "top_candidates": [item["name"] for item in goals["candidates"][:5]],
            "top_8_candidates": [item["name"] for item in goals["candidates"][:8]],
            "top_10_candidates": [item["name"] for item in goals["candidates"][:10]],
            "actual_scorers": [item["name"] for item in actual_scorers],
            "hit_top_3": goals["hit_top_3"],
            "hit_top_5": goals["hit_top_5"],
            "hit_top_8": goals.get("hit_top_8", goals["hit_top_5"]),
            "hit_top_10": goals.get("hit_top_10", goals.get("hit_top_8", goals["hit_top_5"])),
            "has_besiktas_goal": bool(actual_scorers),
        }
        rows.append(row)
        if row["has_besiktas_goal"]:
            eligible.append(row)

    summary = {
        "report_count": len(rows),
        "matches_with_besiktas_goal": len(eligible),
        "top_3_hits": sum(1 for row in eligible if row["hit_top_3"]),
        "top_5_hits": sum(1 for row in eligible if row["hit_top_5"]),
        "top_8_hits": sum(1 for row in eligible if row["hit_top_8"]),
        "top_10_hits": sum(1 for row in eligible if row["hit_top_10"]),
        "top_3_hit_rate": round(sum(1 for row in eligible if row["hit_top_3"]) / len(eligible), 3) if eligible else 0,
        "top_5_hit_rate": round(sum(1 for row in eligible if row["hit_top_5"]) / len(eligible), 3) if eligible else 0,
        "top_8_hit_rate": round(sum(1 for row in eligible if row["hit_top_8"]) / len(eligible), 3) if eligible else 0,
        "top_10_hit_rate": round(sum(1 for row in eligible if row["hit_top_10"]) / len(eligible), 3) if eligible else 0,
    }
    payload = {"summary": summary, "rows": rows}
    json_path = PROCESSED_DIR / f"{args.output_prefix}.json"
    md_path = PROCESSED_DIR / f"{args.output_prefix}.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(build_markdown(payload), encoding="utf-8")
    print(md_path.read_text(encoding="utf-8"))


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# Gol Adayı Backtest Raporu",
        "",
        f"- Rapor sayısı: {summary['report_count']}",
        f"- Beşiktaş'ın gol attığı maç sayısı: {summary['matches_with_besiktas_goal']}",
        f"- Top 3 isabet: {summary['top_3_hits']} (%{round(summary['top_3_hit_rate'] * 100)})",
        f"- Top 5 isabet: {summary['top_5_hits']} (%{round(summary['top_5_hit_rate'] * 100)})",
        f"- Top 8 isabet: {summary['top_8_hits']} (%{round(summary['top_8_hit_rate'] * 100)})",
        f"- Top 10 isabet: {summary['top_10_hits']} (%{round(summary['top_10_hit_rate'] * 100)})",
        "",
        "## Maç Bazlı",
        "",
    ]
    for row in payload["rows"]:
        if not row["has_besiktas_goal"]:
            continue
        lines.append(
            f"- {row['date']} | {row['fixture']} | skor {row['actual_score']} | "
            f"gerçek: {', '.join(row['actual_scorers'])} | "
            f"adaylar: {', '.join(row['top_candidates'])} | "
            f"top3={row['hit_top_3']} top5={row['hit_top_5']} top8={row['hit_top_8']} top10={row['hit_top_10']}"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    main()
