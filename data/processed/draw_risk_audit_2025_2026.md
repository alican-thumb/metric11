# Beraberlik Risk Denetimi

- Test edilen maç: 258
- Gerçek beraberlik: 76 (%29.5)
- MEDIUM/HIGH risk bayrağı: 162
- MEDIUM/HIGH beraberlik yakalama: 54/76 (%71.1 recall, %33.3 precision)
- HIGH risk beraberlik yakalama: 52/76 (%68.4 recall, %35.6 precision)
- Risk sonrası kaçan beraberlik: 22
- Risk dağılımı: {'HIGH': 146, 'LOW': 96, 'MEDIUM': 16}
- Aksiyon dağılımı: {'PROTECT_SIDE_PICK_SHOW_DRAW_SCENARIO': 146, 'KEEP_MAIN_PICK': 96, 'KEEP_PICK_WITH_DRAW_WARNING': 16}

## Okuma

- Bu katman ana 1X2 tahmini değiştirmez; taraf tahminini korumaya alır ve beraberlik senaryosunu görünür yapar.
- Precision gerçek beraberlik baz oranının üstündeyse risk etiketi ürün dili için değerlidir; kesin X tahmini olarak kullanılmamalıdır.
- MEDIUM/HIGH bayraklı maçlarda UI tarafında skor senaryoları ve güven dili daha temkinli gösterilmeli.

## HIGH Risk Maçlar

