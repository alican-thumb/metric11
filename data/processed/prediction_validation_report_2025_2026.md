# Tahmin Doğrulama Raporu 2025/26

## Ölçüm Sınırı

- Beşiktaş ekran kuralları aynı sezon örnekleri incelenerek ayarlandığı için bağımsız doğrulama değildir.
- Bu nedenle Beşiktaş ekran oranı performans kontrolüdür; genel doğruluk vaadi değildir.
- Diğer takımlarda takım-özel ekran düzeltmesi kapalıdır; aşağıdaki oran ham model başlangıç ölçümüdür.

## Sonuçlar

| Ölçüm | Doğruluk | Kullanım |
|---|---:|---|
| Beşiktaş ham model | %51.7 (15/29) | Başlangıç karşılaştırması |
| Beşiktaş ekran ayarı | %55.2 (16/29) | Aynı veri üzerinde kontrol, genellenemez |
| Diğer 17 takım ham model | %46.7 (230/493) | Lig-geneli geliştirme başlangıcı |
| Tekil lig fikstürleri ham model | %50.2 (132/263) | Çift sayım yapılmamış taban ölçüm |

## Kalite Kapıları

- ✓ Takım dışı kalibrasyon engeli — Beşiktaş için ayarlanmış ekran düzeltmesi diğer takımlarda uygulanmaz.
- ✓ Bağımsız doğrulama — Sezon ortası (hafta 18+) walk-forward OOS testi eklendi: %53.6 doğruluk, HIGH güven %60.4. oos_validation raporu güncel.
- ✓ Yayın dili — Lig-geneli raporda hedef takım ve rakip isimleri tahmin etiketine doğru yazılır.

## Sonraki Doğrulama

- Ekran kalibrasyonu yeni sezon kronolojik sonuçlarında sabit kurallarla test edilmeden kullanıcıya yüksek doğruluk iddiası gösterilmemeli.
- Sakat/cezalı, kesin ilk 11, piyasa değeri farkı ve odds tabanı bağlandıktan sonra her özellik için ayrı katkı deneyi çalıştırılmalı.