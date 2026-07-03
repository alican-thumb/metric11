# Lig Geneli Piyasa Değeri / Model Denetimi

- Sezon: 2025-2026
- Transfermarkt kulüp kapsamı: 18/18
- Kadro oyuncusu: 816
- Toplam piyasa değeri: €1,697,785,000
- Maç kapsamı: 177/258 (%69)
- Lig modeli doğruluğu: %46
- Sabit draw-band 0.20 piyasa değeri baseline doğruluğu: %47
- Sabit draw-band 0.20 beraberlik yakalama: %16
- Model / piyasa baseline anlaşmazlığı: 73
- Anlaşmazlıklarda model doğruluğu: %37
- Anlaşmazlıklarda piyasa baseline doğruluğu: %41
- Belirgin değer farkında model hatası: 46

## Kullanım Sınırı

- Retrospektif tanısal benchmark; üretim tahmin girdisi değildir.
- Piyasa değeri snapshot'ı maç tarihlerinden sonraki değer/transfer güncellemelerini içerebilir; ileriye dönük model başarısı iddiası kurulamaz.
- Bu rapor market-value özelliğini modele eklemeden önce geçmiş dönemde nerede açıklayıcı olabileceğini ölçer.

## Eşik Karşılaştırması

| Draw band | Doğruluk | Beraberlik precision | Beraberlik recall | Tahmin dağılımı |
| ---: | ---: | ---: | ---: | --- |
| 0.00 | %49 | %0 | %0 | {'away': 91, 'home': 85, 'draw': 1} |
| 0.10 | %48 | %10 | %2 | {'away': 87, 'home': 80, 'draw': 10} |
| 0.20 | %47 | %28 | %16 | {'away': 76, 'home': 69, 'draw': 32} |
| 0.30 | %49 | %32 | %23 | {'away': 71, 'home': 66, 'draw': 40} |
| 0.40 | %47 | %29 | %30 | {'draw': 58, 'home': 57, 'away': 62} |

## Takım Bazlı Karşılaştırma

| Takım | Değer | Maç | Model | Değer baseline |
| --- | ---: | ---: | ---: | ---: |
| GALATASARAY A.Ş. | €363,750,000 | 24 | %54 | %58 |
| FENERBAHÇE A.Ş. | €328,700,000 | 23 | %65 | %56 |
| BEŞİKTAŞ A.Ş. | €273,350,000 | 24 | %46 | %46 |
| TRABZONSPOR A.Ş. | €169,600,000 | 24 | %42 | %50 |
| GÖZTEPE A.Ş. | €83,300,000 | 24 | %58 | %42 |
| RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ | €75,475,000 | 25 | %60 | %56 |
| SAMSUNSPOR A.Ş. | €70,050,000 | 24 | %46 | %33 |
| ÇAYKUR RİZESPOR A.Ş. | €48,025,000 | 23 | %48 | %48 |
| TÜMOSAN KONYASPOR | €41,975,000 | 23 | %35 | %65 |
| CORENDON ALANYASPOR | €41,700,000 | 22 | %36 | %41 |
| İKAS EYÜPSPOR | €39,825,000 | 23 | %30 | %39 |
| GAZİANTEP FUTBOL KULÜBÜ A.Ş. | €34,850,000 | 23 | %56 | %52 |
| KASIMPAŞA A.Ş. | €34,850,000 | 25 | %32 | %40 |
| KOCAELİSPOR | €28,500,000 | 23 | %35 | %35 |
| GENÇLERBİRLİĞİ | €28,210,000 | 24 | %33 | %42 |

## En Büyük Anlaşmazlıklar

- 26.10.2025 - 20:00 | KASIMPAŞA A.Ş. - BEŞİKTAŞ A.Ş. (1-1) | model=X baseline=Dep gerçek=X | değer farkı=€-238.5m
- 1.05.2026 - 20:00 | GAZİANTEP FUTBOL KULÜBÜ A.Ş. - BEŞİKTAŞ A.Ş. (0-2) | model=X baseline=Dep gerçek=Dep | değer farkı=€-238.5m
- 9.05.2026 - 20:00 | TÜMOSAN KONYASPOR - FENERBAHÇE A.Ş. (0-3) | model=Ev baseline=Dep gerçek=Dep | değer farkı=€-286.73m
- 22.10.2025 - 20:00 | TÜMOSAN KONYASPOR - BEŞİKTAŞ A.Ş. (0-2) | model=Ev baseline=Dep gerçek=Dep | değer farkı=€-231.38m
- 18.01.2026 - 17:00 | KOCAELİSPOR - TRABZONSPOR A.Ş. (1-2) | model=X baseline=Dep gerçek=Dep | değer farkı=€-141.1m
- 5.12.2025 - 20:03 | GALATASARAY A.Ş. - SAMSUNSPOR A.Ş. (3-2) | model=X baseline=Ev gerçek=Ev | değer farkı=€293.7m
- 5.10.2025 - 20:00 | SAMSUNSPOR A.Ş. - FENERBAHÇE A.Ş. (0-0) | model=X baseline=Dep gerçek=X | değer farkı=€-258.65m
- 27.04.2026 - 20:00 | TÜMOSAN KONYASPOR - TRABZONSPOR A.Ş. (2-1) | model=X baseline=Dep gerçek=Ev | değer farkı=€-127.62m
- 15.02.2026 - 20:00 | RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ - BEŞİKTAŞ A.Ş. (2-3) | model=Ev baseline=Dep gerçek=Dep | değer farkı=€-197.88m
- 4.04.2026 - 14:30 | GENÇLERBİRLİĞİ - GÖZTEPE A.Ş. (0-2) | model=X baseline=Dep gerçek=Dep | değer farkı=€-55.09m