- 20.09.2025 - 17:00 | GENÇLERBİRLİĞİ - İKAS EYÜPSPOR | skor 1-0 | tahmin=Ev gerçek=Ev | risk=83 | neden=xg_margin_very_narrow, top_draw_scoreline, probability_margin_narrow, strength_edge_narrow
- 20.09.2025 - 20:00 | TRABZONSPOR A.Ş. - GAZİANTEP FUTBOL KULÜBÜ A.Ş. | skor 1-1 | tahmin=X gerçek=X | risk=85 | neden=draw_probability_high, xg_margin_narrow, top_draw_scoreline, probability_margin_watch
- 27.09.2025 - 17:00 | GAZİANTEP FUTBOL KULÜBÜ A.Ş. - SAMSUNSPOR A.Ş. | skor 2-2 | tahmin=Dep gerçek=X | risk=90 | neden=draw_probability_live, xg_margin_narrow, top_draw_scoreline, probability_margin_narrow
- 28.09.2025 - 17:00 | TÜMOSAN KONYASPOR - RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ | skor 2-1 | tahmin=Ev gerçek=Ev | risk=64 | neden=draw_probability_live, xg_margin_watch, top_draw_scoreline, strength_edge_very_narrow
- 28.09.2025 - 17:00 | ÇAYKUR RİZESPOR A.Ş. - KASIMPAŞA A.Ş. | skor 1-2 | tahmin=Ev gerçek=Dep | risk=100 | neden=draw_probability_live, xg_margin_very_narrow, top_draw_scoreline, probability_margin_very_narrow
- 28.09.2025 - 20:00 | ZECORNER KAYSERİSPOR - GENÇLERBİRLİĞİ | skor 1-1 | tahmin=Ev gerçek=X | risk=95 | neden=draw_probability_watch, xg_margin_very_narrow, top_draw_scoreline, probability_margin_very_narrow
- 3.10.2025 - 20:00 | HESAP.COM ANTALYASPOR - ÇAYKUR RİZESPOR A.Ş. | skor 2-5 | tahmin=Ev gerçek=Dep | risk=70 | neden=draw_probability_watch, xg_margin_narrow, top_draw_scoreline, probability_margin_narrow
- 4.10.2025 - 14:30 | GENÇLERBİRLİĞİ - CORENDON ALANYASPOR | skor 2-2 | tahmin=X gerçek=X | risk=90 | neden=draw_probability_high, xg_margin_narrow, top_draw_scoreline, probability_margin_narrow
- 4.10.2025 - 17:00 | KOCAELİSPOR - İKAS EYÜPSPOR | skor 1-0 | tahmin=Ev gerçek=Ev | risk=97 | neden=draw_probability_live, xg_margin_very_narrow, top_draw_scoreline, probability_margin_narrow
- 5.10.2025 - 14:30 | KASIMPAŞA A.Ş. - TÜMOSAN KONYASPOR | skor 1-1 | tahmin=Dep gerçek=X | risk=91 | neden=draw_probability_live, xg_margin_very_narrow, top_draw_scoreline, probability_margin_narrow
- 5.10.2025 - 17:00 | MISIRLI.COM.TR FATİH KARAGÜMRÜK - GAZİANTEP FUTBOL KULÜBÜ A.Ş. | skor 0-2 | tahmin=Dep gerçek=Dep | risk=36 | neden=xg_margin_watch, top_draw_scoreline, probability_margin_watch, medium_confidence_side_pick
- 5.10.2025 - 20:00 | SAMSUNSPOR A.Ş. - FENERBAHÇE A.Ş. | skor 0-0 | tahmin=X gerçek=X | risk=72 | neden=draw_probability_high, xg_margin_watch, top_draw_scoreline, probability_margin_watch
- 18.10.2025 - 17:00 | ÇAYKUR RİZESPOR A.Ş. - TRABZONSPOR A.Ş. | skor 1-2 | tahmin=Dep gerçek=Dep | risk=70 | neden=draw_probability_watch, xg_margin_narrow, top_draw_scoreline, probability_margin_narrow
- 19.10.2025 - 17:00 | CORENDON ALANYASPOR - GÖZTEPE A.Ş. | skor 1-0 | tahmin=X gerçek=Ev | risk=77 | neden=draw_probability_high, xg_margin_watch, top_draw_scoreline, probability_margin_narrow
- 20.10.2025 - 20:00 | İKAS EYÜPSPOR - KASIMPAŞA A.Ş. | skor 2-0 | tahmin=Dep gerçek=Ev | risk=66 | neden=xg_margin_narrow, top_draw_scoreline, probability_margin_narrow, strength_edge_narrow
- 22.10.2025 - 20:00 | TÜMOSAN KONYASPOR - BEŞİKTAŞ A.Ş. | skor 0-2 | tahmin=Dep gerçek=Dep | risk=85 | neden=xg_margin_very_narrow, top_draw_scoreline, probability_margin_very_narrow, strength_edge_very_narrow
- 22.10.2025 - 20:00 | ÇAYKUR RİZESPOR A.Ş. - RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ | skor 0-0 | tahmin=Ev gerçek=X | risk=58 | neden=draw_probability_live, xg_margin_watch, top_draw_scoreline, strength_edge_very_narrow
- 24.10.2025 - 20:00 | MISIRLI.COM.TR FATİH KARAGÜMRÜK - ZECORNER KAYSERİSPOR | skor 2-2 | tahmin=Ev gerçek=X | risk=56 | neden=draw_probability_watch, xg_margin_watch, top_draw_scoreline, probability_margin_watch
- 25.10.2025 - 17:00 | KOCAELİSPOR - CORENDON ALANYASPOR | skor 2-0 | tahmin=Dep gerçek=Ev | risk=67 | neden=xg_margin_very_narrow, top_draw_scoreline, probability_margin_narrow, low_confidence_side_pick
- 26.10.2025 - 14:30 | HESAP.COM ANTALYASPOR - RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ | skor 0-4 | tahmin=Dep gerçek=Dep | risk=100 | neden=draw_probability_watch, xg_margin_very_narrow, top_draw_scoreline, probability_margin_very_narrow
- 26.10.2025 - 17:00 | GENÇLERBİRLİĞİ - TÜMOSAN KONYASPOR | skor 1-2 | tahmin=X gerçek=Dep | risk=100 | neden=draw_probability_high, xg_margin_very_narrow, top_draw_scoreline, probability_margin_very_narrow
- 26.10.2025 - 20:00 | KASIMPAŞA A.Ş. - BEŞİKTAŞ A.Ş. | skor 1-1 | tahmin=Dep gerçek=X | risk=36 | neden=xg_margin_watch, top_draw_scoreline, strength_edge_narrow, medium_confidence_side_pick
- 27.10.2025 - 20:00 | SAMSUNSPOR A.Ş. - ÇAYKUR RİZESPOR A.Ş. | skor 1-1 | tahmin=Ev gerçek=X | risk=52 | neden=draw_probability_watch, xg_margin_watch, top_draw_scoreline, probability_margin_watch
- 27.10.2025 - 20:00 | GAZİANTEP FUTBOL KULÜBÜ A.Ş. - FENERBAHÇE A.Ş. | skor 0-4 | tahmin=Dep gerçek=Dep | risk=70 | neden=xg_margin_narrow, top_draw_scoreline, probability_margin_narrow, strength_edge_very_narrow
- 31.10.2025 - 20:00 | RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ - KOCAELİSPOR | skor 1-0 | tahmin=Ev gerçek=Ev | risk=50 | neden=draw_probability_watch, xg_margin_watch, top_draw_scoreline, strength_edge_very_narrow
- 2.11.2025 - 14:30 | TÜMOSAN KONYASPOR - SAMSUNSPOR A.Ş. | skor 1-3 | tahmin=Dep gerçek=Dep | risk=66 | neden=draw_probability_live, xg_margin_watch, top_draw_scoreline, probability_margin_watch
- 2.11.2025 - 17:00 | ZECORNER KAYSERİSPOR - KASIMPAŞA A.Ş. | skor 3-2 | tahmin=Dep gerçek=Ev | risk=75 | neden=xg_margin_very_narrow, top_draw_scoreline, probability_margin_very_narrow, low_confidence_side_pick
- 2.11.2025 - 20:00 | BEŞİKTAŞ A.Ş. - FENERBAHÇE A.Ş. | skor 2-3 | tahmin=Dep gerçek=Dep | risk=91 | neden=draw_probability_watch, xg_margin_very_narrow, top_draw_scoreline, probability_margin_very_narrow
- 3.11.2025 - 20:00 | CORENDON ALANYASPOR - GAZİANTEP FUTBOL KULÜBÜ A.Ş. | skor 0-0 | tahmin=Dep gerçek=X | risk=66 | neden=xg_margin_narrow, top_draw_scoreline, probability_margin_narrow, strength_edge_narrow
- 7.11.2025 - 20:00 | GENÇLERBİRLİĞİ - RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ | skor 2-1 | tahmin=Dep gerçek=Ev | risk=60 | neden=draw_probability_watch, xg_margin_narrow, top_draw_scoreline, probability_margin_watch

