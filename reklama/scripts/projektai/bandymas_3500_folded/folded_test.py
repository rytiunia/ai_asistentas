"""TEST „Bandymas" L 3500 - P6 ant FOLDED fono 3900 x 1000 x 40 (v319, Rytis 2026-10-16: „duok testą kaip ant folded plate P6").
Vienas vientisas DXF:
  - kairėje - fono išklotinė (folded_dxf.py, v173: 3976 x 1076, sides inside, Ø3.2 L tvirtinimui 7 mm nuo krašto), FACE OUT;
    ant jos raidžių vietos (LETTER_POSITION, dugno kontūras) ir per foną einančios skylės TOSE PAČIOSE vietose kaip raidžių
    dugne: LETTER_FIX_D3.2 (raidė prie fono - kvadrato / trikampio principu), HOLE_D11_CABLE (laidas pro foną),
    DRAIN_D8 (drenažas - skylutė, ant folded lieka skylutės);
  - dešinėje - P6 raidės (p6_dxf --folded: 1_PRIEKIS, 2_GALAS su D3.2 / D11 / Ø8 skylutėmis).
Laido Ø11 skylė fono briaunoje - 15 mm nuo lenkimo linijos ir 15 mm nuo viršaus (v321). Raidės prie fono tvirtinamos
gamyboje pagal faktą - esminis skylių atitikimas raidėse ir fone (v321).
python3 folded_test.py   (viskas: p6_dxf --folded, lapas, išklotinė, vientisas DXF)"""
import glob
import os
import sys

import ezdxf
import pymupdf as fitz
from ezdxf import bbox

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
import kreives as KR  # noqa: E402
import patikra_dxf  # noqa: E402

S = 1.4077823 * 25.4 / 72                       # mm / pt (kliento failas 1:1,4078)
W, H, DEPTH, T = 3900, 1000, 40, 2
FL = DEPTH - T                                  # flanšas nuo lenkimo linijos
pg = fitz.open(os.path.join(HERE, "Bandymas_folded_client.pdf"))[0]
dr = pg.get_drawings()
PL = next(d["rect"] for d in dr if d["fill"] and d["fill"][0] < 0.1)          # fonas
LT = next(d["rect"] for d in dr if d["fill"] and d["fill"][0] > 0.9)          # raidės
OX, OY = FL + (LT.x0 - PL.x0) * S, FL + (PL.y1 - LT.y1) * S                  # raidžių apačia-kairė išklotinėje

doc = ezdxf.new("R2010", setup=True)
doc.header["$PROJECTNAME"] = "--drain-hole"     # v319: P6 ant folded - drenažas skylutė (patikra_dxf DRENAŽAS SKYLUTE netaiko)
msp = doc.modelspace()
for ly, col, lt in (("CUT", 7, "CONTINUOUS"), ("BEND_UP_90", 1, "DASHED"), ("HOLES_D3.2", 3, "CONTINUOUS"),
                    ("LETTER_POSITION", 6, "DASHED"), ("LETTER_FIX_D3.2", 3, "CONTINUOUS"), ("HOLE_D11_CABLE", 1, "CONTINUOUS"),
                    ("DRAIN_D8", 5, "CONTINUOUS"), ("TEXT", 7, "CONTINUOUS")):
    if ly not in doc.layers:
        doc.layers.add(ly, color=col, linetype=lt)
# v321: pilna eiga - p6_dxf (raidės) -> spec "cable" (D11 raidėje, Ø11 briaunoje 15 / 15) -> lapas -> išklotinė -> vientisas DXF
import json  # noqa: E402
import re  # noqa: E402
import subprocess  # noqa: E402
SCR = os.path.join(HERE, "..", "..")
r_ = subprocess.run(["python3", os.path.join(SCR, "p6_dxf.py"), "Bandymas_folded_client.pdf", "dxf", "--scale", "1.4077823",
                     "--fill", "1,1,1", "--rails-json", "axes.json", "--folded", "--no-letters", "--prefix", "TEST_Bandymas_folded",
                     "--cable", "bottom"], cwd=HERE, capture_output=True, text=True)
