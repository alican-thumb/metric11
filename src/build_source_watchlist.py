from __future__ import annotations

import argparse
import json
from html import escape
from pathlib import Path

from src.config import PROCESSED_DIR, ROOT_DIR


def main() -> None:
    parser = argparse.ArgumentParser(description="Veri kaynak izleme listesinden MD/HTML raporu üretir.")
    parser.add_argument("--input", default=str(ROOT_DIR / "data/manual/source_watchlist.json"))
    parser.add_argument("--output-prefix", default="source_watchlist_2025_2026")
    args = parser.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    md_path = PROCESSED_DIR / f"{args.output_prefix}.md"
    html_path = PROCESSED_DIR / f"{args.output_prefix}.html"
    md_path.write_text(build_markdown(payload), encoding="utf-8")
    html_path.write_text(build_html(payload), encoding="utf-8")
    print(md_path.read_text(encoding="utf-8"))


def build_markdown(payload: dict) -> str:
    sources = payload.get("sources", [])
    connected = [source for source in sources if "connected" in source.get("status", "")]
    planned = [source for source in sources if source.get("status") == "planned" or source.get("status") == "research_needed"]
    high_weight = [source for source in sources if source.get("analysis_weight") in {"core", "high_internal"}]
    lines = [
        "# Veri Kaynak İzleme Listesi",
        "",
        f"- Güncelleme: {payload.get('updated_at')}",
        f"- Kaynak sayısı: {len(sources)}",
        f"- Bağlı/yarı bağlı kaynak: {len(connected)}",
        f"- Planlanan/araştırılacak kaynak: {len(planned)}",
        f"- Analizde yüksek ağırlıklı kaynak: {len(high_weight)}",
        "",
        "## Politika",
        "",
    ]
    for value in payload.get("policy", {}).values():
        lines.append(f"- {value}")
    lines.extend(["", "## Kaynaklar", ""])
    for source in sources:
        lines.append(
            f"- {source['name']} ({source['category']}): durum={source['status']}, risk={source['risk']}, "
            f"güncellik={source['freshness_target']}, ağırlık={source['analysis_weight']}, "
            f"alanlar={', '.join(source.get('fields', [])[:7])}"
        )
    lines.extend(["", "## Günlük Veri Önceliği", ""])
    for source in sorted(sources, key=priority_sort):
        if "daily" in source.get("freshness_target", ""):
            lines.append(f"- {source['name']}: {source['freshness_target']} / {', '.join(source.get('use_cases', [])[:4])}")
    return "\n".join(lines)


def priority_sort(source: dict) -> tuple[int, str]:
    weight_rank = {"core": 0, "high_internal": 1, "validation_and_enrichment": 2, "model_training": 3}
    return (weight_rank.get(source.get("analysis_weight"), 9), source.get("name", ""))


