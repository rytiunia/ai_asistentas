# TEST P3 „Vangelonys" L 4300, gylis 80, rėmas 40x40x2 square RAL 9016, raidės RAL 6017 (v344, Rytis 2026-10-17)
Raidės - Liberation Sans Bold (tik testui):
    python3 ../welcome_p1_test/make_client.py Vangelonys Vangelonys_client.pdf LEN 4300 /usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf
    python3 ../../braizyti_begeliai.py spec.json TEST_P3_Vangelonys.pdf      # + _1-1.pdf, _P3.dxf, rails.json
Laukiama: rėmas 4118 mm -> 3 statmenys (galiniai + vidurinis per stiebą), distanceriai 30 (gylis >= 60), galas plexi 4 + PVC
(raidės >= 400 mm), pjūvyje stačiakampis vamzdis 40, patikra 0.
