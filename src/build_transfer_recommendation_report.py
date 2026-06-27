"""
Süper Lig transfer sezonu için takım bazlı oyuncu öneri raporu üretir.
Her takımın öncelikli pozisyon ihtiyacını, serbest/yakın sözleşmeli adayları
ve 'neden bu oyuncu' mantığını birleştirir.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.config import PROCESSED_DIR, SEASON, SEASON_LABEL
from src.build_team_scout_blueprints import candidate_matches_role
from src.html_utils import preview_nav_label

CONTRACT_URGENCY = {
    "EXPIRING_SOON": 40,
    "ONE_YEAR_WINDOW": 25,
    "TWO_YEAR_WINDOW": 10,
    "STABLE": 3,
}

TRANSFER_WINDOW_LABELS = {
    "EXPIRING_SOON": ("SERBEST TRANSFER FIRSATI", "Sözleşmesi bitiyor — ücretsiz veya sembolik bonusla"),
    "ONE_YEAR_WINDOW": ("MÜZAKERE PENCERESİ", "1 yıl kalan sözleşme — fiyat baskısı yüksek"),
    "TWO_YEAR_WINDOW": ("STANDART TRANSFER", "2 yıl kalan sözleşme — normal piyasa değeri"),
    "STABLE": ("PREMİUM TRANSFER", "Uzun sözleşme — yüksek bonusu göze almalı"),
}

PRIORITY_TIERS = [
    (56, "ACİL", "#dc2626"),
    (35, "YÜKSEK", "#d97706"),
    (20, "NORMAL", "#2563eb"),
    (0,  "STABİL", "#16a34a"),
]

COST_TIER_LABEL = {
    "FREE":   ("ÜCRETSİZ", "#16a34a"),
    "LOW":    ("DÜŞÜK BÜTÇE", "#22c55e"),
    "MEDIUM": ("ORTA BÜTÇE", "#d97706"),
    "HIGH":   ("YÜKSEK BÜTÇE", "#dc2626"),
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Transfer sezonu takim bazli oyuncu oneri raporu uretir.")
    parser.add_argument("--blueprints", default=str(PROCESSED_DIR / "team_scout_blueprints_2025_2026.json"))
    parser.add_argument("--output-prefix", default="transfer_recommendation_report_2025_2026")
    parser.add_argument("--top-candidates", type=int, default=3)
    parser.add_argument("--top-roles", type=int, default=3)
    args = parser.parse_args()

    blueprints_data = json.loads(Path(args.blueprints).read_text(encoding="utf-8"))
    report = build_report(blueprints_data, args.top_roles, args.top_candidates)

    json_path = PROCESSED_DIR / f"{args.output_prefix}.json"
    md_path = PROCESSED_DIR / f"{args.output_prefix}.md"
    html_path = PROCESSED_DIR / f"{args.output_prefix}.html"

    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(build_markdown(report), encoding="utf-8")
    html_path.write_text(build_html(report), encoding="utf-8")
    print(md_path.read_text(encoding="utf-8")[:4000])
    print(f"\nKaydedildi:\n  {json_path}\n  {md_path}\n  {html_path}")


def build_report(blueprints_data: dict, top_roles: int, top_candidates: int) -> dict:
    blueprints = blueprints_data.get("blueprints", [])
    team_reports = [build_team_plan(bp, top_roles, top_candidates) for bp in blueprints]
    team_reports.sort(key=lambda t: -t["priority_score"])
    market_alerts = build_market_alerts(blueprints)
    priority_ranking = build_priority_ranking(team_reports)
    age_curve = build_age_curve_analysis(blueprints)
    total_recommendations = sum(
        len(r["candidates"]) for t in team_reports for r in t["recommendations"]
    )
    return {
        "season": "2025/26",
        "generated_for": "transfer_window",
        "summary": {
            "teams_analyzed": len(team_reports),
            "total_role_needs": sum(len(t["recommendations"]) for t in team_reports),
            "total_candidate_suggestions": total_recommendations,
            "free_agent_opportunities": market_alerts["free_agent_count"],
            "negotiation_window_count": market_alerts["negotiation_window_count"],
            "urgent_teams": sum(1 for t in team_reports if t["priority_score"] >= 56),
            "publication_rule": "Rol önerileri yalnızca dış profil pozisyonu rol ile eşleşen oyuncuları içerir.",
        },
        "team_reports": team_reports,
        "market_alerts": market_alerts,
        "priority_ranking": priority_ranking,
        "age_curve": age_curve,
    }


def build_team_plan(blueprint: dict, top_roles: int, top_candidates: int) -> dict:
    team = blueprint["team"]
    team_ctx = {
        "ppm": blueprint.get("points_per_match") or 1.0,
        "gf": blueprint.get("goals_for_per_match") or 1.0,
        "ga": blueprint.get("goals_against_per_match") or 1.5,
        "weaknesses": blueprint.get("weaknesses", []),
    }
    role_plans = blueprint.get("role_plans", [])[:top_roles]
    recommendations = []
    for role_plan in role_plans:
        candidates_raw = [
            c for c in role_plan.get("top_candidates", [])
            if c.get("team") != team and published_role_candidate(c, role_plan["role_key"])
        ][:top_candidates + 2]
        scored = sorted(
            [score_candidate(c, role_plan, team_ctx) for c in candidates_raw],
            key=lambda c: -c["transfer_score"],
        )[:top_candidates]
        if scored:
            recommendations.append({
                "role_key": role_plan["role_key"],
                "role_label": role_plan["role_label"],
                "need_reason": role_plan["reason"],
                "candidates": scored,
            })
    return {
        "team": team,
        "points_per_match": blueprint.get("points_per_match"),
        "goals_for_per_match": blueprint.get("goals_for_per_match"),
        "goals_against_per_match": blueprint.get("goals_against_per_match"),
        "weaknesses": blueprint.get("weaknesses", []),
        "scout_hint": blueprint.get("scout_need_hint", ""),
        "recommendations": recommendations,
        "priority_score": _team_priority_score(blueprint),
        "priority_tier": _priority_tier_label(blueprint),
    }


def published_role_candidate(candidate: dict, role_key: str) -> bool:
    if not candidate_matches_role(candidate, role_key):
        return False
    if role_key in {"LOW_RISK_REGULAR", "RESALE_VALUE"}:
        return True
    return bool(candidate.get("verified_position"))


def build_priority_ranking(team_reports: list[dict]) -> list[dict]:
    rows = []
    for rank, tr in enumerate(team_reports, 1):
        tier_label, tier_color = _priority_tier_display(tr["priority_score"])
        top_role = tr["recommendations"][0]["role_label"] if tr["recommendations"] else "—"
        rows.append({
            "rank": rank,
            "team": tr["team"],
            "priority_score": tr["priority_score"],
            "tier": tier_label,
            "tier_color": tier_color,
            "points_per_match": tr["points_per_match"],
            "goals_for_per_match": tr["goals_for_per_match"],
            "goals_against_per_match": tr["goals_against_per_match"],
            "weakness_count": len(tr["weaknesses"]),
            "top_role_need": top_role,
        })
    return rows


def score_candidate(candidate: dict, role_plan: dict, team_ctx: dict) -> dict:
    contract_risk = candidate.get("contract_risk") or "STABLE"
    age = candidate.get("age") or 27
    goals = candidate.get("goals") or 0
    starts = candidate.get("starts") or 0
    fit = candidate.get("fit_score") or 100
    contract_months = candidate.get("contract_months_left") or 24
    resale = candidate.get("resale_signal") or "LOW"

    urgency = CONTRACT_URGENCY.get(contract_risk, 3)
    performance = min(50, goals * 3.5 + starts * 0.6)
    age_score = _age_score(age)
    fit_norm = min(40, fit / 5)
    formation_fit = _formation_fit_score(role_plan.get("role_key", ""), candidate.get("verified_position"))

    transfer_score = round(
        urgency * 0.30 + performance * 0.28 + age_score * 0.14 + fit_norm * 0.18 + (formation_fit / 100 * 40) * 0.10,
        1,
    )

    window_type, window_label = TRANSFER_WINDOW_LABELS.get(
        contract_risk, TRANSFER_WINDOW_LABELS["STABLE"]
    )
    cost_tier = _cost_tier(contract_risk, resale, age)
    narrative = _build_narrative(candidate, role_plan, team_ctx, contract_risk, age, goals, starts)

    result = {
        "name": candidate.get("name", ""),
        "current_team": candidate.get("team", ""),
        "age": age,
        "nationality": candidate.get("nationality", ""),
        "contract_months_left": contract_months,
        "contract_risk": contract_risk,
        "goals": goals,
        "starts": starts,
        "cards": candidate.get("cards") or 0,
        "fit_score": fit,
        "resale_signal": resale,
        "transfer_score": transfer_score,
        "transfer_window_type": window_type,
        "transfer_window_label": window_label,
        "cost_tier": cost_tier,
        "position_confidence": candidate.get("position_confidence", ""),
        "verified_position": candidate.get("verified_position"),
        "formation_fit": formation_fit,
        "market_value_eur": candidate.get("market_value_eur"),
        "market_value_text": candidate.get("market_value_text"),
        "tm_id": candidate.get("tm_id"),
        "narrative": narrative,
    }
    if candidate.get("height_cm"):
        result["height_cm"] = candidate["height_cm"]
    if candidate.get("preferred_foot"):
        result["preferred_foot"] = candidate["preferred_foot"]
    return result


_FORMATION_FIT: dict[str, dict[str, int]] = {
    # rol_key → pozisyon_anahtar_kelime → uyum_skoru (0-100)
    # Türkçe (TFF) + İngilizce (Transfermarkt) pozisyon adları
    "CB_DOMINANT": {
        "stoper": 100, "centre-back": 100, "center-back": 100,
        "merkez": 60, "central": 50,
        "bek": 40, "back": 35,
        "orta": 20, "kanat": 10, "forvet": 5, "forward": 5,
    },
    "CM_ENGINE": {
        "orta saha": 100, "central midfield": 100, "attacking midfield": 90,
        "merkez": 90,
        "kanat": 50, "winger": 45,
        "forvet": 30, "forward": 25,
        "bek": 20, "back": 15, "stoper": 10,
    },
    "DM_SECURITY": {
        "defensif": 100, "defensive midfield": 100, "holding": 90,
        "orta saha": 80, "central midfield": 70, "merkez": 70,
        "stoper": 40, "centre-back": 35,
        "bek": 30, "back": 25,
    },
    "ST_SCORER": {
        "forvet": 100, "santrfor": 100, "centre-forward": 100, "striker": 100,
        "kanat": 60, "winger": 55, "second striker": 80,
        "orta": 30, "midfield": 20,
    },
    "LW_CREATOR": {
        "kanat": 100, "sol kanat": 100, "winger": 100, "left winger": 100, "right winger": 90,
        "forvet": 70, "forward": 65,
        "orta": 50, "midfield": 45,
        "bek": 20, "wing-back": 40,
    },
    "FB_TWO_WAY": {
        "bek": 100, "back": 100, "left-back": 100, "right-back": 100, "wing-back": 90,
        "kanat": 60, "winger": 50,
        "orta": 30, "midfield": 25,
        "stoper": 20, "centre-back": 15,
    },
    "GK_STABILITY": {
        "kaleci": 100, "goalkeeper": 100,
    },
    "LOW_RISK_REGULAR": {
        "orta saha": 80, "midfield": 80, "central midfield": 80,
        "kanat": 70, "winger": 70,
        "forvet": 70, "forward": 70,
        "bek": 70, "back": 70,
        "stoper": 70, "centre-back": 70,
    },
    "RESALE_VALUE": {
        "forvet": 90, "forward": 90, "centre-forward": 90,
        "kanat": 90, "winger": 90,
        "orta saha": 80, "midfield": 80,
        "stoper": 70, "centre-back": 70,
        "bek": 70, "back": 70,
    },
}


def _formation_fit_score(role_key: str, verified_position: str | None) -> int:
    """Rol ihtiyacı × oyuncu pozisyonu → 0-100 formasyon uyum skoru."""
    if not verified_position:
        return 50  # bilinmiyor — nötr
    pos_lower = verified_position.lower()
    fit_map = _FORMATION_FIT.get(role_key, {})
    best = 0
    for keyword, score in fit_map.items():
        if keyword in pos_lower:
            best = max(best, score)
    return best if best else 35  # pozisyon var ama eşleşmedi — düşük uyum


def _age_score(age: int) -> float:
    if age <= 21:
        return 28.0
    if age <= 23:
        return 24.0
    if age <= 25:
        return 18.0
    if age <= 27:
        return 12.0
    if age <= 29:
        return 7.0
    if age <= 31:
        return 3.0
    return 0.0


def _cost_tier(contract_risk: str, resale: str, age: int) -> str:
    if contract_risk == "EXPIRING_SOON":
        return "FREE"
    if contract_risk == "ONE_YEAR_WINDOW":
        return "LOW" if (resale == "LOW" or age >= 29) else "MEDIUM"
    if contract_risk == "TWO_YEAR_WINDOW":
        return "MEDIUM"
    return "HIGH" if resale == "HIGH" else "MEDIUM"


def _priority_tier_label(blueprint: dict) -> str:
    score = _team_priority_score(blueprint)
    for threshold, label, _ in PRIORITY_TIERS:
        if score >= threshold:
            return label
    return "STABİL"


def _priority_tier_display(score: float) -> tuple[str, str]:
    for threshold, label, color in PRIORITY_TIERS:
        if score >= threshold:
            return label, color
    return "STABİL", "#16a34a"


def _build_narrative(
    candidate: dict,
    role_plan: dict,
    team_ctx: dict,
    contract_risk: str,
    age: int,
    goals: int,
    starts: int,
) -> str:
    gf = team_ctx["gf"]
    ga = team_ctx["ga"]
    weaknesses = team_ctx["weaknesses"]
    role_label = role_plan.get("role_label", "")
    need_reason = role_plan.get("reason", "")

    # Cümle 1: takım bağlamı
    if ga >= 1.5 and "savunma" in need_reason.lower():
        ctx = f"Savunma kırılgan (maç başına {ga} gol yedi) - {role_label} ihtiyacı net."
    elif gf <= 1.0:
        ctx = f"Gol üretimi zayıf (maç başına {gf} gol attı) - {role_label} pozisyonunda yaratıcılık gerekiyor."
    elif weaknesses:
        ctx = f"{weaknesses[0].capitalize()} sorunu var; {role_label} bu açığı kapatacak."
    else:
        ctx = f"{need_reason}."

    # Cümle 2: oyuncu profili
    name_short = candidate.get("name", "").split()[-1].capitalize()
    perf_parts = []
    if goals > 0:
        perf_parts.append(f"{goals} gol")
    if starts >= 20:
        perf_parts.append(f"{starts} maç")
    elif starts > 0:
        perf_parts.append(f"{starts} maçta sahada")

    perf_str = ", ".join(perf_parts) if perf_parts else "düzenli oyuncu profili"

    if contract_risk == "EXPIRING_SOON":
        mo = candidate.get("contract_months_left") or 1
        contract_str = f"Bu yaz serbest kalıyor (~{mo}ay) — bonussuz transfer fırsatı."
    elif contract_risk == "ONE_YEAR_WINDOW":
        contract_str = "1 yıllık sözleşme — bu yaz müzakere için en uygun pencere."
    elif contract_risk == "TWO_YEAR_WINDOW":
        contract_str = "2 yıl sözleşmesi var — standart bonusu gerektirir."
    else:
        contract_str = "Uzun sözleşme — yüksek bonusu göze almalı."

    age_str = ""
    if age <= 23:
        age_str = f" {age} yaş, uzun vadeli yatırım profili."
    elif age >= 32:
        age_str = f" {age} yaş — deneyim katkısı, kısa dönem çözüm."

    return f"{ctx} {name_short}: {perf_str}. {contract_str}{age_str}"


def _team_priority_score(blueprint: dict) -> float:
    ga = blueprint.get("goals_against_per_match") or 1.5
    gf = blueprint.get("goals_for_per_match") or 1.5
    ppm = blueprint.get("points_per_match") or 1.0
    weakness_count = len(blueprint.get("weaknesses", []))
    return round((3.0 - ppm) * 15 + (ga - 1.0) * 10 + (2.0 - gf) * 8 + weakness_count * 5, 1)


def build_age_curve_analysis(blueprints: list[dict]) -> dict:
    """Tüm adaylardan yaş eğrisi ve değer düşüş riski analizi üretir."""
    seen: dict[str, dict] = {}
    for bp in blueprints:
        for rp in bp.get("role_plans", []):
            for c in rp.get("top_candidates", []):
                pid = c.get("player_id") or c.get("name")
                if pid and pid not in seen:
                    seen[pid] = c

    all_candidates = list(seen.values())

    brackets = {"U21": [], "U24": [], "U27": [], "U30": [], "30+": []}
    for c in all_candidates:
        age = c.get("age") or 0
        if age <= 21:
            brackets["U21"].append(c)
        elif age <= 24:
            brackets["U24"].append(c)
        elif age <= 27:
            brackets["U27"].append(c)
        elif age <= 30:
            brackets["U30"].append(c)
        else:
            brackets["30+"].append(c)

    # Değer düşüş riski: 30+ yaş, market değeri var, kısa sözleşme
    value_cliff = sorted(
        [
            c for c in all_candidates
            if (c.get("age") or 0) >= 30
            and (c.get("market_value_eur") or 0) >= 1_000_000
            and c.get("contract_risk") in ("EXPIRING_SOON", "ONE_YEAR_WINDOW")
        ],
        key=lambda c: -(c.get("market_value_eur") or 0),
    )[:10]

    # Genç değer fırsatı: U23, yüksek fit, expiring
    young_value = sorted(
        [
            c for c in all_candidates
            if (c.get("age") or 99) <= 23
            and c.get("contract_risk") in ("EXPIRING_SOON", "ONE_YEAR_WINDOW")
        ],
        key=lambda c: -(c.get("fit_score") or 0),
    )[:10]

    def _bracket_summary(bracket_list: list[dict]) -> dict:
        if not bracket_list:
            return {"count": 0, "avg_value_m": 0.0, "expiring_count": 0}
        vals = [c.get("market_value_eur") or 0 for c in bracket_list]
        expiring = sum(1 for c in bracket_list if c.get("contract_risk") in ("EXPIRING_SOON", "ONE_YEAR_WINDOW"))
        return {
            "count": len(bracket_list),
            "avg_value_m": round(sum(vals) / len(vals) / 1_000_000, 2),
            "expiring_count": expiring,
        }

    return {
        "brackets": {k: _bracket_summary(v) for k, v in brackets.items()},
        "value_cliff_risk": [
            {
                "name": c.get("name", ""),
                "team": c.get("team", ""),
                "age": c.get("age"),
                "contract_risk": c.get("contract_risk"),
                "contract_months_left": c.get("contract_months_left"),
                "market_value_eur": c.get("market_value_eur"),
            }
            for c in value_cliff
        ],
        "young_value_opportunities": [
            {
                "name": c.get("name", ""),
                "team": c.get("team", ""),
                "age": c.get("age"),
                "contract_risk": c.get("contract_risk"),
                "fit_score": c.get("fit_score"),
                "market_value_eur": c.get("market_value_eur"),
            }
            for c in young_value
        ],
    }


def build_market_alerts(blueprints: list[dict]) -> dict:
    seen: dict[str, dict] = {}
    for bp in blueprints:
        for rp in bp.get("role_plans", []):
            for c in rp.get("top_candidates", []):
                pid = c.get("player_id") or c.get("name")
                if pid and pid not in seen:
                    seen[pid] = c

    all_candidates = list(seen.values())
    expiring = sorted(
        [c for c in all_candidates if c.get("contract_risk") == "EXPIRING_SOON"],
        key=lambda c: -(c.get("goals") or 0) - (c.get("starts") or 0) * 0.3,
    )
    negotiation = sorted(
        [c for c in all_candidates if c.get("contract_risk") == "ONE_YEAR_WINDOW"],
        key=lambda c: -(c.get("goals") or 0) - (c.get("starts") or 0) * 0.3,
    )
    young_expiring = [c for c in expiring if (c.get("age") or 99) <= 25]

    return {
        "free_agent_count": len(expiring),
        "negotiation_window_count": len(negotiation),
        "top_free_agents": _format_market_candidates(expiring[:10]),
        "top_negotiation_targets": _format_market_candidates(negotiation[:10]),
        "young_expiring_talents": _format_market_candidates(young_expiring[:8]),
    }


def _format_market_candidates(candidates: list[dict]) -> list[dict]:
    return [
        {
            "name": c.get("name", ""),
            "team": c.get("team", ""),
            "age": c.get("age"),
            "nationality": c.get("nationality", ""),
            "goals": c.get("goals") or 0,
            "starts": c.get("starts") or 0,
            "cards": c.get("cards") or 0,
            "contract_months_left": c.get("contract_months_left"),
            "contract_risk": c.get("contract_risk"),
            "resale_signal": c.get("resale_signal"),
            "fit_score": c.get("fit_score"),
        }
        for c in candidates
    ]


def build_markdown(report: dict) -> str:
    s = report["summary"]
    lines = [
        "# Süper Lig Transfer Tavsiye Raporu 2025/26",
        "",
        f"- Analiz edilen takım: {s['teams_analyzed']}",
        f"- Toplam pozisyon ihtiyacı: {s['total_role_needs']}",
        f"- Toplam oyuncu önerisi: {s['total_candidate_suggestions']}",
        f"- Acil transfer ihtiyacı olan takım: {s['urgent_teams']}",
        f"- Serbest transfer fırsatı: {s['free_agent_opportunities']} oyuncu",
        f"- Müzakere penceresi (1 yıl kalan): {s['negotiation_window_count']} oyuncu",
        f"- Yayın kuralı: {s['publication_rule']}",
        "",
        "## Transfer Aciliyet Sıralaması",
        "",
        "| Sıra | Takım | Öncelik | Skor | Puan/maç | Attığı gol/maç | Yediği gol/maç | İhtiyaç |",
        "|------|-------|------|------|-----|----|----|---------|",
    ]
    for row in report["priority_ranking"]:
        lines.append(
            f"| {row['rank']} | {row['team']} | {row['tier']} | {row['priority_score']} "
            f"| {row['points_per_match']} | {row['goals_for_per_match']} | {row['goals_against_per_match']} "
            f"| {row['top_role_need']} |"
        )
    lines.extend(["", "## Market Alarmları", "", "Bu liste sözleşme izlemesidir; takım/rol uygunluğu ayrıca doğrulanmış öneri bölümünde değerlendirilir.", "", "### En İyi Serbest Transfer Fırsatları", ""])
    for c in report["market_alerts"]["top_free_agents"][:8]:
        lines.append(
            f"- **{c['name']}** ({c['team']}) "
            f"| {c['age']}y | {c['goals']} gol / {c['starts']} maç "
            f"| sözleşme ~{c.get('contract_months_left', 0)}ay"
        )
    lines.extend(["", "### Müzakere Penceresi (1 Yıl Kalan)", ""])
    for c in report["market_alerts"]["top_negotiation_targets"][:8]:
        lines.append(
            f"- **{c['name']}** ({c['team']}) "
            f"| {c['age']}y | {c['goals']} gol / {c['starts']} maç"
        )
    lines.extend(["", "---", "", "## Takım Bazlı Öneriler", ""])
    for tr in report["team_reports"]:
        if not tr["recommendations"]:
            continue
        lines.extend([
            f"### {tr['team']}  [{tr['priority_tier']}]",
            f"*{tr['points_per_match']} puan/maç | maç başına {tr['goals_for_per_match']} attı | maç başına {tr['goals_against_per_match']} yedi*",
            "",
        ])
        if tr["weaknesses"]:
            lines.append(f"Zayıf nokta: {', '.join(tr['weaknesses'])}")
            lines.append("")
        for rec in tr["recommendations"]:
            lines.append(f"**{rec['role_label']}** — {rec['need_reason']}")
            for i, c in enumerate(rec["candidates"], 1):
                lines.append(
                    f"  {i}. {c['name']} ({c['current_team']}) | "
                    f"{c['age']}y | {c['goals']} gol | {c['transfer_window_type']} | {c['cost_tier']} | "
                    f"skor {c['transfer_score']}"
                )
                lines.append(f"     → {c['narrative']}")
            lines.append("")
    return "\n".join(lines)


def build_html(report: dict) -> str:
    s = report["summary"]
    market = report["market_alerts"]

    team_cards_html = _build_team_cards(report["team_reports"])
    ranking_table_html = _build_ranking_table(report["priority_ranking"])
    age_curve_html = _build_age_curve_html(report["age_curve"])

    def market_table(candidates: list[dict], title: str) -> str:
        rows = ""
        for c in candidates:
            risk_color = "#16a34a" if c.get("contract_risk") == "EXPIRING_SOON" else "#d97706"
            resale_icon = {"HIGH": "yüksek değer", "MEDIUM": "orta değer", "LOW": "kısa vade"}.get(c.get("resale_signal", ""), "")
            mv = c.get("market_value_eur")
            mv_str = f"€{mv / 1_000_000:.1f}M" if mv and mv >= 1_000_000 else (f"€{mv // 1000}K" if mv else "—")
            rows += (
                f"<tr>"
                f"<td><strong>{c['name']}</strong></td>"
                f"<td>{c['team']}</td>"
                f"<td>{c.get('age','')}</td>"
                f"<td>{c.get('nationality','')}</td>"
                f"<td>{c.get('goals',0)} gol / {c.get('starts',0)} maç / {c.get('cards',0)} kart</td>"
                f"<td style='color:{risk_color};font-weight:600'>{c.get('contract_months_left','')}ay</td>"
                f"<td>{resale_icon or 'belirsiz'}</td>"
                f"<td style='color:#fbbf24'>{mv_str}</td>"
                f"</tr>"
            )
        return (
            f"<div class='market-section'>"
            f"<h3>{title}</h3>"
            f"<div class='table-wrap'><table class='market-table'>"
            f"<thead><tr><th>Oyuncu</th><th>Takım</th><th>Yaş</th><th>Mil.</th>"
            f"<th>Performans</th><th>Sözleşme</th><th>Resale</th><th>Piyasa Değeri</th></tr></thead>"
            f"<tbody>{rows}</tbody>"
            f"</table></div></div>"
        )

    free_agent_table = market_table(market["top_free_agents"][:10], "Serbest Transfer Fırsatları (Biten Sözleşme)")
    negotiation_table = market_table(market["top_negotiation_targets"][:10], "Müzakere Penceresi (1 Yıl Kalan)")
    young_table = market_table(market["young_expiring_talents"][:8], "Genç Serbest Transfer Yetenekleri (25 Yaş ve Altı)")

    return f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Scout Raporu — Süper Lig {SEASON_LABEL} | metric11</title>
<meta name="description" content="Süper Lig takımlarına pozisyon bazlı transfer önerileri: piyasa değeri, sözleşme durumu ve performans analizi — metric11.">
<meta property="og:title" content="Scout Raporu — Süper Lig {SEASON_LABEL} | metric11">
<meta property="og:description" content="Süper Lig takımlarına pozisyon bazlı transfer önerileri: piyasa değeri, sözleşme durumu ve performans analizi.">
<meta property="og:image" content="https://metric11.com/og_transfer_recommendation.png">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:image" content="https://metric11.com/og_transfer_recommendation.png">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: Inter, 'Segoe UI', Arial, sans-serif; background: #07150e; color: #e2e8f0; min-height: 100vh; }}
  .topbar {{ min-height:58px; padding:0 clamp(14px,3vw,32px); display:flex; align-items:center; justify-content:space-between; gap:18px; background:#091810; border-bottom:2px solid #1a3023; }}
  .brand {{ display:flex; align-items:center; gap:10px; color:#fff; text-decoration:none; font-size:18px; font-weight:800; letter-spacing:-0.2px; }}
  .brand:visited,.brand:active,.brand:hover {{ color:#fff; }}
  .brand b {{ width:28px; height:28px; border-radius:6px; display:grid; place-items:center; color:#091810; background:#cde94e; font-size:14px; font-weight:900; }}
  .brand .slbl {{ color:#6b7c72; font-size:11px; font-weight:500; border-left:1px solid #2a3d30; padding-left:8px; margin-left:2px; }}
  .topnav {{ display:flex; gap:2px; overflow-x:auto; overflow-y:hidden; -webkit-overflow-scrolling:touch; scrollbar-width:none; }}
  .topnav::-webkit-scrollbar {{ display:none; }}
  .topnav a {{ color:#8fa89a; text-decoration:none; font-size:13px; font-weight:600; white-space:nowrap; flex-shrink:0; padding:8px 11px; border-radius:6px; transition:background .15s,color .15s; }}
  .topnav a:visited {{ color:#8fa89a; }}
  .topnav a:hover {{ background:#162b20; color:#fff; }}
  .topnav a.active {{ background:#162b20; color:#fff; }}
  .header {{ background:#102419; border-bottom:3px solid #116447; padding:24px clamp(14px,3vw,32px); }}
  .header h1 {{ font-size: 1.6rem; font-weight: 700; color: #f8fafc; }}
  .header .subtitle {{ color: #94a3b8; margin-top: 4px; font-size: 0.9rem; }}
  .summary-bar {{ display:grid; grid-template-columns:repeat(6,minmax(0,1fr)); gap:10px; padding:18px clamp(12px,3vw,32px); background:#0b1c13; }}
  .stat-pill {{ background:#102419; border:1px solid #294237; border-radius:8px; padding:11px 14px; min-height:75px; }}
  .stat-pill .val {{ font-size:1.45rem; font-weight:700; color:#cde94e; }}
  .stat-pill .lbl {{ font-size: 0.75rem; color: #64748b; margin-top: 2px; }}
  .tabs {{ display:flex; gap:0; padding:0 clamp(12px,3vw,32px); background:#102419; border-bottom:1px solid #294237; overflow-x:auto; }}
  .tab {{ padding: 12px 20px; cursor: pointer; font-size: 0.85rem; color: #94a3b8; border-bottom: 2px solid transparent; white-space: nowrap; transition: all 0.15s; }}
  .tab:hover {{ color: #e2e8f0; }}
  .tab.active {{ color:#cde94e; border-bottom-color:#cde94e; font-weight:600; }}
  .content {{ padding:22px clamp(12px,3vw,32px) 40px; max-width:1400px; margin:0 auto; }}
  .section {{ display: none; }}
  .section.active {{ display: block; }}
  .team-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(min(100%,520px),1fr)); gap:16px; }}
  .team-card {{ background: #1e293b; border: 1px solid #334155; border-radius: 12px; overflow: hidden; }}
  .team-header {{ padding: 16px 20px; background: #0f172a; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; }}
  .team-name {{ font-weight: 700; font-size: 0.95rem; color: #f1f5f9; }}
  .team-stats {{ font-size: 0.78rem; color: #64748b; }}
  .team-weakness {{ padding: 8px 20px; font-size: 0.78rem; color: #fbbf24; background: rgba(251,191,36,0.05); border-bottom: 1px solid #334155; }}
  .role-block {{ padding: 16px 20px; border-bottom: 1px solid #1e293b; }}
  .role-title {{ font-weight:600; font-size:0.88rem; color:#cde94e; margin-bottom:4px; }}
  .role-reason {{ font-size: 0.78rem; color: #64748b; margin-bottom: 12px; }}
  .candidate {{ background: #0f172a; border: 1px solid #1e293b; border-radius: 8px; padding: 12px 14px; margin-bottom: 8px; }}
  .cand-header {{ display: flex; justify-content: space-between; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 4px; }}
  .cand-name {{ font-weight: 600; font-size: 0.88rem; color: #f1f5f9; }}
  .badge {{ padding: 3px 8px; border-radius: 4px; font-size: 0.68rem; font-weight: 700; color: #fff; white-space: nowrap; }}
  .cand-meta {{ font-size: 0.75rem; color: #94a3b8; margin-bottom: 4px; }}
  .cand-narrative {{ font-size:0.76rem; color:#78d49e; margin-bottom:3px; line-height:1.4; }}
  .cand-contract {{ font-size: 0.72rem; color: #64748b; font-style: italic; }}
  .market-section {{ margin-bottom: 32px; }}
  .market-section h3 {{ font-size: 1rem; font-weight: 600; color: #f1f5f9; margin-bottom: 14px; padding-bottom: 8px; border-bottom: 1px solid #334155; }}
  .market-table {{ width: 100%; border-collapse: collapse; font-size: 0.82rem; }}
  .table-wrap {{ width:100%; overflow-x:auto; border:1px solid #24382e; border-radius:8px; }}
  .table-wrap table {{ min-width:720px; }}
  .market-table th {{ background: #0f172a; padding: 10px 12px; text-align: left; color: #64748b; font-weight: 600; border-bottom: 1px solid #334155; }}
  .market-table td {{ padding: 9px 12px; border-bottom: 1px solid #1e293b; color: #cbd5e1; }}
  .market-table tr:hover td {{ background: #1e293b; }}
  .ranking-table {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; margin-top: 4px; }}
  .ranking-table th {{ background: #0f172a; padding: 11px 14px; text-align: left; color: #64748b; font-weight: 600; border-bottom: 1px solid #334155; }}
  .ranking-table td {{ padding: 10px 14px; border-bottom: 1px solid #1e293b; color: #cbd5e1; }}
  .ranking-table tr:hover td {{ background: #1e293b; }}
  .tier-badge {{ padding: 3px 10px; border-radius: 20px; font-size: 0.72rem; font-weight: 700; color: #fff; }}
  .score-bar-wrap {{ display: flex; align-items: center; gap: 8px; }}
  .score-bar {{ height: 6px; border-radius: 3px; background: #334155; flex: 1; max-width: 120px; }}
  .score-bar-fill {{ height: 100%; border-radius: 3px; }}
  .filter-bar {{ display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }}
  .filter-input {{ background: #1e293b; border: 1px solid #334155; border-radius: 6px; padding: 8px 14px; color: #e2e8f0; font-size: 0.85rem; outline: none; min-width: 200px; }}
  .filter-input:focus {{ border-color:#cde94e; }}
  @media (max-width:900px) {{ .summary-bar {{ grid-template-columns:repeat(3,minmax(0,1fr)); }} }}
  @media (max-width:600px) {{ .topbar {{ flex-direction:column; align-items:stretch; padding:11px 12px 0; gap:0; min-height:unset; }} .brand {{ padding-bottom:8px; }} .topnav {{ border-top:1px solid #1e3228; padding:7px 0 9px; justify-content:flex-start; }} .summary-bar {{ grid-template-columns:repeat(2,minmax(0,1fr)); }} .team-grid {{ grid-template-columns:1fr; }} .content {{ padding:14px 12px 32px; }} }}
  .x-share {{ display:inline-flex; align-items:center; gap:8px; background:#000; color:#fff; text-decoration:none; font-size:14px; font-weight:700; padding:10px 18px; border-radius:8px; transition:background .15s; }}
  .x-share:hover {{ background:#1a1a1a; }}
  .share-bar {{ padding:16px 0 8px; border-top:1px solid #334155; margin-top:24px; }}
</style>
</head>
<body>
<div class="topbar">
  <a class="brand" href="/"><b>11</b> metric11<span class="slbl">Süper Lig 2025/26</span></a>
  <nav class="topnav"><a href="/">Gündem</a><a href="transfer_tracker_2025_2026.html">Transferler</a><a href="all_teams_preview_dashboard_2025_2026.html">{preview_nav_label()}</a><a class="active" href="transfer_recommendation_report_2025_2026.html">Scout</a><a href="football_intelligence_home.html">Analiz</a>
    <a href="worldcup_2026_predictions.html">🌍 WC 2026</a></nav>
</div>
<div class="header">
  <h1>Scout ve transfer merkezi</h1>
  <div class="subtitle">Süper Lig 2025/26 · takım ihtiyaçları · sözleşme pencereleri · pozisyonu doğrulanmış aday önerileri</div>
</div>
<div class="summary-bar">
  <div class="stat-pill"><div class="val">{s['teams_analyzed']}</div><div class="lbl">Takım</div></div>
  <div class="stat-pill"><div class="val">{s['total_role_needs']}</div><div class="lbl">Öncelikli Pozisyon</div></div>
  <div class="stat-pill"><div class="val">{s['total_candidate_suggestions']}</div><div class="lbl">Oyuncu Önerisi</div></div>
  <div class="stat-pill"><div class="val" style="color:#dc2626">{s['urgent_teams']}</div><div class="lbl">Acil Takım</div></div>
  <div class="stat-pill"><div class="val" style="color:#16a34a">{s['free_agent_opportunities']}</div><div class="lbl">Serbest Transfer</div></div>
  <div class="stat-pill"><div class="val" style="color:#d97706">{s['negotiation_window_count']}</div><div class="lbl">Müzakere Penceresi</div></div>
</div>
<div class="tabs">
  <div class="tab active" onclick="showTab('ranking',this)">Lig Sıralaması</div>
  <div class="tab" onclick="showTab('teams',this)">Takım Planları</div>
  <div class="tab" onclick="showTab('market',this)">Market Alarmları</div>
  <div class="tab" onclick="showTab('agecurve',this)">Yaş Eğrisi</div>
</div>
<div class="content">
  <div id="ranking" class="section active">
    {ranking_table_html}
  </div>
  <div id="teams" class="section">
    <div class="filter-bar">
      <input class="filter-input" id="teamFilter" placeholder="Takım ara..." oninput="filterTeams()" />
    </div>
    <div class="team-grid" id="teamGrid">
      {team_cards_html}
    </div>
  </div>
  <div id="market" class="section">
    {free_agent_table}
    {negotiation_table}
    {young_table}
  </div>
  <div id="agecurve" class="section">
    {age_curve_html}
  </div>
  <div class="share-bar">
    <a class="x-share" href="https://twitter.com/intent/tweet?text=S%C3%BCper%20Lig%20transfer%20radar%20%F0%9F%94%8D%20Hangi%20tak%C4%B1m%20kime%20ihtiya%C3%A7%20duyuyor%3F%20Veri%20destekli%20scout%20%C3%B6nerileri%3A&url=https%3A%2F%2Fmetric11.com%2Ftransfer_recommendation_report_2025_2026.html" target="_blank" rel="noopener">&#x1D54F; Paylaş</a>
  </div>
</div>
<script>
function showTab(id, el) {{
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  el.classList.add('active');
}}
function filterTeams() {{
  const q = document.getElementById('teamFilter').value.toLowerCase();
  document.querySelectorAll('.team-card').forEach(card => {{
    const name = (card.dataset.team || '').toLowerCase();
    card.style.display = name.includes(q) ? '' : 'none';
  }});
}}
</script>
  <footer style="text-align:center;padding:40px 16px 28px;color:#8a9e92;font-size:12px;border-top:1px solid #e2e8e4;margin-top:48px;">
    metric11 &middot; <a href="mailto:hello@metric11.com" style="color:#8a9e92;text-decoration:none;border-bottom:1px solid #c5d4ca;">hello@metric11.com</a>
  </footer>
  <script defer src="/_vercel/insights/script.js"></script>
</body>
</html>"""


