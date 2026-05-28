from __future__ import annotations

import argparse
import json
from html import escape
from pathlib import Path

from src.config import PROCESSED_DIR
from src.html_utils import _build_nav


def main() -> None:
    parser = argparse.ArgumentParser(description="Lig scout metrikleri icin statik HTML dashboard uretir.")
    parser.add_argument("--input", default=str(PROCESSED_DIR / "league_scouting_2025_2026.json"))
    parser.add_argument("--output", default=str(PROCESSED_DIR / "league_scouting_2025_2026_dashboard.html"))
    args = parser.parse_args()

    metrics = json.loads(Path(args.input).read_text(encoding="utf-8"))
    output = Path(args.output)
    output.write_text(build_html(metrics), encoding="utf-8")
    print(output)


def build_html(metrics: dict) -> str:
    team_rows = "".join(
        f"<tr><td>{escape(team)}</td><td>{rec['points']}</td><td>{rec['goals_for']}-{rec['goals_against']}</td><td>{rec['goals_for_per_match']}</td><td>{rec['goals_against_per_match']}</td><td>{rec['cards_per_match']}</td></tr>"
        for team, rec in list(metrics["team_metrics"].items())[:20]
    )
    scout_rows = "".join(
        f"<tr><td>{escape(p['name'])}</td><td>{escape(p['team'] or '')}</td><td>{p['scout_value_score']}</td><td>{p['goals']}</td><td>{p['starts']}</td><td>{p['goals_per_start']}</td><td>{p['discipline_risk']}</td></tr>"
        for p in metrics["scout_shortlist"][:40]
    )
    scorer_rows = "".join(
        f"<tr><td>{escape(p['name'])}</td><td>{escape(p['team'] or '')}</td><td>{p['goals']}</td><td>{p['starts']}</td><td>{p['goals_per_start']}</td><td>{p['finishing_signal']}</td></tr>"
        for p in metrics["top_scorers"][:30]
    )
    ref_rows = "".join(
        f"<tr><td>{escape(ref)}</td><td>{rec['matches']}</td><td>{rec['cards_per_match']}</td><td>{rec['goals_per_match']}</td></tr>"
        for ref, rec in list(metrics["referee_metrics"].items())[:20]
    )
    nav = _build_nav("Analiz")
    return f"""<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Süper Lig Scout Paneli — metric11</title>
  <meta name="theme-color" content="#091810">
  <link rel="icon" href="favicon.svg" type="image/svg+xml">
  <style>
    body {{ margin:0; font-family: Inter, system-ui, sans-serif; background:#f5f6f8; color:#17191c; }}
    .topbar {{ position:sticky; top:0; z-index:5; display:flex; align-items:center; justify-content:space-between; gap:20px; min-height:58px; padding:0 clamp(16px,4vw,42px); background:#091810; color:white; border-bottom:2px solid #1a3023; }}
    .brand {{ display:flex; gap:10px; align-items:center; font-weight:800; font-size:18px; color:white; text-decoration:none; flex-shrink:0; letter-spacing:-0.2px; }}
    .brand:visited,.brand:active,.brand:hover {{ color:white; }}
    .brand-mark {{ width:28px; height:28px; display:grid; place-items:center; border-radius:6px; color:#091810; background:#cde94e; font-size:14px; font-weight:900; flex-shrink:0; }}
    .season {{ color:#6b7c72; font-size:11px; font-weight:500; margin-left:2px; border-left:1px solid #2a3d30; padding-left:8px; }}
    nav {{ display:flex; gap:2px; flex-wrap:nowrap; overflow-x:auto; justify-content:flex-end; scrollbar-width:none; }}
    nav::-webkit-scrollbar {{ display:none; }}
    nav a {{ color:#8fa89a; text-decoration:none; font-size:13px; font-weight:600; padding:8px 11px; border-radius:6px; white-space:nowrap; transition:background .15s,color .15s; }}
    nav a:visited {{ color:#8fa89a; }}
    nav a:hover {{ background:#162b20; color:white; }}
    nav a.active {{ background:#162b20; color:white; }}
    .page-header {{ background:#111318; color:white; padding:24px 40px; border-bottom:4px solid #d0182f; }}
    .back-link {{ display:inline-flex; align-items:center; gap:6px; color:#4ade80; text-decoration:none; font-size:13px; font-weight:600; margin-bottom:10px; }}
    .back-link::before {{ content:"←"; }}
    main {{ max-width:1280px; margin:0 auto; padding:24px; }}
    section {{ background:white; border:1px solid #d9dee7; border-radius:8px; margin-bottom:18px; padding:18px; box-shadow:0 8px 24px rgba(20,25,32,.08); }}
    h1 {{ margin:0 0 6px; }} h2 {{ margin:0 0 14px; font-size:18px; }}
    p {{ color:#667085; margin:0; }}
    table {{ width:100%; border-collapse:collapse; font-size:14px; }}
    th,td {{ padding:9px 7px; border-bottom:1px solid #d9dee7; text-align:left; vertical-align:top; }}
    th {{ color:#667085; font-size:12px; }}
    @media (max-width:680px) {{ .topbar {{ position:static; flex-direction:column; align-items:stretch; padding:11px 16px 0; gap:0; min-height:unset; }} .brand {{ padding-bottom:8px; }} .season {{ display:none; }} nav {{ justify-content:flex-start; border-top:1px solid #1e3228; padding:7px 0 9px; }} }}
  </style>
</head>
<body>
  {nav}
  <div class="page-header">
    <a class="back-link" href="/">Ana sayfaya dön</a>
    <h1>Süper Lig 2025-2026 Scout Paneli</h1>
    <p>TFF maç detaylarından üretilmiş MVP scout havuzu: takım güçleri, golcüler, scout kısa listesi ve hakem profilleri.</p>
  </div>
  <main>
    <section><h2>Takım Güçleri</h2><table><thead><tr><th>Takım</th><th>Puan</th><th>Gol</th><th>GF/M</th><th>GA/M</th><th>Kart/M</th></tr></thead><tbody>{team_rows}</tbody></table></section>
    <section><h2>Scout Kısa Liste</h2><table><thead><tr><th>Oyuncu</th><th>Takım</th><th>Scout</th><th>Gol</th><th>İlk 11</th><th>Gol/İlk 11</th><th>Disiplin</th></tr></thead><tbody>{scout_rows}</tbody></table></section>
    <section><h2>Golcü Listesi</h2><table><thead><tr><th>Oyuncu</th><th>Takım</th><th>Gol</th><th>İlk 11</th><th>Gol/İlk 11</th><th>Bitiricilik</th></tr></thead><tbody>{scorer_rows}</tbody></table></section>
    <section><h2>Sert Hakemler</h2><table><thead><tr><th>Hakem</th><th>Maç</th><th>Kart/M</th><th>Gol/M</th></tr></thead><tbody>{ref_rows}</tbody></table></section>
  </main>
  <footer style="text-align:center;padding:40px 16px 28px;color:#8a9e92;font-size:12px;border-top:1px solid #e2e8e4;margin-top:48px;">
    metric11 &middot; <a href="mailto:hello@metric11.com" style="color:#8a9e92;text-decoration:none;border-bottom:1px solid #c5d4ca;">hello@metric11.com</a>
  </footer>
  <script defer src="/_vercel/insights/script.js"></script>
</body>
</html>
"""


if __name__ == "__main__":
    main()

