# LED išdėstymas raidėse - APŠVIESTUMO SIMULIACIJA (v32, Rytis 2026-10-09)

Perrašyta nuo 0 (v23-v27 geometrinės taisyklės ištrintos - netinkamos gamybai). Skriptas `scripts/led_sim.py`,
modulių duomenys - `references/led_lens.md` / `assets/led_lens.json` (tik tiekėjo faktai).

```
python3 scripts/led_sim.py spec.json /mnt/user-data/outputs/<failas>.pdf
```
Spec pavyzdžiai: `assets/spec_led_pn894.json`, `assets/spec_led_coop_225921.json`, `assets/spec_led_spar_225971.json`.
Laukai: `pdf`, `fill_rgb` (spalva arba spalvų sąrašas; `null` - tik KONTŪRAI, pvz. 1:1 eksportas be užpildo),
`min_area_mm2` (numatyta 2000; su diakritikais ė / ū / ų - ~300), `crop_pt`, `scale_mm_per_pt` (1:20 = 7.0556) arba `ref_width_mm`,
`depth`, `module` (null - lyginami visi tinkami), `groups` (raidžių indeksai pagal laidų išvestis lape), `group_names`,
`letter_names`, `main_data`, `psu`, `client`, `title`, `drawing_no`, `order_no`, `date`, `rev`.

## Kodėl kitaip
Profesionalios programos (LED Wizard, SloanLED, GE) remiasi gamintojo tankio lentelėmis raidėms. Lens modulių tiekėjas
tokių lentelių nepateikia - tik 4x4 tinklelį (šviesdėžei) ir kelias taisykles raidėms. Todėl tolygumas skaičiuojamas.

## 1. Šviesos modelis (vienas visiems moduliams)
- LED kristalas - taškinis šaltinis gylyje d po priekiu, I(θ) = I0 cos^a θ, a = 0,5 (platus lęšis), srautas - tiekėjo lm.
- Tiesioginė šviesa į priekio vidinę plokštumą - tik ten, kur šaltinis „mato" tašką (šonai užstoja; 2D atkarpa raidėje).
- Šonai - 10 mm ruožai: apšviestumas nuo modulio -> Lamberto atspindys (ρ = 0,8) į priekį (šviesūs pakraščiai prie modulio).
- Tolesni atspindžiai - tolygus fonas 0,15 x šonams tekęs srautas / priekio plotas.
- Patikra prieš tiekėjo lentelę: modelio 4x4 vidurkis / lentelės lx = 0,48-0,63 visuose stulpeliuose (≈ plexi
  pralaidumas) - modelis atkartoja lentelės tendencijas pagal gylį ir žingsnį.
- Parametrai `LENS_A`, `RHO`, `AMB` - PATIKSLINTI bandymu su pavyzdine raide (vienintelė nežinoma dalis).

