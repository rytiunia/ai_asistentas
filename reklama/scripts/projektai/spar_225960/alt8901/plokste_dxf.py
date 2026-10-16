"""ALT8901 KAFFEPAUSE: kompozito plokštė (apskritimas + rėmo atkartojimas, ACM 3 mm juoda) iš patvirtinto lapo -> į to lapo
P6 DXF atskiru BLOCK / sluoksniu 4_PLOKSTE_ACM3 (ta pati koordinačių sistema kaip raidžių PRIEKIS: nuo raidžių min x, y aukštyn).
Tvirtinimo skylių plokštėje lape nėra - nededama (klausti).
python3 plokste_dxf.py <svarus.pdf> <plates.json> <scale N> <in.dxf>"""
import json, sys
import os
import ezdxf, pymupdf as fitz
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
import kreives as KR  # noqa: E402
from ezdxf.math import BSpline  # noqa
src, pj, N, fn = sys.argv[1], sys.argv[2], float(sys.argv[3]), sys.argv[4]
S = N * 25.4 / 72
pg = fitz.open(src)[0]
L = fitz.Rect()
for d in pg.get_drawings():
    L.include_rect(d["rect"])
doc = ezdxf.readfile(fn)
assert doc.header.get("$INSUNITS") == 4
X = lambda x: (x - L.x0) * S
Y = lambda y: (L.y1 - y) * S
blk = doc.blocks.new("PLOKSTE")
if "4_PLOKSTE_ACM3" not in doc.layers:
    doc.layers.add("4_PLOKSTE_ACM3", color=5)
for pl in json.load(open(pj)):
    pts = []
    for it in pl["items"]:
        if it[0] == "l":
            a, b = it[1], it[2]
            if not pts:
                pts.append((X(a[0]), Y(a[1])))
            pts.append((X(b[0]), Y(b[1])))
        elif it[0] == "c":
            p0, p1, p2, p3 = it[1:5]
            if not pts:
                pts.append((X(p0[0]), Y(p0[1])))
            for k in range(1, 17):
                t = k / 16; u = 1 - t
                x = u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0]
                y = u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1]
                pts.append((X(x), Y(y)))
    blk.add_lwpolyline(KR.fit(pts, True, max(KR.TOL, 0.01 * S)), format="xyb", close=True,
                       dxfattribs={"layer": "4_PLOKSTE_ACM3"})                       # v316 (v313): lankais
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    print(f"plokštė {max(xs) - min(xs):.0f} x {max(ys) - min(ys):.0f} mm, x {min(xs):.0f}..{max(xs):.0f}, y {min(ys):.0f}..{max(ys):.0f}")
doc.modelspace().add_blockref("PLOKSTE", (0, 0), dxfattribs={"layer": "4_PLOKSTE_ACM3"})
KR.saveas(doc, fn)
