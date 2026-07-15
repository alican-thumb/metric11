# Beraberlik Risk Denetimi

- Test edilen maç: 258
- Gerçek beraberlik: 76 (%29.5)
- MEDIUM/HIGH risk bayrağı: 143
- MEDIUM/HIGH beraberlik yakalama: 46/76 (%60.5 recall, %32.2 precision)
- HIGH risk beraberlik yakalama: 43/76 (%56.6 recall, %33.3 precision)
- Risk sonrası kaçan beraberlik: 30
- Risk dağılımı: {'HIGH': 129, 'LOW': 115, 'MEDIUM': 14}
- Aksiyon dağılımı: {'PROTECT_SIDE_PICK_SHOW_DRAW_SCENARIO': 129, 'KEEP_MAIN_PICK': 115, 'KEEP_PICK_WITH_DRAW_WARNING': 14}

## Okuma

- Bu katman ana 1X2 tahmini değiştirmez; taraf tahminini korumaya alır ve beraberlik senaryosunu görünür yapar.
- Precision gerçek beraberlik baz oranının üstündeyse risk etiketi ürün dili için değerlidir; kesin X tahmini olarak kullanılmamalıdır.
- MEDIUM/HIGH bayraklı maçlarda UI tarafında skor senaryoları ve güven dili daha temkinli gösterilmeli.

## HIGH Risk Maçlar

