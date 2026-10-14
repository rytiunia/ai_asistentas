# Kiti produktų moduliai (perkelta iš SKILL.md v71, taisyklės nepakeistos)

### P6 ant stačiakampio Alu profilio (Rytis patvirtino 2026-10-07)
Jei rėmas - stačiakampis / kvadratinis Alu profilis (`rail.type: "square"`), prie jo PRIVIRINAMOS tvirtinimo
ausėlės iš 3 mm Alu: plokštelė sienos plokštumoje (tarp profilio ir sienos), per visą profilio aukštį + išsikišimas
į rėmo vidų (= profilio aukštis), skylė išsikišime (Ø pagal profilį - žr. ausėlių skylė). Išdėstymas - tos pačios
ausėlių taisyklės (`references/auseles.md`), Smax - pagal profilio dydį (□ profiliams lentelėje reikšmių dar
NĖRA -> naudojama U to paties dydžio reikšmė, klausti). Pjūvyje ausėlė rodoma VISADA (balionas = BOM ausėlės
pozicija), BOM: `Mounting ear, welded, Ø{EAR_HOLE} hole | Alu 3 mm | RAL rėmo | {PLATES_N} pcs.`; svoryje ausėlė 3 mm.
`"ears": {"enabled": false}` - tik jei užsakyme aiškiai be ausėlių.

### P1 nešviečiančios raidės ant bėgelių (v29, Rytis 2026-10-08; pirmas atvejis EXTRA order 225978)
- Spec: `"front": "P1"` + `"power_note": "P1 NON-LIT - no LED, plexi, cable or PSU"`, grupėms `lit: false`,
  `cable: false`, `"trafo_box": false`, `face_hex` = RAL spalva (priekis dažytas). Pavyzdys
  `scripts/projektai/extra_225978/spec/s1_fas1000.json`.
- Sandara (kaip SPAR P1 etalone): priekis Alu 2 mm (RAL), šonai Alu 1 mm (RAL), dugnas PVC 10 mm; raidė prie U -
  varžtas per U sienelę į PVC dugną. X ant plokštės - ant 30 mm distancerių, dugnas lygus su šonais (ne įleistas 25).
- BOM: be plexi, plėvelių, A (PVC bortelis), B (varžtas), LED, trafo. Svoris: priekis Al 2, dugnas PVC 10.
- **Dugnas PVC 10 mm NEDAŽYTAS (v184 / v186, Rytis 2026-10-13):** BOM FINISH „-"; REAR VIEW - dugnas šviesiai pilkas
  (nedažytas plastikas, `PVC_RAW`), ne korpuso RAL. Dažytas - tik nurodžius `back_ral`.
- **P1 su hangers (v184):** pjūvyje `PROFILE P1 ON RAILS` - laikiklis (plokštumos virš / po bėgeliais, sienelė prie fasado, Ø6).

