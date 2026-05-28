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


_SCORE_FIELDS = [
    ("immediate_scorer_score",    "Gol Katkısı"),
    ("physical_engine_score",     "Fizik Motoru"),
    ("resale_value_score",        "Resale Değeri"),
    ("contract_opportunity_score","Kontrakt Fırsatı"),
    ("low_risk_regular_score",    "Güvenilirlik"),
]

_BUCKET_META = {
    "immediate_scorer":    ("⚽ Gol",      "immediate_scorer_score"),
    "physical_engine":     ("💪 Fizik",    "physical_engine_score"),
    "resale_value":        ("📈 Resale",   "resale_value_score"),
    "contract_opportunity":("🤝 Kontrakt", "contract_opportunity_score"),
    "low_risk_regular":    ("🛡 Düzenli",  "low_risk_regular_score"),
}

_ARCHETYPE_COLOR = {
    "Bitirici / skor yükü":             ("--arc-red",    "#fff0f2", "#bf1f2f"),
    "Genç değer / gelişim":             ("--arc-blue",   "#edf5ff", "#185ea8"),
    "Fizik motoru / tempo oyuncusu":    ("--arc-orange", "#fff6ed", "#b84f00"),
    "Sertlik ve temas profili":         ("--arc-slate",  "#f1f3f5", "#374151"),
    "Düşük riskli düzenli oyuncu":      ("--arc-green",  "#edf9f3", "#137a4b"),
    "Rotasyon fırsatı":                 ("--arc-gray",   "#f4f6f8", "#667085"),
}


def _score_maxes(candidates: list[dict]) -> dict:
    return {
        field: max((c.get(field) or 0 for c in candidates), default=1) or 1
        for field, _ in _SCORE_FIELDS
    }


def _norm(value: float, mx: float) -> int:
    return min(100, max(0, round(value / mx * 100)))


def _bar_color(pct: int) -> str:
    if pct >= 78:
        return "#137a4b"
    if pct >= 55:
        return "#0d9488"
    if pct >= 35:
        return "#b76b00"
    return "#adb5bd"


def _contract_badge(player: dict) -> str:
    risk = player.get("contract_risk", "")
    months = player.get("contract_months_left")
    end = player.get("contract_end", "")
    label = end[:7] if end else "?"
    if risk == "HIGH":
        return f'<span class="cbadge cbadge-high">⚠ {escape(label)}</span>'
    if risk == "MEDIUM":
        return f'<span class="cbadge cbadge-med">⌛ {escape(label)}</span>'
    if months and months <= 24:
        return f'<span class="cbadge cbadge-low">📅 {escape(label)}</span>'
    return f'<span class="cbadge cbadge-ok">📅 {escape(label)}</span>'


def _value_chip(player: dict) -> str:
    txt = player.get("tm_market_value_text") or ""
    if not txt or txt == "-":
        return ""
    url = player.get("tm_profile_url") or ""
    inner = f'<a href="{escape(url)}" target="_blank" rel="noopener" class="val-link">{escape(txt)}</a>' if url else escape(txt)
    return f'<span class="val-chip">{inner}</span>'


def _archetype_badge(archetype: str) -> str:
    _, bg, color = _ARCHETYPE_COLOR.get(archetype, ("", "#f4f6f8", "#667085"))
    return (
        f'<span class="arc-badge" style="background:{bg};color:{color};border-color:{color}22">'
        f'{escape(archetype)}</span>'
    )


_POS_ATTRS = {
    "FWD": ["finishing", "technique", "positioning", "decisions", "pace", "stamina"],
    "MID": ["passing", "decisions", "technique", "vision", "work_rate", "stamina"],
    "DEF": ["tackling", "decisions", "positioning", "stamina", "pace", "work_rate"],
    "GK":  ["decisions", "positioning", "stamina", "work_rate", "technique", "teamwork"],
}
_ATTR_LABELS = {
    "finishing": "Bitiricilik", "technique": "Teknik", "positioning": "Pozisyon",
    "decisions": "Karar Verme", "pace": "Hız", "stamina": "Kondisyon",
    "passing": "Pas", "vision": "Vizyon", "work_rate": "Çalışma Temposu",
    "tackling": "Müdahale", "teamwork": "Takım Oyunu", "acceleration": "İvme",
}


def _ca_color(ca: int) -> str:
    if ca >= 125:
        return "#137a4b"
    if ca >= 112:
        return "#0d9488"
    if ca >= 100:
        return "#b76b00"
    return "#adb5bd"


