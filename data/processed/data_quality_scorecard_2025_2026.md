# Veri Kalite ve İstatistik Scorecard

- Ambar: `/home/runner/work/metric11/metric11/data/processed/metric11_warehouse.sqlite`
- Genel skor: 84.1/100

## Kontroller

| Alan | Metrik | Değer | Durum | Öncelik | Öneri |
|---|---|---:|---|---|---|
| coverage | season_match_rows | 306 | ✓ | Düşük | Sezon kapsamı 306 maç civarında kalmalı; düşüş olursa collector/parser kontrol edilmeli. |
| coverage | matches_missing_referee | 0 | ✓ | Düşük | Hakem eksikleri kart ve büyük maç risk modelini doğrudan zayıflatır. |
| player_profiles | players_missing_age_profile | missing=0, total=691, missing_pct=0.0 | ✓ | Düşük | Yaş/profil kapsamı scout ve kontrat fırsatı skorunun temel girdisi. |
| player_profiles | tff_transfermarkt_in_scope_match_rate_pct | matched=498, in_scope=626, pct=79.6 | ⚠ İzle | Yüksek | Snapshot kapsamındaki eşleşmeyen oyuncular alias/transfer inceleme kuyruğunda doğrulanmadan piyasa değeri veya pozisyon olarak kullanılmamalı. |
| scouting | unmatched_players_blocking_scout_review | 0 | ✓ | Düşük | Scout kuyruğunu bloke eden oyuncular için aynı kulüp Transfermarkt adı veya resmi profil doğrulanmalı; doğrulanmadan rol önerisi yayınlanmamalı. |
| model | besiktas_display_prediction_accuracy_pct | correct=19, total=29, pct=65.5 | ⚠ İzle | Yüksek | Ekran ayarı aynı sezonda geliştirildi; yeni sezon veya ayrılmış sezonda sabit kurallarla doğrulanmadan genel başarı iddiası yapılmamalı. |
| model | draw_recall_pct | draw_predicted=2, draw_total=9, pct=22.2 | ⚠ İzle | Yüksek | Beraberlik sadece çok yüksek risk ve dar olasılık farkında ekran tahminine çekilmeli; diğer durumlarda korumalı senaryo dili kullanılmalı. |
| calibration | wrong_predictions_with_high_confidence_pct | wrong_high_confidence=1, wrong_total=10, pct=10.0 | ✓ | Orta | Yüksek güvenli hatalarda xG farkı, büyük maç ve beraberlik risk bayrakları güveni aşağı çekmeli. |
| goal_candidates | top_5_hit_pct | hits=20, matches=26, pct=76.9 | ⚠ İzle | Orta | Aday tipleri ayrı backtest edilmeli: primary, penaltı, duran top/defans ve yedek etki. |
| goal_candidates | top_8_hit_pct | hits=22, matches=26, pct=84.6 | ⚠ İzle | Orta | Aday tipleri ayrı backtest edilmeli: primary, penaltı, duran top/defans ve yedek etki. |
| scouting | low_position_confidence_pct | low_confidence=0, total=275, pct=0.0 | ✓ | Orta | Düşük güvenli scout adayları doğrudan pozisyon, boy, ayak ve aksiyon verisiyle zenginleştirilmeli. |

## Öncelikli Aksiyonlar

- **Yüksek öncelik** — model / besiktas_display_prediction_accuracy_pct: Ekran ayarı aynı sezonda geliştirildi; yeni sezon veya ayrılmış sezonda sabit kurallarla doğrulanmadan genel başarı iddiası yapılmamalı.
- **Yüksek öncelik** — model / draw_recall_pct: Beraberlik sadece çok yüksek risk ve dar olasılık farkında ekran tahminine çekilmeli; diğer durumlarda korumalı senaryo dili kullanılmalı.
- **Yüksek öncelik** — player_profiles / tff_transfermarkt_in_scope_match_rate_pct: Snapshot kapsamındaki eşleşmeyen oyuncular alias/transfer inceleme kuyruğunda doğrulanmadan piyasa değeri veya pozisyon olarak kullanılmamalı.
- **Orta öncelik** — goal_candidates / top_5_hit_pct: Aday tipleri ayrı backtest edilmeli: primary, penaltı, duran top/defans ve yedek etki.
- **Orta öncelik** — goal_candidates / top_8_hit_pct: Aday tipleri ayrı backtest edilmeli: primary, penaltı, duran top/defans ve yedek etki.

## Tahmin Karışıklık Matrisi

- tahmin=draw gerçek=draw: 2 maç
- tahmin=draw gerçek=opponent_win: 1 maç
- tahmin=opponent_win gerçek=draw: 1 maç
- tahmin=opponent_win gerçek=opponent_win: 4 maç
- tahmin=opponent_win gerçek=target_win: 1 maç
- tahmin=target_win gerçek=draw: 6 maç
- tahmin=target_win gerçek=opponent_win: 1 maç
- tahmin=target_win gerçek=target_win: 13 maç

## Gol Adayı Segmentleri

- primary+impact_sub: 134 satır, 19 isabet satırı, %14.2
- primary: 106 satır, 12 isabet satırı, %11.3
- impact_sub: 26 satır, 4 isabet satırı, %15.4
- primary+set_piece_defender: 24 satır, 0 isabet satırı, %0.0
- unknown: 8 satır, 2 isabet satırı, %25.0

## Scout Pozisyon Güveni

- MEDIUM_DERIVED_ROLE: 182
- MEDIUM_EXTERNAL: 65
- HIGH_EXTERNAL_PROFILE: 28

## Tablo Kapsamı

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
- team_scout_blueprints: 275
- teams: 18