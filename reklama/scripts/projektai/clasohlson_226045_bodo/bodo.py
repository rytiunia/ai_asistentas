"""Clas Ohlson Bodø - BrandFactory Order 226045 (2026-10-15): LED sign 2 pcs, P8 special (Clas Ohlson standartas) ant
vertikalios folded plokštės 515 x 2380 (mėlyna), logotipas 420 x 824 juodas (backlit). Analogas - Horten 1
(`projektai/clasohlson_horten/sheet3.py`), „same thickness as LED sign you have produced" = Horten: plokštė 40, raidė 3 + 20 ant
spacerių 20. Išklotinė - v173 praktika (flanšai gylis - t). Naudojimas: python3 bodo.py out.pdf"""
import math, os, sys
import pymupdf as fitz
from shapely.geometry import Polygon
from shapely.affinity import scale as sscale, translate as stranslate
from common import *
import data as D

OUT = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "CO-Bodo-5-6-Plate-515x2380_Logo-420x824-2st.pdf")
k1 = 25.4 / 72                                   # kliento failas 1:1
PW, PH, PD, TS = 515, 2380, 40, 2.0
QTY = 2

# ---- raidės / logotipas iš kliento failo
pg = fitz.open(SRC)[0]
LET = []
for d in pg.get_drawings():
    f = d.get("fill")
    if not f or sum(f[:3]) > 0.5:
        continue
    sub = [[(s_[0],) + tuple((q[0] * k1, q[1] * k1) for q in s_[1:]) for s_ in sp] for sp in D._subs(d)]
    polys = [Polygon(D.flat(sp)).buffer(0) for sp in sub if len(D.flat(sp)) > 2]
    g = polys[0]
    for p_ in polys[1:]:
        g = g.symmetric_difference(p_)
    LET.append({"sub": sub, "geom": g, "bb": g.bounds})
D.attach_ref(LET)
LBB = (min(L["bb"][0] for L in LET), min(L["bb"][1] for L in LET), max(L["bb"][2] for L in LET), max(L["bb"][3] for L in LET))
N_SP = sum(len(L["sp"]) for L in LET)
N_SLOT = sum(1 for L in LET for f in L["feats"] if f["type"] == "SLOT")
N_D8 = sum(1 for L in LET for f in L["feats"] if f["type"] == "D8")
A_FACE = sum(L["geom"].area for L in LET) / 1e6
PER = sum(L["geom"].length for L in LET) / 1000
L_LEN = PW - 50
span = PW - 100; n_scr = max(1, round(span / 300)); pitch = span / n_scr
FLT = PD - TS
FLAT = (PW + 2 * FLT, PH + 2 * FLT)              # v173: flanšai = gylis - t

begin(16)
# ---- TAISYKLĖ 33: adaptyvus išdėstymas - masteliai, stulpeliai ir tarpai skaičiuojami iš geometrijos + anotacijų
import layout_engine as LE
from reportlab.pdfbase.pdfmetrics import stringWidth as _sw
A_TOP, A_BOT = 58, 44                                             # viršutiniai matmenys | pavadinimas + mastelis
YT = K.IY0 + A_TOP
SC = LE.pick_scale((PW, PH), (K.IX1 - K.IX0, K.VIEW_BOT - YT - A_BOT))    # FRONT / SIDE / REAR - BENDRAS
s = MM / SC
_side_txt = max(_sw("40 + 20 + 23", "F", 8), _sw("(DETAIL A)", "F", 8))
TR_W = 40 + _sw("12V, 5 m, white", "F", 8)                        # trafo box + laido užrašas
DET_W = 222                                                       # DETAIL A 1:2 su pozicijomis
H_A = (40 + 6 + 55) * MM / 2                                      # DETAIL A (lūžęs) geometrijos aukštis
# zona C (tarp galo ir 3D) - du stulpeliai: [TRAFO BOX viršuje (prie laido) + DETAIL A apačioje] | [LOGO DETAIL per visą aukštį]
LG_W, LG_H = LBB[2] - LBB[0], LBB[3] - LBB[1]
L_TOP, L_BOT = 22, 57                                             # viršutinė grandinė | apatinės grandinės + pavadinimas
_lh = K.VIEW_BOT - (YT - 36)
SCL = LE.pick_scale((LG_W, LG_H), (400, _lh), annot=(12, 52, L_TOP, L_BOT), inter=(),
                    cap_pt=(1e9, 0.6 * PH * s))                    # didžiausias ISO, bet ne didesnė už projekcijas
