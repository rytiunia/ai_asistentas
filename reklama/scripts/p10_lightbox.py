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


# ===================================================================== LAPAS
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
        if pg.is_empty:
            continue
        for ring in [pg.exterior] + list(pg.interiors):
            pts = [(X(x), K.H - Y(y)) for x, y in ring.coords]
            p.moveTo(*pts[0])
            for q in pts[1:]:
                p.lineTo(*q)
            p.close()
    c.drawPath(p, stroke=1, fill=1 if fill is not None else 0, fillMode=0)
    c.restoreState()


def sheet(g, out):
    W, H, D, t = g["w"], g["h"], g["depth"], g["t"]
    fa, fb, ft = g["frame"]
    LL, PR = g["leg_len"], g["proj"]
    PLt = g["plate"][2]
    K.set_band(len(bom(g)) + 1)
    K.init(out + ".tmp", "P10 lightbox")
    K.frame()
    s = MM / g["scale_ga"]
    sl = f"1:{g['scale_ga']:g}"
    top = K.IY0 + 70
    Yv = lambda y: top + y * s
    lg = g.get("logo")

    def front(fx, mirror):
        X = (lambda x: fx + (W + PR - x) * s) if mirror else (lambda x: fx + x * s)
        xl, xr = (X(W), X(0)) if mirror else (X(0), X(W))
        K.set_view(True)
        rect(xl, Yv(0), W * s, H * s, fill=COL_BODY, lw=0.1)
        if lg is not None:
            Xm = (lambda x: X(W - x)) if mirror else X                # B pusė - logotipas skaitomas iš B (veidrodis lape)
            draw_geom(g["logo"], Xm, Yv, fill=COL_PLEX, lw=0.1)
        for P in g["plates_l"]:
            for y_ in P["holes"]:
                a_, b_ = sorted((X(W), X(W + LL)))
                rect(a_, Yv(y_ - fb / 2), LL * s, fb * s, fill=COL_FRAME, lw=0.1)
            a2, _ = sorted((X(W + LL), X(W + PR)))
            rect(a2, Yv(P["yc"] - P["h"] / 2), PLt * s, P["h"] * s, fill=COL_FL, lw=0.1)
        K.set_view(False)
        for y_ in (g["ax"], H - g["ax"]):
            K.centerline(X(W - 20), Yv(y_), X(W + PR + 8), Yv(y_))
        xs_ = sorted([X(0), X(W), X(W + LL), X(W + PR)])
        labs = [f"{W:g}", f"{LL:g}", f"{PLt:g}"]
        hchain(Yv(H) + 16, xs_, [Yv(H)] * 4, labs[::-1] if mirror else labs, size=K.F_DIM_MAIN)
        hdim(xs_[0], xs_[-1], Yv(H) + 36, f"{W + PR:g}", Yv(H), Yv(H), size=K.F_DIM_MAIN)
        if lg is not None:
            lx0 = g["logo_x"]; lx1 = lx0 + g["logo_w"]
            a_, b_ = (X(W - lx1), X(W - lx0)) if mirror else (X(lx0), X(lx1))
            pa, pb = sorted((a_, b_))
            hchain(Yv(0) - 16, [xl, pa, pb, xr], [Yv(0), Yv(g["logo_y"]), Yv(g["logo_y"]), Yv(0)],
                   [f"{(pa - xl) / s:.0f}", f"{g['logo_w']:.0f}", f"{(xr - pb) / s:.0f}"], size=K.F_DIM_MAIN)
        xo = xl - 16 if not mirror else xr + 16
        ly0, ly1 = (g["logo_y"], g["logo_y"] + g["logo_h"]) if lg is not None else (None, None)
        if lg is not None:
            vchain(xo, [Yv(0), Yv(ly0), Yv(ly1), Yv(H)], [xl if not mirror else xr] * 4,
                   [f"{ly0:.0f}", f"{g['logo_h']:.0f}", f"{H - ly1:.0f}"], size=K.F_DIM_MAIN)
        xo2 = xl - 36 if not mirror else xr + 36
        vchain(xo2, [Yv(0), Yv(H)], [xl if not mirror else xr] * 2, [f"{H:g}"], size=K.F_DIM_MAIN)
        return X

    # ------------------------------------------------ SIDE A | VIEW FROM WALL | SIDE B
    fxA = K.IX0 + 80
    XA = front(fxA, False)
    view_title(XA((W + PR) / 2), Yv(H) + 62, "FRONT VIEW - SIDE A", sl)
    # vaizdas iš sienos
    sxc = XA(W + PR) + 150
    Zs = lambda z: sxc + z * s
    K.set_view(True)
    TOT = g["TOT"]
    rect(Zs(-D / 2), Yv(0), D * s, H * s, fill=COL_BODY, lw=0.1)
    for P in g["plates_l"]:
        rect(Zs(-P["w"] / 2), Yv(P["yc"] - P["h"] / 2), P["w"] * s, P["h"] * s, fill=COL_FL, lw=0.1)
        for y_ in P["holes"]:
            circle(Zs(0), Yv(y_), g["plate_hole_d"] / 2 * s, fill=white, lw=0.1)
    K.set_view(False)
    K.centerline(Zs(0), Yv(-8), Zs(0), Yv(H + 8))
    P0 = g["plates_l"][0]; PLw = P0["w"]
    hy_ = sorted(y for P in g["plates_l"] for y in P["holes"])
    ptop = min(P["yc"] - P["h"] / 2 for P in g["plates_l"]); pbot = max(P["yc"] + P["h"] / 2 for P in g["plates_l"])
    yy = [ptop] + hy_ + [pbot]
    vchain(Zs(PLw / 2) + 16, [Yv(v) for v in yy], [Zs(PLw / 2)] * len(yy), [f"{b - a:g}" for a, b in zip(yy, yy[1:])],
           size=K.F_DIM_MAIN)
    vchain(Zs(PLw / 2) + 36, [Yv(ptop), Yv(pbot)], [Zs(PLw / 2)] * 2, [f"{pbot - ptop:g}"], size=K.F_DIM_MAIN)
    hdim(Zs(-PLw / 2), Zs(PLw / 2), Yv(H) + 16, f"{PLw:g}", Yv(pbot), Yv(pbot), size=K.F_DIM_MAIN)
    hdim(Zs(-D / 2), Zs(D / 2), Yv(0) - 16, f"{D:g}", Yv(0), Yv(0), size=K.F_DIM_MAIN)
    K.balloon_auto(Zs(0), Yv(hy_[0]), f"{len(hy_)} x Ø{g['plate_hole_d']:g}", kind="tag", region=None)
    view_title(Zs(0), Yv(H) + 62, "VIEW FROM WALL", sl)
    # B pusė
    fxB = Zs(0) + 120
    XB = front(fxB, True)
    view_title(XB((W + PR) / 2), Yv(H) + 62, "FRONT VIEW - SIDE B", sl)

    # ------------------------------------------------ 2 eilė: 3 mm PAGRINDAS + ILGASRIEGIAI (A, iš vidaus) | 3D A | 3D B
    y2 = Yv(H) + 96
    h2 = K.BAND_Y - y2 - 46                                           # vieta iki juostos (pavadinimai po vaizdais)
    if lg is not None:
        bx0, by0, bx1, by1 = g["base"].bounds
        mg = 12
        sb = min(300 / (bx1 - bx0 + 2 * mg), h2 / (by1 - by0 + 2 * mg))
        nice = [1, 2, 2.5, 4, 5, 8, 10, 12, 15, 20, 25]
        nb = next(v for v in nice if MM / v <= sb); sb = MM / nb
        X2 = lambda x: K.IX0 + 60 + (bx1 + mg - x) * sb              # vaizdas iš vidaus - veidrodis
        Y2 = lambda y: y2 + (y - by0 + mg) * sb
        K.set_view(True)
        draw_geom(g["base"], X2, Y2, fill=HexColor("#EDEDE8"), lw=0.1)
        draw_geom(g["cut"], X2, Y2, fill=white, lw=0.1)
        for x_, y_ in g["studs"]:
            circle(X2(x_), Y2(y_), g["hole_d"] / 2 * sb, fill=white, lw=0.1)
            K.c.saveState(); K.c.setStrokeColor(BLUE); K.c.setLineWidth(0.1)
            K.c.circle(X2(x_), K.H - Y2(y_), g["mark_d"] / 2 * sb, stroke=1, fill=0); K.c.restoreState()
        K.set_view(False)
        hdim(X2(bx1), X2(bx0), Y2(by1) + 16, f"{bx1 - bx0:.0f}", Y2(by1), Y2(by1), size=K.F_DIM_MAIN)
        vchain(X2(bx1) - 16, [Y2(by0), Y2(by1)], [X2(bx1)] * 2, [f"{by1 - by0:.0f}"], size=K.F_DIM_MAIN)
        K.balloon_auto(X2(g["studs"][0][0]), Y2(g["studs"][0][1]), f"{len(g['studs'])} x Ø{g['hole_d']:g}",
                       kind="tag", region=None)
        view_title(X2((bx0 + bx1) / 2), Y2(by1) + 40, "BASE 6 - SIDE A FROM INSIDE", f"1:{nb:g}  |  "
                   f"contour + {g['base_off']:g}, Ø{g['hole_d']:g} at {g['hole_off']:g} / ~{g['hole_pitch']:g}, "
                   f"Alu: D{g['mark_d']:g} blue marks = studs")
    # 3D A ir B
    try:
        import r3d
        bw = 230
        for k_, (yaw, lab) in enumerate(((32, "SIDE A"), (212, "SIDE B"))):
            sc = r3d.Scene(yaw=yaw, pitch=18)
            sc.box((0, 0, -D / 2), (W, 0, 0), (0, H, 0), (0, 0, D), COL_BODY, edge=EDGE)
            for y_ in (g["ax"], H - g["ax"]):
                sc.box((W, H - y_ - fb / 2, -fa / 2), (LL, 0, 0), (0, fb, 0), (0, 0, fa), COL_FRAME, edge=EDGE)
            for P in g["plates_l"]:
                sc.box((W + LL, H - P["yc"] - P["h"] / 2, -P["w"] / 2), (PLt, 0, 0), (0, P["h"], 0), (0, 0, P["w"]), COL_FL, edge=EDGE)
            if lg is not None and g["prot"] > 0:
                sc.extrude_xy(g["logo"], D / 2, D / 2 + g["prot"], COL_PLEX, COL_PLEX, edge=EDGE,
                              xf=lambda x, y, z: (x, H - y, z))
                sc.extrude_xy(g["logo"], D / 2, D / 2 + g["prot"], COL_PLEX, COL_PLEX, edge=EDGE,
                              xf=lambda x, y, z: (W - x, H - y, -z))
            box = (K.IX1 - 2 * bw - 40 + k_ * (bw + 20), y2, bw, h2)
            sc.render(box)
            view_title(box[0] + bw / 2, box[1] + box[3] + 22, "3D - " + lab, "ILLUSTRATIVE")
    except Exception as e:                                          # 3D - ne gamybai
        print("  ! 3D nepavyko:", e)

    # ------------------------------------------------ juosta: TIPINIS PJŪVIS | BOM | MAIN DATA | antraštė
    BY0 = K.BAND_Y; BH = K.IY1 - BY0
    W_P6, W_MD, W_TB = 214, 200, 272
    X_P6 = K.IX0; X_TB = K.IX1 - W_TB; X_MD = X_TB - W_MD; X_BOM = X_P6 + W_P6; W_BOM = X_MD - X_BOM
    section(g, X_P6, BY0, W_P6, BH)
    K.main_data(X_MD, BY0, W_MD, BH, main_data(g), lab_w=60)
    K.bom_table(X_BOM, BY0, W_BOM, BH, bom(g), title="PARTS LIST  (per 1 pcs.)")
    spec = {"client": g["client"], "title": g["title"], "order_no": g["order_no"], "drawing_no": g["drawing_no"],
            "sheet": "1 / 1", "rev": g["rev"], "date": g["date"]}
    K.title_block(X_TB, W_TB, spec, f"{sl} / 1:2")
    K.save(out)


