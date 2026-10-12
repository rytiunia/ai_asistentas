# EXTRA (Coop Extra, užsakovas BrandFactory) - kliento taisyklės

Raktažodžiai: EXTRA, FAS ..., darbo valandos, X apskritimas. Bendrinės P6 / P6+3 / P1 / bėgelių / ausėlių taisyklės -
SKILL.md. Čia - tik EXTRA standartas.
Pavyzdžiai: `assets/spec_extra.json`, `assets/spec_begeliai_extra*.json`, `assets/spec_extra_zframe*.json`,
etalonai `assets/etalonai/EXTRA_225923_begeliai_P6-3_1-25.pdf`, `assets/etalonai/EXTRA_Z_frame_1000H100.pdf`;
projektas `scripts/projektai/extra_225978/` (P1 nešviečiančios, stogo atramos).

## EXTRA standartas (Rytis patvirtino 2026-10-07)
  - X apskritime (P6+3): po apskritimu bėgelio NĖRA - tik 3 mm Alu pagrindas, X raidė tvirtinama per
    distancinius laikiklius.
  - EXTRA (P6): tvirtinimo rėmas - viršutinis + apatinis bėgelis, sujungti BENT 2 statmenais bėgeliais
    (spec `"frame": "verticals"`; statmenų kiekis max(2, ceil(ilgis/2500)+1)).
  - **EXTRA standartas - statmenys VISADA 3 (Rytis patvirtino 2026-10-07):** (1) pradžioje - pirmoji galima vieta po
    „E"; (2) po „T" per jo stiebo vidurį; (3) PASVIRĘS po „A" - atkartoja dešiniosios kojelės pasvirimą per jos vidurį.
    Spec grupėje EXTRA: `"verticals": [{"at": "start"}, {"under": 2, "mode": "stem"},
    {"under": 4, "mode": "leg", "side": "right"}]` (raidžių indeksai pagal x nuo 0; `place_verticals_rule`).
    Galiniame vaizde žymos „447 vert." / „473 diag.".
  - Darbo valandos (P6): tik horizontalūs bėgeliai, be statmenų (`"frame": "horizontal"`).
  - **EXTRA P6+3 bėgeliai VISADA: U profilis su ausėlėmis** - 40x40x2 arba 30x30x2 pagal aprašymą
    (`rail.size/depth`); ausėlė = profilio dydis. **Skylė (Rytis 2026-10-07): Ø6 ant 30 mm profilio, Ø8 ant 40 mm
    ir didesnių** (`EAR_HOLE`, BOM `{EAR_HOLE}`; perrašyti - `"ears": {"hole_d": N}`).

## Laido išėjimas EXTRA (Rytis 2026-10-07)
  * X (raidė ant plokštės) - VISADA iš X kojelės IŠORINIO APATINIO KAMPO (ne iš Z profilio): kojelė, kuri galiniame
    (veidrodiniame) vaizde yra KAIRĖJE; laidas iš kampo tiesiai žemyn;
  * EXTRA - apatinis bėgelis, ties E raide (`"cable": {"rail": "bottom", "end": "first"}`);
  * darbo valandos - vienoje eilėje su EXTRA -> apatinis bėgelis; po EXTRA (apačioje) -> VIRŠUTINIS bėgelis
    (`"cable": {"rail": "auto"}`: auto = viršutinis, jei grupė yra po kita grupe, kitaip apatinis).

## EXTRA X apskritimo Z kabinimas (Rytis patvirtino 2026-10-07; etalonas `assets/etalonai/EXTRA_Z_frame_1000H100.pdf`)
Spec: `"plate": {..., "zframe": {"z": "30x30x30x2", "tube": "20x20x2", "inset": 0.22, "edge_mm": 10,
"gap_mm": 20, "circle_margin": 10}}` (pavyzdys `assets/spec_extra_zframe.json`).
- **Dvi ATSKIROS detalės:** (11) 2 horizontalios Z 30x30x30x2 juostos tvirtinamos tiesiai prie apskritimo nugaros;
  (12+13) sieninis rėmas - 2 Z 30x30x30x2, galuose suvirinti su 20x20x2 Alu stačiakampiu profiliu (wallframe,
  tvirtinamas prie sienos). Montavimas: apskritimas prispaudžiamas prie sienos ir nuleidžiamas ant rėmo Z.
- **Juostų padėtis:** viršus / apačia 0,22 x D nuo apskritimo krašto (Z vaizde iš galo 2·30-2 = 58 mm aukščio).
- **Juostų ilgis** kinta pagal D: abu galai >= 10 mm X raidės viduje per visą tvirtinamo flanšo aukštį (tvirtinimai
  nesimato iš priekio); sieninis rėmas (juosta ± 20 tarpas + 20 vamzdelis) - apskritimo viduje, >= 10 mm nuo krašto;
  abi juostos vienodos, ilgis apvalinamas 5 mm. Rėmo Z = juosta + 2·20; rėmo plotis = juosta + 2·40;
  rėmo aukštis = (D - 2·0,22·D).
