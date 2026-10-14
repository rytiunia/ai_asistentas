# P10_lightbox - dvipusė šviesdėžė, Alu korpusas su IŠKIŠTU stiklu (push-through) (v196-v197, Rytis 2026-10-13)

**Pavadinimas `P10_lightbox`** (Rytis: „yra ir P10 raidės" - NEPAINIOTI su P10 raidžių profiliu). Generatorius `scripts/p10_lightbox.py`
(`python3 scripts/p10_lightbox.py spec.json out.pdf` -> A3 lapas + `out_gamyba.dxf`), testas `scripts/projektai/p10_lightbox_test/`.

Etalonas (kliento brėžinys): `assets/etalonai/P10_lightbox_dvipuse_600x600x80_kliento.pdf` - 600 x 600 x 80, 100 nuo sienos,
Parts List: 1 Frame, 2 Front 2 mm Alu, 3 Back 2 mm Alu, 4 / 5 10 mm white plexi (iškištas), 6 / 7 3 mm white plexi (pagrindas), 8 LED.
Raktažodžiai: P10_lightbox, P10 lightbox, push-through, iškištas stiklas, dvipusė šviesdėžė Alu korpusu su išpjova.

## 1. Korpusas - priekis ir galas = FOLDED PLATE principas
- Priekis ir galas - 2 mm Alu lankstyti padėklai (kaip folded plate, `references/moduliai_folded.md`): kiekvieno flanšas =
  PUSĖ bendro tūrio (gylio), sandūra gylio viduryje. Išklotinė, kampų išpjovos, lenkimo atskaita - kaip folded (`folded_dxf.py`).
- Tvirtinimas prie rėmo - VARŽTAIS per flanšus, žingsnis - standartas iš folded plate; kartais įleidžiamais (potaipiniais) -
  tik kai nurodyta užsakyme (spec `"screws": "countersunk"`).

## 2. Logotipas / tekstas - išpjova Alu + plexi
- Alu išpjova = plexi kontūras + TARPAS ~0,7 mm vienai pusei (standartas, `cut_gap` 0.7).
- Plexi variantai (spec `"glass"`):
  - `"3"` - tik 3 mm plexi iš galo (už išpjovos);
  - `"3+2"` - 5 mm: 3 mm pagrindas + 2 mm įdėklas išpjovoje, LYGIAI su Alu priekiu;
  - `"3+8"` / `"3+10"` - 3 mm pagrindas iš galo + PRIKLIJUOTAS 8 / 10 mm iškištas (išsikišimas = įdėklo storis - Alu storis,
    pvz. 10 - 2 = 8). Lape 10 mm (8 mm) nurodoma tik, kad PRIKLIJUOTAS.
- 3 mm pagrindas (6 / 7): kontūras = raidžių (išpjovos) kontūras + ~30 mm į išorę, SUAPVALINTAS, artimi elementai SULIETI į vieną
  pagrindą (buffer +30 round, union).
- Pagrindo tvirtinimas: 15 mm nuo išpjovos kontūro (į išorę) - Ø8 skylės pagrinde, žingsnis ~100 mm (Rytis patvirtino);
  tose pačiose vietose ant Alu (vidinėje pusėje) - D6 MĖLYNI HAIRLINE žymėjimai: ten prišaunami ilgasriegiai (stud welding),
  ant jų užmaunamas 3 mm pagrindas ir prisukamas veržlėmis.

## 3. Rėmas (1)
- Profilis pagal dydį: nuo □30x30x2 iki □60x60x3 (laikantysis); □20x20x2 - TIK papildomas, nelaikantis.
- Kojos / montavimas prie sienos: atskiros plokštės ARBA vientisa plokštė - pagal klientą arba pagal rėmą (spec `"plates"`:
  `"separate"` | `"single"`). Kitais atvejais - kaip `scripts/sviesdeze.py` (v134 / v144 principai).
- RĖMO VARIANTAI (v202, Rytis 2026-10-13):
  * **A (numatytas):** □ vamzdžių rėmas gylio centre, kojos = pratęsti viršutinis / apatinis skersiniai, statmenys tarp jų,
    plokštės 1A ant kojų galų (atskiros arba `"plates": "single"`).
  * **B (v211, Rytis 2026-10-14 - kojos SIAURESNĖS už dėžę; spec `"legs": {"spacing": <kojų ašių atstumas>, "yc": <centras>}`,
    numatyta yc = H / 2):** skersiniai - tik rėmo plotyje; kojos eina PER galinį (sienos pusės) statmenį - jis iš kelių dalių,
    kojos įvirintos tarp jų (dalių ilgiai lape ir BOM pjaustymo sąraše); montavimo plokštė VIENTISA, aukštis = kojų matmuo
    (spacing + kojos profilis), privirinta prie abiejų kojų galų. Plokštės skylės: MIN 4, kiekis pagal dydį (laisva zona tarp
    kojų, ~120 žingsnis, lyginis); plati plokštė (>= 7 Ø) - 2 stulpeliai, SIAURA - ŠACHMATINE TVARKA (kaip CEOS mažo pilono
    padas, Thales D059422). Lape PLATE 1A gulsčiai. Testas `scripts/projektai/p10_lightbox_test/spec_B.json`.
    **KOJŲ UŽDENGIMAS (v212, Rytis 2026-10-14; kaip sviesdeze v144):** 2 dalys A + B (veidrodinės), Alu 2 mm, korpuso spalva,
    aukštis = kojų matmuo, ilgis 5 mm MAŽESNIS už kojų tarpą (korpusas - plokštė): PO 2.5 mm iš abiejų galų; kojos po juo -
    punktyru; BOM 11. **v214:** plotis 10 mm DIDESNIS už kojų profilį (30 -> 40 = 20 + 20, kiekviena dalis 20; `cover_w`);
    viršuje 2 x Ø3.2 prisukimui (7 nuo krašto); priekyje ir gale (prie korpuso / plokštės) - standumo briaunos 10 mm;
    exploded view - abi dalys ištrauktos į šonus; išklotinė DXF (folded v173: atlankai 20 - t, briaunos 10 - t).
    **v215:** briaunos remtųsi į kojas - TIES KOJOMIS briaunose IŠPJOVOS (nuo laisvo krašto, gylis = kojos/2 + tarpas -
    (plotis/2 - briauna), □30 -> 6 mm; ilgis = kojos profilis + 2 x tarpas); atlankai remiasi į kojas -> aukštis = kojų matmuo + 2t;
    exploded view uždengimai pakelti virš rėmo, ne priglausti. v217: geometrija / DXF - bendras `scripts/koju_uzdengimas.py`.
  * Kitas rėmo principas - neišgalvoti, laukti Ryčio aprašymo / eskizo.

## 4. LED ir maitinimas
- LED - Kaisen DUOLITE (kaip dvipusėms dėžėms, `kaisen_led.json` -> `duolite`).
- PSU vieta ir laidas - pagal dydį ir kliento užklausą (spec `psu`, `cable`); nenurodyta - klausti.

## 5. Spalvos, plėvelė, gamybos failai (Rytis 2026-10-13)
- **v220 (Rytis 2026-10-14): dažosi tik kojos (+ plokštės) ir padėklų išorė; rėmas viduje ir padėklų vidus - BALTI (geresnis švietimas)** - SKILL „Bendrinės taisyklės" 21.
- Spalvos (korpusas, rėmas, kojos, plexi) - PAGAL KLIENTĄ (spec `body_finish`, `frame_finish`, `plexi`); nenurodyta - tuščia vieta.
- Plėvelė ant plexi - būna, pagal užklausą (spec `film`; sunaudojimas - `plevele.py`, nesting atskiriems įdėklams).
- Gamybos failai (Ryčio patvirtinta mano rekomendacija): A3 lapas + vienas DXF `<out>_gamyba.dxf`:
  Alu priekio (A) ir galo (B) padėklų išklotinės FACE OUT (CUT, BEND_UP_90, HOLES_D3.2, CUTOUT_LOGO = kontūras + 0,7,
  MARK_D6_STUDS - mėlynos D6 žymės), sienos pusės flanše - kojų išpjovos; 3 mm pagrindai (PLEXI_BASE_3MM + PLEXI_BASE_HOLES_D8);
  8 / 10 mm įdėklai (PLEXI_INSERT); rėmo pjaustymo sąrašas - lape (BOM 1).

## 5a. Lapo struktūra (v201, Rytis 2026-10-13: „reikia viską sutalpinti į vieną lapą")
VIENAS A3 lapas (buv. 2-3 lapai - v198 GA + FRAME/LED/PARTS, v199 ASSEMBLY):
- 1 eilė: FRONT A, VIEW FROM WALL (kojos, plokštės, siūlė punktyru), FRONT B (veidrodis) - mastelis automatiškai
  (`scale_ga`, 600 dėžei 1:12); SECTION A-A per logotipo centrą (~1.6 x priekio mastelio, 600 dėžei 1:8);
  FRAME (1) + LED (8) su matmenimis, po juo PLATE 1A.
- 2 eilė: 3D A, 3D B, ASSEMBLY - EXPLODED VIEW (tray A - insert 4 - base 6 + veržlės - rėmas + LED - base 7 - insert 5 - tray B,
  balionai = BOM), TOP VIEW (varžtai, siūlė).
- Juosta: DETAIL B (išpjovos kraštas), BOM, MAIN DATA, antspaudas.
- Išimta (v200-v201): pagrindo / įdėklo vaizdas, Alu išklotinė, SECTION C-C, LED lentelė, pjaustymo sąrašas -
  išklotinės, pagrindai su Ø8 ir įdėklai lieka gamybiniame DXF; priekio grandinėje koja + plokštė = iškyša (100).

## 6. Generatoriaus prielaidos (PASIŪLYMAI - Rytis dar netvirtino)
- Rėmo profilis pagal didesnę kraštinę: <= 1000 - □30x30x2, <= 1600 - □40x40x2, <= 2500 - □50x50x3, daugiau - □60x60x3 (spec `frame`).
- Rėmas: tarpas iki padėklo 1 mm (`clear`), kojos - pratęsti viršutinis / apatinis skersiniai; plokštės pagal etaloną 66 x 67 x 8, Ø10
  kojos ašyje (`plate`, `plate_hole_d`); `"plates": "single"` - viena plokštė per abi kojas.
- Padėklų varžtai - folded standartas (Ø3.2 viršutiniame / apatiniame flanše, 7 nuo krašto, 50 nuo galų, ~300); įleidžiami -
  `"screws": "countersunk"`.
- DUOLITE ant viršutinio ir apatinio skersinio; gylis < 100 (lentelės min) - perspėjimas, ryškumą tikrinti.

## 5b. DETAIL B (v213, Rytis 2026-10-14)
Juostos DETAIL B - pjūvis per VISĄ gylį (A | rėmas | B) TRIJOSE vietose, atskirtose nutraukimo linijomis: VIRŠUS (flanšai iki
siūlės, skersinis, DUOLITE, varžtai Ø3.2 per flanšą į skersinį 7 nuo siūlės), STIKLAS (Alu iki išpjovos, tarpas, iškištas
įdėklas, pagrindas, ilgasriegis + veržlė), APAČIA. **Ilgasriegiai PRIŠAUDYTI iš VIDINĖS Alu pusės - niekada nekiaurai priekį.**
Balionai - stulpeliais šonuose (= BOM).
