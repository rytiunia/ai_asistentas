"""Kliento PDF kopija be nurodytų piešinių (pvz. stogo kojų), tekstas pašalinamas. Naudojimas:
python3 clean_client.py in.pdf out.pdf 16,17,18,...  (indeksai pagal page.get_drawings())"""
import sys, pymupdf as f
src = f.open(sys.argv[1])[0]; skip = {int(v) for v in sys.argv[3].split(",") if v}
D = src.get_drawings()
out = f.open(); q = out.new_page(width=src.rect.width, height=src.rect.height)
for i, g in enumerate(D):
    if i in skip:
        continue
    sh = q.new_shape()
    for it in g["items"]:
        k = it[0]
        if k == "l": sh.draw_line(it[1], it[2])
        elif k == "c": sh.draw_bezier(it[1], it[2], it[3], it[4])
        elif k == "re": sh.draw_rect(it[1])
        elif k == "qu": sh.draw_quad(it[1])
    sh.finish(fill=g.get("fill"), color=g.get("color"), width=g.get("width") or 0,
              even_odd=bool(g.get("even_odd", True)), closePath=bool(g.get("closePath")), fill_opacity=g.get("fill_opacity") or 1)
    sh.commit()
out.save(sys.argv[2]); print("OK", sys.argv[2], len(D) - len(skip), "piešinių")
