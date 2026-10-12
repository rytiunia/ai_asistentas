"""Lapas 2/3 - Horten 3: 3D vizualizacijos ant fasado (fasado geometrija - prielaidos)."""
import math, sys
from common import *
import data as D
from shapely.affinity import scale as sscale, translate as stranslate

OUT = sys.argv[1]
begin(9)
VB = K.VIEW_BOT

FH = 1300                     # viršutinės sienos aukštis - PRIELAIDA
H_LOW, H_GRILLE, H_GLASS = 3000, 3400, 3000
a1, a2 = map(math.radians, D.ALPHA)
dirs = [(math.cos(a1), -math.sin(a1)), (1.0, 0.0), (math.cos(a2), math.sin(a2))]
P = [(0.0, 0.0)]
for (dx, dz), l in zip(dirs, D.PLANES):
    P.append((P[-1][0] + dx * l, P[-1][1] + dz * l))
nrm = [(-dz, dx) for dx, dz in dirs]
YC = H_LOW + FH / 2
PY0, PY1 = YC - D.PH / 2, YC + D.PH / 2

C = {"glass": HexColor("#9FC0D2"), "frame": HexColor("#3A4148"), "wall": HexColor("#E3DED4"), "old": HexColor("#C9C5BD"),
     "grille": HexColor("#5A6168"), "fascia": HexColor("#D9D5CC"), "skirt": HexColor("#4B5259"),
     "bulk": HexColor("#F2F2F0"), "tile1": HexColor("#E9E6E0"), "tile2": HexColor("#DEDAD2"), "pier": HexColor("#CFCAC0"),
     "column": HexColor("#F0EFEC"), "planter": HexColor("#5B5F63"), "green": HexColor("#6F9E62"), "bench": HexColor("#A07A52")}


def W(pi, t, y, o):
    (x0, z0), (dx, dz), (nx, nz) = P[pi], dirs[pi], nrm[pi]
    return (x0 + dx * t + nx * o, y, z0 + dz * t + nz * o)


def panel(pi, t0, t1, y0, y1, o, col, stroke=None):
    return [([W(pi, t0, y0, o), W(pi, t1, y0, o), W(pi, t1, y1, o), W(pi, t0, y1, o)], (nrm[pi][0], 0, nrm[pi][1]), col, stroke)]


def box(pi, t0, t1, y0, y1, o0, o1, col, stroke=None):
    nx, nz = nrm[pi]; dx, dz = dirs[pi]
    f = panel(pi, t0, t1, y0, y1, o1, col, stroke)
    top = [([W(pi, t0, y1, o0), W(pi, t1, y1, o0), W(pi, t1, y1, o1), W(pi, t0, y1, o1)], (0, 1, 0), col, stroke)]
    bot = [([W(pi, t0, y0, o0), W(pi, t1, y0, o0), W(pi, t1, y0, o1), W(pi, t0, y0, o1)], (0, -1, 0), col, stroke)]
    sl = [([W(pi, t0, y0, o0), W(pi, t0, y0, o1), W(pi, t0, y1, o1), W(pi, t0, y1, o0)], (-dx, 0, -dz), col, stroke)]
    sr = [([W(pi, t1, y0, o0), W(pi, t1, y0, o1), W(pi, t1, y1, o1), W(pi, t1, y1, o0)], (dx, 0, dz), col, stroke)]
    return f + top + bot + sl + sr


