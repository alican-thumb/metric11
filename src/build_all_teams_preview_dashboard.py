"""
Tüm 18 Süper Lig takımının maç önü arşiv raporlarını tek dashboard'da toplar.
Takım bazlı tahmin doğruluğu, kart sinyali ve kazanma olasılığı karşılaştırması üretir.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.config import PROCESSED_DIR, SEASON, SEASON_LABEL
from src.generate_preview_batch import ALL_TEAMS, team_slug
from src.html_utils import preview_nav_label


def main() -> None:
    parser = argparse.ArgumentParser(description="Tüm takım maç önü arşivini birleştiren dashboard üretir.")
    parser.add_argument("--output", default=str(PROCESSED_DIR / f"all_teams_preview_dashboard_{SEASON}.html"))
    args = parser.parse_args()

    team_data = load_all_teams()
    output = Path(args.output)
    output.write_text(build_html(team_data), encoding="utf-8")
    print(output)


def load_all_teams() -> list[dict]:
    results = []
    for team in ALL_TEAMS:
        slug = team_slug(team)
        index_path = PROCESSED_DIR / f"previews_{slug}_{SEASON}_chronological" / "index.json"
        if not index_path.exists():
            continue
        data = json.loads(index_path.read_text(encoding="utf-8"))
        summary = data.get("summary", {})
        reports = data.get("reports", [])
        results.append({
            "team": team,
            "slug": slug,
            "summary": summary,
            "reports": reports,
            "index_dir": f"previews_{slug}_{SEASON}_chronological",
        })
    results.sort(key=lambda t: -t["summary"].get("prediction_accuracy", 0))
    return results


def build_html(team_data: list[dict]) -> str:
    total_reports = sum(t["summary"].get("generated_reports", 0) for t in team_data)
    avg_accuracy = (
        round(sum(t["summary"].get("prediction_accuracy", 0) for t in team_data) / len(team_data) * 100, 1)
        if team_data else 0
    )
    best_team = team_data[0] if team_data else {}
    high_card_total = sum(t["summary"].get("high_card_signal_reports", 0) for t in team_data)

    ranking_rows = _build_ranking_rows(team_data)
    accuracy_chart = _build_accuracy_bars(team_data)
    recent_big_matches = _build_big_match_rows(team_data)

    return f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Maç Önü Arşivi — Süper Lig {SEASON_LABEL} | metric11</title>
<meta name="description" content="Süper Lig tüm takımlarının maç önü analizleri: olasılıklar, gol adayları, kadro sinyali ve hakem etkisi — metric11.">
<meta property="og:title" content="Maç Önü Arşivi — Süper Lig {SEASON_LABEL} | metric11">
<meta property="og:description" content="Süper Lig tüm takımlarının maç önü analizleri: olasılıklar, gol adayları, kadro sinyali ve hakem etkisi.">
<meta property="og:image" content="https://metric11.com/og-image.png">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:image" content="https://metric11.com/og-image.png">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<style>
  :root {{ --bg:#f3f5f4; --panel:#fff; --ink:#132018; --muted:#627067; --line:#d7ded9; --dark:#091810; --green:#116447; --lime:#cde94e; --red:#bd2936; --amber:#aa6b00; --blue:#22618c; }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: Inter, 'Segoe UI', Arial, sans-serif; background:var(--bg); color:var(--ink); }}
  .topbar {{ min-height:58px; padding:0 clamp(14px,3vw,32px); display:flex; align-items:center; justify-content:space-between; gap:18px; background:var(--dark); color:white; border-bottom:2px solid #1a3023; }}
  .brand {{ display:flex; align-items:center; gap:10px; color:white; text-decoration:none; font-size:18px; font-weight:800; letter-spacing:-0.2px; }}
  .brand:visited,.brand:active,.brand:hover {{ color:white; }}
  .brand b {{ width:28px; height:28px; border-radius:6px; display:grid; place-items:center; color:var(--dark); background:var(--lime); font-size:14px; font-weight:900; }}
  .brand .slbl {{ color:#6b7c72; font-size:11px; font-weight:500; border-left:1px solid #2a3d30; padding-left:8px; margin-left:2px; }}
  .topnav {{ display:flex; gap:2px; overflow-x:auto; overflow-y:hidden; -webkit-overflow-scrolling:touch; scrollbar-width:none; }}
  .topnav::-webkit-scrollbar {{ display:none; }}
  .topnav a {{ white-space:nowrap; flex-shrink:0; color:#8fa89a; padding:8px 11px; border-radius:6px; text-decoration:none; font-size:13px; font-weight:600; transition:background .15s,color .15s; }}
  .topnav a:visited {{ color:#8fa89a; }}
  .topnav a:hover {{ background:#162b20; color:white; }}
  .topnav a.active {{ background:#162b20; color:white; }}
  .header {{ background:#102419; border-bottom:3px solid var(--green); padding:24px clamp(14px,3vw,32px); }}
  .header-inner {{ max-width:1400px; margin:0 auto; }}
  .header h1 {{ font-size:34px; font-weight:700; color:white; }}
  .header .sub {{ color:#c1cec5; font-size:14px; margin-top:7px; }}
  .summary-bar {{ max-width:1400px; margin:0 auto; display:grid; grid-template-columns:repeat(5,minmax(0,1fr)); gap:10px; padding:18px clamp(12px,3vw,32px); }}
  .pill {{ background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:12px 14px; min-height:75px; }}
  .pill .val {{ font-size:23px; font-weight:700; color:var(--green); }}
  .pill .lbl {{ font-size:11px; color:var(--muted); margin-top:5px; }}
  .tabs {{ max-width:1400px; margin:0 auto; display:flex; padding:0 clamp(12px,3vw,32px); overflow-x:auto; }}
  .tab {{ padding:12px 16px; cursor:pointer; font-size:13px; color:var(--muted); border-bottom:2px solid transparent; white-space:nowrap; font-weight:600; }}
  .tab.active {{ color:var(--green); border-bottom-color:var(--green); }}
  .content {{ padding:18px clamp(12px,3vw,32px) 40px; max-width:1400px; margin:0 auto; }}
  .section {{ display: none; }}
  .section.active {{ display: block; }}
  .table-wrap {{ background:var(--panel); border:1px solid var(--line); border-radius:8px; overflow-x:auto; }}
  table {{ width:100%; min-width:720px; border-collapse:collapse; font-size:13px; }}
  th {{ background:#eef2ef; padding:11px 14px; text-align:left; color:var(--muted); font-weight:600; border-bottom:1px solid var(--line); white-space:nowrap; }}
  td {{ padding:11px 14px; border-bottom:1px solid #edf1ee; color:var(--ink); }}
  tr:hover td {{ background:#f7faf7; }}
  .acc-bar-wrap {{ display: flex; align-items: center; gap: 8px; }}
  .acc-bar {{ height:8px; border-radius:4px; background:#e5ebe7; flex:1; max-width:100px; }}
  .acc-fill {{ height: 100%; border-radius: 4px; }}
  .badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 700; color: #fff; }}
  .filter-bar {{ margin-bottom: 20px; }}
  .filter-input {{ background:white; border:1px solid var(--line); border-radius:6px; padding:10px 13px; color:var(--ink); font-size:14px; outline:none; width:min(300px,100%); }}
  .filter-input:focus {{ border-color:var(--green); }}
  .chart-section {{ margin-bottom: 32px; }}
  .chart-section {{ background:white; border:1px solid var(--line); border-radius:8px; padding:18px; }}
  .chart-section h2 {{ color:var(--ink); font-size:17px; margin-bottom:16px; }}
  .bar-row {{ display: flex; align-items: center; gap: 10px; margin-bottom: 7px; font-size: 0.8rem; }}
  .bar-label {{ color:var(--muted); min-width:190px; text-align:right; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
  .bar-outer {{ flex:1; height:18px; background:#e5ebe7; border-radius:3px; max-width:400px; }}
  .bar-inner {{ height: 100%; border-radius: 3px; }}
  .bar-val {{ color: #e2e8f0; min-width: 45px; font-weight: 600; }}
  a {{ color:var(--green); text-decoration:none; }}
  a:hover {{ text-decoration: underline; }}
  @media (max-width:850px) {{ .summary-bar {{ grid-template-columns:repeat(3,minmax(0,1fr)); }} .bar-label {{ min-width:120px; }} }}
  @media (max-width:600px) {{ .topbar {{ flex-direction:column; align-items:stretch; padding:11px 12px 0; gap:0; min-height:unset; }} .brand {{ padding-bottom:8px; }} .topnav {{ border-top:1px solid #1e3228; padding:7px 0 9px; justify-content:flex-start; }} .header h1 {{ font-size:26px; }} .summary-bar {{ grid-template-columns:repeat(2,minmax(0,1fr)); }} .content {{ padding-top:12px; }} .header {{ padding:20px 14px; }} .bar-row {{ gap:7px; }} .bar-label {{ min-width:90px; font-size:11px; }} }}
</style>
</head>
<body>
<div class="topbar">
  <a class="brand" href="/"><b>11</b> metric11<span class="slbl">Süper Lig 2025/26</span></a>
  <nav class="topnav"><a href="/">Gündem</a><a href="transfer_tracker_2025_2026.html">Transferler</a><a class="active" href="all_teams_preview_dashboard_2025_2026.html">{preview_nav_label()}</a><a href="transfer_recommendation_report_2025_2026.html">Scout</a><a href="football_intelligence_home.html">Analiz</a>
    <a href="european_predictions_2026_2027.html">⚽ Avrupa</a></nav>
</div>
<div class="header">
  <div class="header-inner"><h1>Süper Lig maç merkezi</h1>
  <div class="sub">{SEASON_LABEL} sezonu · tüm takımların kronolojik maç raporları · ham model başlangıç ölçümü</div></div>
</div>
<div style="background:#1e3a5f;border-bottom:1px solid #1e40af;padding:12px clamp(12px,3vw,32px);color:#bfdbfe;font-size:13px;">
  <strong style="color:#93c5fd;">Sezon arası ·</strong> 2025/26 lig sezonu tamamlandı. Arşiv maç raporları aktif, yeni tahminler 2026/27 fikstürü açıklanınca otomatik başlayacak. Yaz transfer analizi için <a href="transfer_season_context_2025_2026.html" style="color:#60a5fa;">Transfer Bağlamı</a> ve <a href="transfer_recommendation_report_2025_2026.html" style="color:#60a5fa;">Öneri Raporu</a>'nu incele.
</div>
<div class="summary-bar">
  <div class="pill"><div class="val">{len(team_data)}</div><div class="lbl">Takım</div></div>
  <div class="pill"><div class="val">{total_reports}</div><div class="lbl">Toplam Rapor</div></div>
  <div class="pill"><div class="val">%{avg_accuracy}</div><div class="lbl">Ham Model Ölçümü</div></div>
  <div class="pill"><div class="val" style="color:#ef4444">{high_card_total}</div><div class="lbl">Yüksek Kart Sinyali</div></div>
  <div class="pill"><div class="val" style="color:#22c55e">{best_team.get('team','').split()[0] if best_team else ''}</div><div class="lbl">En Yüksek Doğruluk</div></div>
</div>
<div class="tabs">
  <div class="tab active" onclick="showTab('ranking',this)">Takım Sıralaması</div>
  <div class="tab" onclick="showTab('chart',this)">Doğruluk Karşılaştırması</div>
  <div class="tab" onclick="showTab('bigmatches',this)">Büyük Maçlar</div>
</div>
<div class="content">
  <div id="ranking" class="section active">
    <div class="filter-bar">
      <input class="filter-input" id="teamFilter" placeholder="Takım ara..." oninput="filterRows()" />
    </div>
    <div class="table-wrap"><table id="rankTable">
      <thead><tr>
        <th>#</th><th>Takım</th><th>Rapor</th><th>Büyük Maç</th>
        <th>Yüksek Kart</th><th>Ham Model Ölçümü</th><th>Arşiv</th>
      </tr></thead>
      <tbody>{ranking_rows}</tbody>
    </table></div>
  </div>
  <div id="chart" class="section">
    <div class="chart-section">
      <h2>Takım Bazında Ham Model Ölçümü (%)</h2>
      {accuracy_chart}
    </div>
  </div>
  <div id="bigmatches" class="section">
    <div class="table-wrap"><table>
      <thead><tr>
        <th>Takım</th><th>Maç</th><th>Tarih</th><th>Kazanma %</th><th>Beraberlik %</th>
        <th>Skor Senaryosu</th><th>Ekran Tahmini</th><th>Kart</th>
      </tr></thead>
      <tbody>{recent_big_matches}</tbody>
    </table></div>
  </div>
</div>
<script>
function showTab(id, el) {{
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  el.classList.add('active');
}}
function filterRows() {{
  const q = document.getElementById('teamFilter').value.toLowerCase();
  document.querySelectorAll('#rankTable tbody tr').forEach(row => {{
    row.style.display = row.dataset.team.includes(q) ? '' : 'none';
  }});
}}
</script>
  <footer style="text-align:center;padding:40px 16px 28px;color:#8a9e92;font-size:12px;border-top:1px solid #e2e8e4;margin-top:48px;">
    metric11 &middot; <a href="mailto:hello@metric11.com" style="color:#8a9e92;text-decoration:none;border-bottom:1px solid #c5d4ca;">hello@metric11.com</a>
  </footer>
  <script defer src="/_vercel/insights/script.js"></script>
</body>
</html>"""


