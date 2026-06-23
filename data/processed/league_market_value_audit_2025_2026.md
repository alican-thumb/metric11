# Lig Geneli Piyasa Değeri / Model Denetimi

- Sezon: 2025-2026
- Transfermarkt kulüp kapsamı: 16/18
- Kadro oyuncusu: 452
- Toplam piyasa değeri: €1,243,675,000
- Maç kapsamı: 131/258 (%51)
- Lig modeli doğruluğu: %46
- Sabit draw-band 0.20 piyasa değeri baseline doğruluğu: %49
- Sabit draw-band 0.20 beraberlik yakalama: %5
- Model / piyasa baseline anlaşmazlığı: 53
- Anlaşmazlıklarda model doğruluğu: %32
- Anlaşmazlıklarda piyasa baseline doğruluğu: %43
- Belirgin değer farkında model hatası: 37

## Kullanım Sınırı

- Retrospektif tanısal benchmark; üretim tahmin girdisi değildir.
- Piyasa değeri snapshot'ı maç tarihlerinden sonraki değer/transfer güncellemelerini içerebilir; ileriye dönük model başarısı iddiası kurulamaz.
- Bu rapor market-value özelliğini modele eklemeden önce geçmiş dönemde nerede açıklayıcı olabileceğini ölçer.

## Eşik Karşılaştırması

| Draw band | Doğruluk | Beraberlik precision | Beraberlik recall | Tahmin dağılımı |
| ---: | ---: | ---: | ---: | --- |
| 0.00 | %50 | %0 | %0 | {'home': 63, 'away': 68} |
| 0.10 | %49 | %20 | %2 | {'home': 61, 'away': 65, 'draw': 5} |
| 0.20 | %49 | %20 | %5 | {'home': 59, 'away': 62, 'draw': 10} |
| 0.30 | %52 | %40 | %20 | {'home': 55, 'away': 56, 'draw': 20} |
| 0.40 | %50 | %38 | %29 | {'home': 49, 'away': 50, 'draw': 32} |

## Takım Bazlı Karşılaştırma

| Takım | Değer | Maç | Model | Değer baseline |
| --- | ---: | ---: | ---: | ---: |
| GALATASARAY A.Ş. | €336,650,000 | 20 | %45 | %50 |
| FENERBAHÇE A.Ş. | €240,800,000 | 20 | %65 | %65 |
| BEŞİKTAŞ A.Ş. | €176,000,000 | 22 | %50 | %55 |
| TRABZONSPOR A.Ş. | €129,550,000 | 20 | %50 | %55 |
| GÖZTEPE A.Ş. | €65,750,000 | 20 | %55 | %50 |
| SAMSUNSPOR A.Ş. | €56,100,000 | 20 | %50 | %35 |
| ÇAYKUR RİZESPOR A.Ş. | €39,750,000 | 20 | %45 | %55 |
| TÜMOSAN KONYASPOR | €39,300,000 | 20 | %25 | %50 |
| KASIMPAŞA A.Ş. | €30,800,000 | 21 | %33 | %38 |
| GAZİANTEP FUTBOL KULÜBÜ A.Ş. | €29,800,000 | 19 | %58 | %37 |
| GENÇLERBİRLİĞİ | €26,250,000 | 20 | %30 | %50 |
| KOCAELİSPOR | €24,150,000 | 19 | %42 | %42 |
| İKAS EYÜPSPOR | €17,150,000 | 21 | %29 | %52 |

## En Büyük Anlaşmazlıklar

- 9.05.2026 - 20:00 | TÜMOSAN KONYASPOR - FENERBAHÇE A.Ş. (0-3) | model=Ev baseline=Dep gerçek=Dep | değer farkı=€-201.5m
- 5.12.2025 - 20:03 | GALATASARAY A.Ş. - SAMSUNSPOR A.Ş. (3-2) | model=X baseline=Ev gerçek=Ev | değer farkı=€280.55m
- 1.05.2026 - 20:00 | GAZİANTEP FUTBOL KULÜBÜ A.Ş. - BEŞİKTAŞ A.Ş. (0-2) | model=X baseline=Dep gerçek=Dep | değer farkı=€-146.2m
- 26.10.2025 - 20:00 | KASIMPAŞA A.Ş. - BEŞİKTAŞ A.Ş. (1-1) | model=X baseline=Dep gerçek=X | değer farkı=€-145.2m
- 18.01.2026 - 17:00 | KOCAELİSPOR - TRABZONSPOR A.Ş. (1-2) | model=X baseline=Dep gerçek=Dep | değer farkı=€-105.4m
- 22.10.2025 - 20:00 | TÜMOSAN KONYASPOR - BEŞİKTAŞ A.Ş. (0-2) | model=Ev baseline=Dep gerçek=Dep | değer farkı=€-136.7m
- 5.10.2025 - 20:00 | SAMSUNSPOR A.Ş. - FENERBAHÇE A.Ş. (0-0) | model=X baseline=Dep gerçek=X | değer farkı=€-184.7m
- 27.04.2026 - 20:00 | TÜMOSAN KONYASPOR - TRABZONSPOR A.Ş. (2-1) | model=X baseline=Dep gerçek=Ev | değer farkı=€-90.25m
- 13.04.2026 - 20:00 | İKAS EYÜPSPOR - SAMSUNSPOR A.Ş. (1-2) | model=X baseline=Dep gerçek=Dep | değer farkı=€-38.95m
- 23.11.2025 - 14:30 | GÖZTEPE A.Ş. - KOCAELİSPOR (0-0) | model=X baseline=Ev gerçek=X | değer farkı=€41.6m