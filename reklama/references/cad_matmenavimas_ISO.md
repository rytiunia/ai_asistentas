# CAD / ISO – PRIVALOMOS TECHNINIŲ BRĖŽINIŲ MATMENAVIMO TAISYKLĖS

**Taisyklės statusas: PRIVALOMA. Taikoma visiems automatiškai generuojamiems techniniams, surinkimo ir gamybiniams brėžiniams.**

## 1. ISO STANDARTAI

Visi brėžiniai turi būti generuojami vadovaujantis:

- ISO 129-1:2018 – matmenų pateikimas.
- ISO 128 – linijų tipai, projekcijos ir grafinės taisyklės.
- ISO 5455 – masteliai.
- ISO 5457 – brėžinių lapų formatai.
- ISO 7200 – pagrindinis brėžinio įrašas.
- ISO 3098 – techninis šriftas.
- ISO 2768-1 – bendrosios linijinių ir kampinių matmenų tolerancijos, kai jos aiškiai priskirtos.

## 2. MATAVIMO VIENETAI

- Visi linijiniai matmenys pateikiami tik milimetrais (mm).
- Pagrindiniame brėžinio įraše nurodyti: `ALL DIMENSIONS IN mm UNLESS OTHERWISE SPECIFIED`.
- Prie individualių matmenų nerašyti `mm`.
- Nenaudoti metrų atskiriems matmenims, jei nenurodyta išimtis.
- 1,5 m žymėti `1500`.
- 3 m žymėti `3000`.
- 12 m žymėti `12000`.
- Dešimtainiams dydžiams naudoti kablelį: `1,5`.
- Kampus žymėti su laipsnio simboliu: `45°`.
- Skersmenis žymėti `⌀6`, spindulius `R10`.

## 3. PASIKARTOJANČIŲ MATMENŲ ŽYMĖJIMAS

Vienodi pasikartojantys intervalai žymimi ISO formatu:

- Du intervalai po 1500 mm: `2× 1500 (= 3000)`.
- Trys intervalai po 1000 mm: `3× 1000 (= 3000)`.
- Keturi intervalai po 500 mm: `4× 500 (= 2000)`.

Skliaustuose pateikiama suma yra informacinis matmuo.

Jei bendras ilgis yra kontroliuojamas gamybinis matmuo, jį nurodyti atskirai kaip pagrindinį matmenį. Vengti dvigubo to paties kontroliuojamo matmens nurodymo.

Nenaudoti mišrios formos `2×1.5=3m`, jei brėžinio vienetai yra mm.

Atskirų vienodų detalių kiekį specifikacijoje žymėti atskirai nuo intervalų matmenų, pavyzdžiui, `2 vnt. × 1500 mm`.

## 4. MATMENŲ LINIJŲ IŠDĖSTYMAS

Privaloma matmenų hierarchija:

1. Arčiausiai objekto – lokalūs matmenys, skylės, tarpai ir išpjovos.
2. Toliau – elementų ir atskirų objektų grupių matmenys.
3. Tolimiausiai – bendras konstrukcijos plotis ir aukštis.

Rekomenduojami A3 brėžinio nustatymai (tai praktiniai nustatymai, ne universalūs ISO privalomi dydžiai):

- Pirmos matmenų linijos atstumas nuo kontūro: 10–12 mm.
- Atstumas tarp lygiagrečių matmenų linijų: 7–10 mm.
- Matmenų linijos storis: 0,25 mm.
- Matomo kontūro linijos storis: 0,50 mm.
- Matmenų teksto aukštis: 3,5 mm.
- Rodyklės ilgis: apie 3 mm.
- Iškeltinės linijos išsikišimas už matmenų linijos: apie 2 mm, kai jos storis 0,25 mm.

Matmenų skaičius pateikti taip, kad būtų lengvai skaitomi ir nekliudytų geometrijai.

## 5. LINIJŲ SUSIKIRTIMAI

- Automatiškai vengti matmenų linijų tarpusavio susikirtimų.
- Vengti nereikalingų matmenų ir iškeltinių linijų susikirtimų.
- Jokia linija negali eiti per matmens tekstą.
- Susikirtimas leidžiamas tik tada, kai jis neišvengiamas ir brėžinys lieka vienareikšmis.
- Neišvengiamo matmenų linijos susikirtimo vietoje matmenų linija neturi būti savavališkai nutraukiama.
- Iškeltinės linijos turi aiškiai parodyti, kurio kontūro, krašto, taško ar ašies matmuo nurodomas.
- Matmenų linijos negali būti pakeičiamos gaminio kontūro linijomis.
- Negalima palikti matmenų užrašų už lapo ribų arba vieno ant kito.
- Automatiškai optimizuoti matmenų išdėstymą taip, kad būtų kuo mažiau linijų susikirtimų.

## 6. MATMENŲ GRUPAVIMAS

Jei brėžinyje yra keli atskiri objektai arba logiškos grupės:

- Kiekvienai grupei nurodyti jos plotį ir aukštį.
- Nurodyti atstumus tarp grupių, kai jie būtini gamybai.
- Atskirai nurodyti bendrą visos kompozicijos plotį ir aukštį.
- Matmenys turi būti susieti su faktine grupės geometrija, ne vien su viso brėžinio aprėptimi.
- Vienos grupės matmenų linijos neturi būti vedamos per kitą grupę, jei galima jų išvengti.
- Nepainioti raidžių, skaičių, rėmų ar kitų atskirų elementų su viena bendra matmenų grupe.