d11 = [(float(a), float(b)) for a, b in re.findall(r"L01: .*D11 \w+: \(([\d.]+); ([\d.]+)\)", r_.stdout)][0]
CAB_EDGE = "left"                                    # kliento laido išvestis - kairėje (žiūrint iš priekio)
sp = json.load(open(os.path.join(HERE, "spec.json")))
sp.pop("cable_exit", None)
sp["cable"] = {"d11_mm": [round((LT.x0 - PL.x0) * S + d11[0]), round((LT.y1 - PL.y0) * S - d11[1])], "letter": "letter B",
               "edge": CAB_EDGE, "edge_mm": 15, "label": "12V, 3 m -> trafo box (220V)"}
json.dump(sp, open(os.path.join(HERE, "spec.json"), "w"), indent=1, ensure_ascii=False)
subprocess.run(["python3", os.path.join(SCR, "braizyti_lapa.py"), "spec.json", "TEST_Bandymas_folded.pdf"], cwd=HERE,
               capture_output=True, text=True, check=True)
subprocess.run(["python3", os.path.join(SCR, "folded_dxf.py"), str(W), str(H), "flat.dxf", str(DEPTH), f"--cable-edge={CAB_EDGE}"],
               cwd=HERE, capture_output=True, text=True, check=True)
flat = ezdxf.readfile(os.path.join(HERE, "flat.dxf"))
for e in flat.modelspace():
    c = e.copy()
    msp.add_entity(c)

p6 = ezdxf.readfile(glob.glob(os.path.join(HERE, "dxf", "*_P6_1-1_*.dxf"))[0])
ents = [x for e in p6.modelspace() for x in (e.virtual_entities() if e.dxftype() == "INSERT" else [e])]
n = {"pos": 0, "fix": 0, "d11": 0, "drain": 0}
for e in ents:
    if e.dxf.layer != "2_GALAS":
        continue
    if e.dxftype() == "LWPOLYLINE":
        pts = [(x + OX, y + OY, b) for x, y, *_, b in e.get_points("xyseb")]
        msp.add_lwpolyline(pts, format="xyb", close=e.closed, dxfattribs={"layer": "LETTER_POSITION"}); n["pos"] += 1
    elif e.dxftype() == "CIRCLE":
        r = e.dxf.radius
        lay, k = ("LETTER_FIX_D3.2", "fix") if r < 2 else ("DRAIN_D8", "drain") if r < 4.5 else ("HOLE_D11_CABLE", "d11")
        msp.add_circle((e.dxf.center.x + OX, e.dxf.center.y + OY), r, dxfattribs={"layer": lay}); n[k] += 1
# P6 raidės - dešinėje nuo išklotinės
X0 = W + 2 * FL + 300
for e in ents:
    c = e.copy()
    c.translate(X0, 0, 0)
    msp.add_entity(c)
msp.add_text("FOLDED BACKGROUND 3900 x 1000 x 40, Alu 2 mm - FLAT, FACE OUT; holes LETTER_FIX / D11 / DRAIN = letter back",
             height=25, dxfattribs={"layer": "TEXT"}).set_placement((0, -200))
msp.add_text("P6 LETTERS (1_PRIEKIS face, 2_GALAS back -3 mm)", height=25, dxfattribs={"layer": "TEXT"}).set_placement((X0, -200))
out = os.path.join(HERE, "TEST_Bandymas_folded_combined.dxf")
KR.saveas(doc, out)
b = bbox.extents(msp.query('*[layer=="LETTER_POSITION"]'))
print(f"OK {os.path.basename(out)}: raidžių vieta x {b.extmin.x - FL:.0f}..{b.extmax.x - FL:.0f}, y {b.extmin.y - FL:.0f}..{b.extmax.y - FL:.0f} "
      f"(nuo lenkimo linijos), {n}, patikra: {patikra_dxf.check(out) or 'OK'}")
