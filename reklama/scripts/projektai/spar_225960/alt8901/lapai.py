"""ALT8901 v316 (Rytis 2026-10-16: „blankas naudojamas senas ... visi pataisymai daromi jau pagal dabartines taisykles,
naudoti pačią naujausią skill ir taisyklių redakciją"): raidžių lapai 1-5, 15-17 PERGENERUOJAMI dabartiniu
braizyti_begeliai.py. Duomenys: senas spec (`../spec/<old>.json` - BOM, MAIN DATA, grupės, laidų logika) + PATVIRTINTAS lapas
(raidės, kliento rėmas, ausėlės, mastelis). Seno spec pt koordinatės (senas kliento failas) NENAUDOJAMOS.
python3 lapai.py [raktai...] -> sk/<k>.json, sk/<k>.pdf, rails_<k>.json (DXF moduliui)"""
import copy
import json
import os
import subprocess
import sys

import pymupdf as fitz

import remas_is_lapo as R
import svarus_lapas as SV

HERE = os.path.dirname(os.path.abspath(__file__))
PDF = os.path.join(HERE, "Drawing_SPAR_order_225960_patvirtintas.pdf")
BB = os.path.join(HERE, "..", "..", "..", "braizyti_begeliai.py")
ALT, DATE = "ALT8901_10.16_RS", "2026-10-16"
CFG = json.load(open(os.path.join(HERE, "cfg.json")))
OLD = {"s01_spar8000": "spar8000", "s02_h722big": "h722big", "s03_ole": "ole", "s04_spar3500": "spar3500",
       "s05_h722small": "h722small", "s15_pant": "pant", "s16_smagodt": "smagodt", "s17_kaffepause": "kaffepause"}


def ears_pt(k, c):
    """patvirtintos ausėlės (FRONT VIEW) -> {"top": [x pt], "bottom": [x pt]} pagal artimiausią bėgelį"""
    rj = json.load(open(os.path.join(HERE, f"rails_{k}.json")))
    S = rj["scale"]; H = [r for r in rj["rails"] if r["kind"] == "h"]
    if not rj["ears"] or not H:
        return None
    ymid = (min(r["y0"] for r in H) + max(r["y1"] for r in H)) / 2
    out = {"top": [], "bottom": []}
    for e in rj["ears"]:
        out["top" if e["hy"] < ymid else "bottom"].append(round(e["hx"] / S, 2))
    return {k_: sorted(set(v)) for k_, v in out.items()}


