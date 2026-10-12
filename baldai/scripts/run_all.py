"""Visa grandine vienu paleidimu: projektas.json -> model.json + detales.xlsx + index.html.

    python scripts/run_all.py <projektas.json> --out <dir> [--std <standartas.json>] [--dekorai <dekorai.json>]

Po to: Artifact(index.html) klientui, SendUserFile(detales.xlsx) gamintojui.
Excel formuliu reiksmes perskaiciuoja xlsx skill'o recalc.py (jei yra) - kvieciama automatiskai.
"""
import argparse
import subprocess
import sys
from pathlib import Path

here = Path(__file__).resolve().parent
root = here.parent
ap = argparse.ArgumentParser()
ap.add_argument("projektas")
ap.add_argument("--out", required=True)
ap.add_argument("--std", default=str(root / "assets" / "standartas.json"))
ap.add_argument("--dekorai", default=str(root / "assets" / "dekorai.json"))
a = ap.parse_args()
out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
py = sys.executable

def run(*cmd):
    print("$", " ".join(str(c) for c in cmd))
    subprocess.run([str(c) for c in cmd], check=True)

run(py, here / "engine.py", a.projektas, "--std", a.std, "--dekorai", a.dekorai, "--out", out)
run(py, here / "export_xlsx.py", out / "model.json")
run(py, here / "build_page.py", out / "model.json")
recalc = Path("/mnt/skills/public/xlsx/scripts/recalc.py")
if recalc.exists():
    run(py, recalc, out / "detales.xlsx", "60")
else:
    print("recalc.py nerastas – Excel formulės persiskaičiuos atidarius failą")
print("\nIšvestis:", *(str(out / f) for f in ("model.json", "detales.xlsx", "index.html")), sep="\n  ")
