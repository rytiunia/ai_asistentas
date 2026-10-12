# Folded plate moduliai (perkelta iš SKILL.md v71, taisyklės nepakeistos)

### Folded plate - bendrinės taisyklės (VISI folded užsakymai, bet koks klientas)
**Konstrukcija ir lenkimas (STEP `assets/konstrukcijos/lankstinys_1prie1.step`):** Al 2 mm (lakštas 2000x4000 - Heliopolis, kiti formatai ir L profilių 6 m strypai - `references/medziagos.md`, v73),
gylis pagal užsakymą (dažniausiai 40), 4 užlenkimai 90° į galą, vidinis R2, K 0.44 (PRIELAIDA - Inventor
numatytasis; lape „assumed"), BA 4.524, BD 3.476 / 90°, flanšas iki lenkimo ašies 38.26 (gylis 40). ŠONINIAI flanšai
įsilenkia TARP viršutinio ir apatinio (aukštis H - 2t - 2x0.1 = H - 4.2), kampų išpjova pagal STEP.
Išklotinė = (L + 2·gylis - 2·BD) x (H + 2·gylis - 2·BD); max ilgis - lakšto 4000 - 2x10 paraštė (praktiškai dalis <= 3900).
- **L profilis 30x30x2 Alu** (Rytis patvirtino): ilgis = tvirtinamos kraštinės ilgis - 50 mm
  (po 25 mm nuo galų), pagal nutylėjimą 2 vnt. (viršus + apačia). Ilgis VISADA galiniame vaizde
  (`25 | ilgis | 25` + bendras), BOM - bėginiais metrais `2 x 2.25 = 4.50 m` (`{L_QTY} x {L_LEN_M} = {L_TOTAL_M} m`).
- **Fonas -> L: varžtai DIN 7504 N 4.2x16 T20 (St. gehärtet)**: 50 mm nuo kraštų, žingsnis ~300 mm,
  tolygiai: n = round((kraštinė - 100) / 300). Galiniame vaizde ašys ir `50 | n x žingsnis = ilgis | 50`,
  BOM - bendras kiekis (`14 pcs. (7/L)`).
- **Fono tvirtinimo skylės (v37, Rytis 2026-10-09):** Ø3.2 viršutinėje ir apatinėje užlenktoje briaunoje, ašis **7 mm nuo
  briaunos krašto**; išklotinėje - skylės ir grandinė `50 | n x žingsnis | 50`, DETAIL A - varžto ašis 7 nuo krašto.
- **Lūžtantis fasadas (kelios plokštumos, pvz. Clas Ohlson Horten 3, Rytis 2026-10-09):**
  * ORIENTACIJA: kliento plano eskizas gali būti nupieštas ne iš gatvės pusės - PATIKRINTI ir lape viską rašyti
    ŽIŪRINT IŠ PRIEKIO (iš kairės į dešinę); dalių numeracija, lūžiai, logotipo dalis, laidas - skaičiuojami iš
    plokštumų sąrašo, ne ranka. Neaišku - klausti.
  * Dalijimas pagal medžiagą: max dalis 3900; logotipas / raidės dedami ant VIENOS ištisinės dalies (centruojama
    po logotipu), likę ilgiai - pilnos dalys + likutis į IŠORINĮ kraštą; lūžyje dalys baigiasi.
  * Dalys - ATSKIRI segmentai be jungimo varžtų (jei klientas nenurodė kitaip).
  * KAMPAI NEPATEIKTI -> visos dalys standartinės su 90° šoniniais flanšais (nominalūs ilgiai), kampuose dalys
    susiliečia priekiniu kraštu; kampai lape tik informaciniai („sketch, not measured") + raudonas perspėjimas
    „gamybai reikalingi tikslūs fasado kampai". Kai kampai žinomi - kampo dalies priekis trumpinamas
    gylis·tan(α/2).
- **Kelios dalys vienoje plokštumoje (back plate didesnis už lakštą, pvz. OKQ8 3200x2400, Rytis 2026-10-09):**
  * Sandūra - GRAFIKOS / RAIDŽIŲ TARPE: didžiausio tarpo viduryje (apvalinti 5 mm), grafika ir raidės sandūros
    nekerta; kryptį (horizontali / vertikali) rinktis pagal tarpą ir lakštą, klientui nurodžius - jo vieta.
  * L 30x30x2 TIK viso skydo viršuje ir apačioje (kaip SPAR back plate etalone), ne kiekvienai daliai.
  * Sandūroje dalys sujungiamos per gretimus užlenkimus: Ø6 skylės, žingsnis ~500 PAGAL APKROVAS (lygūs tarpai,
    50 nuo galų, 20 nuo briaunos krašto), varžtai + veržlės (dydis - klausti, kol nepatvirtinta). DETAIL B -
    sandūros pjūvis. „PANEL JOINT" užrašas - tik už reklamos ribų.
  * Jei Rytis nurodo atskirus padėklus be jungimo (pvz. SPAR TYPE 670) - žr. „Folded iš kelių dalių - spec" žemiau.
- **Laidas folded fone (bendra):** TIK po raide - D11 raidės gale (>= 30 mm nuo kontūro, >= 20 nuo tvirtinimo
  skylių) -> už fono -> pro Ø11 skylę UŽLENKTOJE BRIAUNOJE (viršutinėje / apatinėje / ŠONINĖJE) kliento nurodytoje
  vietoje; matmuo iki skylės lape; ant fono išvesties niekada. Kurią briauną - pagal kliento failą / standartą.
- **Išklotinės ir DXF:** lape išklotinė su lenkimo ašimis, Ø3.2 skylėmis, grandinėmis; DXF -
  `scripts/folded_dxf.py PLOTIS AUKŠTIS out.dxf [GYLIS]` (R2, K0.44, 4 x 90°, šonai tarp viršaus ir apačios, Ø3.2 7
  nuo krašto); dalims su sandūra - `scripts/projektai/okq8_vaster/okq8.py: flat_dxf(fn, W, H, holes_top, holes_bot,
  bolts_top, bolts_bot)`. Sluoksniai: CUT / BEND_UP_90_R2 / HOLES_D3.2 / HOLES_D6_JOINT / HOLE_D11_CABLE /
  LETTER_FIX_POINTS / SHEET_2000x4000 / TEXT (ezdxf R2010). Išklotinė braižoma FACE OUT (vaizdas iš priekio).
- **NESTING - išklotinių išdėstymas lakšte (v37):** pirmiausia užpildomas lapo AUKŠTIS nuo krašto (dalys viena virš kitos), tik tada
  einama link lapo galo; CNC paraštė 10 mm. Pvz. 900 aukščio plokštė (išklotinė 973) - 2 juostos per
  2000 aukštį, ilgiausios dalys pirmos (`scripts/projektai/clasohlson_horten/sheet2.py`).
- **Atskiras išklotinių lapas** - tik jei prašoma; pagrindiniame dokumente vietoje išklotinių - 3D ant fasado.

#### Folded iš kelių dalių - spec ir lapas (v28, pirmas atvejis SPAR TYPE 670)
Pavyzdys `assets/spec_folded_2parts.json`, eiga `scripts/projektai/spar_type670/README.md`.
- **Kliento failas:** jei fonas nupieštas keliais užpildais (pvz. 1500 + 2100) - paruošti švarų failą su VIENU fono
  stačiakampiu (`mkclean.py`), kitaip skriptas ima tik didžiausią dalį. Jungčių x (mm nuo kairės) -> `"panel_joints"`.
- **Dalys (variantas „atskiri padėklai", jei nesujungiamos varžtais):** kiekviena dalis - atskiras folded padėklas su VISAIS 4 užlenkimais; L 30x30x2 viršus + apačia KIEKVIENAI
  daliai (ilgis = dalies plotis - 50), varžtai 50 nuo dalies kraštų kas ~300. BOM: `{PARTS}` (1500 + 2100), `{N_PARTS}`,
  `{L_LIST_M}` (`2 x 1.45 + 2 x 2.05`), `{S_PER}` (`6/8`). MAIN DATA: `"main_data_extra": [["Panel parts", "{N_PARTS} pcs.: {PARTS}"]]`.
- **Lape:** jungtis per foną - šviesus punktyras (priekis), sandūra su abiem užlenkimais (galas), linija 3D;
  dalių grandinė virš bendro pločio. **„PANEL JOINT" - TIK pastaba UŽ reklamos ribų** (virš priekio grandinių,
  virš galinio vaizdo varžtų grandinės) su išvadine - NIEKADA ant fasado ar raidžių.
- **Laidas (folded / box lid):** išeina TIK po raide - D11 raidės gale (`d11_mm`, raidė arčiausiai kliento išvesties,
  >= 30 mm nuo kontūro), už fono iki užlenktos briaunos (trasa ne per L: šone x = 12, kur L dar nėra), pro Ø11 skylę
  UŽLENKTOJE BRIAUNOJE kliento nurodytoje vietoje (`edge`: left/right/top/bottom, `edge_mm` - padėtis išilgai
  briaunos, matmuo lape) ir įtampa. Bet kur ant fono išvesties NEDĖTI. Spec:
  `"cable": {"d11_mm": [600, 160], "letter": "letter F", "edge": "left", "edge_mm": 29, "label": "12V, 3 m -> PSU (220V)"}`
  (senas `cable_exit` - tik suderinamumui). Laidas - 0,9 pt raudonas (`_cpoly`, VIEW_MODE hairline netaikomas);
  balionai 9 / 6 - priešingoje pusėje nei laidas.
- **DETAIL A pagal `front`:** `8mm` - plexi 8 mm (3 mm priekis ant šonų galo + 5 mm liežuvis šonų viduje, 45° štrichai),
  varžtas per šoną į liežuvį, PVC bortelio ir A/B balionų NĖRA; `3mm` - kaip anksčiau (PVC + A/B).
- 1:1 folded lapui - `scripts/projektai/spar_type670/one2one.py` (raidės + dalių kontūrai / dugnas -3 mm / L + D11).

### Folded plate + pjaustyta plėvelė (v42, pirmas atvejis OKQ8 Väster S)
Bendra visoms folded plokštėms su vinilo grafika (ORACAL, Avery, 3M ...):
- Lapas: FRONT su kliento grafika (plėvelės spalva), SIDE, REAR (L, Ø3.2 7 nuo krašto, sandūra jei yra),
  DETAIL A (briauna + plėvelė 1:2), DETAIL B (sandūra, jei yra), 3D (r3d); juostoje - pjūvis.
- BOM: plokštė (RAL), plėvelė (kodas spalvotame langelyje), L, varžtai, tvirtinimas į sieną „?".
- Atskirai: vinilo 1:1 PDF (sluoksniai: pjovimas / plokštės kontūras / sandūra) + išklotinių DXF.
- SPALVAS KLAUSTI (plokštės RAL ir plėvelės kodą) - kliento CMYK tik vaizdui.

### Folded / back plate + skaitmeninė SPAUDA (v56, pirmas atvejis SPAR 226004)
- Kliento grafika (JPG / PNG, ne mastelis) PRITRAUKIAMA prie plokštės matmens (W x H) BE IŠKRAIPYMO (cover: mastelis
  pagal ilgesnę pusę, perteklius apkerpamas per centrą, logotipas turi likti) - lape tikras vaizdas; jei proporcijos labai
  skiriasi - pastaba, kad galutinį spaudos failą W x H ruošia dizaineris.
- **SPAR back plate STANDARTAS (v58, Rytis): 2700 (plotis) x 2100 (aukštis), 2 dalys 1400 (viršus) + 700 (apačia) -
  NEPRIKLAUSOMAI nuo grafikos** (taip pat 2000 x 2100). Kliento standartinė sandūra viršesnė už „sandūrą grafikos tarpe".
- Spauda Gel'UV + laminatas ant priekio IR briaunų (BOM plotas (W+80) x (H+80)); plokštė po spauda - RAL 9005
  (etalonas 225960 lapas 7), jei nenurodyta kitaip.
- Dalis didesnė už lakštą -> sandūra horizontalioje linijoje, kurios NEKERTA objektai (foto - pvz. medžio lentų
  griovelis; tamsių eilučių analizė: % stulpelių, kuriuose linija kertama objekto, ~0), abi dalys telpa lakšte
  (išklotinės aukštis <= 1980). Jei švarios linijos tinkamame aukštyje nėra - artimiausia etalono proporcijai
  griovelio linija + pastaba "galutinė sandūra pagal spaudos failą". Toliau - „Kelios dalys vienoje plokštumoje" (L tik viršuje / apačioje, Ø6 ~500).
- Kodas: `scripts/projektai/spar_226004/backplate.py` (+ DXF TOP / BOTTOM).

### Kito profilio raidės ant folded (pvz. P8 special) - bendra
- Raidžių tvirtinimai (spaceriai, varžtai) TIK po raidėmis, niekada atvirame fone.
- Tvirtinimo skylės - pagal kliento profilio standartą (jei klientas turi proporcijų etaloną - pagal jį, žr. kliento
  failą); kitaip klausti. Laidas - „Laidas folded fone (bendra)".

### P6 raidės ant folded plokštės (įgyvendinta: `scripts/braizyti_lapa.py`)
Fonas, L, skylės, varžtai, išklotinės - „Folded plate - bendrinės taisyklės" (aukščiau). Čia - tik P6 raidžių dalis.
- **Fonas:** bet kokios formos kontūras iš kliento failo (stačiakampis, lygiagretainis ...).
  Ne stačiakampiui: kontūras, grandinė nuo aukščiausio taško, kraštinių ilgiai, kampas; galiniame vaizde
  aligned matmenys išilgai pasvirusių kraštų.
- **P6 tipinio pjūvio GRAFIKA - Rytio etalonas `assets/p6_profiliai.pdf`** (Rytis patvirtino 2026-10-07: naudoti jo
  grafiką, išlaikyti ≥90 %): geometrija perbraižoma vektoriškai iš etalono (`scripts/p6_ref.py`, `K.p6_reference`)
  CAD pjūvio taisyklėmis (ISO 128-50, Rytis patvirtino - hairline pjūvis „pradingsta"): pjaunami ploni lakštai
  (šonai, galas, bėgelis, folded plokštės pjūvis) UŽPILDYTI JUODAI su balta tarpo linija tarp gretimų; plexi -
  plonas 45° štrichavimas; matomi kontūrai 0,35 pt; BE spalvų; numeriai - balti balionai (ne juodi „blynai");
  varžtai - CAD žymėjimas (galvutė, kotas, sriegio linija, ašinė). Mazgo detalizacijos (apskritimų, 1/2/A/B,
  legendos) NĖRA. P6_3mm - bendrame žymėjime papildomai A (PVC juosta); P6_8mm - jokių papildomų žymų. 6 variantai - folded / U wallframe / square wallframe
  (`rail.type: "square"`) × plexi 3 mm / 8 mm. Ant viršaus tik gylio matmuo. Naujam variantui - Rytio etalono.
  Tik P6+3 ant plokštės (DETAIL A) lieka piešiamas `p6_typical(variant="plate")`.
- **Ausėlės tipiniame pjūvyje (Rytis patvirtino 2026-10-07):** jei užklausoje yra ausėlės - jos VISADA
  atvaizduojamos P6 ant bėgelių pjūvyje (L: kojelė U viduje ant rėmo vidaus flanšo, kojelė sienos plokštumoje
  į rėmo vidų, Ø skylė su ašine), balionas = BOM ausėlės pozicija (`p6_reference(..., ears=pos)`).
- **P6 sandara (tipinis pjūvis juostoje):** 5 fonas, 3 galas, 2 šonai, 1 plexi, 4 LED su laidu (priekio variantai - žr. „P6 priekio variantai");
  A - fitting PVC edge (klijuojamas STATMENAI plexi plokštumai, pjūvyje - juostelė po šonu, galu prie
  plexi), B - bolt (vertikaliai per šoną į PVC bortelį; niekas nekiša per stiklą). A ir B BOM - TIK P6_3mm
  (Rytis 2026-10-07: P6_8mm BOM A/B eilučių NĖRA; skriptas jas išmeta pagal `front`).
- **POS:** 1 priekis, A PVC, B bolt, 2 šonas, 3 galas, 4 LED, 5 folded fonas, 6 L, 7 tvirtinimas į
  sieną, 8 raidės tvirtinimas prie fono, 9 varžtas fonas-L.
- **BOM kiekiai:** face / back = `{PER_L} m / {A_FACE} m²`, return = `{PER_L} m / {A_RET} m²`
  (perimetras x gylis), PVC = `{PER_L} m`; `{L_SIZE} {L_QTY} {L_LEN} {L_TOTAL}`, `{S_SPEC} {S_MAT} {S_QTY} {S_PER}`.
