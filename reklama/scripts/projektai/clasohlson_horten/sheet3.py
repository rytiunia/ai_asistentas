"""Lapas 3/3 - Clas Ohlson Horten 1: P8 special ant folded plokštės 3000 x 1300, exterior (Clas Ohlson standartas)."""
import math, sys
import pymupdf as fitz
from shapely.geometry import Polygon
from shapely.affinity import scale as sscale, translate as stranslate
from common import *
import data as D

OUT = sys.argv[1]
SRC = "/root/.claude/uploads/454aabe4-a26e-51a4-90bd-3f68e4f6d938/f40b7013-CO-Horten-1-Sign-Plate-3000x1300_LED-2464x1000.pdf"
k1 = 25.4 / 72                                   # failas 1:1
PW, PH, PD = 3000, 1300, 40

# ---- raidės iš kliento failo
pg = fitz.open(SRC)[0]
LET, seen = [], set()
for d in pg.get_drawings():
    f = d.get("fill")
    if not f or sum(f[:3]) > 0.5:
        continue
    subs = D._subs(d)
    sub = [[(s_[0],) + tuple((q[0] * k1, q[1] * k1) for q in s_[1:]) for s_ in sp] for sp in subs]
    polys = [Polygon(D.flat(sp)).buffer(0) for sp in sub if len(D.flat(sp)) > 2]
    g = polys[0]
    for p_ in polys[1:]:
        g = g.symmetric_difference(p_)
    key = tuple(round(v) for v in g.bounds)
    if key in seen:
        continue
    seen.add(key)
    LET.append({"sub": sub, "geom": g, "bb": g.bounds})
D.attach_ref(LET)                       # Clas Ohlson proporcijų etalonas: Ø4 / išilginės / Ø8 pagal dydį
LBB = (min(L["bb"][0] for L in LET), min(L["bb"][1] for L in LET), max(L["bb"][2] for L in LET), max(L["bb"][3] for L in LET))
N_SP = sum(len(L["sp"]) for L in LET)
N_SLOT = sum(1 for L in LET for f in L["feats"] if f["type"] == "SLOT")
N_D8 = sum(1 for L in LET for f in L["feats"] if f["type"] == "D8")
A_FACE = sum(L["geom"].area for L in LET) / 1e6
PER = sum(L["geom"].length for L in LET) / 1000
L_LEN = PW - 50
span = PW - 100; n_scr = round(span / 300); pitch = span / n_scr
FLAT = D.flat_size(PW)[0], PH + 2 * PD - 2 * D.BD

begin(15)
s = MM / 20
X0, YT = K.IX0 + 72, 70
fx = lambda x: X0 + x * s
fy = lambda y: YT + y * s
YB = fy(PH)

# ================================================================ FRONT VIEW 1:20
K.set_view(True)
rect(X0, YT, PW * s, PH * s, fill=NCS, lw=0.5)
tf = lambda x, y: (fx(x), K.Y(fy(y)))
for L in LET:
    draw_sub(L["sub"], tf, fill=BLK, stroke=None)
K.set_view(False)
hdim(X0, fx(PW), YT - 16, f"{PW}", YT, YT, size=12)
xs = [0, LBB[0], LBB[2], PW]
hchain(YB + 18, [fx(v) for v in xs], [YB, fy(LBB[3]), fy(LBB[3]), YB], [f"{round(b - a)}" for a, b in zip(xs, xs[1:])], size=12)
ys = [0, LBB[1], LBB[3], PH]
vchain(X0 - 14, [fy(v) for v in ys], [X0, fx(LBB[0]), fx(LBB[0]), X0], [f"{round(b - a)}" for a, b in zip(ys, ys[1:])], size=8)
vchain(X0 - 36, [YT, YB], [X0, X0], [f"{PH}"], size=12)
leader(fx(2900), fy(1220), fx(PW) + 18, fy(1260), 5)
leader(fx(1500), fy(520), fx(PW) + 18, fy(470), 1)
view_title(X0 + PW * s / 2, YB + 48, "FRONT VIEW", "SCALE 1:20")

# ================================================================ SIDE VIEW (RIGHT) 1:20
SX = fx(PW) + 62
sx = lambda d: SX + d * s                    # d - nuo sienos
K.set_view(True)
rect(sx(0), YT, PD * s, PH * s, fill=NCS, lw=0.4)
for L in LET:
    y0_, y1_ = L["bb"][1], L["bb"][3]
    rect(sx(PD + 20), fy(y0_), 23 * s, (y1_ - y0_) * s, fill=BLK, lw=0.3)
    rect(sx(PD + 20) + 20 * s * 0, fy(y0_), 20 * s, (y1_ - y0_) * s, fill=white, lw=0.2)
for L in LET:
    for _, y_ in L["sp"]:
        rect(sx(PD), fy(y_) - 8 * s, 20 * s, 16 * s, fill=HexColor("#C8C8C8"), lw=0.2)
