from __future__ import annotations

import argparse
import json
from html import escape
from pathlib import Path

from src.config import PROCESSED_DIR, TRANSFER_WATCH_SEASON_LABEL
from src.html_utils import nav_links_html


def main() -> None:
    parser = argparse.ArgumentParser(description="Zenginlestirilmis scout dashboard uretir.")
    parser.add_argument("--input", default=str(PROCESSED_DIR / "league_scouting_enriched_2025_2026.json"))
    parser.add_argument("--output", default=str(PROCESSED_DIR / "league_scouting_enriched_2025_2026_dashboard.html"))
    args = parser.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    output = Path(args.output)
    output.write_text(build_html(payload), encoding="utf-8")
    print(output)


def _mv_str(eur: int | None) -> str:
    if not eur:
        return "—"
    if eur >= 1_000_000:
        return f"€{eur / 1_000_000:.1f}M"
    if eur >= 1_000:
        return f"€{eur // 1000}K"
    return f"€{eur}"


def _contract_badge(risk: str) -> str:
    colors = {
        "EXPIRING_SOON": ("#dc2626", "#fef2f2", "Bitiyor"),
        "FINAL_YEAR":    ("#d97706", "#fffbeb", "Son Yıl"),
        "SECURE":        ("#16a34a", "#f0fdf4", "Güvende"),
    }
    col, bg, label = colors.get(risk, ("#6b7280", "#f9fafb", risk))
    return f'<span style="font-size:10px;font-weight:700;color:{col};background:{bg};padding:2px 7px;border-radius:4px">{label}</span>'


def _resale_badge(signal: str) -> str:
    colors = {"HIGH": "#16a34a", "MEDIUM": "#d97706", "LOW": "#dc2626"}
    col = colors.get(signal, "#6b7280")
    return f'<span style="font-size:10px;font-weight:700;color:{col}">{signal}</span>'


def _player_card(p: dict) -> str:
    name = escape(p.get("name", ""))
    team = escape(p.get("team", ""))
    age = p.get("age", "")
    pos = escape(str(p.get("tm_position") or p.get("tm_position_group") or ""))
    nat = escape(str(p.get("nationality") or ""))
    goals = p.get("goals", 0)
    starts = p.get("starts", 0)
    opp = p.get("opportunity_score", 0)
    scout = p.get("scout_value_score", 0)
    mv = _mv_str(p.get("tm_market_value_eur"))
    contract_end = escape(str(p.get("contract_end") or ""))
    risk = p.get("contract_risk", "")
    resale = p.get("resale_signal", "")
    tm_url = p.get("tm_profile_url") or ""
    pos_group = escape(str(p.get("tm_position_group") or ""))

    opp_color = "#16a34a" if opp >= 7 else ("#d97706" if opp >= 4 else "#6b7280")
    name_html = (
        f'<a href="{escape(tm_url)}" target="_blank" rel="noopener" '
        f'style="color:var(--ink);text-decoration:none;font-weight:700;border-bottom:1px dotted var(--border)">'
        f'{name}</a>'
        if tm_url else f'<span style="font-weight:700">{name}</span>'
    )

    return (
        f'<tr data-pos="{pos_group}" data-team="{team}" data-name="{name.lower()}">'
        f'<td style="min-width:140px">{name_html}</td>'
        f'<td style="font-size:12px;color:var(--muted)">{team}</td>'
        f'<td style="font-size:12px;color:{opp_color};font-weight:700">{opp}</td>'
        f'<td style="font-size:12px">{scout}</td>'
        f'<td style="font-size:12px">{pos}</td>'
        f'<td style="font-size:12px">{age}</td>'
        f'<td style="font-size:12px">{nat}</td>'
        f'<td style="font-size:12px;font-weight:600;color:#f59e0b">{mv}</td>'
        f'<td style="font-size:12px">{goals}</td>'
        f'<td style="font-size:12px;color:var(--muted)">{starts}</td>'
        f'<td style="font-size:12px">{contract_end}</td>'
        f'<td>{_contract_badge(risk)}</td>'
        f'<td>{_resale_badge(resale)}</td>'
        f'</tr>'
    )


