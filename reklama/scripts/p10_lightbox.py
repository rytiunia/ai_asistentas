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
       "led": "DS15", "psu": "", "cable": "", "logo": None, "scale_ga": None,
       "cover_w": None, "cover_thk": 2, "cover_gap": 5}
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
    # v211 (Rytis 2026-10-14) RĖMO VARIANTAS B (spec "legs": {"spacing": <kojų ašių atstumas>, "yc": <centras, numatyta H/2>}):
    #  kojos siauresnės už dėžę - eina PER galinį (sienos pusės) statmenį, kuris iš kelių dalių, kojos įvirintos tarp jų;
    #  viršutinis / apatinis skersiniai - tik rėmo plotyje; montavimo plokštė VIENTISA, aukštis = kojų matmuo (sp + fb);
    #  skylės >= 4, siaurame pade - šachmatine tvarka (kaip CEOS mažo pilono padas).
    LG = S.get("legs") or None
    g["legB"] = bool(LG)
    g["cover"] = None
    xr = (t + cl) + g["FW"]                                          # rėmo sienos pusės išorė
    if g["legB"]:
        sp = float(LG["spacing"]); yc_ = float(LG.get("yc", H / 2))
        g["legs_y"] = [yc_ - sp / 2, yc_ + sp / 2]
        g["L_h"] = g["FW"]                                          # skersiniai - rėmo plotis
        g["L_leg"] = (W + g["leg_len"]) - (xr - fa)                 # koja nuo galinio statmens vidaus iki plokštės
        y_in0, y_in1 = (t + cl) + fb, (t + cl) + g["FH"] - fb
        cuts = [y_in0] + [v for y_ in g["legs_y"] for v in (y_ - fb / 2, y_ + fb / 2)] + [y_in1]
        g["rear_parts"] = [(a_, b_) for a_, b_ in zip(cuts[::2], cuts[1::2])]
        g["L_v"] = g["FH"] - 2 * fa                                 # laisvo galo statmuo
        g["prof_len"] = 2 * g["L_h"] + g["L_v"] + sum(b_ - a_ for a_, b_ in g["rear_parts"]) + 2 * g["L_leg"]
        ph = sp + fb
        hd = S["plate_hole_d"]
        z0_, z1_ = g["legs_y"][0] + fb / 2 + hd, g["legs_y"][1] - fb / 2 - hd        # laisva zona tarp kojų
        n = max(4, int(math.ceil((z1_ - z0_) / 120.0)) + 1)
        if n % 2: n += 1
        if PLw >= 7 * hd:                                            # 2 stulpeliai
            zz = PLw / 2 - 2 * hd
            rows = n // 2
            hz = [(sg * zz, z0_ + (z1_ - z0_) * k / max(rows - 1, 1)) for k in range(rows) for sg in (-1, 1)]
            g["plate_holes_mode"] = "2 columns"
        else:                                                        # siauras - šachmatine tvarka
            zz = max(0.0, PLw / 2 - 2 * hd)
            hz = [((-zz if k % 2 == 0 else zz), z0_ + (z1_ - z0_) * k / (n - 1)) for k in range(n)]
            g["plate_holes_mode"] = "staggered"
        g["plates_l"] = [dict(yc=yc_, w=PLw, h=ph, t=PLt, holes=sorted(set(v for _, v in hz)), hz=hz)]
        # v212 (Rytis 2026-10-14): KOJŲ UŽDENGIMAS - 2 dalys A + B (veidrodinės), Alu 2, korpuso spalva; ilgis 5 mm mažesnis už
        #  kojų tarpą (korpusas - plokštė): po 2.5 mm iš abiejų galų; aukštis = kojų matmuo; plotis cover_w (numatyta kojos + 10)
        # v214 (Rytis 2026-10-14): uždengimas 10 mm platesnis už kojų profilį (30 -> 20 + 20); viršuje 2 x Ø3.2 prisukimui;
        #  priekyje ir gale (prie korpuso / plokštės) lenkiamos standumo briaunos 10 mm
        cw_ = S["cover_w"] or (fa + 10)
        g["cover"] = dict(y0=yc_ - ph / 2, y1=yc_ + ph / 2, w=cw_, thk=S["cover_thk"], gap=S["cover_gap"],
                          L=g["leg_len"] - S["cover_gap"], rib=10.0, holes_top=2)
    else:
        g["legs_y"] = [g["ax"], H - g["ax"]]
        g["L_h"] = (W - (t + cl)) + g["leg_len"]                    # nuo rėmo laisvo krašto iki plokštės
        g["L_v"] = g["FH"] - 2 * fa                                 # statmenys tarp skersinių (laisvas galas + sienos pusė)
        g["prof_len"] = 2 * g["L_h"] + 2 * g["L_v"]
        ys = g["legs_y"]
        if S["plates"] == "single":
            g["plates_l"] = [dict(yc=H / 2, w=PLw, h=ys[1] - ys[0] + PLh, t=PLt, holes=ys, hz=[(0, y) for y in ys])]
        else:
            g["plates_l"] = [dict(yc=y, w=PLw, h=PLh, t=PLt, holes=[y], hz=[(0, y)]) for y in ys]
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
    for y_ in g["legs_y"]:
        sc.box((W, H - y_ - fb / 2, -fa / 2), (LL, 0, 0), (0, fb, 0), (0, 0, fa), COL_FRAME, edge=EDGE)
    if g["cover"]:
        C = g["cover"]
        sc.box((W + C["gap"] / 2, H - C["y1"], -C["w"] / 2), (C["L"], 0, 0), (0, C["y1"] - C["y0"], 0), (0, 0, C["w"]), COL_BODY, edge=EDGE)
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
    nga = g["scale_ga"] or nice_scale(170, max(W + PR, H * 1.15), (5, 6, 8, 10, 12, 15, 20, 25, 30, 40))
    s = MM / nga
    sl = f"1:{nga:g}"
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
        for y_ in g["legs_y"]:
            a_, _ = sorted((X(W), X(W + LL)))
            if g["cover"]:                                          # v212: kojos po uždengimu - punktyru
                rect(a_, Yv(y_ - fb / 2), LL * s, fb * s, stroke=HexColor("#D8D8D8"), lw=0.3, dash=(2, 1.5))
            else:
                rect(a_, Yv(y_ - fb / 2), LL * s, fb * s, fill=COL_FRAME, lw=0.1)
        if g["cover"]:
            C = g["cover"]
            c_a, _ = sorted((X(W + C["gap"] / 2), X(W + LL - C["gap"] / 2)))
            rect(c_a, Yv(C["y0"]), C["L"] * s, (C["y1"] - C["y0"]) * s, fill=COL_BODY, lw=0.1)
        for P in g["plates_l"]:
            a2, _ = sorted((X(W + LL), X(W + PR)))
            rect(a2, Yv(P["yc"] - P["h"] / 2), PLt * s, P["h"] * s, fill=COL_FL, lw=0.1)
        K.set_view(False)
        for y_ in g["legs_y"]:
            K.centerline(X(W - 20), Yv(y_), X(W + PR + 8), Yv(y_))
        xs_ = sorted([X(0), X(W), X(W + PR)])                     # v201: koja + plokštė = iškyša (92 / 8 - sienos vaizde, rėme)
        labs = [f"{W:g}", f"{PR:g}"]
        hchain(Yv(H) + D1, xs_, [Yv(H)] * 3, labs[::-1] if mirror else labs, size=K.F_DIM_MAIN)
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
        la_, lb_ = g["legs_y"]
        vchain(xw + D1 if not mirror else xw - D1, [Yv(0), Yv(la_), Yv(lb_), Yv(H)], [X(W)] + [xw] * 2 + [X(W)],
               [f"{la_:g}", f"{lb_ - la_:g}", f"{H - lb_:g}"], size=K.F_DIM_MAIN)
        return X

    # ------------------------------------------------ SIDE A
    fxA = K.IX0 + 78
    XA = front(fxA, False)
    xc = (g["logo_x"] + g["logo_w"] / 2) if lg is not None else W / 2
    K.cut_plane(XA(xc), Yv(0) - 30, Yv(H) + 54, "A", look="right")
    K.balloon_side([(XA(W * 0.1), Yv(H * 0.9), 2)] + ([(XA(g["logo_x"] + g["logo_w"] * 0.3), Yv(g["logo_y"] + g["logo_h"] * 0.5), 4)]
                                                     if lg is not None else []), XA(0) - 60, "left", up=False)
    K.balloon_auto(XA(W + LL * 0.5), Yv(g["legs_y"][1]), 1)
    if g["cover"]:                                                  # v212: kojų uždengimas
        K.balloon_auto(XA(W + LL * 0.5), Yv(g["cover"]["y1"] - 12), 11)
    view_title(XA((W + PR) / 2), top - 84, "FRONT VIEW - SIDE A", sl)
    # ------------------------------------------------ VAIZDAS IŠ SIENOS
    sxc = XA(W + PR) + 115
    Zs = lambda z: sxc + z * s
    P0 = g["plates_l"][0]; PLw = P0["w"]
    K.set_view(True)
    rect(Zs(-D / 2), Yv(0), D * s, H * s, fill=COL_BODY, lw=0.1)
    nd = fa / 2 + g["clear"]
    for y_ in g["legs_y"]:                                          # kojų išpjovos sienos pusės flanšuose (A + B)
        rect(Zs(-fa / 2), Yv(y_ - fb / 2), fa * s, fb * s, fill=COL_FRAME, lw=0.1)
    for P in g["plates_l"]:
        rect(Zs(-P["w"] / 2), Yv(P["yc"] - P["h"] / 2), P["w"] * s, P["h"] * s, fill=COL_FL, lw=0.1)
        for z_, y_ in P["hz"]:
            circle(Zs(z_), Yv(y_), g["plate_hole_d"] / 2 * s, fill=white, lw=0.1)
    K.set_view(False)
    line(Zs(0), Yv(0), Zs(0), Yv(H), 0.2, HexColor("#888888"), dash=(3, 1.5))     # padėklų sandūra
    face_label(Zs(-D / 2) + 2, Yv(0) - 54, "A", 9); face_label(Zs(D / 2) - 2, Yv(0) - 54, "B", 9)
    hy_ = sorted(set(y for P in g["plates_l"] for y in P["holes"])) if not g["legB"] else []
    ptop = min(P["yc"] - P["h"] / 2 for P in g["plates_l"]); pbot = max(P["yc"] + P["h"] / 2 for P in g["plates_l"])
    yy = [ptop] + hy_ + [pbot]
    ex_ = max(PLw, D) / 2
    if len(yy) > 2:
        vchain(Zs(ex_) + D1, [Yv(v) for v in yy], [Zs(PLw / 2)] * len(yy), [f"{b - a:g}" for a, b in zip(yy, yy[1:])],
               size=K.F_DIM_MAIN)
    VM(Zs(ex_) + D2, Yv(ptop), Yv(pbot), Zs(PLw / 2), f"{pbot - ptop:g}")
    VM(Zs(-ex_) - D1, Yv(0), Yv(H), Zs(-D / 2), f"{H:g}")
    HM(Zs(-D / 2), Zs(D / 2), Yv(0) - D1, f"{D:g}", Yv(0), Yv(0))
    HM(Zs(-PLw / 2), Zs(PLw / 2), Yv(pbot) + D1, f"{PLw:g}", Yv(pbot), Yv(pbot))
    _hz = [q for P in g["plates_l"] for q in P["hz"]]
    K.balloon_side([(Zs(_hz[-1][0]), Yv(_hz[-1][1]), f"{len(_hz)} x Ø{g['plate_hole_d']:g}"),
                    (Zs(nd), Yv(g["legs_y"][0] + fb / 2 + g["clear"]), f"leg cut-out {2 * nd:g}x{fb + 2 * g['clear']:g}")],
                   Zs(ex_) + 40, "right", up=True, tags=True)
    T(Zs(0), Yv(H) + 40, "= WALL DRILLING; - - - tray seam", 8, align="c", color=K.GREY)
    view_title(Zs(0), top - 84, "VIEW FROM WALL", sl)
    # ------------------------------------------------ SIDE B
    fxB = Zs(ex_) + 125
    XB = front(fxB, True)
    K.balloon_side([(XB(W * 0.1), Yv(H * 0.9), 3)] + ([(XB(g["logo_x"] + g["logo_w"] * 0.3), Yv(g["logo_y"] + g["logo_h"] * 0.5), 5)]
                                                     if lg is not None else []), XB(0) + 60, "right", up=False)
    view_title(XB((W + PR) / 2), top - 84, "FRONT VIEW - SIDE B", sl + "  (mirrored)")
    # ------------------------------------------------ SECTION A-A (per logotipo vidurį)
    n5 = nice_scale(H * s * 1.6, H, (4, 5, 6, 8, 10, 12, 15, 20, 25, 30))     # v201: vienas lapas
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
        T(U(0) - 4, Ya(segA[0][0]) - 17, "B", 10, font="FB", align="r")
    view_title(U(D / 2), top - 84, "SECTION A-A", f"1:{n5:g}")
    # ------------------------------------------------ FRAME (1) + LED (8) - v201 iš buv. 2 lapo
    ffx = U(D + pr) + 100
    x0f = t + g["clear"]
    nF = nice_scale(K.IX1 - ffx - 60, W + LL + PLt - x0f, (5, 6, 8, 10, 12, 15, 20, 25, 30, 40, 50))
    fr_r = frame_view(g, ffx, top + x0f * s, nF)
    fbot = top + x0f * s + g["FH"] * MM / nF + 40                  # po rėmo pastabomis
    P0_ = g["plates_l"][0]
    pav = (K.VIEW_BOT - 64 - (D / 2 + pr) * s - 44 - 30) - (fbot + 40) - 50     # iki TOP VIEW pavadinimo
    if g["legB"]:                                                   # v211: ilga plokštė - gulsčiai
        npl = nice_scale(min(fr_r - ffx - 60, K.IX1 - ffx - 80), P0_["h"], (2, 2.5, 4, 5, 8, 10))
        plate_view_h(g, (ffx + fr_r) / 2 - 20, fbot + 40, npl)
    else:
        npl = nice_scale(pav, P0_["h"], (2, 2.5, 4, 5, 8, 10))
        plate_view(g, (ffx + fr_r) / 2, fbot + 40, npl)
    # ------------------------------------------------ 2 eilė: 3D A, 3D B, EXPLODED, PLATE 1A + TOP VIEW
    y3 = max(Yv(H), Ya(H)) + D2 + 50
    h3 = K.VIEW_BOT - y3 - 30
    w3 = 115
    try:
        scene3d(g, -35, (K.IX0 + 30, y3, w3, h3), "3D VIEW - SIDE A")
        scene3d(g, 145, (K.IX0 + 30 + w3 + 30, y3, w3, h3), "3D VIEW - SIDE B")
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
    if g["cover"]:                                                  # v212: uždengimas (kojos po juo)
        C = g["cover"]
        rect(Xt(W + C["gap"] / 2), Zt(-C["w"] / 2), C["L"] * s, C["w"] * s, fill=COL_BODY, lw=0.1)
    else:
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
    # EXPLODED VIEW - tarp 3D B ir TOP VIEW
    ex0 = K.IX0 + 30 + 2 * w3 + 30 + 50
    exploded_view(g, (ex0, y3, tx0 - 60 - ex0, h3 + 8))

    band(g, "1 / 1", "", main_data1(g), bom1(g), detail_b(g))
    K.save(out)


