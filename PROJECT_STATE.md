# Futbol İstihbarat Platformu - Proje Durumu

Son güncelleme: 2026-05-26 (session 6)

## Amaç

Futbolseverler için maç önü analizleri, oyuncu bazlı tahminler, hakem etkisi, gol/kart adayları, takım ihtiyaç analizi ve Football Manager hissi veren scout önerileri üreten veri odaklı bir futbol istihbarat platformu geliştirmek.

Ürün hedefi sadece maç sonucu vermek değil; kullanıcıya "neden?" sorusunun cevabını da anlatan, hikayeli ve rakamsal analizleri birlikte sunan bir deneyim oluşturmak.

## Şu Ana Kadar Yapılanlar

### Veri Toplama

- TFF maç detay sayfaları için scraper/parser yazıldı.
- TFF 2025-2026 Süper Lig fikstürü 1-34 hafta tarandı.
- Beşiktaş 2025-2026 sezonu özel veri seti çıkarıldı.
- Tüm Süper Lig 2025-2026 sezonu çekildi.
- Takım isimleri için alias/normalizasyon katmanı eklendi.

Toplanan lig ölçeği:

- 306 Süper Lig maç detayı
- 6.732 ilk 11 oyuncu kaydı
- 6.000 yedek oyuncu kaydı
- 1.428 kart olayı
- 812 gol olayı

Parse edilen alanlar:

- takım isimleri
- skor
- maç tarihi
- organizasyon
- stat
- hakem / yardımcı hakem / VAR / AVAR
- ilk 11
- yedekler
- kartlar
- gol atan oyuncular
- gol dakikası
- gol tipi
- oyuncu TFF ID
- kulüp TFF ID

### Analiz Katmanları

- Beşiktaş sezon özeti üretildi.
- Oyuncu ilk 11, yedek, kart ve gol metrikleri çıkarıldı.
- Hakem kart profilleri çıkarıldı.
- Büyük maç/derbi kırılımları eklendi.
- Maç önü preview motoru yazıldı.
- Gol adayı sinyali eklendi.
- Maç sonucu ve gol adayı backtest raporları üretildi.
- Tüm lig için scout kısa listesi üretildi.
- Tüm lig için kronolojik Poisson/Elo MVP tahmin modeli üretildi.
- Maç tahminlerine güven seviyesi ve risk bayrakları eklendi.
- Tahmin ve gol adayı backtest dashboard'u üretildi.
- Beşiktaş dashboard'una seçilen maç için "Model Kontrolü" bölümü eklendi.
- TFF oyuncu profil scraper/parser eklendi.
- Beşiktaş 2025-2026 için 46 oyuncu profili toplandı.
- Beşiktaş takım ihtiyaç analizi üretildi.
- Beşiktaş takım ihtiyaç dashboard'u üretildi.
- Scout kısa listesindeki ilk 25 oyuncu için TFF profil verisi toplandı.
- Yaş/sözleşme ile zenginleştirilmiş scout raporu ve dashboard'u üretildi.
- Gol adayı modeli rakip savunma gol yeme profiliyle güçlendirildi.
- Ana ürün giriş paneli üretildi.
- Veri kataloğu/kapsam raporu üretildi.
- Transfermarkt Beşiktaş 2025/26 kadro parser'ı eklendi.
- Beşiktaş takım ihtiyaç analizine pozisyon grubu ve piyasa değeri bağlandı.
- Sakat/cezalı oyuncu için oyuncu uygunluk katmanı eklendi.
- Kırmızı kart ve kart birikiminden otomatik ceza sinyali üretiliyor.
- Manuel sakat/cezalı override dosyası eklendi.
- Maç önü motoru eksik oyuncuları muhtemel 11 ve gol adayı listesinden çıkarıyor, beklenen gol/güven hesabına bağlıyor.
- Football Manager/FIFA tarzı oyuncu attribute veri stratejisi eklendi.
- Lisansı açık veya kullanıcı kullanım hakkı olan CSV dosyalarını normalize edecek attribute import hattı eklendi.
- Zenginleştirilmiş scout modeli attribute dosyası varsa current ability, potential ability, gelişim alanı ve rol-fit sinyalini fırsat skoruna katacak şekilde hazırlandı.
- İç kaynak takibi ile kullanıcıya gösterilebilir genel kaynak kategorisini ayıran kaynak gösterim politikası eklendi.
- FM tarzı rol bazlı scout programı eklendi: skor katkısı, fizik motoru, genç/resale değer, sözleşme fırsatı ve düşük riskli düzenli oyuncu listeleri üretiyor.
- Oyuncular için türetilmiş tahmini fiziksel yük aralığı eklendi.
- Futbol komuta merkezi eklendi: tahmin, maç önü, gol adayı, eksik oyuncu, FM scout ve takım ihtiyacını tek ekranda topluyor.
- API-Football dış API bağlantısı eklendi ve gerçek snapshot denendi.
- API-Football ücretsiz planda 2024 sezonu erişilebilir; 2025 sezonu plan kısıtı nedeniyle boş dönüyor.
- API-Football 2024 snapshot verisi normalize edildi: takım gücü, fikstür ve oyuncu attribute havuzu üretildi.
- Ana ürün sitesi responsive üst navigasyon, komuta merkezi bağlantısı ve veri omurgası özetiyle yenilendi.
- Teknik direktör kadro denetimi eklendi: gerçek ilk 11, modelin önerdiği çekirdek kadro ile karşılaştırılıyor.
- Maç önü raporları artık "hoca doğru kadro mu çıkardı?" sorusuna kadro uyum oranı, tartışmalı tercih etiketi, dışarıda kalan çekirdek oyuncular ve alternatif xG/skor senaryosu ile cevap veriyor.
- Beşiktaş maç önü dashboard'una Teknik Direktör Kadro Denetimi bölümü eklendi.
- Analistliği benzeri taraftar/taktik tartışması fikri ürünleştirildi; site doğrudan içerik olarak okunamadı, kullanıcı tarifindeki konsept veri modülüne çevrildi.
- Takım gücü katmanı eklendi: puan/maç, gol farkı, son form, iç/dış saha performansı ve kadro sürekliliği 100 üzerinden güç skoruna çevriliyor.
- Beşiktaş maç önü tahmin motoru takım gücü farkını xG, kazanma olasılığı ve anlatılı analiz içine dahil ediyor.
- Beşiktaş maç sonucu backtest isabeti %52'den %55'e, büyük maç isabeti %33'ten %50'ye çıktı; lig geneli modelde güç sinyali kontrollü tutuldu ve genel doğruluk %50 seviyesinde korundu.
- Günlük pipeline yeniden çalıştırıldı: 18 komut, 18 başarılı, 0 hata.
- Beraberlik kalibrasyonu test edildi; ana olasılığa agresif uygulanınca doğruluk %48'e düştüğü için geri alındı.
- Beraberlik sinyali artık ana tahmini değiştirmeyen "risk katmanı" olarak rapor ve dashboard'da gösteriliyor.
- Tahmin hata analizi modülü eklendi: kaçan beraberlik, büyük maç hatası, fazla güvenli hata ve gol adayı kaçırma tiplerini ayrı raporluyor.
- Gol adayı motoru genişletildi: primary golcülerin yanına duran top/defans profili, penaltı profili, büyük maç golcüsü ve yedek etki adayı sinyali eklendi.
- Gol adayı backtesti güçlendi: Top 3 %54'ten %58'e çıktı, Top 8/Top 10 %85 seviyesine ulaştı.
- Dashboard gol adayı tablosu artık aday tipini ve ilk 10 adayı gösteriyor.
- Büyük maç/derbi risk profili güçlendirildi: büyük maçlar artık minimum MEDIUM riskle etiketleniyor, normal maç gibi yorumlanmıyor.
- Büyük maç denetim raporu eklendi: 6 derbi/büyük maç için tahmin, gerçek sonuç, beraberlik riski, kart sinyali ve ilk 8 gol adayı birlikte kontrol ediliyor.
- Büyük maç raporunda 6/6 maç MEDIUM/HIGH risk olarak işaretleniyor; mevcut sonuç doğruluğu 3/6 (%50), hata dağılımı 2 kaçan beraberlik ve 1 fazla Beşiktaş iyimserliği.
- Süper Lig istihbarat raporu eklendi: 306 maçtan 18 takım, 691 oyuncu ve 29 hakem için takım gücü, skor penceresi, kart disiplini, oyuncu yük etiketi, hakem tempo etiketi ve scout ihtiyacı çıkarılıyor.
- Ana ürün sayfası ve komuta merkezi yeni lig istihbarat paneline bağlandı.
- Takım scout blueprint raporu eklendi: lig zafiyetleri rol ihtiyacına çevrilip her takım için aday bağlantısı üretiliyor.
- Blueprint aday havuzu lig istihbaratındaki 691 oyuncudan türetilen savunma/denge/fizik proxy adaylarıyla genişletildi; takım-rol-aday bağlantısı 155'ten 335'e çıktı.
- Ana ürün sayfası ve komuta merkezi yeni takım blueprint paneline bağlandı.
- SQLite veri ambarı eklendi: `data/processed/metric11_warehouse.sqlite` içinde maç, kadro, gol, kart, takım profili, oyuncu profili, hakem profili, tahmin, gol adayı ve scout blueprint tabloları tutuluyor.
- Veri ambarı kalite raporu üretildi: 15 tablo, 17.427 satır, 4 hazır görünüm ve 6 kalite bulgusu.
- TFF profil dosyaları ambar oyuncu tablosuna bağlandı; yaş/sözleşme bilgisi olan oyuncu sayısı 83'e çıktı, eksik profil bulgusu 691'den 608'e indi.
- Hazır SQLite görünümleri eklendi: `v_team_power_ranking`, `v_referee_card_risk`, `v_player_load_leaders`, `v_besiktas_scout_blueprint`.
- SQLite sorgu rehberi eklendi: `docs/warehouse_query_cookbook.md`.
- Oyuncu profil zenginleştirme kuyruğu eklendi: 691 lig oyuncusu içinden eksik profiller, ilk 11/gol/kart/tahmini yük/profil etiketiyle önceliklendiriliyor.
- TFF profil collector'a `--player-ids-file` desteği eklendi.
- Öncelikli ilk 60 lig oyuncusu TFF'den başarıyla toplandı; `data/processed/tff_player_profiles_all_priority_2025_2026.json` oluştu.
- Ambar profil kapsamı güncellendi: yaş/sözleşme bilgisi olan oyuncu sayısı 83'ten 143'e çıktı, eksik profil bulgusu 608'den 548'e indi.
- İkinci profil toplama paketi tamamlandı: sıradaki 120 öncelikli lig oyuncusu TFF'den başarıyla toplandı.
- Öncelikli lig profil dosyası 180 oyuncuya çıktı; ambar içinde yaş/sözleşme bilgisi olan oyuncu sayısı 263'e yükseldi.
- Eksik profil bulgusu 548'den 428'e indi; 176 oyuncuda sözleşme bitişi 13 ay veya daha kısa.
- Üçüncü profil toplama paketi tamamlandı: 120 öncelikli oyuncudan 118'i başarıyla toplandı, 2 oyuncuda TFF zaman aşımı/bağlantı kesilmesi oldu.
- Öncelikli lig profil dosyası 298 oyuncuya çıktı; ambar içinde yaş/sözleşme bilgisi olan oyuncu sayısı 381'e yükseldi.
- Eksik profil bulgusu 428'den 310'a indi; 267 oyuncuda sözleşme bitişi 13 ay veya daha kısa.
- Dördüncü profil toplama paketi tamamlandı: sıradaki 120 öncelikli lig oyuncusu TFF'den başarıyla toplandı.
- Öncelikli lig profil dosyası 418 oyuncuya çıktı; ambar içinde yaş/sözleşme bilgisi olan oyuncu sayısı 501'e yükseldi.
- Eksik profil bulgusu 310'dan 190'a indi; 349 oyuncuda sözleşme bitişi 13 ay veya daha kısa.
- Beşinci profil toplama paketi tamamlandı: 120/120 öncelikli oyuncu başarıyla toplandı; öncelikli lig profil dosyası 538 oyuncuya çıktı.
- Altıncı profil toplama paketi tamamlandı: kalan 70/70 oyuncu başarıyla toplandı.
- SQLite ambarında 691/691 oyuncu yaş/profil zenginleştirmesine bağlandı; eksik profil kuyruğu 0'a indi.
- 441 oyuncuda sözleşme bitişi 13 ay veya daha kısa olarak işaretleniyor; bu veri scout fırsat/risk skorlarında kullanılabilir durumda.
- Takım scout blueprint adayları TFF profil verisiyle zenginleştirildi: 335 aday bağlantısının 318'inde yaş ve sözleşme alanı dolu.
- Blueprint düşük proxy güven bulgusu 334'ten 81'e indi; TFF profiliyle desteklenen türetilmiş rol adayları `MEDIUM_DERIVED_ROLE` olarak ayrılıyor.
- SQLite `team_scout_blueprints` tablosuna aday yaşı, sözleşme ayı, resale sinyali ve kontrat riski alanları eklendi.
- Scout rol kuralları sıkılaştırıldı: savunma baskın oyuncuların otomatik olarak 8 numara/fizik motoru listelerine taşınması engellendi.
- Scout kalite ve doğrulama raporu eklendi: 335 blueprint bağlantısı içinde 120 düşük güvenli bağlantı, tekil 10 oyuncu-rol kontrol kuyruğu ve 0 fazla role yayılan oyuncu raporlanıyor.
- Ana ürün sayfası ve komuta merkezi Scout Kalite Denetimi bağlantısını gösteriyor.
- Günlük pipeline yeniden çalıştırıldı: 29 komut, 29 başarılı, 0 hata.
- Blueprint profil okuması düzeltildi: Beşiktaş, scout kısa liste ve tüm öncelikli TFF profil dosyaları birlikte okunuyor; böylece ambar doluyken blueprint adayında yaş/sözleşme boş kalma hatası giderildi.
- `data/manual/player_role_overrides.json` eklendi; scout kalite kuyruğundaki 5 kritik skor rolü için pozisyon, boy, ayak, kaynak URL'i ve kaynak risk etiketi tutuluyor.
- Scout blueprint adaylarına doğrulanmış pozisyon/biyometri katmanı bağlandı; düşük güvenli blueprint bağlantısı 64'ten 0'a, tekil düşük güven oyuncu-rol kuyruğu 5'ten 0'a indi.
- SQLite `team_scout_blueprints` tablosuna doğrulanmış pozisyon, boy, tercih edilen ayak ve pozisyon kaynağı alanları eklendi.
- Veri analiz/istatistik öncelik planı eklendi: veri kalite scorecard, baseline model karşılaştırması, beraberlik risk modeli, gol adayı segment backtest, büyük maç modeli ve scout güven katmanı sıralandı.
- Otomatik veri kalite ve istatistik scorecard modülü eklendi: sezon kapsamı, hakem/profil eksikleri, maç tahmin doğruluğu, beraberlik yakalama, yüksek güvenli hata, gol adayı Top 5/Top 8 ve scout pozisyon güveni tek raporda ölçülüyor.
- İlk scorecard üretildi: genel skor 71.7/100; ana kırmızı alanlar beraberlik yakalama oranı 0/9 ve scout düşük pozisyon güveni 120/335; gol adayı Top 5 %73.1 ve Top 8 %84.6 izleme seviyesinde.
- Scout pozisyon güveni düzeltmelerinden sonra scout düşük pozisyon güveni 0/335 PASS durumuna indi; o aşamada scorecard Sofascore/protected akış sonrası maç sonucu doğruluğu 15/29 kaldığı için 75.6/100 seviyesindeydi.
- Günlük pipeline'a veri kalite scorecard üretimi eklendi.
- Ana ürün sayfası ve komuta merkezi Veri Kalite Scorecard bağlantısını gösteriyor.
- Network'süz günlük pipeline doğrulandı: 29 komut, 29 başarılı, 0 hata.
- Baseline model karşılaştırma modülü eklendi: always-home, puan/maç, son form, Elo-only, Poisson-only ve mevcut hybrid model aynı 258 lig maçı üzerinde karşılaştırılıyor.
- İlk baseline raporu üretildi: Poisson-only accuracy %51.2 ile en yüksek, mevcut hybrid %50.4; mevcut hybrid log loss 1.027 ile en iyi kalibrasyonu veriyor; güçlü modellerde draw recall %0 kaldığı için sıradaki model önceliği beraberlik risk katmanı olarak doğrulandı.
- Beraberlik risk denetim modülü eklendi: `draw_risk_score`, `draw_risk_level`, `protected_prediction` ve `recommended_model_action` alanlarıyla ana 1X2 tahminini değiştirmeden taraf tahminini korumaya alan risk katmanı üretiyor.
- İlk beraberlik risk raporu üretildi: MEDIUM/HIGH risk bayrağı 46/76 beraberliği yakaladı (%60.5 recall, %31.9 precision); ana modelin %0 draw recall'ına göre ürün dilinde önemli uyarı katmanı oldu, ancak kesin X tahmini olarak kullanılmamalı.
- Gol adayı segment backtest modülü eklendi: primary, impact-sub, set-piece defender, penalty profile ve unknown segmentlerini rank/top hit kırılımıyla ölçüyor.
- İlk segment raporu üretildi: primary maç hit rate %75.9, impact-sub %55.2; set-piece defender %4.0 ve penalty profile %0.0 kaldığı için bu iki segmentin Top 5 sıralama etkisi sınırlandırılmalı.
- Gol adayı modelinde segment backtest bulgusu uygulandı: set-piece defender ve doğrulanmamış penalty profile skor etkisi, doğrudan korner/hava topu/penaltıcı verisi gelene kadar düşürüldü.
- Güncellenmiş gol adayı backtesti iyileşti: Top 3 %58'den %62'ye, Top 5 %73'ten %77'ye, Top 10 %85'ten %88'e çıktı; Top 8 %85 seviyesini korudu.
- Veri kalite ve istatistik scorecard o aşamada 75.6/100 seviyesindeydi: scout güven açığı kapalı, ana kırmızı alan Beşiktaş 1X2 doğruluğu ve beraberlik yakalamaydı.
- Network'süz günlük pipeline yeniden doğrulandı: 32 komut, 32 başarılı, 0 hata.
- Beraberlik risk katmanı maç önü preview ve Beşiktaş dashboard'una bağlandı: `draw_risk`, `protected_prediction`, `recommended_model_action` ve Türkçe `action_label` alanları üretildi.
- Maç önü raporları ve dashboard artık "Korumalı taraf tahmini", "Beraberlik uyarılı tahmin" ve "Ana tahmini koru" etiketleriyle beraberlik senaryosunu kullanıcıya görünür gösteriyor.
- Korumalı tahmin aksiyonu denetimi pipeline'a eklendi: 29 Beşiktaş maçında 22 korumalı aksiyon, 7/22 gerçek beraberlik yakalama ve 11/22 taraf tahmini doğru kalma ölçülüyor.
- Korumalı aksiyon yanlış taraf vakaları etiketlendi: 3 Beşiktaş tarafını fazla değerleme, 1 rakibi fazla değerleme, 2 büyük maç taraf dönüşü, 4 HIGH draw risk ama net sonuç vakası.
- Yanlış taraf / side flip denetimi eklendi ve rakip piyasa değeri snapshot'ı bağlandı: güncel ekran tahmini sonrası 3 taraf dönüşü var; 2'si Beşiktaş'ı fazla değerleme, 1'i rakibi fazla değerleme. Rakip piyasa değeri 3/3 vakada kapsanıyor; kalan ortak boşluklar odds baseline, resmi sakatlık akışı ve doğrulanmış maç günü 11 kalitesi.
- Backtest dashboard'u genişletildi: lig geneli beraberlik risk aksiyonları, Beşiktaş korumalı aksiyon backtesti, yanlış taraf denetimi, gol adayı segment denetimi, segment Top 5 hit oranı ve zayıf gol adayı kuyruğu gösteriliyor.
- Komuta merkezi genişletildi: `draw_risk_audit`, `protected_action_audit` ve `side_flip_audit` çıktılarından beraberlik risk katmanı, kaçan beraberlikler, draw risk precision/recall, Beşiktaş korumalı aksiyon metrikleri, yanlış taraf market edge/veri boşlukları ve gol adayı segmentleri doğrudan ana ekranda görünüyor.
- Güncel veri kalite scorecard: 88.3/100. PASS alanları sezon kapsamı, hakem kapsamı, oyuncu profil kapsamı, ekran tahmini doğruluğu, yüksek güvenli hata ve scout pozisyon güveni; ana açık kalan beraberlikleri yakalamak ve odds/sakatlık/11 kalitesi verisini bağlamak.
- Gol adayı motoruna segment backtest kalite katsayısı bağlandı: geçmişte Top 5'e girip isabet üretmeyen oyuncular `quality_adjustment` ile otomatik puan cezası alıyor.
- Güncel gol adayı sonuçları: genel Top 3 %62, Top 5 %77, Top 8 %85, Top 10 %88; segment rank Top 5 hit %70; zayıf Top 5 aday kuyruğu 0'a indi.
- Beşiktaş maç sonucu için ham olasılık tahmininden ayrı `display_prediction` katmanı eklendi. Çok yüksek beraberlik riski ve dar olasılık farkında ekran tahmini beraberliğe çekiliyor.
- Beşiktaş ekran tahmini doğruluğu 15/29 (%52) ham olasılıktan 20/29 (%69) seviyesine çıktı; beraberlik yakalama 0/9'dan 3/9 (%33.3) seviyesine yükseldi.
- Veri kalite scorecard 75.6/100'den 88.3/100'e çıktı; maç sonucu metrikleri artık kullanıcıya gösterilen ekran tahminini ölçüyor.
- `data/manual/opponent_market_values_2025_2026.json` eklendi; side flip rakipleri için Transfermarkt kaynaklı piyasa değeri snapshot'ı tutuyor ve raporda market edge üretiyor.
- Komuta merkezi ve backtest panelindeki teknik terimler sadeleştirildi: `Brier` yerine "Olasılık hata puanı", `draw recall` yerine "Beraberlik yakalama", `precision` yerine "Uyarı isabeti", `xG` yerine ekranda "Gol beklentisi" kullanılıyor.
- Beşiktaş maç önü dashboard'u `Ekran tahmini` alanını gösteriyor ve model kontrolü ham en yüksek olasılık yerine kalibre edilmiş ekran tahminini denetliyor.
- Büyük maç ekran tahmini kalibrasyonu eklendi: rakip gol beklentisi belirgin üstünse beraberlik temkini yerine rakip tarafı korunuyor; güç sinyali rakibe dönük ve kart/oynaklık yüksekse Beşiktaş tarafı düşürülüyor.
- Beşiktaş ekran tahmini 20/29 (%69) seviyesine çıktı; ham tahmine göre +17 puan. Büyük maç doğruluğu 5/6 (%83), scorecard 88.3/100 oldu.
- Backtest paneline `Beşiktaş Ekran Tahmini Denetimi` eklendi; ham tahmin, ekran tahmini, gerçek sonuç ve kalibrasyon ayarı yan yana gösteriliyor.
- Komuta merkezindeki son maçlar tablosuna `Ekran Tahmini` kolonu eklendi.
- Son doğrulama: network'süz günlük pipeline 32 komut, 32 başarılı, 0 hata.
- Tüm 18 Süper Lig takımının Transfermarkt kadro verisi toplandı: 512 oyuncu, toplam €1.38 milyar piyasa değeri. `data/manual/transfermarkt_super_lig_clubs.json` 18 takım verified.
- `src/enrich_players_with_transfermarkt.py` eklendi: 608 TFF oyuncusunun %62'si (375 oyuncu) Transfermarkt ile eşleştirildi; `tm_market_value_eur`, `tm_contract_until`, `tm_position`, `tm_id` alanları eklendi.
- Scout blueprint builder enriched profil dosyasını okuyacak şekilde güncellendi; aday kartlarına `market_value_eur`, `tm_id` alanları bağlandı.
- Transfer tavsiye raporu aday kartlarında gerçek Transfermarkt piyasa değerini gösteriyor; market alarm tablosuna Piyasa Değeri sütunu eklendi.
- Tüm 18 takım için maç önü arşivi üretildi: `generate_preview_batch --all-teams` ile her takım için kronolojik preview arşivi üretiliyor.
- `build_all_teams_preview_dashboard.py` eklendi: tüm takımların tahmin doğruluğu, kart sinyali ve büyük maçlarını karşılaştıran birleşik dashboard.
- `build_transfer_recommendation_report.py` eklendi ve pipeline'a dahil edildi: 18 takım için öncelik sıralaması, aday önerisi, maliyet kademesi ve anlatılı gerekçe üretiyor.
- Lig zafiyet eşikleri gerçekçi değerlere çekildi; yeni zafiyet tipleri eklendi: "hücum verimsizliği", "kadro derinliği sınırlı".
- `SEASON = "2025_2026"` config sabiti eklendi; tüm çıktı dosyaları sezonu otomatik parametre alıyor.
- Günlük pipeline 18 takım --all-teams desteği ve 3 yeni adımla (enrich_transfermarkt, all_teams_preview, transfer_report) güncellendi.
- Haber istihbarat pipeline'ı eklendi: `collect_news_rss.py` (6 kaynak: Hürriyet, Milliyet, Sabah, Haberturk, AA, Takvim; 210+ makale/çalıştırma), `analyze_news_with_claude.py` (Claude Haiku ile yapılandırılmış varlık çıkarımı: transfer, sakat, cezalı, sözleşme), `build_news_intelligence_report.py` (transfer radar, sakat/cezalı tablo, haber akışı dashboard).
- Claude AI analizi için `.env` dosyasında `ANTHROPIC_API_KEY` gerekiyor. Key olmadan dashboard ham RSS verisiyle çalışıyor; key eklenince transfer/sakat/cezalı yapılandırılmış sinyaller aktif hale geliyor.
- Haber İstihbaratı paneli ana ürün sayfasına ve komuta merkezine bağlandı.
- Draw kalibrasyon eklendi: `draw_calibrated_prediction()` fonksiyonu lig geneli tahmin modeline (`model_league_predictions.py`) ve OOS validasyon modülüne (`build_oos_validation.py`) eklendi. Eşikler: draw_p ≥ 0.27 ve gap ≤ 0.12 (yönsel lider ile draw arasındaki fark). Sezon geneli: 17 beraberlik tahmini, %35 precision, recall %0→%7.9 (6/76). OOS ikinci yarı doğruluk değişmedi (%53.6). Genel doğruluk %51.2→%50.8 (-0.4 puan). Model artık sezonda 17 beraberlik tahmin ediyor (önceden 0).
- 13 yüksek kullanımlı eşleşmemiş oyuncu için `data/manual/tm_player_manual_aliases.json` eklendi (Balkovec, Abraham, Szalai, Opoku, Dragus, Rhaldney, Ogundu, En-Nesyri, Ndao, Rak-Sakyi, de Abreu, Fofana, Durán). TM kapsam %62→%74, lig snapshot %81.6.
- OOS validasyon modülü eklendi: `src/build_oos_validation.py` walk-forward kronolojik split, hafta 1-17 ısınma + hafta 18-34 bağımsız test. OOS ikinci yarı %53.6, HIGH güven %60.4.
- Maç günü kadro sinyali eklendi: `src/preview/squad.py` oyuncu önem skoru, `squad_xg_adjustment()` eksik oyuncu xG düzeltmesi. Motor, olasılık ve uygunluk modülleri güncellendi; Sofascore xG yerine oyuncu bazlı etki kullanılıyor.
- Draw kalibrasyonu güçlendirildi: `draw_calibrated_prediction()` fonksiyonuna `strength_edge` bazlı denge katsayısı eklendi (DRAW_BOOST_SCALE=0.12, DRAW_PRED_MIN_PROB=0.26, DRAW_PRED_MAX_GAP=0.14). Beraberlik recall %8'den %29'a çıktı, genel doğruluk %50.8→%51.6.
- Tüm 18 takım için maç önü dashboard üretimi parametre haline getirildi: `build_dashboard.py --all-teams` tek komutla 18 takım HTML üretiyor; TEAM_DISPLAY_NAMES dict'i ve takım bazlı başlıklar/etiketler eklendi.
- Vercel Analytics script'i tüm 33 HTML sayfasına eklendi (`/_vercel/insights/script.js`).
- GitHub Actions'a `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true` eklendi (Node 20 deprecation uyarısı giderildi).
- X (Twitter) Bearer Token eklendi: `collect_news_twitter.py` 30 hesap (18 kulüp + TFF + medya) takip ediyor; `X_BEARER_TOKEN` GitHub Secret olarak ayarlandı.
- Resmi kulüp haber scraper'ı eklendi: `src/collect_official_club_news.py` 18 resmi kulüp sitesini credential gerektirmeden tarıyor.
- Admin sayfası hash koruma güvencesi eklendi: `ADMIN_CREDENTIALS_HASH` env var yokken mevcut `admin.html` korunuyor, üzerine yazılmıyor.
- 2025/26 sezonu bitti — tüm maç önü dashboard'larına otomatik "sezon arası" banner eklendi; 2026/27 fikstürü açılınca banner JS tarih tespiti ile kaybolacak.
- 2026/27 Süper Lig kadrosu güncellendi: küme düşenler (Karagümrük, Antalyaspor, Kayserispor) çıkarıldı; yükselen takımlar (Çorum FK, Erzurumspor FK, Amed SFK) TM ID'leriyle sisteme eklendi. 4 dosya güncellendi: `generate_preview_batch.py`, `build_dashboard.py`, `transfermarkt_super_lig_clubs.json`, `build_transfer_season_context.py`.