## 7. SKYLIŲ IR TVIRTINIMŲ MATMENAVIMAS

- Skylių matmenis pateikti pagal jų centrus.
- Aiškiai pažymėti skersmenį ir skylių kiekį, pvz., `4× ⌀6`.
- Tvirtinimo skylių koordinates pageidautina matmenuoti nuo vienos aiškios atskaitos bazės.
- Naudoti bazinį arba koordinatinį matmenavimą, kai tai sumažina tolerancijų kaupimąsi ir linijų susikirtimus.
- Skylės turi būti susietos su realia 1:1 gamybine geometrija.
- Negalima apskaičiuoti skylių padėties pagal vizualiai sumažintą brėžinio vaizdą.
- Negalima automatiškai sugalvoti skylių tolerancijų ar tvirtinimo atstumų be patvirtintų projektinių taisyklių.

## 8. ILGI OBJEKTAI

- Ilgiems profiliams, pilonams ir konstrukcijoms naudoti atitinkamą mastelį.
- Kai būtina, naudoti sutrumpinto vaizdo pertraukimo žymėjimą.
- Matmenys visada turi atspindėti tikruosius objekto matmenis.
- Sutrumpintam objektui atitinkama matmenų linija turi būti vientisa.
- Nenaudoti vizualaus ilgio kaip tikrojo gamybinio matmens.

## 9. PROJEKCIJOS

Kiekvieną projekciją matmenuoti pagal jos paskirtį:

**PRIEKIS:** bendri gabaritai, objektų grupių plotis, aukštis ir tarpai.

**GALAS:** tvirtinimo rėmai, skylių centrai, profilių išdėstymas, montavimo taškai.

**ŠONAS:** konstrukcijos gylis, medžiagų storiai, išsikišimai ir įleidimai.

**PJŪVIS:** visų reikalingų medžiagų storiai, atstumai, užlaidos ir technologiniai mazgai.

**GAMYBINIS 1:1:** tikra vektorinė geometrija, pjovimo kontūrai, skylių centrai ir tikslūs gamybiniai matmenys.

Matmenų nedubliuoti skirtingose projekcijose, išskyrus atvejus, kai pakartojimas aiškiai reikalingas informacijai arba yra pagalbinis.

## 10. TOLERANCIJOS

- Gamybiniams matmenims turi būti nustatytos tinkamos tolerancijos.
- Individualias tolerancijas naudoti ten, kur jos būtinos surinkimui ir funkcionalumui.
- Bendrąsias tolerancijas taikyti tik tada, kai brėžinyje aiškiai nurodytas atitinkamas standartas ir klasė.
- Negalima išgalvoti tolerancijų iš vien vizualios informacijos.
- Skirtingiems technologiniams procesams gali reikėti skirtingų tolerancijų.

## 11. AUTOMATINIS MATMENŲ IŠDĖSTYMO ALGORITMAS

Prieš pateikiant galutinį brėžinį sistema privalo:

1. Atpažinti atskirus objektus ir jų logines grupes.
2. Nustatyti tikrus geometrinius kontūrus ir jų ribas.
3. Patikrinti matavimo vienetus ir mastelį.
4. Sugeneruoti reikalingus vietinius ir bendruosius matmenis.
5. Išdėstyti matmenų linijas pagal hierarchiją.
6. Patikrinti matmenų linijų, iškeltinių linijų, teksto ir geometrijos susikirtimus.
7. Automatiškai perkelti konfliktuojančias matmenų linijas į laisvas zonas.
8. Patikrinti, kad rodyklės ir iškeltinės linijos būtų susietos su teisingais geometriniais elementais.
9. Pašalinti nereikalingus pasikartojančius matmenis.
10. Patikrinti, ar visi būtini gamybai matmenys yra pateikti.
11. Patikrinti, ar matmenys ir jų tekstas telpa į brėžinio lapą.
12. Atlikti galutinės PDF ir CAD/DXF išvesties kontrolę.

Jei įkeltos geometrijos mastelis nepatvirtintas, draudžiama spėti realius matmenis. Sistema turi reikalauti patvirtinto mastelio arba žinomo kontrolinio matmens.

## 12. PRIVALOMAS GALUTINIS REZULTATAS

Visi automatiškai sugeneruoti brėžiniai privalo būti:

- Matmenuoti milimetrais.
- Aiškūs, tvarkingi ir techniškai vienareikšmiai.
- Suderinti su ISO matmenavimo principais.
- Su logiškai išdėstytomis matmenų linijomis.
- Be teksto persidengimų ir išvengiamų linijų susikirtimų.
- Su visais gamybai būtinais matmenimis.
- Su tikslia faktine CAD geometrija.
- Tinkami perduoti gamybai be papildomo matmenų spėliojimo.

**PAGRINDINĖ TAISYKLĖ:** pirmiausia užtikrinti geometrinį tikslumą, po to ISO atitinkantį matmenavimą, tada automatiškai optimizuoti matmenų išdėstymą ir vizualinį aiškumą. Gražus brėžinio išdėstymas niekada negali būti svarbesnis už tikslų ir vienareikšmį gamybinį matmenį.