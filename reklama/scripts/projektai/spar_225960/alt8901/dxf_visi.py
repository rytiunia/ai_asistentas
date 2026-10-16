"""ALT8901: P6 DXF 1:1 kiekvienam šviečiančiam lapui iš patvirtinto PDF + rails_<key>.json (remas_is_lapo.py).
python3 dxf_visi.py [raktai...]  (be raktų - visi iš cfg.json, kurie turi "rail")"""
import json, os, shutil, subprocess, sys
import pymupdf as fitz
import remas_is_lapo as R
PDF = "Drawing_SPAR_order_225960_patvirtintas.pdf"; ALT = "ALT8901_10.16_RS"
CFG = json.load(open("cfg.json"))
P6 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "p6_dxf.py")
keys = sys.argv[1:] or [k for k, c in CFG.items() if c.get("rail")]
for k in keys:
    c = CFG[k]
    if not os.path.exists(f"rails_{k}.json"):
        R.main(PDF, "cfg.json", k, f"rails_{k}.json")
    fr = R.front_region(fitz.open(PDF)[c["page"]])
    import svarus_lapas as SV
    SV.main(PDF, "cfg.json", k, f"svarus_{k}.pdf")         # tik raidžių kontūrai iš patvirtinto lapo
    n = round(json.load(open(f"rails_{k}.json"))["scale"] / (25.4 / 72))
    shutil.rmtree(f"dxf_{k}", ignore_errors=True)
    cmd = ["python3", P6, f"svarus_{k}.pdf", f"dxf_{k}", "--page", "0", "--scale", str(n),
           "--crop", ",".join(f"{v:.1f}" for v in fr), "--fill", ";".join(",".join(str(x) for x in q) for q in c["fills"]),
           "--rail", str(c["rail"]), "--cable", c["cable"], "--prefix", f"{ALT}_{k}", "--no-letters",
           "--rails-json", f"rails_{k}.json"] + c.get("extra", [])
    r = subprocess.run(cmd, capture_output=True, text=True)
    open(f"log_{k}.txt", "w").write(r.stdout + r.stderr)
    ok = [l for l in r.stdout.splitlines() if l.startswith("OK") or "viso skyli" in l]
    w = [l.strip() for l in r.stdout.splitlines() if l.strip().startswith("!")]
    print(f"{k}: rc {r.returncode} | " + " | ".join(ok)[:300] + f" | perspėjimų {len(w)}")
    if r.returncode:
        print("   ", (r.stderr or r.stdout)[-600:])
