#!/usr/bin/env python3
"""v340 P3 / P3+reflector dokumentas (Rytis 2026-10-17: „paruošk dokumentą su P3 ir P3+reflector"): PAVYZDYS L 3400, gylis 60,
distanceriai 30 (Ø16), galas plexi 4 + PVC (raidės >= 400 mm), rėmas U 30x30x2 (statmenys pagal ilgį: 3277 mm - 3).
Lapas 1 / 2 - P3 (standartas, be reflektorių), lapas 2 / 2 - P3+reflector (etalonas v339, reflektoriai ACM 3, +5 mm).
Raidės - Liberation Sans Bold (tik pavyzdžiui). Prie kiekvieno lapo - 1:1 PDF ir _P3.dxf.
    python3 ../welcome_p1_test/make_client.py PAVYZDYS Pavyzdys_client.pdf LEN 3400 /usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf
    python3 build_order.py   (-> patikra_lapas.py P3_Pavyzdys.pdf = 0)"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SC = os.path.join(HERE, "..", "..")
sys.path.insert(0, SC)
import lapas_core as K  # noqa: E402

OUT = os.path.join(HERE, "P3_Pavyzdys.pdf")
JOBS = [("spec_P3.json", "P3_Pavyzdys_P3"), ("spec_P3_reflector.json", "P3_Pavyzdys_P3_reflector")]
pages = []
for spec, base in JOBS:
    pdf = os.path.join(HERE, base + ".pdf")
    r = subprocess.run([sys.executable, os.path.join(SC, "braizyti_begeliai.py"), os.path.join(HERE, spec), pdf], cwd=HERE,
                       capture_output=True, text=True)
    print("\n".join(l_ for l_ in r.stdout.splitlines() if l_.startswith(("OK", "  !", "  P3"))))
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
