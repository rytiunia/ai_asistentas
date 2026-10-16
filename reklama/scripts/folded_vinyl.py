#!/usr/bin/env python3
"""Folded plate + pjaustyta plėvelė (lipdukai) - BENDRAS generatorius (v283, Rytis 2026-10-15, Joker order 226057 eskelokk).

Anksčiau buvo tik projektų skriptai (OKQ8 Väster S `projektai/okq8_vaster/okq8.py`, SPAR 226004 backplate). Taisyklės -
`references/moduliai_folded.md` („Folded plate - bendrinės taisyklės", „Kelios dalys vienoje plokštumoje",
„Folded plate + pjaustyta plėvelė"), plėvelės sunaudojimas - `plevele.py`, ISO matmenys - taisyklė 30.

Vienas lapas kiekvienai plokštei (spec "panels"): FRONT (plokštė RAL + kliento vektorinė grafika plėvelių spalvomis,
grafikos padėties matmenys), SIDE, REAR (MIRRORED) (L 30x30x2 viršuje ir apačioje, Ø3.2 7 nuo krašto 50 / ~300,
sandūra Ø6 ~500), DETAIL A (viršutinė briauna + L + plėvelė 1:2), DETAIL B (sandūra, jei yra), 3D; juostoje - pjūvis,
BOM (plėvelė - kodas MATERIAL langelyje su spalva, kiekis - sunaudojimas), MAIN DATA, antraštė.
Plokštė didesnė už lakštą (išklotinė > lakštas - paraštės) -> horizontali sandūra DIDŽIAUSIO grafikos tarpo viduryje
(abi dalys telpa lakšte), L tik viso skydo viršuje / apačioje, sandūroje Ø6 ~500 + varžtai / veržlės.
Išvestis: PDF (visi lapai) + `<out>_flat_<panel>_<part>.dxf` išklotinės (FACE OUT, v173 praktika) + plėvelių ploterio DXF.

Naudojimas: python3 folded_vinyl.py spec.json out.pdf
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lapas_core as K  # noqa: E402
import kreives as KR  # noqa: E402  v312: kreivės lankais
import plevele as PL  # noqa: E402
import r3d  # noqa: E402
import pymupdf as fitz  # noqa: E402
from lapas_core import T, line, rect, poly, circle, hdim, vchain, hchain, leader, view_title, MM  # noqa: E402
from reportlab.lib.colors import HexColor, white, black  # noqa: E402
from shapely.geometry import Polygon  # noqa: E402
from shapely.ops import unary_union  # noqa: E402
from shapely.affinity import scale as sscale, translate as stranslate  # noqa: E402

L_SZ = 30.0                                     # L 30x30x2 (moduliai_folded.md)
STD = (10, 15, 20, 25, 30, 40, 50)
GREY_L = HexColor("#B4B4B4")


# ------------------------------------------------------------------ kliento grafika
def _match(f_, col, tol=0.03):
    return f_ is not None and max(abs(a - b) for a, b in zip(f_[:3], col)) <= tol


def load_panel(S, P):
    """plokštės grafika iš kliento PDF: [(vinyl dict, sub (mm, y žemyn nuo viršaus), geom)] - PDF tvarka (sluoksniai)"""
    pg = fitz.open(S["client_pdf"])[S.get("page", 0)]
    r = fitz.Rect(P["rect"])
    k = P["w"] / r.width
    tomm = lambda q: ((q[0] - r.x0) * k, (q[1] - r.y0) * k)
    out = []
    for d in pg.get_drawings():
        f_ = d.get("fill")
        if f_ is None or not r.contains(d["rect"]) or _match(f_, S["bg_fill"], 0.05):
            continue
        v = next((v for v in S["vinyl"] if any(_match(f_, c_) for c_ in v["fills"])), None)
        if v is None:
            print(f"  ! {P['name']}: nežinoma grafikos spalva {tuple(round(x, 3) for x in f_[:3])} - spec 'vinyl' papildyti")
            continue
        sub = K.drawing_to_subpaths(d, tomm)
        g = K.shape_geom(sub).buffer(0)
        if not g.is_empty:
            out.append((v, sub, g))
    return out


def objects_of(G):
    """grafikos grupės (logotipas, tekstas ...) - persidengiančių / artimų elementų sąjungos"""
    gs = [g for _, _, g in G]
    U = unary_union([g.buffer(40) for g in gs])        # užrašo simboliai / logotipo sluoksniai - vienas objektas
    parts = [unary_union([g for g in gs if g.intersects(p)]) for p in getattr(U, "geoms", [U])]
    # vienos eilutės objektai (užrašo žodžiai / skliaustai) - vienas objektas: aukščiai persidengia >= 50 %
    merged = True
    while merged:
        merged = False
        for i in range(len(parts)):
            for j in range(i + 1, len(parts)):
                a, b = parts[i].bounds, parts[j].bounds
                ov = min(a[3], b[3]) - max(a[1], b[1])
                if ov >= 0.5 * min(a[3] - a[1], b[3] - b[1]):
                    parts[i] = unary_union([parts[i], parts[j]]); del parts[j]; merged = True; break
            if merged:
                break
    return parts


def split_rows(P, G, depth, t, sheets):
    """v283: plokštė netelpa lakšte -> horizontali sandūra grafikos tarpe (abi dalys telpa).
    v284 (Rytis 2026-10-15: „didelė skarda: viršutinės dalies išklotinė turi tilpti į 3000x1500 lapą"): lakštai renkami nuo
    MAŽIAUSIO (`sheets_mm`, numatyta 3000x1500, 4000x2000); sandūra - tarpo viduryje, bet ne aukščiau / žemiau, nei leidžia
    mažesnis lakštas (>= 50 nuo grafikos), apvalinta 5 (žemyn)."""
    FL = depth - t
    W, H = P["w"], P["h"]
    if P.get("joints_y") is not None:
        ys = [0] + list(P["joints_y"]) + [H]
        return [b - a for a, b in zip(ys, ys[1:])]
    sheets = sorted([tuple(q) for q in sheets], key=lambda q: q[0] * q[1])

    def hmax(sh):                                      # didžiausias dalies aukštis lakšte (plotis W telpa?)
        mx, mn = max(sh) - 20, min(sh) - 20
        fw = W + 2 * FL
        if fw <= mn:
            return mx - 2 * FL
        if fw <= mx:
            return mn - 2 * FL
        return -1
    for sh in sheets:
        if H <= hmax(sh):
            return [H]
    iv = sorted((g.bounds[1], g.bounds[3]) for g in objects_of(G))
    m = []
    for a, b in iv:
        if m and a <= m[-1][1] + 1:
            m[-1][1] = max(m[-1][1], b)
        else:
            m.append([a, b])
    gaps = ([(0.0, m[0][0])] if m and m[0][0] > 0 else []) + [(b1[1], b2[0]) for b1, b2 in zip(m, m[1:])] + \
           ([(m[-1][1], H)] if m else [(0.0, H)])
    for sh in sheets:                                  # mažiausias lakštas, kuriame telpa abi dalys
        hm = hmax(sh)
        if hm <= 0:
            continue
        best = None
        for g0, g1 in gaps:
            lo, hi = max(g0 + 50, H - hm), min(g1 - 50, hm)
            if lo > hi:
                continue
            y = min(max((g0 + g1) / 2, lo), hi)
            y = math.floor(y / 5) * 5
            if y < lo:
                y += 5
            if lo <= y <= hi and (best is None or g1 - g0 > best[0]):
                best = (g1 - g0, y)
        if best:
            print(f"  {P['name']}: sandūra y{best[1]:g} - abi dalys telpa lakšte {sh[0]}x{sh[1]}")
            return [best[1], H - best[1]]
    print(f"  ! {P['name']}: sandūros grafikos tarpe, kad abi dalys tilptų lakšte, nerasta - PATIKRINTI ranka")
    return [round(H / 2 / 5) * 5, H - round(H / 2 / 5) * 5]


# ------------------------------------------------------------------ smulkūs piešiniai
def zig(xa, xb, yy):
    xm = (xa + xb) / 2
    poly([(xa, yy), (xm - 2, yy), (xm, yy - 3), (xm + 1, yy + 3), (xm + 3, yy), (xb, yy)], close=False, lw=0.3)


def detail_a(x0, y0, depth, t, vin_hex, title):
    """DETAIL A - SECTION 1:2: viršutinė užlenkta briauna, L 30x30x2, Ø3.2 7 nuo krašto, plėvelė ant priekio"""
    sc = MM / 2
    X = lambda d: x0 + d * sc
    Yd = lambda h: y0 + h * sc
    HW = 90
    K.set_view(True)
    rect(X(depth - t), Yd(0), t * sc, HW * sc, fill=black, lw=0.35)
    rect(X(0), Yd(0), (depth - t) * sc, t * sc, fill=black, lw=0.35)
    poly([(X(0), Yd(t + 0.4)), (X(L_SZ), Yd(t + 0.4)), (X(L_SZ), Yd(t + 2.4)), (X(2), Yd(t + 2.4)), (X(2), Yd(t + L_SZ + 0.4)),
          (X(0), Yd(t + L_SZ + 0.4))], fill=GREY_L, lw=0.35)
    rect(X(depth) + 0.2, Yd(18), 1.4, (HW - 18) * sc, fill=HexColor(vin_hex), stroke=black, lw=0.4)   # plėvelė (perdidinta)
    bx = X(7)
    rect(bx - 4.5, Yd(0) - 3.2, 9, 3.2, fill=HexColor("#3A3A3A"), lw=0.4)
    rect(bx - 1.3, Yd(0), 2.6, (t + 2.4 + 8) * sc, fill=HexColor("#6E6E6E"), lw=0.4)
    K.centerline(bx, Yd(0) - 8, bx, Yd(t + 14))
    wy = Yd(t + 20)
    rect(X(-16), wy - 2, (16 + 2 + 4) * sc, 4, fill=HexColor("#6E6E6E"), lw=0.4)
    rect(X(2), wy - 5, 3.5, 10, fill=HexColor("#3A3A3A"), lw=0.4)
    K.centerline(X(-20), wy, X(10), wy)
    zig(X(depth - 10), X(depth + 10), Yd(HW))
    K.set_view(False)                                   # v283: detalės geometrija - hairline (kaip vaizduose)
    hdim(X(0), X(depth), Yd(0) - 30, f"{depth:g}", Yd(0) - 4, Yd(0), size=8)
    hdim(X(0), X(7), Yd(0) - 16, "7", Yd(0) - 4, Yd(0) - 4, size=8, small_side="l")
    T(X(depth) + 10, Yd(0) - 13, "Ø3.2", 8)
    L_, R_ = X(-16) - 24, X(depth) + 40
    leader(X(depth - 1), Yd(70), R_, Yd(78), 1)
    leader(X(depth) + 1, Yd(40), R_, Yd(52), 2)
    leader(bx, Yd(0) - 3, L_, Yd(0) - 10, 4)
    leader(X(-12), wy, L_, Yd(t + 26), 5)
    leader(X(1), Yd(t + 28), L_, Yd(t + 60), 3)
    view_title(X(depth / 2), Yd(HW) + 22, title, "SCALE 1:2  |  top edge (bottom - mirrored)")
    return Yd(HW) + 40


def detail_b(cx, cy, depth, t, hexa, hexb):
    """DETAIL B - PANEL JOINT 1:2: viršutinės dalies apatinė ir apatinės dalies viršutinė briaunos, varžtas Ø6"""
    sc = MM / 2
    X = lambda d: cx + d * sc
    Yj = lambda h: cy + h * sc
    K.set_view(True)
    HB = 42
    rect(X(depth - t), Yj(-HB), t * sc, HB * sc - 0.15, fill=black, lw=0.35)
    rect(X(0), Yj(-0.05 - t), (depth - t) * sc, t * sc, fill=black, lw=0.35)
    rect(X(depth - t), Yj(0.05), t * sc, HB * sc, fill=black, lw=0.35)
    rect(X(0), Yj(0.05), (depth - t) * sc, t * sc, fill=black, lw=0.35)
    bx = X(20)
    rect(bx - 4, Yj(-t - 2) - 3.5, 8, 3.5, fill=HexColor("#3A3A3A"), lw=0.4)
    rect(bx - 1.6, Yj(-t - 2), 3.2, (2 * t + 4) * sc, fill=HexColor("#6E6E6E"), lw=0.4)
    rect(bx - 4, Yj(t + 2), 8, 3.5, fill=HexColor("#3A3A3A"), lw=0.4)
    K.centerline(bx, Yj(-t - 12), bx, Yj(t + 12))
    zig(X(depth - 10), X(depth + 10), Yj(-HB)); zig(X(depth - 10), X(depth + 10), Yj(HB))
    K.set_view(False)
    hchain(Yj(-HB) - 14, [X(0), X(20), X(depth)], [Yj(-t) - 6, Yj(-t - 12) - 1, Yj(-HB) - 4],
           ["20", f"{depth - 20:g}"], size=8)                # v283: iškeltinės - ne ant ašinės / plokštės krašto
    leader(X(depth - 1), Yj(-30), X(depth) + 34, Yj(-34), 1)
    leader(bx + 4, Yj(t + 4), X(-14), Yj(30), 6)
    T(X(depth) + 8, Yj(0) + 3, "joint in graphic gap", 8)
    T(X(depth) + 8, Yj(0) + 14, "Ø6, ~500", 8)
    view_title(X(depth / 2), Yj(HB) + 22, "DETAIL B - PANEL JOINT", "SCALE 1:2  |  vertical section")


# ------------------------------------------------------------------ lapas
def build(S, P, out, sheet_no, n_sheets):
    depth, t = float(S["depth"]), float(S.get("t", 2))
    W, H = float(P["w"]), float(P["h"])
    G = load_panel(S, P)
    hp = split_rows(P, G, depth, t, S.get("sheets_mm", [(3000, 1500), (4000, 2000)]))
    joint = len(hp) > 1
    PLATE = HexColor(S.get("plate_hex") or K.ralhex(str(S["plate_ral"])))
    FL = depth - t
    flats = [(W + 2 * FL, h + 2 * FL) for h in hp]
    span = W - 100; n = max(1, round(span / 300)); pitch = span / n
    nj = max(1, round(span / 500)); pj = span / nj
    # plėvelė - pagal SUNAUDOJIMĄ (v121), kiekvienai spalvai atskirai (lipdukai ant plokštės - užrašas / logotipas nekarpomas)
    VIN = []
    for v in S["vinyl"]:
        gs = [g for vv, _, g in G if vv is v]
        if not gs:
            continue
        p_ = PL.plan(gs, v.get("code", ""), kind=v.get("kind", "color"))
        K.FEAT.add("nest")                               # v304: plėvelės plotas - rulono nesting
        VIN.append((v, p_, sum(g.area for g in gs) / 1e6))
    rows = max(10, 5 + len(VIN) + (1 if joint else 0))
    K.set_band(rows)
    K.init(out + ".tmp", P["name"])
    K.FEAT.add("nest")                                   # v304: plėvelių plotas skaičiuotas rulono nesting (plevele.plan)
    K.frame()
    # ---- mastelis: viršutinė eilė FRONT | SIDE | REAR, apačioje DETAIL A (B) + 3D
    ROW2 = 196                                          # apatinė eilė: DETAIL A / B 1:2 + 3D
    avail_w = K.IX1 - K.IX0 - 260
    avail_h = (K.VIEW_BOT - K.IY0) - ROW2 - 130
    n_ = next((q for q in STD if (2 * W + depth) * MM / q <= avail_w and H * MM / q <= avail_h), STD[-1])
    s = MM / n_
    sc_txt = f"SCALE 1:{n_}"
    # v283: viršutinė eilė (FRONT | SIDE | REAR) centruojama lape (tolygus užpildymas)
    _roww = 92 + W * s + (78 if joint else 56) + depth * s + 96 + W * s + 60
    X0 = K.IX0 + 92 + max(0.0, (K.IX1 - K.IX0 - _roww) / 2)
    YT = K.IY0 + 58
    fx = lambda x: X0 + x * s
    fy = lambda y: YT + y * s
    YB = fy(H)
    # ================= FRONT VIEW
    K.set_view(True)
    rect(X0, YT, W * s, H * s, fill=PLATE, lw=0.5)
    for v, sub, g in G:
        K.draw_shape(sub, lambda x, y: (fx(x), K.Y(fy(y))), fill=HexColor(v["hex"]), stroke=None)
    if joint:
        acc = 0
        for h in hp[:-1]:
            acc += h
            line(X0, fy(acc), fx(W), fy(acc), 0.4, HexColor("#E8E8E8"), dash=([3, 2], 0))
    K.set_view(False)
    hdim(X0, fx(W), YT - 40, f"{W:g}", YT, YT, size=K.F_DIM_MAIN)
    vchain(X0 - 58, [YT, YB], [X0, X0], [f"{H:g}"], size=K.F_DIM_MAIN)
    # grafikos objektų padėtis (vietiniai matmenys arčiausiai): kairėje - viršaus atstumai / aukščiai, viršuje - pločiai
    OBJ = sorted(objects_of(G), key=lambda g: g.bounds[1])
    ys = sorted(set([0.0, H] + [round(v_, 0) for g in OBJ for v_ in (g.bounds[1], g.bounds[3])]))
    vchain(X0 - 26, [fy(v_) for v_ in ys], [X0] * len(ys), [f"{b - a:.0f}" for a, b in zip(ys, ys[1:])], size=K.F_DIM_FRAME)
    if OBJ:
        g0 = OBJ[0]
        xs = [0.0, round(g0.bounds[0]), round(g0.bounds[2]), W]
        hchain(YT - 18, [fx(v_) for v_ in xs], [YT] + [fy(g0.bounds[1])] * 2 + [YT], [f"{b - a:.0f}" for a, b in zip(xs, xs[1:])],
               size=K.F_DIM_FRAME)
    if len(OBJ) > 1:
        gl = OBJ[-1]
        xs = [0.0, round(gl.bounds[0]), round(gl.bounds[2]), W]
        hchain(YB + 18, [fx(v_) for v_ in xs], [YB] + [fy(gl.bounds[3])] * 2 + [YB], [f"{b - a:.0f}" for a, b in zip(xs, xs[1:])],
               size=K.F_DIM_FRAME)
    if joint:
        ys_ = [0] + [sum(hp[:i + 1]) for i in range(len(hp))]
        vchain(fx(W) + 18, [fy(v_) for v_ in ys_], [fx(W)] * len(ys_), [f"{h:g}" for h in hp], size=K.F_DIM_FRAME)
    leader(fx(W * 0.06), fy(H * 0.94), X0 - 30, YB + 40, 1)
    if OBJ:
        rp = max(OBJ, key=lambda g: g.area).representative_point()
        leader(fx(rp.x), fy(rp.y), fx(W) + (44 if joint else 20), fy(min(H, hp[0]) * 0.12), 2)
    view_title(X0 + W * s / 2, YB + 58, "FRONT VIEW", sc_txt)
    # ================= SIDE VIEW
    SX = fx(W) + (78 if joint else 56)
    K.set_view(True)
    acc = 0
    for h in hp:
        rect(SX, fy(acc), depth * s, h * s, fill=PLATE, lw=0.4); acc += h
    K.set_view(False)
    hdim(SX, SX + depth * s, YT - 18, f"{depth:g}", YT, YT, size=K.F_DIM_FRAME, small_side="r")
    T(SX + depth * s + 8, YT + 10, "A", 9, font="FB")
    if joint:
        T(SX + depth * s + 8, fy(hp[0]) + 4, "B", 9, font="FB")
    view_title(SX + depth * s / 2, YB + 58, "SIDE VIEW", sc_txt)
    # ================= REAR VIEW (MIRRORED)
    RX = SX + depth * s + 96
    rx = lambda x: RX + (W - x) * s
    K.set_view(True)
    rect(RX, YT, W * s, H * s, fill=HexColor("#EEF0F2"), lw=0.5)
    for yy in (2, H - 2 - L_SZ):
        rect(rx(W - 25), fy(yy), (W - 50) * s, L_SZ * s, fill=GREY_L, lw=0.4)
    acc = 0
    for h in hp[:-1]:
        acc += h
        line(RX, fy(acc), RX + W * s, fy(acc), 0.5)
    for yy in (7, H - 7):
        for k_ in range(n + 1):
            circle(rx(50 + pitch * k_), fy(yy), 0.9, lw=0.4)
    acc = 0
    for h in hp[:-1]:
        acc += h
        for k_ in range(nj + 1):
            circle(rx(50 + pj * k_), fy(acc), 1.4, fill=HexColor("#3A3A3A"), stroke=None)
    K.set_view(False)
    hchain(YT - 18, [rx(W), rx(W - 50), rx(50), rx(0)], [fy(7) - 3, fy(7) - 3, fy(7) - 3, YT],
           ["50", f"{n}× {pitch:.0f} (= {span:.0f})", "50"], size=K.F_DIM_FRAME)
    hchain(YB + 18, [rx(W), rx(W - 25), rx(25), rx(0)], [YB] * 4, ["25", f"{W - 50:g} (L30x30x2)", "25"], size=K.F_DIM_FRAME)
    leader(rx(W * 0.78), fy(H - 2 - L_SZ / 2), RX + W * s + 22, fy(H * 0.95) - 6, 3)
    leader(rx(50 + pitch), fy(7), RX + W * s + 22, fy(H * 0.12), 4)
    if joint:
        leader(rx(50 + pj), fy(hp[0]), RX + W * s + 22, fy(hp[0]) + 26, 6)
        T(RX + W * s / 2, fy(hp[0]) - 6, f"joint: {nj + 1}× Ø6 (~500)", 8, align="c")
    view_title(RX + W * s / 2, YB + 58, "REAR VIEW (MIRRORED)", f"{sc_txt}  |  Ø3,2 mm, 7 mm from edge")
    # ================= DETAILS + 3D
    DY = K.VIEW_BOT - ROW2 + 34
    vin_main = VIN[0][0]["hex"] if VIN else "#FFFFFF"
    detail_a(K.IX0 + 120, DY, depth, t, vin_main, "DETAIL A - SECTION")
    x3 = K.IX0 + 330
    if joint:
        detail_b(K.IX0 + 420, DY + 66, depth, t, vin_main, vin_main)
        x3 = K.IX0 + 600
    S3 = r3d.Scene(S.get("view_yaw", 28), S.get("view_pitch", 14))
    acc = 0
    for h in hp:
        S3.box((0, H - acc - h + 0.5, 0), (W, 0, 0), (0, h - 1, 0), (0, 0, depth), PLATE, K.mix(PLATE, 0.6))
        acc += h
    for v, sub, g in G:
        gg = stranslate(sscale(g, 1, -1, origin=(0, 0)), 0, H)
        zz = depth + 0.5 + 0.4 * G.index((v, sub, g))   # sluoksniai (logotipo kontūras po raidėmis) - ne tame pačiame z
        for part in getattr(gg, "geoms", [gg]):
            if part.is_empty or part.geom_type != "Polygon":
                continue
            ext = [(x, y, zz) for x, y in list(part.exterior.coords)[:-1]]
            hol = [[(x, y, zz) for x, y in list(r_.coords)[:-1]] for r_ in part.interiors]
            S3.face(ext, (0, 0, 1), HexColor(v["hex"]), None, holes=hol, tile=False, amb=0.9)
    y3 = DY - 24; h3 = K.VIEW_BOT - y3 - 30
    S3.render((x3, y3, K.IX1 - x3 - 20, h3))
    view_title(x3 + (K.IX1 - x3 - 20) / 2, y3 + h3 + 12, "3D VIEW", "ILLUSTRATIVE - NOT TO SCALE")
    # ================= juosta
    BY0 = K.BAND_Y; BH = K.IY1 - BY0
    W_S, W_MD, W_TB = 170, 214, 272
    X_S = K.IX0; X_TB = K.IX1 - W_TB; X_MD = X_TB - W_MD; X_BOM = X_S + W_S; W_BOM = X_MD - X_BOM

    def section(x, y, w, h):                             # v293: tik turinys - K.section_block centruoja bloke
        sc = MM / 2
        xf, yt = x + w / 2 + 10, y + 30
        K.set_view(True)
        rect(xf, yt, t * sc, 70 * sc, fill=black, lw=0.35)
        rect(xf - (depth - t) * sc, yt, (depth - t) * sc, t * sc, fill=black, lw=0.35)
        K.set_view(False)
        rect(xf + t * sc + 0.2, yt + 10, 1.4, 70 * sc - 10, fill=HexColor(vin_main), stroke=black, lw=0.3)
        zig(xf - 8, xf + 12, yt + 70 * sc)
        leader(xf + t * sc + 1, yt + 70, xf + 50, yt + 80, 2)
        leader(xf + 1, yt + 40, xf + 50, yt + 46, 1)
        hdim(xf - (depth - t) * sc, xf + t * sc, yt - 14, f"{depth:g}", yt, yt, size=8)
        yn = yt + 70 * sc + 16                           # pastabos - po pjūviu
        T(x + w / 2, yn, f"Alu {t:g} mm folded, {S.get('finish_short', 'RAL ' + str(S['plate_ral']))}", 7, color=K.GREY, align="c", auto_red=False)
        T(x + w / 2, yn + 10, "+ cut vinyl (front)", 7, color=K.GREY, align="c", auto_red=False)

    K.section_block(X_S, BY0, W_S, BH, "FOLDED PLATE - SECTION 1:2", section)
    A_flat = sum(a_ * b_ for a_, b_ in flats) / 1e6
    L_tot = 2 * (W - 50) / 1000
    kg = A_flat * t * 2.70 + L_tot * 0.000116 * 2700
    n_scr = 2 * (n + 1)
    part_txt = " + ".join(f"{W:g} x {h:g}" for h in hp)
    bom = [["1", f"Folded plate {W:g} x {H:g} x {depth:g} mm" + (f" ({len(hp)} parts)" if joint else ""), f"Alu {t:g} mm folded",
            S.get("finish_short", f"RAL {S['plate_ral']}"), (f"{len(hp)} pcs." if joint else "1 pcs.")]]
    for i, (v, p_, a_) in enumerate(VIN):
        bom.append(["2" if i == 0 else "", f"Vinyl {v['name']}", v["code"], "-", f"{p_['m2']:.2f} m²"])
    bom += [["3", "L profile 30x30x2 (top + bottom)", "Aluminium", "-", f"{L_tot:.2f} m"],
            ["4", "Screw plate -> L, DIN 7504 N 4.2x16", "Steel, hardened", "-", f"{n_scr} pcs."],
            ["5", "Wall fixing", "?", "-", "?"]]
    if joint:
        bom.append(["6", "Bolt + nut, joint (Ø6 holes)", "?", "-", f"{(nj + 1) * (len(hp) - 1)} pcs."])
    md = [["Quantity", f"{P.get('qty', 1)} pcs."], ["Overall size", f"{W:g} x {H:g}"], ["Depth", f"{depth:g}"],
          ["Parts", part_txt if joint else "1"], ["Plate", f"Alu {t:g} mm, folded 4 x 90°"],
          ["Plate finish", S.get("finish", f"RAL {S['plate_ral']}")],
          ["Graphic", f"cut vinyl, {len(VIN)} colours"],
          ["Fixing holes", "Ø3,2 mm, 7 mm from edge, ~300 mm"], ["Mounting", "L30x30x2 top + bottom"],
          ["Illumination", "none"], ["Weight (calc.)", f"≈ {kg:.0f} kg / pcs"]]
    K.main_data(X_MD, BY0, W_MD, BH, md, lab_w=64)
    K.bom_table(X_BOM, BY0, W_BOM, BH, bom)
    tb = {"client": S["client"], "title": f"{S['title']} - {P['name']} {W:g} x {H:g}", "order_no": S.get("order_no", ""),
          "drawing_no": S.get("drawing_no", ""), "sheet": f"{sheet_no} / {n_sheets}", "rev": S.get("rev", "A"),
          "date": S.get("date", ""), "qty": P.get("qty", 1)}
    K.title_block(X_TB, W_TB, tb, f"1:{n_} / 1:2")
    K.save(out)
    return {"hp": hp, "flats": flats, "VIN": VIN, "G": G, "n": n, "pitch": pitch, "nj": nj, "pj": pj, "kg": kg}


def flat_dxf(fn, W, h, depth, t, holes_top, holes_bot, bolts_top, bolts_bot, tb_inside=True):
    """išklotinė (v173 gamybos praktika, FACE OUT): lenkimo linijos W x h, flanšai depth - t.
    v302 (Rytis 2026-10-16, Joker 226057: „folded plates viršus / apačia lenkiasi į vidų"): NUMATYTA viršus / apačia TARP šonų -
    jie iš galų t trumpesni (W - 2t), šonai per visą aukštį (kaip folded_dxf --tb-inside); tb_inside=False - šonai į vidų."""
    import ezdxf
    FL = depth - t
    F, WF = W + 2 * FL, h + 2 * FL
    doc = ezdxf.new("R2010", setup=True); doc.units = ezdxf.units.MM; msp = doc.modelspace()
    for nm, col, lt in (("CUT", 7, "CONTINUOUS"), ("BEND_UP_90", 1, "DASHED"), ("HOLES_D3.2", 3, "CONTINUOUS"),
                        ("HOLES_D6_JOINT", 4, "CONTINUOUS"), ("TEXT", 2, "CONTINUOUS")):
        doc.layers.add(nm, color=col, linetype=lt)
    x0, x1, y0, y1 = FL, FL + W, FL, FL + h
    if tb_inside:
        pts = [(x0 + t, 0), (x1 - t, 0), (x1 - t, y0), (F, y0), (F, y1), (x1 - t, y1), (x1 - t, WF), (x0 + t, WF),
               (x0 + t, y1), (0, y1), (0, y0), (x0 + t, y0)]
    else:
        pts = [(x0, 0), (x1, 0), (x1, y0 + t), (F, y0 + t), (F, y1 - t), (x1, y1 - t), (x1, WF), (x0, WF),
               (x0, y1 - t), (0, y1 - t), (0, y0 + t), (x0, y0 + t)]
    msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": "CUT"})
    msp.add_lwpolyline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], close=True, dxfattribs={"layer": "BEND_UP_90"})
    span = W - 100; n = max(1, round(span / 300))
    for flag, v in ((holes_top, WF - 7), (holes_bot, 7)):
        if flag:
            for k in range(n + 1):
                msp.add_circle((x0 + 50 + span * k / n, v), 1.6, dxfattribs={"layer": "HOLES_D3.2"})
    nj = max(1, round(span / 500))
    for flag, v in ((bolts_top, WF - 20), (bolts_bot, 20)):
        if flag:
            for k in range(nj + 1):
                msp.add_circle((x0 + 50 + span * k / nj, v), 3.0, dxfattribs={"layer": "HOLES_D6_JOINT"})
    msp.add_text(f"FOLDED {W:g} x {h:g} x {depth:g} - Al {t:g} - FLAT {F:.0f} x {WF:.0f} - FACE OUT", height=30,
                 dxfattribs={"layer": "TEXT"}).set_placement((0, -50))
    msp.add_text((f"TOP / BOTTOM INSIDE: top/bottom flanges {W - 2 * t:g} (t shorter each end), sides {h:g}" if tb_inside
                  else f"SIDES INSIDE: side flanges {h - 2 * t:g} (t shorter each end)") + f", flanges {FL:g} from bend line, 4 x 90 up",
                 height=18, dxfattribs={"layer": "TEXT"}).set_placement((0, -90))
    KR.saveas(doc, fn)   # v312: kreivės lankais


def main(spec_path, out):
    S = json.load(open(spec_path, encoding="utf-8"))
    base = os.path.splitext(out)[0]
    pages, res = [], []
    for i, P in enumerate(S["panels"]):
        pp = f"{base}.{P['name']}.pdf"
        r = build(S, P, pp, i + 1, len(S["panels"]))
        pages.append(pp); res.append((P, r))
    K.merge_sheets(pages, out)                            # v293: + lapų .art.json (patikra tikrina visus lapus)
    K.pdf_fix_fonts(out)
    for p in pages:
        for q in (p, p + ".tmp"):
            os.path.exists(q) and os.remove(q)
    depth, t = float(S["depth"]), float(S.get("t", 2))
    for P, r in res:
        hp = r["hp"]
        for j, h in enumerate(hp):
            flat_dxf(f"{base}_flat_{P['name']}{'_' + str(j + 1) if len(hp) > 1 else ''}.dxf", P["w"], h, depth, t,
                     holes_top=(j == 0), holes_bot=(j == len(hp) - 1), bolts_top=(j > 0), bolts_bot=(j < len(hp) - 1),
                     tb_inside=S.get("tb_inside", True))
        for v, p_, a_ in r["VIN"]:
            PL.write_dxf(p_, f"{base}_vinyl_{P['name']}_{v['name'].split()[0].replace('/', '-')}.dxf")
        print(f"  {P['name']}: {P['w']} x {P['h']} parts {hp} flats {[(round(a), round(b)) for a, b in r['flats']]} "
              f"screws {2 * (r['n'] + 1)} kg {r['kg']:.1f}; vinyl " +
              "; ".join(f"{v['name']} {a_:.2f} m² -> {p_['m2']:.2f} m² ({p_['roll']:.0f})" for v, p_, a_ in r["VIN"]))
    print("OK", out, "netelpa:", K.OVERFLOW)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
