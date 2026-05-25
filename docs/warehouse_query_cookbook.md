# Metric11 SQLite Sorgu Rehberi

Bu dosya `data/processed/metric11_warehouse.sqlite` veri ambarı için hızlı sorgu örneklerini tutar.

## Açılış

```bash
sqlite3 data/processed/metric11_warehouse.sqlite
```

## Hazır Görünümler

```sql
SELECT * FROM v_team_power_ranking LIMIT 10;
SELECT * FROM v_referee_card_risk LIMIT 10;
SELECT * FROM v_player_load_leaders LIMIT 20;
SELECT * FROM v_besiktas_scout_blueprint LIMIT 20;
```

## Beşiktaş İçin Scout Blueprint

```sql
SELECT
  role_label,
  candidate_name,
  candidate_team,
  candidate_age,
  contract_months_left,
  resale_signal,
  contract_risk,
  verified_position,
  height_cm,
  preferred_foot,
  position_source,
  fit_score,
  estimated_load_min,
  estimated_load_max,
  position_confidence
FROM team_scout_blueprints
WHERE team_name = 'BEŞİKTAŞ A.Ş.'
ORDER BY role_key, candidate_rank;
```

## Hakem Kart Riski

```sql
SELECT
  referee_name,
  matches,
  cards_per_match,
  goals_per_match,
  draw_rate,
  tempo_label
FROM referee_profiles
WHERE matches >= 3
ORDER BY cards_per_match DESC;
```

## Oyuncu Yük ve Kart Profili

```sql
SELECT
  player_name,
  team_name,
  starts,
  goals,
  cards,
  estimated_load_score,
  profile_tag
FROM player_profiles
WHERE starts >= 20
ORDER BY estimated_load_score DESC;
```

## Maç Tahmini Hataları

```sql
SELECT
  date,
  fixture,
  actual_score,
  predicted,
  actual,
  recommended_action,
  card_signal,
  is_big_match
FROM match_predictions
WHERE correct = 0
ORDER BY date;
```

## Gol Adayı Kontrolü

```sql
SELECT
  match_external_id,
  rank,
  player_name,
  candidate_type,
  goal_threat_score,
  actual_scorer
FROM goal_candidates
WHERE rank <= 8
ORDER BY match_external_id, rank;
```

## Veri Kalite Açıkları

```sql
SELECT severity, area, finding, count_value, recommendation
FROM data_quality_findings
ORDER BY id;
```
