from __future__ import annotations

import argparse
import json
from html import escape
from pathlib import Path

from src.config import PROCESSED_DIR


def main() -> None:
    parser = argparse.ArgumentParser(description="Takim ihtiyac analizi icin statik HTML dashboard uretir.")
    parser.add_argument("--input", default=str(PROCESSED_DIR / "besiktas_team_needs_2025_2026.json"))
    parser.add_argument("--output", default=str(PROCESSED_DIR / "besiktas_team_needs_2025_2026_dashboard.html"))
    args = parser.parse_args()

    report = json.loads(Path(args.input).read_text(encoding="utf-8"))
    output = Path(args.output)
    output.write_text(build_html(report), encoding="utf-8")
    print(output)


def build_html(report: dict) -> str:
    summary = report["summary"]
    needs = "".join(
        f"<tr><td><span class=\"pill {priority_class(item['priority'])}\">{escape(item['priority'])}</span></td>"
        f"<td>{escape(item['need'])}</td><td>{escape(item['reason'])}</td></tr>"
        for item in report["needs"]
    )
    top_assets = "".join(player_row(player) for player in report["top_assets"][:14])
    young_assets = "".join(player_row(player) for player in report["young_assets"][:14])
    contract_risks = "".join(contract_row(player) for player in report["contract_risks"][:18])
    action_plan = "".join(action_row(item) for item in report.get("position_action_plan", []))
    goal_dependency = "".join(
        f"<tr><td>{escape(name)}</td><td>{goals}</td></tr>" for name, goals in report["goal_dependency"][:10]
    )
    age_bands = "".join(
        f"<div class=\"age-band\"><span>{escape(str(label))}</span><strong>{starts}</strong></div>"
        for label, starts in report["starts_by_age_band"].items()
    )
    return f"""<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(report['team'])} Takım İhtiyaç Paneli</title>
  <style>
    :root {{
      --bg:#f4f6f8; --panel:#fff; --ink:#15181d; --muted:#667085; --line:#dce2ea;
      --accent:#111318; --red:#bf1f2f; --amber:#b76b00; --green:#137a4b;
      --shadow:0 8px 22px rgba(18,24,32,.08);
    }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; font-family:Inter, system-ui, sans-serif; background:var(--bg); color:var(--ink); }}
    header {{ background:var(--accent); color:white; padding:26px 40px; border-bottom:4px solid var(--red); }}
    header h1 {{ margin:0 0 6px; font-size:30px; letter-spacing:0; }}
    header p {{ margin:0; color:#c9ced8; }}
    main {{ max-width:1320px; margin:0 auto; padding:24px; }}
    .metrics {{ display:grid; grid-template-columns:repeat(5,1fr); gap:12px; margin-bottom:18px; }}
    .metric, section {{ background:var(--panel); border:1px solid var(--line); border-radius:8px; box-shadow:var(--shadow); }}
    .metric {{ padding:15px; }}
    .metric span {{ display:block; color:var(--muted); font-size:12px; }}
    .metric strong {{ display:block; font-size:28px; margin-top:5px; }}
    .grid {{ display:grid; grid-template-columns:1.1fr .9fr; gap:18px; }}
    section {{ padding:18px; margin-bottom:18px; }}
    h2 {{ margin:0 0 14px; font-size:18px; }}
    table {{ width:100%; border-collapse:collapse; font-size:14px; }}
    th,td {{ padding:9px 7px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; }}
    th {{ color:var(--muted); font-size:12px; }}
    .pill {{ display:inline-flex; min-height:24px; align-items:center; border-radius:999px; padding:0 9px; font-size:12px; border:1px solid var(--line); }}
    .high {{ color:var(--red); background:#fff0f2; border-color:#efb7bf; }}
    .medium {{ color:var(--amber); background:#fff7e8; border-color:#f2d09a; }}
    .low {{ color:var(--green); background:#edf9f3; border-color:#b9dfcd; }}
    .age-grid {{ display:grid; grid-template-columns:repeat(5,1fr); gap:10px; }}
    .age-band {{ border:1px solid var(--line); border-radius:8px; padding:12px; background:#fbfcfd; }}
    .age-band span {{ color:var(--muted); font-size:12px; display:block; }}
    .age-band strong {{ font-size:24px; }}
    @media (max-width:980px) {{ .metrics,.grid,.age-grid {{ grid-template-columns:1fr 1fr; }} }}
    @media (max-width:620px) {{ .metrics,.grid,.age-grid {{ grid-template-columns:1fr; }} header {{ padding:22px; }} main {{ padding:14px; }} }}
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
    <a href="european_predictions_2026_2027.html">⚽ Avrupa</a>
    </nav>
  </div>
  <header>
    <h1>{escape(report['team'])} Takım İhtiyaç Paneli</h1>
    <p>TFF oyuncu profilleri ile maç performansı birleşimi: kadro yaşı, sözleşme riski, gelişim varlıkları ve ihtiyaç sinyalleri.</p>
  </header>
  <main>
    <div class="metrics">
      {metric("Oyuncu", summary["players"])}
      {metric("TM eşleşme", summary.get("transfermarkt_matched_players", 0))}
      {metric("Ortalama yaş", summary["avg_age"])}
      {metric("Ort. sözleşme ayı", summary["avg_contract_months_left"])}
      {metric("U23 oyuncu", summary["u23_players"])}
      {metric("13 ayda bitecek", summary["contract_expiring_13_months"])}
    </div>
    <section>
      <h2>İlk 11 Yükü Yaş Dağılımı</h2>
      <div class="age-grid">{age_bands}</div>
    </section>
    <section>
      <h2>Pozisyon Aksiyon Planı</h2>
      <table><thead><tr><th>Hat</th><th>Öncelik</th><th>Oyuncu</th><th>Düzenli</th><th>Genç</th><th>Değer</th><th>Öneri</th></tr></thead><tbody>{action_plan}</tbody></table>
    </section>
    <section>
      <h2>İhtiyaç Sinyalleri</h2>
      <table><thead><tr><th>Öncelik</th><th>İhtiyaç</th><th>Gerekçe</th></tr></thead><tbody>{needs}</tbody></table>
    </section>
    <div class="grid">
      <div>
        <section><h2>Elde Değer / Gelişim Varlığı</h2>{player_table(top_assets)}</section>
        <section><h2>Genç Varlıklar</h2>{player_table(young_assets)}</section>
      </div>
      <div>
        <section><h2>Sözleşme Riski</h2>{contract_table(contract_risks)}</section>
        <section><h2>Gol Yükü</h2><table><thead><tr><th>Oyuncu</th><th>Gol</th></tr></thead><tbody>{goal_dependency}</tbody></table></section>
      </div>
    </div>
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


def player_table(rows: str) -> str:
    return (
        "<table><thead><tr><th>Oyuncu</th><th>Pozisyon</th><th>Değer</th><th>Yaş</th><th>Asset</th><th>İlk 11</th><th>Gol</th><th>Sözleşme</th></tr></thead>"
        f"<tbody>{rows}</tbody></table>"
    )


def contract_table(rows: str) -> str:
    return (
        "<table><thead><tr><th>Oyuncu</th><th>Risk</th><th>Kalan Ay</th><th>İlk 11</th><th>Bitiş</th></tr></thead>"
        f"<tbody>{rows}</tbody></table>"
    )


def player_row(player: dict) -> str:
    return (
        f"<tr><td>{escape(player['name'])}</td><td>{escape(player.get('position') or '')}</td>"
        f"<td>{escape(player.get('market_value_text') or '')}</td><td>{escape(str(player.get('age') or ''))}</td>"
        f"<td>{player['asset_score']}</td><td>{player['starts']}</td><td>{player['goals']}</td>"
        f"<td>{escape(player.get('contract_end') or '')}</td></tr>"
    )


def contract_row(player: dict) -> str:
    risk = player["contract_risk"]
    return (
        f"<tr><td>{escape(player['name'])}</td><td><span class=\"pill {priority_class(risk)}\">{escape(risk)}</span></td>"
        f"<td>{escape(str(player.get('contract_months_left')))}</td><td>{player['starts']}</td>"
        f"<td>{escape(player.get('contract_end') or '')}</td></tr>"
    )


def action_row(item: dict) -> str:
    return (
        f"<tr><td>{escape(item['label'])}</td><td><span class=\"pill {priority_class(item['priority'])}\">{escape(item['priority'])}</span></td>"
        f"<td>{item['players']}</td><td>{item['regulars']}</td><td>{item['young_assets']}</td>"
        f"<td>€{item['market_value_total_eur']:,}</td><td>{escape(item['recommendation'])}</td></tr>"
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
