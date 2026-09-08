# Erken Haber Kaynak Performansı

- Transfer sinyali: 38
- Resmi olaya dönüşen transfer: 12
- Yayın zamanı bulunan resmi teyit: 5/12
- İlk görülme zamanı bulunan resmi teyit: 12/12
- Ölçülen kaynak: 175 / gözlenen kaynak: 293
- Hesaplanabilir erken haber süresi: 0
- İlk görülmeye göre üst-sınır süre: 3
- X verisi bekleyen izlenen kaynak: 20
- Defterde korunan ilk iddia gözlemi: 3992

## Kanal Kapsamı

- Google News: 291 haber, 30/30 başarılı sorgu.
- Telegram: 6 mesaj, 8/8 erişilebilir kanal.
- X: durum=MISSING_CREDENTIALS, gönderi=0, yapılandırılmış hesap=45.

## Kanal Ölçümü

| Kanal | Gözlem | Ölçülebilir İddia | Resmiye Dönüşen | Ort. Erken Saat | İlk Görülme Üst-Sınırı | Vekil Yanlış Alarm | Skor | Durum |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Google News / medya | 3989 | 1294 | 5 | — | 0.3 | %99.5 | 0.4 | FIRST_SEEN_BOUND |
| Muhabire atıflı medya | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Telegram | 2 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| X | 0 | 0 | 0 | — | — | — | — | X_DATA_UNAVAILABLE |

## Muhabir İzleme

- Google News muhabir sorgusu erken bulgu aramasıdır; yalnız başlıkta açık muhabir atfı taşıyan transfer iddiaları `MEDIA_REPUBLICATION` gözlemi olarak yazılır.

