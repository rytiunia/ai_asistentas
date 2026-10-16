"""ALT8901 (SPAR 225960): ne raidžių gaminių gamybos DXF iš PATVIRTINTO lapo - tik tai, kas lape nurodyta.
- back plate (lapai 7-9): folded Alu 2 mm, bortas 40, dalys pagal lapą (1400 + 700); išklotinė v173 (lenkimo linijos = W x h,
  atlankai gylis - t), v302: VIRŠUS / APAČIA Į VIDŲ (atlankai W - 2t, šonai per visą aukštį); Ø3,2 - 50 + n x žingsnis, 7 mm nuo
  atlanko krašto (viršutinės dalies viršus, apatinės apačia - į L 30x30x2); sandūroje Ø6 - TOSE PAČIOSE vietose (lapas:
  „joint: N bolts through folded edges, same positions"), 20 mm nuo krašto;
- plėvelės (8-9 logotipas, 13 dekoras): kontūrai iš lapo vektorių, mastelis pagal lape nurodytą plotį, sluoksnis pagal spalvą;
- portalas (6): nerūdijančio buferio išklotinė (lapo FLAT PATTERN, mastelis pagal 505).
Visi DXF - mm ($INSUNITS 4), patikra_dxf.py.
python3 kiti_dxf.py"""
import json
import os
import sys

import ezdxf
import pymupdf as fitz
from ezdxf import path as EP

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", ".."))
import patikra_dxf
import kreives as KR  # noqa: E402  v316: kreivės lankais  # noqa: E402

PDF = os.path.join(HERE, "Drawing_SPAR_order_225960_patvirtintas.pdf")
ALT = "ALT8901_10.16_RS"
OUT = os.path.join(HERE, "out")
D = fitz.open(PDF)


def new_doc(layers):
    doc = ezdxf.new("R2010", setup=True)
    doc.units = ezdxf.units.MM; doc.header["$INSUNITS"] = 4; doc.header["$MEASUREMENT"] = 1
    for nm, col, lt in layers:
        if nm not in doc.layers:
            doc.layers.add(nm, color=col, linetype=lt)
    return doc


# ------------------------------------------------------------------ back plate išklotinė
def flat(msp, ox, oy, W, h, depth, t, top, bot, xs, name):
    """top / bot: 'screw' (Ø3,2, 7 nuo krašto) | 'joint' (Ø6, 20 nuo krašto) | None. xs - skylių x nuo plokštės kairės."""
    FL = depth - t
    F, WF = W + 2 * FL, h + 2 * FL
    x0, x1, y0, y1 = FL, FL + W, FL, FL + h
    pts = [(x0 + t, 0), (x1 - t, 0), (x1 - t, y0), (F, y0), (F, y1), (x1 - t, y1), (x1 - t, WF), (x0 + t, WF),
           (x0 + t, y1), (0, y1), (0, y0), (x0 + t, y0)]            # v302: viršus / apačia į vidų
    P = lambda q: (ox + q[0], oy + q[1])
    msp.add_lwpolyline([P(q) for q in pts], close=True, dxfattribs={"layer": "CUT"})
    msp.add_lwpolyline([P(q) for q in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))], close=True,
                       dxfattribs={"layer": "BEND_UP_90"})
    for kind, yy in ((top, WF), (bot, 0)):
        if not kind:
            continue
        e, r, lay = (7, 1.6, "HOLES_D3.2") if kind == "screw" else (20, 3.0, "HOLES_D6_JOINT")
        y = yy - e if yy else e
        for x in xs:
            msp.add_circle(P((x0 + x, y)), r, dxfattribs={"layer": lay})
    msp.add_text(f"{name}: FOLDED {W:g} x {h:g} x {depth:g} - Al {t:g} - FLAT {F:.0f} x {WF:.0f} - FACE OUT", height=30,
                 dxfattribs={"layer": "TEXT"}).set_placement(P((0, -50)))
    msp.add_text(f"TOP / BOTTOM INSIDE: top/bottom flanges {W - 2 * t:g}, sides {h:g}, flanges {FL:g} from bend line, 4 x 90 up",
                 height=18, dxfattribs={"layer": "TEXT"}).set_placement(P((0, -90)))
    return F, WF


