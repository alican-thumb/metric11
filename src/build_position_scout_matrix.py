from __future__ import annotations

import argparse
import json
from html import escape
from pathlib import Path

from src.config import PROCESSED_DIR, TRANSFER_WATCH_SEASON_LABEL

ROLE_REQUIREMENTS = {
    "LW_CREATOR": {
        "label": "Kanat / çizgi kırıcı",
        "position_group": "FWD",
        "verified_positions": {"Left Winger", "Right Winger", "Attacking Midfield"},
        "reason": "Kanat üretimi ve açık alan tehdidi için Süper Lig aday havuzu.",
    },
    "ST_SCORER": {
        "label": "Santrfor / skor yükü",
        "position_group": "FWD",
        "verified_positions": {"Centre-Forward", "Second Striker"},
        "reason": "Dar maçlarda gol olasılığını artıracak direkt skor profili.",
    },
    "CM_ENGINE": {
        "label": "8 numara / fizik motoru",
        "position_group": "MID",
        "verified_positions": {"Central Midfield", "Defensive Midfield", "Attacking Midfield"},
        "reason": "Pres, geçiş ve ikinci top sürekliliğini taşıyacak merkez orta saha.",
    },
    "DM_SECURITY": {
        "label": "6 numara / savunma emniyeti",
        "position_group": "MID",
        "verified_positions": {"Defensive Midfield", "Central Midfield"},
        "reason": "Savunma önü denge ve kart/tempo yönetimi için güvenli profil.",
    },
    "FB_TWO_WAY": {
        "label": "Bek / çift yönlü koridor",
        "position_group": "DEF",
        "verified_positions": {"Left-Back", "Right-Back", "Left Midfield", "Right Midfield"},
        "reason": "Kanat savunması ve bindirme sürekliliği için ekonomik bek profili.",
    },
    "CB_DOMINANT": {
        "label": "Stoper / hava ve temas",
        "position_group": "DEF",
        "verified_positions": {"Centre-Back"},
        "reason": "Duran top, hava topu ve temas yoğunluğu için savunma profili.",
    },
    "GK_STABILITY": {
        "label": "Kaleci / istikrar",
        "position_group": "GK",
        "verified_positions": {"Goalkeeper"},
        "reason": "Rotasyon ve güvenli kadro planı için kaleci profili.",
    },
}

_ARCHETYPE_GROUP = {
    "Bitirici / skor yükü": "FWD",
    "Genç değer / gelişim": "FWD",
    "Fizik motoru / tempo oyuncusu": "MID",
    "Sertlik ve temas profili": "DEF",
    "Düşük riskli düzenli oyuncu": "DEF",
}

