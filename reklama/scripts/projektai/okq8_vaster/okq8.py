"""OKQ8 Väster S (Skyltkoncept 2524677, 2026-10-09): folded plokštė (mėlyna RAL ?) + ORACAL 551 101 balta pjaustyta grafika.
Pozicijos: 1600 x 1200 (3 vnt.), 3200 x 2400 iš 2 dalių 1600 + 1600 (6 vnt., plėvelė per sandūros kraštą)."""
import sys, math
sys.path.insert(0, "/tmp/claude-0/-home-claude/454aabe4-a26e-51a4-90bd-3f68e4f6d938/scratchpad/co")
import common as C
from common import *
import data as D                                          # _subs, flat, lenkimo konstantos
import r3d
import pymupdf as fitz
from shapely.geometry import Polygon, box as sbox
from shapely.ops import unary_union
from shapely.affinity import scale as sscale, translate as stranslate

C.PROJECT = "OKQ8 Vaster S 2524677"
C.CLIENT = "Skyltkoncept Sweden AB"
SRC = "/root/.claude/uploads/454aabe4-a26e-51a4-90bd-3f68e4f6d938/3c39d704-261009_OKQ8_V_STER_S.pdf"
K.FOIL["551 101"] = "#FFFFFF"
BLUE = HexColor(K.ralhex("5002"))                          # RAL 5002 (Rytis 2026-10-09)
PD, t = 40, 2.0
POS = [
    {"W": 1600, "H": 1200, "qty": 3, "rect": (90.6, 68.4, 381.4, 286.6), "parts": [1600], "sheet": "1 / 2", "sc": 15},
    {"W": 3200, "H": 2400, "qty": 6, "rect": (90.6, 369.6, 541.9, 708.3), "parts": [3200], "split_h": True, "sheet": "2 / 2", "sc": 25},
]
pg = fitz.open(SRC)[0]
DRW = pg.get_drawings()


def graphics(pos):
    r = fitz.Rect(pos["rect"]); k = pos["W"] / r.width
    out = []
    for d in DRW:
        if d.get("fill") != (1.0, 1.0, 1.0) or not r.contains(d["rect"]):
            continue
        sub = [[(s_[0],) + tuple(((q[0] - r.x0) * k, (q[1] - r.y0) * k) for q in s_[1:]) for s_ in sp] for sp in D._subs(d)]
        polys = [Polygon(D.flat(sp)).buffer(0) for sp in sub if len(D.flat(sp)) > 2]
        g = polys[0]
        for p_ in polys[1:]:
            g = g.symmetric_difference(p_)
        out.append({"sub": sub, "geom": g})
    return out


