# Etaloninis techninio lapo stilius (VISIEMS projektams)

Šis stilius yra privalomas bet kokiam produktui: raidėms ant folded plokštės, raidėms ant sienos /
bėgelių, pylonams, šviesdėžėms, plokščioms iškaboms ir t.t. Keičiasi tik produkto turinys
(vaizdai, pjūvis, BOM eilutės), bet NE lapo stilius. Vizualūs etalonai: `assets/etalonai/*.pdf`;
PAGRINDINIS kelių pozicijų komplekto etalonas - `assets/etalonai/SPAR_225960_komplektas_18_lapu.pdf`
(taisyklės `references/etalonas_spar_225960.md`, Rytis patvirtino 2026-10-08)
(MDM - stačiakampis 1:10, ALYTUS - labai platus 1:10, EXTRA - lygiagretainis, aukštas 1:20).
Prieš kuriant naujo tipo lapą - peržiūrėk bent vieną etaloną (pdftoppm -> PNG).

## Lapas
- A3 gulsčias. Rėmelis: kairė paraštė 20 mm, kitos 10 mm, 5 mm zonų juosta 1-8 / A-F.
- Šriftas GOST Common (`assets/gost_common.ttf`) visam lapui (atsarginis - osifont). Lapo užrašai - angliškai.
- Spalvos: juoda + pilka. Spalvos tik ten, kur jos yra informacija (RAL užpildai vaizduose, RAL
  pavyzdėliai BOM, 3D vaizdas). Jokių dekoratyvinių perėjimų, šešėlių ar paveikslų lentelėse.

## Zonos
- **Apatinė juosta - VIENTISAS blokas (Rytis 2026-10-07):** stulpeliai (pjūvis | BOM | MAIN DATA | REVISIONS +
  antraštė) be tarpų, bendros kraštinės, nuo juostos viršaus iki rėmelio apačios; BOM ir MAIN DATA eilutės
  išsitempia per visą bloko aukštį; REVISIONS - tuščios eilutės iki antraštės lentelės. Tuščių plotų nėra.
- **Apatinės juostos aukštis KINTA pagal eilučių kiekį (Rytis 2026-10-07):** BOM / MAIN DATA eilutė >= 11 pt
  (8 pt tekstas, nesugrūsta), juosta = max(172, 32 + 11 x eilučių); vaizdų zona atitinkamai mažėja
  (`lapas_core.set_band`, kviečiama prieš išdėstymą). DETAIL A aukštis gali mažėti (250 / 220 / 190).
