# P3 - HALO (reverse-lit) raidės ant distancerių (v336, Rytis 2026-10-17)

Užklausa: „tai P3 profilis, korpusas / priekis Alu, galas 8 mm arba 4 mm su PVC tvirtinimo borteliu, ant distancinių laikiklių,
švietimas į galą. Būna variantas su reflektoriais, 5 mm outside didesni už raides, kurie tvirtinami už raidės prie bėgio.
Tvirtinimai kaip P6, tik tvirtinimo taškas turi būti tvirtinamo ploto centre, o ne šone ar krašte (pavyzdys - A raidė,
tvirtinimai per kojelės ploto centrą, kuris remiasi į rėmą)."
Etalonas: ALT8118 Clas Ohlson „Profile 3" (Front Alu 2, Side Alu 1, Backside white Plexiglas 8 mm, spacers 20 mm, LED ant galo,
RAL 9005). Kiti šaltiniai: `klientai/alfaneon_dsv.md` (DSV P3: Plexiglas WN770 8, DIN 7982 2,9x9,5), `klientai/prancuzai.md`
(halo: back plexi 8-10, spacers 25-60, M4 long thread), `klientai/clasohlson.md` (spaceriai Ø16 į plexi galą, Ø4 skylės),
`klientai/brandfactory.md` (Coop Mega - galas balta plexi 4 mm, spaceriai 30).

## Konstrukcija (spec `"front": "P3"`, `"p3": {...}`) - STANDARTAI v337 (Ryčio atsakymai 2026-10-17)
| raktas | numatyta | reikšmė |
|---|---|---|
| `spacer` | pagal gylį | distanceris (tarpas): gylis < 60 mm - 20, >= 60 mm - 30 |
| `spacer_d` | 16 | Ø16 |
| `rod` / `back_hole` / `rod_hole` | M4 / 4 / 4.5 | ilgasriegis per bėgelį ir distancerį; skylės plexi / reflektoriuje, bėgelyje |
| `back` | pagal aukštį | transparent plexiglass: raidės < 400 mm - 8 (varžtai per šoną į kraštą), >= 400 mm - 4 + PVC 3 bortelis (kaip 5S) |
| `screw` | DIN 7982 2.9 x 9.5 | varžtai per šoną |
| `reflector` | false | STANDARTAS P3 - be reflektorių; užklausoje „P3+reflector" (spec `"front": "P3+reflector"`) - reflektorius = kontūras + `refl_off` (5 mm), už raidės ant bėgelio |
| `refl_mat` / `refl_ral` | ACM 3 mm / ? | standartas ACM (RAL pagal užklausą arba dažyta); būna `"Alu 1.5 mm"`; storis z - iš medžiagos |
| `led` | LED modules on plexi inside, 6500K | LED ant plexi viduje; žingsnis tikslinamas; trafas - bendros taisyklės |
| `drain` / `drain_d` | true / 8 | drenažas - Ø8 PUSLANKIAI galo kontūre žemiausiose vietose (kaip P6 ant rėmo) |
| `edge` / `split` | 5 / 400 | distancerio kraštas nuo galo krašto; ilgas plotas - taškų daugiau |

