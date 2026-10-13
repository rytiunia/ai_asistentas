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
HANG = (279, 1182)                      # pakabų vieta nuo profilio kairės - matuota kliento brėžinyje (be matmens!)
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
    # kliento lape - kryželiu pažymėta skylė kairėje per vidurį (Ø nenurodytas)
    hx2 = 177
    circle(X(hx2), Yp(cy), PL_HD / 2 * s, fill=white, lw=0.1)
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
    K.balloon_auto(X(hx2) - PL_HD / 2 * s * 0.7, Yp(cy) + PL_HD / 2 * s * 0.7, "Ø___", kind="tag", size=8)
    K.balloon_auto(X(cx - LEG / 2), Yp(cy - LEG / 2 + 20), 1)
    K.balloon_auto(X(PL_W * 0.85), Yp(PL_D * 0.15), 2)
    view_title(X(PL_W / 2), Y0 - D2 - 30, "MOUNTING PLATE (2) - TOP VIEW", f"1:10   t = {PL_T} mm")


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


def detail_b(X0, BY0, W0, BH):
    """DETAIL B - pakaba (8A) 1:5, pjūvis skersai profilio"""
    K.header(X0, BY0, W0, "DETAIL B - HANGING  1:5")
    rect(X0, BY0 + 12, W0, BH - 12, lw=0.6)
    K.AUTO["region"] = (X0 + 3, BY0 + 15, X0 + W0 - 3, BY0 + BH - 3)
    s = MM / 5
    cx = X0 + W0 * 0.42
    yb = BY0 + BH - 30                                          # profilio apačia
    Z = lambda z: cx + z * s
    Yv = lambda y: yb - y * s                                   # y nuo profilio apačios
    K.set_view(True)
    t9 = 2
    ytop = PR_H + PR_GAP                                        # dėžės apačia
    # dėžės dugnas (9) su lūžiais
    rect(Z(-BD / 2), Yv(ytop + t9), BD * s, t9 * s, fill=C_BLUE, lw=0.1)
    rect(Z(-BD / 2), Yv(ytop + 40), t9 * s, (40 - t9) * s, fill=C_BLUE, lw=0.1)
    rect(Z(BD / 2 - t9), Yv(ytop + 40), t9 * s, (40 - t9) * s, fill=C_BLUE, lw=0.1)
    line(Z(-BD / 2) - 4, Yv(ytop + 40), Z(BD / 2) + 4, Yv(ytop + 40), 0.1, dash=([4, 1, 1, 1], 0))
    # profilis 120x50x2
    rect(Z(-PR_D / 2), Yv(PR_H), PR_D * s, PR_H * s, fill=C_BLACK, lw=0.1)
    rect(Z(-PR_D / 2 + PR_T), Yv(PR_H - PR_T), (PR_D - 2 * PR_T) * s, (PR_H - 2 * PR_T) * s, fill=white, lw=0.1)
    # pakaba 3 mm: apatinis atlankas ant profilio, statmuo, viršutinis atlankas virš dugno
    th = 3
    GREYH = HexColor("#B4B4B4")
    rect(Z(-PR_D / 2 + 4), Yv(PR_H + th), (PR_D / 2 - 4) * s, th * s, fill=GREYH, lw=0.1)
    rect(Z(-th / 2), Yv(ytop + t9 + th), th * s, (ytop + t9 + th - PR_H) * s, fill=GREYH, lw=0.1)
    rect(Z(-th / 2), Yv(ytop + t9 + th), 30 * s, th * s, fill=GREYH, lw=0.1)
    # varžtai (schema)
    for zz, y0, y1 in ((-PR_D / 4, PR_H - PR_T - 4, PR_H + th + 2), (15, ytop - 4, ytop + t9 + th + 2)):
        rect(Z(zz) - 1.5 * s, Yv(y1), 3 * s, (y1 - y0) * s, fill=HexColor("#3A3A3A"), lw=0.1)
    K.set_view(False)
    for zz in (-PR_D / 4, 15):
        K.centerline(Z(zz), Yv(ytop + 14), Z(zz), Yv(PR_H - 12))
    hchain(Yv(0) + 12, [Z(-PR_D / 2), Z(PR_D / 2)], [Yv(0)] * 2, [f"{PR_D}"], size=K.F_DIM_FRAME, bg=True)
    vchain(Z(PR_D / 2) + 18, [Yv(ytop), Yv(PR_H), Yv(0)], [Z(-th / 2) + th * s, Z(PR_D / 2), Z(PR_D / 2)],
           [f"{PR_GAP}", f"{PR_H}"], size=K.F_DIM_FRAME, bg=True)
    K.balloon_auto(Z(-PR_D / 2), Yv(PR_H * 0.4), 8, region=K.AUTO["region"])
    K.balloon_auto(Z(-th / 2), Yv(PR_H + PR_GAP * 0.5), "8A", region=K.AUTO["region"])
    K.balloon_auto(Z(-BD / 2 + 30), Yv(ytop + t9 / 2), 9, region=K.AUTO["region"])
    T(X0 + 4, BY0 + BH - 6, "hanger 8A: 3 mm Alu, 2 pcs.; screws / width:", 8, color=K.GREY)
    K.AUTO["region"] = None


