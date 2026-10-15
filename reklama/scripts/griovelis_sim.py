#!/usr/bin/env python3
"""P10 (30 mm opal plexi) raidžių LED griovelio APŠVIETIMO SIMULIACIJA (v235, Rytis 2026-10-15:
„griovelis blogas, kampai lieka tušti, sudėjus LED juostą bus netolygus apšvietimas - pabandyk švietimo simuliaciją").

Modelis (kokybinis, parametrai kalibruojami bandymu su pavyzdine raide):
  * opalinis akrilas = sklaidi terpė -> stacionari difuzija su sugertimi raidės plote:  -D lap(phi) + mu phi = S,
    difuzijos ilgis L = sqrt(D / mu) ~ atstumas nuo juostos iki priekio (h = storis - griovelio gylis);
  * šviesa sklinda TIK akrile (tarpai tarp raidės dalių - oras, šviesa nepereina) - skaičiuojama ant raidės kaukės;
  * šonai praleidžia dalį šviesos (Robin sąlyga, alpha);
  * šaltinis - LED juosta griovelio ašyje (tolygus srautas ilgiui), pagal gylį dar išsklaidyta Gauss sigma = h / 3.
Rezultatas: priekio šviesumas, normuotas į viso logotipo medianą; kiekvienai raidei U = P5 / mediana ir tamsių
(< 0.6 medianos) ploto dalis; vertinama raidės plote be 2 mm pakraščio.

Naudojimas: python3 griovelis_sim.py griovelis.dxf out_prefix [--thk=30] [--depth=10] [--L=auto] [--alpha=0.3] [--res=0.5]
  DXF: OUTLINE (uždari kontūrai, mm) + CENTERLINE (SPLINE / LWPOLYLINE) - kaip centerline.py išvestis.
Išvestis: out_prefix_sim.png (žemėlapis), out_prefix_sim.json (rodikliai).
"""
import json
import sys

import cv2
import ezdxf
import numpy as np
from scipy import ndimage
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve
from shapely.geometry import Polygon
from shapely.ops import unary_union

ARG = lambda k, d: float(next((x.split("=")[1] for x in sys.argv if x.startswith(f"--{k}=")), d))


def load(dxf):
    m = ezdxf.readfile(dxf).modelspace()
    rings, lines = [], []
    for e in m:
        lay = e.dxf.layer.upper()
        if e.dxftype() == "LWPOLYLINE":
            pts = [(p[0], p[1]) for p in e.get_points("xy")]
        elif e.dxftype() == "SPLINE":
            pts = [(p.x, p.y) for p in e.flattening(0.05)]
        else:
            continue
        if lay == "OUTLINE" and len(pts) > 2:
            rings.append(Polygon(pts).buffer(0))
        elif lay.startswith("CENTERLINE") and len(pts) > 1:
            lines.append(np.array(pts))
    geo = None
    for r in rings:                                   # even-odd
        geo = r if geo is None else geo.symmetric_difference(r)
    return geo, lines


def simulate(geo, lines, res=0.5, thk=30.0, depth=10.0, L=None, alpha=0.3, pad=6.0):
    h = max(thk - depth, 2.0)
    L = L or h * 0.8
    x0, y0, x1, y1 = geo.bounds
    W, H = int((x1 - x0 + 2 * pad) / res) + 1, int((y1 - y0 + 2 * pad) / res) + 1
    P = lambda x, y: ((x - x0 + pad) / res, (y1 + pad - y) / res)          # y žemyn (paveikslėlis)
    mask = np.zeros((H, W), np.uint8)
    for g in getattr(geo, "geoms", [geo]):
        cv2.fillPoly(mask, [np.array([P(*q) for q in g.exterior.coords], np.int32)], 1)
        for r in g.interiors:
            cv2.fillPoly(mask, [np.array([P(*q) for q in r.coords], np.int32)], 0)
    src = np.zeros((H, W), np.float64)
    for Ln in lines:
        seg = np.diff(Ln, axis=0); sl = np.hypot(*seg.T)
        for a, d_, l_ in zip(Ln[:-1], seg, sl):
            n = max(int(l_ / (res / 2)), 1)
            for t in (np.arange(n) + 0.5) / n:
                px, py = P(a[0] + d_[0] * t, a[1] + d_[1] * t)
                ix, iy = int(px), int(py)
                if 0 <= iy < H and 0 <= ix < W:
                    src[iy, ix] += l_ / n
    src = ndimage.gaussian_filter(src, h / 3 / res) * mask             # sklaida pagal gylį (tik akrile)
    # difuzija raidės kaukėje
    idx = -np.ones((H, W), np.int64)
    ys, xs = np.nonzero(mask)
    idx[ys, xs] = np.arange(len(ys))
    D, mu = 1.0, 1.0 / L ** 2
    k = D / res ** 2
    rows, cols, vals = [], [], []
    diag = np.full(len(ys), mu)
    for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        ny, nx_ = ys + dy, xs + dx
        ok = (ny >= 0) & (ny < H) & (nx_ >= 0) & (nx_ < W)
        nb = np.full(len(ys), -1)
        nb[ok] = idx[ny[ok], nx_[ok]]
        inn = nb >= 0
        diag += np.where(inn, k, alpha * k)
        rows.append(np.nonzero(inn)[0]); cols.append(nb[inn]); vals.append(np.full(inn.sum(), -k))
    n = len(ys)
    A = coo_matrix((np.concatenate(vals + [diag]), (np.concatenate(rows + [np.arange(n)]), np.concatenate(cols + [np.arange(n)]))),
                   shape=(n, n)).tocsc()
    phi = spsolve(A, src[ys, xs])
    E = np.zeros((H, W)); E[ys, xs] = phi
    ev = ndimage.binary_erosion(mask, iterations=int(round(2.0 / res))) > 0     # be 2 mm pakraščio
    med = float(np.median(E[ev])) or 1.0
    E /= med
    return dict(E=E, mask=mask, ev=ev, P=P, res=res, pad=pad, bounds=(x0, y0, x1, y1), h=h, L=L, alpha=alpha)


