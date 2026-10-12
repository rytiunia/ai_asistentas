# ETALONAS: SPAR order 225960 (BrandFactory, 18 lapų) - Rytis patvirtino 2026-10-08

**Statusas:** SPAR / BrandFactory užsakymų ETALONAS ir PAGRINDAS daugumai kitų dokumentų (bet kurio kliento
komplektas iš kelių pozicijų: raidės ant bėgelių, folded plokštės, portalai, back plate, spauda, plėvelės, dekoras).
Ką daryti naujame užsakyme - pirmiausia žiūrėti, kaip tai padaryta čia.

- Pilnas komplektas: `assets/etalonai/SPAR_225960_komplektas_18_lapu.pdf`
  (originalas NAS: `/Volumes/dizainas/RYTIS/DARBAI/uzsienio reklama/Brandfactory/SPAR/SPAR order 225960/Drawing_SPAR order 225960.pdf`).
- Kodas, kuriuo komplektas sugeneruotas: `scripts/projektai/spar_225960/` (README.md - eiga ir kelių keitimas).
- Kliento užklausa: `SPAR Ottersøy Prosjekt NO_4002894.pdf` (6 psl.), tas pats NAS aplankas.

## 1. Lapų sąrašas - kuo remtis

| Lapas | Gaminys | Skriptas / tipas | Kuo etaloninis |
|---|---|---|---|
| 1 | SPAR 8000 + logo, 2 dalys | `braizyti_begeliai` □ 40x40x2 | 2 dalių rėmas, FRAME JOINT, 1 laidas prie logo, bėgelių galai už S ir apskritimo |
| 2 | 7-22 (8-21) 5264, 2 reklamos | `braizyti_begeliai` U30 | 2 grupės - kiekviena savo laidu į 1 trafo box, laidai aplink |
| 3 | OLE P. FJÆR 4400 | U30 | 8 ausėlės (Rytis), laidas kairėje |
| 4 | SPAR 3500 + logo | U30 | vientisi bėgeliai, galai už S ir apskritimo |
| 5 | 7-22 (8-21) 3040 | U30 | ausėlės pagal kliento kvadratėlius |
| 6 | Portalas 4700 x 3050 | `flat_sheets.portal` | viršus iš 2 dalių + DETAIL C angoje, nerūdijanti apsauga |
| 7-9 | Back plate 2700/2000 x 2100 | `flat_sheets.backplate` | VISOS iš 2 dalių (1400+700), TOP VIEW skylių grandinė, DETAIL B |
| 10 | Spauda 3000 x 2300 | `flat_sheets.print_sheet` | ne-iškabos lapas tame pačiame stiliuje |
| 11-12 | Plėvelės PMS 185 / sandblast | `flat_sheets.foil_sheet` | FINISH = plėvelės kodas, spalvotas langelis |
| 13 | Baltas dekoras 769 x 131 | `flat_sheets.decor` | BE fono: baltas logotipas + juoda hairline |
| 14 | Balta spauda ant sandblast | `flat_sheets.sandprint` | 2 dizainai viename lape |
| 15 | PANT 2273 | U30 RAL 8001 | vientisa reklama, apskritimas = balta plexi + pjaustyta plėvelė (decal) |
| 16 | SMÅGODT (vidaus) | U20 | be ausėlių, viršutinis bėgelis į sieną, laidas apačioje |
| 17 | KAFFEPAUSE (vidaus) | U20 | kompozitas = apskritimas + rėmo atkartojimas, plėvelė po raidėmis |
| 18 | FRISK & SUNN 3000 x 1000 | `braizyti_lapa` (folded) | P1 apskritimas atskiras elementas, BOM 10-12, balionai visuose vaizduose |

## 2. BENDROS TAISYKLĖS (galioja VISIEMS dokumentams)

### Lapas ir juosta
- A3, etaloninis rėmelis su zonomis (1-8 / A-F, 8 pt). Vaizdų zona viršuje, apatinė juosta per visą plotį:
  `PJŪVIS (214) | BOM | MAIN DATA (172) | REVISIONS + antraštė (272)` - vientisas blokas, be tarpų.
- BOM stulpeliai: POS 20 | PART .33 | MATERIAL .25 | FINISH .15 | QTY likutis. MATERIAL turi tilpti.
- Juostos eilutė >= 11 pt, tekstas 8 pt; juostos aukštis = max(172, 32 + 11 x eilučių). Nesuspausta.
- Antraštė (ISO 7200): CLIENT 14 pt bold, TITLE, ORDER NO. 14 pt bold (`ALT0000_00.00_RS`, kol nežinomas),
  FILE / DRAWING NO. = projekto pavadinimas, SCALE, FORMAT, SHEET „n / N", REV., PROJECTION, DRAWN, CHECKED, DATE.
