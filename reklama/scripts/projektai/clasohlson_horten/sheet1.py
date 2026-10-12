"""Lapas 1/2 - bendras brėžinys: FRONT (developed), PLAN su kampais, DETAIL A/B/C, 3D, BOM, MAIN DATA."""
import math, sys
from common import *
import data as D

OUT = sys.argv[1]
begin(14)
VB = K.VIEW_BOT

# ================================================================ FRONT VIEW (DEVELOPED) 1:50
s = MM / 50
FW = D.L_TOTAL * s
X0 = K.IX0 + (K.IX1 - K.IX0 - FW) / 2 + 14
YT = 96                                   # plokštės viršus
YB = YT + D.PH * s
fx = lambda xm: X0 + xm * s
fy = lambda ym: YT + ym * s

K.set_view(True)
rect(X0, YT, FW, D.PH * s, fill=NCS, lw=0.5)
for j in D.JOINTS:
    fold = j in D.FOLDS
    if fold:
        line(fx(j), YT - 6, fx(j), YB + 6, 0.3, black, dash=([6, 1.5, 1.5, 1.5], 0))
    else:
        line(fx(j), YT, fx(j), YB, 0.3, HexColor("#3E6E86"), dash=([2, 1.5], 0))
tf = lambda x, y: (fx(x), K.Y(fy(y)))
for L in D.LETTERS:
    draw_sub(L["sub"], tf, fill=BLK, stroke=None)
K.set_view(False)
# dalių numeriai
for p in D.PARTS:
    T(fx(p["x0"]) + 4, YB - 4, f"P{p['no']}", 8, font="FB", color=HexColor("#1D334A"))
for fi, f in enumerate(D.FOLDS):
    T(fx(f), YB + 14, f"FOLD {fi + 1}", 8, font="FB", align="c")
# grandinės viršuje: bendras, plokštumos, dalys
hdim(X0, X0 + FW, YT - 48, f"{D.L_TOTAL}", YT, YT, size=12)
xs = [0, D.FOLDS[0], D.FOLDS[1], D.L_TOTAL]
hchain(YT - 32, [fx(v) for v in xs], [YT] * 4, [f"{b - a}" for a, b in zip(xs, xs[1:])], size=12)
xs = [0] + D.JOINTS + [D.L_TOTAL]
hchain(YT - 16, [fx(v) for v in xs], [YT] * len(xs), [f"{round(b - a)}" for a, b in zip(xs, xs[1:])], size=8)
T(X0 + FW + 6, YT - 13, "PARTS", 8, color=K.GREY)
T(X0 + FW + 6, YT - 29, "PLANES", 8, color=K.GREY)
# apačioje - logotipo padėtis
lb = D.LOGO_BB
xs = [0, lb[0], lb[2], D.L_TOTAL]
hchain(YB + 30, [fx(v) for v in xs], [YB, fy(lb[3]), fy(lb[3]), YB],
       [f"{round(b - a)}" for a, b in zip(xs, xs[1:])], size=12)
T(fx(D.GRILLE_C), YB + 44, f"logo centred on grille axis ({D.GRILLE_C:.0f})", 8, color=K.GREY, align="c")
# kairėje vertikalės
vchain(X0 - 14, [YT, fy(lb[1]), fy(lb[3]), YB], [X0, fx(lb[0]), fx(lb[0]), X0],
       [f"{round(b - a)}" for a, b in zip([0, lb[1], lb[3]], [lb[1], lb[3], D.PH])], size=8)
vchain(X0 - 34, [YT, YB], [X0, X0], [f"{D.PH}"], size=12)
leader(fx(15000), fy(450), fx(15000) + 18, YB + 16, 5)
leader(fx(lb[0] + 90), fy(420), fx(lb[0]) - 30, YB + 14, 1)
view_title(X0 + FW / 2, YB + 64, "FRONT VIEW (DEVELOPED)", "SCALE 1:50  |  folded plate unfolded along facade")

