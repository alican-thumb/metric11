# Metric11 SQLite Veri Ambarı Kalite Raporu

- Dosya: `/home/runner/work/metric11/metric11/data/processed/metric11_warehouse.sqlite`

## Tablo Sayıları

- data_quality_findings: 6
- data_sources: 5
- goal_candidates: 298
- match_cards: 0
- match_goals: 0
- match_lineups: 0
- match_predictions: 29
- matches: 306
- player_profiles: 0
- players: 691
- referee_profiles: 0
- referees: 0
- team_profiles: 18
- team_scout_blueprints: 0
- teams: 18

## Hazır Görünümler

- v_besiktas_scout_blueprint
- v_player_load_leaders
- v_referee_card_risk
- v_team_power_ranking

## Kalite Bulguları

- LOW / matches: Warehouse match rows loaded = 306 -> Bu sayı sezon kapsamıyla tutarlı kalmalı.
- MEDIUM / referees: Matches missing main referee = 306 -> Eksikse TFF parser veya kaynak değişimi kontrol edilmeli.
- LOW / players: Players without age/profile enrichment = 0 -> TFF/Transfermarkt/API profil toplama kapsamı genişletilmeli.
- LOW / scouting: Blueprint candidates with low proxy position confidence = 0 -> Doğrudan pozisyon, boy, ayak ve aksiyon verisiyle güçlendirilmeli.
- MEDIUM / predictions: Beşiktaş match prediction accuracy percent = 55 -> Daha fazla sezon, sakatlık ve odds baseline ile kalibre edilmeli.
- LOW / goal_candidates: Goal candidate rows loaded = 298 -> Top 8/10 performansı ürün için güçlü sinyal.

## Örnek Sorgu Çıktıları

### top_team_power
- {'team_name': 'GALATASARAY A.Ş.', 'overall_power_score': 48.7, 'points_per_match': 1.0}
- {'team_name': 'ÇORUM FK', 'overall_power_score': 48.7, 'points_per_match': 1.0}
- {'team_name': 'KASIMPAŞA A.Ş.', 'overall_power_score': 48.7, 'points_per_match': 1.0}
- {'team_name': 'TRABZONSPOR A.Ş.', 'overall_power_score': 48.7, 'points_per_match': 1.0}
- {'team_name': 'KONYASPOR', 'overall_power_score': 48.7, 'points_per_match': 1.0}

### besiktas_blueprint

### card_heavy_referees
