"""Lapas 2/2 - išklotinės (flat patterns) P1-P6 ir išdėstymas 2000x4000x2 lapuose."""
import math, sys
from common import *
import data as D

OUT = sys.argv[1]
begin(9)
VB = K.VIEW_BOT
s = MM / 40
a, hb, off = D.FL, D.BA / 2, D.FL + D.BA / 2 - D.OSSB          # 38.26, 2.26, 36.52
WF = D.flat_size(0)[1]
SY0, SY1 = off + 2.1, off + D.PH - 2.1                           # šoninio flanšo ribos (895.8)


def outline(F):
    o = off
    return [(o, 0), (F - o, 0), (F - o, SY0), (F, SY0), (F, SY1), (F - o, SY1), (F - o, WF), (o, WF),
            (o, SY1), (0, SY1), (0, SY0), (o, SY0)]


def bolt_ys():
    y0, y1 = 2.1 + 50, D.PH - 2.1 - 50
    return [off + y0 + (y1 - y0) * k / 3 for k in range(4)]


def flat_view(p, x0, y0):
    F = D.flat_size(p["len"])[0]
    X = lambda u: x0 + u * s
    Yv = lambda v: y0 + (WF - v) * s                 # v aukštyn
    K.set_view(True)
    poly([(X(u), Yv(v)) for u, v in outline(F)], fill=HexColor("#EEF8FC"), lw=0.5)
    K.set_view(False)
    for u in (a, F - a):
        K.centerline(X(u), Yv(SY0), X(u), Yv(SY1))
    for v in (a, WF - a):
        K.centerline(X(off), Yv(v), X(F - off), Yv(v))
    span = p["len"] - 100; n = max(1, round(span / 300))
    for v in (7, WF - 7):                                   # Ø3.2 tvirtinimo skylės 7 mm nuo flanšo krašto
        for k in range(n + 1):
            circle(X(off + 50 + span * k / n), Yv(v), 0.9, lw=0.3)
    p["holes"] = (n + 1, n, span / n)
    if p is D.LOGO_PART:                                    # laido Ø11 kairėje šoninėje briaunoje
        vv = WF - (off + D.D11[1])                          # kairė šoninė briauna, D11 aukštyje
        circle(X(20), Yv(vv), 1.6, stroke=K.CABLE, lw=0.5)
        line(X(20), Yv(vv) - 2, X(20) + 30, y0 - 40, 0.3, K.CABLE)
        T(X(20) + 32, y0 - 40, f"Ø11 cable in left side flange: {D.D11[1]:.0f} from top, 20 from edge", 8, color=K.CABLE, auto_red=False)
    for side in (0, 1):
        if False:
            u = 0 if side == 0 else F
            T(X(u) + (-4 if side == 0 else 4), Yv(WF / 2) + 3, "*", 14, font="FB", color=RED, align="r" if side == 0 else "l", auto_red=False)
    T(X(F / 2), Yv(WF / 2) + 3, f"P{p['no']}", 12, font="FB", align="c", color=HexColor("#1D334A"))
    T(X(F / 2), Yv(WF / 2) + 14, "face out (painted)", 8, color=K.GREY, align="c")
    # matmenys
    hdim(X(0), X(F), y0 - 24, f"{F:.1f}", Yv(SY1), Yv(SY1), size=12)
    hchain(y0 - 10, [X(off), X(F - off)], [y0, y0], [f"{F - 2 * off:.1f}"], size=8)
    vchain(X(0) - 12, [Yv(WF), Yv(WF - a), Yv(a), Yv(0)], [X(off), X(off), X(off), X(off)],
           [f"{a:.1f}", f"{WF - 2 * a:.1f}", f"{a:.1f}"], size=8)
    vchain(X(0) - 30, [Yv(WF), Yv(0)], [X(off), X(off)], [f"{WF:.1f}"], size=12)
    end_txt = {"outer": "outer end", "joint": "joint", "fold1": "fold 1 (90°)", "fold2": "fold 2 (90°)"}
    T(X(0), Yv(0) + 12, end_txt[p["ends"][0]], 8, color=K.GREY, auto_red=False)
    T(X(F), Yv(0) + 12, end_txt[p["ends"][1]], 8, color=K.GREY, align="r", auto_red=False)
    nh, n, pt = p["holes"]
    view_title(X(F / 2), Yv(0) + 30, f"P{p['no']} - FLAT ({p['len']})", "SCALE 1:40  |  1 pcs.")
    T(X(F / 2), Yv(0) + 30 + 4 + K.F_SCALE * 1.25 + 11, f"2 x {nh} holes Ø3.2:  50 | {n} x {pt:.1f} | 50,  7 from edge", 8, align="c")


