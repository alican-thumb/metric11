"""Futbolsever odaklı canlı gündem sayfası.

Son transfer haberleri, Twitter sinyalleri, resmi transferler ve
yaz penceresi özetini tek ekranda toplar. Analiz araçlarından önce gelir.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path

from src.config import PROCESSED_DIR, SEASON, TRANSFER_WATCH_SEASON_LABEL

OUTPUT_HTML = PROCESSED_DIR / f"gundem_{SEASON}.html"

WINDOW_OPEN_DATE  = datetime(2026, 6, 1, tzinfo=timezone.utc)
WINDOW_CLOSE_DATE = datetime(2026, 9, 1, tzinfo=timezone.utc)

SOURCE_COLORS = {
    "official_club": ("#16a34a", "#dcfce7", "Resmi Kulüp"),
    "rss":           ("#2563eb", "#dbeafe", "Basın"),
    "google_news":   ("#2563eb", "#dbeafe", "Google News"),
    "twitter":       ("#7c3aed", "#ede9fe", "Twitter"),
    "telegram":      ("#0e7490", "#cffafe", "Telegram"),
    "official":      ("#16a34a", "#dcfce7", "Resmi"),
}

# 1-10 güven skoru: 10=resmi kulüp, 7=ana medya RSS, 5=sosyal medya, 3=bilinmeyen
SOURCE_TRUST: dict[str, int] = {
    "official_club": 10,
    "official":      10,
    "rss":           7,
    "google_news":   6,
    "twitter":       5,
    "telegram":      4,
}

TRANSFER_STATUS = {
    "OFFICIAL":        ("#16a34a", "#dcfce7", "RESMİ"),
    "CORROBORATED":    ("#2563eb", "#dbeafe", "DOĞRULANDI"),
    "TM_CONFIRMED":    ("#7c3aed", "#ede9fe", "TM KADRO"),
    "RUMOR":           ("#d97706", "#fef3c7", "SÖYLENTI"),
    "REVIEW_REQUIRED": ("#6b7280", "#f1f5f9", "İNCELEMEDE"),
}


def _load(path: Path) -> dict | list:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def _window_state() -> tuple[str, str, str, str]:
    """Returns (state, banner_css, dot_css, message) for transfer window."""
    now = datetime.now(timezone.utc)
    if now >= WINDOW_CLOSE_DATE:
        return (
            "closed",
            "background:linear-gradient(90deg,#374151,#1f2937);border-bottom:1px solid #4b5563",
            "background:#9ca3af",
            f"<strong>Transfer penceresi kapandı</strong> — {TRANSFER_WATCH_SEASON_LABEL} sezonu transferleri tamamlandı",
        )
    if now >= WINDOW_OPEN_DATE:
        days_left = (WINDOW_CLOSE_DATE - now).days
        return (
            "open",
            "background:linear-gradient(90deg,#14532d,#166534);border-bottom:1px solid #16a34a",
            "background:#4ade80",
            f"<strong>Transfer penceresi açık</strong> — {days_left} gün kaldı (1 Haz – 31 Ağu 2026)",
        )
    days_left = (WINDOW_OPEN_DATE - now).days
    return (
        "countdown",
        "background:linear-gradient(90deg,#1e3a5f,#0f2a4a);border-bottom:1px solid #1e40af",
        "background:#60a5fa",
        f"Transfer penceresi <strong>{days_left} gün sonra</strong> açılıyor (1 Haziran 2026)",
    )


def _source_badge(source_type: str) -> str:
    color, bg, label = SOURCE_COLORS.get(source_type, ("#6b7280", "#f1f5f9", source_type))
    return f"<span style='font-size:10px;padding:1px 6px;border-radius:3px;font-weight:700;color:{color};background:{bg}'>{escape(label)}</span>"


def _transfer_badge(status: str) -> str:
    color, bg, label = TRANSFER_STATUS.get(status, ("#6b7280", "#f1f5f9", status))
    return f"<span style='font-size:10px;padding:1px 6px;border-radius:3px;font-weight:700;color:{color};background:{bg}'>{escape(label)}</span>"


def _fmt_date(published_at: str | None) -> str:
    if not published_at:
        return ""
    try:
        raw = published_at.strip()
        # Format: "21.5.2026" veya "21.5.2026 14:30"
        if raw and raw[0].isdigit() and "." in raw[:6] and not raw.startswith("202"):
            parts = raw.split(" ")[0].split(".")
            d, m, y = int(parts[0]), int(parts[1]), int(parts[2])
            dt = datetime(y, m, d, tzinfo=timezone.utc)
        # Format: RFC 2822 "Sat, 24 May 2026 ..."
        elif "," in raw[:4]:
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(raw)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
        # Format: ISO 8601 "2026-05-24T14:30:00Z" veya "2026-05-24"
        else:
            dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
        diff = datetime.now(timezone.utc) - dt
        if diff.days < 0:
            return ""
        if diff.days == 0:
            h = diff.seconds // 3600
            return f"{h}sa" if h else "az önce"
        if diff.days == 1:
            return "dün"
        return f"{diff.days}g önce"
    except Exception:
        return ""


def _article_html(a: dict, source_count: int = 1, player_name: str | None = None) -> str:
    title = escape(a.get("title", "")[:120])
    link  = escape(a.get("link", "") or "")
    src   = a.get("source", "")
    stype = a.get("source_type", "rss")
    cats  = a.get("categories") or ([a.get("category")] if a.get("category") else [])
    age   = _fmt_date(a.get("published_at"))
    trust = SOURCE_TRUST.get(stype, 5)

    tag = ""
    if "transfer" in cats:
        tag = "<span style='font-size:10px;color:#d97706;font-weight:700'>⟳ TRANSFER</span> "
    elif "injury" in cats:
        tag = "<span style='font-size:10px;color:#dc2626;font-weight:700'>⚕ SAKAT</span> "
    elif "suspension" in cats:
        tag = "<span style='font-size:10px;color:#9333ea;font-weight:700'>🟥 CEZA</span> "

    title_color = "var(--ink)" if trust >= 6 else "#627067"
    age_html = f"<span style='font-size:11px;color:var(--muted);margin-left:auto'>{escape(age)}</span>" if age else ""
    anchor = f'<a href="{link}" target="_blank" style="color:{title_color};text-decoration:none;line-height:1.4">{tag}{title}</a>' if link else f"<span style='color:{title_color}'>{tag}{title}</span>"
    multi_html = f"<span style='font-size:10px;color:#7c3aed;font-weight:600;margin-left:4px'>{source_count} kaynak</span>" if source_count > 1 else ""
    player_html = f"<span style='font-size:10px;padding:1px 6px;border-radius:3px;background:#fef3c7;color:#92400e;font-weight:600;margin-left:4px'>👤 {escape(player_name)}</span>" if player_name else ""
    return f"""<div style="padding:12px 0;border-bottom:1px solid var(--line)">
  {anchor}{multi_html}{player_html}<div style="margin-top:4px;display:flex;gap:6px;align-items:center">{_source_badge(stype)}<span style="font-size:11px;color:var(--muted)">{escape(src)}</span>{age_html}</div>
