"""ALT8901 (SPAR 225960 patvirtinimas, 2026-10-16): rėmas DXF moduliui iš PATVIRTINTO lapo (kliento valytų failų nėra).
- FRONT VIEW: raidžių sritis = virš „FRONT VIEW" antraštės, kairiau „SIDE VIEW"; mastelis iš bendro pločio (overall_mm),
  pritrauktas prie artimiausio 1:N; bėgeliai / statmenys = rėmo spalvos stačiakampiai (aspect > 3).
- ausėlės = ausėlių spalvos kvadratėliai FRONT VIEW (prie bėgelių iš vidaus), skylė - centre, Ø iš BOM (ear_hole).
Išvestis: rails JSON (origin_pt [0, 0], mm nuo lapo kampo, y žemyn) - p6_dxf.py --rails-json.
python3 remas_is_lapo.py <lapas.pdf> <cfg.json> <raktas> <out.json>"""
import json
import sys

import pymupdf as fitz

PT = 25.4 / 72


def near(c, ref, tol=0.03):
    return c is not None and max(abs(a - b) for a, b in zip(c[:3], ref)) <= tol


def front_region(p):
    fv = p.search_for("FRONT VIEW")[0]
    sv = p.search_for("SIDE VIEW")
    right = min([s.x0 - 5 for s in sv if s.x0 > fv.x1] or [p.rect.width - 10])
    return fitz.Rect(30, 30, right, fv.y0 - 2)


def rear_region(p):
    rv = p.search_for("REAR VIEW")[0]
    fv = p.search_for("FRONT VIEW")[0]
    top = fv.y1 + 2 if rv.y0 > fv.y1 else 30
    return fitz.Rect(30, top, p.rect.width - 10, rv.y0 - 2)


def main(pdf, cfg_path, key, out):
    C = json.load(open(cfg_path))[key]
    p = fitz.open(pdf)[C["page"]]
    FR = fitz.Rect(*C["front"]) if C.get("front") else front_region(p)
    dr = p.get_drawings()
    # mastelis: raidžių / logotipų (C["fills"]) gabaritas FRONT VIEW = overall_mm
    L = fitz.Rect()
    for d in dr:
        if FR.contains(d["rect"]) and any(near(d["fill"], f_, 0.06) for f_ in C["fills"]):
            L.include_rect(d["rect"])
    raw = C["overall_mm"] / L.width / PT
    N = min(C.get("scales", [5, 10, 15, 20, 25, 30, 40, 50, 75, 100, 150, 200]), key=lambda n: abs(n - raw))
    S = N * PT
    if abs(raw - N) / N > 0.02:
        print(f"  ! {key}: mastelis {raw:.2f} toli nuo 1:{N}")

    def rails_in(R):
        out_ = []
        for d in dr:
            r = d["rect"]
            if not R.intersects(r) or not near(d["fill"], C["rail_fill"], 0.012):
                continue
            if max(r.width, r.height) / max(min(r.width, r.height), 0.1) < 3:
                continue
            out_.append(r)
        return out_

    fr_rails = [r for r in rails_in(FR) if FR.contains(r)]
    H = sorted([r for r in fr_rails if r.width >= r.height], key=lambda r: (r.y0, r.x0))
    V = sorted([r for r in fr_rails if r.width < r.height], key=lambda r: r.x0)
    rails = [{"x0": r.x0 * S, "y0": r.y0 * S, "x1": r.x1 * S, "y1": r.y1 * S, "kind": "h", "acc": False, "end": False,
              "poly": None} for r in H]
    rails += [{"x0": r.x0 * S, "y0": r.y0 * S, "x1": r.x1 * S, "y1": r.y1 * S, "kind": "v", "acc": False, "end": False,
               "poly": None} for r in V]
    # ausėlės - FRONT VIEW (matomos prie bėgelių iš vidaus; patvirtintas lapas, REAR VIEW - tos pačios vietos)
    ears = []
    if C.get("ear_fill"):
        for d in dr:
            r = d["rect"]
            if not FR.contains(r) or not near(d["fill"], C["ear_fill"], 0.012):
                continue
            if max(r.width, r.height) * S > 120 or min(r.width, r.height) * S < 15:
                continue
            ears.append({"x0": r.x0 * S, "y0": r.y0 * S, "x1": r.x1 * S, "y1": r.y1 * S, "hx": (r.x0 + r.x1) / 2 * S,
                         "hy": (r.y0 + r.y1) / 2 * S, "d": C.get("ear_hole", 6)})
        ears.sort(key=lambda q: (q["hy"], q["hx"]))
    json.dump({"origin_pt": [0, 0], "scale": S, "separate": False, "rails": rails, "ears": ears, "brackets": []},
              open(out, "w"), indent=1)
    print(f"OK {key}: 1:{N} (raw {raw:.2f}), crop {[round(v) for v in FR]}, bėgeliai h {len(H)} "
          f"[{', '.join(f'{(r.x1 - r.x0) * S:.0f}' for r in H)}], v {len(V)}, ausėlės {len(ears)}")
    return N, FR


if __name__ == "__main__":
    main(*sys.argv[1:5])
