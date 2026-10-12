"""EXTRA order 225978 - lapas 3/5: FAS 700H80 stogo atramos (rekomendacija), etaloninis stilius (lapas_core).
Geometrija (mm): x nuo iškabos kairės (apskritimo kraštas), y - aukštyn nuo stogo, z - gylis (+ į priekį, raidės priekis 100).
Naudojimas: python3 roof_sheet.py <kliento švarus PDF> <out.pdf> [skill scripts dir]"""
import sys, math, json, os
SK = sys.argv[3] if len(sys.argv) > 3 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, SK)
import lapas_core as K
from lapas_core import T, line, rect, poly, hdim, vchain, hchain, leader, view_title, MM
from reportlab.lib.colors import HexColor, white, black, Color
import pymupdf as fitz
from shapely.geometry import Polygon, box as sbox, Point
from shapely.ops import unary_union

SRC, OUT = sys.argv[1], sys.argv[2]
# ---------------------------------------------------------------- kliento geometrija (1:10, pt -> mm)
X0P, Y0P, SC = 461.5, 266.4, 4012 / (1598.7 - 461.5)
ROOF = 850.0                                   # stogas: 150 mm po apskritimu (kliento nurodymas)
CROP = fitz.Rect(450, 255, 1610, 470)
pg = fitz.open(SRC)[0]
shapes = []
for d in pg.get_drawings():
    if d.get("fill") is None or not CROP.contains(d["rect"]):
        continue
    f = tuple(d["fill"][:3])
    if (f[0] < 0.2 and f[1] < 0.2) or (abs(f[0] - 0.91) < 0.05 and abs(f[1] - 0.45) < 0.05):
        continue                                # rodyklių taškai / tekstas / maitinimo ženklai
    sub = K.drawing_to_subpaths(d, lambda q: ((q[0] - X0P) * SC, ROOF - (q[1] - Y0P) * SC))
    shapes.append((sub, f))

# ---------------------------------------------------------------- rėmas (iš 2 lapo braizyti_begeliai išvesties)
def yr(y_top):                                  # y nuo iškabos viršaus -> nuo stogo
    return ROOF - y_top
RAILS = [  # (x0, x1, y_top_from_sign_top) U30x30x2
    (823, 2708, 174), (823, 2833, 508),          # EXTRA
    (3218, 3961, 240), (3290, 3669, 428), (3289, 3960, 523)]   # 7-23
ZSTR = [(135, 485, 154), (135, 485, 700 - 154 - 30)]           # X: Z juostos plokštės nugaroje
D_BACK = 650                                     # atramos (kicker) pėda už kojos plokštumos
# kojos: (x, viršaus aukštis nuo stogo, ką laiko) ; atramos: (x, tvirtinimo aukštis)
LEGS = [(160, 696, "X"), (460, 696, "X"),
        (837, 676, "EXTRA"), (2779, 342, "EXTRA"),
        (3281, 327, "7-23"), (3946, 327, "7-23")]
KICK = [(160, 681, "X"), (460, 681, "X"), (837, 661, "EXTRA"), (2673, 661, "EXTRA"),
        (3363, 595, "7-23"), (3930, 595, "7-23")]
TP = 5                                            # pagrindo plokštės storis

# ---------------------------------------------------------------- vėjas (EN 1991-1-4, prielaida)
QP, CF, GQ = 0.80, 1.8, 1.5
GRP = {"X": (0.385, 500, 681), "EXTRA": (2.050 * 0.420, 500, 661), "7-23": (0.805 * 0.348, 458, 595)}
WIND = {}
for k, (A, zc, hk) in GRP.items():
    F = CF * QP * A
    H_ = F * zc / hk
    L_ = math.hypot(hk, D_BACK)
    N = H_ / 2 * L_ / D_BACK
    V = H_ / 2 * hk / D_BACK
    WIND[k] = dict(A=A, F=F, H=H_, N=N, V=V, L=L_)
