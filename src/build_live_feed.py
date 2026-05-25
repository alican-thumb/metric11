"""Futbolsever odaklı canlı gündem sayfası.

Son transfer haberleri, Twitter sinyalleri, resmi transferler ve
yaz penceresi özetini tek ekranda toplar. Analiz araçlarından önce gelir.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path

from src.config import PROCESSED_DIR, SEASON, SEASON_LABEL

OUTPUT_HTML = PROCESSED_DIR / f"gundem_{SEASON}.html"

WINDOW_DATE = datetime(2026, 6, 1, tzinfo=timezone.utc)

SOURCE_COLORS = {
    "official_club": ("#16a34a", "#dcfce7", "Resmi Kulüp"),
    "rss":           ("#2563eb", "#dbeafe", "Basın"),
    "twitter":       ("#7c3aed", "#ede9fe", "Twitter"),
    "official":      ("#16a34a", "#dcfce7", "Resmi"),
}

TRANSFER_STATUS = {
    "OFFICIAL":        ("#16a34a", "#dcfce7", "RESMİ"),
    "CORROBORATED":    ("#2563eb", "#dbeafe", "DOĞRULANDI"),
    "TM_CONFIRMED":    ("#7c3aed", "#ede9fe", "TM ONAYDI"),
    "RUMOR":           ("#d97706", "#fef3c7", "SÖYLENTI"),
    "REVIEW_REQUIRED": ("#6b7280", "#f1f5f9", "İNCELEMEDE"),
}


def _load(path: Path) -> dict | list:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def _days_to_window() -> int:
    now = datetime.now(timezone.utc)
    delta = (WINDOW_DATE - now).days
    return max(delta, 0)


def _source_badge(source_type: str) -> str:
    color, bg, label = SOURCE_COLORS.get(source_type, ("#6b7280", "#f1f5f9", source_type))
    return f"<span style='font-size:10px;padding:1px 6px;border-radius:3px;font-weight:700;color:{color};background:{bg}'>{escape(label)}</span>"


def _transfer_badge(status: str) -> str:
    color, bg, label = TRANSFER_STATUS.get(status, ("#6b7280", "#f1f5f9", status))
    return f"<span style='font-size:10px;padding:1px 6px;border-radius:3px;font-weight:700;color:{color};background:{bg}'>{escape(label)}</span>"


def _article_html(a: dict) -> str:
    title = escape(a.get("title", "")[:120])
    link  = escape(a.get("link", "") or "")
    src   = a.get("source", "")
    stype = a.get("source_type", "rss")
    cat   = a.get("category", "")
    tag   = ""
    if cat == "transfer":
        tag = "<span style='font-size:10px;color:#d97706;font-weight:700'>⟳ TRANSFER</span> "
    elif cat == "injury":
        tag = "<span style='font-size:10px;color:#dc2626;font-weight:700'>⚕ SAKAT</span> "
    elif cat == "suspension":
        tag = "<span style='font-size:10px;color:#9333ea;font-weight:700'>🟥 CEZA</span> "

    anchor = f'<a href="{link}" target="_blank" style="color:var(--ink);text-decoration:none;line-height:1.4">{tag}{title}</a>' if link else f"{tag}{title}"
    return f"""<div style="padding:12px 0;border-bottom:1px solid var(--line);display:flex;gap:12px;align-items:flex-start">
  <div style="flex:1;min-width:0">{anchor}<div style="margin-top:4px;display:flex;gap:6px;align-items:center">{_source_badge(stype)}<span style="font-size:11px;color:var(--muted)">{escape(src)}</span></div></div>
</div>"""


def _transfer_html(t: dict) -> str:
    player = escape(t.get("player", "?"))
    frm    = escape(t.get("from_club") or "—")
    to     = escape(t.get("to_club") or "—")
    mv     = escape(t.get("market_value_text", "—"))
    status = t.get("status", "REVIEW_REQUIRED")
    link   = t.get("link", "")
    badge  = _transfer_badge(status)
    inner  = f'<a href="{escape(link)}" target="_blank" style="color:var(--ink);text-decoration:none"><strong>{player}</strong></a>' if link else f"<strong>{player}</strong>"
    return f"""<div style="padding:11px 0;border-bottom:1px solid var(--line)">
  <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">{inner}{badge}</div>
  <div style="margin-top:3px;font-size:12px;color:var(--muted)">{frm} → {to} <span style="margin-left:8px;font-weight:600;color:var(--ink)">{mv}</span></div>
