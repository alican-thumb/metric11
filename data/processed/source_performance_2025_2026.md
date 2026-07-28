# Erken Haber Kaynak Performansı

- Transfer sinyali: 61
- Resmi olaya dönüşen transfer: 7
- Yayın zamanı bulunan resmi teyit: 2/7
- İlk görülme zamanı bulunan resmi teyit: 7/7
- Ölçülen kaynak: 102 / gözlenen kaynak: 165
- Hesaplanabilir erken haber süresi: 0
- İlk görülmeye göre üst-sınır süre: 0
- X verisi bekleyen izlenen kaynak: 20
- Defterde korunan ilk iddia gözlemi: 2700

## Kanal Kapsamı

- Google News: 258 haber, 30/30 başarılı sorgu.
- Telegram: 6 mesaj, 8/8 erişilebilir kanal.
- X: durum=MISSING_CREDENTIALS, gönderi=0, yapılandırılmış hesap=45.

## Kanal Ölçümü

| Kanal | Gözlem | Ölçülebilir İddia | Resmiye Dönüşen | Ort. Erken Saat | İlk Görülme Üst-Sınırı | Vekil Yanlış Alarm | Skor | Durum |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Google News / medya | 2697 | 795 | 1 | — | — | %99.8 | 0.1 | PARTIAL_MEASUREMENT |
| Muhabire atıflı medya | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Telegram | 2 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| X | 0 | 0 | 0 | — | — | — | — | X_DATA_UNAVAILABLE |

## Muhabir İzleme

- Google News muhabir sorgusu erken bulgu aramasıdır; yalnız başlıkta açık muhabir atfı taşıyan transfer iddiaları `MEDIA_REPUBLICATION` gözlemi olarak yazılır.

| Muhabir / Ağ | Google Arama Bulgusu | Atıflı Gözlem | Ölçülebilir İddia | Skor Durumu |
|---|---:|---:|---:|---|
| Yağız Sabuncuoğlu | 4 | 1 | 1 | PARTIAL_MEASUREMENT |
| Ertan Süzgün | 1 | 0 | 0 | ATTRIBUTION_PENDING |
| Sports Digitale | 2 | 0 | 0 | ATTRIBUTION_PENDING |
| Yusuf Günaydın | 0 | 0 | 0 | ATTRIBUTION_PENDING |
| Ekrem Konur | 0 | 0 | 0 | ATTRIBUTION_PENDING |

## Skorlama Notu

- Resmi teyide dönüşüm, aynı oyuncu ve hedef kulüp için resmi kulüp duyurusu bulunduğunda sayılır.
- Erken haber saati yalnız hem ilk sinyal hem resmi duyuru yayın zamanı varsa kesin olarak hesaplanır; resmi yayın saati yoksa ilk görülen an ayrı üst-sınır metriğidir.
- Yanlış alarm vekili, 14 günden eski olup resmi teyide dönüşmemiş yönü belirli iddiadır; kesin yanlış bilgi hükmü değildir.

## Kaynaklar

