# 2026-27 Süper Lig — Haftalık Tahmin Karnesi

Oynanan her maçın sonucu, tahmin motorunun takım formu/Elo durumunu ilerletir; bu yüzden bir sonraki haftanın skor tahminleri geçen haftanın gerçek sonuçlarıyla güncellenir. Doğrulanan transferler de aynı şekilde güce yansır.

## Genel Karne

- Değerlendirilen maç: **82**
- İsabet: **40/82** (%49)
- Beraberlik yakalama: **2/14** (%14)
- Yüksek güvenli maç isabeti: **22/33** (%67)
- Brier score: **0.597** (düşük daha iyi; 2025-26 referans 0.600)
- Log loss: **0.997** (düşük daha iyi; 2025-26 referans 1.005)

### Güven bandı kalibrasyonu

_"Beyan edilen ort. olasılık" ile "İsabet" arasındaki fark büyükse (özellikle isabet daha düşükse) model o banttaki kendine güvenini haklı çıkaramıyor demektir. İsabet oranı tek başına aldatıcı olabilir — favoriyi seçip düşük bir olasılıkla tutturmak yüksek isabet ama kötü kalibrasyon demektir. Brier/log loss olasılıkların KENDİSİNİN kalitesini ölçer (düşük = iyi). Referans sütunu geçmiş sezonun 258 maçlık backtest'inden — küçük örneklemli erken hafta sapmalarını buna göre yorumlayın._

| Güven bandı | Maç | İsabet | Beyan edilen ort. olasılık | Brier | Log loss | Referans (2025-26: isabet / brier / logloss) |
| --- | --- | --- | --- | --- | --- | --- |
| HIGH | 33 | 22/33 (%67) | %60 | 0.484 | 0.840 | %64 / 0.516 / 0.885 |
| MEDIUM | 26 | 7/26 (%27) | %47 | 0.694 | 1.127 | %54 / 0.619 / 1.032 |
| LOW | 23 | 11/23 (%48) | %38 | 0.649 | 1.074 | %48 / 0.670 / 1.103 |

### Seçilen tarafa göre isabet

_Model hangi tarafı seçtiğinde ne oldu? Belirli bir seçimde (ör. deplasman favorisi) sistematik hata varsa burada görünür. MEDIUM bandı canlı isabeti %35'in altında kaldıkça fikstür sayfasında bu bant "Kararsız" olarak gösterilir._

| Seçim | Maç | İsabet | Gerçekleşen (Ev / X / Dep) |
| --- | --- | --- | --- |
| Ev | 45 | 25/45 (%56) | 25 / 7 / 13 |
| Beraberlik | 7 | 2/7 (%29) | 2 / 2 / 3 |
| Deplasman | 30 | 13/30 (%43) | 12 / 5 / 13 |

## Hafta 10 — 1/1 isabet (%100)

| Maç | Skor | Tahmin | Sonuç | Güven |
| --- | --- | --- | --- | --- |
| TÜMOSAN KONYASPOR - GALATASARAY A.Ş. | 0 - 4 | Deplasman | ✅ | HIGH |

## Hafta 9 — 5/9 isabet (%56)

| Maç | Skor | Tahmin | Sonuç | Güven |
| --- | --- | --- | --- | --- |
| CORENDON ALANYASPOR - KOCAELİSPOR | 1 - 2 | Beraberlik | ❌ | LOW |
| EYÜPSPOR - KASIMPAŞA A.Ş. | 0 - 1 | Deplasman | ✅ | HIGH |
| GAZİANTEP FUTBOL KULÜBÜ A.Ş. - ERZURUMSPOR FK | 1 - 3 | Ev | ❌ | MEDIUM |
| SAMSUNSPOR A.Ş. - AMED SPORTİF FAALİYETLER | 1 - 2 | Deplasman | ✅ | HIGH |
| TÜMOSAN KONYASPOR - GENÇLERBİRLİĞİ | 2 - 0 | Beraberlik | ❌ | LOW |
| GÖZTEPE A.Ş. - ARCA ÇORUM FK | 2 - 0 | Deplasman | ❌ | LOW |
| ÇAYKUR RİZESPOR A.Ş. - TRABZONSPOR A.Ş. | 3 - 4 | Deplasman | ✅ | HIGH |
| BEŞİKTAŞ A.Ş. - İSTANBUL BAŞAKŞEHİR FK | 2 - 0 | Ev | ✅ | HIGH |
| GALATASARAY A.Ş. - FENERBAHÇE A.Ş. | 2 - 1 | Ev | ✅ | LOW |