def build(k):
    c = CFG[k]
    old = json.load(open(os.path.join(HERE, "..", "spec", OLD[k] + ".json")))
    if not os.path.exists(os.path.join(HERE, f"rails_{k}.json")):
        R.main(PDF, os.path.join(HERE, "cfg.json"), k, os.path.join(HERE, f"rails_{k}.json"))
    rj = json.load(open(os.path.join(HERE, f"rails_{k}.json")))
    N = round(rj["scale"] / (25.4 / 72))
    src = fitz.open(PDF)[c["page"]]
    FR = R.front_region(src)
    # švarus lapas: raidės (perdažytos senų grupių spalvomis) + patvirtinti bėgeliai
    c2 = copy.deepcopy(c)
    c2.update(c.get("sk", {}))                                # lapui: pilna grafika (logotipas, plėvelės), ne DXF kontūrai
    c2["keep_fills"] = [c["rail_fill"]]
    c2["min_pt"] = 20 / (N * 25.4 / 72)                       # < 20 mm - ausėlių skylės, ne raidės (kaip p6_dxf v103)
    tmpcfg = os.path.join(HERE, "sk", f"cfg_{k}.json")
    json.dump({k: c2}, open(tmpcfg, "w"))
    SV.main(PDF, tmpcfg, k, os.path.join(HERE, "sk", f"client_{k}.pdf"))
    s = copy.deepcopy(old)
    s.update({"client_pdf": os.path.join(HERE, "sk", f"client_{k}.pdf"), "page": 0, "scale": N,
              "crop_pt": [round(v, 1) for v in FR], "order_no": ALT, "date": DATE,
              "rail_fills": [c["rail_fill"]], "client_frame": True,
              "rails_json": os.path.join(HERE, "sk", f"rails_bb_{k}.json"), "export_1to1": True})
    s.pop("cable_exits", None)                                # senos kliento pt koordinatės
    ep = ears_pt(k, c)
    cl = fitz.open(os.path.join(HERE, "sk", f"client_{k}.pdf"))[0].get_drawings()
    S = rj["scale"]
    for g in s["groups"]:
        g.pop("ears_pt", None)
        if g.get("lit", True) is not False:
            g.setdefault("led", "White LED")                  # v111: kiekvienai šviečiančiai grupei
        if g.get("rails"):
            # senas spec - Ryčio nurodytas rėmas grupei: patvirtinto lapo bėgeliai, kertantys grupės x, mm nuo grupės raidžių kampo
            gd = [d["rect"] for d in cl if d["fill"] is not None and SV.near(d["fill"], g["client_fill"], 0.05)]
            gx0, gy0, gx1 = min(r.x0 for r in gd), min(r.y0 for r in gd), max(r.x1 for r in gd)
            nr = []
            for q in rj["rails"]:
                if q["kind"] != "h" or q["x1"] / S < gx0 or q["x0"] / S > gx1:
                    continue
                x0, x1 = q["x0"] - gx0 * S, q["x1"] - gx0 * S
                y0, y1 = q["y0"] - gy0 * S, q["y1"] - gy0 * S
                nr.append({"kind": "h", "poly": [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]})
            g["rails"] = nr
        if ep and not g.get("no_rails") and g.get("lit", True) is not False:
            g["ears_pt"] = ep
    for row in s.get("main_data", []):                        # v316 patikra 16: dabartinis cell_units ilgesnis („30 x 30 x 2 mm")
        if row[0] in ("Frame", "Rails"):
            row[1] = row[1].replace(" + ears,", ", ears,").replace(" + ears ", ", ears, ").replace("□ ", "□")
        if row[0] == "Overall size" and any(r_[0] == "Parts" for r_ in s["main_data"]):
            row[1] = row[1].split(" (parts")[0]               # dalys - eilutėje „Parts" (nekartojama)
    s.update(c.get("sk", {}).get("spec_over", {}))
    for g in s["groups"]:
        g.update(c.get("sk", {}).get("group_over", {}).get(g["name"], {}))
    for gi, go in c.get("group_over", {}).items():
        s["groups"][int(gi)].update(go)
    fn = os.path.join(HERE, "sk", f"{k}.json")
    json.dump(s, open(fn, "w"), indent=1, ensure_ascii=False)
    if os.path.exists(os.path.join(HERE, "sk", f"{k}.pdf")):
        os.remove(os.path.join(HERE, "sk", f"{k}.pdf"))          # sena versija niekada nepatikrinama vietoj naujos
    r = subprocess.run(["python3", BB, fn, os.path.join(HERE, "sk", f"{k}.pdf")], capture_output=True, text=True, cwd=HERE)
    open(os.path.join(HERE, "sk", f"{k}.log"), "w").write(r.stdout + r.stderr)
    oks = [l for l in r.stdout.splitlines() if l.startswith("OK")]
    warn = [l.strip() for l in r.stdout.splitlines() if l.strip().startswith("!")]
    print(f"{k}: rc {r.returncode} | " + " | ".join(oks)[:220] + f" | perspėjimų {len(warn)}")
    for w in warn[:12]:
        print("     ", w[:200])
    if r.returncode:
        print((r.stderr or r.stdout)[-1500:])


if __name__ == "__main__":
    os.makedirs(os.path.join(HERE, "sk"), exist_ok=True)
    for k in (sys.argv[1:] or list(OLD)):
        build(k)
