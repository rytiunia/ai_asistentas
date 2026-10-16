"""ALT8901 v316 (Rytis 2026-10-16: „naudoti pačią naujausią skill ir taisyklių redakciją"): gamybos DXF iš DABARTINIŲ
generatorių išvesties (ne iš patvirtinto lapo rėmo) - DXF sutampa su nauju lapu:
  1-5, 15-17  p6_dxf.py: raidės - svarus_<k>.pdf, rėmas / ausėlės / jungtys - sk/rails_bb_<k>.json (braizyti_begeliai lapas);
              17 + plokste_dxf.py (ACM apskritimas);
  7-9         folded_vinyl.py išklotinės + plėvelės (sk/bp7*, sk/bp89*) -> dxf_combine.py (vientisas DXF plokštei);
  6, 13       kiti_dxf.py (portalo buferis, dekoras); 18 - frisk_dxf.py.
Visi -> out/<ALT>_sNN_*.dxf, patikra_dxf (mm, $INSUNITS 4). python3 dxf_rinkinys.py"""
import glob
import json
import os
import shutil
import subprocess
import sys

import pymupdf as fitz

import remas_is_lapo as R

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
SCR = os.path.join(HERE, "..", "..", "..")
sys.path.insert(0, SCR)
import patikra_dxf  # noqa: E402

ALT = "ALT8901_10.16_RS"
PDF = "Drawing_SPAR_order_225960_patvirtintas.pdf"
CFG = json.load(open("cfg.json"))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)
for f in glob.glob(os.path.join(OUT, "*.dxf")):
    os.remove(f)                                              # senos versijos DXF niekada nesiunčiamas kartu su nauju


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print("  ! rc", r.returncode, (r.stderr or r.stdout)[-800:])
    return r


res = []
# --- P6 raidžių lapai
for k in [k for k, c in CFG.items() if c.get("rail")]:
    c = CFG[k]
    rj = f"sk/rails_bb_{k}.json"
    assert os.path.exists(rj), f"{rj} nėra - pirmiau lapai.py"
    n = round(json.load(open(f"rails_{k}.json"))["scale"] / (25.4 / 72))
    fr = R.front_region(fitz.open(PDF)[c["page"]])
    import svarus_lapas as SV
    SV.main(PDF, "cfg.json", k, f"svarus_{k}.pdf")             # raidžių kontūrai (v316: laužtės -> lankai)
    shutil.rmtree(f"dxf_{k}", ignore_errors=True)
    r = run(["python3", os.path.join(SCR, "p6_dxf.py"), f"svarus_{k}.pdf", f"dxf_{k}", "--page", "0", "--scale", str(n),
             "--crop", ",".join(f"{v:.1f}" for v in fr), "--fill", ";".join(",".join(str(x) for x in q) for q in c["fills"]),
             "--rail", str(c["rail"]), "--cable", c["cable"], "--prefix", f"{ALT}_{k}", "--no-letters",
             "--rails-json", rj] + c.get("extra", []))
    open(f"sk/dxf_{k}.log", "w").write(r.stdout + r.stderr)
    fs = sorted(glob.glob(f"dxf_{k}/*_1-1*.dxf"))
    assert fs, f"{k}: p6_dxf DXF nėra"
    dst = os.path.join(OUT, f"{ALT}_{k}.dxf")
    shutil.copy(fs[0], dst)
    if k == "s17_kaffepause":
        run(["python3", "plokste_dxf.py", f"svarus_{k}.pdf", f"svarus_{k}.pdf.plates.json", str(n), dst])
    ok = [l.strip() for l in r.stdout.splitlines() if "rėmas iš" in l or l.startswith("OK")]
    res.append((dst, "; ".join(ok)[:160]))
# --- back plate 7-9: folded_vinyl išvestis -> vientisas DXF
for pref, panel, sheet in (("bp7", "Back plate, box lid 40 mm, print", "s07_backplate_2700_print"),
                           ("bp89", "Back plate, box lid 40 mm, SPAR logo_1", "s08_backplate_2700_logo"),
                           ("bp89", "Back plate, box lid 40 mm, SPAR logo_2", "s09_backplate_2000_logo")):
    r = run(["python3", os.path.join(SCR, "dxf_combine.py"), "sk", pref, "--panels", panel + "|"])
    src = f"sk/{pref}_{panel}_combined.dxf"
    dst = os.path.join(OUT, f"{ALT}_{sheet}.dxf")
    shutil.copy(src, dst)
    res.append((dst, r.stdout.strip()[-160:]))
# --- 6 buferis, 13 dekoras, 18 FRISK
import kiti_dxf as KD  # noqa: E402
for fn, rep in (KD.decor(), KD.bumper()):
    res.append((fn, "; ".join(rep)))
r = run(["python3", "frisk_dxf.py"])
res.append((os.path.join(OUT, f"{ALT}_s18_frisk_sunn.dxf"), r.stdout.strip()[-160:]))
bad = 0
for fn, rep in res:
    e = patikra_dxf.check(fn)
    bad += bool(e)
    print(("OK " if not e else "! ") + os.path.basename(fn), "|", rep, "|", e or "mm")
print("DXF:", len(res), "klaidų:", bad)
