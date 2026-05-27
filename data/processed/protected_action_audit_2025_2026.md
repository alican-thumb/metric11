# Korumalı Tahmin Aksiyonu Denetimi

- Test edilen Beşiktaş maçı: 29
- Korumalı aksiyon verilen maç: 19 (%65.5)
- Korumalı aksiyonda gerçek beraberlik: 5/19 (%26.3)
- Korumalı aksiyonda taraf tahmini doğru kalan maç: 10/19 (%52.6)
- Korumalı aksiyonda taraf tahmini yanlış/beraberlik dışı maç: 4
- HIGH risk korumalı maç: 14 | gerçek beraberlik: 4
- Aksiyon dağılımı: {'PROTECT_SIDE_PICK_SHOW_DRAW_SCENARIO': 14, 'KEEP_MAIN_PICK': 10, 'KEEP_PICK_WITH_DRAW_WARNING': 5}
- Korumalı aksiyon gerçek sonuç dağılımı: {'target_win': 9, 'opponent_win': 5, 'draw': 5}
- Beraberlik dışı yanlış taraf etiketleri: {'opponent_side_overrated': 1, 'high_draw_risk_but_decisive_result': 3, 'narrow_xg_decisive_result': 3, 'low_confidence_wrong_side': 3, 'big_match_side_flip': 1, 'target_side_overrated': 1}

## Okuma

- Bu rapor ana 1X2 doğruluğunu yeniden skorlamaz; aksiyon katmanının kullanıcıya ne kadar temkinli dil kazandırdığını ölçer.
- Korumalı aksiyonun amacı beraberliği kesin tahmin etmek değil, taraf tahmininde beraberlik senaryosunu görünür yapmaktır.
- Beraberlik dışı yanlışlar, yeni veri ihtiyacını gösterir: odds, sakatlık, kadro değeri, oyun akışı ve derbi tempo verisi.

## Korumalı Aksiyon Verilen Maçlar

