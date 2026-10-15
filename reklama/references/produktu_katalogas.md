# Produktų katalogas - TIKSLŪS RAKTAŽODŽIAI užklausoms (v266, Rytis 2026-10-15)

Tikslas: užklausoje parašius raktažodį, iškart paleidžiamas TEISINGAS (naujausias, patvirtintas) generatorius ir etalonas, be
netikslumų ir be senų / klaidingų variantų. `scripts/ziniu_paieska.py` šį katalogą rodo pirmą.

**Užklausos forma:** `<raktažodis> <matmenys> <gylis> <spalvos> [klientas]` + kliento failas (PDF / DXF / AI).
Pvz.: `P6 ant folded pl., 2000x600, 40mm, RAL9010, SPAR` arba `dvipusė šviesdėžė nuo fasado 800x300x100, RAL9010, kojos NCS S 8010-R90B`.

## A. PARUOŠTA (>= 90 % be papildomų patikslinimų) - pakanka raktažodžio + įvesties

| Raktažodis (tiksliai) | Generatorius | Šablonas (spec) | Etalonas / testas | Būtina įvestis |
|---|---|---|---|---|
| `P6 ant folded pl.` (taip pat `5S ant folded pl.`, `P6+foil ant folded pl.`) | `scripts/braizyti_lapa.py` | `assets/spec_pavyzdys.json` (stačiakampis), `assets/spec_extra.json` (ne stačiakampis) | `assets/etalonai/SPAR_225960_komplektas_18_lapu.pdf` | kliento failas, fono matmuo, gylis, priekio variantas (5S / P6 / P6+foil / P6 color), RAL |
| `folded plate + lipdukai` (folded plokštė RAL + pjaustyta plėvelė, kelios plokštės - po lapą; pvz. Joker eskelokk) | `scripts/folded_vinyl.py` | `scripts/projektai/brandfactory_226057_joker/spec_226057.json` (`panels` su `rect` pt kliento PDF, `bg_fill`, `vinyl` - spalva -> ORACAL kodas) | `scripts/projektai/brandfactory_226057_joker/ALT0000_Order_226057.pdf` (BF Order 226057, v283) | kliento PDF (vektorinė grafika), plokščių W x H, gylis, plokštės RAL / dažymas, plėvelių kodai (kiekvienai spalvai), kiekis, tvirtinimas |
| `folded išklotinė <W>x<H>x<D>` | `scripts/folded_dxf.py` | - | `assets/etalonai/folded_1000x1000x40_isklotine_gamyba.dxf` (PATVIRTINTA 10-13) | W x H x gylis, storis |
| `P6 ant bėgelių` (U bėgeliai + ausėlės / statmenys) | `scripts/braizyti_begeliai.py` | `assets/spec_begeliai_extra.json`, `spec_begeliai_extra_1800.json`, `spec_coop_prix.json`, `spec_matkroken.json` | `EXTRA_225923_begeliai_P6-3_1-25.pdf`, `EXTRA_FAS1800_begeliai_auseles_1-50.pdf`, `COOP_PRIX_begeliai_1-20.pdf`, `MATKROKEN_begeliai_1-10.pdf`, `KIWI_226023_komplektas_3_lapai.pdf` | kliento failas, raidžių aukštis / plotis, gylis, priekio variantas, RAL, bėgelio spalva |
| `mišrūs priekiai ant U bėgelių` (pvz. `5S color + P6+foil ant U`; viena iškaba, grupės su skirtingais priekiais / spalvomis, U 30x30x2 be ausėlių) | `scripts/braizyti_begeliai.py` | `assets/spec_misrus_priekiai_U.json` (grupės `"front"`, `"rail_ral"`, `"ears": false`; `"layout": "rows"`, `"view_scale"`, `"view_yaw": 22, "view_pitch": 12`) | `assets/etalonai/BF_226030_Securitas_misrus_priekiai_5S_P6_ant_U.pdf` (BrandFactory Order 226030, v276-v281) | kliento failas, kurios grupės kokio priekio (5S / 5S color / P6 / P6+foil) ir spalvos, šonų / dugnų spalvos, rėmo spalva, maitinimas (iš kurio bėgelio laidai, trafo box), kiekis |
| `P6+3 ant plokštės` | `scripts/braizyti_begeliai.py` (`plate`) | `assets/spec_extra.json` | `extra_X_tvirtinimas_rems_asis.pdf`, `EXTRA_lygiagretainis_1-20.pdf` | kaip aukščiau + plokštės forma / spalva |
| `Z rėmas` (EXTRA Z frame) | `scripts/braizyti_begeliai.py` | `assets/spec_extra_zframe.json`, `spec_extra_zframe_1800.json` | `EXTRA_Z_frame_1000H100.pdf`, `EXTRA_Z_frame_1800U80.pdf` | aukštis, profilis |
| `P6 dxf` (CNC, D3.2 / D11 skylės) | `scripts/p6_dxf.py` | - | `assets/etalonai/extra_darbiniai_DXF_pateikimas.pdf` | kliento failas, mastelis, laido pusė (top / bottom) |
| `dvipusė šviesdėžė nuo fasado <W>x<H>x<D>` (5S stiklas, kojos su uždengimu) | `scripts/sviesdeze.py` | `scripts/projektai/bnskilte_3295_danbolig/spec_DB-0001.json` (naujausias: kojos per galinį statmenį `"leg_in": 0, "leg_chamfer": 90`, `"psu": "plate"`), `assets/spec_sviesdeze_700x370_kojos.json` | `scripts/projektai/sviesdeze_700x370_kojos/`, `bnskilte_3295_danbolig/` (DB-0001), `assets/etalonai/sviesdeze_dvipuse_kojos_zemesnes.pdf` | W x H x gylis, tarpas iki pado, korpuso / kojų spalvos, grafika / logotipas, maitinimas (230 V + PSU ant pado / be PSU) |
| `P10_lightbox_doublesided <W>x<H>x<D>` (Alu padėklai, iškištas stiklas) | `scripts/p10_lightbox_doublesided.py` | `scripts/projektai/p10_lightbox_doublesided_test/spec.json`, `spec_B.json` | `TEST_P10_lightbox_doublesided_B.pdf` (PATVIRTINTA v226; ! 2 eilės išdėstymas pagal taisyklę 26 - TOP VIEW po FRONT A, didelis EXPLODED - dar neperkeltas, perkelti prieš pirmą užsakymą) | W x H x gylis, logotipas, spalvos, kojų variantas (A / B) |
| `plėvelė sunaudojimas` / pjaustymo failas | `scripts/plevele.py`, `scripts/pleveles.py` | - | `scripts/projektai/plevele_test/` | plėvelės kodai, grafika |
| `Patvirtinta, ALT<nnnn>_<MM.DD>_RS` | gamybos paketas | - | `references/patvirtinimas.md` | patvirtintas lapas |