Sluoksniai nuo sienos: rėmas (dydis - užklausoje) + reflektorius (jei yra) + distanceriai + raidės (grupės z0 automatiškai).
Ant FOLDED PLATE - tvirtinimo standartas tas pats (distanceriai tvirtinamo ploto centre); generatorius folded P3 - dar
nepadarytas (pirmam užsakymui). Maketo lape plexi - tik „transparent plexiglass" (be rūšies).
Placeholderiai BOM / MAIN DATA: `{SPACERS}`, `{SPACER_D}`, `{SPACER_L}`, `{P3_BACK}`, `{P3_BACK_TXT}`, `{P3_SCREW}`,
`{P3_SCREW_INTO}`, `{P3_LED}`, `{REFL_MAT}`, `{REFL_RAL}`, `{REFL_N}`, `{REFL_x}` (nesting); PVC bortelio eilutė
(„PVC fixing edge") išmetama, kai galas 8 mm.

## TVIRTINIMAS - tvirtinamo ploto CENTRE (`scripts/p3_raides.py`)
1. Tvirtinamas plotas = raidės dugno (kontūras - 0,7 mm, v341) ir HORIZONTALAUS bėgelio juostos persidengimo komponentas
   (v338: ant statmenų / įstrižų tvirtinimai nesideda; tik akcentui be horizontalaus bėgelio - jo laikiklis). A raidė: apatinis bėgelis - dvi kojelės (du plotai), viršutinis - viršūnė.
2. Taškas - to ploto centroidas; jei ten netelpa distanceris (Ø/2 + 5 mm nuo krašto, Ø16 ant 30 mm bėgelio - ±7 nuo ašies) -
   artimiausia leistina vieta. NE štricho kraštas / galas (skirtumas nuo P6 D3.2).
3. Ilgas plotas išilgai bėgelio (> 400 mm) - lygios dalys, taškas kiekvienos dalies centre; jei raidei taškų mažiau nei pagal
   formą (D: 2 bėgeliai po vieną plotą), plotai dalijami smulkiau (250 / 160).
4. Kiekis ir parinkimas - kaip P6 (`tvirtinimas.shape_n` kvadratas 4 / trikampis 3, FPS, A viršūnė - vienas taškas,
   tarp dviejų to paties bėgelio taškų - nededama). Raidė < 2 distancerių - `K.SHEET_ERR` (patikra 18).
5. Lape: galiniame vaizde distanceriai - mėlyni punktyriniai Ø su kryžiumi (už bėgelio), pavadinime kiekis; šoniniame - tarpas
   ir distanceriai; 3D - distanceriai, švytėjimas (halo) / reflektorius; BOM `{SPACERS}`, `{SPACER_D}`, `{SPACER_L}`,
   `{REFL_N}`, `{BACK_x}` (plexi - kontūras -1 mm), `{REFL_x}` (nesting kontūras +5).
6. Pjūvis `PROFILE P3` (`p3_raides.section`; v344 - rėmo profilis pagal spec: U arba stačiakampis vamzdis, matmuo - rėmo gylis): siena | U + ausėlė | (reflektorius) | distanceris + M4 | plexi galas 8 (varžtas į
   kraštą) arba 4 + PVC bortelis (A) | LED ant galo | šonas 1 | priekis 2.
7. Failai: `<lapas>_1-1.pdf` (+ sluoksniai 4_SPACER_HOLES, 5_REFLECTOR), `<lapas>_P3.dxf` - v341 (Rytis 2026-10-17)
   ATSKIROS GRUPĖS (BLOCK + INSERT + DXF GROUP, kaip P6 `group_layers`): 1 REMAS (bėgeliai, statmenys, ausėlės su Ø),
   2 DUGNAS (plexi galas 0,7 mm inside + distancerių Ø4 + drenažo Ø8 puslankiai), 3 PRIEKIS (raidės kontūras),
   4 REFLEKTORIUS (tik P3+reflector: +5 mm, Ø4,5); kreivės lankais. 3D - be švytėjimo linijų už raidžių.

ETALONAS (v339 / v340, Rytis 2026-10-17): dokumentas P3 + P3+reflector - PAVYZDYS L 3400, gylis 60, distanceriai 30,
galas plexi 4 + PVC, rėmas U 30x30x2 (3277 mm - 3 statmenys); 1 lapas P3 (standartas), 2 lapas P3+reflector (ACM 3, +5 mm):
`assets/etalonai/P3_ir_P3_reflector_PAVYZDYS_etalonas.pdf`, projektas `scripts/projektai/p3_pavyzdys/` (`build_order.py`, 1:1,
`_P3.dxf`). Pjūvyje sienos simbolio nėra (v340). Regresija: „order p3 halo pavyzdys" + `p3_raides.py` savitikra.

## Dar tikslinama
LED žingsnis (P3 lentelė - bus patikslinta); varžtų per šoną žingsnis; folded P3 generatorius.
Testas: `scripts/projektai/p3_vangelonys_test/` (Vangelonys L 4300, gylis 80, rėmas 40x40x2 square RAL 9016, RAL 6017) - regresijoje.
RĖMO PROFILIS P3 (v346, Rytis 2026-10-17): vengti uždaro profilio - standartas U; stačiakampis (uždaras) - TIK pagal užklausos
pareikalavimą (spec `"rail": {"type": "sq", "on_request": true}`, kitaip patikra 18). Tada galinėje (sienos) sienelėje -
didesnė skylė (dydis pagal iškabą, lape „Ø?"), distanceris tvirtinamas per priekinę sienelę kaip U profiliui (M4 + veržlė).
