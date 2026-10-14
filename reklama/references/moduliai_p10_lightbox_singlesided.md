# P10_lightbox_singlesided - vienpusė šviesdėžė, priekis kaip P10_lightbox_doublesided, dugnas - folded plate (v227, Rytis 2026-10-14)

Būklė: SUPRATIMAS PATVIRTINTAS (Rytis 2026-10-14 „teisingai"), parametrai atsakyti (3 sk.). **Generatorius v230:**
`scripts/p10_lightbox_singlesided.py spec.json out.pdf` -> 2 lapai (1: FRONT / RIGHT SIDE (laidas) / SECTION A-A / TOP VIEW, 3D,
EXPLODED, DETAIL B 3 zonos, BOM, MAIN DATA; 2: CAD padėklų išklotinės) + `_gamyba.dxf` (priekis FACE OUT su išpjova + 0,7, D6 žymės,
Ø3.2, išpjova kabeliui; dugnas su Ø3.2 ir kabelio skyle; pagrindas + Ø8; įdėklas). Logotipas - tiesiai iš kliento vektorinio PDF
(spec `"logo": {"pdf", "clip" (dėžės kontūras pt), "fill"}`). Pirmas projektas - `scripts/projektai/leapmotor_33577/` (poz. 30).
Varžtai: priekio atlankas -> dugno atlankas, 7 nuo priekio atlanko laisvo krašto (fasado), viršuje ir apačioje, 50 nuo galų, ~300.
Eskizas (patvirtintas): `assets/konstrukcijos/P10_lightbox_singlesided_eskizas.png` / `.pdf`.
Raktažodžiai: P10_lightbox_singlesided, vienpusė P10 šviesdėžė, single-sided P10 lightbox. Dvipusė - `moduliai_p10_lightbox_doublesided.md`.

## 1. Konstrukcija
- **Priekis** - KAIP P10_lightbox_doublesided: Alu 2 mm lankstytas padėklas (folded v173), logotipo / teksto išpjova + 0,7,
  iškištas plexi įdėklas (PRIKLIJUOTAS prie pagrindo), 3 mm plexi pagrindas ant ilgasriegių (prišaudyti iš VIDINĖS pusės) + veržlės.
- **Dugnas** - PAPRASTA folded plate, **3 mm mažesnė už priekį**, **tūris (atlankų gylis) 30 mm**.
- **Priekis užsideda ant dugno** (priekio atlankai ant dugno atlankų) ir **prisukamas varžtais PER PERIMETRĄ - visi 4 atlankai**
  (v231, Rytis; folded: Ø3.2, 7 mm nuo atlanko krašto, žingsnis ~300, nuo kampų 50; dešiniajame - ne arčiau 40 nuo laido išpjovos).
  Varžtų tipas nenurodomas (standartas, Rytis: „neaktualu").
- **Prie fasado - per dugną tiesiai į fasadą**: tvirtinimo skylių dugne NEBRAIŽYTI (gręžia montuotojas).
- **Rėmo NĖRA** (laikantysis - dugnas).

## 2. Laidas (standartas)
- Dešinės šoninės kraštinės viršuje, **dugno** šoniniame atlanke - skylė su **gumine tarpine**.
- Gylyje - **kuo arčiau dugno galo (fasado)**: skylės centras **23 mm nuo dugno (atlanko) priekinio krašto** (30 gylyje -> 7 nuo dugno plokštės).
- **Priekio** dešiniame atlanke - **atvira išpjova** nuo atlanko laisvo krašto iki tarpinės, kad priekį būtų galima užmauti ant dugno.

## 3. Atsakyta (Rytis 2026-10-14, Leapmotor PO 33577 poz. 30)
1. „3 mm mažesnė" - **3 mm KIEKVIENAI kraštinei** (dugnas W-6 x H-6).
2. **Bendras tūris 80 mm**: priekio atlankas = 80 (- t); **dugnas 30 mm įlenda į priekį** (bendras tūris vis tiek 80).
3. **LED - ant dugno GALINĖS PLOKŠTUMOS** (matomi pjūvyje A-A, DETAIL B ir exploded - v232) (vidinis dugno paviršius prie fasado), NE ant kraštinių (v231, Rytis).
4. Laidas - pagal standartą (2 skyrius); skylės Ø / tarpinės tipas - kai paaiškės (neišgalvoti).
5. **Dugnas - Alu 1,5 mm** (folded v173); priekis - Alu 2 mm.
6. Stiklas: **įdėklas 8 mm** (su Alu 2 -> išsikišimas 6), 3 mm pagrindas - kaip doublesided.

## 4. Dokumentai (įgyvendinta v230; buvęs planas, pagal „Bendrinės taisyklės" 20-24)
1 lapas - kaip P10_lightbox_doublesided etalonas (FRONT, VIEW FROM WALL / dugnas, SECTION A-A, 3D, EXPLODED, TOP VIEW, DETAIL B
pjūvis su pozicijomis, BOM, MAIN DATA); 2 lapas - vietoj rėmo: DUGNAS (CAD) - vaizdai + kabelio skylė, priekio išpjova;
gamybos DXF - priekio ir dugno išklotinės (folded v173), plexi pagrindas / įdėklas.

## 4a. Lapo išdėstymas (v232, Rytis)
1 eilė: FRONT, RIGHT SIDE (laidas), SECTION A-A; dešinė kolona per visą aukštį - **EXPLODED VIEW kuo didesnis**;
2 eilė: 3D, TOP VIEW (mažiau svarbus).

## 5. Dar neatsakyta (Leapmotor poz. 30) - lape „?"
- kabelio skylės aukštis nuo viršaus (y), skylės Ø ir tarpinės tipas, priekio išpjovos plotis (geometrija: centras 7 nuo
  dugno nugaros -> Ø <= ~10, kitaip kerta lenkimą); LED moduliai / PSU - lape „?", tikrinama gamyboje (Rytis 2026-10-14).