Klientų etalonai (kliento raktažodis + produktas): **SPAR / BrandFactory** - `etalonas_spar_225960.md`; **KIWI** - `etalonas_kiwi_226023.md`;
**EXTRA**, **Clas Ohlson**, **OKQ8 / Skyltkoncept**, **BN Skilte** - `references/klientai/*.md`.

## B. DAR NE 90 % - generatorius / aprašas yra, bet kiekvienam užsakymui reikia patikslinimų (klausti prieš braižant)

| Raktažodis | Kas yra | Ko dažniausiai trūksta |
|---|---|---|
| `P10 raidės ant akrilinio rėmo` | `braizyti_begeliai.py` `"front": "P10", "mounting": "acrylic"`, `references/moduliai_p10_raides.md` | LED griovelio gylis, laidų išvestis, smeigių vietos tikrinti akimis |
| `P10 raidės be bėgio` (blokinė, ilgasriegiai + šablonas) | `braizyti_begeliai.py` `"mounting": "none"`, etalonas `P10_be_begio_ilgasriegiai_danbolig_Rytis.pdf` | ilgasriegio dydis / ilgis (klientui), maitinimas |
| `P10_lightbox_singlesided` | `scripts/p10_lightbox_singlesided.py`, `references/moduliai_p10_lightbox_singlesided.md` | laido anga (y, Ø, įvorė), LED (gamyboje) |
| `pylonas / pilonas` | `references/moduliai_pilonai.md`, projekto kodas `thales_d059422` | konstrukcija, pamatas, statika - kiekvienam atskirai |
| `PVC banner / tentinė šviesdėžė`, `termoformavimas`, `flag sign / pendant` | tik aprašai (`moduliai_pvc_banner.md`, `moduliai_termoformavimas.md`, `moduliai_pendant.md`) | generatoriaus nėra - konstrukciją klausti |
| `P6 ant L profilių` (kaip VOLVO BILB26-01001) | `braizyti_begeliai.py` `"mounting": "l_hang"`, `p6_lhang.py`, etalonas `BILB26-01001_P6_ant_L_profiliu.pdf` | fasado L tvirtinimas prie fasado; pirmas atvejis EXLA26-01001 - laukia Ryčio patvirtinimo |
| `P6 palaidos raidės` (atskiros, skylės dugne + šablonas) | `braizyti_begeliai.py` `"mounting": "none"` + `p6_dxf.py --rails-json` | gylis, maitinimas; skylės lape = DXF = šablonas (v268) |
| `P1 nešviečiančios`, `stogo iškaba`, `□ profilis` | `references/moduliai_kiti.md` | po 1 atvejį - klausti |

## C. SENI / KLAIDINGI PAVADINIMAI - NENAUDOTI (užklausoje pasitaikius - versti į naują)

| Senas | Naujas |
|---|---|
| `P6_3mm`, `P6_3mm+foil` | `5S`, `5S+foil` (v210) |
| `P6_8mm`, `P6_8mm+foil`, `P6_8mm color` | `P6`, `P6+foil`, `P6 color` (v233) |
| `P10_lightbox` | `P10_lightbox_doublesided` (v227); NEPAINIOTI su `P10 raidės` |
| `iskabu-techninis-lapas` (senas skill) | `reklama` (GitHub `rytiunia/ai_asistentas/reklama`) - paskyros kopijos NENAUDOTI |
| šviesdėžės varžtai „3 vnt. kraštinei" (v139), „kas 150" (v254) | folded plate formulė: 50 nuo kraštų, ~300 (v258) |
| šviesdėžės kojos įlenda į dėžę 53 / galas 50° (v144) kaip numatytas | Rytis 2026-10-15: kojos PER galinį statmenį (`"leg_in": 0`), kai nenurodyta kitaip |
| LED / PSU modeliai lape (Kaisen, KPS, W, lm) | tik „LED" / „PSU" (v262) |
| P6 DXF senas K 0.44 / R2 / BD 3.476 | dabartinis `p6_dxf.py` (žr. SKILL „P6 DXF") |
