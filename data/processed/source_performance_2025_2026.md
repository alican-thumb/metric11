# Erken Haber Kaynak Performansı

- Transfer sinyali: 66
- Resmi olaya dönüşen transfer: 8
- Yayın zamanı bulunan resmi teyit: 3/8
- İlk görülme zamanı bulunan resmi teyit: 8/8
- Ölçülen kaynak: 137 / gözlenen kaynak: 266
- Hesaplanabilir erken haber süresi: 0
- İlk görülmeye göre üst-sınır süre: 0
- X verisi bekleyen izlenen kaynak: 20
- Defterde korunan ilk iddia gözlemi: 3687

## Kanal Kapsamı

- Google News: 304 haber, 30/30 başarılı sorgu.
- Telegram: 6 mesaj, 8/8 erişilebilir kanal.
- X: durum=MISSING_CREDENTIALS, gönderi=0, yapılandırılmış hesap=45.

## Kanal Ölçümü

| Kanal | Gözlem | Ölçülebilir İddia | Resmiye Dönüşen | Ort. Erken Saat | İlk Görülme Üst-Sınırı | Vekil Yanlış Alarm | Skor | Durum |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Google News / medya | 3684 | 1193 | 1 | — | — | %99.9 | 0.1 | PARTIAL_MEASUREMENT |
| Muhabire atıflı medya | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Telegram | 2 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| X | 0 | 0 | 0 | — | — | — | — | X_DATA_UNAVAILABLE |

## Muhabir İzleme

- Google News muhabir sorgusu erken bulgu aramasıdır; yalnız başlıkta açık muhabir atfı taşıyan transfer iddiaları `MEDIA_REPUBLICATION` gözlemi olarak yazılır.

| Muhabir / Ağ | Google Arama Bulgusu | Atıflı Gözlem | Ölçülebilir İddia | Skor Durumu |
|---|---:|---:|---:|---|
| Yağız Sabuncuoğlu | 3 | 1 | 1 | PARTIAL_MEASUREMENT |
| Ertan Süzgün | 4 | 0 | 0 | ATTRIBUTION_PENDING |
| Sports Digitale | 2 | 0 | 0 | ATTRIBUTION_PENDING |
| Yusuf Günaydın | 1 | 0 | 0 | ATTRIBUTION_PENDING |
| Ekrem Konur | 5 | 0 | 0 | ATTRIBUTION_PENDING |

## Skorlama Notu

- Resmi teyide dönüşüm, aynı oyuncu ve hedef kulüp için resmi kulüp duyurusu bulunduğunda sayılır.
- Erken haber saati yalnız hem ilk sinyal hem resmi duyuru yayın zamanı varsa kesin olarak hesaplanır; resmi yayın saati yoksa ilk görülen an ayrı üst-sınır metriğidir.
- Yanlış alarm vekili, 14 günden eski olup resmi teyide dönüşmemiş yönü belirli iddiadır; kesin yanlış bilgi hükmü değildir.

## Kaynaklar

