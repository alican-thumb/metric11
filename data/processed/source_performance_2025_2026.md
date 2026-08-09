# Erken Haber Kaynak Performansı

- Transfer sinyali: 65
- Resmi olaya dönüşen transfer: 8
- Yayın zamanı bulunan resmi teyit: 3/8
- İlk görülme zamanı bulunan resmi teyit: 8/8
- Ölçülen kaynak: 115 / gözlenen kaynak: 237
- Hesaplanabilir erken haber süresi: 0
- İlk görülmeye göre üst-sınır süre: 0
- X verisi bekleyen izlenen kaynak: 20
- Defterde korunan ilk iddia gözlemi: 3385

## Kanal Kapsamı

- Google News: 310 haber, 30/30 başarılı sorgu.
- Telegram: 6 mesaj, 8/8 erişilebilir kanal.
- X: durum=MISSING_CREDENTIALS, gönderi=0, yapılandırılmış hesap=45.

## Kanal Ölçümü

| Kanal | Gözlem | Ölçülebilir İddia | Resmiye Dönüşen | Ort. Erken Saat | İlk Görülme Üst-Sınırı | Vekil Yanlış Alarm | Skor | Durum |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Google News / medya | 3382 | 1075 | 1 | — | — | %99.9 | 0.1 | PARTIAL_MEASUREMENT |
| Muhabire atıflı medya | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Telegram | 2 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| X | 0 | 0 | 0 | — | — | — | — | X_DATA_UNAVAILABLE |

## Muhabir İzleme

- Google News muhabir sorgusu erken bulgu aramasıdır; yalnız başlıkta açık muhabir atfı taşıyan transfer iddiaları `MEDIA_REPUBLICATION` gözlemi olarak yazılır.

| Muhabir / Ağ | Google Arama Bulgusu | Atıflı Gözlem | Ölçülebilir İddia | Skor Durumu |
|---|---:|---:|---:|---|
| Yağız Sabuncuoğlu | 4 | 1 | 1 | PARTIAL_MEASUREMENT |
| Ertan Süzgün | 2 | 0 | 0 | ATTRIBUTION_PENDING |
| Sports Digitale | 2 | 0 | 0 | ATTRIBUTION_PENDING |
| Yusuf Günaydın | 0 | 0 | 0 | ATTRIBUTION_PENDING |
| Ekrem Konur | 5 | 0 | 0 | ATTRIBUTION_PENDING |

## Skorlama Notu

- Resmi teyide dönüşüm, aynı oyuncu ve hedef kulüp için resmi kulüp duyurusu bulunduğunda sayılır.
- Erken haber saati yalnız hem ilk sinyal hem resmi duyuru yayın zamanı varsa kesin olarak hesaplanır; resmi yayın saati yoksa ilk görülen an ayrı üst-sınır metriğidir.
- Yanlış alarm vekili, 14 günden eski olup resmi teyide dönüşmemiş yönü belirli iddiadır; kesin yanlış bilgi hükmü değildir.

## Kaynaklar