## 2. Tolygumo kriterijai - iš TIEKĖJO raidžių taisyklių
Tiekėjo rekomenduota tiesi eilė (P130L 50 mm / 120; P190L 80 / 200; P65L 40 / 100 ir 30 / 70) sumodeliuojama kanale ->
jos bangavimas ašyje = priimtina riba tam moduliui:
- **U = P5 / vidurkis** (tamsūs tarpai) >= P130L 0,74 | P190L 0,70 | P65L 0,63;
- **H = P95 / vidurkis** (šviesios dėmės) <= P130L 1,24 | P190L 1,33 | P65L 1,45.
Vertinama ANT išvalytos raidės ašies (ten, kur matosi „zebras"); 5 % kraštinių reikšmių - patys galiukai.
- **A = P5 / vidurkis VISAME priekyje** (be 6 mm juostos prie šono) >= ribinės VIENOS eilės: tiekėjo žingsnis tame
  gylyje, linijos plotis 1,25 x žingsnis (LED Wizard / SloanLED vienos eilės riba) - P190L 100 mm -> 0,40; P130L 100 -> 0,49;
  P130L 70 -> 0,41; P65L 60 -> 0,54. Modelio paklaidos abiem pusėm vienodos.
  (v31: KIWI plačių linijų galai buvo tamsūs - ašis tolygi, priekis ne; taisyta galų pratęsimu, A tai tikrina ir lape 2
  rodomas. Tiekėjo šviesdėžės 4x4 riba (0,50-0,59) per griežta raidėms: COOP būtų reikėję 2 eilių, 246 vnt.)

## 3. Išdėstymas (forma - geometrija, žingsnis - fizika)
- Ašis = skeletas; pašalinami kampų „ūsai" (atšaka išeina už sankirtos įbrėžto apskritimo < 0,6 r) ir galų „uodegos".
- Ašis -> šakos tarp galų / sankirtų; uždaros -> žiedai.
- **Linijos galas (v32, gamybos pavyzdžiai):** STATUS galas (plotis iki krašto nesiaurėja) - ašis pratęsiama iki krašto,
  modulis per PUSĘ žingsnio nuo krašto (apskritimas = žingsnis liečia galą); kai žingsnis didesnis už linijos plotį -
  (p/2 + w/2) / 2 (šonai ne veidrodis). SMAILĖ (plotis siaurėja < 60 %) - modulis skeleto gale, į smailę nededamas.
  Ašies bangavimas U / H vertinamas be pratęsimų (galus tikrina A).
- Kiekvienoje šakoje lygiu žingsniu (<= p, n = ceil(L / p)):
  - **status galas** - per pusę žingsnio nuo krašto; **smailė** - skeleto gale;
  - **sankirta** - VIENAS modulis sankirtoje (pagal tiesiausią šakų porą), šakų pirmas modulis - per PILNĄ žingsnį;
  - **tarp dviejų sankirtų** - tik tarpiniai (galuose sankirtų moduliai);
  - **žiedas (O, D, 0)** - lyginis kiekis, fazė simetrijai viršus/apačia, kairė/dešinė.
- Modulis visada išilgai ašies; turi tilpti raidėje (>= 3 mm nuo šono). Netelpantis (linijos galas, lenkimas) -
  mažiausias pataisymas: pastūmimas išilgai ašies (<= 0,3 p), skersai (<= 6 mm), pasukimas (<= 20°); vis tiek netelpa -
  lape raudonas, o modulis tai grupei NETINKA.
- **Eilės (v31):** nuo LED Wizard taisyklės (žr. 3a) iki +2; kiekvienam eilių sk. - didžiausias tinkamas žingsnis;
  imamas variantas su mažiausiai modulių (KIWI: 1 eilė kas 210 - 27 vnt.; 3 eilės kas 220 - 35 vnt.).
- **Žingsnio grupės (v31):** raidės grupuojamos pagal linijos plotį (skirtumas <= 30 %) - LED Wizard „Locked" raidžių rinkiniui.
  Kiekvienai grupei: nuo min(laido ilgis 100 / 200 / 270 mm, tiekėjo žingsnis tame gylyje) žemyn kas 10 mm - pirmas,
  kuriuo VISOS grupės raidės tenkina U ir H. (Vienas žingsnis visai iškabai netinka: siauros raidės nuleidžia žingsnį
  plačioms - KIWI būtų 88 vnt. vietoj 24.)
- **„~p" (v34-v36):** grupės žingsnis p; raidė, kuri netenkina tik dėl diskretaus išdėstymo (pvz. sankirtos dėmė), gali imti
  p - 10 arba p - 20 (gamybos brėžiniuose žingsnis taip pat „~"). COOP: 108 -> 93 vnt.
- **Grupės (v36):** raidės vienoje grupėje, kol linijos plotis skiriasi <= 1,5 karto (`GROUP_W`; buvo 1,3 - didžioji „L"
  atsiskyrė nuo mažųjų). Mažos dalys (< 35 % raidės ploto medianos - i / ė taškai, ū brūkšnys) - artimiausios raidės grupei.
- **Per ploni elementai (v36):** kur linija siauresnė už modulį + 2 x 3 mm (pvz. serifinio „e" skersinis) - modulis
  nededamas (šviečia kaimynai), o ne žymimas raudonai; tos vietos ašies bangavimo U / H nevertinamos.
- **Tolerancija (v36):** U, A >= 0,95 x riba, H <= 1,05 x riba (`TOL_LO`, `TOL_HI`) - modelio neapibrėžtis; be jos
  ribinė raidė (0,62 prieš 0,63) perjungdavo visą užrašą į 2 eiles (+45 % modulių).
- **Užraitai (serifai) ir smailės** į ploto tolygumą A neįskaičiuojami (morfologinis atvėrimas r = 0,3 x plotis).
- **Plonų trumpų užraitų atšakos** (trumpesnės už linijos plotį ir plonesnės nei 0,6 x plotis) skeletone pašalinamos -
  modulių juose nėra. Storų „slab" užraitų (kaip testo „Lietuva tėvyne mūsų" L viršus) - lieka.
- **Papildomos eilės** tik kai linija platesnė už ~1,2 x žingsnį (gamybos pavyzdžiai); siauroms - viena eilė.
- **Lapas (v36):** ilgas užrašas be `groups` - žodžiai automatiškai į 2-4 eilutes, jei mastelis stambesnis (testas: 1:20 -> 1:10);
  jungtys tarp eilučių nebraižomos. Mažų dalių kiekis rašomas prie raidės: „3+1" (i + taškas), „7+3" (u + ū brūkšnys).
- Testas `Lietuva tėvyne mūsų` (1:1 kontūrai, 5253 x 500, gylis 100 - priimta): P65L kas 100, 120 vnt., 60 W;
  P130L / P190L netelpa (~84 mm serifinės linijos lenkimuose).
- **Modulis pagal grupę (v31):** grupei tinka modulis, kuris telpa visose jos raidėse ir tenkina U / H; iš tinkamų -
  mažiausiai modulių, kai skirtumas <= 5 % - mažesnė galia. Vienas tipas visai iškabai, jei tinka visoms grupėms ir
  modulių <= 10 % daugiau. Skirtingi moduliai - atskiros grandinės / įvadai (jei `groups` nenurodyta).
  Lentelėje - kiekvienas modulis visai iškabai (OK / NOT MET / DOES NOT FIT) ir mišrus variantas.

## 3a. LED Wizard principai (docs.ledwizard8.com, Rytis 2026-10-08: „gal tai padės algoritmui")
- **Spacing** - DIDŽIAUSIAS atstumas tarp centrų išilgai eilės, iš gamintojo tankio lentelės, ne didesnis už įtempto
  laido ilgį. Pas mus: žingsnis <= min(tiekėjo žingsnis tame gylyje, modulio laidas); simuliacija gali parinkti mažesnį.
- **Runs (eilės)** - pagal plačiausią raidės liniją ir gylį. Pas mus: 1 eilė, kol linijos plotis <= 1,25 x tiekėjo žingsnis
  (SloanLED: vienos eilės max = žingsnis x 1,25), kitaip ceil(plotis / žingsnis). Linijos plotis - 2 x atstumas iki šono
  ANT AŠIES (90 % procentilis), ne sankirtų „burbulas".
- **Clearance** - nuo šono iki pirmos eilės: 1 eilė - centre; 2 eilės - 25 % pločio; 3 - 1/6 (= plotis / (2 x eilės)).
  Eilės - vidinės lygiagretės (inlines) atstumais c, 3c, ...; siauros vietos - ašis („Auto Join"); nelyginis eilių sk. -
  ašis plačiausiose vietose.
- **Locked** - tie patys nustatymai raidžių rinkiniui -> vienodas ryškumas (pas mus - grupė pagal linijos plotį).
- **Target density** - modulių sk. ploto vienetui raidės dalyse (lape 2: vnt./m² kiekvienai raidei).
- **Uniform spacing** - eilės galai vietoje, tarpiniai tolygiai (pas mus - taip pat).
- **Red wires** - modulių laidas nepasiekia kaimyno -> pažymima (pas mus - lape „links longer than module wire").
- **Round** - aštrūs kampai apvalinami, moduliai ne į kampą (pas mus - smailėse modulių nėra, ašies „ūsai" pašalinti).
Šaltiniai: https://docs.ledwizard8.com/doc/lw8/7.1.2 (PowerFlow property bar), /6.3 (moduliai, eilės, laidai),
/6.12 (Target density), /8.13.6 (Density menu), /7.1.3 (PowerFlow tab).

## 4. Grandinė ir maitinimas
- Raidėje - artimiausias + 2-opt; laidas tiesiai raidės viduje arba ašimi (aplink kampą); jungtis ilgesnė už modulio
  laidą - pažymima („reikia prailginimo").
- **Maitinimas (Rytis 2026-10-09):** kiekviena grupė (`groups`) maitinama per VIENĄ tašką - laido išvestį nurodytoje
  vietoje (`"feed_at": ["right-bottom", "left-bottom", ...]` grupėms; numatyta "left-bottom"). Grandinė prasideda raidėje
  prie įvado. Viršijus tiekėjo ribą iš 1 galo (P65L 50 / P130L 40 / P190L 30 vnt.) - NESKAIDOMA, lape pastaba:
  įtampos kritimą kompensuoja stipresnis maitinimo šaltinis. Senas skaidymas / 2 galai - tik `"split_feeds": true`.
- Laido išvesties vieta - iš techninio lapo REAR VIEW (bėgelio galas su tašku ir „12V El. Output").

## 5. Lapas
1 lapas - CAD išdėstymas kaip gamybos pavyzdžiuose: aplink modulį apskritimas = žingsnis (spalva pagal modulį),
kiekis virš raidės, bendras matmuo apačioje; laidai, įvadai, palyginimo lentelė, MAIN DATA. Ilga iškaba su keliomis
grupėmis - eilutėmis, jei mastelis didesnis. 2 lapas - apšviestumo žemėlapis (E / tos raidės vidurkis - tolygumas raidėje)
+ modulis, U / H, „rel." (raidės vidurkis / visų raidžių mediana - ryškumo balansas tarp raidžių) kiekvienai raidei.

## Ryčio reikalavimai (galioja)
- Smailiose raidžių viršūnėse papildomų modulių NEDĖTI; išdėstymas simetriškose raidėse - simetriškas.
- Lape LED - tik kai Rytis patvirtino modulį; PSU atsargą klausti.

## Patikrinta v32 (v31 skliaustuose)
| Iškaba | Gylis | Rezultatas |
|---|---|---|
| PN894 „7-23" | 100 | P190L kas 230, 24 vnt. (25) |
| COOP 225921 (ALT8869) | 70 | v36: P130L kas 130-170, 87 vnt. (v34: 93; v32: 108), po 1 įvadą grupei |
| SPAR 225971 (siauros, ~78 mm) | 60 | P130L kas 100, 100 vnt. (P65L 121) |
| KIWI 225955 „KIWI minipris" | 100 | KIWI P190L kas 250 + mini pris P65L kas 100 (P190L / P130L mini pris netelpa) - žr. lapą |
| KIWI 225955 „7-23" | 100 | v36: P130L kas 130-150, 18 vnt. (v32: 20) |
Siaurose giliose raidėse simuliacija reikalauja tankiau nei tiekėjo dėžės lentelė - atitinka gido įspėjimą.

Kelios eilės patikrintos sintetiniu plačiu „L" (404 mm, 3 eilės) ir disku (1497 mm, 8 žiedai) - P130L 80 mm, kas 180, OK.