### Stogo iškaba - atramos (v29, Rytis 2026-10-08; pirmas atvejis EXTRA FAS 700H80 takskilt)
- Iškabos lapas - standartinis (bėgeliai, ausėlės, Z rėmas kaip „wall option"); kliento stogo kojas iš kliento PDF
  pašalinti (`clean_client.py`), kitaip atpažįstamos kaip statmenys.
- Atramos - ATSKIRAS lapas (`scripts/projektai/extra_225978/roof_sheet.py`, README ten): FRONT (kojos punktyru už
  iškabos, stogo linija, 150 iki apskritimo), TOP VIEW (pagrindų vietos), SECTION A-A 1:10, DETAIL B (plokštė),
  DETAIL C (koja prie U), 3D iš galo; juostoje - vėjo skaičiavimas, BOM, MAIN DATA.
- Principas: kojos □30x30x2 RAL 7035 kliento vietose (paslėptose vietose - iki viršutinio bėgelio); galinės atramos
  □30x30x2 ~45° prie VIRŠUTINIO bėgelio, pėda 650 už kojų, šakutės + M8 (gniuždoma ir tempiama); kampuotis
  L40x40x4; plokštės 120x120x5 4xØ9 + EPDM. Precedentas EXTRA order 225597 (kojos 25x25, plokštė 120x120x5).
- Vėjas: cf 1.8, qp prielaida 0.8 kN/m² (vb,0 26, II, z 5 m) - lape „ASSUMED", stogo tipą ir vietą KLAUSTI.

### Senų brėžinių perdarymas į mūsų stilių (Rytis 2026-10-07; bet kurio kliento, pvz. ALT8857 Clas Ohlson)
- Įvestis - senas BrandFactory brėžinys: mastelis iš bendro matmens (`scale` = brėžinio mastelis, pvz. 40),
  raidės - užpildyti kontūrai (dublikatai šalinami automatiškai), rėmas - spalvoti stačiakampiai -> spec
  `groups[].rails` (mm nuo raidžių kampo, profilio storis normalizuojamas), `ignore_fills` - rėmo / rodyklių spalvos.
- Duomenys iš seno lapo (medžiagos, spalvos, LED, gylis, laidas, kiekis) -> BOM / MAIN DATA; ORDER NO. - ALT Nr.,
  FILE / DRAWING NO. - užsakovo užsakymo pavadinimas. Ko sename lape nėra - tuščia vieta.
- Kvadratinis / stačiakampis wallframe (□ 60x60x2): `rail.type: "square"`.
- Kelios teksto eilutės + logotipas: kairė grandinė pagal eilutes (logotipas > 1,3 x mediana neįskaičiuojamas).
- Spalvos BOM: RAL, 3M (`VINYL`), Pantone (`PMS` lentelė `lapas_core.py`).
- Storiai svoriui: `face_thk`, `thk_mm` (pvz. {"back": 2}).



## (iš SKILL.md v77) Maitinimas - TRAFO BOX (v9)
- v161 (Rytis 2026-10-13, iš darbų analizės): leistini dėžės variantai - „TRAFO BOX" (bendras), „Trafbox", „Plastic IP box
  with WAGO inside" (Volvo), su PWM / potenciometru (pritemdymas, „+ potentiometer"). PSU numatyta Kaisen KPS / BaltLED BPS;
  **Mean Well - tik kliento nurodymu** (darbuose sutikti: HLG-40-A, HLG-60, HLG-80, HLG-240, XLG-75 / 100 / 150, ELG-75,
  LPV-35, LPF-40-12, PWM-200-24 - Volvo, DSV, BN Skilte, Skyltkoncept sandėliui). Standartinis el. išvesties užrašas:
  „+1,5m ~230V El. Output" / „+1,5m 12V El. Output", „From letter / construction: 1.5m, 12V".
- REAR VIEW: kiekviena šviečianti grupė (raidės, X) turi SAVO laidą; VISI laidai eina į vieną TRAFO BOX.
  Dėžė - rėmo spalvos (RAL bėgelių), užrašas „TRAFO BOX / RAL ….", balionas = BOM „Trafo box" pozicija.
- Prie kiekvieno laido: įtampa ir ilgis. Rytis 2026-10-08: VISI laidai 5 m („12V, 5.0 m"; spec
  `trafo_box.cable_len_m`, null - skaičiuoti |dx|+|dy| iki dėžės + 1 m atsargos). Iš dėžės - maitinimas „230V, ___ m".
- Laido išėjimas (Rytis 2026-10-07): iš bėgelio galo / raidės kojelės kampo pagal kliento standartą
  (EXTRA X / EXTRA / darbo valandos - `references/klientai/extra.md`).
  Nuleidimai tarpe tarp grupių: iš kairės grupės ateinantys - kairėje, iš dešinės - dešinėje, žemesnis išėjimas
  arčiau savo grupės, tarpai >= 7 pt (tolygiai, jei tarpas siauras) - laidai nesikerta. Laisvas galas (kai nenurodytas) parenkamas perrinkus derinius: nuleidimas nekerta kitų grupių, jų matmenų ir ašių grandinių,
  laidai nesutampa. Laidai nesikerta (artimesnis dėžei - aukštesnė eilė).
- v205 (Rytis 2026-10-14): PWM naudojamas ne visur - ant dėžės „PWM" rašomas TIK kai nurodyta (`"pwm": true` arba
  užsakyme „+ PWM" / potenciometras), kitaip tik „RAL ...".
