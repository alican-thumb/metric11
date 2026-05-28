"""Transfer penceresi canlı takip sayfası.

news_intelligence verisindeki transfer sinyallerini takım bazlı düzenler;
resmi transferler, doğrulama bekleyenler ve söylentileri ayrı gösterir.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path

from src.config import (
    PROCESSED_DIR,
    SEASON,
    TRANSFER_WATCH_SEASON,
    TRANSFER_WATCH_SEASON_LABEL,
)
from src.html_utils import preview_nav_label

OUTPUT_HTML = PROCESSED_DIR / f"transfer_tracker_{SEASON}.html"
OUTPUT_JSON = PROCESSED_DIR / f"transfer_tracker_{SEASON}.json"

STATUS_META: dict[str, tuple[str, str, str]] = {
    "OFFICIAL":       ("RESMİ",      "#16a34a", "#dcfce7"),
    "CORROBORATED":   ("DOĞRULANDI", "#2563eb", "#dbeafe"),
    "TM_CONFIRMED":   ("TM KADRO",   "#7c3aed", "#ede9fe"),
    "RUMOR":          ("SÖYLENTI",   "#d97706", "#fef3c7"),
    "REVIEW_REQUIRED":("TAKİPTE",    "#6b7280", "#f1f5f9"),
}

WINDOW_OPEN  = "1 Haziran 2026"
WINDOW_CLOSE = "31 Ağustos 2026"


def _mv(eur: int | None) -> str:
    if not eur:
        return "—"
    if eur >= 1_000_000:
        return f"€{eur / 1_000_000:.1f}M"
    return f"€{eur // 1000}K"


def _title(name: str | None) -> str:
    if not name:
        return "?"
    low = name.replace("İ", "i").replace("I", "ı").lower()
    return " ".join(w.capitalize() for w in low.split())


def _load_signals() -> list[dict]:
    path = PROCESSED_DIR / f"news_intelligence_{SEASON}.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("transfers", data.get("transfer_signals", []))


def _load_tm_signals() -> list[dict]:
    """TM kadro dedektöründen gelen hareket sinyallerini haber sinyali formatına çevir."""
    paths = [
        PROCESSED_DIR / f"tm_squad_changes_{TRANSFER_WATCH_SEASON}.json",
        PROCESSED_DIR / f"tm_squad_changes_{SEASON}.json",
    ]
    path = next((candidate for candidate in paths if candidate.exists()), None)
    if path is None:
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("status") == "baseline_only":
        return []
    signals = []
    for a in data.get("arrivals", []):
        signals.append({
            "player_name": a.get("player_name"),
            "from_club": a.get("from_team"),
            "to_club": a.get("to_team"),
            "transfer_type": "permanent",
            "verification_status": "TM_CONFIRMED",
            "tm_market_value_eur": a.get("market_value_eur"),
            "source": "Transfermarkt Kadro",
            "title": f"{a.get('player_name')} — TM kadro hareketi",
            "link": a.get("profile_url", ""),
        })
    return signals


def _enrich(signals: list[dict]) -> list[dict]:
    result = []
    for s in signals:
        player = _title(s.get("player_name"))
        from_c = _title(s.get("from_club"))
        to_c   = _title(s.get("to_club"))
        status = s.get("verification_status") or s.get("confidence") or "REVIEW_REQUIRED"
        if status not in STATUS_META:
            status = "REVIEW_REQUIRED"
        mv = s.get("tm_market_value_eur")
        result.append({
            "player":       player,
            "from_club":    from_c,
            "to_club":      to_c,
            "transfer_type": s.get("transfer_type", "permanent"),
            "status":       status,
            "market_value_eur": mv,
            "market_value_text": _mv(mv),
            "source":       s.get("source", "?"),
            "title":        s.get("title", ""),
            "link":         s.get("link", ""),
            "published_at": s.get("published_at", ""),
            "window":       s.get("window", "summer_2026"),
        })
    return sorted(result, key=lambda x: (
        {"OFFICIAL": 0, "CORROBORATED": 1, "RUMOR": 2, "REVIEW_REQUIRED": 3}.get(x["status"], 9),
        -(x["market_value_eur"] or 0),
    ))


def _build_summary(signals: list[dict]) -> dict:
    official   = [s for s in signals if s["status"] == "OFFICIAL"]
    confirmed  = [s for s in signals if s["status"] in ("OFFICIAL", "CORROBORATED")]
    total_mv   = sum(s["market_value_eur"] for s in confirmed if s["market_value_eur"])
    by_status  = {}
    for s in signals:
        by_status[s["status"]] = by_status.get(s["status"], 0) + 1
    return {
        "total_signals":    len(signals),
        "official_count":   len(official),
        "confirmed_count":  len(confirmed),
        "total_value_eur":  total_mv,
        "by_status":        by_status,
    }


def _row_html(s: dict) -> str:
    label, color, bg = STATUS_META[s["status"]]
    mv = escape(s["market_value_text"])
    player = escape(s["player"])
    frm    = escape(s["from_club"])
    to     = escape(s["to_club"])
    tt     = "Kalıcı" if s["transfer_type"] == "permanent" else "Kiralık"
    link   = s.get("link", "")
    title  = escape(s.get("title", "") or s["player"])
    src    = escape(s.get("source", "?"))
    link_cell = (
        f'<a href="{escape(link)}" target="_blank" style="color:var(--green);font-size:11px">{title[:60]}{"…" if len(title) > 60 else ""}</a>'
        if link else f'<span style="color:var(--muted);font-size:11px">{src}</span>'
    )
    return f"""<tr>
  <td><strong>{player}</strong></td>
  <td>{frm}</td>
  <td>→</td>
  <td>{to}</td>
  <td><span style="font-size:10px;padding:2px 7px;border-radius:4px;font-weight:700;color:{color};background:{bg}">{label}</span></td>
  <td style="color:var(--muted);font-size:12px">{tt}</td>
  <td style="font-weight:600">{mv}</td>
  <td>{link_cell}</td>
