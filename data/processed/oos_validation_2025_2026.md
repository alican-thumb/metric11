# Out-of-Sample Validasyon Raporu — 2025-2026

Split: Hafta 1-17 birikimli tarih, Hafta 18+ bağımsız test.
_Not: Walk-forward kronolojik backtest. Her tahmin yalnızca önceki maçların birikimiyle yapılır. Hafta 1-17 = ısınma + ilk yarı; hafta 18-34 = bağımsız test penceresi._

## Özet

| Dönem | Doğruluk | Brier | Log Loss |
|---|---:|---:|---:|
| Tüm sezon | %46.1 (119/258) | 0.615 | 1.027 |
| İlk yarı (hafta 1-17) | %46.7 (49/105) | 0.617 | 1.031 |
| **İkinci yarı OOS (hafta 18-34)** | **%45.8 (70/153)** | 0.614 | 1.024 |

## Güven Seviyesi Kırılımı (Tüm Sezon)

| Güven | Doğruluk | |
|---|---:|---|
| HIGH | %59.6 (62/104) | Brier: 0.549 |
| MEDIUM | %37.9 (33/87) | Brier: 0.664 |
| LOW | %35.8 (24/67) | Brier: 0.656 |

## Güven Seviyesi Kırılımı (OOS — İkinci Yarı)

| Güven | Doğruluk | |
|---|---:|---|
| HIGH | %58.7 (37/63) | Brier: 0.561 |
| MEDIUM | %37.5 (18/48) | Brier: 0.659 |
| LOW | %35.7 (15/42) | Brier: 0.642 |

## Sonuç Tipi Kırılımı (Tüm Sezon)

| Gerçek Sonuç | Model Doğruluğu |
|---|---:|
| Ev sahibi kazandı | %53.2 (59/111) |
| Beraberlik | %31.6 (24/76) |
| Deplasman kazandı | %50.7 (36/71) |

## Kümülatif Doğruluk (son 10 hafta)

| Hafta | Kümülatif Doğruluk | Maç |
|---:|---:|---:|
| 25 | %49.7 | 177 |
| 26 | %49.5 | 186 |
| 27 | %49.7 | 195 |
| 28 | %48.5 | 204 |
| 29 | %48.8 | 213 |
| 30 | %48.2 | 222 |
| 31 | %47.6 | 231 |
| 32 | %47.1 | 240 |
| 33 | %47.0 | 249 |
| 34 | %46.1 | 258 |

## Draw Kalibrasyon Karşılaştırması

| | Ham argmax | Kalibre |
|---|---:|---:|
| Tüm sezon doğruluk | %50.4 (130/258) | %46.1 (119/258) |
| OOS ikinci yarı doğruluk | %51.6 (79/153) | %45.8 (70/153) |
| Beraberlik doğruluğu (tüm sezon) | %0.0 (0/76) | %31.6 (24/76) |
| Ev sahibi doğruluğu | %73.0 (81/111) | %53.2 (59/111) |
| Deplasman doğruluğu | %69.0 (49/71) | %50.7 (36/71) |

## Yorumlama

- Tüm sezon doğruluğu walk-forward kronolojik tahmindir; gelecek sonuçlar o anda görülmüyor.
- Hafta 18+ (ikinci yarı OOS) gerçek bağımsız test penceresine en yakın ölçüm.
- Hiperparametreler (K faktör, blend oranı) bu sezon verisine göre ayarlanmadı; genel futbol pratiğine dayanıyor.
- Draw kalibrasyon eşikleri: min draw_p=0.26, max gap=0.18, boost=0.12 (draw_calibrated_prediction).
- Canlı kullanım için: HIGH güven → güvenilir sinyal, LOW güven → bilgi amaçlı.