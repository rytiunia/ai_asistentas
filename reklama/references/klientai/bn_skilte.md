# BN Skilte A/S (Danija) - kliento taisyklės

> v161, 2026-10-13: surinkta iš darbų aplanko `DARBAI/uzsienio reklama` (2024-2026) analizės; Rytis patvirtino, kad tai STANDARTAS. „(spėjimas)" - nepatvirtinta, prieš naudojant lape - klausti. Skyrius „Klausimai Ryčiui" - dar neatsakyta.

Raktažodžiai: BN Skilte, bnskilte, Indkøbsordre, Normal, Unik mand / Unik man / lysmand, Netto, Coop / SuperBrugsen / Kvickly,
DAVIDSEN, BigDollar, Subway, Wash World (WW), Prisma Properties, M3 / K3 Properties, MENY, SJF Bank, flexface, RFQ-YY-MM-NN.
NAS aplankas: `/Volumes/dizainas/RYTIS/DARBAI/uzsienio reklama/bn-skilte.dk` (~6800 failų; 2024-2026 ~2900; daugiausia `normal/`,
`SLB/`, `WASH WORLD pilonai/`, `coop/`, `DAVIDSEN/`, `BigDollar/`). Šviečiantys pilonai su B-0313 šviesdėžėmis - žr.
`references/etalonas_pilonas_prisma_alt8826.md` (čia nekartojama) ir `references/moduliai_pilonai.md`.

## 1. Užsakovas, užsakymai, aplankai
- Užsakovas: BN Skilte A/S, Jomfruløkken 6, DK-8930 Randers NØ (pristatymas ten pat); pirkėjas - Kirkebjerg Parkvej 30, Brøndby.
  BN „Purchase order": Number NNNN, Delivery date, **EX Works**, 90 dienų, suma EUR; eilutėse „Our item" (mūsų kodas
  BN sistemoje: NM-0097 Normal, SW-0001 Subway, DA-0007 Davidsen, NT-0100 Netto, SJF-0014 ...) ir „Your item" (BN produkto kodas,
  pvz. `FAC-B-FML-P6-H1600` - Normal akrilinis frontas H1600xB479, `FAC-B-ML-P5-500` - Profil 5 raidės h500 su LED, „samlet med umleimer").
- Aplankų vardai (perimami iš BN laiško temos):
  - iki ~2025: `Order No NNNN <objektas> <aprašas> ref no NNNNNN-XX` (NNNN - BN order, NNNNNN - BN sales order, XX - BN pardavėjo
    inicialai: MA, CG, LK, LN, KBL, MFA, RFS, HG, SN, CSJ, TN, BHN (spėjimas - pardavėjų inicialai));
  - nuo 2025: `PO NNNN <aprašas> <sales order>` (pvz. `PO 2474 Netto,632 Haderslev 423017`) ir `Indkøbsordre NNNN Fra BN Skilte`;
  - užklausos: `RFQ-YY-MM-NN <aprašas>-XX` -> pasiūlymas `Offer Re RFQ-...`; išankstiniai `Pre-Order ...`; atšaukti - priešdėlis
    `PANAIKINTAS_`; `Order No NNNN` + `RFQ-...` gali būti tame pačiame aplanke (`.../pirminiai/` - pirminiai variantai).
  - Aplanko viduje: `info/` (BN PO pdf, BN brėžiniai `AI_10000x2000_...pdf`, objekto vizualizacija `Volden 1_7 Pylon.pdf`,
    statikos skaičiavimas, logotipai), `Drawing_<užsakymas>[_upd_N].pdf` (brėžinys BN derinimui), `led/`, `pirminiai/`.
- Failai: `ALTnnnn_MM.DD_<užsakymo pavadinimas>.cdr/.pdf`; laikini `_upd_N`, `_upd_YYYYMMDD`; gamybai siunčiami pjovimo failai -
  atskiras aplankas (pvz. `heliopoliui pjauti/ALT6162_06.21_DIBOND_pjauti_1prie1.cdr`, lapas = lakšto dydis 7420x4297).

