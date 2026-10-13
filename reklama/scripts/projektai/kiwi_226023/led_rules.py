"""KIWI 226023 - originalo (ALT8858) LED brėžinių perbraižymo taisyklės led_mini.redraw (v176)."""


def _c(d, key, rgb, tol=0.04):
    v = d.get(key)
    return v is not None and all(abs(a - b) <= tol for a, b in zip(v[:3], rgb))


def _big(d, n=20):
    return max(d["rect"].width, d["rect"].height) > n


P130 = {"as": "module", "kind": "bar", "L_pt": 7.4, "W_pt": 2.1, "n": 3, "led": "#00A651", "name": "P130 green"}
P65 = {"as": "module", "kind": "dot", "L_pt": 4.6, "W_pt": 1.7, "n": 2, "led": "#FFFFFF", "name": "P65 white"}
P130L = {"as": "module", "kind": "dot", "L_pt": 11.0, "W_pt": 5.0, "lens": True, "led": "#00A651", "name": "P130 lens green"}

RULES = {
    0: [
        dict(match=lambda d: d["type"] == "fs" and _c(d, "fill", (0, 1, 0)), **P130),
        dict(match=lambda d: d["type"] == "s" and _c(d, "color", (0.89, 0, 0.06)) and not _big(d, 3), **P65),
        dict(match=lambda d: d["type"] == "s" and (_c(d, "color", (0.6, 1, 0.6)) or _c(d, "color", (0.85, 0.85, 0.85))),
             **{"as": "cover"}),
        dict(match=lambda d: _c(d, "fill", (0.96, 0.7, 0.71)), **{"as": "psu"}),
        dict(match=lambda d: d["type"] == "fs" and _c(d, "fill", (1, 0, 0)), **{"as": "exit"}),
        dict(match=lambda d: d["type"] == "s" and (_c(d, "color", (1, 0, 0)) or _c(d, "color", (0.89, 0, 0.06))),
             **{"as": "cable", "lw": 0.9}),
        dict(match=lambda d: d["type"] == "s" and _c(d, "color", (0.4, 0.72, 0.91)), **{"as": "outline", "col": "#3C8DBC"}),
        dict(match=lambda d: d["type"] == "s" and _c(d, "color", (0.1, 0.1, 0.1)), **{"as": "outline"}),
        dict(match=lambda d: True, **{"as": "skip"}),
    ],
    1: [
        dict(match=lambda d: d["type"] == "s" and _c(d, "color", (0, 0.59, 0.25)) and _big(d), **{"as": "cover"}),
        dict(match=lambda d: d["type"] == "s" and _c(d, "color", (0, 0.59, 0.25)) and not _big(d), **P130L),
        dict(match=lambda d: _c(d, "fill", (0.96, 0.7, 0.71)), **{"as": "psu"}),
        dict(match=lambda d: d["type"] == "s" and _c(d, "color", (0.89, 0, 0.06)), **{"as": "cable", "lw": 0.9}),
        dict(match=lambda d: d["type"] == "s" and _c(d, "color", (0, 0.54, 0.82)), **{"as": "outline", "col": "#3C8DBC"}),
        dict(match=lambda d: d["type"] == "s" and _c(d, "color", (0.1, 0.1, 0.1)), **{"as": "outline"}),
        dict(match=lambda d: True, **{"as": "skip"}),
    ],
}
# legendos miniatiūros: (originalo x, y) prieš atitinkamą „LED Installation" eilutę
LEGEND = {0: [(119.5, 526.0, P130), (119.5, 536.6, P65)], 1: [(180.0, 716.3, P130L)]}
# originalo balionai (BOM pozicijos) -> mūsų balionai už vaizdo: (taikinys originalo x, y, numeris)
BALLOONS = {1: [(206.6, 507.6, "9"), (493.3, 569.3, "10")]}
