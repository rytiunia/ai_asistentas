"""Auselių išdėstymas ant U bėgelių - taisyklė references/auseles.md, Smax lentelė assets/auseles_smax.json.

Koordinatės: mm, y žemyn (viršutinis bėgelis - mažesnis y). Ausėlė visada į rėmo vidų.
place_rail() grąžina ausėlių sąrašą: {"x", "hy", "h", "ext"} - x = ašis, hy = skylės centro y,
h = ausėlės aukštis (es arba daugiau, jei pailginta), ext = pailginta.
"""
import json, math, os
from shapely.geometry import Point

_HERE = os.path.dirname(os.path.abspath(__file__))
SMAX_FILE = os.path.join(_HERE, "..", "assets", "auseles_smax.json")

DEFAULTS = {"inset": 50, "hole_d": 6, "min_edge": 15, "end_window": 300, "step": 5,
            "clear_cap": 40, "ext_max": 250, "min_gap": 150, "end_max": None}


def smax_lookup(depth, font_style, H, override=None):
    """Smax pagal profilį, šriftą ir raidžių aukštį. None = lentelėje '?' -> klausti Ryčio."""
    if override:
        return float(override), "spec"
    tab = json.load(open(SMAX_FILE))
    key = f"U{int(depth)}" + (" script" if font_style == "script" else "")
    cls = "H<=500" if H <= 500 else ("500<H<=800" if H <= 800 else "H>800")
    v = tab.get("table", {}).get(key, {}).get(cls)
    if not v and font_style == "script":           # script be reikšmės -> paprastas x 0.65
        b = tab.get("table", {}).get(f"U{int(depth)}", {}).get(cls)
        v = b * 0.65 if b else None
    return (float(v) if v else None), f"{key} / {cls}"