- spec: `"trafo_box": {"voltage": "12V", "x": <mm>, "reserve_m": 1.0, "mains": "230V", "mains_len": "___ m"}`;
  `"trafo_box": false` - senas režimas (atskiri laidų išėjimai). BOM „Trafo box" eilutė užpildoma automatiškai
  (RAL rėmo spalva, laidų ilgiai).



## (iš SKILL.md v78) Daugialapis dokumentas (v10)
- Kiekvienas lapas - atskiras spec; `"sheet": "3 / 18"` įrašomas į antraštės SHEET langelį (lapas_core ir folded modulis).
- Ne-iškabų pozicijos (back plate, spauda, plėvelės, portalas) - tuo pačiu stiliumi per `lapas_core`
  (rėmelis, vientisa apatinė juosta, BOM / MAIN DATA / antraštė); pirmas juostos blokas - tipinis pjūvis arba MATERIAL.
- Grupė už raidžių (pvz. P00 3 mm apskritimas): `{"behind": true, "no_rails": true, "depth_mm": 3}`;
  kliento faile apskritimas apkerpamas raidėmis, kad nebūtų atpažintas kaip plokštė (6+3).
- Folded: `"element_colors": true` - elementai savo kliento spalva; `"element_return": {"0.6,0.8,0.3": "6039"}`
  - šonų RAL pagal kliento spalvą (suapvalinta 0,1); elementas ant kito elemento 3D - virš jo.



### (iš SKILL.md v84) Kiti produktai (dar neįgyvendinta)
Raidės tiesiai ant sienos (D3.2 / D11), pylonai, šviesdėžės, plokščios iškabos. Stilius -
`references/stilius.md`; konstrukciją klausti.



## (iš SKILL.md v85) Laidai - bėgelių lapas
- **LAIDAS NEKERTA MATMENŲ (v51, Rytis 2026-10-09):** laido trasa niekada nekerta ir neuždengia matmenų linijų,
  užrašų, išvadinių ir ausėlių; jei aukštyn kerta matmenis - patraukti į šoną: `"out": "left"|"right"` (priekio vaizdo
  kryptimi; galiniame veidrodiniame - priešingai), ašių grandinė automatiškai pereina į kitą pusę. Patikrinti PNG.
- **Laidas iš raidės (v50, Rytis 2026-10-09, Joker):** jei užsakyme laidas išeina iš raidės, ne iš bėgelio -
  `"cable": {"from": "letter", "x_pt": <kliento pt>, "out": "up"|"left"|"right"}`: D11 raidės gale **VISADA VIRŠ
  RĖMO** - tarp raidės viršaus ir viršutinio bėgelio, raidės VIDURYJE (x), NIEKADA po rėmu (v52, Rytis 2026-10-09);
  siaurai juostai mažinamas atstumas iki kontūro / bėgelio. Trasa: `up` (NUMATYTA, Rytis v53 - vienodai visuose komplekto lapuose) - aukštyn už matmenų ir į šoną (matmens
  tekstas pasitraukia), `left/right` - horizontaliai virš bėgelio į šoną. **Trafo box be „PWM"**, kai trafo modelis dar nežinomas (patikslinamas suskaičiavus LED):
  `"trafo_box": {"label": "RAL 8014"}`, BOM „Trafo box - model after LED calc.".
- **Laido išvestis (Rytis patvirtino):** kai naudojamas rėmas - laidas išeina iš BĖGELIO GALO nurodytoje pusėje
  (artimiausias horizontalaus bėgelio galas kliento piktogramai). Žymima vingiuota laido imitacija + raudonas
  el. žaibas + prierašas su įtampa ir ilgiu („12V, 2 m" / „220V, 5 m"; įtampa nenurodyta - „___ V").
  Rodoma TIK galiniame vaizde (priekio vaizde - ne). Laidas (Rytis patvirtino 2026-10-07): taškas bėgelio gale
  (matosi, kad išeina iš profilio galo) -> tiesiai už raidžių ribos -> žemyn UŽ vaizdo ribų -> vingiuota uodega po
  savo grupe + žaibas + prierašas; su matmenimis nesimaišo; tos pusės bėgelių ašių grandinė perkeliama į kitą pusę. Be rėmo - D11 išvestis raidės gale. Spec:
  `"cable_exits": [{"pt": [x, y] (kliento PDF pt), "voltage": "12V", "label": "2 m"}]`; BOM eilutė.
