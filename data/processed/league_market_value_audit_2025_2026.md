# Lig Geneli Piyasa Değeri / Model Denetimi

- Sezon: 2025-2026
- Transfermarkt kulüp kapsamı: 18/18
- Kadro oyuncusu: 505
- Toplam piyasa değeri: €1,350,025,000
- Maç kapsamı: 177/258 (%69)
- Lig modeli doğruluğu: %46
- Sabit draw-band 0.20 piyasa değeri baseline doğruluğu: %50
- Sabit draw-band 0.20 beraberlik yakalama: %9
- Model / piyasa baseline anlaşmazlığı: 72
- Anlaşmazlıklarda model doğruluğu: %33
- Anlaşmazlıklarda piyasa baseline doğruluğu: %44
- Belirgin değer farkında model hatası: 46

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
| 0.40 | %49 | %35 | %30 | {'home': 63, 'away': 66, 'draw': 48} |

## Takım Bazlı Karşılaştırma

| Takım | Değer | Maç | Model | Değer baseline |
| --- | ---: | ---: | ---: | ---: |
| GALATASARAY A.Ş. | €336,650,000 | 24 | %54 | %58 |
| FENERBAHÇE A.Ş. | €240,800,000 | 23 | %65 | %65 |
| BEŞİKTAŞ A.Ş. | €176,000,000 | 24 | %46 | %54 |
| TRABZONSPOR A.Ş. | €129,550,000 | 24 | %42 | %50 |
| RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ | €73,100,000 | 25 | %60 | %64 |
| GÖZTEPE A.Ş. | €65,750,000 | 24 | %58 | %42 |
| SAMSUNSPOR A.Ş. | €56,100,000 | 24 | %46 | %42 |
| ÇAYKUR RİZESPOR A.Ş. | €39,750,000 | 23 | %48 | %52 |
| TÜMOSAN KONYASPOR | €38,750,000 | 23 | %35 | %48 |
| CORENDON ALANYASPOR | €33,800,000 | 22 | %36 | %41 |
| KASIMPAŞA A.Ş. | €30,800,000 | 25 | %32 | %40 |
| GAZİANTEP FUTBOL KULÜBÜ A.Ş. | €29,800,000 | 23 | %56 | %48 |
| GENÇLERBİRLİĞİ | €26,250,000 | 24 | %33 | %46 |
| KOCAELİSPOR | €24,150,000 | 23 | %35 | %44 |
| İKAS EYÜPSPOR | €17,150,000 | 23 | %30 | %52 |

## En Büyük Anlaşmazlıklar

- 9.05.2026 - 20:00 | TÜMOSAN KONYASPOR - FENERBAHÇE A.Ş. (0-3) | model=Ev baseline=Dep gerçek=Dep | değer farkı=€-202.05m
- 5.12.2025 - 20:03 | GALATASARAY A.Ş. - SAMSUNSPOR A.Ş. (3-2) | model=X baseline=Ev gerçek=Ev | değer farkı=€280.55m
- 1.05.2026 - 20:00 | GAZİANTEP FUTBOL KULÜBÜ A.Ş. - BEŞİKTAŞ A.Ş. (0-2) | model=X baseline=Dep gerçek=Dep | değer farkı=€-146.2m
- 26.10.2025 - 20:00 | KASIMPAŞA A.Ş. - BEŞİKTAŞ A.Ş. (1-1) | model=X baseline=Dep gerçek=X | değer farkı=€-145.2m
- 18.01.2026 - 17:00 | KOCAELİSPOR - TRABZONSPOR A.Ş. (1-2) | model=X baseline=Dep gerçek=Dep | değer farkı=€-105.4m
- 22.10.2025 - 20:00 | TÜMOSAN KONYASPOR - BEŞİKTAŞ A.Ş. (0-2) | model=Ev baseline=Dep gerçek=Dep | değer farkı=€-137.25m
- 5.10.2025 - 20:00 | SAMSUNSPOR A.Ş. - FENERBAHÇE A.Ş. (0-0) | model=X baseline=Dep gerçek=X | değer farkı=€-184.7m
- 27.04.2026 - 20:00 | TÜMOSAN KONYASPOR - TRABZONSPOR A.Ş. (2-1) | model=X baseline=Dep gerçek=Ev | değer farkı=€-90.8m
- 13.04.2026 - 20:00 | İKAS EYÜPSPOR - SAMSUNSPOR A.Ş. (1-2) | model=X baseline=Dep gerçek=Dep | değer farkı=€-38.95m
- 31.10.2025 - 20:00 | RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ - KOCAELİSPOR (1-0) | model=X baseline=Ev gerçek=Ev | değer farkı=€48.95m