| Kaynak | Katman | Gözlem | Ölçülebilir İddia | Resmiye Dönüşen | Ort. Erken Saat | İlk Görülme Üst-Sınırı | Vekil Yanlış Alarm | Skor | Durum |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| CNN Türk Spor | MEDIA | 97 | 25 | 1 | — | — | %94.1 | 4.7 | PARTIAL_MEASUREMENT |
| Fotomaç | MEDIA | 405 | 86 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Sabah | MEDIA | 255 | 65 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Hürriyet | MEDIA | 238 | 31 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Takvim | MEDIA | 208 | 31 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Aksam Spor | MEDIA | 170 | 16 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Haberturk Spor | MEDIA | 132 | 12 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Fanatik | MEDIA | 92 | 34 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Milliyet | MEDIA | 92 | 19 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| NTVSpor | MEDIA | 91 | 20 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Sporx.com | MEDIA | 88 | 72 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| SonDakika | MEDIA | 86 | 57 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| A SPOR | MEDIA | 83 | 30 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| GZT | MEDIA | 82 | 25 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Ajansspor | MEDIA | 80 | 32 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Son Dakika | MEDIA | 68 | 43 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Taka Gazete | MEDIA | 61 | 43 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Haberler | MEDIA | 50 | 27 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Habertürk | MEDIA | 46 | 30 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Anadolu Ajansı Spor | AGENCY | 42 | 12 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Gazete Vatan | MEDIA | 33 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Haber 7 | MEDIA | 33 | 6 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| beinsports.com.tr | MEDIA | 33 | 9 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| sondakika.com | MEDIA | 31 | 24 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Transfermarkt | MEDIA | 30 | 12 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Halk TV | MEDIA | 29 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Yeniçağ Gazetesi | MEDIA | 29 | 9 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Ensonhaber | MEDIA | 26 | 17 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| FOTOMAÇ | MEDIA | 21 | 4 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| HaberTS | MEDIA | 20 | 13 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Mynet | MEDIA | 18 | 8 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| T24 | MEDIA | 18 | 7 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| 61SAAT | MEDIA | 14 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Nefes Gazetesi | MEDIA | 13 | 5 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Sözcü Gazetesi | MEDIA | 13 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Cumhuriyet | MEDIA | 12 | 5 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| CNN Türk | MEDIA | 11 | 5 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Eurohoops | MEDIA | 11 | 4 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Fotospor | MEDIA | 11 | 5 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Gazete Gerçek | MEDIA | 11 | 4 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Mackolik.com | MEDIA | 11 | 7 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Mersin Haber | MEDIA | 11 | 4 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Sporx | MEDIA | 11 | 10 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Tıbbiye Bülteni | MEDIA | 11 | 11 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| fanatik.com.tr | MEDIA | 10 | 5 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| İhlas Haber Ajansı | MEDIA | 10 | 7 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Karadeniz Gazetesi | MEDIA | 9 | 4 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| DHA / Demirören Haber Ajansı | MEDIA | 8 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Haber61 | MEDIA | 8 | 3 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| birgun.net | MEDIA | 8 | 5 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| AKŞAM | MEDIA | 7 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Konya Yeni Haber | MEDIA | 7 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| hurriyet.com.tr | MEDIA | 7 | 4 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Anadolu Ajansı | MEDIA | 6 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Samsun Haber | MEDIA | 6 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| haberler.com | MEDIA | 6 | 6 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| 24 Saat Gazetesi Ankara | MEDIA | 5 | 3 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Aksiyon.com.TR | MEDIA | 5 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| MSN | MEDIA | 5 | 4 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| NTV Haber | MEDIA | 5 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| transfermarkt.com.tr | MEDIA | 5 | 4 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Çağdaş Kocaeli Gazetesi | MEDIA | 5 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Evrensel.net | MEDIA | 4 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| IHA | MEDIA | 4 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Internet Haber | MEDIA | 4 | 4 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Orta Çizgi | MEDIA | 4 | 3 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Saray Medya | MEDIA | 4 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Yeni Alanya | MEDIA | 4 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| bolgegundemi.com | MEDIA | 4 | 4 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| İlkses Gazetesi | MEDIA | 4 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| A Haber | MEDIA | 3 | 3 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Duhuliye | MEDIA | 3 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Gözlem Gazetesi | MEDIA | 3 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Odatv | MEDIA | 3 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| İstanbul Ticaret Gazetesi | MEDIA | 3 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| İstiklal Gazetesi | MEDIA | 3 | 3 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| 2 Mart Gazetesi | MEDIA | 2 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Başka Gazete | MEDIA | 2 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Bundle | MEDIA | 2 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| CUMHA Cumhur Haber Ajansı | MEDIA | 2 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Diken | MEDIA | 2 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Ege Alternatif | MEDIA | 2 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Habername.com | MEDIA | 2 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| TGRT Haber | MEDIA | 2 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Turkmenportal.com | MEDIA | 2 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Yeni Asır | MEDIA | 2 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Afyon Haber | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Afyon Türkeli Gazetesi | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Antalya Haber - Kanal V | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| BBC | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
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
| Samsun Kent Haber | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Vietnam.vn | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Webaslan | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Yayla Haber | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Yağız Sabuncuoğlu | ATTRIBUTED_MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Yeşil Afşin Gazetesi | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| alanyaturk.com | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| radikal.com.tr | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Yeni Şafak | MEDIA | 19 | 0 | 0 | — | — | — | — | OBSERVING |
| gzt.com | MEDIA | 10 | 7 | 0 | — | — | — | — | OBSERVING |
| A Spor | MEDIA | 9 | 3 | 0 | — | — | — | — | OBSERVING |
| Alanya Postası | MEDIA | 9 | 0 | 0 | — | — | — | — | OBSERVING |
| Türkiye Gazetesi | MEDIA | 8 | 0 | 0 | — | — | — | — | OBSERVING |
| Goal.com | MEDIA | 7 | 1 | 0 | — | — | — | — | OBSERVING |
| STAR - Haberler | MEDIA | 6 | 1 | 0 | — | — | — | — | OBSERVING |
| Gunebakış | MEDIA | 4 | 0 | 0 | — | — | — | — | OBSERVING |
| fotomac.com.tr | MEDIA | 4 | 2 | 0 | — | — | — | — | OBSERVING |
| mynet.com | MEDIA | 4 | 3 | 0 | — | — | — | — | OBSERVING |
| sabah.com.tr | MEDIA | 4 | 2 | 0 | — | — | — | — | OBSERVING |
| sporx.com | MEDIA | 4 | 4 | 0 | — | — | — | — | OBSERVING |
| Özgür Kocaeli | MEDIA | 4 | 0 | 0 | — | — | — | — | OBSERVING |
| Bugün Kocaeli Gazetesi | MEDIA | 3 | 0 | 0 | — | — | — | — | OBSERVING |
| Erzurum Gazetesi | MEDIA | 3 | 2 | 0 | — | — | — | — | OBSERVING |
| Rizedeyiz | MEDIA | 3 | 2 | 0 | — | — | — | — | OBSERVING |
| Samsun Gazetesi | MEDIA | 3 | 0 | 0 | — | — | — | — | OBSERVING |
| samsunhaber.com | MEDIA | 3 | 0 | 0 | — | — | — | — | OBSERVING |
| yenisafak.com | MEDIA | 3 | 0 | 0 | — | — | — | — | OBSERVING |
| 24saatgazetesi.com | MEDIA | 2 | 2 | 0 | — | — | — | — | OBSERVING |
| Anadolu'da Bugün | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Gazete Arena | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Kars Manşet | MEDIA | 2 | 1 | 0 | — | — | — | — | OBSERVING |
| Konya Postası Gazetesi | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Konya Yenigün | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Konya Yenigün Gazetesi | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Konya'nın Sesi | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Merhaba Gazetesi | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Patronlar Dünyası | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Yeni Akit Gazetesi | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Yeni Safak English | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Yüksekova Haber | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| ajansspor.com | MEDIA | 2 | 1 | 0 | — | — | — | — | OBSERVING |
| gazetegercek.com.tr | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| gazetevatan.com | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| milliyet.com.tr | MEDIA | 2 | 1 | 0 | — | — | — | — | OBSERVING |
| nefes.com.tr | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| ntvspor.net | MEDIA | 2 | 2 | 0 | — | — | — | — | OBSERVING |
| samsungazetesi.com | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| t24.com.tr | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| takvim.com.tr | MEDIA | 2 | 1 | 0 | — | — | — | — | OBSERVING |
| tv100 Haber | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| İz Gazete | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| AS TV | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Afyon Şehir | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Akdeniz Manşet Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Amida Haber | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Anadolu'da Bugün Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Antalya Haberal | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Ardahan Haber | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Artı Gerçek | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Ege'de Sonsöz | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Fenerbahçe Spor Kulübü | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Gaziantep Haber | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Gaziantep Oluşum Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Gerçek Gündem | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Gerçek İzmir | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Giresun İleri Gazetesi | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Haber Ekspres | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Haber Global | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Haber S Balıkesir | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Haber Vakti | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Haber3 | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Haberton | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Halk 54 | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| KARAR | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Kayseri Anadolu Haber | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Kayseri Gündem | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Kayseri Olay Haber | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Kocaeli Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Kurtalan Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| N Gazete | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| NTV Spor | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Rize Takip | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Samsun Son Haber | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Son Dakika Samsun Haberleri | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| SuperHaber | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| TV5 Haber | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Trabzonhaber24 | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Transfer Haber | SECONDARY | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Ulusal Kanal | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Yeni Mesaj | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Yeni Çağrı Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Yenigün Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Yozgat Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| alanyapostasi.com.tr | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| amidahaber.com | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| astv.com.tr | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| baskagazete.com | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| bugunkocaeli.com.tr | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| cnnturk.com | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| cumhuriyet.com.tr | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| en.yenisafak.com | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| ensonhaber.com | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| erzurumgazetesi.com.tr | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| gazetearena.com | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| giresunileri.com | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| gozlemgazetesi.com | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| gunebakis.com.tr | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| haberturk.com | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| iha.com.tr | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| istikbalgazetesi.com | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| kayserihaber.com.tr | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| kayseriolay.com | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| kocaeligazetesi.com.tr | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| politikam.com | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| rizeninsesi.net | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| rizetakip.com | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| saraymedya.com | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| sivas360.com | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| sozcu.com.tr | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| tibbiyebulteni.com | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| tv100.com | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| yenicaggazetesi.com | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| yenihaberden.com | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| yerel-haberler.haberturk.com | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| yozgatgazetesi.com | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Çorum Haber Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Çorum Hakimiyet | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| İnternet Haber | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| İstanbul Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| İstikbal Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
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