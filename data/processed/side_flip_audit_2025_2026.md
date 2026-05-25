# Yanlış Taraf / Side Flip Denetimi

- Yanlış taraf vakası: 3
- Korumalı aksiyon içindeki yanlış taraf: 2
- Korumalı olmayan yanlış taraf: 1
- Beşiktaş tarafını fazla değerleme: 1
- Rakibi fazla değerleme: 1
- Büyük maç taraf dönüşü: 0
- HIGH draw risk ama net sonuç: 2
- Rakip piyasa değeri kapsanan vaka: 3/3
- Ortalama Beşiktaş-rakip değer farkı: €124.18m
- Veri boşluğu dağılımı: {'odds_baseline_missing': 3, 'official_injury_feed_missing': 3, 'confirmed_lineup_quality_missing': 3, 'no_matchday_availability_signal': 2}
- Sinyal etiketi dağılımı: {'target_side_overrated': 1, 'model_xg_edge_overtrusted': 1, 'market_value_edge_supports_target': 1, 'opponent_side_overrated': 1, 'high_draw_risk_but_decisive_result': 2, 'low_confidence_wrong_side': 2, 'opponent_xg_edge_overtrusted': 1, 'narrow_xg_decisive_result': 1, 'availability_signal_present': 1}

## Okuma

- Bu rapor beraberlik uyarısını değil, taraf seçiminin tersine döndüğü maçları inceler.
- Rakip piyasa değeri snapshot'ı side flip vakaları için kapatıldı; kalan kritik boşluklar odds baseline, resmi sakatlık akışı ve doğrulanmış maç günü 11 kalitesidir.
- Piyasa değeri farkı tek başına taraf tahmini değildir; modelin xG/güç sinyaliyle çeliştiği maçlarda kalibrasyon kontrolü sağlar.

## Maçlar

- Hafta 9 | BEŞİKTAŞ A.Ş. - GENÇLERBİRLİĞİ | skor 1-2 | tahmin=Beşiktaş gerçek=Rakip | xG=1.91-0.98 edge=0.93 | strength_edge=0.136 | market_edge=€149.75m | eksik=- | risk=LOW 10 | etiket=target_side_overrated, model_xg_edge_overtrusted, market_value_edge_supports_target | veri_boşluğu=odds_baseline_missing, official_injury_feed_missing, confirmed_lineup_quality_missing, no_matchday_availability_signal
- Hafta 22 | RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ - BEŞİKTAŞ A.Ş. | skor 2-3 | tahmin=Rakip gerçek=Beşiktaş | xG=1.35-1.94 edge=-0.59 | strength_edge=-0.034 | market_edge=€102.9m | eksik=- | risk=HIGH 49 | etiket=opponent_side_overrated, high_draw_risk_but_decisive_result, low_confidence_wrong_side, opponent_xg_edge_overtrusted | veri_boşluğu=odds_baseline_missing, official_injury_feed_missing, confirmed_lineup_quality_missing, no_matchday_availability_signal
- Hafta 30 | SAMSUNSPOR A.Ş. - BEŞİKTAŞ A.Ş. | skor 2-1 | tahmin=Beraberlik gerçek=Rakip | xG=1.54-1.53 edge=0.01 | strength_edge=0.097 | market_edge=€119.9m | eksik=EMİRHAN TOPÇU | risk=HIGH 97 | etiket=high_draw_risk_but_decisive_result, narrow_xg_decisive_result, low_confidence_wrong_side, availability_signal_present | veri_boşluğu=odds_baseline_missing, official_injury_feed_missing, confirmed_lineup_quality_missing