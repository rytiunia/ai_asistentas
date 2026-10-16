#!/usr/bin/env python3
"""v304 (Rytis 2026-10-16: „plotą visada skaičiuok nesting principu. tai taisyklė.") - LAKŠTŲ NESTING.

BOM plotas (m²) = medžiagos SUNAUDOJIMAS išdėsčius detales ant tiekėjo lakšto, ne grynasis detalių plotas.
  - detalės: tikri kontūrai (shapely, mm); kiekviena dedama mažiausiu pasuktu gabaritiniu stačiakampiu (kontūro kryptimi),
    leidžiamas pasukimas 90°; tarpas tarp detalių `gap` (10 mm - pjovimo / frezos tarpas), paraštė nuo lakšto krašto
    medziagos.json „parastė_mm" (10);
  - dėliojimas MaxRects (Best Short Side Fit) per lakštus; išbandomi visi tos medžiagos / storio formatai
    (medziagos.json) - imamas mažiausias sunaudojimas;
  - sunaudojimas = pilni lakštai + paskutinio lakšto panaudota juosta (iki toliausios detalės + tarpas, pjaunant skersai
    arba išilgai - mažesnė);
  - šonai (bortai, „returns") - juostos (raidės perimetras x gylis), ilgesnės už lakštą - dalijamos; dėliojamos taip pat.
Plėvelės nesting - plevele.py (rulonas).

    import nesting as NE
    r = NE.nest_parts(geoms, "Acrylic 8 mm white")      # -> {"m2", "sheets", "format", "parts_m2", "waste", "text"}
    r = NE.nest_strips([perimeter_mm...], 80, "Alu 1 mm")
v309 (Rytis 2026-10-16, Leapmotor 33577 - 40 / 20 vnt.): KIEKIS. Užsakymo kiekis gaminamas kartu - detalės dėliojamos
VISAM kiekiui (qty kopijų), BOM „per 1 pcs." = viso sunaudojimas / qty (ne vienos iškabos lakštas su 70 % atliekų).
    r = NE.nest_parts(geoms, mat, qty=40)    # -> r["m2"] per 1 vnt., r["m2_total"], r["qty"]
"""
import math
import re

import medziagos as MEDZ

GAP = 10.0
_MAT = [(r"acryl|plexi|pmma|akril|plazcryl|opal", "pmma"), (r"polycarb|\bpc\b|polikarb", "pc"),
        (r"\bakp\b|dibond|composite|kompozit", "akp"), (r"pvc", "pvc_putu"), (r"\bps\b|polistir", "ps"),
        (r"\balu|alumin|aliumin", "alu")]


def parse_material(text):
    t = str(text or "").lower()
    key = next((k for rx, k in _MAT if re.search(rx, t)), None)
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*mm", t)
    thk = float(m.group(1).replace(",", ".")) if m else None
    return key, thk


def formats(material_text):
    key, thk = parse_material(material_text)
    if not key:
        return [], key, thk
    fm = MEDZ.sheet_formats(key, thk)
    if not fm and thk is not None:                     # storio nėra sąraše - to paties tipo artimiausias storis
        allf = MEDZ.sheet_formats(key, None)
        if allf:
            near = min({f["storis_mm"] for f in allf}, key=lambda s: abs(float(s) - thk))
            fm = [f for f in allf if f["storis_mm"] == near]
            for f in fm:
                f["pastaba"] = f"storis {thk:g} mm formatų sąraše nėra - imtas {near} mm formatas"
    seen, out = set(), []
    for f in fm:
        if f["formatas_mm"] not in seen:
            seen.add(f["formatas_mm"]); out.append(f)
    return out, key, thk


def _rect_of(g):
    """mažiausias pasuktas gabaritinis stačiakampis (ilgis, plotis)"""
    try:
        mr = g.minimum_rotated_rectangle
        xs = list(mr.exterior.coords)[:4]
        d1 = math.dist(xs[0], xs[1]); d2 = math.dist(xs[1], xs[2])
        x0, y0, x1, y1 = g.bounds
        bw, bh = x1 - x0, y1 - y0
        if bw * bh <= d1 * d2 + 1e-6:                   # ašinis gabaritas ne didesnis - jį ir imti
            return max(bw, bh), min(bw, bh)
        return max(d1, d2), min(d1, d2)
    except Exception:
        x0, y0, x1, y1 = g.bounds
        return max(x1 - x0, y1 - y0), min(x1 - x0, y1 - y0)


