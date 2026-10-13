# AlfaNeon / DSV - kliento standartas

> v161, 2026-10-13: surinkta iš darbų aplanko `DARBAI/uzsienio reklama` (2024-2026) analizės; Rytis patvirtino, kad tai STANDARTAS. „(spėjimas)" - nepatvirtinta, prieš naudojant lape - klausti. Skyrius „Klausimai Ryčiui" - dar neatsakyta.

Raktažodžiai: DSV, AlfaNeon, Alfa Neon AB, DSVL25-, 3D Logo DSV indirect, Frontlit, DSV Flexible size, 2D logo DSV aluminium,
P3_letters, DSV-N-W / DSV-N-B. Užsakovas - **Alfa Neon AB** (Kil, Švedija); galutinis klientas - DSV (objektai visoje Europoje).
NAS: `/Volumes/dizainas/RYTIS/DARBAI/uzsienio reklama/AlfaNeon/DSV/` - `DARBINIAI/` (gamybiniai šablonai pagal produktą),
`orders/` (užsakymai), `info/` (Alfa Neon spec., logo, plokščių skaidymas), `DSV Service point/`, `DSV Letters lift/`, `DSV_profiles_template/`.
Visi produktai - FIKSUOTAS katalogas su DSV prekės kodais; naujam užsakymui nebraižoma iš naujo, imamas šablonas pagal kodą.