def _player_card(player: dict, active_field: str, maxes: dict) -> str:
    name = escape(player.get("name") or "")
    team = escape(player.get("team") or "")
    age = player.get("age") or "?"
    nat = escape(player.get("nationality") or "")
    goals = player.get("goals", 0)
    starts = player.get("starts", 0)
    cards = player.get("cards", 0)
    load_lo = player.get("estimated_physical_load_km_min", 0)
    load_hi = player.get("estimated_physical_load_km_max", 0)
    archetype = player.get("archetype", "Rotasyon fırsatı")

    attr_sig = player.get("attribute_signal") or {}
    raw = attr_sig.get("raw_attributes") or {}
    ca = attr_sig.get("current_ability")
    pa = attr_sig.get("potential_ability")
    pos_grp = (player.get("tm_position_group") or "MID").upper()

    # --- attribute barları ---
    if raw:
        attr_keys = _POS_ATTRS.get(pos_grp, _POS_ATTRS["MID"])
        bars = ""
        for key in attr_keys:
            val = raw.get(key)
            if val is None:
                continue
            val_int = int(round(val))
            pct = round(val / 20 * 100)
            clr = _attr_color(val_int)
            bars += (
                f'<div class="attr-row bar-active">'
                f'<span class="attr-lbl">{escape(_ATTR_LABELS.get(key, key))}</span>'
                f'<div class="bar-track">'
                f'<div class="bar-fill" style="width:{pct}%;background:{clr}"></div>'
                f'</div>'
                f'<span class="attr-val" style="color:{clr}">{val_int}</span>'
                f'</div>'
            )
        score_label = str(int(ca)) if ca else "?"
        ring_color = _ca_color(int(ca) if ca else 90)
        pa_html = (
            f'<span class="pa-chip">PA {int(pa)}</span>'
            if pa and pa > (ca or 0) + 2 else ""
        )
    else:
        # fallback: proxy skorlar
        active_pct = _norm(player.get(active_field) or 0, maxes[active_field])
        bars = ""
        for field, label in _SCORE_FIELDS:
            pct = _norm(player.get(field) or 0, maxes[field])
            clr = _bar_color(pct)
            is_active = "bar-active" if field == active_field else ""
            bars += (
                f'<div class="attr-row {is_active}">'
                f'<span class="attr-lbl">{escape(label)}</span>'
                f'<div class="bar-track"><div class="bar-fill" style="width:{pct}%;background:{clr}"></div></div>'
                f'<span class="attr-val" style="color:{clr}">{pct}</span>'
                f'</div>'
            )
        score_label = str(active_pct)
        ring_color = _bar_color(active_pct)
        pa_html = ""

    contract_html = _contract_badge(player)
    value_html = _value_chip(player)
    arc_html = _archetype_badge(archetype)

    return f"""<div class="pcard" style="--ring:{ring_color}">
  <div class="pcard-top">
    <div>
      <div class="pcard-name">{name}</div>
      <div class="pcard-meta">{team} · {age}y · {nat}</div>
    </div>
    <div class="pcard-score" style="color:{ring_color};border-color:{ring_color}33;background:{ring_color}12">{score_label}</div>
  </div>
  <div class="arc-row">{arc_html}{pa_html}</div>
  <div class="attrs">{bars}</div>
  <div class="pcard-stats">
    <span>⚽ <strong>{goals}</strong></span>
    <span>▶ <strong>{starts}</strong></span>
    <span>🟨 <strong>{cards}</strong></span>
    <span>🏃 <strong>{load_lo}–{load_hi}km</strong></span>
  </div>
  <div class="pcard-footer">{contract_html}{value_html}</div>
</div>"""


def _attr_color(val: int) -> str:
    if val >= 16:
        return "#137a4b"
    if val >= 13:
        return "#0d9488"
    if val >= 10:
        return "#b76b00"
    return "#adb5bd"


