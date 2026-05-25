# Veri Analiz ve İstatistik Planı

Güncelleme: 2026-05-24

Bu plan, mevcut MVP'nin veri toplama hattından sonraki asıl darboğaza odaklanır: istatistiksel güven, model kalibrasyonu ve scout sinyali kalitesi.

## Mevcut Analitik Gerçek

- TFF tabanlı sezon kapsamı güçlü: 306 maç, 691 oyuncu, 812 gol ve 1428 kart olayı.
- SQLite ambar hazır ve sorgulanabilir durumda.
- Oyuncu yaş/profil zenginleştirme kapsamı 691/691 seviyesine geldi.
- Gol adayı modeli ürünleşmeye en yakın sinyal: Top 5 %73, Top 8/Top 10 %85.
- Maç sonucu modeli MVP seviyesinde: Beşiktaş özelinde %55, lig genelinde %50.
- En büyük hata tipi beraberlik: Beşiktaş tahmin hatalarının 9 tanesi kaçan beraberlik.

## Öncelik 1: Veri Kalite Scorecard

Amaç her pipeline çalışmasında analitik güveni ölçmek.

Üretilecek/üretilen dosyalar:

- `data/processed/data_quality_scorecard_2025_2026.json`
- `data/processed/data_quality_scorecard_2025_2026.md`

Kontroller:

- sezon maç kapsamı
- hakem eksikliği
- oyuncu profil eksikliği
- maç tahmini doğruluğu
- beraberlik yakalama oranı
- yüksek güvenli hata oranı
- gol adayı Top 5/Top 8 isabeti
- scout pozisyon güveni

## Öncelik 2: Baseline Model Karşılaştırması

Mevcut Poisson/Elo modelinin gerçekten değer katıp katmadığı ayrı ölçülmeli.

Üretilecek/üretilen dosyalar:

- `data/processed/model_baseline_comparison_2025_2026.json`
- `data/processed/model_baseline_comparison_2025_2026.md`

Karşılaştırılacak baseline'lar:

- her zaman ev sahibi
- puan/maç üstünlüğü
- son 5 maç formu
- Elo-only
- Poisson-only
- mevcut hybrid model

Ana metrikler:

- accuracy
- draw recall
- Brier score
- log loss
- high confidence miss rate

İlk bulgu:

- Mevcut hybrid model accuracy'de %50.4, log loss'ta 1.027.
- Saf Poisson baseline accuracy'de %51.2 ile az farkla önde.
- Mevcut hybrid model log loss'ta en iyi; yani olasılık kalibrasyonu tarafında değer katıyor.
- Güçlü modellerin draw recall oranı %0; beraberlik için ayrı risk katmanı gerekliliği doğrulandı.

## Öncelik 3: Beraberlik Risk Modeli

Beraberlik ana tahmine agresif basılınca doğruluk düştüğü için ayrı risk katmanı olmalı.

Üretilecek/üretilen dosyalar:

- `data/processed/draw_risk_audit_2025_2026.json`
- `data/processed/draw_risk_audit_2025_2026.md`

Yeni sinyal:

- `draw_risk_score`
- `protected_prediction`
- `avoid_strong_side_pick`
- `low_edge_match`

Önerilen girdiler:

- dar xG farkı
- dar takım gücü farkı
- iki takım draw rate'i
- düşük toplam gol beklentisi
- büyük maç etiketi
- hakem kart temposu
- son form oynaklığı

İlk bulgu:

- Ana lig modeli beraberlikleri doğrudan tahmin etmiyor: draw recall %0.
- Beraberlik risk katmanı MEDIUM/HIGH bayrakla 46/76 beraberliği yakaladı: %60.5 recall.
- Precision %31.9; gerçek beraberlik baz oranı %29.5 olduğu için bu katman kesin X tahmini değil, taraf tahminini korumaya alma uyarısı olarak kullanılmalı.
- Risk sonrası hâlâ kaçan 30 beraberlik var; bunların önemli kısmında model xG farkını geniş gördüğü için yeni veri olarak oyun akışı/odds/derbi bağlamı gerekiyor.
- Korumalı aksiyon backtesti Beşiktaş özelinde eklendi: 29 maçta 22 korumalı aksiyon, 7/22 gerçek beraberlik (%31.8), 11/22 doğru kalan taraf tahmini. Beraberlik dışı 4 yanlış taraf vakası sonraki model önceliği.
- Bu 4 yanlış taraf vakası etiketlendi: 3 target side overrated, 1 opponent side overrated, 2 big match side flip, 4 high draw risk but decisive result. Bu sonuç odds/kadro değeri/sakatlık/oyun akışı verisini sadece beraberlik için değil, taraf gücü kalibrasyonu için de gerekli kılıyor.
- Side flip denetimi eklendi ve rakip piyasa değeri snapshot'ı bağlandı: güncel ekran tahmini sonrası 3 yanlış taraf vakası var; 2 Beşiktaş tarafını fazla değerleme, 1 rakibi fazla değerleme. Rakip piyasa değeri 3/3 vakada kapsanıyor; kalan ortak boşluklar odds baseline, resmi sakatlık akışı ve doğrulanmış maç günü 11 kalitesi.
- Backtest dashboard'u ve komuta merkezi artık lig geneli draw risk, Beşiktaş korumalı aksiyon metrikleri, yanlış taraf market edge'i ve kalan veri boşluklarını birlikte gösteriyor.

## Öncelik 4: Gol Adayı Segment Backtest

Genel Top 5/Top 8 iyi, fakat aday tipleri ayrı ölçülmeli.

Üretilecek/üretilen dosyalar:

- `data/processed/goal_candidate_segment_backtest_2025_2026.json`
- `data/processed/goal_candidate_segment_backtest_2025_2026.md`

Segmentler:

- primary golcü
- penaltı profili
- duran top/defans
- sonradan giren etki
- büyük maç golcüsü
- orta saha geç koşu profili

Hedef:

- Top 5'i %73'ten %80 bandına taşımak.
- Top 8/10 isabetini korurken ilk 3 sıralamasını güçlendirmek.

İlk bulgu:

- Primary segment maç bazında güçlü: %75.9 maç hit rate.
- Impact-sub segment ayrıca değerli: %55.2 maç hit rate; ayrı "sonradan gol" alanı olarak gösterilmeli.
- Set-piece defender segmenti zayıf: %4.0 maç hit rate ve Top 5'te %0.
- Penalty profile segmenti mevcut veriyle isabet üretmedi; gerçek penaltıcı doğrulanmadan üst sıra bonusu sınırlanmalı.
- Bu bulgu modele işlendi: set-piece defender ve doğrulanmamış penalty profile ağırlıkları düşürüldü. Sonraki backtestte Top 3 %62, Top 5 %77, Top 8 %85, Top 10 %88 oldu.
- Beraberlik risk katmanı maç önü preview/dashboard akışına işlendi; model aksiyonu kullanıcıya "Korumalı taraf tahmini" gibi Türkçe etiketlerle gösteriliyor.
- Bu aşamadaki scorecard 88.3/100 idi; daha sonra eklenen lig-geneli eşleşme ve düşük pozisyon güveni kapıları açıklanan riskleri puanlamaya dahil eder.

## Öncelik 5: Büyük Maç Özel Modeli

Derbi ve büyük maçlar normal lig maçı gibi ele alınmamalı.

Girdiler:

- büyük maç geçmişi
- hakem kart profili
- kadro uyum oranı
- iki takım güç farkı
- kart/tempo riski
- beraberlik eğilimi

Çıktı önce risk sınıfı olmalı; taraf tahmini ikincil kalmalı.

## Öncelik 6: Scout Güven Katmanı

Scout çıktısında skor kadar veri güveni de gösterilmeli.

Takip edilecek alanlar:

- pozisyon güveni
- yaş/sözleşme kapsamı
- piyasa değeri kapsamı
- boy/ayak eksikliği
- rol-fit sinyali kaynağı
- düşük proxy aday oranı

## 2026-05-25 Lig Geneli Uygulama Sonucu