- **Viršus (vaizdų zona):** visi vaizdai išdėstomi automatiškai (žr. „Išdėstymas").
- **Apačia - informacijos juosta per visą plotį** (~172 pt aukščio), iš kairės:
  `TIPINIS PJŪVIS (produkto profilis)` | `BILL OF MATERIALS` | `MAIN DATA` | `REVISIONS + antraštės lentelė`.
- Antraštės lentelė apatiniame dešiniame kampe (ISO 7200 principu): CLIENT, TITLE, ORDER NO.,
  FILE / DRAWING NO., SCALE (DIM. mm), FORMAT, SHEET, REV., PROJECTION (ISO 5456-2 trečiojo kampo
  simbolis), DRAWN, CHECKED, DATE, įmonės pavadinimas.
- NOTES bloko NĖRA (informacija kartojasi). Lentelių antraštės - šviesiai pilka juosta, ne juodas fonas.

## Vaizdai (projekcijos)
- FRONT VIEW - tikras kontūras (bet kokios formos), RAL užpildas, elementai vektoriais iš kliento failo.
- Sienos NEVAIZDUOTI nei projekcijose, nei pjūviuose (jokios brūkšniuotės „WALL").
- SIDE VIEW (RIGHT) - realus vaizdas iš dešinės, NE pjūvis. Dedamas dešinėje nuo priekio (3-iasis kampas).
  Tarpas iki priekio vaizdo proporcingas: max(50 pt, 11 % priekio vaizdo pločio).
- REAR VIEW (MIRRORED) - TIKRAS vaizdas iš nugaros originaliomis spalvomis (raidės, bėgeliai, plokštės);
  tvirtinimo elementai, jų ilgiai ir žingsniai; nematomi elementai - punktyru. BENDRŲ matmenų (plotis, aukštis)
  galiniame vaizde NEDĖTI - jie priekiniame. Galiniame vaizde TIK bendriniai rėmo matmenys (v8):
  bėgelių (rėmo profilių) ilgiai su profiliu, pvz. „3461 (U40x40x2)"; vertikalių/įstrižų profilių ilgiai žyma
  („546 vert.", „578 diag."); bėgelių ašių atstumai (viena grandinė grupės šone).
  Ausėlių grandinių / atstumų tarp ausėlių NEDĖTI. X apskritimo Z juostoms - tik ilgis (plotis) ir aukštis tarp centrų.
- Visi pjūviai (DETAIL A ir P6 ON RAILS) - vienoda pilkų spalvų schema (v9, žr. SKILL.md).
- DETAIL A - SECTION - tikras CAD pjūvis per tvirtinimą (1:2), su lūžio linijomis, siena su
  varžtai su ašinėmis linijomis (be sienos). Detalės žyma (A) pažymima šoniniame vaizde.
  Matmenų, kurie jau yra priekio vaizde, detalėje nekartoti.
- 3D VIEW - tikra aksonometrija (yaw 32°, pitch 17°), plokštuminis šešėliavimas pagal RAL, BE fono,
  sienos ir šešėlio. „ILLUSTRATIVE - NOT TO SCALE".
- Kiekvienas vaizdas: pabrauktas pavadinimas + po juo mastelis.

## Linijos
- Visų objektų kontūrai projekcijose ir pjūviuose - **HAIRLINE 0,1 pt** (`VIEW_MODE`). Storesnė linija
  gali būti palaikyta apvadu, lipduku ar papildoma detale.
  Ausėlės / tvirtinimo plokštelės - irgi hairline, su skyle visuose vaizduose, kur matoma jų plokštuma.
- Matmenų ir išvadinės linijos 0,25-0,3 pt, užpildytos rodyklės. Ašinės - brūkšnys-taškas.
- Lentelių ir lapo rėmeliai - 0,6-1,0 pt (jie ne objektai).

## Matmenys
- **Šrifto dydžiai (Rytis 2026-10-07, `lapas_core.py` F_*):** pagrindiniai matmenys (priekis, šonas) - 12 pt;
  rėmo matmenys (galinis vaizdas: bėgelių ilgiai, ausėlių ir ašių grandinės) - >= 8 pt, ant raidžių su baltu fonu;
  apatinės juostos blokai (BOM, MAIN DATA, REVISIONS, antraštė, pjūvio balionai) - >= 8 pt (netelpantis tekstas
  NEmažinamas žemiau 8 pt - trumpinti tekstą arba platinti stulpelį); vaizdų pavadinimai 13 pt, mastelis 9 pt.
- Grandininiai (chain) matmenys: kairėje vertikali grandinė (nuo kontūro iki elementų ir atgal),
  apačioje horizontali, viršuje bendras plotis ir elementų plotis. Pasvirusiems kraštams - lygiagretūs
  (aligned) matmenys. Pasvirimo kampas nurodomas.
- Visi matmenys mm, sveiki skaičiai (žingsnis gali būti su 1 skaitmeniu po kablelio).

## Masteliai ir išdėstymas
- Masteliai: 1:2, 1:5, 1:10, 1:15, 1:20, 1:25, 1:50 (ISO 5455 eilė + praktiniai 1:15, 1:25).
- Išdėstymą parenka skriptas: perrenka blokų kombinacijas ir mastelius, renkasi tą, kur vaizdai
  didžiausi IR panašaus dydžio (geometrinis vidurkis), mažiausiai tuščios vietos; laisvą vietą
  paskirsto tolygiai. Pozicijų rankomis nedėlioti - keisti vertinimą.

## Pozicijos (balionai) ir BOM
- Apskriti balionai, vienoda numeracija pjūviuose, vaizduose ir BOM. Detalių sudedamosios dalys -
  raidėmis (A, B, ...).
- BOM stulpeliai: POS | PART | MATERIAL | FINISH | QTY (PERIMETER / AREA). THK stulpelio nėra.
- **Spalvos BOM (Rytis 2026-10-07):** FINISH langelis užpildomas VISAS spalva, jame - spalvos kodas
  (`RAL 5003`, `3M 3630-125`); ant tamsios spalvos tekstas baltas. Mažų pavyzdėlių nebėra. Plėvelė: MATERIAL
  `Vinyl foil, cast`, FINISH `3M <kodas>` (spalva iš `VINYL` lentelės `lapas_core.py`; naują kodą įrašyti ten).
- Kiekiai skaičiuojami automatiškai iš geometrijos: perimetras (m) + plotas (m²) paviršiams,
  ilgis (mm) profiliams, vnt. tvirtinimams. Formulės užrašomos (`2 x 2250 = 4500 mm`).
- Nežinomos reikšmės - TUŠČIA vieta įrašymui pagal faktą (ne „?", ne raudona). Tekstas su „:"
  gauna rašymo liniją.

## Kliento grafika lape (v151, visiems produktams)
Kliento maketas / logotipas / tekstas lape - `lapas_core.place_pdf(src_pdf, pno, clip, tl, tr, bl)`: tikslus kliento PDF
fragmentas (vektorius + gyvas tekstas + paveikslėliai + gradientai), 2D - stačiakampis, 3D - lygiagretainis (r3d `S.V.S`
kampai). NEPERPIEŠTI `get_drawings` kontūrais - praranda tekstą, paveikslėlius, gradientus (Thales rev B klaida).
v155: įdedamas fragmentas - ATSKIRAS 1 psl. PDF, iš kurio redakcija pašalinta viskas už iškarpos ir kliento matmenų
užrašai (Thales `clip_src`) - kitaip Corel / tekstų sąraše matosi kliento antraštės Arial / Gotham šriftais. Lapo tekstas - tik GOST Common;
po generavimo patikrinti `pdffonts` / span šriftus: kiti šriftai leidžiami TIK matomoje kliento grafikoje.
v156 / v157 (Rytis 2026-10-13): KLIENTO TEKSTAI VISADA KREIVĖMIS (vektoriai, ne tekstas) - `K.pdf_text_to_paths(fn)`
(`scripts/pdf_outline.py`: keičia TIK teksto operatorius, spalvos / ICC / overprint / skaidrumas lieka baitas į baitą).
GHOSTSCRIPT AR KITO PERRAŠYMO (pdfwrite, perrenderinimo) KLIENTO GRAFIKAI NENAUDOTI - v156 pakeitė spalvas.
KLIENTO GRAFIKA VISADA ATITINKA ORIGINALĄ visose projekcijose, vaizduose ir failuose (Rytis 2026-10-13, svarbi taisyklė):
- korpuso / fono spalvos (RAL plotai po grafika, 3D kūnai) - imamos iš kliento PDF užpildo (Thales `client_fill`), ne hex iš akies;
- patikra po generavimo: fragmento atvaizdas = kliento originalo atvaizdas (CMYK, pikselių skirtumas ~0), OP / ICC objektų skaičius
  nepasikeitęs, `pdffonts` - tik GOST Common (+ nenaudojamas Helvetica), poppler be „Unknown font tag".

## Ko nedaryti
- Neišgalvoti matmenų, medžiagų, storių, tvirtinimų - palikti tuščią vietą ir paklausti.
- Neįterpti paveikslėlių / renderių iš kitų dokumentų - viskas braižoma tuo pačiu CAD stiliumi.
- Nedėti storų kontūrų objektams, dekoratyvinių blokų, NOTES bloko.

## MAIN DATA
- VISADA eilutė „Weight (calc.)": ≈ N kg / pcs, excl. PSU (skaičiuojama pagal `assets/svoris.json`).
- P6 tipinis pjūvis juostoje - Rytio etaloninė geometrija (`assets/p6_profiliai.pdf`); pjaunami lakštai juodai (ISO 128-50), plexi štrichuotas, kontūrai 0,35 pt, be spalvų, be mazgo detalizacijos; balionai 1-5 (+A tik 3 mm).
- Šriftas visur - GOST Common (`assets/gost_common.ttf`).


## Profilių forma (v47, Rytis 2026-10-09)
U profilis visuose vaizduose braižomas kaip U, stačiakampis - kaip stačiakampis vamzdis, L - kaip L. Ta pati forma DETAIL, pjūviuose, šoniniame vaizde ir 3D.

## Linijos projekcijose (v63, Rytis 2026-10-09)
Visų projekcijų (priekinis, šoninis, galinis vaizdas, 3D) objektų linijos - hairline (0.1 pt): kontūrai, bėgeliai, ausėlės, trafo dėžė, sandūros. Storesnės lieka tik matmenų / išvadinių / pavadinimų / rėmelio linijos ir laidas (raudonas 0.9 pt).


## (iš SKILL.md v75) Lapas (v9)
- A3 paraštės minimalios: 5 mm iki išorinio rėmelio, 4 mm zonų juosta.
- ORDER NO. - visada paryškintas 14 pt; nežinomas -> šablonas `ALT0000_00.00_RS`.
- PROFILE P6 ON RAILS pjūvis - TOS PAČIOS spalvos kaip DETAIL A (P6+3): šonai #6E6E6E, galas ir bėgeliai
  #B4B4B4, ausėlės #8C8C8C, PVC #C8C8C8, plexi baltas, varžtai #3A3A3A (`p6_ref.COLOR = True`).


## (iš SKILL.md v75) PDF atidarymas CorelDRAW (Rytis 2026-10-08, patikrinta CorelDRAW 2026 Mac)
- Tekstas PDF'e turi likti TEKSTU ir neišsikraipyti. GOST Common faile PostScript vardas su tarpu („GOST Common");
  reportlab / macOS rašo „GOST-Common" -> Corel ieško „GOST" + stilius „Common", neranda, keičia Helvetica
  (išsibarsčiusios raidės). `lapas_core.pdf_fix_fonts(pdf)` pakeičia BaseFont / FontName į `/GOST#20Common` -
  kviečiama automatiškai `K.save()` ir `braizyti_lapa.py` pabaigoje; sujungus komplektą - iškviesti dar kartą.
- Patikra: `{x[3] for p in pdf for x in p.get_fonts()}` -> „GOST Common" (ne „GOST-Common").
- Corel importas: „Import text as: Text", be „Convert reusable objects into symbols". Kompiuteryje turi būti įdiegtas
  GOST Common (`assets/gost_common.ttf`; Ryčio Mac'e yra `~/Library/Fonts/gost_common.ttf`).
- .cdr - Corel: atidaryti PDF -> Save As `Drawing_<projektas>.cdr` tame pačiame aplanke.



### (iš SKILL.md v80) 3D (r3d) - visi nauji lapai (v38)
`scripts/r3d.py`: vektorinis 3D su teisingu užstojimu - persidengiančių paviršių gylis lyginamas TAME PAČIAME 2D
persidengimo taške (plokštumų lygtys, Newell normalė) -> grafas -> topologinis rikiavimas (ciklai - pagal vidutinį
gylį) -> piešiama iš galo. API: `Scene(yaw, pitch)`, `face`, `box`, `extrude_xy(geom, z0, z1, side, face, edge, xf)`,
`render(box)`. Senas `View3D.solid` (rikiavimas pagal centroidą) - netikslus (prasišvietimas / dingimas).
3D ant fasado su aplinka (pvz. prekybos centro vidus: grindų plytelės, kaimyninės parduotuvės, karnizas, kolonos,
vazonai, suolas) - `scripts/projektai/clasohlson_horten/sheet2v.py: environment()`; platesnis vaizdas, kai prašoma.



### (iš SKILL.md v81) Matmenų taisyklės - visi lapai (v38, Rytis 2026-10-09)
- Viena aiški grandinė eilutėje; maži užrašai iškeliami UŽ grandinės, nesispaudžia į vieną vietą.
- Tankios grandinės (n x žingsnis) - tik `50 | n x p = L | 50` + ašys, ne kiekvienas tarpas.
- Smulkūs mazgai - DETAIL 1:2 lūžęs vaizdas (briauna | lūžis | raidė), ne visas gaminys.
- Ant fasado / raidžių užrašų nededama; pagr. matmenys 12 pt, kiti >= 8 pt.



### (iš SKILL.md v82) Matmenys priekio vaizde (bėgelių modulis)
- Bendras plotis / aukštis + grandinės; grandinė, kartojanti tik bendrą matmenį, nededama.
- Kairė: jei yra plokštė - plokštės ir raidės grandinė; jei NĖRA - kairiausios grupės raidžių viršai ir
  apačios (klasteriai 20 mm, atstovas - didžiausios raidės kraštas; i taškai ir brūkšniai - tik gabaritas),
  pvz. COOP: `240 | 467 | 118 | 85`. Šios grandinės NEŠALINTI.



### (iš SKILL.md v83) Bendras branduolys `scripts/lapas_core.py`
Nauji produktų moduliai rašomi su juo (rėmelis, primityvai su hairline, matmenys, balionai, lentelės,
antraštė, P6 tipiniai pjūviai `p6_typical(variant=rail|folded|plate)`, 3D `View3D`). Senasis
`braizyti_lapa.py` (folded) dar savarankiškas - stilius tas pats.



## (iš SKILL.md v83) Bėgelių lapas - vaizdai ir antraštė
- **Antraštės lentelė (Rytio pavyzdys 2026-10-07):** CLIENT - užsakovas (pvz. BrandFactory, 14 pt bold), TITLE,
  ORDER NO. (14 pt bold, formatas pvz. ALT0000_00.00_RS) | FILE / DRAWING NO. (`drawing_no`), SCALE (DIM. mm) |
  FORMAT | SHEET | REV. | PROJECTION, DRAWN | CHECKED | DATE | tuščias; įmonės pavadinimo apačioje nėra.
- **Galinis vaizdas - tikras vaizdas iš nugaros:** raidės ir bėgeliai originaliomis spalvomis (raidės - šonų
  RAL, bėgeliai - RAL 7035), už plokštės esančios raidės - punktyru; užrašai su baltu fonu.
- Lapas: FRONT (raidžių priekis vinilo spalva), SIDE (plokštė, bėgeliai, raidės), REAR (TIK bėgelių ilgiai,
  vert./diag. žymos, ašių atstumai, X Z juostos ilgis + aukštis tarp centrų; BE ausėlių grandinių), DETAIL A - 6+3 pjūvis, 3D; juostoje - P6 ant bėgelių tipinis pjūvis.
- **Rėmo matmenys galiniame vaizde (Rytis 2026-10-07):** NIEKO neuždengia - visi už raidžių gabarito: viršuje /
  apačioje 1 eilė - ausėlių grandinė, 2 eilė - bėgelio ilgis „L (U..)", 3 eilė - žymos su išvadine (statmenys,
  vidurinis bėgelis, i taško laikiklis); ašių grandinė - šone už grupės; matmenų tekstai pasislenka nuo išvadinių.
  Galinio vaizdo mastelis ne smulkesnis nei 1,5 x priekio.


## (iš SKILL.md v85) Lapas (v9) -> `references/stilius.md` („Lapas (v9)": paraštės 5 / 4 mm, ORDER NO. 14 pt bold, pjūvio spalvos = DETAIL A)


## CAD žymėjimai (v137, Rytis 2026-10-12: „žymėjimai lipa ant projekcijų, pjūvio linijos ir žymėjimai sugrūsti ant projekcijos, nuorodos linijos kertasi")
- **Pjūvio plokštuma (ISO 128-40/44):** per vaizdą NEBRAIŽOMA. Tik storos trumpos atkarpos UŽ vaizdo ribų (abiejuose galuose),
  rodyklės žiūrėjimo kryptimi, raidės prie rodyklių - už vaizdo. `lapas_core.cut_plane(x, y0, y1, "A")` / `cut_plane_h`.
  Atkarpos nesikerta su matmenimis - matmenų grandinės atitraukiamos (>= 32 pt nuo kontūro, kai yra pjūvio žyma).
- **Balionai / žymos su tekstu - STULPELYJE UŽ vaizdo ir už matmenų** (`balloon_column`, `tag_column`): surikiuoti pagal taikinio
  y, tarpas >= 2r + 3 -> išvadinės NESIKERTA tarpusavyje; ant projekcijos - tik išvadinės taškas. Ant projekcijos tekstų
  (pvz. „SIDE A", pastabų apie stiklą / korpusą) NEDĖTI - tai vaizdo pavadinime, pjūvyje ar MAIN DATA.
- Konstrukcinė informacija (stiklas > korpusas, užlaidos) - tik pjūvyje / DETAIL su matmenimis, ne pastaba priekio vaizde.
- Komponentų numeriai vaizduose = BOM POS (1.1, 1.2, 1A ...), ne laisvas tekstas.
- **v138 (Rytis 2026-10-12): išvadinės (balionų / žymų linijos) - ĮSTRIŽOS**, ne horizontalios ir ne vertikalios (ISO 128-22),
  kad nesimaišytų su matmenų linijomis: `balloon_column` / `tag_column` - nuolydis ~33° (iki 42 pt pakilimo), tvarka
  parenkama, kad linijos nesikirstų (taikiniai tuo pačiu kraštu - tvarka pagal y).
- **Tvirtinimo elementai (varžtai) matomi projekcijose:** galvutės vaizduose, kur matoma jų plokštuma (vaizdas iš sienos,
  TOP VIEW), pjūviuose - galvutė + kotas, 3D - galvutės. Montavimo plokštės 3D - su skylėmis ir vamzdžio anga (ne vientisos).
- **v139 (Rytis 2026-10-12): AUTOMATINIS ŽYMĖJIMAS - NUMATYTAS visiems naujiems lapams** („nuorodų linijos chaotiškos ...
  gamybininkas pirmiausiai skaito vizualinę informaciją"): `K.balloon_auto(tx, ty, label | tekstas, kind="balloon"|"tag")`,
  lapas braižomas 2 kartus (`K.auto_begin("collect")` -> PDF -> `K.auto_place(pdf)` -> `K.auto_begin("draw", vietos)` -> vėl).
  Kiekvienas balionas - ARTIMIAUSIOJE laisvoje vietoje šalia detalės (rastro kaukė: linijos, užpildai, matmenys, tekstai,
  stiklo šviesus užpildas - užimta), trumpa įstriža išvadinė (30-60°), kuo mažiau kerta brėžinio linijų, nekerta kitų išvadinių.
  Ribota zona (DETAIL juostoje) - `K.AUTO["region"]`. `balloon_side` / `balloon_column` automatinio režimo metu - per balloon_auto.
- Varžtai 3D - apvalios galvutės (diskai), stiklas 3D - baltas (amb 0,97), ne pilkas.
- **v145 (Rytis 2026-10-12, PATAISO v141): MATMENŲ EILIŠKUMAS** - arčiausiai objekto (1 eilė, `D1` 16 pt) - papildoma
  grandinė, už jos (2 eilė, `D2` 36 pt) - bendras (gabaritinis) matmuo, kad grandinės išvadinės NEKIRSTŲ bendro matmens
  linijos. Funkcijos `HM` / `VM` (`scripts/sviesdeze.py`), taip daryti visuose naujuose lapuose.
- **v145: VIENA LINIJA - VIENA PRASMĖ.** Grandinėje nemaišyti skirtingų dalykų (pvz. stiklo storio, plokštės kraštų ir skylių
  vienoje eilutėje): skylės nuo plokštės kraštų - viena grandinė, plokštės plotis - jos gabaritas, dėžės storis - kitoje pusėje.
  Grandinėje su keliais vienodais skaičiais - prierašas (pvz. „284 (legs)", „53 (leg in)", „340 (plate)").
- **v145: matmenų tarp LED nededama** (LED kiekis ir žingsnis - LED lentelėje / MAIN DATA).
- **Šriftai vienodi visame lape (v145 Rytis: „nepataisyti šriftų dydžiai"):** VISI matmenys vieno dydžio - 12 pt (ir grandinės,
  ir gabaritai); žymos, pastabos - 8 pt; vaizdų pavadinimai 13 pt, masteliai 9 pt. Šviesdėžė: `K.F_DIM_FRAME = K.F_DIM_MAIN`.
- **v152 (Rytis 2026-10-13: „nenaudojamos skill įrašytos taisyklės dėl žymėjimo ... lipama vienas ant kito ar suspaudžiama
  iki nesuprantamo žymėjimo; šriftai vėl skirtingo dydžio“):**
  - Kiekvieno NAUJO lapo skripte - `DIM = K.F_DIM_MAIN` ir VISI `hdim / hchain / vchain` su `DIM` (jokių 8 / 10 matmenims);
    kampai (10°) - irgi matmenys, 12 pt, ne paryškinti. Pastabos / žymos 8 pt, pavadinimai 13, masteliai 9.
  - Atstumai: grandinė 16 pt nuo kontūro, gabaritas 36 pt (antra eilė), trečia eilė 52+. Arčiau - NE.
  - `lapas_core.hchain`: mažo tarpo užrašas - tik kraštinio tarpo išorėje (už grandinės galo); vidurinio - eilėje TOLIAU
    nuo objekto su išvadine; niekada ant kaimyninio tarpo rodyklių. `vchain`: mažas tarpas - horizontalus užrašas šone
    nuo objekto su išvadine, vienas kito neliečia (`free` patikra).
  - Jei 12 pt grandinė mastelyje NETELPA (pvz. 30 | 40 | 40 | 30 per 140 mm 1:20, ankerių žingsniai 1:15) - jos tame
    vaizde NEDĖTI: tik gabaritas, smulkūs matmenys - pjūvyje / DETAIL stambesniu masteliu (nuoroda tekstu).
  - Ant projekcijų tekstų nėra (rėmo elementų ilgiai - BOM formulėje / matmenimis, ne užrašai ant profilių).
  - Žymų (tag) tekstai ir balionai - ne ant kito vaizdo, ne ant pavadinimų, išvadinė nekerta matmenų tekstų.
  - Ilgi elementai (ankeris) - nutraukti lūžio linija, tikras ilgis matmeniu (pvz. „hef 125").
  - PO GENERAVIMO peržiūrėti VISUS lapus 110+ dpi ir taisyti, kol nėra persidengimų.
- **Spalvos vaizduose = užsakytos RAL** (pvz. RAL 7024 korpusas / rėmas - tamsiai pilka vaizduose ir 3D); A2 varžtai - šviesūs.