def _build_team_cards(team_reports: list[dict]) -> str:
    html = ""
    for tr in team_reports:
        if not tr["recommendations"]:
            continue
        weakness_str = " · ".join(tr["weaknesses"]) if tr["weaknesses"] else "Genel yeterli"
        tier_label, tier_color = _priority_tier_display(tr["priority_score"])
        roles_html = ""
        for rec in tr["recommendations"]:
            cands_html = ""
            for c in rec["candidates"]:
                badge_color = {
                    "SERBEST TRANSFER FIRSATI": "#16a34a",
                    "MÜZAKERE PENCERESİ": "#d97706",
                    "STANDART TRANSFER": "#2563eb",
                    "PREMİUM TRANSFER": "#7c3aed",
                }.get(c["transfer_window_type"], "#64748b")
                cost_label, cost_color = COST_TIER_LABEL.get(c["cost_tier"], ("ORTA BÜTÇE", "#d97706"))
                extra_meta = ""
                if c.get("height_cm"):
                    extra_meta += f" · {c['height_cm']}cm"
                if c.get("preferred_foot"):
                    extra_meta += f" · {c['preferred_foot']} ayak"
                resale_icon = {"HIGH": "yüksek değer", "MEDIUM": "orta değer", "LOW": "kısa vade"}.get(c.get("resale_signal", ""), "")
                cands_html += (
                    f"<div class='candidate'>"
                    f"<div class='cand-header'>"
                    f"<span class='cand-name'>{c['name']}</span>"
                    f"<span style='display:flex;gap:4px;flex-wrap:wrap'>"
                    f"<span class='badge' style='background:{badge_color}'>{c['transfer_window_type']}</span>"
                    f"<span class='badge' style='background:{cost_color}'>{cost_label}</span>"
                    f"</span>"
                    f"</div>"
                    f"<div class='cand-meta'>{c['current_team']} · {c['age']}y · {c.get('nationality','')} · "
                    f"{c['goals']} gol / {c['starts']} maç / {c['cards']} kart{extra_meta} · "
                    f"skor {c['transfer_score']} {resale_icon}"
                    f"{_market_value_inline(c)}{_formation_fit_inline(c)}</div>"
                    f"<div class='cand-narrative'>{c['narrative']}</div>"
                    f"<div class='cand-contract'>{c['transfer_window_label']}</div>"
                    f"</div>"
                )
            roles_html += (
                f"<div class='role-block'>"
                f"<div class='role-title'>{rec['role_label']}</div>"
                f"<div class='role-reason'>{rec['need_reason']}</div>"
                f"{cands_html}"
                f"</div>"
            )
        html += (
            f"<div class='team-card' data-team='{tr['team']}'>"
            f"<div class='team-header'>"
            f"<span class='team-name'>{tr['team']}</span>"
            f"<span style='display:flex;gap:6px;align-items:center'>"
            f"<span class='tier-badge' style='background:{tier_color}'>{tier_label}</span>"
            f"<span class='team-stats'>{tr['points_per_match']} puan/maç · {tr['goals_for_per_match']} gol attı/maç · {tr['goals_against_per_match']} gol yedi/maç</span>"
            f"</span>"
            f"</div>"
            f"<div class='team-weakness'>Zayıf alan: {weakness_str}</div>"
            f"{roles_html}"
            f"</div>"
        )
    return html


