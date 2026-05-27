from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path

from src.config import PROCESSED_DIR, SEASON
from src.html_utils import preview_nav_label

TRANSFER_SEASON_START = datetime(2026, 5, 18, tzinfo=timezone.utc)
TRANSFER_SEASON_END   = datetime(2026, 9, 1, tzinfo=timezone.utc)

# Slug → transfer sinyallerindeki kulüp adı eşleştirmesi
SLUG_TO_TRANSFER_NAME: dict[str, str] = {
    "besiktas": "Beşiktaş",
    "galatasaray": "Galatasaray",
    "fenerbahce": "Fenerbahçe",
    "trabzonspor": "Trabzonspor",
    "basaksehir": "Başakşehir",
    "alanyaspor": "Alanyaspor",
    "samsunspor": "Samsunspor",
    "goztepe": "Göztepe",
    "konyaspor": "Konyaspor",
    "rizespor": "Rizespor",
    "gaziantep": "Gaziantep FK",
    "kasimpasa": "Kasımpaşa",
    "kocaelispor": "Kocaelispor",
    "eyupspor": "Eyüpspor",
    "genclerbirligi": "Gençlerbirliği",
    "karagumruk": "Fatih Karagümrük",
    "antalyaspor": "Antalyaspor",
    "kayserispor": "Kayserispor",
}

TFF_CLUB_FRAGMENTS: dict[str, str] = {
    "besiktas": "BEŞİKTAŞ",
    "galatasaray": "GALATASARAY",
    "fenerbahce": "FENERBAHÇE",
    "trabzonspor": "TRABZONSPOR",
    "basaksehir": "BAŞAKŞEHİR",
    "alanyaspor": "ALANYA",
    "samsunspor": "SAMSUN",
    "goztepe": "GÖZTEPE",
    "konyaspor": "KONYA",
    "rizespor": "RİZE",
    "gaziantep": "GAZİANTEP",
    "kasimpasa": "KASIMPAŞA",
    "kocaelispor": "KOCAELİ",
    "eyupspor": "EYÜP",
    "genclerbirligi": "GENÇLERBİRLİĞİ",
    "karagumruk": "KARAGÜMRÜK",
    "antalyaspor": "ANTALYA",
    "kayserispor": "KAYSERİ",
}


def _is_transfer_season() -> bool:
    now = datetime.now(timezone.utc)
    return TRANSFER_SEASON_START <= now <= TRANSFER_SEASON_END


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def _mv(eur: int | None) -> str:
    if not eur:
        return ""
    if eur >= 1_000_000:
        return f" · €{eur / 1_000_000:.1f}M"
    return f" · €{eur // 1000}K"


