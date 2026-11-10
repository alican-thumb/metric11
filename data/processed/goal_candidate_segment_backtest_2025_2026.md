# Gol Adayı Segment Backtest

- Aday satırı: 298
- Maç: 30
- Segment: 4
- Genel backtest: {'report_count': 29, 'matches_with_besiktas_goal': 26, 'top_3_hits': 16, 'top_5_hits': 20, 'top_8_hits': 22, 'top_10_hits': 23, 'top_3_hit_rate': 0.615, 'top_5_hit_rate': 0.769, 'top_8_hit_rate': 0.846, 'top_10_hit_rate': 0.885}

## Rank Kırılımı

| Bucket | Aday satırı | İsabet satırı | İsabetli maç | Maç hit rate | Satır hit rate |
|---|---:|---:|---:|---:|---:|
| top_3 | 90 | 20 | 17 | %56.7 | %22.2 |
| top_5 | 150 | 26 | 21 | %70.0 | %17.3 |
| top_8 | 240 | 32 | 23 | %76.7 | %13.3 |
| top_10 | 298 | 37 | 24 | %80.0 | %12.4 |

## Segment Tablosu

| Segment | Aday satırı | Maç | İsabet satırı | İsabetli maç | Maç hit rate | Satır hit rate | Top 5 maç hit rate | Ortalama sıra |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| unknown | 8 | 1 | 2 | 1 | %100.0 | %25.0 | %100.0 | 4.5 |
| primary | 264 | 29 | 31 | 23 | %79.3 | %11.7 | %62.1 | 5.46 |
| impact_sub | 160 | 29 | 23 | 18 | %62.1 | %14.4 | %51.7 | 4.49 |
| set_piece_defender | 24 | 15 | 0 | 0 | %0.0 | %0.0 | %0.0 | 8.42 |

## Öncelikli Aksiyonlar

- HIGH | Duran top/defans adayları: Defans adaylarını ilk 5'e taşımadan önce takım korner/duran top verisi veya oyuncu boy/hava topu sinyaliyle doğrula.
- MEDIUM | Yedek etki: Impact-sub segmenti primary kadar verimli; maç önü ekranda ilk 5 dışında ayrı 'sonradan gol' alanı olarak göster.
- MEDIUM | Top 5 sıralama: Top 5'i güçlendirmek için düşük isabetli segmentleri ilk 5 yerine 6-10 bandına indir.

## Top 5 Zayıf Aday Kuyruğu

- ISHOLA JUNIOR  OLAITAN | primary | top5=6 | satır=8 | isabet=0 | Top 5 sıralama etkisini düşür veya aday tipini yeniden kontrol et.
- DAVID JURASEK | primary+impact_sub | top5=4 | satır=12 | isabet=0 | Top 5 sıralama etkisini düşür veya aday tipini yeniden kontrol et.