def _market_value_inline(candidate: dict) -> str:
    val = candidate.get("market_value_eur")
    if not val:
        return ""
    if val >= 1_000_000:
        text = f"€{val / 1_000_000:.1f}M"
    else:
        text = f"€{val // 1000}K"
    return f" · <span style='color:#fbbf24;font-weight:600'>{text}</span>"


def _formation_fit_inline(candidate: dict) -> str:
    fit = candidate.get("formation_fit")
    if fit is None:
        return ""
    if fit >= 80:
        color, label = "#16a34a", "formasyon uyumu yüksek"
    elif fit >= 50:
        color, label = "#d97706", "formasyon uyumu orta"
    else:
        color, label = "#dc2626", "formasyon uyumu düşük"
    return f" · <span style='color:{color};font-size:0.8em' title='{label} ({fit}/100)'>⬡{fit}</span>"


def _build_ranking_table(ranking: list[dict]) -> str:
    rows = ""
    max_score = ranking[0]["priority_score"] if ranking else 70
    for row in ranking:
        tier_label, tier_color = _priority_tier_display(row["priority_score"])
        bar_width = round(row["priority_score"] / max_score * 100)
        rows += (
            f"<tr>"
            f"<td style='color:#64748b;font-weight:600'>{row['rank']}</td>"
            f"<td style='font-weight:600;color:#f1f5f9'>{row['team']}</td>"
            f"<td><span class='tier-badge' style='background:{tier_color}'>{tier_label}</span></td>"
            f"<td>"
            f"<div class='score-bar-wrap'>"
            f"<span style='color:{tier_color};font-weight:700;min-width:38px'>{row['priority_score']}</span>"
            f"<div class='score-bar'><div class='score-bar-fill' style='width:{bar_width}%;background:{tier_color}'></div></div>"
            f"</div>"
            f"</td>"
            f"<td>{row['points_per_match']}</td>"
            f"<td>{row['goals_for_per_match']}</td>"
            f"<td>{row['goals_against_per_match']}</td>"
            f"<td style='color:#64748b'>{row['weakness_count']}</td>"
            f"<td style='color:#94a3b8;font-size:0.8rem'>{row['top_role_need']}</td>"
            f"</tr>"
        )
    return (
        "<h2 style='color:#f1f5f9;margin-bottom:16px'>Transfer Aciliyet Sıralaması</h2>"
        "<p style='color:#64748b;font-size:0.82rem;margin-bottom:20px'>"
        "Acil skoru; puan/maç, gol yeme, gol üretimi ve zayıflık sayısına göre hesaplanır. "
        "Yüksek skor = bu yaz daha fazla kadro ihtiyacı.</p>"
        "<div class='table-wrap'><table class='ranking-table'>"
        "<thead><tr>"
        "<th>#</th><th>Takım</th><th>Öncelik</th><th>Aciliyet Skoru</th>"
        "<th>Puan/maç</th><th>Attığı gol/maç</th><th>Yediği gol/maç</th><th>Zayıflık</th><th>İlk İhtiyaç</th>"
        "</tr></thead>"
        f"<tbody>{rows}</tbody>"
        "</table></div>"
    )