## 2026-05-25 Site UI & İçerik İyileştirmeleri (Session 3)

### Ana Sayfa Yeniden Yapılandırma (build_live_feed.py)
- Transfer penceresi 3-durumlu banner eklendi: **Geri Sayım** (1 Haziran öncesi) → **Açık** (yeşil, kaç gün kaldı) → **Kapandı** (gri). `_window_state()` fonksiyonu ve `WINDOW_OPEN_DATE = 2026-06-01`, `WINDOW_CLOSE_DATE = 2026-09-01` sabitleri.
- Ana sayfa layout yeniden yapılandırıldı: Sol sütun = Transferler (üstte, birincil ürün) + Haber Sinyalleri (altta, 6 madde). Sağ sütun = "Analiz Platformu" (kategorilere ayrılmış bağlantılar). Ürün kimliği haber değil analiz/scout olarak öne çıkarıldı.
- "Son Haberler" → "Haber Sinyalleri" olarak yeniden adlandırıldı; "Analiz merkezi" butonu `football_intelligence_home.html`'e yönlendirildi.

### Navigasyon Standardizasyonu (tüm build dosyaları)
- 8 ana sayfanın tamamında 5-madde nav standardize edildi: Gündem · Transferler · Analizler · Scout · Maç Önü.
- Nav CSS standart değerleri: 58px topbar yüksekliği, `#091810` arka plan, `#8fa89a` pasif link rengi, `#162b20` aktif arka plan.
- Logo/marka href'leri `/gundem_2025_2026.html` → `/` olarak düzeltildi (tüm dosyalarda).
- Tarayıcı varsayılan `:visited` (mor) ve `:active` (kırmızı) override sorunu giderildi: `.brand` ve `nav a` için explicit `:visited`, `:active`, `:hover` kuralları eklendi.
- Beşiktaş-özel "Maç Odası" butonu `build_product_home.py`'dan kaldırıldı; `index.html` üretimi durduruldu; `data/processed/index.html` git'ten silindi.

### Haber Kalitesi İyileştirmeleri
- `collect_news_google.py`, `collect_news_telegram.py`, `analyze_news_with_claude.py` içinde `MAX_AGE_DAYS = 14` filtresi eklendi; 14 günden eski haberler toplanmıyor ve analize girmiyor.
- Haber kartlarına yaş etiketi eklendi: "2sa", "dün", "4g önce" formatında `_fmt_date()` fonksiyonu.
- `build_news_intelligence_report.py` nav: fazla "Haberler" 6. nav maddesi kaldırıldı; aktif item Gündem olarak ayarlandı.

### HTML Entity Düzeltmesi (9 build dosyası)
- `&#x131;`→`ı`, `&#x15f;`→`ş`, `&#xfc;`→`ü`, `&#xf6;`→`ö`, `&#xe7;`→`ç`, `&#x11f;`→`ğ` ve diğer tüm Türkçe/özel karakter entity'leri native UTF-8 ile değiştirildi.
- Etkilenen dosyalar: `build_all_teams_preview_dashboard.py`, `build_command_center.py`, `build_dashboard.py`, `build_live_feed.py`, `build_news_intelligence_report.py`, `build_product_home.py`, `build_transfer_recommendation_report.py`, `build_transfer_season_context.py`, `build_transfer_tracker.py`.
- Entity replacement sonrası oluşan kelime hatası düzeltildi: "aşık" → "açık", "aşılıyor" → "açılıyor" (`_window_state()` transfer banner metni).

## 2026-05-25 Haber Kalitesi İyileştirmeleri (Session 3 — devam)

### Telegram Kanal Genişletmesi ve Erişilebilirlik Testi (collect_news_telegram.py)
- Toplam kanal sayısı 6'dan 7'ye çıktı (11 denendi, 4 kaldırıldı).
- Test sonuçları: `superligson`, `futbolhaber`, `superligtransfer`, `basaksehirhaberleri` public preview kapalı/aktif değil — bu 4 kanal kaldırıldı (her çalışmada 12 sn boşuna bekleme önlendi).
- Aktif kanallar: `transferhaber` (20), `sporxhaber` (7), `transferturkiye` (5), `besiktashaberleri` (20), `fenerbahcehaberleri` (4), `galatasarayhaberleri` (5), `trabzonsporhaberleri` (2).
- Kanallar "Transfer/genel sinyal" ve "Kulüp bazlı" kategorileri altında yorumlandı.