sl = MM / SCL
LOGO_W = 12 + LG_W * sl + 52
ASP3 = LE.proj_aspect(LE.box_corners(PW, PH, PD + 43), 30, 14)
P3_W = ASP3 * PH * s                                              # 3D - tokio pat aukščio kaip projekcijos
COLS = [58 + PW * s + 29,                                         # FRONT: 2380 grandinė | pozicijos
        (PD + 43) * s + 10 + _side_txt,                           # SIDE + užrašas
        24 + PW * s + 29,                                         # REAR: D11 grandinė | pozicijos
        max(TR_W, DET_W), LOGO_W, max(P3_W, LE.title_w("3D VIEW", "ILLUSTRATIVE - NOT TO SCALE"))]
CX, G_ = LE.distribute(K.IX0, K.IX1, COLS, margin=(0.5, 1.0))   # Rytis: didesnė paraštė DEŠINĖJE nuo krašto
X0 = CX[0] + 58
fx = lambda x: X0 + x * s
fy = lambda y: YT + y * s
YB = fy(PH)

# ================================================================ FRONT VIEW
K.set_view(True)
rect(X0, YT, PW * s, PH * s, fill=NCS, lw=0.5)
tf = lambda x, y: (fx(x), K.Y(fy(y)))
for L in LET:
    draw_sub(L["sub"], tf, fill=BLK, stroke=None)
K.set_view(False)
hdim(X0, fx(PW), YT - 36, f"{PW}", YT, YT, size=12)
xs = [0, round(LBB[0]), round(LBB[2]), PW]
hchain(YT - 16, [fx(v) for v in xs], [YT, fy(LBB[1]), fy(LBB[1]), YT], [f"{b - a}" for a, b in zip(xs, xs[1:])], size=8)
ys = [0, round(LBB[1]), round(LBB[3]), PH]
vchain(X0 - 16, [fy(v) for v in ys], [X0, fx(LBB[0]), fx(LBB[0]), X0], [f"{b - a}" for a, b in zip(ys, ys[1:])], size=8)
vchain(X0 - 46, [YT, YB], [X0, X0], [f"{PH}"], size=12)
leader(fx(PW * 0.7), fy(PH * 0.8), fx(PW) + 22, fy(PH * 0.86), 5)
leader(fx(LET[0]["geom"].representative_point().x), fy(LET[0]["geom"].representative_point().y), fx(PW) + 22, fy(LBB[1]) - 10, 1)
view_title(X0 + PW * s / 2, YB + 30, "FRONT VIEW", f"SCALE 1:{SC}")

# ================================================================ SIDE VIEW (RIGHT)
SX = CX[1]
sx = lambda d: SX + d * s
K.set_view(True)
rect(sx(0), YT, PD * s, PH * s, fill=NCS, lw=0.4)
for L in LET:
    y0_, y1_ = L["bb"][1], L["bb"][3]
    rect(sx(PD + 20), fy(y0_), 23 * s, (y1_ - y0_) * s, fill=BLK, lw=0.3)
for L in LET:
    for _, y_ in L["sp"]:
        rect(sx(PD), fy(y_) - 8 * s, 20 * s, 16 * s, fill=HexColor("#C8C8C8"), lw=0.2)
K.set_view(False)
hdim(sx(0), sx(PD + 43), YT - 16, "83", YT, fy(LBB[1]), size=8, small_side="r")
T(sx(PD + 43) + 10, fy(LBB[1]) - 18, "40 + 20 + 23", 8, color=K.GREY)
T(sx(PD + 43) + 10, fy(LBB[1]) - 8, "(DETAIL A)", 8, color=K.GREY)
T(sx(PD / 2), YT - 26, "A", 9, font="FB", align="c")
view_title(sx(PD + 43) / 2 + SX / 2, YB + 30, "SIDE VIEW", f"SCALE 1:{SC}")

# ================================================================ REAR VIEW (MIRRORED)
RX = CX[2] + 24
rx = lambda x: RX + (PW - x) * s
ry = fy
K.set_view(True)
rect(RX, YT, PW * s, PH * s, fill=HexColor("#EEF2F4"), lw=0.5)
rect(rx(PW - 25), ry(2), L_LEN * s, 30 * s, fill=HexColor("#B4B4B4"), lw=0.4)
rect(rx(PW - 25), ry(PH - 32), L_LEN * s, 30 * s, fill=HexColor("#B4B4B4"), lw=0.4)
tfr = lambda x, y: (rx(x), K.Y(ry(y)))
for L in LET:
    K.draw_shape(L["sub"], tfr, stroke=K.GREY, lw=0.1, dash=([2, 1.5], 0))