- Projekto pavadinimas - pagal užsakymą („SPAR order 225960"), lapų TITLE „<projektas> - <gaminys>",
  failas `Drawing_<projektas>.pdf` užsakymo aplanke NAS.

### PDF -> CorelDRAW
- PDF'e GOST šrifto vardas „GOST Common" (`lapas_core.pdf_fix_fonts`) - Corel atidaro tekstą TEKSTU, neišsikraipo.
  Komplekte - ir `Drawing_<projektas>.cdr` (Corel: PDF -> Text -> Save As).

### Šriftas (GOST Common) ir dydžiai - privaloma
- Pagrindiniai priekio / šono matmenys **12 pt**; visi kiti (galinio vaizdo grandinės, detalės, pastabos, BOM,
  MAIN DATA, REVISIONS, balionai) **>= 8 pt**; vaizdų pavadinimai **13 pt**, mastelis **9 pt**.
- Netelpantis tekstas NEMAŽINAMAS žemiau 8 pt - trumpinti tekstą arba platinti stulpelį. Skriptai spausdina
  „! NETELPA" - tokių eilučių išvestyje turi nelikti.
- Patikra prieš atiduodant: `python3 scripts/patikra_sriftai.py <lapas.pdf>` - jokio teksto < 8 pt
  (išskyrus antraštės langelių pavadinimus CLIENT / TITLE / ...).

### BOM spalvos
- FINISH langelis su RAL - VISAS užpildytas RAL spalva (tamsiame fone baltas tekstas).
- **Plėvelių kodai - VISADA spalvotame langelyje** (FINISH ir MATERIAL): ORACAL 8500 614 žalia, 551-035 oranžinė,
  551 010 balta, Avery 777-002CF / PMS 185 raudona, sandblast pilka. Naujas kodas - į `lapas_core.FOIL`.
  Plėvelės eilutėje FINISH = plėvelės kodas (RAL atspalvis - pavadinime).
- Kiekviena BOM pozicija pažymėta balionu BENDRAME brėžinyje (priekis / šonas / galas), numeriai nesikartoja.

### Laidai ir maitinimas
- Laidas - **RAUDONA (#E2001A) stora (0,9 pt) ištisinė linija**, užrašai ta pačia spalva; trasa nesutampa su
  matmenų / išvadinių / balionų linijomis, eina APLINK gaminį (per raides nekerta).
- Visur **12V, 3 m**; prie trafo box - tik nuoroda „220V" (be ilgio). Trafo box - po gaminiu, rėmo spalvos,
  užrašai kontrastingi.
- Išvestis - kliento nurodytoje pusėje, **bėgelio GALE** (vidury nupieštas laidas - užklausos klaida);
  į viršų / apačią - >= 60 mm nuo galo. Kelios reklamos - kiekviena savo laidu į VIENĄ trafo box.
  Folded / portalas - D11 žymė galiniame vaizde + užrašas eilutėmis (netelpa už rėmelio).

### Rėmai, ausėlės
- Ausėlės - TIK ten, kur jos kliento faile (kvadratėliai ant bėgelių -> `ears_pt`); nėra - `ears: false`
  (vidaus: viršutinis bėgelis tiesiai į sieną). Aiškus Ryčio nurodymas - viršesnis.
- Bėgelių galai paslėpti už raidžių: pradžia = pirmos raidės kontūras ties bėgelio briaunomis + 30 mm,
  galas prie apskritimo = styga - 30 mm. Pailgintų ausėlių („trumpų statmenų") prie krašto nedėti.
- Rėmas iš 2 dalių - punktyras + „FRAME JOINT" priekio ir galiniame vaizde.

### Ne iškabų lapai (spauda, plėvelės, dekoras, back plate, portalas)
- TAS PATS lapo stilius, juosta ir šrifto taisyklės (`lib/flat.py`: begin / band / finish, `material_block`).
- Plokštės ilgesnės nei medžiaga (plexi 3050, Alu lakštas) - iš 2 dalių su jungties detale (DETAIL B / C),
  detalė dedama prie pat vietos (pvz. portalo angoje po pastaba).
- Balti lipdukai / dekoras - be fono, baltas + juoda hairline (pjovimo linija).

## 3. SPAR specifika
- Prieš darant - peržiūrėti `.../Brandfactory/SPAR/*/ALT*.pdf` (analogiški gaminiai jau gaminti).
- SPAR 8000 iš 2 dalių (SPA | R + logo): □ 40x40x2 su privirintomis ausėlėmis Ø8, tik 2 horizontalūs bėgeliai,
  jungtis tarp A ir R, VIENAS laidas - viršutinio bėgelio gale prie žalio apskritimo (SPA daliai `cable: false`).
- SPAR + logo viena dalis: bėgeliai vientisi; laidas viršutinio bėgelio gale prie S.
- Logotipas: ORACAL 8500 614 ant baltos plexi, šonai RAL 6029, neapšviestas lape kaip atskira grupė.
- PANT: vientisa reklama ant vieno rėmo, apskritimas - balta plexi + pjaustyta žalia plėvelė (kraštas ir
  piktograma iškirpti).
- Vidaus kategorijos (225721 KAFFEBAR): U 20x20x2, laidai tik apačioje, be ausėlių. P00 apskritimas -
  2 mm juodas Alu kompozitas VIENA detale su rėmo atkartojimu, z 20 | 2 | 50, plėvelė ORACAL 551-035.
- FRISK & SUNN TYPE 670 (3600 x 670, 2026-10-08): box lid iš 2 dalių 1500 + 2100 (`panel_joints`), Opal 8 (P6_8mm),
  laidas D11 po F -> Ø11 skylė kairėje užlenktoje briaunoje 29 nuo viršaus, PSU be dėžės; „PANEL JOINT" - pastaba už
  reklamos ribų. Kodas `scripts/projektai/spar_type670/`. 18 lapo (225960) DETAIL A (3 mm) ir „D11 ant fono" - pasenę.
- FRISK & SUNN (225400 / 225724): folded box lid 33, P1 apskritimas - atskiras tūrinis elementas
  (priekis 2 mm Alu RAL 6039, šonas 1 mm, dugnas 10 mm PVC), „&" P6 ant jo; laidas viršuje kairėje.
- Back plate 2000 / 2700 x 2100, box lid 40: iš 2 dalių 1400 + 700, L 30x30x2 viršus + apačia,
  DIN 7504 N 4.2x16 kas ~300, 50 nuo kraštų.
- Portalas (225809 / 202293 / 217482): PLEXIGLAS GS 3H25 3 mm RAL 3020, galas 2 mm Alu, dugnas 10 mm PVC,
  nerūdijanti 1 mm apsauga h 160 tik priekyje ir šonuose; viršus > 3050 - iš 2 dalių (DETAIL C angoje).

## 4. Spec raktai, naudoti etalone (API santrauka)
**`braizyti_begeliai.py` (raidės ant bėgelių):**
- grupė: `"cable": {"rail": "top|bottom", "end": "first|last", "x_pt": <kliento pt>, "dir": -1|1, "out": "up|down|left|right"}`
  arba `"cable": false` (grupė be laido); `"ears_pt": [x pt]` / `{"top": [...], "bottom": [...]}`; `"ears": false`;
  `"rails": [{"kind": "h", "poly": [...]}]` (mm nuo grupės raidžių kairės / viršaus); `"no_rails"`, `"behind"`,
  `"z0"`, `"depth_mm"`, `"lit": false`, `"frame": "horizontal"`.
- lapas: `"rail": {"size", "depth", "ral", "type": "square"}`, `"ears": {"hole_d", "smax"}`,
  `"trafo_box": {"voltage": "12V", "mains": "220V", "cable_len_m": 3, "x"}`, `"joints": [{"x_pt", "label"}]`,
  `"callouts": {"front": [[x_mm, y_mm, poz, dx, dy]], "rear": [...]}`, `"decals": [{"client_fill", "hex", "group"}]`,
  `"ignore_fills"`, `"no_plates"`, `"sheet": "n / N"`, `"drawing_no"`.
- kliento paruošimas (`mkclient2.make`): `splits` / `split_cols` (grupės), `logo_foil` (plexi + pjaustyta plėvelė),
  `logo_replica: (kompozito spalva, plėvelės spalva, juostos aukštis pt)` (apskritimas + rėmo atkartojimas).

**`braizyti_lapa.py` (folded):** `"element_colors": true`, `"element_return": {"r,g,b": "RAL"}`,
`"callouts": {"front": [[x_mm, y_mm, poz, dx, dy]], "side": [[atstumas nuo fono mm, y_mm, poz, dx, dy]]}`,
`"cable_exit": {"x_mm", "y_mm", "where", "label"}`, `"sheet"`, `"drawing_no"`.

**Bendra (`lapas_core.py`):** `F_DIM_MAIN 12`, `F_DIM_FRAME 8`, `F_INFO 8`, `F_VIEW 13`, `F_SCALE 9`, `ROW_H 11`,
`CABLE` / `cable_line()`, `FOIL` / `code_hex()`, `OVERFLOW` (netelpantys tekstai).
