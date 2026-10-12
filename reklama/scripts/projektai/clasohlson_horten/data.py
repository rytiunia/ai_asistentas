"""Clas Ohlson Horten 3 - bendri duomenys: fasadas, folded dalys, P8 raidės, spaceriai, išklotinės."""
import math, sys
import pymupdf as fitz
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union

SK = sys.argv[0] and None
CLIENT_PDF = "/root/.claude/uploads/454aabe4-a26e-51a4-90bd-3f68e4f6d938/517838f6-CO-Horten-3-Sign-Plate-16839x900_LED-3381x720_10proc.pdf"

# ---- fasadas (ranka rašyti matmenys - teisingi)
PLANES = [3684, 6758, 6397]       # Rytis 2026-10-09: ŽIŪRINT IŠ PRIEKIO kairėje trumpesnė kraštinė
ALPHA = [8.0, 18.5]          # PRIELAIDA iš eskizo (ne mastelis) - matuoti vietoje
FOLDS = [PLANES[0], PLANES[0] + PLANES[1]]          # 6397, 13155
L_TOTAL = sum(PLANES)                                 # 16839
PH, PD = 900, 40                                       # plokštės aukštis, gylis

# ---- dalys (Al 2 mm lapas 2000x4000)
MAXP = 3900


def _fill(l, rem_first):
    n = int(l // MAXP); r = round(l - n * MAXP); a = [MAXP] * n
    if r > 0:
        a = [r] + a if rem_first else a + [r]
    return a


_side = (PLANES[1] - MAXP) / 2
PLAN = [_fill(PLANES[0], True), [_side, MAXP, _side], _fill(PLANES[2], False)]   # likutis - į išorinį kraštą
PARTS = []                    # dict: no, plane, x0, len, ends (left/right: 'outer' | 'joint' | 'fold1'/'fold2')
_x = 0
for pi, pcs in enumerate(PLAN):
    for k, ln in enumerate(pcs):
        PARTS.append({"no": len(PARTS) + 1, "plane": pi + 1, "x0": _x, "len": round(ln)})
        _x += ln
for i, p in enumerate(PARTS):
    def end(xe):
        if abs(xe) < 1 or abs(xe - L_TOTAL) < 1:
            return "outer"
        for fi, f in enumerate(FOLDS):
            if abs(xe - f) < 1:
                return f"fold{fi + 1}"
        return "joint"
    p["ends"] = (end(p["x0"]), end(p["x0"] + p["len"]))
JOINTS = sorted({round(p["x0"]) for p in PARTS if p["x0"] > 1})   # 2497, 6397, 7826, 11726, 13155

# ---- skarda / lenkimas (STEP lankstinys_1prie1: t2, R2 vid., šonai tarp viršaus ir apačios, tarpas 0,1)
T_S, R_B, K_F = 2.0, 2.0, 0.44                         # K - PRIELAIDA (Inventor numatytasis)
BA = math.pi / 2 * (R_B + K_F * T_S)                   # 4.524
OSSB = R_B + T_S                                       # 4
BD = 2 * OSSB - BA                                     # 3.476
FL = PD - OSSB + BA / 2                                # flanšas iki lenkimo ašies 38.26
GAP = 0.1
SIDE_H = PH - 2 * T_S - 2 * GAP                        # 895.8
SHEET = (4000, 2000); EDGE_M = 10


def flat_size(ln):
    return ln + 2 * PD - 2 * BD, PH + 2 * PD - 2 * BD


def fold_delta(fi):
    """vidinis kampas: priekis trumpesnis per 40*tan(a/2) kiekvienai daliai prie lūžio"""
    return PD * math.tan(math.radians(ALPHA[fi]) / 2)


# ---- logotipas iš kliento failo (10 %), centruotas virš grotelių
K10 = 25.4 / 72 * 10


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


page = fitz.open(CLIENT_PDF)[0]
_raw, _seen = [], set()
for d in page.get_drawings():
    f = d.get("fill")
    if not f or sum(f[:3]) > 0.5:
        continue
    subs = _subs(d)
    pts = [q for sp in subs for s in sp for q in s[1:]]
    key = tuple(round(v) for v in (min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts)))
    if key in _seen:
        continue
    _seen.add(key); _raw.append(subs)

