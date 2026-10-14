# CEOS Groupe D059422 - Thales Campus Velizy (2026-10-13, rev C)

Taisyklės: `references/moduliai_pilonai.md`.

Paleidimas:
```
THALES_SRC=<kliento PDF> THALES_OUT=<aplankas> python3 thales_pylons.py [E|B|P|all]
```
- `E` - įėjimo pilonas 1050 x 2530, dvipusis (flanšai 300x300x20, kairė koja +60) - lapai 1-2
- `B` - pastatų pilonai 600 x 2130, vienpusiai x4 (balkis 80x40x4, 4 x M16, mėlyna 2 x 43) - lapai 3-4
- `P` - stalinis PMMA planas 297 x 210, 10° pasvirimas - lapas 5
Sujungimas: pymupdf `insert_pdf` eilės tvarka + `lapas_core.pdf_fix_fonts`.

Parametrai - `Pyl(key, W, H, sides, legs "ext"|"int", qty, title)`; `TB` (mėlynos lovelės gylis) nustatomas globaliai
prieš kiekvieno tipo generavimą (40 / 43). Kliento grafikos `clip` (pt) - pagal kliento PDF puslapį.
Išklotinių funkcijos (`flat_blue`, `flat_white`) paliktos gamybai, į kliento dokumentą nededamos.

v207-v208 (Rytis 2026-10-14): išklotinės pagal folded v173 (atlankas = gylis - t, be K / BD), skylės Ø3.2 7 mm nuo atlanko krašto
(ir csk). Mėlynos lovelės - šonai įsilenkia (numatyta); BALTOS lovelės (visos projekte) - VIRŠUS / APAČIA lenkiasi Į VIDŲ tarp
šonų (W - 2t), šonai ir ausės per visą aukštį. `PREFIX=ALT8879_10.13_RS THALES_OUT=... python3 thales_dxf.py`.
v209 (Rytis 2026-10-14): ĮĖJIMO (didelio) pilono balta lovelė apačioje lenkiasi TIK 20 mm (`Pyl.WBOT`), pastatų pilonų - 30.
