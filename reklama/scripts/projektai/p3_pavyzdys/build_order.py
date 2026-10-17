#!/usr/bin/env python3
"""v336 P3 HALO PAVYZDYS (Rytis 2026-10-17): „pateik pavyzdį su PAVYZDYS L3400mm, tūris 60mm, spacer 30mm" - VIENAS dokumentas
P3_Pavyzdys.pdf: lapas 1 / 2 - standartinis P3 (galas plexi 8 mm, halo į sieną), lapas 2 / 2 - su REFLEKTORIAIS (+5 mm) ir galu
plexi 4 mm + PVC bortelis. Raidės - Liberation Sans Bold (tik pavyzdžiui), L 3400. Prie kiekvieno lapo 1:1 PDF ir _P3.dxf.
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
JOBS = [("spec_01.json", "P3_Pavyzdys_01"), ("spec_02.json", "P3_Pavyzdys_02")]
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