def _acc_color(acc: float) -> str:
    if acc >= 0.60:
        return "#116447"
    if acc >= 0.50:
        return "#22618c"
    if acc >= 0.40:
        return "#aa6b00"
    return "#bd2936"


def _build_ranking_rows(team_data: list[dict]) -> str:
    rows = ""
    for rank, t in enumerate(team_data, 1):
        s = t["summary"]
        acc = s.get("prediction_accuracy", 0)
        acc_color = _acc_color(acc)
        bar_w = round(acc * 100)
        slug = t["slug"]
        dashboard_link = f"{slug}_{SEASON}_dashboard_chronological.html"
        archive_link = f"previews_{slug}_{SEASON}_chronological/index.md"
        rows += (
            f"<tr data-team='{t['team'].lower()}'>"
            f"<td style='color:#627067;font-weight:600'>{rank}</td>"
            f"<td style='font-weight:600;color:#132018'><a href='{dashboard_link}' style='color:inherit;text-decoration:none'>{t['team']}</a></td>"
            f"<td>{s.get('generated_reports', 0)}</td>"
            f"<td>{s.get('big_match_reports', 0)}</td>"
            f"<td style='color:#bd2936'>{s.get('high_card_signal_reports', 0)}</td>"
            f"<td>"
            f"<div class='acc-bar-wrap'>"
            f"<span style='color:{acc_color};font-weight:700;min-width:42px'>%{round(acc * 100)}</span>"
            f"<div class='acc-bar'><div class='acc-fill' style='width:{bar_w}%;background:{acc_color}'></div></div>"
            f"</div>"
            f"</td>"
            f"<td><a href='{dashboard_link}'>panel →</a> <a href='{archive_link}' style='margin-left:8px;color:#627067'>arşiv</a></td>"
            f"</tr>"
        )
    return rows


