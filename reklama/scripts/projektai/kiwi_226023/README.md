# KIWI order 226023 (BrandFactory, 2026-10-13) - KIWI ETALONAS (`references/etalonas_kiwi_226023.md`)

Originalas - Tollnes 225948 / ALT8858 (3 psl.): VISA informacija, lentelės ir aprašymai perkelti iš jo, keičiamas tik stilius.
Rezultatas: `assets/etalonai/KIWI_226023_komplektas_3_lapai.pdf` (3 lapai).

1. `python3 mkclient.py` -> client_clean.pdf (kliento PDF p1 -> grupės, decal, pilki bėgeliai; kelias skripte).
2. `python3 mkspec.py client_clean.pdf <ALT8858.pdf>` -> spec1.json / spec2.json (`rails` + `fit_plates`, `bom_cols`,
   `section_labels`, `callouts`, `cable_exits`, `led_fragment` su `rules_py` = `led_rules.py`, `texts` = `frag_gost.TEXT`).
3. `python3 ../../braizyti_begeliai.py spec1.json s1.pdf`, `spec2.json s2.pdf` (2 praėjimai - BB_AUTO automatiškai).
4. `python3 frag_gost.py`-> `prep_all(ALT8858, org_gost.pdf)`; `python3 lanterne.py s3.pdf <ALT8858.pdf> org_gost.pdf`.
5. Sujungti s1, s2, s3 -> `lapas_core.pdf_fix_fonts` -> `qpdf --object-streams=disable` -> `patikra_lapas.py` (0) ->
   `Drawing_KIWI order 226023.pdf` NAS užsakymo aplanke.
`led_sheets.py` - senas (atskiri LED lapai), NENAUDOJAMAS.