## 2. Lapo konvencijos (BN užsakymuose)
- A3 landscape, apačioje eilutė: užsakymo pavadinimas | `ALTnnnn_MM.DD_<autorius>` (rycka / MJ / ING / RS) | `Sheet X of Y`;
  `ALT0000_00.00_rycka` / `_RS` - preliminarus lapas (RFQ / derinimas). Viršuje kairėje juoda žyma `1 pcs.` / `2 pcs.` / `x14`.
- Dešinėje spalvota specifikacijos lentelė: **P PRODUCTION** - MOUNTING WAY; **C CUTTING** - MAIN MATERIALS (Front / Side / Backside /
  Hem, numeruoti 1-5 kaip 3D pjūvyje); **B BENDING** - DEPTH (+ Exterior/Interior); **P PAINTING** - BODY (SIDE) COLOR, MOUNTING FRAME /
  PROFILE COLOR; **I INSTALLATION** - LED; **FRONT COLORS**; **PERIMETER** (m). Profilio žyma rėmelyje: `Profile 5`, `Profile 5S`, `Profile L3`.
- Flexface lapuose vietoj lentelės - numeruotas sudėties sąrašas „1. Lightbox PVC banner ... 10. Lifting eye bolt" (žr. 4 sk.) ir
  LED blokas „Depth / Module / Power / PWM / Brightness 2000 lux / Warranty 5 years / Modules CC / Rows CC".
- Pilonų / plieno lapai - „Parts List" (Item / Part Number), suvirinimo žymos a3-a6 (a5x50 %), metalo lapai danų kalba
  (EN 1090-3 EXC2, S355 / S235J2) - kaip Prisma etalone.
- Dažni užrašai: `INCLUDING PAPER MOUNTING TEMPLATE`, `Folie overlap 5mm` + `Folie connect points`, `Inside frame without painting.`,
  `+1,5m ~230V El. Output`, `+5m 24V El. Output`, `1.5m 12V el. output from each letters`, `IMPORTANT!`.
- Lietuviški gamybos užrašai paliekami tik ne kliento lapuose / ant darbalaukio („NESUMAIŠYTI PUSIŲ", „KAIP VISADA 1 TESTUI").

## 3. Normal (BN tinklo klientas) - stovinčios „Unik mand" ir fasado logo dėžės
### 3a. „Unik mand" (lysmand) P6 / Profile 5S - standartinis tekstas (Bn1010)
`Bn1010 Single-sided special LED light sign decorated with foil. According to B1 class. The box is build in aluminium bottom (2 mm)
and with welded aluminium return (1 mm). Front in 3 mm white PC B1 with a milled edge for mounting and decorated with foil.
NOTE: The backside needs to have a nice finish (in some places it is visible).` Colours: `Return Black ral 9005 gloss 80%`,
`Front ORACAL 551 701`. Return 100 mm (yra 50 mm gylio variantai - Portugalija, `Unik man 50 mm`).
- Sudėtis (numeriai lape): 1 B1 policarbonate; 2 LED modules; 3 Glue - Sealant; 4 Side - 1mm aluminum; 5 Sole - 2mm aluminum;
  A - PVC fitting edge 3 mm (~15 mm aukščio), B - BOLTS. Fronto frezuotas kraštas: užlaida 4 mm, laiptelis 1 mm (lapo pjūvis).
- **Frontas - 3 mm B1 polikarbonatas, du variantai su varnele lape:** `3mm PALSUN B1 Polycarbonate fire retardant plate (Option 1)` /
  `3mm Exolon UV Polycarbonate fire retardant plate (Option 2)`. 2026 lapuose (ALT7965, ALT8820) pažymėtas Option 2 (Exolon UV).
- Dydžiai: H1600 x 478 (BN: H1600xB479), H619 x 450, H1900, H2100, H1200 (FR), H4500 ir H9000 - flexface (žr. 4 sk.).
- **Dvi versijos: `Look right version` / `Look left version`** (veidrodinės), kiekiai atskirai; ant lapo raudonai
  `When packing, mark the box „R" (right)` / `„L" (left)`.
- LED: BMP-S2 (H1600 - 26 vnt. + Transformator ELG-75; H619 - 10 vnt. + XLG-75), perimetras 5 m / 2 m;
  `CONVERTER mounting on the welded fasteners`; 2025 m. užsakyme: `Led's transformers with dimmer to reduce to 2000 lux`.
