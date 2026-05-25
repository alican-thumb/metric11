# Futbol İstihbarat Platformu MVP

Bu klasor, futbol istihbarat platformu icin ilk veri toplama, analiz ve statik dashboard hattini kurar. Amac:

- TFF mac detay sayfalarindan hakem, kart, kadro ve mac metnini test etmek
- API-Football ve football-data.org icin API anahtari varsa kapsam testi yapmak
- Ham veriyi kaynak bazli saklamak
- Hangi veri var, hangisi eksik, hangisi riskli raporlamak
- Mac onu tahminleri, gol adaylari, scout listesi ve takim ihtiyac analizleri uretmek

## Kurulum

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.template .env
```

Paylasilabilir sablon `.env.template` dosyasindadir. Anahtarlar yerelde `.env` veya ignore edilen `.env.example` dosyasında tutulur:

```bash
API_FOOTBALL_KEY=...
FOOTBALL_DATA_KEY=...
X_BEARER_TOKEN=...
```

## Veri Kesif Calistirma

```bash
python -m src.discovery
```

2025-2026 Beşiktaş sezonunu TFF fikstüründen toplamak için:

```bash
python -m src.collect_besiktas_season
```

Cikti:

- `data/raw/`: ham API/HTML/CSV cevaplari
- `data/processed/discovery_report.json`
- `data/processed/discovery_report.md`

## 2025-2026 Super Lig Veri Hatti

Tum lig maclarini TFF'den toplamak:

```bash
python -m src.collect_tff_league_season
```

Besiktas mac onu raporlari ve paneli:

```bash
python -m src.build_player_availability
python -m src.generate_preview_batch
python -m src.backtest_goal_candidates
python -m src.backtest_match_predictions
python -m src.build_dashboard
```

Sakat/cezali bilgisi iki katmanli calisir:

- Otomatik katman: TFF mac kartlarindan kirmizi kart ve kart birikimi icin sonraki mac ceza sinyali uretir.
- Manuel katman: resmi sakatlik/ceza listesi veya guvenilir haberlerden dogrulanan bilgileri `data/manual/player_availability_overrides.json` dosyasindan okur.

Ornek manuel dosya `data/manual/player_availability_overrides.example.json` icindedir. Bu katman muhtemel 11 ve gol adayi listelerinden eksik oyuncuyu cikarir, tahmin guvenini ve beklenen gol hesabini etkiler.

Lig geneli scout, tahmin modeli ve backtest paneli:

```bash
python -m src.analyze_league_scouting --output-prefix league_scouting_2025_2026_normalized
python -m src.build_scout_dashboard --input data/processed/league_scouting_2025_2026_normalized.json --output data/processed/league_scouting_2025_2026_normalized_dashboard.html
python -m src.model_league_predictions
python -m src.build_model_baseline_comparison
python -m src.build_draw_risk_audit
python -m src.build_backtest_dashboard
```

Dış API snapshot verisi:

```bash
python -m src.collect_external_snapshots --season 2024
python -m src.collect_external_snapshots --season 2025
python -m src.analyze_api_football_snapshot
```

Not: API-Football ücretsiz planı 2025 sezonunu kısıtlayabilir. Bu durumda 2025-2026 ana sezon verisi TFF hattından, API-Football ise geçmiş sezon zenginleştirme ve dış doğrulama katmanından gelir.

Besiktas oyuncu profilleri, takim ihtiyac analizi ve paneli:

```bash
python -m src.collect_tff_player_profiles --team "BEŞİKTAŞ A.Ş." --limit 0 --output data/processed/tff_player_profiles_besiktas_2025_2026.json
python -m src.collect_transfermarkt_squad
python -m src.analyze_team_needs
python -m src.build_team_needs_dashboard
```

Scout kisa liste oyuncu profili ve zenginlestirilmis scout paneli:

```bash
python -m src.collect_tff_player_profiles --scout-input data/processed/league_scouting_2025_2026_normalized.json --scout-limit 25 --limit 0 --output data/processed/tff_player_profiles_scout_shortlist_2025_2026.json
python -m src.analyze_enriched_scouting
python -m src.build_enriched_scout_dashboard
python -m src.build_fm_style_scout_program
```

FM/FIFA tarzi oyuncu attribute CSV dosyasi kullanilacaksa once normalize edilir:

```bash
python -m src.import_player_attribute_dataset --input data/manual/player_attribute_imports/players.csv --source-name "Verified Player Attribute Dataset" --license-status "CC0_PUBLIC_DOMAIN" --risk-level LOW
python -m src.analyze_enriched_scouting
```

Kaynak politikasi `data/manual/player_attribute_sources.json` ve `docs/player_attribute_data_strategy.md` dosyalarindadir. Football Manager oyun veritabaninin dogrudan izinsiz dump'i ticari urun verisi olarak kullanilmaz; lisansi acik dataset veya kullanim hakki olan export gerekir.
Ornek CSV formati `data/manual/player_attribute_imports/example_players.csv` dosyasindadir.

Veri katalogu ve ana urun giris sayfasi:

```bash
python -m src.build_sqlite_warehouse
python -m src.build_goal_candidate_segment_backtest
python -m src.build_protected_action_audit
python -m src.build_side_flip_audit
python -m src.build_data_quality_scorecard
python -m src.build_data_catalog
python -m src.build_public_source_summary
python -m src.build_command_center
python -m src.build_product_home
```

`data_catalog_2025_2026` iç kaynak/lisans/risk takibi içindir. `public_source_summary_2025_2026` ise kullanıcı arayüzünde gösterilebilir genel kaynak kategorilerini üretir. Kaynak gizleyerek lisans veya kullanım şartı riski aşılmaya çalışılmaz.

Transfer haber takibi için `python -m src.collect_news_twitter` çalıştırıldığında
`X_BEARER_TOKEN` varsa resmi X API v2 kullanıcı timeline'ları okunur. X API
post okumaları kullanıma göre ücretlendirilebilir; token yalnız kontrollü
günlük çalıştırmada tanımlanmalıdır. Token yoksa Nitter geliştirme fallback'i
denenir ve başarısızlık da snapshot durum bilgisi olarak kaydedilir.

Resmi teyit için anahtarsız birincil yol
`python -m src.collect_official_club_news` komutudur. Bu collector Süper Lig'deki
18 kulübün resmi haber sayfasını tarar, erişemediği kaynağı kapsam metriğinde
gösterir ve resmi transfer duyurularını analiz kapısına taşır. X token'ı bu
yolun çalışması için gerekli değildir.

## Onemli Paneller

- `data/processed/besiktas_2025_2026_dashboard_chronological.html`
- `data/processed/league_scouting_2025_2026_normalized_dashboard.html`
- `data/processed/prediction_backtest_dashboard_2025_2026.html`
- `data/processed/besiktas_team_needs_2025_2026_dashboard.html`
- `data/processed/league_scouting_enriched_2025_2026_dashboard.html`
- `data/processed/fm_style_scout_program_2025_2026.html`
- `data/processed/football_intelligence_home.html`
- `data/processed/football_command_center_2025_2026.html`
- `data/processed/model_baseline_comparison_2025_2026.md`
- `data/processed/draw_risk_audit_2025_2026.md`
- `data/processed/protected_action_audit_2025_2026.md`
- `data/processed/side_flip_audit_2025_2026.md`
- `data/manual/opponent_market_values_2025_2026.json`
- `data/processed/goal_candidate_segment_backtest_2025_2026.md`
- `data/processed/data_catalog_2025_2026.md`
- `data/processed/data_quality_scorecard_2025_2026.md`
- `data/processed/public_source_summary_2025_2026.md`
- `data/processed/transfermarkt_besiktas_squad_2025_2026.md`
- `data/processed/player_availability_besiktas_2025_2026.md`
- `data/processed/api_football_super_lig_snapshot_2024.md`
- `data/processed/api_football_super_lig_snapshot_2025.md`
- `data/processed/api_football_super_lig_2024_analysis.html`
- `docs/player_attribute_data_strategy.md`
- `data/manual/player_attribute_sources.json`

## Ilk Hedef

Ilk sprintin basarisi, Besiktas veya Super Lig icin tum urunu bitirmek degil; su sorulara kanitli cevap vermektir:

- Fikstur ve skor verisini hangi kaynaktan guvenilir aliyoruz?
- TFF mac detaylari scrape edilebilir mi?
- Hakem, kart ve oyuncu metni parse edilebiliyor mu?
- API-Football/football-data.org Super Lig icin hangi endpointleri veriyor?
- Hangi veri tipleri kesin eksik?
- Sifir/dusek butce verisiyle hangi tahmin ve scout sinyalleri olculebilir?

## Bilinen Kritik Eksikler

- TFF oyuncu profilleri yas/sozlesme veriyor ama guvenilir pozisyon/mevki alani vermiyor; Beşiktaş icin bu alan Transfermarkt kadro sayfasiyla tamamlandi.
- Lig scout skoru pozisyon verisi gelene kadar golcu agirlikli kalir.
- Mac sonucu modeli MVP seviyesinde: lig geneli Poisson/Elo modeli yaklasik `%50` dogruluk verdi, urun ekraninda mutlaka guven ve risk bayraklariyla gosterilmeli.
- Gol adayı modeli segment backtest sonrası güçlendirildi: Top 5 `%77`, Top 8 `%85`, Top 10 `%88`.
- Maç önü ekranında beraberlik riskine bağlı korumalı tahmin aksiyonu gösterilir; bu ana 1X2 tahminini değiştirmez, riskli taraf seçimlerinde beraberlik senaryosunu öne çıkarır. Beşiktaş özelinde bu aksiyon ayrıca `protected_action_audit` ile backtest edilir.
- Yanlış taraf denetimi, modelin tarafı ters aldığı maçlarda rakip piyasa değeri market edge'ini gösterir; kalan ana veri boşlukları odds baseline, resmi sakatlık akışı ve doğrulanmış maç günü 11 kalitesidir.
- Ayak, boy, resmi sakatlik gecmisi ve transfer gecmisi icin ek acik kaynak eslestirmesi gerekir.
- Cezali oyuncu sinyali otomatik uretiliyor; sakatlik bilgisi su an manuel override veya resmi kaynak eklemesi gerektiriyor.
- FM/FIFA tarzi attribute import hatti hazir; henuz lisansi dogrulanmis gercek CSV import edilmediyse scout modelinde bu sinyal bos kalir.

## Veritabani

PostgreSQL MVP semasi `db/schema.sql` dosyasindadir.
