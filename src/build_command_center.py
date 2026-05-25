from __future__ import annotations

import argparse
import json
from html import escape
from pathlib import Path

from src.config import PROCESSED_DIR


def main() -> None:
    parser = argparse.ArgumentParser(description="Tahmin, scout, ihtiyaç ve veri durumunu tek komuta merkezinde toplar.")
    parser.add_argument("--output", default=str(PROCESSED_DIR / "football_command_center_2025_2026.html"))
    args = parser.parse_args()

    payload = build_payload()
    output = Path(args.output)
    output.write_text(build_html(payload), encoding="utf-8")
    print(output)


def build_payload() -> dict:
    preview_index = load_json(PROCESSED_DIR / "previews_besiktas_2025_2026_chronological" / "index.json")
    match_backtest = load_json(PROCESSED_DIR / "match_prediction_backtest_2025_2026.json")
    goal_backtest = load_json(PROCESSED_DIR / "goal_candidate_backtest_2025_2026.json")
    league_model = load_json(PROCESSED_DIR / "league_prediction_model_2025_2026.json")
    league_market_audit = load_json(PROCESSED_DIR / "league_market_value_audit_2025_2026.json")
    fm_scout = load_json(PROCESSED_DIR / "fm_style_scout_program_2025_2026.json")
    position_matrix = load_json(PROCESSED_DIR / "position_scout_matrix_2025_2026.json")
    team_needs = load_json(PROCESSED_DIR / "besiktas_team_needs_2025_2026.json")
    availability = load_json(PROCESSED_DIR / "player_availability_besiktas_2025_2026.json")
    data_catalog = load_json(PROCESSED_DIR / "data_catalog_2025_2026.json")
    big_match_report = load_json(PROCESSED_DIR / "big_match_report_2025_2026.json")
    league_intelligence = load_json(PROCESSED_DIR / "league_intelligence_2025_2026.json")
    team_blueprints = load_json(PROCESSED_DIR / "team_scout_blueprints_2025_2026.json")
    scout_quality = load_json(PROCESSED_DIR / "scout_quality_report_2025_2026.json")
    transfermarkt_review = load_json(PROCESSED_DIR / "transfermarkt_match_review_queue_2025_2026.json")
    data_quality = load_json(PROCESSED_DIR / "data_quality_scorecard_2025_2026.json")
    warehouse_quality = load_json(PROCESSED_DIR / "metric11_warehouse_quality.json")
    draw_risk = load_json(PROCESSED_DIR / "draw_risk_audit_2025_2026.json")
    protected_action = load_json(PROCESSED_DIR / "protected_action_audit_2025_2026.json")
    side_flip = load_json(PROCESSED_DIR / "side_flip_audit_2025_2026.json")
    segment_backtest = load_json(PROCESSED_DIR / "goal_candidate_segment_backtest_2025_2026.json")

    preview_reports = []
    for report in preview_index.get("reports", [])[-8:]:
        preview_reports.append(load_json(Path(report["json_path"])))

    league_rows = league_model.get("rows", [])
    wrong_high = [row for row in league_rows if row.get("confidence") == "HIGH" and not row.get("correct")][-8:]
    draw_rows = draw_risk.get("rows", [])
    protected_draw_rows = [
        row for row in draw_rows
        if row.get("recommended_model_action") != "KEEP_MAIN_PICK"
    ][-8:]
    missed_draw_rows = draw_risk.get("missed_draws", [])[-8:]
    protected_previews = [
        item for item in preview_reports
        if item.get("probabilities", {}).get("draw_risk", {}).get("protected_prediction")
    ][-8:]

    return {
        "preview_summary": preview_index.get("summary", {}),
        "match_backtest_summary": match_backtest.get("summary", {}),
        "recent_previews": preview_reports,
        "goal_summary": goal_backtest.get("summary", {}),
        "league_summary": league_model.get("summary", {}),
        "league_market_summary": league_market_audit.get("summary", {}),
        "wrong_high": wrong_high,
        "protected_draw_rows": protected_draw_rows,
        "missed_draw_rows": missed_draw_rows,
        "protected_previews": protected_previews,
        "draw_risk_summary": draw_risk.get("summary", {}),
        "protected_action_summary": protected_action.get("summary", {}),
        "protected_action_rows": protected_action.get("protected_rows", [])[-8:],
        "side_flip_summary": side_flip.get("summary", {}),
        "side_flip_rows": side_flip.get("rows", [])[-8:],
        "segment_backtest": segment_backtest,
        "fm_scout": fm_scout,
        "position_matrix": position_matrix,
        "team_needs": team_needs,
        "availability": availability,
        "data_coverage": data_catalog.get("coverage", {}),
        "big_match_summary": big_match_report.get("summary", {}),
        "big_match_rows": big_match_report.get("rows", []),
        "league_intelligence_summary": league_intelligence.get("summary", {}),
        "team_blueprint_summary": team_blueprints.get("summary", {}),
        "scout_quality_summary": scout_quality.get("summary", {}),
        "transfermarkt_review_summary": transfermarkt_review.get("summary", {}),
        "data_quality": data_quality,
        "warehouse_quality": warehouse_quality,
    }


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def signal_label(value: str | None) -> str:
    return {
        "HIGH": "Yüksek",
        "MEDIUM": "Orta",
        "LOW": "Düşük",
        "VERY_LOW": "Çok düşük",
        "EMPTY": "Belirsiz",
    }.get(value or "", value or "-")


