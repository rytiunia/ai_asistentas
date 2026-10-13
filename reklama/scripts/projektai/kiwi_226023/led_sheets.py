#!/usr/bin/env python3
"""KIWI 226023 - LED INSTALLATION lapai (v161, Rytis 2026-10-13: „nėra led dėliojimo ir kiekių su įtampa").
LED dėliojimas su kiekiais raidėse ir laidais (230V) - TIKSLUS originalo fragmentas (ALT8858 Tollnes, identiški gaminiai),
lentelė - originalo „LED Installation" tekstas. Keičiamas tik lapo stilius.
Paleidimas:  python3 led_sheets.py <originalas.pdf> <out_dir>
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import lapas_core as K  # noqa: E402
from lapas_core import view_title  # noqa: E402

TB0 = {"client": "BrandFactory", "order_no": "ALT0000_10.13_RS", "drawing_no": "Order 226023 KIWI 640 BYGNES",
       "rev": "A", "date": "2026-10-13", "revisions": [["A", "First issue", "2026-10-13", "RS"]]}
COLS = (("POS", 20), ("LED Installation", 0.46), ("Qty", 0.16), ("Power", 0.14), ("Notes", None))

SHEETS = [
    dict(key="s1led", pno=0, clip=(78, 318, 580, 572), sheet="2 / 5", title="KIWI minipris 3362 - LED installation",
         rows=[["", "Module P130 (1W) green", "85 pcs.", "85W", "#009639"],
               ["", "Module P65 (0,5W) white", "63 pcs.", "31,5W", ""],
               ["", "Transf. KPS-100W", "1 vnt.", "", "inside letter"],
               ["", "Transf. KPS-20W", "2 vnt.", "", "inside letter"],
               ["", "Wire 230V (black)", "9 m", "", "230V ~3m x 3"]],
         md=[["Quantity", "3 pcs."], ["Voltage", "230V"], ["Wire", "230V (black): 9 m"],
             ["LED", "qty per letter - on drawing"]]),
    dict(key="s2led", pno=1, clip=(66, 428, 664, 768), sheet="4 / 5", title="7-23  L 2037 - LED installation",
         rows=[["", "Module P130 lens (1W) green", "26 pcs.", "26", "#009639"],
               ["", "KPS-V12-40W", "1 pcs.", "", "inside"],
               ["", "Wire 230V (BLACK)", "3m", "", "230V ~3m"]],
         md=[["Quantity", "3 pcs."], ["Voltage", "230V"], ["Wire", "230V (BLACK): 3m"],
             ["LED", "qty per letter - on drawing"]]),
]


def sheet(src, cfg, out):
    K.set_band(max(len(cfg["md"]), len(cfg["rows"]) + 1))
    K.init(out + ".tmp", cfg["title"])
    K.frame()
    x0, y0, x1, y1 = cfg["clip"]
    cw, ch = x1 - x0, y1 - y0
    aw, ah = K.IX1 - K.IX0 - 60, K.VIEW_BOT - K.IY0 - 80
    k = min(aw / cw, ah / ch)
    w, h = cw * k, ch * k
    X = K.IX0 + (K.IX1 - K.IX0 - w) / 2
    Ytop = K.IY0 + 24
    # reportlab koord. (y aukštyn): tl, tr, bl
    K.place_pdf(src, cfg["pno"], cfg["clip"], (X, K.H - Ytop), (X + w, K.H - Ytop), (X, K.H - Ytop - h), outline=0)
    view_title(X + w / 2, Ytop + h + 30, "LED INSTALLATION", "as original drawing (ALT8858)")
    BY0 = K.BAND_Y; BH = K.IY1 - BY0
    W_MD, W_TB = 230, 272
    X_TB = K.IX1 - W_TB; X_MD = X_TB - W_MD
    K.bom_table(K.IX0, BY0, X_MD - K.IX0, BH, cfg["rows"], title="LED INSTALLATION", cols=COLS)
    K.main_data(X_MD, BY0, W_MD, BH, cfg["md"], lab_w=64)
    K.title_block(X_TB, W_TB, dict(TB0, title=cfg["title"], sheet=cfg["sheet"]), "-")
    K.save(out)


if __name__ == "__main__":
    src, od = sys.argv[1], sys.argv[2]
    for cfg in SHEETS:
        sheet(src, cfg, os.path.join(od, cfg["key"] + ".pdf"))