def detail_b(g):
    """v213 (Rytis 2026-10-14): DETAIL B - pjūvis per VISĄ gylį (A | rėmas | B) TRIJOSE vietose: VIRŠUS / STIKLAS / APAČIA
    (zonos atskirtos nutraukimo linijomis). Ilgasriegiai PRIŠAUDYTI iš VIDINĖS Alu pusės (nekiaurai priekį)."""
    t, pr, bt, it_ = g["t"], g["prot"], g["base_t"], g["ins_t"]
    D, H = g["depth"], g["h"]
    fa, fb, ft = g["frame"]
    cl = g["clear"]

    def detail(X_P6, BY0, W_P6, BH):
        lg = g.get("logo")
        xc = (g["logo_x"] + g["logo_w"] / 2) if lg is not None else g["w"] / 2
        hyo = g["hole_off"]
        ytz = t + cl + fb + 8 + 6                                   # viršaus zona: flanšas, skersinis, LED
        zones = [("TOP", 0.0, ytz)]
        segc = vsegs(g["cut"], xc) if lg is not None else []
        if segc:
            ltop = vsegs(g["logo"], xc)[0][0]
            zones.append(("GLASS", ltop - hyo - 9, ltop + 10))
        zones.append(("BOTTOM", H - ytz, H))
        gap = 9                                                     # tarpas tarp zonų (pt)
        tot_mm = sum(b_ - a_ for _, a_, b_ in zones)
        avail_h = BH - 12 - 26 - 14 - gap * (len(zones) - 1)
        avail_w = W_P6 - 70
        sc = next(n for n in (2, 2.5, 3, 4, 5, 6, 8) if tot_mm * MM / n <= avail_h and (D + 2 * pr) * MM / n <= avail_w)
        s3 = MM / sc
        K.header(X_P6, BY0, W_P6, f"DETAIL B - SECTION TOP / GLASS / BOTTOM  1:{sc:g}")
        rect(X_P6, BY0 + 12, W_P6, BH - 12, lw=0.6)
        reg = (X_P6 + 3, BY0 + 15, X_P6 + W_P6 - 3, BY0 + BH - 16)
        ox = X_P6 + (W_P6 - (D + 2 * pr) * s3) / 2 + pr * s3
        U = lambda u: ox + u * s3                                   # u: 0 = A Alu išorė, D = B Alu išorė
        ys0 = BY0 + 12 + 26
        maps = []
        for name, a_, b_ in zones:
            maps.append((name, a_, b_, ys0)); ys0 += (b_ - a_) * s3 + gap
        bal = []
        for name, a_, b_, sy in maps:
            Yz = lambda y, a_=a_, sy=sy: sy + (y - a_) * s3
            hh = (b_ - a_) * s3
            K.set_view(True)
            if name in ("TOP", "BOTTOM"):
                top_ = name == "TOP"
                yf0 = 0.0 if top_ else H - t                        # flanšas
                yfr = (t + cl) if top_ else (H - t - cl - fb)       # skersinis
                yled = (t + cl + fb) if top_ else (H - t - cl - fb - 8)
                rect(U(0), Yz(a_), t * s3, hh, fill=COL_BODY, lw=0.1)                       # Alu A priekis
                rect(U(D - t), Yz(a_), t * s3, hh, fill=COL_BODY, lw=0.1)                   # Alu B
                rect(U(0), Yz(yf0), (D / 2) * s3, t * s3, fill=COL_BODY, lw=0.1)            # flanšas A (iki siūlės)
                rect(U(D / 2), Yz(yf0), (D / 2) * s3, t * s3, fill=COL_BODY, lw=0.1)        # flanšas B
                rect(U(D / 2 - fa / 2), Yz(yfr), fa * s3, fb * s3, fill=COL_FRAME, lw=0.1)
                rect(U(D / 2 - fa / 2 + ft), Yz(yfr + ft), (fa - 2 * ft) * s3, (fb - 2 * ft) * s3, fill=white, lw=0.1)
                rect(U(D / 2 - 11), Yz(yled), 22 * s3, 8 * s3, fill=COL_LED, lw=0.1)
                for sg in (-1, 1):                                  # varžtai per flanšą į skersinį (7 nuo siūlės)
                    uz = D / 2 + sg * g["screw_edge"]
                    if top_:
                        rect(U(uz) - 1.6 * s3, Yz(-1.2), 3.2 * s3, (t + cl + ft + 5) * s3, fill=COL_STUD, lw=0.1)
                        rect(U(uz) - 3 * s3, Yz(-1.2), 6 * s3, 1.2 * s3, fill=COL_STUD, lw=0.1)
                    else:
                        rect(U(uz) - 1.6 * s3, Yz(H - t - cl - ft - 5), 3.2 * s3, (t + cl + ft + 5 + 1.2) * s3, fill=COL_STUD, lw=0.1)
                        rect(U(uz) - 3 * s3, Yz(H), 6 * s3, 1.2 * s3, fill=COL_STUD, lw=0.1)
                K.set_view(False)
                line(U(D / 2), Yz(a_) - 2, U(D / 2), Yz(b_) + 2, 0.2, HexColor("#888888"), dash=(3, 1.5))
                if top_:
                    bal += [(U(t / 2), Yz(a_ + (b_ - a_) * 0.75), 2), (U(D - t / 2), Yz(a_ + (b_ - a_) * 0.75), 3),
                            (U(D / 2 + fa / 2 - ft / 2), Yz(yfr + fb / 2), 1), (U(D / 2 + 8), Yz(yled + 4), 8),
                            (U(D / 2 - g["screw_edge"]), Yz(t + 1), 10)]
            else:
                ltop = a_ + hyo + 9
                cut_top = vsegs(g["cut"], xc)[0][0]
                btop = vsegs(g["base"], xc)[0][0]
                ys_ = ltop - hyo                                      # ilgasriegio ašis
                for side in ("A", "B"):
                    m = (lambda u: u) if side == "A" else (lambda u: D - u)
                    def R(u0, u1, y0, y1, fill):
                        ua, ub = sorted((m(u0), m(u1)))
                        rect(U(ua), Yz(y0), (ub - ua) * s3, (y1 - y0) * s3, fill=fill, lw=0.1)
                    R(0, t, a_, cut_top, COL_BODY)                           # Alu (virš išpjovos)
                    R(t, t + bt, max(a_, btop), b_, COL_BASE)                 # pagrindas
                    if it_ > 0:
                        R(t - it_, t, ltop, b_, COL_PLEX)                     # įdėklas (iškištas pro išpjovą)
                    R(t, t + bt + 6, ys_ - 2, ys_ + 2, COL_STUD)              # ilgasriegis - nuo VIDINĖS Alu pusės
                    R(t + bt, t + bt + 3, ys_ - 3.5, ys_ + 3.5, HexColor("#8C8C8C"))   # veržlė
                K.set_view(False)
                for u_ in (t, D - t):
                    K.centerline(U(u_) + (-4 if u_ < D / 2 else 4), Yz(ys_), U(u_ + (bt + 9 if u_ < D / 2 else -bt - 9)), Yz(ys_))
                bal += [(U(t - it_ / 2), Yz(b_ - 3), 4), (U(D - t + it_ / 2), Yz(b_ - 3), 5),
                        (U(t + bt / 2), Yz(b_ - 3), 6), (U(D - t - bt / 2), Yz(b_ - 3), 7), (U(t + bt + 4), Yz(ys_), 9)]
            # nutraukimo linijos (zigzag) zonos krašte
            for yy, show in ((Yz(a_), name != "TOP"), (Yz(b_), name != "BOTTOM")):
                if show:
                    xa_, xb_ = U(-pr) - 4, U(D + pr) + 4
                    n_ = 8; pts = []
                    for k in range(n_ + 1):
                        pts.append((xa_ + (xb_ - xa_) * k / n_, yy + (1.5 if k % 2 else -1.5)))
                    for p0, p1 in zip(pts, pts[1:]):
                        line(p0[0], p0[1], p1[0], p1[1], 0.2)
            T(X_P6 + 5, Yz((a_ + b_) / 2) + 3, name, 6.5, color=K.GREY)
        hchain(BY0 + 12 + 16, [U(-pr), U(0), U(D), U(D + pr)], [maps[0][3]] * 4, [f"{pr:g}", f"{D:g}", f"{pr:g}"],
               size=K.F_DIM_FRAME)
        cxm = U(D / 2)
        left = [q for q in bal if q[0] < cxm]; right = [q for q in bal if q[0] >= cxm]
        ytop_, ybot_ = BY0 + 12 + 30, BY0 + BH - 22                # balionai - stulpeliais šonuose, eilės tvarka pagal y
        for lst, bx in ((left, U(-pr) - 26), (right, U(D + pr) + 26)):
            lst.sort(key=lambda q: q[1])
            n_ = len(lst)
            for k, (tx_, ty_, lab) in enumerate(lst):
                by = ytop_ + (ybot_ - ytop_) * (k + 0.5) / max(n_, 1)
                K.leader(tx_, ty_, bx, by, lab, 6)
        T(X_P6 + W_P6 / 2, BY0 + BH - 4, f"gap {g['cut_gap']:g}; insert GLUED to base; studs welded inside, {hyo:g} from glass",
          6.5, align="c", color=K.GREY)

    return detail


