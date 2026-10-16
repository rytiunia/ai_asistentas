"""ALT8901 (SPAR 225960): patvirtinto Corel PDF ORDER NO. keitimas - visas kitas turinys baitas į baitą nekeičiamas.
Senas tekstas pašalinamas redakcija (tik teksto sritis, grafika nepaliečiama), naujas rašomas GOST Common tuo pačiu dydžiu ir baze.
python3 order_no.py in.pdf out.pdf ALT8901_10.16_RS"""
import sys, os
import pymupdf as fitz
src, dst, new = sys.argv[1:4]
OLD = "ALT0000_00.00_RS"
GOST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "..", "assets", "gost_common.ttf")
d = fitz.open(src); n = 0
for p in d:
    hits = []
    for b in p.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            for s in l["spans"]:
                if s["text"].strip() == OLD:
                    hits.append(s)
    for s in hits:
        p.add_redact_annot(fitz.Rect(s["bbox"]))
    if hits:
        p.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE,
                           text=fitz.PDF_REDACT_TEXT_REMOVE)
    for s in hits:
        p.insert_text(fitz.Point(s["origin"]), new, fontsize=s["size"], fontname="GOSTCommon", fontfile=GOST,
                      color=fitz.sRGB_to_pdf(s["color"]), fill=fitz.sRGB_to_pdf(s["color"]),
                      render_mode=2, border_width=0.045)              # paryškinta kaip originale (užpildas + kontūras)
        n += 1
d.save(dst, garbage=3, deflate=True)
print(f"OK {dst}: {n} ORDER NO. pakeista, puslapių {len(d)}")
