from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from src.config import PROCESSED_DIR, SEASON, SEASON_LABEL
from src.html_utils import md_to_html, page_html
from src.normalization import normalize_team_name


DRAW_BANDS = (0.0, 0.10, 0.20, 0.30, 0.40)
RESULT_LABELS = {"home": "Ev", "draw": "X", "away": "Dep"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Lig modeli ile kulüp piyasa değeri baseline'ını karşılaştırır.")
    parser.add_argument("--league-model", default=str(PROCESSED_DIR / f"league_prediction_model_{SEASON}.json"))
    parser.add_argument("--market-values", default=str(PROCESSED_DIR / f"transfermarkt_super_lig_squads_{SEASON}.json"))
    parser.add_argument("--output-prefix", default=f"league_market_value_audit_{SEASON}")
    args = parser.parse_args()

    league_model = load_json(Path(args.league_model))
    market_payload = load_json(Path(args.market_values))
    payload = build_audit(league_model, market_payload)
    md = build_markdown(payload)
    json_path = PROCESSED_DIR / f"{args.output_prefix}.json"
    md_path = PROCESSED_DIR / f"{args.output_prefix}.md"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(md, encoding="utf-8")
    html_path = PROCESSED_DIR / f"{args.output_prefix}.html"
    html_path.write_text(page_html("Lig Piyasa Değeri Denetimi (2025-26 Arşiv)", md_to_html(md), description="18 Süper Lig takımının Transfermarkt kadro değerlerini model tahminleriyle karşılaştıran retrospektif denetim — metric11."), encoding="utf-8")
    print(md)


def load_json(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"Girdi bulunamadı: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def build_audit(league_model: dict, market_payload: dict) -> dict:
    markets = {
        normalize_team_name(club.get("team_name")): club.get("summary", {}).get("market_value_total_eur")
        for club in market_payload.get("clubs", [])
        if club.get("summary", {}).get("market_value_total_eur")
    }
    covered_rows: list[dict[str, Any]] = []
    missing_teams: set[str] = set()
    for row in league_model.get("rows", []):
        home = normalize_team_name(row.get("home"))
        away = normalize_team_name(row.get("away"))
        home_value = markets.get(home)
        away_value = markets.get(away)
        if not home_value or not away_value:
            missing_teams.update(team for team, value in ((home, home_value), (away, away_value)) if not value)
            continue
        log_edge = math.log(home_value / away_value)
        covered_rows.append(
            {
                **row,
                "home_market_value_eur": home_value,
                "away_market_value_eur": away_value,
                "market_edge_million_eur": round((home_value - away_value) / 1_000_000, 2),
                "market_log_edge": round(log_edge, 4),
            }
        )

    thresholds = [evaluate_band(covered_rows, band) for band in DRAW_BANDS]
    diagnostic_best = max(thresholds, key=lambda item: (item["accuracy"], item["draw_recall"]))
    benchmark_band = 0.20
    benchmark = next(item for item in thresholds if item["draw_band"] == benchmark_band)
    benchmark_rows = add_baseline_prediction(covered_rows, benchmark_band)
    disagreements = [
        row for row in benchmark_rows
        if row["predicted"] != row["market_prediction"]
    ]
    high_edge_misses = [
        row for row in benchmark_rows
        if abs(row["market_log_edge"]) >= 0.70 and not row["correct"]
    ]
    by_team: dict[str, dict[str, int]] = defaultdict(lambda: {"matches": 0, "model_correct": 0, "market_correct": 0})
    for row in benchmark_rows:
        for team in (row["home"], row["away"]):
            by_team[team]["matches"] += 1
            by_team[team]["model_correct"] += int(row["correct"])
            by_team[team]["market_correct"] += int(row["market_correct"])

    return {
        "season": SEASON_LABEL,
        "methodology": {
            "scope": "Retrospektif tanısal benchmark; üretim tahmin girdisi değildir.",
            "warning": "Piyasa değeri snapshot'ı maç tarihlerinden sonraki değer/transfer güncellemelerini içerebilir; ileriye dönük model başarısı iddiası kurulamaz.",
            "baseline": "Ev-deplasman toplam piyasa değerlerinin doğal log farkı; mutlak fark eşikten küçükse beraberlik.",
            "reporting_band": benchmark_band,
        },
        "summary": {
            "market_clubs": len(markets),
            "market_players": market_payload.get("summary", {}).get("players", 0),
            "market_value_total_eur": market_payload.get("summary", {}).get("market_value_total_eur", 0),
            "league_model_matches": len(league_model.get("rows", [])),
            "covered_matches": len(covered_rows),
            "coverage_rate": round(len(covered_rows) / len(league_model.get("rows", [])), 3) if league_model.get("rows") else 0,
            "missing_teams": sorted(missing_teams),
            "model_accuracy": league_model.get("summary", {}).get("accuracy", 0),
            "reporting_baseline_accuracy": benchmark["accuracy"],
            "reporting_baseline_draw_recall": benchmark["draw_recall"],
            "model_market_disagreements": len(disagreements),
            "model_accuracy_on_disagreements": accuracy(disagreements, "correct"),
            "market_accuracy_on_disagreements": accuracy(disagreements, "market_correct"),
            "high_market_edge_model_misses": len(high_edge_misses),
            "diagnostic_best_band": diagnostic_best["draw_band"],
            "diagnostic_best_accuracy": diagnostic_best["accuracy"],
        },
        "thresholds": thresholds,
        "team_comparison": [
            {
                "team": team,
                "market_value_eur": markets.get(normalize_team_name(team)),
                **stats,
                "model_accuracy": round(stats["model_correct"] / stats["matches"], 3),
                "market_accuracy": round(stats["market_correct"] / stats["matches"], 3),
            }
            for team, stats in sorted(by_team.items())
        ],
        "largest_disagreements": sorted(disagreements, key=lambda row: abs(row["market_log_edge"]), reverse=True)[:20],
        "high_market_edge_model_misses": sorted(high_edge_misses, key=lambda row: abs(row["market_log_edge"]), reverse=True),
    }


def add_baseline_prediction(rows: list[dict[str, Any]], band: float) -> list[dict[str, Any]]:
    enriched = []
    for row in rows:
        market_prediction = market_result(row["market_log_edge"], band)
        enriched.append({**row, "market_prediction": market_prediction, "market_correct": market_prediction == row["actual"]})
    return enriched


def evaluate_band(rows: list[dict[str, Any]], band: float) -> dict[str, Any]:
    evaluated = add_baseline_prediction(rows, band)
    actual_draws = sum(1 for row in evaluated if row["actual"] == "draw")
    predicted_draws = sum(1 for row in evaluated if row["market_prediction"] == "draw")
    correct_draws = sum(1 for row in evaluated if row["actual"] == "draw" and row["market_prediction"] == "draw")
    return {
        "draw_band": band,
        "accuracy": accuracy(evaluated, "market_correct"),
        "correct": sum(1 for row in evaluated if row["market_correct"]),
        "matches": len(evaluated),
        "prediction_distribution": dict(Counter(row["market_prediction"] for row in evaluated)),
        "draw_precision": round(correct_draws / predicted_draws, 3) if predicted_draws else 0,
        "draw_recall": round(correct_draws / actual_draws, 3) if actual_draws else 0,
    }


def market_result(log_edge: float, band: float) -> str:
    if log_edge > band:
        return "home"
    if log_edge < -band:
        return "away"
    return "draw"


def accuracy(rows: list[dict[str, Any]], key: str) -> float:
    return round(sum(1 for row in rows if row.get(key)) / len(rows), 3) if rows else 0


def build_markdown(payload: dict) -> str:
    summary = payload["summary"]
    methodology = payload["methodology"]
    lines = [
        "# Lig Geneli Piyasa Değeri / Model Denetimi (2025-26 Arşiv)",
        "",
        f"- Sezon: {payload['season']}",
        f"- Transfermarkt kulüp kapsamı: {summary['market_clubs']}/18",
        f"- Kadro oyuncusu: {summary['market_players']}",
        f"- Toplam piyasa değeri: €{summary['market_value_total_eur']:,}",
        f"- Maç kapsamı: {summary['covered_matches']}/{summary['league_model_matches']} (%{round(summary['coverage_rate'] * 100)})",
        f"- Lig modeli doğruluğu: %{round(summary['model_accuracy'] * 100)}",
        f"- Sabit draw-band 0.20 piyasa değeri baseline doğruluğu: %{round(summary['reporting_baseline_accuracy'] * 100)}",
        f"- Sabit draw-band 0.20 beraberlik yakalama: %{round(summary['reporting_baseline_draw_recall'] * 100)}",
        f"- Model / piyasa baseline anlaşmazlığı: {summary['model_market_disagreements']}",
        f"- Anlaşmazlıklarda model doğruluğu: %{round(summary['model_accuracy_on_disagreements'] * 100)}",
        f"- Anlaşmazlıklarda piyasa baseline doğruluğu: %{round(summary['market_accuracy_on_disagreements'] * 100)}",
        f"- Belirgin değer farkında model hatası: {summary['high_market_edge_model_misses']}",
        "",
        "## Kullanım Sınırı",
        "",
        f"- {methodology['scope']}",
        f"- {methodology['warning']}",
        "- Bu rapor market-value özelliğini modele eklemeden önce geçmiş dönemde nerede açıklayıcı olabileceğini ölçer.",
        "",
        "## Eşik Karşılaştırması",
        "",
        "| Draw band | Doğruluk | Beraberlik precision | Beraberlik recall | Tahmin dağılımı |",
        "| ---: | ---: | ---: | ---: | --- |",
    ]
    for item in payload["thresholds"]:
        lines.append(
            f"| {item['draw_band']:.2f} | %{round(item['accuracy'] * 100)} | "
            f"%{round(item['draw_precision'] * 100)} | %{round(item['draw_recall'] * 100)} | "
            f"{item['prediction_distribution']} |"
        )
    lines.extend(["", "## Takım Bazlı Karşılaştırma", "", "| Takım | Değer | Maç | Model | Değer baseline |", "| --- | ---: | ---: | ---: | ---: |"])
    for row in sorted(payload["team_comparison"], key=lambda item: item.get("market_value_eur") or 0, reverse=True):
        lines.append(
            f"| {row['team']} | €{row['market_value_eur']:,} | {row['matches']} | "
            f"%{round(row['model_accuracy'] * 100)} | %{round(row['market_accuracy'] * 100)} |"
        )
    lines.extend(["", "## En Büyük Anlaşmazlıklar", ""])
    for row in payload["largest_disagreements"][:10]:
        lines.append(
            f"- {row['date']} | {row['home']} - {row['away']} ({row['score']}) | "
            f"model={RESULT_LABELS[row['predicted']]} baseline={RESULT_LABELS[row['market_prediction']]} "
            f"gerçek={RESULT_LABELS[row['actual']]} | değer farkı=€{row['market_edge_million_eur']}m"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    main()
