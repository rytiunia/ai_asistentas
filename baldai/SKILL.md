---
name: baldai
description: "Virtuvės korpusinių baldų parametrinis generatorius Ryčio baldininkams: iš sienos matmenų ir korpusų sekos (tekstas, eskizas ar lentelė) vienu paleidimu padaro 3D peržiūrą klientui su dekoro keitimu, priekinę projekciją su matmenimis ir pjovimo lapą Excel pjaustymo centrui (detalės, kantai, raštas, furnitūra, medžiagų suvestinė). Naudok VISADA, kai pokalbyje yra virtuvė, korpusai, spintelės, apatiniai / viršutiniai, fasadai, stalčiai, pjovimo lapas, detalių sąrašas, LMDP / HDF, kantavimas, Egger / Kronospan dekorai, konfigūratorius ar baldininkui reikia vaizdo klientui ir detalių skaičiavimo."
---

# Baldai – virtuvės korpusų generatorius

**Versija: 2026-10-10 v3** (v3: eskizo etalonas pataisytas – viršutiniai 954 iki lubų (860 + 560 + 954 = H2374), niša 2374 / 374; viršutiniams ≥ 700 mm – 2 lentynos (siena A: 73 → 76 detalės); projekcijos viršutinė paraštė korpusams iki lubų; plautuvė 3D šviesi. PAMOKA: pasukto eskizo skaitmenis skaityti du kartus – „954" pasuktas 90° buvo perskaitytas kaip „556"; aukščių grandinę VISADA sutikrinti su išmatuotu lubų aukščiu (suma turi sutapti). v2: standartinė korpusų biblioteka – indaplovės frontas, orkaitės korpusas su kaitlente, niša šaldytuvui su viršutine, aukštas su durimis; dekorai atskirai apatiniams / viršutiniams; HPL siena, LED; standarto perrašymas projekte; prietaisai 3D ir projekcijoje; etaloninis projektas iš kliento eskizo `eskizas_3280`. v1: variklis iš pokalbio prototipo – 4 tipai, pjovimo lapas, 3D puslapis, Excel.)

**!!! VIENAS ŠALTINIS – iCloud zip !!!**
1. Pilnas skill'as (SKILL.md + `scripts/`, `assets/`, `references/`) – `~/Library/Mobile Documents/com~apple~CloudDocs/AI_ASISTENTAS/baldai.zip`.
   Paskyroje (Claude) – tik paleidiklis (`references/paleidiklis_SKILL.md`). Dirbti TIK iš išarchyvuoto zip.
