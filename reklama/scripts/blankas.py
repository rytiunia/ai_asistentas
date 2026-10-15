#!/usr/bin/env python3
"""Tuščias A3 dokumento blankas (v248, Rytis 2026-10-15): rėmelis su zonomis, apatinė juosta (pjūvio blokas, BOM,
MAIN DATA), REVISIONS ir antraštės lentelė su užrašais - BE reikšmių ir be kiekio (juodas kiekio blokas tuščias,
„Sheet" be numerio). Naudojimas: python3 blankas.py [out.pdf]  (numatyta assets/blankas_A3.pdf)"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lapas_core as K  # noqa: E402

out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "assets", "blankas_A3.pdf")
K.set_band(9)
K.init(out + ".tmp", "blank")
K.frame()
W_P6, W_MD, W_TB = 214, 172, 272                     # kaip braizyti_begeliai.py
BY0 = K.BAND_Y
BH = K.IY1 - BY0
X_P6 = K.IX0
X_TB = K.IX1 - W_TB
X_MD = X_TB - W_MD
X_BOM = X_P6 + W_P6
W_BOM = X_MD - X_BOM
K.header(X_P6, BY0, W_P6, "PROFILE / SECTION")
K.rect(X_P6, BY0 + 12, W_P6, BH - 12, lw=0.6)
K.bom_table(X_BOM, BY0, W_BOM, BH, [["", "", "", "", ""] for _ in range(8)], title="BILL OF MATERIALS  (per 1 pcs.)")
K.main_data(X_MD, BY0, W_MD, BH, [["", ""] for _ in range(9)], lab_w=58)
K.title_block(X_TB, W_TB, {"blank": True, "client": "", "title": "", "order_no": "", "drawing_no": "", "date": "",
                           "qty": "", "sheet": ""}, "")
K.save(out)
print("OK", out)
