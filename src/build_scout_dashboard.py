from __future__ import annotations

import argparse
import json
from html import escape
from pathlib import Path

from src.config import PROCESSED_DIR


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
    return f"""<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Süper Lig Scout Paneli</title>
  <style>
    body {{ margin:0; font-family: Inter, system-ui, sans-serif; background:#f5f6f8; color:#17191c; }}
    header {{ background:#111318; color:white; padding:24px 40px; border-bottom:4px solid #d0182f; }}
    main {{ max-width:1280px; margin:0 auto; padding:24px; }}
    section {{ background:white; border:1px solid #d9dee7; border-radius:8px; margin-bottom:18px; padding:18px; box-shadow:0 8px 24px rgba(20,25,32,.08); }}
    h1 {{ margin:0 0 6px; }} h2 {{ margin:0 0 14px; font-size:18px; }}
    p {{ color:#667085; margin:0; }}
    table {{ width:100%; border-collapse:collapse; font-size:14px; }}
    th,td {{ padding:9px 7px; border-bottom:1px solid #d9dee7; text-align:left; vertical-align:top; }}
    th {{ color:#667085; font-size:12px; }}
  </style>
</head>
<body>
  <header>
    <h1>Süper Lig 2025-2026 Scout Paneli</h1>
    <p>TFF maç detaylarından üretilmiş MVP scout havuzu: takım güçleri, golcüler, scout kısa listesi ve hakem profilleri.</p>
  </header>
  <main>
    <section><h2>Takım Güçleri</h2><table><thead><tr><th>Takım</th><th>Puan</th><th>Gol</th><th>GF/M</th><th>GA/M</th><th>Kart/M</th></tr></thead><tbody>{team_rows}</tbody></table></section>
    <section><h2>Scout Kısa Liste</h2><table><thead><tr><th>Oyuncu</th><th>Takım</th><th>Scout</th><th>Gol</th><th>İlk 11</th><th>Gol/İlk 11</th><th>Disiplin</th></tr></thead><tbody>{scout_rows}</tbody></table></section>
    <section><h2>Golcü Listesi</h2><table><thead><tr><th>Oyuncu</th><th>Takım</th><th>Gol</th><th>İlk 11</th><th>Gol/İlk 11</th><th>Bitiricilik</th></tr></thead><tbody>{scorer_rows}</tbody></table></section>
    <section><h2>Sert Hakemler</h2><table><thead><tr><th>Hakem</th><th>Maç</th><th>Kart/M</th><th>Gol/M</th></tr></thead><tbody>{ref_rows}</tbody></table></section>
  </main>
</body>
</html>
"""


if __name__ == "__main__":
    main()

