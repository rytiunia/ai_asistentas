#!/usr/bin/env python3
"""Dvipusė šviesdėžė nuo fasado - 2 lapai (v134-v135, Rytis 2026-10-12).

v134: „paprasčiausia dvipusė šviesdėžė nuo fasado - kojos tai pailgintos rėmo dalys, apsijuosia aliumu, stiklas abiejose
pusėse tvirtinasi kaip P6_3mm". Etalonas assets/etalonai/sviesdeze_dvipuse_nuo_sienos.pdf (500 x 500 x 100, 1:8).
v135: „reikia detaliau - nėra rėmo matmenų, nėra bendrų matmenų tarp montavimo plokščių skylių x/y, neaišku kaip LED dedasi
ir kokie. P6_3mm tipo tvirtinimai - stiklas visada didesnis už korpusą, korpusas mažesnis už stiklą 1.5-2 mm."
  -> 1 lapas: GENERAL ASSEMBLY (priekis, vaizdas iš sienos = gręžimo schema su visais skylių matmenimis x / y, pjūvis A-A,
     3D, DETAIL B 1:1); 2 lapas: FRAME + LED (rėmo gamybinis vaizdas su visais matmenimis, LED vietos ir žingsnis,
     pjūvis C-C per LED, padas 1:2, rėmo pjaustymo sąrašas).
  -> stiklas (plexi) = gabaritas W x H; korpusas (Alu juosta) kiekvienoje pusėje mažesnis per `face_over` (1,5 mm).
  -> LED: Kaisen DUOLITE (dvipusėms dėžėms, šviečia skersai dėžės 10° x 65°) ant rėmo skersinio, pagal Kaisen lentelę
     (dėžė 1000 x H, gylis, žingsnis -> lx); PSU Kaisen KPS IP67 <= 75 %.
Pozicijos kaip etalono Parts List: 1 rėmas + kojos, 1A padas, 2 korpusas, 3 / 5 plexi, 4 / 6 PVC juosta, 7 LED + PSU, 8 varžtai.
Naudojimas:  python3 sviesdeze.py spec.json out.pdf
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lapas_core as K  # noqa: E402
from lapas_core import T, line, rect, poly, circle, hdim, vchain, hchain, leader, view_title, MM  # noqa: E402
from reportlab.lib.colors import HexColor, white  # noqa: E402

DEF = {"client": "", "title": "DOUBLE-SIDED LIGHTBOX, WALL MOUNTED (PROJECTING)", "order_no": "", "drawing_no": "",
       "date": "2026-10-12", "rev": "A", "qty": 1,
       "w": 500, "h": 500, "depth": 100, "face_thk": 3.0, "face_over": 1.5, "band_thk": 1.5, "frame": [30, 30, 2],
       "leg_len": 100, "flange": [100, 100, 8], "flange_r": 10, "hole_d": 10, "hole_pitch": 64,
       "body_finish": "RAL ____", "frame_finish": "RAL ____", "face": "3 mm opal white plexiglass",
       "pvc_edge": [3, 15], "screw_step": 150, "led": "DS15", "led_rows": None, "led_pitch": None,
       "cable": "", "anchors": "", "scale_ga": 8}
COL_BODY, COL_FRAME, COL_FACE, COL_PVC, COL_FL, COL_LED = (HexColor("#9C9C9C"), HexColor("#B4B4B4"), HexColor("#F4F4F2"),
                                                           HexColor("#C8C8C8"), HexColor("#8C8C8C"), HexColor("#F2C230"))
EDGE = HexColor("#555555")


def geom(S):
    g = dict(S)
    W_, H_, D = S["w"], S["h"], S["depth"]
    ov, tb, (fa, fb, ft) = S["face_over"], S["band_thk"], S["frame"]
    g["BW"], g["BH"] = W_ - 2 * ov, H_ - 2 * ov                   # korpusas (Alu juosta) - mažesnis už stiklą
    g["FW"], g["FH"] = g["BW"] - 2 * tb, g["BH"] - 2 * tb          # rėmo išorė
    g["x0"] = ov + tb                                               # rėmo kairė nuo stiklo krašto
    g["ax"] = ov + tb + fa / 2                                      # kojos ašis nuo stiklo viršaus / apačios
    g["xb"] = W_ - ov                                               # korpuso išorė sienos pusėje
    g["xf"] = g["xb"] + S["leg_len"]                                # pado vidinis paviršius
    g["PROJ"] = g["xf"] + S["flange"][2]                            # siena nuo stiklo tolimo krašto
    g["L_h"] = g["xf"] - g["x0"]                                    # skersinis su koja
    g["L_v"] = g["FH"] - 2 * fa                                     # statmuo tarp skersinių
    g["TOT"] = D + 2 * S["face_thk"]
    # LED - Kaisen DUOLITE
    kj = json.load(open(os.path.join(HERE, "..", "assets", "kaisen_led.json"), encoding="utf-8"))
    du = kj["duolite"][S["led"]]
    boxes = sorted(int(b) for b in du["boxes"])
    hb = min(boxes, key=lambda b: abs(b - H_))
    tab = du["boxes"][str(hb)]
    deps = sorted(set(r[0] for r in tab))
    dep = max([d_ for d_ in deps if d_ <= D] or [deps[0]])
    cand = [r for r in tab if r[0] == dep]
    best = max([r for r in cand if r[3] >= 2000] or cand, key=lambda r: r[1])     # didžiausias žingsnis su >= 2000 lx
    p = S["led_pitch"] or best[1]
    span = g["FW"] - 2 * fa                                         # tarp statmenų (skersinio vidinis paviršius)
    n_row = math.ceil(span / p)
    rows_n = S["led_rows"] or (1 if H_ <= 600 else 2)               # Kaisen lentelė: ~26 vnt./m² -> 1 eilė iki ~600 aukščio
    g.update(du=du, led_name="DUOLITE " + S["led"], led_box=hb, led_dep=dep, led_lux=best[3], led_p=p,
             led_step=span / n_row, led_n_row=n_row, led_rows=rows_n, led_n=n_row * rows_n, led_span=span)
    g["led_W"] = g["led_n"] * du["W"]
    import led_km
    g["psu"] = led_km.psu_for(g["led_W"], 12)
    # kiekiai, svoris
    per_b = 2 * (g["BW"] + g["BH"])
    g["per_b"] = per_b
    g["pvc_len"] = 2 * (g["BW"] - 2 * tb + g["BH"] - 2 * tb)
    g["prof_len"] = 2 * g["L_h"] + 2 * g["L_v"]
    rho = json.load(open(os.path.join(HERE, "..", "assets", "svoris.json")))["density_kg_dm3"]
    tube_a = fa * fb - (fa - 2 * ft) * (fb - 2 * ft)
    FLw, FLh, FLt = S["flange"]
    g["kg"] = (2 * W_ * H_ * S["face_thk"] * rho["pmma"] + per_b * D * tb * rho["al"] + g["prof_len"] * tube_a * rho["al"]
               + 2 * FLw * FLh * FLt * rho["al"] + 2 * g["pvc_len"] * S["pvc_edge"][0] * S["pvc_edge"][1] * rho["pvc"]) / 1e6
    # D3.2 varžtų skylės korpuso juostoje: kiekvienoje kraštinėje 2 eilės (z = +-(D/2 - PVC/2), į PVC juostą) kas <= step
    # (v137: per juostos centrą skylių NĖRA - juosta virinama prie rėmo). Kraštinės: top, wall, bottom, front (išklotinės tvarka nuo viršutinio kairio kampo)
    pd_ = S["pvc_edge"][1]
    zs = D / 2 - pd_ / 2
    faces = [("top", g["BW"]), ("wall", g["BH"]), ("bottom", g["BW"]), ("front", g["BH"])]
    holes = []
    for fn, L in faces:
        n = math.ceil(L / S["screw_step"])
        for i in range(n):
            for z in (-zs, zs):
                holes.append((fn, L * (i + 0.5) / n, z, "pvc"))
    g["scr_holes"] = holes
    g["scr_n_face"] = math.ceil(g["BW"] / S["screw_step"])
    g["scr_wall"] = [(ov + u, z, k) for fn, u, z, k in holes if fn == "wall"]
    g["n_scr"] = len(holes)
    return g


def bom_rows(g):
    fa, fb, ft = g["frame"]
    FLw, FLh, FLt = g["flange"]
    pw, pd = g["pvc_edge"]
    return [[1, f"Frame + legs □{fa}x{fb}x{ft:g} (sheet 2)", "Alu EN AW-6060", g["frame_finish"],
             f"2 x {g['L_h']:g} + 2 x {g['L_v']:g} = {g['prof_len']:g} mm"],
            ["1A", f"Flange {FLw:g}x{FLh:g}x{FLt:g}, 4 x Ø{g['hole_d']:g}", "Alu, welded to leg", g["frame_finish"], "2 pcs."],
            [2, f"Body band {g['band_thk']:g} mm x {g['depth']:g}", "Alu, folded, welded to frame", g["body_finish"],
             f"{g['BW']:g} x {g['BH']:g}: {g['per_b']:g} mm"],
            [3, "Face A (glass)", g["face"], "-", f"{g['w']:g} x {g['h']:g} = {g['w'] * g['h'] / 1e6:.2f} m²"],
            [4, f"PVC edge {pw:g} x {pd:g} (face A)", "PVC, glued to face", "white", f"{g['pvc_len']:g} mm"],
            [5, "Face B (glass, mirror)", g["face"], "-", f"{g['w']:g} x {g['h']:g} = {g['w'] * g['h'] / 1e6:.2f} m²"],
            [6, f"PVC edge {pw:g} x {pd:g} (face B)", "PVC, glued to face", "white", f"{g['pvc_len']:g} mm"],
            [7, f"LED Kaisen {g['led_name']} + PSU", f"PSU {g['psu'][0].replace('-5Y', '')}", "6500 K",
             f"{g['led_n']} pcs. ({g['led_W']:.1f} W) + 1 PSU"],
            [8, "Tapping screw, D3.2 holes", "A2", "-", f"{g['n_scr']} pcs. (into PVC edge)"]]


def band(g, sheet, title_extra, md, bom, detail_fn):
    BY0 = K.BAND_Y; BH = K.IY1 - BY0
    W_P6, W_MD, W_TB = 214, 214, 272
    X_P6 = K.IX0; X_TB = K.IX1 - W_TB; X_MD = X_TB - W_MD; X_BOM = X_P6 + W_P6; W_BOM = X_MD - X_BOM
    detail_fn(X_P6, BY0, W_P6, BH)
    K.main_data(X_MD, BY0, W_MD, BH, md, lab_w=64)
    K.bom_table(X_BOM, BY0, W_BOM, BH, bom)
    spec = {"client": g["client"], "title": g["title"] + title_extra, "order_no": g["order_no"],
            "drawing_no": g["drawing_no"], "sheet": sheet, "rev": g["rev"], "date": g["date"]}
    K.title_block(X_TB, W_TB, spec, "1:5 / 1:2 / 1:1")


def flange_view(g, flx, fly, s2):
    fa, fb, ft = g["frame"]
    FLw, FLh, FLt = g["flange"]
    rx = lambda v: flx + (v + FLw / 2) * s2
    ry = lambda v: fly + (v + FLh / 2) * s2
    rr = g["flange_r"]
    pts = []
    for cx_, cy_, a0 in ((FLw / 2 - rr, -FLh / 2 + rr, -90), (FLw / 2 - rr, FLh / 2 - rr, 0),
                         (-FLw / 2 + rr, FLh / 2 - rr, 90), (-FLw / 2 + rr, -FLh / 2 + rr, 180)):
        for k_ in range(7):
            a = math.radians(a0 + 15 * k_)
            pts.append((rx(cx_ + rr * math.cos(a)), ry(cy_ + rr * math.sin(a))))
    poly(pts, fill=COL_FL, lw=0.1)
    hp = g["hole_pitch"] / 2
    for dz in (-hp, hp):
        for dy in (-hp, hp):
            circle(rx(dz), ry(dy), g["hole_d"] / 2 * s2, fill=white, lw=0.1)
    ci = fa - 2 * ft
    rect(rx(-ci / 2), ry(-ci / 2), ci * s2, ci * s2, fill=white, lw=0.1)
    rect(rx(-fa / 2), ry(-fa / 2), fa * s2, fa * s2, lw=0.1, dash=(2, 1.5))
    K.centerline(rx(-FLw / 2 - 8), ry(0), rx(FLw / 2 + 8), ry(0)); K.centerline(rx(0), ry(-FLh / 2 - 8), rx(0), ry(FLh / 2 + 8))
    hchain(ry(FLh / 2) + 16, [rx(-FLw / 2), rx(-hp), rx(hp), rx(FLw / 2)], [ry(FLh / 2)] + [ry(hp)] * 2 + [ry(FLh / 2)],
           [f"{FLw / 2 - hp:g}", f"{2 * hp:g}", f"{FLw / 2 - hp:g}"], size=K.F_DIM_FRAME)
    hdim(rx(-FLw / 2), rx(FLw / 2), ry(FLh / 2) + 32, f"{FLw:g}", e1=ry(FLh / 2), e2=ry(FLh / 2), size=K.F_DIM_FRAME)
    vchain(rx(FLw / 2) + 16, [ry(-FLh / 2), ry(-hp), ry(hp), ry(FLh / 2)], [rx(FLw / 2)] + [rx(hp)] * 2 + [rx(FLw / 2)],
           [f"{FLh / 2 - hp:g}", f"{2 * hp:g}", f"{FLh / 2 - hp:g}"], size=K.F_DIM_FRAME)
    vchain(rx(FLw / 2) + 34, [ry(-FLh / 2), ry(FLh / 2)], [rx(FLw / 2)] * 2, [f"{FLh:g}"], size=K.F_DIM_FRAME)
    K.tag(rx(hp) + 2, ry(-hp) - 2, rx(-FLw / 2) - 6, ry(-FLh / 2) - 14, f"4 x Ø{g['hole_d']:g}", align="r")
    K.tag(rx(0) + 3, ry(0) + 3, rx(-FLw / 2) - 6, ry(FLh / 2) + 10, f"□{ci:g} (tube inside)", align="r")
    T(flx + FLw * s2 / 2, ry(FLh / 2) + 50, f"t = {FLt:g}, R{rr:g}, welded to leg □{fa}x{fb}x{ft:g}", 8, align="c")


# ===================================================================== 1 LAPAS - GENERAL ASSEMBLY
def face_label(x, y, txt, size=10):
    T(x, y + size * 0.35, txt, size, font="FB", align="c", color=K.GREY)


def scene3d(g, yaw, box, title):
    """3D su SIDE A / SIDE B užrašu ant matomo stiklo"""
    import r3d
    Wd, Hd, D, tf, ov = g["w"], g["h"], g["depth"], g["face_thk"], g["face_over"]
    fa, fb, ft = g["frame"]; FLw, FLh, FLt = g["flange"]; ax = g["ax"]; LL = g["leg_len"]
    sc = r3d.Scene(yaw=yaw, pitch=18)
    sc.box((ov, ov, -D / 2), (g["BW"], 0, 0), (0, g["BH"], 0), (0, 0, D), COL_BODY, edge=EDGE)
    sc.box((0, 0, D / 2), (Wd, 0, 0), (0, Hd, 0), (0, 0, tf), COL_FACE, edge=EDGE)
    sc.box((0, 0, -D / 2 - tf), (Wd, 0, 0), (0, Hd, 0), (0, 0, tf), COL_FACE, edge=EDGE)
    for yc in (ax, Hd - ax):
        sc.box((g["xb"], yc - fa / 2, -fb / 2), (LL, 0, 0), (0, fa, 0), (0, 0, fb), COL_FRAME, edge=EDGE)
        sc.box((g["xf"], yc - FLh / 2, -FLw / 2), (FLt, 0, 0), (0, FLh, 0), (0, 0, FLw), COL_FL, edge=EDGE)
    sc.render(box)
    V = sc.V
    for zf, lab in ((D / 2 + tf, "SIDE A"), (-D / 2 - tf, "SIDE B")):
        n = (0, 0, 1 if zf > 0 else -1)
        if V.rot(*n)[2] > 0:
            px, py = V.S(Wd / 2, Hd / 2, zf)
            face_label(px, K.H - py, lab, 11)
    view_title(box[0] + box[2] / 2, box[1] + box[3] + 18, title, "ILLUSTRATIVE - NOT TO SCALE")


def sheet1(g, out):
    Wd, Hd, D, tf, tb, ov = g["w"], g["h"], g["depth"], g["face_thk"], g["band_thk"], g["face_over"]
    fa, fb, ft = g["frame"]
    LL = g["leg_len"]; FLw, FLh, FLt = g["flange"]; ax = g["ax"]; TOT = g["TOT"]
    pw, pd = g["pvc_edge"]
    K.set_band(9)
    K.init(out + ".tmp", "sheet1")
    K.frame(); K.set_view(True)
    s = MM / g["scale_ga"]
    sl = f"1:{g['scale_ga']}"
    top = K.IY0 + 112
    Yv = lambda y: top + y * s
    hp = g["hole_pitch"] / 2
    hy = [ax - hp, ax + hp, Hd - ax - hp, Hd - ax + hp]

    def front(fx, mirror, side):
        """priekio vaizdas; mirror - kojos į kairę (B pusė)"""
        X = (lambda x: fx + (g["PROJ"] - x) * s) if mirror else (lambda x: fx + x * s)
        xl, xr_ = (X(Wd), X(0)) if mirror else (X(0), X(Wd))
        rect(xl, Yv(0), Wd * s, Hd * s, fill=COL_FACE, lw=0.1)
        for yc in (ax, Hd - ax):
            a_, b_ = sorted((X(g["xb"]), X(g["xf"])))
            rect(a_, Yv(yc - fa / 2), LL * s, fa * s, fill=COL_FRAME, lw=0.1)
            a_, b_ = sorted((X(g["xf"]), X(g["PROJ"])))
            rect(a_, Yv(yc - FLh / 2), FLt * s, FLh * s, fill=COL_FL, lw=0.1)
            K.centerline(X(Wd - 20), Yv(yc), X(g["PROJ"] + 8), Yv(yc))
        hdim(xl, xr_, Yv(0) - 32, f"{Wd:g}", e1=Yv(0), e2=Yv(0), size=K.F_DIM_MAIN)
        xs_ = sorted([X(0), X(g["xb"]), X(g["xf"]), X(g["PROJ"])])
        labs = [f"{g['xb']:g}", f"{LL:g}", f"{FLt:g}"]
        hchain(Yv(Hd) + 32, xs_, [Yv(Hd)] * 4, labs[::-1] if mirror else labs, size=K.F_DIM_FRAME)
        hdim(xs_[0], xs_[-1], Yv(Hd) + 52, f"{g['PROJ']:g}", e1=Yv(Hd), e2=Yv(Hd), size=K.F_DIM_MAIN)
        xo = xl - 22 if not mirror else xr_ + 22
        vchain(xo, [Yv(0), Yv(Hd)], [xl if not mirror else xr_] * 2, [f"{Hd:g}"], size=K.F_DIM_MAIN)
        return X

    # ---------------------------------------------------------------- SIDE A | VIEW FROM WALL | SIDE B
    fxA = K.IX0 + 70
    XA = front(fxA, False, "SIDE A")
    K.balloon_column([(XA(Wd * 0.12), Yv(Hd * 0.15), 3)], XA(0) - 52)
    K.balloon_column([(XA(g["xb"] + LL * 0.5), Yv(ax), 1), (XA(g["xf"] + FLt / 2), Yv(Hd - ax + FLh / 2 - 6), "1A")],
                     XA(g["PROJ"]) + 56)
    vchain(XA(g["PROJ"]) + 16, [Yv(0), Yv(ax), Yv(Hd - ax), Yv(Hd)], [XA(Wd)] + [XA(g["PROJ"])] * 2 + [XA(Wd)],
           [f"{ax:g}", f"{Hd - 2 * ax:g}", f"{ax:g}"], size=K.F_DIM_FRAME)
    xcut = Wd * 0.3
    K.cut_plane(XA(xcut), Yv(0), Yv(Hd), "A", look="right")
    view_title(XA(g["PROJ"] / 2), top - 84, "FRONT VIEW - SIDE A", sl)
    # vaizdas iš sienos (gręžimo schema)
    sxc = XA(g["PROJ"]) + 128
    Xs = lambda z: sxc + z * s
    rect(Xs(-D / 2), Yv(ov), D * s, g["BH"] * s, fill=COL_BODY, lw=0.1)
    for zz in (-TOT / 2, TOT / 2 - tf):
        rect(Xs(zz), Yv(0), tf * s, Hd * s, fill=COL_FACE, lw=0.1)
    for (yy, zz, kind) in g["scr_wall"]:                          # D3.2 varžtų skylės korpuse (sienos pusė)
        circle(Xs(zz), Yv(yy), max(0.9, 1.6 * s), fill=white, lw=0.1)
    for yc in (ax, Hd - ax):
        rect(Xs(-FLw / 2), Yv(yc - FLh / 2), FLw * s, FLh * s, fill=COL_FL, lw=0.1)
        for dz in (-hp, hp):
            for dy in (-hp, hp):
                circle(Xs(dz), Yv(yc + dy), g["hole_d"] / 2 * s, fill=white, lw=0.1)
        ci = fa - 2 * ft
        rect(Xs(-ci / 2), Yv(yc - ci / 2), ci * s, ci * s, fill=white, lw=0.1)
    face_label(Xs(-TOT / 2) + 2, Yv(ax - FLh / 2) - 50, "A", 9); face_label(Xs(TOT / 2) - 2, Yv(ax - FLh / 2) - 50, "B", 9)
    K.centerline(Xs(0), Yv(-FLh / 2 + ax - 8), Xs(0), Yv(Hd - ax + FLh / 2 + 8))
    hchain(Yv(ax - FLh / 2) - 14, [Xs(-hp), Xs(hp)], [Yv(hy[0])] * 2, [f"{2 * hp:g}"], size=K.F_DIM_FRAME)
    hdim(Xs(-TOT / 2), Xs(TOT / 2), Yv(ax - FLh / 2) - 30, f"{TOT:g}", e1=Yv(0), e2=Yv(0), size=K.F_DIM_MAIN)
    hchain(Yv(Hd - ax + FLh / 2) + 14, [Xs(-TOT / 2), Xs(-hp), Xs(hp), Xs(TOT / 2)],
           [Yv(Hd)] + [Yv(hy[3])] * 2 + [Yv(Hd)], [f"{TOT / 2 - hp:g}", f"{2 * hp:g}", f"{TOT / 2 - hp:g}"], size=K.F_DIM_FRAME)
    vchain(Xs(FLw / 2) + 16, [Yv(hy[0]), Yv(hy[1]), Yv(hy[2]), Yv(hy[3])], [Xs(hp)] * 4,
           [f"{2 * hp:g}", f"{hy[2] - hy[1]:g}", f"{2 * hp:g}"], size=K.F_DIM_FRAME)
    vchain(Xs(FLw / 2) + 36, [Yv(hy[0]), Yv(hy[3])], [Xs(hp)] * 2, [f"{hy[3] - hy[0]:g}"], size=K.F_DIM_MAIN)
    vchain(Xs(-FLw / 2) - 24, [Yv(hy[0]), Yv(0), Yv(Hd), Yv(hy[3])], [Xs(-hp), Xs(-TOT / 2), Xs(-TOT / 2), Xs(-hp)],
           [f"{-hy[0]:g}", f"{Hd:g}", f"{hy[3] - Hd:g}"], size=K.F_DIM_FRAME)
    yw = g["scr_wall"][len(g["scr_wall"]) // 2]
    K.tag_column([(Xs(hp), Yv(hy[1]), f"8 x Ø{g['hole_d']:g}"), (Xs(0), Yv(Hd - ax), f"cable □{fa - 2 * ft:g}"),
                  (Xs(yw[1]), Yv(yw[0]), "D3.2 (sheet 2)")], Xs(FLw / 2) + 56, size=8)
    T(Xs(0), Yv(Hd) + 38, "= WALL DRILLING", 8, align="c", color=K.GREY)
    view_title(Xs(0), top - 84, "VIEW FROM WALL", sl)
    # SIDE B (veidrodinis - kojos kairėje)
    fxB = Xs(TOT / 2) + 128
    XB = front(fxB, True, "SIDE B")
    K.balloon_column([(XB(Wd * 0.12), Yv(Hd * 0.15), 5)], XB(0) + 52)
    view_title((XB(0) + XB(g["PROJ"])) / 2, top - 84, "FRONT VIEW - SIDE B", sl + "  (mirrored)")
    # ---------------------------------------------------------------- SECTION A-A 1:5
    s5 = MM / 5
    ya = lambda y: top + y * s5
    ax_ = XB(0) + 110
    Xa = lambda z: ax_ + (z + TOT / 2) * s5
    rect(Xa(-fb / 2), ya(ov + tb + fa), fb * s5, g["L_v"] * s5, fill=HexColor("#D6D6D6"), lw=0.1)
    for y0 in (ov, Hd - ov - tb):
        rect(Xa(-D / 2), ya(y0), D * s5, tb * s5, fill=COL_BODY, lw=0.1)
    for zz in (-TOT / 2, TOT / 2 - tf):
        rect(Xa(zz), ya(0), tf * s5, Hd * s5, fill=COL_FACE, lw=0.1)
    for y0 in (ov + tb, Hd - ov - tb - pw):
        rect(Xa(-D / 2), ya(y0), pd * s5, pw * s5, fill=COL_PVC, lw=0.1)
        rect(Xa(D / 2 - pd), ya(y0), pd * s5, pw * s5, fill=COL_PVC, lw=0.1)
    for y0 in (ov + tb, Hd - ov - tb - fa):
        rect(Xa(-fb / 2), ya(y0), fb * s5, fa * s5, fill=COL_FRAME, lw=0.1)
        rect(Xa(-fb / 2 + ft), ya(y0 + ft), (fb - 2 * ft) * s5, (fa - 2 * ft) * s5, fill=white, lw=0.1)
    yl = Hd - ov - tb - fa
    rect(Xa(-11), ya(yl - 8), 22 * s5, 8 * s5, fill=COL_LED, lw=0.1)
    if g["led_rows"] > 1:
        rect(Xa(-11), ya(ov + tb + fa), 22 * s5, 8 * s5, fill=COL_LED, lw=0.1)
    for dz in (-1, 1):
        line(Xa(0), ya(yl - 8), Xa(dz * D / 2), ya(yl - 8 - D / 2 / math.tan(math.radians(32.5))), 0.2,
             HexColor("#C9A000"), dash=(2, 1.5))
    face_label(Xa(-TOT / 2) + 2, ya(0) - 10, "A", 9); face_label(Xa(TOT / 2) - 2, ya(0) - 10, "B", 9)
    vchain(Xa(-TOT / 2) - 24, [ya(0), ya(Hd)], [Xa(-TOT / 2)] * 2, [f"{Hd:g}"], size=K.F_DIM_FRAME)
    hchain(ya(Hd) + 22, [Xa(-TOT / 2), Xa(-D / 2), Xa(-fb / 2), Xa(fb / 2), Xa(D / 2), Xa(TOT / 2)], [ya(Hd)] * 6,
           [f"{tf:g}", f"{(D - fb) / 2:g}", f"{fb:g}", f"{(D - fb) / 2:g}", f"{tf:g}"], size=K.F_DIM_FRAME)
    K.balloon_column([(Xa(fb / 2 - 4), ya(ov + tb + fa / 2), 1), (Xa(TOT / 2 - tf / 2), ya(Hd * 0.3), 5),
                      (Xa(4), ya(yl - 4), 7), (Xa(D / 2 - pd / 2), ya(Hd - ov - tb - pw / 2), 6)], Xa(TOT / 2) + 34)
    K.balloon_column([(Xa(-TOT / 2 + tf / 2), ya(Hd * 0.3), 3), (Xa(-D / 2 + pd / 2), ya(Hd - ov - tb - pw / 2), 4),
                      (Xa(-D / 2 + 20), ya(Hd - ov - tb / 2), 2)], Xa(-TOT / 2) - 52, ymax=ya(Hd) + 2)
    circle(Xa(TOT / 2 - 10), ya(Hd - 12), 16, lw=0.3, dash=(3, 1.5))
    T(Xa(TOT / 2) + 10, ya(Hd + 12) + 4, "B", 10, font="FB")
    view_title(Xa(0), top - 84, "SECTION A-A", "1:5")
    # ---------------------------------------------------------------- 3D: A ir B pusės
    y3 = Yv(Hd) + 80
    h3 = K.VIEW_BOT - y3 - 34
    w3 = 300
    scene3d(g, -35, (K.IX0 + 60, y3, w3, h3), "3D VIEW - SIDE A")
    scene3d(g, 145, (K.IX0 + 60 + w3 + 60, y3, w3, h3), "3D VIEW - SIDE B")
    K.set_view(False)

    def detail(X_P6, BY0, W_P6, BH):
        K.header(X_P6, BY0, W_P6, "DETAIL B - EDGE (AS P6 / 3 mm)  1:1")
        rect(X_P6, BY0 + 12, W_P6, BH - 12, lw=0.6)
        K.set_view(True)
        s3 = MM
        ox, oy = X_P6 + 46, BY0 + 34
        Zx = lambda z: ox + (TOT / 2 - z) * s3
        Yb = lambda y: oy + y * s3
        ymax = (BH - 34) / s3 - 6
        zend = fb / 2 - 2 * ft - 6
        wpx = lambda z0, z1: (z0 - z1) * s3
        rect(Zx(TOT / 2), Yb(0), tf * s3, ymax * s3, fill=COL_FACE, lw=0.1)
        rect(Zx(D / 2), Yb(ov), wpx(D / 2, zend), tb * s3, fill=COL_BODY, lw=0.1)
        rect(Zx(D / 2), Yb(ov + tb), pd * s3, pw * s3, fill=COL_PVC, lw=0.1)
        rect(Zx(fb / 2), Yb(ov + tb), wpx(fb / 2, zend), fa * s3, fill=COL_FRAME, lw=0.1)
        rect(Zx(fb / 2 - ft), Yb(ov + tb + ft), wpx(fb / 2 - ft, zend), (fa - 2 * ft) * s3, fill=white, lw=0.1)
        line(Zx(zend), Yb(ov - 3), Zx(zend), Yb(ov + tb + fa + 3), 0.1, dash=([4, 1, 1, 1], 0))
        zs = D / 2 - pd / 2
        rect(Zx(zs) - 2.4 * s3, Yb(ov - 1.6), 4.8 * s3, 1.6 * s3, fill=HexColor("#3A3A3A"), lw=0.1)
        rect(Zx(zs) - 1.1 * s3, Yb(ov), 2.2 * s3, (tb + pw + 4) * s3, fill=HexColor("#3A3A3A"), lw=0.1)
        K.centerline(Zx(zs), Yb(ov - 5), Zx(zs), Yb(ov + tb + pw + 7))
        K.set_view(False)
        hchain(Yb(ymax) + 4, [Zx(TOT / 2), Zx(D / 2), Zx(zs), Zx(D / 2 - pd)], [Yb(ymax)] * 4,
               [f"{tf:g}", f"{pd / 2:g}", f"{pd / 2:g}"], size=K.F_DIM_FRAME)
        vchain(Zx(TOT / 2) - 10, [Yb(0), Yb(ov), Yb(ov + tb), Yb(ov + tb + pw)], [Zx(TOT / 2)] + [Zx(D / 2)] * 3,
               [f"{ov:g}", f"{tb:g}", f"{pw:g}"], size=K.F_DIM_FRAME)
        K.balloon_column([(Zx(zs) + 2.4 * s3, Yb(ov - 0.8), 8), (Zx(D / 2 - pd - 4), Yb(ov + tb / 2), 2),
                          (Zx(D / 2 - pd + 3), Yb(ov + tb + pw / 2), 4), (Zx(fb / 2 - ft - 2), Yb(ov + tb + fa * 0.5), 1),
                          (Zx(TOT / 2 - tf / 2), Yb(ymax * 0.75), 3)], X_P6 + W_P6 - 12, ymin=BY0 + 22, ymax=BY0 + BH - 22)
        K.tag(Zx(zs) + 1.1 * s3, Yb(ov + tb + pw + 3), Zx(zs) + 16, Yb(ov + tb + pw + 14), "D3.2", size=7, align="l")
        T(X_P6 + W_P6 - 4, BY0 + BH - 6, "side A shown; side B mirror (5 / 6)", 7, align="r", color=K.GREY)

    md = [["Product", "double-sided lightbox, projecting"],
          ["Size (glass)", f"{Wd:g} x {Hd:g} x {TOT:g} mm"],
          ["Sides", "A + B (graphics per side)"],
          ["From wall", f"{g['PROJ']:g} mm (body {LL + FLt:g})"],
          ["Fixing", f"2 flanges, 8 x Ø{g['hole_d']:g}, {g['hole_pitch']:g} x {g['hole_pitch']:g} {g['anchors']}".strip()],
          ["LED / PSU", f"{g['led_n']} x {g['led_name']}, {g['psu'][0].replace('-5Y', '')}"],
          ["Cable", g["cable"] or "through bottom leg + flange:"],
          ["Qty", f"{g['qty']} pcs."],
          ["Weight (calc.)", f"≈ {g['kg']:.1f} kg / pcs, excl. PSU"]]
    band(g, "1 / 2", " - GA", md, bom_rows(g), detail)
    K.save(out)


# ===================================================================== 2 LAPAS - FRAME + LED
def sheet2(g, out):
    D, tb, ov, tf = g["depth"], g["band_thk"], g["face_over"], g["face_thk"]
    fa, fb, ft = g["frame"]
    LL = g["leg_len"]; FLw, FLh, FLt = g["flange"]
    K.set_band(9)
    K.init(out + ".tmp", "sheet2")
    K.frame(); K.set_view(True)
    s = MM / 5
    top = K.IY0 + 112
    fx = K.IX0 + 100
    x0 = g["x0"]
    X = lambda x: fx + (x - x0) * s
    Yv = lambda y: top + (y - x0) * s
    FW, FH = g["FW"], g["FH"]
    xr = x0 + FW
    rect(X(ov), Yv(ov), g["BW"] * s, g["BH"] * s, stroke=HexColor("#9A9A9A"), lw=0.1, dash=(3, 2))   # korpusas (orientacijai)
    for y0 in (x0, x0 + FH - fa):
        rect(X(x0), Yv(y0), g["L_h"] * s, fa * s, fill=COL_FRAME, lw=0.1)
        rect(X(g["xf"]), Yv(y0 + fa / 2 - FLh / 2), FLt * s, FLh * s, fill=COL_FL, lw=0.1)
    for xx in (x0, xr - fa):
        rect(X(xx), Yv(x0 + fa), fa * s, g["L_v"] * s, fill=COL_FRAME, lw=0.1)
    yrow = [x0 + FH - fa] + ([x0 + fa] if g["led_rows"] > 1 else [])
    led_x = [x0 + fa + g["led_step"] * (i + 0.5) for i in range(g["led_n_row"])]
    for yr in yrow:
        up = yr > x0 + FH / 2
        for lx in led_x:
            rect(X(lx - 11), Yv(yr - 8 if up else yr), 22 * s, 8 * s, fill=COL_LED, lw=0.1)
        yw = yr - 4 if up else yr + 4
        line(X(led_x[0]), Yv(yw), X(led_x[-1]), Yv(yw), 0.2, HexColor("#C00000"))
        line(X(led_x[-1]), Yv(yw), X(g["xb"] + 30), Yv(yw), 0.2, HexColor("#C00000"))
    # matmenys
    hdim(X(x0), X(xr), Yv(x0) - 26, f"{FW:g}", e1=Yv(x0), e2=Yv(x0), size=K.F_DIM_MAIN)
    hchain(Yv(x0) - 46, [X(x0), X(g["xb"]), X(g["xf"]), X(g["xf"] + FLt)], [Yv(x0)] * 2 + [Yv(x0 + fa / 2 - FLh / 2)] * 2,
           [f"{g['xb'] - x0:g}", f"{LL:g}", f"{FLt:g}"], size=K.F_DIM_FRAME)
    hdim(X(x0), X(g["xf"]), Yv(x0) - 66, f"{g['L_h']:g}  (□{fa}x{fb}x{ft:g}, 2 pcs.)", e1=Yv(x0), e2=Yv(x0),
         size=K.F_DIM_FRAME)
    ylb = x0 + FH
    hchain(Yv(ylb) + 34, [X(x0), X(x0 + fa)] + [X(v) for v in led_x] + [X(xr - fa), X(xr)], [Yv(ylb)] * (len(led_x) + 4),
           [f"{fa:g}", f"{led_x[0] - x0 - fa:.1f}"] + [f"{g['led_step']:.1f}"] * (len(led_x) - 1) +
           [f"{xr - fa - led_x[-1]:.1f}", f"{fa:g}"], size=K.F_DIM_FRAME)
    hdim(X(x0 + fa), X(xr - fa), Yv(ylb) + 54, f"{g['led_span']:g}  ({g['led_n_row']} x {g['led_step']:.1f})",
         e1=Yv(ylb), e2=Yv(ylb), size=K.F_DIM_FRAME)
    vchain(X(x0) - 26, [Yv(x0), Yv(x0 + fa), Yv(x0 + FH - fa), Yv(x0 + FH)], [X(x0)] * 4,
           [f"{fa:g}", f"{g['L_v']:g}", f"{fa:g}"], size=K.F_DIM_FRAME)
    vchain(X(x0) - 48, [Yv(x0), Yv(x0 + FH)], [X(x0)] * 2, [f"{FH:g}"], size=K.F_DIM_MAIN)
    vchain(X(g["xf"] + FLt) + 24, [Yv(x0 + fa / 2), Yv(x0 + FH - fa / 2)], [X(g["xf"])] * 2, [f"{FH - fa:g}"],
           size=K.F_DIM_FRAME)
    K.balloon_column([(X(xr - 60), Yv(x0 + fa / 2), "1.1"), (X(g["xf"] + FLt / 2), Yv(x0 + fa / 2 + FLh / 2 - 6), "1A"),
                      (X(xr - fa / 2), Yv(x0 + FH * 0.45), "1.3"), (X(led_x[-1]) + 3 * s, Yv(yrow[0] - 4), 7),
                      (X(xr - 60), Yv(x0 + FH - fa / 2), "1.2")], X(g["xf"] + FLt) + 58, r=7)

    xc_ = led_x[len(led_x) // 2]
    K.cut_plane(X(xc_), Yv(x0 + FH - fa) - 10, Yv(x0 + FH), "C", look="right")
    view_title(X(x0 + g["L_h"] / 2), top - 96, "FRAME (1) + LED (7)", "1:5  (from side A, welded)")
    # ---------------------------------------------------------------- SECTION C-C 1:2
    s2 = MM / 2
    cx0, cy0 = X(g["xf"] + FLt) + 170, top + 40
    Zc = lambda z: cx0 + (z + D / 2) * s2
    Yc = lambda y: cy0 + y * s2
    up_ = 70
    rect(Zc(-D / 2 - tf), Yc(-up_), tf * s2, (up_ + fa + tb + ov) * s2, fill=COL_FACE, lw=0.1)
    rect(Zc(D / 2), Yc(-up_), tf * s2, (up_ + fa + tb + ov) * s2, fill=COL_FACE, lw=0.1)
    rect(Zc(-D / 2), Yc(fa), D * s2, tb * s2, fill=COL_BODY, lw=0.1)
    rect(Zc(-fb / 2), Yc(0), fb * s2, fa * s2, fill=COL_FRAME, lw=0.1)
    rect(Zc(-fb / 2 + ft), Yc(ft), (fb - 2 * ft) * s2, (fa - 2 * ft) * s2, fill=white, lw=0.1)
    rect(Zc(-11), Yc(-8), 22 * s2, 8 * s2, fill=COL_LED, lw=0.1)
    for dz in (-1, 1):
        line(Zc(0), Yc(-8), Zc(dz * D / 2), Yc(-8 - D / 2 / math.tan(math.radians(32.5))), 0.25, HexColor("#C9A000"), dash=(2, 1.5))
    T(Zc(0), Yc(-up_) + 10, "65°", 8, align="c", color=HexColor("#8A6D00"))
    hchain(Yc(fa + tb + ov) + 22, [Zc(-D / 2 - tf), Zc(-D / 2), Zc(-fb / 2), Zc(fb / 2), Zc(D / 2), Zc(D / 2 + tf)],
           [Yc(fa + tb)] * 6, [f"{tf:g}", f"{(D - fb) / 2:g}", f"{fb:g}", f"{(D - fb) / 2:g}", f"{tf:g}"], size=K.F_DIM_FRAME)
    K.balloon_column([(Zc(D / 2 + tf / 2), Yc(-up_ * 0.75), 5), (Zc(8), Yc(-4), 7), (Zc(D / 2 - 10), Yc(fa + tb / 2), 2)],
                     Zc(D / 2 + tf) + 32)
    K.balloon_column([(Zc(-D / 2 - tf / 2), Yc(-up_ * 0.6), 3), (Zc(-fb / 2 + 3), Yc(fa / 2), 1)], Zc(-D / 2 - tf) - 32)
    T(Zc(0), Yc(fa + tb) + 52, "LED on member centre - light to both faces", 8, align="c", color=K.GREY)
    view_title(Zc(0), top - 96, "SECTION C-C (LED)", "1:2")
    # ---------------------------------------------------------------- FLANGE 1:2
    flx = Zc(D / 2 + tf) + 110
    flange_view(g, flx, top + 20, s2)
    view_title(flx + FLw * s2 / 2, top - 96, "FLANGE 1A (2 pcs.)", "1:2")
    # ---------------------------------------------------------------- BODY BAND (2) - išklotinė 1:10 su D3.2 skylėmis
    s10 = MM / 10
    faces = [("top", g["BW"]), ("wall", g["BH"]), ("bottom", g["BW"]), ("front", g["BH"])]
    Ltot = sum(L for _, L in faces)
    bx0 = K.IX1 - Ltot * s10 - 70
    by0 = K.VIEW_BOT - 96
    BX = lambda u: bx0 + u * s10
    BY = lambda v: by0 + v * s10                                  # v - nuo A pusės krašto (0) iki B (D)
    rect(BX(0), BY(0), Ltot * s10, D * s10, fill=COL_BODY, lw=0.1)
    starts, u0 = {}, 0.0
    for fn, L in faces:
        starts[fn] = u0
        if u0 > 0:
            line(BX(u0), BY(-3), BX(u0), BY(D + 3), 0.2, dash=(3, 1.5))
        T(BX(u0 + L / 2), BY(D / 2) + 3, fn.upper() + (" (legs)" if fn == "wall" else ""), 7, align="c", color=white)
        u0 += L
    for fn, u, z, k in g["scr_holes"]:
        circle(BX(starts[fn] + u), BY(D / 2 + z), 1.0, fill=white, lw=0.1)
    cl = fa + 2                                                   # kojos anga (vamzdis + 1 mm / pusė)
    for uu in (g["ax"] - ov, g["BH"] - (g["ax"] - ov)):
        rect(BX(starts["wall"] + uu - cl / 2), BY(D / 2 - cl / 2), cl * s10, cl * s10, fill=white, lw=0.1)
    # matmenys: lenkimai, skylių eilės, vienos kraštinės skylių žingsnis
    hchain(BY(0) - 14, [BX(starts[fn]) for fn, _ in faces] + [BX(Ltot)], [BY(0)] * 5, [f"{L:g}" for _, L in faces],
           size=K.F_DIM_FRAME)
    hdim(BX(0), BX(Ltot), BY(0) - 30, f"{Ltot:g}  (band {tb:g} mm, 3 x 90° fold + seam)", e1=BY(0), e2=BY(0), size=K.F_DIM_FRAME)
    zs = D / 2 - g["pvc_edge"][1] / 2
    vchain(BX(Ltot) + 16, [BY(0), BY(D / 2 - zs), BY(D / 2), BY(D / 2 + zs), BY(D)], [BX(Ltot)] * 5,
           [f"{D / 2 - zs:g}", f"{zs:g}", f"{zs:g}", f"{D / 2 - zs:g}"], size=K.F_DIM_FRAME)
    n_ = g["scr_n_face"]; st_ = g["BW"] / n_
    hu = [st_ * (i + 0.5) for i in range(n_)]
    hchain(BY(D) + 14, [BX(0)] + [BX(u) for u in hu] + [BX(g["BW"])], [BY(D / 2 + zs)] * (n_ + 2),
           [f"{hu[0]:.1f}"] + [f"{st_:.1f}"] * (n_ - 1) + [f"{g['BW'] - hu[-1]:.1f}"], size=K.F_DIM_FRAME)
    T(BX(0), BY(D) + 62, f"holes: same on each side ({n_} + {n_} per side, rows {D / 2 - zs:g} from edges) ; band welded to frame (no holes on centre line)", 7, color=K.GREY)
    uu = g["ax"] - ov
    hchain(BY(D) + 32, [BX(starts["wall"]), BX(starts["wall"] + uu), BX(starts["wall"] + g["BH"] - uu), BX(starts["wall"] + g["BH"])],
           [BY(D / 2)] * 4, [f"{uu:g}", f"{g['BH'] - 2 * uu:g}", f"{uu:g}"], size=K.F_DIM_FRAME)
    K.tag(BX(starts["wall"] + uu), BY(D / 2 + cl / 2), BX(starts["wall"] + uu) + 30, BY(D) + 48, f"□{cl:g} leg hole (2)", size=7)
    K.tag(BX(starts["top"] + hu[0]), BY(D / 2 - zs), BX(starts["top"] + hu[0]) + 10, BY(0) - 44,
          f"D3.2 - {g['n_scr']} holes (screws 8, into PVC 4 / 6)", size=7)
    T(BX(0) - 4, BY(0) + 6, "A", 8, font="FB", align="r", color=K.GREY)
    T(BX(0) - 4, BY(D) + 2, "B", 8, font="FB", align="r", color=K.GREY)
    view_title(BX(Ltot / 2), by0 - 66, "BODY BAND (2) - FLAT PATTERN", "1:10")
    K.set_view(False)

    def detail(X_P6, BY0, W_P6, BH):
        K.main_data(X_P6, BY0, W_P6, BH, [
            ["Module", f"Kaisen {g['led_name']}"],
            ["Power / flux", f"{g['du']['W']:g} W, {g['du']['lm']:g} lm, 12 V (assumed)"],
            ["Beam", "10° x 65° (for double-sided boxes)"],
            ["Mounting", "frame member centre, 1 row" if g["led_rows"] == 1 else "top + bottom members"],
            ["Qty / pitch", f"{g['led_n']} pcs., {g['led_step']:.1f} mm (table {g['led_p']:g})"],
            ["Kaisen table", f"box 1000x{g['led_box']}, depth {g['led_dep']}: {g['led_lux']} lx"],
            ["Power total", f"{g['led_W']:.1f} W"],
            ["PSU", f"{g['psu'][0]} ({g['psu'][1]} W, IP67), place:"],
            ["Supply", "not in Alt Reklama price list - check:"]], title="LED (7)", lab_w=64)

    ci = fa - 2 * ft
    frame_cut = [["1.1", f"Top member + leg □{fa}x{fb}x{ft:g}", "Alu EN AW-6060", g["frame_finish"], f"1 x {g['L_h']:g} mm"],
                 ["1.2", f"Bottom member + leg □{fa}x{fb}x{ft:g}", "Alu EN AW-6060", g["frame_finish"], f"1 x {g['L_h']:g} mm (cable)"],
                 ["1.3", f"Vertical □{fa}x{fb}x{ft:g}", "Alu EN AW-6060", g["frame_finish"], f"2 x {g['L_v']:g} mm"],
                 ["1A", f"Flange {FLw:g}x{FLh:g}x{FLt:g} R{g['flange_r']:g}", "Alu", g["frame_finish"],
                  f"2 pcs., 4 x Ø{g['hole_d']:g} + □{ci:g}"],
                 ["", "Frame profile total", "", "", f"{g['prof_len']:g} mm (+ cut allowance)"],
                 [7, f"LED Kaisen {g['led_name']}", f"{g['du']['W']:g} W, 12 V", "6500 K", f"{g['led_n']} pcs."],
                 ["7A", "PSU", g["psu"][0], "IP67", "1 pc."],
                 ["7B", "Cable 2 x 0.75 (LED -> PSU)", "", "", "length:"],
                 ["", "", "", "", ""]]
    md = [["Frame outer", f"{FW:g} x {FH:g} mm"],
          ["Profile", f"□{fa}x{fb}x{ft:g} Alu, centre of depth"],
          ["Legs", f"top + bottom members, +{g['xf'] - g['xb']:g} out of body"],
          ["Leg axes", f"{FH - fa:g} mm (from glass edge {g['ax']:g})"],
          ["Joints", "welded (TIG), ground"],
          ["Body", f"band {g['BW']:g} x {g['BH']:g}, welded to frame"],
          ["Cable", "bottom leg tube -> flange □ hole"],
          ["Finish", g["frame_finish"]],
          ["Qty", f"{g['qty']} set"]]
    band(g, "2 / 2", " - FRAME + LED", md, frame_cut, detail)
    K.save(out)


def main(spec_path, out):
    S = dict(DEF); S.update(json.load(open(spec_path, encoding="utf-8")))
    g = geom(S)
    p1, p2 = out + ".1.pdf", out + ".2.pdf"
    sheet1(g, p1)
    sheet2(g, p2)
    import pymupdf as fitz
    d = fitz.open()
    for p in (p1, p2):
        d.insert_pdf(fitz.open(p))
    d.save(out, garbage=3, deflate=True); d.close()
    K.pdf_fix_fonts(out)
    for p in (p1, p2, p1 + ".tmp", p2 + ".tmp"):
        os.path.exists(p) and os.remove(p)
    print("OK", out, f"svoris {g['kg']:.2f} kg, rėmas {g['FW']:g}x{g['FH']:g}, LED {g['led_n']} x {g['led_name']} "
          f"({g['led_W']:.1f} W, {g['psu'][0]}), netelpa: {K.OVERFLOW}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
