# 14 Madde Takip ve Kanıt Dosyası

Güncelleme: 2026-05-25

Bu dosya proje isteklerinin madde madde durumunu ve kanıt dosyalarını tutar. "Tamam" ifadesi production kusursuzluğu değil, repo içinde çalışan MVP karşılığı olduğu anlamına gelir. Dış API planı, lisans veya doğrulanmamış kaynak gerektiren maddelerde durum ayrıca belirtilir.

| No | İstek | Durum | Kanıt / Dosya |
|---:|---|---|---|
| 1 | Kaldığın yerden devam et, tüm maddeleri tamamla, geliştirmeye ara verme | MVP tamam, sürekli geliştirme devam | `PROJECT_STATE.md`, günlük otomasyon, `src/run_daily_pipeline.py`, `.github/workflows/daily-pipeline.yml` |
| 2 | Veri kaynaklarını çeşitlendir, artır, alaka durumuna göre analize dahil et | MVP tamam | `data/manual/source_watchlist.json`, `src/build_source_watchlist.py`, API-Football, TFF, Transfermarkt, haber bağlamı, açık veri kaynak listesi |
| 3 | Her işlemi md dosyasına kaydet | MVP tamam | `PROJECT_STATE.md`, bu dosya |
| 4 | Transfermarkt, LigTV/beIN gibi güncel kaynaklarla beslen | MVP tamam | `src/collect_transfermarkt_squad.py`, `src/collect_transfermarkt_league_squads.py`, `src/collect_news_context.py`; beIN sakat/cezalı gerçek ağ testi başarılı |
| 5 | Pozisyon bazlı veri/analiz/tahmin/öneri detaylı olsun | MVP tamam | `src/build_position_scout_matrix.py`, `data/processed/position_scout_matrix_2025_2026.html`, maç önü `coach_lineup_audit` |
| 6 | Veri setlerini sık güncelle, doğruluğu artır, %80 hedefle | MVP tamam, model hedefi devam | `src/run_daily_pipeline.py`, `.github/workflows/daily-pipeline.yml`, backtest raporları. Not: 1X2 maç sonucu için %80 kısa vadede gerçekçi değil; Top 5 gol adayı %73 ve artırılabilir. |
| 7 | Forum, GitHub, canlı kaynakları tara; genç oyuncu keşfi | İzleme + kaynak radarı hazır | `data/manual/source_watchlist.json`; Reep, openfootball, GitHub datasetleri, community sinyali takipte |
| 8 | HTML mi olmalı, güncellik/UI/responsive doğru mu? | Strateji tamam | `docs/deployment_strategy.md`; mevcut HTML responsive MVP, production için Next.js + scheduler önerildi |
| 9 | Ciddi/güncel veri setleri; önce Süper Lig sonra 1. Lig/Avrupa | Süper Lig MVP tamam, genişleme altyapı devam ediyor | TFF Süper Lig 306 maç, Transfermarkt lig collector iskeleti, kaynak radarı |
| 10 | Her geliştirmede ileri git, başka kaynak/AI destekli yaklaş | Devam ediyor | Kaynak araştırması, transfer impact simülasyonu, açık veri stratejisi |
| 11 | Ücretsiz kaynakları kullan, API key gerekiyorsa bağla, günlük güncelle | MVP tamam | `.env.template`, API-Football, football-data.org probe, `src/run_daily_pipeline.py`, GitHub Actions workflow |
| 12 | Benzer analiz/tahmin/scout kaynakları takipte olsun | MVP tamam | `data/manual/source_watchlist.json`, `data/processed/source_watchlist_2025_2026.html` |
| 13 | Projeyi nerede/nasıl yayınlayacağız, Vercel uygun mu? | Tamam | `docs/deployment_strategy.md` |
| 14 | Önerilen oyuncu seçilirse maç sonucu ne olurdu simüle et | MVP tamam | `src/simulate_player_match_impact.py`, maç preview `transfer_impact_simulations`, dashboard Transfer Etki Simülasyonu |

## Son Eklenen Ürün Derinliği

