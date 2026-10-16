# Žinomos klaidos (nekartoti) - pilnas sąrašas (perkelta iš SKILL.md v73)

Procesinės (paskyros kopija sena, lygiagretūs pokalbiai, ASCII vardai, auseles.py EXTRA 1800) - lieka SKILL.md.

- **DXF viena grupė (AAA, 2026-10-09):** visi objektai modelspace be blokų - Corel sugrupavo į vieną grupę. Pataisyta v70.
- **„s" lanko galas be skylės (AAA, 2026-10-09):** apatinis bėgelis kirto „s" lanką prie bėgelio galo, ašyje skylė
  netilpo - skriptas paliko tik galiuko skylę, lankas neprispaustas. Pataisyta v69 (papildoma skylė, iki 8 mm nuo ašies).
- **D11 siaurame ruože (AAA „d", 2026-10-09):** `p6_dxf.py` v66 dėjo D11 prie raidės centro ir mažino atstumą iki
  krašto (10 mm) - skylė „d" lanko ir kojelės jungtyje, kur dės LED. Pataisyta v68: pirma pilni 20 mm visoje ašyje.
- **Apatinis bėgelis per trumpas (AAA „Bandymas", 2026-10-09):** bėgelis 151-181 mm „s" raidės apačioje negalėjo
  turėti abiejų kampų 10 mm viduje, galas sustojo „s" kairiame galiuke (2523 vs 2683). Sprendimas - bėgelis +5 mm
  aukštyn (156-186), galas 10 mm nuo „s" išorinio krašto. Taisyklė - „Bėgelis per VISĄ raidžių eilę (v67)".
- **Fasado eskizas apverstas (Clas Ohlson Horten 3, 2026-10-09):** plano eskizas paimtas kaip vaizdas iš priekio - kairė / dešinė sukeistos. Visada patikrinti, iš kurios pusės nupieštas planas, ir paklausti, jei neaišku.
- **DETAIL A folded lape buvo visada 5S** (PVC + A/B), nors juostoje P6_8mm - pataisyta v28 (pagal `front`).
  Etalono 225960 18 lapo DETAIL A turi tą klaidą - perdarant naudoti v28.
- **Folded laidas buvo „D11 bet kur ant fono"** - neteisinga, v28: tik po raide -> skylė užlenktoje briaunoje.
- Bezier valdymo taškai išsikiša už kontūro - nulis ir gabaritai skaičiuojami iš tikros geometrijos
  (įgyvendinta; MATKROKEN 703, ne 708).
- Trūkstamą RAL spalvą įrašyti į RAL lentelę (`lapas_core.py` ir `braizyti_lapa.py`), kitaip piešiama pilka.
  Trūkstamą 3M plėvelės kodą - į `VINYL` (`lapas_core.py`), kitaip FINISH langelis lieka neužpildytas.
- PyMuPDF `rect` CorelDRAW sudėtiniams keliams gali būti klaidingas - gabaritus skaičiuoti iš taškų;
  viename kelyje gali būti visos raidės - skaidyti į raides (įgyvendinta).
- Šoninis vaizdas - realus vaizdas, ne pjūvis. 3D - tikras 3D, ne pasvirusios kopijos.
- Neįterpinėti paveikslų / renderių iš pavyzdžių - viską braižyti pačiam CAD stiliumi.
- Didelės tuščios vietos lape ir nevienodo dydžio vaizdai - keisti išdėstymo vertinimą, ne pozicijas.

- **3D žyma ant objekto** (2026-10-15, danbolig DB-0001): „SIDE A / SIDE B" buvo rašoma ant stiklo 3D vaizde. Žymos - tik šalia
  objekto (`lapas_core.side_label_3d`, SKILL taisyklė 27).
- **Senas generatorius be naujų taisyklių** (2026-10-15, danbolig DB-0001): `sviesdeze.py` naudotas neperskaičius naujesnių
  šviesdėžių modulių (kojos per galinį statmenį, exploded > top view). Prieš šviesdėžę - SKILL taisyklė 26.
- **Spalvos kodas be spalvos BOM** (2026-10-15, danbolig): NCS S 8010-R90B ir 3M 100-54 langeliai buvo balti (nebuvo NCS / 3M
  kodų bibliotekoje). Dabar `ncs_hex` + `VINYL` / `PMS`; naują kodą - įrašyti. SKILL taisyklė 28.
- v322 (Rytis 2026-10-16, „blogas 3d atvaizdavimas", P6 ant folded / FRISK): braizyti_lapa 3D - raidžių šonai nesimatė (raidės plokščios
  su „spygliais" kampuose). PRIEŽASTIS: korpusas `sol.buffer(-inset)` grąžina CW kontūrą, normalės atvirkščios - išoriniai šonai
  atmesti, matėsi tik vidiniai. Dabar kiekvienas poligonas `orient(..., 1.0)` prieš šonų skaičiavimą; šonai tamsinami iki 80 %
  (balti šonai ant baltos raidės nesimatė), tamsaus fono (RAL 9005) atlankai - ne tamsesni už 30 % pilką. Bet koks naujas
  3D: po `buffer()` / `difference()` VISADA orient prieš normalių skaičiavimą (K.View3D.solid tai daro).
- v325 (Rytis 2026-10-16, P6 ant folded galinis vaizdas): balionai 9 / 6 ir laido Ø11 briaunos matmuo „15" su rodyklėmis - vienas
  ant kito (patikra netikrino teksto balione - balionų skaičiai buvo išimti iš 2 TEKSTAS ANT TEKSTO). Dabar patikra 27
  BALIONAS UŽDENGTAS; braizyti_lapa balionus deda priešingoje pusėje nei laido išvestis.