def _build_accuracy_bars(team_data: list[dict]) -> str:
    sorted_data = sorted(team_data, key=lambda t: -t["summary"].get("prediction_accuracy", 0))
    max_acc = max((t["summary"].get("prediction_accuracy", 0) for t in sorted_data), default=1)
    bars = ""
    for t in sorted_data:
        acc = t["summary"].get("prediction_accuracy", 0)
        color = _acc_color(acc)
        bar_w = round((acc / max_acc) * 100) if max_acc else 0
        short_name = t["team"].split()[0]
        bars += (
            f"<div class='bar-row'>"
            f"<div class='bar-label'>{short_name}</div>"
            f"<div class='bar-outer'><div class='bar-inner' style='width:{bar_w}%;background:{color}'></div></div>"
            f"<div class='bar-val' style='color:{color}'>%{round(acc * 100)}</div>"
            f"</div>"
        )
    return bars


def _build_big_match_rows(team_data: list[dict]) -> str:
    all_big: list[dict] = []
    for t in team_data:
        for r in t["reports"]:
            if r.get("is_big_match"):
                all_big.append({**r, "_team": t["team"]})
    all_big.sort(key=lambda r: r.get("date", ""), reverse=True)
    rows = ""
    for r in all_big[:60]:
        card_color = "#ef4444" if r.get("card_signal") == "HIGH" else "#d97706" if r.get("card_signal") == "MEDIUM" else "#64748b"
        card_label = {"HIGH": "Yüksek", "MEDIUM": "Orta", "LOW": "Düşük"}.get(r.get("card_signal"), r.get("card_signal", ""))
        rows += (
            f"<tr>"
            f"<td style='font-size:0.75rem;color:#627067'>{r['_team'].split()[0]}</td>"
            f"<td style='font-weight:600'>{r.get('home_team','')} - {r.get('away_team','')}</td>"
            f"<td style='color:#627067'>{r.get('date','')}</td>"
            f"<td>%{round(r.get('target_win_probability',0)*100)}</td>"
            f"<td>%{round(r.get('draw_probability',0)*100)}</td>"
            f"<td>{r.get('recommended_scoreline') or '—'}</td>"
            f"<td>{r.get('final_prediction_label') or '—'}</td>"
            f"<td><span class='badge' style='background:{card_color}'>{card_label}</span></td>"
            f"</tr>"
        )
    return rows


if __name__ == "__main__":
    main()
