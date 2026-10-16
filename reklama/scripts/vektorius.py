#!/usr/bin/env python3
"""Rastrinio logotipo (PNG / JPG) vektorizavimas lapams (v140, Rytis 2026-10-12: šviesdėžė su logotipu iš PNG).

potrace (pure Python `potracer`) -> Bezier kreivės -> uždari daugiakampiai mm; užpildas even-odd (skylės - akys ir pan.).
  rings(path, width_mm, threshold=128) -> [ [(x, y), ...], ... ]  (x dešinėn, y žemyn, (0, 0) - gabarito kairys viršus)
  size(rings) -> (w, h)
  draw_rl(c, rings, ox, oy_top, s, H, color) - reportlab: piešia lape (y žemyn nuo oy_top), mastelis s (pt / mm)
Pastaba: tai kliento pateiktas failas; gamybai (pjovimui) - geriau originalus vektorinis failas iš kliento.
"""
import math

import numpy as np
from PIL import Image


def _bez(p0, p1, p2, p3, n=10):
    out = []
    for k in range(1, n + 1):
        t = k / n
        a = (1 - t) ** 3; b = 3 * (1 - t) ** 2 * t; c = 3 * (1 - t) * t ** 2; d = t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def rings(path, width_mm, threshold=128, turdsize=4):
    import potrace
    im = Image.open(path).convert("RGBA")
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
    g = np.array(Image.alpha_composite(bg, im).convert("L"))
    bm = potrace.Bitmap(g < threshold)
    plist = bm.trace(turdsize=turdsize, alphamax=1.0, opticurve=True, opttolerance=0.2)
    rs = []
    for curve in plist:
        pts = [(curve.start_point.x, curve.start_point.y)]
        cur = pts[0]
        for seg in curve.segments:
            if seg.is_corner:
                pts += [(seg.c.x, seg.c.y), (seg.end_point.x, seg.end_point.y)]
            else:
                pts += _bez(cur, (seg.c1.x, seg.c1.y), (seg.c2.x, seg.c2.y), (seg.end_point.x, seg.end_point.y))
            cur = (seg.end_point.x, seg.end_point.y)
        rs.append(pts)
    Hh, Ww = g.shape
    def full(r):                                     # paveikslėlio rėmelis / fonas - ne logotipas
        xs_ = [p[0] for p in r]; ys_ = [p[1] for p in r]
        return (max(xs_) - min(xs_)) > 0.97 * Ww and (max(ys_) - min(ys_)) > 0.97 * Hh
    rs = [r for r in rs if not full(r)]
    xs = [p[0] for r in rs for p in r]; ys = [p[1] for r in rs for p in r]
    x0, y0, x1 = min(xs), min(ys), max(xs)
    k = width_mm / (x1 - x0)
    return [[((x - x0) * k, (y - y0) * k) for x, y in r] for r in rs]


def size(rs):
    xs = [p[0] for r in rs for p in r]; ys = [p[1] for r in rs for p in r]
    return max(xs) - min(xs), max(ys) - min(ys)


_SUBS = {}


def draw_rl(c, rs, ox, oy_top, s, Hpage, color, xform=None):
    """reportlab: logotipas lape; xform(x_mm, y_mm) -> (x_pt, y_pt_top_down) (pvz. 3D projekcijai)"""
    from reportlab.pdfgen.canvas import FILL_EVEN_ODD
    c.saveState()
    c.setFillColor(color); c.setStrokeColor(color); c.setLineWidth(0.1)
    import kreives as _KR
    tf = lambda x, y: (lambda XY: (XY[0], Hpage - XY[1]))(xform(x, y) if xform else (ox + x * s, oy_top + y * s))
    p = c.beginPath()
    for r in rs:
        # v326 (patikra 23 KAMPUOTA KREIVĖ, suvestinė E3b): kontūras lankais (kubinės Bezier), ne trumpų tiesių laužtė
        key = (id(rs), id(r), len(r))
        sub = _SUBS.get(key)
        if sub is None:
            sub = _SUBS[key] = _KR.ring_to_sub(r, True) or [("M", r[0])] + [("L", q) for q in r[1:]]
        for s_ in sub:
            if s_[0] == "M":
                p.moveTo(*tf(*s_[1]))
            elif s_[0] == "L":
                p.lineTo(*tf(*s_[1]))
            else:
                a, b, d = tf(*s_[1]), tf(*s_[2]), tf(*s_[3]); p.curveTo(a[0], a[1], b[0], b[1], d[0], d[1])
        p.close()
    c.drawPath(p, stroke=0, fill=1, fillMode=FILL_EVEN_ODD)
    c.restoreState()
