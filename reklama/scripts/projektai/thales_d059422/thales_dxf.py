"""Thales Campus Velizy (CEOS D059422) - gamybiniai DXF 1:1 (v153, patvirtinimas ALT8878_10.13_RS, 2026-10-13).

Skardos išklotinės (Alu 2 mm, R2, K 0.44 -> lenkimo atskaita BD = 3.48 / 90 deg), flanšai, PMMA plokštė.
Sluoksniai: 0_PJOVIMAS (kontūras), 1_LENKIMAS (lenkimo linijos, brūkšninės), 2_SKYLES_CSK (įleidžiami varžtai),
3_SKYLES_KNIEDES (aklosios kniedės), 4_SKYLES_ANKERIAI (flanšas), 9_INFO (tekstas, ne pjovimui).
Skylių skersmenys - PRIELAIDA (CEOS lape „D ___"): csk Ø5.0 (4.8 savigręžis), kniedė Ø4.1 (4.0) - keisti CSK_D / RIV_D.
Naudojimas: THALES_OUT=<aplankas> PREFIX=<ALT> python3 thales_dxf.py"""
import os, sys, math
import ezdxf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import thales_pylons as TP

T_AL, R_AL, K_AL = 2.0, 2.0, 0.44
BA = math.pi / 2 * (R_AL + K_AL * T_AL)
BD = 2 * (R_AL + T_AL) - BA                         # 3.476
CSK_D, RIV_D = 5.0, 4.1
OUT = os.environ.get("THALES_OUT", "out_dxf"); os.makedirs(OUT, exist_ok=True)
PREFIX = os.environ.get("PREFIX", "ALT0000_00.00_RS")
LOG = []


def new():
    d = ezdxf.new("R2010"); d.units = ezdxf.units.MM
    for n, c, lt in (("0_PJOVIMAS", 7, "CONTINUOUS"), ("1_LENKIMAS", 1, "DASHED"), ("2_SKYLES_CSK", 3, "CONTINUOUS"),
                     ("3_SKYLES_KNIEDES", 5, "CONTINUOUS"), ("4_SKYLES_ANKERIAI", 3, "CONTINUOUS"), ("9_INFO", 8, "CONTINUOUS")):
        if lt not in d.linetypes:
            d.linetypes.add(lt, pattern=[6.0, 4.0, -2.0]) if lt == "DASHED" else None
        d.layers.add(n, color=c, linetype=lt)
    return d


def poly(m, pts, layer="0_PJOVIMAS"):
    m.add_lwpolyline(pts, close=True, dxfattribs={"layer": layer})


def bend(m, a, b):
    m.add_line(a, b, dxfattribs={"layer": "1_LENKIMAS"})


def hole(m, x, y, d, layer):
    m.add_circle((x, y), d / 2, dxfattribs={"layer": layer})


def info(m, x, y, txt, h=8):
    m.add_text(txt, height=h, dxfattribs={"layer": "9_INFO"}).set_placement((x, y))


def save(d, name, qty, desc):
    fn = f"{PREFIX}_{name}.dxf"
    d.saveas(os.path.join(OUT, fn)); LOG.append((fn, qty, desc))


def blue_tray(p):
    """mėlyna lovelė: priekis W x HB (išorė), šonai + viršus TB, apačia: rib tarp išpjovų (ext) arba be lenkimo (int).
    Koordinatės: x 0..W, y 0 (apačia) .. HB (viršus) - priekio išorė; atlankai išklotinėje už jos ribų."""
    TB = TP.TB; W, H = p.W, p.HB
    f = TB - BD                                       # atlanko išklotinės ilgis
    d = new(); m = d.modelspace()
    rb = (p.rib - BD) if p.rib else 0
    N = TP.NOTCH
    pts = [(0, 0)]
    if p.rib:
        pts += [(N, 0), (N, -rb), (W - N, -rb), (W - N, 0)]
    pts += [(W, 0), (W + f, 0), (W + f, H), (W, H), (W, H + f), (0, H + f), (0, H), (-f, H), (-f, 0)]
    poly(m, pts)
    bend(m, (0, 0), (0, H)); bend(m, (W, 0), (W, H)); bend(m, (0, H), (W, H))
    if p.rib:
        bend(m, (N, 0), (W - N, 0))
    xo = TB - TP.HO_B - BD / 2                        # varžto ašis nuo lenkimo linijos išklotinėje (~ HO_B nuo išorės)
    for q in p.b_side_holes()[2]:
        hole(m, -(TP.HO_B - BD / 2), q, CSK_D, "2_SKYLES_CSK"); hole(m, W + (TP.HO_B - BD / 2), q, CSK_D, "2_SKYLES_CSK")
    for q in p.b_top_holes()[2]:
        hole(m, q, H + (TP.HO_B - BD / 2), CSK_D, "2_SKYLES_CSK")
    for q in p.rivets_v()[2]:
        y = TP.PL + 5 + q
        hole(m, 16, y, RIV_D, "3_SKYLES_KNIEDES"); hole(m, W - 16, y, RIV_D, "3_SKYLES_KNIEDES")
    nrh = max(2, round(p.LH / 300) + 1)
    for i in range(nrh):
        hole(m, 4 + TP.LP + 30 + i * (p.LH - 60) / (nrh - 1), TP.PL + 5 + 16, RIV_D, "3_SKYLES_KNIEDES")
    info(m, W / 2 - 200, H / 2, f"BLUE TRAY {W}x{H}x{TB} Alu 2 RAL 5022 - {2 * p.qty} pcs. - bends 90 R2 (BD {BD:.2f})")
    save(d, f"{p.key}_BLUE_tray_Alu2_x{2 * p.qty}", 2 * p.qty, f"Blue tray {W}x{H}x{TB}, Alu 2 mm RAL 5022")


