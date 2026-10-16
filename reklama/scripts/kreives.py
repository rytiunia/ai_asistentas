#!/usr/bin/env python3
"""v312 (Rytis 2026-10-16, Leapmotor 33577: „kodėl failai dokumente ir dxf gaunasi su daug taškų, tarp kurių tiesios linijos,
nors failas apvalus, bet gaunasi kampuotas?") - KREIVĖS LANKAIS, NE LAUŽTĖMIS. Viena vieta visiems generatoriams.

PRIEŽASTIS: geometrijos biblioteka (shapely) laiko kontūrus tik tiesių atkarpų daugiakampiais. Kliento Bezier kreivės
nuskaitant buvo skaidomos į 12 (ar 8) atkarpų, ofsetai (buffer: išpjova + 0,7, pagrindas + 30, dugnas - 3, puzzle galvutės)
- vėl atkarpos, o DXF / PDF rašytojai rašė tas atkarpas kaip yra (LWPOLYLINE be lankų). v113 (2026-10-12, „labai daug nodes
ant lenktų linijų") pataisa buvo įdėta TIK į p6_dxf.py, kiti (vėliau sukurti) generatoriai jos nenaudojo, patikra netikrino.

DABAR:
  - nuskaitymas: Bezier skaidomas adaptyviai (sagitta <= 0,01 mm) - `flat_sub`, `bez_flat`;
  - shapely buffer - `BUF_QS` (64 atkarpos ketvirčiui), kad ofsetų lankai būtų tikslūs;
  - DXF: VISI LWPOLYLINE prieš išsaugant - tiesės + lankai (bulge), nuokrypis <= 0,02 mm: `saveas(doc, path)` arba
    `fit_dxf(path)`; Corel / CNC mazgai tik atkarpų galuose (kaip po „Reduce nodes");
  - PDF (lapas, 1:1): lapas_core.path_of - lygios laužtės braižomos lankais (Bezier), `ring_to_sub`;
  - patikra_dxf.py: KAMPUOTA KREIVĖ - laužtė, kurioje >= 6 iš eilės trumpos atkarpos su mažais posūkiais (be lankų).
Tikri kampai (posūkis > MAX_TURN) lieka kampais - aštuonkampis nevirsta apskritimu.
"""
import math

TOL = 0.02            # mm - lanko nuokrypis nuo taškų
FLAT_TOL = 0.01       # mm - Bezier skaidymo sagitta
MAX_TURN = 20.0       # ° - didžiausias posūkis tarp gretimų atkarpų, kurios dar laikomos viena kreive
CHORD_TOL = 0.5       # mm - leidžiamas lanko nuokrypis nuo stygos (taškai ant tikros kreivės, styga - aproksimacija)
BUF_QS = 64           # shapely buffer quad_segs


# ------------------------------------------------------------------ Bezier
def bez(p0, p1, p2, p3, t):
    u = 1 - t
    return (u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
            u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1])


def bez_flat(p0, p1, p2, p3, tol=FLAT_TOL):
    """Bezier -> taškai (be p0), segmentų sk. pagal sagitta <= tol"""
    L_ = math.dist(p0, p1) + math.dist(p1, p2) + math.dist(p2, p3)
    n = max(4, min(600, int(math.sqrt(max(L_, 1e-9) / (8 * tol)) * 2) + 1))
    return [bez(p0, p1, p2, p3, i / n) for i in range(1, n + 1)]


def flat_sub(sp, tol=FLAT_TOL):
    """subpath [("M", p), ("L", p), ("C", p1, p2, p3)] -> taškai (uždaras žiedas be pasikartojančio galo)"""
    pts, cur = [], None
    for s_ in sp:
        if s_[0] in ("M", "L"):
            cur = tuple(s_[1]); pts.append(cur)
        else:
            pts += bez_flat(cur, s_[1], s_[2], s_[3], tol); cur = tuple(s_[3])
    out = [pts[0]] if pts else []
    for q in pts[1:]:
        if math.dist(q, out[-1]) > 1e-4:
            out.append(q)
    if len(out) > 2 and math.dist(out[0], out[-1]) < 1e-4:
        out.pop()
    return out


# ------------------------------------------------------------------ tiesės + lankai
def _circ3(a, b, c):
    ax, ay = a; bx, by = b; cx, cy = c
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if abs(d) < 1e-12:
        return None
    a2, b2, c2 = ax * ax + ay * ay, bx * bx + by * by, cx * cx + cy * cy
    ux = (a2 * (by - cy) + b2 * (cy - ay) + c2 * (ay - by)) / d
    uy = (a2 * (cx - bx) + b2 * (ax - cx) + c2 * (bx - ax)) / d
    return ux, uy, math.hypot(ax - ux, ay - uy)


