# Out-of-Sample Validasyon Raporu — 2025-2026

Split: Hafta 1-17 birikimli tarih, Hafta 18+ bağımsız test.
_Not: Walk-forward kronolojik backtest. Her tahmin yalnızca önceki maçların birikimiyle yapılır. Hafta 1-17 = ısınma + ilk yarı; hafta 18-34 = bağımsız test penceresi._

## Özet

| Dönem | Doğruluk | Brier | Log Loss |
|---|---:|---:|---:|
| Tüm sezon | %51.6 (133/258) | 0.61 | 1.019 |
| İlk yarı (hafta 1-17) | %49.5 (52/105) | 0.613 | 1.025 |
| **İkinci yarı OOS (hafta 18-34)** | **%52.9 (81/153)** | 0.608 | 1.015 |

## Güven Seviyesi Kırılımı (Tüm Sezon)

| Güven | Doğruluk | |
|---|---:|---|
| HIGH | %60.6 (63/104) | Brier: 0.537 |
| MEDIUM | %42.0 (37/88) | Brier: 0.663 |
| LOW | %50.0 (33/66) | Brier: 0.655 |

## Güven Seviyesi Kırılımı (OOS — İkinci Yarı)

| Güven | Doğruluk | |
|---|---:|---|
| HIGH | %59.4 (38/64) | Brier: 0.551 |
| MEDIUM | %42.9 (21/49) | Brier: 0.657 |
| LOW | %55.0 (22/40) | Brier: 0.64 |

## Sonuç Tipi Kırılımı (Tüm Sezon)

| Gerçek Sonuç | Model Doğruluğu |
|---|---:|
| Ev sahibi kazandı | %66.7 (74/111) |
| Beraberlik | %18.4 (14/76) |
| Deplasman kazandı | %63.4 (45/71) |

## Kümülatif Doğruluk (son 10 hafta)

| Hafta | Kümülatif Doğruluk | Maç |
|---:|---:|---:|
| 25 | %53.1 | 177 |
| 26 | %53.8 | 186 |
| 27 | %54.4 | 195 |
| 28 | %53.4 | 204 |
| 29 | %54.0 | 213 |
| 30 | %53.2 | 222 |
| 31 | %52.4 | 231 |
| 32 | %52.5 | 240 |
| 33 | %52.2 | 249 |
| 34 | %51.6 | 258 |

## Draw Kalibrasyon Karşılaştırması

| | Ham argmax | Kalibre |
|---|---:|---:|
| Tüm sezon doğruluk | %50.4 (130/258) | %51.6 (133/258) |
| OOS ikinci yarı doğruluk | %51.6 (79/153) | %52.9 (81/153) |
| Beraberlik doğruluğu (tüm sezon) | %0.0 (0/76) | %18.4 (14/76) |
| Ev sahibi doğruluğu | %73.0 (81/111) | %66.7 (74/111) |
| Deplasman doğruluğu | %69.0 (49/71) | %63.4 (45/71) |

## Yorumlama

- Tüm sezon doğruluğu walk-forward kronolojik tahmindir; gelecek sonuçlar o anda görülmüyor.
- Hafta 18+ (ikinci yarı OOS) gerçek bağımsız test penceresine en yakın ölçüm.
- Hiperparametreler (K faktör, blend oranı) bu sezon verisine göre ayarlanmadı; genel futbol pratiğine dayanıyor.
- Draw kalibrasyon eşikleri: min draw_p=0.28, max gap=0.18, boost=0.0 (draw_calibrated_prediction).
- Canlı kullanım için: HIGH güven → güvenilir sinyal, LOW güven → bilgi amaçlı.