#!/usr/bin/env python3
"""PO 3311 BN Skilte - Kvickly Skibhusvej: logotipas iš KELIŲ DALIŲ (Rytis 2026-10-16: „padaryti raides kaip pridėtame
pavyzdyje ALT7782_11.17_Indkøbsordre 2261 Fra BN Skilte, iš kelių dalių").

Kliento fasado PDF logotipas - VIENAS sulietas kontūras (visos raidės susijungusios) + i taškas + 2 skylės. Kaip pavyzdyje
(„Sign from 3 pieces"): K | vick | ly (+ i taškas - atskiras elementas):
  - K: K viršutinės šakos dešinysis kraštas (670,72)->(538,248) tęsiasi per v kairės šakos viršų iki K apatinės kojos
    vidinio kampo (422,402) - visi taškai vienoje tiesėje, todėl K = pilna K forma, o v gauna K šakos kraštą;
  - k | l: k šakos baigiasi ties l stiebo kairiu kraštu (x = 2444 A mastelyje) - vertikalus pjūvis, trikampė skylė
    tarp k šakų ir l tampa atvira;
  - i taškas - kliento atskiras kontūras.
Rezultatas: `Kvickly_pieces_<poz>.pdf` - dalys kaip atskiri užpildyti kontūrai (kreivės - lankai / Bezier, kreives.py),
1 pt = 1 mm * 72 / 25,4 (spec "scale": 1.0), braizyti_begeliai jas ima kaip atskiras raides.
    python3 pieces.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SC = os.path.join(HERE, "..", "..")
sys.path.insert(0, SC)
import pymupdf as fitz  # noqa: E402
from shapely.geometry import Polygon, box  # noqa: E402
from shapely.ops import unary_union  # noqa: E402
from shapely import affinity  # noqa: E402
import lapas_core as K  # noqa: E402
import kreives as KR  # noqa: E402

SRC = os.path.join(HERE, "Kvickly_Skibhusvej_3_9_Facade.pdf")
# pozicijos: (BN brėžinio žymė, logotipo kelio rect pt fasado PDF, tikslus plotis mm iš PO)
POZ = {"01_KV-1137": ((89.2, 146.4, 214.7, 180.1), 3322.0),
       "02_KV-1136": ((427.9, 136.1, 562.4, 172.2), 2373.0)}
MMPT = 72 / 25.4


def logo_drawing(rect):
    pg = fitz.open(SRC)[0]
    for d in pg.get_drawings():
        r = d["rect"]
        if d.get("fill") and min(d["fill"]) > 0.95 and abs(r.x0 - rect[0]) < 1 and abs(r.y0 - rect[1]) < 1:
            return d
    raise SystemExit(f"logotipo kelias {rect} nerastas")


def pieces(rect, width_mm):
    d = logo_drawing(rect)
    x0, y0, x1, _ = d["rect"]
    k = width_mm / (x1 - x0)
    subs = K.drawing_to_subpaths(d, lambda q: ((q[0] - x0) * k, (q[1] - y0) * k))
    polys = [Polygon(KR.flat_sub(sp)).buffer(0) for sp in subs]
    outer = max(polys, key=lambda p: p.area)
    rest = [p for p in polys if p is not outer]
    holes = [p for p in rest if outer.contains(p.representative_point())]
    dots = [p for p in rest if not outer.contains(p.representative_point())]
    body = outer.difference(unary_union(holes)) if holes else outer
    # tiesių viršūnės (tikslios, ne apvalintos) - pagal A mastelio vardines koordinates
    V = [s_[1] if s_[0] in ("M", "L") else s_[3] for s_ in subs[[i for i, p in enumerate(polys) if p is outer][0]]]
    f = width_mm / 3322.0

    def v(x, y):
        return min(V, key=lambda q: (q[0] - x * f) ** 2 + (q[1] - y * f) ** 2)
    polyK = Polygon([v(0, 72), v(210, 72), v(210, 372), v(426, 72), v(670, 72), v(422, 402), v(666, 773), v(413, 773),
                     v(210, 463), v(210, 773), v(0, 773)])
    pK = body.intersection(polyK).buffer(0)
    xl = v(2444, 48)[0]                                   # l stiebo kairysis kraštas
    other = body.difference(polyK).buffer(0)
    pvick = other.intersection(box(-1e4, -1e4, xl, 1e4)).buffer(0)
    ply = other.intersection(box(xl, -1e4, 1e4, 1e4)).buffer(0)
    out = [("K", pK), ("vick", pvick), ("ly", ply)] + [("i dot", p) for p in dots]
    # patikra: dalys = visas logotipas, nesikerta
    tot = unary_union([p for _, p in out])
    full = unary_union([body] + dots)
    assert abs(tot.area - full.area) < 1.0, (tot.area, full.area)
    for i in range(len(out)):
        for j in range(i + 1, len(out)):
            assert out[i][1].intersection(out[j][1]).area < 1.0, (out[i][0], out[j][0])
    return out


def write_pdf(parts, path):
    xs = [p.bounds for _, p in parts]
    W_ = max(b[2] for b in xs) - min(b[0] for b in xs)
    H_ = max(b[3] for b in xs) - min(b[1] for b in xs)
    mx, my = min(b[0] for b in xs), min(b[1] for b in xs)
    doc = fitz.open()
    pg = doc.new_page(width=(W_ + 40) * MMPT, height=(H_ + 40) * MMPT)
    P = lambda q: fitz.Point((q[0] - mx + 20) * MMPT, (q[1] - my + 20) * MMPT)
    for _, p in parts:
        sh = pg.new_shape()
        K.fitz_subs(sh, K.geom_subs(p), P)
        sh.finish(color=None, fill=(1, 1, 1), even_odd=True, closePath=True)
        sh.commit()
    doc.save(path, garbage=4, deflate=True)
    # iškarpa - 15 mm aplink dalis (lankų Bezier valdymo taškai išeina už kontūro - kitaip i taškas atmetamas)
    return [5 * MMPT, 5 * MMPT, (W_ + 35) * MMPT, (H_ + 35) * MMPT], (W_, H_)


if __name__ == "__main__":
    for poz, (rect, w) in POZ.items():
        parts = pieces(rect, w)
        crop, (W_, H_) = write_pdf(parts, os.path.join(HERE, f"Kvickly_pieces_{poz}.pdf"))
        print(poz, f"{W_:.1f} x {H_:.1f} mm", "crop_pt", [round(c, 2) for c in crop],
              "; ".join(f"{n} {p.bounds[2] - p.bounds[0]:.0f}x{p.bounds[3] - p.bounds[1]:.0f}" for n, p in parts))