def detail_top(ax0, ay0, joint=False):
    """DETAIL A - SECTION 1:2: viršutinė užlenkta briauna, L 30x30x2, Ø3.2 7 nuo krašto, plėvelė ant priekio"""
    sc = MM / 2
    X = lambda d: ax0 + d * sc
    Yd = lambda h: ay0 + h * sc
    HW = 90
    K.set_view(True)
    rect(X(PD - t), Yd(0), t * sc, HW * sc, fill=black, lw=0.35)
    rect(X(0), Yd(0), (PD - t) * sc, t * sc, fill=black, lw=0.35)
    poly([(X(0), Yd(t + 0.4)), (X(30), Yd(t + 0.4)), (X(30), Yd(t + 2.4)), (X(2), Yd(t + 2.4)), (X(2), Yd(t + 30.4)),
          (X(0), Yd(t + 30.4))], fill=HexColor("#B4B4B4"), lw=0.35)
    K.set_view(False)
    rect(X(PD) + 0.2, Yd(18), 1.4, (HW - 18) * sc, fill=white, stroke=black, lw=0.3)        # plėvelė (perdidinta)
    bx = X(7)
    rect(bx - 4.5, Yd(0) - 3.2, 9, 3.2, fill=HexColor("#3A3A3A"), lw=0.3)
    rect(bx - 1.3, Yd(0), 2.6, (t + 2.4 + 8) * sc, fill=HexColor("#6E6E6E"), lw=0.25)
    K.centerline(bx, Yd(0) - 8, bx, Yd(t + 14))
    wy = Yd(t + 20)
    rect(X(-16), wy - 2, (16 + 2 + 4) * sc, 4, fill=HexColor("#6E6E6E"), lw=0.25)
    rect(X(2), wy - 5, 3.5, 10, fill=HexColor("#3A3A3A"), lw=0.3)
    K.centerline(X(-20), wy, X(10), wy)
    zig(X(PD - 10), X(PD + 10), Yd(HW))
    hchain(Yd(0) - 26, [X(0), X(PD)], [Yd(0), Yd(0)], ["40"], size=8)
    hdim(X(0), X(7), Yd(0) - 42, "7", Yd(0), Yd(0), size=8, small_side="l")
    T(X(7) + 8, Yd(0) - 39.5, "Ø3.2 hole", 8)
    L_ = X(-16) - 22; R_ = X(PD) + 40
    leader(X(PD - 1), Yd(70), R_, Yd(78), 1)
    leader(X(PD) + 1, Yd(40), R_, Yd(46), 2)
    leader(X(1), Yd(t + 26), L_, Yd(t + 34), 3)
    leader(bx, Yd(0) - 3, L_, Yd(0) - 14, 4)
    leader(X(-12), wy, L_, Yd(t + 52), 5)
    return Yd(HW)


def gap_joint(G, H):
    """horizontali sandūra - didžiausio tarpo tarp grafikos grupių (virš teksto) viduryje, suapvalinta iki 5"""
    import math as _m
    iv = sorted((g["geom"].bounds[1], g["geom"].bounds[3]) for g in G if not g["geom"].is_empty)
    m = []
    for a, b in iv:
        if m and a <= m[-1][1] + 1:
            m[-1][1] = max(m[-1][1], b)
        else:
            m.append([a, b])
    gaps = [(b2[0] - b1[1], (b1[1] + b2[0]) / 2, b1[1], b2[0]) for b1, b2 in zip(m, m[1:])]
    g = max(gaps)
    return round(g[1] / 5) * 5, g[2], g[3]


def detail_joint_h(cx, cy):
    """DETAIL B - JOINT (vertical section) 1:2: viršutinės dalies apatinė ir apatinės dalies viršutinė briaunos, varžtas"""
    sc = MM / 2
    X = lambda d: cx + d * sc                      # d - nuo sienos
    Yj = lambda h: cy + h * sc                     # h - žemyn nuo sandūros (+ apačia)
    K.set_view(True)
    rect(X(PD - t), Yj(-70), t * sc, 70 * sc - 0.15, fill=black, lw=0.35)          # viršutinės dalies priekis
    rect(X(0), Yj(-0.05 - t), (PD - t) * sc, t * sc, fill=black, lw=0.35)          # jos apatinė briauna
    rect(X(PD - t), Yj(0.05), t * sc, 70 * sc, fill=black, lw=0.35)                 # apatinės dalies priekis
    rect(X(0), Yj(0.05), (PD - t) * sc, t * sc, fill=black, lw=0.35)               # jos viršutinė briauna
    K.set_view(False)
    bx = X(20)
    rect(bx - 4, Yj(-t - 2) - 3.5, 8, 3.5, fill=HexColor("#3A3A3A"), lw=0.3)
    rect(bx - 1.6, Yj(-t - 2), 3.2, (2 * t + 4) * sc, fill=HexColor("#6E6E6E"), lw=0.25)
    rect(bx - 4, Yj(t + 2), 8, 3.5, fill=HexColor("#3A3A3A"), lw=0.3)
    K.centerline(bx, Yj(-t - 12), bx, Yj(t + 12))
    rect(X(PD) + 0.2, Yj(-60), 1.4, 46 * sc, fill=white, lw=0.3)                       # plėvelė (grafika) virš sandūros
    rect(X(PD) + 0.2, Yj(18), 1.4, 46 * sc, fill=white, lw=0.3)                        # plėvelė (tekstas) po sandūra
    zig(X(PD - 10), X(PD + 10), Yj(-70)); zig(X(PD - 10), X(PD + 10), Yj(70))
    hchain(Yj(-70) - 14, [X(0), X(20), X(PD)], [Yj(-t)] * 3, ["20", "20"], size=8)
    leader(X(PD - 1), Yj(-40), X(PD) + 40, Yj(-48), 1)
    leader(X(PD) + 1, Yj(30), X(PD) + 40, Yj(40), 2)
    leader(bx, Yj(t + 4), bx - 30, Yj(30), 6)
    T(X(PD) + 6, Yj(0) + 3, "joint in graphic gap", 8)
    T(X(PD) + 6, Yj(0) + 14, "Ø6 holes, ~500", 8)
    T(X(0) - 4, Yj(0) + 3, "wall", 8, color=K.GREY, align="r")


