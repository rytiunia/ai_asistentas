#!/usr/bin/env python3
"""v172 (Rytis 2026-10-13: „matmenų linijos sugrūdamos viena ant kitos; nuorodų linijos lipa ant skaičių, fono, kitų linijų;
kai kur ne hairline. Visos problemos buvo aptartos, dabar vėl kartojasi. Kodėl?") - AUTOMATINĖ lapo patikra.
Taisyklės buvo tik tekste (stilius.md) - generatoriai jų nevykdė ir nebuvo jokios patikros. Dabar PRIVALOMA: kiekvienas
lapas prieš atiduodant - `python3 scripts/patikra_lapas.py lapas.pdf [--skip x0,y0,x1,y1 ...]`, rezultatas turi būti 0 klaidų.

Tikrinama vaizdų zonoje (virš apatinės juostos):
  1. HAIRLINE - objektų linijos tik 0,1 pt (leidžiama: matmenys / išvadinės 0,2-0,3, pjūvio plokštuma 0,8, laidas 0,9,
     sandūros punktyras 0,5, balti fonai). Kita - klaida (pvz. įdėto originalo 0,43 pt kontūrai).
  2. TEKSTAS ANT TEKSTO - užrašų stačiakampiai nesikerta.
  3. LINIJA PER TEKSTĄ - matmenų / išvadinių / laidų linijos (>= 0,2 pt) nekerta svetimo teksto (skaičių).
  4. MATMENYS VIENAS ANT KITO - lygiagrečios matmenų linijos toje pačioje eilėje (±1,5 pt) neužeina viena ant kitos.
  5. IŠVADINĖ PER IŠVADINĘ / MATMENĮ - nuorodų (išvadinių) linijos nesikerta su kitomis matmenų / išvadinių linijomis.
--skip - sritys, kurių 2-5 netikrinti (įdėtas originalo fragmentas: jo turinys - originalo, ne mūsų išdėstymas).
v182: `<lapas>.pdf.art.json` (rašo lapas_core.save per place_pdf) - KLIENTO GRAFIKA (spausdinama, v162 neliečiama): joje
netikrinama nieko (ir hairline); atkarpos, visiškai už savo iškarpos (clip), nematomos - netikrinamos.
"""
import math
import sys

import pymupdf as fitz

HAIR_OK = (0.0, 0.12)
ALLOWED = [(0.18, 0.31), (0.49, 0.51), (0.79, 0.81), (0.89, 0.91)]


def _segs(dr):
    out = []
    for it in dr["items"]:
        if it[0] == "l":
            out.append((it[1].x, it[1].y, it[2].x, it[2].y))
        elif it[0] == "re":
            r = it[1]
            out += [(r.x0, r.y0, r.x1, r.y0), (r.x1, r.y0, r.x1, r.y1), (r.x1, r.y1, r.x0, r.y1), (r.x0, r.y1, r.x0, r.y0)]
        elif it[0] == "c":                               # Bezier - laužtė (ne styga: apskritimo styga kirstų skaičių)
            p0, p1, p2, p3 = it[1], it[2], it[3], it[4]
            pts = []
            for k in range(7):
                t = k / 6
                pts.append(((1 - t) ** 3 * p0.x + 3 * (1 - t) ** 2 * t * p1.x + 3 * (1 - t) * t * t * p2.x + t ** 3 * p3.x,
                            (1 - t) ** 3 * p0.y + 3 * (1 - t) ** 2 * t * p1.y + 3 * (1 - t) * t * t * p2.y + t ** 3 * p3.y))
            out += [(a[0], a[1], b[0], b[1]) for a, b in zip(pts[:-1], pts[1:])]
    return out


