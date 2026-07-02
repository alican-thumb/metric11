# Lig Geneli Piyasa Değeri / Model Denetimi

- Sezon: 2025-2026
- Transfermarkt kulüp kapsamı: 17/18
- Kadro oyuncusu: 777
- Toplam piyasa değeri: €1,669,285,000
- Maç kapsamı: 154/258 (%60)
- Lig modeli doğruluğu: %46
- Sabit draw-band 0.20 piyasa değeri baseline doğruluğu: %49
- Sabit draw-band 0.20 beraberlik yakalama: %18
- Model / piyasa baseline anlaşmazlığı: 60
- Anlaşmazlıklarda model doğruluğu: %37
- Anlaşmazlıklarda piyasa baseline doğruluğu: %42
- Belirgin değer farkında model hatası: 41

## Kullanım Sınırı

- Retrospektif tanısal benchmark; üretim tahmin girdisi değildir.
- Piyasa değeri snapshot'ı maç tarihlerinden sonraki değer/transfer güncellemelerini içerebilir; ileriye dönük model başarısı iddiası kurulamaz.
- Bu rapor market-value özelliğini modele eklemeden önce geçmiş dönemde nerede açıklayıcı olabileceğini ölçer.

## Eşik Karşılaştırması

| Draw band | Doğruluk | Beraberlik precision | Beraberlik recall | Tahmin dağılımı |
| ---: | ---: | ---: | ---: | --- |
| 0.00 | %51 | %0 | %0 | {'away': 79, 'home': 74, 'draw': 1} |
| 0.10 | %49 | %12 | %2 | {'away': 76, 'home': 70, 'draw': 8} |
| 0.20 | %49 | %30 | %18 | {'away': 65, 'home': 59, 'draw': 30} |
| 0.30 | %49 | %31 | %22 | {'away': 62, 'home': 57, 'draw': 35} |
| 0.40 | %49 | %32 | %31 | {'draw': 47, 'home': 51, 'away': 56} |

## Takım Bazlı Karşılaştırma

| Takım | Değer | Maç | Model | Değer baseline |
| --- | ---: | ---: | ---: | ---: |
| GALATASARAY A.Ş. | €363,750,000 | 22 | %59 | %64 |
| FENERBAHÇE A.Ş. | €328,700,000 | 22 | %64 | %55 |
| BEŞİKTAŞ A.Ş. | €273,350,000 | 22 | %41 | %41 |
| TRABZONSPOR A.Ş. | €169,600,000 | 23 | %44 | %48 |
| GÖZTEPE A.Ş. | €83,300,000 | 22 | %55 | %46 |
| RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ | €75,475,000 | 23 | %65 | %56 |
| SAMSUNSPOR A.Ş. | €70,050,000 | 23 | %44 | %35 |
| ÇAYKUR RİZESPOR A.Ş. | €48,025,000 | 22 | %50 | %46 |
| TÜMOSAN KONYASPOR | €41,975,000 | 21 | %38 | %67 |
| CORENDON ALANYASPOR | €41,700,000 | 20 | %40 | %40 |
| İKAS EYÜPSPOR | €39,825,000 | 21 | %33 | %43 |
| GAZİANTEP FUTBOL KULÜBÜ A.Ş. | €34,850,000 | 22 | %55 | %55 |
| KASIMPAŞA A.Ş. | €34,850,000 | 23 | %30 | %44 |
| GENÇLERBİRLİĞİ | €28,210,000 | 22 | %36 | %46 |

## En Büyük Anlaşmazlıklar

- 26.10.2025 - 20:00 | KASIMPAŞA A.Ş. - BEŞİKTAŞ A.Ş. (1-1) | model=X baseline=Dep gerçek=X | değer farkı=€-238.5m
- 1.05.2026 - 20:00 | GAZİANTEP FUTBOL KULÜBÜ A.Ş. - BEŞİKTAŞ A.Ş. (0-2) | model=X baseline=Dep gerçek=Dep | değer farkı=€-238.5m
- 9.05.2026 - 20:00 | TÜMOSAN KONYASPOR - FENERBAHÇE A.Ş. (0-3) | model=Ev baseline=Dep gerçek=Dep | değer farkı=€-286.73m
- 22.10.2025 - 20:00 | TÜMOSAN KONYASPOR - BEŞİKTAŞ A.Ş. (0-2) | model=Ev baseline=Dep gerçek=Dep | değer farkı=€-231.38m
- 5.12.2025 - 20:03 | GALATASARAY A.Ş. - SAMSUNSPOR A.Ş. (3-2) | model=X baseline=Ev gerçek=Ev | değer farkı=€293.7m
- 5.10.2025 - 20:00 | SAMSUNSPOR A.Ş. - FENERBAHÇE A.Ş. (0-0) | model=X baseline=Dep gerçek=X | değer farkı=€-258.65m
- 27.04.2026 - 20:00 | TÜMOSAN KONYASPOR - TRABZONSPOR A.Ş. (2-1) | model=X baseline=Dep gerçek=Ev | değer farkı=€-127.62m
- 15.02.2026 - 20:00 | RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ - BEŞİKTAŞ A.Ş. (2-3) | model=Ev baseline=Dep gerçek=Dep | değer farkı=€-197.88m
- 4.04.2026 - 14:30 | GENÇLERBİRLİĞİ - GÖZTEPE A.Ş. (0-2) | model=X baseline=Dep gerçek=Dep | değer farkı=€-55.09m
- 7.11.2025 - 20:00 | GENÇLERBİRLİĞİ - RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ (2-1) | model=X baseline=Dep gerçek=Ev | değer farkı=€-47.27m