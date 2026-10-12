#!/usr/bin/env python3
"""LED Lens modulių išdėstymas raidėse - APŠVIESTUMO SIMULIACIJA (v31, Rytis 2026-10-08). Aprašas: references/led_sim.md.

  1. Modelis: LED - taškinis šaltinis gylyje d, I(θ) ~ cos^a θ; tiesioginė šviesa tik kur šaltinis „mato" tašką
     (šonai užstoja); šonų 10 mm ruožai - Lamberto atspindys (ρ); tolesni atspindžiai - tolygus fonas.
  2. Ribos: tiekėjo raidžių eilės taisyklės (P130L 50/120, P190L 80/200, P65L 40/100, 30/70) sumodeliuotos kanale ->
     U = P5/vidurkis ir H = P95/vidurkis ašyje kiekvienam moduliui.
  3. Forma: ašis (skeletas be „ūsų") -> šakos / žiedai; galuose modulis, sankirtoje vienas, žiedai simetriški;
     plačios linijos - kelios eilės (LED Wizard Runs / Clearance).
  4. Žingsnis - pagal linijos pločio grupę (didžiausias, kuriuo grupė tenkina U / H); modulis - pagal grupę
     (telpantis, mažiausiai vnt.; vienas tipas, jei <= 10 % daugiau).
  5. Lapas: 1 - CAD išdėstymas, grandinės, įvadai, palyginimas; 2 - apšviestumo žemėlapis ir U / H raidėms.

Naudojimas:  python3 led_sim.py spec.json out.pdf
Spec: pdf, fill_rgb (spalva arba sąrašas), crop_pt, scale_mm_per_pt | ref_width_mm, depth, module (null - parenka),
      letter_names, groups, group_names, main_data, client, title, drawing_no, order_no, date, rev, psu.
Modelio parametrai (keisti tik pagal bandymą su pavyzdine raide): LENS_A, RHO, AMB.
"""
import json
import math
import re
import os
import sys

import numpy as np
import pymupdf as fitz
from scipy import ndimage
from shapely import affinity
from shapely.geometry import Polygon
from shapely.prepared import prep

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "assets", "led_lens.json")

LENS_A = 0.5        # I(θ) ~ cos^a θ; a < 1 - platesnis nei Lambertas (Lens). Patikslinti bandymu.
RHO = 0.8           # šonų atspindys (balti / Alu viduje) - 1-as atspindys skaičiuojamas tiesiogiai (šonų ruožai)
AMB = 0.15          # tolesni atspindžiai: tolygus fonas = AMB * (šonams tekęs srautas) / A_priekio
WS = 10.0           # mm - šono ruožo ilgis
EDGE = 6.0          # mm - pakraščio juosta, neįskaičiuojama į tolygumą
EV = 6.0            # mm - vertinimo tinklelis
CAND = 6.0          # mm - kandidatų tinklelis
CLEAR = 3.0         # mm - modulis nuo šono
TOL_LO, TOL_HI = 0.95, 1.05   # modelio tolerancija ribose: U, A >= 0,95 x riba; H <= 1,05 x riba (v36; U, A buvo 0,995)
GROUP_W = 1.5       # raidės vienoje žingsnio / modulio grupėje, jei linijos plotis skiriasi <= 1,5 karto (v36; buvo 1,3)


def data():
    return json.load(open(DATA, encoding="utf-8"))


