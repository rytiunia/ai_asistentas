#!/usr/bin/env python3
"""KIWI Lanterne med lys (BrandFactory order 226023, KIWI 640 BYGNES) - 1 lapas mūsų stiliumi (lapas_core).

Konstrukcija - kaip ankstesni gaminti KIWI lanterne (Tollnes 225948 ALT8858, HITRA 225553, Svolvær 202739):
2 x Alu profilis 100x20x2 (šonai), galinė 1,5 mm Alu, viršaus dangtis 1,5 mm su LED (Edge SM280-12V + KPS 15W),
apačioje 1 mm nerūdijančio plieno uždengimas h 700 (reguliuojamas), sekcijų jungtys su 3 mm Alu plokštelėmis.
Kliento duomenys (order 226023): korpusas 6800 x 500 x 100, padalintas, RAL 6018, LED (belysning kraftig led), EL viršuje.
v160 (Rytis 2026-10-13): visa informacija ir aprašymai - iš originalaus dokumento (Parts List, užrašai), keičiamas tik stilius.
Sekcijos 800 + 3000 + 3000 (pirmasis 226023 dokumentas).
Paleidimas:  python3 lanterne.py out.pdf
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import lapas_core as K  # noqa: E402
from lapas_core import T, line, rect, poly, circle, hdim, vchain, view_title, MM  # noqa: E402
from reportlab.lib.colors import HexColor, white, black  # noqa: E402

# ---------------------------------------------------------------- duomenys
H_BODY = 6800            # korpuso aukštis (kliento 6800, kiekis 6,80 m)
W, D = 500, 100          # korpusas
CAP_W, CAP_D, CAP_H = 505, 105, 150   # viršaus dangtis (kaip Tollnes)
PR_W, PR_T = 20, 2       # profilis 100x20x2
BACK_T = 1.5
SS_H = 700               # nerūdijantis uždengimas
SECT = [800, 3000, 3000]  # nuo viršaus (*)
N_LED, LED = 5, "Edge SM280-12V"
PSU = "KPS 15W"
RAL = "RAL 6018"
C_G = HexColor(K.code_hex(RAL))
C_GD = K.mix(C_G, 0.72)
C_SS = HexColor("#B9BCBE")
C_LED = HexColor("#F2F2F2")
C_RED = HexColor("#E2001A")
DIM = K.F_DIM_MAIN
D1, D2 = 16, 36

TB = {"client": "BrandFactory", "title": "Lanterne med lys 6800, RAL 6018",
      "order_no": "ALT0000_10.13_RS", "drawing_no": "Order 226023 KIWI 640 BYGNES", "rev": "A", "date": "2026-10-13",
      "sheet": "3 / 3", "revisions": [["A", "First issue", "2026-10-13", "RS"]]}


def HM(x1, x2, y, label, e1, e2):
    hdim(x1, x2, y, label, e1=e1, e2=e2, size=DIM)


def VM(x, ys, ext, labels):
    vchain(x, ys, [ext] * len(ys), labels, size=DIM, bg=True)


def joints_from_bottom():
    """sekcijų sandūrų aukščiai nuo apačios"""
    out, y = [], H_BODY
    for s in SECT[:-1]:
        y -= s
        out.append(y)
    return out


# ---------------------------------------------------------------- vaizdai
def front_view(X0, YG, s):
    """FRONT VIEW: atvira priekio pusė - matosi profiliai ir galinė (tamsesnė)"""
    xb, yt = X0, YG - H_BODY * s
    rect(xb, yt, W * s, H_BODY * s, fill=C_GD, lw=K.HAIR)                       # galinė per angą
    for xx in (0, W - PR_W):
        rect(xb + xx * s, yt, PR_W * s, H_BODY * s, fill=C_G, lw=K.HAIR)     # šonų profiliai (20 priekyje)
    cx0 = xb - (CAP_W - W) / 2 * s
    rect(cx0, yt - 0, CAP_W * s, CAP_H * s, fill=C_G, lw=K.HAIR)              # dangtis
    rect(cx0, YG - SS_H * s, CAP_W * s, SS_H * s, fill=C_SS, lw=K.HAIR)       # nerūdijantis uždengimas
    for yj in joints_from_bottom():
        line(xb - 3, YG - yj * s, xb + W * s + 3, YG - yj * s, 0.3, dash=([4, 1.5, 1, 1.5], 0))
    # matmenys: kairėje grandinė (dangtis, sekcijos), už jos - bendras
    ys = [yt] + [YG - yj * s for yj in joints_from_bottom()] + [YG]
    VM(cx0 - D1, ys, cx0, [f"{v}" for v in SECT])
    VM(cx0 - D1 - D2 + 4, [yt, YG], cx0, [f"{H_BODY}"])
    # dešinėje - dangtis ir uždengimas
    xr = cx0 + CAP_W * s
    VM(xr + D1, [yt, yt + CAP_H * s], xr, [f"{CAP_H}"])
    VM(xr + D1, [YG - SS_H * s, YG], xr, [f"{SS_H}"])
    HM(cx0, cx0 + CAP_W * s, yt - D2, f"{CAP_W}", yt, yt)
    HM(xb, xb + W * s, yt - D1, f"{W}", yt, yt)
    # EL išvestis viršuje
    ex, ey = xb + W * s * 0.8, yt
    line(ex, ey, ex, ey - 26, 0.9, C_RED)
    T(ex + 4, ey - 20, "+1,5m  ~230V  El. Output", K.F_INFO, color=C_RED)
    return dict(x0=cx0, x1=cx0 + CAP_W * s, yt=yt, yb=YG, xb=xb)


def side_view(X0, YG, s):
    """SIDE VIEW (RIGHT): profilis 100 + galinė; uždengimas, dangtis"""
    yt = YG - H_BODY * s
    rect(X0, yt, D * s, H_BODY * s, fill=C_G, lw=K.HAIR)
    rect(X0, yt, CAP_D * s, 75 * s, fill=C_G, lw=K.HAIR)
    rect(X0, YG - SS_H * s, CAP_D * s, SS_H * s, fill=C_SS, lw=K.HAIR)
    VM(X0 + CAP_D * s + D1, [yt, yt + 75 * s], X0 + CAP_D * s, ["75"])
    for yj in joints_from_bottom():
        y_ = YG - yj * s
        line(X0 - 3, y_, X0 + D * s + 3, y_, 0.3, dash=([4, 1.5, 1, 1.5], 0))
        for k in (0.3, 0.7):                                                    # varžtai (jungties plokštelė)
            circle(X0 + D * s * k, y_ - 40 * s, 0.9, fill=black, lw=0)
            circle(X0 + D * s * k, y_ + 40 * s, 0.9, fill=black, lw=0)
    HM(X0, X0 + D * s, yt - D1, f"{D}", yt, yt)
    HM(X0, X0 + CAP_D * s, yt - D2, f"{CAP_D}", yt, yt)
    return dict(x0=X0, x1=X0 + CAP_D * s, yt=yt, yb=YG)


def rear_view(X0, YG, s):
    """REAR VIEW: galinė iš 3 dalių (sandūros) - tvirtinimas prie fasado nežinomas"""
    yt = YG - H_BODY * s
    rect(X0, yt, W * s, H_BODY * s, fill=C_G, lw=K.HAIR)
    rect(X0 - (CAP_W - W) / 2 * s, yt, CAP_W * s, CAP_H * s, fill=C_G, lw=K.HAIR)
    rect(X0 - (CAP_W - W) / 2 * s, YG - SS_H * s, CAP_W * s, SS_H * s, fill=C_SS, lw=K.HAIR)
    for yj in joints_from_bottom():
        line(X0, YG - yj * s, X0 + W * s, YG - yj * s, 0.5)
    return dict(x0=X0, x1=X0 + W * s, yt=yt, yb=YG)


def section_aa(X0, Y0, s):
    """SECTION A-A (horizontalus pjūvis per korpusą): galinė 1,5 + 2 profiliai 100x20x2, LED šviesa iš viršaus"""
    # y žemyn = nuo fasado į priekį
    rect(X0, Y0, W * s, BACK_T * s, fill=C_GD, lw=0.35)                        # galinė
    for xx in (0, W - PR_W):
        x_ = X0 + xx * s
        rect(x_, Y0 + BACK_T * s, PR_W * s, D * s, fill=C_G, lw=0.35)
        rect(x_ + PR_T * s, Y0 + (BACK_T + PR_T) * s, (PR_W - 2 * PR_T) * s, (D - 2 * PR_T) * s, fill=white, lw=0.35)
    yb = Y0 + (BACK_T + D) * s
    HM(X0, X0 + W * s, yb + D1, f"{W}", yb, yb)
    VM(X0 + W * s + D1, [Y0, Y0 + BACK_T * s + D * s], X0 + W * s, [f"{D}"])
    T(X0 + W * s / 2, Y0 - 4, "FACADE SIDE", K.F_INFO, color=K.GREY, align="c")
    return dict(x0=X0, x1=X0 + W * s, yt=Y0, yb=yb)


def detail_top(X0, Y0, s):
    """DETAIL B (vertikalus pjūvis per viršų): dangtis 1,5 mm, LED moduliai šviečia žemyn, PSU, laidas"""
    hh = 240
    # profilis (šonas) ir galinė
    rect(X0, Y0 + CAP_H * s, BACK_T * s, (hh - CAP_H) * s, fill=C_GD, lw=0.35)
    rect(X0 + BACK_T * s, Y0 + 40 * s, D * s, (hh - 40) * s, fill=C_G, lw=K.HAIR)
    # dangtis
    poly([(X0 - 2 * s, Y0 + CAP_H * s), (X0 - 2 * s, Y0), (X0 + CAP_D * s, Y0), (X0 + CAP_D * s, Y0 + CAP_H * s)],
         stroke=black, lw=0.6, close=False)
    # LED moduliai po dangčiu (žemyn), PSU
    for k in range(2):
        rect(X0 + (20 + k * 40) * s, Y0 + 3 * s, 25 * s, 8 * s, fill=C_LED, lw=0.35)
    rect(X0 + 15 * s, Y0 + 14 * s, 70 * s, 18 * s, fill=HexColor("#CFCFCF"), lw=0.35)
    for k in range(4):                                                          # šviesos kryptis
        xx = X0 + (25 + k * 18) * s
        line(xx, Y0 + 34 * s, xx - 6 * s, Y0 + 120 * s, 0.25, K.GREY, dash=([2, 2], 0))
    line(X0 + 80 * s, Y0, X0 + 80 * s, Y0 - 22, 0.9, C_RED)
    VM(X0 + CAP_D * s + D1, [Y0, Y0 + CAP_H * s], X0 + CAP_D * s, [f"{CAP_H}"])
    # lūžio linija apačioje
    yb = Y0 + hh * s
    poly([(X0 - 6, yb), (X0 + 30 * s, yb), (X0 + 40 * s, yb - 5), (X0 + 55 * s, yb + 5), (X0 + 65 * s, yb),
          (X0 + D * s + 8, yb)], lw=0.3, close=False)
    return dict(x0=X0, x1=X0 + CAP_D * s, yt=Y0, yb=yb, led=(X0 + 32 * s, Y0 + 7 * s), psu=(X0 + 80 * s, Y0 + 24 * s),
                cap=(X0 + CAP_D * s, Y0 + 60 * s), cab=(X0 + 80 * s, Y0 - 14), prof=(X0 + 60 * s, Y0 + 200 * s), back=(X0, Y0 + 220 * s))


def detail_joint(X0, Y0, s):
    """DETAIL C (sandūra, vaizdas iš šono be išorinės sienelės): plokštelė 3 mm į abu profilius, 2 + 2 varžtai"""
    hh = 210
    rect(X0, Y0, D * s, hh * s, fill=C_G, lw=K.HAIR)
    yj = Y0 + hh / 2 * s
    line(X0, yj, X0 + D * s, yj, 0.6)
    rect(X0 + 15 * s, yj - 75 * s, 70 * s, 150 * s, fill=HexColor("#A9A9A9"), lw=0.35, dash=([3, 1.5], 0))
    for dy in (-40, 40):
        for k in (0.3, 0.7):
            circle(X0 + D * s * k, yj + dy * s, 2.0, fill=black, lw=0)
    for yy in (Y0, Y0 + hh * s):
        poly([(X0 - 6, yy), (X0 + 30 * s, yy), (X0 + 40 * s, yy - 5), (X0 + 55 * s, yy + 5), (X0 + 65 * s, yy),
              (X0 + D * s + 8, yy)], lw=0.3, close=False)
    return dict(x0=X0, x1=X0 + D * s, yt=Y0, yb=Y0 + hh * s, plate=(X0 + 50 * s, yj - 60 * s),
                screw=(X0 + D * s * 0.7, yj + 40 * s))


def view3d(box):
    import r3d
    sc = r3d.Scene(yaw=34, pitch=14)
    EDGE = HexColor("#3A3A3A")
    sc.box((0, 0, 0), (W, 0, 0), (0, H_BODY, 0), (0, 0, BACK_T), C_GD, edge=EDGE)
    for xx in (0, W - PR_W):
        sc.box((xx, 0, BACK_T), (PR_W, 0, 0), (0, H_BODY - CAP_H, 0), (0, 0, D), C_G, edge=EDGE)
    off = (CAP_W - W) / 2
    sc.box((-off, H_BODY - CAP_H, 0), (CAP_W, 0, 0), (0, CAP_H, 0), (0, 0, CAP_D), C_G, edge=EDGE)
    sc.box((-off, 0, BACK_T), (CAP_W, 0, 0), (0, SS_H, 0), (0, 0, CAP_D - BACK_T), C_SS, edge=EDGE)
    sc.render(box)
    return sc


# ---------------------------------------------------------------- juosta
def bom():
    """Parts List - kaip originale (Tollnes 225948 Sheet 3)"""
    return [[1, "100x20x2mm Alu profile"], [2, "Backside, 1.5mm Alu"], [3, "Top cover, 1.5mm Alu"],
            [4, "1mm stainless steel cover"], [5, "LED's with transformator"], [6, "Ffitting plate, 3mm Alu"],
            [7, "Screws"]]


def weight():
    prof = (2 * (100 + 20) - 4 * PR_T) * PR_T * 1e-6 * 2700 * 2 * (sum(SECT) - CAP_H) / 1000
    back = W * H_BODY * 1e-6 * BACK_T * 1e-3 * 2700
    cap = (CAP_W * CAP_D + 2 * CAP_W * CAP_H + 2 * CAP_D * CAP_H) * 1e-6 * 1.5e-3 * 2700
    ss = (CAP_W + 2 * CAP_D) * SS_H * 1e-6 * 1e-3 * 7900
    return prof + back + cap + ss


def main_data():
    return [["Quantity", "1 pcs."],
            ["Body height", f"{H_BODY}"],
            ["LED modules", f"Edge Modules SM280-12V, {N_LED}pcs."],
            ["Trafo", PSU],
            ["El. Output", "+1,5m  ~230V"],
            ["Colour", RAL],
            ["Weight (calc.)", f"≈ {weight():.0f} kg / pcs, excl. LED"]]


def band_section(x, y, w, h):
    """juostos kairė: tipinis pjūvis A-A 1:5"""
    K.header(x, y, w, "SECTION C-C  (1:10)")
    rect(x, y + 12, w, h - 12, lw=0.6)
    s = MM / 10
    X0 = x + (w - W * s) / 2 - 8
    r = section_aa(X0, y + 46, s)
    K.leader(r["x0"] + 10 * s, r["yt"] + 60 * s, r["x0"] - 14, r["yb"] + 34, 1)
    K.leader(r["x0"] + 400 * s, r["yt"] + 0.7 * s, r["x0"] + 400 * s + 22, r["yt"] - 16, 2)


def sheet(out):
    md, bm = main_data(), bom()
    K.set_band(max(len(md), len(bm) + 1, 12))
    K.init(out + ".tmp", "KIWI 226023 Lanterne")
    K.frame()
    s40 = MM / 40
    YG = K.VIEW_BOT - 30
    xf = K.IX0 + 110
    f = front_view(xf, YG, s40)
    xs = f["x1"] + 70
    sv = side_view(xs, YG, s40)
    xr = sv["x1"] + 90
    rv = rear_view(xr, YG, s40)
    yt = f["yt"]
    view_title((f["x0"] + f["x1"]) / 2, YG + 24, "FRONT VIEW", "SCALE 1:40")
    view_title((sv["x0"] + sv["x1"]) / 2 + 10, YG + 24, "SIDE VIEW", "SCALE 1:40")
    view_title((rv["x0"] + rv["x1"]) / 2, YG + 24, "REAR VIEW", "SCALE 1:40")
    # pjūvio plokštuma A-A per priekį (už vaizdo ribų)
    ya = YG - 2000 * s40
    K.cut_plane_h(ya, f["x0"], f["x1"], "C", look="down")
    # detalės B / C
    s5 = MM / 2
    xb = rv["x1"] + 135
    db = detail_top(xb, yt + 40, s5)
    view_title((db["x0"] + db["x1"]) / 2, db["yb"] + 26, "DETAIL B", "SCALE 1:2")
    xc = db["x1"] + 110
    dc = detail_joint(xc, yt + 40, s5)
    view_title((dc["x0"] + dc["x1"]) / 2, dc["yb"] + 40, "DETAIL A - CONNECTION POINT", "SCALE 1:2")
    # žymos B / C ant šoninio vaizdo
    for (cx_, cy_), lt in (((sv["x0"] + 4, yt + 6), "B"), ((sv["x0"] + 4, YG - joints_from_bottom()[1] * s40), "A")):
        circle(cx_, cy_, 9, lw=0.35)
        T(cx_ + 9, cy_ - 7, lt, 10, font="FB")
    # 3D
    x3 = dc["x1"] + 70
    box3 = (x3, K.IY0 + 30, K.IX1 - 20 - x3, YG - K.IY0 - 40)
    view3d(box3)
    view_title(x3 + box3[2] / 2, YG + 24, "3D VIEW", "ILLUSTRATIVE - NOT TO SCALE")
    # balionai (BOM POS)
    K.leader(f["x0"] + 3, YG - 1500 * s40, f["x0"] - 40, YG - 1300 * s40, 1)
    K.leader(f["xb"] + W * s40 / 2, YG - 4300 * s40, f["x0"] - 40, YG - 4000 * s40, 2)
    K.leader(rv["x1"] - 3, yt + 4, rv["x1"] + 30, yt + 30, 3)
    K.leader(rv["x1"] - 3, YG - 350 * s40, rv["x1"] + 30, YG - 600 * s40, 4)
    K.leader(*db["led"], db["x0"] - 34, db["yt"] + 6, 5)
    K.leader(*db["back"], db["x0"] - 34, db["back"][1] + 20, 2)
    K.leader(*db["prof"], db["x1"] + 40, db["prof"][1] + 10, 1)
    K.leader(*dc["plate"], dc["x0"] - 34, dc["plate"][1] - 20, 6)
    K.leader(*dc["screw"], dc["x0"] - 34, dc["screw"][1] + 30, 7)
    # originalo paaiškinimai (žymos už vaizdų)
    for yj in joints_from_bottom():
        K.tag(sv["x1"] - 1, YG - yj * s40, sv["x1"] + 14, YG - yj * s40 + 22, "Connection point", 8)
    K.tag(rv["x1"] - 1, YG - joints_from_bottom()[1] * s40, rv["x1"] + 12, YG - joints_from_bottom()[1] * s40 + 22,
          "Backside plate connect point", 8)
    K.tag(rv["x1"] - 1, YG - 200 * s40, rv["x1"] + 12, YG - 2, "Cover with adjustable position", 8)
    K.tag(*db["psu"], db["x1"] + 12, db["yt"] - 14, "LED modules with transformator", 8)
    # juosta
    BY0 = K.BAND_Y; BH = K.IY1 - BY0
    W_D, W_MD, W_TB = 214, 230, 272
    X_D = K.IX0; X_TB = K.IX1 - W_TB; X_MD = X_TB - W_MD; X_BOM = X_D + W_D; W_BOM = X_MD - X_BOM
    band_section(X_D, BY0, W_D, BH)
    K.bom_table(X_BOM, BY0, W_BOM, BH, bm, title="PARTS LIST", cols=(("POS", 20), ("Part Number", None)))
    K.main_data(X_MD, BY0, W_MD, BH, md, lab_w=64)
    K.title_block(X_TB, W_TB, TB, "1:40 / 1:10 / 1:2")
    K.save(out)


if __name__ == "__main__":
    sheet(sys.argv[1])
