#!/usr/bin/env python3
"""P10_lightbox - dvipusė šviesdėžė Alu korpusu su IŠKIŠTU stiklu (push-through) (v197, Rytis 2026-10-13).

Taisyklės - references/moduliai_p10_lightbox.md. Etalonas assets/etalonai/P10_lightbox_dvipuse_600x600x80_kliento.pdf.
- korpusas: priekis (A) ir galas (B) - 2 mm Alu lankstyti padėklai FOLDED principu, flanšas = pusė gylio, sandūra gylio viduryje;
  prisukami prie rėmo per viršutinį / apatinį flanšą (folded standartas: Ø3.2, 7 mm nuo flanšo krašto, 50 nuo galų, ~300);
  sienos pusės flanšuose - išpjovos kojoms (rėmo skersiniai = kojos);
- logotipas: išpjova Alu = kontūras + 0,7; plexi variantas "3" / "3+2" / "3+8" / "3+10"; 3 mm pagrindas = kontūras + 30
  (suapvalintas, sulietas); Ø8 skylės 15 mm nuo kontūro, žingsnis ~100; tose vietose ant Alu - D6 mėlynos žymės (ilgasriegiai);
- rėmas □30x30x2 ... □60x60x3 pagal dydį (□20x20x2 - tik papildomas), kojos - pratęsti skersiniai, plokštės "separate" / "single";
- LED - Kaisen DUOLITE ant rėmo skersinių (viršus + apačia).
Išvestis: A3 lapas (GA) + gamybinis DXF (padėklų išklotinės su išpjova, skylėmis, D6 žymėmis; 3 mm pagrindai su Ø8; įdėklai).
Naudojimas: python3 p10_lightbox.py spec.json out.pdf   (DXF - out.pdf -> out_gamyba.dxf)
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lapas_core as K  # noqa: E402
from lapas_core import T, line, rect, poly, circle, hdim, vchain, hchain, view_title, MM  # noqa: E402
from reportlab.lib.colors import HexColor, white  # noqa: E402
from shapely.geometry import Polygon, Point, box as sbox  # noqa: E402
from shapely.ops import unary_union  # noqa: E402
from shapely import affinity  # noqa: E402

DEF = {"client": "", "title": "DOUBLE-SIDED LIGHTBOX P10 - PUSH-THROUGH", "order_no": "ALT0000_00.00_RS", "drawing_no": "",
       "date": "2026-10-13", "rev": "A", "qty": "?",
       "w": 600, "h": 600, "depth": 80, "t": 2.0, "proj": 100, "clear": 1.0,
       "glass": "3+10", "cut_gap": 0.7, "base_off": 30, "hole_off": 15, "hole_d": 8, "hole_pitch": 100, "mark_d": 6,
       "frame": None, "plates": "separate", "plate": [66, 67, 8], "plate_hole_d": 10,
       "screw_step": 300, "screw_edge": 7, "screw_end": 50, "screws": "",
       "body_finish": "", "frame_finish": "", "plexi": "opal white", "film": "",
       "led": "DS15", "psu": "", "cable": "", "logo": None, "scale_ga": 8}
COL_FRAME, COL_FL, COL_PLEX = HexColor("#B4B4B4"), HexColor("#8C8C8C"), HexColor("#F7F7F2")
COL_BODY = HexColor("#3A3A3A")
BLUE = HexColor("#1F5FD0")
EDGE = HexColor("#555555")


def frame_auto(W, H):
    """v197 PASIŪLYMAS (Rytis: „nuo 30x30x2 iki 60x60x3 pagal dydį") - ribos dar nepatvirtintos"""
    m = max(W, H)
    return [30, 30, 2] if m <= 1000 else [40, 40, 2] if m <= 1600 else [50, 50, 3] if m <= 2500 else [60, 60, 3]


def glass_parts(code):
    """'3' / '3+2' / '3+8' / '3+10' -> (pagrindas, įdėklas)"""
    p = [float(v) for v in str(code).replace(" ", "").split("+")]
    return p[0], (p[1] if len(p) > 1 else 0.0)


def logo_geom(L):
    """kliento logotipas (PNG -> vektorius) -> shapely (mm, y žemyn nuo logotipo viršaus), even-odd"""
    import vektorius
    rs = vektorius.rings(L["file"], L["width"])
    g = None
    for r in rs:
        if len(r) < 3:
            continue
        p = Polygon(r).buffer(0)
        g = p if g is None else g.symmetric_difference(p)
    return g.buffer(0)


def ring_points(ring, pitch, nmin=3):
    L = ring.length
    n = max(nmin, round(L / pitch))
    return [ring.interpolate(L * (k + 0.5) / n) for k in range(n)]


def geom(S):
    g = dict(S)
    W, H, D, t = S["w"], S["h"], S["depth"], S["t"]
    g["frame"] = S["frame"] or frame_auto(W, H)
    fa, fb, ft = g["frame"]
    g["PD"] = D / 2                                                 # padėklo flanšas = pusė tūrio
    g["base_t"], g["ins_t"] = glass_parts(S["glass"])
    g["prot"] = max(0.0, g["ins_t"] - t)                            # išsikišimas (10 - 2 = 8); "3+2" - lygiai su Alu
    g["TOT"] = D + 2 * g["prot"]
    cl = S["clear"]
    g["FW"], g["FH"] = W - 2 * (t + cl), H - 2 * (t + cl)           # rėmo išorė
    g["ax"] = t + cl + fa / 2                                       # kojų (skersinių) ašis nuo dėžės viršaus / apačios
    PLw, PLh, PLt = S["plate"]
    g["leg_len"] = S["proj"] - PLt                                  # koja nuo korpuso iki plokštės
    g["L_h"] = (W - (t + cl)) + g["leg_len"]                        # nuo rėmo laisvo krašto iki plokštės
    g["L_v"] = g["FH"] - 2 * fa                                     # statmenys tarp skersinių (laisvas galas + sienos pusė)
    g["prof_len"] = 2 * g["L_h"] + 2 * g["L_v"]
    ys = [g["ax"], H - g["ax"]]
    if S["plates"] == "single":
        g["plates_l"] = [dict(yc=H / 2, w=PLw, h=ys[1] - ys[0] + PLh, t=PLt, holes=ys)]
    else:
        g["plates_l"] = [dict(yc=y, w=PLw, h=PLh, t=PLt, holes=[y]) for y in ys]
    # logotipas
    g["logo"] = None
    if S.get("logo"):
        L = S["logo"]
        lg = logo_geom(L)
        x0_, y0_, x1_, y1_ = lg.bounds
        lw_, lh_ = x1_ - x0_, y1_ - y0_
        lx = L.get("x", (W - lw_) / 2); ly = L.get("y", (H - lh_) / 2)
        lg = affinity.translate(lg, lx - x0_, ly - y0_)              # dėžės koordinatės (A pusė, iš priekio), y žemyn
        g["logo"], g["logo_w"], g["logo_h"], g["logo_x"], g["logo_y"] = lg, lw_, lh_, lx, ly
        g["cut"] = lg.buffer(S["cut_gap"], join_style=2, mitre_limit=5)
        g["base"] = lg.buffer(S["base_off"], join_style=1)          # suapvalintas, artimi elementai sulieti
        hole_ring = lg.buffer(S["hole_off"], join_style=1)
        pts = []
        for p_ in getattr(hole_ring, "geoms", [hole_ring]):
            pts += ring_points(p_.exterior, S["hole_pitch"])
        g["studs"] = [(round(p.x, 1), round(p.y, 1)) for p in pts]
        g["base_parts"] = list(getattr(g["base"], "geoms", [g["base"]]))
    # LED - Kaisen DUOLITE (kaip sviesdeze.py)
    kj = json.load(open(os.path.join(HERE, "..", "assets", "kaisen_led.json"), encoding="utf-8"))
    du = kj["duolite"][S["led"]]
    boxes = sorted(int(b) for b in du["boxes"])
    hb = min(boxes, key=lambda b: abs(b - H))
    tab = du["boxes"][str(hb)]
    deps = sorted(set(r[0] for r in tab))
    dep = max([d_ for d_ in deps if d_ <= D] or [deps[0]])
    g["led_warn"] = None if any(d_ <= D for d_ in deps) else f"gylis {D:g} < DUOLITE lentelės min {deps[0]} - ryškumą tikrinti"
    cand = [r for r in tab if r[0] == dep]
    best = max([r for r in cand if r[3] >= 2000] or cand, key=lambda r: r[1])
    span = g["FW"] - 2 * fa
    n_row = max(1, math.ceil(span / best[1]))
    g.update(led_name="DUOLITE " + S["led"], led_p=best[1], led_lux=best[3], led_n_row=n_row, led_n=2 * n_row,
             led_step=span / n_row, led_W=2 * n_row * du["W"])
    import led_km
    g["psu_name"] = S["psu"] or led_km.psu_for(g["led_W"], 12)[0].replace("-5Y", "")
    # padėklų varžtai (folded standartas): viršutinis / apatinis flanšas, 7 nuo krašto, 50 nuo galų, ~300
    span_s = W - 2 * S["screw_end"]
    ns = max(1, round(span_s / S["screw_step"]))
    g["scr_x"] = [S["screw_end"] + span_s * k / ns for k in range(ns + 1)]
    g["n_scr"] = 2 * 2 * len(g["scr_x"])                             # 2 padėklai x 2 flanšai
    # svoris (apytikslis)
    rho = json.load(open(os.path.join(HERE, "..", "assets", "svoris.json")))["density_kg_dm3"]
    tray = (W * H + 2 * (W + H) * g["PD"]) * t
    cut_a = g["cut"].area if g.get("logo") else 0
    tube_a = fa * fb - (fa - 2 * ft) * (fb - 2 * ft)
    pmma = 0
    if g.get("logo"):
        pmma = 2 * (g["base"].area * g["base_t"] + g["logo"].area * g["ins_t"])
    g["kg"] = (2 * (tray - cut_a * t) * rho["al"] + g["prof_len"] * tube_a * rho["al"]
               + sum(P["w"] * P["h"] * P["t"] for P in g["plates_l"]) * rho["al"] + pmma * rho["pmma"]) / 1e6
    return g


def prof(a, b, t):
    return f"□{a:g}x{b:g}x{t:g}" if a == b else f"{max(a, b):g}x{min(a, b):g}x{t:g}"


# ===================================================================== LAPAI (v198 - kaip dvipusė šviesdėžė sviesdeze.py: GA + FRAME / PARTS)
import sviesdeze as SV  # noqa: E402
from sviesdeze import HM, VM, D1, D2, face_label, band  # noqa: E402
COL_LED = SV.COL_LED
COL_BASE = HexColor("#E4E4DE")
COL_STUD = HexColor("#B0B0B0")


def draw_geom(geo, X, Y, fill=None, stroke=None, lw=0.1, dash=None):
    c = K.c
    c.saveState()
    if fill is not None:
        c.setFillColor(fill)
    c.setStrokeColor(stroke or HexColor("#000000")); c.setLineWidth(lw)
    if dash:
        c.setDash(*dash)
    p = c.beginPath()
    for pg in getattr(geo, "geoms", [geo]):
        if pg.is_empty or not hasattr(pg, "exterior"):
            continue
        for ring in [pg.exterior] + list(pg.interiors):
            pts = [(X(x), K.H - Y(y)) for x, y in ring.coords]
            p.moveTo(*pts[0])
            for q in pts[1:]:
                p.lineTo(*q)
            p.close()
    c.drawPath(p, stroke=1, fill=1 if fill is not None else 0, fillMode=0)
    c.restoreState()


def vsegs(geo, x, y0=-1e4, y1=1e4):
    """geometrijos pjūvis vertikalia linija x -> [(ya, yb)]"""
    from shapely.geometry import LineString
    if geo is None:
        return []
    ix = geo.intersection(LineString([(x, y0), (x, y1)]))
    out = []
    for q in getattr(ix, "geoms", [ix]):
        if not q.is_empty and q.length > 0.5:
            ys_ = [c_[1] for c_ in q.coords]
            out.append((min(ys_), max(ys_)))
    return sorted(out)


def nice_scale(avail_pt, size_mm, opts=(2, 2.5, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30, 40, 50)):
    return next((n for n in opts if size_mm * MM / n <= avail_pt), opts[-1])


def scene3d(g, yaw, box, title):
    import r3d
    W, H, D = g["w"], g["h"], g["depth"]
    fa, fb, ft = g["frame"]; LL = g["leg_len"]; PLt = g["plate"][2]
    sc = r3d.Scene(yaw=yaw, pitch=18)
    sc.box((0, 0, -D / 2), (W, 0, 0), (0, H, 0), (0, 0, D), COL_BODY, edge=EDGE)
    for y_ in (g["ax"], H - g["ax"]):
        sc.box((W, H - y_ - fb / 2, -fa / 2), (LL, 0, 0), (0, fb, 0), (0, 0, fa), COL_FRAME, edge=EDGE)
    for P in g["plates_l"]:
        sc.box((W + LL, H - P["yc"] - P["h"] / 2, -P["w"] / 2), (PLt, 0, 0), (0, P["h"], 0), (0, 0, P["w"]), COL_FL, edge=EDGE)
    if g.get("logo") is not None:
        pr = max(g["prot"], 0.6)
        sc.extrude_xy(g["logo"], D / 2, D / 2 + pr, COL_PLEX, COL_PLEX, edge=EDGE, xf=lambda x, y, z: (x, H - y, z))
        sc.extrude_xy(g["logo"], D / 2, D / 2 + pr, COL_PLEX, COL_PLEX, edge=EDGE, xf=lambda x, y, z: (W - x, H - y, -z))
    sc.render(box)
    V = sc.V
    for zf, lab in ((D / 2, "SIDE A"), (-D / 2, "SIDE B")):
        if V.rot(0, 0, 1 if zf > 0 else -1)[2] > 0:
            px, py = V.S(W / 2, H * 0.06, zf)
            face_label(px, K.H - py, lab, 8)
    view_title(box[0] + box[2] / 2, box[1] + box[3] + 18, title, "ILLUSTRATIVE - NOT TO SCALE")


def sheet1(g, out):
    W, H, D, t = g["w"], g["h"], g["depth"], g["t"]
    fa, fb, ft = g["frame"]
    LL, PR = g["leg_len"], g["proj"]
    PLt = g["plate"][2]
    pr, bt, it_ = g["prot"], g["base_t"], g["ins_t"]
    TOT = g["TOT"]
    lg = g.get("logo")
    K.set_band(len(bom1(g)) + 1)
    K.init(out + ".tmp", "sheet1")
    K.frame()
    s = MM / g["scale_ga"]
    sl = f"1:{g['scale_ga']:g}"
    top = K.IY0 + 112
    Yv = lambda y: top + y * s
    ax = g["ax"]

    def front(fx, mirror):
        X = (lambda x: fx + (W + PR - x) * s) if mirror else (lambda x: fx + x * s)
        xl, xr = (X(W), X(0)) if mirror else (X(0), X(W))
        K.set_view(True)
        rect(xl, Yv(0), W * s, H * s, fill=COL_BODY, lw=0.1)
        if lg is not None:
            Xm = (lambda x: X(W - x)) if mirror else X
            draw_geom(g["logo"], Xm, Yv, fill=COL_PLEX, lw=0.1)
        for y_ in (ax, H - ax):
            a_, _ = sorted((X(W), X(W + LL)))
            rect(a_, Yv(y_ - fb / 2), LL * s, fb * s, fill=COL_FRAME, lw=0.1)
        for P in g["plates_l"]:
            a2, _ = sorted((X(W + LL), X(W + PR)))
            rect(a2, Yv(P["yc"] - P["h"] / 2), PLt * s, P["h"] * s, fill=COL_FL, lw=0.1)
        K.set_view(False)
        for y_ in (ax, H - ax):
            K.centerline(X(W - 20), Yv(y_), X(W + PR + 8), Yv(y_))
        xs_ = sorted([X(0), X(W), X(W + LL), X(W + PR)])
        labs = [f"{W:g}", f"{LL:g}", f"{PLt:g}"]
        hchain(Yv(H) + D1, xs_, [Yv(H)] * 4, labs[::-1] if mirror else labs, size=K.F_DIM_MAIN)
        HM(xs_[0], xs_[-1], Yv(H) + D2, f"{W + PR:g}", Yv(H), Yv(H))
        if lg is not None:
            lx0 = g["logo_x"]; lx1 = lx0 + g["logo_w"]
            pa, pb = sorted((X(W - lx1), X(W - lx0)) if mirror else (X(lx0), X(lx1)))
            hchain(Yv(0) - D1, [xl, pa, pb, xr], [Yv(0), Yv(g["logo_y"]), Yv(g["logo_y"]), Yv(0)],
                   [f"{(pa - xl) / s:.0f}", f"{g['logo_w']:.0f}", f"{(xr - pb) / s:.0f}"], size=K.F_DIM_MAIN)
            ly0, ly1 = g["logo_y"], g["logo_y"] + g["logo_h"]
            xe = xl if not mirror else xr
            xo = xe - D1 if not mirror else xe + D1
            vchain(xo, [Yv(0), Yv(ly0), Yv(ly1), Yv(H)], [xe, pa if not mirror else pb, pa if not mirror else pb, xe],
                   [f"{ly0:.0f}", f"{g['logo_h']:.0f}", f"{H - ly1:.0f}"], size=K.F_DIM_MAIN)
        xe = xl if not mirror else xr
        VM(xe - D2 if not mirror else xe + D2, Yv(0), Yv(H), xe, f"{H:g}")
        xw = X(W + PR)
        vchain(xw + D1 if not mirror else xw - D1, [Yv(0), Yv(ax), Yv(H - ax), Yv(H)], [X(W)] + [xw] * 2 + [X(W)],
               [f"{ax:g}", f"{H - 2 * ax:g}", f"{ax:g}"], size=K.F_DIM_MAIN)
        return X

    # ------------------------------------------------ SIDE A
    fxA = K.IX0 + 78
    XA = front(fxA, False)
    xc = (g["logo_x"] + g["logo_w"] / 2) if lg is not None else W / 2
    K.cut_plane(XA(xc), Yv(0) - 30, Yv(H) + 54, "A", look="right")
    K.balloon_side([(XA(W * 0.1), Yv(H * 0.9), 2)] + ([(XA(g["logo_x"] + g["logo_w"] * 0.3), Yv(g["logo_y"] + g["logo_h"] * 0.5), 4)]
                                                     if lg is not None else []), XA(0) - 60, "left", up=False)
    K.balloon_side([(XA(W + LL * 0.5), Yv(ax), 1), (XA(W + PR - PLt / 2), Yv(H - ax + g["plate"][1] / 2 - 6), "1A")],
                   XA(W + PR) + 56, "right", up=False)
    view_title(XA((W + PR) / 2), top - 84, "FRONT VIEW - SIDE A", sl)
    # ------------------------------------------------ VAIZDAS IŠ SIENOS
    sxc = XA(W + PR) + 150
    Zs = lambda z: sxc + z * s
    P0 = g["plates_l"][0]; PLw = P0["w"]
    K.set_view(True)
    rect(Zs(-D / 2), Yv(0), D * s, H * s, fill=COL_BODY, lw=0.1)
    nd = fa / 2 + g["clear"]
    for y_ in (ax, H - ax):                                         # kojų išpjovos sienos pusės flanšuose (A + B)
        rect(Zs(-fa / 2), Yv(y_ - fb / 2), fa * s, fb * s, fill=COL_FRAME, lw=0.1)
    for P in g["plates_l"]:
        rect(Zs(-P["w"] / 2), Yv(P["yc"] - P["h"] / 2), P["w"] * s, P["h"] * s, fill=COL_FL, lw=0.1)
        for y_ in P["holes"]:
            circle(Zs(0), Yv(y_), g["plate_hole_d"] / 2 * s, fill=white, lw=0.1)
    K.set_view(False)
    line(Zs(0), Yv(0), Zs(0), Yv(H), 0.2, HexColor("#888888"), dash=(3, 1.5))     # padėklų sandūra
    face_label(Zs(-D / 2) + 2, Yv(0) - 54, "A", 9); face_label(Zs(D / 2) - 2, Yv(0) - 54, "B", 9)
    hy_ = sorted(y for P in g["plates_l"] for y in P["holes"])
    ptop = min(P["yc"] - P["h"] / 2 for P in g["plates_l"]); pbot = max(P["yc"] + P["h"] / 2 for P in g["plates_l"])
    yy = [ptop] + hy_ + [pbot]
    ex_ = max(PLw, D) / 2
    vchain(Zs(ex_) + D1, [Yv(v) for v in yy], [Zs(PLw / 2)] * len(yy), [f"{b - a:g}" for a, b in zip(yy, yy[1:])],
           size=K.F_DIM_MAIN)
    VM(Zs(ex_) + D2, Yv(ptop), Yv(pbot), Zs(PLw / 2), f"{pbot - ptop:g}")
    VM(Zs(-ex_) - D1, Yv(0), Yv(H), Zs(-D / 2), f"{H:g}")
    HM(Zs(-D / 2), Zs(D / 2), Yv(0) - D1, f"{D:g}", Yv(0), Yv(0))
    HM(Zs(-PLw / 2), Zs(PLw / 2), Yv(pbot) + D1, f"{PLw:g}", Yv(pbot), Yv(pbot))
    K.balloon_side([(Zs(0), Yv(hy_[-1]), f"{len(hy_)} x Ø{g['plate_hole_d']:g}"),
                    (Zs(nd), Yv(ax + fb / 2 + g["clear"]), f"leg cut-out {2 * nd:g}x{fb + 2 * g['clear']:g}")],
                   Zs(ex_) + 40, "right", up=True, tags=True)
    T(Zs(0), Yv(H) + 40, "= WALL DRILLING; - - - tray seam", 8, align="c", color=K.GREY)
    view_title(Zs(0), top - 84, "VIEW FROM WALL", sl)
    # ------------------------------------------------ SIDE B
    fxB = Zs(ex_) + 160
    XB = front(fxB, True)
    K.balloon_side([(XB(W * 0.1), Yv(H * 0.9), 3)] + ([(XB(g["logo_x"] + g["logo_w"] * 0.3), Yv(g["logo_y"] + g["logo_h"] * 0.5), 5)]
                                                     if lg is not None else []), XB(0) + 60, "right", up=False)
    view_title(XB((W + PR) / 2), top - 84, "FRONT VIEW - SIDE B", sl + "  (mirrored)")
    # ------------------------------------------------ SECTION A-A (per logotipo vidurį)
    avail_h = K.VIEW_BOT - top - 160                                # po pjūviu - TOP VIEW
    n5 = nice_scale(avail_h, H, (4, 5, 6, 8, 10, 12, 15, 20))
    s5 = MM / n5
    xs0 = XB(0) + 90
    U = lambda u: xs0 + (u + pr) * s5                               # u: 0 = A Alu išorė, D = B Alu išorė
    Ya = lambda y: top + y * s5
    K.set_view(True)
    segA = vsegs(g["cut"], xc) if lg is not None else []
    segB = vsegs(g["cut"], W - xc) if lg is not None else []
    for side, segs_ in (("A", segA), ("B", segB)):
        u0 = 0 if side == "A" else D - t
        ya_ = 0
        for a_, b_ in segs_ + [(H, H)]:
            if a_ > ya_:
                rect(U(u0), Ya(ya_), t * s5, (a_ - ya_) * s5, fill=COL_BODY, lw=0.1)        # Alu priekis / galas (be išpjovos)
            ya_ = b_
        fu0 = 0 if side == "A" else D / 2
        for yf in (0, H - t):                                       # viršutinis / apatinis flanšas (iki sandūros)
            rect(U(fu0), Ya(yf), (D / 2) * s5, t * s5, fill=COL_BODY, lw=0.1)
        if lg is not None:
            ub = t if side == "A" else D - t - bt
            for a_, b_ in vsegs(g["base"], xc if side == "A" else W - xc):
                rect(U(ub), Ya(a_), bt * s5, (b_ - a_) * s5, fill=COL_BASE, lw=0.1)
            if it_ > 0:
                ui = t - it_ if side == "A" else D - t
                for a_, b_ in vsegs(g["logo"], xc if side == "A" else W - xc):
                    rect(U(ui), Ya(a_), it_ * s5, (b_ - a_) * s5, fill=COL_PLEX, lw=0.1)
    for y0 in (t + g["clear"], H - t - g["clear"] - fb):            # rėmo skersiniai gylio viduryje
        rect(U(D / 2 - fa / 2), Ya(y0), fa * s5, fb * s5, fill=COL_FRAME, lw=0.1)
        rect(U(D / 2 - fa / 2 + ft), Ya(y0 + ft), (fa - 2 * ft) * s5, (fb - 2 * ft) * s5, fill=white, lw=0.1)
    yl_t = t + g["clear"] + fb
    yl_b = H - t - g["clear"] - fb
    rect(U(D / 2 - 11), Ya(yl_t), 22 * s5, 8 * s5, fill=COL_LED, lw=0.1)
    rect(U(D / 2 - 11), Ya(yl_b - 8), 22 * s5, 8 * s5, fill=COL_LED, lw=0.1)
    K.set_view(False)
    for dz in (-1, 1):
        hb_ = (D / 2) / math.tan(math.radians(32.5))
        line(U(D / 2), Ya(yl_t + 8), U(D / 2 + dz * D / 2), Ya(yl_t + 8 + hb_), 0.2, HexColor("#C9A000"), dash=(2, 1.5))
        line(U(D / 2), Ya(yl_b - 8), U(D / 2 + dz * D / 2), Ya(yl_b - 8 - hb_), 0.2, HexColor("#C9A000"), dash=(2, 1.5))
    line(U(D / 2), Ya(-4), U(D / 2), Ya(H + 4), 0.2, HexColor("#888888"), dash=(3, 1.5))
    face_label(U(-pr) + 2, Ya(0) - 10, "A", 9); face_label(U(D + pr) - 2, Ya(0) - 10, "B", 9)
    hchain(Ya(H) + D1, [U(-pr), U(0), U(D), U(D + pr)], [Ya(H)] * 4, [f"{pr:g}", f"{D:g}", f"{pr:g}"], size=K.F_DIM_MAIN)
    HM(U(-pr), U(D + pr), Ya(H) + D2, f"{TOT:g}", Ya(H), Ya(H))
    if segA:
        yy = [0] + [v for sg in segA for v in sg] + [H]
        vchain(U(-pr) - D1, [Ya(v) for v in yy], [U(0)] * len(yy), [f"{b - a:.0f}" for a, b in zip(yy, yy[1:])],
               size=K.F_DIM_MAIN)
    VM(U(-pr) - D2, Ya(0), Ya(H), U(-pr), f"{H:g}")
    if segA:
        ym = (segA[0][0] + segA[0][1]) / 2
        K.balloon_side([(U(t / 2), Ya(H * 0.85), 2), (U(-pr / 2), Ya(ym), 4), (U(t + bt / 2), Ya(segA[0][1] + 15), 6),
                        (U(D / 2 - fa / 2), Ya(t + 10), 1), (U(D / 2 - 11), Ya(yl_t + 4), 8)], U(-pr) - 62, "left", up=True)
        K.balloon_side([(U(D - t / 2), Ya(H * 0.85), 3), (U(D + pr / 2), Ya(ym), 5), (U(D - t - bt / 2), Ya(segA[0][1] + 15), 7)],
                       U(D + pr) + 24, "right", up=True)
        circle(U(0), Ya(segA[0][0]), 14, lw=0.3, dash=(3, 1.5))
        T(U(0) - 30, Ya(segA[0][0]) - 20, "B", 10, font="FB")
    view_title(U(D / 2), top - 84, "SECTION A-A", f"1:{n5:g}")
    # ------------------------------------------------ 2 eilė: 3D A, 3D B, TOP VIEW
    y3 = Yv(H) + 96
    h3 = K.VIEW_BOT - y3 - 34
    w3 = 250
    try:
        scene3d(g, -35, (K.IX0 + 50, y3, w3, h3), "3D VIEW - SIDE A")
        scene3d(g, 145, (K.IX0 + 50 + w3 + 40, y3, w3, h3), "3D VIEW - SIDE B")
    except Exception as e:
        print("  ! 3D:", e)
    # TOP VIEW: padėklų flanšai (A / B), sandūra, varžtai Ø3.2 (10)
    tx0 = K.IX1 - (W + PR) * s - 90
    tyc = K.VIEW_BOT - 64
    Xt = lambda x: tx0 + x * s
    Zt = lambda z: tyc + z * s                                      # z > 0 - A pusė (apačioje)
    K.set_view(True)
    rect(Xt(0), Zt(-D / 2), W * s, D * s, fill=COL_BODY, lw=0.1)
    if pr > 0 and lg is not None:
        for sg in (1, -1):
            rect(Xt(g["logo_x"]), Zt(sg * D / 2) if sg > 0 else Zt(-D / 2 - pr), g["logo_w"] * s, pr * s, fill=COL_PLEX, lw=0.1)
    rect(Xt(W), Zt(-fa / 2), LL * s, fa * s, fill=COL_FRAME, lw=0.1)
    rect(Xt(W + LL), Zt(-PLw / 2), PLt * s, PLw * s, fill=COL_FL, lw=0.1)
    for x_ in g["scr_x"]:
        for sg in (1, -1):
            circle(Xt(x_), Zt(sg * g["screw_edge"]), 1.6 * s + 0.6, fill=white, lw=0.1)
    K.set_view(False)
    line(Xt(0), Zt(0), Xt(W), Zt(0), 0.2, HexColor("#888888"), dash=(3, 1.5))
    face_label(Xt(0) - 8, Zt(D / 2 - 6), "A", 8); face_label(Xt(0) - 8, Zt(-D / 2 + 6), "B", 8)
    xs_ = [0] + g["scr_x"] + [W]
    hchain(Zt(-D / 2 - pr) - D1, [Xt(v) for v in xs_], [Zt(-g["screw_edge"])] * len(xs_),
           [f"{b - a:.0f}" for a, b in zip(xs_, xs_[1:])], size=K.F_DIM_MAIN)
    vchain(Xt(W + PR) + D1, [Zt(-g["screw_edge"]), Zt(g["screw_edge"])], [Xt(W)] * 2, [f"{2 * g['screw_edge']:g}"],
           size=K.F_DIM_MAIN)
    T(Xt(W / 2), Zt(D / 2 + pr) + 24, f"screws 10: {g['n_scr']} pcs. Ø3.2, top + bottom flanges, {g['screw_edge']:g} from seam", 8,
      align="c", color=K.GREY)
    view_title(Xt((W + PR) / 2), Zt(-D / 2 - pr) - 44, "TOP VIEW", sl)

    band(g, "1 / 3", " - GA", main_data1(g), bom1(g), detail_b(g))
    K.save(out)


def detail_b(g):
    t, pr, bt, it_ = g["t"], g["prot"], g["base_t"], g["ins_t"]

    def detail(X_P6, BY0, W_P6, BH):
        """DETAIL B - išpjovos kraštas (A), 2:1: Alu, tarpas, iškištas įdėklas, pagrindas, ilgasriegis + veržlė"""
        hyo = g["hole_off"]
        vtop = -6.0                                                  # v: 0 = išpjovos kraštas, + į Alu pusę
        vmax = hyo + 6.0
        avail = BH - 12 - 22 - 20                                    # antraštė, matmenys viršuje, pastabos apačioje
        sc = 2.0 if (vmax - vtop) * 2 * MM <= avail else (1.5 if (vmax - vtop) * 1.5 * MM <= avail else 1.0)
        s3 = sc * MM
        K.header(X_P6, BY0, W_P6, f"DETAIL B - CUT-OUT EDGE  {sc:g}:1")
        rect(X_P6, BY0 + 12, W_P6, BH - 12, lw=0.6)
        reg = (X_P6 + 3, BY0 + 15, X_P6 + W_P6 - 3, BY0 + BH - 26)
        ox = X_P6 + 60 + pr * s3
        Z = lambda z: ox + z * s3                                   # z: 0 = Alu išorė, + į dėžės vidų
        oy = BY0 + 12 + 22
        Yb = lambda v: oy + (v - vtop) * s3
        K.set_view(True)
        rect(Z(0), Yb(g["cut_gap"]), t * s3, (vmax - g["cut_gap"]) * s3, fill=COL_BODY, lw=0.1)
        rect(Z(t), Yb(vtop), bt * s3, (vmax - vtop) * s3, fill=COL_BASE, lw=0.1)
        if it_ > 0:
            rect(Z(t - it_), Yb(vtop), it_ * s3, (-vtop) * s3, fill=COL_PLEX, lw=0.1)
        rect(Z(0), Yb(hyo - 2), (t + bt + 5) * s3, 4 * s3, fill=COL_STUD, lw=0.1)
        rect(Z(t + bt), Yb(hyo - 3.5), 3 * s3, 7 * s3, fill=HexColor("#8C8C8C"), lw=0.1)
        K.set_view(False)
        K.centerline(Z(-pr) - 4, Yb(hyo), Z(t + bt + 9), Yb(hyo))
        hchain(BY0 + 26, [Z(t - it_), Z(0), Z(t + bt)], [Yb(vtop)] * 3, [f"{pr:g}", f"{t:g}+{bt:g}"],
               size=K.F_DIM_FRAME)
        vchain(Z(-pr) - 10, [Yb(0), Yb(hyo)], [Z(0)] * 2, [f"{hyo:g}"], size=K.F_DIM_FRAME)
        for tx_, ty_, lab in ((Z(t / 2), Yb((g["cut_gap"] + hyo - 2) / 2), 2), (Z(t - it_ / 2), Yb(vtop / 2), 4),
                              (Z(t + bt / 2), Yb(hyo + 4), 6), (Z(t + bt + 4), Yb(hyo), 9)):
            K.balloon_auto(tx_, ty_, lab, region=reg)
        T(X_P6 + W_P6 / 2, BY0 + BH - 13, f"gap {g['cut_gap']:g}; insert {it_:g} GLUED to base 6",
          6.5, align="c", color=K.GREY)
        T(X_P6 + W_P6 / 2, BY0 + BH - 4, f"stud welded (D{g['mark_d']:g} mark); B = mirror", 6.5, align="c", color=K.GREY)

    return detail


def bom1(g):
    fa, fb, ft = g["frame"]
    P0 = g["plates_l"][0]
    W, H = g["w"], g["h"]
    rows = [[1, f"Frame + legs {prof(fa, fb, ft)} (sheet 2)", "Alu, welded", g["frame_finish"] or "",
             f"2 x {g['L_h']:.0f} + 2 x {g['L_v']:.0f} mm"],
            ["1A", f"Mounting plate {P0['w']:g}x{P0['h']:g}x{P0['t']:g}, Ø{g['plate_hole_d']:g}", "Alu, welded to leg",
             g["frame_finish"] or "", f"{len(g['plates_l'])} pcs."],
            [2, f"Front A, folded {W:g}x{H:g}x{g['PD']:g} (sheet 2)", f"Alu {g['t']:g} mm", g["body_finish"] or "", "1 pc."],
            [3, f"Back B, folded {W:g}x{H:g}x{g['PD']:g} (sheet 2)", f"Alu {g['t']:g} mm", g["body_finish"] or "", "1 pc."]]
    if g.get("logo") is not None:
        if g["ins_t"] > 0:
            for k_, sd in ((4, "A"), (5, "B")):
                rows.append([k_, f"Insert {sd} {g['ins_t']:g} mm, GLUED to base", f"Plexi {g['plexi']}", g["film"] or "-",
                             f"1 pc. {g['logo'].area / 1e6:.3f} m²"])
        for k_, sd in ((6, "A"), (7, "B")):
            rows.append([k_, f"Base {sd} {g['base_t']:g} mm, {len(g['studs'])} x Ø{g['hole_d']:g} (sheet 2)", f"Plexi {g['plexi']}",
                         "-", f"1 pc. {g['base'].area / 1e6:.3f} m²"])
    rows += [[8, f"LED Kaisen {g['led_name']} (sheet 2)", "PSU " + g["psu_name"], "6500 K", f"{g['led_n']} pcs. ({g['led_W']:.1f} W)"]]
    if g.get("logo") is not None:
        rows += [[9, "Stud (welded to Alu) + nut", "?", "-", f"{2 * len(g['studs'])} pcs."]]
    rows += [[10, ("Countersunk screw" if g["screws"] == "countersunk" else "Screw") + ", Ø3.2 holes in flanges", "A2", "-",
              f"{g['n_scr']} pcs."]]
    return rows


def main_data1(g):
    md = [["Product", "P10 lightbox, 2-sided"],
          ["Size", f"{g['w']:g} x {g['h']:g} x {g['depth']:g} (+ 2 x {g['prot']:g})"],
          ["From wall", f"{g['proj']:g} mm (legs {g['leg_len']:g} + plate {g['plate'][2]:g})"],
          ["Body", f"Alu {g['t']:g}, 2 folded trays A + B, seam centre"],
          ["Glass", f"{g['glass']} mm, cut-out + {g['cut_gap']:g}"],
          ["Frame", f"{prof(*g['frame'])} {g['frame_finish'] or ''}".strip()],
          ["LED / PSU", f"{g['led_n']} x {g['led_name']}, {g['psu_name']}"],
          ["Qty", f"{g['qty']}"],
          ["Weight (calc.)", f"≈ {g['kg']:.1f} kg / pcs, excl. PSU"]]
    if g["film"]:
        md.insert(5, ["Film", g["film"]])
    return md


# ===================================================================== 2 LAPAS - FRAME + LED + DALYS
def sheet2(g, out):
    W, H, D, t = g["w"], g["h"], g["depth"], g["t"]
    fa, fb, ft = g["frame"]
    LL, PR = g["leg_len"], g["proj"]
    PLw, PLh, PLt = g["plate"]
    K.set_band(9)
    K.init(out + ".tmp", "sheet2")
    K.frame()
    top = K.IY0 + 112
    hv = K.VIEW_BOT - top
    nF = nice_scale(min(hv * 0.33, 420), max(H, (W + PR) * 0.62), (4, 5, 6, 8, 10, 12, 15, 20))
    s = MM / nF
    x0 = t + g["clear"]
    fx = K.IX0 + 100
    X = lambda x: fx + (x - x0) * s
    Yv = lambda y: top + (y - x0) * s
    FW, FH = g["FW"], g["FH"]
    xr = x0 + FW
    xf = W + LL                                                     # plokštės vidinis paviršius
    K.set_view(True)
    rect(X(0), Yv(0), W * s, H * s, stroke=HexColor("#9A9A9A"), lw=0.1, dash=(3, 2))   # korpusas
    for y0 in (x0, x0 + FH - fb):
        rect(X(x0), Yv(y0), (xf - x0) * s, fb * s, fill=COL_FRAME, lw=0.1)
    for xx in (x0, xr - fa):
        rect(X(xx), Yv(x0 + fb), fa * s, g["L_v"] * s, fill=COL_FRAME, lw=0.1)
    for P in g["plates_l"]:
        rect(X(xf), Yv(P["yc"] - P["h"] / 2), PLt * s, P["h"] * s, fill=COL_FL, lw=0.1)
    led_x = [x0 + fa + g["led_step"] * (i + 0.5) for i in range(g["led_n_row"])]
    yrow = [x0 + fb, x0 + FH - fb]
    for k_, yr in enumerate(yrow):
        for lx in led_x:
            rect(X(lx - 11), Yv(yr if k_ == 0 else yr - 8), 22 * s, 8 * s, fill=COL_LED, lw=0.1)
        yw = yr + 4 if k_ == 0 else yr - 4
        line(X(led_x[0]), Yv(yw), X(xr - fa), Yv(yw), 0.2, HexColor("#C00000"))
    K.set_view(False)
    hchain(Yv(x0) - D1, [X(x0), X(W), X(xf), X(xf + PLt)], [Yv(x0)] * 2 + [Yv(g["plates_l"][0]["yc"] - PLh / 2)] * 2,
           [f"{W - x0:g}", f"{LL:g}", f"{PLt:g}"], size=K.F_DIM_FRAME)
    HM(X(x0), X(xf), Yv(x0) - D2 - 14, f"{g['L_h']:.0f}  ({prof(fa, fb, ft)}, 2 pcs.)", Yv(x0), Yv(x0))
    vchain(X(x0) - D1, [Yv(x0), Yv(x0 + fb), Yv(x0 + FH - fb), Yv(x0 + FH)], [X(x0)] * 4,
           [f"{fb:g}", f"{g['L_v']:.0f}", f"{fb:g}"], size=K.F_DIM_FRAME)
    VM(X(x0) - D2, Yv(x0), Yv(x0 + FH), X(x0), f"{FH:g}")
    vchain(X(xf + PLt) + D1, [Yv(g["ax"]), Yv(H - g["ax"])], [X(xf)] * 2, [f"{H - 2 * g['ax']:g}"], size=K.F_DIM_FRAME)
    K.balloon_side([(X(W + 20), Yv(x0 + fb / 2), "1.1"), (X(xr - fa / 2), Yv(H * 0.4), "1.3")],
                   X(xf + PLt) + 40, "right", up=False, r=7)
    K.balloon_side([(X(led_x[-1] + 11), Yv(yrow[1] - 4), 8), (X(W + 20), Yv(x0 + FH - fb / 2), "1.2")],
                   X(xf + PLt) + 40, "right", up=True, r=7)
    K.cut_plane(X(led_x[len(led_x) // 2]), Yv(x0 + FH - fb) - 10, Yv(x0 + FH), "C", look="right")
    view_title(X((x0 + xf) / 2), top - 96, "FRAME (1) + LED (8)", f"1:{nF:g}  (from side A, welded)")
    # ------------------------------------------------ SECTION C-C (LED) 1:2
    s2 = MM / 2
    pr, bt = g["prot"], g["base_t"]
    cx0, cy0 = X(xf + PLt) + 190, top + 40
    Zc = lambda z: cx0 + (z + D / 2) * s2
    Yc = lambda y: cy0 + y * s2
    up_ = 60
    K.set_view(True)
    for zz in (-D / 2, D / 2 - t):
        rect(Zc(zz), Yc(-up_), t * s2, (up_ + fb + g["clear"] + t) * s2, fill=COL_BODY, lw=0.1)
    for zz in (-D / 2, 0):
        rect(Zc(zz), Yc(fb + g["clear"]), (D / 2) * s2, t * s2, fill=COL_BODY, lw=0.1)
    rect(Zc(-fa / 2), Yc(0), fa * s2, fb * s2, fill=COL_FRAME, lw=0.1)
    rect(Zc(-fa / 2 + ft), Yc(ft), (fa - 2 * ft) * s2, (fb - 2 * ft) * s2, fill=white, lw=0.1)
    rect(Zc(-11), Yc(-8), 22 * s2, 8 * s2, fill=COL_LED, lw=0.1)
    K.set_view(False)
    line(Zc(0), Yc(-up_), Zc(0), Yc(fb + g["clear"] + t + 3), 0.2, HexColor("#888888"), dash=(3, 1.5))
    for dz in (-1, 1):
        hb_ = min(D / 2 / math.tan(math.radians(32.5)), up_ - 10)
        line(Zc(0), Yc(-8), Zc(dz * hb_ * math.tan(math.radians(32.5))), Yc(-8 - hb_), 0.25, HexColor("#C9A000"), dash=(2, 1.5))
    hchain(Yc(fb + g["clear"] + t) + D1, [Zc(-D / 2), Zc(-fa / 2), Zc(fa / 2), Zc(D / 2)], [Yc(fb + g["clear"] + t)] * 4,
           [f"{(D - fa) / 2:g}", f"{fa:g}", f"{(D - fa) / 2:g}"], size=K.F_DIM_FRAME)
    HM(Zc(-D / 2), Zc(D / 2), Yc(fb + g["clear"] + t) + D2, f"{D:g}", Yc(fb + g["clear"] + t), Yc(fb + g["clear"] + t))
    vchain(Zc(D / 2) + D1, [Yc(0), Yc(fb), Yc(fb + g["clear"]), Yc(fb + g["clear"] + t)], [Zc(fa / 2)] * 2 + [Zc(D / 2)] * 2,
           [f"{fb:g}", f"{g['clear']:g}", f"{t:g}"], size=K.F_DIM_FRAME)
    K.balloon_side([(Zc(D / 2 - t / 2), Yc(-up_ * 0.7), 3), (Zc(11), Yc(-6), 8), (Zc(D / 4), Yc(fb + g["clear"] + t / 2), 3)],
                   Zc(D / 2) + 46, "right", up=True)
    K.balloon_side([(Zc(-D / 2 + t / 2), Yc(-up_ * 0.7), 2), (Zc(-fa / 2), Yc(fb / 2), 1)], Zc(-D / 2) - 14, "left", up=True)
    T(Zc(0), Yc(fb + g["clear"] + t) + 62, "DUOLITE on member - light to both faces; trays seam at centre", 8, align="c",
      color=K.GREY)
    view_title(Zc(0), top - 96, "SECTION C-C (LED)", "1:2")
    # ------------------------------------------------ PLATE 1A 1:2
    flx = Zc(D / 2) + 150
    P0 = g["plates_l"][0]
    sp = MM / (2 if P0["h"] <= 200 else 5)
    rxp = lambda z: flx + (z + P0["w"] / 2) * sp
    ryp = lambda y: top + 30 + (y - (P0["yc"] - P0["h"] / 2)) * sp
    K.set_view(True)
    rect(rxp(-P0["w"] / 2), ryp(P0["yc"] - P0["h"] / 2), P0["w"] * sp, P0["h"] * sp, fill=COL_FL, lw=0.1)
    for y_ in P0["holes"]:
        circle(rxp(0), ryp(y_), g["plate_hole_d"] / 2 * sp, fill=white, lw=0.1)
        rect(rxp(-fa / 2), ryp(y_ - fb / 2), fa * sp, fb * sp, lw=0.2, dash=(2, 1.5))
    K.set_view(False)
    for y_ in P0["holes"]:
        K.centerline(rxp(-P0["w"] / 2 - 6), ryp(y_), rxp(P0["w"] / 2 + 6), ryp(y_))
    K.centerline(rxp(0), ryp(P0["yc"] - P0["h"] / 2) - 6, rxp(0), ryp(P0["yc"] + P0["h"] / 2) + 6)
    HM(rxp(-P0["w"] / 2), rxp(P0["w"] / 2), ryp(P0["yc"] + P0["h"] / 2) + D1, f"{P0['w']:g}",
       ryp(P0["yc"] + P0["h"] / 2), ryp(P0["yc"] + P0["h"] / 2))
    yyp = [P0["yc"] - P0["h"] / 2] + P0["holes"] + [P0["yc"] + P0["h"] / 2]
    vchain(rxp(P0["w"] / 2) + D1, [ryp(v) for v in yyp], [rxp(P0["w"] / 2)] * len(yyp),
           [f"{b - a:g}" for a, b in zip(yyp, yyp[1:])], size=K.F_DIM_FRAME)
    T(rxp(0), ryp(P0["yc"] + P0["h"] / 2) + 44, f"t = {P0['t']:g}, Ø{g['plate_hole_d']:g}, welded to leg ({len(g['plates_l'])} pcs.)",
      8, align="c")
    view_title(rxp(0), top - 96, "PLATE 1A", f"1:{2 if P0['h'] <= 200 else 5}")
    # ------------------------------------------------ TRAY (2) - FLAT PATTERN 1:10
    s10 = MM / 10
    outline, (bx0, by0, bx1, by1), holes, (F, WF) = tray_flat(g, True)
    tx0 = K.IX0 + 70
    tyb = K.VIEW_BOT - 52
    TX = lambda u: tx0 + u * s10
    TY = lambda v: tyb - v * s10                                    # DXF y aukštyn
    K.set_view(True)
    draw_geom(outline, TX, TY, fill=COL_BODY, lw=0.1)
    K.set_view(False)
    line(TX(bx0), TY(by0), TX(bx1), TY(by0), 0.2, HexColor("#C00000"), dash=(3, 1.5))
    line(TX(bx0), TY(by1), TX(bx1), TY(by1), 0.2, HexColor("#C00000"), dash=(3, 1.5))
    line(TX(bx0), TY(by0), TX(bx0), TY(by1), 0.2, HexColor("#C00000"), dash=(3, 1.5))
    line(TX(bx1), TY(by0), TX(bx1), TY(by1), 0.2, HexColor("#C00000"), dash=(3, 1.5))
    for hx, hy in holes:
        circle(TX(hx), TY(hy), 1.6 * s10 + 0.5, fill=white, lw=0.1)
    if g.get("logo") is not None:
        draw_geom(g["cut"], lambda x: TX(bx0 + x), lambda y: TY(by1 - y), fill=white, lw=0.1)
        K.c.saveState(); K.c.setStrokeColor(BLUE); K.c.setLineWidth(0.1)
        for sx, sy in g["studs"]:
            K.c.circle(TX(bx0 + sx), K.H - TY(by1 - sy), max(0.8, g["mark_d"] / 2 * s10), stroke=1, fill=0)
        K.c.restoreState()
    hchain(TY(WF) - D1, [TX(0), TX(bx0), TX(bx1), TX(F)], [TY(WF)] * 4, [f"{bx0:g}", f"{W:g}", f"{F - bx1:g}"], size=K.F_DIM_FRAME)
    HM(TX(0), TX(F), TY(WF) - D2, f"{F:g}", TY(WF), TY(WF))
    vchain(TX(F) + D1, [TY(WF), TY(by1), TY(by0), TY(0)], [TX(bx1)] * 4, [f"{WF - by1:g}", f"{H:g}", f"{by0:g}"],
           size=K.F_DIM_FRAME)
    VM(TX(F) + D2, TY(WF), TY(0), TX(F), f"{WF:g}")
    xs_ = [0] + sorted(set(hx for hx, _ in holes)) + [F]
    hchain(TY(0) + D1, [TX(v) for v in xs_], [TY(holes[0][1])] * len(xs_), [f"{b - a:.0f}" for a, b in zip(xs_, xs_[1:])],
           size=K.F_DIM_FRAME)
    T(TX(F / 2), TY(0) + 34, f"Alu {t:g}; bend lines {W:g} x {H:g} (red), flanges {g['PD'] - t:g} from bend line, sides inside;", 7.5,
      align="c", color=K.GREY)
    T(TX(F / 2), TY(0) + 44, f"Ø3.2 {g['screw_edge']:g} from edge; cut-out + {g['cut_gap']:g}; D{g['mark_d']:g} blue = studs; leg cut-outs wall side",
      7.5, align="c", color=K.GREY)
    view_title(TX(F / 2), TY(WF) - 66, "FRONT A (2) - FLAT PATTERN, FACE OUT", "1:10  (back B (3) = mirror, wall side left)")
    # ------------------------------------------------ BASE (6) + INSERT (4) 1:5
    if g.get("logo") is not None:
        bxa, bya, bxb, byb = g["base"].bounds
        avail_w = K.IX1 - (TX(F) + 120) - 20
        nb = nice_scale(avail_w, bxb - bxa, (4, 5, 6, 8, 10, 12, 15, 20))
        sb = MM / nb
        BX = lambda x: TX(F) + 130 + (x - bxa) * sb
        BYy = lambda y: K.VIEW_BOT - 70 - (byb - bya) * sb + (y - bya) * sb
        K.set_view(True)
        draw_geom(g["base"], BX, BYy, fill=COL_BASE, lw=0.1)
        draw_geom(g["logo"], BX, BYy, fill=COL_PLEX, lw=0.1, dash=([2, 1.5], 0))
        for x_, y_ in g["studs"]:
            circle(BX(x_), BYy(y_), g["hole_d"] / 2 * sb, fill=white, lw=0.1)
        K.set_view(False)
        HM(BX(bxa), BX(bxb), BYy(byb) + D1, f"{bxb - bxa:.0f}", BYy(byb), BYy(byb))
        VM(BX(bxa) - D1, BYy(bya), BYy(byb), BX(bxa), f"{byb - bya:.0f}")
        K.balloon_auto(BX(g["studs"][0][0]), BYy(g["studs"][0][1]), f"{len(g['studs'])} x Ø{g['hole_d']:g}", kind="tag")
        T(BX((bxa + bxb) / 2), BYy(byb) + 40, f"base 6 = contour + {g['base_off']:g} (round); Ø{g['hole_d']:g} at {g['hole_off']:g}, "
          f"~{g['hole_pitch']:g}; insert 4 (- - -) glued", 7.5, align="c", color=K.GREY)
        view_title(BX((bxa + bxb) / 2), BYy(bya) - 40, "BASE 6 + INSERT 4 (A, from outside)", f"1:{nb:g}  (B = mirror)")

    def detail(X_P6, BY0, W_P6, BH):
        K.main_data(X_P6, BY0, W_P6, BH, [
            ["Module", f"Kaisen {g['led_name']}"],
            ["Mounting", "top + bottom members"],
            ["Qty / pitch", f"{g['led_n']} pcs., {g['led_step']:.1f} mm (table {g['led_p']:g})"],
            ["Kaisen table", f"{g['led_lux']} lx" + (" - depth < table min!" if g["led_warn"] else "")],
            ["Power total", f"{g['led_W']:.1f} W"],
            ["PSU", f"{g['psu_name']}, place:"],
            ["Cable", g["cable"] or "through leg -> plate:"]], title="LED (8)", lab_w=64)

    cut = [["1.1", f"Top member + leg {prof(fa, fb, ft)}", "Alu EN AW-6060", g["frame_finish"] or "", f"1 x {g['L_h']:.0f} mm"],
           ["1.2", f"Bottom member + leg {prof(fa, fb, ft)}", "Alu EN AW-6060", g["frame_finish"] or "", f"1 x {g['L_h']:.0f} mm"],
           ["1.3", f"Vertical {prof(fa, fb, ft)}", "Alu EN AW-6060", g["frame_finish"] or "", f"2 x {g['L_v']:.0f} mm"],
           ["1A", f"Plate {P0['w']:g}x{P0['h']:g}x{P0['t']:g}, Ø{g['plate_hole_d']:g}", "Alu", g["frame_finish"] or "",
            f"{len(g['plates_l'])} pcs."],
           ["", "Frame profile total", "", "", f"{g['prof_len']:.0f} mm (+ cut allowance)"],
           [8, f"LED Kaisen {g['led_name']}", "12 V", "6500 K", f"{g['led_n']} pcs."],
           ["8A", "PSU", g["psu_name"], "IP67", "1 pc."],
           ["8B", "Cable 2 x 0.75 (LED -> PSU)", "", "", "length:"]]
    md = [["Frame outer", f"{FW:g} x {FH:g} mm"],
          ["Profile", f"{prof(fa, fb, ft)} Alu, centre of depth"],
          ["Legs", f"top + bottom members, +{LL:g} out of body"],
          ["Leg axes", f"{H - 2 * g['ax']:g} mm (from box edge {g['ax']:g})"],
          ["Joints", "welded (TIG), ground"],
          ["Trays", f"2 x folded Alu {t:g}, flat {F:g} x {WF:g}"],
          ["Finish", g["frame_finish"] or ""],
          ["Qty", f"{g['qty']}"]]
    band(g, "2 / 3", " - FRAME + LED + PARTS", md, cut, detail)
    K.save(out)


# ===================================================================== DXF
def tray_flat(g, wall_right=True):
    """padėklo išklotinė (folded v173: lenkimo linijos W x H, flanšai PD - t, šonai t trumpesni), face out (y žemyn -> y aukštyn
    DXF'e). Sienos pusės flanše - išpjovos kojoms (pusė kojos + clear). Grąžina (cut polygon, bend rect, holes)."""
    W, H, t, PD = g["w"], g["h"], g["t"], g["PD"]
    fa, fb, ft = g["frame"]
    FL = PD - t
    x0, x1, y0, y1 = FL, FL + W, FL, FL + H
    F, WF = W + 2 * FL, H + 2 * FL
    outline = Polygon([(x0, 0), (x1, 0), (x1, y0 + t), (F, y0 + t), (F, y1 - t), (x1, y1 - t), (x1, WF), (x0, WF),
                       (x0, y1 - t), (0, y1 - t), (0, y0 + t), (x0, y0 + t)])
    # kojų išpjovos sienos pusės (šoniniame) flanše: koja fb aukščio, gylyje - fa / 2 + clear nuo sandūros
    notch_d = fa / 2 + g["clear"]
    notches = []
    for yax in (g["ax"], H - g["ax"]):
        yc = y1 - yax                                                 # DXF y aukštyn: viršus = y1
        if wall_right:
            notches.append(sbox(F - notch_d, yc - fb / 2 - g["clear"], F + 1, yc + fb / 2 + g["clear"]))
        else:
            notches.append(sbox(-1, yc - fb / 2 - g["clear"], notch_d, yc + fb / 2 + g["clear"]))
    outline = outline.difference(unary_union(notches))
    holes = [(x0 + u, v) for u in g["scr_x"] for v in (g["screw_edge"], WF - g["screw_edge"])]
    return outline, (x0, y0, x1, y1), holes, (F, WF)


def write_dxf(g, path):
    import ezdxf
    doc = ezdxf.new("R2010", setup=True); doc.units = ezdxf.units.MM
    msp = doc.modelspace()
    for name, col, lt in (("CUT", 7, "CONTINUOUS"), ("BEND_UP_90", 1, "DASHED"), ("HOLES_D3.2", 3, "CONTINUOUS"),
                          ("CUTOUT_LOGO", 7, "CONTINUOUS"), ("MARK_D6_STUDS", 5, "CONTINUOUS"),
                          ("PLEXI_BASE_3MM", 6, "CONTINUOUS"), ("PLEXI_BASE_HOLES_D8", 6, "CONTINUOUS"),
                          ("PLEXI_INSERT", 4, "CONTINUOUS"), ("TEXT", 2, "CONTINUOUS")):
        doc.layers.add(name, color=col, linetype=lt)

    def pl(geo, layer, ox, oy, flip_y=None, mirror_w=None):
        for pg in getattr(geo, "geoms", [geo]):
            if pg.is_empty:
                continue
            for ring in [pg.exterior] + list(pg.interiors):
                pts = []
                for x, y in ring.coords:
                    if mirror_w is not None:
                        x = mirror_w - x
                    if flip_y is not None:
                        y = flip_y - y
                    pts.append((ox + x, oy + y))
                msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": layer})

    def txt(s_, x, y, hgt=12):
        msp.add_text(s_, height=hgt, dxfattribs={"layer": "TEXT"}).set_placement((x, y))

    W, H = g["w"], g["h"]
    gap = 120
    ox = 0
    for side, wall_right in (("A", True), ("B", False)):
        outline, (x0, y0, x1, y1), holes, (F, WF) = tray_flat(g, wall_right)
        pl(outline, "CUT", ox, 0)
        msp.add_lwpolyline([(ox + x0, y0), (ox + x1, y0), (ox + x1, y1), (ox + x0, y1)], close=True,
                           dxfattribs={"layer": "BEND_UP_90"})
        for hx, hy in holes:
            msp.add_circle((ox + hx, hy), 1.6, dxfattribs={"layer": "HOLES_D3.2"})
        if g.get("logo") is not None:
            # face out: A - kaip iš priekio; B - iš B pusės (logotipas skaitomas, veidrodis A atžvilgiu)
            for pg in getattr(g["cut"], "geoms", [g["cut"]]):
                for ring in [pg.exterior] + list(pg.interiors):
                    pts = [(ox + x0 + ((W - x) if side == "B" else x), y1 - y) for x, y in ring.coords]
                    msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": "CUTOUT_LOGO"})
            for sx, sy in g["studs"]:
                msp.add_circle((ox + x0 + ((W - sx) if side == "B" else sx), y1 - sy), g["mark_d"] / 2,
                               dxfattribs={"layer": "MARK_D6_STUDS"})
        txt(f"{side}: FOLDED {W:g}x{H:g}x{g['PD']:g} Alu {g['t']:g} - FLAT {F:g}x{WF:g} - FACE OUT"
            + (" - wall side right" if wall_right else " - wall side left"), ox, -30)
        ox += F + gap
    # plexi: pagrindai ir įdėklai (A ir B), po padėklais
    if g.get("logo") is not None:
        bx0, by0, bx1, by1 = g["base"].bounds
        oy = -(by1 - by0) - 120
        cx = 0
        for side in ("A", "B"):
            mw = (bx0 + bx1) if side == "B" else None
            for pg in g["base_parts"]:
                for ring in [pg.exterior] + list(pg.interiors):
                    pts = [(cx + ((mw - x) if mw else x) - bx0, oy + (by1 - y)) for x, y in ring.coords]
                    msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": "PLEXI_BASE_3MM"})
            for sx, sy in g["studs"]:
                msp.add_circle((cx + ((mw - sx) if mw else sx) - bx0, oy + (by1 - sy)), g["hole_d"] / 2,
                               dxfattribs={"layer": "PLEXI_BASE_HOLES_D8"})
            txt(f"BASE {side} {g['base_t']:g} mm plexi - {len(g['studs'])} x D{g['hole_d']:g}", cx, oy - 30)
            cx += (bx1 - bx0) + gap
            if g["ins_t"] > 0:
                lx0, ly0, lx1, ly1 = g["logo"].bounds
                for pg in getattr(g["logo"], "geoms", [g["logo"]]):
                    for ring in [pg.exterior] + list(pg.interiors):
                        pts = [(cx + (((lx0 + lx1) - x) if side == "B" else x) - lx0, oy + (ly1 - y)) for x, y in ring.coords]
                        msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": "PLEXI_INSERT"})
                txt(f"INSERT {side} {g['ins_t']:g} mm plexi - GLUED to base", cx, oy - 30)
                cx += (lx1 - lx0) + gap
    doc.saveas(path)
    return path


# ===================================================================== 3 LAPAS - ASSEMBLY / EXPLODED VIEW (v199)
COL_NUT = HexColor("#9C9C9C")


def _slab(sc, geo, w0, w1, col, xf, edge=None):
    """shapely (u, v) kūnas w0..w1, abi plokštumos (r3d atmeta nugarines - plonoms detalėms reikia abiejų)"""
    sc.extrude_xy(geo, w0, w1, col, col, edge=edge, xf=xf)
    for gg in getattr(geo, "geoms", [geo]):
        if gg.is_empty:
            continue
        ext = [xf(x, y, w0) for x, y in list(gg.exterior.coords)[:-1]]
        hol = [[xf(x, y, w0) for x, y in list(r.coords)[:-1]] for r in gg.interiors]
        n = sc._nrm(xf(0, 0, w0), xf(1, 0, w0), xf(0, 1, w0), ref=xf(0, 0, w0 - 1), base=xf(0, 0, w0))
        sc.face(ext, n, col, edge, holes=hol, tile=False)


def _hexagon(x, y, s):
    r = s / math.sqrt(3)
    return Polygon([(x + r * math.cos(math.radians(30 + 60 * k)), y + r * math.sin(math.radians(30 + 60 * k))) for k in range(6)])


def exploded(g, box, yaw=-58, pitch=18):
    """sprogstamasis vaizdas išilgai gylio (z): padėklas A - įdėklas A - pagrindas A (+ veržlės) - rėmas + LED -
    pagrindas B - įdėklas B - padėklas B. Grąžina {pozicija: 2D taškas (lapo koord.)} balionams."""
    import r3d
    W, H, D, t = g["w"], g["h"], g["depth"], g["t"]
    fa, fb, ft = g["frame"]
    LL, PR = g["leg_len"], g["proj"]
    PLw, PLh, PLt = g["plate"]
    cl, bt, it_ = g["clear"], g["base_t"], g["ins_t"]
    x0 = t + cl
    FH, FW = g["FH"], g["FW"]
    xr, xf = x0 + FW, W + LL
    M = max(W, H)
    e_base, e_ins, e_tray, e_nut = 0.55 * M, 0.95 * M, 1.45 * M, 0.3 * M
    stud_l = bt + 8
    sc = r3d.Scene(yaw=yaw, pitch=pitch)
    lg = g.get("logo")
    anc = {}

    def side_xf(sgn, dz):
        """side koordinatės (u, v = lapo x, y žemyn) + w (gylis nuo centro į tą pusę) -> pasaulis"""
        if sgn > 0:
            return lambda u, v, w: (u, H - v, w + dz)
        return lambda u, v, w: (W - u, H - v, -(w + dz))

    for sgn in (1, -1):
        sd = "A" if sgn > 0 else "B"
        # ---- padėklas (2 / 3): priekis su išpjova + 4 flanšai, sienos pusės flanše kojų išpjovos, ilgasriegiai
        xp = side_xf(sgn, e_tray)
        face_geo = sbox(0, 0, W, H)
        if lg is not None:
            face_geo = face_geo.difference(g["cut"])
        _slab(sc, face_geo, D / 2 - t, D / 2, COL_BODY, xp, edge=EDGE)
        zs = lambda w, dz=e_tray: sgn * (w + dz)
        for y0_ in (0, H - t):                                      # viršus / apačia
            z_a, z_b = sorted((zs(0), zs(D / 2 - t)))
            sc.box((0, y0_, z_a), (W, 0, 0), (0, t, 0), (0, 0, z_b - z_a), COL_BODY, edge=EDGE)
        z_a, z_b = sorted((zs(0), zs(D / 2 - t)))
        sc.box((0, t, z_a), (t, 0, 0), (0, H - 2 * t, 0), (0, 0, z_b - z_a), COL_BODY, edge=EDGE)   # tolimas šonas
        nd = fa / 2 + cl
        wall = sbox(t, 0, H - t, D / 2 - t)
        for ya in (g["ax"], H - g["ax"]):
            wall = wall.difference(sbox(ya - fb / 2 - cl, 0, ya + fb / 2 + cl, nd))
        _slab(sc, wall, W - t, W, COL_BODY, lambda u, v, w: (w, u, sgn * (v + e_tray)), edge=EDGE)
        if lg is not None:
            for (u, v) in g["studs"]:
                _slab(sc, Point(u, v).buffer(3, 3), D / 2 - t - stud_l, D / 2 - t, COL_STUD, xp)
        anc[2 if sgn > 0 else 3] = xp(W * 0.12, H * 0.82, D / 2 if sgn > 0 else D / 2 - t)
        # varžtai (10) - viršutinis flanšas, |z| = 7 nuo siūlės, ištraukti į viršų
        for x_ in g["scr_x"]:
            z_ = sgn * (7 + e_tray)
            sh = Point(x_, z_).buffer(1.6, 3)
            hd = Point(x_, z_).buffer(3.2, 3)
            up = 0.08 * M
            sc.extrude_xy(sh, H + up, H + up + 12, COL_STUD, COL_STUD, xf=lambda a, b, c: (a, c, b))
            _slab(sc, hd, H + up + 12, H + up + 14, COL_STUD, lambda a, b, c: (a, c, b))
        anc["10" + sd] = (g["scr_x"][len(g["scr_x"]) // 2], H + 0.08 * M + 13, sgn * (7 + e_tray))
        if lg is None:
            continue
        # ---- pagrindas (6 / 7) su Ø8, įdėklas (4 / 5) ant jo išorės, veržlės (9) vidinėje pusėje
        xb = side_xf(sgn, e_base)
        holes = unary_union([Point(u, v).buffer(g["hole_d"] / 2, 4) for (u, v) in g["studs"]])
        _slab(sc, g["base"].difference(holes), D / 2 - t - bt, D / 2 - t, COL_BASE, xb, edge=EDGE)
        xi = side_xf(sgn, e_ins)
        _slab(sc, g["logo"], D / 2 - t, D / 2 - t + it_, COL_PLEX, xi, edge=EDGE)
        xn = side_xf(sgn, e_nut)
        for (u, v) in g["studs"]:
            _slab(sc, _hexagon(u, v, 10).difference(Point(u, v).buffer(3, 3)), D / 2 - t - bt - 5, D / 2 - t - bt,
                  COL_NUT, xn)
        rp = g["base"].difference(g["logo"].buffer(4)).representative_point()
        anc[6 if sgn > 0 else 7] = xb(rp.x, rp.y, D / 2 - t if sgn > 0 else D / 2 - t - bt)
        lp = g["logo"].representative_point()
        anc[4 if sgn > 0 else 5] = xi(lp.x, lp.y, D / 2 - t + it_ if sgn > 0 else D / 2 - t)
        su, sv = max(g["studs"], key=lambda p: p[0] - p[1])
        anc["9" + sd] = xn(su, sv, D / 2 - t - bt - 5)
        anc["9s" + sd] = xp(su, sv, D / 2 - t - stud_l)
        anc["ax" + sd] = [(xp(u, v, D / 2 - t - stud_l), xn(u, v, D / 2 - t - bt - 5)) for (u, v) in
                          (min(g["studs"], key=lambda p: p[0]), max(g["studs"], key=lambda p: p[0]))]
    # ---- rėmas (1) + kojos + plokštės (1A) + LED (8), gylio centre
    for ys in (x0, x0 + FH - fb):
        sc.box((x0, H - ys - fb, -fa / 2), (xf - x0, 0, 0), (0, fb, 0), (0, 0, fa), COL_FRAME, edge=EDGE)
    for xx in (x0, xr - fa):
        sc.box((xx, H - x0 - FH + fb, -fa / 2), (fa, 0, 0), (0, FH - 2 * fb, 0), (0, 0, fa), COL_FRAME, edge=EDGE)
    for P in g["plates_l"]:
        sc.box((xf, H - P["yc"] - P["h"] / 2, -P["w"] / 2), (PLt, 0, 0), (0, P["h"], 0), (0, 0, P["w"]), COL_FL, edge=EDGE)
    led_x = [x0 + fa + g["led_step"] * (i + 0.5) for i in range(g["led_n_row"])]
    for k_, ys in enumerate((x0 + fb, x0 + FH - fb - 8)):
        for lx in led_x:
            sc.box((lx - 11, H - ys - 8, -11), (22, 0, 0), (0, 8, 0), (0, 0, 22), COL_LED, edge=EDGE)
    anc["1"] = (x0 + FW * 0.3, H - x0 - fb / 2, fa / 2)
    anc["1A"] = (xf + PLt, H - g["plates_l"][0]["yc"], 0)
    anc["8"] = (led_x[0], H - (x0 + FH - fb - 8), 11)
    sc.render(box)
    V = sc.V
    to2 = lambda p: (V.S(*p)[0], K.H - V.S(*p)[1])
    return {k: ([(to2(a), to2(b)) for a, b in v] if str(k).startswith("ax") else to2(v)) for k, v in anc.items()}


def sheet3(g, out):
    K.set_band(len(bom1(g)) + 1)
    K.init(out + ".tmp", "sheet3")
    K.frame()
    top = K.IY0 + 60
    col_w = 250                                                     # surinkimo eiga dešinėje
    vx0, vx1 = K.IX0 + 20, K.IX1 - col_w - 30
    box = (vx0, top, vx1 - vx0, K.VIEW_BOT - top - 30)
    A = exploded(g, box)
    reg = (K.IX0 + 4, K.IY0 + 4, vx1 + 10, K.VIEW_BOT - 4)
    for sd in ("A", "B"):                                           # surinkimo ašys: ilgasriegis -> skylė -> veržlė
        for a, b in A.get("ax" + sd, []):
            K.centerline(a[0], a[1], b[0], b[1])
    for key, lab in (("1", "1"), ("1A", "1A"), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), ("8", 8),
                     ("9A", 9), ("9B", 9), ("10A", 10), ("10B", 10)):
        if key in A:
            K.balloon_auto(A[key][0], A[key][1], lab, region=reg)
    view_title((vx0 + vx1) / 2, top - 22, "ASSEMBLY - EXPLODED VIEW", "ILLUSTRATIVE - NOT TO SCALE; parts moved apart along depth")
    # ------------------------------------------------ surinkimo eiga
    cx = K.IX1 - col_w - 10
    view_title(cx + col_w / 2, top - 22, "ASSEMBLY SEQUENCE", "order of work")
    fa, fb, ft = g["frame"]
    steps = [
        ("FRAME (1)", [f"Weld members {prof(fa, fb, ft)}: top / bottom = legs", "+ 2 verticals between them; weld plates 1A", "to legs, grind welds (sheet 2)."]),
        ("LED (8)", [f"Fix {g['led_n']} x {g['led_name']} on top + bottom", "members, wire to PSU; cable through leg", "and plate."]),
        ("TRAYS A (2) / B (3)", ["Laser cut flat (DXF), bend flanges 90 deg,", f"weld studs (9) at blue D{g['mark_d']:g} marks on", "the inside face."]),
        ("INSERT -> BASE", [f"Glue insert A (4) on base A (6),", "insert B (5) on base B (7);", "insert centred on base contour."]),
        ("BASE -> TRAY", ["Put base on studs from inside, insert", f"goes through cut-out (gap {g['cut_gap']:g} around);", "tighten nuts (9)."]),
        ("CLOSE", ["Slide tray A over frame (legs in flange", "notches), then tray B; seam at centre;", f"screws (10) in top + bottom flanges."]),
    ]
    y = top + 20
    for i, (h_, ls) in enumerate(steps, 1):
        T(cx + 6, y + 12, f"STEP {i} - {h_}", 8.5, font="FB")
        for j, l_ in enumerate(ls):
            T(cx + 6, y + 25 + j * 11, l_, 7.5)
        y += 25 + len(ls) * 11 + 10
    T(cx, y + 4, "Side B = mirror of side A.", 7.5, color=K.GREY)
    T(cx, y + 15, "Balloons = BOM positions.", 7.5, color=K.GREY)
    band(g, "3 / 3", " - ASSEMBLY", main_data1(g), bom1(g), detail_b(g))
    K.save(out)


def main(spec_path, out):
    S = dict(DEF); S.update(json.load(open(spec_path, encoding="utf-8")))
    if S.get("logo") and not os.path.isabs(S["logo"]["file"]):     # logotipo kelias - nuo spec failo
        S["logo"] = dict(S["logo"], file=os.path.join(os.path.dirname(os.path.abspath(spec_path)), S["logo"]["file"]))
    global COL_BODY, COL_FRAME, COL_FL
    if str(S.get("body_finish", "")).upper().startswith("RAL"):
        COL_BODY = HexColor(K.ralhex(S["body_finish"]))
    if str(S.get("frame_finish", "")).upper().startswith("RAL"):
        COL_FRAME = COL_FL = HexColor(K.ralhex(S["frame_finish"]))
    K.F_DIM_FRAME = K.F_DIM_MAIN
    g = geom(S)
    p1, p2, p3 = out + ".1.pdf", out + ".2.pdf", out + ".3.pdf"
    for fn, pp in ((sheet1, p1), (sheet2, p2), (sheet3, p3)):                    # 2 praėjimai - automatinis žymėjimas
        K.auto_begin("collect"); K.AUTO["region"] = None
        fn(g, pp)
        pl_ = K.auto_place(pp)
        K.auto_begin("draw", pl_); K.AUTO["region"] = None
        fn(g, pp)
        K.auto_begin(None)
    import pymupdf as fitz
    d = fitz.open()
    for pp in (p1, p2, p3):
        d.insert_pdf(fitz.open(pp))
    d.save(out, garbage=3, deflate=True); d.close()
    K.pdf_fix_fonts(out)
    for pp in (p1, p2, p3, p1 + ".tmp", p2 + ".tmp", p3 + ".tmp"):
        os.path.exists(pp) and os.remove(pp)
    dxf = os.path.splitext(out)[0] + "_gamyba.dxf"
    write_dxf(g, dxf)
    print("OK", out, dxf)
    print(f"  rėmas {prof(*g['frame'])} (PASIŪLYMAS pagal dydį), skersinis+koja {g['L_h']:.0f}, statmuo {g['L_v']:.0f}; "
          f"LED {g['led_n']} x {g['led_name']} ({g['led_W']:.1f} W), {g['psu_name']}; svoris {g['kg']:.1f} kg")
    if g.get("logo") is not None:
        print(f"  logotipas {g['logo_w']:.0f} x {g['logo_h']:.0f}, pagrindas {len(g['base_parts'])} d., ilgasriegiai {len(g['studs'])} / pusei")
    if g["led_warn"]:
        print("  !", g["led_warn"])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