### Kaynak Güvenilirlik Skoru (build_live_feed.py)
- `SOURCE_TRUST` sözlüğü eklendi: `official_club`=10, `rss`=7, `google_news`=6, `twitter`=5, `telegram`=4.
- `_article_html()` trust skoru ≥6 ise koyu renk (var(--ink)), <6 ise soluk renk (#627067) kullanıyor; düşük güvenli kaynaklar görsel olarak ayrışıyor.

### Yinelenen Haber Tespiti (build_live_feed.py)
- `_deduplicate_articles()` fonksiyonu eklendi: başlık kelime örtüşmesi ≥3 olan haberler gruplandırılıyor.
- Her grupta en yüksek trust skorlu kaynak öne çıkıyor; birden fazla kaynak varsa "N kaynak" etiketi gösteriliyor.
- `build_html()` artık ham 18 haber yerine deduplicate edilmiş 6 grubu gösteriyor.

### Analiz Platformu Link Durumu (build_live_feed.py)
- `_ana_link()` helper fonksiyonu: PROCESSED_DIR'de dosya var mı kontrol eder; yoksa pasif stil (cursor:not-allowed, muted renk) gösterir, varsa aktif yeşil link.
- Sağ panel linklerinin tamamı bu fonksiyondan geçiyor.

### Mobil CSS Genişletmesi (build_live_feed.py)
- `@media(max-width:600px)`: `pills` 2 sütunlu grid, `panel` ve `main` padding sıkıştırıldı. Küçük ekranlarda daha kompakt görünüm.

## 2026-05-25 Yaş Eğrisi Analizi (Session 3 — devam)

### Scout Raporu Yaş Eğrisi Tab'ı (build_transfer_recommendation_report.py)
- `build_age_curve_analysis()` fonksiyonu eklendi: tüm blueprint aday havuzundan yaş bracketi dağılımı (U21/U24/U27/U30/30+), bracket başına ortalama piyasa değeri ve sözleşme riski sayısı hesaplanıyor.
- **Değer düşüş riski**: 30+ yaş, piyasa değeri ≥€1M ve kısa sözleşmeli oyuncular listeleniyor — değer penceresi kapanmadan satış/uzatma kararı alınması için uyarı.
- **Genç değer fırsatı**: U23 + expiring sözleşmeli oyuncular — düşük bonusla edinme fırsatı.
- HTML raporu yeni "Yaş Eğrisi" tab'ı ile genişledi: 5 bracket kartı + değer düşüş risk tablosu + genç fırsat tablosu.
- `build_report()` artık `age_curve` alanını da JSON'a ekliyor.

## 2026-05-25 _fmt_date() Çok Format Desteği (Session 3 — devam)

### Tarih Parse Genişletmesi (build_live_feed.py)
- `_fmt_date()` fonksiyonu şu formatları destekliyor:
  - `21.5.2026` — TFF/Türk tarih formatı (mevcut)
  - `2026-05-24T14:30:00Z` — ISO 8601 + Z suffix
  - `2026-05-24T14:30:00+00:00` — ISO 8601 + offset
  - `2026-05-24` — Yalnızca tarih
  - `Sat, 24 May 2026 10:00:00 +0000` — RFC 2822 (Google News RSS formatı)
- Tüm formatlar test edildi; None girişi boş string döndürüyor.

### Dashboardlar

Statik HTML olarak iki demo üretildi:

- Beşiktaş maç önü zeka paneli
- Süper Lig scout paneli
- Tahmin/backtest kontrol paneli
- Beşiktaş takım ihtiyaç paneli
- Zenginleştirilmiş scout paneli
- Ana ürün giriş paneli

Bu dosyalar server gerektirmez; doğrudan tarayıcıda açılabilir.

## Önemli Dosyalar

### Kod

- `src/collectors/tff.py`  
  TFF maç detay parser'ı. Maç, hakem, ilk 11, yedek, kart ve gol olaylarını parse eder.

- `src/collectors/tff_fixture.py`  
  TFF fikstür haftalarını parse eder.

- `src/collect_besiktas_season.py`  
  Beşiktaş 2025-2026 sezon maçlarını toplar.

- `src/collect_tff_league_season.py`  
  Tüm Süper Lig 2025-2026 maç detaylarını toplar.

- `src/collect_tff_player_profiles.py`  
  TFF oyuncu profillerinden yaş, uyruk, lisans, kulüp ve sözleşme verisi toplar.

- `src/collect_transfermarkt_squad.py`  
  Transfermarkt kadro sayfasından pozisyon, pozisyon grubu, sözleşme ve piyasa değeri toplar.

- `src/analyze_besiktas_season.py`  
  Beşiktaş sezon oyuncu/hakem/büyük maç metriklerini üretir.

- `src/generate_match_preview.py`  
  Tek maç için maç önü raporu üretir. Kadro önerisi, gol adayı, transfer etki simülasyonu ve teknik direktör kadro denetimi de üretir.

- `src/generate_preview_batch.py`  
  Beşiktaş sezonu için toplu maç önü rapor arşivi üretir.

- `src/build_player_availability.py`  
  TFF kart olaylarından otomatik cezalı sinyali ve manuel sakat/cezalı override dosyasından oyuncu uygunluk raporu üretir.

- `src/import_player_attribute_dataset.py`  
  FM/FIFA tarzı oyuncu attribute CSV dosyalarını lisans/risk bilgisiyle normalize eder.

- `src/backtest_goal_candidates.py`  
  Gol adayı tahminlerini backtest eder.

- `src/backtest_match_predictions.py`  
  Maç sonucu tahminlerini backtest eder.

- `src/analyze_prediction_errors.py`  
  Maç sonucu ve gol adayı hatalarını sınıflandırır; model geliştirme önceliklerini üretir.

- `src/build_big_match_report.py`  
  Büyük maç/derbi raporlarını ayrı denetler; taraf tahmini, gerçek sonuç, risk seviyesi, beraberlik/kart sinyali ve gol adaylarını tek raporda toplar.

- `src/build_league_intelligence_report.py`  
  Tüm Süper Lig için takım, oyuncu ve hakem profili çıkarır; takım zafiyetlerini scout ihtiyacına dönüştürür ve HTML/MD/JSON rapor üretir.

- `src/build_team_scout_blueprints.py`  
  Takım zafiyetlerini rol ihtiyacına çevirir; FM/pozisyon scout havuzu ve lig istihbaratından türetilmiş proxy adaylarla her takım için oyuncu öneri blueprint'i üretir.

- `src/build_sqlite_warehouse.py`  
  İşlenmiş JSON raporlarını tek SQLite veri ambarına aktarır; kalite raporu ve hazır analiz görünümleri üretir.

- `src/build_data_quality_scorecard.py`  
  SQLite ambar ve backtest çıktılarından veri/istatistik sağlık skoru üretir; model, beraberlik, gol adayı ve scout güven açıklarını önceliklendirir.

- `src/build_player_profile_enrichment_queue.py`  
  Eksik TFF oyuncu profillerini önceliklendirir; sıradaki toplama paketleri için ID dosyası üretir.

- `src/analyze_league_scouting.py`  
  Tüm lig oyuncu/takım/scout/hakem metriklerini üretir.

- `src/analyze_team_needs.py`  
  Oyuncu profili, sözleşme ve maç performansını birleştirerek takım ihtiyaç raporu üretir.

- `src/analyze_enriched_scouting.py`  
  Lig scout kısa listesini TFF oyuncu profilleriyle birleştirip fırsat skoru, sözleşme riski ve resale sinyali üretir. Attribute import dosyası varsa FM/FIFA tarzı current/potential/rol-fit sinyalini de skora ekler.

- `src/model_league_predictions.py`  
  Tüm lig maçlarını tarih sırasıyla kullanarak Poisson/Elo tabanlı maç sonucu olasılığı ve backtest üretir. Puan/maç, gol farkı ve clean sheet/scoreless sinyallerini kontrollü kalibrasyon olarak kullanır.

- `src/build_model_baseline_comparison.py`  
  Mevcut lig tahmin modelini always-home, puan/maç, son form, Elo-only ve Poisson-only baseline'larıyla karşılaştırır.

- `src/build_draw_risk_audit.py`  
  Lig tahminlerinden beraberlik risk skoru ve korumalı tahmin aksiyonu üretir; risk bayrağının recall/precision değerini denetler.

- `src/build_goal_candidate_segment_backtest.py`  
  Gol adayı tiplerini segment bazında backtest eder; zayıf segmentleri ve Top 5 sıralama etkisi düşürülecek adayları raporlar.

- `src/build_protected_action_audit.py`  
  Beşiktaş maç önü raporlarındaki korumalı tahmin aksiyonlarını denetler; beraberlik uyarısı verilen maçlarda gerçek sonuç dağılımı, taraf tahmini doğruluğu ve HIGH/MEDIUM risk performansını ölçer.

- `src/build_side_flip_audit.py`  
  Beşiktaş taraf tahmini tersine dönen maçları inceler; xG edge, güç farkı, eksik oyuncu, risk seviyesi, sinyal etiketleri ve veri boşluklarını raporlar.

- `src/normalization.py`  
  Sponsor/isim değişikliği nedeniyle bölünen takım adlarını tek canonical takım adına indirger.

- `src/collectors/tff_player.py`  
  TFF oyuncu profil sayfasını parse eder.

- `src/build_dashboard.py`  
  Beşiktaş maç önü dashboard HTML dosyasını üretir. Kadro önerisi, teknik direktör kadro denetimi, skor senaryoları ve transfer etki simülasyonunu gösterir.

- `src/build_scout_dashboard.py`  
  Lig scout dashboard HTML dosyasını üretir.

- `src/build_backtest_dashboard.py`  
  Lig tahmin modeli, beraberlik risk aksiyonu, gol adayı motoru ve gol adayı segment denetimi için model performans dashboard'u üretir.

- `src/build_team_needs_dashboard.py`  
  Yaş, sözleşme, gol yükü, genç varlıklar ve sözleşme risklerini takım ihtiyaç paneline dönüştürür.

- `src/build_enriched_scout_dashboard.py`  
  Zenginleştirilmiş scout raporunu HTML dashboard'a dönüştürür.

- `src/build_product_home.py`  
  Tüm MVP panellerini tek ana ürün giriş sayfasında toplar.

- `src/build_data_catalog.py`  
  Toplanan veri kaynakları, kapsam, eksik alanlar ve ürün hazırlık durumunu raporlar.

- `src/build_public_source_summary.py`  
  İç veri kaynağı bilgisini bozmadan kullanıcı arayüzünde gösterilebilir genel kaynak kategori özetini üretir.

- `src/build_fm_style_scout_program.py`  
  Zenginleştirilmiş scout listesinden FM tarzı rol bazlı aday programı ve dashboard üretir.

- `src/build_command_center.py`  
  Tahmin performansı, Beşiktaş maç önü raporları, takım ihtiyaçları ve FM scout adaylarını tek statik HTML komuta merkezinde toplar.

- `src/collect_sofascore_stats.py`  
  Sofascore ücretsiz API'sinden Süper Lig 2025-2026 maç istatistiklerini toplar. xG, şut, şuta isabet, korner, faul, pas, top hakimiyeti, hava topu ve önlenen gol. `SOFASCORE_TO_TFF` dict ile Sofascore isimleri TFF canonical isimlere çevriliyor. `--skip-existing` ile incrementel güncelleme destekli.

- `src/enrich_tff_with_sofascore.py`  
  TFF maç verisi ile Sofascore istatistiklerini `tarih|ev_sahibi_takım` anahtarıyla birleştirir. Her maç kaydına `sofascore_stats` ve `sofascore_id` alanları ekler. Çıktı `tff_super_lig_enriched_2025_2026.json` pipeline'ın ana maç verisi dosyasıdır.

- `src/collect_external_snapshots.py`  
  API-Football Süper Lig snapshot verisini toplar.

- `src/analyze_api_football_snapshot.py`  
  API-Football geçmiş sezon snapshot verisini takım gücü ve oyuncu rol/attribute havuzuna dönüştürür.

### Veri ve Raporlar

- `data/processed/tff_besiktas_2025_2026_matches.json`  
  Beşiktaş sezon maç detayları.

- `data/processed/tff_trendyol_super_lig_2025_2026_matches.json`  
  Tüm Süper Lig sezon maç detayları. Ham TFF verisi; Sofascore zenginleştirmesi uygulanmamış.

- `data/processed/sofascore_match_stats_2025_2026.json`  
  Sofascore'dan toplanan 306 maç istatistiği. xG ve 11 ek stat kategorisi içeriyor.

- `data/processed/tff_super_lig_enriched_2025_2026.json`  
  **Pipeline'ın ana maç veri dosyası.** TFF maç detayları + Sofascore stats birleşimi. 306/306 maç eşleşti. Her maç kaydında `sofascore_stats` alanı var. Tüm analiz, model ve preview script'leri bu dosyayı okuyor.

- `data/processed/besiktas_2025_2026_deep_metrics.md`  
  Beşiktaş detaylı sezon metrikleri.

- `data/processed/previews_besiktas_2025_2026_chronological/index.md`  
  Kronolojik veriyle üretilmiş Beşiktaş maç önü rapor arşivi.

- `data/processed/besiktas_2025_2026_dashboard_chronological.html`  
  Beşiktaş maç önü demo paneli.

- `data/processed/league_scouting_2025_2026.md`  
  Süper Lig scout ve takım metrikleri.

- `data/processed/league_scouting_2025_2026_normalized.md`  
  Takım alias düzeltmesi uygulanmış Süper Lig scout ve takım metrikleri.

- `data/processed/league_scouting_2025_2026_dashboard.html`  
  Süper Lig scout demo paneli.

- `data/processed/league_scouting_2025_2026_normalized_dashboard.html`  
  Takım alias düzeltmesi uygulanmış Süper Lig scout demo paneli.

- `data/processed/match_prediction_backtest_2025_2026.md`  
  Maç sonucu tahmin backtest raporu.

- `data/processed/goal_candidate_backtest_2025_2026.md`  
  Gol adayı backtest raporu.

- `data/processed/league_prediction_model_2025_2026.md`  
  Lig geneli Poisson/Elo MVP model backtest raporu.

- `data/processed/model_baseline_comparison_2025_2026.md`  
  Lig tahmin modeli için baseline karşılaştırması ve beraberlik/model kalibrasyon bulguları.

- `data/processed/draw_risk_audit_2025_2026.md`  
  Beraberlik risk katmanı denetimi; kaçan beraberlikler ve korumalı tahmin aksiyonlarını listeler.

- `data/processed/protected_action_audit_2025_2026.md`  
  Beşiktaş özelinde korumalı tahmin aksiyonunun gerçek sonuç dağılımı, beraberlik yakalama ve taraf tahmini koruma performansını gösterir.

- `data/processed/side_flip_audit_2025_2026.md`  
  Yanlış taraf tahmini vakalarını, rakip piyasa değeri market edge'ini ve odds/resmi sakatlık/maç günü 11 kalitesi gibi kalan veri boşluklarını listeler.

- `data/processed/goal_candidate_segment_backtest_2025_2026.md`  
  Gol adayı segmentlerinin rank, maç hit rate ve zayıf aday kuyruklarını gösterir.

- `data/processed/prediction_backtest_dashboard_2025_2026.html`  
  Tahmin modeli, güven kırılımı, yanlış yüksek güvenli maçlar, beraberlik risk aksiyonları, gol adayı başarısı ve segment kalite paneli.

- `data/processed/tff_player_profiles_besiktas_2025_2026.json`  
  Beşiktaş oyuncularının TFF profil verileri.

- `data/processed/besiktas_team_needs_2025_2026.md`  
  Beşiktaş yaş/sözleşme/performans bazlı takım ihtiyaç raporu.

- `data/processed/besiktas_team_needs_2025_2026_dashboard.html`  
  Beşiktaş takım ihtiyaç paneli.

- `data/processed/tff_player_profiles_scout_shortlist_2025_2026.json`  
  Scout kısa listesindeki ilk 25 oyuncunun TFF profil verileri.

- `data/processed/league_scouting_enriched_2025_2026.md`  
  Yaş/sözleşme ile zenginleştirilmiş scout raporu.

- `data/processed/league_scouting_enriched_2025_2026_dashboard.html`  
  Zenginleştirilmiş scout paneli.

- `data/processed/football_intelligence_home.html`  
  Tüm MVP panellerine bağlanan ana ürün giriş sayfası.

- `data/processed/data_catalog_2025_2026.md`  
  Veri kapsamı, kaynaklar, mevcut alanlar, eksik alanlar ve ürün hazırlık raporu.

- `data/processed/data_quality_scorecard_2025_2026.md`  
  Veri/istatistik sağlık skoru; model, beraberlik, gol adayı ve scout güven açıklarını tek raporda izler.

- `data/processed/public_source_summary_2025_2026.md`  
  Kullanıcı arayüzünde gösterilebilir kaynak kategori özeti.

- `data/processed/fm_style_scout_program_2025_2026.md`  
  Rol bazlı scout programı: hemen skor katkısı, fizik motoru, genç/resale, sözleşme fırsatı ve düşük riskli düzenli oyuncu listeleri.

- `data/processed/fm_style_scout_program_2025_2026.html`  
  FM tarzı scout programı dashboard'u.

- `data/processed/football_command_center_2025_2026.html`  
  Ürünün tek ekrandan gezilebilir komuta merkezi.

- `data/processed/api_football_super_lig_snapshot_2024.md`  
  API-Football ücretsiz planda erişilebilen 2024 Süper Lig snapshot özeti.

- `data/processed/api_football_super_lig_snapshot_2025.md`  
  API-Football 2025 sezonu denemesi; ücretsiz plan kısıtını gösterir.

- `data/processed/api_football_super_lig_2024_analysis.html`  
  API-Football geçmiş sezon veri paneli: takım gücü, oyuncu rating/şut/pas/duel/kart metrikleri.

- `data/processed/transfermarkt_besiktas_squad_2025_2026.md`  
  Beşiktaş Transfermarkt pozisyon ve piyasa değeri raporu.

- `data/processed/player_availability_besiktas_2025_2026.md`  
  Beşiktaş maçları için otomatik cezalı ve manuel sakat/cezalı oyuncu uygunluk raporu.

- `data/manual/player_availability_overrides.example.json`  
  Resmi sakatlık/ceza veya güvenilir haber kaynaklarından elle doğrulanan eksikleri eklemek için örnek dosya.

- `data/manual/player_attribute_sources.json`  
  FM/FIFA tarzı attribute veri kaynaklarının lisans, risk ve kullanım politikasını tutar.

- `docs/player_attribute_data_strategy.md`  
  Football Manager hissi veren scout önerisi için attribute veri stratejisi ve hukuki güvenlik notları.

## Önemli Bulgular

### Maç Sonucu Tahmini

Mevcut MVP heuristik modeli zayıf.

- Rapor sayısı: 29
- Doğru tahmin: 13
- Doğruluk: %45
- Büyük maç doğruluğu: %0

Bu model gerçek ürün için yeterli değil. Büyük maçlarda özel model/katsayı gerekiyor.

Lig geneli Poisson/Elo MVP modeli heuristik Beşiktaş modelinden daha sağlıklı bir temel verdi ama hâlâ ürün standardı değil.

- Test edilen maç: 258
- Doğru tahmin: 130
- Doğruluk: %50
- Ortalama en yüksek olasılık: 0.499
- Brier skoru: 0.615
- Log loss: 1.027
- Yüksek güvenli maç doğruluğu: %59.2

Kritik not: Model skor/sonuç olasılığı üretmek için kullanılabilir; tek başına "kesin taraf" önermemeli. Ürün ekranında güven seviyesi, beraberlik riski, xG farkı ve neden-sonuç anlatısı birlikte gösterilmeli.

### Gol Adayı Tahmini

Gol adayı motoru daha umut verici.

- Beşiktaş'ın gol attığı maç: 26
- Top 3 içinde gerçek golcü yakalama: %54
- Top 5 içinde gerçek golcü yakalama: %73

Bu alan ürün içinde kullanılabilir ama daha iyi hale getirmek için oyuncu pozisyonu, süre ve penaltı kullanıcısı eklenmeli. Rakip savunma gol yeme profili eklendi ve Top 3 isabet %50'den %54'e çıktı.

### Scout

İlk scout kısa listesi sadece TFF maç performansı bazlıdır.

Kullanılan sinyaller:

- gol
- ilk 11 sayısı
- yedek kadro
- kart/disiplin riski
- uygunluk skoru
- bitiricilik sinyali

Henüz eksik:

- piyasa değeri
- pozisyon
- ayak
- boy
- sakatlık geçmişi
- transfer geçmişi
- maaş tahmini
- fiziksel yük

Beşiktaş özelinde yaş ve sözleşme bitişi artık TFF profil verisinden geliyor.

- Oyuncu profili: 46
- Ortalama yaş: 25.7
- Ortalama kalan sözleşme ayı: 16.5
- U23 oyuncu: 13
- 13 ay içinde sözleşmesi bitecek oyuncu: 25

İlk takım ihtiyaç raporu, sözleşme riski olan düzenli oyuncular için yenileme veya ikame planını HIGH öncelik olarak işaretledi.

Scout kısa listesinin ilk 25 oyuncusuna profil katmanı eklendi.

- Profilli oyuncu: 25
- U24 oyuncu: 3
- Sözleşme riski/fırsatı: 13
- Fırsat skoru en yüksek isimler: Eldor Shomurodov, Paul Onuachu, Anderson Talisca, Mohamed Bayo, Felipe Augusto
- Genç değer sinyali öne çıkanlar: Felipe Augusto, Juan Santos, Dorgeles Nene

Veri kataloğu mevcut kapsamı netleştirdi.

- Normalize takım sayısı: 18
- Maç kadrosunda benzersiz oyuncu: 691
- Ana hakem: 29
- Transfermarkt Beşiktaş oyuncu: 28
- Transfermarkt Beşiktaş toplam piyasa değeri: €176M
- Ürün hazırlık durumu: maç önü raporları MVP_READY, gol adayları PROMISING_MVP, maç sonucu tahmini NEEDS_MODEL_WORK

Oyuncu uygunluk katmanı eklendi.

- İncelenen Beşiktaş maçı: 34
- Eksik oyuncu sinyali olan maç: 11
- Otomatik ceza sinyali: 14
- Manuel sakat/cezalı giriş: 0
- Not: Kırmızı kart/ikinci sarı sonrası ceza MEDIUM güvenle, kart birikimi ise resmi disiplin listesiyle doğrulanmadığı için LOW güvenle işaretlenir.

FM/FIFA tarzı attribute hattı hazırlandı.

- Aday kaynak kaydı: 4
- Güvenli kullanım: lisansı açık Kaggle/GitHub dataset veya kullanım hakkı olan CSV export
- Riskli kullanım: Football Manager oyun dosyası dump'ı veya lisansı belirsiz database mirror
- Model etkisi: current ability, potential ability, growth room, fiziksel/mental/teknik skor ve rol-fit fırsat skoruna eklenebilir.
- Not: Henüz gerçek attribute CSV import edilmediyse bu sinyal boş kalır; pipeline hazırdır.

FM tarzı scout programı üretildi.

- Aday oyuncu: 25
- Rol listesi: 5
- Roller: hemen skor katkısı, fizik motoru, genç/resale değer, sözleşme fırsatı, düşük riskli düzenli oyuncu
- Fiziksel yük: gerçek tracking verisi değildir; ilk 11, kadro sürekliliği, kart/temas, gol profili ve uygunluk skorundan türetilmiş düşük güvenli tahmini aralıktır.

Dış API durumu:

- API-Football 2024: 7 endpoint başarılı; 342 fikstür, 19 takım, gol/asist/kart listeleri erişildi.
- API-Football 2025: endpointler çalışıyor ama ücretsiz plan sezon erişimini kısıtlıyor; response boş.
- API-Football 2024 normalize oyuncu attribute havuzu: gol, asist, rating, pozisyon, key pass, duel, tackle, interception, kart.
- Sonuç: 2025-2026 canlı ana omurga TFF verisi; API-Football şimdilik geçmiş sezon doğrulama/zenginleştirme katmanı.

Beşiktaş takım ihtiyaç analizinde TFF oyuncu profillerinden 27 oyuncu Transfermarkt kadrosuyla eşleşti.

- Eşleşen toplam değer: €166M
- Pozisyon aksiyon planı üretildi: kaleci MEDIUM; savunma, orta saha ve hücum HIGH öncelik.
- Orta saha hattında düzenli oyuncu sözleşme riski: Kristjan Asllani, Orkun Kökçü
- Hücum hattında düzenli oyuncu sözleşme riski: Cengiz Ünder, El Bilal Toure, Milot Rashica

## Bilinen Sorunlar

1. TFF haftaları kronolojik sırada değil.  
   Bu düzeltildi: maç önü raporları artık gerçek maç tarihine göre önceki maçları kullanıyor.

2. Takım isimlerinde sponsor/isim değişimi alias problemi var.  
   İlk düzeltme eklendi: `GENÇLERBİRLİĞİ` ve `NATURA DÜNYASI GENÇLERBİRLİĞİ`, ayrıca `FATİH KARAGÜMRÜK A.Ş.` ve `MISIRLI.COM.TR FATİH KARAGÜMRÜK` birleştiriliyor. Oyuncu aliasları hâlâ eksik.

3. Maç sonucu modeli düşük doğrulukta.  
   Heuristik model %45, lig geneli Poisson/Elo MVP %50 doğruluk verdi. Oyuncu uygunluk katmanı eklendi ama gerçek model için daha iyi muhtemel 11, resmi sakatlık, hakem tempo etkisi, formasyon ve takım tarzı gerekir.

4. Scout skoru şu an forvet/golcü ağırlıklı.  
   Pozisyon bilgisi gelmeden savunmacı, bek, orta saha için adil değil.

5. Dashboardlar statik HTML.  
   Ürünleşme için Next.js/FastAPI veya Streamlit panel gerekir.

6. Veri TFF odaklı.  
   Oyuncu değerleri ve profil bilgileri için Transfermarkt benzeri kaynaklar eklenmeli.

7. TFF profil sayfasında güvenilir pozisyon/mevki alanı bulunamadı.  
   Yaş ve sözleşme TFF'den geliyor; pozisyon için ayrı kaynak eşleştirmesi gerekiyor.

8. Sakatlık bilgisi resmi ve düzenli bir feed'den gelmiyor.  
   Şimdilik otomatik cezalı sinyali + manuel override kullanılıyor. Resmi kulüp/TFF duyuruları veya güvenilir haber kaynakları bağlanmalı.

9. Football Manager veritabanı doğrudan proprietary kabul edilmeli.  
   Lisansı doğrulanmamış dump/scrape ticari ürün verisine alınmamalı. Bunun yerine lisansı açık FM/FIFA tarzı attribute datasetleri veya kullanım hakkı olan exportlar kullanılmalı.

10. Kaynak gizlemek hukuki/etik riskleri çözmez.  
    İç sistemde gerçek kaynak, lisans durumu ve risk saklanır. Ürün arayüzünde izinli kaynak adı veya genel kategori gösterilir.

## Devam Planı

## 2026-05-24 Refactoring: generate_match_preview.py Bölündü

- `src/generate_match_preview.py` (1.727 satır) `src/preview/` paketi olarak 11 modüle bölündü.
- Mevcut tüm importlar (`build_preview`, `write_preview`, `build_markdown`, `parse_tff_datetime`, `simulate_transfer_candidate`) kırılmadan çalışıyor.
- Yeni dosya yapısı:
  - `src/preview/__init__.py` — public re-export
  - `src/preview/constants.py` — BIG_MATCH_OPPONENTS, SPECIALIST_SCORE_MULTIPLIERS, ACTION_LABELS (22 satır)
  - `src/preview/engine.py` — build_preview, write_preview orkestratörü (135 satır)
  - `src/preview/form.py` — parse_tff_datetime, summarize_team_form, summarize_team_strength, clamp_score (161 satır)
  - `src/preview/opponent.py` — summarize_opponent_vs_besiktas_history, summarize_opponent_defense (83 satır)
  - `src/preview/players.py` — summarize_players, load_availability, availability_for_match, summarize_referee (130 satır)
  - `src/preview/goal_candidates.py` — summarize_goal_candidates, build_goal_specialists, merge_goal_candidates (242 satır)
  - `src/preview/probability.py` — Poisson motoru, draw risk, big match profil, estimate_probabilities (410 satır)
  - `src/preview/lineup.py` — build_lineup_recommendation, build_coach_lineup_audit, lineup_score (143 satır)
  - `src/preview/transfer.py` — build_transfer_impact_simulations, simulate_transfer_candidate, transfer_xg_delta (132 satır)
  - `src/preview/narrative.py` — build_narrative (145 satır)
  - `src/preview/markdown.py` — build_markdown (146 satır)
  - `src/generate_match_preview.py` — CLI entry point wrapper (43 satır)
- Bilinen not: `build_goal_specialists` içinde `"BEŞİKTAŞ A.Ş."` hardcoded — mevcut davranış korundu, ileride `target_team` parametresine bağlanmalı.

## 2026-05-24 Sofascore xG Entegrasyonu ve Pipeline Bağlantısı

### Veri Toplama: Sofascore API

- `src/collect_sofascore_stats.py` eklendi: `api.sofascore.com` ücretsiz API'sinden Süper Lig 2025-2026 maç istatistikleri toplandı.
- Toplanan veri: xG, şut, şuta isabet, şut içi alan, büyük fırsat, top hakimiyeti, korner, faul, pas, doğru pas, hava topu, önlenen gol.
- 306/306 maç toplandı; tamamında xG verisi mevcut.
- Sofascore → TFF canonical isim mapping eklendi: `SOFASCORE_TO_TFF` dict (18 takım).
- Çıktı: `data/processed/sofascore_match_stats_2025_2026.json`

### Zenginleştirme: TFF + Sofascore Birleştirme

- `src/enrich_tff_with_sofascore.py` eklendi: TFF maç verisi ve Sofascore istatistiklerini `tarih|ev_sahibi_takım` anahtarıyla birleştiriyor.
- 306/306 maç eşleşti (%100 kapsam).
- Her maç kaydına `sofascore_stats` ve `sofascore_id` alanları eklendi.
- Çıktı: `data/processed/tff_super_lig_enriched_2025_2026.json`

### Model İyileştirmesi: xG Harmanlama

- `src/preview/form.py` güncellendi: `summarize_team_form` artık `sofascore_stats` alanından `xg_for`, `xg_against`, `shots_on_target` değerlerini form özetine ekliyor.
- Yeni form çıktı alanları: `xg_for_per_match`, `xg_against_per_match`, `sot_per_match`, `xg_data_matches`.
- `src/preview/probability.py` güncellendi: `_blend_xg_goals` yardımcı fonksiyonu eklendi.
  - Harman: %60 Sofascore xG + %40 tarihi gol ortalaması.
  - xG verisi yoksa saf tarihi gol ortalamasına geri döner.
- `estimate_probabilities` artık hem ev sahibi hem rakip için xG harmanlı lambda kullanıyor.
- Return dict'e `xg_data_available` alanı eklendi.

### Backtest İyileştirmesi

- Beşiktaş `taraf_eğilimi` isabeti: %55 → %67 (xG harmanlama sonrası).
- Lig geneli yüksek güvenli maç isabeti: %59.2 → %59.6.
- xG gerçekçi aralığa geriledi: ~2.35 (tarih bazlı) → ~1.71 (gerçekçi).

### Pipeline Bağlantısı

- `src/run_daily_pipeline.py` güncellendi:
  - `NETWORK_COMMANDS`'a `collect_sofascore_stats --skip-existing` eklendi (`collect_tff_league_season`'dan sonra).
  - `DEFAULT_COMMANDS`'ın başına `enrich_tff_with_sofascore` eklendi (tüm analiz adımlarından önce).