def build_html(payload: dict) -> str:
    league = payload["league_summary"]
    league_market = payload["league_market_summary"]
    goal = payload["goal_summary"]
    preview = payload["preview_summary"]
    match_backtest_summary = payload["match_backtest_summary"]
    fm_summary = payload["fm_scout"].get("summary", {})
    position_summary = payload["position_matrix"].get("summary", {})
    team_summary = payload["team_needs"].get("summary", {})
    availability_summary = payload["availability"].get("summary", {})
    big_match_summary = payload["big_match_summary"]
    league_intelligence_summary = payload["league_intelligence_summary"]
    team_blueprint_summary = payload["team_blueprint_summary"]
    scout_quality_summary = payload["scout_quality_summary"]
    transfermarkt_review_summary = payload["transfermarkt_review_summary"]
    data_quality = payload["data_quality"]
    warehouse_quality = payload["warehouse_quality"]
    draw_risk_summary = payload["draw_risk_summary"]
    protected_action_summary = payload["protected_action_summary"]
    side_flip_summary = payload["side_flip_summary"]
    segment_backtest = payload["segment_backtest"]
    segment_summary = segment_backtest.get("summary", {})
    rank_buckets = segment_summary.get("rank_buckets", {})

    recent_previews = "".join(preview_row(item) for item in payload["recent_previews"])
    protected_preview_rows = "".join(protected_preview_row(item) for item in payload["protected_previews"])
    needs = "".join(
        f"<tr><td><span class=\"pill {priority_class(item['priority'])}\">{escape(item['priority'])}</span></td>"
        f"<td>{escape(item['need'])}</td><td>{escape(item['reason'])}</td></tr>"
        for item in payload["team_needs"].get("needs", [])[:6]
    )
    scorer_rows = candidate_rows(payload["fm_scout"].get("role_buckets", {}).get("immediate_scorer", [])[:6])
    engine_rows = candidate_rows(payload["fm_scout"].get("role_buckets", {}).get("physical_engine", [])[:6])
    resale_rows = candidate_rows(payload["fm_scout"].get("role_buckets", {}).get("resale_value", [])[:6])
    position_rows = position_candidate_rows(payload["position_matrix"].get("roles", [])[:4])
    wrong_rows = "".join(model_row(row) for row in payload["wrong_high"])
    protected_draw_rows = "".join(draw_risk_row(row) for row in payload["protected_draw_rows"])
    missed_draw_rows = "".join(draw_risk_row(row) for row in payload["missed_draw_rows"])
    protected_action_rows = "".join(protected_action_row(row) for row in payload["protected_action_rows"])
    side_flip_rows = "".join(side_flip_row(row) for row in payload["side_flip_rows"])
    segment_rows = "".join(segment_row(row) for row in segment_backtest.get("segments", []))
    weak_goal_rows = "".join(weak_goal_candidate_row(row) for row in segment_backtest.get("weak_candidates", [])[:8])

    return f"""<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Analiz Merkezi — metric11</title>
  <meta name="description" content="Tahmin performansı, maç önü arşivi, gol adayları ve scout kararları tek ekranda.">
  <meta property="og:title" content="Analiz Merkezi — metric11">
  <meta property="og:image" content="/og-image.svg">
  <meta name="theme-color" content="#091810">
  <link rel="icon" href="favicon.svg" type="image/svg+xml">
  <style>
    :root {{ --bg:#f3f5f4; --panel:#fff; --ink:#132018; --muted:#627067; --line:#d7ded9; --dark:#091810; --red:#bd2936; --amber:#b76b00; --green:#116447; --lime:#cde94e; --blue:#22618c; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; font-family:Inter, "Segoe UI", Arial, sans-serif; background:var(--bg); color:var(--ink); }}
    .topbar {{ position:sticky; top:0; z-index:5; min-height:62px; padding:0 clamp(14px,3vw,32px); display:flex; align-items:center; justify-content:space-between; gap:18px; background:var(--dark); color:white; border-bottom:1px solid #203328; }}
    .brand {{ display:flex; align-items:center; gap:10px; color:white; text-decoration:none; font-weight:800; font-size:18px; }}
    .brand b {{ display:grid; place-items:center; width:29px; height:29px; border-radius:7px; background:var(--lime); color:var(--dark); font-size:14px; }}
    .topnav {{ display:flex; gap:5px; overflow-x:auto; }}
    .topnav a {{ white-space:nowrap; color:#d5ded8; padding:10px 11px; border-radius:6px; text-decoration:none; font-size:13px; font-weight:600; }}
    .topnav a.active {{ background:#162b20; color:white; }}
    header {{ background:#102419; color:white; padding:25px clamp(14px,3vw,32px); border-bottom:3px solid var(--green); }}
    header > div {{ max-width:1420px; margin:0 auto; }}
    header h1 {{ margin:0 0 7px; font-size:35px; letter-spacing:0; }}
    header p {{ margin:0; color:#c1cec5; max-width:1100px; line-height:1.5; font-size:14px; }}
    main {{ max-width:1420px; margin:0 auto; padding:20px clamp(12px,2.5vw,24px) 40px; }}
    .metrics {{ display:grid; grid-template-columns:repeat(8,minmax(0,1fr)); gap:10px; margin-bottom:18px; }}
    .metric, section, details {{ background:var(--panel); border:1px solid var(--line); border-radius:8px; }}
    .metric {{ padding:13px 12px; min-height:76px; }}
    .metric span {{ display:block; color:var(--muted); font-size:11px; line-height:1.3; }}
    .metric strong {{ display:block; font-size:22px; margin-top:7px; }}
    .grid {{ display:grid; grid-template-columns:1fr 1fr; gap:18px; }}
    section {{ padding:17px; margin-bottom:16px; overflow-x:auto; }}
    h2 {{ margin:0 0 14px; font-size:17px; }}
    table {{ width:100%; border-collapse:collapse; font-size:13px; }}
    .wide table {{ min-width:970px; }}
    th,td {{ padding:9px 7px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; }}
    th {{ color:var(--muted); font-size:12px; }}
    .pill {{ display:inline-flex; min-height:23px; align-items:center; border-radius:999px; padding:0 8px; font-size:12px; border:1px solid var(--line); }}
    .high {{ color:var(--red); background:#fff0f2; border-color:#efb7bf; }}
    .medium {{ color:var(--amber); background:#fff7e8; border-color:#f2d09a; }}
    .low {{ color:var(--green); background:#edf9f3; border-color:#b9dfcd; }}
    .role {{ color:var(--blue); background:#edf5ff; border-color:#bbd7f5; }}
    .links {{ display:flex; gap:7px; overflow-x:auto; margin-bottom:18px; padding-bottom:4px; }}
    .links a {{ display:inline-flex; align-items:center; min-height:36px; padding:0 12px; border:1px solid var(--line); border-radius:6px; color:var(--ink); background:white; white-space:nowrap; text-decoration:none; font-size:13px; font-weight:600; }}
    details {{ margin-bottom:18px; overflow:hidden; }}
    summary {{ cursor:pointer; padding:13px 15px; font-size:14px; font-weight:700; list-style:none; }}
    summary::-webkit-details-marker {{ display:none; }}
    .metrics.more {{ padding:0 12px 12px; margin:0; }}
    @media (max-width:1100px) {{ .metrics {{ grid-template-columns:repeat(4,1fr); }} .grid {{ grid-template-columns:1fr; }} }}
    @media (max-width:680px) {{ .topbar {{ position:static; flex-direction:column; align-items:flex-start; padding:12px; }} .topnav {{ width:100%; }} header h1 {{ font-size:27px; }} .metrics {{ grid-template-columns:repeat(2,minmax(0,1fr)); }} main {{ padding:12px; }} header {{ padding:20px 14px; }} table {{ font-size:12px; }} section {{ padding:13px; }} }}
  </style>
</head>
<body>
  <div class="topbar">
    <a class="brand" href="football_intelligence_home.html"><b>11</b> metric11</a>
    <nav class="topnav">
      <a href="football_intelligence_home.html">Merkez</a>
      <a class="active" href="football_command_center_2025_2026.html">Analiz</a>
      <a href="besiktas_2025_2026_dashboard_chronological.html">Maç Önü</a>
      <a href="transfer_recommendation_report_2025_2026.html">Scout</a>
      <a href="all_teams_preview_dashboard_2025_2026.html">Lig</a>
      <a href="system_status.html">Durum</a>
    </nav>
  </div>
  <header>
    <div><h1>Analiz merkezi</h1>
    <p>Beşiktaş maç önü raporları, tahmin kontrolü, gol adayı performansı ve scout kararlarını aynı operasyon yüzünde incele.</p></div>
  </header>
  <main>
    <div class="links">
      <a href="besiktas_2025_2026_dashboard_chronological.html">Maç Önü Paneli</a>
      <a href="prediction_backtest_dashboard_2025_2026.html">Tahmin Backtest</a>
      <a href="all_teams_preview_dashboard_2025_2026.html">Tüm Takım Maç Önü</a>
      <a href="league_market_value_audit_2025_2026.html">Lig Değer Audit</a>
      <a href="prediction_validation_report_2025_2026.html">Tahmin Doğrulama</a>
      <a href="oos_validation_2025_2026.html">OOS Validasyon</a>
      <a href="big_match_report_2025_2026.html">Büyük Maç Raporu</a>
      <a href="fm_style_scout_program_2025_2026.html">FM Scout</a>
      <a href="league_intelligence_2025_2026.html">Lig İstihbaratı</a>
      <a href="team_scout_blueprints_2025_2026.html">Takım Blueprint</a>
      <a href="transfer_recommendation_report_2025_2026.html">Transfer Raporu</a>
      <a href="transfer_season_context_2025_2026.html">Transfer Sezonu</a>
      <a href="news_intelligence_dashboard_2025_2026.html">Haber İstihbaratı</a>
      <a href="scout_quality_report_2025_2026.html">Scout Kalite</a>
      <a href="transfermarkt_match_review_queue_2025_2026.html">TM Eşleşme Kuyruğu</a>
      <a href="metric11_warehouse_quality.html">Veri Ambarı</a>
      <a href="data_quality_scorecard_2025_2026.html">Kalite Skoru</a>
      <a href="position_scout_matrix_2025_2026.html">Pozisyon Scout</a>
      <a href="api_football_super_lig_deep_2024_analysis.html">Dış Derin Veri</a>
      <a href="source_watchlist_2025_2026.html">Kaynak Radarı</a>
      <a href="player_alias_quality_2025_2026.html">Alias Kalitesi</a>
      <a href="besiktas_team_needs_2025_2026_dashboard.html">Takım İhtiyacı</a>
      <a href="data_catalog_2025_2026.html">Veri Kataloğu</a>
    </div>
    <div class="metrics">
      {metric("Maç önü raporu", preview.get("generated_reports", 0))}
      {metric("BJK ekran kontrolü", f"%{round(match_backtest_summary.get('accuracy', 0) * 100)}")}
      {metric("Lig ham ölçümü", f"%{round(league.get('accuracy', 0) * 100)}")}
      {metric("Lig değer kapsamı", f"{league_market.get('covered_matches', 0)} / {league_market.get('league_model_matches', 0)}")}
      {metric("Büyük maç uyarısı", big_match_summary.get("high_or_medium_risk_count", 0))}
      {metric("Golcü listesi isabeti", f"%{round(goal.get('top_5_hit_rate', 0) * 100)}")}
      {metric("Scout kontrol kuyruğu", scout_quality_summary.get("low_confidence_blueprint_links", 0))}
      {metric("Veri kalite skoru", data_quality.get("score", 0))}
    </div>
    <details>
      <summary>Ek model ve veri ölçümlerini göster</summary>
      <div class="metrics more">
      {metric("Ham tahmine göre artış", f"+{round((match_backtest_summary.get('accuracy', 0) - match_backtest_summary.get('raw_accuracy', 0)) * 100)} puan")}
      {metric("Değer tabanı", f"%{round(league_market.get('reporting_baseline_accuracy', 0) * 100)}")}
      {metric("Emin olunan maçlar", f"%{round(league.get('confidence_breakdown', {}).get('HIGH', {}).get('accuracy', 0) * 100)}")}
      {metric("FM scout adayı", fm_summary.get("candidate_count", 0))}
      {metric("Lig oyuncu profili", league_intelligence_summary.get("players", 0))}
      {metric("Takım-oyuncu eşleşmesi", team_blueprint_summary.get("candidate_links", 0))}
      {metric("TM lig içi eşleşme", f"%{round(transfermarkt_review_summary.get('in_scope_match_rate', 0) * 100, 1)}")}
      {metric("TM yüksek kullanım açığı", transfermarkt_review_summary.get("review_tier_counts", {}).get("HIGH_USAGE_UNRESOLVED", 0))}
      {metric("Scout bloke eden eşleşme", transfermarkt_review_summary.get("scout_blocking_unmatched", 0))}
      {metric("Beraberlik uyarısı", draw_risk_summary.get("medium_plus_flags", 0))}
      {metric("Beraberlik yakalama", f"%{round(draw_risk_summary.get('medium_plus_recall', 0) * 100)}")}
      {metric("Uyarı isabeti", f"%{round(draw_risk_summary.get('medium_plus_precision', 0) * 100)}")}
      {metric("BJK temkinli tahmin", protected_action_summary.get("protected_count", 0))}
      {metric("BJK beraberlik uyarısı", f"%{round(protected_action_summary.get('protected_draw_precision', 0) * 100)}")}
      {metric("Ters taraf hatası", side_flip_summary.get("side_flip_count", 0))}
      {metric("Rakip değer kapsama", f"{side_flip_summary.get('opponent_market_value_covered', 0)} / {side_flip_summary.get('side_flip_count', 0)}")}
      {metric("Odds/veri boşluğu", side_flip_summary.get("missing_data_gap_counts", {}).get("odds_baseline_missing", 0))}
      {metric("Kaçan beraberlik", draw_risk_summary.get("missed_draws_after_risk", 0))}
      {metric("Golcü segment isabeti", f"%{round(rank_buckets.get('top_5', {}).get('match_hit_rate', 0) * 100)}")}
      {metric("Ambar satırı", sum(warehouse_quality.get("table_counts", {}).values()))}
      {metric("Pozisyon rolü", position_summary.get("roles", 0))}
      </div>
    </details>
    <section class="wide">
      <h2>Son Beşiktaş Maç Önü Raporları</h2>
      <table><thead><tr><th>Maç</th><th>Tarih</th><th>Kazanma Olasılığı</th><th>Ekran Tahmini</th><th>Skor</th><th>Gol Beklentisi</th><th>Kart</th><th>Eksik</th><th>Gol Adayı İlk 3</th></tr></thead><tbody>{recent_previews}</tbody></table>
    </section>
    <div class="grid">
      <section><h2>Takım İhtiyaçları</h2><table><thead><tr><th>Öncelik</th><th>İhtiyaç</th><th>Gerekçe</th></tr></thead><tbody>{needs}</tbody></table></section>
      <section><h2>Kadro Gerçekliği</h2><table><tbody>
        <tr><th>Oyuncu profili</th><td>{team_summary.get("players", 0)}</td></tr>
        <tr><th>Transfermarkt eşleşme</th><td>{team_summary.get("transfermarkt_matched_players", 0)}</td></tr>
        <tr><th>Ortalama yaş</th><td>{team_summary.get("avg_age")}</td></tr>
        <tr><th>13 ayda bitecek sözleşme</th><td>{team_summary.get("contract_expiring_13_months")}</td></tr>
        <tr><th>Toplam piyasa değeri</th><td>€{team_summary.get("market_value_total_eur", 0):,}</td></tr>
      </tbody></table></section>
    </div>
    <div class="grid">
      <section><h2>FM Scout: Hemen Skor Katkısı</h2>{candidate_table(scorer_rows)}</section>
      <section><h2>FM Scout: Fizik Motoru</h2>{candidate_table(engine_rows)}</section>
      <section><h2>FM Scout: Genç / Resale</h2>{candidate_table(resale_rows)}</section>
      <section><h2>Pozisyon Bazlı Scout İlk Sinyaller</h2><table><thead><tr><th>Rol</th><th>Aday</th><th>Fit</th><th>Güven</th><th>Neden</th></tr></thead><tbody>{position_rows}</tbody></table></section>
    </div>
    <section><h2>Modelin Öğrenmesi Gerekenler</h2><table><thead><tr><th>Maç</th><th>Skor</th><th>Tahmin</th><th>Gerçek</th><th>Güven</th></tr></thead><tbody>{wrong_rows}</tbody></table></section>
    <section><h2>Beraberlik Risk Katmanı</h2><table><thead><tr><th>Maç</th><th>Skor</th><th>Tahmin</th><th>Gerçek</th><th>Risk</th><th>Aksiyon</th></tr></thead><tbody>{protected_draw_rows}</tbody></table></section>
    <section><h2>Kaçan Beraberlikler</h2><table><thead><tr><th>Maç</th><th>Skor</th><th>Tahmin</th><th>Gerçek</th><th>Risk</th><th>Aksiyon</th></tr></thead><tbody>{missed_draw_rows}</tbody></table></section>
    <section><h2>Beşiktaş Korumalı Aksiyon Backtesti</h2><table><thead><tr><th>Maç</th><th>Skor</th><th>Tahmin</th><th>Gerçek</th><th>Risk</th><th>Aksiyon</th></tr></thead><tbody>{protected_action_rows}</tbody></table></section>
    <section><h2>Yanlış Taraf Denetimi</h2><table><thead><tr><th>Maç</th><th>Skor</th><th>Tahmin</th><th>Gerçek</th><th>xG Edge</th><th>Market Edge</th><th>Veri Boşluğu</th></tr></thead><tbody>{side_flip_rows}</tbody></table></section>
    <section><h2>Korumalı Beşiktaş Tahminleri</h2><table><thead><tr><th>Maç</th><th>Tarih</th><th>Ana Tahmin</th><th>Risk</th><th>Aksiyon</th><th>Skor</th></tr></thead><tbody>{protected_preview_rows}</tbody></table></section>
    <div class="grid">
      <section><h2>Gol Adayı Segmentleri</h2><table><thead><tr><th>Segment</th><th>Aday</th><th>Maç Hit</th><th>Top 5 Hit</th><th>Ortalama Rank</th></tr></thead><tbody>{segment_rows}</tbody></table></section>
      <section><h2>Zayıf Gol Adayı Kuyruğu</h2><table><thead><tr><th>Oyuncu</th><th>Tip</th><th>Top 5</th><th>İsabet</th><th>Aksiyon</th></tr></thead><tbody>{weak_goal_rows}</tbody></table></section>
    </div>
  </main>
  <script defer src="/_vercel/insights/script.js"></script>
</body>
</html>
"""


