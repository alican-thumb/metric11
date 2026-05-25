# Erken Haber Kaynak Performansı

- Transfer sinyali: 54
- Resmi olaya dönüşen transfer: 3
- Yayın zamanı bulunan resmi teyit: 0/3
- Ölçülen kaynak: 2 / gözlenen kaynak: 25
- Hesaplanabilir erken haber süresi: 0
- X verisi bekleyen izlenen kaynak: 13
- Defterde korunan ilk iddia gözlemi: 46

## Kanal Kapsamı

- Google News: 381 haber, 26/26 başarılı sorgu.
- Telegram: 48 mesaj, 6/6 erişilebilir kanal.
- X: durum=MISSING_CREDENTIALS, gönderi=0, yapılandırılmış hesap=45.

## Kanal Ölçümü

| Kanal | Gözlem | Ölçülebilir İddia | Resmiye Dönüşen | Ort. Erken Saat | Vekil Yanlış Alarm | Skor | Durum |
|---|---:|---:|---:|---:|---:|---:|---|
| Google News / medya | 44 | 2 | 0 | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Telegram | 2 | 1 | 0 | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| X | 0 | 0 | 0 | — | — | — | X_DATA_UNAVAILABLE |

## Muhabir İzleme

- Google News muhabir sorgusu, erken bulgu aramasıdır; haber başlığı veya kanıt kaydı muhabire açık atıf taşımadan isabet skoruna yazılmaz.

| Muhabir / Ağ | Google Arama Bulgusu | Skor Durumu |
|---|---:|---|
| Yağız Sabuncuoğlu | 15 | ATTRIBUTION_PENDING |
| Ertan Süzgün | 15 | ATTRIBUTION_PENDING |
| Sports Digitale | 15 | ATTRIBUTION_PENDING |
| Yakın Takip | 15 | ATTRIBUTION_PENDING |
| Ekrem Konur | 15 | ATTRIBUTION_PENDING |

## Skorlama Notu

- Resmi teyide dönüşüm, aynı oyuncu ve hedef kulüp için resmi kulüp duyurusu bulunduğunda sayılır.
- Erken haber saati yalnız hem ilk sinyal hem resmi duyuru zamanı varsa hesaplanır.
- Yanlış alarm vekili, 14 günden eski olup resmi teyide dönüşmemiş yönü belirli iddiadır; kesin yanlış bilgi hükmü değildir.

## Kaynaklar

| Kaynak | Katman | Gözlem | Ölçülebilir İddia | Resmiye Dönüşen | Ort. Erken Saat | Vekil Yanlış Alarm | Skor | Durum |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Milliyet | MEDIA | 3 | 1 | 0 | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Beşiktaş Haberleri | SECONDARY | 1 | 1 | 0 | — | %100.0 | 0.0 | PARTIAL_MEASUREMENT |
| Takvim Spor | MEDIA | 8 | 0 | 0 | — | — | — | OBSERVING |
| Hürriyet | MEDIA | 5 | 1 | 0 | — | — | — | OBSERVING |
| Fanatik | MEDIA | 3 | 0 | 0 | — | — | — | OBSERVING |
| Hürriyet Spor | MEDIA | 3 | 0 | 0 | — | — | — | OBSERVING |
| Mackolik.com | MEDIA | 3 | 0 | 0 | — | — | — | OBSERVING |
| beinsports.com.tr | MEDIA | 3 | 0 | 0 | — | — | — | OBSERVING |
| Ajansspor | MEDIA | 1 | 0 | 0 | — | — | — | OBSERVING |
| Anadolu Ajansı | MEDIA | 1 | 0 | 0 | — | — | — | OBSERVING |
| Cumhuriyet | MEDIA | 1 | 0 | 0 | — | — | — | OBSERVING |
| Diken | MEDIA | 1 | 0 | 0 | — | — | — | OBSERVING |
| GZT | MEDIA | 1 | 0 | 0 | — | — | — | OBSERVING |
| Habertürk | MEDIA | 1 | 0 | 0 | — | — | — | OBSERVING |
| Halk TV | MEDIA | 1 | 0 | 0 | — | — | — | OBSERVING |
| Konya Yeni Haber | MEDIA | 1 | 0 | 0 | — | — | — | OBSERVING |
| NTVSpor | MEDIA | 1 | 0 | 0 | — | — | — | OBSERVING |
| Nefes Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | OBSERVING |
| STAR - Haberler | MEDIA | 1 | 0 | 0 | — | — | — | OBSERVING |
| Sporx.com | MEDIA | 1 | 0 | 0 | — | — | — | OBSERVING |
| Takvim | MEDIA | 1 | 0 | 0 | — | — | — | OBSERVING |
| Transfer Haber | SECONDARY | 1 | 0 | 0 | — | — | — | OBSERVING |
| Türkiye Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | OBSERVING |
| Yeniçağ Gazetesi | MEDIA | 1 | 0 | 0 | — | — | — | OBSERVING |
| politikam.com | MEDIA | 1 | 0 | 0 | — | — | — | OBSERVING |
| @AmputeFutbol | SECONDARY | 0 | 0 | 0 | — | — | — | X_DATA_UNAVAILABLE |
| @EkremKonur | SECONDARY | 0 | 0 | 0 | — | — | — | X_DATA_UNAVAILABLE |
| @FabrizioRomano | SECONDARY | 0 | 0 | 0 | — | — | — | X_DATA_UNAVAILABLE |
| @GercekBJK | SECONDARY | 0 | 0 | 0 | — | — | — | X_DATA_UNAVAILABLE |
| @GizemKaya__ | SECONDARY | 0 | 0 | 0 | — | — | — | X_DATA_UNAVAILABLE |
| @KaraKartalBlog | SECONDARY | 0 | 0 | 0 | — | — | — | X_DATA_UNAVAILABLE |
| @SportsDigitale | SECONDARY | 0 | 0 | 0 | — | — | — | X_DATA_UNAVAILABLE |
| @WebdikBesiktas | SECONDARY | 0 | 0 | 0 | — | — | — | X_DATA_UNAVAILABLE |
| @YakinTakip | SECONDARY | 0 | 0 | 0 | — | — | — | X_DATA_UNAVAILABLE |
| @ertansuzgun | SECONDARY | 0 | 0 | 0 | — | — | — | X_DATA_UNAVAILABLE |
| @transfermarkt_TR | SECONDARY | 0 | 0 | 0 | — | — | — | X_DATA_UNAVAILABLE |
| @yagosabuncuoglu | SECONDARY | 0 | 0 | 0 | — | — | — | X_DATA_UNAVAILABLE |
| @yusufgunaydn | SECONDARY | 0 | 0 | 0 | — | — | — | X_DATA_UNAVAILABLE |
| Fenerbahçe Haberleri | SECONDARY | 0 | 0 | 0 | — | — | — | NO_TRANSFER_CLAIMS |
| Galatasaray Haberleri | SECONDARY | 0 | 0 | 0 | — | — | — | NO_TRANSFER_CLAIMS |
| Süper Lig Son Dakika | SECONDARY | 0 | 0 | 0 | — | — | — | NO_TRANSFER_CLAIMS |
| Trabzonspor Haberleri | SECONDARY | 0 | 0 | 0 | — | — | — | NO_TRANSFER_CLAIMS |