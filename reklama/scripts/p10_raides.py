"""P10 raidės (30 mm balta plexi blokas) - tipinis pjūvis lapo juostoje (v242-v244, Rytis 2026-10-15).
Etalonas: assets/etalonai/P10_Boots_ALT6739_akriliniai_begeliai.pdf, aprašas references/moduliai_p10_raides.md.
Pjūvis skersai raidės štricho per smeigę. Nuo fasado: akrilinis rėmas (įleista skylė Ø12 x 15 iš galo + Ø5 kiaurai,
laidų griovelis nugaroje) | plexi 30 blokas: gale ĮLEIDIMAS 1,5 mm, į kurį ĮSILEIDŽIA Alu 1,5 dugnelis (v244, Rytis:
„alu dugnelis įsileidžia į bloką"), kraštas aplink - plexi (rim, etalone ~5 mm); LED griovelis iš galo (po dugneliu),
LED juosta griovelio dugne; smeigė privirinta prie dugnelio. Bendras gylis = 30 + rėmas.
Balionai (BOM): 1 plexi blokas, 2 LED, 3 Alu dugnelis (įleistas), 4 smeigė + veržlė, 5 rėmas."""
from reportlab.lib.colors import HexColor, white

PLEX = HexColor("#F7F7F2")
ACR = HexColor("#CFE6F5")
ALU = HexColor("#B4B4B4")
STUD = HexColor("#3A3A3A")
LED = HexColor("#F2E28C")


