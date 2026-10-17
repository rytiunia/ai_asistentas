# GALIOJANČIOS LAPO TAISYKLĖS + NAUDOJIMO LOGIKA (suvestinė)

Atnaujinta: v330 (2026-10-17)

Rytis 2026-10-16: „išsaugok taisykles ir naudojimo logiką ir padaryk, kad kitą kartą vėl nebūtų daroma su senomis
taisyklėmis ir nustatymais".

Šis failas yra VIENA vieta, kur surašyta, kaip DABAR daromas bet kuris A3 techninis lapas. SKILL.md numeruotos taisyklės
yra istorija su priežastimis. Kur jos prieštarauja šiam failui, galioja naujesnė vNNN (taisyklė 0b), o šis failas
atnaujinamas tame pačiame commit'e.

`patikra_lapas.py` tikrina, kad šio failo „Atnaujinta: vNNN" nebūtų senesnė už SKILL „Versija". Jei senesnė, išmeta klaidą
SUVESTINĖ PASENUSI.

## P6 - PAGRINDINĖ TAISYKLĖ (v320, Rytis 2026-10-16: „išsaugok kaip pagrindinę taisyklę P6")

Galioja VISIEMS P6 darbams. Testai: `scripts/projektai/bandymas_3500/` (P6 ant U 30x30x2) ir
`scripts/projektai/bandymas_3500_folded/` (P6 ant folded 3900 x 1000 x 40) - po generatorių pakeitimų turi duoti tą patį.

| | P6 ant RĖMO (U / L / □) | P6 ant FOLDED fono |
|---|---|---|
| Tvirtinimas D3.2 | kvadrato / trikampio principas (4 / 3, štrichų centrai ant bėgelio ašies) | tas pats principas, ašys be rėmo (`--folded`) |
| Drenažas Ø8 | PUSLANKIS dugno kontūre (išpjaunamas su kontūru) | SKYLUTĖ dugne + ta pati skylė fone |
| DXF | `p6_dxf.py --rails-json` (raidės + rėmas) | `p6_dxf.py --folded` (raidės) -> `scripts/p6_folded.py` (v327, BENDRAS: `folded_dxf.py` išklotinė + LETTER_POSITION + LETTER_FIX_D3.2 / HOLE_D11_CABLE / DRAIN_D8 1:1 kaip raidžių dugne + raidės) -> vienas DXF |
| Lapas | `braizyti_begeliai.py` | `braizyti_lapa.py` |
| Skylės fone | - | D3.2, D11, Ø8 - TOS PAČIOS vietos kaip raidžių dugne (1:1); tvirtinama gamyboje pagal faktą |
| Laidas iš fono | - | Ø11 briaunoje: 15 mm nuo lenkimo linijos (fono priekio) ir 15 mm nuo viršaus (v321) |

Detalės: D2 (tvirtinimas), E3 (drenažas, P6 ant folded). Laukiamas rezultatas - testų README.
REGRESIJA: `python3 scripts/test_p6.py` = OK (po kiekvieno p6_dxf / braizyti_begeliai / braizyti_lapa / folded_dxf pakeitimo).
Formos principas (taškų skaičius iš supaprastinto gaubto, pirmas - toliausiai nuo centro, toliau FPS) - VIENA vieta
`scripts/tvirtinimas.py` (v327): p6_dxf D3.2 (gaubtas 0,16) ir akrilo rėmo smeigės braizyti_begeliai (0,12).

## A. Darbo eiga - PRIVALOMA kiekvieną kartą

1. `git pull` (repo `rytiunia/ai_asistentas`, `reklama/`). Dirbti TIK iš klono. Paskyros kopijos ir atmintis nėra
   taisyklių šaltinis.
2. Perskaityti ŠĮ failą. Tada `python3 scripts/ziniu_paieska.py <produktas> <raktažodžiai>` (taisyklė 0) parodo šeimos
   generatorius, etalonus ir naujausias taisykles.
3. Generatorius parenkamas pagal katalogą (`references/produktu_katalogas.md`).
   - Seno projekto skriptas (`scripts/projektai/...`) yra tik DUOMENŲ analogas.
   - Jo koordinatės, masteliai ir užrašai NEkopijuojami. Kopijuojant iš karto pritaikyti šio failo B-D dalis.
4. Braižoma TIK per `lapas_core` (K) ir `layout_engine` (LE) funkcijas, nurodytas žemiau. Ranka rašytos koordinatės, masteliai
   ar „gražinimai" negalimi: patikra juos randa.
