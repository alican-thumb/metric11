# Erken Haber Kaynak Performansı

- Transfer sinyali: 27
- Resmi olaya dönüşen transfer: 3
- Yayın zamanı bulunan resmi teyit: 1/3
- İlk görülme zamanı bulunan resmi teyit: 3/3
- Ölçülen kaynak: 10 / gözlenen kaynak: 73
- Hesaplanabilir erken haber süresi: 0
- İlk görülmeye göre üst-sınır süre: 0
- X verisi bekleyen izlenen kaynak: 20
- Defterde korunan ilk iddia gözlemi: 491

## Kanal Kapsamı

- Google News: 201 haber, 30/30 başarılı sorgu.
- Telegram: 6 mesaj, 8/8 erişilebilir kanal.
- X: durum=MISSING_CREDENTIALS, gönderi=0, yapılandırılmış hesap=45.

## Kanal Ölçümü

| Kanal | Gözlem | Ölçülebilir İddia | Resmiye Dönüşen | Ort. Erken Saat | İlk Görülme Üst-Sınırı | Vekil Yanlış Alarm | Skor | Durum |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Google News / medya | 488 | 60 | 1 | — | — | %92.3 | 6.2 | PARTIAL_MEASUREMENT |
| Muhabire atıflı medya | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Telegram | 2 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| X | 0 | 0 | 0 | — | — | — | — | X_DATA_UNAVAILABLE |

## Muhabir İzleme

- Google News muhabir sorgusu erken bulgu aramasıdır; yalnız başlıkta açık muhabir atfı taşıyan transfer iddiaları `MEDIA_REPUBLICATION` gözlemi olarak yazılır.

| Muhabir / Ağ | Google Arama Bulgusu | Atıflı Gözlem | Ölçülebilir İddia | Skor Durumu |
|---|---:|---:|---:|---|
| Yağız Sabuncuoğlu | 1 | 1 | 1 | PARTIAL_MEASUREMENT |
| Ertan Süzgün | 3 | 0 | 0 | ATTRIBUTION_PENDING |
| Sports Digitale | 0 | 0 | 0 | ATTRIBUTION_PENDING |
| Yusuf Günaydın | 0 | 0 | 0 | ATTRIBUTION_PENDING |
| Ekrem Konur | 0 | 0 | 0 | ATTRIBUTION_PENDING |

## Skorlama Notu

- Resmi teyide dönüşüm, aynı oyuncu ve hedef kulüp için resmi kulüp duyurusu bulunduğunda sayılır.
- Erken haber saati yalnız hem ilk sinyal hem resmi duyuru yayın zamanı varsa kesin olarak hesaplanır; resmi yayın saati yoksa ilk görülen an ayrı üst-sınır metriğidir.
- Yanlış alarm vekili, 14 günden eski olup resmi teyide dönüşmemiş yönü belirli iddiadır; kesin yanlış bilgi hükmü değildir.

## Kaynaklar

| Kaynak | Katman | Gözlem | Ölçülebilir İddia | Resmiye Dönüşen | Ort. Erken Saat | İlk Görülme Üst-Sınırı | Vekil Yanlış Alarm | Skor | Durum |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| CNN Türk Spor | MEDIA | 10 | 2 | 1 | — | — | %0.0 | 80.0 | PARTIAL_MEASUREMENT |
| Takvim | MEDIA | 53 | 4 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Hürriyet | MEDIA | 49 | 4 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Milliyet | MEDIA | 26 | 4 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Fanatik | MEDIA | 16 | 4 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Mackolik.com | MEDIA | 3 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Diken | MEDIA | 2 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Turkmenportal.com | MEDIA | 2 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Beşiktaş Haberleri | SECONDARY | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Yağız Sabuncuoğlu | ATTRIBUTED_MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Fotomaç | MEDIA | 64 | 10 | 0 | — | — | — | — | OBSERVING |
| Sabah | MEDIA | 31 | 1 | 0 | — | — | — | — | OBSERVING |
| Aksam Spor | MEDIA | 26 | 0 | 0 | — | — | — | — | OBSERVING |
| NTVSpor | MEDIA | 21 | 3 | 0 | — | — | — | — | OBSERVING |
| Haberturk Spor | MEDIA | 17 | 1 | 0 | — | — | — | — | OBSERVING |
| FOTOMAÇ | MEDIA | 14 | 3 | 0 | — | — | — | — | OBSERVING |
| A SPOR | MEDIA | 13 | 4 | 0 | — | — | — | — | OBSERVING |
| Ajansspor | MEDIA | 9 | 3 | 0 | — | — | — | — | OBSERVING |
| GZT | MEDIA | 9 | 0 | 0 | — | — | — | — | OBSERVING |
| Son Dakika | MEDIA | 9 | 1 | 0 | — | — | — | — | OBSERVING |
| beinsports.com.tr | MEDIA | 8 | 0 | 0 | — | — | — | — | OBSERVING |
| Haberler | MEDIA | 7 | 1 | 0 | — | — | — | — | OBSERVING |
| SonDakika | MEDIA | 7 | 1 | 0 | — | — | — | — | OBSERVING |
| Anadolu Ajansı Spor | AGENCY | 6 | 0 | 0 | — | — | — | — | OBSERVING |
| Taka Gazete | MEDIA | 6 | 0 | 0 | — | — | — | — | OBSERVING |
| Habertürk | MEDIA | 5 | 1 | 0 | — | — | — | — | OBSERVING |
| Yeniçağ Gazetesi | MEDIA | 5 | 0 | 0 | — | — | — | — | OBSERVING |
| Haber 7 | MEDIA | 4 | 0 | 0 | — | — | — | — | OBSERVING |
| HaberTS | MEDIA | 4 | 0 | 0 | — | — | — | — | OBSERVING |
| sondakika.com | MEDIA | 4 | 1 | 0 | — | — | — | — | OBSERVING |
| Halk TV | MEDIA | 3 | 0 | 0 | — | — | — | — | OBSERVING |
| Mersin Haber | MEDIA | 3 | 1 | 0 | — | — | — | — | OBSERVING |
| Nefes Gazetesi | MEDIA | 3 | 0 | 0 | — | — | — | — | OBSERVING |
| Transfermarkt | MEDIA | 3 | 0 | 0 | — | — | — | — | OBSERVING |
| Cumhuriyet | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Eurohoops | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Gazete Vatan | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Haber61 | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Samsun Haber | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Sporx.com | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Yeni Şafak | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Çağdaş Kocaeli Gazetesi | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Afyon Türkeli Gazetesi | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Akdeniz Manşet Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Alanya Postası | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Anadolu Ajansı | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| BBC | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Ege Alternatif | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Ege'de Sonsöz | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Ensonhaber | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Evrensel.net | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Fotospor | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Gazete Gerçek | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Gunebakış | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Karadeniz Gazetesi | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Kocaeli Barış Gazetesi | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Konya Postası Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Konya Yeni Haber | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Mynet | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| NTV Haber | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Orta Çizgi | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| STAR - Haberler | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Sözcü Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| T24 | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Transfer Haber | SECONDARY | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Türkiye Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Vietnam.vn | MEDIA | 1 | 1 | 0 | — | — | — | — | OBSERVING |
| Yeni Asır | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| politikam.com | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Çorum Haber Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Özgür Kocaeli | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| İstanbul Ticaret Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| İz Gazete | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
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