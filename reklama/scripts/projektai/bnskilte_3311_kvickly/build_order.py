#!/usr/bin/env python3
"""PO 3311 BN Skilte - Kvickly Skibhusvej (KV-1137 + KV-1136) - VIENAS dokumentas ALT0000_PO_3311_Kvickly.pdf (suvestinė D, v296):
  lapas 1 / 2 - KV-1137 (3322 x 892, gylis 70), lapas 2 / 2 - KV-1136 (2373 x 637, gylis 60); pirma pieces.py (spec "sheet"); 1:1 PDF - kiekvienai iškabai.
    python3 build_order.py   (-> patikra_lapas.py ALT0000_PO_3311_Kvickly.pdf = 0)"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SC = os.path.join(HERE, "..", "..")
sys.path.insert(0, SC)
import lapas_core as K  # noqa: E402

OUT = os.path.join(HERE, "ALT0000_PO_3311_Kvickly.pdf")
JOBS = [("spec_01_KV-1137.json", "ALT0000_PO_3311_Kvickly_KV-1137"),
        ("spec_02_KV-1136.json", "ALT0000_PO_3311_Kvickly_KV-1136")]
subprocess.run([sys.executable, os.path.join(HERE, "pieces.py")], check=True)   # logotipas -> dalys
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