_JS = """
<script>
var _rows = null;
function getRows() {
  if (!_rows) _rows = Array.from(document.querySelectorAll('#playerTbody tr'));
  return _rows;
}
function applyFilters() {
  var q = document.getElementById('searchBox').value.toLowerCase();
  var pos = document.getElementById('posFilter').value;
  var contract = document.getElementById('contractFilter').value;
  var rows = getRows();
  var shown = 0;
  rows.forEach(function(r) {
    var nameMatch = !q || r.dataset.name.includes(q) || r.dataset.team.toLowerCase().includes(q);
    var posMatch = !pos || r.dataset.pos === pos;
    var cells = r.querySelectorAll('td');
    var riskText = cells[11] ? cells[11].textContent.trim() : '';
    var contractMatch = !contract ||
      (contract === 'EXPIRING_SOON' && riskText === 'Bitiyor') ||
      (contract === 'FINAL_YEAR' && riskText === 'Son Yıl') ||
      (contract === 'SECURE' && riskText === 'Güvende');
    var show = nameMatch && posMatch && contractMatch;
    r.style.display = show ? '' : 'none';
    if (show) shown++;
  });
  document.getElementById('shownCount').textContent = shown;
}
function sortTable(col) {
  var tbody = document.getElementById('playerTbody');
  var rows = Array.from(tbody.querySelectorAll('tr'));
  var asc = tbody.dataset.sortCol === col && tbody.dataset.sortDir !== 'desc';
  rows.sort(function(a, b) {
    var av = a.querySelectorAll('td')[col] ? a.querySelectorAll('td')[col].textContent.trim() : '';
    var bv = b.querySelectorAll('td')[col] ? b.querySelectorAll('td')[col].textContent.trim() : '';
    var an = parseFloat(av.replace(/[^0-9.-]/g,'')); var bn = parseFloat(bv.replace(/[^0-9.-]/g,''));
    if (!isNaN(an) && !isNaN(bn)) return asc ? bn - an : an - bn;
    return asc ? av.localeCompare(bv) : bv.localeCompare(av);
  });
  rows.forEach(function(r){ tbody.appendChild(r); });
  tbody.dataset.sortCol = col; tbody.dataset.sortDir = asc ? 'desc' : 'asc';
  _rows = null;
}
</script>
"""


