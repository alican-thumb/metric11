# Erken Haber Kaynak Performansı

- Transfer sinyali: 65
- Resmi olaya dönüşen transfer: 5
- Yayın zamanı bulunan resmi teyit: 2/5
- İlk görülme zamanı bulunan resmi teyit: 5/5
- Ölçülen kaynak: 78 / gözlenen kaynak: 154
- Hesaplanabilir erken haber süresi: 0
- İlk görülmeye göre üst-sınır süre: 0
- X verisi bekleyen izlenen kaynak: 20
- Defterde korunan ilk iddia gözlemi: 2191

## Kanal Kapsamı

- Google News: 275 haber, 30/30 başarılı sorgu.
- Telegram: 6 mesaj, 8/8 erişilebilir kanal.
- X: durum=MISSING_CREDENTIALS, gönderi=0, yapılandırılmış hesap=45.

## Kanal Ölçümü

| Kanal | Gözlem | Ölçülebilir İddia | Resmiye Dönüşen | Ort. Erken Saat | İlk Görülme Üst-Sınırı | Vekil Yanlış Alarm | Skor | Durum |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Google News / medya | 2188 | 621 | 1 | — | — | %99.7 | 0.3 | PARTIAL_MEASUREMENT |
| Muhabire atıflı medya | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Telegram | 2 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| X | 0 | 0 | 0 | — | — | — | — | X_DATA_UNAVAILABLE |

## Muhabir İzleme

- Google News muhabir sorgusu erken bulgu aramasıdır; yalnız başlıkta açık muhabir atfı taşıyan transfer iddiaları `MEDIA_REPUBLICATION` gözlemi olarak yazılır.

| Muhabir / Ağ | Google Arama Bulgusu | Atıflı Gözlem | Ölçülebilir İddia | Skor Durumu |
|---|---:|---:|---:|---|
| Yağız Sabuncuoğlu | 3 | 1 | 1 | PARTIAL_MEASUREMENT |
| Ertan Süzgün | 2 | 0 | 0 | ATTRIBUTION_PENDING |
| Sports Digitale | 0 | 0 | 0 | ATTRIBUTION_PENDING |
| Yusuf Günaydın | 1 | 0 | 0 | ATTRIBUTION_PENDING |
| Ekrem Konur | 1 | 0 | 0 | ATTRIBUTION_PENDING |

## Skorlama Notu

- Resmi teyide dönüşüm, aynı oyuncu ve hedef kulüp için resmi kulüp duyurusu bulunduğunda sayılır.
- Erken haber saati yalnız hem ilk sinyal hem resmi duyuru yayın zamanı varsa kesin olarak hesaplanır; resmi yayın saati yoksa ilk görülen an ayrı üst-sınır metriğidir.
- Yanlış alarm vekili, 14 günden eski olup resmi teyide dönüşmemiş yönü belirli iddiadır; kesin yanlış bilgi hükmü değildir.

## Kaynaklar

