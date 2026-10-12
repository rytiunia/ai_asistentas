# Pjovimo lapas – konvencijos ir pritaikymas pjaustymo centrui

Pjovimo lapas yra vienintelis dokumentas, kurį baldininkas siunčia toliau. Jame klaida nematoma iki tol, kol
atvažiuoja plokštės. Todėl visi matmenys ir žymėjimai eina iš `model.json`, o ne rašomi ranka.

## Dabartinis formatas (`export_xlsx.py`)

Lapai: **Suvestinė** (m² iš pjovimo lapų sumų formulėmis, lapų skaičius `ROUNDUP(m² / (lapo m² × išeiga))`, kantų
metrai), po vieną lapą kiekvienai medžiagai (**LMDP18 korpusai**, **LMDP18 fasadai**, **LMDP16 stalčiai**,
**HDF3 nugarėlės**, **Stalviršis**), **Furnitūra**, **Standartas**.

Stulpeliai pjovimo lape:

| Stulpelis | Reikšmė |
|---|---|
| Nr. | Eilutė grupėje. |
| Detalė | Pavadinimas (Šonas, Dugnas, Fasadas (durys) …). |
| Žymėjimas | Korpusai, kuriems detalė priklauso: „K1 ×2, K3" – sujungtų eilučių atsekamumas. |
| L, W | **Galutiniai matmenys su kantu.** L – išilgai rašto. Be rašto – L didesnis. |
| Vnt. | Sujungtas kiekis. |
| Storis, Dekoras | Iš grupės. |
| Kantas L1 / L2 / W1 / W2 | ABS storis mm ant tos kraštinės; tuščia = be kanto. L1 – priekinė (matoma) kraštinė. |
| Raštas | V – vertikalus (šonai, durys), H – horizontalus (dugnai, stalčių fasadai), – be rašto. |
| Plotas, m² | Formulė `L×W×vnt / 1e6`. |

Vienodos detalės sujungiamos pagal (pavadinimas, L, W, storis, kantai, raštas) – ne tik pagal matmenis, kad
skirtingai kantuotos detalės neliktų vienoje eilutėje.

## Kai pjaustymo centras turi savo šabloną

Gauti jų Excel ir atkartoti 1:1, kad baldininkas tik persiųstų failą. Keisti **tik** `export_xlsx.py` funkciją `cut_sheet`
(stulpelių tvarka, pavadinimai) ir, jei reikia, reikšmių išvedimą. Tipiniai skirtumai:

- **Be kanto.** Jei centras nori matmenų be kanto: `L − (L1 + L2)`, `W − (W1 + W2)`. Daryti formule iš modelio
  reikšmių, ne perrašant skaičius; lape aiškiai užrašyti „matmenys be kanto".
- **Kantų žymėjimas** vienu stulpeliu: „2-2-0,8-0,8", „I-I-P-P" (ilgis / plotis) ar „1/1/0/0". Sudaryti iš `kantai[]`.
- **Raštas** kaip „taip/ne" arba „L išilgai" – keisti žymėjimą, ne logiką (L visada išilgai rašto modelyje).
- **Medžiagų kodai** tiekėjo kalba (Egger H1180 ST37, Kronospan K001 PW) – tai `standartas.json` reikšmės.
- **Nesujungti** – kai centras nori po eilutę kiekvienai detalei (etiketėms): rašyti iš `detales[]`, ne `pjovimas[]`.

## Patikros prieš siunčiant

- Suvestinės m² = pjovimo lapų sumų (formulės, `recalc.py` `total_errors: 0`).
- Fasadų grupės dekoras sutampa su tuo, kurį klientas patvirtino puslapyje (puslapio chip'as keičia tik rodymą –
  į `standartas.json` ir Excel reikia įrašyti patvirtintą kodą ir paleisti iš naujo).
- Korpusų ID ir pločiai žymėjimo stulpelyje atitinka projekciją.
