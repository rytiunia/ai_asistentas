#!/usr/bin/env python3
"""Centerline per raidžių ploto vidurį (v149): skeletas -> šakelių valymas -> galai tiesiai į ploto vidurį (ne į kampą) ->
mazgų zonos nukerpamos (R = 2 x pusplotis), tiesiausiai tęsiančios šakos sujungiamos Hermite kreive (kryžiuje - 2 poros),
kitos - T jungtimi; išlyginimas; DXF CENTERLINE (SPLINE) + OUTLINE, PDF peržiūra.
Naudojimas: python3 centerline.py kontūrai.pdf out  (-> out.dxf, out.pdf)
-> šakelių valymas -> grandinės -> išlyginimas (Gauss) -> supaprastinimas -> DXF (LWPOLYLINE) + PDF peržiūra."""
import sys
import numpy as np
import pymupdf as fitz
import networkx as nx
from shapely.geometry import Polygon
from shapely.ops import unary_union
from skimage.morphology import skeletonize
from scipy.ndimage import distance_transform_edt, gaussian_filter1d
import cv2

SRC, OUT = sys.argv[1], sys.argv[2]
PX = 3.0                                  # px / pt
page = fitz.open(SRC)[0]
d = page.get_drawings()[0]


def subpaths(d, n=16):
    S, cur, last = [], [], None
    for it in d["items"]:
        a = it[1]
        if last is None or abs(a.x - last.x) > 1e-3 or abs(a.y - last.y) > 1e-3:
            if len(cur) > 2:
                S.append(cur)
            cur = [(a.x, a.y)]
        if it[0] == "l":
            cur.append((it[2].x, it[2].y)); last = it[2]
        elif it[0] == "c":
            p0, p1, p2, p3 = it[1:5]
            for k in range(1, n + 1):
                t = k / n
                cur.append(((1-t)**3*p0.x + 3*(1-t)**2*t*p1.x + 3*(1-t)*t*t*p2.x + t**3*p3.x,
                            (1-t)**3*p0.y + 3*(1-t)**2*t*p1.y + 3*(1-t)*t*t*p2.y + t**3*p3.y))
            last = p3
    if len(cur) > 2:
        S.append(cur)
    return S


rings = [Polygon(s).buffer(0) for s in subpaths(d)]
geom = None
for r in rings:                            # even-odd
    geom = r if geom is None else geom.symmetric_difference(r)
x0, y0, x1, y1 = geom.bounds
pad = 10
W, H = int((x1 - x0 + 2 * pad) * PX), int((y1 - y0 + 2 * pad) * PX)
img = np.zeros((H, W), np.uint8)
toPx = lambda x, y: ((x - x0 + pad) * PX, (y - y0 + pad) * PX)
for g in getattr(geom, "geoms", [geom]):
    ext = np.array([toPx(*p) for p in g.exterior.coords], np.int32)
    cv2.fillPoly(img, [ext], 1, lineType=cv2.LINE_8)
    for h in g.interiors:
        cv2.fillPoly(img, [np.array([toPx(*p) for p in h.coords], np.int32)], 0)
dist = distance_transform_edt(img)
sk = skeletonize(img > 0)
ys, xs = np.nonzero(sk)
G = nx.Graph()
pts = set(zip(ys.tolist(), xs.tolist()))
for (y, x) in pts:
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if (dy or dx) and (y + dy, x + dx) in pts:
                G.add_edge((y, x), (y + dy, x + dx), w=np.hypot(dy, dx))
# triangulų (8-kaimynystės) sutraukimas: įstrižai, kai yra stačia jungtis
for (a, b) in list(G.edges()):
    if abs(a[0] - b[0]) == 1 and abs(a[1] - b[1]) == 1:
        if (a[0], b[1]) in pts or (b[0], a[1]) in pts:
            G.remove_edge(a, b)


