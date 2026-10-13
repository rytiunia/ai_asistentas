# BrandFactory (Norvegija / Švedija) - bendras standartas + tinklai be atskiro failo

> v161, 2026-10-13: surinkta iš darbų aplanko `DARBAI/uzsienio reklama` (2024-2026) analizės; Rytis patvirtino, kad tai STANDARTAS. „(spėjimas)" - nepatvirtinta, prieš naudojant lape - klausti. Skyrius „Klausimai Ryčiui" - dar neatsakyta.

Raktažodžiai: BrandFactory, Brand Factory Norge AS / Brand Factory Nordic AB, KIWI, MENY, JOKER, COOP, KFC, Boots apotek,
Norli, ALTI, OBS BYGG, ICA, Burger King, Konsulent / Tiltak / Tegning.
NEDUBLIUOJA: SPAR -> `klientai/spar_brandfactory.md` + `etalonas_spar_225960.md`; EXTRA -> `extra.md`; Clas Ohlson ->
`clasohlson.md`; KIWI 226023 / Joker 226001 -> `scripts/projektai/kiwi_226023/`, `joker_reinslettveien/`.
Šaltinis: NAS `/Volumes/dizainas/RYTIS/DARBAI/uzsienio reklama/Brandfactory/` (~3 760 .cdr, ~3 040 .pdf; 761 užsakymo
aplankas su ALT .cdr; 2023 - 65, 2024 - 449, 2025 - 528, 2026 - 627 ALT failų).

## 1. Užsakovas ir užsakymo dokumentai
- Norvegija: **Brand Factory Norge AS**, PB 98 Furuset, 1001 Oslo (sąskaitos / pristatymas - Prof. Birkelandsvei 27 B / 36,
  1081 Oslo), tel. +47 23 26 55 00, www.brandfactory.no. Švedija: **Brand Factory Nordic AB** (ICA, KFC, Clas Ohlson SE, BK).