def flat_dxf(fn, W, H, holes_top, holes_bot, bolts_top, bolts_bot):
    import ezdxf
    BA = math.pi / 2 * (2 + 0.44 * t); OSSB = 2 + t; BD = 2 * OSSB - BA
    a = PD - OSSB + BA / 2; off = a + BA / 2 - OSSB
    F, WF = W + 2 * PD - 2 * BD, H + 2 * PD - 2 * BD
    SY0, SY1 = off + t + 0.1, off + H - t - 0.1
    doc = ezdxf.new("R2010", setup=True); doc.units = ezdxf.units.MM; msp = doc.modelspace()
    for nm, col, lt in (("CUT", 7, "CONTINUOUS"), ("BEND_UP_90_R2", 1, "DASHDOT"), ("HOLES_D3.2", 3, "CONTINUOUS"),
                        ("HOLES_D6_JOINT", 4, "CONTINUOUS"), ("TEXT", 2, "CONTINUOUS")):
        doc.layers.add(nm, color=col, linetype=lt)
    o = off
    msp.add_lwpolyline([(o, 0), (F - o, 0), (F - o, SY0), (F, SY0), (F, SY1), (F - o, SY1), (F - o, WF), (o, WF),
                        (o, SY1), (0, SY1), (0, SY0), (o, SY0)], close=True, dxfattribs={"layer": "CUT"})
    for u in (a, F - a):
        msp.add_line((u, SY0), (u, SY1), dxfattribs={"layer": "BEND_UP_90_R2"})
    for v in (a, WF - a):
        msp.add_line((off, v), (F - off, v), dxfattribs={"layer": "BEND_UP_90_R2"})
    span = W - 100; n = max(1, round(span / 300))
    xs = [off + 50 + span * k / n for k in range(n + 1)]
    for flag, v in ((holes_top, WF - 7), (holes_bot, 7)):
        if flag:
            for x in xs:
                msp.add_circle((x, v), 1.6, dxfattribs={"layer": "HOLES_D3.2"})
    nj = max(1, round(span / 500)); xj = [off + 50 + span * k / nj for k in range(nj + 1)]
    for flag, v in ((bolts_top, WF - 20), (bolts_bot, 20)):
        if flag:
            for x in xj:
                msp.add_circle((x, v), 3.0, dxfattribs={"layer": "HOLES_D6_JOINT"})
    msp.add_text(f"FOLDED PLATE {W:.0f} x {H:.0f} x {PD} - Al 2 mm - FLAT {F:.1f} x {WF:.1f} - FACE OUT", height=30,
                 dxfattribs={"layer": "TEXT"}).set_placement((F / 2, WF / 2), align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)
    msp.add_text(f"R2 K0.44 BD {BD:.2f} | 4 x 90 up | D3.2 7 from edge, L holes 50 | {n} x {span / n:.1f} | 50; joint D6 20 from edge ~500",
                 height=20, dxfattribs={"layer": "TEXT"}).set_placement((0, -40))
    doc.saveas(fn)
    return F, WF


