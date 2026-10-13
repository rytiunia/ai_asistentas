# P10 - dvipusė šviesdėžė, Alu korpusas su IŠKIŠTU stiklu (push-through) (v196, Rytis 2026-10-13)

Etalonas (kliento brėžinys): `assets/etalonai/P10_sviesdeze_dvipuse_600x600x80_kliento.pdf` - 600 x 600 x 80, 100 nuo sienos,
Parts List: 1 Frame, 2 Front 2 mm Alu, 3 Back 2 mm Alu, 4 / 5 10 mm white plexi (iškištas), 6 / 7 3 mm white plexi (pagrindas), 8 LED.
Raktažodžiai: P10, push-through, iškištas stiklas, dvipusė šviesdėžė Alu korpusu su išpjova.

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
- Pagrindo tvirtinimas: 15 mm nuo išpjovos kontūro (į išorę) - Ø8 skylės pagrinde, žingsnis ~100 mm (Rytis rašė „~10" - PATIKSLINTI);
  tose pačiose vietose ant Alu (vidinėje pusėje) - D6 MĖLYNI HAIRLINE žymėjimai: ten prišaunami ilgasriegiai (stud welding),
  ant jų užmaunamas 3 mm pagrindas ir prisukamas veržlėmis.

## 3. Rėmas (1)
- Profilis pagal dydį: nuo □30x30x2 iki □60x60x3 (laikantysis); □20x20x2 - TIK papildomas, nelaikantis.
- Kojos / montavimas prie sienos: atskiros plokštės ARBA vientisa plokštė - pagal klientą arba pagal rėmą (spec `"plates"`:
  `"separate"` | `"single"`). Kitais atvejais - kaip `scripts/sviesdeze.py` (v134 / v144 principai).

## 4. LED ir maitinimas
- LED - Kaisen DUOLITE (kaip dvipusėms dėžėms, `kaisen_led.json` -> `duolite`).
- PSU vieta ir laidas - pagal dydį ir kliento užklausą (spec `psu`, `cable`); nenurodyta - klausti.

## 5. Dar neatsakyta (klausti, lape - tuščia vieta)
- Korpuso / rėmo / kojų spalvos (RAL), plexi rūšis (opal WN770 ar kt.), plėvelė ant plexi.
- Gamybos failai: Alu priekio / galo išklotinės DXF (išpjova, varžtų skylės, D6 žymės), 3 mm pagrindo ir 8 / 10 mm įdėklų CNC DXF,
  rėmo pjaustymo sąrašas - patvirtinti.
- Ø8 skylių žingsnis pagrinde (~100 mm?).