- Lipdukų lapas (paskutinis lapas): QUALITY CONTROL lipdukas, `REF....` lipdukai - klijuojami iš vidaus ant šono / ant gaminio
  pakuotės / ant nugarinės pusės; dėžės žyma R / L; `QC APPROVAL`.
- Dažni užsakymai: stock / lagerordre (15+15 vnt.), **tik frontai** (`Akrylfront til lysmand`, `ONLY FRONT WITH GRAPHICS`,
  `Only 3mm B1 Polycarbonate front with decals for P6 LED sign`) - lapas tik su fronto kontūru, PVC krašto pjūviu ir L/R kiekiais.
- Etalonai NAS: `normal/NORMAL etalonas/` (`NORMAL H1600_etalonas_2025_pagal_Zydruna.cdr`, `H1900 etalonas_standartinis /
  nestandartinis debeselis_2025.cdr`, `50mm turio LED deliojimas.cdr`).

### 3b. Normal facade logo lightbox 452x1093 (BN item 5000007) ir 600x1452 (5000008) - patvirtinta gamybai 2024-04-19
- Konstrukcija (BN brėžinio pozicijos): Pos.1 Front 3 mm Alu su išfrezuotomis (flipped) raidėmis; Pos.2 backplate 2 mm Alu;
  Pos.3 opal plate 3 mm B1 PC (Lexan) prie fronto - 34 (452) / 38 (600) welding bolts M4x16 + veržlės / poveržlės;
  Pos.5 return front Alu 1,5x90; Pos.6 return back 2x20; Pos.7 sraigtai 3,9x9,5 flat head tapping type C, hex socket,
  galvutė RAL 9005 gloss 80; Pos.8 aluface 3 mm balta LED plokštė (404x1045 / 552x1404) - dvipusė juosta + klijai, skylės sutampa;
  LED Balt S2 1 W: 17 vnt. (452) / 23 vnt. (600); converter 40 W LPF-40-12. 4 x Ø7 tvirtinimui, drenažas Ø5,5 apatiniame taške.
- Medžiagos: EN AW-6060/6063 T6 (DS/EN 755-3); dažymas juodas RAL 9005 gloss 80; suvirinimas pagal EN 1090-3 EXC2.
- **BN QC pretenzijos (test PO720, 2024-05) - privaloma:** return 2 mm pagal BN brėžinį (1,2 mm per silpnas); return 90 mm;
  sandūra apačioje ir sutaškyta (ne tik sandarinta); LED tik S2, ant visų modulių klijai/silikonas; šviesumas 2000-2200 lux;
  12 V pusėje Wago nereikia (užspaudžiamos jungtys OK); įžeminimo gnybtas min Ø6,5; front return - užrakinta skylė Ø5;
  aluface ir backplate skylių sutapimas (kreipiamieji kaiščiai); dažai turi sukietėti prieš pakuojant.