- Aşağıdaki script'lerin `--input` varsayılanı `tff_trendyol_super_lig_2025_2026_matches.json`'dan `tff_super_lig_enriched_2025_2026.json`'a geçirildi:
  - `generate_preview_batch.py`
  - `model_league_predictions.py`
  - `analyze_league_scouting.py`
  - `build_model_baseline_comparison.py`
  - `build_league_intelligence_report.py`
- Hardcoded path güncellemeleri:
  - `build_sqlite_warehouse.py`: `load_all()` içinde zenginleştirilmiş dosyayı okuyor.
  - `build_data_catalog.py`: `build_catalog()` içinde zenginleştirilmiş dosyayı okuyor.

## 2026-05-24 Hakem Etkisi Entegrasyonu (model_league_predictions.py)

- `LEAGUE_AVG_CARDS = 4.67`, `LEAGUE_AVG_GOALS = 2.65` sabitler eklendi (sezon analiz ortalaması).
- `_main_referee(match)`: `officials` listesinden `role == "Hakem"` olanı çıkarıyor.
- `_referee_stats(referee_history, name)`: Kronolojik hakem geçmişinden `cards_per_match` ve `goals_per_match` hesaplıyor (min 4 maç gerekli, veri sızıntısı yok).
- `_referee_goal_adjustment(ref_stats)`: Kart etkisi `(lig_ort - ref_kart) × 0.018` + gol etkisi `(ref_gol - lig_ort) × 0.04`. Maksimum ±0.10 düzeltme.
- `predict_match`: `ref_adj` ile `expected_home` ve `expected_away` hafifçe ayarlanıyor.
- `risk_flags`: `referee_cards_per_match > 5.5` ise `"yüksek kart hakemi"` bayrağı ekleniyor.
- Hakem profili çıktısı: `referee_adj`, `referee_cards_per_match`, `referee_goals_per_match` alanları eklendi.
- Pipeline çıktısında `main_referee` alanı eklendi.
- Pipeline doğrulandı: 32 komut, 32 başarılı, 0 hata.

Hakem kırılımı (lig sezonu analizi):
- YASİN KOL: 5.38 kart/maç, 2.24 gol/maç → fizik oyun, gol baskılama
- ÇAĞDAŞ ALTAY: 3.46 kart/maç, 3.54 gol/maç → açık oyun, gol ortamı
- KADİR SAĞLAM: 5.93 kart/maç — en yüksek kart profili
- Not: Hakem etkisi aggregate backtest'te görünmez (düzeltmeler küçük); asıl değeri "yüksek kart hakemi" risk bayrağının kart piyasası sinyali olarak kullanılması.

## 2026-05-24 Beraberlik Risk ve Model Kalibrasyon İyileştirmesi

### xG Blending: model_league_predictions.py

- `update_history` fonksiyonuna `xg_for` ve `xg_against` parametreleri eklendi; `sofascore_stats`'tan her maç için okunuyor.
- `predict_match`: en az 3 xG kayıtlı maç varsa `gf_eff = 0.6 * avg(xg_vals) + 0.4 * goals_avg` blending kullanılıyor.
- `home_xg_efficiency` / `away_xg_efficiency` çıktı alanları eklendi (ortalama xG / ortalama gol).
- `risk_flags`: favori takımın `xg_efficiency > 1.35` ise `"favori xG israfı"` bayrağı ekleniyor.

### Yeni Draw Sinyalleri (probability.py `draw_calibration_signal`)

- **Favori xG israfı** (`goal_edge >= 0.3` ve favori `xg_for > goals_for * 1.35`) → lift +0.04
- **Düşük şuta isabet ortamı** (iki takım sot_per_match toplamı < 7.5) → lift +0.025
- **Genel düşük xG bağlamı** (4 tarafın ortalama xG < 1.1) → lift +0.03

### build_draw_risk_audit.py: Yeni Sinyal

