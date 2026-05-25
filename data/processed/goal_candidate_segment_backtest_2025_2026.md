# Gol Adayı Segment Backtest

- Aday satırı: 298
- Maç: 30
- Segment: 4
- Genel backtest: {'report_count': 29, 'matches_with_besiktas_goal': 26, 'top_3_hits': 16, 'top_5_hits': 20, 'top_8_hits': 22, 'top_10_hits': 23, 'top_3_hit_rate': 0.615, 'top_5_hit_rate': 0.769, 'top_8_hit_rate': 0.846, 'top_10_hit_rate': 0.885}

## Rank Kırılımı

| Bucket | Aday satırı | İsabet satırı | İsabetli maç | Maç hit rate | Satır hit rate |
|---|---:|---:|---:|---:|---:|
| top_3 | 90 | 20 | 17 | %56.7 | %22.2 |
| top_5 | 150 | 28 | 21 | %70.0 | %18.7 |
| top_8 | 240 | 32 | 23 | %76.7 | %13.3 |
| top_10 | 298 | 36 | 24 | %80.0 | %12.1 |

## Segment Tablosu

| Segment | Aday satırı | Maç | İsabet satırı | İsabetli maç | Maç hit rate | Satır hit rate | Top 5 maç hit rate | Ortalama sıra |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| unknown | 8 | 1 | 2 | 1 | %100.0 | %25.0 | %100.0 | 4.5 |
| primary | 262 | 29 | 30 | 22 | %75.9 | %11.5 | %65.5 | 5.45 |
| impact_sub | 162 | 29 | 23 | 18 | %62.1 | %14.2 | %51.7 | 4.56 |
| set_piece_defender | 25 | 15 | 0 | 0 | %0.0 | %0.0 | %0.0 | 8.16 |

## Öncelikli Aksiyonlar

- HIGH | Duran top/defans adayları: Defans adaylarını ilk 5'e taşımadan önce takım korner/duran top verisi veya oyuncu boy/hava topu sinyaliyle doğrula.
- MEDIUM | Yedek etki: Impact-sub segmenti primary kadar verimli; maç önü ekranda ilk 5 dışında ayrı 'sonradan gol' alanı olarak göster.
- MEDIUM | Top 5 sıralama: Top 5'i güçlendirmek için düşük isabetli segmentleri ilk 5 yerine 6-10 bandına indir.

## Top 5 Zayıf Aday Kuyruğu

- Top 5 içinde tekrar eden sıfır isabetli aday yok.