# Kullanıcıya Gösterilebilir Kaynak Özeti

- Sezon: 2025-2026
- Not: Bu özet gerçek kaynak takibini saklamaz; sadece ürün arayüzünde kullanılacak güvenli kategori dilini üretir.

## Kaynak Kategorileri

- Resmi federasyon maç verisi (SCRAPING, risk=MEDIUM): Süper Lig 306 maç
- Resmi federasyon oyuncu profili (SCRAPING, risk=MEDIUM): Beşiktaş 46 oyuncu + scout kısa liste 25 oyuncu
- Piyasa değeri ve kadro profili (SCRAPING, risk=HIGH): Beşiktaş 2025/26 kadro: pozisyon ve piyasa değeri
- Model türetilmiş uygunluk sinyali (DERIVED+MANUAL, risk=MEDIUM): Beşiktaş 2025/26 kart cezası çıkarımı + manuel sakat/cezalı override dosyası
- Oyuncu attribute ve potansiyel veri seti (OPEN_DATASET_OR_VERIFIED_EXPORT, risk=LOW_TO_HIGH_BY_LICENSE): 4 aday kaynak kaydı; normalize import varsa 0 oyuncu
- Dış futbol API doğrulama ve geçmiş sezon zenginleştirme (API, risk=MEDIUM): 2024 sezonu ücretsiz planda erişilebilir; 2025 sezonu plan kısıtı nedeniyle boş dönüyor

## Politika

- Her veri kaynağı içeride gerçek ad, lisans durumu, risk ve güven etiketiyle tutulur.
- Kullanıcıya yalnızca izinli kaynak adı veya genel kaynak kategorisi gösterilir; lisans/izin sorunu olan veri ticari ürüne alınmaz.
- Kaynağı gizleyerek lisans, robots, kullanım şartı veya telif riskini aşma yöntemi kullanılmaz.