def metric(label: str, value) -> str:
    return f'<div class="metric"><span>{escape(str(label))}</span><strong>{escape(str(value))}</strong></div>'


def preview_row(preview: dict) -> str:
    match = preview.get("match", {})
    prob = preview.get("probabilities", {})
    goals = preview.get("goal_candidates", {}).get("candidates", [])[:3]
    goal_names = ", ".join(player.get("name", "") for player in goals)
    fixture = f"{match.get('home_team')} - {match.get('away_team')}"
    probability = (
        f"BJK %{round(prob.get('target_win_probability', 0) * 100)} / "
        f"X %{round(prob.get('draw_probability', 0) * 100)} / "
        f"Rakip %{round(prob.get('opponent_win_probability', 0) * 100)}"
    )
    xg = f"{prob.get('expected_goals_for')} - {prob.get('expected_goals_against')}"
    scoreline = (prob.get("recommended_scoreline") or {}).get("score") or "-"
    display_prediction = (prob.get("display_prediction") or {}).get("label") or "-"
    missing = prob.get("availability_missing_count", 0)
    return (
        f"<tr><td>{escape(fixture)}</td><td>{escape(match.get('date', ''))}</td><td>{escape(probability)}</td>"
        f"<td>{escape(display_prediction)}</td><td>{escape(scoreline)}</td><td>{escape(xg)}</td><td><span class=\"pill {priority_class(str(prob.get('card_signal', 'LOW')))}\">{escape(signal_label(str(prob.get('card_signal', ''))))}</span></td>"
        f"<td>{missing}</td><td>{escape(goal_names)}</td></tr>"
    )


