# metric11.com Yayın ve Güncellik Stratejisi

Güncelleme: 2026-05-23

## Kısa Cevap

Statik HTML mevcut MVP için doğru: hızlı, ucuz, Vercel/Netlify/GitHub Pages üzerinde kolay yayınlanır ve responsive sayfalar zaten üretilebiliyor.

Ancak statik HTML tek başına veriyi güncel tutmaz. Güncellik için veri pipeline'ının düzenli çalışması gerekir. Bu yüzden ürün mimarisi iki parçalı olmalı:

- Frontend: Vercel üzerinde statik HTML veya Next.js.
- Veri pipeline: GitHub Actions, Render cron, Railway cron, PythonAnywhere scheduled task veya kendi küçük VPS üzerinde günlük çalışan Python job.

## MVP Yayın Planı

1. İlk yayın:
   - `data/processed/*.html` dosyalarını Vercel static output olarak yayınla.
   - Ana giriş: `football_intelligence_home.html`.
   - Alan adı: `metric11.com`.

2. Günlük veri yenileme:
   - TFF maç/fikstür collector.
   - TFF oyuncu profili collector.
   - Transfermarkt kontrollü güncelleme.
   - API-Football izin verilen endpoint güncellemesi.
   - Kaynak izleme raporu.
   - Analiz ve dashboard build.

3. Ürünleşme:
   - Next.js frontend.
   - FastAPI backend.
   - Supabase veya Neon PostgreSQL.
   - Object storage veya repo artifact olarak JSON snapshot.

## Vercel Uygun mu?

Evet, frontend için uygun. Ücretsiz başlangıç için iyi seçenek.

Vercel şu işler için uygundur:

- responsive ürün arayüzü
- statik dashboard
- Next.js sayfaları
- JSON dosyalarından okuyan frontend
- landing değil, gerçek analiz ekranı

Vercel şu işler için tek başına yeterli değildir:

- uzun süren scraper
- rate-limit beklemeli veri toplama
- günlük büyük veri işleme
- browser/Selenium tarzı collector

Bu yüzden scraper ve model job'ları Vercel dışında çalışmalı, üretilen JSON/HTML çıktısı Vercel'e deploy edilmelidir.

## Ücretsiz Mimari Önerisi

- Frontend: Vercel Free
- Kod deposu ve scheduler: GitHub + GitHub Actions
- Veritabanı: Supabase Free veya Neon Free
- Hafif backend: Render Free/Fly.io/Railway denemesi veya başlangıçta backend yok
- Dosya çıktıları: repo artifact, GitHub Pages artifact veya Supabase Storage

## Günlük Job Sırası

```bash
python -m src.collect_tff_league_season
python -m src.collect_besiktas_season
python -m src.collect_tff_player_profiles --team "BEŞİKTAŞ A.Ş." --limit 0 --output data/processed/tff_player_profiles_besiktas_2025_2026.json
python -m src.collect_transfermarkt_squad
python -m src.build_player_availability
python -m src.analyze_league_scouting --output-prefix league_scouting_2025_2026_normalized
python -m src.analyze_team_needs
python -m src.analyze_enriched_scouting
python -m src.build_fm_style_scout_program
python -m src.build_position_scout_matrix
python -m src.model_league_predictions
python -m src.generate_preview_batch
python -m src.backtest_goal_candidates
python -m src.backtest_match_predictions
python -m src.build_source_watchlist
python -m src.build_data_catalog
python -m src.build_dashboard
python -m src.build_backtest_dashboard
python -m src.build_team_needs_dashboard
python -m src.build_enriched_scout_dashboard
python -m src.build_command_center
python -m src.build_product_home
```

## GitHub Actions

Repo içinde hazır workflow eklendi:

- `.github/workflows/daily-pipeline.yml`

Varsayılan zamanlı çalışma network collector'ları çalıştırmadan mevcut veriden analiz ve dashboard üretir. Manuel çalıştırmada `include_network=true` seçilirse TFF, Transfermarkt ve haber/sakat-cezalı collector'ları da çalışır.

Gerekli secret'lar:

- `API_FOOTBALL_KEY`
- `FOOTBALL_DATA_KEY`

Vercel tarafında en temiz akış:

1. GitHub Actions pipeline verileri üretir.
2. `data/processed` çıktıları artifact veya repo commit/PR akışıyla güncellenir.
3. Vercel statik/Next.js frontend'i bu JSON/HTML çıktılarından yayınlar.

## Doğruluk Hedefi

%80 maç sonucu doğruluğu gerçekçi bir kısa vadeli hedef değildir. Futbolda 1X2 sonucu yüksek rastlantısallık içerir. Daha gerçekçi ürün hedefleri:

- maç sonucu yön eğilimi: önce %55-60, sonra %62-65
- gol adayı Top 5: %73'ten %80 bandına çıkarmak
- skor senaryosu: tek skor yerine ilk 3 skor senaryosunda isabet ölçmek
- kart riski: hakem + takım kart profiliyle ayrı modellemek
- oyuncu önerisi: pozisyon/rol bazında tutarlılık ve ekonomik fırsat skoru

Ürün dili kesin hüküm değil, güven aralığı ve senaryo olmalıdır.