def prune(G, factor=2.6, rounds=8):
    """šakelės nuo galo iki mazgo, trumpesnės už vietinį plotį x factor - šalinamos"""
    for _ in range(rounds):
        removed = False
        for e in [n for n in G.nodes if G.degree(n) == 1]:
            if e not in G or G.degree(e) != 1:
                continue
            path, cur, prev = [e], e, None
            while True:
                nb = [n for n in G.neighbors(cur) if n != prev]
                if len(nb) != 1 or G.degree(cur) > 2 and cur != e:
                    break
                prev, cur = cur, nb[0]
                path.append(cur)
                if G.degree(cur) != 2:
                    break
            if G.degree(path[-1]) >= 3:
                L = sum(np.hypot(a[0] - b[0], a[1] - b[1]) for a, b in zip(path, path[1:]))
                if L < factor * dist[path[-1]]:
                    G.remove_nodes_from(path[:-1]); removed = True
        if not removed:
            break


prune(G)
G.remove_nodes_from([c for comp in list(nx.connected_components(G)) if len(comp) < 15 for c in comp])

# grandinės tarp mazgų (laipsnis != 2)
chains, seen = [], set()
nodes = [n for n in G.nodes if G.degree(n) != 2]
for n in nodes:
    for nb in G.neighbors(n):
        if (n, nb) in seen:
            continue
        path, prev, cur = [n, nb], n, nb
        seen.add((n, nb)); seen.add((nb, n))
        while G.degree(cur) == 2:
            nxt = [m for m in G.neighbors(cur) if m != prev][0]
            seen.add((cur, nxt)); seen.add((nxt, cur))
            prev, cur = cur, nxt
            path.append(cur)
        chains.append(path)
for comp in nx.connected_components(G):                 # uždari kontūrai be mazgų (o, e akys ir pan.)
    if all(G.degree(n) == 2 for n in comp):
        cyc = nx.cycle_basis(G.subgraph(comp))
        if cyc:
            c = cyc[0]; chains.append(c + [c[0]])

# mazgų klasteriai: trumpos grandinės tarp dviejų šakojimosi mazgų (< 1.5 x plotis) sutraukiamos į vieną tašką
par = {}
def fnd(a):
    while par.get(a, a) != a:
        a = par[a]
    return a
keep = []
for c in chains:
    a_, b_ = c[0], c[-1]
    if a_ != b_ and G.degree(a_) >= 3 and G.degree(b_) >= 3:
        L = sum(np.hypot(p[0] - q[0], p[1] - q[1]) for p, q in zip(c, c[1:]))
        if L < 1.5 * max(dist[a_], dist[b_]):
            par[fnd(a_)] = fnd(b_); continue
    keep.append(c)
cl_ = {}
for n in list(par) + [v for v in par.values()]:
    cl_.setdefault(fnd(n), set()).add(n)
cen = {r: tuple(np.mean([np.array(n, float) for n in m], axis=0)) for r, m in cl_.items()}
def to_pt(p):
    return (p[1] / PX + x0 - pad, p[0] / PX + y0 - pad)


# ---------------------------------------------------------------- v2: „rašiklio" linijos
# grandinės: (taškai px [y, x] float, galo žyma: ("J", id) mazgas / ("E", None) laisvas galas / ("L", None) uždara)
def jkey(n):
    if n in par or n in cl_:
        return ("J", fnd(n))
    if n in G and G.degree(n) >= 3:
        return ("J", n)
    return ("E", None)


Jpos = {}
CH = []
for c in keep:
    c = list(c)
    if len(c) > 2 and c[0] == c[-1] and all(G.degree(n) == 2 for n in c[1:-1]) and G.degree(c[0]) == 2:
        CH.append({"p": np.array(c, float), "t": [("L", None), ("L", None)]}); continue
    tg = [jkey(c[0]), jkey(c[-1])]
    for i, t in zip((0, -1), tg):
        if t[0] == "J":
            Jpos[t[1]] = np.array(cen[t[1]] if t[1] in cen else t[1], float)
            c[i] = tuple(Jpos[t[1]])
    if len(c) > 1:
        CH.append({"p": np.array(c, float), "t": tg})


def D(q):
    iy, ix = int(round(q[0])), int(round(q[1]))
    if 0 <= iy < dist.shape[0] and 0 <= ix < dist.shape[1]:
        return dist[iy, ix]
    return 0.0


def arclen(a):
    return np.r_[0, np.cumsum(np.hypot(*np.diff(a, axis=0).T))]