def _build_age_curve_html(age_curve: dict) -> str:
    brackets = age_curve.get("brackets", {})
    cliff = age_curve.get("value_cliff_risk", [])
    young = age_curve.get("young_value_opportunities", [])

    BRACKET_ORDER = ["U21", "U24", "U27", "U30", "30+"]
    BRACKET_COLORS = {"U21": "#22c55e", "U24": "#84cc16", "U27": "#eab308", "U30": "#f97316", "30+": "#ef4444"}

    bracket_cards = ""
    for b in BRACKET_ORDER:
        info = brackets.get(b, {})
        color = BRACKET_COLORS[b]
        bracket_cards += (
            f"<div style='background:#0f172a;border:1px solid #1e293b;border-radius:8px;padding:14px 18px;flex:1;min-width:110px;text-align:center'>"
            f"<div style='font-size:20px;font-weight:700;color:{color}'>{info.get('count', 0)}</div>"
            f"<div style='font-size:12px;color:#64748b;margin:2px 0'>{b}</div>"
            f"<div style='font-size:11px;color:#94a3b8'>ort. €{info.get('avg_value_m', 0):.1f}M</div>"
            f"<div style='font-size:10px;color:#d97706'>{info.get('expiring_count', 0)} sözleşme riski</div>"
            f"</div>"
        )

    def _cliff_row(c: dict) -> str:
        mv = c.get("market_value_eur") or 0
        mv_str = f"€{mv / 1_000_000:.1f}M" if mv >= 1_000_000 else f"€{mv // 1000}K"
        risk_color = "#dc2626" if c.get("contract_risk") == "EXPIRING_SOON" else "#d97706"
        return (
            f"<tr><td><strong style='color:#f1f5f9'>{c['name']}</strong></td>"
            f"<td style='color:#94a3b8'>{c['team']}</td>"
            f"<td style='color:#f97316'>{c['age']}</td>"
            f"<td style='color:{risk_color};font-weight:600'>{c.get('contract_months_left','')}ay</td>"
            f"<td style='color:#fbbf24'>{mv_str}</td></tr>"
        )

    def _young_row(c: dict) -> str:
        mv = c.get("market_value_eur") or 0
        mv_str = f"€{mv / 1_000_000:.1f}M" if mv >= 1_000_000 else (f"€{mv // 1000}K" if mv else "—")
        risk_label = "Serbest" if c.get("contract_risk") == "EXPIRING_SOON" else "1 yıl"
        return (
            f"<tr><td><strong style='color:#f1f5f9'>{c['name']}</strong></td>"
            f"<td style='color:#94a3b8'>{c['team']}</td>"
            f"<td style='color:#22c55e'>{c['age']}</td>"
            f"<td style='color:#16a34a;font-weight:600'>{risk_label}</td>"
            f"<td style='color:#fbbf24'>{mv_str}</td></tr>"
        )

    cliff_rows = "".join(_cliff_row(c) for c in cliff) or "<tr><td colspan='5' style='color:#64748b;padding:12px'>Veri yok</td></tr>"
    young_rows = "".join(_young_row(c) for c in young) or "<tr><td colspan='5' style='color:#64748b;padding:12px'>Veri yok</td></tr>"
    tbl_header = "<thead><tr><th>Oyuncu</th><th>Takım</th><th>Yaş</th><th>Sözleşme</th><th>Piyasa Değeri</th></tr></thead>"

    return (
        "<h2 style='color:#f1f5f9;margin-bottom:8px'>Yaş Eğrisi Analizi</h2>"
        "<p style='color:#64748b;font-size:0.82rem;margin-bottom:20px'>"
        "Lig genelindeki aday havuzunun yaş dağılımı, değer düşüş riski ve genç fırsat profili.</p>"
        f"<div style='display:flex;gap:10px;flex-wrap:wrap;margin-bottom:28px'>{bracket_cards}</div>"
        "<h3 style='color:#ef4444;margin-bottom:10px'>Değer Düşüş Riski (30+ Yaş + Kısa Sözleşme)</h3>"
        "<p style='color:#64748b;font-size:0.8rem;margin-bottom:12px'>Piyasa değeri yüksek ancak sözleşmesi biten veya 1 yıl kalan 30+ yaş oyuncular — değer penceresi kapanmadan satış veya uzatma kararı verilmeli.</p>"
        "<div class='table-wrap' style='margin-bottom:28px'><table class='market-table'>"
        f"{tbl_header}<tbody>{cliff_rows}</tbody></table></div>"
        "<h3 style='color:#22c55e;margin-bottom:10px'>Genç Değer Fırsatları (23 Yaş Altı + Expiring)</h3>"
        "<p style='color:#64748b;font-size:0.8rem;margin-bottom:12px'>Sözleşmesi biten veya 1 yıl kalan U23 oyuncular — düşük bonusla edinme fırsatı.</p>"
        "<div class='table-wrap'><table class='market-table'>"
        f"{tbl_header}<tbody>{young_rows}</tbody></table></div>"
    )


if __name__ == "__main__":
    main()