def bom1(g):
    fa, fb, ft = g["frame"]
    P0 = g["plates_l"][0]
    W, H = g["w"], g["h"]
    if g["legB"]:                                                   # v211: rėmo variantas B
        _rp = " + ".join(f"{b_ - a_:.0f}" for a_, b_ in g["rear_parts"])
        r1 = [[1, f"Frame + 2 legs {prof(fa, fb, ft)}", "Alu, welded", g["frame_finish"] or "",
               f"{g['prof_len']:.0f} mm (cut list - frame view)"],
              ["1A", f"Mounting plate {P0['w']:g}x{P0['h']:g}x{P0['t']:g}, {len(P0['hz'])} x Ø{g['plate_hole_d']:g}",
               "Alu, welded to legs", g["frame_finish"] or "", "1 pc."]]
    else:
        r1 = [[1, f"Frame + legs {prof(fa, fb, ft)}", "Alu, welded", g["frame_finish"] or "",
               f"2 x {g['L_h']:.0f} + 2 x {g['L_v']:.0f} mm"],
              ["1A", f"Mounting plate {P0['w']:g}x{P0['h']:g}x{P0['t']:g}, Ø{g['plate_hole_d']:g}", "Alu, welded to leg",
               g["frame_finish"] or "", f"{len(g['plates_l'])} pcs."]]
    rows = r1 + [
            [2, f"Front A, folded {W:g}x{H:g}x{g['PD']:g} (DXF)", f"Alu {g['t']:g} mm", g["body_finish"] or "", "1 pc."],
            [3, f"Back B, folded {W:g}x{H:g}x{g['PD']:g} (DXF)", f"Alu {g['t']:g} mm", g["body_finish"] or "", "1 pc."]]
    if g.get("logo") is not None:
        if g["ins_t"] > 0:
            for k_, sd in ((4, "A"), (5, "B")):
                rows.append([k_, f"Insert {sd} {g['ins_t']:g} mm, GLUED to base", f"Plexi {g['plexi']}", g["film"] or "-",
                             f"1 pc. {g['logo'].area / 1e6:.3f} m²"])
        for k_, sd in ((6, "A"), (7, "B")):
            rows.append([k_, f"Base {sd} {g['base_t']:g} mm, {len(g['studs'])} x Ø{g['hole_d']:g} (DXF)", f"Plexi {g['plexi']}",
                         "-", f"1 pc. {g['base'].area / 1e6:.3f} m²"])
    rows += [[8, f"LED Kaisen {g['led_name']}", "PSU " + g["psu_name"], "6500 K", f"{g['led_n']} pcs. ({g['led_W']:.1f} W)"]]
    if g.get("logo") is not None:
        rows += [[9, "Stud (welded to Alu) + nut", "?", "-", f"{2 * len(g['studs'])} pcs."]]
    rows += [[10, ("Countersunk screw" if g["screws"] == "countersunk" else "Screw") + ", Ø3.2 holes in flanges", "A2", "-",
              f"{g['n_scr']} pcs."]]
    if g["cover"]:                                                  # v212: kojų uždengimas
        C = g["cover"]
        rows += [[11, f"Leg cover A + B, 2 x Ø3.2 top (DXF)", f"Alu {C['thk']:g} folded, ribs {C['rib']:g}", g["body_finish"] or "",
                  f"2 pcs., {C['L']:g} x {C['y1'] - C['y0']:g} x {C['w'] / 2:g}"]]
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