- **Pakavimas (BN instrukcija „Pakkevejledning", 2024-05-22):** 1 sluoksnis putplasčio (tik popierinė juosta) -> gofrokartonas
  (juosta be firmos logo) -> ant briaunos, max 2 sluoksniai -> paletė apvyniota, min 80 mm šakėms.

### 3c. Kiti Normal
- Didelė fasado dėžė (Order 2273, ALT7521): 2 dalys, 3 mm balta DIBOND + Mactac 9849-18, rėmas 30x30x2, Z 30x30x3 (5180 ilgio)
  sienai, Trafo box RAL 9010, 5 m 12 V (3x1,5 mm²), LED 6000-7000 K. „First fix DIBOND to the frame, then apply film".
- P6 raidės ant kojų (IE0101 H2000, PO 2861 NL): front 4 mm balta plexi, side 1,2 mm, back 2 mm, gylis 180 (Interior),
  PRO190 1,5 W 6500 K (122 vnt. / 183 W), KPS-60-12 x5 + KPS-100-12 **trafo raidžių viduje**, kojos 60x60x2 / 50x50x2 Alu,
  tvirtinimo plokštė 5 mm + 5 mm atramos, body RAL 9005 gloss 80, frame RAL 9010 gloss 80, +1,5 m ~230 V.
- H9000 Unik man flexface (ALT5780): PVC banner 4+4 UV, 3 mm balta dibond su LED, kraštas 2 + 1,2 mm Alu RAL 9005/9010 (priekis baltas,
  šonas juodas), rėmas 30x30x2 + 25x25x2, atrama 5 mm, Z profilis, kėlimo kilpa, gylis 200, front Alu 5 mm / back 3 mm lenkti lankai,
  Trafo box + 10 m laidas. Montavimo klaidų ataskaita (`normal H9000 explain.cdr`): plokštės turi susiremti be tarpo, rėmas - pagal lazerinį nivelyrą.

## 4. Flexface (PVC banner šviesdėžės) - BN standartinė sudėtis
Tekstas lape (kartojasi visuose 2023-2026 užsakymuose):
`1. Lightbox PVC banner (with vinyl folie). 2. Backside, 3mm WHITE dibond (with LED modules). 3. Edge cover, 2mm + 1.5mm aluminium
(arba folded 1.5mm). 4. PVC banner mounting support (Alu tube D16x2). 5. Frame, 30x30x2mm aluminium profile. 6. Frame, 25x25x2mm
aluminium profile. 7. Suport, 5mm aluminium (Coop - 3mm). 8. LED modules. 9. Hanging details, Z profile 30x30x3mm (30x30x30x3).
10. Lifting eye bolt.` + `Inside/Inner frame without painting.`
- Gylis 150 (Netto) arba 200 (DAVIDSEN, BYGMA, THansen, EOM, H9000). Rėmas iš 2 dalių - „fitting together with bolts";
  sandūros „Joints with a glued plate"; banerio jungtis „Folie overlap 5mm".
- LED variantai lapuose: KM-T7-W 7 W, CC ~420-470 mm, 24 V, PWM 200 W + potentiometer, 2000 lux, 5 years (DAVIDSEN);
  PRO320Lens 2 W, CC ~300, 62 vnt. / 124 W (Netto); KM-P4 2 W HE CC 170, 1800 lux (BYGMA); CROWN OPTO S4+ BMP-S4P.1 24 V,
  XLG-200 x2, 6500 K (EOM 34 m pilonas). Išvadas: `+5m 24V El. Output` arba `+5m 12V 3x2.5mm² El. Output`.
- Elektra: instaliacinė dėžutė IP56 24 V lauke su Wago (gelis) + elektros lipdukas; įžeminimo laidas į Alu rėmą; trafo - komplekte
  atskirai arba viduje ant privirintų laikiklių (`Inside the lightbox converters and installation boxes fitting on the welded fasteners`);
  Coop: `Rear cable exit through the back surface. 3×1.5 mm² double-insulated grey cable, 10m`.
- Montavimas sienoje: wallframe = Z 30x30x3 Alu + privirinta 3 mm Alu juosta; „Fitt lightbox Z with frame Z profile, use self drill
  screw on a top profile"; viršutinis profilis - karštai cinkuoti varžtai; dangtelių varžtai DIN 7504 N 4.2x16 T20.
  Pilone: L 60x60x4 plienas / L 50x50x10 Alu + 5 mm reguliavimo plokštė, 105°, ovalios skylės, `Expandable gasket to keep light inside`.
- Spalvos pagal tinklą: Netto - šonai RAL 7021 gloss 30 %, wallframe RAL 7021; Coop / SuperBrugsen / Kvickly - kraštas RAL 3020 80 % gloss,
  frontas Avery 4506-Red (BLOCKOUT), PWM-200-24; Kvickly tent - rėmas 30x80x2, cover RAL 3020 / PMS 355C glans 80; BigDollar - RAL 9005 matt,
  ORACAL 8500 021/031/070; DAVIDSEN - PANTONE 7686C, Avery 5512QM / 4543.
- Lape skaičiuojamas plėvelės kiekis („Folie 6.8m2") ir DIBOND išklotinės („DIBOND 3100x990", lakštai 2 mm 1220x3100, 3 mm 1500x3050 /
  1500x4050 / 2000x4000), dažnai svorio lentelė (Banner ~1 kg/m², ACM ~4,1 kg/m², 30x30x2 0,62 kg/m ... TOTAL).

## 5. Pilonai
- **Šviečiantys pilonai su B-0313 šviesdėžėmis** (Prisma Skejby, M3 Ringsted, K3 Nørresundby) - žr. Prisma etaloną. 10x2 m „fællespylon"
  (M3 / K3, 2025): 2000 x 10275 (10000 + 250 kojos), gylis 530; laukai 2000x2000 / 2000x1000, tarpai 32, šviesdėžė gylis 140,
  priekis 3 mm balta plexi su grafika, galas 3 mm ACM, PRO320 2 W 6500 K 24 V (64 vnt. 2x2 / 32 vnt. 2x1), LED drivers - apačioje;
  RAL 7016; rėmas RHS 250x150x8 S355J2H + 50x50x4, pado plokštė 25 mm S355 600x460 6xØ34, M30 rym-varžtai; apdaila 30x30x2 Alu L
  + 2 mm Alu dangteliai. `info/` - BN statikos skaičiavimas (`V-LU-1243-1_PY_H10m_Static_calculation_.pdf`).
- **Flag pylon su plexi įdėklais** (Wash World, Prisma Holstebro 14 m / 7 m, Hammelev 8 m): korpusas 2 mm Alu, raidės/formos
  `inlay from 6mm white plexiglas, GS WH02` (+ decals), tvirtinimas `30x30x2mm L profile + 20x20x2mm L profile` kas ~100 mm,
  apačia L 30x30x2 + dugno plokštė su 20 mm standumo briauna; folijos ORACAL 8500 translucent + Gel'UV + gloss laminate, ORACAL 551
  gloss, Avery 701, Avery 759-05 PF Komatsu Grey, Avery 4502 TF, 3M 580-10E reflective; Day / Night vaizdai; korpusas ir koja
  RAL 9005 gloss 80 % (Prisma Hammelev - RAL 7016 gloss 60 %, rėmas primed). Pakeitimų lapuose - `OLD / NEW` + `Old file: ALT....`.
- Kiti: Sylvan Viby (Alu rėmas 120x120x5 + 40x40x4, kojos 20 mm Alu, atramos 10 mm, Ø34), WW Landskrona 6x6 m flexface (S-beam
  300x300x14, 120x120x8), City Nord (plieno koja + L 60x60x5), K3 kojų dangteliai 2 mm Alu RAL 7016.

## 6. Raidės ir kiti produktai
- **Subway** (2025-2026): Profile 5 (ELKAMET profile White / Yellow), front 3 mm balta plexi, side 1 mm, back 1,5 mm, gylis 120 Exterior,
  body White RAL 9003 ~60 % gloss / RAL 1023 ~60 % gloss, front 3M Scotchcal 3630-125, LED White 6500 K (P130L 64 vnt.), KPS-100-12V,
  `1.5m 12V el. output from each letters` į bendrą converter; skylės Ø6 tvirtinimui / Ø10 laidui (atskiras BN lapas
  `Subway mounting and wiring holes`); `INCLUDING PAPER MOUNTING TEMPLATE`; LED laidai paliekami viduje, mėlynos jungtys -
  „kaip Normal reklamoms". Tipinis dydis 3153 x 629 (raidės h500).
- Bendra raidžių lentelė BN lapuose: Front White 4 mm plexiglas, Side 1,5 mm, Backside 2 mm, Aluminium hem 2 mm
  („Plexiglas fixing to hem with fastners"), gylis 80-200; PVC fitting edge 3-5 mm + BOLTS; wallframe 40x40x2 / 50x50x2 / 60x60x2.
- MENY flagsign (dvipusis): 2/3/4 mm balta plexi, raudona PLEXIGLAS GS Rot 3H25, koja D50x5 Alu, montavimo plokštė 10 mm Alu,
  vidinis žiedas 1,5 mm, išorinė juosta 2 mm, korpusas 3 mm, 12 V 5 m 3x1,5 juodas kabelis. SJF Bank flagsign: 8 mm balta plexi (lazeris),
  korpusas 2 mm, rėmas 3 mm Alu + 50x50x4 / 40x20x2, vamzdžiai D30x2 / D25x2, RAL 7005 / RAL 9010 gloss 60 %, Metamark MT-642.
- Smulkūs: Netto rondel Ø3000 / Ø2550 (KPS-V12-300, montavimo lapas su žingsniais), neonflex ant 8 mm skaidraus plexi, RGBW (LEMLUX,
  KAISEN KPS-V12-300), poveržlės 2 mm VIVAK Ø30 x2000 („TABS"), medinės raidės.

## 7. Medžiagos, spalvos, LED - BN standartai (santrauka)
- **Plexiglas XT WN770 opal - BN standartas** (Rytis 2026-10-13); BN lapuose rašoma „White ... plexiglas" / „opal white acrylic".
- **B1 polikarbonatas (PALSUN B1 / Exolon UV) - tik BN** (Normal frontai ir opal plokštės, „According to B1 class").
- Spalvos: RAL su blizgesiu lape („gloss 80 %", „gloss 60 %", „gloss 30 %", „matt finish"), PMS, NCS (McDonald's NCS S 0580-Y10R).
- LED / PSU, kaip rodo failai: 12 V raidės - KAISEN KPS (V12-40, 60-12, 100-12, 300), BaltLED moduliai (BMP-S2, PRO190, P130L, PRO320);
  flexface 24 V - PWM-200-24 / PWM-120-24 (Mean Well) su potenciometru; Unik mand - ELG-75 / XLG-75; Normal logo dėžė - LPF-40-12
  (BN specifikacija). Spalvinė temperatūra 6500 K (lapuose „6000-7000K" senesniuose). Hybel: rezervas `+20%` prie galios.

## 8. Etalonai (NAS, santykiniai keliai nuo `bn-skilte.dk/`)
1. `normal/PO_3239_Normal_424987/ALT8820_09.28_PO 3239 Normal 424987.pdf` - Unik mand frontas, L/R, B1 PC.
2. `normal/NORMAL etalonas/NORMAL_sviesdezes_2024/PATVIRTINTI_GAMYBAI_20240419/GAMYBINIAI/Normal facade sign 600 x 1452 _ 190424_upd_070524.pdf`
   (+ `.../pokavimas/Pakkevejledning - Normal facadeskilte.pdf`, `.../papildoma info 20240529/QC report Test order PO720.pdf`).
3. `PO 2474 Netto,632 Haderslev 423017/ALT7955_01.13_PO 2474 Netto,632 Haderslev 423017.cdr` - flexface 150 mm + wallframe.
4. `Order No 2323 M3 Property Ringsted 10x2m pylon ref no 421465-LN/ALT7548_09.10_..._upd_20250915.pdf` - 10x2 m pilonas.
5. `SUBWAY/PO 2583 Subway Herning/ALT8090_02.12_PO 2583 Subway Herning.pdf` - Profile 5 raidės.

## Neišspręsta - klausti Ryčio, kai klausimas iškyla darant projektą (ne iš anksto)
1. LED/PSU: BN flexface ir Unik mand lapuose nuolat Mean Well (PWM-200-24, XLG/ELG-75, LPF-40-12). Ar BN tai išimtis (kliento specifikacija),
   ar ir čia default Kaisen KPS / BaltLED BPS, o Mean Well - tik kai BN nurodo?
2. B1 PC: 2026 lapuose pažymėtas Option 2 (Exolon UV). Ar dabar default Exolon UV, o PALSUN B1 - alternatyva?
3. WN770 BN failuose nerastas pavadinimu: kur tiksliai jį rašyti BN lapuose - raidžių / šviesdėžių priekis („White 3/4 mm plexiglas"),
   o B1 PC lieka tik Normal ir B1 klasės gaminiams?
4. Normal logo dėžės return: BN brėžinyje front return 1,5 mm, QC reikalauja 2 mm - koks galutinis standartas (1,5 ar 2 mm)?
5. Flexface atrama „Suport 5mm" vs „3mm" (Coop/SuperBrugsen) - ar 3 mm tik Coop standartas?
