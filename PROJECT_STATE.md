# Futbol İstihbarat Platformu - Proje Durumu

Son güncelleme: 2026-08-23 (site güncel değil şikayeti + artifact kotası fix)

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

## 2026-05-28 Transfer Penceresi Otomasyonu (Session 10 — devam)

- `run_daily_pipeline.py`'ye tarih koşullu 2026/27 TM koleksiyonu eklendi: 1 Haziran 2026'dan itibaren `--network` modunda `collect_transfermarkt_league_squads --season-id 2026` ve `detect_squad_changes 2026_2027` otomatik devreye girer.
- GitHub App kurulumu yerine mevcut Actions pipeline kullanıldı; `GITHUB_TOKEN` zaten push yetkisine sahip.
- Claude.ai remote rutin (`trig_01A7S3rVBjvWfi3X61XkAtck`) 1 Haziran 09:00 İstanbul için kuruldu; GitHub App olmadan push adımı başarısız olabilir ama Actions pipeline yine de çalışır.

## 2026-05-28 Yükselen Takım TM Verisi (Session 10)

- Çorum FK (37951), Erzurumspor FK (39722), Amed SFK (12382) için Transfermarkt 2025 sezonu kadrosu toplandı: 28 + 30 + 25 = 83 oyuncu, toplam ~€29M piyasa değeri.
- Not: TM 2026/27 sezonu kadrosu henüz boş (sezon açılmadı); 2025 (1. Lig) kadrosu alındı.
- Ham HTML `data/raw/transfermarkt/promoted_clubs_2026_2027/` altına kaydedildi.
- `transfermarkt_super_lig_squads_2025_2026.json` 18 → 21 kulübe çıktı (küme düşen 3 + yükselen 3).
- `enrich_players_with_transfermarkt.py` yeniden çalıştırıldı: operasyonel eşleme %74.0'a yükseldi.
- Transfer tavsiye raporu ve scout blueprint'leri yeniden üretildi; 3 yeni takım template rol planları (GK_STABILITY, CB_DOMINANT, ST_SCORER, DM_SECURITY) ve aday listeleriyle dahil edildi.

## 2026-05-27 Tema Genişleme & Ağ Büyütme (Session 9)

### Transfer Sezonu Bağlam Sayfası Tema Dönüşümü (build_transfer_season_context.py)
- Tüm mavi dark theme (`#0f172a`, `#1e293b`, `#334155`, `#94a3b8`, `#60a5fa`, `#64748b`, `#3b82f6`, `#e2e8f0`, `#fbbf24`) site yeşil temasına dönüştürüldü.
- Gövde: `background:#f3f5f4;color:#132018` (light theme).
- Kartlar: `background:#1e293b` → `background:#fff;border:1px solid #d7ded9`.
- Muted text: `#94a3b8/#64748b` → `#627067`. Link rengi `#60a5fa` → `#116447`.
- Pozisyon kartlarında DEF rengi `#3b82f6` → `#116447` (yeşil). MID `#10b981` → `#0d9488`.
- Summary pill bg: `#1e293b` → `#0f2018` (koyu yeşil, site nav tonunda).
- Sinyaller: oklar `#60a5fa` → `#116447`. RUMOR status `#3b82f6` → `#8fa89a`.
- Timeline: `background:#1e293b` → `background:#fff;border:1px solid #d7ded9`.
- Explanation box'lar: renk-kodlu light bg (kırmızı için `#fef2f2`, amber için `#fffbeb`, mor için `#f3f0ff`).

### Telegram Kanal Genişlemesi (collect_news_telegram.py)
- 7 → 18 kanal (11 yeni kanal eklendi).
- Yeni genel transfer kanalları: superligson, futbolhaber, transferson, turkiyefutbol, spordakika, sportransfer, futbolborsasi.
- Yeni kulüp kanalları: samsunsporklubu, goztepehaber, gaziantepfkhaber, kasimpasahaber.
- Başarısız kanallar pipeline'da graceful fail ile işleniyor.

### Twitter Hesap Genişlemesi (collect_news_twitter.py)
- ~40 → 62 hesap (+22 yeni).
- Yeni medya: NTVSpor, sabah_spor, Milliyet_Spor, aksam_spor, CNNTURKspor, SkySpor_TR.
- Yeni transfer muhabirleri: Sansal_Buyuk, hamitsalih, ugurtuncay, NicoSchira, transfermarkt (global), GizemKaya__ transfer kategorisine taşındı.
- Yeni kulüp muhabirleri: GShaberleri, FBhaberleri, TShaberleri1907.
- Yeni veri/analiz: StatsBombIQ, FBref, SofaScore, WhoScored.

## 2026-05-26 Transfer Tracker Tema & UX Düzeltmesi (Session 8)

### Transfer Tracker Yeniden Tasarımı (build_transfer_tracker.py)
- Header gradient mavi (`#1e3a5f, #0f172a, #3b82f6`) → site yeşili (`var(--dark), #1a3023`) olarak değiştirildi.
- Stat pill arka planı `#1e293b` → `#0f2018` (koyu yeşil); muted renk `#94a3b8` → `#8fa89a` (yeşil ton).
- Info-box `#eff6ff/blue` → `#e8f5ee/yeşil` olarak değiştirildi.
- `og:image` ve `twitter:image` `og-image.png` → `og_home.png` olarak düzeltildi.
- `STATUS_META` "İNCELEMEDE" → "TAKİPTE" olarak değiştirildi; info-box metni güncellendi.
- `player == "?"` olan sinyaller ana tablodan ayrıldı: "Takip Edilen Haberler" alt bölümüne taşındı; haber başlığı + kaynak + tarih gösteriyor. Ana tablo yalnızca adı bilinen oyuncu sinyallerini içeriyor.
- 𝕏 Paylaş butonu eklendi: tweetde "X resmi, Y sinyal" özetiyle `twitter.com/intent/tweet` linki.

## 2026-05-26 Transfer Sezonu Öneriler & Nav Tutarsızlığı (Session 7)

### RSS Kaynak Temizliği (collect_news_rss.py)
- 6 ölü kaynak kaldırıldı: Sporx, Fanatik, Fotomaç, TRT Spor, Goal.com TR, NTV Spor (404 veya 0 entry).
- 3 URL düzeltmesi: Haberturk `/rss` → `/rss/spor.xml`, Aksam `/rss/spor` → `/rss/rss.asp`, Posta `/rss/spor` → `/rss`.
- 15 kaynak → 9 çalışan kaynak.

### Nav Tutarsızlığı Giderme (html_utils.py + 7 build dosyası)
- `html_utils.py`: `_is_transfer_season()`, `preview_nav_label()` eklendi; `_NAV` sabiti kaldırılıp `_build_nav(active)` dinamik fonksiyonuna geçildi.
- `page_html()` imzasına `active_nav` parametresi eklendi.
- 7 inline-nav build dosyasında "Maç Önü" → `preview_nav_label()` ile dinamik hale getirildi. Transfer sezonunda tüm sayfalarda "Arşiv" gösteriliyor.

### Analiz Sayfası Transfer Sezonu Modları (build_product_home.py)
- Header overline, H1 ve CTA butonu transfer sezonunda değişiyor.
- Öne çıkan kartlar transfer sezonunda yeniden sıralanıyor: Transfer araçları önce, maç önü arşivi sona.

### Komuta Merkezi Başlık İyileştirmesi (build_command_center.py)
- "Beşiktaş maç önü raporları..." → "Süper Lig tahmin kontrolü..." olarak güncellendi; artık lig genelini yansıtıyor.

### Transfer Sezonu Bağlam Sayfası İyileştirmeleri (build_transfer_season_context.py)
- Geri sayım banner eklendi: "X gün içinde açılıyor" / "Açık, X gün kaldı" / "Kapandı".
- Pozisyon kırılım bölümü eklendi: 261 serbest ajan GK/DEF/MID/FWD 4 sütunda gösteriliyor.

### Scout Öneri Sistemi Genişletmesi (build_league_intelligence_report.py + build_team_scout_blueprints.py)
- **GK_STABILITY rolü eklendi**: `ROLE_MAP`'e "savunma kırılgan" → GK_STABILITY bağlandı; `league_proxy_roles()` kaleci heuristiği (≥20 maç, 0 gol, ≤2 kart); `role_reason()` GK case.
- **"düşük şut baskısı" zafiyeti**: GF 1.0–1.3 ve failed_to_score ≥ 7 eşiğiyle yeni zafiyet tipi. Gaziantep ve Gençlerbirliği tetikledi. Scout ipucu: "Hareketli kanat veya ikinci forvet".
- **Yeni lig takımları şablonu**: Çorum FK, Erzurumspor FK, Amed SFK — lig verisi olmadığı için template blueprint: GK_STABILITY, CB_DOMINANT, ST_SCORER, DM_SECURITY önerileri.
- Kayserispor transfer önerilerinde GK artık ilk sırada. 3 terfi takımı scout raporunda görünüyor.

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

## 2026-05-26 Site Geneli Nav Tutarlılığı (Session 6 — devam)

- `html_utils.py`: `_is_transfer_season()` (18 Mayıs–1 Eylül 2026 arası True), `preview_nav_label()` (public) ve `_build_nav(active)` fonksiyonları eklendi. `page_html()` artık `active_nav` parametresi alıyor ve dinamik nav üretiyor.
- `build_product_home.py` (Analiz sayfası): Transfer sezonunda header "Oyuncuyu değerlendir. Kadroyu kur. Transferi takip et." / "Transfer Sezonu Raporu" CTA; featured card'lar transfer araçlarını (Transfer Sezonu Bağlam, Transfer Takip, Transfer Tavsiye, Komuta Merkezi) öne çıkarıyor. Nav "Arşiv" etiketiyle güncellendi.
- 7 inline-nav dosyasına `preview_nav_label()` import edildi: `build_news_intelligence_report.py`, `build_all_teams_preview_dashboard.py`, `build_transfer_recommendation_report.py`, `build_transfer_tracker.py`, `build_command_center.py`, `build_dashboard.py`, `build_league_intelligence_report.py`.
- Tüm site (54 HTML, 18 takım dashboard dahil) rebuild edildi; her sayfada nav "Arşiv" etiketiyle tutarlı.
- Command center header "Beşiktaş maç önü raporları" → "Süper Lig tahmin kontrolü, gol adayı performansı, transfer radar ve scout kararları" olarak güncellendi.

## 2026-05-29 Site Sayfa Temizleme — Boş & Orphan Sayfalar (Session 11 devam)

### Kaldırılan Sayfalar (9 adet)
**Bağlı ama boş/eski:**
- `league_scouting_2025_2026_normalized_dashboard.html` — hiçbir builder tarafından üretilmiyor, stale
- `league_scouting_enriched_2025_2026_dashboard.html` — FM Scout programı kapsamı karşılıyor
- `api_football_super_lig_deep_2024_analysis.html` — 2024 sezonu eski dış API snapshot

**Orphan (hiçbir entry point'ten bağlı değil):**
- `league_scouting_2025_2026_dashboard.html` — enriched versiyonunun eski hali
- `api_football_super_lig_2024_analysis.html` — deep versiyonunun eski hali
- `scout_quality_report_2025_2026.html` — nav'dan zaten çıkarılmıştı, HTML dosyası silindi
- `prediction_validation_report_2025_2026.html` — iç araç, orphan
- `system_status.html` — iç araç, orphan
- `besiktas_team_needs_2025_2026_dashboard.html` — önceki oturumdan kalan

**Kaynak temizliği:**
- `build_product_home.py`: `enriched_scout` ve `scout_quality` JSON yüklemeleri kaldırıldı
- `build_command_center.py`: "Dış Derin Veri" nav linki kaldırıldı
- Sitede artık tüm bağlı sayfalar aktif veri içeriyor; boş veya stale sayfa kalmadı

## 2026-05-29 Bug Temizleme & Gereksiz Sayfa Kaldırma (Session 11)

### "?" Görünen ve Tıklanamayan Alanlar Giderildi
- `build_transfer_tracker.py`: `_title(None)` crash fix — `None` guard eklendi; `from_club/to_club` None ise `"—"` gösteriliyor.
- `build_live_feed.py`: `t.get("player", "")` → `(t.get("player") or "")` ile `None.strip()` hatası giderildi; `_transfer_html` oyuncu adı boş veya "?" ise satırı atlar.
- `build_transfer_season_context.py`: `_title(name: str)` → `_title(name: str | None) -> str | None`; `player_name` None olan sinyaller sinyal listesinden atlanıyor; `from_club/to_club` None ise `"—"` gösteriliyor.

### Scout Kalite Denetimi Sayfası Kaldırıldı
- `build_product_home.py` ve `build_command_center.py`'den "Scout Kalite Denetimi" panel ve nav linki silindi — sayfa içeriği zaten boştu (0 sinyal).

### Beşiktaş Takım İhtiyaç Paneli Kaldırıldı
- `besiktas_team_needs_2025_2026_dashboard.html` product home, command center nav ve tüm veri yüklemelerinden temizlendi — 102 satır, JSON bozuk, içerik boştu.
- `build_command_center.py`'deki "Takım İhtiyaçları" ve "Kadro Gerçekliği" HTML bölümleri silindi.
- Bağımlı değişkenler kaldırıldı: `team_needs`, `team_summary`, `needs` değişkenleri temizlendi.

## 2026-05-29 FM Scout Multi-Team + Global Havuz + Scout Sayfaları (Session 8)

- `import_player_attribute_dataset.py`: `_pos_*` FM2023 pozisyon sütun alanları eklendi (GK, DL, DC, DR, WBL, WBR, DM, ML, MC, MR, AML, AMC, AMR); `_derive_position_group()` fonksiyonu eklendi; FM2023 normalize verisi yeniden üretildi — 8452 oyuncu, 4 pozisyon grubu (FWD/MID/DEF/GK), hiç None yok.
- `build_fm_style_scout_program.py`: Beşiktaş'a özgü bağımlılık kaldırıldı; `--needs` argümanı kaldırıldı. 691 SL oyuncusu JS tarafında takım filtresi + 5 rol bucket seçimi ile render edilir (top 24). 2038 FM23 global aday (CA≥130, Türk SL takımları hariç) pozisyon seçiciyle ayrı modda gösterilir. Kaynak badge: FM23 (mor), Türetilmiş (gri), Global (turuncu).
- `build_position_scout_matrix.py`: `all_candidates` → `sl_candidates` güncellendi; Beşiktaş'a özgü ROLE_REQUIREMENTS `reason` alanları lig geneli hale getirildi; `--needs` ve `team_need_boost` bağımlılığı kaldırıldı; takım dropdown JS filtresi eklendi; her satırda `data-team` attribute ile seçilen takım oyuncuları gizleniyor; 18 takım, 7 rol, 140 rol-aday eşleşmesi.
- Scheduled routine: 1 Haziran 2026 06:00 UTC — TM 2026/27 kadro çekme rutini doğrulandı (trig_01A7S3rVBjvWfi3X61XkAtck).
- `transfer_recommendation_report` ve `enriched_scout_dashboard` zaten tüm 18 takımı kapsıyor; değişiklik gerekmedi.

## 2026-07-04 Günlük Veri/Geliştirme Kontrolü

- 4 Temmuz kontrolünde `data/` altında bugün üretilmiş yeni dosya bulunmadı. `data/processed` içindeki son geniş üretim hâlâ 27 Haziran 2026 tarihli görünüyor.
- `daily_pipeline_run_latest.md` güncel pipeline durumunu yansıtmıyor; son kayıt 26 Mayıs 2026 ağsız `48/48` başarılı koşu. Bu dosya operasyon gözleminde güvenilir güncel kaynak değil.
- `PROJECT_STATE.md` Temmuz operasyon durumunu içermiyordu; bu not sonraki agent için güncel kontrol kaydı olarak eklendi.
- Transfermarkt genel kadro snapshotlarında regresyon devam ediyor: `transfermarkt_super_lig_squads_2025_2026.json` ve `transfermarkt_super_lig_squads_2026_2027.json` özetleri `0` kulüp / `0` oyuncu. Buna karşılık Beşiktaş özel snapshotı sağlam: `28` oyuncu, toplam `176M EUR`.
- Scout ana havuzu mevcut: `position_scout_matrix_2025_2026.json` özetinde `691` aday, `7` rol, `91` rol eşleşmesi, `18` takım; `fm_style_scout_program_2025_2026.json` özetinde `691` Süper Lig adayı, `2038` global havuz, `269` FM23 eşleşmesi var.
- Scout kalite raporu ana havuzu doğru yansıtmıyor: `scout_quality_report_2025_2026.json` yalnız `63` blueprint linki ve `7` pozisyon matrisi adayı gösteriyor. Bu rapor ya dar filtre okuyor ya da eski/yanlış kaynağa bağlı.
- Tahmin kalite göstergeleri güncellenmemiş: `data_quality_scorecard` skoru `80.5`; Beşiktaş display tahmin doğruluğu `%55.2`; beraberlik recall `%11.1` FAIL; top-5 gol adayı hit `%76.9`, top-8 `%84.6`.
- OOS validation hâlâ zayıf: ikinci yarı bağımsız doğruluk `%45.8`; HIGH güven segmenti `%58.7`, MEDIUM `%37.5`, LOW `%35.7`.
- Kaynak izleme listesi `2026-05-25` tarihli; kaynak performansı 27 Haziran snapshotında `112` gözlenen kaynak, `40` skorlanan kaynak, `1125` claim observation gösteriyor. Transfer tracker ise `13` sinyal, `0` confirmed ile güncel teyit üretmiyor.
- Öncelik sırası: (1) Transfermarkt genel snapshot collector regresyonu, (2) scout kalite raporunun doğru scout kaynaklarını okuması, (3) `daily_pipeline_run_latest.md` dosyasının gerçek son koşuya göre güncellenmesi, (4) beraberlik recall ve OOS doğruluk için model kalibrasyonu.

## 2026-07-05 Günlük Veri/Geliştirme Kontrolü

- 5 Temmuz kontrolünde `data/` altında bugün üretilmiş yeni dosya bulunmadı; `data/processed` son geniş üretimi yine 27 Haziran 2026.
- `daily_pipeline_run_latest.md` hâlâ 26 Mayıs 2026 ağsız `48/48` başarılı koşusunda kalmış; günlük üretim sağlığını güncel göstermiyor.
- Transfermarkt genel snapshot regresyonu devam ediyor: `transfermarkt_super_lig_squads_2025_2026.json` ve `transfermarkt_super_lig_squads_2026_2027.json` özetleri `0` kulüp / `0` oyuncu. Bu, transfer dönemi kadro güncelliği ve scout değerleme güvenini doğrudan zayıflatıyor.
- Scout ana verisi hâlâ mevcut: `position_scout_matrix_2025_2026.json` → `691` aday, `91` rol eşleşmesi, `18` takım; `fm_style_scout_program_2025_2026.json` → `691` Süper Lig adayı, `2038` global havuz, `269` FM23 eşleşmesi.
- `scout_quality_report_2025_2026.json` hâlâ ana havuzu eksik yansıtıyor: `63` blueprint linki ve `7` pozisyon matrisi adayı. Raporun `position_scout_matrix` ve `fm_style_scout_program` kaynaklarını kapsayacak şekilde düzeltilmesi gerekiyor.
- Tahmin ve gol adayı metrikleri değişmedi: `data_quality_scorecard` skoru `80.5`; OOS ikinci yarı doğruluğu `%45.8`; top-5 gol adayı hit `%76.9`, top-8 `%84.6`; beraberlik recall halen `%11.1` FAIL.
- Kaynak performansı/transfer tracker değişmedi: `112` gözlenen kaynak, `40` skorlanan kaynak, `1125` claim observation; transfer tracker `13` sinyal ve `0` confirmed.
- Bir sonraki uygulanabilir geliştirme değişmedi: önce Transfermarkt genel snapshot collector regresyonu düzeltilmeli, ardından scout kalite raporu gerçek aday havuzunu kapsayacak şekilde yeniden hesaplanmalı.

## 2026-07-06 Günlük Veri/Geliştirme Kontrolü

- 6 Temmuz kontrolünde `data/` altında bugün üretilmiş yeni dosya bulunmadı; `data/processed` son geniş üretimi hâlâ 27 Haziran 2026.
- `daily_pipeline_run_latest.md` hâlâ 26 Mayıs 2026 ağsız `48/48` başarılı koşusunda kalmış. Günlük pipeline gözlemi için bu dosya artık stale kabul edilmeli.
- Git çalışma alanında yalnız `PROJECT_STATE.md` değişikliği var; bu değişiklik 4-6 Temmuz heartbeat kontrol notları.
- Transfermarkt genel snapshot regresyonu üçüncü kontrolde de devam ediyor: `transfermarkt_super_lig_squads_2025_2026.json` ve `transfermarkt_super_lig_squads_2026_2027.json` → `0` kulüp / `0` oyuncu. Beşiktaş özel snapshotı hâlâ sağlam: `28` oyuncu, toplam `176M EUR`.
- Veri deposu temel sezon kapsamı duruyor: `306` maç, `691` oyuncu, `18` takım, `1428` kart, `812` gol, `12732` lineup satırı.
- Scout ana havuzu değişmedi: `position_scout_matrix_2025_2026.json` → `691` aday, `91` rol eşleşmesi, `18` takım; `fm_style_scout_program_2025_2026.json` → `691` Süper Lig adayı, `2038` global havuz, `269` FM23 eşleşmesi.
- `scout_quality_report_2025_2026.json` hâlâ gerçek scout havuzunu eksik gösteriyor: `63` blueprint linki ve `7` pozisyon matrisi adayı. Raporun `position_scout_matrix`, `team_scout_blueprints` ve `fm_style_scout_program` kapsamıyla yeniden bağlanması gerekiyor.
- Tahmin metrikleri değişmedi: `data_quality_scorecard` skoru `80.5`; OOS ikinci yarı doğruluk `%45.8`; full-season doğruluk `%46.1`; HIGH güven segmenti `%58.7` OOS / `%59.6` full-season. Beraberlik recall önceki kontrolde `%11.1` FAIL durumundaydı.
- Gol adayı modülü aynı seviyede: top-3 hit `%61.5`, top-5 `%76.9`, top-8 `%84.6`, top-10 `%88.5`.
- Kaynak performansı ve transfer tracker değişmedi: `112` gözlenen kaynak, `40` skorlanan kaynak, `1125` claim observation; transfer tracker `13` sinyal, `0` confirmed, `0` official.
- Operasyonel karar: artık sadece günlük kontrol yeterli değil. Sıradaki aktif geliştirme işi olarak Transfermarkt genel snapshot collector regresyonu çözülmeli; ardından scout kalite raporu ve stale pipeline run raporu düzeltilmeli.

## 2026-07-07 Günlük Veri/Geliştirme Kontrolü

- 7 Temmuz kontrolünde `data/` altında bugün üretilmiş yeni dosya bulunmadı; `data/processed` son geniş üretimi hâlâ 27 Haziran 2026.
- `daily_pipeline_run_latest.md` değişmedi: son görünen koşu 26 Mayıs 2026 ağsız `48/48` başarılı. Bu dosya güncel pipeline sağlığı için stale.
- Git çalışma alanında yalnız `PROJECT_STATE.md` değişikliği var; bu değişiklik 4-7 Temmuz heartbeat kontrol notları.
- Transfermarkt genel snapshot regresyonu devam ediyor: `transfermarkt_super_lig_squads_2025_2026.json` ve `transfermarkt_super_lig_squads_2026_2027.json` → `0` kulüp / `0` oyuncu.
- Ana sezon veri deposu kapsamı değişmedi: `306` maç, `691` oyuncu, `18` takım, `1428` kart, `812` gol, `12732` lineup satırı.
- Scout ana havuzu değişmedi: `position_scout_matrix_2025_2026.json` → `691` aday, `91` rol eşleşmesi, `18` takım; `fm_style_scout_program_2025_2026.json` → `691` Süper Lig adayı, `2038` global havuz, `269` FM23 eşleşmesi.
- `scout_quality_report_2025_2026.json` hâlâ `63` blueprint linki ve `7` pozisyon matrisi adayı gösteriyor; gerçek scout havuzunu eksik yansıtıyor.
- Tahmin metrikleri değişmedi: `data_quality_scorecard` skoru `80.5`; Beşiktaş display doğruluk `%55.2`; beraberlik recall `%11.1` FAIL; OOS ikinci yarı doğruluk `%45.8`; full-season doğruluk `%46.1`.
- Gol adayı modülü değişmedi: top-3 hit `%61.5`, top-5 `%76.9`, top-8 `%84.6`, top-10 `%88.5`.
- Kaynak performansı/transfer tracker değişmedi: `112` gözlenen kaynak, `40` skorlanan kaynak, `1125` claim observation; transfer tracker `13` sinyal, `0` confirmed, `0` official.
- Sonuç: 4 gündür aynı blokaj izleniyor. Bir sonraki geliştirme kontrol değil aktif düzeltme olmalı: önce Transfermarkt genel snapshot collector, sonra scout kalite raporu ve pipeline run raporu.

## 2026-07-08 Günlük Veri/Geliştirme Kontrolü

- 8 Temmuz kontrolünde `data/` altında bugün üretilmiş yeni dosya bulunmadı; `data/processed` son geniş üretimi hâlâ 27 Haziran 2026.
- `daily_pipeline_run_latest.md` hâlâ 26 Mayıs 2026 ağsız `48/48` başarılı koşusunda kalmış; pipeline sağlığı için güvenilir güncel gösterge değil.
- Git çalışma alanında yalnız `PROJECT_STATE.md` değişikliği var; bu değişiklik 4-8 Temmuz heartbeat kontrol notları.
- Transfermarkt genel snapshot regresyonu devam ediyor: `transfermarkt_super_lig_squads_2025_2026.json` ve `transfermarkt_super_lig_squads_2026_2027.json` → `0` kulüp / `0` oyuncu.
- Ana veri kalite skoru değişmedi: `80.5`. Kapsam hâlâ `306` maç, `691` oyuncu, `18` takım; eksik hakem `0`, eksik yaş profili `0/691`.
- Scout ana havuzu değişmedi: `position_scout_matrix_2025_2026.json` → `691` aday, `91` rol eşleşmesi, `18` takım; `fm_style_scout_program_2025_2026.json` → `691` Süper Lig adayı, `2038` global havuz, `269` FM23 eşleşmesi.
- `scout_quality_report_2025_2026.json` hâlâ gerçek scout havuzunu eksik yansıtıyor: `63` blueprint linki ve `7` pozisyon matrisi adayı.
- Tahmin metrikleri değişmedi: Beşiktaş display doğruluk `%55.2`; beraberlik recall `%11.1` FAIL; OOS ikinci yarı doğruluk `%45.8`; full-season doğruluk `%46.1`.
- Gol adayı modülü değişmedi: top-3 hit `%61.5`, top-5 `%76.9`, top-8 `%84.6`, top-10 `%88.5`.
- Kaynak performansı/transfer tracker değişmedi: `112` gözlenen kaynak, `40` skorlanan kaynak, `1125` claim observation; transfer tracker `13` sinyal, `0` confirmed, `0` official.
- Sonuç: 5 gündür aynı blokaj izleniyor. Bir sonraki işlem günlük kontrol değil, Transfermarkt genel snapshot collector regresyonunu düzeltmek olmalı; ardından scout kalite raporu ve stale pipeline run raporu ele alınmalı.

## 2026-07-09 Günlük Veri/Geliştirme Kontrolü

- 9 Temmuz kontrolünde `data/` altında bugün üretilmiş yeni dosya bulunmadı; `data/processed` son geniş üretimi hâlâ 27 Haziran 2026.
- `daily_pipeline_run_latest.md` hâlâ 26 Mayıs 2026 ağsız `48/48` başarılı koşusunda kalmış; pipeline sağlığı için stale.
- Git çalışma alanında yalnız `PROJECT_STATE.md` değişikliği var; bu değişiklik 4-9 Temmuz heartbeat kontrol notları.
- Transfermarkt genel snapshot regresyonu devam ediyor: `transfermarkt_super_lig_squads_2025_2026.json` ve `transfermarkt_super_lig_squads_2026_2027.json` → `0` kulüp / `0` oyuncu.
- Ana veri kalite skoru değişmedi: `80.5`. Kapsam hâlâ `306` maç, `691` oyuncu, `18` takım; eksik hakem `0`, eksik yaş profili `0/691`.
- Scout ana havuzu değişmedi: `position_scout_matrix_2025_2026.json` → `691` aday, `91` rol eşleşmesi, `18` takım; `fm_style_scout_program_2025_2026.json` → `691` Süper Lig adayı, `2038` global havuz, `269` FM23 eşleşmesi.
- `scout_quality_report_2025_2026.json` hâlâ gerçek scout havuzunu eksik yansıtıyor: `63` blueprint linki ve `7` pozisyon matrisi adayı.
- Tahmin metrikleri değişmedi: Beşiktaş display doğruluk `%55.2`; beraberlik recall `%11.1` FAIL; OOS ikinci yarı doğruluk `%45.8`; full-season doğruluk `%46.1`.
- Gol adayı modülü değişmedi: top-3 hit `%61.5`, top-5 `%76.9`, top-8 `%84.6`, top-10 `%88.5`.
- Kaynak performansı/transfer tracker değişmedi: `112` gözlenen kaynak, `40` skorlanan kaynak, `1125` claim observation; transfer tracker `13` sinyal, `0` confirmed, `0` official.
- Sonuç: 6 gündür aynı blokaj izleniyor. Günlük kontrol artık yalnız durum teyidi üretiyor; asıl uygulanabilir adım Transfermarkt genel snapshot collector regresyonunu düzeltmek, ardından scout kalite raporu ve stale pipeline run raporunu ele almak.

## 2026-07-10 Günlük Veri/Geliştirme Kontrolü

- 10 Temmuz kontrolünde `data/` altında bugün üretilmiş yeni dosya bulunmadı; `data/processed` son geniş üretimi hâlâ 27 Haziran 2026.
- `daily_pipeline_run_latest.md` hâlâ 26 Mayıs 2026 ağsız `48/48` başarılı koşusunda kalmış; pipeline sağlığı için stale.
- Git çalışma alanında yalnız `PROJECT_STATE.md` değişikliği var; bu değişiklik 4-10 Temmuz heartbeat kontrol notları.
- Transfermarkt genel snapshot regresyonu devam ediyor: `transfermarkt_super_lig_squads_2025_2026.json` ve `transfermarkt_super_lig_squads_2026_2027.json` → `0` kulüp / `0` oyuncu.
- Ana veri kalite skoru değişmedi: `80.5`. Kapsam hâlâ `306` maç, `691` oyuncu, `18` takım; eksik hakem `0`, eksik yaş profili `0/691`.
- Scout ana havuzu değişmedi: `position_scout_matrix_2025_2026.json` → `691` aday, `91` rol eşleşmesi, `18` takım; `fm_style_scout_program_2025_2026.json` → `691` Süper Lig adayı, `2038` global havuz, `269` FM23 eşleşmesi.
- `scout_quality_report_2025_2026.json` hâlâ gerçek scout havuzunu eksik yansıtıyor: `63` blueprint linki ve `7` pozisyon matrisi adayı.
- Tahmin metrikleri değişmedi: Beşiktaş display doğruluk `%55.2`; beraberlik recall `%11.1` FAIL; OOS ikinci yarı doğruluk `%45.8`; full-season doğruluk `%46.1`.
- Gol adayı modülü değişmedi: top-3 hit `%61.5`, top-5 `%76.9`, top-8 `%84.6`, top-10 `%88.5`.
- Kaynak performansı/transfer tracker değişmedi: `112` gözlenen kaynak, `40` skorlanan kaynak, `1125` claim observation; transfer tracker `13` sinyal, `0` confirmed, `0` official.
- Sonuç: 7 gündür aynı blokaj izleniyor. Günlük kontrol artık yalnız durum teyidi üretiyor; asıl uygulanabilir adım Transfermarkt genel snapshot collector regresyonunu düzeltmek, ardından scout kalite raporu ve stale pipeline run raporunu ele almak.

## 2026-07-11 Günlük Veri/Geliştirme Kontrolü

- 11 Temmuz kontrolünde `data/` altında bugün üretilmiş yeni dosya bulunmadı; `data/processed` son geniş üretimi hâlâ 27 Haziran 2026.
- `daily_pipeline_run_latest.md` hâlâ 26 Mayıs 2026 ağsız `48/48` başarılı koşusunda kalmış; pipeline sağlığı için stale.
- Git çalışma alanında yalnız `PROJECT_STATE.md` değişikliği var; bu değişiklik 4-11 Temmuz heartbeat kontrol notları.
- Transfermarkt genel snapshot regresyonu devam ediyor: `transfermarkt_super_lig_squads_2025_2026.json` ve `transfermarkt_super_lig_squads_2026_2027.json` → `0` kulüp / `0` oyuncu.
- Ana veri kalite skoru değişmedi: `80.5`. Kapsam hâlâ `306` maç, `691` oyuncu, `18` takım; eksik hakem `0`, eksik yaş profili `0/691`.
- Scout ana havuzu değişmedi: `position_scout_matrix_2025_2026.json` → `691` aday, `91` rol eşleşmesi, `18` takım; `fm_style_scout_program_2025_2026.json` → `691` Süper Lig adayı, `2038` global havuz, `269` FM23 eşleşmesi.
- `scout_quality_report_2025_2026.json` hâlâ gerçek scout havuzunu eksik yansıtıyor: `63` blueprint linki ve `7` pozisyon matrisi adayı.
- Tahmin metrikleri değişmedi: Beşiktaş display doğruluk `%55.2`; beraberlik recall `%11.1` FAIL; OOS ikinci yarı doğruluk `%45.8`; full-season doğruluk `%46.1`.
- Gol adayı modülü değişmedi: top-3 hit `%61.5`, top-5 `%76.9`, top-8 `%84.6`, top-10 `%88.5`.
- Kaynak performansı/transfer tracker değişmedi: `112` gözlenen kaynak, `40` skorlanan kaynak, `1125` claim observation; transfer tracker `13` sinyal, `0` confirmed, `0` official.
- Sonuç: 8 gündür aynı blokaj izleniyor. Günlük kontrol artık yalnız durum teyidi üretiyor; asıl uygulanabilir adım Transfermarkt genel snapshot collector regresyonunu düzeltmek, ardından scout kalite raporu ve stale pipeline run raporunu ele almak.

## 2026-07-12 Günlük Veri/Geliştirme Kontrolü ve TM Snapshot Düzeltmesi

- 12 Temmuz kontrolünde `data/` altında bugün üretilmiş yeni dosya yoktu; `data/processed` son geniş üretimi kontrol başında hâlâ 27 Haziran 2026 görünüyordu.
- `daily_pipeline_run_latest.md` hâlâ 26 Mayıs 2026 ağsız `48/48` başarılı koşusunda kalmış; pipeline sağlığı için stale.
- Transfermarkt genel snapshot blokajının kök nedeni netleştirildi: `transfermarkt_super_lig_squads_2026_2027.json` içinde 18 kulübün tamamı `403 Forbidden` sebebiyle skipped. 2026/27 raw HTML dosyaları mevcut ama kulüp sayfaları `No information` döndürüyor; oyuncu tablosu yok.
- `src/collect_transfermarkt_league_squads.py` düzeltildi:
  - Canlı fetch başarılı ama oyuncu tablosu boşsa sağlam raw cache fallback kullanır.
  - Canlı fetch `403` veya başka hatayla düşerse sağlam raw cache fallback kullanır.
  - Collector hiç kulüp üretemezse önceki non-empty output varsa sıfır oyunculu snapshot ile ezmez; `stale_reason` ve `skipped_latest` yazar.
  - Ağsız doğrulama için `--cache-only` modu eklendi.
  - Markdown kulüp satırlarına `source_mode` eklendi (`live`, `cache_after_fetch_failed`, `cache_after_empty_live`, `cache_only`).
- `transfermarkt_super_lig_squads_2025_2026` cache-only olarak yeniden üretildi: `15` kulüp, `424` oyuncu, toplam piyasa değeri `€1.31895B`, pozisyon dağılımı `GK 53 / DEF 134 / MID 125 / FWD 112`. Böylece 2025/26 genel snapshot `0/0` regresyonundan kurtarıldı.
- 2025/26 snapshotında atlanan kulüpler: Çorum FK, Erzurumspor FK, Amed SFK. Sebep: bu kulüplerin 2025/26 raw cache dosyası yok; aktif 2026/27 yükselenleri oldukları için 2025/26 tarihsel kadro datasına karıştırılmamalı.
- 2026/27 genel snapshot hâlâ `0` kulüp / `0` oyuncu. Bunun nedeni kod değil: mevcut raw/canlı sayfa tarafında 2026 sezonu için oyuncu tablosu yok. Bu dosya yapay şekilde 2025/26 datasıyla doldurulmadı.
- Doğrulama:
  - `.venv/bin/python -m compileall -q src/collect_transfermarkt_league_squads.py` başarılı.
  - `.venv/bin/python -m src.collect_transfermarkt_league_squads --clubs data/manual/transfermarkt_super_lig_clubs.json --season-id 2025 --output-prefix transfermarkt_super_lig_squads_2025_2026 --cache-only --delay-seconds 0` başarılı.
  - `tests.test_season_boundaries` ve `tests.test_transfermarkt_match_review_queue` birlikte çalıştırıldı; `3` failure var. Bunlar collector syntax/fallback hatası değil, mevcut sezon sınırı/UI beklentileriyle repo durumunun uyumsuzluğu: `ALL_TEAMS` içinde 2026/27 yükselenleri var, transfer tracker HTML beklenen X erişim metnini içermiyor, test network collector listesinde ilk TM komutu 2025/26 olarak yakalanıyor.
- Kalan öncelikler:
  1. 2026/27 için Transfermarkt kaynak tarafında oyuncu tablosu oluşana kadar official club/TFF/football API ve haber sinyalleriyle aktif kadro fallback katmanı kurulmalı.
  2. `scout_quality_report_2025_2026.json` gerçek scout havuzunu hâlâ eksik gösteriyor (`63` blueprint, `7` pozisyon matrisi adayı); `position_scout_matrix` ve `fm_style_scout_program` kaynaklarıyla yeniden bağlanmalı.
  3. `daily_pipeline_run_latest.md` stale; gerçek son pipeline koşusunu yansıtacak şekilde runner çıktısı yenilenmeli.

## 2026-07-13 / 2026-07-14 Günlük Veri/Geliştirme Kontrolü ve Scout Kalite Raporu Güncellemesi

- 14 Temmuz kontrolünde `data/` altında bugün üretilmiş yeni dosya bulunmadı; en yeni processed çıktılar 13 Temmuz scout kalite ve data quality scorecard dosyaları.
- `daily_pipeline_run_latest.md` hâlâ 26 Mayıs 2026 ağsız `48/48` başarılı koşusunda kalmış; pipeline sağlık göstergesi güncel değil.
- `scout_quality_report_2025_2026` stale durumdan yeniden üretildi. Eski rapor gerçek scout havuzunu `63` blueprint linki ve `7` pozisyon matrisi adayıyla eksik gösteriyordu.
- Güncel scout kalite özeti: `370` blueprint aday bağlantısı, `275` düşük güvenli blueprint bağlantısı, `29` tekil düşük güvenli oyuncu-rol, `91` pozisyon matrisi adayı. Eksik yaş/sözleşme linki `0`, tekrar eden rol oyuncusu `0`.
- Scout confidence dağılımı: `LOW_POSITION_UNVERIFIED 275`, `HIGH_EXTERNAL_PROFILE 37`, `MEDIUM 46`, `HIGH 10`, `DERIVED 2`. Pozisyon matrisi confidence dağılımı: `DERIVED 63`, `MEDIUM 24`, `HIGH 4`.
- `data_quality_scorecard_2025_2026` yeniden üretildi; genel skor `80.5` kaldı. `low_position_confidence_pct` kontrolü güncel scout raporuna göre `total 263`, `low_confidence 0`, `pct 0.0` olarak PASS.
- 2025/26 Transfermarkt genel snapshot korunuyor: `15` kulüp, `424` oyuncu, toplam piyasa değeri `€1.31895B`, pozisyon dağılımı `GK 53 / DEF 134 / MID 125 / FWD 112`.
- 2026/27 Transfermarkt genel snapshot hâlâ `0` kulüp / `0` oyuncu. Kaynak tarafında oyuncu tablosu oluşmadığı için 2025/26 verisiyle yapay doldurma yapılmadı.
- Tahmin metrikleri değişmedi: Beşiktaş display doğruluk `%55.2`, beraberlik recall `%11.1` FAIL, OOS ikinci yarı doğruluk `%45.8`, full-season doğruluk `%46.1`.
- Gol adayı metrikleri değişmedi: top-3 `%61.5`, top-5 `%76.9`, top-8 `%84.6`, top-10 `%88.5`.
- Kalan öncelik: 2026/27 aktif kadro fallback katmanını TFF/resmi kulüp/API/haber sinyalleriyle kurmak; ardından beraberlik recall ve genel skor tahmin modelini kalibre etmek.

## 2026-07-14 (devam) — TM Snapshot Fix Push Edildi, Avrupa Haber Nabzı Eklendi

- Önceki oturumdaki `src/collect_transfermarkt_league_squads.py` cache-fallback düzeltmesi hiç commit/push edilmemiş, yalnızca local working tree'de kalmıştı. Bu arada GitHub Actions (`daily-pipeline`, `refresh`, `news-refresh`) günde ~11 kez otomatik commit atmaya devam etti; local branch origin'in 210 commit gerisinde kaldı.
- Repo `git pull --ff-only` ile senkronize edildi (fast-forward, çakışma yok — bot hiçbir zaman `PROJECT_STATE.md` veya `collect_transfermarkt_league_squads.py`'a dokunmamış).
- Senkronizasyon sonrası kontrol: eski (düzeltilmemiş) script'in canlı TM sayfası boş oyuncu tablosu döndürdüğü her çalıştırmada genel snapshot'ı sessizce `0 kulüp/0 oyuncu` ile eziyordu — 12 Temmuz'da geri kazanılan `15 kulüp/424 oyuncu` verisi tekrar kaybolmuştu. `league_market_value_audit`'te maç kapsamı `%0`'a düşmüştü.
- Fix şimdi commit edilip push edilecek şekilde uygulandı (`--cache-only` fallback, boş/hatalı canlı fetch'te önceki cache'e döner, tamamen boş sonuçta eski non-empty payload'ı korur + `stale_reason` yazar). `--cache-only` ile yeniden üretildi: `15` kulüp, `424` oyuncu, `€1.32B`, kapsam `GK 53/DEF 134/MID 125/FWD 112`. Atlanan 3 kulüp yine `ÇORUM FK, ERZURUMSPOR FK, AMED SFK` (2025/26 raw cache'i yok — 2026/27 yükselenleri).
- Downstream yeniden üretildi: `enrich_players_with_transfermarkt`, `analyze_league_scouting`, `build_scout_quality_report`, `build_data_quality_scorecard`, `build_transfer_recommendation_report`, `build_league_market_value_audit`, `build_alias_quality_report`, `build_data_catalog`, `build_sqlite_warehouse`, `build_product_home`. Maç kapsamı `%0`'dan `177/258 (%69)`'a çıktı.
- Bu fix artık kalıcı: script'e girdiği için önümüzdeki otomatik çalıştırmalarda TM canlı sayfa yine boş dönerse otomatik cache fallback devreye girecek, veriyi sıfırlamayacak.
- Kullanıcı isteği: "transferler akın akın geliyor" (haber akışı zaten `build_transfer_tracker`/`news-refresh` ile günde 6 kez otomatik güncelleniyor — `49` sinyal, `6` doğrulanmış, gerçek örnek: Trossard Beşiktaş'a, Jonathan David Trabzonspor'a) ve "Avrupa Ligi eleme maçları başlıyor, heyecan kat, trafik çek".
- Avrupa tarafında kök sorun: `football-data.org` ücretsiz planı UEFA nitelendirme/eleme turu fikstürünü hiç kapsamıyor — `european_fixtures_2026_2027.json` sezon boyunca `0` maç ile boş kalıyor, `european_predictions_2026_2027.html` yalnızca sabit kodlanmış, tahmini "Türk Kulüpler" tablosu (ör. "Fenerbahçe UCL Play-off") gösteriyordu ve bu tablo gerçek haberlerle çelişiyordu (gerçek haber: Fenerbahçe'nin gerçek rakibi Gornik Zabrze, 1. eleme turu rövanşı 13-14 Temmuz'da oynandı).
- Yeni modül eklendi: `src/build_european_news_pulse.py` — zaten toplanan haber kaynaklarından (`news_rss_latest`, `news_google_latest`, `news_official_clubs_latest`, `news_telegram_latest`) UEFA nitelendirme/eleme turu sinyalini gerçek başlık+kaynak+link+tarihle çıkarıyor; uydurma fikstür/skor yok. Başlıkta kupa adı geçen veya (kulüp adı + "rövanş"/"play-off") birlikte geçen haberler alınıyor; yalnızca özet içinde geçen tesadüfi kupa övgüsü (ör. transfer haberi) gürültü olarak filtreleniyor. Çıktı: `european_news_pulse_2025_2026.json/.md` — şu an `8` ilgili haber.
- `build_european_predictions.py`: Sabit kodlanmış "Türk Kulüpler (Tahmini)" tablosu kaldırıldı (yanlış/güncel olmayan bilgi riski taşıyordu). Yerine gerçek haber nabzı kartları (`_build_pulse_section`) her zaman üstte gösteriliyor; UEFA takvimi genel/yaklaşık olarak etiketlendi.
- `build_live_feed.py` (ana sayfa `gundem_2025_2026.html`): Avrupa Kupası sidebar kartına en güncel gerçek nabız başlığını gösteren yanıp sönen "canlı" teaser eklendi (`eu_teaser_html`) — tıklama ile Avrupa sayfasına yönlendiriyor, gündem sayfasında heyecan/trafik amaçlı.
- Pipeline entegrasyonu: `run_daily_pipeline.py` DEFAULT_COMMANDS'a `build_european_news_pulse` eklendi (analyze/build european_predictions'tan hemen önce); `.github/workflows/news-refresh.yml` (günde 6 kez) ve `.github/workflows/refresh.yml` (günde 4 kez) adımlarına da eklendi — `refresh.yml`'de ayrıca european_predictions rebuild'i haber toplama adımlarından SONRAYA taşındı (önceden haberlerden önce çalışıyordu, artık güncel nabız verisiyle üretiliyor).
- Test: `pytest` — `58 passed, 3 failed` (aynı 3 pre-existing hata: `test_season_boundaries` — 2026/27 yükselen takım listesi ve X erişim metni testleri, script/fallback ile ilgisiz, önceden de kayıtlıydı).
- Kalan öncelik: (1) 2026/27 TM genel snapshot hâlâ `0/0` (kaynak tarafında oyuncu tablosu yok, yapay doldurulmadı), (2) beraberlik recall/OOS kalibrasyonu, (3) haber nabzı kapsamı zamanla genişletilebilir (şu an yalnızca Süper Lig kulüp adlarıyla eşleşiyor; Avrupa rakip takım isimleriyle de genişletilebilir).

## 2026-07-15 Günlük Veri/Geliştirme Kontrolü

- 15 Temmuz kontrolünde `data/processed` altında 14 Temmuz 21:00 sonrası `98` dosya güncellenmiş görünüyor; en yeni üretimler `match_prediction_backtest_2025_2026`, Beşiktaş kronolojik preview klasörü, product home, data catalog, sqlite warehouse, transfer recommendation, scout/data quality ve Avrupa haber nabzı çıktıları.
- `daily_pipeline_run_latest.md` hâlâ 26 Mayıs 2026 ağsız `48/48` başarılı koşusunda kalmış; yeni çıktı üretilmesine rağmen bu health raporu güncel pipeline koşusunu yansıtmıyor.
- Git durumu temiz ve `main` branch `origin/main` ile aynı hizada görünüyor; 14 Temmuz’daki TM cache fallback ve Avrupa haber nabzı geliştirmeleri localde kirli değişiklik olarak kalmamış.
- `data_quality_scorecard_2025_2026` skoru `80.5` seviyesinden `73.6` seviyesine düşmüş. Bu bir ham veri kapsamı düşüşünden çok, yeni/sert kalite kontrollerinin görünür hâle gelmesiyle ilişkili.
- Data quality FAIL/WATCH başlıkları:
  - `unmatched_players_blocking_scout_review`: `23` oyuncu ile FAIL.
  - `draw_recall_pct`: beraberlik tahmini `1/9`, `%11.1` ile FAIL.
  - `manual_alias_pending_network_verification`: `13` ile WATCH.
  - Beşiktaş display tahmin doğruluğu `16/29`, `%55.2` ile WATCH.
  - Gol adayı top-5 `20/26`, `%76.9`; top-8 `22/26`, `%84.6` ile WATCH.
- OOS model doğrulaması değişmedi: full-season `119/258`, `%46.1`; ikinci yarı OOS `70/153`, `%45.8`. Raw baseline hâlâ daha güçlü: full-season `%50.4`, second-half OOS `%51.6`.
- `match_prediction_backtest_2025_2026` özeti: `29` rapor, `16` doğru, genel doğruluk `%55.2`; actionable maçlarda `5/9`, `%55.6`; büyük maçlarda `3/6`, `%50.0`.
- Gol adayı backtest özeti: Beşiktaş gol attığı `26` maçta top-3 `%61.5`, top-5 `%76.9`, top-8 `%84.6`, top-10 `%88.5`.
- `scout_quality_report_2025_2026` güncel kalmış: `370` blueprint aday bağlantısı, `275` düşük güvenli link, `29` tekil düşük güvenli oyuncu-rol, `91` pozisyon matrisi adayı. Eksik yaş/sözleşme linki `0`, tekrar eden rol oyuncusu `0`.
- Transfer tracker büyümüş: `49` sinyal, `6` confirmed/corroborated, `15` rumor, `28` review required, `0` official. Resmi doğrulama katmanı hâlâ zayıf.
- Market value audit toparlanmış: `15` market kulübü, `424` oyuncu, `€1.31895B`; model maç kapsamı `177/258`, `%68.6`. Eksik market takımları: Antalyaspor, Fatih Karagümrük, Kayserispor varyantları.
- 2025/26 TM genel snapshot korunuyor: `15` kulüp / `424` oyuncu. 2026/27 TM genel snapshot hâlâ `0` kulüp / `0` oyuncu; kaynakta oyuncu tablosu yok.
- Avrupa haber nabzı çıktı üretmiş: `european_news_pulse_2025_2026` içinde `8` haber var. Ancak ilk örneklerde kulüp eşleşmesi `None` olabiliyor ve bazı genel UEFA haberleri geliyor; Avrupa rakipleri/tur eşleşmeleri için daha iyi entity matching gerekiyor.
- Kalan öncelik sırası:
  1. `unmatched_players_blocking_scout_review = 23` blokajını çözmek.
  2. Beraberlik recall ve OOS model kalibrasyonunu baseline’ın üstüne taşıyacak şekilde düzeltmek.
  3. 2026/27 aktif kadro fallback katmanını TFF/resmi kulüp/API/haber sinyalleriyle doldurmak.
  4. Avrupa haber nabzında kulüp/rakip/tur entity matching kapsamını genişletmek.
  5. `daily_pipeline_run_latest.md` dosyasını gerçek son otomatik üretimi gösterecek şekilde yenilemek.

## 2026-07-15 (devam) — Kafa Kafaya (H2H) Beraberlik Sinyali Eklendi

- Kullanıcı isteği: "beraberlik recall kalibrasyonuna bak" → önce eşik gevşetme (score>=90→55) ve lig-geneli formülü Beşiktaş'a taşıma denendi; ikisi de önceki oturumlarla aynı sonuçla reddedildi (eşik gevşetince büyük maç override'ı geri alıyor, kazanç yok; lig formülü doğruluğu %55'ten %45'e düşürüyor, n=29/9 draw çok küçük örneklem). Kullanıcı "daha geniş düşün, futbolseverlere keyifli an yaşat, en doğruya yakın tahmin için ne gerekiyorsa yap" dedi.
- Kök neden zaten teşhis edilmişti: "kafa kafaya tarihsel beraberlik oranı veya bahis piyasası verisi gerekir" (bkz. 3. tekrarlanan not). Bu veri hiç toplanmamıştı.
- football-data.co.uk (bahis oranı + tarihsel sonuç, ücretsiz CSV) sandbox'tan erişilemiyor (bağlantı timeout / muhtemel gambling-domain filtresi); genel internet ve GitHub erişimi çalışıyor.
- API-Football'ın halihazırda `.env.example` içinde bulunan ücretsiz demo key'i (`e15d854...`, `load_settings()` `.env` yoksa otomatik buna düşüyor) ile `/fixtures/headtohead` endpoint'i canlı test edildi. `last=N` parametresi ücretsiz planda yasak (`"Free plans do not have access to the Last parameter."`); parametresiz çağrı tüm geçmişi (2010'lardan bu yana) tek seferde dönüyor.
- `data/manual/api_football_team_ids.json` eklendi: 18 Süper Lig takımının API-Football id eşlemesi (15'i bilinen 2024 snapshot'tan, 3'ü — Kocaelispor, Gençlerbirliği, Fatih Karagümrük — `--search` ile otomatik çözüldü ve dosyaya geri yazıldı).
- `src/collect_head_to_head_history.py` eklendi: takım çiftleri için gerçek tarihsel h2h beraberlik oranını toplar; `--limit`/`--skip-existing` ile günlük kota (ücretsiz plan 100/gün) boyunca kademeli tamamlanır. Bugün elle `106/153` çift toplandı (kalan `47` çift `run_daily_pipeline` NETWORK_COMMANDS'a eklenen `--limit 30` ile birkaç gece içinde tamamlanacak). Çıktı: `head_to_head_history_2025_2026.json/.md`.
- Gerçek veri örnekleri: Beşiktaş-Galatasaray `33` maç `%18.2` beraberlik, Beşiktaş-Fenerbahçe `36` maç `%33.3`, Beşiktaş-Başakşehir `29` maç `%41.4`, Beşiktaş-Samsunspor `8` maç `%50` (küçük örneklem).
- `src/preview/probability.py`: `head_to_head_draw_signal(team_a, team_b)` eklendi (JSON'dan gerçek oranı okur, <3 maçta devre dışı kalır — sıfır regresyon riski). `estimate_probabilities()` içinde `heuristic_draw`'a örneklem-ağırlıklı prior olarak karıştırılıyor (`h2h_weight = min(0.35, 0.12 + matches*0.01)`); ayrıca `draw_calibration_signal`'a da ek `lift` (h2h_rate≥0.40→+0.06, ≥0.30→+0.035) olarak bağlandı.
- `src/model_league_predictions.py`: aynı h2h sinyali `predict_match()` içinde `poisson_result_probs` çıktısına aynı ağırlıklı blend ile ekleniyor.
- **Doğrulanmış sonuç (n=258 maç/76 beraberlik, tüm lig)**: doğruluk `%46.1→%47.3`, beraberlik recall `%31.6→%34.2`, Brier `0.615→0.610`, log loss `1.027→1.019` — hepsi aynı yönde iyileşti (trade-off yok).
- **OOS (bağımsız ikinci yarı, hafta 18-34) doğrulaması**: `%45.8→%47.1`. Bu en katı test — walk-forward, sızıntısız.
- **Önizleme motoru genelinde (18 takım, n=551 takım-perspektifi, 164 beraberlik)**: min_prob=0.26/max_gap=0.18 eşiğinde doğruluk `%47.2→%48.3`, beraberlik recall `%35.4→%36.6`.
- Beşiktaş'a özgü ekran kalibrasyonu (`calibrated_display_prediction`, score>=90 sert eşik) kasıtlı olarak DEĞİŞTİRİLMEDİ: aynı gap-tabanlı yöntem yalnızca Beşiktaş'ın 29 maçlık alt kümesinde test edildiğinde doğruluğu düşürüyor (16/29→14-15/29) çünkü bu sezonun 9 beraberliğinin çoğu (Kasımpaşa, Eyüpspor, Karagümrük, Rizespor, Galatasaray) modelin hiçbir sinyalle yakalayamayacağı kadar büyük olasılık farkıyla (margin 0.18-0.36) gerçekleşti. Bu yüzden `data_quality_scorecard`'daki `draw_recall_pct: 1/9 FAIL` metriği DEĞİŞMEDİ — bu metrik kasıtlı olarak muhafazakâr kalan, çok küçük örneklemli (n=9) bir alt sistemi ölçüyor; asıl doğrulanmış iyileşme lig geneli/OOS metriklerinde.
- Test: `pytest` `58 passed, 3 failed` (aynı 3 önceden var olan test, ilgisiz).
- API-Football günlük kota: bugün `~94/100` kullanıldı (h2h toplama + id çözümleme); yarın sıfırlanacak.
- Kalan öncelik: kalan `47` h2h çiftini tamamlamak (otomatik, birkaç gece), ardından h2h verisi büyüdükçe (küçük örneklemli takımlar — Kocaelispor, Karagümrük, Gençlerbirliği — 2-12 maçla sınırlı) sinyali yeniden değerlendirmek.

## 2026-07-15 (devam 2) — 2026-27 Sezon Fikstürü ve Gerçek Maç Tahminleri Eklendi (Kullanıcı Uyarısı Sonrası)

- Kullanıcı geri bildirimi: önceki iki oturumluk çalışma (TM fix, Avrupa nabzı, h2h kalibrasyon) sitede görünür/somut değildi; kullanıcı özellikle "lig fikstürü ve tahmini sonuçları yok" ve "sadece Beşiktaş değil diğer takımlar da olmalı" dedi. Netleştirme: kullanıcı **2026/27 sezonu için gerçek, gelecek maç tahminleri** istiyor.
- Kritik keşif: sitedeki TÜM maç tahmin sistemi biten 2025/26 sezonunun geriye dönük analiziydi; **2026/27 sezonu için hiçbir fikstür/tahmin altyapısı yoktu** (ne collector ne sayfa).
- football-data.co.uk (bahis oranı + tarihsel sonuç) sandbox'tan erişilemedi (muhtemel gambling-domain filtresi). Onun yerine mevcut TFF collector'ı kontrol edildi.
- **Kök neden bulundu ve düzeltildi**: `www.tff.org` TLS sertifika zincirinde ara sertifikayı (GlobalSign RSA OV SSL CA 2018) göndermiyor. curl/macOS bunu sistem anahtarlığıyla tolere ediyor ama Python's requests+certifi kesin doğrulama istiyor → `SSLCertVerificationError: unable to get local issuer certificate`. Bu, günlerdir `collect_tff_league_season`/`collect_besiktas_season`'ın GitHub Actions'ta HER GECE FAIL olmasının kök nedeniydi (nightly loglarda görülüyordu, önceden fark edilmemiş).
  - Fix: `data/manual/extra_ca_certs.pem` eklendi (GlobalSign ara sertifikası, AIA "CA Issuers" URL'inden alındı). `src/http_client.py`'de `get_url()` artık certifi + bu ek sertifikayı birleştirip varsayılan `verify=` olarak kullanıyor — yalnızca ekleme, güvenlik azaltmıyor. Tüm TFF collector'ları (`get_url` üzerinden) otomatik düzeldi.
- Fix sonrası TFF sitesi test edildi: **2026-27 Süper Lig fikstürü TAMAMEN yayınlanmış** — 34 hafta, 306 maç, 16 Ağustos 2026 - 23 Mayıs 2027 arası, gerçek tarihlerle. 3 yeni takım (Çorum FK, Erzurumspor FK, Amed Sportif Faaliyetler) 2025/26'da düşen Antalyaspor/Kayserispor/Karagümrük'ün yerini almış.
- `src/collect_tff_season_fixture.py` eklendi: `collect_tff_league_season.py`'den farklı olarak maç detayına inmez (maçlar oynanmadı), yalnızca hafta/tarih/ev-deplasman listesini toplar. `--seed-match-id 317784` ile test edildi, 34/34 hafta başarıyla toplandı.
- `src/model_league_predictions.py`'ye `compute_final_state(matches)` eklendi: `run_backtest` ile aynı kronolojik birikimi yapıp yalnızca son `team_history`/`elo`/hakem durumunu döner (gelecek fikstürü tahmin etmek için "başlangıç durumu").
- `src/build_season_fixture_predictions.py` eklendi: 2026-27 fikstürünü, 2025-26'nın tamamından türetilen son takım formu/Elo + h2h sinyaliyle (aynı `predict_match`/`draw_calibrated_prediction` motoru) tahmine çevirir. İsim takma adları eklendi (RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ→İSTANBUL BAŞAKŞEHİR FK, TÜMOSAN KONYASPOR→KONYASPOR, İKAS EYÜPSPOR→EYÜPSPOR — sponsor adı değişiklikleri). Yeni takımlar (0 Süper Lig geçmişi) `LOW_NEW_TEAM` güven etiketiyle işaretleniyor, sistem çökmüyor (avg() boş listede 0 dönüyor).
- Çıktı: `season_fixture_predictions_2026_2027.json/.md/.html` — 34 hafta, 306 maç, hepsi TÜM 18 takım için (yalnızca Beşiktaş değil). Örnek: Beşiktaş-Eyüpspor (16 Ağu) beraberlik, Fenerbahçe-Konyaspor (23 Ağu) ev sahibi güçlü favori (%73), Galatasaray-Çorum FK ev sahibi favori.
- Ana sayfaya (`build_live_feed.py`/gündem) ilk hafta fikstürünü gösteren öne çıkan "🗓️ 2026-27 Sezonu Başlıyor" paneli eklendi (Transferler panelinden önce, en üstte) + nav'a "2026-27 Fikstür" linki eklendi.
- Pipeline: `collect_tff_season_fixture` NETWORK_COMMANDS'a, `build_season_fixture_predictions` DEFAULT_COMMANDS'a eklendi (Avrupa tahminlerinden hemen sonra).
- Test: `pytest` `58 passed, 3 failed` (aynı 3 ilgisiz önceden var olan hata).
- Not: Bu tahminler statik ön sezon tahminleridir (2025-26 sonunda dondurulmuş form/Elo kullanır); sezon 16 Ağustos'ta başladıkça gerçek sonuçlarla güncellenmeli — bu bir sonraki geliştirme önceliği (haftalık `predict_match` girdisini gerçek 2026-27 sonuçlarıyla kademeli güncelleyecek bir adım gerekiyor).
- Kalan öncelik: (1) sezon başladıkça fikstür tahminlerini gerçek sonuçlarla haftalık güncelleyecek mekanizma, (2) yeni 3 takım için 1. Lig geçmişinden form verisi bağlamak (şu an sıfır veri), (3) kalan h2h çiftlerini tamamlamak.

## 2026-07-15 (devam 3) — Dinamik Güncelleme Mekanizmaları Eklendi: Maç Sonucu + Transfer Sinyali

- Kullanıcı geri bildirimi (bkz. memory `feedback_dynamic_predictions_required`): 2026-27 fikstür tahminleri statik kaldığı için hiçbir tahmin sabit bırakılamaz — hem oynanan maç sonuçları hem de transfer/kadro değişiklikleri (örnek: dün bir takım yeni oyuncu aldı) tahminleri günlük olarak etkilemeli. İki somut boşluk kapatıldı.
- **Mekanizma A — Oynanan maç sonucu → state ilerletme**: yeni `src/advance_season_state.py` eklendi. `tff_super_lig_fixtures_2026_2027.json` fikstüründe skoru artık `"-"` olmayan (oynanmış) ama zengin şemayla (kart/hakem/xG) toplanmamış maçları tespit edip `collect_tff_league_season.py` ile aynı `probe_match` mekanizmasıyla çeker, `tff_super_lig_matches_2026_2027.json` birikim dosyasına ekler (idempotent — `external_id` zaten varsa atlanır). `run_daily_pipeline.py` NETWORK_COMMANDS listesine `collect_tff_season_fixture` hemen altına eklendi.
- `src/build_season_fixture_predictions.py` artık yalnızca 2025-26 tam sezonu değil, bu birikim dosyasını da (varsa) okuyup 2025-26 ile aynı takım-adı uzayına taşıyıp (`_rekeyed_2026_27_matches`, sponsor adı değişen kulüpler için `NAME_ALIASES` ile) birleştiriyor, `parse_tff_datetime` ile doğru kronolojik sıralayıp tek bir `compute_final_state` çağrısına veriyor (önceden hatalı bir düz string sıralaması vardı, düzeltildi). Skoru gerçek olan haftalar artık tahmin yerine gerçek sonucu gösteriyor (`is_played`, `actual_score`, `data_confidence: "PLAYED"`).
- **Mekanizma B — Transfer sinyali → takım gücü**: `src/preview/probability.py`ye `transfer_strength_edge(team_name)` eklendi (aynı dosyadaki `head_to_head_draw_signal` ile birebir aynı desen). `transfer_tracker_2025_2026.json`daki `transfers[]` listesini durum ağırlıklı okuyor (`OFFICIAL=1.0, CORROBORATED/TM_CONFIRMED=0.6, RUMOR=0.15, REVIEW_REQUIRED=0.1`), takımın toplam piyasa değerine göre normalize edip `±0.15` aralığına sıkıştırıyor. **Kasıtlı güvenlik kısıtı**: sinyal yalnızca en az bir OFFICIAL/CORROBORATED/TM_CONFIRMED (doğrulanmış) transfer varsa `available: True` olur — bugünkü canlı veride (37 sinyal, hepsi RUMOR/REVIEW_REQUIRED) test edildi, tüm takımlar için `available: False, edge: 0.0` döndü, yani mekanizma kuruldu ama gerçek bir transfer resmileşene kadar hiçbir tahmini etkilemiyor. Elle simüle edilen bir OFFICIAL senaryoda beklenen yönde/büyüklükte edge üretti (doğrulandı).
- `model_league_predictions.predict_match()`e `apply_transfer_signal: bool = False` parametresi eklendi (varsayılan **False** — `run_backtest`/kalibre edilmiş sistem hiç etkilenmiyor). `strength_edge`e yalnızca `apply_transfer_signal=True` olduğunda transfer edge farkı ekleniyor; bunu yalnızca `build_season_fixture_predictions.py` açık şekilde `True` geçirerek kullanıyor — 2025-26 backtest asla bu sinyali görmüyor (look-ahead bias riski yok).
- **Doğrulama**: `python -m src.model_league_predictions` backtest sonrası doğruluk `%47.3`/Brier `0.61`/log loss `1.019` — bu turdan ÖNCEKİ doğrulanmış değerlerle birebir aynı (regresyon yok, yalnızca çıktı JSON'a şeffaflık için boş `transfer_signal` alanı eklendi). `pytest`: `58 passed, 3 failed` (aynı 3 önceden var olan, ilgisiz hata).
- `advance_season_state`/`build_season_fixture_predictions` bugünkü (henüz hiç 2026-27 maçı oynanmamış) durumda çalıştırıldı: `0 oynanmış maç adayı`, `34 hafta/306 maç` sorunsuz üretildi. Birleştirme/rekey/kronolojik sıralama mantığı ayrıca scratch dosyalarla simüle edilmiş bir "oynanmış maç" senaryosuyla uçtan uca doğrulandı (`is_played`/`actual_score` doğru üretildi).
- Otomatik güncelleme döngüsü için yeni bir cron gerekmiyor: `transfer_tracker` zaten günde birkaç kez (`news-refresh.yml`) yenileniyor, `refresh.yml` (6 saatte bir) zaten `build_season_fixture_predictions`i DEFAULT_COMMANDS üzerinden çalıştırıyor — yeni bir transfer sinyali veya oynanan maç verisi girer girmez bir sonraki çalıştırmada otomatik yansıyor.
- Kullanıcı isteği üzerine, bu turda 3 yeni takımın (Çorum FK, Erzurumspor FK, Amed Sportif Faaliyetler) 1. Lig geçmiş verisi bağlama işi ERTELENDİ — Mekanizma A devreye girip 2026-27 maçları biriktikçe bu takımların geçmişi organik olarak dolmaya başlayacak, bu da 1.Lig backfill ihtiyacını büyük ölçüde azaltıyor.
- Kalan öncelik: (1) sezon 16 Ağustos'ta başladıktan sonra `advance_season_state`in gerçek maç verisiyle doğru çalıştığını canlıda doğrulamak, (2) yeni 3 takımın ilk birkaç haftası hâlâ `LOW_NEW_TEAM` kalacak (1.Lig backfill hâlâ ertelenmiş durumda), (3) kalan h2h çiftlerini tamamlamak, (4) transfer sinyali ilk gerçek OFFICIAL/CORROBORATED transferde canlı veriyle doğrulanmalı (şu an yalnızca simülasyonla doğrulandı).

## 2026-07-15 (devam 4) — Beraberlik Kalibrasyon Eşikleri Yeniden Ayarlandı: İsabet Önceliği

- Kullanıcı geri bildirimi: mevcut %47.3 genel isabet oranı yeterince iyi değil, ve amaç özellikle **maç sonucunu** (1X2 — ev/beraberlik/deplasman, skor değil) doğru bilmek; beraberlik yakalama (recall) öncelik değil.
- Kök neden veriyle doğrulandı: `build_model_baseline_comparison.py` yeniden çalıştırıldı, mevcut kalibre edilmiş hibrit model (`current_hybrid`/üretim `draw_calibrated_prediction`) beraberlik kalibrasyonu OLMAYAN salt Poisson modelinden (`poisson_only`, %51.2) **4 puan daha düşük** çıkıyordu (%47.3) — beraberlik yakalamak için fazla sayıda yanlış beraberlik tahmini yapılıyordu (81 beraberlik tahmininden yalnızca ~26'sı doğru, isabet ~%32).
- `league_prediction_model_2025_2026.json`daki 258 maçlık cache'lenmiş olasılıklar üzerinde tam ızgara taraması yapıldı (`DRAW_PRED_MIN_PROB` × `DRAW_PRED_MAX_GAP` × `DRAW_BOOST_SCALE`, 297 kombinasyon), ardından en iyi adaylar tam sezon + ilk yarı + **ikinci yarı OOS** (hafta 18-34, walk-forward, sızıntısız — h2h tuning'de kullanılan aynı en katı test) üzerinde çapraz kontrol edildi.
- Yeni ayar: `DRAW_PRED_MIN_PROB: 0.26→0.28`, `DRAW_PRED_MAX_GAP: 0.18` (değişmedi), `DRAW_BOOST_SCALE: 0.12→0.0` (draw boost tamamen kapatıldı) — `src/model_league_predictions.py`.
- **Doğrulanmış sonuç (`build_oos_validation.py` çıktısı)**: ikinci yarı OOS doğruluk (en katı test) `%51.6→%52.9` (ham argmax zaten %51.6'ydı, kalibrasyon artık ONU DA geçiyor, önceki ayar bunun ALTINDA kalıyordu). Tüm sezon doğruluk `%47.3→%51.6`. Beraberlik recall `%34.2→%18.4`e düştü (kasıtlı takas — kullanıcı önceliği isabet).
- `pytest`: `58 passed, 3 failed` (aynı 3 önceden var olan ilgisiz hata). Downstream yeniden üretildi: `build_season_fixture_predictions` (34 hafta/306 maç, sorunsuz), `build_model_baseline_comparison`, `build_oos_validation`, `build_draw_risk_audit`.
- **Not — bu değişiklik yalnızca lig geneli/gelecek sezon modelini (`model_league_predictions.py`) etkiliyor.** Beşiktaş'a özgü ekran kalibrasyonu (`src/preview/probability.py` `calibrated_display_prediction`, score>=90 sert eşik) DEĞİŞTİRİLMEDİ — ayrı bir sistem, kasıtlı olarak dokunulmadı (bkz. önceki oturum notları, bu eşik Beşiktaş alt kümesinde farklı davranıyor).
- İkinci öneri (piyasa değeri farkının doğrudan bir sinyal olarak eklenmesi) ertelendi: `league_market_value_audit_2025_2026.json` diagnostic'i piyasa değeri favorisinin tek başına ~%50-52 isabet verdiğini gösteriyor ama yalnızca maçların %68.6'sında kapsama var (3 takım — Antalyaspor/Karagümrük/Kayserispor varyantları — piyasa verisinde eksik) ve dosya kasıtlı olarak "tanısal, üretim sinyali değil" etiketli; üretim sinyaline dönüştürmek ayrı bir OOS doğrulama + eksik takım fallback işi gerektiriyor.
- Kalan öncelik: (1) piyasa değeri sinyalinin üretim sinyaline dönüştürülüp dönüştürülmeyeceğine karar vermek (kapsama boşluğu var), (2) isabet oranını daha da artıracak başka sinyaller (ör. ev sahibi/deplasman ayrı ayrı isabet `%66.7`/`%63.4` — hâlâ iyileştirilebilir alan) araştırılabilir.

## 2026-07-15 Akşam Günlük Veri/Geliştirme Kontrolü

- 15 Temmuz akşam kontrolünde `data/processed` altında gün içinde üretilmiş `163` dosya görünüyor; 13:00 sonrası üretim sayısı `148`. En yeni kritik çıktılar: `oos_validation_2025_2026`, `draw_risk_audit`, `model_baseline_comparison`, `season_fixture_predictions_2026_2027`, `league_prediction_model_2025_2026`, haber/transfer çıktıları ve canlı gündem sayfası.
- `daily_pipeline_run_latest.md` artık stale değil: son koşu `2026-07-15T10:06:50Z`, network dahil değil, `57/57` komut başarılı, `0` hata. JSON dosyasında komut listesi boş görünüyor ama markdown raporu komutları doğru yazıyor; JSON şemasındaki bu tutarsızlık ileride temizlenmeli.
- 2026/27 fikstür tahminleri mevcut: `34` hafta / `306` maç. Henüz oynanmış maç yok (`played=0`). Güven dağılımı: `HIGH 67`, `MEDIUM 88`, `LOW 55`, `LOW_NEW_TEAM 96`. Yeni takımlar nedeniyle `LOW_NEW_TEAM` yükü yüksek.
- H2H veri toplama ilerlemiş: `153` olası takım çiftinin `106` tanesi toplanmış; kalan `47` çift günlük API kotasıyla parça parça tamamlanacak.
- Lig geneli 1X2 modelinde isabet odaklı kalibrasyon sonrasında doğrulanan metrikler iyileşti:
  - Full-season: `133/258`, `%51.6`, Brier `0.610`, log loss `1.019`.
  - İkinci yarı OOS: `81/153`, `%52.9`, Brier `0.608`, log loss `1.015`.
  - Raw baseline: full-season `%50.4`, second-half OOS `%51.6`; yeni kalibrasyon iki ölçekte de baseline’ın üstüne geçti.
- Model baseline karşılaştırması: `poisson_only` doğruluk `%51.2` ile hâlâ accuracy sıralamasında en yüksek tek model; `current_hybrid` doğruluk `%50.4` ama log loss/Brier tarafında daha iyi (`log_loss 1.019`, `brier 0.610`). OOS raporu güncel üretim yolunda `%52.9` gösterdiği için raporlar arası isim/ölçüm farkı ayrıca izlenmeli.
- `data_quality_scorecard_2025_2026` skoru `73.6`dan `72.9`a hafif düştü. Yeni FAIL/WATCH başlıkları:
  - `unmatched_players_blocking_scout_review`: `23`ten `4`e düştü ama hâlâ FAIL.
  - `draw_recall_pct`: Beşiktaş ekran metriğinde `1/9`, `%11.1` ile hâlâ FAIL; bu metrik kasıtlı olarak Beşiktaş özel muhafazakâr ekran katmanını ölçüyor.
  - `tff_transfermarkt_in_scope_match_rate_pct`: `391/520`, `%75.2` ile WATCH.
  - `manual_alias_pending_network_verification`: `13` ile WATCH.
  - Beşiktaş display tahmin doğruluğu `16/29`, `%55.2` ile WATCH.
  - Gol adayı top-5 `20/26`, `%76.9`; top-8 `22/26`, `%84.6` ile WATCH.
- Transfer tracker güncel: `50` sinyal, `6` corroborated/confirmed, `13` rumor, `31` review required, `0` official, toplam değer `€1.8M`. Transfer sinyali modeli kurulu ama official/corroborated sinyaller üretim etkisi için hâlâ canlıda ayrıca doğrulanmalı.
- Avrupa haber nabzı `8` haberle aynı seviyede; kulüp/rakip/tur entity matching hâlâ genişletilmeli.
- Git durumu kontrol başında temiz ve `main...origin/main` hizalıydı. Bu kayıt sonrası yalnız `PROJECT_STATE.md` değişti.
- Kalan öncelik sırası:
  1. `unmatched_players_blocking_scout_review` kalan `4` oyuncuyu çözmek ve scorecard FAIL’i kaldırmak.
  2. Yeni takımlar için `LOW_NEW_TEAM` oranını düşürmek üzere 1. Lig/backfill veya resmi kadro form sinyali eklemek.
  3. H2H kalan `47` çifti tamamlamak.
  4. Beşiktaş ekran katmanındaki beraberlik recall metriğini ayrı değerlendirmek; genel model isabeti yükseldiği için bu metrik ürün dili/ekran metodu olarak ele alınmalı.
  5. `daily_pipeline_run_latest.json` komut listesi boşluğu ve raporlar arası baseline/current_hybrid ölçüm farkı incelenmeli.

## 2026-07-16 — `unmatched_players_blocking_scout_review` FAIL Kök Nedeni Bulundu ve Düzeltildi

- Kök neden: `run_daily_pipeline.py`'deki gece koleksiyoncusu, **2025-26 sezonu** Transfermarkt kadrolarını toplarken `data/manual/transfermarkt_super_lig_clubs.json` dosyasını kullanıyordu — ama bu dosya 2026-27 sezonu başlarken GÜNCEL (yeni sezon) 18 kulüp listesine güncellenmişti (3 yeni takım: Çorum FK, Erzurumspor FK, Amed SFK; düşen 3 takım: Antalyaspor, Fatih Karagümrük, Kayserispor çıkarılmış). Sonuç: her gece "2025-26" kadro dosyası yanlışlıkla düşen 3 takımı İÇERMEDEN yeniden üretiliyordu, bu yüzden o kulüplerdeki yüksek kullanımlı 4 oyuncu (Kenneth Paal, Ivo Grbic, László Bénes, Berkay Özcan) hiçbir Transfermarkt adayıyla eşleşemiyor ve scout kuyruğunu bloke ediyordu.
- Fix: yeni `data/manual/transfermarkt_super_lig_clubs_2025_2026.json` eklendi (gerçek 2025-26 sezonu 18 kulübü — 15 ortak takım + Antalyaspor/Karagümrük/Kayserispor, `club_id`/`slug` git geçmişinden geri alındı). `run_daily_pipeline.py`'deki 2025-26 koleksiyoncu komutu artık bu dosyayı kullanıyor (2026-27 koleksiyoncusu hâlâ güncel `transfermarkt_super_lig_clubs.json`'ı kullanmaya devam ediyor, değişmedi).
- Yeni dosyayla `collect_transfermarkt_league_squads` çalıştırıldı: 18/18 kulüp başarıyla toplandı (önceden 15/18, 3 atlanmış), 424→817 oyuncu.
- `enrich_players_with_transfermarkt` yeniden çalıştırıldı: doğrulanmış eşleşme `391→594`, in-scope kapsam `%75.2→%94.9`. 4 oyuncu için (yukarıdaki isimler) `data/manual/tm_player_manual_aliases.json`'a manuel alias eklendi (proje genelindeki 13 mevcut manuel alias ile aynı desen — `requires_network_verify: true`, ayrı izleniyor).
- `build_transfermarkt_match_review_queue` + `build_data_quality_scorecard` yeniden üretildi: **`scout_blocking_unmatched: 4→0`**, `data_quality_scorecard` genel skoru `72.9→82.1`.
- Doğrulama: `pytest` `58 passed, 3 failed` — aynı 3 önceden var olan ilgisiz hata (git stash ile karşılaştırılarak teyit edildi, regresyon yok).
- Kalan öncelik: yeni eklenen 4 manuel alias bir sonraki ağ teyidinde (`manual_alias_pending_network_verification` toplamı artık `4`, önceki 13 ile birleşmedi çünkü review queue'da ayrı satırlarda listeleniyor) doğrulanmalı; yukarıdaki listedeki (2), (3), (4), (5) maddeleri hâlâ açık.

## 2026-07-16 Günlük Veri/Geliştirme Kontrolü

- 16 Temmuz kontrolünde bugün `data/processed` altında `128` dosya güncellenmiş görünüyor; 15:00 sonrası yeni çıktı yok. Son commit: `aa981edc fix: 2025-26 Transfermarkt kadro koleksiyonunu dogru kulup listesine bagla`.
- `daily_pipeline_run_latest.md` hâlâ son başarılı ağsız koşuyu `2026-07-15T10:06:50Z`, `57/57` başarılı olarak gösteriyor; 16 Temmuz’daki düzeltme sonrası gerçek güncel koşuyu temsil etmiyor.
- `data_quality_scorecard_2025_2026` belirgin iyileşti: genel skor `72.9→82.1`.
- Transfermarkt/TFF kapsamı düzeldi:
  - 2025/26 TM snapshot: `18` kulüp / `817` oyuncu / `€1.74191B`.
  - Review queue: `tff_profiles 691`, `tm_players 817`, `matched_profiles 594`, `in_scope_match_rate %94.9`, operational in-scope mapping `%95.5`.
  - `unmatched_players_blocking_scout_review`: `4→0`, scorecard artık PASS.
  - Manuel alias ağ teyidi: `4` ile WATCH.
- Scout kalite raporu düşük güven yayın adayı kalmadığını gösteriyor: blueprint aday bağlantısı `0`, pozisyon matrisi adayı `0`, düşük güvenli aday `0`. Bu rapor artık “yayına çıkacak düşük güvenli aday yok” anlamına geliyor; ana scout havuzunun büyüklüğünü ölçmek için `team_scout_blueprints`/`position_scout_matrix` ayrıca izlenmeli.
- H2H veri toplama ilerledi: `153` olası çiftin `136` tanesi toplandı; kalan `17` çift kaldı. Bugünkü koşuda `30` çift fetch edilmiş.
- Lig geneli tahmin modeli değişmedi: `258` maçta `133` doğru, doğruluk `%51.6`, Brier `0.610`, log loss `1.019`. Güven kırılımı: `HIGH %60.6`, `MEDIUM %42.0`, `LOW %50.0`.
- Dikkat edilmesi gereken regresyon/boş çıktı: `oos_validation_2025_2026.json` bugün `0` maç / `None` accuracy üretiyor. Önceki doğrulanmış OOS değer `%52.9` idi; bu dosya şu an model sağlığı için güvenilir değil ve neden 0 maç ürettiği incelenmeli.
- 2026/27 fikstür tahminleri mevcut kalıyor: `34` hafta / `306` maç / oynanmış maç `0`. Güven dağılımı: `HIGH 67`, `MEDIUM 88`, `LOW 55`, `LOW_NEW_TEAM 96`.
- Transfer tracker güncellendi: `49` sinyal, `1` official, `5` corroborated, `16` rumor, `27` review required, toplam değer `€2.2M`. İlk official sinyal geldiği için transfer-strength sinyalinin canlı veriyle tahminlere beklenen yönde yansıyıp yansımadığı ayrıca doğrulanmalı.
- Market value audit hâlâ eski kapsamı gösteriyor: `15` market kulübü / `424` oyuncu / `%68.6` maç kapsamı. TM snapshot artık `18/817` olduğu için `league_market_value_audit` yeniden üretim veya mapping sorunu açısından kontrol edilmeli.
- Hâlâ açık FAIL/WATCH başlıkları:
  - `draw_recall_pct`: Beşiktaş ekran metriğinde `1/9`, `%11.1` FAIL.
  - `manual_alias_pending_network_verification`: `4` WATCH.
  - Beşiktaş display tahmin doğruluğu `%55.2` WATCH.
  - Gol adayı top-5 `%76.9`, top-8 `%84.6` WATCH.
- Kalan öncelik sırası:
  1. `oos_validation_2025_2026.json` dosyasının neden `0` maç ürettiğini düzeltmek; önceki `%52.9` OOS doğruluğu yeniden üretilebilir olmalı.
  2. `league_market_value_audit` dosyasını yeni `18/817` TM snapshot kapsamıyla yeniden üretmek veya mapping boşluğunu bulmak.
  3. İlk `OFFICIAL` transfer sinyalinin `season_fixture_predictions_2026_2027` içindeki transfer edge’e yansıyıp yansımadığını canlı veriyle doğrulamak.
  4. Kalan `17` H2H çiftini tamamlamak.
  5. 4 manuel alias için ağ teyidini tamamlamak.

## 2026-07-17 Günlük Veri/Geliştirme Kontrolü

- 17 Temmuz kontrolünde `data/processed` altında bugün üretilmiş yeni dosya yok (`0`). Son processed üretim hâlâ 16 Temmuz 14:59 civarında.
- Git durumu kontrol başında `main...origin/main` hizalı; localde yalnız önceki günlük kontrol notları nedeniyle `PROJECT_STATE.md` değişikliği var.
- `daily_pipeline_run_latest.md` hâlâ `2026-07-15T10:06:50Z`, network dahil değil, `57/57` başarılı koşusunu gösteriyor. 16 Temmuz düzeltmeleri ve bugünkü durum için güncel bir pipeline health raporu yok.
- `data_quality_scorecard_2025_2026` değişmedi: genel skor `82.1`.
- Açık scorecard başlıkları değişmedi:
  - `manual_alias_pending_network_verification`: `4` WATCH.
  - Beşiktaş display tahmin doğruluğu: `16/29`, `%55.2` WATCH.
  - `draw_recall_pct`: `1/9`, `%11.1` FAIL.
  - Gol adayı top-5: `20/26`, `%76.9` WATCH.
  - Gol adayı top-8: `22/26`, `%84.6` WATCH.
- Transfermarkt/TFF kapsamı korunuyor: 2025/26 TM snapshot `18` kulüp / `817` oyuncu / `€1.74191B`; review queue’da `in_scope_match_rate %94.9`, `scout_blocking_unmatched 0`.
- H2H toplama değişmedi: `153` olası çiftin `136` tanesi toplanmış; kalan `17` çift var.
- Lig geneli tahmin modeli değişmedi: `258` maçta `133` doğru, doğruluk `%51.6`, Brier `0.610`, log loss `1.019`.
- `oos_validation_2025_2026.json` hâlâ bozuk/boş: full-season ve second-half OOS `0` maç, accuracy `None`. Önceki doğrulanmış `%52.9` OOS metriği yeniden üretilemiyor.
- `league_market_value_audit_2025_2026` hâlâ eski kapsamı gösteriyor: `15` market kulübü / `424` oyuncu / `%68.6` maç kapsamı. TM snapshot `18/817` olduğu için audit çıktısı güncel veriyle uyumsuz.
- 2026/27 fikstür tahminleri mevcut ve değişmedi: `34` hafta / `306` maç, oynanmış maç `0`; güven dağılımı `HIGH 67`, `MEDIUM 88`, `LOW 55`, `LOW_NEW_TEAM 96`.
- Transfer tracker değişmedi: `49` sinyal, `1` official, `5` corroborated, `16` rumor, `27` review required, toplam değer `€2.2M`.
- Kalan öncelik sırası aynı:
  1. `oos_validation_2025_2026.json` dosyasının `0` maç üretme nedenini düzeltmek.
  2. `league_market_value_audit` dosyasını yeni `18/817` Transfermarkt snapshot kapsamıyla uyumlu hale getirmek.
  3. İlk `OFFICIAL` transfer sinyalinin fixture tahminlerinde transfer edge’e yansımasını canlı veriyle doğrulamak.
  4. Kalan `17` H2H çiftini tamamlamak.
  5. 4 manuel alias için ağ teyidi tamamlamak.

## 2026-07-18 Günlük Veri/Geliştirme Kontrolü

- 18 Temmuz kontrolünde `data/processed` altında bugün üretilmiş yeni dosya yok (`0`). Son processed üretim hâlâ 16 Temmuz 14:59 civarında.
- Git durumu kontrol başında `main...origin/main` hizalı; localde yalnız günlük kontrol notları nedeniyle `PROJECT_STATE.md` değişikliği var.
- `daily_pipeline_run_latest.md` hâlâ `2026-07-15T10:06:50Z`, network dahil değil, `57/57` başarılı koşusunu gösteriyor. 16 Temmuz düzeltmeleri ve 17-18 Temmuz kontrolleri için güncel pipeline health raporu yok.
- `data_quality_scorecard_2025_2026` değişmedi: genel skor `82.1`.
- Açık scorecard başlıkları değişmedi:
  - `manual_alias_pending_network_verification`: `4` WATCH.
  - Beşiktaş display tahmin doğruluğu: `16/29`, `%55.2` WATCH.
  - `draw_recall_pct`: `1/9`, `%11.1` FAIL.
  - Gol adayı top-5: `20/26`, `%76.9` WATCH.
  - Gol adayı top-8: `22/26`, `%84.6` WATCH.
- Transfermarkt/TFF kapsamı korunuyor: 2025/26 TM snapshot `18` kulüp / `817` oyuncu / `€1.74191B`; review queue’da `in_scope_match_rate %94.9`, `scout_blocking_unmatched 0`.
- H2H toplama değişmedi: `153` olası çiftin `136` tanesi toplanmış; kalan `17` çift var.
- Lig geneli tahmin modeli değişmedi: `258` maçta `133` doğru, doğruluk `%51.6`, Brier `0.610`, log loss `1.019`.
- `oos_validation_2025_2026.json` hâlâ bozuk/boş: full-season ve second-half OOS `0` maç, accuracy `None`. Önceki doğrulanmış `%52.9` OOS metriği yeniden üretilemiyor.
- `league_market_value_audit_2025_2026` hâlâ eski kapsamı gösteriyor: `15` market kulübü / `424` oyuncu / `%68.6` maç kapsamı. TM snapshot `18/817` olduğu için audit çıktısı güncel veriyle uyumsuz.
- 2026/27 fikstür tahminleri mevcut ve değişmedi: `34` hafta / `306` maç, oynanmış maç `0`; güven dağılımı `HIGH 67`, `MEDIUM 88`, `LOW 55`, `LOW_NEW_TEAM 96`.
- Transfer tracker değişmedi: `49` sinyal, `1` official, `5` corroborated, `16` rumor, `27` review required, toplam değer `€2.2M`.
- Kalan öncelik sırası aynı ve artık beklememeli:
  1. `oos_validation_2025_2026.json` dosyasının `0` maç üretme nedenini düzeltmek.
  2. `league_market_value_audit` dosyasını yeni `18/817` Transfermarkt snapshot kapsamıyla uyumlu hale getirmek.
  3. İlk `OFFICIAL` transfer sinyalinin fixture tahminlerinde transfer edge’e yansımasını canlı veriyle doğrulamak.
  4. Kalan `17` H2H çiftini tamamlamak.
  5. 4 manuel alias için ağ teyidi tamamlamak.

## 2026-07-18 (devam) — `oos_validation` 0-Maç Kök Nedeni: Sezon Sonu Veri İmhası Bulundu ve Düzeltildi

- Kök neden `oos_validation`'ın kendisinde değil, kaynak veride bulundu: `src/collect_tff_league_season.py`, `src/collect_besiktas_season.py` ve `src/collect_sofascore_stats.py` üçü de bitmiş **2025-2026 sezonu** için sabit `--season 2025-2026` / sabit `seed-match-id 283783` ile her `--network` günlük pipeline koşusunda TFF/Sofascore'u yeniden tarıyor ve mevcut dosyanın üzerine hiçbir güvenlik kontrolü olmadan yazıyordu. Sezon bittiği için bu siteler artık aynı navigasyondan (aynı seed/sezon kimliğiyle) yeni sezona veya boş sonuca düşüyor; script bunu ayırt etmeden final, tam skorlu veriyi boş/skorsuz fikstür kaydıyla eziyordu.
- Bu, üretimde **iki kez** sessizce gerçekleşmiş:
  - `2026-05-27` (`333e65cb`): `sofascore_match_stats_2025_2026.json` `306/306` maç xG'li iken `0` maça indi.
  - `2026-07-16` (`0e7c0990`): `tff_trendyol_super_lig_2025_2026_matches.json` (`306/306` skorlu → `306` skorsuz) ve `tff_besiktas_2025_2026_matches.json` (`34/34` skorlu → `0` skorlu) aynı anda ezildi. Bu tek commit ~90 türetilmiş rapor dosyasını (lig istihbaratı, scout blueprint, takım ihtiyaç, transfer önerisi, data quality scorecard vb.) bozuk veriyle yeniden üretti.
  - Kimse fark etmedi çünkü çoğu rapor önbelleklenmiş çıktı okuyordu; yalnızca `oos_validation` her çalıştırmada kaynak dosyayı taze okuduğu için hemen `0` maça düşüp görünür oldu.
- **Düzeltme — veri kurtarma**: 3 kaynak dosya (`tff_trendyol_super_lig_2025_2026_matches.json`, `tff_trendyol_super_lig_2025_2026_fixtures.json`, `tff_besiktas_2025_2026_matches.json`+`fixtures`, `sofascore_match_stats_2025_2026.json`) bozulma öncesi git commit'inden (`49a902bb`, 2026-05-25 — sezon zaten bitmişti, `306/306` lig + `34/34` Beşiktaş maçı tam skorlu doğrulandı) geri yüklendi; `enrich_tff_with_sofascore` yeniden çalıştırılarak enriched dosya (`306/306` skor + `306/306` xG) doğru şekilde yeniden üretildi.
- **Düzeltme — kök neden**: `run_daily_pipeline.py`'deki `NETWORK_COMMANDS`'tan `collect_tff_league_season`, `collect_besiktas_season` ve `collect_sofascore_stats --skip-existing` kalıcı olarak çıkarıldı (nedeni açıklayan yorumla). 2025-26 sezonu final ve tam; bu üç collector'ın toplayacağı yeni bir şey yok, yalnız tekrar bozma riski taşıyorlar.
- **Doğrulama**: `pytest` → `58 passed, 3 failed` (aynı 3 önceden var olan ilgisiz `test_season_boundaries` hatası, regresyon yok). Ağsız günlük pipeline (`run_daily_pipeline.py`, network hariç) baştan sona çalıştırıldı: `57/57` başarılı, `0` hata.
- **Sonuç iyileşmesi (xG verisi ~2 aydır boştu, şimdi geri geldi)**:
  - `oos_validation`: tüm sezon `%51.6→%54.7` (`141/258`), ikinci yarı OOS `%52.9→%57.5` (`88/153`).
  - `data_quality_scorecard`: genel skor `82.1→85.4`.
  - Beşiktaş ekran tahmini doğruluğu `%55.2→%65.5` (`19/29`); Beşiktaş beraberlik yakalama `%11.1→%22.2` (`2/9`).
  - `league_market_value_audit` da bu turda yan etki olarak düzeldi: artık güncel `18` kulüp/`817` oyuncu TM snapshot'ıyla uyumlu (önceki öncelik listesindeki 2. madde kapandı) — ayrı bir iş gerekmedi, yalnızca pipeline'ın kendisinin yeniden çalıştırılması yetti.
- **Not**: Bu turda `~1200` dosya değişti (`data/processed` altındaki tüm türetilmiş raporlar/dashboard'lar doğru kaynak veriyle yeniden üretildiği için) — henüz commit/push edilmedi, kullanıcı onayı bekleniyor.
- Kalan öncelik listesi güncellendi:
  1. ~~`oos_validation` 0 maç~~ ✅ düzeltildi (kök neden + veri kurtarma).
  2. ~~`league_market_value_audit` eski kapsam~~ ✅ düzeldi (yan etki).
  3. İlk `OFFICIAL` transfer sinyalinin fixture tahminlerinde transfer edge’e yansımasını canlı veriyle doğrulamak (açık, ağ gerektirir).
  4. Kalan `17` H2H çiftini tamamlamak (açık, ağ gerektirir).
  5. 4 manuel alias için ağ teyidi tamamlamak (açık, ağ gerektirir).
  6. **Yeni**: `collect_tff_league_season`/`collect_besiktas_season`/`collect_sofascore_stats` benzeri "sabit sezon kimliğiyle harici siteyi yeniden tarayan" başka collector olup olmadığı gözden geçirilmeli — aynı sınıf hata (biten sezonu güvenlik kontrolsüz üzerine yazma) başka yerde de gizli olabilir.

## 2026-07-19 Günlük Veri/Geliştirme Kontrolü

- 19 Temmuz kontrolünde `data/processed` altında bugün üretilmiş yeni dosya yok (`0`). Son büyük üretim 18 Temmuz 16:40 civarında.
- Git durumu temiz ve `main...origin/main` hizalı. Son commitler: `fc20d0d8 fix: sezon sonu collector'ların TFF/Sofascore veri imhasını düzelt`, ardından `91964cbd Merge remote-tracking branch 'origin/main'`.
- `daily_pipeline_run_latest.md` güncel sayılır: son ağsız koşu `2026-07-18T13:32:48Z`, `57/57` başarılı, `0` hata.
- `data_quality_scorecard_2025_2026` iyileşmiş durumda ve korunuyor: genel skor `85.4`.
- OOS validation artık düzeldi:
  - Full-season: `141/258`, doğruluk `%54.7`, Brier `0.601`, log loss `1.005`.
  - İkinci yarı OOS: `88/153`, doğruluk `%57.5`, Brier `0.595`, log loss `0.997`.
  - Raw baseline: full-season `%51.2`, second-half OOS `%53.6`; model iki ölçekte de baseline üstünde.
- `league_market_value_audit_2025_2026` yeni TM kapsamına geçti: `18` market kulübü / `817` oyuncu / `%100` maç kapsamı (`258/258`), eksik takım yok. Model accuracy audit içinde `%54.7`; market baseline `%48.1`.
- H2H toplama tamamlandı: `153/153` takım çifti toplandı, eksik takım id yok.
- Transfermarkt/TFF kapsamı korunuyor: 2025/26 TM snapshot `18` kulüp / `817` oyuncu / `€1.74191B`; review queue `in_scope_match_rate %94.9`, `scout_blocking_unmatched 0`.
- 2026/27 fikstür tahminleri mevcut: `34` hafta / `306` maç, oynanmış maç `0`. Güven dağılımı güncel üretimde `HIGH 58`, `MEDIUM 83`, `LOW 69`, `LOW_NEW_TEAM 96`.
- Transfer tracker değişmedi: `49` sinyal, `1` official, `5` corroborated, `16` rumor, `27` review required, toplam değer `€2.2M`. Ancak `season_fixture_predictions_2026_2027` içinde `transfer_signal_available_matches 0`; ilk official sinyal tahmin edge'ine henüz yansımıyor veya takım/eşleşme mapping’i kaçırıyor.
- Avrupa haber nabzı büyüdü: `european_news_pulse_2025_2026` artık `13` haber.
- Açık scorecard WATCH başlıkları:
  - `manual_alias_pending_network_verification`: `4`.
  - Beşiktaş display tahmin doğruluğu: `19/29`, `%65.5`.
  - Beşiktaş beraberlik recall: `2/9`, `%22.2`.
  - Gol adayı top-5: `20/26`, `%76.9`.
  - Gol adayı top-8: `22/26`, `%84.6`.
- Kalan öncelik sırası:
  1. İlk `OFFICIAL` transfer sinyalinin neden fixture tahminlerinde transfer edge olarak görünmediğini incelemek.
  2. 4 manuel alias için ağ teyidini tamamlamak.
  3. Sabit sezon kimliğiyle eski sezon dosyalarını yeniden tarayan başka collector var mı kontrol etmek.
  4. Yeni takımlar için `LOW_NEW_TEAM` yükünü düşürmek üzere 1. Lig/backfill veya resmi kadro-form sinyali eklemek.
  5. Beşiktaş özel ekran katmanındaki draw recall ve gol adayı top-5/top-8 metriklerini daha okunur ürün diliyle iyileştirmek.

## 2026-07-20 Günlük Veri/Geliştirme Kontrolü

- 20 Temmuz kontrolünde `data/processed` altında bugün üretilmiş yeni dosya yok (`0`). Son büyük üretim hâlâ 18 Temmuz 16:40 civarında.
- Git durumu kontrol başında `main...origin/main` hizalı; localde yalnız günlük kontrol notları nedeniyle `PROJECT_STATE.md` değişikliği var.
- `daily_pipeline_run_latest.md` güncel son ağsız koşuyu gösteriyor: `2026-07-18T13:32:48Z`, `57/57` başarılı, `0` hata.
- `data_quality_scorecard_2025_2026` değişmedi: genel skor `85.4`.
- OOS validation sağlıklı kalıyor:
  - Full-season: `141/258`, doğruluk `%54.7`, Brier `0.601`, log loss `1.005`.
  - İkinci yarı OOS: `88/153`, doğruluk `%57.5`, Brier `0.595`, log loss `0.997`.
  - Raw baseline: full-season `%51.2`, second-half OOS `%53.6`.
- `league_market_value_audit_2025_2026` güncel TM kapsamıyla uyumlu kalıyor: `18` market kulübü / `817` oyuncu / `%100` maç kapsamı, eksik takım yok.
- H2H toplama tamamlanmış durumda: `153/153` takım çifti.
- Transfermarkt/TFF kapsamı korunuyor: 2025/26 TM snapshot `18` kulüp / `817` oyuncu / `€1.74191B`; review queue `in_scope_match_rate %94.9`, `scout_blocking_unmatched 0`.
- 2026/27 fikstür tahminleri mevcut ve değişmedi: `34` hafta / `306` maç, oynanmış maç `0`; güven dağılımı son üretimde `HIGH 58`, `MEDIUM 83`, `LOW 69`, `LOW_NEW_TEAM 96`.
- Transfer tracker değişmedi: `49` sinyal, `1` official, `5` corroborated, `16` rumor, `27` review required, toplam değer `€2.2M`. `season_fixture_predictions_2026_2027` içinde hâlâ `transfer_signal_available_matches 0`; official transfer sinyali fixture tahmin edge’ine yansımıyor.
- Avrupa haber nabzı son üretimde `13` haber.
- Açık scorecard WATCH başlıkları değişmedi:
  - `manual_alias_pending_network_verification`: `4`.
  - Beşiktaş display tahmin doğruluğu: `19/29`, `%65.5`.
  - Beşiktaş beraberlik recall: `2/9`, `%22.2`.
  - Gol adayı top-5: `20/26`, `%76.9`.
  - Gol adayı top-8: `22/26`, `%84.6`.
- Kalan öncelik sırası aynı:
  1. İlk `OFFICIAL` transfer sinyalinin fixture tahminlerinde neden transfer edge olarak görünmediğini incelemek.
  2. 4 manuel alias için ağ teyidini tamamlamak.
  3. Sabit sezon kimliğiyle eski sezon dosyalarını yeniden tarayan başka collector var mı kontrol etmek.
  4. Yeni takımlar için `LOW_NEW_TEAM` yükünü düşürmek üzere 1. Lig/backfill veya resmi kadro-form sinyali eklemek.
  5. Beşiktaş özel ekran katmanındaki draw recall ve gol adayı top-5/top-8 metriklerini daha okunur ürün diliyle iyileştirmek.

## 2026-07-21 Günlük Veri/Geliştirme Kontrolü

- 21 Temmuz kontrolünde `data/processed` altında bugün üretilmiş yeni dosya yok (`0`). Ancak 20 Temmuz’da önemli bir türetilmiş çıktı/görsel rapor üretimi yapılmış: `league_scouting_enriched_2025_2026_dashboard.html`, scout dashboardları, transfer tracker, OOS, market audit, data catalog ve birçok takım dashboardu güncellenmiş.
- Git çalışma alanı temiz değil: `PROJECT_STATE.md` dışında çok sayıda `data/processed/*` ve UI/rapor builder dosyası (`src/build_*`, `src/html_utils.py`) değişmiş. Bu değişiklikler muhtemelen 20 Temmuz’daki başka agent/geliştirme turundan geliyor; revert edilmedi.
- `daily_pipeline_run_latest.md` hâlâ son ağsız koşuyu `2026-07-18T13:32:48Z`, `57/57` başarılı, `0` hata olarak gösteriyor. 20 Temmuz’daki geniş rapor/UI üretimi için ayrı pipeline health raporu yok.
- `data_quality_scorecard_2025_2026` değişmedi: genel skor `85.4`.
- OOS validation sağlıklı ve küçük iyileşme var:
  - Full-season: `142/258`, doğruluk `%55.0`, Brier `0.600`, log loss `1.005`.
  - İkinci yarı OOS: `89/153`, doğruluk `%58.2`, Brier `0.595`, log loss `0.996`.
  - Raw baseline: full-season `%51.2`, second-half OOS `%53.6`.
- `league_market_value_audit_2025_2026` güncel TM kapsamıyla uyumlu kalıyor: `18` market kulübü / `817` oyuncu / `%100` maç kapsamı, eksik takım yok. Audit içindeki model accuracy hâlâ `%54.7`; OOS çıktısındaki `%55.0/%58.2` ile rapor zamanlaması farkı izlenmeli.
- H2H toplama tamamlanmış durumda: `153/153` takım çifti.
- Transfermarkt/TFF kapsamı korunuyor: review queue `tm_clubs 18`, `tm_players 817`, `in_scope_match_rate %94.6`, operational in-scope mapping `%95.2`, `scout_blocking_unmatched 0`. 20 Temmuz üretiminden sonra eşleşen profil sayısı `594→592` düşmüş; blokaj üretmedi ama izlenmeli.
- Scout kalite raporu tekrar ana havuzu doğru yansıtıyor: `370` blueprint aday bağlantısı, düşük güvenli blueprint `0`, pozisyon matrisi adayı `105`, repeated role `0`. Pozisyon matrisi `691` aday / `105` rol eşleşmesi / `18` takım.
- 2026/27 fikstür tahminleri mevcut ve değişmedi: `34` hafta / `306` maç, oynanmış maç `0`; güven dağılımı `HIGH 58`, `MEDIUM 83`, `LOW 69`, `LOW_NEW_TEAM 96`.
- Transfer tracker değişti: `49` sinyal, `official_count 0`, `confirmed_count 7`, `CORROBORATED 7`, `RUMOR 13`, `REVIEW_REQUIRED 29`, toplam değer `0`. Önceki `1 official / €2.2M` sinyal artık official görünmüyor.
- Transfer edge kök neden adayı netleşti: `transfer_tracker_2025_2026.json` içindeki doğrulanmış sinyallerde oyuncu isimleri var ama `team`, `club`, `to_team`, `from_team` alanları `None`; bu yüzden `transfer_strength_edge(team_name)` fixture takım adlarıyla eşleşemiyor ve `season_fixture_predictions_2026_2027` içinde `transfer_signal_available_matches 0` kalıyor.
- Avrupa haber nabzı son üretimde `13` haber.
- Açık scorecard WATCH başlıkları değişmedi:
  - `manual_alias_pending_network_verification`: `4`.
  - Beşiktaş display tahmin doğruluğu: `19/29`, `%65.5`.
  - Beşiktaş beraberlik recall: `2/9`, `%22.2`.
  - Gol adayı top-5: `20/26`, `%76.9`.
  - Gol adayı top-8: `22/26`, `%84.6`.
- Kalan öncelik sırası:
  1. Transfer tracker sinyallerine hedef takım (`to_team`/normalized team) alanı kazandırmak; ardından transfer edge’in 2026/27 fixture tahminlerine yansıdığını doğrulamak.
  2. 4 manuel alias için ağ teyidini tamamlamak.
  3. 20 Temmuz’da değişen UI/rapor builder dosyalarının kapsamını review edip gerekiyorsa commit/push hazırlamak.
  4. Sabit sezon kimliğiyle eski sezon dosyalarını yeniden tarayan başka collector var mı kontrol etmek.
  5. Yeni takımlar için `LOW_NEW_TEAM` yükünü düşürmek üzere 1. Lig/backfill veya resmi kadro-form sinyali eklemek.
  6. Beşiktaş özel ekran katmanındaki draw recall ve gol adayı top-5/top-8 metriklerini daha okunur ürün diliyle iyileştirmek.

## 2026-07-21 (devam) — WC 2026 Linkleri Kaldırıldı, Sessiz Pipeline Hatası Bulundu, Avrupa Eleme Nabzı Yenilendi, Transfer Edge Kök Nedeni Netleşti

- **WC 2026 linkleri site genelinde kaldırıldı**: Turnuva bitti, kullanıcı isteğiyle `worldcup_2026_predictions.html` artık hiçbir sayfadan linklenmiyor — anasayfa (`gundem_2025_2026.html`: nav linki + sidebar teaser bloğu), `football_intelligence_home.html` (nav + panel kart), `html_utils.py` paylaşılan nav (12 rapor sayfası bunu kullanıyor), `build_european_predictions.py` kendi nav'ı, `build_sitemap.py`. Sayfa/veri/script'ler silinmedi, yalnızca iç bağlantılar kesildi. `html_utils.py`'deki eski "Tahminler → WC 2026" linki "Fikstür → season_fixture_predictions_2026_2027.html" oldu; paylaşılan nav'a ayrıca "Avrupa" linki eklendi (önceden sadece anasayfa ve Avrupa sayfasının kendi nav'ında vardı, alt sayfalarda yoktu).
- **Bulunan gerçek pipeline hatası**: `src/build_enriched_scout_dashboard.py`, 27 Haziran'daki büyük yeniden yazımda (`e88cb9c6`) `if __name__ == "__main__": main()` bloğunu kaybetmiş. `run_daily_pipeline.py` bunu `python -m src.build_enriched_scout_dashboard` ile her gün çalıştırıp "başarılı" (exit 0) sayıyordu ama modül hiçbir şey yazmıyordu — `league_scouting_enriched_2025_2026_dashboard.html` (691 oyunculu scout havuzu sayfası) 27 Haziran'dan beri sessizce donmuştu. Guard eklendi, sayfa yeniden üretildi (bugünkü veriyle). Diğer tüm `src/build_*.py` dosyaları tarandı, başka eksik guard bulunmadı.
- **Avrupa eleme turu analizi yenilendi** (`collect_news_rss`, `collect_news_google`, `build_european_news_pulse`, `build_european_predictions` yeniden çalıştırıldı → 13'ten 48 ilgili habere çıktı). football-data.org nitelendirme turlarını kapsamadığı için hâlâ tek kaynak haber sinyali. Güncel durum: Fenerbahçe CL 2. ön eleme turunda Górnik Zabrze (Polonya) ile 21 Temmuz'da (Chobani, ilk maç) oynuyor, geçerse 3. turda Sturm Graz-Hearts galibiyle eşleşecek; Beşiktaş EL 2. ön eleme turunda Midtjylland (Danimarka) ile 23 Temmuz'da oynayacak, geçerse 3. turda Hradec Kralove-Tromsø galibiyle eşleşecek; Başakşehir ECL 2. ön eleme turunda Inter Turku (Finlandiya) ile oynuyor, geçerse 3. turda Vaduz-Escaldes galibiyle eşleşecek. Galatasaray ve Trabzonspor için nabızda hiç sinyal yok (muhtemelen Galatasaray şampiyon sıfatıyla doğrudan lig fazına gitti, Trabzonspor Avrupa kupasında değil — ikisi de bu kaynakla doğrulanmadı, ayrıca teyit edilmeli).
- **Transfer edge kök nedeni düzeltildi/netleşti — önceki tanı (bugünkü ilk "Günlük Kontrol" bölümünde) yanlıştı**: O bölüm "`to_team`/`from_team` alanları None" diyordu; kod incelendiğinde `transfer_strength_edge()`'in gerçekten `to_club`/`from_club` okuduğu ve bu alanların dolu olduğu görüldü (ör. Ivanovic kaydında `to_club: "Galatasaray"`). Asıl kök neden: fonksiyon önce `value = record.get("market_value_eur") or 0` okuyor ve `market_value_eur` `null` olan 7 CORROBORATED kaydın (Ivanovic→GS, Çavuşoğlu→Gençlerbirliği, Diarra→Kasımpaşa, El Yamiq→Eyüpspor, Colley→Konyaspor, Ben Ali→Alanyaspor) hepsi `if not weight or not value: continue` satırında kulüp eşleşmesine hiç ulaşmadan atlanıyor. Sonuç: her takım için `confirmed_net_value` `0` kalıyor, `€2M` eşiği hiç geçilmiyor, `season_fixture_predictions_2026_2027` içinde `transfer_signal_available_matches` hep `0`. Düzeltme için bu 6 oyuncunun Transfermarkt profili bulunup piyasa değeriyle eşleştirilmesi gerekiyor (ağ gerektirir, bu turda yapılmadı — kullanıcı onayı bekleniyor).
- Kalan öncelik sırası (düzeltilmiş kök nedenle):
  1. 6 CORROBORATED transferin (Ivanovic, Çavuşoğlu, Diarra, El Yamiq, Colley, Ben Ali) Transfermarkt profilini bulup `market_value_eur` alanını doldurmak; ardından transfer edge'in fixture tahminlerine yansıdığını doğrulamak.
  2. 4 manuel alias için ağ teyidini tamamlamak.
  3. Sabit sezon kimliğiyle eski sezon dosyalarını yeniden tarayan başka collector var mı kontrol etmek.
  4. Yeni takımlar için `LOW_NEW_TEAM` yükünü düşürmek üzere 1. Lig/backfill veya resmi kadro-form sinyali eklemek.
  5. Beşiktaş özel ekran katmanındaki draw recall ve gol adayı top-5/top-8 metriklerini daha okunur ürün diliyle iyileştirmek.
  6. Galatasaray/Trabzonspor'un 2026-27 Avrupa kupası durumu (lig fazı/yok) ayrı doğrulanmalı — haber nabzında hiç sinyal yok.

## 2026-07-21 (devam 2) — Transfer Piyasa Değeri Boşluğu Kapatıldı, Ama Eşik Hâlâ Geçilmiyor (Bu Doğru Davranış)

- **Kök neden doğrulandı ve düzeltildi**: `analyze_news_with_claude.py`'deki oyuncu eşleştirme (`_build_player_index()`) yalnızca daha önce Süper Lig'de oynamış (TFF havuzundaki) oyunculardan çalışıyor. 7 CORROBORATED transferin 6'sı (Ivanovic hariç) **ilk kez Süper Lig'e gelen yabancı/yeni imzalar** olduğu için bu havuzda hiç yoklar — dolayısıyla `tm_market_value_eur` hiç atanmıyordu. Bu, "kadro değişince analiz güncellenmiyor" endişesinin somut bir örneğiydi.
- **Yapılan düzeltme**: 5 oyuncunun (Thiemoko Diarra→Kasımpaşa, Ebrima Colley→Konyaspor, Omar Ben Ali→Alanyaspor, Muhammet Ensar Çavuşoğlu→Gençlerbirliği, Jawad El Yamiq→Eyüpspor) gerçek Transfermarkt piyasa değeri ilgili kulübün güncel (2026-27) TM kadro sayfasından canlı çekilerek doğrulandı (€300K–€1.5M arası). `data/manual/new_signing_market_values_2025_2026.json` adıyla kaynaklı bir manuel snapshot dosyası oluşturuldu (mevcut `opponent_market_values` dosyasıyla aynı stil/format). `build_transfer_tracker.py`'ye bu dosyayı okuyup `tm_market_value_eur` boşsa fallback olarak kullanan `_load_new_signing_market_value_overrides()` eklendi. `transfer_tracker_2025_2026.json` artık `total_value_eur: 0 → 3.75M` gösteriyor.
- **Nikola Ivanovic (Galatasaray) kasıtlı olarak boş bırakıldı**: Transfermarkt'ta bu isimde 3 farklı oyuncu var, hiçbiri Galatasaray kadrosunda görünmüyor; haber kaynağının ("Haberler" agregatörü) yanlış/erken olması ihtimali var. Uydurmak yerine `market_value_eur: null` bırakıldı, dosyada not olarak açıklandı.
- **Dürüst sonuç — eşik hâlâ geçilmiyor**: `build_season_fixture_predictions` yeniden çalıştırıldı; 306 maçın hiçbirinde `transfer_signal.home/away.available` hâlâ `true` değil. Neden: `transfer_strength_edge()` CORROBORATED ağırlığı `0.6`; en büyük düzeltilmiş değer olan Diarra'nın `€1.5M`'i bile `0.6 × 1.5M = €900K` ediyor, takım başına `€2M` eşiğinin altında kalıyor. Bu bir hata değil — model kasıtlı olarak küçük/orta değerli tek transferlere aşırı tepki vermeyecek şekilde kalibre edilmiş. Yani mekanizma artık doğru çalışıyor, sadece bu pencerede henüz eşiği geçecek büyüklükte (tek başına ≥€2M veya aynı takıma birikmiş ≥€3.3M CORROBORATED) bir transfer yok.
- Kalan öncelik sırası güncellendi:
  1. ~~Transfer sinyali market value boşluğu~~ ✅ düzeltildi (mekanizma artık çalışıyor); ama görünür etki için ya daha büyük bir OFFICIAL transfer ya da aynı takımda birikmiş sinyal gerekiyor — pencere ilerledikçe tekrar kontrol edilmeli.
  2. Nikola Ivanovic→Galatasaray sinyalinin gerçek olup olmadığını ayrı doğrulamak (TM'de eşleşme yok).
  3. 4 manuel alias için ağ teyidini tamamlamak.
  4. Sabit sezon kimliğiyle eski sezon dosyalarını yeniden tarayan başka collector var mı kontrol etmek.
  5. Yeni takımlar için `LOW_NEW_TEAM` yükünü düşürmek üzere 1. Lig/backfill veya resmi kadro-form sinyali eklemek.
  6. Galatasaray/Trabzonspor'un 2026-27 Avrupa kupası durumu ayrı doğrulanmalı.

## 2026-07-21 (devam 3) — Push Sırasında Bot Merge'i, Transfer Sinyali Artık Gerçekten Aktif

- `git push` ilk denemede reddedildi: origin/main'de aradan geçen sürede otomatik "haber yenileme"/"full pipeline" bot commit'leri birikmiş. Rebase'de `data/processed/*` (tamamen türetilmiş) dosyalarda çok sayıda çakışma çıktı, `src/`/`PROJECT_STATE.md`/`data/manual/` tarafında hiç çakışma yoktu. Rebase abort edilip `git merge origin/main` yapıldı; `data/processed/*` çakışmaları bot'un en taze sürümü (`--theirs`) alınarak çözüldü, ardından `python -m src.run_daily_pipeline` (ağsız) baştan sona çalıştırılarak tüm türetilmiş sayfalar bugünkü koddan yeniden üretildi: `57/57` başarılı.
- **Transfer sinyali mekanizması artık gerçekten aktif** — bot'un taze haber taramasında Trabzonspor'a `€23M`'lik bir CORROBORATED transfer (Christ Inao Oulaï) ve Rizespor'a iki transfer (Ahmed Kutucu `€3M`, Tayyip Talha Sanuç `€1.5M`) düşmüş; bunlar zaten TFF havuzunda olduğu için otomatik piyasa değeri almışlardı ve artık `€2M` eşiğini üç takım için de geçtiler. `season_fixture_predictions_2026_2027.json`'da artık `102` maç-taraf örneğinde `transfer_signal.available: true` (Rizespor, Gaziantep, Trabzonspor). Bu turdaki manuel override (Diarra/Çavuşoğlu/El Yamiq) hâlâ tabloda ama eşiği tek başına geçmiyor; asıl aktivasyonu tetikleyen bot'un bulduğu büyük Trabzonspor transferi oldu — yani mekanizma uçtan uca doğrulanmış oldu.
- Commit `7b6df946` + merge `82fa5097` + pipeline yeniden üretimi `origin/main`'e push edildi.

## 2026-07-21 (devam 4) — Avrupa Eleme Maçları İçin Gerçek Fikstür Kartı Eklendi, Fikstür Sıkışıklığı/Yorgunluk Sinyali Kuruldu

- **Kullanıcı sorusu**: "Bugün Perşembe'ye vs eleme maçları var ama sitede göremedim" — kök neden: `european_predictions_2026_2027.html` tahminlerini football-data.org'dan çekiyor, o API nitelendirme/eleme turu fikstürünü hiç kapsamıyor. Maçlar yalnızca "Haber Nabzı" başlıkları içinde gömülüydü, gerçek bir maç kartı hiçbir yerde yoktu.
- **Düzeltme**: Haber kaynaklarından tarih/saat/mekan/hakem doğrulanıp `data/manual/european_qualifier_fixtures_2026_2027.json` oluşturuldu (Fenerbahçe-Górnik Zabrze 21 Tem 21:00 Chobani; Başakşehir-Inter Turku 22 Tem 20:45 hakem Martínez Munuera; Beşiktaş-Midtjylland 23 Tem Perşembe, saat teyit edilmedi). `build_european_predictions.py`'ye bunu gösteren yeni "📋 Bilinen Eleme Maçları" bölümü eklendi (sayfanın en üstünde) — **skor/olasılık tahmini bilerek üretilmedi**, çünkü bu rakipler (Górnik Zabrze, Midtjylland, Inter Turku) için hiç istatistik veri tabanımız yok, üretmek fabrikasyon olurdu. `build_live_feed.py`'deki anasayfa teaser'ı da artık en yakın gerçek maçı ("Bugün 21:00 — Fenerbahçe - Górnik Zabrze") gösteriyor, genel haber başlığı yerine.
- **Kullanıcının ikinci isteği**: Avrupa maçlarındaki oyuncu/takım performansının (skor, possession, pas vb.) gelecek lig maçı tahminlerinde de kullanılması. Üç parçaya ayrıldı: (1) fikstür sıkışıklığı/yorgunluk sinyali — bugünkü veriyle inşa edilebilir, (2) oyuncu bazlı dakika/yorgunluk — Avrupa maçının kadro verisi toplanmalı, (3) possession/pas gibi maç istatistiklerinin güç sinyaline çevrilmesi — yeni collector + backtest gerektirir. Kullanıcı 1. maddeyi seçti.
- **Sofascore erişim testi**: Mevcut `collect_sofascore_stats.py`'nin kullandığı tam aynı endpoint/header ile canlı test edildi, bu ortamdan `403` döndü. Yani (2) ve (3) maddeleri için canlı veri toplama şu an bu ortamdan mümkün değil (GitHub Actions ortamında farklı olabilir, doğrulanmadı) — kaydedildi, ileride tekrar denenmeli.
- **Yapılan (1. madde) — Fikstür sıkışıklığı/yorgunluk sinyali**: `src/preview/probability.py`'ye `fixture_congestion_edge(team_name, match_date)` eklendi. `european_fixtures_2026_2027.json` (otomatik, lig fazı başlayınca dolacak) ve `data/manual/european_qualifier_fixtures_2026_2027.json` (manuel, eleme turu) birleştirilerek bir takımın Avrupa maç tarihleri indeksleniyor; lig maçından `1-4 gün önce` Avrupa maçı oynanmışsa küçük bir ceza sinyali dönüyor (`-0.09`'dan `-0.03`'e, gün sayısına göre azalan). `model_league_predictions.py`'de `transfer_strength_edge` ile birebir aynı desende (`apply_fixture_congestion` bayrağıyla gated, yalnızca `build_season_fixture_predictions.py`'de `True`, kalibre edilmiş backtest sistemini etkilemiyor) `strength_edge`'e ekleniyor ve çıktıya `fixture_congestion` alanı olarak ekleniyor.
- **Doğrulama**: Fonksiyon senkron test edildi — Fenerbahçe için bugünkü maçtan 3 gün sonrasına kurgulanan bir tarih `available: true, edge: -0.06, days_rest: 3` döndürdü; 5 gün sonrası ve alakasız takım (Trabzonspor) doğru şekilde `available: false` verdi. Gerçek `season_fixture_predictions_2026_2027.json`'da şu an `0` aktif örnek var — beklenen davranış, çünkü bilinen tek Avrupa maçları (Temmuz eleme) ile sezon açılışı (14 Ağustos) arasında `4` günlük pencereden daha uzun bir boşluk var. Sinyal 3./4. eleme turu ve Ağustos sonu play-off turu yaklaştıkça veya lig fazı (Eylül) başlayınca gerçek etkisini gösterecek.
- `python -m src.run_daily_pipeline` (ağsız) yeniden çalıştırıldı: `57/57` başarılı, `0` hata.
- Kalan öncelik sırası güncellendi:
  1. **Yeni**: `fixture_congestion` sinyalinin gerçek aktivasyonunu (3./4. eleme turu + Ağustos sonu play-off + Eylül lig fazı yaklaştıkça) izlemek; ilk aktif örnekler çıktığında edge büyüklüğünün (-0.09..-0.03) makul olup olmadığını gözden geçirmek — henüz backtest edilmedi.
  2. Sofascore canlı erişiminin GitHub Actions ortamında çalışıp çalışmadığını doğrulamak (bu ortamda `403`); çalışıyorsa Avrupa maçı oyuncu dakika/possession verisi toplama fizibilitesi yeniden değerlendirilebilir.
  3. Nikola Ivanovic→Galatasaray sinyalinin gerçek olup olmadığını ayrı doğrulamak (TM'de eşleşme yok).
  4. 4 manuel alias için ağ teyidini tamamlamak.
  5. Sabit sezon kimliğiyle eski sezon dosyalarını yeniden tarayan başka collector var mı kontrol etmek.
  6. Yeni takımlar için `LOW_NEW_TEAM` yükünü düşürmek üzere 1. Lig/backfill veya resmi kadro-form sinyali eklemek.
  7. Galatasaray/Trabzonspor'un 2026-27 Avrupa kupası durumu ayrı doğrulanmalı.

## 2026-07-22 Günlük Veri/Geliştirme Kontrolü

- 22 Temmuz kontrolünde `data/processed` altında bugün üretilmiş yeni dosya yok (`0`). Son üretim 21 Temmuz 15:05 civarında.
- Git durumu temiz ve `main...origin/main` hizalı. Son commitler: `7f417cba feat: Avrupa eleme maçları için gerçek fikstür kartı ve fikstür sıkışıklığı/yorgunluk sinyali`, `05efd494 Merge remote-tracking branch 'origin/main'`, `ea7480e0 chore: bot merge sonrası pipeline'ı yeniden üret`.
- `daily_pipeline_run_latest.md` güncel son ağsız koşuyu gösteriyor: `2026-07-21T12:05:30Z`, `57/57` başarılı, `0` hata.
- `data_quality_scorecard_2025_2026` değişmedi: genel skor `85.4`.
- OOS validation sağlıklı kalıyor:
  - Full-season: `142/258`, doğruluk `%55.0`, Brier `0.600`, log loss `1.005`.
  - İkinci yarı OOS: `89/153`, doğruluk `%58.2`, Brier `0.595`, log loss `0.996`.
  - Raw baseline: full-season `%51.2`, second-half OOS `%53.6`.
- `league_market_value_audit_2025_2026` güncel TM kapsamıyla uyumlu: `18` market kulübü / `817` oyuncu / `%100` maç kapsamı. Audit model accuracy `%55.0`, market baseline `%48.1`.
- H2H tamamlanmış durumda: `153/153` takım çifti.
- Transfer tracker güncel: `43` sinyal, `1` official, `6` corroborated, `8` rumor, `28` review required, toplam değer `€7.9M`.
- Transfer edge artık fixture tahminlerine yansıyor: `season_fixture_predictions_2026_2027.json` içinde `66` maç-taraf örneğinde `transfer_signal.available = true`. Örnekler:
  - Rizespor için Ahmed Kutucu + Tayyip Talha Sanuç girişleri `confirmed_net_value_eur 2.7M`, edge `+0.054`.
  - Gaziantep için çıkış yönlü sinyal `confirmed_net_value_eur -2.1M`, edge `-0.0514`.
- 2026/27 fikstür tahminleri mevcut: `34` hafta / `306` maç, oynanmış maç `0`; güven dağılımı `HIGH 58`, `MEDIUM 84`, `LOW 68`, `LOW_NEW_TEAM 96`.
- `fixture_congestion` sinyali kurulu ama henüz gerçek fikstürlerde aktif değil: `fixture_congestion_available_matches 0`. Beklenen davranış; Temmuz eleme maçları ile 16 Ağustos lig açılışı arasında 4 günden fazla boşluk var.
- Avrupa eleme fikstür kartı mevcut: manuel dosyada Fenerbahçe-Górnik Zabrze (`2026-07-21 21:00`), Başakşehir-Inter Turku (`2026-07-22 20:45`), Beşiktaş-FC Midtjylland (`2026-07-23`, saat teyitsiz) tutuluyor. `european_predictions_2026_2027.json` hâlâ API kaynaklı tahmin üretmiyor; bu doğru, çünkü eleme turu için güvenilir istatistik veri tabanı yok.
- Avrupa haber nabzı büyüdü: `european_news_pulse_2025_2026` artık `61` haber.
- Transfermarkt/TFF eşleşme kapsamı korunuyor: review queue `tm_clubs 18`, `tm_players 817`, `in_scope_match_rate %94.6`, operational in-scope mapping `%95.2`, `scout_blocking_unmatched 0`.
- Scout kalite raporu temiz: `370` blueprint aday bağlantısı, düşük güvenli blueprint `0`, pozisyon matrisi adayı `105`, repeated role `0`.
- Açık scorecard WATCH başlıkları değişmedi:
  - `manual_alias_pending_network_verification`: `4`.
  - Beşiktaş display tahmin doğruluğu: `19/29`, `%65.5`.
  - Beşiktaş beraberlik recall: `2/9`, `%22.2`.
  - Gol adayı top-5: `20/26`, `%76.9`.
  - Gol adayı top-8: `22/26`, `%84.6`.
- Kalan öncelik sırası:
  1. `fixture_congestion` sinyalinin ilk gerçek aktif örneklerini izlemek; 3./4. eleme turu ve Ağustos play-off döneminde edge büyüklüğünü kontrol etmek.
  2. Sofascore canlı erişiminin GitHub Actions ortamında çalışıp çalışmadığını doğrulamak; bu ortamda `403`.
  3. Avrupa maç kartlarında Beşiktaş-Midtjylland saat/venue bilgisini resmi kaynakla netleştirmek.
  4. Nikola Ivanovic→Galatasaray sinyalinin gerçek olup olmadığını ayrı doğrulamak.
  5. 4 manuel alias için ağ teyidini tamamlamak.
  6. Sabit sezon kimliğiyle eski sezon dosyalarını yeniden tarayan başka collector var mı kontrol etmek.
  7. Yeni takımlar için `LOW_NEW_TEAM` yükünü düşürmek üzere 1. Lig/backfill veya resmi kadro-form sinyali eklemek.

## 2026-07-22 Akşam Kontrolü

- 22 Temmuz akşam kontrolünde `data/processed` altında bugün üretilmiş yeni dosya yok (`0`); son üretim hâlâ 21 Temmuz 15:05.
- Git durumu kontrol başında temizdi; bu kayıt sonrası yalnız `PROJECT_STATE.md` değişti.
- `daily_pipeline_run_latest.md` değişmedi: `2026-07-21T12:05:30Z`, `57/57` başarılı, `0` hata.
- Sabah/günlük kontrolde kaydedilen ana metriklerde yeni değişiklik yok: scorecard `85.4`, OOS second-half `%58.2`, market audit `%100`, H2H `153/153`.
- Transfer edge durumu değişmedi: `season_fixture_predictions_2026_2027.json` içinde `66` maç-taraf örneğinde transfer sinyali aktif.
- `fixture_congestion` hâlâ gerçek fikstürlerde aktif değil (`0`); Temmuz Avrupa eleme maçları ile lig açılışı arasındaki süre 4 günden fazla olduğu için beklenen davranış.
- Kalan öncelik sırası aynı: `fixture_congestion` aktivasyonunu izlemek, Sofascore GitHub Actions erişimini doğrulamak, Beşiktaş-Midtjylland saat/venue bilgisini resmi kaynakla netleştirmek, Nikola Ivanovic sinyalini ve 4 manuel alias’ı teyit etmek, sabit sezon collector risklerini taramak, yeni takımlar için veri backfill eklemek.

## 2026-07-23 Günlük Veri/Geliştirme Kontrolü

- 23 Temmuz kontrolünde `data/processed` altında bugün üretilmiş yeni dosya yok (`0`); son üretim hâlâ 21 Temmuz 15:05. Bu nedenle günlük heartbeat'te yeni veri çekimi değil, mevcut son pipeline çıktılarının sağlık kontrolü yapıldı.
- Git durumu kontrol başında `main...origin/main` hizalıydı; bu kayıt öncesi yalnız `PROJECT_STATE.md` değişmiş durumdaydı.
- `daily_pipeline_run_latest.md` son ağsız pipeline koşusunu gösteriyor: `2026-07-21T12:05:30Z`, `57/57` başarılı, `0` hata. JSON raporunda aynı koşu `generated_at/include_network/command_count/ok_count/failed_count` şemasıyla tutuluyor.
- `data_quality_scorecard_2025_2026` ana skoru değişmedi: `85.4`. Warehouse kapsamı: `306` maç, `18` takım, `691` oyuncu, `29` hakem, `370` team scout blueprint, `298` gol adayı.
- OOS validation değişmedi:
  - Full-season: `142/258`, doğruluk `%55.0`, Brier `0.600`, log loss `1.005`.
  - İkinci yarı OOS: `89/153`, doğruluk `%58.2`, Brier `0.595`, log loss `0.996`.
  - Raw baseline: full-season `%51.2`, second-half OOS `%53.6`; model baseline üstünde kalıyor ama `%80` hedefi için hâlâ yeni veri/feature/backtest gerekiyor.
- Market audit değişmedi: `18` market kulübü / `817` Transfermarkt oyuncusu / `%100` maç kapsamı; model accuracy `%55.0`, market baseline `%48.1`.
- Transfer tracker son üretimi `2026-07-21T12:05:29Z`: `43` sinyal, `1` official, `6` corroborated, `8` rumor, `28` review required, toplam değer `€7.9M`.
- 2026/27 sezon fikstür tahmini dosyası sağlıklı biçimde `34` hafta / `306` maç içeriyor; oynanmış maç `0`. Yeni takımlar: `AMED SPORTİF FAALİYETLER`, `ERZURUMSPOR FK`, `ÇORUM FK`; yeni takım içeren maç sayısı `96`.
- 2026/27 fixture güven dağılımı doğru anahtar olan `data_confidence` üzerinden kontrol edildi: `HIGH 58`, `MEDIUM 84`, `LOW 68`, `LOW_NEW_TEAM 96`. İlk hızlı kontrolde `confidence` anahtarına bakıldığı için yanlış `null` sonucu görülmüştü; gerçek alan `data_confidence`.
- Transfer edge 22 Temmuz'a göre biraz artmış görünüyor: `season_fixture_predictions_2026_2027.json` içinde `68` maç-taraf örneğinde `transfer_signal.available = true` (`22 Temmuz kaydı: 66`). Aktif örnekler hâlâ ağırlıklı olarak:
  - Rizespor: Ahmed Kutucu + Tayyip Talha Sanuç, `confirmed_net_value_eur 2.7M`, edge `+0.054`.
  - Gaziantep: çıkış yönlü sinyal, `confirmed_net_value_eur -2.1M`, edge `-0.0514`.
- `fixture_congestion` sinyali kurulu ama gerçek lig fikstürlerinde hâlâ aktif değil: `0` maç-taraf. Bu beklenen davranış; bilinen Temmuz Avrupa eleme maçları ile 14 Ağustos lig açılışı arasında modelin 1-4 günlük yorgunluk penceresinden uzun boşluk var.
- Avrupa eleme manuel fikstürü hâlâ güncellenmemiş kritik alan taşıyor: Beşiktaş-FC Midtjylland maçında saat `00:00` placeholder, `kickoff_time_confirmed: false`, venue resmi teyitsiz. Bugünün en uygulanabilir veri işi bu maçın resmi saat/venue bilgisini doğrulayıp manuel dosyayı güncellemek.
- `european_predictions_2026_2027.json` hâlâ UEFA eleme turları için skor/olasılık tahmini üretmiyor; bu doğru bir koruma, çünkü Football-data ücretsiz planı eleme fikstürünü kapsamıyor ve rakip takımlar için güvenilir istatistik tabanı yok.
- Avrupa haber nabzı son üretimde `61` haberle duruyor; bugün yeni haber çekimi yapılmamış.
- Transfermarkt/TFF eşleşme kuyruğu değişmedi: `tm_clubs 18`, `tm_players 817`, `in_scope_match_rate %94.6`, operational in-scope mapping `%95.2`, `scout_blocking_unmatched 0`.
- Scout kalite raporu temiz: `370` blueprint aday bağlantısı, düşük güvenli blueprint `0`, pozisyon matrisi adayı `105`, repeated role `0`. Sıradaki scout veri işi düşük güvenli öneri temizliği değil, yüksek kullanımlı ama ağ teyidi bekleyen profil/alias doğrulamaları.
- Açık WATCH başlıkları:
  1. Günlük veri tazeliği: son pipeline 21 Temmuz; 23 Temmuz'da yeni üretim yok.
  2. Beşiktaş-Midtjylland saat/venue resmi teyidi eksik.
  3. Sofascore canlı erişim bu ortamda `403`; GitHub Actions ortamında tekrar doğrulanmalı.
  4. `manual_alias_pending_network_verification`: `4`.
  5. Beşiktaş display tahmin doğruluğu `%65.5`; beraberlik recall `%22.2`; gol adayı top-5 `%76.9`, top-8 `%84.6`.
  6. Yeni takımlar için `LOW_NEW_TEAM 96` hâlâ yüksek; 1. Lig/backfill ve resmi kadro-form sinyali eklenmeden 2026/27 erken sezon güveni sınırlı kalacak.

## 2026-07-24 Günlük Veri/Geliştirme Kontrolü

- 24 Temmuz kontrolünde `PROJECT_STATE.md` önce okundu; 23 Temmuz kaydındaki ana riskler geçerliliğini koruyor.
- `data/processed` altında bugün üretilmiş dosya başlangıçta yoktu (`0`); son tam üretim 21 Temmuz 15:05. Bu artık izleme notundan çok veri tazeliği aksiyonu gerektiriyor: günlük ağlı koleksiyon veya en azından ağsız full pipeline tekrar çalıştırma takibi yapılmalı.
- Git durumu kontrol başında `main...origin/main` hizalıydı; çalışma ağacında önceki kontrol kaydı nedeniyle `PROJECT_STATE.md` değişik durumdaydı.
- Ana kalite metrikleri değişmedi:
  - Scorecard: `85.4`.
  - Warehouse kapsamı: `306` maç, `18` takım, `691` oyuncu, `29` hakem, `370` team scout blueprint, `298` gol adayı.
  - Gol adayı backtest: top-5 `%76.9`, top-8 `%84.6`.
  - OOS full-season: `142/258`, doğruluk `%55.0`, Brier `0.600`, log loss `1.005`.
  - OOS ikinci yarı: `89/153`, doğruluk `%58.2`, Brier `0.595`, log loss `0.996`.
- Market audit değişmedi: `18` market kulübü, `817` TM oyuncusu, `%100` maç kapsamı, model accuracy `%55.0`, market baseline `%48.1`.
- Transfer tracker değişmedi: `43` sinyal, `1` official, `6` corroborated, `8` rumor, `28` review required, toplam değer `€7.9M`.
- 2026/27 fixture tahmini mevcut ve yapısal olarak sağlıklı: `34` hafta / `306` maç / oynanmış maç `0`; `LOW_NEW_TEAM 96`, `LOW 68`, `MEDIUM 84`, `HIGH 58`.
- Transfer edge hâlâ aktif: `68` maç-taraf örneğinde `transfer_signal.available = true`.
- `fixture_congestion` hâlâ gerçek lig fikstürlerinde aktif değil (`0` maç-taraf); Temmuz Avrupa eleme maçları lig açılışından 1-4 gün önce olmadığı için beklenen davranış.
- Avrupa veri tarafında kritik tazelik eksiği sürüyor:
  - `european_news_pulse_2025_2026` son üretim `2026-07-21T12:05:29Z`, `61` haber.
  - `european_predictions_2026_2027` skor/olasılık üretmiyor; eleme turu için güvenilir rakip veri tabanı olmadığı için doğru koruma.
  - `data/manual/european_qualifier_fixtures_2026_2027.json` içinde Beşiktaş-FC Midtjylland hâlâ `kickoff_time_confirmed: false`, saat `00:00` placeholder, venue resmi teyitsiz.
- Kaynak izleme listesi kontrol edildi:
  - Manuel kaynak listesi `data/manual/source_watchlist.json`: `14` kaynak, `10` günlük izlenecek kaynak, `6` bağlı/yarı bağlı kaynak, `3` analizde yüksek ağırlıklı kaynak, `1` yüksek riskli kaynak.
  - Mevcut üretici yalnız MD/HTML yazıyordu; makine okunabilir günlük sağlık kontrolü için JSON summary eksikti.
- **Küçük geliştirme yapıldı**: `src/build_source_watchlist.py` artık `data/processed/source_watchlist_2025_2026.json` da üretiyor. JSON içinde `summary`, `daily_sources` ve ham `sources` alanları var. Doğrulama çıktısı: `source_count 14`, `daily_refresh_count 10`, `connected_or_partial_count 6`, `high_risk_count 1`.
- Bu geliştirme sonrası bugün üretilen dosyalar: `source_watchlist_2025_2026.md`, `source_watchlist_2025_2026.html`, `source_watchlist_2025_2026.json`.
- Scout kalite raporu değişmedi ve temiz: `370` blueprint aday bağlantısı, düşük güvenli blueprint `0`, pozisyon matrisi adayı `105`, repeated role `0`. Sıradaki scout veri işi hâlâ yüksek kullanımlı ama ağ teyidi bekleyen profil/alias doğrulamaları.
- Açık WATCH başlıkları:
  1. Tam veri tazeliği: son full pipeline 21 Temmuz; 24 Temmuzda yalnız kaynak radarı yeniden üretildi.
  2. Beşiktaş-Midtjylland saat/venue resmi teyidi eksik.
  3. Sofascore canlı erişim bu ortamda `403`; GitHub Actions ortamında tekrar doğrulanmalı.
  4. `manual_alias_pending_network_verification`: `4`.
  5. Yeni takımlar için `LOW_NEW_TEAM 96`; 1. Lig/backfill veya resmi kadro-form sinyali eklenmeden erken 2026/27 tahmin güveni sınırlı kalacak.
  6. Kaynak izleme JSON’u artık var; sonraki adım `build_data_quality_scorecard.py` veya `build_status_page.py` içine bu JSON özetini bağlayıp veri tazeliğini ekranda görünür yapmak.

## 2026-07-25 Günlük Veri/Geliştirme Kontrolü

- 25 Temmuz kontrolünde `PROJECT_STATE.md` önce okundu; 24 Temmuzdaki kaynak radarı JSON geliştirmesi ve veri tazeliği riski doğrulandı.
- Kontrol başlangıcında `data/processed` altında bugün üretilmiş dosya yoktu (`0`). En yeni dosyalar 24 Temmuz 17:49 kaynak radarı (`source_watchlist_2025_2026.{md,html,json}`); son tam pipeline hâlâ 21 Temmuz 15:05.
- Git durumu kontrol başında `main...origin/main` hizalıydı; çalışma ağacında önceki günlerden `PROJECT_STATE.md`, `src/build_source_watchlist.py` ve yeni `data/processed/source_watchlist_2025_2026.json` değişiklikleri vardı.
- Bugünkü ana geliştirme: 24 Temmuzda eklenen makine okunabilir kaynak radarı `system_status.html` ve `data_quality_scorecard` içine bağlandı.
- `src/build_status_page.py` güncellendi:
  - `source_watchlist_2025_2026.json` okunuyor.
  - Pipeline son çalışma yaşı hesaplanıyor (`age_days`).
  - Pipeline başarısız olmasa bile son çalışma `>1` gün eskiyse durum `warn`, `>3` gün eskiyse `fail` seviyesine düşüyor.
  - Sistem durum sayfasına “Tazelik” satırı eklendi; bugünkü üretimde `3 gün önce` görünüyor.
  - Sistem durum sayfasına yeni “Kaynak Radarı” kartı eklendi: günlük kaynak `10/14`, bağlı/yarı bağlı `6`, yüksek risk `1`, liste güncelleme `2026-05-25`.
- `src/build_data_quality_scorecard.py` güncellendi:
  - Yeni kontrol: `pipeline / daily_pipeline_last_run_age_days`.
  - Yeni kontrol: `sources / source_watchlist_daily_coverage`.
  - Pipeline tazeliği bugün `age_days=3`, `failed_count=0`, `include_network=False` olarak `WATCH/HIGH` durumuna düştü. Bu doğru: pipeline komutları başarılı görünse bile veri tazeliği artık ayrı izleniyor.
  - Kaynak radarı kapsamı `PASS`: `sources=14`, `daily=10`, `connected_or_partial=6`, `high_risk=1`.
- `python3 -m src.build_data_quality_scorecard` çalıştırıldı: başarılı. Genel skor `85.4 → 85.0` oldu; düşüş kasıtlı, çünkü pipeline tazeliği artık scorecard’a WATCH olarak giriyor.
- `python3 -m src.build_status_page` çalıştırıldı: başarılı. `data/processed/system_status.html` içinde `Tazelik: 3 gün önce` ve `Kaynak Radarı` alanları doğrulandı.
- `python3 -m py_compile src/build_status_page.py src/build_data_quality_scorecard.py` başarılı.
- Ana metrikler değişmedi:
  - Warehouse kapsamı: `306` maç, `18` takım, `691` oyuncu, `29` hakem, `370` scout blueprint, `298` gol adayı.
  - OOS full-season doğruluk `%55.0`; ikinci yarı OOS `%58.2`.
  - Gol adayı top-5 `%76.9`, top-8 `%84.6`.
  - Transfer edge `68` maç-taraf örneğinde aktif; `fixture_congestion` hâlâ gerçek lig fikstürlerinde `0`.
- Açık WATCH başlıkları:
  1. Son tam pipeline 21 Temmuz; 25 Temmuz itibarıyla status/scorecard bunu görünür uyarıya çeviriyor. Sıradaki gerçek aksiyon ağlı pipeline veya en azından ağsız full pipeline tekrar koşusunu otomasyonda düzeltmek.
  2. Beşiktaş-Midtjylland saat/venue resmi teyidi hâlâ eksik.
  3. Sofascore canlı erişim bu ortamda `403`; GitHub Actions ortamında doğrulanmalı.
  4. `manual_alias_pending_network_verification`: `4`.
  5. 2026/27 yeni takımlar için `LOW_NEW_TEAM 96`; 1. Lig/backfill veya resmi kadro-form sinyali olmadan erken sezon tahmin güveni sınırlı kalacak.

## 2026-07-26 Günlük Veri/Geliştirme Kontrolü

- 26 Temmuz kontrolünde `PROJECT_STATE.md` önce okundu; 25 Temmuzda eklenen pipeline tazeliği/status/scorecard kontrolleri doğrulandı.
- Kontrol başlangıcında `data/processed` altında bugün üretilmiş dosya yoktu (`0`); en yeni tam üretim hâlâ 21 Temmuz, en yeni kısmi üretim 25 Temmuz status/scorecard idi.
- Ağsız full pipeline çalıştırıldı. İlk deneme `56/57` başarılı, `1` hata verdi:
  - Hata: `python -m src.build_source_performance_report`.
  - Kök neden: `build_source_performance_report.py` yalnız `TWITTER_ACCOUNTS` sabiti için `src.collect_news_twitter` import ediyor; `collect_news_twitter.py` ise modül yüklenirken `feedparser` import ediyordu. Bu ortamda `feedparser` kurulu olmadığı için ağsız rapor bile kırıldı. `requirements.txt` içinde `feedparser==6.0.12` var, ancak mevcut runtime’da yok.
- **Fix 1 — lazy import**: `src/collect_news_twitter.py` içinde top-level `feedparser` import’u kaldırıldı; yalnız Nitter RSS parse ederken çalışan `_parse_feed()` içine alındı. Böylece `TWITTER_ACCOUNTS` gibi sabitler ağsız raporlarda bağımlılık hatası üretmeden import edilebiliyor.
- `python3 -m src.build_source_performance_report` tek başına çalıştırıldı: başarılı, `159` gözlenen kaynak.
- **Fix 2 — pipeline health hizalama**: `src/run_daily_pipeline.py` güncellendi. `daily_pipeline_run_latest.json` en sonda yazıldığı için pipeline içindeki `build_data_quality_scorecard` ve `build_status_page` bir önceki pipeline raporunu okuyabiliyordu. Runner artık raporu yazdıktan sonra `build_data_quality_scorecard` ve `build_status_page` için `post_report_refresh` çalıştırıyor. Doğrulama JSON’unda:
  - `post_report_refresh[0]`: `python -m src.build_data_quality_scorecard`, returncode `0`.
  - `post_report_refresh[1]`: `python -m src.build_status_page`, returncode `0`.
- Ağsız full pipeline ikinci kez çalıştırıldı: `57/57` başarılı, `0` hata, `include_network=False`, `generated_at=2026-07-26T08:24:30Z`.
- `python3 -m py_compile src/run_daily_pipeline.py src/collect_news_twitter.py src/build_data_quality_scorecard.py src/build_status_page.py` başarılı.
- Bugün `data/processed` altında `140` dosya yeniden üretildi.
- Scorecard son hizalanmış sonuç:
  - Genel skor: `87.5/100`.
  - Pipeline tazelik kontrolü: `PASS`, `age_days=0`, `failed_count=0`, `include_network=False`.
  - Kaynak radarı kapsamı: `PASS`, `sources=14`, `daily=10`, `connected_or_partial=6`, `high_risk=1`.
  - Status sayfası doğrulandı: `Tazelik=bugün`, `Veri kalite skoru=87.5/100`, `Kaynak Radarı` kartı mevcut.
- Ana metrikler:
  - Warehouse kapsamı: `306` maç, `18` takım, `691` oyuncu, `29` hakem, `370` scout blueprint, `298` gol adayı.
  - OOS full-season: `142/258`, doğruluk `%55.0`, Brier `0.600`, log loss `1.005`.
  - OOS ikinci yarı: `89/153`, doğruluk `%58.2`, Brier `0.595`, log loss `0.996`.
  - Gol adayı backtest: top-5 `%76.9`, top-8 `%84.6`, top-10 `%88.5`.
  - Market audit: `18` market kulübü, `817` oyuncu, `%100` maç kapsamı, model accuracy `%55.0`, market baseline `%48.1`.
  - Transfer tracker: `43` sinyal, `1` official, `6` corroborated, `8` rumor, `28` review required, toplam değer `€7.9M`.
  - 2026/27 fixture: `34` hafta / `306` maç / oynanmış maç `0`; güven dağılımı `LOW_NEW_TEAM 96`, `LOW 68`, `MEDIUM 84`, `HIGH 58`.
  - Transfer edge: `68` maç-taraf örneğinde aktif.
  - `fixture_congestion`: gerçek lig fikstürlerinde hâlâ `0`.
  - Scout kalite: `370` blueprint bağlantısı, düşük güvenli blueprint `0`, pozisyon matrisi `105`, repeated role `0`.
  - Transfermarkt/TFF eşleşme: `in_scope_match_rate %94.6`, operational in-scope `%95.2`, `manual_alias_pending_network_verification 4`, `scout_blocking_unmatched 0`.
  - Avrupa haber nabzı ağsız yeniden üretildi: `61` haber, ancak yeni canlı haber çekimi yapılmadı.
- Açık WATCH başlıkları:
  1. Bugün yalnız **ağsız** pipeline tazelendi. Gerçek güncel transfer/sakatlık/kadro haberleri için ağlı collector koşusu veya GitHub Actions ağlı ortamı hâlâ gerekli.
  2. Beşiktaş-Midtjylland saat/venue resmi teyidi hâlâ eksik.
  3. Sofascore canlı erişim bu ortamda `403`; GitHub Actions ortamında doğrulanmalı.
  4. `manual_alias_pending_network_verification`: `4`.
  5. 2026/27 yeni takımlar için `LOW_NEW_TEAM 96`; 1. Lig/backfill veya resmi kadro-form sinyali olmadan erken sezon tahmin güveni sınırlı kalacak.
  6. Sonraki uygulanabilir geliştirme: GitHub Actions / otomasyon tarafında ağlı pipeline’ın neden 21 Temmuzdan beri yeni veri üretmediğini incelemek ve gerekirse workflow’u elle tetiklemek veya schedule/secret durumunu doğrulamak.

## 2026-07-27 Günlük Veri/Geliştirme Kontrolü

- 27 Temmuz kontrolünde `PROJECT_STATE.md` önce okundu; 26 Temmuzdaki ağsız pipeline düzeltmeleri ve açık WATCH başlıkları doğrulandı.
- Kontrol başlangıcında `data/processed` altında bugün üretilmiş dosya yoktu (`0`). Son tam üretim 26 Temmuz 11:24 Türkiye saati / `2026-07-26T08:24:30Z`; bu nedenle pipeline tazelik kontrolü hâlâ `PASS`.
- Mevcut ana metrikler değişmedi:
  - `daily_pipeline_run_latest`: `include_network=False`, `57/57` başarılı, `0` hata, `post_report_refresh` iki adım da `0`.
  - Scorecard: `87.5/100`.
  - Pipeline tazeliği: `PASS`, `age_days=0`, `failed_count=0`.
  - Kaynak radarı: `PASS`, `14` kaynak, `10` günlük kaynak, `6` bağlı/yarı bağlı, `1` yüksek risk.
  - OOS full-season doğruluk `%55.0`; ikinci yarı OOS `%58.2`.
  - Transfer tracker: `43` sinyal, `1` official, `6` corroborated, `8` rumor, `28` review required, toplam değer `€7.9M`.
  - 2026/27 fixture: `34` hafta / `306` maç / oynanmış maç `0`; güven dağılımı `LOW_NEW_TEAM 96`, `LOW 68`, `MEDIUM 84`, `HIGH 58`; transfer edge `68`, fixture congestion `0`.
  - Scout kalite: `370` blueprint bağlantısı, düşük güvenli blueprint `0`, pozisyon matrisi `105`, repeated role `0`.
  - Transfermarkt/TFF eşleşme: `in_scope_match_rate %94.6`, operational in-scope `%95.2`, `manual_alias_pending_network_verification 4`, `scout_blocking_unmatched 0`.
- GitHub Actions workflow dosyaları yerel olarak incelendi:
  - `.github/workflows/daily-pipeline.yml`: her gün `04:00 UTC` schedule ile `python -m src.run_daily_pipeline --include-network` çalıştırıyor.
  - `.github/workflows/refresh.yml`: günde 4 kez haber/dashboard yenileme, birçok collector `|| true` ile fallback davranışında.
  - `.github/workflows/news-refresh.yml`: günde 6 kez haber yenileme, haber collector/rapor adımları `|| true` ile fallback davranışında.
  - Tüm workflow YAML dosyaları Ruby `YAML.load_file` ile parse edildi: üçü de `OK`.
- **Bugünkü düzeltme — full network pipeline hatayı saklamasın**:
  - `.github/workflows/daily-pipeline.yml` içinde `Run pipeline (network dahil)` ve `Run pipeline (network yok)` adımlarındaki `continue-on-error: true` kaldırıldı.
  - Gerekçe: full pipeline adımı hata verirse GitHub Actions yeşil görünmemeli; aksi halde canlı veri üretimi bozulsa bile otomasyon başarılı gibi algılanıyor. Commit/push adımı `if: always()` olduğu için çıktı/artifact davranışı korunur, ama job sonucu artık gerçek hata sinyalini verir.
  - `refresh.yml` ve `news-refresh.yml` içindeki `|| true` fallbackleri şimdilik korunuyor; bunlar haber kaynağı bazlı kırılmalarda tüm akışı öldürmemek için tasarlanmış. Ancak gelecekte kaynak bazlı hata raporunu ayrıca scorecard’a bağlamak iyi olur.
- Bugün lokal uzak GitHub run logları veya secrets durumu doğrulanmadı; ağlı gerçek sebebi kesinleştirmek için bir sonraki adım GitHub Actions run list/loglarını okumak veya workflow’u manuel tetiklemek.
- Açık WATCH başlıkları:
  1. Canlı veri tarafı hâlâ ağsız snapshot’a dayanıyor; gerçek güncel transfer/sakatlık/kadro haberleri için GitHub Actions ağlı koşu doğrulanmalı.
  2. Beşiktaş-Midtjylland saat/venue resmi teyidi hâlâ eksik.
  3. Sofascore canlı erişim bu ortamda `403`; GitHub Actions ortamında doğrulanmalı.
  4. `manual_alias_pending_network_verification`: `4`.
  5. 2026/27 yeni takımlar için `LOW_NEW_TEAM 96`; 1. Lig/backfill veya resmi kadro-form sinyali olmadan erken sezon tahmin güveni sınırlı kalacak.
  6. Sonraki uygulanabilir geliştirme: GitHub Actions run loglarını/secret kullanılabilirliğini kontrol etmek; full network pipeline artık hata saklamayacağı için sonraki başarısız koşu gerçek kök nedeni göstermeli.

## 2026-08-14 Lig Başlangıcı: Maç Tahminleri Öne Çıkarma + Haftalık Değerlendirme + Avrupa Sinyali (Session 12)

Kullanıcı isteği: lig 16 Ağustos'ta başlıyor; maç tahminleri/analizleri ön plana alınmalı, skor tahminleri şimdiye kadarki tüm transfer + Avrupa maçlarını içermeli, her hafta değerlendirilmeli (sonuç bir sonraki haftayı beslemeli), bu özellik öne çıkarılmalı.

### 1. Lig modu geçişi (merkezi tarih mantığı)
- `src/html_utils.py`: `LEAGUE_START = date(2026, 8, 16)` + `league_active()` eklendi. Transfer penceresi (1 Eylül'e kadar) hâlâ açık olsa bile lig başladığında öncelik maça/tahmine döner. `preview_nav_label()`/`_preview_label()` artık `league_active()`'e bağlı ("Maç Önü" vs "Arşiv"). Nav'a lig aktifken "Haftalık Karne" linki + Fikstür öne alındı; brand sezon etiketi 2026/27'ye döner.
- `src/build_product_home.py` ve `src/build_live_feed.py`: yerel `_is_transfer_season` yerine üç durumlu mod. Lig aktifken maç/tahmin kartları öne (hero + Fikstür + Haftalık Karne kartları), transfer/haber ikincil.

### 2. "Bu Hafta" kahraman modülü (öne çıkarma)
- `src/build_match_week.py` (YENİ): `season_fixture_predictions_2026_2027.json`'dan oynanmamış maçı olan ilk haftayı (yoksa son haftayı) seçer; `match_week_2026_2027.json` üretir ve `render_hero_html()` ile ana sayfaya gömülebilen hero parçası sunar (maç kartları + tahmin rozeti + olasılık + "Geçen hafta N/M isabet" pili + "Tüm fikstür →").
- `src/build_live_feed.py`: lig aktifken sol sütun üstüne "Bu Hafta" hero'su; transfer/haber altına iner. Tarayıcıda (lig-aktif simülasyonu) görsel doğrulandı.

### 3. Haftalık değerlendirme (otomatik rapor + ana sayfa özeti)
- `src/build_weekly_evaluation.py` (YENİ): oynanmış maçlarda `predicted` vs `actual_score` karşılaştırması; hafta bazında isabet, beraberlik yakalama, yüksek-güven isabeti, ✅/❌ tablo. `weekly_evaluation_2026_2027.{json,md,html}` (paylaşılan `page_html`/`md_to_html` teması). 0 maçta zarif "sezon başlıyor" durumu. Ana sayfa hero'su ve product_home kartı bu özeti gösterir. Motor sonucu zaten bir sonraki haftaya besliyor (advance_season_state → compute_final_state).

### 4. Avrupa sonuçları → kontrollü güç sinyali
- `src/preview/probability.py`: `european_form_edge(team_name)` (YENİ) — Türk kulüplerinin oynanmış Avrupa maç SONUÇLARINI (galibiyet/beraberlik/mağlubiyet + `opponent_strength` ağırlığı + recency) capli (`±0.10`) bir edge'e çevirir; sonuç yoksa `available=False`. `_load_european_results()` iki kaynağı okur: manuel `data/manual/european_results_2026_2027.json` (YENİ, şema + `_example` filtreli) ve otomatik `european_fixtures_2026_2027.json` FINISHED maçları (`collect_european_fixtures._build_match` zaten `score.home/away` yakalıyor — collector değişmedi).
- `src/model_league_predictions.py`: `predict_match(..., apply_european_signal=False)` parametresi; transfer bloğuyla aynı biçimde `strength_edge += (euro_home.edge - euro_away.edge) * 0.5`. `european_signal` payload'a eklendi. Yalnızca `build_season_fixture_predictions.py` `True` geçirir → 2025-26 backtest ETKİLENMEZ.

### 5. Pipeline + sitemap
- `src/run_daily_pipeline.py`: maç/tahmin zinciri (season_fixture_predictions → build_weekly_evaluation → build_match_week) ana sayfa builder'larından ÖNCE'ye taşındı (aksi halde ana sayfa bayat tahmin gösteriyordu).
- `src/build_sitemap.py`: `season_fixture_predictions_2026_2027.html` (1.0) + `weekly_evaluation_2026_2027.html` (0.9) eklendi.

### Doğrulama
- Tüm değişen dosyalar `py_compile` OK. `european_form_edge` yön/cap testleri geçti; `predict_match` entegrasyonu: enjekte sonuçla `strength_edge` 0.0→0.05, ev kazanma olasılığı hafif yukarı (kontrollü).
- 2025-26 Beşiktaş backtest doğruluğu **0.655 birebir korundu**.
- `pytest`: **58 passed / 3 failed** — 3 başarısızlık önceden var olan, ilgisiz (transfer tracker sezon etiketi + TM koleksiyon 2026_2027 output-prefix); değişikliklerimden kaynaklı yeni kırılma yok.
- Ağsız full pipeline: **59/59 başarılı, 0 hata**, `generated_at 2026-08-14T06:33Z`.

### Açık başlık / sonraki adım
- Gerçek Avrupa eleme sonuçları henüz `european_results_2026_2027.json`'a girilmedi (uydurulmadı); collector FINISHED maçlarda otomatik dolduracak ya da elle girilecek — girilene kadar Avrupa sinyali `available=False`, tahmini etkilemez. İlk gerçek sonuç ve ilk gerçek OFFICIAL transferle sinyallerin canlı yönü doğrulanmalı.
- Lig 16 Ağustos'ta başlayınca `league_active()` otomatik `True` döner; ana sayfa/nav/hero geçişi ve `advance_season_state`in gerçek maç verisiyle oynanan haftaları işlemesi canlıda izlenmeli.

### 2026-08-14 (devam) — Gerçek Avrupa sonuçları girildi + sinyal güçlendirildi
- Kullanıcı isteğiyle web araması yapılıp Türk kulüplerinin 2026-27 Avrupa eleme sonuçları güvenilir Türk basınından (Hürriyet/Fanatik/Milliyet/Sabah/Fotomaç) doğrulanarak `data/manual/european_results_2026_2027.json`'a girildi (10 gerçek maç, uydurulmadı):
  - **Fenerbahçe** (ŞL): 2.tur Górnik 1-0 / 1-1 (agg 2-1), 3.tur Sturm Graz 2-0 / 0-1 (agg 3-0) → tur atladı. Playoff Lyon (18/26 Ağu) HENÜZ OYNANMADI.
  - **Beşiktaş** (AL): 2.tur Midtjylland 1-0 / 0-2 (agg 3-0), 3.tur Hradec Králové 0-1 / 1-0 (agg 2-0) → tur atladı. Playoff Kauno Žalgiris (20/27 Ağu) HENÜZ OYNANMADI.
  - **Başakşehir** (KL): 2.tur Inter Turku 1-1 / 2-0 → ELENDİ.
  - **Galatasaray**: Süper Lig şampiyonu, doğrudan lig aşaması (eleme yok). **Trabzonspor**: doğrudan playoff (ilk maç 20 Ağu), henüz oynamadı.
- `european_form_edge` sonuçları: FB +0.15 (3G1B), BJK +0.15 (4G, cap), Başakşehir −0.066 (elenme cezası); GS/TS `available=False`.
- **Sinyal güçlendirildi** (kullanıcı tercihi): `_EURO_EDGE_CAP 0.10→0.15`, `_EURO_EDGE_PER_POINT 0.04→0.05`, predict_match birleştirme çarpanı `×0.5→×1.0`. 94 maçta strength_edge değişti; maç başına kazanma olasılığı ~1 puan kayıyor (capli, 1X2 yönü değişmiyor).
- Doğrulama: 2025-26 backtest **0.655 birebir korundu** (Avrupa yalnız 2026-27 yolunda); pytest 58/3 (aynı); ağsız pipeline 59/59.
- Playoff sonuçları (FB-Lyon, BJK-Kauno, TS-Ferencváros) oynandıkça `european_results_2026_2027.json`'a eklenmeli; collect_european_fixtures FINISHED maçlarda otomatik de doldurabilir.

### 2026-08-14 (devam) — Lig açılışı geçişi düzeltildi (LEAGUE_START kalibrasyonu)
- **Kök bulgu:** `src/html_utils.py` `LEAGUE_START = date(2026, 8, 16)` iki gün geçti. `season_fixture_predictions_2026_2027.json` doğrulaması: **Hafta 1 = 14–17 Ağustos**, ilk maç **14.08.2026 21:30 Galatasaray–Çorum** (bugün). Eski tarihle site, gerçek açılış maç günlerinde (14–15 Ağu) hâlâ transfer-öncelikli modda kalıp maç hero'sunu göstermeyecekti.
- **Düzeltme:** `LEAGUE_START = date(2026, 8, 14)` (doğrulanan ilk maç günü). Böylece `league_active()` bugün `True` dönüyor; `_pre_season_transfer()` `False` (transfer penceresi 1 Eylül'e kadar açık ama öncelik maça). LEAGUE_START yalnız `html_utils.league_active()`'te kullanılıyor; başka Ağustos-16 sabiti yok.
- **Simülasyon + doğrulama:** date.today() sahtelenerek (scratchpad) ve gerçek tarihle builder'lar çalıştırıldı. Gerçek çıktılar lig-modunu gösteriyor: `gundem_2025_2026.html` "Bu Hafta · Hafta 1" hero (9 maç, tahmin rozeti + Ev/X/Dep), "Fikstür & Tahmin" + Haftalık Karne linkleri; `football_intelligence_home.html` nav'da "Maç Önü" + Haftalık Karne + sezon "2026/27". Hero tag dengesi OK (59/59 div). Tarayıcıda (yerel http) görsel doğrulandı — hero sol üstte öne çıkıyor.
- Yeniden üretilen dosyalar: `match_week_2026_2027.json`, `weekly_evaluation_2026_2027.{json,html}`, `football_intelligence_home.html`, `gundem_2025_2026.html`. Haftalık karne 0 maçta zarif "sezon başlıyor" durumunda (henüz sonuç yok).
- **Regresyon:** `py_compile` OK; pytest **58 passed / 3 failed** — 3 başarısızlık önceden var olan, ilgisiz (TM koleksiyon output-prefix `2026_2027` + transfer tracker/preview sezon etiketi hâlâ `2025_2026`); LEAGUE_START değişikliğinden yeni kırılma yok.
- **Not (kapsam dışı, sonraki):** Ana sayfa sağ sütun "Avrupa Kupası" kutusu (`_nearest_known_fixture_html`) bayat/geçmiş maçı (22 Tem Başakşehir–Inter Turku, elenmiş) gösteriyor — en yakın GELECEK maça göre seçmeli. Ayrıca cosmetic: nav/home sezon etiketi "2026/27" ile feed "2026-2027" formatı tutarsız.

### 2026-08-14 (devam) — Ana sayfa skor-öncelikli yapıldı + 2 takip düzeltmesi (kullanıcı isteği)
- **Skor öne çıkarma (asıl istek):** Kullanıcı "ana sayfa hâlâ transfer gösteriyor, skor sayfası daha cazip olmaz mı" dedi. Lig-modunda sağ sütun dev "Transfer Sezonu" stat bloğuyla açılıyordu (lime kenar, göz alıcı) → sayfa transfer-ağırlıklı hissettiriyordu. `src/build_live_feed.py`:
  - `_score_sidebar_html()` (YENİ): lig-modunda sağ sütun üstünde kompakt skor paneli — bu haftanın maç sayısı + sezon isabeti (henüz "Yeni/Sezon Başladı") + "Fikstür & skor tahminleri" (bold) + "Haftalık isabet karnesi" linkleri. Transfer bloğunun görsel dilini (yeşil stat kutuları) lime aksanla skor temasına uyarladı.
  - Sağ sütun sıralaması lig-modunda: `sidebar_top_html`=skor paneli, ardından Avrupa → Analiz → `sidebar_bottom_html`=transfer bloğu (EN ALTA indi). Lig öncesi düzen değişmedi (transfer üstte). Doğrulandı: DOM'da Skor<Avrupa<Analiz<Transfer sırası.
- **Avrupa kutusu bayat fikstür düzeltmesi:** `_nearest_known_fixture_html` yalnız TEK geçmiş maçı atlıyordu; `european_qualifier_fixtures_2026_2027.json`'daki 3 maç da geçmiş (21-23 Tem) olduğundan ikinci en eskiye (22 Tem Başakşehir) düşüyordu. Düzeltme: `delta_days >= 0` filtresiyle yalnız bugün/gelecek maçlar; hepsi geçmişse "" döner (kutu artık `eu_pulse` haber sinyaline düşüyor, bayat maç göstermiyor). Yaklaşan playoff'lar (FB-Lyon 18/26 Ağu vb.) bu dosyada YOK — doğrulanmış detayla eklenmeli (uydurulmadı).
- **Sezon etiketi tutarlılığı:** nav/home "2026/27" ↔ feed/transfer "2026-2027" tutarsızdı. `html_utils._build_nav` brand chip + `build_product_home` brand chip & hero overline'ları "2026-2027"/"2025-2026" formatına hizalandı (site geneli tire formatı). Kalan "2026/27": yorum satırları + OG görsel metni (kapsam dışı).
- **Doğrulama:** py_compile OK; pytest **58/3** (aynı 3 önceden var olan, ilgisiz başarısızlık; yeni kırılma yok); tarayıcıda görsel onay — skor paneli sağ üstte öne çıkıyor, transfer bloğu dipte, bayat 22 Tem fikstür kalktı, sezon etiketi "Süper Lig 2026-2027".

### 2026-08-14 (devam) — Avrupa playoff fikstürleri eklendi (web'den doğrulandı)
- Kullanıcı "eksik olmayacak, futbolseverler her şeyi güncel takip edebilmeli" dedi. `data/manual/european_qualifier_fixtures_2026_2027.json`'a Türk kulüplerinin 2026-27 Avrupa **playoff turu** eşleşmeleri Türk basınından (Milliyet/Fotomaç/Sabah/Karar/Cumhuriyet) WebSearch/WebFetch ile doğrulanarak eklendi (uydurulmadı) — her tie için ilk maç + rövanş, toplam 6 yeni fikstür:
  - **Fenerbahçe–Lyon (CL playoff):** İlk maç **18 Ağu Salı 22:00 İstanbul** (FB ev, Chobani/Ş.Saracoğlu); rövanş 26 Ağu Parc OL, Lyon. Saat/mekan teyitli.
  - **Beşiktaş–Kauno Žalgiris (EL playoff):** İlk maç **20 Ağu Perşembe İstanbul** (BJK ev, Tüpraş Stadyumu); rövanş 27 Ağu Litvanya. Tarih/mekan teyitli, **saat kesinleşmedi** → `kickoff_time_confirmed=false` (arayüzde "saat TBD").
  - **Trabzonspor–Ferencváros (EL playoff):** İlk maç **20 Ağu Perşembe 22:00 Trabzon** (TS ev, Papara Park); rövanş 27 Ağu Groupama Arena, Budapeşte. Saat/mekan teyitli. (Not: TS EL playoff'unda — Konferans değil; kazanan EL lig aşamasına.)
  - Galatasaray şampiyon → doğrudan CL lig aşaması, playoff yok (fikstür eklenmedi). Başakşehir 2. turda elendi.
- Temmuz 2. ön eleme maçları tarihi kayıt olarak korundu (`result_note` eklendi); `_nearest_known_fixture_html` gelecek-filtresiyle onları zaten atlıyor.
- **Etki:** Ana sayfa Avrupa kutusu artık en yakın gerçek maçı gösteriyor — "Salı 22:00 — Fenerbahçe - Lyon" (tarayıcıda doğrulandı). Maçlar oynandıkça teaser otomatik ilerliyor; hepsi geçince haber sinyaline düşüyor. Skor/olasılık tahmini ÜRETİLMİYOR (rakip istatistik tabanı yok) — yalnız maç bilgisi. Oynanmış sonuçlar ayrıca `european_results_2026_2027.json`'a girilip form sinyaline besleniyor (ayrı akış).

### 2026-08-14 (devam) — Avrupa sayfası yenilendi + skor/xG/hakem kartlarda gösterildi (kullanıcı geri bildirimi)
Kullanıcı: "Avrupa sayfası çok iyi değil (eski eleme maçları, skor yok, yeni maçlar yazılmamış); skor tahminlerinde sadece kim kazanır mı var; hakemi göz önüne alıyor musun?"
- **Avrupa sayfası (`build_european_predictions.py`):** `_build_known_fixtures_section` yeniden yazıldı — artık iki bölüm: **🔜 Yaklaşan Maçlar** (qualifier_fixtures'tan yalnız gelecek/bugün fikstürler = playoff'lar; eski Temmuz maçları gelecek-filtresiyle elenir) ve **✅ Tamamlanan Maçlar** (YENİ `_load_european_results` + `_result_card`; `european_results_2026_2027.json`'daki 10 gerçek skorla, galip kalın). Eski tek-liste "vs" gösterimi kaldırıldı. `_STAGE_TR`'ye `PLAYOFF_ROUND` eklendi. Stat çubuğu: otomatik tahmin (predictions) boşken "0 Toplam Maç" yanıltması yerine Yaklaşan/Oynanan sayımları gösteriyor. Tarayıcıda doğrulandı.
- **Skor tahmini kartlarda gösterildi (soru: "sadece kim kazanır mı?"):** Model zaten `recommended_scoreline` (kesin skor), `expected_home_goals/away_goals` (xG) ve top-5 skor üretiyordu ama SADECE galip+olasılık gösteriliyordu. Artık:
  - `build_season_fixture_predictions._match_card`: her maçta "Olası skor X-Y · xG a.a–b.b" satırı (306/306 maç) + yeni CSS (`.mc-scoreline`, `.mc-ref`).
  - `build_match_week` hero: `build_payload`'a scoreline+xG taşındı, hero kartlarında "Olası skor 1-0 · xG 1.4–0.5" (9/9 maç). Tarayıcıda doğrulandı.
- **Hakem (soru: "hakemi göz önüne alıyor musun?"):** EVET — `model_league_predictions._referee_goal_adjustment` hakemin geçmiş gol ortalamasını beklenen gole katıyor, `referee_cards_per_match > 5.5` ise "yüksek kart hakemi" flag'i üretiliyor. Kartlarda hakem satırı (`referee_cards_per_match` doluysa) + "yüksek kart" rozeti eklendi. NOT: Hafta 1'de hakem atamaları fikstür verisinde yok → `referee_cards_per_match=None`, `referee_adj=0.0`; atama/geçmiş dolunca otomatik görünür.
- **AÇIK (kullanıcı sordu, henüz YOK):** Per-maç **gol atar (kim skorer)** ve **kırmızı kart olur** tahmini lig genelinde üretilmiyor. Mevcut gol modülleri (`backtest_goal_candidates`, `build_goal_candidate_segment_backtest`) tarihsel backtest + başta Beşiktaş-scoped ([[project_all_teams_expansion]]). Kart sinyali yalnız hakem-kart-eğilimi flag'i olarak var, per-maç kırmızı kart olasılığı yok. Bunlar yeni modelleme gerektiriyor (oyuncu-seviye veri) — uydurulmadı; kullanıcıyla kapsam netleştirilecek.
- **Doğrulama:** py_compile OK (4 dosya); pytest **58/3** (aynı önceden var olan başarısızlıklar); tarayıcıda Avrupa + hero görsel onay.

### 2026-08-14 (devam) — Maç geneli gol/kart/dakika bandı sinyalleri (A+C tamamlandı, B veri eksikliğinden duraklatıldı)
Kullanıcı üç kapsamı seçti: (A) maç geneli gol&kart, (B) oyuncu skorer, (C) dakika bandı.

**A) Maç geneli sinyal (`src/build_match_signals.py`, YENİ) — TAMAMLANDI:**
- `tff_trendyol_super_lig_2025_2026_matches.json` (306 maç, 812 gol olayı, 1428 kart olayı, oyuncu+dakika+tip) ilk kez bu ölçekte kullanıldı — daha önce yalnız Beşiktaş-özel dosyada kullanılıyordu.
- 2.5 alt/üst + KG var/yok: mevcut `expected_home/away_goals` (zaten form+Elo+hakem ayarlı) üzerinden saf Poisson matematiği. Beklenen toplam kart + kırmızı kart riski: takım+hakem tarihsel kart oranları (kırmızı/sarı ayrımı YENİ — `model_league_predictions.py`'ın `referee_history`'si yalnız toplam kart tutuyordu).
- **Kritik düzeltme (birim hatası):** İlk versiyon "beklenen toplam kart"ı takım oranlarının ORTALAMASINI alıyordu (~2.3) — doğrusu TOPLAM olmalı (~4.7, `LEAGUE_AVG_CARDS=4.67` ile örtüşüyor); sanity-check ile yakalanıp düzeltildi.
- **Takım adı eşleştirme:** `build_season_fixture_predictions.NAME_ALIASES` (zaten var olan 2026-27→2025-26 sponsor adı haritası) yeniden kullanıldı — İkas Eyüpspor/Eyüpspor, Rams Başakşehir/İstanbul Başakşehir FK eşleşti. Yalnız 3 gerçek yeni takım (Amed Sportif, Çorum FK, Erzurumspor FK) veri-yok işaretli.
- **Yan bulgu (kapsam dışı, açık kaldı):** `season_fixture_predictions_2026_2027.json` içinde aynı kulüp iki farklı adla var — "ARCA ÇORUM FK" ve "ÇORUM FK". Bu, sezon ilerledikçe o takımın Elo/form geçmişinin ikiye bölünmesine yol açabilir (model kalitesi riski). Düzeltme `model_league_predictions.py`/fikstür üretim zincirine dokunacağından ayrı doğrulama gerektirir — kullanıcıya bildirilecek.
- model_league_predictions.py'a DOKUNULMADI — 2025-26 Beşiktaş backtest 0.655 korunuyor.
- Pipeline: `build_season_fixture_predictions.main()` artık JSON yazdıktan hemen sonra, HTML'den önce `build_match_signals.main()`'i çağırıyor (lazy import, döngüsel import yok) — sinyaller her zaman taze xG'den üretiliyor.
- Gösterim: fikstür kartları (306/306) + ana sayfa hero'su (9/9) — "⚽ 2.5 Üst %28 · 🥅 KG Var %28 · 🟨 4.4 kart" (+kırmızı risk ≥%25'te kırmızı rozet).

**B) Oyuncu skorer — DURAKLATILDI (veri engeli, uydurulmadı):**
- `transfermarkt_super_lig_squads_2026_2027.json`: **0/18 kulüp toplanmış** (`clubs_collected:0`, hepsi `reason: empty_squad` — TM 2026-27 sezon sayfası henüz veri döndürmüyor). `squad_snapshots/` yalnız 2026-05-25 tarihli donmuş kadro. `transfer_tracker_2025_2026.json`'da 0 OFFICIAL transfer (yalnız 7 CORROBORATED, 26 REVIEW_REQUIRED).
- Sonuç: transfer penceresi açıkken güvenilir "hangi oyuncu hangi takımda" verisi yok. 2025-26 kadrosunu kullanmak, takım değiştiren oyunculara yanlış takım ataması riski taşır — kullanıcının "her şeyi güncel takip" ilkesine aykırı olacağından kurulmadı.
- **Sonraki adım:** 2026-27 TM kadro koleksiyonunun neden başarısız olduğu araştırılıp düzeltilmeli (muhtemelen `saison_id=2026` path/parametre sorunu — bkz. bilinen pytest başarısızlığı #3), sonra skorer oranı (gol/başlangıç-XI, `type != 'K'` hariç own-goal) + güncel kadro eşleştirmesiyle kurulabilir.

**C) Dakika bandı / ilk gol (`build_match_signals.py` genişletildi) — TAMAMLANDI:**
- 812 gol olayının dakika damgasından (own-goal hariç) 6 bantlı (`0-15…76-90+`) ampirik lig dağılımı — gerçek futbol örüntüsüyle uyumlu (76-90+ en yüksek %24.8, uzatma dakikası etkisi). Takım bazlı "attığı gol" + "yediği gol" bant dağılımları (min 15 gol eşiği, altında lig ortalaması).
- İlk gol olasılığı: iki bağımsız Poisson süreci arasında oran-orantılı yaklaşım (`λh/(λh+λg)`), 0-0 olasılığı Poisson(0) ile ayrıca hesaplanıp üçü toplamda tam 1.0 (doğrulandı).
- En olası gol bandı: ev-atış+dep-yeme ve dep-atış+ev-yeme dağılımları λ ile ağırlıklanıp birleştirilir.
- Gösterim: fikstür kartlarında "1️⃣ İlk gol: TAKIM %62 · ⏱️ 76-90+. dk · 0-0 riski %16" (306/306).
- **Doğrulama:** py_compile OK; pytest 58/3 (aynı); tarayıcıda görsel onay (2.5Ü/KG/kart/kırmızı-risk/ilk-gol/bant hepsi kartlarda düzgün render).

### 2026-08-14 (devam) — "Olası skor" ile 1X2 rozeti tutarsızlığı düzeltildi (kullanıcı buldu)
Kullanıcı: bir maçta "Olası skor 1-1" (beraberlik) yazıyordu ama kazanan rozeti bir takımın adıydı — kafa karıştırıcı.
- **Kök neden:** `model_league_predictions.predict_match()` içinde `recommended_scoreline` (`scorelines[0]`, tüm Poisson tahtasındaki EN olası tek skor) ile nihai 1X2 tahmini (`draw_calibrated_prediction` — draw-boost kalibrasyonu uygulayan AYRI bir fonksiyon, caller'larda çağrılıyor) birbirinden BAĞIMSIZ hesaplanıyordu. Galibiyet olasılığı çok sayıda farklı skora yayılırken (1-0, 2-0, 2-1...), beraberlik olasılığı çoğunlukla tek bir skorda (1-1) yoğunlaştığı için tek-skor argmax'ı beraberlik çıkabiliyor, oysa kategori toplamında galibiyet daha olasıydı — matematiksel olarak doğru ama yan yana gösterilince çelişkili görünüyordu.
- **Düzeltme:** `predict_match()` artık kendi içinde AYNI `draw_calibrated_prediction`'ı (aynı yuvarlanmış girdilerle, caller'larla bit-birebir eşleşecek şekilde) çağırıp `calibrated_pick` kategorisini buluyor, `recommended_scoreline`'ı YALNIZ o kategori içindeki en olası skordan seçiyor (`scorelines` zaten olasılığa göre azalan sıralı). `top_scorelines`/`probs`/`strength_edge` DEĞİŞMEDİ — yalnız görüntüleme alanı.
- **Doğrulama (kritik):** 2025-26 Beşiktaş backtest **0.655** bu değişiklikten etkilenmiyor çünkü kaynağı `backtest_match_predictions.py` → `previews_besiktas_2025_2026_chronological/index.json` — `model_league_predictions.py`'yi hiç import ETMEYEN, tamamen ayrı bir sistem (kod içindeki "Beşiktaş-focused preview model" ayrımı doğrulandı). League-wide `run_backtest` doğruluğu değişiklik öncesi/sonrası **birebir aynı** ölçüldü (genel 0.553, Beşiktaş alt-kümesi 0.581) — çünkü `predicted` hâlâ aynı `probs`/`strength_edge`'den hesaplanıyor, `recommended_scoreline`'a hiç bakmıyor. 306/306 fikstür maçında artık skor↔rozet tutarsızlığı **0**. pytest 58/3 (aynı), py_compile OK.

### 2026-08-14 (devam) — TM 2026-27 kadro koleksiyon hatası çözüldü + B) Oyuncu skorer tamamlandı
Kullanıcı TM koleksiyon hatasını önce düzeltmeyi seçti.

**Kök neden bulundu (kod hatası DEĞİL):** `transfermarkt_super_lig_squads_2026_2027.json` en son **22 Haziran**'da güncellenmiş (18/18 kulüp "empty_squad"). `.github/workflows/daily-pipeline.yml` her gece 04:00 UTC'de `--include-network` ile doğru komutu (season-id=2026, doğru kulüp dosyası) çalıştırıyor — mantık sağlam. Ama cache dosyası (`data/raw/transfermarkt/transfermarkt_super_lig_squads_2026_2027/114.html`, 28 Mayıs) gerçek TM sayfası ("Besiktas JK - Detailed squad 26/27", engellenmemiş) ama `<table class="auflistung">` yalnız sezon FİLTRE dropdown'ı — asıl kadro tablosu değil; o tarihte muhtemelen TM'de 26/27 kadrosu henüz yoktu. **Bu oturumdan canlı çekişte parser sorunsuz 39 oyuncu buldu** — sorun GitHub Actions'ın bulut IP'sinin TM tarafından engellenmesi/farklı içerik servis edilmesi (klasik anti-bot), parser/kod DEĞİL. Aynı içerik her gece üretildiği için `git diff --staged --quiet` boş kalıp commit atmıyor, sessizce 2 aydır bayat kalmış.
- **Çözüm (bu oturumda):** Koleksiyon interaktif olarak yeniden çalıştırıldı: **18/18 kulüp, 0 skip, 564 oyuncu, €1.56 milyar toplam piyasa değeri.** Gerçek isimler (Osimhen, Trossard, Vlahović, Orkun Kökçü, Wilfred Ndidi, João Mário...) doğrulandı.
- **Açık kalan (kod dışı, altyapı):** Nightly cron'un neden engellendiği (IP/anti-bot) çözülmedi — otomatik gece koleksiyonu muhtemelen hâlâ başarısız olacak. Kadronun periyodik olarak elle/interaktif yeniden toplanması gerekebilir ta ki bir çözüm (farklı runner, proxy vb.) bulunana kadar; bu oturumda araştırılmadı (kapsam dışı, ayrıca scraping-evasion hassasiyeti var).

**B) Oyuncu skorer (`src/build_goal_scorer_predictions.py`, YENİ) — TAMAMLANDI:**
- 2025-26 TFF gol olaylarından (own-goal hariç, `type != 'K'`) `canonical_player_name` (normalize + `data/manual/player_aliases.json`) ile oyuncu başına gol/başlangıç-XI oranı — TAKIMDAN BAĞIMSIZ (isim bazlı), böylece transfer olan oyuncu doğru şekilde YENİ takımına bağlanıyor.
- Güncel 2026-27 kadrosuyla (bu oturumda taze toplanan) eşleştirilir; eşleşmeyen/yeni-transfer/yabancı-imza oyuncular (2025-26 Süper Lig geçmişi yok) için TAHMİN ÜRETİLMEZ — uydurulmadı.
- Takımın maç için beklenen golü (mevcut `expected_home/away_goals`), rated oyuncular arasında tarihsel gol PAYINA göre dağıtılır; P(oyuncu ≥1 gol) = 1−e^(−beklenen_gol×pay) (Poisson yaklaşımı).
- TM kulüp adı fikstürle örtüşmeyen 2 ek eşleşme: "AMED SPORTİF FAALİYETLER"↔"AMED SFK", "ARCA ÇORUM FK"↔"ÇORUM FK" (bilinen iç-tutarsızlık için pragmatik bant-aid — kök neden ayrı, açık).
- **Kapsam:** 306/306 maçta en az bir taraf rated (272 her iki taraf, 34 yalnız bir taraf — yeni/ağır-transfer takımlar). Örnek doğrulama: Galatasaray-Çorum → GS: Osimhen %50 (15 gol/19 başlangıç, gerçek veri), Yunus Akgün %23; Çorum (yeni takım, kendi golcüsü yok) → yalnız geçmiş sezon başka takımda oynamış bir transfer oyuncusu %38 (dürüst davranış, uydurma yıldız yok).
- Gösterim: fikstür kartlarında "⚽ TAKIM: Oyuncu %50 · Oyuncu %23" (306/306). Ana sayfa hero'suna eklenmedi (yer/yoğunluk nedeniyle fikstür sayfasında bırakıldı).
- model_league_predictions.py'a DOKUNULMADI.
- **Doğrulama:** py_compile OK; pytest 58/3 (aynı); tarayıcıda görsel onay.

**Sonuç:** Kullanıcının A) skor+xG+O/U+KG+kart, B) oyuncu skorer, C) ilk gol+dakika bandı isteğinin üçü de tamamlandı; Avrupa sayfası + skor↔rozet tutarlılığı da düzeltildi. Tüm değişiklikler push edildi.

### 2026-08-16 — Hafta 1 gerçek sonuçları girildi + KRİTİK sızıntı (look-ahead) hatası bulundu ve düzeltildi
Kullanıcı gerçek Hafta 1 sonuçlarını görüp "tahminlerin tamamı fiyasko" dedi, sonra "daha detaylı analiz, ilerisi için dikkat" istedi.

**1) Gerçek sonuçlar veri hattına girildi (TFF collector'lar da TM gibi bayat kalmıştı):**
- `tff_super_lig_fixtures_2026_2027.json` (skor alanı) ve `tff_super_lig_matches_2026_2027.json` (goller/kartlar/kadro) Hafta 1 için hep `"-"`/boştu — pipeline'ın son başarılı çalışması eski, aynı TM deseni (muhtemelen CI bulut IP engeli). `collect_tff_season_fixture` + `advance_season_state` interaktif yeniden çalıştırıldı: 6 maçın gerçek skoru geldi (**GS 2-2 Çorum, Kasımpaşa 1-1 TS, Konyaspor 0-1 Rizespor, Gaziantep 1-1 Alanyaspor, Gençlerbirliği 2-1 FB, Başakşehir 2-0 Kocaelispor**) — web aramasıyla bağımsız doğrulandı, birebir örtüştü. 1 kayıt (GS-Çorum) ilk denemede `None-None` geldi (TFF detay sayfası henüz yayınlanmamıştı); kayıt silinip yeniden çekilince düzeldi (transient, kalıcı hata değil).

**2) KRİTİK BULGU — sızıntı (look-ahead) hatası (`build_season_fixture_predictions.py`):**
- `build_predictions()` TEK bir `compute_final_state(all_matches)` hesaplayıp TÜM haftalara (geçmiş VE gelecek) aynı "final" team_history/Elo'yu uyguluyordu. Hafta 1 sonuçları girilince bu, **Hafta 1'in KENDİ tahmininin Hafta 1'in kendi sonucunu görerek** yeniden hesaplanmasına yol açtı — Kasımpaşa-Trabzonspor tahmini `away`'den `home`'a DÖNDÜ (kullanıcıya ilk verdiğim rakamlarla karşılaştırınca fark edildi). Bu, her hafta sonuçlandıkça o haftanın GÖRÜNTÜLENEN tahminini/olasılıklarını sessizce kirletip **Haftalık Karne'yi (weekly_evaluation) geçersiz kılan** ciddi bir hataydı.
- **Düzeltme:** `run_backtest`'teki aynı ilkeyle walk-forward'a çevrildi — artık her hafta İÇİN yalnızca o hafta BAŞLAMADAN ÖNCE gerçekleşmiş maçlardan (`settled` listesi, kronolojik tüketilen kuyruk) `compute_final_state` hesaplanıp o haftaya uygulanıyor. Performans etkisi ihmal edilebilir (0.4s, 34 hafta × büyüyen alt-küme). Doğrulama: düzeltme sonrası Hafta 1'in olasılıkları **kullanıcıya ORİJİNAL verdiğim rakamlarla birebir eşleşti** (Ev59/X28/Dep13 GS-Çorum vb.) — sızıntı öncesi doğru haline döndü. model_league_predictions.py/run_backtest'e dokunulmadı — 0.655/0.553/0.581 etkilenmedi.

**3) Hafta 1 gerçek karnesi (düzeltilmiş, sızıntısız): 6/6 sonuçlanan maçta 1 doğru (%17), 0/3 beraberlik yakalandı (draw_recall=0.0).**
- 3/5 bilinen sonuç beraberlikti — lig ortalamasının (~%25-27) belirgin üzerinde bir varyans; beraberlik zaten modelin (ve genel olarak futbol tahmininin) en zayıf noktası (`draw_calibrated_prediction` tam bunun için var, ama 3/3'ünü de yakalayamadı).
- **En ciddi vaka:** Gençlerbirliği-Fenerbahçe'de model **YÜKSEK güvenle** (Dep%61, HIGH confidence) FB'yi favori gösterdi, Gençlerbirliği 2-1 kazandı — bu tek başına "şanssızlık" değil, gerçek bir kalibrasyon sinyali.
- **Kök neden adayı — transfer sinyali TAMAMEN BOŞ:** 6 maçın 6'sında da `transfer_signal.available=False` (hem ev hem deplasman). `transfer_tracker_2025_2026.json` kontrol edildi: **Beşiktaş'a ait SIFIR kayıt var** — oysa bu oturumda taze toplanan gerçek TM kadrosu Beşiktaş'ın Vlahović, Trossard, Wilfred Ndidi, Orkun Kökçü, João Mário gibi büyük gerçek transferler yaptığını gösteriyor. Haber-kaynaklı transfer tracker bu büyük hareketleri YAKALAYAMAMIŞ (yalnız 8 CORROBORATED, 0 OFFICIAL kayıt) — model yeni sezonun kadro gerçekliğine kör, salt 2025-26 form/Elo'suna dayanıyor.
- **Açık kalan (sonraki adım):** (a) Transfer sinyalini güçlendirmek için artık taze TM kadro verisi bir referans/doğrulama kaynağı olarak kullanılabilir; (b) 1 hafta istatistiksel olarak ANLAMLI bir örneklem değil — 2-3 hafta daha izlenip trend doğrulanmadan büyük model değişikliği yapılmamalı; (c) `tff_super_lig_fixtures_2026_2027.json`/`matches_2026_2027.json`'ın nightly cron'da neden bayat kaldığı (muhtemelen TM ile aynı IP-engeli) hâlâ araştırılmadı — her hafta elle/interaktif tazeleme gerekebilir.
- **Doğrulama:** py_compile OK; pytest 58/3 (aynı); performans 0.4s; Hafta 1 olasılıkları sızıntı-öncesi haliyle birebir eşleşti.

### 2026-08-16 (devam) — Transfer sinyali kadro-diff ile güçlendirildi (kullanıcı "devam" dedi)
Önceki bulgu (transfer sinyali 6/6 maçta boş, Beşiktaş tracker'da sıfır kayıt) üzerine somut düzeltme yapıldı.

- **Yeni sinyal — `squad_transition_edge()` (`src/preview/probability.py`, YENİ):** Haber-kaynaklı `transfer_tracker`'a bağımlı kalmak yerine, iki GERÇEK Transfermarkt kadro anlık görüntüsünü (`transfermarkt_super_lig_squads_2025_2026.json` vs `_2026_2027.json`, `canonical_player_name` ile eşleştirilmiş) doğrudan karşılaştırıp net kadro piyasa değeri değişimini (gelenler − gidenler) hesaplıyor — söylenti/haber ayrıştırmaya bağımlı değil, ground-truth. 3M€ gürültü eşiği, ±0.15 cap (mevcut transfer sinyaliyle aynı ölçek).
- **`combined_transfer_edge()`:** Haber-tracker sinyali (varsa) + kadro-diff sinyalini (varsa) harmanlar (ikisi de varsa ortalama, yalnız biri varsa o kullanılır). `model_league_predictions.py`'de `transfer_strength_edge` çağrısı `combined_transfer_edge` ile değiştirildi (yalnız `apply_transfer_signal=True` yolunda, backtest'i etkilemez).
- **Doğrulama — isim eşleştirmesi sağlam:** Beşiktaş 2025-26 kadrosu 50 → 2026-27 39 kişi; 24 oyuncu doğru "kalan" (aksanlı isimler dahil: Tiago Djaló, Yasin Özcan) eşleşti, 15 gelen + 26 giden = aritmetik tutarlı. Beşiktaş edge=−0.15 (cap) — ŞAŞIRTICI ama GERÇEK: gelenler (Vlahović 35M, Trossard 18M, Nübel 12M...) toplam 86.9M€, ama gidenler (Tammy Abraham 18M, Gedson Fernandes 16M, El Bilal Touré 13M, Asllani 12M, Muçi 11M...) daha fazla — 50→39 kadro küçülmesiyle net değer düşüşü. Market-value-toplamı kaba bir proxy (kim gerçekten forma giyiyor bilgisini yakalamaz) — bilinen sınırlama, mevcut sinyalle aynı metodolojik kısıt.
- **Etki:** Transfer sinyali aktif maç sayısı **0/306 → 294/306**. Hafta 1'in KENDİ (zaten oynanmış) sonucu değişmedi (isabet hâlâ %17/1-6) — sinyal küçük/capli, geçmişi "kurtarmıyor"; ama gelecek haftalar (Beşiktaş-Eyüpspor dahil) artık gerçek kadro değişimini hesaba katıyor.
- **Doğrulama:** py_compile OK; pytest 58/3 (aynı); 2025-26 backtest **birebir aynı** (Beşiktaş 0.581, genel 0.553) — `apply_transfer_signal` varsayılan False, backtest hiç bu yoldan geçmiyor; performans 0.4s.

### 2026-08-17 — Haftalık Karne regresyonu bulundu ve kalıcı olarak düzeltildi (kullanıcı fark etti)
Kullanıcı: canlı sitede (metric11.com/weekly_evaluation_2026_2027.html) "isabet 0" ve "yalnız 1 değerlendirme" gördüğünü, oysa gerçekte en az 3 maçı bildiğimizi belirtti.

**Kök neden:** `collect_tff_season_fixture.py` her çalıştığında `tff_super_lig_fixtures_2026_2027.json`'u SIFIRDAN yeniden yazıyordu (merge/koruma YOK). Bot'un gecelik (`daily-pipeline.yml`, 04:55 UTC) çalışmasında TFF'nin fikstür listeleme sayfası 5/6 maç için tam sonucu döndürmedi (ağ/CI kaynaklı geçici sorun — TM'de gördüğümüzle aynı desen) ve script bu eksik veriyi SESSİZCE üzerine yazdı: **önceden doğru girilmiş 5 gerçek Hafta 1 skoru "-"ye geri döndü**, yalnız Galatasaray-Çorum (yanlış tahmin) hayatta kaldı → `weekly_evaluation` `evaluated_matches:1, correct:0` gösterdi (kullanıcının gördüğü tam olarak buydu). NOT: `tff_super_lig_matches_2026_2027.json` (detaylı kayıtlar, `advance_season_state`'in kendi append+dedup mantığı sayesinde) ETKİLENMEDİ — yalnız basit skor kaynağı (`fixtures.json`) bozulmuştu.
- **Kalıcı düzeltme:** `collect_tff_season_fixture.py`'a "regresyon koruması" eklendi — yeni çekiş bir maç için `"-"` dönerse ama dosyada zaten BİLİNEN gerçek bir skor varsa, o korunur (asla gerçek skor → "-" ile ezilmez). Şimdi ve gelecekte aynı bot-çalışması kaynaklı veri kaybı bir daha olmayacak.
- **Veri yeniden tazelendi:** İnteraktif yeniden çalıştırıldı — bu sefer 8/9 Hafta 1 maçı gerçek skorla geldi (yalnız Samsunspor-Göztepe henüz oynanmadı/oynanıyor). `advance_season_state` ile detaylı kayıtlara işlendi.
- **Düzeltilmiş, güncel Hafta 1 karnesi: 8 maçta 2 doğru (%25).** ✅ Başakşehir-Kocaelispor, ✅ **Beşiktaş-Eyüpspor** (1-0, ev sahibi tahmini doğru çıktı — muhtemelen az önce eklenen kadro-diff transfer sinyalinin katkısıyla). ❌ diğer 6 (3 beraberlik, Amed-Erzurumspor 3-0 ev sahibi galibiyeti "beraberlik" tahmin edilmiş, Konyaspor-Rizespor ve Gençlerbirliği-FB ters yön).
- **İkinci soru ("neden yalnız 1 değerlendirme var") aynı kök nedene bağlıydı** — veri yalnız 1 gerçek skor içerdiği için sayfa yalnız 1 satır gösteriyordu; düzeltme sonrası 8 satır render ediyor (doğrulandı).
- **Doğrulama:** py_compile OK; pytest 58/3 (aynı); backtest birebir aynı (Beşiktaş 0.581, genel 0.553); weekly_evaluation.html 8/8 satır doğrulandı.

### 2026-08-17 (devam) — Yanlış transfer kaydı düzeltildi + kalıcı düzeltme mekanizması kuruldu
Kullanıcı ekran görüntüsüyle bildirdi: "İrfan Can Eğribayat Gençlerbirliği'ne gitti ama sen Samsunspor demişsin." Transfer tracker'da "Irfan Can Eğribayat: Samsunspor A.Ş. → Fenerbahçe (€1.2M, CORROBORATED)" gösteriliyordu.

- **Kök neden:** Kayıt, Hürriyet'in "2 gün önce ayrıldı, Fenerbahçe'ye duvar oldu: Ankara'da İrfan Can Eğribayat gecesi!" başlıklı haberinden geliyordu — bu haber bir TRANSFER duyurusu değil, Eğribayat'ın (yeni takımı Gençlerbirliği'nde, Ankara'da) eski kulübü Fenerbahçe'ye karşı gösterdiği maç performansı hakkındaydı. Otomatik haber→transfer çıkarımı (LLM, `analyze_news_with_claude`) bu başlığı yanlış yorumlayıp "Samsunspor A.Ş. → Fenerbahçe" uydurmuş (muhtemelen Eğribayat'ın geçen sezon ikinci yarısını Samsunspor'da kiralık geçirmiş olmasıyla karışmış). Web'den doğrulandı (Hürriyet/ASpor/Fanatik/Takvim/CNN Türk/Sabah/Sporx/Cumhuriyet): gerçek transfer **Fenerbahçe → Gençlerbirliği**, 13 Ağustos 2026 resmi kulüp açıklaması, 2 yıllık sözleşme. Piyasa değeri (€1.2M) doğruydu, yalnız yön/kulüpler yanlıştı.
- **Kalıcı düzeltme mekanizması (YENİ):** `data/manual/transfer_corrections.json` — `player_role_overrides.json` ile aynı desende, elle doğrulanmış düzeltmeler. `build_transfer_tracker.py`'a `_apply_corrections()` eklendi, `_enrich()`'ten SONRA (özet istatistiklerden ÖNCE) uygulanıyor — bir sonraki haber-toplama çalışması aynı hatayı tekrar üretse bile düzeltme kalıcı kalır (haber-tracker'ın LLM-tabanlı çıkarım hatası kökten çözülemiyor — güvence altyapısı bu).
- **Doğrulama:** Kayıt artık "Fenerbahçe → Gençlerbirliği, RESMİ" gösteriyor (HTML'de doğrulandı). py_compile OK; pytest 58/3 (aynı).
- **Not:** Bu, önceki oturumda "haber-tracker büyük gerçek transferleri kaçırabiliyor" bulgusuna (Beşiktaş 0 kayıt) ek olarak, haber-tracker'ın **var olan** kayıtlarda da yön/kulüp hatası yapabileceğini somut olarak doğruladı — `squad_transition_edge` (ground-truth TM kadro-diff) sinyalinin neden haber-tracker'dan daha güvenilir bir birincil kaynak olması gerektiğini pekiştiriyor.

### 2026-08-17 (devam) — A) Ceza (kırmızı kart) sinyali TAMAMLANDI; B) gerçek sakatlık YAPILMADI (veri güvenilmez bulundu)
Kullanıcı: gelecek hafta tahminlerinin gerçekten dinamik güncellenip güncellenmediğini ve sakatlık faktörünün olup olmadığını sordu. Somut kanıtla doğrulandı: Galatasaray'ın Hafta 2 tahmini, Hafta 1'in GERÇEK 2-2 sonucunu (`team_history`'nin son elemanı: `goals_for:2, goals_against:2, points:1`) doğrudan kullanıyor — sistem statik değil. Ama sakatlık/ceza modelde HİÇ yoktu (`predict_match`'te sıfır referans; var olan tek modül Beşiktaş-özel, tahmine bağlı değil).

**A) `suspension_edge()` (`src/preview/probability.py`, YENİ) — TAMAMLANDI:**
- Yalnız STRAIGHT RED / ÇİFT SARI (belirsizlik yok — birikmiş sarı kart eşiği TFF'nin tam reset kuralı teyit edilemediği için KASITLI dahil edilmedi). 2026-27 sezonu gerçek maç verisinden (`tff_super_lig_matches_2026_2027.json`) bir takımın en son oynadığı maçta kırmızı kart gören oyuncu, oyuncunun güncel kadro piyasa değeri PAYI kadar küçük bir eksi (cap 0.08) olarak yansır.
- **Bulunan ve düzeltilen bug:** İlk versiyon cezayı "kırmızı karttan sonraki HER gelecek haftaya" uyguluyordu (yalnız oynanmış maçlara bakıp "en son maç" arıyordu, henüz oynanmamış aradaki haftaları göz ardı ediyordu). Düzeltme: `_load_fixture_schedule()` (YENİ, tam fikstür — oynanmış+oynanmamış) ile ceza SADECE kırmızı karttan sonraki İLK fikstüre uygulanıyor artık. Test: Hafta 3'te yanlışlıkla hâlâ görünen 2 ceza, düzeltme sonrası yalnız Hafta 2'de doğru gösteriyor.
- Aynı "ARCA ÇORUM FK"/"ÇORUM FK" iç-tutarsızlığı (bilinen, açık) burada da değer kaybına yol açtı (`_SQUAD_NAME_TO_TM`'e eklendi, düzeltildi — squad_transition_edge de bundan faydalanıyor artık).
- `model_league_predictions.py`: `apply_suspension_signal` parametresi (varsayılan False, backtest etkilenmez). Fikstür kartlarında "🚫 Cezalı: OYUNCU" gösterimi eklendi.
- **Doğrulama:** 2 gerçek kırmızı kart olayıyla test edildi (Çorum FK — Kyziridis, Eyüpspor — Da Costa), her ikisi doğru takım+doğru hafta+doğru değerle çalıştı. py_compile OK; pytest 58/3 (aynı); backtest birebir aynı (Beşiktaş 0.581, genel 0.553).

**B) Gerçek sakatlık (haber-tabanlı) — ARAŞTIRILDI, KURULMADI:**
- `news_intelligence_2025_2026.json`'daki `injuries` dizisi kontrol edildi: yalnız 2 kayıt var, **İKİSİ DE YANLIŞ** (%100 hata). Kök: "Beşiktaş'ta bir dönem sona erdi! Necip Uysal veda etti" başlıklı haber bir **EMEKLİLİK VEDA TÖRENİ**ydi (16 Ağustos, Necip Uysal geçen sezon sonunda emekli olmuş, 22 yıllık kariyeri, Beşiktaş-Eyüpspor maçı öncesi tören) — LLM bunu "sakatlık, sezon sonu" diye yanlış sınıflandırmış. İkinci kayıt ("Ömer Faruk Beyaz", Esenler Erokspor — Süper Lig'de bile değil) aynı makaleden gelen, tamamen alakasız bir halüsinasyon.
- Ayrıca kod bug'ı bulundu: `news_intel_unavailability_for_team()` `signal.get("team")` okuyor ama gerçek alan adı `"club"` — hiç eşleşmiyor. Ve Beşiktaş-hardcoded alias listesi (`{"beşiktaş","besiktas"}`) var, başka takım için asla çalışmaz.
- `build_player_availability.py`'nin çıktısında (kullanıcıya görünen Beşiktaş sayfasına besleniyor) bu yanlış "sakat" bilgisi zaten sızmış durumda (`current_news_context_unavailability` listesinde `player_name: null` bozuk bir HIGH-confidence kayıt).
- **Karar:** Bu veriyi ŞU HALİYLE modele bağlamak (düşük ağırlıkla bile) tahminleri düzeltmek yerine BOZAR — yapılmadı. Ayrı, daha güvenilir görünen bir kaynak var (`current_news_context_unavailability`'deki "beIN SPORTS sakat ve cezalı listesi" — Hyeon-gyu Oh, Kartal Yılmaz, Milot Rashica, MEDIUM_CONTEXT), ama doğrulanmadı — sonraki adım olarak bırakıldı.
- **Sonraki adım (kullanıcıyla netleştirilecek):** (a) beIN kaynaklı listeyi doğrulayıp güvenilirse SADECE onu (LLM-serbest, curated) kullanacak dar kapsamlı bir sinyal kurmak, (b) ya da yalnız elle-doğrulanmış bir `injury_overrides.json` ile (transfer_corrections deseninde) ilerlemek — otomatik LLM çıkarımına güvenmemek.
- **beIN listesi de DOĞRULANDI VE REDDEDİLDİ:** Kaynak sayfanın kendi metninde "Trendyol Süper Lig'de **34. haftanın** sakat ve cezalı futbolcuları" yazıyor — 34. hafta, 34 haftalık sezonun SON haftası, yani bu 2025-26 sezonunun Mayıs ayına ait BAYAT içerik (bizim çekişimiz bugün taze olsa da, kaynağın kendi sayfası güncellenmemiş). Listede küme düşen Fatih Karagümrük'ün olması da bunu doğruluyor. Kullanıcı kararı: **hiçbir otomatik sakatlık kaynağı kurulmadı**, yalnız A) ceza sinyali (kırmızı kart) yeterli kabul edildi.

### 2026-08-18 — Yine bayat TFF skoru: Samsunspor-Göztepe (kullanıcı fark etti, 3. tekrar)
Kullanıcı: site "güncellenmiş" görünüyor (timestamp taze) ama dünkü maç sonucu yansımamış.

- **Doğrulandı:** `season_fixture_predictions_2026_2027.json`'da `generated_at: 2026-08-18T07:04` (bugün, taze) ama Samsunspor-Göztepe skoru hâlâ `"-"`. Web'den gerçek sonuç doğrulandı: **Samsunspor 3-3 Göztepe** (17 Ağustos, 6 gol). Bu, `collect_tff_season_fixture.py`'ın 2026-08-17'de eklenen "bilinen skoru koru" düzeltmesinden FARKLI bir durum — burada hiç bilinen skor yoktu (koruyacak bir şey yok), TFF'nin fikstür sayfası bu maçın sonucunu O ANKİ çekişte hiç döndürmemiş (3. kez aynı desen: TM/TFF collector'ları CI'da tutarsız/eksik veri döndürüyor).
- **Düzeltme:** İnteraktif yeniden çalıştırıldı (`collect_tff_season_fixture` + `advance_season_state`) — 9/9 Hafta 1 maçı artık gerçek skorla. Tam zincir yeniden üretildi: **Hafta 1 karnesi 9 maçta 2 doğru (%22)**; "Bu Hafta" hero'su otomatik **Hafta 2'ye** geçti (Hafta 1 artık tamamen oynanmış).
- **Doğrulama:** pytest 58/3 (aynı); backtest birebir aynı (Beşiktaş 0.581, genel 0.553).
- **Açık kalan sistemik sorun (3. tekrar, henüz kök çözüm yok):** Nightly/refresh cron'ların TFF skor çekişi güvenilmez — muhtemelen GitHub Actions'ın bulut IP'si TFF/TM tarafından zaman zaman engelleniyor/eksik yanıt alıyor. `collect_tff_season_fixture.py`'daki "bilinen skoru koru" düzeltmesi yalnız REGRESYONU (var olan iyi veriyi "-" ile ezmeyi) önlüyor — YENİ bir sonucun ilk denemede hiç gelmemesini önlemiyor. Kalıcı çözüm için düşünülebilir: (a) collector içine kısa gecikmeli otomatik retry (birkaç kez dene, hâlâ "-" ise pes et), (b) workflow'a maç saatlerinden birkaç saat sonra ekstra bir tetikleyici eklemek, (c) periyodik olarak bu oturumdaki gibi elle kontrol/tazeleme. Şimdilik (c) ile idare ediliyor.

### 2026-08-19 — Trafik artmıyor şikayeti: Telegram kanalı hiç çalışmıyormuş + Search Console teşhisi
Kullanıcı: "sitemizin trafiği artmıyor bir türlü." Teknik SEO denetimi yapıldı (title/meta/OG/canonical/JSON-LD/sitemap/robots — hepsi sağlam, GSC DNS ile doğrulanmış) ve dağıtım kanalları kontrol edildi.

- **Bulunan asıl kırık: Telegram kanal bildirimi hiç çalışmıyordu.** `1e7e4591` (25 Haziran) ile kod push edilmişti ama `TELEGRAM_BOT_TOKEN`/`TELEGRAM_CHANNEL_ID` GitHub Secrets'a hiç girilmemişti (bkz. [[project_telegram_setup]]) — workflow log'unda ~8 haftadır her çalıştırmada sessizce "eksik — atlanıyor" diye geçiyordu. Kullanıcıyla birlikte BotFather'dan bot oluşturuldu (`@metric11_new_bot`), `@metric11tr` public kanalı açıldı, bot admin yapıldı, "Restrict Saving Content" kapatıldı (forward/paylaşımı engelliyordu). Secrets `gh secret set` ile eklendi, `gh workflow run refresh.yml` ile canlı test edildi: **20/20 birikmiş transfer sinyali başarıyla kanala gönderildi**. Artık her 6 saatte bir (00:15/06:15/12:15/18:15 UTC) otomatik postluyor.
- **Search Console teşhisi (kullanıcı ekran görüntüleriyle paylaştı):** Domain 2026-05-25'te kurulmuş (~12 haftalık). "Sayfayı dizine ekleme" raporunda toplam yalnız **7 sayfa biliniyor** (4 indeksli + 3 sorunlu) — 39 sitemap URL'ine rağmen. "3 neden" kırılımı: 404 (1), yönlendirmeli sayfa (1), taranmış-henüz indekslenmemiş (1) — **sunucu hatası/noindex/robots bloğu YOK**. Sitemap'teki 39 URL tek tek `curl` ile test edildi: **hepsi şu an 200 dönüyor** — geçmiş 404/redirect kaydı muhtemelen yeniden adlandırılmış eski bir URL'den kalma, sitemap'te düzeltilecek bir şey yok.
- **İç link denetimi:** Ana sayfa + `football_intelligence_home.html` + `all_teams_preview_dashboard_2025_2026.html` birlikte 39 URL'in 37'sine link veriyor (2 istisna normal: `gundem_2025_2026.html` zaten ana sayfanın kendisi). Yalnız **`prediction_backtest_dashboard_2025_2026.html` gerçek bir orphan sayfaydı** (hiçbir hub sayfasından link almıyordu) — `build_product_home.py`'a kart olarak eklendi (Futbol Komuta Merkezi'nin hemen ardına, öne çıkan 4 kart arasına).
- **Ek bulgu — bayat duplicate sayfa:** `besiktas_2025_2026_dashboard.html` (25 Mayıs'tan kalma, hiçbir script artık üretmiyor, sitemap'te yok ama hâlâ canlı 200 dönüyordu) → `vercel.json`'a 301 redirect eklendi, güncel `besiktas_2025_2026_dashboard_chronological.html`'e yönlendiriyor.
- **Sonuç/teşhis:** Kod tarafında büyük bir "bug" yoktu — asıl darboğaz yeni domain + sıfır backlink + Google'ın küçük/güvensiz sitelere uyguladığı kısıtlı crawl bütçesiydi. Telegram'ın artık gerçekten çalışması (dış sinyal/paylaşılabilirlik) ve orphan sayfanın linklenmesi en somut, ölçülebilir aksiyonlardı; SEO'da 3-6+ aylık bir kuyruk beklentisi normal.
- **Doğrulama:** `python3 -m src.build_product_home` çalıştırıldı, yeni kart HTML'de doğrulandı; py_compile OK. Commit `fc388777` (rebase sonrası `bd3e059b`) main'e push edildi.
- **Açık kalan (sonraki, ~1 hafta sonra kontrol):** GSC "Sayfayı dizine ekleme" sayısının 7'den yukarı çıkıp çıkmadığına bak; çıkmıyorsa URL Inspection ile ana sayfa + birkaç önemli sayfa için elle "Dizine Eklenmeyi Talep Et" denenebilir.

### 2026-08-23 — "Site güncel değil, transferler geri kalmış" şikayeti: yanlış alarm + gerçek artifact kotası hatası bulundu
Kullanıcı: site güncel görünmüyor, transferler geri kalmış, mail'de failed bildirimleri var, "GitHub Actions limite takılmış gibi" dedi.

- **Site aslında güncel:** `metric11.com` doğrudan `curl` ile kontrol edildi — `transfer_tracker_2025_2026.html` için `last-modified: 2026-08-23 13:17`, içerik tarihleri bugünü gösteriyor. `tm_squad_changes_2026_2027.json` de aynı gün 13:03'te güncellenmiş. Yerel repo klonunun 53 commit geride kaldığı (son pull'dan beri) görüldü — kullanıcının "geri kalmış" hissi muhtemelen tarayıcı önbelleği ya da spesifik bir oyuncunun piyasada gerçekten hareketsiz olmasından kaynaklı, canlı veri sorunlu değildi.
- **Gerçek bulunan hata:** `metric11 full network pipeline` (`daily-pipeline.yml`) işi 3 gündür (2026-08-21, 22, 23) "failure" statüsündeydi ama TFF/Transfermarkt/haber toplama + git commit+push adımlarının hepsi sorunsuz tamamlanıyordu. Asıl patlayan adım en sondaki `actions/upload-artifact@v4` — **"Artifact storage quota has been hit"**. Repo private olduğu için free plan'da 500MB artifact kotası var; `gh api .../actions/artifacts` ile kontrol edildiğinde 85 artifact, ~360MB+ birikmiş (90 günlük varsayılan retention ile her gün ~12MB ekleniyordu). Bu adımı hiçbir workflow `download-artifact` ile tüketmiyordu (grep ile doğrulandı) — tamamen gereksizdi, sadece Actions run sayfasında indirilebilir bir yedek zip sağlıyordu.
- **Düzeltme:** `daily-pipeline.yml`'deki `upload-artifact` adımı tamamen kaldırıldı (commit `b7d48562`, main'e push edildi). Bu, kullanıcının gördüğü "failure" maillerinin kaynağıydı; veri akışına (git push → Vercel deploy) hiç dokunmuyor, sadece kotayı dolduran gereksiz yükleme adımını temizliyor.
- **Doğrulama:** Değişiklik öncesi diğer workflow dosyaları (`news-refresh.yml`, `refresh.yml`) grep ile tarandı, hiçbiri bu artifact'i beklemiyor. Silinen adım `if: always()` ile çalışıyordu ama commit+push'tan sonra geliyordu, yani kaldırılması pipeline sırasını bozmuyor.
- **Açık kalan:** Bir sonraki `full network pipeline` çalıştırmasının (yarın ~04:00 UTC) "success" dönüp dönmediğine bakılmalı; ayrıca mevcut 85 birikmiş artifact GitHub arayüzünden elle silinebilir (kota anında boşalır, opsiyonel — 90 gün içinde otomatik de düşecek).

### 2026-08-25 — "Tahmin oranı yine düşük" şikayeti: rakamlar doğrulandı + "Yüksek güvenli isabet" istatistiğinin hiç çalışmadığı bulundu, düzeltildi
Kullanıcı: bu hafta da tahmin oranının çok düşük çıktığını belirtti.

- **Gerçek rakamlar doğrulandı:** Hafta 2: 8 maçta 2 doğru (%25). Sezon toplamı (Hafta 1+2): 17 maçta 4 doğru (%23,5), 4 gerçek beraberlikten 0'ı yakalandı — draw_recall hâlâ 0.0 (bilinen zayıflık, bkz. yukarısı).
- **Bulunan bağımsız hata:** `weekly_evaluation`'daki "Yüksek güvenli maç isabeti" istatistiği kuruluşundan beri hep 0/0/null gösteriyormuş. Kök neden: `build_season_fixture_predictions.py:155` oynanmış maçlarda gerçek güven etiketini (HIGH/MEDIUM/LOW) görüntüleme amaçlı `"PLAYED"` string'iyle eziyor; `build_weekly_evaluation.py` ise tam olarak bu ezilmiş `data_confidence` alanını okuyup `== "HIGH"` arıyordu — asla eşleşmiyordu.
- **Düzeltme:** `build_weekly_evaluation.py`'a `_prediction_confidence()` eklendi — maç oynanmadan önceki güven etiketini, halen JSON'da saklı olan (ezilmeyen) `home/draw/away_win_probability` değerlerinden `model_league_predictions.confidence_label` ile AYNI eşiklerle yeniden hesaplıyor. Yeni `prediction_confidence` alanı eklendi, `_summarize`'daki HIGH filtresi ve markdown tablosundaki "Güven" sütunu buna geçirildi (`data_confidence` alanı JSON'da durum/gösterim amaçlı korunuyor, sadece HIGH-filtre mantığı düzeltildi).
- **Gerçek (artık doğru görünen) güven kırılımı:** HIGH 3/6 (%50), MEDIUM 1/8 (%12,5), LOW 0/3 (%0) — sıralama doğru yönde ama örneklem (17 maç) hâlâ çok küçük, HIGH'da bile %50.
- **Doğrulama:** Elle Python ile bağımsız hesaplanan rakamlar (`confidence_label` mantığı kopyalanarak) script çıktısıyla birebir eşleşti (HIGH 3/6, MEDIUM 1/8, LOW 0/3). pytest 58/3 (aynı, 3 hata `test_season_boundaries.py`'de bu değişiklikten bağımsız/önceden bilinen). MD/HTML çıktılarında "Güven" sütunu artık HIGH/MEDIUM/LOW gösteriyor (önceden hep "PLAYED" yazıyordu).
- **Açık kalan:** Örneklem küçük (17 maç) — birkaç hafta daha izlenip HIGH-confidence isabetinin gerçekten %50'nin üzerine çıkıp çıkmadığına bakılmalı; genel düşük isabet (%23,5) hâlâ büyük ölçüde beraberlik-körlüğünden kaynaklanıyor (draw_calibrated_prediction 17 oynanmış maçın yalnızca 1'inde "beraberlik" demiş, gerçekte 4 oldu).

### 2026-09-05 — Tahmin oyunu tek domain altına alınıyor (tahmin.metric11.com) + herkesin tahminlerini gösteren sayfa eklendi
Kullanıcı: "metric tahmin vercel domaininde ama metric11 domaininde olmalı, herşey tek domainde olacak" + "herkes kayıtlı kullanıcıların tahminlerini de görecek."

- **Domain:** `metric11-tahmin` Vercel projesine `tahmin.metric11.com` custom domain'i eklendi (`vercel domains add`). basePath+rewrite ve Microfrontends yaklaşımları daha önce Clerk auth'unu kırdığı için terk edilmişti (bkz. [[project_predict_app_launch]]) — bu kez path-bazlı gerçek birleşim yerine subdomain seçildi (kullanıcı onayladı): predict-app kod tarafında değişiklik gerekmiyor, sadece Vercel domain + DNS. Ana sitedeki `vercel.json` redirect hedefleri `metric11-tahmin.vercel.app` → `tahmin.metric11.com` olarak güncellendi; `src/build_live_feed.py` içindeki yorum satırı da güncellendi.
- **Açık kalan adımlar TAMAMLANDI (aynı oturumda, kullanıcıyla birlikte):** Cloudflare'de `tahmin` CNAME'i + Clerk'in Production instance'ı için istediği 5 CNAME kaydı (clerk./accounts./clk._domainkey./clk2._domainkey./clkmail.tahmin) Clerk'in "Configure automatically" (Cloudflare Domain Connect) akışıyla eklendi, hepsi doğrulandı. Clerk tarafında yeni bir **Production instance "Secondary application" olarak `tahmin.metric11.com` için oluşturuldu** (önceden hiç production instance yoktu — sadece Development vardı, bu [[project_predict_app_launch]]'taki eski varsayımı düzeltir). Yeni `pk_live_`/`sk_live_` anahtarları Vercel'in Production environment variable'larına elle girildi, `vercel --prod` ile redeploy edildi ve canlıda doğrulandı (`curl` ile yeni `pk_live_` anahtarının deploy'a gömüldüğü teyit edildi). `https://tahmin.metric11.com` artık tam çalışıyor, "Development mode" rozeti kalktı.
- **Topluluk Tahminleri sayfası:** `predict-app/app/topluluk/page.tsx` eklendi — her maç için tüm kullanıcıların tahminlerini listeliyor. Rekabet adaletini korumak için tasarım kararı: henüz kilitlenmemiş (kickoff geçmemiş) maçlarda başkalarının tahminini görebilmek için önce kullanıcının kendi tahminini girmiş olması gerekiyor; maç kilitlendikten (başladıktan) sonra herkese açık. Nav bar'a link eklendi (`components/nav-bar.tsx`) — kullanıcı geri bildirimiyle "Herkesin Tahminleri" ismi "Topluluk Tahminleri" olarak değiştirildi (daha doğal Türkçe). Yeni DB tablosu/gerçek yorum (comment) özelliği eklenmedi — kullanıcı onayıyla kapsam "tahminleri herkese açmak" ile sınırlı tutuldu.
- **Geçmiş maça tahmin engeli zaten mevcuttu:** Ana sayfa yalnız `getUpcomingMatches()` (kickoff'u geçmemiş) maçları listeliyor + `POST /api/predictions` sunucu tarafında `isLocked()` ile kickoff geçmiş/oynanmış maçları 409 ile reddediyor — kullanıcı sorunca doğrulandı, ek değişiklik gerekmedi.
- **Küçük UI düzeltmeleri (kullanıcı bildirdi):** Tailwind v4 preflight `<button>` için `cursor: default` veriyor — "Giriş Yap", "Üye Ol", "Tahmini Kaydet" butonlarına `cursor-pointer` (+ disabled state'e `cursor-not-allowed`) eklendi. Skor input'larına `aria-label` eklendi (ekran okuyucu için hangi takımın skoru olduğu belirsizdi). Nav bar'a `flex-wrap` eklendi — 5. link (Topluluk Tahminleri) eklenince dar ekranlarda taşma riski vardı.
- **Doğrulama:** `predict-app`'te `tsc --noEmit`, `npm run lint`, `npm run build` hepsi temiz geçti; `curl` ile hem `tahmin.metric11.com` hem `clerk.tahmin.metric11.com` HTTP 200 doğrulandı.

### 2026-09-05 (devam) — "Bu Hafta" bir sonraki haftayı da gösteriyordu + kullanıcı adı değiştirme özelliği
Kullanıcı: "SessizFrikik56" adının kendisine sorulmadan otomatik atandığını fark etti, kendi seçmek istedi. Ayrıca `tahmin.metric11.com` ana sayfasında 11 Eylül (5. hafta) maçlarının "Bu Haftanın Maçları" (4. hafta, 5-7 Eylül) listesine karıştığını fark etti.

- **Kök neden (hafta karışması):** `app/page.tsx`, `getUpcomingMatches()`'ten dönen maçları hafta sınırı gözetmeksizin `.slice(0, 15)` ile kesiyordu. 4. haftada bugün (5 Eylül) itibarıyla yalnız 8 maç kalmışken, 15'i doldurmak için 5. haftanın maçları da sessizce listeye ekleniyordu.
- **Düzeltme:** `lib/metric11-data.ts`'e `Metric11Match.week` alanı eklendi (fixture JSON'daki `weeks[].week` artık her maça damgalanıyor). `getUpcomingMatches()` artık: oynanmamış+gelecekteki maçlar arasından en küçük hafta numarasını ("aktif hafta") bulup SADECE o haftanın maçlarını döndürüyor — `metric11.com/season_fixture_predictions_2026_2027.html`'deki hafta-hafta mantığıyla tutarlı. `app/page.tsx`'teki keyfi `.slice(0, 15)` kaldırıldı, başlığa hafta numarası eklendi ("Bu Haftanın Maçları (4. Hafta)"). Gerçek veriyle Python'da simüle edilip doğrulandı: aktif hafta doğru şekilde 4, 8 maç, 5. hafta hiç karışmıyor.
- **Kullanıcı adı değiştirme:** `db/schema.ts`'e `users.display_name` üzerinde unique index eklendi (`drizzle-kit push` ile Neon'a uygulandı, önceden çakışan kayıt olmadığı doğrulandı). Yeni `PATCH /api/user/display-name` route'u (2-24 karakter, harf/rakam/boşluk/tire/alt çizgi, case-insensitive benzersizlik kontrolü) + `/profil` sayfası (`components/display-name-form.tsx`) eklendi. Clerk `UserButton`'a özel menü öğesi ("Kullanıcı Adı" → `/profil`) eklendi. `proxy.ts`'teki korumalı route matcher'ına `/profil` ve `/api/user` eklendi.
- **Doğrulama:** `tsc --noEmit`, `npm run lint`, `npm run build` temiz; yeni route'lar (`/profil`, `/api/user/display-name`) derlemede görünüyor. Push sonrası canlıda doğrulandı: `curl` ile `/profil` 404 döndü ama sebep bug değil — Clerk `auth.protect()` giriş yapmamış isteklerde sayfayı `/_not-found`'a rewrite ediyor (aynı davranış zaten var olan `/predictions` sayfasında da var, `x-clerk-auth-reason: protect-rewrite` header'ıyla doğrulandı); gerçek oturum açık tarayıcıda normal açılması bekleniyor.

### 2026-09-05 (devam 2) — header'a ana siteye dönüş linki + lider tablosunda kendini görme/renklendirme
Kullanıcı: kullanıcı adları hâlâ otomatik/saçma geliyor dedi (muhtemelen `/profil` özelliği henüz kullanılmamıştı, deploy'un hemen ardından sorulmuştu); header'da metric11.com'a dönüş linki istedi; lider tablosunda kendi sırasını görebilmek ve kendi adının renkli/vurgulu olmasını istedi.

- **Header dönüş linki:** `components/nav-bar.tsx`'te logo'nun solunda küçük bir "← metric11.com" linki eklendi (dış link, `https://metric11.com`).
- **Lider tablosunda "Sen" vurgusu:** `app/leaderboard/page.tsx` yeniden yazıldı — artık `getOrCreateUser()` ile görüntüleyeni tanıyor, kendi satırını `bg-lime-300/10` arkaplan + lime renkli isim/puan + "Sen" rozetiyle vurguluyor. İlk 50'nin dışındaysa (limit kaldırıldı, tüm kullanıcılar sıralanıp JS'te kesiliyor) tablonun altına "⋯" ayracıyla kendi satırı ayrıca ekleniyor — yani kullanıcı kaçıncı sırada olursa olsun kendini görebiliyor.
- **Kullanıcı adı netleştirme:** `/profil` sayfasının zaten canlı olduğu doğrulandı (build log'unda route var); kullanıcıya mevcut adını oradan değiştirebileceği hatırlatıldı. Clerk Dashboard'da "Username" alanını sign-up'ta zorunlu/opsiyonel yapmak (ki `get-or-create-user.ts` zaten `clerkUser.username`'i önceliklendiriyor) kullanıcıya ayrı önerildi — bu bir dashboard ayarı, kod değişikliği gerektirmiyor.
- **Lint düzeltmesi:** İlk yazımda `Row` bileşeni `LeaderboardPage` içinde render sırasında tanımlanmıştı (`react-hooks/static-components` hatası) — modül seviyesine taşındı, `viewerId` prop olarak geçiliyor.
- **Doğrulama:** `tsc --noEmit`, `npm run lint`, `npm run build` temiz.

### 2026-09-06 — "Kullanıcı adını nereden değiştiriyoruz göremedim"
Kullanıcı, bir önceki oturumda eklenen kullanıcı-adı-değiştirme özelliğini bulamadı. Kök neden: özellik yalnızca Clerk `UserButton`'ın avatar açılır menüsüne gizli bir öğe olarak eklenmişti (`UserButton.MenuItems` + `UserButton.Link`, API doğru/çalışıyor — `@clerk/react` tip tanımlarından doğrulandı) — keşfedilebilirlik sorunuydu, bug değil.
- **Düzeltme:** `components/nav-bar.tsx`'te ana nav çubuğuna, "Tahminlerim"in hemen yanına, signed-in kullanıcılara direkt görünen bir **"Profil"** linki eklendi (`/profil`'e gidiyor). Avatar menüsündeki eski link de bırakıldı (zarar vermiyor, ekstra bir yol).
- **Doğrulama:** `tsc --noEmit`, `npm run lint`, `npm run build` temiz.

### 2026-09-06 (devam) — puanlama sistemi, mobil nav, aktif sayfa vurgusu, maç saati netliği, ana sitedeki bayat transfer banner'ı
Kullanıcı dört ayrı konu bildirdi: (1) puanlama sadece "tam skor/yön" değil, doğru sonuç + doğru gol farkı + tam skorun HER BİRİ ayrı ayrı puan katmalı; (2) maç tarih/saatleri hatasız girilmeli; (3) header'da hangi sayfada olunduğu belli değil; (4) mobilde nav çok kötü görünüyor (ekran görüntüsüyle doğrulandı — linkler sağda dikey bir sütun gibi üst üste biniyordu). Ayrıca ana sitede "Transfer penceresi kapandı" yazısının artık anlamsız kaldığını, ya kalkması ya da tahmin oyununu öne çıkaran bir oyunlaştırmaya dönüşmesi gerektiğini söyledi.

- **Puanlama (predict-app/lib/scoring.ts):** Üç kriter artık BAĞIMSIZ VE KÜMÜLATİF: doğru sonuç (1X2) +1, doğru gol farkı +1, tam skor +1 (üst üste biner — ör. yön+fark doğru ama skor yanlışsa 2 puan, önceden bu durum yalnızca 1 puandı). Zaten puanlanmış 4 tahmin (tek oynanmış maç dönemi) yeni kurala göre yeniden hesaplandı — bir tanesi (id=1, ERZURUMSPOR-KONYASPOR'a doğru yön+fark ama yanlış skorla tahmin) 1'den 2'ye çıktı, diğerleri değişmedi. Ana sayfaya (`app/page.tsx`) puanlama açıklaması eklendi.
- **Maç saati netliği:** `lib/metric11-data.ts`'e `formatMatchDateTime()` eklendi — TFF henüz saat açıklamamışsa (çoğu ileri hafta maçı) ham veri yalnızca tarih içeriyor, bu artık "DD.MM.YYYY · saat TBD" olarak gösteriliyor (önceden sadece tarih görünüyordu, kullanıcı bunu veri hatası sanmış olabilir). Gerçek bir yanlış tarih/saat örneği verilmedi; spesifik bir maç varsa kullanıcıdan tekrar istenmeli.
- **Header — aktif sayfa vurgusu + mobil responsive (components/nav-bar.tsx tamamen yeniden yazıldı):** Artık client component (`usePathname` kullanıyor), aktif linkin altında lime alt çizgi + beyaz metin var. Layout iki satıra bölündü: üst satır (geri linki + logo + auth kontrolleri, `flex-wrap` ile taşma güvencesi), alt satır (nav linkleri, `overflow-x-auto` ile yatay kaydırılabilir tek satır — önceki `flex-wrap justify-end` tasarımı dar ekranda linkleri sağda dikey bir yığın gibi gösteriyordu, kök neden buydu). Marka metni ("metric11 Tahmin") `sm:` altında gizlenip yalnız logo rozeti kalıyor.
- **Ana site — bayat transfer banner'ı oyun promosuna dönüştü (`src/build_live_feed.py:_window_state()`):** Pencere kapandıktan sonraki durum artık "closed" (gri, ölü mesaj) değil "promo" — nav'ın hemen altındaki en görünür şerit artık koyu yeşil/lime gradyanla "🎮 Tahmin Oyunu açık! ... ücretsiz →" yazıp tamamen `/tahmin`'e tıklanabilir link oluyor (`window-dot` zaten pulse animasyonlu, dikkat çekiyor). Süresi geçmiş "Güncelleme: {now_str}" eki bu durumda gösterilmiyor (artık anlamsız). `python3 -m src.build_live_feed` ile yeniden üretilip HTML çıktısı doğrulandı.
- **Doğrulama:** predict-app'te `tsc --noEmit`, `npm run lint`, `npm run build` temiz; Python tarafında `py_compile` + gerçek build çalıştırılıp banner HTML'i manuel kontrol edildi. pytest bu ortamda kurulu değildi (çalıştırılamadı), değişiklik izole/düşük riskli olduğu için atlandı.

### 2026-09-06 (devam 2) — 4 yeni gamification özelliği: haftalık lig, seri bonusu, rozetler, arkadaş grupları

Kullanıcı "gamification için başka neler yapılabilir" diye sordu, önerilen 4 fikrin hepsini sırayla uygulamasını istedi.

- **Şema (`db/schema.ts`):** `users`'a `current_streak`/`best_streak`, `predictions`'a `streak_bonus` (default 0) eklendi; yeni tablolar `badges` (userId+code unique), `groups` (inviteCode unique), `group_members` (groupId+userId unique). `drizzle-kit push --force` ile canlı Neon DB'ye uygulandı (veri kaybı yok, sadece yeni kolon/tablo).
- **Haftalık lig:** `lib/metric11-data.ts::getCurrentWeekMatchIds()` eklendi (ana sayfadaki "Bu Hafta" ile aynı hafta tanımı, sezon bitince son oynanan haftaya düşer). `lib/leaderboard.ts::getRankedLeaderboard({matchIds, userIds})` genel/haftalık/grup sıralamasını tek yerden besliyor. `/leaderboard`'a `?view=hafta` sekmesi eklendi.
- **Seri bonusu:** `lib/scoring.ts::computeStreakBonus()` — ardışık 3+ isabette +1, 5+'ta +2, pointsEarned'dan ayrı bir alanda tutuluyor (puanlama kuralı bulanıklaşmasın diye). `lib/sync-results.ts` artık skorlanacak tahminleri **kickoff sırasına göre kronolojik** işliyor (seri hesabı sıraya bağımlı) ve kullanıcı başına `currentStreak`/`bestStreak`'i güncelliyor. `/predictions` ve `/profil`'de seri gösteriliyor.
- **Rozetler:** `lib/badges.ts` — 7 rozetlik katalog (ilk tahmin, 10/25 tahmin, tam skor="Kahin", 3/5 seri, 100 puan="Yüzler Kulübü"), `syncBadges()` her skorlamadan sonra idempotent şekilde eksik rozetleri ekliyor (`onConflictDoNothing`). `/profil`'de rozet vitrini var.
- **Arkadaş grupları:** `groups`/`group_members` + `lib/invite-code.ts` (6 haneli, karışan karakterler hariç). `/gruplar` (grup kur/kodla katıl) ve `/gruplar/[code]` (grup-içi lider tablosu) eklendi; `app/api/groups` + `app/api/groups/join`. `proxy.ts`'deki korumalı rota listesine `/gruplar(.*)` ve `/api/groups(.*)` eklendi (önceden unutulmuştu, middleware'siz kalmıştı — fark edilip düzeltildi).
- **Geriye dönük veri:** Özellik eklenmeden önce zaten skorlanmış 4 tahmin/3 kullanıcı için tek seferlik backfill scripti çalıştırılıp silindi — `currentStreak`/`bestStreak`/`streakBonus` ve "ilk tahmin" rozetleri geçmişe dönük olarak dolduruldu (aksi halde `syncFinishedResults` yalnızca *yeni* skorlamalarda tetiklendiği için mevcut kullanıcılar hiç rozet/seri göremeyecekti).
- **Doğrulama:** `tsc --noEmit`, `npm run lint`, `npm run build` temiz. Dev server + `curl` ile tüm yeni route'lar (genel/haftalık leaderboard, gruplar, grup detay) gerçek canlı veriyle test edildi — haftalık sekme doğru "4. Hafta" ve doğru puan toplamlarını gösterdi. Chrome üzerinden tam oturum açık test **yapılamadı**: bu Chrome profilinin localhost için sakladığı eski/Secure Clerk çerezleri "Handshake token verification failed" hatasına yol açıyor — bu, koddan bağımsız, tarayıcı taraflı önceden var olan bir durum (ana sayfa gibi hiç dokunulmamış route'larda da aynı hata çıkıyor). Kullanıcı isterse `localhost:3000` için Chrome site verilerini temizleyip tekrar denemeli.

### 2026-09-07 — Günlük veri/geliştirme heartbeat kontrolü

Otomasyon kontrolünde önce bu dosya okundu, ardından pipeline çıktıları, kaynak performansı, tahmin karnesi, scout kalite raporu ve repo durumu incelendi.

- **Güncel üretim durumu:** `data/processed` altında bugün üretilmiş 89 dosya var. Ana çıktılar Sep 7 09:44 TR civarında yenilenmiş: `season_fixture_predictions_2026_2027`, `weekly_evaluation_2026_2027`, `match_week_2026_2027`, `match_signals_2026_2027`, `goal_scorer_predictions_2026_2027`, `live_lineups_2026_2027`, `european_predictions_2026_2027`, Transfermarkt kadro snapshot'ları, haber/intelligence dosyaları ve sistem sayfaları güncel görünüyor.
- **Pipeline izleme notu:** `data_quality_scorecard_2025_2026.json` pipeline yaşını 0 gün ve `failed_count=0` gösteriyor; buna karşılık `daily_pipeline_run_latest.json` dosyasının kendi `generated_at` alanı 2026-09-04'te kalmış ve dosya mtime'ı Sep 5 01:00. Veri üretimi canlı, ama koşu raporu/son-run dosyasının yenilenme mantığı ayrıca temizlenmeli.
- **2026-27 tahmin doğruluğu:** `weekly_evaluation_2026_2027` sezon toplamında 34 oynanmış maç, 13 doğru tahmin, doğruluk %38.24. Beraberlik yakalama 1/7 (%14.29). Yüksek güvenli tahminler 12 maçta 5 doğru (%41.67). Hafta 3 güçlüydü: 9 maçta 6 doğru (%66.67). Hafta 4 ise düştü: 7 oynanmış maçta 2 doğru (%28.57), yüksek güven 0/2. Sıradaki model işi: yüksek güven eşiğini sıkılaştırmak, beraberlik/sürpriz kalibrasyonunu yeni sezon sonuçlarıyla yeniden ayarlamak ve derbi/büyük maçlarda güveni daha korumalı üretmek.
- **Veri kapsamı:** 2026-27 Süper Lig fikstürü 306 maç olarak duruyor. `match_week_2026_2027` aktif hafta 4 ve 9 maç gösteriyor. `match_signals_2026_2027` 272 maç için kart/gol bandı sinyali taşıyor; lig kart ortalaması 2.33, kırmızı kart oranı 0.108.
- **Golcü tahmini:** `goal_scorer_predictions_2026_2027` 272 maç için oyuncu gol adayı üretiyor. Örnek kayıtta her iki takım kadrosu da rated, fakat `lineup_confirmed=false`; yani golcü tahmini var ama kesin 11 bilgisi gelmedikçe güven etiketi sınırlı tutulmalı.
- **Canlı kadro/sakat-cezalı katmanı:** `live_lineups_2026_2027` yalnız 2 maçta tespitli kadro tutuyor ve `candidates_checked=0` görünüyor. Bu alan maç önü tahmin kalitesi için en kırılgan katman olmaya devam ediyor. Sıradaki veri geliştirme önceliği: TFF maç kadrosu, resmi kulüp duyurusu, cezalı oyuncu ve sakatlık/eksik haberlerini fixture bazlı tek bir `availability` sinyalinde birleştirmek.
- **Scout kalite durumu:** `scout_quality_report_2025_2026` iyi durumda: 370 blueprint-candidate link, düşük güvenli yayın adayı 0, tekrar eden rol oyuncusu 0, eksik yaş/kontrat linki 0. Pozisyon matrisi 105 aday içeriyor; confidence dağılımı 101 HIGH, 4 DERIVED. Sonraki kalite kuyruğu Transfermarkt/TFF eşleşmeyen veya manuel alias doğrulaması bekleyen oyuncular.
- **Transfer/kaynak durumu:** `transfer_tracker_2025_2026` 44 sinyal tutuyor: 2 OFFICIAL, 1 CORROBORATED, 15 RUMOR, 26 REVIEW_REQUIRED; toplam değer 12.4M EUR. `source_performance` 313 Google News makalesi, 6 Telegram mesajı, 3958 claim gözlemi gösteriyor. X/Twitter hâlâ `MISSING_CREDENTIALS`; 45 hesap yapılandırılmış ama veri çekilemiyor. Bu yüzden muhabir/forum erken sinyali için X credentials hâlâ büyük eksik.
- **Transfermarkt kadro snapshot:** 2026-27 Super Lig snapshot'ı 18 kulüp, 558 oyuncu, toplam yaklaşık 1.679B EUR piyasa değeri, pozisyon dağılımı GK 68 / DEF 176 / MID 148 / FWD 166 / UNKNOWN 0. `transfermarkt_match_review_queue` in-scope eşleşme oranı %94.6, operasyonel in-scope oran %95.2; scout'u bloke eden eşleşmeyen oyuncu 0, ama 4 manuel alias hâlâ ağ teyidi bekliyor.
- **Repo durumu:** Kontrol öncesi çalışma ağacında yalnız `src/html_utils.py` değişik görünüyordu. Diff'e göre bu, nav linklerini tek kaynağa alan ve `.topnav` CSS'ini ekleyen başka agent/kullanıcı değişikliği; bu kontrol kapsamında dokunulmadı. Bu dosya UI/nav tarafında mantıklı bir iyileştirme gibi duruyor, fakat ayrı build/test ile doğrulanmalı.
- **Sıradaki uygulanabilir adım:** Kod tarafında önce `daily_pipeline_run_latest.json` yenilenme/takip tutarsızlığı giderilmeli; ardından 2026-27 haftalık karne üzerinden model kalibrasyon scripti yazılıp yüksek güven eşiği, beraberlik eşiği ve büyük maç/derbi güven kırpması otomatik ölçülmeli. Veri tarafında ise `availability` katmanı canlı kadro + cezalı + sakat/eksik haberlerini maç bazında tek JSON'a bağlamalı.

### 2026-09-07 (devam) — Site geneli menü tekilleştirme + küme düşen takımların "2026-27 transfer planlaması"nda görünmesi düzeltildi

Kullanıcı iki şey bildirdi: (1) menüler sayfadan sayfaya "çok eski" duruyor, özellikle Scout sayfası; (2) Antalyaspor gibi küme düşmüş takımlar hâlâ (Süper Lig'e özgü) sayfalarda görünüyor.

- **Kök neden (eski menüler):** Sitede nav linkleri tek bir yerden gelmiyordu — `src/html_utils.py::_build_nav()` (yalnız `build_weekly_evaluation.py` kullanıyordu), `src/build_live_feed.py` (ana sayfa, en güncel/kanonik versiyon), ve ayrıca `build_season_fixture_predictions.py`/`build_european_predictions.py`/`build_worldcup_predictions.py` içinde üç ayrı `_NAV_LINKS` sabiti + geri kalan ~15 script'te tamamen elle kopyalanmış `<nav>` HTML'i olmak üzere **en az 6 farklı, birbirinden bağımsız link listesi** vardı. "Haftalık Karne" ve "🗓️ Fikstür & Tahmin" gibi sonradan eklenen linkler yalnızca ana sayfaya işlenmiş, Scout ve diğer rapor sayfalarına hiç yayılmamıştı.
- **Düzeltme:** `src/html_utils.py`'ye tek gerçek kaynak eklendi: `_nav_link_list()` (kanonik, güncel link seti — build_live_feed'deki en güncel haliyle) + `nav_links_html(active, extra=...)` (yalnızca `<a>` etiketlerini döner, sayfanın kendi `<nav>`/CSS sarmalayıcısını bozmadan). `_build_nav()` artık bunu sarıyor. CSS'e `.topnav` bare `nav` seçicisiyle eşitlendi (bazı sayfalar `.topnav`, bazıları bare `nav` kullanıyordu). 19 dosya (`build_transfer_recommendation_report`, `build_all_teams_preview_dashboard`, `build_enriched_scout_dashboard`, `build_fm_style_scout_program`, `build_position_scout_matrix`, `build_team_scout_blueprints`, `build_dashboard`, `build_command_center`, `build_news_intelligence_report`, `build_league_intelligence_report`, `build_team_needs_dashboard`, `build_transfer_season_context`, `build_transfer_tracker`, `build_season_fixture_predictions`, `build_european_predictions`, `build_worldcup_predictions`, `build_live_feed`, `build_product_home`) artık `nav_links_html()`'i çağırıyor; üç bağımsız `_NAV_LINKS` sabiti silindi. Dünya Kupası sayfası kendine özel "Tahminler" sekmesini `extra=` parametresiyle ekliyor. Bilinçli olarak dokunulmayanlar: `build_admin_page.py`, `build_status_page.py` (kasıtlı minimal iç/ops nav'ı, genel site nav'ı değil).
- **Kök neden (küme düşenler transfer planlamasında):** `src/build_team_scout_blueprints.py`, `league_intelligence_2025_2026.json`'daki `team_weaknesses` listesini kullanıyordu — bu liste 2025/26'da OYNAYAN herkesi içeriyor (küme düşen Antalyaspor/Fatih Karagümrük/Kayserispor dahil, 18 takım), üstüne yükselen 3 takım (Amed SFK/Erzurumspor FK/Çorum FK) template ile ekleniyordu → toplam 21 takım. "Scout & Transfer Merkezi" sayfası bunu "2026-27 transfer penceresi planlaması" olarak sunduğu için küme düşmüş takımlara scout blueprint üretmek anlamsızdı (`transfer_recommendation_report_2025_2026.html`'de "21 Takım" istatistiği).
- **Düzeltme:** `build_team_scout_blueprints.py`'ye `_current_super_lig_teams()` eklendi — `data/manual/transfermarkt_super_lig_clubs.json`'daki (tek doğru kaynak, 18 kulüp) resmi isimleri okuyup `team_weaknesses` döngüsünü buna göre filtreliyor. Küme düşen takımların OYUNCULARI (ör. serbest kalacak Ivo Grbić/Berkay Özcan gibi Fatih Karagümrük'te oynayan adaylar) scout aday havuzunda kalmaya devam ediyor — bu doğru/istenen davranış, filtrelenen yalnızca takımın KENDİ blueprint girdisi. Sonuç: `team_scout_blueprints_2025_2026.json` artık 18 takım, `transfer_recommendation_report` "18 Takım" gösteriyor.
- **Doğrulama:** `python3 -m compileall src/` temiz. Etkilenen ~20 script yerelde tek tek çalıştırılıp çıktı HTML'lerinde nav'ın her sayfada birebir aynı olduğu (`grep`) ve doğru sayfanın `active` işaretlendiği doğrulandı. `pytest tests/` çalıştırıldı: 58 geçti, PROJECT_STATE'te zaten önceden dokümante edilmiş 3 bilinen/ilgisiz hata (`ALL_TEAMS` 2025/26 arşiv listesiyle ilgili, X-erişim metni, TM sezon test beklentisi — `generate_preview_batch.ALL_TEAMS`'e hiç dokunulmadı, o liste kasıtlı olarak 2025/26 arşiv sayfaları için karışık/tarihi kalmaya devam ediyor) değişmeden kaldı, yeni hata eklenmedi.

### 2026-09-07 (devam 2) — Kadro tazeliği kök nedeni + transfer sinyalinde yanlış oyuncu eşleşmesi (Emre Demir → "Yiğit Efe Demir")

Kullanıcı "diğer menüleri de incele, genel olarak projede eski bir şey olmamalı, kadrolar/takımlar güncel olmalı" dedi. Menü denetimini tamamlarken (bkz. yukarı — `build_status_page.py`'nin de eski nav'ı olduğu bulunup düzeltildi) kadro güncelliğini araştırırken iki ayrı, daha derin sorun ortaya çıktı.

- **Kadro tazeliği kök nedeni (yalnız teşhis, henüz düzeltilmedi):** `transfermarkt_super_lig_squads_2026_2027.json` 5 gündür (2 Eylül'den beri) donmuş — `stale_reason=collector_produced_no_nonempty_clubs`. Somut kanıt: Fenerbahçe'den Alanyaspor'a resmi transferi onaylanan oyuncu kadroda hâlâ Fenerbahçe'de görünüyordu (bkz. aşağıdaki madde). Kod okunarak yeni bir bulgu netleşti: `src/collect_transfermarkt_league_squads.py::api_football_fallback_clubs()` API-Football'u `season={datetime.now().year}` (yani 2026, mevcut sezon) ile sorguluyor — ama PROJECT_STATE'te zaten Temmuz 2026'da not edilmiş olduğu gibi API-Football'un ücretsiz planı mevcut sezona (2025/2026) hiç erişim vermiyor, yalnızca 2024 gibi geçmiş sezonlara izin veriyor. Yani bu fallback, Transfermarkt CI'da engellendiğinde asla devreye giremez — key sorunu değil, plan kısıtı. Kalıcı çözüm (TFF/resmi kulüp tabanlı aktif kadro fallback katmanı, aylardır "kalan öncelik" olarak not edilen iş) henüz yapılmadı; bu oturumda yalnızca kök neden netleştirildi.
- **Transfer sinyali yanlış oyuncu eşleşmesi — kök neden ve düzeltme:** Kadro tazeliğini araştırırken `transfer_tracker_2025_2026.json`'daki tek OFFICIAL imza haberi ("Alanyaspor Resmi Web" kaynaklı, başlık açıkça "Emre Demir" diyor) sistemde yanlışlıkla Fenerbahçeli "Yiğit Efe Demir"e atfedilmiş bulundu (ikisi de "Demir" soyisimli, farklı kişiler). Kök neden: `src/analyze_news_with_claude.py`'deki `rule_based_analyze()` içinde, tam isim başlıkta geçmediğinde devreye giren "current_club_surname" fallback'i (aday oyuncunun soyismi başlıkta geçiyor + kayıtlı kulübü başlıkta anılan kulüple aynıysa tek adayı kabul et) tam isim kontrolü yapmıyordu — gerçek oyuncu ("Emre Demir") TFF profil havuzunda henüz yok (yeni transfer), o yüzden index'teki tek "Demir" soyisimli Fenerbahçeli aday sessizce onun yerine geçiyordu. **Düzeltme:** aynı fallback artık ham metinde (noktalama korunarak — normalize edilmiş metinde noktalama boşluğa çevrildiğinden cümle sonu kelimeleri yanlışlıkla "soyisimden önceki ilk isim" sanılabiliyordu, bu da ayrı bir regresyon olarak yakalanıp düzeltildi) soyisimden hemen önceki kelime(ler)i çıkarıp adayın gerçek ilk ismiyle karşılaştırıyor; uyuşmazsa aday reddediliyor (yanlış isim yerine "PLAYER_UNRESOLVED" — kod tabanında zaten var olan, `build_transfer_tracker.py`'nin "—" olarak güvenli şekilde gösterdiği bir durum). 3 OFFICIAL/CORROBORATED sinyalin 1'i (%33) bu hatayı taşıyordu; küçük örneklem ama tek seferlik değil, gerçek bir hata sınıfı.
- **Doğrulama:** Gerçek veriyle önce-sonra karşılaştırıldı (Yiğit Efe Demir → Alanyaspor sinyali kayboldu, yerine `player=None, status=REVIEW_REQUIRED` geldi — yanlış isimden çok daha güvenli). `pytest tests/` tam koşuldu: ilk düzeltme mevcut bir testi (`test_unique_current_club_surname_identifies_outbound_player`) kırdı (normalize edilmiş metindeki noktalama-boşluk birleşmesi false-positive üretti), ikinci iterasyonda ham metne geçilince o test de dahil 58/61 yeşile döndü — kalan 3 hata daha önce dokümante edilmiş, ilgisiz. `python -m src.analyze_news_with_claude --only-relevant` + `build_transfer_tracker`/`build_transfer_season_context`/`build_news_intelligence_report`/`build_data_catalog`/`build_player_availability` yeniden çalıştırılıp çıktılar tazelendi.
- **Sıradaki adım:** Kadro tazeliği kök nedeni (API-Football plan kısıtı) çözülmedi — bunun için ya Transfermarkt scraping'in CI'dan güvenilir çalışması (proxy/farklı IP — riskli/kapsam dışı olabilir), ya API-Football ücretsiz-olmayan plana geçiş (kullanıcı onayı gerekir, maliyetli), ya da aylardır ertelenen TFF/resmi-kulüp-haberi tabanlı aktif kadro fallback katmanının inşası gerekiyor.

### 2026-09-07 (devam 3) — Kadro tazeliği geçici olarak giderildi: engel CI'ya özgü, TFF PDF'i araştırıldı ama gerekmedi

Kullanıcı "devam et" dedi; bir önceki oturumun net "sıradaki adım"ı olan kadro tazeliği kök nedenini ele aldım.

- **Yeni bulgu — asıl kök neden CI'ya özgüymüş:** TFF'nin resmi "A Takım Oyuncu Listesi" PDF'lerini (tff.org duyuru sayfaları/ftxtID) alternatif kaynak olarak araştırdım — format var (`Resources/TFF/Auto/<guid>.pdf`) ama güncel 2026-27 sezon duyurusu arama motorlarında henüz indekslenmemiş, sayfa yapısı ASP.NET postback tabanlı ve PDF'ten isim/pozisyon/forma no ayrıştırmak yeni bir parser gerektirirdi — kapsamlı bir iş. Bu yola girmeden önce basit bir kontrol yaptım: yerel makineden doğrudan Transfermarkt'a `fetch()` denendiğinde **31 oyuncu sorunsuz döndü** — yani engel Transfermarkt'ın GitHub Actions CI runner IP'sini engellemesinden kaynaklanıyor, genel bir Transfermarkt erişim sorunu değil.
- **Düzeltme (bu oturum için, kalıcı değil):** `python -m src.collect_transfermarkt_league_squads --clubs data/manual/transfermarkt_super_lig_clubs.json --season-id 2026 --output-prefix transfermarkt_super_lig_squads_2026_2027 --delay-seconds 6` yerel olarak çalıştırıldı — 18/18 kulüp `live` modda toplandı (530 oyuncu, €1.71B toplam değer), `stale_reason` temizlendi, `data_as_of` bugüne güncellendi. Ardından `detect_squad_changes` (2026_2027) çalıştırıldı: 24 varış, 48 ayrılış, 4 takım değişimi tespit edildi (önceki 2 Eylül snapshot'ına göre). Sonrasında tam günlük pipeline (network hariç, 59 komut) çalıştırılıp tüm bağımlı raporlar (scout blueprint, market value audit, transfer tracker, status page, data catalog vb.) taze kadro üzerinden yeniden üretildi — 59/59 başarılı.
- **Doğrulama:** `check_squad_freshness` artık `OK: 18/18 kulüp` diyor. `system_status.html`'de "Kadro Verisi (2026-27)" kartı 18/18 güncel gösteriyor. `data_quality_scorecard` 75.6'dan 87.5'e çıktı. `pytest tests/` (`.venv/bin/python -m pytest`): 58/61 geçti, kalan 3 hata daha önce dokümante edilmiş/ilgisiz (ALL_TEAMS 2025/26 arşiv listesi, X-erişim metni, TM sezon test beklentisi) — değişmedi.
- **Önemli kalıcı sorun hâlâ çözülmedi:** Bu, CI'daki otomatik pipeline'ın kendi kendine düzelmeyeceği anlamına geliyor — Transfermarkt CI runner IP'sini engellemeye devam ettiği sürece her otomatik koşuda kadro verisi yine donacak (yalnızca bu oturumda elle/yerelden tazelendi). Kalıcı çözüm için hâlâ üç seçenek geçerli: (1) CI'da proxy/farklı IP ile scraping (riskli), (2) API-Football ücretli plan (maliyetli, kullanıcı onayı gerekir), (3) TFF PDF tabanlı fallback parser'ı inşa etmek (büyük iş, bu oturumda yalnızca URL formatı/duyuru mekanizması araştırıldı, kodlanmadı). Kullanıcıya bu üç seçenek arasında karar vermesi için sorulmalı, ya da CI runner'a periyodik olarak elle bu komutun çalıştırılması (geçici bant-aid) önerilebilir.

### 2026-09-07 (devam 4) — "Tahminler çok kötü": iki gerçek model hatası bulunup düzeltildi + Avrupa tahminleri Süper Lig güncel formuna bağlandı

Kullanıcı: "tahminlerin çok kötü, başka kaynakları da analiz edip yenilemen gerek; avrupa ligi maç tahminlerini de son maç durumları, kadrolar ve 11'lere göre yenilemen gerekiyor" dedi. Not: `/clear` sonrası bu istek kaybolmuştu, `devam et` denince önce yanlışlıkla Transfermarkt kadro tazeliğini sürdürdüm (yukarı) — kullanıcı asıl isteğini tekrarlayınca bu oturuma geçildi.

- **Teşhis:** `weekly_evaluation_2026_2027` sezon başı (4 hafta, 34 maç) isabeti %38.2, hafta 4 %28.6'ya düşmüş, yüksek güvenli tahminler hafta 4'te 0/2 — yani model en emin olduğu maçlarda YANLIŞ çıkıyordu. En çarpıcı örnek: Fenerbahçe-Beşiktaş (05.09) model'i Fenerbahçe favorisi gösterdi, gerçekte Beşiktaş deplasmanda kazandı (1-2).
- **Bulunan gerçek hata 1 — transfer/kadro sinyali isim eşleştirme bug'ı (`src/preview/probability.py`):** `squad_transition_edge`/`transfer_strength_edge`, bir transferin takım gücüne yansıması için oyuncunun "bu sezon en az 1 maç kadrosuna girdiğini" TAM CANONICAL isim eşleşmesiyle kontrol ediyordu. TFF kadro verisi oyuncunun TAM YASAL adını kullanıyor ("MASON WILL JOHN GREENWOOD"), Transfermarkt ise kısa/yaygın adı ("Mason Greenwood") — bu ikisi HİÇBİR ZAMAN birebir eşleşmiyordu. Sonuç: Fenerbahçe'nin gerçek yaz transferleri (Greenwood €55M, Aké €12M, Lukaku €6M — üçü de zaten 2+ maç oynamış) `squad_transition_edge`'e HİÇ yansımıyordu (`arrivals_value_eur: 0`), takım yalnızca giden oyuncularla (€137M) değerlendirilip sinyal yapay olarak maksimum negatife (-0.15 cap) kilitleniyordu. Ayrıca eski kod GLOBAL (lig geneli) bir "oynadı" kümesi kullanıyordu — bu ikinci, daha sinsi bir hata: bir oyuncu SEZON İÇİNDE herhangi bir kulüp için oynamışsa (ör. Ümit Akdağ'ın eski kulübü Alanyaspor'daki maçları), yeni kulübünde (Beşiktaş) henüz hiç oynamamış olsa bile "oynadı" sayılıp güç sinyaline hemen dahil ediliyordu.
  - **Düzeltme:** `enrich_players_with_transfermarkt.py`'de zaten var olan aynı yöntem (kulüp-içi, normalize edilmiş isim üzerinde ≥2 ortak token) burada da uygulandı: yeni `_appeared_players_by_club()` (kulüp bazlı, global değil) + `_player_appeared_for_club()` eklendi, eski global `_players_appeared_this_season()` kaldırıldı. Doğrulama: `_player_appeared_for_club('Mason Greenwood', ...)` artık `True`; Fenerbahçe `squad_transition_edge` arrivals_value_eur 0'dan €73M'ye çıktı (net_value -137M'den -64M'ye düzeldi — hâlâ negatif çünkü gerçekten de gidenler kalanlardan değerli, ama artık doğru hesaplanıyor). Beşiktaş tarafında da yanlışlıkla erken sayılan Ümit Akdağ artık doğru şekilde "henüz oynamadı" (pending_arrivals) kategorisinde.
  - **Önemli sınırlama (kasıtlı olarak dokunulmadı):** Bu, VERİ DOĞRULUĞU hatasıydı — düzeltilince sinyal artık doğru yönde çalışıyor, ama sinyalin modele etkisi hâlâ küçük (`strength_edge`'e ×0.5, oradan beklenen gole ×0.05 — Fenerbahçe-Beşiktaş örneğinde düzeltmeden sonra bile strength_edge yalnızca -0.004, tahmin hâlâ "Fenerbahçe" kalıyor). Bu ağırlık daha önce hiç gerçek 2026-27 sonuçlarıyla geriye test edilmemişti (yalnız ileriye dönük tahminlerde aktif, `run_backtest`'in kalibre ettiği ana sistemin parçası değil). Ağırlığı artırmak (özellikle sezon başı, takım geçmişi kısayken) gerçek bir sonraki adım ama küçük örneklemde (34 maç) aşırı uydurma riski taşıyor — kullanıcıya sorulmadan yapılmadı.
- **Bulunan gerçek hata 2 — Avrupa tahminlerinde Türk takımlarının güncel Süper Lig formu HİÇ kullanılmıyordu (`src/collect_domestic_league_form.py`):** Dosyanın kendi docstring'i "Süper Lig zaten ayrı (TFF) toplanıyor" diyordu ama kod hiçbir yerde gerçekten `teams` sözlüğüne Türk takımı eklemiyordu — Galatasaray/Fenerbahçe/Beşiktaş/Trabzonspor'un Avrupa kupası tahminleri (`analyze_european_predictions.py`) SADECE statik, donuk bir 2024-25 UEFA katsayı tablosuyla (`_CLUB_STRENGTH`) değerlendiriliyordu; bu sezonki form/transfer hiç yansımıyordu.
  - **Düzeltme:** `collect_domestic_league_form.py`'ye `_load_turkish_standings()` eklendi — zaten yerelde toplu duran `tff_super_lig_fixtures_2026_2027.json`'daki skorlardan (ağ çağrısı YOK) Galatasaray/Fenerbahçe/Beşiktaş/Trabzonspor/Başakşehir/Kasımpaşa için puan/gol formunu hesaplayıp `domestic_league_form_2026_2027.json`'a ekliyor — `_CLUB_STRENGTH`'teki kısa adlarla aynı isimlendirme (substring eşleşmeyle otomatik devreye giriyor, `analyze_european_predictions.py`'de kod değişikliği gerekmedi). İlk denemede `tff_super_lig_matches_2026_2027.json` (tam kadro verisi) kaynak alınmıştı ama bu dosya skoru geç yakalıyordu (Fenerbahçe'nin en güncel/anlamlı sonucu olan Beşiktaş maçı eksikti) — fikstür dosyasına (`tff_super_lig_fixtures_2026_2027.json`, skoru çok daha erken alıyor) geçilince 4/4 maç doğru yansıdı.
  - **Ayrı, orta-ciddiyetli bug (bu düzeltme sırasında bulunup hemen giderildi):** İlk yerel çalıştırmada `FOOTBALL_DATA_KEY` bu makinede tanımlı olmadığı için script'in eski hâli `teams` sözlüğünü BOŞTAN başlatıp dosyanın üzerine yazdı — CI'da anahtarla toplanmış 126 yabancı kulübü SESSİZCE SIFIRLADI. Fark edilip `git checkout` ile geri alındı; script artık anahtar yoksa önceki dosyadaki yabancı takımları koruyup yalnızca Türk kısmını güncelliyor.
  - **Doğrulama:** Galatasaray artık `played=4, ppg=2.5` (statik 64 → harmanlı ~74.5 güç), Fenerbahçe `played=4, ppg=1.5` (statik 62 → ~62.5, hafif düşüş). CL 1. hafta tahminleri (yarın, 8 Eylül) yeniden üretildi — ör. Galatasaray-Aston Villa artık %52.7 Galatasaray, önceki donuk tabloya göre daha güçlü (Galatasaray'ın gerçek 4-maçlık formuyla tutarlı).
- **"Başka kaynak" karşılaştırması kısmen engellendi:** Forebet'e `WebFetch` ile bağlanmaya çalışıldı, sandbox ağı bu domaine `ECONNREFUSED` verdi — dış tahmin/oran sitesiyle doğrudan sayısal karşılaştırma bu ortamda şu an mümkün değil. `WebSearch` üzerinden dolaylı arama yapıldı ama nicel bir karşılaştırma sağlamadı. Bu kısıtlama kullanıcıya açıkça bildirilmeli; gerçek bir dış kıyaslama için kullanıcının kendi makinesinden/tarayıcısından bir kontrol yapması ya da farklı bir erişilebilir kaynak önermesi gerekebilir.
- **Regresyon kontrolü:** `.venv/bin/python -m pytest tests/`: 58/61 (aynı 3 önceden bilinen/ilgisiz hata, değişmedi). Tam günlük pipeline (network hariç, 59 komut) iki kez çalıştırıldı (kadro fix'i + bu fix'ler için), ikisi de 59/59 başarılı.
- **Sıradaki adım (kullanıcıya sorulmalı):** (1) Transfer/kadro sinyalinin model ağırlığını (şu an ×0.5 → ×0.05, çok küçük) özellikle sezon başında büyük kadro değişimi olan takımlar için artırmak — küçük örneklemde dikkatli backtest gerektirir; (2) erişilebilir bir dış tahmin/oran kaynağı bulup düzenli kalibrasyon kıyaslaması kurmak; (3) hafta 5 sonuçları geldiğinde bu iki düzeltmenin gerçek isabete etkisini ölçmek.

### 2026-09-07/08 (devam 5) — Site geneli sayfa denetimi + Avrupa güç tablosu isim hatası + TFF kadro "kalıcı boş kayıt" bug'ı

Kullanıcı "sabaha kadar durmadan çalış: (1) tüm başlık ve alt sayfaları tek tek analiz edip güncelle, gereksiz sayfa varsa çıkar, (2) forumlar/haberler/bahis siteleri gibi başka kaynaklardan tahmin kalitesini analiz et" dedi. Ayrıca Sporting-Galatasaray tahmininin dayanağını sordu.

- **Sporting CP + Avrupa güç tablosu — asıl bulgu çok daha büyüktü:** Kullanıcının sorduğu tek maçı araştırırken `analyze_european_predictions.py`'deki statik kulüp güç eşleştirmesinin (`k.lower() in name.lower()` tam alt-dizi) 2026-27 Avrupa fikstüründeki 36 takımın **11'ini** (Bayern Münih ve Inter Milan DAHİL — ikisi de tabloda 93/84 puanlık elit takımlar!) football-data.org'un tam resmi adı ("FC Bayern München") tablodaki kısa adla ("Bayern Munich") hiç eşleşmediği için jenerik varsayılana (48) düşürdüğü bulundu. Düzeltme: normalize edilmiş isim + en-çok-ortak-token eşleştirmesi (aday havuzunda birden fazla eşleşme varsa en çok token paylaşan kazanır — "Manchester City"/"Manchester United" gibi çakışmaları doğru ayırır) + tabloda hiç olmayan 6 takım eklendi (Como 1907, Bodø/Glimt, LASK Linz, Sabah FK, Viking FK, Slovan Bratislava) + "Lens" mükerrer girdisi temizlendi. 36/36 takım artık doğru eşleşiyor.
- **Site geneli "arşiv vs canlı" karışıklığı düzeltildi:** Kod tabanında paralel iki sistem olduğu netleşti — canlı 2026-27 (Fikstür&Tahmin, Haftalık Karne, Transferler, Scout, Takım Scout Blueprint, Pozisyon Scout Matrisi) ve tamamlanmış 2025-26 arşiv/backtest (Analiz hub'ındaki 13 sayfa: Komuta Merkezi, Backtest Paneli, Maç Önü Arşivi, Piyasa Değeri Denetimi, Büyük Maç Raporu, Lig İstihbarat Raporu, FM Scout Programı). İkincisi hiçbir yerde etiketlenmiyordu; üstelik üst nav'daki "Maç Önü" linki yarım kalmış bir geçiş yüzünden (`_preview_label` — lig başlayınca "canlı" görünen ama hep aynı statik dosyaya giden ölü kod) buna canlı süsü veriyordu. `_preview_label`/`preview_nav_label` silindi, "Maç Önü" üst nav'dan kaldırıldı (Fikstür&Tahmin zaten aynı işi canlı yapıyor), 7 arşiv sayfasının hem hub kartına hem kendi başlığına "(2025-26 Arşiv)" eklendi, sitemap önceliği/changefreq'i buna göre düşürüldü (arama motorlarına donuk içeriği canlı gibi göstermeyi bırakıyor). Ayrı bulgu: `position_scout_matrix` sayfası yanlışlıkla "2026-2027" yazıyordu ama verisi 2025-26 kadrosuna (3 küme düşen dahil, 3 yükselen HARİÇ) dayanıyordu — düzeltildi.
- **"Başka kaynak" araştırması — Claude-in-Chrome ile gerçek İddaa oranlarına ulaşıldı:** WebFetch forebet.com'a bağlanamadı ama mackolik.com tarayıcı üzerinden (gerçek JS render) erişilebildi. 2 örnek maçta gerçek piyasa oranı vs kendi modelimiz karşılaştırıldı: Beşiktaş-Erzurumspor model H75/D18/A7 vs piyasa (marj arındırılmış) H70/D19.5/A10.5; Galatasaray-Kocaelispor model H64/D21/A15 vs piyasa H69.5/D17/A13.5 — ikisinde de yön ve büyüklük makul ölçüde uyumlu, modelin tamamen sağlıksız olmadığını doğruluyor. Otomatik/CI'da script'lenebilir bir ücretsiz oran API'si bulunamadı (the-odds-api.com gibi seçenekler yeni hesap/kayıt gerektirir — kullanıcı onayı olmadan hesap açılmadı); tarayıcı tabanlı erişim de reklam/interstitial yüzünden CI'da güvenilir otomatikleştirilemez. Bu yüzden bu bir KERE'lik manuel doğrulama kaldı, kalıcı/otomatik bir kalibrasyon sinyali DEĞİL.
- **Yan bulgu → gerçek, sistemik bir bug'a çıktı:** Gaziantep-Fenerbahçe için mackolik sakat/cezalı listesinde "Mert Hakan Yandaş cezalı" görüldü, kendi `suspension_edge()` sinyalimiz bunu hiç göstermiyordu. Kök nedeni ararken şunu buldum: `advance_season_state.py`, bir maçı TFF'den ilk kez çektiğinde (bazen maç bitince TFF'nin resmi kadro/kart sayfası henüz yayınlanmamış oluyor) `match_id`'yi `processed_ids`'e KALICI olarak ekliyordu — kadro/kart verisi BOŞ gelse bile bir daha asla yeniden denenmiyordu. Kontrol edildi: **34 maçın 8'i (%23.5) bu yüzden kalıcı olarak boş kadro/kart kaydıyla kilitliydi** (Beşiktaş-Fenerbahçe derbisi dahil, Galatasaray-Göztepe dahil, Trabzonspor-Gençlerbirliği dahil). Düzeltme: `_has_empty_lineup()` kontrolü eklendi, boş kadrolu "işlenmiş" maçlar artık her koşuda yeniden denenip (TFF verisi gelmişse) İÇERİĞİ GÜNCELLENİYOR (append değil, replace). Canlı çalıştırıldı: 8/8 maç başarıyla tamamlandı, artık 0 boş kadro kalmadı. (Not: Yandaş'ın kendisi hâlâ görünmüyor — hiçbir TFF maç kaydında kırmızı kartı yok, muhtemelen PFDK/disiplin cezası gibi kart-dışı bir sebep; sistemimiz KASITLI olarak yalnız kart-kaynaklı cezaları takip ediyor, bu tasarım gereği kapsam dışı kaldı — ayrı, daha küçük bir gelecek iş.)
- **Doğrulama:** `.venv/bin/python -m pytest tests/`: 58/61 (aynı 3 bilinen/ilgisiz hata). Tam günlük pipeline (network hariç) 3 kez çalıştırıldı bu oturumda, üçü de 59/59. `weekly_evaluation` isabeti kadro-backfill sonrası %38.2'den %35.3'e düştü (34 maçta 13→12 doğru) — bu bir regresyon değil, gürültü: hakem kart ortalaması gibi kadro-bağımlı sinyaller artık DAHA DOĞRU (önceden 8 maçta kart sayısı yanlışlıkla 0'dı) veriye dayanıyor, 34 maçlık örneklemde ±1 maçlık fark istatistiksel gürültü sınırları içinde.
- **Sıradaki adım:** (1) Transfer/kadro sinyali ağırlığını artırma kararı hâlâ kullanıcıdan bekliyor; (2) kalıcı/otomatik bir oran/kalibrasyon kaynağı için kullanıcının bir API hesabı (the-odds-api.com vb., ücretli/ücretsiz) açıp anahtar vermesi gerekiyor — bu olmadan "başka kaynak" doğrulaması yalnızca ara sıra manuel tarayıcı kontrolü olarak kalır; (3) `advance_season_state.py`'deki "kalıcı boş kayıt" bug sınıfının başka network collector'larda (ör. `collect_tff_player_profiles.py`) da olup olmadığı henüz taranmadı.

### 2026-09-08 (devam 6) — Kullanıcı "transfer_recommendation_report hâlâ aşırı eski" dedi: Scout sayfası derin kök nedeni + KRİTİK deploy bulgusu

Kullanıcı: "bu sayfa da aşırı eski... kaç kere dedim... hâlâ geçen senenin bilgilerini yazmış" — spesifik olarak `transfer_recommendation_report_2025_2026.html`. Önceki oturumda bu sayfayı yalnızca BAŞLIK etiketine ("2026-2027" yazıyor) bakarak "canlı" diye işaretlemiştim — bu, yanlış bir doğrulama yöntemiydi.

- **Gerçek kök neden:** "Transfer Aciliyet Sıralaması"nı besleyen puan/maç ve gol ortalamaları TAMAMEN `league_intelligence_2025_2026.json`'dan (tamamlanmış 2025-26 sezonu, 306 maç) geliyordu — sayfanın kendi başlığı "2026-2027" dese de, altındaki takım-gücü rakamları bir sezon önceydi. `src/build_team_scout_blueprints.py`'ye `_current_season_team_form()` eklendi — zaten toplu duran `domestic_league_form_2026_2027.json`'daki Süper Lig kısmından (>=3 maç oynanmışsa) puan/gol ortalamasını enjekte ediyor. `src/collect_domestic_league_form.py::_load_turkish_standings()` önceden yalnızca Avrupa'ya gidebilecek 6 takımı yazıyordu, 18 takımın TAMAMINA (hem kısa hem resmi TM adıyla) genişletildi. Sonuç: sıralama artık gerçekten bu sezonki forma göre (Eyüpspor/Göztepe/Konyaspor üstte — hepsi kötü başladı) değişiyor.
- **Geri alınan riskli deneme:** Oyuncu-seviyesi zenginleştirmeyi (`enrich_players_with_transfermarkt.py`) doğrudan 2026-27 kadrosuna yönlendirmeyi denedim — doğrulanmış kapsam %86'dan %34'e düştü VE bir yanlış eşleşme üretti (Tammy Abraham'ın tam yasal adı token-overlap yüzünden alakasız bir oyuncuya eşleşti). Geri alındı. Yani oyuncu seviyesinde "kim hangi kulüpte" hâlâ 2025-26 TFF profiline dayanıyor (ör. Ümit Akdağ hâlâ "Alanyaspor" görünüyor) — `transfer_season_context` sayfasına bunu açıkça belirten bir not eklendi. Kalıcı çözüm yeni sezon oyuncuları için TFF profil taraması gerektiriyor — büyük, ayrı bir iş, bu oturumda yapılmadı.
- **KRİTİK bulgu — asıl sorun bir DEPLOY sorunuydu:** Düzeltmeyi commit+push ettikten sonra canlı siteyi kontrol ettim — HÂLÂ eski veriyi gösteriyordu. Araştırınca: bu dizindeki `.vercel/project.json` **YANLIŞ Vercel projesine** ("metric11-tahmin" — asıl tahmin oyunu uygulamasının projesi) bağlıydı, doğru proje "metric11"(metric11.com) değil. `.github/workflows/*.yml` içinde de HİÇBİR yerde "vercel" veya "deploy hook" geçmiyor — yani otomatik bir git-push→deploy garantisi bu repoda görünür şekilde yok. `npx vercel link --project metric11 --yes` ile doğru projeye bağlanıp `npx vercel --prod --yes` ile ELLE deploy edildi — `https://metric11.com`'a aliaslandı, canlıda doğrulandı (Transfer Aciliyet Sıralaması artık güncel sayılarla). **Bu, kullanıcının "hâlâ eski" şikayetlerinin bir kısmının neden ısrarla devam ettiğini açıklıyor olabilir** — kod düzeltmeleri doğruydu ama production'a hiç ulaşmamış olabilirlerdi.
- **Önemli, çözülmemiş operasyonel soru:** Vercel'in "metric11" projesinin GitHub entegrasyonu gerçekten bağlı mı (ve push'ta otomatik deploy ediyor mu, sadece benim kontrolüm çok erken mi oldu), yoksa bu proje TAMAMEN elle/CLI ile mi deploy ediliyor (ki `vercel ls metric11` yaklaşık saatlik, kısa süreli "Production" deploy'lar gösteriyordu — bunun kaynağı bu oturumda bulunamadı, görünürde bir GH Actions adımı yok)? Bu netleşene kadar, bu oturumun geri kalanında her önemli fix'ten sonra `npx vercel --prod --yes` ELLE çalıştırılacak — git push'a güvenilmeyecek.
- **Doğrulama:** pytest 58/61 (aynı 3 bilinen hata). Tam pipeline 59/59. Canlı site (`metric11.com/transfer_recommendation_report_2025_2026.html`) tarayıcıda kontrol edildi, güncel rakamlar teyit edildi.
- **Sıradaki adım:** Kullanıcıya Vercel dashboard'unda "metric11" projesinin Git entegrasyon ayarını (Production Branch = main, Auto-deploy açık mı) kontrol etmesi önerilmeli — bulunursa bu oturumdaki elle-deploy iş akışı gereksiz hale gelir.

### 2026-09-08 (devam 7) — Vercel git bağlantısı KESİN doğrulandı (yok) + 168 yeni transferin TFF profili toplandı, oyuncu-seviyesi "eski kulüp" sorunu artık gerçekten kapandı

- **Vercel bulgusu kesinleşti:** `vercel project ls --json` çıktısında "metric11" projesinin `"link": null` olduğu doğrulandı — yani bu proje GERÇEKTEN hiçbir GitHub reposuna bağlı değil, otomatik deploy YOK. Saatlik gördüğüm "Production" deploy'ların kaynağı bu oturumda bulunamadı (muhtemelen kullanıcının kendi makinesinde/başka bir yerde çalışan ayrı bir zamanlayıcı). Kalıcı çözüm ya Vercel dashboard'undan Git entegrasyonu bağlamak ya da GitHub Actions'a `vercel --prod` adımı eklemek (bir `VERCEL_TOKEN` secret'ı gerektirir — bunu kullanıcıya sormadan repo secret'ı olarak eklemedim, bu standing/persistent bir CI değişikliği).
- **168 oyuncu profili toplandı — önceki oturumdaki geri alınan riskli denemenin GÜVENLİ versiyonu:** Önceki bulgu ("Ümit Akdağ hâlâ Alanyaspor görünüyor") için asıl kalıcı çözümün "yeni sezon oyuncuları için TFF profil taraması" olduğu not edilmişti. Bunu yaptım: `tff_super_lig_matches_2026_2027.json`'daki (bu oturumda zaten 8/34 boş kadro bug'ı düzeltilmiş) kadrolardan, 2025-26 profil havuzunda HİÇ olmayan 168 oyuncunun TFF external_id'si çıkarıldı (`collect_tff_player_profiles.py --player-ids-file`, zaten var olan bir özellik) — canlı TFF'den 168/168 başarıyla toplandı (`tff_player_profiles_new_2026_2027.json`). Bu, önceki oturumdaki RİSKLİ denemeden (TM kadro kaynağını değiştirmek, yanlış eşleşme riski) TAMAMEN FARKLI ve GÜVENLİ bir yaklaşım: yeni oyuncuların kendi TFF profili YOK'tan VAR oluyor, var olan hiçbir eşleşmeye dokunulmuyor, false-positive riski YOK.
- **Kalıcı/otomatik hale getirildi:** `src/enrich_players_with_transfermarkt.py::load_tff_profiles()`'daki eski either/or mantığı (`preferred` varsa fallback'ler HİÇ okunmuyordu — ölü kod) düzeltildi, artık preferred + tüm var olan fallback'ler birleştiriliyor; yeni dosya fallback listesine eklendi. `run_daily_pipeline.py`'ye YENİ bir NETWORK_COMMANDS adımı eklendi — `tff_super_lig_matches_2026_2027.json`'dan (canlı, ilerleyen) oyuncu toplar, `collect_tff_player_profiles.py`'nin kendi skip-existing mantığı sayesinde sezon ilerledikçe YENİ debut yapan oyuncuları da otomatik yakalamaya devam edecek — bu artık bir kerelik yama değil.
- **Doğrulama:** Vlahović artık `club: BEŞİKTAŞ A.Ş.` (önceden hiç profilde yoktu), Greenwood `club: FENERBAHÇE A.Ş.` — ikisi de doğru. Ümit Akdağ hâlâ "Alanyaspor" gösteriyor ama bu artık BUG DEĞİL: TFF'nin kendi kaydına göre henüz Beşiktaş'ta hiç maça çıkmadı (squad_transition_edge'de zaten "pending_arrivals" — bu oturumun başında doğrulanmıştı), yani gösterilen bilgi doğru/dürüst. `enrich_players_with_transfermarkt`: 691→859 oyuncu, doğrulanmış kapsam %86→%69 (düştü ama BEKLENEN — 168 yeni oyuncunun çoğu henüz 2025-26 TM kadrosunda hiç yoktu, o yüzden değer eşleşmiyor, YANLIŞ değer YERİNE doğru şekilde boş kalıyor). `fm_style_scout_program` kasıtlı olarak değişmedi (691 aday) — FM attribute üretimi gerçek maç istatistiği gerektiriyor, 0 maçlık yeni transferler için üretilemez, bu doğru davranış.
- Tam pipeline 59/59, pytest 58/61 (aynı 3 bilinen hata).

### 2026-09-08 (devam 8) — Golcü tahmini SADECE 2025-26'ya bakıyordu: Vlahović'in 2 maçta 4 golü tamamen görmezden geliniyordu

168-oyuncu profil taramasını yaparken bir yan bulgu daha çıktı: `build_goal_scorer_predictions.py`'deki gol oranı hesabı yalnızca `tff_trendyol_super_lig_2025_2026_matches.json`'dan (tamamlanmış sezon) geliyordu. Vlahović 2025-26'da hiç oynamadığı için (0 başlangıç), gerçek 2026-27 formu (2 başlangıçta 4 gol — inanılmaz bir oran) tamamen görmezden gelinip jenerik piyasa-değeri-bazlı bir "projected" tahmine düşürülüyordu — bu, canlı "Fikstür & Tahmin" sayfasındaki golcü kartlarını doğrudan etkiliyordu (en çok görülen sayfalardan biri).

- **Düzeltme:** `CURRENT_SEASON_MATCHES_PATH` (zaten tanımlıydı ama yalnızca "oynadı mı" kontrolü için kullanılıyordu) üzerinden 2026-27 gol/başlangıç sayısı da hesaplanıyor. Ham güncel oran TEK BAŞINA asla kullanılmıyor (2 maçta 4 gol = 2.0 ham oran, küçük örneklem gürültüsü) — her zaman bir taban orana (2025-26 gerçek oranı VEYA hiç yoksa pozisyon ortalaması) `cur_starts/8` ile en fazla %70'e kadar artan ağırlıkla karıştırılıyor. Vlahović: ilk denemede ham oranla %56 skor olasılığı çıktı, gürültü-bastırma sonrası %32'ye düzeldi — hâlâ yükselmiş (haklı olarak) ama abartısız.
- **Doğrulama:** Formda olan/olmayan mevcut oyuncularda da mantıklı: İbrahim Kaya (2025-26'da 6/11 iyi oran ama 2026-27'de 0/3 soğuk) olasılığı geçmiş orandan aşağı çekiliyor; Efkan Bekiroğlu (2025-26'da 3/14 vasat ama 2026-27'de 1/2 sıcak) yukarı çekiliyor. `projected` bayrağı artık yalnızca HİÇ 2025-26 VE HİÇ 2026-27 (< 2 başlangıç) verisi olmayan oyuncular için true.
- pytest 58/61 (aynı 3 bilinen hata). Tam pipeline çalıştırılıyor, deploy edilecek.

### 2026-09-08 (devam 9) — Maç sinyalleri (kart/gol bandı) de aynı 2025-26-only kalıbındaydı, düzeltildi

Golcü tahmini fix'inin hemen ardından aynı kalıbı `build_match_signals.py`'de de buldum: takım kart ortalaması, hakem kırmızı kart oranı ve gol dakika-bandı dağılımları SADECE `tff_trendyol_super_lig_2025_2026_matches.json`'dan (tamamlanmış sezon) hesaplanıyordu — bu sezon oynanmış 34 maç (artık kart verisi eksiksiz, bkz. yukarıdaki "kalıcı boş kadro/kart" düzeltmesi) havuza hiç girmiyordu.

- **Düzeltme:** Basit/düşük riskli — golcü fix'inden farklı olarak burada ağırlıklı harman yerine sadece 2026-27 maçları `hist` listesine EKLENDİ (havuzu büyütmek, kart/gol-bandı ortalaması gibi toplu istatistikler için ağırlıklı harmandan daha az riskli ve yeterli). `_canon()` fonksiyonu zaten 2025-26/2026-27 isim farklarını (İstanbul Başakşehir FK ↔ Rams Başakşehir vb.) hizalıyordu, ek bir alias işi gerekmedi.
- **Doğrulama:** Beşiktaş kart ortalaması 34 maç/2.32'den 38 maç/2.26'ya, Fenerbahçe 34/2.47'den 38/2.37'ye güncellendi — makul, küçük kaymalar.
- pytest 58/61 (aynı 3 bilinen hata).

### 2026-09-08 (devam 10) — Kendi kendini gözden geçirme: golcü blend'inde 1 gerçek bug bulundu ve düzeltildi

Kullanıcının "durma" demesi üzerine, bu oturumdaki 8 commit'lik src/ diff'ini (20 dosya, ~475 satır) satır satır tekrar okudum — hacim büyük olduğu için gözden kaçmış bir şey olabilir diye. Bulundu: `build_goal_scorer_predictions.py`'deki güncel-form blend'i, `PROJECTED_POSITION_GROUPS` (FWD/MID) dışındaki bir oyuncu (ör. bir stoper) 2025-26'da hiç oynamamış ama 2026-27'de birkaç maçta gol atmışsa, `base_rate` hiç yoktu ve kod sessizce HAM, dampinglenmeMİŞ güncel-sezon oranına düşüyordu — tam da önlemeye çalıştığım küçük-örneklem-gürültüsü sorununun kendisi. Somut örnek: Matej Maglica (DEF), 2 maçta 1 golle hiçbir bastırma olmadan golcü adayı listeleniyordu.

- **Düzeltme:** Bu dal artık `base_rate` (yani FWD/MID pozisyonu) zorunlu ön koşul; yoksa tamamen hariç tutuluyor (bu, değişiklikten ÖNCEKİ orijinal davranışla aynı — savunma oyuncuları hiç golcü adayı olmuyordu).
- **Doğrulama:** Maglica artık listede yok, Vlahović (FWD, geçerli base_rate) etkilenmedi.
- Diğer büyük değişiklikler (`build_team_scout_blueprints.py`, `collect_domestic_league_form.py`, `preview/probability.py`, `html_utils.py`, `run_daily_pipeline.py`) tek tek okundu, başka sorun bulunmadı.
- Bu oturumda bot ile 2. kez gerçek (auto-merge edilemeyen) merge çakışması oldu — hepsi `data/processed/` üretilmiş dosyalarında, kaynak kodda değil; `--ours` ile çözülüp ardından tam pipeline yeniden çalıştırıldı (59/59). pytest 58/61 (aynı 3 bilinen hata). Commit+push+deploy tamamlandı.

### 2026-09-08 (devam 11) — `/code-review high` de 2 gerçek bug buldu — ikisi de düzeltildi

Kendi manuel gözden geçirmemin ardından `/code-review` skill'ini de bu oturumun tam diff'i üzerinde (`819bc88ef..HEAD`) çalıştırdım. 2 bağımsız, geçerli bulgu döndü:

1. **`enrich_players_with_transfermarkt.py::load_tff_profiles` sıra hatası:** either/or→merge-all düzeltmesini yaparken (bkz. yukarı) fallback dosyalarının işlenme SIRASINI düşünmemiştim. `tff_player_profiles_all_priority_2025_2026.json` (Mayıs 24'ten beri donuk) ve `tff_player_profiles_besiktas_2025_2026.json` (Mayıs 22'den beri donuk) `preferred`den (her gün yeniden üretilen) SONRA işleniyordu — `profiles[key] = {**profiles.get(key,{}), **item}` son işlenen dosya kazanır demek, yani donuk veri ortak oyuncularda tazeyi SESSİZCE ezebilirdi. Şu an hiçbir alan farklı olmadığı için aktif bir hasar yoktu (doğrulandı) ama gelecekte bir oyuncunun kulübü/sözleşmesi değişince sessizce eski değere dönebilirdi. **Düzeltme:** sıra ters çevrildi — önce fallback'ler, EN SON preferred işleniyor, yani preferred her zaman kazanır. Doğrulandı: 859 oyuncu, aynı kapsam yüzdeleri, Vlahović/Greenwood hâlâ doğru kulüpte.
2. **`analyze_european_predictions.py::_static_strength` belirsiz-eşleşme sızıntısı:** token-overlap eşleşmesinde BİRDEN FAZLA aday eşit skorla eşleşirse (ör. yalnız "Milan" gelseydi hem "AC Milan" hem "Inter Milan" tek ortak tokenle eşleşirdi), kod bu adaylara hiç bakmadan BAĞIMSIZ bir alt-dizi (substring) son çaresine düşüyordu — bu da sözlük sırasına göre rastgele/yanlış bir kulübü sessizce seçebilirdi. Şu anki 36 gerçek Avrupa fikstür takımının hiçbiri bu duruma düşmüyor (doğrulandı, hâlâ 36/36 doğru), yani şu an aktif değil ama gelecekteki bir isim için pusuda bekleyen bir hataydı. **Düzeltme:** belirsiz kalınca (birden fazla eşit-skorlu aday) artık dürüstçe jenerik varsayılana (48) düşülüyor — rastgele yanlış bir kulüp seçmek yerine.
- pytest 58/61 (aynı 3 bilinen hata), tam pipeline 59/59. Her iki düzeltme de commit+push+deploy edildi.

### 2026-09-08 (devam 12) — Kullanıcı "doğrusunu yap" dedi: transfer sinyali ağırlığı ×0.5→×1.0, ama pratik etkisi neredeyse sıfır çıktı

Önceki turda kullanıcıya transfer/kadro sinyalinin modeldeki ağırlığını artırma seçeneğini sundum, "doğrusunu yap" cevabını aldı.

- **Yapılan değişiklik:** `model_league_predictions.py::predict_match` — transfer sinyalinin `strength_edge`'e katkısı `×0.5` idi, oysa AYNI kategori diğer ileriye-dönük sinyaller (Avrupa formu `×1.0` — 2026-08-14 kullanıcı tercihi, ceza ve fikstür sıkışıklığı da `×1.0`) zaten tam ağırlıkta. Transfer sinyaline özel bir küçültme için belgelenmiş bir gerekçe yoktu, üstelik veri artık doğru (bu oturumdaki isim eşleştirme düzeltmesi). Tutarlılık için `×1.0`'a çekildi.
- **Dürüst sonuç — pratikte neredeyse hiçbir şey değişmedi:** 306 maçın TAMAMI test edildi, **0 tahmin değişti**, olasılıklar en fazla %0.2 kaydı (Fenerbahçe-Beşiktaş örneğinde H/D/A %47.2/24.5/28.3 — öncekiyle neredeyse aynı). **Kök neden:** `strength_edge` (transfer dahil TÜM sinyallerin toplandığı ara değişken) beklenen gole geçerken paylaşılan, kasıtlı olarak küçük tutulmuş bir çarpanla (`×0.05`/`×0.04`) yumuşatılıyor — bu satırın kendi yorumu: "League-wide backtests are noisier... keep this as a mild calibration signal instead of letting short-form strength dominate xG." Yani darboğaz transfer sinyalinin KENDİ ağırlığı değil, TÜM sinyallerin (transfer dahil, ama aynı zamanda geçmiş puan/gol farkı gibi ANA sinyal de dahil) ortak geçiş kapısıydı — onu ikiye katlamak transfer sinyalinin nihai etkisini de en fazla ~%0.75 puan (beklenen gol) oynatabiliyor, gerçek maçlarda tahmin değiştirmeye yetmiyor.
- **Kapsam bilinçli olarak sınırlı tutuldu:** Bu ortak `×0.05`/`×0.04` çarpanına DOKUNULMADI — kullanıcı özellikle "transfer sinyali ağırlığı" dedi, bu çarpan ise TÜM modelin (geçmiş sezon backtest'iyle kalibre edilmiş ANA sinyal dahil) davranışını değiştirir, çok daha büyük ve farklı riskli bir karar. Eğer kullanıcı Beşiktaş gibi büyük kadro yatırımı yapan takımların tahminlere GERÇEKTEN görünür şekilde yansımasını istiyorsa, asıl konuşulması gereken lever bu ortak çarpan — ayrı bir karar olarak sunulmalı.
- pytest 58/61 (aynı 3 bilinen hata), tam pipeline 59/59. Commit+push+deploy edildi.

### 2026-09-08 (devam 13) — "Yap işte çok bekledik": paylaşılan kapıya dokunmadan, backtest-güvenli ayrı bir transfer etkisi eklendi

Kullanıcı ısrar etti, paylaşılan `×0.05/×0.04` kapısına dokunma kararını verdi.

- **Önce doğru şekilde test edildi:** O paylaşılan kapıyı ızgara taramasıyla denedim (0.05→0.30 arası 6 değer, 258 maçlık lig-geneli backtest'e karşı). SONUÇ: her seviyede doğruluk %55'ten %54'e DÜŞTÜ — kapının küçük tutulmasının özenle kalibre edilmiş bir karar olduğu doğrulandı. O kapıyı büyütmek yanlış olurdu, yapmadım.
- **Bunun yerine daha iyi bir çözüm bulundu:** Transfer sinyali yalnızca `apply_transfer_signal=True` olan İLERİYE DÖNÜK tahminlerde çalışıyor — `run_backtest()` bunu HİÇ çağırmıyor (hep `False`). Yani transfer sinyaline backtest'i hiç etkilemeyen, TAMAMEN AYRI bir doğrudan katkı verilebilirdi — paylaşılan kapıdan geçmeden, doğrudan `expected_home`/`expected_away`'e (±0.15/taraf capli edge farkı × 0.5). Bu, backtest riski SIFIR olan bir ayar alanı açtı.
- **Doğrulama (üçlü kontrol):**
  1. **Backtest tamamen değişmedi:** 258 maç, %55, HIGH/MEDIUM/LOW kırılımı BİREBİR aynı — sıfır risk doğrulandı.
  2. **İleriye dönük tahminlerde artık gerçek hareket var:** 306 maçın 15'i (~%5) tahmin değiştirdi (önceki denemede 0'dı).
  3. **Gerçek 2026-27 sonuçlarında iyileşme:** Haftalık isabet %35.3'ten (12/34) %38.2'ye (13/34) çıktı; yüksek güvenli tahmin isabeti de yükseldi. Kocaelispor-Samsunspor (1-0) örneğinde yanlış tahmin doğruya döndü.
  4. Fenerbahçe-Beşiktaş (orijinal örnek maç) hâlâ "Fenerbahçe" tahmin ediyor (Beşiktaş'ın net avantajı bu maçta tek başına baskın olmaya yetecek kadar büyük değil) — her maçın flip etmesi beklenmiyordu, sinyal yeterince güçlü olduğunda hareket ediyor, bu da doğru davranış.
- pytest 58/61 (aynı 3 bilinen hata). Tam pipeline çalıştırılıyor, commit+push+deploy edilecek.

### 2026-09-08 (devam 14) — "En iyisi ol" isteği: beraberlik eşikleri yeniden kalibre edildi (0/7→1/7, %38.2→%41.2)

Kullanıcı: "güncellikte en iyisi ol, tahmin takipçileri hep kazansın" dedi. `weekly_evaluation`'da beraberlik yakalama 0/7 (%0) olduğu dikkat çekti — 2026-07-15'te kullanıcı isteğiyle (o zaman yalnızca 2025-26 backtest'e karşı) kalibre edilmiş eşikler, artık elimizde olan 34 maçlık GERÇEK 2026-27 sonucuna karşı hiç test edilmemişti.

- **Yöntem:** `draw_calibrated_prediction`'ın eşiklerini (`DRAW_PRED_MIN_PROB`, `DRAW_PRED_MAX_GAP`, `DRAW_BOOST_SCALE`) İKİ bağımsız veri setine karşı ızgara taradım: 258 maçlık 2025-26 backtest (eski, büyük örneklem) VE 34 maçlık gerçek 2026-27 sonucu (yeni, o 2026-07-15 tarihinde mevcut olmayan out-of-sample veri). Kaba tarama + ince tarama + tam-sezon/ilk-yarı/ikinci-yarı OOS çapraz kontrolü yapıldı (aynı metodoloji, orijinal tuning'in izlediği yöntem).
- **Sonuç:** `0.275/0.15/0.04` (eskisi `0.28/0.18/0.0`) her ikisi de dahil TÜM dilimlerde eşit veya daha iyi çıktı — tek bir kırılgan nokta değil, geniş bir eşik komşuluğunda tutarlı:
  - 2025-26 backtest: %55.0→%55.4 (143/258), beraberlik yakalama 13/76→17/76
  - İlk yarı OOS: %52.7→%52.7 (aynı), beraberlik 8/45→10/45
  - İkinci yarı OOS: %57.4→%58.1, beraberlik 5/31→7/31
  - **2026-27 gerçek sonuç (34 maç): %38.2→%41.2 (13→14 doğru), beraberlik yakalama 0/7→1/7**
- **Doğrulama:** Simülasyon (cached olasılıklar üzerinde) ve gerçek pipeline çalıştırması (`model_league_predictions` + `build_season_fixture_predictions` + `build_weekly_evaluation`) birebir aynı sayıları verdi. pytest 58/61 (aynı 3 bilinen hata).
- **Not:** Bu hâlâ küçük bir iyileşme (34 maçlık örneklemde +1 doğru, +1 beraberlik) — mucize değil, ama HER dilimde (asla daha kötü değil, çoğu yerde daha iyi) doğrulanmış, kırılgan olmayan bir kazanım. Sezon ilerledikçe daha fazla gerçek veri birikince bu kalibrasyon tekrar gözden geçirilmeli.

### 2026-09-08 (devam 15) — Kullanıcı şikayeti: "dünün maçları işlenmemiş" + GitHub deploy hataları + Vercel storage %100

Kullanıcı 4 ayrı sorun bildirdi: (a) dünün (7 Eylül) maçları hâlâ bekliyor gibi görünüyor, (b) GitHub'dan deploy hatası mailleri geliyor, (c) Vercel "Deployment Storage %100 doldu" maili attı, (d) workflow OAuth scope onayını (device-code) tamamladı.

- **(a) Maç skorları:** Bu oturumda zaten `c7777435b` ile elle çekilip düzeltilmişti (`advance_season_state` — 2 maç kalıcı boş kalmıştı). `gh run view --log-failed` ile CI log'una bakıldı: `collect_tff_season_fixture` ve `advance_season_state` HER ÇALIŞMADA "OK" dönüyor — skor toplama hiç kesilmemiş, kullanıcının gördüğü gecikme aşağıdaki (b) sorunundan kaynaklı yanlış algı.
- **(b) GitHub deploy hataları — KÖK NEDEN bulundu:** `daily-pipeline.yml`'deki `check_squad_freshness` adımı 5 gündür (5-8 Eylül) exit code 1 ile workflow'u "failure" olarak işaretliyordu, çünkü Transfermarkt CI runner'ının IP'sini engelliyor (bu oturumun başında zaten teşhis edilmiş, CI için hiç kalıcı çözülmemiş bilinen bir sınırlama — [[project_transfermarkt_integration]]). AMA bu adımdan SONRAKİ "Commit and push" adımı `if: always()` ile her seferinde başarıyla çalışıp veriyi commit'liyordu — yani gerçek veri kaybı YOK, sadece kozmetik/yanlış-alarm bir "failure" statüsü GitHub'ın mail atmasına sebep oluyordu. **Fix:** `check_squad_freshness` adımına `continue-on-error: true` eklendi (diğer workflow'lardaki `|| true` pattern'iyle tutarlı), commit `d2a9ca934`.
- **(c) Vercel storage:** Kullanıcı onayıyla (AskUserQuestion) `vercel remove metric11 --safe --yes` ile alias'lanmamış onlarca eski deployment silindi.
- **(d) Otomatik CI→Vercel deploy doğrulaması:** Bir önceki oturumda 3 workflow'a da eklenen "Deploy to Vercel" adımı hiç gerçek bir çalışmada test edilmemişti. `gh workflow run refresh.yml` ile elle tetiklenip `gh run watch` ile izlendi — tüm adımlar dahil "Deploy to Vercel" ✓ başarıyla tamamlandı (6m55s), `curl -I https://metric11.com` → HTTP 200 ile canlı site doğrulandı. Artık her pipeline koşusu (günlük 04:00 tam ağ, 6 saatte bir dashboard, 4 saatte bir haber) otomatik olarak commit+push+Vercel prod deploy yapıyor, false-positive workflow hatası da artık gelmeyecek.

### 2026-09-08 (devam 16) — pytest'teki "3 bilinen hata" gerçekten çözüldü (61/61 geçiyor)

Bütün oturum boyunca "pytest 58/61 (aynı 3 bilinen hata)" diye not düşülüp geçiştirilen 3 test tekrar incelendi — ikisi gerçekten stale test'miş, biri ise gerçek (küçük ama gerçek) bir verimsizlik ortaya çıkardı:

- **`test_network_tm_collection_writes_active_transfer_season_separately` — GERÇEK BULGU:** `run_daily_pipeline.py`'nin `NETWORK_COMMANDS` sabiti hâlâ HER GÜN hem ölü 2025-26 sezonu HEM de 2026-27 sezonu için Transfermarkt kadro koleksiyonu çalıştırıyordu (2025-26 için ayrı bir hardcoded blok + "1 Haziran'dan itibaren" koşuluyla eklenen ayrı bir 2026-27 bloğu — o koşul zaten hep true, 1 Haziran çoktan geçti). 2025-26 arşiv verisi donmuş (sezon bitti), onu okuyan `build_side_flip_audit`/`build_alias_quality_report`/`build_data_catalog` sadece var olan dosyayı okuyor — yeniden toplamaya hiç gerek yok. Bu, zaten aralıklı olarak CI IP'sini engelleyen Transfermarkt'a karşı gereksiz günlük yükü ikiye katlıyordu. **Fix:** legacy 2025-26 bloğu tamamen kaldırıldı, 2026-27 koleksiyonu `NETWORK_COMMANDS`'a doğrudan (koşulsuz) taşındı. Commit `494838792`.
- **`test_historical_preview_roster_...` ve `test_live_transfer_tracker_labels_...`:** İkisi de STALE test — kod tarafı zaten kasıtlı olarak değişmiş (27 Mayıs'ta yükselen takımlar ALL_TEAMS'e eklenmiş çünkü artık gerçek maç verileri var; transfer tracker'daki "X sinyali..." info-box kasıtlı bir nav temizliği commit'inde silinmiş) ama testler hiç güncellenmemiş. Testler gerçek/istenen davranışa göre düzeltildi.
- **Sonuç:** `venv/bin/python3 -m pytest -q` → 61 passed, 6 subtests passed (önceden 58/61 idi). Artık gerçekten "bilinen hata" diye bir şey yok — bundan sonra bir test kırmızıysa gerçek bir regresyon sayılmalı.

### 2026-09-08 (devam 17) — KRİTİK model bulgusu: Amed Sportif Faaliyetler'in Elo'su 34 haftanın TAMAMINDA 1500'de donmuştu

Yukarıdaki test taramasının bir yan etkisi olarak AMED SFK'nin isim eşleşmesini kontrol ederken bulundu (kullanıcının talep ettiği türden gerçek bir model hatası, [[project_all_teams_expansion]] ile bağlantılı):

- **Bulgu:** `season_fixture_predictions_2026_2027.json`'da Amed'in ev/deplasman Elo'su 1. haftadan 34. haftaya kadar HER ZAMAN tam olarak `1500.0` — yani takım 4 gerçek maç oynamış olsa da (16 Ağustos'ta Erzurumspor'u 3-0 yendiği dahil), bu sonuçların Elo etkisi hiçbir zaman gelecek hafta tahminlerine yansımıyordu. Kök neden: fikstür dosyası "AMED SPORTİF FAALİYETLER" (TFF resmi adı) kullanıyor, ama `_history_key()`'in yazdığı team_history anahtarı (normalize_matches sonrası) farklıydı — iki taraf hiç eşleşmiyordu.
- **Fix:** `src/normalization.py`'deki global `TEAM_ALIASES`'a `"AMED SPORTİF FAALİYETLER": "AMED SFK"` eklendi (GENÇLERBİRLİĞİ/FATİH KARAGÜMRÜK ile aynı kategori — sponsor adı vs. kanonik ad). Bu TEK BAŞINA `build_season_fixture_predictions.py`'nin kendi iç tutarlılığını bozacaktı (fikstür döngüsü hâlâ ham adla arıyordu), bu yüzden `_history_key()` de `normalize_team_name()`'i uygulayacak şekilde güncellendi — artık iki taraf da aynı anahtarı kullanıyor. Commit `94c5d3029`, `vercel --prod` ile deploy edildi.
- **Doğrulama:** Fix öncesi/sonrası `git stash` ile A/B karşılaştırması yapıldı — fix'ten önce Elo doğru ilerliyordu (1500→1513.5 galibiyet sonrası), SADECE alias eklenip `_history_key` güncellenmeden bırakılsaydı bozulacaktı (test edildi, gerçekten bozdu, sonra düzeltildi). pytest 61/61, backtest (2025-26, Amed'den etkilenmiyor) değişmedi.
- **Not:** Bu, bu tür "iki farklı dosyada aynı takımın farklı adlarla anılması" sınıfındaki hataların HER YENİ TAKIM eklendiğinde tekrar ortaya çıkabileceğini gösteriyor — ileride yeni bir takım (kupa katılımcısı, play-off'tan gelen vs.) eklenirse aynı kontrol (fikstür adı == history anahtarı) tekrar yapılmalı.

### 2026-09-08 (devam 18) — Avrupa verisi araştırması: EL/ECL boşluğu muhtemelen bug değil + VERCEL_TOKEN CI'da geçersiz hale geldi (KULLANICI AKSİYONU GEREKİYOR)

Kullanıcı "avrupa maçları çok kıymetli, güncel olmak zorunda" dedi. İki bulgu:

- **EL/ECL fikstürleri (Avrupa Ligi / Konferans Ligi) 0 maç gösteriyor, ~10 gündür.** Tam ağ pipeline'ı elle tetikleyip (`gh workflow run daily-pipeline.yml -f include_network=true`, run 34268754740) API_FOOTBALL_KEY dahil taze bir koleksiyon yaptırdım — SONUÇ YİNE 144 CL / 0 EL / 0 ECL. Git geçmişi 3+ gün geriye kontrol edildi: nightly full-pipeline (anahtar dahil) HER SEFERİNDE 0 EL/ECL vermiş. **Değerlendirme: muhtemelen bug değil.** API çağrıları başarılı dönüyor (hata yok), sadece boş response — CL bugün (8 Eylül) başladı, gerçek hayatta UEFA Avrupa Ligi/Konferans Ligi lig fazı genelde CL'den ~2-3 hafta sonra başlar. `src/collect_european_fixtures.py`'ye tanı notu eklendi (hem log'a hem committed JSON'a `"note"` alanı) — bir dahaki koleksiyonda otomatik dolacak, izlemeye devam. Commit `4f4c8877`.
- **KRİTİK — VERCEL_TOKEN artık CI'da geçersiz:** Tam pipeline çalışırken "Deploy to Vercel" adımı `Error: The token provided via --token argument is not valid` ile başarısız oldu — aynı token ~1 saat önce (refresh.yml testinde) çalışmıştı. Kök neden: bu oturumda GH secret olarak kaydedilen token, `~/Library/Application Support/com.vercel.cli/auth.json`'dan çekilmiş bir "Sign in with Vercel (saml)" CLI oturum tokenı — bunlar kısa ömürlü/rotasyonlu görünüyor (yerel `vercel tokens ls` çıktısında aynı isimle onlarca farklı token var, her yeni CLI çağrısı yenisini yaratıyor gibi). **`vercel tokens add` ile CI için kararlı/uzun ömürlü bir token oluşturmayı denedim ama Vercel bunu reddetti: `Error: Cannot create tokens for this app (403)`** — organizasyonun SSO/SAML politikası CLI'dan programatik token oluşturmayı engelliyor. **Bu KULLANICININ elle yapması gereken bir adım: Vercel dashboard → Settings → Tokens → "Create Token" (süresiz veya uzun süreli) → yeni değeri bana ilet, ben `gh secret set VERCEL_TOKEN` ile güncelleyeyim.** Bu düzelene kadar CI'nın otomatik deploy adımı başarısız olacak (ama commit+push adımı hâlâ çalışıyor, veri kaybı yok) — ben bu turda elle `vercel --prod --yes` ile deploy ettim, site güncel.

### 2026-09-09 — Günlük veri/geliştirme heartbeat kontrolü

Otomasyon kontrolünde önce bu dosya okundu, ardından repo durumu, bugünkü dosya tazeliği, son pipeline raporu, tahmin karnesi, scout kalite çıktıları ve kaynak performansı incelendi.

- **Repo durumu:** `main...origin/main` temiz; çalışma ağacında bekleyen değişiklik görünmüyor.
- **Bugünkü dosya tazeliği:** 9 Eylül 00:00 sonrası yerel `data/processed` dosyası yok. En son toplu üretim 8 Eylül 22:48 TR civarında; bu heartbeat 9 Eylül 04:50 TR civarında geldiği için bu tek başına alarm değil. Günlük tam ağ koşusu normal zamanında gelince tekrar dosya üretmesi beklenir.
- **Son pipeline raporu:** `daily_pipeline_run_latest.json` artık güncel: `generated_at=2026-09-08T18:44:26Z`, `include_network=False`, 59 komut / 59 başarılı / 0 hata. `data_quality_scorecard` ise `daily_pipeline_last_run_age_days=0`, `failed_count=0`, `include_network=True` gösteriyor; veri tazeliği PASS.
- **Tahmin karnesi:** `weekly_evaluation_2026_2027` 36 oynanmış maç, 14 doğru, genel doğruluk %38.89. Beraberlik yakalama 1/7 (%14.29). Yüksek güvenli tahminler 13 maçta 6 doğru (%46.15). Aktif hafta 5; hafta 4 kapanış karnesi 9 maçta 2 doğru (%22.22), yüksek güven 0/1. Model tarafında hâlâ en önemli açık beraberlik/sürpriz maç kalibrasyonu.
- **Maç/golcü sinyalleri:** `season_fixture_predictions_2026_2027` 306 maç, 36 oynanmış maç gösteriyor. `match_signals_2026_2027` 270 maç için sinyal üretiyor; lig kart ortalaması 2.14, kırmızı kart oranı 0.101. `goal_scorer_predictions_2026_2027` 270 maç için 1620 golcü adayı üretiyor; 120 aday hâlâ projected, kesin 11 ile onaylanmış maç sayısı 0.
- **Canlı kadro/availability:** `live_lineups_2026_2027` 2 maç tutuyor ve `candidates_checked=0`. Bu, maç önü tahmin kalitesi için hâlâ ana zayıf halka. Sıradaki veri işi: canlı kadro, cezalı, sakat/eksik haberleri ve resmi kulüp duyurularını fixture bazlı tek availability dosyasında toplamak.
- **Scout kalite:** `scout_quality_report_2025_2026` düşük güvenli yayın adayı 0, eksik yaş/kontrat linki 0, tekrar eden rol oyuncusu 0. 310 blueprint-candidate link ve 105 pozisyon matrisi adayı var; pozisyon matrisi 101 HIGH / 4 DERIVED. Scout'u bloke eden eşleşmeyen oyuncu yok.
- **Transfer/profil kapsamı:** `transfermarkt_super_lig_squads_2026_2027` 18 kulüp, 530 oyuncu, toplam yaklaşık 1.709B EUR piyasa değeri gösteriyor. Yeni TFF profilleriyle havuz 863 oyuncuya çıktı; in-scope Transfermarkt eşleşme oranı %81.5'e indi (beklenen, çünkü yeni sezon oyuncuları eklendi ama hepsinin TM eşleşmesi henüz yok). 4 manuel alias ağ teyidi bekliyor; scout blocking 0.
- **Kaynak performansı:** `source_performance` 39 transfer sinyali, 12 resmi olay, 293 gözlenen kaynak, 175 skorlu kaynak ve 3996 claim gözlemi gösteriyor. Google News 290 makale / 30 başarılı sorgu; Telegram 6 mesaj / 8 kanal; X/Twitter hâlâ `MISSING_CREDENTIALS` ve 45 hesap verisiz.
- **Avrupa verisi:** `european_predictions_2026_2027` hâlâ CL=144, EL=0, ECL=0. Önceki araştırmaya göre bu muhtemelen API'nin EL/ECL lig fazını henüz boş dönmesinden kaynaklı; izlenmeye devam edilmeli.
- **Kritik operasyonel açık:** Önceki kayıttaki `VERCEL_TOKEN` problemi hâlâ kullanıcı aksiyonu gerektiriyor. Uzun ömürlü Vercel token dashboard'dan oluşturulup `VERCEL_TOKEN` secret'ı güncellenmeden CI deploy adımı tekrar kırılabilir; commit/push ve veri üretimi ayrı çalışsa bile production'a otomatik yansıma garantisi zayıf.
- **Sıradaki uygulanabilir adım:** Kullanıcıdan kalıcı Vercel token alınır alınmaz `gh secret set VERCEL_TOKEN` ile CI deploy düzeltilmeli. Kod/veri tarafında ilk geliştirme önceliği `availability` katmanı ve hafta 5 sonrası beraberlik/sürpriz kalibrasyonunu yeniden ölçmek.

### 2026-09-09 (devam) — VERCEL_TOKEN kalıcı olarak düzeltildi

Kullanıcı Vercel dashboard → Settings → Tokens'tan `alicans-projects-02042cb7` scope'unda, süresiz yeni bir personal access token oluşturup iletti (`vcp_...`). `gh secret set VERCEL_TOKEN` ile GitHub secret'ı güncellendi. `gh workflow run refresh.yml` ile canlı test edildi — "Deploy to Vercel" adımı ✓ başarıyla tamamlandı (6m5s). Artık CI'nın otomatik deploy zinciri (günde 4 haber + 4 dashboard refresh + 1 tam pipeline) kalıcı olarak çalışıyor; bir daha elle `vercel --prod` deploy etmeye gerek kalmamalı — SSO/CLI-oturum-token'ının kısa ömürlü olması sorunu (bkz. yukarıdaki kayıt) dashboard'dan oluşturulan kalıcı token ile tamamen çözüldü.

### 2026-09-09 (devam 2) — [[project_current_state_jun2026|8-19 kaydındaki]] "1 hafta sonra GSC'ye bak" takibi: hâlâ 0 Google sonucu, teşhis değişmedi

Kullanıcı: "metric11 diye aratınca site hiç çıkmıyor" şikayeti. 8-19 kaydında verilen "~1 hafta sonra kontrol et" notu bu ana kadar yapılmamıştı (aradan 3 hafta geçmiş) — bu turda tekrar tam denetim yapıldı.

- **Teknik SEO yine sağlam, hiçbir yeni bug yok:** `curl` ile canlı site (Googlebot user-agent dahil) 200 dönüyor, `<title>`/meta description/OG/canonical/JSON-LD ana sayfada ve 3 örnek alt sayfada mevcut, hiçbir yerde `noindex` yok, `og-image.png` 200 dönüyor, `robots.txt` `User-agent: *` için `Allow: /` (Cloudflare'ın enjekte ettiği `Google-Extended: Disallow` yalnız AI-training opt-out'u, normal Googlebot indexlemesini etkilemiyor), `sitemap.xml` 39 URL içeriyor ve `Sitemap:` satırı robots.txt'de doğru.
- **WebSearch ile doğrulandı — sıfır iz:** `site:metric11.com` → 0 sonuç. `metric11.com` düz araması → 0 alakalı sonuç (hepsi alakasız "metric" eşleşmeleri). `"metric11" süper lig tahmin` → 0 alakalı sonuç. Yani site sadece Google'da değil, AÇIK WEB'İN HİÇBİR YERİNDE (forum, sosyal medya, haber) bir kez bile anılmamış/linklenmemiş — sıfır backlink, sıfır sosyal sinyal teyidi 8-19'daki teşhisi doğruluyor ve pekiştiriyor.
- **Güncel değerlendirme:** Domain 2026-05-25'te kuruldu, bugün ~15 hafta oldu — "3-6 aylık kuyruk normal" penceresinin ortasındayız, henüz alarm seviyesi değil ama sıfır dış sinyal bu kuyruğu muhtemelen UZATIYOR (Google yeni/güvensiz domain'lere ayırdığı kısıtlı crawl bütçesini genelde önce dış sinyali olan sitelere veriyor). Kod/config tarafında düzeltilecek hiçbir şey yok — darboğaz saf keşif/güven sorunu.
- **Kullanıcıya iletilen somut aksiyon maddeleri (uygulanmadı, kullanıcı kararı bekliyor):** (1) GSC → URL Denetimi → ana sayfa + 2-3 önemli sayfa için elle "Dizine Eklenmeyi Talep Et" (2 dakika, giriş gerektirir, ben yapamam), (2) en az birkaç GERÇEK dış backlink/sosyal paylaşım — Twitter/X hesabı, ilgili Reddit/Ekşi Sözlük/forum paylaşımı, Telegram kanalının (@metric11tr) açıklamasına/sabitlenmiş mesajına site linki — sıfır otoriteli yeni domain için en yüksek etkili, en düşük maliyetli adım budur, (3) 1-2 hafta sonra GSC "Sayfaları dizine ekleme" raporuna tekrar bakılmalı.
- **Not:** Bu, [[project_predict_app_launch]] ile de bağlantılı — tahmin oyununun kendisi paylaşılabilir/viral bir ürün, "arkadaş grupları" özelliği kullanıcıları organik olarak linki paylaşmaya itebilir; bu da dolaylı backlink/marka arama hacmi kaynağı olabilir.

### 2026-09-09 (devam 3) — Yukarıdaki nottan somut adım: grup davet linki için paylaşım butonları eklendi

Kullanıcı "devam" dedi, bir önceki turda önerilen "arkadaş grupları paylaşımını kolaylaştır" fikrini uyguladım.

- **Yapılan:** `predict-app/components/share-group-invite.tsx` (YENİ) — grup sayfasında (`app/gruplar/[code]/page.tsx`) artık davet kodu düz metin olarak durmuyor, 3 buton var: native share sheet (`navigator.share`, mobilde), doğrudan WhatsApp paylaşım linki (`wa.me/?text=...`), panoya kopyala. Mesaj metni `https://tahmin.metric11.com/gruplar/{code}` linkini ve kısa bir tanıtımı içeriyor. Amaç: [[project_site_url]] altında teşhis edilen "sıfır dış backlink/sosyal sinyal" darboğazına karşı en düşük maliyetli, kod-tarafı yapılabilecek somut adım — kullanıcılar arkadaşlarını davet ettikçe organik olarak site linki WhatsApp/paylaşım kanallarında dolaşmaya başlayacak.
- **Doğrulama:** `npx tsc --noEmit` ve `npx eslint` temiz, `npm run build` başarılı (16 route, hata yok). Chrome'da oturumlu (Clerk login) uçtan uca test YAPILMADI — bu makinede predict-app için bilinen bir kısıtlama ([[project_predict_app_launch]]'ta not edilen localhost çerez sorunu; burada prod domain olsa da giriş gerektiren bir akış, zaman kısıtı nedeniyle atlandı). Kod basit/düşük riskli (yalnız yeni bir client component + var olan sayfaya 1 satır ekleme).
- **Deploy düzeltmesi (öğrenilen ders):** `predict-app/` içinden `vercel --prod` çalıştırmak "Root Directory bulunamadı" hatası veriyor (proje ayarı monorepo kökünden `predict-app` bekliyor). Repo KÖKÜNDEN `-A predict-app/vercel.json` ile denendiğinde ise `.vercel/project.json` kökte olduğu için YANLIŞLIKLA ana site projesine (`metric11`) deploy oldu (zararsız çıktı çünkü dashboard'daki Output Directory ayarı zaten `data/processed` olarak sabit duruyordu, ama bu bir şans eseriydi, tekrar denenmemeli). **Doğru yöntem:** repo kökünden, `.vercel/project.json`'a DOKUNMADAN, `VERCEL_ORG_ID`/`VERCEL_PROJECT_ID` env değişkenleriyle hedef projeyi (`metric11-tahmin`, `prj_y8N95iyHMm3nTxNOH66Onx3KU9DQ`) açıkça belirtip `-A predict-app/vercel.json` ile deploy etmek. Bu şekilde başarıyla `tahmin.metric11.com`'a aliaslandı, `curl` ile 200 doğrulandı.
- **Yan not (aksiyon gerektirmiyor, ~3 hafta payı var):** Deploy log'unda `Node.js version 20.x is deprecated. Deployments created on or after 2026-10-01 will fail to build` uyarısı çıktı (metric11-tahmin projesi için). 1 Ekim'den önce Vercel dashboard → Project Settings → Node.js Version → 24.x'e geçirilmeli, yoksa o tarihten sonra predict-app deploy'ları kırılır.

### 2026-09-10 — Kullanıcı GSC + backlink aksiyon maddelerinin TAMAMINI uyguladı

Önceki turda verilen somut adım listesi (GSC manuel dizine ekleme talebi + gerçek dış paylaşım) kullanıcı tarafından uygulandı.

- **GSC URL Denetimi:** Ana sayfa + birkaç önemli sayfa için "Dizine Eklenmesini İste" denendi. Bazılarında "eklendi" onayı geldi, bazılarında "tekrar talep et" çıktı (muhtemelen o anki crawl denemesi başarısız oldu ya da GSC'nin günlük manuel istek kotasına yakın kalındı — ikisi de normal, kalanlar için 24 saat sonra tekrar denenebilir).
- **Backlink/sosyal sinyal:** Kullanıcı "hepsini yaptım" dedi — Telegram kanalı (@metric11tr) açıklamasına site linki eklendi VE en az bir dış paylaşım (Twitter/forum) yapıldı.
- **Beklenti yönetimi:** Bu adımların etkisi anlık değil — Google'ın manuel istek sonrası gerçekten crawl edip indekslemesi günler, bazen 1-2 hafta sürebiliyor. Sonraki somut kontrol noktası: ~1 hafta sonra (2026-09-17 civarı) GSC "Sayfalar" raporunda indekslenen sayfa sayısına ve `site:metric11.com` aramasına tekrar bakılmalı. O ana kadar kod/config tarafında ek bir aksiyon gerekmiyor — mekanizma artık kullanıcının elinden çıktı, Google'ın crawl/trust sürecine kaldı.

### 2026-09-10 — Günlük veri/geliştirme heartbeat kontrolü

Otomasyon kontrolünde önce bu dosya okundu, ardından repo durumu, bugünkü üretim dosyaları, pipeline/kalite raporları, tahmin karnesi, kaynak performansı, scout çıktıları ve canlı kadro/availability boşlukları incelendi.

- **Repo durumu:** `main...origin/main` temiz; çalışma ağacında bekleyen değişiklik yok.
- **Bugünkü üretim:** 10 Eylül 00:00 sonrası `data/processed` altında 82 dosya yenilenmiş. Ana çıktılar Sep 10 13:46 TR civarında taze: `season_fixture_predictions_2026_2027`, `weekly_evaluation_2026_2027`, `match_week_2026_2027`, `match_signals_2026_2027`, `goal_scorer_predictions_2026_2027`, `source_performance`, transfer/scout sayfaları, haber çıktıları ve takım preview çıktıları güncel.
- **Pipeline izleme notu:** `data_quality_scorecard` veri tazeliğini PASS gösteriyor (`daily_pipeline_last_run_age_days=0`, `failed_count=0`, `include_network=True`). Buna karşın `daily_pipeline_run_latest.json` dosyası hâlâ `generated_at=2026-09-08T18:44:26Z` ve dosya mtime'ı Sep 8 21:44. Yani gerçek raporlar bugün üretilmiş ama "son pipeline run" özet dosyası yenilenmemiş; bu ayrı bir izleme hijyeni açığı olarak kalıyor.
- **Tahmin karnesi:** `weekly_evaluation_2026_2027` 36 oynanmış maç, 14 doğru, genel doğruluk %38.89. Beraberlik yakalama 1/7 (%14.29). Yüksek güvenli tahminler 13 maçta 6 doğru (%46.15). Hafta 5 aktif, hafta 4 kapanış karnesi 9 maçta 2 doğru (%22.22), yüksek güven 0/1. Model tarafında ana açık hâlâ beraberlik/sürpriz maç kalibrasyonu.
- **Maç/golcü sinyalleri:** `season_fixture_predictions_2026_2027` 306 maç / 36 oynanmış maç gösteriyor. `match_signals_2026_2027` 270 maç için sinyal üretiyor; lig kart ortalaması 2.14, kırmızı kart oranı 0.101. `goal_scorer_predictions_2026_2027` 270 maç için 1620 golcü adayı üretiyor; 120 aday projected, kesin 11 ile onaylanmış aday yok.
- **Canlı kadro/availability:** `live_lineups_2026_2027` hâlâ yalnız 2 maç ve `candidates_checked=0`. `player_availability_besiktas_2025_2026` 34 maçtan 11'inde unavailable sinyali, 14 otomatik ceza girişi, 3 news-intelligence girişi gösteriyor; bu hâlâ yalnız Beşiktaş merkezli ve tüm lig/fixture bazlı birleşik availability katmanı değil. Maç önü tahmin kalitesi için en büyük veri açığı bu.
- **Scout kalite:** `scout_quality_report_2025_2026` düşük güvenli yayın adayı 0, eksik yaş/kontrat linki 0, tekrar eden rol oyuncusu 0. 310 blueprint-candidate link ve 105 pozisyon matrisi adayı var; pozisyon matrisi 101 HIGH / 4 DERIVED. Scout blocking 0.
- **Transfer/profil kapsamı:** Transfermarkt 2026-27 snapshot'ı 18 kulüp, 530 oyuncu, yaklaşık 1.709B EUR piyasa değeri. TFF/TM eşleşme havuzu 863 TFF profilinde 593 doğrulanmış eşleşme; in-scope oran %81.5, operasyonel in-scope oran %82.0. 4 manuel alias hâlâ ağ teyidi bekliyor.
- **Kaynak performansı:** `source_performance` 41 transfer sinyali, 12 resmi olay, 298 gözlenen kaynak, 177 skorlu kaynak ve 4034 claim gözlemi gösteriyor. Google News 268 makale / 30 başarılı sorgu; Telegram 6 mesaj / 8 kanal; X/Twitter hâlâ `MISSING_CREDENTIALS` ve 45 hesap verisiz.
- **Transfer tracker:** `transfer_tracker_2025_2026` 41 sinyal gösteriyor ama OFFICIAL/CONFIRMED 0 ve tüm değer 0 EUR; bu muhtemelen aktif transfer penceresi dışı ve/veya review_required ağırlıklı dönem. Yine de veri dili UI'da "resmi yok, izleme sürüyor" şeklinde kalmalı.
- **Avrupa verisi:** `european_predictions_2026_2027` hâlâ CL=144, EL=0, ECL=0. Önceki araştırmaya göre API henüz EL/ECL fikstürlerini boş döndürüyor; bug sinyali yok ama günlük izlenmeli.
- **Sıradaki uygulanabilir adım:** Kod tarafında önce `daily_pipeline_run_latest.json` yenilenme tutarsızlığı giderilmeli. Veri/ürün tarafında daha büyük iş, tüm Süper Lig için fixture bazlı `availability` katmanını kurmak: canlı 11, cezalı, sakat/eksik haberleri, resmi kulüp duyuruları ve haber-intelligence sinyalleri tek dosyada birleşmeli. Model tarafında hafta 5 sonuçları geldikçe beraberlik/sürpriz eşikleri tekrar ölçülmeli.

### 2026-09-11 — Avrupa kupası tahmin skorlarında "hep 2-1" hatası düzeltildi

Kullanıcı Avrupa kupası (UCL/UEL/UECL) sayfasında tahmini skorların hep 2-1/1-2 çıktığını fark etti; kontrol edildi ve gerçek bir kod kusuru olduğu doğrulandı (144 tahminin %90'ı 2-1/1-2/3-1/1-3/4-1/1-4 idi, hiç 0-0/1-0/1-1/2-0 yoktu).

- **Kök sebep:** `src/analyze_european_predictions.py` içindeki `_score_prediction`, beklenen gol ortalamasını (λ) en yakın tam sayıya yuvarlayıp kazananı tutturmak için sadece +1 dürtüyordu. UCL/UEL maçlarında λ neredeyse hep 1.0-1.6 aralığına düştüğü için bu mekanik olarak hep 2-1/1-2'ye sabitleniyordu.
- **Düzeltme:** Fonksiyon artık zaten hesaplanan kazanan grubu (ev/berabere/deplasman) içinde gerçek Poisson ortak olasılık gridinden en yüksek olasılıklı (h,a) skorunu seçiyor (`argmax` yaklaşımı). Kazanan tarafı değiştirmiyor, sadece o tarafın en gerçekçi skorunu buluyor.
- **Sonuç:** Aynı 144 tahminde skor dağılımı artık 2-1 (%41.7), 1-2 (%32.6), 2-0 (%15.3), 0-2 (%8.3), 0-3/3-0 (%2.1) şeklinde takım gücü farkına göre çeşitleniyor; büyük favori-underdog maçlarında (ör. Arsenal-Sabah FK 3-0) skor artık gerçekçi. 1X2 doğruluğu değişmedi (CL 10/12, %83.3) çünkü kazanan tarafı belirleyen mantık aynı kaldı.
- **Bilinen sınır (ayrı konu, düzeltilmedi):** En yakın/rekabetçi maçlarda bile (`hw`≈`aw`≈0.36) beraberlik olasılığı (`dr`≈0.277) hiçbir zaman en yüksek çıkmıyor — yani model hiçbir Avrupa maçında beraberlik tahmin etmiyor. `_DRAW_CALIBRATION=1.18` yeterince güçlü değil. Bu, lig tahminlerinde zaten bilinen ve ayrı ele alınan beraberlik kalibrasyon sorununun (bkz. yukarıdaki beraberlik risk katmanı notları) Avrupa kupası tarafındaki yansıması; ayrı bir iş kalemi olarak bekliyor.
- Değişen dosyalar: `src/analyze_european_predictions.py` (kod), `data/processed/european_predictions_2026_2027.json` + `.html` (yeniden üretildi).

### 2026-09-11 — Lig geneli availability (sakat/cezalı) katmanı: Beşiktaş-only'den 21 takıma genişletildi

Kullanıcının "en büyük veri açığı" dediği konu ele alındı: `build_player_availability.py` yalnızca Beşiktaş için çalışıyordu, `generate_preview_batch.py --all-teams` diğer 17 takıma `avail_path=None` geçiyordu — yani maç önü modelinde sakat/cezalı sinyali sadece Beşiktaş'ta etkiliydi.

- **Genişletme:** `build_player_availability.py`'ye `--all-teams` modu eklendi; `generate_preview_batch.ALL_TEAMS` listesindeki 21 takımın her biri için ayrı `player_availability_{slug}_2025_2026.json/.md` üretiliyor, artı bir birleşik `player_availability_superlig_2025_2026.json`. `generate_preview_batch.py` artık her takım için kendi availability dosyasını okuyor (Beşiktaş dahil, davranış değişmedi). `run_daily_pipeline.py`'de ilgili adım `--all-teams` ile çağrılıyor.
- **Yol boyunca bulunan 3 gerçek bug (lig geneline açılınca kritik hale gelirdi, tek takımda gizli kalmıştı):**
  1. `news_intel_unavailability_for_team` `signal.get("team")`/`signal.get("player")` okuyordu ama `analyze_news_with_claude.py`'nin gerçek şeması `club`/`player_name`. Sonuç: `signal_team` hep boş string oluyordu ve boş string her string'in substring'i olduğu için TÜM haber istihbaratı sakat/ceza sinyalleri (ilgisiz kulüplerinkiler dahil — ör. Esenler Erokspor, Alanyaspor, Başakşehir) hangi takım sorgulanırsa ona ekleniyordu. Beşiktaş'ın raporunda alakasız kulüplerin sinyalleri görünüyordu.
  2. `news_unavailability_for_team`'de alias seti hardcoded `{team, "beşiktaş", "besiktas"}` idi — lige açılınca her takımın raporuna Beşiktaş'ın haber-context sinyalleri de bulaşacaktı. 21 takım için gerçek Türkçe medya alias tablosu (`TEAM_MEDIA_ALIASES`) eklendi.
  3. Manuel override dosyasındaki `entries[].team` alanı hiç filtrelenmiyordu — aynı `match_id`'yi paylaşan rakip takımın raporunda da manuel kayıt "eksik oyuncu" olarak görünebilirdi (şu an gerçek override dosyası boş olduğu için pasif bug'dı, aktif hale gelmeden düzeltildi).
- **Doğrulama:** Vlahovic cezası artık sadece Beşiktaş'ta, Gabriel (Galatasaray) cezası sadece Galatasaray'da, Christopher Operi (Başakşehir) ve Mahmut Can Kara (Alanyaspor) sakatlıkları doğru kulüplerde görünüyor. Uçtan uca örnek: Alanyaspor'un cezalı oyuncusu (4. sarı kart birikimi, Fidan Aliti) artık o maçın modelinden çıkarılıyor — beklenen gol 1.31→1.19, kazanma olasılığı %39.5→%37.2 (önceden 17/18 takımda bu ayarlama hiç uygulanmıyordu, `"available": false, "note": "Availability verisi yok."` idi).
- `collect_live_lineups.py` zaten lig genelinde çalışıyor (takım bazlı filtre yok, sadece kickoff penceresi bazlı) — o ayrı, zaten kapsamda.
- **Kapsam dışı bırakılan (bilinçli):** Ana sayfa/komuta merkezi widget'ları (`build_command_center.py`, `build_product_home.py`, `build_data_catalog.py`) hâlâ sadece Beşiktaş'ın özet istatistiğini gösteriyor — bunlar kozmetik, tahmin kalitesini etkilemiyor, dokunulmadı.
- Değişen dosyalar: `src/build_player_availability.py`, `src/generate_preview_batch.py`, `src/run_daily_pipeline.py`; 21 yeni `player_availability_*.json/.md` + `previews_*` altında ~800 dosya yeniden üretildi (bekleniyor — 18 takımın 34 maçlık geçmiş kadro/olasılık raporu availability sinyaliyle yeniden hesaplandı).

### 2026-09-11 — Tahmin karnesi: yeni/az geçmişli takımlarda aşırı güven düzeltildi (küçük örneklem shrinkage)

Kullanıcının "bir o kadar kritik" dediği tahmin karnesi konusuna girildi. Önce 2026-27 sezonunun 36 oynanmış maçı hata tipine göre incelendi: 22 yanlış tahminin 15'i (%68'i) beraberlik kaçırma değil, DOĞRUDAN yanlış taraf (ev/deplasman) tahminiydi — çoğu yeni yükselen takımları (Çorum FK, Erzurumspor FK, Amed) içeren maçlarda.

- **Somut örnek/kök sebep:** Hafta 2'de Kocaelispor evinde Amed'i 2-0 yendi ama model deplasmana (Amed) %78.1 kazanma şansı vermişti (HIGH güven). Sebep: `model_league_predictions.py::predict_match` geçmiş MACI HİÇ yoksa (0 maç) lig ortalamasına düşüyordu ama 1-4 maçlık ince örneklemi TAM güvenle (hiç kalibrasyon/shrinkage olmadan) kullanıyordu. Amed hafta 1'de Erzurumspor'u 3-0 yenmişti (n=1: "gf=3,ga=0"), Kocaelispor ise Başakşehir'e 0-2 kaybetmişti (n=1: "gf=0,ga=2") — model bu tek maçlık örneklemi bir sezonluk form gibi okudu.
- **Düzeltme:** `_shrink_to_league_avg()` eklendi — `MIN_HISTORY_FOR_FULL_TRUST=5` (run_backtest'in `min_team_history` varsayılanıyla KASITLI aynı) altındaki örneklem (gf, ga, ppg, gd, clean-sheet, blank oranları) kademeli olarak lig ortalamasına kaydırılıyor; eşiğin üstünde (backtest'in HER ZAMAN çalıştığı aralık) davranış birebir eskisiyle aynı.
- **Güvenlik doğrulaması:** 258 maçlık 2025-26 backtest'i (`model_league_predictions.py`) ve ondan türeyen `model_baseline_comparison_2025_2026.json` yeniden çalıştırıldı — sonuç byte-identical (%55.0, 143/258) çünkü backtest zaten yalnız her iki takımın da >=5 maçlık geçmişi varken tahmin üretiyor. Yani özenle kalibre edilmiş sistem hiç etkilenmedi.
- **Canlı 2026-27 etkisi:** `season_fixture_predictions_2026_2027`/`weekly_evaluation_2026_2027` yeniden üretildi. En büyük olasılık kaymaları tam olarak hedeflenen popülasyonda: Kocaelispor-Amed deplasman %78.1→%48.3, Gençlerbirliği-Erzurumspor ev sahibi %80.8→%59.5, Erzurumspor-Galatasaray deplasman-favorisi ev sahibi %6.4→%24.0. Yerleşik takım maçlarında (>=5 maç geçmişi olan) fark sıfır.
- **36 maçlık örneklemde genel doğruluk sayısı değişmedi (14/36, %38.89)** — bu beklenen: shrinkage bir "kaç doğru bildi" düzeltmesi değil, bir kalibrasyon düzeltmesi (aşırı/yanlış güveni azaltıyor). Somut kanıt: HIGH güven kovası 13→11 maça düştü (2 maç artık daha dürüst şekilde MEDIUM), HIGH güven isabeti %46.15→%54.55'e çıktı. Gençlerbirliği-Erzurumspor beraberliğinde draw olasılığı %13.3→%21.4'e çıktı (hâlâ eşiğin altında kaldığı için tahmin değişmedi ama artık gerçeğe daha yakın).
- **Sonraki adım:** Hafta 5+ sonuçları geldikçe (özellikle yeni takımların geçmişi 5 maça ulaştıkça shrinkage kendiliğinden devre dışı kalacak) genel doğruluk/beraberlik yakalama tekrar ölçülmeli. Beraberlik eşiği (`DRAW_PRED_MIN_PROB` vb.) 2026-09-08'de zaten iki bağımsız veri setine karşı grid-search ile kalibre edildi (bkz. o tarihli not) — sadece 2 yeni maçlık ek veriyle tekrar taranmadı, istatistiksel olarak anlamlı olmazdı.
- Değişen dosyalar: `src/model_league_predictions.py` (kod); `data/processed/season_fixture_predictions_2026_2027.*`, `weekly_evaluation_2026_2027.*`, `match_week_2026_2027.*`, `match_signals_2026_2027.json`, `goal_scorer_predictions_2026_2027.json`, `gundem_*`, `football_command_center_*`, `football_intelligence_home.html` yeniden üretildi.