5. `python3 scripts/patikra_lapas.py lapas.pdf` turi duoti 0; DXF - `python3 scripts/patikra_dxf.py *.dxf` = 0 (v302).
   - KREIVĖS VISADA LANKAIS (v313, Rytis: „taisyklė, kuri turi veikti visada") - E3b; patikra_lapas tikrina ir lapą, ir
     šalia jo esančius to paties vardo DXF.
   - Patikra kartu paleidžia `taisykliu_lint.py` lapo generatoriui (kelias imamas iš `<lapas>.pdf.art.json`).
   - Paskui lapas peržiūrimas AKIMIS: PNG, visas lapas ir priartinti blokai.
   - REGRESIJA (v326, Rytis 2026-10-16: „sistema turi veikti stabiliai ir klaidos neturi kartotis"): po KIEKVIENO bendro
     generatoriaus / `lapas_core` / patikros pakeitimo, prieš commit - `python3 scripts/regresija.py` (visi etaloniniai /
     testiniai projektai pergeneruojami laikiname veidrodyje, patikra_lapas / patikra_corel / patikra_dxf / test_p6 = 0).
     Kiekviena ŽINOMA išimtis - `KNOWN` su priežastimi. Naujas tipinis projektas -> naujas `CASES` atvejis.
   - Aplinka: `pip install -r requirements.txt` (+ sistemoje `qpdf`).
6. Ryčio pataisa = nauja taisyklė. TAME PAČIAME commit'e:
   - (a) SKILL.md įrašas su priežastimi;
   - (b) ŠIS failas (B-D dalis + „Atnaujinta");
   - (c) vykdymas `lapas_core` / generatoriuje;
   - (d) patikros punktas `patikra_lapas.py` arba lint taisyklė `taisykliu_lint.py`;
   - (e) pergeneruoti tos dienos / atviro užsakymo lapai, kad patikra = 0;
   - (f) `python3 scripts/regresija.py` - visi OK (v326).

   Versiją kelti `python3 scripts/versija.py "aprašas"`: pakelia SKILL ir šio failo versiją kartu.
7. Atsakyme nurodyti „reklama vNNN, GitHub <hash>". Lapas siunčiamas tik su patikra = 0.

## B. Lapo išdėstymas (TAISYKLĖ 33, `references/adaptive_layout.md`)

- Fiksuotų koordinačių nėra. Masteliai, stulpeliai ir tarpai skaičiuojami iš geometrijos ir anotacijų.
  - `SC = LE.pick_scale((W, H), (laisvas plotis, laisvas aukštis), annot=...)`
  - `CX, G = LE.distribute(K.IX0, K.IX1, [stulpelių pločiai], margin=(0.5, 1.0))`
  - `LE.report(...)` iškviečiamas PRIEŠ `K.save`.
- FRONT / SIDE / REAR turi vieną bendrą didžiausią telpantį mastelį: pirmiausia ISO 5455, 1:15 / 1:25 tik nurodžius lape.
  Joks vaizdas nedidinamas ir nemažinamas atskirai. `braizyti_begeliai` renkasi TIK n(galas) = n(priekis) (v309; iki tol
  galui leista iki 2,5 x smulkiau - LEAP26-01002 gavosi 1:15 / 1:20); patikra 21 SKIRTINGI MASTELIAI. Antraštėje - vienas
  mastelis („1:20", ne „1:20 / 1:20"); 2 lape - tik tikrai nubraižytų vaizdų masteliai.
- Stulpelio plotis = geometrija + matmenų / pozicijų juostos, bet ne mažiau už pavadinimo ir mastelio eilutę
  (`LE.title_w`). Tarpai vienodi.
- Paraštė prie rėmo: kairėje 0,5 tarpo, DEŠINĖJE 1 tarpas (Rytis v292).
- Vaizdų pavadinimai rašomi vienoje eilėje (YB + 30).
- Papildoma detalė dedama PO kita detale tame pačiame stulpelyje arba savame stulpelyje. Niekada neįspraudžiama tarp vaizdų.
- Detalių zona skaidoma į stulpelius pagal turinį. Mažas elementas (TRAFO BOX) neturi savo stulpelio.
- DETAIL / SECTION mastelis:
  - didžiausias ISO: 1:1, 1:2, 1:5, 1:10;
  - detalė ne aukštesnė nei 0,6 pagrindinių projekcijų (`pick_scale(cap_pt=...)`), kad būtų išlaikyta hierarchija.
- 3D (NOT TO SCALE):
  - vienodas koeficientas visoms ašims;
  - centruojamas pagal matomą kontūrą;
  - užima 85-100 % zonos;
  - aukštam ir siauram gaminiui 3D dedamas dešinėje, tokio pat aukščio kaip projekcijos.
- 3D žymos (SIDE A ir pan.) rašomos šalia objekto, niekada ant jo (taisyklė 27).
- Ilga žema iškaba (pvz. 6712 x 375): `braizyti_begeliai` išdėstymas trimis eilėmis - FRONT + SIDE / REAR / didelis 3D
  per visą plotį (v295, Order 33580); 3D nepaliekamas mažas kampe.
- Užrašai be turinio („Power / PSU / cable exits:") nededami, kai ta informacija jau yra legendoje; grupės LED užrašas
  atskiroms raidėms (be rėmo) - PO grupe galiniame vaizde (v295).

## C. Matmenys, tekstai, pozicijos (TAISYKLĖS 30, 34, `references/cad_matmenavimas_ISO.md`)

- ISO 129-1:
  - linija ant linijos negalima;
  - iškeltinė baigiasi pirmame kontūre;
  - jei >= 3 vienodi intervalai, rašoma `n× v (= L)`;
  - matmuo nedubliuojamas;
  - hierarchija: vietiniai matmenys arčiau, gabaritas toliau.
- Vienetai tik mm (antraštė „ALL DIMENSIONS IN mm"). Prie matmenų „mm" nerašoma.
- Dešimtainis KABLELIS. `K.T()` jį uždeda pats.
- LENTELĖSE (BOM / MAIN DATA / TITLE) kiekviena reikšmė turi vienetą:
  - matmuo „515 x 2380 x 40 mm", „Ø3,2 mm";
  - kiekis „0,93 m", „6,64 m / 0,12 m²", „41 pcs.";
  - matmenų grupę be vieneto `K.cell_units` papildo „mm";
  - dviprasmybę (Ø su x: matmuo ar kiekis?) generatorius rašo aiškiai: „Ø16 x 20 mm", „Ø4 mm: 41 pcs.".
- Lentelės langelio tekstas trumpinamas, kad tilptų (detalės - BOM eilutėje, ne MAIN DATA); patikra 16. Šrifto nemažinti.
  v326: `K.wrap_cell` automatiškai (BOM, MAIN DATA, antraštės langeliai): 1) 3 dalių grupė kompaktiškai „30 x 30 x 2 mm" ->
  „30x30x2 mm", „->" -> „>"; 2) dviem eilutėmis, kol blokas talpina (eilutė >= 11 pt + 9,5 pt kiekvienai papildomai);
  vienetas neatskiriamas nuo skaičiaus, „RAL ___" - kartu. MAIN DATA etikečių stulpelis - ne platesnis nei ilgiausia
  etiketė + 8 pt. Kas vis tiek netelpa - NETELPA LANGELYJE, generatorius trumpina tekstą (pvz. „inside white" - į MAIN DATA).
- PLOTAS VISADA NESTING PRINCIPU (v304, Rytis: „tai taisyklė"). BOM m² = medžiagos sunaudojimas, ne grynasis plotas
  (IŠIMTIS - folded plokštė: BOM QTY = gaminio plotas W x H m², ne nesting, v324 - E3c):
  - lakštai (akrilas, PC, Alu, AKP, PVC) - `scripts/nesting.py`: tikri kontūrai -> mažiausias pasuktas gabaritinis
    stačiakampis, pasukimas 90°, tarpas 10 mm, paraštė 10 mm;
  - dėliojama MaxRects (BSSF ir bottom-left), lakštas abiem kryptimis, visi tiekėjo formatai (`assets/medziagos.json`),
    imamas mažiausias sunaudojimas;
  - sunaudojimas = pilni lakštai + paskutinio lakšto panaudota juosta;
  - KIEKIS (v309, Leapmotor 33577 - 40 / 20 vnt.): dėliojama VISAM užsakymo kiekiui (spec „qty"; `nest_parts(..., qty=)`),
    BOM „per 1 pcs." = viso sunaudojimas / kiekis (ne vienos iškabos lakštas su 70 % atliekų);
  - šonai - juostos perimetras x gylis; juostos dėliojamos ir eilėmis (1D FFD, ilgesnė už eilę - pilnos eilės + likutis),
    imamas mažesnis iš MaxRects / eilių (v309);
  - plėvelė - `plevele.plan` (rulonas 1320 / 1190);
  - `braizyti_begeliai` BOM vietos žymos: `{A_x}` priekiai, `{BACK_x}` dugnai, `{RET_x}` šonai, `{FOIL_x}` plėvelė
    (x = 6 / 63 / ALL / grupė);
  - ranka įrašytas plotas - klaida 18; m² be nesting - patikra 19 PLOTAS NE NESTING;
  - folded plokštės eilutė (gaminio m², v324) - FEAT „folded_qty", patikra 19 jos netaiko; „nest" žymima TIK kai nesting
    tikrai skaičiuotas (po `K.init`, kuris FEAT išvalo) (v327);
  - nežinoma medžiaga nesting'ui (`braizyti_lapa` {A_FACE} / {A_RET} / {A_BACK}) - „?" + lapo klaida, ne grynasis plotas (v327);
  - `plevele.bom_text` - tik rezultatas „1,74 m² (roll 1190 mm)" (v327);
  - v326: BENDRA funkcija naujiems / šviesdėžių generatoriams - `K.nest_m2(geoms, medžiaga, žyma, qty=K.order_qty(spec qty))`
    (nesting + FEAT „nest" + „?" ir lapo klaida, jei medžiaga nežinoma); sviesdeze stiklai A / B, p10 lightbox įdėklai /
    pagrindai - per ją;
  - svoriui naudojamas grynasis plotas.
- BOM kiekyje rašomas tik rezultatas: sunaudojimas su atliekomis. Lakšto matmenų ir formulių „2× ... =" nerašyti.
- Spalvos kodas FINISH / MATERIAL langelyje rašomas su spalva langelyje (RAL / NCS / PMS / plėvelė / plexi).
  NCS ir PMS kodai be „RAL".
- Pozicijų balionai nepersidengia. `K.leader` pats atitraukia balioną, BOM balionai mažinami pagal eilutę.
  Numeriai = galutinės BOM pozicijos.
- Nežinoma reikšmė spec'e / generatoriuje rašoma „?": `K.T()` „?" pašalina - lape tuščias langelis (tekstas su „:" - rašymo
  linija), atsakyme klausimas Ryčiui. Nieko neišgalvoti. (Lape „?" ar „RAL ? matt" nematomas - SKILL 7, stilius.md.)
- Užrašai angliškai, GOST šriftas visur.
- Objektų geometrija vaizduose piešiama hairline (`K.set_view(True)`). Dvigubų linijų būti neturi.

## D. Blokai apatinėje juostoje (TAISYKLĖS 5, 34)

- Kiekvienas pjūvio / profilio / DETAIL blokas yra bloko CENTRE (horizontaliai ir vertikaliai).
  - Naujas blokas: `K.section_block(x, y, w, h, "TITLE", fn)`. fn piešia tik turinį, pastabos dedamos prie turinio.
  - Seno tipo funkcija, kuri pati piešia antraštę ir rėmelį: `K.centered(x, y, w, h, fn, name, frame=True)`.
- Patikra:
  - 12 NECENTRUOTA / NETELPA BLOKE;
  - 13 BLOKAS NECENTRUOJAMAS: juostos antraštė su SECTION / PROFILE / DETAIL nubraižyta ne per šias funkcijas.
- Keli lapai viename PDF jungiami per `K.merge_sheets(pages, out)`, kad išliktų kiekvieno lapo patikros duomenys.
  v326: `fitz insert_pdf` ciklas be sidecar - lint LAPAI BE merge_sheets (sviesdeze / p10 doublesided taip slėpė NETELPA,
  blokus ir nesting žymą nuo patikros).
- Vieno užsakymo kelios iškabos = VIENAS dokumentas `ALT0000_Order_<nr>.pdf` (Rytis v296, Order 33580): kiekviena iškaba -
  savas lapas (spec `"sheet": "1 / 2"`, `"2 / 2"`), sujungta `K.merge_sheets`; 1:1 failai - atskirai kiekvienai iškabai.
  Generatorius su 2 lapais (`braizyti_begeliai` akrilo rėmas / U laikikliai, `p10_lightbox_singlesided`): spec `"sheet": "a / n"`
  = PIRMO lapo numeris, antras - (a+1) / n (v309). Pavyzdys - `projektai/leapmotor_33577/build_order.py` (3 iškabos, 6 lapai).

## D2. Konstrukcija - rėmas (v297)

- RAIDŽIŲ TVIRTINIMAS - KVADRATO / TRIKAMPIO PRINCIPAS (v245, VISIEMS rėmams nuo v317; Rytis 2026-10-16: „kur dingo
  taisyklė raides tvirtinti pagal kvadrato ir trikampio principą?"): D3.2 / smeigių kiekis pagal raidės FORMĄ -
  supaprastinto gaubto kampai (kvadratas / stačiakampis 4: B n d a s m; trikampis 3: A y P V), 2..6, platiems + 1 kas
  500 mm, maža (< 200 mm) - iki 3. Taškai - štrichų, kertančių bėgelio ašį, CENTRE (centerline; išilginiame štriche -
  galuose), parenkami kuo toliau vienas nuo kito; tame pačiame bėgelyje du taškai arčiau nei 0,3 raidės pločio (A viršūnė)
  ar taškas tarp dviejų jau parinktų (P viršus) - nededamas. Kiekviena raidė >= 2. `p6_dxf.py` numatyta (senas
  prispaudimo R būdas - tik `--press-fill`, lint TVIRTINIMAS NE PAGAL FORMĄ); akrilo rėmas - `braizyti_begeliai._acr_studs`.
  Bandymas: `scripts/projektai/bandymas_3500/` (Bandymas L 3500, P6 ant U 30x30x2: B n d a s m - 4, y - 3).
- KIEKVIENA raidės / elemento dalis (atskiras kontūras: E brūkšnelis, taškas, akcentas, kablelis) privalo liesti rėmą.
  Dalis be rėmo: `braizyti_begeliai` automatiškai deda statmenį per jos vidurį tarp artimiausių bėgelių. Jei bėgelis yra
  tik iš vienos pusės, statmuo daromas T forma (v193).
- Neišsprendus: patikra 18 KONSTRUKCIJA / KABO ORE (`K.SHEET_ERR`).
- BOM sienos rėmo (wall L) ilgis = tik horizontalūs (`{RAIL_H_M}`). Raidžių rėmas - su statmenimis.
- Jei rėme yra statmenys, jų turi būti BENT 2 (v298). Du ilgi bėgeliai su vienu statmeniu nėra stabilūs.
  Antras statmuo dedamas po KRAŠTINE (toliausia nuo pirmojo) raide. Toje raidėje jis statomas ten, kur raidė jį uždengia
  daugiausia, kad statmuo kuo mažiau matytųsi (v299, EXLANTIX - po X). Jei raidės nėra - patikra 18.
- GALINIS statmuo - po KRAŠTINE pilno aukščio raide abiejuose galuose (v311, Rytis 2026-10-16 LEAP26-01002: „papildoma
  statmena po R raide gale"). Raidė be stiebo / kojelės (R, P šiame šrifte) - statmuo ten, kur ji jį dengia daugiausia (>= 50 %);
  ankstesnis kraštinis (pvz. po T) lieka tarpiniu. `auto_remas.single_verticals`.
- Pailga dalis be rėmo (E brūkšnelis, plotis >= 2 x aukštis) gauna HORIZONTALŲ bėgelį savo ašyje. Galai - pagal rėmo
  tvirtinimo taisyklę: kraštinio štricho VIDURYJE (kraštas + pusė štricho), abu kampai >= 10 mm dalies viduje (v300)
  plius statmenį iki rėmo. Taip dalis turi >= 2 tvirtinimo taškus ir D11 laido išvestį bėgelio ašyje (v299).
  Šio bėgelio matmuo dedamas virš jo, ne išvadine.
- L profilių sistema (l_hang): sienos rėmas (wall L) galiniame vaizde rodomas PUNKTYRU, su savo matmeniu ir pozicija.
  Ilgis = atstumas tarp kraštinių rėmo statmenų ašių - 2 x 50 mm (v300; be statmenų - bėgelio ilgis - 2 x 50).
  BOM kiekis - `{WALL_L_M}`.
- AKRILINIS rėmas (v311, LEAP26-01002 / 06002):
  - Ø8 fasado tvirtinimai - tarpuose tarp SIMBOLIŲ (logotipas iš kelių dalių = vienas simbolis), kas antras tarpas NUO
    KRAŠTŲ, abu kraštiniai tarpai visada (LEAP: R/O, T/O, M/P, A/E, L/LOGO); spec `"holes_gaps"` - tikslūs tarpai;
  - laido griovelis ir laidų skylės kiaurai - TIK APATINIAME bėgelyje (spec `"groove_rails": "all"` - visur, kaip iki v311);
  - kiekviena raidės dalis >= 2 smeigės (v244) - kitaip patikra 18; vientisas bėgelis nuo spec `"single_w"` platinamas
    kas 5 mm, kol visos dalys gauna po 2 (LEAP26-06002: prašyta 50, smeigės kraštas 5 mm -> 65 mm, Rytis pasirinko).
- Spalvos: visa RAL Classic paletė (213 spalvų) yra `assets/ral_classic.json` (v298). Nežinomas RAL kodas nebėra tyli
  pilka spalva, o patikros 18 klaida. Naujas kodas įrašomas į paletę.

## D4. LED dėliojimas (v329, Rytis 2026-10-17: „A raidėje vienoje kojelėje 3 LED, o kitoje jau 4, ir nėra brūkšnelyje tarp kojelių")

- Įrankis - `scripts/led_km.py` (Kaisen; LED PDF - atskiras dokumentas). NUMATYTAS išdėstymas `strokes` (ne `ilp`):
  - raidės ašis -> LINIJOS: sankirtoje šakos jungiamos pagal tiesiausią tąsą (A koja per brūkšnį - viena linija);
    aštrus kampas (A / M / W viršūnė) - modulis kampe, kampo taškas - kojų tiesių sankirtoje (plokščia viršūnė - per vidurį);
  - kiekviena linija dalijama TOLYGIAI (laisvas galas - p/2 nuo krašto, T galas - pusė tarpo): vienodos linijos -> vienodas
    kiekis (simetrija); kiekviena linija >= 0,3 p gauna >= 1 LED (A / H brūkšnys niekada be LED);
  - serifai / užraitai (trumpa ir plona laisva atšaka) - be LED; trumpa STORA atšaka (t skersinio kairė) - su LED, nebent jos
    tąsa irgi trumpa atšaka (i / m pėdų pora); žiedai - lyginis n, simetriška fazė; > 2 p plotis - tinklelis;
  - PADENGIMAS (v329b, Rytis „Testavimas": „a raidėje trūksta 1 LED, t viršuje kairėje neįdėtas"): raidės plote
    nepadengta dėmė (> 0,12 p², toliau nei 0,55 p nuo LED - a galvutė, uodega) gauna LED ten, kur jis padengia daugiausia
    (>= 0,5 p nuo kitų, pasuktas pagal formą). Parametrai `LED_GAP_R`, `LED_GAP_A` (led_km.py).
- `ilp` (aprėpties minimumas) - tik spec `"layout": "ilp"`.
- Regresija: `scripts/test_led.py` (projektai/led_test), įtraukta į `regresija.py`.

## D3. Maitinimas (v302)

- Jei naudojamas TRAFO BOX, punktyrinė laidų linija galiniame vaizde visada nueina iki TRAFO BOX, o pati dėžė yra
  nubraižyta. Tai galioja ir atskiroms raidėms be rėmo (vienos linijos išvestys).
- Ant dėžės užrašas: „TRAFO BOX", PWM (jei nurodyta) ir spalva iš BOM. Prie dėžės dedama pozicija ir 230V.

## E. Produktų / klientų taisyklės

- Produkto šeimos taisyklės: `references/moduliai_*.md`.
- Klientų taisyklės: `references/klientai/*.md`. Pvz. Clas Ohlson vertikali plokštė: Ø11 kairėje šoninėje briaunoje PAČIAME
  VIRŠUJE, 50 mm nuo viršaus.
- Etalonai: `assets/etalonai/`.
- Konfliktas sprendžiamas taip: kliento taisyklė > produkto taisyklė > bendra; naujesnė vNNN > senesnė.
- Logotipas, kurio raidės kliento faile SULIETOS į vieną kontūrą, P6 raidėms gaminamas IŠ KELIŲ DALIŲ (v314, Rytis 2026-10-16,
  BN PO 3311 Kvickly, pavyzdys ALT7782 „Sign from 3 pieces"): pjūviai - raidžių kraštų tęsiniais ten, kur raidės susiliečia
  (ne bet kur), atskiri kontūrai (i taškas) - atskiros dalys; dalys -> vektorinis šaltinis (kreivės lankais) -> braizyti_begeliai.
  Analogas: `scripts/projektai/bnskilte_3311_kvickly/pieces.py`.
  - DALYS PARODOMOS lape (v315, Rytis: „nėra atvaizduota, kad raidės į vientisą reklamą susideda iš 3 dalių"): spec
    `"pieces_view"` - priekyje sandūros J1.. (raudona brūkšninė hairline, pratęsta už kontūro), žymos PART 1..n, 3D
    „SIGN FROM n PIECES" su atitrauktomis dalimis. Generatorius pats aptinka besiliečiančias dalis - be `pieces_view` patikra 18.
  - TVIRTINIMO TAŠKAI KIEKVIENAI RAIDEI (v315, „interpretuojant raides kaip atskiras"): spec `"fix_split_x"` - raidžių ribos
    dalyse (mm nuo kairės); kiekviena raidė >= 2 taškai; smulkios dalys (i taškas) neskaidomos. Be jo (dalys + mounting none)
    - patikra 18.

## E2. Patvirtinimas -> gamybos paketas (`references/patvirtinimas.md`)

- Siunčiama TIK: maketo PDF (ORDER NO. = ALT), LED PDF (jei šviečia), VIENTISI (visos iškabos) DXF - po vieną kiekvienam
  lapui / plokštei; failų po raidę / dalį, laido variantų poros, ZIP, patikros PNG - NESIUNČIAMA.
- P6 / raidės: `p6_dxf.py --no-letters --rails-json --cable bottom|top` (v326: be `--cable` numatyta `both` = 2 failai). Folded plate + lipdukai: `folded_vinyl.py` + `scripts/dxf_combine.py`
  (v299) - atskiri `_flat_` / `_vinyl_` failai NESIUNČIAMI.
- v316 (Rytis 2026-10-16, SPAR 225960: „blankas naudojamas senas. net jei įkeliamas dokumentas generuotas ankstesne data,
  visi pataisymai daromi jau pagal dabartines taisykles ... naudoti pačią naujausią skill ir taisyklių redakciją"):
  PATVIRTINTAS DOKUMENTAS - TIK DUOMENŲ ŠALTINIS (BOM, MAIN DATA, užrašai, matmenys, raidės, rėmas, ausėlės, grafika).
  VISI lapai VISADA generuojami iš naujo DABARTINIAIS generatoriais, blanku (K.frame, v248 antraštė) ir taisyklėmis
  (nesting m², vienetai, kablelis, bendras mastelis, hairline, ausėlių / jungčių žingsnis ...), net jei dokumentas senas
  ar taisytas Corel'yje. ORDER NO. keitimas esamame PDF (v308 / v310 `order_no.py`) - NEBENAUDOJAMAS gamybos paketui.
  DXF / LED - iš NAUJŲ lapų išvesties (`rails_bb` json, folded_vinyl išklotinės), ne iš patvirtinto lapo rėmo.
  Ataskaitoje - skirtumų sąrašas (kas pasikeitė dėl naujesnių taisyklių) ir klausimai. Pavyzdys:
  `scripts/projektai/spar_225960/alt8901/` (lapai.py, kiti_lapai.py, rinkinys.py, dxf_rinkinys.py, led_visi.py).
- Seni generatoriai su savo blanku (pvz. `braizyti_lapa.py` - buvo 20 / 10 mm paraštės) taisomi PAČIAME generatoriuje
  (v316: K.frame, K.centered pjūvis, nesting, bendras mastelis), ne projekto skripte.
- Teksto keitimas ESAMAME PDF (ORDER NO. ir pan.) - TIK originalo šriftu: glifų ID iš jo ToUnicode, keičiami turinio srauto
  baitai, failas per qpdf (`alt8901/order_no.py`). pymupdf `insert_text` / TextWriter ir pymupdf `save` galutiniam failui
  NENAUDOTI - įterpia antrą Type0 šriftą, Corel „file corrupted" (v310, Rytis 2026-10-16).

## E3. DXF failai (v302, Rytis 2026-10-16: „failai ne pagal mastelį, įkelti reikia 1:1000")

- P6 ANT RĖMO - DRENAŽAS PUSLANKIU (v318, Rytis 2026-10-16: „drenažo išėmimas daromas kaip linijos puslankis, taupant
  pjovimo laiką, nes skylutė - atskira opcija, o čia išpjaunama pjovimo metu. Ant folded plate lieka kaip yra - skylutės"):
  Ø8 puslankis DUGNO KONTŪRE (2_GALAS) žemiausioje vietoje - centras kontūre, išpjova į raidės vidų, vienas uždaras kontūras
  su dugnu (ne atskiras apskritimas). `p6_dxf.py` numatyta; sena skylutė - tik `--drain-hole`. patikra_dxf DRENAŽAS SKYLUTE.
  Folded plate (folded_vinyl) - skylutės lieka. Etalonas: `assets/etalonai/drenazas_puslankis_P6.pdf`.
- P6 ANT FOLDED FONO (v319, Rytis 2026-10-16 „duok testą kaip ant folded plate P6"): `p6_dxf.py --folded` - be rėmo
  (ašys separate), D3.2 kvadrato / trikampio principu, drenažas - Ø8 SKYLUTĖ (ne puslankis); fono išklotinėje
  tos pačios skylės raidžių vietose (LETTER_FIX_D3.2 / HOLE_D11_CABLE / DRAIN_D8) + LETTER_POSITION. v326 patikslinta:
  `folded_dxf.py` pats šių sluoksnių NEDEDA (tik išklotinė, Ø3.2 L tvirtinimui, Ø11 briaunoje su `--cable-edge`); raidžių
  dugno kontūrus ir skyles iš `p6_dxf --folded` DXF į išklotinę perkelia `scripts/projektai/bandymas_3500_folded/folded_test.py`
  (analogas naujam užsakymui).
  braizyti_lapa išklotinė = (W + 2·(atlankas - t)) x (H + 2·(atlankas - t)) (buvo + 2·raidžių gylis). Testas
  `scripts/projektai/bandymas_3500_folded/`.
- Visi gamybos DXF - geometrija mm IR antraštė `$INSUNITS = 4` (mm). Po `ezdxf.new()` VISADA `doc.units = ezdxf.units.MM`
  (ezdxf numatyta - metrai, Corel importuoja x1000).
- Prieš siunčiant: `python3 scripts/patikra_dxf.py <failai>.dxf` = 0 (`dxf_combine.py` tikrina pats).

## E3b. Kreivės - LANKAIS, ne laužtėmis (v312, Rytis 2026-10-16 Leapmotor: „daug taškų, tarp kurių tiesios linijos, nors
failas apvalus, bet gaunasi kampuotas"; ta pati pastaba buvo v113, bet pataisa buvo tik p6_dxf.py)

- Viena vieta - `scripts/kreives.py`. Kliento Bezier skaidomas ADAPTYVIAI (`flat_sub` / `bez_flat`, sagitta <= 0,01 mm),
  ne 8 / 10 / 12 atkarpų kreivei (`K.shape_geom`, `K.split_letters`, `K.perim`, lightbox logotipas).
- DXF išsaugomas TIK per `KR.saveas(doc, path)`: visi LWPOLYLINE -> tiesės + lankai (bulge), nuokrypis <= 0,02 mm
  (didesnis nuo stygos - tik tolygiai išskaidytame lanke); tikri kampai (posūkis > 20°) lieka kampais. Senas DXF -
  `python3 scripts/kreives_fit.py failas.dxf`.
- PDF: `K.path_of` / `K.poly` / `K.ring_path` / `View3D` / `p6_vaizdas.draw_geom` / `PD2.draw_geom` - lygios laužtės braižomos
  lankais (Bezier); 1:1 PDF dugnas / rėmas - `K.fitz_subs(K.geom_subs(geo))`; 3D (iliustracinis) - geometrija
  supaprastinama iki ~0,25 pt lape (`r3d.view_simplify`), gamybos geometrija nekeičiama.
- Patikra: `patikra_dxf.py` KAMPUOTA KREIVĖ - laužtė su >= 6 iš eilės trumpomis atkarpomis ir mažais posūkiais, be lankų;
  `patikra_lapas.py` 23 KAMPUOTA KREIVĖ - lape kontūras iš >= 12 tokių atkarpų + to paties vardo DXF šalia lapo (v313);
  lint DXF BE LANKŲ - `.saveas(` ne per `KR.saveas` (v313). LED lapai (`led_km.py`), r3d 3D plokštumos - taip pat lankais.
  LEAP 33577: DXF mazgai 4107 -> 212 / 10542 -> 622, lapas 1: 31 394 atkarpos -> 2 025 + 1 422 kreivės.
- v326: rastrinis logotipas (`vektorius.rings` -> `vektorius.draw_rl`, sviesdeze / p10 lightbox) braižomas per
  `KR.ring_to_sub` - lankais, ne potrace laužte (anksčiau 1252 atkarpų kontūras, patikra 23 to nematė, nes lapai jungti be sidecar).

## E3c. Folded plokštės BOM kiekis - m² (v323, Rytis 2026-10-16: „folded plate QTY pažymėta kaip 1 pcs, o turi būti plate m2")

- Folded plokštės (fono, back plate) BOM QTY - TIK GAMINIO PLOTAS W x H (v324, Rytis: „turi būti rašoma tik gaminio plotas,
  jeigu plate 3,9 x 1 m - rašoma 3,9 m2"): 3900 x 1000 -> „3,90 m²". NE išklotinė, NE lakšto sunaudojimas (nesting išimtis),
  NE „1 pcs." (`nesting.folded_qty`).
- Kelios dalys - „A1 - 3,78 m², A2 - 1,89 m²" (dalys A1, A2 ... iš viršaus; tie patys vardai lape - šoniniame vaizde
  ir MAIN DATA „Parts": „A1 2700 x 1400 + A2 2700 x 700").
- Vykdo `folded_vinyl.py` ir `braizyti_lapa.py` (eilutė su „folded" ir kiekiu „N pcs." -> m²). Patikra 26 FOLDED BE m².
- Šviesdėžių LOVELĖS (front / back tray, folded A / B) - taip pat TIK FASADO m² (v328, Rytis: „tik fasado m2"):
  `p10_lightbox_singlesided`, `p10_lightbox_doublesided`; patikra 26 tikrina ir „tray", ir „pc." / „pcs.".
- SPAUDA (v328, Rytis: „spauda dokumente tik nurodoma, gamyboje kitas spaudos algoritmas"): BOM spaudos eilutė - tik kas
  ir iš kokio failo, kiekis „per production", m² NESKAIČIUOJAMAS. Patikra 29 SPAUDA SU PLOTU.
- LAIDAS (v328, Rytis: „laidas, jei nenurodyta užklausoje, 1.5 m"): numatytas 12V / 230V laido ilgis - 1,5 m
  (`braizyti_begeliai` trafo_box.cable_len_m); kitas - tik jei nurodyta užklausoje (pvz. SPAR 225960 - 3 m).

## E4. Folded lenkimas - TRUMPOSIOS KRAŠTINĖS Į VIDŲ (v328, Rytis 2026-10-16: „pagal nutylėjimą trumposios kraštinės lenkiasi į vidų, kitas variantas nurodomas, jei ne standartas")

- Į vidų (tarp kitų atlankų, iš galų t trumpesni) lenkiami TRUMPŲJŲ kraštinių atlankai: W >= H - šonai (sides inside,
  viršus / apačia užsilenkia ant jų); H > W - viršus / apačia (W - 2t), šonai per visą aukštį.
- Vienodai visur: `folded_dxf.py` (fonas, P6 ant folded - `p6_folded.py`, lovelės), `folded_vinyl.py` (plokštė + lipdukai).
- Ne standartas - TIK nurodžius užsakyme: `folded_dxf.py --tb-inside` / `--sides-inside`, spec `"tb_inside": true / false`
  (pvz. Joker 226057 v302 „viršus / apačia į vidų" - jo spec'e; SPAR 225960 bp7 / bp89 - spec'e).
- DXF TEXT sluoksnyje - užrašas „TOP / BOTTOM INSIDE" arba „SIDES INSIDE".

## E5. Įdėta kliento / seno lapo grafika - faile TIK lape matomi objektai (v307, Rytis 2026-10-16 KIA 33597)

- „dokumente daug pašalinių objektų, faile tik lape esantys objektai": CorelDRAW atidaro VISUS PDF objektus, ir tuos,
  kurie paslėpti už iškarpos (clip) ar už lapo ribų.
- Fragmentai įdedami TIK per `K.place_pdf` - jis per `K.clip_source(src, pno, clip)` iš šaltinio puslapio kopijos ištrina
  viską, kas nesikerta su iškarpa (vektoriai, tekstas, paveikslėliai), tada įdeda. Tiesiai `show_pdf_page(..., clip=)` -
  ne (lint VISAS ŠALTINIO PUSLAPIS); jei būtina - `show_pdf_page(r, K.clip_source(src, pno, clip), 0, clip=...)`.
- Seno turinio likučiai iškarpos viduje (senas frontas, matmenys) IŠTRINAMI redakcija
  (`add_redact_annot` + `apply_redactions(graphics=PDF_REDACT_LINE_ART_REMOVE_IF_TOUCHED)`), NE uždengiami baltu
  stačiakampiu (lint BALTAS DANGTIS).
- `K.save` - `garbage=4` (pasikartojantys ICC / šriftai vieną kartą; KIA 5,6 -> 1,5 MB).
- GOST VISUR (v328, Rytis 2026-10-16: „visi įkelti pavyzdžiai ir dokumentai keičiami į GOST šriftą. GOST šriftas
  pagrindinis galutiniame dokumente"): `K.place_pdf(..., gost=True)` (numatyta) - visas fragmento gyvas tekstas (bet koks
  šriftas, ir seno lapo GOST kopija) iš fragmento pašalinamas ir perrašomas lapo GOST šriftu toje pačioje vietoje
  (dydis, spalva, kryptis); fragmentas be teksto - be šriftų resursų. Lape - VIENAS GOST šriftas (patikra 22 COREL).
  `gost=False` - tik kliento logotipo dizaino tekstui, su `# lint-ok: priežastis` (lint ĮDĖTAS TEKSTAS NE GOST).
  Išimtis - simboliai, kurių GOST Common neturi (Å / Æ / Ø / Ä / Ö) - osifont (v11 / v146).
- LED PDF (`led_km.py`) - atskiras dokumentas: modulio / PSU modeliai ir užrašai jame lieka (v328, Rytis: v262 „tik LED / PSU"
  LED PDF NETAIKOMA).

## F. Ką tikrina automatika (lapas neatiduodamas, kol ne 0)

`patikra_lapas.py`:
1. HAIRLINE.
2. TEKSTAS ANT TEKSTO.
3. LINIJA PER TEKSTĄ.
4. MATMENYS VIENAS ANT KITO.
5. IŠVADINĖ KERTA.
6. LINIJA ANT LINIJOS.
7. MATMENYS KERTASI.
8. RODYKLĖS PERSIDENGIA.
9. BALIONAI PERSIDENGIA.
10. DEŠIMTAINIS TAŠKAS.
11. VIENETAS NENURODYTAS (BOM POS balione „1.1" - pozicijos numeris, ne kiekis; v326).
12. NECENTRUOTA / NETELPA BLOKE.
13. BLOKAS NECENTRUOJAMAS.
14. SENA TAISYKLĖ (generatoriaus lint: fiksuotos vietos / mastelis projekto skripte, projekto lapas be `layout_engine`,
    BOM formulės, blokas be centravimo).
15. SUVESTINĖ PASENUSI.
16. NETELPA LANGELYJE (v294): tekstas netelpa lentelės langelyje; trumpinti tekstą, šrifto nemažinti.
17. VIENETAS NENURODYTAS - ir lentelėje skaičius su kableliu be vieneto („10,00" -> „10,00 m"), v296.
18. KONSTRUKCIJA (KABO ORE ir kt. - generatoriaus aptiktos klaidos), v297.
19. PLOTAS NE NESTING (v304).
20. PAŠALINIAI OBJEKTAI (v307): objektai paslėpti už iškarpos arba už lapo ribų (įdėtas visas šaltinio puslapis).
    Lint: VISAS ŠALTINIO PUSLAPIS, BALTAS DANGTIS.
21. SKIRTINGI MASTELIAI (v309): FRONT / SIDE / REAR lape skirtingais masteliais.
22. COREL (v310): lape daugiau nei vienas GOST šriftas, „GOST-Common" vardas arba qpdf --check klaida - CorelDRAW
    „file corrupted" (`scripts/patikra_corel.py`, kviečiama iš patikra_lapas.py).
23. KAMPUOTA KREIVĖ (v313): lape - kontūras iš trumpų tiesių ten, kur turi būti lankas; šalia lapo esantys to paties
    vardo DXF - laužtės be lankų (patikra_dxf). Lint: DXF BE LANKŲ.
24. UŽ RĖMELIO (v316): užrašas (ne zonų žymė) išeina už vidinio rėmelio.
25. DRENAŽAS SKYLUTE (v318) - TAI `patikra_dxf.py` punktas, ne lapo PDF tikrinimas: P6 dugne (2_GALAS) Ø8 apskritimai vietoj
    puslankio kontūre. patikra_lapas.py jį parodo tik per šalia lapo esančius to paties vardo DXF (kaip 23).
26. FOLDED BE m² (v323): folded plokštės BOM kiekis „N pcs." vietoj gaminio ploto m² (A1 - m², A2 - m²; v324 - W x H).
27. BALIONAS UŽDENGTAS (v325, Rytis 2026-10-16: „reikia taisyklės, kad vengtų tokių persidengimų, nes dabar vienas ant kito,
    neinformatyvu"): į baliono apskritimą nepatenka svetimas tekstas (matmens skaičius), matmens rodyklė ar antras užrašas.
    Generatoriuje: balionai dedami PRIEŠINGOJE pusėje nei laido išvestis / jos matmuo (braizyti_lapa galinis vaizdas).
    v326: P1 pjūvio (K.p1_typical) šono balionas 2 - raidės viduje, ne ant gylio matmens.
28. ANTRAŠTĖS MASTELIS (v327): antraštės SCALE langelyje - tik masteliai, kurie yra lapo vaizduose / blokuose (p10 doublesided
    rašė numatytus „1:5 / 1:2 / 1:1"); sviesdeze.band `scales` - privalomas. Vienas bendras mastelis - vienas įrašas.
29. SPAUDA SU PLOTU (v328): BOM spaudos eilutėje m² - spauda tik nurodoma („per production").
- (be numerio) DVIGUBA LINIJA (v190, SKILL bendrinė 9): du įdėti hairline kontūrai arčiau nei 0,6 pt - spaudoje susilieja į
  storą liniją (tikrinama kartu su 1 HAIRLINE).

`taisykliu_lint.py` (generatoriaus kodas): FIKSUOTA VIETA, FIKSUOTAS MASTELIS, KIEKIS SU FORMULE, BLOKAS BE CENTRAVIMO,
VISAS ŠALTINIO PUSLAPIS, DXF BE LANKŲ, TVIRTINIMAS NE PAGAL FORMĄ, LAPAI BE merge_sheets (v326), ĮDĖTAS TEKSTAS NE GOST (v328), BALTAS DANGTIS, BE LAYOUT_ENGINE.

`regresija.py` (v326): visi `CASES` - patikra_lapas / patikra_corel / patikra_dxf = 0 ir test_p6 OK.

Ko automatika NEtikrina (tikrinama akimis kiekvieną kartą):
- ar vaizdai proporcingi ir subalansuoti;
- ar duomenys atitinka kliento užsakymą (pvz. formatas 2000x1062 ir išmatuota 1063 - klausti);
- ar laidų / tvirtinimo logika atitinka kliento taisykles.
