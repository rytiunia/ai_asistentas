# SPAR order 225960 - PATVIRTINTA, ALT8901_10.16_RS (2026-10-16)

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