# ================================================================ PLAN VIEW 1:50
a1, a2 = map(math.radians, D.ALPHA)
dirs = [(math.cos(a1), -math.sin(a1)), (1.0, 0.0), (math.cos(a2), math.sin(a2))]
P = [(0.0, 0.0)]
for (dx, dz), l in zip(dirs, D.PLANES):
    P.append((P[-1][0] + dx * l, P[-1][1] + dz * l))
zs = [p[1] for p in P]; xsP = [p[0] for p in P]
PX0 = K.IX0 + (K.IX1 - K.IX0 - (max(xsP) - min(xsP)) * s) / 2 - 40
PYB = 364                                     # z = 0 linija (gatvės pusė apačioje)
px = lambda x: PX0 + x * s
pz = lambda z: PYB + (z - max(zs)) * s + 0
nrm = [(-dz, dx) for dx, dz in dirs]          # į gatvę


def off_line(o):
    pts = []
    for i, p in enumerate(P):
        if i == 0:
            n = nrm[0]; pts.append((p[0] + n[0] * o, p[1] + n[1] * o))
        elif i == len(P) - 1:
            n = nrm[-1]; pts.append((p[0] + n[0] * o, p[1] + n[1] * o))
        else:
            n1, n2 = nrm[i - 1], nrm[i]; m = (n1[0] + n2[0], n1[1] + n2[1]); k = o / (1 + n1[0] * n2[0] + n1[1] * n2[1])
            pts.append((p[0] + m[0] * k, p[1] + m[1] * k))
    return pts


back, front = off_line(0), off_line(D.PD)
K.set_view(True)
poly([(px(x), pz(z)) for x, z in back + front[::-1]], fill=NCS, lw=0.5)
K.set_view(False)
# dalių sandūros plane
for p in D.PARTS[1:]:
    xm = p["x0"]; acc = 0
    for pi, l in enumerate(D.PLANES):
        if xm <= acc + l + 0.5:
            t = xm - acc; break
        acc += l
    b0 = (P[pi][0] + dirs[pi][0] * t, P[pi][1] + dirs[pi][1] * t)
    n = nrm[pi] if t > 0.5 else (nrm[pi - 1][0] + nrm[pi][0], nrm[pi - 1][1] + nrm[pi][1])
    if t <= 0.5:
        k = D.PD / (1 + nrm[pi - 1][0] * nrm[pi][0] + nrm[pi - 1][1] * nrm[pi][1]); n = (n[0] * k / D.PD, n[1] * k / D.PD)
    line(px(b0[0]), pz(b0[1]), px(b0[0] + n[0] * D.PD), pz(b0[1] + n[1] * D.PD), 0.3)
# dalių žymos (gatvės pusėje)
for p in D.PARTS:
    xm = p["x0"] + p["len"] / 2; acc = 0
    for pi, l in enumerate(D.PLANES):
        if xm <= acc + l:
            t = xm - acc; break
        acc += l
    q = (P[pi][0] + dirs[pi][0] * t + nrm[pi][0] * 260, P[pi][1] + dirs[pi][1] * t + nrm[pi][1] * 260)
    T(px(q[0]), pz(q[1]) + 3, f"P{p['no']}", 8, font="FB", align="c", color=HexColor("#1D334A"))
# aligned matmenys už plokštės (sienos pusėje)
for i in range(3):
    a, b = P[i], P[i + 1]; n = nrm[i]; o = -230
    A = (px(a[0] + n[0] * o), pz(a[1] + n[1] * o)); B = (px(b[0] + n[0] * o), pz(b[1] + n[1] * o))
    line(px(a[0]) , pz(a[1]), A[0], A[1], 0.25, K.EXT); line(px(b[0]), pz(b[1]), B[0], B[1], 0.25, K.EXT)
    line(*A, *B, 0.3)
    ang = math.degrees(math.atan2(-(B[1] - A[1]), B[0] - A[0]))
    K.arrowhead(A[0], A[1], ang + 180); K.arrowhead(B[0], B[1], ang)
    mx, my = (A[0] + B[0]) / 2, (A[1] + B[1]) / 2
    T(mx - 4 * math.sin(math.radians(ang)), my - 3 * math.cos(math.radians(ang)), f"{D.PLANES[i]}", 12, align="c", rot=ang)
