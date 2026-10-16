"""v320 P6 PAGRINDINĖS TAISYKLĖS regresija (Rytis 2026-10-16: „išsaugok kaip pagrindinę taisyklę P6").
Paleisti po KIEKVIENO p6_dxf / braizyti_begeliai / braizyti_lapa / folded_dxf pakeitimo:  python3 scripts/test_p6.py
Tikrina testus projektai/bandymas_3500 (P6 ant U 30x30x2) ir projektai/bandymas_3500_folded (P6 ant folded):
  - D3.2 kvadrato / trikampio principu: B a n d m a s - po 4, y - 3 (viso 31);
  - drenažas: ant rėmo - puslankiai dugno kontūre (0 Ø8 apskritimų), ant folded - Ø8 skylutės (ir fone);
  - patikra_dxf = 0. Exit 1 - jei kas nors nesutampa."""
import collections
import glob
import os
import re
import shutil
import subprocess
import sys

import ezdxf

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import patikra_dxf  # noqa: E402

P = os.path.join(HERE, "projektai")
EXP = {"L01": 4, "L02": 4, "L03": 4, "L04": 4, "L05": 3, "L06": 4, "L07": 4, "L08": 4}
err = []


def p6(cwd, args):
    out = os.path.join(cwd, "dxf")
    shutil.rmtree(out, ignore_errors=True)
    r = subprocess.run(["python3", os.path.join(HERE, "p6_dxf.py")] + args, cwd=cwd, capture_output=True, text=True)
    if r.returncode:
        err.append(f"{os.path.basename(cwd)}: p6_dxf rc {r.returncode}: {r.stderr[-300:]}")
        return r.stdout, None
    return r.stdout, glob.glob(os.path.join(out, "*_P6_1-1_*.dxf"))[0]


def circles(fn):
    d = ezdxf.readfile(fn)
    ents = [x for e in d.modelspace() for x in (e.virtual_entities() if e.dxftype() == "INSERT" else [e])]
    return collections.Counter(round(e.dxf.radius, 1) for e in ents if e.dxftype() == "CIRCLE" and e.dxf.layer == "2_GALAS")


def holes(out, tag):
    got = {m.group(1): int(m.group(2)) for m in re.finditer(r"^\s+(L\d\d): (\d+) skyl", out, re.M)}
    if got != EXP:
        err.append(f"{tag}: D3.2 ne pagal formą - {got} (laukta {EXP})")


# 1) P6 ant rėmo
c1 = os.path.join(P, "bandymas_3500")
out, fn = p6(c1, ["Bandymas_client.pdf", "dxf", "--scale", "1.4077823", "--rails-json", "rails.json", "--no-letters",
                  "--prefix", "TEST_Bandymas_3500", "--cable", "bottom"])
if fn:
    holes(out, "rėmas")
    c = circles(fn)
    if c.get(4.0):
        err.append(f"rėmas: drenažas turi būti PUSLANKIS kontūre, rasta {c[4.0]} x Ø8 skylučių")
    if "PUSLANKIAI" not in out:
        err.append("rėmas: p6_dxf nepranešė apie drenažo puslankius")
    err += [f"rėmas DXF: {e}" for e in patikra_dxf.check(fn)]
# 2) P6 ant folded
c2 = os.path.join(P, "bandymas_3500_folded")
out, fn = p6(c2, ["Bandymas_folded_client.pdf", "dxf", "--scale", "1.4077823", "--fill", "1,1,1", "--rails-json", "axes.json",
                  "--folded", "--no-letters", "--prefix", "TEST_Bandymas_folded", "--cable", "bottom"])
if fn:
    holes(out, "folded")
    c = circles(fn)
    if not c.get(4.0):
        err.append("folded: drenažas turi būti Ø8 SKYLUTĖS (ant folded lieka skylutės) - nerasta")
    err += [f"folded DXF: {e}" for e in patikra_dxf.check(fn)]
    r = subprocess.run(["python3", "folded_test.py"], cwd=c2, capture_output=True, text=True)   # pilna eiga (v321)
    comb = os.path.join(c2, "TEST_Bandymas_folded_combined.dxf")
    if r.returncode or not os.path.exists(comb):
        err.append(f"folded: vientisas DXF nepavyko {r.stderr[-300:]}")
    else:
        d = ezdxf.readfile(comb)
        lay = collections.Counter(e.dxf.layer for e in d.modelspace() if e.dxftype() == "CIRCLE")
        if lay.get("LETTER_FIX_D3.2") != 31 or not lay.get("DRAIN_D8"):
            err.append(f"folded: fone turi būti tos pačios skylės - {dict(lay)}")
        err += [f"folded vientisas DXF: {e}" for e in patikra_dxf.check(comb)]
        # v321: Ø11 laido skylė briaunoje - 15 nuo lenkimo linijos ir 15 nuo viršaus (kairė: x = 38 - 15, y = 1038 - 15)
        ed = [e for e in d.modelspace() if e.dxftype() == "CIRCLE" and e.dxf.layer == "HOLE_D11_CABLE" and e.dxf.center.x < 38]
        if not ed or abs(ed[0].dxf.center.x - 23) > 0.1 or abs(ed[0].dxf.center.y - 1023) > 0.1 or abs(ed[0].dxf.radius - 5.5) > 0.01:
            err.append(f"folded: Ø11 briaunoje turi būti 15 / 15 nuo lenkimo / viršaus - {[(e.dxf.center.x, e.dxf.center.y) for e in ed]}")
        # v321: skylės fone = raidžių dugno skylės (1:1)
        p6d = ezdxf.readfile(fn)
        le = [x for e in p6d.modelspace() for x in (e.virtual_entities() if e.dxftype() == "INSERT" else [e])]
        lh = sorted((round(e.dxf.radius, 1), round(e.dxf.center.x, 1), round(e.dxf.center.y, 1)) for e in le
                    if e.dxftype() == "CIRCLE" and e.dxf.layer == "2_GALAS")
        fh = [(round(e.dxf.radius, 1), e.dxf.center.x, e.dxf.center.y) for e in d.modelspace() if e.dxftype() == "CIRCLE"
              and e.dxf.layer in ("LETTER_FIX_D3.2", "DRAIN_D8", "HOLE_D11_CABLE") and e.dxf.center.x > 38]
        if lh and fh:
            ox = min(q[1] for q in fh if q[0] == 1.6) - min(q[1] for q in lh if q[0] == 1.6)
            oy = min(q[2] for q in fh if q[0] == 1.6) - min(q[2] for q in lh if q[0] == 1.6)
            bad = [q for q in fh if not any(abs(q[0] - a) < 0.05 and abs(q[1] - ox - b) < 0.2 and abs(q[2] - oy - c_) < 0.2
                                            for a, b, c_ in lh)]
            if bad or len(fh) != len(lh):
                err.append(f"folded: fono skylės nesutampa su raidžių dugnu ({len(fh)} / {len(lh)})")
for e in err:
    print("  !", e)
print("P6 PAGRINDINĖ TAISYKLĖ:", "OK" if not err else f"{len(err)} klaid.")
sys.exit(1 if err else 0)
