# ADAPTIVE CAD DRAWING LAYOUT — PRIVALOMA TAISYKLĖ

## 1. Pagrindinis tikslas

Sukurti automatinę, geometrijos pagrindu veikiančią gamybinių brėžinių komponavimo sistemą (Adaptive Technical Drawing Layout Engine).

Sistema privalo kiekvieną kartą iš naujo apskaičiuoti projekcijų dydžius, mastelius ir pozicijas pagal tikruosius gaminio gabaritus, formą, proporcijas ir techninės informacijos kiekį.

**Draudžiama naudoti fiksuotas projekcijų koordinates, dydžius arba vieną nekintantį lapo išdėstymo šabloną visiems gaminiams.**

Pagrindiniai prioritetai:
1. Geometrinis ir matmenų tikslumas.
2. Vienodas ortogonalių projekcijų mastelis.
3. Maksimalus naudingo lapo ploto išnaudojimas.
4. Aiškus projekcijų atskyrimas ir vizualinė hierarchija.
5. Jokių objektų, matmenų, tekstų ar žymėjimo linijų persidengimų.

## 2. Projekcijų mastelių taisyklės

FRONT VIEW, SIDE VIEW ir REAR VIEW:

- Visoms trims projekcijoms privalomas VIENODAS mastelis.
- Projekcijų aukštis privalo būti geometriškai vienodas, kai jos vaizduoja tą patį bendrą gaminio aukštį.
- SIDE VIEW gylis turi atitikti tikrąjį konstrukcijos gylį.
- REAR VIEW turi atitikti tikrąjį galinį vaizdą, nekeičiant geometrijos proporcijų.
- Keičiantis gaminio matmenims, visų trijų projekcijų mastelis perskaičiuojamas kartu.
- Negalima vienos ortogonalios projekcijos padidinti arba sumažinti nepriklausomai nuo kitų, siekiant užpildyti tuščią vietą.

DETAIL / SECTION:

- Nepriklausomas mastelis.
- Automatiškai parenkamas didžiausias tinkamas mastelis, leidžiantis aiškiai parodyti visas konstrukcijos detales.
- Prioritetas teikiamas tikriems CAD masteliams, pvz., 1:1, 1:2, 1:5.
- Detalės mastelis privalo būti nurodytas.

3D / ISOMETRIC VIEW:

- Nepriklausomas vizualinis dydis („NOT TO SCALE“).
- Automatiškai didinamas iki didžiausio dydžio, telpančio jam skirtoje zonoje.
- Negalima keisti X, Y ir Z proporcijų atskirai.
- Naudojamas vienodas mastelio koeficientas visoms trimis ašims.
- Objektas centruojamas pagal faktinį matomą 3D geometrijos kontūrą, o ne pagal visos scenos ar fiksuotos kameros ribas.
- Privalomas automatinis kameros pritaikymas objektui („camera fit to object“).
- Negalima palikti mažo 3D objekto didelės tuščios zonos kampe.

## 3. Automatinis lapo padalijimas

Lapas automatiškai suskirstomas į funkcines zonas:

A — FRONT / SIDE / REAR projekcijos.

B — 3D / ISOMETRIC VIEW.

C — DETAIL A / SECTION / konstrukciniai mazgai.

D — BILL OF MATERIALS / techniniai duomenys.

E — TITLE BLOCK / REVISION / pagrindinė informacija.

D ir E zonos rezervuojamos pagal realų lentelių turinį, privalomus laukus ir minimalų įskaitomą teksto dydį.

A, B ir C zonų plotai privalo būti DINAMIŠKI.

Pradinis orientacinis viršutinės grafinės srities paskirstymas:

- Ortogonalios projekcijos: 50–65 %.
- 3D projekcija: 15–30 %.
- Konstrukciniai pjūviai: 15–30 %.

Tai nėra fiksuotas šablonas. Procentai turi būti koreguojami pagal objektų realų pločio / aukščio santykį ir informacijos kiekį.