def scene():
    Q = []
    # kairė plokštuma 3684 (žiūrint iš priekio): esama siena 1030 kraštinėje + esamas stiklas 2654
    Q += panel(0, 0, 1030, 0, H_LOW, 0, C["old"], HexColor("#A9A59D"))
    for k in range(2):
        Q += panel(0, 1030 + k * 1327, 1030 + (k + 1) * 1327, 0, H_GLASS, 0, C["glass"], C["frame"])
    # 2 plokštuma: grotelės 6758 (viršus už sienos)
    Q += panel(1, 0, 6758, 0, H_LOW, 0, C["grille"], C["frame"])
    # dešinė plokštuma 6397: nauja siena 3647 prie grotelių + esamas stiklas 2750 kraštinėje
    Q += panel(2, 0, 3647, 0, H_LOW, 0, C["wall"], HexColor("#B9B3A8"))
    for k in range(2):
        Q += panel(2, 3647 + k * 1375, 3647 + (k + 1) * 1375, 0, H_GLASS, 0, C["glass"], C["frame"])
    # viršutinė siena + skirtas + prekybos centro karnizas
    for pi, l in enumerate(D.PLANES):
        Q += panel(pi, 0, l, H_LOW, H_LOW + FH, 0, C["fascia"], HexColor("#B9B3A8"))
        Q += panel(pi, 0, l, H_LOW - 30, H_LOW + 10, 1, C["skirt"])
        Q += panel(pi, 0, l, H_LOW + FH, H_LOW + FH + 700, 0, C["bulk"], HexColor("#CFCFCF"))
    # folded dalys
    for p in D.PARTS:
        acc = 0
        for pi, l in enumerate(D.PLANES):
            if p["x0"] < acc + l - 0.5:
                break
            acc += l
        t0 = p["x0"] - acc
        Q += box(pi, t0 + 1, t0 + p["len"] - 1, PY0, PY1, 0, D.PD, NCS, HexColor("#5D8EA6"))
    return Q


def environment(S):
    """prekybos centro vidus: grindų plytelės, kaimyninės parduotuvės, karnizas, kolonos, vazonai, suolai"""
    x0e, x1e, zb, zf = -9000, 25500, -2200, 9200
    T_ = 1500
    zs = [zb + i * T_ for i in range(int((zf - zb) / T_) + 1)]
    xs = [x0e + i * T_ for i in range(int((x1e - x0e) / T_) + 1)]
    for ii, (za, zb_) in enumerate(zip(zs, zs[1:])):
        for jj, (xa, xb) in enumerate(zip(xs, xs[1:])):
            col = C["tile1"] if (ii + jj) % 2 else C["tile2"]
            S.face([(xa, 0, zb_), (xb, 0, zb_), (xb, 0, za), (xa, 0, za)], (0, 1, 0), col, HexColor("#CFCAC1"), 0.1)
    # kaimyninės parduotuvės: kairėje (z = 0) ir dešinėje (z = P3)
    def shop(xa, xb, z, sign_col):
        S.face([(xa, 0, z), (xa + 600, 0, z), (xa + 600, H_LOW + FH, z), (xa, H_LOW + FH, z)], (0, 0, 1), C["pier"], HexColor("#B9B3A8"))
        n = max(1, round((xb - xa - 600) / 1500))
        w = (xb - xa - 600) / n
        for k in range(n):
            a, b = xa + 600 + k * w, xa + 600 + (k + 1) * w
            S.face([(a, 0, z), (b, 0, z), (b, H_LOW, z), (a, H_LOW, z)], (0, 0, 1), C["glass"], C["frame"], 0.25)
        S.face([(xa + 600, H_LOW, z), (xb, H_LOW, z), (xb, H_LOW + FH, z), (xa + 600, H_LOW + FH, z)], (0, 0, 1), C["fascia"], HexColor("#B9B3A8"))
        cx = (xa + 600 + xb) / 2
        S.box((cx - 1600, H_LOW + FH / 2 - 300, z), (3200, 0, 0), (0, 600, 0), (0, 0, 60), sign_col, HexColor("#9A9A9A"))
        S.face([(xa, H_LOW + FH, z), (xb, H_LOW + FH, z), (xb, H_LOW + FH + 700, z), (xa, H_LOW + FH + 700, z)], (0, 0, 1), C["bulk"], HexColor("#CFCFCF"))
    shop(-8400, 0, 0.0, HexColor("#E8E4DA"))
    shop(P[3][0], P[3][0] + 8400, P[3][1], HexColor("#DDE3E8"))
    # kaimyninių sienų galai (gylis) - tik matomi kraštai
    # kolonos
    for cx, cz in ((-2600, 7600), (20000, 7600)):
        S.box((cx - 350, 0, cz - 350), (700, 0, 0), (0, H_LOW + FH + 900, 0), (0, 0, 700), C["column"], HexColor("#BDBDBD"))
    # vazonai su augalais ir suolai
    for cx, cz in ((4200, 5200), (12600, 5200)):
        S.box((cx - 900, 0, cz - 300), (1800, 0, 0), (0, 550, 0), (0, 0, 600), C["planter"], HexColor("#6E6E6E"))
        S.box((cx - 850, 550, cz - 250), (1700, 0, 0), (0, 280, 0), (0, 0, 500), C["green"], HexColor("#4E7A45"))
    for cx, cz in ((8400, 6400),):
        S.box((cx - 1000, 380, cz - 220), (2000, 0, 0), (0, 70, 0), (0, 0, 440), C["bench"], HexColor("#7A5A3C"))
        for dx in (-800, 700):
            S.box((cx + dx, 0, cz - 180), (100, 0, 0), (0, 380, 0), (0, 0, 360), C["column"], HexColor("#9A9A9A"))


