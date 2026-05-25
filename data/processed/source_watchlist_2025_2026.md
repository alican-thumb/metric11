# Veri Kaynak İzleme Listesi

- Güncelleme: 2026-05-25
- Kaynak sayısı: 11
- Bağlı/yarı bağlı kaynak: 4
- Planlanan/araştırılacak kaynak: 5
- Analizde yüksek ağırlıklı kaynak: 3

## Politika

- Her kaynak gerçek adı, URL'i, veri alanı, lisans durumu, risk ve güncellik ritmiyle içeride tutulur.
- Ürün arayüzünde yalnızca izinli kaynak adı veya genel kaynak kategorisi gösterilir.
- Kaynak gizleyerek lisans, robots, kullanım şartı veya telif riskini aşma yöntemi kullanılmaz.

## Kaynaklar

- TFF maç detayları (official_match_data): durum=connected, risk=medium, güncellik=daily_during_season, ağırlık=core, alanlar=fixture, score, lineup, bench, goals, cards, referee
- TFF oyuncu profilleri (official_player_profiles): durum=connected, risk=medium, güncellik=weekly_and_transfer_window_daily, ağırlık=core, alanlar=birth_date, age, nationality, license_no, club, contract_start, contract_end
- Transfermarkt squad pages (market_value_and_squad): durum=connected_super_lig_snapshot_2025_2026, risk=high, güncellik=weekly_and_transfer_window_daily_subject_to_terms, ağırlık=high_internal, alanlar=position, position_group, age, contract_until, market_value, profile_url
- beIN SPORTS / LigTV news and match context (news_context): durum=planned, risk=medium, güncellik=daily, ağırlık=context_only, alanlar=injury_news, suspension_news, transfer_news, manager_quotes, probable_lineups
- API-Football (external_api): durum=connected_2024_plan_limited_2025, risk=medium, güncellik=daily_if_plan_allows, ağırlık=validation_and_enrichment, alanlar=fixtures, standings, squads, player_stats, top_scorers, cards, injuries
- football-data.org (external_api): durum=collector_available_needs_key_and_competition_mapping, risk=low_medium, güncellik=daily, ağırlık=supporting, alanlar=matches, standings, teams, scorers
- Football-Data.co.uk (historical_results_and_odds): durum=collector_available, risk=low_medium, güncellik=weekly, ağırlık=model_training, alanlar=historical_results, odds, shots_if_available, cards_if_available
- StatsBomb Open Data (open_event_data): durum=planned, risk=low_medium, güncellik=monthly, ağırlık=model_training, alanlar=event_coordinates, shots, passes, pressures, xg_training_examples
- openfootball datasets (open_reference_data): durum=planned, risk=low, güncellik=monthly, ağırlık=reference, alanlar=clubs, players, leagues, fixtures
- Reep register / entity ID crosswalk (entity_resolution): durum=research_needed, risk=low_medium, güncellik=weekly_if_usable, ağırlık=infrastructure, alanlar=player_provider_ids, team_provider_ids, cross_source_identity
- Süper Lig and club forums/social news (community_signal): durum=planned, risk=medium, güncellik=daily_transfer_window, ağırlık=weak_signal_only, alanlar=rumor, fan_sentiment, emerging_young_players, transfer_links

## Günlük Veri Önceliği

- TFF maç detayları: daily_during_season / match_preview, score_prediction, goal_candidates, availability
- TFF oyuncu profilleri: weekly_and_transfer_window_daily / team_needs, contract_risk, resale_signal, scout_filtering
- Transfermarkt squad pages: weekly_and_transfer_window_daily_subject_to_terms / team_needs, market_value, position_mapping, transfer_window_tracking
- API-Football: daily_if_plan_allows / external_validation, player_quality_signal, injury_history, scout_enrichment
- Süper Lig and club forums/social news: daily_transfer_window / scout_watchlist_ideas, rumor_context, manual_review_queue
- beIN SPORTS / LigTV news and match context: daily / availability_manual_review, lineup_context, transfer_window_context, narrative_analysis
- football-data.org: daily / cross_check_scores, fixture_validation, league_expansion