- `score_row`'a `"favori xG israfı"` flag sinyali eklendi → score +10.

### Ölçüm Sonuçları (önceki → sonraki)

| Metrik | Önceki | Sonraki |
|---|---|---|
| Genel tahmin doğruluğu | 50.4% | 51.2% |
| Brier skoru | 0.615 | 0.607 |
| Log loss | 1.027 | 1.015 |
| HIGH güven maç doğruluğu | 59.6% | 61.9% |
| Draw recall (MEDIUM+) | 60.5% | 68.4% |
| Draw precision (MEDIUM+) | 31.9% | 32.1% |
| Kaçan beraberlik | 30 | 24 |

- Pipeline doğrulandı: 32 komut, 32 başarılı, 0 hata.
- Kritik not: Kalan 24 "kaçan beraberlik" büyük delta'lı yapısal bozulmalar (GS-BJK, FB-GS gibi). Bunları yakalamak için kafa kafaya tarihsel beraberlik oranı veya bahis piyasası verisi gerekir; Sofascore sinyalleriyle ulaşılabilecek üst sınır bu.

## 2026-05-24 Transfer Tavsiye Raporu Modülü

### Yeni Dosya: src/build_transfer_recommendation_report.py

Transfer penceresi için 18 Süper Lig takımına pozisyon bazlı oyuncu öneri motoru. `team_scout_blueprints_2025_2026.json` üzerinde çalışır.

**Skor formülü:**
- `transfer_score = urgency(0.35) + performance(0.30) + age_score(0.15) + fit_norm(0.20)`
- urgency: CONTRACT_RISK tipine göre (EXPIRING_SOON=40, ONE_YEAR_WINDOW=25, TWO_YEAR_WINDOW=10, STABLE=3)
- performance: gol * 3.5 + maç_başlangıcı * 0.6, max 50
- age_score: U21=28, U23=24, U25=18, U27=12, U29=7, U31=3, 31+=0
- fit_norm: blueprint fit skoru / 5, max 40

**Market alarmları:**
- Serbest transfer fırsatı (7 oyuncu): Orkun Kökçü, Barış Alper Yılmaz, Laszlo Benes, Alexandru Maxim, Samet Akaydın, Heliton, Fidan Aliti
- Müzakere penceresi (1 yıl kalan, 5 oyuncu): Kozlowski, Nuno Lima, Opoku, Oosterwolde, Pedro Pereira

**Çıktılar:**
- `data/processed/transfer_recommendation_report_2025_2026.json`
- `data/processed/transfer_recommendation_report_2025_2026.md`
- `data/processed/transfer_recommendation_report_2025_2026.html` — takım filtreli HTML dashboard, tabbed market alerts

**Pipeline ve dashboard bağlantısı:**
- `run_daily_pipeline.py` DEFAULT_COMMANDS'a eklendi (build_command_center'dan önce)
- `build_product_home.py`'a "Transfer Tavsiye Raporu" kartı eklendi (162 öneri)
- `build_command_center.py` nav barına "Transfer Raporu" linki eklendi

**Doğrulama (ilk sürüm):** 18 takım, 54 pozisyon ihtiyacı, 162 öneri, 0 hata.

### 2026-05-24 Transfer Raporu İyileştirmeleri

Üç geliştirme tek geçişte uygulandı:

**1. Transfer Aciliyet Sıralaması (yeni HTML tab: "Lig Sıralaması")**
- Tüm 18 takım `priority_score`'a göre sıralandı, görsel tier rozetleriyle (ACİL / YÜKSEK / NORMAL / STABİL) ve progress bar ile
- Tier eşikleri: ACİL≥56, YÜKSEK≥35, NORMAL≥20, STABİL<20
- HTML varsayılan açılış tabı "Lig Sıralaması" oldu
- Örnek: Kayserispor (69.7 ACİL) → Galatasaray (12.8 STABİL)

**2. Takım bağlamını kullanan anlatı gerekçe (`_build_narrative`)**
- Cümle 1: takım sorunu bağlamı (GA, GF, zayıflık) + rol ihtiyacı
- Cümle 2: oyuncu performansı + sözleşme durumu + yaş profili
- Örnek: "Savunma kırılgan (GA 1.82) — Stoper / hava ve temas ihtiyacı net. Santos: 32 maç. Bu yaz serbest kalıyor (~1ay) — bonussuz transfer fırsatı."

**3. Bütçe/maliyet sinyali (`transfer_cost_tier`)**
- FREE: EXPIRING_SOON → bonussuz transfer
- LOW: ONE_YEAR_WINDOW + (resale=LOW veya yaş≥29)
- MEDIUM: ONE_YEAR_WINDOW orta profil / TWO_YEAR_WINDOW
- HIGH: STABLE + resale=HIGH
- Her aday kartında ikinci badge olarak gösteriliyor

Ayrıca aday kartına `cards`, `height_cm` (varsa), `preferred_foot` (varsa), `resale_signal` eklendi. Market tablosuna Resale sütunu eklendi.

Not: Pozisyon sinyalleri scout blueprint'ten türetilmiş; gerçek sahada pozisyon doğrulaması önerilir.

### 2026-05-24 Weakness + Rol Çeşitliliği Düzeltmesi

**Sorun:** `late_goals_against >= 5` eşiği tüm 18 takımı kapsıyordu → hepsi "son bölüm gol yeme riski" alıyordu → ROLE_MAP'te CM_ENGINE ilk rol olarak herkes için atanıyordu → ranking tablosunda 13/18 takım "8 numara / fizik motoru" gösteriyordu.

**`build_league_intelligence_report.py` değişiklikleri:**
- `late_goals_against >= 5` → `>= 13` (6 takım: Gaziantep 19, Rize 17, Samsunspor/Kasımpaşa/Eyüp 16, Antalya 15)
- `cards_for_per_match >= 2.8` → `>= 2.5` (Gaziantep, Kasımpaşa, Konyaspor, Göztepe artı)
- `failed_to_score >= 7` → `>= 10` (Eyüp, Kocaeli, Antalya, Gençler, Kayserispor, Karagümrük)
- YENİ: `goals_for_per_match < 1.0` → "hücum verimsizliği" (Kocaeli 0.76, Kayserispor 0.79)
- YENİ: `weaknesses boş AND ppm >= 1.5 AND GA <= 1.2` → "kadro derinliği sınırlı" (GS, FB, Trabzon, Başakşehir, Beşiktaş)

**`build_team_scout_blueprints.py` ROLE_MAP eklemeleri:**
- "hücum verimsizliği": ["ST_SCORER", "LW_CREATOR"]
- "kadro derinliği sınırlı": ["LW_CREATOR", "FB_TWO_WAY"]

**Sonuç:** Ranking tablosunda 6 farklı birincil rol:
- CB_DOMINANT: Antalya, Kayserispor, Karagümrük, Gaziantep, Rize (savunma kırılgan)
- CM_ENGINE: Kasımpaşa, Eyüp, Samsunspor, Alanyaspor (son bölüm gol yeme)
- ST_SCORER: Kocaeli, Gençler (hücum verimsizliği/skor üretim)
- DM_SECURITY: Konyaspor, Göztepe (kart baskısı)
- LW_CREATOR: GS, FB, Trabzon, Başakşehir, Beşiktaş (kadro derinliği sınırlı)

## 2026-05-24 Tüm Takımlara Maç Önü Arşivi + Season Config

### SEASON config sabiti (src/config.py)
- `SEASON = "2025_2026"` ve `SEASON_LABEL = "2025-2026"` eklendi.
- `generate_preview_batch.py` artık `from src.config import SEASON` kullanıyor; dosya yolları bu sabite göre türetiliyor.
- Gelecek sezon geçişi için tek değişiklik: `config.py`'da `SEASON = "2026_2027"`.

### Tüm takımlara maç önü batch (generate_preview_batch.py)
- `--all-teams` flag eklendi: 18 Süper Lig takımının tamamı için otomatik çalışır.
- Her takım için slug haritası: `_TEAM_SLUGS` dict (Türkçe karakter normalizasyon sorunu çözüldü).
- Çıktı dizini: `previews_{slug}_{SEASON}_chronological/` formatında, Beşiktaş için `previews_besiktas_2025_2026_chronological` (geriye dönük uyumluluk korundu).
- Availability dosyası sadece Beşiktaş için kullanılıyor, diğer takımlar için `None`.
- Tahmin doğruluğu hesabı düzeltildi: `final_prediction` artık hedef takımın ev/deplasman perspektifinden değerlendiriliyor (`target_win`/`opponent_win`/`draw`).

**Sonuç:** 18 takım × 29 rapor = **522 maç önü raporu** üretildi.

| Takım | Doğruluk |
|---|---|
| Beşiktaş, Galatasaray, Gaziantep | %69 |
| Kayserispor | %59 |
| Başakşehir | %62 |
| Samsunspor, Karagümrük | %55 |
| Fenerbahçe | %52 |
| Kocaeli, Konyaspor, Gençler, Antalya, Alanyaspor | %48 |
| Trabzon, Göztepe | %45 |
| Rize, Kasımpaşa, Eyüp | %38 |

### Yeni dashboard: build_all_teams_preview_dashboard.py
- Tüm 18 takımın index.json'larını okur.
- 3 tab: Takım Sıralaması (doğruluk sırası + progress bar), Doğruluk Karşılaştırması (yatay bar chart), Büyük Maçlar.
- Çıktı: `data/processed/all_teams_preview_dashboard_2025_2026.html`
- `build_product_home.py`'a "Tüm Takım Maç Önü Arşivi" kartı eklendi (522 rapor / 18 takım).