K.set_view(False)
hdim(sx(0), sx(PD + 43), YT - 14, "83", YT, fy(LBB[1]), size=8, small_side="r")
T(sx(PD + 43) + 26, YT - 11, "(40 + 20 + 23, see DETAIL A)", 8, color=K.GREY)
vchain(sx(PD + 43) + 16, [YT, YB], [sx(PD), sx(PD)], [f"{PH}"], size=12)
circle(sx(PD / 2), YT + 4, 9, lw=0.4)
T(sx(PD / 2) - 14, YT - 1, "A", 9, font="FB", align="r")
view_title(sx(40), YB + 48, "SIDE VIEW (RIGHT)", "SCALE 1:20")

# ================================================================ DETAIL A - SECTION 1:2 (lūžęs)
LY = round(LBB[1])
ax0 = sx(PD + 43) + 150
ya = detail_a(ax0, YT + 40, LY)
view_title(ax0 + 20 * MM / 2, ya + 20, "DETAIL A - SECTION", "SCALE 1:2  |  top edge + letter, broken view")

# ================================================================ REAR VIEW (MIRRORED) 1:20
RY = YB + 92
rx = lambda x: X0 + (PW - x) * s            # veidrodinis
ry = lambda y: RY + y * s
K.set_view(True)
rect(X0, RY, PW * s, PH * s, fill=HexColor("#EEF2F4"), lw=0.5)
rect(rx(PW - 25), ry(2), L_LEN * s, 30 * s, fill=HexColor("#B4B4B4"), lw=0.3)
rect(rx(PW - 25), ry(PH - 32), L_LEN * s, 30 * s, fill=HexColor("#B4B4B4"), lw=0.3)
tfr = lambda x, y: (rx(x), K.Y(ry(y)))
for L in LET:
    K.draw_shape(L["sub"], tfr, stroke=K.GREY, lw=0.1, dash=([2, 1.5], 0))
K.set_view(False)
for L in LET:
    for x_, y_ in L["sp"]:
        line(rx(x_) - 2, ry(y_), rx(x_) + 2, ry(y_), 0.3); line(rx(x_), ry(y_) - 2, rx(x_), ry(y_) + 2, 0.3)
for yy in (7, PH - 7):
    for i in range(n_scr + 1):
        circle(rx(50 + pitch * i), ry(yy), 0.9, lw=0.3)
for i in range(n_scr + 1):
    K.centerline(rx(50 + pitch * i), RY - 4, rx(50 + pitch * i), ry(12))
hchain(RY - 14, [rx(PW), rx(PW - 50), rx(50), rx(0)], [RY - 4, RY - 4, RY - 4, RY - 4],
       ["50", f"{n_scr} x {pitch:.0f} = {span:.0f}", "50"], size=8)
hchain(ry(PH) + 16, [rx(PW), rx(PW - 25), rx(25), rx(0)], [ry(PH)] * 4, ["25", f"{L_LEN} (L30x30x2)", "25"], size=8)
leader(rx(PW / 2), ry(PH - 17), rx(PW / 2) + 40, ry(PH) + 34, 6)
leader(rx(800), ry(7), rx(800) - 30, RY - 30, 9)
T(fx(PW) + 8, ry(PH / 2), "Ø3.2 x 2 x 11, 7 from edge", 8)
T(fx(PW) + 8, ry(PH / 2) + 11, f"+ letter fixing points Ø4 x {N_SP}", 8, color=K.GREY)
T(fx(PW) + 8, ry(PH / 2) + 22, "letters hidden - dashed", 8, color=K.GREY)
dx_, dy_ = D.d11_point(min(LET, key=lambda L: L["bb"][0]))     # logotipo lankas (kairėje)
hx = rx(dx_)
bxL = fx(PW) + 18
circle(hx, ry(dy_), 1.6, fill=K.CABLE, stroke=None)
T(hx - 4, ry(dy_) + 12, "D11", 8, color=K.CABLE, align="r", auto_red=False)
K.cable_line([(hx, ry(dy_)), (bxL, ry(dy_))])                    # kairė šoninė briauna (veidrodiniame - dešinėje)
circle(rx(0), ry(dy_), 1.8, stroke=K.CABLE, lw=0.6)
rect(bxL, RY + 6, 70, 24, fill=HexColor(K.ralhex("7044")), lw=0.5)
T(bxL + 35, RY + 16, "TRAFO BOX", 8, font="FB", align="c"); T(bxL + 35, RY + 25, "RAL 7044", 8, align="c")
T(bxL + 35, RY + 1, "12V, 5.0 m, white", 8, color=K.CABLE, align="c", auto_red=False)
K.cable_line([(bxL + 70, RY + 18), (bxL + 86, RY + 18)]); T(bxL + 88, RY + 21, "230V", 8, color=K.CABLE, auto_red=False)
hchain(ry(PH) + 34, [rx(PW), rx(dx_), rx(0)], [ry(PH)] * 3, [f"{PW - dx_:.0f}", f"{dx_:.0f}"], size=8)
T(fx(PW) + 8, ry(PH / 2) + 33, f"Ø11 in left side edge, {dy_:.0f} from top", 8, color=K.CABLE, auto_red=False)
view_title(X0 + PW * s / 2, ry(PH) + 50, "REAR VIEW (MIRRORED)", "SCALE 1:20")