cols = [K.IX0 + 62, K.IX0 + 420]
rows = [78, 250, 422]
order = [D.PARTS[0], D.PARTS[1], D.PARTS[2], D.PARTS[3], D.PARTS[4], D.PARTS[5]]
for i, p in enumerate(order):
    flat_view(p, cols[i // 3], rows[i % 3])

# ---- detalė: kampas ir skylė (1:2)
# ---- NESTING: 3 lapai 2000x4000
sn = MM / 50
NX = K.IX1 - 4000 * sn - 86
cols_ = None
# Rytis 2026-10-09: pildoma nuo krašto per lapo aukštį (2 juostos), tada link lapo galo
_by = sorted(D.PARTS, key=lambda p: -p["len"])            # ilgiausios pirmos, po 2 per lapo aukštį
sheets = []
for p in _by:
    F_ = D.flat_size(p["len"])[0]
    for sh_ in sheets:
        col = sh_[-1]
        if len(col) < 2:
            col.append(p["no"]); break
    else:
        sheets.append([[p["no"]]])
SHEET_OF = {no: si + 1 for si, sh_ in enumerate(sheets) for col in sh_ for no in col}
used = 0
for si, cols_ in enumerate(sheets):
    y0 = 92 + si * 150
    rect(NX, y0, 4000 * sn, 2000 * sn, fill=HexColor("#F4F4F4"), lw=0.5)
    u = D.EDGE_M
    for col in cols_:
        cw = 0
        for li, no in enumerate(col):
            ly = y0 + (D.EDGE_M + li * (WF + D.EDGE_M)) * sn
            p = D.PARTS[no - 1]; F = D.flat_size(p["len"])[0]
            rect(NX + u * sn, ly, F * sn, WF * sn, fill=HexColor("#D6EEF7"), lw=0.3)
            T(NX + (u + F / 2) * sn, ly + WF * sn / 2 + 3, f"P{no}  {F:.0f} x {WF:.0f}", 8, font="FB", align="c")
            used += F * WF; cw = max(cw, F)
        u += cw + D.EDGE_M
    T(NX + 4000 * sn + 6, y0 + 10, f"SHEET {si + 1}", 9, font="FB")
    T(NX + 4000 * sn + 6, y0 + 22, "2000x4000x2", 8, color=K.GREY)
    if si == 0:
        hdim(NX, NX + 4000 * sn, y0 - 12, "4000", y0, y0, size=12)
        vchain(NX - 14, [y0 + v * sn for v in (0, D.EDGE_M, D.EDGE_M + WF, 2 * D.EDGE_M + WF, 2 * D.EDGE_M + 2 * WF, 2000)],
               [NX] * 6, ["10", f"{WF:.0f}", "10", f"{WF:.0f}", f"{2000 - 2 * D.EDGE_M - 2 * WF:.0f}"], size=8)
        vchain(NX - 46, [y0, y0 + 2000 * sn], [NX, NX], ["2000"], size=12)
    if si == 2:
        ox = 2 * D.EDGE_M + 1502
        T(NX + (ox + (4000 - ox) / 2) * sn, y0 + 1000 * sn + 3, f"offcut ≈ {4000 - ox:.0f} x 2000", 8, color=K.GREY, align="c")
view_title(NX + 2000 * sn, 92 + 3 * 150 - 14, "NESTING - Al 2000 x 4000 x 2", "SCALE 1:50  |  CNC margin 10, 2 lanes per sheet")
util = used / (3 * 4000 * 2000) * 100
T(cols[1] + 165, 575, "ALL PARTS: 4 x 90° bends, R2 - facade angles not given, corner parts as standard parts", 9, font="FB", align="c")


def bend_data(x, y, w, h):
    rows_ = [("Material", "Alu 2 mm (sheet 2000x4000)"), ("Inner radius R", "2 mm (STEP)"), ("K-factor", f"{D.K_F} (assumed)"),
             ("Bend allowance", f"{D.BA:.2f} mm"), ("Bend deduction", f"{D.BD:.2f} mm / 90°"),
             ("Flange to bend line", f"{a:.2f} mm"), ("Side flanges", f"{D.SIDE_H:.1f}, between top/bottom"),
             ("Bends", "4 x 90° up, R2"), ("Corner relief", "per STEP lankstinys_1prie1")]
    yy = y + 14
    for lab, val in rows_:
        T(x + 6, yy, lab, 8, color=K.GREY); T(x + 92, yy, val, 8); yy += 15


bom = []
for p in D.PARTS:
    F, Wf = D.flat_size(p["len"])
    sh = SHEET_OF[p["no"]]
    star = ""
    bom.append([f"5.{p['no']}", f"P{p['no']} {p['len']}{star} - flat {F:.1f} x {Wf:.1f}", "Alu 2 mm folded", "NCS S 0540-B", f"1 pcs. / sheet {sh}"])
bom.append(["", "Al sheet 2000 x 4000 x 2", "Aluminium", "-", "3 pcs."])
bom.append(["", "Fixing holes top + bottom, 7 from edge", "Ø3.2", "-", f"{2 * sum(p['holes'][0] for p in D.PARTS)} holes"])
flatA = sum(D.flat_size(p["len"])[0] * WF for p in D.PARTS) / 1e6
md = [["Parts", "6 pcs. (P1-P6)"], ["Sheets", "3 pcs. 2000x4000x2"], ["Flat area", f"{flatA:.2f} m²"],
      ["Utilization", f"{util:.0f} %"], ["Max flat", f"{D.flat_size(3900)[0]:.1f} (sheet 3980 usable)"],
      ["Finish", "NCS S 0540-B, outside only"], ["Inside", "unpainted"], ["Letter holes", f"see 1:1 file; Ø11 cable in P{D.LOGO_PART['no']}"],
      ["Bends", "all 90° (angles not given)"]]
band("FLAT PATTERN DATA", bend_data, bom, md, "Clas Ohlson Horten 3 - flat patterns P1-P6, nesting", "1 / 1", "1:40 / 1:50", md_lab=70)
K.save(OUT)
print("util", round(util, 1), "overflow", K.OVERFLOW)
