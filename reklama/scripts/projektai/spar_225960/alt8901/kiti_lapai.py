"""ALT8901 v316 (Rytis 2026-10-16: „blankas naudojamas senas ... visi pataisymai daromi pagal dabartines taisykles"):
SPAR 225960 lapai 6 (portalas) ir 10-14 (spauda, plėvelės, dekoras, spauda ant sandblast) DABARTINIU blanku ir taisyklėmis.
Duomenys (BOM, MAIN DATA, užrašai, matmenys, grafika) - iš PATVIRTINTO lapo (`Drawing_SPAR_order_225960_patvirtintas.pdf`),
išdėstymas - layout_engine (TAISYKLĖ 33), juostos blokai - K.section_block (TAISYKLĖ 5), lentelės - K.bom_table / main_data
(vienetai, dešimtainis kablelis - lapas_core). Portalo geometrija - kaip patvirtintame (seno flat_sheets.portal duomenys).
python3 kiti_lapai.py [6 10 11 12 13 14]"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", ".."))
import lapas_core as K  # noqa: E402
import layout_engine as LE  # noqa: E402
import pymupdf as fitz  # noqa: E402
from lapas_core import T, rect, poly, line, hdim, hchain, vchain, leader, view_title, MM  # noqa: E402
from reportlab.lib.colors import HexColor, white, black  # noqa: E402
from shapely.geometry import box as sbox  # noqa: E402

SRC = os.path.join(HERE, "Drawing_SPAR_order_225960_patvirtintas.pdf")
ALT, DATE, CLIENT, PRJ = "ALT8901_10.16_RS", "2026-10-16", "BrandFactory", "SPAR order 225960"
SK = os.path.join(HERE, "sk")
D = fitz.open(SRC)
W_S, W_MD, W_TB = 214, 172, 272


# ------------------------------------------------------------------ bendra
def start(name, rows):
    K.OVERFLOW.clear()
    K.set_band(rows)
    out = os.path.join(SK, f"{name}.pdf")
    K.init(out + ".tmp", name)
    K.frame()
    return out


def band(sec_title, sec_fn, bom, md, title, sheet, scale_txt, qty="1 pcs."):
    BY0 = K.BAND_Y; BH = K.IY1 - BY0
    X_TB = K.IX1 - W_TB; X_MD = X_TB - W_MD; X_BOM = K.IX0 + W_S; W_BOM = X_MD - X_BOM
    K.section_block(K.IX0, BY0, W_S, BH, sec_title, sec_fn)
    K.bom_table(X_BOM, BY0, W_BOM, BH, bom, title="BILL OF MATERIALS  (per 1 pcs.)")
    K.main_data(X_MD, BY0, W_MD, BH, md, lab_w=62)
    K.title_block(X_TB, W_TB, {"client": CLIENT, "title": f"{PRJ} - {title}", "drawing_no": PRJ, "date": DATE, "rev": "A",
                               "order_no": ALT, "sheet": f"{sheet} / 18", "qty": qty}, scale_txt)


def finish(out, rep):
    LE.report(os.path.basename(out), *rep)
    K.save(out)
    K.pdf_fix_fonts(out)
    os.path.exists(out + ".tmp") and os.remove(out + ".tmp")
    print("OK", out, "netelpa:", K.OVERFLOW)


def material_fn(items):
    """MATERIAL blokas: [(pavadinimas, hex | None, aprašas)] - turinys centruojamas section_block"""
    def fn(x, y, w, h):
        n = len(items); bh = 40 * n - 10
        yy = y + (h - bh) / 2
        for lab, col, txt in items:
            rect(x + 14, yy, 46, 30, fill=HexColor(col) if col else white, lw=0.4)
            T(x + 68, yy + 12, lab, 9, font="FB", fit=w - 80, fit_min=8)
            T(x + 68, yy + 24, txt, 8, color=K.GREY, fit=w - 80, fit_min=8)
            yy += 40
    return fn


def image_of(pno, xref, name):
    fn = os.path.join(SK, name)
    pix = fitz.Pixmap(D, xref)
    if pix.n - pix.alpha >= 4:
        pix = fitz.Pixmap(fitz.csRGB, pix)
    pix.save(fn)
    return fn


def vec_items(pno, clip, pred):
    """lapo vektoriai srityje -> [(sub pt, fill, color)]"""
    out = []
    for d in D[pno].get_drawings():
        if fitz.Rect(clip).contains(d["rect"]) and pred(d):
            out.append(d)
    return out


def draw_vec(ds, clip, x, y, w, h, fill=None, stroke=black):
    cl = fitz.Rect(clip)
    kx, ky = w / cl.width, h / cl.height
    for d in ds:
        sub = K.drawing_to_subpaths(d, lambda q: ((q[0] - cl.x0) * kx + x, (q[1] - cl.y0) * ky + y))
        K.draw_shape(sub, lambda a, b: (a, K.Y(b)), fill=fill if fill is not None else HexColor("#%02X%02X%02X" % tuple(
            int(255 * c) for c in d["fill"][:3])), stroke=stroke)


# ------------------------------------------------------------------ grafikos lapai (10-14)
def nest(objs, kind, film="", roll_mm=None, separate=False, qty_txt=None):
    """v316 (TAISYKLĖ v304): plėvelės m² - rulono nesting (plevele.plan), ne grynasis plotas -> BOM tekstas"""
    import plevele as PL
    r = PL.plan(objs, film, kind=kind, roll_mm=roll_mm, separate=separate, keep_lines=False)
    K.FEAT.add("nest")
    print("  nest:", r["text"], *[n for n in r["notes"] if n.startswith("!")])
    t = f"{r['roll']:.0f} mm x {r['length_mm'] / 1000:.2f} m = {r['m2']:.2f} m²".replace(".", ",")
    return (f"{qty_txt} / " if qty_txt else "") + t, r



def graphics_sheet(name, sheet, title, items, notes, mat, bom, md):
    """items: [{w, h, title, sub, draw(x, y, s)}] - viena eilė, bendras mastelis (LE.pick_scale), stulpeliai LE.distribute"""
    out = start(name, max(8, len(bom) + 6))
    K.FEAT.add("nest")                                            # m² - nest() (plevele.plan) prieš K.init
    A_L, A_T, A_B = 46, 46, 62                                   # matmenys kairėje / viršuje, pavadinimas apačioje
    NOTE_W = max([K.pdfmetrics.stringWidth(t_, "FB" if i == 0 else "F", 9 if i == 0 else 8) for i, t_ in enumerate(notes)] or [0])
    aw = (K.IX1 - K.IX0) - len(items) * A_L - (NOTE_W + 40 if notes else 0) - 60 * len(items)
    ah = K.VIEW_BOT - K.IY0 - A_T - A_B
    SC = LE.pick_scale((sum(it["w"] for it in items), max(it["h"] for it in items)), (aw, ah))
    s = MM / SC
    cols = [max(A_L + it["w"] * s, LE.title_w(it["title"], f"SCALE 1:{SC}  |  {it['sub']}" if it["sub"] else f"SCALE 1:{SC}") + 10)
            for it in items] + ([NOTE_W] if notes else [])
    CX, G = LE.distribute(K.IX0, K.IX1, cols, margin=(0.5, 1.0))
    fill = {}
    for it, cx, cw in zip(items, CX, cols):
        fw, fh = it["w"] * s, it["h"] * s
        x = cx + A_L + (cw - A_L - fw) / 2
        y = K.IY0 + A_T + (ah - fh) / 2
        K.set_view(True)                                         # objektų linijos - hairline (patikra 1)
        it["draw"](x, y, s)
        K.set_view(False)
        if it.get("extra"):
            it["extra"](x, y, s)
        hdim(x, x + fw, y - 22, it.get("wl", f"{it['w']:g}"), y, y, size=K.F_DIM_MAIN)
        vchain(x - 22, [y, y + fh], [x, x], [it.get("hl", f"{it['h']:g}")], size=K.F_DIM_MAIN)
        view_title(x + fw / 2, y + fh + 30, it["title"], f"SCALE 1:{SC}" + (f"  |  {it['sub']}" if it["sub"] else ""))
        fill[it["title"]] = (fh, ah)
    if notes:
        nx = CX[-1]; ny = K.IY0 + A_T + ah / 2 - 8 * len(notes)
        for i, t_ in enumerate(notes):
            T(nx, ny + 14 * i, t_, 9 if i == 0 else 8, font="FB" if i == 0 else "F")
    band("MATERIAL", material_fn(mat), bom, md, title, sheet, f"1:{SC}", qty=md[0][1])
    finish(out, (SC, G, fill))


def s10():
    img = image_of(9, 81, "print_s10.png")
    JY = 1150                                                     # sandūra (patvirtintas lapas: 2 dalys, 10 mm užlaida)
    t1, _ = nest([sbox(0, 0, 3000, JY + 10), sbox(0, 0, 3000, 2300 - JY)], "print", film="digital print", separate=True)
    t2, _ = nest([sbox(0, 0, 3000, JY + 10), sbox(0, 0, 3000, 2300 - JY)], "print", film="laminate", separate=True)

    def extra(x, y, s):
        K.set_view(True)
        line(x, y + JY * s, x + 3000 * s, y + JY * s, 0.5, K.CABLE, dash=([6, 2, 1.5, 2], 0))   # sandūra - matoma ant tamsios spaudos
        K.set_view(False)
        vchain(x + 3000 * s + 22, [y, y + JY * s, y + 2300 * s], [x + 3000 * s] * 3, [f"{JY}", f"{2300 - JY}"], size=K.F_DIM_MAIN)
    items = [{"w": 3000, "h": 2300, "title": "FRONT VIEW", "sub": "client preview, print from original file", "extra": extra,
              "draw": lambda x, y, s: (rect(x, y, 3000 * s, 2300 * s, fill=HexColor("#2B2B2B"), lw=0.4),
                                       K.c.drawImage(img, x, K.Y(y + 2300 * s), 3000 * s, 2300 * s))}]
    graphics_sheet("s10_print", 10, "Print 3000 x 2300 mm (separate files for printing)", items,
                   ["Print only - no back plate.", "Original print forwarded - separate files for printing.", "Material / laminate:",
                    "The vinyl graphic consists of two parts.", "Provide a 10 mm overlap at the joint."],
                   [("PRINT", "#3A3A3A", "original file - forwarded"), ("LAMINATE gloss", None, "")],
                   [[1, "Print, 2 parts, 10 mm overlap", "", "", "per production"], ["", "Laminate", "", "-", t2]],   # v328: spauda tik nurodoma
                   [["Quantity", "1 pcs."], ["Size", "3000 x 2300 mm"], ["Parts", "2 (joint 1150, overlap 10 mm)"], ["Product", "print only"],
                    ["Artwork", "original file (forwarded)"], ["Material", ""], ["Finish", ""], ["Weight (calc.)", "-"]])


def foil(name, sheet, title, W, H, hexc, matname, mat_sub, bom, md):
    items = [{"w": W, "h": H, "title": "FOIL - FLAT", "sub": "", "draw": lambda x, y, s: rect(x, y, W * s, H * s, fill=HexColor(hexc), lw=0.4)}]
    graphics_sheet(name, sheet, title, items, [], [(matname, hexc, mat_sub)], bom, md)


def s11():
    # 1220 mm pločio lakštas netelpa į 1190 spalvotos plėvelės rulono darbinį plotį -> Avery 777 rulonas 1230 mm (KLAUSIMAS Rytis)
    t, _ = nest([sbox(0, 0, 5000, 1220)], "color", film="Avery 777-002CF", roll_mm=1230)
    foil("s11_foil_PMS185", 11, "Foil PMS 185 - Avery 777-002CF or equivalent", 5000, 1220, "#E4002B", "FOIL PMS 185",
         "Avery 777-002CF or equiv.", [[1, "Foil PMS 185, 5000 x 1220 mm", "ORACAL 551 032 gloss", "foil", t]],
         [["Quantity", "1 pcs."], ["Size", "5000 x 1220 mm"], ["Material", "ORACAL 551 032 gloss"], ["Weight (calc.)", "-"]])


def s12():
    t, _ = nest([sbox(0, 0, 23000, 1220)], "white", film="sandblast")
    foil("s12_sandblast_foil", 12, "Sandblast foil 23000 x 1220 mm", 23000, 1220, "#C4C5C9", "SANDBLAST FOIL", "sandblast foil",
         [[1, "Sandblast foil, 23000 x 1220 mm", "sandblast foil Poli-Etch 5054", "sandblast", t]],
         [["Quantity", "1 pcs."], ["Size", "23000 x 1220 mm"], ["Material", "sandblast foil"], ["Weight (calc.)", "-"]])


def s13():
    clip = (350, 275, 792, 358)
    ds = vec_items(12, clip, lambda d: d.get("fill") is not None and d.get("color") is not None)
    r = fitz.Rect(ds[0]["rect"])
    for d in ds[1:]:
        r |= d["rect"]
    items = [{"w": 769, "h": 131.3, "title": "FRONT VIEW", "sub": "white, outline = cut line", "hl": "131,3",
              "draw": lambda x, y, s: draw_vec(ds, r, x, y, 769 * s, 131.3 * s, fill=white, stroke=black)}]
    t, _ = nest([sbox(0, 0, 769, 131.3)] * 7, "white", film="ORACAL 551 101 white", separate=True, qty_txt="7 pcs.")
    graphics_sheet("s13_white_decor", 13, "White decor SPAR logo 769 x 131,3 mm", items, [],
                   [("WHITE DECOR", "#FFFFFF", "material")], [[1, "White decor SPAR logo", "ORACAL 551 101 gloss", "white", t]],
                   [["Quantity", "7 pcs."], ["Size", "769 x 131,3 mm"], ["Colour", "white"], ["Material", ""], ["Weight (calc.)", "-"]])


def s14():
    imgB = image_of(13, 106, "sandprint_B.png")
    ra = fitz.Rect(224.5, 162.4, 488.2, 404.8)
    dsA = vec_items(13, ra, lambda d: d.get("fill") is not None and min(d["fill"][:3]) > 0.97)

    def dA(x, y, s):
        rect(x, y, 930 * s, 855 * s, fill=HexColor("#C4C5C9"), lw=0.4)
        draw_vec(dsA, ra, x, y, 930 * s, 855 * s, fill=white, stroke=None)

    def dB(x, y, s):
        rect(x, y, 930 * s, 855 * s, fill=HexColor("#C4C5C9"), lw=0.4)
        K.c.drawImage(imgB, x, K.Y(y + 855 * s), 930 * s, 855 * s)
    def note(extra_txt):
        def fn(x, y, s):
            T(x + 465 * s, y + 855 * s + 66, "White print on sandblast foil", 8, align="c", auto_red=False)
            for i, t_ in enumerate(extra_txt):
                T(x + 465 * s, y + 855 * s + 82 + 12 * i, t_, 8, font="FB", align="c", auto_red=False)
        return fn
    items = [{"w": 930, "h": 855, "title": "DESIGN A - 5 pcs.", "sub": "client preview", "draw": dA, "extra": note([])},
             {"w": 930, "h": 855, "title": "DESIGN B - 5 pcs.", "sub": "client preview", "draw": dB,
              "extra": note(["A vector file is required."])}]
    tA, _ = nest([sbox(0, 0, 930, 855)] * 5, "print", film="sandblast print", separate=True, qty_txt="5 pcs.")
    tB, _ = nest([sbox(0, 0, 930, 855)] * 5, "print", film="sandblast print", separate=True, qty_txt="5 pcs.")
    graphics_sheet("s14_print_on_sandblast", 14, "White print on sandblast foil 930 x 855 mm", items, [],
                   [("SANDBLAST FOIL", "#C4C5C9", "white print")],
                   [[1, "White print on sandblast foil, design A", "sandblast foil Poli-Etch 5054", "white print", tA],
                    [2, "White print on sandblast foil, design B", "sandblast foil Poli-Etch 5054", "white print", tB]],
                   [["Quantity", "5 + 5 pcs."], ["Size", "930 x 855 mm"], ["Material", "sandblast foil"], ["Print", "white"],
                    ["Artwork", "separate files for printing"], ["Weight (calc.)", "-"]])


# ------------------------------------------------------------------ portalas (6)
def s06():
    W, H, L, B, F, Dp = 4700, 3050, 300, 300, 160, 100
    XJ = W / 2
    red = HexColor(K.ralhex("3020")); grey = HexColor("#C9CACE")
    out = start("s06_portal", 12)
    A_TOP, A_BOT, A_L = 58, 56, 60
    ROW2 = 150                                                    # apatinė eilė: buferio išklotinė + vaizdas iš viršaus + 3D
    ah = K.VIEW_BOT - K.IY0 - A_TOP - A_BOT - ROW2
    CAB_W = 112                                                   # laido užrašai dešinėje nuo galinio vaizdo
    # v316 patikra 21: FRONT / SIDE / REAR - VIENAS bendras mastelis (patvirtintame galinis buvo 1:50)
    SC = LE.pick_scale((2 * W + Dp, H), ((K.IX1 - K.IX0) - 2 * A_L - CAB_W - 40 - 4 * 30, ah))
    s = MM / SC
    RN, rs = SC, s
    ROW2 = K.VIEW_BOT - K.IY0 - (A_TOP + H * s + A_BOT) - 20          # likusi vieta - apatinei eilei (didesnis buferis / 3D)
    cols = [A_L + W * s, max(Dp * s + 30, LE.title_w("SIDE VIEW (RIGHT)", f"SCALE 1:{SC}")), W * rs + CAB_W]
    CX, G = LE.distribute(K.IX0, K.IX1, cols, margin=(0.5, 0.5))
    fx = CX[0] + A_L; fy = K.IY0 + A_TOP
    X = lambda mm: fx + mm * s
    Yv = lambda mm: fy + mm * s
    # FRONT VIEW
    K.set_view(True)
    for a in (0, W - L):
        rect(X(a), Yv(0), L * s, (H - F) * s, fill=red, lw=0.4)
        rect(X(a), Yv(H - F), L * s, F * s, fill=grey, lw=0.4)
    rect(X(L), Yv(0), (W - 2 * L) * s, B * s, fill=red, lw=0.4)
    line(X(XJ), Yv(0), X(XJ), Yv(B) + 6, 0.5, black, dash=([6, 2, 1.5, 2], 0))
    K.set_view(False)
    hdim(X(0), X(W), fy - 44, "4700", fy, fy, size=K.F_DIM_MAIN)
    # v316: viršaus dalys (2050 + 2050, sandūra C) - toje pačioje grandinėje, ne atskira grandinė per angą
    hchain(fy - 20, [X(0), X(L), X(XJ), X(W - L), X(W)], [fy] * 5, ["300", f"{XJ - L:.0f}", f"{W - L - XJ:.0f}", "300"],
           size=K.F_DIM_MAIN)
    vchain(fx - 48, [Yv(0), Yv(H)], [fx] * 2, ["3050"], size=K.F_DIM_MAIN)
    vchain(fx - 24, [Yv(0), Yv(B), Yv(H - F), Yv(H)], [fx] * 4, ["300", "2590", "160"], size=K.F_DIM_MAIN)
    vchain(X(W - L) - 25, [Yv(B), Yv(H)], [X(W - L) - 25] * 2, ["2750"], size=K.F_DIM_MAIN)
    T(X(XJ), Yv(B) + 14, "TOP FROM 2 PARTS - JOINT C", 8, font="FB", align="c", auto_red=False)
    leader(X(W - L / 2), Yv(H - F / 2), X(W) + 25, Yv(H - F / 2) + 18, 3)
    leader(X(L / 2), Yv(H * 0.8), X(L) + 30, Yv(H * 0.88), 1)
    view_title(fx + W * s / 2, Yv(H) + 30, "FRONT VIEW", f"SCALE 1:{SC}")
    # DETAIL C - viršaus sandūra (3D), angoje po užrašu
    V3c = K.View3D()
    dk_ = HexColor("#8E1018")
    cw_, ch_ = min(150, (W - 2 * L) * s * 0.4), min(100, (H - B - F) * s * 0.4)
    cx0 = X(XJ) - cw_ / 2; cy0 = Yv(B) + 30
    sol = [(sbox(0, 0, 220, 300), 0, 100, red, red), (sbox(360, 0, 580, 300), 0, 100, red, red), (sbox(270, 10, 360, 290), 0, 88, dk_, dk_)]
    K.set_view(True)
    _iso(V3c, (cx0, cy0, cw_, ch_), sol)
    K.set_view(False)
    view_title(cx0 + cw_ / 2, cy0 + ch_ + 14, "DETAIL C - TOP JOINT", "plexiglas front 2 parts, inner sleeve")
    # SIDE VIEW
    sx = CX[1] + (cols[1] - Dp * s) / 2
    K.set_view(True)
    rect(sx, Yv(0), Dp * s, (H - F) * s, fill=red, lw=0.4)
    rect(sx, Yv(H - F), Dp * s, F * s, fill=grey, lw=0.4)
    K.set_view(False)
    hdim(sx, sx + Dp * s, fy - 20, "100", fy, fy, size=K.F_DIM_MAIN, small_side="r")
    view_title(sx + Dp * s / 2, Yv(H) + 30, "SIDE VIEW (RIGHT)", f"SCALE 1:{SC}")
    # REAR VIEW (MIRRORED) - be apsaugos
    rx = CX[2]; ry = fy
    K.set_view(True)
    for a in (0, W - L):
        rect(rx + a * rs, ry, L * rs, H * rs, fill=red, lw=0.4)
    rect(rx + L * rs, ry, (W - 2 * L) * rs, B * rs, fill=red, lw=0.4)
    line(rx + (W - XJ) * rs, ry - 4, rx + (W - XJ) * rs, ry + B * rs + 4, 0.5, black, dash=([6, 2, 1.5, 2], 0))
    K.set_view(False)
    T(rx + W * rs / 2, ry + B * rs + 12, "Backside 2 mm Alu, painted RAL 3020", 8, align="c")
    cxp, cyp = rx + (W - L / 2) * rs, ry + 150 * rs
    K.c.saveState(); K.c.setFillColor(white); K.c.setStrokeColor(black); K.c.setLineWidth(0.1)
    K.c.circle(cxp, K.Y(cyp), 3, stroke=1, fill=1); K.c.restoreState()
    xe = rx + W * rs + 16
    K.cable_line([(cxp + 3, cyp), (xe, cyp)])
    for i_, (t_, col) in enumerate((("D11 cable exit", None), ("top left (front view)", None), ("12V, 3 m + dimming", K.CABLE),
                                    ("-> trafo box (220V)", K.CABLE))):
        T(xe + 3, cyp - 3 + 11 * i_, t_, 8, **({"color": col, "auto_red": False} if col else {}))
    view_title(rx + W * rs / 2, ry + H * rs + 30, "REAR VIEW (MIRRORED)", f"SCALE 1:{RN}")
    # 3D
    V3 = K.View3D()
    solids = [(sbox(0, F, L, H), 0, Dp, red, red), (sbox(W - L, F, W, H), 0, Dp, red, red), (sbox(L, H - B, XJ - 4, H), 0, Dp, red, red),
              (sbox(XJ + 4, H - B, W - L, H), 0, Dp, red, red), (sbox(0, 0, L, F), 0, Dp, grey, grey), (sbox(W - L, 0, W, F), 0, Dp, grey, grey)]
    y3 = K.VIEW_BOT - ROW2 + 6
    h3 = ROW2 - 40
    w3 = min(cols[2], h3 * 1.9)
    K.set_view(True)
    _iso(V3, (CX[2] + (cols[2] - w3) / 2, y3, w3, h3), solids)
    K.set_view(False)
    view_title(CX[2] + cols[2] / 2, y3 + h3 + 16, "3D VIEW", "ILLUSTRATIVE - NOT TO SCALE")
    # BUFERIS: išklotinė 505 x 160 + vaizdas iš viršaus 304 x 102 (apatinė eilė, po priekiu)
    BS = LE.pick_scale((505 + 304 + 120, 160), (CX[2] - G - CX[0] - A_L, ROW2 - 50), iso=(2, 5, 10))
    k = MM / BS
    by = K.VIEW_BOT - ROW2 + 22
    T(fx, by - 6, "(3)  STAINLESS STEEL BUMPER 1 mm  -  2 pcs.  (front + 2 sides, front view only)", 8, font="FB", auto_red=False)
    ux = fx; uy = by + 22
    K.set_view(True)
    rect(ux, uy, 505 * k, 160 * k, fill=HexColor("#E3E4E8"), lw=0.4)
    K.set_view(False)
    for bl in (101.5, 403.5):
        line(ux + bl * k, uy, ux + bl * k, uy + 160 * k, 0.3, K.GREY, dash=([4, 1, 1, 1], 0))
    hdim(ux, ux + 505 * k, uy - 10, "505", uy, uy)
    vchain(ux - 12, [uy, uy + 160 * k], [ux] * 2, ["160"])
    T(ux + 505 * k / 2, uy + 160 * k + 14, f"FLAT PATTERN  (bend lines dash-dot)  |  SCALE 1:{BS}", 8, color=K.GREY, align="c", auto_red=False)
    tx = ux + 505 * k + 60; tyy = uy + 6
    t1 = 1.0 * k + 0.6
    K.set_view(True)
    poly([(tx, tyy), (tx + 304 * k, tyy), (tx + 304 * k, tyy + 102 * k), (tx + 304 * k - t1, tyy + 102 * k), (tx + 304 * k - t1, tyy + t1),
          (tx + t1, tyy + t1), (tx + t1, tyy + 102 * k), (tx, tyy + 102 * k)], fill=HexColor("#8C8C8C"), lw=0.3)
    K.set_view(False)
    hdim(tx, tx + 304 * k, tyy - 10, "304", tyy, tyy)
    vchain(tx + 304 * k + 12, [tyy, tyy + 102 * k], [tx + 304 * k] * 2, ["102"])
    T(tx + 152 * k, tyy + 102 * k + 14, "TOP VIEW  (inner 302 x 101)", 8, color=K.GREY, align="c", auto_red=False)

    def sec(x, y, w, h):
        s2 = (w - 70) / 300.0
        ox, oy = x + (w - 300 * s2) / 2, y + (h - 100 * s2) / 2 - 6
        tt = 3 * s2 * 2.2
        K.set_view(True)
        rect(ox, oy, 300 * s2, 100 * s2, fill=None, lw=0.3)
        K.hatch(ox, oy + 100 * s2 - tt, 300 * s2, tt, 2)
        K.hatch(ox, oy, tt, 100 * s2, 2); K.hatch(ox + 300 * s2 - tt, oy, tt, 100 * s2, 2)
        rect(ox + tt, oy, 300 * s2 - 2 * tt, 2.5, fill=black, lw=0.3)
        for f_ in (0.25, 0.5, 0.75):
            rect(ox + 300 * s2 * f_ - 7, oy + 2.5, 14, 4.5, fill=white, lw=0.35)
        K.set_view(False)
        hdim(ox, ox + 300 * s2, oy - 12, "300", oy, oy)
        vchain(ox + 300 * s2 + 14, [oy, oy + 100 * s2], [ox + 300 * s2] * 2, ["100"])
        leader(ox + 300 * s2 * 0.6, oy + 100 * s2 - tt / 2, ox + 300 * s2 * 0.6, oy + 100 * s2 + 16, 1)
        leader(ox + 60, oy + 1.2, ox + 40, oy - 16, 4)
        leader(ox + 300 * s2 * 0.5, oy + 5, ox + 300 * s2 * 0.5 + 24, oy + 30, 5)
        T(x + w / 2, oy + 100 * s2 + 30, "section through leg / beam - wall side up", 8, color=K.GREY, align="c", auto_red=False)
    # v316 (TAISYKLĖ v304): m² - lakštų nesting (nesting.py), ne grynasis plotas
    import nesting as NE
    pl = "PLEXIGLAS GS 3H25, 3 mm"
    # sija - 2 dalys per sandūrą C (XJ), kaip viršus
    body = [sbox(0, 0, L, H - F)] * 2 + [sbox(0, 0, Dp, H - F)] * 4 + [sbox(0, 0, Dp, XJ - L)] * 4
    n1 = NE.nest_parts(body, pl, label="body")
    n2 = NE.nest_parts([sbox(0, 0, XJ - L, B)] * 2, pl, label="top")
    n4 = NE.nest_parts([sbox(0, 0, L, H)] * 2 + [sbox(0, 0, XJ - L, B)] * 2, "Alu 2 mm", label="backside")
    print(" nesting:", n1["text"], "|", n2["text"], "|", n4["text"])
    K.FEAT.add("nest")
    m2 = lambda r: f"{r['m2']:.2f} m²".replace(".", ",")
    bom = [[1, "Body, red plexiglas (front + sides)", pl, "RAL 3020", m2(n1)],
           [2, "TOP, red plexiglas - 2 parts (joint C)", "PLEXIGLAS GS 3H25, 3 mm", "RAL 3020", f"2 pcs. (2 x 2050 mm) / {m2(n2)}"],
           [3, "Bumper 505 x 160 mm, bent 304 x 102 mm", "Stainless steel 1 mm", "-", "2 pcs."],
           [4, "Backside", "Alu 2 mm", "RAL 3020", m2(n4)],
           [5, "LED modules + dimmer", "", "", ""],
           [6, "Bottom", "PVC 10 mm", "-", "2 pcs."],
           [7, "Trafo box 12V + dimming (cable 12V, 3 m)", "Alu box", "-", "1 pcs."],
           [8, "Wall / floor fixing", "", "-", ""]]
    md = [["Quantity", "1 pcs."], ["Overall size", "4700 x 3050 mm"], ["Profile width", "300 mm"], ["Depth", "100 mm"],
          ["Clear opening", "4100 x 2750 mm"], ["Top", "2 parts 2050 + 2050, joint C"], ["Face", "PLEXIGLAS GS 3H25, RAL 3020"],
          ["Backside", "Alu 2 mm, RAL 3020"], ["Bumper", "stainless 1 mm, h 160 mm, front"], ["Illumination", "LED + dimming"],
          ["Power", "12V 3 m -> trafo box 220V"], ["Weight (calc.)", "≈ 35 kg / pcs, excl. PSU"]]
    band("PORTAL - TYPICAL SECTION", sec, bom, md, "Portal - entrance, illuminated", 6, f"1:{SC}")
    finish(out, (SC, G, {"front H": (H * s, ah)}))


# ------------------------------------------------------------------ FRISK & SUNN (18) - braizyti_lapa.py (P6 ant folded fono)
def s18():
    import json
    import subprocess
    sp = json.load(open(os.path.join(HERE, "..", "spec", "frisk.json")))
    sp.update({"client_pdf": os.path.join(HERE, "svarus_s18_frisk.pdf"), "order_no": ALT, "date": DATE, "sheet": "18 / 18"})
    for r in sp["bom"]:
        if str(r[1]).startswith("Screw lid"):                     # v316 patikra 16: dabartiniai vienetai ilgesni - spec į MATERIAL
            r[1], r[2] = "Screw lid -> L", "{S_SPEC}"
    # v316 (TAISYKLĖ v304): P1 apskritimo m² - lakšto / juostos nesting (buvo grynasis plotas)
    import math
    import nesting as NE
    from shapely.geometry import Point
    circ = Point(0, 0).buffer(299, 128)
    per = math.pi * 598 / 1000
    for r in sp["bom"]:
        if str(r[1]).startswith("P1 circle"):
            mat = r[2]
            n = (NE.nest_strips([per * 1000], 70, mat, label=r[1]) if "return" in r[1] else NE.nest_parts([circ], mat, label=r[1]))
            print("  nesting:", n["text"])
            m2 = f"{n['m2']:.2f} m²" if n.get("m2") is not None else "?"
            r[4] = (f"{per:.2f} m / " if "back" not in r[1] else "") + m2
    fn = os.path.join(SK, "s18_frisk.json")
    json.dump(sp, open(fn, "w"), indent=1, ensure_ascii=False)
    out = os.path.join(SK, "s18_frisk.pdf")
    os.path.exists(out) and os.remove(out)
    r = subprocess.run(["python3", os.path.join(HERE, "..", "..", "..", "braizyti_lapa.py"), fn, out], capture_output=True, text=True)
    print("\n".join(l for l in (r.stdout + r.stderr).splitlines() if l.startswith(("OK", "  !", "  nesting", "Trace")) or "Error" in l))


def _iso(V3, box_xywh, solids):
    pts = []
    for g, z0, z1, *_ in solids:
        x0, y0, x1, y1 = g.bounds
        pts += [(x, yv, z) for x in (x0, x1) for yv in (y0, y1) for z in (z0, z1)]
    V3.fit(pts, box_xywh)
    for g, z0, z1, side, face in sorted(solids, key=lambda t: (t[1], V3.depth_key(t[0], (t[1] + t[2]) / 2))):
        V3.solid(g, z0, z1, side, face)


if __name__ == "__main__":
    os.makedirs(SK, exist_ok=True)
    F = {"6": s06, "10": s10, "11": s11, "12": s12, "13": s13, "14": s14, "18": s18}
    for k in (sys.argv[1:] or list(F)):
        F[k]()