- 20.09.2025 - 17:00 | GENÇLERBİRLİĞİ - İKAS EYÜPSPOR | skor 1-0 | tahmin=Ev gerçek=Ev | risk=81 | neden=xg_margin_very_narrow, top_draw_scoreline, probability_margin_very_narrow, strength_edge_narrow
- 20.09.2025 - 20:00 | TRABZONSPOR A.Ş. - GAZİANTEP FUTBOL KULÜBÜ A.Ş. | skor 1-1 | tahmin=X gerçek=X | risk=65 | neden=draw_probability_high, xg_margin_watch, draw_scoreline_top_two, probability_margin_watch
- 27.09.2025 - 17:00 | GAZİANTEP FUTBOL KULÜBÜ A.Ş. - SAMSUNSPOR A.Ş. | skor 2-2 | tahmin=X gerçek=X | risk=99 | neden=draw_probability_live, xg_margin_very_narrow, top_draw_scoreline, probability_margin_very_narrow
- 28.09.2025 - 17:00 | ÇAYKUR RİZESPOR A.Ş. - KASIMPAŞA A.Ş. | skor 1-2 | tahmin=X gerçek=Dep | risk=100 | neden=draw_probability_high, xg_margin_very_narrow, top_draw_scoreline, probability_margin_very_narrow
- 28.09.2025 - 20:00 | ZECORNER KAYSERİSPOR - GENÇLERBİRLİĞİ | skor 1-1 | tahmin=X gerçek=X | risk=85 | neden=xg_margin_very_narrow, top_draw_scoreline, probability_margin_very_narrow, strength_edge_very_narrow
- 3.10.2025 - 20:00 | HESAP.COM ANTALYASPOR - ÇAYKUR RİZESPOR A.Ş. | skor 2-5 | tahmin=Ev gerçek=Dep | risk=38 | neden=draw_probability_live, draw_scoreline_top_two, medium_confidence_side_pick, existing_draw_flag
- 4.10.2025 - 14:30 | GENÇLERBİRLİĞİ - CORENDON ALANYASPOR | skor 2-2 | tahmin=X gerçek=X | risk=64 | neden=draw_probability_high, xg_margin_watch, draw_scoreline_top_two, probability_margin_watch
- 4.10.2025 - 17:00 | KOCAELİSPOR - İKAS EYÜPSPOR | skor 1-0 | tahmin=X gerçek=Ev | risk=100 | neden=draw_probability_high, xg_margin_very_narrow, top_draw_scoreline, probability_margin_very_narrow
- 5.10.2025 - 14:30 | KASIMPAŞA A.Ş. - TÜMOSAN KONYASPOR | skor 1-1 | tahmin=Dep gerçek=X | risk=36 | neden=xg_margin_watch, top_draw_scoreline, probability_margin_watch, medium_confidence_side_pick
- 5.10.2025 - 20:00 | SAMSUNSPOR A.Ş. - FENERBAHÇE A.Ş. | skor 0-0 | tahmin=X gerçek=X | risk=96 | neden=draw_probability_high, xg_margin_narrow, top_draw_scoreline, probability_margin_narrow
- 19.10.2025 - 17:00 | CORENDON ALANYASPOR - GÖZTEPE A.Ş. | skor 1-0 | tahmin=X gerçek=Ev | risk=70 | neden=draw_probability_high, xg_margin_watch, draw_scoreline_top_two, probability_margin_narrow
- 20.10.2025 - 20:00 | İKAS EYÜPSPOR - KASIMPAŞA A.Ş. | skor 2-0 | tahmin=X gerçek=Ev | risk=78 | neden=draw_probability_high, xg_margin_narrow, draw_scoreline_top_two, probability_margin_watch
- 22.10.2025 - 20:00 | TÜMOSAN KONYASPOR - BEŞİKTAŞ A.Ş. | skor 0-2 | tahmin=Ev gerçek=Dep | risk=60 | neden=xg_margin_narrow, top_draw_scoreline, probability_margin_narrow, strength_edge_very_narrow
- 22.10.2025 - 20:00 | ÇAYKUR RİZESPOR A.Ş. - RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ | skor 0-0 | tahmin=X gerçek=X | risk=88 | neden=draw_probability_live, xg_margin_narrow, top_draw_scoreline, probability_margin_narrow
- 24.10.2025 - 20:00 | MISIRLI.COM.TR FATİH KARAGÜMRÜK - ZECORNER KAYSERİSPOR | skor 2-2 | tahmin=Ev gerçek=X | risk=40 | neden=xg_margin_watch, top_draw_scoreline, strength_edge_very_narrow, medium_confidence_side_pick
- 25.10.2025 - 17:00 | KOCAELİSPOR - CORENDON ALANYASPOR | skor 2-0 | tahmin=Dep gerçek=Ev | risk=36 | neden=xg_margin_watch, top_draw_scoreline, probability_margin_watch, medium_confidence_side_pick
- 26.10.2025 - 14:30 | HESAP.COM ANTALYASPOR - RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ | skor 0-4 | tahmin=X gerçek=Dep | risk=95 | neden=draw_probability_watch, xg_margin_very_narrow, top_draw_scoreline, probability_margin_very_narrow
- 26.10.2025 - 17:00 | GENÇLERBİRLİĞİ - TÜMOSAN KONYASPOR | skor 1-2 | tahmin=X gerçek=Dep | risk=100 | neden=draw_probability_live, xg_margin_very_narrow, top_draw_scoreline, probability_margin_very_narrow
- 26.10.2025 - 20:00 | KASIMPAŞA A.Ş. - BEŞİKTAŞ A.Ş. | skor 1-1 | tahmin=Dep gerçek=X | risk=50 | neden=xg_margin_narrow, top_draw_scoreline, probability_margin_watch, strength_edge_narrow
- 27.10.2025 - 20:00 | SAMSUNSPOR A.Ş. - ÇAYKUR RİZESPOR A.Ş. | skor 1-1 | tahmin=Ev gerçek=X | risk=46 | neden=draw_probability_watch, xg_margin_watch, top_draw_scoreline, strength_edge_narrow
- 27.10.2025 - 20:00 | GAZİANTEP FUTBOL KULÜBÜ A.Ş. - FENERBAHÇE A.Ş. | skor 0-4 | tahmin=Dep gerçek=Dep | risk=85 | neden=xg_margin_very_narrow, top_draw_scoreline, probability_margin_very_narrow, strength_edge_very_narrow
- 31.10.2025 - 20:00 | RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ - KOCAELİSPOR | skor 1-0 | tahmin=X gerçek=Ev | risk=56 | neden=draw_probability_watch, xg_margin_watch, top_draw_scoreline, probability_margin_watch
- 2.11.2025 - 14:30 | TÜMOSAN KONYASPOR - SAMSUNSPOR A.Ş. | skor 1-3 | tahmin=X gerçek=Dep | risk=66 | neden=xg_margin_narrow, top_draw_scoreline, probability_margin_narrow, strength_edge_narrow
- 2.11.2025 - 17:00 | ZECORNER KAYSERİSPOR - KASIMPAŞA A.Ş. | skor 3-2 | tahmin=Dep gerçek=Ev | risk=46 | neden=draw_probability_watch, xg_margin_watch, top_draw_scoreline, probability_margin_watch
- 2.11.2025 - 20:00 | BEŞİKTAŞ A.Ş. - FENERBAHÇE A.Ş. | skor 2-3 | tahmin=X gerçek=Dep | risk=84 | neden=draw_probability_live, xg_margin_narrow, top_draw_scoreline, probability_margin_narrow
- 3.11.2025 - 20:00 | CORENDON ALANYASPOR - GAZİANTEP FUTBOL KULÜBÜ A.Ş. | skor 0-0 | tahmin=Dep gerçek=X | risk=81 | neden=xg_margin_very_narrow, top_draw_scoreline, probability_margin_very_narrow, strength_edge_narrow
- 7.11.2025 - 20:00 | GENÇLERBİRLİĞİ - RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ | skor 2-1 | tahmin=X gerçek=Ev | risk=60 | neden=draw_probability_watch, xg_margin_narrow, top_draw_scoreline, probability_margin_watch
- 8.11.2025 - 14:30 | GAZİANTEP FUTBOL KULÜBÜ A.Ş. - ÇAYKUR RİZESPOR A.Ş. | skor 2-2 | tahmin=Ev gerçek=X | risk=65 | neden=xg_margin_narrow, top_draw_scoreline, probability_margin_narrow, strength_edge_very_narrow
- 8.11.2025 - 20:00 | KASIMPAŞA A.Ş. - GÖZTEPE A.Ş. | skor 0-2 | tahmin=X gerçek=Dep | risk=100 | neden=draw_probability_live, xg_margin_very_narrow, top_draw_scoreline, probability_margin_very_narrow
- 9.11.2025 - 14:30 | MISIRLI.COM.TR FATİH KARAGÜMRÜK - TÜMOSAN KONYASPOR | skor 2-0 | tahmin=Dep gerçek=Ev | risk=73 | neden=xg_margin_very_narrow, top_draw_scoreline, probability_margin_narrow, strength_edge_narrow