def _maxrects(items, W, H, gap, rule="bssf"):
    """items [(w, h)] -> lakštų sąrašas [[(x, y, w, h)]], ilgis = W (x), plotis = H (y). BSSF, pasukimas 90°."""
    order = sorted(range(len(items)), key=lambda i: -items[i][0] * items[i][1])
    sheets = []
    for i in order:
        w, h = items[i][0] + gap, items[i][1] + gap
        placed = False
        for sh in sheets:
            best = None
            for fr in sh["free"]:
                for (a, b) in ((w, h), (h, w)):
                    if a <= fr[2] + 1e-6 and b <= fr[3] + 1e-6:
                        sc = (min(fr[2] - a, fr[3] - b), fr[0]) if rule == "bssf" else (fr[0] + a, fr[1])   # bl - kompaktiška juosta
                        if best is None or sc < best[0]:
                            best = (sc, (fr[0], fr[1], a, b))
            if best:
                _place(sh, best[1]); placed = True
                break
        if not placed:
            sh = {"free": [(0.0, 0.0, W + gap, H + gap)], "used": []}
            sheets.append(sh)
            if w <= W + gap + 1e-6 and h <= H + gap + 1e-6:
                _place(sh, (0.0, 0.0, w, h))
            elif h <= W + gap + 1e-6 and w <= H + gap + 1e-6:
                _place(sh, (0.0, 0.0, h, w))
            else:
                sh["used"].append((0.0, 0.0, w, h)); sh["oversize"] = True
    return sheets


def _place(sh, r):
    sh["used"].append(r)
    x, y, w, h = r
    nf = []
    for fr in sh["free"]:
        fx, fy, fw, fh = fr
        if x >= fx + fw or x + w <= fx or y >= fy + fh or y + h <= fy:
            nf.append(fr); continue
        if x > fx:
            nf.append((fx, fy, x - fx, fh))
        if x + w < fx + fw:
            nf.append((x + w, fy, fx + fw - x - w, fh))
        if y > fy:
            nf.append((fx, fy, fw, y - fy))
        if y + h < fy + fh:
            nf.append((fx, y + h, fw, fy + fh - y - h))
    nf = [f for f in nf if f[2] > 1 and f[3] > 1]
    sh["free"] = [f for f in nf if not any(g is not f and g[0] <= f[0] and g[1] <= f[1] and g[0] + g[2] >= f[0] + f[2]
                                           and g[1] + g[3] >= f[1] + f[3] for g in nf)]


def _nest_rects(rects, material_text, parts_m2, label, qty=1):
    qty = max(1, int(qty or 1))
    rects = list(rects) * qty
    parts_m2 = parts_m2 * qty
    fm, key, thk = formats(material_text)
    if not fm:
        return {"m2": None, "text": f"! nesting: medžiagos '{material_text}' lakštų formatų nėra (medziagos.json) - plotas neapskaičiuotas",
                "parts_m2": parts_m2}
    p = float(MEDZ.data()["lakstai"].get("parastė_mm", 10))
    best = None
    for f in fm:
        L0, S0 = f["formatas_mm"]
        for (L, S) in ((L0, S0), (S0, L0)):              # juosta išilgai ir skersai lakšto
            for rule in ("bssf", "bl"):
                W, H = L - 2 * p, S - 2 * p
                sheets = _maxrects(rects, W, H, GAP, rule)
                n = len(sheets)
                last = sheets[-1]["used"] if sheets else []
                lx = max((x + w for x, y, w, h in last), default=0.0)   # paskutinio lakšto panaudota juosta:
                ly = max((y + h for x, y, w, h in last), default=0.0)   #  pjaunama skersai ARBA išilgai - mažesnė
                m2 = ((n - 1) * L * S + min(min(L, lx + p) * S, min(S, ly + p) * L)) / 1e6 if n else 0.0
                cand = {"m2": m2, "sheets": n, "format": (L0, S0), "supplier": f.get("tiekejas", "?"), "parts_m2": parts_m2,
                        "waste": (1 - parts_m2 / m2) if m2 else 0.0, "oversize": any(sh.get("oversize") for sh in sheets)}
                if best is None or cand["m2"] < best["m2"] - 1e-9:
                    best = cand
    best["qty"], best["m2_total"] = qty, best["m2"]
    best["m2"], best["parts_m2"] = best["m2_total"] / qty, parts_m2 / qty
    best["text"] = ((f"nesting {label} ({qty} pcs.): " if qty > 1 else f"nesting {label}: ")
                    + f"{best['sheets']} x {best['format'][0]:.0f}x{best['format'][1]:.0f} ({best['supplier']}) -> "
                    f"{best['m2_total']:.2f} m²" + (f" = {best['m2']:.3f} m² / pcs." if qty > 1 else "")
                    + f" (detalės {parts_m2:.2f} m², atliekos {best['waste'] * 100:.0f} %)"
                    + (" ! detalė didesnė už lakštą - dalinti" if best["oversize"] else "")
                    + (f" ({fm[0]['pastaba']})" if fm and fm[0].get("pastaba", "").startswith("storis") else ""))
    return best