# ===================================================================== v201: VIENAS LAPAS - rėmas, plokštė 1A, exploded (buv. 2 lapas)
def frame_view(g, fx, top, nF):
    """FRAME (1) + LED (8): kairysis viršutinis rėmo kampas (x0) = (fx, top)"""
    W, H, t = g["w"], g["h"], g["t"]
    fa, fb, ft = g["frame"]
    LL = g["leg_len"]
    PLw, PLh, PLt = g["plate"]
    s = MM / nF
    x0 = t + g["clear"]
    X = lambda x: fx + (x - x0) * s
    Yv = lambda y: top + (y - x0) * s
    FW, FH = g["FW"], g["FH"]
    xr = x0 + FW
    xf = W + LL
    K.set_view(True)
    rect(X(0), Yv(0), W * s, H * s, stroke=HexColor("#9A9A9A"), lw=0.1, dash=(3, 2))   # korpusas
    if g["legB"]:                                                   # v211: skersiniai rėmo plotyje, kojos per galinį statmenį
        for y0 in (x0, x0 + FH - fb):
            rect(X(x0), Yv(y0), FW * s, fb * s, fill=COL_FRAME, lw=0.1)
        rect(X(x0), Yv(x0 + fb), fa * s, g["L_v"] * s, fill=COL_FRAME, lw=0.1)
        for a_, b_ in g["rear_parts"]:
            rect(X(xr - fa), Yv(a_), fa * s, (b_ - a_) * s, fill=COL_FRAME, lw=0.1)
        for y_ in g["legs_y"]:
            rect(X(xr - fa), Yv(y_ - fb / 2), (xf - xr + fa) * s, fb * s, fill=COL_FRAME, lw=0.1)
    else:
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
    K.set_view(False)
    if g["legB"]:
        hchain(Yv(x0) - D1, [X(x0), X(xr)], [Yv(x0)] * 2, [f"{FW:g}"], size=K.F_DIM_FRAME)
        yl_ = g["legs_y"][1] + fb / 2
        hchain(Yv(yl_) + 12, [X(xr - fa), X(xf)], [Yv(yl_)] * 2, [f"{g['L_leg']:.0f}"], size=K.F_DIM_FRAME)
        HM(X(x0), X(xf + PLt), Yv(x0) - D2, f"{xf + PLt - x0:g}", Yv(x0), Yv(x0))
    else:
        hchain(Yv(x0) - D1, [X(x0), X(W), X(xf)], [Yv(x0)] * 3, [f"{W - x0:g}", f"{LL:g}"], size=K.F_DIM_FRAME)
        HM(X(x0), X(xf), Yv(x0) - D2, f"{g['L_h']:.0f}", Yv(x0), Yv(x0))
    vchain(X(x0) - D1, [Yv(x0), Yv(x0 + fb), Yv(x0 + FH - fb), Yv(x0 + FH)], [X(x0)] * 4,
           [f"{fb:g}", f"{g['L_v']:.0f}", f"{fb:g}"], size=K.F_DIM_FRAME)
    VM(X(x0) - D2, Yv(x0), Yv(x0 + FH), X(x0), f"{FH:g}")
    la_, lb_ = g["legs_y"]
    vchain(X(xf + PLt) + D1, [Yv(la_), Yv(lb_)], [X(xf)] * 2, [f"{lb_ - la_:g}"], size=K.F_DIM_FRAME)
    if g["legB"]:
        _rp = [x0 + fb] + [v for a_, b_ in g["rear_parts"] for v in (a_, b_)][1:-1] + [x0 + FH - fb]
        vchain(X(xr - fa) - 10, [Yv(v) for v in _rp], [X(xr - fa)] * len(_rp), [f"{b - a:.0f}" for a, b in zip(_rp, _rp[1:])],
               size=K.F_DIM_FRAME)
    K.balloon_auto(X(xr - fa / 2), Yv(H * 0.45), 1)
    K.balloon_auto(X(led_x[0] if g["legB"] else led_x[-1]), Yv(yrow[1] - 4), 8)
    T(X(x0), Yv(x0 + FH) + 16, (f"{prof(fa, fb, ft)}: members 2 x {g['L_h']:.0f}, legs 2 x {g['L_leg']:.0f} (through rear vertical)"
                               if g["legB"] else f"{prof(fa, fb, ft)}: legs 2 x {g['L_h']:.0f}, verticals 2 x {g['L_v']:.0f}"),
      7, color=K.GREY)
    T(X(x0), Yv(x0 + FH) + 25, f"welded, ground; LED {g['led_n']} pcs., {g['led_step']:.0f} mm", 7, color=K.GREY)
    view_title(X((x0 + xf) / 2), top - x0 * s - 84, "FRAME (1) + LED (8)", f"1:{nF:g}  (from side A)")
    return X(xf + PLt) + D1 + 10


