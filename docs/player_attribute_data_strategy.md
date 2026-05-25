# Oyuncu Attribute Veri Stratejisi

Bu projede Football Manager hissi veren scout önerisi üretmek istiyoruz. Bunun için oyuncunun sadece gol/ilk 11 geçmişi yetmez; teknik, mental, fiziksel, potansiyel ve rol uyumu sinyalleri gerekir.

## Güvenli Kullanım Kuralı

Football Manager veritabanı doğrudan ticari bir ürünün parçasıdır. Oyun dosyası dump'ı, izinsiz export veya lisansı belirsiz mirror veri kaynakları ürün veri tabanına kör şekilde alınmayacak.

Kaynak adını gizlemek lisans veya kullanım şartı sorununu çözmez. Bu yüzden iki seviyeli gösterim kullanılır:

- İç sistem: gerçek kaynak adı, URL, lisans durumu, risk seviyesi ve güven skoru saklanır.
- Ürün arayüzü: izin durumuna göre "açık veri seti", "resmi maç verisi", "model türetilmiş sinyal" gibi genel kategori gösterilebilir.
- Engellenen yaklaşım: ticari kullanım hakkı olmayan veriyi kaynağını saklayarak ürüne koymak.

Kullanılabilir kaynaklar:

- Lisansı açık Kaggle/GitHub CSV veri setleri.
- Kullanım hakkı doğrulanmış kullanıcı exportları.
- CC0/Public Domain FIFA/European Soccer Database gibi attribute kaynakları.
- Manuel araştırma için FM database görüntüleyicileri, ancak otomatik ticari scraping yapılmadan.

## Modele Eklenecek Sinyaller

- `current_ability`: bugünkü kalite seviyesi.
- `potential_ability`: gelişim tavanı.
- `growth_room`: potansiyel - mevcut seviye.
- `pace`, `acceleration`, `stamina`, `work_rate`, `teamwork`: fiziksel/tempo profili.
- `finishing`, `passing`, `tackling`, `positioning`, `decisions`: rol bazlı ana yetenekler.
- `role_fit_score`: Beşiktaş veya seçilen takımın ihtiyaç rolüne göre 0-100 uyum.
- `resale_potential_score`: yaş + potansiyel + piyasa değeri + süre kombinasyonu.

## Ürün İçindeki Rolü

Bu veri maç sonucu tahmininde ana karar verici olmayacak. Scout ve takım ihtiyaç modülünde ek sinyal olacak:

- "Bu oyuncu ucuz ama potansiyeli yüksek."
- "Bu oyuncu mevcut oyuna hemen katkı verir."
- "Bu oyuncu tempo/pres isteyen orta saha rolüne uyuyor."
- "Bu oyuncunun resale potansiyeli yüksek."

## İthalat Akışı

1. CSV dosyası `data/manual/player_attribute_imports/` altına konur.
2. `python -m src.import_player_attribute_dataset --input ... --source-name ... --license-status ...` çalıştırılır.
3. Normalleştirilmiş çıktı `data/processed/player_attribute_dataset_normalized.json` olur.
4. Scout modeli bu dosyayı bulursa fırsat skoruna attribute tabanlı rol/potansiyel sinyali ekler.

## Risk Etiketleri

- `LOW`: CC0/Public Domain veya açık lisans.
- `MEDIUM`: lisans doğrulaması gerekli, araştırma/MVP için kullanılabilir.
- `HIGH`: kullanım şartları belirsiz, ticari ürün için otomatik kullanılmamalı.
