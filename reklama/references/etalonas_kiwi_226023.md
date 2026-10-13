# ETALONAS: KIWI order 226023 KIWI 640 BYGNES (BrandFactory, 3 lapai) - Rytis patvirtino 2026-10-13

**Statusas:** VISŲ KIWI dokumentų ETALONAS iki atskiro Ryčio nurodymo. Naujas KIWI užsakymas (raidės / logotipas ant
rėmo, 7-23, Lanterne / kolona) daromas TIKSLIAI taip: tas pats lapų išdėstymas, lentelės, LED vaizdas, žymėjimas,
patikra. Keičiasi tik produkto turinys (matmenys, kiekiai, rėmas, LED - iš to užsakymo originalo / kliento PDF).
Bendras stilius - kaip visur (`references/stilius.md`, `etalonas_spar_225960.md`); šis etalonas papildo KIWI specifika.

- Lapai: `assets/etalonai/KIWI_226023_komplektas_3_lapai.pdf`
  (NAS: `/Volumes/dizainas/RYTIS/DARBAI/uzsienio reklama/Brandfactory/KIWI/KIWI order 226023/Drawing_Order 226023 KIWI 640 BYGNES.pdf`).
- Kodas: `scripts/projektai/kiwi_226023/` (README.md - eiga), generatorius `scripts/braizyti_begeliai.py` + `lanterne.py`.
- Originalas, iš kurio perkelta informacija: Tollnes 225948 / ALT8858 (3 psl.: KIWI 3362, 7-23 2037, Lanterne 6800).

## 1. Lapai

| Lapas | Gaminys | Skriptas | Kuo etaloninis |
|---|---|---|---|
| 1 / 3 | KIWI minipris 3362 x 1095 (3 vnt.) | `braizyti_begeliai` + spec1 (`mkspec.py`) | rėmas 40x20x2 RAL 7024 „DIVIDED", jungtis 15x15x2, LED miniatiūros P130 + P65, 3 laidai 230V virš rėmo, angliška lentelė |
| 2 / 3 | 7-23 2037 x 709 (3 vnt.) | `braizyti_begeliai` + spec2 | įstrižas rėmas (554 diag.), LED P130 lens miniatiūros, lentelė LIETUVIŠKAI - kaip originale |
| 3 / 3 | Lanterne 6800 x 500 x 100, RAL 6018 | `lanterne.py` | FRONT / SIDE / REAR + originalo fragmentas (3D, A, B), SECTION C-C juostoje, Parts List su FINISH |

## 2. Raidžių / logotipo lapas (1, 2)
- **Išdėstymas (ketvirčiai):** FRONT VIEW (+ SIDE VIEW dešinėje) - kairė viršus, REAR VIEW (MIRRORED) - dešinė viršus,
  LED INSTALLATION - kairė apačia, 3D VIEW - dešinė apačia. Kiekvienas vaizdas centruojamas savo ketvirtyje
  (spec `led_fragment` įjungia šį išdėstymą).
- **Juosta:** PROFILE ON RAILS - TYPICAL SECTION (□ profilis pagal tikrą pjūvį: 40x20 rodomas 40 x 20, ne 40 x 40) |
  originalo lentelė (`bom_cols`, `bom_title`: „MATERIALS TO MAKE ONE UNIT" arba originalo kalba) su spalvų langeliais
  `#RRGGBB` | MAIN DATA | REVISIONS + antraštė.
- **Rėmas:** tik originalo bėgeliai (`rails` su `len`), fitting plates originalo vietose (`fit_plates`), `client_frame: true`,
  `ears.enabled: false`, `frame_round_mm: 0`; galinio vaizdo ilgiai „3219 (□40x20x2)", žymos „740 vert." / „554 diag.";
  žymos toje pačioje vertikalėje sujungiamos („226 / 130 vert."); padalijimas - `joints` „DIVIDED".
- **Ausėlės (fitting plates 40 x 75 Ø8):** skylė originalo vietoje, plokštelė VISADA privirinta prie bėgelio (v179) - jokių ausėlių ore.
- **Laido išvestys:** TIK originalo LED brėžinio vietose (`cable_exits[].point`, `up_mm`, `side`), raudonas laidas į viršų
  už vaizdo ribų, užrašas „230V, ~3 m". Vienas variantas - jokio „bėgelio galo" papildomo.
- **LED INSTALLATION:** originalas PERBRAIŽOMAS (`scripts/led_mini.py`, spec `led_fragment.rules_py` -> projekto
  `led_rules.py` spalvų taisyklės): kontūrai hairline, moduliai - MINIATIŪROS (korpusas + LED / lęšis, kryptis iš originalo),
  aprėptis - šviesūs žali apskritimai, trafai - pilki stačiakampiai su „100W / 18W", laidai raudoni 0,9 pt, kiekiai raidėse
  žali, legenda „LED Installation:" su miniatiūromis - originalo tekstu (GOST). Kiekis po perbraižymo tikrinamas su originalu.
- **Balionai:** TIK už vaizdo ribų (`balloon_auto(..., avoid=[vaizdo dėžė])`), 2 praėjimai; pjūvio numeriai pagal originalo
  BOM (`section_labels`); išvadinė gali kirsti tik VIENĄ matmens liniją statmenai, kai objektas apsuptas matmenų.

## 3. Lanterne / kolonos lapas (3)
- Kairėje FRONT / SIDE / REAR VIEW (1:40) su matmenimis ir užrašais („Connection point", „Backside plate connect point",
  „Cover with adjustable position"), „+1,5m ~230V El. Output" laidas virš matmenų; pjūvio plokštuma C - REAR VIEW.
- Dešinėje - ORIGINALO fragmentas (3D, B (1:10), A (1:10)) `place_pdf(..., under=True)`, Arial užrašai pašalinti ir
  perrašyti GOST (`frag_gost.py`), linijos -> hairline (`gost_frag.hairline`). Savų DETAIL A / B NEDAROMA.
- Parts List: POS | Part Number | Description | Qty | FINISH - originalo aprašai lentelėje, FINISH = detalės RAL
  (spalvotas langelis „RAL 6018"); LED / trafo / išvestis - pos. 5 eilutėse.
- Juostoje SECTION C-C (1:10) su FACADE SIDE.

## 4. Privaloma prieš atiduodant
1. GOST Common visur (ir fragmentuose); `lapas_core.pdf_fix_fonts`; `qpdf --object-streams=disable` (CorelDRAW).
2. `python3 scripts/patikra_lapas.py lapas.pdf` - 0 klaidų; `patikra_sriftai.py`.
3. Visos objektų linijos hairline; matmenys nesugrūsti, išvadinės nekerta skaičių / fono / kitų išvadinių.
4. Failas: `Drawing_Order NNNNNN <pavadinimas>.pdf` užsakymo aplanke NAS; ORDER NO. `ALT0000_MM.DD_RS`, kol ALT nežinomas.
