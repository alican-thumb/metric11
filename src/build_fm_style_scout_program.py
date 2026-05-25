from __future__ import annotations

import argparse
import json
from html import escape
from pathlib import Path

from src.config import PROCESSED_DIR


def main() -> None:
    parser = argparse.ArgumentParser(description="FM tarzı scout programı: rol, fiziksel yük, fırsat ve takım ihtiyacı önerileri üretir.")
    parser.add_argument("--scout", default=str(PROCESSED_DIR / "league_scouting_enriched_2025_2026.json"))
    parser.add_argument("--needs", default=str(PROCESSED_DIR / "besiktas_team_needs_2025_2026.json"))
    parser.add_argument("--output-prefix", default="fm_style_scout_program_2025_2026")
    args = parser.parse_args()

    scout = json.loads(Path(args.scout).read_text(encoding="utf-8"))
    needs = json.loads(Path(args.needs).read_text(encoding="utf-8"))
    payload = build_payload(scout, needs)

    json_path = PROCESSED_DIR / f"{args.output_prefix}.json"
    md_path = PROCESSED_DIR / f"{args.output_prefix}.md"
    html_path = PROCESSED_DIR / f"{args.output_prefix}.html"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(build_markdown(payload), encoding="utf-8")
    html_path.write_text(build_html(payload), encoding="utf-8")
    print(md_path.read_text(encoding="utf-8"))


def build_payload(scout: dict, needs: dict) -> dict:
    candidates = []
    for player in scout.get("enriched_shortlist", []):
        candidate = enrich_candidate(player)
        candidates.append(candidate)

    role_buckets = {
        "immediate_scorer": top_by(candidates, "immediate_scorer_score"),
        "physical_engine": top_by(candidates, "physical_engine_score"),
        "resale_value": top_by(candidates, "resale_value_score"),
        "contract_opportunity": top_by(candidates, "contract_opportunity_score"),
        "low_risk_regular": top_by(candidates, "low_risk_regular_score"),
    }
    return {
        "team": needs.get("team"),
        "summary": {
            "candidate_count": len(candidates),
            "high_priority_needs": sum(1 for item in needs.get("needs", []) if item.get("priority") == "HIGH"),
            "role_buckets": len(role_buckets),
            "model_note": "MVP rol motoru; TFF maç kullanımı, gol, kart, yaş, sözleşme ve varsa attribute sinyalinden türetilir.",
        },
        "team_needs": needs.get("needs", []),
        "position_action_plan": needs.get("position_action_plan", []),
        "role_buckets": role_buckets,
        "all_candidates": sorted(candidates, key=lambda item: item["overall_fm_fit_score"], reverse=True),
    }


