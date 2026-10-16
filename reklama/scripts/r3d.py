"""Vektorinis 3D su TEISINGU užstojimu (be prasišvietimo / dingimo).
Algoritmas: paviršiai (atmetus nugarinius) smulkinami į plyteles -> projekcija -> rikiuojama nuo ARČIAUSIOS ->
kiekvienos plytelės matoma dalis = jos 2D poligonas MINUS jau uždengtas plotas (shapely) -> piešiama tik matoma dalis.
Kontūrai (briaunos) piešiami po to, tik matomos atkarpų dalys (tikrinama pagal arčiau esančias plyteles)."""
import math
from shapely.geometry import Polygon, LineString, Point, MultiPolygon
from shapely.ops import unary_union
from shapely.strtree import STRtree
from shapely import prepared
import lapas_core as K
from reportlab.lib.colors import Color, HexColor



def view_simplify(geom, k=1500.0):
    """v312: 3D vaizdui geometrija supaprastinama (paklaida = gabaritas / k, ~0,1 pt lape) - kreivės išlieka glotnios,
    bet nebe tūkstančiai atkarpų (CorelDRAW mazgai). Gamybos geometrija (DXF, 1:1) nekeičiama."""
    try:
        x0, y0, x1, y1 = geom.bounds
        tol = max(x1 - x0, y1 - y0) / k
        return geom.simplify(tol, preserve_topology=True) if tol > 0 else geom
    except Exception:
        return geom