</div>"""


def _transfer_html(t: dict) -> str:
    raw_player = t.get("player") or ""
    if not raw_player or raw_player == "?":
        return ""
    player = escape(raw_player)
    _frm = t.get("from_club") or ""
    _to  = t.get("to_club") or ""
    frm  = escape(_frm if _frm and _frm != "?" else "—")
    to   = escape(_to  if _to  and _to  != "?" else "—")
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


def _deduplicate_articles(articles: list[dict]) -> list[tuple[dict, int]]:
    """Başlık benzerliğine göre haberleri grupla. (en iyi haber, kaynak sayısı) döner."""
    STOP = {"ve", "ile", "de", "da", "bir", "bu", "için", "the", "a", "in", "of", "to"}
    MIN_MATCH = 3

    def keywords(title: str) -> set[str]:
        words = title.lower().split()
        return {w for w in words if len(w) > 3 and w not in STOP}

    groups: list[list[int]] = []
    used = set()

    for i, a in enumerate(articles):
        if i in used:
            continue
        kw_i = keywords(a.get("title", ""))
        group = [i]
        for j, b in enumerate(articles):
            if j <= i or j in used:
                continue
            kw_j = keywords(b.get("title", ""))
            if len(kw_i & kw_j) >= MIN_MATCH:
                group.append(j)
                used.add(j)
        used.add(i)
        groups.append(group)

    result = []
    for group in groups:
        best = max(group, key=lambda idx: SOURCE_TRUST.get(articles[idx].get("source_type", ""), 5))
        result.append((articles[best], len(group)))
    return result


def _build_player_index(transfers: list[dict]) -> dict[str, str]:
    """Transfer listesinden oyuncu adı → tam ad eşlem tablosu üretir (soyad bazlı)."""
    index: dict[str, str] = {}
    for t in transfers:
        full = (t.get("player") or "").strip()
        if not full:
            continue
        parts = full.split()
        for part in parts:
            if len(part) >= 4:
                index[part.lower()] = full
        if len(parts) >= 2:
            index[parts[-1].lower()] = full  # soyad
    return index


def _detect_player(title: str, player_index: dict[str, str]) -> str | None:
    """Haber başlığında geçen ilk bilinen oyuncu adını döner (kelime sınırı kontrolü ile)."""
    import re
    title_lower = title.lower()
    title_words = set(re.findall(r"[a-züöşıçğ]{4,}", title_lower))
    for token, full_name in player_index.items():
        if token in title_words:
            return full_name
    return None


def _ana_link(href: str, label: str, bold: bool = False) -> str:
    exists = (PROCESSED_DIR / href).exists()
    if exists:
        weight = "font-weight:600;" if bold else ""
        return f'<a href="{escape(href)}" style="color:var(--green);text-decoration:none;{weight}">→ {escape(label)}</a>'
    return f'<span style="color:var(--muted);cursor:not-allowed" title="Henüz oluşturulmadı">→ {escape(label)}</span>'


def build_html() -> str:
    intel    = _load(PROCESSED_DIR / f"news_intelligence_{SEASON}.json")
    tracker  = _load(PROCESSED_DIR / f"transfer_tracker_{SEASON}.json")
    ctx      = _load(PROCESSED_DIR / f"transfer_season_context_{SEASON}.json")

    transfers_all = tracker.get("transfers", [])
    player_index = _build_player_index(transfers_all)

    raw_articles = (intel.get("recent_articles") or [])[:18]
    deduped = _deduplicate_articles(raw_articles)
    articles_with_count = [
        (a, cnt, _detect_player(a.get("title", ""), player_index))
        for a, cnt in deduped[:6]
    ]
    transfers_show = [t for t in transfers_all if t.get("status") in ("OFFICIAL", "CORROBORATED", "TM_CONFIRMED")][:8]
    if len(transfers_show) < 4:
        transfers_show = transfers_all[:8]

    ctx_summary = ctx.get("summary", {}) if isinstance(ctx, dict) else {}
    free_agents = ctx_summary.get("free_agents_count", 0)
    final_year  = ctx_summary.get("final_year_count", 0)
    signals_count = ctx_summary.get("transfer_signals_count", 0)
    tracker_summary = tracker.get("summary", {}) if isinstance(tracker, dict) else {}
    official_count = tracker_summary.get("official_count", 0)

    _state, banner_css, dot_css, window_msg = _window_state()
    _is_transfer_season = _state in ("countdown", "open")

    mv_eur = ctx_summary.get("free_agent_total_market_value_eur", 0)
    mv_str = f"€{mv_eur / 1_000_000:.0f}M" if mv_eur >= 1_000_000 else ""

    now_str = datetime.now(timezone.utc).strftime("%d.%m.%Y %H:%M UTC")
    articles_html = "".join(_article_html(a, cnt, player) for a, cnt, player in articles_with_count) or "<p style='color:var(--muted);padding:16px 0'>Henüz sinyal yok.</p>"
    transfers_html = "".join(_transfer_html(t) for t in transfers_show) or "<p style='color:var(--muted);padding:16px 0'>Henüz transfer kaydı yok.</p>"

    if _is_transfer_season:
        transfer_sidebar_html = (
            '<div class="panel" style="border-top:3px solid var(--lime);font-size:13px">'
            '<div style="font-size:10px;font-weight:700;color:var(--lime);letter-spacing:.06em;margin-bottom:10px;text-transform:uppercase">Transfer Sezonu 2026-2027</div>'
            '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:14px">'
            f'<div style="background:#0f2318;border-radius:6px;padding:10px 12px"><div style="font-size:22px;font-weight:800;color:white">{free_agents}</div><div style="color:#8fa89a;font-size:11px;margin-top:2px">Serbest Kalacak</div></div>'
            f'<div style="background:#0f2318;border-radius:6px;padding:10px 12px"><div style="font-size:22px;font-weight:800;color:white">{final_year}</div><div style="color:#8fa89a;font-size:11px;margin-top:2px">Son Yıl Kontrat</div></div>'
            f'<div style="background:#0f2318;border-radius:6px;padding:10px 12px"><div style="font-size:22px;font-weight:800;color:white">{signals_count}</div><div style="color:#8fa89a;font-size:11px;margin-top:2px">Transfer Sinyali</div></div>'
            f'<div style="background:#0f2318;border-radius:6px;padding:10px 12px"><div style="font-size:18px;font-weight:800;color:white">{mv_str}</div><div style="color:#8fa89a;font-size:11px;margin-top:2px">Serbest Piyasa Değeri</div></div>'
            '</div>'
            f'<div style="display:flex;flex-direction:column;gap:7px">{_ana_link(f"transfer_recommendation_report_{SEASON}.html", "Takım transfer önerileri →", bold=True)}{_ana_link(f"transfer_season_context_{SEASON}.html", "Serbest kalacak oyuncular →")}</div>'
            '</div>'
        )
    else:
        transfer_sidebar_html = ""

    if not _is_transfer_season:
        analysis_transfer_links_html = (
            '<div style="font-size:10px;font-weight:700;color:var(--muted);letter-spacing:.06em;margin-bottom:6px;text-transform:uppercase">Transfer &amp; Kadro</div>'
            '<div style="display:flex;flex-direction:column;gap:7px;margin-bottom:14px">'
            f'{_ana_link(f"transfer_recommendation_report_{SEASON}.html", "Takım transfer önerileri", bold=True)}'
            f'{_ana_link(f"transfer_season_context_{SEASON}.html", "Serbest kalacak oyuncular")}'
            f'{_ana_link(f"transfer_tracker_{SEASON}.html", "Transfer takip listesi")}'
            '</div>'
        )
    else:
        analysis_transfer_links_html = ""

    return f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Gündem — Süper Lig {TRANSFER_WATCH_SEASON_LABEL} | metric11</title>
<meta name="description" content="Süper Lig transfer haberleri, sakat-cezalı listesi ve güncel transfer takibi. Tüm kaynaklar tek sayfada — metric11.">
<meta property="og:title" content="Gündem — Süper Lig {TRANSFER_WATCH_SEASON_LABEL} | metric11">
<meta property="og:description" content="Süper Lig transfer haberleri, sakat-cezalı listesi ve güncel transfer takibi.">
<meta property="og:image" content="https://metric11.com/og-image.png">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:image" content="https://metric11.com/og-image.png">
<meta property="og:url" content="https://metric11.com/">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="canonical" href="https://metric11.com/">
<script type="application/ld+json">{{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "metric11",
  "url": "https://metric11.com",
  "description": "Süper Lig istatistik, transfer takibi ve futbol analiz platformu.",
  "inLanguage": "tr"
}}</script>
<style>
  :root{{--bg:#f3f5f4;--panel:#fff;--ink:#132018;--muted:#627067;--line:#d7ded9;--dark:#091810;--green:#116447;--lime:#cde94e}}
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:Inter,'Segoe UI',Arial,sans-serif;background:var(--bg);color:var(--ink)}}
  .topbar{{min-height:58px;padding:0 clamp(14px,3vw,32px);display:flex;align-items:center;justify-content:space-between;gap:18px;background:var(--dark);border-bottom:2px solid #1a3023}}
  .brand{{display:flex;align-items:center;gap:10px;color:white;text-decoration:none;font-size:18px;font-weight:800;letter-spacing:-0.2px}}
  .brand:visited,.brand:active,.brand:hover{{color:white}}
  .brand b{{width:28px;height:28px;border-radius:6px;display:grid;place-items:center;color:var(--dark);background:var(--lime);font-size:14px;font-weight:900}}
  .brand .slbl{{color:#6b7c72;font-size:11px;font-weight:500;border-left:1px solid #2a3d30;padding-left:8px;margin-left:2px}}
  .topnav{{display:flex;gap:2px;overflow-x:auto;scrollbar-width:none}}
  .topnav::-webkit-scrollbar{{display:none}}
  .topnav a{{white-space:nowrap;color:#8fa89a;padding:8px 11px;border-radius:6px;text-decoration:none;font-size:13px;font-weight:600;transition:background .15s,color .15s}}
  .topnav a:visited{{color:#8fa89a}}
  .topnav a:hover{{background:#162b20;color:white}}
  .topnav a.active{{background:#162b20;color:white}}
  .window-banner{{padding:10px clamp(14px,3vw,32px);color:#d1fae5;font-size:13px;display:flex;align-items:center;gap:10px}}
  .window-dot{{width:8px;height:8px;border-radius:50%;flex-shrink:0;animation:pulse 2s infinite}}
  @keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.4}}}}
  .main{{max-width:1200px;margin:0 auto;padding:20px clamp(12px,3vw,32px) 50px;display:grid;grid-template-columns:1fr 360px;gap:24px}}
  .panel{{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:18px 20px}}
  .panel h2{{font-size:15px;font-weight:700;margin-bottom:2px;color:var(--ink)}}
  .panel .sub{{font-size:11px;color:var(--muted);margin-bottom:12px}}
  .pills{{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:24px}}
  .see-more{{display:block;text-align:center;padding:10px;font-size:12px;color:var(--green);font-weight:600;text-decoration:none;border-top:1px solid var(--line);margin-top:8px}}
  .see-more:hover{{text-decoration:underline}}
  @media(max-width:860px){{.main{{grid-template-columns:1fr}}}}
  @media(max-width:600px){{
    .topbar{{flex-direction:column;align-items:stretch;padding:11px 12px 0;gap:0;min-height:unset}}
    .brand{{padding-bottom:8px}}
    .topnav{{border-top:1px solid #1e3228;padding:7px 0 9px}}
    .pills{{display:grid;grid-template-columns:1fr 1fr;gap:8px}}
    .panel{{padding:14px 14px}}
    .main{{padding:12px 10px 40px}}
  }}
</style>
</head>
<body>
<div class="topbar">
  <a class="brand" href="/"><b>11</b> metric11<span class="slbl">Süper Lig {TRANSFER_WATCH_SEASON_LABEL}</span></a>
  <nav class="topnav">
    <a class="active" href="/">Gündem</a>
    <a href="transfer_tracker_{SEASON}.html">Transferler</a>
    <a href="all_teams_preview_dashboard_{SEASON}.html">{"Arşiv" if _is_transfer_season else "Maç Önü"}</a>
    <a href="transfer_recommendation_report_{SEASON}.html">Scout</a>
    <a href="football_intelligence_home.html">Analiz</a>
    <a href="worldcup_2026_predictions.html">🌍 WC 2026</a>
    <a href="european_predictions_2026_2027.html">⚽ Avrupa</a>
  </nav>
</div>
<div class="window-banner" style="{banner_css}">
  <div class="window-dot" style="{dot_css}"></div>
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
      <h2>Transferler</h2>
      <div class="sub">Resmi · Doğrulanmış · TM Onaylı</div>
      {transfers_html}
      <a class="see-more" href="transfer_tracker_{SEASON}.html">Tüm transfer takibine git →</a>
    </div>
    <div class="panel" style="margin-top:16px">
      <h2>Haber Sinyalleri</h2>
      <div class="sub">Son 14 gün · Basın + Resmi Kulüp + Google News</div>
      {articles_html}
      <a class="see-more" href="news_intelligence_dashboard_{SEASON}.html">Detaylı haber analizi →</a>
    </div>
  </div>
  <div style="display:flex;flex-direction:column;gap:16px">
    {transfer_sidebar_html}
    <div class="panel" style="font-size:13px">
      <h2 style="margin-bottom:14px">Analiz Platformu</h2>
      {analysis_transfer_links_html}
      <div style="font-size:10px;font-weight:700;color:var(--muted);letter-spacing:.06em;margin-bottom:6px;text-transform:uppercase">{"Sezon Arşivi" if _is_transfer_season else "Maç &amp; Tahmin"}</div>
      <div style="display:flex;flex-direction:column;gap:7px">
        {_ana_link(f"all_teams_preview_dashboard_{SEASON}.html", "Maç önü arşivi (18 takım)", bold=not _is_transfer_season)}
        {_ana_link(f"transfer_tracker_{SEASON}.html", "Transfer takip listesi") if _is_transfer_season else ""}
        {_ana_link("football_intelligence_home.html", "Tüm analiz araçları")}
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
    print(OUTPUT_HTML)


if __name__ == "__main__":
    main()