Sistema turi gebėti perkelti 3D vaizdą virš pjūvio, šalia pjūvio arba į kitą laisvą zoną, jeigu taip išnaudojamas didesnis naudingas lapo plotas.

## 4. Geometrijos analizė prieš komponavimą

Prieš dėliojant brėžinį būtina:

1. Nustatyti realų bendrą gaminio Bounding Box.
2. Atskirai apskaičiuoti FRONT, SIDE, REAR, 3D ir kiekvieno DETAIL geometrines ribas.
3. Nustatyti gaminio aukščio ir pločio santykį (Aspect Ratio).
4. Įvertinti kiekvienos projekcijos matmenų, tekstų, išnašų ir pozicijų žymėjimo zonas.
5. Apskaičiuoti reikalingą plotą ne tik geometrijai, bet ir visai jos anotacijų sistemai.
6. Sugeneruoti kelis galimus išdėstymo variantus ir pasirinkti geriausią pagal aiškumą, mastelį bei ploto išnaudojimą.

Jeigu gaminys aukštas ir siauras, pasirinkti vertikalioms projekcijoms tinkamą išdėstymą.

Jeigu gaminys žemas ir platus, automatiškai pertvarkyti projekcijas platesnei kompozicijai.

Jeigu objektas sudėtingas, suteikti daugiau vietos reikalingiems pjūviams ir matmenims.

Nekeisti geometrinių proporcijų siekiant vizualinio užpildymo.

## 5. Automatinis mastelio parinkimas

Ortogonaliosioms projekcijoms:

- Apskaičiuoti didžiausią bendrą mastelį, kuriam esant visos trys projekcijos telpa į paskirtas zonas kartu su jų anotacijomis.
- Pirmenybę teikti ISO 5455 rekomenduojamiems masteliams.
- Jei leidžiami nestandartiniai tarpiniai masteliai, juos naudoti tik aiškiai nurodant tikrąją mastelio reikšmę.
- Mastelį rinktis pagal realią spausdinamo lapo geometriją milimetrais, ne pagal ekrano pikselius.
- Jeigu projekcijas galima padidinti nepažeidžiant kitų taisyklių, sistema privalo tai padaryti.

3D projekcijai:

- Apskaičiuoti matomos geometrijos Bounding Box po izometrinės projekcijos.
- Automatiškai pritaikyti kamerą ir mastelį taip, kad dominuojantis geometrijos matmuo užimtų maždaug 85–95 % jam skirtos zonos atitinkamo matmens.
- Palikti saugią zoną kraštuose.
- Jeigu objektas siauras ir aukštas, neužpildyti pločio dirbtinai ištempiant objektą.
- Jeigu šalia lieka daug nenaudojamos erdvės, perskirstyti projekcijų zonas arba į tą vietą perkelti kitą tinkamą brėžinio elementą.

## 6. Tarpų ir laisvos erdvės optimizavimas

Sistema turi automatiškai valdyti:

- Tarpus tarp projekcijų.
- Atstumus nuo matmenų linijų iki gretimų elementų.
- Atstumus nuo projekcijų iki lapo rėmelio.
- Tarpus tarp 3D vaizdo, pjūvių ir techninių lentelių.

Tarpai turi būti vizualiai nuoseklūs ir proporcingi elementų dydžiui.

Negalima:
- Sugrūsti projekcijų vienoje pusėje paliekant didelę laisvą zoną kitoje.
- Mažinti 3D vaizdo vien todėl, kad pradiniame šablone jam numatytas mažas langelis.
- Palikti neproporcingai didelių tarpų tarp projekcijų.
- Didinti detalės ar lentelės vien tik dėl tuščios vietos, jei toks didinimas nepagerina įskaitomumo.

Vertinti faktinę nenaudojamą erdvę atsižvelgiant į gaminio Aspect Ratio. Aukšto ir siauro gaminio tuščias plotas šonuose savaime nėra klaida, jeigu objektas jau pasiekė maksimalų leidžiamą aukštį.

## 7. CAD / ISO matmenys ir anotacijos