def _transfer_window_section(slug: str, team_display: str) -> str:
    transfer_name = SLUG_TO_TRANSFER_NAME.get(slug, team_display)
    tff_fragment = TFF_CLUB_FRAGMENTS.get(slug, team_display.upper())

    # Transfer sinyalleri
    intel = _load_json(PROCESSED_DIR / f"news_intelligence_{SEASON}.json")
    all_signals = intel.get("transfers", [])
    team_signals = [
        s for s in all_signals
        if (s.get("to_club") or "").lower() == transfer_name.lower()
        or (s.get("from_club") or "").lower() == transfer_name.lower()
    ]

    # Sözleşme bitenler (transfer_season_context)
    ctx = _load_json(PROCESSED_DIR / f"transfer_season_context_{SEASON}.json")
    free_agents = [
        p for p in ctx.get("free_agents_top20", [])
        if tff_fragment in (p.get("team") or "").upper()
    ]
    final_year = [
        p for p in ctx.get("final_year_top20", [])
        if tff_fragment in (p.get("team") or "").upper()
    ]

    if not team_signals and not free_agents and not final_year:
        return ""

    rows_html = ""
    STATUS_COLOR = {
        "OFFICIAL": ("#16a34a", "#dcfce7", "RESMİ"),
        "CORROBORATED": ("#2563eb", "#dbeafe", "DOĞRULANDI"),
        "RUMOR": ("#d97706", "#fef3c7", "SÖYLENTI"),
        "REVIEW_REQUIRED": ("#6b7280", "#f1f5f9", "TAKİPTE"),
    }
    for s in team_signals[:6]:
        player = escape(s.get("player_name") or "?")
        to_c   = escape(s.get("to_club") or "—")
        frm    = escape(s.get("from_club") or "—")
        vs     = f"{frm} → {to_c}"
        st     = s.get("verification_status") or "REVIEW_REQUIRED"
        col, bg, lbl = STATUS_COLOR.get(st, ("#6b7280", "#f1f5f9", st))
        mv     = _mv(s.get("tm_market_value_eur"))
        title  = escape((s.get("title") or "")[:70])
        link   = s.get("link", "")
        link_tag = f'<a href="{escape(link)}" target="_blank" style="color:#116447;font-size:11px;display:block;margin-top:3px">{title}</a>' if link else ""
        rows_html += f"""<div style="padding:10px 0;border-bottom:1px solid #e8eeed">
  <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap">
    <strong style="font-size:14px">{player}</strong>
    <span style="font-size:11px;color:#627067">{vs}{mv}</span>
    <span style="font-size:10px;padding:1px 7px;border-radius:4px;font-weight:700;color:{col};background:{bg}">{lbl}</span>
  </div>
  {link_tag}
</div>"""

    expiry_html = ""
    if free_agents or final_year:
        expiry_rows = ""
        for p in free_agents[:4]:
            name = escape(p.get("name") or "?")
            mv2  = _mv(p.get("market_value_eur"))
            expiry_rows += f'<div style="padding:5px 0;border-bottom:1px solid #e8eeed;font-size:13px"><strong>{name}</strong><span style="color:#bd2936;font-size:11px;margin-left:6px">Sözleşme bitiyor{mv2}</span></div>'
        for p in final_year[:3]:
            name = escape(p.get("name") or "?")
            mv2  = _mv(p.get("market_value_eur"))
            expiry_rows += f'<div style="padding:5px 0;border-bottom:1px solid #e8eeed;font-size:13px"><strong>{name}</strong><span style="color:#d97706;font-size:11px;margin-left:6px">Son yıl{mv2}</span></div>'
        if expiry_rows:
            expiry_html = f"""<div style="margin-top:16px">
  <div style="font-size:12px;font-weight:700;color:#627067;text-transform:uppercase;letter-spacing:.05em;margin-bottom:8px">Sözleşme Durumu</div>
  {expiry_rows}
</div>"""

    signals_block = f"""<div style="margin-bottom:4px">
  <div style="font-size:12px;font-weight:700;color:#627067;text-transform:uppercase;letter-spacing:.05em;margin-bottom:8px">Transfer Sinyalleri ({len(team_signals)})</div>
  {rows_html if rows_html else '<p style="color:#627067;font-size:13px">Henüz sinyal yok.</p>'}
</div>""" if team_signals else ""

    return f"""<div style="background:#fff;border:1px solid #d7ded9;border-radius:12px;padding:20px 24px;margin-bottom:20px">
  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;flex-wrap:wrap;gap:8px">
    <div>
      <span style="font-size:12px;font-weight:700;color:#116447;text-transform:uppercase;letter-spacing:.05em">Transfer Penceresi</span>
      <h3 style="margin:4px 0 0;font-size:17px;color:#132018">{escape(team_display)} — Yaz 2026</h3>
    </div>
    <a href="transfer_tracker_{SEASON}.html" style="font-size:12px;color:#116447;font-weight:600;text-decoration:none">Tüm transfer radarı →</a>
  </div>
  {signals_block}
  {expiry_html}
</div>"""

