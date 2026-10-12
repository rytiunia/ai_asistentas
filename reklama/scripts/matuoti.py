#!/usr/bin/env python3
"""Matuoja vektorinio kliento PDF elementus realiais mm.

Naudojimas:
  python3 matuoti.py failas.pdf --ref-mm 1995        # didžiausio užpildyto elemento (fono) plotis mm
  python3 matuoti.py failas.pdf --scale 3.5278       # mm vienam PDF taškui (1:10 = 3.5278)
  python3 matuoti.py failas.pdf --ref-mm 1995 --min-stroke 30

Išveda kiekvieno užpildyto elemento padėtį nuo fono kampo, matmenis ir
linijos storį (stroke). Stroke matuojamas rastru (0,5 mm/px), paklaida ~±1 mm.
Reikia: pip install pymupdf scipy numpy --break-system-packages
"""
import argparse
import sys

import numpy as np
import pymupdf as fitz
from scipy import ndimage

ap = argparse.ArgumentParser()
ap.add_argument("pdf")
ap.add_argument("--page", type=int, default=0)
g = ap.add_mutually_exclusive_group(required=True)
g.add_argument("--ref-mm", type=float, help="didžiausio užpildyto elemento plotis mm")
g.add_argument("--scale", type=float, help="mm vienam PDF taškui")
ap.add_argument("--min-stroke", type=float, default=None, help="pažymėti elementus plonesnius nei N mm")
a = ap.parse_args()

page = fitz.open(a.pdf)[a.page]
fills = [d for d in page.get_drawings() if d.get("fill") is not None]
if not fills:
    sys.exit("Nerasta užpildytų vektorinių elementų: failas gal ne vektorinis arba tekstas ne kreivėmis.")
bg = max(fills, key=lambda d: d["rect"].width * d["rect"].height)
S = a.scale if a.scale else a.ref_mm / bg["rect"].width
B = bg["rect"]
print(f"Mastelis: {S:.4f} mm/pt (~1:{S / 0.35278:.1f})")
print(f"Didžiausias elementas (fonas): {B.width * S:.0f} x {B.height * S:.0f} mm, "
      f"spalva RGB {tuple(round(c, 3) for c in bg['fill'])}")

PX = 0.5
zoom = S / PX
items = [d for d in fills if d is not bg and d["rect"].width * S > 3 and d["rect"].height * S > 3]
items.sort(key=lambda d: (round(d["rect"].y0 * S / 50), d["rect"].x0))

print("\nNr     x0    y0  plotis aukštis  stroke_med stroke_min  spalva")
def true_rect(d):
    # d["rect"] kartais neteisingas (CorelDRAW sudėtiniai keliai) - skaičiuojam iš taškų
    pts = [q for it in d["items"] for q in it[1:] if hasattr(q, "x")]
    for it in d["items"]:
        if it[0] == "re":
            pts += [it[1].tl, it[1].br]
    if not pts:
        return d["rect"]
    return fitz.Rect(min(q.x for q in pts), min(q.y for q in pts), max(q.x for q in pts), max(q.y for q in pts))


for i, d in enumerate(items):
    r = true_rect(d)
    clip = fitz.Rect(r.x0 - 1, r.y0 - 1, r.x1 + 1, r.y1 + 1)
    tmp = fitz.open()
    tp = tmp.new_page(width=page.rect.width, height=page.rect.height)
    sh = tp.new_shape()
    for it in d["items"]:
        if it[0] == "l":
            sh.draw_line(it[1], it[2])
        elif it[0] == "c":
            sh.draw_bezier(it[1], it[2], it[3], it[4])
        elif it[0] == "re":
            sh.draw_rect(it[1])
        elif it[0] == "qu":
            sh.draw_quad(it[1])
    sh.finish(fill=(0, 0, 0), color=None, even_odd=bool(d.get("even_odd", True)), closePath=True)
    sh.commit()
    pix = tp.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=clip, colorspace=fitz.csGRAY)
    m = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w) < 128
    lab, n = ndimage.label(m)
    col = tuple(round(c, 2) for c in d["fill"])
    # vienas kelias gali turėti kelias raides - matuojam kiekvieną atskirą dalį
    for k in range(1, n + 1):
        mk = lab == k
        ys, xs = np.nonzero(mk)
        if (xs.max() - xs.min()) * PX < 3 and (ys.max() - ys.min()) * PX < 3:
            continue
        dt = ndimage.distance_transform_edt(mk) * PX
        ridge = (dt == ndimage.maximum_filter(dt, size=5)) & (dt > 1)
        v = dt[ridge] * 2 if ridge.any() else np.array([dt.max() * 2])
        med, lo = float(np.median(v)), float(np.percentile(v, 10))
        flag = "  <-- PER PLONA" if a.min_stroke and lo < a.min_stroke else ""
        x0 = (r.x0 - 1 - B.x0) * S + xs.min() * PX
        y0 = (r.y0 - 1 - B.y0) * S + ys.min() * PX
        w_ = (xs.max() - xs.min() + 1) * PX
        h_ = (ys.max() - ys.min() + 1) * PX
        tag = f"{i}" if n == 1 else f"{i}.{k}"
        print(f"{tag:<5}{x0:5.0f} {y0:5.0f} {w_:7.0f} {h_:7.0f} {med:10.1f} {lo:10.1f}  {col}{flag}")
