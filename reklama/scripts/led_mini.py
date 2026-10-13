#!/usr/bin/env python3
"""v176 (Rytis 2026-10-13: „pataisyk LED atvaizdavimą profesionaliau su LED miniatiūromis") - LED dėliojimo lapas mūsų CAD
stiliumi iš originalo LED brėžinio: originalas NEĮDEDAMAS paveikslu, o PERBRAIŽOMAS - raidžių kontūrai, rėmas, skylės - hairline
(kaip originale, ta pati geometrija), moduliai - MINIATIŪROS (korpusas + LED / lęšiai, pasukti pagal originalo kryptį),
aprėpties apskritimai - šviesūs hairline, PSU - pilkas stačiakampis, laidas - raudonas, išvestis - taškas.
Moduliai, kiekiai, laidai, PSU vietos - TIK iš originalo (padėtys ir kryptys nekeičiamos).

`redraw(K, src, pno, clip, X0, Ytop, k, rules)` - rules: [{"match": f(d) -> bool, "as": "outline"|"rail"|"cover"|"module"|
"psu"|"cable"|"exit"|"skip", ...}] - pirmoji tinkanti taisyklė; "module" parametrai: kind ("bar" brūkšnys su kryptimi |
"dot" taškas / lęšis), L_pt, W_pt (miniatiūros dydis originalo pt), n (LED skaičius), led (spalva hex), lens (bool).
Grąžina {"modules": [(x, y, ang, rule)], ...} - legendai ir kiekio patikrai.
"""
import math

import pymupdf as fitz
from reportlab.lib.colors import HexColor, white, black

COVER = HexColor("#9ED79E")
BODY_EDGE = HexColor("#3A3A3A")
PSU_FILL = HexColor("#E6E6E6")


def _pts(d):
    out = []
    for it in d["items"]:
        if it[0] == "l":
            out += [it[1], it[2]]
        elif it[0] == "c":
            out += [it[1], it[4]]
        elif it[0] == "re":
            r = it[1]; out += [r.tl, r.tr, r.br, r.bl]
        elif it[0] == "qu":
            q = it[1]; out += [q.ul, q.ur, q.lr, q.ll]
    return out


def _axis(d):
    """brūkšnio (modulio) centras, ilgoji ašis (rad), ilgis, plotis - iš taškų (PCA)"""
    ps = _pts(d)
    cx = sum(p.x for p in ps) / len(ps); cy = sum(p.y for p in ps) / len(ps)
    sxx = sum((p.x - cx) ** 2 for p in ps); syy = sum((p.y - cy) ** 2 for p in ps); sxy = sum((p.x - cx) * (p.y - cy) for p in ps)
    ang = 0.5 * math.atan2(2 * sxy, sxx - syy)
    ca, sa = math.cos(ang), math.sin(ang)
    u = [(p.x - cx) * ca + (p.y - cy) * sa for p in ps]; v = [-(p.x - cx) * sa + (p.y - cy) * ca for p in ps]
    return cx, cy, ang, max(u) - min(u), max(v) - min(v)


def _path(K, d, T, close=None):
    p = K.c.beginPath()
    cur = None
    for it in d["items"]:
        if it[0] == "re":
            r = it[1]
            pts = [T(r.x0, r.y0), T(r.x1, r.y0), T(r.x1, r.y1), T(r.x0, r.y1)]
            p.moveTo(*pts[0]); [p.lineTo(*q) for q in pts[1:]]; p.close(); cur = None
            continue
        if it[0] == "qu":
            q = it[1]
            pts = [T(q.ul.x, q.ul.y), T(q.ur.x, q.ur.y), T(q.lr.x, q.lr.y), T(q.ll.x, q.ll.y)]
            p.moveTo(*pts[0]); [p.lineTo(*q_) for q_ in pts[1:]]; p.close(); cur = None
            continue
        a = it[1]
        if cur is None or abs(cur.x - a.x) > 1e-3 or abs(cur.y - a.y) > 1e-3:
            p.moveTo(*T(a.x, a.y))
        if it[0] == "l":
            p.lineTo(*T(it[2].x, it[2].y)); cur = it[2]
        elif it[0] == "c":
            p.curveTo(*T(it[2].x, it[2].y), *T(it[3].x, it[3].y), *T(it[4].x, it[4].y)); cur = it[4]
    if close if close is not None else d.get("closePath"):
        p.close()
    return p