# kampai prie lūžių
for fi in range(2):
    c0 = P[fi + 1]; d_in, d_out = dirs[fi], dirs[fi + 1]
    R = 900
    ext = (c0[0] + d_in[0] * R * 1.25, c0[1] + d_in[1] * R * 1.25)
    line(px(c0[0]), pz(c0[1]), px(ext[0]), pz(ext[1]), 0.2, K.GREY, dash=([4, 1, 1, 1], 0))
    th0 = math.atan2(d_in[1], d_in[0]); th1 = math.atan2(d_out[1], d_out[0])
    pts = [(px(c0[0] + R * math.cos(th0 + (th1 - th0) * k / 20)), pz(c0[1] + R * math.sin(th0 + (th1 - th0) * k / 20))) for k in range(21)]
    poly(pts, close=False, lw=0.3)
    tm = (th0 + th1) / 2
    lx = px(c0[0]) + (-62 if fi == 0 else 62); ly = pz(c0[1]) + 26
    T(lx, ly, f"≈{D.ALPHA[fi]:g}°", 9, align="c")
    T(lx, ly + 11, "(sketch, not measured)", 8, color=K.GREY, align="c")
# raidės plane: P8 (spaceris 20 + raidė 23) priešais P4 priekį
for L in D.LETTERS:
    x0_, x1_ = L["bb"][0] - D.PLANES[0], L["bb"][2] - D.PLANES[0]
    y_a, y_b = pz(P[1][1] + D.PD + 20), pz(P[1][1] + D.PD + 43)
    rect(px(P[1][0] + x0_), y_a, (x1_ - x0_) * s, max(0.8, y_b - y_a), fill=BLK, stroke=None)
    lx_ = px(P[1][0] + (x0_ + x1_) / 2)
    line(lx_, y_a - 0.3, lx_, y_a - 0.3, 0.1)
leader(px(P[1][0] + D.LETTERS[0]["bb"][0] - D.PLANES[0] + 150), pz(P[1][1] + D.PD + 32), px(P[1][0] + 1200), pz(P[1][1]) + 26, 1)
T(px(P[0][0]) - 6, pz(P[0][1]) + 12, "STREET SIDE", 8, color=K.GREY, align="r")
leader(px(P[2][0] - 1500), pz(P[2][1] + 20), px(P[2][0] - 1500) - 6, pz(P[2][1]) + 22, 5)
view_title(K.IX0 + 120, PYB - 18, "PLAN VIEW (TOP)", "SCALE 1:50  |  wall not shown")
wy = pz(max(zs)) - 52
# ---------------------------------------------------------------- REAR VIEW P4 (MIRRORED) 1:50 + laidas
P4 = D.LOGO_PART
RX1, RY0 = K.IX1 - 26, 402
rx = lambda xg: RX1 - (xg - P4["x0"]) * s          # veidrodinis: kairė -> dešinėje
ry = lambda yg: RY0 + yg * s
K.set_view(True)
rect(rx(P4["x0"] + P4["len"]), RY0, P4["len"] * s, D.PH * s, fill=HexColor("#EEF2F4"), lw=0.5)
for yy in (2, D.PH - 32):
    rect(rx(P4["x0"] + P4["len"] - 25), ry(yy), (P4["len"] - 50) * s, 30 * s, fill=HexColor("#B4B4B4"), lw=0.3)
for L in D.LETTERS:
    K.draw_shape(L["sub"], lambda x, y: (rx(x), K.Y(ry(y))), stroke=K.GREY, lw=0.1, dash=([2, 1.5], 0))