class Scene:
    def __init__(self, yaw=32, pitch=17, light=(-0.45, 0.75, 0.55), tile=250.0):
        self.V = K.View3D(yaw=yaw, pitch=pitch, light=light)
        self.faces = []            # (pts3, holes3, normal, fill, edge_col, edge_lw, amb)
        self.tile = tile
        self.flat = False                                          # v224: CAD - be šešėliavimo (baltas + juodi kontūrai)

    # ---------------------------------------------------------------- geometrija
    def face(self, pts3, normal, fill, edge=None, edge_lw=0.15, holes=(), amb=0.6, tile=True):
        self.faces.append({"p": pts3, "h": list(holes), "n": normal, "fill": fill, "edge": edge, "lw": edge_lw,
                           "amb": amb, "tile": tile})

    def box(self, o, u, v, w, fill, edge=None, amb=0.6):
        """dėžė: kampas o, kraštinių vektoriai u, v, w (3D, mm)"""
        def add(a, b):
            return tuple(x + y for x, y in zip(a, b))
        def cross(a, b):
            return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
        def neg(a):
            return tuple(-x for x in a)
        def unit(a):
            l_ = math.sqrt(sum(x * x for x in a)) or 1
            return tuple(x / l_ for x in a)
        o2 = add(o, w)
        P = [o, add(o, u), add(add(o, u), v), add(o, v)]
        Q = [o2, add(o2, u), add(add(o2, u), v), add(o2, v)]
        nw = unit(cross(u, v))
        if sum(a * b for a, b in zip(nw, w)) < 0:
            nw = neg(nw)
        nu, nv = unit(u), unit(v)
        self.face(Q, nw, fill, edge, amb=amb); self.face(P, neg(nw), fill, edge, amb=amb)
        self.face([P[0], P[1], Q[1], Q[0]], neg(nv), fill, edge, amb=amb)
        self.face([P[3], P[2], Q[2], Q[3]], nv, fill, edge, amb=amb)
        self.face([P[0], P[3], Q[3], Q[0]], neg(nu), fill, edge, amb=amb)
        self.face([P[1], P[2], Q[2], Q[1]], nu, fill, edge, amb=amb)

    def extrude_xy(self, geom, z0, z1, side, face_col, edge=None, xf=None):
        """shapely (x, y) kūnas, ištemptas z0..z1 (+z į žiūrovą); xf(x, y, z) -> pasaulio taškas"""
        xf = xf or (lambda x, y, z: (x, y, z))
        geom = view_simplify(geom)                      # v312: iliustracinis 3D - be tūkstančių šoninių juostelių
        for g in getattr(geom, "geoms", [geom]):
            from shapely.geometry.polygon import orient
            g = orient(g, 1.0)
            for ring in [g.exterior] + list(g.interiors):
                c = list(ring.coords)
                for (x0, y0), (x1, y1) in zip(c[:-1], c[1:]):
                    L = math.hypot(x1 - x0, y1 - y0)
                    if L < 1e-6:
                        continue
                    n2 = ((y1 - y0) / L, -(x1 - x0) / L)
                    a, b = xf(x0, y0, z0), xf(x1, y1, z0)
                    cc, d = xf(x1, y1, z1), xf(x0, y0, z1)
                    n3 = self._nrm(a, b, cc, ref=xf(x0 + n2[0], y0 + n2[1], z0), base=a)
                    self.face([a, b, cc, d], n3, side, None, tile=False, amb=0.72)
            ext = [xf(x, y, z1) for x, y in list(g.exterior.coords)[:-1]]
            hol = [[xf(x, y, z1) for x, y in list(r.coords)[:-1]] for r in g.interiors]
            nz = self._nrm(xf(0, 0, z1), xf(1, 0, z1), xf(0, 1, z1), ref=xf(0, 0, z1 + 1), base=xf(0, 0, z1))
            self.face(ext, nz, face_col, edge, holes=hol, tile=False)

    @staticmethod
    def _nrm(a, b, c, ref, base):
        u = [b[i] - a[i] for i in range(3)]; v = [c[i] - a[i] for i in range(3)]
        n = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
        l_ = math.sqrt(sum(x * x for x in n)) or 1
        n = tuple(x / l_ for x in n)
        d = [ref[i] - base[i] for i in range(3)]
        if sum(n[i] * d[i] for i in range(3)) < 0:
            n = tuple(-x for x in n)
        return n

    # ---------------------------------------------------------------- piešimas
    def _tiles(self, f):
        p = f["p"]
        if not f["tile"] or len(p) != 4 or f["h"]:
            return [p]
        d = lambda a, b: math.dist(a, b)
        nu = max(1, int(math.ceil(max(d(p[0], p[1]), d(p[3], p[2])) / self.tile)))
        nv = max(1, int(math.ceil(max(d(p[0], p[3]), d(p[1], p[2])) / self.tile)))
        lerp = lambda a, b, t: tuple(a[i] + (b[i] - a[i]) * t for i in range(3))
        out = []
        for i in range(nu):
            for j in range(nv):
                def P(s, t):
                    return lerp(lerp(p[0], p[1], s), lerp(p[3], p[2], s), t)
                out.append([P(i / nu, j / nv), P((i + 1) / nu, j / nv), P((i + 1) / nu, (j + 1) / nv), P(i / nu, (j + 1) / nv)])
        return out

    def render(self, box):
        """Tikslus užstojimas: kiekvienai persidengiančių (2D) paviršių porai gylis lyginamas TAME PAČIAME
        taške (persidengimo vidinis taškas, plokštumų lygtys vaizdo erdvėje) -> grafas 'A priešais B' ->
        topologinis rikiavimas -> piešiama nuo tolimiausio. Didelių / mažų objektų santykis nebesvarbus."""
        V = self.V
        pts = [q for f in self.faces for q in f["p"]]
        V.fit(pts, box)
        F = []
        for fi, f in enumerate(self.faces):
            if V.rot(*f["n"])[2] <= 1e-6:
                continue
            R = [V.rot(*q) for q in f["p"]]
            # Newell normalė vaizdo erdvėje
            nx = ny = nz = 0.0
            for a, b in zip(R, R[1:] + R[:1]):
                nx += (a[1] - b[1]) * (a[2] + b[2]); ny += (a[2] - b[2]) * (a[0] + b[0]); nz += (a[0] - b[0]) * (a[1] + b[1])
            if abs(nz) < 1e-9:
                continue
            cx = sum(r[0] for r in R) / len(R); cy = sum(r[1] for r in R) / len(R); cz = sum(r[2] for r in R) / len(R)
            d = nx * cx + ny * cy + nz * cz
            p2 = [V.S(*q) for q in f["p"]]
            hol = [[V.S(*q) for q in h] for h in f["h"]]
            poly = Polygon(p2, hol).buffer(0)
            if poly.is_empty or poly.area < 1e-4:
                continue
            F.append({"poly": poly, "pl": (nx, ny, nz, d), "mz": cz, "f": f,
                      "col": f["fill"] if self.flat else V.shade(f["fill"], f["n"], f["amb"])})
        k, ox, oy = V.k, V.ox, V.oy

        def depth(i, x, y):
            nx, ny, nz, d = F[i]["pl"]
            X, Y_ = (x - ox) / k, (y - oy) / k
            return (d - nx * X - ny * Y_) / nz
        n = len(F)
        tree = STRtree([e["poly"] for e in F])
        behind = [set() for _ in range(n)]        # behind[i] - paviršiai, kurie yra UŽ i (piešiami anksčiau)
        for i in range(n):
            pi = F[i]["poly"]
            for j in tree.query(pi):
                j = int(j)
                if j <= i:
                    continue
                pj = F[j]["poly"]
                if not pi.intersects(pj):
                    continue
                inter = pi.intersection(pj)
                if inter.is_empty or inter.area < 0.02:
                    continue
                pt = inter.representative_point()
                di, dj = depth(i, pt.x, pt.y), depth(j, pt.x, pt.y)
                if abs(di - dj) < 1e-6:
                    continue
                if di > dj:
                    behind[i].add(j)
                else:
                    behind[j].add(i)
        # topologinis rikiavimas (pirmi - tie, už kurių nieko nėra); ciklai - pagal vidutinį gylį
        indeg = [0] * n
        ahead = [[] for _ in range(n)]
        for i in range(n):
            for j in behind[i]:
                ahead[j].append(i); indeg[i] += 1
        import heapq
        heap = [(F[i]["mz"], i) for i in range(n) if indeg[i] == 0]
        heapq.heapify(heap)
        order, done = [], [False] * n
        while len(order) < n:
            if not heap:
                rest = [i for i in range(n) if not done[i]]
                i0 = min(rest, key=lambda i: F[i]["mz"]); indeg[i0] = 0; heapq.heappush(heap, (F[i0]["mz"], i0))
            _, i = heapq.heappop(heap)
            if done[i]:
                continue
            done[i] = True; order.append(i)
            for j in ahead[i]:
                indeg[j] -= 1
                if indeg[j] == 0 and not done[j]:
                    heapq.heappush(heap, (F[j]["mz"], j))
        c = K.c
        for i in order:
            e = F[i]; g = e["poly"]; f = e["f"]
            for gg in getattr(g, "geoms", [g]):
                if gg.geom_type != "Polygon":
                    continue
                c.saveState(); c.setFillColor(e["col"])
                c.setStrokeColor(f["edge"] or e["col"]); c.setLineWidth(K.HAIR)
                p = c.beginPath()
                for ring in [gg.exterior] + list(gg.interiors):
                    K.ring_path(p, list(ring.coords))          # v313: lankai (Bezier), ne laužtė
                c.drawPath(p, stroke=1, fill=1, fillMode=0); c.restoreState()

    @staticmethod
    def _ln(run, col, lw):
        c = K.c
        c.saveState(); c.setStrokeColor(col); c.setLineWidth(K.HAIR); c.line(*run[0], *run[1]); c.restoreState()
