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
- team_scout_blueprints: 310
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
- MEDIUM / scouting: Blueprint candidates with low proxy position confidence = 34 -> Doğrudan pozisyon, boy, ayak ve aksiyon verisiyle güçlendirilmeli.
- MEDIUM / predictions: Beşiktaş match prediction accuracy percent = 65 -> Daha fazla sezon, sakatlık ve odds baseline ile kalibre edilmeli.
- LOW / goal_candidates: Goal candidate rows loaded = 298 -> Top 8/10 performansı ürün için güçlü sinyal.

## Örnek Sorgu Çıktıları

### top_team_power
- {'team_name': 'GALATASARAY A.Ş.', 'overall_power_score': 84.4, 'points_per_match': 2.26}
- {'team_name': 'FENERBAHÇE A.Ş.', 'overall_power_score': 76.5, 'points_per_match': 2.18}
- {'team_name': 'RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ', 'overall_power_score': 73.3, 'points_per_match': 1.68}
- {'team_name': 'TRABZONSPOR A.Ş.', 'overall_power_score': 68.6, 'points_per_match': 2.03}
- {'team_name': 'BEŞİKTAŞ A.Ş.', 'overall_power_score': 62.5, 'points_per_match': 1.76}

### besiktas_blueprint
- {'role_label': 'Bek / çift yönlü koridor', 'candidate_name': 'ALEXANDRU IULIAN MAXIM', 'candidate_team': 'GAZİANTEP FUTBOL KULÜBÜ A.Ş.', 'fit_score': 127.7, 'position_confidence': 'MEDIUM_DERIVED_ROLE'}
- {'role_label': 'Bek / çift yönlü koridor', 'candidate_name': 'MATEUSZ LIS', 'candidate_team': 'GÖZTEPE A.Ş.', 'fit_score': 124.4, 'position_confidence': 'MEDIUM_DERIVED_ROLE'}
- {'role_label': 'Bek / çift yönlü koridor', 'candidate_name': 'ANDREAS GIANNIOTIS', 'candidate_team': 'KASIMPAŞA A.Ş.', 'fit_score': 123.3, 'position_confidence': 'MEDIUM_DERIVED_ROLE'}
- {'role_label': 'Bek / çift yönlü koridor', 'candidate_name': 'KENNETH IMMANUEL PAAL', 'candidate_team': 'HESAP.COM ANTALYASPOR', 'fit_score': 119.9, 'position_confidence': 'MEDIUM_DERIVED_ROLE'}
- {'role_label': 'Bek / çift yönlü koridor', 'candidate_name': 'IVO  GRBIC', 'candidate_team': 'MISIRLI.COM.TR FATİH KARAGÜMRÜK', 'fit_score': 117.8, 'position_confidence': 'MEDIUM_DERIVED_ROLE'}
- {'role_label': 'Sol açık / çizgi kırıcı', 'candidate_name': 'KACPER SZYMON KOZLOWSKI', 'candidate_team': 'GAZİANTEP FUTBOL KULÜBÜ A.Ş.', 'fit_score': 112.62, 'position_confidence': 'HIGH'}
- {'role_label': 'Sol açık / çizgi kırıcı', 'candidate_name': 'DORGELES NENE', 'candidate_team': 'FENERBAHÇE A.Ş.', 'fit_score': 95.84, 'position_confidence': 'HIGH'}
- {'role_label': 'Sol açık / çizgi kırıcı', 'candidate_name': 'BARIŞ ALPER YILMAZ', 'candidate_team': 'GALATASARAY A.Ş.', 'fit_score': 94.66, 'position_confidence': 'HIGH'}
- {'role_label': 'Sol açık / çizgi kırıcı', 'candidate_name': 'ERNEST MUÇİ', 'candidate_team': 'TRABZONSPOR A.Ş.', 'fit_score': 92.54, 'position_confidence': 'HIGH'}
- {'role_label': 'Sol açık / çizgi kırıcı', 'candidate_name': 'KAZEEM ADEREMI J. OLAIGBE', 'candidate_team': 'TRABZONSPOR A.Ş.', 'fit_score': 92.39, 'position_confidence': 'HIGH'}

### card_heavy_referees
- {'referee_name': 'FATİH TOKAİL', 'cards_per_match': 9.0, 'tempo_label': 'KARTLI'}
- {'referee_name': 'ERDEM MERTOĞLU', 'cards_per_match': 6.67, 'tempo_label': 'KARTLI'}
- {'referee_name': 'GÜRCAN HASOVA', 'cards_per_match': 6.17, 'tempo_label': 'KARTLI'}
- {'referee_name': 'KADİR SAĞLAM', 'cards_per_match': 5.93, 'tempo_label': 'KARTLI'}
- {'referee_name': 'ARDA KARDEŞLER', 'cards_per_match': 5.67, 'tempo_label': 'KARTLI'}
