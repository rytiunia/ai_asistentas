# Bandymas „Bandymas / antras" (v74, 2026-10-10) - 2 eilutės ant vieno rėmo, 7860 x 2590 mm, P6_8mm, U30 RAL 9016
Kliento failas 882b0462-aa.pdf (be bėgelių) -> client_rails.pdf: pridėti pilki bėgeliai (2 per eilutę, ašis 26 mm nuo x-aukščio
krašto) + 2 jungiamieji statmenys tarpe po „a". spec.json: merge_rows, trafo_box false, laidas apačioje kairėje.
python3 ../../braizyti_begeliai.py spec.json out.pdf
Laukiama: 4 bėgeliai 7645 / 7577 / 4343 / 4258, statmenys 5 + 3, jungiamieji 2 x 525, 6 strypai, 2 perspėjimai „jungti iš 2".
v75: spec_auto.json - `auto_frame` iš 882b0462-aa.pdf (be bėgelių); Rytio pavyzdys aa_remas_rytis.pdf (veidrodinis galinis vaizdas).
python3 ../../braizyti_begeliai.py spec_auto.json out_auto.pdf  -> bėgeliai per štrichų centrus, statmenys 3 + 2 per abi eilutes.
v76: spec_BB.json - LIETUVA / TĖVYNE MŪSŲ (baltos raidės, akcentai), 6 strypai, 2 statmenys per abi eilutes.
v83: spec_wide.json - kvadratas + I + apskritimas gale: rėmas iki raidės galo, ausėlės išsikiša už raidės (4 vnt.).
v85: P6 DXF BB - RAILS_JSON=rails_BB.json ../../braizyti_begeliai.py spec_BB.json x.pdf; ../../p6_dxf.py db01b4b7-BB.pdf dxf --scale 2.8346 --rails-json rails_BB.json --names LIETUVATEtVYNEMUbSU
v106: spec.json (client_rails.pdf) - kliento ašys 82-86 mm nuo tvirtinimo ploto centro -> rėmas perdaromas pagal skill (= spec_auto); kliento rėmui - "client_frame": true.
