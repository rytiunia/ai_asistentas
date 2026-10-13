#!/usr/bin/env python3
"""OKQ8 height restriction (Skyltkoncept, ALT8877_10.13_RS) - kliento brėžinio perdarymas į mūsų lapo stilių.

Duomenys - TIK iš kliento lapo (okq8 height restriction, Skyltkoncept, Sheet 1 of 1): matmenys, Parts List 1-12, spalvos.
Grafika (rodyklės, „Biltvätt", automobilis + dušai, „FRI HÖJD 2,70m.") - vektoriai iš kliento spalvų schemos bloko
(dėžė 3000 x 520, profilis 1500 x 120), nes priekio vaizdas kliento PDF - rastras.
Išvestinis (ne kliento matmuo, matuotas kliento mastelyje): profilio vieta 180 | 660 | 1500 | 660.
Paleidimas:  OKQ8_SRC=<kliento.pdf> python3 height_restriction.py out.pdf
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import lapas_core as K  # noqa: E402
from lapas_core import T, line, rect, poly, circle, hdim, vchain, hchain, view_title, MM  # noqa: E402
from reportlab.lib.colors import HexColor, white, black  # noqa: E402
import pymupdf as fitz  # noqa: E402

SRC = os.environ.get("OKQ8_SRC", "/mnt/user-data/uploads/ALT8877_10_13_okq8_height_restriction.pdf")

# ---------------------------------------------------------------- kliento duomenys (nekeisti)
BW, BOXH, BD = 3000, 520, 200          # dėžė: 3000 (kliento), 3440 - 150 - 2770 = 520, gylis 200
TOT_H = 3440
BASE_H = 150                            # pagrindo (uždengimo 7) aukštis
LEG_TOP = 2770                          # nuo pagrindo viršaus iki dėžės apačios
LEG = 180                               # koja □180x180x5
BASE_W, BASE_D = 906, 506               # uždengimas 7 (priekis / šonas)
PL_W, PL_D, PL_T = 900, 500, 15         # montavimo plokštė 2
PL_HX, PL_HY, PL_HD = 375, 350, 32      # skylės: 375 + 375, 350, Ø32
PR_L, PR_H, PR_D, PR_T = 1500, 120, 50, 2   # aukščio profilis 8
PR_GAP = 100                            # tarpas dėžė -> profilis
CLEAR = 2700                            # FRI HÖJD
PR_X = LEG + (BW - LEG - PR_L) / 2      # 840 (išvestinis: profilis laisvo tarpo centre, kliento mastelyje 842 / 658)
HANG = (297.5, 1206.4)                  # pakabos 8A nuo profilio kairės: gamybinis failas 1134.5 / 2043.4 nuo kojos išorės (+3)
Y_BOX0 = BASE_H + LEG_TOP               # 2920 dėžės apačia nuo žemės
Y_PR0 = CLEAR                           # 2700 profilio apačia

C_BLUE = HexColor("#2F3159")            # NCS S 4055-R70B (kliento pavyzdėlis)
C_GREY = HexColor("#9A9790")            # NCS S 2500-N (kliento pavyzdėlis)
C_BLACK = HexColor(K.code_hex("RAL 9005"))
NCS = {"NCS S 4055-R70B": "#2F3159", "NCS S 2500-N": "#9A9790"}
EDGE = HexColor("#555555")

_ch = K.code_hex                         # BOM FINISH langeliui - NCS spalvos


def code_hex(v, ral=True):
    for k_, h_ in NCS.items():
        if k_ in str(v):
            return h_
    return _ch(v, ral)


K.code_hex = code_hex


# ---------------------------------------------------------------- kliento grafika (vektoriai)
def _rings(path_d, rect_pt, W_mm, H_mm, n=8):
    """pymupdf drawing -> žiedai mm (x dešinėn, y žemyn nuo rect kairio viršaus)"""
    sx, sy = W_mm / rect_pt.width, H_mm / rect_pt.height
    f = lambda p: ((p.x - rect_pt.x0) * sx, (p.y - rect_pt.y0) * sy)
    rings, cur, last = [], [], None
    for it in path_d["items"]:
        op = it[0]
        if op == "re":
            r = it[1]
            rings.append([f(fitz.Point(r.x0, r.y0)), f(fitz.Point(r.x1, r.y0)), f(fitz.Point(r.x1, r.y1)), f(fitz.Point(r.x0, r.y1))])
            continue
        p0 = it[1]
        if last is None or abs(p0.x - last.x) > 1e-3 or abs(p0.y - last.y) > 1e-3:
            if len(cur) > 2:
                rings.append(cur)
            cur = [f(p0)]
        if op == "l":
            cur.append(f(it[2])); last = it[2]
        elif op == "c":
            a, b, c_, d = it[1:5]
            for k in range(1, n + 1):
                t = k / n
                x = (1 - t) ** 3 * a.x + 3 * (1 - t) ** 2 * t * b.x + 3 * (1 - t) * t * t * c_.x + t ** 3 * d.x
                y = (1 - t) ** 3 * a.y + 3 * (1 - t) ** 2 * t * b.y + 3 * (1 - t) * t * t * c_.y + t ** 3 * d.y
                cur.append(f(fitz.Point(x, y)))
            last = d
    if len(cur) > 2:
        rings.append(cur)
    return rings


def client_graphics():
    pg = fitz.open(SRC)[0]
    box = prof = None
    glow = stick = fri = None
    for d in pg.get_drawings():
        r = d["rect"]
        if not (900 < r.x0 and r.x1 < 1130 and 95 < r.y0 and r.y1 < 165):
            continue
        fl = d.get("fill")
        if fl and len(d["items"]) == 1 and fl[2] > 0.5 and r.width > 150:
            box = r                                             # mėlyna dėžė (spalvų schema)
        elif fl and max(fl) < 0.2 and len(d["items"]) <= 4 and r.width > 80:
            prof = r                                            # juodas profilis
    for d in pg.get_drawings():
        r = d["rect"]
        fl = d.get("fill")
        if not fl or min(fl) < 0.9 or not (900 < r.x0 and r.x1 < 1130 and 95 < r.y0 and r.y1 < 165):
            continue
        if box and r.y1 <= box.y1 + 0.5:
            if r.width > 100:
                glow = d
            else:
                stick = d
        elif prof:
            fri = d
    G = {"glow": _rings(glow, box, BW, BOXH), "sticker": _rings(stick, box, BW, BOXH),
         "fri": _rings(fri, prof, PR_L, PR_H)}
    G["bb"] = {k: (min(x for r in v for x, _ in r), min(y for r in v for _, y in r),
                   max(x for r in v for x, _ in r), max(y for r in v for _, y in r)) for k, v in G.items()}
    return G


def draw_rings(rs, xf, col):
    from reportlab.pdfgen.canvas import FILL_EVEN_ODD
    c = K.c
    c.saveState(); c.setFillColor(col); c.setLineWidth(0)
    p = c.beginPath()
    for r in rs:
        for i, (x, y) in enumerate(r):
            X, Yy = xf(x, y)
            (p.moveTo if i == 0 else p.lineTo)(X, K.H - Yy)
        p.close()
    c.drawPath(p, stroke=0, fill=1, fillMode=FILL_EVEN_ODD)
    c.restoreState()


# ---------------------------------------------------------------- matmenys (v145: grandinė arčiau, gabaritas už jos)
D1, D2 = 16, 38


def HM(x1, x2, y, label, e1, e2):
    hdim(x1, x2, y, label, e1=e1, e2=e2, size=K.F_DIM_MAIN)
    K._Tbg((x1 + x2) / 2, y - 2.5, label, K.F_DIM_MAIN, align="c")


def VM(x, y1, y2, ext, label):
    vchain(x, [y1, y2], [ext, ext], [label], size=K.F_DIM_MAIN, bg=True)


def detail_mark(x, y, r, letter):
    circle(x, y, r, lw=0.35)
    T(x + r * 0.75, y - r * 0.75, letter, 10, font="FB")


# ---------------------------------------------------------------- vaizdai
def front_view(G, X0, YG, s):
    X = lambda x: X0 + x * s                     # x nuo dėžės kairės (= kojos kairė)
    Yg = lambda y: YG - y * s                    # y nuo žemės aukštyn
    lc = LEG / 2
    K.set_view(True)
    rect(X(lc - BASE_W / 2), Yg(BASE_H), BASE_W * s, BASE_H * s, fill=C_GREY, lw=0.1)
    rect(X(0), Yg(Y_BOX0), LEG * s, LEG_TOP * s, fill=C_GREY, lw=0.1)
    rect(X(0), Yg(TOT_H), BW * s, BOXH * s, fill=C_BLUE, lw=0.1)
    draw_rings(G["glow"] + G["sticker"], lambda u, v: (X(u), Yg(TOT_H) + v * s), white)
    for hx in HANG:
        line(X(PR_X + hx), Yg(Y_BOX0), X(PR_X + hx), Yg(Y_PR0 + PR_H), 0.1)
    rect(X(PR_X), Yg(Y_PR0 + PR_H), PR_L * s, PR_H * s, fill=C_BLACK, lw=0.1)
    draw_rings(G["fri"], lambda u, v: (X(PR_X + u), Yg(Y_PR0 + PR_H) + v * s), white)
    K.set_view(False)
    # viršus: grandinė (kojos / profilio vieta) arčiau, gabaritas 3000 už jos
    yt = Yg(TOT_H)
    hchain(yt - D1, [X(0), X(LEG), X(PR_X), X(PR_X + PR_L), X(BW)],
           [Yg(Y_BOX0), Yg(Y_BOX0), Yg(Y_PR0 + PR_H), Yg(Y_PR0 + PR_H), yt],
           [f"{LEG}", f"{PR_X - LEG:g}", f"{PR_L}", f"{BW - PR_X - PR_L:g}"], size=K.F_DIM_MAIN, bg=True)
    HM(X(0), X(BW), yt - D2, f"{BW}", yt, yt)
    # kairė: 150 | 2770 | 520, gabaritas 3440
    xl = X(lc - BASE_W / 2)
    vchain(xl - D1, [Yg(TOT_H), Yg(Y_BOX0), Yg(BASE_H), Yg(0)], [X(0), X(0), xl, xl],
           [f"{BOXH}", f"{LEG_TOP}", f"{BASE_H}"], size=K.F_DIM_MAIN, bg=True)
    VM(xl - D2, Yg(TOT_H), Yg(0), xl, f"{TOT_H}")
    # apačia: pagrindas 363 | 180 | 363, gabaritas 906
    yb = Yg(0)
    sd = (BASE_W - LEG) / 2
    hchain(yb + D1, [X(lc - BASE_W / 2), X(0), X(LEG), X(lc + BASE_W / 2)], [yb, Yg(BASE_H), Yg(BASE_H), yb],
           [f"{sd:g}", f"{LEG}", f"{sd:g}"], size=K.F_DIM_MAIN, bg=True)
    HM(X(lc - BASE_W / 2), X(lc + BASE_W / 2), yb + D2, f"{BASE_W}", yb, yb)
    # dešinė: tarpas 100 + profilis 120
    xr = X(BW) + D1
    vchain(xr, [Yg(Y_BOX0), Yg(Y_PR0 + PR_H), Yg(Y_PR0)], [X(BW), X(PR_X + PR_L), X(PR_X + PR_L)],
           [f"{PR_GAP}", f"{PR_H}"], size=K.F_DIM_MAIN, bg=True)
    # laisvas aukštis 2700 - nuo žemės iki profilio apačios
    xc = X(PR_X + PR_L * 0.3)
    line(X(lc + BASE_W / 2) + 2, yb, xc + 6, yb, 0.25, K.EXT)
    vchain(xc, [Yg(Y_PR0), yb], [xc, xc], [f"{CLEAR}"], size=K.F_DIM_MAIN, bg=True)
    # žymos (automatinis išdėstymas)
    bb = G["bb"]
    gx0, gy0, gx1, gy1 = bb["glow"]
    K.tag(X(gx0 + 60), Yg(TOT_H) + (gy0 + gy1) / 2 * s, X(LEG + 120), Yg(Y_BOX0) + 34, "Glowing: 10 + 12", size=8)
    sx0, sy0, sx1, sy1 = bb["sticker"]
    K.balloon_auto(X((sx0 + sx1) / 2), Yg(TOT_H) + sy1 * s - 2, "Sticker: 13", kind="tag", size=8, prefer=[315])
    K.balloon_auto(X(BW * 0.97), Yg(TOT_H - BOXH * 0.15), 9)
    K.balloon_auto(X(PR_X + HANG[1]), Yg(Y_BOX0 - PR_GAP * 0.3), "8A")
    K.balloon_auto(X(LEG * 0.5), Yg(1500), 1)
    K.balloon_auto(X(lc + BASE_W * 0.35), Yg(BASE_H * 0.5), 7)
    K.cut_plane(X(1500), Yg(TOT_H) - D2 - 10, Yg(Y_PR0), "A", look="right")
    view_title(X(BW / 2), K.IY0 + 22, "FRONT VIEW", "1:25")


def side_view(X0, YG, s):
    """vaizdas iš dešinės; x - gylis nuo centro"""
    X = lambda z: X0 + z * s
    Yg = lambda y: YG - y * s
    K.set_view(True)
    rect(X(-BASE_D / 2), Yg(BASE_H), BASE_D * s, BASE_H * s, fill=C_GREY, lw=0.1)
    line(X(0), Yg(BASE_H), X(0), Yg(0), 0.1)                       # 2 uždengimo pusės (7)
    rect(X(-LEG / 2), Yg(Y_BOX0), LEG * s, LEG_TOP * s, fill=C_GREY, lw=0.1)
    rect(X(-BD / 2), Yg(TOT_H), BD * s, BOXH * s, fill=C_BLUE, lw=0.1)
    line(X(0), Yg(TOT_H), X(0), Yg(Y_BOX0), 0.1)                   # sandūra 9 / 9
    line(X(0), Yg(Y_BOX0), X(0), Yg(Y_PR0 + PR_H), 0.1)            # pakaba
    rect(X(-PR_D / 2), Yg(Y_PR0 + PR_H), PR_D * s, PR_H * s, fill=C_BLACK, lw=0.1)
    K.set_view(False)
    detail_mark(X(0), Yg(Y_BOX0 - PR_GAP / 2), 11, "B")
    yt = Yg(TOT_H)
    HM(X(-BD / 2), X(BD / 2), yt - D1, f"{BD}", yt, yt)
    ym = Yg(1500)
    HM(X(-LEG / 2), X(LEG / 2), ym, f"{LEG}", None, None)
    yb = Yg(0)
    HM(X(-BASE_D / 2), X(BASE_D / 2), yb + D1, f"{BASE_D}", yb, yb)
    K.balloon_auto(X(PR_D / 2), Yg(Y_PR0 + PR_H * 0.3), 8)
    K.balloon_auto(X(LEG / 2), Yg(2200), 1)
    view_title(X(0), K.IY0 + 22, "SIDE VIEW (RIGHT)", "1:25")


def plate_view(X0, Y0, s):
    """montavimo plokštė 2 iš viršaus; X0, Y0 - kairys viršus"""
    X = lambda x: X0 + x * s
    Yp = lambda y: Y0 + y * s
    cx, cy = PL_W / 2, PL_D / 2
    K.set_view(True)
    rect(X(0), Yp(0), PL_W * s, PL_D * s, fill=HexColor("#C9C9C9"), lw=0.1)
    hx = [cx - PL_HX, cx, cx + PL_HX]
    hy = [cy - PL_HY / 2, cy + PL_HY / 2]
    for x in hx:
        for y in hy:
            circle(X(x), Yp(y), PL_HD / 2 * s, fill=white, lw=0.1)
    # gamybinis failas: Ø40 kabelio anga 241.5 nuo centro, anga kojai □184 (koja per plokštę)
    hx2 = cx + CABLE_HX
    circle(X(hx2), Yp(cy), CABLE_D / 2 * s, fill=white, lw=0.1)
    rect(X(cx - SQ / 2), Yp(cy - SQ / 2), SQ * s, SQ * s, fill=white, lw=0.1)
    rect(X(cx - LEG / 2), Yp(cy - LEG / 2), LEG * s, LEG * s, fill=C_GREY, lw=0.1)
    rect(X(cx - LEG / 2 + 5), Yp(cy - LEG / 2 + 5), (LEG - 10) * s, (LEG - 10) * s, fill=white, lw=0.1)
    K.set_view(False)
    for x in hx + [hx2]:
        K.centerline(X(x), Yp(cy - PL_HY / 2) - 8 if x != hx2 else Yp(cy) - 8, X(x), Yp(cy + PL_HY / 2) + 8 if x != hx2 else Yp(cy) + 8)
    for y in hy + [cy]:
        K.centerline(X(0) - 6, Yp(y), X(PL_W) + 6, Yp(y))
    yt = Yp(0)
    hchain(yt - D1, [X(cx - PL_HX), X(cx), X(cx + PL_HX)], [Yp(hy[0])] * 3, [f"{PL_HX}", f"{PL_HX}"],
           size=K.F_DIM_MAIN, bg=True)
    HM(X(0), X(PL_W), yt - D2, f"{PL_W}", yt, yt)
    VM(X(PL_W) + D1, Yp(hy[0]), Yp(hy[1]), X(cx + PL_HX), f"{PL_HY}")
    VM(X(PL_W) + D2, Yp(0), Yp(PL_D), X(PL_W), f"{PL_D}")
    K.balloon_auto(X(cx + PL_HX) + PL_HD / 2 * s * 0.7, Yp(hy[1]) + PL_HD / 2 * s * 0.7, f"6 x Ø{PL_HD}", kind="tag", size=8)
    K.balloon_auto(X(hx2) + CABLE_D / 2 * s * 0.7, Yp(cy) + CABLE_D / 2 * s * 0.7, f"Ø{CABLE_D} cable", kind="tag", size=8)
    hchain(Yp(PL_D) + D1, [X(cx), X(hx2), X(PL_W)], [Yp(cy)] * 2 + [Yp(PL_D)], [f"{CABLE_HX:g}", f"{PL_W - hx2:g}"],
           size=K.F_DIM_MAIN, bg=True)
    K.balloon_auto(X(cx - LEG / 2), Yp(cy - LEG / 2 + 20), 1)
    K.balloon_auto(X(PL_W * 0.85), Yp(PL_D * 0.15), 2)
    view_title(X(PL_W / 2), Y0 - D2 - 30, "MOUNTING PLATE (2) - TOP VIEW", f"1:10   t = {PL_T} mm, □{SQ} for leg 1")


def view3d(G, box):
    import r3d
    sc = r3d.Scene(yaw=-30, pitch=16)
    lc = LEG / 2
    sc.box((lc - BASE_W / 2, 0, -BASE_D / 2), (BASE_W, 0, 0), (0, BASE_H, 0), (0, 0, BASE_D), C_GREY, edge=EDGE)
    sc.box((0, BASE_H, -LEG / 2), (LEG, 0, 0), (0, LEG_TOP, 0), (0, 0, LEG), C_GREY, edge=EDGE)
    sc.box((0, Y_BOX0, -BD / 2), (BW, 0, 0), (0, BOXH, 0), (0, 0, BD), C_BLUE, edge=EDGE)
    sc.box((PR_X, Y_PR0, -PR_D / 2), (PR_L, 0, 0), (0, PR_H, 0), (0, 0, PR_D), C_BLACK, edge=EDGE)
    for hx in HANG:
        sc.box((PR_X + hx - 15, Y_PR0 + PR_H, -1.5), (30, 0, 0), (0, PR_GAP, 0), (0, 0, 3), HexColor("#B4B4B4"), edge=EDGE)
    sc.render(box)
    V = sc.V
    zf = BD / 2
    if V.rot(0, 0, 1)[2] > 0:
        def xf(u, v):
            px, py = V.S(u, TOT_H - v, zf + 0.5); return px, K.H - py
        draw_rings(G["glow"] + G["sticker"], xf, white)

        def xf2(u, v):
            px, py = V.S(PR_X + u, Y_PR0 + PR_H - v, PR_D / 2 + 0.5); return px, K.H - py
        draw_rings(G["fri"], xf2, white)
    view_title(box[0] + box[2] / 2, box[1] - 30, "3D VIEW", "ILLUSTRATIVE - NOT TO SCALE")



# ---------------------------------------------------------------- vidinė konstrukcija (rev B)
# Kliento exploded view: 1 koja + 4 viršutinis □80 (suvirinta) + 6 atrama po 4 + 5 rėmas □40 (apatinis bėgis su LED,
# statmenys), 9 dvi lovelės (priekis / galas), 10 plexi už išpjovų, 7 dvi uždengimo pusės, 3 atramos prie plokštės,
# 11 jungčių dėžutė ant plokštės. Matmenys, kurių kliento lape nėra, - * ALT PASIŪLYMAS (lape pažymėta, klausimai Q).
T9 = 2                                  # 9 lovelės skarda 2 mm (gamybinis failas: atlankas 98 + 2 = 100)
B4, B4W, B4T = 100, 80, 3               # 4: gamybiniame faile 100 aukščio (kliento lape □80x80x3) - Q
R5, R5T = 40, 2                         # 5 □40x40x2
LX0 = 3                                 # rėmo nulis (kojos išorė) nuo dėžės krašto: 2 skarda + 1 laisvumas
FR_L = 2994                             # rėmo ilgis (gamybinis failas)
Y_B4T = TOT_H - T9 - 1                  # 3437
Y_B4B = Y_B4T - B4                      # 3337
X_END = LX0 + FR_L                      # 2997
B4_L = FR_L                             # 2994
LEG_L = Y_B4B                           # 3337 - koja per plokštės angą □184 iki pagrindo (gamybinis failas)
V5_L = 374                              # statmenys (gamybinis failas)
Y_R5T = Y_B4B - V5_L                    # 2963
Y_R5B = Y_R5T - R5                      # 2923
R5_L = FR_L - LEG                       # 2814
VERTS = [LX0 + 797, LX0 + 2380, LX0 + 2974]   # statmenų ašys: kairys kraštas 777 / 2360 / 2954 nuo kojos išorės
HANG_F = (1134.5, 2043.4)               # pakabų ašys nuo kojos išorės (gamybinis failas)
G3_L, G3_H, G3_C = 500, 127, 63.5       # 3 atramos 500 x 127 x 5, nuožulos 63.5 (gamybinis failas, 2 vnt.)
G3_TOP = G3_L - 2 * G3_C
S6, S6_B = 228.1, 61.3                  # 6: viršus 228 po 4, apačia 61 ant 5, aukštis 374 (gamybinis failas)
SQ = 184                                # plokštės anga kojai □184 (koja 180 + 2 x 2)
CABLE_HX = 691.5 - PL_W / 2             # Ø40 kabelio anga: 241.5 nuo centro (gamybinis failas, vaizdas iš viršaus)
CABLE_D = 40
JB = (95, 205, 100)                     # 11 dėžutė x0, x1, aukštis nuo plokštės centro * (vieta - pasiūlymas)
PLEXI_OV = 16                           # 10 plexi: 2535 x 325 bendras (gamybinis), užlaida ≈ 16-24
SCREW_P = 322                           # Ø3.2 skylės atlankuose kas 322.2, 4.6 nuo atlanko krašto (gamybinis)
N_LED = 11                              # kliento exploded - 11 modulių (kiekis nepatvirtintas)

C_STEEL = HexColor("#8E99A4")           # plienas (vidinis rėmas) - medžiagos spalva
C_PLEXI = HexColor("#F4F4F2")
C_LED = HexColor("#F2C230")
C_JB = HexColor("#D5D5D5")
C_HANG = HexColor("#B4B4B4")
RED = HexColor("#C8102E")
HATCH_STEEL = HexColor("#4A4A4A")


def s6_pts():
    x0 = LX0 + LEG
    return [(x0, Y_B4B), (x0 + S6, Y_B4B), (x0 + S6_B, Y_R5T), (x0, Y_R5T)]


def plexi_geom(G):
    """10: plexi = švytinčios išpjovos + PLEXI_OV užlaida (y aukštyn, mm)"""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    ps = []
    for r in G["glow"]:
        p = Polygon([(u, TOT_H - v) for u, v in r]).buffer(0)
        if p.area > 50:
            ps.append(p)
    U = unary_union(ps).buffer(PLEXI_OV, join_style=2)
    return list(getattr(U, "geoms", [U]))


def detail_b(X0, BY0, W0, BH):
    """DETAIL B - pakaba 8A 1:5 (pjūvis skersai): 8 kabinamas ant 2 pakabų, pakaba per 9 atlankus prisukta į 5"""
    K.header(X0, BY0, W0, "DETAIL B - HANGER 8A  1:5")
    rect(X0, BY0 + 12, W0, BH - 12, lw=0.6)
    K.AUTO["region"] = (X0 + 3, BY0 + 15, X0 + W0 - 3, BY0 + BH - 3)
    s = MM / 5
    cx = X0 + W0 * 0.40
    yb = BY0 + BH - 22
    Z = lambda z: cx - z * s                                    # priekis (z+) kairėje
    Yv = lambda y: yb - (y - Y_PR0) * s
    K.set_view(True)
    ytop = Y_BOX0
    ycut = Y_R5T + 8
    for zs in (1, -1):                                          # 9 priekis / galas: dugno atlankas + šonas (lūžis)
        z_out = zs * BD / 2
        rect(min(Z(z_out), Z(0)), Yv(ytop + T9), abs(Z(z_out) - Z(0)), T9 * s, fill=C_BLUE, lw=0.1)
        rect(min(Z(z_out), Z(z_out - zs * T9)), Yv(ycut), T9 * s, (ycut - ytop) * s, fill=C_BLUE, lw=0.1)
    line(Z(BD / 2) - 4, Yv(ycut), Z(-BD / 2) + 4, Yv(ycut), 0.1, dash=([4, 1, 1, 1], 0))
    rect(Z(R5 / 2), Yv(Y_R5T), R5 * s, R5 * s, fill=C_STEEL, lw=0.1)                       # 5
    rect(Z(R5 / 2 - R5T), Yv(Y_R5T - R5T), (R5 - 2 * R5T) * s, (R5 - 2 * R5T) * s, fill=white, lw=0.1)
    rect(Z(PR_D / 2), Yv(Y_PR0 + PR_H), PR_D * s, PR_H * s, fill=C_BLACK, lw=0.1)          # 8
    rect(Z(PR_D / 2 - PR_T), Yv(Y_PR0 + PR_H - PR_T), (PR_D - 2 * PR_T) * s, (PR_H - 2 * PR_T) * s, fill=white, lw=0.1)
    th = 3                                                      # 8A: Z forma, 3 mm Alu
    yp = Y_PR0 + PR_H
    rect(Z(PR_D / 2 - 4), Yv(yp + th), (PR_D / 2 - 4 + th / 2) * s, th * s, fill=C_HANG, lw=0.1)
    rect(Z(th / 2), Yv(ytop), th * s, (ytop - yp - th) * s, fill=C_HANG, lw=0.1)
    rect(Z(th / 2), Yv(ytop), 32 * s, th * s, fill=C_HANG, lw=0.1)                          # viršutinis atlankas
    K.set_view(False)
    SCRC = HexColor("#3A3A3A")
    for zz, y0, y1 in ((PR_D / 4, yp - PR_T - 4, yp + th + 2), (-14, ytop - th - 2, ytop + T9 + R5T + 6)):
        rect(Z(zz) - 1.5 * s, Yv(y1), 3 * s, (y1 - y0) * s, fill=SCRC, lw=0.1)
        K.centerline(Z(zz), Yv(y1 + 8), Z(zz), Yv(y0 - 8))
    hchain(Yv(Y_PR0) + 10, [Z(PR_D / 2), Z(-PR_D / 2)], [Yv(Y_PR0)] * 2, [f"{PR_D}"], size=K.F_DIM_FRAME, bg=True)
    vchain(Z(-BD / 2) - 12, [Yv(ytop), Yv(yp), Yv(Y_PR0)], [Z(-BD / 2), Z(-PR_D / 2), Z(-PR_D / 2)],
           [f"{PR_GAP}", f"{PR_H}"], size=K.F_DIM_FRAME, bg=True)
    rg = K.AUTO["region"]
    K.balloon_auto(Z(PR_D / 2), Yv(Y_PR0 + PR_H * 0.4), 8, region=rg)
    K.balloon_auto(Z(th / 2), Yv(yp + PR_GAP * 0.45), "8A", region=rg)
    K.balloon_auto(Z(BD / 2 - 40), Yv(ytop + T9 / 2), 9, region=rg)
    K.balloon_auto(Z(-R5 / 2), Yv(Y_R5T - R5 / 2), 5, region=rg)
    K.balloon_auto(Z(-14) - 1.5 * s, Yv(ytop + T9 + 6), "M6", kind="tag", region=rg, size=8)
    T(X0 + W0 - 4, BY0 + 80, "8A = 2 x L 45x110x3", 8, color=K.GREY, align="r")
    T(X0 + W0 - 4, BY0 + 90, "Ø6 + slot 6x20, M6", 8, color=K.GREY, align="r")
    K.AUTO["region"] = None


# ---------------------------------------------------------------- BOM / MAIN DATA (1 lapas)
def bom():
    return [
        [1, "Leg □180x180x5 - through plate 2 to beam 4", "Steel, welded", "NCS S 2500-N", f"1 pc., L {LEG_L}"],
        [2, f"Plate {PL_W}x{PL_D}x{PL_T}, □{SQ}, 6xØ{PL_HD}, Ø{CABLE_D}", "Steel, welded to 1", "", "1 pc."],
        [3, f"Supports {G3_L}x{G3_H}x5, leg front + back", "Steel, welded 1 + 2", "", "2 pcs."],
        [4, f"Top frame {B4}x{B4W}x{B4T}? (client □80)", "Steel, welded on 1", "", f"1 pc., L {B4_L}"],
        [5, "Frame □40x40x2 - bottom rail + 3 verticals", "Steel, welded 1 + 4", "", f"{R5_L} + 3 x {V5_L:g}"],
        [6, f"Support 5 mm {S6:.0f} / {S6_B:.0f} x {V5_L:g} - leg, 4 - 5", "Steel, welded 1 + 4 + 5", "", "1 pc."],
        [7, "Bottom cover, flat 1002x325 + strip", "Alu 1.5 mm, folded", "NCS S 2500-N", "2 + 2 pcs."],
        [8, f"Height profile {PR_H}x{PR_D}x{PR_T}", "Alu", "RAL 9005", f"1 pc., {PR_L} mm"],
        ["8A", "Hanger: 2 x L 45x110 (DETAIL B)", "Alu 3 mm, folded", "", "8 pcs. (4 sets)"],
        [9, f"Tray {BW}x{BOXH}x{BD // 2}, flat 3196x716", "Alu 2 mm, folded", "NCS S 4055-R70B", "2 pcs."],
        [10, "Glowing: arrows + Biltvätt, behind 9", "Plexiglass 3 mm white", "-", "3 pcs."],
        [11, "Junction box - on plate 2", "IP65:", "-", "1 pc."],
        [12, "LED's - on top of rail 5", "", "", "pcs.:"],
        [13, "Decals: car + showers, FRI HÖJD 2,70m.", "Vinyl foil, cast", "ORACAL 551 101", "1 set"],
    ]


def weight():
    st, al = 7.85e-6, 2.7e-6
    leg = (LEG ** 2 - (LEG - 10) ** 2) * LEG_L * st
    plate = PL_W * PL_D * PL_T * st
    top = (B4 ** 2 - (B4 - 2 * B4T) ** 2) * B4_L * st
    frame = (R5 ** 2 - (R5 - 2 * R5T) ** 2) * (R5_L + 3 * V5_L) * st
    gus = 2 * (G3_L * G3_H - G3_C ** 2) * 5 * st + (S6 + S6_B) / 2 * V5_L * 5 * st
    faces = 2 * (BW * BOXH + 2 * BW * BD / 2 + 2 * BOXH * BD / 2) * T9 * al
    prof = (PR_H * PR_D - (PR_H - 4) * (PR_D - 4)) * PR_L * al
    cover = (BASE_W * BASE_D + 2 * (BASE_W + BASE_D) * BASE_H) * 1.5 * al
    return leg + plate + top + frame + gus + faces + prof + cover


def main_data():
    return [["Product", "height restriction, cantilever, 1 leg"],
            ["Overall", f"{BW} x {TOT_H} x {BASE_D} mm"],
            ["Sign box", f"{BW} x {BOXH} x {BD} mm (2 trays 9)"],
            ["Clear height", f"{CLEAR} mm (FRI HÖJD 2,70m.)"],
            ["Structure", "steel 1-6 welded (sheet 2)"],
            ["Anchors", f"6 x Ø{PL_HD}:"],
            ["Glowing", "arrows + Biltvätt (10 + 12)"],
            ["Stickers", "car + showers, FRI HÖJD (13)"],
            ["Backside", "graphics:"],
            ["Power", "voltage / cable:"],
            ["Qty", "1 pcs."],
            ["Weight (calc.)", f"≈ {weight():.0f} kg / pcs, excl. LED"],
            ["*", "ALT proposal - not in production file (Q)"]]


TB = {"client": "Skyltkoncept Sweden AB (OKQ8)", "title": "OKQ8 HEIGHT RESTRICTION - BILTVÄTT",
      "order_no": "ALT8877_10.13_RS", "drawing_no": "okq8 height restriction", "rev": "C", "date": "2026-10-13",
      "revisions": [["A", "First issue", "2026-10-13", "RS"], ["B", "Structure, exploded, sections", "2026-10-13", "RS"], ["C", "Data from production file", "2026-10-13", "RS"]]}


def sheet1(G, out):
    md, bm = main_data(), bom()
    K.set_band(max(len(md), len(bm) + 1))
    K.init(out + ".tmp", "ALT8877 OKQ8 height restriction - GA")
    K.frame()
    s25 = MM / 25
    YG = K.VIEW_BOT - 62
    X0 = K.IX0 + 106
    front_view(G, X0, YG, s25)
    xs = X0 + BW * s25 + D1 + 40 + 50 + BASE_D / 2 * s25
    side_view(xs, YG, s25)
    s10 = MM / 10
    px0 = K.IX1 - 72 - PL_W * s10
    plate_view(px0, K.IY0 + 108, s10)
    x3 = xs + BASE_D / 2 * s25 + 60
    view3d(G, (x3, K.IY0 + 345, K.IX1 - 10 - x3, YG - (K.IY0 + 345) + 30))
    BY0 = K.BAND_Y; BH = K.IY1 - BY0
    W_D, W_MD, W_TB = 214, 230, 272
    X_D = K.IX0; X_TB = K.IX1 - W_TB; X_MD = X_TB - W_MD; X_BOM = X_D + W_D; W_BOM = X_MD - X_BOM
    detail_b(X_D, BY0, W_D, BH)
    K.bom_table(X_BOM, BY0, W_BOM, BH, bm,
                cols=(("POS", 20), ("PART", 0.38), ("MATERIAL", 0.23), ("FINISH", 0.17), ("QTY", None)))
    K.main_data(X_MD, BY0, W_MD, BH, md, lab_w=64)
    K.title_block(X_TB, W_TB, dict(TB, sheet="1 / 2", title=TB["title"] + " - GA"), "1:25 / 1:10 / 1:5")
    K.save(out)


# ---------------------------------------------------------------- 2 lapas: konstrukcija
def exploded(G, box):
    """EXPLODED VIEW - kaip kliento, mūsų stiliumi; medžiagos spalvomis (MATERIALS KEY)"""
    import r3d
    from shapely.geometry import Polygon
    sc = r3d.Scene(yaw=-26, pitch=18)
    lc = LX0 + LEG / 2
    E = {"9F": 1500, "9B": -1000, "10": 800, "8": -650, "7": 700, "7y": -200}
    # plokštė 2 + atramos 3 + koja 1 + 4 + 6 + 5
    sc.box((lc - PL_W / 2, 0, -PL_D / 2), (PL_W, 0, 0), (0, PL_T, 0), (0, 0, PL_D), C_STEEL, edge=EDGE)
    for zs in (1, -1):
        g3 = Polygon([(lc - G3_L / 2, PL_T), (lc + G3_L / 2, PL_T), (lc + G3_L / 2, PL_T + G3_H - G3_C), (lc + G3_TOP / 2, PL_T + G3_H), (lc - G3_TOP / 2, PL_T + G3_H), (lc - G3_L / 2, PL_T + G3_H - G3_C)])
        z0 = zs * (LEG / 2) if zs > 0 else -LEG / 2 - 5
        sc.extrude_xy(g3, z0, z0 + 5, C_STEEL, C_STEEL, edge=EDGE)
    sc.box((LX0, 0, -LEG / 2), (LEG, 0, 0), (0, LEG_L, 0), (0, 0, LEG), C_GREY, edge=EDGE)
    sc.box((LX0, Y_B4B, -B4W / 2), (B4_L, 0, 0), (0, B4, 0), (0, 0, B4W), C_STEEL, edge=EDGE)
    sc.extrude_xy(Polygon(s6_pts()), -2.5, 2.5,
                  C_STEEL, C_STEEL, edge=EDGE)
    sc.box((LX0 + LEG, Y_R5B, -R5 / 2), (R5_L, 0, 0), (0, R5, 0), (0, 0, R5), C_STEEL, edge=EDGE)
    for vx in VERTS:
        sc.box((vx - R5 / 2, Y_R5T, -R5 / 2), (R5, 0, 0), (0, V5_L, 0), (0, 0, R5), C_STEEL, edge=EDGE)
    gx0, _, gx1, _ = G["bb"]["glow"]
    led_x = [gx0 + (gx1 - gx0) * (i + 0.5) / N_LED for i in range(N_LED)]
    for x in led_x:
        sc.box((x - 30, Y_R5T, -12), (60, 0, 0), (0, 8, 0), (0, 0, 24), C_LED, edge=EDGE)
    # 11 dėžutė
    sc.box((lc + JB[0], PL_T, -50), (JB[1] - JB[0], 0, 0), (0, JB[2], 0), (0, 0, 100), C_JB, edge=EDGE)
    # 10 plexi
    for p in plexi_geom(G):
        sc.extrude_xy(p, BD / 2 - T9 - 3 + E["10"], BD / 2 - T9 + E["10"], C_PLEXI, C_PLEXI, edge=EDGE)
    # 9 lovelės: veidas + atlankai (viršus, apačia su išpjova kojai, galai)
    for key, zs in (("9F", 1), ("9B", -1)):
        dz = E[key]
        zf = zs * BD / 2
        zi = zf - zs * T9
        zl, zh = (0, zi) if zs > 0 else (zi, 0)
        if zs > 0:
            sc.box((0, Y_BOX0, zi + dz), (BW, 0, 0), (0, BOXH, 0), (0, 0, T9), C_BLUE, edge=EDGE)
        else:
            sc.box((0, Y_BOX0, zf + dz), (BW, 0, 0), (0, BOXH, 0), (0, 0, T9), C_BLUE, edge=EDGE)
        sc.box((0, TOT_H - T9, zl + dz), (BW, 0, 0), (0, T9, 0), (0, 0, zh - zl), C_BLUE, edge=EDGE)
        sc.box((LX0 + LEG, Y_BOX0, zl + dz), (BW - LX0 - LEG, 0, 0), (0, T9, 0), (0, 0, zh - zl), C_BLUE, edge=EDGE)
        for x0 in (0, BW - T9):
            sc.box((x0, Y_BOX0, zl + dz), (T9, 0, 0), (0, BOXH, 0), (0, 0, zh - zl), C_BLUE, edge=EDGE)
    # 8 + 8A
    for hx in HANG:
        sc.box((PR_X + hx - 15, Y_PR0 + PR_H + E["8"], -1.5), (30, 0, 0), (0, PR_GAP, 0), (0, 0, 3), C_HANG, edge=EDGE)
    sc.box((PR_X, Y_PR0 + E["8"], -PR_D / 2), (PR_L, 0, 0), (0, PR_H, 0), (0, 0, PR_D), C_BLACK, edge=EDGE)
    # 7 dvi pusės
    for zs in (1, -1):
        dz = zs * E["7"]
        z0 = 0 if zs > 0 else -BASE_D / 2
        sc.box((lc - BASE_W / 2, E["7y"], z0 + dz), (BASE_W, 0, 0), (0, BASE_H, 0), (0, 0, BASE_D / 2), C_GREY, edge=EDGE)
    sc.render(box)
    V = sc.V
    P = lambda x, y, z: (V.S(x, y, z)[0], K.H - V.S(x, y, z)[1])
    # grafika ant priekinės lovelės (išpjovos - šviesios) ir ant profilio
    if V.rot(0, 0, 1)[2] > 0:
        zf = BD / 2 + E["9F"] + 0.5
        draw_rings(G["glow"] + G["sticker"], lambda u, v: P(u, TOT_H - v, zf), white)
        draw_rings(G["fri"], lambda u, v: P(PR_X + u, Y_PR0 + E["8"] + PR_H - v, PR_D / 2 + 0.5), white)
    # surinkimo kryptys (brūkšnys-taškas)
    for (a, b) in (((BW * 0.93, Y_BOX0 + BOXH * 0.3, 40), (BW * 0.93, Y_BOX0 + BOXH * 0.3, BD / 2 + E["9F"])),
                   ((BW * 0.93, Y_BOX0 + BOXH * 0.3, -40), (BW * 0.93, Y_BOX0 + BOXH * 0.3, -BD / 2 + E["9B"])),
                   ((PR_X + HANG[0], Y_R5B, 0), (PR_X + HANG[0], Y_PR0 + PR_H + PR_GAP + E["8"], 0)),
                   ((lc + BASE_W * 0.4, BASE_H * 0.5, BASE_D / 2), (lc + BASE_W * 0.4, E["7y"] + BASE_H * 0.5, BASE_D / 2 + E["7"]))):
        (x1, y1), (x2, y2) = P(*a), P(*b)
        line(x1, y1, x2, y2, 0.25, K.GREY, dash=([5, 2, 1, 2], 0))
    tg = [(P(lc, PL_T + 1500, LEG / 2), 1), (P(lc + PL_W * 0.4, PL_T, PL_D * 0.4), 2),
          (P(lc - G3_L * 0.3, PL_T + G3_H * 0.4, LEG / 2 + 5), 3), (P(BW * 0.55, Y_B4T, 0), 4),
          (P(VERTS[1], Y_R5T + V5_L * 0.5, R5 / 2), 5), (P(LX0 + LEG + S6 * 0.3, Y_B4B - 60, 2.5), 6),
          (P(lc - BASE_W * 0.35, E["7y"] + BASE_H, BASE_D / 2 + E["7"]), 7),
          (P(PR_X + PR_L * 0.85, Y_PR0 + E["8"], PR_D / 2), 8), (P(PR_X + HANG[1], Y_PR0 + PR_H + PR_GAP * 0.6 + E["8"], 1.5), "8A"),
          (P(BW * 0.5, Y_BOX0 + 4, BD / 2 + E["9F"]), 9), (P(BW * 0.3, TOT_H - T9, -BD / 2 + E["9B"] + 40), 9),
          (P(led_x[2], Y_R5T + 4, 12), 12), (P(lc + JB[0], PL_T + JB[2] * 0.6, 50), 11)]
    pl = plexi_geom(G)
    big = max(pl, key=lambda p: p.area)
    tg.append((P(big.bounds[0] + 30, big.bounds[1] + 20, BD / 2 - T9 + E["10"]), 10))
    for (x, y), n in tg:
        K.balloon_auto(x, y, n, region=(box[0], box[1], box[0] + box[2], box[1] + box[3]))
    # suvirinimo žymos (kaip kliento „Weldded")
    for a in ((LX0 + LEG, Y_B4B, LEG / 2), (LX0, Y_B4B, LEG / 2)):
        x, y = P(*a)
        circle(x, y, 3.2, stroke=RED, lw=0.6)
    xw, yw = P(LX0, Y_B4B, LEG / 2)
    K.balloon_auto(xw, yw, "Welded 1 + 4 + 6", kind="tag", size=8, region=(box[0], box[1], box[0] + box[2], box[1] + box[3]))
    view_title(box[0] + box[2] / 2, K.IY0 + 22, "EXPLODED VIEW", "ILLUSTRATIVE - NOT TO SCALE")


def frame_view(G, X0, YG, s):
    """STEEL FRAME 1-6 - priekio vaizdas 1:50 (dėžė ir uždengimas - punktyru)"""
    X = lambda x: X0 + x * s
    Yg = lambda y: YG - y * s
    lc = LX0 + LEG / 2
    K.set_view(True)
    rect(X(0), Yg(TOT_H), BW * s, BOXH * s, lw=0.1, dash=(3, 2))                      # 9 kontūras
    rect(X(lc - BASE_W / 2), Yg(BASE_H), BASE_W * s, BASE_H * s, lw=0.1, dash=(3, 2))   # 7 kontūras
    rect(X(lc - PL_W / 2), Yg(PL_T), PL_W * s, PL_T * s, fill=C_STEEL, lw=0.1)
    poly([(X(lc - G3_L / 2), Yg(PL_T)), (X(lc + G3_L / 2), Yg(PL_T)), (X(lc + G3_L / 2), Yg(PL_T + G3_H - G3_C)),
          (X(lc + G3_TOP / 2), Yg(PL_T + G3_H)), (X(lc - G3_TOP / 2), Yg(PL_T + G3_H)),
          (X(lc - G3_L / 2), Yg(PL_T + G3_H - G3_C))], fill=C_STEEL, lw=0.1)
    rect(X(LX0), Yg(Y_B4B), LEG * s, LEG_L * s, fill=C_GREY, lw=0.1)
    for hx in HANG_F:
        line(X(LX0 + hx), Yg(Y_R5B) + 2, X(LX0 + hx), Yg(Y_R5T) - 2, 0.6)
    rect(X(LX0), Yg(Y_B4T), B4_L * s, B4 * s, fill=C_STEEL, lw=0.1)
    poly([(X(a), Yg(b)) for a, b in s6_pts()], fill=C_STEEL, lw=0.1)
    rect(X(LX0 + LEG), Yg(Y_R5T), R5_L * s, R5 * s, fill=C_STEEL, lw=0.1)
    for vx in VERTS:
        rect(X(vx - R5 / 2), Yg(Y_B4B), R5 * s, V5_L * s, fill=C_STEEL, lw=0.1)
    gx0, _, gx1, _ = G["bb"]["glow"]
    for i in range(N_LED):
        x = gx0 + (gx1 - gx0) * (i + 0.5) / N_LED
        rect(X(x - 30), Yg(Y_R5T + 8), 60 * s, 8 * s, fill=C_LED, lw=0.1)
    rect(X(lc + JB[0]), Yg(PL_T + JB[2]), (JB[1] - JB[0]) * s, JB[2] * s, fill=C_JB, lw=0.1)
    K.set_view(False)
    # matmenys: viršuje 4 ilgis, rėmo statmenų grandinė; kairėje koja, dešinėje statmuo
    yt = Yg(TOT_H)
    hchain(yt - D1, [X(LX0 + LEG), X(VERTS[0]), X(VERTS[1]), X(VERTS[2])], [Yg(Y_R5T)] * 4,
           [f"{VERTS[0] - LX0 - LEG:g}", f"{VERTS[1] - VERTS[0]:g}", f"{VERTS[2] - VERTS[1]:g}"], size=K.F_DIM_FRAME, bg=True)
    HM(X(LX0), X(X_END), yt - D2, f"{B4_L} (4)", Yg(Y_B4T), Yg(Y_B4T))
    xl = X(lc - BASE_W / 2)
    vchain(xl - D1, [Yg(Y_B4T), Yg(Y_B4B), Yg(0)], [X(LX0), X(LX0), X(lc - PL_W / 2)],
           [f"{B4}", f"{LEG_L} (1)"], size=K.F_DIM_FRAME, bg=True)
    xr = X(BW) + D1
    vchain(xr, [Yg(Y_B4B), Yg(Y_R5T), Yg(Y_R5B)], [X(VERTS[2] + R5 / 2), X(X_END), X(X_END)],
           [f"{V5_L:g}", f"{R5}"], size=K.F_DIM_FRAME, bg=True)
    yb = Yg(0)
    hchain(yb + D1, [X(lc - G3_L / 2), X(lc + G3_L / 2)], [Yg(PL_T)] * 2, [f"{G3_L}"], size=K.F_DIM_FRAME, bg=True)
    yh = Yg(Y_R5B) + 14
    hchain(yh, [X(LX0), X(LX0 + HANG_F[0]), X(LX0 + HANG_F[1])], [Yg(Y_R5B)] * 3,
           [f"{HANG_F[0]:g}", f"{HANG_F[1] - HANG_F[0]:.1f} (8A)"], size=K.F_DIM_FRAME, bg=True)
    HM(X(LX0 + LEG), X(X_END), yh + 22, f"{R5_L} (5)", Yg(Y_R5B), Yg(Y_R5B))
    for (x, y, n) in ((X(lc), Yg(1800), 1), (X(lc + PL_W * 0.42), Yg(PL_T / 2), 2), (X(lc + G3_L * 0.35), Yg(PL_T + 40), 3),
                      (X(BW * 0.45), Yg(Y_B4T - B4 / 2), 4), (X(VERTS[1]), Yg(Y_B4B - V5_L * 0.5), 5),
                      (X(LX0 + LEG + S6 * 0.3), Yg(Y_B4B - S6 * 0.3), 6), (X(gx0 + 200), Yg(Y_R5T + 4), 12),
                      (X(lc + (JB[0] + JB[1]) / 2), Yg(PL_T + JB[2] / 2), 11)):
        K.balloon_auto(x, y, n)
    view_title(X(BW / 2), K.IY0 + 22, "STEEL FRAME 1-6 (FRONT)", "1:50   9 / 7 - dashed")


def section_aa(G, X0, Ytop, s):
    """SECTION A-A per dėžę ir profilį (x = 1500), priekis (9 su išpjova) - kairėje"""
    Z = lambda z: X0 - z * s
    Yv = lambda y: Ytop + (TOT_H - y) * s
    K.set_view(True)
    for zs in (1, -1):
        zf = zs * BD / 2
        zl, zh = sorted((zf, zf - zs * T9))
        rect(Z(zh), Yv(TOT_H), T9 * s, BOXH * s, fill=C_BLUE, lw=0.1)                     # veidas
        za, zb = sorted((0, zf - zs * T9))
        rect(Z(zb), Yv(TOT_H), (zb - za) * s, T9 * s, fill=C_BLUE, lw=0.1)                # viršaus atlankas
        rect(Z(zb), Yv(Y_BOX0 + T9), (zb - za) * s, T9 * s, fill=C_BLUE, lw=0.1)          # dugno atlankas
    rect(Z(B4W / 2), Yv(Y_B4T), B4W * s, B4 * s, fill=C_STEEL, lw=0.1)                    # 4
    rect(Z(B4W / 2 - B4T), Yv(Y_B4T - B4T), (B4W - 2 * B4T) * s, (B4 - 2 * B4T) * s, fill=white, lw=0.1)
    rect(Z(R5 / 2), Yv(Y_R5T), R5 * s, R5 * s, fill=C_STEEL, lw=0.1)                      # 5
    rect(Z(R5 / 2 - R5T), Yv(Y_R5T - R5T), (R5 - 2 * R5T) * s, (R5 - 2 * R5T) * s, fill=white, lw=0.1)
    rect(Z(R5 / 2), Yv(Y_B4B), R5 * s, V5_L * s, lw=0.1, dash=(2, 1.5))                  # statmuo už pjūvio
    rect(Z(12), Yv(Y_R5T + 8), 24 * s, 8 * s, fill=C_LED, lw=0.1)                         # 12
    bb = G["bb"]["glow"]
    yg0, yg1 = TOT_H - bb[3] - PLEXI_OV, TOT_H - bb[1] + PLEXI_OV
    zp = BD / 2 - T9
    rect(Z(zp), Yv(yg1), 3 * s, (yg1 - yg0) * s, fill=C_PLEXI, lw=0.1)                    # 10
    rect(Z(PR_D / 2), Yv(Y_PR0 + PR_H), PR_D * s, PR_H * s, fill=C_BLACK, lw=0.1)         # 8
    rect(Z(PR_D / 2 - PR_T), Yv(Y_PR0 + PR_H - PR_T), (PR_D - 2 * PR_T) * s, (PR_H - 2 * PR_T) * s, fill=white, lw=0.1)
    rect(Z(1.5), Yv(Y_BOX0), 3 * s, PR_GAP * s, lw=0.1, dash=(2, 1.5))                    # 8A už pjūvio
    K.set_view(False)
    for zz, yy in ((B4 / 4, TOT_H), (B4 / 4, Y_BOX0)):
        K.centerline(Z(zz), Yv(yy) - 6, Z(zz), Yv(yy) + 10)
    # ŠVIESA: LED -> veidas (rodyklė)
    yt = Yv(TOT_H)
    HM(Z(BD / 2), Z(-BD / 2), yt - D2, f"{BD}", yt, yt)
    hchain(yt - D1, [Z(BD / 2), Z(0), Z(-BD / 2)], [yt] * 3, [f"{BD // 2}", f"{BD // 2}"], size=K.F_DIM_FRAME, bg=True)
    xr = Z(-BD / 2) + D1
    vchain(xr, [Yv(TOT_H), Yv(Y_BOX0), Yv(Y_PR0 + PR_H), Yv(Y_PR0)], [Z(-BD / 2), Z(-BD / 2), Z(-PR_D / 2), Z(-PR_D / 2)],
           [f"{BOXH}", f"{PR_GAP}", f"{PR_H}"], size=K.F_DIM_FRAME, bg=True)
    xl = Z(BD / 2) - D1
    vchain(xl, [Yv(TOT_H), Yv(Y_B4B), Yv(Y_R5T), Yv(Y_BOX0)], [Z(B4W / 2), Z(B4W / 2), Z(R5 / 2), Z(BD / 2)],
           [f"{B4 + T9 + 1}", f"{V5_L:g}", f"{R5 + T9 + 1}"], size=K.F_DIM_FRAME, bg=True)
    for (x, y, n) in ((Z(BD / 2), Yv(TOT_H - 150), 9), (Z(-B4W / 2), Yv(Y_B4T - 40), 4), (Z(-R5 / 2), Yv(Y_R5T - 20), 5),
                      (Z(zp - 1.5), Yv((yg0 + yg1) / 2), 10), (Z(-12), Yv(Y_R5T + 4), 12),
                      (Z(-PR_D / 2), Yv(Y_PR0 + PR_H / 2), 8)):
        K.balloon_auto(x, y, n)
    K.balloon_auto(Z(4.6), Yv(Y_BOX0), f"Ø3.2 / {SCREW_P}", kind="tag", size=8, prefer=[210])
    detail_mark(Z(0), Yv(Y_BOX0 - PR_GAP / 2), 16, "B")
    view_title(X0, K.IY0 + 22, "SECTION A-A", "1:5")


def section_cc(X0, YG, s):
    """SECTION C-C per pagrindą (z = 0), žiūrint iš priekio; kabelio kelias - raudonai"""
    X = lambda x: X0 + x * s                                    # x nuo plokštės centro
    Yg = lambda y: YG - y * s
    lc = 0
    h_show = 330
    K.set_view(True)
    for a, b in ((-PL_W / 2, -SQ / 2), (SQ / 2, PL_W / 2)):
        rect(X(a), Yg(PL_T), (b - a) * s, PL_T * s, fill=HATCH_STEEL, lw=0.1)              # 2 pjūvis, anga □184
    hx = CABLE_HX
    rect(X(hx - CABLE_D / 2), Yg(PL_T), CABLE_D * s, PL_T * s, fill=white, stroke=None)     # Ø40 kabeliui
    for xx in (-PL_HX, PL_HX):
        rect(X(xx - PL_HD / 2), Yg(PL_T), PL_HD * s, PL_T * s, lw=0.1, dash=(1.5, 1), fill=None)
    poly([(X(-G3_L / 2), Yg(PL_T)), (X(G3_L / 2), Yg(PL_T)), (X(G3_L / 2), Yg(PL_T + G3_H - G3_C)),
          (X(G3_TOP / 2), Yg(PL_T + G3_H)), (X(-G3_TOP / 2), Yg(PL_T + G3_H)),
          (X(-G3_L / 2), Yg(PL_T + G3_H - G3_C))], fill=C_STEEL, lw=0.1)                  # 3 už pjūvio
    for xx in (-LEG / 2, LEG / 2 - 5):
        rect(X(xx), Yg(h_show), 5 * s, h_show * s, fill=HATCH_STEEL, lw=0.1)              # 1 per plokštę iki pagrindo
    line(X(-LEG / 2) - 5, Yg(h_show), X(LEG / 2) + 5, Yg(h_show), 0.1, dash=([4, 1, 1, 1], 0))
    ct = 1.5
    for xx in (-BASE_W / 2, BASE_W / 2 - ct):
        rect(X(xx), Yg(BASE_H), ct * s, BASE_H * s, fill=C_GREY, lw=0.1)                  # 7 šonai
    for a, b in ((-BASE_W / 2, -LEG / 2 - 3), (LEG / 2 + 3, BASE_W / 2)):
        rect(X(a), Yg(BASE_H), (b - a) * s, ct * s, fill=C_GREY, lw=0.1)                  # 7 viršus, išpjova kojai
    rect(X(JB[0]), Yg(PL_T + JB[2]), (JB[1] - JB[0]) * s, JB[2] * s, fill=C_JB, lw=0.1)   # 11
    K.set_view(False)
    yc = PL_T + 70                                              # kabelis: koja -> skylė sienelėje -> 11 -> Ø plokštėje
    K.cable_line([(X(40), Yg(h_show - 20)), (X(40), Yg(yc)), (X(JB[0]), Yg(yc))])
    K.cable_line([(X(JB[1]), Yg(PL_T + 40)), (X(hx), Yg(PL_T + 40)), (X(hx), Yg(0) + 10)])
    circle(X(LEG / 2 - 2.5), Yg(yc), 2, fill=white, lw=0.3)
    yb = Yg(0)
    HM(X(-BASE_W / 2), X(BASE_W / 2), yb + D2, f"{BASE_W} (7)", yb, yb)
    hchain(yb + D1, [X(-PL_W / 2), X(-G3_L / 2), X(0), X(hx), X(PL_W / 2)], [Yg(0), Yg(PL_T)] + [Yg(0)] * 3,
           [f"{(PL_W - G3_L) / 2:g}", f"{G3_L / 2:g}", f"{CABLE_HX:g}", f"{PL_W / 2 - CABLE_HX:g}"], size=K.F_DIM_FRAME, bg=True)
    xr = X(BASE_W / 2) + D1
    vchain(xr, [Yg(BASE_H), Yg(PL_T + G3_H), Yg(PL_T), Yg(0)], [X(BASE_W / 2), X(G3_TOP / 2), X(PL_W / 2), X(PL_W / 2)],
           [f"{BASE_H - PL_T - G3_H:g}", f"{G3_H}", f"{PL_T}"], size=K.F_DIM_FRAME, bg=True)
    for (x, y, n) in ((X(-LEG / 2 + 2), Yg(260), 1), (X(-PL_W * 0.38), Yg(PL_T / 2), 2), (X(-G3_L * 0.3), Yg(PL_T + 50), 3),
                      (X(BASE_W / 2 - 1), Yg(BASE_H * 0.6), 7), (X((JB[0] + JB[1]) / 2), Yg(PL_T + JB[2] * 0.7), 11)):
        K.balloon_auto(x, y, n)
    K.balloon_auto(X(hx), Yg(0) + 6, f"power in Ø{CABLE_D}", kind="tag", size=8)
    view_title(X(0), Yg(h_show) - 34, "SECTION C-C - BASE", "1:10   cable - red")


def materials_key(x, y):
    rows = [(C_GREY, "Steel 1 / Alu 7 - NCS S 2500-N"), (C_STEEL, "Steel 2-6 (inside), finish:"),
            (C_BLUE, "Alu 2 mm 9 - NCS S 4055-R70B"), (C_BLACK, "Alu 8 - RAL 9005"), (C_HANG, "Alu 3 mm 8A"),
            (C_PLEXI, "Plexi 3 mm white 10"), (C_LED, "LED 12"), (C_JB, "Junction box 11"),
            (HATCH_STEEL, "Steel - in section")]
    T(x, y, "MATERIALS KEY", 9, font="FB")
    for i, (col, txt) in enumerate(rows):
        yy = y + 8 + i * 13
        rect(x, yy, 16, 9, fill=col, lw=0.3)
        T(x + 22, yy + 7, txt, 8)


STEPS = [
    f"1  Base: leg 1 through plate 2 (opening □{SQ}), bottom flush, welded all round; supports 3 (2 x {G3_L}x{G3_H}) welded front + back.",
    f"2  Top frame 4 ({B4_L}) welded on top of leg 1; frame 5: rail {R5_L} welded to leg, 3 verticals {V5_L:g} welded rail - beam.",
    f"3  Support 6 ({S6:.0f} top / {S6_B:.0f} bottom x {V5_L:g}) welded to leg 1, beam 4 and rail 5. Steel 1-6 finish: ___ .",
    "4  LED 12 on top of rail 5 (under glowing graphics); cable inside leg 1 -> hole in leg* -> junction box 11 on plate 2.",
    f"5  Plexi 10 (3 pcs., 2535 x 325 overall) on inside of front 9: holes plexi Ø8, tray Ø6 x 71 - bolts / studs: ___ .",
    "6  Trays 9 (flat 3196 x 716, returns 98, corners cut 98 x 100): leg 1 in notch 186 x 100 of bottom return.",
    f"7  Trays fixed through returns into 4 / 5 / end vertical: Ø3.2, pitch {SCREW_P}, 4.6 from return edge (rivets / screws: ___).",
    f"8  Hangers 8A at {HANG_F[0]:g} / {HANG_F[1]:g} from leg outer face: upper L bolted M6 to rail 5, lower L to profile 8, slot = height adj.",
    "9  Bottom cover 7: 2 halves around leg, joined at ends with 2 strips 20 x 200 (4 x Ø3.2).",
    f"10 On site: plate 2 on 6 anchors Ø{PL_HD}; power in through Ø{CABLE_D} into junction box 11 (SECTION C-C).",
    "Source: production file (1:1, METALAS + flats). *  = ALT proposal, not in production file - confirm (Q).",
]
QUEST = [
    f"Q1  Top frame 4: production file {B4} high, client list □80x80x3 - which profile ({B4}x{B4W}x{B4T}?)",
    "Q2  Hangers 8A: 8 pcs. (4 sets) in flats, frame marks only 2 positions - 2 or 4 hangers?",
    "Q3  Bottom cover 7: bend lines not in flat 1002 x 325 - fold geometry / height 150?",
    "Q4  Plexi 10 fixing: Ø6 in tray x 71 / Ø8 in plexi x 61 - bolts or studs? Ø4 x 10 in plexi - purpose?",
    "Q5  Steel finish 1-6: hot-dip galvanized / powder coat? Trays 9 fixing - rivets or screws Ø3.2?",
    "Q6  LED 12: type, qty, voltage; cable hole in leg, junction box 11 type and position*.",
    f"Q7  Cable hole Ø{CABLE_D}: production file - right of leg (top view), client sheet - left. Which side?",
    "Q8  Backside graphics (client 3D: none)? Anchors type / length?",
]


def sheet2(G, out):
    K.set_band(15)
    K.init(out + ".tmp", "ALT8877 OKQ8 height restriction - structure")
    K.frame()
    BY0 = K.BAND_Y; BH = K.IY1 - BY0
    exploded(G, (K.IX0 + 14, K.IY0 + 60, 560, K.VIEW_BOT - K.IY0 - 70))
    s50 = MM / 50
    frame_view(G, K.IX0 + 650, K.IY0 + 112 + TOT_H * s50, s50)
    s10 = MM / 10
    section_aa(G, K.IX1 - 92, K.IY0 + 96, MM / 5)
    section_cc(K.IX0 + 650 + 120, K.VIEW_BOT - 52, s10)
    materials_key(K.IX0 + 360, K.VIEW_BOT - 120)
    W_TB, W_Q = 272, 300
    X_TB = K.IX1 - W_TB; X_Q = X_TB - W_Q; W_S = X_Q - K.IX0
    K.header(K.IX0, BY0, W_S, "CONSTRUCTION / ASSEMBLY")
    rect(K.IX0, BY0 + 12, W_S, BH - 12, lw=0.6)
    lh = (BH - 18) / len(STEPS)
    for i, s_ in enumerate(STEPS):
        T(K.IX0 + 5, BY0 + 12 + lh * (i + 0.5) + 3.5, s_, 8, fit=W_S - 10, fit_min=7.5)
    K.header(X_Q, BY0, W_Q, "QUESTIONS TO CLIENT")
    rect(X_Q, BY0 + 12, W_Q, BH - 12, lw=0.6)
    lq = (BH - 18) / len(QUEST)
    for i, q in enumerate(QUEST):
        T(X_Q + 5, BY0 + 12 + lq * (i + 0.5) + 3.5, q, 8, color=RED, auto_red=False, fit=W_Q - 10, fit_min=7)
    K.title_block(X_TB, W_TB, dict(TB, sheet="2 / 2", title=TB["title"] + " - STRUCTURE"), "1:50 / 1:10 / 1:5")
    K.save(out)


def main(out):
    K.F_DIM_FRAME = K.F_DIM_MAIN                                # v145: visi matmenys vienodo dydžio
    G = client_graphics()
    parts = []
    for i, fn in enumerate((sheet1, sheet2)):
        pp = f"{out}.{i + 1}.pdf"
        K.auto_begin("collect"); K.AUTO["region"] = None
        fn(G, pp)
        pl = K.auto_place(pp)
        K.auto_begin("draw", pl); K.AUTO["region"] = None
        fn(G, pp)
        K.auto_begin(None)
        parts.append(pp)
    d = fitz.open()
    for p in parts:
        d.insert_pdf(fitz.open(p))
    d.save(out, garbage=3, deflate=True); d.close()
    K.pdf_fix_fonts(out)
    for p in parts:
        for q in (p, p + ".tmp"):
            os.path.exists(q) and os.remove(q)
    print("OK", out, f"svoris ≈ {weight():.0f} kg", "netelpa:", K.OVERFLOW)


if __name__ == "__main__":
    main(sys.argv[1])
