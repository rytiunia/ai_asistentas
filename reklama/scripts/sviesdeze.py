#!/usr/bin/env python3
"""Dvipusė šviesdėžė nuo fasado (v134, Rytis 2026-10-12: „paprasčiausia dvipusė šviesdėžė nuo fasado - kojos tai pailgintos
rėmo dalys, apsijuosia aliumu, stiklas abiejose pusėse tvirtinasi kaip P6_3mm"). Etalonas:
assets/etalonai/sviesdeze_dvipuse_nuo_sienos.pdf (kliento / gamybos pavyzdys, 500 x 500 x 100, 1:8).

Konstrukcija (pozicijos kaip etalono Parts List):
  1  rėmas □30x30x2 Alu (gylio viduryje) - viršutinis ir apatinis skersiniai PAILGINTI iki sienos = kojos;
  1A kojos padas 100x100x8 Alu, 4 x Ø10 (64 x 64), centre - laido anga (vamzdžio vidus), privirintas;
  2  korpusas - 1,5 mm Alu juosta aplink (gylis = korpuso gylis), sienos pusėje angos kojoms;
  3/5 3 mm balta (opal) plexi abiejose pusėse (5 - veidrodinė pusė);
  4/6 3 mm PVC juosta plexi gale (P6_3mm principas: juosta priklijuota prie plexi, korpusas prisukamas į ją);
  7  LED + maitinimo blokas; 8 savisriegiai varžtai.
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
from reportlab.lib.colors import HexColor, white, black  # noqa: E402

DEF = {"client": "", "title": "DOUBLE-SIDED LIGHTBOX, WALL MOUNTED (PROJECTING)", "order_no": "", "drawing_no": "",
       "date": "2026-10-12", "rev": "A", "qty": 1,
       "w": 500, "h": 500, "depth": 100, "face_thk": 3.0, "band_thk": 1.5, "frame": [30, 30, 2],
       "leg_len": 100, "flange": [100, 100, 8], "flange_r": 10, "hole_d": 10, "hole_pitch": 64,
       "body_finish": "RAL ____", "frame_finish": "RAL ____", "face": "3 mm opal white plexiglass",
       "pvc_edge": [3, 15], "screw_step": 150, "led": "", "psu": "", "cable": "", "anchors": ""}

COL_BODY, COL_FRAME, COL_FACE, COL_PVC, COL_FL = (HexColor("#9C9C9C"), HexColor("#B4B4B4"), HexColor("#F4F4F2"),
                                                  HexColor("#C8C8C8"), HexColor("#8C8C8C"))


def main(spec_path, out):
    S = dict(DEF); S.update(json.load(open(spec_path, encoding="utf-8")))
    Wd, Hd, D, tf, tb = S["w"], S["h"], S["depth"], S["face_thk"], S["band_thk"]
    fa, fb, ft = S["frame"]
    LL = S["leg_len"]
    FLw, FLh, FLt = S["flange"]
    TOT = D + 2 * tf                                  # bendras storis su plexi
    PROJ = Wd + LL + FLt                              # išsikišimas nuo sienos
    ax = tb + fa / 2                                  # kojos ašis nuo korpuso viršaus / apačios
    FR = Wd - 2 * tb                                  # rėmo išorė
    L_h = FR + tb + LL                                # skersinis su koja: nuo rėmo kairės iki pado
    L_v = FR - 2 * fa
    # ---------------------------------------------------------------- kiekiai / svoris
    per = 2 * (Wd + Hd)
    pvc_len = 2 * 2 * (FR + FR)                       # 2 pusės x perimetras
    tube_a = (fa * fb - (fa - 2 * ft) * (fb - 2 * ft))
    prof_len = 2 * L_h + 2 * L_v
    rho = json.load(open(os.path.join(HERE, "..", "assets", "svoris.json")))["density_kg_dm3"]
    kg = (2 * Wd * Hd * tf * rho["pmma"] + per * D * tb * rho["al"] + prof_len * tube_a * rho["al"]
          + 2 * FLw * FLh * FLt * rho["al"] + pvc_len * S["pvc_edge"][0] * S["pvc_edge"][1] * rho["pvc"]) / 1e6
    n_scr_side = math.ceil(per / S["screw_step"])
    n_scr = 2 * n_scr_side + 8

    K.set_band(9)
    tmp = out + ".tmp"
    K.init(tmp, os.path.splitext(os.path.basename(out))[0])
    K.frame()
    K.set_view(True)
    s = MM / 5                                        # 1:5
    top = K.IY0 + 92

    # ================================================================ FRONT VIEW 1:5 (siena dešinėje)
    fx = K.IX0 + 78
    X = lambda x: fx + x * s
    Yv = lambda y: top + y * s
    rect(X(0), Yv(0), Wd * s, Hd * s, fill=COL_FACE, stroke=black, lw=0.1)
    # rėmas už plexi - punktyru
    for x0, y0, w_, h_ in ((tb, tb, FR, fa), (tb, Hd - tb - fa, FR, fa), (tb, tb + fa, fa, L_v), (Wd - tb - fa, tb + fa, fa, L_v)):
        rect(X(x0), Yv(y0), w_ * s, h_ * s, stroke=HexColor("#7A7A7A"), lw=0.1, dash=(2, 1.5))
    for yc in (ax, Hd - ax):
        rect(X(Wd), Yv(yc - fa / 2), LL * s, fa * s, fill=COL_FRAME, lw=0.1)
        rect(X(Wd + LL), Yv(yc - FLh / 2), FLt * s, FLh * s, fill=COL_FL, lw=0.1)
        K.centerline(X(Wd - 20), Yv(yc), X(PROJ + 12), Yv(yc))
    # matmenys
    hdim(X(0), X(Wd), Yv(0) - 30, f"{Wd:.0f}", e1=Yv(0), e2=Yv(0), size=K.F_DIM_MAIN)
    hchain(Yv(Hd) + 26, [X(0), X(Wd), X(Wd + LL), X(PROJ)], [Yv(Hd)] * 2 + [Yv(Hd - ax + FLh / 2)] * 2,
           [f"{Wd:.0f}", f"{LL:.0f}", f"{FLt:.0f}"], size=K.F_DIM_FRAME)
    hdim(X(0), X(PROJ), Yv(Hd) + 46, f"{PROJ:.0f}", e1=Yv(Hd), e2=Yv(Hd - ax + FLh / 2), size=K.F_DIM_MAIN)
    vchain(X(0) - 26, [Yv(0), Yv(Hd)], [X(0), X(0)], [f"{Hd:.0f}"], size=K.F_DIM_MAIN)
    vchain(X(PROJ) + 22, [Yv(0), Yv(ax), Yv(Hd - ax), Yv(Hd)], [X(Wd)] + [X(PROJ)] * 2 + [X(Wd)],
           [f"{ax:g}", f"{Hd - 2 * ax:g}", f"{ax:g}"], size=K.F_DIM_FRAME)
    leader(X(Wd * 0.3), Yv(Hd * 0.35), X(Wd * 0.3) - 40, Yv(Hd * 0.35) - 40, 3)
    leader(X(Wd + LL * 0.5), Yv(ax), X(Wd + LL * 0.5) + 6, Yv(ax) - 34, 1)
    leader(X(Wd + LL + FLt / 2), Yv(Hd - ax + FLh / 2 - 8), X(PROJ) + 50, Yv(Hd - ax) + 40, "1A")
    leader(X(tb + fa / 2), Yv(Hd * 0.6), X(0) + 30, Yv(Hd * 0.6) + 30, 1)
    T(X(Wd / 2), Yv(Hd / 2) + 4, "SIDE A", 10, align="c", color=K.GREY)
    view_title(X(PROJ / 2), top - 66, "FRONT VIEW (SIDE A)", "1:5  (side B - mirrored)")
    T(X(PROJ) + 4, Yv(-FLh / 2 + ax) - 6, "WALL", 7, color=K.GREY)

    # ================================================================ SIDE VIEW iš sienos pusės 1:5
    sx = X(PROJ) + 120
    Xs = lambda z: sx + (z + TOT / 2) * s          # z - gylis nuo vidurio
    rect(Xs(-TOT / 2), Yv(0), TOT * s, Hd * s, fill=COL_BODY, lw=0.1)
    for zz in (-TOT / 2, TOT / 2 - tf):
        rect(Xs(zz), Yv(0), tf * s, Hd * s, fill=COL_FACE, lw=0.1)
    for yc in (ax, Hd - ax):
        rect(Xs(-FLw / 2), Yv(yc - FLh / 2), FLw * s, FLh * s, fill=COL_FL, lw=0.1)
        hp = S["hole_pitch"] / 2
        for dz in (-hp, hp):
            for dy in (-hp, hp):
                circle(Xs(dz), Yv(yc + dy), S["hole_d"] / 2 * s, fill=white, lw=0.1)
        ci = fa - 2 * ft
        rect(Xs(-ci / 2), Yv(yc - ci / 2), ci * s, ci * s, fill=white, lw=0.1)
    hdim(Xs(-TOT / 2), Xs(TOT / 2), Yv(0) - 30, f"{TOT:.0f}", e1=Yv(0), e2=Yv(0), size=K.F_DIM_MAIN)
    hchain(Yv(Hd) + 26, [Xs(-TOT / 2), Xs(-TOT / 2 + tf), Xs(TOT / 2 - tf), Xs(TOT / 2)], [Yv(Hd)] * 4,
           [f"{tf:g}", f"{D:g}", f"{tf:g}"], size=K.F_DIM_FRAME)
    leader(Xs(FLw / 2 - 4), Yv(ax + 30), Xs(TOT / 2) + 34, Yv(ax + 60), "1A")
    leader(Xs(TOT / 2 - tf / 2), Yv(Hd * 0.5), Xs(TOT / 2) + 34, Yv(Hd * 0.5), 5)
    leader(Xs(-TOT / 2 + tf / 2), Yv(Hd * 0.42), Xs(-TOT / 2) - 30, Yv(Hd * 0.42), 3)
    leader(Xs(0), Yv(Hd * 0.62), Xs(TOT / 2) + 34, Yv(Hd * 0.66), 2)
    view_title(Xs(0), top - 66, "SIDE VIEW (FROM WALL)", "1:5")

    # ================================================================ SECTION A-A 1:5 (vertikalus pjūvis korpuso viduryje)
    ax_ = Xs(TOT / 2) + 110
    Xa = lambda z: ax_ + (z + TOT / 2) * s
    pw, pd = S["pvc_edge"]
    # vidinis vertikalus rėmo narys (matomas už pjūvio)
    rect(Xa(-fb / 2), Yv(tb + fa), fb * s, L_v * s, fill=HexColor("#D6D6D6"), lw=0.1)
    for yy in (0.25, 0.5, 0.75):                     # LED moduliai ant rėmo (7)
        yc = tb + fa + L_v * yy
        rect(Xa(-fb / 2) - 3.2, Yv(yc - 9), 3.2, 18 * s, fill=white, lw=0.1)
        rect(Xa(fb / 2), Yv(yc - 9), 3.2, 18 * s, fill=white, lw=0.1)
    for y0 in (0, Hd - tb):                           # korpusas (pjūvis)
        rect(Xa(-D / 2), Yv(y0), D * s, tb * s, fill=COL_BODY, lw=0.1)
    for zz in (-TOT / 2, TOT / 2 - tf):               # plexi (pjūvis)
        rect(Xa(zz), Yv(0), tf * s, Hd * s, fill=COL_FACE, lw=0.1)
    for y0 in (tb, Hd - tb - pw):                     # PVC juostos (P6: po korpusu, nuo plexi į vidų)
        rect(Xa(-D / 2), Yv(y0), pd * s, pw * s, fill=COL_PVC, lw=0.1)
        rect(Xa(D / 2 - pd), Yv(y0), pd * s, pw * s, fill=COL_PVC, lw=0.1)
    for y0 in (tb, Hd - tb - fa):                     # rėmo skersiniai (pjūvis)
        rect(Xa(-fb / 2), Yv(y0), fb * s, fa * s, fill=COL_FRAME, lw=0.1)
        rect(Xa(-fb / 2 + ft), Yv(y0 + ft), (fb - 2 * ft) * s, (fa - 2 * ft) * s, fill=white, lw=0.1)
    vchain(Xa(-TOT / 2) - 22, [Yv(0), Yv(Hd)], [Xa(-TOT / 2)] * 2, [f"{Hd:.0f}"], size=K.F_DIM_FRAME)
    hchain(Yv(Hd) + 26, [Xa(-TOT / 2), Xa(-fb / 2), Xa(fb / 2), Xa(TOT / 2)], [Yv(Hd)] * 4,
           [f"{(TOT - fb) / 2:g}", f"{fb:g}", f"{(TOT - fb) / 2:g}"], size=K.F_DIM_FRAME)
    leader(Xa(0), Yv(tb + fa / 2), Xa(TOT / 2) + 34, Yv(30), 1)
    leader(Xa(fb / 2) + 2, Yv(tb + fa + L_v * 0.5), Xa(TOT / 2) + 34, Yv(Hd * 0.45), 7)
    leader(Xa(D / 2 - pd / 2), Yv(Hd - tb - pw / 2), Xa(TOT / 2) + 34, Yv(Hd - 50), 6)
    leader(Xa(-D / 2 + pd / 2), Yv(Hd - tb - pw / 2), Xa(-TOT / 2) - 34, Yv(Hd - 70), 4)
    leader(Xa(0) - 10, Yv(Hd - tb / 2), Xa(-TOT / 2) - 34, Yv(Hd - 20), 2)
    circle(Xa(TOT / 2 - 10), Yv(Hd - 12), 18, lw=0.3)
    T(Xa(TOT / 2) + 6, Yv(Hd - 12) + 22, "B", 11, font="FB")
    view_title(Xa(0), top - 66, "SECTION A-A", "1:5")

    # ================================================================ FLANGE 1:2
    s2 = MM / 2
    flx, fly = Xa(TOT / 2) + 130, top + 10
    rx = lambda v: flx + (v + FLw / 2) * s2
    ry = lambda v: fly + (v + FLh / 2) * s2
    rr = S["flange_r"]
    pts = []
    for cx_, cy_, a0 in ((FLw / 2 - rr, -FLh / 2 + rr, -90), (FLw / 2 - rr, FLh / 2 - rr, 0),
                         (-FLw / 2 + rr, FLh / 2 - rr, 90), (-FLw / 2 + rr, -FLh / 2 + rr, 180)):
        for k_ in range(7):
            a = math.radians(a0 + 15 * k_)
            pts.append((rx(cx_ + rr * math.cos(a)), ry(cy_ + rr * math.sin(a))))
    poly(pts, fill=COL_FL, lw=0.1)
    hp = S["hole_pitch"] / 2
    for dz in (-hp, hp):
        for dy in (-hp, hp):
            circle(rx(dz), ry(dy), S["hole_d"] / 2 * s2, fill=white, lw=0.1)
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
    K.tag(rx(hp) + 2, ry(-hp) - 2, rx(-FLw / 2) - 6, ry(-FLh / 2) - 14, f"4 x Ø{S['hole_d']:g}", align="r")
    K.tag(rx(0) + 3, ry(0) + 3, rx(-FLw / 2) - 6, ry(FLh / 2) + 10, f"cable □{ci:g} (tube)", align="r")
    T(flx + FLw * s2 / 2, ry(FLh / 2) + 50, f"t = {FLt:g} mm, welded to leg □{fa}x{fb}x{ft:g}, R{rr:g}", 8, align="c")
    view_title(flx + FLw * s2 / 2, top - 66, "FLANGE 1A (x2)", "1:2")

    # ================================================================ 3D
    import r3d
    sc = r3d.Scene(yaw=-35, pitch=18)
    z0, z1 = -D / 2, D / 2
    sc.box((0, 0, z0), (Wd, 0, 0), (0, Hd, 0), (0, 0, D), COL_BODY, edge=HexColor("#555555"))
    sc.box((0, 0, z1), (Wd, 0, 0), (0, Hd, 0), (0, 0, tf), COL_FACE, edge=HexColor("#555555"))
    sc.box((0, 0, z0 - tf), (Wd, 0, 0), (0, Hd, 0), (0, 0, tf), COL_FACE, edge=HexColor("#555555"))
    for yc in (ax, Hd - ax):
        sc.box((Wd, yc - fa / 2, -fb / 2), (LL, 0, 0), (0, fa, 0), (0, 0, fb), COL_FRAME, edge=HexColor("#555555"))
        sc.box((Wd + LL, yc - FLh / 2, -FLw / 2), (FLt, 0, 0), (0, FLh, 0), (0, 0, FLw), COL_FL, edge=HexColor("#555555"))
    b3 = (flx - 20, ry(FLh / 2) + 90, 270, K.VIEW_BOT - (ry(FLh / 2) + 90) - 30)
    sc.render(b3)
    view_title(b3[0] + b3[2] / 2, b3[1] + b3[3] + 16, "3D VIEW", "ILLUSTRATIVE - NOT TO SCALE")
    K.set_view(False)

    # ================================================================ apatinė juosta
    BY0 = K.BAND_Y; BH = K.IY1 - BY0
    W_P6, W_MD, W_TB = 200, 200, 272
    X_P6 = K.IX0; X_TB = K.IX1 - W_TB; X_MD = X_TB - W_MD; X_BOM = X_P6 + W_P6; W_BOM = X_MD - X_BOM
    # DETAIL B 1:2 - kraštas (P6_3mm principas)
    K.header(X_P6, BY0, W_P6, "DETAIL B - EDGE (AS P6 / 3 mm)  1:1")
    rect(X_P6, BY0 + 12, W_P6, BH - 12, lw=0.6)
    K.set_view(True)
    s3 = MM / 1                                       # 1:1
    ox, oy = X_P6 + 14, BY0 + 30
    Zx = lambda z: ox + (TOT / 2 - z) * s3            # z nuo vidurio; kairėje plexi A
    Yb = lambda y: oy + y * s3                        # y nuo korpuso viršaus žemyn
    ymax = (BH - 30) / s3 - 4
    zend = fb / 2 - 2 * ft - 6
    wpx = lambda z0, z1: (z0 - z1) * s3
    rect(Zx(TOT / 2), Yb(0), tf * s3, ymax * s3, fill=COL_FACE, lw=0.1)                    # 3 plexi
    rect(Zx(D / 2), Yb(0), wpx(D / 2, zend), tb * s3, fill=COL_BODY, lw=0.1)                 # 2 korpusas
    rect(Zx(D / 2), Yb(tb), pd * s3, pw * s3, fill=COL_PVC, lw=0.1)                          # 4 PVC
    rect(Zx(fb / 2), Yb(tb), wpx(fb / 2, zend), fa * s3, fill=COL_FRAME, lw=0.1)             # 1 rėmas
    rect(Zx(fb / 2 - ft), Yb(tb + ft), wpx(fb / 2 - ft, zend), (fa - 2 * ft) * s3, fill=white, lw=0.1)
    zl = Zx(zend)
    line(zl, Yb(-3), zl, Yb(tb + fa + 3), 0.1, dash=([4, 1, 1, 1], 0))                           # lūžio linija
    zs = D / 2 - pd / 2                                                                         # 8 varžtas korpusas -> PVC
    rect(Zx(zs) - 2.4 * s3, Yb(-1.6), 4.8 * s3, 1.6 * s3, fill=HexColor("#3A3A3A"), lw=0.1)
    rect(Zx(zs) - 1.1 * s3, Yb(0), 2.2 * s3, (tb + pw + 4) * s3, fill=HexColor("#3A3A3A"), lw=0.1)
    K.centerline(Zx(zs), Yb(-5), Zx(zs), Yb(tb + pw + 7))
    K.set_view(False)
    hchain(Yb(ymax) + 2, [Zx(TOT / 2), Zx(D / 2), Zx(D / 2 - pd)], [Yb(ymax)] * 3, [f"{tf:g}", f"{pd:g}"], size=K.F_DIM_FRAME)
    leader(Zx(TOT / 2 - tf / 2), Yb(ymax * 0.6), Zx(D / 2 - 30), Yb(ymax * 0.62), 3)
    leader(Zx(D / 2 - pd * 0.7), Yb(tb + pw / 2), Zx(D / 2 - 26), Yb(tb + pw + 14), 4)
    leader(Zx(D / 2 - pd - 8), Yb(tb / 2), Zx(D / 2 - pd - 20), Yb(tb + 10), 2)
    leader(Zx(fb / 2 - 10), Yb(tb + fa * 0.6), X_P6 + W_P6 - 14, Yb(tb + fa * 0.9), 1)
    leader(Zx(zs) + 1.1 * s3, Yb(tb + pw + 2), Zx(zs) + 10, Yb(tb + 24), 8)
    T(X_P6 + W_P6 - 4, BY0 + BH - 6, "same on side B (mirror: 5 / 6)", 7, align="r", color=K.GREY)

    md = [["Product", "double-sided lightbox, projecting"],
          ["Size", f"{Wd:.0f} x {Hd:.0f} x {TOT:.0f} mm"],
          ["From wall", f"{PROJ:.0f} mm (legs {LL:.0f} + flange {FLt:g})"],
          ["Faces", f"2 x {S['face']}"],
          ["Fixing", f"2 legs, flange 4 x Ø{S['hole_d']:g} {S['anchors']}".strip()],
          ["LED / PSU", (S["led"] + (" / " + S["psu"] if S["psu"] else "")) or "per LED calc.:"],
          ["Cable", S["cable"] or "through leg tube + flange:"],
          ["Qty", f"{S['qty']} pcs."],
          ["Weight (calc.)", f"≈ {kg:.1f} kg / pcs, excl. PSU"]]
    K.main_data(X_MD, BY0, W_MD, BH, md, lab_w=62)
    bom = [[1, f"Frame + legs □{fa}x{fb}x{ft:g}", "Alu EN AW-6060", S["frame_finish"],
            f"2 x {L_h:.0f} (legs) + 2 x {L_v:.0f} = {prof_len:.0f} mm"],
           ["1A", f"Flange {FLw:g}x{FLh:g}x{FLt:g}, 4 x Ø{S['hole_d']:g}", "Alu, welded", S["frame_finish"], "2 pcs."],
           [2, f"Body band {tb:g} mm, {D:.0f} wide", "Alu sheet", S["body_finish"], f"{per:.0f} x {D:.0f} mm, 2 leg cut-outs"],
           [3, "Face A", S["face"], "-", f"{Wd:.0f} x {Hd:.0f} = {Wd * Hd / 1e6:.2f} m²"],
           [4, f"PVC edge {pw:g} x {pd:g} (face A)", "PVC", "white", f"{2 * (FR + FR):.0f} mm"],
           [5, "Face B (mirror)", S["face"], "-", f"{Wd:.0f} x {Hd:.0f} = {Wd * Hd / 1e6:.2f} m²"],
           [6, f"PVC edge {pw:g} x {pd:g} (face B)", "PVC", "white", f"{2 * (FR + FR):.0f} mm"],
           [7, "LED modules + PSU", S["led"] or "per LED calc.:", "-", ""],
           [8, "Tapping screw (band -> PVC / frame)", "A2", "-", f"≈ {n_scr} pcs. (step ≤ {S['screw_step']})"]]
    K.bom_table(X_BOM, BY0, W_BOM, BH, bom)
    spec = {"client": S["client"], "title": S["title"], "order_no": S["order_no"], "drawing_no": S["drawing_no"],
            "sheet": "1 / 1", "rev": S["rev"], "date": S["date"]}
    K.title_block(X_TB, W_TB, spec, "1:5 / 1:2")
    K.save(out)
    os.path.exists(tmp) and os.remove(tmp)
    print("OK", out, f"svoris {kg:.2f} kg, profilis {prof_len:.0f} mm", "netelpa:", K.OVERFLOW)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
