# P6 montavimo būdai (v90, Rytis 2026-10-11)

Spec `"mounting"`: `"ears"` (numatyta) | `"brackets"` | `"none"`. Kodas - `scripts/braizyti_begeliai.py`
(+ `assets/tvirtinimas.json` „brackets"), DXF - `scripts/p6_dxf.py` (`--separate` / `--rails-json`).
Be atskiro nurodymo užsakyme - VISADA standartinis montavimas (ausėlės), taip pat ir P6+3 (ant plokštės).

## 1. Ausėlės (`"ears"`, standartas)
Rėmas (U arba stačiakampis) su ausėlėmis - `references/auseles.md`. Nekeista.

## 2. U laikikliai = HANGERS - rėmas BE ausėlių (`"brackets"`)
**SUTARTINIS UŽRAŠAS (Rytis v103):** užsakyme rėmo prierašas „+ hangers“ (pvz. „frame 30x30x2mm + hangers RAL 7024“) = šis režimas;
„+ ears“ = ausėlės (1 skyrius). Lape angliškai - Hanger. Skriptas režimą ima iš MAIN DATA Rails teksto, jei `mounting` nenurodytas.
Rėmas tvirtinamas tiesiai į fasadą per profilį:
1. Daromi 2, 3, 4 ar 5 U formos laikikliai (pagal rėmo ilgį) per viršutinį ir apatinį rėmo bėgelį.
2. Laikikliai pritvirtinami prie fasado, į juos įstatomas rėmas ir prisukamas viršuje ir apačioje.

**Rėmas ir laikiklių vieta (Rytis 2026-10-11, patikslinta v92):**
- Horizontalūs bėgeliai - kaip įprasta: per raidžių viršutinių / apatinių horizontalių štrichų centrą (pvz. E viršutinės ir
  apatinės kojelės centras). Nekeičiami dėl laikiklių.
- **Laikikliai ir statmenys - per RAIDĖS CENTRĄ, ne prie krašto:**
  - per tiesaus stiebo vidurį (T stiebas, E nugarėlė);
  - raidei be tiesaus stiebo (S, A) - per raidės centrą (gabarito vidurys).
- **Didelės raidės / konstrukcijos:** geriau stambus rėmas gale, kuris dalinai matysis ir stabilizuos visą konstrukciją,
  nei silpninti struktūrą dėl taisyklės „rėmas nesimato". Dydžio ir apkrovų taisyklės pagal situaciją keičiamos TIK
  didelėms konstrukcijoms. Skriptas (H >= 1000, `large_h_mm`): laikiklis, kuriam arti nėra raidės centro, lieka tolygioje
  vietoje (gali matytis); rekomenduoja stambesnį profilį (pvz. 40x40) - Rytis sprendžia.
- Visi Ryčio pateikti skaičiai (1000 / 1080, 33, 200 / 100) - PAVYZDŽIAI; taisyklės - principai.

**Laikiklio matmenys:**
- **Vidinis aukštis = rėmo aukštis + 2 mm** (Rytis 2026-10-11).
  - Rėmo aukštis - nuo viršutinio bėgelio viršutinės plokštumos iki apatinio bėgelio apatinės.
  - Rėmas montuojant pasideda ant apatinės plokštumos; 2 mm laisvumas leidžia įdėti rėmą tarp plokštelių ir prisukti.
  - Išorinis aukštis = rėmas + 2 + 2 x 3.
- **Plotis 50.**
- **Viršutinė ir apatinė plokštuma - pagal rėmą** (išorinis matmuo): rėmas 30x30 -> 33, 40x40 -> 43.
- **Medžiaga:** gaminama pagal dydį iš Al 3 mm; jei svoris didelis - iš plieno 3 mm.
- **Skylės į fasadą:** D6 (30 profiliui) / D8 (40).
  - Kiekis: rėmas < 1000 - 2, rėmas >= 1000 - 3.
  - Išdėstymas: žingsnis p, nuo viršaus / apačios iki pirmos / paskutinės skylės - p / 2 (pvz. tarp skylių 200 -> nuo galų 100).
  - Rytis taip nurodė 2 skylėms; 3 skylėms taikomas tas pats principas - PATVIRTINTI.
- **Viršutinėje ir apatinėje plokštumoje** - po vieną D6 (prisukti į bėgelį).

Skriptas laikiklius:
- **v187 (Rytis 2026-10-13): POZICIJOS - ta pati formulė kaip laikiklio skylių: žingsnis p = rėmo ilgis / n, nuo rėmo galų p / 2**
  (2 vnt. - L/4 ir 3L/4); prie raidžių centrų nebetraukiama (senas v91 elgesys atšauktas);
- galiniame vaizde braižo juos TIK PUNKTYRU (kontūras ir skylės, be užpildo; v184, Rytis 2026-10-13);
- į BOM automatiškai prideda eilutę (jei spec jos neturi; placeholderiai `{BRK_N} {BRK_DIM} {BRK_MAT} {BRK_H}`)
  ir pašalina ausėlių eilutes, MAIN DATA „+ ears" -> „+ hangers" (lape U laikiklis = HANGER, v102);
- prideda svorį;
- P6 IR P1 pjūvyje (PROFILE P6 / P1 ON RAILS; P1 - v184) braižo laikiklį: sienelė prie fasado, viršutinė / apatinė plokštuma aplink bėgelius,
  ašinės Ø6, balionas su BOM pozicija (v94, Rytis: kur naudojami laikikliai - pjūvyje turi matytis);
- sudaro **2 lapą - laikiklio gamybinį brėžinį**: vaizdas nuo fasado su skylių grandine, šonas su įstatytu rėmu
  (punktyru, guli ant apatinės plokštumos, vidus = rėmas + 2), vaizdas iš viršaus 1:1, NOTES, BOM, MAIN DATA.

**Laikiklių kiekis (v185, Rytis 2026-10-13 - PATVIRTINTA):** rėmo ilgis iki 2,5 m - 2 vnt, iki 4 m - 3, iki 7 m - 4, toliau pagal tą pačią
formulę (ribų prieaugis didėja po 1,5 m: 11,5 m - 5, 17,5 m - 6 ... - tęsinys PATVIRTINTI), `assets/tvirtinimas.json` `n_by_len_mm`.

**PASIŪLYMAI - Rytis dar nepatvirtino** (keičiami `assets/tvirtinimas.json`):

- plienas, kai raidžių plotas >= 0,5 m² / rėmo m (kaip masyvių raidžių taisyklė v87);
- „didelės" raidės - H >= 1000; 3 skylių riba (rėmas >= 1000).

## 3. Atskiros raidės - jokio rėmo (`"none"`)
- Kiekviena raidė tvirtinama į fasadą per dugną. Dugno tvirtinimo skylės - pagal skill'o skylių logiką.
  Ašys - horizontalūs bėgeliai, kurie būtų rėme (kliento pilki arba `auto_frame`). Jie lape, BOM ir svoryje NERODOMI,
  į `RAILS_JSON` eksportuojami su `"separate": true`.
- **Elektra:** spec `"letters_power"`:
  - `"per_letter"` (numatyta) - iš kiekvienos raidės po 12V 1,5 m laidą, laidų išvestys VIENOJE horizontalioje linijoje
    per visas raides;
  - `"wago"` - jungtys raidžių viduje WAGO, vienas maitinimo laidas.
- **Lape:** galiniame vaizde raudona punktyrinė linija su išvesčių taškais ir užrašu. Pjūvio blokas -
  „PROFILE P6 - FIXED TO FACADE (SEPARATE LETTERS)".
- **DXF:** `RAILS_JSON=rails.json braizyti_begeliai.py spec.json lapas.pdf`, tada
  `p6_dxf.py klientas.pdf out --rails-json rails.json --no-letters` (`--separate` įsijungia iš JSON):
  - `3_REMAS` nėra;
  - D11 - viena bendra linija, parenkama taip, kad visose raidėse dugnas būtų kuo platesnis (>= 20 mm nuo krašto,
    trūkstant - 15 / 12 / 10 / 8 su perspėjimu);
  - D11 - plačiausio ruožo viduryje, >= 25 mm nuo varžtų;
  - failas `<prefix>_P6_1-1_laidas_linija.dxf`.
- **Ko brėžinyje nėra - BOM ir MAIN DATA NĖRA (Rytis 2026-10-11, net su 0 m - klaidina).**
  - Skriptas pats pašalina bėgelių, ausėlių ir sienos tvirtinimo eilutes.
  - Vietoj jų įterpia „Fixing through back to facade (DXF)".
  - Laido eilutę perrašo pagal `letters_power`; pozicijas pernumeruoja.
  - MAIN DATA be „Rails", su „Mounting: separate letters, no frame".
  - Šoniniame vaizde - tik raidės gylis (rėmo 30 nėra).

## Bendros taisyklės (v90)
- **Fasadas** nenurodytas = BETONAS: į jį galima tvirtinti bet kurioje vietoje (`wall` numatyta `concrete`).
  Fasado niuansai nurodomi užklausoje papildomai.
- **Varžtai** (raidės sienelės, laikiklių, plokštumų) - TIK TEORINĖ dalis. Galutinę varžto vietą nustato gamybininkas,
  nes teoriškai neįmanoma numatyti, kur jis tikslingiausias. Lape - tipinė vieta / žingsnis, ne galutinė.
- **Įtampa / laidas:** jei užklausoje nenurodyta - KLAUSTI (įvedama ranka). Standartai:
  - 220V, 1,5 m;
  - 12V, 1,5 m;
  - 12V + TRAFO BOX (jau aprašyta, `trafo_box`).

Bandymai: `scripts/projektai/montavimas_v90/` (README - komandos ir laukiami rezultatai).
