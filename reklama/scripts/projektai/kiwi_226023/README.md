# KIWI order 226023 KIWI 640 BYGNES (BrandFactory, 2026-10-13) - 3 lapai mūsų stiliumi

Analogas - Tollnes 225948 (ALT8858): 3 x KIWI minipris 3362 x 1095, 3 x 7-23 2037 x 709 (P5S, rėmas O 40x20x2 RAL 7024,
fitting plates 40x75 Ø8), 1 x Lanterne 6800 x 500 x 100 RAL 6018.
1. `python3 mkclient.py client_clean.pdf` (kliento PDF p1: KIWI išorė - žymeklio spalva, žalia - decal; minipris - 8 mm
   stiklo kontūrai + juoda decal; 7-23; bėgeliai pilki, KIWI | minipris rėmas padalintas ties x 414 pt).
2. `python3 ../../braizyti_begeliai.py spec1.json s1.pdf`, `spec2.json s2.pdf` (mastelis kliento faile 1:40, `client_frame`).
3. `python3 lanterne.py s3.pdf` (lapas_core; sekcijos 800 + 3000 + 3000 - ALT pasiūlymas).
4. Sujungti, `lapas_core.pdf_fix_fonts`, `Drawing_Order 226023 KIWI 640 BYGNES.pdf` užsakymo aplanke NAS.