def protected_preview_row(preview: dict) -> str:
    match = preview.get("match", {})
    prob = preview.get("probabilities", {})
    call = prob.get("recommended_call", {})
    draw_risk = prob.get("draw_risk", {})
    fixture = f"{match.get('home_team')} - {match.get('away_team')}"
    labels = {
        "target_win": "Beşiktaş",
        "draw": "Beraberlik",
        "opponent_win": "Rakip",
    }
    action = call.get("action_label") or action_label(draw_risk.get("recommended_model_action"))
    scoreline = (prob.get("recommended_scoreline") or {}).get("score") or "-"
    return (
        f"<tr><td>{escape(fixture)}</td><td>{escape(match.get('date', ''))}</td>"
        f"<td>{escape(labels.get(call.get('result'), call.get('result', '')))}</td>"
        f"<td><span class=\"pill {priority_class(draw_risk.get('risk_level', 'LOW'))}\">{escape(signal_label(draw_risk.get('risk_level', 'LOW')))} / {draw_risk.get('score', 0)}</span></td>"
        f"<td>{escape(action)}</td><td>{escape(scoreline)}</td></tr>"
    )


def candidate_table(rows: str) -> str:
    return (
        "<table><thead><tr><th>Oyuncu</th><th>Rol</th><th>Fit</th><th>Yaş</th><th>Gol</th><th>Yük</th></tr></thead>"
        f"<tbody>{rows}</tbody></table>"
    )


