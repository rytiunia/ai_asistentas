"""Bendras lapų karkasas (lapas_core) - Clas Ohlson Horten 3."""
import sys, os, tempfile, math
SKILL = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))  # reklama/ (skill'o šaknis)
sys.path.insert(0, os.path.join(SKILL, "scripts"))
import lapas_core as K
from lapas_core import T, line, rect, poly, circle, hdim, hchain, vchain, leader, balloon, view_title, MM
from reportlab.lib.colors import HexColor, white, black

PROJECT = "Order 226045"
CLIENT = "BrandFactory"
DATE = "2026-10-15"
PLATE_HEX = "#94DCF4"            # kliento faile (NCS S 0540-B semi matte)
K.FOIL["NCS S 0540-B"] = PLATE_HEX
RED = HexColor("#E2001A")
NCS = HexColor(PLATE_HEX)
BLK = HexColor("#0E0E10")


def begin(n_rows):
    K.OVERFLOW.clear()
    K.set_band(n_rows)
    tmp = tempfile.mktemp(suffix=".pdf")
    K.init(tmp, PROJECT)
    K.frame()


def band(first_title, first_fn, bom, md, title, sheet, scales, w_first=214, md_lab=62, qty=1):
    BY0 = K.BAND_Y; BH = K.IY1 - BY0
    W_MD, W_TB = 200, 272
    X0 = K.IX0; X_TB = K.IX1 - W_TB; X_MD = X_TB - W_MD
    X_BOM = X0 + w_first; W_BOM = X_MD - X_BOM
    K.header(X0, BY0, w_first, first_title)
    rect(X0, BY0 + 12, w_first, BH - 12, lw=0.6)
    first_fn(X0, BY0 + 12, w_first, BH - 12)
    K.bom_table(X_BOM, BY0, W_BOM, BH, bom, title="BILL OF MATERIALS  (per 1 pcs.)")
    K.main_data(X_MD, BY0, W_MD, BH, md, lab_w=md_lab)
    sp = {"client": CLIENT, "title": title, "drawing_no": PROJECT, "date": DATE,
          "rev": "A", "order_no": "ALT0000_00.00_RS", "sheet": sheet, "qty": qty}
    K.title_block(X_TB, W_TB, sp, scales)


def warn_box(x, y, w, lines, size=9):
    """raudonas perspėjimas (kaip etalone 'Plate from 2 parts!')"""
    h = 8 + len(lines) * (size + 3.5)
    rect(x, y, w, h, stroke=RED, lw=0.8)
    for i, s in enumerate(lines):
        T(x + w / 2, y + 6 + (i + 0.8) * (size + 3.5) - 1, s, size, font="FB" if i == 0 else "F", color=RED, align="c", auto_red=False)
    return h


def draw_sub(sub, tf, fill=None, stroke=black, lw=0.1):
    K.draw_shape(sub, tf, fill=fill, stroke=stroke, lw=lw)


P8 = {"W": 70, "ov": 2, "tw": 7.5, "tb": 7}
# ClasOhlson_proporcijos.pdf (Rytis 2026-10-09): plexi 20 = galas 7 + ertmė 13 (A-A), sienelė ~7.5 (kontūrų atstumas, S1/S3);
# Al priekio išsikišimas (ov) faile nenurodytas - lape tuščia vieta, brėžinyje 2 mm tik proporcijai
PLEXI_C = HexColor("#FFFFFF")