NMAX = max(w["N"] for w in WIND.values()); VMAX = max(w["V"] for w in WIND.values())
for k, w in WIND.items():
    print(f"  {k}: A {w['A']:.2f} m2, F {w['F']:.2f} kN, kicker N {w['N']:.2f} kN (ULS {w['N'] * GQ:.2f}), foot V {w['V']:.2f} kN")

BOM_ROWS = 10
K.set_band(BOM_ROWS)
tmp = OUT + ".tmp"
K.init(tmp, "EXTRA_order_225978_3_roof_mount")
K.frame()
LEGC, KICKC, RAILC, PLC = HexColor("#9A9A9A"), HexColor("#B0B0B0"), HexColor("#C8C8C8"), HexColor("#7A7A7A")

# ================================================================ FRONT VIEW 1:25
s1 = MM / 20
FX, FYR = K.IX0 + 64, K.IY0 + 196                # x=0 ir stogo linija
F = lambda x, y: (FX + x * s1, FYR - y * s1)
K.set_view(True)
for x0, x1, yt in RAILS:
    a, b = F(x0, yr(yt)), F(x1, yr(yt + 30))
    rect(a[0], a[1], b[0] - a[0], b[1] - a[1], fill=RAILC, lw=0.4)
for x0, x1, yt in ZSTR:
    a, b = F(x0, yr(yt)), F(x1, yr(yt + 30))
    rect(a[0], a[1], b[0] - a[0], b[1] - a[1], fill=RAILC, lw=0.4, dash=(2, 1))
for x, ht, _ in LEGS:                            # kojos - už iškabos (matomos tik žemiau raidžių)
    a, b = F(x - 15, ht), F(x + 15, 0)
    rect(a[0], a[1], b[0] - a[0], b[1] - a[1], fill=LEGC, lw=0.4)
    a, b = F(x - 60, TP), F(x + 60, 0)
    rect(a[0], a[1], b[0] - a[0], b[1] - a[1], fill=PLC, lw=0.4)
for sub, f in shapes:
    if abs(f[0] - 0.58) < 0.03 and abs(f[1] - 0.59) < 0.03:
        continue                                  # kliento bėgelių grafika - vietoj jos tikri profiliai
    K.draw_shape(sub, lambda x, y: (F(x, y)[0], K.Y(F(x, y)[1])), fill=Color(*f), stroke=HexColor("#555555"), lw=0.1)
for x, ht, _ in LEGS:                            # kojų dalis po raidėmis - punktyru (už iškabos)
    a, b = F(x - 15, ht), F(x + 15, 0)
    rect(a[0], a[1], b[0] - a[0], b[1] - a[1], fill=None, stroke=HexColor("#444444"), lw=0.3, dash=(2, 1.2))
K.set_view(False)
# stogo linija
line(F(-150, 0)[0], FYR, F(4162, 0)[0], FYR, 0.5, GREY := HexColor("#6E6E6E"))
T(F(4162, 0)[0] + 3, FYR + 3, "ROOF", 8, color=GREY, auto_red=False)
# matmenys
hdim(F(0, 0)[0], F(4012, 0)[0], F(0, 850)[1] - 30, "4012", F(0, 850)[1], F(4012, 850)[1], size=12)
xs = [0] + [x for x, _, _ in LEGS] + [4012]
hchain(FYR + 22, [F(x, 0)[0] for x in xs], [FYR + 2] * len(xs),
       [f"{b - a:.0f}" for a, b in zip(xs[:-1], xs[1:])], size=8)
vchain(F(0, 0)[0] - 18, [F(0, 850)[1], F(0, 150)[1], FYR], [F(350, 850)[0], F(350, 150)[0], F(0, 0)[0]],
       ["700", "150"], size=12)
vchain(F(4012, 0)[0] + 22, [F(0, 710)[1], F(0, 661)[1], F(0, 327)[1], F(0, 290)[1], FYR],
       [F(2850, 0)[0]] * 5, ["49", "334", "37", "290"], size=8)
