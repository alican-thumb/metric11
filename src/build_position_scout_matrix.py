from __future__ import annotations

import argparse
import json
from html import escape
from pathlib import Path

from src.config import PROCESSED_DIR


ROLE_REQUIREMENTS = {
    "LW_CREATOR": {
        "label": "Sol açık / çizgi kırıcı",
        "position_group": "FWD",
        "verified_positions": ["Left Winger", "Right Winger", "Attacking Midfield"],
        "need_tags": ["kanat", "hücum", "yaratıcılık", "sol"],
        "reason": "Kanat üretimi ve açık alan tehdidi için süper lig aday havuzu.",
    },
    "ST_SCORER": {
        "label": "Santrfor / skor yükü",
        "position_group": "FWD",
        "verified_positions": ["Centre-Forward", "Second Striker"],
        "need_tags": ["hücum", "gol", "bitirici"],
        "reason": "Dar maçlarda gol olasılığını artıracak direkt skor profili.",
    },
    "CM_ENGINE": {
        "label": "8 numara / fizik motoru",
        "position_group": "MID",
        "verified_positions": ["Central Midfield", "Defensive Midfield", "Attacking Midfield"],
        "need_tags": ["orta saha", "fizik", "pres", "tempo"],
        "reason": "Pres, geçiş ve ikinci top sürekliliğini taşıyacak merkez orta saha.",
    },
    "DM_SECURITY": {
        "label": "6 numara / savunma emniyeti",
        "position_group": "MID",
        "verified_positions": ["Defensive Midfield", "Central Midfield"],
        "need_tags": ["orta saha", "savunma", "denge"],
        "reason": "Savunma önü denge ve kart/tempo yönetimi için güvenli profil.",
    },
    "FB_TWO_WAY": {
        "label": "Bek / çift yönlü koridor",
        "position_group": "DEF",
        "verified_positions": ["Left-Back", "Right-Back", "Left Midfield", "Right Midfield"],
        "need_tags": ["bek", "savunma", "kanat", "tempo"],
        "reason": "Kanat savunması ve bindirme sürekliliği için ekonomik bek profili.",
    },
    "CB_DOMINANT": {
        "label": "Stoper / hava ve temas",
        "position_group": "DEF",
        "verified_positions": ["Centre-Back"],
        "need_tags": ["stoper", "savunma", "hava", "temas"],
        "reason": "Duran top, hava topu ve temas yoğunluğu için savunma profili.",
    },
    "GK_STABILITY": {
        "label": "Kaleci / istikrar",
        "position_group": "GK",
        "verified_positions": ["Goalkeeper"],
        "need_tags": ["kaleci", "istikrar"],
        "reason": "Rotasyon ve güvenli kadro planı için kaleci profili.",
    },
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Pozisyon bazlı scout matrisi ve takım ihtiyacı eşleşmesi üretir.")
    parser.add_argument("--scout", default=str(PROCESSED_DIR / "fm_style_scout_program_2025_2026.json"))
    parser.add_argument("--output-prefix", default="position_scout_matrix_2025_2026")
    args = parser.parse_args()

    scout = json.loads(Path(args.scout).read_text(encoding="utf-8"))
    payload = build_payload(scout)

    json_path = PROCESSED_DIR / f"{args.output_prefix}.json"
    md_path = PROCESSED_DIR / f"{args.output_prefix}.md"
    html_path = PROCESSED_DIR / f"{args.output_prefix}.html"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(build_markdown(payload), encoding="utf-8")
    html_path.write_text(build_html(payload), encoding="utf-8")
    print(md_path.read_text(encoding="utf-8"))


def build_payload(scout: dict) -> dict:
    candidates = scout.get("sl_candidates", []) or scout.get("all_candidates", [])
    team_names = scout.get("team_names", sorted(set(c.get("team", "") for c in candidates if c.get("team"))))
    role_lists = {}
    for role_key, role in ROLE_REQUIREMENTS.items():
        ranked = []
        for candidate in candidates:
            if not candidate_matches_verified_role(candidate, role):
                continue
            item = score_candidate_for_role(candidate, role_key, role)
            if item["role_fit_score"] >= min_role_threshold(role_key):
                ranked.append(item)
        ranked.sort(key=lambda item: item["role_fit_score"], reverse=True)
        role_lists[role_key] = ranked[:20]

    return {
        "summary": {
            "candidate_count": len(candidates),
            "roles": len(ROLE_REQUIREMENTS),
            "matched_role_candidates": sum(len(items) for items in role_lists.values()),
            "team_count": len(team_names),
            "model_note": "Pozisyon matrisi 691 oyuncunun tamamını tarar; yayınlanan rol adayları Transfermarkt pozisyonu allowlist ile doğrulanan oyunculardır.",
        },
        "team_names": team_names,
        "roles": [
            {
                "role_key": role_key,
                **ROLE_REQUIREMENTS[role_key],
                "top_candidates": role_lists[role_key],
            }
            for role_key in ROLE_REQUIREMENTS
        ],
    }



def candidate_matches_verified_role(candidate: dict, role: dict) -> bool:
    verified_position = candidate.get("tm_position")
    allowed_positions = role.get("verified_positions")
    return bool(verified_position and (not allowed_positions or verified_position in allowed_positions))


def score_candidate_for_role(candidate: dict, role_key: str, role: dict) -> dict:
    inferred_group, inferred_role, confidence = infer_candidate_position(candidate)
    group_match = 1.0 if inferred_group == role["position_group"] else 0.18 if inferred_group == "UNKNOWN" else 0.08
    base = candidate.get("overall_fm_fit_score", 0) * 0.42
    starts = candidate.get("starts", 0)
    goals = candidate.get("goals", 0)
    cards = candidate.get("cards", 0)
    age = candidate.get("age") or 30
    load_max = candidate.get("estimated_physical_load_km_max", 9.0)
    external = candidate.get("external_api_signal", {})
    external_role = external.get("external_role_score") or 0
    role_specific = role_specific_score(role_key, candidate, goals, starts, cards, age, load_max, external_role)
    need_boost = 2.0
    economy = economy_score(candidate)
    risk_penalty = risk_penalty_score(candidate)
    score = (base + role_specific + need_boost + economy - risk_penalty) * group_match
    return {
        **candidate,
        "target_role_key": role_key,
        "target_role_label": role["label"],
        "inferred_position_group": inferred_group,
        "inferred_role": inferred_role,
        "position_confidence": confidence,
        "role_fit_score": round(score, 2),
        "need_boost": round(need_boost, 2),
        "economy_score": round(economy, 2),
        "risk_penalty": round(risk_penalty, 2),
        "why_fit": explain_fit(role_key, candidate, inferred_role, confidence),
        "commercial_note": commercial_note(candidate),
    }


def infer_candidate_position(candidate: dict) -> tuple[str, str, str]:
    tm_position = candidate.get("tm_position") or ""
    tm_group = candidate.get("tm_position_group") or ""
    external_position = (candidate.get("external_api_signal", {}) or {}).get("position") or ""
    archetype = candidate.get("archetype", "")
    goals = candidate.get("goals", 0)
    cards = candidate.get("cards", 0)
    starts = candidate.get("starts", 0)
    headers = candidate.get("header_goals", 0)
    load_max = candidate.get("estimated_physical_load_km_max", 0)

    if tm_group in {"GK", "DEF", "MID", "FWD"}:
        return tm_group, tm_position or "Transfermarkt pozisyonu", "MEDIUM_EXTERNAL"
    if "Goalkeeper" in external_position:
        return "GK", "Kaleci", "MEDIUM_EXTERNAL"
    if "Defender" in external_position:
        return "DEF", "Savunma", "MEDIUM_EXTERNAL"
    if "Midfielder" in external_position:
        return "MID", "Orta saha", "MEDIUM_EXTERNAL"
    if "Forward" in external_position:
        if headers >= 4 or goals >= 12:
            return "FWD", "Santrfor / bitirici", "MEDIUM_EXTERNAL"
        return "FWD", "Kanat/forvet", "MEDIUM_EXTERNAL"
    if goals >= 12:
        return "FWD", "Santrfor / bitirici", "LOW_DERIVED"
    if goals >= 6 and load_max >= 10.3:
        return "FWD", "Kanat/gezgin forvet", "LOW_DERIVED"
    if "Fizik motoru" in archetype or (starts >= 20 and cards >= 5 and goals <= 6):
        return "MID", "Fizik motoru / temas", "LOW_DERIVED"
    if cards >= 7 and goals <= 4:
        return "DEF", "Temas/savunma profili", "LOW_DERIVED"
    if starts >= 24 and goals <= 3:
        return "DEF", "Düzenli savunma/denge", "LOW_DERIVED"
    return "UNKNOWN", "Pozisyon doğrulama gerekli", "VERY_LOW"


def role_specific_score(role_key: str, candidate: dict, goals: int, starts: int, cards: int, age: int, load_max: float, external_role: float) -> float:
    if role_key == "ST_SCORER":
        return goals * 4.8 + starts * 0.35 + min(10, external_role * 0.025)
    if role_key == "LW_CREATOR":
        striker_penalty = 28 if goals >= 12 else 0
        striker_penalty += 12 if candidate.get("header_goals", 0) >= 4 else 0
        return goals * 1.4 + starts * 0.65 + max(0, load_max - 9.4) * 6.0 + youth_bonus(age) + min(8, external_role * 0.018) - striker_penalty
    if role_key == "CM_ENGINE":
        return starts * 0.9 + max(0, load_max - 9.7) * 8.5 + min(10, cards * 0.7) + youth_bonus(age) * 0.5
    if role_key == "DM_SECURITY":
        return starts * 0.75 + max(0, load_max - 9.4) * 6.5 + min(9, cards * 0.9) - goals * 0.2
    if role_key == "FB_TWO_WAY":
        return starts * 0.72 + max(0, load_max - 9.8) * 7.5 + youth_bonus(age) * 0.65 + min(7, goals * 0.55)
    if role_key == "CB_DOMINANT":
        return starts * 0.82 + candidate.get("header_goals", 0) * 2.2 + min(10, cards * 0.75)
    if role_key == "GK_STABILITY":
        return starts * 0.9 - goals * 1.5 - cards * 0.7
    return 0.0


def min_role_threshold(role_key: str) -> float:
    if role_key in {"LW_CREATOR", "ST_SCORER"}:
        return 52.0
    if role_key in {"CM_ENGINE", "DM_SECURITY", "FB_TWO_WAY", "CB_DOMINANT"}:
        return 45.0
    return 35.0



def economy_score(candidate: dict) -> float:
    age = candidate.get("age") or 30
    contract_risk = candidate.get("contract_risk")
    resale = candidate.get("resale_signal")
    score = 0.0
    if age <= 23:
        score += 12
    elif age <= 25:
        score += 8
    elif age <= 28:
        score += 4
    else:
        score -= min(9, (age - 28) * 1.5)
    if contract_risk == "HIGH":
        score += 10
    elif contract_risk == "MEDIUM":
        score += 6
    if resale == "HIGH":
        score += 10
    elif resale == "MEDIUM":
        score += 4
    return score


def risk_penalty_score(candidate: dict) -> float:
    penalty = 0.0
    if candidate.get("discipline_risk") == "HIGH":
        penalty += 8
    elif candidate.get("discipline_risk") == "MEDIUM":
        penalty += 3
    if candidate.get("position_confidence") == "VERY_LOW":
        penalty += 4
    external = candidate.get("external_api_signal", {})
    if external.get("matched") and (external.get("yellow_cards") or 0) >= 8:
        penalty += 2
    return penalty


def youth_bonus(age: int) -> float:
    if age <= 21:
        return 10
    if age <= 23:
        return 7
    if age <= 25:
        return 4
    return 0


def explain_fit(role_key: str, candidate: dict, inferred_role: str, confidence: str) -> str:
    parts = [
        f"Rol okuması: {inferred_role} ({confidence}).",
        f"İlk 11 {candidate.get('starts', 0)}, gol {candidate.get('goals', 0)}, kart {candidate.get('cards', 0)}.",
        f"Tahmini yük {candidate.get('estimated_physical_load_km_min')}-{candidate.get('estimated_physical_load_km_max')} km.",
    ]
    if role_key in {"LW_CREATOR", "CM_ENGINE", "FB_TWO_WAY"}:
        parts.append("Tempo ve tekrar koşu ihtiyacı olan rolde fiziksel yük proxy'si öne çıkarıldı.")
    if candidate.get("contract_risk") in {"HIGH", "MEDIUM"}:
        parts.append(f"Sözleşme fırsatı {candidate.get('contract_risk')} seviyesinde.")
    if candidate.get("resale_signal") == "HIGH":
        parts.append("Genç değer/resale sinyali güçlü.")
    return " ".join(parts)


def commercial_note(candidate: dict) -> str:
    age = candidate.get("age")
    if candidate.get("resale_signal") == "HIGH":
        return "Al-sat değeri yüksek aday; doğru maaş/bonservis bandında ekonomik upside sağlar."
    if candidate.get("contract_risk") == "HIGH":
        return "Sözleşme fırsatı nedeniyle düşük bonservis veya serbest kalma pazarlığı izlenmeli."
    if age and age >= 30:
        return "Kısa vadeli sportif katkı adayı; resale beklentisi düşük tutulmalı."
    return "Sportif katkı ve maliyet dengesi ayrıca piyasa değeriyle doğrulanmalı."


def build_markdown(payload: dict) -> str:
    lines = [
        "# Süper Lig Pozisyon Bazlı Scout Matrisi",
        "",
        f"- Aday oyuncu: {payload['summary']['candidate_count']}",
        f"- Rol sayısı: {payload['summary']['roles']}",
        f"- Rol-aday eşleşmesi: {payload['summary']['matched_role_candidates']}",
        f"- Takım: {payload['summary']['team_count']}",
        f"- Not: {payload['summary']['model_note']}",
        "",
    ]
    for role in payload["roles"]:
        lines.extend(["", f"## {role['label']}", "", f"- Rol gerekçesi: {role['reason']}"])
        for candidate in role["top_candidates"][:8]:
            lines.append(
                f"- {candidate['name']} ({candidate.get('team')}): fit={candidate['role_fit_score']}, "
                f"yaş={candidate.get('age')}, rol={candidate['inferred_role']}, güven={candidate['position_confidence']}, "
                f"gol={candidate.get('goals')}, ilk11={candidate.get('starts')}, ekonomi={candidate['economy_score']}. "
                f"{candidate['why_fit']} {candidate['commercial_note']}"
            )
    return "\n".join(lines)


def build_html(payload: dict) -> str:
    sections = "".join(role_section(role) for role in payload["roles"])
    team_names_json = json.dumps(payload["team_names"], ensure_ascii=False)
    return f"""<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Pozisyon Scout Matrisi — Süper Lig | metric11</title>
  <meta name="description" content="Süper Lig takımları için pozisyon bazlı scout matrisi: santrfor, 8 numara, bek ve daha fazla rol için aday eşleşmesi — metric11.">
  <meta property="og:title" content="Pozisyon Scout Matrisi — metric11">
  <meta property="og:description" content="Süper Lig takımları için pozisyon bazlı scout matrisi: rol ihtiyacı ve ekonomik fırsatla aday eşleşmesi — metric11.">
  <meta property="og:image" content="https://metric11.com/og-image.png">
  <meta property="og:type" content="website">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:image" content="https://metric11.com/og-image.png">
  <meta name="theme-color" content="#091810">
  <link rel="icon" href="favicon.svg" type="image/svg+xml">
  <style>
    :root {{ --bg:#f4f6f8; --panel:#fff; --ink:#14171c; --muted:#667085; --line:#dce2ea; --dark:#111318; --green:#137a4b; --blue:#185ea8; --amber:#b76b00; --shadow:0 8px 22px rgba(18,24,32,.08); }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; font-family:Inter, system-ui, sans-serif; background:var(--bg); color:var(--ink); }}
    header {{ background:var(--dark); color:white; padding:28px 42px; border-bottom:4px solid var(--green); }}
    header h1 {{ margin:0 0 7px; font-size:32px; letter-spacing:0; }}
    header p {{ margin:0; color:#c9ced8; max-width:1040px; line-height:1.5; }}
    main {{ max-width:1420px; margin:0 auto; padding:24px; }}
    .ctrl-bar {{ display:flex; align-items:center; gap:12px; flex-wrap:wrap; margin-bottom:18px; padding:12px 14px; background:var(--panel); border:1px solid var(--line); border-radius:8px; box-shadow:var(--shadow); }}
    .ctrl-bar label {{ font-size:13px; font-weight:600; color:var(--muted); }}
    .ctrl-bar select {{ font-family:inherit; font-size:13px; font-weight:600; color:var(--ink); background:var(--panel); border:1px solid var(--line); border-radius:7px; padding:7px 12px; cursor:pointer; outline:none; }}
    .ctrl-bar select:focus {{ border-color:#0d9488; }}
    .metrics {{ display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:18px; }}
    .metric, section {{ background:var(--panel); border:1px solid var(--line); border-radius:8px; box-shadow:var(--shadow); }}
    .metric {{ padding:15px; }}
    .metric span {{ display:block; color:var(--muted); font-size:12px; }}
    .metric strong {{ display:block; font-size:26px; margin-top:5px; }}
    section {{ padding:18px; margin-bottom:18px; overflow-x:auto; }}
    h2 {{ margin:0 0 6px; font-size:18px; }}
    .reason {{ color:var(--muted); margin:0 0 12px; }}
    table {{ width:100%; border-collapse:collapse; font-size:13px; }}
    th,td {{ padding:9px 7px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; }}
    th {{ color:var(--muted); font-size:12px; }}
    .pill {{ display:inline-flex; min-height:23px; align-items:center; border-radius:999px; padding:0 8px; font-size:12px; border:1px solid #bbd7f5; color:var(--blue); background:#edf5ff; }}
    tr.hidden {{ display:none; }}
    @media (max-width:900px) {{ .metrics {{ grid-template-columns:1fr 1fr; }} main {{ padding:14px; }} header {{ padding:22px; }} table {{ font-size:12px; }} }}
    @media (max-width:620px) {{ .metrics {{ grid-template-columns:1fr; }} }}
    .topbar{{position:sticky;top:0;z-index:5;display:flex;align-items:center;justify-content:space-between;gap:20px;min-height:52px;padding:0 clamp(16px,4vw,42px);background:#111318;color:white;border-bottom:2px solid #1a3023;}}
    .brand{{display:flex;gap:8px;align-items:center;font-weight:800;font-size:17px;color:white;text-decoration:none;}}
    .brand:visited,.brand:hover{{color:white;}}
    .brand-mark{{width:26px;height:26px;display:grid;place-items:center;border-radius:5px;color:#111318;background:#a3e635;font-size:13px;font-weight:900;}}
    nav{{display:flex;gap:2px;overflow-x:auto;-webkit-overflow-scrolling:touch;scrollbar-width:none;}}
    nav::-webkit-scrollbar{{display:none;}}
    nav a{{color:#8fa89a;text-decoration:none;font-size:13px;font-weight:600;padding:8px 10px;border-radius:6px;white-space:nowrap;}}
    nav a:hover,nav a.active{{background:#162b20;color:white;}}
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
    <h1>Pozisyon Scout Matrisi — Süper Lig</h1>
    <p>Her rol için adaylar yaş, sözleşme fırsatı, tahmini fiziksel yük, gol/ilk 11/kart profili ve dış veri sinyaliyle puanlanır. Takım seçerek kendi kadronuzdaki oyuncuları filtreleyin.</p>
  </header>
  <main>
    <div class="ctrl-bar">
      <label for="team-select">Scouting takımı:</label>
      <select id="team-select" onchange="filterByTeam()">
        <option value="">Tüm Takımlar</option>
      </select>
      <span style="font-size:12px;color:var(--muted)" id="filter-note">Seçilen takımın oyuncuları gizlenir.</span>
    </div>
    <div class="metrics">
      {metric("Aday", payload["summary"]["candidate_count"])}
      {metric("Rol", payload["summary"]["roles"])}
      {metric("Rol-aday", payload["summary"]["matched_role_candidates"])}
      {metric("Takım", payload["summary"]["team_count"])}
    </div>
    {sections}
  </main>
  <footer style="text-align:center;padding:40px 16px 28px;color:#8a9e92;font-size:12px;border-top:1px solid #e2e8e4;margin-top:48px;">
    metric11 &middot; <a href="mailto:hello@metric11.com" style="color:#8a9e92;text-decoration:none;border-bottom:1px solid #c5d4ca;">hello@metric11.com</a>
  </footer>
  <script>
  const TEAM_NAMES = {team_names_json};
  TEAM_NAMES.forEach(t => {{
    const opt = document.createElement('option');
    opt.value = t; opt.textContent = t;
    document.getElementById('team-select').appendChild(opt);
  }});
  function filterByTeam() {{
    const selected = document.getElementById('team-select').value;
    document.querySelectorAll('tr[data-team]').forEach(row => {{
      row.classList.toggle('hidden', selected !== '' && row.dataset.team === selected);
    }});
    const note = document.getElementById('filter-note');
    note.textContent = selected ? selected + ' oyuncuları gizlendi.' : 'Seçilen takımın oyuncuları gizlenir.';
  }}
  </script>
  <script defer src="/_vercel/insights/script.js"></script>
</body>
</html>
"""


def role_section(role: dict) -> str:
    rows = "".join(candidate_row(candidate) for candidate in role["top_candidates"][:10])
    return (
        f"<section><h2>{escape(role['label'])}</h2><p class=\"reason\">{escape(role['reason'])}</p>"
        "<table><thead><tr><th>Oyuncu</th><th>Takım</th><th>Fit</th><th>Rol Okuması</th>"
        "<th>Güven</th><th>Yaş</th><th>Gol</th><th>İlk 11</th><th>Yük</th><th>Ekonomi</th><th>Neden</th></tr></thead>"
        f"<tbody>{rows}</tbody></table></section>"
    )


def candidate_row(candidate: dict) -> str:
    load = f"{candidate.get('estimated_physical_load_km_min')}-{candidate.get('estimated_physical_load_km_max')}"
    team = candidate.get('team') or ''
    return (
        f"<tr data-team=\"{escape(team)}\"><td>{escape(candidate.get('name', ''))}</td><td>{escape(team)}</td>"
        f"<td>{candidate['role_fit_score']}</td><td><span class=\"pill\">{escape(candidate['inferred_role'])}</span></td>"
        f"<td>{escape(candidate['position_confidence'])}</td><td>{escape(str(candidate.get('age') or ''))}</td>"
        f"<td>{candidate.get('goals', 0)}</td><td>{candidate.get('starts', 0)}</td><td>{load}</td>"
        f"<td>{candidate['economy_score']}</td><td>{escape(candidate['why_fit'] + ' ' + candidate['commercial_note'])}</td></tr>"
    )


def metric(label: str, value) -> str:
    return f'<div class="metric"><span>{escape(str(label))}</span><strong>{escape(str(value))}</strong></div>'


if __name__ == "__main__":
    main()
