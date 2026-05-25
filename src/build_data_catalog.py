from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.config import PROCESSED_DIR, ROOT_DIR
from src.html_utils import md_to_html, page_html
from src.generate_preview_batch import ALL_TEAMS, team_slug
from src.normalization import normalize_matches


def main() -> None:
    parser = argparse.ArgumentParser(description="Toplanan veri setleri icin kaynak/kapsam/eksik raporu uretir.")
    parser.add_argument("--output-prefix", default="data_catalog_2025_2026")
    args = parser.parse_args()

    catalog = build_catalog()
    md = build_markdown(catalog)
    json_path = PROCESSED_DIR / f"{args.output_prefix}.json"
    md_path = PROCESSED_DIR / f"{args.output_prefix}.md"
    json_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(md, encoding="utf-8")
    html_path = PROCESSED_DIR / f"{args.output_prefix}.html"
    html_path.write_text(page_html("Veri Kataloğu", md_to_html(md)), encoding="utf-8")
    print(md)


def build_catalog() -> dict:
    league_matches = normalize_matches(load_json(PROCESSED_DIR / "tff_super_lig_enriched_2025_2026.json", []))
    besiktas_profiles = load_json(PROCESSED_DIR / "tff_player_profiles_besiktas_2025_2026.json", [])
    scout_profiles = load_json(PROCESSED_DIR / "tff_player_profiles_scout_shortlist_2025_2026.json", [])
    priority_profiles = load_json(PROCESSED_DIR / "tff_player_profiles_all_priority_2025_2026.json", [])
    league_profiles = load_json(PROCESSED_DIR / "tff_player_profiles_league_all_2025_2026.json", [])
    transfermarkt = load_json(PROCESSED_DIR / "transfermarkt_besiktas_squad_2025_2026.json", {})
    transfermarkt_league = load_json(PROCESSED_DIR / "transfermarkt_super_lig_squads_2025_2026.json", {})
    transfermarkt_player_profiles = load_json(PROCESSED_DIR / "transfermarkt_super_lig_player_profiles_2025_2026.json", {})
    enriched_profiles = load_json(PROCESSED_DIR / "tff_player_profiles_enriched_2025_2026.json", [])
    previews = load_json(PROCESSED_DIR / "previews_besiktas_2025_2026_chronological" / "index.json", {})
    goal_backtest = load_json(PROCESSED_DIR / "goal_candidate_backtest_2025_2026.json", {})
    match_backtest = load_json(PROCESSED_DIR / "match_prediction_backtest_2025_2026.json", {})
    big_match_report = load_json(PROCESSED_DIR / "big_match_report_2025_2026.json", {})
    error_analysis = load_json(PROCESSED_DIR / "prediction_error_analysis_2025_2026.json", {})
    league_model = load_json(PROCESSED_DIR / "league_prediction_model_2025_2026.json", {})
    league_market_audit = load_json(PROCESSED_DIR / "league_market_value_audit_2025_2026.json", {})
    availability = load_json(PROCESSED_DIR / "player_availability_besiktas_2025_2026.json", {})
    attribute_sources = load_json(ROOT_DIR / "data/manual/player_attribute_sources.json", {})
    attribute_dataset = load_json(PROCESSED_DIR / "player_attribute_dataset_normalized.json", {})
    fm_scout = load_json(PROCESSED_DIR / "fm_style_scout_program_2025_2026.json", {})
    position_matrix = load_json(PROCESSED_DIR / "position_scout_matrix_2025_2026.json", {})
    league_intelligence = load_json(PROCESSED_DIR / "league_intelligence_2025_2026.json", {})
    team_blueprints = load_json(PROCESSED_DIR / "team_scout_blueprints_2025_2026.json", {})
    scout_quality = load_json(PROCESSED_DIR / "scout_quality_report_2025_2026.json", {})
    transfermarkt_review = load_json(PROCESSED_DIR / "transfermarkt_match_review_queue_2025_2026.json", {})
    warehouse_quality = load_json(PROCESSED_DIR / "metric11_warehouse_quality.json", {})
    profile_queue = load_json(PROCESSED_DIR / "player_profile_enrichment_queue_2025_2026.json", {})
    source_watchlist = load_json(ROOT_DIR / "data/manual/source_watchlist.json", {})
    news_context = load_json(PROCESSED_DIR / "news_context_snapshot_2025_2026.json", {})
    news_intelligence = load_json(PROCESSED_DIR / "news_intelligence_2025_2026.json", {})
    news_rss = load_json(PROCESSED_DIR / "news_rss_latest_2025_2026.json", {})
    news_official = load_json(PROCESSED_DIR / "news_official_clubs_latest_2025_2026.json", {})
    news_twitter = load_json(PROCESSED_DIR / "news_twitter_latest_2025_2026.json", {})
    api_football_2024 = load_json(PROCESSED_DIR / "api_football_super_lig_snapshot_2024.json", {})
    api_football_2025 = load_json(PROCESSED_DIR / "api_football_super_lig_snapshot_2025.json", {})
    api_football_analysis = load_json(PROCESSED_DIR / "api_football_super_lig_2024_analysis.json", {})
    api_football_deep = load_json(PROCESSED_DIR / "api_football_super_lig_deep_snapshot_2024.json", {})
    api_football_deep_analysis = load_json(PROCESSED_DIR / "api_football_super_lig_deep_2024_analysis.json", {})
    alias_quality = load_json(PROCESSED_DIR / "player_alias_quality_2025_2026.json", {})
    all_preview_indexes = [
        load_json(PROCESSED_DIR / f"previews_{team_slug(team)}_2025_2026_chronological" / "index.json", {})
        for team in ALL_TEAMS
    ]
    tm_matched_profiles = sum(1 for player in enriched_profiles if player.get("tm_id"))
    twitter_posts = news_twitter.get("total_tweets", 0)
    twitter_successful_accounts = sum(1 for account in news_twitter.get("accounts", []) if not account.get("error"))
    twitter_provider = news_twitter.get("provider", "not_run")
    twitter_status = news_twitter.get("collection_status", "NO_SNAPSHOT")
    official_articles = news_official.get("total_articles", 0)
    official_sources = news_official.get("successful_sources", 0)
    official_configured = news_official.get("configured_sources", 18)
    official_status = news_official.get("collection_status", "NO_SNAPSHOT")
    official_coverage = (
        f"{official_articles} duyuru; {official_sources}/{official_configured} kulüp sitesi erişilebilir; "
        f"durum={official_status}"
        if news_official
        else "18 resmi kulüp sitesi yapılandırıldı; snapshot henüz yok"
    )
    if twitter_posts:
        twitter_coverage = (
            f"{twitter_posts} gönderi snapshot'ı; {twitter_successful_accounts} hesap başarılı; "
            f"kaynak={twitter_provider}"
        )
    elif news_twitter:
        twitter_coverage = (
            f"Collector çalıştı ({twitter_provider}/{twitter_status}); "
            "kullanılabilir gönderi snapshot'ı yok"
        )
    else:
        twitter_coverage = "Collector yapılandırıldı; başarılı snapshot henüz yok"

    teams = set()
    players = set()
    referees = set()
    cards = 0
    goals = 0
    starters = 0
    bench = 0
    for match in league_matches:
        teams.add(match["home_team"]["name"])
        teams.add(match["away_team"]["name"])
        for side in ("home", "away"):
            starters += len(match["lineups"][side]["starting"])
            bench += len(match["lineups"][side]["bench"])
            cards += len(match["cards"][side])
            goals += len(match["goals"][side])
            for group in ("starting", "bench"):
                for player in match["lineups"][side][group]:
                    players.add(player.get("external_id") or player["name"])
        for official in match.get("officials", []):
            if official.get("role") == "Hakem":
                referees.add(official["name"])

    return {
        "season": "2025-2026",
        "sources": [
            {
                "name": "TFF maç detayları",
                "public_label": "Resmi federasyon maç verisi",
                "type": "SCRAPING",
                "risk": "MEDIUM",
                "license_status": "VERIFY_TERMS",
                "display_policy": "INTERNAL_SOURCE_PUBLIC_CATEGORY",
                "coverage": "Süper Lig 306 maç",
                "fields": ["fikstür", "skor", "hakem", "ilk 11", "yedek", "kart", "gol", "dakika", "oyuncu ID"],
            },
            {
                "name": "TFF oyuncu profilleri",
                "public_label": "Resmi federasyon oyuncu profili",
                "type": "SCRAPING",
                "risk": "MEDIUM",
                "license_status": "VERIFY_TERMS",
                "display_policy": "INTERNAL_SOURCE_PUBLIC_CATEGORY",
                "coverage": f"İşlenen lig profil havuzu {len(enriched_profiles)} profil; lig snapshot içi eşleşme ayrıca ölçülür",
                "fields": ["doğum tarihi", "yaş", "uyruk", "lisans", "kulüp", "sözleşme başlangıç", "sözleşme bitiş"],
            },
            {
                "name": "Transfermarkt kadro sayfası",
                "public_label": "Piyasa değeri ve kadro profili",
                "type": "SCRAPING",
                "risk": "HIGH",
                "license_status": "VERIFY_TERMS_BEFORE_COMMERCIAL_USE",
                "display_policy": "INTERNAL_SOURCE_PUBLIC_CATEGORY",
                "coverage": "Süper Lig 2025/26: 18 kulüp kadrosu, pozisyon ve piyasa değeri",
                "fields": ["pozisyon", "pozisyon grubu", "yaş", "sözleşme bitiş", "piyasa değeri", "profil tam adı"],
            },
            {
                "name": "Oyuncu uygunluk sinyalleri",
                "public_label": "Model türetilmiş uygunluk sinyali",
                "type": "DERIVED+MANUAL",
                "risk": "MEDIUM",
                "license_status": "DERIVED_FROM_INTERNAL_DATA_AND_MANUAL_VERIFICATION",
                "display_policy": "PUBLIC_DERIVED_SIGNAL_ALLOWED",
                "coverage": "Beşiktaş 2025/26 kart cezası çıkarımı + manuel sakat/cezalı override dosyası",
                "fields": ["maç", "oyuncu", "durum", "neden", "güven", "kaynak", "tahmine dahil/dışla"],
            },
            {
                "name": "Türk spor haber RSS akışı",
                "public_label": "Güncel spor haber bağlamı",
                "type": "RSS_NEWS",
                "risk": "MEDIUM",
                "license_status": "VERIFY_TERMS_AND_QUOTE_LIMITS",
                "display_policy": "SHOW_LINK_AND_DERIVED_SIGNAL_ONLY",
                "coverage": (
                    f"{news_rss.get('total_articles', 0)} ham haber; "
                    f"{news_intelligence.get('analyzed_articles', 0)} ilgili analiz; "
                    f"{news_intelligence.get('transfer_signals', 0)} transfer iddiası"
                ),
                "fields": ["başlık", "kaynak", "yayın zamanı", "transfer iddiası", "kaynak teyit durumu"],
            },
            {
                "name": "Süper Lig resmi kulüp web duyuruları",
                "public_label": "Resmi kulüp duyuruları",
                "type": "OFFICIAL_CLUB_NEWS",
                "risk": "LOW_MEDIUM",
                "license_status": "VERIFY_TERMS_AND_LINK_DERIVED_DISPLAY",
                "display_policy": "SHOW_LINK_AND_DERIVED_SIGNAL_ONLY",
                "coverage": official_coverage,
                "fields": ["kulüp", "duyuru başlığı", "yayın zamanı", "resmi transfer teyidi", "bağlantı"],
            },
            {
                "name": "X resmi kulüp ve futbol haber hesapları",
                "public_label": "Resmi kulüp ve sosyal haber duyuruları",
                "type": "X_SOCIAL_SIGNAL",
                "risk": "MEDIUM",
                "license_status": "PLATFORM_TERMS_AND_DISPLAY_REQUIREMENTS",
                "display_policy": "SHOW_LINK_AND_DERIVED_SIGNAL_ONLY",
                "coverage": twitter_coverage,
                "fields": ["hesap türü", "gönderi kimliği", "resmi teyit", "transfer iddiası", "bağlantı"],
            },
            {
                "name": "FM/FIFA tarzı oyuncu attribute kaynakları",
                "public_label": "Oyuncu attribute ve potansiyel veri seti",
                "type": "OPEN_DATASET_OR_VERIFIED_EXPORT",
                "risk": "LOW_TO_HIGH_BY_LICENSE",
                "license_status": "SOURCE_SPECIFIC",
                "display_policy": "SHOW_ONLY_IF_LICENSE_ALLOWED",
                "coverage": f"{len(attribute_sources.get('candidate_sources', []))} aday kaynak kaydı; normalize import varsa {attribute_dataset.get('summary', {}).get('players_out', 0)} oyuncu",
                "fields": ["current ability", "potential ability", "growth room", "fiziksel skor", "mental skor", "teknik skor", "rol uyumu"],
            },
            {
                "name": "API-Football Süper Lig snapshot",
                "public_label": "Dış futbol API doğrulama ve geçmiş sezon zenginleştirme",
                "type": "API",
                "risk": "MEDIUM",
                "license_status": "API_PLAN_LIMITED",
                "display_policy": "INTERNAL_SOURCE_PUBLIC_CATEGORY",
                "coverage": "2024 sezonu ücretsiz planda erişilebilir; 2025 sezonu plan kısıtı nedeniyle boş dönüyor; derin snapshot rate-limit kontrollü çalışır",
                "fields": ["lig", "puan durumu", "takımlar", "fikstür", "gol krallığı", "asist", "kart", "kadro", "sakatlık", "oyuncu sezon istatistiği"],
            },
        ],
        "coverage": {
            "matches": len(league_matches),
            "teams": len(teams),
            "unique_players_in_match_sheets": len(players),
            "main_referees": len(referees),
            "starting_records": starters,
            "bench_records": bench,
            "cards": cards,
            "goals": goals,
            "besiktas_player_profiles": len(besiktas_profiles),
            "scout_shortlist_profiles": len(scout_profiles),
            "priority_player_profiles": len(priority_profiles),
            "league_player_profiles": len(league_profiles),
            "transfermarkt_besiktas_players": transfermarkt.get("summary", {}).get("players", 0),
            "transfermarkt_besiktas_market_value_total_eur": transfermarkt.get("summary", {}).get("market_value_total_eur", 0),
            "transfermarkt_league_clubs": transfermarkt_league.get("summary", {}).get("clubs", 0),
            "transfermarkt_league_players": transfermarkt_league.get("summary", {}).get("players", 0),
            "transfermarkt_league_market_value_total_eur": transfermarkt_league.get("summary", {}).get("market_value_total_eur", 0),
            "transfermarkt_profile_details_collected": transfermarkt_player_profiles.get("summary", {}).get("profiles_collected", 0),
            "transfermarkt_profile_full_names": transfermarkt_player_profiles.get("summary", {}).get("profiles_with_full_name", 0),
            "tff_tm_enriched_profiles": len(enriched_profiles),
            "tff_tm_matched_profiles": tm_matched_profiles,
            "tff_tm_match_rate": round(tm_matched_profiles / len(enriched_profiles), 3) if enriched_profiles else 0,
            "tff_tm_snapshot_in_scope_profiles": transfermarkt_review.get("summary", {}).get("snapshot_in_scope_tff_profiles", 0),
            "tff_tm_in_scope_match_rate": transfermarkt_review.get("summary", {}).get("in_scope_match_rate", 0),
            "tff_tm_unmatched_profiles": transfermarkt_review.get("summary", {}).get("unmatched_profiles", 0),
            "tff_tm_scout_blocking_unmatched": transfermarkt_review.get("summary", {}).get("scout_blocking_unmatched", 0),
            "tff_tm_high_usage_unresolved": transfermarkt_review.get("summary", {}).get("review_tier_counts", {}).get("HIGH_USAGE_UNRESOLVED", 0),
            "besiktas_previews": previews.get("summary", {}).get("generated_reports", 0),
            "all_teams_preview_teams": len([item for item in all_preview_indexes if item.get("reports")]),
            "all_teams_preview_reports": sum(item.get("summary", {}).get("generated_reports", 0) for item in all_preview_indexes),
            "goal_candidate_top3": goal_backtest.get("summary", {}).get("top_3_hit_rate"),
            "goal_candidate_top5": goal_backtest.get("summary", {}).get("top_5_hit_rate"),
            "goal_candidate_top8": goal_backtest.get("summary", {}).get("top_8_hit_rate"),
            "goal_candidate_top10": goal_backtest.get("summary", {}).get("top_10_hit_rate"),
            "besiktas_match_prediction_accuracy": match_backtest.get("summary", {}).get("accuracy"),
            "besiktas_actionable_prediction_accuracy": match_backtest.get("summary", {}).get("actionable_accuracy"),
            "besiktas_big_match_prediction_accuracy": match_backtest.get("summary", {}).get("big_match_accuracy"),
            "big_match_risk_reports": big_match_report.get("summary", {}).get("big_match_count", 0),
            "big_match_medium_high_risk_count": big_match_report.get("summary", {}).get("high_or_medium_risk_count", 0),
            "prediction_error_misses": error_analysis.get("summary", {}).get("match_misses", 0),
            "prediction_error_missed_draws": error_analysis.get("summary", {}).get("miss_types", {}).get("missed_draw", 0),
            "league_prediction_accuracy": league_model.get("summary", {}).get("accuracy"),
            "league_market_audit_covered_matches": league_market_audit.get("summary", {}).get("covered_matches", 0),
            "league_market_baseline_accuracy": league_market_audit.get("summary", {}).get("reporting_baseline_accuracy"),
            "availability_matches": availability.get("summary", {}).get("matches", 0),
            "availability_signal_matches": availability.get("summary", {}).get("matches_with_unavailable", 0),
            "availability_unavailable_entries": availability.get("summary", {}).get("auto_suspension_entries", 0)
            + availability.get("summary", {}).get("manual_entries", 0),
            "attribute_candidate_sources": len(attribute_sources.get("candidate_sources", [])),
            "attribute_imported_players": attribute_dataset.get("summary", {}).get("players_out", 0),
            "attribute_matched_current_ability": attribute_dataset.get("summary", {}).get("with_current_ability", 0),
            "fm_style_scout_candidates": fm_scout.get("summary", {}).get("candidate_count", 0),
            "fm_style_role_buckets": fm_scout.get("summary", {}).get("role_buckets", 0),
            "position_scout_roles": position_matrix.get("summary", {}).get("roles", 0),
            "position_scout_role_candidates": position_matrix.get("summary", {}).get("matched_role_candidates", 0),
            "league_intelligence_teams": league_intelligence.get("summary", {}).get("teams", 0),
            "league_intelligence_players": league_intelligence.get("summary", {}).get("players", 0),
            "league_intelligence_referees": league_intelligence.get("summary", {}).get("referees", 0),
            "team_scout_blueprint_teams": team_blueprints.get("summary", {}).get("teams", 0),
            "team_scout_blueprint_candidate_links": team_blueprints.get("summary", {}).get("candidate_links", 0),
            "scout_quality_low_confidence_links": scout_quality.get("summary", {}).get("low_confidence_blueprint_links", 0),
            "scout_quality_unique_low_confidence_player_roles": scout_quality.get("summary", {}).get("low_confidence_unique_player_roles", 0),
            "scout_quality_repeated_role_players": scout_quality.get("summary", {}).get("repeated_role_players", 0),
            "warehouse_tables": len(warehouse_quality.get("table_counts", {})),
            "warehouse_rows_total": sum(warehouse_quality.get("table_counts", {}).values()) if warehouse_quality.get("table_counts") else 0,
            "warehouse_quality_findings": len(warehouse_quality.get("findings", [])),
            "profile_enrichment_queue": profile_queue.get("summary", {}).get("queued", 0),
            "profile_enrichment_missing_candidates": profile_queue.get("summary", {}).get("missing_candidates", 0),
            "source_watchlist_sources": len(source_watchlist.get("sources", [])),
            "source_watchlist_daily_sources": sum(
                1 for source in source_watchlist.get("sources", []) if "daily" in source.get("freshness_target", "")
            ),
            "news_context_sources_ok": news_context.get("ok_count", 0),
            "news_context_signals": news_context.get("summary", {}).get("signals", 0),
            "news_context_structured_unavailability": len(news_context.get("team_unavailability", [])),
            "news_rss_articles": news_rss.get("total_articles", 0),
            "news_official_articles": official_articles,
            "news_official_successful_sources": official_sources,
            "news_official_configured_sources": official_configured,
            "news_official_status": official_status,
            "news_intelligence_articles": news_intelligence.get("analyzed_articles", 0),
            "news_transfer_claims": news_intelligence.get("transfer_signals", 0),
            "news_transfer_status_counts": news_intelligence.get("transfer_status_counts", {}),
            "news_twitter_posts": twitter_posts,
            "news_twitter_successful_accounts": twitter_successful_accounts,
            "news_twitter_provider": twitter_provider,
            "news_twitter_status": twitter_status,
            "api_football_2024_successful_endpoints": api_football_2024.get("summary", {}).get("successful_endpoints", 0),
            "api_football_2024_fixtures": endpoint_count(api_football_2024, "fixtures"),
            "api_football_2024_teams": endpoint_count(api_football_2024, "teams"),
            "api_football_2025_successful_endpoints": api_football_2025.get("summary", {}).get("successful_endpoints", 0),
            "api_football_2025_fixtures": endpoint_count(api_football_2025, "fixtures"),
            "api_football_2024_player_pool": len(api_football_analysis.get("player_attribute_pool", [])),
            "api_football_2024_deep_successful_endpoints": api_football_deep.get("summary", {}).get("successful_endpoints", 0),
            "api_football_2024_deep_squad_players": api_football_deep.get("summary", {}).get("squad_player_count", 0),
            "api_football_2024_deep_injuries": api_football_deep.get("summary", {}).get("injury_count", 0),
            "api_football_2024_deep_player_stat_rows": api_football_deep.get("summary", {}).get("player_stat_rows", 0),
            "api_football_2024_deep_combined_player_pool": api_football_deep_analysis.get("summary", {}).get("combined_player_pool", 0),
            "player_alias_entries": alias_quality.get("summary", {}).get("alias_players", 0),
            "alias_tff_transfermarkt_match_rate": alias_quality.get("comparisons", {}).get("league_tff_vs_transfermarkt", {}).get("match_rate", 0),
            "alias_tff_api_match_rate": alias_quality.get("comparisons", {}).get("scout_tff_vs_api_deep", {}).get("match_rate", 0),
        },
        "available_fields": [
            "team", "match_date", "score", "venue", "referee", "var", "lineup", "bench",
            "cards", "goals", "goal_minute", "goal_type", "player_tff_id", "birth_date",
            "age", "nationality", "contract_start", "contract_end", "player_position", "position_group", "market_value",
            "automatic_suspension_signal", "manual_injury_override", "manual_suspension_override",
            "external_current_ability", "external_potential_ability", "role_fit_score",
            "estimated_physical_load_km_range", "fm_role_archetype", "overall_fm_fit_score",
            "api_football_historical_fixtures", "api_football_top_scorers", "api_football_cards",
            "api_football_squads", "api_football_injury_history_signal", "api_football_player_season_stats",
            "player_alias_canonical_name", "cross_source_match_score",
            "transfermarkt_match_review_category", "transfermarkt_in_scope_match_rate",
            "recommended_scoreline", "top_scoreline_scenarios", "recommended_model_action",
            "lineup_recommendation", "attacking_priority", "card_caution",
            "team_strength_score", "attack_score", "defense_score", "form_score", "venue_score", "continuity_score",
            "big_match_volatility_score", "big_match_risk_level", "big_match_draw_risk",
            "coach_lineup_alignment_rate", "coach_lineup_verdict", "alternative_model_lineup_xg",
            "alternative_model_lineup_scoreline",
            "position_role_fit_score", "position_confidence", "scout_economy_score", "source_freshness_target",
            "team_power_score", "team_scoring_window", "team_conceding_window", "team_weakness_hint",
            "team_scout_blueprint_role", "team_scout_blueprint_candidate_fit",
            "scout_quality_low_confidence_queue", "scout_quality_repeated_role_spread",
            "sqlite_warehouse_table_counts", "warehouse_quality_findings",
            "profile_enrichment_priority_score", "profile_enrichment_queue_rank",
            "player_estimated_load_score", "player_profile_tag", "referee_tempo_label",
            "transfer_impact_simulated_xg_delta", "transfer_impact_simulated_scoreline", "selected_player_what_if",
            "news_injury_signal", "news_suspension_signal", "news_probable_lineup_context",
            "news_transfer_claim", "news_transfer_verification_status", "news_transfer_evidence_sources",
            "official_social_announcement_signal", "official_club_web_announcement_signal",
        ],
        "missing_fields": [
            "preferred_foot",
            "height_cm",
            "salary",
            "official_injury_history_feed",
            "transfer_fee_history",
            "event coordinates",
            "shots",
            "assists",
            "xG",
            "xA",
            "passes",
            "pressures",
            "tracking/running distance",
            "verified_fm_commercial_license",
            "api_football_2025_paid_plan_access",
        ],
        "product_readiness": {
            "match_previews": "MVP_READY",
            "goal_candidates": "PROMISING_MVP",
            "match_result_prediction": "IMPROVED_MVP_NEEDS_MORE_FEATURES",
            "big_match_risk_audit": "MVP_READY_RISK_LAYER",
            "scouting": "MVP_WITH_PARTIAL_POSITION_VALUE",
            "team_needs": "MVP_WITH_BESIKTAS_POSITION_VALUE",
            "availability": "MVP_AUTO_SUSPENSION_MANUAL_INJURY",
            "fm_style_attributes": "IMPORT_READY_NEEDS_LICENSED_DATASET",
            "fm_style_scout_program": "MVP_READY_DERIVED_ROLE_ENGINE",
            "position_scout_matrix": "MVP_READY_NEEDS_STRONGER_POSITION_DATA",
            "league_intelligence": "MVP_READY_DERIVED_TEAM_PLAYER_REFEREE_LAYER",
            "team_scout_blueprints": "MVP_READY_TEAM_WEAKNESS_TO_ROLE_TO_CANDIDATE",
            "scout_quality_report": "MVP_READY_REVIEW_QUEUE",
            "sqlite_warehouse": "MVP_READY_QUERYABLE_LOCAL_DATA_STORE",
            "profile_enrichment_queue": "MVP_READY_PRIORITY_COLLECTION_QUEUE",
            "source_watchlist": "MVP_READY_DAILY_REFRESH_PLAN",
            "news_context": "CONNECTED_LOW_TO_MEDIUM_CONFIDENCE",
            "transfer_news_intelligence": "RSS_CONNECTED_OFFICIAL_CLUB_WEB_CONNECTED_X_OPTIONAL_REVIEW_GATED",
            "api_football": "CONNECTED_2024_HISTORY_PLAN_LIMITED_2025",
        },
        "source_display_policy": {
            "internal_rule": "Her veri kaynağı içeride gerçek ad, lisans durumu, risk ve güven etiketiyle tutulur.",
            "public_rule": "Kullanıcıya yalnızca izinli kaynak adı veya genel kaynak kategorisi gösterilir; lisans/izin sorunu olan veri ticari ürüne alınmaz.",
            "blocked_rule": "Kaynağı gizleyerek lisans, robots, kullanım şartı veya telif riskini aşma yöntemi kullanılmaz.",
        },
    }


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def endpoint_count(snapshot: dict, label: str) -> int:
    for endpoint in snapshot.get("summary", {}).get("endpoints", []):
        if endpoint.get("label") == label:
            return endpoint.get("item_count") or 0
    return 0


