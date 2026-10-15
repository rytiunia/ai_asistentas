#!/usr/bin/env python3
"""1:1 PDF (braizyti_begeliai `_1-1.pdf`, OCG sluoksniai) -> CAD DXF mm, y aukštyn (v273, Rytis 2026-10-15: „pateik ... cad failą").
Kiekvienas PDF sluoksnis -> to paties pavadinimo DXF sluoksnis; uždari kontūrai - LWPOLYLINE (kreivės išskaidomos, tol mm),
apskritimai (4 Bezier lankai) - CIRCLE, linijos - LINE. Papildomai `--merge other.dxf:LAYER1,LAYER2` - perkelti sluoksnius
iš kito DXF (pvz. griovelis_b GROOVE_8MM / CENTERLINE), jei jo koordinatės tos pačios (mm, y aukštyn, tas pats nulis).
Naudojimas: python3 pdf1to1_dxf.py in_1-1.pdf out.dxf [--tol=0.05] [--merge f.dxf:L1,L2]"""
import math
import sys

import ezdxf
import pymupdf as fitz

PT = 25.4 / 72


def bez(p0, p1, p2, p3, n):
    return [((1 - t) ** 3 * p0.x + 3 * (1 - t) ** 2 * t * p1.x + 3 * (1 - t) * t * t * p2.x + t ** 3 * p3.x,
             (1 - t) ** 3 * p0.y + 3 * (1 - t) ** 2 * t * p1.y + 3 * (1 - t) * t * t * p2.y + t ** 3 * p3.y)
            for t in [i / n for i in range(1, n + 1)]]


def main(a):
    src, out = a[0], a[1]
    tol = float(next((x.split("=")[1] for x in a if x.startswith("--tol=")), 0.05))
    merge = next((a[i + 1] for i, x in enumerate(a) if x == "--merge"), None)
    pg = fitz.open(src)[0]
    H = pg.rect.height
    M = lambda x, y: (x * PT, (H - y) * PT)
    doc = ezdxf.new("R2010", setup=True)
    doc.units = ezdxf.units.MM
    msp = doc.modelspace()
    cnt = {}
    for d in pg.get_drawings():
        lay = (d.get("layer") or "0").replace("?", "X")
        if lay not in doc.layers:
            doc.layers.add(lay)
        subs, cur = [], []
        for it in d["items"]:
            if it[0] == "re":
                r = it[1]
                subs.append(([(r.x0, r.y0), (r.x1, r.y0), (r.x1, r.y1), (r.x0, r.y1)], True, 0)); cur = []
                continue
            p0 = it[1]
            if not cur or abs(cur[-1][0] - p0.x) > 1e-6 or abs(cur[-1][1] - p0.y) > 1e-6:
                if len(cur) > 1:
                    subs.append((cur, False, ncur))
                cur, ncur = [(p0.x, p0.y)], 0
            if it[0] == "l":
                cur.append((it[2].x, it[2].y))
            elif it[0] == "c":
                L = math.dist((p0.x, p0.y), (it[4].x, it[4].y)) * PT
                n = max(2, min(64, int(math.sqrt(max(L, 0.1) / max(tol, 1e-3)) * 2)))
                cur += bez(p0, it[2], it[3], it[4], n); ncur += 1
        if len(cur) > 1:
            subs.append((cur, False, ncur))
        for pts, closed, nc in subs:
            closed = closed or math.dist(pts[0], pts[-1]) < 1e-3
            xs, ys = [p[0] for p in pts], [p[1] for p in pts]
            w, h = max(xs) - min(xs), max(ys) - min(ys)
            if closed and nc == 4 and abs(w - h) < 0.02 * max(w, h, 1e-6):     # apskritimas
                c = M((max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2)
                msp.add_circle(c, w * PT / 2, dxfattribs={"layer": lay}); cnt[lay] = cnt.get(lay, 0) + 1
                continue
            q = [M(*p) for p in pts]
            if closed and math.dist(q[0], q[-1]) < 1e-3:
                q = q[:-1]
            if len(q) == 2 and not closed:
                msp.add_line(q[0], q[1], dxfattribs={"layer": lay})
            else:
                msp.add_lwpolyline(q, close=closed, dxfattribs={"layer": lay})
            cnt[lay] = cnt.get(lay, 0) + 1
    if merge:
        f_, lays = merge.split(":")
        sd = ezdxf.readfile(f_)
        for e in sd.modelspace():
            if e.dxf.layer in lays.split(","):
                if e.dxf.layer not in doc.layers:
                    doc.layers.add(e.dxf.layer)
                msp.add_foreign_entity(e.copy()) if hasattr(msp, "add_foreign_entity") else msp.add_entity(e.copy())
                cnt[e.dxf.layer] = cnt.get(e.dxf.layer, 0) + 1
    doc.saveas(out)
    print("OK", out, cnt)


if __name__ == "__main__":
    main(sys.argv[1:])
