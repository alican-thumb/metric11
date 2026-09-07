from __future__ import annotations

import argparse
import json
from html import escape
from pathlib import Path

from src.config import PROCESSED_DIR
from src.html_utils import nav_links_html

# FM2023 Turkish Super Lig clubs (exclude from global pool to avoid double-counting)
_TURKISH_FM23_TEAMS = {
    "Galatasaray A.Ş.", "Trabzonspor A.Ş.", "Konyaspor", "Kayserispor",
    "Sivasspor", "Gaziantep Futbol Kulübü A.Ş.", "Antalyaspor", "Alanyaspor",
    "Rizespor A.Ş.", "Hatayspor",
}

_GLOBAL_CA_MIN = 130


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scout", default=str(PROCESSED_DIR / "league_scouting_enriched_2025_2026.json"))
    parser.add_argument("--fm23", default=str(PROCESSED_DIR / "player_attribute_dataset_fm2023_normalized.json"))
    parser.add_argument("--output-prefix", default="fm_style_scout_program_2025_2026")
    args = parser.parse_args()

    scout = json.loads(Path(args.scout).read_text(encoding="utf-8"))
    fm23_data = json.loads(Path(args.fm23).read_text(encoding="utf-8"))

    sl_candidates = [enrich_candidate(p) for p in scout.get("enriched_shortlist", [])]
    global_pool = _build_global_pool(fm23_data)
    team_names = sorted(set(c["team"] for c in sl_candidates))

    payload = {
        "summary": {
            "sl_candidates": len(sl_candidates),
            "global_pool": len(global_pool),
            "fm23_matched": sum(1 for c in sl_candidates if (c.get("fm23_signal") or {}).get("matched")),
            "teams": len(team_names),
            "global_ca_min": _GLOBAL_CA_MIN,
        },
        "sl_candidates": sl_candidates,
        "global_pool": global_pool,
        "team_names": team_names,
    }

    prefix = args.output_prefix
    (PROCESSED_DIR / f"{prefix}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    html = build_html(payload)
    (PROCESSED_DIR / f"{prefix}.html").write_text(html, encoding="utf-8")
    print(f"SL: {len(sl_candidates)} oyuncu, Global: {len(global_pool)} oyuncu, HTML yazıldı.")


def _build_global_pool(fm23_data: dict) -> list[dict]:
    pool = []
    for p in fm23_data.get("players", []):
        ca = p.get("current_ability") or 0
        team = p.get("team") or ""
        if ca < _GLOBAL_CA_MIN:
            continue
        if team in _TURKISH_FM23_TEAMS:
            continue
        pool.append({
            "name": p.get("name") or "",
            "team": team,
            "age": p.get("age"),
            "position": p.get("position") or "",
            "position_group": p.get("position_group") or "MID",
            "current_ability": ca,
            "potential_ability": p.get("potential_ability"),
            "growth_room": p.get("growth_room"),
            "raw_attributes": p.get("raw_attributes") or {},
        })
    pool.sort(key=lambda x: x["current_ability"], reverse=True)
    return pool


def enrich_candidate(player: dict) -> dict:
    attribute = player.get("attribute_signal") or {}
    external = player.get("external_api_signal") or {}
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
        immediate_scorer * 0.25 + physical_engine * 0.18
        + resale_value * 0.22 + contract_opportunity * 0.22 + low_risk_regular * 0.13
    )

    result = {k: v for k, v in player.items()}
    result.update({
        "archetype": archetype,
        "estimated_physical_load_km_min": physical_min,
        "estimated_physical_load_km_max": physical_max,
        "immediate_scorer_score": round(immediate_scorer, 2),
        "physical_engine_score": round(physical_engine, 2),
        "resale_value_score": round(resale_value, 2),
        "contract_opportunity_score": round(contract_opportunity, 2),
        "low_risk_regular_score": round(low_risk_regular, 2),
        "overall_fm_fit_score": round(overall, 2),
    })
    return result


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