def build_html(payload: dict) -> str:
    sources = payload.get("sources", [])
    rows = "".join(source_row(source) for source in sources)
    daily = "".join(source_row(source) for source in sources if "daily" in source.get("freshness_target", ""))
    policy_items = "".join(f"<li>{escape(value)}</li>" for value in payload.get("policy", {}).values())
    return f"""<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Veri Kaynak İzleme Listesi</title>
  <style>
    :root {{ --bg:#f4f6f8; --panel:#fff; --ink:#14171c; --muted:#667085; --line:#dce2ea; --dark:#111318; --red:#bf1f2f; --amber:#b76b00; --green:#137a4b; --blue:#185ea8; --shadow:0 8px 22px rgba(18,24,32,.08); }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; font-family:Inter, system-ui, sans-serif; background:var(--bg); color:var(--ink); }}
    header {{ background:var(--dark); color:white; padding:28px 42px; border-bottom:4px solid var(--blue); }}
    header h1 {{ margin:0 0 7px; font-size:32px; letter-spacing:0; }}
    header p {{ margin:0; color:#c9ced8; max-width:1000px; line-height:1.5; }}
    main {{ max-width:1380px; margin:0 auto; padding:24px; }}
    .metrics {{ display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:18px; }}
    .metric, section {{ background:var(--panel); border:1px solid var(--line); border-radius:8px; box-shadow:var(--shadow); }}
    .metric {{ padding:15px; }}
    .metric span {{ display:block; color:var(--muted); font-size:12px; }}
    .metric strong {{ display:block; font-size:26px; margin-top:5px; }}
    section {{ padding:18px; margin-bottom:18px; overflow-x:auto; }}
    h2 {{ margin:0 0 12px; font-size:18px; }}
    table {{ width:100%; border-collapse:collapse; font-size:13px; }}
    th,td {{ padding:9px 7px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; }}
    th {{ color:var(--muted); font-size:12px; }}
    .pill {{ display:inline-flex; min-height:23px; align-items:center; border-radius:999px; padding:0 8px; font-size:12px; border:1px solid var(--line); }}
    .high {{ color:var(--red); background:#fff0f2; border-color:#efb7bf; }}
    .medium {{ color:var(--amber); background:#fff7e8; border-color:#f2d09a; }}
    .low {{ color:var(--green); background:#edf9f3; border-color:#b9dfcd; }}
    .status {{ color:var(--blue); background:#edf5ff; border-color:#bbd7f5; }}
    ul {{ margin:0; padding-left:18px; line-height:1.6; }}
    @media (max-width:900px) {{ .metrics {{ grid-template-columns:1fr 1fr; }} main {{ padding:14px; }} header {{ padding:22px; }} table {{ font-size:12px; }} }}
    @media (max-width:620px) {{ .metrics {{ grid-template-columns:1fr; }} }}
  </style>
</head>
<body>
  <header>
    <h1>Veri Kaynak İzleme Listesi</h1>
    <p>metric11.com için canlı/güncel veri kaynakları, risk seviyesi, kullanım amacı ve güncelleme ritmi.</p>
  </header>
  <main>
    <div class="metrics">
      {metric("Kaynak", len(sources))}
      {metric("Günlük izlenecek", sum(1 for source in sources if "daily" in source.get("freshness_target", "")))}
      {metric("Bağlı/yarı bağlı", sum(1 for source in sources if "connected" in source.get("status", "")))}
      {metric("Yüksek risk", sum(1 for source in sources if source.get("risk") == "high"))}
    </div>
    <section><h2>Politika</h2><ul>{policy_items}</ul></section>
    <section><h2>Günlük Öncelik</h2>{source_table(daily)}</section>
    <section><h2>Tüm Kaynaklar</h2>{source_table(rows)}</section>
  </main>
  <script defer src="/_vercel/insights/script.js"></script>
</body>
</html>
"""


def source_table(rows: str) -> str:
    return (
        "<table><thead><tr><th>Kaynak</th><th>Kategori</th><th>Durum</th><th>Risk</th>"
        "<th>Güncellik</th><th>Ağırlık</th><th>Alanlar</th><th>Kullanım</th></tr></thead>"
        f"<tbody>{rows}</tbody></table>"
    )


def source_row(source: dict) -> str:
    return (
        f"<tr><td><a href=\"{escape(source['url'])}\">{escape(source['name'])}</a></td>"
        f"<td>{escape(source['category'])}</td>"
        f"<td><span class=\"pill status\">{escape(source['status'])}</span></td>"
        f"<td><span class=\"pill {risk_class(source['risk'])}\">{escape(source['risk'])}</span></td>"
        f"<td>{escape(source['freshness_target'])}</td><td>{escape(source['analysis_weight'])}</td>"
        f"<td>{escape(', '.join(source.get('fields', [])[:8]))}</td>"
        f"<td>{escape(', '.join(source.get('use_cases', [])[:5]))}</td></tr>"
    )


def risk_class(risk: str) -> str:
    if risk == "high":
        return "high"
    if risk in {"medium", "low_medium"}:
        return "medium"
    return "low"


def metric(label: str, value) -> str:
    return f'<div class="metric"><span>{escape(str(label))}</span><strong>{escape(str(value))}</strong></div>'


if __name__ == "__main__":
    main()
