"""Search Console ve trafik snapshot'larından haftalık büyüme raporu üretir."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from urllib.parse import urlparse

from src.config import PROCESSED_DIR
from src.html_utils import page_html

MANUAL_DIR = Path("data/manual")
OUTPUT_JSON = PROCESSED_DIR / "growth_measurement_2026_2027.json"
OUTPUT_MD = PROCESSED_DIR / "growth_measurement_2026_2027.md"
OUTPUT_HTML = PROCESSED_DIR / "growth_measurement_2026_2027.html"


def _load_snapshots(directory: Path = MANUAL_DIR) -> list[dict]:
    snapshots = []
    for path in sorted(directory.glob("growth_metrics_snapshot_*.json")):
        try:
            item = json.loads(path.read_text(encoding="utf-8"))
            item["snapshot_file"] = path.name
            snapshots.append(item)
        except (OSError, json.JSONDecodeError):
            continue
    return sorted(snapshots, key=lambda item: item.get("captured_at", ""))


def _ctr(clicks: int, impressions: int) -> float:
    return clicks / impressions if impressions else 0.0


def _delta(current: dict, previous: dict | None) -> dict:
    if not previous:
        return {"available": False}
    cur_perf = current.get("performance", {})
    prev_perf = previous.get("performance", {})
    cur_index = current.get("indexing", {})
    prev_index = previous.get("indexing", {})
    return {
        "available": True,
        "clicks": cur_perf.get("clicks", 0) - prev_perf.get("clicks", 0),
        "impressions": cur_perf.get("impressions", 0) - prev_perf.get("impressions", 0),
        "ctr": cur_perf.get("ctr", 0) - prev_perf.get("ctr", 0),
        "indexed": cur_index.get("indexed", 0) - prev_index.get("indexed", 0),
        "not_indexed": cur_index.get("not_indexed", 0) - prev_index.get("not_indexed", 0),
    }


def build_report(snapshots: list[dict]) -> dict:
    if not snapshots:
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "status": "missing_snapshot",
            "actions": ["Search Console performans snapshot'ı eklenmeli."],
        }

    current = snapshots[-1]
    previous = snapshots[-2] if len(snapshots) > 1 else None
    perf = current.get("performance", {})
    indexing = current.get("indexing", {})
    reasons = indexing.get("reasons", {})
    queries = []
    for row in current.get("queries", []):
        item = dict(row)
        item["ctr"] = _ctr(item.get("clicks", 0), item.get("impressions", 0))
        queries.append(item)
    pages = []
    for row in current.get("pages", []):
        item = dict(row)
        item["ctr"] = _ctr(item.get("clicks", 0), item.get("impressions", 0))
        item["label"] = urlparse(item.get("url", "")).path or "/"
        pages.append(item)

    zero_click_queries = sorted(
        (row for row in queries if row["clicks"] == 0 and row["impressions"] > 0),
        key=lambda row: -row["impressions"],
    )
    zero_click_pages = sorted(
        (row for row in pages if row["clicks"] == 0 and row["impressions"] > 0),
        key=lambda row: -row["impressions"],
    )
    impressions = perf.get("impressions", 0)
    ctr = perf.get("ctr", 0)
    discovered = reasons.get("discovered_not_indexed", 0)
    actions = []
    if impressions < 1000:
        actions.append("Birincil darboğaz gösterim hacmi: yeni seri sayfa yerine mevcut güçlü sayfalara dağıtım ve referans bağlantı sağla.")
    if ctr >= 0.08:
        actions.append("CTR sağlıklı; başlıkları topluca değiştirme. Öncelik daha fazla sorguda görünmek olmalı.")
    if discovered > indexing.get("indexed", 0):
        actions.append("Keşfedilip indekslenmeyen URL yığını yüksek. Noindex temizliğinin etkisini sonraki GSC güncellemesinde ölç.")
    if zero_click_queries:
        actions.append(f"İlk içerik fırsatı: '{zero_click_queries[0]['query']}' sorgusu için mevcut hedef sayfayı güçlendir.")
    vercel = current.get("vercel_analytics", {})
    if vercel.get("status") != "connected":
        actions.append("Vercel Web Analytics interaktif onayı tamamlanmadan sosyal UTM oturumları ölçülemez.")

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "ready",
        "snapshot": {
            "captured_at": current.get("captured_at"),
            "file": current.get("snapshot_file"),
            "period": current.get("period", {}),
            "source": current.get("source"),
        },
        "performance": perf,
        "indexing": indexing,
        "vercel_analytics": vercel,
        "delta": _delta(current, previous),
        "queries": sorted(queries, key=lambda row: (-row["clicks"], -row["impressions"])),
        "pages": sorted(pages, key=lambda row: (-row["clicks"], -row["impressions"])),
        "opportunities": {
            "zero_click_queries": zero_click_queries,
            "zero_click_pages": zero_click_pages,
        },
        "actions": actions,
    }


def _pct(value: float | None) -> str:
    return "—" if value is None else f"%{value * 100:.1f}".replace(".", ",")


def build_markdown(report: dict) -> str:
    if report.get("status") != "ready":
        return "# Büyüme Ölçümü\n\nHenüz Search Console snapshot'ı yok.\n"
    p = report["performance"]
    i = report["indexing"]
    lines = [
        "# metric11 Büyüme Ölçümü",
        "",
        f"- Dönem: {report['snapshot']['period'].get('label', '—')}",
        f"- Tıklama: {p.get('clicks', 0)}",
        f"- Gösterim: {p.get('impressions', 0)}",
        f"- CTR: {_pct(p.get('ctr'))}",
        f"- Ortalama konum: {p.get('average_position', '—')}",
        f"- İndeksli / indeks dışı: {i.get('indexed', 0)} / {i.get('not_indexed', 0)}",
        "",
        "## Öncelikli Aksiyonlar",
        "",
    ]
    lines.extend(f"- {action}" for action in report["actions"])
    lines.extend(["", "## En Çok Trafik Alan Sayfalar", "", "| Sayfa | Tıklama | Gösterim | CTR |", "|---|---:|---:|---:|"])
    for row in report["pages"][:10]:
        lines.append(f"| {row['label']} | {row['clicks']} | {row['impressions']} | {_pct(row['ctr'])} |")
    return "\n".join(lines) + "\n"


def build_html(report: dict) -> str:
    if report.get("status") != "ready":
        return page_html("Büyüme Ölçümü", "<h1>Büyüme Ölçümü</h1><p>Henüz veri snapshot'ı yok.</p>", noindex=True)
    p = report["performance"]
    i = report["indexing"]
    reasons = i.get("reasons", {})
    vercel = report.get("vercel_analytics", {})
    cards = [
        ("Tıklama", str(p.get("clicks", 0)), report["snapshot"]["period"].get("label", "")),
        ("Gösterim", str(p.get("impressions", 0)), "Arama görünürlüğü"),
        ("CTR", _pct(p.get("ctr")), "Sonuçtan siteye geçiş"),
        ("Ort. konum", str(p.get("average_position", "—")).replace(".", ","), "Google sıralaması"),
    ]
    card_html = "".join(
        f'<div class="gm-card"><span>{escape(label)}</span><strong>{escape(value)}</strong><small>{escape(note)}</small></div>'
        for label, value, note in cards
    )
    action_html = "".join(f"<li>{escape(action)}</li>" for action in report["actions"])
    page_rows = "".join(
        f'<tr><td><a href="{escape(row["url"])}">{escape(row["label"])}</a></td><td>{row["clicks"]}</td><td>{row["impressions"]}</td><td>{_pct(row["ctr"])}</td></tr>'
        for row in report["pages"][:10]
    )
    query_rows = "".join(
        f'<tr><td>{escape(row["query"])}</td><td>{row["clicks"]}</td><td>{row["impressions"]}</td><td>{_pct(row["ctr"])}</td></tr>'
        for row in report["queries"][:10]
    )
    body = f"""<style>
