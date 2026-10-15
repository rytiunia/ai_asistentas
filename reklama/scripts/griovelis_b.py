#!/usr/bin/env python3
"""P10 (30 mm plexi) LED griovelis - VARIANTAS B (v235, Rytis 2026-10-15: „griovelis blogas, kampai lieka tušti").

Skirtumai nuo centerline.py (A):
  * linija = griovelio ZONOS (raidė - (griovelis/2 + sienelė), mitre) skeletas -> kampai AŠTRŪS (nebeapvalinami R = 2 x
    pusplotis), linija eina iki kampo pusiaukampinės;
  * galai PRATĘSIAMI tiesiai iki zonos krašto (griovelis baigiasi sienelės atstumu nuo raidės galo);
  * PLAČIOS dalys (max plotis >= wide, pvz. simbolis ~50 mm) - viena juosta nepašviečia kraštų: griovelis - KONTŪRO
    LYGIAGRETUS žiedas, atstumu max(griovelis/2 + sienelė, plotis / 4) nuo krašto (dvi eilės, kampai užpildomi).
Patikrinimas - griovelis_sim.py (apšvietimo simuliacija).

Naudojimas: python3 griovelis_b.py in.dxf (OUTLINE, mm) out_prefix [--groove=8] [--wall=2] [--wide=40] [--res=0.25]
Išvestis: out_prefix.dxf (OUTLINE, CENTERLINE, GROOVE_8MM, PROBLEM).
"""
import sys

import cv2
import ezdxf
import networkx as nx
import numpy as np
from shapely.geometry import LineString, Polygon, Point
from shapely.ops import unary_union
from skimage.morphology import skeletonize

ARG = lambda k, d: float(next((x.split("=")[1] for x in sys.argv if x.startswith(f"--{k}=")), d))


