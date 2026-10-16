#!/usr/bin/env python3
"""Order 33580 (OMODA OMJE26-01001 + EXLANTIX EXLA26-01001) - VIENAS dokumentas ALT0000_Order_33580.pdf (suvestinė D, v296):
  lapas 1 / 2 - OMJE26-01001, lapas 2 / 2 - EXLA26-01001 (spec "sheet"); 1:1 PDF - kiekvienai iškabai.
    python3 build_order.py   (-> patikra_lapas.py ALT0000_Order_33580.pdf = 0)"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SC = os.path.join(HERE, "..", "..")
sys.path.insert(0, SC)
import lapas_core as K  # noqa: E402

OUT = os.path.join(HERE, "ALT0000_Order_33580.pdf")
JOBS = [("spec_OMJE26-01001.json", "ALT0000_Order_33580_OMJE26-01001"),
        ("spec_EXLA26-01001.json", "ALT0000_Order_33580_EXLA26-01001")]
pages = []
for spec, base in JOBS:
    pdf = os.path.join(HERE, base + ".pdf")
    r = subprocess.run([sys.executable, os.path.join(SC, "braizyti_begeliai.py"), os.path.join(HERE, spec), pdf], cwd=HERE,
                       capture_output=True, text=True)
    print("\n".join(l_ for l_ in r.stdout.splitlines() if l_.startswith(("OK", "  !"))))
    if r.returncode:
        sys.exit(r.stderr[-2000:])
    pages.append(pdf)
K.merge_sheets(pages, OUT)
K.pdf_fix_fonts(OUT)
for p_ in pages:
    os.remove(p_)
    for x_ in (p_ + ".auto.json", p_ + ".art.json"):
        os.path.exists(x_) and os.remove(x_)
print("OK", OUT)