def enrich_candidate(player: dict) -> dict:
    attribute = player.get("attribute_signal", {})
    external = player.get("external_api_signal", {})
    starts = player.get("starts", 0)
    goals = player.get("goals", 0)
    cards = player.get("cards", 0)
    age = player.get("age")
    opportunity = player.get("opportunity_score", 0)
    scout_value = player.get("scout_value_score", 0)
    physical_min, physical_max = estimate_physical_load(player)
    archetype = infer_archetype(player, physical_min, physical_max)
    discipline_penalty = 10 if player.get("discipline_risk") == "HIGH" else 4 if player.get("discipline_risk") == "MEDIUM" else 0
    age_bonus = max(0, 25 - (age or 30)) * 2.2 if age else 0
    contract_bonus = contract_opportunity_bonus(player)
    role_fit = attribute.get("role_fit_score") or 0
    potential = attribute.get("potential_ability") or 0
    growth = attribute.get("growth_room") or 0
    external_role = external.get("external_role_score") or 0
    external_rating = external.get("rating") or 0
    external_minutes = external.get("minutes") or 0
    external_quality = min(18, external_role * 0.045) + min(7, max(0, external_rating - 6.55) * 5) + min(4, external_minutes / 850)

    immediate_scorer = goals * 8 + starts * 0.8 + scout_value * 0.35 + external_quality * 0.35 - discipline_penalty
    scorer_profile_penalty = max(0, goals - 10) * 4.5
    physical_engine = physical_max * 7.5 + starts * 1.7 - cards * 1.2 + role_fit * 0.25 + external_defensive_bonus(external) - scorer_profile_penalty
    resale_age_penalty = max(0, (age or 30) - 25) * 7.0
    resale_value = age_bonus + goals * 2.4 + starts * 0.9 + growth * 0.3 + potential * 0.06 + external_quality * 0.18 - resale_age_penalty
    contract_opportunity = contract_bonus + opportunity * 0.5 + scout_value * 0.2 + external_quality * 0.15
    low_risk_regular = starts * 2.4 + player.get("availability_score", 0) * 0.45 + external_quality * 0.12 - cards * 2.0

    overall = (
        immediate_scorer * 0.25
        + physical_engine * 0.18
        + resale_value * 0.22
        + contract_opportunity * 0.22
        + low_risk_regular * 0.13
    )
    return {
        **player,
        "archetype": archetype,
        "estimated_physical_load_km_min": physical_min,
        "estimated_physical_load_km_max": physical_max,
        "physical_load_confidence": "LOW_DERIVED",
        "immediate_scorer_score": round(immediate_scorer, 2),
        "physical_engine_score": round(physical_engine, 2),
        "resale_value_score": round(resale_value, 2),
        "contract_opportunity_score": round(contract_opportunity, 2),
        "low_risk_regular_score": round(low_risk_regular, 2),
        "overall_fm_fit_score": round(overall, 2),
        "external_quality_score": round(external_quality, 2),
        "recommendation": recommendation_text(player, archetype, physical_min, physical_max),
    }


def external_defensive_bonus(external: dict) -> float:
    if not external.get("matched"):
        return 0.0
    return min(8, (external.get("duels_won") or 0) * 0.05 + (external.get("tackles") or 0) * 0.1 + (external.get("interceptions") or 0) * 0.14)


def infer_archetype(player: dict, physical_min: float, physical_max: float) -> str:
    goals = player.get("goals", 0)
    starts = player.get("starts", 0)
    cards = player.get("cards", 0)
    age = player.get("age") or 30
    if goals >= 12:
        return "Bitirici / skor yükü"
    if age <= 24 and starts >= 12:
        return "Genç değer / gelişim"
    if physical_max >= 11.6 and starts >= 20:
        return "Fizik motoru / tempo oyuncusu"
    if cards >= 8 and goals <= 4:
        return "Sertlik ve temas profili"
    if starts >= 24:
        return "Düşük riskli düzenli oyuncu"
    return "Rotasyon fırsatı"


def estimate_physical_load(player: dict) -> tuple[float, float]:
    starts = player.get("starts", 0)
    bench = player.get("bench", 0)
    goals = player.get("goals", 0)
    cards = player.get("cards", 0)
    availability = player.get("availability_score", 0)
    base = 8.7
    base += min(1.5, starts / 34 * 1.8)
    base += min(0.55, bench / 34 * 0.8)
    base += min(0.35, cards * 0.04)
    if goals >= 10:
        base -= 0.25
    if availability >= 85:
        base += 0.35
    low = max(7.4, base - 0.65)
    high = min(12.8, base + 0.85)
    return round(low, 1), round(high, 1)


def contract_opportunity_bonus(player: dict) -> float:
    risk = player.get("contract_risk")
    months = player.get("contract_months_left")
    if risk == "HIGH":
        return 24
    if risk == "MEDIUM":
        return 15
    if months is not None and months <= 24:
        return 8
    return 2


def recommendation_text(player: dict, archetype: str, physical_min: float, physical_max: float) -> str:
    external = player.get("external_api_signal", {})
    parts = [
        f"{archetype} profili.",
        f"Model tahmini fiziksel yük {physical_min}-{physical_max} km bandında.",
    ]
    if external.get("matched"):
        parts.append(
            f"2024 dış API sinyali: rating {external.get('rating') or 'yok'}, rol skoru {external.get('external_role_score') or 'yok'}."
        )
    if player.get("contract_risk") in {"HIGH", "MEDIUM"}:
        parts.append(f"Sözleşme fırsatı {player['contract_risk']} seviyesinde.")
    if player.get("resale_signal") == "HIGH":
        parts.append("Resale potansiyeli yüksek.")
    if player.get("goals", 0) >= 10:
        parts.append("Skor katkısı lig içi scout havuzunda öne çıkıyor.")
    return " ".join(parts)