- Hafta 3 | 22.10.2025 - 20:00 | TÜMOSAN KONYASPOR - BEŞİKTAŞ A.Ş. | skor 0-2 | tahmin=Beşiktaş gerçek=Beşiktaş | aksiyon=Korumalı taraf tahmini | risk=HIGH 58 | neden=xg_margin_watch, top_draw_scoreline, probability_margin_watch, strength_edge_very_narrow, low_confidence_side_pick, draw_calibration_medium
- Hafta 11 | 2.11.2025 - 20:00 | BEŞİKTAŞ A.Ş. - FENERBAHÇE A.Ş. | skor 2-3 | tahmin=Rakip gerçek=Rakip | aksiyon=Korumalı taraf tahmini | risk=HIGH 95 | neden=draw_probability_live, xg_margin_watch, top_draw_scoreline, probability_margin_narrow, strength_edge_very_narrow, low_confidence_side_pick, draw_calibration_high, big_match_high_volatility
- Hafta 12 | 8.11.2025 - 20:00 | HESAP.COM ANTALYASPOR - BEŞİKTAŞ A.Ş. | skor 1-3 | tahmin=Beşiktaş gerçek=Beşiktaş | aksiyon=Korumalı taraf tahmini | risk=HIGH 55 | neden=draw_probability_watch, xg_margin_watch, top_draw_scoreline, strength_edge_very_narrow, low_confidence_side_pick
- Hafta 13 | 23.11.2025 - 17:00 | BEŞİKTAŞ A.Ş. - SAMSUNSPOR A.Ş. | skor 1-1 | tahmin=Beraberlik gerçek=Beraberlik | aksiyon=Korumalı taraf tahmini | risk=HIGH 100 | neden=draw_probability_watch, xg_margin_very_narrow, top_draw_scoreline, probability_margin_very_narrow, strength_edge_very_narrow, low_confidence_side_pick, draw_calibration_high
- Hafta 14 | 30.11.2025 - 20:00 | MISIRLI.COM.TR FATİH KARAGÜMRÜK - BEŞİKTAŞ A.Ş. | skor 0-2 | tahmin=Beşiktaş gerçek=Beşiktaş | aksiyon=Korumalı taraf tahmini | risk=HIGH 76 | neden=draw_probability_watch, xg_margin_narrow, top_draw_scoreline, probability_margin_watch, strength_edge_very_narrow, low_confidence_side_pick, draw_calibration_medium
- Hafta 15 | 8.12.2025 - 20:00 | BEŞİKTAŞ A.Ş. - GAZİANTEP FUTBOL KULÜBÜ A.Ş. | skor 2-2 | tahmin=Beşiktaş gerçek=Beraberlik | aksiyon=Beraberlik uyarılı tahmin | risk=MEDIUM 28 | neden=top_draw_scoreline, strength_edge_very_narrow, medium_confidence_side_pick, draw_calibration_medium, strong_side_probability_penalty
- Hafta 16 | 14.12.2025 - 20:00 | TRABZONSPOR A.Ş. - BEŞİKTAŞ A.Ş. | skor 3-3 | tahmin=Rakip gerçek=Beraberlik | aksiyon=Korumalı taraf tahmini | risk=HIGH 57 | neden=xg_margin_watch, top_draw_scoreline, probability_margin_narrow, strength_edge_very_narrow, low_confidence_side_pick
- Hafta 21 | 8.02.2026 - 20:00 | BEŞİKTAŞ A.Ş. - CORENDON ALANYASPOR | skor 2-2 | tahmin=Beşiktaş gerçek=Beraberlik | aksiyon=Korumalı taraf tahmini | risk=HIGH 55 | neden=draw_probability_watch, xg_margin_watch, top_draw_scoreline, strength_edge_very_narrow, low_confidence_side_pick
- Hafta 22 | 15.02.2026 - 20:00 | RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ - BEŞİKTAŞ A.Ş. | skor 2-3 | tahmin=Rakip gerçek=Beşiktaş | aksiyon=Beraberlik uyarılı tahmin | risk=MEDIUM 31 | neden=draw_scoreline_top_two, strength_edge_very_narrow, medium_confidence_side_pick, draw_calibration_medium
- Hafta 23 | 22.02.2026 - 20:00 | BEŞİKTAŞ A.Ş. - GÖZTEPE A.Ş. | skor 4-0 | tahmin=Beraberlik gerçek=Beşiktaş | aksiyon=Korumalı taraf tahmini | risk=HIGH 100 | neden=draw_probability_live, xg_margin_very_narrow, top_draw_scoreline, probability_margin_very_narrow, strength_edge_very_narrow, low_confidence_side_pick, draw_calibration_high
- Hafta 24 | 28.02.2026 - 16:00 | KOCAELİSPOR - BEŞİKTAŞ A.Ş. | skor 0-1 | tahmin=Beşiktaş gerçek=Beşiktaş | aksiyon=Beraberlik uyarılı tahmin | risk=MEDIUM 31 | neden=top_draw_scoreline, strength_edge_very_narrow, medium_confidence_side_pick
- Hafta 25 | 7.03.2026 - 20:00 | BEŞİKTAŞ A.Ş. - GALATASARAY A.Ş. | skor 0-1 | tahmin=Rakip gerçek=Rakip | aksiyon=Korumalı taraf tahmini | risk=HIGH 35 | neden=draw_scoreline_top_two, probability_margin_watch, strength_edge_very_narrow, low_confidence_side_pick
- Hafta 26 | 15.03.2026 - 20:00 | GENÇLERBİRLİĞİ - BEŞİKTAŞ A.Ş. | skor 0-2 | tahmin=Beşiktaş gerçek=Beşiktaş | aksiyon=Beraberlik uyarılı tahmin | risk=MEDIUM 34 | neden=draw_probability_watch, draw_scoreline_top_two, strength_edge_very_narrow, medium_confidence_side_pick
- Hafta 28 | 5.04.2026 - 20:00 | FENERBAHÇE A.Ş. - BEŞİKTAŞ A.Ş. | skor 1-0 | tahmin=Beraberlik gerçek=Rakip | aksiyon=Korumalı taraf tahmini | risk=HIGH 100 | neden=draw_probability_watch, xg_margin_very_narrow, top_draw_scoreline, probability_margin_very_narrow, strength_edge_very_narrow, low_confidence_side_pick, draw_calibration_high, big_match_high_volatility
- Hafta 29 | 10.04.2026 - 20:00 | BEŞİKTAŞ A.Ş. - HESAP.COM ANTALYASPOR | skor 4-2 | tahmin=Beşiktaş gerçek=Beşiktaş | aksiyon=Beraberlik uyarılı tahmin | risk=MEDIUM 34 | neden=draw_probability_watch, draw_scoreline_top_two, strength_edge_very_narrow, medium_confidence_side_pick
- Hafta 30 | 19.04.2026 - 17:00 | SAMSUNSPOR A.Ş. - BEŞİKTAŞ A.Ş. | skor 2-1 | tahmin=Beşiktaş gerçek=Rakip | aksiyon=Korumalı taraf tahmini | risk=HIGH 89 | neden=draw_probability_watch, xg_margin_very_narrow, top_draw_scoreline, probability_margin_narrow, strength_edge_very_narrow, low_confidence_side_pick, draw_calibration_medium
- Hafta 32 | 1.05.2026 - 20:00 | GAZİANTEP FUTBOL KULÜBÜ A.Ş. - BEŞİKTAŞ A.Ş. | skor 0-2 | tahmin=Beşiktaş gerçek=Beşiktaş | aksiyon=Korumalı taraf tahmini | risk=HIGH 76 | neden=draw_probability_watch, xg_margin_narrow, top_draw_scoreline, probability_margin_watch, strength_edge_very_narrow, low_confidence_side_pick, draw_calibration_medium
- Hafta 33 | 9.05.2026 - 20:00 | BEŞİKTAŞ A.Ş. - TRABZONSPOR A.Ş. | skor 1-2 | tahmin=Rakip gerçek=Rakip | aksiyon=Korumalı taraf tahmini | risk=HIGH 89 | neden=draw_probability_live, xg_margin_watch, top_draw_scoreline, probability_margin_watch, strength_edge_very_narrow, low_confidence_side_pick, draw_calibration_high, big_match_high_volatility
- Hafta 34 | 15.05.2026 - 20:00 | ÇAYKUR RİZESPOR A.Ş. - BEŞİKTAŞ A.Ş. | skor 2-2 | tahmin=Beşiktaş gerçek=Beraberlik | aksiyon=Korumalı taraf tahmini | risk=HIGH 45 | neden=xg_margin_watch, top_draw_scoreline, strength_edge_very_narrow, low_confidence_side_pick

