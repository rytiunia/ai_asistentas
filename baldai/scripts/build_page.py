"""model.json + assets/template.html -> index.html (3D perziura, projekcija, pjovimo lapas).

    python scripts/build_page.py <dir>/model.json [--out <dir>/index.html] [--template assets/template.html]

index.html publikuojamas kaip artifact (Artifact tool) - klientas atsidaro telefone.
three.js kraunamas is cdnjs; jei nepasikrauna, puslapis vis tiek rodo projekcija ir lenteles.
"""
import argparse
import json
from pathlib import Path

here = Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser()
ap.add_argument("model")
ap.add_argument("--out")
ap.add_argument("--template", default=str(here / "assets" / "template.html"))
a = ap.parse_args()

model_path = Path(a.model)
model = json.loads(model_path.read_text(encoding="utf-8"))
tpl = Path(a.template).read_text(encoding="utf-8")
assert "__MODEL_JSON__" in tpl, "šablone nėra __MODEL_JSON__ žymės"
title = model["projektas"].get("pavadinimas", "Virtuvė")
html = tpl.replace("<title>Virtuvės siena A</title>", f"<title>{title}</title>")
html = html.replace("<h1>Virtuvės siena A</h1>", f"<h1>{title}</h1>")
html = html.replace("__MODEL_JSON__", json.dumps(model, ensure_ascii=False))
out = Path(a.out) if a.out else model_path.with_name("index.html")
out.write_text(html, encoding="utf-8")
print(f"saved {out} ({len(html) // 1024} KB)")