def build_html(payload: dict) -> str:
    summary = payload["summary"]
    sl_json = json.dumps(payload["sl_candidates"], ensure_ascii=False)
    global_json = json.dumps(payload["global_pool"], ensure_ascii=False)
    team_names_json = json.dumps(payload["team_names"], ensure_ascii=False)

    return f"""<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>FM Scout Programı — metric11</title>
  <meta name="description" content="Süper Lig 2025-2026 scouting programı: 691 oyuncu için Football Manager tarzı attribute barları, takım ihtiyacı eşleşmesi — metric11.">
  <meta property="og:title" content="FM Scout Programı — metric11">
  <meta property="og:description" content="Süper Lig 2025-2026 scouting programı: 691 oyuncu için Football Manager tarzı attribute barları — metric11.">
  <meta property="og:image" content="https://metric11.com/og-image.png">
  <meta property="og:type" content="website">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:image" content="https://metric11.com/og-image.png">
  <meta name="theme-color" content="#091810">
  <link rel="icon" href="favicon.svg" type="image/svg+xml">
  <style>
    :root{{--bg:#f3f5f4;--panel:#fff;--ink:#132018;--muted:#627067;--line:#d7ded9;--dark:#091810;--green:#116447;--teal:#0d9488;--shadow:0 4px 16px rgba(9,24,16,.07);}}
    *{{box-sizing:border-box;margin:0;padding:0;}}
    body{{font-family:Inter,system-ui,sans-serif;background:var(--bg);color:var(--ink);}}
    .topbar{{position:sticky;top:0;z-index:10;display:flex;align-items:center;justify-content:space-between;gap:20px;min-height:58px;padding:0 clamp(14px,4vw,40px);background:#091810;border-bottom:2px solid #1a3023;}}
    .brand{{display:flex;gap:8px;align-items:center;font-weight:800;font-size:17px;color:white;text-decoration:none;}}
    .brand:visited,.brand:active,.brand:hover{{color:white;}}
    .brand-mark{{width:26px;height:26px;display:grid;place-items:center;border-radius:5px;color:#091810;background:#a3e635;font-size:13px;font-weight:900;}}
    nav{{display:flex;gap:2px;overflow-x:auto;scrollbar-width:none;}}
    nav::-webkit-scrollbar{{display:none;}}
    nav a{{color:#8fa89a;text-decoration:none;font-size:13px;font-weight:600;padding:8px 10px;border-radius:6px;white-space:nowrap;}}
    nav a:visited{{color:#8fa89a;}}
    nav a:hover,nav a.active{{background:#162b20;color:white;}}

    header{{background:var(--dark);color:white;padding:26px clamp(16px,4vw,40px) 22px;border-bottom:4px solid var(--green);}}
    header h1{{font-size:clamp(22px,3vw,30px);font-weight:800;letter-spacing:-.5px;margin-bottom:6px;}}
    header p{{color:#8fa89a;font-size:14px;max-width:780px;line-height:1.55;}}

    main{{max-width:1380px;margin:0 auto;padding:20px clamp(12px,3vw,28px) 40px;}}

    .summary-bar{{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:20px;}}
    .s-pill{{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:10px 16px;display:flex;flex-direction:column;gap:2px;min-width:120px;box-shadow:var(--shadow);}}
    .s-pill span{{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.05em;}}
    .s-pill strong{{font-size:24px;font-weight:800;color:var(--ink);}}

    .ctrl-bar{{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:18px;padding:12px 14px;background:var(--panel);border:1px solid var(--line);border-radius:10px;box-shadow:var(--shadow);}}
    .mode-btn{{background:none;border:1px solid var(--line);cursor:pointer;font-family:inherit;font-size:13px;font-weight:700;color:var(--muted);padding:7px 16px;border-radius:7px;transition:all .15s;}}
    .mode-btn.active{{background:#0f2018;color:white;border-color:#0f2018;}}
    .mode-btn:hover:not(.active){{background:#e8ede9;color:var(--ink);}}
    select{{font-family:inherit;font-size:13px;font-weight:600;color:var(--ink);background:var(--panel);border:1px solid var(--line);border-radius:7px;padding:7px 12px;cursor:pointer;outline:none;}}
    select:focus{{border-color:#0d9488;}}
    .ctrl-sep{{color:var(--line);}}

    .tab-bar{{display:flex;gap:4px;overflow-x:auto;scrollbar-width:none;margin-bottom:16px;background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:5px;box-shadow:var(--shadow);}}
    .tab-bar::-webkit-scrollbar{{display:none;}}
    .tab{{flex-shrink:0;background:none;border:none;cursor:pointer;font-family:inherit;font-size:13px;font-weight:600;color:var(--muted);padding:8px 16px;border-radius:7px;transition:all .15s;}}
    .tab.active{{background:#0f2018;color:white;}}
    .tab:hover:not(.active){{background:#e8ede9;color:var(--ink);}}

    .cards-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px;}}

    .pcard{{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px;box-shadow:var(--shadow);display:flex;flex-direction:column;gap:10px;border-top:3px solid var(--ring,var(--green));transition:box-shadow .15s;}}
    .pcard:hover{{box-shadow:0 8px 28px rgba(9,24,16,.13);}}
    .pcard-top{{display:flex;justify-content:space-between;align-items:flex-start;gap:8px;}}
    .pcard-name{{font-size:14px;font-weight:800;color:var(--ink);line-height:1.3;letter-spacing:-.2px;}}
    .pcard-meta{{font-size:12px;color:var(--muted);margin-top:2px;}}
    .pcard-score{{flex-shrink:0;width:42px;height:42px;border-radius:50%;display:grid;place-items:center;font-size:16px;font-weight:900;border:2px solid;}}

    .arc-badge{{display:inline-flex;align-items:center;border-radius:6px;padding:3px 8px;font-size:11px;font-weight:700;border:1px solid;letter-spacing:.02em;width:fit-content;}}
    .arc-row{{display:flex;align-items:center;gap:6px;flex-wrap:wrap;}}
    .pa-chip{{font-size:11px;font-weight:700;color:#185ea8;background:#edf5ff;border:1px solid #bbd7f5;padding:3px 8px;border-radius:6px;}}
    .src-badge{{font-size:10px;font-weight:600;padding:2px 7px;border-radius:4px;}}
    .src-fm23{{color:#6b3fa0;background:#f3eeff;border:1px solid #d4b8f0;}}
    .src-global{{color:#b84f00;background:#fff6ed;border:1px solid #f5c58a;}}
    .src-turetilmis{{color:#555;background:#f0f0f0;border:1px solid #ccc;}}

    .attrs{{display:flex;flex-direction:column;gap:5px;}}
    .attr-row{{display:grid;grid-template-columns:90px 1fr 28px;align-items:center;gap:6px;}}
    .attr-lbl{{font-size:11px;color:var(--muted);font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}}
    .bar-track{{height:7px;background:#e8ede9;border-radius:99px;overflow:hidden;}}
    .bar-fill{{height:100%;border-radius:99px;}}
    .attr-val{{font-size:12px;font-weight:800;text-align:right;}}

    .pcard-stats{{display:flex;gap:10px;flex-wrap:wrap;padding:8px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line);font-size:12px;color:var(--muted);}}
    .pcard-stats strong{{color:var(--ink);}}
    .pcard-footer{{display:flex;align-items:center;gap:8px;flex-wrap:wrap;}}
    .cbadge{{font-size:11px;font-weight:700;padding:3px 8px;border-radius:6px;border:1px solid;}}
    .cbadge-high{{color:#bf1f2f;background:#fff0f2;border-color:#efb7bf;}}
    .cbadge-med{{color:#b76b00;background:#fff7e8;border-color:#f2d09a;}}
    .cbadge-low{{color:#0d9488;background:#f0fdfc;border-color:#99e6e0;}}
    .cbadge-ok{{color:var(--muted);background:#f4f6f8;border-color:var(--line);}}
    .val-chip{{font-size:11px;font-weight:700;color:var(--green);background:#edf9f3;border:1px solid #b9dfcd;padding:3px 8px;border-radius:6px;}}
    .val-link{{color:inherit;text-decoration:none;}}
    .val-link:hover{{text-decoration:underline;}}

    .empty{{padding:40px;text-align:center;color:var(--muted);font-size:14px;}}
    @media(max-width:640px){{
      .cards-grid{{grid-template-columns:1fr;}}
      .ctrl-bar{{flex-direction:column;align-items:flex-start;}}
    }}
  </style>
</head>
<body>
  <div class="topbar">
    <a class="brand" href="/"><span class="brand-mark">11</span> metric11</a>
    <nav class="topnav">{nav_links_html("transfer_recommendation_report_2025_2026.html")}</nav>
  </div>

  <header>
    <h1>FM Scout Programı</h1>
    <p>
      {summary['sl_candidates']} Süper Lig oyuncusu · {summary['global_pool']} global aday (CA ≥ {summary['global_ca_min']}) ·
      {summary['fm23_matched']} SL oyuncusunda FM23 gerçek attribute barları
    </p>
  </header>

  <main>
    <div class="summary-bar">
      <div class="s-pill"><span>Süper Lig</span><strong>{summary['sl_candidates']}</strong></div>
      <div class="s-pill"><span>Global Havuz</span><strong>{summary['global_pool']}</strong></div>
      <div class="s-pill"><span>FM23 Eşleşmesi</span><strong>{summary['fm23_matched']}</strong></div>
      <div class="s-pill"><span>Takım</span><strong>{summary['teams']}</strong></div>
    </div>

    <div class="ctrl-bar">
      <button class="mode-btn active" id="btn-sl" onclick="setMode('sl')">🇹🇷 Süper Lig</button>
      <button class="mode-btn" id="btn-global" onclick="setMode('global')">🌍 Global Havuz</button>
      <span class="ctrl-sep">|</span>
      <div id="sl-controls" style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;">
        <select id="team-select" onchange="render()">
          <option value="">Tüm Takımlar (691)</option>
        </select>
        <select id="bucket-select" onchange="render()">
          <option value="immediate_scorer_score">⚽ Gol Katkısı</option>
          <option value="physical_engine_score">💪 Fizik Motoru</option>
          <option value="resale_value_score">📈 Resale Değeri</option>
          <option value="contract_opportunity_score">🤝 Kontrakt Fırsatı</option>
          <option value="low_risk_regular_score">🛡 Güvenilirlik</option>
        </select>
      </div>
      <div id="global-controls" style="display:none;gap:10px;align-items:center;flex-wrap:wrap;">
        <select id="pos-select" onchange="render()">
          <option value="">Tüm Pozisyonlar</option>
          <option value="FWD">⚽ Forvet (FWD)</option>
          <option value="MID">🔄 Orta Saha (MID)</option>
          <option value="DEF">🛡 Defans (DEF)</option>
          <option value="GK">🧤 Kaleci (GK)</option>
        </select>
      </div>
    </div>

    <div id="cards-area" class="cards-grid"></div>
  </main>

  <footer style="text-align:center;padding:40px 16px 28px;color:#8a9e92;font-size:12px;border-top:1px solid #e2e8e4;margin-top:48px;">
    metric11 &middot; <a href="mailto:hello@metric11.com" style="color:#8a9e92;text-decoration:none;border-bottom:1px solid #c5d4ca;">hello@metric11.com</a>
  </footer>

  <script>
  const SL = {sl_json};
  const GLOBAL = {global_json};
  const TEAM_NAMES = {team_names_json};

  const POS_ATTRS = {{
    FWD: ['finishing','technique','positioning','decisions','composure','dribbling','pace','stamina'],
    MID: ['passing','decisions','technique','vision','first_touch','anticipation','work_rate','stamina'],
    DEF: ['tackling','marking','decisions','positioning','concentration','stamina','pace','strength'],
    GK:  ['decisions','positioning','stamina','work_rate','concentration','teamwork'],
  }};
  const ATTR_LABELS = {{
    finishing:'Bitiricilik',technique:'Teknik',positioning:'Pozisyon',decisions:'Karar Verme',
    pace:'Hız',stamina:'Kondisyon',passing:'Pas',vision:'Vizyon',work_rate:'Çalışma Temposu',
    tackling:'Müdahale',teamwork:'Takım Oyunu',acceleration:'İvme',dribbling:'Dribling',
    first_touch:'İlk Dokunuş',composure:'Soğukkanlılık',concentration:'Konsantrasyon',
    anticipation:'Öngörü',marking:'Markaj',strength:'Fiziksel Güç',heading:'Kafa Vuruşu',
    long_shots:'Uzak Şut',crossing:'Orta',flair:'Yaratıcılık',agility:'Çeviklik',
    balance:'Denge',natural_fitness:'Doğal Form',
  }};
  const ARCHETYPE_COLORS = {{
    'Bitirici / skor yükü':          ['#fff0f2','#bf1f2f'],
    'Genç değer / gelişim':          ['#edf5ff','#185ea8'],
    'Fizik motoru / tempo oyuncusu': ['#fff6ed','#b84f00'],
    'Sertlik ve temas profili':      ['#f1f3f5','#374151'],
    'Düşük riskli düzenli oyuncu':   ['#edf9f3','#137a4b'],
    'Rotasyon fırsatı':              ['#f4f6f8','#667085'],
  }};

  let currentMode = 'sl';

  // Populate team dropdown
  TEAM_NAMES.forEach(t => {{
    const opt = document.createElement('option');
    opt.value = t; opt.textContent = t;
    document.getElementById('team-select').appendChild(opt);
  }});

  function setMode(mode) {{
    currentMode = mode;
    document.getElementById('btn-sl').classList.toggle('active', mode === 'sl');
    document.getElementById('btn-global').classList.toggle('active', mode === 'global');
    document.getElementById('sl-controls').style.display = mode === 'sl' ? 'flex' : 'none';
    document.getElementById('global-controls').style.display = mode === 'global' ? 'flex' : 'none';
    render();
  }}

  function attrColor(v) {{
    if (v >= 16) return '#137a4b';
    if (v >= 13) return '#0d9488';
    if (v >= 10) return '#b76b00';
    return '#adb5bd';
  }}
  function caColor(ca) {{
    if (ca >= 160) return '#137a4b';
    if (ca >= 140) return '#0d9488';
    if (ca >= 130) return '#b76b00';
    return '#adb5bd';
  }}
  function esc(s) {{
    return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }}

  function arcBadge(arch) {{
    const [bg,color] = ARCHETYPE_COLORS[arch]||['#f4f6f8','#667085'];
    return `<span class="arc-badge" style="background:${{bg}};color:${{color}};border-color:${{color}}22">${{esc(arch)}}</span>`;
  }}

  function attrBars(raw, posGroup) {{
    const keys = POS_ATTRS[posGroup] || POS_ATTRS.MID;
    let html = '';
    for (const key of keys) {{
      const val = raw[key];
      if (val == null) continue;
      const v = Math.round(val);
      const pct = Math.round(val / 20 * 100);
      const clr = attrColor(v);
      html += `<div class="attr-row"><span class="attr-lbl">${{esc(ATTR_LABELS[key]||key)}}</span><div class="bar-track"><div class="bar-fill" style="width:${{pct}}%;background:${{clr}}"></div></div><span class="attr-val" style="color:${{clr}}">${{v}}</span></div>`;
    }}
    return html;
  }}

  function renderSLCard(p) {{
    const fm23 = p.fm23_signal||{{}};
    const derived = p.derived_signal||{{}};
    const attr = p.attribute_signal||{{}};
    const posGrp = (p.tm_position_group||'MID').toUpperCase();

    let raw, ca, pa, srcLabel, srcClass;
    if (fm23.matched) {{
      raw = fm23.raw_attributes||{{}}; ca = fm23.current_ability; pa = fm23.potential_ability;
      srcLabel = 'FM23'; srcClass = 'src-fm23';
    }} else if (derived.matched) {{
      raw = derived.raw_attributes||{{}}; ca = derived.current_ability; pa = derived.potential_ability;
      srcLabel = 'Türetilmiş'; srcClass = 'src-turetilmis';
    }} else {{
      raw = attr.raw_attributes||{{}}; ca = attr.current_ability; pa = attr.potential_ability;
      srcLabel = null; srcClass = '';
    }}

    const scoreField = document.getElementById('bucket-select').value;
    const scoreVal = p[scoreField]||0;
    const allScores = SL.map(x=>x[scoreField]||0);
    const maxScore = Math.max(...allScores) || 1;
    const pct = Math.min(100, Math.round(scoreVal/maxScore*100));
    function barColor(pc) {{
      if (pc>=78) return '#137a4b';
      if (pc>=55) return '#0d9488';
      if (pc>=35) return '#b76b00';
      return '#adb5bd';
    }}

    let barsHtml, scoreLabel, ringColor;
    if (Object.keys(raw).length > 0) {{
      barsHtml = attrBars(raw, posGrp);
      scoreLabel = ca ? String(Math.round(ca)) : '?';
      ringColor = ca ? caColor(Math.round(ca)) : '#adb5bd';
    }} else {{
      const SCORE_FIELDS = [
        ['immediate_scorer_score','Gol Katkısı'],['physical_engine_score','Fizik Motoru'],
        ['resale_value_score','Resale Değeri'],['contract_opportunity_score','Kontrakt Fırsatı'],
        ['low_risk_regular_score','Güvenilirlik']
      ];
      barsHtml = SCORE_FIELDS.map(([f,lbl]) => {{
        const v = p[f]||0;
        const mx = Math.max(...SL.map(x=>x[f]||0))||1;
        const pc = Math.min(100,Math.round(v/mx*100));
        const clr = barColor(pc);
        const active = f===scoreField?' style="opacity:1"':'';
        return `<div class="attr-row"${{active}}><span class="attr-lbl">${{esc(lbl)}}</span><div class="bar-track"><div class="bar-fill" style="width:${{pc}}%;background:${{clr}}"></div></div><span class="attr-val" style="color:${{clr}}">${{pc}}</span></div>`;
      }}).join('');
      scoreLabel = String(pct);
      ringColor = barColor(pct);
    }}

    const paChip = (pa && ca && pa > ca + 2) ? `<span class="pa-chip">PA ${{Math.round(pa)}}</span>` : '';
    const srcBadge = srcLabel ? `<span class="src-badge ${{srcClass}}">${{srcLabel}}</span>` : '';
    const risk = p.contract_risk||'';
    const end = (p.contract_end||'').slice(0,7)||'?';
    let cbadge;
    if (risk==='HIGH') cbadge=`<span class="cbadge cbadge-high">⚠ ${{esc(end)}}</span>`;
    else if (risk==='MEDIUM') cbadge=`<span class="cbadge cbadge-med">⌛ ${{esc(end)}}</span>`;
    else if (p.contract_months_left&&p.contract_months_left<=24) cbadge=`<span class="cbadge cbadge-low">📅 ${{esc(end)}}</span>`;
    else cbadge=`<span class="cbadge cbadge-ok">📅 ${{esc(end)}}</span>`;
    const valTxt = p.tm_market_value_text||'';
    const valUrl = p.tm_profile_url||'';
    const valChip = valTxt && valTxt!=='-' ? `<span class="val-chip">${{valUrl?`<a href="${{esc(valUrl)}}" target="_blank" rel="noopener" class="val-link">${{esc(valTxt)}}</a>`:esc(valTxt)}}</span>` : '';

    const loMin = p.estimated_physical_load_km_min||0;
    const loMax = p.estimated_physical_load_km_max||0;

    return `<div class="pcard" style="--ring:${{ringColor}}">
  <div class="pcard-top">
    <div><div class="pcard-name">${{esc(p.name||'')}}</div><div class="pcard-meta">${{esc(p.team||'')}} · ${{p.age||'?'}}y · ${{esc(p.nationality||'')}}</div></div>
    <div class="pcard-score" style="color:${{ringColor}};border-color:${{ringColor}}33;background:${{ringColor}}12">${{scoreLabel}}</div>
  </div>
  <div class="arc-row">${{arcBadge(p.archetype||'Rotasyon fırsatı')}}${{paChip}}${{srcBadge}}</div>
  <div class="attrs">${{barsHtml}}</div>
  <div class="pcard-stats"><span>⚽ <strong>${{p.goals||0}}</strong></span><span>▶ <strong>${{p.starts||0}}</strong></span><span>🟨 <strong>${{p.cards||0}}</strong></span><span>🏃 <strong>${{loMin}}–${{loMax}}km</strong></span></div>
  <div class="pcard-footer">${{cbadge}}${{valChip}}</div>
</div>`;
  }}

  function renderGlobalCard(p) {{
    const ca = p.current_ability||0;
    const pa = p.potential_ability;
    const raw = p.raw_attributes||{{}};
    const posGrp = p.position_group||'MID';
    const ringColor = caColor(ca);
    const barsHtml = attrBars(raw, posGrp);
    const paChip = (pa && pa > ca+2) ? `<span class="pa-chip">PA ${{Math.round(pa)}}</span>` : '';
    const growthChip = (p.growth_room && p.growth_room > 5) ? `<span class="pa-chip">+${{Math.round(p.growth_room)}}</span>` : '';

    return `<div class="pcard" style="--ring:${{ringColor}}">
  <div class="pcard-top">
    <div><div class="pcard-name">${{esc(p.name||'')}}</div><div class="pcard-meta">${{esc(p.team||'')}} · ${{p.age||'?'}}y · ${{esc(p.position||'')}}</div></div>
    <div class="pcard-score" style="color:${{ringColor}};border-color:${{ringColor}}33;background:${{ringColor}}12">${{Math.round(ca)}}</div>
  </div>
  <div class="arc-row"><span class="arc-badge" style="background:#f4f6f8;color:#374151;border-color:#37415122">CA ${{Math.round(ca)}}</span>${{paChip}}${{growthChip}}<span class="src-badge src-global">FM23 Global</span></div>
  <div class="attrs">${{barsHtml}}</div>
  <div class="pcard-stats"><span>📊 CA <strong>${{Math.round(ca)}}</strong></span><span>🎯 PA <strong>${{pa?Math.round(pa):'?'}}</strong></span><span>🔢 ${{esc(posGrp)}}</span></div>
</div>`;
  }}

  function render() {{
    const area = document.getElementById('cards-area');
    if (currentMode === 'sl') {{
      const teamFilter = document.getElementById('team-select').value;
      const scoreField = document.getElementById('bucket-select').value;
      let players = teamFilter ? SL.filter(p => p.team !== teamFilter) : SL;
      players = [...players].sort((a,b) => (b[scoreField]||0)-(a[scoreField]||0)).slice(0,24);
      if (!players.length) {{ area.innerHTML='<div class="empty">Aday bulunamadı.</div>'; return; }}
      area.innerHTML = players.map(renderSLCard).join('');
    }} else {{
      const posFilter = document.getElementById('pos-select').value;
      let players = posFilter ? GLOBAL.filter(p => p.position_group === posFilter) : GLOBAL;
      players = players.slice(0, 24);
      if (!players.length) {{ area.innerHTML='<div class="empty">Aday bulunamadı.</div>'; return; }}
      area.innerHTML = players.map(renderGlobalCard).join('');
    }}
  }}

  render();
  </script>
  <script defer src="/_vercel/insights/script.js"></script>
</body>
</html>"""


if __name__ == "__main__":
    main()