K.set_view(False)
dx_, dy_ = D.D11
hx = rx(dx_)
circle(hx, ry(dy_), 1.6, fill=K.CABLE, stroke=None)
xb1 = rx(P4["x0"] + P4["len"]) - 14                         # trafo box kairiau nuo galinio vaizdo
ex = rx(P4["x0"])                                           # P3 KAIRĖS šoninė briauna (veidrodiniame - dešinėje)
K.cable_line([(hx, ry(dy_)), (ex + 8, ry(dy_)), (ex + 8, RY0 - 20), (xb1, RY0 - 20)])
circle(ex, ry(dy_), 1.8, stroke=K.CABLE, lw=0.6)
vchain(ex + 18, [RY0, ry(dy_)], [ex, ex], [f"{dy_:.0f}"], size=8)
rect(xb1 - 64, RY0 - 32, 64, 24, fill=HexColor(K.ralhex("7044")), lw=0.5)
T(xb1 - 32, RY0 - 22, "TRAFO BOX", 8, font="FB", align="c")
T(xb1 - 32, RY0 - 13, "RAL 7044", 8, align="c")
T((xb1 + ex) / 2, RY0 - 24, "12V, 5.0 m, white cable", 8, color=K.CABLE, align="c", auto_red=False)
K.cable_line([(xb1 - 64, RY0 - 20), (xb1 - 80, RY0 - 20)]); T(xb1 - 82, RY0 - 17, "230V", 8, color=K.CABLE, align="r", auto_red=False)
hchain(ry(D.PH) + 14, [rx(P4["x0"] + P4["len"]), rx(dx_), rx(P4["x0"])], [ry(D.PH)] * 3,
       [f"{P4['x0'] + P4['len'] - dx_:.0f}", f"{dx_ - P4['x0']:.0f}"], size=8)
T(hx - 4, ry(dy_) + 12, "D11", 8, color=K.CABLE, align="r", auto_red=False)
view_title(rx(P4["x0"] + P4["len"] / 2), ry(D.PH) + 36, f"REAR VIEW P{P4['no']} (MIRRORED)", "SCALE 1:50  |  Ø11 in left side edge, letters dashed")


# ================================================================ DETAIL A - SECTION 1:2 (lūžęs)
ya = detail_a(K.IX0 + 128, 440, 90)
view_title(K.IX0 + 128 + 20 * MM / 2, ya + 20, "DETAIL A - SECTION", "SCALE 1:2  |  top edge + letter, broken view")

# ================================================================ DETAIL B - PANEL JOINT (plan section) 1:2
t = D.T_S
sB = MM / 2
bx0, by0 = K.IX0 + 395, 452                  # sandūros ašis x, sienos plokštuma y (plano pjūvis: gatvė apačioje)
XB = lambda u: bx0 + u * sB
YB_ = lambda d: by0 + d * sB                 # d - nuo sienos į gatvę
K.set_view(True)
for sg in (-1, 1):
    x_in = XB(sg * (D.GAP / 2 + 0.05))
    # priekis
    xa, xb = (XB(-60), XB(-0.05 - 0.0)) if sg < 0 else (XB(0.05), XB(60))
    rect(min(xa, xb), YB_(D.PD - t), abs(xb - xa), t * sB, fill=black, lw=0.35)
    # šoninis flanšas
    xf = XB(sg * 0.05) if sg > 0 else XB(-0.05 - t)
    rect(xf, YB_(0), t * sB, (D.PD - t) * sB, fill=black, lw=0.35)
K.set_view(False)
yb_ = YB_(18)
for sg in (-1, 1):
    poly([(XB(sg * 60), YB_(D.PD) + 4), (XB(sg * 60) - 3, YB_(D.PD - t) - 2), (XB(sg * 60) + 3, YB_(D.PD - t) - 6), (XB(sg * 60), YB_(D.PD - t) - 10)], close=False, lw=0.3)
