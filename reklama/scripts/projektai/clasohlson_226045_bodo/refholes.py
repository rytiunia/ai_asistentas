"""Clas Ohlson P8 special - gamybos proporcijų etalonas (ClasOhlson_proporcijos.pdf, 1:1, 3 dydžiai).
Kiekvienai raidei: išorinis plexi kontūras, vidinis (ertmė) kontūras, skylės (Ø4, išilginė 6x3.7, Ø8).
Taikymas: tikslinei raidei imamas ARTIMIAUSIO aukščio etalono dydis, skylių centrai perkeliami proporcingai
(mastelis = aukščių santykis), skylių DIAMETRAI / matmenys NEKEIČIAMI."""
import math
import pymupdf as fitz
from shapely.geometry import Polygon, Point
import data as D

import os
REF_PDF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "assets", "clasohlson_proporcijos.pdf")   # skill'o etalonas
SETS = {"S1": {"outer": 0, "inner": 2, "holes": [1, 3]},
        "S2": {"outer": 24, "inner": 23, "holes": [25, 26]},
        "S3": {"outer": 5, "inner": 4, "holes": [6, 7, 8, 9]}}
k = 25.4 / 72
_ds = fitz.open(REF_PDF)[0].get_drawings()


def _polys(i):
    out = []
    for sp in D._subs(_ds[i]):
        pts = [(x * k, y * k) for x, y in D.flat(sp)]
        if len(pts) > 2:
            out.append(Polygon(pts).buffer(0))
    return out


def group_letters(polys):
    """kontūrai -> raidės (išorinis + skylės)"""
    polys = sorted(polys, key=lambda g: -g.area)
    groups = []
    for g in polys:
        host = next((h for h in groups if h["outer"].contains(g.representative_point())), None)
        if host:
            host["geom"] = host["geom"].difference(g)
        else:
            groups.append({"outer": g, "geom": g})
    return [h["geom"] for h in groups]


def order_letters(geoms):
    """ikona (2 kairiausi) + eilutės iš viršaus, eilutėje pagal x -> C l a s O h l s o n"""
    gs = sorted(geoms, key=lambda g: g.bounds[0])
    icon = gs[:2]
    rest = gs[2:]
    rows = []
    for g in sorted(rest, key=lambda g: (g.bounds[1] + g.bounds[3]) / 2):
        cy = (g.bounds[1] + g.bounds[3]) / 2
        r = next((r for r in rows if abs(r[0] - cy) < 0.6 * (g.bounds[3] - g.bounds[1])), None)
        if r:
            r[1].append(g)
        else:
            rows.append([cy, [g]])
    rows.sort(key=lambda r: r[0])
    # 'a' / 's' / 'o' žemesni - priskirti eilutei pagal apačią
    out = list(icon)
    for _, r in rows:
        out += sorted(r, key=lambda g: g.bounds[0])
    return out


def _rows_fix(geoms):
    """eilutės pagal raidžių apačią (baseline) - patikimiau nei centrai"""
    gs = sorted(geoms, key=lambda g: g.bounds[0])
    icon, rest = gs[:2], gs[2:]
    rows = []
    for g in rest:
        b = g.bounds[3]
        r = next((r for r in rows if abs(r[0] - b) < 40), None)
        if r:
            r[1].append(g)
        else:
            rows.append([b, [g]])
    rows.sort(key=lambda r: r[0])
    out = list(icon)
    for _, r in rows:
        out += sorted(r, key=lambda g: g.bounds[0])
    return out


REF = {}
for name, st in SETS.items():
    outer = _rows_fix(group_letters(_polys(st["outer"])))
    inner_all = group_letters(_polys(st["inner"]))
    feats = []
    for hi in st["holes"]:
        for sp in D._subs(_ds[hi]):
            pts = [(x * k, y * k) for x, y in D.flat(sp)]
            xs, ys = [p[0] for p in pts], [p[1] for p in pts]
            w, h = max(xs) - min(xs), max(ys) - min(ys)
            cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
            typ = "D4" if abs(w - h) < 0.6 and w < 5 else ("D8" if abs(w - h) < 0.6 else "SLOT")
            feats.append({"c": (cx, cy), "w": round(w, 1), "h": round(h, 1), "type": typ})
    letters = []
    for g in outer:
        inn = max((q for q in inner_all if g.contains(q.representative_point())), key=lambda q: q.area, default=None)
        fs = [f for f in feats if g.buffer(1).contains(Point(f["c"]))]
        x0, y0, x1, y1 = g.bounds
        wall = (g.area - inn.area) / ((g.length + inn.length) / 2) if inn is not None else None
        letters.append({"geom": g, "bb": g.bounds, "H": y1 - y0, "feats": fs, "wall": wall})
    REF[name] = letters

NAMES = ["logo arc", "logo o", "C", "l", "a", "s", "O", "h", "l", "s", "o", "n"]


def apply(target_geoms):
    """target_geoms - tikslinės raidės (shapely, mm, y žemyn) bet kokia tvarka.
    Grąžina [{geom, name, ref, scale, feats:[{c, w, h, type}], inner}] tvarka NAMES."""
    tg = _rows_fix(target_geoms)
    out = []
    for i, g in enumerate(tg):
        Ht = g.bounds[3] - g.bounds[1]
        best = min(REF, key=lambda n: abs(math.log(Ht / REF[n][i]["H"])))
        r = REF[best][i]
        s = Ht / r["H"]
        fs = []
        for f in r["feats"]:
            c = (g.bounds[0] + (f["c"][0] - r["bb"][0]) * s, g.bounds[1] + (f["c"][1] - r["bb"][1]) * s)
            ok = g.contains(Point(c))
            fs.append({"c": c, "w": f["w"], "h": f["h"], "type": f["type"], "inside": ok})
        wall = round(r["wall"], 1)
        out.append({"geom": g, "name": NAMES[i], "ref": best, "scale": s, "feats": fs, "wall": wall,
                    "inner": g.buffer(-wall, join_style=2)})
    return out


if __name__ == "__main__":
    for n, L in REF.items():
        print(n, [len(l["feats"]) for l in L], "H", [round(l["H"]) for l in L][:4], "wall", sorted({round(l["wall"], 1) for l in L}))
        from collections import Counter
        print("  types", Counter(f["type"] for l in L for f in l["feats"]), Counter((f["type"], f["w"], f["h"]) for l in L for f in l["feats"]).most_common(6))
    res = apply([L["geom"] for L in D.LETTERS])
    print("H3", [(r["name"], r["ref"], round(r["scale"], 2), len(r["feats"]), sum(not f["inside"] for f in r["feats"])) for r in res])
