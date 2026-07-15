# Lig Geneli Piyasa Değeri / Model Denetimi

- Sezon: 2025-2026
- Transfermarkt kulüp kapsamı: 15/18
- Kadro oyuncusu: 424
- Toplam piyasa değeri: €1,318,950,000
- Maç kapsamı: 177/258 (%69)
- Lig modeli doğruluğu: %47
- Sabit draw-band 0.20 piyasa değeri baseline doğruluğu: %50
- Sabit draw-band 0.20 beraberlik yakalama: %9
- Model / piyasa baseline anlaşmazlığı: 76
- Anlaşmazlıklarda model doğruluğu: %36
- Anlaşmazlıklarda piyasa baseline doğruluğu: %42
- Belirgin değer farkında model hatası: 44

## Kullanım Sınırı

- Retrospektif tanısal benchmark; üretim tahmin girdisi değildir.
- Piyasa değeri snapshot'ı maç tarihlerinden sonraki değer/transfer güncellemelerini içerebilir; ileriye dönük model başarısı iddiası kurulamaz.
- Bu rapor market-value özelliğini modele eklemeden önce geçmiş dönemde nerede açıklayıcı olabileceğini ölçer.

## Eşik Karşılaştırması

| Draw band | Doğruluk | Beraberlik precision | Beraberlik recall | Tahmin dağılımı |
| ---: | ---: | ---: | ---: | --- |
| 0.00 | %49 | %0 | %0 | {'home': 85, 'away': 92} |
| 0.10 | %49 | %14 | %2 | {'home': 82, 'away': 88, 'draw': 7} |
| 0.20 | %50 | %28 | %9 | {'home': 77, 'away': 82, 'draw': 18} |
| 0.30 | %52 | %41 | %23 | {'home': 71, 'away': 74, 'draw': 32} |
| 0.40 | %50 | %37 | %30 | {'home': 64, 'away': 67, 'draw': 46} |

## Takım Bazlı Karşılaştırma

| Takım | Değer | Maç | Model | Değer baseline |
| --- | ---: | ---: | ---: | ---: |
| GALATASARAY A.Ş. | €336,650,000 | 24 | %50 | %58 |
| FENERBAHÇE A.Ş. | €240,800,000 | 23 | %52 | %65 |
| BEŞİKTAŞ A.Ş. | €176,000,000 | 24 | %42 | %54 |
| TRABZONSPOR A.Ş. | €129,550,000 | 24 | %46 | %50 |
| RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ | €73,100,000 | 25 | %60 | %64 |
| GÖZTEPE A.Ş. | €65,750,000 | 24 | %58 | %42 |
| SAMSUNSPOR A.Ş. | €56,100,000 | 24 | %58 | %42 |
| ÇAYKUR RİZESPOR A.Ş. | €39,750,000 | 23 | %48 | %52 |
| TÜMOSAN KONYASPOR | €39,300,000 | 23 | %35 | %48 |
| CORENDON ALANYASPOR | €33,800,000 | 22 | %46 | %41 |
| KASIMPAŞA A.Ş. | €30,800,000 | 25 | %28 | %40 |
| GAZİANTEP FUTBOL KULÜBÜ A.Ş. | €29,800,000 | 23 | %56 | %48 |
| GENÇLERBİRLİĞİ | €26,250,000 | 24 | %50 | %46 |
| KOCAELİSPOR | €24,150,000 | 23 | %39 | %44 |
| İKAS EYÜPSPOR | €17,150,000 | 23 | %35 | %52 |

## En Büyük Anlaşmazlıklar

- 9.05.2026 - 20:00 | TÜMOSAN KONYASPOR - FENERBAHÇE A.Ş. (0-3) | model=Ev baseline=Dep gerçek=Dep | değer farkı=€-201.5m
- 5.12.2025 - 20:03 | GALATASARAY A.Ş. - SAMSUNSPOR A.Ş. (3-2) | model=X baseline=Ev gerçek=Ev | değer farkı=€280.55m
- 1.05.2026 - 20:00 | GAZİANTEP FUTBOL KULÜBÜ A.Ş. - BEŞİKTAŞ A.Ş. (0-2) | model=X baseline=Dep gerçek=Dep | değer farkı=€-146.2m
- 18.01.2026 - 17:00 | KOCAELİSPOR - TRABZONSPOR A.Ş. (1-2) | model=X baseline=Dep gerçek=Dep | değer farkı=€-105.4m
- 22.10.2025 - 20:00 | TÜMOSAN KONYASPOR - BEŞİKTAŞ A.Ş. (0-2) | model=Ev baseline=Dep gerçek=Dep | değer farkı=€-136.7m
- 15.05.2026 - 20:00 | ÇAYKUR RİZESPOR A.Ş. - BEŞİKTAŞ A.Ş. (2-2) | model=X baseline=Dep gerçek=X | değer farkı=€-136.25m
- 20.09.2025 - 20:00 | TRABZONSPOR A.Ş. - GAZİANTEP FUTBOL KULÜBÜ A.Ş. (1-1) | model=X baseline=Ev gerçek=X | değer farkı=€99.75m
- 5.10.2025 - 20:00 | SAMSUNSPOR A.Ş. - FENERBAHÇE A.Ş. (0-0) | model=X baseline=Dep gerçek=X | değer farkı=€-184.7m
- 27.04.2026 - 20:00 | TÜMOSAN KONYASPOR - TRABZONSPOR A.Ş. (2-1) | model=X baseline=Dep gerçek=Ev | değer farkı=€-90.25m
- 13.04.2026 - 20:00 | İKAS EYÜPSPOR - SAMSUNSPOR A.Ş. (1-2) | model=X baseline=Dep gerçek=Dep | değer farkı=€-38.95m