"""TEST „Bandymas" L 3500 - P6 ant FOLDED fono 3900 x 1000 x 40 (v319, Rytis 2026-10-16: „duok testą kaip ant folded plate P6").
Vienas vientisas DXF (v326: per bendrą scripts/p6_folded.py):
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
import patikra_dxf  # noqa: E402

S = 1.4077823 * 25.4 / 72                       # mm / pt (kliento failas 1:1,4078)
W, H, DEPTH, T = 3900, 1000, 40, 2
FL = DEPTH - T                                  # flanšas nuo lenkimo linijos
pg = fitz.open(os.path.join(HERE, "Bandymas_folded_client.pdf"))[0]
dr = pg.get_drawings()
PL = next(d["rect"] for d in dr if d["fill"] and d["fill"][0] < 0.1)          # fonas
LT = next(d["rect"] for d in dr if d["fill"] and d["fill"][0] > 0.9)          # raidės

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
# v326: išklotinė + raidžių vieta / skylės + raidės - BENDRAS scripts/p6_folded.py (ne projekto kodas)
import p6_folded as P6F  # noqa: E402
out = os.path.join(HERE, "TEST_Bandymas_folded_combined.dxf")
n = P6F.combine(glob.glob(os.path.join(HERE, "dxf", "*_P6_1-1_*.dxf"))[0], W, H, DEPTH, (LT.x0 - PL.x0) * S, (PL.y1 - LT.y1) * S,
                out, cable_edge=CAB_EDGE, t=T)
msp = ezdxf.readfile(out).modelspace()
b = bbox.extents(msp.query('*[layer=="LETTER_POSITION"]'))
print(f"OK {os.path.basename(out)}: raidžių vieta x {b.extmin.x - FL:.0f}..{b.extmax.x - FL:.0f}, y {b.extmin.y - FL:.0f}..{b.extmax.y - FL:.0f} "
      f"(nuo lenkimo linijos), {n}, patikra: {patikra_dxf.check(out) or 'OK'}")