import r3d


def render(box_, yaw, pitch, title, sub):
    S = r3d.Scene(yaw=yaw, pitch=pitch)
    environment(S)
    for pts3, n, col, st in scene():
        S.face(pts3, n, col, edge=st, edge_lw=0.2)
    for k_ in range(1, int(6758 / 120)):                              # grotelių strypai
        S.face([W(1, k_ * 120 - 10, 40, 4), W(1, k_ * 120 + 10, 40, 4), W(1, k_ * 120 + 10, H_LOW - 40, 4),
                W(1, k_ * 120 - 10, H_LOW - 40, 4)], (0, 0, 1), HexColor("#7C848B"))
    xf = lambda x, y, z: (P[1][0] + x, y, P[1][1] + D.PD + z)
    for L in D.LETTERS:
        g = sscale(L["geom"], 1, -1, origin=(0, 0)); g = stranslate(g, -D.PLANES[0], PY1)
        S.extrude_xy(g, 20, 43, HexColor("#F4F4F4"), BLK, xf=xf)
    S.render(box_)
    x, y, w, h = box_
    view_title(x + w / 2, y + h + 16, title, sub)


bx = K.IX0 + 10; bw = K.IX1 - K.IX0 - 20
render((bx, 40, bw, 260), 3, 13, "3D VIEW - SHOPPING CENTRE (FRONT)", "ILLUSTRATIVE - NOT TO SCALE  |  mall interior and facade geometry ASSUMED")
hw = (bw - 30) / 2
render((bx, 360, hw, 220), -30, 14, "3D VIEW - FROM LEFT", "ILLUSTRATIVE - NOT TO SCALE")
render((bx + hw + 30, 360, hw, 220), 32, 14, "3D VIEW - FROM RIGHT", "ILLUSTRATIVE - NOT TO SCALE")


def legend(x, y, w, h):
    items = [("Folded plate P1-P6, Alu 2 mm", PLATE_HEX, "NCS S 0540-B semi matte"),
             ("Letters P8 special, face Al 3 mm", "#0E0E10", "RAL 9005 semi matt, plexi sides lit"),
             ("Upper facade wall (existing)", "#D9D5CC", "colour / height ASSUMED")]
    yy = y + 10
    for lab, col, txt in items:
        rect(x + 10, yy, 34, 24, fill=HexColor(col), lw=0.4)
        T(x + 52, yy + 10, lab, 8, font="FB", fit=w - 58, fit_min=8)
        T(x + 52, yy + 21, txt, 8, color=K.GREY, fit=w - 58, fit_min=8)
        yy += 34


bom = [["", "Position: Clas Ohlson Horten 3 (sheet 1)", "", "", "1 pcs."],
       ["5", "Folded plate P1-P6, 40 deep, 90° bends", "Alu 2 mm folded", "NCS S 0540-B", "6 pcs."],
       ["1", "Letters P8 special (logo 3381 x 720)", "Al 3 + plexi 20", "RAL 9005", "12 pcs."],
       ["3", "LED Baltled Crown Mini 0.3 W", "-", "6500K", "?"],
       ["", "Facade - reference only", "", "", ""]]
md = [["Facade planes", "3684 / 6758 / 6397 (from left)"], ["Facade angles", "≈8° / ≈18.5° (sketch only)"],
      ["Glass height", "≈3000 ASSUMED"], ["Grille", "6758 x 3400"], ["Skirt height", "3000"],
      ["Upper wall", f"≈{FH} ASSUMED, mall interior"], ["Plate position", "centred on upper wall"],
      ["Logo", "centred on grille axis"], ["View", "illustrative only"]]
band("MATERIALS / COLOURS", legend, bom, md, "Clas Ohlson Horten 3 - 3D views on facade", "2 / 3", "-")
K.save(OUT)
print("overflow", K.OVERFLOW)