def section(g, x, y, w, h):
    """PJŪVIS per išpjovos kraštą, A pusė (B - veidrodis): Alu padėklas, 3 mm pagrindas, iškištas įdėklas (priklijuotas),
    ilgasriegis + veržlė; mastelis - kad blokas būtų užpildytas"""
    K.header(x, y, w, "P10_LIGHTBOX - SECTION AT CUT-OUT (SIDE A)")
    rect(x, y + 12, w, h - 12, lw=0.6)
    t, bt, it_, pr = g["t"], g["base_t"], g["ins_t"], g["prot"]
    zin = t + bt + 8                                                 # į vidų nuo Alu išorės (z > 0 - į dėžės vidų)
    zr = pr + zin
    vr = g["hole_off"] + 22 + 12
    s2 = min((w - 90) / zr, (h - 60) / vr)
    ox = x + 28 + pr * s2                                           # Alu išorinė plokštuma
    Z = lambda z: ox + z * s2
    yb = y + 40
    Yy = lambda v: yb + (v + 12) * s2                                # v: 0 = išpjovos kraštas (Alu), < 0 - įdėklas
    vh = vr - 12
    K.set_view(True)
    rect(Z(0), Yy(g["cut_gap"]), t * s2, (vh - g["cut_gap"]) * s2, fill=COL_BODY, lw=0.1)            # 2 Alu
    rect(Z(t), Yy(-12), bt * s2, (vh + 12) * s2, fill=HexColor("#EDEDE8"), lw=0.1)                  # 6 pagrindas
    if it_ > 0:
        rect(Z(t - it_), Yy(-12), it_ * s2, 12 * s2, fill=COL_PLEX, lw=0.1)                          # 4 įdėklas
    hy = g["hole_off"]
    rect(Z(t), Yy(hy - 2), (bt + 6) * s2, 4 * s2, fill=HexColor("#B8B8B8"), lw=0.1)                 # 9 ilgasriegis
    rect(Z(t + bt), Yy(hy - 3.5), 3 * s2, 7 * s2, fill=HexColor("#8C8C8C"), lw=0.1)                  # veržlė
    K.set_view(False)
    K.centerline(Z(-pr) - 4, Yy(hy), Z(t + bt + 10), Yy(hy))
    hchain(y + 28, [Z(t - it_), Z(0), Z(t), Z(t + bt)], [Yy(-12)] * 2 + [Yy(-12)] * 2,
           [f"{pr:g}", f"{t:g}", f"{bt:g}"], size=8)
    vchain(Z(-pr) - 12, [Yy(0), Yy(hy)], [Z(t)] * 2, [f"{hy:g}"], size=8)
    reg = (x + 3, y + 15, x + w - 3, y + h - 22)
    for tx_, ty_, lab in ((Z(t / 2), Yy(vh * 0.8), 2), (Z(t - it_ / 2), Yy(-6), 4), (Z(t + bt / 2), Yy(vh * 0.55), 6),
                          (Z(t + bt + 4), Yy(hy), 9)):
        K.balloon_auto(tx_, ty_, lab, region=reg)
    T(x + w / 2, y + h - 14, f"insert {it_:g} GLUED to base; cut = contour + {g['cut_gap']:g}", 7.5, align="c", color=K.GREY)
    T(x + w / 2, y + h - 5, "side B = mirror; frame + DUOLITE at box edge", 7.5, align="c", color=K.GREY)