def candidate_rows(players: list[dict]) -> str:
    return "".join(
        f"<tr><td>{escape(player['name'])}<br><span class=\"muted\">{escape(player.get('team') or '')}</span></td>"
        f"<td><span class=\"pill role\">{escape(player['archetype'])}</span></td><td>{player['overall_fm_fit_score']}</td>"
        f"<td>{escape(str(player.get('age') or ''))}</td><td>{player['goals']}</td>"
        f"<td>{player['estimated_physical_load_km_min']}-{player['estimated_physical_load_km_max']}</td></tr>"
        for player in players
    )


def position_candidate_rows(roles: list[dict]) -> str:
    rows = []
    for role in roles:
        for candidate in role.get("top_candidates", [])[:2]:
            rows.append(
                f"<tr><td>{escape(role.get('label', ''))}</td>"
                f"<td>{escape(candidate.get('name', ''))}<br><span class=\"muted\">{escape(candidate.get('team') or '')}</span></td>"
                f"<td>{candidate.get('role_fit_score', 0)}</td>"
                f"<td><span class=\"pill role\">{escape(signal_label(candidate.get('position_confidence', '')))}</span></td>"
                f"<td>{escape(candidate.get('why_fit', '')[:180])}</td></tr>"
            )
    return "".join(rows)