</tr>"""


def _news_section_html(unnamed: list[dict]) -> str:
    if not unnamed:
        return ""
    items = "".join(
        f"""<div style="padding:10px 0;border-bottom:1px solid var(--line)">
  <a href="{escape(s.get('link','')or'#')}" target="_blank" rel="noopener"
     style="color:var(--ink);font-size:13px;font-weight:600;text-decoration:none;line-height:1.4">
    {escape((s.get('title') or s.get('source') or '—')[:120])}
  </a>
  <div style="font-size:11px;color:var(--muted);margin-top:3px">{escape(s.get('source',''))} · {escape(s.get('published_at','')[:10] or '—')}</div>
</div>"""
        for s in unnamed
    )
    return f"""
<section style="background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:18px;margin-top:24px">
  <h2 style="font-size:16px;font-weight:700;margin:0 0 14px;padding-bottom:8px;border-bottom:1px solid var(--line)">
    Takip Edilen Haberler <span style="font-weight:400;color:var(--muted);font-size:13px">({len(unnamed)} haber — oyuncu adı henüz doğrulanmadı)</span>
  </h2>
  {items}
</section>"""


def build_html(signals: list[dict], summary: dict) -> str:
    from urllib.parse import quote
    now = datetime.now(timezone.utc).strftime("%d.%m.%Y %H:%M")
    named   = [s for s in signals if s["player"] != "?"]
    unnamed = [s for s in signals if s["player"] == "?"]
    rows = "\n".join(_row_html(s) for s in named) if named else "<tr><td colspan='8' style='padding:24px;text-align:center;color:var(--muted)'>Henüz kayıtlı transfer yok</td></tr>"
    share_text = quote(
        f"Süper Lig transfer radarı: {summary['official_count']} resmi, "
        f"{summary['total_signals']} sinyal takipte — metric11.com"
    )
    total_mv_label = _mv(summary["total_value_eur"])
    stat_pills = "".join(
        f"""<div style="background:#0f2018;border-radius:10px;padding:14px 20px;text-align:center;min-width:110px;flex:1">
  <div style="font-size:22px;font-weight:700;color:{STATUS_META.get(k, ('','#cde94e',''))[1] or '#cde94e'}">{v}</div>
  <div style="font-size:11px;color:#8fa89a;margin-top:2px">{STATUS_META.get(k,('?','',''))[0]}</div>
