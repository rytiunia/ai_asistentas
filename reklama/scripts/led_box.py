#!/usr/bin/env python3
"""LED šviesdėžei (kvadratinis tinklelis) - variantai iš TIEKĖJO lentelių (Rytis 2026-10-09).

Naujesnė 24V lentelė (P320L): kiekvienam gyliui iki 3 žingsnių / ryškumų -> spausdinami visi, kad būtų galima
rinktis ryškumą. Senesnė 12V Lens lentelė (P65L / P130L / P190L): vienas žingsnis gyliui (45 % / 30 % plexi).

Tinklelis: nx = ceil(plotis / p), ny = ceil(aukštis / p); kraštinė eilė - pusė faktinio žingsnio nuo krašto
(kaip tiekėjo testo dėžėje ir gamybos pavyzdžiuose). Faktinis žingsnis <= lentelės žingsnis.
Gylis tarp lentelės stulpelių - imamas ŽEMESNIS stulpelis (kaip led_sim.supplier_spacing). Žemiau lentelės - netaikoma.
lx - tiekėjo testo reikšmė, perskaičiuota pagal FAKTINĮ tankį (lx ~ vnt./m²: tiekėjo lentelėje 120 mm gylyje
130-135 lx vienam vnt./m² visiems trims žingsniams). Vienodi tinkleliai (skirtingi lentelės žingsniai -> tas pats
nx x ny) rodomi vieną kartą.

Naudojimas:  python3 led_box.py <plotis_mm> <aukštis_mm> <gylis_mm> [modulis ...] [--plexi 45|30]
             (be modulio - visi, kuriems yra lentelė)
"""
import json
import math
import os
import sys

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "led_lens.json")


def options(mod, depth, plexi="45"):
    """[(pitch, lux, pastaba)] tiekėjo lentelės stulpelis gyliui (žemesnis), ir modulio duomenys"""
    D = json.load(open(DATA, encoding="utf-8"))
    if mod in D.get("lux_table_24v", {}):
        tab, md = D["lux_table_24v"][mod], D["modules_24v"][mod]
        cols = sorted(int(c) for c in tab)
        ok = [c for c in cols if c <= depth]
        if not ok:
            return md, None, []
        col = ok[-1]
        return md, col, [(r["pitch_mm"], r["lux"], r.get("note", "")) for r in tab[str(col)]]
    if mod in D.get("lux_table", {}) and mod != "_info":
        tab, md = D["lux_table"][mod], D["modules"][mod]
        cols = sorted(int(c) for c in tab)
        ok = [c for c in cols if c <= depth]
        if not ok:
            return md, None, []
        col = ok[-1]
        p, lx = tab[str(col)][plexi]
        return md, col, [(p, lx, f"plexi {plexi} %")]
    return None, None, []


def grid(Wb, Hb, p):
    nx, ny = max(1, math.ceil(Wb / p - 1e-9)), max(1, math.ceil(Hb / p - 1e-9))
    return nx, ny, Wb / nx, Hb / ny


def main(argv):
    plexi = "45"
    if "--plexi" in argv:
        i = argv.index("--plexi"); plexi = argv[i + 1]; argv = argv[:i] + argv[i + 2:]
    Wb, Hb, depth = float(argv[0]), float(argv[1]), float(argv[2])
    D = json.load(open(DATA, encoding="utf-8"))
    mods = argv[3:] or [m for m in D.get("lux_table_24v", {}) if m != "_info"] + [m for m in D.get("lux_table", {}) if m != "_info"]
    print(f"Šviesdėžė {Wb:.0f} x {Hb:.0f} mm, gylis {depth:.0f} mm")
    print(f"{'modulis':8} {'V':>3} {'lent.':>5} {'žingsnis':>8} {'tinklelis':>10} {'faktinis':>11} {'vnt.':>5} {'W':>7} {'~lx':>6} "
          f"{'grandinės':>9}  pastaba")
    for mod in mods:
        md, col, opts = options(mod, depth, plexi)
        if md is None:
            print(f"{mod:8} - nėra duomenų"); continue
        if not opts:
            print(f"{mod:8} - gylis {depth:.0f} mm mažesnis už lentelės pradžią"); continue
        chain = md.get("chain_pcs") or md.get("chain_1end")
        seen = set()
        for p, lx, note in opts:
            nx, ny, sx, sy = grid(Wb, Hb, p)
            if (nx, ny) in seen:
                continue
            seen.add((nx, ny))
            n = nx * ny
            lx = round(lx * (n / (Wb * Hb / 1e6)) / (1e6 / p ** 2) / 50) * 50     # pagal faktinį tankį
            feeds = math.ceil(n / chain) if chain else 0
            print(f"{mod:8} {md.get('V', 12):>3} {col:>5} {p:>6} mm {nx:>4} x {ny:<4} {sx:>4.0f} x {sy:<4.0f} {n:>5} {n * md['W']:>6.1f} "
                  f"{lx:>6} {feeds:>4} x<={chain}  {note}")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(__doc__); sys.exit(1)
    main(sys.argv[1:])