vchain(XB(60) + 16, [YB_(0), YB_(D.PD)], [XB(0.05 + t), XB(60)], ["40"], size=8)
leader(XB(-30), YB_(D.PD - 1), XB(-40), YB_(D.PD) + 14, 5)
T(XB(0), YB_(0) - 6, "separate parts - no joint bolts", 8, color=K.GREY, align="c")
T(XB(0), YB_(D.PD) + 30, "P2|P3, P3|P4, P5|P6: flat joint", 8, color=K.GREY, align="c")
view_title(XB(0), YB_(D.PD) + 52, "DETAIL B - PANEL JOINT", "SCALE 1:2  |  plan section")

# ================================================================ DETAIL C - FOLD JOINT 1:5 (90° flanšai)
sC = MM / 5
cx0, cy0 = K.IX0 + 572, 520                  # priekių susitikimo taškas
al = math.radians(D.ALPHA[0])
K.set_view(True)
for sg in (-1, 1):
    ux, uz = (-math.cos(al), -math.sin(al)) if sg < 0 else (1.0, 0.0)
    nx, nz = (uz, -ux) if sg < 0 else (-uz, ux)      # į sieną
    Lp = 200
    pts = [(0, 0), (ux * Lp, uz * Lp), (ux * Lp + nx * t, uz * Lp + nz * t), (nx * t, nz * t)]
    poly([(cx0 + x * sC, cy0 - z * sC) for x, z in pts], fill=black, lw=0.35)
    fl = [(0, 0), (nx * D.PD, nz * D.PD), (nx * D.PD + ux * t, nz * D.PD + uz * t), (ux * t, uz * t)]
    poly([(cx0 + x * sC, cy0 - z * sC) for x, z in fl], fill=black, lw=0.35)
    ex, ez = nx * D.PD * 0.6 + ux * 14, nz * D.PD * 0.6 + uz * 14
    T(cx0 + ex * sC + (-6 if sg < 0 else 6), cy0 - ez * sC + 3, "90°", 8, align="r" if sg < 0 else "l")
K.set_view(False)
T(cx0 + 14, cy0 + 14, "all end flanges 90°", 8)
T(cx0 + 14, cy0 + 25, "(facade angles not given)", 8, color=K.GREY)
T(cx0 + 14, cy0 + 36, "parts meet at front edge", 8, color=K.GREY)
T(cx0 - 66, cy0 + 36, "P1", 8, font="FB"); T(cx0 + 96, cy0 - 6, "P2", 8, font="FB")
view_title(cx0, cy0 + 56, "DETAIL C - FOLD (P1|P2, P4|P5)", "SCALE 1:5  |  plan section, angle from sketch")

# ================================================================ 3D VIEW (r3d - teisingas užstojimas)
import r3d
from shapely.affinity import scale as sscale, translate as stranslate
S3 = r3d.Scene(yaw=24, pitch=24, tile=400)
for p in D.PARTS:
    acc = 0
    for pi, l in enumerate(D.PLANES):
        if p["x0"] < acc + l - 0.5:
            break
        acc += l
    t0 = p["x0"] - acc
    (x0_, z0_), (dx_, dz_), (nx_, nz_) = P[pi], dirs[pi], nrm[pi]
    o = (x0_ + dx_ * (t0 + 2), 0, z0_ + dz_ * (t0 + 2))
    S3.box(o, (dx_ * (p["len"] - 4), 0, dz_ * (p["len"] - 4)), (0, D.PH, 0), (nx_ * D.PD, 0, nz_ * D.PD), NCS, HexColor("#5D8EA6"))
xf_ = lambda x, y, z: (P[1][0] + x - D.PLANES[0], y, P[1][1] + D.PD + z)
for L in D.LETTERS:
    g = sscale(L["geom"], 1, -1, origin=(0, 0)); g = stranslate(g, 0, D.PH)
    S3.extrude_xy(g, 20, 43, HexColor("#F2F2F2"), BLK, xf=xf_)