def recontour(geo, res=0.1):
    """rastras -> kontūrai su skylėmis (cv2 RETR_CCOMP); sutvarko kontūrus, kur skylė prijungta nulinio pločio siūle"""
    x0, y0, x1, y1 = geo.bounds
    pad = 1.0
    W, H = int((x1 - x0 + 2 * pad) / res) + 1, int((y1 - y0 + 2 * pad) / res) + 1
    P = lambda x, y: ((x - x0 + pad) / res, (y1 + pad - y) / res)
    m = np.zeros((H, W), np.uint8)
    for g in getattr(geo, "geoms", [geo]):
        cv2.fillPoly(m, [np.array([P(*q) for q in g.exterior.coords], np.int32)], 1)
        for r in g.interiors:
            cv2.fillPoly(m, [np.array([P(*q) for q in r.coords], np.int32)], 0)
    cs, hi = cv2.findContours(m, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    Q = lambda c: [(x * res + x0 - pad, y1 + pad - y * res) for x, y in c.reshape(-1, 2)]
    polys = []
    for i, c in enumerate(cs):
        if hi[0][i][3] == -1 and len(c) >= 3:
            holes, j = [], hi[0][i][2]
            while j != -1:
                if len(cs[j]) >= 3:
                    holes.append(Q(cs[j]))
                j = hi[0][j][0]
            polys.append(Polygon(Q(c), holes).buffer(0))
    return unary_union(polys)


def max_width(g):
    lo, hi = 0.0, 200.0
    while hi - lo > 0.2:
        m = (lo + hi) / 2
        lo, hi = (lo, m) if g.buffer(-m).is_empty else (m, hi)
    return 2 * lo


def skel_lines(core, res, spur_min):
    x0, y0, x1, y1 = core.bounds
    pad = 2.0
    W, H = int((x1 - x0 + 2 * pad) / res) + 1, int((y1 - y0 + 2 * pad) / res) + 1
    P = lambda x, y: ((x - x0 + pad) / res, (y1 + pad - y) / res)
    Q = lambda c, r: (c * res + x0 - pad, y1 + pad - r * res)
    m = np.zeros((H, W), np.uint8)
    for g in getattr(core, "geoms", [core]):
        cv2.fillPoly(m, [np.array([P(*q) for q in g.exterior.coords], np.int32)], 1)
        for r in g.interiors:
            cv2.fillPoly(m, [np.array([P(*q) for q in r.coords], np.int32)], 0)
    sk = skeletonize(m > 0)
    ys, xs = np.nonzero(sk)
    pts = set(zip(ys.tolist(), xs.tolist()))
    G = nx.Graph()
    G.add_nodes_from(pts)
    for (y, x) in pts:
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if (dy or dx) and (y + dy, x + dx) in pts:
                    G.add_edge((y, x), (y + dy, x + dx), w=float(np.hypot(dy, dx)))
    for a, b in list(G.edges()):                    # įstrižai, kai yra stačia jungtis
        if abs(a[0] - b[0]) == 1 and abs(a[1] - b[1]) == 1 and ((a[0], b[1]) in pts or (b[0], a[1]) in pts):
            G.remove_edge(a, b)
    # šakelių (galų šakučių, kampų ūsų) šalinimas
    for _ in range(20):
        changed = False
        for e in [n for n in G.nodes if G.degree(n) == 1]:
            if e not in G or G.degree(e) != 1:
                continue
            path, cur, prev, L = [e], e, None, 0.0
            while True:
                nb = [n for n in G.neighbors(cur) if n != prev]
                if len(nb) != 1 or G.degree(cur) > 2 and cur != e:
                    break
                L += G[cur][nb[0]]["w"] * res
                prev, cur = cur, nb[0]
                path.append(cur)
                if G.degree(cur) != 2:
                    break
            if G.degree(cur) >= 3 and L < spur_min:
                G.remove_nodes_from(path[:-1]); changed = True
        if not changed:
            break
    G.remove_nodes_from([n for n in list(G.nodes) if G.degree(n) == 0])
    # kraštinės tarp mazgų (laipsnis != 2) -> polilinijos
    lines, seen = [], set()
    nodes = [n for n in G.nodes if G.degree(n) != 2]
    for n in nodes:
        for nb in G.neighbors(n):
            if (n, nb) in seen:
                continue
            path = [n, nb]; seen.add((n, nb)); seen.add((nb, n))
            prev, cur = n, nb
            while G.degree(cur) == 2:
                nx_ = [q for q in G.neighbors(cur) if q != prev][0]
                seen.add((cur, nx_)); seen.add((nx_, cur))
                prev, cur = cur, nx_
                path.append(cur)
            lines.append(path)
    for cyc in nx.cycle_basis(G.subgraph([n for n in G.nodes if G.degree(n) == 2])):   # uždari žiedai (O)
        if all(G.degree(n) == 2 for n in cyc) and len(cyc) > 10:
            lines.append(cyc + [cyc[0]])
    # lygiagretūs trumpi keliai tarp tų pačių mazgų (skeleto kilpelės, pvz. O) - paliekamas tik trumpiausias
    def plen(p):
        return sum(np.hypot(a[0] - b[0], a[1] - b[1]) for a, b in zip(p, p[1:])) * res
    grp = {}
    for p in lines:
        if p[0] != p[-1]:
            grp.setdefault(tuple(sorted((p[0], p[-1]))), []).append(p)
    drop = set()
    for ps in grp.values():
        if len(ps) > 1:
            ps = sorted(ps, key=plen)
            drop.update(id(p) for p in ps[1:] if plen(p) < 3 * spur_min)
    lines = [p for p in lines if id(p) not in drop]
    out = []
    for p in lines:
        a = np.array([Q(c, r) for r, c in p], np.float64)
        a = cv2.approxPolyDP(a.astype(np.float32).reshape(-1, 1, 2), 0.35, False).reshape(-1, 2).astype(np.float64)
        out.append(a)
    # žiedas, nutrūkęs ties skeleto mazgu (O) - uždaromas
    for i, a in enumerate(out):
        if len(a) > 3 and not np.allclose(a[0], a[-1]) and np.hypot(*(a[0] - a[-1])) < 25 and LineString(a).length > 100:
            out[i] = np.vstack([a, a[:1]])
    # galų pratęsimas iki zonos krašto (tiesiai, pagal galo kryptį)
    deg = {}
    for a in out:
        for e in (tuple(np.round(a[0], 1)), tuple(np.round(a[-1], 1))):
            deg[e] = deg.get(e, 0) + 1
    zone = core.buffer(-0.05)
    for i, a in enumerate(out):
        if len(a) < 2 or np.allclose(a[0], a[-1]):
            continue
        for end in (0, -1):
            if deg.get(tuple(np.round(a[end], 1)), 0) > 1:
                continue
            q, r_ = (a[0], a[min(len(a) - 1, 3)]) if end == 0 else (a[-1], a[max(0, len(a) - 4)])
            d = q - r_
            if np.hypot(*d) < 1e-6:
                continue
            d = d / np.hypot(*d)
            t = 0.0
            while zone.contains(Point(q + d * (t + res))) and t < 200:
                t += res
            if t > 0.5:
                a = np.vstack([q + d * t, a]) if end == 0 else np.vstack([a, q + d * t])
        out[i] = a
    return [a for a in out if LineString(a).length > 3]


def main():
    src, outp = sys.argv[1], sys.argv[2]
    GROOVE, WALL, WIDE, RES = ARG("groove", 8), ARG("wall", 2), ARG("wide", 40), ARG("res", 0.25)
    rpt = GROOVE / 2 + WALL
    m = ezdxf.readfile(src).modelspace()
    rings = [Polygon([(p[0], p[1]) for p in e.get_points("xy")]).buffer(0) for e in m.query("LWPOLYLINE")
             if e.dxf.layer.upper() == "OUTLINE"]
    geo = None
    for r in rings:
        geo = r if geo is None else geo.symmetric_difference(r)
    geo = recontour(geo)                             # v235: kontūrai su „siūle" (O vienu kontūru) -> tikros skylės
    lines = []
    for g in sorted(getattr(geo, "geoms", [geo]), key=lambda g: g.bounds[0]):
        w = max_width(g)
        if w >= WIDE:                                # plati dalis - kontūro lygiagretus žiedas
            o = max(rpt, w / 4)
            off = g.buffer(-o, join_style=2, mitre_limit=4)
            n0 = len(lines)
            for pg in getattr(off, "geoms", [off]):
                for rg in [pg.exterior] + list(pg.interiors):
                    if rg.length >= 40:
                        lines.append(np.array(rg.coords))
            # siauros vietos, kurių žiedas neapima - ašis
            covered = unary_union([LineString(a).buffer(o + 1) for a in lines[n0:]]) if len(lines) > n0 else None
            rest = g.buffer(-rpt, join_style=2, mitre_limit=4)
            if covered is not None:
                rest = rest.difference(covered.buffer(2))
            for pg in getattr(rest, "geoms", [rest]):
                if pg.area > 150:
                    lines += skel_lines(pg, RES, spur_min=8.0)
            print(f"  x {g.bounds[0]:.0f}: plati ({w:.0f} mm) - žiedas {o:.1f} mm nuo krašto")
        else:
            core = g.buffer(-rpt, join_style=2, mitre_limit=4)
            if core.is_empty:
                print(f"  ! x {g.bounds[0]:.0f}: griovelis + sienelė netelpa (plotis {w:.0f})"); continue
            cw = max_width(core)
            lines += skel_lines(core, RES, spur_min=max(8.0, 2.2 * cw))
            print(f"  x {g.bounds[0]:.0f}: plotis {w:.0f} mm - ašis su aštriais kampais, galai iki sienelės")
    groove = unary_union([LineString(a).buffer(GROOVE / 2, quad_segs=16) for a in lines])
    bad = groove.difference(geo.buffer(-WALL))
    bad = [b for b in getattr(bad, "geoms", [bad]) if b.area > 0.5]
    doc = ezdxf.new("R2010"); doc.units = ezdxf.units.MM
    ms = doc.modelspace()
    for ln, c in (("OUTLINE", 7), ("CENTERLINE", 1), ("GROOVE_8MM", 3), ("PROBLEM", 6)):
        doc.layers.add(ln, color=c)
    for g in getattr(geo, "geoms", [geo]):
        for r in [g.exterior] + list(g.interiors):
            ms.add_lwpolyline(list(r.coords), close=True, dxfattribs={"layer": "OUTLINE"})
    for g in getattr(groove, "geoms", [groove]):
        for r in [g.exterior] + list(g.interiors):
            ms.add_lwpolyline(list(r.coords), close=True, dxfattribs={"layer": "GROOVE_8MM"})
    for b in bad:
        ms.add_lwpolyline(list(b.exterior.coords), close=True, dxfattribs={"layer": "PROBLEM"})
    for a in lines:
        ms.add_lwpolyline([tuple(p) for p in a], dxfattribs={"layer": "CENTERLINE"})
    doc.saveas(outp + ".dxf")
    print(f"OK {outp}.dxf: linijų {len(lines)}, juostos ilgis {sum(LineString(a).length for a in lines) / 1000:.2f} m, "
          f"probleminių zonų {len(bad)}")


if __name__ == "__main__":
    main()
