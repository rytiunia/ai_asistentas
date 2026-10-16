# TEST „Bandymas" L 3500 - P6 ant FOLDED fono 3900 x 1000 x 40 (v319, Rytis 2026-10-16: „duok testą kaip ant folded plate P6")
Bandymas_folded_client.pdf - fonas (RAL 9005) + raidės iš ../bandymas_3500 (centre).
    python3 ../../braizyti_lapa.py spec.json TEST_Bandymas_folded.pdf                 # lapas (P6 ant folded)
    python3 ../../folded_dxf.py 3900 1000 flat.dxf 40                                   # išklotinė 3976 x 1076 (v173)
    python3 ../../p6_dxf.py Bandymas_folded_client.pdf dxf --scale 1.4077823 --fill 1,1,1 --rails-json axes.json \
            --folded --no-letters --prefix TEST_Bandymas_folded --cable bottom          # raidės: D3.2 forma, Ø8 SKYLUTĖS
    python3 folded_test.py                                                              # vientisas DXF
axes.json - ašys iš ../bandymas_3500/rails.json (tik horizontalios, separate). Laukiama: D3.2 31 (kaip ant rėmo: 4 / y 3),
drenažas Ø8 skylutės 14 (ne puslankiai), ant fono tos pačios skylės (LETTER_FIX_D3.2 / HOLE_D11_CABLE / DRAIN_D8).
v321: folded_test.py daro visą eigą; Ø11 laido skylė fono kairėje briaunoje 15 mm nuo lenkimo linijos ir 15 mm nuo viršaus
(išklotinėje x 23, y 1023); BOM 8 „per production / holes = letter back"; test_p6.py tikrina skylių atitikimą 1:1.