def _turn(a, b, c):
    v1 = (b[0] - a[0], b[1] - a[1]); v2 = (c[0] - b[0], c[1] - b[1])
    if math.hypot(*v1) < 1e-9 or math.hypot(*v2) < 1e-9:
        return 0.0
    return math.degrees(abs(math.atan2(v1[0] * v2[1] - v1[1] * v2[0], v1[0] * v2[0] + v1[1] * v2[1])))


def _line_ok(P, i, j, tol):
    (x0, y0), (x1, y1) = P[i], P[j]
    L = math.hypot(x1 - x0, y1 - y0)
    if L < 1e-9:
        return all(math.hypot(P[k][0] - x0, P[k][1] - y0) <= tol for k in range(i, j + 1))
    for k in range(i + 1, j):
        if abs((x1 - x0) * (y0 - P[k][1]) - (x0 - P[k][0]) * (y1 - y0)) / L > tol:
            return False
    return True


def _arc_ok(P, i, j, tol, TT):
    if j - i < 2:
        return None
    if any(TT[k] > MAX_TURN for k in range(i + 1, j)):          # tikras kampas lanko viduje - ne lankas
        return None
    m = (i + j) // 2
    c = _circ3(P[i], P[m], P[j])
    if c is None or c[2] > 1e5:
        return None
    ux, uy, r = c
    prev = math.atan2(P[i][1] - uy, P[i][0] - ux)
    tot, sgn = 0.0, 0
    for k in range(i + 1, j + 1):
        if abs(math.hypot(P[k][0] - ux, P[k][1] - uy) - r) > tol:
            return None
        a = math.atan2(P[k][1] - uy, P[k][0] - ux)
        da = (a - prev + math.pi) % (2 * math.pi) - math.pi
        s_ = 1 if da > 0 else -1 if da < 0 else 0
        if s_ and sgn and s_ != sgn:
            return None
        sgn = sgn or s_
        tot += da; prev = a
        ch = math.hypot(P[k][0] - P[k - 1][0], P[k][1] - P[k - 1][1])
        sag = r - math.sqrt(max(r * r - ch * ch / 4, 0))
        if sag > tol:
            # didesnis nuokrypis nuo stygos - TIK tolygiai išskaidytame lanke (gretimos stygos panašaus ilgio, pvz. buffer
            #  lankai); ilga tiesi atkarpa šalia kreivės lieka tiese (kitaip lankas „išsipučia" iki 0,5 mm)
            nb = [math.hypot(P[q][0] - P[q - 1][0], P[q][1] - P[q - 1][1]) for q in (k - 1, k + 1) if i < q <= j]
            if sag > CHORD_TOL or not nb or ch > 1.5 * min(nb):
                return None
    if abs(tot) >= math.pi * 1.98:
        return None
    return math.tan(tot / 4)


def fit(pts, closed=True, tol=TOL):
    """taškai -> [(x, y, bulge)] - tiesės + lankai (DXF LWPOLYLINE „xyb"); uždaram - be pasikartojančio galo"""
    P = [tuple(map(float, q[:2])) for q in pts]
    if closed and len(P) > 1 and math.dist(P[0], P[-1]) < 1e-9:
        P = P[:-1]
    n = len(P)
    if n < 4:
        return [(x, y, 0.0) for x, y in P]
    if closed:
        k0 = max(range(n), key=lambda k: _turn(P[k - 1], P[k], P[(k + 1) % n]))   # pradžia - aštriausiame kampe
        P = P[k0:] + P[:k0] + [P[k0]]
    N = len(P) - 1
    TT = [0.0] + [_turn(P[k - 1], P[k], P[k + 1]) for k in range(1, N)] + [0.0]
    out, i = [], 0
    while i < N:
        hi, step = i + 1, 1
        while hi + step <= N and _line_ok(P, i, hi + step, tol):
            hi += step; step *= 2
        step //= 2
        while step >= 1:
            if hi + step <= N and _line_ok(P, i, hi + step, tol):
                hi += step
            step //= 2
        jl, ja, ba = hi, None, 0.0
        j, step, best = i + 2, 1, None
        while j <= N:
            b_ = _arc_ok(P, i, j, tol, TT)
            if b_ is None:
                break
            best = (j, b_); j += step; step *= 2
        if best:
            lo_, hi_ = best[0], min(j, N + 1)
            while hi_ - lo_ > 1:
                md = (lo_ + hi_) // 2
                b_ = _arc_ok(P, i, md, tol, TT)
                if b_ is not None:
                    best = (md, b_); lo_ = md
                else:
                    hi_ = md
            ja, ba = best
        if ja and ja > jl:
            out.append((P[i][0], P[i][1], ba)); i = ja
        else:
            out.append((P[i][0], P[i][1], 0.0)); i = jl
    if not closed:
        out.append((P[-1][0], P[-1][1], 0.0))
    return out