- Transfermarkt lig snapshot'ı 18/18 takım, 512 oyuncu ve toplam €1,378,850,000 piyasa değeri kapsıyor.
- TFF lig profil havuzu tamamlandı: maç kadrosunda yer alan 691/691 oyuncu resmi TFF profiliyle işleniyor; ayrı tutulduğu için önceki paydada görünmeyen Beşiktaş profilleri de kapsama alındı.
- Transfermarkt lig profil-tam-ad katmanı toplandı: 18/18 takım, 512/512 oyuncu profil sayfası, 277 resmi ek tam-ad alanı ve 0 başarısız profil.
- Oyuncu zenginleştirmesi kulüp içinde eşleşme şartıyla sıkılaştırıldı ve canonical/Latin/profil-tam-ad normalizasyonu bağlandı: 498/691 TFF profili eşleşti (%72.1), lig snapshot kapsamındaki 626 profilde oran %79.6; takım dışı yanlış isim bağlama riski kaldırıldı.
- `Juan`, `Carlo Holse`, `Fred`, `Show`, `Ruan`, `Héliton` ve `Janderson` gibi kısa adlar tekil yamalar yerine profil tam-ad katmanıyla doğrulanabilir hale geldi; scout önerisini bloke eden eşleşmeyen oyuncu sayısı 0.
- `transfermarkt_match_review_queue_2025_2026` raporu 18 takım kapsama tablosu ile kalan 193 profilin tamamını açıklanabilir kuyruğa ayırıyor: 65 snapshot dışı, 128 mevcut snapshot içinde güvenilir aday bulunmayan profil. Lig-içi çözülmemiş kuyruğun 13 kaydı yüksek kullanımlı, 115 kaydı rotasyon kullanımlıdır.
- Zengin scout ve pozisyon matrisi lig-geneli enriched profile bağlandı; Transfermarkt pozisyon allowlist'i ara matris ve yayın blueprint'inde uygulanır. Doğrulanmış santrforlar artık kanat rolüne taşınmaz.
- İlk-40 scout sınırı kaldırıldı: zengin scout ve FM hesapları maç kadrosundaki 691/691 oyuncunun tamamını işler; pozisyon matrisi yayınında doğrulanmış pozisyona sahip 84 rol-aday eşleşmesi bulunur ve doğrulanmamış üst-aday yayımlanmaz.
- Scorecard yeni kapsama kapılarını içererek 84.1/100 ölçüyor; lig içi TFF/Transfermarkt eşleşme oranı %79.6 `WATCH`, scout bloke eden eşleşme 0 `PASS`, düşük pozisyon güveni 0/275 `PASS`.
- `league_market_value_audit_2025_2026` raporu lig modelinin 258/258 maçını değer baseline'ıyla karşılaştırıyor.
- Sabit `draw_band=0.20` değer baseline doğruluğu %51; mevcut lig modelinin doğruluğu da %51. Bu snapshot aynı sezon/sonraki değer değişimlerini içerebildiği için üretim tahmin özelliği sayılmayacak.
- Tüm takım maç önü arşivi 18 takım ve 522 rapor olarak üretildi; takım etiketleri hedef takım adına göre doğrulandı.

Sıradaki istatistiksel iş, yeni sinyali modele eklemek değil; odds baseline ve resmi sakatlık/muhtemel 11 verisini aynı lig-geneli kapsamla getirip çok sezonlu zaman-ayrımlı doğrulama yapmaktır.

## Yeni Veri Öncelikleri

En yüksek getirili veri sırası:

1. Çok sezonlu TFF maç geçmişi.
2. Şut, korner, topa sahip olma, pas, asist, oyuncu maç istatistiği.
3. Odds veya piyasa beklentisi baseline'ı.
4. Resmi sakat/cezalı ve muhtemel 11 kaynakları.
5. Oyuncu pozisyon, boy, ayak, piyasa değeri kapsamı.
6. Lisansı temiz attribute dataset.

## Gerçekçi Başarı Hedefleri

- Maç sonucu yön eğilimi: önce %60-65 bandı.
- Beraberlik risk uyarısı: kaçan beraberlikleri ayrı görünür kılmak.
- Gol adayı Top 5: %80 bandı.
- Gol adayı Top 8/10: %85 seviyesini korumak.
- Scout: düşük pozisyon güvenli aday oranını %30 altından %10 altına indirmek.