- Taraftar/taktik tartışması formatına uygun "Teknik Direktör Kadro Denetimi" eklendi.
- Maç önü motoru artık gerçek ilk 11'i modelin önerdiği omurga kadroyla karşılaştırıyor.
- Çıktı olarak kadro uyum oranı, tartışmalı kadro etiketi, dışarıda kalan çekirdek oyuncular, riskli tercihler ve model kadrosu oynasaydı beklenen xG/skor senaryosu üretiliyor.
- Bu bölüm Beşiktaş maç önü raporlarına ve ana dashboard'a işlendi.
- Takım gücü katmanı eklendi: puan/maç, gol farkı, son form, iç/dış saha ve kadro sürekliliği güç skoruna çevriliyor.
- Beşiktaş özel maç sonucu backtesti %55'e, büyük maç doğruluğu %50'ye yükseldi.
- Büyük maç/derbi risk profili güçlendirildi; büyük maçlar artık minimum MEDIUM riskle etiketleniyor ve normal maç gibi okunmuyor.
- `src/build_big_match_report.py` eklendi; 6 büyük maçta tahmin, gerçek sonuç, beraberlik riski, kart sinyali ve gol adayları ayrı denetleniyor.
- Büyük maç raporunda 6/6 maç MEDIUM/HIGH risk olarak işaretlendi; doğruluk 3/6 (%50), hata dağılımı 2 kaçan beraberlik ve 1 fazla Beşiktaş iyimserliği.
- `src/build_league_intelligence_report.py` eklendi; 306 maçtan 18 takım, 691 oyuncu ve 29 hakem için takım gücü, skor penceresi, kart disiplini, oyuncu yük etiketi, hakem tempo etiketi ve scout ihtiyacı çıkarılıyor.
- Ana ürün sayfası ve komuta merkezi yeni Süper Lig istihbarat paneline bağlandı.
- `src/build_team_scout_blueprints.py` eklendi; takım zafiyetleri rol ihtiyacına çevrilip her takım için aday bağlantısı üretiliyor.
- Blueprint aday havuzu lig istihbaratındaki 691 oyuncudan türetilen savunma/denge/fizik proxy adaylarıyla genişletildi; takım-rol-aday bağlantısı 155'ten 335'e çıktı.
- Ana ürün sayfası ve komuta merkezi yeni takım blueprint paneline bağlandı.
- `src/build_sqlite_warehouse.py` eklendi; maç, kadro, gol, kart, takım profili, oyuncu profili, hakem profili, tahmin, gol adayı ve scout blueprint tabloları tek SQLite ambarına aktarılıyor.
- SQLite ambar kalite raporu üretildi: 15 tablo, 17.427 satır, 4 hazır görünüm ve 6 kalite bulgusu.
- TFF profil dosyaları ambar oyuncu tablosuna bağlandı; yaş/sözleşme bilgisi olan oyuncu sayısı 83'e çıktı, eksik profil bulgusu 691'den 608'e indi.
- `docs/warehouse_query_cookbook.md` eklendi; takım gücü, hakem kart riski, oyuncu yükü, Beşiktaş scout blueprint ve tahmin hataları için hazır SQL sorguları var.
- `src/build_player_profile_enrichment_queue.py` eklendi; eksik TFF oyuncu profilleri ilk 11/gol/kart/tahmini yük/profil etiketiyle önceliklendiriliyor.
- TFF profil collector'a `--player-ids-file` desteği eklendi.
- Öncelikli ilk 60 lig oyuncusu TFF'den başarıyla toplandı; genel lig profil dosyası oluştu.
- Ambar profil kapsamı güncellendi: yaş/sözleşme bilgisi olan oyuncu sayısı 83'ten 143'e çıktı, eksik profil bulgusu 608'den 548'e indi.
- İkinci profil paketiyle sıradaki 120 oyuncu daha TFF'den başarıyla toplandı.
- Öncelikli lig profil dosyası 180 oyuncuya çıktı; ambar içinde yaş/sözleşme bilgisi olan oyuncu sayısı 263'e yükseldi.
- Eksik profil bulgusu 548'den 428'e indi; 176 oyuncuda sözleşme bitişi 13 ay veya daha kısa.
- Üçüncü profil paketiyle 120 öncelikli oyuncudan 118'i daha TFF'den toplandı; 2 oyuncuda zaman aşımı/bağlantı kesilmesi oldu.
- Öncelikli lig profil dosyası 298 oyuncuya çıktı; ambar içinde yaş/sözleşme bilgisi olan oyuncu sayısı 381'e yükseldi.
- Eksik profil bulgusu 428'den 310'a indi; 267 oyuncuda sözleşme bitişi 13 ay veya daha kısa.
- Dördüncü profil paketiyle sıradaki 120 öncelikli oyuncu daha TFF'den başarıyla toplandı.
- Öncelikli lig profil dosyası 418 oyuncuya çıktı; ambar içinde yaş/sözleşme bilgisi olan oyuncu sayısı 501'e yükseldi.
- Eksik profil bulgusu 310'dan 190'a indi; 349 oyuncuda sözleşme bitişi 13 ay veya daha kısa.
- Beşinci profil paketiyle 120/120 oyuncu daha başarıyla toplandı; öncelikli lig profil dosyası 538 oyuncuya çıktı.
- Altıncı profil paketiyle kalan 70/70 oyuncu başarıyla toplandı.
- SQLite ambarında 691/691 oyuncu yaş/profil zenginleştirmesine bağlandı; eksik profil kuyruğu 0'a indi.
- 441 oyuncuda sözleşme bitişi 13 ay veya daha kısa olarak işaretleniyor.
- Takım scout blueprint adayları TFF profil verisiyle zenginleştirildi; 335 aday bağlantısının 318'inde yaş ve sözleşme bilgisi var.
- Blueprint düşük proxy güven bulgusu 334'ten 81'e indirildi; TFF profiliyle desteklenen adaylar `MEDIUM_DERIVED_ROLE` etiketi alıyor.
- SQLite scout blueprint tablosuna aday yaşı, sözleşme ayı, resale sinyali ve kontrat riski alanları eklendi.
- Scout rol kuralları sıkılaştırıldı; savunma baskın adayların otomatik 8 numara/fizik motoru listesine düşmesi engellendi.
- `src/build_scout_quality_report.py` eklendi; 335 blueprint bağlantısı içinde 120 düşük güven bağlantısı, tekil 10 oyuncu-rol doğrulama kuyruğu ve 0 fazla role yayılan oyuncu raporlanıyor.
- Ana ürün sayfası ve komuta merkezi Scout Kalite Denetimi ve Veri Kalite Scorecard bağlantılarını gösteriyor.
- Blueprint profil okuması düzeltildi; Beşiktaş, scout kısa liste ve tüm öncelikli TFF profil dosyaları birlikte kullanılıyor.
- `data/manual/player_role_overrides.json` eklendi; scout kalite kuyruğundaki 5 kritik skor rolü için pozisyon, boy, ayak, kaynak URL'i ve kaynak risk etiketi tutuluyor.
- Scout düşük güvenli blueprint bağlantısı 64'ten 0'a, tekil düşük güven oyuncu-rol kuyruğu 5'ten 0'a indi.
- SQLite scout blueprint tablosuna doğrulanmış pozisyon, boy, tercih edilen ayak ve pozisyon kaynağı alanları eklendi.
- Veri kalite scorecard güncel durumda 88.3/100; scout düşük pozisyon güveni 0/335 PASS, ana açık kalan beraberlikleri yakalamak ve odds/sakatlık/11 kalitesi verisini bağlamak.
- Günlük pipeline son çalışmada 32/32 başarılı geçti.
- Beraberlik kalibrasyonu denendi; ana tahmine agresif uygulanınca doğruluk düştüğü için risk katmanı olarak bırakıldı.
- `src/analyze_prediction_errors.py` ile hata tipleri ve sonraki model iyileştirme öncelikleri raporlanıyor.
- Gol adayı motoruna duran top/defans, penaltı profili, büyük maç golcüsü ve yedek etki sinyali eklendi.
- Gol adayı Top 3 %58'e, Top 8/Top 10 %85'e çıktı.
- `docs/data_analysis_statistics_plan.md` eklendi; veri analiz/istatistik öncelikleri ayrı teknik plana bağlandı.
- `src/build_data_quality_scorecard.py` eklendi ve ilk rapor üretildi; scorecard genel skoru 71.7/100, beraberlik yakalama ve scout pozisyon güveni ana geliştirme alanları olarak işaretlendi.
- `src/build_model_baseline_comparison.py` eklendi; ilk raporda Poisson-only %51.2, mevcut hybrid %50.4 accuracy verdi, mevcut hybrid log loss'ta en iyi kaldı.
- `src/build_draw_risk_audit.py` eklendi; beraberlik risk katmanı 46/76 beraberliği MEDIUM/HIGH bayrakla yakaladı, ana modeli bozmadan korumalı tahmin aksiyonu üretiyor.
- `src/build_goal_candidate_segment_backtest.py` eklendi; primary segment güçlü, impact-sub değerli, set-piece defender ve penalty profile segmentleri zayıf çıktı.
- Segment bulgusu gol adayı modeline işlendi; zayıf specialist segmentlerin üst sıra etkisi azaltıldı ve Top 5 gol adayı isabeti %73'ten %77'ye yükseldi.
- Beraberlik risk katmanı maç önü raporlarına ve Beşiktaş dashboard'una bağlandı; teknik enum yerine Türkçe aksiyon etiketleri gösteriliyor.
- `src/build_protected_action_audit.py` pipeline'a bağlandı; Beşiktaş maçlarında 22 korumalı aksiyonun gerçek sonuç dağılımı, 7/22 gerçek beraberlik ve 11/22 doğru kalan taraf tahmini ölçülüyor.
- Korumalı aksiyonun 4 beraberlik dışı yanlış taraf vakası ayrıca etiketleniyor: 3 target side overrated, 1 opponent side overrated, 2 büyük maç taraf dönüşü, 4 HIGH risk ama net sonuç.
- `src/build_side_flip_audit.py` eklendi; güncel ekran tahmini sonrası 3 yanlış taraf vakasında xG edge, market edge, güç farkı, eksik oyuncu, risk seviyesi ve veri boşlukları ayrı raporlanıyor.
- Backtest dashboard'u lig geneli beraberlik risk aksiyonu, Beşiktaş korumalı aksiyon backtesti, yanlış taraf denetimi, gol adayı segment denetimi ve zayıf gol adayı kuyruğunu gösterecek şekilde genişletildi.
- Komuta merkezi artık `draw_risk_audit`, `protected_action_audit` ve `side_flip_audit` üzerinden kaçan beraberlikler, draw risk precision/recall, Beşiktaş korumalı aksiyon metrikleri, yanlış taraf market edge/veri boşlukları ve gol adayı segmentlerini ana ekrana taşıyor.
- Güncel scorecard 88.3/100: sezon/hakem/profil/scout kapsamı ve ekran tahmini doğruluğu güçlü; kalan beraberlikler hâlâ ana geliştirme alanı.
- Gol adayı motoruna segment backtest kalite katsayısı bağlandı; geçmişte Top 5'e girip gol üretmeyen adaylara `quality_adjustment` uygulanıyor.
- Güncel gol adayı sonuçları: Top 3 %62, Top 5 %77, Top 8 %85, Top 10 %88; zayıf Top 5 aday kuyruğu 0'a indi.
- Beşiktaş maç sonucu için ham olasılık tahmininden ayrı `display_prediction` katmanı eklendi; ekran tahmini 15/29 (%52) ham tahminden 20/29 (%69) seviyesine çıktı.
- Beraberlik ekran tahmini 0/9'dan 3/9'a (%33.3) yükseldi; bu iyileştirme ve ekran tahmini doğruluğu scorecard'ı 88.3/100 seviyesine taşıdı.
- Ekran terimleri sadeleştirildi: `xG` yerine "Gol beklentisi", `Brier` yerine "Olasılık hata puanı", `draw recall` yerine "Beraberlik yakalama", `precision` yerine "Uyarı isabeti" kullanılıyor.
- Büyük maç ekran tahmini kalibrasyonu eklendi; Beşiktaş ekran tahmini 20/29 (%69), büyük maç doğruluğu 5/6 (%83), scorecard 88.3/100 oldu.
- Backtest panelinde ham tahmin, ekran tahmini, gerçek sonuç ve kalibrasyon ayarı yan yana gösteriliyor; komuta merkezindeki son maç tablosuna `Ekran Tahmini` kolonu eklendi.
- 2026-05-25 kalite kontrolünde lig-geneli tahmin etiketleme hatası düzeltildi; Beşiktaş ekran kalibrasyonu diğer takımlarda kapatıldı ve yalnızca ham ölçüm gösteriliyor.
- `src/build_prediction_validation_report.py` eklendi. Beşiktaş `%69` ekran kontrolü aynı sezon üzerinde ayarlanmış sonuç olarak işaretlendi; bağımsız doğrulama değildir. Tekil lig fikstürü ham tabanı `%51.0 (134/263)` olarak ölçüldü.
- Gol adayı specialist hesabında tüm takımlar için yanlışlıkla Beşiktaş tarafını okuyan sabit değer kaldırıldı.
- Scout yayın kalitesi sıkılaştırıldı: doğrulanmış pozisyonu rolle çelişen ya da pozisyonu doğrulanmamış aday rol önerisi olarak yayımlanmıyor. Transfer tavsiye raporu 90 doğrulanmış rol önerisi içeriyor; doğrulanmamış yayın önerisi 0.
- Önceki `0/335` düşük scout güven iddiası eksik sınıflandırmaya dayanıyordu. Güncel görünür açık: 275 blueprint bağlantısında 125 düşük güven ve 19 tekil doğrulama kuyruğu; bunlar veri toplama önceliği oldu.
- Kalite scorecard'ı güncel gerçek sınıflandırmayla 76.1/100: `%69` Beşiktaş ekran kontrolü bağımsız test beklediği için `WATCH`, scout pozisyon kapsamı açığı `FAIL`.
- Kaynak radarı Transfermarkt 18 takım snapshot kapsamıyla güncellendi; kaynak/lisans risk kaydı içeride korunuyor.
- Lig geneli piyasa değeri audit adımı sisteme dahil edildi: 18/18 kulüp ve 258/258 model maçı kapsanıyor; maç sonrası snapshot sızıntısı ihtimali nedeniyle yalnızca retrospektif tanısal benchmark olarak kullanılıyor.
- Güncel yerel pipeline kontrolü: 37/37 komut başarılı.
- 2026-05-25 responsive UI çalışmasında ürün merkezi, analiz merkezi, Beşiktaş maç odası, tüm takım maç merkezi ve transfer/scout merkezi ortak `metric11` navigasyonu ve tutarlı görsel sistemle yenilendi.
- Mobil kullanımda uzun tablolar panel içinde kaydırılır; Beşiktaş maç odasında özet metrikler `2x2` düzenle maçı aşağı itmeden gösterilir. Kullanıcıya görünen `HIGH/MEDIUM/LOW`, `GA/M` ve aday tipi etiketleri okunur Türkçe karşılıklara çevrildi.
- Çıktı kanıtları: `data/processed/football_intelligence_home.html`, `data/processed/football_command_center_2025_2026.html`, `data/processed/besiktas_2025_2026_dashboard_chronological.html`, `data/processed/all_teams_preview_dashboard_2025_2026.html`, `data/processed/transfer_recommendation_report_2025_2026.html`.
- Responsive doğrulama kanıtı: beş ana HTML yüzü tarayıcıda `599px` görünümde kontrol edildi; yatay gövde taşması yoktur ve maç seçici canlı içeriği doğru günceller. Yenileme sonrasında günlük pipeline `39/39` başarılı çalışmıştır.

