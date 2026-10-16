"""ALT8901: švarus „kliento" PDF p6_dxf.py moduliui iš PATVIRTINTO lapo FRONT VIEW - tik raidžių / logotipų kontūrai,
perkelti iš lapo be pakeitimų (tie patys segmentai ir koordinatės, tas pats puslapio dydis -> rails JSON tinka).
- cfg "fills": raidžių spalvos; "solid": spalvos, kurių kontūrui imamas tik IŠORINIS subkontūras (P6 logotipo dugnas -
  apskritimas; medis / buteliai - plėvelė, ne skylės dugne);
- cfg "exclude_pt": stačiakampiai pt, kurių objektai praleidžiami (FRAME JOINT ženklas, matmenų žymekliai);
- "plates": spalvos, kurios eksportuojamos atskirai (pvz. KAFFEPAUSE kompozito apskritimas) -> <out>.plates.json (pt).
python3 svarus_lapas.py <lapas.pdf> <cfg.json> <raktas> <out.pdf>"""
import json
import sys

import pymupdf as fitz

import remas_is_lapo as R


def subpaths(items):
    out, cur, prev = [], [], None
    for it in items:
        if it[0] == "re":
            if cur:
                out.append(cur); cur = []
            out.append([it]); prev = None; continue
        if it[0] == "qu":
            if cur:
                out.append(cur); cur = []
            out.append([it]); prev = None; continue
        a = it[1]
        if prev is not None and abs(a.x - prev.x) + abs(a.y - prev.y) > 0.01 and cur:
            out.append(cur); cur = []
        cur.append(it)
        prev = it[2] if it[0] == "l" else it[4]
    if cur:
        out.append(cur)
    return out


def bbox(sp):
    xs, ys = [], []
    for it in sp:
        qs = [it[1].tl, it[1].br] if it[0] == "re" else [it[1].rect.tl, it[1].rect.br] if it[0] == "qu" else it[1:]
        for q in qs:
            xs.append(q.x); ys.append(q.y)
    return fitz.Rect(min(xs), min(ys), max(xs), max(ys))


ARC_TOL_PT = 0.01     # v316 (v313 „kreivės lankais"): patvirtinto lapo laužtės (sena shapely geometrija) -> lankai, pt


def draw(shape, sps):
    import os as _os
    sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "..", ".."))
    import kreives as KR
    for sp in sps:
        if len(sp) >= 5 and all(it[0] == "l" for it in sp):
            pts = [(sp[0][1].x, sp[0][1].y)] + [(it[2].x, it[2].y) for it in sp]
            closed = abs(pts[0][0] - pts[-1][0]) + abs(pts[0][1] - pts[-1][1]) < 0.01
            sub = KR.ring_to_sub(pts, closed, ARC_TOL_PT)
            cur = None
            for s_ in sub:
                if s_[0] == "M":
                    cur = fitz.Point(*s_[1])
                elif s_[0] == "L":
                    shape.draw_line(cur, fitz.Point(*s_[1])); cur = fitz.Point(*s_[1])
                else:
                    shape.draw_bezier(cur, fitz.Point(*s_[1]), fitz.Point(*s_[2]), fitz.Point(*s_[3])); cur = fitz.Point(*s_[3])
            continue
        for it in sp:
            if it[0] == "l":
                shape.draw_line(it[1], it[2])
            elif it[0] == "c":
                shape.draw_bezier(it[1], it[2], it[3], it[4])
            elif it[0] == "re":
                shape.draw_rect(it[1])
            elif it[0] == "qu":
                shape.draw_quad(it[1])


def near(c, q, t=0.02):
    return c is not None and max(abs(a - b) for a, b in zip(c[:3], q)) <= t


def main(pdf, cfg, key, out):
    C = json.load(open(cfg))[key]
    src = fitz.open(pdf)[C["page"]]
    FR = R.front_region(src)
    EX = [fitz.Rect(*r) for r in C.get("exclude_pt", [])]
    doc = fitz.open(); pg = doc.new_page(width=src.rect.width, height=src.rect.height)
    n, plates = 0, []
    for d in src.get_drawings():
        r = d["rect"]
        if d["fill"] is None or not FR.contains(r) or any(e.contains(r) for e in EX):
            continue
        if max(r.width, r.height) < C.get("min_pt", 0):              # v316: ausėlių skylės / žymekliai (< 20 mm) - ne raidės
            continue
        if any(near(d["fill"], q) for q in C.get("plates", [])):
            sps = subpaths(d["items"]); outer = max(sps, key=lambda s: bbox(s).get_area())
            plates.append({"fill": list(d["fill"][:3]), "items": [[it[0]] + [[p.x, p.y] for p in it[1:]] if it[0] in "lc" else
                                                                 [it[0], [it[1].x0, it[1].y0, it[1].x1, it[1].y1]] for it in outer]})
            continue
        if any(near(d["fill"], q, 0.012) for q in C.get("keep_fills", [])):          # v316: patvirtinti bėgeliai - kaip yra
            sh = pg.new_shape(); draw(sh, subpaths(d["items"]))
            sh.finish(fill=d["fill"][:3], color=None, even_odd=True, closePath=False); sh.commit(); n += 1
            continue
        if not any(near(d["fill"], q) for q in C["fills"]):
            continue
        sps = subpaths(d["items"])
        fill = d["fill"][:3]
        for src_, dec_ in C.get("decal_from", []):                    # v316: P6 logotipas = vientisas kontūras + plėvelė (decal)
            if near(d["fill"], src_):
                sh = pg.new_shape(); draw(sh, [max(sps, key=lambda s_: bbox(s_).get_area())])
                sh.finish(fill=fill, color=None, even_odd=True, closePath=False); sh.commit(); n += 1
                fill = dec_                                            # pilnas kelias (su iškirpimais) - decal spalva
        for x0, x1, col in C.get("recolor", []):                     # v316: grupė pagal x (pt) -> senų spec client_fill
            if x0 <= (r.x0 + r.x1) / 2 <= x1:
                fill = col
        for src_, col in C.get("recolor_fill", []):                   # v316: plėvelė (decal) -> senų spec decal client_fill
            if near(d["fill"], src_):
                fill = col
        if any(near(d["fill"], q) for q in C.get("solid", [])):
            sps = [max(sps, key=lambda s: bbox(s).get_area())]
        sh = pg.new_shape(); draw(sh, sps)
        sh.finish(fill=fill, color=None, even_odd=True, closePath=False); sh.commit(); n += 1
    doc.save(out)
    if plates:
        json.dump(plates, open(out + ".plates.json", "w"))
    print(f"OK {key}: {n} objektų -> {out}" + (f", plokštės {len(plates)}" if plates else ""))


if __name__ == "__main__":
    main(*sys.argv[1:5])
