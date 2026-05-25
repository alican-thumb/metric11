# Erken Haber Kaynak Performansı

- Transfer sinyali: 53
- Resmi olaya dönüşen transfer: 3
- Yayın zamanı bulunan resmi teyit: 1/3
- İlk görülme zamanı bulunan resmi teyit: 3/3
- Ölçülen kaynak: 7 / gözlenen kaynak: 26
- Hesaplanabilir erken haber süresi: 0
- İlk görülmeye göre üst-sınır süre: 0
- X verisi bekleyen izlenen kaynak: 13
- Defterde korunan ilk iddia gözlemi: 49

## Kanal Kapsamı

- Google News: 378 haber, 26/26 başarılı sorgu.
- Telegram: 48 mesaj, 6/6 erişilebilir kanal.
- X: durum=MISSING_CREDENTIALS, gönderi=0, yapılandırılmış hesap=45.

## Kanal Ölçümü

| Kanal | Gözlem | Ölçülebilir İddia | Resmiye Dönüşen | Ort. Erken Saat | İlk Görülme Üst-Sınırı | Vekil Yanlış Alarm | Skor | Durum |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Google News / medya | 46 | 7 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Muhabire atıflı medya | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Telegram | 2 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| X | 0 | 0 | 0 | — | — | — | — | X_DATA_UNAVAILABLE |

## Muhabir İzleme

- Google News muhabir sorgusu erken bulgu aramasıdır; yalnız başlıkta açık muhabir atfı taşıyan transfer iddiaları `MEDIA_REPUBLICATION` gözlemi olarak yazılır.

| Muhabir / Ağ | Google Arama Bulgusu | Atıflı Gözlem | Ölçülebilir İddia | Skor Durumu |
|---|---:|---:|---:|---|
| Yağız Sabuncuoğlu | 15 | 1 | 1 | PARTIAL_MEASUREMENT |
| Ertan Süzgün | 15 | 0 | 0 | ATTRIBUTION_PENDING |
| Sports Digitale | 15 | 0 | 0 | ATTRIBUTION_PENDING |
| Yusuf Günaydın | 15 | 0 | 0 | ATTRIBUTION_PENDING |
| Ekrem Konur | 15 | 0 | 0 | ATTRIBUTION_PENDING |

## Skorlama Notu

- Resmi teyide dönüşüm, aynı oyuncu ve hedef kulüp için resmi kulüp duyurusu bulunduğunda sayılır.
- Erken haber saati yalnız hem ilk sinyal hem resmi duyuru yayın zamanı varsa kesin olarak hesaplanır; resmi yayın saati yoksa ilk görülen an ayrı üst-sınır metriğidir.
- Yanlış alarm vekili, 14 günden eski olup resmi teyide dönüşmemiş yönü belirli iddiadır; kesin yanlış bilgi hükmü değildir.

## Kaynaklar

| Kaynak | Katman | Gözlem | Ölçülebilir İddia | Resmiye Dönüşen | Ort. Erken Saat | İlk Görülme Üst-Sınırı | Vekil Yanlış Alarm | Skor | Durum |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Hürriyet | MEDIA | 5 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Fanatik | MEDIA | 3 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Mackolik.com | MEDIA | 3 | 2 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Milliyet | MEDIA | 3 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Beşiktaş Haberleri | SECONDARY | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Diken | MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Yağız Sabuncuoğlu | ATTRIBUTED_MEDIA | 1 | 1 | 0 | — | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Takvim Spor | MEDIA | 9 | 0 | 0 | — | — | — | — | OBSERVING |
| Hürriyet Spor | MEDIA | 3 | 0 | 0 | — | — | — | — | OBSERVING |
| beinsports.com.tr | MEDIA | 3 | 0 | 0 | — | — | — | — | OBSERVING |
| GZT | MEDIA | 2 | 0 | 0 | — | — | — | — | OBSERVING |
| Ajansspor | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Anadolu Ajansı | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Cumhuriyet | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Habertürk | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Halk TV | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Konya Yeni Haber | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| NTVSpor | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Nefes Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| STAR - Haberler | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Sporx.com | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Takvim | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Transfer Haber | SECONDARY | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Türkiye Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| Yeniçağ Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| politikam.com | MEDIA | 1 | 0 | 0 | — | — | — | — | OBSERVING |
| @AmputeFutbol | SECONDARY | 0 | 0 | 0 | — | — | — | — | X_DATA_UNAVAILABLE |
| @EkremKonur | SECONDARY | 0 | 0 | 0 | — | — | — | — | X_DATA_UNAVAILABLE |
| @FabrizioRomano | SECONDARY | 0 | 0 | 0 | — | — | — | — | X_DATA_UNAVAILABLE |
| @GercekBJK | SECONDARY | 0 | 0 | 0 | — | — | — | — | X_DATA_UNAVAILABLE |
| @GizemKaya__ | SECONDARY | 0 | 0 | 0 | — | — | — | — | X_DATA_UNAVAILABLE |
| @KaraKartalBlog | SECONDARY | 0 | 0 | 0 | — | — | — | — | X_DATA_UNAVAILABLE |
| @SportsDigitale | SECONDARY | 0 | 0 | 0 | — | — | — | — | X_DATA_UNAVAILABLE |
| @WebdikBesiktas | SECONDARY | 0 | 0 | 0 | — | — | — | — | X_DATA_UNAVAILABLE |
| @YakinTakip | SECONDARY | 0 | 0 | 0 | — | — | — | — | X_DATA_UNAVAILABLE |
| @ertansuzgun | SECONDARY | 0 | 0 | 0 | — | — | — | — | X_DATA_UNAVAILABLE |
| @transfermarkt_TR | SECONDARY | 0 | 0 | 0 | — | — | — | — | X_DATA_UNAVAILABLE |
| @yagosabuncuoglu | SECONDARY | 0 | 0 | 0 | — | — | — | — | X_DATA_UNAVAILABLE |
| @yusufgunaydn | SECONDARY | 0 | 0 | 0 | — | — | — | — | X_DATA_UNAVAILABLE |
| Fenerbahçe Haberleri | SECONDARY | 0 | 0 | 0 | — | — | — | — | NO_TRANSFER_CLAIMS |
| Galatasaray Haberleri | SECONDARY | 0 | 0 | 0 | — | — | — | — | NO_TRANSFER_CLAIMS |
| Süper Lig Son Dakika | SECONDARY | 0 | 0 | 0 | — | — | — | — | NO_TRANSFER_CLAIMS |
| Trabzonspor Haberleri | SECONDARY | 0 | 0 | 0 | — | — | — | — | NO_TRANSFER_CLAIMS |