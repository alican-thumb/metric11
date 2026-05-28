from __future__ import annotations

import argparse
import json
from html import escape
from pathlib import Path

from src.config import PROCESSED_DIR


def main() -> None:
    parser = argparse.ArgumentParser(description="Yas/sozlesme ile zenginlestirilmis scout dashboard uretir.")
    parser.add_argument("--input", default=str(PROCESSED_DIR / "league_scouting_enriched_2025_2026.json"))
    parser.add_argument("--output", default=str(PROCESSED_DIR / "league_scouting_enriched_2025_2026_dashboard.html"))
    args = parser.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    output = Path(args.output)
    output.write_text(build_html(payload), encoding="utf-8")
    print(output)


def build_html(payload: dict) -> str:
    summary = payload["summary"]
    full_rows = "".join(player_row(player) for player in payload["enriched_shortlist"][:30])
    young_rows = "".join(player_row(player) for player in payload["young_value"][:12])
    contract_rows = "".join(player_row(player) for player in payload["contract_opportunities"][:12])
    return f"""<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Zenginleştirilmiş Scout Paneli</title>
  <style>
    :root {{
      --bg:#f5f7fa; --panel:#fff; --ink:#15181d; --muted:#667085; --line:#dce2ea;
      --accent:#121722; --green:#147a4d; --amber:#b76b00; --red:#bf1f2f; --shadow:0 8px 22px rgba(18,24,32,.08);
    }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; font-family:Inter, system-ui, sans-serif; background:var(--bg); color:var(--ink); }}
    header {{ background:var(--accent); color:white; padding:26px 40px; border-bottom:4px solid var(--green); }}
    header h1 {{ margin:0 0 6px; font-size:30px; letter-spacing:0; }}
    header p {{ color:#c9ced8; margin:0; }}
    main {{ max-width:1320px; margin:0 auto; padding:24px; }}
    .metrics {{ display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:18px; }}
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
    .high {{ color:var(--green); background:#edf9f3; border-color:#b9dfcd; }}
    .medium {{ color:var(--amber); background:#fff7e8; border-color:#f2d09a; }}
    .low {{ color:var(--red); background:#fff0f2; border-color:#efb7bf; }}
    @media (max-width:760px) {{ .metrics {{ grid-template-columns:1fr; }} main {{ padding:14px; }} header {{ padding:22px; }} table {{ font-size:12px; }} }}
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
    <h1>Zenginleştirilmiş Scout Paneli</h1>
    <p>TFF maç performansı + TFF oyuncu profili + opsiyonel FM/FIFA tarzı attribute verisi: fırsat skoru, yaş, sözleşme riski, rol uyumu ve yeniden satış sinyali.</p>
  </header>
  <main>
    <div class="metrics">
      {metric("Profilli oyuncu", summary["profiled_players"])}
      {metric("U24 oyuncu", summary["u24_players"])}
      {metric("Sözleşme fırsatı", summary["contract_risk_players"])}
      {metric("Attribute eşleşme", summary.get("attribute_matched_players", 0))}
    </div>
    <section><h2>Fırsat Skoru</h2>{table(full_rows)}</section>
    <section><h2>Genç Değer</h2>{table(young_rows)}</section>
    <section><h2>Sözleşme Fırsatları</h2>{table(contract_rows)}</section>
  </main>
  <footer style="text-align:center;padding:40px 16px 28px;color:#8a9e92;font-size:12px;border-top:1px solid #e2e8e4;margin-top:48px;">
    metric11 &middot; <a href="mailto:hello@metric11.com" style="color:#8a9e92;text-decoration:none;border-bottom:1px solid #c5d4ca;">hello@metric11.com</a>
  </footer>
  <script defer src="/_vercel/insights/script.js"></script>
</body>
</html>
"""


def metric(label: str, value) -> str:
    return f'<div class="metric"><span>{escape(label)}</span><strong>{escape(str(value))}</strong></div>'


def table(rows: str) -> str:
    return (
        "<table><thead><tr><th>Oyuncu</th><th>Takım</th><th>Fırsat</th><th>Scout</th><th>Yaş</th>"
        "<th>Rol-fit</th><th>PA</th><th>Gol</th><th>İlk 11</th><th>Sözleşme</th><th>Risk</th><th>Resale</th></tr></thead>"
        f"<tbody>{rows}</tbody></table>"
    )


def player_row(player: dict) -> str:
    attribute = player.get("attribute_signal", {})
    return (
        f"<tr><td>{escape(player['name'])}</td><td>{escape(player.get('team') or '')}</td>"
        f"<td>{player['opportunity_score']}</td><td>{player['scout_value_score']}</td><td>{escape(str(player.get('age') or ''))}</td>"
        f"<td>{escape(str(attribute.get('role_fit_score') or ''))}</td><td>{escape(str(attribute.get('potential_ability') or ''))}</td>"
        f"<td>{player['goals']}</td><td>{player['starts']}</td><td>{escape(player.get('contract_end') or '')}</td>"
        f"<td>{escape(player['contract_risk'])}</td><td><span class=\"pill {resale_class(player['resale_signal'])}\">{escape(player['resale_signal'])}</span></td></tr>"
    )


def resale_class(signal: str) -> str:
    if signal == "HIGH":
        return "high"
    if signal == "MEDIUM":
        return "medium"
    return "low"


if __name__ == "__main__":
    main()