# ---------------------------------------------------------------- BOM / MAIN DATA
def bom():
    return [
        [1, "Leg □180x180x5 (welded to 4)", "Steel", "NCS S 2500-N", "1 pc., L:"],
        [2, f"Mounting plate {PL_W}x{PL_D}x{PL_T}, 6 x Ø{PL_HD}", "Steel", "", "1 pc."],
        [3, "Supports 5 mm (leg - plate)", "Steel", "", "pcs.:"],
        [4, "Top frame □80x80x3 (welded to 1)", "Steel", "", "L:"],
        [5, "Frame □40x40x2", "Steel", "", "L:"],
        [6, "Support 5 mm", "Steel", "", "pcs.:"],
        [7, f"Bottom cover {BASE_W}x{BASE_D}x{BASE_H}, 2 halves", "Alu 1.5 mm", "NCS S 2500-N", "2 pcs."],
        [8, f"Height profile {PR_H}x{PR_D}x{PR_T}", "Alu", "RAL 9005", f"1 pc., {PR_L} mm"],
        ["8A", "Hanger (DETAIL B)", "Alu 3 mm", "", "2 pcs."],
        [9, f"Front / backside {BW}x{BOXH}x{BD}", "Alu 2 mm", "NCS S 4055-R70B", "2 pcs."],
        [10, "Glowing graphics: arrows + Biltvätt", "Plexiglass 3 mm white", "-", "1:1 file"],
        [11, "Junction box", "", "-", "1 pc."],
        [12, "LED's", "", "", "pcs.:"],
        [13, "Decals: car + showers, FRI HÖJD 2,70m.", "Vinyl foil, cast", "ORACAL 551 101", "1 set"],
    ]


def weight():
    st, al = 7.85e-6, 2.7e-6
    leg = (LEG ** 2 - (LEG - 10) ** 2) * (TOT_H - PL_T) * st
    plate = PL_W * PL_D * PL_T * st
    top = (80 ** 2 - 74 ** 2) * BW * st
    faces = 2 * BW * BOXH * 2 * al
    prof = (PR_H * PR_D - (PR_H - 4) * (PR_D - 4)) * PR_L * al
    cover = (BASE_W * BASE_D + 2 * (BASE_W + BASE_D) * BASE_H) * 1.5 * al
    return leg + plate + top + faces + prof + cover


def main_data():
    return [["Product", "height restriction, cantilever, 1 leg"],
            ["Overall", f"{BW} x {TOT_H} x {BASE_D} mm"],
            ["Sign box", f"{BW} x {BOXH} x {BD} mm"],
            ["Clear height", f"{CLEAR} mm (FRI HÖJD 2,70m.)"],
            ["Base", f"plate {PL_W}x{PL_D}x{PL_T}, cover {BASE_W}x{BASE_D}x{BASE_H}"],
            ["Anchors", f"6 x Ø{PL_HD}:"],
            ["Glowing", "arrows + Biltvätt (10 + 12)"],
            ["Stickers", "car + showers, FRI HÖJD (13)"],
            ["Backside", "graphics:"],
            ["Welded", "1 + 4 (leg - top frame)"],
            ["Power", "voltage / cable:"],
            ["Qty", "1 pcs."],
            ["Weight (calc.)", f"≈ {weight():.0f} kg / pcs, excl. 3, 5, 6, LED"]]


# ---------------------------------------------------------------- lapas
def sheet(G, out):
    md, bm = main_data(), bom()
    K.set_band(max(len(md), len(bm) + 1))
    K.init(out + ".tmp", "ALT8877 OKQ8 height restriction")
    K.frame()
    s25 = MM / 25
    YG = K.VIEW_BOT - 62                                        # žemė (vietos apatiniams matmenims)
    X0 = K.IX0 + 106
    front_view(G, X0, YG, s25)
    xs = X0 + BW * s25 + D1 + 40 + 50 + BASE_D / 2 * s25
    side_view(xs, YG, s25)
    s10 = MM / 10
    px0 = K.IX1 - 72 - PL_W * s10
    plate_view(px0, K.IY0 + 108, s10)
    x3 = xs + BASE_D / 2 * s25 + 60
    view3d(G, (x3, K.IY0 + 300, K.IX1 - 10 - x3, YG - (K.IY0 + 300) + 30))
    BY0 = K.BAND_Y; BH = K.IY1 - BY0
    W_D, W_MD, W_TB = 214, 230, 272
    X_D = K.IX0; X_TB = K.IX1 - W_TB; X_MD = X_TB - W_MD; X_BOM = X_D + W_D; W_BOM = X_MD - X_BOM
    detail_b(X_D, BY0, W_D, BH)
    K.bom_table(X_BOM, BY0, W_BOM, BH, bm,
                cols=(("POS", 20), ("PART", 0.37), ("MATERIAL", 0.22), ("FINISH", 0.19), ("QTY", None)))
    K.main_data(X_MD, BY0, W_MD, BH, md, lab_w=64)
    spec = {"client": "Skyltkoncept Sweden AB (OKQ8)", "title": "OKQ8 HEIGHT RESTRICTION - BILTVÄTT",
            "order_no": "ALT8877_10.13_RS", "drawing_no": "okq8 height restriction", "sheet": "1 / 1", "rev": "A",
            "date": "2026-10-13"}
    K.title_block(X_TB, W_TB, spec, "1:25 / 1:10 / 1:5")
    K.save(out)


def main(out):
    K.F_DIM_FRAME = K.F_DIM_MAIN                                # v145: visi matmenys vienodo dydžio
    G = client_graphics()
    K.auto_begin("collect"); K.AUTO["region"] = None
    sheet(G, out)
    pl = K.auto_place(out)
    K.auto_begin("draw", pl); K.AUTO["region"] = None
    sheet(G, out)
    K.auto_begin(None)
    if os.path.exists(out + ".tmp"):
        os.remove(out + ".tmp")
    print("OK", out, f"svoris ≈ {weight():.0f} kg", "netelpa:", K.OVERFLOW)


if __name__ == "__main__":
    main(sys.argv[1])
