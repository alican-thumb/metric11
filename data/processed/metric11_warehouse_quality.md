# Metric11 SQLite Veri Ambarı Kalite Raporu

- Dosya: `/home/runner/work/metric11/metric11/data/processed/metric11_warehouse.sqlite`

## Tablo Sayıları

- data_quality_findings: 6
- data_sources: 5
- goal_candidates: 298
- match_cards: 1428
- match_goals: 812
- match_lineups: 12732
- match_predictions: 29
- matches: 306
- player_profiles: 691
- players: 691
- referee_profiles: 29
- referees: 29
- team_profiles: 18
- team_scout_blueprints: 370
- teams: 18

## Hazır Görünümler

- v_besiktas_scout_blueprint
- v_player_load_leaders
- v_referee_card_risk
- v_team_power_ranking

## Kalite Bulguları

- LOW / matches: Warehouse match rows loaded = 306 -> Bu sayı sezon kapsamıyla tutarlı kalmalı.
- LOW / referees: Matches missing main referee = 0 -> Eksikse TFF parser veya kaynak değişimi kontrol edilmeli.
- LOW / players: Players without age/profile enrichment = 0 -> TFF/Transfermarkt/API profil toplama kapsamı genişletilmeli.
- LOW / scouting: Blueprint candidates with low proxy position confidence = 0 -> Doğrudan pozisyon, boy, ayak ve aksiyon verisiyle güçlendirilmeli.
- MEDIUM / predictions: Beşiktaş match prediction accuracy percent = 55 -> Daha fazla sezon, sakatlık ve odds baseline ile kalibre edilmeli.
- LOW / goal_candidates: Goal candidate rows loaded = 298 -> Top 8/10 performansı ürün için güçlü sinyal.

## Örnek Sorgu Çıktıları

### top_team_power
- {'team_name': 'GALATASARAY A.Ş.', 'overall_power_score': 84.4, 'points_per_match': 2.26}
- {'team_name': 'FENERBAHÇE A.Ş.', 'overall_power_score': 76.5, 'points_per_match': 2.18}
- {'team_name': 'RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ', 'overall_power_score': 73.3, 'points_per_match': 1.68}
- {'team_name': 'TRABZONSPOR A.Ş.', 'overall_power_score': 68.6, 'points_per_match': 2.03}
- {'team_name': 'BEŞİKTAŞ A.Ş.', 'overall_power_score': 62.5, 'points_per_match': 1.76}

### besiktas_blueprint
- {'role_label': 'Bek / çift yönlü koridor', 'candidate_name': 'YHOAN MANY ANDZOUANA', 'candidate_team': 'TÜMOSAN KONYASPOR', 'fit_score': 110.2, 'position_confidence': 'MEDIUM_DERIVED_ROLE'}
- {'role_label': 'Bek / çift yönlü koridor', 'candidate_name': 'ROLAND SALLAI', 'candidate_team': 'GALATASARAY A.Ş.', 'fit_score': 101.9, 'position_confidence': 'MEDIUM_DERIVED_ROLE'}
- {'role_label': 'Bek / çift yönlü koridor', 'candidate_name': 'RUAN PEREIRA DUARTE', 'candidate_team': 'CORENDON ALANYASPOR', 'fit_score': 100.9, 'position_confidence': 'MEDIUM_DERIVED_ROLE'}
- {'role_label': 'Bek / çift yönlü koridor', 'candidate_name': 'ZEKİ YAVRU', 'candidate_team': 'SAMSUNSPOR A.Ş.', 'fit_score': 97.2, 'position_confidence': 'MEDIUM_DERIVED_ROLE'}
- {'role_label': 'Bek / çift yönlü koridor', 'candidate_name': 'WAGNER FABRICIO CARDOSO DE PINA', 'candidate_team': 'TRABZONSPOR A.Ş.', 'fit_score': 87.03, 'position_confidence': 'MEDIUM_EXTERNAL'}
- {'role_label': 'Sol açık / çizgi kırıcı', 'candidate_name': 'YUNUS AKGÜN', 'candidate_team': 'GALATASARAY A.Ş.', 'fit_score': 104.95, 'position_confidence': 'MEDIUM_EXTERNAL'}
- {'role_label': 'Sol açık / çizgi kırıcı', 'candidate_name': 'BARIŞ ALPER YILMAZ', 'candidate_team': 'GALATASARAY A.Ş.', 'fit_score': 99.7, 'position_confidence': 'MEDIUM_EXTERNAL'}
- {'role_label': 'Sol açık / çizgi kırıcı', 'candidate_name': 'KAZEEM ADEREMI J. OLAIGBE', 'candidate_team': 'TRABZONSPOR A.Ş.', 'fit_score': 97.06, 'position_confidence': 'MEDIUM_EXTERNAL'}
- {'role_label': 'Sol açık / çizgi kırıcı', 'candidate_name': 'GÖKTAN GÜRPÜZ', 'candidate_team': 'GENÇLERBİRLİĞİ', 'fit_score': 95.73, 'position_confidence': 'MEDIUM_EXTERNAL'}
- {'role_label': 'Sol açık / çizgi kırıcı', 'candidate_name': 'DORGELES NENE', 'candidate_team': 'FENERBAHÇE A.Ş.', 'fit_score': 95.33, 'position_confidence': 'MEDIUM_EXTERNAL'}

### card_heavy_referees
- {'referee_name': 'FATİH TOKAİL', 'cards_per_match': 9.0, 'tempo_label': 'KARTLI'}
- {'referee_name': 'ERDEM MERTOĞLU', 'cards_per_match': 6.67, 'tempo_label': 'KARTLI'}
- {'referee_name': 'GÜRCAN HASOVA', 'cards_per_match': 6.17, 'tempo_label': 'KARTLI'}
- {'referee_name': 'KADİR SAĞLAM', 'cards_per_match': 5.93, 'tempo_label': 'KARTLI'}
- {'referee_name': 'ARDA KARDEŞLER', 'cards_per_match': 5.67, 'tempo_label': 'KARTLI'}