def top_by(candidates: list[dict], field: str, limit: int = 12) -> list[dict]:
    return sorted(candidates, key=lambda item: item[field], reverse=True)[:limit]


def build_markdown(payload: dict) -> str:
    lines = [
        f"# {payload['team']} FM Tarzı Scout Programı",
        "",
        f"- Aday oyuncu: {payload['summary']['candidate_count']}",
        f"- Yüksek öncelikli ihtiyaç: {payload['summary']['high_priority_needs']}",
        f"- Not: {payload['summary']['model_note']}",
        f"- Dış API eşleşmesi: {sum(1 for item in payload['all_candidates'] if item.get('external_api_signal', {}).get('matched'))}",
        "",
        "## Takım İhtiyaç Özeti",
        "",
    ]
    for need in payload["team_needs"][:8]:
        lines.append(f"- {need['priority']}: {need['need']} — {need['reason']}")
    labels = {
        "immediate_scorer": "Hemen Skor Katkısı",
        "physical_engine": "Fizik Motoru",
        "resale_value": "Genç / Resale Değeri",
        "contract_opportunity": "Sözleşme Fırsatı",
        "low_risk_regular": "Düşük Riskli Düzenli Oyuncu",
    }
    for bucket, title in labels.items():
        lines.extend(["", f"## {title}", ""])
        for player in payload["role_buckets"][bucket][:8]:
            lines.append(
                f"- {player['name']} ({player['team']}): fit={player['overall_fm_fit_score']}, "
                f"rol={player['archetype']}, yaş={player.get('age')}, gol={player['goals']}, ilk11={player['starts']}, "
                f"yük={player['estimated_physical_load_km_min']}-{player['estimated_physical_load_km_max']} km, "
                f"dış-api={player.get('external_quality_score', 0)}, "
                f"öneri={player['recommendation']}"
            )
    return "\n".join(lines)


