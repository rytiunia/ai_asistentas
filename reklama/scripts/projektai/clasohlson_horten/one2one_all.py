"""1:1 failai pagal Clas Ohlson proporcijų etaloną: plexi kontūras, ertmė (sienelė), Ø4, išilginės, Ø8, plokštė."""
import sys, pymupdf as fitz
sys.path.insert(0, ".")
import data as D

k = 72 / 25.4
LAY = [("1_PLEXI_OUTER", (0, 0, 0)), ("2_PLEXI_INNER_wall", (0, 0.55, 0.2)), ("3_HOLES_D4", (0.89, 0, 0.1)),
       ("4_SLOTS_6.1x3.7", (0.8, 0, 0.8)), ("5_HOLES_D8", (1, 0.5, 0)), ("6_PLATE", (0, 0.2, 0.9)), ("7_CABLE_D11", (0.89, 0, 0.1))]


def make(letters, out, x0, W, H, title):
    doc = fitz.open(); pg = doc.new_page(width=W * k, height=H * k)
    oc = {n: doc.add_ocg(n, on=True) for n, _ in LAY}
    col = dict(LAY)
    tp = lambda x, y: fitz.Point((x - x0) * k, y * k)
    def rings(geom, layer):
        sh = pg.new_shape()
        for g in getattr(geom, "geoms", [geom]):
            for r in [g.exterior] + list(g.interiors):
                pts = [tp(*q) for q in r.coords]
                sh.draw_polyline(pts)
        sh.finish(color=col[layer], width=0.1, closePath=False, oc=oc[layer]); sh.commit()
    for L in letters:
        sh = pg.new_shape()
        for sp in L["sub"]:
            cur = None
            for s in sp:
                if s[0] == "M": cur = tp(*s[1])
                elif s[0] == "L": q = tp(*s[1]); sh.draw_line(cur, q); cur = q
                else: q = tp(*s[3]); sh.draw_bezier(cur, tp(*s[1]), tp(*s[2]), q); cur = q
            sh.draw_line(cur, tp(*sp[0][1]))
        sh.finish(color=col["1_PLEXI_OUTER"], width=0.1, closePath=False, oc=oc["1_PLEXI_OUTER"]); sh.commit()
        rings(L["inner"], "2_PLEXI_INNER_wall")
        for f in L["feats"]:
            c = tp(*f["c"]); sh = pg.new_shape()
            if f["type"] == "SLOT":
                w, h = 6.1 * k, 3.7 * k; r = h / 2
                sh.draw_rect(fitz.Rect(c.x - w / 2, c.y - h / 2, c.x + w / 2, c.y + h / 2), radius=(0.5 * h / w, 0.5))
                lay = "4_SLOTS_6.1x3.7"
            else:
                d = 4.0 if f["type"] == "D4" else 8.0
                sh.draw_circle(c, d / 2 * k); lay = "3_HOLES_D4" if d == 4 else "5_HOLES_D8"
            sh.finish(color=col[lay], width=0.1, oc=oc[lay]); sh.commit()
    d11 = D.d11_point(min(letters, key=lambda L: L["bb"][0]))
    sh = pg.new_shape(); sh.draw_circle(tp(*d11), 5.5 * k); sh.finish(color=col["7_CABLE_D11"], width=0.1, oc=oc["7_CABLE_D11"]); sh.commit()
    sh = pg.new_shape(); sh.draw_rect(fitz.Rect(0, 0, W * k, H * k)); sh.finish(color=col["6_PLATE"], width=0.1, oc=oc["6_PLATE"]); sh.commit()
    doc.set_metadata({"title": title}); doc.save(out, garbage=3, deflate=True)


P4 = D.LOGO_PART
make(D.LETTERS, sys.argv[1], P4["x0"], P4["len"], D.PH, f"Clas Ohlson Horten 3 - P{P4['no']} 1:1")
src = open("sheet3.py").read().split("begin(15)")[0]
g = {"__name__": "x"}; exec(src, g)
make(g["LET"], sys.argv[2], 0, g["PW"], g["PH"], "Clas Ohlson Horten 1 - 1:1")
print("ok")
