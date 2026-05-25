from __future__ import annotations

import argparse
import json
from html import escape
from pathlib import Path

from src.config import PROCESSED_DIR, SEASON


def main() -> None:
    parser = argparse.ArgumentParser(description="Tum MVP panellerini baglayan ana urun HTML sayfasi uretir.")
    parser.add_argument("--output", default=str(PROCESSED_DIR / "football_intelligence_home.html"))
    args = parser.parse_args()

    output = Path(args.output)
    html = build_html()
    output.write_text(html, encoding="utf-8")
    index = output.parent / "index.html"
    index.write_text(html, encoding="utf-8")
    print(output)


def build_html() -> str:
    preview_summary = load_json(PROCESSED_DIR / "previews_besiktas_2025_2026_chronological" / "index.json").get("summary", {})
    goal_summary = load_json(PROCESSED_DIR / "goal_candidate_backtest_2025_2026.json").get("summary", {})
    match_summary = load_json(PROCESSED_DIR / "match_prediction_backtest_2025_2026.json").get("summary", {})
    league_summary = load_json(PROCESSED_DIR / "league_prediction_model_2025_2026.json").get("summary", {})
    league_market = load_json(PROCESSED_DIR / "league_market_value_audit_2025_2026.json").get("summary", {})
    team_needs = load_json(PROCESSED_DIR / "besiktas_team_needs_2025_2026.json").get("summary", {})
    enriched_scout = load_json(PROCESSED_DIR / "league_scouting_enriched_2025_2026.json").get("summary", {})
    fm_scout = load_json(PROCESSED_DIR / "fm_style_scout_program_2025_2026.json").get("summary", {})
    position_matrix = load_json(PROCESSED_DIR / "position_scout_matrix_2025_2026.json").get("summary", {})
    big_match_report = load_json(PROCESSED_DIR / "big_match_report_2025_2026.json").get("summary", {})
    league_intelligence = load_json(PROCESSED_DIR / "league_intelligence_2025_2026.json").get("summary", {})
    team_blueprints = load_json(PROCESSED_DIR / "team_scout_blueprints_2025_2026.json").get("summary", {})
    scout_quality = load_json(PROCESSED_DIR / "scout_quality_report_2025_2026.json").get("summary", {})
    transfermarkt_review = load_json(PROCESSED_DIR / "transfermarkt_match_review_queue_2025_2026.json").get("summary", {})
    data_quality = load_json(PROCESSED_DIR / "data_quality_scorecard_2025_2026.json")
    warehouse_quality = load_json(PROCESSED_DIR / "metric11_warehouse_quality.json")
    data_catalog = load_json(PROCESSED_DIR / "data_catalog_2025_2026.json").get("coverage", {})
    availability = load_json(PROCESSED_DIR / "player_availability_besiktas_2025_2026.json").get("summary", {})
    api_football_2024 = load_json(PROCESSED_DIR / "api_football_super_lig_snapshot_2024.json").get("summary", {})
    api_analysis = load_json(PROCESSED_DIR / "api_football_super_lig_2024_analysis.json").get("summary", {})
    api_deep = load_json(PROCESSED_DIR / "api_football_super_lig_deep_2024_analysis.json").get("summary", {})
    alias_quality = load_json(PROCESSED_DIR / "player_alias_quality_2025_2026.json").get("summary", {})
    transfer_report = load_json(PROCESSED_DIR / "transfer_recommendation_report_2025_2026.json").get("summary", {})
    news_intel = load_json(PROCESSED_DIR / f"news_intelligence_{SEASON}.json")
    transfer_season = load_json(PROCESSED_DIR / f"transfer_season_context_{SEASON}.json") or {}
    prediction_validation = load_json(PROCESSED_DIR / "prediction_validation_report_2025_2026.json").get("metrics", {})
    all_teams_total = _count_all_teams_reports()

    cards = [
        panel_card(
            "Futbol Komuta Merkezi",
            "Tahmin performansı, Beşiktaş maç önü arşivi, gol adayları, FM scout ve takım ihtiyacını tek ekranda toplar.",
            "football_command_center_2025_2026.html",
            "tek ekran",
        ),
        panel_card(
            "Beşiktaş Maç Önü Zeka Paneli",
            "Form, skor senaryoları, kadro tercihi, sakat/cezalı uygunluk sinyali, kart riski, gol adayları, model kontrolü ve anlatılı maç önü raporu.",
            "besiktas_2025_2026_dashboard_chronological.html",
            f"{preview_summary.get('generated_reports', 0)} rapor",
        ),
        panel_card(
            "Tüm Takım Maç Önü Arşivi",
            "18 Süper Lig takımının tamamı için kronolojik maç önü raporları, tahmin doğruluğu karşılaştırması ve büyük maç sinyalleri.",
            "all_teams_preview_dashboard_2025_2026.html",
            f"{all_teams_total} rapor / 18 takım",
        ),
        panel_card(
            "Tahmin Backtest Paneli",
            "Lig geneli Poisson/Elo modelinin doğru/yanlış, güven ve 18 takım piyasa değeri benchmark kırılımı.",
            "prediction_backtest_dashboard_2025_2026.html",
            f"%{round(league_summary.get('accuracy', 0) * 100)} sonuç doğruluğu",
        ),
        panel_card(
            "Lig Piyasa Değeri Denetimi",
            "18 takımın kadro değerlerini lig modeliyle retrospektif karşılaştırır; üretim tahmini olarak kullanılmaz.",
            "league_market_value_audit_2025_2026.html",
            f"{league_market.get('covered_matches', 0)} maç kapsamı",
        ),
        panel_card(
            "Tahmin Doğrulama Raporu",
            "Beşiktaş üzerinde ayarlanmış ekran kontrolünü, lig-geneli ham ölçümden ayırır ve bağımsız test açığını gösterir.",
            "prediction_validation_report_2025_2026.html",
            f"%{round((prediction_validation.get('unique_league_fixtures_raw_baseline', {}).get('accuracy') or 0) * 100)} ham lig tabanı",
        ),
        panel_card(
            "Büyük Maç Denetim Raporu",
            "Derbi ve büyük maçlarda taraf tahmini, gerçek sonuç, beraberlik riski, kart sinyali ve gol adayı kalitesini ayrı kontrol eder.",
            "big_match_report_2025_2026.html",
            f"{big_match_report.get('high_or_medium_risk_count', 0)} riskli maç",
        ),
        panel_card(
            "Süper Lig Scout Paneli",
            "TFF maç performansından takım güçleri, golcüler, scout kısa listesi ve hakem profilleri.",
            "league_scouting_2025_2026_normalized_dashboard.html",
            "18 takım",
        ),
        panel_card(
            "Süper Lig İstihbarat Raporu",
            "Tüm lig için takım gücü, skor penceresi, kart disiplini, oyuncu yük etiketi, hakem tempo profili ve scout ihtiyacı çıkarır.",
            "league_intelligence_2025_2026.html",
            f"{league_intelligence.get('players', 0)} oyuncu",
        ),
        panel_card(
            "Takım Scout Blueprint",
            "Lig zafiyetlerini rol ihtiyacına çevirir ve her takım için mevcut aday havuzundan oyuncu bağlantısı kurar.",
            "team_scout_blueprints_2025_2026.html",
            f"{team_blueprints.get('candidate_links', 0)} bağlantı",
        ),
        panel_card(
            "Haber İstihbaratı",
            "Türk spor basınından otomatik haber akışı. Transfer iddiaları, sakat/cezalı sinyalleri ve kadro haberleri kaynak güveniyle sınıflandırılıp oyuncu ve takım verisine bağlanır.",
            f"news_intelligence_dashboard_{SEASON}.html",
            f"{news_intel.get('total_articles', 0)} makale · {news_intel.get('transfer_signals', 0)} haber iddiası",
        ),
        panel_card(
            "Transfer Sezonu Bağlam Raporu",
            "Yaz 2026 transfer penceresine hazırlık: sözleşmesi biten oyuncular, son yıl kontrat adayları ve resmi teyit bekleyen transfer haber iddiaları.",
            f"transfer_season_context_{SEASON}.html",
            f"{transfer_season.get('summary', {}).get('free_agents_count', 0)} serbest kalacak · {transfer_season.get('summary', {}).get('final_year_count', 0)} son yıl",
        ),
        panel_card(
            "Transfer Tavsiye Raporu",
            "18 takım için yalnızca pozisyonu dış profille eşleşmiş rol önerileri; serbest transfer ve genç yetenek izleme listeleri.",
            "transfer_recommendation_report_2025_2026.html",
            f"{transfer_report.get('total_candidate_suggestions', 0)} öneri",
        ),
        panel_card(
            "Scout Kalite Denetimi",
            "Düşük pozisyon güvenli adayları, fazla role yayılan oyuncuları ve doğrulanması gereken veri alanlarını inceleme kuyruğuna alır.",
            "scout_quality_report_2025_2026.html",
            f"{scout_quality.get('low_confidence_blueprint_links', 0)} kontrol",
        ),
        panel_card(
            "Transfermarkt Eşleşme Kuyruğu",
            "Lig snapshot kapsamındaki TFF oyuncu eşleşmelerini ve scout yayınına engel olan doğrulama açıklarını listeler.",
            "transfermarkt_match_review_queue_2025_2026.html",
            f"{transfermarkt_review.get('review_tier_counts', {}).get('HIGH_USAGE_UNRESOLVED', 0)} yüksek kullanım açığı",
        ),
        panel_card(
            "Zenginleştirilmiş Scout Paneli",
            "Lig oyuncu havuzuna yaş, sözleşme riski, fırsat skoru, resale ve opsiyonel FM/FIFA tarzı attribute sinyali eklendi.",
            "league_scouting_enriched_2025_2026_dashboard.html",
            f"{enriched_scout.get('profiled_players', 0)} profilli oyuncu",
        ),
        panel_card(
            "FM Tarzı Scout Programı",
            "Oyuncuları skor katkısı, fizik motoru, genç/resale değer, sözleşme fırsatı ve düşük riskli düzenli oyuncu rollerine ayırır.",
            "fm_style_scout_program_2025_2026.html",
            f"{fm_scout.get('candidate_count', 0)} aday",
        ),
        panel_card(
            "Pozisyon Bazlı Scout Matrisi",
            "Sol açık, santrfor, 8 numara, 6 numara, bek, stoper ve kaleci rolleri için adayları takım ihtiyacı ve ekonomik fırsatla eşleştirir.",
            "position_scout_matrix_2025_2026.html",
            f"{position_matrix.get('roles', 0)} rol",
        ),
        panel_card(
            "Beşiktaş Takım İhtiyaç Paneli",
            "Kadro yaşı, sözleşme riski, genç varlıklar, gol yükü ve ihtiyaç sinyalleri.",
            "besiktas_team_needs_2025_2026_dashboard.html",
            f"{team_needs.get('players', 0)} oyuncu",
        ),
        panel_card(
            "Veri Kataloğu",
            "Toplanan veri kapsamı, kaynak riski, eksik kritik alanlar ve ürün hazırlık durumu.",
            "data_catalog_2025_2026.html",
            f"{data_catalog.get('matches', 0)} maç",
        ),
        panel_card(
            "Veri Kalite Scorecard",
            "Kapsam, oyuncu profili, tahmin doğruluğu, beraberlik yakalama, gol adayı ve scout pozisyon güveni için sağlık kartı.",
            "data_quality_scorecard_2025_2026.html",
            f"{data_quality.get('score', 0)}/100",
        ),
        panel_card(
            "SQLite Veri Ambarı",
            "Maç, takım, oyuncu, hakem, tahmin, gol adayı ve scout blueprint tablolarını tek sorgulanabilir dosyada toplar.",
            "metric11_warehouse_quality.html",
            f"{sum(warehouse_quality.get('table_counts', {}).values())} satır",
        ),
        panel_card(
            "Veri Kaynak İzleme Listesi",
            "TFF, Transfermarkt, beIN SPORTS/LigTV, API, açık veri, forum ve GitHub kaynaklarını risk/güncellik ritmiyle takip eder.",
            "source_watchlist_2025_2026.html",
            "kaynak radarı",
        ),
        panel_card(
            "Dış API Veri Paneli",
            "API-Football 2024 sezonundan puan durumu, fikstür, oyuncu rating, şut, pas, duel, asist ve kart sinyalleri.",
            "api_football_super_lig_2024_analysis.html",
            f"{api_analysis.get('fixtures', 0)} fikstür",
        ),
        panel_card(
            "Dış API Derin Veri Paneli",
            "2024 kadro havuzu, oyuncu sezon istatistikleri ve geçmiş sakatlık sinyalleriyle scout doğrulama katmanı.",
            "api_football_super_lig_deep_2024_analysis.html",
            f"{api_deep.get('combined_player_pool', 0)} oyuncu",
        ),
        panel_card(
            "Oyuncu Alias Kalite Raporu",
            "Lig geneli TFF/Transfermarkt ve scout TFF/dış API canonical ad eşleşmesi kalitesini gösterir.",
            "player_alias_quality_2025_2026.html",
            f"{alias_quality.get('alias_players', 0)} alias",
        ),
    ]

    # Kullanıcıya gösterilen kartlar (ilk 4 featured)
    user_cards = cards[:15]
    # Sadece yönetici/analist erişimi — ana sayfada görünmez
    admin_cards = cards[15:]

    featured_cards = "".join(user_cards[:4])
    module_cards = "".join(user_cards[4:])
    admin_section = "".join(admin_cards)

    return f"""<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>metric11 — Süper Lig Futbol İstihbaratı</title>
  <meta name="description" content="Süper Lig maç tahminleri, gol adayları, scout analizleri ve transfer istihbaratı. 18 takım, gerçek veri.">
  <meta property="og:title" content="metric11 — Süper Lig Futbol İstihbaratı">
  <meta property="og:description" content="Süper Lig maç tahminleri, gol adayları, scout analizleri ve transfer istihbaratı. 18 takım, gerçek veri.">
  <meta property="og:image" content="/og-image.svg">
  <meta property="og:type" content="website">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="theme-color" content="#091810">
  <link rel="icon" href="favicon.svg" type="image/svg+xml">
  <style>
    :root {{
      --bg:#f3f5f4; --panel:#fff; --ink:#132018; --muted:#627067; --line:#d7ded9;
      --red:#bd2936; --green:#116447; --lime:#cde94e; --blue:#22618c; --dark:#091810; --soft:#e8eee9;
    }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; font-family:Inter, "Segoe UI", Arial, sans-serif; background:var(--bg); color:var(--ink); }}
    .topbar {{ position:sticky; top:0; z-index:5; display:flex; align-items:center; justify-content:space-between; gap:20px; min-height:64px; padding:0 clamp(16px,4vw,42px); background:var(--dark); color:white; border-bottom:1px solid #203328; }}
    .brand {{ display:flex; gap:11px; align-items:center; font-weight:800; font-size:19px; }}
    .brand-mark {{ width:30px; height:30px; display:grid; place-items:center; border-radius:7px; color:var(--dark); background:var(--lime); font-size:15px; }}
    .season {{ color:#a7b3ab; font-size:12px; font-weight:500; margin-left:4px; }}
    nav {{ display:flex; gap:4px; flex-wrap:nowrap; overflow-x:auto; overflow-y:hidden; justify-content:flex-end; -webkit-overflow-scrolling:touch; scrollbar-width:none; }}
    nav::-webkit-scrollbar {{ display:none; }}
    nav a {{ color:#d5ded8; text-decoration:none; font-size:13px; font-weight:600; padding:9px 10px; border-radius:6px; white-space:nowrap; flex-shrink:0; }}
    nav a:hover, nav a.active {{ background:#162b20; color:white; }}
    header {{ background:#102419; color:white; padding:28px clamp(16px,4vw,42px) 25px; border-bottom:3px solid var(--green); }}
    .matchroom {{ max-width:1360px; margin:0 auto; display:grid; grid-template-columns:minmax(320px,1.05fr) minmax(400px,.95fr); align-items:end; gap:28px; }}
    .overline {{ color:var(--lime); font-size:12px; text-transform:uppercase; font-weight:700; margin-bottom:11px; }}
    header h1 {{ margin:0 0 10px; font-size:43px; letter-spacing:0; max-width:720px; line-height:1.08; }}
    header p {{ margin:0; max-width:690px; color:#c1cec5; line-height:1.55; font-size:14px; }}
    .hero-actions {{ display:flex; gap:10px; flex-wrap:wrap; margin-top:18px; }}
    .hero-actions a {{ display:inline-flex; align-items:center; min-height:42px; padding:0 16px; border-radius:6px; text-decoration:none; font-weight:700; font-size:14px; }}
    .primary {{ background:var(--lime); color:var(--dark); }}
    .secondary {{ border:1px solid #355044; color:white; }}
    .scoreboard {{ border:1px solid #294237; border-radius:8px; padding:15px 17px; background:#0b1c13; }}
    .scoreboard-head {{ display:flex; justify-content:space-between; align-items:center; color:#afbeb5; font-size:12px; margin-bottom:14px; }}
    .live {{ display:inline-flex; align-items:center; gap:6px; color:#d9e3dc; }}
    .live::before {{ content:""; width:7px; height:7px; border-radius:50%; background:var(--lime); }}
    .board-grid {{ display:grid; grid-template-columns:repeat(4,1fr); gap:10px; }}
    .board-grid span {{ display:block; color:#91a196; font-size:11px; min-height:29px; }}
    .board-grid strong {{ display:block; color:white; font-size:22px; }}
    main {{ max-width:1360px; margin:0 auto; padding:22px clamp(14px,3vw,30px) 42px; }}
    .section-title {{ display:flex; align-items:end; justify-content:space-between; gap:14px; margin:8px 0 14px; }}
    .section-title h2 {{ margin:0; font-size:19px; }}
    .section-title p {{ margin:0; color:var(--muted); font-size:13px; }}
    .metrics {{ display:grid; grid-template-columns:repeat(8,1fr); gap:10px; margin-bottom:22px; }}
    .metric, .card, section, details {{ background:var(--panel); border:1px solid var(--line); border-radius:8px; }}
    .metric {{ padding:13px 12px; min-height:76px; }}
    .metric span {{ display:block; color:var(--muted); font-size:11px; line-height:1.3; }}
    .metric strong {{ display:block; font-size:22px; margin-top:7px; }}
    .featured {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:12px; margin-bottom:26px; }}
    .cards {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:12px; margin-bottom:20px; }}
    .card {{ padding:16px; min-height:164px; display:flex; flex-direction:column; justify-content:space-between; }}
    .featured .card {{ border-top:3px solid var(--green); min-height:192px; }}
    .card h2 {{ margin:0 0 7px; font-size:16px; line-height:1.3; }}
    .featured .card h2 {{ font-size:18px; }}
    .card p {{ color:var(--muted); font-size:13px; margin:0 0 14px; line-height:1.48; }}
    .card a {{ display:inline-flex; align-items:center; color:var(--green); text-decoration:none; font-weight:700; font-size:13px; }}
    .card a::after {{ content:"  >"; margin-left:7px; }}
    .tag {{ display:inline-flex; align-self:flex-start; min-height:23px; align-items:center; border-radius:4px; padding:0 8px; font-size:11px; color:var(--green); background:#edf5ef; border:1px solid #cce0d3; margin-bottom:11px; font-weight:600; }}
    section {{ padding:18px; margin-bottom:18px; }}
    section h2 {{ margin:0 0 12px; font-size:17px; }}
    .split {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; }}
    ul {{ margin:0; padding-left:18px; color:#30343a; line-height:1.65; }}
    details {{ padding:0; margin-bottom:26px; overflow:hidden; }}
    summary {{ list-style:none; cursor:pointer; padding:14px 16px; font-weight:700; font-size:14px; }}
    summary::-webkit-details-marker {{ display:none; }}
    .detail-metrics {{ display:grid; grid-template-columns:repeat(5,1fr); gap:10px; padding:0 14px 14px; }}
    @media (max-width:1120px) {{ .matchroom {{ grid-template-columns:1fr; }} .metrics {{ grid-template-columns:repeat(4,1fr); }} .featured {{ grid-template-columns:repeat(2,1fr); }} .cards {{ grid-template-columns:repeat(2,1fr); }} .detail-metrics {{ grid-template-columns:repeat(3,1fr); }} }}
    @media (max-width:680px) {{ .topbar {{ position:static; flex-direction:column; align-items:stretch; padding:11px 16px 0; gap:0; min-height:unset; }} .brand {{ padding-bottom:8px; }} .season {{ display:none; }} nav {{ justify-content:flex-start; border-top:1px solid #1e3228; padding:7px 0 9px; }} header {{ padding:22px 16px; }} header h1 {{ font-size:28px; }} .board-grid, .metrics, .featured, .cards, .detail-metrics, .split {{ grid-template-columns:repeat(2,minmax(0,1fr)); }} main {{ padding:15px 12px 34px; }} .card {{ min-height:auto; }} .section-title {{ align-items:start; flex-direction:column; }} }}
    @media (max-width:430px) {{ .board-grid, .featured, .cards, .detail-metrics, .split {{ grid-template-columns:1fr; }} .metrics {{ grid-template-columns:repeat(2,minmax(0,1fr)); }} header h1 {{ font-size:24px; }} }}
  </style>
</head>
<body>
  <div class="topbar">
    <div class="brand"><span class="brand-mark">11</span> metric11 <span class="season">Süper Lig 2025/26</span></div>
    <nav>
      <a class="active" href="football_intelligence_home.html">Merkez</a>
      <a href="football_command_center_2025_2026.html">Analiz</a>
      <a href="besiktas_2025_2026_dashboard_chronological.html">Maç Önü</a>
      <a href="transfer_recommendation_report_2025_2026.html">Scout</a>
      <a href="all_teams_preview_dashboard_2025_2026.html">Lig</a>
    </nav>
  </div>
  <header>
    <div class="matchroom">
      <div>
        <div class="overline">Maç günü merkezi</div>
        <h1>Maçı oku. Kadroyu tartış. Oyuncuyu keşfet.</h1>
        <p>Skor senaryoları, gol adayları, eksik oyuncu etkisi ve transfer seçenekleri tek sezon veri akışında izleniyor.</p>
        <div class="hero-actions">
          <a class="primary" href="besiktas_2025_2026_dashboard_chronological.html">Beşiktaş maç odası</a>
          <a class="secondary" href="football_command_center_2025_2026.html">Analiz merkezi</a>
        </div>
      </div>
      <div class="scoreboard">
        <div class="scoreboard-head"><span>Model sağlık panosu</span><span class="live">Güncel veri seti</span></div>
        <div class="board-grid">
          <div><span>Lig ham ölçümü</span><strong>%{round((prediction_validation.get('unique_league_fixtures_raw_baseline', {}).get('accuracy') or 0) * 100)}</strong></div>
          <div><span>Gol adayı ilk 5</span><strong>%{round(goal_summary.get('top_5_hit_rate', 0) * 100)}</strong></div>
          <div><span>Onaylı scout önerisi</span><strong>{transfer_report.get('total_candidate_suggestions', 0)}</strong></div>
          <div><span>Veri sağlık skoru</span><strong>{data_quality.get('score', 0)}</strong></div>
        </div>
      </div>
    </div>
  </header>
  <main>
    <div class="section-title"><h2>Öne çıkan deneyimler</h2><p>Futbolseverin ilk gireceği dört alan</p></div>
    <div class="featured">{featured_cards}</div>
    <div class="section-title"><h2>Sezon rakamları</h2><p>2025-26 sezonu verisinden</p></div>
    <div class="metrics">
      {metric("Tahmin doğruluğu", f"%{round((prediction_validation.get('unique_league_fixtures_raw_baseline', {}).get('accuracy') or 0) * 100)}")}
      {metric("Maç önü raporu", preview_summary.get("generated_reports", 0))}
      {metric("Büyük maç uyarısı", big_match_report.get("high_or_medium_risk_count", 0))}
      {metric("Gol adayı isabeti", f"%{round(goal_summary.get('top_5_hit_rate', 0) * 100)}")}
      {metric("Transfer önerisi", transfer_report.get('total_candidate_suggestions', 0))}
      {metric("Serbest kalacak oyuncu", transfer_season.get('summary', {}).get('free_agents_count', 0))}
      {metric("Eksik oyuncu sinyali", availability.get("auto_suspension_entries", 0) + availability.get("manual_entries", 0))}
      {metric("Scout profili", enriched_scout.get("profiled_players", 0))}
    </div>
    <div class="section-title"><h2>Tüm araçlar</h2><p>Tahmin, scout, transfer ve haber modülleri</p></div>
    <div class="cards">{module_cards}</div>
    <div class="split">
      <section>
        <h2>Ürün Gerçekliği</h2>
        <ul>
          <li>Maç sonucu modeli lig genelinde %{round(league_summary.get('accuracy', 0) * 100)}, Beşiktaş maç önü arşivinde %{round(match_summary.get('accuracy', 0) * 100)} doğrulukta; ürün dili olasılık, güven ve senaryo üzerinden ilerler.</li>
          <li>Taraf eğilimi verilen Beşiktaş maçlarında isabet %{round(match_summary.get('actionable_accuracy', 0) * 100)}; zayıf sinyalli maçlar artık senaryo anlatımı olarak işaretlenir.</li>
          <li>Gol adayı motoru Top 5 içinde %{round(goal_summary.get('top_5_hit_rate', 0) * 100)} isabet verdi; bu modül ürün tarafında daha güçlü.</li>
          <li>FM scout programı rol bazlı aday, tahmini fiziksel yük ve sözleşme fırsatı üretir.</li>
        </ul>
      </section>
      <section>
        <h2>Veri Omurgası</h2>
        <ul>
          <li>TFF 2025-2026: {data_catalog.get('matches', 0)} maç, {data_catalog.get('goals', 0)} gol, {data_catalog.get('cards', 0)} kart.</li>
          <li>Transfermarkt: {data_catalog.get('transfermarkt_league_clubs', 0)}/18 kulüp, {data_catalog.get('transfermarkt_league_players', 0)} oyuncu ve €{data_catalog.get('transfermarkt_league_market_value_total_eur', 0):,} lig piyasa değeri katmanı.</li>
          <li>API-Football: 2024 geçmiş sezon snapshot ve derin kadro/sakatlık katmanı bağlı; 2025 plan kısıtı nedeniyle ana sezon TFF ile yürür.</li>
        </ul>
      </section>
    </div>
  </main>
  <script defer src="/_vercel/insights/script.js"></script>
</body>
</html>
"""


def _count_all_teams_reports() -> int:
    from src.generate_preview_batch import ALL_TEAMS, team_slug
    from src.config import SEASON
    total = 0
    for team in ALL_TEAMS:
        slug = team_slug(team)
        idx = PROCESSED_DIR / f"previews_{slug}_{SEASON}_chronological" / "index.json"
        if idx.exists():
            data = json.loads(idx.read_text(encoding="utf-8"))
            total += data.get("summary", {}).get("generated_reports", 0)
    return total


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def metric(label: str, value) -> str:
    return f'<div class="metric"><span>{escape(label)}</span><strong>{escape(str(value))}</strong></div>'


def panel_card(title: str, body: str, href: str, tag: str) -> str:
    return (
        f'<article class="card"><div><span class="tag">{escape(tag)}</span><h2>{escape(title)}</h2>'
        f'<p>{escape(body)}</p></div><a href="{escape(href)}">Paneli Aç</a></article>'
    )


if __name__ == "__main__":
    main()
