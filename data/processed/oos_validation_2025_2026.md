# Out-of-Sample Validasyon Raporu — 2025-2026

Split: Hafta 1-17 birikimli tarih, Hafta 18+ bağımsız test.
_Not: Walk-forward kronolojik backtest. Her tahmin yalnızca önceki maçların birikimiyle yapılır. Hafta 1-17 = ısınma + ilk yarı; hafta 18-34 = bağımsız test penceresi._

## Özet

| Dönem | Doğruluk | Brier | Log Loss |
|---|---:|---:|---:|
| Tüm sezon | %50.4 (130/258) | 0.607 | 1.015 |
| İlk yarı (hafta 1-17) | %50.5 (53/105) | 0.614 | 1.028 |
| **İkinci yarı OOS (hafta 18-34)** | **%50.3 (77/153)** | 0.602 | 1.007 |

## Güven Seviyesi Kırılımı (Tüm Sezon)

| Güven | Doğruluk | |
|---|---:|---|
| HIGH | %61.9 (52/84) | Brier: 0.53 |
| MEDIUM | %48.9 (45/92) | Brier: 0.625 |
| LOW | %40.2 (33/82) | Brier: 0.665 |

## Güven Seviyesi Kırılımı (OOS — İkinci Yarı)

| Güven | Doğruluk | |
|---|---:|---|
| HIGH | %60.4 (29/48) | Brier: 0.547 |
| MEDIUM | %50.9 (27/53) | Brier: 0.597 |
| LOW | %40.4 (21/52) | Brier: 0.657 |

## Sonuç Tipi Kırılımı (Tüm Sezon)

| Gerçek Sonuç | Model Doğruluğu |
|---|---:|
| Ev sahibi kazandı | %55.9 (62/111) |
| Beraberlik | %40.8 (31/76) |
| Deplasman kazandı | %52.1 (37/71) |

## Kümülatif Doğruluk (son 10 hafta)

| Hafta | Kümülatif Doğruluk | Maç |
|---:|---:|---:|
| 25 | %53.7 | 177 |
| 26 | %52.7 | 186 |
| 27 | %52.8 | 195 |
| 28 | %52.0 | 204 |
| 29 | %52.6 | 213 |
| 30 | %51.8 | 222 |
| 31 | %51.1 | 231 |
| 32 | %51.7 | 240 |
| 33 | %51.8 | 249 |
| 34 | %50.4 | 258 |

## Draw Kalibrasyon Karşılaştırması

| | Ham argmax | Kalibre |
|---|---:|---:|
| Tüm sezon doğruluk | %51.2 (132/258) | %50.4 (130/258) |
| OOS ikinci yarı doğruluk | %53.6 (82/153) | %50.3 (77/153) |
| Beraberlik doğruluğu (tüm sezon) | %0.0 (0/76) | %40.8 (31/76) |
| Ev sahibi doğruluğu | %73.0 (81/111) | %55.9 (62/111) |
| Deplasman doğruluğu | %71.8 (51/71) | %52.1 (37/71) |

## Yorumlama

- Tüm sezon doğruluğu walk-forward kronolojik tahmindir; gelecek sonuçlar o anda görülmüyor.
- Hafta 18+ (ikinci yarı OOS) gerçek bağımsız test penceresine en yakın ölçüm.
- Hiperparametreler (K faktör, blend oranı) bu sezon verisine göre ayarlanmadı; genel futbol pratiğine dayanıyor.
- Draw kalibrasyon eşikleri: min draw_p=0.26, max gap=0.18, boost=0.12 (draw_calibrated_prediction).
- Canlı kullanım için: HIGH güven → güvenilir sinyal, LOW güven → bilgi amaçlı.