"""Clas Ohlson Order 226045 Bodø - pagalbinės funkcijos (iš clasohlson_horten/data.py be Horten fasado duomenų)."""
import math
from shapely.geometry import Point


def _subs(d):
    subs, cur, last = [], [], None
    for it in d["items"]:
        if it[0] == "re":
            r = it[1]; subs.append([("M", (r.x0, r.y0)), ("L", (r.x1, r.y0)), ("L", (r.x1, r.y1)), ("L", (r.x0, r.y1))]); continue
        p0 = (it[1].x, it[1].y)
        if last is None or math.dist(p0, last) > 0.01:
            if cur:
                subs.append(cur)
            cur = [("M", p0)]
        if it[0] == "l":
            cur.append(("L", (it[2].x, it[2].y))); last = (it[2].x, it[2].y)
        elif it[0] == "c":
            cur.append(("C", (it[2].x, it[2].y), (it[3].x, it[3].y), (it[4].x, it[4].y))); last = (it[4].x, it[4].y)
    if cur:
        subs.append(cur)
    return subs


def _bez(p0, p1, p2, p3, t):
    return tuple((1 - t) ** 3 * a + 3 * (1 - t) ** 2 * t * b + 3 * (1 - t) * t * t * c + t ** 3 * d for a, b, c, d in zip(p0, p1, p2, p3))


def flat(sp, n=14):
    pts, cur = [], None
    for s in sp:
        if s[0] in ("M", "L"):
            cur = s[1]; pts.append(cur)
        else:
            for i in range(1, n + 1):
                pts.append(_bez(cur, s[1], s[2], s[3], i / n))
            cur = s[3]
    return pts


LETTERS = []                                     # refholes __main__ suderinamumui


def attach_ref(letters):
    """tvirtinimai pagal Clas Ohlson proporcijų etaloną (refholes): Ø4 = spaceriai, išilginės, Ø8"""
    import refholes as RH
    res = RH.apply([L["geom"] for L in letters])
    for r in res:
        L = next(L for L in letters if L["geom"] is r["geom"])
        L.update({"name": r["name"], "ref": r["ref"], "scale": r["scale"], "feats": r["feats"], "wall": r["wall"],
                  "inner": r["inner"], "sp": [f["c"] for f in r["feats"] if f["type"] == "D4"]})
    return res


# laidas (Clas Ohlson standartas, Rytis 2026-10-09): baltas 12V, 5 m, KAIRĖJE VIRŠUJE -> trafo box RAL 7044
CABLE = {"voltage": "12V", "len_m": 5.0, "colour": "white", "trafo_ral": "7044"}


def d11_point(L, edge=30):
    """D11 logotipo lanko viršutinėje dalyje: >= 30 mm nuo kontūro, >= 20 mm nuo Ø4, kuo arčiau viršaus"""
    g = L["geom"]
    for e in (edge, 25, 20):
        inner = g.buffer(-e)
        if not inner.is_empty:
            break
    x0, y0, x1, y1 = g.bounds
    best = None
    y = y0
    while y < y0 + (y1 - y0) * 0.3 and best is None:
        x = x0
        while x <= x1:
            p = Point(x, y)
            if inner.contains(p) and all(math.dist((x, y), s) >= 20 for s in L["sp"]):
                if best is None or x > best[0]:
                    best = (x, y)
            x += 2
        y += 2
    return best
