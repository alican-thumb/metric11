# 2026-27 Süper Lig — Haftalık Tahmin Karnesi

Oynanan her maçın sonucu, tahmin motorunun takım formu/Elo durumunu ilerletir; bu yüzden bir sonraki haftanın skor tahminleri geçen haftanın gerçek sonuçlarıyla güncellenir. Doğrulanan transferler de aynı şekilde güce yansır.

## Genel Karne

- Değerlendirilen maç: **54**
- İsabet: **21/54** (%39)
- Beraberlik yakalama: **2/11** (%18)
- Yüksek güvenli maç isabeti: **9/19** (%47)
- Brier score: **0.666** (düşük daha iyi; 2025-26 referans 0.600)
- Log loss: **1.092** (düşük daha iyi; 2025-26 referans 1.005)

### Güven bandı kalibrasyonu

_"Beyan edilen ort. olasılık" ile "İsabet" arasındaki fark büyükse (özellikle isabet daha düşükse) model o banttaki kendine güvenini haklı çıkaramıyor demektir. İsabet oranı tek başına aldatıcı olabilir — favoriyi seçip düşük bir olasılıkla tutturmak yüksek isabet ama kötü kalibrasyon demektir. Brier/log loss olasılıkların KENDİSİNİN kalitesini ölçer (düşük = iyi). Referans sütunu geçmiş sezonun 258 maçlık backtest'inden — küçük örneklemli erken hafta sapmalarını buna göre yorumlayın._

| Güven bandı | Maç | İsabet | Beyan edilen ort. olasılık | Brier | Log loss | Referans (2025-26: isabet / brier / logloss) |
| --- | --- | --- | --- | --- | --- | --- |
| HIGH | 19 | 9/19 (%47) | %59 | 0.628 | 1.038 | %64 / 0.516 / 0.885 |
| MEDIUM | 20 | 4/20 (%20) | %46 | 0.696 | 1.124 | %54 / 0.619 / 1.032 |
| LOW | 15 | 8/15 (%53) | %39 | 0.676 | 1.117 | %48 / 0.670 / 1.103 |

## Hafta 6 — 4/9 isabet (%44)

| Maç | Skor | Tahmin | Sonuç | Güven |
| --- | --- | --- | --- | --- |
| KASIMPAŞA A.Ş. - TÜMOSAN KONYASPOR | 0 - 0 | Ev | ❌ | HIGH |
| ARCA ÇORUM FK - CORENDON ALANYASPOR | 1 - 2 | Ev | ❌ | HIGH |
| KOCAELİSPOR - GAZİANTEP FUTBOL KULÜBÜ A.Ş. | 2 - 0 | Ev | ✅ | MEDIUM |
| TRABZONSPOR A.Ş. - GALATASARAY A.Ş. | 4 - 0 | Deplasman | ❌ | HIGH |
| İSTANBUL BAŞAKŞEHİR FK - GENÇLERBİRLİĞİ | 4 - 0 | Ev | ✅ | LOW |
| FENERBAHÇE A.Ş. - EYÜPSPOR | 8 - 0 | Ev | ✅ | HIGH |
| ERZURUMSPOR FK - SAMSUNSPOR A.Ş. | 1 - 0 | Deplasman | ❌ | MEDIUM |
| AMED SPORTİF FAALİYETLER - BEŞİKTAŞ A.Ş. | 3 - 2 | Ev | ✅ | MEDIUM |
| GÖZTEPE A.Ş. - ÇAYKUR RİZESPOR A.Ş. | 2 - 2 | Ev | ❌ | LOW |

## Hafta 5 — 3/9 isabet (%33)

| Maç | Skor | Tahmin | Sonuç | Güven |
| --- | --- | --- | --- | --- |
| BEŞİKTAŞ A.Ş. - ERZURUMSPOR FK | 3 - 0 | Ev | ✅ | HIGH |
| EYÜPSPOR - ÇAYKUR RİZESPOR A.Ş. | 0 - 2 | Ev | ❌ | MEDIUM |
| SAMSUNSPOR A.Ş. - ARCA ÇORUM FK | 1 - 5 | Ev | ❌ | MEDIUM |
| CORENDON ALANYASPOR - GÖZTEPE A.Ş. | 2 - 2 | Beraberlik | ✅ | LOW |
| TÜMOSAN KONYASPOR - TRABZONSPOR A.Ş. | 1 - 0 | Deplasman | ❌ | MEDIUM |
| GENÇLERBİRLİĞİ - KASIMPAŞA A.Ş. | 1 - 2 | Ev | ❌ | HIGH |
| AMED SPORTİF FAALİYETLER - İSTANBUL BAŞAKŞEHİR FK | 5 - 0 | Deplasman | ❌ | MEDIUM |
| GALATASARAY A.Ş. - KOCAELİSPOR | 1 - 0 | Ev | ✅ | HIGH |
| GAZİANTEP FUTBOL KULÜBÜ A.Ş. - FENERBAHÇE A.Ş. | 0 - 0 | Deplasman | ❌ | HIGH |

## Hafta 4 — 2/9 isabet (%22)

