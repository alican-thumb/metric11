"""
Claude analizi yapılmış haber verilerinden HTML istihbarat dashboard'u üretir.
Transfer, sakat, cezalı, sözleşme ve genel haber kategorilerini Süper Lig takım verisiyle birleştirir.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from src.config import PROCESSED_DIR, SEASON, SEASON_LABEL


def main() -> None:
    parser = argparse.ArgumentParser(description="Haber istihbarat dashboard'u üretir.")
    parser.add_argument("--input", default=str(PROCESSED_DIR / f"news_intelligence_{SEASON}.json"))
    parser.add_argument("--rss-fallback", default=str(PROCESSED_DIR / f"news_rss_latest_{SEASON}.json"))
    parser.add_argument("--output", default=str(PROCESSED_DIR / f"news_intelligence_dashboard_{SEASON}.html"))
    args = parser.parse_args()

    input_path = Path(args.input)
    if input_path.exists():
        intel = json.loads(input_path.read_text(encoding="utf-8"))
    else:
        # Fallback: build basic intel from raw RSS without Claude analysis
        rss_path = Path(args.rss_fallback)
        if not rss_path.exists():
            raise SystemExit(f"Ne istihbarat dosyası ne de RSS dosyası bulunamadı.")
        intel = _build_basic_intel_from_rss(json.loads(rss_path.read_text(encoding="utf-8")))

    html = build_html(intel)
    Path(args.output).write_text(html, encoding="utf-8")
    print(args.output)


def _build_basic_intel_from_rss(rss_payload: dict) -> dict:
    """Claude analizi olmadan ham RSS verilerinden temel istihbarat yapısı üretir."""
    articles = rss_payload.get("articles", [])
    relevant = [a for a in articles if a.get("super_lig_relevant")]
    recent = sorted(relevant or articles, key=lambda a: a.get("published_at") or "", reverse=True)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "season": SEASON,
        "total_articles": len(articles),
        "analyzed_articles": 0,
        "transfer_signals": sum(1 for a in articles if "transfer" in a.get("categories", [])),
        "injury_signals": sum(1 for a in articles if "injury" in a.get("categories", [])),
        "suspension_signals": sum(1 for a in articles if "suspension" in a.get("categories", [])),
        "player_mentions": 0,
        "transfers": [],
        "injuries": [],
        "suspensions": [],
        "recent_articles": [
            {
                "article_id": a["article_id"],
                "title": a["title"],
                "link": a["link"],
                "source": a["source_name"],
                "published_at": a.get("published_at"),
                "categories": a.get("categories", []),
                "super_lig_relevant": a.get("super_lig_relevant"),
                "summary_tr": a.get("summary", "")[:200],
                "tags": a.get("categories", []),
            }
            for a in recent[:60]
        ],
    }


def build_html(intel: dict) -> str:
    transfer_rows = _build_transfer_rows(intel.get("transfers", []))
    injury_rows = _build_injury_rows(intel.get("injuries", []))
    suspension_rows = _build_suspension_rows(intel.get("suspensions", []))
    news_feed = _build_news_feed(intel.get("recent_articles", []))
    promo_count = intel.get("promotion_signals", 0)

    total = intel.get("total_articles", 0)
    analyzed = intel.get("analyzed_articles", 0)
    gen_at = intel.get("generated_at", "")[:16].replace("T", " ")

    return f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Haber İstihbaratı {SEASON_LABEL}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0f172a; color: #e2e8f0; }}
  .header {{ background: linear-gradient(135deg, #1e293b, #0f172a); border-bottom: 1px solid #334155; padding: 20px 28px; }}
  .header h1 {{ font-size: 1.4rem; font-weight: 700; color: #f8fafc; }}
  .header .sub {{ color: #94a3b8; font-size: 0.8rem; margin-top: 4px; }}
  .summary-bar {{ display: flex; gap: 12px; padding: 14px 28px; background: #1e293b; border-bottom: 1px solid #334155; flex-wrap: wrap; }}
  .pill {{ background: #0f172a; border: 1px solid #334155; border-radius: 8px; padding: 8px 14px; }}
  .pill .val {{ font-size: 1.3rem; font-weight: 700; color: #38bdf8; }}
  .pill .lbl {{ font-size: 0.7rem; color: #64748b; margin-top: 1px; }}
  .tabs {{ display: flex; padding: 0 28px; background: #1e293b; border-bottom: 1px solid #334155; overflow-x: auto; }}
  .tab {{ padding: 11px 18px; cursor: pointer; font-size: 0.82rem; color: #94a3b8; border-bottom: 2px solid transparent; white-space: nowrap; }}
  .tab.active {{ color: #38bdf8; border-bottom-color: #38bdf8; font-weight: 600; }}
  .content {{ padding: 24px 28px; max-width: 1300px; }}
  .section {{ display: none; }}
  .section.active {{ display: block; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.82rem; }}
  th {{ background: #0f172a; padding: 10px 12px; text-align: left; color: #64748b; font-weight: 600; border-bottom: 1px solid #334155; white-space: nowrap; }}
  td {{ padding: 9px 12px; border-bottom: 1px solid #1e293b; color: #cbd5e1; vertical-align: top; }}
  tr:hover td {{ background: #1e293b; }}
  .badge {{ display: inline-block; padding: 2px 7px; border-radius: 4px; font-size: 0.68rem; font-weight: 700; color: #fff; }}
  .conf-high {{ background: #16a34a; }}
  .conf-medium {{ background: #d97706; }}
  .conf-low {{ background: #64748b; }}
  .tag {{ background: #1e293b; border: 1px solid #334155; border-radius: 3px; padding: 1px 5px; font-size: 0.65rem; color: #94a3b8; margin-right: 3px; }}
  .news-card {{ background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 14px 16px; margin-bottom: 10px; }}
  .news-card:hover {{ border-color: #475569; }}
  .news-title {{ font-weight: 600; font-size: 0.88rem; color: #f1f5f9; margin-bottom: 4px; }}
  .news-meta {{ font-size: 0.72rem; color: #64748b; margin-bottom: 6px; }}
  .news-summary {{ font-size: 0.78rem; color: #94a3b8; line-height: 1.4; }}
  .news-tags {{ margin-top: 8px; }}
  .filter-bar {{ margin-bottom: 16px; }}
  .filter-input {{ background: #1e293b; border: 1px solid #334155; border-radius: 6px; padding: 7px 12px; color: #e2e8f0; font-size: 0.82rem; outline: none; min-width: 200px; }}
  .filter-input:focus {{ border-color: #38bdf8; }}
  a {{ color: #38bdf8; text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  .mv-badge {{ color: #fbbf24; font-weight: 600; }}
  .empty {{ color: #475569; font-size: 0.85rem; padding: 20px 0; text-align: center; }}
</style>
</head>
<body>
<div class="header">
  <h1>📰 Haber İstihbaratı — Süper Lig {SEASON_LABEL}</h1>
  <div class="sub">Claude AI analizi · {analyzed}/{total} makale analiz edildi · {gen_at} UTC</div>
</div>
<div class="summary-bar">
  <div class="pill"><div class="val">{total}</div><div class="lbl">Toplam Makale</div></div>
  <div class="pill"><div class="val">{analyzed}</div><div class="lbl">Analiz Edilen</div></div>
  <div class="pill"><div class="val" style="color:#22c55e">{intel.get('transfer_signals',0)}</div><div class="lbl">Transfer Sinyali</div></div>
  <div class="pill"><div class="val" style="color:#ef4444">{intel.get('injury_signals',0)}</div><div class="lbl">Sakat Sinyali</div></div>
  <div class="pill"><div class="val" style="color:#f59e0b">{intel.get('suspension_signals',0)}</div><div class="lbl">Cezalı Sinyali</div></div>
  <div class="pill"><div class="val">{intel.get('player_mentions',0)}</div><div class="lbl">Oyuncu Haberi</div></div>
  <div class="pill"><div class="val" style="color:#a78bfa">{intel.get('promotion_signals',0)}</div><div class="lbl">Lig Değişikliği</div></div>
</div>
<div class="tabs">
  <div class="tab active" onclick="showTab('feed',this)">Haber Akışı</div>
  <div class="tab" onclick="showTab('transfers',this)">Transfer Radar</div>
  <div class="tab" onclick="showTab('injuries',this)">Sakat / Cezalı</div>
  <div class="tab" onclick="showTab('promotions',this)">Lig Değişiklikleri</div>
</div>
<div class="content">
  <div id="feed" class="section active">
    <div class="filter-bar">
      <input class="filter-input" id="feedFilter" placeholder="Haber ara (takım, oyuncu...)..." oninput="filterFeed()"/>
    </div>
    <div id="newsFeed">
      {news_feed if news_feed else '<div class="empty">Henüz analiz edilmiş haber yok. analyze_news_with_claude çalıştır.</div>'}
    </div>
  </div>
  <div id="transfers" class="section">
    {f'''<table>
      <thead><tr>
        <th>Oyuncu</th><th>Gönderen</th><th>Alan</th><th>Tip</th>
        <th>Bedel / Değer</th><th>Güven</th><th>Kaynak</th><th>Tarih</th>
      </tr></thead>
      <tbody>{transfer_rows}</tbody>
    </table>''' if transfer_rows else '<div class="empty">Transfer sinyali bulunamadı.</div>'}
  </div>
  <div id="injuries" class="section">
    {f'''<table>
      <thead><tr>
        <th>Oyuncu</th><th>Kulüp</th><th>Tip</th><th>Süre</th><th>Güven</th><th>Tarih</th>
      </tr></thead>
      <tbody>{injury_rows}{suspension_rows}</tbody>
    </table>''' if (injury_rows or suspension_rows) else '<div class="empty">Sakat/cezalı sinyali bulunamadı.</div>'}
  </div>
  <div id="promotions" class="section">
    {_build_promotions_section(intel)}
  </div>
</div>
<script>
function showTab(id, el) {{
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  el.classList.add('active');
}}
function filterFeed() {{
  const q = document.getElementById('feedFilter').value.toLowerCase();
  document.querySelectorAll('.news-card').forEach(card => {{
    card.style.display = card.dataset.text.includes(q) ? '' : 'none';
  }});
}}
</script>
</body>
</html>"""


