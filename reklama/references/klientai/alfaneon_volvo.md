# Alfa Neon AB / VOLVO - kliento taisyklės ir standartinių gaminių katalogas

> v161, 2026-10-13: surinkta iš darbų aplanko `DARBAI/uzsienio reklama` (2024-2026) analizės; Rytis patvirtino, kad tai STANDARTAS. „(spėjimas)" - nepatvirtinta, prieš naudojant lape - klausti. Skyrius „Klausimai Ryčiui" - dar neatsakyta.

Raktažodžiai: Volvo, Alfa Neon, AlfaNeon, VOLV24-, VOLV25-, BS module, Blue shield, Top sign / Toppskylt, Tomahawk,
Mounting kit 5,5 / 7,5 / 9,3, Entrance sign, Directional, Charging totem, Bilia, Bilmånsson, Brandt, Helmia, Bilbolaget, Rejmes.
Užsakovas: **Alfa Neon AB** (Årstidsvägen 8, 66535 Kil, SE), pirkėjo atstovas P. Månsén; tiekėjas UAB ALT reklama.
Galutiniai klientai - Volvo dileriai Švedijoje (pristatymas „Direktleverans“ dileriui arba į Alfa Neon Kil).
NAS: `/Volumes/dizainas/RYTIS/DARBAI/uzsienio reklama/AlfaNeon/VOLVO` (iš debesies nepasiekiamas - prašyti failų).
**Standartas = `VOLVO/VOLVO_darbiniai failai/`** (Rytis). Visi gaminiai turi Alfa Neon prekės kodą; užsakymas = kodų sąrašas.

## 1. Kodų sistema
- `VOLV24-GGNNN[-V][H|V]`: `24`/`25` - kodo sukūrimo metai (ne užsakymo), `GG` - šeima, `NNN` - gaminys, `-V` - variantas
  (vietovė/tekstas/revizija), `H` = Höger (dešinė), `V` = Vänster (kairė) - pilono viršaus pusės.
- Šeimos (iš 97 Purchase order 32045-33212 ir lapų):
  `01` P6 raidės VOLVO (nerūd. plieno šonai) · `02` BS = Blue Shield fasado moduliai (`021` 1200 pločio, `022` 2400,
  `023` 3600, `024` 4800; `02001-xx` montavimo bėgis) · `03` pilonų viršai, Entrance/Directional/Charging/Pole ·
  `05` sieninės (cassette, entrance wall) · `06` pilono viršai ACM pilonui (06005/06006 V/H) ir „BLOKAS“ (06003) ·
  `07` stulpai/profiliai.
- Dilerių individualūs gaminiai: `BILB` Bilbolaget, `BILD` Bildeve, `BILI` Bilia, `BILK` Bilkompaniet, `BILM` (spėjimas: Bilmånsson),
  `BRAN`/`BRADN` Brandt, `HELM` Helmia, `SKOB` Skobes, `FINV`, `STEN` + `YY-GGNNN` ta pačia logika (01 = raidės, 05 = sieninės, 07 = profiliai).
- Kitos PO eilutės: `AM-703` „Deduction milling machine 30% ALT“ (nuolaida), `AM-203` transportas - į lapus neina.

## 2. Bendri Volvo standartai (pagal lapus)
- **Spalvos:** Volvo mėlyna **RAL 50050** (Volvo spec, tikra) - frontai, BS plokštės, montavimo bėgiai; pilka **RAL 7024**
  (šonai/galai, rėmai, kojos, mounting kit plienas); balta **RAL 9016** (šviesdėžių galai, charging totemai, balti BS 02302-1/-2);
  pilki „grey“ moduliai RAL 7024 gloss 85 (02221/02311/02409). Lape rašoma `Ral 50050, 50% gloss` + `p.c.` (powder coating) arba `w.p.` (wet paint).
