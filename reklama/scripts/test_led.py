"""v329 LED DĖLIOJIMO regresija (Rytis 2026-10-17: „tam tikrose situacijose LED nedėdavo, nors ten reikėjo, ir A raidėje
vienoje kojelėje 3 LED, o kitoje jau 4, ir nėra brūkšnelyje tarp kojelių").
Testas projektai/led_test: AHMWBRSEKX (sans bold ir serif, aukštis 500 mm, gylis 100) - led_km numatytas išdėstymas (strokes):
  - SIMETRIJA: simetriškose raidėse (A H M W X) modulių kairėje = dešinėje (vidurio juosta ± 0,1 pločio neskaičiuojama);
  - BRŪKŠNYS: A ir H skersiniame brūkšnyje (tarp kojų, brūkšnio aukštyje) - >= 1 modulis;
  - PADENGIMAS: kiekvienas raidės ašies taškas (skeletas) <= 0,75 p nuo artimiausio modulio (nėra vietų be LED);
  - visi moduliai raidės viduje, tarpusavyje >= 0,45 p.
python3 scripts/test_led.py  -> exit 1, jei kas nors nesutampa."""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import led_km as LK  # noqa: E402
import led_sim as LS  # noqa: E402
from shapely.geometry import Point  # noqa: E402

D = os.path.join(HERE, "projektai", "led_test")
NAMES = "AHMWBRSEKX"
SYM = "AHMWX"
err = []
for f in ("spec_sans.json", "spec_serif.json"):
    spec = json.load(open(os.path.join(D, f)))
    spec["pdf"] = os.path.join(D, spec["pdf"])
    res = LK.run(spec)
    p = res[0]["pitch"]
    for ch, x in zip(NAMES, res[0]["letters"]):
        g, pts = x["g"], x["pts"]
        tag = f"{f[5:-5]} {ch}"
        x0, y0, x1, y1 = g.bounds
        cx, w = (x0 + x1) / 2, x1 - x0
        if ch in SYM and "sans" in f:                      # serif A / M / W / X - storio asimetrija (plona / stora koja)
            l_ = sum(1 for q in pts if q[0] < cx - 0.1 * w); r_ = sum(1 for q in pts if q[0] > cx + 0.1 * w)
            if l_ != r_:
                err.append(f"{tag}: nesimetriška - kairėje {l_}, dešinėje {r_}")
        if ch in "AH":
            # brūkšnys: horizontali juosta raidės viduryje tarp kojų (A - apatinėje pusėje)
            ys = [q[1] for q in pts if abs(q[0] - cx) < (0.15 if ch == "A" else 0.3) * w]
            band = (y0 + 0.45 * (y1 - y0), y0 + 0.85 * (y1 - y0)) if ch == "A" else (y0 + 0.3 * (y1 - y0), y0 + 0.7 * (y1 - y0))
            if not any(band[0] <= y <= band[1] for y in ys):
                err.append(f"{tag}: skersiniame brūkšnyje nėra LED")
        for q in pts:
            if not g.buffer(1).contains(Point(q[0], q[1])):
                err.append(f"{tag}: modulis už raidės ({q[0]:.0f}; {q[1]:.0f})")
        for i in range(len(pts)):
            for j in range(i + 1, len(pts)):
                if math.dist(pts[i][:2], pts[j][:2]) < 0.45 * p - 1:
                    err.append(f"{tag}: moduliai per arti ({math.dist(pts[i][:2], pts[j][:2]):.0f} < {0.45 * p:.0f})")
        far = 0
        A = np.array([q[:2] for q in pts])
        sw = LS.stroke_max(g)
        for pa in LS.skeleton_paths(g):
            if pa["kind"] != "loop" and "j" in pa["ends"] and (pa["cum"][-1] < 1.0 * sw or LK.is_serif(pa["P"], pa["ends"], g, sw)):
                continue                                   # serifai / užraitai (trumpos atšakos) - ne raidės linija
            cu = pa["cum"]
            for s_, u_ in zip(pa["P"][::5], cu[::5]):
                # laisvo galo zona (<= 0,6 linijos pločio nuo krašto, serifo kampas) - šviečia šonų atspindys, netikrinama
                if (pa["ends"][0] in ("edge", "free") and u_ < 0.6 * sw) or (pa["ends"][1] in ("edge", "free") and cu[-1] - u_ < 0.6 * sw):
                    continue
                if A.size and np.min(np.hypot(*(A - s_).T)) > 0.75 * p:
                    far += 1
        if far:
            err.append(f"{tag}: {far} ašies taškų toliau nei 0,75 p nuo LED (vieta be LED)")
# v331 (Rytis 2026-10-17, „Testavimas" - slab šriftas, 3779 x 615 mm, kontūrai užpildyti): t - skersinio kairė ir uodegos
#  galas su LED, tolygiai (t >= 7, ne 3 apačioje), a - uodega su LED (a >= 8); ne per tankiai (viso <= 80, >= 0,5 p)
spec = json.load(open(os.path.join(D, "spec_testavimas.json")))
spec["pdf"] = os.path.join(D, spec["pdf"])
r = LK.run(spec)[0]
cnt = [len(x["pts"]) for x in r["letters"]]
if len(cnt) != 11 or cnt[3] < 7 or cnt[4] < 8 or cnt[9] < 8 or sum(cnt) > 80:
    err.append(f"Testavimas: LED kiekiai {cnt} (laukta t >= 7, a >= 8, viso <= 80)")
for ch, x in zip("Testavimas", r["letters"]):
    q_ = x["pts"]
    for i in range(len(q_)):
        for j in range(i + 1, len(q_)):
            if math.dist(q_[i][:2], q_[j][:2]) < 0.5 * r["pitch"] - 1:
                err.append(f"Testavimas {ch}: sugrūsta - {math.dist(q_[i][:2], q_[j][:2]):.0f} < 0,5 p")
for e in err:
    print("  !", e)
print("LED DĖLIOJIMAS:", "OK" if not err else f"{len(err)} klaid.")
sys.exit(1 if err else 0)
