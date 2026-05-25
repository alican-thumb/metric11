# Out-of-Sample Validasyon Raporu — 2025-2026

Split: Hafta 1-17 birikimli tarih, Hafta 18+ bağımsız test.
_Not: Walk-forward kronolojik backtest. Her tahmin yalnızca önceki maçların birikimiyle yapılır. Hafta 1-17 = ısınma + ilk yarı; hafta 18-34 = bağımsız test penceresi._

## Özet

| Dönem | Doğruluk | Brier | Log Loss |
|---|---:|---:|---:|
| Tüm sezon | %50.8 (131/258) | 0.607 | 1.015 |
| İlk yarı (hafta 1-17) | %46.7 (49/105) | 0.614 | 1.028 |
| **İkinci yarı OOS (hafta 18-34)** | **%53.6 (82/153)** | 0.602 | 1.007 |

## Güven Seviyesi Kırılımı (Tüm Sezon)

| Güven | Doğruluk | |
|---|---:|---|
| HIGH | %61.9 (52/84) | Brier: 0.53 |
| MEDIUM | %51.1 (47/92) | Brier: 0.625 |
| LOW | %39.0 (32/82) | Brier: 0.665 |

## Güven Seviyesi Kırılımı (OOS — İkinci Yarı)

| Güven | Doğruluk | |
|---|---:|---|
| HIGH | %60.4 (29/48) | Brier: 0.547 |
| MEDIUM | %56.6 (30/53) | Brier: 0.597 |
| LOW | %44.2 (23/52) | Brier: 0.657 |

## Sonuç Tipi Kırılımı (Tüm Sezon)

| Gerçek Sonuç | Model Doğruluğu |
|---|---:|
| Ev sahibi kazandı | %69.4 (77/111) |
| Beraberlik | %7.9 (6/76) |
| Deplasman kazandı | %67.6 (48/71) |

## Kümülatif Doğruluk (son 10 hafta)

| Hafta | Kümülatif Doğruluk | Maç |
|---:|---:|---:|
| 25 | %50.3 | 177 |
| 26 | %50.5 | 186 |
| 27 | %51.8 | 195 |
| 28 | %51.5 | 204 |
| 29 | %52.1 | 213 |
| 30 | %51.8 | 222 |
| 31 | %51.5 | 231 |
| 32 | %52.1 | 240 |
| 33 | %52.2 | 249 |
| 34 | %50.8 | 258 |

## Draw Kalibrasyon Karşılaştırması

| | Ham argmax | Kalibre |
|---|---:|---:|
| Tüm sezon doğruluk | %51.2 (132/258) | %50.8 (131/258) |
| OOS ikinci yarı doğruluk | %53.6 (82/153) | %53.6 (82/153) |
| Beraberlik doğruluğu (tüm sezon) | %0.0 (0/76) | %7.9 (6/76) |
| Ev sahibi doğruluğu | %73.0 (81/111) | %69.4 (77/111) |
| Deplasman doğruluğu | %71.8 (51/71) | %67.6 (48/71) |

## Yorumlama

- Tüm sezon doğruluğu walk-forward kronolojik tahmindir; gelecek sonuçlar o anda görülmüyor.
- Hafta 18+ (ikinci yarı OOS) gerçek bağımsız test penceresine en yakın ölçüm.
- Hiperparametreler (K faktör, blend oranı) bu sezon verisine göre ayarlanmadı; genel futbol pratiğine dayanıyor.
- Draw kalibrasyon eşikleri: min draw_p=0.27, max gap=0.12 (draw_calibrated_prediction).
- Canlı kullanım için: HIGH güven → güvenilir sinyal, LOW güven → bilgi amaçlı.