# ------------------------------------------------------------------ geometrija
def _bez(p0, p1, p2, p3, t):
    return (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3


def read_letters(pdf, fill_rgb, tol=0.02, crop_pt=None, scale=None, ref_width_mm=None, page=0, min_area_mm2=2000):
    """raidės iš PDF: užpildytos nurodyta spalva; fill_rgb = null - KONTŪRAI (visi uždari keliai, pvz. raidžių
    linijos be užpildo, iš vieno ar kelių kelių; even-odd: vidinės formos - skylės)"""
    pg = fitz.open(pdf)[page]
    fills = None if fill_rgb is None else (fill_rgb if isinstance(fill_rgb[0], (list, tuple)) else [fill_rgb])
    raw = []
    for d in pg.get_drawings():
        f = d.get("fill")
        if fills is not None and (not f or not any(all(abs(a - b) <= tol for a, b in zip(f, fc)) for fc in fills)):
            continue
        r = d["rect"]
        if crop_pt and not (r.x0 >= crop_pt[0] and r.y0 >= crop_pt[1] and r.x1 <= crop_pt[2] and r.y1 <= crop_pt[3]):
            continue
        subs, cur = [], []
        for it in d["items"]:
            if it[0] == "l":
                a, b = it[1], it[2]
                if cur and (abs(cur[-1][0] - a.x) > 1e-3 or abs(cur[-1][1] - a.y) > 1e-3):
                    subs.append(cur); cur = []
                if not cur:
                    cur.append((a.x, a.y))
                cur.append((b.x, b.y))
            elif it[0] == "c":
                a, b, c, e = [np.array([p.x, p.y]) for p in it[1:5]]
                if cur and (abs(cur[-1][0] - a[0]) > 1e-3 or abs(cur[-1][1] - a[1]) > 1e-3):
                    subs.append(cur); cur = []
                if not cur:
                    cur.append(tuple(a))
                for t in np.linspace(0, 1, 13)[1:]:
                    cur.append(tuple(_bez(a, b, c, e, t)))
            elif it[0] == "re":
                q = it[1]; subs.append([(q.x0, q.y0), (q.x1, q.y0), (q.x1, q.y1), (q.x0, q.y1)])
            elif it[0] == "qu":
                q = it[1]; subs.append([(q.ul.x, q.ul.y), (q.ur.x, q.ur.y), (q.lr.x, q.lr.y), (q.ll.x, q.ll.y)])
        if cur:
            subs.append(cur)
        raw.append(subs)
    allp = [p for subs in raw for s_ in subs for p in s_]
    x0 = min(p[0] for p in allp); y0 = min(p[1] for p in allp); x1 = max(p[0] for p in allp)
    S = scale if scale else ref_width_mm / (x1 - x0)
    out = []
    for subs in raw:
        polys = [Polygon([((x - x0) * S, (y - y0) * S) for x, y in s_]).buffer(0) for s_ in subs if len(s_) >= 3]
        polys.sort(key=lambda p: -p.area)
        g = None
        for p in polys:                                   # even-odd: vidinės formos - skylės
            if g is None:
                g = p
            elif g.buffer(-0.01).contains(p):
                g = g.difference(p)
            else:
                g = g.union(p)
        if g is None or g.is_empty:
            continue
        for gg in (list(g.geoms) if hasattr(g, "geoms") else [g]):
            if gg.area >= min_area_mm2:
                out.append(gg)
    out.sort(key=lambda g: g.bounds[0])
    return out, S


def raster(g, res):
    """raidės kaukė res mm tinklelyje; grąžina mask, (x0, y0)"""
    from skimage.draw import polygon as dpoly
    x0, y0, x1, y1 = g.bounds
    W = int(math.ceil((x1 - x0) / res)) + 3; H = int(math.ceil((y1 - y0) / res)) + 3
    m = np.zeros((H, W), bool)
    ox, oy = x0 - res, y0 - res
    for gg in (list(g.geoms) if hasattr(g, "geoms") else [g]):
        xs, ys = np.array(gg.exterior.coords).T
        rr, cc = dpoly((ys - oy) / res, (xs - ox) / res, m.shape); m[rr, cc] = True
        for h in gg.interiors:
            xs, ys = np.array(h.coords).T
            rr, cc = dpoly((ys - oy) / res, (xs - ox) / res, m.shape); m[rr, cc] = False
    return m, (ox, oy)


# ------------------------------------------------------------------ šviesos modelis
def module_leds(mod, x, y, ang):
    """LED kristalų padėtys modulyje (išilgai modulio ašies)"""
    md = data()["modules"][mod]
    k, ml = md["leds"], md["size_mm"][0]
    if k == 1:
        return [(x, y)]
    off = np.linspace(-0.3 * ml, 0.3 * ml, k)
    return [(x + o * math.cos(ang), y + o * math.sin(ang)) for o in off]


def e_point(src, pts, d, phi, a=LENS_A):
    """tiesioginis apšviestumas (lx, kai mm -> m) iš vieno LED kristalo, srautas phi lm"""
    I0 = phi * (a + 1) / (2 * math.pi)                    # cd
    r2 = ((pts[:, 0] - src[0]) ** 2 + (pts[:, 1] - src[1]) ** 2) / 1e6 + (d / 1000.0) ** 2
    R = np.sqrt(r2); c = (d / 1000.0) / R
    return I0 * c ** (a + 1) / r2


def reference(mod, depth, spacing, a=LENS_A):
    """tiekėjo 4x4 tinklelis (atvira dėžė): vidutinis E ir tolygumas centrinėje ląstelėje"""
    md = data()["modules"][mod]
    phi = md["lm"] / md["leds"]
    xs = (np.arange(4) - 1.5) * spacing
    src = [p for x in xs for y in xs for p in module_leds(mod, x, y, 0.0)]
    g = np.linspace(-spacing / 2, spacing / 2, 25)
    P = np.array([(x, y) for x in g for y in g])
    E = sum(e_point(s, P, depth, phi, a) for s in src)
    return float(E.mean()), float(E.min() / E.mean())


def supplier_spacing(mod, depth, plexi="45"):
    """tiekėjo žingsnis tame gylyje (lentelė; tarp stulpelių - žemesnis; Ryčio taisyklės raidėms)"""
    D = data()
    for r in D["special"].get(mod, []):
        if r["use"] in ("any", "letter") and depth >= r["depth_min"] and (r["depth_max"] is None or depth <= r["depth_max"]):
            sp = r["spacing_mm"]
            return sp[plexi] if isinstance(sp, dict) else sp, r["note"]
    cols = sorted(int(c) for c in D["lux_table"][mod])
    ok = [c for c in cols if c <= depth]
    if not ok:
        return None, None
    return D["lux_table"][mod][str(ok[-1])][plexi][0], f"lentelė {ok[-1]} mm"


def visible(mask, res, org, src, pts_idx_rc):
    """ar šaltinis mato kiekvieną tašką (2D: atkarpa visa raidės viduje) - tikrinama 24 taškais"""
    sr = ((src[1] - org[1]) / res, (src[0] - org[0]) / res)
    t = np.linspace(0, 1, 24)[:, None]
    rr = sr[0] + (pts_idx_rc[:, 0][None, :] - sr[0]) * t
    cc = sr[1] + (pts_idx_rc[:, 1][None, :] - sr[1]) * t
    ri = np.clip(np.round(rr).astype(int), 0, mask.shape[0] - 1)
    ci = np.clip(np.round(cc).astype(int), 0, mask.shape[1] - 1)
    return mask[ri, ci].all(axis=0)


def contrib_matrix(g, mod, depth, positions):
    """kiekvieno modulio [(x, y, ang)] įnašas į raidės plokštumos taškus: tiesioginis (su šonų užstojimu) +
    1-as atspindys nuo šonų (Lamberto, 10 mm ruožai) + tolesnių atspindžių fonas.
    Grąžina dict: P (taškai), A (moduliai x taškai), m, org, rows, cols, dtm"""
    md = data()["modules"][mod]; phi = md["lm"] / md["leds"]
    m, org, dtm, rows, cols, P, A_face, pidx, Wl, widx, Kwe = _wall_kernel(g, depth)
    zw = depth / 2.0
    I0 = phi * (LENS_A + 1) / (2 * math.pi)
    A = np.zeros((len(positions), len(P)), np.float32)
    for n_, (x, y, ang) in enumerate(positions):
        vis = visible(m, EV, org, (x, y), pidx); visw = visible(m, EV, org, (x, y), widx)
        e = np.zeros(len(P)); Ew = np.zeros(len(Wl))
        for sx, sy in module_leds(mod, x, y, ang):
            e += e_point((sx, sy), P, depth, phi)
            vx, vy, vz = (Wl[:, 0] - sx) / 1000, (Wl[:, 1] - sy) / 1000, zw / 1000
            r2 = vx ** 2 + vy ** 2 + vz ** 2; r = np.sqrt(r2)
            Ew += I0 * (vz / r) ** LENS_A * np.clip(-(vx * Wl[:, 2] + vy * Wl[:, 3]) / r, 0, None) / r2
        e *= vis; Ew *= visw
        A[n_] = e + RHO * (Ew @ Kwe) + AMB * float((Ew * Wl[:, 4]).sum()) / A_face
    return {"P": P, "A": A, "m": m, "org": org, "rows": rows, "cols": cols, "dtm": dtm}


_KW = {}


def _wall_kernel(g, depth):
    """raidės tinklelis ir šonų -> priekio branduolys (nepriklauso nuo modulių - kaupiamas)"""
    key = (g.wkb, depth)
    if key in _KW:
        return _KW[key]
    m, org = raster(g, EV)
    dtm = ndimage.distance_transform_edt(m) * EV
    rows, cols = np.nonzero(m)
    P = np.column_stack([org[0] + cols * EV, org[1] + rows * EV])
    A_face = m.sum() * (EV / 1000) ** 2
    pidx = np.column_stack([rows, cols]).astype(float)
    Wl = wall_samples(g, depth); zw = depth / 2.0
    widx = np.column_stack([(Wl[:, 1] - org[1]) / EV, (Wl[:, 0] - org[0]) / EV])
    Kwe = np.zeros((len(Wl), len(P)), np.float32)
    for k, (wx, wy, nx, ny, aw) in enumerate(Wl):
        ux, uy, uz = (P[:, 0] - wx) / 1000, (P[:, 1] - wy) / 1000, (depth - zw) / 1000
        r2 = ux ** 2 + uy ** 2 + uz ** 2; r = np.sqrt(r2)
        Kwe[k] = (np.clip((ux * nx + uy * ny) / r, 0, None) * uz / r * aw / (math.pi * r2)) * visible(m, EV, org, (wx, wy), pidx)
    _KW.clear() if len(_KW) > 40 else None
    _KW[key] = (m, org, dtm, rows, cols, P, A_face, pidx, Wl, widx, Kwe)
    return _KW[key]


_SW = {}
_DT2 = {}


def _dt2(g):
    """atstumas iki šono (mm), 2 mm tinklelis - kaupiamas"""
    k = g.wkb
    if k not in _DT2:
        m, org = raster(g, 2.0)
        _DT2[k] = (ndimage.distance_transform_edt(m) * 2.0, org)
    return _DT2[k]


def _stroke_w(g):
    k = g.wkb
    if k not in _SW:
        _SW[k] = stroke_max(g)
    return _SW[k]


def area_u(cm, E, g=None):
    """tolygumas priekyje (be EDGE juostos prie šono): 5 % procentilis / vidurkis.
    Su g - be UŽRAITŲ (serifų) ir smailių: plonesnės nei 0,6 x linijos pločio vietos pašalinamos morfologiniu
    atvėrimu (r = 0,3 x plotis) - ten modulių nededama (Rytis: į smailes nededama), gamyboje jos kiek tamsesnės."""
    sel = cm["dtm"][cm["rows"], cm["cols"]] >= EDGE
    if g is not None:
        r_ = 0.3 * _stroke_w(g) / EV
        if r_ >= 1:
            n_ = int(math.ceil(r_))
            yy, xx = np.mgrid[-n_:n_ + 1, -n_:n_ + 1]
            op = ndimage.binary_opening(cm["m"], structure=(xx ** 2 + yy ** 2) <= r_ ** 2)
            sel2 = sel & op[cm["rows"], cm["cols"]]
            if sel2.sum() >= 0.5 * sel.sum():
                sel = sel2
    Es = E[sel] if sel.any() else E
    return float(np.percentile(Es, 5) / Es.mean()) if len(Es) and Es.mean() > 0 else 0.0


def row_ref(mod, depth, s, wf=1.25, n=7):
    """priimtinas ploto tolygumas: VIENA eilė tiekėjo žingsniu s tame gylyje, linijos plotis = 1,25 x s
    (LED Wizard / SloanLED: didžiausias plotis vienai eilei). Raidė turi būti ne prastesnė už šią ribinę eilę -
    modelio paklaidos (šonai, lęšis) abiem atvejais vienodos"""
    w = wf * s; Lr = n * s
    g = Polygon([(0, 0), (Lr, 0), (Lr, w), (0, w)])
    pos = [((i + 0.5) * s, w / 2, 0.0) for i in range(n)]
    cm = contrib_matrix(g, mod, depth, pos)
    return area_u(cm, cm["A"].sum(axis=0))


def line_mask(cm):
    from skimage.morphology import skeletonize
    dtm, m, rows, cols = cm["dtm"], cm["m"], cm["rows"], cm["cols"]
    ridge_m = ndimage.maximum_filter(dtm, size=max(3, int(60 / EV)))
    return (skeletonize(m) & (dtm >= 0.5 * ridge_m))[rows, cols]


def field(g, mod, depth, positions):
    cm = contrib_matrix(g, mod, depth, positions)
    return cm["P"], cm["A"].sum(axis=0), line_mask(cm)


def ripple(E, line):
    """bangavimas ašyje: 5 % procentilis / vidurkis (5 % - patys linijos galiukai neįskaitomi)"""
    Ec = E[line]
    return float(np.percentile(Ec, 5) / Ec.mean()) if len(Ec) and Ec.mean() > 0 else 0.0


def hot(E, line):
    """šviesios dėmės ašyje: 95 % procentilis / vidurkis"""
    Ec = E[line]
    return float(np.percentile(Ec, 95) / Ec.mean()) if len(Ec) and Ec.mean() > 0 else 9.0


def line_ripple(mod, depth, pitch, width=150.0, n=9):
    """TIESI eilė kanale (plotis width): bangavimas ašyje (5 % procentilis / vid) vidurinėje dalyje"""
    Lr = n * pitch
    g = Polygon([(0, 0), (Lr, 0), (Lr, width), (0, width)])
    pos = [((i + 0.5) * pitch, width / 2, 0.0) for i in range(n)]
    P, E, line = field(g, mod, depth, pos)
    sel = line & (P[:, 0] > 3 * pitch) & (P[:, 0] < Lr - 3 * pitch)
    return ripple(E, sel), float(E[sel].mean()), hot(E, sel)


# TIEKĖJO taisyklės RAIDĖMS (viena eilė) - priimtino bangavimo atskaita (Ryčio / tiekėjo gidas 2026-10-08)
LETTER_RULES = [("P130L", 50, 120), ("P190L", 80, 200), ("P65L", 40, 100), ("P65L", 30, 70)]


def ripple_threshold(width=150.0):
    v = [line_ripple(m_, d_, p_, width)[0] for m_, d_, p_ in LETTER_RULES]
    return float(np.mean(v)), v


# ------------------------------------------------------------------ vienos raidės išdėstymas
def mirror_axes(g):
    """raidės simetrijos ašys (vertikali / horizontali), jei veidrodinis atvaizdas sutampa >= 97 %"""
    x0, y0, x1, y1 = g.bounds
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    ax = []
    for sx, sy, nm in ((-1, 1, "v"), (1, -1, "h")):
        m = affinity.scale(g, xfact=sx, yfact=sy, origin=(cx, cy))
        if g.intersection(m).area / g.area >= 0.97:
            ax.append(nm)
    return ax, (cx, cy)


def wall_samples(g, depth):
    """šonų ruožai: vidurio taškas (x, y), vidinė normalė (nx, ny), plotas m²"""
    out = []
    for ring in [g.exterior] + list(g.interiors):
        Ls = ring.length
        n = max(int(Ls / WS), 3)
        for k in range(n):
            p = ring.interpolate((k + 0.5) * Ls / n)
            q = ring.interpolate((k + 0.5) * Ls / n + 0.5)
            tx, ty = q.x - p.x, q.y - p.y; tl = math.hypot(tx, ty) or 1
            nx, ny = -ty / tl, tx / tl
            if not g.contains(Polygon([(p.x + nx * 1.5, p.y + ny * 1.5), (p.x + nx * 1.6, p.y + ny * 1.5),
                                        (p.x + nx * 1.5, p.y + ny * 1.6)])):
                nx, ny = -nx, -ny
            out.append((p.x + nx * 0.8, p.y + ny * 0.8, nx, ny, (Ls / n) * depth / 1e6))
    return np.array(out)


def skeleton_dirs(m, res, org):
    """linijos krypties laukas: kiekvienam taškui - artimiausio skeleto taško liestinė"""
    from skimage.morphology import skeletonize
    sk = skeletonize(m)
    sr, sc = np.nonzero(sk)
    if len(sr) < 3:
        return lambda x, y: 0.0
    pts = np.column_stack([org[0] + sc * res, org[1] + sr * res])
    from scipy.spatial import cKDTree
    kd = cKDTree(pts)
    ang = np.zeros(len(pts))
    for i, nb in enumerate(kd.query_ball_point(pts, 15.0)):
        Q = pts[nb] - pts[nb].mean(axis=0)
        if len(nb) >= 3:
            w_, v_ = np.linalg.eigh(Q.T @ Q)
            d_ = v_[:, -1]; ang[i] = math.atan2(d_[1], d_[0])
    return lambda x, y: float(ang[kd.query((x, y))[1]])


def skeleton_paths(g):
    """raidės ašis -> šakos (taškų sekos mm) tarp galų / sankirtų; uždaros - žiedai.
    Valymas: kampų „ūsai" (atšaka, kuri išeina už sankirtos įbrėžto apskritimo < 0.6 r) ir galų „uodegos" į galo kampus."""
    import networkx as nx
    from skimage.morphology import skeletonize
    m, org = raster(g, 2.0)
    dt = ndimage.distance_transform_edt(m) * 2.0
    sk = skeletonize(m)
    w_let = float(np.percentile(2 * dt[sk], 90)) if sk.any() else 0.0     # linijos plotis (kaip stroke_max)
    G = nx.Graph()
    ys, xs = np.nonzero(sk); S = set(zip(ys.tolist(), xs.tolist()))
    for (y, x) in S:
        G.add_node((y, x))
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if (dy or dx) and (y + dy, x + dx) in S:
                    G.add_edge((y, x), (y + dy, x + dx), w=math.hypot(dy, dx) * 2.0)
    for (a, b) in list(G.edges()):                      # įstrižos briaunos 4-kaimynų trikampiuose
        if abs(a[0] - b[0]) == 1 and abs(a[1] - b[1]) == 1 and (G.has_node((a[0], b[1])) or G.has_node((b[0], a[1]))):
            G.remove_edge(a, b)

    def walk(e):
        path, prev, cur = [e], None, e
        while True:
            nb = [n for n in G.neighbors(cur) if n != prev]
            if len(nb) != 1:
                break
            prev, cur = cur, nb[0]; path.append(cur)
            if G.degree(cur) != 2:
                break
        return path
    for _ in range(8):                                  # kampų „ūsai"
        ch = False
        for e in [n for n in G.nodes if G.degree(n) == 1]:
            if e not in G or G.degree(e) != 1:
                continue
            path = walk(e); j = path[-1]
            if G.degree(j) < 3:
                continue
            dj = dt[j]
            ext = max(math.hypot((p[0] - j[0]) * 2, (p[1] - j[1]) * 2) + dt[p] for p in path) - dj
            plen = sum(math.hypot((a_[0] - b_[0]) * 2, (a_[1] - b_[1]) * 2) for a_, b_ in zip(path[:-1], path[1:]))
            # kampų „ūsai"; UŽRAITAI (serifai): trumpa (< linijos plotis) ir plona (< 0,6 x linijos plotis) atšaka
            wbr = float(np.median([2 * dt[q] for q in path]))
            if ext < 0.6 * dj or (plen < w_let and wbr < 0.6 * w_let):
                G.remove_nodes_from(path[:-1]); ch = True
        if not ch:
            break
    for e in [n for n in G.nodes if G.degree(n) == 1]:  # galų „uodegos" (iki ~0.75 linijos pločio)
        if e not in G or G.degree(e) != 1:
            continue
        path = walk(e)
        ref = float(np.median([dt[q] for q in path[len(path) // 3:]])) if len(path) > 15 else float(max(dt[q] for q in path))
        cut = 0
        while cut < len(path) - 2 and dt[path[cut]] < 0.85 * ref and cut * 2.0 < 1.5 * ref:
            cut += 1
        G.remove_nodes_from(path[:cut])
    keys = {n for n in G.nodes if G.degree(n) != 2}
    out, seen = [], set()
    for a in keys:
        for b in G.neighbors(a):
            if (a, b) in seen:
                continue
            path, prev, cur = [a], a, b; seen.add((a, b))
            while cur not in keys:
                path.append(cur)
                nxt = [n for n in G.neighbors(cur) if n != prev]
                if not nxt:
                    break
                prev, cur = cur, nxt[0]
            path.append(cur); seen.add((cur, path[-2]))
            out.append(("open", path))
    comps = [c for c in nx.connected_components(G) if not (c & keys)]
    for c in comps:                                     # žiedai (O, D, 0)
        cyc = nx.cycle_basis(G.subgraph(c))
        if cyc:
            out.append(("loop", cyc[0] + [cyc[0][0]]))
    res = []
    for kind, path in out:
        P = np.array([(org[0] + x * 2.0, org[1] + y * 2.0) for y, x in path], float)
        seg = np.hypot(*np.diff(P, axis=0).T)
        if seg.sum() < 4:
            continue
        ends = [("free" if G.degree(path[0]) == 1 else "j"), ("free" if G.degree(path[-1]) == 1 else "j")] if kind == "open" else ["loop", "loop"]
        wend = [0.0, 0.0]
        Pe = P                                                  # vertinimo ašis - be pratęsimų iki krašto
        if kind == "open":
            if ends[1] == "free":
                P, ends[1], wend[1] = _extend_end(P, m, org, dt)
            if ends[0] == "free":
                P, ends[0], wend[0] = _extend_end(P[::-1], m, org, dt)
                P = P[::-1]
            seg = np.hypot(*np.diff(P, axis=0).T)
        res.append({"kind": kind, "P": P, "cum": np.concatenate([[0], np.cumsum(seg)]), "ends": ends, "wend": wend, "Pe": Pe})
    return res


def _extend_end(P, m, org, dt, res=2.0):
    """laisvas linijos galas. Skeletas baigiasi ~ pusė pločio nuo galo krašto.
    - STAČIAS galas (plotis iki krašto nesiaurėja): ašis pratęsiama IKI galo krašto -> grąžina "edge";
      modulis dedamas per pusę žingsnio nuo krašto („ląstelė" - kaip gamybos brėžiniuose, apskritimas liečia galą).
    - SMAILĖ (plotis siaurėja < 60 % galo pločio): nekeičiama -> "free" (modulis ašies gale, į smailę nededamas)."""
    def inside(q):
        r_, c_ = int(round((q[1] - org[1]) / res)), int(round((q[0] - org[0]) / res))
        return 0 <= r_ < m.shape[0] and 0 <= c_ < m.shape[1] and bool(m[r_, c_])

    def ray(q, d, lim=3000.0):
        t = 0.0
        while t < lim and inside(q + d * (t + res)):
            t += res
        return t
    end = P[-1]
    k = len(P) - 1
    while k > 0 and math.hypot(*(P[k] - end)) < 30:
        k -= 1
    v = end - P[k]; nv = math.hypot(*v)
    if nv < 1e-6:
        return P, "free", 0.0
    v = v / nv; nrm = np.array([-v[1], v[0]])
    w_end = ray(end, nrm) + ray(end, -nrm)
    L_ = ray(end, v)
    if L_ <= res or w_end <= 0:
        return P, "edge", w_end
    add = []
    t = res
    while t <= L_:
        q = end + v * t
        if t < L_ - 0.25 * w_end and ray(q, nrm) + ray(q, -nrm) < 0.6 * w_end:
            return P, "free", w_end                            # smailė
        add.append(q); t += res
    return (np.vstack([P, np.array(add)]) if add else P), "edge", w_end


def _at(path, u):
    P, cum = path["P"], path["cum"]
    u = min(max(u, 0), cum[-1])
    j = min(int(np.searchsorted(cum, u)), len(P) - 1)
    a, b = P[max(j - 5, 0)], P[min(j + 5, len(P) - 1)]
    return float(P[j][0]), float(P[j][1]), math.atan2(b[1] - a[1], b[0] - a[0])


def structured(paths, pitch, bounds):
    """lygiu žingsniu (<= p) kiekvienoje šakoje (gamybos brėžinių „ląstelės" - modulio apskritimas = žingsnis):
    - STATUS linijos galas - modulis per pusę žingsnio nuo krašto (apskritimas liečia galą; kai žingsnis > plotis -
      (p/2 + w/2) / 2); smailė - modulis ašies gale;
    - SANKIRTA - vienas modulis pačioje sankirtoje (pagal tiesiausią šakų porą), šakų pirmas modulis - per PILNĄ žingsnį
      nuo jos (aplink sankirtą tas pats žingsnis; be dėmės);
    - žiedas (O, D, 0) - lyginis n, fazė simetrijai viršus / apačia, kairė / dešinė."""
    pos, junc = [], []
    for pa in paths:
        L = pa["cum"][-1]
        if pa["kind"] == "loop":
            n = max(2, math.ceil(L / pitch - 0.05)); n += n % 2
            x0, y0, x1, y1 = bounds; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            best = None
            for ph in np.linspace(0, L / n, 24, endpoint=False):
                A_ = np.array([_at(pa, (ph + i * L / n) % L)[:2] for i in range(n)])
                err = 0.0
                for mx, my, w_ in ((1, -1, 1.0), (-1, 1, 0.5)):
                    M_ = np.column_stack([cx + mx * (A_[:, 0] - cx), cy + my * (A_[:, 1] - cy)])
                    err += w_ * float(np.min(np.hypot(M_[:, None, 0] - A_[None, :, 0], M_[:, None, 1] - A_[None, :, 1]), axis=1).sum())
                if best is None or err < best[0]:
                    best = (err, ph)
            pos += [_at(pa, (best[1] + i * L / n) % L) for i in range(n)]
            continue
        e0, e1 = pa["ends"]
        for e_, et in ((0, e0), (1, e1)):                     # sankirtų taškai ir šakų kryptys
            if et == "j":
                P = pa["P"] if e_ == 0 else pa["P"][::-1]
                k = min(len(P) - 1, 25)                         # kryptis ~50 mm baze (sankirtos lenkimas neiškreipia)
                junc.append((P[0][0], P[0][1], math.atan2(P[k][1] - P[0][1], P[k][0] - P[0][0]), L))
        # inkarai: status galas - per pusę žingsnio nuo krašto (gamybos „ląstelė"); kai žingsnis didesnis už linijos plotį -
        # vidurkis tarp p/2 ir w/2 (šonų atspindys ne veidrodis - galas kitaip lieka tamsus); smailė - ašies galas;
        # sankirta - sankirtos modulis (atskirai)
        wend = pa.get("wend", [0.0, 0.0])

        def off(et, w_):
            if et != "edge":
                return 0.0
            return pitch / 2 if pitch <= w_ or w_ <= 0 else (pitch / 2 + w_ / 2) / 2
        a_, b_ = off(e0, wend[0]), L - off(e1, wend[1])
        if e0 != "j" and e1 != "j" and b_ - a_ < 0.3 * pitch:
            pos.append(_at(pa, L / 2)); continue
        k_ = max(1, math.ceil((b_ - a_) / pitch - 0.05))
        us = [a_ + i * (b_ - a_) / k_ for i in range(k_ + 1)]
        if e0 == "j":
            us = us[1:]
        if e1 == "j":
            us = us[:-1]
        pos += [_at(pa, u) for u in us]
    # sankirtų moduliai (artimi taškai - viena sankirta)
    jpos = []
    used = [False] * len(junc)
    for a in range(len(junc)):
        if used[a]:
            continue
        grp = [b for b in range(len(junc)) if not used[b] and math.hypot(junc[a][0] - junc[b][0], junc[a][1] - junc[b][1]) < 12]
        for b in grp:
            used[b] = True
        x = float(np.mean([junc[b][0] for b in grp])); y = float(np.mean([junc[b][1] for b in grp]))
        dirs = [junc[b][2] for b in grp if junc[b][3] >= 25] or [junc[b][2] for b in grp]   # be trumpų jungčių tarp sankirtų
        best, ang = -1, dirs[0] if dirs else 0.0
        for u in range(len(dirs)):
            for v in range(u + 1, len(dirs)):
                d_ = abs(math.atan2(math.sin(dirs[u] - dirs[v]), math.cos(dirs[u] - dirs[v])))
                if d_ > best:                                   # tiesiausios poros ašis (abiejų krypčių vidurkis)
                    best = d_
                    ang = math.atan2(math.sin(dirs[u]) + math.sin(dirs[v] + math.pi), math.cos(dirs[u]) + math.cos(dirs[v] + math.pi))
        jpos.append((x, y, ang))
    return jpos + pos


def fit_modules(g, pos, ml, mw, slide=0.0):
    """modulis visas raidėje (>= CLEAR nuo šono). Netelpantis (linijos galas, lenkimas) - mažiausias pataisymas:
    pastūmimas išilgai savo ašies (iki `slide` mm), skersai (iki 6 mm) ir pasukimas (iki 20 laipsnių);
    jei vis tiek netelpa - paliekamas vietoje ir pažymimas (fits=False, lape raudonas)"""
    gp = prep(g.buffer(-CLEAR))
    base = Polygon([(-ml / 2, -mw / 2), (ml / 2, -mw / 2), (ml / 2, mw / 2), (-ml / 2, mw / 2)])

    def rect(x, y, a):
        return affinity.translate(affinity.rotate(base, a, use_radians=True, origin=(0, 0)), x, y)
    ts = [0.0] + [s_ * t for t in np.arange(2.0, slide + 1e-6, 2.0) for s_ in (1, -1)]
    tries = sorted(((t, n_, da) for t in ts for n_ in (0.0, 3.0, -3.0, 6.0, -6.0) for da in (0, 10, -10, 20, -20)),
                   key=lambda z: abs(z[0]) + 2 * abs(z[1]) + 0.8 * abs(z[2]))
    out = []
    for (x, y, ang) in pos:
        hit = None
        for t, n_, da in tries:
            c_, s_ = math.cos(ang), math.sin(ang)
            x2, y2, a2 = x + t * c_ - n_ * s_, y + t * s_ + n_ * c_, ang + math.radians(da)
            if gp.contains(rect(x2, y2, a2)):
                hit = (x2, y2, a2)
                break
        out.append({"x": hit[0], "y": hit[1], "ang": hit[2], "fits": True} if hit else
                   {"x": x, "y": y, "ang": ang, "fits": False})
    return out


def dedupe(pos, min_d):
    out = []
    for q in pos:
        if all(math.hypot(q[0] - r[0], q[1] - r[1]) >= min_d for r in out):
            out.append(q)
    return out


# ------------------------------------------------------------------ grandinė ir laidų ilgiai
def path_graph(paths):
    """raidės ašies grafas (šakos + sankirtos), laidams ir grandinės atstumams"""
    import networkx as nx
    G = nx.Graph(); pts = []
    for pa in paths:
        P = pa["P"]
        ids = []
        for q in P:
            ids.append(len(pts)); pts.append((float(q[0]), float(q[1])))
        for a, b in zip(ids[:-1], ids[1:]):
            G.add_edge(a, b, w=math.hypot(pts[a][0] - pts[b][0], pts[a][1] - pts[b][1]))
        if pa["kind"] == "loop":
            G.add_edge(ids[-1], ids[0], w=0.0)
    deg_end = [n for n in G.nodes if G.degree(n) <= 1]
    for a in deg_end:                                    # sankirtos: šakų galai arti vienas kito
        for b in G.nodes:
            if a != b and not G.has_edge(a, b):
                d_ = math.hypot(pts[a][0] - pts[b][0], pts[a][1] - pts[b][1])
                if d_ < 12:
                    G.add_edge(a, b, w=d_)
    return G, np.array(pts) if pts else np.zeros((0, 2))


def chain_letter(mods, g, start, paths=None):
    """grandinė raidėje: atstumai IŠILGAI ašies (laidas eina raidės viduje); artimiausias kaimynas + 2-opt.
    Grąžina (tvarka, laido ilgiai, laido polilinijos)"""
    import networkx as nx
    n = len(mods)
    if n <= 1:
        return mods, [], []
    G, pts = path_graph(paths or [])
    from scipy.spatial import cKDTree
    snap = list(cKDTree(pts).query([(q["x"], q["y"]) for q in mods])[1]) if len(pts) else [None] * n
    D = np.zeros((n, n)); route = {}
    from shapely.geometry import LineString
    gp_ = prep(g.buffer(1.0))
    for i in range(n):
        dist, pth = (nx.single_source_dijkstra(G, snap[i], weight="w") if snap[i] is not None else ({}, {}))
        for j in range(n):
            if i == j:
                continue
            straight = math.hypot(mods[i]["x"] - mods[j]["x"], mods[i]["y"] - mods[j]["y"])
            if gp_.contains(LineString([(mods[i]["x"], mods[i]["y"]), (mods[j]["x"], mods[j]["y"])])):
                D[i, j] = straight                              # laidas tiesiai raidės viduje
                route[(i, j)] = [(mods[i]["x"], mods[i]["y"]), (mods[j]["x"], mods[j]["y"])]
            elif snap[j] in dist:
                D[i, j] = dist[snap[j]]
                route[(i, j)] = [(mods[i]["x"], mods[i]["y"])] + [tuple(pts[k]) for k in pth[snap[j]][::3]] + [(mods[j]["x"], mods[j]["y"])]
            else:
                D[i, j] = 1.4 * math.hypot(mods[i]["x"] - mods[j]["x"], mods[i]["y"] - mods[j]["y"])
                route[(i, j)] = [(mods[i]["x"], mods[i]["y"]), (mods[j]["x"], mods[j]["y"])]
    best = None
    for s0 in range(n):
        seq = [s0]; rest = set(range(n)) - {s0}
        while rest:
            j = min(rest, key=lambda j: D[seq[-1], j]); seq.append(j); rest.remove(j)
        imp = True
        while imp:
            imp = False
            for a in range(1, n - 1):
                for b in range(a + 1, n):
                    q = seq[:a] + seq[a:b + 1][::-1] + seq[b + 1:]
                    if sum(D[q[k], q[k + 1]] for k in range(n - 1)) < sum(D[seq[k], seq[k + 1]] for k in range(n - 1)) - 1e-6:
                        seq = q; imp = True
        cost = sum(D[seq[k], seq[k + 1]] for k in range(n - 1)) + 0.5 * math.hypot(mods[seq[0]]["x"] - start[0], mods[seq[0]]["y"] - start[1])
        if best is None or cost < best[0]:
            best = (cost, seq)
    seq = best[1]
    return [mods[k] for k in seq], [D[seq[k], seq[k + 1]] for k in range(n - 1)], [route[(seq[k], seq[k + 1])] for k in range(n - 1)]


# ------------------------------------------------------------------ visa iškaba
def path_mask(P, paths, tol=EV * 0.75):
    """vertinimo taškai ant IŠVALYTOS ašies (tos pačios, ant kurios dedami moduliai)"""
    from scipy.spatial import cKDTree
    if not paths:
        return np.zeros(len(P), bool)
    Q = np.vstack([pa.get("Pe", pa["P"]) for pa in paths])      # galų pratęsimai iki krašto nevertinami (tikrina A)
    d_, _ = cKDTree(Q).query(P)
    return d_ <= tol


def stroke_max(g):
    """linijos plotis (mm) - LED Wizard „Stroke Width": 2 x atstumas iki šono ANT AŠIES, 90 % procentilis
    (sankirtų „burbulai" - X centras, p sujungimas - neįskaičiuojami)"""
    from skimage.morphology import skeletonize
    m, org = raster(g, 2.0)
    dt = ndimage.distance_transform_edt(m) * 2.0
    v = 2 * dt[skeletonize(m)]
    return float(np.percentile(v, 90)) if len(v) else float(2 * dt.max())


def runs_for(w_max, s_grid):
    """eilių skaičius pagal plačiausią liniją (LED Wizard „Runs"): 1, kol plotis <= 1,25 x tiekėjo tinklelio žingsnis
    (SloanLED: vienos eilės max plotis = žingsnis x 1,25), kitaip ceil(plotis / žingsnis)"""
    return 1 if w_max <= 1.25 * s_grid else int(math.ceil(w_max / s_grid))


def multi_run_paths(g, base_paths, runs, w_max):
    """kelios eilės (LED Wizard): atstumas nuo šono (Clearance) c = plotis / (2 x eilės) - 2 eilės -> 25 %, 3 -> 1/6;
    eilės = vidinės lygiagretės (inlines) atstumu c, 3c, ...; siauros vietos (kur lygiagretė išnyksta) - ašis
    („Auto Join"); nelyginis eilių sk. - ašis plačiausiose vietose"""
    c = w_max / (2.0 * runs)
    out = []
    k = 0
    while (2 * k + 1) * c < w_max / 2 - 1e-6:
        off = g.buffer(-(2 * k + 1) * c, join_style=1)
        for gg in (list(off.geoms) if hasattr(off, "geoms") else [off]):
            if gg.is_empty:
                continue
            for ring in [gg.exterior] + list(gg.interiors):
                n_ = max(int(ring.length / 2.0), 8)                       # sutankinti kas ~2 mm
                P = np.array([(ring.interpolate(t * ring.length / n_).x, ring.interpolate(t * ring.length / n_).y)
                              for t in range(n_ + 1)], float)
                seg = np.hypot(*np.diff(P, axis=0).T)
                if seg.sum() > 20:
                    out.append({"kind": "loop", "P": P, "cum": np.concatenate([[0], np.cumsum(seg)]), "ends": ["loop", "loop"]})
        k += 1
    m, org = raster(g, 2.0)
    dt = ndimage.distance_transform_edt(m) * 2.0
    for pa in base_paths:                                # ašis: siauros vietos (< c) ir nelyginio sk. vidurinė eilė
        r_ = np.clip(np.round((pa["P"][:, 1] - org[1]) / 2.0).astype(int), 0, m.shape[0] - 1)
        c_ = np.clip(np.round((pa["P"][:, 0] - org[0]) / 2.0).astype(int), 0, m.shape[1] - 1)
        d_ = dt[r_, c_]
        keep = (d_ < c) | ((runs % 2 == 1) & (d_ >= (runs - 1) * c))
        idx = np.nonzero(keep)[0]
        if len(idx) < 3:
            continue
        splits = np.split(idx, np.nonzero(np.diff(idx) > 1)[0] + 1)
        for sp_ in splits:
            if len(sp_) < 3:
                continue
            P = pa["P"][sp_]
            seg = np.hypot(*np.diff(P, axis=0).T)
            if seg.sum() < 20:
                continue
            out.append({"kind": "open", "P": P, "cum": np.concatenate([[0], np.cumsum(seg)]), "ends": ["free", "free"]})
    return out


def letter_eval(g, mod, depth, pos, paths=None):
    cm = contrib_matrix(g, mod, depth, [(q[0], q[1], q[2]) for q in pos])
    E = cm["A"].sum(axis=0) if len(pos) else np.zeros(len(cm["P"]))
    line = path_mask(cm["P"], paths) if paths else line_mask(cm)
    mw_ = data()["modules"][mod]["size_mm"][1]              # per plonos vietos (modulis netelpa) - nevertinamos
    thin = 2 * cm["dtm"][cm["rows"], cm["cols"]] < mw_ + 2 * CLEAR
    if (line & ~thin).sum() >= 0.7 * line.sum():
        line = line & ~thin
    return ripple(E, line), float(E[line].mean()) if line.any() else 0.0, cm, E, line, hot(E, line), area_u(cm, E, g)


def solve(spec, verbose=True):
    """LED Wizard principas + simuliacija: eilių sk. (Runs) ir atstumas nuo šono (Clearance) - pagal plačiausią liniją;
    žingsnis (Spacing) - didžiausias <= min(laido ilgis, tiekėjo žingsnis tame gylyje), kuriuo VISOS raidės tenkina
    tiekėjo eilės bangavimą; vienas žingsnis visoms raidėms (LED Wizard „Locked" - vienodas ryškumas)"""
    D = data()
    depth = spec["depth"]
    L, _ = read_letters(spec["pdf"], spec.get("fill_rgb"), crop_pt=spec.get("crop_pt"),
                        scale=spec.get("scale_mm_per_pt"), ref_width_mm=spec.get("ref_width_mm"),
                        min_area_mm2=spec.get("min_area_mm2", 2000), page=spec.get("page", 0))   # v103: "page"
    paths = [skeleton_paths(g) for g in L]
    mods_try = [spec["module"]] if spec.get("module") else list(D["modules"])
    results = {}
    for mod in mods_try:
        sp, why = supplier_spacing(mod, depth)
        if not sp:
            continue
        md = D["modules"][mod]; ml, mw = md["size_mm"][:2]; wire = md["spacing_max_mm"]
        rules = [r for r in LETTER_RULES if r[0] == mod]
        ref_ = [line_ripple(*r) for r in rules]
        U_t = float(np.mean([r_[0] for r_ in ref_]))           # tamsios vietos: ne prasčiau nei tiekėjo eilė
        H_t = float(np.mean([r_[2] for r_ in ref_]))           # šviesios dėmės: ne daugiau nei tiekėjo eilė
        UA_t = row_ref(mod, depth, sp)                        # ploto tolygumas: ne prasčiau nei ribinė viena eilė (1,25 x žingsnis)
        cache, rp_cache = {}, {}
        wmax = [stroke_max(g) for g in L]
        runs0 = [runs_for(w_, sp) for w_ in wmax]

        def rpath(i, r_):
            if (i, r_) not in rp_cache:
                rp_cache[(i, r_)] = paths[i] if r_ == 1 else multi_run_paths(L[i], paths[i], r_, wmax[i])
            return rp_cache[(i, r_)]

        # žingsnio grupės: panašaus linijos pločio raidės (skirtumas <= 30 %) - LED Wizard „Locked" raidžių rinkiniui
        # mažos dalys (taškai, brūkšneliai virš raidžių - ė, ū, i taškas): < 25 % raidės ploto medianos -> artimiausios
        # raidės grupei (tas pats modulis ir žingsnis kaip jos raidei)
        amed = float(np.median([g.area for g in L]))
        small = {i for i, g in enumerate(L) if g.area < 0.35 * amed and len(L) > 2}
        order_ = sorted([i for i in range(len(L)) if i not in small], key=lambda i: wmax[i])
        pgroups = []
        for i in order_:
            if pgroups and wmax[i] <= GROUP_W * min(wmax[k] for k in pgroups[-1]):
                pgroups[-1].append(i)
            else:
                pgroups.append([i])
        for i in sorted(small):
            j = min((k for k in range(len(L)) if k not in small), key=lambda k: L[k].distance(L[i]))
            next(g_ for g_ in pgroups if j in g_).append(i)
        lay, st, pitch_of, runs, rpaths = [None] * len(L), [None] * len(L), [None] * len(L), [None] * len(L), [None] * len(L)

        def place(i, p, r_):
            g, pa = L[i], rpath(i, r_)
            pos = dedupe(structured(pa, p, g.bounds), 0.5 * p) if pa else []
            if not pos:
                c_ = g.representative_point(); pos = [(c_.x, c_.y, 0.0)]
            return pos

        def one(i, p, r_):
            key = (i, p, r_)
            if key in cache:
                return cache[key]
            g, pa = L[i], rpath(i, r_)
            fm = fit_modules(g, place(i, p, r_), ml, mw, slide=min(0.3 * p, ml / 2 + 10))
            # per ploni elementai (pvz. „e" skersinis): linija siauresnė už modulį + 2 x CLEAR - modulis nededamas
            dt2, org2 = _dt2(g)
            def wloc(q):
                r2 = int(round((q["y"] - org2[1]) / 2.0)); c2 = int(round((q["x"] - org2[0]) / 2.0))
                return 2 * float(dt2[min(max(r2, 0), dt2.shape[0] - 1), min(max(c2, 0), dt2.shape[1] - 1)])
            # netelpantis modulis pašalinamas (šviečia kaimynai); TIKRAS netilpimas (modulio tipas netinka) - tik ten,
            # kur linija pakankamai plati (>= modulis + 2 x CLEAR + 10 mm), bet modulis vis tiek netelpa (lenkimai)
            real_bad = sum(1 for q in fm if not q["fits"] and wloc(q) >= mw + 2 * CLEAR + 10)
            nfm = len(fm)
            keep = [q for q in fm if q["fits"]]
            if keep:
                fm = keep
            pos = [(q["x"], q["y"], q["ang"]) for q in fm]
            u, Em, _, _, _, h, ua = letter_eval(g, mod, depth, pos, pa)
            r_ = (fm, {"U": u, "H": h, "UA": ua, "E": Em, "n": len(pos), "dens": len(pos) / (g.area / 1e6),
                       "fit": 1.0 - real_bad / max(nfm, 1)})
            cache[key] = r_
            return r_

        def passes(st_):
            return st_["n"] <= 1 or (st_["U"] >= U_t * TOL_LO and st_["H"] <= H_t * TOL_HI and st_["UA"] >= UA_t * TOL_LO)
        lo, hi = int(0.8 * depth), int(min(wire, sp))       # žingsnis <= laido ilgis IR tiekėjo žingsnis tame gylyje (LED Wizard „Spacing")
        ok_ = True
        gres = []
        for grp in pgroups:
            # eilių sk. (Runs) nuo LED Wizard taisyklės iki +2; kiekvienam - didžiausias tinkamas žingsnis; imamas
            # variantas su mažiausiu modulių sk. (modulių sk. žinomas be simuliacijos - blogesni nevertinami)
            best = None                                      # (n, p, extra)
            for extra in range(0, 3):
                for p in range(hi, lo - 1, -10):
                    if extra > 0 and max(wmax[i] for i in grp) < 1.2 * p:
                        continue                             # papildomos eilės - tik kai linija platesnė už ~1,2 x žingsnį (gamybos pavyzdžiai)
                    n_geo = sum(len(place(i, p, runs0[i] + extra)) for i in grp)
                    if best is not None and n_geo >= best[0]:
                        break
                    # „~p" kaip gamybos brėžiniuose: raidė, kuri netenkina tik dėl diskretaus išdėstymo, gali imti p - 10 / p - 20
                    pp_, res_ = [], []
                    for i in grp:
                        r_ = one(i, p, runs0[i] + extra); q_ = p
                        for dq in (10, 20):                  # ~p: iki -20 mm (diskretus išdėstymas, sankirtos)
                            if passes(r_[1]) or p - dq < lo:
                                break
                            r2 = one(i, p - dq, runs0[i] + extra)
                            if passes(r2[1]):
                                r_, q_ = r2, p - dq
                        res_.append(r_); pp_.append(q_)
                    okg = all(passes(r_[1]) for r_ in res_)
                    if verbose:
                        print(f"    {mod} grupė {grp} eilės +{extra} p={p} n={n_geo}: "
                              + " ".join(f"{r_[1]['U']:.2f}/{r_[1]['H']:.2f}/{r_[1]['UA']:.2f}" for r_ in res_) + (" OK" if okg else ""))
                    if okg:
                        best = (sum(r_[1]["n"] for r_ in res_), p, extra, pp_)
                        break
            if best is None:
                best = (0, lo, 0, [lo] * len(grp)); ok_ = False
            _, p, extra, pp_ = best
            for i, q_ in zip(grp, pp_):
                lay[i], st[i] = one(i, q_, runs0[i] + extra); pitch_of[i] = q_
                runs[i] = runs0[i] + extra; rpaths[i] = rpath(i, runs[i])
            gres.append({"pitch": p, "runs_extra": extra, "ok": all(passes(st[i]) for i in grp),
                         "fit": all(st[i]["fit"] >= 1.0 for i in grp), "fitfrac": float(np.mean([st[i]["fit"] for i in grp])),
                         "n": sum(st[i]["n"] for i in grp), "W": sum(st[i]["n"] for i in grp) * md["W"]})
        best = max(pitch_of)
        n = sum(s_["n"] for s_ in st)
        results[mod] = {"pitch_of": pitch_of, "pgroups": pgroups, "runs": runs, "wmax": wmax, "rpaths": rpaths, "pitch": best, "U_t": U_t, "H_t": H_t, "UA_t": UA_t, "supplier_spacing": sp, "why": why, "lay": lay, "stats": st, "n": n,
                        "W": n * md["W"], "ok": ok_, "gres": gres, "fit": all(g_["fit"] for g_ in gres)}
        if verbose:
            print(f"  {mod}: žingsniai {sorted(set(pitch_of))} mm, eilės {sorted(set(runs))}, {n} vnt., {n * md['W']:.1f} W, "
                  f"U >= {U_t:.2f}, H <= {H_t:.2f}, UA >= {UA_t:.2f}: {'OK' if ok_ else 'NETENKINA'}")
    return L, paths, results


def _fewest(cands, n_of, W_of):
    """mažiausiai modulių (montavimas); kai skirtumas <= 5 % - mažesnė galia"""
    nmin = min(n_of(m) for m in cands)
    return min([m for m in cands if n_of(m) <= nmin * 1.05], key=W_of)


def pick(results):
    ok = {k: v for k, v in results.items() if v["ok"] and v.get("fit", True)} or {k: v for k, v in results.items() if v["ok"]} or results
    return _fewest(list(ok), lambda m: ok[m]["n"], lambda m: ok[m]["W"])


def choose(results, spec, nL):
    """modulis kiekvienai raidei. LED Wizard: kiekvienam raidžių rinkiniui (linijos plotis) - savi nustatymai.
    Grupei tinka modulis, kuris TELPA visose jos raidėse (>= CLEAR nuo šono) ir tenkina U / H; iš tinkamų -
    mažiausiai modulių, kai skirtumas <= 5 % - mažesnė galia. Vienas tipas visai iškabai, jei jis tinka visoms
    grupėms ir modulių <= 10 % daugiau nei mišriame variante (paprastesnis užsakymas ir grandinės)."""
    if spec.get("module"):
        return [spec["module"]] * nL
    mods = list(results)
    pg = results[mods[0]]["pgroups"]
    adm = lambda m, k: results[m]["gres"][k]["ok"] and results[m]["gres"][k]["fit"]
    per = []
    for k in range(len(pg)):
        c = [m for m in mods if adm(m, k)] or \
            [max(mods, key=lambda m: (results[m]["gres"][k]["fitfrac"], -results[m]["gres"][k]["n"]))]
        per.append(_fewest(c, lambda m: results[m]["gres"][k]["n"], lambda m: results[m]["gres"][k]["W"]))
    nmix = sum(results[per[k]]["gres"][k]["n"] for k in range(len(pg)))
    singles = [m for m in mods if all(adm(m, k) for k in range(len(pg)))]
    if singles:
        s_ = _fewest(singles, lambda m: results[m]["n"], lambda m: results[m]["W"])
        if results[s_]["n"] <= 1.1 * nmix:
            return [s_] * nL
    mod_of = [None] * nL
    for k, grp in enumerate(pg):
        for i in grp:
            mod_of[i] = per[k]
    return mod_of


def merged(results, mod_of):
    """vienas rezultatas iš kelių modulių (pagal raidę)"""
    D = data()["modules"]
    keys = ("lay", "stats", "rpaths", "pitch_of", "runs", "wmax")
    R = {k: [results[m][k][i] for i, m in enumerate(mod_of)] for k in keys}
    R["mod_of"] = list(mod_of)
    R["pgroups"] = results[mod_of[0]]["pgroups"]
    R["U_t_of"] = [results[m]["U_t"] for m in mod_of]
    R["H_t_of"] = [results[m]["H_t"] for m in mod_of]
    R["UA_t_of"] = [results[m]["UA_t"] for m in mod_of]
    R["used"] = sorted(set(mod_of), key=lambda m: -D[m]["W"])
    R["n_of"] = {m: sum(st["n"] for st, mm in zip(R["stats"], mod_of) if mm == m) for m in R["used"]}
    R["n"] = sum(R["n_of"].values())
    R["W"] = sum(D[m]["W"] * c for m, c in R["n_of"].items())
    R["pitch"] = max(R["pitch_of"])
    return R


def fmt_p(ps):
    """žingsniai lentelei: iki 3 - išvardinti, daugiau - intervalas"""
    v = sorted(set(ps), reverse=True)
    return " / ".join(str(p_) for p_ in v) if len(v) <= 3 else f"{v[-1]}-{v[0]}"


def feed_plan(n, mod, single=True):
    """Ryčio gamyba (2026-10-09): maitinimas paduodamas per VIENĄ tašką nurodytoje vietoje (laido išvestis),
    įtampos kritimą kompensuoja stipresnis maitinimo šaltinis -> visada "1end"; viršijus tiekėjo ribą iš 1 galo -
    "1end+" (lape pastaba). single=False - senas variantas (2 galai / skaidymas)."""
    m = data()["modules"][mod]
    if single:
        return ("1end" if n <= m["chain_1end"] else "1end+"), [(0, n)]
    if n <= m["chain_1end"]:
        return "1end", [(0, n)]
    if n <= m["chain_2ends"][0]:
        return "2ends", [(0, n)]
    k = math.ceil(n / m["chain_1end"]); st = math.ceil(n / k)
    return "split", [(a, min(a + st, n)) for a in range(0, n, st)]


def sheet(spec, L, paths, results, out):
    import lapas_core as K
    from reportlab.lib.colors import HexColor, black, white
    D = data()
    mod_of = choose(results, spec, len(L))
    R = merged(results, mod_of)
    used = R["used"]; mixed = len(used) > 1
    MODL = " + ".join(used)
    MDS = {m: D["modules"][m] for m in used}
    geom = {m: MDS[m]["size_mm"][:2] for m in used}
    wire_of = lambda i: MDS[mod_of[i]]["spacing_max_mm"]
    depth = spec["depth"]
    names = spec.get("letter_names") or [f"L{i + 1}" for i in range(len(L))]
    nm_ = lambda i: names[i] if i < len(names) else f"L{i + 1}"
    if spec.get("groups"):
        groups = spec["groups"]
        gnames = spec.get("group_names") or [f"G{k + 1}" for k in range(len(groups))]
    elif mixed:                                          # skirtingi moduliai - atskiros grandinės / įvadai
        groups = [[i for i in range(len(L)) if mod_of[i] == m] for m in used]
        gnames = [f"{m}" for m in used]
    else:
        groups = [list(range(len(L)))]; gnames = ["G1"]
    # grandinės: raidėse - artimiausias + 2-opt, raidės iš kairės; grupės - atskiri įvadai
    chains, long_links = [], 0
    feeds_at = spec.get("feed_at") or []                 # pvz. ["right-bottom", "left-bottom"] - kiekvienai grupei
    for k, gi in enumerate(groups):
        fa = feeds_at[k] if k < len(feeds_at) else "left-bottom"
        gb = (min(L[i].bounds[0] for i in gi), min(L[i].bounds[1] for i in gi), max(L[i].bounds[2] for i in gi), max(L[i].bounds[3] for i in gi))
        start = (gb[2] + 40 if "right" in fa else gb[0] - 40, gb[1] if "top" in fa else gb[3])
        _m = re.match(r"letter:(\d+)", str(fa))           # v103 (Joker): laidas iš RAIDĖS - "letter:5-top" (indeksas nuo 0)
        if _m and int(_m.group(1)) < len(L):
            _b = L[int(_m.group(1))].bounds
            start = ((_b[0] + _b[2]) / 2, _b[1] - 40 if "bottom" not in fa else _b[3] + 40)
        gi = sorted(gi, key=lambda i: abs((L[i].bounds[0] + L[i].bounds[2]) / 2 - start[0]))   # nuo įvado pusės
        seq = []
        for i in gi:
            mods = [dict(q) for q in R["lay"][i]]
            o, links, routes = chain_letter(mods, L[i], start, R["rpaths"][i])
            long_links += sum(1 for d_ in links if d_ > wire_of(i))
            for t_, q in enumerate(o):
                q["letter"] = i
                q["route_in"] = routes[t_ - 1] if t_ > 0 else None
            seq += o
            if o:
                start = (o[-1]["x"], o[-1]["y"])
        gm = min({mod_of[i] for i in gi}, key=lambda m: MDS[m]["chain_1end"])      # mišri grandinė - griežčiausias modulis
        kind, parts = feed_plan(len(seq), gm, single=not spec.get("split_feeds"))
        chains.append({"name": gnames[k], "seq": seq, "kind": kind, "parts": parts, "limit": MDS[gm]["chain_1end"], "mod": gm})
    GW = max(g.bounds[2] for g in L); GH = max(g.bounds[3] for g in L)
    # mastelis: viena eilė arba grupės eilutėmis (kai didesnis mastelis)
    K.init(out + ".tmp.pdf", spec.get("title", "LED layout"))
    K.set_band(12)
    AW = K.IX1 - K.IX0 - 170; AH = K.VIEW_BOT - K.IY0 - 70 - 120
    SCS = (2, 2.5, 3, 4, 5, 6, 7, 8, 10, 12.5, 15, 20, 25, 30, 40, 50)
    bb = lambda idx: (min(L[i].bounds[0] for i in idx), min(L[i].bounds[1] for i in idx),
                      max(L[i].bounds[2] for i in idx), max(L[i].bounds[3] for i in idx))
    # modulio apskritimas (skersmuo = žingsnis, kaip gamybos brėžiniuose) - lapo išdėstymui skaičiuojamos jų ribos
    CE = []
    for i, g in enumerate(L):
        r_ = R["pitch_of"][i] / 2
        xs_ = [q["x"] for q in R["lay"][i]] or [g.bounds[0]]; ys_ = [q["y"] for q in R["lay"][i]] or [g.bounds[1]]
        CE.append((min(g.bounds[0], min(xs_) - r_), min(g.bounds[1], min(ys_) - r_),
                   max(g.bounds[2], max(xs_) + r_), max(g.bounds[3], max(ys_) + r_)))
    bbc = lambda idx: (min(CE[i][0] for i in idx), min(CE[i][1] for i in idx), max(CE[i][2] for i in idx), max(CE[i][3] for i in idx))

    def fit(rows):
        for sc in SCS:
            k_ = K.MM / sc
            w_ = max(bbc(r)[2] - bbc(r)[0] for r in rows) * k_
            h_ = sum(bbc(r)[3] - bbc(r)[1] for r in rows) * k_ + 90 * (len(rows) - 1)
            if w_ <= AW and h_ <= AH:
                return sc
        return SCS[-1]
    amed_ = float(np.median([g.area for g in L]))           # mažos dalys (taškai, brūkšneliai) - kiekis prie raidės „3+1"
    small_of = {}
    if len(L) > 2:
        reg_ = [i for i, g in enumerate(L) if g.area >= 0.35 * amed_]
        for i, g in enumerate(L):
            if g.area < 0.35 * amed_ and reg_:
                small_of[i] = min(reg_, key=lambda k_: L[k_].distance(g))
    rows = [list(range(len(L)))]
    SC = fit(rows)
    if not spec.get("groups") and len(L) > 1:                # ilgas užrašas - žodžiai eilutėmis, jei mastelis stambesnis
        xs_ = sorted(range(len(L)), key=lambda i: L[i].bounds[0])
        Hm = max(g.bounds[3] - g.bounds[1] for g in L)
        words, cur, xr = [], [xs_[0]], L[xs_[0]].bounds[2]
        for i in xs_[1:]:
            if L[i].bounds[0] - xr > 0.35 * Hm:
                words.append(cur); cur = []
            cur.append(i); xr = max(xr, L[i].bounds[2])
        words.append(cur)
        import itertools
        for k_ in range(2, min(len(words), 4) + 1):           # žodžiai į k eilučių (iš eilės), stambiausias mastelis
            for cuts in itertools.combinations(range(1, len(words)), k_ - 1):
                cand = [sum(words[a_:b_], []) for a_, b_ in zip((0,) + cuts, cuts + (len(words),))]
                sc_ = fit(cand)
                if sc_ < SC:
                    rows, SC = cand, sc_
    if spec.get("groups") and len(groups) > 1 and fit(groups) < SC:    # eilutėmis - tik fizinės grupės
        rows = groups; SC = fit(groups)
    k = K.MM / SC
    tot_h = sum(bbc(r)[3] - bbc(r)[1] for r in rows) * k + 90 * (len(rows) - 1)
    py = K.IY0 + 70 + max(0, (AH - tot_h) / 2)
    TF = {}
    for r in rows:
        b = bbc(r); px = K.IX0 + (K.IX1 - K.IX0 - (b[2] - b[0]) * k) / 2
        for i in r:
            TF[i] = (px, py, b)
        py += (b[3] - b[1]) * k + 90

    def Xi(i, x):
        return TF[i][0] + (x - TF[i][2][0]) * k

    def Yi(i, y):
        return TF[i][1] + (y - TF[i][2][1]) * k
    ybot = max(Yi(i, CE[i][3]) for i in range(len(L))) + 34          # po apskritimais - bendras matmuo
    FACE = HexColor("#FFF4CC"); MODC = HexColor("#2B2B2B"); WIRE = HexColor("#404040")

    def letters_outline(fill=FACE):
        for i, g in enumerate(L):
            K.poly([(Xi(i, x), Yi(i, y)) for x, y in g.exterior.coords], fill=fill, stroke=black, lw=0.35)
            for h_ in g.interiors:
                K.poly([(Xi(i, x), Yi(i, y)) for x, y in h_.coords], fill=white if fill else None, stroke=black, lw=0.35)

    CIRC = {"P190L": HexColor("#3A3A3A"), "P130L": HexColor("#1F5FA8"), "P65L": HexColor("#7A4BA0")}

    def modules_draw():
        for ch in chains:                                   # apskritimai (skersmuo = žingsnis) po moduliais
            for q in ch["seq"]:
                i = q["letter"]
                K.circle(Xi(i, q["x"]), Yi(i, q["y"]), R["pitch_of"][i] / 2 * k, fill=None,
                         stroke=CIRC.get(mod_of[i], black), lw=0.3)
        for ch in chains:
            for q in ch["seq"]:
                c_, s_ = math.cos(q["ang"]), math.sin(q["ang"])
                ml, mw = geom[mod_of[q["letter"]]]
                pts = [(q["x"] + dx * c_ - dy * s_, q["y"] + dx * s_ + dy * c_) for dx, dy in
                       ((-ml / 2, -mw / 2), (ml / 2, -mw / 2), (ml / 2, mw / 2), (-ml / 2, mw / 2))]
                i = q["letter"]
                K.poly([(Xi(i, x), Yi(i, y)) for x, y in pts], fill=MODC if q.get("fits", True) else K.CABLE, stroke=black, lw=0.3)
                for (lx, ly) in module_leds(mod_of[i], q["x"], q["y"], q["ang"]):
                    K.circle(Xi(i, lx), Yi(i, ly), 1.4, fill=white, stroke=None)
    # ---------------- 1 lapas: išdėstymas
    K.frame()
    K.view_title((K.IX0 + K.IX1) / 2, K.IY0 + 26, "FRONT VIEW - LED LAYOUT (FACE REMOVED)", f"1:{SC:g}")
    letters_outline()
    nfeeds = 0
    for ch in chains:
        seq = ch["seq"]; cuts = {a for a, _ in ch["parts"]}
        for t in range(1, len(seq)):
            if t in cuts:
                continue
            a, b = seq[t - 1], seq[t]
            if TF[a["letter"]][1] != TF[b["letter"]][1]:       # kita lapo eilutė (žodžiai eilutėmis) - jungtis nebraižoma
                continue
            if a["letter"] != b["letter"] or not b.get("route_in"):
                K.line(Xi(a["letter"], a["x"]), Yi(a["letter"], a["y"]), Xi(b["letter"], b["x"]), Yi(b["letter"], b["y"]),
                       0.4, WIRE, dash=([3, 2], 0))
            else:
                K.poly([(Xi(b["letter"], x), Yi(b["letter"], y)) for x, y in b["route_in"]], stroke=WIRE, lw=0.4, close=False)
        fps = [seq[a] for a, _ in ch["parts"]] + ([seq[-1]] if ch["kind"] == "2ends" else [])
        for f in fps:
            i = f["letter"]; yb = Yi(i, max(L[j].bounds[3] for j in groups[chains.index(ch)]))
            K.cable_line([(Xi(i, f["x"]), Yi(i, f["y"])), (Xi(i, f["x"]), yb + 8)]); nfeeds += 1
        for a, b in ch["parts"]:
            qa, qb = seq[a], seq[b - 1]
            K.leader(Xi(qa["letter"], qa["x"]), Yi(qa["letter"], qa["y"]), Xi(qa["letter"], qa["x"]) + 20, Yi(qa["letter"], qa["y"]) - 18, str(a + 1))
            K.leader(Xi(qb["letter"], qb["x"]), Yi(qb["letter"], qb["y"]), Xi(qb["letter"], qb["x"]) - 20, Yi(qb["letter"], qb["y"]) - 18, str(b))
    modules_draw()
    for r in rows:
        b = bb(r); i0 = r[0]
        for i in r:
            if i in small_of:
                continue
            g = L[i]
            lab = "+".join(str(len(R['lay'][j])) for j in [i] + [k_ for k_, par in small_of.items() if par == i])
            K.T(Xi(i, (g.bounds[0] + g.bounds[2]) / 2), Yi(i0, bbc(r)[1]) - 7, lab, 10, font="FB", align="c")
        K.hchain(Yi(i0, bbc(r)[3]) + 24, [Xi(i0, b[0]), Xi(i0, b[2])], [Yi(i0, b[3]), Yi(i0, b[3])], [f"{b[2] - b[0]:.0f}"], size=K.F_DIM_MAIN)
        K.vchain(Xi(i0, bbc(r)[2]) + 16, [Yi(i0, b[1]), Yi(i0, b[3])], [Xi(i0, b[2]) + 4, Xi(i0, b[2]) + 4], [f"{b[3] - b[1]:.0f}"], size=8)
    kinds = {"1end": "fed at one point", "1end+": "fed at one point", "2ends": "fed from both ends", "split": "split into chains"}
    uniq = lambda idx: ", ".join(dict.fromkeys(nm_(i) for i in idx))
    pgs = [g_ for g_ in R["pgroups"]]
    if mixed:
        l1 = "LED by stroke width (12V, on stroke centre line): " + "; ".join(
            f"{m} {MDS[m]['W']} W - {uniq([i for i in range(len(L)) if mod_of[i] == m])}, pitch <= "
            + " / ".join(str(p_) for p_ in sorted({R['pitch_of'][i] for i in range(len(L)) if mod_of[i] == m}, reverse=True)) + " mm"
            for m in used) + ". Numbers - modules per letter."
    else:
        ptxt = ", ".join(f"{'+'.join(nm_(i) for i in grp)}: <= {max(R['pitch_of'][i] for i in grp)} mm" for grp in pgs) \
            if len(set(R["pitch_of"])) > 1 else f"<= {R['pitch']} mm"
        l1 = f"LED {used[0]} ({MDS[used[0]]['name']}), {MDS[used[0]]['W']} W, 12V - on stroke centre line, pitch {ptxt}; numbers - modules per letter."
    lim = "; ".join(f"{m}: P5/mean >= {results[m]['U_t']:.2f}, P95/mean <= {results[m]['H_t']:.2f}" for m in used)
    lima = "; ".join(f"{m} >= {results[m]['UA_t']:.2f}" for m in used)
    fitn = []
    for grp in pgs:                                       # kodėl ne didesnis modulis - netelpa
        m = mod_of[grp[0]]; k_ = pgs.index(grp)
        nf = [m2 for m2 in results if m2 != m and not results[m2]["gres"][k_]["fit"] and D["modules"][m2]["W"] > MDS[m]["W"]]
        if nf:
            fitn.append(f"{uniq(grp)} (stroke ~{np.median([R['wmax'][i] for i in grp]):.0f} mm): {', '.join(nf)} do not fit "
                        f"(module + 2 x {CLEAR:.0f} mm clearance) -> {m}")
    notes = [l1,
             f"Layout by illuminance simulation (sheet 2): ripple on centre line not worse than supplier's letter row ({lim}); "
             f"whole face P5/mean not worse than one row at supplier pitch in a stroke 1.25 x pitch wide ({lima}).",
             "Circle = pitch (centre to centre). Square stroke end - module half a pitch from the end; pointed end - none in the tip; "
             "junction - one module, branches one pitch away. "
             + (f"Rows: {max(R['runs'])} in widest strokes (clearance = stroke / (2 x rows))." if max(R['runs']) > 1 else
                f"One row in all strokes (widest {max(R['wmax']):.0f} mm <= 1.25 x supplier grid pitch).")]
    if fitn:
        notes.append("; ".join(fitn) + ".")
    over = [c for c in chains if c["kind"] == "1end+"]
    notes += ["; ".join(f"{c['name']}: {len(c['seq'])} pcs. - {kinds[c['kind']]}" for c in chains) + ". Red - 12V feed. Dashed - jumper between letters."
              + (" " + "; ".join(f"{c['name']} > {c['limit']} pcs. ({c['mod']} supplier limit from one end)" for c in over)
                 + " - one feed point, voltage drop compensated by a stronger PSU." if over else ""),
              (f"! {long_links} links longer than module wire ({' / '.join(str(MDS[m]['spacing_max_mm']) for m in used)} mm) - extension wire needed."
               if long_links else f"All module-to-module links <= module wire ({' / '.join(str(MDS[m]['spacing_max_mm']) for m in used)} mm)."),
              "Model to be confirmed with a sample letter (lens profile, interior reflectance)."]
    ny = ybot + 40
    for i, t in enumerate(notes):
        K.T(K.IX0 + 14, ny + i * 11, f"{i + 1}. {t}", 8, fit=K.IX1 - K.IX0 - 30, fit_min=8)
    BY0, BH = K.BAND_Y, K.IY1 - K.BAND_Y
    W_TB, W_MD = 272, 236
    X_TB = K.IX1 - W_TB; X_MD = X_TB - W_MD; X_T = K.IX0; W_T = X_MD - X_T
    K.header(X_T, BY0, W_T, f"LED SELECTION - SIMULATED, DEPTH {depth} mm")
    cols = [("MODULE", 0.27), ("PITCH", 0.12), ("QTY", 0.12), ("POWER", 0.12), ("SUPPLIER BOX PITCH", 0.19), ("CHECK", 0.18)]
    yy, xx = BY0 + 12, X_T
    for n_, f_ in cols:
        K.rect(xx, yy, W_T * f_, 12, fill=HexColor("#F6F6F6"), lw=0.4); K.T(xx + 3, yy + 8.6, n_, 8, font="FB"); xx += W_T * f_
    yy += 12
    trows = []
    for m_, r in results.items():
        trows.append((not mixed and m_ == used[0],
                      [f"{m_} {D['modules'][m_]['name']} {D['modules'][m_]['W']} W" + ("  << SELECTED" if (not mixed and m_ == used[0]) else ""),
                       fmt_p(r["pitch_of"]) + " mm", f"{r['n']} pcs.", f"{r['W']:.1f} W",
                       f"{r['supplier_spacing']} mm",
                       "DOES NOT FIT" if not r.get("fit", True) else ("OK" if r["ok"] else "NOT MET")]))
    if mixed:
        trows.append((True, [f"{MODL} by stroke width  << SELECTED",
                             fmt_p(R["pitch_of"]) + " mm", f"{R['n']} pcs.", f"{R['W']:.1f} W",
                             " / ".join(f"{results[m]['supplier_spacing']}" for m in used) + " mm", "OK"]))
    for sel, row in trows:
        xx = X_T
        for (n_, f_), v in zip(cols, row):
            K.rect(xx, yy, W_T * f_, 16, fill=HexColor("#FFF4CC") if sel else None, lw=0.3)
            K.T(xx + 3, yy + 11, v, 8, font="FB" if sel else "F", fit=W_T * f_ - 5, fit_min=8); xx += W_T * f_
        yy += 16
    for i, t in enumerate(["Pitch chosen by simulation: largest pitch (<= module wire, <= supplier pitch) meeting the ripple limits.",
                           "Same pitch for letters of similar stroke width (+/- 30 %); module per group - fewest that fit (one type if <= 10 % more)."]):
        K.T(X_T + 4, yy + 12 + i * 11, t, 8, color=K.GREY)
    K.rect(X_T, BY0 + 12, W_T, BH - 12, lw=0.6)
    md_rows = list(map(tuple, spec.get("main_data", []))) + [
        ("Depth", f"{depth} mm"), ("Size", f"{GW:.0f} x {GH:.0f} mm"), ("LED", (f"{MODL}, 12V" if mixed else f"{used[0]} {MDS[used[0]]['name']}, 12V, {MDS[used[0]]['W']} W")),
        ("LED qty", (" + ".join(str(R["n_of"][m]) for m in used) + f" = {R['n']} pcs." if mixed else f"{R['n']} pcs.")),
        ("LED power", f"{R['W']:.1f} W (modules only)"),
        ("Pitch", fmt_p(R["pitch_of"]) + " mm (by stroke width)"),
        ("12V feeds", f"{nfeeds}"), ("PSU", spec.get("psu", "?"))]
    K.main_data(X_MD, BY0, W_MD, BH, md_rows, lab_w=58)
    tb = {"client": spec.get("client", "?"), "title": spec.get("title", "LED LAYOUT"), "date": spec["date"],
          "drawing_no": spec.get("drawing_no", ""), "order_no": spec.get("order_no", "?"), "rev": spec.get("rev", "A"), "sheet": "1 / 2"}
    if spec.get("revisions"):
        tb["revisions"] = spec["revisions"]
    K.title_block(X_TB, W_TB, tb, f"1:{SC:g}")
    # ---------------- 2 lapas: apšviestumo patikra
    K.c.showPage()
    K.frame()
    K.view_title((K.IX0 + K.IX1) / 2, K.IY0 + 26, "ILLUMINANCE CHECK - SIMULATED FACE (INSIDE)", f"1:{SC:g}")
    import tempfile
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    stats, allE, evals = [], [], []
    for i, (g, pa) in enumerate(zip(L, R["rpaths"])):
        pos = [(q["x"], q["y"], q["ang"]) for q in R["lay"][i]]
        u, Em, cm, E, line, hh, ua = letter_eval(g, mod_of[i], depth, pos, pa)
        evals.append((cm, E, Em)); allE.append(Em); stats.append((nm_(i), len(pos), u, hh, ua))
    Eref = float(np.median(allE))
    for r in rows:
        b = bb(r)
        fig = plt.figure(figsize=((b[2] - b[0]) * k / 72, (b[3] - b[1]) * k / 72), dpi=150)
        ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(b[0], b[2]); ax.set_ylim(b[3], b[1]); ax.axis("off")
        for i in r:
            P = evals[i][0]["P"]
            ax.scatter(P[:, 0], P[:, 1], c=np.clip(evals[i][1] / max(evals[i][2], 1e-9), 0, 1.6), s=(EV * k * 150 / 72) ** 2 / 2.2, marker="s",
                       cmap="inferno", vmin=0.2, vmax=1.6, linewidths=0)
        tmp = tempfile.mktemp(suffix=".png")
        fig.savefig(tmp, transparent=True); plt.close(fig)
        i0 = r[0]
        K.c.drawImage(tmp, Xi(i0, b[0]), K.H - Yi(i0, b[3]), width=(b[2] - b[0]) * k, height=(b[3] - b[1]) * k, mask="auto")
    letters_outline(fill=None)
    modules_draw()
    ty = ybot + 24
    K.T(K.IX0 + 14, ty, "Colour: illuminance / mean of the same letter (dark 0.2 ... bright 1.6) - uniformity within a letter. "
        "Ripple on centre line: U = P5 / mean, H = P95 / mean. Rel. = letter mean / median of all letters.", 8, fit=K.IX1 - K.IX0 - 30, fit_min=8)
    K.T(K.IX0 + 14, ty + 11, "Limits from supplier's letter row: " + "; ".join(f"{m} U >= {results[m]['U_t']:.2f}, H <= {results[m]['H_t']:.2f}" for m in used)
        + "; face A = P5 / mean >= " + ", ".join(f"{m} {results[m]['UA_t']:.2f}" for m in used)
        + f" (one row, stroke 1.25 x supplier pitch). Model: lens cos^{LENS_A}, wall reflectance {RHO}.", 8, fit=K.IX1 - K.IX0 - 30, fit_min=8)
    ncol = 4; colw = (K.IX1 - K.IX0 - 28) / ncol; x0_ = K.IX0 + 14; y0_ = ty + 28
    for j, (nm, n_, u, hh, ua) in enumerate(stats):
        cx_ = x0_ + (j % ncol) * colw; cy_ = y0_ + (j // ncol) * 11
        okj = n_ <= 1 or (u >= R["U_t_of"][j] * TOL_LO and hh <= R["H_t_of"][j] * TOL_HI and ua >= R["UA_t_of"][j] * TOL_LO)
        K.T(cx_, cy_, f'"{nm}": {mod_of[j]} {n_} pcs, U {u:.2f}, H {hh:.2f}, A {ua:.2f}, rel. {allE[j] / Eref:.2f}, {n_ / (L[j].area / 1e6):.0f}/m2 '
            + ("OK" if okj else "!"), 8, color=black if okj else K.CABLE, fit=colw - 6, fit_min=8)
    K.set_band(4)
    tb["sheet"] = "2 / 2"
    K.title_block(X_TB, W_TB, tb, f"1:{SC:g}")
    K.save(out)
    if os.path.exists(out + ".tmp.pdf"):
        os.remove(out + ".tmp.pdf")
    return MODL, nfeeds, long_links


if __name__ == "__main__":
    sp = json.load(open(sys.argv[1], encoding="utf-8"))
    if not os.path.isabs(sp["pdf"]):
        sp["pdf"] = os.path.join(os.path.dirname(os.path.abspath(sys.argv[1])), sp["pdf"])
    L, paths, R = solve(sp)
    if os.environ.get("LED_SIM_PKL"):                    # derinimui: išsaugoti sprendimą
        import pickle
        pickle.dump((L, paths, R), open(os.environ["LED_SIM_PKL"], "wb"))
    if len(sys.argv) > 2:
        print(sheet(sp, L, paths, R, sys.argv[2]))