T(F(4012, 0)[0] + 52, F(0, 661)[1] + 3, "top rail", 8, color=GREY, auto_red=False)
T(F(4012, 0)[0] + 52, F(0, 327)[1] + 3, "bottom rail", 8, color=GREY, auto_red=False)
for i, (x, ht, g) in enumerate(LEGS):
    if i in (0, 2, 4):
        leader(*F(x, ht * 0.15 + 10), F(x, 0)[0] + (-26 if i == 0 else 22), FYR + 46, 1)
leader(*F(3946 + 40, 3), F(3946, 0)[0] + 40, FYR + 46, 3)
K.c.saveState(); K.c.setStrokeColor(black); K.c.setLineWidth(0.6)
for x in (837,):                                  # pjūvio A-A žyma per EXTRA koją
    xa = F(x, 0)[0]
    K.c.line(xa, K.Y(F(0, 900)[1]), xa, K.Y(F(0, 870)[1])); K.c.line(xa, K.Y(FYR + 8), xa, K.Y(FYR + 0))
K.c.restoreState()
T(F(837, 0)[0] + 4, F(0, 900)[1] + 2, "A", 9, font="FB")
view_title(F(2006, 0)[0], FYR + 74, "FRONT VIEW - ROOF MOUNT", "SCALE 1:20  |  legs behind the sign - dashed")

# ================================================================ TOP VIEW 1:25 (stogo planas)
TY0 = FYR + 118                                    # iškabos priekio linija
Tz = lambda x, z: (FX + x * s1, TY0 + (100 - z) * s1)   # z: 100 priekis, 0 raidžių galas, -30 bėgelis, -60 koja
K.set_view(True)
for x0, x1, _ in [(812, 2862, 0), (3207, 4012, 0)]:
    a, b = Tz(x0, 100), Tz(x1, 0)
    rect(a[0], a[1], b[0] - a[0], b[1] - a[1], fill=HexColor("#D9D9D9"), lw=0.4)
a, b = Tz(30, 100), Tz(580, 0)
rect(a[0], a[1], b[0] - a[0], b[1] - a[1], fill=HexColor("#D9D9D9"), lw=0.4)
a, b = Tz(0, -30), Tz(700, -33)
rect(a[0], a[1], b[0] - a[0], b[1] - a[1], fill=HexColor("#F7B500"), lw=0.4)
for x0, x1, _ in ZSTR[:1]:
    a, b = Tz(x0, -33), Tz(x1, -63)
    rect(a[0], a[1], b[0] - a[0], b[1] - a[1], fill=RAILC, lw=0.4)
for x0, x1, _ in RAILS[:2] + RAILS[2:3]:
    a, b = Tz(x0, 0), Tz(x1, -30)
    rect(a[0], a[1], b[0] - a[0], b[1] - a[1], fill=RAILC, lw=0.4)
for (x, ht, g), (xk, hk, _) in zip(LEGS, KICK):
    zl = -45 if g != "X" else -78                 # kojos ašis (už bėgelio / Z juostos)
    a, b = Tz(x - 60, zl + 60), Tz(x + 60, zl - 60)
    rect(a[0], a[1], b[0] - a[0], b[1] - a[1], fill=PLC, lw=0.4)
    a, b = Tz(x - 15, zl + 15), Tz(x + 15, zl - 15)
    rect(a[0], a[1], b[0] - a[0], b[1] - a[1], fill=LEGC, lw=0.4)
    a, b = Tz(xk - 15, zl), Tz(xk + 15, zl - D_BACK)
    rect(a[0], a[1], b[0] - a[0], b[1] - a[1], fill=KICKC, lw=0.4)
    a, b = Tz(xk - 60, zl - D_BACK + 60), Tz(xk + 60, zl - D_BACK - 60)
    rect(a[0], a[1], b[0] - a[0], b[1] - a[1], fill=PLC, lw=0.4)
