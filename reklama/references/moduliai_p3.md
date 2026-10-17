# P3 - HALO (reverse-lit) raidės ant distancerių (v336, Rytis 2026-10-17)

Užklausa: „tai P3 profilis, korpusas / priekis Alu, galas 8 mm arba 4 mm su PVC tvirtinimo borteliu, ant distancinių laikiklių,
švietimas į galą. Būna variantas su reflektoriais, 5 mm outside didesni už raides, kurie tvirtinami už raidės prie bėgio.
Tvirtinimai kaip P6, tik tvirtinimo taškas turi būti tvirtinamo ploto centre, o ne šone ar krašte (pavyzdys - A raidė,
tvirtinimai per kojelės ploto centrą, kuris remiasi į rėmą)."
Etalonas: ALT8118 Clas Ohlson „Profile 3" (Front Alu 2, Side Alu 1, Backside white Plexiglas 8 mm, spacers 20 mm, LED ant galo,
RAL 9005). Kiti šaltiniai: `klientai/alfaneon_dsv.md` (DSV P3: Plexiglas WN770 8, DIN 7982 2,9x9,5), `klientai/prancuzai.md`
(halo: back plexi 8-10, spacers 25-60, M4 long thread), `klientai/clasohlson.md` (spaceriai Ø16 į plexi galą, Ø4 skylės),
`klientai/brandfactory.md` (Coop Mega - galas balta plexi 4 mm, spaceriai 30).

## Konstrukcija (spec `"front": "P3"`, `"p3": {...}`)
| raktas | numatyta | reikšmė |
|---|---|---|
| `spacer` | 30 | tarpas raidės galas -> bėgelis / reflektorius, mm |
| `spacer_d` | 16 | distancerio Ø (Clas Ohlson) |
| `back` | 8 | galas balta plexi 8 (varžtai per šoną į plexi kraštą) arba 4 (+ PVC 3 mm bortelis, varžtai į bortelį) |
| `back_hole` / `rod_hole` | 4 / 4.5 | skylė plexi gale / reflektoriuje (DXF) |
| `reflector` | false | reflektorius = raidės kontūras + `refl_off` (5 mm), už raidės ant bėgelio |
| `refl_t` | 3 | tik brėžiniui; medžiaga / storis - „?" (klausimynas) |
| `edge` | 5 | distancerio kraštas nuo galo krašto |
| `split` | 400 | ilgas tvirtinamas plotas išilgai bėgelio dalijamas kas <= 400 |

Grupės z0 = bėgelis + (reflektorius) + `spacer` (automatiškai). Priekis Alu (`face_hex` / `return_ral`), galas balta plexi.

## TVIRTINIMAS - tvirtinamo ploto CENTRE (`scripts/p3_raides.py`)
1. Tvirtinamas plotas = raidės galo (kontūras - 1 mm šonas) ir bėgelio juostos persidengimo komponentas (h, v ir ĮSTRIŽI
   bėgeliai - pagal jų poly). A raidė: apatinis bėgelis - dvi kojelės (du plotai), viršutinis - viršūnė.
2. Taškas - to ploto centroidas; jei ten netelpa distanceris (Ø/2 + 5 mm nuo krašto, Ø16 ant 30 mm bėgelio - ±7 nuo ašies) -
   artimiausia leistina vieta. NE štricho kraštas / galas (skirtumas nuo P6 D3.2).
3. Ilgas plotas išilgai bėgelio (> 400 mm) - lygios dalys, taškas kiekvienos dalies centre; jei raidei taškų mažiau nei pagal
   formą (D: 2 bėgeliai po vieną plotą), plotai dalijami smulkiau (250 / 160).
4. Kiekis ir parinkimas - kaip P6 (`tvirtinimas.shape_n` kvadratas 4 / trikampis 3, FPS, A viršūnė - vienas taškas,
   tarp dviejų to paties bėgelio taškų - nededama). Raidė < 2 distancerių - `K.SHEET_ERR` (patikra 18).
5. Lape: galiniame vaizde distanceriai - mėlyni punktyriniai Ø su kryžiumi (už bėgelio), pavadinime kiekis; šoniniame - tarpas
   ir distanceriai; 3D - distanceriai, švytėjimas (halo) / reflektorius; BOM `{SPACERS}`, `{SPACER_D}`, `{SPACER_L}`,
   `{REFL_N}`, `{BACK_x}` (plexi - kontūras -1 mm), `{REFL_x}` (nesting kontūras +5).
6. Pjūvis `PROFILE P3` (`p3_raides.section`): siena | U + ausėlė | (reflektorius) | distanceris + M4 | plexi galas 8 (varžtas į
   kraštą) arba 4 + PVC bortelis (A) | LED ant galo | šonas 1 | priekis 2.
7. Failai: `<lapas>_1-1.pdf` (+ sluoksniai 4_SPACER_HOLES, 5_REFLECTOR), `<lapas>_P3.dxf` (1_FRONT_ALU2, 2_BACK_PLEXI su Ø
   skylėmis, 5_REFLECTOR), kreivės lankais.

Pavyzdys: `scripts/projektai/p3_pavyzdys/` (PAVYZDYS L 3400, gylis 60, spacer 30; 1 lapas - standartas, plexi 8;
2 lapas - reflektoriai + plexi 4 + PVC). Regresija: „order p3 halo pavyzdys" + `p3_raides.py` savitikra (A kojelių centrai).

## Neišspręsta (klausimynas Ryčiui 2026-10-17, lape „?")
Distancerio Ø / medžiaga / spalva; tvirtinimas (M4 ilgasriegis? į plexi sriegis ar įvorė; 4 mm galui - kiaurai su veržle?);
reflektoriaus medžiaga, storis, spalva, tvirtinimas prie bėgelio; LED vieta (ant galo / ant priekio vidaus), tipas, K;
plexi rūšis (WN770 / GS); kada 4 mm, kada 8 mm; PVC bortelio matmenys; varžtai per šoną (DIN 7982 2,9x9,5?); rėmas P3 - U 30x30x2
ar Z / taškinis be rėmo (DSV „point mounting no rail"); minimalus tvirtinamas plotas; drenažas; trafo vieta; laido išvestis.
