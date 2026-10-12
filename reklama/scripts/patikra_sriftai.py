"""v18: šrifto dydžių patikra - python3 patikra_sriftai.py lapas.pdf; spausdina tekstus < 8 pt (be antraštės langelių pavadinimų)."""
import pymupdf as f, sys, collections
d=f.open(sys.argv[1])
CAP={"CLIENT","TITLE","ORDER NO.","FILE / DRAWING NO.","SCALE (DIM. mm)","FORMAT","SHEET","REV.","PROJECTION","DRAWN","CHECKED","DATE"}
for i,p in enumerate(d):
    bad=collections.Counter(); ex={}
    for b in p.get_text("dict")["blocks"]:
        for l in b.get("lines",[]):
            for s in l["spans"]:
                t=s["text"].strip()
                if not t or t in CAP: continue
                if s["size"]<7.95:
                    zone="band" if s["bbox"][1]>p.rect.height*0.70 else "view"
                    k=(zone,round(s["size"],1)); bad[k]+=1; ex.setdefault(k,[]).append(t[:28])
    print(f"p{i+1}", dict(bad), {k:v[:4] for k,v in ex.items()})