2. Kompiuteris nepasiekiamas – PRIEŠ darbą paprašyti Ryčio įkelti zip į pokalbį. Variklio iš atminties neatkurti.
3. Atsakyme nurodyti versiją (pvz. „baldai v1, iCloud zip").
4. Pakeitus skill'ą: pakelti „Versija", senąjį zip → `AI_ASISTENTAS/_archyvas/baldai_vNN_YYYY-MM-DD.zip`, naują zip – į tą pačią vietą
   (`device_commit_files`, `expectedMtimeMs` = stage metu gautas). Failų vardai zip'e – tik ASCII. Paleidiklio nekeisti,
   nebent keičiasi zip vieta.

Vartotojas: Rytis (Alytus, iškabų gamyba, CNC nestingas). Galutinis naudotojas – baldininkas, kuris nemoka 3D.
Kalbėti lietuviškai, tiesiai, be komplimentų. Puslapio ir Excel užrašai – lietuviškai.

## Ką skill'as daro ir ko ne

Vienas duomenų modelis (`model.json`) → trys išvestys iš **tų pačių detalių**: 3D vaizdas, projekcija, pjovimo lapas.
3D čia ne piešinys – kiekviena dėžė yra pjovimo lapo eilutė. Pakeitus standartą persiskaičiuoja viskas.

Veikia: viena tiesi siena; biblioteka `references/korpusai.md` (PRIVALOMA perskaityti prieš rašant projektą) –
apatiniai su durimis / stalčiais / plautuvės / indaplovės frontas / orkaitė su kaitlente, viršutiniai, niša šaldytuvui su
viršutine spintele, aukštas sandėliukas; stalviršis, cokolis, HPL siena, LED per liniją; dekorai atskirai eilėms;
sujungtos pjovimo eilutės; kantų metrai; furnitūra; lapų įvertis; standarto perrašymas projekte.
**Neveikia (nedaryti „ant greito"):** kampiniai korpusai, L / U virtuvės, gartraukio spintelė, integruotas šaldytuvas su
durimis, aukštas su orkaite, langai ir vamzdžiai, nugarėlė į griovelį. Jei to reikia – pasakyti Ryčiui, kad tai naujas
variklio modulis, ne parametras (sąrašas `korpusai.md` pabaigoje).

## Trys taisyklės

1. **Standartas – ne kodas.** Visi konstrukciniai skaičiai yra `assets/standartas.json`. Prototipo reikšmės – tipinis
   nedidelis cechas (18 mm LMDP, 3 mm HDF užleista, 2/4 mm tarpai, Blum Tandem 13 mm, cokolis 100). Jei gamintojo
   standartas nežinomas – naudoti šį, bet atsakyme **pasakyti, kad tai prototipo standartas**. Niekada neįsivaizduoti
   gamintojo reikšmių – paklausti (`references/standartas.md` – klausimynas).
2. **Pločių suma = sienos ilgis.** Variklis tai tikrina ir sustoja su klaida. Nespręsti už baldininką, kurį korpusą
   platinti – parodyti skirtumą ir paklausti (dažnas atsakymas: tarpinė juosta prie sienos arba paskutinis korpusas pagal matmenį).
3. **Pjovimo lapas – gamybos dokumentas.** Matmenys galutiniai su kantu, L išilgai rašto, kantai ABS mm. Jei pjaustymo
   centras reikalauja kito formato (be kanto, kitoks žymėjimas) – keisti `export_xlsx.py`, ne skaičius rankomis
   (`references/pjovimo_lapas.md`).

## Eiga

1. **Įvestis → `projektas.json`.** Iš baldininko teksto („siena 3,2 m, apatinės: 600 stalčiai, 900 plautuvė, 600, 600, 500;
   viršuje 1000, 800, 800, 600"), eskizo nuotraukos ar lentelės surašyti korpusus iš kairės į dešinę. Formatas –
   `assets/projektai/eskizas_3280.json` (pilnas: niša, indaplovė, orkaitė, HPL, LED, dekorai, standarto perrašymas) arba
   `siena_A.json` (paprastas). Tipai ir jų laukai – `references/korpusai.md`. Eskizo nuotrauką pasukti (PIL), iškirpti
   elevaciją, planą ir užrašus, padidinti – skaityti dalimis; pločių sumą patikrinti prieš rašant. Ką eskize pats piešėjas
   pažymėjo „?" ar ko nėra (aukšto korpuso turinys, gartraukis, stalviršio kodas) – rašyti į projekto `_pastaba` ir
   atsakyme išvardyti kaip tikslintina; standarto reikšmes naudoti, bet neišgalvoti kliento duomenų. Neaiškumus, kurie
   keičia konstrukciją, klausti PRIEŠ paleidimą.
2. **Paleidimas:**
   ```
   python scripts/run_all.py projektas.json --out <darbo_aplankas> [--std gamintojo_standartas.json]
   ```
   Duoda `model.json`, `detales.xlsx` (su perskaičiuotomis formulėmis, jei yra xlsx skill'o `recalc.py`) ir `index.html`.
3. **Pateikimas.** `index.html` → Artifact (klientas atsidaro telefone, suka 3D, renkasi dekorą); `detales.xlsx` →
   SendUserFile. Jei kompiuteris susietas ir Rytis nurodė aplanką – ir ten.
4. **Patikra prieš atiduodant** (privaloma, 1 min): `model.json` detalių skaičius ir pjovimo eilutės sutampa su puslapiu;
   Excel „Suvestinė" m² = pjovimo lapų sumos; `recalc.py` `total_errors: 0`; projekcijoje korpusų ID ir pločiai – tie patys
   kaip įvestyje. Kai keičiamas variklis – palyginti `model.json` su `assets/projektai/siena_A` etalonu (žr. „Keitimai").
5. **Atsakymas trumpas:** kas sugeneruota, kiek detalių / eilučių / m², kurį standartą naudojai, kas liko neaišku. Be sąrašo,
   ką puslapis turi – jis pats matosi.

## Failai

| Failas | Paskirtis |
|---|---|
| `scripts/engine.py` | Variklis: `Engine(std).build(projektas, dekorai)` → `model.json`. Korpusų tipai – metodai `apatinis`, `stalciai`, `virsutinis`, `frontai_durys`. |
| `scripts/export_xlsx.py` | `model.json` → Excel: „Suvestinė" (formulės), lapas kiekvienai medžiagai, „Furnitūra", „Standartas". |
| `scripts/build_page.py` | `model.json` + `assets/template.html` → `index.html`. |
| `scripts/run_all.py` | Visa grandinė + `recalc.py`. |
| `assets/standartas.json` | Konstrukcinis standartas – vienintelė vieta skaičiams. |
| `assets/dekorai.json` | Fasadų dekorų variantai puslapio chip'ams (Egger kodai, spalva, ar yra raštas). |
| `assets/template.html` | Puslapis: three.js r128 (cdnjs), projekcija SVG, lentelės; `__MODEL_JSON__` žymė. Dark/light. |
| `assets/projektai/siena_A.json` | Regresijos etalonas: 2450 mm, K1–K4 + V1–V3 → 76 detalės (v1–v2: 73; v3 viršutiniams 720 pridėta antra lentyna). |
| `assets/projektai/eskizas_3280.json` | Pilnas etalonas iš kliento eskizo: niša 660 (2374, spintelė 374) + 600/450/600/600/370 + 5×524 (954, iki lubų) → 105 detalės, 34 eilutės, HPL, LED. |
| `references/korpusai.md` | Korpusų biblioteka: kiekvieno tipo konstrukcija, laukai, eilės, dekorai, ko dar nemoka. |
| `references/standartas.md` | Kiekvieno parametro prasmė ir klausimynas gamintojui. |
| `references/pjovimo_lapas.md` | Pjovimo lapo konvencijos ir kaip pritaikyti prie pjaustymo centro šablono. |
| `references/paleidiklis_SKILL.md` | Paskyros paleidiklis (kopija). |

## Modelio struktūra (`model.json`)

- `detales[]` – kiekviena fizinė detalė: `korpusas`, `detale`, `grupe` (korpusas / fasadas / stalcius / nugarele / stalvirsis / hpl; `prietaisas` – tik vaizdui, į pjovimą neina), `eile` (fasadams: apatiniai / virsutiniai),
  `L`, `W`, `storis`, `kantai [L1, L2, W1, W2]`, `rastas` (V / H / –), `pos [x, y, z]`, `size [dx, dy, dz]`. Iš `pos`/`size`
  puslapis stato 3D – todėl detalė be teisingos pozicijos iškart matosi vaizde.
- `korpusai[]` – gabaritai, `frontai[]` (fasadai su rankenėlėmis), `prietaisai[]` (užrašai projekcijoje), nišai – `virsutine`.
- `pjovimas[]` – grupės pagal medžiagą (`fasadas:apatiniai`, `fasadas:virsutiniai` atskirai), vienodos detalės sujungtos, `zymejimas` rodo korpusus („K1 ×2, K3").
- `suvestine` – m² ir lapai pagal grupę, kantų metrai (+5 %), furnitūra.

## Keitimai variklyje

Naujas korpuso tipas = įrašas `TIPAI` (eilė: apatinis / virsutinis / abu) + metodas `Engine` klasėje (apatiniams – šaka
`apatinis()`, aukštiems – metodas tipo vardu), konstruojamas iš `karkasas`, `durys`, `stalcius`, `fasadas`, `prietaisas`.
Kiekviena detalė per `self.part(...)` su pozicija 3D – be jos nepriimti; prietaisai per `self.prietaisas` (vaizdas) ir
`prietaisai[]` (projekcijos užrašas). Po keitimo paleisti abu etalonus (`siena_A`, `eskizas_3280`) ir patikrinti, kad
nepakitusių tipų detalės liko identiškos (diff `model.json` `detales` be `prietaisas`). Aprašyti tipą `references/korpusai.md`.
Puslapio pakeitimai – tik `assets/template.html`; JS sintaksę tikrinti `node --check` (išimti `<script>` bloką).
