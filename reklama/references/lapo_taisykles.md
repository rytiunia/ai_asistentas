# GALIOJANČIOS LAPO TAISYKLĖS + NAUDOJIMO LOGIKA (suvestinė)

Atnaujinta: v306 (2026-10-16)

Rytis 2026-10-16: „išsaugok taisykles ir naudojimo logiką ir padaryk, kad kitą kartą vėl nebūtų daroma su senomis
taisyklėmis ir nustatymais".

Šis failas yra VIENA vieta, kur surašyta, kaip DABAR daromas bet kuris A3 techninis lapas. SKILL.md numeruotos taisyklės
yra istorija su priežastimis. Kur jos prieštarauja šiam failui, galioja naujesnė vNNN (taisyklė 0b), o šis failas
atnaujinamas tame pačiame commit'e.

`patikra_lapas.py` tikrina, kad šio failo „Atnaujinta: vNNN" nebūtų senesnė už SKILL „Versija". Jei senesnė, išmeta klaidą
SUVESTINĖ PASENUSI.

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
   - Patikra kartu paleidžia `taisykliu_lint.py` lapo generatoriui (kelias imamas iš `<lapas>.pdf.art.json`).
   - Paskui lapas peržiūrimas AKIMIS: PNG, visas lapas ir priartinti blokai.
