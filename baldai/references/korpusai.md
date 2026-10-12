# Korpusų biblioteka – standartinė konstrukcija

Čia surašyta, kaip variklis konstruoja kiekvieną tipą. Tai ir yra „biblioteka": baldininkas rašo tik tipą ir plotį,
visa kita – iš standarto (`assets/standartas.json`). Skaičiai žemiau – standarto raktai, ne konstantos kode.

Bendra visiems korpusams (`Engine.karkasas`): du šonai (L = aukštis, W = gylis − nugarėlė, kantas priekyje), dugnas,
viršus – pilna plokštė (viršutiniai, aukšti) arba dvi 100 mm juostos (apatiniai, po stalviršiu), lentynos
(trumpesnės per `lentynos_atitraukimas`, 2 mm laisvumo pločiu), užleista HDF nugarėlė = korpuso išorinis gabaritas.
Fasadai: atitraukti `tarpas_krastuose` nuo korpuso kraštų, tarp fasadų `tarpas_tarp`, visos 4 kraštinės kantuotos
`kantas.matomas`. Durys: 1 iki 600 mm pločio, kitaip 2 (projektas gali perrašyti `durys`). Lankstai: 2 iki 900 mm
durų aukščio, 3 iki 1500, 4 virš. Rankenėlė: durims vertikali prie atidarymo krašto (apatiniams viršuje,
viršutiniams apačioje), stalčiams horizontali per vidurį.

| Tipas | Eilė | Konstrukcija | Projekto laukai |
|---|---|---|---|
| `apatinis_durys` | apatinė | karkasas + 1 lentyna + durys | `plotis`, `durys` |
| `apatinis_stalciai` | apatinė | karkasas be lentynų + n stalčių: fasadai lygūs, dėžė 16 mm (`stalcius.*`), bėgelių komplektas kiekvienam | `plotis`, `stalciai` (2–4) |
| `apatinis_plautuve` | apatinė | karkasas be lentynų + durys; plautuvė tik vaizde, išpjova – furnitūros eilutė | `plotis`, `durys` |
| `apatinis_indaplove` | apatinė | **be korpuso** – tik fasadas (plotis − 2·tarpas × aukštis − 2·tarpas), rankenėlė viršuje; kaimynų šonai – nišos sienos; cokolis tęsiasi | `plotis` (450 / 600) |
| `apatinis_orkaite` | apatinė | karkasas be lentynų; orkaitės lentyna taip, kad niša viršuje = `orkaite.nisa_aukstis` (595) iki korpuso viršaus; po lentyna stalčius (žemos dėžės `stalciaus_dezes_aukstis`); kaitlentė stalviršyje virš korpuso – vaizde ir išpjovos eilutė | `plotis` (600) |
| `virsutinis` | viršutinė | karkasas su pilnu viršumi, lentynos: 0 iki 400, 1 iki 700, 2 nuo 700; durys, 2 pakabos | `plotis`, `durys`, `aukstis`, `gylis` (nenurodžius – standartas) |
| `aukstas_nisa` | abi | niša laisvai stovinčiam šaldytuvui: šoninė plokštė per visą aukštį (`nisa.gylis`, kantas priekyje ir viršuje) iš nurodytos pusės; viršuje `virsutinis` nišos gylio ir pločio tarp plokštės ir sienos; šaldytuvas tik vaizde; cokolio ir stalviršio čia nėra | `plotis`, `aukstis`, `virsutines_aukstis`, `sonai` (kaire / desine / abu), `durys` |
| `aukstas_durys` | abi | sandėliukas: karkasas nuo cokolio iki `aukstis`, pilnas viršus, `lentynos` (4), durys dviem aukštais – riba `duru_riba` (numatyta – viršutinių apačia, kad linijos sutaptų su eile) | `plotis`, `aukstis`, `lentynos`, `durys`, `duru_riba` |

Linijos elementai (ne korpusai): **stalviršis** per visą apatinių eilę (`stalvirsis.gylis`, atskiras tiekėjas),
**cokolis** per apatinių eilę (fasadų medžiaga, apatinių dekoras), **HPL siena** (`"hpl": {}` projekte) tarp stalviršio
viršaus ir viršutinių apačios ten, kur sutampa apatinė ir viršutinė eilės, **LED** (`"led": true`) – metrai po viršutiniais.

## Eilės ir pločių kontrolė

Korpusai rašomi iš kairės į dešinę viena seka. Apatiniai užima apatinę eilę, viršutiniai – viršutinę, aukšti – abi
(prieš aukštą abi eilės turi būti vienodo ilgio). Abiejų eilių suma turi sutapti su sienos ilgiu, kitaip variklis
sustoja ir parodo skirtumą – sprendžia baldininkas (tarpinė juosta, platinamas korpusas).

## Dekorai

Projekto `"dekorai": {"apatiniai": "<kodas>", "virsutiniai": "<kodas>"}` – kodai iš `assets/dekorai.json`. Fasadai
pjovimo lape skaidomi į dvi grupes (apatinių su cokoliu, viršutinių). Puslapyje klientas keičia abi eiles atskirai –
tai tik rodymas; patvirtintus kodus įrašyti į projektą ir paleisti iš naujo. Stalviršio ir HPL dekorą rašyti į
`standartas.stalvirsis` / `standartas.hpl` (projekto perrašymas) – nežinomą palikti `?`, ne spėti.

## Standarto perrašymas projekte

`"standartas": {...}` projekte sujungiamas su `assets/standartas.json` (gilus merge). Tipiniai atvejai: viršutinių
aukštis ir apačia nuo grindų (pagal kliento HPL juostą), cokolis (kad stalviršio viršus būtų ten, kur matuota),
nišos gylis. Keisti tik tai, ką klientas / baldininkas nurodė.

## Ko biblioteka dar nemoka (naujas modulis, ne parametras)

Kampiniai korpusai (L / U virtuvės), gartraukio spintelė su išpjova, aukštas korpusas su integruota orkaite /
mikrobange, integruotas šaldytuvas (niša su durimis), stalviršio jungimas kampe, nugarėlė į griovelį,
rankenėlių frezavimas (gola profilis), kolonos / sienų iškyšos. Prašant – pasakyti, kad tai naujas modulis,
ir paklausti baldininko konstrukcijos.