def build_markdown(catalog: dict) -> str:
    coverage = catalog["coverage"]
    transfer_status = coverage.get("news_transfer_status_counts", {})
    lines = [
        "# Veri Kataloğu ve Kapsam Raporu",
        "",
        f"- Sezon: {catalog['season']}",
        f"- Maç: {coverage['matches']}",
        f"- Takım: {coverage['teams']}",
        f"- Maç kadrosunda benzersiz oyuncu: {coverage['unique_players_in_match_sheets']}",
        f"- Ana hakem: {coverage['main_referees']}",
        f"- İlk 11 kaydı: {coverage['starting_records']}",
        f"- Yedek kaydı: {coverage['bench_records']}",
        f"- Kart olayı: {coverage['cards']}",
        f"- Gol olayı: {coverage['goals']}",
        f"- Beşiktaş oyuncu profili: {coverage['besiktas_player_profiles']}",
        f"- Eski scout parça profil dosyası: {coverage['scout_shortlist_profiles']}",
        f"- Eski öncelikli profil parça dosyası: {coverage['priority_player_profiles']}",
        f"- Birleşik lig oyuncu profili: {coverage['league_player_profiles']}",
        f"- Transfermarkt Süper Lig kulübü: {coverage['transfermarkt_league_clubs']}/18",
        f"- Transfermarkt Süper Lig oyuncusu: {coverage['transfermarkt_league_players']}",
        f"- Transfermarkt Süper Lig toplam değer: €{coverage['transfermarkt_league_market_value_total_eur']:,}",
        f"- Transfermarkt oyuncu profil detayı/tam adı: {coverage['transfermarkt_profile_details_collected']}/{coverage['transfermarkt_profile_full_names']}",
        f"- TFF / Transfermarkt zenginleşen profil: {coverage['tff_tm_matched_profiles']}/{coverage['tff_tm_enriched_profiles']} (%{round(coverage['tff_tm_match_rate'] * 100)})",
        f"- TFF / Transfermarkt lig snapshot içi kapsama: {coverage['tff_tm_matched_profiles']}/{coverage['tff_tm_snapshot_in_scope_profiles']} (%{round(coverage['tff_tm_in_scope_match_rate'] * 100, 1)})",
        f"- TFF / Transfermarkt inceleme kuyruğu: {coverage['tff_tm_unmatched_profiles']} profil; scout bloke eden {coverage['tff_tm_scout_blocking_unmatched']}",
        f"- TFF / Transfermarkt yüksek kullanımlı çözülmemiş: {coverage['tff_tm_high_usage_unresolved']} profil",
        f"- Beşiktaş maç önü raporu: {coverage['besiktas_previews']}",
        f"- Tüm takım maç önü raporu: {coverage['all_teams_preview_reports']} ({coverage['all_teams_preview_teams']} takım)",
        f"- Gol adayı Top 3: %{round((coverage['goal_candidate_top3'] or 0) * 100)}",
        f"- Gol adayı Top 5: %{round((coverage['goal_candidate_top5'] or 0) * 100)}",
        f"- Gol adayı Top 8: %{round((coverage['goal_candidate_top8'] or 0) * 100)}",
        f"- Gol adayı Top 10: %{round((coverage['goal_candidate_top10'] or 0) * 100)}",
        f"- Beşiktaş maç önü sonuç tahmini: %{round((coverage['besiktas_match_prediction_accuracy'] or 0) * 100)}",
        f"- Beşiktaş taraf eğilimi isabeti: %{round((coverage['besiktas_actionable_prediction_accuracy'] or 0) * 100)}",
        f"- Beşiktaş büyük maç tahmini: %{round((coverage['besiktas_big_match_prediction_accuracy'] or 0) * 100)}",
        f"- Büyük maç risk raporu: {coverage['big_match_risk_reports']} maç",
        f"- Büyük maç MEDIUM/HIGH risk işareti: {coverage['big_match_medium_high_risk_count']}",
        f"- Tahmin hata analizi kaçan maç: {coverage['prediction_error_misses']}",
        f"- Tahmin hata analizi kaçan beraberlik: {coverage['prediction_error_missed_draws']}",
        f"- Lig tahmin doğruluğu: %{round((coverage['league_prediction_accuracy'] or 0) * 100)}",
        f"- Lig piyasa değeri audit kapsamı: {coverage['league_market_audit_covered_matches']} maç",
        f"- Lig piyasa değeri baseline doğruluğu: %{round((coverage['league_market_baseline_accuracy'] or 0) * 100)}",
        f"- Oyuncu uygunluk maç kapsamı: {coverage['availability_matches']}",
        f"- Eksik oyuncu sinyali olan maç: {coverage['availability_signal_matches']}",
        f"- Eksik oyuncu sinyali: {coverage['availability_unavailable_entries']}",
        f"- FM/FIFA tarzı attribute aday kaynağı: {coverage['attribute_candidate_sources']}",
        f"- Normalize attribute oyuncusu: {coverage['attribute_imported_players']}",
        f"- Current ability bulunan attribute oyuncusu: {coverage['attribute_matched_current_ability']}",
        f"- FM tarzı scout adayı: {coverage['fm_style_scout_candidates']}",
        f"- FM tarzı rol listesi: {coverage['fm_style_role_buckets']}",
        f"- Pozisyon scout rolü: {coverage['position_scout_roles']}",
        f"- Pozisyon scout rol-aday eşleşmesi: {coverage['position_scout_role_candidates']}",
        f"- Lig istihbarat takım profili: {coverage['league_intelligence_teams']}",
        f"- Lig istihbarat oyuncu profili: {coverage['league_intelligence_players']}",
        f"- Lig istihbarat hakem profili: {coverage['league_intelligence_referees']}",
        f"- Takım scout blueprint: {coverage['team_scout_blueprint_teams']} takım",
        f"- Takım scout aday bağlantısı: {coverage['team_scout_blueprint_candidate_links']}",
        f"- Scout düşük güven inceleme kuyruğu: {coverage['scout_quality_low_confidence_links']}",
        f"- Scout tekil düşük güven oyuncu-rol: {coverage['scout_quality_unique_low_confidence_player_roles']}",
        f"- Scout fazla role yayılan oyuncu: {coverage['scout_quality_repeated_role_players']}",
        f"- SQLite veri ambarı tablo sayısı: {coverage['warehouse_tables']}",
        f"- SQLite veri ambarı toplam satır: {coverage['warehouse_rows_total']}",
        f"- SQLite veri kalite bulgusu: {coverage['warehouse_quality_findings']}",
        f"- Profil zenginleştirme kuyruğu: {coverage['profile_enrichment_queue']}",
        f"- Profil zenginleştirme eksik aday: {coverage['profile_enrichment_missing_candidates']}",
        f"- İzlenen veri kaynağı: {coverage['source_watchlist_sources']}",
        f"- Günlük izlenecek kaynak: {coverage['source_watchlist_daily_sources']}",
        f"- Haber/sakat-cezalı başarılı kaynak: {coverage['news_context_sources_ok']}",
        f"- Haber/sakat-cezalı sinyal: {coverage['news_context_signals']}",
        f"- Haber/sakat-cezalı yapılandırılmış oyuncu: {coverage['news_context_structured_unavailability']}",
        f"- RSS haber kaydı: {coverage['news_rss_articles']}",
        (
            f"- Resmi kulüp web duyurusu: {coverage['news_official_articles']} | "
            f"erişilebilir site={coverage['news_official_successful_sources']}/"
            f"{coverage['news_official_configured_sources']} | durum={coverage['news_official_status']}"
        ),
        f"- Haber analizine alınan içerik: {coverage['news_intelligence_articles']}",
        (
            f"- Transfer haber iddiası: {coverage['news_transfer_claims']} | "
            f"resmi={transfer_status.get('OFFICIAL', 0)}, "
            f"çoklu kaynak={transfer_status.get('CORROBORATED', 0)}, "
            f"söylenti={transfer_status.get('RUMOR', 0)}, "
            f"inceleme gerekli={transfer_status.get('REVIEW_REQUIRED', 0)}"
        ),
        (
            f"- X gönderi snapshot'ı: {coverage['news_twitter_posts']} | "
            f"başarılı hesap={coverage['news_twitter_successful_accounts']} | "
            f"kaynak={coverage['news_twitter_provider']} | durum={coverage['news_twitter_status']}"
        ),
        f"- API-Football 2024 başarılı endpoint: {coverage['api_football_2024_successful_endpoints']}",
        f"- API-Football 2024 fikstür: {coverage['api_football_2024_fixtures']}",
        f"- API-Football 2024 takım: {coverage['api_football_2024_teams']}",
        f"- API-Football 2025 fikstür: {coverage['api_football_2025_fixtures']} (plan kısıtı olabilir)",
        f"- API-Football 2024 oyuncu attribute havuzu: {coverage['api_football_2024_player_pool']}",
        f"- API-Football 2024 derin başarılı endpoint: {coverage['api_football_2024_deep_successful_endpoints']}",
        f"- API-Football 2024 derin kadro oyuncusu: {coverage['api_football_2024_deep_squad_players']}",
        f"- API-Football 2024 derin sakatlık kaydı: {coverage['api_football_2024_deep_injuries']}",
        f"- API-Football 2024 derin oyuncu istatistik satırı: {coverage['api_football_2024_deep_player_stat_rows']}",
        f"- API-Football 2024 derin birleşik oyuncu havuzu: {coverage['api_football_2024_deep_combined_player_pool']}",
        f"- Manuel oyuncu alias kaydı: {coverage['player_alias_entries']}",
        f"- Alias lig geneli TFF/Transfermarkt eşleşme oranı: %{round(coverage['alias_tff_transfermarkt_match_rate'] * 100)}",
        f"- Alias scout TFF/Dış API eşleşme oranı: %{round(coverage['alias_tff_api_match_rate'] * 100)}",
        "",
        "## Kaynaklar",
        "",
    ]
    for source in catalog["sources"]:
        lines.append(
            f"- {source['name']} / public='{source['public_label']}' "
            f"({source['type']}, risk={source['risk']}, license={source['license_status']}): {source['coverage']}"
        )
    lines.extend(["", "## Kaynak Gösterim Politikası", ""])
    for _, policy in catalog["source_display_policy"].items():
        lines.append(f"- {policy}")
    lines.extend(["", "## Var Olan Alanlar", ""])
    lines.append(", ".join(catalog["available_fields"]))
    lines.extend(["", "## Eksik Kritik Alanlar", ""])
    for field in catalog["missing_fields"]:
        lines.append(f"- {field}")
    lines.extend(["", "## Ürün Hazırlık Durumu", ""])
    for area, status in catalog["product_readiness"].items():
        lines.append(f"- {area}: {status}")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
