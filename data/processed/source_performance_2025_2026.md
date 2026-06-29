# Erken Haber Kaynak Performansı

- Transfer sinyali: 38
- Resmi olaya dönüşen transfer: 3
- Yayın zamanı bulunan resmi teyit: 1/3
- İlk görülme zamanı bulunan resmi teyit: 3/3
- Ölçülen kaynak: 41 / gözlenen kaynak: 113
- Hesaplanabilir erken haber süresi: 0
- İlk görülmeye göre üst-sınır süre: 0
- X verisi bekleyen izlenen kaynak: 20
- Defterde korunan ilk iddia gözlemi: 1179

## Kanal Kapsamı

- Google News: 221 haber, 30/30 başarılı sorgu.
- Telegram: 6 mesaj, 8/8 erişilebilir kanal.
- X: durum=MISSING_CREDENTIALS, gönderi=0, yapılandırılmış hesap=45.

## Kanal Ölçümü

| Kanal | Gözlem | Ölçülebilir İddia | Resmiye Dönüşen | Ort. Erken Saat | İlk Görülme Üst-Sınırı | Vekil Yanlış Alarm | Skor | Durum |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Google News / medya | 1176 | 263 | 1 | — | — | %99.0 | 0.8 | PARTIAL_MEASUREMENT |
| Muhabire atıflı medya | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Telegram | 2 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| X | 0 | 0 | 0 | — | — | — | — | X_DATA_UNAVAILABLE |

## Muhabir İzleme

- Google News muhabir sorgusu erken bulgu aramasıdır; yalnız başlıkta açık muhabir atfı taşıyan transfer iddiaları `MEDIA_REPUBLICATION` gözlemi olarak yazılır.

| Muhabir / Ağ | Google Arama Bulgusu | Atıflı Gözlem | Ölçülebilir İddia | Skor Durumu |
|---|---:|---:|---:|---|
| Yağız Sabuncuoğlu | 0 | 1 | 1 | PARTIAL_MEASUREMENT |
| Ertan Süzgün | 0 | 0 | 0 | ATTRIBUTION_PENDING |
| Sports Digitale | 0 | 0 | 0 | ATTRIBUTION_PENDING |
| Yusuf Günaydın | 1 | 0 | 0 | ATTRIBUTION_PENDING |
| Ekrem Konur | 0 | 0 | 0 | ATTRIBUTION_PENDING |

## Skorlama Notu

- Resmi teyide dönüşüm, aynı oyuncu ve hedef kulüp için resmi kulüp duyurusu bulunduğunda sayılır.
- Erken haber saati yalnız hem ilk sinyal hem resmi duyuru yayın zamanı varsa kesin olarak hesaplanır; resmi yayın saati yoksa ilk görülen an ayrı üst-sınır metriğidir.
- Yanlış alarm vekili, 14 günden eski olup resmi teyide dönüşmemiş yönü belirli iddiadır; kesin yanlış bilgi hükmü değildir.

## Kaynaklar

