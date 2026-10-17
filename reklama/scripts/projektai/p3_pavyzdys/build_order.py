#!/usr/bin/env python3
"""v339 P3+reflector ETALONAS (Rytis 2026-10-17: „sheet 2 - P3 profilio etalonas"; standartas P3 - be reflektorių, su jais -
užklausoje „P3+reflector"): PAVYZDYS L 3400, gylis 60, distanceriai 30 (Ø16), galas plexi 4 + PVC (raidės >= 400 mm),
reflektoriai ACM 3 (+5 mm), rėmas U 30x30x2 (statmenys tik galuose). Raidės - Liberation Sans Bold (tik pavyzdžiui).
Prie lapo - 1:1 PDF ir _P3.dxf.
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
TMP = os.path.join(HERE, "P3_Pavyzdys_lapas.pdf")
r = subprocess.run([sys.executable, os.path.join(SC, "braizyti_begeliai.py"), os.path.join(HERE, "spec.json"), TMP], cwd=HERE,
                   capture_output=True, text=True)
print("\n".join(l_ for l_ in r.stdout.splitlines() if l_.startswith(("OK", "  !", "  P3"))))
if r.returncode:
    sys.exit(r.stderr[-2000:])
K.merge_sheets([TMP], OUT)
K.pdf_fix_fonts(OUT)
os.remove(TMP)
for x_ in (TMP + ".auto.json", TMP + ".art.json"):
    os.path.exists(x_) and os.remove(x_)
for a_, b_ in (("P3_Pavyzdys_lapas_1-1.pdf", "P3_Pavyzdys_1-1.pdf"), ("P3_Pavyzdys_lapas_P3.dxf", "P3_Pavyzdys_P3.dxf")):
    os.replace(os.path.join(HERE, a_), os.path.join(HERE, b_))
print("OK", OUT)
