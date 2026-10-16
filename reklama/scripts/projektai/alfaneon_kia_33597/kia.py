#!/usr/bin/env python3
"""Alfa Neon - KIA order 33597, PBVK25-01000-1 (Rytis 2026-10-16: „paruošk gamybinį dokumentą pagal seniau darytą failą").

ORIGINALO PERDARYMAS (SKILL „Originalo perdarymas į mūsų stilių", v160): visa informacija, matmenys, pozicijos ir lentelė -
iš seno lapo (KIA_order_33597.pdf, įdėtas senas lapas + 1:1 maketas), keičiamas TIK stilius:
  - FRONT VIEW - švarūs 1:1 maketo kontūrai (fonas, KIA, PBV, Hyötyajoneuvot), matmenys - originalo reikšmės (ISO 129-1);
  - SIDE VIEW - korpusas 20, raidžių storiai iš originalo (KIA 2 mm Alu, PBV 3 mm plexi);
  - 3D + detalės 2 / 3, EXPLODED, suvirintų smeigių detalė, montavimas ant stiklo - ORIGINALO FRAGMENTAI (K.place_pdf);
    mėlyni užrašai originale - kreivės (ne GOST) -> pašalinami ir perrašomi GOST (gost_frag);
  - Parts List - originalo pavadinimu ir stulpeliais.
Išdėstymas - layout_engine (TAISYKLĖ 33), blokas juostoje - K.section_block / centered (TAISYKLĖ 5).

    python3 kia.py ALT0000_KIA_order_33597.pdf
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import pymupdf as fitz
from reportlab.lib.colors import HexColor, black, white

import lapas_core as K
import layout_engine as LE
import gost_frag as GF
from lapas_core import T, rect, hdim, hchain, vchain, view_title, MM

SRC = os.path.join(HERE, "KIA_order_33597.pdf")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "ALT0000_KIA_order_33597.pdf")
FRAG = os.path.join(HERE, "frag_src.pdf")
FRONT = os.path.join(HERE, "front_src.pdf")
BLUE = "#64B3D9"

# ---------------------------------------------------------------- originalo duomenys (seno lapo reikšmės)
PW, PH, PD = 500, 540, 20
TOP = [85, 330, 85]                         # „85 mm | 330 mm | 85 mm"
LEFT = [84, 77, 37, 69, 95, 38, 139]        # viršus -> apačia
W_PBV, W_HY = 176, 310
PARTS = [["1", "Body, 4mm black brushed\nAluminum Composite Panel"], ["2", "Letters front, 2mm Brushed Alu"],
         ["3", "3mm white plexiglass"], ["4", "ORACAL 551 101 WHITE foil"], ["5", "Fitting L profile 15x15x2mm Alu"],
         ["6", "ORACAL 551 702 BLACK foil"]]
PART_NO = "PBVK25-01000-1"

# ---------------------------------------------------------------- 1:1 maketas -> švarus fronto šaltinis (tik užpildyti kontūrai)
PANEL = fitz.Rect(353, 311, 1770, 1841)     # fonas 500 x 540 (1:1, 2,835 pt/mm)
KMM = PANEL.width / PW


def make_front_src():
    src = fitz.open(SRC)[0]
    d = fitz.open(); pg = d.new_page(width=src.rect.width, height=src.rect.height)
    grab = fitz.Rect(PANEL.x0 - 2, PANEL.y0 - 2, PANEL.x1 + 2, PANEL.y1 + 2)
    boxes = []
    for dr in src.get_drawings():
        if dr.get("fill") is None or not grab.contains(dr["rect"]):
            continue
        sh = pg.new_shape()
        for it in dr["items"]:
            if it[0] == "l":
                sh.draw_line(it[1], it[2])
            elif it[0] == "c":
                sh.draw_bezier(it[1], it[2], it[3], it[4])
            elif it[0] == "re":
                sh.draw_rect(it[1])
            elif it[0] == "qu":
                sh.draw_quad(it[1])
        sh.finish(fill=dr["fill"], color=None, even_odd=dr.get("even_odd", True), closePath=dr.get("closePath", True))
        sh.commit()
        boxes.append((dr["rect"], dr["fill"]))
    d.save(FRONT, garbage=3, deflate=True)
    return boxes


# ---------------------------------------------------------------- seno lapo fragmentai (šaltinio pt)
CLIP = {"iso": (2222, 5595, 2580, 5940), "expl": (1880, 5972, 2392, 6300), "weld": (1570, 6100, 1860, 6300),
        "glass": (2388, 6112, 2600, 6312)}
# mėlyni užrašai - kreivės (ne GOST): šalinami ir perrašomi GOST [x0, y_baseline, tekstas, cap, spalva, align, rot]
BLUE_TXT = [((2230, 5722, 2370, 5729), "THK 2mm Silver brushed Aluminum"), ((2255, 5880, 2348, 5888), "THK 3mm White Acrylic"),
            ((2301, 5926, 2344, 5934), "White vinyl"), ((2531, 6207, 2588, 6219), "Black vinyl"),
            ((2459, 6119, 2506, 6130), "glass wall"), ((2437, 6152, 2450, 6160), "20"),
            ((2316, 5605, 2320, 5611), "2"), ((2279, 5749, 2283, 5755), "3")]
REDACT_DIMS = [(1690, 5998, 1932, 6065)]    # seno fronto matmenys 176 / 310 (patenka į EXPLODED iškarpą)


WHITEOUT = [(1876, 5968, 1992, 6004), (2064, 5968, 2092, 6004), (1992, 5968, 2040, 6008)]   # seno fronto / šono apačia EXPLODED iškarpoje


def make_frag_src():
    GF.prep(SRC, 0, [r for r, _ in BLUE_TXT] + REDACT_DIMS, FRAG)
    d = fitz.open(FRAG)
    for r in WHITEOUT:
        d[0].draw_rect(fitz.Rect(r), color=None, fill=(1, 1, 1), overlay=True)
    d.save(FRAG + ".tmp.pdf", garbage=3, deflate=True); d.close(); os.replace(FRAG + ".tmp.pdf", FRAG)
    GF.hairline(FRAG, pages=[0])                         # v172: įdėto originalo linijos - hairline (lape objektai tik hairline)


def frag_texts(key):
    c = CLIP[key]
    out = []
    for r, t in BLUE_TXT:
        if c[0] <= r[0] and r[2] <= c[2] and c[1] <= r[1] and r[3] <= c[3]:
            h = r[3] - r[1]
            out.append([(r[0] + r[2]) / 2, r[3], t, h * 0.95 if t[0].isupper() or t[0].isdigit() else h * 0.75, BLUE, "c", 0])
    return out


def place_frag(key, x, y, k, under=True):
    c = CLIP[key]
    w, h = (c[2] - c[0]) * k, (c[3] - c[1]) * k
    K.place_pdf(FRAG, 0, c, (x, K.H - y), (x + w, K.H - y), (x, K.H - y - h), outline=0, under=under)
    GF.draw(K, c, x, y, k, frag_texts(key))
    return w, h


def fsize(key, k):
    c = CLIP[key]
    return (c[2] - c[0]) * k, (c[3] - c[1]) * k


# ---------------------------------------------------------------- lapas
make_front_src(); make_frag_src()
K.OVERFLOW.clear()
K.set_band(12)
K.init(OUT + ".tmp", "KIA order 33597")
K.frame()

A_TOP, A_BOT = 62, 66                                          # viršaus matmenų eilės | apačios matmenys + pavadinimas
SC = LE.pick_scale((PW, PH), (K.IX1 - K.IX0, K.VIEW_BOT - K.IY0 - A_TOP - A_BOT))
s = MM / SC
YT = K.IY0 + A_TOP + (K.VIEW_BOT - K.IY0 - A_TOP - A_BOT - PH * s) / 2      # priekis / šonas - vertikaliai centre
KF = 0.7                                                       # originalo fragmentų mastelis (NOT TO SCALE)
W_ISO, H_ISO = fsize("iso", KF); W_W, H_W = fsize("weld", KF); W_E, H_E = fsize("expl", KF)
GAPV = max(60, 0.13 * PW * s)
COLS = [64 + PW * s, PD * s + 3 * s + 30, max(W_ISO + 30 + W_W, W_E)]
CX, G_ = LE.distribute(K.IX0, K.IX1, COLS, margin=(0.5, 1.0))
FX = CX[0] + 64
fx = lambda x: FX + x * s
fy = lambda y: YT + y * s
YB = fy(PH)

# FRONT VIEW - švarus 1:1 maketas, mastelis 1:SC
K.place_pdf(FRONT, 0, tuple(PANEL), (FX, K.H - YT), (FX + PW * s, K.H - YT), (FX, K.H - YT - PH * s), outline=0, under=True)
boxes = sorted(make_front_src(), key=lambda b: b[0].y0)
mm = lambda r: ((r.x0 - PANEL.x0) / KMM, (r.y0 - PANEL.y0) / KMM, (r.x1 - PANEL.x0) / KMM, (r.y1 - PANEL.y0) / KMM)
logo, pbv, hy = [mm(b[0]) for b in boxes if b[1][0] < 0.99 and b[0].width < PANEL.width * 0.9][:1] + \
    [mm(b[0]) for b in boxes if b[1][0] > 0.99][:2]
hdim(fx(0), fx(PW), YT - 40, f"{PW}", YT, YT, size=12)
hchain(YT - 20, [fx(0), fx(logo[0]), fx(logo[2]), fx(PW)], [YT, fy(logo[1]), fy(logo[1]), YT], [str(v) for v in TOP], size=8)
ys = [0, logo[1], logo[3], pbv[1], pbv[3], hy[1], hy[3], PH]
vchain(FX - 20, [fy(v) for v in ys], [FX, fx(logo[0]), fx(logo[0]), fx(pbv[0]), fx(pbv[0]), fx(hy[0]), fx(hy[0]), FX],
       [str(v) for v in LEFT], size=8)
vchain(FX - 48, [YT, YB], [FX, FX], [f"{PH}"], size=12)
hdim(fx(pbv[0]), fx(pbv[2]), YB + 16, f"{W_PBV}", fy(pbv[3]), fy(pbv[3]), size=8)
hdim(fx(hy[0]), fx(hy[2]), YB + 34, f"{W_HY}", fy(hy[3]), fy(hy[3]), size=8)
view_title(FX + PW * s / 2, YB + 58, "FRONT VIEW", f"SCALE 1:{SC}")

# SIDE VIEW (RIGHT) - korpusas 20, ant priekio: KIA 2 mm Alu, PBV 3 mm plexi (originalo storiai)
SX = CX[1] + 6
K.set_view(True)
rect(SX, YT, PD * s, PH * s, fill=HexColor("#141414"), lw=0.3)
rect(SX + PD * s, fy(logo[1]), 2 * s, (logo[3] - logo[1]) * s, fill=HexColor("#B9B9B9"), lw=0.2)
rect(SX + PD * s, fy(pbv[1]), 3 * s, (pbv[3] - pbv[1]) * s, fill=white, lw=0.2)
K.set_view(False)
hdim(SX, SX + PD * s, YT - 20, f"{PD}", YT, YT, size=8, small_side="r")
view_title(SX + PD * s / 2 + 10, YB + 58, "SIDE VIEW", f"SCALE 1:{SC}")

# originalo fragmentai: 3D + detalės 2 / 3 | suvirintos smeigės ; žemiau - EXPLODED
RX = CX[2]
TTL = 36
_h1 = max(H_ISO, H_W)
_free = (K.VIEW_BOT - K.IY0 - 20) - (_h1 + H_E + 2 * TTL)
ry1 = K.IY0 + 20 + _free / 3
place_frag("iso", RX, ry1 + (_h1 - H_ISO) / 2, KF)
view_title(RX + W_ISO / 2, ry1 + _h1 + 16, "3D VIEW + DETAILS 2 / 3", "ILLUSTRATIVE - NOT TO SCALE")
place_frag("weld", RX + COLS[2] - W_W, ry1 + (_h1 - H_W) / 2, KF)
view_title(RX + COLS[2] - W_W / 2, ry1 + _h1 + 16, "DETAIL - KIA LOGO", "welded fasteners, not to scale")
ry2 = ry1 + _h1 + TTL + _free / 3
place_frag("expl", RX + (COLS[2] - W_E) / 2, ry2, KF)
view_title(RX + COLS[2] / 2, ry2 + H_E + 16, "EXPLODED VIEW", "NOT TO SCALE")

# ---------------------------------------------------------------- juosta: montavimo pjūvis | Parts List | MAIN DATA | antraštė
BY0 = K.BAND_Y; BH = K.IY1 - BY0
W_SEC, W_MD, W_TB = 214, 214, 272
X_TB = K.IX1 - W_TB; X_MD = X_TB - W_MD; X_BOM = K.IX0 + W_SEC; W_BOM = X_MD - X_BOM
KG = min((W_SEC - 20) / (CLIP["glass"][2] - CLIP["glass"][0]), (BH - 12 - 16) / (CLIP["glass"][3] - CLIP["glass"][1]))


def glass(x, y, w, h):
    gw, gh = fsize("glass", KG)
    rect(x + (w - gw) / 2, y + (h - gh) / 2, gw, gh, fill=white, stroke=None)      # matuojamas fragmento plotas
    place_frag("glass", x + (w - gw) / 2, y + (h - gh) / 2, KG, under=False)   # virš matavimo stačiakampio


K.section_block(K.IX0, BY0, W_SEC, BH, "SECTION - MOUNTING ON GLASS WALL", glass)
K.bom_table(X_BOM, BY0, W_BOM, BH, PARTS, title="Parts List", cols=(("Item", 0.08), ("Part Number", None)))
K.main_data(X_MD, BY0, W_MD, BH, [["Quantity", "1 pcs."], ["Part number", PART_NO], ["Overall size", f"{PW} x {PH} x {PD} mm"],
                                    ["Body", "ACP 4 mm, black brushed"], ["Letters", "KIA 2 mm Alu / PBV 3 mm plexi"],
                                    ["Text", "ORACAL 551 101 white"], ["Mounting", "L 15x15x2 + 3M tape, glass"],
                                    ["Glass wall", "ORACAL 551 702 black"]], lab_w=62)
K.title_block(X_TB, W_TB, {"client": "Alfa Neon AB", "title": f"KIA order 33597 - {PART_NO}, {PW} x {PH} x {PD} mm",
                           "drawing_no": "KIA order 33597", "date": "2026-10-16", "rev": "A", "order_no": "ALT0000_00.00_RS",
                           "sheet": "1 / 1", "qty": "1 pcs."}, f"1:{SC}")
LE.report("KIA 33597", SC, G_, {"front H": (PH * s, K.VIEW_BOT - K.IY0 - A_TOP - A_BOT)})
K.save(OUT)
K.pdf_fix_fonts(OUT)
for f_ in (FRAG, FRONT, OUT + ".tmp"):                                       # tarpiniai šaltiniai - kuriami kiekvieną kartą iš KIA_order_33597.pdf
    os.path.exists(f_) and os.remove(f_)
print("OK", OUT, "scale 1:%d" % SC, "logo", [round(v) for v in logo], "PBV", [round(v) for v in pbv], "Hy", [round(v) for v in hy],
      "overflow", K.OVERFLOW)