| Kaynak | Katman | Gözlem | Ölçülebilir İddia | Resmiye Dönüşen | Ort. Erken Saat | İlk Görülme Üst-Sınırı | Vekil Yanlış Alarm | Skor | Durum |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| CNN Türk Spor | MEDIA | 77 | 17 | 1 | — | — | %92.3 | 6.2 | PARTIAL_MEASUREMENT |
| Fotomaç | MEDIA | 333 | 69 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Sabah | MEDIA | 225 | 54 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Hürriyet | MEDIA | 201 | 24 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Takvim | MEDIA | 170 | 26 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Aksam Spor | MEDIA | 139 | 10 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Haberturk Spor | MEDIA | 114 | 10 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Milliyet | MEDIA | 81 | 15 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| A SPOR | MEDIA | 79 | 29 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| NTVSpor | MEDIA | 79 | 16 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Fanatik | MEDIA | 77 | 28 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Sporx.com | MEDIA | 68 | 54 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Ajansspor | MEDIA | 67 | 26 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| SonDakika | MEDIA | 67 | 40 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| GZT | MEDIA | 66 | 17 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Son Dakika | MEDIA | 59 | 34 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Taka Gazete | MEDIA | 55 | 40 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Habertürk | MEDIA | 39 | 23 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Haberler | MEDIA | 38 | 17 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Anadolu Ajansı Spor | AGENCY | 35 | 11 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| beinsports.com.tr | MEDIA | 31 | 8 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Haber 7 | MEDIA | 26 | 4 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Yeniçağ Gazetesi | MEDIA | 26 | 7 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Halk TV | MEDIA | 24 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Transfermarkt | MEDIA | 24 | 10 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Ensonhaber | MEDIA | 21 | 14 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| FOTOMAÇ | MEDIA | 21 | 4 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| sondakika.com | MEDIA | 21 | 14 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| HaberTS | MEDIA | 20 | 13 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Gazete Vatan | MEDIA | 19 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| T24 | MEDIA | 16 | 6 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Mynet | MEDIA | 11 | 4 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Tıbbiye Bülteni | MEDIA | 11 | 11 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| 61SAAT | MEDIA | 10 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| CNN Türk | MEDIA | 10 | 4 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Eurohoops | MEDIA | 10 | 3 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Fotospor | MEDIA | 10 | 4 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Mackolik.com | MEDIA | 10 | 7 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Mersin Haber | MEDIA | 9 | 3 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Nefes Gazetesi | MEDIA | 9 | 3 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Cumhuriyet | MEDIA | 8 | 3 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Gazete Gerçek | MEDIA | 8 | 4 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Karadeniz Gazetesi | MEDIA | 8 | 3 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Sporx | MEDIA | 8 | 7 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| birgun.net | MEDIA | 8 | 5 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Haber61 | MEDIA | 7 | 3 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| İhlas Haber Ajansı | MEDIA | 7 | 4 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| DHA / Demirören Haber Ajansı | MEDIA | 6 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Konya Yeni Haber | MEDIA | 6 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| AKŞAM | MEDIA | 5 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Aksiyon.com.TR | MEDIA | 5 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| MSN | MEDIA | 5 | 4 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| NTV Haber | MEDIA | 5 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Anadolu Ajansı | MEDIA | 4 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Evrensel.net | MEDIA | 4 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| IHA | MEDIA | 4 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Yeni Alanya | MEDIA | 4 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Çağdaş Kocaeli Gazetesi | MEDIA | 4 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| İlkses Gazetesi | MEDIA | 4 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| 24 Saat Gazetesi Ankara | MEDIA | 3 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Orta Çizgi | MEDIA | 3 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| İstanbul Ticaret Gazetesi | MEDIA | 3 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| 2 Mart Gazetesi | MEDIA | 2 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| A Haber | MEDIA | 2 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| CUMHA Cumhur Haber Ajansı | MEDIA | 2 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Diken | MEDIA | 2 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Ege Alternatif | MEDIA | 2 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Internet Haber | MEDIA | 2 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Odatv | MEDIA | 2 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| TGRT Haber | MEDIA | 2 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Turkmenportal.com | MEDIA | 2 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| bolgegundemi.com | MEDIA | 2 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| fanatik.com.tr | MEDIA | 2 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Afyon Türkeli Gazetesi | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Antalya Haber - Kanal V | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| BBC | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Başka Gazete | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Beşiktaş Haberleri | SECONDARY | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Bursa Hakimiyet | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Canlı Gaste | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Gaziantep Söz | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Gündem Beşiktaş | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Haber 1 | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Haber Aktüel | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Haber Kıbrıs | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Hentbolhaber.Net | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Hunat TV | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Investing.com Türkiye | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Kocaeli Barış Gazetesi | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Kocaeli Kent Gazetesi | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Malta Haber | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Memleket | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| NationalTurk | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Olay53.com | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Vietnam.vn | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Webaslan | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Yayla Haber | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Yağız Sabuncuoğlu | ATTRIBUTED_MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| alanyaturk.com | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| haberler.com | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| radikal.com.tr | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| İstiklal Gazetesi | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Yeni Şafak | MEDIA | 10 | 0 | 0 | — | — | — | — | OBSERVING |
| Sözcü Gazetesi | MEDIA | 8 | 1 | 0 | — | — | — | — | OBSERVING |
| Alanya Postası | MEDIA | 7 | 0 | 0 | — | — | — | — | OBSERVING |
| Türkiye Gazetesi | MEDIA | 7 | 0 | 0 | — | — | — | — | OBSERVING |
| STAR - Haberler | MEDIA | 5 | 0 | 0 | — | — | — | — | OBSERVING |
| Samsun Haber | MEDIA | 5 | 1 | 0 | — | — | — | — | OBSERVING |
| Özgür Kocaeli | MEDIA | 4 | 0 | 0 | — | — | — | — | OBSERVING |
| Duhuliye | MEDIA | 3 | 1 | 0 | — | — | — | — | OBSERVING |
| Goal.com | MEDIA | 3 | 0 | 0 | — | — | — | — | OBSERVING |
| Saray Medya | MEDIA | 3 | 1 | 0 | — | — | — | — | OBSERVING |
| Anadolu'da Bugün | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Gunebakış | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Gözlem Gazetesi | MEDIA | 2 | 1 | 0 | — | — | — | — | OBSERVING |
| Habername.com | MEDIA | 2 | 1 | 0 | — | — | — | — | OBSERVING |
| Konya Postası Gazetesi | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Konya Yenigün Gazetesi | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Konya'nın Sesi | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Merhaba Gazetesi | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Patronlar Dünyası | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Yeni Akit Gazetesi | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Yeni Asır | MEDIA | 2 | 1 | 0 | — | — | — | — | OBSERVING |
| Yüksekova Haber | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| samsunhaber.com | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| İz Gazete | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Afyon Haber | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Afyon Şehir | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Akdeniz Manşet Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Anadolu'da Bugün Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Ardahan Haber | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Artı Gerçek | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Bugün Kocaeli Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Bundle | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Ege'de Sonsöz | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Erzurum Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Fenerbahçe Spor Kulübü | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Gazete Arena | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Gaziantep Oluşum Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Gerçek İzmir | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Haber Ekspres | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Haber Vakti | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Haber3 | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Halk 54 | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Kars Manşet | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Kayseri Anadolu Haber | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Konya Yenigün | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Kurtalan Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| NTV Spor | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Rizedeyiz | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Samsun Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Samsun Kent Haber | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Samsun Son Haber | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| SuperHaber | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Trabzonhaber24 | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Transfer Haber | SECONDARY | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Ulusal Kanal | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Yeni Çağrı Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Yenigün Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Yeşil Afşin Gazetesi | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| politikam.com | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| tv100 Haber | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Çorum Haber Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Çorum Hakimiyet | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| İstanbul Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
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