| Kaynak | Katman | Gözlem | Ölçülebilir İddia | Resmiye Dönüşen | Ort. Erken Saat | İlk Görülme Üst-Sınırı | Vekil Yanlış Alarm | Skor | Durum |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| CNN Türk Spor | MEDIA | 35 | 8 | 1 | — | — | %66.7 | 26.7 | PARTIAL_MEASUREMENT |
| Fotomaç | MEDIA | 155 | 27 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Hürriyet | MEDIA | 92 | 6 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Sabah | MEDIA | 88 | 12 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Takvim | MEDIA | 70 | 5 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Aksam Spor | MEDIA | 56 | 3 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Haberturk Spor | MEDIA | 44 | 3 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| A SPOR | MEDIA | 42 | 9 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Milliyet | MEDIA | 42 | 6 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| NTVSpor | MEDIA | 36 | 6 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Fanatik | MEDIA | 33 | 11 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Taka Gazete | MEDIA | 30 | 21 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Son Dakika | MEDIA | 28 | 11 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Ajansspor | MEDIA | 25 | 8 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Sporx.com | MEDIA | 24 | 16 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| SonDakika | MEDIA | 23 | 8 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| FOTOMAÇ | MEDIA | 21 | 4 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Habertürk | MEDIA | 18 | 7 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| beinsports.com.tr | MEDIA | 17 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Haberler | MEDIA | 16 | 5 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Yeniçağ Gazetesi | MEDIA | 16 | 5 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| sondakika.com | MEDIA | 11 | 6 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Sporx | MEDIA | 7 | 6 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Transfermarkt | MEDIA | 7 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Mackolik.com | MEDIA | 6 | 4 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Mersin Haber | MEDIA | 6 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Gazete Gerçek | MEDIA | 4 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Karadeniz Gazetesi | MEDIA | 4 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Orta Çizgi | MEDIA | 3 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Yeni Alanya | MEDIA | 3 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Diken | MEDIA | 2 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Evrensel.net | MEDIA | 2 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Turkmenportal.com | MEDIA | 2 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| A Haber | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Afyon Türkeli Gazetesi | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| BBC | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Beşiktaş Haberleri | SECONDARY | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Kocaeli Barış Gazetesi | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Vietnam.vn | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Yağız Sabuncuoğlu | ATTRIBUTED_MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| radikal.com.tr | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| GZT | MEDIA | 26 | 1 | 0 | — | — | — | — | OBSERVING |
| Anadolu Ajansı Spor | AGENCY | 14 | 2 | 0 | — | — | — | — | OBSERVING |
| HaberTS | MEDIA | 13 | 8 | 0 | — | — | — | — | OBSERVING |
| Gazete Vatan | MEDIA | 11 | 1 | 0 | — | — | — | — | OBSERVING |
| Haber 7 | MEDIA | 11 | 0 | 0 | — | — | — | — | OBSERVING |
| Halk TV | MEDIA | 8 | 1 | 0 | — | — | — | — | OBSERVING |
| Eurohoops | MEDIA | 7 | 3 | 0 | — | — | — | — | OBSERVING |
| CNN Türk | MEDIA | 5 | 1 | 0 | — | — | — | — | OBSERVING |
| Haber61 | MEDIA | 5 | 2 | 0 | — | — | — | — | OBSERVING |
| Fotospor | MEDIA | 4 | 2 | 0 | — | — | — | — | OBSERVING |
| Konya Yeni Haber | MEDIA | 4 | 1 | 0 | — | — | — | — | OBSERVING |
| Mynet | MEDIA | 4 | 1 | 0 | — | — | — | — | OBSERVING |
| Türkiye Gazetesi | MEDIA | 4 | 0 | 0 | — | — | — | — | OBSERVING |
| İlkses Gazetesi | MEDIA | 4 | 2 | 0 | — | — | — | — | OBSERVING |
| 61SAAT | MEDIA | 3 | 1 | 0 | — | — | — | — | OBSERVING |
| NTV Haber | MEDIA | 3 | 1 | 0 | — | — | — | — | OBSERVING |
| Nefes Gazetesi | MEDIA | 3 | 0 | 0 | — | — | — | — | OBSERVING |
| STAR - Haberler | MEDIA | 3 | 0 | 0 | — | — | — | — | OBSERVING |
| T24 | MEDIA | 3 | 1 | 0 | — | — | — | — | OBSERVING |
| Yeni Şafak | MEDIA | 3 | 0 | 0 | — | — | — | — | OBSERVING |
| Çağdaş Kocaeli Gazetesi | MEDIA | 3 | 1 | 0 | — | — | — | — | OBSERVING |
| İstanbul Ticaret Gazetesi | MEDIA | 3 | 2 | 0 | — | — | — | — | OBSERVING |
| Alanya Postası | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Anadolu'da Bugün | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Cumhuriyet | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Ensonhaber | MEDIA | 2 | 1 | 0 | — | — | — | — | OBSERVING |
| Goal.com | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| IHA | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Samsun Haber | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| fanatik.com.tr | MEDIA | 2 | 1 | 0 | — | — | — | — | OBSERVING |
| İz Gazete | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| 2 Mart Gazetesi | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| AKŞAM | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Akdeniz Manşet Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Anadolu Ajansı | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Anadolu'da Bugün Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Ege Alternatif | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Ege'de Sonsöz | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Fenerbahçe Spor Kulübü | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Gaziantep Oluşum Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Gerçek İzmir | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Gunebakış | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Gözlem Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Haber Ekspres | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Haber Kıbrıs | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Hentbolhaber.Net | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Internet Haber | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Konya Postası Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| MSN | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Malta Haber | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Memleket | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Merhaba Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Odatv | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Patronlar Dünyası | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Samsun Son Haber | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| SuperHaber | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Sözcü Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| TGRT Haber | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Transfer Haber | SECONDARY | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Tıbbiye Bülteni | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Ulusal Kanal | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Yeni Akit Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Yeni Asır | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Yeni Çağrı Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Yenigün Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| alanyaturk.com | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| birgun.net | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| bolgegundemi.com | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| haberler.com | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| politikam.com | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Çorum Haber Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Özgür Kocaeli | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
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