def section(K, x, y, w, h, spec, acry, rail_w, title="PROFILE P10", stroke=None):
    from lapas_core import rect, line, T, hdim
    K.header(x, y, w, title)
    rect(x, y + 12, w, h - 12, lw=0.6)
    side_ral = next((g.get("return_ral") for g in spec.get("groups", []) if g.get("return_ral")), None)
    SIDE = HexColor(K.ralhex(side_ral)) if side_ral else HexColor("#6E6E6E")
    P = dict({"thk": 30.0, "back_t": 1.5, "rim": 5.0}, **(spec.get("p10") or {}))
    TR = float(acry["thk"]) if acry else 20.0
    TP, TB, RIM = float(P["thk"]), float(P["back_t"]), float(P["rim"])
    gr = spec.get("p10_groove") or {"w": 8, "d": None}
    gw, gd = float(gr.get("w") or 8), gr.get("d")
    gdd = float(gd) if gd else 10.0                      # piešimui; matmuo „?" jei nenurodytas
    RW = float(rail_w or 40)
    S = float(stroke or 24)                              # štricho plotis
    HL = S + 26                                          # rodomas ruožas aplink štrichą (platus bėgelis - nukirptas)
    tot = TR + TP
    k = min((w - 80) / (tot + 10), (h - 12 - 66) / HL)
    ox, oy = x + 30, y + 12 + 22
    X = lambda z: ox + (z + 6) * k
    Y = lambda v: oy + v * k
    yc = HL / 2
    s0, s1 = yc - S / 2, yc + S / 2
    K.set_view(True)
    ry0, ry1 = max(yc - RW / 2, 0), min(yc + RW / 2, HL)
    rect(X(0), Y(ry0), TR * k, (ry1 - ry0) * k, fill=ACR, lw=0.4)
    CUT = (ry0 == 0, ry1 == HL)                          # bėgelis platesnis už rodomą ruožą - nutraukimo linijos
    st = (acry or {}).get("stud", {"d": 5, "cb_d": 12, "cb_depth": 15})
    if acry:
        rect(X(0), Y(yc - st["cb_d"] / 2), st["cb_depth"] * k, st["cb_d"] * k, fill=white, lw=0.3)
        rect(X(st["cb_depth"]), Y(yc - st["d"] / 2), (TR - st["cb_depth"]) * k, st["d"] * k, fill=white, lw=0.3)
        g_ = acry.get("groove") or {}
        gw_r, gd_r = float(g_.get("w", 6)), float(g_.get("d", 3.5))
        go = st["cb_d"] / 2 + gw_r / 2 + 2
        if yc - go - gw_r / 2 >= ry0:
            rect(X(0), Y(yc - go - gw_r / 2), gd_r * k, gw_r * k, fill=white, lw=0.3)
    # plexi blokas, šonai dažyti
    rect(X(TR), Y(s0), TP * k, S * k, fill=PLEX, lw=0.4)
    rect(X(TR), Y(s0), TP * k, 0.8 * k, fill=SIDE, lw=0.1)
    rect(X(TR), Y(s1 - 0.8), TP * k, 0.8 * k, fill=SIDE, lw=0.1)
    # LED griovelis iš galo (po dugneliu) + juosta dugne
    rect(X(TR + TB), Y(yc - gw / 2), gdd * k, gw * k, fill=white, lw=0.3)
    rect(X(TR + TB + gdd - 1.6), Y(yc - gw / 2 + 0.8), 1.6 * k, (gw - 1.6) * k, fill=LED, lw=0.2)
    # Alu dugnelis ĮLEISTAS į bloką (lygiai su bloko galu), aplink plexi kraštas RIM
    rect(X(TR), Y(s0 + RIM), TB * k, (S - 2 * RIM) * k, fill=ALU, lw=0.3)
    if acry:                                             # smeigė (privirinta prie dugnelio) + veržlė įleidime
        rect(X(2), Y(yc - st["d"] / 2), (TR - 2) * k, st["d"] * k, fill=STUD, lw=0.2)
        rect(X(4), Y(yc - st["cb_d"] / 2 + 1.5), 4 * k, (st["cb_d"] - 3) * k, fill=HexColor("#8C8C8C"), lw=0.2)
    K.set_view(False)
    for f_, yy in zip(CUT, (0, HL)):
        if f_:
            pts_ = [(X(-1.5) + (X(TR + 1.5) - X(-1.5)) * j / 6, Y(yy) + (1.6 if j % 2 else -1.6)) for j in range(7)]
            for p0, p1 in zip(pts_, pts_[1:]):
                line(p0[0], p0[1], p1[0], p1[1], 0.25)
    if any(CUT):
        T(X(TR / 2), Y(HL) + 8, f"rail {RW:g}", 6, align="c", color=K.GREY)
    yt, yb = min(ry0, s0), max(ry1, s1)
    line(X(-4), Y(yt - 4), X(-4), Y(yb + 4), 1.2, HexColor("#888888"))
    T(X(-4) - 5, Y(yc), "FACADE", 6, rot=90, align="c", color=K.GREY)
    hdim(X(0), X(TR), Y(yt) - 10, f"{TR:g}", Y(ry0), Y(ry0), size=7)
    hdim(X(TR), X(TR + TP), Y(yt) - 10, f"{TP:g}", Y(s0), Y(s0), size=7)
    hdim(X(0), X(tot), Y(yb) + 16, f"{tot:g}", Y(ry1), Y(s1), size=7)
    T(x + 5, Y(yb) + 28, f"Alu {TB:g} back recessed into block (rim {RIM:g}); LED groove {gw:g} x {gd if gd else '?'} from back",
      6, color=K.GREY)
    bx = X(tot) + 14
    pts = [((X(TR + TP * 0.75), Y(s0 + S * 0.2)), "1"), ((X(TR + TB + gdd - 0.8), Y(yc)), "2"),
           ((X(TR + TB / 2), Y(s1 - RIM - 1)), "3"), ((X(TR - 3), Y(yc + 1)), "4"), ((X(TR / 2), Y(ry1 - 3)), "5")]
    for i, ((px, py), n) in enumerate(pts):
        K.leader(px, py, bx, Y(yt) + 4 + i * ((yb - yt) * k - 8) / 4, n, 6)
