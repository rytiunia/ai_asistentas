# Medžiagų formatai ir 6 m strypų taisyklė (v73, Rytis 2026-10-10)

Duomenys - `assets/medziagos.json` (tiekėjų formatai; keisti TIK ten), kodas - `scripts/medziagos.py`
(`nest_bars`, `trim_to_stock`, `sheet_fit`; CLI `python3 scripts/medziagos.py bars 3025 3025 600` /
`sheet 2400 1200 alu 2`). Šaltiniai 2026-10-10: Heliopolis e-parduotuvė ir produktų puslapis
(„Profilių ilgis - 6 metrai"), Plastena (PMMA). Kainos nerašomos. `?` = Rytis dar nepatvirtino tiekėjo / formato.

## 1. Profiliai - strypas 6000 mm

| Profilis | Tiekėjas / kodas | Ilgis | Naudojimas |
|---|---|---|---|
| L 30x30x2 | Heliopolis A-8012 | 6 m | folded plokštės tvirtinimas (viršus + apačia), L prie sienos bėgeliams, ausėlės 30 |
| L 40x40x2 | Heliopolis A-8028 / anoduotas | 6 m | ausėlės 40 |
| O 20x20x1.5, O 25x15x1.5, L 20x15x2, L 15x15x1.5, U 6x9x1.5 | Heliopolis | 6 m | pagalbiniai |
| Alu juosta 30x2 / 40x2 (J4002) / 50x2 | Heliopolis | 6 m | plokščios juostos |
| Alu juosta ritinyje 1x30 / 1x50 (1050A H24) | Heliopolis | ritinys | raidžių šonai |
| **U 30x30x2, U 40x40x2** (bėgeliai), **Z 30x30x30x2**, **20x20x2** ir **30x30x3** vamzdžiai | **?** (Heliopolis e-parduotuvėje nėra) | 6 m (standartas) | bėgeliai, EXTRA X rėmas, FAS 700 |

Parametrai (`medziagos.json` -> `profiliai`): `strypas_mm` 6000, `prapjova_mm` 3 (pjūklo prapjova vienam pjūviui - Rytis patvirtino 2026-10-10), `galo_atsarga_mm` 0, `trim_max_mm` 100 (didžiausias vieno horizontalaus bėgelio patrumpinimas, abu galai
kartu), `trim_step_mm` 5. Spec perrašymas: `"stock": {"enabled": true, "bar_mm": 6000, "kerf_mm": 3, "end_mm": 0, "trim_max_mm": 100}`.

**Strypų skaičiavimas (visuose rėmo / profilių moduliuose):** visos to paties profilio dalys užsakyme (horizontalūs
bėgeliai, statmenys, vertikalūs laikikliai - VISŲ grupių kartu) dėliojamos į 6 m strypus (FFD, ilgiausios pirmos);
į strypą telpa, jei `suma + prapjova x (n dalių - 1) + galo atsarga <= 6000`. Konsolėje - planas
`2 x 6 m: [2995+2995] [600+600]` ir atlieka; BOM placeholderiai `{RAIL_BARS}` (strypų kiekis), `{RAIL_PLAN}`,
`{BAR_M}` (6), `{PRAIL_BARS}` (plokštės bėgelis), folded `{L_BARS}`. Naujuose spec'uose bėgelių eilutėje rašyti
`{RAIL_LIST_M} = {RAIL_TOTAL_M} m ({RAIL_BARS} x {BAR_M} m bars)`; esamų etalonų BOM nekeičiamas.
Dalis ilgesnė už 6 m -> strypų plane skaidoma į 6000 + likutis (likutis dėliojamas su kitomis dalimis) ir perspėjimas „jungti iš 2 dalių (sandūra po raide, prie statmens)" - sandūros vietą parenka Rytis (v74).

## 2. 6 m taisyklė rėmui po raidėmis (PAGRINDINĖ, Rytis 2026-10-10)

Darant rėmą po raidėmis atsižvelgti į standartinį 6 m profilio ilgį ir VENGTI rėmo, kuris sudėliotas gaunasi pvz.
6,05 m (2 x 3025): jis netelpa į vieną strypą - antras strypas beveik visas atlieka. Tokiu atveju rėmo dalys
PATRUMPINAMOS, kad tilptų į 6 m, bet patrumpinimas NETURI pažeisti kitų taisyklių. Retas atvejis - taisyklė galioja
tik kai pasitaiko atitikmuo (`braizyti_begeliai.py`, blokas „6 m STRYPŲ TAISYKLĖ", prieš ausėles):

1. Po bėgelių galų (10 mm taisyklė, v67) ir PRIEŠ ausėles suskaičiuojamas strypų kiekis n0 su visomis dalimis
   (statmenų kiekis ir ilgis - įvertis pagal tą pačią formulę kaip `place_verticals`).
2. Ieškomas MAŽIAUSIAS patrumpinimas d (žingsnis 5 mm, iki `trim_max_mm`), po kurio strypų reikia mažiau (n < n0).
   Trumpinami TIK horizontalūs bėgeliai (iš kliento grafikos); detalizacijos rėmas (`groups[].rails`), statmenys,
   vertikalūs laikikliai, plokštės bėgelis, Z rėmas - NEKEIČIAMI. Patrumpinimas dalijamas abiem galams simetriškai
   (rėmas lieka centre po raidėmis); jei vienas galas riboja - likutis į kitą galą. Bėgelis, kurio trumpinti
   nereikia (strypų kiekis be jo nesikeičia), lieka pilnas.
3. Galo laisvumas (kiek galima trumpinti, `_h_slack`) - iš geometrijos, kad NEPAŽEISTŲ kitų taisyklių:
   abu galo kampai lieka >= 10 mm (`rail_edge_mm`) kraštinės raidės viduje TOJE PAČIOJE raidėje (skylė / tarpas
   stabdo); galas lieka kraštinės raidės IŠORINĖJE pusėje (ne arčiau raidės vidurio, v67); galas prie raidės
   skylės (pvz. „6" akutė) laisvumo neturi. Patrumpintas bėgelis vis tiek pasiekia abi kraštines raides.
4. Ausėlės, statmenys, laido išvestis iš bėgelio galo - skaičiuojami PO patrumpinimo, ant galutinio bėgelio
   (kraštinės ausėlės <= 300 mm nuo naujo galo, statmenys po raidėmis ir t. t. - taisyklės nesikeičia).
5. Jei per `trim_max_mm` tilptų, bet laisvumo neužtenka (10 mm / išorinės pusės taisyklės) - NETRUMPINAMA,
   perspėjimas `! 6 m taisyklė: ... trumpinti neleidžia ... - Rytis sprendžia` (atsakyme pateikti). Jei
   patrumpinimas strypų kiekio nemažina (pvz. 2 x 3025 + 2 statmenys po 220 - antras strypas reikalingas vis
   tiek) - bėgeliai paliekami kaip yra.
6. Konsolėje: `6 m taisyklė: TEST bėgelis y60: 3025 -> 2995 mm (-15 kairė / -15 dešinė)` ir
   `6 m taisyklė (30x30x2): 2 -> 1 strypai; 1 x 6 m: [2995+2995]`. Atsakyme Ryčiui VISADA paminėti, kad bėgeliai
   patrumpinti dėl 6 m taisyklės ir kiek. P6 DXF (`p6_dxf.py`) bėgelius ima iš kliento failo - jei lape bėgeliai
   patrumpinti, DXF rėmą (`3_REMAS`) daryti pagal lapo ilgius (pasakyti skirtumą).
7. Folded L profiliai (plotis - 50) - standartas, NETRUMPINAMI: jei 2 x L netelpa į vieną strypą (pvz. plokštė
   3050 -> 2 x 3000 + prapjova), tik perspėjimas - Rytis sprendžia.

Bandymas: `scripts/projektai/strypai_6m_test/` (`make_test.py` -> H I I I H, 2 bėgeliai po 3025 -> 2995 + 2995,
1 strypas; `spec_6050_v.json` su statmenimis - 2 strypai, netrumpinama; `spec_folded_3050.json` - L 2 x 3000 perspėjimas).

## 3. Lakštai - formatai ir pritaikymas

`sheet_fit(w, h, medžiaga, storis)`: detalė telpa, jei `(ilgoji + 2 x 10) x (trumpoji + 2 x 10) <= formatas` (bet
kuria kryptimi; paraštė `lakstai.parastė_mm` 10). Netelpa -> „dalyti į N dalis" (folded - `moduliai_folded.md`
„Folded iš kelių dalių", sandūros taisyklės ten). Medžiagos raktažodžiai (`zodynas`): plexi / pmma / acrylic,
pvc / forex / simopor, akp / dibond / lightbond / albond, alu, pc, ps.

| Medžiaga | Tiekėjas | Formatai (mm) x storis | Naudojimas skill'e |
|---|---|---|---|
| PMMA Plexiglas XT WN770 opal (balta) | Heliopolis | 4050x2050 x 8 | P6_8mm priekis |
| PMMA Plexiglas XT skaidri | Heliopolis | 3050x2050 x 5 | - |
| PMMA PLAZCRYL balta R7065 / R7068 | Plastena | 3050x2050 x 2 / 3 / 4 / 10 / 15; 4000x2050 x 3; 2050x1500 ir 1020x1000 x 2 / 3 / 4 | P6_3mm priekis (balta 3 mm) |
| PMMA PLAZCRYL matinė (opal) R7072 | Plastena | 3050x2050 x 2 / 3 | - |
| PMMA PLAZCRYL XT skaidri | Plastena | 3050x2050 x 1.5 / 2 / 3 / 4 / 10 / 12; 2050x2000, 2050x1000, 1020x1000 x 2 / 3 / 4 | - |
| PMMA spalvota (P6_3mm color) | ? | 3050x2050 x 3 (tikrinti pagal spalvą) | P6_3mm color |
| PVC putų Simopor (SIMONA) / PP Connect | Heliopolis | 3050x2050 x 2 / 4 / 5; 3050x2030 x 1 / 8; 3050x1530 x 5 (pilka) | PVC bortelis / P1 dugnas 3 mm - formatas ? |
| AKP LIGHTBOND PLUS | Heliopolis | 3050x1500 x 3 (balta); 4050x1500 x 3 (sidabrinė, raudona); 3100x1220 x 2 / 3 | plokščios iškabos, back plate |
| AKP ALBOND PVDF | Heliopolis | 3200x1500 x 4 (balta, sidabrinė ~9006, antracitas ~7016, juoda ~9005, tamsiai pilka) | - |
| Alu lakštas EN AW 1050A H14/24 | Heliopolis | 3000x1500 x 1.5 / 2; 4000x2000 x 2 | folded plokštė (Al 2, lakštas 2000x4000), raidžių galas 1.5 |
| Alu 3 mm (P6+3 plokštė, EXTRA X), Alu 1 mm lakštas | ? | 3000x1500 (patvirtinti) | plokštė, šonai |
| PC EXOLON / IMPEX UVP skaidri, IMPEX 866 opal | Heliopolis | 3050x2050 x 2 / 3 / 4 / 6; opal 3 | šviesdėžės |
| PS 744 balta (IROPLASTIC) | Heliopolis | 2000x1000 x 1 / 1.5; 3050x2050 x 2 / 3 | - |

Pritaikymas lape: folded išklotinė (`braizyti_lapa.py`, `folded_dxf.py`) tikrinama automatiškai (konsolė
`išklotinė 3130 x 680 (alu 2 mm): telpa: 4000x2000 ...`); P6 priekis / plokštė - `python3 scripts/medziagos.py sheet W H plexi 8`
kai elementas didelis (> 2000 mm) - netelpa -> sakyti, dalijimo vietą klausti. Nesting į lakštą - `moduliai_folded.md` „NESTING".

## Bėgelis ilgesnis už strypą (v90 / v93, Rytis 2026-10-11)
v93: PIRMIAUSIA trumpinamas iki strypo ilgio (pvz. 6500 -> 6000, `braizyti_begeliai.py`, be `trim_max` ribos), jei galai lieka
kraštinių raidžių viduje ir išorinėje pusėje (`_h_slack(..., cap_over)`) - konstrukcija nesusilpnėja, sandūros nėra.
Tik jei netelpa - jungiama:
Pagrindinė taisyklė - taupyti medžiagą: kur bus sandūra, nesvarbu, bet turi likti kuo mažiau atliekų. `nest_bars` ieško
pirmos dalies ilgio (nuo pilno strypo iki lygių dalių, žingsnis 50) taip, kad visas profilio planas užimtų mažiausiai
strypų ir liktų didžiausias vientisas likutis (`LAST_SPLITS`). Bėgelis <= 6 m NIEKADA nedalijamas ir nevirinamas iš dalių
vien dėl taupymo.

## Strypai visam užsakymui (v98, Rytis 2026-10-11)
Strypų planas ir bėgelių trumpinimas skaičiuojami VISAM užsakymui (spec `qty`): 2 vnt. iškabų po du ~3,05 m bėgelius be
patrumpinimo užimtų 4 strypus, patrumpinus (pvz. 3042/3089 -> 2972/3019) - 2 strypus po 2 bėgelius + 1 statmenims.
Renkamas mažiausias patrumpinimas su mažiausiu strypų kiekiu; didesnis - tik jei vientisas likutis padidėja >= 500 mm.