for yy in (7, PH - 7):
    for i in range(n_scr + 1):
        circle(rx(50 + pitch * i), ry(yy), 0.9, lw=0.4)
for L in LET:
    for x_, y_ in L["sp"]:
        circle(rx(x_), ry(y_), 0.6, fill=black, stroke=None)
K.set_view(False)
hchain(YT - 16, [rx(PW), rx(PW - 50), rx(50), rx(0)], [ry(7) - 3, ry(7) - 3, ry(7) - 3, YT],
       ["50", f"{n_scr}× {pitch:.0f}" if n_scr > 1 else f"{pitch:.0f}", "50"], size=8)
hchain(YB + 16, [rx(PW), rx(PW - 25), rx(25), rx(0)], [YB] * 4, ["25", f"{L_LEN}", "25"], size=8)
leader(rx(PW * 0.5), ry(PH - 17), RX + PW * s + 22, ry(PH - 70), 6)
leader(rx(50), ry(PH - 7), RX + PW * s + 22, ry(PH - 30), 9)
dx_, dy_ = D.d11_point(max(LET, key=lambda L: L["geom"].area))     # logotipo lankas
hx = rx(dx_)
circle(hx, ry(dy_), 1.6, fill=K.CABLE, stroke=None)
T(hx - 4, ry(dy_) - 4, "D11", 8, color=K.CABLE, align="r", auto_red=False)
# v288 išdėstymas (Rytis 2026-10-15): po galo vaizdo - TRAFO BOX | [DETAIL A virš LOGO DETAIL] | 3D; vienodi tarpai g
bxL = CX[3]
# Rytis 2026-10-15: „laido išvestis pačiame viršuje" - Ø11 kairėje šoninėje briaunoje VIRŠUJE (EX_Y nuo viršaus, po L 30x30
#  + 18 tarpas), laidas už plokštės nuo D11 aukštyn, tada į šoną
EX_Y = 50
ey = ry(EX_Y)
K.cable_line([(hx, ry(dy_)), (hx, ey), (rx(0), ey), (bxL + 35, ey), (bxL + 35, ey + 40)])
K.set_view(True); circle(rx(0), ey, 1.8, stroke=K.CABLE, lw=0.6); K.set_view(False)
T(rx(0) + 4, ey - 4, "Ø11", 8, color=K.CABLE, auto_red=False)
by_ = ey + 40
rect(bxL, by_, 70, 24, fill=HexColor(K.ralhex("7044")), lw=0.5)
T(bxL + 35, by_ + 10, "TRAFO BOX", 8, font="FB", align="c"); T(bxL + 35, by_ + 19, "RAL 7044", 8, align="c")
T(bxL + 40, ey + 22, "12V, 5 m, white", 8, color=K.CABLE, auto_red=False)
K.cable_line([(bxL + 35, by_ + 24), (bxL + 35, by_ + 38)]); T(bxL + 35, by_ + 47, "230V", 8, color=K.CABLE, align="c", auto_red=False)
vchain(RX - 14, [YT, ey, ry(dy_)], [rx(PW), rx(PW), rx(PW)], [f"{EX_Y}", f"{dy_ - EX_Y:.0f}"], size=8)
T(RX + PW * s / 2, YB + 66, f"Ø3,2 mm, 7 mm from edge; letter fixings Ø4 mm, {N_SP} pcs. (dots); Ø11 mm in left side edge, 50 mm from top", 7, color=K.GREY, align="c")
view_title(RX + PW * s / 2, YB + 30, "REAR VIEW (MIRRORED)", f"SCALE 1:{SC}")

# ================================================================ DETAIL A - SECTION 1:2 (lūžęs)
LY = round(LBB[1])
ax0 = CX[3] + 52
ya = detail_a(ax0, YB + 30 - 16 - H_A, LY)          # pavadinimas - pavadinimų eilėje
view_title(ax0 + 20 * MM / 2, ya + 16, "DETAIL A - SECTION", "SCALE 1:2  |  top edge + letter, broken view")