- **Lape (Rytis 2026-10-07):** Z-Z pjūvio NĖRA (nieko neduoda). Z juostų matmenys - GALINIAME VAIZDE prie kitų rėmo
  matmenų (viršuje: grandinė apskritimo kraštas - juosta - kraštas ir juostos ilgis „L (Z..)"; šone: vertikali
  grandinė 0,22·D / 58 / ... ), rėmas ten tik punktyru. Atskiras vaizdas **WALLFRAME - X CIRCLE (welded)** su savo
  matmenimis (plotis, Z ilgis, aukštis, Z aukščiai). DETAIL A schemoje - TIK apskritimo Z juostos viršuje ir apačioje
  ties distancerių varžtais (7), sieninio rėmo ten nėra. Priekyje Z juostos punktyru. Šonas `30+3+30`.
- BOM: `{ZP_LEN} {ZP_TOTAL_M}` juostos, `{ZF_LEN} {ZF_TOTAL_M}` rėmo Z, `{ZT_LEN} {ZT_TOTAL_M}` vamzdeliai,
  `{ZW}` rėmo plotis, `{Z_SIZE} {ZT_SIZE}`; svoryje skaičiuojama. Tvirtinimas Z->plokštė ir rėmas->siena - klausti.
- **Išdėstymo prioritetai (Rytis 2026-10-07, FAS 1800 testas):** (1) galinis vaizdas NE smulkesnis nei 1:50 - jei
  netelpa, mažinama DETAIL A (iki 150 pt), wallframe mastelis, ir vaizdai dedami greta (FRONT+SIDE | REAR viršuje);
  (2) WALLFRAME šalia šoninio; (3) didesni masteliai. Apatinė juosta - eilutė 11 pt, tekstas 8 pt (Rytis 2026-10-08: nesuspausta).
- **Grupės viena po kita (pvz. 7-23 po EXTRA):** galiniame vaizde užstotos pusės grandinės perkeliamos: viršutinės
  grupės apatinė ausėlių grandinė - į TARPĄ tarp grupių (jei >= 13 pt), jos bėgelio ilgis ir žymos - viršuje;
  apatinės grupės viršutinė grandinė ir ilgis - apačioje, toliau eilėmis. Laidų uodegos toje pačioje pusėje -
  skirtingose eilėse (13 pt). Matmenų užrašai grandinėse nesidengia (maži tarpai - šone / eile aukščiau).
- **Išdėstymas su Z (Rytis 2026-10-07):** viršuje FRONT | SIDE | WALLFRAME X (rėmas tęsia šoninio vaizdo eilę),
  apačioje DETAIL A | REAR | 3D (3D - didesnis). Wallframe mastelis parenkamas, kad tilptų šalia šoninio.

## EXTRA order 225978 rev B - „one frame" (Rytis 2026-10-09, TIK ŠIAM UŽSAKYMUI)
Kliento failai `1_extra_P6_3mm`, `2_extra_P6_3mm`, `3_extra_P6_3mm_one_frame`, `4_extra_P1_one_frame` (info failų
pavadinimuose). P6 - vientisas bėgis; FAS 700H80 ir FAS 1000H80 P1 - rėmas vientisas su raidėmis ir apskritimu
(`"one_frame"`), 7-23 - atskiras rėmas; P1 X tvirtinama tiesiai prie apskritimo be distancerių (`plate.gap_mm: 0`).
Stogo atramų lapo šiame komplekte nėra (Rytis).
FAS 700H80 (stogo iškaba): rėmas STAČIAKAMPIS □ 30x30x3, BE montavimo ausėlių (`rail.type: "square"`, grupėms
`"ears": false`); laido išvestys: X + EXTRA - VIENA, apatinis bėgelis A raidės gale (`EXTRA cable: {"rail": "bottom",
"end": "last"}`, X `cable: false`); 7-23 - apatinis bėgelis „7" gale (`{"rail": "bottom", "end": "first"}`). Kiekiai: FAS 1000H80 P1 - 1, FAS 700H80 - 1 (Ryčio sąraše „EXTRA FAS
1000H80 - 1" - patikslinti), 7-23 H480 - 4, 7-23 H864 - 4. Standartas kitiems EXTRA - Z kabinimas (aukščiau) lieka.
Spec - `scripts/projektai/extra_225978/spec_one_frame/` (client_pdf keliai - pakeisti; FAS 700 kliento PDF
išvalomas `clean_client.py ... 16,17,18,19,20,21,22,23,113,114,115,116`).

## Kita
- Stogo atramų precedentas - EXTRA order 225597 (kojos 25x25, plokštė 120x120x5); order 225978 - FAS 700H80 takskilt.
- ŽINOMA PROBLEMA: `auseles.py` EXTRA 1800H80 (U40, H 1080) - žr. SKILL.md „Žinomos klaidos".
