# GALIOJANČIOS LAPO TAISYKLĖS + NAUDOJIMO LOGIKA (suvestinė)

Atnaujinta: v297 (2026-10-16)

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
5. `python3 scripts/patikra_lapas.py lapas.pdf` turi duoti 0.
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

## E. Produktų / klientų taisyklės

- Produkto šeimos taisyklės: `references/moduliai_*.md`.
- Klientų taisyklės: `references/klientai/*.md`. Pvz. Clas Ohlson vertikali plokštė: Ø11 kairėje šoninėje briaunoje PAČIAME
  VIRŠUJE, 50 mm nuo viršaus.
- Etalonai: `assets/etalonai/`.
- Konfliktas sprendžiamas taip: kliento taisyklė > produkto taisyklė > bendra; naujesnė vNNN > senesnė.

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
16. NETELPA LANGELYJE (v294): tekstas netelpa lentelės langelyje; trumpinti tekstą, šrifto nemažinti.

Ko automatika NEtikrina (tikrinama akimis kiekvieną kartą):
- ar vaizdai proporcingi ir subalansuoti;
- ar duomenys atitinka kliento užsakymą (pvz. formatas 2000x1062 ir išmatuota 1063 - klausti);
- ar laidų / tvirtinimo logika atitinka kliento taisykles.
