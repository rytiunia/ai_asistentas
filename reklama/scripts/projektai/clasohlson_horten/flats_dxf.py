"""Horten 3 išklotinės DXF 1:1 (mm), išdėstytos lakštuose 2000x4000 kaip lape 2 (nesting)."""
import sys, math
sys.path.insert(0, ".")
import ezdxf
import data as D

OUT = sys.argv[1]
a, off = D.FL, D.FL + D.BA / 2 - D.OSSB
WF = D.flat_size(0)[1]
SY0, SY1 = off + 2.1, off + D.PH - 2.1
doc = ezdxf.new("R2010", setup=True); doc.units = ezdxf.units.MM
msp = doc.modelspace()
for name, col, lt in (("CUT", 7, "CONTINUOUS"), ("BEND_UP_90_R2", 1, "DASHDOT"), ("HOLES_D3.2", 3, "CONTINUOUS"),
                      ("HOLE_D11_CABLE", 6, "CONTINUOUS"), ("LETTER_FIX_POINTS", 4, "CONTINUOUS"),
                      ("SHEET_2000x4000", 8, "DASHED"), ("TEXT", 2, "CONTINUOUS")):
    doc.layers.add(name, color=col, linetype=lt)


def part(p, ox, oy):
    F = D.flat_size(p["len"])[0]
    P = lambda u, v: (ox + u, oy + v)
    o = off
    pts = [(o, 0), (F - o, 0), (F - o, SY0), (F, SY0), (F, SY1), (F - o, SY1), (F - o, WF), (o, WF),
           (o, SY1), (0, SY1), (0, SY0), (o, SY0)]
    msp.add_lwpolyline([P(*q) for q in pts], close=True, dxfattribs={"layer": "CUT"})
    for u in (a, F - a):
        msp.add_line(P(u, SY0), P(u, SY1), dxfattribs={"layer": "BEND_UP_90_R2"})
    for v in (a, WF - a):
        msp.add_line(P(off, v), P(F - off, v), dxfattribs={"layer": "BEND_UP_90_R2"})
    span = p["len"] - 100; n = max(1, round(span / 300))
    for v in (7, WF - 7):
        for k in range(n + 1):
            msp.add_circle(P(off + 50 + span * k / n, v), 1.6, dxfattribs={"layer": "HOLES_D3.2"})
    if p is D.LOGO_PART:
        msp.add_circle(P(20, WF - (off + D.D11[1])), 5.5, dxfattribs={"layer": "HOLE_D11_CABLE"})
        for L in D.LETTERS:
            for x, y in L["sp"]:
                u, v = off + x - p["x0"], WF - (off + y)
                msp.add_line(P(u - 6, v), P(u + 6, v), dxfattribs={"layer": "LETTER_FIX_POINTS"})
                msp.add_line(P(u, v - 6), P(u, v + 6), dxfattribs={"layer": "LETTER_FIX_POINTS"})
    msp.add_text(f"P{p['no']}  {p['len']} - flat {F:.1f} x {WF:.1f} - Al 2 mm - FACE OUT",
                 height=40, dxfattribs={"layer": "TEXT"}).set_placement(P(F / 2, WF / 2), align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)
    return F


# nesting kaip lape 2: ilgiausios pirmos, po 2 per lapo aukštį
by = sorted(D.PARTS, key=lambda p: -p["len"])
sheets = []
for p in by:
    for sh in sheets:
        if len(sh) < 2:
            sh.append(p); break
    else:
        sheets.append([p])
for si, sh in enumerate(sheets):
    sx = si * 4600
    msp.add_lwpolyline([(sx, 0), (sx + 4000, 0), (sx + 4000, 2000), (sx, 2000)], close=True, dxfattribs={"layer": "SHEET_2000x4000"})
    msp.add_text(f"SHEET {si + 1} - Al 2000 x 4000 x 2", height=60, dxfattribs={"layer": "TEXT"}).set_placement((sx, 2080))
    for li, p in enumerate(sh):
        part(p, sx + D.EDGE_M, D.EDGE_M + li * (WF + D.EDGE_M))
msp.add_text("Clas Ohlson Horten 3 - flat patterns 1:1 mm | R2 K0.44 BD 3.48 | all bends 90 up | fixing holes D3.2, 7 from edge",
             height=50, dxfattribs={"layer": "TEXT"}).set_placement((0, -150))
doc.saveas(OUT)
print("sheets", [[p["no"] for p in sh] for sh in sheets])