| Kaynak | Katman | Gözlem | Ölçülebilir İddia | Resmiye Dönüşen | Ort. Erken Saat | İlk Görülme Üst-Sınırı | Vekil Yanlış Alarm | Skor | Durum |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| CNN Türk Spor | MEDIA | 61 | 14 | 1 | — | — | %88.9 | 8.9 | PARTIAL_MEASUREMENT |
| Fotomaç | MEDIA | 275 | 54 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Sabah | MEDIA | 185 | 40 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Hürriyet | MEDIA | 162 | 19 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Takvim | MEDIA | 134 | 14 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Aksam Spor | MEDIA | 109 | 7 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Haberturk Spor | MEDIA | 96 | 8 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| A SPOR | MEDIA | 72 | 27 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Milliyet | MEDIA | 70 | 14 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| NTVSpor | MEDIA | 66 | 14 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Fanatik | MEDIA | 59 | 21 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Sporx.com | MEDIA | 57 | 44 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Taka Gazete | MEDIA | 52 | 39 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Son Dakika | MEDIA | 50 | 27 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Ajansspor | MEDIA | 49 | 19 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| GZT | MEDIA | 49 | 11 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| SonDakika | MEDIA | 45 | 24 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Habertürk | MEDIA | 35 | 19 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Anadolu Ajansı Spor | AGENCY | 30 | 8 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Haberler | MEDIA | 29 | 12 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| beinsports.com.tr | MEDIA | 27 | 7 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Yeniçağ Gazetesi | MEDIA | 26 | 7 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| FOTOMAÇ | MEDIA | 21 | 4 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Halk TV | MEDIA | 18 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| HaberTS | MEDIA | 17 | 11 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Transfermarkt | MEDIA | 17 | 7 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Gazete Vatan | MEDIA | 16 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Ensonhaber | MEDIA | 13 | 7 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| T24 | MEDIA | 13 | 6 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| sondakika.com | MEDIA | 12 | 7 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Tıbbiye Bülteni | MEDIA | 10 | 10 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Mynet | MEDIA | 9 | 3 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Nefes Gazetesi | MEDIA | 9 | 3 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| CNN Türk | MEDIA | 8 | 4 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Eurohoops | MEDIA | 8 | 3 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Mackolik.com | MEDIA | 8 | 5 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Mersin Haber | MEDIA | 8 | 3 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| 61SAAT | MEDIA | 7 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Karadeniz Gazetesi | MEDIA | 7 | 3 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Sporx | MEDIA | 7 | 6 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| birgun.net | MEDIA | 7 | 4 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Fotospor | MEDIA | 6 | 3 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Gazete Gerçek | MEDIA | 6 | 3 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| İhlas Haber Ajansı | MEDIA | 6 | 3 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Haber61 | MEDIA | 5 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Konya Yeni Haber | MEDIA | 5 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Evrensel.net | MEDIA | 4 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| IHA | MEDIA | 4 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| NTV Haber | MEDIA | 4 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Yeni Alanya | MEDIA | 4 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| İlkses Gazetesi | MEDIA | 4 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| MSN | MEDIA | 3 | 3 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Orta Çizgi | MEDIA | 3 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Çağdaş Kocaeli Gazetesi | MEDIA | 3 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| İstanbul Ticaret Gazetesi | MEDIA | 3 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| 2 Mart Gazetesi | MEDIA | 2 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| A Haber | MEDIA | 2 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Diken | MEDIA | 2 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Turkmenportal.com | MEDIA | 2 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| fanatik.com.tr | MEDIA | 2 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Afyon Türkeli Gazetesi | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| BBC | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Beşiktaş Haberleri | SECONDARY | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Gaziantep Söz | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Haber Kıbrıs | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Hentbolhaber.Net | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Internet Haber | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Kocaeli Barış Gazetesi | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Kocaeli Kent Gazetesi | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Malta Haber | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Memleket | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Odatv | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Vietnam.vn | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Yağız Sabuncuoğlu | ATTRIBUTED_MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| alanyaturk.com | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| bolgegundemi.com | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| haberler.com | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| radikal.com.tr | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Haber 7 | MEDIA | 20 | 2 | 0 | — | — | — | — | OBSERVING |
| Cumhuriyet | MEDIA | 7 | 3 | 0 | — | — | — | — | OBSERVING |
| Türkiye Gazetesi | MEDIA | 7 | 0 | 0 | — | — | — | — | OBSERVING |
| Yeni Şafak | MEDIA | 7 | 0 | 0 | — | — | — | — | OBSERVING |
| Sözcü Gazetesi | MEDIA | 6 | 0 | 0 | — | — | — | — | OBSERVING |
| Aksiyon.com.TR | MEDIA | 5 | 2 | 0 | — | — | — | — | OBSERVING |
| DHA / Demirören Haber Ajansı | MEDIA | 5 | 2 | 0 | — | — | — | — | OBSERVING |
| STAR - Haberler | MEDIA | 5 | 0 | 0 | — | — | — | — | OBSERVING |
| 24 Saat Gazetesi Ankara | MEDIA | 3 | 1 | 0 | — | — | — | — | OBSERVING |
| Anadolu Ajansı | MEDIA | 3 | 1 | 0 | — | — | — | — | OBSERVING |
| Goal.com | MEDIA | 3 | 0 | 0 | — | — | — | — | OBSERVING |
| Samsun Haber | MEDIA | 3 | 0 | 0 | — | — | — | — | OBSERVING |
| AKŞAM | MEDIA | 2 | 1 | 0 | — | — | — | — | OBSERVING |
| Alanya Postası | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Anadolu'da Bugün | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| CUMHA Cumhur Haber Ajansı | MEDIA | 2 | 1 | 0 | — | — | — | — | OBSERVING |
| Ege Alternatif | MEDIA | 2 | 1 | 0 | — | — | — | — | OBSERVING |
| Konya Yenigün Gazetesi | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Merhaba Gazetesi | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Patronlar Dünyası | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| TGRT Haber | MEDIA | 2 | 1 | 0 | — | — | — | — | OBSERVING |
| samsunhaber.com | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Özgür Kocaeli | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| İz Gazete | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Afyon Şehir | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Akdeniz Manşet Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Anadolu'da Bugün Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Antalya Haber - Kanal V | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Artı Gerçek | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Başka Gazete | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Bugün Kocaeli Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Bursa Hakimiyet | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Canlı Gaste | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Duhuliye | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Ege'de Sonsöz | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Erzurum Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Fenerbahçe Spor Kulübü | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Gaziantep Oluşum Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Gerçek İzmir | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Gunebakış | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Gözlem Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Gündem Beşiktaş | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Haber 1 | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Haber Aktüel | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Haber Ekspres | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Haber Vakti | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Haber3 | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Habername.com | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Hunat TV | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Investing.com Türkiye | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Kars Manşet | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Konya Postası Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Kurtalan Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| NTV Spor | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| NationalTurk | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Olay53.com | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Samsun Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Samsun Son Haber | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Saray Medya | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| SuperHaber | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Trabzonhaber24 | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Transfer Haber | SECONDARY | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Ulusal Kanal | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Webaslan | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Yayla Haber | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Yeni Akit Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Yeni Asır | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Yeni Çağrı Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Yenigün Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Yüksekova Haber | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| politikam.com | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| tv100 Haber | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Çorum Haber Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Çorum Hakimiyet | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| İstanbul Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| İstiklal Gazetesi | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| @EkremKonur | SECONDARY | 0 | 0 | 0 | — | — | — | — | X_DATA_UNAVAILABLE |
| @FBhaberleri | SECONDARY | 0 | 0 | 0 | — | — | — | — | X_DATA_UNAVAILABLE |
| @FabrizioRomano | SECONDARY | 0 | 0 | 0 | — | — | — | — | X_DATA_UNAVAILABLE |
| @GShaberleri | SECONDARY | 0 | 0 | 0 | — | — | — | — | X_DATA_UNAVAILABLE |
| @GercekBJK | SECONDARY | 0 | 0 | 0 | — | — | — | — | X_DATA_UNAVAILABLE |
| @GizemKaya__ | SECONDARY | 0 | 0 | 0 | — | — | — | — | X_DATA_UNAVAILABLE |
| @KaraKartalBlog | SECONDARY | 0 | 0 | 0 | — | — | — | — | X_DATA_UNAVAILABLE |
| @NicoSchira | SECONDARY | 0 | 0 | 0 | — | — | — | — | X_DATA_UNAVAILABLE |
| @Sansal_Buyuk | SECONDARY | 0 | 0 | 0 | — | — | — | — | X_DATA_UNAVAILABLE |
| @SportsDigitale | SECONDARY | 0 | 0 | 0 | — | — | — | — | X_DATA_UNAVAILABLE |
| @TShaberleri1907 | SECONDARY | 0 | 0 | 0 | — | — | — | — | X_DATA_UNAVAILABLE |
| @WebdikBesiktas | SECONDARY | 0 | 0 | 0 | — | — | — | — | X_DATA_UNAVAILABLE |
| @YakinTakip | SECONDARY | 0 | 0 | 0 | — | — | — | — | X_DATA_UNAVAILABLE |
| @ertansuzgun | SECONDARY | 0 | 0 | 0 | — | — | — | — | X_DATA_UNAVAILABLE |
| @hamitsalih | SECONDARY | 0 | 0 | 0 | — | — | — | — | X_DATA_UNAVAILABLE |
| @transfermarkt | SECONDARY | 0 | 0 | 0 | — | — | — | — | X_DATA_UNAVAILABLE |
| @transfermarkt_TR | SECONDARY | 0 | 0 | 0 | — | — | — | — | X_DATA_UNAVAILABLE |
| @ugurtuncay | SECONDARY | 0 | 0 | 0 | — | — | — | — | X_DATA_UNAVAILABLE |
| @yagosabuncuoglu | SECONDARY | 0 | 0 | 0 | — | — | — | — | X_DATA_UNAVAILABLE |
| @yusufgunaydn | SECONDARY | 0 | 0 | 0 | — | — | — | — | X_DATA_UNAVAILABLE |
| Fenerbahçe Haberleri | SECONDARY | 0 | 0 | 0 | — | — | — | — | NO_TRANSFER_CLAIMS |
| Galatasaray Haberleri | SECONDARY | 0 | 0 | 0 | — | — | — | — | NO_TRANSFER_CLAIMS |
| Spor Transfer | SECONDARY | 0 | 0 | 0 | — | — | — | — | NO_TRANSFER_CLAIMS |
| Sporx Haber | SECONDARY | 0 | 0 | 0 | — | — | — | — | NO_TRANSFER_CLAIMS |
| Trabzonspor Haberleri | SECONDARY | 0 | 0 | 0 | — | — | — | — | NO_TRANSFER_CLAIMS |
| Transfer Türkiye | SECONDARY | 0 | 0 | 0 | — | — | — | — | NO_TRANSFER_CLAIMS |