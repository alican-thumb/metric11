# Yanlış Taraf / Side Flip Denetimi

- Yanlış taraf vakası: 5
- Korumalı aksiyon içindeki yanlış taraf: 4
- Korumalı olmayan yanlış taraf: 1
- Beşiktaş tarafını fazla değerleme: 2
- Rakibi fazla değerleme: 1
- Büyük maç taraf dönüşü: 1
- HIGH draw risk ama net sonuç: 3
- Rakip piyasa değeri kapsanan vaka: 4/5
- Ortalama Beşiktaş-rakip değer farkı: €78.78m
- Veri boşluğu dağılımı: {'odds_baseline_missing': 5, 'official_injury_feed_missing': 5, 'confirmed_lineup_quality_missing': 5, 'no_matchday_availability_signal': 4, 'opponent_market_value_missing': 1}
- Sinyal etiketi dağılımı: {'target_side_overrated': 2, 'model_xg_edge_overtrusted': 1, 'market_value_edge_supports_target': 2, 'opponent_side_overrated': 1, 'opponent_xg_edge_overtrusted': 1, 'high_draw_risk_but_decisive_result': 3, 'narrow_xg_decisive_result': 3, 'low_confidence_wrong_side': 3, 'big_match_side_flip': 1, 'availability_signal_present': 1}

## Okuma

- Bu rapor beraberlik uyarısını değil, taraf seçiminin tersine döndüğü maçları inceler.
- Rakip piyasa değeri snapshot'ı side flip vakaları için kapatıldı; kalan kritik boşluklar odds baseline, resmi sakatlık akışı ve doğrulanmış maç günü 11 kalitesidir.
- Piyasa değeri farkı tek başına taraf tahmini değildir; modelin xG/güç sinyaliyle çeliştiği maçlarda kalibrasyon kontrolü sağlar.

## Maçlar

- Hafta 9 | BEŞİKTAŞ A.Ş. - GENÇLERBİRLİĞİ | skor 1-2 | tahmin=Beşiktaş gerçek=Rakip | xG=1.96-0.99 edge=0.97 | strength_edge=0.136 | market_edge=€149.75m | eksik=- | risk=LOW 10 | etiket=target_side_overrated, model_xg_edge_overtrusted, market_value_edge_supports_target | veri_boşluğu=odds_baseline_missing, official_injury_feed_missing, confirmed_lineup_quality_missing, no_matchday_availability_signal
- Hafta 22 | RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ - BEŞİKTAŞ A.Ş. | skor 2-3 | tahmin=Rakip gerçek=Beşiktaş | xG=1.35-2.22 edge=-0.87 | strength_edge=-0.034 | market_edge=- | eksik=- | risk=MEDIUM 31 | etiket=opponent_side_overrated, opponent_xg_edge_overtrusted | veri_boşluğu=opponent_market_value_missing, odds_baseline_missing, official_injury_feed_missing, confirmed_lineup_quality_missing, no_matchday_availability_signal
- Hafta 23 | BEŞİKTAŞ A.Ş. - GÖZTEPE A.Ş. | skor 4-0 | tahmin=Beraberlik gerçek=Beşiktaş | xG=1.35-1.34 edge=0.01 | strength_edge=-0.005 | market_edge=€110.25m | eksik=- | risk=HIGH 100 | etiket=high_draw_risk_but_decisive_result, narrow_xg_decisive_result, low_confidence_wrong_side | veri_boşluğu=odds_baseline_missing, official_injury_feed_missing, confirmed_lineup_quality_missing, no_matchday_availability_signal
- Hafta 28 | FENERBAHÇE A.Ş. - BEŞİKTAŞ A.Ş. | skor 1-0 | tahmin=Beraberlik gerçek=Rakip | xG=1.63-1.76 edge=-0.13 | strength_edge=-0.018 | market_edge=€-64.8m | eksik=- | risk=HIGH 100 | etiket=big_match_side_flip, high_draw_risk_but_decisive_result, narrow_xg_decisive_result, low_confidence_wrong_side | veri_boşluğu=odds_baseline_missing, official_injury_feed_missing, confirmed_lineup_quality_missing, no_matchday_availability_signal
- Hafta 30 | SAMSUNSPOR A.Ş. - BEŞİKTAŞ A.Ş. | skor 2-1 | tahmin=Beşiktaş gerçek=Rakip | xG=1.64-1.58 edge=0.06 | strength_edge=0.097 | market_edge=€119.9m | eksik=EMİRHAN TOPÇU | risk=HIGH 89 | etiket=target_side_overrated, high_draw_risk_but_decisive_result, narrow_xg_decisive_result, low_confidence_wrong_side, availability_signal_present, market_value_edge_supports_target | veri_boşluğu=odds_baseline_missing, official_injury_feed_missing, confirmed_lineup_quality_missing