def _conf_class(conf: str) -> str:
    return {"HIGH": "conf-high", "MEDIUM": "conf-medium"}.get(conf, "conf-low")


def _format_date(dt_str: str | None) -> str:
    if not dt_str:
        return "—"
    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        return dt.strftime("%d.%m %H:%M")
    except Exception:  # noqa: BLE001
        return dt_str[:10]


def _build_transfer_rows(transfers: list[dict]) -> str:
    if not transfers:
        return ""
    rows = ""
    for t in transfers[:40]:
        conf = t.get("confidence", "LOW")
        fee = ""
        if t.get("fee_eur_million"):
            fee = f"€{t['fee_eur_million']}M"
        elif t.get("fee_try_million"):
            fee = f"₺{t['fee_try_million']}M"
        else:
            fee = "Serbest" if t.get("transfer_type") == "free" else "Bilinmiyor"
        mv = t.get("tm_market_value_eur")
        mv_str = f" <span class='mv-badge'>€{mv/1_000_000:.1f}M</span>" if mv else ""
        rows += (
            f"<tr>"
            f"<td><strong>{t.get('player_name','')}</strong>{mv_str}</td>"
            f"<td style='color:#94a3b8'>{t.get('from_club','?')}</td>"
            f"<td style='color:#22c55e;font-weight:600'>{t.get('to_club','?')}</td>"
            f"<td><span class='tag'>{t.get('transfer_type','?')}</span></td>"
            f"<td>{fee}</td>"
            f"<td><span class='badge {_conf_class(conf)}'>{conf}</span></td>"
            f"<td><a href='{t.get('link','#')}' target='_blank'>{t.get('source','?')[:15]}</a></td>"
            f"<td style='color:#64748b'>{_format_date(t.get('published_at'))}</td>"
            f"</tr>"
        )
    return rows