def _samples(x_lo, x_hi, step):
    n = max(0, int((x_hi - x_lo) // step))
    return [x_lo + i * step for i in range(n + 1)]


def _free(LET, x, y, min_edge):
    p = Point(x, y)
    if LET.contains(p):
        return None
    d = LET.distance(p)
    return d if d >= min_edge else None


def _intervals(pts):
    """[(x, clearance)] -> ištisiniai laisvi intervalai (sąrašai)"""
    out, cur, prev = [], [], None
    for x, c in pts:
        if c is None:
            if cur:
                out.append(cur); cur = []
        else:
            cur.append((x, c))
    if cur:
        out.append(cur)
    return out


def _best_in(iv, cap, toward):
    """didžiausias atstumas iki kontūro (ribojamas cap), lygiųjų atveju - arčiau `toward`"""
    return max(iv, key=lambda p: (min(p[1], cap), -abs(p[0] - toward)))


def place_rail(LET, x0, x1, base_y, inward, es, smax, cfg=None, phys=None):
    """Vieno bėgelio ausėlės - optimizacija (DP per laisvas padėtis), ne tolygus žingsnis.

    Tikslas eilės tvarka:
      1) mažiausias ausėlių kiekis, kai tarpas tarp gretimų <= Smax, o pirmoji / paskutinė
         ne toliau kaip end_max nuo bėgelio galo (konsolė);
      2) be pailgintų ausėlių (pailginta - tik jei kitaip sprendinio nėra, tik prie galų);
      0) KRAŠTINĖS: <= end_window (300) nuo galo, jei ten yra laisva vieta; jei ne - artimiausioje galimoje
         vietoje. Tai svarbiau už kiekį (geriau papildoma ausėlė nei ilga konsolė);
      3) pirmoji ir paskutinė - KUO ARČIAU bėgelio galų (abu galai vienodai, W_END = 3/mm);
      4) didesnis atstumas iki kontūro, tolygesni tarpai.
    base_y - bėgelio briauna rėmo vidaus pusėje, inward = +1 (viršutinis) / -1 (apatinis).
    """
    C = dict(DEFAULTS); C.update(cfg or {})
    st, cap = C["step"], C["clear_cap"]
    xa, xb = x0 + es / 2 + C["inset"], x1 - es / 2 - C["inset"]
    warn = []
    if xb <= xa:
        return [], ["bėgelis per trumpas ausėlėms"]
    soft = C["end_window"]
    end_max = C.get("end_max") or (min(0.5 * smax, 600) if smax else max(soft, 500))
    end_max = max(end_max, soft)
    hy0 = base_y + inward * es / 2

    # kandidatai: (x, hy, h, ext, clearance)
    cands = []
    for x in _samples(xa, xb, st):
        c = _free(LET, x, hy0, C["min_edge"])
        if c is not None:
            cands.append((x, hy0, es, False, c))
    for x in _samples(xa, xb, 2 * st):              # pailgintos - tik prie galų, trumpiausios
        if min(x - x0, x1 - x) > soft or _free(LET, x, hy0, C["min_edge"]) is not None:
            continue
        h = es + st
        while h <= es + C["ext_max"] + 1e-6:
            hy = base_y + inward * (h - es / 2)
            c = _free(LET, x, hy, C["min_edge"])
            if c is not None:
                cands.append((x, hy, h, True, c)); break
            h += st
    cands.sort(key=lambda q: q[0])
    if not cands:
        return [], ["ant bėgelio nėra nė vienos laisvos vietos ausėlei - spręsti ranka"]

    W_EAR, W_EXT = 1e6, 1e4
    # fizika (jei duota): phys = {"load": f(xa, xb) -> kN, "N": kN/ausėlei, "size": "40x40x2", "P": parametrai}
    if phys:
        LD, NR, PP, SZ = phys["load"], phys["N"], phys["P"], phys["size"]

        def seg_ok(xa_, xb_):
            g_ = xb_ - xa_
            F = LD(xa_, xb_)
            if F > NR:
                return False
            L_, _ = rail_limits(SZ, F / max(g_ / 1000, 1e-6), PP)
            return g_ <= L_

        def over_ok(a_end, x_):
            a_ = abs(x_ - a_end)
            F = LD(min(a_end, x_), max(a_end, x_))
            if F > NR / 2:
                return False
            _, C_ = rail_limits(SZ, F / max(a_ / 1000, 1e-6), PP)
            return a_ <= C_
    else:
        def seg_ok(xa_, xb_):
            return True

        def over_ok(a_end, x_):
            return True
    n_min = 2
    if phys and (x1 - x0) > phys["P"]["redundancy"]["long_rail_mm"]:
        n_min = phys["P"]["redundancy"]["min_ears_long_rail"]

    def node_cost(q):
        return W_EAR + (W_EXT + q[2] if q[3] else 0) + 3 * (cap - min(q[4], cap))

    # Rytis patvirtino: pirmoji ir paskutinė ausėlė - KUO ARČIAU bėgelio galo laisvoje vietoje (abu galai
    # vienodai). Svoris 3/mm nusveria tarpo iki kontūro ir tarpų tolygumo baudas (max ~300), bet ne
    # ausėlių kiekį (W_EAR) ir ne pailginimą (W_EXT): 600 mm * 3 = 1800 < 1e4.
    W_END = C.get("end_weight", 3.0)

    def start_cost(q):
        d = q[0] - x0
        return W_END * d + 20 * max(0, d - soft)

    def end_cost(q):
        d = x1 - q[0]
        return W_END * d + 20 * max(0, d - soft)

    def solve(lim_s, lim_e=None, gcap=math.inf):
        lim_e = lim_s if lim_e is None else lim_e
        n = len(cands)
        best, prev = [math.inf] * n, [-1] * n
        for i, q in enumerate(cands):
            if q[0] - x0 <= lim_s and over_ok(x0, q[0]):
                best[i] = node_cost(q) + start_cost(q)
        if smax is None and not phys:               # tik dvi galinės
            fin = [(best[i] + node_cost(cands[j]) + end_cost(cands[j]), i, j)
                   for i in range(n) if best[i] < math.inf
                   for j in range(n) if x1 - cands[j][0] <= lim_e and cands[j][0] - cands[i][0] >= C["min_gap"]]
            if not fin:
                return None
            _, i, j = min(fin)
            return [cands[i], cands[j]]
        st_ = best[:]                                  # pradžios kaina (1 ausėlė)
        pth, prev = [math.inf] * n, [-1] * n          # kelias su >= 2 ausėlėmis
        for j in range(n):
            xj = cands[j][0]
            for i in range(j):
                bi = min(st_[i], pth[i])
                if bi == math.inf:
                    continue
                g = xj - cands[i][0]
                if g < C["min_gap"] or g > min((smax or math.inf) * (1 + C.get("smax_tol", 0.0)), gcap) or not seg_ok(cands[i][0], xj):
                    continue
                v = bi + node_cost(cands[j]) + 200 * (g / (smax or 1000)) ** 2
                if v < pth[j]:
                    pth[j], prev[j] = v, i
        ends = [(pth[j] + end_cost(cands[j]), j) for j in range(n)
                if pth[j] < math.inf and x1 - cands[j][0] <= lim_e and over_ok(x1, cands[j][0])]
        if not ends:
            return None
        _, j = min(ends)
        path = [cands[j]]
        while True:                                    # atgal: jei i pasiektas pradžia pigiau - sustoti
            i = prev[j]
            path.append(cands[i])
            if st_[i] <= pth[i]:
                break
            j = i
        return path[::-1]

    # Rytis patvirtino (abu galai vienodai): kraštinė ausėlė <= end_window (300) nuo bėgelio galo, jei ten yra
    # laisva vieta; jei nėra - ARTIMIAUSIOJE galimoje vietoje (+ end_tol). Šis reikalavimas svarbesnis už
    # mažiausią kiekį: geriau papildoma ausėlė, nei ilga konsolė prie galo.
    tol = C.get("end_tol", 25)
    # Rytis 2026-10-07: NEPAILGINTOS ausėlės visada pirmiau - sprendžiama tik su standartinėmis vietomis;
    # pailgintos įtraukiamos TIK jei be jų sprendinio nėra
    ALL_C = cands
    path, warn_ = None, []
    for use_ext in (False, True):
        cands = [q for q in ALL_C if use_ext or not q[3]]
        if not cands:
            continue
        warn_ = []
        d_s = min(q[0] - x0 for q in cands)
        d_e = min(x1 - q[0] for q in cands)
        lim_s = soft if d_s <= soft else d_s + tol
        lim_e = soft if d_e <= soft else d_e + tol
        path = solve(lim_s, lim_e)
        gcap = math.inf
        while path is not None and len(path) < n_min:              # perteklinis tvirtinimas (>= 3 ant ilgo bėgelio)
            span = path[-1][0] - path[0][0]
            gcap = min(gcap, span / (n_min - 1) * 1.15) if gcap == math.inf else gcap * 0.9
            p2 = solve(lim_s, lim_e, gcap)
            if p2 is None:
                break
            path = p2
        if path is None:
            path = solve(max(lim_s, end_max), max(lim_e, end_max))
            if path is not None:
                warn_.append(f"kraštinė ausėlė toliau nei artimiausia laisva vieta prie galo (tarpas > Smax) - patikrinti")
        if path is None:
            path = solve(x1 - x0)
            if path is not None:
                warn_.append(f"galinė ausėlė toliau nei {end_max:.0f} mm nuo bėgelio galo - patikrinti")
        if path is not None:
            break
    warn += warn_
    if path is None:
        path = solve(x1 - x0) if cands else None
    if path is None and ALL_C:
        # v80 (Rytis 2026-10-10, BB LIETUVA viršus): sprendinio su tarpu <= Smax nėra (ilgi ruožai be laisvos vietos) -
        # GODUS išdėstymas per visą bėgelį, kad ausėlės būtų visur, kur tik yra vietos: nuo artimiausios galui vietos
        # kaskart imama tolimiausia laisva vieta Smax ribose; jei tokios nėra - artimiausia už ribos (perspėjimas);
        # pabaigoje - artimiausia kitam galui. Nepailgintos pirmiau.
        lim_ = (smax or 1000) * (1 + C.get("smax_tol", 0.0))
        cs = sorted([q for q in ALL_C if not q[3]] or ALL_C, key=lambda q: q[0])
        path = [min(cs, key=lambda q: q[0] - x0)]
        last_ = max(cs, key=lambda q: q[0])
        while path[-1][0] < last_[0] - 1:
            nxt = [q for q in cs if C["min_gap"] <= q[0] - path[-1][0] <= lim_]
            if nxt:
                q = max(nxt, key=lambda q: q[0])
                if q[0] >= last_[0] - 1 or not any(qq[0] > q[0] + C["min_gap"] for qq in cs):
                    q = last_
            else:
                beyond = [q for q in cs if q[0] - path[-1][0] > lim_]
                if not beyond:
                    break
                q = min(beyond, key=lambda q: q[0])
                warn.append(f"tarpas {q[0] - path[-1][0]:.0f} mm > Smax {lim_:.0f} tarp x{path[-1][0]:.0f} ir x{q[0]:.0f} (nėra laisvos vietos) - tikrinti")
            path.append(q)
        if x1 - path[-1][0] > end_max:
            warn.append(f"galinė ausėlė {x1 - path[-1][0]:.0f} mm nuo bėgelio galo (laisvos vietos arčiau nėra) - patikrinti")
        if path[0][0] - x0 > end_max:
            warn.append(f"pirmoji ausėlė {path[0][0] - x0:.0f} mm nuo bėgelio galo (laisvos vietos arčiau nėra) - patikrinti")
        warn.append("sprendinio su tarpu <= Smax nėra - godus išdėstymas per visą bėgelį")
    if path is None:
        warn.append("nėra sprendinio su tarpu <= Smax - spręsti ranka")
        return [], warn
    if smax is None and not phys:
        warn.append("Smax lentelėje '?' - tarpinės ausėlės nedėtos, paklausk Ryčio")
    return [{"x": q[0], "hy": q[1], "h": q[2], "ext": q[3]} for q in path], warn


def _phys_checks(phys):
    """(seg_ok, over_ok) vienam bėgeliui - tos pačios patikros kaip place_rail"""
    if not phys:
        return (lambda a, b: True), (lambda e, x: True)
    LD, NR, PP, SZ = phys["load"], phys["N"], phys["P"], phys["size"]

    def seg_ok(xa_, xb_):
        g_ = xb_ - xa_
        F = LD(xa_, xb_)
        if F > NR:
            return False
        L_, _ = rail_limits(SZ, F / max(g_ / 1000, 1e-6), PP)
        return g_ <= L_

    def over_ok(a_end, x_):
        a_ = abs(x_ - a_end)
        F = LD(min(a_end, x_), max(a_end, x_))
        if F > NR / 2:
            return False
        _, C_ = rail_limits(SZ, F / max(a_ / 1000, 1e-6), PP)
        return a_ <= C_
    return seg_ok, over_ok


def place_frame(LET, rails, es, smax, cfg=None, phys=None):
    """Viršutinis + apatinis bėgelis kartu (Rytis patvirtino, 2026-10-07):
      * KRAŠTINĖS ausėlės (pirmoji / paskutinė) kiekvienam bėgeliui atskirai - KUO ARČIAU bėgelio galo,
        bet IŠVENGIANT pailginimo: pirmiau pastumiama į laisvą vietą (pvz. link raidės centro, „c" angoje),
        pailginama tik jei standartinės vietos nėra iki end_max arba neišlaiko konsolė - tada MAŽIAUSIAS
        pailginimas (pastūmus link raidės centro), tik po to artumas galui;
      * TARPINĖS - poromis: viršutinė ir apatinė tame pačiame x (vienoje linijoje); jei tiksliai negalima -
        kuo mažesnis poslinkis (iki align_max); tarpas tarp gretimų <= Smax ir fizikos patikros;
      * mažiausias porų kiekis, tada mažiausias poslinkis, tada tolygumas.
    rails: [{"x0","x1","base","inward","ext_max","phys"}] (2 vnt.: viršus, apačia).
    Grąžina (ears_per_rail, warnings) arba (None, warnings), jei poromis neišeina."""
    C = dict(DEFAULTS); C.update(cfg or {})
    st, mg = C["step"], C["min_gap"]
    soft = C["end_window"]
    end_max = C.get("end_max") or (min(0.5 * smax, 600) if smax else 600)
    end_max = max(end_max, soft)
    align_max = C.get("align_max", 150)
    warn = []
    info = []
    for r in rails:
        x0, x1, base, inw = r["x0"], r["x1"], r["base"], r["inward"]
        xa, xb = x0 + es / 2 + C["inset"], x1 - es / 2 - C["inset"]
        hy0 = base + inw * es / 2
        std = [(x, c) for x in _samples(xa, xb, st) for c in [_free(LET, x, hy0, C["min_edge"])] if c is not None]
        ext = []
        for x in _samples(xa, xb, st):
            if min(x - x0, x1 - x) > end_max or _free(LET, x, hy0, C["min_edge"]) is not None:
                continue
            h = es + st
            while h <= es + r.get("ext_max", C["ext_max"]) + 1e-6:
                hy = base + inw * (h - es / 2)
                c = _free(LET, x, hy, C["min_edge"])
                if c is not None:
                    ext.append((x, hy, h, c)); break
                h += st
        seg_ok, over_ok = _phys_checks(r.get("phys"))
        info.append({"x0": x0, "x1": x1, "hy0": hy0, "std": std, "ext": ext, "seg_ok": seg_ok, "over_ok": over_ok})

    def end_ear(I, at_start):
        e_ = I["x0"] if at_start else I["x1"]
        d = (lambda x: x - e_) if at_start else (lambda x: e_ - x)
        for x, c in sorted(I["std"], key=lambda q: d(q[0])):          # 1) standartinė, kuo arčiau galo
            if d(x) > end_max:
                break
            if I["over_ok"](e_, x):
                return {"x": x, "hy": I["hy0"], "h": es, "ext": False}
        # 1b) Rytis 2026-10-07: NEPAILGINTA ausėlė visada pirmiau už pailgintą - jei lange nėra laisvos vietos,
        #     imama artimiausia standartinė už lango, jei ją išlaiko konsolės / inkaro patikra
        for x, c in sorted(I["std"], key=lambda q: d(q[0])):
            if I["over_ok"](e_, x):
                return {"x": x, "hy": I["hy0"], "h": es, "ext": False}
        # 2) pailginta - tik jei kitaip negalima: lange <= 300 mm nuo galo MAŽIAUSIAS pailginimas (pastumti link
        #    raidės centro, pvz. „c" viduje), tada arčiau galo; už lango - tik jei lange nieko nėra
        for x, hy, h, c in sorted(I["ext"], key=lambda q: (d(q[0]) > soft, q[2], d(q[0]))):
            if I["over_ok"](e_, x):
                return {"x": x, "hy": hy, "h": h, "ext": True}
        if I["std"]:                                                    # 3) artimiausia, su perspėjimu
            x, c = min(I["std"], key=lambda q: d(q[0]))
            warn.append(f"kraštinė ausėlė {d(x):.0f} mm nuo galo - konsolė nepatikrinta / per ilga, patikrinti")
            return {"x": x, "hy": I["hy0"], "h": es, "ext": False}
        return None

    T, B = info
    ends = [end_ear(T, True), end_ear(T, False), end_ear(B, True), end_ear(B, False)]
    if any(e is None for e in ends):
        return None, warn + ["nėra laisvos vietos kraštinei ausėlei - spręsti ranka"]
    sT, eT, sB, eB = ends
    # Smax lentelė - praktinė rekomendacija: leidžiama viršyti iki smax_tol (15 %), jei taip sutaupoma ausėlių pora
    # (Rytis 2026-10-07: MATKROKEN užtenka 8, ne 10); fizikos patikros (apkrova, įlinkis, konsolė) lieka griežtos
    lim = min((smax or math.inf) * (1 + C.get("smax_tol", 0.0)), C.get("gap_cap", math.inf))

    # tarpinių porų mazgai: (xt, xb, poslinkis, prioritetas)
    Bx = [x for x, _ in B["std"]]
    import bisect
    nodes = []
    for xt, ct in T["std"]:
        if xt <= sT["x"] + mg or xt >= eT["x"] - mg:
            continue
        k = bisect.bisect_left(Bx, xt)
        best = None
        for j in (k - 1, k):
            if 0 <= j < len(Bx):
                xb = Bx[j]
                if xb <= sB["x"] + mg or xb >= eB["x"] - mg:
                    continue
                off = abs(xb - xt)
                if off <= align_max and (best is None or off < best[1]):
                    best = (xb, off)
        if best:
            nodes.append((xt, best[0], best[1]))
    nodes.sort(key=lambda q: (q[0] + q[1]) / 2)
    W_PAIR, W_OFF = 1e6, 50.0
    # v77 (Rytis 2026-10-10): kelių eilučių rėmas - antros eilutės ausėlės ŠACHMATIŠKAI (ne vienoje linijoje su kitos
    # eilutės ausėlėmis): mazgas arčiau nei stagger_gap nuo `avoid_x` gauna baudą (naudojamas tik jei kitaip neišeina)
    _avoid = C.get("avoid_x") or []
    _sg = C.get("stagger_gap", 250)

    def _stag(x):
        return W_OFF * 2 * _sg if any(abs(x - a) < _sg for a in _avoid) else 0.0

    def ok_t(a, b):
        return mg <= b - a <= lim and T["seg_ok"](a, b)

    def ok_b(a, b):
        return mg <= b - a <= lim and B["seg_ok"](a, b)

    def evn(g_):
        return 200 * (g_ / (smax or 1000)) ** 2

    n_min = C.get("n_min", 2)
    need = max(0, n_min - 2)
    # DP: būsena = (mazgas, tarpinių skaičius iki need), kaina
    INF = math.inf
    n = len(nodes)
    cost = [[INF] * (need + 1) for _ in range(n)]
    prev = [[None] * (need + 1) for _ in range(n)]
    for i, (xt, xb, off) in enumerate(nodes):
        if ok_t(sT["x"], xt) and ok_b(sB["x"], xb):
            cost[i][min(1, need)] = W_PAIR + W_OFF * off + evn(xt - sT["x"]) + evn(xb - sB["x"]) + _stag(xt)
    for i in range(n):
        for k in range(need + 1):
            if cost[i][k] == INF:
                continue
            xt, xb, _ = nodes[i]
            for j in range(i + 1, n):
                yt, yb, off = nodes[j]
                if yt - xt > lim and yb - xb > lim:
                    break
                if not (ok_t(xt, yt) and ok_b(xb, yb)):
                    continue
                k2 = min(k + 1, need)
                v = cost[i][k] + W_PAIR + W_OFF * off + evn(yt - xt) + evn(yb - xb) + _stag(yt)
                if v < cost[j][k2]:
                    cost[j][k2], prev[j][k2] = v, (i, k)
    best = None
    if need == 0 and ok_t(sT["x"], eT["x"]) and ok_b(sB["x"], eB["x"]):
        best = (evn(eT["x"] - sT["x"]) + evn(eB["x"] - sB["x"]), None)
    for i in range(n):
        c_ = cost[i][need]
        if c_ == INF:
            continue
        xt, xb, _ = nodes[i]
        if ok_t(xt, eT["x"]) and ok_b(xb, eB["x"]):
            v = c_ + evn(eT["x"] - xt) + evn(eB["x"] - xb)
            if best is None or v < best[0]:
                best = (v, (i, need))
    if best is None:
        return None, warn + ["tarpinių ausėlių poromis (vienoje linijoje) sudėti nepavyko"]
    mids = []
    stt = best[1]
    while stt is not None:
        i, k = stt
        mids.append(nodes[i])
        stt = prev[i][k]
    mids.reverse()
    top = [sT] + [{"x": xt, "hy": T["hy0"], "h": es, "ext": False} for xt, _, _ in mids] + [eT]
    bot = [sB] + [{"x": xb, "hy": B["hy0"], "h": es, "ext": False} for _, xb, _ in mids] + [eB]
    offs = [o for _, _, o in mids if o > 0]
    if offs:
        warn.append(f"{len(offs)} porų poslinkis iki {max(offs):.0f} mm (tiksliai vienoje linijoje negalima dėl raidžių)")
    return [top, bot], warn


# ------------------------------------------------------------------ fizika: vėjas, bėgelis, inkaras
TV_FILE = os.path.join(_HERE, "..", "assets", "tvirtinimas.json")


def load_params(override=None):
    P = json.load(open(TV_FILE))
    for k, v in (override or {}).items():
        if isinstance(v, dict) and isinstance(P.get(k), dict):
            P[k].update(v)
        else:
            P[k] = v
    return P


def wind_qp(vb0=24.0, terrain="III", z_m=8.0, rho=1.25, **_):
    """EN 1991-1-4: qp(z) = ce(z)·qb, kN/m² (c0 = 1, kI = 1)."""
    z0, zmin = {"0": (0.003, 1), "I": (0.01, 1), "II": (0.05, 2), "III": (0.3, 5), "IV": (1.0, 10)}[str(terrain)]
    z = max(z_m, zmin)
    kr = 0.19 * (z0 / 0.05) ** 0.07
    cr = kr * math.log(z / z0)
    Iv = 1 / math.log(z / z0)
    qb = 0.5 * rho * vb0 ** 2 / 1000
    return (1 + 7 * Iv) * cr ** 2 * qb


def u_section(size):
    """U b x h x t (web b lygiagreti sienai, flanšai h statmeni sienai). Lenkimas nuo apkrovos statmenos sienai.
    Grąžina I (mm4), W (mm3)."""
    b, h, t = [float(v) for v in str(size).lower().split("x")]
    parts = [(b * t, t / 2, b * t ** 3 / 12)] + [(t * (h - t), t + (h - t) / 2, t * (h - t) ** 3 / 12)] * 2
    A = sum(p[0] for p in parts)
    yc = sum(p[0] * p[1] for p in parts) / A
    I = sum(p[2] + p[0] * (p[1] - yc) ** 2 for p in parts)
    return I, I / max(yc, h - yc)


def rail_limits(size, w_kNm, P):
    """Didžiausias tarpas (laisvai atremta sija) ir konsolė pagal stiprumą ir įlinkį, kai linijinė apkrova w (kN/m)."""
    I, W = u_section(size)
    a = P["alu"]
    w = max(w_kNm, 1e-6)                                            # N/mm = kN/m
    M_rd = a["f0_MPa"] / a["gamma_M1"] * W                          # Nmm
    g = P["gamma_Q"]
    L_str = math.sqrt(8 * M_rd / (g * w))
    L_def = (384 * a["E_MPa"] * I / (5 * w * a["defl_span"])) ** (1 / 3)
    C_str = math.sqrt(2 * M_rd / (g * w))
    C_def = (8 * a["E_MPa"] * I / (w * a["defl_cant"])) ** (1 / 3)
    return min(L_str, L_def), min(C_str, C_def)
