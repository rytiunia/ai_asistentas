#!/usr/bin/env python3
"""LED (Kaisen PRISM, v127) išdėstymas raidėse - GAMYBOS STILIUS (v119, Rytis 2026-10-12: „led dėliojimas vis dar blogas",
pavyzdžiai: assets/led_pavyzdziai/, ypač ALT8873 EXTRA 225978_1 / _2 - Ryčio perdaryti mūsų lapai).

NUMATYTAS LED įrankis (led_sim.py Lens simuliacija - tik paprašius). Principas:
  - modulis KM-P2 HE 0,72 W (balti 6500K) / KM-P2-R HE 0,72 W (raudoni) - viena eilė per raidės ašį;
  - žingsnis („atstumas tarp centrų") pagal gylį: 50 -> 100, 70 -> 120, 80 -> 130, 100 -> 140 mm (spec "pitch" - kitaip);
  - apskritimas aplink modulį = žingsnis; statūs galai - apskritimas liečia galą (modulis p/2 nuo krašto),
    sankirtoje vienas modulis, žiedai simetriški (led_sim.structured, v119 galų taisyklė);
  - labai plati linija (> 2 x žingsnis) - tinklelis per plotą (EXTRA H1800 X);
  - galia = vnt. x 0,72 W; PSU - mažiausias KPS, kurio apkrova <= 75 %.
Lapas: kiekis virš raidės, aukštis / plotis, eilutė „LED module ... | N PCS. | Galia: ~W | Depth | Atstumas tarp centru",
PSU, „N pcs.", M 1:x, pavadinimas „<ALT>_<užsakymas>_LED".

Naudojimas: python3 led_km.py spec.json out.pdf
Spec: pdf, page, crop_pt, scale_mm_per_pt | ref_width_mm, depth, qty, order_no, title ("ALT..._... _LED"),
      groups: [{fill_rgb, led: "white" | "red", name, pitch?}]  (arba fill_rgb + led viršuje - viena grupė).
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import led_sim as LS  # noqa: E402  read_letters, skeleton_paths, _at, stroke_max

# v127 (Rytis 2026-10-12: „pridedu papildomą informaciją dėl LED ... failai gauti gamyboje, laikyti kaip NAUJĄ VERSIJĄ"):
# moduliai, PSU ir ryškumo lentelės - Kaisen Electric (assets/kaisen_led.json: kainoraštis 2023 Alt Reklama + Modules Depth
# table 2023). Modulis pagal gylį (kainoraščio diapazonai, PRISM 12V): 30-49 KM-P0, 50-59 KM-P1, 60-100 KM-P2 0,72W,
# 101-120 KM-P2 1W, 121-150 KM-P3 1,5W, 151-250 KM-P4 2W; raudoni - KM-P*-R; plona linija (< 35 mm) - MINI3.
# Žingsnis - DIDŽIAUSIAS ryškumo lentelėje su lx >= lux_target (2200; Ryčio lapai: KM-P2 d100 p140 = 2250 lx), <= CC.
# PSU - Kaisen KPS outdoor IP67 (12V / 24V), apkrova <= 75 %.
_KJ = json.load(open(os.path.join(HERE, "..", "assets", "kaisen_led.json"), encoding="utf-8"))
MODDB = {m["code"]: dict(m, name=m["code"]) for m in _KJ["modules"]}
_TAB = {b["name"]: [(float(d), float(p_), float(l)) for d, p_, l in b["table"]] for b in _KJ["depth_tables"]}
PSU = [tuple(x) for x in _KJ["psu_12v_outdoor"]]
PSU24 = [tuple(x) for x in _KJ["psu_24v_outdoor"]]
PSU_LOAD = 0.75
LUX = float(_KJ.get("lux_target", 2200))


def mod_for(depth, spec_mod=None, led="white", w=None):
    if spec_mod:
        return spec_mod
    if w is not None and w < _KJ.get("narrow_stroke_mm", 35) and led != "red":
        for r in _KJ["narrow"]:
            if r["depth"][0] <= depth <= r["depth"][1]:
                return r["code"]
    code = "KM-P2-W"
    for r in _KJ["letters_default"]:
        if r["depth"][0] <= depth <= r["depth"][1]:
            code = r["code"]; break
    if led == "red":
        code = _KJ["red"].get(code, code)
    return code


def mod_label(m, led):
    d = MODDB[m]
    return f"{d['code']} {str(d['W']).replace('.', ',')}W {d['V']}V" + (" RED" if d.get("color") == "red" else " 6500K")


def leds_of(m):
    w = MODDB[m]["W"]
    return 1 if w <= 0.5 else 2 if w <= 1.0 else 3 if w <= 1.5 else 4


def pitch_for(depth, m="KM-P2-W", led="white"):
    """didžiausias lentelės žingsnis su lx >= LUX (tarp lentelės gylių - tiesinė interpoliacija pagal gylį)"""
    md = MODDB[m]
    tab = _TAB.get(md.get("table") or "")
    cap = md.get("cc_mm") or 999
    if not tab:
        return int(min(cap, 0.7 * cap) // 10 * 10)
    ds = sorted(set(d for d, _, _ in tab))
    dd = min(max(depth, ds[0]), ds[-1])
    lo = max([d for d in ds if d <= dd]); hi = min([d for d in ds if d >= dd])
    best = None
    for p_ in sorted(set(p_ for _, p_, _ in tab)):
        def lx(d):
            v = [l for d2, p2, l in tab if d2 == d and p2 == p_]
            return v[0] if v else None
        a, b = lx(lo), lx(hi)
        if a is None or b is None:
            continue
        l = a if hi == lo else a + (b - a) * (dd - lo) / (hi - lo)
        if l >= LUX and p_ <= cap:
            best = p_
    if best is None:
        best = min(p_ for _, p_, _ in tab)
    return int(best)


def psu_for(watts, V=12):
    lst = PSU if V == 12 else PSU24
    for nm, w in lst:
        if watts <= PSU_LOAD * w:
            return nm, w
    nm, w = lst[-1]
    n = math.ceil(watts / (PSU_LOAD * w))
    return f"{n} x {nm}", w * n


def _split_bends(pa, pitch, ang_min=45.0):
    """v126: aštrus lenkimas (7, L, Z kampas) - šaka dalijama per kampą, kampe - modulis (Ryčio taisyklė 3)"""
    P, cum = pa["P"], pa["cum"]
    if pa["kind"] == "loop" or len(P) < 30:
        return [pa], []
    k = 12
    cuts = []
    for i in range(k, len(P) - k):
        a = P[i] - P[i - k]; b = P[i + k] - P[i]
        na, nb = math.hypot(*a), math.hypot(*b)
        if na < 1e-6 or nb < 1e-6:
            continue
        t = math.degrees(math.acos(max(-1, min(1, float(a @ b) / (na * nb)))))
        if t >= ang_min and cum[i] > 0.4 * pitch and cum[-1] - cum[i] > 0.4 * pitch:
            if cuts and cum[i] - cum[cuts[-1][0]] < 0.5 * pitch:
                if t > cuts[-1][1]:
                    cuts[-1] = (i, t)
                continue
            cuts.append((i, t))
    if not cuts:
        return [pa], []
    out, corners, i0 = [], [], 0
    e0, e1 = pa["ends"]
    idx = [c for c, _ in cuts]
    for n_, i1 in enumerate(idx + [len(P) - 1]):
        sub = P[i0:i1 + 1]
        cs = np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(sub, axis=0).T))])
        ends = [e0 if n_ == 0 else "c", e1 if i1 == len(P) - 1 else "c"]
        out.append({"P": sub, "cum": cs, "kind": "open", "ends": ends})
        i0 = i1
    corners = [(float(P[c][0]), float(P[c][1])) for c in idx]
    return out, corners


def chain(g, pitch):
    """v126 viena eilė per ašį (Ryčio lapai): status galas - modulis p/2 nuo krašto; sankirtoje ir aštriame kampe -
    po modulį; šaka tarp jų - lygiais tarpais <= ~p; galiniai moduliai NEŠALINAMI dėl sankirtos (A kojos)"""
    paths0 = LS.skeleton_paths(g)
    pos, nodes = [], []
    paths = []
    for pa in paths0:
        sp, cn = _split_bends(pa, pitch)
        paths += sp
        nodes += [(x, y, "c") for x, y in cn]
    for pa in paths:
        L = pa["cum"][-1]
        if pa["kind"] == "loop":
            n = max(2, round(L / pitch)); n += n % 2
            x0, y0, x1, y1 = g.bounds; cx = (x0 + x1) / 2
            best = None
            for ph in np.linspace(0, L / n, 24, endpoint=False):
                A_ = np.array([LS._at(pa, (ph + i * L / n) % L)[:2] for i in range(n)])
                M_ = np.column_stack([cx - (A_[:, 0] - cx), A_[:, 1]])
                err = float(np.min(np.hypot(M_[:, None, 0] - A_[None, :, 0], M_[:, None, 1] - A_[None, :, 1]), axis=1).sum())
                if best is None or err < best[0]:
                    best = (err, ph)
            pos += [LS._at(pa, (best[1] + i * L / n) % L) for i in range(n)]
            continue
        e0, e1 = pa["ends"]
        for e_, et in ((0, e0), (1, e1)):
            if et == "j":
                P = pa["P"] if e_ == 0 else pa["P"][::-1]
                nodes.append((float(P[0][0]), float(P[0][1]), "j"))
        node = lambda et: et in ("j", "c")
        a_ = pitch / 2 if e0 == "edge" else 0.0
        b_ = L - (pitch / 2 if e1 == "edge" else 0.0)
        if not node(e0) and not node(e1):                 # du galai
            if b_ - a_ < 0.5 * pitch:
                pos.append(LS._at(pa, L / 2)); continue
            k_ = max(1, round((b_ - a_) / pitch))
            us = [a_ + i * (b_ - a_) / k_ for i in range(k_ + 1)]
        elif node(e0) and node(e1):                       # tarp dviejų mazgų - tik vidiniai
            k_ = max(1, round(L / pitch))
            us = [L * i / k_ for i in range(1, k_)]
        else:                                             # galas -> mazgas: nuo galo p/2, lygiai iki mazgo
            fw = not node(e0)
            free_off = a_ if fw else L - b_
            span = L - free_off
            k_ = max(1, round(span / pitch))
            st = span / k_
            us = [free_off + i * st for i in range(k_)]
            if not fw:
                us = [L - u for u in us]
        pos += [LS._at(pa, u) for u in us]
    # mazgai (sankirtos / kampai): artimi - vienas; mazgo modulis nededamas, jei šalia (< 0,45 p) yra šakos modulis
    nd = []
    for q in nodes:
        if all(math.dist(q[:2], r[:2]) > 15 for r in nd):
            nd.append(q)
    out = [tuple(float(v) for v in q[:3]) for q in pos]
    pruned = []
    for q in out:
        if all(math.dist(q[:2], r[:2]) >= 0.45 * pitch for r in pruned):
            pruned.append(q)
    for x, y, _ in nd:
        if all(math.dist((x, y), r[:2]) >= 0.55 * pitch for r in pruned):
            pruned.append((x, y, 0.0))
    return pruned


def grid(g, pitch):
    """plati linija - tinklelis per plotą (centrai >= 0,35 p nuo krašto), fazė - daugiausia taškų"""
    inner = g.buffer(-0.35 * pitch)
    if inner.is_empty:
        return chain(g, pitch)
    from shapely import contains_xy
    x0, y0, x1, y1 = g.bounds
    best = []
    for fx in np.linspace(0, pitch, 6, endpoint=False):
        for fy in np.linspace(0, pitch, 6, endpoint=False):
            xs = np.arange(x0 + fx, x1, pitch); ys = np.arange(y0 + fy, y1, pitch)
            X, Y = np.meshgrid(xs, ys); X, Y = X.ravel(), Y.ravel()
            k = contains_xy(inner, X, Y)
            pts = [(x_, y_, 0.0) for x_, y_ in zip(X[k].tolist(), Y[k].tolist())]
            if len(pts) > len(best):
                best = pts
    return best


def place(g, pitch):
    w = LS.stroke_max(g)
    return (grid(g, pitch), "grid") if w > 2.0 * pitch else (chain(g, pitch), "chain")


def run(spec):
    groups = spec.get("groups") or [{"fill_rgb": spec["fill_rgb"], "led": spec.get("led", "white"), "name": ""}]
    depth = spec["depth"]
    res = []
    allL = []
    for gr in groups:
        L, S = LS.read_letters(spec["pdf"], gr["fill_rgb"], crop_pt=spec.get("crop_pt"), scale=spec.get("scale_mm_per_pt"),
                               ref_width_mm=spec.get("ref_width_mm"), page=spec.get("page", 0),
                               min_area_mm2=spec.get("min_area_mm2", 300))
        allL.append(L)
    # bendras nulis: visų grupių min (read_letters nulina pagal savo grupę) - perskaičiuojama pagal PDF
    import pymupdf as fitz
    pg = fitz.open(spec["pdf"])[spec.get("page", 0)]
    sc = spec.get("scale_mm_per_pt")
    org = {}
    for k, gr in enumerate(groups):
        fills = gr["fill_rgb"] if isinstance(gr["fill_rgb"][0], (list, tuple)) else [gr["fill_rgb"]]
        xs, ys = [], []
        for d in pg.get_drawings():
            f = d.get("fill"); r = d["rect"]; c = spec.get("crop_pt")
            if not f or not any(all(abs(a - b) <= 0.02 for a, b in zip(f, fc)) for fc in fills):
                continue
            if c and not (r.x0 >= c[0] and r.y0 >= c[1] and r.x1 <= c[2] and r.y1 <= c[3]):
                continue
            xs.append(r.x0); ys.append(r.y0)
        org[k] = (min(xs), min(ys))
    gx, gy = min(o[0] for o in org.values()), min(o[1] for o in org.values())
    from shapely import affinity
    for k, (gr, L) in enumerate(zip(groups, allL)):
        dx, dy = (org[k][0] - gx) * sc, (org[k][1] - gy) * sc
        L = [affinity.translate(g, dx, dy) for g in L]
        w_med = float(np.median([LS.stroke_max(g) for g in L])) if L else None
        m = mod_for(depth, gr.get("module") or spec.get("module"), gr.get("led", "white"), w_med)
        p = gr.get("pitch") or spec.get("pitch") or pitch_for(depth, m, gr.get("led", "white"))
        if not (gr.get("pitch") or spec.get("pitch")) and L:
            # v126: plonos linijos (mažos raidės) - žingsnis <= 1,6 x linijos plotis (geometrinė aprėptis)
            p = int(min(p, max(60, round(1.6 * w_med / 10.0) * 10)))
        per = []
        for g in L:
            pts, mode = place(g, p)
            per.append({"g": g, "pts": pts, "mode": mode})
        n = sum(len(x["pts"]) for x in per)
        watts = n * MODDB[m]["W"]
        res.append({"gr": gr, "mod": m, "pitch": p, "letters": per, "n": n, "W": watts, "psu": psu_for(watts, MODDB[m]["V"])})
        print(f"  {gr.get('name') or 'grupė'}: {mod_label(m, gr.get('led', 'white'))} žingsnis ~{p} -> " +
              ", ".join(str(len(x['pts'])) for x in per) + f" = {n} vnt., {watts:.1f} W, {psu_for(watts, MODDB[m]['V'])[0]}" +
              ("" if all(x["mode"] == "chain" for x in per) else "  (plati linija - tinklelis)"))
    return res


def _wire_order(pts):
    """v126: grandinės eiga raidėje - artimiausias kaimynas nuo apatinio kairio + 2-opt (laidas be šuolių)"""
    if len(pts) < 3:
        return list(pts)
    rest = list(pts)
    cur = min(rest, key=lambda q: q[0] - q[1] * 0.5)
    seq = [cur]; rest.remove(cur)
    while rest:
        cur = min(rest, key=lambda q: math.dist(q[:2], seq[-1][:2]))
        seq.append(cur); rest.remove(cur)
    improved = True
    while improved:
        improved = False
        for i in range(1, len(seq) - 2):
            for j in range(i + 1, len(seq) - 1):
                d0 = math.dist(seq[i - 1][:2], seq[i][:2]) + math.dist(seq[j][:2], seq[j + 1][:2])
                d1 = math.dist(seq[i - 1][:2], seq[j][:2]) + math.dist(seq[i][:2], seq[j + 1][:2])
                if d1 < d0 - 1e-6:
                    seq[i:j + 1] = seq[i:j + 1][::-1]; improved = True
    return seq


def sheet(spec, res, out):
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A3, landscape
    from reportlab.lib.colors import HexColor, black, white
    from reportlab.lib.units import mm
    W, H = landscape(A3)
    c = canvas.Canvas(out, pagesize=(W, H))
    GREY = HexColor("#E2E8E5"); RED = HexColor("#E2001A"); ORANGE = HexColor("#F7A600")
    # rėmas
    c.setLineWidth(0.4); c.setStrokeColor(HexColor("#BBBBBB")); c.rect(10 * mm, 10 * mm, W - 20 * mm, H - 20 * mm)
    c.setFont("Helvetica", 7); c.setFillColor(HexColor("#888888"))
    for i in range(8):
        x = 10 * mm + (W - 20 * mm) * (i + 0.5) / 8
        c.drawCentredString(x, H - 8 * mm, str(i + 1)); c.drawCentredString(x, 5 * mm, str(i + 1))
    for i, ch in enumerate("ABCDEF"):
        y = H - 10 * mm - (H - 20 * mm) * (i + 0.5) / 6
        c.drawCentredString(5 * mm, y, ch); c.drawCentredString(W - 5 * mm, y, ch)
    # turinys: visų grupių raidės
    allg = [x["g"] for r in res for x in r["letters"]]
    x0 = min(g.bounds[0] for g in allg); y0 = min(g.bounds[1] for g in allg)
    x1 = max(g.bounds[2] for g in allg); y1 = max(g.bounds[3] for g in allg)
    PW_, PH_ = x1 - x0, y1 - y0
    n_info = len(res)
    box_w, box_h = W - 70 * mm, H - 20 * mm - 60 * mm - n_info * 22
    s = min(box_w / PW_, box_h / PH_) * 0.92
    sc_ = 1.0 / (s / mm)                                  # 1 mm lapo = sc_ mm gaminio
    nice = [2, 2.5, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30, 40, 50]
    M = next((v for v in nice if v >= sc_), sc_)
    s = mm / M
    ox = (W - PW_ * s) / 2 - x0 * s
    top = H - 10 * mm - 28 * mm
    T = lambda x, y: (ox + x * s, top - (y - y0) * s)
    for r in res:
        col = RED if r["gr"].get("led") == "red" else black
        for x in r["letters"]:
            g = x["g"]
            for poly in getattr(g, "geoms", [g]):
                p_ = c.beginPath()
                for ring in [poly.exterior] + list(poly.interiors):
                    pts = [T(*q) for q in ring.coords]
                    p_.moveTo(*pts[0])
                    for q in pts[1:]:
                        p_.lineTo(*q)
                    p_.close()
                c.setFillColor(GREY); c.setStrokeColor(GREY); c.setLineWidth(0.1)
                c.drawPath(p_, stroke=0, fill=1, fillMode=0)
            c.setStrokeColor(col); c.setLineWidth(0.35)
            for (px, py, ang) in x["pts"]:
                cx, cy = T(px, py)
                c.circle(cx, cy, r["pitch"] / 2 * s, stroke=1, fill=0)
            # v120: LED IMITACIJA - modulio korpusas (lentelės matmenys) pagal ašies kryptį + LED / lęšiai (Rytis: gamybai
            # priimtiniau nei vieni apskritimai); grandinės laidas tarp gretimų modulių
            md = MODDB[r["mod"]]
            sz = md.get("size_mm") or [0.32 * r["pitch"], 0.12 * r["pitch"]]   # BaltLED matmenų nenurodo - simbolinis
            nl = leds_of(r["mod"])
            ml, mw = sz[0] * s, sz[1] * s
            seq = _wire_order(x["pts"])
            c.setStrokeColor(HexColor("#555555")); c.setLineWidth(0.3)
            for a_, b_ in zip(seq, seq[1:]):
                if math.dist(a_[:2], b_[:2]) <= 1.6 * r["pitch"]:
                    p0, p1 = T(*a_[:2]), T(*b_[:2]); c.line(p0[0], p0[1], p1[0], p1[1])
            for (px, py, ang) in seq:
                cx, cy = T(px, py)
                c.saveState(); c.translate(cx, cy); c.rotate(-math.degrees(ang))
                c.setFillColor(white); c.setStrokeColor(black); c.setLineWidth(0.4)
                c.roundRect(-ml / 2, -mw / 2, ml, mw, min(1.5, mw / 4), stroke=1, fill=1)
                c.setFillColor(col if r["gr"].get("led") == "red" else HexColor("#F2C200"))
                for i_ in range(nl):
                    lx = -ml / 2 + ml * (i_ + 0.5) / nl
                    c.circle(lx, 0, max(0.6, mw * 0.28), stroke=0, fill=1)
                c.restoreState()
            # kiekis virš raidės
            bx0, by0, bx1, by1 = g.bounds
            ymax = min(q[1] for q in x["pts"]) - r["pitch"] / 2 if x["pts"] else by0
            tx, ty = T((bx0 + bx1) / 2, min(by0, ymax))
            c.setFillColor(black); c.setFont("Helvetica-Bold", 13)
            c.drawCentredString(tx, ty + 8, str(len(x["pts"])))
    # matmenys
    c.setStrokeColor(black); c.setFillColor(black); c.setLineWidth(0.5)
    xa, yb = T(x0, y1); xb, _ = T(x1, y1)
    yd = yb - 14
    c.line(xa, yd, xb, yd); c.line(xa, yd - 4, xa, yd + 4); c.line(xb, yd - 4, xb, yd + 4)
    c.setFont("Helvetica", 9); c.drawCentredString((xa + xb) / 2, yd - 11, f"{PW_:.0f} mm")
    xl = xa - 14; _, yt = T(x0, y0)
    c.line(xl, yt, xl, yb); c.line(xl - 4, yt, xl + 4, yt); c.line(xl - 4, yb, xl + 4, yb)
    c.saveState(); c.translate(xl - 3, (yt + yb) / 2); c.rotate(90); c.drawCentredString(0, 0, f"{PH_:.0f} mm"); c.restoreState()
    # informacija
    yi = yd - 34
    for r in res:
        led = r["gr"].get("led", "white")
        c.setFont("Helvetica", 12); c.setFillColor(black)
        nm = (r["gr"].get("name") + ":  ") if r["gr"].get("name") and len(res) > 1 else ""
        c.drawString(xa, yi, f"{nm}LED module {mod_label(r['mod'], led)}  |  {r['n']} PCS.  |  Galia: ~{r['W']:.0f}W  |  "
                             f"Depth: {spec['depth']} mm  |  Atstumas tarp centru ~{r['pitch']} mm")
        if led == "red":
            c.setFillColor(RED); c.drawString(xa, yi - 14, "RED LED Modules"); c.setFillColor(black)
        else:
            c.drawString(xa, yi - 14, "White LED Modules, 6500K")
        c.drawString(xa + 200, yi - 14, f"PSU {r['psu'][0]}  ({r['psu'][1]} W, {MODDB[r['mod']]['V']} V, IP67)")
        yi -= 34
    # apačia
    c.setFillColor(black); c.rect(10 * mm, 22 * mm, 34 * mm, 14 * mm, stroke=0, fill=1)
    c.setFillColor(white); c.setFont("Helvetica", 18); c.drawString(13 * mm, 26 * mm, f"{spec.get('qty', 1)} pcs.")
    c.setFillColor(HexColor("#F2F2F2")); c.rect(10 * mm, 10 * mm, W - 20 * mm - 30 * mm, 12 * mm, stroke=0, fill=1)
    c.setFillColor(black); c.setFont("Helvetica", 16)
    c.drawString(16 * mm, 14 * mm, spec.get("title") or f"{spec.get('order_no', '')}_LED")
    c.setFont("Helvetica", 11); c.drawRightString(W - 42 * mm, 25 * mm, f"M 1:{M:g}")
    c.setFillColor(ORANGE); c.rect(W - 40 * mm, 10 * mm, 30 * mm, 18 * mm, stroke=0, fill=1)
    c.setFillColor(black); c.setFont("Helvetica-Bold", 20); c.drawCentredString(W - 25 * mm, 15 * mm, "LED")
    c.showPage(); c.save()
    return out


if __name__ == "__main__":
    sp = json.load(open(sys.argv[1], encoding="utf-8"))
    r = run(sp)
    if len(sys.argv) > 2:
        print("OK", sheet(sp, r, sys.argv[2]))