def _build_injury_rows(injuries: list[dict]) -> str:
    rows = ""
    for inj in injuries[:20]:
        conf = inj.get("confidence", "LOW")
        weeks = f"~{inj['estimated_weeks_out']} hafta" if inj.get("estimated_weeks_out") else (inj.get("return_date") or "Belirsiz")
        mv = inj.get("tm_market_value_eur")
        mv_str = f" <span class='mv-badge'>€{mv/1_000_000:.1f}M</span>" if mv else ""
        rows += (
            f"<tr>"
            f"<td><strong>{inj.get('player_name','')}</strong>{mv_str}</td>"
            f"<td style='color:#94a3b8'>{inj.get('club','?')}</td>"
            f"<td style='color:#ef4444'>{inj.get('injury_type','?')}</td>"
            f"<td>{weeks}</td>"
            f"<td><span class='badge {_conf_class(conf)}'>{conf}</span></td>"
            f"<td style='color:#64748b'>{_format_date(inj.get('published_at'))}</td>"
            f"</tr>"
        )
    return rows


def _build_suspension_rows(suspensions: list[dict]) -> str:
    rows = ""
    for sus in suspensions[:15]:
        conf = sus.get("confidence", "LOW")
        matches = f"{sus['matches_missed']} maç" if sus.get("matches_missed") else "Belirsiz"
        mv = sus.get("tm_market_value_eur")
        mv_str = f" <span class='mv-badge'>€{mv/1_000_000:.1f}M</span>" if mv else ""
        rows += (
            f"<tr>"
            f"<td><strong>{sus.get('player_name','')}</strong>{mv_str}</td>"
            f"<td style='color:#94a3b8'>{sus.get('club','?')}</td>"
            f"<td style='color:#f59e0b'>Cezalı — {sus.get('reason','?')}</td>"
            f"<td>{matches}</td>"
            f"<td><span class='badge {_conf_class(conf)}'>{conf}</span></td>"
            f"<td style='color:#64748b'>—</td>"
            f"</tr>"
        )
    return rows