def draw_p8(xf, ytop, sc, W=P8["W"], ov=P8["ov"], tw=P8["tw"], tb=P8["tb"], ycut=None, hmax=None):
    """P8 special pjūvis per raidės liniją: xf - plokštės priekio x (pt), gylis į dešinę; ytop - raidės krašto y (pt).
    Y(h) - jei duota ycut(h_mm)->pt (lūžęs vaizdas). Al 3 priekis platesnis už plexi (ov), plexi 20 išfrezuotas:
    galas tb (7) prie plokštės, sienelės tw, ertmė atvira į priekį, LED ant priekio per vidurį, spaceris į plexi galą."""
    Yh = ycut or (lambda h: ytop + h * sc)
    yc = Yh(W / 2)
    K.set_view(True)
    rect(xf, yc - 8 * sc, 20 * sc, 16 * sc, fill=HexColor("#C8C8C8"), lw=0.3)                     # spaceris
    hm = W if hmax is None else min(W, hmax)
    parts = [(xf + 20 * sc, Yh(ov), tb * sc, Yh(min(W - ov, hm)) - Yh(ov)),                       # plexi galas
             (xf + 20 * sc, Yh(ov), 20 * sc, tw * sc)]                                             # sienelė viršuje
    if W - ov <= hm:
        parts.append((xf + 20 * sc, Yh(W - ov - tw), 20 * sc, tw * sc))                            # sienelė apačioje
    for (x_, y_, w_, h_) in parts:
        if h_ <= 0:
            continue
        rect(x_, y_, w_, h_, fill=PLEXI_C, lw=0.35); K.hatch(x_, y_, w_, h_, step=2)
        rect(x_, y_, w_, h_, lw=0.35)
    rect(xf + 40 * sc, Yh(0), 3 * sc, Yh(hm) - Yh(0), fill=black, lw=0.35)                       # Al 3 priekis
    rect(xf + 36.5 * sc, yc - 5 * sc, 3.5 * sc, 10 * sc, fill=HexColor("#FFC20E"), lw=0.25)        # LED
    rect(xf - 3 * sc, yc - 1.0, (3 + 20 + tb + 5) * sc, 2.0, fill=HexColor("#6E6E6E"), lw=0.25)  # varžtas iš vidaus
    rect(xf - 3 * sc - 3, yc - 3, 3, 6, fill=HexColor("#3A3A3A"), lw=0.3)
    K.set_view(False)                                     # v285: varžtas - hairline geometrija
    K.centerline(xf - 3 * sc - 6, yc, xf + 46 * sc, yc)
    return yc


def zig(x0, x1, y):
    poly([(x0, y), (x0 + (x1 - x0) * 0.4, y), (x0 + (x1 - x0) * 0.47, y - 3), (x0 + (x1 - x0) * 0.53, y + 3),
          (x0 + (x1 - x0) * 0.6, y), (x1, y)], close=False, lw=0.3)


def detail_a(ax0, ay0, LY, PD=40, t=2.0):
    """DETAIL A - SECTION 1:2, lūžęs vaizdas: viršutinė briauna (0..40) | lūžis | raidė (LY-8 .. LY+47).
    ax0 - sienos plokštuma (nebraižoma), ay0 - plokštės viršus. Grąžina apatinį y."""
    sc = MM / 2
    TOP, GAP = 40, 6
    def Yd(h):
        return ay0 + sc * (h if h <= TOP else TOP + GAP + (h - (LY - 8)))
    X = lambda d: ax0 + d * sc
    END = LY + 47
    K.set_view(True)
    rect(X(PD - t), Yd(0), t * sc, TOP * sc, fill=black, lw=0.35)                                # priekis viršuje
    rect(X(PD - t), Yd(LY - 8), t * sc, Yd(END) - Yd(LY - 8), fill=black, lw=0.35)              # priekis ties raide
    rect(X(0), Yd(0), (PD - t) * sc, t * sc, fill=black, lw=0.35)                                # užlenkta briauna
    poly([(X(0), Yd(t + 0.4)), (X(30), Yd(t + 0.4)), (X(30), Yd(t + 2.4)), (X(2), Yd(t + 2.4)), (X(2), Yd(t + 30.4)),
          (X(0), Yd(t + 30.4))], fill=HexColor("#B4B4B4"), lw=0.35)                              # L 30x30x2
    bx = X(7)                                                                                     # Ø3.2, 7 nuo krašto
    rect(bx - 4.5, Yd(0) - 3.2, 9, 3.2, fill=HexColor("#3A3A3A"), lw=0.3)
    rect(bx - 1.3, Yd(0), 2.6, (t + 2.4 + 8) * sc, fill=HexColor("#6E6E6E"), lw=0.25)
    wy = Yd(t + 20)
    rect(X(-16), wy - 2, (16 + 2 + 4) * sc, 4, fill=HexColor("#6E6E6E"), lw=0.25)
    rect(X(2), wy - 5, 3.5, 10, fill=HexColor("#3A3A3A"), lw=0.3)
    zig(X(PD - 8), X(PD + 8), Yd(TOP) + 0.5)
    zig(X(PD - 8), X(PD + 8), Yd(LY - 8) - 0.5)
    K.set_view(False)                                     # v285: detalės geometrija - hairline (ISO, patikra)
    K.centerline(bx, Yd(0) - 8, bx, Yd(t + 14))
    K.centerline(X(-20), wy, X(10), wy)
    yc = draw_p8(X(PD), Yd(LY), sc, ycut=lambda h: Yd(LY + h), hmax=END - LY)
    K.set_view(True); zig(X(PD - 8), X(PD + 50), Yd(END)); K.set_view(False)
    # matmenys - viena aiški grandinė viršuje, kiti - šone
    hchain(Yd(0) - 26, [X(0), X(PD), X(PD + 20), X(PD + 27), X(PD + 40), X(PD + 43)],
           [Yd(0), Yd(0), Yd(LY), Yd(LY), Yd(LY), Yd(LY)], ["40", "20", "7", "13", "3"], size=8)
    hdim(X(0), X(7), Yd(0) - 44, "7", Yd(0), Yd(0) - 9, size=8, small_side="l")   # v285: iškeltinė - ašinės tęsinys
    T(X(7) + 8, Yd(0) - 41.5, "Ø3.2 hole", 8)
    vchain(X(PD + 43) + 26, [Yd(0), Yd(LY)], [X(PD), X(PD + 43)], [f"{LY}"], size=8)
    vchain(X(PD + 43) + 12, [Yd(LY), Yd(LY + P8["ov"]), Yd(LY + P8["ov"] + P8["tw"])], [X(PD + 43), X(PD + 40), X(PD + 40)],
           ["?", "7.5"], size=8)
    R = X(PD + 43) + 46
    leader(X(PD + 41.5), Yd(LY + 40), R, Yd(LY + 44), 1)
    leader(X(PD + 32), Yd(LY + P8["ov"] + 3), R, Yd(LY + 12), 2)
    leader(X(PD + 38), yc + 2, R, yc - 2, 3)
    leader(X(PD + 10), yc - 6 * sc, X(PD + 6), Yd(LY - 8) + 4, 4)
    L_ = X(-16) - 22
    leader(X(PD - 1), Yd(LY - 4), L_, Yd(LY - 4) + 2, 5)
    leader(X(1), Yd(t + 26), L_, Yd(t + 34), 6)
    leader(X(-12), wy, L_, Yd(t + 14), 7)
    leader(X(PD) - 4, yc + 1, L_, yc + 14, 8)
    leader(bx, Yd(0) - 3, L_, Yd(0) - 14, 9)
    return Yd(END)


