import pymupdf as fitz
KEEP={"7-22 (8-21)","OLE P. FJÆR"}
d=fitz.open("in/otter.pdf")
for i,p in enumerate(d):
    for b in p.get_text("dict")["blocks"]:
        for l in b.get("lines",[]):
            t="".join(s["text"] for s in l["spans"]).strip(); sz=l["spans"][0]["size"]
            if not (sz>15 and t in KEEP): p.add_redact_annot(l["bbox"])
    p.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE)
    svg=p.get_svg_image(text_as_path=True)
    s=fitz.open("svg", svg.encode()); q=fitz.open("pdf", s.convert_to_pdf())
    q.save(f"t/clean_p{i+1}.pdf")
print("ok")