def build_html(payload: dict) -> str:
    summary = payload["summary"]
    all_players = payload["enriched_shortlist"]

    # Tüm benzersiz pozisyon grupları
    pos_groups = sorted({p.get("tm_position_group", "") for p in all_players if p.get("tm_position_group")})
    pos_options = "".join(
        f'<option value="{escape(pg)}">{escape(pg)}</option>' for pg in pos_groups
    )

    rows_html = "".join(_player_card(p) for p in all_players)
    total = len(all_players)
    expiring = sum(1 for p in all_players if p.get("contract_risk") == "EXPIRING_SOON")
    final_yr = sum(1 for p in all_players if p.get("contract_risk") == "FINAL_YEAR")
    u24 = summary.get("u24_players", 0)
    with_mv = sum(1 for p in all_players if p.get("tm_market_value_eur"))

    return f"""<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Scout Havuzu {TRANSFER_WATCH_SEASON_LABEL} | metric11</title>
  <meta name="description" content="Süper Lig 691 oyuncu scout veri havuzu — {TRANSFER_WATCH_SEASON_LABEL} transfer planlaması. Fırsat skoru, piyasa değeri, sözleşme durumu.">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <style>
    :root{{--bg:#09111f;--panel:#0e1929;--panel2:#13223a;--ink:#e2e8f0;--muted:#64748b;--border:#1e3a5f;}}
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
    .hero{{background:linear-gradient(160deg,#0a1929 0%,#060e1d 100%);padding:24px clamp(12px,3vw,32px) 20px;border-bottom:1px solid var(--border)}}
    .hero h1{{font-size:clamp(18px,3vw,26px);font-weight:800;color:white;margin-bottom:6px}}
    .hero p{{font-size:13px;color:var(--muted)}}
    .stat-bar{{display:flex;gap:10px;padding:14px clamp(12px,3vw,32px);flex-wrap:wrap;border-bottom:1px solid var(--border)}}
    .stat-chip{{background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:9px 14px;text-align:center;min-width:100px}}
    .stat-chip .v{{font-size:18px;font-weight:800}}
    .stat-chip .l{{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:.5px;margin-top:2px}}
    .filter-bar{{display:flex;gap:10px;flex-wrap:wrap;padding:14px clamp(12px,3vw,32px);border-bottom:1px solid var(--border);align-items:center}}
    .filter-bar input,.filter-bar select{{background:var(--panel);border:1px solid var(--border);color:var(--ink);padding:7px 12px;border-radius:6px;font-size:13px;min-width:160px}}
    .filter-bar input::placeholder{{color:var(--muted)}}
    .shown-count{{font-size:12px;color:var(--muted);margin-left:auto}}
    .table-wrap{{overflow-x:auto;padding:0 clamp(12px,3vw,32px) 60px}}
    table{{width:100%;border-collapse:collapse;font-size:13px;margin-top:12px}}
    th{{color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.5px;padding:8px 10px;border-bottom:1px solid var(--border);white-space:nowrap;cursor:pointer;background:var(--bg)}}
    th:hover{{color:var(--ink)}}
    td{{padding:8px 10px;border-bottom:1px solid rgba(30,58,95,.4);vertical-align:middle}}
    tr:hover td{{background:rgba(14,25,41,.6)}}
    @media(max-width:660px){{.filter-bar{{flex-direction:column;align-items:stretch}}.shown-count{{margin-left:0}}}}
  </style>
</head>
<body>
<div class="topbar">
  <a class="brand" href="/"><b>11</b> metric11</a>
  <nav class="topnav">{nav_links_html("transfer_recommendation_report_2025_2026.html")}</nav>
</div>

<div class="hero">
  <h1>Scout Havuzu <span style="color:#cde94e">{TRANSFER_WATCH_SEASON_LABEL}</span></h1>
  <p>Süper Lig 2025-26 sezonu verisine dayalı · Fırsat skoru, Transfermarkt piyasa değeri, sözleşme durumu · Günlük güncellenir</p>
</div>

<div class="stat-bar">
  <div class="stat-chip"><div class="v">{total}</div><div class="l">Toplam Oyuncu</div></div>
  <div class="stat-chip"><div class="v" style="color:#dc2626">{expiring}</div><div class="l">Sözleşme Bitiyor</div></div>
  <div class="stat-chip"><div class="v" style="color:#d97706">{final_yr}</div><div class="l">Son Yıl Kontrat</div></div>
  <div class="stat-chip"><div class="v" style="color:#60a5fa">{u24}</div><div class="l">U24 Oyuncu</div></div>
  <div class="stat-chip"><div class="v" style="color:#f59e0b">{with_mv}</div><div class="l">TM Değeri Var</div></div>
</div>

<div class="filter-bar">
  <input type="search" id="searchBox" placeholder="Oyuncu veya takım ara..." oninput="applyFilters()">
  <select id="posFilter" onchange="applyFilters()">
    <option value="">Tüm Pozisyonlar</option>
    {pos_options}
  </select>
  <select id="contractFilter" onchange="applyFilters()">
    <option value="">Tüm Sözleşmeler</option>
    <option value="EXPIRING_SOON">Bitiyor</option>
    <option value="FINAL_YEAR">Son Yıl</option>
    <option value="SECURE">Güvende</option>
  </select>
  <span class="shown-count"><span id="shownCount">{total}</span> oyuncu gösteriliyor</span>
</div>

<div class="table-wrap">
  <table>
    <thead>
      <tr>
        <th onclick="sortTable(0)">Oyuncu ↕</th>
        <th onclick="sortTable(1)">Takım ↕</th>
        <th onclick="sortTable(2)" title="Fırsat skoru (0-10)">Fırsat ↕</th>
        <th onclick="sortTable(3)" title="Scout değer skoru">Scout ↕</th>
        <th onclick="sortTable(4)">Pozisyon ↕</th>
        <th onclick="sortTable(5)">Yaş ↕</th>
        <th onclick="sortTable(6)">Milliyet ↕</th>
        <th onclick="sortTable(7)">TM Değeri ↕</th>
        <th onclick="sortTable(8)">Gol ↕</th>
        <th onclick="sortTable(9)">İlk11 ↕</th>
        <th onclick="sortTable(10)">Kontrat Bitiş ↕</th>
        <th>Risk</th>
        <th>Resale</th>
      </tr>
    </thead>
    <tbody id="playerTbody">
      {rows_html}
    </tbody>
  </table>
</div>

<script defer src="/_vercel/insights/script.js"></script>
{_JS}
</body>
</html>"""


if __name__ == "__main__":
    main()