K.set_view(False)
T(Tz(0, 0)[0] - 6, Tz(0, 50)[1] + 3, "FRONT", 8, align="r", color=GREY, auto_red=False)
zl = -45
vchain(Tz(4012, 0)[0] + 22, [Tz(0, zl)[1], Tz(0, zl - D_BACK)[1]], [Tz(3930, 0)[0]] * 2, [f"{D_BACK}"], size=8)
leader(*Tz(3930, zl - D_BACK * 0.3), Tz(3930, 0)[0] - 40, Tz(0, zl - D_BACK * 0.3)[1], 2)
leader(*Tz(2673 + 40, zl - D_BACK), Tz(2673, 0)[0] + 60, Tz(0, zl - D_BACK)[1] + 14, 3)
view_title(F(2006, 0)[0], Tz(0, zl - D_BACK - 60)[1] + 34, "TOP VIEW (ROOF PLAN)", "SCALE 1:20  |  base plate positions")

# ================================================================ SECTION A-A 1:10 (per EXTRA koją x=837)
s2 = MM / 10
SX, SYR = K.IX0 + 800, K.IY0 + 290                 # SX - iškabos priekio plokštuma (z=100), SYR - stogas
S = lambda z, y: (SX - (100 - z) * s2, SYR - y * s2)   # vaizdas iš dešinės: priekis dešinėje? -> priekis kairėje
S = lambda z, y: (SX + (100 - z) * s2, SYR - y * s2)   # priekis (z=100) - kairėje, gilyn - į dešinę
K.set_view(True)
# raidė E (P6, 100) - šonas
a, b = S(100, 710), S(0, 290)
rect(a[0], a[1], b[0] - a[0], b[1] - a[1], fill=HexColor("#C1121C"), lw=0.4)
rect(a[0], a[1], 0.9, b[1] - a[1], fill=white, lw=0.3)
# bėgeliai U30 (pjūvis)
for yc in (661, 327):
    a, b = S(0, yc + 15), S(-30, yc - 15)
    rect(a[0], a[1], b[0] - a[0], b[1] - a[1], fill=RAILC, lw=0.4)
    rect(a[0] + 0.6, a[1] + 0.6, b[0] - a[0] - 1.2, b[1] - a[1] - 1.2, fill=white, lw=0.2)
# kampuotis L40x40x4 + koja □30x30x2
a, b = S(-30, 676), S(-60, 0 + TP)
rect(a[0], a[1], b[0] - a[0], b[1] - a[1], fill=LEGC, lw=0.4)
for yc in (661, 327):
    a, b = S(-30, yc + 20), S(-34, yc - 20)
    rect(a[0], a[1], b[0] - a[0], b[1] - a[1], fill=PLC, lw=0.3)
    K.centerline(S(10, yc)[0], S(0, yc)[1], S(-70, yc)[0], S(0, yc)[1])
# pagrindo plokštės
for zc in (-45, -45 - D_BACK):
    a, b = S(zc + 60, TP), S(zc - 60, 0)
    rect(a[0], a[1], b[0] - a[0], b[1] - a[1], fill=PLC, lw=0.4)
    for dz in (-45, 45):
        K.centerline(S(zc + dz, 0)[0], S(0, 20)[1], S(zc + dz, 0)[0], S(0, -20)[1])
# atrama (kicker) □30x30x2: nuo viršutinio bėgelio (661) iki pėdos (z = -45 - 650)
p0, p1 = (-45, 661), (-45 - D_BACK, TP + 25)
ang = math.atan2(p0[1] - p1[1], p0[0] - p1[0])
nx, ny = -math.sin(ang) * 15, math.cos(ang) * 15
pts = [S(p0[0] + nx, p0[1] + ny), S(p0[0] - nx, p0[1] - ny), S(p1[0] - nx, p1[1] - ny), S(p1[0] + nx, p1[1] + ny)]
poly(pts, fill=KICKC, lw=0.4)
# šakutės (fork lug) galuose
for q in (p0, p1):
    K.c.saveState(); K.c.setFillColor(white); K.c.setStrokeColor(black); K.c.setLineWidth(0.4)
    K.c.circle(S(*q)[0], K.Y(S(*q)[1]), 2.2, stroke=1, fill=1); K.c.restoreState()