- **Blizgumas (kaip lapuose):** RAL 50050 - BS plokštės 70% (02101/02201/02301, w.p.), 4800 moduliai, viršų frontai, bėgiai,
  dangteliai, entrance/directional - 50%; RAL 7024 - pilono viršų šonai/galai 50% p.c., pilonų/kasečių rėmai 70% p.c.;
  RAL 9016 - šviesdėžių galas 30% p.c., charging 70% p.c., entrance 3A 50% w.p.
- **LED 4000K** visur (P01 0,5W žingsnis 85-100; P02/P2 1W žingsnis 100-160; KAISEN P3 1,5W žingsnis 140 pilono viršuose;
  Bp01 1,4W žingsnis 70 charging). Charging gaminiams PO rašo 4100K.
- **Maitinimas - Mean Well (Volvo lapų standartas):** XLG-A 75W / 100W / 150W, HLG-A 40W (HLG-40-A), HLG 150W, LPV 35W (P6 raidėms),
  XLG-40/100 (dilerių raidės). Bendrinė taisyklė (Kaisen/BaltLED default) Volvo standartiniams gaminiams netaikoma - spec. lapuose jau Mean Well.
- **Elektra:** `Plastic IP box (wago inside)` (dažyta kaip rėmas, w.p.) arba trafo „Inside“; kabelis `230V, black, 3m (leave inside)`;
  2 trafų moduliuose 6 m (3 m kiekvienam). Raidėms ant bėgelio - `1.5mm Alu box (wago inside)` + `+1,5 m 12V El. Output`.
- **CE lipdukas** ant LED dėžės nugaros (pastaba lape „CE lipdukas ant LED dėžės nugaros“); lipduke data, užsakymas, kodas ir 2 skaičiai
  (pvz. `0,25 | 46,2`, spėjimas: A ir kg). Alfa Neon lipdukas 45x20 (`AlfaNeon/NEW CE sticker and Alfa Neon sticker/`).
- **Opalinis akrilas:** įdėklai `Plexiglas XT WN770 t=10mm` (pilonai, entrance, directional, charging), P6 frontai `XT Wn770 t=8mm`;
  BS moduliuose įdėklas `Plazcast 1845N t=20mm` (laiptuotas frezuotas kraštas „Milled edge“, seniau `Plexiglas XT 0A000 t=5mm` laikiklis);
  šviesdėžių (Service) frontas `Plexiglas XT Wn071 t=4mm` + `Oracal 8500-070 Black` tekstas.
- **Plėvelės:** ORACAL 551 702 / 701 matt (juodi subtitrai), ORACAL 551 101 / 551-010 white, Oralite 5500-010 (balta atšvaitinė, directional),
  Oralite 5500-070, „White reflective foil“.
- **Montavimas:** BS - `Al. L 50x50x2` bėgis (RAL 50050, 50%) + `Distancer Al 10 mm`; 4800 moduliai `L 50x50x3` + 2x `M12` kėlimo ąsos;
  pilono viršai - `Al. L 50x50x10` (RAL 7024) ant mounting kit, 2x `M16` ąsos; directional large - `M16 Lifting Eye Bolt`.

## 3. Katalogas (kodas -> gaminys)
### 01 - P6 raidės „VOLVO“ (stanless steel letters)
| Kodas | Gaminys | Konstrukcija |
|---|---|---|
| VOLV24-01001 | Volvo P6 3023x235 | Front XT Wn770 8 mm, šonai+dugnas nerūd. A2 316 brushed 0,8 mm, rėmas U 40x60x40x3 / 30x50x30x3 / 20x40x25x3 + L 40x40x4 (2x L40x40x250), P01 4000K 39 vnt. žingsnis 100, LPV 35W inside frame, IP box. Rėmo bėgis 2780. „Mounting parts delivered not assembled“: 4x M6 bolt, 4x M6 nut, 8x M6 washer, 20 self tapping screws RAL rėmo. |
| VOLV24-01002 | Volvo P6 2015x157 | tas pats, rėmas L=2400 + 2 L 40x100 L=80 RAL 50050 |
| VOLV24-01002-2 | P6 2015x157, LED driver outside | U 20x20x2 bėgiai RAL 9002, trafo box Alu 1,5 (`_2 rails` variantas) |
| VOLV24-01003 | Volvo P6 4032x313 | kaip 01001, rėmas RAL 50050 |
| VOLV24-01004, VOLV25-01010/-01011, VOLV24-01012-1 | „Charging“ raidės 225/300 (1372x225, 2271x300) | XT fronts, nerūd. šonai, 4100K, rėmas RAL 7035 / 9006, + VOLV25-07001 stulpai |
| VOLV24-07001 | Charging poles | □ 80x80x2500, RAL 9016 |
Dilerių raidės (BILx/HELM/BRAN/SKOB/STEN/FINV) - P6 (P5 S) baltais frontais, nerūd. šonai arba Alu juosta 1 mm + Alu 1,5 dugnas, rėmas pagal dilerį (RAL 9003/9006/7024/9002...).

