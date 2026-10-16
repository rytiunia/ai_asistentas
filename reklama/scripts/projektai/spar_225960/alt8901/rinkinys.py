"""ALT8901 v316: 18 lapų (lapai.py, kiti_lapai.py, folded_vinyl bp7 / bp89, braizyti_lapa FRISK) -> VIENAS maketo PDF.
K.merge_sheets (kartu su .art.json - patikra tikrina visus lapus) -> pdf_fix_fonts (GOST Common) -> qpdf be object streams
(CorelDRAW). Šaltinių .art.json lieka (kopijos sujungiamos). python3 rinkinys.py"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", ".."))
import lapas_core as K  # noqa: E402

ORDER = ["s01_spar8000", "s02_h722big", "s03_ole", "s04_spar3500", "s05_h722small", "s06_portal", "bp7", "bp89",
         "s10_print", "s11_foil_PMS185", "s12_sandblast_foil", "s13_white_decor", "s14_print_on_sandblast",
         "s15_pant", "s16_smagodt", "s17_kaffepause", "s18_frisk"]
OUT = os.path.join(HERE, "out", "ALT8901_10.16_RS_SPAR_order_225960.pdf")
tmp = tempfile.mkdtemp()
pages = []
for k in ORDER:
    src = os.path.join(HERE, "sk", f"{k}.pdf")
    dst = os.path.join(tmp, f"{len(pages):02d}_{k}.pdf")
    shutil.copy(src, dst)
    if os.path.exists(src + ".art.json"):
        shutil.copy(src + ".art.json", dst + ".art.json")    # merge_sheets šalina šaltinio sidecar - dirbama su kopija
    pages.append(dst)
mid = os.path.join(tmp, "merged.pdf")
K.merge_sheets(pages, mid)
K.pdf_fix_fonts(mid)
subprocess.run(["qpdf", "--object-streams=disable", mid, OUT], check=True)
shutil.copy(mid + ".art.json", OUT + ".art.json")
shutil.rmtree(tmp)
import pymupdf as fitz  # noqa: E402
print("OK", OUT, "lapų", len(fitz.open(OUT)))
