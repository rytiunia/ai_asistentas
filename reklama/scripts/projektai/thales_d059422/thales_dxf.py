"""Thales Campus Velizy (CEOS D059422) - gamybiniai DXF 1:1.
v207 (Rytis 2026-10-14: „kodėl folded plates lankstiniai ne pagal taisykles? skylės 3,2 mm, 7 mm nuo kraštinės,
nepriklausomai ar varžtas įleidžiamas ar ne"): skardos išklotinės pagal FOLDED taisyklę v173 (`references/moduliai_folded.md`):
lenkimo linijos = išoriniai matmenys, atlankas nuo lenkimo linijos = gylis - t, ŠONAI ĮSILENKIA (t trumpesni ten, kur susitinka
su viršaus / apačios atlanku), K faktoriaus / BA NĖRA; tvirtinimo skylės Ø3.2, ašis 7 mm nuo atlanko krašto (ir csk, ir ne).
Sluoksniai kaip folded_dxf.py: CUT, BEND_UP_90, HOLES_D3.2, HOLES_RIVET (kniedės - prielaida), HOLES_ANCHOR_D14, TEXT.
Naudojimas: THALES_OUT=<aplankas> PREFIX=<ALT> python3 thales_dxf.py"""
import os, sys, math
import ezdxf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import thales_pylons as TP

T_AL = 2.0
HD, HE = 3.2, 7.0                                   # skylės Ø ir ašis nuo atlanko krašto
RIV_D = 4.1                                         # aklosios kniedės - PRIELAIDA (kliento lape Ø nėra)
OUT = os.environ.get("THALES_OUT", "out_dxf"); os.makedirs(OUT, exist_ok=True)
PREFIX = os.environ.get("PREFIX", "ALT0000_00.00_RS")
LOG = []


def new():
    d = ezdxf.new("R2010", setup=True); d.units = ezdxf.units.MM
    for n, c, lt in (("CUT", 7, "CONTINUOUS"), ("BEND_UP_90", 1, "DASHED"), ("HOLES_D3.2", 3, "CONTINUOUS"),
                     ("HOLES_RIVET", 5, "CONTINUOUS"), ("HOLES_ANCHOR_D14", 3, "CONTINUOUS"), ("TEXT", 2, "CONTINUOUS")):
        d.layers.add(n, color=c, linetype=lt)
    return d


def poly(m, pts, layer="CUT"):
    m.add_lwpolyline(pts, close=True, dxfattribs={"layer": layer})


def bend(m, a, b):
    m.add_line(a, b, dxfattribs={"layer": "BEND_UP_90"})


def hole(m, x, y, d=HD, layer="HOLES_D3.2"):
    m.add_circle((x, y), d / 2, dxfattribs={"layer": layer})


def info(m, x, y, txt, h=8):
    m.add_text(txt, height=h, dxfattribs={"layer": "TEXT"}).set_placement((x, y))


def save(d, name, qty, desc):
    fn = f"{PREFIX}_{name}.dxf"
    d.saveas(os.path.join(OUT, fn)); LOG.append((fn, qty, desc))


def blue_tray(p):
    """mėlyna lovelė (FACE OUT): priekis W x HB (lenkimo linijos), šonai + viršus TB; apačia - briauna tarp išpjovų (ext)
    arba be lenkimo (int). Viršus per visą W, šonai įsilenkia - t trumpesni ties viršumi."""
    t = T_AL; TB = TP.TB; W, H = p.W, p.HB
    f = TB - t                                        # atlankas nuo lenkimo linijos
    d = new(); m = d.modelspace()
    rb = (p.rib - t) if p.rib else 0
    N = TP.NOTCH
    pts = [(0, 0)]
    if p.rib:
        pts += [(N, 0), (N, -rb), (W - N, -rb), (W - N, 0)]
    pts += [(W, 0), (W + f, 0), (W + f, H - t), (W, H - t), (W, H + f), (0, H + f), (0, H - t), (-f, H - t), (-f, 0)]
    poly(m, pts)
    bend(m, (0, 0), (0, H)); bend(m, (W, 0), (W, H)); bend(m, (0, H), (W, H))
    if p.rib:
        bend(m, (N, 0), (W - N, 0))
    for q in p.b_side_holes()[2]:
        hole(m, -f + HE, q); hole(m, W + f - HE, q)
    for q in p.b_top_holes()[2]:
        hole(m, q, H + f - HE)
    for q in p.rivets_v()[2]:
        y = TP.PL + 5 + q
        hole(m, 16, y, RIV_D, "HOLES_RIVET"); hole(m, W - 16, y, RIV_D, "HOLES_RIVET")
    nrh = max(2, round(p.LH / 300) + 1)
    for i in range(nrh):
        hole(m, 4 + TP.LP + 30 + i * (p.LH - 60) / (nrh - 1), TP.PL + 5 + 16, RIV_D, "HOLES_RIVET")
    info(m, W / 2 - 250, H / 2, f"BLUE TRAY {W}x{H}x{TB} Alu {t:g} RAL 5022 - {2 * p.qty} pcs. - FACE OUT - flat {W + 2 * f:g} x {H + f + rb:g}")
    info(m, W / 2 - 250, H / 2 - 14, f"returns {f:g} from bend line, sides inside (H - t), D{HD:g} {HE:g} from edge; rivets D{RIV_D:g} (assumption)", 6)
    save(d, f"{p.key}_BLUE_tray_Alu2_x{2 * p.qty}", 2 * p.qty, f"Blue tray {W}x{H}x{TB}, Alu 2 mm RAL 5022, flat {W + 2 * f:g} x {H + f + rb:g}")