def build_html(payload: dict) -> str:
    buckets = "".join(bucket_section(key, title, payload["role_buckets"][key]) for key, title in (
        ("immediate_scorer", "Hemen Skor Katkısı"),
        ("physical_engine", "Fizik Motoru"),
        ("resale_value", "Genç / Resale Değeri"),
        ("contract_opportunity", "Sözleşme Fırsatı"),
        ("low_risk_regular", "Düşük Riskli Düzenli Oyuncu"),
    ))
    needs = "".join(
        f"<tr><td><span class=\"pill {priority_class(item['priority'])}\">{escape(item['priority'])}</span></td>"
        f"<td>{escape(item['need'])}</td><td>{escape(item['reason'])}</td></tr>"
        for item in payload["team_needs"][:8]
    )
    return f"""<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(payload['team'])} FM Tarzı Scout Programı</title>
  <style>
    :root {{ --bg:#f4f6f8; --panel:#fff; --ink:#15181d; --muted:#667085; --line:#dce2ea; --dark:#111318; --red:#bf1f2f; --amber:#b76b00; --green:#137a4b; --blue:#185ea8; --shadow:0 8px 22px rgba(18,24,32,.08); }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; font-family:Inter, system-ui, sans-serif; background:var(--bg); color:var(--ink); }}
    header {{ background:var(--dark); color:white; padding:28px 42px; border-bottom:4px solid var(--green); }}
    header h1 {{ margin:0 0 7px; font-size:32px; letter-spacing:0; }}
    header p {{ margin:0; color:#c9ced8; max-width:980px; line-height:1.5; }}
    main {{ max-width:1360px; margin:0 auto; padding:24px; }}
    .metrics {{ display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin-bottom:18px; }}
    .metric, section {{ background:var(--panel); border:1px solid var(--line); border-radius:8px; box-shadow:var(--shadow); }}
    .metric {{ padding:15px; }}
    .metric span {{ display:block; color:var(--muted); font-size:12px; }}
    .metric strong {{ display:block; font-size:28px; margin-top:5px; }}
    section {{ padding:18px; margin-bottom:18px; }}
    h2 {{ margin:0 0 14px; font-size:18px; }}
    table {{ width:100%; border-collapse:collapse; font-size:14px; }}
    th,td {{ padding:9px 7px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; }}
    th {{ color:var(--muted); font-size:12px; }}
    .pill {{ display:inline-flex; min-height:24px; align-items:center; border-radius:999px; padding:0 9px; font-size:12px; border:1px solid var(--line); }}
    .high {{ color:var(--red); background:#fff0f2; border-color:#efb7bf; }}
    .medium {{ color:var(--amber); background:#fff7e8; border-color:#f2d09a; }}
    .low {{ color:var(--green); background:#edf9f3; border-color:#b9dfcd; }}
    .role {{ color:var(--blue); background:#edf5ff; border-color:#bbd7f5; }}
    @media (max-width:900px) {{ .metrics {{ grid-template-columns:1fr; }} main {{ padding:14px; }} header {{ padding:22px; }} table {{ font-size:12px; }} }}
  </style>
</head>
<body>
  <header>
    <h1>{escape(payload['team'])} FM Tarzı Scout Programı</h1>
    <p>Rol bazlı aday listesi: skor katkısı, fizik motoru, genç/resale değer, sözleşme fırsatı ve düşük riskli düzenli oyuncu. Fiziksel yük değerleri olay verisinden türetilmiş tahmini aralıktır.</p>
  </header>
  <main>
    <div class="metrics">
      {metric("Aday", payload["summary"]["candidate_count"])}
      {metric("Yüksek ihtiyaç", payload["summary"]["high_priority_needs"])}
      {metric("Rol listesi", payload["summary"]["role_buckets"])}
    </div>
    <section><h2>Takım İhtiyaç Özeti</h2><table><thead><tr><th>Öncelik</th><th>İhtiyaç</th><th>Gerekçe</th></tr></thead><tbody>{needs}</tbody></table></section>
    {buckets}
  </main>
  <script defer src="/_vercel/insights/script.js"></script>
</body>
</html>
"""


def metric(label: str, value) -> str:
    return f'<div class="metric"><span>{escape(str(label))}</span><strong>{escape(str(value))}</strong></div>'


def bucket_section(key: str, title: str, players: list[dict]) -> str:
    rows = "".join(player_row(player, key) for player in players[:12])
    return (
        f"<section><h2>{escape(title)}</h2><table><thead><tr><th>Oyuncu</th><th>Takım</th><th>Rol</th>"
        f"<th>Fit</th><th>Rol Skoru</th><th>Dış API</th><th>Yaş</th><th>Gol</th><th>İlk 11</th><th>Yük km</th><th>Öneri</th></tr></thead>"
        f"<tbody>{rows}</tbody></table></section>"
    )


def player_row(player: dict, bucket: str) -> str:
    score_field = {
        "immediate_scorer": "immediate_scorer_score",
        "physical_engine": "physical_engine_score",
        "resale_value": "resale_value_score",
        "contract_opportunity": "contract_opportunity_score",
        "low_risk_regular": "low_risk_regular_score",
    }[bucket]
    load = f"{player['estimated_physical_load_km_min']}-{player['estimated_physical_load_km_max']}"
    return (
        f"<tr><td>{escape(player['name'])}</td><td>{escape(player.get('team') or '')}</td>"
        f"<td><span class=\"pill role\">{escape(player['archetype'])}</span></td>"
        f"<td>{player['overall_fm_fit_score']}</td><td>{player[score_field]}</td><td>{player.get('external_quality_score', 0)}</td>"
        f"<td>{escape(str(player.get('age') or ''))}</td><td>{player['goals']}</td><td>{player['starts']}</td>"
        f"<td>{load}</td><td>{escape(player['recommendation'])}</td></tr>"
    )


def priority_class(priority: str) -> str:
    value = priority.lower()
    if value == "high":
        return "high"
    if value == "medium":
        return "medium"
    return "low"


if __name__ == "__main__":
    main()