def model_row(row: dict) -> str:
    labels = {"home": "Ev", "draw": "X", "away": "Dep"}
    match = f"{row.get('home')} - {row.get('away')}"
    return (
        f"<tr><td>{escape(match)}</td><td>{escape(row.get('score', ''))}</td>"
        f"<td>{labels.get(row.get('predicted'), '')}</td><td>{labels.get(row.get('actual'), '')}</td>"
        f"<td><span class=\"pill {priority_class(row.get('confidence', 'LOW'))}\">{escape(signal_label(row.get('confidence', '')))}</span></td></tr>"
    )


def draw_risk_row(row: dict) -> str:
    labels = {"home": "Ev", "draw": "X", "away": "Dep"}
    match = f"{row.get('home')} - {row.get('away')}"
    return (
        f"<tr><td>{escape(match)}</td><td>{escape(row.get('score', ''))}</td>"
        f"<td>{labels.get(row.get('predicted'), '')}</td><td>{labels.get(row.get('actual'), '')}</td>"
        f"<td><span class=\"pill {priority_class(row.get('draw_risk_level', 'LOW'))}\">{escape(signal_label(row.get('draw_risk_level', 'LOW')))} / {row.get('draw_risk_score', 0)}</span></td>"
        f"<td>{escape(action_label(row.get('recommended_model_action')))}</td></tr>"
    )


