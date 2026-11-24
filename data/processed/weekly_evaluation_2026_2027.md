# 2026-27 Süper Lig — Haftalık Tahmin Karnesi

Oynanan her maçın sonucu, tahmin motorunun takım formu/Elo durumunu ilerletir; bu yüzden bir sonraki haftanın skor tahminleri geçen haftanın gerçek sonuçlarıyla güncellenir. Doğrulanan transferler de aynı şekilde güce yansır.

## Genel Karne

- Değerlendirilen maç: **0**
- İsabet: **0/0** (%0)
- Beraberlik yakalama: **0/0** (—)
- Yüksek güvenli maç isabeti: **0/0** (—)
- Güçlü seçim tanı metriği: **0/0** (—), kapsam —
- İleriye dönük kilitli güçlü seçim: **0/0** (—), kapsam —
- Brier score: **—** (düşük daha iyi; 2025-26 referans 0.600)
- Log loss: **—** (düşük daha iyi; 2025-26 referans 1.005)

_Tanı metriği bugünkü yayın politikasını geçmiş maçlara uygular ve ürün iddiası değildir. İleriye dönük metrik, karar maçtan önce snapshot'a kilitlendikten sonra birikir._

### Güven bandı kalibrasyonu

_"Beyan edilen ort. olasılık" ile "İsabet" arasındaki fark büyükse (özellikle isabet daha düşükse) model o banttaki kendine güvenini haklı çıkaramıyor demektir. İsabet oranı tek başına aldatıcı olabilir — favoriyi seçip düşük bir olasılıkla tutturmak yüksek isabet ama kötü kalibrasyon demektir. Brier/log loss olasılıkların KENDİSİNİN kalitesini ölçer (düşük = iyi). Referans sütunu geçmiş sezonun 258 maçlık backtest'inden — küçük örneklemli erken hafta sapmalarını buna göre yorumlayın._

| Güven bandı | Maç | İsabet | Beyan edilen ort. olasılık | Brier | Log loss | Referans (2025-26: isabet / brier / logloss) |
| --- | --- | --- | --- | --- | --- | --- |
| HIGH | 0 | — | — | — | — | %64 / 0.516 / 0.885 |
| MEDIUM | 0 | — | — | — | — | %54 / 0.619 / 1.032 |
| LOW | 0 | — | — | — | — | %48 / 0.670 / 1.103 |

### Seçilen tarafa göre isabet

_Model hangi tarafı seçtiğinde ne oldu? Belirli bir seçimde (ör. deplasman favorisi) sistematik hata varsa burada görünür. MEDIUM bandı canlı isabeti %35'in altında kaldıkça fikstür sayfasında bu bant "Kararsız" olarak gösterilir._

| Seçim | Maç | İsabet | Gerçekleşen (Ev / X / Dep) |
| --- | --- | --- | --- |

[Olasılık kovaları ve seçici yayın politikası →](prediction_calibration_audit_2026_2027.html)

_Sezon henüz başlamadı; ilk maçlar oynandıkça karne otomatik dolacak._

