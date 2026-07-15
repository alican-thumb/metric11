# Model Baseline Karşılaştırması

- Test edilen maç: 258
- Gerçek beraberlik sayısı: 76
- En iyi accuracy: poisson_only
- En iyi log loss: current_hybrid

## Model Tablosu

| Model | Accuracy | Doğru | Draw recall | Draw precision | Brier | Log loss | Yüksek güvenli hata | Tahmin dağılımı |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| poisson_only | %51.2 | 132/258 | %0.0 | %0.0 | 0.617 | 1.03 | 32 | {'home': 156, 'away': 102} |
| current_hybrid | %50.4 | 130/258 | %0.0 | %0.0 | 0.61 | 1.019 | 41 | {'home': 152, 'away': 106} |
| recent_form_edge | %48.4 | 125/258 | %27.6 | %43.8 | 0.631 | 1.047 | 24 | {'away': 112, 'draw': 48, 'home': 98} |
| points_per_match_edge | %48.1 | 124/258 | %27.6 | %42.0 | 0.627 | 1.041 | 23 | {'away': 106, 'home': 102, 'draw': 50} |
| elo_only | %44.2 | 114/258 | %7.9 | %15.8 | 0.618 | 1.028 | 29 | {'home': 173, 'draw': 38, 'away': 47} |
| always_home | %43.0 | 111/258 | %0.0 | %0.0 | 0.654 | 1.08 | 0 | {'home': 258} |

## Okuma

- Mevcut hybrid model %50.4 accuracy ile basit ev sahibi baseline'ının %43.0 seviyesine karşı ölçüldü.
- En yüksek accuracy poisson_only modelinde: %51.2.
- Draw recall düşük kalan modeller beraberlikleri ana tahmine çevirmeden risk etiketi olarak güçlendirmeli.

## Son 30 Maç Karşılaştırması