def white_tray(p):
    """balta lovelė: priekis W x OVH; šonai + apačia 30; viršus: EAR (iki vidurio / galo) + galinė plokštuma 30;
    ausės (EAR x 30) - šono viršuje, uždaro šoną virš mėlynos."""
    W, H = p.W, p.OVH
    S = TP.TW - BD                                    # šono / apačios atlankas
    top1 = TP.EAR - BD                                # viršus (2 lenkimai: priekis->viršus, viršus->galinė plokštuma)
    top2 = 30 - BD / 2
    ear = TP.EAR - BD                                 # ausė išklotinėje (šono plotis viršuje)
    EH = 30                                           # ausės aukštis
    d = new(); m = d.modelspace()
    pts = [(0, -S), (W, -S), (W, 0), (W + S, 0), (W + S, H - EH), (W + ear, H - EH), (W + ear, H), (W, H),
           (W, H + top1 + top2), (0, H + top1 + top2), (0, H), (-ear, H), (-ear, H - EH), (-S, H - EH), (-S, 0), (0, 0)]
    poly(m, pts)
    bend(m, (0, 0), (W, 0)); bend(m, (0, 0), (0, H)); bend(m, (W, 0), (W, H)); bend(m, (0, H), (W, H))
    bend(m, (0, H + top1), (W, H + top1))
    ho = TP.HO_W - BD / 2
    for q in p.w_side_holes()[2]:
        hole(m, -ho, q, CSK_D, "2_SKYLES_CSK"); hole(m, W + ho, q, CSK_D, "2_SKYLES_CSK")
    for q in p.w_bot_holes()[2]:
        hole(m, q, -ho, CSK_D, "2_SKYLES_CSK")
    for q in p.w_bot_holes()[2]:                     # galinė plokštuma -> L 25 ant mėlyno viršaus (žingsnis ~300)
        hole(m, q, H + top1 + top2 - 16, CSK_D, "2_SKYLES_CSK")
    hole(m, -(ear - 20), H - EH + 12, CSK_D, "2_SKYLES_CSK"); hole(m, W + ear - 20, H - EH + 12, CSK_D, "2_SKYLES_CSK")
    info(m, W / 2 - 200, H / 2, f"WHITE TRAY {W}x{H} Alu 2 RAL 9016 - top {TP.EAR} + rear 30 - {p.sides * p.qty} pcs.")
    save(d, f"{p.key}_WHITE_tray_Alu2_x{p.sides * p.qty}", p.sides * p.qty, f"White tray {W}x{H}, top {TP.EAR} + 30, Alu 2 mm RAL 9016")


def flange(p):
    d = new(); m = d.modelspace()
    F = p.FL; e = (F - 237) / 2
    poly(m, [(0, 0), (F, 0), (F, F), (0, F)])
    for a in (e, F - e):
        for b in (e, F - e):
            hole(m, a, b, 14, "4_SKYLES_ANKERIAI")
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
    TP.TB = 40; TP.EAR = TP.TW + TP.TB
    E = TP.Pyl("ENT", 1050, 2530, 2, "ext", 1, "Entrance pylon")
    blue_tray(E); white_tray(E); flange(E)
    TP.TB = 43; TP.EAR = TP.TW + 2 * TP.TB
    B = TP.Pyl("BLD", 600, 2130, 1, "int", 4, "Building pylon")
    blue_tray(B); white_tray(B)
    pmma()
    for fn, q, ds in LOG:
        print(f"{fn}: {q} pcs. - {ds}")
    print(f"BD {BD:.3f} mm / 90 deg (Alu {T_AL}, R{R_AL}, K {K_AL}); csk D{CSK_D}, rivet D{RIV_D} (prielaida)")