| Muhabir / Ağ | Google Arama Bulgusu | Atıflı Gözlem | Ölçülebilir İddia | Skor Durumu |
|---|---:|---:|---:|---|
| Yağız Sabuncuoğlu | 2 | 1 | 1 | PARTIAL_MEASUREMENT |
| Ertan Süzgün | 3 | 0 | 0 | ATTRIBUTION_PENDING |
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
| nefes.com.tr | MEDIA | 5 | 1 | 1 | — | 0.3 | %0.0 | 80.0 | FIRST_SEEN_BOUND |
| 24 Saat Gazetesi Ankara | MEDIA | 6 | 2 | 1 | — | 0.2 | %50.0 | 40.0 | FIRST_SEEN_BOUND |
| Nefes Gazetesi | MEDIA | 19 | 6 | 1 | — | 0.3 | %83.3 | 13.3 | FIRST_SEEN_BOUND |
| Transfermarkt | MEDIA | 48 | 18 | 1 | — | — | %92.3 | 6.2 | PARTIAL_MEASUREMENT |
| CNN Türk Spor | MEDIA | 120 | 26 | 1 | — | — | %95.2 | 3.8 | PARTIAL_MEASUREMENT |
| Fotomaç | MEDIA | 434 | 91 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Sabah | MEDIA | 285 | 63 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Hürriyet | MEDIA | 266 | 39 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Takvim | MEDIA | 247 | 28 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Aksam Spor | MEDIA | 187 | 15 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Haberturk Spor | MEDIA | 153 | 13 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| NTVSpor | MEDIA | 104 | 24 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Fanatik | MEDIA | 101 | 34 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| GZT | MEDIA | 99 | 31 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Milliyet | MEDIA | 96 | 25 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Sporx.com | MEDIA | 96 | 76 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Son Dakika | MEDIA | 94 | 64 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Ajansspor | MEDIA | 89 | 36 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| A SPOR | MEDIA | 76 | 29 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Anadolu Ajansı Spor | AGENCY | 74 | 20 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Taka Gazete | MEDIA | 66 | 53 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Habertürk | MEDIA | 64 | 38 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| SonDakika | MEDIA | 57 | 34 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Haberler | MEDIA | 52 | 29 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| A Spor | MEDIA | 44 | 17 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Gazete Vatan | MEDIA | 44 | 3 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| beinsports.com.tr | MEDIA | 41 | 11 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Haber 7 | MEDIA | 33 | 5 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Ensonhaber | MEDIA | 32 | 20 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| sondakika.com | MEDIA | 32 | 25 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Halk TV | MEDIA | 29 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Yeniçağ Gazetesi | MEDIA | 28 | 8 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| HaberTS | MEDIA | 26 | 17 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| T24 | MEDIA | 24 | 12 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Mynet | MEDIA | 22 | 10 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| FOTOMAÇ | MEDIA | 21 | 4 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Sözcü Gazetesi | MEDIA | 20 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Cumhuriyet | MEDIA | 17 | 10 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Mackolik.com | MEDIA | 17 | 13 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| CNN Türk | MEDIA | 15 | 10 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Gazete Gerçek | MEDIA | 14 | 5 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Sporx | MEDIA | 14 | 12 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Yeni Şafak | MEDIA | 13 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Alanya Postası | MEDIA | 12 | 3 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Mersin Haber | MEDIA | 12 | 6 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| birgun.net | MEDIA | 12 | 7 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| fanatik.com.tr | MEDIA | 12 | 5 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| hurriyet.com.tr | MEDIA | 12 | 5 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Anadolu Ajansı | MEDIA | 11 | 8 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| DHA / Demirören Haber Ajansı | MEDIA | 11 | 6 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Haber61 | MEDIA | 11 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Tıbbiye Bülteni | MEDIA | 11 | 11 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| transfermarkt.com.tr | MEDIA | 11 | 4 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| 61SAAT | MEDIA | 10 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Eurohoops | MEDIA | 10 | 3 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Fotospor | MEDIA | 10 | 5 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Saray Medya | MEDIA | 10 | 3 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| ajansspor.com | MEDIA | 10 | 5 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| İhlas Haber Ajansı | MEDIA | 10 | 5 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| sporx.com | MEDIA | 9 | 9 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Karadeniz Gazetesi | MEDIA | 8 | 3 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Konya Yeni Haber | MEDIA | 8 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| STAR - Haberler | MEDIA | 8 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| gzt.com | MEDIA | 8 | 6 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| haberler.com | MEDIA | 8 | 6 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| sabah.com.tr | MEDIA | 8 | 6 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Evrensel.net | MEDIA | 7 | 3 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| NTV Haber | MEDIA | 7 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Yeni Alanya | MEDIA | 7 | 3 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Çağdaş Kocaeli Gazetesi | MEDIA | 7 | 3 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Aksiyon.com.TR | MEDIA | 6 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Gözlem Gazetesi | MEDIA | 6 | 5 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Manşet Haber | MEDIA | 6 | 3 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Samsun Gazetesi | MEDIA | 6 | 3 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Özgür Kocaeli | MEDIA | 6 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| İlkses Gazetesi | MEDIA | 6 | 4 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| AKŞAM | MEDIA | 5 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| MSN | MEDIA | 5 | 4 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Yeni Asır | MEDIA | 5 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| ensonhaber.com | MEDIA | 5 | 4 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| milliyet.com.tr | MEDIA | 5 | 3 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| A Haber | MEDIA | 4 | 4 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| IHA | MEDIA | 4 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Kocaeli Barış Gazetesi | MEDIA | 4 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Orta Çizgi | MEDIA | 4 | 3 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| İnternet Haber | MEDIA | 4 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| İz Gazete | MEDIA | 4 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| 2 Mart Gazetesi | MEDIA | 3 | 3 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Ege Alternatif | MEDIA | 3 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Ege'de Sonsöz | MEDIA | 3 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Haber Ege | MEDIA | 3 | 3 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Habername.com | MEDIA | 3 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Hunat TV | MEDIA | 3 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| KARAR | MEDIA | 3 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Konya Yenigün | MEDIA | 3 | 3 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Odatv | MEDIA | 3 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Son Dakika Samsun Haberleri | MEDIA | 3 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| aa.com.tr | MEDIA | 3 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| dokuzeylul.com | MEDIA | 3 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| mansethaber.com | MEDIA | 3 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| samsunhaber.com | MEDIA | 3 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| t24.com.tr | MEDIA | 3 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| yenisafak.com | MEDIA | 3 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| İstanbul Ticaret Gazetesi | MEDIA | 3 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Artı Gerçek | MEDIA | 2 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| CUMHA Cumhur Haber Ajansı | MEDIA | 2 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Diken | MEDIA | 2 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Gazete Pencere | MEDIA | 2 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Gerçek İzmir | MEDIA | 2 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Gündeme Bakış | MEDIA | 2 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Haber Aktüel | MEDIA | 2 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Investing.com Türkiye | MEDIA | 2 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Kayseri Gündem Gazetesi | MEDIA | 2 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Memleket | MEDIA | 2 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| TGRT Haber | MEDIA | 2 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Turkmenportal.com | MEDIA | 2 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| alanyapostasi.com.tr | MEDIA | 2 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| alanyaturk.com | MEDIA | 2 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| cnnturk.com | MEDIA | 2 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| haberts.com | MEDIA | 2 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| haberturk.com | MEDIA | 2 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| kayserihaber.com.tr | MEDIA | 2 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| mackolik.com | MEDIA | 2 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| takagazete.com.tr | MEDIA | 2 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| 2mart.com.tr | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Afyon Haber | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Afyon Türkeli Gazetesi | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Akdenizmanset | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Antalya Haber - Kanal V | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| BBC | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Başka Gazete | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Beşiktaş Haberleri | SECONDARY | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Bundle | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Bursa Hakimiyet | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Canlı Gaste | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Ege Postası | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Gaziantep Söz | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Giresun İleri Gazetesi | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Gündem Beşiktaş | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Güneydoğu Ekspres | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Haber 1 | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Haber Kıbrıs | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Hentbolhaber.Net | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Internet Haber | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| KAYSERİ YEREL HABER | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Kanal 3 Tv | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Kocaeli Kent Gazetesi | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Malta Haber | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Medya Siyah Beyaz | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| N Gazete | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| NationalTurk | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Olay53.com | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| SES15 | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Trakya Gazetesi | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Vietnam.vn | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Webaslan | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Yayla Haber | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Yağız Sabuncuoğlu | ATTRIBUTED_MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Yeşil Afşin Gazetesi | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| baskentgazete.com.tr | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| bolgegundemi.com | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| cumhuriyet.com.tr | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| dha.com.tr | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| egedesonsoz.com | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| fotomac.com.tr | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| fotospor.com.tr | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| haberege.com.tr | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| ilkses.com.tr | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| kayseriyerelhaber.com | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| medyasiyahbeyaz.com | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| ngazete.com | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| radikal.com.tr | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| siyasalbirikim.com.tr | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| trakyagazetesi.com.tr | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| İstiklal Gazetesi | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| ntvspor.net | MEDIA | 12 | 2 | 0 | — | — | — | — | OBSERVING |
| Türkiye Gazetesi | MEDIA | 8 | 0 | 0 | — | — | — | — | OBSERVING |
| gazetevatan.com | MEDIA | 7 | 0 | 0 | — | — | — | — | OBSERVING |
| Samsun Haber | MEDIA | 6 | 0 | 0 | — | — | — | — | OBSERVING |
| Goal.com | MEDIA | 5 | 0 | 0 | — | — | — | — | OBSERVING |
| Bugün Kocaeli Gazetesi | MEDIA | 3 | 0 | 0 | — | — | — | — | OBSERVING |
| gazetegercek.com.tr | MEDIA | 3 | 1 | 0 | — | — | — | — | OBSERVING |
| ntv.com.tr | MEDIA | 3 | 1 | 0 | — | — | — | — | OBSERVING |
| saraymedya.com | MEDIA | 3 | 0 | 0 | — | — | — | — | OBSERVING |
| 24saatgazetesi.com | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| 61saat.com | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Anadolu'da Bugün | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Duhuliye | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| GALATASARAY.ORG | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Gazete Arena | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Gaziantep Oluşum Gazetesi | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Gerçek Fethiye | MEDIA | 2 | 2 | 0 | — | — | — | — | OBSERVING |
| Günebakış Gazetesi Trabzon | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Konya Postası Gazetesi | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Konya Yenigün Gazetesi | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Konya'nın Sesi | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Kurtalan Gazetesi | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Merhaba Gazetesi | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Patronlar Dünyası | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Samsun Kent Haber | MEDIA | 2 | 2 | 0 | — | — | — | — | OBSERVING |
| Samsun Son Haber | MEDIA | 2 | 1 | 0 | — | — | — | — | OBSERVING |
| Yüksekova Haber | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| aksam.com.tr | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| instagram.com | MEDIA | 2 | 1 | 0 | — | — | — | — | OBSERVING |
| sozcu.com.tr | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| takvim.com.tr | MEDIA | 2 | 1 | 0 | — | — | — | — | OBSERVING |
| 12punto | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| 5 Ocak Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Afyon Ana Haber | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Afyon Şehir | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Akdeniz Manşet Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Anadolu'da Bugün Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Aydın Ses Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Bengü Türk | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Bigpara | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Bjk.com.tr | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Bursa Saati | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Bursa Saati Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Bursada Bugün | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Denizli Haber | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Erhan Gülenç | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Erzurum Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Evrensel | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Fenerbahçe Spor Kulübü | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Gunebakış | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Güneysu53 | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Haber Ekspres | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Haber S Balıkesir | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Haber Vakti | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Haber3 | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Kahta Haber Postası | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Karaman Gündem | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Kars Manşet | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Küçük Saat / Adana Haberleri | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| MANŞET İZ | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Medyabar | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Mshale | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Mücadele Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| NTV Spor | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Odakgazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| SPORANKİ | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Samsun İlk Haber | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| SuperHaber | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Toros Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Trabzonhaber24 | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Transfer Haber | SECONDARY | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Ulusal Kanal | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| YENİ ADIM GAZETESİ | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Yeni Akit Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Yeni Ankara | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Yeni Çağrı Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Yenigün Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| bjk.com.tr | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| bursasaati.com.tr | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| cankiripostasi.com | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| fethiyetv.com | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| gaziantepolusum.com | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| goal.com | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| gundemebakis.com | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| gunebakis.com.tr | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| gunes.com | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| guneysu53.com | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| haber61.net | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| haber7.com | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| haberalanya.com.tr | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| habername.com | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| iha.com.tr | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| kahtahaberpostasi.com | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| karamangundem.com | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| kayserihaber.com | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| kocaelibarisgazetesi.com | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| mansetalanya.com | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| memleket.com.tr | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| mucadelegazetesi.com.tr | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| odakgazetesi.com | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| ozgurkocaeli.com.tr | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| politikam.com | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| samsungazetesi.com | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| samsunilkhaber.com.tr | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| samsunkenthaber.com.tr | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| spor.haber7.com | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| sporanki.com | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| star.com.tr | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| tv100 Haber | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| yenialanya.com | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| yeniasir.com.tr | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| yenicaggazetesi.com | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| yenihaberden.com | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| yerel-haberler.haberturk.com | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Çankırı Postası | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
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