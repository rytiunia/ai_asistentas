#!/usr/bin/env python3
"""P10_lightbox_singlesided - vienpusė šviesdėžė (v230, Rytis 2026-10-14; pirmas užsakymas Leapmotor PO 33577 poz. 30).
Taisyklės - references/moduliai_p10_lightbox_singlesided.md. Priekis kaip P10_lightbox_doublesided (Alu padėklas su logotipo
išpjova + 0,7, iškištas įdėklas PRIKLIJUOTAS prie 3 mm pagrindo, pagrindas ant ilgasriegių, prišaudytų iš VIDINĖS pusės);
dugnas - paprasta folded plate (Alu 1,5), 3 mm mažesnė kiekvienai kraštinei, tūris 30, įlenda į priekį (bendras tūris = priekio
atlankas); priekis prisukamas per atlankus į dugno atlankus (folded standartas Ø3.2, 7 nuo atlanko krašto); prie fasado - per
dugną (skylių nebraižyti); laidas - dešinės šoninės viršuje, dugno atlanke skylė su gumine tarpine, centras 23 nuo dugno
priekinio krašto, priekio atlanke išpjova nuo laisvo krašto; LED - ant dugno (tipas - tik patvirtintas).
Koordinatės: x - į dešinę, y - žemyn (nuo dėžės viršaus), z - gylis (0 = fasadas / dugno nugara, D = priekio paviršius).
Naudojimas: python3 p10_lightbox_singlesided.py spec.json out.pdf   (-> out.pdf 2 lapai + out_gamyba.dxf)"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lapas_core as K  # noqa: E402
from lapas_core import hdim, vchain, hchain, view_title, MM  # noqa: E402
from reportlab.lib.colors import HexColor, white, black  # noqa: E402
from shapely.geometry import Polygon, Point, box as sbox, LineString  # noqa: E402
from shapely.ops import unary_union  # noqa: E402
from shapely import affinity  # noqa: E402
import sviesdeze as SV  # noqa: E402
from sviesdeze import HM, VM, D1, D2, face_label, band  # noqa: E402
from sviesdeze import rect, poly, circle, line, T  # noqa: E402  CAD režimas (SV._CAD) 2 lapui
import p10_lightbox_doublesided as PD2  # noqa: E402

DEF = {"client": "", "title": "LIGHTBOX P10 SINGLE-SIDED - PUSH-THROUGH", "order_no": "ALT0000_00.00_RS", "drawing_no": "",
       "date": "", "rev": "A", "qty": "?",
       "w": 750, "h": 750, "depth": 80, "t": 2.0, "back_t": 1.5, "back_depth": 30, "back_off": 3.0,
       "glass": "3+8", "cut_gap": 0.7, "base_off": 30, "hole_off": 15, "hole_d": 8, "hole_pitch": 100, "mark_d": 6,
       "screw_step": 300, "screw_edge": 7, "screw_end": 50,
       "cable": {"from_back_front": 23, "y": None, "hole_d": None, "slot_w": None, "grommet": ""},
       "body_finish": "", "back_finish": "", "plexi": "opal white", "film": "",
       "led": None, "psu": "", "logo": None}
COL_BODY, COL_BACK = HexColor("#3A3A3A"), HexColor("#9A9A9A")
COL_PLEX, COL_BASE, COL_STUD = HexColor("#F7F7F2"), HexColor("#E4E4DE"), HexColor("#B0B0B0")
COL_INWHITE = HexColor("#F2F2F2")
EDGE = HexColor("#555555")
RED = HexColor("#C00000")


def unk(v, fmt="{:g}"):
    return "?" if v in (None, "", "?") else fmt.format(v)


# ===================================================================== logotipas iš kliento PDF (vektorius, 1:1 pt)
def logo_from_pdf(L, base_dir):
    """L: {"pdf", "page", "clip": [x0, y0, x1, y1] pt (dėžės kontūras), "fill": [r, g, b], "scale"} -> shapely (mm, dėžės koord.)"""
    import pymupdf as fitz
    pth = L["pdf"] if os.path.isabs(L["pdf"]) else os.path.join(base_dir, L["pdf"])
    pg = fitz.open(pth)[L.get("page", 0)]
    x0, y0, x1, y1 = L["clip"]
    k = 25.4 / 72 * float(L.get("scale", 1.0))
    fc = L.get("fill", [1, 1, 1])
    geo = []
    for d in pg.get_drawings():
        f_ = d.get("fill")
        if not f_ or max(abs(a - b) for a, b in zip(f_, fc)) > 0.03:
            continue
        r_ = d["rect"]
        if r_.x0 < x0 - 1 or r_.x1 > x1 + 1 or r_.y0 < y0 - 1 or r_.y1 > y1 + 1:
            continue
        rings, cur = [], []
        for it in d["items"]:
            if it[0] == "re":
                q = it[1]; rings.append([(q.x0, q.y0), (q.x1, q.y0), (q.x1, q.y1), (q.x0, q.y1)]); continue
            a = it[1]
            if cur and (abs(cur[-1][0] - a.x) > 0.3 or abs(cur[-1][1] - a.y) > 0.3):
                rings.append(cur); cur = []
            if not cur:
                cur = [(a.x, a.y)]
            if it[0] == "l":
                cur.append((it[2].x, it[2].y))
            elif it[0] == "c":
                p0, p1, p2, p3 = it[1:5]
                for i in range(1, 13):
                    tt = i / 12
                    cur.append(((1 - tt) ** 3 * p0.x + 3 * (1 - tt) ** 2 * tt * p1.x + 3 * (1 - tt) * tt ** 2 * p2.x + tt ** 3 * p3.x,
                                (1 - tt) ** 3 * p0.y + 3 * (1 - tt) ** 2 * tt * p1.y + 3 * (1 - tt) * tt ** 2 * p2.y + tt ** 3 * p3.y))
        if cur:
            rings.append(cur)
        g_ = None
        for rg in rings:
            if len(rg) >= 3:
                p_ = Polygon([((x - x0) * k, (y - y0) * k) for x, y in rg]).buffer(0)
                g_ = p_ if g_ is None else g_.symmetric_difference(p_)
        if g_ is not None and not g_.is_empty:
            geo.append(g_)
    return unary_union(geo).buffer(0)


# ===================================================================== geometrija
def geom(S, base_dir):
    g = dict(S)
    W, H, D, t = S["w"], S["h"], S["depth"], S["t"]
    g["base_t"], g["ins_t"] = PD2.glass_parts(S["glass"])
    g["prot"] = max(0.0, g["ins_t"] - t)
    g["TOT"] = D + g["prot"]
    off, tb, DB = S["back_off"], S["back_t"], S["back_depth"]
    g["BW"], g["BH"] = W - 2 * off, H - 2 * off                       # dugnas - 3 mm mažesnis kiekvienai kraštinei
    g["gap"] = (W - 2 * t - g["BW"]) / 2                              # tarpas tarp priekio vidaus ir dugno išorės
    C = dict(DEF["cable"]); C.update(S.get("cable") or {})
    C["z"] = DB - C["from_back_front"]                                # skylės centras nuo fasado (dugno nugaros)
    C["y_"] = C["y"] if C.get("y") not in (None, "?") else None
    g["cab"] = C
    g["logo"] = None
    if S.get("logo"):
        lg = logo_from_pdf(S["logo"], base_dir)
        x0_, y0_, x1_, y1_ = lg.bounds
        g["logo"], g["logo_w"], g["logo_h"], g["logo_x"], g["logo_y"] = lg, x1_ - x0_, y1_ - y0_, x0_, y0_
        g["cut"] = lg.buffer(S["cut_gap"], join_style=2, mitre_limit=5)
        g["base"] = lg.buffer(S["base_off"], join_style=1)
        ring = lg.buffer(S["hole_off"], join_style=1)
        pts = []
        for p_ in getattr(ring, "geoms", [ring]):
            pts += PD2.ring_points(p_.exterior, S["hole_pitch"])
        g["studs"] = [(round(p.x, 1), round(p.y, 1)) for p in pts]
        g["base_parts"] = list(getattr(g["base"], "geoms", [g["base"]]))
    span_s = W - 2 * S["screw_end"]
    ns = max(1, round(span_s / S["screw_step"]))
    g["scr_x"] = [S["screw_end"] + span_s * k / ns for k in range(ns + 1)]
    # v231 (Rytis 2026-10-14): priekis prisukamas PER PERIMETRĄ - visi 4 atlankai; dešiniajame - ne ties laido išpjova
    span_v = H - 2 * S["screw_end"]
    nv_ = max(1, round(span_v / S["screw_step"]))
    g["scr_y"] = [S["screw_end"] + span_v * k / nv_ for k in range(nv_ + 1)]
    cy_ = (S.get("cable") or {}).get("y")
    g["scr_yr"] = [y_ for y_ in g["scr_y"] if cy_ in (None, "?") or abs(y_ - cy_) > 40]
    g["n_scr"] = 2 * len(g["scr_x"]) + len(g["scr_y"]) + len(g["scr_yr"])
    rho = json.load(open(os.path.join(HERE, "..", "assets", "svoris.json")))["density_kg_dm3"]
    front = (W * H + 2 * (W + H) * (D - t)) * t - (g["cut"].area * t if g["logo"] is not None else 0)
    back = (g["BW"] * g["BH"] + 2 * (g["BW"] + g["BH"]) * (DB - tb)) * tb
    pm = (g["base"].area * g["base_t"] + g["logo"].area * g["ins_t"]) if g["logo"] is not None else 0
    g["kg"] = ((front + back) * rho["al"] + pm * rho["pmma"]) / 1e6
    return g


# ===================================================================== pagalbinės
def draw_geom(geo, X, Y, fill=None, stroke=None, lw=0.1):
    PD2.draw_geom(geo, X, Y, fill=fill, stroke=stroke, lw=lw)


def vsegs(geo, x):
    return PD2.vsegs(geo, x)


def nice_scale(avail, size, opts=(2, 2.5, 4, 5, 6, 8, 10, 12, 15, 20)):
    return next((n for n in opts if size * MM / n <= avail), opts[-1])


def screw(Xz, Yy, z, y, s, up=True):
    """varžtas per priekio ir dugno atlankus (pjūvyje): galvutė išorėje"""
    rect(Xz(z) - 1.6 * s, Yy(y) - (1.2 * s if up else 0), 3.2 * s, 7 * s if up else 7 * s, fill=COL_STUD, lw=0.1)


# ===================================================================== 1 LAPAS
def sheet1(g, out):
    W, H, D, t = g["w"], g["h"], g["depth"], g["t"]
    tb, DB, off = g["back_t"], g["back_depth"], g["back_off"]
    bt, it_, pr = g["base_t"], g["ins_t"], g["prot"]
    lg = g["logo"]
    C = g["cab"]
    K.set_band(max(len(bom1(g)), 9) + 1)
    K.init(out + ".tmp", "sheet1")
    K.frame()
    top = K.IY0 + 112
    n = nice_scale(min(250, (K.VIEW_BOT - top - 230)), max(W, H), (5, 6, 8, 10, 12, 15))
    s = MM / n
    sl = f"1:{n:g}"
    # ---------------------------------------------------------------- FRONT VIEW
    fx = K.IX0 + 80
    X = lambda x: fx + x * s
    Yv = lambda y: top + y * s
    K.set_view(True)
    rect(X(0), Yv(0), W * s, H * s, fill=COL_BODY, lw=0.1)
    if lg is not None:
        draw_geom(lg, X, Yv, fill=COL_PLEX, lw=0.1)                # (išpjova + 0,7 - lape nesimato, DXF)
    K.set_view(False)
    if lg is not None:
        lx0, lx1 = g["logo_x"], g["logo_x"] + g["logo_w"]
        ly0, ly1 = g["logo_y"], g["logo_y"] + g["logo_h"]
        hchain(Yv(0) - D1, [X(0), X(lx0), X(lx1), X(W)], [Yv(0), Yv(ly0), Yv(ly0), Yv(0)],
               [f"{lx0:.0f}", f"{g['logo_w']:.0f}", f"{W - lx1:.0f}"], size=K.F_DIM_MAIN)
        vchain(X(0) - D1, [Yv(0), Yv(ly0), Yv(ly1), Yv(H)], [X(0), X(lx0), X(lx0), X(0)],
               [f"{ly0:.0f}", f"{g['logo_h']:.0f}", f"{H - ly1:.0f}"], size=K.F_DIM_MAIN)
    HM(X(0), X(W), Yv(0) - D2, f"{W:g}", Yv(0), Yv(0))
    VM(X(0) - D2, Yv(0), Yv(H), X(0), f"{H:g}")
    xc = (g["logo_x"] + g["logo_w"] / 2) if lg is not None else W / 2
    K.cut_plane(X(xc), Yv(0), Yv(H), "A", look="right", out=(46, 30))   # v276: žymė virš matmenų eilių (ne per 750 tekstą)
    K.balloon_auto(X(W * 0.08), Yv(H * 0.92), 1)
    if lg is not None:
        p_ = lg.representative_point()
        K.balloon_auto(X(p_.x), Yv(p_.y), 3)
    view_title(X(W / 2), top - 84, "FRONT VIEW", sl)
    # ---------------------------------------------------------------- RIGHT SIDE VIEW (laidas)
    sx = X(W) + 130
    Z = lambda z: sx + z * s                                          # z: 0 = fasadas (kairėje), D = priekis
    K.set_view(True)
    rect(Z(0), Yv(0), D * s, H * s, fill=COL_BODY, lw=0.1)            # priekio dešinysis atlankas
    if pr > 0 and lg is not None:
        for a_, b_ in vsegs(lg, g["logo_x"] + g["logo_w"]):
            pass
    yc = C["y_"] if C["y_"] is not None else None
    if yc is not None:
        hdia = C["hole_d"] or 10
        sw = C["slot_w"] or (hdia + 4)
        rect(Z(0), Yv(yc - sw / 2), (C["z"]) * s, sw * s, fill=white, lw=0.1)          # išpjova nuo laisvo krašto
        circle(Z(C["z"]), Yv(yc), sw / 2 * s, fill=white, lw=0.1)
        circle(Z(C["z"]), Yv(yc), hdia / 2 * s, fill=HexColor("#202020"), lw=0.1)     # tarpinė (dugno atlanke)
    for y_ in g["scr_yr"]:                                            # v231: varžtai per perimetrą (dešinysis atlankas)
        circle(Z(g["screw_edge"]), Yv(y_), max(1.6 * s, 0.9), fill=white, lw=0.1)
    K.set_view(False)
    line(Z(0) - 14, Yv(-10), Z(0) - 14, Yv(H + 10), 1.2, HexColor("#888888"))
    T(Z(0) - 20, Yv(H / 2), "FACADE", 7, color=K.GREY, rot=90, align="c")
    hchain(Yv(H) + D1, [Z(0), Z(DB), Z(D)], [Yv(H)] * 3, [f"{DB:g} (back)", f"{D - DB:g}"], size=K.F_DIM_MAIN)
    HM(Z(0), Z(D), Yv(H) + D2, f"{D:g}", Yv(H), Yv(H))
    if yc is not None:
        hchain(Yv(0) - D1, [Z(0), Z(C["z"]), Z(DB)], [Yv(yc)] * 3, [f"{C['z']:g}", f"{C['from_back_front']:g}"], size=K.F_DIM_MAIN)
        vchain(Z(D) + D1, [Yv(0), Yv(yc)], [Z(D)] * 2, [f"{yc:g}"], size=K.F_DIM_MAIN)
        K.balloon_auto(Z(C["z"]), Yv(yc), f"cable Ø{unk(C['hole_d'])} + grommet (back flange)", kind="tag")
        K.balloon_auto(Z(C["z"] * 0.4), Yv(yc + (C["slot_w"] or 14) / 2), "slot in front flange", kind="tag")
    else:
        T(Z(D / 2), Yv(-20), "cable hole: y from top = ?", 8, align="c", color=RED)
    view_title(Z(D / 2), top - 84, "RIGHT SIDE VIEW", sl + "  (cable)")
    # ---------------------------------------------------------------- SECTION A-A
    n5 = nice_scale(K.VIEW_BOT - top - 230, H, (4, 5, 6, 8, 10, 12))
    s5 = MM / n5
    ax0 = Z(D) + 140
    U = lambda z: ax0 + z * s5
    Ya = lambda y: top + y * s5
    K.set_view(True)
    rect(U(0), Ya(off), tb * s5, g["BH"] * s5, fill=COL_BACK, lw=0.1)                       # dugnas
    for y0 in (off, H - off - tb):
        rect(U(0), Ya(y0), DB * s5, tb * s5, fill=COL_BACK, lw=0.1)                         # dugno atlankai
    for y0 in (0, H - t):
        rect(U(0), Ya(y0), D * s5, t * s5, fill=COL_BODY, lw=0.1)                           # priekio atlankai
    segA = vsegs(g["cut"], xc) if lg is not None else []
    ya_ = 0
    for a_, b_ in segA + [(H, H)]:
        if a_ > ya_:
            rect(U(D - t), Ya(ya_), t * s5, (a_ - ya_) * s5, fill=COL_BODY, lw=0.1)          # priekis (be išpjovos)
        ya_ = b_
    if lg is not None:
        for a_, b_ in vsegs(g["base"], xc):
            rect(U(D - t - bt), Ya(a_), bt * s5, (b_ - a_) * s5, fill=COL_BASE, lw=0.1)
        for a_, b_ in vsegs(lg, xc):
            rect(U(D - t), Ya(a_), it_ * s5, (b_ - a_) * s5, fill=COL_PLEX, lw=0.1)
    for y_ in (t + 0.5, H - t - 0.5):
        rect(U(g["screw_edge"]) - 1.6 * s5, Ya(y_ - 1.2 if y_ < H / 2 else y_ - 6), 3.2 * s5, 7.2 * s5, fill=COL_STUD, lw=0.1)
    K.set_view(False)
    line(U(-6), Ya(-10), U(-6), Ya(H + 10), 1.2, HexColor("#888888"))
    hchain(Ya(H) + D1, [U(0), U(DB), U(D), U(D + pr)], [Ya(H)] * 4, [f"{DB:g}", f"{D - DB:g}", f"{pr:g}"], size=K.F_DIM_MAIN)
    HM(U(0), U(D + pr), Ya(H) + D2 + 10, f"{D + pr:g}", Ya(H), Ya(H))
    VM(U(D + pr) + D2, Ya(0), Ya(H), U(D), f"{H:g}")
    VM(U(-6) - 26, Ya(off), Ya(H - off), U(0), f"{g['BH']:g} (back)")
    bal = [(U(D - t / 2), Ya(H * 0.9), 1), (U(tb / 2), Ya(H * 0.85), 2), (U(DB * 0.6), Ya(off + tb / 2), 2),
           (U(g["screw_edge"]), Ya(t + 3), 8)]
    if segA:
        ym = (segA[0][0] + segA[0][1]) / 2
        bal += [(U(D - t + it_ / 2), Ya(ym), 3), (U(D - t - bt / 2), Ya(segA[0][1] + 12), 4)]
    for tx_, ty_, lb_ in bal:
        K.balloon_auto(tx_, ty_, lb_)
    # v231 (Rytis 2026-10-14): LED - ant DUGNO GALINĖS PLOKŠTUMOS (vidinis paviršius), ne ant kraštinių
    K.set_view(True)
    for k_ in range(4):
        ym_ = off + g["BH"] * (k_ + 0.5) / 4
        rect(U(tb), Ya(ym_ - 20), 10 * s5, 40 * s5, fill=HexColor("#F2E28C"), lw=0.3)
    K.set_view(False)
    K.balloon_auto(U(tb + 5), Ya(off + g["BH"] * 0.625), 6)
    T(U(DB) + 4, Ya(H / 2), "LED on back base: ?", 7, align="c", color=RED, rot=90)
    view_title(U(D / 2), top - 84, "SECTION A-A", f"1:{n5:g}")
    # ---------------------------------------------------------------- v232 (Rytis): EXPLODED - kuo didesnis (dešinė kolona per
    #  visą aukštį); TOP VIEW mažiau svarbus - 2 eilėje šalia 3D
    ex0 = ax0 + (D + pr) * s5 + 120
    exw, exh = K.IX1 - 30 - ex0, K.VIEW_BOT - 40 - (top - 50)
    try:
        exploded(g, (ex0, top - 50, exw, exh))
        view_title(ex0 + exw / 2, K.VIEW_BOT - 22, "ASSEMBLY - EXPLODED VIEW",
                   "back 2 (to facade) + LED 6 on back base - base 4 + insert 3 - front 1; screws 8 on perimeter; inside white")
    except Exception as e:
        print("  ! exploded:", e)
    y3 = max(Yv(H), Ya(H)) + D2 + 60
    h3 = K.VIEW_BOT - y3 - 30
    try:
        scene3d(g, (K.IX0 + 40, y3, 230, h3))
        view_title(K.IX0 + 40 + 115, y3 + h3 + 18, "3D VIEW", "ILLUSTRATIVE - NOT TO SCALE")
    except Exception as e:
        print("  ! 3D:", e)
    # TOP VIEW (varžtai) - 2 eilė
    tx0 = K.IX0 + 40 + 230 + 90
    Xt = lambda x: tx0 + x * s
    Zt = lambda z: y3 + 50 + (D + pr - z) * s                       # z = D (priekis) viršuje
    K.set_view(True)
    rect(Xt(0), Zt(D), W * s, D * s, fill=COL_BODY, lw=0.1)
    if lg is not None and pr > 0:
        rect(Xt(g["logo_x"]), Zt(D + pr), g["logo_w"] * s, pr * s, fill=COL_PLEX, lw=0.1)
    for x_ in g["scr_x"]:
        circle(Xt(x_), Zt(g["screw_edge"]), max(1.6 * s, 0.9), fill=white, lw=0.1)
    K.set_view(False)
    xs_ = [0] + g["scr_x"] + [W]
    hchain(Zt(0) + D1, [Xt(v) for v in xs_], [Zt(g["screw_edge"])] * len(xs_), [f"{b - a:.0f}" for a, b in zip(xs_, xs_[1:])],
           size=K.F_DIM_MAIN)
    vchain(Xt(W) + D1, [Zt(g["screw_edge"]), Zt(0)], [Xt(W)] * 2, [f"{g['screw_edge']:g}"], size=K.F_DIM_MAIN)
    T(Xt(W / 2), Zt(0) + D2 + 12, f"screws (8) on PERIMETER (all 4 flanges): {g['n_scr']} pcs., holes Ø3.2, "
      f"{g['screw_edge']:g} from edge", 7, align="c", color=K.GREY)
    view_title(Xt(W / 2), Zt(0) + D2 + 48, "TOP VIEW", sl)
    band(g, "1 / 2", "", main_data1(g), bom1(g), detail_b(g), f"{sl} / 1:{n5:g}")
    K.save(out)


def bom1(g):
    W, H = g["w"], g["h"]
    rows = [[1, f"Front tray {W:g}x{H:g}x{g['depth']:g}, in white", f"Alu {g['t']:g} mm", g["body_finish"] or "", "1 pc."],
            [2, f"Back tray {g['BW']:g}x{g['BH']:g}x{g['back_depth']:g}, in white", f"Alu {g['back_t']:g} mm",
             g["back_finish"] or "", "1 pc."]]
    if g["logo"] is not None:
        rows += [[3, f"Insert {g['ins_t']:g} mm, GLUED to base (protr. {g['prot']:g})", f"Plexi {g['plexi']}", g["film"] or "-",
                  f"1 pc. {g['logo'].area / 1e6:.3f} m²"],
                 [4, f"Base {g['base_t']:g} mm, {len(g['studs'])} x Ø{g['hole_d']:g} (DXF)", f"Plexi {g['plexi']}", "-",
                  f"1 pc. {g['base'].area / 1e6:.3f} m²"],
                 [5, "Stud (welded inside front) + nut", "?", "-", f"{len(g['studs'])} pcs."]]
    rows += [[6, "LED on back base (inside)", "LED", "-", "?"],                  # v262: be modelių / specifikacijų
             [7, f"Cable gland / rubber grommet Ø{unk(g['cab']['hole_d'])}", g["cab"].get("grommet") or "?", "-", "1 pc."],
             [8, "Screw front -> back, perimeter", "-", "-", f"{g['n_scr']} pcs."],
             [9, "Fixing to facade through back", "screws + anchors", "-", "?"]]
    return rows


def main_data1(g):
    return [["Product", "P10_lightbox_singlesided"],
            ["Size", f"{g['w']:g} x {g['h']:g} x {g['depth']:g} (+ {g['prot']:g})"],
            ["Front", f"Alu {g['t']:g}, {g['body_finish'] or '?'}"],
            ["Back", f"Alu {g['back_t']:g}, {g['back_depth']:g} deep, -{g['back_off']:g}/side"],
            ["Glass", f"{g['glass']} mm, cut-out + {g['cut_gap']:g}"],
            ["LED / PSU", "?"],
            ["Cable", f"right side, top; Ø{unk(g['cab']['hole_d'])} + grommet"],
            ["Qty", f"{g['qty']}"],
            ["Weight (calc.)", f"≈ {g['kg']:.1f} kg / pcs, excl. PSU"]]


def detail_b(g):
    """DETAIL B - pjūvis per visą gylį TRIJOSE vietose VIRŠUS / STIKLAS / APAČIA (taisyklė 20)"""
    W, H, D, t = g["w"], g["h"], g["depth"], g["t"]
    tb, DB, off = g["back_t"], g["back_depth"], g["back_off"]
    bt, it_, pr = g["base_t"], g["ins_t"], g["prot"]

    def detail(X_P6, BY0, W_P6, BH):
        lg = g["logo"]
        xc = (g["logo_x"] + g["logo_w"] / 2) if lg is not None else W / 2
        zt = off + tb + 18
        zones = [("TOP", 0.0, zt)]
        if lg is not None:
            seg = vsegs(g["cut"], xc)
            if seg:
                c0 = seg[0][0]
                zones.append(("GLASS", c0 - g["hole_off"] - 10, c0 + 12))
        zones.append(("BOTTOM", H - zt, H))
        gap = 9
        tot = sum(b - a for _, a, b in zones)
        sc = next(n for n in (1, 1.5, 2, 2.5, 3, 4, 5, 6, 8) if tot * MM / n <= BH - 12 - 26 - 14 - gap * (len(zones) - 1)
                  and (D + pr) * MM / n <= W_P6 - 80)
        s3 = MM / sc
        K.header(X_P6, BY0, W_P6, f"DETAIL B - SECTION TOP / GLASS / BOTTOM  1:{sc:g}")
        rect(X_P6, BY0 + 12, W_P6, BH - 12, lw=0.6)
        ox = X_P6 + (W_P6 - (D + pr) * s3) / 2
        U = lambda z: ox + z * s3
        ys = BY0 + 12 + 26
        bal = []
        for name, a_, b_ in zones:
            Yz = lambda y, a_=a_, ys=ys: ys + (y - a_) * s3
            K.set_view(True)
            if name != "GLASS":
                topz = name == "TOP"
                rect(U(D - t), Yz(a_), t * s3, (b_ - a_) * s3, fill=COL_BODY, lw=0.1)
                rect(U(0), Yz(off if topz else b_ - off - (b_ - a_) + (b_ - a_) - 0), tb * s3, 0.01, lw=0.1)
                yfb = off if topz else H - off - tb
                rect(U(0), Yz(off if topz else a_), tb * s3, ((b_ - off) - a_ if topz else (H - off) - a_) * s3 if not topz else (b_ - off) * s3,
                     fill=COL_BACK, lw=0.1)
                rect(U(0), Yz(yfb), DB * s3, tb * s3, fill=COL_BACK, lw=0.1)
                yff = 0 if topz else H - t
                rect(U(0), Yz(yff), D * s3, t * s3, fill=COL_BODY, lw=0.1)
                yy = 0 if topz else H
                rect(U(g["screw_edge"]) - 1.6 * s3, Yz(yy - 1.2 if topz else yy - 7.2), 3.2 * s3, 7.2 * s3, fill=COL_STUD, lw=0.1)
                rect(U(g["screw_edge"]) - 3 * s3, Yz(-1.2 if topz else H), 6 * s3, 1.2 * s3, fill=COL_STUD, lw=0.1)
                if topz:
                    bal += [(U(D - t / 2), Yz(a_ + (b_ - a_) * 0.8), 1), (U(DB * 0.7), Yz(yfb + tb / 2), 2),
                            (U(g["screw_edge"]), Yz(1), 8)]
            else:
                c0 = vsegs(g["cut"], xc)[0][0]
                l0 = vsegs(lg, xc)[0][0]
                bb0 = vsegs(g["base"], xc)[0][0]
                ysd = l0 - g["hole_off"]
                rect(U(D - t), Yz(a_), t * s3, (c0 - a_) * s3, fill=COL_BODY, lw=0.1)
                rect(U(D - t - bt), Yz(max(a_, bb0)), bt * s3, (b_ - max(a_, bb0)) * s3, fill=COL_BASE, lw=0.1)
                rect(U(D - t), Yz(l0), it_ * s3, (b_ - l0) * s3, fill=COL_PLEX, lw=0.1)
                rect(U(D - t - bt - 6), Yz(ysd - 2), (bt + 6) * s3, 4 * s3, fill=COL_STUD, lw=0.1)         # ilgasriegis iš vidaus
                rect(U(D - t - bt - 3), Yz(ysd - 3.5), 3 * s3, 7 * s3, fill=HexColor("#8C8C8C"), lw=0.1)   # veržlė
                rect(U(0), Yz(a_), tb * s3, (b_ - a_) * s3, fill=COL_BACK, lw=0.1)
                _lm = min(30.0, (b_ - a_) - 8)                                                      # v232: LED ant dugno
                rect(U(tb), Yz(a_ + 4), 10 * s3, _lm * s3, fill=HexColor("#F2E28C"), lw=0.3)
                bal.append((U(tb + 5), Yz(a_ + 4 + _lm / 2), 6))
                bal += [(U(D - t + it_ / 2), Yz(b_ - 3), 3), (U(D - t - bt / 2), Yz(b_ - 3), 4), (U(D - t - bt - 4), Yz(ysd), 5),
                        (U(tb / 2), Yz(b_ - 6), 2)]
            K.set_view(False)
            for yy, show in ((Yz(a_), name != "TOP"), (Yz(b_), name != "BOTTOM")):
                if show:
                    xa_, xb_ = U(-4), U(D + pr) + 4
                    pts = [(xa_ + (xb_ - xa_) * k / 8, yy + (1.5 if k % 2 else -1.5)) for k in range(9)]
                    for p0, p1 in zip(pts, pts[1:]):
                        line(p0[0], p0[1], p1[0], p1[1], 0.2)
            T(X_P6 + 5, Yz((a_ + b_) / 2) + 3, name, 6.5, color=K.GREY)
            ys += (b_ - a_) * s3 + gap
        cxm = U((D + pr) / 2)
        left = sorted([q for q in bal if q[0] < cxm], key=lambda q: q[1])
        right = sorted([q for q in bal if q[0] >= cxm], key=lambda q: q[1])
        y0_, y1_ = BY0 + 12 + 30, BY0 + BH - 22
        for lst, bx in ((left, U(0) - 30), (right, U(D + pr) + 30)):
            for k, (tx_, ty_, lab) in enumerate(lst):
                K.leader(tx_, ty_, bx, y0_ + (y1_ - y0_) * (k + 0.5) / max(len(lst), 1), lab, 6)
        T(X_P6 + W_P6 / 2, BY0 + BH - 4, f"gap {g['cut_gap']:g}; insert GLUED to base; studs welded inside; back inside front", 6.5,
          align="c", color=K.GREY)
    return detail


# ===================================================================== 3D
def _box(sc, x0, y0, z0, dx, dy, dz, col, edge=EDGE):
    sc.box((x0, y0, z0), (dx, 0, 0), (0, dy, 0), (0, 0, dz), col, edge=edge)


def scene3d(g, box):
    import r3d
    W, H, D, t = g["w"], g["h"], g["depth"], g["t"]
    sc = r3d.Scene(yaw=-32, pitch=18)
    face = sbox(0, 0, W, H)
    if g["logo"] is not None:
        face = face.difference(g["cut"])
    PD2._slab(sc, face, D - t, D, COL_BODY, lambda u, v, w: (u, H - v, w), edge=EDGE)
    for y0 in (0, H - t):
        _box(sc, 0, H - y0 - t, 0, W, t, D - t, COL_BODY)
    for x0 in (0, W - t):
        _box(sc, x0, t, 0, t, H - 2 * t, D - t, COL_BODY)
    if g["logo"] is not None:
        PD2._slab(sc, g["logo"], D - t, D - t + g["ins_t"], COL_PLEX, lambda u, v, w: (u, H - v, w), edge=EDGE)
    sc.render(box)


def exploded(g, box):
    import r3d
    W, H, D, t = g["w"], g["h"], g["depth"], g["t"]
    tb, DB, off = g["back_t"], g["back_depth"], g["back_off"]
    M = max(W, H)
    sc = r3d.Scene(yaw=-55, pitch=14)
    sc.flat = False
    anc = {}
    # dugnas (prie fasado): plokštė + atlankai, išorė - spalva, vidus - baltas (taisyklė 21)
    _box(sc, off, off, 0, g["BW"], g["BH"], tb, COL_BACK)
    _box(sc, off, off, tb, g["BW"], g["BH"], 0.3, COL_INWHITE)
    for y0 in (off, H - off - tb):
        _box(sc, off, y0, 0, g["BW"], tb, DB, COL_BACK)
    for x0 in (off, W - off - tb):
        _box(sc, x0, off + tb, 0, tb, g["BH"] - 2 * tb, DB, COL_BACK)
    anc[2] = (off + g["BW"] * 0.2, H - off, DB * 0.5)
    for i_ in range(3):                                               # v231: LED ant dugno galinės plokštumos
        for j_ in range(3):
            _box(sc, off + g["BW"] * (i_ + 0.5) / 3 - 20, off + g["BH"] * (j_ + 0.5) / 3 - 12, tb + 0.3, 40, 24, 6, HexColor("#F2E28C"))
    anc[6] = (off + g["BW"] * 0.5, off + g["BH"] * 0.5, tb + 6)
    e_b, e_i, e_f = 0.45 * M, 0.75 * M, 1.05 * M
    if g["logo"] is not None:
        holes = unary_union([Point(u, v).buffer(g["hole_d"] / 2, 4) for u, v in g["studs"]])
        PD2._slab(sc, g["base"].difference(holes), e_b, e_b + g["base_t"], HexColor("#E4E4DE"),
                  lambda u, v, w: (u, H - v, w), edge=EDGE)
        PD2._slab(sc, g["logo"], e_i, e_i + g["ins_t"], COL_PLEX, lambda u, v, w: (u, H - v, w), edge=EDGE)
        rp = g["base"].difference(g["logo"].buffer(4)).representative_point()
        anc[4] = (rp.x, H - rp.y, e_b + g["base_t"])
        lp = g["logo"].representative_point()
        anc[3] = (lp.x, H - lp.y, e_i + g["ins_t"])
    face = sbox(0, 0, W, H)
    if g["logo"] is not None:
        face = face.difference(g["cut"])
    PD2._slab(sc, face, e_f + D - t, e_f + D, COL_BODY, lambda u, v, w: (u, H - v, w), edge=EDGE)
    for y0 in (0, H - t):
        _box(sc, 0, H - y0 - t, e_f, W, t, D - t, COL_BODY)
    for x0 in (0, W - t):
        _box(sc, x0, t, e_f, t, H - 2 * t, D - t, COL_BODY)
    anc[1] = (W * 0.1, H * 0.12, e_f + D)
    sc.render(box)
    V = sc.V
    reg = (box[0] - 20, box[1] - 10, box[0] + box[2] + 20, box[1] + box[3] + 10)
    for k, p in anc.items():
        x_, y_ = V.S(*p)
        K.balloon_auto(x_, K.H - y_, k, region=reg)


# ===================================================================== 2 LAPAS - CAD: padėklų išklotinės (priekis, dugnas)
def flat_tray(W, H, Dp, t):
    """folded v173: lenkimo linijos = išoriniai matmenys W x H; atlankas = Dp - t; šonai t trumpesni (vidun)"""
    FL = Dp - t
    x0, x1, y0, y1 = FL, FL + W, FL, FL + H
    F, WF = W + 2 * FL, H + 2 * FL
    outline = Polygon([(x0, 0), (x1, 0), (x1, y0 + t), (F, y0 + t), (F, y1 - t), (x1, y1 - t), (x1, WF), (x0, WF),
                       (x0, y1 - t), (0, y1 - t), (0, y0 + t), (x0, y0 + t)])
    return outline, (x0, y0, x1, y1), FL, (F, WF)


def flats(g):
    """priekio ir dugno išklotinės (y ŽEMYN, kaip lape): kontūras, lenkimo stačiakampis, skylės, logotipas, išpjovos"""
    W, H, D, t = g["w"], g["h"], g["depth"], g["t"]
    tb, DB, off = g["back_t"], g["back_depth"], g["back_off"]
    C = g["cab"]
    # PRIEKIS (iš priekio): atlanko laisvas kraštas = fasadas (z = 0); varžtai 7 nuo laisvo krašto
    ofr, bfr, FLf, (Ff, WFf) = flat_tray(W, H, D, t)
    x0, y0, x1, y1 = bfr
    hf = [(x0 + u, g["screw_edge"]) for u in g["scr_x"]] + [(x0 + u, WFf - g["screw_edge"]) for u in g["scr_x"]]
    hf_s = [(g["screw_edge"], y0 + v) for v in g["scr_y"]] + [(Ff - g["screw_edge"], y0 + v) for v in g["scr_yr"]]
    slots = []
    if C["y_"] is not None:                                        # dešinysis atlankas: x nuo x1 (lenkimas, z = D-t) iki Ff (z = 0)
        sw = C["slot_w"] or ((C["hole_d"] or 10) + 4)
        zc = C["z"]
        xs = Ff - zc                                               # skylės centras atlanke
        sl_ = unary_union([sbox(xs, y0 + C["y_"] - sw / 2, Ff + 1, y0 + C["y_"] + sw / 2),
                           Point(xs, y0 + C["y_"]).buffer(sw / 2, 24)])
        ofr = ofr.difference(sl_)
        slots.append(sl_)
    front = dict(outline=ofr, bend=bfr, holes=hf, holes_s=hf_s, FL=FLf, size=(Ff, WFf), ox=x0, oy=y0)
    # DUGNAS (iš priekio, vidus): atlanko laisvas kraštas = dugno priekis (z = DB); varžtų skylės ties z = 7 nuo fasado
    obk, bbk, FLb, (Fb, WFb) = flat_tray(g["BW"], g["BH"], DB, tb)
    bx0, by0, bx1, by1 = bbk
    zs = g["screw_edge"]                                           # nuo fasado (dugno nugaros = lenkimo linija)
    hb = [(bx0 + (u - off), by0 - zs) for u in g["scr_x"]] + [(bx0 + (u - off), by1 + zs) for u in g["scr_x"]]
    hb_s = [(bx0 - zs, by0 + (v - off)) for v in g["scr_y"]] + [(bx1 + zs, by0 + (v - off)) for v in g["scr_yr"]]
    cab = None
    if C["y_"] is not None:
        cab = (bx1 + C["z"], by0 + (C["y_"] - off), (C["hole_d"] or 10) / 2)
    back = dict(outline=obk, bend=bbk, holes=hb, holes_s=hb_s, FL=FLb, size=(Fb, WFb), cable=cab, ox=bx0, oy=by0)
    return front, back


def sheet2(g, out):
    SV._CAD = True
    try:
        _sheet2(g, out)
    finally:
        SV._CAD = False


def _sheet2(g, out):
    W, H, D, t = g["w"], g["h"], g["depth"], g["t"]
    fr, bk = flats(g)
    K.set_band(7)
    K.init(out + ".tmp", "sheet2")
    K.frame()
    top = K.IY0 + 112
    Fw, Fh = fr["size"]; Bw, Bh = bk["size"]
    avail_w = (K.IX1 - K.IX0 - 60 - 4 * 70) / 2
    n = nice_scale(min(avail_w * Fh / max(Fw, 1), K.VIEW_BOT - top - 120), Fh, (5, 6, 8, 10, 12, 15))
    s = MM / n
    blk = (K.IX1 - K.IX0) / 2
    for i, (ttl, d, mat) in enumerate((("FRONT 1 - FLAT PATTERN (face out)", fr, f"Alu {g['t']:g}"),
                                       ("BACK 2 - FLAT PATTERN (inside view)", bk, f"Alu {g['back_t']:g}"))):
        Fw_, Fh_ = d["size"]
        ox = K.IX0 + i * blk + (blk - Fw_ * s) / 2
        oy = top + (K.VIEW_BOT - top - 90 - Fh_ * s) / 2
        X = lambda x, ox=ox: ox + x * s
        Y = lambda y, oy=oy: oy + y * s
        draw_geom(d["outline"], X, Y, fill=white, lw=K.HAIR)
        bx0, by0, bx1, by1 = d["bend"]
        rect(X(bx0), Y(by0), (bx1 - bx0) * s, (by1 - by0) * s, lw=K.HAIR, dash=(4, 2))
        for hx, hy in d["holes"] + d["holes_s"]:
            circle(X(hx), Y(hy), max(1.6 * s, 0.8), lw=0.2)
        _hl = [q for q in d["holes_s"] if q[0] < Fw_ / 2]                # kairiojo atlanko skylės - grandinė kairėje
        if _hl:
            ys_ = [0] + [hy for _, hy in _hl] + [Fh_]
            vchain(X(0) - D1, [Y(v) for v in ys_], [X(_hl[0][0])] * len(ys_), [f"{b - a:.0f}" for a, b in zip(ys_, ys_[1:])],
                   size=K.F_DIM_FRAME)
        if i == 0 and g["logo"] is not None:
            draw_geom(affinity.translate(g["cut"], d["ox"], d["oy"]), X, Y, lw=0.3)
            for sx_, sy_ in g["studs"]:
                circle(X(d["ox"] + sx_), Y(d["oy"] + sy_), max(g["mark_d"] / 2 * s, 0.6), lw=0.2, dash=(1, 1))
        if i == 1 and d.get("cable"):
            cx_, cy_, r_ = d["cable"]
            circle(X(cx_), Y(cy_), r_ * s, lw=K.HAIR)
            K.balloon_auto(X(cx_), Y(cy_), f"cable Ø{unk(g['cab']['hole_d'])} + grommet", kind="tag")
        # v276 ISO: iškeltinė - iki PIRMO kontūro taško (atlanko kampo), ne išilgai išpjovos krašto (linija ant linijos)
        hchain(Y(0) - D1, [X(0), X(bx0), X(bx1), X(Fw_)], [Y(by0), Y(0), Y(0), Y(by0)],
               [f"{bx0:g}", f"{bx1 - bx0:g}", f"{Fw_ - bx1:g}"], size=K.F_DIM_FRAME)
        HM(X(0), X(Fw_), Y(0) - D2, f"{Fw_:g}", Y(by0), Y(by0))
        vchain(X(Fw_) + D1, [Y(0), Y(by0), Y(by1), Y(Fh_)], [X(bx1), X(Fw_), X(Fw_), X(bx1)], [f"{by0:g}", f"{by1 - by0:g}", f"{Fh_ - by1:g}"],
               size=K.F_DIM_FRAME)
        VM(X(Fw_) + D2 + 20, Y(0), Y(Fh_), X(Fw_), f"{Fh_:g}")
        hy0 = d["holes"][-1][1]                                     # apatinio atlanko skylės - grandinė apačioje
        xs_ = [0] + [hx for hx, _ in d["holes"][len(g["scr_x"]):]] + [Fw_]
        hchain(Y(Fh_) + D1, [X(v) for v in xs_], [Y(hy0)] * len(xs_), [f"{b - a:.0f}" for a, b in zip(xs_, xs_[1:])],
               size=K.F_DIM_FRAME)
        T(X(Fw_ / 2), Y(Fh_) + D2 + 14, f"{mat}, folded v173 (bend lines = outside), flanges {d['FL']:g}, holes Ø3.2", 7,
          align="c", color=K.GREY)
        view_title(X(Fw_ / 2), top - 84, ttl, f"1:{n:g}")
    K.set_view(False)

    def detail(X_P6, BY0, W_P6, BH):
        K.main_data(X_P6, BY0, W_P6, BH, [
            ["Front", f"{W:g}x{H:g}x{D:g}, Alu {t:g}"],
            ["Back", f"{g['BW']:g}x{g['BH']:g}x{g['back_depth']:g}, Alu {g['back_t']:g}"],
            ["Gap", f"{g['gap']:g} mm / side (back in front)"],
            ["Screws", f"{g['n_scr']} x, perimeter, {g['screw_edge']:g} from flange edge"],
            ["Cable", f"z {g['cab']['z']:g} from facade, y {unk(g['cab']['y_'])}"]], title="TRAYS", lab_w=64)
    md = [["Bend rule", "folded v173, no K-factor"], ["Flanges front", f"{D - t:g}"],
          ["Flanges back", f"{g['back_depth'] - g['back_t']:g}"], ["Qty", f"{g['qty']}"]]
    rows = [[1, "Front tray (DXF)", f"Alu {t:g}", g["body_finish"] or "", "1 pc."],
            [2, "Back tray (DXF)", f"Alu {g['back_t']:g}", g["back_finish"] or "", "1 pc."]]
    band(g, "2 / 2", "", md, rows, detail, f"1:{n:g}")
    K.save(out)


# ===================================================================== DXF
def write_dxf(g, path):
    import ezdxf
    doc = ezdxf.new("R2010"); doc.units = ezdxf.units.MM
    for ln, col in (("CUT", 7), ("BEND_UP_90", 1), ("HOLES_D3.2", 3), ("CUTOUT_LOGO", 6), ("MARK_D6_STUDS", 5),
                    ("CABLE_HOLE", 4), ("PLEXI_BASE_3MM", 2), ("PLEXI_BASE_HOLES_D8", 2), ("PLEXI_INSERT", 30), ("TEXT", 8)):
        doc.layers.add(ln, color=col)
    m = doc.modelspace()
    fr, bk = flats(g)
    ox = 0.0
    for nm, d in (("FRONT 1", fr), ("BACK 2", bk)):
        Fw_, Fh_ = d["size"]
        Q = lambda x, y, ox=ox, Fh_=Fh_: (round(ox + x, 3), round(Fh_ - y, 3))
        for pg in getattr(d["outline"], "geoms", [d["outline"]]):
            for ring in [pg.exterior] + list(pg.interiors):
                m.add_lwpolyline([Q(*c) for c in ring.coords], close=True, dxfattribs={"layer": "CUT"})
        bx0, by0, bx1, by1 = d["bend"]
        m.add_lwpolyline([Q(bx0, by0), Q(bx1, by0), Q(bx1, by1), Q(bx0, by1)], close=True, dxfattribs={"layer": "BEND_UP_90"})
        for hx, hy in d["holes"] + d["holes_s"]:
            m.add_circle(Q(hx, hy), 1.6, dxfattribs={"layer": "HOLES_D3.2"})
        if nm == "FRONT 1" and g["logo"] is not None:
            for pg in getattr(g["cut"], "geoms", [g["cut"]]):
                for ring in [pg.exterior] + list(pg.interiors):
                    m.add_lwpolyline([Q(d["ox"] + x, d["oy"] + y) for x, y in ring.coords], close=True, dxfattribs={"layer": "CUTOUT_LOGO"})
            for sx_, sy_ in g["studs"]:
                m.add_circle(Q(d["ox"] + sx_, d["oy"] + sy_), g["mark_d"] / 2, dxfattribs={"layer": "MARK_D6_STUDS"})
        if d.get("cable"):
            cx_, cy_, r_ = d["cable"]
            m.add_circle(Q(cx_, cy_), r_, dxfattribs={"layer": "CABLE_HOLE"})
        m.add_text(f"{nm}: FLAT {Fw_:g} x {Fh_:g} - " + ("FACE OUT" if nm == "FRONT 1" else "INSIDE VIEW") +
                   ("" if g["cab"]["hole_d"] else " - cable hole / slot size = ? (10 / 14 assumed)"),
                   dxfattribs={"layer": "TEXT", "height": 8}).set_placement((ox, -30))
        ox += Fw_ + 100
    if g["logo"] is not None:
        bx0, by0, bx1, by1 = g["base"].bounds
        oy = -(by1 - by0) - 120
        Q = lambda x, y: (round(x - bx0, 3), round(oy + (by1 - y), 3))
        for pg in g["base_parts"]:
            for ring in [pg.exterior] + list(pg.interiors):
                m.add_lwpolyline([Q(*c) for c in ring.coords], close=True, dxfattribs={"layer": "PLEXI_BASE_3MM"})
        for sx_, sy_ in g["studs"]:
            m.add_circle(Q(sx_, sy_), g["hole_d"] / 2, dxfattribs={"layer": "PLEXI_BASE_HOLES_D8"})
        cx = (bx1 - bx0) + 100
        for pg in getattr(g["logo"], "geoms", [g["logo"]]):
            for ring in [pg.exterior] + list(pg.interiors):
                m.add_lwpolyline([(round(cx + x - bx0, 3), round(oy + (by1 - y), 3)) for x, y in ring.coords], close=True,
                                 dxfattribs={"layer": "PLEXI_INSERT"})
        m.add_text(f"BASE {g['base_t']:g} mm + INSERT {g['ins_t']:g} mm (GLUED)", dxfattribs={"layer": "TEXT", "height": 8}).set_placement((0, oy - 30))
    doc.saveas(path)
    return path


def main(spec_path, out):
    S = dict(DEF); S.update(json.load(open(spec_path, encoding="utf-8")))
    global COL_BODY, COL_BACK
    if str(S.get("body_finish", "")).upper().startswith("RAL"):
        COL_BODY = HexColor(K.ralhex(S["body_finish"]))
    if str(S.get("back_finish", "")).upper().startswith("RAL"):
        COL_BACK = HexColor(K.ralhex(S["back_finish"]))
    K.F_DIM_FRAME = K.F_DIM_MAIN
    g = geom(S, os.path.dirname(os.path.abspath(spec_path)))
    p1, p2 = out + ".1.pdf", out + ".2.pdf"
    for fn, pp in ((sheet1, p1), (sheet2, p2)):
        K.auto_begin("collect"); K.AUTO["region"] = None
        fn(g, pp)
        pl = K.auto_place(pp)
        K.auto_begin("draw", pl); K.AUTO["region"] = None
        fn(g, pp)
        K.auto_begin(None)
    import pymupdf as fitz
    d = fitz.open()
    for pp in (p1, p2):
        d.insert_pdf(fitz.open(pp))
    d.save(out, garbage=3, deflate=True); d.close()
    K.pdf_fix_fonts(out)
    for pp in (p1, p2, p1 + ".tmp", p2 + ".tmp"):
        os.path.exists(pp) and os.remove(pp)
    dxf = write_dxf(g, os.path.splitext(out)[0] + "_gamyba.dxf")
    print("OK", out, dxf, f"svoris {g['kg']:.1f} kg; dugnas {g['BW']:g}x{g['BH']:g}, tarpas {g['gap']:g}/pusei;"
          + (f" logotipas {g['logo_w']:.0f}x{g['logo_h']:.0f}, ilgasriegiai {len(g['studs'])}" if g["logo"] is not None else ""))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
