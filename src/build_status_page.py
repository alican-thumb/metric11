"""Sistem durumu ve pipeline sağlık sayfası."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path

from src.config import PROCESSED_DIR, SEASON


def main() -> None:
    payload = build_status()
    out = PROCESSED_DIR / "system_status.html"
    out.write_text(build_html(payload), encoding="utf-8")
    print(out)


def build_status() -> dict:
    pipeline = _load(PROCESSED_DIR / "daily_pipeline_run_latest.json") or {}
    news = _load(PROCESSED_DIR / f"news_intelligence_{SEASON}.json") or {}
    league = _load(PROCESSED_DIR / f"tff_super_lig_enriched_{SEASON}.json") or []
    model = _load(PROCESSED_DIR / f"league_prediction_model_{SEASON}.json") or {}
    previews = _load(PROCESSED_DIR / f"previews_besiktas_{SEASON}_chronological" / "index.json") or {}
    data_quality = _load(PROCESSED_DIR / f"data_quality_scorecard_{SEASON}.json") or {}
    source_watchlist = _load(PROCESSED_DIR / f"source_watchlist_{SEASON}.json") or {}

    matches = league if isinstance(league, list) else []
    scored = [m for m in matches if m.get("home_team", {}).get("score") is not None]
    dates = sorted([m.get("match_date", "") for m in scored if m.get("match_date")], reverse=True)
    last_match_date = dates[0] if dates else None

    pipeline_ok = pipeline.get("ok_count", 0)
    pipeline_total = pipeline.get("command_count", 0)
    pipeline_failed = pipeline.get("failed_count", 0)
    pipeline_age_days = _age_days(pipeline.get("generated_at"))
    pipeline_status = "ok" if pipeline_failed == 0 else ("warn" if pipeline_failed <= 3 else "fail")
    if pipeline_age_days is not None and pipeline_age_days > 3:
        pipeline_status = "fail"
    elif pipeline_age_days is not None and pipeline_age_days > 1 and pipeline_status == "ok":
        pipeline_status = "warn"
    source_summary = source_watchlist.get("summary", {})

    return {
        "generated_at": datetime.now(timezone.utc).strftime("%d.%m.%Y %H:%M UTC"),
        "pipeline": {
            "last_run": _fmt_date(pipeline.get("generated_at")),
            "age_days": pipeline_age_days,
            "ok": pipeline_ok,
            "failed": pipeline_failed,
            "total": pipeline_total,
            "status": pipeline_status,
        },
        "data": {
            "matches_total": len(matches),
            "matches_with_score": len(scored),
            "last_match_date": last_match_date,
            "model_predictions": len(model.get("rows", [])),
            "preview_reports": previews.get("summary", {}).get("generated_reports", 0),
            "quality_score": data_quality.get("score", 0),
        },
        "news": {
            "total_articles": news.get("total_articles", 0),
            "analyzed": news.get("analyzed_articles", 0),
            "transfer_signals": news.get("transfer_signals", 0),
            "official_transfers": news.get("transfer_status_counts", {}).get("OFFICIAL", 0),
            "review_transfers": news.get("transfer_status_counts", {}).get("REVIEW_REQUIRED", 0),
            "injury_signals": news.get("injury_signals", 0),
            "last_updated": _fmt_date(news.get("generated_at")),
        },
        "sources": {
            "source_count": source_summary.get("source_count", 0),
            "daily_refresh_count": source_summary.get("daily_refresh_count", 0),
            "connected_or_partial_count": source_summary.get("connected_or_partial_count", 0),
            "high_risk_count": source_summary.get("high_risk_count", 0),
            "updated_at": source_watchlist.get("updated_at") or "—",
        },
    }


def _fmt_date(iso: str | None) -> str:
    if not iso:
        return "—"
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%d.%m.%Y %H:%M UTC")
    except Exception:
        return iso[:16]


def _age_days(iso: str | None) -> int | None:
    if not iso:
        return None
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return max((datetime.now(timezone.utc) - dt.astimezone(timezone.utc)).days, 0)
    except Exception:
        return None


def _load(path: Path):
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _status_dot(status: str) -> str:
    colors = {"ok": "#116447", "warn": "#c98000", "fail": "#bd2936"}
    labels = {"ok": "Sağlıklı", "warn": "Uyarı", "fail": "Hata"}
    c = colors.get(status, "#627067")
    lbl = labels.get(status, status)
    return f'<span style="display:inline-flex;align-items:center;gap:6px;"><span style="width:9px;height:9px;border-radius:50%;background:{c};display:inline-block;"></span>{lbl}</span>'


def build_html(d: dict) -> str:
    p = d["pipeline"]
    data = d["data"]
    news = d["news"]
    sources = d["sources"]

    pipeline_bar_pct = round(p["ok"] / max(p["total"], 1) * 100)
    pipeline_bar_color = "#116447" if p["failed"] == 0 else ("#c98000" if p["failed"] <= 3 else "#bd2936")

    return f"""<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Sistem Durumu — metric11</title>
  <meta name="description" content="Pipeline sağlığı, veri tazeliği ve ziyaretçi analitiği.">
  <meta name="theme-color" content="#091810">
  <link rel="icon" href="favicon.svg" type="image/svg+xml">
  <style>
    :root {{
      --bg:#f3f5f4;--panel:#fff;--ink:#132018;--muted:#627067;--line:#d7ded9;
      --green:#116447;--lime:#cde94e;--dark:#091810;--soft:#e8eee9;--red:#bd2936;
    }}
    *{{box-sizing:border-box;}}
    body{{margin:0;font-family:Inter,"Segoe UI",Arial,sans-serif;background:var(--bg);color:var(--ink);}}
    .topbar{{position:sticky;top:0;z-index:5;display:flex;align-items:center;justify-content:space-between;gap:20px;min-height:64px;padding:0 clamp(16px,4vw,42px);background:var(--dark);color:white;border-bottom:1px solid #203328;}}
    .brand{{display:flex;gap:11px;align-items:center;font-weight:800;font-size:19px;color:white;text-decoration:none;flex-shrink:0;}}
    .brand-mark{{width:30px;height:30px;display:grid;place-items:center;border-radius:7px;color:var(--dark);background:var(--lime);font-size:15px;flex-shrink:0;}}
    .season{{color:#a7b3ab;font-size:12px;font-weight:500;margin-left:4px;}}
    nav{{display:flex;gap:4px;flex-wrap:nowrap;overflow-x:auto;overflow-y:hidden;justify-content:flex-end;-webkit-overflow-scrolling:touch;scrollbar-width:none;}}
    nav::-webkit-scrollbar{{display:none;}}
    nav a{{color:#d5ded8;text-decoration:none;font-size:13px;font-weight:600;padding:9px 10px;border-radius:6px;white-space:nowrap;flex-shrink:0;}}
    nav a:hover,nav a.active{{background:#162b20;color:white;}}
    .wrap{{max-width:1100px;margin:0 auto;padding:32px clamp(14px,3vw,32px) 60px;}}
    h1{{font-size:26px;margin:0 0 4px;}}
    .sub{{color:var(--muted);font-size:13px;margin:0 0 28px;}}
    .grid3{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:24px;}}
    .grid2{{display:grid;grid-template-columns:repeat(2,1fr);gap:16px;margin-bottom:24px;}}
    .card{{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:20px 22px;}}
    .card-title{{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);font-weight:700;margin:0 0 14px;}}
    .big-num{{font-size:36px;font-weight:800;line-height:1;margin:0 0 4px;}}
    .big-label{{font-size:12px;color:var(--muted);}}
    .row{{display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid var(--line);font-size:13px;}}
    .row:last-child{{border-bottom:none;}}
    .row-label{{color:var(--muted);}}
    .row-value{{font-weight:600;}}
    .prog-wrap{{background:var(--soft);border-radius:4px;height:8px;margin:10px 0;overflow:hidden;}}
    .prog-bar{{height:100%;border-radius:4px;transition:width .3s;}}
    .ext-link{{display:inline-flex;align-items:center;gap:7px;padding:10px 16px;border-radius:7px;font-size:13px;font-weight:700;text-decoration:none;border:1px solid var(--line);color:var(--ink);background:var(--panel);}}
    .ext-link:hover{{background:var(--soft);}}
    .ext-links{{display:flex;gap:10px;flex-wrap:wrap;margin-top:24px;}}
    @media(max-width:700px){{.grid3,.grid2{{grid-template-columns:1fr;}}}}
    @media(max-width:680px){{.topbar{{position:static;flex-direction:column;align-items:stretch;padding:11px 16px 0;gap:0;min-height:unset;}}.brand{{padding-bottom:8px;}}.season{{display:none;}}nav{{justify-content:flex-start;border-top:1px solid #1e3228;padding:7px 0 9px;}}}}
  </style>
</head>
<body>
  <div class="topbar">
    <a class="brand" href="football_intelligence_home.html"><span class="brand-mark">11</span> metric11 <span class="season">Süper Lig 2025/26</span></a>
    <nav>
      <a href="football_intelligence_home.html">Merkez</a>
      <a href="football_command_center_2025_2026.html">Analiz</a>
      <a href="besiktas_2025_2026_dashboard_chronological.html">Maç Önü</a>
      <a href="transfer_recommendation_report_2025_2026.html">Scout</a>
      <a href="all_teams_preview_dashboard_2025_2026.html">Lig</a>

    </nav>
  </div>

  <div class="wrap">
    <h1>Sistem Durumu</h1>
    <p class="sub">Son güncelleme: {escape(d["generated_at"])}</p>

    <div class="grid3">
      <div class="card">
        <div class="card-title">Pipeline</div>
        <div class="big-num">{p["ok"]}<span style="font-size:16px;color:var(--muted);">/{p["total"]}</span></div>
        <div class="big-label">başarılı komut</div>
        <div class="prog-wrap"><div class="prog-bar" style="width:{pipeline_bar_pct}%;background:{pipeline_bar_color};"></div></div>
        <div class="row"><span class="row-label">Durum</span><span class="row-value">{_status_dot(p["status"])}</span></div>
        <div class="row"><span class="row-label">Son çalışma</span><span class="row-value">{escape(p["last_run"])}</span></div>
        <div class="row"><span class="row-label">Tazelik</span><span class="row-value">{escape(_freshness_label(p["age_days"]))}</span></div>
        <div class="row"><span class="row-label">Hata</span><span class="row-value" style="color:{'var(--red)' if p['failed'] > 0 else 'inherit'}">{p["failed"]} komut</span></div>
      </div>

      <div class="card">
        <div class="card-title">Veri</div>
        <div class="big-num">{data["matches_total"]}</div>
        <div class="big-label">toplam maç</div>
        <div style="height:10px;"></div>
        <div class="row"><span class="row-label">Skorlu maç</span><span class="row-value">{data["matches_with_score"]}</span></div>
        <div class="row"><span class="row-label">Son maç tarihi</span><span class="row-value">{escape(data["last_match_date"] or "—")}</span></div>
        <div class="row"><span class="row-label">Tahmin kaydı</span><span class="row-value">{data["model_predictions"]}</span></div>
        <div class="row"><span class="row-label">Maç önü raporu</span><span class="row-value">{data["preview_reports"]}</span></div>
        <div class="row"><span class="row-label">Veri kalite skoru</span><span class="row-value">{data["quality_score"]}/100</span></div>
      </div>

      <div class="card">
        <div class="card-title">Haber ve Sinyaller</div>
        <div class="big-num">{news["total_articles"]}</div>
        <div class="big-label">makale</div>
        <div style="height:10px;"></div>
        <div class="row"><span class="row-label">Analiz edilen</span><span class="row-value">{news["analyzed"]}</span></div>
        <div class="row"><span class="row-label">Transfer iddiası</span><span class="row-value">{news["transfer_signals"]}</span></div>
        <div class="row"><span class="row-label">Resmi / inceleme gerekli</span><span class="row-value">{news["official_transfers"]} / {news["review_transfers"]}</span></div>
        <div class="row"><span class="row-label">Sakatlık sinyali</span><span class="row-value">{news["injury_signals"]}</span></div>
        <div class="row"><span class="row-label">Son güncelleme</span><span class="row-value">{escape(news["last_updated"])}</span></div>
      </div>
    </div>

    <div class="grid2">
      <div class="card">
        <div class="card-title">Kaynak Radarı</div>
        <div class="big-num">{sources["daily_refresh_count"]}<span style="font-size:16px;color:var(--muted);">/{sources["source_count"]}</span></div>
        <div class="big-label">günlük izlenen kaynak</div>
        <div style="height:10px;"></div>
        <div class="row"><span class="row-label">Bağlı/yarı bağlı</span><span class="row-value">{sources["connected_or_partial_count"]}</span></div>
        <div class="row"><span class="row-label">Yüksek risk</span><span class="row-value">{sources["high_risk_count"]}</span></div>
        <div class="row"><span class="row-label">Liste güncelleme</span><span class="row-value">{escape(str(sources["updated_at"]))}</span></div>
      </div>
      <div class="card">
        <div class="card-title">Ziyaretçi Analitiği</div>
        <p style="font-size:13px;color:var(--muted);margin:0 0 14px;">Vercel Analytics ile sayfa görüntüleme, benzersiz ziyaretçi, en çok ziyaret edilen sayfalar ve coğrafi dağılım takibi.</p>
        <a class="ext-link" href="https://vercel.com/alicans-projects-02042cb7/metric11/analytics" target="_blank">
          Vercel Analytics'i Aç →
        </a>
      </div>
    </div>

    <div class="grid2">
      <div class="card">
        <div class="card-title">Pipeline Günlükleri</div>
        <p style="font-size:13px;color:var(--muted);margin:0 0 14px;">GitHub Actions'ta her pipeline çalışmasının detaylı logları, hata mesajları ve geçmiş çalıştırmalar.</p>
        <a class="ext-link" href="https://github.com/alican-thumb/metric11/actions" target="_blank">
          GitHub Actions'ı Aç →
        </a>
      </div>
    </div>

    <div class="ext-links">
      <a class="ext-link" href="football_intelligence_home.html">← Ana Sayfaya Dön</a>
      <a class="ext-link" href="data_quality_scorecard_2025_2026.html">Veri Kalite Detayı</a>
      <a class="ext-link" href="prediction_validation_report_2025_2026.html">Tahmin Doğrulama</a>
    </div>
  </div>
  <script defer src="/_vercel/insights/script.js"></script>
</body>
</html>"""


def _freshness_label(age_days: int | None) -> str:
    if age_days is None:
        return "bilinmiyor"
    if age_days == 0:
        return "bugün"
    return f"{age_days} gün önce"


if __name__ == "__main__":
    main()
