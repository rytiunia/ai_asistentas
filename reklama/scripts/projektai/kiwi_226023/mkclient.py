import pymupdf as fitz, sys
src=fitz.open("/mnt/user-data/uploads/Order_226023_ALT_Reklama_KIWI_640_BYGNES.pdf")[0]
D=src.get_drawings()
def put(pg,dr,fill):
    sh=pg.new_shape()
    for it in dr["items"]:
        if it[0]=="l": sh.draw_line(it[1],it[2])
        elif it[0]=="c": sh.draw_bezier(it[1],it[2],it[3],it[4])
        elif it[0]=="re": sh.draw_rect(it[1])
        elif it[0]=="qu": sh.draw_quad(it[1])
    sh.finish(fill=fill,color=None,even_odd=dr.get("even_odd",True),closePath=dr.get("closePath",True)); sh.commit()
def rail(pg,x0,y0,x1,y1):
    pg.draw_rect(fitz.Rect(x0,y0,x1,y1),color=None,fill=(0.5,0.5,0.5))
o=fitz.open(); pg=o.new_page(width=src.rect.width,height=src.rect.height)
for x0,x1,y0,y1 in [(260,413.2,361.4,364.2),(260,413.2,416.7,419.5),(415.2,488.1,361.4,364.2),(415.2,488.1,380.2,383.0),(415.2,479.1,398.9,401.7),(415.2,479.5,416.7,419.5)]:
    rail(pg,x0,y0,x1,y1)
for x0,x1,y0,y1 in [(285.4,409.4,508.6,511.4),(285.4,409.4,545.4,548.3),(295.7,368.9,530.3,533.1)]:
    rail(pg,x0,y0,x1,y1)

# sheet 1
KIWI_OUT=(0.85,0.1,0.1); MP=(0.22,0.2,0.21); GREEN=(0.66,0.81,0.27)
for dr in D:
    r=dr["rect"]; f=dr.get("fill")
    if f is None: continue
    f=tuple(round(v,2) for v in f)
    if f==(0.22,0.2,0.21) and abs(r.x0-251.6)<0.5 and r.width>150: put(pg,dr,KIWI_OUT)
    elif f==(0.66,0.81,0.27) and r.y0>350 and r.y1<430: put(pg,dr,GREEN)
    elif f==(0.22,0.2,0.21) and abs(r.x0-423.5)<0.5: MPD=dr
    elif f==(1.0,1.0,1.0) and dr["type"]=="fs" and fitz.Rect(421,350,492,431).contains(r) and r.width>4: put(pg,dr,MP)
put(pg,MPD,(0.35,0.35,0.05))

# sheet 2: 7-23 (copy greens/blacks in region)
for dr in D:
    r=dr["rect"]; f=dr.get("fill")
    if f is None or not fitz.Rect(260,490,440,570).contains(r): continue
    f=tuple(round(v,2) for v in f)
    if f==(0.22,0.2,0.21): put(pg,dr,(0.1,0.1,0.85))
    elif f==(0.66,0.81,0.27): put(pg,dr,GREEN)
o.save(sys.argv[1])
