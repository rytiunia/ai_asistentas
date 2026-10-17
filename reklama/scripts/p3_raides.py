#!/usr/bin/env python3
"""v336 (Rytis 2026-10-17, etalonas ALT8118 Clas Ohlson „Profile 3"): P3 - HALO (reverse-lit) raidės.

Konstrukcija: korpusas / priekis Alu (priekis 2 mm, šonas 1 mm, RAL), GALAS balta plexi 8 mm (varžtai per šoną į plexi
kraštą) ARBA 4 mm su PVC tvirtinimo borteliu (varžtai per šoną į bortelį, kaip 5S); LED raidės viduje ant galo, šviečia
ATGAL (į sieną / reflektorių). Raidė ant DISTANCERIŲ (spacer, vamzdelis + ilgasriegis) prie bėgelio (rėmo).
Variantas su REFLEKTORIAIS: plokštė = raidės kontūras + 5 mm (outside), tvirtinama UŽ raidės prie bėgelio; distanceriai -
nuo reflektoriaus iki raidės galo.

TVIRTINIMAS (Rytis 2026-10-17): kaip P6 (kvadrato / trikampio principas, tvirtinimas.shape_n + FPS), TIK tvirtinimo taškas -
TVIRTINAMO PLOTO CENTRE, ne šone ar krašte: tvirtinamas plotas = raidės (galo) ir bėgelio persidengimo komponentas
(pvz. A - kojelės plotas, kuriuo raidė remiasi į rėmą); taškas - to ploto centroidas (jei netelpa distanceris - artimiausia
leistina vieta). Ilgas plotas išilgai bėgelio (> split mm) dalijamas į lygias dalis, taškas - kiekvienos dalies centre.

cfg(spec)                       - spec "p3" su numatytomis reikšmėmis (nežinomos - klausimyne, lape „?")
spacers(letters, rails, P)      - [(x, y, raidės nr.)], klaidos
section(K, x, y, w, h, depth, P, ...) - PROFILE P3 pjūvio blokas (antraštė + rėmelis, kaip p1_typical)
write_dxf(path, letters, sp, P) - gamybos DXF: priekis, galas su distancerių skylėmis, reflektorius (kreivės lankais)
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shapely.geometry import box as _box, Point as _Pt  # noqa: E402
from shapely.ops import nearest_points  # noqa: E402

# v337 (Rytis 2026-10-17, atsakymai į klausimyną) - STANDARTAI:
#  distanceris Ø16, ilgis pagal raidės gylį: < 60 mm - 20, >= 60 mm - 30; sluoksniai: rėmas + reflektorius (jei yra) +
#  distanceriai + raidės; M4 ilgasriegis (plexi Ø4, reflektorius / bėgelis Ø4,5); reflektorius - ACM (RAL pagal užklausą
#  arba dažyta), būna Alu 1,5; LED ant plexi viduje, 6500K, žingsnis tikslinamas; maketo lape plexi - tik „transparent
#  plexiglass"; galas 8 mm raidėms < 400 mm aukščio, >= 400 mm - 4 mm + PVC bortelis (kaip 5S); varžtai per šoną
#  DIN 7982 2,9 x 9,5; ilgas tvirtinamas plotas - taškų daugiau; drenažas - Ø8 puslankiai galo kontūre (kaip P6 ant rėmo).
DEF = {
    "spacer": None,        # None - pagal gylį (SPACER_BY_DEPTH)
    "spacer_d": 16,
    "rod": "M4",
    "back_hole": 4,
    "rod_hole": 4.5,
    "back": None,          # None - pagal raidžių aukštį (BACK_BY_HEIGHT)
    "side_t": 1.0,         # šonas Alu 1 (pjūvio brėžiniui)
    "back_inset": 0.7,     # v341 (Rytis 2026-10-17): P3 DUGNAS (plexi galas) - 0,7 mm inside nuo raidės kontūro
    "face_t": 2.0,         # priekis Alu 2
    "edge": 5,             # distancerio krašto atstumas nuo galo krašto (mm)
    "split": 400,          # ilgas tvirtinamas plotas išilgai bėgelio dalijamas kas <= split
    "reflector": False,    # v339: standartas P3 - be reflektorių; „P3+reflector" (spec front) - su
    "refl_off": 5,         # reflektorius = kontūras + 5 mm (outside)
    "refl_mat": "ACM 3 mm",   # standartas ACM; arba "Alu 1.5 mm"
    "refl_ral": "?",       # pagal užklausą
    "pvc_edge": None,      # None - pagal galą (4 mm -> True)
    "screw": "DIN 7982 2.9 x 9.5",
    "led": "LED modules on plexi inside, 6500K",
    "drain_d": 8,
    "drain": True,         # exterior - Ø8 puslankiai galo kontūre
}
SPACER_BY_DEPTH = (60, 20, 30)     # gylis < 60 -> 20, >= 60 -> 30
BACK_BY_HEIGHT = (400, 8, 4)       # raidės aukštis < 400 -> 8, >= 400 -> 4 + PVC


def cfg(spec, letter_h=None):
    """letter_h - aukščiausios raidės aukštis (mm): galo storis pagal BACK_BY_HEIGHT, jei spec "p3" "back" nenurodytas"""
    import re
    import p6_front as P6F
    P = dict(DEF)
    P["reflector"] = bool(P6F.parse(spec.get("front", "P3")).get("reflector"))   # v339: „P3+reflector" užklausoje
    P.update(spec.get("p3") or {})
    d_ = float(spec.get("depth_mm", 60))
    if P["spacer"] is None:
        P["spacer"] = SPACER_BY_DEPTH[1] if d_ < SPACER_BY_DEPTH[0] else SPACER_BY_DEPTH[2]
    if P["back"] is None:
        P["back"] = BACK_BY_HEIGHT[1] if (letter_h or 0) < BACK_BY_HEIGHT[0] else BACK_BY_HEIGHT[2]
    if P["pvc_edge"] is None:
        P["pvc_edge"] = float(P["back"]) < 8
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*mm", str(P["refl_mat"]))
    P["refl_t"] = float(m.group(1).replace(",", ".")) if m else 3.0
    P["r"] = float(P["spacer_d"]) / 2
    return P


def drain_points(back, prom=5.0, step=1.0, merge=30.0):
    """Ø8 PUSLANKIAI galo kontūre (kaip P6 ant rėmo, p6_dxf.drain_points notch): išorinio kontūro lokalūs žemiausi taškai
    (y žemyn), kai abiem kryptimis kontūras pakyla >= prom; plokščia apačia - jos vidurys; virš taško medžiaga, po juo tuščia"""
    out = []
    for poly in _parts(back):
        ring = poly.exterior
        L = ring.length
        n = max(16, int(L / step))
        pts = [ring.interpolate(L * i / n) for i in range(n)]
        ys = [p.y for p in pts]
        for i in range(n):
            y = ys[i]
            if y < ys[i - 1] - 1e-6 or y < ys[(i + 1) % n] - 1e-6:
                continue
            ok, span = True, [i]
            for dirn in (1, -1):
                j, rose = i, False
                for _ in range(n):
                    j = (j + dirn) % n
                    if ys[j] > y + 0.3:
                        ok = False; break
                    if abs(ys[j] - y) <= 0.3:
                        span.append(j)
                    if ys[j] <= y - prom:
                        rose = True; break
                if not ok or not rose:
                    ok = False; break
            if not ok:
                continue
            xs_ = sorted(pts[k].x for k in span)
            xm = (xs_[0] + xs_[-1]) / 2
            q = min((pts[k] for k in span), key=lambda p: abs(p.x - xm))
            if not (poly.contains(_Pt(q.x, q.y - 6)) and poly.contains(_Pt(q.x, q.y - 2.5))
                    and not poly.contains(_Pt(q.x, q.y + 2.5))):
                continue
            if all(math.hypot(q.x - a, q.y - b) > merge for a, b in out):
                out.append((round(q.x, 2), round(q.y, 2)))
    return out


def back_shape(o, P, sp=()):
    """plexi galas (dugnas): kontūras - back_inset (0,7), drenažo Ø8 puslankiai (exterior); grąžina (geom, drenažo centrai)"""
    import kreives as KR
    from shapely.ops import unary_union
    b = o["geom"].buffer(-P["back_inset"], quad_segs=KR.BUF_QS)
    if not P.get("drain"):
        return b, []
    dr = [q for q in drain_points(b) if all(math.hypot(q[0] - x, q[1] - y) > P["r"] + P["drain_d"] for x, y, *_ in sp)]
    if dr:
        b = b.difference(unary_union([_Pt(q).buffer(P["drain_d"] / 2, quad_segs=64) for q in dr]))
    return b, dr


def _parts(g):
    return [q for q in getattr(g, "geoms", [g]) if q.geom_type == "Polygon" and not q.is_empty]


def _rail_geom(rl):
    """bėgelio plotas ir ilgoji kryptis: h / v - stačiakampis, įstrižas („d") - jo poly"""
    from shapely.geometry import Polygon
    if rl.get("poly") and rl["kind"] not in ("h", "v"):
        band = Polygon(rl["poly"]).buffer(0)
        mr = list(band.minimum_rotated_rectangle.exterior.coords)[:3]
        e1 = (mr[1][0] - mr[0][0], mr[1][1] - mr[0][1]); e2 = (mr[2][0] - mr[1][0], mr[2][1] - mr[1][1])
        lu, sw = (e1, math.hypot(*e2)) if math.hypot(*e1) >= math.hypot(*e2) else (e2, math.hypot(*e1))
        n = math.hypot(*lu) or 1
        return band, (lu[0] / n, lu[1] / n), sw
    band = _box(rl["x0"], rl["y0"], rl["x1"], rl["y1"])
    if rl["kind"] == "h":
        return band, (1.0, 0.0), rl["y1"] - rl["y0"]
    return band, (0.0, 1.0), rl["x1"] - rl["x0"]


def candidates(o, rails, P):
    """tvirtinami plotai (raidės galas ∩ bėgelis) -> jų centrai [(x, y, plotas, bėgelio nr., t išilgai bėgelio, u)]"""
    from shapely import affinity
    geom = o["geom"]
    r = P["r"]
    back = geom.buffer(-P["back_inset"])
    allowed = geom.buffer(-(P["back_inset"] + r + P["edge"]))
    out = []
    for ri, rl in enumerate(rails):
        band, u, w_ = _rail_geom(rl)
        bx = band.bounds
        if not (bx[2] > o["bb"][0] and bx[0] < o["bb"][2] and bx[3] > o["bb"][1] and bx[1] < o["bb"][3]):
            continue
        sh = max(0.0, min(r, w_ / 2 - 0.5))           # distancerio centras - bėgelio sienelėje (Ø16 ant 30 - ±7)
        rb = band.buffer(-sh, join_style=2) if sh > 0 else band
        ang = math.degrees(math.atan2(u[1], u[0]))
        for comp in _parts(back.intersection(band)):
            if comp.area < 1:
                continue
            cr = affinity.rotate(comp, -ang, origin=(0, 0))          # bėgelio kryptis -> x
            a_, b_ = cr.bounds[0], cr.bounds[2]
            L = b_ - a_
            n = max(1, math.ceil(L / float(P["split"])))
            pieces = [comp] if n == 1 else [
                affinity.rotate(cr.intersection(_box(a_ + L * k / n, -1e7, a_ + L * (k + 1) / n, 1e7)), ang, origin=(0, 0))
                for k in range(n)]
            for pc in pieces:
                for pp in _parts(pc):
                    tgt = pp.intersection(allowed).intersection(rb)
                    if tgt.is_empty:
                        continue
                    c = pp.centroid
                    q = c if tgt.contains(c) else nearest_points(tgt, c)[0]
                    out.append((round(q.x, 1), round(q.y, 1), pp.area, ri, q.x * u[0] + q.y * u[1], u))
    return out


def select(o, cands, P):
    """kiek ir kurie: tvirtinimas.shape_n (kvadratas 4, trikampis 3 ...) + FPS kaip P6 D3.2 (p6_dxf.shape_holes)"""
    import tvirtinimas as TV
    # tame pačiame bėgelyje per arti (< 2 Ø) - lieka didesnio ploto
    cs = []
    for q in sorted(cands, key=lambda q: -q[2]):
        if all(math.dist(q[:2], s[:2]) >= 2 * P["spacer_d"] for s in cs):
            cs.append(q)
    n_t = TV.shape_n(o["geom"], o["bb"], 0.16)
    if len(cs) <= 2:
        return [q[:2] for q in cs], n_t
    pts = [q[:2] for q in cs]
    info = {q[:2]: q for q in cs}
    sel = [TV.fps_start(pts, o["geom"])]
    w_ = o["bb"][2] - o["bb"][0]
    dmin = max(20, 0.25 * min(w_, o["bb"][3] - o["bb"][1]))
    xy = list(o["geom"].convex_hull.exterior.coords)

    def ok(q):
        ri, t, u = info[q][3], info[q][4], info[q][5]
        same = [info[s][4] for s in sel if info[s][3] == ri]
        span = max(p_[0] * u[0] + p_[1] * u[1] for p_ in xy) - min(p_[0] * u[0] + p_[1] * u[1] for p_ in xy)
        if any(abs(ts - t) < max(dmin, 0.3 * span) for ts in same):
            return False                                  # A viršūnė: du kojų taškai - vienas (trikampis)
        lo = [ts for ts in same if ts < t]; hi = [ts for ts in same if ts > t]
        if lo and hi and min(hi) - max(lo) < 1000:
            return False                                  # tarp dviejų to bėgelio taškų - nestabilina
        return min(math.dist(q, s) for s in sel) >= dmin
    while len(sel) < min(n_t, len(pts)):
        rest = [q for q in pts if q not in sel and ok(q)]
        if not rest:
            break
        sel.append(max(rest, key=lambda q: min(math.dist(q, s) for s in sel)))
    return sel, n_t


def spacers(letters, rails, P):
    """visos raidės -> distancerių taškai [(x, y, i)], klaidos (raidė < 2 distancerių - lapo klaida)"""
    out, err = [], []
    # v338 (Rytis 2026-10-17: „ant statmenų tvirtinimai nesideda, išimtis tik labai didelės raidės su papildomais skersiniais
    #  (taisyklė bus vėliau)"): distanceriai TIK ant horizontalių bėgelių; statmenys / įstrižai - ne. Dalis, kurios joks
    #  horizontalus bėgelis nekerta (akcentas, taškas), - ant savo laikiklio (acc / ext_holder), kaip P6 D3.2 (v85).
    hr = [r for r in rails if r["kind"] == "h"]
    holders = [r for r in rails if r["kind"] != "h" and (r.get("acc") or r.get("ext_holder"))]
    for i, o in enumerate(letters):
        rails = hr if candidates(o, hr, P) else holders
        sel, n_t = select(o, candidates(o, rails, P), P)
        for sp_ in (250, 160):                      # trūksta iki formos sk. (D - 2 bėgeliai po 1 plotą) - platų plotą
            if len(sel) >= n_t:                     #  dalinti į lygias dalis, taškas kiekvienos dalies centre
                break
            s2, _ = select(o, candidates(o, rails, dict(P, split=sp_)), P)
            if len(s2) > len(sel):
                sel = s2
        if len(sel) < 2:
            err.append(f"P3 raidė {i + 1} (x {o['bb'][0]:.0f}): tik {len(sel)} distanceris(-iai) - tvirtinamo ploto ant "
                       f"bėgelio nepakanka (reikia >= 2; keisti rėmą / statmenį)")
        out += [(x, y, i) for x, y in sel]
    return out, err


# ------------------------------------------------------------------ PROFILE P3 pjūvis
def section(K, x, y, w, h, depth, P, title=None, numbers=None, ears=True, rail_kind="u", spacer_lbl=None):
    """P3 tipinis pjūvis (schema): siena | U bėgelis (+ ausėlė) | [reflektorius] | distanceris + ilgasriegis |
    plexi galas 8 (varžtas per šoną) arba 4 + PVC bortelis | LED ant galo (šviečia atgal) | šonas Alu 1 | priekis Alu 2."""
    from reportlab.lib.colors import HexColor
    nm = {"face": 1, "ret": 2, "back": 3, "led": 4, "mount": 5, "fit": 6, "spacer": 7, "refl": 8, "pvc": "A", "screw": "B"}
    nm.update(numbers or {})
    K.header(x, y, w, title or "PROFILE P3 (HALO) - TYPICAL SECTION")
    K.rect(x, y + 12, w, h - 12, lw=0.6)
    K.set_view(True)
    px0, py0, pw_, ph_ = x, y + 12, w, h - 12
    SECT = HexColor("#111111")
    PLX = HexColor("#F4F7FA")
    refl = bool(P.get("reflector"))
    yt, yb = py0 + 30, py0 + ph_ - 22                      # raidės štrichas (šonai)
    ym = (yt + yb) / 2
    # mastelis: siena 10 | bėgelis 30 | refl | tarpas | gylis + balionai 24
    tot = 30 + (P["refl_t"] if refl else 0) + float(P["spacer"]) + depth
    k = min((pw_ - 58) / tot, 1.2)
    wall = px0 + 22
    xr1 = wall + 30 * k                                     # bėgelio sienelė prie raidės
    xf0 = xr1 + (P["refl_t"] * k if refl else 0)            # reflektoriaus priekis
    xb0 = xf0 + float(P["spacer"]) * k                      # raidės galas
    xf = xb0 + depth * k                                    # priekis
    # v340 (Rytis 2026-10-17: „nereikia sienos simbolio profilio pjūvyje") - siena nebraižoma, rėmas nuo sienos plokštumos
    # U bėgelis (anga į sieną) + ausėlė
    t_, Uh = 2 * k, 30 * k
    uy = ym - Uh / 2
    K.poly([(wall, uy), (xr1, uy), (xr1, uy + Uh), (wall, uy + Uh), (wall, uy + Uh - t_), (xr1 - t_, uy + Uh - t_),
            (xr1 - t_, uy + t_), (wall, uy + t_)], fill=HexColor("#B4B4B4"), lw=0.4)
    if ears:
        K.poly([(wall, uy + Uh - t_), (wall + t_, uy + Uh - t_), (wall + t_, yb + 12), (wall, yb + 12)],
               fill=HexColor("#8C8C8C"), lw=0.4)
        K.line(wall - 6, yb + 6, wall + t_ + 4, yb + 6, 0.2, K.GREY, dash=([3, 1, 1, 1], 0))
    # reflektorius (+5 mm už raidės kontūro)
    if refl:
        ro = P["refl_off"] * k
        K.rect(xr1, yt - ro, P["refl_t"] * k, (yb - yt) + 2 * ro, fill=HexColor("#FFF6D6"), lw=0.4)
    # distanceris + ilgasriegis
    r = P["r"] * k
    K.rect(xf0, ym - r, xb0 - xf0, 2 * r, fill=HexColor("#D9D9D9"), lw=0.35)
    rod_end = xb0 + (min(6.0, float(P["back"]) - 1.5) * k if float(P["back"]) >= 8 else float(P["back"]) * k + 3)
    K.rect(xr1 - t_ - 1.8, ym - 1.6, rod_end - (xr1 - t_ - 1.8), 3.2, fill=HexColor("#3A3A3A"), lw=0.2)
    K.rect(xr1 - t_ - 3.2, ym - 3.0, 1.4, 6.0, fill=HexColor("#3A3A3A"), lw=0.2)      # veržlė bėgelio viduje
    if float(P["back"]) < 8:
        K.rect(rod_end, ym - 3.0, 1.4, 6.0, fill=HexColor("#3A3A3A"), lw=0.2)         # veržlė raidės viduje
    K.line(wall - 6, ym, xb0 + float(P["back"]) * k + 6, ym, 0.2, K.GREY, dash=([3, 1, 1, 1], 0))
    # raidė: galas plexi (vidiniame šono krašte), šonai Alu 1, priekis Alu 2
    bt = float(P["back"]) * k
    RT, TF = max(1.4, P["side_t"] * k * 1.4), max(2.2, P["face_t"] * k * 1.2)
    K.rect(xb0, yt + RT, bt, yb - yt - 2 * RT, fill=PLX, lw=0.45)
    K.rect(xb0, yt, xf - TF - xb0, RT, fill=SECT, lw=0.3)
    K.rect(xb0, yb - RT, xf - TF - xb0, RT, fill=SECT, lw=0.3)
    K.rect(xf - TF, yt, TF, yb - yt, fill=SECT, lw=0.3)
    if P["pvc_edge"]:                                      # PVC bortelis (3 x 15) ant galo, prie šono; varžtas per šoną
        for top in (True, False):
            yy = yt + RT if top else yb - RT - 3 * k
            K.rect(xb0 + bt, yy, 15 * k, 3 * k, fill=HexColor("#D9D9D9"), lw=0.3)
            sx = xb0 + bt + 7.5 * k
            K.rect(sx - 0.9, (yt - 1.2) if top else (yb - RT - 3 * k), 1.8, RT + 3 * k + 1.2, fill=HexColor("#3A3A3A"), lw=0.2)
    else:                                                  # varžtas per šoną į plexi kraštą
        for top in (True, False):
            sx = xb0 + bt / 2
            K.rect(sx - 0.9, (yt - 1.2) if top else (yb - RT - 4), 1.8, RT + 5.2, fill=HexColor("#3A3A3A"), lw=0.2)
    # LED ant galo (vidus), šviesa atgal per plexi
    lx = xb0 + bt
    for yy in (yt + (yb - yt) * 0.30, yt + (yb - yt) * 0.70):
        K.rect(lx, yy - 3.5, 3.0, 7.0, fill=HexColor("#FFE066"), lw=0.3)
    YEL = HexColor("#E0A800")
    for ya, yb_ in ((yt + 6, yt - 10), (ym - 10, ym - 22), (yb - 6, yb + 10)):
        K.line(xb0 - 1, ya, xf0 + 2, yb_, 0.5, YEL, dash=([2, 1.2], 0))
    K.set_view(False)
    # matmenys: gylis | tarpas | (reflektorius) | bėgelis
    _ye = yt - (P["refl_off"] * k if refl else 0)
    if refl:                                                # v340: reflektoriaus storis - ne grandinėje (be „?" tarpo)
        K.hchain(py0 + 14, [wall, xr1], [uy, uy], [f"{30:.0f}"], 7)
        K.hchain(py0 + 14, [xf0, xb0, xf], [_ye] * 3, [spacer_lbl or f"{float(P['spacer']):.0f}", f"{depth:.0f}"], 7)
    else:
        K.hchain(py0 + 14, [wall, xr1, xb0, xf], [uy, uy, yt, yt], [f"{30:.0f}", spacer_lbl or f"{float(P['spacer']):.0f}",
                                                                     f"{depth:.0f}"], 7)
    # balionai
    K.leader(xf - TF / 2, ym + 4, xf + 14, ym + 4, nm["face"])
    K.leader(xb0 + (xf - xb0) * 0.6, yb - RT / 2, xf + 14, yb - 8, nm["ret"])
    K.leader(xb0 + bt / 2, yt + (yb - yt) * 0.85, xb0 + bt / 2 + 18, yb + 12, nm["back"], 5)
    K.leader(lx + 1.5, yt + (yb - yt) * 0.30, xf - 16, yt + (yb - yt) * 0.18, nm["led"], 5)
    K.leader(wall + 10, uy, wall + 6, py0 + 22, nm["mount"], 5)
    if ears:
        K.leader(wall + t_ / 2, yb + 9, wall - 14, yb + 4, nm["fit"], 5)
    K.leader((xf0 + xb0) / 2, ym + r, (xf0 + xb0) / 2 + 4, yb + 14, nm["spacer"], 5)
    if refl:
        K.leader(xr1 + P["refl_t"] * k / 2, yt + 4, xr1 - 12, (yt + uy) / 2, nm["refl"], 5)
    if P["pvc_edge"]:
        K.leader(xb0 + bt + 10 * k, yt + RT + 1.5 * k, xb0 + bt + 30, yt + 12, nm["pvc"], 5)


# ------------------------------------------------------------------ DXF
def write_dxf(path, letters, sp, P, frame=(), ears=()):
    """v341 (Rytis 2026-10-17: „dxf pateikiami su atskiromis grupėmis: rėmas - viena grupė, dugnas su skylėmis - antra grupė,
    priekis - 3 grupė"): kaip P6 (p6_dxf.group_layers) - kiekvienas sluoksnis savo BLOCK + INSERT + DXF GROUP ->
    Corel / AutoCAD atskiros grupės: 1_REMAS (bėgeliai, statmenys, ausėlės su Ø), 2_DUGNAS (plexi galas -0,7 su distancerių
    Ø skylėmis ir drenažo puslankiais), 3_PRIEKIS (raidės kontūras), 4_REFLEKTORIUS (tik P3+reflector: +5 su Ø).
    frame - [poly taškai], ears - [(x0, y0, x1, y1, hx, hy, d)]. Vaizdas iš priekio, y aukštyn, kreivės lankais."""
    import ezdxf
    import kreives as KR
    doc = ezdxf.new("R2010", setup=True)
    doc.units = ezdxf.units.MM
    LAY = [("1_REMAS", 5), ("2_DUGNAS", 1), ("3_PRIEKIS", 7)] + ([("4_REFLEKTORIUS", 30)] if P.get("reflector") else []) \
        + [("TEXT", 8)]
    for nm_, col in LAY:
        doc.layers.add(nm_, color=col)
    m = doc.modelspace()
    ymax = max([o["bb"][3] for o in letters] + [q[1] for f_ in frame for q in f_])
    Q = lambda q: (round(q[0], 3), round(ymax - q[1], 3))

    def ring(g, layer):
        for pg in _parts(g):
            for rg in [pg.exterior] + list(pg.interiors):
                m.add_lwpolyline([Q(c) for c in rg.coords], close=True, dxfattribs={"layer": layer})
    for f_ in frame:
        m.add_lwpolyline([Q(q) for q in f_], close=True, dxfattribs={"layer": "1_REMAS"})
    for x0, y0, x1, y1, hx, hy, d in ears:
        m.add_lwpolyline([Q(q) for q in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))], close=True, dxfattribs={"layer": "1_REMAS"})
        m.add_circle(Q((hx, hy)), d / 2, dxfattribs={"layer": "1_REMAS"})
    for i, o in enumerate(letters):
        ring(back_shape(o, P, [q for q in sp if q[2] == i])[0], "2_DUGNAS")     # su drenažo Ø8 puslankiais
        for x, y, j in sp:
            if j == i:
                m.add_circle(Q((x, y)), float(P["back_hole"]) / 2, dxfattribs={"layer": "2_DUGNAS"})
        ring(o["geom"], "3_PRIEKIS")
        if P.get("reflector"):
            ring(o["geom"].buffer(P["refl_off"], quad_segs=KR.BUF_QS), "4_REFLEKTORIUS")
            for x, y, j in sp:
                if j == i:
                    m.add_circle(Q((x, y)), float(P["rod_hole"]) / 2, dxfattribs={"layer": "4_REFLEKTORIUS"})
    m.add_text(f"P3{'+reflector' if P.get('reflector') else ''}: {len(sp)} spacers D{float(P['spacer_d']):g} x "
               f"{float(P['spacer']):g} mm (holes D{float(P['back_hole']):g} in back), back transparent plexiglass "
               f"{float(P['back']):g} mm, {float(P['back_inset']):g} mm inside" + (" + PVC edge" if P["pvc_edge"] else "")
               + (f", drainage D{float(P['drain_d']):g} semicircles" if P.get("drain") else "")
               + (f"; reflector {P['refl_mat']} +{float(P['refl_off']):g} mm, holes D{float(P['rod_hole']):g}" if P.get("reflector") else "")
               + "; view FROM FRONT", dxfattribs={"layer": "TEXT", "height": 12}).set_placement((0, -40))
    for lay, _ in LAY[:-1]:                                  # grupės: BLOCK + INSERT (0, 0) + DXF GROUP
        ents = [e for e in m if e.dxf.layer == lay and e.dxftype() != "INSERT"]
        if not ents:
            continue
        bname = lay.split("_", 1)[1]
        blk = doc.blocks.new(name=bname)
        for e in ents:
            blk.add_entity(e.copy())
            m.delete_entity(e)
        doc.groups.new(bname).extend([m.add_blockref(bname, (0, 0), dxfattribs={"layer": lay})])
    KR.saveas(doc, path)
    return path