### 02 - BS (Blue Shield) fasado moduliai
Konstrukcija (02201 / 02301 lapai): `Plate Al 2 mm` lankstytas padėklas (gylis 73, bendras 139 su bėgiu), VOLVO raidės išfrezuotos,
įdėklas Plazcast 1845N 20 mm, LED dėžė iš ACM 3 mm prie priklijuoto L 20x20x2, privirinti varžtai („Welded fasteners“),
`Mounting Al. L 50x50x2` RAL 50050, „BE SPACER!“ / „Galinės detalės atskiros ir privirintos“. Logotipas 2015x156 ant 2400 modulio, 3369 pl. ant 3600.
| Kodas | Gaminys | Pastaba |
|---|---|---|
| 02101 / 02102 / 02103 | BS 1200x600 logo / 1200x600 / 1200x300 | logo: P02 20 vnt., HLG-A 40W (arba XLG 75W) |
| 02104-3 / -4 | BS 1200x600 Service / Skadeverkstad | šviesdėžė: XT Wn071 4 mm, galas Al 2 RAL 9016 30% p.c., P2 21 vnt. žingsnis 160, HLG-A 40W, Oracal 8500-070 |
| 02105 | BS 1200 Covering plate Blue | |
| 02201 | **BS 2400x1200 module - logo** (dažniausias, 47 PO) | Flat, illuminated, P2 30 vnt. ~100, XLG-A 75W (vėliau 40W), 4,5 m² Al 2 |
| 02202 / 02203 / 02204 / 02205 / 02209 / 02211 / 02222 / 02223 / 02224 / 02225 / 02228 / 02231 | BS 2400 x 1200 / 600 / 450 / 200 / 900 / 300 / 1050 / 1100 / 400 / 500 / 350 / ... | nešviečiantys: Plate Al 2 + Distancer Al 10 + L 50x50x2 |
| 02206-5 / -6 / -7 / -8 / -9 / -10 / -12 | BS 2400x1200 (-10: 2400x800) šviesdėžė su tekstu: Service / Skadeverkstad / Däckverkstad / Certifierade begagnade bilar / Bilvård | XT Wn071 4 mm, P2 105 vnt. ž. 160, XLG-100W, RAL 9016 30% |
| 02207 (-1, -1A) | BS 2400 Covering plate Blue (balta - RAL 9016) | Al 2, „Upper plate bended 80x49, lower 80x22“, 50% gloss |
| 02212 / 02213 / 02214(-1..-3) | **Horizontalus skydas**: 1200x1200 blue / 2400x1200 logo / 2400x1200 Service šviesdėžė | 02213 + 02212 + 02214-3 = 6000x1200 (order 33343); 135 P02, XLG-A 75W + 150W |
| 02215 / 02216 / 02217 | Horizontalus 1200x600 logo / blue / Service | |
| 02221 / 02311 / 02409 | 2400x200 / 3600x200 / 4800x250 grey | RAL 7024 gloss 85 |
| 02229 | BS 400x1200 (horizontally) | |
| 02301 | **BS 3600x900 module - logo** (37 PO) | P02 64 vnt. ~100, HLG 150W / XLG 100W, rėmas U 20x20x2 + L 40x40x3, L 50x50x2 12 m |
| 02302 (-1 balta, -2 balta „Service“ nešviečianti) / 02303 / 02304 / 02305 / 02309 / 02310 / 02312 | BS 3600 x 900 / 600 / 450 / 300 / 150 / 200 | |
| 02307 / 02308 | BS 3600 Covering plate Blue / White | |
| 02401 / 02402 / 02404 / 02405 | BS 4800 x 1200 logo / 1200 / 600 / 300 | rėmas L 40x40x3, stiffener A/B, 2x M12 ąsos, P02 69 vnt. ž. 150, XLG-75 |
| 02406 | BS 4800 Covering plate Blue | |
| 02001-xx | BS Mounting Rail 50x50, Blue RAL 50050 | ilgiai: -1=3600, -2=3300, -4=5400, -5=3000, -6=2400, -7=4200, -8=2100, -10=3900, -11=5100, -13=4800, -14=1200, -15=1800, -17=900, -18=5600, -19=1700, -20=4500, -21=600, -23=1500, -25=2200, -26=1650, -27=4350, -29=4050, -30=3600, -31=4950, -33=7800, -34=4000, -35=2300, -36=5550, -37=5250, -39=4100, -40=3800, -42=3250, -45=2750 |
Pagalbiniai matmenys: `Pagalbiniai_failai/matmenys sviecianciu fasiu/` (šviesdėžė 1200x600: 1196/1074/1038, gylis 69-70; 2400x1200: 2396/2272/2236).