# ------------------------------------------------------------------ vektoriai iš lapo -> DXF (mm)
def vec_paths(page, rect, pred):
    """lapo užpildyti / kontūriniai keliai srityje -> (fill, [ezdxf Path]) pt koordinatėmis"""
    out = []
    for d in page.get_drawings():
        if not rect.contains(d["rect"]) or not pred(d):
            continue
        ps, cur, prev = [], None, None
        for it in d["items"]:
            if it[0] == "re":
                r = it[1]; p = EP.Path((r.x0, r.y0))
                for q in ((r.x1, r.y0), (r.x1, r.y1), (r.x0, r.y1)):
                    p.line_to(q)
                p.close(); ps.append(p); cur = None; continue
            a = it[1]
            if cur is None or prev is None or abs(a.x - prev.x) + abs(a.y - prev.y) > 0.01:
                if cur is not None:
                    ps.append(cur)
                cur = EP.Path((a.x, a.y))
            if it[0] == "l":
                cur.line_to((it[2].x, it[2].y)); prev = it[2]
            elif it[0] == "c":
                cur.curve4_to((it[4].x, it[4].y), (it[2].x, it[2].y), (it[3].x, it[3].y)); prev = it[4]
        if cur is not None:
            ps.append(cur)
        out.append((d.get("fill"), d.get("color"), ps))
    return out


def put_vec(msp, items, S, ox, oy, layer_of, ref):
    """pt -> mm: x = (x - ref.x0) * S + ox, y = (ref.y1 - y) * S + oy"""
    n = 0
    for fill, col, ps in items:
        lay = layer_of(fill, col)
        if not lay:
            continue
        for p in ps:
            pts = [((q.x - ref.x0) * S + ox, (ref.y1 - q.y) * S + oy) for q in p.flattening(0.05 / S)]
            if len(pts) > 2:
                # v316 (v313 „kreivės lankais"): lapo laužtės -> lankai šaltinio tikslumu (0,01 pt lape)
                msp.add_lwpolyline(KR.fit(pts, True, max(KR.TOL, 0.01 * S)), format="xyb", close=True,
                                   dxfattribs={"layer": lay}); n += 1
    return n


def bbox_of(items):
    xs, ys = [], []
    for _, _, ps in items:
        for p in ps:
            for q in p.flattening(0.01):
                xs.append(q.x); ys.append(q.y)
    return fitz.Rect(min(xs), min(ys), max(xs), max(ys))


def near(c, q, t=0.03):
    return c is not None and max(abs(a - b) for a, b in zip(c[:3], q)) <= t


LAY = [("CUT", 7, "CONTINUOUS"), ("BEND_UP_90", 1, "DASHED"), ("HOLES_D3.2", 3, "CONTINUOUS"),
       ("HOLES_D6_JOINT", 4, "CONTINUOUS"), ("TEXT", 2, "CONTINUOUS")]


def backplate(key, page, W, parts, n_holes, logo=None):
    span = W - 100
    xs = [50 + span * k / (n_holes - 1) for k in range(n_holes)]
    lays = LAY + ([("VINYL_WHITE_ORACAL_551_010", 7, "CONTINUOUS"), ("VINYL_GREEN_ORACAL_8500_614", 3, "CONTINUOUS")] if logo else [])
    doc = new_doc(lays); msp = doc.modelspace()
    y = 0; xmax = 0
    for j, h in enumerate(parts):
        top = "screw" if j == 0 else "joint"
        bot = "screw" if j == len(parts) - 1 else "joint"
        F, WF = flat(msp, 0, y - (h + 76), W, h, 40, 2, top, bot, xs, f"PART {j + 1} - {W:g} x {h:g}")
        y -= WF + 250; xmax = max(xmax, F)
    rep = [f"išklotinės {len(parts)}: " + ", ".join(f"{W + 76:g} x {h + 76:g}" for h in parts), f"Ø3,2 / Ø6 po {n_holes}"]
    if logo:
        p = D[page]
        R = fitz.Rect(*logo["rect"])
        items = vec_paths(p, R, lambda d: d.get("fill") is not None and (near(d["fill"], (1, 1, 1)) or near(d["fill"], logo["green"])))
        ref = bbox_of(items); S = logo["w_mm"] / ref.width
        lay = lambda f, c: "VINYL_GREEN_ORACAL_8500_614" if near(f, logo["green"]) else "VINYL_WHITE_ORACAL_551_010"
        n = put_vec(msp, items, S, xmax + 400, 0, lay, ref)
        rep.append(f"logotipas {ref.width * S:.0f} x {ref.height * S:.1f} mm, kontūrų {n}")
    fn = os.path.join(OUT, f"{ALT}_{key}.dxf"); KR.saveas(doc, fn)
    return fn, rep