def _build_news_feed(articles: list[dict]) -> str:
    if not articles:
        return ""
    html = ""
    for a in articles:
        cats = a.get("categories", [])
        tags = a.get("tags", [])
        clubs = a.get("mentioned_clubs", [])
        all_tags = list(set(cats + tags + clubs))[:8]
        tag_html = "".join(f"<span class='tag'>{t}</span>" for t in all_tags)
        source = a.get("source", "")
        date_str = _format_date(a.get("published_at"))
        summary = a.get("summary_tr") or ""
        is_twitter = a.get("source_type") == "twitter"
        source_icon = "𝕏 " if is_twitter else ""
        source_color = "color:#1d9bf0" if is_twitter else ""
        search_text = f"{a.get('title','')} {summary} {' '.join(all_tags)} {source}".lower()
        html += (
            f"<div class='news-card' data-text='{search_text}'>"
            f"<div class='news-title'><a href='{a.get('link','#')}' target='_blank'>{a.get('title','')}</a></div>"
            f"<div class='news-meta' style='{source_color}'>{source_icon}{source} · {date_str}</div>"
            f"<div class='news-summary'>{summary}</div>"
            f"<div class='news-tags'>{tag_html}</div>"
            f"</div>"
        )
    return html


def _build_promotions_section(intel: dict) -> str:
    promotions = intel.get("promotions", [])
    promo_cards = ""
    for p in promotions[:20]:
        event = p.get("event_type", "")
        color = "#22c55e" if "promot" in event or "champion" in event or "playoff" in event else "#ef4444"
        label = "YÜKSELME" if "promot" in event or "champion" in event or "playoff" in event else "DÜŞME"
        conf = p.get("confidence", "LOW")
        promo_cards += (
            f"<div class='news-card'>"
            f"<div class='news-title' style='color:{color}'>"
            f"<span class='badge' style='background:{color}'>{label}</span> "
            f"{p.get('club','?')} — {p.get('detail','')[:100]}"
            f"</div>"
            f"<div class='news-meta'>{p.get('source','?')} · {_format_date(p.get('published_at'))} · güven: {conf}</div>"
            f"</div>"
        )

    context = f"""
<div style='background:#1e293b;border:1px solid #334155;border-radius:8px;padding:16px;margin-bottom:20px;'>
  <h3 style='color:#f1f5f9;font-size:0.95rem;margin-bottom:12px;'>2026-2027 Sezonu Etkileyenler</h3>
  <p style='color:#94a3b8;font-size:0.8rem;line-height:1.5;'>
    Süper Lig'e yükselen takımlar yeni kadro ihtiyaçlarıyla aktif transfer yapacak.
    Küme düşen takımların yıldızları serbest transfer fırsatına dönüşebilir.
    Aşağıdaki sinyaller haber kaynaklarından otomatik çıkarıldı.
  </p>
</div>
{promo_cards if promo_cards else '<div class="empty">Henüz promosyon/küme düşme sinyali tespit edilmedi.</div>'}"""
    return context


if __name__ == "__main__":
    main()