def white_tray(p):
    """balta lovelė (FACE OUT): priekis W x OVH; šonai + apačia TW; viršus EAR + galinė plokštuma 30 (2 lenkimai);
    ausės (EAR x 30) šonų viršuje. v208: viršus / apačia įsilenkia TARP šonų (W - 2t), šonai per visą aukštį."""
    t = T_AL; W, H = p.W, p.OVH
    S = TP.TW - t                                     # šono atlankas
    SB = p.WBOT - t                                   # v209: apačios atlankas (įėjimo pilonas - 20, pastatų - 30)
    top1 = TP.EAR - t                                 # viršus tarp lenkimo linijų
    top2 = 30 - t                                     # galinė plokštuma
    ear = TP.EAR - t                                  # ausė (šono plotis viršuje)
    EH = 30
    d = new(); m = d.modelspace()
    # v208 (Rytis 2026-10-14): WHITE plates (visos projekte) - VIRŠUS / APAČIA LENKIASI Į VIDŲ (tarp šonų, folded --tb-inside):
    #  viršaus ir apačios atlankai iš abiejų galų t trumpesni (x t .. W - t), šonai (ir ausės) - per visą aukštį 0 .. H
    pts = [(t, -SB), (W - t, -SB), (W - t, 0), (W + S, 0), (W + S, H - EH), (W + ear, H - EH), (W + ear, H), (W - t, H),
           (W - t, H + top1 + top2), (t, H + top1 + top2), (t, H), (-ear, H), (-ear, H - EH), (-S, H - EH), (-S, 0), (t, 0)]
    poly(m, pts)
    bend(m, (0, 0), (W, 0)); bend(m, (0, 0), (0, H)); bend(m, (W, 0), (W, H)); bend(m, (0, H), (W, H))
    bend(m, (t, H + top1), (W - t, H + top1))
    for q in p.w_side_holes()[2]:
        hole(m, -S + HE, q); hole(m, W + S - HE, q)
    for q in p.w_bot_holes()[2]:
        hole(m, q, -SB + HE)
    for q in p.w_bot_holes()[2]:                     # galinė plokštuma -> L 25 ant mėlyno viršaus (žingsnis ~300)
        hole(m, q, H + top1 + top2 - HE)
    ye = H - EH / 2
    hole(m, -ear + HE, ye); hole(m, W + ear - HE, ye)
    FW_, FH_ = W + 2 * ear, H + SB + top1 + top2
    info(m, W / 2 - 250, H / 2, f"WHITE TRAY {W}x{H} Alu {t:g} RAL 9016 - bottom {p.WBOT}, top {TP.EAR} + rear 30 - {p.sides * p.qty} pcs. - FACE OUT - flat {FW_:g} x {FH_:g}")
    info(m, W / 2 - 250, H / 2 - 14, f"returns = depth - t from bend line, TOP / BOTTOM INSIDE (W - 2t), sides full height, D{HD:g} {HE:g} from edge", 6)
    save(d, f"{p.key}_WHITE_tray_Alu2_x{p.sides * p.qty}", p.sides * p.qty, f"White tray {W}x{H}, bottom {p.WBOT}, top {TP.EAR} + 30, Alu 2 mm RAL 9016, flat {FW_:g} x {FH_:g}")


def flange(p):
    d = new(); m = d.modelspace()
    F = p.FL; e = (F - 237) / 2
    poly(m, [(0, 0), (F, 0), (F, F), (0, F)])
    for a in (e, F - e):
        for b in (e, F - e):
            hole(m, a, b, 14, "HOLES_ANCHOR_D14")
    info(m, 10, F + 10, f"BASE FLANGE {F}x{F}x{p.FLT} Alu 6082-T6, 4 x D14 / 237 - 2 pcs.")
    save(d, f"{p.key}_FLANGE_{F}x{F}x{p.FLT}_x2", 2, f"Base flange {F}x{F}x{p.FLT}, 4 x Ø14 / 237")


def pmma():
    """PMMA 4 mm, 297 x (210 + 80) ištiesta, termoformuojama R10 (vidinis): išklotinė pagal neutralią ašį (t/2)."""
    t, R, H, F, W = 4.0, 10.0, 210.0, 80.0, 297.0
    L = (H - (R + t)) + (F - (R + t)) + math.pi / 2 * (R + t / 2)
    d = new(); m = d.modelspace()
    poly(m, [(0, 0), (W, 0), (W, L), (0, L)])
    yb = F - (R + t) + math.pi / 4 * (R + t / 2)      # lenkimo vidurio linija
    bend(m, (0, yb), (W, yb))
    info(m, 10, L + 10, f"PMMA clear 4 mm {W:.0f} x {L:.1f} (flat) - thermoform R10 inside, 100 deg (face leans back 10) - 1 pc.")
    save(d, "PMMA_plate_297x210_t4_x1", 1, f"PMMA 4 mm flat {W:.0f} x {L:.1f}, bend line {yb:.1f} from foot edge")


if __name__ == "__main__":
    TP.TB = 40; TP.EAR = TP.TW + TP.TB; TP.HO_B = TP.TB - TP.HO_EDGE
    E = TP.Pyl("ENT", 1050, 2530, 2, "ext", 1, "Entrance pylon")
    blue_tray(E); white_tray(E); flange(E)
    TP.TB = 43; TP.EAR = TP.TW + 2 * TP.TB; TP.HO_B = TP.TB - TP.HO_EDGE
    B = TP.Pyl("BLD", 600, 2130, 1, "int", 4, "Building pylon")
    blue_tray(B); white_tray(B)
    pmma()
    for fn, q, ds in LOG:
        print(f"{fn}: {q} pcs. - {ds}")
    print(f"folded v173: returns = depth - t, sides inside; holes D{HD:g} {HE:g} from edge; rivet D{RIV_D:g} (prielaida)")