def p8_band(x, y, w, h):
    """juostos blokas: P8 special pjūvis A-A per raidės liniją, 1:2 (pagal ClasOhlson_proporcijos A-A)"""
    sP = MM / 2
    W_, ov, tw, tb = P8["W"], P8["ov"], P8["tw"], P8["tb"]
    xf, yt = x + 52, y + 34
    Xp = lambda d: xf + d * sP
    K.set_view(True)
    rect(Xp(-2), yt - 6, 2 * sP, W_ * sP + 12, fill=black, lw=0.35)                         # folded plokštė
    K.set_view(False)
    yc = draw_p8(Xp(0), yt, sP)
    hchain(yt - 14, [Xp(0), Xp(20), Xp(27), Xp(40), Xp(43)], [yc - 8 * sP, yt + ov * sP, yt + ov * sP, yt, yt],
           ["20", "7", "13", "3"], size=8)
    vchain(Xp(43) + 12, [yt, yt + ov * sP, yt + (ov + tw) * sP], [Xp(43), Xp(40), Xp(40)], ["?", "7.5"], size=8)
    R = Xp(43) + 44
    leader(Xp(41.5), yt + W_ * sP * 0.9, R, yt + W_ * sP * 0.98, 1)
    leader(Xp(33), yt + (W_ - ov - tw / 2) * sP, R, yt + W_ * sP * 0.74, 2)
    leader(Xp(38), yc + 3, R, yc + 2, 3)
    leader(Xp(12), yc - 6 * sP, R, yt + 22, 4)
    leader(Xp(-1), yt + W_ * sP * 0.9, Xp(-2) - 16, yt + W_ * sP * 0.98, 5)
    leader(Xp(-3) - 3, yc, Xp(-2) - 16, yt + 14, 8)
    T(Xp(23.5), yc + 14, "Ø4", 8, align="c")
    T(x + w / 2, y + h - 16, "plexi 20: back 7 + cavity 13, walls 7.5; Al 3 face", 8, color=K.GREY, align="c", auto_red=False)
    T(x + w / 2, y + h - 5, "larger (overhang ?); LED on face; Ø4 holes = spacers", 8, color=K.GREY, align="c", auto_red=False)