### 03 / 06 - Pilonų viršai (Top sign / Toppskylt, „Tomahawk“) - visada pora V + H
Konstrukcija (03004/03005/03006 V_H): Front Al 3 mm RAL 50050 50%, side/back Al 2 RAL 7024 50% p.c., rėmas □150x50x3 + □40x40x2,
Mounting `L 50x50x10` RAL 7024, stiffener Al 3, raidės **termoformuotas White PET 3 mm** priklijuotas (įdubimas 28/20),
LED panel ACM 3, KAISEN P3 1,5W ž. 140, XLG-A trafas inside, IP box RAL 7024 w.p., 2x M16 ąsa. Frontas 2 dalių: sandūroje
privirinti Ø10 strypai su kūginiais galais + pailgintos skylės (top/bottom judėjimui), visi kraštai lankstyti.
| Kodas | Pilonas | Matmenys | LED / trafas |
|---|---|---|---|
| VOLV24-03004V/H | Top sign 5,5 m | 3580 x 1109, gylis 173 (bėgiai 3000, raidės h 231) | 44 P3, XLG-A 100W |
| VOLV24-03005V/H | Top sign 7,5 m | 4786 x 1482, gylis 238, frontas 2940 + 1846 | 48 P3, XLG-A 100W |
| VOLV24-03006V/H | Top sign 9,3 m | 5900 x 1840 (order 33465: 1844), gylis 238, frontas 3400 + 2500, bėgiai 5000 | 62 P3, XLG-A 150W |
| VOLV24-06005V/H, 06006V/H | 7,5 / 9,3 viršai ACM pilonui („Fits ACM pylon“, `VOLV24-03006 V_H - ACM`) | kaip 03005/03006 | |
| VOLV24-03018 | Top sign 3400 x 1100 (raidės PET 15 mm) | gylis 161 | 44 P3, XLG-A 100W |
Matmenys sutampa su Volvo 2025 „Far distance single brand“ S/M/L (W3580/W4787/W5900) ir „Volvo Tomahawk 5.5/7.5/9.3 m“
(`volvo2025/.../Ritningar/` - Volvo brėžinių biblioteka, tik informacijai). Termoformavimo STL (L, O, V 7,5 ir 9,3) ir formos -
`Pagalbiniai_failai/TERMOFORMAVIMAS/`, `VOLV24-03004 V_H/forma termoformavimui/` („-6mm“, frezuojama radiusine freza kaip 3D forma).
Nauja viršų versija `VOLVO_Top_Sign_New_Solution_20250218`: dviejų dalių šviesdėžė ant rėmo, minkšta guminė tarpinė perimetru, frontas Al 3.