## Hâlâ Kaçan Beraberlikler

- 21.09.2025 - 20:00 | KASIMPAŞA A.Ş. - FENERBAHÇE A.Ş. | skor 1-1 | tahmin=Dep | risk=0 | xG=0.93-1.6 | draw_p=0.217
- 27.09.2025 - 17:00 | İKAS EYÜPSPOR - GÖZTEPE A.Ş. | skor 0-0 | tahmin=Dep | risk=0 | xG=0.64-1.75 | draw_p=0.249
- 4.10.2025 - 20:00 | GALATASARAY A.Ş. - BEŞİKTAŞ A.Ş. | skor 1-1 | tahmin=Ev | risk=0 | xG=2.41-1.12 | draw_p=0.182
- 1.11.2025 - 20:00 | GALATASARAY A.Ş. - TRABZONSPOR A.Ş. | skor 0-0 | tahmin=Ev | risk=6 | xG=1.98-1.33 | draw_p=0.218
- 8.11.2025 - 17:03 | TRABZONSPOR A.Ş. - CORENDON ALANYASPOR | skor 1-1 | tahmin=Ev | risk=0 | xG=1.72-0.92 | draw_p=0.244
- 1.12.2025 - 20:00 | SAMSUNSPOR A.Ş. - CORENDON ALANYASPOR | skor 1-1 | tahmin=Ev | risk=0 | xG=1.72-0.82 | draw_p=0.238
- 1.12.2025 - 20:00 | FENERBAHÇE A.Ş. - GALATASARAY A.Ş. | skor 1-1 | tahmin=Ev | risk=5 | xG=2.06-1.31 | draw_p=0.249
- 6.12.2025 - 20:00 | RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ - FENERBAHÇE A.Ş. | skor 1-1 | tahmin=Dep | risk=0 | xG=1.45-2.13 | draw_p=0.187
- 7.12.2025 - 17:03 | KOCAELİSPOR - KASIMPAŞA A.Ş. | skor 0-0 | tahmin=Ev | risk=0 | xG=1.63-0.92 | draw_p=0.247
- 8.12.2025 - 20:00 | CORENDON ALANYASPOR - HESAP.COM ANTALYASPOR | skor 0-0 | tahmin=Ev | risk=0 | xG=1.67-0.98 | draw_p=0.24
- 14.12.2025 - 20:00 | TRABZONSPOR A.Ş. - BEŞİKTAŞ A.Ş. | skor 3-3 | tahmin=Ev | risk=24 | xG=2.06-1.33 | draw_p=0.252
- 17.01.2026 - 20:00 | GALATASARAY A.Ş. - GAZİANTEP FUTBOL KULÜBÜ A.Ş. | skor 1-1 | tahmin=Ev | risk=0 | xG=2.39-1.0 | draw_p=0.171
- 25.01.2026 - 14:30 | GAZİANTEP FUTBOL KULÜBÜ A.Ş. - TÜMOSAN KONYASPOR | skor 1-1 | tahmin=Ev | risk=12 | xG=1.73-1.01 | draw_p=0.241
- 25.01.2026 - 20:00 | FENERBAHÇE A.Ş. - GÖZTEPE A.Ş. | skor 1-1 | tahmin=Ev | risk=5 | xG=2.16-1.35 | draw_p=0.245
- 26.01.2026 - 20:00 | İKAS EYÜPSPOR - BEŞİKTAŞ A.Ş. | skor 2-2 | tahmin=Dep | risk=0 | xG=0.95-1.79 | draw_p=0.222
- 30.01.2026 - 20:02 | HESAP.COM ANTALYASPOR - TRABZONSPOR A.Ş. | skor 1-1 | tahmin=Dep | risk=0 | xG=1.3-2.2 | draw_p=0.211
- 31.01.2026 - 17:00 | RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ - ÇAYKUR RİZESPOR A.Ş. | skor 2-2 | tahmin=Ev | risk=0 | xG=2.42-1.14 | draw_p=0.182
- 8.02.2026 - 17:00 | TÜMOSAN KONYASPOR - GÖZTEPE A.Ş. | skor 0-0 | tahmin=Dep | risk=9 | xG=0.83-1.63 | draw_p=0.254
- 8.02.2026 - 20:00 | BEŞİKTAŞ A.Ş. - CORENDON ALANYASPOR | skor 2-2 | tahmin=Ev | risk=0 | xG=1.78-1.0 | draw_p=0.246
- 14.02.2026 - 14:30 | GENÇLERBİRLİĞİ - ÇAYKUR RİZESPOR A.Ş. | skor 2-2 | tahmin=Ev | risk=21 | xG=1.67-1.1 | draw_p=0.228
- 15.02.2026 - 17:00 | GÖZTEPE A.Ş. - ZECORNER KAYSERİSPOR | skor 0-0 | tahmin=Ev | risk=0 | xG=1.81-0.55 | draw_p=0.256
- 23.02.2026 - 20:00 | FENERBAHÇE A.Ş. - KASIMPAŞA A.Ş. | skor 1-1 | tahmin=Ev | risk=0 | xG=2.32-0.62 | draw_p=0.152
- 28.02.2026 - 20:00 | GÖZTEPE A.Ş. - İKAS EYÜPSPOR | skor 0-0 | tahmin=Ev | risk=9 | xG=1.83-0.97 | draw_p=0.25
- 1.03.2026 - 16:00 | GENÇLERBİRLİĞİ - ZECORNER KAYSERİSPOR | skor 0-0 | tahmin=Ev | risk=5 | xG=1.58-0.89 | draw_p=0.229
- 1.03.2026 - 20:00 | HESAP.COM ANTALYASPOR - FENERBAHÇE A.Ş. | skor 2-2 | tahmin=Dep | risk=0 | xG=1.0-2.2 | draw_p=0.203
- 18.03.2026 - 20:00 | RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ - HESAP.COM ANTALYASPOR | skor 0-0 | tahmin=Ev | risk=0 | xG=2.01-1.15 | draw_p=0.214
- 12.04.2026 - 20:00 | GALATASARAY A.Ş. - KOCAELİSPOR | skor 1-1 | tahmin=Ev | risk=0 | xG=2.28-0.79 | draw_p=0.176
- 27.04.2026 - 20:00 | BEŞİKTAŞ A.Ş. - MISIRLI.COM.TR FATİH KARAGÜMRÜK | skor 0-0 | tahmin=Ev | risk=0 | xG=1.91-0.8 | draw_p=0.236
- 2.05.2026 - 20:00 | TRABZONSPOR A.Ş. - GÖZTEPE A.Ş. | skor 1-1 | tahmin=Ev | risk=21 | xG=1.79-1.22 | draw_p=0.239
- 17.05.2026 - 20:00 | FENERBAHÇE A.Ş. - İKAS EYÜPSPOR | skor 3-3 | tahmin=Ev | risk=0 | xG=2.07-1.21 | draw_p=0.245