def plate_view_h(g, cx, top, n):
    """v211 PLATE 1A rėmo variantui B - gulsčiai (ilgis = kojų matmuo išilgai x), centras cx, viršus top"""
    fa, fb, ft = g["frame"]
    P0 = g["plates_l"][0]
    sp = MM / n
    L, Wp = P0["h"], P0["w"]
    X = lambda y: cx + (y - P0["yc"]) * sp
    Y = lambda z: top + (z + Wp / 2) * sp
    K.set_view(True)
    rect(X(P0["yc"] - L / 2), Y(-Wp / 2), L * sp, Wp * sp, fill=COL_FL, lw=0.1)
    for y_ in g["legs_y"]:
        rect(X(y_ - fb / 2), Y(-fa / 2), fb * sp, fa * sp, lw=0.2, dash=(2, 1.5))
    for z_, y_ in P0["hz"]:
        circle(X(y_), Y(z_), g["plate_hole_d"] / 2 * sp, fill=white, lw=0.1)
    K.set_view(False)
    for z_, y_ in P0["hz"]:
        K.centerline(X(y_), Y(z_) - 6, X(y_), Y(z_) + 6)
    K.centerline(X(P0["yc"] - L / 2) - 5, Y(0), X(P0["yc"] + L / 2) + 5, Y(0))
    ys_ = [P0["yc"] - L / 2] + [y_ for _, y_ in sorted(P0["hz"], key=lambda q: q[1])] + [P0["yc"] + L / 2]
    yb = Y(Wp / 2)
    hchain(yb + D1, [X(v) for v in ys_], [yb] * len(ys_), [f"{b - a:.0f}" for a, b in zip(ys_, ys_[1:])], size=K.F_DIM_FRAME)
    HM(X(ys_[0]), X(ys_[-1]), yb + D2, f"{L:g}", yb, yb)
    zs_ = sorted(set(round(z_, 2) for z_, _ in P0["hz"]))
    xr_ = X(P0["yc"] + L / 2)
    vchain(xr_ + D1, [Y(-Wp / 2)] + [Y(z_) for z_ in zs_] + [Y(Wp / 2)], [xr_] * (len(zs_) + 2),
           [f"{b - a:g}" for a, b in zip([-Wp / 2] + zs_, zs_ + [Wp / 2])], size=K.F_DIM_FRAME)
    xl_ = X(P0["yc"] - L / 2)
    VM(xl_ - D1, Y(-Wp / 2), Y(Wp / 2), xl_, f"{Wp:g}")
    T(cx, yb + D2 + 18, f"t = {P0['t']:g}, {len(P0['hz'])} x Ø{g['plate_hole_d']:g} {g['plate_holes_mode']}, welded to both legs (- - -)",
      7.5, align="c", color=K.GREY)
    view_title(cx, top - 26, "PLATE 1A", f"1:{n:g}  (one plate, length = legs)")


