#!/usr/bin/env python3
"""Dvipusė šviesdėžė nuo fasado - 2 lapai (v134-v135, Rytis 2026-10-12).

v134: „paprasčiausia dvipusė šviesdėžė nuo fasado - kojos tai pailgintos rėmo dalys, apsijuosia aliumu, stiklas abiejose
pusėse tvirtinasi kaip 5S (buv. P6_3mm)". Etalonas assets/etalonai/sviesdeze_dvipuse_nuo_sienos.pdf (500 x 500 x 100, 1:8).
v135: „reikia detaliau - nėra rėmo matmenų, nėra bendrų matmenų tarp montavimo plokščių skylių x/y, neaišku kaip LED dedasi
ir kokie. 5S (buv. P6_3mm) tipo tvirtinimai - stiklas visada didesnis už korpusą, korpusas mažesnis už stiklą 1.5-2 mm."
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
import koju_uzdengimas as KU  # noqa: E402
from lapas_core import T, line, rect, poly, circle, hdim, vchain, hchain, leader, view_title, MM  # noqa: E402
from reportlab.lib.colors import HexColor, white  # noqa: E402

DEF = {"client": "", "title": "DOUBLE-SIDED LIGHTBOX, WALL MOUNTED (PROJECTING)", "order_no": "", "drawing_no": "",
       "date": "2026-10-12", "rev": "A", "qty": 1,
       "w": 500, "h": 500, "depth": 140, "face_thk": 3.0, "face_over": 1.5, "band_thk": 1.5, "frame": [30, 30, 2],
       "leg_len": 100, "flange": [100, 100, 8], "flange_r": 10, "hole_d": 10, "hole_pitch": 64,
       "body_finish": "RAL ____", "frame_finish": "RAL ____", "face": "3 mm opal white plexiglass",
       "pvc_edge": [3, 15], "screw_step": 150, "led": "DS15", "led_rows": None, "led_pitch": None,
       "cable": "", "anchors": "", "scale_ga": 8, "screws_per_edge": 3, "logo": None,
       # v144: "legs_type": "inset" - kojos ŽEMESNĖS už dėžę (atskiri □40x40x4 vamzdžiai po rėmo skersiniais, viena
       # montavimo plokštė, kojų uždengimai 2 mm Alu, trafo plokštelė); "frame" - pailginti rėmo skersiniai (v134)
       "legs_type": "frame", "leg": [40, 40, 4], "leg_in": 53, "leg_chamfer": 50, "plate": [140, None, 5],
       "plate_pitch": 109, "plate_hole_d": 8, "cable_hole": 11, "cover_w": None, "cover_thk": 2, "cover_gap": 5, "trafo_plate": [40, 1.5],
       "proj": None}
COL_BODY, COL_FRAME, COL_FACE, COL_PVC, COL_FL, COL_LED = (HexColor("#9C9C9C"), HexColor("#B4B4B4"), HexColor("#F4F4F2"),
                                                           HexColor("#C8C8C8"), HexColor("#8C8C8C"), HexColor("#F2C230"))
EDGE = HexColor("#555555")
COL_INWHITE = HexColor("#F2F2F2")                                   # v220: rėmas viduje / korpuso vidus - balti

# v220 (Rytis 2026-10-14): 2 lapas - kaip CAD brėžinys, BE SPALVŲ, tik linijos (_CAD = True tik sheet2)
_CAD = False
_k_rect, _k_poly, _k_circle, _k_line, _k_T = rect, poly, circle, line, T


def _cad_args(fill, stroke):
    if not _CAD:
        return fill, stroke
    return (white if fill is not None else None), (K.black if stroke is not None else None)


def rect(x, y, w, h, fill=None, stroke=K.black, lw=0.5, dash=None):
    fill, stroke = _cad_args(fill, stroke)
    _k_rect(x, y, w, h, fill=fill, stroke=stroke, lw=lw, dash=dash)


def poly(pts, fill=None, stroke=K.black, lw=0.5, close=True, dash=None):
    fill, stroke = _cad_args(fill, stroke)
    _k_poly(pts, fill=fill, stroke=stroke, lw=lw, close=close, dash=dash)


def circle(x, y, r, fill=None, stroke=K.black, lw=0.5, dash=None):
    fill, stroke = _cad_args(fill, stroke)
    _k_circle(x, y, r, fill=fill, stroke=stroke, lw=lw, dash=dash)


def line(x1, y1, x2, y2, w=0.3, col=K.black, dash=None):
    _k_line(x1, y1, x2, y2, w, K.black if _CAD else col, dash)


def T(x, y, txt, size=7.5, *a, color=None, **kw):
    if _CAD and color is not None:
        color = K.black
    if color is None:
        _k_T(x, y, txt, size, *a, **kw)
    else:
        _k_T(x, y, txt, size, *a, color=color, **kw)


def geom(S):
    g = dict(S)
    W_, H_, D = S["w"], S["h"], S["depth"]
    ov, tb, (fa, fb, ft) = S["face_over"], S["band_thk"], S["frame"]
    g["BW"], g["BH"] = W_ - 2 * ov, H_ - 2 * ov                   # korpusas (Alu juosta) - mažesnis už stiklą
    g["FW"], g["FH"] = g["BW"] - 2 * tb, g["BH"] - 2 * tb          # rėmo išorė
    g["x0"] = ov + tb                                               # rėmo kairė nuo stiklo krašto
    g["ax"] = ov + tb + fa / 2                                      # kojos ašis nuo stiklo viršaus / apačios
    g["xb"] = W_ - ov                                               # korpuso išorė sienos pusėje
    g["xr"] = g["x0"] + g["FW"]                                     # rėmo išorė sienos pusėje
    inset = S.get("legs_type") == "inset"
    g["inset"] = inset
    PT = S["plate"][2] if inset else S["flange"][2]
    if S.get("proj"):                                               # atstumas nuo sienos iki tolimo stiklo krašto
        g["leg_len"] = S["proj"] - PT - g["xb"]
    g["xf"] = g["xb"] + g["leg_len"]                                # pado / plokštės vidinis paviršius
    g["PROJ"] = g["xf"] + PT                                        # siena nuo stiklo tolimo krašto
    g["L_h"] = g["xf"] - g["x0"]                                    # skersinis su koja
    g["L_v"] = g["FH"] - 2 * fa                                     # statmuo tarp skersinių
    g["TOT"] = D + 2 * S["face_thk"]
    if inset:
        lw_, ld_, lt_ = S["leg"]
        g["ax"] = ov + tb + fa + lw_ / 2                            # koja tiesiai po skersiniu (rėmo viduje)
        PLw, PLh, PLt = S["plate"]
        PLh = PLh or (H_ - 2 * g["ax"] + lw_ + 16)
        g["PLw"], g["PLh"], g["PLt"] = PLw, PLh, PLt
        g["leg_x0"] = g["xr"] - S["leg_in"]                         # kojos pradžia (ilgoji briauna prie skersinio)
        g["leg_dxc"] = lw_ / math.tan(math.radians(S["leg_chamfer"]))
        g["L_leg"] = g["xf"] - g["leg_x0"]
        g["L_h"] = g["FW"]
        pp = S["plate_pitch"] / 2
        g["legs"] = [dict(y=y_, h=lw_, d=ld_) for y_ in (g["ax"], H_ - g["ax"])]
        g["plates"] = [dict(yc=H_ / 2, h=PLh, w=PLw, t=PLt, r=0, d=S["plate_hole_d"], tube=None,
                            holes=[(dz, y_) for y_ in (g["ax"], H_ - g["ax"]) for dz in (-pp, pp)],
                            cable=(0, g["ax"] + lw_ / 2 + 12, S["cable_hole"]))]
        # v217 („Bendrinės taisyklės" 19): bendras modulis - plotis kojos + 10, aukštis kojų matmuo + 2t, briaunos 10 su išpjovomis
        g["covers"] = [KU.make([g["ax"], H_ - g["ax"]], lw_, ld_, g["leg_len"], thk=S["cover_thk"], gap=S["cover_gap"],
                               w=S["cover_w"])]
        g["led_a"], g["led_b"] = g["x0"] + fa, g["leg_x0"] - 10    # LED skersinyje iki kojos
        g["x_tp"] = g["leg_x0"] + g["leg_dxc"] + 6                   # trafo plokštelė (y-z plokštumoje) tarp kojų
        g["tp_h"] = H_ - 2 * g["ax"] - lw_
    else:
        FLw, FLh, FLt = S["flange"]; hp_ = S["hole_pitch"] / 2
        g["legs"] = [dict(y=y_, h=fa, d=fb) for y_ in (g["ax"], H_ - g["ax"])]
        g["plates"] = [dict(yc=y_, h=FLh, w=FLw, t=FLt, r=S["flange_r"], d=S["hole_d"], tube=fa - 2 * ft, cable=None,
                            holes=[(dz, y_ + dy) for dz in (-hp_, hp_) for dy in (-hp_, hp_)]) for y_ in (g["ax"], H_ - g["ax"])]
        g["covers"] = []
        g["led_a"], g["led_b"] = g["x0"] + fa, g["xr"] - fa
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
    span = g["led_b"] - g["led_a"]                                  # tarp statmenų / iki kojos
    n_row = math.ceil(span / p)
    rows_n = S["led_rows"] or 2                                      # v139 Rytis: LED apačioje IR viršuje
    g.update(du=du, led_name="DUOLITE " + S["led"], led_box=hb, led_dep=dep, led_lux=best[3], led_p=p,
             led_step=span / n_row, led_n_row=n_row, led_rows=rows_n, led_n=n_row * rows_n, led_span=span)
    g["led_W"] = g["led_n"] * du["W"]
    import led_km
    g["psu"] = led_km.psu_for(g["led_W"], 12)
    # kiekiai, svoris
    per_b = 2 * (g["BW"] + g["BH"])
    g["per_b"] = per_b
    g["pvc_len"] = 2 * (g["BW"] - 2 * tb + g["BH"] - 2 * tb)
    g["prof_len"] = 2 * g["L_h"] + (1 if inset else 2) * g["L_v"]
    rho = json.load(open(os.path.join(HERE, "..", "assets", "svoris.json")))["density_kg_dm3"]
    tube_a = fa * fb - (fa - 2 * ft) * (fb - 2 * ft)
    pl_v = sum(P["w"] * P["h"] * P["t"] for P in g["plates"])
    extra = 0
    if inset:
        lw_, ld_, lt_ = S["leg"]
        extra = 2 * g["L_leg"] * (lw_ * ld_ - (lw_ - 2 * lt_) * (ld_ - 2 * lt_))
        C = g["covers"][0]
        extra += (2 * g["leg_len"] * (C["y1"] - C["y0"]) + 2 * g["leg_len"] * C["w"]) * S["cover_thk"]
        extra += g["tp_h"] * S["trafo_plate"][0] * S["trafo_plate"][1]
    g["kg"] = (2 * W_ * H_ * S["face_thk"] * rho["pmma"] + per_b * D * tb * rho["al"] + g["prof_len"] * tube_a * rho["al"]
               + (pl_v + extra) * rho["al"] + 2 * g["pvc_len"] * S["pvc_edge"][0] * S["pvc_edge"][1] * rho["pvc"]) / 1e6
    # D3.2 varžtų skylės korpuso juostoje: kiekvienoje kraštinėje 2 eilės (z = +-(D/2 - PVC/2), į PVC juostą) kas <= step
    # (v137: per juostos centrą skylių NĖRA - juosta virinama prie rėmo). Kraštinės: top, wall, bottom, front (išklotinės tvarka nuo viršutinio kairio kampo)
    pd_ = S["pvc_edge"][1]
    zs = D / 2 - pd_ / 2
    faces = [("top", g["BW"]), ("wall", g["BH"]), ("bottom", g["BW"]), ("front", g["BH"])]
    holes = []
    for fn, L in faces:
        n = S["screws_per_edge"] or math.ceil(L / S["screw_step"])     # v139 Rytis: 3 vnt. kraštinei
        for i in range(n):
            for z in (-zs, zs):
                holes.append((fn, L * (i + 0.5) / n, z, "pvc"))
    g["scr_holes"] = holes
    g["scr_n_face"] = S["screws_per_edge"] or math.ceil(g["BW"] / S["screw_step"])
    g["scr_wall"] = [(ov + u, z, k) for fn, u, z, k in holes if fn == "wall"]
    g["n_scr"] = len(holes)
    # v140: logotipas (kliento PNG -> vektorius), abiejose pusėse, centre
    g["logo_r"] = None
    if S.get("logo"):
        import vektorius
        L_ = S["logo"]
        g["logo_r"] = vektorius.rings(L_["file"], L_["width"])
        g["logo_w"], g["logo_h"] = vektorius.size(g["logo_r"])
        g["logo_x"] = (W_ - g["logo_w"]) / 2
        g["logo_y"] = L_.get("top", (H_ - g["logo_h"]) / 2)
        g["logo_col"] = HexColor(L_.get("color", "#000000"))
        g["logo_mat"] = L_.get("material", "film:")
    return g


def prof(a, b, t):
    """profilio pavadinimas: □30x30x2 / 40x20x2 (stačiakampis - didesnė kraštinė pirma)"""
    return f"□{a:g}x{b:g}x{t:g}" if a == b else f"{max(a, b):g}x{min(a, b):g}x{t:g}"


def bom_rows(g):
    fa, fb, ft = g["frame"]
    FLw, FLh, FLt = g["flange"]
    pw, pd = g["pvc_edge"]
    if g["inset"]:
        lw_, ld_, lt_ = g["leg"]
        P = g["plates"][0]
        head = [[1, f"Frame {prof(fa, fb, ft)} (sheet 2)", "Alu EN AW-6060", "white (inside)",
                 f"2 x {g['L_h']:g} + 1 x {g['L_v']:g} = {g['prof_len']:g} mm"],
                ["1B", f"Legs {prof(lw_, ld_, lt_)}, end {g['leg_chamfer']:g}°", "Alu, welded to frame", g["frame_finish"],
                 f"2 x {g['L_leg']:.0f} mm"],
                ["1A", f"Mounting plate {P['w']:g}x{P['h']:g}x{P['t']:g}, 4 x Ø{P['d']:g} + Ø{g['cable_hole']:g}",
                 "Alu, welded to legs", g["frame_finish"], "1 pc."],
                ["1C", f"Trafo plate {g['trafo_plate'][1]:g} mm (PSU)", "Alu, welded between legs", "-",
                 f"{g['tp_h']:g} x {g['trafo_plate'][0]:g} mm"]]
    else:
        head = [[1, f"Frame + legs {prof(fa, fb, ft)}, in body white", "Alu EN AW-6060", f"{g['frame_finish']} legs",
                 f"2 x {g['L_h']:g} + 2 x {g['L_v']:g} = {g['prof_len']:g} mm"],
                ["1A", f"Flange {FLw:g}x{FLh:g}x{FLt:g}, 4 x Ø{g['hole_d']:g}", "Alu, welded to leg", g["frame_finish"], "2 pcs."]]
    return head + [[2, f"Body band {g['band_thk']:g} x {g['depth']:g}, inside white", "Alu, folded, welded to frame", f"{g['body_finish']} out",
             f"{g['BW']:g} x {g['BH']:g}: {g['per_b']:g} mm"],
            [3, "Face A (glass)", g["face"], "-", f"{g['w']:g} x {g['h']:g} = {g['w'] * g['h'] / 1e6:.2f} m²"],
            [4, f"PVC edge {pw:g} x {pd:g} (face A)", "PVC, glued to face", "white", f"{g['pvc_len']:g} mm"],
            [5, "Face B (glass, mirror)", g["face"], "-", f"{g['w']:g} x {g['h']:g} = {g['w'] * g['h'] / 1e6:.2f} m²"],
            [6, f"PVC edge {pw:g} x {pd:g} (face B)", "PVC, glued to face", "white", f"{g['pvc_len']:g} mm"],
            [7, f"LED Kaisen {g['led_name']} + PSU", f"PSU {g['psu'][0].replace('-5Y', '')}", "6500 K",
             f"{g['led_n']} pcs. ({g['led_W']:.1f} W) + 1 PSU"],
            [8, "Tapping screw, D3.2 holes", "A2", "-", f"{g['n_scr']} pcs. (into PVC edge)"]] + (
           [[9, "Logo, sides A + B", g["logo_mat"], "black", f"2 pcs., {g['logo_w']:g} x {g['logo_h']:.0f} mm"]]
           if g.get("logo_r") else []) + (
           [[10, *KU.bom_desc(g["covers"][0]), g["body_finish"], f"2 pcs., {KU.size_txt(g['covers'][0])}"]]
           if g["covers"] else [])


def band(g, sheet, title_extra, md, bom, detail_fn, scales="1:5 / 1:2 / 1:1"):
    BY0 = K.BAND_Y; BH = K.IY1 - BY0
    W_P6, W_MD, W_TB = 214, 214, 272
    X_P6 = K.IX0; X_TB = K.IX1 - W_TB; X_MD = X_TB - W_MD; X_BOM = X_P6 + W_P6; W_BOM = X_MD - X_BOM
    detail_fn(X_P6, BY0, W_P6, BH)
    K.main_data(X_MD, BY0, W_MD, BH, md, lab_w=64)
    K.bom_table(X_BOM, BY0, W_BOM, BH, bom)
    spec = {"client": g["client"], "title": g["title"] + title_extra, "order_no": g["order_no"],
            "drawing_no": g["drawing_no"], "sheet": sheet, "rev": g["rev"], "date": g["date"]}
    K.title_block(X_TB, W_TB, spec, scales)


D1, D2 = 16, 36                                                     # v145: 1 eilė (grandinė), 2 eilė (gabaritas)


def HM(x1, x2, y, label, e1, e2, size=None):
    """v141 PAGRINDINIS (gabaritinis) horizontalus matmuo - ARČIAUSIAI objekto, 12 pt, tekstas su baltu fonu
    (papildomų grandinių išvadinės jo neuždengia); braižomas PO papildomų grandinių"""
    size = size or K.F_DIM_MAIN
    hdim(x1, x2, y, "", e1=e1, e2=e2, size=size)                 # v198: tekstas vieną kartą (su baltu fonu), ne dvigubas
    K._Tbg((x1 + x2) / 2, y - 2.5, label, size, align="c")


def VM(x, y1, y2, ext, label, size=None):
    vchain(x, [y1, y2], [ext, ext], [label], size=size or K.F_DIM_MAIN, bg=True)


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
    hchain(ry(FLh / 2) + D1, [rx(-FLw / 2), rx(-hp), rx(hp), rx(FLw / 2)], [ry(FLh / 2)] + [ry(hp)] * 2 + [ry(FLh / 2)],
           [f"{FLw / 2 - hp:g}", f"{2 * hp:g}", f"{FLw / 2 - hp:g}"], size=K.F_DIM_FRAME)
    vchain(rx(FLw / 2) + D1, [ry(-FLh / 2), ry(-hp), ry(hp), ry(FLh / 2)], [rx(FLw / 2)] + [rx(hp)] * 2 + [rx(FLw / 2)],
           [f"{FLh / 2 - hp:g}", f"{2 * hp:g}", f"{FLh / 2 - hp:g}"], size=K.F_DIM_FRAME)
    HM(rx(-FLw / 2), rx(FLw / 2), ry(FLh / 2) + D2, f"{FLw:g}", ry(FLh / 2), ry(FLh / 2))
    VM(rx(FLw / 2) + D2, ry(-FLh / 2), ry(FLh / 2), rx(FLw / 2), f"{FLh:g}")
    K.balloon_auto(rx(hp) + 2, ry(-hp) - 2, f"4 x Ø{g['hole_d']:g}", kind="tag", region=K.AUTO.get("region"))
    K.balloon_auto(rx(0) + 3, ry(0) + 3, f"□{ci:g} (tube inside)", kind="tag", region=K.AUTO.get("region"))
    T(flx + FLw * s2 / 2, ry(FLh / 2) + 50, f"t = {FLt:g}, R{rr:g}, welded to leg □{fa}x{fb}x{ft:g}", 8, align="c")


def plate_view(g, flx, fly, s2):
    """v144: viena montavimo plokštė (vaizdas iš sienos): 4 x Ø skylės, kabelio Ø, kojų vamzdžiai ir uždengimas punktyru"""
    P = g["plates"][0]; lw_, ld_, lt_ = g["leg"]; Hd = g["h"]
    w2, h2 = P["w"] / 2, P["h"] / 2
    rx = lambda z: flx + (z + w2) * s2
    ry = lambda y: fly + (y - P["yc"] + h2) * s2
    rect(rx(-w2), ry(P["yc"] - h2), P["w"] * s2, P["h"] * s2, fill=COL_FL, lw=0.1)
    for dz, y_ in P["holes"]:
        circle(rx(dz), ry(y_), P["d"] / 2 * s2, fill=white, lw=0.1)
    circle(rx(P["cable"][0]), ry(P["cable"][1]), P["cable"][2] / 2 * s2, fill=white, lw=0.1)
    for L in g["legs"]:
        rect(rx(-ld_ / 2), ry(L["y"] - lw_ / 2), ld_ * s2, lw_ * s2, lw=0.3, dash=(2, 1.5))
        K.centerline(rx(-w2 - 6), ry(L["y"]), rx(w2 + 6), ry(L["y"]))
    C = g["covers"][0]
    rect(rx(-C["w"] / 2), ry(C["y0"]), C["w"] * s2, (C["y1"] - C["y0"]) * s2, stroke=HexColor("#555555"), lw=0.2, dash=(4, 2))
    K.centerline(rx(0), ry(P["yc"] - h2 - 6), rx(0), ry(P["yc"] + h2 + 6))
    hz = sorted(set(dz for dz, _ in P["holes"]))
    hchain(ry(P["yc"] - h2) - D1, [rx(-w2), rx(hz[0]), rx(hz[-1]), rx(w2)], [ry(P["yc"] - h2)] * 4,
           [f"{w2 + hz[0]:g}", f"{hz[-1] - hz[0]:g}", f"{w2 - hz[-1]:g}"], size=K.F_DIM_FRAME)
    HM(rx(-w2), rx(w2), ry(P["yc"] - h2) - D2, f"{P['w']:g}", ry(P["yc"] - h2), ry(P["yc"] - h2))
    hy = sorted(set(y_ for _, y_ in P["holes"]))
    yy = [P["yc"] - h2] + hy + [P["yc"] + h2]
    vchain(rx(w2) + D1, [ry(v) for v in yy], [rx(w2)] + [rx(hz[-1])] * len(hy) + [rx(w2)],
           [f"{b - a:g}" for a, b in zip(yy, yy[1:])], size=K.F_DIM_FRAME)
    VM(rx(w2) + D2, ry(yy[0]), ry(yy[-1]), rx(w2), f"{P['h']:g}")
    cy_ = P["cable"][1]
    vchain(rx(-w2) - D1, [ry(hy[0]), ry(cy_)], [rx(-ld_ / 2)] * 2, [f"{cy_ - hy[0]:g}"], size=K.F_DIM_FRAME)
    K.balloon_auto(rx(hz[-1]), ry(hy[-1]), f"4 x Ø{P['d']:g}", kind="tag", region=K.AUTO.get("region"))
    K.balloon_auto(rx(0), ry(cy_), f"Ø{P['cable'][2]:g} cable", kind="tag", region=K.AUTO.get("region"))
    K.balloon_auto(rx(ld_ / 2), ry(hy[0] + lw_ / 2), f"leg {prof(lw_, ld_, lt_)} (1B)", kind="tag", region=K.AUTO.get("region"))
    K.balloon_auto(rx(C["w"] / 2), ry(P["yc"]), f"cover 10 ({C['w']:g})", kind="tag", region=K.AUTO.get("region"))
    T(flx + P["w"] * s2 / 2, ry(P["yc"] + h2) + 26, f"t = {P['t']:g}, legs welded; cable inside cover", 8, align="c")


# ===================================================================== 1 LAPAS - GENERAL ASSEMBLY
def face_label(x, y, txt, size=10):
    T(x, y + size * 0.35, txt, size, font="FB", align="c", color=K.GREY)


def _circle_pts(cx, cy, r, n=20):
    return [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def _flange3d(sc, g, P):
    """padas / montavimo plokštė (x plokštuma) su skylėmis ir vamzdžio anga - abi plokštumos + kraštai"""
    Hd = g["h"]; yc = Hd - P["yc"]
    w2, h2, t = P["w"] / 2, P["h"] / 2, P["t"]
    outline = [(-w2, -h2), (w2, -h2), (w2, h2), (-w2, h2)]
    holes = [_circle_pts(dz, -(y_ - P["yc"]), P["d"] / 2) for dz, y_ in P["holes"]]
    if P["cable"]:
        holes.append(_circle_pts(P["cable"][0], -(P["cable"][1] - P["yc"]), P["cable"][2] / 2))
    ci = P["tube"]
    if ci:
        holes.append([(-ci / 2, -ci / 2), (ci / 2, -ci / 2), (ci / 2, ci / 2), (-ci / 2, ci / 2)])
    for x, nx in ((g["xf"], -1), (g["xf"] + t, 1)):
        Q = lambda q: (x, yc + q[1], q[0])
        sc.face([Q(q) for q in outline], (nx, 0, 0), COL_FL, edge=EDGE, holes=[[Q(q) for q in h] for h in holes], tile=False)
    x0, x1 = g["xf"], g["xf"] + t
    for (z0, y0), (z1, y1), n in (((-w2, -h2), (w2, -h2), (0, -1, 0)), ((w2, h2), (-w2, h2), (0, 1, 0)),
                                  ((w2, -h2), (w2, h2), (0, 0, 1)), ((-w2, h2), (-w2, -h2), (0, 0, -1))):
        sc.face([(x0, yc + y0, z0), (x1, yc + y0, z0), (x1, yc + y1, z1), (x0, yc + y1, z1)],
                n, COL_FL, edge=EDGE, tile=False)
    if ci:                                                          # vamzdžio vidus (tamsus) - matosi pro angą
        sc.face([(x1 - 0.5, yc - ci / 2, -ci / 2), (x1 - 0.5, yc + ci / 2, -ci / 2), (x1 - 0.5, yc + ci / 2, ci / 2),
                 (x1 - 0.5, yc - ci / 2, ci / 2)], (1, 0, 0), HexColor("#3A3A3A"), tile=False)


def scene3d(g, yaw, box, title):
    """3D su SIDE A / SIDE B užrašu ant matomo stiklo"""
    import r3d
    Wd, Hd, D, tf, ov = g["w"], g["h"], g["depth"], g["face_thk"], g["face_over"]
    fa, fb, ft = g["frame"]; FLw, FLh, FLt = g["flange"]; ax = g["ax"]; LL = g["leg_len"]
    sc = r3d.Scene(yaw=yaw, pitch=18)
    sc.box((ov, ov, -D / 2), (g["BW"], 0, 0), (0, g["BH"], 0), (0, 0, D), COL_BODY, edge=EDGE)
    WHITE3 = HexColor("#FFFFFF")
    sc.box((0, 0, D / 2), (Wd, 0, 0), (0, Hd, 0), (0, 0, tf), WHITE3, edge=EDGE, amb=0.97)
    sc.box((0, 0, -D / 2 - tf), (Wd, 0, 0), (0, Hd, 0), (0, 0, tf), WHITE3, edge=EDGE, amb=0.97)
    for L in g["legs"]:
        if not g["covers"]:
            sc.box((g["xb"], Hd - L["y"] - L["h"] / 2, -L["d"] / 2), (LL, 0, 0), (0, L["h"], 0), (0, 0, L["d"]), COL_FRAME,
                   edge=EDGE)
    for C in g["covers"]:                                         # v144: kojų uždengimas (korpuso spalva)
        sc.box((g["xb"] + g["cover_gap"] / 2, Hd - C["y1"], -C["w"] / 2), (LL - g["cover_gap"], 0, 0), (0, C["y1"] - C["y0"], 0), (0, 0, C["w"]), COL_BODY, edge=EDGE)
    for P in g["plates"]:
        _flange3d(sc, g, P)
    SCR = HexColor("#D0D0D0")
    hr = 3.5
    for fn, u, z, k in g["scr_holes"]:                            # varžtų galvutės - APVALIOS (diskas ant juostos)
        if fn == "top":
            P = lambda a_, b_, x=ov + u: (x + a_, Hd - ov + 0.6, z + b_); n = (0, 1, 0)
        elif fn == "bottom":
            P = lambda a_, b_, x=Wd - ov - u: (x + a_, ov - 0.6, z + b_); n = (0, -1, 0)
        elif fn == "wall":
            P = lambda a_, b_, y=Hd - ov - u: (Wd - ov + 0.6, y + a_, z + b_); n = (1, 0, 0)
        else:
            P = lambda a_, b_, y=ov + u: (ov - 0.6, y + a_, z + b_); n = (-1, 0, 0)
        sc.face([P(*q) for q in _circle_pts(0, 0, hr, 16)], n, SCR, tile=False, amb=0.9)
    sc.render(box)
    V = sc.V
    import vektorius
    for zf, lab in ((D / 2 + tf, "SIDE A"), (-D / 2 - tf, "SIDE B")):
        n = (0, 0, 1 if zf > 0 else -1)
        if V.rot(*n)[2] > 0:
            if g.get("logo_r"):                                     # logotipas ant matomo stiklo (B - skaitomas iš B)
                def xf(u, v, zf=zf):
                    x = g["logo_x"] + u if zf > 0 else Wd - (g["logo_x"] + u)
                    px_, py_ = V.S(x, Hd - (g["logo_y"] + v), zf)
                    return px_, K.H - py_
                vektorius.draw_rl(K.c, g["logo_r"], 0, 0, 1, K.H, g["logo_col"], xform=xf)
                px, py = V.S(Wd / 2, Hd * 0.04, zf)
                face_label(px, K.H - py - 2, lab, 8)
            else:
                px, py = V.S(Wd / 2, Hd / 2, zf)
                face_label(px, K.H - py, lab, 11)
    view_title(box[0] + box[2] / 2, box[1] + box[3] + 18, title, "ILLUSTRATIVE - NOT TO SCALE")


# ===================================================================== DETAIL B (v218) + EXPLODED VIEW (v218)
COL_SCR = HexColor("#B8B8B8")


def _zigzag(xa, xb, yy):
    n_ = 8
    pts = [(xa + (xb - xa) * k / n_, yy + (1.5 if k % 2 else -1.5)) for k in range(n_ + 1)]
    for p0, p1 in zip(pts, pts[1:]):
        line(p0[0], p0[1], p1[0], p1[1], 0.2)


def detail_b(g):
    """v218 (Rytis 2026-10-14: „pjūvyje pozicijos ... 5S tipo šviesdėžėse viršaus / apačios"): DETAIL B - pjūvis per VISĄ
    gylį (stiklas A | korpusas + rėmas | stiklas B) DVIEJOSE vietose VIRŠUS / APAČIA, atskirtose nutraukimo linija;
    pozicijos (balionai = BOM) stulpeliais šonuose."""
    Hd, D, tf, tb, ov, TOT = g["h"], g["depth"], g["face_thk"], g["band_thk"], g["face_over"], g["TOT"]
    fa, fb, ft = g["frame"]
    pw, pd = g["pvc_edge"]
    zs = D / 2 - pd / 2

    def detail(X_P6, BY0, W_P6, BH):
        ytz = ov + tb + fa + 8 + 6
        zones = [("TOP", 0.0, ytz), ("BOTTOM", Hd - ytz, Hd)]
        gap = 9
        tot_mm = sum(b_ - a_ for _, a_, b_ in zones)
        avail_h = BH - 12 - 26 - 14 - gap
        avail_w = W_P6 - 70
        sc = next((n for n in (1, 1.5, 2, 2.5, 3, 4, 5, 6, 8) if tot_mm * MM / n <= avail_h and TOT * MM / n <= avail_w), 8)
        s3 = MM / sc
        K.header(X_P6, BY0, W_P6, f"DETAIL B - SECTION TOP / BOTTOM  1:{sc:g}")
        rect(X_P6, BY0 + 12, W_P6, BH - 12, lw=0.6)
        ox = X_P6 + (W_P6 - TOT * s3) / 2
        U = lambda u: ox + (u + TOT / 2) * s3                     # u: -TOT/2 = A stiklo išorė, +TOT/2 = B
        ys0 = BY0 + 12 + 26
        maps = []
        for name, a_, b_ in zones:
            maps.append((name, a_, b_, ys0)); ys0 += (b_ - a_) * s3 + gap
        bal = []
        for name, a_, b_, sy in maps:
            Yz = lambda y, a_=a_, sy=sy: sy + (y - a_) * s3
            top_ = name == "TOP"
            K.set_view(True)
            ya_, yb_ = (0.0, b_) if top_ else (a_, Hd)
            for zz in (-TOT / 2, TOT / 2 - tf):                    # stiklai (3 / 5)
                rect(U(zz), Yz(ya_), tf * s3, (yb_ - ya_) * s3, fill=COL_FACE, lw=0.1)
            yband = ov if top_ else Hd - ov - tb
            rect(U(-D / 2), Yz(yband), D * s3, tb * s3, fill=COL_BODY, lw=0.1)         # korpuso juosta (2)
            ypvc = ov + tb if top_ else Hd - ov - tb - pw
            for z0 in (-D / 2, D / 2 - pd):                         # PVC bortelis (4 / 6)
                rect(U(z0), Yz(ypvc), pd * s3, pw * s3, fill=COL_PVC, lw=0.1)
            yfr = ov + tb if top_ else Hd - ov - tb - fa             # rėmo skersinis (1)
            rect(U(-fb / 2), Yz(yfr), fb * s3, fa * s3, fill=COL_FRAME, lw=0.1)
            rect(U(-fb / 2 + ft), Yz(yfr + ft), (fb - 2 * ft) * s3, (fa - 2 * ft) * s3, fill=white, lw=0.1)
            led = top_ and g["led_rows"] > 1 or not top_
            yled = yfr + fa if top_ else yfr - 8
            if led:
                rect(U(-11), Yz(yled), 22 * s3, 8 * s3, fill=COL_LED, lw=0.1)
            for zz in (-zs, zs):                                    # varžtai (8) per juostą į PVC
                if top_:
                    rect(U(zz) - 3.5 * s3, Yz(ov - 1.6), 7 * s3, 1.6 * s3, fill=COL_SCR, lw=0.1)
                    rect(U(zz) - 1.1 * s3, Yz(ov), 2.2 * s3, (tb + pw + 4) * s3, fill=COL_SCR, lw=0.1)
                else:
                    rect(U(zz) - 3.5 * s3, Yz(Hd - ov), 7 * s3, 1.6 * s3, fill=COL_SCR, lw=0.1)
                    rect(U(zz) - 1.1 * s3, Yz(Hd - ov - tb - pw - 4), 2.2 * s3, (tb + pw + 4) * s3, fill=COL_SCR, lw=0.1)
            K.set_view(False)
            for zz in (-zs, zs):
                K.centerline(U(zz), Yz(a_) - 2, U(zz), Yz(b_) + 2)
            _zigzag(U(-TOT / 2) - 4, U(TOT / 2) + 4, Yz(b_ if top_ else a_))
            T(U(-(fb / 2 + D / 2) / 2), Yz((a_ + b_) / 2) + 3, name, 6.5, align="c", color=K.GREY)   # zonos vardas - tuščioje dėžės vidaus vietoje
            if top_:
                bal += [(U(-D / 2 + pd / 2), Yz(ypvc + pw / 2), 4), (U(D / 2 - pd / 4), Yz(ypvc + pw / 2), 6),
                        (U(-D / 2 + 4), Yz(yband + tb / 2), 2), (U(fb / 2 - ft / 2), Yz(yfr + fa / 2), 1),
                        (U(zs) + 3.5 * s3, Yz(ov - 0.8), 8)]
            else:
                ym = a_ + (b_ - a_) * 0.75
                bal += [(U(8), Yz(yled + 4), 7), (U(-TOT / 2 + tf / 2), Yz(ym), 3), (U(TOT / 2 - tf / 2), Yz(ym), 5)]
        hchain(BY0 + 12 + 16, [U(-TOT / 2), U(-D / 2), U(D / 2), U(TOT / 2)], [maps[0][3]] * 4, [f"{tf:g}", f"{D:g}", f"{tf:g}"],
               size=K.F_DIM_FRAME)
        cxm = U(0)
        left = [q for q in bal if q[0] < cxm]; right = [q for q in bal if q[0] >= cxm]
        ytop_, ybot_ = BY0 + 12 + 30, BY0 + BH - 22
        for lst, bx in ((left, U(-TOT / 2) - 22), (right, U(TOT / 2) + 22)):
            lst.sort(key=lambda q: q[1])
            n_ = len(lst)
            for k, (tx_, ty_, lab) in enumerate(lst):
                by = ytop_ + (ybot_ - ytop_) * (k + 0.5) / max(n_, 1)
                K.leader(tx_, ty_, bx, by, lab, 6)
        T(X_P6 + W_P6 / 2, BY0 + BH - 4, f"screws 8 (D3.2) through band into PVC edge; band welded to frame", 6.5,
          align="c", color=K.GREY)

    return detail


def _slab(sc, geo, w0, w1, col, xf, edge=None):
    sc.extrude_xy(geo, w0, w1, col, col, edge=edge, xf=xf)
    for gg in getattr(geo, "geoms", [geo]):
        ext = [xf(x, y, w0) for x, y in list(gg.exterior.coords)[:-1]]
        hol = [[xf(x, y, w0) for x, y in list(r.coords)[:-1]] for r in gg.interiors]
        n = sc._nrm(xf(0, 0, w0), xf(1, 0, w0), xf(0, 1, w0), ref=xf(0, 0, w0 - 1), base=xf(0, 0, w0))
        sc.face(ext, n, col, edge, holes=hol, tile=False)


def exploded(g, box, yaw=-54, pitch=17):
    """v218: sprogstamasis vaizdas išilgai gylio (z): stiklas A (3) - PVC 4 - korpusas (2) + rėmas (1) + LED (7) + kojos /
    padai - PVC 6 - stiklas B (5); varžtai (8) ištraukti į viršų; kojų uždengimas (10) - atitrauktas virš kojų, A / B į šonus."""
    import r3d
    from shapely.geometry import Point
    Wd, Hd, D, tf, tb, ov = g["w"], g["h"], g["depth"], g["face_thk"], g["band_thk"], g["face_over"]
    fa, fb, ft = g["frame"]
    pw, pd = g["pvc_edge"]
    x0, FW, FH, xr = g["x0"], g["FW"], g["FH"], g["xr"]
    M = max(Wd, Hd)
    e_pvc, e_face = 0.5 * M, 0.82 * M
    sc = r3d.Scene(yaw=yaw, pitch=pitch)
    anc = {}
    Y = lambda y: Hd - y                                            # y žemyn -> pasaulio y aukštyn
    # korpuso juosta (2) - 4 kraštinės
    BW, BH = g["BW"], g["BH"]
    for (xa, ya, w_, h_) in ((ov, ov, BW, tb), (ov, Hd - ov - tb, BW, tb), (ov, ov + tb, tb, BH - 2 * tb),
                             (Wd - ov - tb, ov + tb, tb, BH - 2 * tb)):
        sc.box((xa, Y(ya + h_), -D / 2), (w_, 0, 0), (0, h_, 0), (0, 0, D), COL_BODY, edge=EDGE)
    anc[2] = (ov + BW * 0.25, Y(ov), D / 2 * 0.3)
    # rėmas (1) + kojos + padai / plokštė (1A)
    if g["inset"]:
        lw_, ld_, lt_ = g["leg"]
        for y0 in (x0, x0 + FH - fa):
            sc.box((x0, Y(y0 + fa), -fb / 2), (FW, 0, 0), (0, fa, 0), (0, 0, fb), COL_FRAME, edge=EDGE)
        sc.box((x0, Y(x0 + FH - fa), -fb / 2), (fa, 0, 0), (0, FH - 2 * fa, 0), (0, 0, fb), COL_FRAME, edge=EDGE)
        for L in g["legs"]:
            sc.box((g["leg_x0"], Y(L["y"] + lw_ / 2), -ld_ / 2), (g["xf"] - g["leg_x0"], 0, 0), (0, lw_, 0), (0, 0, ld_),
                   COL_FRAME, edge=EDGE)
        L0 = g["legs"][0]
        anc["1B"] = (g["xb"] + (g["xf"] - g["xb"]) * 0.45, Y(L0["y"] - lw_ / 2), ld_ / 4)
        sc.box((g["x_tp"], Y(g["ax"] + lw_ / 2 + g["tp_h"]), -g["trafo_plate"][0] / 2), (g["trafo_plate"][1], 0, 0),
               (0, g["tp_h"], 0), (0, 0, g["trafo_plate"][0]), HexColor("#7A7A7A"), edge=EDGE)
    else:
        for y0 in (x0, x0 + FH - fa):
            sc.box((x0, Y(y0 + fa), -fb / 2), (g["L_h"], 0, 0), (0, fa, 0), (0, 0, fb), COL_FRAME, edge=EDGE)
        for xx in (x0, xr - fa):
            sc.box((xx, Y(x0 + FH - fa), -fb / 2), (fa, 0, 0), (0, FH - 2 * fa, 0), (0, 0, fb), COL_FRAME, edge=EDGE)
    for P in g["plates"]:
        _flange3d(sc, g, P)
    P0 = g["plates"][0]
    anc["1A"] = (g["xf"] + P0["t"], Y(P0["yc"] + P0["h"] / 2 - 10), P0["w"] / 2 * 0.5)
    anc[1] = (x0 + FW * 0.72, Y(x0 + FH - fa), fb / 2 - 3)            # apatinio skersinio viršus (matomas)
    # LED (7)
    led_x = [g["led_a"] + g["led_step"] * (i + 0.5) for i in range(g["led_n_row"])]
    rows = [x0 + FH - fa - 8] + ([x0 + fa] if g["led_rows"] > 1 else [])
    for yr in rows:
        for lx in led_x:
            sc.box((lx - 11, Y(yr + 8), -11), (22, 0, 0), (0, 8, 0), (0, 0, 22), COL_LED, edge=EDGE)
    anc[7] = (led_x[-1], Y(rows[0]), 11)
    # stiklai (3 / 5) + PVC borteliai (4 / 6)
    iw, ih = Wd - 2 * (ov + tb), Hd - 2 * (ov + tb)
    for sgn in (1, -1):
        zf = sgn * (D / 2 + e_face)
        za = min(zf, zf + sgn * tf)
        sc.box((0, 0, za), (Wd, 0, 0), (0, Hd, 0), (0, 0, tf), COL_FACE, edge=EDGE, amb=0.97)
        zp = sgn * (D / 2 + e_pvc)
        zpa = min(zp, zp - sgn * pd)
        xi, yi = ov + tb, ov + tb
        for (xa, ya, w_, h_) in ((xi, yi, iw, pw), (xi, yi + ih - pw, iw, pw), (xi, yi + pw, pw, ih - 2 * pw),
                                 (xi + iw - pw, yi + pw, pw, ih - 2 * pw)):
            sc.box((xa, Y(ya + h_), zpa), (w_, 0, 0), (0, h_, 0), (0, 0, pd), COL_PVC, edge=EDGE)
        anc[3 if sgn > 0 else 5] = (Wd * 0.15, Hd * 0.85, zf + sgn * tf)
        anc[4 if sgn > 0 else 6] = (xi + iw * 0.5, Y(yi + pw / 2), zp)
    # varžtai (8) - viršutinė kraštinė, ištraukti į viršų
    up = 0.1 * M
    tops = [(u, z) for fn, u, z, k in g["scr_holes"] if fn == "top"]
    for u, z in tops:
        xx = ov + u
        sh = Point(xx, z).buffer(1.1, 3); hd = Point(xx, z).buffer(3.5, 3)
        sc.extrude_xy(sh, Hd + up, Hd + up + 12, COL_SCR, COL_SCR, xf=lambda a, b, c: (a, c, b))
        _slab(sc, hd, Hd + up + 12, Hd + up + 13.6, COL_SCR, lambda a, b, c: (a, c, b))
    if tops:
        u, z = max(tops, key=lambda q: q[1])
        anc[8] = (ov + u, Hd + up + 13.6, z)
    # kojų uždengimas (10) - A / B, atitraukta virš kojų (kaip P10_lightbox v215)
    if g["covers"]:
        C = g["covers"][0]; ct = C["thk"]; hw = C["w"] / 2; Lc = C["L"]; xc0 = g["xb"] + C["gap"] / 2
        lift = Hd + 0.12 * M - Y(C["y1"])                          # visas uždengimas VIRŠ dėžės (ne priglaustas)
        yb_, yt_ = Y(C["y1"]) + lift, Y(C["y0"]) + lift
        for sgn in (1, -1):
            dz = sgn * 0.12 * M
            zo = lambda z, sgn=sgn, dz=dz: sgn * z + dz
            za, zb = sorted((zo(hw - ct), zo(hw)))
            sc.box((xc0, yb_, za), (Lc, 0, 0), (0, yt_ - yb_, 0), (0, 0, zb - za), COL_BODY, edge=EDGE)
            za, zb = sorted((zo(0), zo(hw)))
            for yy in (yb_, yt_ - ct):
                sc.box((xc0, yy, za), (Lc, 0, 0), (0, ct, 0), (0, 0, zb - za), COL_BODY, edge=EDGE)
            za, zb = sorted((zo(hw - C["rib"]), zo(hw)))
            for xx in (xc0, xc0 + Lc - ct):
                sc.box((xx, yb_ + ct, za), (ct, 0, 0), (0, yt_ - yb_ - 2 * ct, 0), (0, 0, zb - za), COL_BODY, edge=EDGE)
            anc["10" + ("A" if sgn > 0 else "B")] = (xc0 + Lc / 2, yt_ - (yt_ - yb_) * 0.3, zo(hw))
    sc.render(box)
    V = sc.V
    return {k: (V.S(*p)[0], K.H - V.S(*p)[1]) for k, p in anc.items()}


def exploded_view(g, box):
    A = exploded(g, box)
    ex0, ey0, ew, eh = box
    reg = (ex0 - 20, ey0 - 10, ex0 + ew + 20, ey0 + eh + 10)
    for key, lab in (("1", 1), (1, 1), ("1A", "1A"), ("1B", "1B"), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8),
                     ("10A", 10), ("10B", 10)):
        if key in A:
            K.balloon_auto(A[key][0], A[key][1], lab, region=reg)
    view_title(ex0 + ew / 2, ey0 + eh + 18, "ASSEMBLY - EXPLODED VIEW",          # pavadinimas apačioje - kaip 3D vaizdų
               "not to scale; face A + PVC 4 - body 2 + frame 1 + LED 7 - PVC 6 + face B")


def sheet1(g, out):
    Wd, Hd, D, tf, tb, ov = g["w"], g["h"], g["depth"], g["face_thk"], g["band_thk"], g["face_over"]
    fa, fb, ft = g["frame"]
    LL = g["leg_len"]; FLw, FLh, FLt = g["flange"]; ax = g["ax"]; TOT = g["TOT"]
    pw, pd = g["pvc_edge"]
    K.set_band(10 if g.get("logo_r") else 9)
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
        if g.get("logo_r"):                                         # logotipas - abiejose pusėse skaitomas normaliai
            import vektorius
            vektorius.draw_rl(K.c, g["logo_r"], xl + g["logo_x"] * s, Yv(g["logo_y"]), s, K.H, g["logo_col"])
            lx0, lx1 = xl + g["logo_x"] * s, xl + (g["logo_x"] + g["logo_w"]) * s
            hchain(Yv(0) - D1, [xl, lx0, lx1, xr_], [Yv(0), Yv(g["logo_y"]), Yv(g["logo_y"]), Yv(0)],
                   [f"{g['logo_x']:g}", f"{g['logo_w']:g}", f"{g['logo_x']:g}"], size=K.F_DIM_FRAME)
            xo2 = xl - D1 if not mirror else xr_ + D1
            ly0, ly1 = g["logo_y"], g["logo_y"] + g["logo_h"]
            vchain(xo2, [Yv(0), Yv(ly0), Yv(ly1), Yv(Hd)], [xl if not mirror else xr_] + [lx0 if not mirror else lx1] * 2 +
                   [xl if not mirror else xr_], [f"{ly0:.0f}", f"{g['logo_h']:.0f}", f"{Hd - ly1:.0f}"], size=K.F_DIM_FRAME)
        a_, b_ = sorted((X(g["xb"]), X(g["xf"])))
        for L in g["legs"]:
            if not g["covers"]:
                rect(a_, Yv(L["y"] - L["h"] / 2), LL * s, L["h"] * s, fill=COL_FRAME, lw=0.1)
        cg = g["cover_gap"]                                         # v145 / v212: uždengimas 5 mm trumpesnis - po 2.5 iš abiejų galų
        c_a, c_b = sorted((X(g["xb"] + cg / 2), X(g["xf"] - cg / 2)))
        for C in g["covers"]:                                       # v144: kojų uždengimas, kojos po juo - punktyru
            rect(c_a, Yv(C["y0"]), (LL - cg) * s, (C["y1"] - C["y0"]) * s, fill=COL_BODY, lw=0.1)
            for L in g["legs"]:
                rect(a_, Yv(L["y"] - L["h"] / 2), LL * s, L["h"] * s, stroke=HexColor("#D8D8D8"), lw=0.3, dash=(2, 1.5))
        for P in g["plates"]:
            a2, b2 = sorted((X(g["xf"]), X(g["PROJ"])))
            rect(a2, Yv(P["yc"] - P["h"] / 2), P["t"] * s, P["h"] * s, fill=COL_FL, lw=0.1)
        for L in g["legs"]:
            K.centerline(X(Wd - 20), Yv(L["y"]), X(g["PROJ"] + 8), Yv(L["y"]))
        xs_ = sorted([X(0), X(g["xb"]), X(g["xf"]), X(g["PROJ"])])
        labs = [f"{g['xb']:g}", f"{LL:g}", f"{g['plates'][0]['t']:g}"]
        hchain(Yv(Hd) + D1, xs_, [Yv(Hd)] * 4, labs[::-1] if mirror else labs, size=K.F_DIM_FRAME)
        lg = g.get("logo_r") is not None                           # v145: grandinė arčiausiai, gabaritas už jos
        HM(xl, xr_, Yv(0) - (D2 if lg else D1), f"{Wd:g}", Yv(0), Yv(0))
        HM(xs_[0], xs_[-1], Yv(Hd) + D2, f"{g['PROJ']:g}", Yv(Hd), Yv(Hd))
        xo = (xl - (D2 if lg else D1)) if not mirror else (xr_ + (D2 if lg else D1))
        VM(xo, Yv(0), Yv(Hd), xl if not mirror else xr_, f"{Hd:g}")
        return X

    # ---------------------------------------------------------------- SIDE A | VIEW FROM WALL | SIDE B
    fxA = K.IX0 + 70
    XA = front(fxA, False, "SIDE A")
    K.balloon_side([(XA(Wd * 0.05), Yv(Hd * 0.1), 3)], XA(0) - 22, "left", up=True)
    P0 = g["plates"][0]
    if g["covers"]:
        C0 = g["covers"][0]
        K.balloon_side([(XA(g["xb"] + g["cover_gap"] / 2 + (LL - g["cover_gap"]) * 0.5), Yv(Hd / 2), 10),
                        (XA(g["xf"] + P0["t"] / 2), Yv(C0["y0"] + 10), "1A")], XA(g["PROJ"]) + 16, "right", up=False)
        vchain(XA(g["PROJ"]) + D1, [Yv(0), Yv(ax), Yv(Hd - ax), Yv(Hd)], [XA(Wd)] + [XA(g["PROJ"])] * 2 + [XA(Wd)],
               [f"{ax:g}", f"{Hd - 2 * ax:g} (legs)", f"{ax:g}"], size=K.F_DIM_FRAME)
    else:
        K.balloon_side([(XA(g["xb"] + LL * 0.6), Yv(ax), 1), (XA(g["xf"] + FLt / 2), Yv(ax + FLh / 2 - 8), "1A")],
                       XA(g["PROJ"]) + 16, "right", up=False)
        vchain(XA(g["PROJ"]) + 16, [Yv(0), Yv(ax), Yv(Hd - ax), Yv(Hd)], [XA(Wd)] + [XA(g["PROJ"])] * 2 + [XA(Wd)],
               [f"{ax:g}", f"{Hd - 2 * ax:g}", f"{ax:g}"], size=K.F_DIM_FRAME)
    xcut = Wd * 0.1
    K.cut_plane(XA(xcut), Yv(0), Yv(Hd), "A", look="right")
    view_title(XA(g["PROJ"] / 2), top - 84, "FRONT VIEW - SIDE A", sl)
    # vaizdas iš sienos (gręžimo schema)
    sxc = XA(g["PROJ"]) + 128
    Xs = lambda z: sxc + z * s
    rect(Xs(-D / 2), Yv(ov), D * s, g["BH"] * s, fill=COL_BODY, lw=0.1)
    for zz in (-TOT / 2, TOT / 2 - tf):
        rect(Xs(zz), Yv(0), tf * s, Hd * s, fill=COL_FACE, lw=0.1)
    for (yy, zz, kind) in g["scr_wall"]:                          # varžtų (8) galvutės Ø7 korpuse (sienos pusė)
        circle(Xs(zz), Yv(yy), 3.5 * s, fill=HexColor("#B8B8B8"), lw=0.1)
    hz = sorted(set(round(z_, 2) for P in g["plates"] for z_, _ in P["holes"]))
    hyv = sorted(set(round(y_, 2) for P in g["plates"] for _, y_ in P["holes"]))
    pl_top = min(P["yc"] - P["h"] / 2 for P in g["plates"]); pl_bot = max(P["yc"] + P["h"] / 2 for P in g["plates"])
    PW2 = max(P["w"] for P in g["plates"]) / 2
    ytop = min(0, pl_top)
    for P in g["plates"]:
        rect(Xs(-P["w"] / 2), Yv(P["yc"] - P["h"] / 2), P["w"] * s, P["h"] * s, fill=COL_FL, lw=0.1)
        for dz, y_ in P["holes"]:
            circle(Xs(dz), Yv(y_), P["d"] / 2 * s, fill=white, lw=0.1)
        if P["tube"]:
            ci = P["tube"]
            rect(Xs(-ci / 2), Yv(P["yc"] - ci / 2), ci * s, ci * s, fill=white, lw=0.1)
        if P["cable"]:
            circle(Xs(P["cable"][0]), Yv(P["cable"][1]), P["cable"][2] / 2 * s, fill=white, lw=0.1)
    for C in g["covers"]:                                         # uždengimas už plokštės - punktyru
        rect(Xs(-C["w"] / 2), Yv(C["y0"]), C["w"] * s, (C["y1"] - C["y0"]) * s, lw=0.2, dash=(2, 1.5))
    face_label(Xs(-TOT / 2) + 2, Yv(ytop) - 56, "A", 9); face_label(Xs(TOT / 2) - 2, Yv(ytop) - 56, "B", 9)
    ybot = max(Hd, pl_bot)
    K.centerline(Xs(0), Yv(ytop - 8), Xs(0), Yv(ybot + 8))
    # v145: VIENA linija - VIENA prasmė; grandinė arčiausiai, gabaritas už jos
    zz_ = sorted(set([-PW2, PW2] + hz))                           # viršuje: skylės plokštėje + plokštės plotis
    pl_e = Yv(pl_top) if PW2 * 2 >= TOT else Yv(ytop)
    hchain(Yv(ytop) - D1, [Xs(z_) for z_ in zz_], [pl_e if z_ in (-PW2, PW2) else Yv(hyv[0]) for z_ in zz_],
           [f"{b - a:g}" for a, b in zip(zz_, zz_[1:])], size=K.F_DIM_FRAME)
    HM(Xs(-PW2), Xs(PW2), Yv(ytop) - D2 - 10, f"{2 * PW2:g}", pl_e, pl_e)
    HM(Xs(-TOT / 2), Xs(TOT / 2), Yv(ybot) + D1, f"{TOT:g}", Yv(Hd), Yv(Hd))     # apačioje: dėžės storis
    ex_ = max(PW2 * 2, TOT) / 2
    yr_ = sorted(set([pl_top, pl_bot] + hyv))                     # dešinėje: skylės nuo plokštės kraštų + plokštės aukštis
    vchain(Xs(ex_) + D1, [Yv(v) for v in yr_], [Xs(PW2) if v in (pl_top, pl_bot) else Xs(hz[-1]) for v in yr_],
           [f"{b - a:g}" for a, b in zip(yr_, yr_[1:])], size=K.F_DIM_FRAME)
    VM(Xs(ex_) + D2, Yv(pl_top), Yv(pl_bot), Xs(PW2), f"{pl_bot - pl_top:g}")
    yl_ = sorted(set([0, Hd, pl_top, pl_bot]))                   # kairėje: plokštė nuo stiklo kraštų + stiklo aukštis
    vchain(Xs(-ex_) - D1, [Yv(v) for v in yl_], [Xs(-TOT / 2) if v in (0, Hd) else Xs(-PW2) for v in yl_],
           [f"{b - a:g}" for a, b in zip(yl_, yl_[1:])], size=K.F_DIM_FRAME)
    VM(Xs(-ex_) - D2, Yv(0), Yv(Hd), Xs(-TOT / 2), f"{Hd:g}")
    yw = g["scr_wall"][len(g["scr_wall"]) // 2]
    nh = sum(len(P["holes"]) for P in g["plates"])
    P0 = g["plates"][0]
    cab = ((Xs(P0["cable"][0]), Yv(P0["cable"][1]), f"cable Ø{P0['cable'][2]:g}") if P0["cable"]
           else (Xs(0), Yv(Hd - ax), f"cable □{fa - 2 * ft:g}"))
    K.balloon_side([(Xs(yw[1]), Yv(yw[0]), "screw 8 (D3.2)"), (Xs(hz[-1]), Yv(hyv[-1]), f"{nh} x Ø{P0['d']:g}"), cab],
                   Xs(ex_) + 36, "right", up=True, tags=True)
    T(Xs(0), Yv(Hd) + 38, "= WALL DRILLING", 8, align="c", color=K.GREY)
    view_title(Xs(0), top - 84, "VIEW FROM WALL", sl)
    # SIDE B (veidrodinis - kojos kairėje)
    fxB = Xs(TOT / 2) + 128
    XB = front(fxB, True, "SIDE B")
    K.balloon_side([(XB(Wd * 0.05), Yv(Hd * 0.1), 5)], XB(0) + 22, "right", up=True)
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
    zs8 = D / 2 - pd / 2
    for zz in (-zs8, zs8):
        for top_ in (True, False):
            yh = ov - 1.6 if top_ else Hd - ov
            ysh = ov if top_ else Hd - ov - tb - pw - 4
            rect(Xa(zz) - 3.5 * s5, ya(yh), 7 * s5, 1.6 * s5, fill=HexColor("#B8B8B8"), lw=0.1)
            rect(Xa(zz) - 1.1 * s5, ya(ysh), 2.2 * s5, (tb + pw + 4) * s5, fill=HexColor("#B8B8B8"), lw=0.1)
    yl = Hd - ov - tb - fa
    rect(Xa(-11), ya(yl - 8), 22 * s5, 8 * s5, fill=COL_LED, lw=0.1)
    if g["led_rows"] > 1:
        rect(Xa(-11), ya(ov + tb + fa), 22 * s5, 8 * s5, fill=COL_LED, lw=0.1)
    for dz in (-1, 1):
        line(Xa(0), ya(yl - 8), Xa(dz * D / 2), ya(yl - 8 - D / 2 / math.tan(math.radians(32.5))), 0.2,
             HexColor("#C9A000"), dash=(2, 1.5))
    face_label(Xa(-TOT / 2) + 2, ya(0) - 10, "A", 9); face_label(Xa(TOT / 2) - 2, ya(0) - 10, "B", 9)
    hchain(ya(Hd) + D1, [Xa(-TOT / 2), Xa(-D / 2), Xa(-fb / 2), Xa(fb / 2), Xa(D / 2), Xa(TOT / 2)], [ya(Hd)] * 6,
           [f"{tf:g}", f"{(D - fb) / 2:g}", f"{fb:g}", f"{(D - fb) / 2:g}", f"{tf:g}"], size=K.F_DIM_FRAME)
    HM(Xa(-TOT / 2), Xa(TOT / 2), ya(Hd) + D2 + 10, f"{TOT:g}", ya(Hd), ya(Hd))
    VM(Xa(-TOT / 2) - 24, ya(0), ya(Hd), Xa(-TOT / 2), f"{Hd:g}")
    K.balloon_side([(Xa(zs8) + 3.5 * s5, ya(ov - 0.8), 8), (Xa(fb / 2), ya(ov + tb + fa * 0.7), 1),
                    (Xa(TOT / 2), ya(Hd * 0.35), 5), (Xa(11), ya(yl - 4), 7),
                    (Xa(D / 2 - 2), ya(Hd - ov - tb - pw / 2), 6)], Xa(TOT / 2) + 4, "right", up=True)
    K.balloon_side([(Xa(-TOT / 2), ya(Hd * 0.35), 3), (Xa(-D / 2 + 2), ya(Hd - ov - tb - pw / 2), 4),
                    (Xa(-D / 2 + 26), ya(Hd - ov - tb / 2), 2)], Xa(-TOT / 2) - 24, "left", up=True)

    circle(Xa(TOT / 2 - 10), ya(Hd - 12), 16, lw=0.3, dash=(3, 1.5))
    T(Xa(TOT / 2) + 14, ya(Hd - 30), "B", 10, font="FB")
    view_title(Xa(0), top - 84, "SECTION A-A", "1:5")
    # ---------------------------------------------------------------- 3D: A ir B pusės
    y3 = Yv(Hd) + 80
    h3 = K.VIEW_BOT - y3 - 34
    # v218: 3D A | 3D B | ASSEMBLY - EXPLODED VIEW (kaip P10_lightbox), dešinėje TOP VIEW
    tx_l = K.IX1 - g["PROJ"] * MM / g["scale_ga"] - 90 - 50       # TOP VIEW kairys kraštas - tarpas
    w3 = 190
    scene3d(g, -35, (K.IX0 + 40, y3, w3, h3), "3D VIEW - SIDE A")
    scene3d(g, 145, (K.IX0 + 40 + w3 + 40, y3, w3, h3), "3D VIEW - SIDE B")
    exx = K.IX0 + 40 + 2 * (w3 + 40) + 10
    exploded_view(g, (exx, y3, tx_l - exx, h3))
    # ---------------------------------------------------------------- TOP VIEW (varžtai 8)
    tx0 = K.IX1 - g["PROJ"] * s - 90
    tyc = K.VIEW_BOT - 70
    Xt = lambda x: tx0 + x * s
    Zt = lambda z: tyc - z * s                                    # A pusė (z+) apačioje? -> A apačioje: z+ žemyn
    Zt = lambda z: tyc + z * s
    rect(Xt(ov), Zt(-D / 2), g["BW"] * s, D * s, fill=COL_BODY, lw=0.1)
    for zz in (-D / 2 - tf, D / 2):
        rect(Xt(0), Zt(zz), Wd * s, tf * s, fill=COL_FACE, lw=0.1)
    if g["covers"]:
        cw = g["covers"][0]["w"]
        rect(Xt(g["xb"]), Zt(-g["leg"][1] / 2), LL * s, g["leg"][1] * s, fill=COL_FRAME, lw=0.1)
        rect(Xt(g["xb"] + g["cover_gap"] / 2), Zt(-cw / 2), (LL - g["cover_gap"]) * s, cw * s, fill=COL_BODY, lw=0.1)
    else:
        rect(Xt(g["xb"]), Zt(-fb / 2), LL * s, fb * s, fill=COL_FRAME, lw=0.1)
    P0 = g["plates"][0]
    rect(Xt(g["xf"]), Zt(-P0["w"] / 2), P0["t"] * s, P0["w"] * s, fill=COL_FL, lw=0.1)
    tops = [(u, z) for fn, u, z, k in g["scr_holes"] if fn == "top"]
    for u, z in tops:
        circle(Xt(ov + u), Zt(z), 3.5 * s, fill=HexColor("#B8B8B8"), lw=0.1)
    face_label(Xt(0) - 8, Zt(D / 2 + tf / 2), "A", 8); face_label(Xt(0) - 8, Zt(-D / 2 - tf / 2), "B", 8)
    us = sorted(set(round(u, 2) for u, z in tops))
    hchain(Zt(D / 2 + tf) + 18, [Xt(ov)] + [Xt(ov + u) for u in us] + [Xt(Wd - ov)], [Zt(zs8)] * (len(us) + 2),
           [f"{us[0]:.1f}"] + [f"{b - a:.1f}" for a, b in zip(us, us[1:])] + [f"{g['BW'] - us[-1]:.1f}"], size=K.F_DIM_FRAME)
    vchain(Xt(g["PROJ"]) + 14, [Zt(-D / 2), Zt(-zs8), Zt(zs8), Zt(D / 2)], [Xt(Wd - ov)] * 4,
           [f"{D / 2 - zs8:g}", f"{2 * zs8:g}", f"{D / 2 - zs8:g}"], size=K.F_DIM_FRAME)
    K.balloon_side([(Xt(ov + us[0]) - 3.5 * s, Zt(zs8), 8), (Xt(ov + 6), Zt(0), 2)], Xt(0) - 16, "left", up=False)
    T(Xt(Wd / 2), Zt(D / 2 + tf) + 44, f"{len(g['scr_holes'])} screws: {2 * len(us)} per side of band, into PVC edge", 8,
      align="c", color=K.GREY)
    view_title(Xt(g["PROJ"] / 2), Zt(-P0["w"] / 2) - 40, "TOP VIEW", sl)
    K.set_view(False)

    md = [["Product", "double-sided lightbox, projecting"],
          ["Size (glass)", f"{Wd:g} x {Hd:g} x {TOT:g} mm"],
          ["Sides", (f"A + B: logo {g['logo_w']:g} x {g['logo_h']:.0f} (9)" if g.get("logo_r") else "A + B (graphics per side)")],
          ["From wall", f"{g['PROJ']:g} mm (body {LL + FLt:g})"],
          ["Fixing", (f"1 plate {P0['w']:g}x{P0['h']:g}, 4 x Ø{P0['d']:g}, {g['plate_pitch']:g} x {Hd - 2 * ax:g} {g['anchors']}"
                      if g["inset"] else
                      f"2 flanges, 8 x Ø{g['hole_d']:g}, {g['hole_pitch']:g} x {g['hole_pitch']:g} {g['anchors']}").strip()],
          ["LED / PSU", f"{g['led_n']} x {g['led_name']}, {g['psu'][0].replace('-5Y', '')}"],
          ["Cable", g["cable"] or ("inside leg cover -> plate Ø" + f"{g['cable_hole']:g}" if g["inset"]
                                   else "through bottom leg + flange:")],
          ["Qty", f"{g['qty']} pcs."],
          ["Weight (calc.)", f"≈ {g['kg']:.1f} kg / pcs, excl. PSU"]]
    band(g, "1 / 2", " - GA", md, bom_rows(g), detail_b(g), f"1:{g['scale_ga']:g} / 1:5")
    K.save(out)


def frame_inset(g, X, Yv, s, led_x, yrow):
    """v144: rėmas su ŽEMESNĖMIS kojomis - skersiniai + priekinis statmuo, kojos □40x40x4 po skersiniais (galas 50°),
    trafo plokštelė tarp kojų, viena montavimo plokštė"""
    fa, fb, ft = g["frame"]; x0, FW, FH, xr = g["x0"], g["FW"], g["FH"], g["xr"]
    lw_, ld_, lt_ = g["leg"]; lx0, dxc = g["leg_x0"], g["leg_dxc"]
    P = g["plates"][0]; Hd = g["h"]
    for y0 in (x0, x0 + FH - fa):
        rect(X(x0), Yv(y0), FW * s, fa * s, fill=COL_FRAME, lw=0.1)
    rect(X(x0), Yv(x0 + fa), fa * s, g["L_v"] * s, fill=COL_FRAME, lw=0.1)
    for L in g["legs"]:
        top_ = L["y"] < Hd / 2
        ya, yb = L["y"] - lw_ / 2, L["y"] + lw_ / 2                 # ya - prie skersinio (top) / yb - prie skersinio (bottom)
        if top_:
            pts = [(lx0, ya), (g["xf"], ya), (g["xf"], yb), (lx0 + dxc, yb)]
        else:
            pts = [(lx0 + dxc, ya), (g["xf"], ya), (g["xf"], yb), (lx0, yb)]
        poly([(X(a), Yv(b)) for a, b in pts], fill=COL_FRAME, lw=0.1)
        poly([(X(a), Yv(b)) for a, b in pts], lw=0.25)
    rect(X(g["x_tp"]), Yv(g["ax"] + lw_ / 2), g["trafo_plate"][1] * s, g["tp_h"] * s, fill=HexColor("#7A7A7A"), lw=0.1)
    psu_h = min(150, g["tp_h"] - 40)
    rect(X(g["x_tp"] + g["trafo_plate"][1]), Yv(Hd / 2 - psu_h / 2), 30 * s, psu_h * s, fill=HexColor("#5A5A5A"), lw=0.1)
    T(X(g["x_tp"] + 16), Yv(Hd / 2) + 3, "PSU", 6, align="c", color=white)
    rect(X(g["xf"]), Yv(P["yc"] - P["h"] / 2), P["t"] * s, P["h"] * s, fill=COL_FL, lw=0.1)
    for yr in yrow:
        up = yr > x0 + FH / 2
        for lx in led_x:
            rect(X(lx - 11), Yv(yr - 8 if up else yr), 22 * s, 8 * s, fill=COL_LED, lw=0.1)
        yw = yr - 4 if up else yr + 4
        line(X(led_x[0]), Yv(yw), X(led_x[-1]), Yv(yw), 0.2, HexColor("#C00000"))
        line(X(led_x[-1]), Yv(yw), X(g["x_tp"]), Yv(yw), 0.2, HexColor("#C00000"))
    # matmenys (v145: viena linija - viena prasmė; grandinė arčiausiai, gabaritas už jos; tarp LED matmenų nėra)
    hchain(Yv(x0) - D1, [X(x0), X(lx0), X(xr)], [Yv(x0)] * 3, [f"{lx0 - x0:g}", f"{xr - lx0:g} (leg in)"], size=K.F_DIM_FRAME)
    HM(X(x0), X(xr), Yv(x0) - D2, f"{FW:g}", Yv(x0), Yv(x0))
    yb_ = Yv(max(x0 + FH, P["yc"] + P["h"] / 2))
    hchain(yb_ + D1, [X(xr), X(g["xf"]), X(g["PROJ"])], [Yv(x0 + FH), Yv(P["yc"] + P["h"] / 2), Yv(P["yc"] + P["h"] / 2)],
           [f"{g['xf'] - xr:g}", f"{P['t']:g}"], size=K.F_DIM_FRAME)
    HM(X(lx0), X(g["xf"]), yb_ + D2, f"{g['L_leg']:.0f} (leg 1B)", Yv(g["h"] - g["ax"] + lw_ / 2), Yv(P["yc"] + P["h"] / 2))
    vchain(X(x0) - D1, [Yv(x0), Yv(x0 + fa), Yv(x0 + FH - fa), Yv(x0 + FH)], [X(x0)] * 4,
           [f"{fa:g}", f"{g['L_v']:g}", f"{fa:g}"], size=K.F_DIM_FRAME)
    VM(X(x0) - D2, Yv(x0), Yv(x0 + FH), X(x0), f"{FH:g}")
    ylg = [g["ax"] - lw_ / 2, g["ax"] + lw_ / 2, Hd - g["ax"] - lw_ / 2, Hd - g["ax"] + lw_ / 2]
    vchain(X(g["PROJ"]) + D1, [Yv(v) for v in ylg], [X(g["xf"])] * 4, [f"{lw_:g}", f"{ylg[2] - ylg[1]:g}", f"{lw_:g}"],
           size=K.F_DIM_FRAME)
    VM(X(g["PROJ"]) + D2, Yv(P["yc"] - P["h"] / 2), Yv(P["yc"] + P["h"] / 2), X(g["PROJ"]), f"{P['h']:g} (plate)")
    T(X(lx0 + dxc / 2) + 8, Yv(g["ax"] + lw_ / 2) + 10, f"{g['leg_chamfer']:g}°", 8)
    K.balloon_side([(X(x0 + FW * 0.3), Yv(x0 + fa / 2), "1.1"), (X(x0 + FW * 0.3), Yv(x0 + FH - fa / 2), "1.2"),
                    (X(x0 + fa / 2), Yv(x0 + FH * 0.35), "1.3"), (X(g["xf"] - 10), Yv(g["ax"]), "1B"),
                    (X(g["xf"] + P["t"]), Yv(P["yc"] - P["h"] / 2 + 10), "1A"), (X(g["x_tp"]), Yv(Hd / 2 + 60), "1C"),
                    (X(led_x[-1] + 11), Yv(yrow[0] - 4), 7)], X(g["PROJ"]) + 24, "right", up=True, r=7)


def end_view(g, cx, Yv, s):
    """v219 (Rytis 2026-10-14): rėmo VAIZDAS IŠ GALO (iš sienos) - tvirtinimo plokštės / padai su matmenimis, rėmo nariai,
    kojos (punktyru po plokšte), korpusas punktyru; tame pačiame mastelyje ir aukštyje kaip FRAME vaizdas."""
    D, ov, tb = g["depth"], g["face_over"], g["band_thk"]
    fa, fb, ft = g["frame"]
    x0, FH = g["x0"], g["FH"]
    Zs = lambda z: cx + z * s
    rect(Zs(-D / 2), Yv(ov), D * s, g["BH"] * s, stroke=HexColor("#9A9A9A"), lw=0.1, dash=(3, 2))          # korpusas
    for y0 in (x0, x0 + FH - fa):                                   # skersinių galai
        rect(Zs(-fb / 2), Yv(y0), fb * s, fa * s, fill=COL_FRAME, lw=0.1)
        rect(Zs(-fb / 2 + ft), Yv(y0 + ft), (fb - 2 * ft) * s, (fa - 2 * ft) * s, fill=white, lw=0.1)
    if not g["inset"]:                                              # galinis statmuo
        rect(Zs(-fb / 2), Yv(x0 + fa), fb * s, g["L_v"] * s, fill=COL_FRAME, lw=0.1)
    for P in g["plates"]:
        y0p = P["yc"] - P["h"] / 2
        rect(Zs(-P["w"] / 2), Yv(y0p), P["w"] * s, P["h"] * s, fill=COL_FL, lw=0.1)
        for dz, y_ in P["holes"]:
            circle(Zs(dz), Yv(y_), P["d"] / 2 * s, fill=white, lw=0.1)
        if P["tube"]:
            ci = P["tube"]
            rect(Zs(-ci / 2), Yv(P["yc"] - ci / 2), ci * s, ci * s, fill=white, lw=0.1)
        if P["cable"]:
            circle(Zs(P["cable"][0]), Yv(P["cable"][1]), P["cable"][2] / 2 * s, fill=white, lw=0.1)
    for L in g["legs"]:                                             # kojos po plokšte - punktyru
        rect(Zs(-L["d"] / 2), Yv(L["y"] - L["h"] / 2), L["d"] * s, L["h"] * s, stroke=HexColor("#555555"), lw=0.25, dash=(2, 1.5))
        K.centerline(Zs(-max(P["w"] for P in g["plates"]) / 2 - 6), Yv(L["y"]), Zs(max(P["w"] for P in g["plates"]) / 2 + 6), Yv(L["y"]))
    PW2 = max(P["w"] for P in g["plates"]) / 2
    pl_top = min(P["yc"] - P["h"] / 2 for P in g["plates"]); pl_bot = max(P["yc"] + P["h"] / 2 for P in g["plates"])
    ytop, ybot = min(ov, pl_top), max(g["h"] - ov, pl_bot)
    K.centerline(Zs(0), Yv(ytop) - 8, Zs(0), Yv(ybot) + 8)
    hz = sorted(set(round(z_, 2) for P in g["plates"] for z_, _ in P["holes"]))
    hyv = sorted(set(round(y_, 2) for P in g["plates"] for _, y_ in P["holes"]))
    # viršuje: skylės z + plokštės plotis; apačioje: korpuso gylis
    zz_ = sorted(set([-PW2, PW2] + hz))
    hchain(Yv(ytop) - D1, [Zs(z_) for z_ in zz_], [Yv(pl_top) if z_ in (-PW2, PW2) else Yv(hyv[0]) for z_ in zz_],
           [f"{b - a:g}" for a, b in zip(zz_, zz_[1:])], size=K.F_DIM_FRAME)
    HM(Zs(-PW2), Zs(PW2), Yv(ytop) - D2, f"{2 * PW2:g}", Yv(pl_top), Yv(pl_top))
    ex_ = max(PW2, D / 2)
    HM(Zs(-D / 2), Zs(D / 2), Yv(ybot) + D1, f"{D:g} (body)", Yv(g["h"] - ov), Yv(g["h"] - ov))
    # dešinėje: skylės y nuo plokštės kraštų + plokštės aukštis (kiekvienai plokštei)
    yr_ = sorted(set([P["yc"] + sg * P["h"] / 2 for P in g["plates"] for sg in (-1, 1)] + hyv))
    edges = {round(P["yc"] + sg * P["h"] / 2, 2) for P in g["plates"] for sg in (-1, 1)}
    vchain(Zs(ex_) + D1, [Yv(v) for v in yr_], [Zs(PW2) if round(v, 2) in edges else Zs(hz[-1]) for v in yr_],
           [f"{b - a:g}" for a, b in zip(yr_, yr_[1:])], size=K.F_DIM_FRAME)
    VM(Zs(ex_) + D2, Yv(pl_top), Yv(pl_bot), Zs(PW2), f"{pl_bot - pl_top:g}")
    # kairėje: plokštės nuo rėmo išorės + rėmo aukštis
    yl_ = sorted(set([x0, x0 + FH, pl_top, pl_bot]))
    vchain(Zs(-ex_) - D1, [Yv(v) for v in yl_], [Zs(-fb / 2) if v in (x0, x0 + FH) else Zs(-PW2) for v in yl_],
           [f"{b - a:g}" for a, b in zip(yl_, yl_[1:])], size=K.F_DIM_FRAME)
    VM(Zs(-ex_) - D2, Yv(x0), Yv(x0 + FH), Zs(-fb / 2), f"{FH:g} (frame)")
    P0 = g["plates"][0]
    nh = sum(len(P["holes"]) for P in g["plates"])
    tags = [(Zs(hz[-1]), Yv(hyv[-1]), f"{nh} x Ø{P0['d']:g}"), (Zs(PW2), Yv(P0["yc"] - P0["h"] / 2 + 6), "1A")]
    if P0["cable"]:
        tags.append((Zs(P0["cable"][0]), Yv(P0["cable"][1]), f"cable Ø{P0['cable'][2]:g}"))
    elif P0["tube"]:
        tags.append((Zs(0), Yv(g["h"] - g["ax"]), f"cable □{P0['tube']:g}"))
    K.balloon_side(tags, Zs(ex_) + D2 + 22, "right", up=True, tags=True)
    if g["inset"]:
        note = f"plate t = {P0['t']:g}, welded to legs 1B {prof(*g['leg'])} (dashed)"
    else:
        note = f"flanges t = {P0['t']:g}, R{g['flange_r']:g}, welded to legs {prof(fa, fb, ft)}"
    T(Zs(0), Yv(ybot) + D1 + 30, note, 8, align="c", color=K.GREY)
    return ex_


# ===================================================================== 2 LAPAS - FRAME + LED
def sheet2(g, out):
    global _CAD
    _CAD = True
    try:
        _sheet2(g, out)
    finally:
        _CAD = False


def _sheet2(g, out):
    D, tb, ov, tf = g["depth"], g["band_thk"], g["face_over"], g["face_thk"]
    fa, fb, ft = g["frame"]
    LL = g["leg_len"]; FLw, FLh, FLt = g["flange"]
    K.set_band(9)
    K.init(out + ".tmp", "sheet2")
    K.frame(); K.set_view(True)
    # v219 (Rytis 2026-10-14): SECTION C-C išimtas; rėmas DIDESNIS (mastelis pagal vietą) + VAIZDAS IŠ GALO su plokštėmis
    x0 = g["x0"]
    top = K.IY0 + 112
    pl_t = min([x0] + [P["yc"] - P["h"] / 2 for P in g["plates"]]); pl_b = max([x0 + g["FH"]] + [P["yc"] + P["h"] / 2 for P in g["plates"]])
    PWm = max(P["w"] for P in g["plates"])
    gw_mm = (g["PROJ"] - x0) + max(PWm, D)                          # geometrija horizontaliai (rėmas + galas)
    fixed = 50 + 50 + 40 + 50 + 100                                 # matmenys / balionai / tarpai (kairė, rėmo dešinė, tarpas, galo kairė / dešinė)
    hav = (K.VIEW_BOT - 96 - 66 - 8) - top - 50                    # iki BODY BAND pavadinimo (apačioje matmenys / pastaba 50)
    wav = K.IX1 - K.IX0 - 20
    SC = (2, 2.5, 3, 4, 5, 6, 8, 10)
    nsc = next((n for n in SC if gw_mm * MM / n + fixed <= wav and (pl_b - pl_t) * MM / n <= hav), 10)
    nb, layB = 10, False                                            # BODY BAND mastelis
    # B išdėstymas: rėmas + galas per VISĄ aukštį kairėje, BODY BAND (smulkesnis) apačioje dešinėje
    Lband = 2 * (g["BW"] + g["BH"])
    havB = K.VIEW_BOT - top - (D2 + 22)
    for n in SC:
        if n >= nsc or (pl_b - pl_t) * MM / n > havB:
            continue
        blk = gw_mm * MM / n + fixed
        nb_ = next((m for m in (10, 12, 15, 20) if blk + 40 + Lband * MM / m + 90 <= wav), None)
        if nb_:
            nsc, nb, layB = n, nb_, True
            break
    g["scale_fr"], g["scale_band"] = nsc, nb
    print(f"  sheet2: hav {hav:.0f}/{havB:.0f}, h {(pl_b - pl_t):.0f} mm, w {gw_mm:.0f} mm -> 1:{nsc:g}, band 1:{nb:g}")
    s = MM / nsc
    wblk = (wav - (Lband * MM / nb + 90 + 40)) if layB else wav
    fx = K.IX0 + 10 + (wblk - (gw_mm * MM / nsc + fixed)) / 2 + 50
    X = lambda x: fx + (x - x0) * s
    Yv = lambda y: top + (y - x0) * s
    FW, FH = g["FW"], g["FH"]
    xr = x0 + FW
    rect(X(ov), Yv(ov), g["BW"] * s, g["BH"] * s, stroke=HexColor("#9A9A9A"), lw=0.1, dash=(3, 2))   # korpusas
    yrow = [x0 + FH - fa] + ([x0 + fa] if g["led_rows"] > 1 else [])
    led_x = [g["led_a"] + g["led_step"] * (i + 0.5) for i in range(g["led_n_row"])]
    if g["inset"]:
        frame_inset(g, X, Yv, s, led_x, yrow)
    else:
        for y0 in (x0, x0 + FH - fa):
            rect(X(x0), Yv(y0), g["L_h"] * s, fa * s, fill=COL_FRAME, lw=0.1)
            rect(X(g["xf"]), Yv(y0 + fa / 2 - FLh / 2), FLt * s, FLh * s, fill=COL_FL, lw=0.1)
        for xx in (x0, xr - fa):
            rect(X(xx), Yv(x0 + fa), fa * s, g["L_v"] * s, fill=COL_FRAME, lw=0.1)
        for yr in yrow:
            up = yr > x0 + FH / 2
            for lx in led_x:
                rect(X(lx - 11), Yv(yr - 8 if up else yr), 22 * s, 8 * s, fill=COL_LED, lw=0.1)
            yw = yr - 4 if up else yr + 4
            line(X(led_x[0]), Yv(yw), X(led_x[-1]), Yv(yw), 0.2, HexColor("#C00000"))
            line(X(led_x[-1]), Yv(yw), X(g["xb"] + 30), Yv(yw), 0.2, HexColor("#C00000"))
        # matmenys
        hchain(Yv(x0) - D1, [X(x0), X(g["xb"]), X(g["xf"]), X(g["xf"] + FLt)], [Yv(x0)] * 2 + [Yv(x0 + fa / 2 - FLh / 2)] * 2,
               [f"{g['xb'] - x0:g}", f"{LL:g}", f"{FLt:g}"], size=K.F_DIM_FRAME)
        hdim(X(x0), X(g["xf"]), Yv(x0) - D2 - 20, f"{g['L_h']:g}  (□{fa}x{fb}x{ft:g}, 2 pcs.)", e1=Yv(x0), e2=Yv(x0),
             size=K.F_DIM_FRAME)
        ylb = x0 + FH
        vchain(X(x0) - D1, [Yv(x0), Yv(x0 + fa), Yv(x0 + FH - fa), Yv(x0 + FH)], [X(x0)] * 4,
               [f"{fa:g}", f"{g['L_v']:g}", f"{fa:g}"], size=K.F_DIM_FRAME)
        HM(X(x0), X(xr), Yv(x0) - D2, f"{FW:g}", Yv(x0), Yv(x0))
        VM(X(x0) - D2, Yv(x0), Yv(x0 + FH), X(x0), f"{FH:g}")
        vchain(X(g["xf"] + FLt) + 24, [Yv(x0 + fa / 2), Yv(x0 + FH - fa / 2)], [X(g["xf"])] * 2, [f"{FH - fa:g}"],
               size=K.F_DIM_FRAME)
        K.balloon_side([(X(g["xb"] + 30), Yv(x0 + fa), "1.1"), (X(g["xf"] + FLt), Yv(x0 + fa / 2 + 28), "1A"),
                        (X(xr), Yv(x0 + FH * 0.3), "1.3")], X(g["xf"] + FLt) + 24, "right", up=False, r=7)
        K.balloon_side([(X(xr - fa), Yv(yrow[0] - 4), 7), (X(g["xb"] + 30), Yv(x0 + FH - fa), "1.2")],
                       X(g["xf"] + FLt) + 24, "right", up=True, r=7)

    view_title(X(x0 + (g["PROJ"] - x0) / 2), top - 96, "FRAME (1) + LED (7)",
               f"1:{nsc:g}  (from side A, welded; LED on member centre - light to both faces)")
    # ---------------------------------------------------------------- VIEW FROM WALL (galas) - plokštės su matmenimis
    cxe = X(g["PROJ"]) + 64 + 40 + 50 + max(PWm, D) / 2 * s
    end_view(g, cxe, Yv, s)
    view_title(cxe, top - 96, "FRAME - VIEW FROM WALL (END)", f"1:{nsc:g}  (mounting plates 1A)")
    # ---------------------------------------------------------------- BODY BAND (2) - išklotinė 1:10 su D3.2 skylėmis
    s10 = MM / g["scale_band"]
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
        T(BX(u0 + L / 2), BY(D / 2) + 3, fn.upper() + (" (legs)" if fn == "wall" else ""), 8, align="c", color=white)
        u0 += L
    for fn, u, z, k in g["scr_holes"]:
        circle(BX(starts[fn] + u), BY(D / 2 + z), 1.0, fill=white, lw=0.1)
    L0 = g["legs"][0]
    cl, cd = L0["h"] + 2, L0["d"] + 2                             # kojos anga (vamzdis + 1 mm / pusė)
    for uu in (g["ax"] - ov, g["BH"] - (g["ax"] - ov)):
        rect(BX(starts["wall"] + uu - cl / 2), BY(D / 2 - cd / 2), cl * s10, cd * s10, fill=white, lw=0.1)
    # matmenys: lenkimai, skylių eilės, vienos kraštinės skylių žingsnis
    hchain(BY(0) - D1, [BX(starts[fn]) for fn, _ in faces] + [BX(Ltot)], [BY(0)] * 5, [f"{L:g}" for _, L in faces],
           size=K.F_DIM_FRAME)
    HM(BX(0), BX(Ltot), BY(0) - D2, f"{Ltot:g}  (band {tb:g} mm, 3 x 90° fold + seam)", BY(0), BY(0))
    zs = D / 2 - g["pvc_edge"][1] / 2
    vchain(BX(Ltot) + 16, [BY(0), BY(D / 2 - zs), BY(D / 2), BY(D / 2 + zs), BY(D)], [BX(Ltot)] * 5,
           [f"{D / 2 - zs:g}", f"{zs:g}", f"{zs:g}", f"{D / 2 - zs:g}"], size=K.F_DIM_FRAME)
    n_ = g["scr_n_face"]; st_ = g["BW"] / n_
    hu = [st_ * (i + 0.5) for i in range(n_)]
    hchain(BY(D) + 14, [BX(0)] + [BX(u) for u in hu] + [BX(g["BW"])], [BY(D / 2 + zs)] * (n_ + 2),
           [f"{hu[0]:.1f}"] + [f"{st_:.1f}"] * (n_ - 1) + [f"{g['BW'] - hu[-1]:.1f}"], size=K.F_DIM_FRAME)
    T(BX(0), BY(D) + 62, f"holes: same on each side ({n_} + {n_} per side, rows {D / 2 - zs:g} from edges) ; band welded to frame (no holes on centre line)", 8, color=K.GREY)
    uu = g["ax"] - ov
    hchain(BY(D) + 32, [BX(starts["wall"]), BX(starts["wall"] + uu), BX(starts["wall"] + g["BH"] - uu), BX(starts["wall"] + g["BH"])],
           [BY(D / 2)] * 4, [f"{uu:g}", f"{g['BH'] - 2 * uu:g}", f"{uu:g}"], size=K.F_DIM_FRAME)
    K.balloon_auto(BX(starts["wall"] + uu), BY(D / 2 + cd / 2), f"{cl:g}x{cd:g} leg hole (2)", kind="tag", region=K.AUTO.get("region"), size=8)
    K.balloon_auto(BX(starts["bottom"] + hu[0]), BY(D / 2 + zs), f"D3.2 - {g['n_scr']} holes (screws 8, into PVC 4 / 6)",
                   kind="tag", size=8)
    T(BX(0) - 4, BY(0) + 6, "A", 8, font="FB", align="r", color=K.GREY)
    T(BX(0) - 4, BY(D) + 2, "B", 8, font="FB", align="r", color=K.GREY)
    view_title(BX(Ltot / 2), by0 - 66, "BODY BAND (2) - FLAT PATTERN", f"1:{g['scale_band']:g}")
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
            ["PSU", f"{g['psu'][0].replace('-5Y', '')} ({g['psu'][1]} W), place:"],
            ["Supply", "not in Alt Reklama price list - check:"]], title="LED (7)", lab_w=64)

    ci = fa - 2 * ft
    frame_cut = [["1.1", f"Top member + leg □{fa}x{fb}x{ft:g}", "Alu EN AW-6060", f"{g['frame_finish']} leg", f"1 x {g['L_h']:g} mm"],
                 ["1.2", f"Bottom member + leg □{fa}x{fb}x{ft:g}", "Alu EN AW-6060", f"{g['frame_finish']} leg", f"1 x {g['L_h']:g} mm (cable)"],
                 ["1.3", f"Vertical □{fa}x{fb}x{ft:g}", "Alu EN AW-6060", "white", f"2 x {g['L_v']:g} mm"],
                 ["1A", f"Flange {FLw:g}x{FLh:g}x{FLt:g} R{g['flange_r']:g}", "Alu", g["frame_finish"],
                  f"2 pcs., 4 x Ø{g['hole_d']:g} + □{ci:g}"],
                 ["", "Frame profile total", "", "", f"{g['prof_len']:g} mm (+ cut allowance)"],
                 [7, f"LED Kaisen {g['led_name']}", f"{g['du']['W']:g} W, 12 V", "6500 K", f"{g['led_n']} pcs."],
                 ["7A", "PSU", g["psu"][0], "IP67", "1 pc."],
                 ["7B", "Cable 2 x 0.75 (LED -> PSU)", "", "", "length:"],
                 ["", "", "", "", ""]]
    if g["inset"]:
        lw_, ld_, lt_ = g["leg"]; P = g["plates"][0]
        frame_cut = [["1.1", f"Top member {prof(fa, fb, ft)}", "Alu EN AW-6060", "white", f"1 x {FW:g} mm"],
                     ["1.2", f"Bottom member {prof(fa, fb, ft)}", "Alu EN AW-6060", "white", f"1 x {FW:g} mm"],
                     ["1.3", f"Front vertical {prof(fa, fb, ft)}", "Alu EN AW-6060", "white", f"1 x {g['L_v']:g} mm"],
                     ["1B", f"Leg {prof(lw_, ld_, lt_)}, end {g['leg_chamfer']:g}°", "Alu EN AW-6060", g["frame_finish"],
                      f"2 x {g['L_leg']:.0f} mm"],
                     ["1A", f"Mounting plate {P['w']:g}x{P['h']:g}x{P['t']:g}", "Alu", g["frame_finish"],
                      f"1 pc., 4 x Ø{P['d']:g} + Ø{g['cable_hole']:g}"],
                     ["1C", f"Trafo plate {g['trafo_plate'][1]:g} mm", "Alu", "-", f"{g['tp_h']:g} x {g['trafo_plate'][0]:g} mm"],
                     [7, f"LED Kaisen {g['led_name']}", f"{g['du']['W']:g} W, 12 V", "6500 K", f"{g['led_n']} pcs."],
                     ["7A", "PSU (on 1C)", g["psu"][0], "IP67", "1 pc."],
                     ["7B", "Cable 2 x 0.75 (LED -> PSU)", "", "", "length:"]]
    md = [["Frame outer", f"{FW:g} x {FH:g} mm"],
          ["Profile", f"{prof(fa, fb, ft)} Alu, centre of depth"],
          ["Legs", (f"{prof(*g['leg'])} under members, in {g['leg_in']:g}, out {g['xf'] - g['xb']:g}" if g["inset"]
                    else f"top + bottom members, +{g['xf'] - g['xb']:g} out of body")],
          ["Leg axes", f"{g['h'] - 2 * g['ax']:g} mm (from glass edge {g['ax']:g})"],
          ["Joints", "welded (TIG), ground"],
          ["Body", f"band {g['BW']:g} x {g['BH']:g}, welded to frame"],
          ["Cable", ("PSU on 1C -> inside cover -> plate Ø" + f"{g['cable_hole']:g}") if g["inset"]
           else "bottom leg tube -> flange □ hole"],
          ["Finish", f"legs + plates {g['frame_finish']}; inside white"],
          ["Qty", f"{g['qty']} set"]]
    band(g, "2 / 2", " - FRAME + LED", md, frame_cut, detail, f"1:{g['scale_fr']:g} / 1:{g['scale_band']:g}")
    K.save(out)


def main(spec_path, out):
    S = dict(DEF); S.update(json.load(open(spec_path, encoding="utf-8")))
    global COL_BODY, COL_FRAME, COL_FL                                 # v141: spalvos pagal RAL (pvz. 7024)
    if str(S.get("body_finish", "")).upper().startswith("RAL") and "_" not in S["body_finish"]:
        COL_BODY = HexColor(K.ralhex(S["body_finish"]))
    if str(S.get("frame_finish", "")).upper().startswith("RAL") and "_" not in S["frame_finish"]:
        COL_FRAME = COL_FL = HexColor(K.ralhex(S["frame_finish"]))
    K.F_DIM_FRAME = K.F_DIM_MAIN                                    # v145 (Rytis): visi matmenys vienodo dydžio
    g = geom(S)
    p1, p2 = out + ".1.pdf", out + ".2.pdf"
    for fn, pp in ((sheet1, p1), (sheet2, p2)):                    # v139: 2 praėjimai - automatinis žymėjimas
        K.auto_begin("collect"); K.AUTO["region"] = None
        fn(g, pp)
        pl = K.auto_place(pp)
        K.auto_begin("draw", pl); K.AUTO["region"] = None
        fn(g, pp)
        K.auto_begin(None)
    import pymupdf as fitz
    d = fitz.open()
    for p in (p1, p2):
        d.insert_pdf(fitz.open(p))
    d.save(out, garbage=3, deflate=True); d.close()
    K.pdf_fix_fonts(out)
    for p in (p1, p2, p1 + ".tmp", p2 + ".tmp"):
        os.path.exists(p) and os.remove(p)
    if g["covers"]:                                                 # v217: kojų uždengimo išklotinė (Bendrinės taisyklės 19)
        import ezdxf
        doc = ezdxf.new("R2010"); doc.units = ezdxf.units.MM
        for ln, col in (("CUT", 7), ("BEND_UP_90", 1), ("HOLES_D3.2", 3), ("TEXT", 8)):
            doc.layers.add(ln, color=col)
        KU.write_flat(doc.modelspace(), g["covers"][0], 0)
        doc.saveas(os.path.splitext(out)[0] + "_gamyba.dxf")
    print("OK", out, f"svoris {g['kg']:.2f} kg, rėmas {g['FW']:g}x{g['FH']:g}, LED {g['led_n']} x {g['led_name']} "
          f"({g['led_W']:.1f} W, {g['psu'][0]}), netelpa: {K.OVERFLOW}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
