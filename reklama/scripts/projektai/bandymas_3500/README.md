# TEST „Bandymas" L 3500, P6 ant U 30x30x2 (v317, Rytis 2026-10-16)
Tikrina raidžių tvirtinimą pagal KVADRATO / TRIKAMPIO principą (suvestinė D2).
Bandymas_client.pdf - raidės iš ../p6_dxf_test/Bandymas_test_B.pdf (be kliento bėgelių; rėmas - auto_frame).
    python3 ../../braizyti_begeliai.py spec.json TEST_Bandymas_3500.pdf      # -> rails.json
    python3 ../../p6_dxf.py Bandymas_client.pdf dxf --scale 1.4077823 --rails-json rails.json --no-letters \
            --prefix TEST_Bandymas_3500 --cable bottom
Laukiama: B a n d m a s - po 4 (kvadratas: 2 viršutiniame + 2 apatiniame bėgelyje), y - 3 (trikampis), viso 31.
v318: drenažas - Ø8 puslankiai dugno kontūre (2_GALAS), ne skylutės; viso 17 puslankių.
