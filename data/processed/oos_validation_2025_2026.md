# Out-of-Sample Validasyon Raporu — 2025-2026

Split: Hafta 1-17 birikimli tarih, Hafta 18+ bağımsız test.
_Not: Walk-forward kronolojik backtest. Her tahmin yalnızca önceki maçların birikimiyle yapılır. Hafta 1-17 = ısınma + ilk yarı; hafta 18-34 = bağımsız test penceresi._

## Özet

| Dönem | Doğruluk | Brier | Log Loss |
|---|---:|---:|---:|
| Tüm sezon | %55.0 (142/258) | 0.6 | 1.005 |
| İlk yarı (hafta 1-17) | %50.5 (53/105) | 0.608 | 1.017 |
| **İkinci yarı OOS (hafta 18-34)** | **%58.2 (89/153)** | 0.595 | 0.996 |

## Güven Seviyesi Kırılımı (Tüm Sezon)

| Güven | Doğruluk | |
|---|---:|---|
| HIGH | %64.0 (57/89) | Brier: 0.516 |
| MEDIUM | %55.3 (47/85) | Brier: 0.619 |
| LOW | %45.2 (38/84) | Brier: 0.67 |

## Güven Seviyesi Kırılımı (OOS — İkinci Yarı)

| Güven | Doğruluk | |
|---|---:|---|
| HIGH | %62.7 (32/51) | Brier: 0.527 |
| MEDIUM | %56.9 (29/51) | Brier: 0.605 |
| LOW | %54.9 (28/51) | Brier: 0.653 |

## Sonuç Tipi Kırılımı (Tüm Sezon)

| Gerçek Sonuç | Model Doğruluğu |
|---|---:|
| Ev sahibi kazandı | %72.1 (80/111) |
| Beraberlik | %17.1 (13/76) |
| Deplasman kazandı | %69.0 (49/71) |

## Kümülatif Doğruluk (son 10 hafta)

| Hafta | Kümülatif Doğruluk | Maç |
|---:|---:|---:|
| 25 | %55.4 | 177 |
| 26 | %55.9 | 186 |
| 27 | %56.9 | 195 |
| 28 | %57.4 | 204 |
| 29 | %57.7 | 213 |
| 30 | %57.2 | 222 |
| 31 | %56.7 | 231 |
| 32 | %56.7 | 240 |
| 33 | %56.6 | 249 |
| 34 | %55.0 | 258 |

## Draw Kalibrasyon Karşılaştırması

| | Ham argmax | Kalibre |
|---|---:|---:|
| Tüm sezon doğruluk | %51.2 (132/258) | %55.0 (142/258) |
| OOS ikinci yarı doğruluk | %53.6 (82/153) | %58.2 (89/153) |
| Beraberlik doğruluğu (tüm sezon) | %0.0 (0/76) | %17.1 (13/76) |
| Ev sahibi doğruluğu | %73.0 (81/111) | %72.1 (80/111) |
| Deplasman doğruluğu | %71.8 (51/71) | %69.0 (49/71) |

## Yorumlama

- Tüm sezon doğruluğu walk-forward kronolojik tahmindir; gelecek sonuçlar o anda görülmüyor.
- Hafta 18+ (ikinci yarı OOS) gerçek bağımsız test penceresine en yakın ölçüm.
- Hiperparametreler (K faktör, blend oranı) bu sezon verisine göre ayarlanmadı; genel futbol pratiğine dayanıyor.
- Draw kalibrasyon eşikleri: min draw_p=0.28, max gap=0.18, boost=0.0 (draw_calibrated_prediction).
- Canlı kullanım için: HIGH güven → güvenilir sinyal, LOW güven → bilgi amaçlı.