def _seg_rect(s, r):
    """atkarpa kerta stačiakampį (Liang-Barsky)"""
    x0, y0, x1, y1 = s
    dx, dy = x1 - x0, y1 - y0
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, x0 - r.x0), (dx, r.x1 - x0), (-dy, y0 - r.y0), (dy, r.y1 - y0)):
        if p == 0:
            if q < 0:
                return False
        else:
            t = q / p
            if p < 0:
                t0 = max(t0, t)
            else:
                t1 = min(t1, t)
            if t0 > t1:
                return False
    return True


def _cross(a, b):
    def ccw(p, q, r):
        return (r[1] - p[1]) * (q[0] - p[0]) - (q[1] - p[1]) * (r[0] - p[0])
    p1, p2, p3, p4 = (a[0], a[1]), (a[2], a[3]), (b[0], b[1]), (b[2], b[3])
    d1, d2, d3, d4 = ccw(p3, p4, p1), ccw(p3, p4, p2), ccw(p1, p2, p3), ccw(p1, p2, p4)
    return d1 * d2 < -1e-6 and d3 * d4 < -1e-6


def check(pdf, band_y=None, skips=(), verbose=True):
    doc = fitz.open(pdf)
    arts = []
    import json, os
    if os.path.exists(pdf + ".art.json"):                                          # v182: K.place_pdf kliento grafikos sritys
        arts = json.load(open(pdf + ".art.json"))["art"]
    total = 0
    for pno, pg in enumerate(doc):
        errs = []
        by = band_y
        if by is None:                                   # apatinės juostos viršus - aukščiausia ilga horizontali 0,6-1 pt linija
            cands = [round(d["rect"].y0) for d in pg.get_drawings() if d.get("width") and 0.55 < d["width"] < 1.05
                     and d["rect"].width > 100 and d["rect"].y0 > pg.rect.height * 0.55]
            cands = [y for y in set(cands) if cands.count(y) >= 2]     # juostos blokų antraštės - kelios toje pačioje y
            by = min(cands) if cands else pg.rect.height * 0.78
        top = 32
        S = [fitz.Rect(s) for s in skips if (len(s) == 4) or s[4] == pno]
        S = [fitz.Rect(s[:4]) for s in skips if len(s) == 4 or s[4] == pno]
        ART = [fitz.Rect(a[0] - 1, a[1] - 1, a[2] + 1, a[3] + 1) for a in arts if a[4] == pno]
        S += [fitz.Rect(a) for a in ART]                                           # kliento grafika - ir 2-5 netikrinami
        inskip = lambda r: any(k.intersects(r) for k in S)
        spans = []
        for b in pg.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                for s in l["spans"]:
                    r = fitz.Rect(s["bbox"])
                    if s["text"].strip() and r.y1 < by and r.y0 > top:
                        h = r.height
                        if abs(l["dir"][0]) > 0.5:
                            rr = fitz.Rect(r.x0 + 0.5, r.y0 + h * 0.22, r.x1 - 0.5, r.y1 - h * 0.18)   # tik glifų kūnas
                        else:                                                                    # pasuktas tekstas
                            w = r.width
                            rr = fitz.Rect(r.x0 + w * 0.18, r.y0 + 0.5, r.x1 - w * 0.22, r.y1 - 0.5)
                        spans.append((rr, s["text"].strip(), l["dir"]))
        lines, leaders = [], []
        # v182: iškarpos (clip) - atkarpos visiškai už savo iškarpos nematomos (pvz. įdėto fragmento turinys už rėmo) -> netikrinamos
        vis = []
        stack = []
        for d in pg.get_drawings(extended=True):
            L = d.get("level", 0)
            while stack and stack[-1][0] >= L:
                stack.pop()
            cur = stack[-1][1] if stack else None
            if d["type"] == "clip":
                sc = fitz.Rect(d["scissor"])
                if sc.is_empty or sc.x0 > sc.x1 or sc.y0 > sc.y1:
                    sc = fitz.Rect(0, 0, 0, 0)
                stack.append((L, sc if cur is None else (sc & cur)))
                continue
            if d["type"] == "group" or "items" not in d:
                stack.append((L, cur if cur is not None else pg.rect))
                continue
            if cur is not None:
                cr = fitz.Rect(cur.x0 - 0.05, cur.y0 - 0.05, cur.x1 + 0.05, cur.y1 + 0.05)
                if cur.is_empty or not any(_seg_rect(sg, cr) for sg in _segs(d)):
                    continue                                                       # visa kelio dalis nematoma
                d = dict(d); d["_clip"] = cr
            if any(a_.contains(d["rect"]) for a_ in ART):
                continue                                                           # kliento grafika (v162 - neliečiama)
            vis.append(d)
        for d in vis:
            r = d["rect"]
            if r.y0 >= by - 1 or r.y1 < top or d["type"] not in ("s", "fs") or r.width > pg.rect.width * 0.8:
                continue
            w = d.get("width") or 0
            col = d.get("color") or (0, 0, 0)
            white = min(col) > 0.95
            if white:
                continue
            ok = HAIR_OK[0] <= w <= HAIR_OK[1] or any(a <= w <= b for a, b in ALLOWED)
            if not ok and r.width * r.height > 0.5:
                errs.append(f"HAIRLINE: linija {w:.2f} pt ties ({r.x0:.0f}, {r.y0:.0f})")
            if w >= 0.18 and not inskip(r):
                dark = max(col) < 0.35
                for sg in _segs(d):
                    if "_clip" in d and not _seg_rect(sg, d["_clip"]):
                        continue
                    lines.append((sg, w if dark or col[0] > 0.6 else -w, d))      # pilkos išvadinės (ext) - neigiamas
        # balionų skaičiai (tekstas apskritime) - išvadinė eina iki centro po baltu užpildu, netikrinami
        circ = [fitz.Rect(d["rect"]) for d in pg.get_drawings() if d["rect"].width < 20 and abs(d["rect"].width - d["rect"].height) < 1
                and sum(1 for it in d["items"] if it[0] == "c") >= 4]
        spans = [sp for sp in spans if not any(c_.contains(sp[0]) for c_ in circ)]
        # baltu fonu (maskė) apjuostas tekstas - linija po juo nematoma
        masks = [fitz.Rect(d["rect"]) for d in pg.get_drawings() if d["type"] == "f" and d.get("fill") and min(d["fill"]) > 0.97
                 and d["rect"].width < 200 and d["rect"].height < 40]
        masked = [sp for sp in spans if any(m_.contains(sp[0]) for m_ in masks)]
        # 2. tekstas ant teksto (ir baltu fonu apjuosti)
        for i in range(len(spans)):
            for j in range(i + 1, len(spans)):
                a, b = spans[i][0], spans[j][0]
                if a.intersects(b) and not (inskip(a) or inskip(b)):
                    if abs(a.y0 - b.y0) < 0.5 and abs(a.x1 - b.x0) < 2:          # ta pati eilutė, kelios spalvos
                        continue
                    errs.append(f"TEKSTAS ANT TEKSTO: '{spans[i][1]}' x '{spans[j][1]}' ({a.x0:.0f}, {a.y0:.0f})")
        # 3. linija per tekstą (baltu fonu apjuosti - linija po jais nematoma)
        for rr, t, dr_ in spans:
            if inskip(rr) or any(rr == m_[0] for m_ in masked):
                continue
            hit = [sg for sg, w, d in lines if _seg_rect(sg, rr)]
            # leidžiama: teksto paties pabraukimas (lygiagreti linija apačioje) - glifų kūno stačiakampis to neapima
            if hit:
                errs.append(f"LINIJA PER TEKSTĄ: '{t}' ({rr.x0:.0f}, {rr.y0:.0f}) - {len(hit)} atkarp.")
        # 4. matmenys vienas ant kito (lygiagrečios ilgos 0,25-0,3 pt atkarpos toje pačioje eilėje, persidengia)
        dims = [sg for sg, w, d in lines if 0.24 <= w <= 0.31]
        hz = [s for s in dims if abs(s[1] - s[3]) < 0.2 and abs(s[0] - s[2]) > 12]
        vt = [s for s in dims if abs(s[0] - s[2]) < 0.2 and abs(s[1] - s[3]) > 12]
        for grp, ax in ((hz, 1), (vt, 0)):
            for i in range(len(grp)):
                for j in range(i + 1, len(grp)):
                    a, b = grp[i], grp[j]
                    if abs(a[ax] - b[ax]) > 1.5:
                        continue
                    o = 1 - ax
                    a0, a1 = sorted((a[o], a[o + 2])); b0, b1 = sorted((b[o], b[o + 2]))
                    ov = min(a1, b1) - max(a0, b0)
                    if ov > 3 and not (abs(a0 - b0) < 0.5 and abs(a1 - b1) < 0.5):
                        errs.append(f"MATMENYS VIENAS ANT KITO: eilė {a[ax]:.0f}, ({max(a0, b0):.0f}..{min(a1, b1):.0f})")
        # 5. įstrižos išvadinės nesikerta su matmenimis / kitomis išvadinėmis
        diag = [sg for sg, w, d in lines if 0.24 <= w <= 0.31 and abs(sg[0] - sg[2]) > 2 and abs(sg[1] - sg[3]) > 2]
        straight = [sg for sg, w, d in lines if 0.18 <= w <= 0.31 and sg not in diag]
        # v176: išvadinė į objektą, kurį iš visų pusių supa matmenų eilės (balionas privalo būti UŽ vaizdo ribų), neišvengiamai
        # kerta VIENĄ matmens liniją - leidžiama tik viena, statmenai (>= 45°) ir ne arčiau 4 pt nuo teksto. Kita - klaida.
        def _ang_ok(a, b):
            va = (a[2] - a[0], a[3] - a[1]); vb = (b[2] - b[0], b[3] - b[1])
            cs = abs(va[0] * vb[0] + va[1] * vb[1]) / (math.hypot(*va) * math.hypot(*vb) + 1e-9)
            return cs <= math.cos(math.radians(45))
        def _xpt(a, b):
            x1, y1, x2, y2 = a; x3, y3, x4, y4 = b
            dd = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
            t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / dd
            return x1 + t * (x2 - x1), y1 + t * (y2 - y1)
        for a in diag:
            dimx = []
            for b in diag + straight:
                if a is not b and _cross(a, b):
                    if b in straight and 0.24 <= max(abs(b[0] - b[2]), abs(b[1] - b[3])) and _ang_ok(a, b):
                        px_, py_ = _xpt(a, b)
                        near = any(fitz.Rect(sp[0].x0 - 4, sp[0].y0 - 4, sp[0].x1 + 4, sp[0].y1 + 4).contains(fitz.Point(px_, py_))
                                   for sp in spans)
                        if not near:
                            dimx.append(b)
                            continue
                    errs.append(f"IŠVADINĖ KERTA LINIJĄ: ({a[0]:.0f}, {a[1]:.0f}) -> ({a[2]:.0f}, {a[3]:.0f})")
            if len(dimx) > 1:
                errs.append(f"IŠVADINĖ KERTA {len(dimx)} MATMENŲ LINIJAS: ({a[0]:.0f}, {a[1]:.0f}) -> ({a[2]:.0f}, {a[3]:.0f})")
        errs = sorted(set(errs))
        total += len(errs)
        if verbose:
            print(f"psl. {pno + 1}: {len(errs)} klaid.")
            for e in errs[:80]:
                print("   ", e)
    return total


if __name__ == "__main__":
    args = sys.argv[1:]
    pdf = args[0]
    sk = []
    i = 1
    while i < len(args):
        if args[i] == "--skip":
            sk.append(tuple(float(v) for v in args[i + 1].split(",")))
            i += 2
        else:
            i += 1
    n = check(pdf, skips=sk)
    print("IŠ VISO:", n)
    sys.exit(1 if n else 0)