def build(pos, out):
    W, H = pos["W"], pos["H"]
    G = graphics(pos)
    hp = [H]
    if pos.get("split_h"):
        yj, ga, gb_ = gap_joint(G, H)
        hp = [yj, H - yj]
        pos["gap"] = (ga, gb_)
    pos["hp"] = hp
    joint = len(hp) > 1
    begin(12)
    s = MM / pos["sc"]
    X0, YT = K.IX0 + 76, 66
    fx = lambda x: X0 + x * s; fy = lambda y: YT + y * s
    YB_ = fy(H)
    # ---------------------------------------------------------------- FRONT VIEW
    K.set_view(True)
    rect(X0, YT, W * s, H * s, fill=BLUE, lw=0.5)
    for g in G:
        draw_sub(g["sub"], lambda x, y: (fx(x), K.Y(fy(y))), fill=white, stroke=None)
    K.set_view(False)
    hdim(X0, fx(W), YT - 18, f"{W}", YT, YT, size=12)
    vchain(X0 - 38, [YT, YB_], [X0, X0], [f"{H}"], size=12)
    if joint:
        yj = hp[0]
        line(X0, fy(yj), fx(W), fy(yj), 0.4, HexColor("#BFC6E6"), dash=([3, 2], 0))
        vchain(X0 - 16, [YT, fy(yj), YB_], [X0, X0, X0], [f"{hp[0]}", f"{hp[1]}"], size=12)
        ga, gb_ = pos["gap"]
        vchain(fx(W) + 14, [fy(ga), fy(yj), fy(gb_)], [fx(W * 0.62)] * 3, [f"{yj - ga:.0f}", f"{gb_ - yj:.0f}"], size=8)
        T(X0 + W * s / 2, YB_ + 16, "PANEL JOINT - centred in the gap between car and text", 8, align="c")
    leader(fx(W * 0.06), fy(H * 0.92), X0 - 16, YB_ + 14, 1)
    gx = max(G, key=lambda g: g["geom"].area)
    rp = gx["geom"].representative_point()
    leader(fx(rp.x), fy(rp.y), fx(W) + 16, fy(H * 0.2), 2)
    view_title(X0 + W * s / 2, YB_ + (34 if joint else 30), "FRONT VIEW", f"SCALE 1:{pos['sc']}")
    # ---------------------------------------------------------------- SIDE VIEW
    SX = fx(W) + 60
    K.set_view(True)
    acc = 0
    for h in hp:
        rect(SX, fy(acc), PD * s, h * s, fill=BLUE, lw=0.4); acc += h
    K.set_view(False)
    hdim(SX, SX + PD * s, YT - 18, "40", YT, YT, size=8, small_side="r")
    circle(SX + PD * s / 2, YT + 4, 8, lw=0.4); T(SX - 6, YT - 2, "A", 9, font="FB", align="r")
    if joint:
        circle(SX + PD * s / 2, fy(hp[0]), 8, lw=0.4); T(SX - 6, fy(hp[0]) - 6, "B", 9, font="FB", align="r")
    view_title(SX + PD * s / 2, YB_ + 30, "SIDE VIEW", f"SCALE 1:{pos['sc']}")
    # ---------------------------------------------------------------- REAR VIEW (MIRRORED)
    RX = SX + PD * s + 100
    rx = lambda x: RX + (W - x) * s
    ry = lambda y: YT + y * s
    K.set_view(True)
    rect(RX, YT, W * s, H * s, fill=HexColor("#EEF2F4"), lw=0.5)
    for yy in (2, H - 32):                                           # L tik viršuje ir apačioje (etalonas: back plate iš 2 dalių)
        rect(rx(W - 25), ry(yy), (W - 50) * s, 30 * s, fill=HexColor("#B4B4B4"), lw=0.3)
    if joint:
        line(RX, ry(hp[0]), RX + W * s, ry(hp[0]), 0.5)
    K.set_view(False)
    span = W - 100; n = max(1, round(span / 300))
    for yy in (7, H - 7):
        for k_ in range(n + 1):
            circle(rx(50 + span * k_ / n), ry(yy), 0.9, lw=0.3)
    nj = max(1, round(span / 500)); pj = span / nj          # sandūra: Ø6, ~500 pagal apkrovas (Rytis 2026-10-09)
    if joint:
        for k_ in range(nj + 1):
            circle(rx(50 + pj * k_), ry(hp[0]), 1.4, fill=HexColor("#3A3A3A"), stroke=None)
        hchain(ry(hp[0]) + 14, [rx(W), rx(W - 50), rx(50), rx(0)], [ry(hp[0])] * 4, ["50", f"{nj} x {pj:.0f} = {span}", "50"], size=8)
    n_scr = 2 * (n + 1)
    hchain(YT - 14, [rx(W), rx(W - 50), rx(50), rx(0)], [YT] * 4, ["50", f"{n} x {span / n:.0f} = {span}", "50"], size=8)
    hchain(YB_ + 16, [rx(W), rx(W - 25), rx(25), rx(0)], [YB_] * 4, ["25", f"{W - 50} (L30x30x2)", "25"], size=8)
    leader(rx(W * 0.8), ry(H - 17), RX + W * s + 22, ry(H - 120), 3)
    leader(rx(W - 50), ry(7), rx(W - 50) - 18, YT - 30, 4)
    if joint:
        leader(rx(50 + pj), ry(hp[0]), RX + W * s + 22, ry(hp[0]) - 30, 6)
        T(RX + W * s / 2, ry(hp[0]) - 6, f"joint: {nj + 1} x Ø6, ~500 (by load)", 8, align="c")
    view_title(RX + W * s / 2, YB_ + 40, "REAR VIEW (MIRRORED)", f"SCALE 1:{pos['sc']}  |  Ø3.2, 7 from edge")
    # ---------------------------------------------------------------- DETAILS + 3D
    DY = max(YB_ + 96, 410)
    ya = detail_top(K.IX0 + 110, DY)
    view_title(K.IX0 + 110 + 20 * MM / 2, ya + 20, "DETAIL A - SECTION", "SCALE 1:2  |  top edge")
    x3 = K.IX0 + 300
    if joint:
        detail_joint_h(K.IX0 + 360, DY + 70)
        view_title(K.IX0 + 380, DY + 70 + 70 * MM / 2 + 22, "DETAIL B - PANEL JOINT", "SCALE 1:2  |  vertical section")
        x3 = K.IX0 + 540
    S3 = r3d.Scene()
    acc = 0
    for h in hp:                                       # y aukštyn: apatinė dalis apačioje
        S3.box((0, H - acc - h + 1, 0), (W, 0, 0), (0, h - 2, 0), (0, 0, PD), BLUE, HexColor("#1E2E78"))
        acc += h
    for g in G:
        gg = sscale(g["geom"], 1, -1, origin=(0, 0)); gg = stranslate(gg, 0, H)
        for part in getattr(gg, "geoms", [gg]):
            ext = [(x, y, PD + 0.5) for x, y in list(part.exterior.coords)[:-1]]
            hol = [[(x, y, PD + 0.5) for x, y in list(r_.coords)[:-1]] for r_ in part.interiors]
            S3.face(ext, (0, 0, 1), white, None, holes=hol, tile=False, amb=0.9)
    y3 = DY - 10; h3 = K.VIEW_BOT - y3 - 24
    S3.render((x3, y3, K.IX1 - x3 - 10, h3))
    view_title(x3 + (K.IX1 - x3 - 10) / 2, y3 + h3 + 6, "3D VIEW", "ILLUSTRATIVE - NOT TO SCALE")
    # ---------------------------------------------------------------- juosta
    def section(x, y, w, h):
        sc = MM / 2
        xf, yt = x + 70, y + 26
        K.set_view(True)
        rect(xf, yt, t * sc, 70 * sc, fill=black, lw=0.35)
        rect(xf - (PD - t) * sc, yt, (PD - t) * sc, t * sc, fill=black, lw=0.35)
        K.set_view(False)
        rect(xf + t * sc + 0.2, yt + 10, 1.4, 70 * sc - 10, fill=white, lw=0.3)
        zig(xf - 8, xf + 12, yt + 70 * sc)
        leader(xf + t * sc + 1, yt + 70, xf + 60, yt + 74, 2)
        leader(xf + 1, yt + 40, xf + 60, yt + 42, 1)
        hchain(yt - 10, [xf - (PD - t) * sc, xf + t * sc], [yt, yt], ["40"], size=8)
        T(x + w / 2, y + h - 16, "Alu 2 mm folded, RAL 5002", 8, color=K.GREY, align="c", auto_red=False)
        T(x + w / 2, y + h - 5, "+ ORACAL 551 101 white, cut vinyl", 8, color=K.GREY, align="c", auto_red=False)
    flats = [(D.flat_size(W)[0], h + 2 * PD - 2 * D.BD) for h in hp]
    A_flat = sum(a_ * b_ for a_, b_ in flats) / 1e6
    A_vin = sum(g["geom"].area for g in G if not g["geom"].is_empty) / 1e6
    L_tot = 2 * (W - 50) / 1000
    Wt = A_flat * 2 * 2.70 + L_tot * 116e-6 * 2700
    n_bolt = (nj + 1) if joint else 0
    bom = [["1", (f"Folded plate {W} x {hp[0]} (top) +\n{W} x {hp[1]} (bottom), 40 deep" if joint else f"Folded plate {W} x {H}, 40 deep"),
            "Alu 2 mm folded", "RAL 5002", ("1 + 1 pcs. / flats\n" if joint else "1 pcs. / flat ") + " + ".join(f"{a_:.0f} x {b_:.0f}" for a_, b_ in flats)],
           ["2", "Graphic - cut vinyl (car, showers, text)", "ORACAL 551 101", "551 101", f"{A_vin:.2f} m²"],
           ["3", "L profile 30x30x2 (top + bottom)", "Aluminium", "-", f"2 x {(W - 50) / 1000:.2f} = {L_tot:.2f} m"],
           ["4", "Screw plate -> L, DIN 7504 N 4.2x16", "Steel, hard.", "-", f"{n_scr} pcs. ({n + 1}/L)"],
           ["5", "Wall fixing", "?", "?", "?"]]
    if joint:
        bom.append(["6", "Bolt + nut, joint, Ø6 holes ~500", "?", "-", f"{n_bolt} pcs."])
    md = [["Quantity", f"{pos['qty']} pcs."], ["Overall size", f"{W} x {H}"],
          ["Parts", (f"{hp[0]} (top) + {hp[1]} (bottom)" if joint else "1")],
          ["Plate", "Alu 2 mm, depth 40, R2, 90°"], ["Plate finish", "RAL 5002"],
          ["Graphic", "ORACAL 551 101 white"], ["Fixing holes", "Ø3.2, 7 from edge, 50 / ~300"],
          ["Mounting", "L30x30x2 top + bottom"], ["Illumination", "none"],
          ["Joint", f"in graphic gap, {n_bolt} x Ø6 ~500" if joint else "-"], ["Inside", "unpainted"],
          ["Weight (calc.)", f"≈ {Wt:.0f} kg / pcs"]]
    band("FOLDED PLATE + VINYL - SECTION (1:2)", section, bom, md,
         f"OKQ8 Vaster S - folded plate {W} x {H}, vinyl ({pos['qty']} pcs.)", pos["sheet"], f"1:{pos['sc']} / 1:2")
    K.save(out)
    print(W, H, "parts", hp, "flats", [(round(a_, 1), round(b_, 1)) for a_, b_ in flats], "vinyl", round(A_vin, 2), "screws", n_scr,
          "bolts", n_bolt, "W", round(Wt, 1), "overflow", K.OVERFLOW)
    return G


if __name__ == "__main__":
    GG = [build(p, f"s{i + 1}.pdf") for i, p in enumerate(POS)]
