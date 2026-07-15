# Out-of-Sample Validasyon Raporu — 2025-2026

Split: Hafta 1-17 birikimli tarih, Hafta 18+ bağımsız test.
_Not: Walk-forward kronolojik backtest. Her tahmin yalnızca önceki maçların birikimiyle yapılır. Hafta 1-17 = ısınma + ilk yarı; hafta 18-34 = bağımsız test penceresi._

## Özet

| Dönem | Doğruluk | Brier | Log Loss |
|---|---:|---:|---:|
| Tüm sezon | %47.3 (122/258) | 0.61 | 1.019 |
| İlk yarı (hafta 1-17) | %47.6 (50/105) | 0.613 | 1.025 |
| **İkinci yarı OOS (hafta 18-34)** | **%47.1 (72/153)** | 0.608 | 1.015 |

## Güven Seviyesi Kırılımı (Tüm Sezon)

| Güven | Doğruluk | |
|---|---:|---|
| HIGH | %60.6 (63/104) | Brier: 0.537 |
| MEDIUM | %39.8 (35/88) | Brier: 0.663 |
| LOW | %36.4 (24/66) | Brier: 0.655 |

## Güven Seviyesi Kırılımı (OOS — İkinci Yarı)

| Güven | Doğruluk | |
|---|---:|---|
| HIGH | %59.4 (38/64) | Brier: 0.551 |
| MEDIUM | %38.8 (19/49) | Brier: 0.657 |
| LOW | %37.5 (15/40) | Brier: 0.64 |

## Sonuç Tipi Kırılımı (Tüm Sezon)

| Gerçek Sonuç | Model Doğruluğu |
|---|---:|
| Ev sahibi kazandı | %55.0 (61/111) |
| Beraberlik | %34.2 (26/76) |
| Deplasman kazandı | %49.3 (35/71) |

## Kümülatif Doğruluk (son 10 hafta)

| Hafta | Kümülatif Doğruluk | Maç |
|---:|---:|---:|
| 25 | %51.4 | 177 |
| 26 | %51.1 | 186 |
| 27 | %51.8 | 195 |
| 28 | %50.0 | 204 |
| 29 | %49.8 | 213 |
| 30 | %49.1 | 222 |
| 31 | %48.1 | 231 |
| 32 | %47.5 | 240 |
| 33 | %47.4 | 249 |
| 34 | %47.3 | 258 |

## Draw Kalibrasyon Karşılaştırması

| | Ham argmax | Kalibre |
|---|---:|---:|
| Tüm sezon doğruluk | %50.4 (130/258) | %47.3 (122/258) |
| OOS ikinci yarı doğruluk | %51.6 (79/153) | %47.1 (72/153) |
| Beraberlik doğruluğu (tüm sezon) | %0.0 (0/76) | %34.2 (26/76) |
| Ev sahibi doğruluğu | %73.0 (81/111) | %55.0 (61/111) |
| Deplasman doğruluğu | %69.0 (49/71) | %49.3 (35/71) |

## Yorumlama

- Tüm sezon doğruluğu walk-forward kronolojik tahmindir; gelecek sonuçlar o anda görülmüyor.
- Hafta 18+ (ikinci yarı OOS) gerçek bağımsız test penceresine en yakın ölçüm.
- Hiperparametreler (K faktör, blend oranı) bu sezon verisine göre ayarlanmadı; genel futbol pratiğine dayanıyor.
- Draw kalibrasyon eşikleri: min draw_p=0.26, max gap=0.18, boost=0.12 (draw_calibrated_prediction).
- Canlı kullanım için: HIGH güven → güvenilir sinyal, LOW güven → bilgi amaçlı.