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
       "cable": "", "anchors": ""}
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
    g["n_scr"] = 2 * math.ceil(per_b / S["screw_step"]) + 8
    return g


def bom_rows(g):
    fa, fb, ft = g["frame"]
    FLw, FLh, FLt = g["flange"]
    pw, pd = g["pvc_edge"]
    return [[1, f"Frame + legs □{fa}x{fb}x{ft:g} (sheet 2)", "Alu EN AW-6060", g["frame_finish"],
             f"2 x {g['L_h']:g} + 2 x {g['L_v']:g} = {g['prof_len']:g} mm"],
            ["1A", f"Flange {FLw:g}x{FLh:g}x{FLt:g}, 4 x Ø{g['hole_d']:g}", "Alu, welded to leg", g["frame_finish"], "2 pcs."],
            [2, f"Body band {g['band_thk']:g} mm x {g['depth']:g}", "Alu sheet, folded", g["body_finish"],
             f"{g['BW']:g} x {g['BH']:g}: {g['per_b']:g} mm, 2 leg holes"],
            [3, "Face A (glass)", g["face"], "-", f"{g['w']:g} x {g['h']:g} = {g['w'] * g['h'] / 1e6:.2f} m²"],
            [4, f"PVC edge {pw:g} x {pd:g} (face A)", "PVC, glued to face", "white", f"{g['pvc_len']:g} mm"],
            [5, "Face B (glass, mirror)", g["face"], "-", f"{g['w']:g} x {g['h']:g} = {g['w'] * g['h'] / 1e6:.2f} m²"],
            [6, f"PVC edge {pw:g} x {pd:g} (face B)", "PVC, glued to face", "white", f"{g['pvc_len']:g} mm"],
            [7, f"LED Kaisen {g['led_name']} + PSU", f"PSU {g['psu'][0].replace('-5Y', '')}", "6500 K",
             f"{g['led_n']} pcs. ({g['led_W']:.1f} W) + 1 PSU"],
            [8, "Tapping screw (band -> PVC / frame)", "A2", "-", f"≈ {g['n_scr']} pcs. (step ≤ {g['screw_step']})"]]


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
def sheet1(g, out):
    Wd, Hd, D, tf, tb, ov = g["w"], g["h"], g["depth"], g["face_thk"], g["band_thk"], g["face_over"]
    fa, fb, ft = g["frame"]
    LL = g["leg_len"]; FLw, FLh, FLt = g["flange"]; ax = g["ax"]; TOT = g["TOT"]
    pw, pd = g["pvc_edge"]
    K.set_band(9)
    K.init(out + ".tmp", "sheet1")
    K.frame(); K.set_view(True)
    s = MM / 5
    top = K.IY0 + 112
    # ---------------------------------------------------------------- FRONT VIEW
    fx = K.IX0 + 78
    X = lambda x: fx + x * s
    Yv = lambda y: top + y * s
    rect(X(0), Yv(0), Wd * s, Hd * s, fill=COL_FACE, lw=0.1)
    rect(X(ov), Yv(ov), g["BW"] * s, g["BH"] * s, stroke=HexColor("#7A7A7A"), lw=0.1, dash=(2, 1.5))   # korpusas po stiklu
    for yc in (ax, Hd - ax):
        rect(X(g["xb"]), Yv(yc - fa / 2), LL * s, fa * s, fill=COL_FRAME, lw=0.1)
        rect(X(g["xf"]), Yv(yc - FLh / 2), FLt * s, FLh * s, fill=COL_FL, lw=0.1)
        K.centerline(X(Wd - 20), Yv(yc), X(g["PROJ"] + 12), Yv(yc))
    hdim(X(0), X(Wd), Yv(0) - 30, f"{Wd:g}", e1=Yv(0), e2=Yv(0), size=K.F_DIM_MAIN)
    hchain(Yv(Hd) + 26, [X(0), X(g["xb"]), X(g["xf"]), X(g["PROJ"])], [Yv(Hd)] * 2 + [Yv(Hd - ax + FLh / 2)] * 2,
           [f"{g['xb']:g}", f"{LL:g}", f"{FLt:g}"], size=K.F_DIM_FRAME)
    hdim(X(0), X(g["PROJ"]), Yv(Hd) + 46, f"{g['PROJ']:g}", e1=Yv(Hd), e2=Yv(Hd - ax + FLh / 2), size=K.F_DIM_MAIN)
    vchain(X(0) - 26, [Yv(0), Yv(Hd)], [X(0), X(0)], [f"{Hd:g}"], size=K.F_DIM_MAIN)
    vchain(X(g["PROJ"]) + 22, [Yv(0), Yv(ax), Yv(Hd - ax), Yv(Hd)], [X(Wd)] + [X(g["PROJ"])] * 2 + [X(Wd)],
           [f"{ax:g}", f"{Hd - 2 * ax:g}", f"{ax:g}"], size=K.F_DIM_FRAME)
    leader(X(Wd * 0.3), Yv(Hd * 0.35), X(Wd * 0.3) - 40, Yv(Hd * 0.35) - 40, 3)
    leader(X(g["xb"] + LL * 0.5), Yv(ax), X(g["xb"] + LL * 0.5) + 6, Yv(ax) - 34, 1)
    leader(X(g["xf"] + FLt / 2), Yv(Hd - ax + FLh / 2 - 8), X(g["PROJ"]) + 50, Yv(Hd - ax) + 40, "1A")
    leader(X(ov), Yv(Hd * 0.62), X(0) + 34, Yv(Hd * 0.62) + 30, 2)
    T(X(Wd / 2), Yv(Hd / 2) + 4, "SIDE A", 10, align="c", color=K.GREY)
    K.tag(X(ov) + 1, Yv(Hd * 0.85), X(Wd * 0.18), Yv(Hd * 0.93), f"body {g['BW']:g} x {g['BH']:g} (glass -{ov:g} / side)", size=7)
    line(X(Wd / 2), Yv(-12), X(Wd / 2), Yv(Hd + 12), 0.4)
    T(X(Wd / 2) + 3, Yv(-12) - 2, "A", 11, font="FB")
    T(X(Wd / 2) + 3, Yv(Hd + 12) + 10, "A", 11, font="FB")
    view_title(X(g["PROJ"] / 2), top - 96, "FRONT VIEW (SIDE A)", "1:5  (side B - mirrored)")
    # ---------------------------------------------------------------- SIDE VIEW iš sienos = gręžimo schema
    sx = X(g["PROJ"]) + 150
    Xs = lambda z: sx + (z + TOT / 2) * s
    rect(Xs(-D / 2), Yv(ov), D * s, g["BH"] * s, fill=COL_BODY, lw=0.1)
    for zz in (-TOT / 2, TOT / 2 - tf):
        rect(Xs(zz), Yv(0), tf * s, Hd * s, fill=COL_FACE, lw=0.1)
    hp = g["hole_pitch"] / 2
    hy = [ax - hp, ax + hp, Hd - ax - hp, Hd - ax + hp]
    for yc in (ax, Hd - ax):
        rect(Xs(-FLw / 2), Yv(yc - FLh / 2), FLw * s, FLh * s, fill=COL_FL, lw=0.1)
        for dz in (-hp, hp):
            for dy in (-hp, hp):
                circle(Xs(dz), Yv(yc + dy), g["hole_d"] / 2 * s, fill=white, lw=0.1)
        ci = fa - 2 * ft
        rect(Xs(-ci / 2), Yv(yc - ci / 2), ci * s, ci * s, fill=white, lw=0.1)
    K.centerline(Xs(0), Yv(-FLh / 2 + ax - 10), Xs(0), Yv(Hd - ax + FLh / 2 + 10))
    hchain(Yv(ax - FLh / 2) - 18, [Xs(-hp), Xs(hp)], [Yv(hy[0])] * 2, [f"{2 * hp:g}"], size=K.F_DIM_FRAME)
    hdim(Xs(-TOT / 2), Xs(TOT / 2), Yv(ax - FLh / 2) - 36, f"{TOT:g}", e1=Yv(0), e2=Yv(0), size=K.F_DIM_MAIN)
    hchain(Yv(Hd - ax + FLh / 2) + 18, [Xs(-TOT / 2), Xs(-hp), Xs(hp), Xs(TOT / 2)],
           [Yv(Hd)] + [Yv(hy[3])] * 2 + [Yv(Hd)], [f"{TOT / 2 - hp:g}", f"{2 * hp:g}", f"{TOT / 2 - hp:g}"], size=K.F_DIM_FRAME)
    vchain(Xs(FLw / 2) + 20, [Yv(hy[0]), Yv(hy[1]), Yv(hy[2]), Yv(hy[3])], [Xs(hp)] * 4,
           [f"{2 * hp:g}", f"{hy[2] - hy[1]:g}", f"{2 * hp:g}"], size=K.F_DIM_FRAME)
    vchain(Xs(FLw / 2) + 42, [Yv(hy[0]), Yv(hy[3])], [Xs(hp)] * 2, [f"{hy[3] - hy[0]:g}"], size=K.F_DIM_MAIN)
    vchain(Xs(-FLw / 2) - 20, [Yv(hy[0]), Yv(0), Yv(Hd), Yv(hy[3])], [Xs(-hp), Xs(-TOT / 2), Xs(-TOT / 2), Xs(-hp)],
           [f"{-hy[0]:g}", f"{Hd:g}", f"{hy[3] - Hd:g}"], size=K.F_DIM_FRAME)
    K.tag(Xs(hp) + 2, Yv(hy[1]) + 2, Xs(FLw / 2) + 8, Yv(ax + 40), f"8 x Ø{g['hole_d']:g}", size=8)
    K.tag(Xs(0) + 2, Yv(Hd - ax) + 2, Xs(FLw / 2) + 8, Yv(Hd - ax - 34), f"cable □{fa - 2 * ft:g}", size=8)
    leader(Xs(0), Yv(Hd * 0.55), Xs(-TOT / 2) - 44, Yv(Hd * 0.62), 2)
    T(Xs(0), Yv(Hd) + 46, "= WALL DRILLING (view from wall)", 8, align="c", color=K.GREY)
    view_title(Xs(0), top - 96, "SIDE VIEW (FROM WALL)", "1:5")
    # ---------------------------------------------------------------- SECTION A-A
    ax_ = Xs(TOT / 2) + 150
    Xa = lambda z: ax_ + (z + TOT / 2) * s
    rect(Xa(-fb / 2), Yv(ov + tb + fa), fb * s, g["L_v"] * s, fill=HexColor("#D6D6D6"), lw=0.1)     # statmuo už pjūvio
    for y0 in (ov, Hd - ov - tb):
        rect(Xa(-D / 2), Yv(y0), D * s, tb * s, fill=COL_BODY, lw=0.1)
    for zz in (-TOT / 2, TOT / 2 - tf):
        rect(Xa(zz), Yv(0), tf * s, Hd * s, fill=COL_FACE, lw=0.1)
    for y0 in (ov + tb, Hd - ov - tb - pw):
        rect(Xa(-D / 2), Yv(y0), pd * s, pw * s, fill=COL_PVC, lw=0.1)
        rect(Xa(D / 2 - pd), Yv(y0), pd * s, pw * s, fill=COL_PVC, lw=0.1)
    for y0 in (ov + tb, Hd - ov - tb - fa):
        rect(Xa(-fb / 2), Yv(y0), fb * s, fa * s, fill=COL_FRAME, lw=0.1)
        rect(Xa(-fb / 2 + ft), Yv(y0 + ft), (fb - 2 * ft) * s, (fa - 2 * ft) * s, fill=white, lw=0.1)
    yl = Hd - ov - tb - fa                                         # LED ant apatinio skersinio (šviečia aukštyn)
    rect(Xa(-11), Yv(yl - 8), 22 * s, 8 * s, fill=COL_LED, lw=0.1)
    if g["led_rows"] > 1:
        rect(Xa(-11), Yv(ov + tb + fa), 22 * s, 8 * s, fill=COL_LED, lw=0.1)
    for dz in (-1, 1):                                             # spindulys 10°x65° - į abu veidus
        line(Xa(0), Yv(yl - 8), Xa(dz * D / 2), Yv(yl - 8 - D / 2 / math.tan(math.radians(32.5))), 0.2,
             HexColor("#C9A000"), dash=(2, 1.5))
    vchain(Xa(-TOT / 2) - 22, [Yv(0), Yv(Hd)], [Xa(-TOT / 2)] * 2, [f"{Hd:g}"], size=K.F_DIM_FRAME)
    hchain(Yv(Hd) + 26, [Xa(-TOT / 2), Xa(-D / 2), Xa(-fb / 2), Xa(fb / 2), Xa(D / 2), Xa(TOT / 2)], [Yv(Hd)] * 6,
           [f"{tf:g}", f"{(D - fb) / 2:g}", f"{fb:g}", f"{(D - fb) / 2:g}", f"{tf:g}"], size=K.F_DIM_FRAME)
    leader(Xa(0), Yv(ov + tb + fa / 2), Xa(TOT / 2) + 34, Yv(30), 1)
    leader(Xa(6), Yv(yl - 4), Xa(TOT / 2) + 34, Yv(Hd - 80), 7)
    leader(Xa(D / 2 - pd / 2), Yv(Hd - ov - tb - pw / 2), Xa(TOT / 2) + 34, Yv(Hd - 40), 6)
    leader(Xa(-D / 2 + pd / 2), Yv(Hd - ov - tb - pw / 2), Xa(-TOT / 2) - 40, Yv(Hd - 70), 4)
    leader(Xa(-20), Yv(Hd - ov - tb / 2), Xa(-TOT / 2) - 40, Yv(Hd - 30), 2)
    leader(Xa(-TOT / 2 + tf / 2), Yv(Hd * 0.3), Xa(-TOT / 2) - 40, Yv(Hd * 0.3), 3)
    leader(Xa(TOT / 2 - tf / 2), Yv(Hd * 0.3), Xa(TOT / 2) + 34, Yv(Hd * 0.3), 5)
    circle(Xa(TOT / 2 - 10), Yv(Hd - 12), 18, lw=0.3)
    T(Xa(TOT / 2) + 6, Yv(Hd - 12) + 22, "B", 11, font="FB")
    view_title(Xa(0), top - 96, "SECTION A-A", "1:5")
    # ---------------------------------------------------------------- 3D
    import r3d
    sc = r3d.Scene(yaw=-35, pitch=18)
    sc.box((ov, ov, -D / 2), (g["BW"], 0, 0), (0, g["BH"], 0), (0, 0, D), COL_BODY, edge=EDGE)
    sc.box((0, 0, D / 2), (Wd, 0, 0), (0, Hd, 0), (0, 0, tf), COL_FACE, edge=EDGE)
    sc.box((0, 0, -D / 2 - tf), (Wd, 0, 0), (0, Hd, 0), (0, 0, tf), COL_FACE, edge=EDGE)
    for yc in (ax, Hd - ax):
        sc.box((g["xb"], yc - fa / 2, -fb / 2), (LL, 0, 0), (0, fa, 0), (0, 0, fb), COL_FRAME, edge=EDGE)
        sc.box((g["xf"], yc - FLh / 2, -FLw / 2), (FLt, 0, 0), (0, FLh, 0), (0, 0, FLw), COL_FL, edge=EDGE)
    x3 = Xa(TOT / 2) + 110
    b3 = (x3, top + 20, K.IX1 - x3 - 20, K.VIEW_BOT - top - 60)
    sc.render(b3)
    view_title(b3[0] + b3[2] / 2, b3[1] + b3[3] + 18, "3D VIEW", "ILLUSTRATIVE - NOT TO SCALE")
    K.set_view(False)

    def detail(X_P6, BY0, W_P6, BH):
        K.header(X_P6, BY0, W_P6, "DETAIL B - EDGE (AS P6 / 3 mm)  1:1")
        rect(X_P6, BY0 + 12, W_P6, BH - 12, lw=0.6)
        K.set_view(True)
        s3 = MM
        ox, oy = X_P6 + 46, BY0 + 34
        Zx = lambda z: ox + (TOT / 2 - z) * s3
        Yb = lambda y: oy + y * s3                                  # y nuo stiklo krašto
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
        hchain(Yb(ymax) + 4, [Zx(TOT / 2), Zx(D / 2), Zx(D / 2 - pd)], [Yb(ymax)] * 3, [f"{tf:g}", f"{pd:g}"], size=K.F_DIM_FRAME)
        vchain(Zx(TOT / 2) - 10, [Yb(0), Yb(ov), Yb(ov + tb), Yb(ov + tb + pw)], [Zx(TOT / 2)] + [Zx(D / 2)] * 3,
               [f"{ov:g}", f"{tb:g}", f"{pw:g}"], size=K.F_DIM_FRAME)
        leader(Zx(TOT / 2 - tf / 2), Yb(ymax * 0.62), Zx(D / 2 - 30), Yb(ymax * 0.64), 3)
        leader(Zx(D / 2 - pd * 0.7), Yb(ov + tb + pw / 2), Zx(D / 2 - 26), Yb(ov + tb + pw + 14), 4)
        leader(Zx(D / 2 - pd - 8), Yb(ov + tb / 2), Zx(D / 2 - pd - 22), Yb(ov + tb + 10), 2)
        leader(Zx(fb / 2 - 10), Yb(ov + tb + fa * 0.6), X_P6 + W_P6 - 14, Yb(ov + tb + fa * 0.9), 1)
        leader(Zx(zs) + 1.1 * s3, Yb(ov + tb + pw + 2), Zx(zs) + 10, Yb(ov + tb + 26), 8)
        T(X_P6 + W_P6 - 4, BY0 + BH - 6, f"glass > body {ov:g} mm / side; side B mirror", 7, align="r", color=K.GREY)

    md = [["Product", "double-sided lightbox, projecting"],
          ["Glass (overall)", f"{Wd:g} x {Hd:g} x {TOT:g} mm"],
          ["Body", f"{g['BW']:g} x {g['BH']:g} x {D:g} (glass -{ov:g} / side)"],
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
    hchain(Yv(ylb) + 24, [X(x0), X(x0 + fa)] + [X(v) for v in led_x] + [X(xr - fa), X(xr)], [Yv(ylb)] * (len(led_x) + 4),
           [f"{fa:g}", f"{led_x[0] - x0 - fa:.1f}"] + [f"{g['led_step']:.1f}"] * (len(led_x) - 1) +
           [f"{xr - fa - led_x[-1]:.1f}", f"{fa:g}"], size=K.F_DIM_FRAME)
    hdim(X(x0 + fa), X(xr - fa), Yv(ylb) + 44, f"{g['led_span']:g}  ({g['led_n_row']} x {g['led_step']:.1f})",
         e1=Yv(ylb), e2=Yv(ylb), size=K.F_DIM_FRAME)
    vchain(X(x0) - 26, [Yv(x0), Yv(x0 + fa), Yv(x0 + FH - fa), Yv(x0 + FH)], [X(x0)] * 4,
           [f"{fa:g}", f"{g['L_v']:g}", f"{fa:g}"], size=K.F_DIM_FRAME)
    vchain(X(x0) - 48, [Yv(x0), Yv(x0 + FH)], [X(x0)] * 2, [f"{FH:g}"], size=K.F_DIM_MAIN)
    vchain(X(g["xf"] + FLt) + 24, [Yv(x0 + fa / 2), Yv(x0 + FH - fa / 2)], [X(g["xf"])] * 2, [f"{FH - fa:g}"],
           size=K.F_DIM_FRAME)
    K.tag(X(xr - fa / 2), Yv(x0 + FH * 0.4), X(xr) + 30, Yv(x0 + FH * 0.4) - 16, f"{g['L_v']:g} vert. (2 pcs.)", size=8)
    K.tag(X(g["xb"]), Yv(x0 + fa) + 2, X(g["xb"]) + 24, Yv(x0 + FH * 0.22), "body face (2)", size=7)
    K.tag(X(led_x[1]), Yv(yrow[0] - 6), X(led_x[1]) + 16, Yv(x0 + FH * 0.62),
          f"7: {g['led_n_row']} x {g['led_name']}" + (" (bottom + top)" if g["led_rows"] > 1 else " on bottom member"), size=8)
    K.tag(X(g["xf"] + FLt / 2), Yv(x0 + FH - fa / 2), X(g["xf"]) + 32, Yv(x0 + FH) + 70, "cable out: bottom leg + flange", size=7)
    leader(X(x0 + 150), Yv(x0 + fa / 2), X(x0 + 150) + 20, Yv(x0 + 60), 1)
    leader(X(g["xf"] + FLt / 2), Yv(x0 + fa / 2 + 30), X(g["xf"]) + 40, Yv(x0) + 40, "1A")
    T(X(x0 + FW / 2), Yv(x0 + FH / 2) - 4, "welded frame, all joints", 8, align="c", color=K.GREY)
    T(X(x0 + FW / 2), Yv(x0 + FH / 2) + 8, "view from side A (glass removed)", 8, align="c", color=K.GREY)
    xc_ = led_x[len(led_x) // 2]
    line(X(xc_), Yv(x0 + FH - fa - 45), X(xc_), Yv(x0 + FH - fa - 12), 0.4)
    T(X(xc_) + 3, Yv(x0 + FH - fa - 45) + 2, "C-C", 10, font="FB")
    view_title(X(x0 + g["L_h"] / 2), top - 96, "FRAME (1) + LED (7)", "1:5")
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
    leader(Zc(4), Yc(-4), Zc(D / 2 + tf) + 30, Yc(-40), 7)
    leader(Zc(-fb / 2 + 3), Yc(fa / 2), Zc(-D / 2 - tf) - 30, Yc(fa / 2), 1)
    leader(Zc(D / 2 - 10), Yc(fa + tb / 2), Zc(D / 2 + tf) + 30, Yc(fa + 12), 2)
    leader(Zc(-D / 2 - tf / 2), Yc(-up_ * 0.6), Zc(-D / 2 - tf) - 30, Yc(-up_ * 0.6), 3)
    leader(Zc(D / 2 + tf / 2), Yc(-up_ * 0.75), Zc(D / 2 + tf) + 30, Yc(-up_ * 0.8), 5)
    T(Zc(0), Yc(fa + tb) + 52, "LED on member centre - light to both faces", 8, align="c", color=K.GREY)
    view_title(Zc(0), top - 96, "SECTION C-C (LED)", "1:2")
    # ---------------------------------------------------------------- FLANGE 1:2
    flx = Zc(D / 2 + tf) + 110
    flange_view(g, flx, top + 20, s2)
    view_title(flx + FLw * s2 / 2, top - 96, "FLANGE 1A (2 pcs.)", "1:2")
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
                 [8, "Tapping screw (band -> frame)", "A2", "-", "8 pcs."]]
    md = [["Frame outer", f"{FW:g} x {FH:g} mm"],
          ["Profile", f"□{fa}x{fb}x{ft:g} Alu, centre of depth"],
          ["Legs", f"top + bottom members, +{g['xf'] - g['xb']:g} out of body"],
          ["Leg axes", f"{FH - fa:g} mm (from glass edge {g['ax']:g})"],
          ["Joints", "welded (TIG), ground"],
          ["Body fit", f"band {g['BW']:g} x {g['BH']:g} over frame"],
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