### Mounting kits (plienas, cinkuota + RAL 7024; Alfa Neon SolidWorks brėžiniai + DXF/STEP lazeriui)
| Kodas | Kam | Sudėtis |
|---|---|---|
| VOLV24-03004-2 | 5,5 m | Plate_1_5,5 x4, Plate_2_5,5 x4 (+Wedge 1/2 DXF); M12x50 50, M12 nut 50, washer 100 |
| VOLV24-03005-2 (rev A) | 7,5 m | 4 lankstytos plieno plokštės, L profile steel_1 x4, 50x50x720; M12x50 64 + nut 64 + washer 128, M16x40 16 + nut 16 + washer 32; ~145 kg |
| VOLV24-03005-3 („typ Nybro“), -4 (Ulricehamn, dwg 24-029), -5 (Täby, UPD_2), -28 | 7,5 m pilono variantai pagal vietą | DXF `7,5-N.dxf`, Gusset, L1, Wedge_1/2 |
| VOLV24-03005-54 | 7,5 m cover plates | Al 2 mm RAL 7024 (Top/Bottom/Side cover 4786) |
| VOLV24-03006-2 (REV-B) | 9,3 m | 4 plokštės, 60x60x6 L=900 ir 1250, L profile steel_1/_2 x2; M12x40 76, M16x50 56 (+ veržlės, poveržlės); ~257 kg |
| VOLV24-03006-5 (Vallentuna, dwg 2024-024), -10 (cover plates Al 2 RAL 7024), -22 | 9,3 m variantai | |
Atsargų apskaita: `VOLVO/VOLVO_mounting_kits_apskaita.xlsx` (7.5-2 / 7.5-3 / 7.5-4 / 9.3-2: sandėlyje, užsakyta, viso).
Visas pilonas 9,3 (Alfa Neon 12-0081-S, plienas, 9320 aukštis) + transportavimo stovas 12-0109 - `GAMYBINIAI_nuo 20250210/VOLVO pylon 9,3/`.

### 03 - Laisvai stovintys
| Kodas | Gaminys | Konstrukcija |
|---|---|---|
| 03001-N | Entrance Sign Service 600x1800 (Side A/B, SS arba DS), N = vietovė (Boden, Bollnäs, Vinsta, Strängnäs...) | Front/Back Al 2 RAL 50050 50% p.c. + 3A RAL 9016 50% w.p., įdėklas XT WN770 10 mm (VOLVO šviečia), juodi subtitrai ORACAL 551 701/702 matt, rėmas □60x60x3 + □30x30x2 RAL 7024 70% p.c., kasetė ant L 15x15x2, mounting pads Al 10, XLG 75W, IP box; laukeliai 600/300/300/75 |
| 03002, 03003-1 | Directional Road Sign 1100x800 DS | □100x100x3, Oralite 5500-010/070, mont. stotelės 500 pamatui |
| 03008-1 | Polesign VOLVO Service 6 m | plieno □150x150x8 6 m + plokštė 25 mm, viršus RAL 50050, apačia XT WN071 4 mm, P01 140 vnt. ž. 85, XLG-100W, dwg 24-021 |
| 03010-N | Charging DS Totem 1800x800 | Al 2 RAL 9016 70%, □100x100x4, Bp01 1,4W 4000K, HLG-A 40W, „Charging“ 8 mm clear |
| 03011-N, 03015-N (SS), 03016-N (DS, `_doublesided`) | Directional small 1066x1500 (tekstinė dalis 960/1070 x 1310, kojos 190) | Front/Back Al 2 RAL 50050 50%, □100x100x3 RAL 7024, rodyklės/tekstas XT WN770 3 mm balti, P02 ž. 150, HLG-40-A, Oralite 5500-010 juostos |
| 03012-N | Directional Large 1688x3000 DS | □100x100x4, L 20x20x2, logo 1+10, M16 ąsa, XLG 75W |
| 03013 | Front to existing Directional small | |

