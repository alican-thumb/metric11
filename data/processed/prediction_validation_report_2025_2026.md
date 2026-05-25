# Tahmin Doğrulama Raporu 2025/26

## Ölçüm Sınırı

- Beşiktaş ekran kuralları aynı sezon örnekleri incelenerek ayarlandığı için bağımsız doğrulama değildir.
- Bu nedenle Beşiktaş ekran oranı performans kontrolüdür; genel doğruluk vaadi değildir.
- Diğer takımlarda takım-özel ekran düzeltmesi kapalıdır; aşağıdaki oran ham model başlangıç ölçümüdür.

## Sonuçlar

| Ölçüm | Doğruluk | Kullanım |
|---|---:|---|
| Beşiktaş ham model | %51.7 (15/29) | Başlangıç karşılaştırması |
| Beşiktaş ekran ayarı | %65.5 (19/29) | Aynı veri üzerinde kontrol, genellenemez |
| Diğer 17 takım ham model | %49.3 (243/493) | Lig-geneli geliştirme başlangıcı |
| Tekil lig fikstürleri ham model | %51.0 (134/263) | Çift sayım yapılmamış taban ölçüm |

## Kalite Kapıları

- PASS: Takım dışı kalibrasyon engeli - Beşiktaş için ayarlanmış ekran düzeltmesi diğer takımlarda uygulanmaz.
- PASS: Bağımsız doğrulama - Sezon ortası (hafta 18+) walk-forward OOS testi eklendi: %53.6 doğruluk, HIGH güven %60.4. oos_validation raporu güncel.
- PASS: Yayın dili - Lig-geneli raporda hedef takım ve rakip isimleri tahmin etiketine doğru yazılır.

## Sonraki Doğrulama

- Ekran kalibrasyonu yeni sezon kronolojik sonuçlarında sabit kurallarla test edilmeden kullanıcıya yüksek doğruluk iddiası gösterilmemeli.
- Sakat/cezalı, kesin ilk 11, piyasa değeri farkı ve odds tabanı bağlandıktan sonra her özellik için ayrı katkı deneyi çalıştırılmalı.