x3, y3w, w3, h3 = K.IX0 + 700, 508, K.IX1 - K.IX0 - 705, VB - 508 - 24
S3.render((x3, y3w, w3, h3))
view_title(x3 + w3 / 2, y3w + h3 + 14, "3D VIEW", "ILLUSTRATIVE - NOT TO SCALE")


# ================================================================ juosta
p8_section = p8_band


Lsum = sum(p["len"] - 50 for p in D.PARTS)
l_list = " + ".join(f"2 x {(p['len'] - 50) / 1000:.2f}" for p in D.PARTS)
scr = [round((p["len"] - 100) / 300) + 1 for p in D.PARTS]
N_SCR = 2 * sum(scr)
flatA = sum(D.flat_size(p["len"])[0] * D.flat_size(p["len"])[1] for p in D.PARTS) / 1e6
w_plate = flatA * 2 * 2.70
w_face = D.A_FACE * 3 * 2.70; w_plexi = D.A_FACE * 20 * 1.19
w_L = 2 * Lsum / 1000 * 116e-6 * 2700
W = w_plate + w_face + w_plexi + w_L
bom = [
    ["1", "Letter face P8 special", "Alu 3 mm", "RAL 9005", f"{D.PER:.2f} m / {D.A_FACE:.2f} m²"],
    ["2", "Letter body P8, milled shell", "Plexi 20 mm white", "-", f"{D.PER:.2f} m / {D.A_FACE:.2f} m²"],
    ["3", "LED Baltled Crown Mini 0.3 W", "-", "6500K", "?"],
    ["4", "Spacer Ø16x20 on Ø4 holes (CO std.)", "Aluminium", "-", f"{D.N_SP} pcs."],
    ["5", "Folded plate P1-P6, 40 deep", "Alu 2 mm folded", "NCS S 0540-B", f"6 pcs. / {flatA:.2f} m² flat"],
    ["6", "L profile 30x30x2 (top + bottom)", "Aluminium", "-", f"{2 * Lsum / 1000:.2f} m (12 pcs.)"],
    ["7", "Wall fixing", "?", "?", "?"],
    ["8", "Letter fixing through plate", "?", "-", f"{D.N_SP} pcs."],
    ["9", "Screw plate -> L, DIN 7504 N 4.2x16", "Steel, hard.", "-", f"{N_SCR} pcs."],
    ["10", "Cable 12V, white (D11 -> Ø11 side edge)", "-", "white", "5.0 m"],
    ["11", "Trafo box 12V", "?", "RAL 7044", "1 pcs."],
]
md = [
    ["Quantity", "1 pcs."],
    ["Overall size", f"{D.L_TOTAL} x {D.PH} (developed)"],
    ["Folds", "90° flanges (angles not given)"],
    ["Parts", "6 separate pcs., max 3900"],
    ["Plate", "Alu 2 mm, depth 40, R2"],
    ["Plate finish", "NCS S 0540-B semi matte"],
    ["Letters", "P8 special 3 + 20, spacers 20"],
    ["Letter finish", "RAL 9005 semi matt"],
    ["Illumination", "Baltled Crown Mini 0.3 W 6500K"],
    ["Letter holes", f"Ø4 x{D.N_SP}, slot 6.1x3.7 x{D.N_SLOT}, Ø8 x{D.N_D8}"],
    ["Mounting", "L30x30x2 top + bottom / part"],
    ["Fixing holes", "Ø3.2, 7 from edge, 50 / ~300"],
    ["Cable", "12V 5 m white, left side -> 7044"],
    ["Weight (calc.)", f"≈ {W:.0f} kg / pcs, excl. PSU"],
]
band("P8 SPECIAL - SECTION A-A (1:2)", p8_section, bom, md, "Clas Ohlson Horten 3 - folded plate 16839 x 900, P8", "1 / 3", "1:50 / 1:2")
K.save(OUT)
print("weight", round(W, 1), "screws", N_SCR, "L", 2 * Lsum, "overflow", K.OVERFLOW)
