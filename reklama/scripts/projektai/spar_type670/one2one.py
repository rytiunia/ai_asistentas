import pymupdf as fitz, sys
from shapely.geometry import Polygon
src = fitz.open(sys.argv[2] if len(sys.argv) > 2 else 'frisk670_client.pdf')[0]; D = src.get_drawings()
X0, Y0 = 53.9, 341.5; S = 3600 / (1074.4 - 53.9); k = 72 / 25.4
PW, PH, J = 3600, 670, [1500]
doc = fitz.open(); pg = doc.new_page(width=PW * k, height=PH * k)
L1, L2, L3 = doc.add_ocg("1_LETTERS"), doc.add_ocg("2_BACK_inset_3mm"), doc.add_ocg("3_FRAME")
def P(p): return fitz.Point((p.x - X0) * S * k, (p.y - Y0) * S * k)
def M(x, y): return fitz.Point(x * k, y * k)
sh = pg.new_shape()   # 1 - plokštės dalys + raidės / apskritimas (kliento kreivės)
for a, b in zip([0] + J, J + [PW]):
    sh.draw_rect(fitz.Rect(M(a, 0), M(b, PH)))
sh.finish(width=0.1, color=(0, 0, 0), fill=None, oc=L1); sh.commit()
polys = []
for g in D[1:]:
    sh = pg.new_shape(); rings, cur = [], []
    last = None
    for it in g['items']:
        if it[0] == 're':
            r_ = it[1]; q = [P(r_.tl), P(r_.tr), P(r_.br), P(r_.bl)]
            sh.draw_polyline(q + [q[0]])
            if cur: rings.append(cur)
            rings.append(q); cur = []; last = None
            continue
        if it[0] == 'l':
            a, b = P(it[1]), P(it[2]); sh.draw_line(a, b)
            if last is None or abs(a.x-last.x)+abs(a.y-last.y) > 1e-3:
                if cur: rings.append(cur)
                cur = [a]
            cur.append(b); last = b
        elif it[0] == 'c':
            a = P(it[1]); q = [P(it[i]) for i in (2, 3, 4)]; sh.draw_bezier(a, *q)
            if last is None or abs(a.x-last.x)+abs(a.y-last.y) > 1e-3:
                if cur: rings.append(cur)
                cur = [a]
            for i in range(1, 17):
                t = i / 16
                cur.append(fitz.Point(*[(1-t)**3*a_[j] + 3*(1-t)**2*t*q[0][j] + 3*(1-t)*t*t*q[1][j] + t**3*q[2][j]
                                        for j, a_ in [(0, a), (1, a)]]))
            last = q[2]
    if cur: rings.append(cur)
    sh.finish(width=0.1, color=(0, 0, 0), fill=None, closePath=False, oc=L1); sh.commit()
    geo = None
    for r in rings:
        if len(r) >= 3:
            p_ = Polygon([(q.x, q.y) for q in r]).buffer(0)
            geo = p_ if geo is None else geo.symmetric_difference(p_)
    polys.append(geo)
for geo in polys:      # 2 - dugnas 3 mm į vidų
    bk = geo.buffer(-3 * k, join_style=2, mitre_limit=10)
    sh = pg.new_shape()
    for pl in getattr(bk, 'geoms', [bk]):
        for ring in [pl.exterior] + list(pl.interiors):
            sh.draw_polyline([fitz.Point(*c) for c in ring.coords])
    sh.finish(width=0.1, color=(0.85, 0, 0), fill=None, closePath=True, oc=L2); sh.commit()
sh = pg.new_shape()    # 3 - L profiliai (vaizdas iš priekio, punktyrinė padėtis) + D11
for a, b in zip([0] + J, J + [PW]):
    for y0 in (2, PH - 32):
        sh.draw_rect(fitz.Rect(M(a + 25, y0), M(b - 25, y0 + 30)))
sh.draw_circle(M(600, 160), 5.5 * k)   # D11 po raide F
sh.finish(width=0.1, color=(0, 0.35, 0.85), fill=None, oc=L3); sh.commit()
doc.set_metadata({"title": "SPAR TYPE 670 FRISK & SUNN 1:1"})
doc.save(sys.argv[1], garbage=3, deflate=True); print("OK", sys.argv[1])