# ================================================================ 3D VIEW (r3d)
import r3d
S3 = r3d.Scene()
x3, y3, w3, h3 = K.IX1 - 430, RY - 30, 410, K.VIEW_BOT - RY + 10
S3.box((0, 0, 0), (PW, 0, 0), (0, PH, 0), (0, 0, PD), NCS, HexColor("#5D8EA6"))
for L in LET:
    g = sscale(L["geom"], 1, -1, origin=(0, 0)); g = stranslate(g, 0, PH)
    S3.extrude_xy(g, PD + 20, PD + 43, HexColor("#F4F4F4"), BLK)
S3.render((x3, y3, w3, h3))
view_title(x3 + w3 / 2, y3 + h3 + 4, "3D VIEW", "ILLUSTRATIVE - NOT TO SCALE")


# ================================================================ juosta
W_pl = FLAT[0] * FLAT[1] / 1e6 * 2 * 2.70
W = W_pl + A_FACE * 3 * 2.70 + A_FACE * 20 * 1.19 + 2 * L_LEN / 1000 * 116e-6 * 2700
bom = [
    ["1", "Letter face P8 special", "Alu 3 mm", "RAL 9005", f"{PER:.2f} m / {A_FACE:.2f} m²"],
    ["2", "Letter body P8, milled shell", "Plexi 20 mm white", "-", f"{PER:.2f} m / {A_FACE:.2f} m²"],
    ["3", "LED Baltled Crown Mini 0.3 W", "-", "6500K", "?"],
    ["4", "Spacer Ø16x20 on Ø4 holes (CO std.)", "Aluminium", "-", f"{N_SP} pcs."],
    ["5", f"Folded plate {PW} x {PH}, 40 deep", "Alu 2 mm folded", "NCS S 0540-B", f"1 pcs. / flat {FLAT[0]:.0f} x {FLAT[1]:.0f}"],
    ["6", "L profile 30x30x2 (top + bottom)", "Aluminium", "-", f"2 x {L_LEN / 1000:.2f} = {2 * L_LEN / 1000:.2f} m"],
    ["7", "Wall fixing", "?", "?", "?"],
    ["8", "Letter fixing through plate", "?", "-", f"{N_SP} pcs."],
    ["9", "Screw plate -> L, DIN 7504 N 4.2x16", "Steel, hard.", "-", f"{2 * (n_scr + 1)} pcs. ({n_scr + 1}/L)"],
    ["10", "Cable 12V, white (D11 -> Ø11 side edge)", "-", "white", "5.0 m"],
    ["11", "Trafo box 12V", "?", "RAL 7044", "1 pcs."],
]
md = [["Quantity", "1 pcs."], ["Overall size", f"{PW} x {PH}"], ["Environment", "Exterior"],
      ["Plate", "Alu 2 mm, depth 40, R2, 1 pcs."], ["Flat", f"{FLAT[0]:.0f} x {FLAT[1]:.0f} (Al 2000x4000)"],
      ["Plate finish", "NCS S 0540-B semi matte"], ["Logo", f"{LBB[2] - LBB[0]:.0f} x {LBB[3] - LBB[1]:.0f}, centred"],
      ["Letters", "P8 special 3 + 20, spacers 20"], ["Letter finish", "RAL 9005 semi matt"],
      ["Illumination", "Baltled Crown Mini 0.3 W 6500K"], ["Mounting", "L30x30x2 top + bottom"],
      ["Fixing holes", "Ø3.2, 7 from edge, 50 / ~300"], ["Cable", "12V 5 m white, left side -> 7044"],
      ["Letter holes", f"Ø4 x{N_SP}, slot 6.1x3.7 x{N_SLOT}, Ø8 x{N_D8}"], ["Weight (calc.)", f"≈ {W:.0f} kg / pcs, excl. PSU"]]
band("P8 SPECIAL - SECTION A-A (1:2)", p8_band, bom, md, "Clas Ohlson Horten 1 - folded plate 3000 x 1300, P8", "3 / 3", "1:20 / 1:2")
K.save(OUT)
print("logo", [round(v) for v in LBB], "letters", len(LET), "spacers", N_SP, [len(L["sp"]) for L in LET], "W", round(W, 1), "flat", FLAT, "overflow", K.OVERFLOW)