def tangent_at_end(a, L):
    """kryptis iš grandinės vidaus į galą (a[-1]) pagal paskutinį L ilgio ruožą"""
    s = arclen(a); k = np.searchsorted(s, s[-1] - L)
    v = a[-1] - a[max(0, min(k, len(a) - 2))]
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else v


def march(p, v, stop):
    """eina tiesiai kryptimi v, kol stop(q) - grąžina taškų sąrašą"""
    out, q = [], p.copy()
    for _ in range(4000):
        q = q + v * 0.5
        if stop(q):
            break
        out.append(q.copy())
    return out


# 1) laisvi galai: nukerpamas iškreiptas galas (plotis staigiai mažėja - kampas) ir pratęsiama tiesiai į ploto vidurį
for ch in CH:
    for side in (0, 1):
        if ch["t"][side][0] != "E":
            continue
        a = ch["p"] if side == 1 else ch["p"][::-1]
        s = arclen(a); Ltot = s[-1]
        wd = np.array([D(q) for q in a])
        wm = float(np.median(wd))
        # nuo galo atgal: kol plotis < 0.8 mediana (ne daugiau 45 % grandinės ir 2.5 pločio)
        k = len(a) - 1
        lim = max(Ltot - min(0.45 * Ltot, 2.5 * wm), 0)
        while k > 1 and s[k] > lim and wd[k] < 0.8 * wm:
            k -= 1
        a2 = a[:k + 1]
        v = tangent_at_end(a2, min(1.2 * wm, 0.3 * s[k] + 1))
        w0 = max(D(a2[-1]), 1.0)
        ext = march(a2[-1], v, lambda q: D(q) < 0.8 * w0)
        a3 = np.vstack([a2] + ([np.array(ext)] if ext else []))
        ch["p"] = a3 if side == 1 else a3[::-1]

# 2) mazgai: šakos nukerpamos R = 1.4 x pusplotis nuo mazgo; dvi tiesiausiai tęsiančios - sujungiamos Hermite kreive,
#    kitos - tiesiai iki sujungtos kreivės (T jungtis)
def hermite(p0, t0, p1, t1, n=40):
    L = np.linalg.norm(p1 - p0)
    t = np.linspace(0, 1, n)[:, None]
    h00, h10, h01, h11 = 2*t**3 - 3*t**2 + 1, t**3 - 2*t**2 + t, -2*t**3 + 3*t**2, t**3 - t**2
    return h00 * p0 + h10 * t0 * L + h01 * p1 + h11 * t1 * L


ends = {}                                   # J -> [(ch_idx, side)]
for i, ch in enumerate(CH):
    for side in (0, 1):
        if ch["t"][side][0] == "J":
            ends.setdefault(ch["t"][side][1], []).append((i, side))
links = {}                                  # (i, side) -> (j, side2, bridge pts)
tees = []                                   # (i, side, J)
for J, br in ends.items():
    P = Jpos[J]; R = 2.0 * max(D(P), 2.0)
    info = []
    for (i, side) in br:
        a = CH[i]["p"] if side == 0 else CH[i]["p"][::-1]      # a[0] = mazgas
        d = np.hypot(*(a - P).T)
        k = int(np.argmax(d > R)) if (d > R).any() else len(a) - 1
        k = min(max(k, 1), len(a) - 2) if len(a) > 3 else len(a) - 1
        rest = a[k:]
        wl = max(float(np.median([D(q) for q in rest])), 2.0)
        v = rest[0] - rest[min(len(rest) - 1, max(2, int(1.5 * wl)))]   # kryptis į mazgą
        v = v / (np.linalg.norm(v) or 1)
        new = rest if side == 0 else rest[::-1]
        CH[i]["p"] = new
        info.append((i, side, rest[0], v))
    used = set()
    cand = []
    for x in range(len(info)):
        for y in range(x + 1, len(info)):
            if info[x][0] == info[y][0] and len(info) > 2:
                continue
            cand.append((float(np.dot(info[x][3], -info[y][3])), x, y))
    for dot, x, y in sorted(cand, reverse=True):          # godus porinimas: kryžiuje (t) - 2 poros
        if x in used or y in used:
            continue
        if dot < (-0.2 if not used else 0.3):
            continue
        i1, s1, p1, v1 = info[x]; i2, s2, p2, v2 = info[y]
        br_ = hermite(p1, v1, p2, -v2)
        links[(i1, s1)] = (i2, s2, br_); links[(i2, s2)] = (i1, s1, br_[::-1])
        used |= {x, y}
    for z, (i, side, p, v) in enumerate(info):
        if z not in used:
            tees.append((i, side, p, v, J, R))