| Kaynak | Katman | Gözlem | Ölçülebilir İddia | Resmiye Dönüşen | Ort. Erken Saat | İlk Görülme Üst-Sınırı | Vekil Yanlış Alarm | Skor | Durum |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| CNN Türk Spor | MEDIA | 107 | 27 | 1 | — | — | %94.7 | 4.2 | PARTIAL_MEASUREMENT |
| Fotomaç | MEDIA | 434 | 90 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Sabah | MEDIA | 267 | 70 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Hürriyet | MEDIA | 252 | 34 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Takvim | MEDIA | 230 | 34 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Aksam Spor | MEDIA | 178 | 17 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Haberturk Spor | MEDIA | 146 | 13 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Fanatik | MEDIA | 103 | 37 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Milliyet | MEDIA | 102 | 22 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| NTVSpor | MEDIA | 93 | 20 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Sporx.com | MEDIA | 93 | 77 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Ajansspor | MEDIA | 91 | 35 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| SonDakika | MEDIA | 87 | 58 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| GZT | MEDIA | 86 | 26 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| A SPOR | MEDIA | 83 | 30 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Son Dakika | MEDIA | 73 | 48 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Taka Gazete | MEDIA | 63 | 45 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Haberler | MEDIA | 54 | 29 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Habertürk | MEDIA | 52 | 35 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Anadolu Ajansı Spor | AGENCY | 51 | 16 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Gazete Vatan | MEDIA | 36 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| sondakika.com | MEDIA | 36 | 29 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Haber 7 | MEDIA | 34 | 6 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Transfermarkt | MEDIA | 34 | 16 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| beinsports.com.tr | MEDIA | 33 | 9 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Halk TV | MEDIA | 31 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Yeniçağ Gazetesi | MEDIA | 30 | 9 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Ensonhaber | MEDIA | 29 | 19 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| FOTOMAÇ | MEDIA | 21 | 4 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| HaberTS | MEDIA | 21 | 13 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Mynet | MEDIA | 20 | 8 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| T24 | MEDIA | 19 | 7 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Sözcü Gazetesi | MEDIA | 16 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Cumhuriyet | MEDIA | 15 | 7 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| 61SAAT | MEDIA | 14 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Nefes Gazetesi | MEDIA | 14 | 5 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Mackolik.com | MEDIA | 13 | 9 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| CNN Türk | MEDIA | 12 | 6 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| gzt.com | MEDIA | 12 | 8 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| DHA / Demirören Haber Ajansı | MEDIA | 11 | 4 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Eurohoops | MEDIA | 11 | 4 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Fotospor | MEDIA | 11 | 5 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Gazete Gerçek | MEDIA | 11 | 4 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Mersin Haber | MEDIA | 11 | 4 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Sporx | MEDIA | 11 | 10 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Tıbbiye Bülteni | MEDIA | 11 | 11 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| fanatik.com.tr | MEDIA | 11 | 5 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| İhlas Haber Ajansı | MEDIA | 10 | 7 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Haber61 | MEDIA | 9 | 3 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Karadeniz Gazetesi | MEDIA | 9 | 4 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| AKŞAM | MEDIA | 8 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| birgun.net | MEDIA | 8 | 5 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| haberler.com | MEDIA | 8 | 7 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| hurriyet.com.tr | MEDIA | 8 | 5 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Anadolu Ajansı | MEDIA | 7 | 3 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Konya Yeni Haber | MEDIA | 7 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| 24 Saat Gazetesi Ankara | MEDIA | 6 | 3 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Samsun Haber | MEDIA | 6 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Saray Medya | MEDIA | 6 | 4 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| ajansspor.com | MEDIA | 6 | 4 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| fotomac.com.tr | MEDIA | 6 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| milliyet.com.tr | MEDIA | 6 | 3 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Aksiyon.com.TR | MEDIA | 5 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| MSN | MEDIA | 5 | 4 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| NTV Haber | MEDIA | 5 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| sporx.com | MEDIA | 5 | 5 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| takvim.com.tr | MEDIA | 5 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| transfermarkt.com.tr | MEDIA | 5 | 4 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Çağdaş Kocaeli Gazetesi | MEDIA | 5 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| İlkses Gazetesi | MEDIA | 5 | 3 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Evrensel.net | MEDIA | 4 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| IHA | MEDIA | 4 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Internet Haber | MEDIA | 4 | 4 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Orta Çizgi | MEDIA | 4 | 3 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Yeni Alanya | MEDIA | 4 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| bolgegundemi.com | MEDIA | 4 | 4 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| mynet.com | MEDIA | 4 | 3 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| ntvspor.net | MEDIA | 4 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| A Haber | MEDIA | 3 | 3 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Bundle | MEDIA | 3 | 3 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Duhuliye | MEDIA | 3 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Erzurum Gazetesi | MEDIA | 3 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Gözlem Gazetesi | MEDIA | 3 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Odatv | MEDIA | 3 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Rizedeyiz | MEDIA | 3 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Yeni Asır | MEDIA | 3 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| İstanbul Ticaret Gazetesi | MEDIA | 3 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| İstiklal Gazetesi | MEDIA | 3 | 3 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| 2 Mart Gazetesi | MEDIA | 2 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| 24saatgazetesi.com | MEDIA | 2 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Başka Gazete | MEDIA | 2 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| CUMHA Cumhur Haber Ajansı | MEDIA | 2 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Diken | MEDIA | 2 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Ege Alternatif | MEDIA | 2 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Habername.com | MEDIA | 2 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Kars Manşet | MEDIA | 2 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| TGRT Haber | MEDIA | 2 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Turkmenportal.com | MEDIA | 2 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| ensonhaber.com | MEDIA | 2 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| AS TV | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Afyon Haber | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Afyon Türkeli Gazetesi | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Antalya Haber - Kanal V | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| BBC | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Beşiktaş Haberleri | SECONDARY | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Bursa Hakimiyet | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Canlı Gaste | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Gaziantep Haber | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Gaziantep Söz | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Gündem Beşiktaş | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Haber 1 | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Haber Aktüel | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Haber Global | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Haber Kıbrıs | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Hentbolhaber.Net | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Hunat TV | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Investing.com Türkiye | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Kocaeli Barış Gazetesi | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Kocaeli Kent Gazetesi | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Malta Haber | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Memleket | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| N Gazete | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| NationalTurk | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Olay53.com | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Samsun Kent Haber | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| TV5 Haber | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Vietnam.vn | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Webaslan | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Yayla Haber | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Yağız Sabuncuoğlu | ATTRIBUTED_MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Yeşil Afşin Gazetesi | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| alanyaturk.com | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| astv.com.tr | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| erzurumgazetesi.com.tr | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| iha.com.tr | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| radikal.com.tr | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| tibbiyebulteni.com | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Yeni Şafak | MEDIA | 21 | 0 | 0 | — | — | — | — | OBSERVING |
| A Spor | MEDIA | 13 | 5 | 0 | — | — | — | — | OBSERVING |
| Alanya Postası | MEDIA | 9 | 0 | 0 | — | — | — | — | OBSERVING |
| Türkiye Gazetesi | MEDIA | 9 | 0 | 0 | — | — | — | — | OBSERVING |
| Goal.com | MEDIA | 7 | 1 | 0 | — | — | — | — | OBSERVING |
| STAR - Haberler | MEDIA | 7 | 2 | 0 | — | — | — | — | OBSERVING |
| sabah.com.tr | MEDIA | 6 | 4 | 0 | — | — | — | — | OBSERVING |
| Samsun Gazetesi | MEDIA | 5 | 2 | 0 | — | — | — | — | OBSERVING |
| yenisafak.com | MEDIA | 5 | 0 | 0 | — | — | — | — | OBSERVING |
| Özgür Kocaeli | MEDIA | 5 | 1 | 0 | — | — | — | — | OBSERVING |
| Gunebakış | MEDIA | 4 | 0 | 0 | — | — | — | — | OBSERVING |
| samsungazetesi.com | MEDIA | 4 | 2 | 0 | — | — | — | — | OBSERVING |
| Bugün Kocaeli Gazetesi | MEDIA | 3 | 0 | 0 | — | — | — | — | OBSERVING |
| gazetevatan.com | MEDIA | 3 | 0 | 0 | — | — | — | — | OBSERVING |
| haberturk.com | MEDIA | 3 | 3 | 0 | — | — | — | — | OBSERVING |
| samsunhaber.com | MEDIA | 3 | 0 | 0 | — | — | — | — | OBSERVING |
| Anadolu'da Bugün | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Ege'de Sonsöz | MEDIA | 2 | 1 | 0 | — | — | — | — | OBSERVING |
| Gazete Arena | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| KARAR | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Konya Postası Gazetesi | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Konya Yenigün | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Konya Yenigün Gazetesi | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Konya'nın Sesi | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Manşet Haber | MEDIA | 2 | 2 | 0 | — | — | — | — | OBSERVING |
| Merhaba Gazetesi | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Patronlar Dünyası | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Yeni Akit Gazetesi | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Yeni Safak English | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Yüksekova Haber | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| gazetegercek.com.tr | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| mackolik.com | MEDIA | 2 | 2 | 0 | — | — | — | — | OBSERVING |
| nefes.com.tr | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| sozcu.com.tr | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| t24.com.tr | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| tv100 Haber | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| yenicaggazetesi.com | MEDIA | 2 | 1 | 0 | — | — | — | — | OBSERVING |
| İz Gazete | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Afyon Şehir | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Akdeniz Manşet Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Akdenizmanset | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Amida Haber | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Anadolu'da Bugün Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Antalya Haberal | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Ardahan Haber | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Artı Gerçek | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Bursa Saati | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Demokrat Kocaeli | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Fenerbahçe Spor Kulübü | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Gaziantep Oluşum Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Gerçek Gündem | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Gerçek İzmir | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Giresun İleri Gazetesi | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Haber Ege | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Haber Ekspres | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Haber S Balıkesir | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Haber Vakti | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Haber3 | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Haberton | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Halk 54 | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| KAYSERİ YEREL HABER | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Kayseri Anadolu Haber | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Kayseri Gündem | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Kayseri Olay Haber | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Kocaeli Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Konhaber | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Kurtalan Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Medya Siyah Beyaz | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| NTV Spor | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Odak Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Odakgazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Rize Takip | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| SES15 | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Samsun Son Haber | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Sanayi Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Son Dakika Samsun Haberleri | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| SuperHaber | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Trabzonhaber24 | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Transfer Haber | SECONDARY | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Ulusal Kanal | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Yeni Mesaj | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Yeni Çağrı Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Yenigün Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Yozgat Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| alanyapostasi.com.tr | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| amidahaber.com | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| baskagazete.com | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| bugunkocaeli.com.tr | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| bundle.app | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| bursasaati.com.tr | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| cagdaskocaeli.com.tr | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| cnnturk.com | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| cumhuriyet.com.tr | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| egedesonsoz.com | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| en.yenisafak.com | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| gazetearena.com | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| giresunileri.com | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| gozlemgazetesi.com | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| gunebakis.com.tr | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| haberege.com.tr | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| halktv.com.tr | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| ilkses.com.tr | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| istikbalgazetesi.com | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| karar.com | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| kayserigundem.com.tr | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| kayserihaber.com.tr | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| kayseriolay.com | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| kayseriyerelhaber.com | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| kocaeligazetesi.com.tr | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| medyasiyahbeyaz.com | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| odakgazetesi.com | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| politikam.com | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| rizeninsesi.net | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| rizetakip.com | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| sanayigazetesi.com.tr | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| saraymedya.com | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| ses15.com.tr | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| sivas360.com | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| star.com.tr | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| turkiyegazetesi.com.tr | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| tv100.com | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
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