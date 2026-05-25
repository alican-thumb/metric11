from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from src.config import PROCESSED_DIR
from src.normalization import normalize_team_name


RESULT_LABELS = {
    "target_win": "Beşiktaş",
    "draw": "Beraberlik",
    "opponent_win": "Rakip",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Beşiktaş taraf tahmini tersine dönen maçları denetler.")
    parser.add_argument(
        "--protected-action-audit",
        default=str(PROCESSED_DIR / "protected_action_audit_2025_2026.json"),
    )
    parser.add_argument(
        "--market-values",
        default=str(PROCESSED_DIR / "transfermarkt_super_lig_squads_2025_2026.json"),
    )
    parser.add_argument("--output-prefix", default="side_flip_audit_2025_2026")
    args = parser.parse_args()

    protected_audit = json.loads(Path(args.protected_action_audit).read_text(encoding="utf-8"))
    market_values = load_market_values(Path(args.market_values))
    audit = build_audit(protected_audit.get("rows", []), market_values)

    json_path = PROCESSED_DIR / f"{args.output_prefix}.json"
    md_path = PROCESSED_DIR / f"{args.output_prefix}.md"
    json_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(build_markdown(audit), encoding="utf-8")
    print(md_path.read_text(encoding="utf-8"))


def build_audit(rows: list[dict[str, Any]], market_values: dict[str, Any]) -> dict[str, Any]:
    side_flips = [enrich_row(row, market_values) for row in rows if row.get("side_pick_wrong")]
    protected_side_flips = [row for row in side_flips if row["protected"]]
    unprotected_side_flips = [row for row in side_flips if not row["protected"]]

    return {
        "summary": {
            "side_flip_count": len(side_flips),
            "protected_side_flip_count": len(protected_side_flips),
            "unprotected_side_flip_count": len(unprotected_side_flips),
            "target_overrated_count": sum(1 for row in side_flips if row["predicted"] == "target_win"),
            "opponent_overrated_count": sum(1 for row in side_flips if row["predicted"] == "opponent_win"),
            "big_match_side_flip_count": sum(1 for row in side_flips if row["is_big_match"]),
            "high_draw_risk_side_flip_count": sum(1 for row in side_flips if row.get("draw_risk_level") == "HIGH"),
            "opponent_market_value_covered": sum(1 for row in side_flips if row.get("opponent_market_value_eur")),
            "avg_market_value_edge_million_eur": avg(
                row["market_value_edge_million_eur"]
                for row in side_flips
                if row.get("market_value_edge_million_eur") is not None
            ),
            "missing_data_gap_counts": dict(Counter(gap for row in side_flips for gap in row["data_gaps"])),
            "signal_tag_counts": dict(Counter(tag for row in side_flips for tag in row["signal_tags"])),
        },
        "rows": side_flips,
        "protected_side_flips": protected_side_flips,
        "unprotected_side_flips": unprotected_side_flips,
    }


def enrich_row(row: dict[str, Any], market_values: dict[str, Any]) -> dict[str, Any]:
    preview = load_preview(row)
    probabilities = preview.get("probabilities", {})
    match = preview.get("match", {})
    availability = preview.get("availability_signal", {})
    expected_for = probabilities.get("expected_goals_for")
    expected_against = probabilities.get("expected_goals_against")
    xg_edge = round((expected_for or 0) - (expected_against or 0), 3)
    signal_tags = list(row.get("failure_tags", []))
    target_market = market_values.get(normalize_team_name(match.get("target_team", "BEŞİKTAŞ A.Ş.")) or "")
    opponent_market = market_values.get(normalize_team_name(match.get("opponent", "")) or "")
    market_value_edge = None
    if target_market and opponent_market:
        market_value_edge = round((target_market["market_value_total_eur"] - opponent_market["market_value_total_eur"]) / 1_000_000, 2)

    if xg_edge > 0.25 and row["predicted"] == "target_win":
        signal_tags.append("model_xg_edge_overtrusted")
    if xg_edge < -0.25 and row["predicted"] == "opponent_win":
        signal_tags.append("opponent_xg_edge_overtrusted")
    if availability.get("unavailable"):
        signal_tags.append("availability_signal_present")
    if probabilities.get("card_signal") == "HIGH":
        signal_tags.append("high_card_volatility")
    if market_value_edge is not None:
        if market_value_edge > 60 and row["predicted"] == "target_win":
            signal_tags.append("market_value_edge_supports_target")
        elif market_value_edge < -30 and row["predicted"] == "opponent_win":
            signal_tags.append("market_value_edge_supports_opponent")
        elif abs(market_value_edge) < 20:
            signal_tags.append("market_value_near_balanced")

    return {
        **row,
        "opponent": match.get("opponent"),
        "home_away": match.get("home_away"),
        "expected_goals_for": expected_for,
        "expected_goals_against": expected_against,
        "xg_edge": xg_edge,
        "strength_edge": probabilities.get("strength_edge"),
        "target_market_value_eur": target_market.get("market_value_total_eur") if target_market else None,
        "opponent_market_value_eur": opponent_market.get("market_value_total_eur") if opponent_market else None,
        "market_value_edge_million_eur": market_value_edge,
        "market_value_source_url": opponent_market.get("source_url") if opponent_market else None,
        "availability_missing_count": probabilities.get("availability_missing_count", 0),
        "unavailable_players": [
            item.get("player_name") or item.get("player_external_id") or "unknown"
            for item in availability.get("unavailable", [])
        ],
        "card_signal": probabilities.get("card_signal"),
        "recommended_scoreline": (probabilities.get("recommended_scoreline") or {}).get("score"),
        "signal_tags": signal_tags,
        "data_gaps": data_gaps(preview, opponent_market),
    }


def data_gaps(preview: dict[str, Any], opponent_market: dict[str, Any] | None) -> list[str]:
    gaps = [
        "odds_baseline_missing",
        "official_injury_feed_missing",
        "confirmed_lineup_quality_missing",
    ]
    if not opponent_market:
        gaps.insert(0, "opponent_market_value_missing")
    if not preview.get("availability_signal", {}).get("unavailable"):
        gaps.append("no_matchday_availability_signal")
    if not preview.get("probabilities", {}).get("big_match_profile"):
        gaps.append("no_big_match_profile")
    return gaps


def load_market_values(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("clubs"):
        return {
            normalize_team_name(club.get("team_name") or "") or "": {
                "team_name": club.get("team_name"),
                "market_value_total_eur": club.get("summary", {}).get("market_value_total_eur"),
                "source_url": club.get("url"),
            }
            for club in payload["clubs"]
        }
    return {
        normalize_team_name(item.get("canonical_team") or item.get("team_name") or "") or "": item
        for item in payload.get("teams", [])
    }


def load_preview(row: dict[str, Any]) -> dict[str, Any]:
    match_id = row["match_id"]
    path = PROCESSED_DIR / "previews_besiktas_2025_2026_chronological" / f"week_{int(row['week']):02d}_{match_id}.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def avg(values) -> float | None:
    values = list(values)
    return round(sum(values) / len(values), 2) if values else None


def build_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Yanlış Taraf / Side Flip Denetimi",
        "",
        f"- Yanlış taraf vakası: {summary['side_flip_count']}",
        f"- Korumalı aksiyon içindeki yanlış taraf: {summary['protected_side_flip_count']}",
        f"- Korumalı olmayan yanlış taraf: {summary['unprotected_side_flip_count']}",
        f"- Beşiktaş tarafını fazla değerleme: {summary['target_overrated_count']}",
        f"- Rakibi fazla değerleme: {summary['opponent_overrated_count']}",
        f"- Büyük maç taraf dönüşü: {summary['big_match_side_flip_count']}",
        f"- HIGH draw risk ama net sonuç: {summary['high_draw_risk_side_flip_count']}",
        f"- Rakip piyasa değeri kapsanan vaka: {summary['opponent_market_value_covered']}/{summary['side_flip_count']}",
        f"- Ortalama Beşiktaş-rakip değer farkı: €{summary['avg_market_value_edge_million_eur']}m",
        f"- Veri boşluğu dağılımı: {summary['missing_data_gap_counts']}",
        f"- Sinyal etiketi dağılımı: {summary['signal_tag_counts']}",
        "",
        "## Okuma",
        "",
        "- Bu rapor beraberlik uyarısını değil, taraf seçiminin tersine döndüğü maçları inceler.",
        "- Rakip piyasa değeri snapshot'ı side flip vakaları için kapatıldı; kalan kritik boşluklar odds baseline, resmi sakatlık akışı ve doğrulanmış maç günü 11 kalitesidir.",
        "- Piyasa değeri farkı tek başına taraf tahmini değildir; modelin xG/güç sinyaliyle çeliştiği maçlarda kalibrasyon kontrolü sağlar.",
        "",
        "## Maçlar",
        "",
    ]
    for row in payload["rows"]:
        gaps = ", ".join(row["data_gaps"])
        tags = ", ".join(row["signal_tags"]) or "-"
        unavailable = ", ".join(row["unavailable_players"]) or "-"
        market_edge = f"€{row['market_value_edge_million_eur']}m" if row.get("market_value_edge_million_eur") is not None else "-"
        lines.append(
            f"- Hafta {row['week']} | {row['fixture']} | skor {row['actual_score']} | "
            f"tahmin={RESULT_LABELS[row['predicted']]} gerçek={RESULT_LABELS[row['actual']]} | "
            f"xG={row['expected_goals_for']}-{row['expected_goals_against']} edge={row['xg_edge']} | "
            f"strength_edge={row.get('strength_edge')} | market_edge={market_edge} | eksik={unavailable} | "
            f"risk={row.get('draw_risk_level') or '-'} {row.get('draw_risk_score') or '-'} | "
            f"etiket={tags} | veri_boşluğu={gaps}"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    main()