## Beraberlik Dışı Yanlış Taraf Vakaları

- Hafta 22 | RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ - BEŞİKTAŞ A.Ş. | skor 2-3 | tahmin=Rakip gerçek=Beşiktaş | risk=MEDIUM 31 | etiket=opponent_side_overrated
- Hafta 23 | BEŞİKTAŞ A.Ş. - GÖZTEPE A.Ş. | skor 4-0 | tahmin=Beraberlik gerçek=Beşiktaş | risk=HIGH 100 | etiket=high_draw_risk_but_decisive_result, narrow_xg_decisive_result, low_confidence_wrong_side
- Hafta 28 | FENERBAHÇE A.Ş. - BEŞİKTAŞ A.Ş. | skor 1-0 | tahmin=Beraberlik gerçek=Rakip | risk=HIGH 100 | etiket=big_match_side_flip, high_draw_risk_but_decisive_result, narrow_xg_decisive_result, low_confidence_wrong_side
- Hafta 30 | SAMSUNSPOR A.Ş. - BEŞİKTAŞ A.Ş. | skor 2-1 | tahmin=Beşiktaş gerçek=Rakip | risk=HIGH 89 | etiket=target_side_overrated, high_draw_risk_but_decisive_result, narrow_xg_decisive_result, low_confidence_wrong_side