def protected_action_row(row: dict) -> str:
    labels = {"target_win": "BJK", "draw": "X", "opponent_win": "Rakip"}
    return (
        f"<tr><td>{escape(row.get('fixture', ''))}</td><td>{escape(row.get('actual_score', ''))}</td>"
        f"<td>{labels.get(row.get('predicted'), '')}</td><td>{labels.get(row.get('actual'), '')}</td>"
        f"<td><span class=\"pill {priority_class(row.get('draw_risk_level', 'LOW'))}\">{escape(signal_label(row.get('draw_risk_level')))} / {row.get('draw_risk_score') or '-'}</span></td>"
        f"<td>{escape(row.get('action_label', ''))}</td></tr>"
    )


def side_flip_row(row: dict) -> str:
    labels = {"target_win": "BJK", "draw": "X", "opponent_win": "Rakip"}
    gaps = ", ".join(row.get("data_gaps", [])[:3]) or "-"
    market_edge = row.get("market_value_edge_million_eur")
    market_edge_text = f"€{market_edge}m" if market_edge is not None else "-"
    return (
        f"<tr><td>{escape(row.get('fixture', ''))}</td><td>{escape(row.get('actual_score', ''))}</td>"
        f"<td>{labels.get(row.get('predicted'), '')}</td><td>{labels.get(row.get('actual'), '')}</td>"
        f"<td>{row.get('xg_edge')}</td><td>{escape(market_edge_text)}</td><td>{escape(gaps)}</td></tr>"
    )