</div>"""


def _pill(val: str, label: str, color: str = "var(--green)") -> str:
    return f"""<div style="background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:12px 16px;text-align:center;flex:1;min-width:100px">
  <div style="font-size:20px;font-weight:700;color:{color}">{escape(val)}</div>
  <div style="font-size:11px;color:var(--muted);margin-top:2px">{escape(label)}</div>
</div>"""


def build_html() -> str:
    intel    = _load(PROCESSED_DIR / f"news_intelligence_{SEASON}.json")
    tracker  = _load(PROCESSED_DIR / f"transfer_tracker_{SEASON}.json")
    ctx      = _load(PROCESSED_DIR / f"transfer_season_context_{SEASON}.json")

    articles = (intel.get("recent_articles") or [])[:12]
    transfers_all = tracker.get("transfers", [])
    transfers_show = [t for t in transfers_all if t.get("status") in ("OFFICIAL", "CORROBORATED", "TM_CONFIRMED")][:8]
    if len(transfers_show) < 4:
        transfers_show = transfers_all[:8]

    ctx_summary = ctx.get("summary", {}) if isinstance(ctx, dict) else {}
    free_agents = ctx_summary.get("free_agents_count", 0)
    final_year  = ctx_summary.get("final_year_count", 0)
    signals_count = ctx_summary.get("transfer_signals_count", 0)
    tracker_summary = tracker.get("summary", {}) if isinstance(tracker, dict) else {}
    official_count = tracker_summary.get("official_count", 0)

    days_left = _days_to_window()
    window_msg = (
        f"Transfer penceresi <strong>{days_left} gün sonra</strong> açılıyor (1 Haziran 2026)"
        if days_left > 0 else
        "<strong>Transfer penceresi açık</strong> — 1 Haz – 31 Ağu 2026"
    )

    now_str = datetime.now(timezone.utc).strftime("%d.%m.%Y %H:%M UTC")
    articles_html = "".join(_article_html(a) for a in articles) or "<p style='color:var(--muted);padding:16px 0'>Henüz makale yok.</p>"
    transfers_html = "".join(_transfer_html(t) for t in transfers_show) or "<p style='color:var(--muted);padding:16px 0'>Henüz transfer kaydı yok.</p>"

    return f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Gündem — Süper Lig {SEASON_LABEL}</title>
<style>
  :root{{--bg:#f3f5f4;--panel:#fff;--ink:#132018;--muted:#627067;--line:#d7ded9;--dark:#091810;--green:#116447;--lime:#cde94e}}
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:Inter,'Segoe UI',Arial,sans-serif;background:var(--bg);color:var(--ink)}}
  .topbar{{min-height:62px;padding:0 clamp(14px,3vw,32px);display:flex;align-items:center;justify-content:space-between;gap:18px;background:var(--dark)}}
  .brand{{display:flex;align-items:center;gap:10px;color:white;text-decoration:none;font-size:18px;font-weight:800}}
  .brand b{{width:29px;height:29px;border-radius:7px;display:grid;place-items:center;color:var(--dark);background:var(--lime);font-size:14px}}
  .topnav{{display:flex;gap:4px;overflow-x:auto;scrollbar-width:none}}
  .topnav::-webkit-scrollbar{{display:none}}
  .topnav a{{white-space:nowrap;color:#d5ded8;padding:9px 10px;border-radius:6px;text-decoration:none;font-size:13px;font-weight:600}}
  .topnav a.active{{background:#162b20;color:white}}
  .window-banner{{background:linear-gradient(90deg,#1e3a5f,#0f2a4a);padding:10px clamp(14px,3vw,32px);color:#bfdbfe;font-size:13px;border-bottom:1px solid #1e40af;display:flex;align-items:center;gap:10px}}
  .window-dot{{width:8px;height:8px;border-radius:50%;background:#60a5fa;flex-shrink:0;animation:pulse 2s infinite}}
  @keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.4}}}}
  .main{{max-width:1200px;margin:0 auto;padding:20px clamp(12px,3vw,32px) 50px;display:grid;grid-template-columns:1fr 360px;gap:24px}}
  .panel{{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:18px 20px}}
  .panel h2{{font-size:15px;font-weight:700;margin-bottom:2px;color:var(--ink)}}
  .panel .sub{{font-size:11px;color:var(--muted);margin-bottom:12px}}
  .pills{{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:24px}}
  .see-more{{display:block;text-align:center;padding:10px;font-size:12px;color:var(--green);font-weight:600;text-decoration:none;border-top:1px solid var(--line);margin-top:8px}}
  .see-more:hover{{text-decoration:underline}}
  @media(max-width:860px){{.main{{grid-template-columns:1fr}}}}
  @media(max-width:600px){{.topbar{{flex-direction:column;align-items:stretch;padding:11px 12px 0;gap:0;min-height:unset}}.brand{{padding-bottom:8px}}.topnav{{border-top:1px solid #1e3228;padding:7px 0 9px}}}}
</style>
</head>
<body>
<div class="topbar">
  <a class="brand" href="gundem_{SEASON}.html"><b>11</b> metric11</a>
  <nav class="topnav">
    <a class="active" href="gundem_{SEASON}.html">Gündem</a>
    <a href="transfer_tracker_{SEASON}.html">Transferler</a>
    <a href="all_teams_preview_dashboard_{SEASON}.html">Maç Önü</a>
    <a href="transfer_recommendation_report_{SEASON}.html">Scout</a>
    <a href="football_intelligence_home.html">Analiz</a>
  </nav>
</div>
<div class="window-banner">
  <div class="window-dot"></div>
  <span>{window_msg} · Güncelleme: {now_str}</span>
</div>
<div class="main">
  <div>
    <div class="pills">
      {_pill(str(official_count), "Resmi Transfer", "#16a34a")}
      {_pill(str(signals_count), "Transfer Sinyali", "#d97706")}
      {_pill(str(free_agents), "Serbest Kalacak", "#2563eb")}
      {_pill(str(final_year), "Son Yıl Kontrat", "#7c3aed")}
    </div>
    <div class="panel">
      <h2>Son Haberler</h2>
      <div class="sub">{len(articles)} makale · RSS + Kulüp Siteleri + Twitter</div>
      {articles_html}
      <a class="see-more" href="news_intelligence_dashboard_{SEASON}.html">Tüm haberleri gör →</a>
    </div>
  </div>
  <div style="display:flex;flex-direction:column;gap:16px">
    <div class="panel">
      <h2>Transferler</h2>
      <div class="sub">Resmi · Doğrulanmış · TM Onaylı</div>
      {transfers_html}
      <a class="see-more" href="transfer_tracker_{SEASON}.html">Transfer takibine git →</a>
    </div>
    <div class="panel" style="font-size:13px">
      <h2 style="margin-bottom:12px">Araçlar</h2>
      <div style="display:flex;flex-direction:column;gap:7px">
        <a href="transfer_season_context_{SEASON}.html" style="color:var(--green);text-decoration:none">→ Serbest kalacak oyuncular</a>
        <a href="transfer_recommendation_report_{SEASON}.html" style="color:var(--green);text-decoration:none">→ Takım transfer önerileri</a>
        <a href="all_teams_preview_dashboard_{SEASON}.html" style="color:var(--green);text-decoration:none">→ Maç önü arşivi (2025/26)</a>
        <a href="football_command_center_{SEASON}.html" style="color:var(--green);text-decoration:none">→ Komuta merkezi</a>
        <a href="football_intelligence_home.html" style="color:var(--green);text-decoration:none">→ Tüm araçlar</a>
      </div>
    </div>
  </div>
</div>
<script defer src="/_vercel/insights/script.js"></script>
</body>
</html>"""


def main() -> None:
    html = build_html()
    OUTPUT_HTML.write_text(html, encoding="utf-8")
    # index.html'i gündem sayfasına yönlendir
    redirect = PROCESSED_DIR / "index.html"
    redirect.write_text(f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<meta http-equiv="refresh" content="0;url=gundem_{SEASON}.html">
<title>metric11</title></head>
<body><a href="gundem_{SEASON}.html">Yükleniyor…</a></body></html>""", encoding="utf-8")
    print(OUTPUT_HTML)


if __name__ == "__main__":
    main()