def ring_to_sub(pts, closed=True, tol=TOL):
    """taškai -> subpath (M / L / C): lankai - kubinės Bezier (<= 90° vienai), PDF braižymui"""
    F = fit(pts, closed, tol)
    if not F:
        return []
    sp = [("M", F[0][:2])]
    seq = F + ([F[0]] if closed else [])
    for (x0, y0, b), (x1, y1, _) in zip(seq, seq[1:]):
        if abs(b) < 1e-9:
            sp.append(("L", (x1, y1)))
            continue
        th = 4 * math.atan(b)                                  # lanko kampas (su ženklu)
        ch = math.hypot(x1 - x0, y1 - y0)
        r = ch / (2 * abs(math.sin(th / 2)))
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        nx, ny = -(y1 - y0) / ch, (x1 - x0) / ch                # kairė normalė
        d = r * math.cos(th / 2) * (1 if th > 0 else -1)
        cx, cy = mx + nx * d, my + ny * d
        a0 = math.atan2(y0 - cy, x0 - cx)
        k = max(1, math.ceil(abs(th) / (math.pi / 2)))
        dt = th / k
        for s in range(k):
            t0, t1 = a0 + dt * s, a0 + dt * (s + 1)
            al = 4 / 3 * math.tan(dt / 4)
            p0 = (cx + r * math.cos(t0), cy + r * math.sin(t0)); p3 = (cx + r * math.cos(t1), cy + r * math.sin(t1))
            p1 = (p0[0] - al * r * math.sin(t0), p0[1] + al * r * math.cos(t0))
            p2 = (p3[0] + al * r * math.sin(t1), p3[1] - al * r * math.cos(t1))
            sp.append(("C", p1, p2, p3 if s < k - 1 else (x1, y1)))
    return sp


def smooth_sub(sp, min_pts=6):
    """subpath: jei tik M / L ir >= min_pts taškų - lygios dalys lankais; kitaip - kaip yra"""
    if len(sp) < min_pts or any(s_[0] not in ("M", "L") for s_ in sp):
        return sp
    return ring_to_sub([tuple(s_[1]) for s_ in sp], True)          # path_of uždaro kiekvieną subpath


# ------------------------------------------------------------------ DXF
def fit_dxf_doc(doc, tol=TOL, min_pts=6):
    """visi LWPOLYLINE be lankų (>= min_pts taškų) - tiesės + lankai; grąžina (pakeista, mazgų prieš, po)"""
    n_, before, after = 0, 0, 0
    for lay in [doc.modelspace()] + [b for b in doc.blocks if not b.name.startswith("*")]:
        for e in list(lay.query("LWPOLYLINE")):
            pts = list(e.get_points("xyb"))
            if len(pts) < min_pts or any(abs(p[2]) > 1e-12 for p in pts):
                continue
            F = fit([p[:2] for p in pts], bool(e.closed), tol)
            if len(F) < len(pts):
                e.set_points(F, format="xyb")
                n_ += 1; before += len(pts); after += len(F)
    return n_, before, after


def saveas(doc, path, tol=TOL):
    """DXF išsaugojimas VISIEMS generatoriams: kreivės lankais (v312), mm antraštė (v302)"""
    import ezdxf
    doc.units = ezdxf.units.MM
    doc.header["$INSUNITS"] = 4
    fit_dxf_doc(doc, tol)
    doc.saveas(path)
    return path


def fit_dxf(path, out=None, tol=TOL):
    import ezdxf
    doc = ezdxf.readfile(path)
    r = fit_dxf_doc(doc, tol)
    doc.saveas(out or path)
    return r


def angular_runs(pts, closed=True, min_run=6, max_len=30.0):
    """KAMPUOTA KREIVĖ: ilgiausia seka iš eilės trumpų atkarpų (<= max_len) su mažais posūkiais (0,3°..MAX_TURN)"""
    P = [tuple(q[:2]) for q in pts]
    n = len(P)
    if n < min_run + 1:
        return 0
    best = run = 0
    rng = range(n) if closed else range(1, n - 1)
    for k in rng:
        a, b, c = P[k - 1], P[k], P[(k + 1) % n]
        t = _turn(a, b, c)
        if 0.3 <= t <= MAX_TURN and math.dist(a, b) <= max_len and math.dist(b, c) <= max_len:
            run += 1; best = max(best, run)
        else:
            run = 0
    return best
