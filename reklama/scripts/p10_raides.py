"""P10 raidės (30 mm balta plexi blokas) - tipinis pjūvis lapo juostoje (v242, Rytis 2026-10-15).
Etalonas: assets/etalonai/P10_Boots_ALT6739_akriliniai_begeliai.pdf, aprašas references/moduliai_p10_raides.md.
Sluoksniai nuo fasado: akrilinis rėmas 20 (įleista skylė Ø12 x 15 iš galo + Ø5 kiaurai, laidų griovelis nugaroje) |
Alu 1,5 nugara su privirinta smeige | plexi 30 blokas su LED grioveliu iš galo (LED juosta griovelio dugne) | priekis.
Balionai (BOM): 1 plexi blokas, 2 LED, 3 Alu nugara, 4 smeigė + veržlė, 5 rėmas."""
from reportlab.lib.colors import HexColor, white, black

PLEX = HexColor("#F7F7F2")
ACR = HexColor("#CFE6F5")
ALU = HexColor("#B4B4B4")
STUD = HexColor("#3A3A3A")
LED = HexColor("#F2E28C")


def section(K, x, y, w, h, spec, acry, rail_w, title="PROFILE P10"):
    from lapas_core import rect, line, T, hdim, vchain
    K.header(x, y, w, title)
    rect(x, y + 12, w, h - 12, lw=0.6)
    side_ral = next((g.get("return_ral") for g in spec.get("groups", []) if g.get("return_ral")), None)
    SIDE = HexColor(K.ralhex(side_ral)) if side_ral else HexColor("#6E6E6E")
    TR = float(acry["thk"]) if acry else 20.0
    TB = 1.5
    TP = 30.0 - TB                                       # Rytis 2026-10-15: P10 = 30 mm + rėmas (bendras 30 + rėmo storis)
    gr = spec.get("p10_groove") or {"w": 8, "d": None}
    gw, gd = float(gr.get("w") or 8), gr.get("d")
    gdd = float(gd) if gd else 10.0                      # piešimui; matmuo „?" jei nenurodytas
    RW = float(rail_w or 40)
    HL = RW + 14                                         # rodomas raidės štricho ruožas
    tot = TR + TB + TP
    k = min((w - 80) / (tot + 10), (h - 12 - 66) / HL)
    ox = x + 30
    oy = y + 12 + 22
    X = lambda z: ox + (z + 6) * k
    Y = lambda v: oy + v * k
    yc = HL / 2
    K.set_view(True)
    # rėmas (pjūvis per smeigę)
    ry0, ry1 = yc - RW / 2, yc + RW / 2
    rect(X(0), Y(ry0), TR * k, RW * k, fill=ACR, lw=0.4)
    if acry:
        st = acry.get("stud", {"d": 5, "cb_d": 12, "cb_depth": 15})
        rect(X(0), Y(yc - st["cb_d"] / 2), st["cb_depth"] * k, st["cb_d"] * k, fill=white, lw=0.3)
        rect(X(st["cb_depth"]), Y(yc - st["d"] / 2), (TR - st["cb_depth"]) * k, st["d"] * k, fill=white, lw=0.3)
        g_ = acry.get("groove") or {}
        gw_r, gd_r = float(g_.get("w", 6)), float(g_.get("d", 3.5))
        go = st["cb_d"] / 2 + gw_r / 2 + 2
        rect(X(0), Y(yc - go - gw_r / 2), gd_r * k, gw_r * k, fill=white, lw=0.3)
    # Alu nugara + plexi blokas (šonai dažyti - kraštai)
    rect(X(TR), Y(0), TB * k, HL * k, fill=ALU, lw=0.3)
    rect(X(TR + TB), Y(0), TP * k, HL * k, fill=PLEX, lw=0.4)
    rect(X(TR + TB), Y(0), TP * k, 0.8 * k, fill=SIDE, lw=0.1)
    rect(X(TR + TB), Y(HL - 0.8), TP * k, 0.8 * k, fill=SIDE, lw=0.1)
    # LED griovelis iš galo (ašyje) + juosta dugne
    rect(X(TR + TB), Y(yc - gw / 2), gdd * k, gw * k, fill=white, lw=0.3)
    rect(X(TR + TB + gdd - 1.6), Y(yc - gw / 2 + 0.8), 1.6 * k, (gw - 1.6) * k, fill=LED, lw=0.2)
    # smeigė (privirinta prie nugaros) + veržlė įleidime
    if acry:
        sy = yc + RW / 4 if False else yc
        rect(X(2), Y(sy - 2.5), (TR - 2) * k, 5 * k, fill=STUD, lw=0.2)
        rect(X(4), Y(sy - 4.5), 4 * k, 9 * k, fill=HexColor("#8C8C8C"), lw=0.2)
    K.set_view(False)
    line(X(-4), Y(-6), X(-4), Y(HL + 6), 1.2, HexColor("#888888"))
    T(X(-4) - 5, Y(HL / 2), "FACADE", 6, rot=90, align="c", color=K.GREY)
    hdim(X(0), X(TR), Y(-2) - 8, f"{TR:g}", Y(ry0), Y(ry0), size=7)
    hdim(X(TR), X(TR + TB + TP), Y(-2) - 8, f"{TB + TP:g}", Y(0), Y(0), size=7)
    hdim(X(0), X(tot), Y(HL) + 14, f"{TR + TB + TP:g}", Y(HL), Y(HL), size=7)
    T(X(tot / 2), Y(HL) + 26, f"LED groove {gw:g} x {gd if gd else '?'} deep (from back), strip on groove bottom", 6, align="c",
      color=K.GREY)
    bx = X(tot) + 14
    pts = [((X(TR + TB + TP * 0.7), Y(HL * 0.15)), "1"), ((X(TR + TB + gdd - 0.8), Y(yc)), "2"),
           ((X(TR + TB / 2), Y(HL * 0.85)), "3"), ((X(TR - 3), Y(yc + 2)), "4"), ((X(TR / 2), Y(ry1 - 3)), "5")]
    for i, ((px, py), n) in enumerate(pts):
        K.leader(px, py, bx, Y(0) + 4 + i * (HL * k - 8) / 4, n, 6)
