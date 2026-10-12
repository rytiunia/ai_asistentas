# Clas Ohlson Horten (BrandFactory, 2026-10-09) - P8 special ant folded plokštės

Pozicijos: Horten 3 (16839 x 900, 3 fasado plokštumos, 6 atskiros dalys) ir Horten 1 (3000 x 1300, exterior).
Lapai: `sheet1.py` (Horten 3 bendras), `sheet2v.py` (Horten 3 3D ant fasado), `sheet3.py` (Horten 1),
`sheet2.py` (Horten 3 išklotinės + nesting, atskiras failas), `one2one_all.py` (1:1 abiem).
- `refholes.py` - Clas Ohlson P8 special proporcijų etalonas (`assets/clasohlson_proporcijos.pdf`, 1:1, 3 dydžiai):
  raidei imamas artimiausio aukščio dydis, skylės perkeliamos proporcingai, Ø4 / išilginė 6.1x3.7 / Ø8 NEKINTA.
- `r3d.py` - 3D su teisingu užstojimu (taip pat `scripts/r3d.py`).
- Keliai (kliento failai /root/.claude/uploads/..., skill'o katalogas) - pakeisti `common.py`, `data.py`, `refholes.py`, `sheet3.py`.
Eiga: `python3 sheet1.py s1.pdf; python3 sheet2v.py s2v.pdf; python3 sheet3.py s3.pdf` -> sujungti, `K.pdf_fix_fonts`.