## DSV spalvos ir logotipo taisyklė
- Mėlyna: **RAL 5003** = Pantone 281 C = CMYK 100/85/5/40 = HEX #002664. Balta: **RAL 9010** (raidės / ACM).
- „Touch-up" purškikliai: mėlynas RAL 5003, baltas RAL 9003.
- Miltelinis dažymas: **60 % gloss** (PO „Gloss Level: 60 %"). Pirmas pavyzdinis (ALT7335, 32669) buvo 70-85 % - nebenaudoti.
- Kiekviename ACM / kasetės lape tekstas: „The minimum margin of space around the logo should be equal to the height of the logo."
  Iš to: logotipo aukštis = plokštės aukštis / 3, plotis ≈ 3,39 x aukštis (žr. lentelę žemiau).

## Kodų katalogas (DSVL25-xxxxx)
Dydžiai (logo plotis x aukštis, mm): Xsmall 1000x295, Small 2000x589(590), Medium 3000x883(885), Large 4400x1296(1298), Xlarge 6000x1767(1770).

| Produktas | Blue (RAL 5003) | White (RAL 9010) |
|---|---|---|
| 3D Logo DSV indirect illumination - Xsmall / Small / Medium / Large / Xlarge | 01008 / 01000 / 01001 / 01002 / 01006 | 01009 / 01003 / 01004 / 01005 / 01007 |
| 3D Logo DSV Frontlit illumination (P6) L1000 / 2000 / 3000 / 4400 / 6000 | 01010 / 01012 / 01014 / 01016 / 01018 | 01011 / 01013 / 01015 / 01017 / 01019 |
| DSV 2D logo (aluminium / ACM frezuotas) Small / Medium / Large / Xlarge | 07000 / 07001 / 07002 / 07006 | 07003 (spėjimas) / 07004 (spėjimas) / 07005 / 07007 |
| DSV Flexible size (logo ant ACM plokštės), kodas = 05000 + 2 x dydžio nr. (Blue lyginis, White nelyginis) | 05000 1000x250, 05002 2000x500, 05004 2500x625 (spėjimas), 05006 3000x750, 05008 4000x1000, 05010 5000x1250, 05012 6000x1500, 05014 7840x1920, 05016 10000x2500, 05018 12000x3000, 05020/05022 15000x3750 / 20000x5000 (spėjimas) | 05001, 05003, 05005 2500x625, 05007, 05009, 05011, 05013, 05015 7840x1920, 05017 10000x2500, 05019 12000x3000, 05023 20000x5000 |

Priedai: **DSVL25-07000-A** - Spray can blue RAL 5003 400 ml; **DSVL25-07000-B** - Spray can white RAL 9003 400 ml.
Dėžės: DSVL25-7000-A Wooden crate Flex.signs/2D 1-10 sheets; DSVL25-73000-3 Wooden crate M (3100/440/1150);
DSVL25-74400-6 Wooden crate L (4500/1000/1650). Pakavimo lapuose dar: 4500x550x1650, 4500x250x1650.
Šviesdėžė dvipusė: DSVO25-02010.
Kodų klaidos failuose (netikėti jomis): BLANKAS White lape 01002 vietoj 01003; ALT8642 „07006 White"; ALT8545 „05007 White 7000x750";
dėžės kodas „DSVL25-7000-A" sutampa su purškiklio „07000-A".

## 3D Logo DSV indirect illumination (P3 - „halo", šviečia atgal į sieną)
Šablonai: `DARBINIAI/DSV_P3_letters/gamybai/DSV_P3_letters_Blue|White/` (5 lapai L1000-L6000), FRANCE variantas atskirai.
Konstrukcija (visiems dydžiams): 1. Front - Aluminium sheet t=2 mm, 2. Side - Aluminium tape t=1 mm (abu RAL, Powder Coating 60 % gloss),
3. Back - **Plexiglas WN770 t=8 mm** (šviečianti nugara), LED „Inside letters" ant nugaros, trafo raidės viduje.
Priekio tvirtinimas - **Screws DIN 7982 C T 2,9x9,5 mm T10** („Front fitting screws positions" brėžinys + kabelio išėjimas).

| Dydis | Gylis | Tvirtinimas | LED | Trafo | Svoris | Kabelis |
|---|---|---|---|---|---|---|
| L1000 (1000x295) | 60 | D10x20 vamzdelių distanceriai 20 mm + fitting bolt 10 vnt. (be Z) | PRO190Lens 6500K 1,5 W | HLG-80 | ~8 kg | +1,5 m |
| L2000 (2000x589) | 70 | Z 30x30x3 (2 m), PVC guide 22x22x22 6 vnt., self tapping 5,5x50 9 vnt., fitting bolt 8x25 15 vnt. | PRO190Lens 27 vnt. 40,5 W | HLG-80 | ~15,2 kg | +1,5 m, ~42 priekio varžtai |
| L3000 (3000x883) | 80 | Z 40x40x3, PVC 32x32x32 6 vnt., 5,5x60 10 vnt., bolt 8x25 16 vnt. | P190L 49 vnt. 73,5 W | HLG-120 | ~30,5 kg | +2 m, ~59 |
| L4400 (4400x1296) | 100 | Z 40x40x3, PVC 10 vnt., 5,5x60 14 vnt., bolt 8x25 24 vnt.; plexi nugara iš 3 dalių | P190L 85 vnt. 127,5 W | HLG-150 | ~62,5 kg | +2,7 m, ~73 |
| L6000 (6000x1767) | 100 | 2 atskiros dalys (3420 + 2580); Z ant ženklo atskiri kiekvienai daliai, sieninis Z ištisinis; PVC 18, 5,5x60 18, bolt 8x25 30 | PRO320Lens 24V 2 W, 115 vnt. 230 W (79 + 36), WAGO jungtis | HLG-240-24V + HLG-150-24V | ~72,5 kg | +4,5 m, ~90 |

- Medžiagų kiekiai lape: L2000 1,2 m² / šonas 9,2 m; L3000 2,7 m² / 14 m; L4400 5,8 m²; L6000 10,6 m² / 28,5 m.
- Montavimas: „hanging profile" (Z) ant ženklo nugaros + sieniniai Z profiliai + „locking screws"; detalė „Z profile fixing with supports".
  Atstumas nuo sienos L2000 - 30, kitų - 40 (lapo pjūvis). Sieninių Z išdėstymas ir ilgiai - `DSV_wall_mounting/PROFILIAI_DSV.cdr`
  (2m_30x30Z, 3m_40x40Z, 4,4m_40x40Z); montavimo instrukcija `L2000/L3000/L4400/L6000_DSV_wall_mounting.pdf` - 6 žingsniai
  (lazeriu apatinė linija, apatiniai Z, viršutiniai Z - L2000 430 mm virš apatinių, užkabinti, nuleisti, nebūtini savisriegiai).
- Montavimo šablonai iš **10 mm FOREX**: DSV_3m (2956x729), DSV_4,4m, DSV_6m (ALT8527_06.17). Pavyzdiniame - „INCLUDING PAPER MOUNTING TEMPLATE".
- FRANCE variantas (L4400): Removable bolts, Lifting hooks, 30x30x2 kvadratinis profilis + 2 mm Al „support triangle"; po montavimo profilis
  išstumiamas pro šoną, ženklas pristumiamas prie sienos ir fiksuojamas.
- Kėlimo įrankis „DSV Signage lift" (MJ): plienas 150x50, 40x40, 40x20 + Lifting hook.
- Įtampos lipdukai (`Itampos_lipdukai`): „DSV L3000W | 92 | 0.4", „DSV L4400W/B | 161 | 0.7" + užsakymo nr. + data (spėjimas: W ir A).

DSV / Alfa Neon PO aprašas (tikrinti prieš lapą): „Aluminum letters Powder-coated, Rear panel made of 8 mm Plexiglas **GS Wh14**,
LED 6,500K, internal transformer **Mean Well HLG** & outdoor waterproof protection box, Depth 80 mm (Medium) / 100 mm (Large, Xlarge),
Wall distance 30 mm (point mounting no rail), Gloss 60 %". Mean Well HLG čia - kliento reikalavimas (ne Kaisen/BaltLED).

## 3D Logo DSV Frontlit (P6 - šviečia priekis)
Šablonai: `DARBINIAI/DSV_P6_letters/DSV_P6_letters_B|W/`, frezavimas `DSV_P6_frezavimui.cdr`.
- Front - Plexiglas WN770 t=8 mm (L1000-L3000); L4400/L6000 - WN770 t=4 mm + „1A Front fitting PVC plastic t=3 mm" + „Strengthening Al 2 mm".
- Exterior: Translucent foil **ORACAL 8500 006** (folijos sandūra „Folie overlap 5 mm", „Plexiglass connect point").
- Side Al tape 1 mm, Back Al sheet 2 mm (RAL, 60 %), Z profilis 20x20x2 (L1000) / 30x30x2 (L2000) / 40x40x2 (L3000+), PVC guide,
  fitting bolt M6x15, self tapping 5,5x30, „4mm fitting holes on a backside".
- LED PRO190Lens 6500K 1,5 W; trafo HLG-80 (L1000, L2000), HLG-120 (L3000), HLG-150 (L4400, L6000).
- Priekio varžtai DIN 7982 C T 2,2x6,5 T10 (L1000-L3000), 2,9x9,5 (L4400+).

## DSV 2D logo aluminium
- 3 mm ACM, RAL 5003 arba RAL 9010, CNC kontūrinis frezavimas, be apšvietimo (Tech. spec.: „aluminum letters powder-coated, flat").
- Small 2000x590; Medium 3000 (2 dalys 2419 + 581); Large 4400x1298 (3 dalys A/B/C, „The sign is made of three separate parts");
  Xlarge 6000x1758. Šablonai `DARBINIAI/2D Logo DSV ACM milled/` (DSV-letters_L2/L3/L4,4/L6-B|W). Dažniausiai su purškikliu 07000-A.

## DSV Flexible size (DSV logo on ACM plate)
- PO: „3mm aluminum composite (0,2 mm Alu on both sides)"; Blue RAL 5003 + white vinyl / White RAL 9010 + blue vinyl.
- Plėvelės lapuose: ant baltos - **ORACAL 751 CG-050** (anksčiau 551 050); ant mėlynos - ImagePerfect 2556PA Plus White Gloss arba ORACAL 551 101.
- Lapas „White/Blue 3mm ACM sheet with / without graphics****", serija DSV-N-W / DSV-N-B (`DARBINIAI/DSV logo on ACM plate_white|blue/`),
  sandūros tarpas **5 mm**, plokštės ≤ 2500 pločio, aukštis 1250 / 1500 / 957,5 (2 eilės).
- Plokštė -> logo (`info/DSV_size_on_a_ACM/detaliu skaidymas.cdr`): 1000x250 -> 282x83; 2000x500 -> 565x166; 3000x750 (2500+495) -> 847x250;
  4000x1000 (2500+1495) -> 1130x333; 5005x1250 (2x2500) -> 1409x415; 6000x1500 (990+2500+2500) -> 1695x500; 7840x1920 -> 2700x640;
  12000x3005 -> 3395x1001; 15025x3760 -> 4248x1253; 20000x5005 -> 5655x1668. Naujieji (2026-03, tik W): 2720, 4080, 5980, 8160.
- Užsakymo lape - dydžių juosta 1000 ... 20.000 mm ir pažymėtas užsakytas dydis.

## Šviesdėžės ir smulkūs
- **Single-sided lightbox 700x370x80** (patvirtinta, užsakymai po 100 vnt. ALT8220, ALT8861): korpusas 3 mm ACM Blue RAL 5003 (lankstytas,
  countersunk rivets/screws), dugnas 3 mm ACM, logo išfrezuotas, įleistas 4 mm baltas plexi („The plexiglass is inlaid"), trafo + LED ant 1,5 mm Al
  plokštelės, +1,5 m ~230V išvadas (kampe 50x50). LED (BaltLED pasiūlymas): Challenger 1 BMP-M1-O2UH160CW075 12V 0,75 W 6500K, 8 vnt., BPSP-20-12V.
- **Double-sided lightbox 700x370x80** + 100 flanšas (viso 800): rėmas 30x30x2 (+20x30x2) Al, montavimo plokštė 5 mm Al (Ø8), 4 mm baltas plexi,
  front/back 3 mm ACM, rėmo dangtis 3 mm ACM, LED Crown Duo W2 24V (BMP-W2-DS765E2 2 W, 4 vnt.), trafas LPV-20-24. Pirmesnė versija
  (ALT7855, WN770 8 mm + Mini Sem 1 + KPS-20 + kojos 40x40x4) - nebenaudojama.
- **DSV Flat sign** 420x297 3 mm ACM + polymeric foil digital print + gloss laminate (logo 265x78); **sticker** 210x148 (logo 133x39) skaidri plėvelė.
- **Cassette** 3500x1800x50, 2 mm Al folded plate RAL 9010 + ORACAL 751 CG-050 logo 2200x650, varžtai DIN 7504 N 4,2x16 T20.

## Užsakymų dokumentavimas
- Aplankas `orders/DSV order NNNNN/`: `Purchase order NNNNN.pdf` + `NNNNN.xml` (Monitor ERP ORDERS420 - kodas, kiekis, aprašas, pristatymo adresas,
  Goods label + Ref.no.), `ALT####_MM.DD_DSV order NNNNN.cdr/.pdf/.jpg`, `Drawing_*.pdf`. Pristatymas DAP, „Direktleverans" į DSV objektą, padėklas.
- Užsakymo lapas A3: antraštė pagal šeimą („3D_logo_DSV_indirect Blue", „DSV_flexible_size", „2D_logo_DSV_aluminium"), 6 langeliai:
  „N pcs." juodame fone + kodas + pavadinimas + logo su gabaritais. Apačioje: užsakymo pavadinimas | ALFA NEON logo | ALT####_MM.DD + autorius | Sheet.
  Keli lapai - po vieną šeimai; gale „Packing_list" (dėžių nr. ir turinys, pvz. „#777 L4400 - 1 vnt.").
- Šablonas: `orders/BLANKAS_ATNAUJINTAS 03.27.cdr` (7 lapai: indirect Blue, indirect White, Frontlit Blue, Frontlit White, Flexible x2 + spray, 2D).
- Remontas / trūkstama dalis - tas pats lapas su pastaba („Only the missing part of the existing sign will be manufactured. Old order ALT8293...").
- Gamybiniai lapai (`DARBINIAI/`) - ALT0000_00.00_rycka, DSV ženklelis su „Quantity x*", dydžiu, spalva, mastelu ir svoriu, BOM lentelė Pos/Name/Material/Quantity/Notes.

## Etalonai
- `AlfaNeon/DSV/orders/BLANKAS_ATNAUJINTAS 03.27.cdr` - užsakymo šablonas, kodai.
- `AlfaNeon/DSV/DARBINIAI/DSV_P3_letters/gamybai/DSV_P3_letters_Blue/pdf/DSV_P3_letters_Blue.pdf` - P3 L1000-L6000 BOM.
- `AlfaNeon/DSV/DARBINIAI/DSV_P3_letters/gamybai/DSV_wall_mounting/L2000_DSV_wall_mounting.pdf` - montavimas.
- `AlfaNeon/DSV/orders/DSV order number 33541/` (PO + xml + ALT8823) - tipinis užsakymas.
- `AlfaNeon/DSV/DARBINIAI/DSV_lighbox_singleside/pirminiai/ALT7927_01.05_DSV_lighbox_singlesided_700x370mm_NEW_20260105.pdf`.

## Klausimai Ryčiui
1. Indirect nugara: lapuose Plexiglas WN770 8 mm, o DSV PO - „GS Wh14 8 mm". Kuris galioja?
2. White 3D Small: 01003 (ALT8642) ar 01002 (BLANKAS)? 2D logo White kodai 07003 / 07004 - ar teisingai Small / Medium?
3. Frontlit White - ar taip pat ORACAL 8500 006 folija (lapuose ta pati), ar be folijos?
4. PO rašo „Wall distance 30 mm, point mounting no rail", o gaminame su Z profiliais (40 mm L3000+). Ar PO tekstas tiesiog senas?
5. Ar Frontlit (P6) ir dvipusė šviesdėžė realiai gaminami, ar tik katalogo pozicijos?