</div>"""
        for k, v in sorted(summary["by_status"].items())
    )
    return f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Transfer Takip — Süper Lig {TRANSFER_WATCH_SEASON_LABEL} | metric11</title>
<meta name="description" content="Süper Lig yaz transfer penceresi takibi: resmi transferler, teyitli iddialar ve TM kadro değişiklikleri — metric11.">
<meta property="og:title" content="Transfer Takip — Süper Lig {TRANSFER_WATCH_SEASON_LABEL} | metric11">
<meta property="og:description" content="Süper Lig yaz transfer penceresi takibi: resmi transferler, teyitli iddialar ve TM kadro değişiklikleri.">
<meta property="og:image" content="https://metric11.com/og_home.png">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://metric11.com/og_home.png">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<style>
  :root{{--bg:#f3f5f4;--panel:#fff;--ink:#132018;--muted:#627067;--line:#d7ded9;--dark:#091810;--green:#116447;--lime:#cde94e}}
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:Inter,'Segoe UI',Arial,sans-serif;background:var(--bg);color:var(--ink)}}
  .topbar{{min-height:58px;padding:0 clamp(14px,3vw,32px);display:flex;align-items:center;justify-content:space-between;gap:18px;background:var(--dark);color:white;border-bottom:2px solid #1a3023}}
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
  .header{{background:var(--dark);border-bottom:3px solid #1a3023;padding:24px clamp(14px,3vw,32px)}}
  .header h1{{font-size:28px;font-weight:700;color:white;margin-bottom:6px}}
  .header .sub{{color:#8fa89a;font-size:13px}}
  .stat-bar{{display:flex;gap:12px;padding:18px clamp(12px,3vw,32px);flex-wrap:wrap;max-width:1400px;margin:0 auto}}
  .stat-mv{{background:linear-gradient(135deg,#064e3b,#065f46);border-radius:10px;padding:14px 20px;text-align:center;min-width:140px;flex:1}}
  .stat-mv .v{{font-size:22px;font-weight:700;color:#34d399}}
  .stat-mv .l{{font-size:11px;color:#6ee7b7;margin-top:2px}}
  main{{max-width:1400px;margin:0 auto;padding:18px clamp(12px,3vw,32px) 50px}}
  .filter-bar{{margin-bottom:16px;display:flex;gap:10px;flex-wrap:wrap;align-items:center}}
  .filter-input{{background:white;border:1px solid var(--line);border-radius:6px;padding:9px 13px;color:var(--ink);font-size:14px;outline:none;width:min(280px,100%)}}
  .filter-input:focus{{border-color:var(--green)}}
  .table-wrap{{background:var(--panel);border:1px solid var(--line);border-radius:8px;overflow-x:auto}}
  table{{width:100%;min-width:800px;border-collapse:collapse;font-size:13px}}
  th{{background:#eef2ef;padding:11px 14px;text-align:left;color:var(--muted);font-weight:600;border-bottom:1px solid var(--line);white-space:nowrap}}
  td{{padding:11px 14px;border-bottom:1px solid #edf1ee;vertical-align:middle}}
  tr:hover td{{background:#f7faf7}}
  .info-box{{background:#e8f5ee;border:1px solid #a7c9b3;border-radius:8px;padding:14px 18px;margin-bottom:20px;font-size:13px;color:#116447;line-height:1.6}}
  @media(max-width:600px){{.topbar{{flex-direction:column;align-items:stretch;padding:11px 12px 0;gap:0;min-height:unset}}.brand{{padding-bottom:8px}}.topnav{{border-top:1px solid #1e3228;padding:7px 0 9px}}}}
</style>
</head>
<body>
<div class="topbar">
  <a class="brand" href="/"><b>11</b> metric11<span class="slbl">Süper Lig {TRANSFER_WATCH_SEASON_LABEL}</span></a>
  <nav class="topnav">
    <a href="/">Gündem</a>
    <a class="active" href="transfer_tracker_{SEASON}.html">Transferler</a>
    <a href="all_teams_preview_dashboard_{SEASON}.html">{preview_nav_label()}</a>
    <a href="transfer_recommendation_report_{SEASON}.html">Scout</a>
    <a href="football_intelligence_home.html">Analiz</a>
  </nav>
</div>
<div class="header">
  <h1>Transfer Takip — {TRANSFER_WATCH_SEASON_LABEL}</h1>
  <div class="sub">Yaz penceresi: {WINDOW_OPEN} – {WINDOW_CLOSE} · {summary['total_signals']} sinyal · Güncelleme: {now}</div>
</div>
<div class="stat-bar">
  {stat_pills}
  <div class="stat-mv"><div class="v">{total_mv_label}</div><div class="l">Toplam Teyitli Değer</div></div>
</div>
<main>
  <div class="filter-bar">
    <input class="filter-input" id="filterInput" placeholder="Oyuncu veya kulüp ara…" oninput="filterRows(this.value)">
    <span style="font-size:13px;color:var(--muted)">{len(named)} kayıt</span>
  </div>
  <div class="table-wrap">
    <table id="transferTable">
      <thead><tr>
        <th>Oyuncu</th><th>Kaynak Kulüp</th><th></th><th>Hedef Kulüp</th>
        <th>Durum</th><th>Tip</th><th>Piyasa Değeri</th><th>Kaynak</th>
      </tr></thead>
      <tbody id="tbody">{rows}</tbody>
    </table>
  </div>
  {_news_section_html(unnamed)}
  <div style="margin-top:24px;padding-top:16px;border-top:1px solid var(--line);display:flex;gap:14px;flex-wrap:wrap;align-items:center">
    <a href="transfer_season_context_{SEASON}.html" style="color:var(--green);font-size:13px;font-weight:600">→ Serbest Kalacak Oyuncular &amp; Sözleşme Analizi</a>
    <a href="transfer_recommendation_report_{SEASON}.html" style="color:var(--green);font-size:13px;font-weight:600">→ Takım Bazlı Transfer Önerileri</a>
  </div>
  <div style="margin-top:16px">
    <a class="x-share" href="https://twitter.com/intent/tweet?text={share_text}&url=https%3A%2F%2Fmetric11.com%2Ftransfer_tracker_{SEASON}.html" target="_blank" rel="noopener"
       style="display:inline-flex;align-items:center;gap:8px;background:#000;color:#fff;text-decoration:none;font-size:14px;font-weight:700;padding:10px 18px;border-radius:8px">
      𝕏 Paylaş
    </a>
  </div>
</main>
<script>
function filterRows(q) {{
  q = q.toLowerCase();
  document.querySelectorAll('#tbody tr').forEach(row => {{
    row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
  }});
}}
</script>
<footer style="text-align:center;padding:40px 16px 28px;color:#8a9e92;font-size:12px;border-top:1px solid #e2e8e4;margin-top:48px;">
  metric11 &middot; <a href="mailto:hello@metric11.com" style="color:#8a9e92;text-decoration:none;border-bottom:1px solid #c5d4ca;">hello@metric11.com</a>
</footer>
<script defer src="/_vercel/insights/script.js"></script>
</body>
</html>"""


def main() -> None:
    signals_raw = _load_signals() + _load_tm_signals()
    # TM sinyalleriyle haber sinyallerini birleştir; aynı oyuncu için TM olanı tercih et
    seen: dict[str, int] = {}
    deduped = []
    for s in signals_raw:
        key = (s.get("player_name") or "").upper().strip()
        if not key:
            deduped.append(s)
            continue
        if key in seen:
            existing = deduped[seen[key]]
            if s.get("verification_status") in ("TM_CONFIRMED", "OFFICIAL", "CORROBORATED"):
                deduped[seen[key]] = s
        else:
            seen[key] = len(deduped)
            deduped.append(s)
    signals_raw = deduped
    signals = _enrich(signals_raw)
    summary = _build_summary(signals)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "season": SEASON,
        "transfer_watch_season": TRANSFER_WATCH_SEASON,
        "summary": summary,
        "transfers": signals,
    }
    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    OUTPUT_HTML.write_text(build_html(signals, summary), encoding="utf-8")
    print(f"✓ {len(signals)} transfer sinyali · {OUTPUT_HTML}")


if __name__ == "__main__":
    main()
