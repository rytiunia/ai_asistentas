# Clas Ohlson (užsakovas BrandFactory) - kliento taisyklės

Raktažodžiai: Clas Ohlson, CO, Horten, Bodø (Order 226045), ALT8857, P8 special. Bendrinės folded / nesting / DXF / 3D / matmenų taisyklės -
SKILL.md. Projektas `scripts/projektai/clasohlson_horten/` (README ten): Horten 3 (16839 x 900 ant 3 plokštumų,
6 dalys) ir Horten 1 (3000 x 1300, exterior). Senas brėžinys ALT8857 - „Senų brėžinių perdarymas".

## P8 special raidė (Rytis 2026-10-09, „viskas pagal Clas Ohlson standartą")
- Priekis Al 3 mm, DIDESNIS už plexi (išsikišimas - KLAUSTI, lape „?").
- Plexi 20 mm išfrezuotas apvalkalas: galas 7 + ertmė 13, sienelė ~7.5 (lygaus storio).
- LED Baltled Crown Mini 0.3 W 6500K ant priekio vidaus per vidurį (kiekis - klausti / skaičiuoti).
- Spaceriai Ø16 x 20 į plexi galą, TIK po raidėmis.
- Pjūvis - `co/common.py: draw_p8`, DETAIL A 1:2 lūžęs vaizdas `detail_a`.

## Tvirtinimai pagal dydį - `assets/clasohlson_proporcijos.pdf` (3 dydžiai, 1:1)
Raidei imamas ARTIMIAUSIO AUKŠČIO etalonas, skylių centrai perkeliami proporcingai, DIAMETRAI NEKINTA:
Ø4 (spaceriai), išilginė 6.1 x 3.7, Ø8 (paskirtis - klausti). Kodas `refholes.py` (`apply()`).
1:1 failas - 7 sluoksniai (raidės, dugnas, plokštė, Ø4, išilginės, Ø8, 7_CABLE_D11).

## Laidas ir maitinimas (Rytis 2026-10-09)
- Baltas 12V, 5 m, KAIRĖJE VIRŠUJE: D11 logotipo lanke (>= 30 nuo kontūro, >= 20 nuo Ø4, kuo arčiau viršaus,
  `data.d11_point`) -> horizontaliai už plokštės -> Ø11 KAIRĖJE ŠONINĖJE užlenktoje briaunoje D11 aukštyje
  (20 nuo briaunos krašto, matmuo nuo viršaus) -> TRAFO BOX RAL 7044 -> 230V.
- Rodoma galiniame vaizde ir išklotinėje.

## Folded fonas
- Spalva (Horten) NCS S 0540-B, dažoma tik išorė.
- Horten 3: fasado kampai nepateikti -> visos dalys 90° (bendra taisyklė); dalys atskiros, be jungimo skylių.
- 3D - ant fasado prekybos centro viduje (`sheet2v.environment`).

## Neišspręsta (lape „?")
Tvirtinimas į sieną, raidės tvirtinimo elementas per plokštę, LED kiekis, priekio išsikišimas, Ø8 paskirtis, ORDER NO.

## Bodø - Order 226045 (2026-10-15)
LED sign 2 vnt.: vertikali folded plokštė 515 x 2380 x 40 (mėlyna), logotipas 420 x 824 P8 special („same thickness as LED sign
you have produced" = Horten: plokštė 40, raidė 3 + 20, spaceriai 20). Projektas `scripts/projektai/clasohlson_226045_bodo/`
(savarankiškas - `bodo.py`, vietinės common / data / refholes kopijos). Išklotinė 591 x 2456 - lakštas 3000x1500.
