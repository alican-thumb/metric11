# Lig Geneli Piyasa Değeri / Model Denetimi

- Sezon: 2025-2026
- Transfermarkt kulüp kapsamı: 18/18
- Kadro oyuncusu: 817
- Toplam piyasa değeri: €1,741,910,000
- Maç kapsamı: 258/258 (%100)
- Lig modeli doğruluğu: %55
- Sabit draw-band 0.20 piyasa değeri baseline doğruluğu: %48
- Sabit draw-band 0.20 beraberlik yakalama: %16
- Model / piyasa baseline anlaşmazlığı: 86
- Anlaşmazlıklarda model doğruluğu: %44
- Anlaşmazlıklarda piyasa baseline doğruluğu: %24
- Belirgin değer farkında model hatası: 44

## Kullanım Sınırı

- Retrospektif tanısal benchmark; üretim tahmin girdisi değildir.
- Piyasa değeri snapshot'ı maç tarihlerinden sonraki değer/transfer güncellemelerini içerebilir; ileriye dönük model başarısı iddiası kurulamaz.
- Bu rapor market-value özelliğini modele eklemeden önce geçmiş dönemde nerede açıklayıcı olabileceğini ölçer.

## Eşik Karşılaştırması

| Draw band | Doğruluk | Beraberlik precision | Beraberlik recall | Tahmin dağılımı |
| ---: | ---: | ---: | ---: | --- |
| 0.00 | %51 | %0 | %0 | {'away': 130, 'home': 127, 'draw': 1} |
| 0.10 | %50 | %19 | %4 | {'away': 123, 'home': 119, 'draw': 16} |
| 0.20 | %48 | %25 | %16 | {'away': 107, 'home': 103, 'draw': 48} |
| 0.30 | %50 | %32 | %26 | {'away': 99, 'home': 96, 'draw': 63} |
| 0.40 | %48 | %31 | %36 | {'draw': 88, 'home': 83, 'away': 87} |

## Takım Bazlı Karşılaştırma

| Takım | Değer | Maç | Model | Değer baseline |
| --- | ---: | ---: | ---: | ---: |
| GALATASARAY A.Ş. | €363,750,000 | 28 | %64 | %64 |
| FENERBAHÇE A.Ş. | €328,700,000 | 29 | %69 | %59 |
| BEŞİKTAŞ A.Ş. | €273,350,000 | 29 | %55 | %52 |
| TRABZONSPOR A.Ş. | €169,600,000 | 29 | %59 | %55 |
| GÖZTEPE A.Ş. | €83,300,000 | 28 | %57 | %46 |
| RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ | €75,475,000 | 29 | %66 | %59 |
| SAMSUNSPOR A.Ş. | €70,050,000 | 29 | %55 | %38 |
| ÇAYKUR RİZESPOR A.Ş. | €48,025,000 | 29 | %48 | %48 |
| TÜMOSAN KONYASPOR | €41,975,000 | 29 | %52 | %59 |
| CORENDON ALANYASPOR | €41,700,000 | 28 | %43 | %39 |
| İKAS EYÜPSPOR | €39,825,000 | 29 | %41 | %34 |
| GAZİANTEP FUTBOL KULÜBÜ A.Ş. | €34,850,000 | 29 | %52 | %52 |
| KASIMPAŞA A.Ş. | €34,850,000 | 29 | %55 | %38 |
| ZECORNER KAYSERİSPOR | €29,875,000 | 28 | %46 | %46 |
| KOCAELİSPOR | €28,500,000 | 28 | %54 | %32 |
| GENÇLERBİRLİĞİ | €28,210,000 | 29 | %52 | %41 |
| HESAP.COM ANTALYASPOR | €26,275,000 | 28 | %57 | %46 |
| MISIRLI.COM.TR FATİH KARAGÜMRÜK | €23,600,000 | 29 | %59 | %55 |

## En Büyük Anlaşmazlıklar

- 20.09.2025 - 20:00 | TRABZONSPOR A.Ş. - GAZİANTEP FUTBOL KULÜBÜ A.Ş. (1-1) | model=X baseline=Ev gerçek=X | değer farkı=€134.75m
- 5.10.2025 - 20:00 | SAMSUNSPOR A.Ş. - FENERBAHÇE A.Ş. (0-0) | model=X baseline=Dep gerçek=X | değer farkı=€-258.65m
- 27.04.2026 - 20:00 | TÜMOSAN KONYASPOR - TRABZONSPOR A.Ş. (2-1) | model=Ev baseline=Dep gerçek=Ev | değer farkı=€-127.62m
- 15.02.2026 - 20:00 | RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ - BEŞİKTAŞ A.Ş. (2-3) | model=Ev baseline=Dep gerçek=Dep | değer farkı=€-197.88m
- 22.02.2026 - 20:03 | MISIRLI.COM.TR FATİH KARAGÜMRÜK - SAMSUNSPOR A.Ş. (0-0) | model=Ev baseline=Dep gerçek=X | değer farkı=€-46.45m
- 18.04.2026 - 17:00 | KOCAELİSPOR - GÖZTEPE A.Ş. (1-1) | model=X baseline=Dep gerçek=X | değer farkı=€-54.8m
- 13.02.2026 - 20:00 | HESAP.COM ANTALYASPOR - SAMSUNSPOR A.Ş. (3-1) | model=Ev baseline=Dep gerçek=Ev | değer farkı=€-43.77m
- 18.01.2026 - 17:00 | GENÇLERBİRLİĞİ - SAMSUNSPOR A.Ş. (1-1) | model=X baseline=Dep gerçek=X | değer farkı=€-41.84m
- 24.01.2026 - 17:00 | SAMSUNSPOR A.Ş. - KOCAELİSPOR (0-0) | model=X baseline=Ev gerçek=X | değer farkı=€41.55m
- 14.12.2025 - 14:30 | GAZİANTEP FUTBOL KULÜBÜ A.Ş. - GÖZTEPE A.Ş. (0-1) | model=Ev baseline=Dep gerçek=Dep | değer farkı=€-48.45m