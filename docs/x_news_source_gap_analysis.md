# X Haber Kaynakları Boşluk Analizi

Güncelleme: 2026-05-25

## Amaç

metric11 haber, sakat/cezalı, kadro ve transfer bağlamı için X kaynak
kapsamını Süper Lig'in tüm takımlarına genişletmek. Bu belge yalnız projede
henüz doğru biçimde tanımlı olmayan kaynakları ve mevcut kayıtlardaki
düzeltmeleri listeler; otomatik yayın güveni anlamına gelmez.

## Mevcut Durum

- `src/collect_news_twitter.py` içinde 30 hesap tanımlı: 18 resmi kulüp,
  TFF/lig, medya ve transfer sinyal hesapları.
- Collector resmi X API v2 kullanıcı timeline yolunu destekliyor; bunun için
  ortamda `X_BEARER_TOKEN` gerekir. Anahtar yokken Nitter yalnız geliştirme
  fallback'i olarak denenir ve başarısız olsa bile durum snapshot'ı yazılır.
- Başarılı gönderi snapshot'ı henüz yok; bu nedenle mevcut transfer analiz
  çıktısında X teyidi yoktur. Resmi teyit boşluğu anahtarsız resmi web
  collector'ı ile kapatılmıştır: canlı ölçümde 18 kulüp kaydının 16'sına
  erişilmiş ve 13 tekil resmi sinyal duyurusu alınmıştır.
- Önceki üç resmi handle açığı kodda giderildi:

| Kayıt | Eski handle | Kullanılan ana handle | Neden |
|---|---|---|---|
| Beşiktaş | `@bjkcom` | [`@Besiktas`](https://x.com/Besiktas) | Resmi ana X hesabı budur. |
| Galatasaray | `@galatasaray` | [`@GalatasaraySK`](https://x.com/GalatasaraySK) | Mevcut handle İngilizce hesap; Türkçe resmi duyuru için ana hesap izlenmeli. |
| TFF | `@TFForg` | [`@TFF_Org`](https://x.com/TFF_Org) | Kodda handle yazımı resmi hesapla uyuşmuyor. |

## Öncelik A: Yapılandırılmış Resmi Kulüp Hesapları

Bu kaynaklar resmi duyuru olduğu için kadro dışı/sakatlık, maç kadrosu,
ceza, resmi transfer, teknik direktör ve sözleşme olaylarında en yüksek
güvenli haber katmanıdır.

| Takım | X hesabı | Durum | Alınabilecek veri |
|---|---|---|---|
| RAMS Başakşehir | [`@ibfk2014`](https://x.com/ibfk2014) | Doğrulandı | İlk 11, kadro, sakat/cezalı açıklaması, transfer/imza, teknik ekip |
| Corendon Alanyaspor | [`@Alanyaspor`](https://x.com/Alanyaspor) | Doğrulandı | Kadro, sakatlık, transfer, maç duyurusu |
| Samsunspor | [`@Samsunspor`](https://x.com/Samsunspor) | Doğrulandı | Kadro, sözleşme/transfer, Avrupa/lig maç bağlamı |
| Göztepe | [`@Goztepe`](https://x.com/Goztepe) | Canlı profil doğrulaması gerekli | Kadro, transfer, kulüp açıklaması |
| TÜMOSAN Konyaspor | [`@konyaspor`](https://x.com/konyaspor) | Doğrulandı | Kadro, sakatlık, transfer |
| Çaykur Rizespor | [`@CRizesporAS`](https://x.com/CRizesporAS) | Doğrulandı | İlk 11 ve açık sakatlık bildirimi dahil availability sinyali |
| Gaziantep FK | [`@gaziantepfk`](https://x.com/gaziantepfk) | Canlı profil doğrulaması gerekli | Kadro, transfer, sakat/cezalı |
| Kasımpaşa | [`@kasimpasa`](https://x.com/kasimpasa) | Canlı profil doğrulaması gerekli | Kadro, transfer, teknik ekip |
| Kocaelispor | [`@Kocaelispor`](https://x.com/Kocaelispor) | Doğrulandı | Sözleşme uzatma, teknik direktör, transfer, kadro |
| ikas Eyüpspor | [`@eyupsporkulubu`](https://x.com/eyupsporkulubu) | Doğrulandı | Kadro, transfer, kulüp duyurusu |
| Gençlerbirliği | [`@kirmizikara`](https://x.com/kirmizikara) | Canlı profil doğrulaması gerekli | Teknik direktör, kadro, transfer |
| Fatih Karagümrük | [`@karagumruk_sk`](https://x.com/karagumruk_sk) | Canlı profil doğrulaması gerekli | Kadro, transfer, maç duyurusu |
| Hesap.com Antalyaspor | [`@Antalyaspor`](https://x.com/Antalyaspor) | Doğrulandı | Kadro, sakatlık, transfer |
| Zecorner Kayserispor | [`@KayserisporFK`](https://x.com/KayserisporFK) | Canlı profil doğrulaması gerekli | Kadro, oyuncu değişimi, gol/maç akışı, transfer |

## Öncelik B: Yapılandırılmış Lig ve Haber Kaynakları

| Kaynak | X hesabı | Projede durum | Kullanım | Güven kuralı |
|---|---|---|---|---|
| Trendyol Süper Lig | [`@superlig`](https://x.com/superlig) | Collector'da tanımlı, snapshot bekliyor | Fikstür, haftalık program, resmi lig duyurusu | TFF ile çapraz doğrula |
| TRT Spor | [`@trtspor`](https://x.com/trtspor) | Collector'da tanımlı, snapshot bekliyor | Son dakika sakatlık/transfer/kulüp açıklaması yayılımı | Haber sinyali; resmi hesapla onaylanmadan availability uygulanmaz |
| Sports Digitale | [`@SportsDigitale`](https://x.com/SportsDigitale) | Collector'da tanımlı, snapshot bekliyor | Transfer anlaşmaları, kart cezası, kadro gelişmeleri | İkincil sinyal; resmi/TFF doğrulaması gerekir |
| Yağız Sabuncuoğlu | [`@yagosabuncuoglu`](https://x.com/yagosabuncuoglu) | Collector'da tanımlı, snapshot bekliyor | Transfer ve kadro dışı/sakatlık erken uyarısı | Rumor/lead olarak saklanır; doğrudan model girdisi olmaz |

Mevcut collector'da bulunan `@beINSPORTS_TR`, `@fanatikgazetesi`,
`@hurspor`, `@fotomacgazetesi`, `@transfermarkt_TR`, `@YakinTakip` ve
`@TurkishFootball` bu tabloya tekrar dahil edilmedi.

## Kaynaklardan Üretilecek Alanlar

| Veri türü | Öncelikli kaynak | Kaydedilecek alanlar | Modele giriş kuralı |
|---|---|---|---|
| İlk 11 / kadro | Resmi kulüp hesabı | `team`, `match_date`, `players`, `post_id`, `post_url`, `published_at` | Maç öncesi doğrulanmış kadro olarak kullanılabilir |
| Sakat / kadroda yok | Resmi kulüp, sonra resmi yayıncı | `player_name`, `team`, `status`, `reason_text`, `confidence`, `source_post_id` | Resmi kulüp açıklaması `VERIFIED`; medya `REVIEW_REQUIRED` |
| Cezalı | TFF/PFDK veya resmi kulüp | `player_name`, `team`, `ban_type`, `effective_match`, `source_post_id` | TFF/resmi kulüp doğrulaması olmadan maç motoruna girmez |
| Transfer / sözleşme | Resmi kulüp; medya/muhabir erken sinyal | `player_name`, `from_team`, `to_team`, `event_type`, `reported_fee`, `status` | `official` olmadan scout değerini değiştirmez |
| Teknik direktör değişimi | Resmi kulüp | `team`, `coach`, `event_type`, `effective_date` | Form/model yorum katmanına doğrulanmış bağlam olarak eklenebilir |
| Muhtemel 11 / söylenti | Medya ve muhabir | `player_name`, `team`, `claim`, `confidence`, `corroboration_count` | Yalnız görünür haber bağlamı; xG ayarı üretmez |

## Toplama Yöntemi ve Yayın Kuralı

Collector artık üretim yolunda X API kullanıcı gönderileri endpoint'ini
`GET /2/users/:id/tweets` kullanır ve hesapları `GET /2/users/by` ile çözer.
Nitter RSS kararlı veya yetkilendirilmiş ana veri yolu değildir; sadece
geliştirme fallback'i olarak korunur. X API post okumaları kullanıma göre
ücretlendirildiği için anahtar ve kredi/bütçe olmadan otomatik API çağrısı
yapılmaz.

- Ham saklama: post kimliği, hesap kimliği, metin, oluşturma zamanı, kaynak
  URL'i ve çıkarılmış sinyal; medya dosyası kopyalanmamalı.
- Ürün gösterimi: orijinal X gönderisi gösterilecekse X display ve attribution
  kurallarına uyulmalı.
- Yayın güveni: `OFFICIAL_VERIFIED`, `MEDIA_CORROBORATED`,
  `RUMOR_REVIEW_REQUIRED` seviyeleri zorunlu tutulmalı.
- Model güveni: yalnız `OFFICIAL_VERIFIED` availability ve ceza sinyalleri
  doğrudan maç önü hesaplamasını etkileyebilir.

## Uygulama Sırası

1. Anahtar gerektirmeyen `src.collect_official_club_news` collector'ı ile
   18 kulübün resmi web duyurularını günlük tara; erişim kapsamını ve resmi
   transfer teyitlerini snapshot içinde sakla.
2. Opsiyonel sosyal hız/zenginleştirme gerektiğinde `X_BEARER_TOKEN` ve
   kontrollü okuma bütçesiyle X hesaplarında snapshot üret.
3. TFF ve resmi kulüp kaynaklarıyla availability şemasını tüm 18 takıma aç.
4. `@trtspor`, `@SportsDigitale` ve `@yagosabuncuoglu` kaynaklarından gelen
   verinin yalnız `secondary_signal` olarak kaldığını testle güvenceye al.
5. Nitter geliştirme fallback'i olarak ayrıldı; ilk gerçek X API snapshot'ı
   sonrasında saklama ve display politikasını gerçek veriyle denetle.
6. Kaynak bazlı kapsama raporu üret: hesap erişim başarısı, bulunan resmi
   sakat/ceza sinyali, doğrulanan transfer ve çözülmeyen haber kuyruğu.

## Doğrulama Kaynakları

- Resmi profil doğrulamaları: [Beşiktaş](https://x.com/Besiktas),
  [Galatasaray](https://x.com/GalatasaraySK), [TFF](https://x.com/TFF_Org),
  [Başakşehir](https://x.com/ibfk2014), [Alanyaspor](https://x.com/Alanyaspor),
  [Konyaspor](https://x.com/konyaspor), [Kocaelispor](https://x.com/Kocaelispor),
  [Eyüpspor](https://x.com/eyupsporkulubu).
- Doğrudan gönderiyle doğrulanan etkin hesaplar:
  [Çaykur Rizespor](https://x.com/CRizesporAS/status/1974142200855556376),
  [Samsunspor](https://x.com/Samsunspor/status/2024621638705201522),
  [Antalyaspor](https://x.com/Antalyaspor/status/2015412021697675422),
  [beIN SPORTS Türkiye](https://x.com/beINSPORTS_TR/status/2041456168086720524),
  [Sports Digitale](https://x.com/SportsDigitale/status/2040856569106051321).
- API ve kullanım politikası:
  [X API user timelines](https://docs.x.com/x-api/posts/timelines/introduction),
  [X API pricing](https://docs.x.com/x-api/getting-started/pricing),
  [X API recent search](https://docs.x.com/x-api/posts/search/introduction),
  [X Developer Policy](https://docs.x.com/developer-terms/policy),
  [X display requirements](https://docs.x.com/developer-terms/display-requirements).