### 05 - Sieninės
| Kodas | Gaminys | Konstrukcija |
|---|---|---|
| 05001 | VOLVO 5900x1850 Cassette, gylis 50, nešviečianti | Front Al 3 RAL 50050, galas Al 2 RAL 7024, rėmas 40x40x3, ORACAL 551 101 raidės |
| 05100-N | Entrance Sign wall 600x1200 / 600x1500 / 600x1800 | Top plate Al 2 RAL 50050 50%, bottom RAL 9016 30%, Plazcast 1845N 10 mm, P02, HLG-A 40W, ORACAL 551 702 matt, L 50x50x2 (VOLV24-02001-21) arba 5 mm spaceriai |

## 4. Kaip surenkamas užsakymas
- Alfa Neon siunčia **Purchase order NNNNN** (PDF) + nuo 2025-02 `NNNNN.xml` (Monitor ERP ORDERS420) į `info/`. Eilutė = kodas, kiekis,
  trumpas aprašas (pvz. „Flat. illuminated / Blue RAL 50050“), Goods label (pvz. 53289 „Volvo Bilia Trelleborg“), pristatymo adresas.
- Lape **niekas neperbraižoma iš naujo** - order lapas yra A3 apžvalga: moduliai sudėlioti kaip ant fasado su kodais ir matmenimis,
  `1 pcs.` žyma, pastabos (pvz. „Blue shield 3600x3630mm + VOLV24-02001-1 BS Mounting Rail 50x50 L3600mm (2 pcs.)“).
  Gamyba - pagal standartinius kodo lapus `GAMYBINIAI_nuo 20250210/...`.
- **Vertikalus Blue shield** = BS moduliai vienas ant kito + covering plate viršuje ir apačioje + 2 bėgiai 02001 (order 33465: 02307 + 02302 + 02301 + 02302 + 02302 + 02307 = 3600x3630).
- **Horizontalus skydas** = 02213 (logo) + 02212 (blue) + 02214-x (balta šviesdėžė) + 02207-1/-1A dangteliai (balti RAL 9016 virš baltos dalies) = 6000x1200 (order 33343).
- **Pilono viršus** = `03006V` + `03006H` (ar 03005/03004) + atitinkamas mounting kit `0300x-N` (+ cover plates -54/-10), dažnai su P6 VOLVO 01001.
- Nestandartinė pozicija tame pačiame užsakyme (pvz. Bilbolaget raidės) - atskiras lapas/blokas order lape arba atskiras kodo aplankas.
- Modifikacija pažymima tekste („VOLV24-03006-5 MODIFIED“) arba nauju variantu `-N`.

## 5. Failų ir aplankų konvencijos
- Užsakymo aplankas: `VOLVO/Volvo_order_NNNNN/` (variantai: `VOLVO order NNNNN`, `Volvo_0rder_`, `Order NNNNN <dileris>`). Viduje:
  `<order>.cdr` (darbinis), `Drawing_<order>.pdf` (siuntimui prieš patvirtinimą), `ALTnnnn_MM.DD_<order>.cdr/.pdf` (patvirtintas),
  `Backup_of_*`, `info/` (PO pdf, xml, dilerio brėžiniai/DXF). Kelių lapų užsakyme papildomai `..._PYLON.pdf`, `Mounting_pad_...pdf`.