# 3) sujungimas į ilgas linijas per links
done = set(); strokes = []
def piece(i, side_in):
    a = CH[i]["p"]
    return a if side_in == 0 else a[::-1]
for i in range(len(CH)):
    if i in done:
        continue
    # rasti pradžią: eiti atgal, kol nėra link
    cur, side = i, 0
    seen_ = {i}
    while (cur, side) in links:
        j, s2, _ = links[(cur, side)]
        if j in seen_:
            break
        seen_.add(j); cur, side = j, 1 - s2
    start = (cur, side)
    pts, cur, side_in = [], cur, side
    closed = False
    while True:
        done.add(cur)
        seg = piece(cur, side_in)
        pts.append(seg)
        out_side = 1 - side_in
        if (cur, out_side) not in links:
            break
        j, s2, brg = links[(cur, out_side)]
        if j in done:
            pts.append(brg); closed = True
            break
        pts.append(brg)
        cur, side_in = j, s2
    strokes.append({"p": np.vstack(pts), "closed": closed or CH[i]["t"][0][0] == "L"})

# 4) išlyginimas (galai fiksuoti), T šakos pritraukiamos prie išlygintos pagrindinės linijos
def smooth2(a, closed):
    if len(a) < 6:
        return a
    s = arclen(a); n = max(int(s[-1] / 1.0), 6)
    u = np.linspace(0, s[-1], n)
    a = np.c_[np.interp(u, s, a[:, 0]), np.interp(u, s, a[:, 1])]
    wm = float(np.median([D(q) for q in a]))
    sig = max(3.0, 0.9 * wm)
    mode = "wrap" if closed else "nearest"
    b = np.c_[gaussian_filter1d(a[:, 0], sig, mode=mode), gaussian_filter1d(a[:, 1], sig, mode=mode)]
    if not closed:
        k = np.clip(np.minimum(np.arange(n), np.arange(n)[::-1]) / (2 * sig), 0, 1)[:, None]
        b = a * (1 - k) + b * k
        b = np.c_[gaussian_filter1d(b[:, 0], sig / 2, mode="nearest"), gaussian_filter1d(b[:, 1], sig / 2, mode="nearest")]
        b[0], b[-1] = a[0], a[-1]
    return b


for st in strokes:
    st["s"] = smooth2(st["p"], st["closed"])
allS = [st["s"] for st in strokes]
for (i, side, p, v, J, R) in tees:
    own = None
    for st in strokes:
        if np.hypot(*(st["s"] - p).T).min() < 1.5:
            own = st; break
    if own is None:
        continue
    vv = -v                                         # kryptis nuo šakos galo į mazgą (tęsinys)
    vv = v
    best = None
    for st in strokes:
        A = st["s"]
        rel = A - p
        dp = np.hypot(*rel.T)
        proj = rel @ vv
        perp = np.abs(rel[:, 0] * vv[1] - rel[:, 1] * vv[0])
        ok = (dp > 0.6 * R) & (proj > 0) & (dp < 3.0 * R)
        if st is own:                               # savo linijoje - tik toli nuo šakos (pvz. e skersinis)
            k0 = int(np.argmin(np.hypot(*(A - p).T)))
            s_ = arclen(A); ok &= np.abs(s_ - s_[k0]) > 3 * R
        if not ok.any():
            continue
        sc = np.where(ok, perp + 0.15 * dp, np.inf)
        k = int(np.argmin(sc))
        if best is None or sc[k] < best[0]:
            best = (sc[k], A[k], st, k)
    if best is None:
        continue
    _, tgt, st2, k = best
    A = st2["s"]
    tdir = A[min(k + 1, len(A) - 1)] - A[max(k - 1, 0)]
    tdir = tdir / (np.linalg.norm(tdir) or 1)
    # galas įeina į pagrindinę liniją jos kryptimi (be „laiptelio"), pusė parenkama pagal šakos kryptį
    if np.dot(tdir, vv) < 0:
        tdir = -tdir
    endt = vv * 0.85 + tdir * 0.15
    endt = endt / (np.linalg.norm(endt) or 1)
    brg = hermite(p, vv, tgt, endt, n=24)
    a = own["s"]
    if np.hypot(*(a[0] - p)) < np.hypot(*(a[-1] - p)):
        own["s"] = np.vstack([brg[::-1], a[1:]])
    else:
        own["s"] = np.vstack([a[:-1], brg])

