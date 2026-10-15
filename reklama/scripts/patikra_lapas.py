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

import re
_DEC = re.compile(r"(?<![A-Za-z0-9_.,/])(\d+)\.(\d+)(?![\d.]*\.\d)(?=[^\d]|$)")
_DIMG = re.compile(r"(?:(?<=[^\w][LU])|(?<=^[LU])|(?<![\w,]))[Ø⌀]?\d+(?:,\d+)?(?:(?:\s*x\s*|\s+×\s+|(?<=\d)×\s*)[Ø⌀]?\d+(?:,\d+)?)+(?!\w|,\d)|[Ø⌀]\d+(?:,\d+)?(?!\w|,\d)")
_UNIT = re.compile(r"\s*(mm|m²|m\b|cm|°|˚)")
_LABEL = re.compile(r"[Ø⌀~≈(]?\d+(?:,\d+)?[)]?")          # vienas matmens skaičius brėžinyje (be x) - ne lentelės laukas
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
    arts, blocks = [], []
    import json, os
    if os.path.exists(pdf + ".art.json"):                                          # v182: K.place_pdf kliento grafikos sritys
        _j = json.load(open(pdf + ".art.json"))
        arts = _j.get("art", [])
        blocks = _j.get("blocks", [])
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
        # v190 (Rytis 2026-10-13: „pasikartojančios klaidos: ne hairline projekcijose") - DVIGUBA LINIJA: du hairline
        #  kontūrai (vienas kito viduje) arčiau nei 0,6 pt per visą perimetrą spaudoje susilieja į storą liniją
        _hl = [d["rect"] for d in vis if d["type"] in ("s", "fs") and (d.get("width") or 0) <= 0.12
               and d["rect"].y0 < by - 1 and d["rect"].y1 > top and d["rect"].width > 10 and d["rect"].height > 10
               and not any(a_.contains(d["rect"]) for a_ in ART)]
        _hl.sort(key=lambda r: (round(r.x0, 1), round(r.y0, 1)))
        for i in range(len(_hl)):
            a = _hl[i]
            for j in range(i + 1, len(_hl)):
                b = _hl[j]
                if b.x0 - a.x0 > 0.6:
                    break
                m = [abs(b.x0 - a.x0), abs(b.y0 - a.y0), abs(b.x1 - a.x1), abs(b.y1 - a.y1)]
                nested = (a.contains(b) or b.contains(a))
                if nested and 0.03 < max(m) < 0.6 and min(m) > 0.03 and not inskip(a):
                    errs.append(f"DVIGUBA LINIJA: kontūrai {max(m):.2f} pt vienas nuo kito ties ({a.x0:.0f}, {a.y0:.0f}) - susilieja į storą liniją")
                    break
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
        # 6. v276 (Rytis 2026-10-15, ISO 129-1 / references/cad_matmenavimas_ISO.md 5 sk.: „vėl linija ant linijos, žmogaus akiai tai
        #  labai klaidinanti informacija") - LINIJA ANT LINIJOS: matmenų / iškeltinių linijų (0,18-0,31, ir pilkos) atkarpa, sutampanti
        #  (ta pati tiesė ±0,6 pt, persidengia > 2 pt) su KITO objekto linija (kitas matmuo, pjūvio žymė, kontūras, išvadinė)
        allseg = []
        for d in vis:
            r_ = d["rect"]
            if r_.y0 >= by - 1 or r_.y1 < top or d["type"] not in ("s", "fs") or r_.width > pg.rect.width * 0.8:
                continue
            for sg in _segs(d):
                if math.hypot(sg[2] - sg[0], sg[3] - sg[1]) > 2:
                    allseg.append((sg, abs(d.get("width") or 0), id(d), bool(str(d.get("dashes") or "").strip("[] 0"))))
        dimsegs = [(sg, w, did) for sg, w, did, ds in allseg if 0.18 <= w <= 0.31 and not ds   # matmenų linijos niekada nebūna punktyrinės
                   and math.hypot(sg[2] - sg[0], sg[3] - sg[1]) >= 7]                         # < 7 pt - skylių centro kryželiai, ne matmenys
        allseg = [(sg, w, did) for sg, w, did, ds in allseg]
        def _coll(a, b):
            if abs(a[1] - a[3]) < 0.3 and abs(b[1] - b[3]) < 0.3 and abs(a[1] - b[1]) < 0.6:
                o = 0
            elif abs(a[0] - a[2]) < 0.3 and abs(b[0] - b[2]) < 0.3 and abs(a[0] - b[0]) < 0.6:
                o = 1
            else:
                return 0
            a0, a1 = sorted((a[o], a[o + 2])); b0, b1 = sorted((b[o], b[o + 2]))
            return min(a1, b1) - max(a0, b0)
        seen = set()
        for sg, w, did in dimsegs:
            if inskip(fitz.Rect(min(sg[0], sg[2]), min(sg[1], sg[3]), max(sg[0], sg[2]) + 0.1, max(sg[1], sg[3]) + 0.1)):
                continue
            for sg2, w2, did2 in allseg:
                if did2 == did:
                    continue
                ov = _coll(sg, sg2)
                if ov > 2:
                    k_ = (round(min(sg[0], sg2[0])), round(min(sg[1], sg2[1])))
                    if k_ not in seen:
                        seen.add(k_)
                        errs.append(f"LINIJA ANT LINIJOS: ({sg[0]:.0f}, {sg[1]:.0f})-({sg[2]:.0f}, {sg[3]:.0f}) x "
                                    f"({sg2[0]:.0f}, {sg2[1]:.0f})-({sg2[2]:.0f}, {sg2[3]:.0f}) [{w:.2f}/{w2:.2f} pt], {ov:.0f} pt")
        # 7. v276: MATMENŲ LINIJOS KERTASI (dvi tamsios matmenų linijos, statmenos, kertasi ne galuose)
        dl = [sg for sg, w, d in lines if 0.24 <= w <= 0.31 and max(abs(sg[0] - sg[2]), abs(sg[1] - sg[3])) > 8
              and (abs(sg[0] - sg[2]) < 0.2 or abs(sg[1] - sg[3]) < 0.2)]
        for i in range(len(dl)):
            for j in range(i + 1, len(dl)):
                if _cross(dl[i], dl[j]):
                    a_, b_ = dl[i], dl[j]
                    errs.append(f"MATMENYS KERTASI: ({a_[0]:.0f}, {a_[1]:.0f})-({a_[2]:.0f}, {a_[3]:.0f}) x ({b_[0]:.0f}, {b_[1]:.0f})-({b_[2]:.0f}, {b_[3]:.0f})")
        # 8. v276: RODYKLĖS PERSIDENGIA - mažos užpildytos rodyklės (matmenų, pjūvio žymių) viena ant kitos (> 40 % ploto)
        arr = [fitz.Rect(d["rect"]) for d in vis if d["type"] == "f" and len(d["items"]) == 3 and d.get("fill")
               and max(d["fill"]) < 0.15
               and all(it[0] == "l" for it in d["items"]) and d["rect"].width < 9 and d["rect"].height < 9
               and d["rect"].y0 < by - 1 and d["rect"].y1 > top]
        for i in range(len(arr)):
            for j in range(i + 1, len(arr)):
                a_, b_ = arr[i], arr[j]
                ia = a_ & b_
                if not ia.is_empty and ia.width * ia.height > 0.4 * min(a_.width * a_.height, b_.width * b_.height) \
                        and not (abs(a_.x0 - b_.x0) < 0.05 and abs(a_.y0 - b_.y0) < 0.05) and not inskip(a_):
                    errs.append(f"RODYKLĖS PERSIDENGIA: ({a_.x0:.0f}, {a_.y0:.0f})")
        # 9. v291 (Rytis 2026-10-15: „numeracijos skaičiai negali persidengti vienas su kitu") - BALIONAI PERSIDENGIA (visas lapas)
        bal = [fitz.Rect(d["rect"]) for d in pg.get_drawings() if 9 < d["rect"].width < 20
               and abs(d["rect"].width - d["rect"].height) < 0.6 and sum(1 for it in d["items"] if it[0] == "c") >= 4
               and d.get("fill") and min(d["fill"]) > 0.95 and d.get("color") is not None and max(d["color"]) < 0.2]
        for i in range(len(bal)):
            for j in range(i + 1, len(bal)):
                a_, b_ = bal[i], bal[j]
                dist = math.hypot((a_.x0 + a_.x1 - b_.x0 - b_.x1) / 2, (a_.y0 + a_.y1 - b_.y0 - b_.y1) / 2)
                if dist < (a_.width + b_.width) / 2 + 0.5:
                    errs.append(f"BALIONAI PERSIDENGIA: ({a_.x0:.0f}, {a_.y0:.0f}) x ({b_.x0:.0f}, {b_.y0:.0f})")
        # 10.-11. v291 (Rytis: „lentelėje nesuprasi kas kaip pažymėta - m ar mm? buvo įdėta taisyklė dėl matmenų ir informacijos")
        #  10 DEŠIMTAINIS TAŠKAS - visur kablelis (TAISYKLĖ 30); 11 VIENETAS NENURODYTAS - apatinėje juostoje (BOM / MAIN DATA /
        #  antraštė) matmenų grupė („515 x 2380", „Ø3,2", „30x30x2") privalo turėti vienetą (mm / m), kitaip neaišku m ar mm
        allsp = []
        for b in pg.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                for s_ in l["spans"]:
                    if s_["text"].strip() and not any(fitz.Rect(a_).contains(fitz.Rect(s_["bbox"])) for a_ in ART):
                        allsp.append((fitz.Rect(s_["bbox"]), s_["text"].strip()))
        for r_, t_ in allsp:
            if _DEC.search(t_):
                errs.append(f"DEŠIMTAINIS TAŠKAS (turi būti kablelis): '{t_}' ({r_.x0:.0f}, {r_.y0:.0f})")
            if r_.y0 > by and re.fullmatch(r"\d+(?:,\d+)?", t_):
                lab_ = [t2 for r2, t2 in allsp if abs(r2.y0 - r_.y0) < 2 and r2.x1 <= r_.x0 + 1 and r_.x0 - r2.x1 < 40]
                if lab_ and re.search(r"depth|size|width|height|length|thick", lab_[-1], re.I):
                    errs.append(f"VIENETAS NENURODYTAS (mm / m?): '{lab_[-1]}' = '{t_}' ({r_.x0:.0f}, {r_.y0:.0f})")
            if r_.y0 > by and not _LABEL.fullmatch(t_):
                for m_ in _DIMG.finditer(t_):
                    if not _UNIT.match(t_[m_.end():]):
                        errs.append(f"VIENETAS NENURODYTAS (mm / m?): '{m_.group(0)}' laukelyje '{t_}' ({r_.x0:.0f}, {r_.y0:.0f})")
        # 12. v291 TAISYKLĖ 5 (Rytis: „profilio pjūvis visada centruojamas savo bloke") - CENTRAVIMAS: lapas_core.centered blokai
        for bx, by_, bw, bh, bp, bn in blocks:
            if bp != pno:
                continue
            B = fitz.Rect(bx, by_, bx + bw, by_ + bh)
            Bi = fitz.Rect(bx + 1, by_ + 1, bx + bw - 1, by_ + bh - 1)
            rs = [fitz.Rect(d["rect"]) for d in pg.get_drawings() if Bi.contains(d["rect"]) and not d["rect"].is_empty]
            rs += [r_ for r_, t_ in allsp if Bi.contains(r_)]
            for r_, t_ in allsp:                                                   # tekstas per bloko kraštą - netelpa
                if r_.intersects(B) and not Bi.contains(r_) and r_.y0 > B.y0 + 1:
                    errs.append(f"NETELPA BLOKE '{bn}': '{t_}' ({r_.x0:.0f}, {r_.y0:.0f})")
            if not rs:
                continue
            bb = rs[0]
            for r_ in rs[1:]:
                bb |= r_
            ddx, ddy = (bb.x0 + bb.x1 - B.x0 - B.x1) / 2, (bb.y0 + bb.y1 - B.y0 - B.y1) / 2
            if abs(ddx) > max(3, 0.03 * bw) or abs(ddy) > max(3, 0.03 * bh):
                errs.append(f"NECENTRUOTA BLOKE '{bn}': poslinkis x {ddx:+.0f}, y {ddy:+.0f} pt")
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
