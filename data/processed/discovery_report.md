# Futbol Veri Kesif Raporu

Olusturma zamani: `2026-05-22T05:19:00.493800+00:00`

## Ozet

- TFF test edilen mac sayisi: 4, basarili: 4
- API-Football testleri: 1, atlanan: 1
- football-data.org testleri: 1, atlanan: 1
- football-data.co.uk CSV testi basarili: False
- Islenmis TFF mac veri seti: `/Users/alicanakyol/Documents/analiz/data/processed/tff_matches.json`

## TFF Mac Detay Testleri

- Mac ID `249505`: ok=True, status=200
  - Mac: BEŞİKTAŞ A.Ş. 3 - 2 ÇAYKUR RİZESPOR A.Ş.
  - Organizasyon: Trendyol Süper Lig (Profesyonel Takım)
  - Ham dosya: `/Users/alicanakyol/Documents/analiz/data/raw/tff/20260522T051826Z_match_249505.html`
  - Parse JSON: `/Users/alicanakyol/Documents/analiz/data/raw/tff_parsed/20260522T051826Z_match_249505.json`
  - Hakem satiri sayisi: 7
  - Parse edilen hakem linki: 7
  - Parse edilen ilk 11 oyuncusu: 22
  - Parse edilen yedek oyuncu: 20
  - Parse edilen kart olayi: 5
  - Sari kart metin sayimi: 5
  - Kirmizi kart metin sayimi: 0
- Mac ID `249392`: ok=True, status=200
  - Mac: BEŞİKTAŞ A.Ş. 2 - 0 TRABZONSPOR A.Ş.
  - Organizasyon: Trendyol Süper Lig (Profesyonel Takım)
  - Ham dosya: `/Users/alicanakyol/Documents/analiz/data/raw/tff/20260522T051826Z_match_249392.html`
  - Parse JSON: `/Users/alicanakyol/Documents/analiz/data/raw/tff_parsed/20260522T051826Z_match_249392.json`
  - Hakem satiri sayisi: 7
  - Parse edilen hakem linki: 7
  - Parse edilen ilk 11 oyuncusu: 22
  - Parse edilen yedek oyuncu: 20
  - Parse edilen kart olayi: 3
  - Sari kart metin sayimi: 3
  - Kirmizi kart metin sayimi: 0
- Mac ID `264125`: ok=True, status=200
  - Mac: BEŞİKTAŞ A.Ş. 1 - 0 FENERBAHÇE A.Ş.
  - Organizasyon: Trendyol Süper Lig Şamil Ekinci Sezonu (Profesyonel Takım)
  - Ham dosya: `/Users/alicanakyol/Documents/analiz/data/raw/tff/20260522T051827Z_match_264125.html`
  - Parse JSON: `/Users/alicanakyol/Documents/analiz/data/raw/tff_parsed/20260522T051827Z_match_264125.json`
  - Hakem satiri sayisi: 7
  - Parse edilen hakem linki: 6
  - Parse edilen ilk 11 oyuncusu: 22
  - Parse edilen yedek oyuncu: 20
  - Parse edilen kart olayi: 2
  - Sari kart metin sayimi: 2
  - Kirmizi kart metin sayimi: 0
- Mac ID `264089`: ok=True, status=200
  - Mac: BEŞİKTAŞ A.Ş. 1 - 3 KASIMPAŞA A.Ş.
  - Organizasyon: Trendyol Süper Lig Şamil Ekinci Sezonu (Profesyonel Takım)
  - Ham dosya: `/Users/alicanakyol/Documents/analiz/data/raw/tff/20260522T051827Z_match_264089.html`
  - Parse JSON: `/Users/alicanakyol/Documents/analiz/data/raw/tff_parsed/20260522T051827Z_match_264089.json`
  - Hakem satiri sayisi: 7
  - Parse edilen hakem linki: 6
  - Parse edilen ilk 11 oyuncusu: 22
  - Parse edilen yedek oyuncu: 20
  - Parse edilen kart olayi: 6
  - Sari kart metin sayimi: 6
  - Kirmizi kart metin sayimi: 0

## API-Football

- `leagues?search=Super Lig`: ok=False, skipped=True, status=None, item_count=None
  - Not/Hata: API_FOOTBALL_KEY bulunamadi; .env icine eklenirse test edilir.

## football-data.org

- `competitions`: ok=False, skipped=True, status=None, item_count=None
  - Not/Hata: FOOTBALL_DATA_KEY bulunamadi; .env icine eklenirse test edilir.

## football-data.co.uk CSV

- ok=False, status=None, sample_rows=0
- Referee kolonu: False
- Kart kolonlari: False
- Odds kolonlari: False
- Hata: HTTPSConnectionPool(host='www.football-data.co.uk', port=443): Read timed out. (read timeout=30)

## Ilk Karar

Bu rapor kaynaklarin gercek cevaplarini saklar. Bir sonraki adim, API anahtarlari eklendikten sonra Super Lig fixture/lineup/player endpointlerini fixture bazinda test etmektir.