.gm-head{{margin:8px 0 22px}}.gm-head h1{{margin:0 0 6px;font-size:clamp(25px,4vw,34px)}}.gm-head p{{margin:0;color:#627067}}
.gm-grid{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:18px 0}}
.gm-card{{border:1px solid #d7ded9;background:#fff;border-radius:8px;padding:16px;display:flex;flex-direction:column;min-width:0}}
.gm-card span{{font-size:12px;color:#627067}}.gm-card strong{{font-size:30px;margin:6px 0}}.gm-card small{{color:#627067}}
.gm-panel{{border:1px solid #d7ded9;background:#fff;border-radius:8px;padding:18px;margin:14px 0}}.gm-panel h2{{font-size:18px;margin:0 0 12px}}
.gm-kpis{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}}.gm-kpi{{background:#f3f5f4;padding:12px;border-radius:6px}}
.gm-kpi b{{display:block;font-size:22px}}.gm-kpi span{{font-size:12px;color:#627067}}
.gm-table-wrap{{overflow-x:auto}}table{{width:100%;border-collapse:collapse;font-size:13px}}th,td{{padding:10px;border-bottom:1px solid #e2e8e4;text-align:right}}th:first-child,td:first-child{{text-align:left}}td a{{color:#116447}}
.gm-warn{{border-left:4px solid #c98000}}.gm-actions{{margin:0;padding-left:20px}}.gm-actions li{{margin:8px 0;line-height:1.5}}
@media(max-width:760px){{.gm-grid{{grid-template-columns:repeat(2,minmax(0,1fr))}}}}@media(max-width:420px){{.gm-grid,.gm-kpis{{grid-template-columns:1fr}}}}
</style>
<section class="gm-head"><h1>Büyüme Ölçümü</h1><p>{escape(report['snapshot']['period'].get('label', ''))} · Snapshot {escape(report['snapshot'].get('captured_at') or '—')}</p></section>
<div class="gm-grid">{card_html}</div>
<section class="gm-panel"><h2>Google indeks kapsamı</h2><div class="gm-kpis">
<div class="gm-kpi"><b>{i.get('indexed', 0)}</b><span>İndekslenen sayfa</span></div><div class="gm-kpi"><b>{i.get('not_indexed', 0)}</b><span>İndeks dışı sayfa</span></div>
<div class="gm-kpi"><b>{reasons.get('discovered_not_indexed', 0)}</b><span>Keşfedildi, henüz indekslenmedi</span></div><div class="gm-kpi"><b>{reasons.get('crawled_not_indexed', 0)}</b><span>Tarandı, indekslenmedi</span></div>
</div></section>
<section class="gm-panel gm-warn"><h2>Öncelikli aksiyonlar</h2><ol class="gm-actions">{action_html}</ol></section>
<section class="gm-panel"><h2>Aramada trafik alan sayfalar</h2><div class="gm-table-wrap"><table><thead><tr><th>Sayfa</th><th>Tıklama</th><th>Gösterim</th><th>CTR</th></tr></thead><tbody>{page_rows}</tbody></table></div></section>
<section class="gm-panel"><h2>Arama sorguları</h2><div class="gm-table-wrap"><table><thead><tr><th>Sorgu</th><th>Tıklama</th><th>Gösterim</th><th>CTR</th></tr></thead><tbody>{query_rows}</tbody></table></div></section>
<section class="gm-panel"><h2>Sosyal trafik ölçümü</h2><p>Vercel Analytics durumu: <strong>{escape(vercel.get('status', 'bilinmiyor'))}</strong>.</p><p>{escape(vercel.get('note', ''))}</p></section>
"""
    return page_html(
        "Büyüme Ölçümü",
        body,
        description="metric11 Search Console, indeks kapsamı ve sosyal trafik ölçüm raporu.",
        noindex=True,
        canonical_path="growth_measurement_2026_2027.html",
    )


def main() -> None:
    report = build_report(_load_snapshots())
    OUTPUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    OUTPUT_MD.write_text(build_markdown(report), encoding="utf-8")
    OUTPUT_HTML.write_text(build_html(report), encoding="utf-8")
    print(f"Büyüme ölçümü: {report.get('status')} -> {OUTPUT_HTML}")


if __name__ == "__main__":
    main()