def bom(g):
    fa, fb, ft = g["frame"]
    P0 = g["plates_l"][0]
    W, H = g["w"], g["h"]
    rows = [[1, f"Frame + legs {prof(fa, fb, ft)}", "Alu, welded", g["frame_finish"] or "",
             f"2 x {g['L_h']:.0f} + 2 x {g['L_v']:.0f} mm"],
            ["1A", (f"Mounting plate {P0['w']:g}x{P0['h']:g}x{P0['t']:g}, Ø{g['plate_hole_d']:g}"), "Alu, welded to leg",
             g["frame_finish"] or "", f"{len(g['plates_l'])} pcs."],
            [2, f"Front (A) folded {W:g}x{H:g}x{g['PD']:g}, cut-out", f"Alu {g['t']:g} mm", g["body_finish"] or "", "1 pc."],
            [3, f"Back (B) folded {W:g}x{H:g}x{g['PD']:g}, cut-out", f"Alu {g['t']:g} mm", g["body_finish"] or "", "1 pc."]]
    if g.get("logo") is not None:
        if g["ins_t"] > 0:
            rows += [[4, f"Insert A {g['ins_t']:g} mm, glued to base", f"Plexi {g['plexi']}", g["film"] or "-",
                      f"1 pc. {g['logo'].area / 1e6:.3f} m²"],
                     [5, f"Insert B {g['ins_t']:g} mm, glued to base", f"Plexi {g['plexi']}", g["film"] or "-",
                      f"1 pc. {g['logo'].area / 1e6:.3f} m²"]]
        rows += [[6, f"Base A {g['base_t']:g} mm, {len(g['studs'])} x Ø{g['hole_d']:g}", f"Plexi {g['plexi']}", "-",
                  f"1 pc. {g['base'].area / 1e6:.3f} m²"],
                 [7, f"Base B {g['base_t']:g} mm, {len(g['studs'])} x Ø{g['hole_d']:g}", f"Plexi {g['plexi']}", "-",
                  f"1 pc. {g['base'].area / 1e6:.3f} m²"]]
    rows += [[8, f"LED Kaisen {g['led_name']} + PSU", g["psu_name"], "6500 K", f"{g['led_n']} pcs. ({g['led_W']:.1f} W)"]]
    if g.get("logo") is not None:
        rows += [[9, "Studs (welded to Alu) + nuts", "?", "-", f"{2 * len(g['studs'])} pcs."]]
    rows += [[10, ("Countersunk screw" if g["screws"] == "countersunk" else "Screw") + ", D3.2 in flanges", "A2", "-",
              f"{g['n_scr']} pcs."]]
    return rows


