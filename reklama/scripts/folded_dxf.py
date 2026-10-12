"""Folded plokštės išklotinė DXF pagal skill'ą (v37+): Al 2 mm, R2, K 0.44, gylis 40 (STEP lankstinys_1prie1),
šoniniai flanšai TARP viršutinio ir apatinio (0.1 tarpas), Ø3.2 tvirtinimo skylės viršutinėje / apatinėje briaunoje
7 mm nuo krašto, 50 nuo galų, žingsnis ~300. Naudojimas: python3 folded_dxf.py PLOTIS AUKŠTIS out.dxf [GYLIS]"""
import sys, math
import ezdxf

W, H, OUT = float(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
PD = float(sys.argv[4]) if len(sys.argv) > 4 else 40.0
t, R, Kf, GAP = 2.0, 2.0, 0.44, 0.1
BA = math.pi / 2 * (R + Kf * t); OSSB = R + t; BD = 2 * OSSB - BA
a = PD - OSSB + BA / 2                 # flanšas iki lenkimo ašies
off = a + BA / 2 - OSSB                # realios koordinatės -> išklotinė
F, WF = W + 2 * PD - 2 * BD, H + 2 * PD - 2 * BD
SY0, SY1 = off + t + GAP, off + H - t - GAP

doc = ezdxf.new("R2010", setup=True); doc.units = ezdxf.units.MM
msp = doc.modelspace()
for name, col, lt in (("CUT", 7, "CONTINUOUS"), ("BEND_UP_90_R2", 1, "DASHDOT"), ("HOLES_D3.2", 3, "CONTINUOUS"), ("TEXT", 2, "CONTINUOUS")):
    doc.layers.add(name, color=col, linetype=lt)
o = off
pts = [(o, 0), (F - o, 0), (F - o, SY0), (F, SY0), (F, SY1), (F - o, SY1), (F - o, WF), (o, WF),
       (o, SY1), (0, SY1), (0, SY0), (o, SY0)]
msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": "CUT"})
for u in (a, F - a):
    msp.add_line((u, SY0), (u, SY1), dxfattribs={"layer": "BEND_UP_90_R2"})
for v in (a, WF - a):
    msp.add_line((off, v), (F - off, v), dxfattribs={"layer": "BEND_UP_90_R2"})
span = W - 100; n = max(1, round(span / 300))
for v in (7, WF - 7):
    for k in range(n + 1):
        msp.add_circle((off + 50 + span * k / n, v), 1.6, dxfattribs={"layer": "HOLES_D3.2"})
msp.add_text(f"FOLDED PLATE {W:.0f} x {H:.0f} x {PD:.0f} - Al {t:.0f} mm - FLAT {F:.1f} x {WF:.1f} - FACE OUT",
             height=min(30, H / 20), dxfattribs={"layer": "TEXT"}).set_placement((F / 2, WF / 2), align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)
msp.add_text(f"R{R:.0f} K{Kf} BD {BD:.2f} | 4 x 90 up | side flanges {H - 2 * t - 2 * GAP:.1f} between top/bottom | "
             f"D3.2 x 2 x {n + 1}: 50 | {n} x {span / n:.1f} | 50, 7 from edge",
             height=min(20, H / 30), dxfattribs={"layer": "TEXT"}).set_placement((0, -40))
doc.saveas(OUT)
print(f"flat {F:.2f} x {WF:.2f}, bend line {a:.2f} from edge, holes 2 x {n + 1} pitch {span / n:.1f}, side flange {H - 2 * t - 2 * GAP:.1f}")
# v73: ar išklotinė telpa į tiekėjo Alu lakštą (assets/medziagos.json, paraštė 10 mm)
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import medziagos as MEDZ
print("sheet:", MEDZ.sheet_text(MEDZ.sheet_fit(F, WF, "alu", t)))