def nest_parts(geoms, material_text, label="parts", qty=1):
    gs = [g for g in geoms if g is not None and not g.is_empty]
    rects = [_rect_of(g) for g in gs]
    return _nest_rects(rects, material_text, sum(g.area for g in gs) / 1e6, label, qty)


def _ffd_strips(lengths, w, material_text, qty):
    """v309: juostos - 1D dėliojimas eilėmis (First Fit Decreasing): lakšte eilių = (S - 2p + gap) // (w + gap),
    eilės ilgis L - 2p; ilgesnė už eilę juosta dalijama. Abi lakšto kryptys, visi formatai, mažiausias sunaudojimas."""
    fm, _, _ = formats(material_text)
    p = float(MEDZ.data()["lakstai"].get("parastė_mm", 10))
    best = None
    for f in fm:
        L0, S0 = f["formatas_mm"]
        for (L, S) in ((L0, S0), (S0, L0)):
            rl, nr = L - 2 * p, int((S - 2 * p + GAP) // (w + GAP))
            if nr < 1 or rl <= GAP:
                continue
            pieces = []
            for x in list(lengths) * qty:                  # ilgesnė už eilę - pilnos eilės + likutis (šono sandūra bet kur)
                while x + GAP > rl + 1e-6:
                    pieces.append(rl - GAP); x -= rl - GAP
                if x > 1:
                    pieces.append(x)
            rows = []
            for x in sorted(pieces, reverse=True):
                for i, r in enumerate(rows):
                    if r + x + GAP <= rl + 1e-6:
                        rows[i] = r + x + GAP; break
                else:
                    rows.append(x + GAP)
            n_sh = math.ceil(len(rows) / nr)
            last = len(rows) - (n_sh - 1) * nr
            m2 = ((n_sh - 1) * L * S + min(S, p + last * (w + GAP)) * L) / 1e6   # paskutinis - panaudotų eilių juosta
            if best is None or m2 < best["m2"]:
                best = {"m2": m2, "sheets": n_sh, "format": (L0, S0), "supplier": f.get("tiekejas", "?"), "oversize": False}
    return best


def nest_strips(lengths_mm, width_mm, material_text, label="returns", qty=1):
    fm, _, _ = formats(material_text)
    Lmax = max((f["formatas_mm"][0] for f in fm), default=3000) - 2 * 10 - GAP
    rects = []
    for L in lengths_mm:
        n = max(1, math.ceil(L / Lmax))
        rects += [(L / n, width_mm)] * n
    r = _nest_rects(rects, material_text, sum(lengths_mm) * width_mm / 1e6, label, qty)
    q = max(1, int(qty or 1))
    f_ = _ffd_strips(lengths_mm, width_mm, material_text, q) if r.get("m2") is not None else None
    if f_ and f_["m2"] < r["m2_total"] - 1e-9:                 # eilėmis - mažesnis sunaudojimas
        pm = r["parts_m2"] * q
        r.update(sheets=f_["sheets"], format=f_["format"], supplier=f_["supplier"], m2_total=f_["m2"], m2=f_["m2"] / q,
                 waste=1 - pm / f_["m2"])
        r["text"] = ((f"nesting {label} ({q} pcs.): " if q > 1 else f"nesting {label}: ")
                     + f"{r['sheets']} x {r['format'][0]:.0f}x{r['format'][1]:.0f} ({r['supplier']}) juostos eilėmis -> "
                     f"{r['m2_total']:.2f} m²" + (f" = {r['m2']:.3f} m² / pcs." if q > 1 else "")
                     + f" (detalės {pm:.2f} m², atliekos {r['waste'] * 100:.0f} %)")
    return r
