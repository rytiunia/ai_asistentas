# 6 m strypų taisyklės bandymai (v73, 2026-10-10)
python3 make_test.py                                        # strypai_6050.pdf: H I I I H, 2 bėgeliai po 3025 (rėmas 6050)
python3 ../../braizyti_begeliai.py spec_6050.json out_6050.pdf        # laukiama: 3025 -> 2995 (-15/-15), 1 x 6 m [2995+2995]
python3 ../../braizyti_begeliai.py spec_6050_v.json out_6050_v.pdf    # su statmenimis: 2 strypai, NETRUMPINAMA (nepadėtų)
python3 ../../braizyti_lapa.py spec_folded_3050.json out_folded_3050.pdf   # folded 3050: L 2 x 3000 -> perspėjimas, 2 strypai
Kliento PDF 1:1 (pt = mm, `scale` 72/25.4). Taisyklės - `references/medziagos.md`.
