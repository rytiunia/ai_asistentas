# Auselių išdėstymas ant U bėgelių

Įgyvendinta: `scripts/auseles.py` (kviečia `braizyti_begeliai.py`). Smax reikšmės - `assets/auseles_smax.json`
(lentelę keisti TIK ten, šis failas - aprašas).

## Fizika (svarbiausia) - `assets/tvirtinimas.json`, `scripts/auseles.py`
Ausėlių kiekį ir tarpus lemia ne vien geometrija. Kiekvienam bėgeliui tikrinama:
1. **Apkrova:** vėjas pagal EN 1991-1-4: qp(z) = ce(z)·0,5·ρ·vb² (numatyta vb,0 = 24 m/s, reljefo
   kategorija III, z = 8 m -> qp ≈ 0,56 kN/m²; PATIKRINTI su LST EN 1991-1-4 NA ir objekto aukščiu),
   jėgos koeficientas cf = 1,8 (signboard, EN 1991-1-4 7.4.3 - konservatyvu raidėms atitrauktoms nuo
   sienos) + savasis svoris 0,15 kN/m². Raidžių priekio plotas paskirstomas išilgai bėgelio
   (vertikalūs pjūviai kas 10 mm), dalinamas tarp nešančių bėgelių; raidės už bėgelio galų - galiniam segmentui.
2. **Inkaras:** apkrova ausėlei (pusė tarpų iš abiejų pusių + konsolė) ≤ rekomenduojama inkaro apkrova
   sienai (`spec "wall"`: concrete 0,71 / solid_brick 0,59 / sand_lime 0,60 / hollow_sand_lime 0,33 /
   perforated_brick 0,17 / aerated_G4 0,14 kN - fischer SX 8, jau su saugos koeficientu; Ø6 skylė ->
   5-6 mm varžtas). **Siena nenurodyta -> `concrete` (v90, Rytis 2026-10-11: fasadas VISADA laikomas betoniniu, į kurį
   galima tvirtinti bet kurioje vietoje; fasado niuansai nurodomi papildomai).** `unknown` - tik kai Rytis nurodo, kad siena neaiški.
3. **Bėgelio stiprumas ir įlinkis:** U profilio W, I (lenkimas statmenai sienai), Al f0 = 120 MPa, γM1 1,1,
   γQ 1,5; tarpas - laisvai atremta sija, įlinkis ≤ L/150; konsolė ≤ C/75.