if __name__ == "__main__":
    # savitikra: A ant dviejų bėgelių - 3 taškai (trikampis), kojelių centruose; L - 2+ taškai
    from shapely.geometry import Polygon
    A = Polygon([(0, 600), (250, 0), (350, 0), (600, 600), (480, 600), (300, 150), (120, 600)])
    o = {"geom": A, "bb": A.bounds}
    rails = [{"x0": -50, "x1": 650, "y0": 120, "y1": 150, "kind": "h"}, {"x0": -50, "x1": 650, "y0": 450, "y1": 480, "kind": "h"}]
    P = cfg({"depth_mm": 60}, 600)
    sp, err = spacers([o], rails + [{"x0": 280, "x1": 310, "y0": 150, "y1": 450, "kind": "v"},     # statmuo / įstrižas -
                                    {"x0": 60, "x1": 200, "y0": 150, "y1": 450, "kind": "d",       #  tvirtinimų ant jų nėra
                                     "poly": [(170, 150), (200, 150), (90, 450), (60, 450)]}], P)
    assert all(130 <= y <= 155 or 445 <= y <= 480 for _, y, _ in sp), sp
    print("A:", sp, err)
    legs = [p for p in sp if p[1] > 400]
    assert len(sp) == 3 and len(legs) == 2, sp
    for x, y, _ in legs:                                    # kojelės ploto centras (ne kraštas)
        comp = [c for c in _parts(A.buffer(-1).intersection(_box(-50, 450, 650, 480))) if c.distance(_Pt(x, y)) < 1][0]
        assert abs(comp.centroid.x - x) < 1.0, (x, comp.centroid.x)
    # v337 standartai: distanceris pagal gylį, galas pagal aukštį, drenažas - puslankis A kojelių apačioje
    assert cfg({"depth_mm": 50})["spacer"] == 20 and cfg({"depth_mm": 60})["spacer"] == 30
    assert cfg({}, 399)["back"] == 8 and not cfg({}, 399)["pvc_edge"] and cfg({}, 400)["back"] == 4 and cfg({}, 400)["pvc_edge"]
    b_, dr_ = back_shape(o, P, sp)
    assert len(dr_) == 2 and all(q[1] > 590 for q in dr_), dr_
    assert b_.area < A.buffer(-0.7).area - 40, "puslankiai neiškirpti"
    assert not cfg({"front": "P3"})["reflector"] and cfg({"front": "P3+reflector"})["reflector"]   # v339
    assert abs(back_shape(o, dict(P, drain=False))[0].area - A.buffer(-0.7).area) < 1          # v341: dugnas 0,7 inside
    import ezdxf, tempfile                                   # v341: DXF - atskiros grupės REMAS / DUGNAS / PRIEKIS
    _f = tempfile.mktemp(suffix=".dxf")
    write_dxf(_f, [o], sp, P, frame=[[(-50, 120), (650, 120), (650, 150), (-50, 150)]], ears=[(0, 150, 30, 190, 15, 175, 6)])
    _d = ezdxf.readfile(_f)
    assert {g_[0] for g_ in _d.groups} == {"REMAS", "DUGNAS", "PRIEKIS"}, [g_[0] for g_ in _d.groups]
    assert len(list(_d.blocks["DUGNAS"].query("CIRCLE"))) == len(sp)
    os.remove(_f)
    import auto_remas as AR                                   # v340 / v342 rėmo taisyklė (bendra visiems rėmams, išskyrus EXTRA)
    assert [AR.n_verticals(x) for x in (2999, 3000, 4999, 5000)] == [2, 3, 3, 4]
    assert AR.even_pick(0, 3000, [500, 1300, 1800, 2900], 1) == [1]               # vidurinis - arčiausiai centro
    assert AR.even_pick(0, 6000, [900, 1500, 2100, 3800, 4100, 5200], 2) == [2, 4]   # 4 statmenys - vienodi tarpai
    print("OK p3_raides savitikra")