def decor():
    p = D[12]
    items = vec_paths(p, fitz.Rect(150, 150, 900, 450), lambda d: d.get("fill") is not None and near(d["fill"], (1, 1, 1))
                      and d.get("color") is not None)
    ref = bbox_of(items); S = 769 / ref.width
    doc = new_doc([("VINYL_WHITE_ORACAL_551_101", 7, "CONTINUOUS"), ("TEXT", 2, "CONTINUOUS")]); msp = doc.modelspace()
    n = put_vec(msp, items, S, 0, 0, lambda f, c: "VINYL_WHITE_ORACAL_551_101", ref)
    msp.add_text("WHITE DECOR SPAR LOGO - ORACAL 551 101 gloss - 7 pcs.", height=12,
                 dxfattribs={"layer": "TEXT"}).set_placement((0, -30))
    fn = os.path.join(OUT, f"{ALT}_s13_decor.dxf"); KR.saveas(doc, fn)
    return fn, [f"dekoras {ref.width * S:.0f} x {ref.height * S:.1f} mm, kontūrų {n}, 7 pcs."]


def bumper():
    p = D[5]
    t = p.search_for("FLAT PATTERN")[0]
    R = fitz.Rect(t.x0 - 120, t.y0 - 120, t.x1 + 200, t.y0 - 1)
    items = vec_paths(p, R, lambda d: d.get("color") is not None and d.get("fill") is not None)
    bends = vec_paths(p, R, lambda d: d.get("fill") is None and d.get("dashes") not in (None, "[] 0"))
    ref = bbox_of(items); S = 505 / ref.width
    doc = new_doc([("CUT", 7, "CONTINUOUS"), ("BEND_90", 1, "DASHDOT"), ("TEXT", 2, "CONTINUOUS")]); msp = doc.modelspace()
    n = put_vec(msp, items, S, 0, 0, lambda f, c: "CUT", ref)
    nb = 0
    for _, _, ps in bends:
        for pth in ps:
            pts = [((q.x - ref.x0) * S, (ref.y1 - q.y) * S) for q in pth.flattening(0.05 / S)]
            if len(pts) >= 2:
                msp.add_lwpolyline(pts, dxfattribs={"layer": "BEND_90"}); nb += 1
    msp.add_text("STAINLESS STEEL BUMPER 1 mm - 505 x 160, bent 304 x 102 - 2 pcs.", height=12,
                 dxfattribs={"layer": "TEXT"}).set_placement((0, -30))
    fn = os.path.join(OUT, f"{ALT}_s06_portal_bumper.dxf"); KR.saveas(doc, fn)
    return fn, [f"buferis {ref.width * S:.0f} x {ref.height * S:.1f} mm, kontūrų {n}, lenkimo linijų {nb}, 2 pcs."]


if __name__ == "__main__":
    LOGO8 = {"rect": [262, 166, 455, 201], "green": (0.0, 0.53, 0.29), "w_mm": 1000}
    LOGO9 = {"rect": [196, 155, 389, 190], "green": (0.0, 0.53, 0.29), "w_mm": 1000}
    res = [backplate("s07_backplate_2700_print", 6, 2700, [1400, 700], 10),
           backplate("s08_backplate_2700_logo", 7, 2700, [1400, 700], 10, LOGO8),
           backplate("s09_backplate_2000_logo", 8, 2000, [1400, 700], 7, LOGO9),
           decor(), bumper()]
    for fn, rep in res:
        e = patikra_dxf.check(fn)
        print(f"OK {os.path.basename(fn)}: " + "; ".join(rep) + ("" if not e else f"  ! {e}"))