# ================================================================ LOGO DETAIL 1:10 (Rytis 2026-10-15: „trūksta detalesnių logotipo matmenų")
#  ženklas (lankas + žiedas), eilutės „Clas" / „Ohlson" - aukščiai, tarpai, pločiai; matmenys nuo logotipo gabarito kampo
_sym = [L for L in LET if L["bb"][1] < LBB[1] + 0.75 * (LBB[3] - LBB[1]) and L["bb"][3] - L["bb"][1] > 200]
_txt = [L for L in LET if L not in _sym]
_r1 = [L for L in _txt if L["bb"][1] < min(L_["bb"][3] for L_ in _txt) - 1]
_r1 = [L for L in _txt if L["bb"][3] <= min(L_["bb"][3] for L_ in _txt) + 5]
_r2 = [L for L in _txt if L not in _r1]
bbox = lambda Ls: (min(L["bb"][0] for L in Ls), min(L["bb"][1] for L in Ls), max(L["bb"][2] for L in Ls), max(L["bb"][3] for L in Ls))
SB, R1, R2 = bbox(_sym), bbox(_r1), bbox(_r2)
_arc = max(_sym, key=lambda L: L["bb"][3] - L["bb"][1]); _ring = min(_sym, key=lambda L: L["bb"][3] - L["bb"][1])
x3 = CX[5] + (COLS[5] - P3_W) / 2                                                # 3D - dešinėje, siauras aukštas
LXL = CX[4] + 12                                                # LOGO DETAIL - savas stulpelis
lx = lambda x: LXL + (x - LBB[0]) * sl
_lt = (YT - 36) + (_lh - (L_TOP + LG_H * sl + L_BOT)) / 2 + L_TOP   # centruota vertikaliai zonoje
ly = lambda y: _lt + (y - LBB[1]) * sl
K.set_view(True)
for L in LET:
    draw_sub(L["sub"], lambda x, y: (lx(x), K.Y(ly(y))), fill=BLK, stroke=None)
K.set_view(False)
# visos vertikalios grandinės - DEŠINĖJE (kairėje - DETAIL A pozicijos 1-3, ISO: išvadinės nekerta matmenų)
_rx = lambda Ls: lx(max(L["bb"][2] for L in Ls))
yy = [LBB[1], _ring["bb"][1], _ring["bb"][3], SB[3], R1[1], R1[3], R2[1], R2[3]]
lab = [f"{b - a:.0f}" for a, b in zip(yy, yy[1:])]; lab[1] = "Ø" + lab[1]
xr = lx(LBB[2])
vchain(xr + 14, [ly(v) for v in yy], [lx(_arc["bb"][2]), lx(_ring["bb"][2]), lx(_ring["bb"][2]), lx(_arc["bb"][2]),
       lx(R1[2]), lx(R1[2]), lx(R2[2]), lx(R2[2])], lab, size=8)
vchain(xr + 30, [ly(v) for v in (LBB[1], SB[3], LBB[3])], [xr + 14] * 3, [f"{SB[3] - LBB[1]:.0f}", f"{LBB[3] - SB[3]:.0f}"], size=8)
vchain(xr + 46, [ly(LBB[1]), ly(LBB[3])], [xr + 30] * 2, [f"{LBB[3] - LBB[1]:.0f}"], size=8)
xs1 = [LBB[0], _ring["bb"][0], _arc["bb"][2], _ring["bb"][2]]
hchain(ly(LBB[1]) - 12, [lx(v) for v in xs1], [ly(_arc["bb"][1]), ly(_ring["bb"][1]), ly(_arc["bb"][1]), ly(_ring["bb"][1])],
       [f"{b - a:.0f}" for a, b in zip(xs1, xs1[1:])], size=8)
xs2 = [LBB[0], R2[0], R1[2], R2[2]]
hchain(ly(LBB[3]) + 14, [lx(v) for v in xs2], [ly(_arc["bb"][3]), ly(R2[3]), ly(R1[3]), ly(R2[3])],
       [f"{b - a:.0f}" for a, b in zip(xs2, xs2[1:])], size=8)
hdim(lx(LBB[0]), lx(LBB[2]), ly(LBB[3]) + 28, f"{LBB[2] - LBB[0]:.0f}", ly(_arc["bb"][3]), ly(R2[3]), size=8)
view_title(lx((LBB[0] + LBB[2]) / 2), ly(LBB[3]) + 43, "LOGO DETAIL", f"SCALE 1:{SCL}  |  from logo outline")