def segment_row(row: dict) -> str:
    return (
        f"<tr><td><span class=\"pill role\">{escape(row.get('segment', ''))}</span></td>"
        f"<td>{row.get('candidate_rows', 0)}</td>"
        f"<td>%{round(row.get('match_hit_rate', 0) * 100, 1)}</td>"
        f"<td>%{round(row.get('top5_match_hit_rate', 0) * 100, 1)}</td>"
        f"<td>{row.get('avg_rank', 0)}</td></tr>"
    )


def weak_goal_candidate_row(row: dict) -> str:
    return (
        f"<tr><td>{escape(row.get('player_name', ''))}</td>"
        f"<td><span class=\"pill role\">{escape(row.get('candidate_type', ''))}</span></td>"
        f"<td>{row.get('top5_rows', 0)}</td><td>{row.get('hits', 0)}</td>"
        f"<td>{escape(row.get('recommendation', ''))}</td></tr>"
    )


def action_label(action: str | None) -> str:
    labels = {
        "PROTECT_SIDE_PICK_SHOW_DRAW_SCENARIO": "Korumalı taraf tahmini",
        "KEEP_PICK_WITH_DRAW_WARNING": "Beraberlik uyarılı tahmin",
        "KEEP_MAIN_PICK": "Ana tahmini koru",
    }
    return labels.get(action or "", action or "")


def priority_class(priority: str) -> str:
    value = priority.lower()
    if value == "high":
        return "high"
    if value == "medium":
        return "medium"
    return "low"


if __name__ == "__main__":
    main()
