#!/usr/bin/env python3
"""Order 33577 LEAPMOTOR (Alfa Neon AB) - VIENAS užsakymo dokumentas ALT0000_Order_33577.pdf (suvestinė D, v296):
  poz. 10 LEAP26-01002 Outdoor Logo 4500 x 585 - P6 60 mm ant skaidraus akrilo rėmo (lapai 1-2)
  poz. 20 LEAP26-06002 Indoor Logo 1730 x 225   - P6 60 mm ant skaidraus akrilo rėmo (lapai 3-4)
  poz. 30 LEAP26-02002-1 Lightbox 750 x 750 x 50 - P10_lightbox_singlesided (lapai 5-6)
Rytis 2026-10-16: „raidės P6, tūris 60mm, visa kita pagal užklausą" (PO 33577 + Leap_Motors_signs_2026-10-14.pdf).
Generatoriai: braizyti_begeliai.py, p10_lightbox_singlesided.py; lapai jungiami K.merge_sheets; 1:1 ir DXF - kiekvienai iškabai.
    python3 build_order.py   (-> patikra_lapas.py ALT0000_Order_33577.pdf = 0)"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SC = os.path.join(HERE, "..", "..")
sys.path.insert(0, SC)
import lapas_core as K  # noqa: E402

OUT = os.path.join(HERE, "ALT0000_Order_33577.pdf")
JOBS = [("braizyti_begeliai.py", "spec_LEAP26-01002.json", "ALT0000_Order_33577_LEAP26-01002"),
        ("braizyti_begeliai.py", "spec_LEAP26-06002.json", "ALT0000_Order_33577_LEAP26-06002"),
        ("p10_lightbox_singlesided.py", "spec_LEAP26-02002-1.json", "ALT0000_Order_33577_LEAP26-02002-1")]
pages = []
for gen, spec, base in JOBS:
    pdf = os.path.join(HERE, base + ".pdf")
    r = subprocess.run([sys.executable, os.path.join(SC, gen), os.path.join(HERE, spec), pdf], cwd=HERE,
                       capture_output=True, text=True)
    print("\n".join(l_ for l_ in r.stdout.splitlines() if l_.startswith(("OK", "  !", "  nesting", "  Letter"))))
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