- Matmenų reikšmės niekada nesikeičia dėl brėžinio mastelio.
- Visi matmenys pagal nutylėjimą milimetrais.
- Matmenų linijos turi likti susietos su tikraisiais geometrijos taškais.
- Projektavimo metu matmenų ir išnašų užimamas plotas laikomas tikra komponavimo kliūtimi.
- Draudžiami matmenų tekstų, pozicijų numerių ir geometrijos persidengimai.
- Linijų storis, rodyklės ir tekstų dydžiai parenkami pagal spausdinamo dokumento reikalavimus, o ne proporcingai sumažinami kartu su modeliu.
- Matmenų ir žymėjimų įskaitomumas turi didesnį prioritetą nei lapo užpildymo procentas.

## 8. Automatinė komponavimo optimizacija

Naudoti kelių etapų optimizavimo algoritmą:

1. Išmatuoti visas projekcijas.
2. Apskaičiuoti jų anotacijų zonas.
3. Nustatyti laisvą lapo darbinį plotą.
4. Sugeneruoti alternatyvius zonų išdėstymus.
5. Kiekvienam variantui apskaičiuoti maksimalų tinkamą ortogonalių projekcijų mastelį.
6. Atskirai maksimaliai pritaikyti 3D ir DETAIL mastelius.
7. Patikrinti ribas, kolizijas, matmenis ir tekstus.
8. Įvertinti nenaudojamą plotą, vizualinį balansą ir informacijos įskaitomumą.
9. Pasirinkti geriausią galiojantį variantą.
10. Tik po visų patikrų generuoti galutinį PDF.

Optimizavimo prioritetų tvarka:

**Geometrinis tikslumas → vienodas ortogonalių projekcijų mastelis → matmenų įskaitomumas → kolizijų nebuvimas → maksimalus projekcijų dydis → racionalus laisvo ploto panaudojimas → vizualinis balansas.**

Negalima pagerinti žemesnio prioriteto kriterijaus pažeidžiant aukštesnio prioriteto reikalavimą.

## 9. Automatinis alternatyvų pasirinkimas

Jeigu pradinis A3 išdėstymas netinka:

- Pirmiausia pertvarkyti projekcijų zonas.
- Tuomet optimizuoti tarpus.
- Jei leidžiama, įvertinti kitą lapo orientaciją.
- Jei būtina, sumažinti bendrą ortogonalių projekcijų mastelį.
- Jeigu informacija vis tiek netelpa įskaitomai, siūlyti papildomą lapą arba didesnį formatą.

Draudžiama tyliai nukirpti projekcijas, paslėpti matmenis arba sumažinti tekstą iki neįskaitomo dydžio.

## 10. Galutinio rezultato privaloma patikra

Po kiekvieno brėžinio generavimo atlikti automatinę vizualinio išdėstymo validaciją.

Patikrinti:

- FRONT, SIDE ir REAR turi identišką tikrąjį mastelį.
- Visos projekcijos rodomos pilnai.
- 3D vaizdas maksimaliai padidintas pagal savo zoną.
- DETAIL / SECTION įskaitomi ir nėra be reikalo sumažinti.
- Nėra persidengimų.
- Nėra nepagrįstai didelių tuščių tarpų.
- Lentelės, matmenys ir išnašos nesikerta.
- Lapas vizualiai subalansuotas.
- Dokumentas įskaitomas atspausdintas tikruoju A3 formatu.

**SVARBIAUSIA TAISYKLĖ:**

BRĖŽINIO IŠDĖSTYMAS PRIVALO PRISITAIKYTI PRIE GAMINIO GEOMETRIJOS, O NE GAMINIO GEOMETRIJA PRIE FIKSUOTO BRĖŽINIO ŠABLONO.

Kiekvienas naujas gaminys turi inicijuoti pilną projekcijų ribų, mastelių, zonų ir komponavimo perskaičiavimą.

Sistema negali laikyti ankstesnio gaminio projekcijų dydžių ar pozicijų tinkamais naujam gaminiui be pakartotinio optimizavimo.