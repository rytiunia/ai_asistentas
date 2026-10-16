"""ALT8901: LED dėliojimas (led_km.py, Kaisen) kiekvienam šviečiančiam lapui iš švaraus lapo (svarus_<k>.pdf),
gylis - iš patvirtinto lapo; visi lapai -> out/ALT8901_10.16_RS_SPAR_order_225960_LED.pdf"""
import json, os, subprocess
import pymupdf as fitz
import remas_is_lapo as R
HERE = os.path.dirname(os.path.abspath(__file__))
LK = os.path.join(HERE, "..", "..", "..", "led_km.py")
CFG = json.load(open("cfg.json"))
JOBS = [("s01_spar8000", 80, "SPAR 8000 + logo"), ("s02_h722big", 80, "7-22 (8-21) 5264"), ("s03_ole", 80, "OLE P. FJÆR"),
        ("s04_spar3500", 80, "SPAR 3500 + logo"), ("s05_h722small", 80, "7-22 (8-21) 3040"), ("s15_pant", 80, "EUROSPAR PANT"),
        ("s16_smagodt", 50, "SMÅGODT"), ("s17_kaffepause", 50, "KAFFEPAUSE"), ("s18_frisk", 70, "FRISK & SUNN")]
pages = []
for k, depth, nm in JOBS:
    c = CFG[k]
    n = round(json.load(open(f"rails_{k}.json"))["scale"] / (25.4 / 72)) if os.path.exists(f"rails_{k}.json") else 20
    pg = fitz.open(f"svarus_{k}.pdf")[0]
    L = None
    for d in pg.get_drawings():
        L = d["rect"] if L is None else L | d["rect"]
    lit = [q for q in c["fills"] if not (k == "s18_frisk" and q != [0.98, 1, 1])]   # FRISK: P1 apskritimas ir fonas nešviečia
    spec = {"pdf": f"svarus_{k}.pdf", "page": 0, "crop_pt": [L.x0 - 2, L.y0 - 2, L.x1 + 2, L.y1 + 2],
            "scale_mm_per_pt": n * 25.4 / 72, "depth": depth, "qty": 1,
            "title": f"ALT8901_10.16_RS SPAR order 225960_{CFG[k]['page'] + 1}_LED {nm}",
            "groups": [{"fill_rgb": q, "led": "white", "name": nm} for q in lit][:1] if len(lit) == 1 else
                      [{"fill_rgb": q, "led": "white", "name": f"{nm} {i + 1}"} for i, q in enumerate(lit)]}
    json.dump(spec, open(f"led_{k}.json", "w"), indent=1)
    out = f"led_{k}.pdf"
    r = subprocess.run(["python3", LK, f"led_{k}.json", out], capture_output=True, text=True)
    line = [l.strip() for l in r.stdout.splitlines() if "vnt." in l]
    print(f"{k}: rc {r.returncode} | " + " || ".join(line)[:400])
    if r.returncode:
        print(r.stderr[-500:])
    else:
        pages.append(out)
doc = fitz.open()
for p in pages:
    doc.insert_pdf(fitz.open(p))
os.makedirs("out", exist_ok=True)
doc.save("out/ALT8901_10.16_RS_SPAR_order_225960_LED.pdf")
print("OK LED lapų", len(pages))