def plate_view(g, cx, top, n):
    """PLATE 1A: centras cx, viršus top"""
    fa, fb, ft = g["frame"]
    P0 = g["plates_l"][0]
    sp = MM / n
    rxp = lambda z: cx + z * sp
    ryp = lambda y: top + (y - (P0["yc"] - P0["h"] / 2)) * sp
    K.set_view(True)
    rect(rxp(-P0["w"] / 2), ryp(P0["yc"] - P0["h"] / 2), P0["w"] * sp, P0["h"] * sp, fill=COL_FL, lw=0.1)
    for z_, y_ in P0["hz"]:
        circle(rxp(z_), ryp(y_), g["plate_hole_d"] / 2 * sp, fill=white, lw=0.1)
    for y_ in g["legs_y"]:                                          # kojos (punktyru) - privirintos
        rect(rxp(-fa / 2), ryp(y_ - fb / 2), fa * sp, fb * sp, lw=0.2, dash=(2, 1.5))
    K.set_view(False)
    for z_, y_ in P0["hz"]:
        K.centerline(rxp(z_ - 8), ryp(y_), rxp(z_ + 8), ryp(y_))
    K.centerline(rxp(0), ryp(P0["yc"] - P0["h"] / 2) - 5, rxp(0), ryp(P0["yc"] + P0["h"] / 2) + 5)
    _zs = sorted(set(round(z_, 2) for z_, _ in P0["hz"])) if g["legB"] else []
    _yb = ryp(P0["yc"] + P0["h"] / 2)
    if len(_zs) > 1:
        hchain(_yb + D1, [rxp(-P0["w"] / 2)] + [rxp(z_) for z_ in _zs] + [rxp(P0["w"] / 2)], [_yb] * (len(_zs) + 2),
               [f"{b - a:g}" for a, b in zip([-P0["w"] / 2] + _zs, _zs + [P0["w"] / 2])], size=K.F_DIM_FRAME)
    HM(rxp(-P0["w"] / 2), rxp(P0["w"] / 2), _yb + (D2 if len(_zs) > 1 else D1), f"{P0['w']:g}", _yb, _yb)
    yyp = [P0["yc"] - P0["h"] / 2] + sorted(set(P0["holes"])) + [P0["yc"] + P0["h"] / 2]
    if min(b - a for a, b in zip(yyp, yyp[1:])) * sp >= 45:
        vchain(rxp(P0["w"] / 2) + D1, [ryp(v) for v in yyp], [rxp(P0["w"] / 2)] * len(yyp),
               [f"{b - a:g}" for a, b in zip(yyp, yyp[1:])], size=K.F_DIM_FRAME)
    else:
        VM(rxp(P0["w"] / 2) + D1, ryp(yyp[0]), ryp(yyp[-1]), rxp(P0["w"] / 2), f"{P0['h']:g}")
    T(rxp(0), ryp(P0["yc"] + P0["h"] / 2) + (52 if len(_zs) > 1 else 30),
      (f"t = {P0['t']:g}, {len(P0['hz'])} x Ø{g['plate_hole_d']:g} {g['plate_holes_mode']}, one plate welded to both legs"
       if g["legB"] else f"t = {P0['t']:g}, Ø{g['plate_hole_d']:g}, welded to leg ({len(g['plates_l'])} pcs.), hole centred"),
      7.5, align="c", color=K.GREY)
    view_title(rxp(0), top - 26, "PLATE 1A", f"1:{n:g}")