def module(K, x, y, ang, L, Wd, n=3, led="#00A651", lens=False):
    """LED modulio miniatiūra (lapo koord., reportlab y aukštyn): korpusas su suapvalintais kampais, n LED / lęšis"""
    c = K.c
    c.saveState(); c.translate(x, y); c.rotate(ang)
    c.setLineWidth(K.HAIR); c.setStrokeColor(BODY_EDGE); c.setFillColor(white)
    c.roundRect(-L / 2, -Wd / 2, L, Wd, min(Wd * 0.35, 1.2), stroke=1, fill=1)
    col = HexColor(led)
    if lens:
        r_ = Wd * 0.42
        c.setFillColor(white); c.circle(0, 0, r_, stroke=1, fill=1)
        c.setFillColor(col); c.circle(0, 0, r_ * 0.45, stroke=0, fill=1)
    else:
        for i in range(n):
            lx = -L / 2 + L * (i + 0.5) / n
            c.setFillColor(col); c.circle(lx, 0, Wd * 0.28, stroke=1 if led.upper() in ("#FFFFFF", "#FFF") else 0, fill=1)
    c.setStrokeColor(BODY_EDGE)                              # laido išvadai (galai)
    c.line(-L / 2 - Wd * 0.35, 0, -L / 2, 0); c.line(L / 2, 0, L / 2 + Wd * 0.35, 0)
    c.restoreState()


def redraw(K, src, pno, clip, X0, Ytop, k, rules, outline_col=black):
    pg = fitz.open(src)[pno]
    C = fitz.Rect(clip)
    T = lambda x, y: (X0 + (x - clip[0]) * k, K.H - (Ytop + (y - clip[1]) * k))
    res = {"modules": [], "psu": [], "exits": []}
    later = {"cover": [], "outline": [], "rail": [], "psu": [], "cable": [], "module": [], "exit": []}
    for d in pg.get_drawings():
        if not C.contains(d["rect"]):
            continue
        for ru in rules:
            if ru["match"](d):
                if ru["as"] != "skip":
                    later[ru["as"]].append((d, ru))
                break
    c = K.c
    for d, ru in later["cover"]:                             # aprėpties apskritimai - fone
        c.saveState(); c.setLineWidth(K.HAIR); c.setStrokeColor(COVER)
        c.drawPath(_path(K, d, T, True), stroke=1, fill=0); c.restoreState()
    for kind in ("rail", "outline"):
        for d, ru in later[kind]:
            c.saveState(); c.setLineWidth(K.HAIR); c.setStrokeColor(HexColor(ru.get("col", "#000000")))
            if ru.get("fill"):
                c.setFillColor(HexColor(ru["fill"]))
            c.drawPath(_path(K, d, T), stroke=1, fill=1 if ru.get("fill") else 0, fillMode=1); c.restoreState()
    for d, ru in later["psu"]:
        r = d["rect"]
        (x0, y1), (x1, y0) = T(r.x0, r.y0), T(r.x1, r.y1)
        c.saveState(); c.setLineWidth(K.HAIR); c.setStrokeColor(BODY_EDGE); c.setFillColor(PSU_FILL)
        cx_, cy_, ang_, L_, W_ = _axis(d)
        c.translate(*T(cx_, cy_)); c.rotate(-math.degrees(ang_))
        c.rect(-L_ * k / 2, -W_ * k / 2, L_ * k, W_ * k, stroke=1, fill=1)
        c.restoreState()
        res["psu"].append((r.x0, r.y0, r.x1, r.y1))
    for d, ru in later["cable"]:
        c.saveState(); c.setLineWidth(ru.get("lw", 0.5)); c.setStrokeColor(K.CABLE)
        c.drawPath(_path(K, d, T, False), stroke=1, fill=0); c.restoreState()
    mods = []
    for d, ru in later["module"]:
        cx_, cy_, ang_, L_, W_ = _axis(d)
        mods.append([cx_, cy_, ang_, ru, L_])
    for m in mods:                                           # taškiniams (lęšiai) - kryptis pagal artimiausią kaimyną
        if m[3].get("kind") == "dot":
            nb = sorted((math.dist(m[:2], q[:2]), q) for q in mods if q is not m and q[3] is m[3])
            if nb:
                q = nb[0][1]; m[2] = math.atan2(q[1] - m[1], q[0] - m[0])
    for cx_, cy_, ang_, ru, L_ in mods:
        X, Y = T(cx_, cy_)
        module(K, X, Y, -math.degrees(ang_), ru["L_pt"] * k, ru["W_pt"] * k, ru.get("n", 3), ru.get("led", "#00A651"),
               ru.get("lens", False))
        res["modules"].append((cx_, cy_, ang_, ru.get("name", "")))
    for d, ru in later["exit"]:
        r = d["rect"]
        X, Y = T((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2)
        c.saveState(); c.setFillColor(K.CABLE); c.circle(X, Y, 1.4, stroke=0, fill=1); c.restoreState()
        res["exits"].append((X, Y))
    return res


def legend_icon(K, x, y, ru, k=1.0, scale=2.2):
    """miniatiūra legendai (lapo koord. y žemyn)"""
    module(K, x, K.H - y, 0, ru["L_pt"] * k * scale, ru["W_pt"] * k * scale, ru.get("n", 3), ru.get("led", "#00A651"),
           ru.get("lens", False))
