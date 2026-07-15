# Lig Geneli Piyasa Değeri / Model Denetimi

- Sezon: 2025-2026
- Transfermarkt kulüp kapsamı: 15/18
- Kadro oyuncusu: 424
- Toplam piyasa değeri: €1,318,950,000
- Maç kapsamı: 177/258 (%69)
- Lig modeli doğruluğu: %52
- Sabit draw-band 0.20 piyasa değeri baseline doğruluğu: %50
- Sabit draw-band 0.20 beraberlik yakalama: %9
- Model / piyasa baseline anlaşmazlığı: 55
- Anlaşmazlıklarda model doğruluğu: %40
- Anlaşmazlıklarda piyasa baseline doğruluğu: %33
- Belirgin değer farkında model hatası: 40

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
| GALATASARAY A.Ş. | €336,650,000 | 24 | %58 | %58 |
| FENERBAHÇE A.Ş. | €240,800,000 | 23 | %65 | %65 |
| BEŞİKTAŞ A.Ş. | €176,000,000 | 24 | %46 | %54 |
| TRABZONSPOR A.Ş. | €129,550,000 | 24 | %54 | %50 |
| RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ | €73,100,000 | 25 | %68 | %64 |
| GÖZTEPE A.Ş. | €65,750,000 | 24 | %62 | %42 |
| SAMSUNSPOR A.Ş. | €56,100,000 | 24 | %62 | %42 |
| ÇAYKUR RİZESPOR A.Ş. | €39,750,000 | 23 | %48 | %52 |
| TÜMOSAN KONYASPOR | €39,300,000 | 23 | %39 | %48 |
| CORENDON ALANYASPOR | €33,800,000 | 22 | %41 | %41 |
| KASIMPAŞA A.Ş. | €30,800,000 | 25 | %36 | %40 |
| GAZİANTEP FUTBOL KULÜBÜ A.Ş. | €29,800,000 | 23 | %56 | %48 |
| GENÇLERBİRLİĞİ | €26,250,000 | 24 | %46 | %46 |
| KOCAELİSPOR | €24,150,000 | 23 | %52 | %44 |
| İKAS EYÜPSPOR | €17,150,000 | 23 | %44 | %52 |

## En Büyük Anlaşmazlıklar

- 9.05.2026 - 20:00 | TÜMOSAN KONYASPOR - FENERBAHÇE A.Ş. (0-3) | model=Ev baseline=Dep gerçek=Dep | değer farkı=€-201.5m
- 22.10.2025 - 20:00 | TÜMOSAN KONYASPOR - BEŞİKTAŞ A.Ş. (0-2) | model=Ev baseline=Dep gerçek=Dep | değer farkı=€-136.7m
- 20.09.2025 - 20:00 | TRABZONSPOR A.Ş. - GAZİANTEP FUTBOL KULÜBÜ A.Ş. (1-1) | model=X baseline=Ev gerçek=X | değer farkı=€99.75m
- 5.10.2025 - 20:00 | SAMSUNSPOR A.Ş. - FENERBAHÇE A.Ş. (0-0) | model=X baseline=Dep gerçek=X | değer farkı=€-184.7m
- 23.11.2025 - 14:30 | GÖZTEPE A.Ş. - KOCAELİSPOR (0-0) | model=X baseline=Ev gerçek=X | değer farkı=€41.6m
- 18.04.2026 - 17:00 | KOCAELİSPOR - GÖZTEPE A.Ş. (1-1) | model=X baseline=Dep gerçek=X | değer farkı=€-41.6m
- 4.04.2026 - 14:30 | GENÇLERBİRLİĞİ - GÖZTEPE A.Ş. (0-2) | model=Ev baseline=Dep gerçek=Dep | değer farkı=€-39.5m
- 15.02.2026 - 20:00 | RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ - BEŞİKTAŞ A.Ş. (2-3) | model=Ev baseline=Dep gerçek=Dep | değer farkı=€-102.9m
- 24.01.2026 - 17:00 | SAMSUNSPOR A.Ş. - KOCAELİSPOR (0-0) | model=X baseline=Ev gerçek=X | değer farkı=€31.95m
- 13.12.2025 - 14:30 | ÇAYKUR RİZESPOR A.Ş. - İKAS EYÜPSPOR (3-0) | model=X baseline=Ev gerçek=Ev | değer farkı=€22.6m