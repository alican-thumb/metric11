# Metric11: Süper Lig için 90 günlük ürün planı (28 Kasım 2026)

## Karar ve kanıt

Önce taraftar ürünü: Her hafta takımının maçına hazırlan, kendi tercihini dene, maç bitince modelle karşılaştır. Ana ölçüt toplam sayfa değil, bir sonraki lig haftasında geri gelip ikinci bir maçla etkileşen taraftar oranı. Kulüp satışları ayrı bir hipotez; trafik veya ödeme isteği henüz kanıtlanmadı.

| İncelenen ürün | Doğrulanabilen teklif | Bizim kararımız |
|---|---|---|
| [FotMob](https://www.fotmob.com/my/topnews/3949) | Maç içinde şut haritası, canlı xG ve fantasy puanları | Canlı skor hızında yarışma; karar öncesi gerekçe ve maç sonrası hesap ver. |
| [Comparisonator](https://comparisonator.com/tr/) | Pozisyon ve lig bazlı karşılaştırma, benzerlik, sanal transfer | Sadece benzer oyuncu listesi fark yaratmaz. İhtiyacı, alternatifi, maliyet belirsizliğini ve ödünleşmeyi açıkla. |
| [DataMB](https://datamb.football/guide/index.html?lang=tr) | Pozisyona göre yüzdelikler ve oyuncu radarları | Bir yüzdeliğin yanında referans ligi, sezon, dakika ve örneklem olsun. |
| [Analist Ligi](https://analistligi.com/) | Spor analisti yetiştirme konumlandırması; iç akış doğrulanamadı | Taraftar katılımını deneyle doğrula; rakibin özellik veya büyüklüğü hakkında çıkarım yapma. |

Ürün sayfaları pazardaki teklifleri gösterir, kullanım veya gelir kanıtı değildir. [Metric11 ana sayfasında](https://metric11.com/) şampiyonluk, kadro ve karne zaten var. Aynı anda hafta 13 için “bu hafta” ve “geçen hafta” denmesi; Samsunspor maçında en yüksek olasılık deplasmandayken beraberlik seçiminin açıklanmaması somut sürtünmeler. Ayrıca hazırlık haberi transfer olarak etiketlenmiş. Mobil kullanım araştırması henüz yapılmadı.

## Uygulama ve karar kapıları

| Sıra | Teslim | Kabul / durdurma koşulu |
|---|---|---|
| 1. Hafta 1: kanıt | Tahmini başlama anından önce UTC zaman damgası ve model sürümüyle sakla. Erteleme, tarihi belirsiz maç, ilk kez sonuçla gelen kayıt ve tekrar koşma testleri. Sonuç (1X2), tam skor, golcü ve kart karnelerini ayır. | İleriye dönük her kayıtta zaman damgası doğrulanmış başlangıçtan önce. Eksikler paydadan sessizce düşmez; toplam kapsam ayrıca yazılır. |
| 2. Hafta 1–2: veri | Kaynak başına son deneme, son dolu yanıt, takım ve alan doluluğu. TFF kadrolarını kulüp/tarih/oyuncu kimliğiyle eşle. Sakat, cezalı, şüpheli ve bilinmeyeni ayır. | 18 takım için güncellik görünür; boş fiyat sıfır avro olmaz; bir maçta oynamamak ayrılık veya sakatlık kanıtı sayılmaz. Yeniden kullanım izni belirsiz alan yayımlanmaz. |
| 3. Hafta 2–4: maç merkezi | Mobil ilk ekranda favori, temel gerekçe, belirsizlik ve tek eylem: kendi tahminini yap. Maç sonrası aynı adres gerçek sonuç ve kaçırılan varsayımı gösterir. Şampiyonluk ekranına “bu maç kazanılırsa / kaybedilirse” karşılaştırması. | 5 taraftarla görev testi; en az 4'ü yardım almadan favoriyi, belirsizliği ve kendi seçimini bulmalı. 360 px genişlikte yatay taşma olmamalı. |
| 4. Hafta 3–8: model | Haftalık ilerleyen testte mevcut model, basit ev avantajı ve Poisson ile aynı fikstürde alternatif modeli karşılaştır. Sakatlık ve ilk 11 sinyallerini tek tek aç/kapat. | İlk 30 kilitli maç yalnız ara kontrol. Sezon/hafta ve kapsama göre log loss, Brier, isabet, beraberlik precision/recall raporlanmadan üretim modeli değişmez. Küçük farkı başarı sayma. |
| 5. Hafta 4–8: scout | Beşiktaş ve farklı bütçeli ikinci bir kulüpte iki rol pilotu. Her rol için mevcut kadrodan çözüm + üç dış aday: güncel dakika, yaş, sözleşme, rol kanıtı, maliyet tarihi, karşı argüman. | İzleme listesine alınan her adayın takım ve pozisyonu doğrulanır. Ölçülmeyen koşu km'si, maaş ve bonservis üretilmez. “Oynasaydı” çıktısı aynı rakip ve dakika varsayımında olasılık farkıdır, nedensel sonuç değildir. |
| 6. Hafta 2–12: dağıtım | Derbi dosyası, haftalık şampiyonluk değişimi ve bir genç oyuncu için paylaşılabilir kartlar. Mevcut kalıcı sayfaya yönlendir; özel grup daveti ve maç sonrası karne dönüşünü ölç. | Dört maç haftasında arama gösterimi → maç sayfası → tahmin kaydı → sonraki hafta dönüşü ayrı ölç. Küçük örneklemde kanal kazananı ilan etme. |

## Kapsam ve bütçe

Mevcut statik HTML + JSON'u herkese açık analizler için, Next.js'i kişisel kadro ve oyun için koru. Sırf tasarım için yeniden yazma; iki alan arasında ortak maç kimliği, görünüm ve kampanya ölçümü kullan. Önce isimsiz toplam olay sayıları; kişisel veriyi analiz deposuna kopyalama. Kaynak koşulları ve kullanılan barındırma planının ticari kullanım şartları doğrulanmadan reklam/sponsor başlatma.

Bu çeyrekte satın alma yok. 1. Lig ancak bir tam maç haftasında fikstür, sonuç ve kadro kapsamı ölçülüp eksikleri açıklandığında pilot olur. Avrupa, yerel uygulama, canlı takip verisi ve kulüp aboneliği bekler. Kulüp ürünü için geliştirmeden önce iki scout ve bir spor editörüyle örnek rapor üzerinden görüş; hangi kararı değiştirdiğini ve neye ödeme yapacaklarını sor.
