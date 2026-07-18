# Tahmin Hata Analizi

- Maç tahmini: 19/29 (%66)
- Hatalı maç: 10
- Gol adayı Top 3 kaçan: 10
- Gol adayı Top 5 kaçan: 6
- Gol adayı Top 8 kaçan: 4
- Gol adayı Top 10 kaçan: 3

## Hata Tipleri

- missed_draw: 7
- big_match_miss: 1
- overconfident_miss: 6
- overrated_opponent: 2
- overrated_besiktas: 7

## Öncelikli İyileştirmeler

- HIGH | Beraberlik riski: Ana olasılığı bozmadan beraberlik risk katmanını UI'da daha görünür yap; xG farkı dar ve güç farkı düşük maçları 'korumalı senaryo' diye etiketle.
- HIGH | Büyük maç modeli: Derbi/büyük maçlar için ayrı katsayı eğit; hakem kart profili, önceki büyük maç oyuncu kart/gol sinyali ve kadro denetimi etkisini ayrı ölç.
- MEDIUM | Güven kalibrasyonu: Yüksek olasılık verilen ama yanlış çıkan maçlarda confidence seviyesini düşüren risk bayrakları ekle.
- MEDIUM | Gol adayı: Defans, duran top ve sonradan giren oyuncu gol olasılığı için ayrı aday havuzu üret; mevcut model ilk 11/gol formuna fazla bağlı.

## Kritik Kaçan Maçlar

- 4.10.2025 - 20:00 | GALATASARAY A.Ş. - BEŞİKTAŞ A.Ş. | skor 1-1 | tahmin=opponent_win gerçek=draw | Beraberlik riski ana tahminin gerisinde kalmış.
- 18.10.2025 - 17:03 | BEŞİKTAŞ A.Ş. - GENÇLERBİRLİĞİ | skor 1-2 | tahmin=target_win gerçek=opponent_win | Beşiktaş form veya güç sinyali fazla pozitif ağırlık almış.
- 26.10.2025 - 20:00 | KASIMPAŞA A.Ş. - BEŞİKTAŞ A.Ş. | skor 1-1 | tahmin=target_win gerçek=draw | Beraberlik riski ana tahminin gerisinde kalmış.
- 8.12.2025 - 20:00 | BEŞİKTAŞ A.Ş. - GAZİANTEP FUTBOL KULÜBÜ A.Ş. | skor 2-2 | tahmin=target_win gerçek=draw | Beraberlik riski ana tahminin gerisinde kalmış.
- 26.01.2026 - 20:00 | İKAS EYÜPSPOR - BEŞİKTAŞ A.Ş. | skor 2-2 | tahmin=target_win gerçek=draw | Beraberlik riski ana tahminin gerisinde kalmış.
- 8.02.2026 - 20:00 | BEŞİKTAŞ A.Ş. - CORENDON ALANYASPOR | skor 2-2 | tahmin=target_win gerçek=draw | Beraberlik riski ana tahminin gerisinde kalmış.
- 15.02.2026 - 20:00 | RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ - BEŞİKTAŞ A.Ş. | skor 2-3 | tahmin=opponent_win gerçek=target_win | Rakip güç/form sinyali fazla pozitif ağırlık almış.
- 19.04.2026 - 17:00 | SAMSUNSPOR A.Ş. - BEŞİKTAŞ A.Ş. | skor 2-1 | tahmin=draw gerçek=opponent_win | Düşük marjlı hata.
- 27.04.2026 - 20:00 | BEŞİKTAŞ A.Ş. - MISIRLI.COM.TR FATİH KARAGÜMRÜK | skor 0-0 | tahmin=target_win gerçek=draw | Beraberlik riski ana tahminin gerisinde kalmış.
- 15.05.2026 - 20:00 | ÇAYKUR RİZESPOR A.Ş. - BEŞİKTAŞ A.Ş. | skor 2-2 | tahmin=target_win gerçek=draw | Beraberlik riski ana tahminin gerisinde kalmış.