## Hâlâ Kaçan Beraberlikler

- 21.09.2025 - 20:00 | KASIMPAŞA A.Ş. - FENERBAHÇE A.Ş. | skor 1-1 | tahmin=Dep | risk=0 | xG=0.91-1.77 | draw_p=0.204
- 27.09.2025 - 17:00 | İKAS EYÜPSPOR - GÖZTEPE A.Ş. | skor 0-0 | tahmin=Dep | risk=17 | xG=0.92-1.64 | draw_p=0.265
- 4.10.2025 - 20:00 | GALATASARAY A.Ş. - BEŞİKTAŞ A.Ş. | skor 1-1 | tahmin=Ev | risk=0 | xG=2.23-1.37 | draw_p=0.196
- 1.11.2025 - 20:00 | GALATASARAY A.Ş. - TRABZONSPOR A.Ş. | skor 0-0 | tahmin=Ev | risk=0 | xG=2.1-1.33 | draw_p=0.21
- 1.12.2025 - 20:00 | SAMSUNSPOR A.Ş. - CORENDON ALANYASPOR | skor 1-1 | tahmin=Ev | risk=6 | xG=1.9-1.02 | draw_p=0.227
- 6.12.2025 - 20:00 | RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ - FENERBAHÇE A.Ş. | skor 1-1 | tahmin=Dep | risk=0 | xG=1.39-2.06 | draw_p=0.19
- 8.12.2025 - 20:00 | CORENDON ALANYASPOR - HESAP.COM ANTALYASPOR | skor 0-0 | tahmin=Ev | risk=9 | xG=1.66-0.92 | draw_p=0.241
- 17.01.2026 - 20:00 | GALATASARAY A.Ş. - GAZİANTEP FUTBOL KULÜBÜ A.Ş. | skor 1-1 | tahmin=Ev | risk=0 | xG=2.35-1.13 | draw_p=0.177
- 25.01.2026 - 20:00 | FENERBAHÇE A.Ş. - GÖZTEPE A.Ş. | skor 1-1 | tahmin=Ev | risk=22 | xG=1.95-1.16 | draw_p=0.255
- 26.01.2026 - 20:00 | İKAS EYÜPSPOR - BEŞİKTAŞ A.Ş. | skor 2-2 | tahmin=Dep | risk=6 | xG=1.11-1.84 | draw_p=0.219
- 30.01.2026 - 20:02 | HESAP.COM ANTALYASPOR - TRABZONSPOR A.Ş. | skor 1-1 | tahmin=Dep | risk=6 | xG=1.21-1.86 | draw_p=0.228
- 31.01.2026 - 17:00 | RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ - ÇAYKUR RİZESPOR A.Ş. | skor 2-2 | tahmin=Ev | risk=0 | xG=2.06-1.22 | draw_p=0.227
- 8.02.2026 - 20:00 | BEŞİKTAŞ A.Ş. - CORENDON ALANYASPOR | skor 2-2 | tahmin=Ev | risk=6 | xG=1.75-1.02 | draw_p=0.248
- 15.02.2026 - 17:00 | GÖZTEPE A.Ş. - ZECORNER KAYSERİSPOR | skor 0-0 | tahmin=Ev | risk=14 | xG=1.68-0.83 | draw_p=0.276
- 23.02.2026 - 20:00 | FENERBAHÇE A.Ş. - KASIMPAŞA A.Ş. | skor 1-1 | tahmin=Ev | risk=0 | xG=2.02-0.67 | draw_p=0.177
- 28.02.2026 - 20:00 | GÖZTEPE A.Ş. - İKAS EYÜPSPOR | skor 0-0 | tahmin=Ev | risk=16 | xG=1.75-1.03 | draw_p=0.257
- 1.03.2026 - 20:00 | HESAP.COM ANTALYASPOR - FENERBAHÇE A.Ş. | skor 2-2 | tahmin=Dep | risk=0 | xG=0.96-2.05 | draw_p=0.211
- 18.03.2026 - 20:00 | RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ - HESAP.COM ANTALYASPOR | skor 0-0 | tahmin=Ev | risk=0 | xG=2.1-1.04 | draw_p=0.207
- 11.04.2026 - 17:00 | CORENDON ALANYASPOR - TRABZONSPOR A.Ş. | skor 1-1 | tahmin=Dep | risk=21 | xG=1.25-1.84 | draw_p=0.237
- 12.04.2026 - 20:00 | GALATASARAY A.Ş. - KOCAELİSPOR | skor 1-1 | tahmin=Ev | risk=0 | xG=2.06-0.91 | draw_p=0.203
- 27.04.2026 - 20:00 | BEŞİKTAŞ A.Ş. - MISIRLI.COM.TR FATİH KARAGÜMRÜK | skor 0-0 | tahmin=Ev | risk=0 | xG=1.8-0.92 | draw_p=0.248
- 17.05.2026 - 20:00 | FENERBAHÇE A.Ş. - İKAS EYÜPSPOR | skor 3-3 | tahmin=Ev | risk=0 | xG=2.13-1.07 | draw_p=0.239