def main_data(g):
    md = [["Product", "P10 lightbox, 2-sided"],
          ["Size", f"{g['w']:g} x {g['h']:g} x {g['depth']:g} (+ 2 x {g['prot']:g})"],
          ["From wall", f"{g['proj']:g} mm (legs {g['leg_len']:g} + plate {g['plate'][2]:g})"],
          ["Body", f"Alu {g['t']:g} folded A + B, {g['body_finish'] or ''}".strip().rstrip(",")],
          ["Glass", f"{g['glass']} mm, cut-out + {g['cut_gap']:g}"],
          ["Frame", f"{prof(*g['frame'])} {g['frame_finish'] or ''}".strip()],
          ["Plates", f"{g['plates']}, {sum(len(P['holes']) for P in g['plates_l'])} x Ø{g['plate_hole_d']:g}"],
          ["LED / PSU", f"{g['led_n']} x {g['led_name']}, {g['psu_name']}"],
          ["Qty", f"{g['qty']}"],
          ["Weight (calc.)", f"≈ {g['kg']:.1f} kg / pcs, excl. PSU"]]
    if g["film"]:
        md.insert(5, ["Film", g["film"]])
    return md


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


def main(spec_path, out):
    S = dict(DEF); S.update(json.load(open(spec_path, encoding="utf-8")))
    global COL_BODY, COL_FRAME, COL_FL
    if str(S.get("body_finish", "")).upper().startswith("RAL"):
        COL_BODY = HexColor(K.ralhex(S["body_finish"]))
    if str(S.get("frame_finish", "")).upper().startswith("RAL"):
        COL_FRAME = COL_FL = HexColor(K.ralhex(S["frame_finish"]))
    K.F_DIM_FRAME = K.F_DIM_MAIN
    g = geom(S)
    K.auto_begin("collect"); K.AUTO["region"] = None
    sheet(g, out)
    pl_ = K.auto_place(out)
    K.auto_begin("draw", pl_); K.AUTO["region"] = None
    sheet(g, out)
    K.auto_begin(None)
    K.pdf_fix_fonts(out)
    if os.path.exists(out + ".tmp"):
        os.remove(out + ".tmp")
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
