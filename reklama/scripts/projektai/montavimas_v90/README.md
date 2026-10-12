# v90 bandymai: P6 priekiai ir montavimo būdai (2026-10-11)
Kliento failas - `../p6_dxf_test/TESTAS.pdf` (1 pt = 1 mm, `scale` 2.8346), spec iš programos bandymo RK-2610-001.
```
python3 ../../braizyti_begeliai.py spec_ears.json out_ears.pdf          # standartas: ausėlės
python3 ../../braizyti_begeliai.py spec_brackets.json out_brk.pdf       # U laikikliai: bėgeliai įprastai, 5 vnt. per raidžių centrus (T, E, T stiebai, A, S vidurys), H 1094 (rėmas 1086 + 2 + 2 x 3), 3 x D6, plienas, 2 lapas
RAILS_JSON=rj_none.json python3 ../../braizyti_begeliai.py spec_none.json out_none.pdf   # atskiros raidės: be rėmo BOM / MAIN DATA / šono matmens, laidų linija y241
python3 ../../p6_dxf.py ../p6_dxf_test/TESTAS.pdf dxf_none --scale 2.8346 --names TESTAS --no-letters --rails-json rj_none.json
#   -> SEP..._laidas_linija.dxf: skylės ant ašių, be 3_REMAS, D11 linija y1090 nuo apačios
python3 ../../braizyti_begeliai.py spec_20mm_foil.json out_20.pdf       # 20 mm balta + plėvelė: frezuota, svoris ~147 kg
python3 ../../braizyti_begeliai.py spec_8mm_color.json out_8c.pdf       # 8 mm spalvota: kantelis spalvotas
```
Taisyklės - `references/moduliai_montavimas.md`, SKILL.md „P6 priekio variantai".