# ================================================================ 3D VIEW
import r3d
S3 = r3d.Scene(30, 14)
# Rytis 2026-10-15: 3D - DEŠINĖJE, praktiškai tokio pat dydžio kaip priekio / galo projekcijos (tas pats aukštis YT..YB)
y3 = YT
w3, h3 = P3_W, YB - YT
S3.box((0, 0, 0), (PW, 0, 0), (0, PH, 0), (0, 0, PD), NCS, HexColor("#5D8EA6"))
for L in LET:
    g = sscale(L["geom"], 1, -1, origin=(0, 0)); g = stranslate(g, 0, PH)
    S3.extrude_xy(g, PD + 20, PD + 43, HexColor("#F4F4F4"), BLK)
S3.render((x3, y3, w3, h3))
view_title(x3 + w3 / 2, YB + 30, "3D VIEW", "ILLUSTRATIVE - NOT TO SCALE")

# ================================================================ juosta
W_pl = FLAT[0] * FLAT[1] / 1e6 * TS * 2.70
WT = W_pl + A_FACE * 3 * 2.70 + A_FACE * 20 * 1.19 + 2 * L_LEN / 1000 * 116e-6 * 2700
bom = [
    ["1", "Letter face P8 special", "Alu 3 mm", "RAL 9005", f"{PER:.2f} m / {A_FACE:.2f} m²"],
    ["2", "Letter body P8, milled shell", "Plexi 20 mm white", "-", f"{PER:.2f} m / {A_FACE:.2f} m²"],
    ["3", "LED", "LED", "-", "?"],
    ["4", "Spacer Ø16 x 20 mm, Ø4 mm holes", "Aluminium", "-", f"{N_SP} pcs."],
    ["5", f"Folded plate {PW} x {PH} x {PD} mm", "Alu 2 mm folded", "NCS S 0540-B", "1 pcs."],
    ["6", "L profile 30 x 30 x 2 mm (top + bottom)", "Aluminium", "-", f"{2 * L_LEN / 1000:.2f} m"],
    ["7", "Wall fixing", "?", "-", "?"],
    ["8", "Letter fixing through plate", "?", "-", f"{N_SP} pcs."],
    ["9", "Screw plate -> L, DIN 7504 N 4,2 x 16 mm", "Steel, hardened", "-", f"{2 * (n_scr + 1)} pcs."],
    ["10", "Cable 12V white, D11 -> Ø11 mm side", "cable", "-", "5 m"],
    ["11", "Trafo box (PSU)", "PSU", "RAL 7044", "1 pcs."],
]
md = [["Quantity", f"{QTY} pcs."], ["Overall size", f"{PW} x {PH} x {PD} mm"], ["Environment", "Exterior ?"],
      ["Plate", "Alu 2 mm, sheet 3000 x 1500 mm"], ["Flat", f"{FLAT[0]:.0f} x {FLAT[1]:.0f} mm, 1 part"],
      ["Plate finish", "NCS S 0540-B semi matt"], ["Logo", f"{LBB[2] - LBB[0]:.0f} x {LBB[3] - LBB[1]:.0f} mm"],
      ["Letters", "P8: Al 3 mm + plexi 20 mm"], ["Letter finish", "RAL 9005 semi matt"],
      ["Illumination", "LED, backlit"], ["Mounting", "L 30 x 30 x 2 mm, top + bottom"],
      ["Fixing holes", "Ø3,2 mm, 7 mm from edge, ~300 mm"], ["Cable", "12V, 5 m, white, left side top"],
      ["Letter holes", f"Ø4 mm: {N_SP} pcs., slots: {N_SLOT} pcs." if not N_D8 else f"Ø4 mm: {N_SP}, slots: {N_SLOT}, Ø8 mm: {N_D8} pcs."], ["Weight (calc.)", f"≈ {WT:.0f} kg / pcs., excl. PSU"]]
band("P8 SPECIAL - SECTION A-A (1:2)", p8_band, bom, md, "Order 226045 Clas Ohlson Bodø - LED sign 515 x 2380 mm, P8 special", "1 / 1",
     f"1:{SC} / 1:2", qty=QTY)
K.save(OUT)
K.pdf_fix_fonts(OUT)
LE.report("Bodø 226045", SC, G_, {"ortho H": (PH * s, K.VIEW_BOT - YT - A_BOT), "3D H": (h3, YB - YT),
          f"logo 1:{SCL} H": (L_TOP + LG_H * sl + L_BOT, _lh)})
print("logo", [round(v) for v in LBB], "letters", len(LET), "spacers", N_SP, "flat", FLAT, "W", round(WT, 1), "overflow", K.OVERFLOW)