GRILLE_C = PLANES[0] + PLANES[1] / 2                 # 9776
_allx = [q[0] for s in _raw for sp in s for q in flat(sp)]
LOGO_X0_CL = min(_allx) * K10
DX = GRILLE_C - (min(_allx) + max(_allx)) / 2 * K10
LETTERS = []                 # sub (mm, y žemyn nuo plokštės viršaus), geom (y žemyn), bb
for subs in _raw:
    sub = [[(s[0],) + tuple((q[0] * K10 + DX, q[1] * K10) for q in s[1:]) for s in sp] for sp in subs]
    polys = [Polygon(flat(sp)).buffer(0) for sp in sub if len(flat(sp)) > 2]
    g = polys[0]
    for p in polys[1:]:
        g = g.symmetric_difference(p)
    LETTERS.append({"sub": sub, "geom": g, "bb": g.bounds})
LETTERS.sort(key=lambda L: L["bb"][0])
LOGO_BB = (min(L["bb"][0] for L in LETTERS), min(L["bb"][1] for L in LETTERS),
           max(L["bb"][2] for L in LETTERS), max(L["bb"][3] for L in LETTERS))
NAMES = ["logo arc", "logo o", "C", "l", "a", "s", "O", "h", "l", "s", "o", "n"]

# ---- spaceriai TIK po raidėmis (Ø16, centras >= 16 mm nuo krašto)
SP_D, SP_EDGE = 16, 16


def spacer_points(g):
    inner = g.buffer(-SP_EDGE)
    if inner.is_empty:
        return []
    x0, y0, x1, y1 = g.bounds
    cand = []
    y = y0
    while y <= y1:
        x = x0
        while x <= x1:
            p = Point(x, y)
            if inner.contains(p):
                cand.append((x, y, g.exterior.distance(p) if g.geom_type == "Polygon" else g.boundary.distance(p)))
            x += 8
        y += 8
    cand = [(x, y, g.boundary.distance(Point(x, y))) for x, y, _ in cand]
    n = max(2, min(6, math.ceil(g.area / 45000) + 1))
    cand.sort(key=lambda c: -c[2]); pick = [cand[0]]
    while len(pick) < n:
        best, bd = None, -1
        for c in cand:
            d = min(math.dist(c[:2], p[:2]) for p in pick)
            if d > bd:
                bd, best = d, c
        if bd < 60:
            break
        pick.append(best)
    return [(round(p[0], 1), round(p[1], 1)) for p in pick]


# tvirtinimai pagal Clas Ohlson proporcijų etaloną (refholes): Ø4 = spaceriai, išilginės, Ø8
import refholes as RH


def attach_ref(letters):
    res = RH.apply([L["geom"] for L in letters])
    for r in res:
        L = next(L for L in letters if L["geom"] is r["geom"])
        L.update({"name": r["name"], "ref": r["ref"], "scale": r["scale"], "feats": r["feats"], "wall": r["wall"],
                  "inner": r["inner"], "sp": [f["c"] for f in r["feats"] if f["type"] == "D4"]})
    return res


REF_RES = attach_ref(LETTERS)
N_SP = sum(len(L["sp"]) for L in LETTERS)
N_SLOT = sum(1 for L in LETTERS for f in L["feats"] if f["type"] == "SLOT")
N_D8 = sum(1 for L in LETTERS for f in L["feats"] if f["type"] == "D8")
A_FACE = sum(L["geom"].area for L in LETTERS) / 1e6
PER = sum(L["geom"].length for L in LETTERS) / 1000

if __name__ == "__main__":
    print("parts", [(p["no"], p["len"], p["ends"]) for p in PARTS])
    print("joints", JOINTS, "BD", round(BD, 3), "FL", round(FL, 2), "flat", [tuple(round(v, 1) for v in flat_size(p["len"])) for p in PARTS])
    print("logo bb", [round(v, 1) for v in LOGO_BB], "w", round(LOGO_BB[2] - LOGO_BB[0], 1), "h", round(LOGO_BB[3] - LOGO_BB[1], 1))
    print("letters", len(LETTERS), "spacers", N_SP, [len(L["sp"]) for L in LETTERS], "A", round(A_FACE, 3), "PER", round(PER, 2))
    print("delta", [round(fold_delta(i), 1) for i in range(2)])


# ---- laidas (Rytis 2026-10-09): baltas 12V, 5 m, KAIRĖJE VIRŠUJE -> trafo box RAL 7044
CABLE = {"voltage": "12V", "len_m": 5.0, "colour": "white", "trafo_ral": "7044"}


def d11_point(L, edge=30):
    """D11 raidės (logotipo lanko) viršutinėje dalyje: >= 30 mm nuo kontūro, >= 20 mm nuo Ø4, kuo arčiau viršaus"""
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


D11 = d11_point(LETTERS[0])

LOGO_PART = next(p for p in PARTS if p["x0"] <= LOGO_BB[0] and p["x0"] + p["len"] >= LOGO_BB[2])