def exploded_view(g, box):
    A = exploded(g, box)
    ex0, ey0, ew, eh = box
    reg = (ex0 - 20, ey0 - 10, ex0 + ew + 20, ey0 + eh + 10)
    for sd in ("A", "B"):                                           # surinkimo ašys: ilgasriegis -> veržlė
        for a_, b_ in A.get("ax" + sd, []):
            K.centerline(a_[0], a_[1], b_[0], b_[1])
    for key, lab in (("1", "1"), ("1A", "1A"), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), ("8", 8),
                     ("9A", 9), ("9B", 9), ("10A", 10), ("10B", 10), ("11A", 11), ("11B", 11)):
        if key in A:
            K.balloon_auto(A[key][0], A[key][1], lab, region=reg)
    view_title(ex0 + ew / 2, ey0 - 26, "ASSEMBLY - EXPLODED VIEW",
               "not to scale; tray A - insert 4 - base 6 + nuts - frame + LED - base 7 - insert 5 - tray B")


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
    for yax in g["legs_y"]:
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
    # v214: kojų uždengimo išklotinė (1 dalis; B - veidrodinė), folded v173: atlankas = gylis - t, briaunos tarp atlankų
    if g.get("cover"):
        C = g["cover"]; tc = C["thk"]; Lc = C["L"]; Hc = C["y1"] - C["y0"]
        fl = C["w"] / 2 - tc; rb = C["rib"] - tc
        cx0, cy0 = ox + rb, fl
        pts = [(cx0, 0), (cx0 + Lc, 0), (cx0 + Lc, cy0 + tc), (cx0 + Lc + rb, cy0 + tc), (cx0 + Lc + rb, cy0 + Hc - tc),
               (cx0 + Lc, cy0 + Hc - tc), (cx0 + Lc, cy0 + Hc + fl), (cx0, cy0 + Hc + fl), (cx0, cy0 + Hc - tc),
               (cx0 - rb, cy0 + Hc - tc), (cx0 - rb, cy0 + tc), (cx0, cy0 + tc)]
        msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": "CUT"})
        msp.add_lwpolyline([(cx0, cy0), (cx0 + Lc, cy0), (cx0 + Lc, cy0 + Hc), (cx0, cy0 + Hc)], close=True,
                           dxfattribs={"layer": "BEND_UP_90"})
        for k in range(C["holes_top"]):
            msp.add_circle((cx0 + Lc * (k + 1) / (C["holes_top"] + 1), cy0 + Hc + fl - 7), 1.6, dxfattribs={"layer": "HOLES_D3.2"})
        txt(f"LEG COVER {Lc:g}x{Hc:g}x{C['w'] / 2:g} Alu {tc:g} - x 2 (A + B mirror) - flanges {fl:g}, ribs {rb:g}, 2 x D3.2 top", ox, -30)
        ox += Lc + 2 * rb + gap
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