### Pipeline güncellemesi
- `run_daily_pipeline.py`: `generate_preview_batch` → `generate_preview_batch --all-teams`
- `build_all_teams_preview_dashboard` eklendi (generate_preview_batch'ten hemen sonra).
- Toplam komut sayısı: 33.

## 2026-05-22 Son Geliştirme Notu

- API-Football derin snapshot collector eklendi: `src/collect_api_football_deep_snapshot.py`.
- Collector rate-limit uyumlu hale getirildi: `--delay-seconds`, `--retry-seconds`, `--retries`.
- 2024 Süper Lig derin snapshot toplandı:
  - 25 başarılı endpoint
  - 19 takım
  - 19 takım kadrosu
  - 625 kadro oyuncusu
  - 1750 sakatlık/geçmiş uygunluk sinyali
  - ücretsiz plan sınırı nedeniyle 60 oyuncu istatistik satırı
- Derin snapshot normalize edildi: `src/analyze_api_football_deep_snapshot.py`.
- Yeni çıktı: `data/processed/api_football_super_lig_deep_2024_analysis.html`.
- Birleşik dış oyuncu havuzu 115 oyuncuya çıktı.
- Scout zenginleştirme artık varsayılan olarak derin API analiz dosyasını kullanıyor:
  - `data/processed/api_football_super_lig_deep_2024_analysis.json`
- Dış API oyuncu sinyali scout skoruna bağlandı:
  - rating
  - dakika
  - gol/asist
  - şut
  - kilit pas
  - duel kazanımı
  - tackle/interception
  - kart
  - geçmiş sakatlık sinyali
- 2025-2026 TFF scout kısa listesinde 5 oyuncu dış API havuzuyla eşleşti:
  - Victor Osimhen
  - Barış Alper Yılmaz
  - Yunus Akgün
  - Ali Sowe
  - Marius Moundilmadji
- FM tarzı scout programına dış API kalite skoru ve dış API açıklama cümlesi eklendi.
- Ana ürün sayfasına `Dış API Derin Veri Paneli` kartı eklendi.
- Komuta merkezine `Dış Derin Veri` bağlantısı eklendi.
- Veri kataloğu derin API kapsamını göstermeye başladı.
- Oyuncu alias katmanı eklendi: `data/manual/player_aliases.json`.
- Ortak canonical isim fonksiyonları `src/normalization.py` içine taşındı.
- TFF, Transfermarkt ve API-Football arası eşleşme kalite raporu eklendi: `src/build_alias_quality_report.py`.
- Yeni çıktı: `data/processed/player_alias_quality_2025_2026.md`.
- Yanlış pozitif eşleşmeleri azaltmak için dış API scout eşleştirme eşiği sıkılaştırıldı.
- Scout kısa liste TFF profil kapsamı 25 oyuncudan 40 oyuncuya çıkarıldı.
- Zengin scout ve FM scout artık 40 profilli adayla çalışıyor.

Önemli not: API-Football 2025 sezonu ücretsiz planda boş dönüyor. 2025-2026 ana canlı omurga TFF verisiyle yürür; API-Football 2024 geçmiş sezon doğrulama, oyuncu kalitesi, kadro, sakatlık ve scout zenginleştirme katmanı olarak kullanılır.

## 2026-05-22 Ek Geliştirme: Skor, Kadro ve Tahmin Kalibrasyonu

- Maç önü motoruna rakibin son 5 maç hücum/savunma formu bağlandı.
- Sonuç olasılıkları artık yalnızca yüzde değil, Poisson tabanlı en olası skor senaryolarını da üretiyor.
- Her maç raporuna `recommended_scoreline`, `top_scorelines`, `recommended_action` ve `lineup_recommendation` alanları eklendi.
- Kadro önerisi artık çekirdek ilk 11, hücum önceliği, kart riski ve eksik oyuncu dışlama bilgisi veriyor.
- Beşiktaş maç önü dashboard'una "En olası skor", "Model aksiyonu", "Kadro Tercih Önerisi" ve "Skor Senaryoları" bölümleri eklendi.
- Lig geneli Poisson/Elo tahmin modeline de en olası skor çıktısı eklendi.
- Beşiktaş maç sonucu backtest'i önceki kalibrasyona göre iyileşti:
  - sonuç tahmini: 15/29, %52
  - taraf eğilimi verilen maçlar: 6/11, %55
  - büyük maçlar: 2/6, %33
- Gol adayı modeli mevcut durumda Top 3 için %54, Top 5 için %73 isabet veriyor.
- Örnek: Beşiktaş-Trabzonspor raporunda model skoru 1-1 senaryosu, kadro planı ve gol adayı olarak Orkun Kökçü çıkıyor; gerçek maçta Orkun gol atan oyuncular arasında.

Güncellenen ana dosyalar:

- `src/generate_match_preview.py`
- `src/generate_preview_batch.py`
- `src/model_league_predictions.py`
- `src/backtest_match_predictions.py`
- `src/build_dashboard.py`
- `src/build_backtest_dashboard.py`
- `src/build_command_center.py`
- `src/build_data_catalog.py`
- `src/build_product_home.py`

## 2026-05-23 Geliştirme: Kaynak Radarı, Pozisyon Scout Matrisi ve Yayın Stratejisi

- metric11.com için veri kaynak izleme listesi eklendi: `data/manual/source_watchlist.json`.
- Kaynak radarı üretici script'i eklendi: `src/build_source_watchlist.py`.
- Yeni çıktı: `data/processed/source_watchlist_2025_2026.md` ve `data/processed/source_watchlist_2025_2026.html`.
- İzlenen kaynak sayısı 11:
  - TFF maç detayları
  - TFF oyuncu profilleri
  - Transfermarkt squad pages
  - beIN SPORTS / LigTV haber ve maç bağlamı
  - API-Football
  - football-data.org
  - Football-Data.co.uk
  - StatsBomb Open Data
  - openfootball datasets
  - entity ID crosswalk kaynakları
  - Süper Lig/forum/community sinyalleri
- Günlük izlenecek kaynak sayısı 7 olarak raporlanıyor.
- Pozisyon bazlı scout matrisi eklendi: `src/build_position_scout_matrix.py`.
- Yeni çıktı: `data/processed/position_scout_matrix_2025_2026.md` ve `data/processed/position_scout_matrix_2025_2026.html`.
- Pozisyon scout rolleri:
  - sol açık / çizgi kırıcı
  - santrfor / skor yükü
  - 8 numara / fizik motoru
  - 6 numara / savunma emniyeti
  - bek / çift yönlü koridor
  - stoper / hava ve temas
  - kaleci / istikrar
- Pozisyon matrisi 40 adaydan 7 rol için 24 rol-aday eşleşmesi üretiyor.
- Pozisyon verisi zayıf olduğu için savunma/orta saha/kaleci rollerinde düşük güvenli proxy adayları filtrelendi; boş kalan roller açık veri eksiği olarak görünür bırakıldı.
- Ana ürün sayfasına `Pozisyon Bazlı Scout Matrisi` ve `Veri Kaynak İzleme Listesi` kartları eklendi.
- Komuta merkezine `Pozisyon Scout` ve `Kaynak Radarı` bağlantıları eklendi.
- Veri kataloğu artık pozisyon scout rol sayısını, rol-aday eşleşmesini ve kaynak izleme kapsamını gösteriyor.
- Yayın/güncellik stratejisi dokümanı eklendi: `docs/deployment_strategy.md`.
- Teknik karar:
  - Statik HTML MVP ve demo için yeterli.
  - Güncellik HTML ile değil, günlük veri pipeline'ı ile sağlanır.
  - Vercel frontend için uygun; scraper/model job'ları GitHub Actions, Render cron, PythonAnywhere veya VPS tarafında çalışmalı.
- Doğruluk hedefi gerçekçi çerçeveye alındı:
  - kısa vadede maç sonucu için %80 iddiası gerçekçi değil
  - önce yön eğilimi %55-60, sonra %62-65 hedeflenmeli
  - gol adayı Top 5 %73'ten %80 bandına taşınabilir
  - skor tahmini tek skor yerine ilk 3 skor senaryosu olarak ölçülmeli

## 2026-05-23 Ek Geliştirme: Oyuncu Olsaydı Maç Sonucu Ne Olurdu Simülasyonu

- Kullanıcının 14. maddesi için transfer/oyuncu etki simülasyonu maç önü motoruna eklendi.
- Her maç preview JSON'una `transfer_impact_simulations` alanı eklendi.
- Simülasyon, pozisyon scout matrisindeki önerilen oyuncular için şu çıktıları üretiyor:
  - mevcut xG
  - oyuncu eklenseydi simüle xG
  - xG farkı
  - simüle Beşiktaş kazanma/beraberlik/rakip kazanma olasılığı
  - simüle en olası skor
  - etki etiketi: `MARGINAL`, `LOW_POSITIVE`, `MEDIUM_IMPACT`, `HIGH_IMPACT`
- Maç önü markdown raporlarına `Transfer Etki Simülasyonu` bölümü eklendi.
- Beşiktaş maç önü dashboard'una `Transfer Etki Simülasyonu` tablosu eklendi.
- Kullanıcı seçimi için komut satırı simülatörü eklendi: `src/simulate_player_match_impact.py`.
- Örnek komut:

```bash
python -m src.simulate_player_match_impact --preview data/processed/previews_besiktas_2025_2026_chronological/week_33_283844.json --player "Kacper Kozlowski"
```

- Örnek çıktı: Beşiktaş-Trabzonspor maçında Kacper Kozlowski sol açık rolünde simüle edildiğinde model xG'yi `1.57-1.25` bandından `1.84-1.23` bandına taşıyor; Beşiktaş kazanma olasılığı simülasyonda `%52` oluyor.
- Transfermarkt lig geneli genişleme için kontrollü collector eklendi: `src/collect_transfermarkt_league_squads.py`.
- Transfermarkt kulüp mapping örneği eklendi: `data/manual/transfermarkt_super_lig_clubs.example.json`.
- Not: Transfermarkt toplu collector doğrulanmamış kulüp slug/id mapping ile çalıştırılmamalı; `--only-verified` ile güvenli ve kademeli çalıştırılmalı.

## 2026-05-23 Ek Geliştirme: 14 Madde Takibi ve Güncel Haber/Sakat-Cezalı Bağlamı

- 14 madde için takip ve kanıt dosyası oluşturuldu: `docs/14_madde_takip.md`.
- Günlük pipeline runner eklendi: `src/run_daily_pipeline.py`.
- Haber/sakat-cezalı bağlam collector'ı eklendi: `src/collect_news_context.py`.
- beIN SPORTS sakat/cezalı sayfası gerçek ağ erişimiyle test edildi.
- Üretilen çıktı: `data/processed/news_context_snapshot_2025_2026.md`.
- Güncel sinyal örneği:
  - Beşiktaş sakat: Hyeon-gyu Oh, Kartal Yılmaz, Milot Rashica
  - Kaynak sinyali: beIN SPORTS sakat/cezalı sayfası
  - Güven: `MEDIUM_CONTEXT`
- FootballToday sakat/cezalı sayfası erişildi ancak ilk parser koşusunda anlamlı sinyal çıkarmadı; parser iyileştirilecek.
- Veri kataloğu artık haber/sakat-cezalı başarılı kaynak ve sinyal sayısını gösteriyor.
- Günlük pipeline GitHub Actions workflow'u eklendi: `.github/workflows/daily-pipeline.yml`.
- Workflow manuel `include_network=true` ile ağ collector'larını, zamanlı varsayılan akışta ise network'süz analiz/dashboard pipeline'ını çalıştırır.
- `docs/deployment_strategy.md` GitHub Actions + Vercel akışıyla güncellendi.
- Network'süz günlük pipeline test edildi: 18 komut, 18 başarılı, 0 hata.

### Kısa Vadeli

1. Oyuncu alias normalizasyonunu dış API, TFF ve Transfermarkt arasında genişletmeye devam et.
2. Scout profil toplama işini ilk 40'tan ilk 100 oyuncuya genişlet.
3. API-Football derin oyuncu sayfalarını ücretsiz plan izin verdiği ölçüde günlük parçalara bölerek büyüt.
4. Maç sonucu modelini iyileştirmeye devam et:
   - muhtemel 11 etkisini oyuncu rating/rol katsayısıyla sayısallaştır
   - cezalı/sakat oyuncu etkisini takım gücü katsayısına daha sert bağla
   - hakem kart/tempo etkisini gol ve kart piyasasına ayrı bağla
   - büyük maç katsayısını derbi backtest'ine göre kalibre et
   - beraberlik kalibrasyonunu düşük tempolu maçlarda güçlendir
5. Gol adayı modeline oyuncunun son maç gol/süre trendini, rakip savunma gol yeme profilini ve penaltıcı bilgisini ekle.

### Orta Vadeli

1. Oyuncu pozisyonlarını ve profil bilgilerini ekle.
2. Transfermarkt/kulüp/TFF oyuncu profili scraping araştırması yap.
3. Oyuncu scout modülünü pozisyon bazlı hale getir:
   - forvet
   - kanat
   - merkez orta saha
   - bek
   - stoper
   - kaleci
4. Takım ihtiyaç analizi ekle.
5. Tahmini fiziksel yük skoru üret:
   - ilk 11 sıklığı
   - pozisyon
   - maç temposu
   - kart/faul/oyun yoğunluğu
   - üst üste maç yükü
6. FM/FIFA tarzı attribute CSV dosyasını doğrulanmış lisansla import et ve scout modelinde gerçek eşleşme oranını ölç.

### Uzun Vadeli

1. Next.js tabanlı profesyonel dashboard.
2. FastAPI backend.
3. PostgreSQL veri katmanı.
4. API/scraper scheduler.
5. AI destekli hikayeli analiz üretimi.
6. Tüm takımlar için maç önü raporları.
7. Football Manager tarzı scout/transfer öneri ekranı. ✓ (build_transfer_recommendation_report.py — 2026-05-24)

## 2026-05-26 Codex - Canlı Transfer İddiası Tekilleştirme

- `src/analyze_news_with_claude.py` içinde güncel transfer iddiaları olay düzeyinde gruplanır: aynı oyuncu-hedef yönü farklı sinyal türleriyle tekrar sayılmaz; başlığı aynı RSS/Google yayın tekrarları tek iddiada kanıt olarak tutulur.
- Aynı yayıncının `Hürriyet Spor` / `Hürriyet` gibi kanal adları bağımsız teyit sayısını şişirmez; ayrı yayıncı teyidi olmadan söylenti `CORROBORATED` seviyesine yükselmez.
- `src/build_source_performance_report.py` aynı kanonik yayıncı kimliğini tarihçe ve skorlamada da kullanır; aynı olayın RSS/Google tekrarları erken-haber performans gözlemini çift saymaz.
- Açık yön taşıyan dış oyuncu başlığı (`Eldar Şomurodov Başakşehir'e transfer oldu`) oyuncu veritabanında yer almasa da yönlü `RUMOR` olarak çözümlenir. `Galatasaray'da ayrılık` benzeri anonim gidiş başlıkları geliş transferi gibi yazılmaz, `REVIEW_REQUIRED` olarak korunur.
- Hedef kulübü açıkça geçen dış oyuncu manşetleri (`Can Uzun` operasyonu, `Mohamed Salah` bombası, `Alexander Sörloth` bonservis haberi) veritabanında oyuncu kaydı bulunmasa da yönlü söylentiye çevrilir; yalnız açık isim-hedef ilişkisi olan başlıklarda uygulanır.
- `Bütçe ayrıldı` ifadesi artık oyuncu ayrılığı sinyali sayılmaz; aynı başlıktaki doğrulanabilir transfer ilgisi korunurken yanlış gidiş yönü engellenir.
- `Kulüp'te bir ayrılık daha`, `isimle yollar ayrılıyor` ve `transfer için ayrılacaklar` biçimindeki anonim ayrılık başlıkları, oyuncu tahmini yapılmadan kulüpten çıkış yönünde tutulur.
- Kadrodaki oyuncunun tekil soyadı başlıkta ve kendi kulübüyle birlikte geçiyorsa güvenli biçimde mevcut oyuncuya bağlanır: `Oulai` bonservis haberi anonim Trabzonspor gelişi yerine hedefi bilinmeyen Trabzonspor çıkış iddiası olur. Aynı oyuncu ve aynı çıkış kulübüne ait hedefi belirsiz kanıtlar tek olayda birleşir.
- Güncel snapshot sonucu: `33` ham transfer mention'ından `22` tekil canlı iddia; `1` çoklu kaynaklı iddia, `4` yönlü söylenti ve `17` inceleme kaydı. Önceki güncellik filtresinin bastırdığı `6` eski/tarihsiz mention tarihsel alanda kalmaya devam eder.
- Doğrulama: `.venv/bin/python -m unittest discover -s tests`, `.venv/bin/python -m compileall -q src tests` ve `git diff --check` başarılı (`61/61` test).

## 2026-05-26 Oyuncu-Haber Eşleştirme ve Formasyonel Uyum (Session 4)

### Oyuncu-Haber Eşleştirme (build_live_feed.py)
- `_build_player_index()`: transfer listesinden soyad bazlı arama sözlüğü üretir.
- `_detect_player()`: haber başlığında geçen ilk bilinen oyuncu adını tespit eder.
- Haber kartlarında eşleşen oyuncu sarı badge ile gösteriliyor (`👤 Oyuncu Adı`).

### Formasyonel Uyum Skoru (build_transfer_recommendation_report.py)
- `_FORMATION_FIT` matrisi: 9 rol (CB_DOMINANT, CM_ENGINE, DM_SECURITY, ST_SCORER, LW_CREATOR, FB_TWO_WAY, GK_STABILITY, LOW_RISK_REGULAR, RESALE_VALUE) → pozisyon anahtar kelimesi → uyum skoru (0-100).
- Hem Türkçe (TFF) hem İngilizce (Transfermarkt) pozisyon adları destekleniyor.
- `_formation_fit_score()`: rol × pozisyon → 0-100 skoru üretir (bilinmiyorsa 50 nötr, eşleşmezse 35 düşük uyum).
- `score_candidate()`: `formation_fit` hesaplanıyor ve transfer_score'a %10 ağırlıkla katılıyor.
- `result` dict'ine `"formation_fit"` alanı eklendi.
- `_formation_fit_inline()`: HTML kart içinde ⬡ sembolü + renk (yeşil≥80, turuncu≥50, kırmızı<50) olarak gösteriliyor.
- Test dağılımı: Centre-Back → CB_DOMINANT = 100, Defensive Midfield → DM_SECURITY = 100, Central Midfield → DM_SECURITY = 70.

## 2026-05-26 Codex Entegrasyonu ve Haber Güvenilirliği (Session 4)

### Codex Değişiklikleri Doğrulandı
- `src/config.py`: `TRANSFER_WATCH_SEASON = "2026_2027"` ve `TRANSFER_WATCH_SEASON_LABEL = "2026-2027"` sabitleri eklendi. Tamamlanan analiz sezonu (2025-2026) ile aktif transfer izleme sezonu ayrıştırıldı.
- `build_live_feed.py`, `build_transfer_tracker.py`, `build_news_intelligence_report.py`: Başlık ve meta etiketleri `TRANSFER_WATCH_SEASON_LABEL` kullanıyor — site "Süper Lig 2026-2027" olarak gösteriliyor.
- `src/detect_squad_changes.py`: Transfermarkt kadro snapshot karşılaştırması ile otomatik transfer dedektörü. Her çalışmada önceki snapshot ile fark alır.
- `src/build_transfermarkt_match_review_queue.py`: TFF-TM eşleşme kuyruğu üretici modülü eklendi.
- `run_daily_pipeline.py`: `detect_squad_changes` ve `collect_transfermarkt_league_squads --season-id 2026` pipeline'a eklendi.
- 8 yeni test eklendi (`tests/test_season_boundaries.py`, `tests/test_transfermarkt_match_review_queue.py`) — 8/8 PASS.
- Tüm kritik build modülleri test edildi: 7/7 hatasız çalışıyor.

### Haber Güncelleme Sorunu ve Çözümü
- **Sorun**: `news-refresh.yml` 02:15 UTC scheduled run bugün çalışmadı (GitHub Actions schedule atlama davranışı).
- **Anlık çözüm**: Haberler local çekildi (31 bugün makalesi), Vercel'e deploy edildi.
- **Kalıcı çözüm**: `refresh.yml`'e haber toplama fallback adımları eklendi — 6 saatlik refresh (00:15, 06:15, 12:15, 18:15 UTC) artık RSS + Google News + resmi kulüp haberlerini de çekiyor.

## Çalıştırma Komutları

Kurulum:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Beşiktaş sezon verisi:

```bash
python -m src.collect_besiktas_season
python -m src.analyze_besiktas_season
python -m src.build_player_availability
python -m src.generate_preview_batch
python -m src.backtest_goal_candidates
python -m src.backtest_match_predictions
python -m src.build_protected_action_audit
python -m src.build_side_flip_audit
python -m src.build_big_match_report
python -m src.build_dashboard
```

Sofascore istatistik toplama ve TFF zenginleştirme (ağ gerektirir):

```bash
python -m src.collect_sofascore_stats --skip-existing
python -m src.enrich_tff_with_sofascore
```

Tüm lig verisi ve scout:

```bash
python -m src.collect_tff_league_season
python -m src.collect_sofascore_stats --skip-existing
python -m src.enrich_tff_with_sofascore
python -m src.analyze_league_scouting
python -m src.build_scout_dashboard
```

Normalize scout ve lig geneli tahmin modeli:

```bash
python -m src.analyze_league_scouting --output-prefix league_scouting_2025_2026_normalized
python -m src.build_scout_dashboard --input data/processed/league_scouting_2025_2026_normalized.json --output data/processed/league_scouting_2025_2026_normalized_dashboard.html
python -m src.build_league_intelligence_report
python -m src.build_team_scout_blueprints
python -m src.build_player_profile_enrichment_queue
python -m src.model_league_predictions
python -m src.build_model_baseline_comparison
python -m src.build_draw_risk_audit
python -m src.build_protected_action_audit
python -m src.build_side_flip_audit
python -m src.build_sqlite_warehouse
python -m src.build_goal_candidate_segment_backtest
python -m src.build_data_quality_scorecard
python -m src.build_backtest_dashboard
```

Beşiktaş oyuncu profili ve takım ihtiyaç analizi:

```bash
python -m src.collect_tff_player_profiles --team "BEŞİKTAŞ A.Ş." --limit 0 --output data/processed/tff_player_profiles_besiktas_2025_2026.json
python -m src.collect_transfermarkt_squad
python -m src.analyze_team_needs
python -m src.build_team_needs_dashboard
```

Scout kısa liste profil zenginleştirme:

```bash
python -m src.collect_tff_player_profiles --scout-input data/processed/league_scouting_2025_2026_normalized.json --scout-limit 40 --limit 0 --output data/processed/tff_player_profiles_scout_shortlist_2025_2026.json
python -m src.collect_tff_player_profiles --player-ids-file data/processed/player_profile_enrichment_queue_2025_2026_ids.txt --limit 60 --sleep 0.25 --output data/processed/tff_player_profiles_all_priority_2025_2026.json
# Opsiyonel: lisansı doğrulanmış attribute CSV varsa önce import edilir.
# python -m src.import_player_attribute_dataset --input data/manual/player_attribute_imports/players.csv --source-name "Verified Player Attribute Dataset" --license-status "CC0_PUBLIC_DOMAIN" --risk-level LOW
python -m src.analyze_enriched_scouting
python -m src.build_enriched_scout_dashboard
python -m src.build_fm_style_scout_program
python -m src.build_alias_quality_report
python -m src.build_sqlite_warehouse
python -m src.build_data_quality_scorecard
python -m src.build_data_catalog
python -m src.build_public_source_summary
python -m src.build_transfer_recommendation_report
python -m src.build_command_center
python -m src.build_product_home
```

Transfer tavsiye raporu (tek başına):

```bash
python -m src.build_transfer_recommendation_report
```

API-Football derin snapshot ve analiz:

```bash
python -m src.collect_api_football_deep_snapshot --season 2024 --max-player-pages 8 --delay-seconds 7 --retry-seconds 15 --retries 2
python -m src.analyze_api_football_deep_snapshot
python -m src.analyze_enriched_scouting
python -m src.build_fm_style_scout_program
python -m src.build_data_catalog
python -m src.build_command_center
python -m src.build_product_home
```

## Devam Ederken İlk Yapılacak İş

Bir sonraki oturumda önce `PROJECT_STATE.md` okunmalı. Ardından öncelik:

1. Lig modelini çok sezonlu veya rolling time-split veriyle bağımsız doğrula; aynı sezon snapshot benchmark'ını eğitim özelliği gibi kullanma.
2. Odds/piyasa beklentisi baseline'ını 18 takım kapsamıyla topla ve model karşılaştırmasına ekle.
3. Resmi sakatlık/cezalı ve muhtemel 11 kaynaklarını tüm takımlar için düzenli collector haline getir.
4. TFF/Transfermarkt kuyruğunda kalan 193 profili zaman farkı/transfer/kadro dışı sınıflarına ayır; lig snapshot içinde güvenilir aday bulunmayan 128 kaydın önce 13 yüksek kullanımlı oyuncusunu doğrula ve profil veya transfer geçmişi kanıtı olmadan eşleşme üretme.
5. API-Football derin oyuncu istatistik sayfalarını parça parça büyüt.
6. Lisansı doğrulanmış FM/FIFA tarzı attribute CSV dosyası import et.
7. Kaçan beraberlikleri incele: düşük tempo, maç günü kadro kalitesi ve odds sinyalini ekle.
8. Tahmin modeline hakem kart/tempo etkisini daha güçlü bağla.
9. Pozisyon matrisi için doğrudan aksiyon verisi, tercih edilen ayak, boy ve sakatlık/transfer geçmişi kaynaklarını araştır.
10. Gol adayı kalite katsayısının sonraki pipeline koşularında Top 3/Top 5 etkisini izlemeye devam et; düşüş olursa katsayıyı gevşet.
11. Büyük maç ekran tahminini iyileştir: net sonuçlanan büyük maçlarda beraberlik override'ının fazla temkinli kaldığı vakaları ayrı katsayıyla denetle.

## 2026-05-25 Kalite Düzeltmesi ve Doğrulama Durumu

- Claude tarafından eklenen Transfermarkt lig snapshot, oyuncu enrichment, 18 takım maç önü arşivi ve transfer tavsiye ekranları okundu; mevcut pipeline ile uyumlu biçimde devam edildi.
- Lig-geneli preview motorunda bulunan iki kritik hata düzeltildi: gol specialist hesabındaki sabit Beşiktaş tarafı kaldırıldı; tahmin etiketleri artık hedef takım/rakip adını doğru yazar.
- Beşiktaş verisi üzerinde ayarlanmış `display_prediction` kuralları diğer 17 takıma uygulanmıyor. Diğer takımlar `raw_unvalidated_team` ile ham model başlangıç ölçümünü gösteriyor.
- `src/build_prediction_validation_report.py` eklendi ve günlük pipeline'a bağlandı. Rapor Beşiktaş ekran oranını bağımsız doğrulama olarak sunmaz.
- Güncel tahmin doğrulama sonuçları: Beşiktaş ham model 15/29 (%51.7); Beşiktaş aynı veri üzerinde ekran kontrolü 20/29 (%69.0); diğer 17 takım ham model 243/493 (%49.3); çift sayılmamış tekil lig fikstürü ham tabanı 134/263 (%51.0).
- Scout rol yayın filtresi sıkılaştırıldı. Transfer tavsiye raporu artık yalnızca dış profildeki pozisyonu istenen rolle eşleşen oyuncuları rol önerisi olarak yayımlar; doğrulanmamış adaylar araştırma kuyruğunda tutulur.
- Bu düzeltme ve tam-ad eşleşmeleri sonrası transfer raporu 18 takım için 141 doğrulanmış rol önerisi üretir; yayınlanan önerilerde doğrulanmamış pozisyon sayısı 0'dır.
- `src/build_tff_league_profile_pool.py` eklendi ve eksik 37 resmi TFF profili toplandı: maç kadrosunda görünen 691/691 oyuncu artık tek lig profil havuzunda işlenir; önceki 608 profilli paydanın Beşiktaş'ı dışarıda bıraktığı giderildi.
- `src/collect_transfermarkt_player_profiles.py` eklendi: 18/18 kulüpteki 512/512 Transfermarkt profil sayfası toplandı, başarısız sayfa 0, resmi ek tam-ad alanı bulunan profil 277.
- TFF / Transfermarkt oyuncu zenginleştirmesi kulüp sınırıyla güvenli hale getirildi; canonical alias, Latin karakter ve profil tam-ad katmanları kullanılıyor. Sonuç: 498/691 profil (%72.1), lig snapshot kapsamındaki 626 profilde %79.6 eşleşme.
- `src/build_transfermarkt_match_review_queue.py` artık tüm eşleşmeyen kayıtları ve 18 takım kapsama tablosunu gösterir: kalan 193 profilin 65'i snapshot dışı kulüp, 128'i mevcut snapshot içinde güvenilir aday bulunmayan kayıttır; bu 128 kaydın 13'u yüksek kullanımlı, 115'i rotasyon kullanımlı çözülmemiş oyuncudur.
- Transfermarkt tam-ad alanları `Juan Santos da Silva -> Juan`, `Carl Johan Holse Justesen -> Carlo Holse`, `Frederico Rodrigues de Paula Santos -> Fred` ve önceki kısa-ad eşleşmelerini lig-geneli kural üzerinden doğrular; scout yayınına engel eşleşme 0'dır.
- Side flip denetimi kısmi manuel rakip snapshot'ı yerine 18 kulübü kapsayan Transfermarkt lig dosyasını okuyor; incelenen 3/3 yanlış taraf vakasında piyasa değeri mevcut.
- `src/build_league_market_value_audit.py` eklendi: 18/18 kulüp, 512 oyuncu ve 258/258 model maçında retrospektif değer benchmark'ı üretildi. Sabit `draw_band=0.20` baseline doğruluğu %51, lig modeli doğruluğu %51; snapshot üretim tahminine doğrudan eklenmeyecek.
- Veri kataloğu, backtest paneli, komuta merkezi ve ürün ana sayfası lig-geneli değer kapsamını gösteriyor. Tüm takım önizleme kapsamı 18 takım / 522 rapor olarak doğrulandı.
- Veri kalite scorecard'ı eşleşme kapsamasını ve scout bloke eden ad eşleşmelerini kalite kapısı olarak ölçüyor; bu nedenle açıklar metriklerden saklanmıyor.
- Zengin scout ve pozisyon matrisi lig-geneli enriched profil dosyasına bağlandı; Transfermarkt pozisyon allowlist'i matris ve blueprint seviyesinde uygulanır. Örneğin `Juan Santos da Silva` santrfor olarak doğrulandığı için sol açık önerisinden çıkarıldı.
- Önceki ilk-40 scout giriş sınırı kaldırıldı: zengin scout ve FM aday motoru maç kadrosundaki 691/691 oyuncuyu puanlar; pozisyon matrisi bu havuzdan yalnız doğrulanmış pozisyonlu 84 rol-aday kaydını yayınlar.
- Tam-ad ve pozisyon akışı sonrası blueprint içinde 275 bağlantıda düşük güvenli aday 0, tekil düşük güven oyuncu-rol kuyruğu 0 ve scout blokajı 0'dır.
- Güncel scorecard 84.1/100'dür; `%69` Beşiktaş ekran kontrolü bağımsız test olmadığı için `WATCH`, lig-içi eşleşme `%79.6` olduğu için `WATCH`; scout düşük pozisyon güveni ise `PASS` gösterilir.
- Ağsız günlük pipeline, diğer güncellemelerle birlikte güncel bağımlılık sırasıyla 41/41 adımı hatasız çalıştırır; alias kalite raporu ve haber istihbarat çıktısı panellerden önce yeniden üretilir.
- Kaynak radarı güncellendi: Transfermarkt durumu `connected_super_lig_snapshot_2025_2026`, kullanım şartı/lisans kontrol gerekliliği korunuyor.
### Öncelikli Sonraki İş

1. ✅ 13 yüksek kullanımlı eşleşmeyen oyuncuya manual alias ile pozisyon+piyasa değeri atandı.
2. ✅ Walk-forward OOS validasyonu eklendi; ikinci yarı %53.6, HIGH güven %61.9.
3. ✅ Maç günü kadro sinyali model girdisi yapıldı.

### Canlı Çıkış Öncesi Kalan

1. Kalan 115 rotasyon-kullanımlı eşleşmeyenin tamamlanması (öncelik düşük, scout blocking 0).
2. ✅ Beraberlik tahmin sorunu giderildi: DRAW_PRED_MAX_GAP 0.14→0.18, OOS draw recall %7.9→%40.8 (31/76). build_oos_validation.py strength_edge eksikliği düzeltildi.
3. Manual alias network verify: 13 alias `requires_network_verify=true`; değerler knowledge-based, TM'den doğrulanmalı.

## 2026-05-25 Responsive Arayüz Yenilemesi

- Kullanıcı önceliği doğrultusunda veri/model katmanına dokunulmadan ana ürün yüzleri yeniden düzenlendi: `src/build_product_home.py`, `src/build_command_center.py`, `src/build_dashboard.py`, `src/build_all_teams_preview_dashboard.py` ve `src/build_transfer_recommendation_report.py`.
- Ürün girişi artık modül yığını yerine maç günü akışını öne çıkaran bir merkez ekranıdır. Ortak `metric11` navigasyonu ile `Merkez`, `Analiz`, `Maç Önü`, `Scout` ve `Lig` yüzleri arasında doğrudan geçiş sağlanır.
- Beşiktaş maç odası mobilde maç seçimi ve ana olasılıkları ilk görünümde tutacak şekilde düzenlendi; dört özet metrik dar ekranda `2x2` yerleşir. Kart sinyali, güven, rakip savunma ve gol aday tipi gibi görünen etiketler teknik enum yerine anlaşılır Türkçe ifadeler kullanır.
- Analiz merkezi metrik yoğunluğunu düşürerek temel sağlık göstergelerini görünür, ikincil kontrolleri açılır bölüm içinde tutar. Lig ve scout ekranlarında büyük tablolar panel içinde yatay kaydırılır; sayfa gövdesi mobilde taşmaz.
- Yeni HTML çıktıları üretildi: `data/processed/football_intelligence_home.html`, `football_command_center_2025_2026.html`, `besiktas_2025_2026_dashboard_chronological.html`, `all_teams_preview_dashboard_2025_2026.html`, `transfer_recommendation_report_2025_2026.html`.
- Bu arayüz aşamasındaki doğrulama kaydı: `python -m compileall -q src` başarılı; o aşamadaki ağsız günlük pipeline `39/39` başarılıydı. Güncel pipeline sonucu yukarıdaki kalite bölümünde `41/41` olarak kayıtlıdır. Tarayıcı kontrolünde beş ana sayfa `599px` dar görünümde yatay sayfa taşması üretmedi; maç seçimi değiştirildiğinde ilgili maç verileri ve Türkçe sinyaller güncellendi.

## 2026-05-25 Haber Pipeline ve Transfer Sezonu Bağlam Raporu

- RSS haber toplayıcısı (`src/collect_news_rss.py`) güncel kodda `15` Türk spor kaynağı yapılandırır.
- Twitter/X toplayıcısı genişletildi (`src/collect_news_twitter.py`): `45` hesabı izler; bunların `18` adedi aktif 2026/27 lig kulübünün resmi hesabı, Karagümrük dahil `19` resmi kulüp hesabı transfer-geçiş izleme kapsamındadır. `X_BEARER_TOKEN` varsa resmi X API v2 kullanıcı timeline'ını, yoksa durum snapshot'ını üretir.
- Anahtar gerektirmeyen resmi kulüp duyuru collector'ı eklendi (`src/collect_official_club_news.py`): aktif 2026/27 lig kapsamındaki `18` resmi web kaynağına ek olarak düşen üç kulübü transfer-geçiş izlemesinde korur (`21` yapılandırılmış kaynak). X artık resmi teyidin zorunlu bağımlılığı değildir.
- Resmi web collector canlı doğrulaması: toplam `19/21`, aktif lig kapsamı `16/18` site erişimi ve gürültü filtresi sonrası `18` tekil duyuru. Galatasaray TLS sertifika doğrulaması ve Eyüpspor DNS çözümleme hatası açık hata kaydı olarak tutulur.
- X collector erişim başarısız olsa bile durum snapshot'ı üretir. Güncel yerel çıktı `x_api/MISSING_CREDENTIALS`: `0/45` başarılı hesap ve `0` gönderi; underground/sosyal haber katmanı henüz analiz için canlı veri üretmiyor.
- Transfer haberleri kaynak teyit kapısından geçer: Google News ve Telegram ikincil sinyalleri dahil `430` ilgili içerik analiz edildi; `47` transfer sinyalinin `3` adedi resmi, `3` adedi tek kaynaklı söylenti, `41` adedi inceleme gerektirir. Yalnız yönü belirlenen resmi `Ernest Muçi`, `Dan Agyei` ve `Laszlo Benes` duyuruları model kullanımına açılır.
- Haber analiz motoru yeniden yazıldı (`src/analyze_news_with_claude.py`): API anahtarı gerektirmeyen kural-tabanlı Türkçe NER sistemi; transfer/sakat/cezalı/yükseliş/sözleşme regex kalıpları, 691 oyuncu veritabanıyla eşleşme. Claude Haiku isteğe bağlı iyileştirici olarak eklendi.
- Haber istihbarat raporu (`src/build_news_intelligence_report.py`) 4 sekmeye genişletildi: Haber Akışı, Transfer Radar, Sakat/Cezalı, Lig Değişiklikleri. Çorumspor ve diğer yükselen takımlar için yükseliş sinyali tespiti eklendi.
- Transfer Sezonu Bağlam Raporu eklendi (`src/build_transfer_season_context.py`): 261 sözleşmesi biten oyuncu (€429M toplam değer, Barış Alper Yılmaz €30M önde), 180 son yıl adayı, yükselen takım analizi, transfer penceresi takvimi. Günlük pipeline'a eklendi.
- Komuta merkezi ve ürün ana sayfası yeni raporu bağladı.

## 2026-05-25 Maç Günü Kadro Sinyali Model Girdisi

- `src/preview/squad.py` eklendi: tarihsel ilk 11 verisinden oyuncu önem skoru hesaplar.
  - `build_player_importance(matches, team, n_window=30, gk_ids)` → key/rotation/fringe sınıflandırması
  - Kaleciler (TM pozisyon datası + shirt_number=1) saldırı cezasından muaf
  - ≥2 eksik maç + pozitif lift → veri-tabanlı ceza (max 0.12); aksi halde key oyuncuya flat 0.05
  - `squad_xg_adjustment(importance, unavailable_ids)` → (total_penalty, breakdown)
- `src/preview/players.py` güncellendi: `availability_for_match()` artık `player_importance` alıyor; unavailable oyuncuların `impact` alanı UNKNOWN yerine REGULAR/ROTATION/FRINGE olarak doluyor.
- `src/preview/engine.py` güncellendi: player_importance tüm sezon verisinden hesaplanıyor; squad_xg_adjustment availability_signal'a ekleniyor; TM pozisyon datasından GK idi'leri yükleniyor.
- `src/preview/probability.py` güncellendi: kaba `missing_count * 0.05` yerine squad_xg_adjustment kullanılıyor (yoksa eski fallback devreye giriyor).
- `src/build_player_availability.py` güncellendi: news_intelligence_2025_2026.json'dan sakat/cezalı sinyaller de çekiliyor; iki kaynak name+status üzerinden dedup ediliyor.
- Test sonucu: Orkun Kökçü cezalı → impact=REGULAR, squad adj=-0.12, beklenen gol 1.71→1.26.

## 2026-05-25 Haber Ağı Genişletmesi ve Gündem Fan Sayfası

### Sezon Sonu ve 2026/27 Kadro

- Sezon arası banner: `build_dashboard.py` ve `build_all_teams_preview_dashboard.py` tüm maçlar geçmişte kaldığında otomatik blue banner gösteriyor; 2026/27 fikstür yüklenince kaybolacak.
- Küme düşenler: Karagümrük, Antalyaspor, Kayserispor.
- Yükselen takımlar: Çorum FK (TM: corum-fk/37951), Erzurumspor FK (TM: erzurumspor-fk/39722), Amed SFK (TM: amed-sk/12382). Alanyaspor elde kaldı.
- 4 dosyada (generate_preview_batch, build_dashboard, build_transfer_season_context, transfermarkt_super_lig_clubs.json) güncellendi. Sezon_id "2026"'ya çevrildi.

### Haber Ağı

- RSS kaynakları 8 → 15: NTV Spor, Sporx, Fanatik, Fotomaç, CNN Türk Spor, TRT Spor, Goal.com TR eklendi.
- Twitter hesapları 30 → 45: transfer_news (ertansuzgun, yusufgunaydn, EkremKonur, FabrizioRomano), analytics (TaktikSehri, kutubolgesi, PassHatasiii, OptaJoe), official (CorumFK1925, ErzurumsporFK, Amedspor), secondary_signal (GizemKaya__, GercekBJK, AmputeFutbol, WebdikBesiktas, KaraKartalBlog), media (HaberKartali).
- Google News RSS, aktif 2026/27 lig listesindeki `18` takımın tamamı ve `3` genel konu sorgusu ile çalışır; canlı doğrulamada `21/21` sorgudan `306` tekil haber üretildi.
- Public Telegram collector `6/6` kanaldan `48` mesaj üretti; kanal adında kulüp geçse dahi tüm Telegram girdileri doğrulanana kadar yalnız `SECONDARY` sinyal sayılır.
- Türkçe ve İngilizce anahtar kelimeler genişletildi (teknik direktör, resmileşti, here we go, signs, deal vb.).
- GitHub Actions `news-refresh.yml` eklendi: 02:15, 08:15, 14:15, 20:15 UTC haber yenileme; günlük full pipeline ayrıca 04:00 UTC'de ağ kaynaklarını yeniler.
- `detect_squad_changes.py` eklendi: günlük Transfermarkt kadro snapshot'ı alır, değişiklikleri (gelen/giden) karşılaştırır; çıktı `tm_squad_changes_2025_2026.json`.
- `build_transfer_tracker.py` eklendi: news_intelligence + TM kadro değişikliklerini birleştirerek transfer_tracker HTML ve JSON üretir.

### 2026-05-25 Kapsam ve Pipeline Düzeltmeleri

- `build_transfer_season_context.py` içindeki HTML kapanış string sözdizimi hatası giderildi; ağsız günlük üretim zinciri `47/47` başarılı doğrulandı.
- X kapsam metriği yalnız aktif ligdeki resmi kulüp hesaplarını sayacak şekilde ayrıştırıldı; ikincil kulüp hesapları resmi kapsamı şişirmiyor. Toplam resmi kulüp izleme sayısı ayrı metrikte korunuyor.
- Resmi web kaynak yapılandırmasına Çorum FK, Erzurumspor FK ve Amed SFK eklendi. Karagümrük, Antalyaspor ve Kayserispor geçmiş resmi transfer teyitlerini kaybetmemek için `current_league: false` geçiş kaynağı olarak tutuldu.
- `news-refresh.yml` analiz hatasını `|| true` ile gizlemeyi bıraktı; istihbarat analizi başarısızsa yayımlama zinciri de başarısız sayılacak.
- Sosyal sinyaller için teyit kapısı sıkılaştırıldı: iki puanlanmamış Telegram/X kaynağı resmi veya çoklu medya teyidi üretemez; sponsorlu/kısa kulüp adları aynı hedef olarak ele alınarak kendi-kendine transfer kayıtları inceleme durumuna düşürülür.
- Doğrulama: `python -m compileall -q src tests` başarılı; birim test paketi `24/24` başarılı.

### Gündem Sayfası (Ana Sayfa)

- `src/build_live_feed.py` eklendi: `gundem_2025_2026.html` üretir.
  - Transfer penceresi geri sayım banner (animasyonlu).
  - 4 özet pill: resmi transferler, sinyal sayısı, serbest kalacak, son yıl kontrat.
  - 2 sütun: sol=son 12 haber (kategori etiketleri: TRANSFER/SAKAT/CEZA), sağ=teyitli transferler + araçlar.
  - `index.html` artık gündem sayfasına yönlendiriyor.
- `html_utils.py` ve `build_transfer_tracker.py` navı güncellendi: Gündem ilk sıraya taşındı.
- Pipeline ve `news-refresh.yml`'e eklendi.

## 2026-05-25 Erken Haber Kaynak Performansı

- `src/build_source_performance_report.py` eklendi. Rapor, yönü belirli transfer iddialarını resmi kulüp duyurularıyla eşleyerek kaynak bazında resmiye dönüşüm, ölçülebilen erken yayın süresi ve `14` gün sonra halen teyitsiz kalan iddialar için yanlış-alarm vekili üretir.
- `data/processed/source_claim_history_2025_2026.json` kalıcı ilk-sinyal defteridir. Güncel haber snapshot'ında kaybolan resmi olay veya erken iddia geçmişten silinmez; sonraki resmi teyit geldiğinde ilk görüldüğü zamanla eşleştirilebilir.
- Google News kapsamı `18` aktif lig takımı, `3` genel konu ve `5` muhabir/underground izleme sorgusu olmak üzere `26/26` başarılı sorguyla `378` haber üretir. Genel ve gürültülü `Yakın Takip` sorgusu kaldırıldı; Yağız Sabuncuoğlu, Ertan Süzgün, Sports Digitale, Yusuf Günaydın ve Ekrem Konur sorguları ayrı ayrı `15` arama bulgusu üretti.
- Muhabir sorguları yalnız keşif sinyalidir; yalnız başlığında açık kaynak atfı bulunan transfer iddiası `MEDIA_REPUBLICATION` olarak muhabire yazılır. `Yakın Takip` genel haber ifadesi olduğundan muhabir hesabı sayılmaz. X snapshot'ı halen `MISSING_CREDENTIALS` ve `0` gönderidir.
- Güncel performans çıktısı: `53` transfer sinyali, tarihçe defterinde korunan `3` resmi olay, `26` gözlenen kaynak, `49` korunan tekil iddia gözlemi ve `7` skorlanabilen kaynak. Yağız Sabuncuoğlu adına açık atıflı `1` ölçülebilir medya iddiası yakalandı; Ertan Süzgün, Sports Digitale, Yusuf Günaydın ve Ekrem Konur için henüz ölçülebilir atıflı iddia yoktur.
- Resmi duyuru zamanı çıkarımı `time`, article meta ve JSON-LD üzerinden genişletildi; `Laszlo Benes` duyurusunda yayın zamanı yakalandı. Resmi `3` olayın `1/3` adedinde kesin yayın zamanı, `3/3` adedinde collector ilk-görülme zamanı bulunur. Kesin yayın süresi ve ilk-görülmeye dayalı üst-sınır metrikleri ayrı tutulur; henüz resmiye dönüşen erken sinyal bulunmadığından hesaplanan süre `0`dır.
- Mevcut olgunlaşmış örneklerde medya, Telegram ve açık muhabir atfı kanal özetleri teyide dönüşmemiş sinyalleri yanlış-alarm vekili olarak gösterir; bu oran kesin yanlış haber kararı değildir.
- Kaynak performansı ürün ekranına uygun bir yüzey olmadığı için HTML paneli kaldırıldı. İç çıktılar `data/processed/source_performance_2025_2026.{json,md}` ve `source_claim_history_2025_2026.json` olarak günlük pipeline içinde tutulur; ürün ana sayfası, komuta merkezi ve gündem ekranı bu iç rapora link vermez.
- Doğrulama: `python -m compileall -q src tests`, `python -m unittest discover -s tests -p 'test_*.py'` ve `git diff --check` başarılı; birim test paketi `36/36` geçer.

## 2026-05-25 (Session 2) — Site Kalitesi, Nav Tutarlılığı, Analiz Odağı

### Transfer Penceresi 3-State Banner

- `src/build_live_feed.py`: `WINDOW_OPEN_DATE = 2026-06-01`, `WINDOW_CLOSE_DATE = 2026-09-01` tanımlandı.
- `_window_state()` fonksiyonu 3 durum döndürür: `countdown` (mavi, geri sayım) → `open` (yeşil, kaç gün kaldı) → `closed` (gri).
- Banner rengi ve nokta rengi inline style olarak dinamik üretiliyor; her GitHub Actions çalışmasında otomatik geçiş yaşanacak.
- Şu anki durum (2026-05-25): "Transfer penceresi 6 gün sonra açılıyor" — mavi banner.

### Header/Nav Kalite Düzeltmeleri (Tüm Sayfalar)

- Tarayıcının varsayılan mor (`:visited`) ve kırmızı (`:active`) link renklerini ezmek için tüm sayfalara `.brand:visited, .brand:active { color: white }` ve `nav a:visited { color: #8fa89a }` kuralları eklendi.
- Logo ve "Gündem" nav linkleri `href="gundem_2025_2026.html"` → `href="/"` olarak güncellendi (URL temiz kalıyor).
- Topbar yüksekliği 62px → 58px; `border-bottom: 2px solid #1a3023` ile görsel ayırıcı eklendi.
- Nav link rengi `#d5ded8` → `#8fa89a` (daha dengeli kontrast); hover/active durumu `#162b20` arka plan + beyaz yazı.
- Logo yanına `| Süper Lig 2025/26` sezon etiketi eklendi — tüm sayfalarda tutarlı.
- Etkilenen kaynak dosyalar: `html_utils.py`, `build_live_feed.py`, `build_dashboard.py`, `build_all_teams_preview_dashboard.py`, `build_news_intelligence_report.py`, `build_transfer_season_context.py`, `build_transfer_recommendation_report.py`, `build_transfer_tracker.py`, `build_command_center.py`, `build_product_home.py`.

### Beşiktaş Odaklı İçeriklerin Kaldırılması

- `build_product_home.py` hero bölümündeki "Beşiktaş maç odası" butonu kaldırıldı; yerine "Maç Önü Arşivi" (18 takım, `all_teams_preview_dashboard`) geldi.
- "Beşiktaş Maç Önü Zeka Paneli" kartı → "Tüm Takım Maç Önü Arşivi" olarak genelleştirildi.
- `build_product_home.py` artık `index.html` üretmiyor (vercel.json rewrite yeterli). Eski `data/processed/index.html` git'ten silindi.
- `football_command_center` header'ındaki "Beşiktaş maç önü raporları" metni henüz güncellenmedi (düşük öncelik).

### Nav Standardizasyonu (5-Item Sabit Nav)

- Denetim sonucu: `transfer_tracker` ve `football_command_center` kaçmış; `#d5ded8` rengi, 62px yükseklik, `gundem_2025_2026.html` logosu vardı.
- `build_transfer_tracker.py` ve `build_command_center.py` güncellendi: 58px, `#8fa89a`, `/` logo, season etiket.
- `news_intelligence_dashboard`: "Haberler" extra nav item kaldırıldı; active = Gündem (haberler Gündem'in alt sayfası).
- `transfer_season_context`: "Transfer Sezonu" extra nav item kaldırıldı; active = Transferler.
- Tüm 8 ana sayfa artık aynı 5-item nav kullanıyor: Gündem → Transferler → Maç Önü → Scout → Analiz.

### Haber Tarih Filtresi

- `collect_news_google.py`: `MAX_AGE_DAYS = 14`; collector seviyesinde 14 günden eski haberler drop ediliyor.
- `collect_news_telegram.py`: Aynı `MAX_AGE_DAYS = 14` filtresi eklendi.
- `analyze_news_with_claude.py`: `recent_articles` listesi 14 gün cutoff ile ek filtreleniyor.
- Motivasyon: 9 aylık Kayseri haberi gibi çok eski içeriklerin gündem sayfasına sızması engellendi.

### Haber Kartlarına Yaş Etiketi

- `build_live_feed.py`: `_fmt_date()` fonksiyonu eklendi.
- Her haber kartında sağda "2sa", "dün", "4g önce", "az önce" formatında yaş etiketi gösteriliyor.
- Türkçe tarih formatı (ör. "21.5.2026") ile ISO 8601 formatı her ikisi de destekleniyor.

### Analiz Odaklı Ana Sayfa Yeniden Yapısı

- Ürün kimliği: haber sitesi değil, analiz/tahmin/transfer öneri platformu.
- `build_live_feed.py` layout değişti:
  - **Sol sütun**: Transferler paneli üste (öne çıktı) → altında "Haber Sinyalleri" (12'den 6'ya indirildi, ikincil konum).
  - **Sağ sütun**: Kategorili "Analiz Platformu" paneli — "Transfer & Kadro" / "Maç & Tahmin" / "Tüm Araçlar" başlıkları.
- "Son Haberler" → "Haber Sinyalleri" olarak yeniden adlandırıldı (haberler veri sinyali, ürün değil).

### Diğer

- `.env.template` commit edildi: `API_FOOTBALL_KEY`, `ANTHROPIC_API_KEY`, `X_BEARER_TOKEN` vb. boş şablon; gerçek key içermiyor.
- `transfer_tracker_2025_2026.json` uncommitted: yalnız `generated_at` timestamp farkı, pipeline bir sonraki çalışmasında güncellenecek.

### Eksikler / Sıradaki

- `football_command_center` header metni hâlâ Beşiktaş'a özgü (düşük öncelik).
- ✅ Secondary/utility sayfalar topbar eklendi: `fm_style_scout`, `league_intelligence`, `position_scout_matrix`, `enriched_scout_dashboard`, `team_needs_dashboard` artık sticky metric11 navigasyonuna sahip.
- ✅ Transfer penceresi mantığı doğrulandı: 1 Haziran 2026'da otomatik "açık" moda geçiyor, 1 Eylül'de kapanıyor.
- `og-image.svg` tagline güncellemesi yapılmadı (mevcut: "Maç Tahminleri · Scout · Transfer İstihbaratı").

## 2026-05-26 Pipeline Kararlılık Düzeltmeleri (Session 5)

- `build_dashboard.py`: Python 3.11 f-string triple-quote (`"""` inside `f"""`) uyumsuzluğu giderildi. `off_season_banner` değişkenine taşındı. GitHub Actions 3.11 kullanıyor; bu desen Python 3.12+'da çalışır.
- `refresh.yml`: `git pull --rebase` → `git pull -X ours` değiştirildi. Codex ve runner aynı anda `data/processed/` dosyalarına yazdığında artık rebase çakışması yaşanmıyor; taze build edilen dosyalar her zaman kazanıyor.
- Son 3 schedule çalışması failure idi (25.05 19:57, 26.05 04:32, 26.05 10:17); 26.05 14:51 çalışması `build_dashboard` ve `news` adımlarını geçti, push çakışmasında battı. Bu commit sonrası pipeline stabil olmalı.

## 2026-05-26 Codex - Sezon Sınırı ve Transfermarkt Eşleme Güveni

- Tarihsel analiz sezonu (`2025_2026`) ile canlı transfer izleme sezonu (`2026_2027`) ayrıldı. `config.py` içinde `TRANSFER_WATCH_SEASON` tanımlandı; Haziran-Ağustos 2026 canlı haber/transfer yüzeyleri artık `2026-2027` etiketi gösterir.
- `generate_preview_batch.py` ve `build_dashboard.py`, beslendikleri 2025/26 maç arşivinin gerçek 18 takım kadrosunda tutuldu. Böylece tüm takım maç önü kapsamı yeniden `522` rapor / `18` takım olarak üretildi; 2026/27 yükselenleri tarihsel maç raporuna veri yokken karıştırılmaz.
- Günlük TM ağ toplaması aktif kadroyu artık `transfermarkt_super_lig_squads_2026_2027.json` dosyasına yazar. `detect_squad_changes.py` parametreli hale getirildi ve 2026/27 snapshot klasörü/çıktısı ayrıldı; tarihsel 2025/26 TM snapshot'ının üstüne yazma riski kapatıldı.
- `build_transfer_tracker.py`, aktif `tm_squad_changes_2026_2027.json` çıktısını önceleyip mevcut tarihsel dosyaya geriye uyumlu fallback yapar. TM kadro tespiti ekranda resmi transfer gibi değil `TM KADRO` sinyali olarak gösterilir.
- API anahtarı bulunmayan X collector günlük `NETWORK_COMMANDS` zincirinden çıkarıldı; modül isteğe bağlı kullanım için korunur. Canlı transfer metni artık X sinyalini yalnız erişim yapılandırıldığında değerlendirildiği biçimde ifade eder.
- Manuel Transfermarkt alias eşlemeleri doğrulanmış snapshot eşleşmesiyle karıştırılmadan ayrıca izlenir: `498` doğrulanmış eşleşme, ağ teyidi bekleyen `13` manuel eşleme ve lig içi manuel dahil kullanılabilir kapsama `%81.6`. Manuel eşlemeler çözülmemiş yüksek kullanım kuyruğunu yapay biçimde büyütmez.
- Regresyon kapsamı `tests/test_transfermarkt_match_review_queue.py` ve `tests/test_season_boundaries.py` ile genişletildi. Doğrulama: `.venv/bin/python -m compileall -q src tests` ve `.venv/bin/python -m unittest discover -s tests -p 'test_*.py'` başarılı (`44/44`).

## 2026-05-26 RSS Kaynak Temizliği (Session 6)

- `collect_news_rss.py` RSS kaynak listesi 15→9 kaynağa indirildi. 5 kaynak 404 döndürüyor, 1 kaynak (NTV Spor) HTML sayfa döndürüyor (feedparser 0 entry): Sporx, Fanatik, Fotomaç, TRT Spor, Goal.com TR, NTV Spor kaldırıldı.
- URL düzeltmeleri: Aksam `/rss/spor`→`/rss/rss.asp`, Posta `/rss/spor`→`/rss`, Haberturk `/rss` (genel)→`/rss/spor.xml` (spor özel, 30 entry).
- Kalan 9 çalışan kaynak: Hürriyet, Milliyet, Sabah, Haberturk Spor, AA Spor, Takvim, Aksam, Posta, CNN Türk.

## 2026-05-26 Transfer Sezonu Modu ve Diğer İyileştirmeler (Session 5)

- `build_live_feed.py`: Transfer penceresi 3-durumlu banner eklendi; `_is_transfer_season` bayrağıyla ana sayfa layout'u dinamik olarak transfer sezonu moduna geçiyor. Transfer sezonu paneli (serbest kalacak, son yıl kontrat, transfer sinyali, piyasa değeri metrik grid'i) ve Analiz Platformu transfer/scout linkleri aktifleşiyor.
- `build_dashboard.py`: Python 3.11 uyumlu `off_season_banner` değişkeni, "Sezon arısı" yazım hatası düzeltmesi.
- `src/model_league_predictions.py`: `DRAW_PRED_MAX_GAP` 0.14→0.18; beraberlik recall %28.9→%40.8, genel doğruluk %51.6→%50.4.
- `src/build_oos_validation.py`: `draw_calibrated_prediction` çağrısına eksik `strength_edge` parametresi eklendi; backtest ile ana model tutarsızlığı giderildi.
- OG Image: `data/processed/og-image.png` üretildi (1200×630 Pillow PNG). Tüm 10 HTML builder dosyasında `og:image` SVG→PNG ve göreceli→mutlak URL (`https://metric11.com/og-image.png`); Twitter/X kart önizlemesi düzeltildi.
- `collect_news_telegram.py`: Aktif olmayan 4 kanal kaldırıldı (superligson, futbolhaber, superligtransfer, basaksehirhaberleri); aktif kanal sayısı 11→7.
- Secondary page topbarlar: `build_fm_style_scout_program.py`, `build_league_intelligence_report.py`, `build_position_scout_matrix.py`, `build_enriched_scout_dashboard.py`, `build_team_needs_dashboard.py` — 5 dosyaya standart sticky metric11 topbar eklendi.
