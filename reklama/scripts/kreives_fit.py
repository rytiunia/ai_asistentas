#!/usr/bin/env python3
"""v312: esamo DXF kreivės lankais (laužtės -> tiesės + lankai, nuokrypis <= 0,02 mm), mm antraštė.
    python3 scripts/kreives_fit.py failas.dxf [...]   (perrašo vietoje)"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kreives as KR  # noqa: E402

for f in sys.argv[1:]:
    import ezdxf
    doc = ezdxf.readfile(f)
    n, a, b = KR.fit_dxf_doc(doc)
    KR.saveas(doc, f)
    print(f"{f}: {n} kontūr., mazgų {a} -> {b}")