_EXT_POS_GROUP = {
    "Forward": "FWD",
    "Attacker": "FWD",
    "Midfielder": "MID",
    "Defender": "DEF",
    "Goalkeeper": "GK",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Pozisyon bazlı scout matrisi üretir.")
    parser.add_argument("--scout", default=str(PROCESSED_DIR / "fm_style_scout_program_2025_2026.json"))
    parser.add_argument("--output-prefix", default="position_scout_matrix_2025_2026")
    args = parser.parse_args()

    scout = json.loads(Path(args.scout).read_text(encoding="utf-8"))
    payload = build_payload(scout)

    prefix = args.output_prefix
    (PROCESSED_DIR / f"{prefix}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (PROCESSED_DIR / f"{prefix}.md").write_text(build_markdown(payload), encoding="utf-8")
    (PROCESSED_DIR / f"{prefix}.html").write_text(build_html(payload), encoding="utf-8")
    print(f"{payload['summary']['matched_role_candidates']} rol-aday eşleşmesi, HTML yazıldı.")


def _infer_group(candidate: dict) -> tuple[str, str]:
    """Return (position_group, confidence) using multi-signal fallback."""
    # 1. Transfermarkt group
    tm_group = candidate.get("tm_position_group") or ""
    if tm_group in {"GK", "DEF", "MID", "FWD"}:
        return tm_group, "HIGH"

    # 2. External API position
    ext_pos = (candidate.get("external_api_signal") or {}).get("position") or ""
    mapped = _EXT_POS_GROUP.get(ext_pos)
    if mapped:
        return mapped, "MEDIUM"

    # 3. Archetype
    archetype = candidate.get("archetype") or ""
    arch_group = _ARCHETYPE_GROUP.get(archetype)
    if arch_group:
        return arch_group, "DERIVED"

    # 4. Stats-based heuristics
    goals = candidate.get("goals", 0)
    starts = candidate.get("starts", 0)
    cards = candidate.get("cards", 0)

    if goals >= 10:
        return "FWD", "DERIVED"
    if goals >= 6:
        return "FWD", "LOW"
    if cards >= 7 and goals <= 3:
        return "DEF", "LOW"
    if starts >= 20 and goals <= 2:
        return "DEF", "LOW"

    return "UNKNOWN", "VERY_LOW"


def _candidate_matches_role(candidate: dict, role: dict) -> tuple[bool, float]:
    """Returns (matches, group_match_multiplier)."""
    tm_pos = candidate.get("tm_position")
    if tm_pos:
        if tm_pos in role["verified_positions"]:
            return True, 1.0
        return False, 0.0

    group, confidence = _infer_group(candidate)
    if group == role["position_group"]:
        multiplier = {"HIGH": 1.0, "MEDIUM": 0.85, "DERIVED": 0.70, "LOW": 0.55}.get(confidence, 0.0)
        return True, multiplier
    return False, 0.0


def build_payload(scout: dict) -> dict:
    candidates = scout.get("sl_candidates", []) or scout.get("all_candidates", [])
    team_names = scout.get("team_names", sorted({c.get("team", "") for c in candidates if c.get("team")}))
    role_lists: dict[str, list] = {}

    for role_key, role in ROLE_REQUIREMENTS.items():
        ranked = []
        for candidate in candidates:
            matches, multiplier = _candidate_matches_role(candidate, role)
            if not matches:
                continue
            scored = _score_for_role(candidate, role_key, role, multiplier)
            if scored["role_fit_score"] >= _threshold(role_key):
                ranked.append(scored)
        ranked.sort(key=lambda x: x["role_fit_score"], reverse=True)
        role_lists[role_key] = ranked[:15]

    return {
        "summary": {
            "candidate_count": len(candidates),
            "roles": len(ROLE_REQUIREMENTS),
            "matched_role_candidates": sum(len(v) for v in role_lists.values()),
            "team_count": len(team_names),
        },
        "team_names": team_names,
        "roles": [
            {
                "role_key": rk,
                "label": ROLE_REQUIREMENTS[rk]["label"],
                "position_group": ROLE_REQUIREMENTS[rk]["position_group"],
                "verified_positions": sorted(ROLE_REQUIREMENTS[rk]["verified_positions"]),
                "reason": ROLE_REQUIREMENTS[rk]["reason"],
                "top_candidates": role_lists[rk],
            }
            for rk in ROLE_REQUIREMENTS
        ],
    }


def _score_for_role(candidate: dict, role_key: str, role: dict, multiplier: float) -> dict:
    group, confidence = _infer_group(candidate)
    goals = candidate.get("goals", 0)
    starts = candidate.get("starts", 0)
    cards = candidate.get("cards", 0)
    age = candidate.get("age") or 30
    load_max = candidate.get("estimated_physical_load_km_max", 9.0)
    ext = candidate.get("external_api_signal") or {}
    ext_role = ext.get("external_role_score") or 0

    base = candidate.get("overall_fm_fit_score", 0) * 0.40
    role_score = _role_specific(role_key, goals, starts, cards, age, load_max, ext_role, candidate)
    economy = _economy(candidate)
    risk = _risk(candidate)

    raw_score = base + role_score + 2.0 + economy - risk
    final_score = round(raw_score * multiplier, 2)

    return {
        **candidate,
        "target_role_key": role_key,
        "target_role_label": role["label"],
        "inferred_group": group,
        "position_confidence": confidence,
        "role_fit_score": final_score,
        "economy_score": round(economy, 2),
        "why_fit": _explain(role_key, candidate, group, confidence),
        "commercial_note": _commercial(candidate),
    }


def _role_specific(role_key: str, goals: int, starts: int, cards: int, age: int, load_max: float, ext_role: float, candidate: dict) -> float:
    if role_key == "ST_SCORER":
        return goals * 4.8 + starts * 0.35 + min(10, ext_role * 0.025)
    if role_key == "LW_CREATOR":
        return goals * 1.8 + starts * 0.6 + max(0, load_max - 9.4) * 5.0 + _youth(age) + min(8, ext_role * 0.018)
    if role_key == "CM_ENGINE":
        return starts * 0.9 + max(0, load_max - 9.5) * 8.0 + min(10, cards * 0.6) + _youth(age) * 0.5
    if role_key == "DM_SECURITY":
        return starts * 0.8 + max(0, load_max - 9.2) * 6.0 + min(9, cards * 0.85) - goals * 0.25
    if role_key == "FB_TWO_WAY":
        return starts * 0.7 + max(0, load_max - 9.5) * 7.0 + _youth(age) * 0.6 + min(6, goals * 0.5)
    if role_key == "CB_DOMINANT":
        return starts * 0.85 + candidate.get("header_goals", 0) * 2.0 + min(10, cards * 0.7)
    if role_key == "GK_STABILITY":
        return starts * 1.0 - goals * 2.0 - cards * 0.8
    return 0.0


def _threshold(role_key: str) -> float:
    thresholds = {
        "ST_SCORER": 30.0,
        "LW_CREATOR": 25.0,
        "CM_ENGINE": 20.0,
        "DM_SECURITY": 18.0,
        "FB_TWO_WAY": 18.0,
        "CB_DOMINANT": 18.0,
        "GK_STABILITY": 15.0,
    }
    return thresholds.get(role_key, 20.0)


def _economy(candidate: dict) -> float:
    age = candidate.get("age") or 30
    score = 0.0
    if age <= 23:
        score += 12
    elif age <= 25:
        score += 8
    elif age <= 28:
        score += 4
    else:
        score -= min(9, (age - 28) * 1.5)
    risk = candidate.get("contract_risk")
    if risk == "HIGH":
        score += 10
    elif risk == "MEDIUM":
        score += 6
    resale = candidate.get("resale_signal")
    if resale == "HIGH":
        score += 10
    elif resale == "MEDIUM":
        score += 4
    return score


def _risk(candidate: dict) -> float:
    penalty = 0.0
    if candidate.get("discipline_risk") == "HIGH":
        penalty += 8
    elif candidate.get("discipline_risk") == "MEDIUM":
        penalty += 3
    return penalty


def _youth(age: int) -> float:
    if age <= 21:
        return 10
    if age <= 23:
        return 7
    if age <= 25:
        return 4
    return 0


def _explain(role_key: str, candidate: dict, group: str, confidence: str) -> str:
    parts = [
        f"Poz. grup: {group} ({confidence}).",
        f"İlk 11: {candidate.get('starts', 0)}, Gol: {candidate.get('goals', 0)}, Kart: {candidate.get('cards', 0)}.",
    ]
    risk = candidate.get("contract_risk")
    if risk in {"HIGH", "MEDIUM"}:
        parts.append(f"Sözleşme fırsatı: {risk}.")
    if candidate.get("resale_signal") == "HIGH":
        parts.append("Resale potansiyeli yüksek.")
    return " ".join(parts)


def _commercial(candidate: dict) -> str:
    if candidate.get("resale_signal") == "HIGH":
        return "Al-sat değeri yüksek."
    if candidate.get("contract_risk") == "HIGH":
        return "Serbest kalma yakın; bonservis düşük olabilir."
    age = candidate.get("age")
    if age and age >= 30:
        return "Kısa vadeli sportif katkı adayı."
    return "Maliyet/katkı dengesi piyasa değeriyle doğrulanmalı."


def build_markdown(payload: dict) -> str:
    lines = [
        "# Süper Lig Pozisyon Bazlı Scout Matrisi",
        "",
        f"- Aday: {payload['summary']['candidate_count']}",
        f"- Rol-aday: {payload['summary']['matched_role_candidates']}",
        "",
    ]
    for role in payload["roles"]:
        lines.extend(["", f"## {role['label']}", f"_{role['reason']}_", ""])
        for c in role["top_candidates"][:8]:
            lines.append(
                f"- {c['name']} ({c.get('team')}) — fit={c['role_fit_score']}, "
                f"yaş={c.get('age')}, gol={c.get('goals')}, ilk11={c.get('starts')}"
            )
    return "\n".join(lines)


_NAV = """<div class="topbar">
  <a class="brand" href="/"><b>11</b> metric11</a>
  <nav>
    <a href="/">Gündem</a>
    <a href="transfer_tracker_2025_2026.html">Transferler</a>
    <a href="all_teams_preview_dashboard_2025_2026.html">Maç Önü</a>
    <a class="active" href="position_scout_matrix_2025_2026.html">Scout Matrisi</a>
    <a href="league_scouting_enriched_2025_2026_dashboard.html">Scout Havuzu</a>
    <a href="transfer_recommendation_report_2025_2026.html">Öneriler</a>
    <a href="football_intelligence_home.html">Analiz</a>
    <a href="worldcup_2026_predictions.html">🌍 WC 2026</a>
    <a href="european_predictions_2026_2027.html">⚽ Avrupa</a>
  </nav>
</div>"""


def build_html(payload: dict) -> str:
    summary = payload["summary"]
    sections_html = "".join(_role_section(r) for r in payload["roles"])
    team_names_json = json.dumps(payload["team_names"], ensure_ascii=False)

    return f"""<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Pozisyon Scout Matrisi {TRANSFER_WATCH_SEASON_LABEL} | metric11</title>
  <meta name="description" content="Süper Lig pozisyon bazlı scout matrisi: santrfor, 8 numara, bek ve daha fazla rol için aday eşleşmesi — metric11.">
  <meta property="og:title" content="Pozisyon Scout Matrisi — metric11">
  <meta property="og:image" content="https://metric11.com/og-image.png">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <style>
    :root{{--bg:#09111f;--panel:#0e1929;--panel2:#13223a;--ink:#e2e8f0;--muted:#64748b;--border:#1e3a5f;--green:#4ade80;--amber:#f59e0b;--red:#f87171;}}
    *{{box-sizing:border-box;margin:0;padding:0}}
    body{{font-family:Inter,"Segoe UI",Arial,sans-serif;background:var(--bg);color:var(--ink);min-height:100vh}}
    .topbar{{min-height:54px;padding:0 clamp(12px,3vw,32px);display:flex;align-items:center;justify-content:space-between;gap:16px;background:#060e1d;border-bottom:2px solid #1a3023}}
    .brand{{display:flex;align-items:center;gap:9px;color:white;text-decoration:none;font-size:17px;font-weight:800}}
    .brand:visited,.brand:hover{{color:white}}
    .brand b{{width:26px;height:26px;border-radius:5px;display:grid;place-items:center;background:#cde94e;color:#060e1d;font-size:13px;font-weight:900}}
    nav{{display:flex;gap:2px;overflow-x:auto;scrollbar-width:none}}
    nav::-webkit-scrollbar{{display:none}}
    nav a{{white-space:nowrap;color:#64748b;padding:7px 10px;border-radius:6px;text-decoration:none;font-size:12px;font-weight:600;transition:.15s}}
    nav a:visited{{color:#64748b}}
    nav a:hover,nav a.active{{background:#0f2030;color:white}}
    .hero{{background:linear-gradient(160deg,#0a1929,#060e1d);padding:24px clamp(12px,3vw,32px) 20px;border-bottom:1px solid var(--border)}}
    .hero h1{{font-size:clamp(18px,3vw,24px);font-weight:800;margin-bottom:6px}}
    .hero p{{font-size:13px;color:var(--muted)}}
    .stat-bar{{display:flex;gap:10px;padding:14px clamp(12px,3vw,32px);flex-wrap:wrap;border-bottom:1px solid var(--border)}}
    .stat-chip{{background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:9px 14px;text-align:center;min-width:90px}}
    .stat-chip .v{{font-size:18px;font-weight:800}}
    .stat-chip .l{{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.5px;margin-top:2px}}
    .ctrl-bar{{display:flex;gap:10px;flex-wrap:wrap;padding:14px clamp(12px,3vw,32px);border-bottom:1px solid var(--border);align-items:center}}
    .ctrl-bar select{{background:var(--panel);border:1px solid var(--border);color:var(--ink);padding:7px 12px;border-radius:6px;font-size:13px}}
    main{{padding:16px clamp(12px,3vw,32px) 60px}}
    .role-section{{background:var(--panel);border:1px solid var(--border);border-radius:10px;margin-bottom:16px;overflow:hidden}}
    .role-header{{padding:14px 16px;border-bottom:1px solid var(--border);display:flex;align-items:center;gap:12px}}
    .role-header h2{{font-size:15px;font-weight:700;margin:0}}
    .role-header p{{font-size:12px;color:var(--muted);margin:0}}
    .role-table-wrap{{overflow-x:auto}}
    table{{width:100%;border-collapse:collapse;font-size:12px}}
    th{{color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.4px;padding:8px 10px;border-bottom:1px solid var(--border);white-space:nowrap;background:var(--bg)}}
    td{{padding:8px 10px;border-bottom:1px solid rgba(30,58,95,.35);vertical-align:middle}}
    tr:hover td{{background:rgba(14,25,41,.6)}}
    tr.team-hide{{display:none}}
    .conf-badge{{font-size:10px;font-weight:700;padding:2px 7px;border-radius:4px}}
    .conf-HIGH{{color:#4ade80;background:rgba(74,222,128,.1)}}
    .conf-MEDIUM{{color:#60a5fa;background:rgba(96,165,250,.1)}}
    .conf-DERIVED{{color:#f59e0b;background:rgba(245,158,11,.1)}}
    .conf-LOW{{color:#94a3b8;background:rgba(148,163,184,.1)}}
    .contract-high{{color:#f87171}}
    .contract-med{{color:#f59e0b}}
    .mv-chip{{color:#f59e0b;font-weight:700}}
    .empty-msg{{padding:20px;color:var(--muted);font-size:13px;text-align:center}}
    @media(max-width:640px){{.ctrl-bar{{flex-direction:column}}}}
  </style>
</head>
<body>
{_NAV}
<div class="hero">
  <h1>Pozisyon Scout Matrisi <span style="color:#cde94e">{TRANSFER_WATCH_SEASON_LABEL}</span></h1>
  <p>Her rol için adaylar yaş, sözleşme fırsatı, tahmini yük, gol/ilk 11 profiliyle puanlanır. Takım seçerek kendi kadronuzdaki oyuncuları gizleyin.</p>
</div>
<div class="stat-bar">
  <div class="stat-chip"><div class="v">{summary["candidate_count"]}</div><div class="l">Aday</div></div>
  <div class="stat-chip"><div class="v">{summary["roles"]}</div><div class="l">Rol</div></div>
  <div class="stat-chip"><div class="v">{summary["matched_role_candidates"]}</div><div class="l">Eşleşme</div></div>
  <div class="stat-chip"><div class="v">{summary["team_count"]}</div><div class="l">Takım</div></div>
</div>
<div class="ctrl-bar">
  <label for="team-select" style="font-size:13px;color:var(--muted)">Scout takımı:</label>
  <select id="team-select" onchange="filterByTeam()">
    <option value="">Tüm Takımlar</option>
  </select>
  <span style="font-size:12px;color:var(--muted)" id="filter-note">Seçilen takımın oyuncuları gizlenir.</span>
</div>
<main>
{sections_html}
</main>
<script>
const TEAM_NAMES = {team_names_json};
TEAM_NAMES.forEach(t => {{
  const opt = document.createElement('option');
  opt.value = t; opt.textContent = t;
  document.getElementById('team-select').appendChild(opt);
}});
function filterByTeam() {{
  const sel = document.getElementById('team-select').value;
  document.querySelectorAll('tr[data-team]').forEach(r => {{
    r.classList.toggle('team-hide', sel !== '' && r.dataset.team === sel);
  }});
  document.getElementById('filter-note').textContent = sel ? sel + ' oyuncuları gizlendi.' : 'Seçilen takımın oyuncuları gizlenir.';
}}
</script>
<script defer src="/_vercel/insights/script.js"></script>
</body>
</html>"""


def _mv_str(eur) -> str:
    if not eur:
        return "—"
    if eur >= 1_000_000:
        return f"€{eur/1_000_000:.1f}M"
    if eur >= 1_000:
        return f"€{eur//1000}K"
    return f"€{eur}"


def _role_section(role: dict) -> str:
    candidates = role["top_candidates"]
    if not candidates:
        rows = f'<tr><td colspan="10" class="empty-msg">Rol için yeterli veri bulunamadı.</td></tr>'
    else:
        rows = "".join(_candidate_row(c) for c in candidates)

    return f"""<div class="role-section">
  <div class="role-header">
    <div>
      <h2>{escape(role["label"])}</h2>
      <p>{escape(role["reason"])}</p>
    </div>
    <span style="margin-left:auto;font-size:12px;color:var(--muted)">{len(candidates)} aday</span>
  </div>
  <div class="role-table-wrap">
    <table>
      <thead><tr>
        <th>Oyuncu</th><th>Takım</th><th>Fit</th><th>Güven</th>
        <th>Yaş</th><th>Gol</th><th>İlk 11</th><th>TM Değeri</th>
        <th>Sözleşme</th><th>Açıklama</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </div>
</div>"""


def _candidate_row(c: dict) -> str:
    team = c.get("team") or ""
    conf = c.get("position_confidence", "")
    contract_end = str(c.get("contract_end") or "—")[:7]
    risk = c.get("contract_risk") or ""
    risk_class = "contract-high" if risk == "HIGH" else ("contract-med" if risk == "MEDIUM" else "")
    mv = _mv_str(c.get("tm_market_value_eur"))
    tm_url = c.get("tm_profile_url") or ""
    name = escape(c.get("name") or "")
    name_html = (
        f'<a href="{escape(tm_url)}" target="_blank" rel="noopener" '
        f'style="color:var(--ink);font-weight:600;text-decoration:none;border-bottom:1px dotted var(--border)">{name}</a>'
        if tm_url else f'<span style="font-weight:600">{name}</span>'
    )
    return (
        f'<tr data-team="{escape(team)}">'
        f'<td style="min-width:130px">{name_html}</td>'
        f'<td style="font-size:11px;color:var(--muted)">{escape(team)}</td>'
        f'<td style="font-weight:700;color:#60a5fa">{c.get("role_fit_score", 0):.1f}</td>'
        f'<td><span class="conf-badge conf-{conf}">{conf}</span></td>'
        f'<td>{c.get("age", "—")}</td>'
        f'<td style="font-weight:600">{c.get("goals", 0)}</td>'
        f'<td style="color:var(--muted)">{c.get("starts", 0)}</td>'
        f'<td class="mv-chip">{mv}</td>'
        f'<td class="{risk_class}">{contract_end}</td>'
        f'<td style="font-size:11px;color:var(--muted);max-width:280px">{escape(c.get("why_fit", ""))}</td>'
        f'</tr>'
    )


if __name__ == "__main__":
    main()
