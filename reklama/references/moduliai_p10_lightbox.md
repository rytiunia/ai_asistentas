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

## 4. LED ir maitinimas
- LED - Kaisen DUOLITE (kaip dvipusėms dėžėms, `kaisen_led.json` -> `duolite`).
- PSU vieta ir laidas - pagal dydį ir kliento užklausą (spec `psu`, `cable`); nenurodyta - klausti.

## 5. Spalvos, plėvelė, gamybos failai (Rytis 2026-10-13)
- Spalvos (korpusas, rėmas, kojos, plexi) - PAGAL KLIENTĄ (spec `body_finish`, `frame_finish`, `plexi`); nenurodyta - tuščia vieta.
- Plėvelė ant plexi - būna, pagal užklausą (spec `film`; sunaudojimas - `plevele.py`, nesting atskiriems įdėklams).
- Gamybos failai (Ryčio patvirtinta mano rekomendacija): A3 lapas + vienas DXF `<out>_gamyba.dxf`:
  Alu priekio (A) ir galo (B) padėklų išklotinės FACE OUT (CUT, BEND_UP_90, HOLES_D3.2, CUTOUT_LOGO = kontūras + 0,7,
  MARK_D6_STUDS - mėlynos D6 žymės), sienos pusės flanše - kojų išpjovos; 3 mm pagrindai (PLEXI_BASE_3MM + PLEXI_BASE_HOLES_D8);
  8 / 10 mm įdėklai (PLEXI_INSERT); rėmo pjaustymo sąrašas - lape (BOM 1).

## 5a. Lapų struktūra (v198, Rytis: „nėra detalizacijos ir suprantamo pjūvio", pagrindas - double-sided šviesdėžės)
Kaip `sviesdeze.py` + surinkimo lapas - 3 A3 lapai viename PDF:
- 1 / 2 GA: FRONT A, VIEW FROM WALL (kojos, plokštės, padėklų siūlė punktyru), FRONT B (veidrodis), SECTION A-A per logotipo
  centrą (padėklai, flanšai, išpjovos tarpas, įdėklai, pagrindai, rėmas, DUOLITE spinduliai; grandinė `prot | D | prot`),
  3D A / B, TOP VIEW (varžtai, siūlė); juostoje DETAIL B - išpjovos kraštas (mastelis 2:1 / 1.5:1 / 1:1 pagal vietą:
  Alu, tarpas, įdėklas, pagrindas, ilgasriegis + veržlė), BOM, MAIN DATA.
- 2 / 2 FRAME + LED + PARTS: rėmas su LED eilėmis ir C-C, SECTION C-C (LED) 1:2, PLATE 1A 1:2, FRONT A išklotinė 1:10
  (lenkimo linijos raudonos, Ø3.2, išpjova, D6 mėlynos žymės), BASE + INSERT vaizdas; juostoje LED lentelė, pjaustymo sąrašas, MAIN DATA.
- 3 / 3 ASSEMBLY (v199, Rytis: „reikia exploded view, nes niekas neaišku"): sprogstamasis 3D vaizdas išilgai gylio -
  padėklas A (išorė, kojų išpjovos flanše) - įdėklas A - pagrindas A su Ø8 - veržlės - rėmas + kojos + plokštės + DUOLITE -
  veržlės - pagrindas B - įdėklas B - padėklas B (vidus su ilgasriegiais); varžtai ištraukti virš flanšų; ašys ilgasriegis ->
  veržlė; dešinėje STEP 1-6 surinkimo eiga (rėmas, LED, padėklai + ilgasriegiai, įdėklas ant pagrindo, pagrindas ant
  ilgasriegių, uždarymas); juostoje DETAIL B + BOM + MAIN DATA.
- BOM pozicijos = balionėlių numeriai visuose lapuose; DXF nepasikeitęs.

## 6. Generatoriaus prielaidos (PASIŪLYMAI - Rytis dar netvirtino)
- Rėmo profilis pagal didesnę kraštinę: <= 1000 - □30x30x2, <= 1600 - □40x40x2, <= 2500 - □50x50x3, daugiau - □60x60x3 (spec `frame`).
- Rėmas: tarpas iki padėklo 1 mm (`clear`), kojos - pratęsti viršutinis / apatinis skersiniai; plokštės pagal etaloną 66 x 67 x 8, Ø10
  kojos ašyje (`plate`, `plate_hole_d`); `"plates": "single"` - viena plokštė per abi kojas.
- Padėklų varžtai - folded standartas (Ø3.2 viršutiniame / apatiniame flanše, 7 nuo krašto, 50 nuo galų, ~300); įleidžiami -
  `"screws": "countersunk"`.
- DUOLITE ant viršutinio ir apatinio skersinio; gylis < 100 (lentelės min) - perspėjimas, ryškumą tikrinti.