def per_letter(S, geo):
    lab, nl = ndimage.label(S["mask"])
    out = []
    for i in range(1, nl + 1):
        m = (lab == i) & S["ev"]
        if m.sum() < 50:
            continue
        v = S["E"][m]
        ys_, xs_ = np.nonzero(lab == i)
        out.append(dict(x_mm=float(xs_.min() * S["res"] - S["pad"]), x1_mm=float(xs_.max() * S["res"] - S["pad"]),
                        U=float(np.percentile(v, 5) / np.median(v)), dark=float((v < 0.6 * np.median(v)).mean()),
                        mean=float(v.mean())))
    out.sort(key=lambda d: d["x_mm"])
    return out


def render(S, lines, path, title):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    # v235: kiekviena raidė normuojama į SAVO medianą (tolygumas raidėje; ryškumo balansas tarp raidžių - atskirai)
    lab, nl = ndimage.label(S["mask"])
    En = S["E"].copy()
    for i in range(1, nl + 1):
        mm_ = (lab == i) & S["ev"]
        if mm_.sum():
            En[lab == i] /= float(np.median(S["E"][mm_])) or 1.0
    S = dict(S, E=En)
    E = np.ma.masked_where(S["mask"] == 0, S["E"])
    H, W = E.shape
    fig = plt.figure(figsize=(min(40, W * S["res"] / 40), H * S["res"] / 40 + 1.2), dpi=110)
    ax = fig.add_axes([0.01, 0.02, 0.92, 0.84])
    cm = matplotlib.colormaps["inferno"].copy(); cm.set_bad("white")
    im = ax.imshow(E, cmap=cm, vmin=0, vmax=1.6, interpolation="bilinear")
    for Ln in lines:
        q = np.array([S["P"](*p) for p in Ln])
        ax.plot(q[:, 0], q[:, 1], color="#00E5FF", lw=0.6)
    dk = (S["E"] < 0.6) & S["ev"]
    ax.contour(dk.astype(float), levels=[0.5], colors="#3BFF3B", linewidths=0.5)
    ax.set_axis_off()
    cax = fig.add_axes([0.94, 0.1, 0.012, 0.7]); fig.colorbar(im, cax=cax).set_label("brightness / letter median", fontsize=7)
    fig.suptitle(title, fontsize=9, x=0.01, ha="left")
    fig.savefig(path); plt.close(fig)


if __name__ == "__main__":
    dxf, out = sys.argv[1], sys.argv[2]
    geo, lines = load(dxf)
    S = simulate(geo, lines, res=ARG("res", 0.5), thk=ARG("thk", 30), depth=ARG("depth", 10),
                 L=(ARG("L", 0) or None), alpha=ARG("alpha", 0.3))
    pl = per_letter(S, geo)
    allv = S["E"][S["ev"]]
    summ = dict(U=float(np.mean([d["U"] for d in pl])), U_min=float(min(d["U"] for d in pl)),
                dark=float(np.average([d["dark"] for d in pl], weights=[d["x1_mm"] - d["x_mm"] for d in pl])),
                h=S["h"], L=S["L"], alpha=S["alpha"], letters=pl)
    json.dump(summ, open(out + "_sim.json", "w"), indent=1)
    render(S, lines, out + "_sim.png",
           f"{out}: LED strip in groove - face brightness (h = {S['h']:g} mm, L = {S['L']:.0f} mm); "
           f"U(P5/median) avg {summ['U']:.2f} / min {summ['U_min']:.2f}, dark (<0.6) = {summ['dark'] * 100:.1f} %  |  green = dark zones, cyan = strip")
    print(f"U vid. {summ['U']:.2f}, min {summ['U_min']:.2f}, tamsu {summ['dark'] * 100:.1f} %")
    for d in pl:
        print(f"  x {d['x_mm']:.0f}-{d['x1_mm']:.0f}: U {d['U']:.2f}, tamsu {d['dark'] * 100:.1f} %")
