import sys
import pymupdf as f
src=f.open(sys.argv[1] if len(sys.argv) > 1 else 'client.pdf');p=src[0]
D=p.get_drawings()
out=f.open();q=out.new_page(width=p.rect.width,height=p.rect.height)
sh=q.new_shape()
bg=D[52]['fill']
sh.draw_rect(f.Rect(53.9,341.5,1074.4,531.4)); sh.finish(fill=bg,color=None,width=0)
for i in [54]+list(range(55,65)):
    g=D[i]
    for it in g['items']:
        k=it[0]
        if k=='l': sh.draw_line(it[1],it[2])
        elif k=='c': sh.draw_bezier(it[1],it[2],it[3],it[4])
        elif k=='re': sh.draw_rect(it[1])
        elif k=='qu': sh.draw_quad(it[1])
    sh.finish(fill=g['fill'],color=None,width=0,even_odd=True,closePath=True)
sh.commit();out.save(sys.argv[2] if len(sys.argv) > 2 else 'frisk670_client.pdf')