- Užsakymo Nr.: NO - 6 skaitmenys **20xxxx-22xxxx** (pvz. 225670); SE - **39xxxx / 40xxxx** (ICA 399916, 401802; BK 394061).
  BF projekto Nr. (`Prosjekt`) - kitas 6 skaitmenų numeris 11xxxx-12xxxx (pvz. „Prosjekt: 116654 / 218845", „Joker Fyresdal
  Prosjekt 119008") - lape ORDER NO. rašomas užsakymo Nr., ne Prosjekt.
- Kontaktas (Vår referanse / Konsulent): **Birgit Wiig**; BF dizaineris **Freddy Wiig (FW)**, senesniuose - Freddy Skaugen.
- Užsakymo dokumentas `info/`: (a) NO „**Bestilling**" PDF `Order no NNNNNN.pdf` (Bestillingsdato, Prosjekt, Ønsket lev. dato,
  eilutės: BF art.nr. 100xxxxx + aprašymas, pvz. „MENY Fasadeskilt 4m GEN 3 - P01 + P6 vakumformet 4000x1720mm",
  „MENY Åpningstid H400mm 1 tegn Gen 3 - P6 H=400 D=60 8 STK"); (b) Monitor ERP **„Pirkimo užsakymas NNNNNN.pdf" + `NNNNNN.xml`**
  (ORDERS420: Buyer BrandFactory Norge AS, BuyerReference, GoodsLabeling = 2 nr. ženklinimui, DeliveryAddress - dažnai
  montuotojas, pvz. „BS Montasje, Sarpsborg", DeliveryPeriod, eilutės su matmenimis ir medžiagomis tekstu).
  Pristatymo adresą ir pakuotės žymėjimą imti iš čia (spėjimas: GoodsLabeling eilutės = ženklinimas ant pakuotės).

## 2. BF kliento brėžinio (info/) antraštė - kaip skaityti
BF lapas A3 gulsčias; viršuje eilutė „**<TINKLAS> - <objektas / tipas>**" + kontaktai; apačioje tamsi juosta:
`Tiltak:` (Skilt / Fasadeskilt / Pylonskilt / Sykkelstativ) | `Tegning:` (pavadinimas arba BF serverio kelias, pvz.
`U:\N\Norli\Design\Norli-Skilt-2023-400`, `L:\KKK\Kiwi\Elementer for tegning\Sykkelstativ\Sykkelstativ-03A`) |
`Konsulent:` / `Designer:` | `Dato:` / `Endret:` / `Rev.:` | `Skala:` (1:10, 1:20 A3, 1:25, 1:50, 1:100) |
`Adresse / Postnr. / Gnr./Bnr.` (kartais) | © tekstas: „Opphavsrettighetene til denne tegning tilhører Brand Factory Nordic AB
(senesni - Brand Factory Norge AS). Tegningen eller dens innhold kan ikke deles, kopieres eller på noe annet vis anvendes uten
vår tillatelse." - **mūsų lape šito teksto ir BF juostos NEKOPIJUOTI** (mūsų juosta - stilius.md).
BF tekste: profilio tipas („Profile 5s", „Profil 01+6 vakuumformet", „Profile 01+5", „Type 200/300/2000"), formatas,
„Frame Ral ...", gylis, „1 pc". BF „Profile 5 / 5s" mūsų lapuose dažnai daroma kaip Profile 6 (Norli 225670 - BF
„profile 5s 60 mm", mūsų „Profile 6, 60 mm") - neaišku -> klausti.

## 3. Aplanko ir failų struktūra (NAS)
- `Brandfactory/<TINKLAS>/<užsakymo aplankas>/` (didieji tinklai: SPAR, KIWI, MENY, JOKER, EXTRA, COOP, ClasOhlson, KFC, ALTI,
  Boots apotek, OBS BYGG, Burger King, POWER, ICA ...); vienkartiniai - tiesiai `Brandfactory/Order NNNNNN <objektas>/`.
- Aplanko vardas: „Order NNNNNN <objektas>" (159), „Order no NNNNNN" (95), „<TINKLAS>_Order no NNNNNN" / „<TINKLAS> order
  NNNNNN" (SPAR, KIWI, JOKER, COOP, EXTRA), SE - „PO NNNNNN ...".
- Viduje (iš 761): `ALTNNNN_MM.DD_<inicialai>.cdr` + to paties vardo `.pdf` (753), `Drawing_<aplanko vardas>.pdf` (627 - tas
  pats lapas klientui), `<aplanko vardas>.cdr` (darbinis), `Backup_of_*.cdr` (Corel), `info/` (178: BF brėžinys .pdf/.cdr,
  Bestilling / Pirkimo užsakymas, .xml, foto IMG_*.jpeg, el. laiškų image00N.png), kartais `pvz/` (analogai), `pirminiai/`,
  `foto/`, `3d/`. DXF aplankuose beveik nėra (3) - gamyba iš .cdr.
- ALT pavadinimas: `ALT<Nr>_<MM.DD>_<inicialai>` - rycka (Rytis), MJ, nuo 2026 - RS; nepatvirtintas - `ALT0000_00.00_<inicialai>`.
- Tinklų etalonai: `KIWI/ETALONAS/` (+ `ETALONAS 2026`, `ETALONAS 2027`, `OLD`), `MENY/ETALONAI/`, `JOKER/ETALONAS_2026/`,
  `Boots apotek/etalonas/`, `KFC/Etalonas/`, `ClasOhlson/ETALONAI/`.

## 4. Senasis ALT lapas (Corel šablonas, BF užsakymai 2023-2026)
A3, rėmelis su zonomis 1-8 / A-F. Kairėje viršuje juoda žyma **„N pcs."** (šalia gali būti „Interior", „ST").
Apatinė juosta: `<užsakymo aplanko vardas>` | `BrandFactory` | `ALTNNNN_MM.DD_rycka` | `Sheet n of N`.
Dešinėje pilka kolona: viršuje skirtukas **„Profile N"** (6, 10 ...) + 3D sprogdintas raidės vaizdas ir pjūvis su
pozicijų numeriais 1-8 ir raidėmis „A. Fitting edge (PVC) / B. BOLTS"; po juo spalvoti blokai, kairėje kiekvienos eilutės -
varnelės langelis, dešinėje - pozicijos Nr. (juodas kvadratas):
| Juostelė (spalva) | Blokas | Tipinis turinys |
|---|---|---|
| **P / PRODUCTION** (geltona) | MOUNTING WAY: | „Aluminium U profiles, 30x30x2mm" (5), „30x30x30x2mm fitting L profile" (6), „Background, 1.5mm Alu", „Welded fasteners", „Mounting plate, 8mm Alu" |
| **C / CUTTING** (žalia) | MAIN MATERIALS: | „Front: White 8mm (3mm) plexiglas" (1), „Side: aluminium 1mm" (2), „Backside: aluminium 1.5mm" (3), „Fitting egde, 3mm PVC" (A) |
| **B / BENDING** (violetinė) | DEPTH: | „70 mm" + „Exterior" / „Interior" |
| **P / PAINTING** (oranžinė) | BODY COLOR: / SIDE COLOR: + MOUNTING FRAME / PROFILE COLOR: (arba WALLFRAME / BACKGROUND COLOR) | RAL / NCS su spalvotu langeliu |
| **I / INSTALLATION** (žalsvai mėlyna) | LED: | „LED" (4) + „WHITE 6500K" |
| **FRONT / COLORS** (mėlyna) | COLORS: + PERIMETER: | plėvelių kodai su spalvotu langeliu; „6 meters" |
Laidas lape: raudonas žaibas + „+1,5m ~230V El. Output" (PSU raidėje) arba „+1,5m 12V El. Output" (trafo box atskirai);
„+3m 12V BLACK el. cable", „PWM + potentiometer". Didesniuose (KIWI) - lentelė „Materials to make one unit" /
„Medžiagų žiniaraštis vienam gaminiui" (Poz., Detalės pavadinimas, Medžiaga su lydiniu AW-1050A H24 / AW-6060/6063 T6, kiekis
b/m / m² / vnt., pastabos) + „Perimeter NN m". (Spėjimas: C/B/P/I juostelės = gamybos etapai, varnelės - pažymėti atliktą.)
Naujiems lapams galioja `stilius.md` / SPAR etalonas; šis šablonas - tik kaip skaityti senus BF užsakymus ir ką jie turi turėti
(blokų turinys = mūsų MAIN DATA / BOM laukai).