- 27.04.2026 - 17:00 | CORENDON ALANYASPOR - SAMSUNSPOR A.Ş. | skor 2-3 | gerçek=Dep | always_home=Ev, points_per_match_edge=Dep, recent_form_edge=Dep, elo_only=Ev, poisson_only=Ev, current_hybrid=Ev
- 27.04.2026 - 20:00 | TÜMOSAN KONYASPOR - TRABZONSPOR A.Ş. | skor 2-1 | gerçek=Ev | always_home=Ev, points_per_match_edge=Dep, recent_form_edge=Ev, elo_only=Dep, poisson_only=Ev, current_hybrid=Dep
- 27.04.2026 - 20:00 | BEŞİKTAŞ A.Ş. - MISIRLI.COM.TR FATİH KARAGÜMRÜK | skor 0-0 | gerçek=X | always_home=Ev, points_per_match_edge=Ev, recent_form_edge=Ev, elo_only=Ev, poisson_only=Ev, current_hybrid=Ev
- 1.05.2026 - 17:00 | ÇAYKUR RİZESPOR A.Ş. - TÜMOSAN KONYASPOR | skor 3-2 | gerçek=Ev | always_home=Ev, points_per_match_edge=Dep, recent_form_edge=Dep, elo_only=Ev, poisson_only=Ev, current_hybrid=Ev
- 1.05.2026 - 20:00 | GAZİANTEP FUTBOL KULÜBÜ A.Ş. - BEŞİKTAŞ A.Ş. | skor 0-2 | gerçek=Dep | always_home=Ev, points_per_match_edge=Dep, recent_form_edge=Dep, elo_only=Dep, poisson_only=Dep, current_hybrid=Dep
- 2.05.2026 - 20:00 | FENERBAHÇE A.Ş. - RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ | skor 3-1 | gerçek=Ev | always_home=Ev, points_per_match_edge=X, recent_form_edge=X, elo_only=Ev, poisson_only=Ev, current_hybrid=Ev
- 2.05.2026 - 20:00 | TRABZONSPOR A.Ş. - GÖZTEPE A.Ş. | skor 1-1 | gerçek=X | always_home=Ev, points_per_match_edge=Ev, recent_form_edge=X, elo_only=Ev, poisson_only=Ev, current_hybrid=Ev
- 2.05.2026 - 20:00 | SAMSUNSPOR A.Ş. - GALATASARAY A.Ş. | skor 4-1 | gerçek=Ev | always_home=Ev, points_per_match_edge=Dep, recent_form_edge=X, elo_only=Dep, poisson_only=Dep, current_hybrid=Dep
- 3.05.2026 - 20:00 | ZECORNER KAYSERİSPOR - İKAS EYÜPSPOR | skor 1-1 | gerçek=X | always_home=Ev, points_per_match_edge=X, recent_form_edge=X, elo_only=Ev, poisson_only=Dep, current_hybrid=Dep
- 3.05.2026 - 20:00 | HESAP.COM ANTALYASPOR - CORENDON ALANYASPOR | skor 0-0 | gerçek=X | always_home=Ev, points_per_match_edge=Dep, recent_form_edge=X, elo_only=X, poisson_only=Dep, current_hybrid=Dep
- 3.05.2026 - 20:00 | MISIRLI.COM.TR FATİH KARAGÜMRÜK - GENÇLERBİRLİĞİ | skor 1-0 | gerçek=Ev | always_home=Ev, points_per_match_edge=Ev, recent_form_edge=Ev, elo_only=Ev, poisson_only=Ev, current_hybrid=Ev
- 3.05.2026 - 20:00 | KASIMPAŞA A.Ş. - KOCAELİSPOR | skor 1-1 | gerçek=X | always_home=Ev, points_per_match_edge=Ev, recent_form_edge=Ev, elo_only=Ev, poisson_only=Ev, current_hybrid=Ev
- 9.05.2026 - 20:00 | GENÇLERBİRLİĞİ - KASIMPAŞA A.Ş. | skor 3-2 | gerçek=Ev | always_home=Ev, points_per_match_edge=Dep, recent_form_edge=Dep, elo_only=X, poisson_only=Dep, current_hybrid=Dep
- 9.05.2026 - 20:00 | GALATASARAY A.Ş. - HESAP.COM ANTALYASPOR | skor 4-2 | gerçek=Ev | always_home=Ev, points_per_match_edge=Ev, recent_form_edge=Ev, elo_only=Ev, poisson_only=Ev, current_hybrid=Ev
- 9.05.2026 - 20:00 | BEŞİKTAŞ A.Ş. - TRABZONSPOR A.Ş. | skor 1-2 | gerçek=Dep | always_home=Ev, points_per_match_edge=Dep, recent_form_edge=X, elo_only=Ev, poisson_only=Ev, current_hybrid=Ev
- 9.05.2026 - 20:00 | RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ - SAMSUNSPOR A.Ş. | skor 3-0 | gerçek=Ev | always_home=Ev, points_per_match_edge=Dep, recent_form_edge=Dep, elo_only=Ev, poisson_only=Ev, current_hybrid=Ev
- 9.05.2026 - 20:00 | KOCAELİSPOR - MISIRLI.COM.TR FATİH KARAGÜMRÜK | skor 0-1 | gerçek=Dep | always_home=Ev, points_per_match_edge=Dep, recent_form_edge=Dep, elo_only=Ev, poisson_only=Dep, current_hybrid=Dep
- 9.05.2026 - 20:00 | GÖZTEPE A.Ş. - GAZİANTEP FUTBOL KULÜBÜ A.Ş. | skor 2-1 | gerçek=Ev | always_home=Ev, points_per_match_edge=Ev, recent_form_edge=Ev, elo_only=Ev, poisson_only=Ev, current_hybrid=Ev
- 9.05.2026 - 20:00 | TÜMOSAN KONYASPOR - FENERBAHÇE A.Ş. | skor 0-3 | gerçek=Dep | always_home=Ev, points_per_match_edge=X, recent_form_edge=X, elo_only=Dep, poisson_only=Ev, current_hybrid=Ev
- 9.05.2026 - 20:00 | İKAS EYÜPSPOR - ÇAYKUR RİZESPOR A.Ş. | skor 4-0 | gerçek=Ev | always_home=Ev, points_per_match_edge=Dep, recent_form_edge=Dep, elo_only=X, poisson_only=Dep, current_hybrid=Dep
- 9.05.2026 - 20:00 | CORENDON ALANYASPOR - ZECORNER KAYSERİSPOR | skor 3-1 | gerçek=Ev | always_home=Ev, points_per_match_edge=X, recent_form_edge=Dep, elo_only=Ev, poisson_only=Ev, current_hybrid=Ev
- 15.05.2026 - 20:00 | ÇAYKUR RİZESPOR A.Ş. - BEŞİKTAŞ A.Ş. | skor 2-2 | gerçek=X | always_home=Ev, points_per_match_edge=Dep, recent_form_edge=X, elo_only=Dep, poisson_only=Dep, current_hybrid=Dep
- 16.05.2026 - 17:00 | MISIRLI.COM.TR FATİH KARAGÜMRÜK - CORENDON ALANYASPOR | skor 2-1 | gerçek=Ev | always_home=Ev, points_per_match_edge=Ev, recent_form_edge=Ev, elo_only=X, poisson_only=Dep, current_hybrid=Dep
- 16.05.2026 - 20:00 | GAZİANTEP FUTBOL KULÜBÜ A.Ş. - RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ | skor 1-2 | gerçek=Dep | always_home=Ev, points_per_match_edge=Dep, recent_form_edge=Dep, elo_only=Dep, poisson_only=Dep, current_hybrid=Dep
- 16.05.2026 - 20:00 | SAMSUNSPOR A.Ş. - GÖZTEPE A.Ş. | skor 3-0 | gerçek=Ev | always_home=Ev, points_per_match_edge=Ev, recent_form_edge=Ev, elo_only=Ev, poisson_only=Ev, current_hybrid=Ev
- 17.05.2026 - 17:00 | ZECORNER KAYSERİSPOR - TÜMOSAN KONYASPOR | skor 2-1 | gerçek=Ev | always_home=Ev, points_per_match_edge=Dep, recent_form_edge=Dep, elo_only=Dep, poisson_only=Dep, current_hybrid=Dep
- 17.05.2026 - 20:00 | FENERBAHÇE A.Ş. - İKAS EYÜPSPOR | skor 3-3 | gerçek=X | always_home=Ev, points_per_match_edge=Ev, recent_form_edge=X, elo_only=Ev, poisson_only=Ev, current_hybrid=Ev
- 17.05.2026 - 20:00 | KASIMPAŞA A.Ş. - GALATASARAY A.Ş. | skor 1-0 | gerçek=Ev | always_home=Ev, points_per_match_edge=Dep, recent_form_edge=Dep, elo_only=Dep, poisson_only=Dep, current_hybrid=Dep
- 17.05.2026 - 20:00 | TRABZONSPOR A.Ş. - GENÇLERBİRLİĞİ | skor 0-3 | gerçek=Dep | always_home=Ev, points_per_match_edge=Ev, recent_form_edge=X, elo_only=Ev, poisson_only=Ev, current_hybrid=Ev
- 17.05.2026 - 20:00 | HESAP.COM ANTALYASPOR - KOCAELİSPOR | skor 1-0 | gerçek=Ev | always_home=Ev, points_per_match_edge=X, recent_form_edge=Dep, elo_only=X, poisson_only=Ev, current_hybrid=Ev