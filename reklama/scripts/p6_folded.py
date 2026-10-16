#!/usr/bin/env python3
"""v326 P6 ANT FOLDED - BENDRAS vientiso DXF generatorius (Rytis 2026-10-16: „sistema turi veikti stabiliai ir klaidos
neturi kartotis"; iki v326 ši logika buvo tik projektai/bandymas_3500_folded/folded_test.py).

Vienas DXF (P6 pagrindinė taisyklė, suvestinė „P6 - PAGRINDINĖ TAISYKLĖ"):
  - kairėje - fono išklotinė (folded_dxf.py: CUT / BEND_UP_90 / HOLES_D3.2 L tvirtinimui / HOLE_D11_CABLE briaunoje
    15 mm nuo lenkimo ir 15 mm nuo viršaus), FACE OUT;
  - ant jos - raidžių vieta (LETTER_POSITION = raidžių dugno kontūras) ir per foną einančios skylės TOSE PAČIOSE vietose
    kaip raidžių dugne (1:1): LETTER_FIX_D3.2, HOLE_D11_CABLE, DRAIN_D8;
  - dešinėje - P6 raidės (p6_dxf --folded: 1_PRIEKIS, 2_GALAS).

    python3 p6_folded.py <p6_dxf DXF (_P6_1-1_*.dxf)> <W> <H> <gylis> <raidžių X> <raidžių Y> <out.dxf> [--cable-edge left|right|none] [--t 2]
raidžių X / Y - mm nuo fono PRIEKIO kairio apatinio kampo iki p6_dxf nulio (raidžių kairė apačia).
Funkcija: combine(p6_dxf, W, H, depth, lx, ly, out, cable_edge="none", t=2) -> {"pos", "fix", "d11", "drain"}"""
import argparse
import os
import subprocess
import sys
import tempfile

import ezdxf

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kreives as KR  # noqa: E402
import patikra_dxf  # noqa: E402

LAYERS = (("CUT", 7, "CONTINUOUS"), ("BEND_UP_90", 1, "DASHED"), ("HOLES_D3.2", 3, "CONTINUOUS"),
          ("LETTER_POSITION", 6, "DASHED"), ("LETTER_FIX_D3.2", 3, "CONTINUOUS"), ("HOLE_D11_CABLE", 1, "CONTINUOUS"),
          ("DRAIN_D8", 5, "CONTINUOUS"), ("TEXT", 7, "CONTINUOUS"))


def combine(p6_dxf, W, H, depth, lx, ly, out, cable_edge="none", t=2, tb_inside=None):
    """tb_inside None - standartas (v328: trumposios kraštinės į vidų), True / False - ne standartas (nurodyta užsakyme)"""
    fl = depth - t                                           # flanšas nuo lenkimo linijos (v173)
    ox, oy = fl + lx, fl + ly                                # raidžių nulis išklotinėje
    doc = ezdxf.new("R2010", setup=True)
    doc.header["$PROJECTNAME"] = "--drain-hole"              # P6 ant folded - drenažas skylutė (patikra_dxf DRENAŽAS SKYLUTE netaiko)
    msp = doc.modelspace()
    for ly_, col, lt in LAYERS:
        if ly_ not in doc.layers:
            doc.layers.add(ly_, color=col, linetype=lt)
    tmp = tempfile.mkdtemp()
    flat_fn = os.path.join(tmp, "flat.dxf")
    cmd = ["python3", os.path.join(HERE, "folded_dxf.py"), f"{W:g}", f"{H:g}", flat_fn, f"{depth:g}"]
    if cable_edge in ("left", "right"):
        cmd.append(f"--cable-edge={cable_edge}")
    if tb_inside is not None:
        cmd.append("--tb-inside" if tb_inside else "--sides-inside")
    subprocess.run(cmd, capture_output=True, text=True, check=True)
    for e in ezdxf.readfile(flat_fn).modelspace():
        msp.add_entity(e.copy())
    p6 = ezdxf.readfile(p6_dxf)
    ents = [x for e in p6.modelspace() for x in (e.virtual_entities() if e.dxftype() == "INSERT" else [e])]
    n = {"pos": 0, "fix": 0, "d11": 0, "drain": 0}
    for e in ents:
        if e.dxf.layer != "2_GALAS":
            continue
        if e.dxftype() == "LWPOLYLINE":
            pts = [(x + ox, y + oy, b) for x, y, *_, b in e.get_points("xyseb")]
            msp.add_lwpolyline(pts, format="xyb", close=e.closed, dxfattribs={"layer": "LETTER_POSITION"}); n["pos"] += 1
        elif e.dxftype() == "CIRCLE":
            r = e.dxf.radius
            lay, k = ("LETTER_FIX_D3.2", "fix") if r < 2 else ("DRAIN_D8", "drain") if r < 4.5 else ("HOLE_D11_CABLE", "d11")
            msp.add_circle((e.dxf.center.x + ox, e.dxf.center.y + oy), r, dxfattribs={"layer": lay}); n[k] += 1
    x0 = W + 2 * fl + 300                                    # P6 raidės - dešinėje nuo išklotinės
    for e in ents:
        c = e.copy()
        c.translate(x0, 0, 0)
        msp.add_entity(c)
    msp.add_text(f"FOLDED BACKGROUND {W:g} x {H:g} x {depth:g}, Alu {t:g} mm - FLAT, FACE OUT; holes LETTER_FIX / D11 / DRAIN = letter back",
                 height=25, dxfattribs={"layer": "TEXT"}).set_placement((0, -200))
    msp.add_text("P6 LETTERS (1_PRIEKIS face, 2_GALAS back -3 mm)", height=25, dxfattribs={"layer": "TEXT"}).set_placement((x0, -200))
    KR.saveas(doc, out)
    return n


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("p6_dxf"); ap.add_argument("W", type=float); ap.add_argument("H", type=float)
    ap.add_argument("depth", type=float); ap.add_argument("lx", type=float); ap.add_argument("ly", type=float)
    ap.add_argument("out"); ap.add_argument("--cable-edge", default="none", choices=["left", "right", "none"])
    ap.add_argument("--t", type=float, default=2)
    a = ap.parse_args()
    n = combine(a.p6_dxf, a.W, a.H, a.depth, a.lx, a.ly, a.out, a.cable_edge, a.t)
    print(f"OK {a.out}: {n}, patikra: {patikra_dxf.check(a.out) or 'OK'}")