| Maç | Skor | Tahmin | Sonuç | Güven |
| --- | --- | --- | --- | --- |
| İSTANBUL BAŞAKŞEHİR FK - GALATASARAY A.Ş. | 2 - 3 | Deplasman | ✅ | LOW |
| ERZURUMSPOR FK - TÜMOSAN KONYASPOR | 1 - 0 | Deplasman | ❌ | LOW |
| FENERBAHÇE A.Ş. - BEŞİKTAŞ A.Ş. | 1 - 2 | Ev | ❌ | MEDIUM |
| KASIMPAŞA A.Ş. - AMED SPORTİF FAALİYETLER | 2 - 2 | Deplasman | ❌ | LOW |
| ARCA ÇORUM FK - EYÜPSPOR | 3 - 0 | Deplasman | ❌ | MEDIUM |
| TRABZONSPOR A.Ş. - GENÇLERBİRLİĞİ | 5 - 0 | Deplasman | ❌ | MEDIUM |
| KOCAELİSPOR - SAMSUNSPOR A.Ş. | 1 - 0 | Ev | ✅ | LOW |
| ÇAYKUR RİZESPOR A.Ş. - CORENDON ALANYASPOR | 0 - 1 | Beraberlik | ❌ | LOW |
| GÖZTEPE A.Ş. - GAZİANTEP FUTBOL KULÜBÜ A.Ş. | 2 - 4 | Ev | ❌ | MEDIUM |

## Hafta 3 — 6/9 isabet (%67)

| Maç | Skor | Tahmin | Sonuç | Güven |
| --- | --- | --- | --- | --- |
| GENÇLERBİRLİĞİ - ERZURUMSPOR FK | 1 - 1 | Ev | ❌ | HIGH |
| TÜMOSAN KONYASPOR - KOCAELİSPOR | 1 - 2 | Ev | ❌ | LOW |
| GAZİANTEP FUTBOL KULÜBÜ A.Ş. - ÇAYKUR RİZESPOR A.Ş. | 1 - 2 | Deplasman | ✅ | LOW |
| GALATASARAY A.Ş. - GÖZTEPE A.Ş. | 3 - 2 | Ev | ✅ | HIGH |
| EYÜPSPOR - CORENDON ALANYASPOR | 2 - 1 | Ev | ✅ | MEDIUM |
| İSTANBUL BAŞAKŞEHİR FK - KASIMPAŞA A.Ş. | 1 - 1 | Ev | ❌ | HIGH |
| SAMSUNSPOR A.Ş. - FENERBAHÇE A.Ş. | 0 - 2 | Deplasman | ✅ | LOW |
| AMED SPORTİF FAALİYETLER - TRABZONSPOR A.Ş. | 2 - 1 | Ev | ✅ | MEDIUM |
| BEŞİKTAŞ A.Ş. - ARCA ÇORUM FK | 6 - 2 | Ev | ✅ | HIGH |

## Hafta 2 — 2/9 isabet (%22)

| Maç | Skor | Tahmin | Sonuç | Güven |
| --- | --- | --- | --- | --- |
| ERZURUMSPOR FK - GALATASARAY A.Ş. | 0 - 4 | Deplasman | ✅ | HIGH |
| ÇAYKUR RİZESPOR A.Ş. - SAMSUNSPOR A.Ş. | 0 - 2 | Ev | ❌ | MEDIUM |
| ARCA ÇORUM FK - KASIMPAŞA A.Ş. | 0 - 1 | Ev | ❌ | MEDIUM |
| FENERBAHÇE A.Ş. - TÜMOSAN KONYASPOR | 4 - 2 | Ev | ✅ | HIGH |
| TRABZONSPOR A.Ş. - İSTANBUL BAŞAKŞEHİR FK | 2 - 1 | Deplasman | ❌ | HIGH |
| EYÜPSPOR - GAZİANTEP FUTBOL KULÜBÜ A.Ş. | 0 - 1 | Ev | ❌ | MEDIUM |
| CORENDON ALANYASPOR - BEŞİKTAŞ A.Ş. | 1 - 0 | Deplasman | ❌ | MEDIUM |
| GÖZTEPE A.Ş. - GENÇLERBİRLİĞİ | 0 - 1 | Ev | ❌ | MEDIUM |
| KOCAELİSPOR - AMED SPORTİF FAALİYETLER | 2 - 0 | Deplasman | ❌ | MEDIUM |

## Hafta 1 — 4/9 isabet (%44)

| Maç | Skor | Tahmin | Sonuç | Güven |
| --- | --- | --- | --- | --- |
| GALATASARAY A.Ş. - ARCA ÇORUM FK | 2 - 2 | Ev | ❌ | HIGH |
| KASIMPAŞA A.Ş. - TRABZONSPOR A.Ş. | 1 - 1 | Beraberlik | ✅ | LOW |
| TÜMOSAN KONYASPOR - ÇAYKUR RİZESPOR A.Ş. | 0 - 1 | Ev | ❌ | LOW |
| GAZİANTEP FUTBOL KULÜBÜ A.Ş. - CORENDON ALANYASPOR | 1 - 1 | Deplasman | ❌ | MEDIUM |
| GENÇLERBİRLİĞİ - FENERBAHÇE A.Ş. | 2 - 1 | Deplasman | ❌ | HIGH |
| İSTANBUL BAŞAKŞEHİR FK - KOCAELİSPOR | 2 - 0 | Ev | ✅ | HIGH |
| AMED SPORTİF FAALİYETLER - ERZURUMSPOR FK | 3 - 0 | Ev | ✅ | LOW |
| BEŞİKTAŞ A.Ş. - EYÜPSPOR | 1 - 0 | Ev | ✅ | HIGH |
| SAMSUNSPOR A.Ş. - GÖZTEPE A.Ş. | 3 - 3 | Ev | ❌ | LOW |