- Standartinių gaminių lapai: `VOLVO_darbiniai failai/GAMYBINIAI_nuo 20250210/` - `sukelti frezavimui/<KODAS>/` (CNC frezavimui įkelti),
  `stanless steel letters/<KODAS>/`, `uzdengimai/<KODAS>/` (covering plates), `VOLVO pylon 9,3/`, `VOLV24-06003_BLOKAS/`.
  Kodo aplanke: `<KODAS>[_nuo_20250210_gamybai].cdr` + `.pdf` + poaplankis su `*_1.jpg..._N.jpg` (kiekvieno lapo vaizdas),
  `seni/`, `iki YYYYMMDD/`, `pirminiai/`, `info/`, `paskaiciavimui/` (sąmatai); revizijos `_upd_YYYYMMDD`.
  Seni 2024 m. lapai - `VOLVO 2024/<KODAS>/` (`EO_ALFA_NEON_<YYMM>_<PO>_Volvo_(_<nr>_<poz>).pdf`, .CDL/.eps - nebenaudoti).
- Mounting kits: `VOLVO_darbiniai failai/Mounting kits/<KODAS>_.../` (PDF + DXF + STEP), užsakymai tiekėjui `Mounting kits/Uzsakymai/Pilono_detaliu_uzsakymas_YYYYMMDD/<N>_PCS_<KODAS>/`.
- Maketavimo šablonai: `VOLVO_darbiniai failai/maketavimui/` (2400/3600/4800 „skardos“, 5,5 / 7,5 / 9,3 pilonas, blankas, su SERVICE).
- Lapų antraštė: kairėje viršuje `1 pcs.` / `* pcs.` (juodas laukelis) + **kodas** raudonai (`VOLV24-02201`), `M 1:20`; title block
  `ALT0000_00.00_rycka | Sheet X of Y` standartiniuose kodų lapuose (katalogas, ne užsakymas), užsakyme `ALTnnnn_MM.DD_rycka`;
  kitų braižytojų inicialai `_MJ`, `_EV`. Lentelė `Pos. | Name | Material | Quantity | Notes`, vaizdai Front/Top/Side/Back view, (A-A)/(B-B) pjūviai.
  Lietuviškos gamybos pastabos lape leidžiamos (raudonai/žaliai: „BE SPACER!“, „Prisiklijuoja“, „CE lipdukas...“).

## Etalonai
- `VOLVO/VOLVO_darbiniai failai/GAMYBINIAI_nuo 20250210/sukelti frezavimui/VOLV24-02201/VOLV24-02201_nuo_20250210_gamybai.pdf` (BS logo modulis)
- `.../sukelti frezavimui/VOLV24-03006 V_H/VOLV24-03006 V_H_upd-20250307.pdf` (9,3 m viršus V/H, 12 lapų)
- `VOLVO/VOLVO_darbiniai failai/Mounting kits/VOLV24-03006-2_Mounting kit 9,3/VOLV24-03006-2_Mounting kit 9,3.PDF`
- `VOLVO/VOLVO order 33465/ALT8779_09.17_VOLVO order 33465.pdf` (užsakymo lapas iš kodų) + `Volvo_order_33212/info/33212.xml` (PO formatas)
- `.../stanless steel letters/VOLV24-01001/VOLV24-01001.pdf` (P6 VOLVO 3023x235)

## Klausimai Ryčiui
1. VOLV24-01001 / 01004 rėmas lape RAL 5013, o PO - „Frame + 2 L profiles ... RAL 50050“. Kuris teisingas dabar?
2. RAL 50050 blizgumas: BS 2400/3600 plokštės lapuose 70% (w.p.), visa kita 50%. Ar 70% vis dar galioja, ar viską vienodai 50%?
3. Trafai: Volvo lapuose tik Mean Well (XLG-A 75/100/150, HLG-A 40, LPV 35). Ar Volvo standartiniams kodams paliekam Mean Well, nors bendrinis default - Kaisen/BaltLED?
4. Service šviesdėžių frontas lapuose `Plexiglas XT Wn071 4 mm`, o Volvo opalo standartas - WN770. Ar 02104/02206/02214 keisti į WN770?
5. Kuo skiriasi 06005/06006 V/H nuo 03005/03006 V/H (tik „fits ACM pylon“ tvirtinimas?) ir kas yra VOLV24-06003 „BLOKAS“?