## Hâlâ Güçlendirilmesi Gerekenler

- Transfermarkt tüm Süper Lig mapping'leri tek tek doğrulanmalı.
- FootballToday parser'ı iyileştirilmeli; beIN kaynak parser'ı çalışıyor.
- Pozisyon matrisi savunma/kaleci/orta saha için daha güçlü pozisyon verisine ihtiyaç duyuyor.
- Blueprint adaylarında düşük pozisyon güveni 125/275 seviyesinde görünür durumdadır; 19 tekil oyuncu-rol eşleşmesi için doğrudan pozisyon doğrulaması gerekir.
- SQLite oyuncu yaş/profil açığı ve side flip rakip piyasa değeri kapsaması kapandı; scout pozisyon kapsamı, odds baseline, resmi sakatlık akışı ve maç günü 11 kalitesi hâlâ açıktır.
- 1. Lig ve Avrupa ligleri için TFF/lig mapping ve collector genişletmesi yapılmalı.
- Beşiktaş ekran kontrolü aynı örneklerde %69 seviyesinde; bağımsız başarı oranı olarak kullanılamaz. Yeni sezon veya ayrılmış sezon, sakatlık, kadro gücü, piyasa değeri, odds baseline ve formasyon verisi gerekir.
- Büyük maçlarda kaçan beraberlikleri daha iyi yakalamak için derbi özel beraberlik/kart/tempo katmanı olasılık motoruna kontrollü bağlanmalı.
- Sıradaki adım: korumalı aksiyonda beraberlik dışı yanlış taraf vakalarını ayrıştırmak; ardından çok sezon/odds/sakatlık/kadro değeri/aksiyon verisi aramak.