## Hafta 8 — 7/9 isabet (%78)

| Maç | Skor | Tahmin | Sonuç | Güven |
| --- | --- | --- | --- | --- |
| ARCA ÇORUM FK - ÇAYKUR RİZESPOR A.Ş. | 2 - 1 | Ev | ✅ | MEDIUM |
| ERZURUMSPOR FK - EYÜPSPOR | 2 - 0 | Ev | ✅ | HIGH |
| AMED SPORTİF FAALİYETLER - TÜMOSAN KONYASPOR | 1 - 0 | Ev | ✅ | HIGH |
| GENÇLERBİRLİĞİ - GALATASARAY A.Ş. | 0 - 1 | Deplasman | ✅ | MEDIUM |
| FENERBAHÇE A.Ş. - CORENDON ALANYASPOR | 3 - 0 | Ev | ✅ | HIGH |
| KASIMPAŞA A.Ş. - SAMSUNSPOR A.Ş. | 4 - 1 | Ev | ✅ | HIGH |
| KOCAELİSPOR - GÖZTEPE A.Ş. | 1 - 2 | Beraberlik | ❌ | LOW |
| İSTANBUL BAŞAKŞEHİR FK - GAZİANTEP FUTBOL KULÜBÜ A.Ş. | 2 - 1 | Beraberlik | ❌ | LOW |
| TRABZONSPOR A.Ş. - BEŞİKTAŞ A.Ş. | 2 - 0 | Ev | ✅ | LOW |

## Hafta 7 — 6/9 isabet (%67)

| Maç | Skor | Tahmin | Sonuç | Güven |
| --- | --- | --- | --- | --- |
| GALATASARAY A.Ş. - KASIMPAŞA A.Ş. | 3 - 1 | Ev | ✅ | HIGH |
| GENÇLERBİRLİĞİ - AMED SPORTİF FAALİYETLER | 2 - 2 | Deplasman | ❌ | MEDIUM |
| CORENDON ALANYASPOR - ERZURUMSPOR FK | 0 - 0 | Ev | ❌ | HIGH |
| SAMSUNSPOR A.Ş. - TRABZONSPOR A.Ş. | 0 - 3 | Deplasman | ✅ | HIGH |
| ÇAYKUR RİZESPOR A.Ş. - FENERBAHÇE A.Ş. | 0 - 3 | Deplasman | ✅ | HIGH |
| TÜMOSAN KONYASPOR - İSTANBUL BAŞAKŞEHİR FK | 0 - 0 | Deplasman | ❌ | MEDIUM |
| GAZİANTEP FUTBOL KULÜBÜ A.Ş. - ARCA ÇORUM FK | 0 - 3 | Deplasman | ✅ | MEDIUM |
| BEŞİKTAŞ A.Ş. - KOCAELİSPOR | 2 - 1 | Ev | ✅ | HIGH |
| EYÜPSPOR - GÖZTEPE A.Ş. | 0 - 4 | Deplasman | ✅ | LOW |

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
| ÇAYKUR RİZESPOR A.Ş. - SAMSUNSPOR A.Ş. | 0 - 2 | Ev | ❌ | LOW |
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
| TÜMOSAN KONYASPOR - ÇAYKUR RİZESPOR A.Ş. | 0 - 1 | Ev | ❌ | MEDIUM |
| GAZİANTEP FUTBOL KULÜBÜ A.Ş. - CORENDON ALANYASPOR | 1 - 1 | Deplasman | ❌ | MEDIUM |
| GENÇLERBİRLİĞİ - FENERBAHÇE A.Ş. | 2 - 1 | Deplasman | ❌ | HIGH |
| İSTANBUL BAŞAKŞEHİR FK - KOCAELİSPOR | 2 - 0 | Ev | ✅ | HIGH |
| AMED SPORTİF FAALİYETLER - ERZURUMSPOR FK | 3 - 0 | Ev | ✅ | LOW |
| BEŞİKTAŞ A.Ş. - EYÜPSPOR | 1 - 0 | Ev | ✅ | HIGH |
| SAMSUNSPOR A.Ş. - GÖZTEPE A.Ş. | 3 - 3 | Ev | ❌ | LOW |