a, b = S(p1[0] + 12, TP + 34), S(p1[0] - 12, TP)
rect(a[0], a[1], b[0] - a[0], b[1] - a[1], fill=PLC, lw=0.3)
K.set_view(False)
line(S(160, 0)[0], SYR, S(-800, 0)[0], SYR, 0.5, GREY)
T(S(-800, 0)[0] + 3, SYR + 3, "ROOF", 8, color=GREY, auto_red=False)
# matmenys
vchain(S(100, 0)[0] - 18, [S(0, 710)[1], S(0, 661)[1], S(0, 327)[1], S(0, 290)[1], SYR],
       [S(100, 0)[0]] * 5, ["49", "334", "37", "290"], size=8)
vchain(S(100, 0)[0] - 40, [S(0, 710)[1], SYR], [S(100, 0)[0]] * 2, ["710"], size=12)
hdim(S(-45, 0)[0], S(-45 - D_BACK, 0)[0], SYR + 22, f"{D_BACK}", SYR + 2, SYR + 2, size=12)
hdim(S(100, 0)[0], S(-45, 0)[0], SYR + 22, "145", SYR + 2, SYR + 2, size=8, small_side="l")
_deg = math.degrees(math.atan2(661 - TP - 25, D_BACK))
T(S(-45 - D_BACK + 90, 0)[0], SYR - 14, f"~{_deg:.0f}°", 9)
T(*S(-45 - D_BACK / 2 + 70, 360), f"L ≈ {WIND['EXTRA']['L']:.0f}", 8, rot=-_deg)
leader(*S(-45, 520), S(-45, 0)[0] + 36, S(0, 560)[1], 1)
leader(*S(-45 - D_BACK * 0.55, 661 * 0.45 + 15), S(-45 - D_BACK * 0.55, 0)[0] + 40, S(0, 400)[1], 2)
leader(*S(-45 - D_BACK - 40, 3), S(-45 - D_BACK, 0)[0] + 30, SYR + 44, 3)
leader(*S(-45 + 40, 3), S(-45, 0)[0] + 40, SYR + 44, 3)
leader(*S(p0[0], p0[1]), S(p0[0], 0)[0] + 50, S(0, 700)[1], 4)
leader(*S(-32, 661 + 18), S(-32, 0)[0] + 20, S(0, 790)[1], 5)
T(S(-300, 0)[0], S(0, 810)[1], "U30x30x2 rail (sheet 2)", 8, color=GREY, auto_red=False)
view_title(S(-300, 0)[0], SYR + 74, "SECTION A-A", "SCALE 1:10  |  EXTRA leg, typical for all legs")

# ================================================================ DETAIL B - pagrindo plokštė 1:5 (planas)
s5 = MM / 5
BX, BY = K.IX0 + 1035, K.IY0 + 70
B = lambda x, y: (BX + x * s5, BY + y * s5)
K.set_view(True)
a, b = B(-60, -60), B(60, 60)
rect(a[0], a[1], b[0] - a[0], b[1] - a[1], fill=PLC, lw=0.4)
a, b = B(-15, -15), B(15, 15)
rect(a[0], a[1], b[0] - a[0], b[1] - a[1], fill=LEGC, lw=0.4)
rect(a[0] + 2 * s5, a[1] + 2 * s5, b[0] - a[0] - 4 * s5, b[1] - a[1] - 4 * s5, fill=white, lw=0.3)
for dx in (-45, 45):
    for dy in (-45, 45):
        K.c.saveState(); K.c.setFillColor(white); K.c.setStrokeColor(black); K.c.setLineWidth(0.4)
        K.c.circle(B(dx, dy)[0], K.Y(B(dx, dy)[1]), 4.5 * s5, stroke=1, fill=1); K.c.restoreState()
        K.centerline(B(dx - 9, dy)[0], B(0, dy)[1], B(dx + 9, dy)[0], B(0, dy)[1])
        K.centerline(B(dx, 0)[0], B(0, dy - 9)[1], B(dx, 0)[0], B(0, dy + 9)[1])
