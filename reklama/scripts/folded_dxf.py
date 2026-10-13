"""Folded plokštės išklotinė DXF - GAMYBOS PRAKTIKA (v173, Rytis 2026-10-13, etalonas
`assets/etalonai/folded_1000x1000x40_isklotine_gamyba.dxf`):
- lenkimo linijos = stačiakampis W x H (vienas uždaras kontūras, sluoksnis BEND_UP_90);
- visi flanšai nuo lenkimo linijos = gylis - t (40 -> 38; Al 2 mm), t. y. lenkimo atskaita = t / 90°, K faktoriaus nėra;
- viršutinis / apatinis (užsilenkiantys) flanšai - per visą plotį tarp šonų lenkimo linijų (W);
- šoniniai (įsilenkiantys tarp skardų) flanšai - iš abiejų galų t (2 mm) trumpesni: H - 2t;
- kampų išpjova stačiakampė, be spindulių.
1000x1000x40 -> išklotinė 1076 x 1076. Ø3.2 tvirtinimo skylės (skill v37) - atskirame sluoksnyje HOLES_D3.2,
7 mm nuo viršaus / apačios flanšo krašto, 50 nuo galų, žingsnis ~300 (`--no-holes` - be jų).
NUMATYTA (Rytis 2026-10-13, bet kokiems matmenims): „sides inside" - šonai įsilenkia į vidų, viršus / apačia užsilenkia ant jų.
`--tb-inside` (v174, tik nurodžius „top/bottom inside"): viršus / apačia įsilenkia TARP šonų - jie t trumpesni iš galų (W - 2t), šonai per visą aukštį H.
Naudojimas: python3 folded_dxf.py PLOTIS AUKŠTIS out.dxf [GYLIS] [--t 2] [--no-holes] [--tb-inside]"""
import sys, os
import ezdxf

argv = sys.argv[1:]
t = 2.0
if "--t" in argv:
    i = argv.index("--t"); t = float(argv[i + 1]); del argv[i:i + 2]
args = [a for a in argv if not a.startswith("--")]
W, H, OUT = float(args[0]), float(args[1]), args[2]
PD = float(args[3]) if len(args) > 3 else 40.0
HOLES = "--no-holes" not in sys.argv
TB_IN = "--tb-inside" in sys.argv          # v174: viršus / apačia tarp šonų
FL = PD - t                                  # flanšas nuo lenkimo linijos (40 -> 38)
F, WF = W + 2 * FL, H + 2 * FL               # išklotinė

doc = ezdxf.new("R2010", setup=True); doc.units = ezdxf.units.MM
msp = doc.modelspace()
for name, col, lt in (("CUT", 7, "CONTINUOUS"), ("BEND_UP_90", 1, "DASHED"), ("HOLES_D3.2", 3, "CONTINUOUS"), ("TEXT", 2, "CONTINUOUS")):
    doc.layers.add(name, color=col, linetype=lt)
x0, x1, y0, y1 = FL, FL + W, FL, FL + H      # lenkimo linijos
if TB_IN:   # viršus / apačia trumpesni: x0+t .. x1-t; šonai per visą: y0 .. y1
    pts = [(x0 + t, 0), (x1 - t, 0), (x1 - t, y0), (F, y0), (F, y1), (x1 - t, y1), (x1 - t, WF), (x0 + t, WF),
           (x0 + t, y1), (0, y1), (0, y0), (x0 + t, y0)]
else:
    pts = [(x0, 0), (x1, 0), (x1, y0 + t), (F, y0 + t), (F, y1 - t), (x1, y1 - t), (x1, WF), (x0, WF),
           (x0, y1 - t), (0, y1 - t), (0, y0 + t), (x0, y0 + t)]
msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": "CUT"})
msp.add_lwpolyline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], close=True, dxfattribs={"layer": "BEND_UP_90"})
span = W - 100; n = max(1, round(span / 300))
if HOLES:
    for v in (7, WF - 7):
        for k in range(n + 1):
            msp.add_circle((x0 + 50 + span * k / n, v), 1.6, dxfattribs={"layer": "HOLES_D3.2"})
th = min(30, H / 20)
msp.add_text(f"FOLDED PLATE {W:.0f} x {H:.0f} x {PD:.0f} - Al {t:g} mm - FLAT {F:.0f} x {WF:.0f} - FACE OUT",
             height=th, dxfattribs={"layer": "TEXT"}).set_placement((F / 2, -2 * th), align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)
msp.add_text(f"bend lines = {W:.0f} x {H:.0f}, flanges {FL:g} from bend line, "
             + (f"top/bottom flanges {W - 2 * t:g} INSIDE (t shorter each end), sides {H:g}" if TB_IN else f"SIDES INSIDE (default): side flanges {H - 2 * t:g} (t shorter each end)")
             + ", 4 x 90 up"
             + (f" | D3.2 x 2 x {n + 1}: 50 | {n} x {span / n:.1f} | 50, 7 from edge" if HOLES else ""),
             height=th * 0.6, dxfattribs={"layer": "TEXT"}).set_placement((F / 2, -3.6 * th), align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)
doc.saveas(OUT)
print(f"flat {F:g} x {WF:g}, bend lines {W:g} x {H:g}, flanges {FL:g} from bend line, "
      + (f"top/bottom {W - 2 * t:g} inside, sides {H:g}" if TB_IN else f"side flanges {H - 2 * t:g}")
      + (f", holes 2 x {n + 1} pitch {span / n:.1f}" if HOLES else ", no holes"))
# v73: ar išklotinė telpa į tiekėjo Alu lakštą (assets/medziagos.json, paraštė 10 mm)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import medziagos as MEDZ
print("sheet:", MEDZ.sheet_text(MEDZ.sheet_fit(F, WF, "alu", t)))
