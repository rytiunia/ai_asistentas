# P10 raidės (30 mm plexi) ant skaidraus akrilinio rėmo - etalonas (Rytis 2026-10-15)

**NEPAINIOTI su P10_lightbox_doublesided / singlesided (šviesdėžės).** Etalonas: `assets/etalonai/P10_Boots_ALT6739_akriliniai_begeliai.pdf`
(Boots apotek Åsane, BrandFactory, ALT6739_01.14_rycka, 2 lapai + gamybos detalės; Rytio pavyzdys „P10 jau darytos ant akrilinių bėgelių").
Visa, kas žemiau - perskaityta iš etalono (ne prielaidos).

## Konstrukcija (Profile 10, 1 lapo pjūvis)
1. Priekis - **balta plexi 30 mm** (raidė - vientisas blokas); 2. LED - nugaroje išfrezuotame griovelyje / kišenėje;
3. Nugara - **Alu 1,5 mm**; 4. **privirinti tvirtinimai** (welded fasteners - smeigės nugaroje); 5. **20 mm skaidrus plexi rėmas**.
Gylis 30 mm (raidė), vidaus (Interior); šonai RAL; priekiui gali būti plėvelė (ORACAL 8500).
„Šitie viduriukai kaip ADOPT tik įsigilina ir klijuojasi plėvelė" - smulkūs vidurio elementai tik įgilinami, ant jų plėvelė.

- **Alu 1,5 dugnelis ĮSILEIDŽIA į bloką** (Rytis 2026-10-15): bloko gale įleidimas 1,5 mm, aplink plexi kraštas
  (etalone ~5 mm - vidinis kontūras „30mm plexi" lape); bendras raidės gylis 30. Smeigės privirintos prie dugnelio ->
  nuo raidės krašto >= kraštas + 1 + Ø/2. Pjūvis `scripts/p10_raides.py`.
- **Kiekviena raidė / dalis - >= 2 smeigės; kiekis pagal formą (kvadratas 4, trikampis 3), taškai arti štricho centerline,
  ant vieno bėgelio - kuo labiau viena horizontali linija** (Rytis 2026-10-15). Mažų reklamų bėgelis gali būti 55 mm.
  Panašios raidės tvirtinamos vienodai (P kaip R); maža raidė (pvz. M ~170 mm) - užtenka 3 taškų.

- **P10 BE BĖGIO (blokinė reklama, `"mounting": "none"`)** (Rytis 2026-10-15, BN danbolig PO 3295): blokas tiesiai prie fasado,
  **Alu dugnelyje privirinti ilgasriegiai** (`"p10_rod": {"d": 6, "label": "M?"}`) + **popierinis montavimo šablonas**;
  **ilgasriegiai VIENOJE LINIJOJE viršuje ir VIENOJE apačioje** - ETALONAS: Rytio ranka sudėliotas DB-0002
  `assets/etalonai/P10_be_begio_ilgasriegiai_danbolig_Rytis.pdf` (v252): bendros visoms x aukščio raidėms; viršutinė ~12 % x aukščio
  nuo viršaus, apatinė ~82 % (~15-20 mm virš laidų išvesčių linijos); taškas - kertamo štricho vidurys; jei linija eina išilgai
  lanko / skersinio (o, n, a viršus) - taškai to ruožo GALUOSE (štricho vidurio atstumu nuo krašto); plati raidė - kairysis ir
  dešinysis taškas linijoje (o, d, n, a, b = 4), siaura (i, l) 1 + 1; **g - 2 viršuje, 1 apačioje (stiebo pusėje) + 1 kojelėje
  (jos viršutinėje dalyje, prie bazinės linijos)**; **i taškas - 2 ĮSTRIŽAI (priešingi kampai), laido išvestis centre**;
  danbolig 1800 x 352 = 30 vnt.;
  **g kojelėje - papildomas tvirtinimas**; **i taške - 2 tvirtinimai + sava laido išvestis**; ne ant laidų išvesčių;
  maitinimas „12V per letter + trafo box" (trafo neaprašomas); 3D vaizde - aiški nuoroda angliškai apie dažymą
  (spec `"note_3d"`, pvz. „FRONT PAINTED IN 2 LAYERS: 1st WHITE, 2nd BLACK"); ilgasriegio dydis / ilgis - klausimas klientui (lape „M?"); 1:1 sluoksnis `4_THREADED_RODS_<label>`. Šonai gali šviesti
  (nedažyti, `return_hex`), priekis dažytas (`face_hex`, pvz. baltai + juodai, klientas vėliau auksuoja).

## LED griovelis raidėje (lapas „30mm plexi", mėlyna linija)
- Raidėse - **viena linija per štricho vidurį**, tiesios atkarpos, **aštrios sankirtos** (A skersinis iki kojų ašių, A viršūnė -
  linija iki pat viršūnės, k šakos sujungtos su stiebu), **linijos eina beveik iki raidės galų**.
- **Plačios dalys (kryžius) - kelios lygiagrečios tiesios eilės** (kryžiaus rankose 3 eilės ~ plotis / 4 žingsniu), eilės
  kerta viena kitą, baigiasi ~ prieš galą. -> `scripts/griovelis_b.py` (B) ir `griovelis_sim.py` (simuliacija).

## Akrilinis rėmas (20 mm skaidrus plexi)
- **P10 VISADA = 30 mm blokas + rėmas; bendras gylis = 30 + rėmo storis** (Rytis 2026-10-15).
- **Raidės prisukamos per ATSKIRAS ĮLEISTAS SKYLES** (Rytis 2026-10-15: „atskiros įleistos skylės, kad būtų galima prisukti
  raides ir netrukdytų veržlė"): bėgelio ašyje po raidėmis **iš priekio Ø5 kiaurai, iš galo Ø12 x 15 įleidimas** veržlei
  (veržlė neliečia fasado); smeigės privirintos raidės nugaroje. NE ištisinis T griovelis.
  Generatorius: `braizyti_begeliai.py` `"acrylic": {"stud": {"d": 5, "cb_d": 12, "cb_depth": 15, "edge": 8, "two_if": 400}}` -
  1 smeigė raidei bėgelyje (2 - kai raidė >= 400), ne arčiau jungčių / Ø8 / statmenų; DXF STUD_HOLE_D5_THROUGH, COUNTERBORE_D12_DEPTH15_BACK.
- **Mažos raidės - VIENAS bėgelis 60 mm** (platesnis, jei trukdo tvirtinimui ar laidams), kai dviem bėgeliams nelieka
  tarpo bent bėgelio pločio (Rytis 2026-10-15, Leapmotor poz. 20: raidės 113 mm).
- **Laidų griovelis - kaip etalone: 6 mm pločio, 3,5 mm gylio** (mėlyna centerline palei bėgelį, ne ašyje - šalia
  tvirtinimo skylių eilės: poslinkis = Ø12 / 2 + griovelis / 2 + 2); prie raidžių - **ovalios skylės kiaurai** laidams
  (CABLE_SLOT_THROUGH, po 1 raidei) (Rytis 2026-10-15: „laidui griovelis kaip pavyzdyje").
- Dalys jungiamos **puzzle (interlocking) jungtimis, klijuojamos** („Bonding acrylic frame parts together with interlocking joints",
  DETAIL A 1:5); statmenų galuose - puzzle galvutės (detalės iš galo).
- Vidaus pakabinimas (Boots): stovai iš rėmo statmenų iki lubų, Alu tvirtinimo detalė - plokštelė 100 x 100 Alu 5 mm (Ø11 x 4,
  stačiakampė anga) + 40x25x2 Alu atvamzdis (Ø10, 70); „pasirinkus aukštį stovai nupjaunami ir pritvirtinami".
- Trafo box RAL 9005, 12 V / 220 V; laidas rėmo grioveliu.

## Lapai (etalono forma)
1 lapas - priekis su matmenimis, galinis vaizdas su laidu ir trafo box, Profile 10 pjūvis (1-5), MOUNTING / MATERIALS / DEPTH /
SIDE COLOR / LED / COLORS lentelė; 2 lapas - rėmo CAD (statmenų žingsnis, 35 pločiai, šonas 20 + 30), explode su Parts List
(1 20mm clear plexiglass, 2 Alu fitting part, 3 30mm acrylic letters), DETAIL A puzzle, tvirtinimo detalės, 3D.

## CAD failas (v273, Rytis 2026-10-15: „pateik ... cad failą")
`python3 scripts/pdf1to1_dxf.py <_1-1.pdf> <out.dxf> --merge <griovelis>.dxf:GROOVE_8MM,CENTERLINE` - DXF mm, y aukštyn, VAIZDAS IŠ
PRIEKIO: 1_LETTERS (bloko kontūras), 2_BACK_inset_<rim>mm (Alu dugnelio įleidimas), 4_THREADED_RODS_* (ilgasriegiai), 5_CABLE_EXITS_D11,
GROOVE_8MM + CENTERLINE (LED griovelis `griovelis_b.py --groove=8 --wall=2` iš 1_LETTERS kontūrų; plačios dalys >= 40 - žiedas).
Griovelio gylis - lape „?" (klausti). Pavyzdys: `scripts/projektai/bnskilte_3295_danbolig/cad/ALT0000_DB-0002_danbolig_CAD.dxf`.