4. **Perteklinis tvirtinimas:** bėgelis > 1500 mm - min. 3 ausėlės (plastikinių inkarų ETA
   „multiple use": nutrūkus vienam taškui apkrova persiskirsto; 2 ausėlės ant ilgo bėgelio - NE).
5. **Praktinė riba Smax** (lentelė žemiau) - montavimas, sienos nelygumai; galioja mažesnis iš fizikos ir lentelės.
Lape: MAIN DATA `Wind qp` ir `Ear load` (max kN/ausėlei, siena).

## Smax - praktinė viršutinė riba tarp gretimų auselių (mm)

H = tipinis raidės aukštis grupėje (raidžių aukščių mediana - p uodegos, i taškai, brūkšnys neįtakoja).
"script" = rašytinis / plonų elementų šriftas (spec grupėje: `"font_style": "script"`, numatyta `regular`).

| Profilis          | H ≤ 500 | 500 < H ≤ 800 | H > 800 |
|-------------------|---------|---------------|---------|
| U 30x30x2         | ?       | 1000          | ?       |
| U 30x30x2 script  | ?       | 650           | ?       |
| U 40x40x2         | 3300    | ?             | 1200    |
| U 40x40x2 script  | ?       | ?             | ?       |

Šaltiniai: EXTRA 1400 (U30, 1000), Matkroken (U30 script, 650), COOP PRIX (U40, 3300), EXTRA 1800 (U40, 1200).
"?" -> skriptas tarpinių nededa, išspausdina perspėjimą; klausti Ryčio.
**Script šriftas:** Smax lentelės reikšmė (0,65 x paprasto) - rekomendacija; tarpas gali ją viršyti iki 15 %
(`smax_tol`), jei taip sutaupoma ausėlių pora; fizikos patikros lieka griežtos (Rytis 2026-10-07: MATKROKEN -
8 ausėlės, ne 10). Paprastam šriftui `smax_tol` = 0.
Vienkartinis perrašymas: grupėje `"ears_smax": 1400` arba visam lapui `"ears": {"smax": 1400}`.

## Taikymas (scripts/auseles.py - optimizacija, ne tolygus žingsnis)
**Pailginimas (Rytis 2026-10-07):** nepailginta ausėlė VISADA pirmiau - jei lange iki 300 mm nėra laisvos vietos,
imama artimiausia standartinė vieta už lango (jei konsolė / inkaras išlaiko); pailginta - tik kai be jos sprendinio nėra.
**Skylė:** Ø6 ant 30 mm profilio, Ø8 ant 40 mm ir didesnių.
**Rėmas su viršutiniu + apatiniu bėgeliu (Rytis patvirtino 2026-10-07) - `place_frame`:**
- TARPINĖS ausėlės POROMIS vienoje vertikalėje (viršutinė ir apatinė tame pačiame x; jei raidės neleidžia -
  mažiausias poslinkis iki 150 mm); tarpai ≤ Smax ir fizikos patikros; mažiausias porų kiekis.
- KRAŠTINĖS (pirma raidė, pvz. „c", ir paskutinė, pvz. „x") lygiavimo nesilaiko: kuo arčiau galo, BET vengiant
  pailginimo - pirmiau standartinė laisva vieta iki end_max (pvz. „c" angoje pastumti link raidės centro),
  tik tada pailginta su MAŽIAUSIU pailginimu lange ≤300 mm.
- Nepavykus poromis - kiekvienam bėgeliui atskirai (`place_rail`, žemiau); fizikai neišlaikius -
  geometrinis išdėstymas su perspėjimu.

Kiekvienam bėgeliui atskirai (atsarginis būdas):
1. Kandidatai: visos padėtys kas 5 mm, kur skylė Ø6 laisvoje zonoje (centras ≥ 15 mm nuo kontūro,
   ne raidės viduje): tarpai tarp raidžių / žodžių, atviros ir uždaros ertmės, X/A V tarpai.
   Pailgintos (aukštinamos į rėmo vidų iki 250 mm) - tik iki 300 mm nuo galų ir tik ten,
   kur standartinė netelpa.
2. Sprendinys - kelias per kandidatus (dinaminis programavimas) su sąlygomis:
   tarpas tarp gretimų ≤ Smax ir ≥ 150 mm;
   **KRAŠTINĖS (Rytis patvirtino, abu galai vienodai):** pirmoji ir paskutinė ausėlė - KUO ARČIAU bėgelio
   galo galimoje pagal taisykles vietoje: ≤ 300 mm nuo galo, jei ten yra laisva vieta (įskaitant ribotai
   pailgintą); jei nėra - artimiausioje laisvoje vietoje (+25 mm). Pvz. COOP: tarp „i" ir „x" ausėlė
   dedama prie „x", ne prie „i". Šis reikalavimas SVARBESNIS už mažiausią kiekį - geriau papildoma
   ausėlė, nei ilga konsolė prie galo.
3. Kriterijai eilės tvarka (kai kraštinių sąlyga įvykdyta): (a) MAŽIAUSIAS ausėlių kiekis;
   (b) be pailgintų - pailginta tik jei be jos sprendinio nėra; (c) kraštinės kuo arčiau galų
   (3 balai/mm - nusveria (d)); (d) didesnis atstumas iki kontūro (iki 40 mm), tolygesni tarpai.
   **Pailginimo riba:** ne daugiau kaip iki rėmo vidaus vidurio (pusė tarpo tarp viršutinio ir apatinio
   bėgelio) ir ne daugiau 250 mm - ausėlė negali nusileisti iki kito bėgelio.
4. Sprendinio nėra -> leidžiama toliau nuo galo + perspėjimas; vis tiek nėra -> spręsti ranka.
5. Vidurinis bėgis ir statmenys ausėlių negauna.
6. Lape: ausėlės HAIRLINE su Ø skyle visuose vaizduose (priekinis, galinis, 3D); galiniame vaizde ausėlių grandinė nuo bėgelio galų, pailgintos braižomos aukštesnės;
   BOM `{PLATES_N} pcs. ({PLATES_EXT} extended)`.

Patikrinta su Rytio pataisymais: FAS 1800U80 (EXTRA 720 mm, U30) - 4 + 4 be pailginimų
(E/X, X/T, T/R, R/A viršuje; E/X, X/T, R anga, A vidus apačioje), 7-23 - 2 + 2.


## (iš SKILL.md v75) Ausėlių žingsnio tolerancija (v8)
Tarpas tarp ausėlių gali viršyti Smax iki **+5 %** (pvz. 1250 > 1200) - tada papildoma pora NEDEDAMA.
Priežastis: FAS1800 atveju dėl 50 mm viršijimo atsirado nereikalingos ausėlės ties R pilvu ir kojele.
Ausėlės dedamos tik ten, kur būtina pagal vėją / ankerį; nedėti „dėl gražumo".

## Rėmo gale - viena ausėlė, ne dvi šalia (v94, Rytis 2026-10-11)
Jei rėmo gale (pvz. prie „S") išdėstymas duoda dvi ausėles viena šalia kitos (< 0,5 Smax), paliekama VIENA - leistinoje
vietoje kuo arčiau galinės reklamos dalies (kraštinė). Tarpas iki kitos ausėlės gausis didesnis už Smax (leidžiama iki
1,5 Smax) - toks sprendimas logiškesnis nei dvi ausėlės greta. Bėgeliui > 1500 mm lieka >= 3 ausėlės. Apkrova ausėlei
perskaičiuojama; viršijus inkaro rekomenduojamą - perspėjimas `! apkrova ausėlei ... > inkaro` (Rytis sprendžia).



## v190 (Rytis 2026-10-13, „Alytus,"): ausėlės pagal apkrovą prie rėmo galų
- Bėgelis, pratęstas už rėmo kampo (pvz. iki kablelio, pratęsimas <= end_max), - konsolė: kraštinė ausėlė ieškoma prie RĖMO
  KAMPO (galinio statmens), ne pratęsimo gale; konsolės apkrova ir ilgis tikrinami iki tikro bėgelio galo (`over_ok`).
  Ilgas pratęsimas (pakopinis rėmas, > end_max) - savas galas, kaip anksčiau.
- Konsolėje spausdinamos kiekvienos ausėlės apkrovos (kN) - matyti, ar kuri nors perkrauta.
