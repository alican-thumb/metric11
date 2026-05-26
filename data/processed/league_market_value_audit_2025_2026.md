# Lig Geneli Piyasa Değeri / Model Denetimi

- Sezon: 2025-2026
- Transfermarkt kulüp kapsamı: 18/18
- Kadro oyuncusu: 512
- Toplam piyasa değeri: €1,378,850,000
- Maç kapsamı: 258/258 (%100)
- Lig modeli doğruluğu: %50
- Sabit draw-band 0.20 piyasa değeri baseline doğruluğu: %51
- Sabit draw-band 0.20 beraberlik yakalama: %10
- Model / piyasa baseline anlaşmazlığı: 99
- Anlaşmazlıklarda model doğruluğu: %35
- Anlaşmazlıklarda piyasa baseline doğruluğu: %37
- Belirgin değer farkında model hatası: 61

## Kullanım Sınırı

- Retrospektif tanısal benchmark; üretim tahmin girdisi değildir.
- Piyasa değeri snapshot'ı maç tarihlerinden sonraki değer/transfer güncellemelerini içerebilir; ileriye dönük model başarısı iddiası kurulamaz.
- Bu rapor market-value özelliğini modele eklemeden önce geçmiş dönemde nerede açıklayıcı olabileceğini ölçer.

## Eşik Karşılaştırması

| Draw band | Doğruluk | Beraberlik precision | Beraberlik recall | Tahmin dağılımı |
| ---: | ---: | ---: | ---: | --- |
| 0.00 | %52 | %0 | %0 | {'home': 127, 'away': 131} |
| 0.10 | %52 | %33 | %5 | {'home': 121, 'away': 125, 'draw': 12} |
| 0.20 | %51 | %30 | %10 | {'home': 114, 'away': 117, 'draw': 27} |
| 0.30 | %52 | %33 | %21 | {'home': 105, 'away': 105, 'draw': 48} |
| 0.40 | %51 | %35 | %30 | {'home': 96, 'away': 96, 'draw': 66} |

## Takım Bazlı Karşılaştırma

| Takım | Değer | Maç | Model | Değer baseline |
| --- | ---: | ---: | ---: | ---: |
| GALATASARAY A.Ş. | €336,650,000 | 28 | %64 | %64 |
| FENERBAHÇE A.Ş. | €240,800,000 | 29 | %66 | %66 |
| BEŞİKTAŞ A.Ş. | €176,000,000 | 29 | %52 | %59 |
| TRABZONSPOR A.Ş. | €129,550,000 | 29 | %45 | %55 |
| RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ | €73,100,000 | 29 | %59 | %66 |
| GÖZTEPE A.Ş. | €65,750,000 | 28 | %54 | %46 |
| SAMSUNSPOR A.Ş. | €56,100,000 | 29 | %52 | %45 |
| ÇAYKUR RİZESPOR A.Ş. | €39,750,000 | 29 | %45 | %52 |
| TÜMOSAN KONYASPOR | €39,300,000 | 29 | %62 | %45 |
| CORENDON ALANYASPOR | €33,800,000 | 28 | %46 | %39 |
| KASIMPAŞA A.Ş. | €30,800,000 | 29 | %31 | %41 |
| GAZİANTEP FUTBOL KULÜBÜ A.Ş. | €29,800,000 | 29 | %62 | %48 |
| GENÇLERBİRLİĞİ | €26,250,000 | 29 | %55 | %48 |
| ZECORNER KAYSERİSPOR | €24,750,000 | 28 | %54 | %54 |
| KOCAELİSPOR | €24,150,000 | 28 | %29 | %39 |
| HESAP.COM ANTALYASPOR | €19,450,000 | 28 | %43 | %54 |
| İKAS EYÜPSPOR | €17,150,000 | 29 | %31 | %45 |
| MISIRLI.COM.TR FATİH KARAGÜMRÜK | €15,700,000 | 29 | %59 | %55 |

## En Büyük Anlaşmazlıklar

- 27.09.2025 - 20:00 | MISIRLI.COM.TR FATİH KARAGÜMRÜK - TRABZONSPOR A.Ş. (3-4) | model=X baseline=Dep gerçek=Dep | değer farkı=€-113.85m
- 1.05.2026 - 20:00 | GAZİANTEP FUTBOL KULÜBÜ A.Ş. - BEŞİKTAŞ A.Ş. (0-2) | model=X baseline=Dep gerçek=Dep | değer farkı=€-146.2m
- 18.01.2026 - 17:00 | KOCAELİSPOR - TRABZONSPOR A.Ş. (1-2) | model=X baseline=Dep gerçek=Dep | değer farkı=€-105.4m
- 20.09.2025 - 20:00 | TRABZONSPOR A.Ş. - GAZİANTEP FUTBOL KULÜBÜ A.Ş. (1-1) | model=X baseline=Ev gerçek=X | değer farkı=€99.75m
- 26.10.2025 - 14:30 | HESAP.COM ANTALYASPOR - RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ (0-4) | model=X baseline=Dep gerçek=Dep | değer farkı=€-53.65m
- 22.02.2026 - 20:03 | MISIRLI.COM.TR FATİH KARAGÜMRÜK - SAMSUNSPOR A.Ş. (0-0) | model=X baseline=Dep gerçek=X | değer farkı=€-40.4m
- 27.04.2026 - 20:00 | TÜMOSAN KONYASPOR - TRABZONSPOR A.Ş. (2-1) | model=X baseline=Dep gerçek=Ev | değer farkı=€-90.25m
- 13.04.2026 - 20:00 | İKAS EYÜPSPOR - SAMSUNSPOR A.Ş. (1-2) | model=X baseline=Dep gerçek=Dep | değer farkı=€-38.95m
- 18.10.2025 - 17:00 | ÇAYKUR RİZESPOR A.Ş. - TRABZONSPOR A.Ş. (1-2) | model=X baseline=Dep gerçek=Dep | değer farkı=€-89.8m
- 31.10.2025 - 20:00 | RAMS BAŞAKŞEHİR FUTBOL KULÜBÜ - KOCAELİSPOR (1-0) | model=X baseline=Ev gerçek=Ev | değer farkı=€48.95m