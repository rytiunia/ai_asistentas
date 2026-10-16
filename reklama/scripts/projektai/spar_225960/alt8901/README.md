# SPAR order 225960 - PATVIRTINTA, ALT8901_10.16_RS (2026-10-16)

## v316 - VISKAS PERGENERUOTA DABARTINĖMIS TAISYKLĖMIS (Rytis: „blankas naudojamas senas ... naudoti pačią naujausią skill")
Patvirtintas `Drawing_SPAR_order_225960_patvirtintas.pdf` - tik duomenys. Eiga (iš šio katalogo):

| Žingsnis | Skriptas | Rezultatas |
|---|---|---|
| Raidžių lapai 1-5, 15-17 | `lapai.py` (braizyti_begeliai; rėmas / ausėlės `remas_is_lapo.py`, raidės `svarus_lapas.py`, seni `../spec/*.json`) | `sk/<k>.pdf`, `sk/rails_bb_<k>.json` |
| Back plate 7-9 | `folded_vinyl.py sk/spec_bp7.json sk/bp7.pdf`, `... sk/spec_bp89.json sk/bp89.pdf` | `sk/bp7.pdf`, `sk/bp89.pdf` + flat / vinyl DXF |
| Portalas 6, grafika 10-14, FRISK 18 | `kiti_lapai.py` (lapas_core + layout_engine; 18 - `braizyti_lapa.py`) | `sk/s06..s14, s18*.pdf` |
| Rinkinys | `rinkinys.py` (merge_sheets -> pdf_fix_fonts -> qpdf) | `out/ALT8901_10.16_RS_SPAR_order_225960.pdf` (18 lapų) |
| DXF | `dxf_rinkinys.py` (p6_dxf `--rails-json sk/rails_bb_<k>.json`, dxf_combine, kiti_dxf, frisk_dxf) | `out/*.dxf` (14) |
| LED | `led_visi.py` | `out/ALT8901_10.16_RS_SPAR_order_225960_LED.pdf` |

Patikra: `patikra_lapas.py` (kiekvienas lapas ir rinkinys) = 0, `patikra_corel.py` = 0, `patikra_dxf.py` = 0.
`order_no.py` (v310, tik ORDER NO. keitimas) - ATŠAUKTAS v316, paliktas istorijai.

## Senesnė eiga (v308 / v310 - ATŠAUKTA)

Šaltinis - patvirtintas Corel PDF `Drawing_SPAR_order_225960_patvirtintas.pdf` (18 lapų, Ryčio Corel taisymai 2026-10-08).
Kliento valytų failų (`/home/claude/w/sk/*_client.pdf`) repo nėra - viskas imama iš patvirtinto lapo.

| Žingsnis | Skriptas | Rezultatas |
|---|---|---|
| Dokumentas | `order_no.py` (v310) | `out/ALT8901_10.16_RS_SPAR_order_225960.pdf` - tik ORDER NO.: originalo šrifto glifai turinio sraute, qpdf; žodžiai / objektai / šriftai tie patys, `patikra_corel.py` = 0 |
| Rėmas | `remas_is_lapo.py` + `cfg.json` | `rails_<k>.json` - bėgeliai ir ausėlės iš FRONT VIEW (rėmo / ausėlių spalva), mastelis iš bendro pločio |
| Raidės | `svarus_lapas.py` | `svarus_<k>.pdf` - tik raidžių kontūrai (logotipai - išorinis kontūras, FRAME JOINT / žymekliai - `exclude_pt`, plokštės - `plates`) |
| P6 DXF | `dxf_visi.py` (+ `plokste_dxf.py` KAFFEPAUSE ACM apskritimas) | `out/<ALT>_s01..s17.dxf` |
| Kiti DXF | `kiti_dxf.py` (back plate 7-9, dekoras 13, portalo buferis 6), `frisk_dxf.py` (18) | `out/<ALT>_s06/07/08/09/13/18*.dxf` |
| LED | `led_visi.py` (merge_sheets -> pdf_fix_fonts -> qpdf) | `out/<ALT>_SPAR_order_225960_LED.pdf` (9 lapai) |

DXF NĖRA: 10 / 14 (spauda - originalūs failai), 11 / 12 (plėvelės ruloniniai stačiakampiai 5000 x 1220 / 23000 x 1220),
6 portalo plexi / galas / PVC dugnas (lape dalijimo nėra - klausti).