def build_html(payload: dict) -> str:
    all_candidates = payload["all_candidates"]
    maxes = _score_maxes(all_candidates)
    external_matched = sum(1 for c in all_candidates if c.get("external_api_signal", {}).get("matched"))

    tab_btns = ""
    tab_panels = ""
    for i, (key, (label, score_field)) in enumerate(_BUCKET_META.items()):
        players = payload["role_buckets"][key][:12]
        cards = "".join(_player_card(p, score_field, maxes) for p in players)
        active_cls = " active" if i == 0 else ""
        tab_btns += f'<button class="tab{active_cls}" data-tab="{key}">{label}</button>'
        tab_panels += f'<div class="tab-panel{active_cls}" id="tab-{key}"><div class="cards-grid">{cards}</div></div>'

    needs_rows = "".join(
        f"<tr><td><span class=\"pill {priority_class(item['priority'])}\">{escape(item['priority'])}</span></td>"
        f"<td>{escape(item['need'])}</td><td>{escape(item['reason'])}</td></tr>"
        for item in payload["team_needs"][:8]
    )

    return f"""<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{escape(payload['team'])} Scout Programı — metric11</title>
  <style>
    :root{{--bg:#f3f5f4;--panel:#fff;--ink:#132018;--muted:#627067;--line:#d7ded9;--dark:#091810;--green:#116447;--teal:#0d9488;--shadow:0 4px 16px rgba(9,24,16,.07);}}
    *{{box-sizing:border-box;margin:0;padding:0;}}
    body{{font-family:Inter,system-ui,sans-serif;background:var(--bg);color:var(--ink);}}

    /* topbar */
    .topbar{{position:sticky;top:0;z-index:10;display:flex;align-items:center;justify-content:space-between;gap:20px;min-height:58px;padding:0 clamp(14px,4vw,40px);background:#091810;border-bottom:2px solid #1a3023;}}
    .brand{{display:flex;gap:8px;align-items:center;font-weight:800;font-size:17px;color:white;text-decoration:none;}}
    .brand:visited,.brand:active,.brand:hover{{color:white;}}
    .brand-mark{{width:26px;height:26px;display:grid;place-items:center;border-radius:5px;color:#091810;background:#a3e635;font-size:13px;font-weight:900;}}
    nav{{display:flex;gap:2px;overflow-x:auto;scrollbar-width:none;}}
    nav::-webkit-scrollbar{{display:none;}}
    nav a{{color:#8fa89a;text-decoration:none;font-size:13px;font-weight:600;padding:8px 10px;border-radius:6px;white-space:nowrap;}}
    nav a:visited{{color:#8fa89a;}}
    nav a:hover,nav a.active{{background:#162b20;color:white;}}

    /* header */
    header{{background:var(--dark);color:white;padding:26px clamp(16px,4vw,40px) 22px;border-bottom:4px solid var(--green);}}
    header h1{{font-size:clamp(22px,3vw,30px);font-weight:800;letter-spacing:-.5px;margin-bottom:6px;}}
    header p{{color:#8fa89a;font-size:14px;max-width:780px;line-height:1.55;}}

    /* layout */
    main{{max-width:1380px;margin:0 auto;padding:20px clamp(12px,3vw,28px) 40px;}}

    /* summary pills */
    .summary-bar{{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:20px;}}
    .s-pill{{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:10px 16px;display:flex;flex-direction:column;gap:2px;min-width:120px;box-shadow:var(--shadow);}}
    .s-pill span{{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.05em;}}
    .s-pill strong{{font-size:24px;font-weight:800;color:var(--ink);}}

    /* needs table */
    .needs-section{{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px 18px;margin-bottom:22px;box-shadow:var(--shadow);}}
    .needs-section h2{{font-size:15px;font-weight:700;margin-bottom:12px;}}
    table{{width:100%;border-collapse:collapse;font-size:13px;}}
    th,td{{padding:8px 6px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top;}}
    th{{color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.05em;}}
    .pill{{display:inline-flex;align-items:center;border-radius:999px;padding:2px 9px;font-size:11px;font-weight:600;border:1px solid;}}
    .high{{color:#bf1f2f;background:#fff0f2;border-color:#efb7bf;}}
    .medium{{color:#b76b00;background:#fff7e8;border-color:#f2d09a;}}
    .low{{color:var(--green);background:#edf9f3;border-color:#b9dfcd;}}

    /* tabs */
    .tab-bar{{display:flex;gap:4px;overflow-x:auto;scrollbar-width:none;margin-bottom:16px;background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:5px;box-shadow:var(--shadow);}}
    .tab-bar::-webkit-scrollbar{{display:none;}}
    .tab{{flex-shrink:0;background:none;border:none;cursor:pointer;font-family:inherit;font-size:13px;font-weight:600;color:var(--muted);padding:8px 16px;border-radius:7px;transition:all .15s;}}
    .tab.active{{background:#0f2018;color:white;}}
    .tab:hover:not(.active){{background:#e8ede9;color:var(--ink);}}

    /* tab panels */
    .tab-panel{{display:none;}}
    .tab-panel.active{{display:block;}}

    /* cards grid */
    .cards-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px;}}

    /* player card */
    .pcard{{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px;box-shadow:var(--shadow);display:flex;flex-direction:column;gap:10px;border-top:3px solid var(--ring,var(--green));transition:box-shadow .15s;}}
    .pcard:hover{{box-shadow:0 8px 28px rgba(9,24,16,.13);}}
    .pcard-top{{display:flex;justify-content:space-between;align-items:flex-start;gap:8px;}}
    .pcard-name{{font-size:14px;font-weight:800;color:var(--ink);line-height:1.3;letter-spacing:-.2px;}}
    .pcard-meta{{font-size:12px;color:var(--muted);margin-top:2px;}}
    .pcard-score{{flex-shrink:0;width:42px;height:42px;border-radius:50%;display:grid;place-items:center;font-size:16px;font-weight:900;border:2px solid;}}

    /* archetype badge */
    .arc-badge{{display:inline-flex;align-items:center;border-radius:6px;padding:3px 8px;font-size:11px;font-weight:700;border:1px solid;letter-spacing:.02em;width:fit-content;}}

    /* attribute bars */
    .attrs{{display:flex;flex-direction:column;gap:5px;}}
    .attr-row{{display:grid;grid-template-columns:90px 1fr 28px;align-items:center;gap:6px;opacity:.65;transition:opacity .1s;}}
    .attr-row.bar-active{{opacity:1;}}
    .attr-lbl{{font-size:11px;color:var(--muted);font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}}
    .bar-track{{height:7px;background:#e8ede9;border-radius:99px;overflow:hidden;}}
    .bar-fill{{height:100%;border-radius:99px;transition:width .3s;}}
    .attr-val{{font-size:12px;font-weight:800;text-align:right;}}

    /* quick stats */
    .pcard-stats{{display:flex;gap:10px;flex-wrap:wrap;padding:8px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line);font-size:12px;color:var(--muted);}}
    .pcard-stats strong{{color:var(--ink);}}

    /* footer */
    .pcard-footer{{display:flex;align-items:center;gap:8px;flex-wrap:wrap;}}
    .cbadge{{font-size:11px;font-weight:700;padding:3px 8px;border-radius:6px;border:1px solid;}}
    .cbadge-high{{color:#bf1f2f;background:#fff0f2;border-color:#efb7bf;}}
    .cbadge-med{{color:#b76b00;background:#fff7e8;border-color:#f2d09a;}}
    .cbadge-low{{color:#0d9488;background:#f0fdfc;border-color:#99e6e0;}}
    .cbadge-ok{{color:var(--muted);background:#f4f6f8;border-color:var(--line);}}
    .val-chip{{font-size:11px;font-weight:700;color:var(--green);background:#edf9f3;border:1px solid #b9dfcd;padding:3px 8px;border-radius:6px;}}
    .val-link{{color:inherit;text-decoration:none;}}
    .val-link:hover{{text-decoration:underline;}}
    .arc-row{{display:flex;align-items:center;gap:6px;flex-wrap:wrap;}}
    .pa-chip{{font-size:11px;font-weight:700;color:#185ea8;background:#edf5ff;border:1px solid #bbd7f5;padding:3px 8px;border-radius:6px;}}

    @media(max-width:640px){{
      .cards-grid{{grid-template-columns:1fr;}}
      .summary-bar .s-pill{{min-width:90px;}}
    }}
  </style>
</head>
<body>
  <div class="topbar">
    <a class="brand" href="/"><span class="brand-mark">11</span> metric11</a>
    <nav>
      <a href="/">Gündem</a>
      <a href="transfer_tracker_2025_2026.html">Transferler</a>
      <a href="all_teams_preview_dashboard_2025_2026.html">Maç Önü</a>
      <a class="active" href="transfer_recommendation_report_2025_2026.html">Scout</a>
      <a href="football_intelligence_home.html">Analiz</a>
    </nav>
  </div>

  <header>
    <h1>{escape(payload['team'])} — Scout Programı</h1>
    <p>Rol bazlı FM tarzı aday listesi · Attribute barları lig içi aday havuzuna göre normalize edilmiştir · Fiziksel yük olay verisinden türetilmiş tahmin aralığıdır</p>
  </header>

  <main>
    <div class="summary-bar">
      {_s_pill("Aday", payload["summary"]["candidate_count"])}
      {_s_pill("Yüksek ihtiyaç", payload["summary"]["high_priority_needs"])}
      {_s_pill("Rol listesi", payload["summary"]["role_buckets"])}
      {_s_pill("Dış API eşleşmesi", external_matched)}
    </div>

    <div class="needs-section">
      <h2>Takım İhtiyaç Özeti</h2>
      <table><thead><tr><th>Öncelik</th><th>İhtiyaç</th><th>Gerekçe</th></tr></thead>
      <tbody>{needs_rows}</tbody></table>
    </div>

    <div class="tab-bar">{tab_btns}</div>
    {tab_panels}
  </main>

  <script>
    document.querySelectorAll('.tab').forEach(btn => {{
      btn.addEventListener('click', () => {{
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
        btn.classList.add('active');
        document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
      }});
    }});
  </script>
  <script defer src="/_vercel/insights/script.js"></script>
</body>
</html>"""


def _s_pill(label: str, value) -> str:
    return f'<div class="s-pill"><span>{escape(str(label))}</span><strong>{escape(str(value))}</strong></div>'


def priority_class(priority: str) -> str:
    v = priority.lower()
    if v == "high":
        return "high"
    if v == "medium":
        return "medium"
    return "low"


if __name__ == "__main__":
    main()