K.set_view(False)
hdim(B(-60, 0)[0], B(60, 0)[0], B(0, -60)[1] - 22, "120", B(0, -60)[1], B(0, -60)[1])
hchain(B(0, -60)[1] - 10, [B(x, 0)[0] for x in (-60, -45, 45, 60)], [B(0, -45)[1]] * 4, ["15", "90", "15"])
vchain(B(60, 0)[0] + 14, [B(0, -60)[1], B(0, 60)[1]], [B(60, 0)[0]] * 2, ["120"])
T(B(0, 0)[0], B(0, 60)[1] + 14, "4 x Ø9, plate Alu 5 mm, leg welded", 8, align="c")
T(B(0, 0)[0], B(0, 60)[1] + 25, "kicker foot: same plate + fork lug, M8", 8, align="c")
view_title(B(0, 0)[0], B(0, 60)[1] + 48, "DETAIL B - BASE PLATE", "SCALE 1:5  |  EPDM 3 mm pad under plate")

# ================================================================ DETAIL C - koja / atrama prie U bėgelio 1:5 (pjūvis)
CX, CY = K.IX0 + 1030, K.IY0 + 470
C = lambda z, y: (CX + (0 - z) * s5, CY - y * s5)
K.set_view(True)
a, b = C(30, 25), C(0, -25)                        # raidės galas (fragmentas)
rect(a[0], a[1], b[0] - a[0], b[1] - a[1], fill=HexColor("#C1121C"), lw=0.4)
a, b = C(0, 15), C(-30, -15)                       # U30x30x2
rect(a[0], a[1], b[0] - a[0], b[1] - a[1], fill=RAILC, lw=0.4)
rect(C(-2, 0)[0], C(0, 13)[1], (C(-30, 0)[0] - C(-2, 0)[0]), (C(0, -13)[1] - C(0, 13)[1]), fill=white, lw=0.3)
a, b = C(-30, 34), C(-34, -34)                     # kampuotis L40x40x4 (kojelė prie U flanšų galų)
rect(a[0], a[1], b[0] - a[0], b[1] - a[1], fill=PLC, lw=0.4)
a, b = C(-34, 45), C(-64, -45)                     # koja □30x30x2
rect(a[0], a[1], b[0] - a[0], b[1] - a[1], fill=LEGC, lw=0.4)
rect(a[0] + 2 * s5, a[1], b[0] - a[0] - 4 * s5, b[1] - a[1], fill=white, lw=0.3)
for yb in (22,):
    K.centerline(C(-10, 0)[0], C(0, yb)[1], C(-70, 0)[0], C(0, yb)[1])
    rect(C(-34, 0)[0], C(0, yb + 4)[1], C(-66, 0)[0] - C(-34, 0)[0], 8 * s5, fill=HexColor("#3A3A3A"), lw=0.2)
K.centerline(C(-20, 0)[0], C(0, 15)[1] - 6, C(-20, 0)[0], C(0, -15)[1] + 6)
K.set_view(False)
leader(*C(-15, 15), C(-15, 0)[0] - 40, C(0, 60)[1], 5)
leader(*C(-49, -30), C(-49, 0)[0] + 30, C(0, -60)[1], 1)
leader(*C(-50, 22), C(-50, 0)[0] + 30, C(0, 60)[1], 6)
leader(*C(-20, -12), C(-20, 0)[0] - 30, C(0, -60)[1], 7)
T(C(-20, 0)[0], C(0, -45)[1] + 34, "bracket L40x40x4, l = 60", 8, align="c")
view_title(C(-20, 0)[0], C(0, -45)[1] + 60, "DETAIL C - LEG TO RAIL", "SCALE 1:5  |  schematic")

# ================================================================ 3D VIEW (stogo atramos)
V3 = K.View3D(yaw=150, pitch=20)
def letter_geoms():
    out = []
    for sub, f in shapes:
        if abs(f[0] - 0.58) < 0.03 and abs(f[1] - 0.59) < 0.03:
            continue
        g = None
        for sp in sub:
            pts = K.flatten(sp, 10)
            if len(pts) >= 3:
                q = Polygon(pts).buffer(0); g = q if g is None else g.symmetric_difference(q)
        if g is not None and g.area > 10:
            out.append((g, f))
    return out