TEAM_DISPLAY_NAMES: dict[str, str] = {
    "besiktas": "Beşiktaş",
    "galatasaray": "Galatasaray",
    "fenerbahce": "Fenerbahçe",
    "trabzonspor": "Trabzonspor",
    "basaksehir": "Başakşehir",
    "alanyaspor": "Alanyaspor",
    "samsunspor": "Samsunspor",
    "goztepe": "Göztepe",
    "konyaspor": "Konyaspor",
    "rizespor": "Rizespor",
    "gaziantep": "Gaziantep FK",
    "kasimpasa": "Kasımpaşa",
    "kocaelispor": "Kocaelispor",
    "eyupspor": "Eyüpspor",
    "genclerbirligi": "Gençlerbirliği",
    "karagumruk": "Fatih Karagümrük",
    "antalyaspor": "Antalyaspor",
    "kayserispor": "Kayserispor",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Mac onu raporlari icin statik HTML dashboard uretir.")
    parser.add_argument("--team-slug", default="besiktas")
    parser.add_argument("--team-name", default=None)
    parser.add_argument("--index", default=None)
    parser.add_argument("--goal-backtest", default=str(PROCESSED_DIR / "goal_candidate_backtest_2025_2026.json"))
    parser.add_argument("--output", default=None)
    parser.add_argument("--all-teams", action="store_true", help="Tüm 18 takım için dashboard üret")
    args = parser.parse_args()

    if args.all_teams:
        for slug, name in TEAM_DISPLAY_NAMES.items():
            _build_for_team(slug, name, args.goal_backtest)
    else:
        slug = args.team_slug
        name = args.team_name or TEAM_DISPLAY_NAMES.get(slug, slug.title())
        _build_for_team(slug, name, args.goal_backtest, args.index, args.output)


def _build_for_team(slug: str, team_name: str, goal_backtest_path_str: str, index_path_str: str | None = None, output_path_str: str | None = None) -> None:
    index_path = Path(index_path_str) if index_path_str else PROCESSED_DIR / f"previews_{slug}_{SEASON}_chronological" / "index.json"
    output_path = Path(output_path_str) if output_path_str else PROCESSED_DIR / f"{slug}_{SEASON}_dashboard_chronological.html"

    if not index_path.exists():
        print(f"Atlandı ({team_name}): {index_path} bulunamadı")
        return

    index_payload = json.loads(index_path.read_text(encoding="utf-8"))
    goal_backtest = {}
    goal_backtest_path = Path(goal_backtest_path_str)
    if goal_backtest_path.exists():
        goal_backtest = json.loads(goal_backtest_path.read_text(encoding="utf-8")).get("summary", {})
    previews = []
    for report in index_payload["reports"]:
        # json_path may be an absolute CI path; resolve relative to index dir
        p = Path(report["json_path"])
        if not p.exists():
            p = index_path.parent / p.name
        if not p.exists():
            continue
        preview = json.loads(p.read_text(encoding="utf-8"))
        previews.append(preview)

    today = datetime.now(timezone.utc).date()
    has_upcoming = any(
        _parse_match_date(p.get("match", {}).get("date", "")) is not None
        and _parse_match_date(p.get("match", {}).get("date", "")) > today  # type: ignore[operator]
        for p in previews
    )
    output_path.write_text(
        build_html(index_payload["summary"], previews, goal_backtest, team_name, is_off_season=not has_upcoming, team_slug=slug),
        encoding="utf-8",
    )
    print(output_path)


def _parse_match_date(date_str: str):
    try:
        return datetime.strptime(date_str.split(" - ")[0].strip(), "%d.%m.%Y").date()
    except ValueError:
        return None


def build_html(summary: dict, previews: list[dict], goal_backtest: dict, team_name: str = "Beşiktaş", is_off_season: bool = False, team_slug: str = "besiktas") -> str:
    data_json = (
        json.dumps({"summary": summary, "goal_backtest": goal_backtest, "previews": previews}, ensure_ascii=False)
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
    )
    options = "\n".join(
        f'<option value="{idx}">{idx + 6}. hafta - {escape(p["match"]["home_team"])} vs {escape(p["match"]["away_team"])}</option>'
        for idx, p in enumerate(previews)
    )
    off_season_banner = (
        '<div style="background:#e8f5ee;border-left:4px solid #116447;border-radius:8px;padding:14px 20px;'
        'margin-bottom:20px;color:#132018;font-size:14px;line-height:1.6;">'
        '<strong style="color:#116447;">Sezon arası</strong> &mdash; 2025/26 sezonu tamamlandı. '
        'Geçmiş maç analizleri ve tahmin arşivi aşağıda incelenebilir. '
        '2026/27 fikstürü açıklandığında tahminler otomatik olarak güncellenir.</div>'
    ) if is_off_season else ""
    transfer_section = _transfer_window_section(team_slug, team_name) if _is_transfer_season() else ""
    return f"""<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(team_name)} Maç Önü — Süper Lig 2025/26 | metric11</title>
  <meta name="description" content="{escape(team_name)} 2025/26 sezonu maç önü analizleri: olasılıklar, gol adayları ve kadro sinyali — metric11.">
  <meta property="og:title" content="{escape(team_name)} Maç Önü — metric11">
  <meta property="og:description" content="{escape(team_name)} 2025/26 sezonu maç önü analizleri: olasılıklar, gol adayları ve kadro sinyali.">
  <meta property="og:image" content="https://metric11.com/og-image.png">
  <meta property="og:type" content="website">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:image" content="https://metric11.com/og-image.png">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <style>
    :root {{
      --bg: #f3f5f4;
      --panel: #ffffff;
      --ink: #132018;
      --muted: #627067;
      --line: #d7ded9;
      --accent: #116447;
      --accent-2: #116447;
      --lime: #cde94e;
      --dark: #091810;
      --warn: #b76b00;
      --bad: #bd2936;
      --shadow: 0 8px 24px rgba(20, 25, 32, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--ink);
    }}
    .topbar {{
      position: sticky;
      top: 0;
      z-index: 5;
      min-height: 58px;
      padding: 0 clamp(14px, 3vw, 32px);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 18px;
      background: var(--dark);
      border-bottom: 2px solid #1a3023;
    }}
    .brand {{
      display: flex;
      align-items: center;
      gap: 10px;
      color: white;
      text-decoration: none;
      font-weight: 800;
      font-size: 18px;
      letter-spacing: -0.2px;
    }}
    .brand:visited,.brand:active,.brand:hover {{ color: white; }}
    .brand b {{
      display: grid;
      place-items: center;
      width: 28px;
      height: 28px;
      border-radius: 6px;
      color: var(--dark);
      background: var(--lime);
      font-size: 14px;
      font-weight: 900;
    }}
    .brand .slbl {{ color:#6b7c72; font-size:11px; font-weight:500; border-left:1px solid #2a3d30; padding-left:8px; margin-left:2px; }}
    .topnav {{ display: flex; gap: 2px; overflow-x: auto; overflow-y: hidden; -webkit-overflow-scrolling: touch; scrollbar-width: none; }}
    .topnav::-webkit-scrollbar {{ display: none; }}
    .topnav a {{
      white-space: nowrap;
      flex-shrink: 0;
      color: #8fa89a;
      padding: 8px 11px;
      border-radius: 6px;
      text-decoration: none;
      font-size: 13px;
      font-weight: 600;
      transition: background .15s, color .15s;
    }}
    .topnav a:visited {{ color: #8fa89a; }}
    .topnav a:hover {{ background: #162b20; color: white; }}
    .topnav a.active {{ background: #162b20; color: white; }}
    header {{
      background: #102419;
      color: white;
      padding: 24px clamp(18px, 4vw, 48px);
      border-bottom: 3px solid var(--accent);
    }}
    header > div {{ max-width: 1280px; margin: 0 auto; }}
    header h1 {{
      margin: 0 0 6px;
      font-size: 36px;
      letter-spacing: 0;
    }}
    header p {{ margin: 0; color: #c1cec5; max-width: 980px; line-height: 1.5; }}
    main {{
      max-width: 1280px;
      margin: 0 auto;
      padding: 22px clamp(14px, 3vw, 32px) 42px;
    }}
    .toolbar {{
      display: grid;
      grid-template-columns: minmax(260px, 1fr) repeat(4, minmax(130px, 180px));
      gap: 12px;
      align-items: stretch;
      margin-bottom: 16px;
    }}
    select, .metric, section {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: var(--shadow);
    }}
    select {{
      width: 100%;
      min-height: 56px;
      padding: 0 14px;
      color: var(--ink);
      font-size: 15px;
    }}
    .metric {{
      padding: 12px 14px;
      min-height: 56px;
    }}
    .metric span {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.2;
    }}
    .metric strong {{
      display: block;
      font-size: 20px;
      margin-top: 4px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: minmax(0, 1.15fr) minmax(0, 0.85fr);
      gap: 16px;
    }}
    section {{
      padding: 18px;
      margin-bottom: 16px;
      overflow-x: auto;
    }}
    h2 {{
      margin: 0 0 14px;
      font-size: 18px;
      letter-spacing: 0;
    }}
    .fixture {{
      display: flex;
      flex-wrap: wrap;
      align-items: baseline;
      gap: 10px;
      margin-bottom: 12px;
    }}
    .fixture strong {{ font-size: 30px; }}
    .fixture span {{ color: var(--muted); }}
    .prob-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 10px;
    }}
    .prob {{
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      min-height: 92px;
    }}
    .prob label {{ color: var(--muted); font-size: 13px; }}
    .prob b {{ display: block; font-size: 28px; margin: 6px 0; }}
    .bar {{
      height: 7px;
      border-radius: 999px;
      background: #e7ebf1;
      overflow: hidden;
    }}
    .bar i {{
      display: block;
      height: 100%;
      background: var(--accent);
      width: var(--w);
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }}
    th, td {{
      text-align: left;
      border-bottom: 1px solid var(--line);
      padding: 9px 6px;
      vertical-align: top;
    }}
    th {{ color: var(--muted); font-size: 12px; font-weight: 600; }}
    .pill {{
      display: inline-flex;
      align-items: center;
      min-height: 26px;
      border-radius: 999px;
      padding: 0 10px;
      border: 1px solid var(--line);
      font-size: 12px;
      background: #f9fafb;
    }}
    .pill.high {{ color: var(--bad); border-color: #f0bac1; background: #fff1f3; }}
    .pill.medium {{ color: var(--warn); border-color: #f4d197; background: #fff8eb; }}
    .pill.low {{ color: var(--accent-2); border-color: #b7dfd0; background: #eefbf6; }}
    .narrative p {{
      margin: 0 0 12px;
      color: #30343a;
      line-height: 1.58;
    }}
    .muted {{ color: var(--muted); }}
    @media (max-width: 900px) {{
      .grid, .prob-grid {{ grid-template-columns: 1fr; }}
      .toolbar {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .toolbar select {{ grid-column: 1 / -1; }}
    }}
    @media (max-width: 680px) {{
      .topbar {{ position: static; flex-direction: column; align-items: stretch; padding: 11px 12px 0; gap: 0; min-height: unset; }}
      .brand {{ padding-bottom: 8px; }}
      .topnav {{ border-top: 1px solid #1e3228; padding: 7px 0 9px; justify-content: flex-start; }}
      header {{ padding: 18px 14px; }}
      header h1 {{ font-size: 22px; }}
      .fixture strong {{ font-size: 21px; }}
      .prob b {{ font-size: 22px; }}
      main {{ padding: 10px 10px 30px; }}
      section {{ padding: 12px; }}
      table {{ min-width: 320px; font-size: 12px; }}
      .toolbar {{ grid-template-columns: 1fr; }}
      .toolbar select {{ grid-column: auto; }}
    }}
    @media (max-width: 430px) {{
      header h1 {{ font-size: 18px; }}
      .prob-grid {{ grid-template-columns: 1fr 1fr; }}
    }}
  </style>
</head>
<body>
  <div class="topbar">
    <a class="brand" href="/"><b>11</b> metric11<span class="slbl">Süper Lig 2025/26</span></a>
    <nav class="topnav">
      <a href="/">Gündem</a>
      <a href="transfer_tracker_2025_2026.html">Transferler</a>
      <a class="active" href="all_teams_preview_dashboard_2025_2026.html">{preview_nav_label()}</a>
      <a href="transfer_recommendation_report_2025_2026.html">Scout</a>
      <a href="football_intelligence_home.html">Analiz</a>
    </nav>
  </div>
  <header>
    <div>
      <h1>{escape(team_name)} maç odası</h1>
      <p>2025/26 sezonu: maç seç, olasılıkları, gol adaylarını, kadro kararını ve eksik oyuncu etkisini birlikte incele.</p>
    </div>
  </header>
  <main>
    {transfer_section}
    {off_season_banner}
    <div class="toolbar">
      <select id="matchSelect" aria-label="Maç seç">{options}</select>
      <div class="metric"><span>Üretilen rapor</span><strong>{summary.get("generated_reports", 0)}</strong></div>
      <div class="metric"><span>Büyük maç</span><strong>{summary.get("big_match_reports", 0)}</strong></div>
      <div class="metric"><span>Yüksek kart sinyali</span><strong>{summary.get("high_card_signal_reports", 0)}</strong></div>
      <div class="metric"><span>Gol adayı ilk 5</span><strong>%{round(goal_backtest.get("top_5_hit_rate", 0) * 100)}</strong></div>
    </div>
    <div class="grid">
      <div>
        <section>
          <div class="fixture">
            <strong id="fixtureTitle"></strong>
            <span id="fixtureMeta"></span>
          </div>
          <div class="prob-grid">
            <div class="prob"><label>{escape(team_name)} kazanır</label><b id="pWin"></b><div class="bar"><i id="pWinBar"></i></div></div>
            <div class="prob"><label>Beraberlik</label><b id="pDraw"></b><div class="bar"><i id="pDrawBar"></i></div></div>
            <div class="prob"><label>Rakip kazanır</label><b id="pLose"></b><div class="bar"><i id="pLoseBar"></i></div></div>
          </div>
        </section>
        <section>
          <h2>Olası 11 Sinyali</h2>
          <table>
            <thead><tr><th>Oyuncu</th><th>Son pencere ilk 11</th><th>Yedek</th></tr></thead>
            <tbody id="starters"></tbody>
          </table>
        </section>
        <section>
          <h2>Anlatılı Analiz</h2>
          <div class="narrative" id="narrative"></div>
        </section>
        <section>
          <h2>Model Kontrolü</h2>
          <table>
            <thead><tr><th>Tahmin</th><th>Gerçek</th><th>Durum</th><th>Not</th></tr></thead>
            <tbody id="modelAudit"></tbody>
          </table>
        </section>
      </div>
      <div>
        <section>
          <h2>Maç Sinyalleri</h2>
          <p><span class="muted">Hakem:</span> <strong id="referee"></strong></p>
          <p><span class="muted">Gol beklentisi:</span> <strong id="xg"></strong></p>
          <p><span class="muted">En olası skor:</span> <strong id="scoreline"></strong></p>
          <p><span class="muted">Ekran tahmini:</span> <strong id="displayPrediction"></strong></p>
          <p><span class="muted">Model aksiyonu:</span> <strong id="modelAction"></strong></p>
          <p><span class="muted">Korumalı tahmin:</span> <strong id="protectedPrediction"></strong></p>
          <p><span class="muted">Rakip savunma:</span> <strong id="opponentDefense"></strong></p>
          <p><span class="muted">Eksik oyuncu:</span> <strong id="availabilitySummary"></strong></p>
          <p><span class="muted">Beraberlik riski:</span> <strong id="drawRisk"></strong></p>
          <p><span class="muted">Büyük maç profili:</span> <strong id="bigMatchProfile"></strong></p>
          <p><span class="muted">Kart sinyali:</span> <span id="cardSignal" class="pill"></span></p>
          <p><span class="muted">{escape(team_name)} kart beklentisi:</span> <strong id="cardExpectation"></strong></p>
          <p><span class="muted">Güven:</span> <strong id="confidence"></strong></p>
        </section>
        <section>
          <h2>Eksik / Uygunluk Sinyali</h2>
          <table>
            <thead><tr><th>Oyuncu</th><th>Durum</th><th>Kaynak</th></tr></thead>
            <tbody id="availabilityRows"></tbody>
          </table>
        </section>
        <section>
          <h2>Kadro Tercih Önerisi</h2>
          <p><span class="muted">Plan:</span> <strong id="lineupPlan"></strong></p>
          <table>
            <thead><tr><th>Öncelik</th><th>Oyuncular / Not</th></tr></thead>
            <tbody id="lineupRecommendation"></tbody>
          </table>
        </section>
        <section>
          <h2>Takım Gücü Katmanı</h2>
          <table>
            <thead><tr><th>Başlık</th><th>{escape(team_name)}</th><th>Rakip</th></tr></thead>
            <tbody id="teamStrength"></tbody>
          </table>
        </section>
        <section>
          <h2>Teknik Direktör Kadro Denetimi</h2>
          <p><span class="muted">Karar:</span> <strong id="coachVerdict"></strong></p>
          <table>
            <thead><tr><th>Başlık</th><th>Değer</th></tr></thead>
            <tbody id="coachAudit"></tbody>
          </table>
        </section>
        <section>
          <h2>Skor Senaryoları</h2>
          <table>
            <thead><tr><th>Skor</th><th>Olasılık</th></tr></thead>
            <tbody id="scorelines"></tbody>
          </table>
        </section>
        <section>
          <h2>Transfer Etki Simülasyonu</h2>
          <table>
            <thead><tr><th>Oyuncu</th><th>Rol</th><th>Gol Etkisi</th><th>Yeni Skor</th><th>Takım %</th></tr></thead>
            <tbody id="transferImpact"></tbody>
          </table>
        </section>
        <section>
          <h2>Kart Riski</h2>
          <table>
            <thead><tr><th>Oyuncu</th><th>Kart/İlk 11</th><th>Büyük maç kart</th></tr></thead>
            <tbody id="cardRisks"></tbody>
          </table>
        </section>
        <section>
          <h2>Gol Adayları</h2>
          <table>
            <thead><tr><th>Oyuncu</th><th>Tip</th><th>Skor</th><th>Geçmiş gol</th></tr></thead>
            <tbody id="goalCandidates"></tbody>
          </table>
        </section>
        <section>
          <h2>Form Penceresi</h2>
          <table>
            <thead><tr><th>Rakip</th><th>Skor</th><th>Kart</th></tr></thead>
            <tbody id="formRows"></tbody>
          </table>
        </section>
      </div>
    </div>
  </main>
  <script id="payload" type="application/json">{data_json}</script>
  <script>
    const payload = JSON.parse(document.getElementById('payload').textContent);
    const select = document.getElementById('matchSelect');
    const pct = value => `%${{Math.round(value * 100)}}`;
    const setBar = (id, value) => document.getElementById(id).style.setProperty('--w', `${{Math.round(value * 100)}}%`);
    const esc = value => String(value ?? '').replace(/[&<>"']/g, ch => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;', "'": '&#39;'}}[ch]));
    const labels = {{ target: {json.dumps(team_name)}, draw: 'Beraberlik', opponent: 'Rakip' }};
    const actionLabels = {{
      PROTECT_SIDE_PICK_SHOW_DRAW_SCENARIO: 'Korumalı taraf tahmini',
      KEEP_PICK_WITH_DRAW_WARNING: 'Beraberlik uyarılı tahmin',
      KEEP_MAIN_PICK: 'Ana tahmini koru',
      taraf_eğilimi: 'Taraf eğilimi',
      senaryo_anlat: 'Senaryo anlat',
      beraberlik_korumalı_senaryo: 'Beraberlik korumalı senaryo',
    }};
    const actionLabel = value => actionLabels[value] || value || 'Senaryo anlat';
    const signalLabels = {{ HIGH: 'Yüksek', MEDIUM: 'Orta', LOW: 'Düşük', NONE: 'Yok' }};
    const signalLabel = value => signalLabels[value] || value || '-';
    const candidateLabels = {{
      primary: 'Ana gol adayı',
      impact_sub: 'Oyuna sonradan etki',
      set_piece_defender: 'Duran top tehdidi',
      penalty_profile: 'Penaltı profili',
      big_match_scorer: 'Büyük maç golcüsü',
    }};
    const candidateLabel = value => String(value || 'primary').split('+').map(item => candidateLabels[item] || item).join(' + ');

    function predictedResult(prob) {{
      const entries = [
        ['target', prob.target_win_probability],
        ['draw', prob.draw_probability],
        ['opponent', prob.opponent_win_probability],
      ];
      entries.sort((a, b) => b[1] - a[1]);
      return entries[0][0];
    }}

    function actualResult(match) {{
      const parts = String(match.actual_score || '').split('-').map(value => Number(value.trim()));
      if (parts.length !== 2 || parts.some(Number.isNaN)) return 'unknown';
      const [homeGoals, awayGoals] = parts;
      if (homeGoals === awayGoals) return 'draw';
      const targetWon = match.home_away === 'home' ? homeGoals > awayGoals : awayGoals > homeGoals;
      return targetWon ? 'target' : 'opponent';
    }}

    function auditNote(prob) {{
      const xgGap = Math.abs(prob.expected_goals_for - prob.expected_goals_against);
      const notes = [];
      if (xgGap < 0.35) notes.push('gol beklentisi farkı dar');
      if (prob.draw_probability >= 0.27) notes.push('beraberlik canlı');
      if (prob.confidence === 'LOW') notes.push('düşük güven');
      return notes.length ? notes.join(', ') : 'net sinyal';
    }}

    function render(index) {{
      const preview = payload.previews[index];
      const match = preview.match;
      const prob = preview.probabilities;
      document.getElementById('fixtureTitle').textContent = `${{match.home_team}} - ${{match.away_team}}`;
      document.getElementById('fixtureMeta').textContent = `${{match.date}} | Gerçek skor: ${{match.actual_score}} | Maç ID: ${{match.match_id}}`;
      document.getElementById('pWin').textContent = pct(prob.target_win_probability);
      document.getElementById('pDraw').textContent = pct(prob.draw_probability);
      document.getElementById('pLose').textContent = pct(prob.opponent_win_probability);
      setBar('pWinBar', prob.target_win_probability);
      setBar('pDrawBar', prob.draw_probability);
      setBar('pLoseBar', prob.opponent_win_probability);
      document.getElementById('referee').textContent = match.main_referee || 'Yok';
      document.getElementById('xg').textContent = `${{prob.expected_goals_for}} - ${{prob.expected_goals_against}}`;
      document.getElementById('scoreline').textContent = prob.recommended_scoreline?.score
        ? `${{prob.recommended_scoreline.score}} (%${{Math.round((prob.recommended_scoreline.probability || 0) * 100)}})`
        : 'Yok';
      const displayPrediction = prob.display_prediction || {{}};
      document.getElementById('displayPrediction').textContent = displayPrediction.label
        ? `${{displayPrediction.label}}${{displayPrediction.adjustment === 'high_draw_risk_override' ? ' (beraberlik kalibrasyonu)' : ''}}`
        : labels[predictedResult(prob)];
      document.getElementById('modelAction').textContent = actionLabel(prob.recommended_call?.action);
      const drawRisk = prob.draw_risk || {{}};
      document.getElementById('protectedPrediction').textContent = drawRisk.protected_prediction
        ? `${{actionLabel(drawRisk.recommended_model_action)}} | ${{signalLabel(drawRisk.risk_level)}} / ${{drawRisk.score}}`
        : `${{actionLabel(drawRisk.recommended_model_action || 'KEEP_MAIN_PICK')}} | ${{signalLabel(drawRisk.risk_level || 'LOW')}}`;
      const defense = preview.opponent_defense || {{}};
      document.getElementById('opponentDefense').textContent = defense.available
        ? `Maç başına ${{defense.goals_against_per_match}} gol yedi | golcü etkisi ${{defense.goal_candidate_multiplier}}`
        : 'Yetersiz veri';
      const availability = preview.availability_signal || {{ unavailable: [] }};
      document.getElementById('availabilitySummary').textContent = availability.unavailable.length
        ? `${{availability.unavailable.length}} sinyal`
        : 'Sinyal yok';
      const drawCalibration = prob.draw_calibration || {{}};
      document.getElementById('drawRisk').textContent = drawCalibration.risk_level
        ? `${{signalLabel(drawCalibration.risk_level)}}${{drawCalibration.reasons?.length ? ' | ' + drawCalibration.reasons.join(', ') : ''}}${{drawRisk.reasons?.length ? ' | aksiyon: ' + drawRisk.reasons.slice(0, 3).join(', ') : ''}}`
        : 'Yok';
      const bigMatchProfile = prob.big_match_profile || {{}};
      document.getElementById('bigMatchProfile').textContent = bigMatchProfile.available
        ? `${{signalLabel(bigMatchProfile.risk_level)}} / ${{bigMatchProfile.volatility_score}} | ${{bigMatchProfile.adjustment}}`
        : 'Normal maç';
      document.getElementById('availabilityRows').innerHTML = availability.unavailable.length
        ? availability.unavailable.map(item =>
          `<tr><td>${{esc(item.player_name)}}</td><td>${{esc(item.status)}} / ${{esc(item.reason)}}</td><td>${{esc(item.source)}} (${{esc(signalLabel(item.confidence))}})</td></tr>`
        ).join('')
        : '<tr><td colspan="3" class="muted">Bu maç için kayıtlı eksik oyuncu sinyali yok.</td></tr>';
      const cardSignal = document.getElementById('cardSignal');
      cardSignal.textContent = signalLabel(prob.card_signal);
      cardSignal.className = `pill ${{String(prob.card_signal || 'low').toLowerCase()}}`;
      document.getElementById('cardExpectation').textContent = prob.team_card_expectation;
      document.getElementById('confidence').textContent = signalLabel(prob.confidence);
      document.getElementById('starters').innerHTML = preview.player_signals.likely_starters.slice(0, 11).map(player =>
        `<tr><td>${{esc(player.name)}}</td><td>${{player.recent_starts}}</td><td>${{player.recent_bench}}</td></tr>`
      ).join('');
      const lineup = preview.lineup_recommendation || {{}};
      document.getElementById('lineupPlan').textContent = lineup.plan || 'Yok';
      const caution = (lineup.card_caution || []).map(item => `${{item.name}} (${{item.cards_per_recent_start}})`).join(', ');
      document.getElementById('lineupRecommendation').innerHTML = [
        ['Çekirdek 11', (lineup.core_starters || []).slice(0, 11).join(', ') || 'Yok'],
        ['Hücum önceliği', (lineup.attacking_priority || []).join(', ') || 'Yok'],
        ['Disiplin uyarısı', caution || 'Belirgin sinyal yok'],
        ['Eksikten çıkarılan', (lineup.unavailable_removed || []).join(', ') || 'Yok'],
      ].map(row => `<tr><td>${{esc(row[0])}}</td><td>${{esc(row[1])}}</td></tr>`).join('');
      const teamStrength = preview.team_strength_signal || {{}};
      const opponentStrength = preview.opponent_strength_signal || {{}};
      document.getElementById('teamStrength').innerHTML = teamStrength.available && opponentStrength.available
        ? [
          ['Güç skoru', teamStrength.strength_score, opponentStrength.strength_score],
          ['Atak', teamStrength.attack_score, opponentStrength.attack_score],
          ['Savunma', teamStrength.defense_score, opponentStrength.defense_score],
          ['Son form', teamStrength.form_score, opponentStrength.form_score],
          ['Süreklilik', teamStrength.continuity_score, opponentStrength.continuity_score],
          ['Çekirdek oyuncu', teamStrength.core_player_count, opponentStrength.core_player_count],
        ].map(row => `<tr><td>${{esc(row[0])}}</td><td>${{esc(row[1])}}</td><td>${{esc(row[2])}}</td></tr>`).join('')
        : '<tr><td colspan="3" class="muted">Takım gücü katmanı için yeterli veri yok.</td></tr>';
      const coachAudit = preview.coach_lineup_audit || {{}};
      document.getElementById('coachVerdict').textContent = coachAudit.verdict || 'Yok';
      const questionable = (coachAudit.questionable_starters || []).map(item => `${{item.name}}: ${{item.reason}}`).join(' | ');
      document.getElementById('coachAudit').innerHTML = [
        ['Uyum', coachAudit.alignment_rate != null ? `%${{Math.round(coachAudit.alignment_rate * 100)}}` : 'Yok'],
        ['Gerçek 11 skoru', coachAudit.actual_lineup_score ?? 'Yok'],
        ['Model 11 skoru', coachAudit.recommended_lineup_score ?? 'Yok'],
        ['Alternatif gol beklentisi', coachAudit.alternative_xg_for != null ? `${{prob.expected_goals_for}}-${{prob.expected_goals_against}} -> ${{coachAudit.alternative_xg_for}}-${{coachAudit.alternative_xg_against}}` : 'Yok'],
        ['Modelde olup gerçek 11'de olmayan', (coachAudit.omitted_core_players || []).join(', ') || 'Yok'],
        ['Tartışmalı tercihler', questionable || 'Belirgin sinyal yok'],
      ].map(row => `<tr><td>${{esc(row[0])}}</td><td>${{esc(row[1])}}</td></tr>`).join('');
      document.getElementById('scorelines').innerHTML = (prob.top_scorelines || []).slice(0, 6).map(item =>
        `<tr><td>${{esc(item.score)}}</td><td>%${{Math.round((item.probability || 0) * 100)}}</td></tr>`
      ).join('');
      const transferImpact = preview.transfer_impact_simulations || {{ candidates: [] }};
      document.getElementById('transferImpact').innerHTML = transferImpact.candidates.length
        ? transferImpact.candidates.slice(0, 6).map(item =>
          `<tr><td>${{esc(item.player_name)}}<br><span class="muted">${{esc(item.current_team)}} / ${{esc(item.impact_label)}}</span></td>` +
          `<td>${{esc(item.target_role)}}<br><span class="muted">fit ${{item.role_fit_score}} / ${{esc(item.position_confidence)}}</span></td>` +
          `<td>${{item.current_expected_goals_for}}-${{item.current_expected_goals_against}} -> ${{item.simulated_expected_goals_for}}-${{item.simulated_expected_goals_against}}</td>` +
          `<td>${{esc(item.simulated_scoreline?.score || '-')}}</td><td>%${{Math.round((item.simulated_target_win_probability || 0) * 100)}}</td></tr>`
        ).join('')
        : '<tr><td colspan="5" class="muted">Bu maç için transfer etki simülasyonu yok.</td></tr>';
      document.getElementById('cardRisks').innerHTML = preview.player_signals.card_risk_players.slice(0, 8).map(player =>
        `<tr><td>${{esc(player.name)}}</td><td>${{player.cards_per_recent_start}}</td><td>${{player.big_match_cards}}</td></tr>`
      ).join('');
      document.getElementById('goalCandidates').innerHTML = preview.goal_candidates.candidates.slice(0, 10).map(player => {{
        const hit = player.actual_scorer ? ' <span class="pill low">gol</span>' : '';
        return `<tr><td>${{esc(player.name)}}${{hit}}</td><td>${{esc(candidateLabel(player.candidate_type))}}</td><td>${{player.goal_threat_score}}</td><td>${{player.season_goals_before_match}}</td></tr>`;
      }}).join('');
      document.getElementById('formRows').innerHTML = preview.team_form.results.map(row =>
        `<tr><td>${{esc(row.opponent)}}</td><td>${{esc(row.score)}}</td><td>${{row.cards}}</td></tr>`
      ).join('');
      document.getElementById('narrative').innerHTML = preview.narrative.map(text => `<p>${{esc(text)}}</p>`).join('');
      const displayMap = {{ target_win: 'target', draw: 'draw', opponent_win: 'opponent' }};
      const predicted = displayMap[prob.display_prediction?.final_result] || predictedResult(prob);
      const actual = actualResult(match);
      const correct = predicted === actual;
      document.getElementById('modelAudit').innerHTML =
        `<tr><td>${{labels[predicted]}}</td><td>${{labels[actual] || 'Bilinmiyor'}}</td><td>${{correct ? '<span class="pill low">doğru</span>' : '<span class="pill high">yanlış</span>'}}</td><td>${{esc(auditNote(prob))}}</td></tr>`;
    }}

    select.addEventListener('change', event => render(Number(event.target.value)));
    render(0);
  </script>
  <script defer src="/_vercel/insights/script.js"></script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