6. Ryčio pataisa = nauja taisyklė. TAME PAČIAME commit'e:
   - (a) SKILL.md įrašas su priežastimi;
   - (b) ŠIS failas (B-D dalis + „Atnaujinta");
   - (c) vykdymas `lapas_core` / generatoriuje;
   - (d) patikros punktas `patikra_lapas.py` arba lint taisyklė `taisykliu_lint.py`;
   - (e) pergeneruoti tos dienos / atviro užsakymo lapai, kad patikra = 0.

   Versiją kelti `python3 scripts/versija.py "aprašas"`: pakelia SKILL ir šio failo versiją kartu.
7. Atsakyme nurodyti „reklama vNNN, GitHub <hash>". Lapas siunčiamas tik su patikra = 0.

## B. Lapo išdėstymas (TAISYKLĖ 33, `references/adaptive_layout.md`)

- Fiksuotų koordinačių nėra. Masteliai, stulpeliai ir tarpai skaičiuojami iš geometrijos ir anotacijų.
  - `SC = LE.pick_scale((W, H), (laisvas plotis, laisvas aukštis), annot=...)`
  - `CX, G = LE.distribute(K.IX0, K.IX1, [stulpelių pločiai], margin=(0.5, 1.0))`
  - `LE.report(...)` iškviečiamas PRIEŠ `K.save`.
- FRONT / SIDE / REAR turi vieną bendrą didžiausią telpantį mastelį: pirmiausia ISO 5455, 1:15 / 1:25 tik nurodžius lape.
  Joks vaizdas nedidinamas ir nemažinamas atskirai.
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
- Lentelės langelio tekstas trumpinamas, kad tilptų (detalės - BOM eilutėje, ne MAIN DATA); patikra 16.
- PLOTAS VISADA NESTING PRINCIPU (v304, Rytis: „tai taisyklė"). BOM m² = medžiagos sunaudojimas, ne grynasis plotas:
  - lakštai (akrilas, PC, Alu, AKP, PVC) - `scripts/nesting.py`: tikri kontūrai -> mažiausias pasuktas gabaritinis
    stačiakampis, pasukimas 90°, tarpas 10 mm, paraštė 10 mm;
  - dėliojama MaxRects (BSSF ir bottom-left), lakštas abiem kryptimis, visi tiekėjo formatai (`assets/medziagos.json`),
    imamas mažiausias sunaudojimas;
  - sunaudojimas = pilni lakštai + paskutinio lakšto panaudota juosta;
  - šonai - juostos perimetras x gylis;
  - plėvelė - `plevele.plan` (rulonas 1320 / 1190);
  - `braizyti_begeliai` BOM vietos žymos: `{A_x}` priekiai, `{BACK_x}` dugnai, `{RET_x}` šonai, `{FOIL_x}` plėvelė
    (x = 6 / 63 / ALL / grupė);
  - ranka įrašytas plotas - klaida 18; m² be nesting - patikra 19 PLOTAS NE NESTING;
  - svoriui naudojamas grynasis plotas.
- BOM kiekyje rašomas tik rezultatas: sunaudojimas su atliekomis. Lakšto matmenų ir formulių „2× ... =" nerašyti.
- Spalvos kodas FINISH / MATERIAL langelyje rašomas su spalva langelyje (RAL / NCS / PMS / plėvelė / plexi).
  NCS ir PMS kodai be „RAL".
- Pozicijų balionai nepersidengia. `K.leader` pats atitraukia balioną, BOM balionai mažinami pagal eilutę.
  Numeriai = galutinės BOM pozicijos.
- Nežinoma reikšmė rašoma „?": tuščias langelis ir klausimas Ryčiui. Nieko neišgalvoti.
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
- Vieno užsakymo kelios iškabos = VIENAS dokumentas `ALT0000_Order_<nr>.pdf` (Rytis v296, Order 33580): kiekviena iškaba -
  savas lapas (spec `"sheet": "1 / 2"`, `"2 / 2"`), sujungta `K.merge_sheets`; 1:1 failai - atskirai kiekvienai iškabai.

## D2. Konstrukcija - rėmas (v297)

- KIEKVIENA raidės / elemento dalis (atskiras kontūras: E brūkšnelis, taškas, akcentas, kablelis) privalo liesti rėmą.
  Dalis be rėmo: `braizyti_begeliai` automatiškai deda statmenį per jos vidurį tarp artimiausių bėgelių. Jei bėgelis yra
  tik iš vienos pusės, statmuo daromas T forma (v193).
- Neišsprendus: patikra 18 KONSTRUKCIJA / KABO ORE (`K.SHEET_ERR`).
- BOM sienos rėmo (wall L) ilgis = tik horizontalūs (`{RAIL_H_M}`). Raidžių rėmas - su statmenimis.
- Jei rėme yra statmenys, jų turi būti BENT 2 (v298). Du ilgi bėgeliai su vienu statmeniu nėra stabilūs.
  Antras statmuo dedamas po KRAŠTINE (toliausia nuo pirmojo) raide. Toje raidėje jis statomas ten, kur raidė jį uždengia
  daugiausia, kad statmuo kuo mažiau matytųsi (v299, EXLANTIX - po X). Jei raidės nėra - patikra 18.
- Pailga dalis be rėmo (E brūkšnelis, plotis >= 2 x aukštis) gauna HORIZONTALŲ bėgelį savo ašyje. Galai - pagal rėmo
  tvirtinimo taisyklę: kraštinio štricho VIDURYJE (kraštas + pusė štricho), abu kampai >= 10 mm dalies viduje (v300)
  plius statmenį iki rėmo. Taip dalis turi >= 2 tvirtinimo taškus ir D11 laido išvestį bėgelio ašyje (v299).
  Šio bėgelio matmuo dedamas virš jo, ne išvadine.
- L profilių sistema (l_hang): sienos rėmas (wall L) galiniame vaizde rodomas PUNKTYRU, su savo matmeniu ir pozicija.
  Ilgis = atstumas tarp kraštinių rėmo statmenų ašių - 2 x 50 mm (v300; be statmenų - bėgelio ilgis - 2 x 50).
  BOM kiekis - `{WALL_L_M}`.
- Spalvos: visa RAL Classic paletė (213 spalvų) yra `assets/ral_classic.json` (v298). Nežinomas RAL kodas nebėra tyli
  pilka spalva, o patikros 18 klaida. Naujas kodas įrašomas į paletę.

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

## E2. Patvirtinimas -> gamybos paketas (`references/patvirtinimas.md`)

- Siunčiama TIK: maketo PDF (ORDER NO. = ALT), LED PDF (jei šviečia), VIENTISI DXF po vieną kiekvienam lapui / plokštei.
- P6 / raidės: `p6_dxf.py --no-letters --rails-json`. Folded plate + lipdukai: `folded_vinyl.py` + `scripts/dxf_combine.py`
  (v299) - atskiri `_flat_` / `_vinyl_` failai NESIUNČIAMI.

## E3. DXF failai (v302, Rytis 2026-10-16: „failai ne pagal mastelį, įkelti reikia 1:1000")

- Visi gamybos DXF - geometrija mm IR antraštė `$INSUNITS = 4` (mm). Po `ezdxf.new()` VISADA `doc.units = ezdxf.units.MM`
  (ezdxf numatyta - metrai, Corel importuoja x1000).
- Prieš siunčiant: `python3 scripts/patikra_dxf.py <failai>.dxf` = 0 (`dxf_combine.py` tikrina pats).

## E4. Folded plate + lipdukai - lenkimas (v302, Rytis 2026-10-16 Joker 226057)

- `folded_vinyl.py` išklotinė: VIRŠUS / APAČIA LENKIASI Į VIDŲ (tarp šonų) - jų atlankai iš galų t trumpesni (W - 2t),
  šonai per visą aukštį; spec `"tb_inside": false` - šonai į vidų. DXF TEXT sluoksnyje užrašas „TOP / BOTTOM INSIDE".

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
11. VIENETAS NENURODYTAS.
12. NECENTRUOTA / NETELPA BLOKE.
13. BLOKAS NECENTRUOJAMAS.
14. SENA TAISYKLĖ (generatoriaus lint: fiksuotos vietos / mastelis projekto skripte, projekto lapas be `layout_engine`,
    BOM formulės, blokas be centravimo).
15. SUVESTINĖ PASENUSI.
17. VIENETAS NENURODYTAS - ir lentelėje skaičius su kableliu be vieneto („10,00" -> „10,00 m"), v296.
18. KONSTRUKCIJA (KABO ORE ir kt. - generatoriaus aptiktos klaidos), v297.
19. PLOTAS NE NESTING (v304).
16. NETELPA LANGELYJE (v294): tekstas netelpa lentelės langelyje; trumpinti tekstą, šrifto nemažinti.

Ko automatika NEtikrina (tikrinama akimis kiekvieną kartą):
- ar vaizdai proporcingi ir subalansuoti;
- ar duomenys atitinka kliento užsakymą (pvz. formatas 2000x1062 ir išmatuota 1063 - klausti);
- ar laidų / tvirtinimo logika atitinka kliento taisykles.