LG = letter_geoms()
circ = [(g, f) for g, f in LG if g.bounds[2] - g.bounds[0] > 650]
lets = [(g, f) for g, f in LG if (g, f) not in circ]
def box3(x0, x1, y0, y1, z0, z1):
    return [(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]
def bar(p0, p1, w=30):                      # strypas tarp p0 ir p1 (x, y, z) - kvadratinis w
    import numpy as np
    a, b = np.array(p0, float), np.array(p1, float); d = b - a; d /= np.linalg.norm(d)
    u = np.cross(d, [1, 0, 0]); u /= np.linalg.norm(u); v = np.cross(d, u)
    h = w / 2
    return [tuple(q + su * h * u + sv * h * v) for q in (a, b) for su in (-1, 1) for sv in (-1, 1)]
FACES = [(0, 1, 3, 2), (4, 5, 7, 6), (0, 1, 5, 4), (2, 3, 7, 6), (0, 2, 6, 4), (1, 3, 7, 5)]
def draw_cuboid(P, col):
    import numpy as np
    cen = np.mean(np.array(P, float), axis=0)
    fs = []
    for fc in FACES:
        q = [np.array(P[i], float) for i in fc]
        n = np.cross(q[1] - q[0], q[3] - q[0]); n /= (np.linalg.norm(n) or 1)
        if np.dot(n, np.mean(q, axis=0) - cen) < 0:
            n = -n
        if V3.rot(*n)[2] <= 0:
            continue
        fs.append((sum(V3.rot(*v)[2] for v in q) / 4, [tuple(v) for v in q], n))
    for _, q, n in sorted(fs, key=lambda t: t[0]):
        cc = V3.shade(col, n); V3.fpoly(q, cc, HexColor("#777777"), 0.15)
ISO = (K.IX0 + 640, K.IY0 + 395, 330, 180)
pts3 = box3(0, 4012, 0, 850, -760, 100)
V3.fit(pts3, ISO)
items = []
for (x, ht, g), (xk, hk, _) in zip(LEGS, KICK):
    zb = -93 if g == "X" else -60
    items.append((zb - 400, box3(x - 15, x + 15, TP, ht, zb, zb + 30), LEGC))
    items.append((zb - 500, bar((xk, hk, zb + 15), (xk, TP + 25, zb + 15 - D_BACK)), KICKC))
    for zc in (zb + 15, zb + 15 - D_BACK):
        items.append((zc - 600, box3(x - 60 if zc == zb + 15 else xk - 60, x + 60 if zc == zb + 15 else xk + 60, 0, TP, zc - 60, zc + 60), PLC))
for x0, x1, yt in RAILS:
    items.append((-30, box3(x0, x1, yr(yt + 30), yr(yt), -30, 0), RAILC))
for x0, x1, yt in ZSTR:
    items.append((-60, box3(x0, x1, yr(yt + 30), yr(yt), -63, -33), RAILC))
DR = []
for _, P, col in items:
    DR.append((sum(V3.rot(*p)[2] for p in P) / len(P), "c", P, col))
for g, f in circ:                             # vaizdas iš galo: matoma nugara (z mažesnė)
    DR.append((V3.depth_key(g, -31), "s", (g, -30, -33), Color(*f), Color(*f)))
for g, f in lets:
    _ret = HexColor("#C1121C") if f[0] > 0.7 and f[1] < 0.3 else HexColor("#F7B500")
    DR.append((V3.depth_key(g, 50), "s", (g, 100, 0), _ret, HexColor("#C9C9C9")))
for _, kind, P, col, *bk in sorted(DR, key=lambda t: t[0]):
    if kind == "c":
        draw_cuboid(P, col)
    else:
        V3.solid(P[0], P[1], P[2], col, bk[0])
view_title(ISO[0] + ISO[2] / 2, ISO[1] + ISO[3] + 14, "3D VIEW - FROM BEHIND", "ILLUSTRATIVE - NOT TO SCALE")

# ================================================================ apatinė juosta
BY0 = K.BAND_Y; BH = K.IY1 - BY0
W_P6, W_MD, W_TB = 214, 172, 272
X_P6 = K.IX0; X_TB = K.IX1 - W_TB; X_MD = X_TB - W_MD; X_BOM = X_P6 + W_P6; W_BOM = X_MD - X_BOM
K.header(X_P6, BY0, W_P6, "WIND LOAD (EN 1991-1-4) - ASSUMED")
rect(X_P6, BY0 + 12, W_P6, BH - 12, lw=0.6)
rows = [("qp(z)", f"{QP:.2f} kN/m² (vb,0 26, terrain II, z 5 m)"), ("cf", "1.8 (signboard, 7.4.3)"),
        ("F X/EXTRA/7-23", " / ".join(f"{WIND[k]['F']:.2f}" for k in ("X", "EXTRA", "7-23")) + " kN"),
        ("Kicker N max", f"{NMAX:.2f} kN (ULS {NMAX * GQ:.2f} kN)"),
        ("Foot uplift max", f"{VMAX:.2f} kN (ULS {VMAX * GQ:.2f} kN)"),
        ("Kicker □30x30x2", f"Ncr ≈ {math.pi ** 2 * 70000 * 29419 / 941 ** 2 / 1000:.0f} kN >> N - OK"),
        ("Without kickers", "moment base on roof - NOT advised"),
        ("Ballast option", "≈ 50 / 160 / 75 kg (7-23/EXTRA/X)"),
        ("CHECK", "site wind zone + roof structure")]
K.main_data(X_P6, BY0, W_P6, BH, [list(r) for r in rows], title="WIND LOAD (EN 1991-1-4) - ASSUMED", lab_w=70)
bom = [[1, "Roof leg □30x30x2", "Alu EN AW-6060 T66", "RAL 7035", "6 pcs.: 2x691, 671, 337, 2x322"],
       [2, "Back support (kicker) □30x30x2", "Alu EN AW-6060 T66", "RAL 7035", "6 pcs.: 2x≈940, 2x≈925, 2x≈880"],
       [3, "Base plate 120x120x5, 4x Ø9", "Alu", "RAL 7035", "12 pcs. (6 legs + 6 kicker feet)"],
       [4, "Fork lug 5 mm (kicker ends)", "Alu, welded", "RAL 7035", "12 pcs."],
       [5, "Bracket L40x40x4, l = 60", "Alu", "RAL 7035", "15 pcs."],
       [6, "Bolt M8 + nut + washers", "A2-70", "-", "≈ 30 pcs."],
       [7, "Bolt M6 into U flange + nut", "A2-70", "-", "≈ 32 pcs."],
       [8, "EPDM pad 120x120x3", "EPDM", "-", "12 pcs."],
       [9, "Roof fixing (to roof structure)", "?", "-", "?"],
       [10, "Flashing / sealing of fixings", "?", "-", "?"]]
K.bom_table(X_BOM, BY0, W_BOM, BH, bom, title="BILL OF MATERIALS - ROOF MOUNT  (per 1 sign)")
md = [["Sign", "FAS 700H80 (7-23), sheet 2"], ["Mount", "Roof, detachable (bolted)"],
      ["Legs", "6 pcs. □30x30x2, RAL 7035"], ["Back support", "6 kickers ~45°, foot 650 back"],
      ["Circle -> roof", "150 (client)"], ["Leg -> sign", "bracket + M6/M8, A2"],
      ["X circle", "legs to Z strips on sheet"], ["Base", "plate 120x120x5 + EPDM"],
      ["Roof type", "?"], ["Wall option", "ears + wallframe (sh. 2)"]]
K.main_data(X_MD, BY0, W_MD, BH, md, lab_w=58)
spec = {"client": "BrandFactory", "title": "EXTRA order 225978 - FAS 700H80 ROOF MOUNT, recommendation",
        "order_no": "ALT0000_00.00_RS", "drawing_no": "EXTRA order 225978", "sheet": "3 / 5", "rev": "A",
        "date": "2026-10-08"}
K.title_block(X_TB, W_TB, spec, "1:25 / 1:10 / 1:5")
K.save(OUT)
os.path.exists(tmp) and os.remove(tmp)
print("OK", OUT, "netelpa:", K.OVERFLOW)