## 5. Bendra BF užsakymams (kas kartojasi)
- P6 raidės: priekis balta plexi **8 mm** (dažniausiai) arba **3 mm + PVC 3 mm fitting edge**, šonai Alu 1 mm, galas Alu 1,5 mm;
  vidaus raidės - Profile 10 = balta plexi **30 mm** (Boots, MENY vidaus) arba 20 mm skaidri + vinyl wrapped (OBS margos).
- Rėmas: Alu U 20x20x2 / 25x25x2 / 30x30x2 + L tvirtinimo plokštelės („Aluminium L profile fitting plates, 6 pcs., Ø6 mm
  holes", 25-30 mm pločio; 25x25 ir didesniems - Ø8); rėmas paprastai matinis RAL (7035 matt, 7024, 8011, 9006 ...).
- LED baltas, „WHITE 6500K"; PSU - Kaisen KPS (KPS-V12-40W, KPS-60-12, KPS-100-12); laidas 1,5 m (12V arba ~230V), 3 m 12V black.
- Back plate / folded: Alu 2 mm (1,5 mm) užlenkta, briauna 40 mm; tvirtinimas L 30x30x2 + varžtai + DIN 7504 N 4.2x16 T20
  savisriegiai; 2700 x 2100 - iš 2 dalių 1400 + 700, sujungiama varžtais („! Plate from 2 parts!") - kaip SPAR.
- Plėvelės: Oracal 551 (lauko), 8500 (šviečiančioms), 641; 3M 3630; Mactac 9849-55 (KIWI žalia); spauda Gel'UV + gloss laminate.

## 6. Tinklai

### KIWI (29 imties failai; NO)
- BF „Standard for storage": Profile 5s, šviesa raidėse (didesniems 150-190 - P4), gylis 100 mm, LED white / green / red,
  Alu 2 mm, frosted akrilas, žalia PMS 361 / raudona Fasson 987, juoda matinė; „barring profile" RAL 7024 (senesni 1013 /
  3012 / 8011), „Sometimes special ordered with different color on frame".
- Etalonai `KIWI/ETALONAS/ETALONAS 2027/`: KIWI L1535, L2180, **L3362 (minipris 3362 x 1095)**, 7-23 L1660 / L1991; 2026 -
  7-23 L1328, kolona, `pilonas_H5000/` (8 lapai, balta plexi T10, galų užlenkimas 69°); OLD - L3992, 7-23 L935-2423, 8-21, Son 9-21.
- L3362 (ALT8757, 225704): rėmas Al kvadratinis 40x20x2 RAL 7024, padalintas tarp KIWI ir minipris („divided", jungtis
  15x15x2), fitting plates 40 x 75 Ø8 - 14 vnt., KIWI - 3 mm stiklas, minipris - 8 mm; Mactac 9849-55 + Oracal 641-070;
  Plexiglas WH02SC 3 mm, PVC juosta 3 mm, drenažo skylės, 1:1 „Frame welding template" (šabloninis popierius); perimetras 25 m.
  LED P130 (1W) green 61 + white 42 vnt., 12V 3 m išvestys. ETALONAS 2027 L3362: rėmas RAL 3003, P130 green 85 + P65 white 63,
  trafai RAIDĖSE (KPS-V12-100W 1 + KPS-20W 2), laidas 230V 9 m.
- Kiti KIWI: bendri trafai (Order 221846, KPS-100-12 / KPS-60-12, „Converterbox RAL 7024 / 8011, dimmable converter"),
  laido išvestys virš rėmo, Bicycle rack (5 mm plienas, ground mounted - BF brėžinys), Lanterne (RAL 6018) - 226023.
  Etalonai: `KIWI/KIWI order 225704/ALT8757_09.11_KIWI order 225704.cdr`, `KIWI/ETALONAS/ETALONAS 2027/ETALONAS_KIWI L_3362.cdr`.

### MENY (17; NO) - Logo Gen. 3 „P01 + P6 vakuumformet"
- Logo formatai (BF): **2000 x 860, 3000 x 1290, 4000 x 1720** (lankas; 4000 - stygos 3028 / 2990 mm).
- Konstrukcija (ALT8675, 225437 - 5 lapai): (1) termoformuotas gaubtas **3 mm PLEXIGLAS GS 3H25** (raudonas; senesni - XT 3H25),
  ilgiems - „Plexiglas connect" (2 dalys); (2) priekio rėmelis Alu 2 mm RAL 7047; (3) dugnas 2 mm / šonai 1,5 mm Alu su
  **RAUDONAIS LED**, RAL 7047; (4) šoniniai laikikliai Alu 2 mm (~20 vnt.); (6) raidės P6, balta plexi, korpusas RAL 7047,
  klijuojamos prie priekio; (7) rėmas U 25x25x2 + Z, RAL 7047 matt; (8) **wallframe Z 30x30x3 + 20x20x2** (+ lifting hooks),
  spalva pagal objektą (RAL 7024 / 7037 / 8011 / 8024 / 3009 / 7047 matt). Gyliai 35 + 45 + 50 = 130 mm; raidės (A) 50 mm.
  Laidai aliuminio juosta (cable supports). „Converter box RAL 7024 - PWM: RED BACKGROUND + LETTERS" + potenciometras,
  +3 m 12V black. Termoformai: forma iš 40 mm plokštės + 5 mm MDF pastorinimas + 2 mm PVC šablonas / 3D frezuota forma.
- Darbo valandos „8-22(8-20)": P6 (B) 60 mm ant U 25x25x2 + fitting plates (Ø6, 25 mm), H 227-330 (BF: H400 1 tegn).
- Vidaus MENY: 30 mm balta plexi, blockout vinyl gale, U 15x15x2, RAL 7016 gloss 30% powder coated; dvipusė šviesdėžė L1200
  (raudona GS 3H25 + 10 mm balta plexi įleistos raidės, koja Ø40, RAL 9006).
  Etalonai: `MENY/MENY order 225437/ALT8675_08.14_MENY order 225437.cdr`, `MENY/ETALONAI/MENY_L____/MENY_L4000_2025_letters.cdr`.

### JOKER (18; NO)
- Logo „Type 2000" L2000 (ETALONAS_2026/JOKER_L2000, ALT7449): 2000 x 762, P6 „joker" balta 8 mm, šonai RAL 9005, gylis 80
  (60 + 40 fonas), ant **folded Alu 1,5 mm fono, briauna 40** „Covered with folie": Oracal **551 022** (geltona), **551 603**
  (žalia), **551 701** (juoda), **8500 330** (raudonas taškas); montavimas L 30x30x2 + varžtai + DIN 7504 N 4.2x16 T20; laidas
  +1,5 m ~230V už plokštės; perimetras 10 m.
- Back plate 2700 x 2100 RAL 1020, 2 dalys 1400 + 700, logo plėvele (551 022/603/701/321/010), 2 mm, briauna 40 (ALT8187).
- Darbo valandos Type 200 / 300 (P6, rėmas RAL 9003 / 9005 / 8014), U 20x20x2 + L 20x20x20x2, Ø6; parkavimo lentelės - balta
  ACM + Gel'UV („SPAUDAI SPALVAS PADARYTI PAGAL JOKER SPAUDOS ETALONĄ"). Etalonas: `JOKER/Order no 222109/ALT8187_03.10_Order no 222109.cdr`.

### COOP (5; NO)
- 6-24 / Coop Mega: P6 8 mm arba 3 mm + PVC 3, gylis 70, šonai **RAL 5003**, rėmas U 30x30x2 + L 30x30x30x2 (6 vnt., Ø6),
  **RAL 7035 matt**, WHITE 6500K, +1,5 m ~230V (ALT8331, 223217). Coop Mega - RAL 6005, galas balta plexi 4 mm, spaceriai 30.
  Pavyzdžiai: PANTONE 186C ≈ Mactac 9859-166 Cast, vidus RAL 9003, drenažo skylė.

### Boots apotek (5; NO)
- Lauko šviesdėžė (etalonas `Boots apotek/etalonas/sviesdezes_460_ir_570.cdr`): korpusas 2 mm Alu (juosta su įfrezavimais
  lenkimui), 3 mm balta plexi + PVC 3, LED P2 16 vnt., KPS-V12-40W, tvirtinimo plokštė 8 mm Alu, rėmas 30x30x3, RAL 6029 / 6037,
  kryžius Oracal 8500 614. Raidės lauke: 8 mm plexi, RAL 9003 / 6029, U 30x30x2, laido dangtis Alu L, RAL 9006.
- Vidaus pakabinama (Jessheim ALT7945): Profile 10 (30 mm plexi), kojos 30x30x2 / 35x35x2 teleskopinės, min 500 / max 1000,
  plokštelė 8 mm Alu 70 x 70, M6x45, trafo box RAL 9006, „NICE LOOKING BACKSIDE".

### Norli (225670 / 225671; NO) - „400 mm pendant sign" (nedheng)
- BF: Profile 5s, 60 mm, apačia ir rėmelis juoda matinė / Gloss 40 (RAL 9005), balta akrilo priekis (+ spauda Leker), balti LED,
  kabinama ant skaidraus akrilo „barrier rails" ir lubų laikiklių; formatai 1205 x 400 (norli), 1511,97 x 400 (LEKER).
- ALT8769: Profile 6, 60 mm, interior; 20 mm skaidri plexi wallframe + kojos (klijuojama „interlocking joints"), Alu □ 50x30x3
  (RAL 9006), plokštelės 5 mm Alu 100 x 100, M6x40; pakabinimas min 500 / max 800; perimetras 8 / 6,3 m; laidas +1,5 m black
  12V į converter. Etalonas: `NORLI LEKER_Order no 225670/ALT8769_09.16_NORLI LEKER_Order no 225670.cdr`.

### ALTI (prekybos centrai; 6) - nuomininkų iškabos
- ALTI NESTTUN (ALT7692): P6 3 mm + PVC 3, gylis 80, korpusas RAL 5011, rėmas U 30x30x2 + dangtis Alu L, spalva NCS S 2010-Y20R,
  lankai Oracal 8500 054, perimetras 32 m. Flekkefjord / Sandnessjøen: 4 mm plexi + PVC 4, rėmas 60x60x2 RAL 7042.

### OBS BYGG (3)
- Plokštės 2 mm Alu, 25 mm užlenkta, RAL 2011 + Oracal 551 512 (mėlyna) / 551 101 (balta), vidus RAL 7016; raidės - 3 mm plexi,
  RAL 5013, fonas 2 mm Alu. Vidaus (margos raidės) - 20 mm skaidri plexi, vinyl wrapped, priekis 2 mm Alu, galas 4 mm plexi.

### KFC (SE), ICA (SE), Burger King (SE)
- KFC `KFC/Etalonas/`: drive-thru height detector („HEIGHT LIMIT 2.50 M", 3 mm Alu, L 50x50x2, atšvaitinės plėvelės),
  order kiosk su stogeliu, menu board; RAL 3020 / 9005 / 7016, 3M 3630-53, Oracal 551 702. KFC Bernstorp - PVC banner šviesdėžė.
- ICA: šviesdėžės korpusas 2 mm Alu „negative cut", priekis 3 mm balta plexi, RAL 5002 / 7016 / 3020; raidės 8 mm, RAL 9003.
- BK: termoformuota 3 mm plexi, LED 5100K, RAL 9006, 3M 3630-84 / -143.

## Klausimai Ryčiui
1. Ar senasis ALT Corel šablonas (C / B / P / I blokai) dar naudojamas BF užsakymams, ar viskas jau SPAR etalono stiliumi?
2. BF „Profile 5 / 5s" -> mes darome Profile 6 (Norli) - tai taisyklė visiems BF užsakymams?
3. KIWI 2027 etalonas (trafai raidėse, 230V, rėmas RAL 3003) - ar tai naujas KIWI standartas vietoj 12V 3 m išvesčių?
4. MENY wallframe spalva kinta (7024 / 7037 / 8011 / 3009 ...) - visada pagal Bestilling / BF brėžinį, ar yra numatyta?
5. Ar „GoodsLabeling" numerius iš Pirkimo užsakymo .xml reikia rašyti lape / pakuotėje?