# ===================================================================== EXPLODED VIEW (v199; v200 - 2 lape)
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


def exploded(g, box, yaw=-58, pitch=11):
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
        for ya in g["legs_y"]:
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
    if g["legB"]:
        for ys in (x0, x0 + FH - fb):
            sc.box((x0, H - ys - fb, -fa / 2), (FW, 0, 0), (0, fb, 0), (0, 0, fa), COL_FRAME, edge=EDGE)
        sc.box((x0, H - x0 - FH + fb, -fa / 2), (fa, 0, 0), (0, FH - 2 * fb, 0), (0, 0, fa), COL_FRAME, edge=EDGE)
        for a_, b_ in g["rear_parts"]:
            sc.box((xr - fa, H - b_, -fa / 2), (fa, 0, 0), (0, b_ - a_, 0), (0, 0, fa), COL_FRAME, edge=EDGE)
        for y_ in g["legs_y"]:
            sc.box((xr - fa, H - y_ - fb / 2, -fa / 2), (xf - xr + fa, 0, 0), (0, fb, 0), (0, 0, fa), COL_FRAME, edge=EDGE)
    else:
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
    if g["cover"]:                                                  # v214: uždengimo dalys A / B - ištrauktos į šonus
        C = g["cover"]; ct = C["thk"]; hw = C["w"] / 2; Lc = C["L"]; xc0 = W + C["gap"] / 2
        yb_, yt_ = H - C["y1"], H - C["y0"]
        for sgn in (1, -1):
            dz = sgn * 0.11 * M
            zo = lambda z, sgn=sgn, dz=dz: sgn * z + dz
            za, zb = sorted((zo(hw - ct), zo(hw)))
            sc.box((xc0, yb_, za), (Lc, 0, 0), (0, yt_ - yb_, 0), (0, 0, zb - za), COL_BODY, edge=EDGE)          # šonas
            za, zb = sorted((zo(0), zo(hw)))
            for yy in (yb_, yt_ - ct):                                                                                # viršus / apačia
                sc.box((xc0, yy, za), (Lc, 0, 0), (0, ct, 0), (0, 0, zb - za), COL_BODY, edge=EDGE)
            za, zb = sorted((zo(hw - C["rib"]), zo(hw)))
            for xx in (xc0, xc0 + Lc - ct):                                                                           # briaunos 10
                sc.box((xx, yb_ + ct, za), (ct, 0, 0), (0, yt_ - yb_ - 2 * ct, 0), (0, 0, zb - za), COL_BODY, edge=EDGE)
            anc["11" + ("A" if sgn > 0 else "B")] = (xc0 + Lc / 2, yt_ - (yt_ - yb_) * 0.3, zo(hw))
    anc["1"] = (x0 + FW * 0.3, H - x0 - fb / 2, fa / 2)
    anc["1A"] = (xf + PLt, H - g["plates_l"][0]["yc"], 0)
    anc["8"] = (led_x[0], H - (x0 + FH - fb - 8), 11)
    sc.render(box)
    V = sc.V
    to2 = lambda p: (V.S(*p)[0], K.H - V.S(*p)[1])
    return {k: ([(to2(a), to2(b)) for a, b in v] if str(k).startswith("ax") else to2(v)) for k, v in anc.items()}


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
    p1 = out + ".1.pdf"
    for fn, pp in ((sheet1, p1),):                    # 2 praėjimai - automatinis žymėjimas
        K.auto_begin("collect"); K.AUTO["region"] = None
        fn(g, pp)
        pl_ = K.auto_place(pp)
        K.auto_begin("draw", pl_); K.AUTO["region"] = None
        fn(g, pp)
        K.auto_begin(None)
    import pymupdf as fitz
    d = fitz.open()
    for pp in (p1,):
        d.insert_pdf(fitz.open(pp))
    d.save(out, garbage=3, deflate=True); d.close()
    K.pdf_fix_fonts(out)
    for pp in (p1, p1 + ".tmp"):
        os.path.exists(pp) and os.remove(pp)
    dxf = os.path.splitext(out)[0] + "_gamyba.dxf"
    write_dxf(g, dxf)
    print("OK", out, dxf)
    print(f"  rėmas {prof(*g['frame'])} (PASIŪLYMAS pagal dydį)" + (f" VARIANTAS B: kojos 2 x {g['L_leg']:.0f} per galinį statmenį, padas {g['plates_l'][0]['w']:g}x{g['plates_l'][0]['h']:g}, {len(g['plates_l'][0]['hz'])} sk. {g['plate_holes_mode']}" if g["legB"] else f", skersinis+koja {g['L_h']:.0f}, statmuo {g['L_v']:.0f}") + "; "
          f"LED {g['led_n']} x {g['led_name']} ({g['led_W']:.1f} W), {g['psu_name']}; svoris {g['kg']:.1f} kg")
    if g.get("logo") is not None:
        print(f"  logotipas {g['logo_w']:.0f} x {g['logo_h']:.0f}, pagrindas {len(g['base_parts'])} d., ilgasriegiai {len(g['studs'])} / pusei")
    if g["led_warn"]:
        print("  !", g["led_warn"])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
