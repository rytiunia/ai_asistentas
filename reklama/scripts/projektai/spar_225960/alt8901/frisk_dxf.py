"""ALT8901 lapas 18 FRISK & SUNN: vienas DXF - folded fonas 3000 x 1000 x 33 (Alu 2, RAL 9005) išklotinė (v302 viršus / apačia
į vidų, Ø3,2 į L 30x30x2: 50 + 10 x 290, 7 mm nuo krašto, viršus + apačia), raidžių / P1 padėtis fone (sluoksnis
LETTER_POSITION, FACE OUT) + P6 raidžių ir P1 apskritimo kontūrai (p6_dxf blokai, dešinėje).
Raidžių / P1 tvirtinimas prie fono ir D11 vieta lape nenurodyti - skylių nededama (klausti)."""
import os, sys
import ezdxf, pymupdf as fitz
from ezdxf.addons import Importer
from ezdxf.math import Matrix44
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
import patikra_dxf
import kreives as KR  # noqa: E402
import kiti_dxf as K

S = 20 * 25.4 / 72
pg = fitz.open("svarus_s18_frisk.pdf")[0]
dr = pg.get_drawings()
BG = next(d for d in dr if K.near(d["fill"], (0.05, 0.05, 0.06)))["rect"]
W, H, DEP, T = 3000, 1000, 33, 2
FL = DEP - T
doc = K.new_doc(K.LAY + [("LETTER_POSITION", 6, "DASHED")]); msp = doc.modelspace()
span = W - 100
xs = [50 + span * k / 10 for k in range(11)]
F, WF = K.flat(msp, 0, 0, W, H, DEP, T, "screw", "screw", xs, "BACKGROUND - box lid 33")
# raidžių / P1 padėtis (lapo FRONT VIEW, mm nuo fono kairio apatinio kampo, + atlankas)
items = K.vec_paths(pg, fitz.Rect(0, 0, 2000, 2000), lambda d: not K.near(d["fill"], (0.05, 0.05, 0.06)))
n = 0
for fill, col, ps in items:
    for p in ps:
        pts = [((q.x - BG.x0) * S + FL, (BG.y1 - q.y) * S + FL) for q in p.flattening(0.05 / S)]
        if len(pts) > 2:
            msp.add_lwpolyline(KR.fit(pts, True, max(KR.TOL, 0.01 * S)), format="xyb", close=True,
                               dxfattribs={"layer": "LETTER_POSITION"}); n += 1             # v316: lankais
ox = F + 400
for fn, tag in (("dxf_s18a/ALT8901_10.16_RS_s18_frisk_P6_P6_1-1.dxf", "P6"), ("dxf_s18b/ALT8901_10.16_RS_s18_frisk_P1_P6_1-1.dxf", "P1")):
    src = ezdxf.readfile(fn); imp = Importer(src, doc)
    imp.import_modelspace(); imp.finalize()
    from ezdxf import bbox
    new = [e for e in msp if e.dxftype() == "INSERT" and not e.has_xdata("ALT")]   # ką tik importuoti (blokai gali būti pervadinti)
    for e in new:
        e.set_xdata("ALT", [(1000, tag)])
    b = bbox.extents(new)
    T_ = Matrix44.translate(ox - b.extmin.x, 0 - b.extmin.y, 0)
    for e in new:
        e.transform(T_)
    ox += b.size.x + 300
out = "out/ALT8901_10.16_RS_s18_frisk_sunn.dxf"
KR.saveas(doc, out)
print(f"OK {out}: fonas FLAT {F:.0f} x {WF:.0f}, L skylės 2 x 11, padėties kontūrų {n}, {patikra_dxf.check(out) or 'mm OK'}")
