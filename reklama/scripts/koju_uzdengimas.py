"""KOJŲ UŽDENGIMAS - bendra visiems generatoriams („Bendrinės taisyklės" 19; Rytis 2026-10-14, v212-v217).

Galioja VISOSE situacijose, kur yra kojų uždengimas (sviesdeze inset, P10_lightbox_doublesided B, ...):
- 2 dalys A + B (veidrodinės), Alu 2 mm, korpuso spalva, lankstinys pagal folded v173 (atlankas = gylis - t);
- ilgis = kojų tarpas (korpusas - plokštė) - 5 mm (po 2.5 iš abiejų galų);
- plotis = kojos profilis (skersai) + 10 (□30 -> 40 = 20 + 20);
- viršuje 2 x Ø3.2 prisukimui, 7 mm nuo atlanko krašto;
- priekyje ir gale standumo briaunos 10 mm; TIES KOJOMIS briaunose IŠPJOVOS (briaunos remtųsi į kojas);
- atlankai remiasi į kojas -> aukštis = kojų matmuo + 2t.
"""
from shapely.geometry import Polygon, box as sbox
from shapely.ops import unary_union

RIB = 10.0
HOLE_EDGE = 7.0
HOLE_D = 3.2


def make(legs_y, leg_h, leg_w, leg_len, thk=2.0, gap=5.0, w=None, rib=RIB, clear=1.0, holes_top=2):
    """legs_y - kojų ašys (y, dėžės koord.), leg_h - kojos profilis y kryptimi, leg_w - skersai (z),
    leg_len - kojų tarpas (korpusas - plokštė). Grąžina dict (y0 / y1 - dėžės koord.)."""
    w = w or (leg_w + 10.0)
    ya, yb = min(legs_y) - leg_h / 2, max(legs_y) + leg_h / 2
    return dict(y0=ya - thk, y1=yb + thk, w=w, thk=thk, gap=gap, L=leg_len - gap, rib=rib, holes_top=holes_top,
                notch_d=max(0.0, leg_w / 2 + clear - (w / 2 - rib)),
                notches=[(y_ - leg_h / 2 - clear, y_ + leg_h / 2 + clear) for y_ in legs_y])


def size_txt(C):
    return f"{C['L']:g} x {C['y1'] - C['y0']:g} x {C['w'] / 2:g}"


def bom_desc(C):
    return f"Leg cover A + B, 2 x Ø{HOLE_D:g} top (DXF)", f"Alu {C['thk']:g}, ribs {C['rib']:g} notched"


def write_flat(msp, C, ox, txt=None):
    """1 dalies išklotinė (B - veidrodinė) nuo ox; grąžina užimtą plotį."""
    tc = C["thk"]; Lc = C["L"]; Hc = C["y1"] - C["y0"]
    fl = C["w"] / 2 - tc; rb = C["rib"] - tc
    cx0, cy0 = ox + rb, fl
    flat = Polygon([(cx0, 0), (cx0 + Lc, 0), (cx0 + Lc, cy0 + tc), (cx0 + Lc + rb, cy0 + tc), (cx0 + Lc + rb, cy0 + Hc - tc),
                    (cx0 + Lc, cy0 + Hc - tc), (cx0 + Lc, cy0 + Hc + fl), (cx0, cy0 + Hc + fl), (cx0, cy0 + Hc - tc),
                    (cx0 - rb, cy0 + Hc - tc), (cx0 - rb, cy0 + tc), (cx0, cy0 + tc)])
    nd = C["notch_d"]
    if nd > 0:                                                      # briaunų išpjovos ties kojomis
        cuts = []
        for ya, yb in C["notches"]:
            fa, fb = cy0 + (C["y1"] - yb), cy0 + (C["y1"] - ya)    # DXF y aukštyn
            cuts.append(sbox(cx0 - rb - 1, fa, cx0 - rb + nd, fb))
            cuts.append(sbox(cx0 + Lc + rb - nd, fa, cx0 + Lc + rb + 1, fb))
        flat = flat.difference(unary_union(cuts))
    for pg in getattr(flat, "geoms", [flat]):
        msp.add_lwpolyline([(round(x, 3), round(y, 3)) for x, y in pg.exterior.coords], close=True, dxfattribs={"layer": "CUT"})
    msp.add_lwpolyline([(cx0, cy0), (cx0 + Lc, cy0), (cx0 + Lc, cy0 + Hc), (cx0, cy0 + Hc)], close=True,
                       dxfattribs={"layer": "BEND_UP_90"})
    n = C["holes_top"]
    for k in range(n):
        msp.add_circle((cx0 + Lc * (k + 1) / (n + 1), cy0 + Hc + fl - HOLE_EDGE), HOLE_D / 2, dxfattribs={"layer": "HOLES_D3.2"})
    label = (f"LEG COVER {Lc:g}x{Hc:g}x{C['w'] / 2:g} Alu {tc:g} - x 2 (A + B mirror) - flanges {fl:g}, ribs {rb:g} "
             f"(notched {nd:g} at legs), {n} x D{HOLE_D:g} top")
    if txt:
        txt(label, ox, -30)
    else:
        msp.add_text(label, dxfattribs={"layer": "TEXT", "height": 8}).set_placement((ox, -30))
    return Lc + 2 * rb