lines = []
for st in strokes:
    a = np.array([to_pt(q) for q in st["s"]])
    approx = cv2.approxPolyDP(a.astype(np.float32).reshape(-1, 1, 2), 0.12, st["closed"]).reshape(-1, 2)
    if st["closed"]:
        approx = np.vstack([approx, approx[:1]])
    lines.append(approx)

# DXF (mm: 1 pt = 0.3528 mm), y aukštyn
import ezdxf
doc = ezdxf.new("R2010"); doc.units = ezdxf.units.MM
msp = doc.modelspace()
doc.layers.add("CENTERLINE", color=1); doc.layers.add("OUTLINE", color=7)
MMk = 25.4 / 72
for g in getattr(geom, "geoms", [geom]):
    for r in [g.exterior] + list(g.interiors):
        msp.add_lwpolyline([((x - x0) * MMk, (y1 - y) * MMk) for x, y in r.coords], close=True, dxfattribs={"layer": "OUTLINE"})
for L in lines:
    msp.add_spline([((x - x0) * MMk, (y1 - y) * MMk) for x, y in L], dxfattribs={"layer": "CENTERLINE"}) if len(L) > 3 else \
        msp.add_lwpolyline([((x - x0) * MMk, (y1 - y) * MMk) for x, y in L], dxfattribs={"layer": "CENTERLINE"})
doc.saveas(OUT + ".dxf")

# PDF: originalas + raudona centerline (vektoriai)
out = fitz.open()
pg = out.new_page(width=page.rect.width, height=page.rect.height)
pg.show_pdf_page(pg.rect, fitz.open(SRC), 0)
sh = pg.new_shape()
for L in lines:
    sh.draw_polyline([fitz.Point(*p) for p in L])
    sh.finish(color=(0.89, 0, 0.1), width=1.2, closePath=False, lineCap=1, lineJoin=1)
sh.commit()
out.save(OUT + ".pdf")
print("chains", len(lines), "mazgų", sum(len(L) for L in lines), "dydis mm", round((x1 - x0) * MMk), round((y1 - y0) * MMk))
if False:
    for g in getattr(geom, "geoms", [geom]):
        b = g.bounds; print([round(v) for v in b], round(g.area), len(g.interiors))
    cv2.imwrite("mask.png", (img * 255)[::4, ::4]); cv2.imwrite("sk.png", (sk * 255).astype(np.uint8)[::2, ::2])
if False:
    for c in chains:
        a = np.array([to_pt(p) for p in c])
        if a[:, 0].min() > 4890 and a[:, 0].max() < 5300:
            print("chain", len(c), a[:, 0].min().round(), a[:, 0].max().round(), a[:, 1].min().round(), a[:, 1].max().round(), G.degree(c[0]), G.degree(c[-1]))
    for L in lines:
        if L[:, 0].min() > 4890 and L[:, 0].max() < 5300:
            print("line", len(L), L[:, 0].min(), L[:, 1].min(), np.isnan(L).any())
    for comp in nx.connected_components(G):
        a = np.array([to_pt(p) for p in comp])
        if a[:, 0].min() > 4890 and a[:, 0].max() < 5300:
            sub = G.subgraph(comp); print("comp", len(comp), sorted(dict(sub.degree()).values()).count(1), [d for d in dict(sub.degree()).values() if d > 2])
