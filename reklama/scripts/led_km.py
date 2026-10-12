#!/usr/bin/env python3
"""LED (Kaisen PRISM, v127) išdėstymas raidėse - GAMYBOS STILIUS (v119, Rytis 2026-10-12: „led dėliojimas vis dar blogas",
pavyzdžiai: assets/led_pavyzdziai/, ypač ALT8873 EXTRA 225978_1 / _2 - Ryčio perdaryti mūsų lapai).

NUMATYTAS LED įrankis (led_sim.py Lens simuliacija - tik paprašius). Principas:
  - modulis KM-P2 HE 0,72 W (balti 6500K) / KM-P2-R HE 0,72 W (raudoni) - viena eilė per raidės ašį;
  - žingsnis („atstumas tarp centrų") pagal gylį: 50 -> 100, 70 -> 120, 80 -> 130, 100 -> 140 mm (spec "pitch" - kitaip);
  - apskritimas aplink modulį = žingsnis; statūs galai - apskritimas liečia galą (modulis p/2 nuo krašto),
    sankirtoje vienas modulis, žiedai simetriški (led_sim.structured, v119 galų taisyklė);
  - labai plati linija (> 2 x žingsnis) - tinklelis per plotą (EXTRA H1800 X);
  - galia = vnt. x 0,72 W; PSU - mažiausias KPS, kurio apkrova <= 75 %.
Lapas: kiekis virš raidės, aukštis / plotis, eilutė „LED module ... | N PCS. | Galia: ~W | Depth | Atstumas tarp centru",
PSU, „N pcs.", M 1:x, pavadinimas „<ALT>_<užsakymas>_LED".

Naudojimas: python3 led_km.py spec.json out.pdf
Spec: pdf, page, crop_pt, scale_mm_per_pt | ref_width_mm, depth, qty, order_no, title ("ALT..._... _LED"),
      groups: [{fill_rgb, led: "white" | "red", name, pitch?}]  (arba fill_rgb + led viršuje - viena grupė).
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import led_sim as LS  # noqa: E402  read_letters, skeleton_paths, _at, stroke_max

# v127 (Rytis 2026-10-12: „pridedu papildomą informaciją dėl LED ... failai gauti gamyboje, laikyti kaip NAUJĄ VERSIJĄ"):
# moduliai, PSU ir ryškumo lentelės - Kaisen Electric (assets/kaisen_led.json: kainoraštis 2023 Alt Reklama + Modules Depth
# table 2023). Modulis pagal gylį (kainoraščio diapazonai, PRISM 12V): 30-49 KM-P0, 50-59 KM-P1, 60-100 KM-P2 0,72W,
# 101-120 KM-P2 1W, 121-150 KM-P3 1,5W, 151-250 KM-P4 2W; raudoni - KM-P*-R; plona linija (< 35 mm) - MINI3.
# Žingsnis - DIDŽIAUSIAS ryškumo lentelėje su lx >= lux_target (2200; Ryčio lapai: KM-P2 d100 p140 = 2250 lx), <= CC.
# PSU - Kaisen KPS outdoor IP67 (12V / 24V), apkrova <= 75 %.
_KJ = json.load(open(os.path.join(HERE, "..", "assets", "kaisen_led.json"), encoding="utf-8"))
MODDB = {m["code"]: dict(m, name=m["code"]) for m in _KJ["modules"]}
_TAB = {b["name"]: [(float(d), float(p_), float(l)) for d, p_, l in b["table"]] for b in _KJ["depth_tables"]}
PSU = [tuple(x) for x in _KJ["psu_12v_outdoor"]]
PSU24 = [tuple(x) for x in _KJ["psu_24v_outdoor"]]
PSU_LOAD = 0.75
LUX = float(_KJ.get("lux_target", 2200))


def mod_for(depth, spec_mod=None, led="white", w=None):
    if spec_mod:
        return spec_mod
    if w is not None and w < _KJ.get("narrow_stroke_mm", 35) and led != "red":
        for r in _KJ["narrow"]:
            if r["depth"][0] <= depth <= r["depth"][1]:
                return r["code"]
    code = "KM-P2-W"
    for r in _KJ["letters_default"]:
        if r["depth"][0] <= depth <= r["depth"][1]:
            code = r["code"]; break
    if led == "red":
        code = _KJ["red"].get(code, code)
    return code


def mod_label(m, led):
    d = MODDB[m]
    return f"{d['code']} {str(d['W']).replace('.', ',')}W {d['V']}V" + (" RED" if d.get("color") == "red" else " 6500K")


def leds_of(m):
    w = MODDB[m]["W"]
    return 1 if w <= 0.5 else 2 if w <= 1.0 else 3 if w <= 1.5 else 4


def pitch_for(depth, m="KM-P2-W", led="white"):
    """didžiausias lentelės žingsnis su lx >= LUX (tarp lentelės gylių - tiesinė interpoliacija pagal gylį)"""
    md = MODDB[m]
    tab = _TAB.get(md.get("table") or "")
    cap = md.get("cc_mm") or 999
    if not tab:
        return int(min(cap, 0.7 * cap) // 10 * 10)
    ds = sorted(set(d for d, _, _ in tab))
    dd = min(max(depth, ds[0]), ds[-1])
    lo = max([d for d in ds if d <= dd]); hi = min([d for d in ds if d >= dd])
    best = None
    for p_ in sorted(set(p_ for _, p_, _ in tab)):
        def lx(d):
            v = [l for d2, p2, l in tab if d2 == d and p2 == p_]
            return v[0] if v else None
        a, b = lx(lo), lx(hi)
        if a is None or b is None:
            continue
        l = a if hi == lo else a + (b - a) * (dd - lo) / (hi - lo)
        if l >= LUX and p_ <= cap:
            best = p_
    if best is None:
        best = min(p_ for _, p_, _ in tab)
    return int(best)


def psu_for(watts, V=12):
    lst = PSU if V == 12 else PSU24
    for nm, w in lst:
        if watts <= PSU_LOAD * w:
            return nm, w
    nm, w = lst[-1]
    n = math.ceil(watts / (PSU_LOAD * w))
    return f"{n} x {nm}", w * n


def _split_bends(pa, pitch, ang_min=45.0):
    """v126: aštrus lenkimas (7, L, Z kampas) - šaka dalijama per kampą, kampe - modulis (Ryčio taisyklė 3)"""
    P, cum = pa["P"], pa["cum"]
    if pa["kind"] == "loop" or len(P) < 30:
        return [pa], []
    k = 12
    cuts = []
    for i in range(k, len(P) - k):
        a = P[i] - P[i - k]; b = P[i + k] - P[i]
        na, nb = math.hypot(*a), math.hypot(*b)
        if na < 1e-6 or nb < 1e-6:
            continue
        t = math.degrees(math.acos(max(-1, min(1, float(a @ b) / (na * nb)))))
        if t >= ang_min and cum[i] > 0.4 * pitch and cum[-1] - cum[i] > 0.4 * pitch:
            if cuts and cum[i] - cum[cuts[-1][0]] < 0.5 * pitch:
                if t > cuts[-1][1]:
                    cuts[-1] = (i, t)
                continue
            cuts.append((i, t))
    if not cuts:
        return [pa], []
    out, corners, i0 = [], [], 0
    e0, e1 = pa["ends"]
    idx = [c for c, _ in cuts]
    for n_, i1 in enumerate(idx + [len(P) - 1]):
        sub = P[i0:i1 + 1]
        cs = np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(sub, axis=0).T))])
        ends = [e0 if n_ == 0 else "c", e1 if i1 == len(P) - 1 else "c"]
        out.append({"P": sub, "cum": cs, "kind": "open", "ends": ends})
        i0 = i1
    corners = [(float(P[c][0]), float(P[c][1])) for c in idx]
    return out, corners


def chain(g, pitch):
    """v126 viena eilė per ašį (Ryčio lapai): status galas - modulis p/2 nuo krašto; sankirtoje ir aštriame kampe -
    po modulį; šaka tarp jų - lygiais tarpais <= ~p; galiniai moduliai NEŠALINAMI dėl sankirtos (A kojos)"""
    paths0 = LS.skeleton_paths(g)
    pos, nodes = [], []
    paths = []
    for pa in paths0:
        sp, cn = _split_bends(pa, pitch)
        paths += sp
        nodes += [(x, y, "c") for x, y in cn]
    for pa in paths:
        L = pa["cum"][-1]
        if pa["kind"] == "loop":
            n = max(2, round(L / pitch)); n += n % 2
            x0, y0, x1, y1 = g.bounds; cx = (x0 + x1) / 2
            best = None
            for ph in np.linspace(0, L / n, 24, endpoint=False):
                A_ = np.array([LS._at(pa, (ph + i * L / n) % L)[:2] for i in range(n)])
                M_ = np.column_stack([cx - (A_[:, 0] - cx), A_[:, 1]])
                err = float(np.min(np.hypot(M_[:, None, 0] - A_[None, :, 0], M_[:, None, 1] - A_[None, :, 1]), axis=1).sum())
                if best is None or err < best[0]:
                    best = (err, ph)
            pos += [LS._at(pa, (best[1] + i * L / n) % L) for i in range(n)]
            continue
        e0, e1 = pa["ends"]
        for e_, et in ((0, e0), (1, e1)):
            if et == "j":
                P = pa["P"] if e_ == 0 else pa["P"][::-1]
                nodes.append((float(P[0][0]), float(P[0][1]), "j"))
        node = lambda et: et in ("j", "c")
        a_ = pitch / 2 if e0 == "edge" else 0.0
        b_ = L - (pitch / 2 if e1 == "edge" else 0.0)
        if not node(e0) and not node(e1):                 # du galai
            if b_ - a_ < 0.5 * pitch:
                pos.append(LS._at(pa, L / 2)); continue
            k_ = max(1, round((b_ - a_) / pitch))
            us = [a_ + i * (b_ - a_) / k_ for i in range(k_ + 1)]
        elif node(e0) and node(e1):                       # tarp dviejų mazgų - tik vidiniai
            k_ = max(1, round(L / pitch))
            us = [L * i / k_ for i in range(1, k_)]
        else:                                             # galas -> mazgas: nuo galo p/2, lygiai iki mazgo
            fw = not node(e0)
            free_off = a_ if fw else L - b_
            span = L - free_off
            k_ = max(1, round(span / pitch))
            st = span / k_
            us = [free_off + i * st for i in range(k_)]
            if not fw:
                us = [L - u for u in us]
        pos += [LS._at(pa, u) for u in us]
    # mazgai (sankirtos / kampai): artimi - vienas; mazgo modulis nededamas, jei šalia (< 0,45 p) yra šakos modulis
    nd = []
    for q in nodes:
        if all(math.dist(q[:2], r[:2]) > 15 for r in nd):
            nd.append(q)
    out = [tuple(float(v) for v in q[:3]) for q in pos]
    pruned = []
    for q in out:
        if all(math.dist(q[:2], r[:2]) >= 0.45 * pitch for r in pruned):
            pruned.append(q)
    for x, y, _ in nd:
        if all(math.dist((x, y), r[:2]) >= 0.55 * pitch for r in pruned):
            pruned.append((x, y, 0.0))
    return pruned


def grid(g, pitch):
    """plati linija - tinklelis per plotą (centrai >= 0,35 p nuo krašto), fazė - daugiausia taškų"""
    inner = g.buffer(-0.35 * pitch)
    if inner.is_empty:
        return chain(g, pitch)
    from shapely import contains_xy
    x0, y0, x1, y1 = g.bounds
    best = []
    for fx in np.linspace(0, pitch, 6, endpoint=False):
        for fy in np.linspace(0, pitch, 6, endpoint=False):
            xs = np.arange(x0 + fx, x1, pitch); ys = np.arange(y0 + fy, y1, pitch)
            X, Y = np.meshgrid(xs, ys); X, Y = X.ravel(), Y.ravel()
            k = contains_xy(inner, X, Y)
            pts = [(x_, y_, 0.0) for x_, y_ in zip(X[k].tolist(), Y[k].tolist())]
            if len(pts) > len(best):
                best = pts
    return best


# v128 (Rytis 2026-10-12: „kai kur labai gerai, o kai kur net LED nepridėti ... taisyklės tik rekomendacijos ... labiau žiūrimas
# švietimo padengimas ... švietimas turi būti tolygus miksuojant taisyklių ir formos algoritmą"):
# 1) taisyklių išdėstymas (chain / grid) - pradinis;
# 2) ŠVIESOS PADENGIMO MODELIS veide: modulio šviesos dėmė E(d) = 1 / (1 + (d / s)^2)^2, s = COV_S x p_lx (p_lx - žingsnis pagal
#    gylio / lx lentelę, t.y. modulio optika + gylis; 1 = tiesiai virš modulio), moduliai sumuojami. Kalibruota pagal Ryčio
#    priimtus lapus: tarp modulių p atstumu ašyje / krašte - šviesu, galas p/2 nuo krašto - šviesu, 7 kampas už 0,8 p - tamsu.
#    Taškas TAMSUS, jei E < COV_E x E_ref, kur E_ref - tiesios tos pačios raidės pločio linijos su moduliais kas p apšvieta
#    krašte tarp modulių (t.y. tai, ką duoda taisyklė tiesioje vietoje - „gerai“ etalonas). Siaura krašto juosta (COV_EDGE x p) nevertinama - ją apšviečia šonų atspindys.
#    Tamsios dėmės (>= COV_MIN x p²) užpildomos godžiai: modulis ten, kur labiausiai pašviesina tamsų plotą (ašies / gilaus
#    ploto taškai, >= 0,45 p nuo kitų), pasuktas pagal vietinę ašį;
# 3) perteklius: modulis arčiau nei COV_DUP x p, be kurio tamsių dėmių nepadaugėja - šalinamas (karštos dėmės, pvz. brūkšnys
#    su 3 -> 2).
COV_S, COV_E, COV_EDGE, COV_MIN, COV_DUP = 0.60, 0.65, 0.08, 0.025, 0.70


def _cov_state(g, pitch):
    from scipy import ndimage
    res = max(1.5, pitch / 35.0)
    m, (ox, oy) = LS.raster(g, res)
    edt = ndimage.distance_transform_edt(m) * res
    ev = m & (edt >= COV_EDGE * pitch)
    mx = ndimage.maximum_filter(edt, size=3)
    ridge = m & (edt >= mx - 0.75 * res)
    cand = m & (ridge | (edt >= 0.35 * pitch)) & (edt >= min(0.15 * pitch, 0.6 * edt.max()))
    cand2 = m & (edt >= min(0.15 * pitch, 0.6 * edt.max()))
    sm = ndimage.gaussian_filter(edt, 1.5)
    gyy, gyx = np.gradient(np.gradient(sm, axis=0)); gxy, gxx = np.gradient(np.gradient(sm, axis=1))
    YY, XX = np.mgrid[0:m.shape[0], 0:m.shape[1]]
    return dict(res=res, m=m, ox=ox, oy=oy, edt=edt, ev=ev, cand=cand, cand2=cand2, ridge=ridge, X=ox + XX * res, Y=oy + YY * res,
                hxx=gxx, hyy=gyy, hxy=(gxy + gyx) / 2)


def illum(st, pts, sp):
    E = np.zeros(st["m"].shape)
    for q in pts:
        d2 = (st["X"] - q[0]) ** 2 + (st["Y"] - q[1]) ** 2
        E += 1.0 / (1.0 + d2 / (sp * sp)) ** 2
    return E


def _e_ref(st, pitch, sp):
    """tiesios linijos (plotis - raidės ašies mediana) krašto taškas tarp modulių kas p"""
    hw = float(np.median(st["edt"][st["cand"]])) if st["cand"].any() else 0.3 * pitch
    y = max(0.0, hw - COV_EDGE * pitch)
    return sum(1.0 / (1.0 + ((i + 0.5) ** 2 * pitch * pitch + y * y) / (sp * sp)) ** 2 for i in range(-4, 4))


def _spots(st, E, pitch):
    from scipy import ndimage
    dark = st["ev"] & (E < COV_E * st["eref"])
    lab, n = ndimage.label(dark)
    if not n:
        return 0.0, np.zeros_like(dark)
    area = ndimage.sum(dark, lab, range(1, n + 1)) * st["res"] ** 2
    keep = [i + 1 for i, a in enumerate(area) if a >= COV_MIN * pitch * pitch]
    big = np.isin(lab, keep)
    return float(big.sum() * st["res"] ** 2), big


def _axis_angle(st, r, c):
    a, b, d = st["hxx"][r, c], st["hxy"][r, c], st["hyy"][r, c]
    w, v = np.linalg.eigh(np.array([[a, b], [b, d]]))
    vx, vy = v[:, 1]                      # mažiausiai išlinkusi kryptis = ašis
    return math.atan2(vy, vx)


def _obj(st, E):
    T = 0.95 * st["eref"]                 # tikslas - tiesios linijos lygis (tolygumas), ne tik slenkstis
    e = E[st["ev"]]
    return float(np.sum(np.maximum(0, T - e) ** 2) + 0.05 * np.sum(np.maximum(0, e - 2.2 * st["eref"]) ** 2))


def _relax(st, pts, pitch, h, iters=6):
    """modulių pastūmimas (taškas raidės viduje, >= 0,12 p nuo krašto, <= 0,3 p nuo pradinės vietos), mažinant trūkumą"""
    from scipy.ndimage import map_coordinates
    pts = list(pts); home = [q[:2] for q in pts]
    E = illum(st, pts, h); J = _obj(st, E)
    step = 0.12 * pitch
    def inside(x, y):
        c = (x - st["ox"]) / st["res"]; r = (y - st["oy"]) / st["res"]
        return float(map_coordinates(st["edt"], [[r], [c]], order=1)[0]) >= min(0.12 * pitch, 0.6 * st["edt"].max())
    def one(q):
        d2 = (st["X"] - q[0]) ** 2 + (st["Y"] - q[1]) ** 2
        return 1.0 / (1.0 + d2 / (h * h)) ** 2
    for _ in range(iters):
        moved = False
        for i, q in enumerate(pts):
            base = E - one(q)
            best = None
            for a in range(8):
                x = q[0] + step * math.cos(a * math.pi / 4); y = q[1] + step * math.sin(a * math.pi / 4)
                if math.dist((x, y), home[i]) > 0.3 * pitch or not inside(x, y):
                    continue
                dn = min([math.dist((x, y), o[:2]) for j, o in enumerate(pts) if j != i] or [9e9])
                d0 = min([math.dist(q[:2], o[:2]) for j, o in enumerate(pts) if j != i] or [9e9])
                if dn < 0.45 * pitch and dn <= d0:
                    continue
                E2 = base + one((x, y)); J2 = _obj(st, E2)
                if J2 < J - 1e-9 and (best is None or J2 < best[0]):
                    best = (J2, x, y, E2)
            if best:
                J, x, y, E = best; pts[i] = (x, y, q[2]); moved = True
        if not moved:
            step /= 2
            if step < 0.03 * pitch:
                break
    return pts


def coverage(g, pts, pitch, p_lx):
    """v128 švietimo tolygumo papildymas / perteklius; grąžina (pts, pridėta, pašalinta)"""
    from scipy.signal import fftconvolve
    st = _cov_state(g, pitch)
    h = COV_S * max(pitch, p_lx or pitch)
    st["eref"] = _e_ref(st, max(pitch, p_lx or pitch), h)
    pts = list(pts)
    k = int(math.ceil(2.5 * h / st["res"]))
    yy, xx = np.mgrid[-k:k + 1, -k:k + 1]
    K = 1.0 / (1.0 + (xx * xx + yy * yy) * st["res"] ** 2 / (h * h)) ** 2
    added = 0
    E = illum(st, pts, h)
    a_unc, big = _spots(st, E, pitch)
    for _ in range(40):
        if a_unc <= 0:
            break
        gain = fftconvolve(big.astype(float) * (COV_E * st["eref"] - np.minimum(E, COV_E * st["eref"])), K, mode="same")
        ok = st["cand2"].copy()
        for q in pts:
            ok &= np.hypot(st["X"] - q[0], st["Y"] - q[1]) >= 0.35 * pitch
        if not ok.any():
            break
        score = np.where(ok, gain * np.where(st["cand"], 1.0, 0.85), -1)   # ašis / gilus plotas - pirmenybė
        r, c = np.unravel_index(int(np.argmax(score)), score.shape)
        q = (float(st["X"][r, c]), float(st["Y"][r, c]), _axis_angle(st, r, c))
        E1 = illum(st, pts + [q], h)
        a1, big1 = _spots(st, E1, pitch)
        if a1 > a_unc - 0.5 * COV_MIN * pitch * pitch:
            break
        pts.append(q); E, a_unc, big = E1, a1, big1
        added += 1
    # 3) pakoreguotos vietos: jei buvo tamsių dėmių - moduliai pastumiami (<= 0,3 p nuo pradinės vietos), kol tamsių / karštų
    #    dėmių mažėja (formos algoritmas taisyklių išdėstymą tik pataiso)
    if added or a_unc > 0:
        pts = _relax(st, pts, pitch, h)
        E = illum(st, pts, h); a_unc, big = _spots(st, E, pitch)
    removed = 0
    changed = True
    while changed and len(pts) > 1:
        changed = False
        nn = [min(math.dist(q[:2], o[:2]) for o in pts if o is not q) for q in pts]
        for i in sorted(range(len(pts)), key=lambda i: nn[i]):
            if nn[i] >= COV_DUP * pitch:
                break
            trial = pts[:i] + pts[i + 1:]
            a1, _ = _spots(st, illum(st, trial, h), pitch)
            if a1 <= a_unc + 1e-6:
                pts = trial; removed += 1; changed = True
                break
    return pts, added, removed


# v129 (Rytis 2026-10-12: „vistiek dėliojimas labai keistas, neatitinka nei gamybinių, nei teorinių planų"):
# NUMATYTAS - APSKRITIMŲ PAKAVIMAS kaip Ryčio gamybos lapuose (ALT8873 Åpn894, ALT8852 EXTRA, ALT8855 Matkroken):
# kiekvienas modulis = apskritimas Ø žingsnis (Kaisen „teorinis“ modulio plotas), apskritimai raidės VIDUJE, liečia vienas kitą
# (centrų atstumas ~0,85-1,0 p, galai - liečia raidės galą) ir raidės kraštus; siaura linija (< p) - centrai ašyje, apskritimas išlenda per šonus.
#  1) leistinos centrų vietos A: edt >= min(p/2, 0,85 x vietinis linijos pusplotis);
#  2) pradžia - linijos galas: apskritimas liečia galą (min [plotas 1,5 p spinduliu] - 3 x [raidės plotas apskritime]);
#  3) fronto augimas: kitas apskritimas LIEČIA jau padėtą (atstumas 0,9-1,0 p) ten, kur padengia daugiausia nepadengto ploto
#     (todėl eina linija, šakojasi sankirtose, plačioje linijoje - 2 eilės kaip ALT8852);
#  4) nepasiekta dalis - naujas frontas; likę tarpai (>= 45 % apskritimo naujo ploto) - užpildomi (atstumas >= 0,6 p);
#  5) modulis pasuktas pagal vietinę raidės kryptį (raidės taškų PCA apskritime).
PK_MIN, PK_MAX, PK_GAP = 0.70, 1.00, 0.75


def pack(g, pitch):
    from scipy import ndimage
    from scipy.signal import fftconvolve
    res = max(1.5, pitch / 28.0)
    m, (ox, oy) = LS.raster(g, res)
    pad = int(math.ceil(0.8 * pitch / res))
    m = np.pad(m, pad); ox -= pad * res; oy -= pad * res
    edt = ndimage.distance_transform_edt(m) * res
    r = pitch / 2.0
    loc = ndimage.maximum_filter(edt, size=max(3, int(pitch / res) | 1))
    ridge = m & (edt >= ndimage.maximum_filter(edt, size=3) - 0.75 * res)
    A = m & ((edt >= np.minimum(r, 0.85 * loc)) | (ridge & (edt >= 0.5 * np.minimum(r, loc))))   # ašis - iki galų / kampų
    YY, XX = np.mgrid[0:m.shape[0], 0:m.shape[1]]
    X = ox + XX * res; Y = oy + YY * res
    def disk(rad):
        k = int(math.ceil(rad / res)); yy, xx = np.mgrid[-k:k + 1, -k:k + 1]
        return ((xx * xx + yy * yy) * res * res <= rad * rad).astype(float)
    D = disk(r)
    mf = m.astype(float)
    maxcov = fftconvolve(mf, D, mode="same") * res * res
    area15 = fftconvolve(mf, disk(1.5 * pitch), mode="same") * res * res
    _, (ni, nj) = ndimage.distance_transform_edt(~A, return_indices=True)

    def grow(P, gap_only=False):
        P = [tuple(q) for q in P]
        cov = np.zeros(m.shape, bool); dmin = np.full(m.shape, np.inf)
        for x, y in P:
            d = np.hypot(X - x, Y - y); cov |= d <= r; dmin = np.minimum(dmin, d)
        for _ in range(400):
            newc = fftconvolve((m & ~cov).astype(float), D, mode="same") * res * res
            ratio = np.where(maxcov > 1, newc / np.maximum(maxcov, 1), 0)
            ok = A & (dmin >= 0.9 * pitch)
            ring = A & (dmin >= PK_MIN * pitch) & (dmin <= PK_MAX * pitch + res)   # galas - arčiau (tolygiai - relax)
            cand = ring & (ratio >= (0.45 if gap_only else 0.30))
            if cand.any():
                sc = np.where(cand, newc, -1)
            else:
                st = ok & (ratio >= 0.60)
                if st.any():
                    sc = np.where(st, 3.0 * maxcov - area15, -np.inf)
                else:
                    gp = m & (dmin >= PK_GAP * pitch) & (ratio >= 0.55) & (edt >= min(0.3 * pitch, 0.6 * edt.max()))
                    if not gp.any():
                        break
                    sc = np.where(gp, newc, -1)
            i, j = np.unravel_index(int(np.argmax(sc)), sc.shape)
            x, y = float(X[i, j]), float(Y[i, j])
            d = np.hypot(X - x, Y - y); cov |= d <= r; dmin = np.minimum(dmin, d)
            P.append((x, y))
        return np.array(P, float).reshape(-1, 2)

    def proj(x, y):
        i = int(round((y - oy) / res)); j = int(round((x - ox) / res))
        i = min(max(i, 0), m.shape[0] - 1); j = min(max(j, 0), m.shape[1] - 1)
        return float(X[ni[i, j], nj[i, j]]), float(Y[ni[i, j], nj[i, j]])

    def covmask(P):
        c = np.zeros(m.shape, int)
        for x, y in P:
            c += (X - x) ** 2 + (Y - y) ** 2 <= r * r
        return c

    def relax(P, iters, prune):
        # 6) tolygumas: persidengę (< 0,95 p) apskritimai stumiami vienas nuo kito, nepadengta raidės dalis traukia;
        #    centras lieka A; prune - šalinamas apskritimas, kurio nuosavas plotas < 20 %.
        for it in range(iters):
            if len(P) < 2:
                break
            C = covmask(P)
            unc = m & (C == 0)
            uy, ux = Y[unc], X[unc]
            newP = P.copy()
            for k, (x, y) in enumerate(P):
                f = np.zeros(2)
                for l, (x2, y2) in enumerate(P):
                    if l == k:
                        continue
                    d = math.hypot(x - x2, y - y2)
                    if d < 0.95 * pitch:
                        f += 0.35 * (0.95 * pitch - d) * np.array([x - x2, y - y2]) / max(d, 1e-6)
                if ux.size:
                    dd = np.hypot(ux - x, uy - y); sel = dd < 1.1 * pitch
                    if sel.any():
                        f += 0.25 * np.array([ux[sel].mean() - x, uy[sel].mean() - y]) * \
                            min(1.0, sel.sum() * res * res / (0.3 * math.pi * r * r))
                newP[k] = proj(x + f[0], y + f[1])
            done = np.abs(newP - P).max() < 0.3 * res
            P = newP
            if prune and it in (15, 30) or (prune and done):
                C = covmask(P)
                own = [(m & (C == 1) & ((X - x) ** 2 + (Y - y) ** 2 <= r * r)).sum() /
                       max((m & ((X - x) ** 2 + (Y - y) ** 2 <= r * r)).sum(), 1) for x, y in P]
                k = int(np.argmin(own))
                if own[k] < 0.20 and len(P) > 1:
                    P = np.delete(P, k, axis=0); done = False
            if done:
                break
        return P

    P = grow([])
    P = relax(P, 40, True)
    P = grow(P, gap_only=True)
    P = relax(P, 20, False)
    out = []
    rr = 0.6 * pitch
    for x, y in P:
        sel = m & (np.hypot(X - x, Y - y) <= rr)
        px, py = X[sel] - x, Y[sel] - y
        if px.size > 3:
            Cv = np.cov(np.vstack([px, py])); w_, v_ = np.linalg.eigh(Cv); ang = math.atan2(v_[1, 1], v_[0, 1])
        else:
            ang = 0.0
        if ang > math.pi / 2: ang -= math.pi
        if ang <= -math.pi / 2: ang += math.pi
        out.append((float(x), float(y), ang))
    return out


# v131 (Rytis 2026-10-12: „vistiek keletoje vietų nedėti LED, nors jie ten turėtų būti" -> rekomenduotas ir patvirtintas
# („bandyk") GAMYBOS LYGIO sprendimas): LED išdėstymas - OPTIMIZAVIMO uždavinys (aprėptis, sveikųjų sk. programavimas, HiGHS):
#  - kandidatai - raidės taškai kas ~p/10 (centras ne prie pat krašto: edt >= min(0,22 p, 0,6 vietinio pusploto));
#  - SĄLYGA: kiekvienas raidės veido taškas (be krašto juostos IL_EDGE x p - šonų atspindys) <= IL_R x p nuo modulio
#    -> tuščių vietų (t skersinio galas, e skersinis, d pilvo viršus) NEGALI likti;
#  - ribojimas: langelyje 0,38 p x 0,38 p - ne daugiau 1 modulio (nesusispaudžia);
#  - tikslas: MAŽIAUSIAI modulių; lygiaverčių - arčiau ašies (baudos taškas už nutolimą nuo ašies);
#  - rezultatas pastovus (ta pati raidė - tas pats išdėstymas).
IL_R, IL_EDGE, IL_REL, IL_SEP, IL_STEP, IL_WALL, IL_RV, IL_RE, IL_ENDF, IL_DENS = 0.60, 0.10, 0.35, 0.75, 0.10, 0.03, 0.80, 0.64, 0.42, 0.90


def ilp(g, pitch, time_limit=30, n_min=0):
    from scipy import ndimage
    from scipy.optimize import milp, LinearConstraint, Bounds
    from scipy.sparse import csr_matrix
    res = max(1.5, pitch / 40.0)
    m, (ox, oy) = LS.raster(g, res)
    pad = 3
    m = np.pad(m, pad); ox -= pad * res; oy -= pad * res
    edt = ndimage.distance_transform_edt(m) * res
    loc = ndimage.maximum_filter(edt, size=max(3, int(pitch / res) | 1))
    YY, XX = np.mgrid[0:m.shape[0], 0:m.shape[1]]
    X = ox + XX * res; Y = oy + YY * res
    st = max(1, int(round(IL_STEP * pitch / res)))
    sub = np.zeros(m.shape, bool); sub[::st, ::st] = True
    cmask = sub & m & (edt >= np.minimum(0.22 * pitch, 0.6 * loc))
    dst = max(1, int(round(0.08 * pitch / res)))
    dsub = np.zeros(m.shape, bool); dsub[::dst, ::dst] = True
    dmask = dsub & m & (edt >= np.maximum(np.minimum(IL_EDGE * pitch, 0.5 * loc), IL_REL * loc))
    cx, cy = X[cmask], Y[cmask]; dx, dy = X[dmask], Y[dmask]
    if cx.size == 0:
        return []
    R = IL_R * pitch
    # v132 (Rytis: „LED dėliojama lovyje ... įdėjus į tūrį kampas blokuoja šviesą"): taškas apšviečiamas tik jei tiesi linija
    # modulis -> taškas (vaizdas iš viršaus) visa eina raidės viduje - šoninės sienelės užstoja (kampai, e / t / 3 lenkimai).
    mi = m.copy()
    nsamp = max(8, int(R / res))
    ts = np.linspace(0.0, 1.0, nsamp)[1:-1]
    def visible(x0, y0, xs, ys):
        px = x0 + (xs[:, None] - x0) * ts[None, :]; py = y0 + (ys[:, None] - y0) * ts[None, :]
        jj = np.clip(np.rint((px - ox) / res).astype(int), 0, m.shape[1] - 1)
        ii = np.clip(np.rint((py - oy) / res).astype(int), 0, m.shape[0] - 1)
        return mi[ii, jj].all(axis=1)
    rows, cols = [], []
    for k in range(dx.size):
        j = np.nonzero((cx - dx[k]) ** 2 + (cy - dy[k]) ** 2 <= R * R)[0]
        if j.size:
            j = j[visible(dx[k], dy[k], cx[j], cy[j])]
        if j.size == 0:                       # nepasiekiamas taškas - artimiausias MATOMAS kandidatas (bet kokiu atstumu)
            d2 = (cx - dx[k]) ** 2 + (cy - dy[k]) ** 2
            order = np.argsort(d2)[:200]
            vis = visible(dx[k], dy[k], cx[order], cy[order])
            j = order[vis][:1] if vis.any() else order[:1]
        rows += [k] * j.size; cols += j.tolist()
    Acov = csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(dx.size, cx.size))
    # v132: VISAS veidas iki pat sienelės (juosta IL_WALL x p) turi MATYTI bent vieną modulį <= IL_RV x p atstumu -
    # kampo „šešėlyje" (už lenkimo, prie sienelės) šonų atspindys neapšviečia, todėl ten būtinas savas modulis.
    wmask = dsub & m & (edt >= IL_WALL * pitch) & ~dmask
    wx, wy = X[wmask], Y[wmask]
    # v133 (Rytis: „t viršus, brūkšnelio kairė pusė, apatinis galas - šviesos pritruks; EXTRA E galiukai nešvies"):
    # LINIJOS GALAI - taškas, kurio aplinkoje (0,5 p) mažai raidės ploto (< IL_ENDF) -> modulis <= IL_RE x p
    # (atitinka taisyklę „modulis p/2 nuo galo, linijos ašyje"), kiti sienelės taškai - <= IL_RV x p.
    from scipy.signal import fftconvolve
    kk = int(math.ceil(0.5 * pitch / res)); yy_, xx_ = np.mgrid[-kk:kk + 1, -kk:kk + 1]
    dk = ((xx_ * xx_ + yy_ * yy_) * res * res <= (0.5 * pitch) ** 2).astype(float)
    frac = fftconvolve(m.astype(float), dk, mode="same") / dk.sum()
    wend = frac[wmask] < IL_ENDF
    rows2, cols2 = [], []
    for k in range(wx.size):
        RV = (IL_RE if wend[k] else IL_RV) * pitch
        j = np.nonzero((cx - wx[k]) ** 2 + (cy - wy[k]) ** 2 <= RV * RV)[0]
        if j.size:
            j = j[visible(wx[k], wy[k], cx[j], cy[j])]
        if j.size:
            rows2 += [len(set(rows2)) if False else k] * j.size; cols2 += j.tolist()
    if rows2:
        r2 = np.array(rows2); ur, ri = np.unique(r2, return_inverse=True)
        Awall = csr_matrix((np.ones(len(cols2)), (ri, cols2)), shape=(ur.size, cx.size))
        from scipy.sparse import vstack as _vs
        Acov = _vs([Acov, Awall]).tocsr()
    # tarpas tarp modulių >= IL_SEP x p: kiekviename IL_SEP/2 spindulio skritulyje - ne daugiau 1 modulio
    hr = IL_SEP * pitch / 2.0
    rr2, cc2 = [], []
    for k in range(cx.size):
        j = np.nonzero((cx - cx[k]) ** 2 + (cy - cy[k]) ** 2 <= hr * hr)[0]
        rr2 += [k] * j.size; cc2 += j.tolist()
    Acell = csr_matrix((np.ones(len(rr2)), (rr2, cc2)), shape=(cx.size, cx.size))
    off = 1.0 - edt[cmask] / np.maximum(loc[cmask], 1e-6)          # 0 - ašis, 1 - kraštas
    c = 1.0 + 0.15 * np.clip(off, 0, 1)
    cons = [LinearConstraint(Acov, lb=1, ub=np.inf), LinearConstraint(Acell, lb=0, ub=1)]
    if n_min:
        cons.append(LinearConstraint(np.ones((1, cx.size)), lb=n_min, ub=np.inf))
    r_ = milp(c, constraints=cons, integrality=np.ones(cx.size), bounds=Bounds(0, 1),
              options={"time_limit": time_limit, "mip_rel_gap": 0.01, "disp": False})
    if r_.x is None:                          # langelio ribojimas per griežtas (labai maža forma) - be jo
        r_ = milp(c, constraints=[cons[0]] + cons[2:], integrality=np.ones(cx.size), bounds=Bounds(0, 1),
                  options={"time_limit": time_limit, "mip_rel_gap": 0.01, "disp": False})
    sel = np.nonzero(r_.x > 0.5)[0]
    out = []
    for k in sel:
        x, y = float(cx[k]), float(cy[k])
        q = m & (np.hypot(X - x, Y - y) <= 0.6 * pitch)
        px, py = X[q] - x, Y[q] - y
        if px.size > 3:
            w_, v_ = np.linalg.eigh(np.cov(np.vstack([px, py]))); ang = math.atan2(v_[1, 1], v_[0, 1])
        else:
            ang = 0.0
        if ang > math.pi / 2: ang -= math.pi
        if ang <= -math.pi / 2: ang += math.pi
        out.append((x, y, ang))
    return out


def place(g, pitch, p_lx=None, layout="ilp"):
    if layout == "ilp":
        return ilp(g, pitch), "ilp", 0, 0
    if layout == "pack":
        return pack(g, pitch), "pack", 0, 0
    w = LS.stroke_max(g)
    pts, mode = (grid(g, pitch), "grid") if w > 2.0 * pitch else (chain(g, pitch), "chain")
    pts, a, r = coverage(g, pts, pitch, p_lx)
    return pts, mode, a, r


def run(spec):
    groups = spec.get("groups") or [{"fill_rgb": spec["fill_rgb"], "led": spec.get("led", "white"), "name": ""}]
    depth = spec["depth"]
    res = []
    allL = []
    for gr in groups:
        L, S = LS.read_letters(spec["pdf"], gr["fill_rgb"], crop_pt=spec.get("crop_pt"), scale=spec.get("scale_mm_per_pt"),
                               ref_width_mm=spec.get("ref_width_mm"), page=spec.get("page", 0),
                               min_area_mm2=spec.get("min_area_mm2", 300))
        allL.append(L)
    # bendras nulis: visų grupių min (read_letters nulina pagal savo grupę) - perskaičiuojama pagal PDF
    import pymupdf as fitz
    pg = fitz.open(spec["pdf"])[spec.get("page", 0)]
    sc = spec.get("scale_mm_per_pt")
    org = {}
    for k, gr in enumerate(groups):
        fills = gr["fill_rgb"] if isinstance(gr["fill_rgb"][0], (list, tuple)) else [gr["fill_rgb"]]
        xs, ys = [], []
        for d in pg.get_drawings():
            f = d.get("fill"); r = d["rect"]; c = spec.get("crop_pt")
            if not f or not any(all(abs(a - b) <= 0.02 for a, b in zip(f, fc)) for fc in fills):
                continue
            if c and not (r.x0 >= c[0] and r.y0 >= c[1] and r.x1 <= c[2] and r.y1 <= c[3]):
                continue
            xs.append(r.x0); ys.append(r.y0)
        org[k] = (min(xs), min(ys))
    gx, gy = min(o[0] for o in org.values()), min(o[1] for o in org.values())
    from shapely import affinity
    for k, (gr, L) in enumerate(zip(groups, allL)):
        dx, dy = (org[k][0] - gx) * sc, (org[k][1] - gy) * sc
        L = [affinity.translate(g, dx, dy) for g in L]
        w_med = float(np.median([LS.stroke_max(g) for g in L])) if L else None
        m = mod_for(depth, gr.get("module") or spec.get("module"), gr.get("led", "white"), w_med)
        p = gr.get("pitch") or spec.get("pitch") or pitch_for(depth, m, gr.get("led", "white"))
        p_lx = p
        if not (gr.get("pitch") or spec.get("pitch")) and L:
            # v126: plonos linijos (mažos raidės) - žingsnis <= 1,6 x linijos plotis (geometrinė aprėptis)
            p = int(min(p, max(60, round(1.6 * w_med / 10.0) * 10)))
        per = []
        for g in L:
            pts, mode, a_, r_ = place(g, p, p_lx, gr.get("layout") or spec.get("layout") or "ilp")
            per.append({"g": g, "pts": pts, "mode": mode, "cov": (a_, r_)})
        lay = gr.get("layout") or spec.get("layout") or "ilp"
        if lay == "ilp" and len(per) > 1:
            # v133 (Rytis: „7 ir 3 bendroje grandinėje atrodys blankiau"): vienodas ryškumas grupėje - modulių tankis
            # (vnt. / veido plotas) kiekvienoje raidėje >= IL_DENS x grupės medianos; trūksta - ILP su min. kiekiu
            dens = [len(x["pts"]) / max(x["g"].area, 1) for x in per]
            D = float(np.median(dens))
            for x, d_ in zip(per, dens):
                need = int(math.ceil(IL_DENS * D * x["g"].area - 1e-9))
                if len(x["pts"]) < need:
                    x["pts"] = ilp(x["g"], p, n_min=need); x["cov"] = (need - len(x["pts"]), 0)
        n = sum(len(x["pts"]) for x in per)
        watts = n * MODDB[m]["W"]
        res.append({"gr": gr, "mod": m, "pitch": p, "plx": p_lx, "letters": per, "n": n, "W": watts, "psu": psu_for(watts, MODDB[m]["V"])})
        print(f"  {gr.get('name') or 'grupė'}: {mod_label(m, gr.get('led', 'white'))} žingsnis ~{p} -> " +
              ", ".join(str(len(x['pts'])) for x in per) + f" = {n} vnt., {watts:.1f} W, {psu_for(watts, MODDB[m]['V'])[0]}" +
              ("" if all(x["mode"] in ("chain", "pack", "ilp") for x in per) else "  (plati linija - tinklelis)") +
              f"  [padengimas: +{sum(x['cov'][0] for x in per)} / -{sum(x['cov'][1] for x in per)}]")
    return res


def _wire_order(pts):
    """v126: grandinės eiga raidėje - artimiausias kaimynas nuo apatinio kairio + 2-opt (laidas be šuolių)"""
    if len(pts) < 3:
        return list(pts)
    rest = list(pts)
    cur = min(rest, key=lambda q: q[0] - q[1] * 0.5)
    seq = [cur]; rest.remove(cur)
    while rest:
        cur = min(rest, key=lambda q: math.dist(q[:2], seq[-1][:2]))
        seq.append(cur); rest.remove(cur)
    improved = True
    while improved:
        improved = False
        for i in range(1, len(seq) - 2):
            for j in range(i + 1, len(seq) - 1):
                d0 = math.dist(seq[i - 1][:2], seq[i][:2]) + math.dist(seq[j][:2], seq[j + 1][:2])
                d1 = math.dist(seq[i - 1][:2], seq[j][:2]) + math.dist(seq[i][:2], seq[j + 1][:2])
                if d1 < d0 - 1e-6:
                    seq[i:j + 1] = seq[i:j + 1][::-1]; improved = True
    return seq


def sheet(spec, res, out):
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A3, landscape
    from reportlab.lib.colors import HexColor, black, white
    from reportlab.lib.units import mm
    W, H = landscape(A3)
    c = canvas.Canvas(out, pagesize=(W, H))
    GREY = HexColor("#E2E8E5"); RED = HexColor("#E2001A"); ORANGE = HexColor("#F7A600")
    # rėmas
    c.setLineWidth(0.4); c.setStrokeColor(HexColor("#BBBBBB")); c.rect(10 * mm, 10 * mm, W - 20 * mm, H - 20 * mm)
    c.setFont("Helvetica", 7); c.setFillColor(HexColor("#888888"))
    for i in range(8):
        x = 10 * mm + (W - 20 * mm) * (i + 0.5) / 8
        c.drawCentredString(x, H - 8 * mm, str(i + 1)); c.drawCentredString(x, 5 * mm, str(i + 1))
    for i, ch in enumerate("ABCDEF"):
        y = H - 10 * mm - (H - 20 * mm) * (i + 0.5) / 6
        c.drawCentredString(5 * mm, y, ch); c.drawCentredString(W - 5 * mm, y, ch)
    # turinys: visų grupių raidės
    allg = [x["g"] for r in res for x in r["letters"]]
    x0 = min(g.bounds[0] for g in allg); y0 = min(g.bounds[1] for g in allg)
    x1 = max(g.bounds[2] for g in allg); y1 = max(g.bounds[3] for g in allg)
    PW_, PH_ = x1 - x0, y1 - y0
    n_info = len(res)
    box_w, box_h = W - 70 * mm, H - 20 * mm - 60 * mm - n_info * 22
    s = min(box_w / PW_, box_h / PH_) * 0.92
    sc_ = 1.0 / (s / mm)                                  # 1 mm lapo = sc_ mm gaminio
    nice = [2, 2.5, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30, 40, 50]
    M = next((v for v in nice if v >= sc_), sc_)
    s = mm / M
    ox = (W - PW_ * s) / 2 - x0 * s
    top = H - 10 * mm - 28 * mm
    T = lambda x, y: (ox + x * s, top - (y - y0) * s)
    for r in res:
        col = RED if r["gr"].get("led") == "red" else black
        for x in r["letters"]:
            g = x["g"]
            for poly in getattr(g, "geoms", [g]):
                p_ = c.beginPath()
                for ring in [poly.exterior] + list(poly.interiors):
                    pts = [T(*q) for q in ring.coords]
                    p_.moveTo(*pts[0])
                    for q in pts[1:]:
                        p_.lineTo(*q)
                    p_.close()
                c.setFillColor(GREY); c.setStrokeColor(GREY); c.setLineWidth(0.1)
                c.drawPath(p_, stroke=0, fill=1, fillMode=0)
            c.setStrokeColor(col); c.setLineWidth(0.35)
            for (px, py, ang) in x["pts"]:
                cx, cy = T(px, py)
                c.circle(cx, cy, r["pitch"] / 2 * s, stroke=1, fill=0)
            # v120: LED IMITACIJA - modulio korpusas (lentelės matmenys) pagal ašies kryptį + LED / lęšiai (Rytis: gamybai
            # priimtiniau nei vieni apskritimai); grandinės laidas tarp gretimų modulių
            md = MODDB[r["mod"]]
            sz = md.get("size_mm") or [0.32 * r["pitch"], 0.12 * r["pitch"]]   # BaltLED matmenų nenurodo - simbolinis
            nl = leds_of(r["mod"])
            ml, mw = sz[0] * s, sz[1] * s
            seq = _wire_order(x["pts"])
            c.setStrokeColor(HexColor("#555555")); c.setLineWidth(0.3)
            for a_, b_ in zip(seq, seq[1:]):
                if math.dist(a_[:2], b_[:2]) <= 1.6 * r["pitch"]:
                    p0, p1 = T(*a_[:2]), T(*b_[:2]); c.line(p0[0], p0[1], p1[0], p1[1])
            for (px, py, ang) in seq:
                cx, cy = T(px, py)
                c.saveState(); c.translate(cx, cy); c.rotate(-math.degrees(ang))
                c.setFillColor(white); c.setStrokeColor(black); c.setLineWidth(0.4)
                c.roundRect(-ml / 2, -mw / 2, ml, mw, min(1.5, mw / 4), stroke=1, fill=1)
                c.setFillColor(col if r["gr"].get("led") == "red" else HexColor("#F2C200"))
                for i_ in range(nl):
                    lx = -ml / 2 + ml * (i_ + 0.5) / nl
                    c.circle(lx, 0, max(0.6, mw * 0.28), stroke=0, fill=1)
                c.restoreState()
            # kiekis virš raidės; v129: jei virš raidės yra kita forma (ö / i taškai) - po raide
            bx0, by0, bx1, by1 = g.bounds
            ymax = min(q[1] for q in x["pts"]) - r["pitch"] / 2 if x["pts"] else by0
            ybot = max(q[1] for q in x["pts"]) + r["pitch"] / 2 if x["pts"] else by1
            above = any(o is not x and o["g"].bounds[0] < bx1 and o["g"].bounds[2] > bx0 and o["g"].bounds[3] <= by0 + 1
                        for rr_ in res for o in rr_["letters"])
            c.setFillColor(black); c.setFont("Helvetica-Bold", 13)
            if above:
                tx, ty = T((bx0 + bx1) / 2, max(by1, ybot))
                c.drawCentredString(tx, ty - 18, str(len(x["pts"])))
            else:
                tx, ty = T((bx0 + bx1) / 2, min(by0, ymax))
                c.drawCentredString(tx, ty + 8, str(len(x["pts"])))
    # matmenys
    c.setStrokeColor(black); c.setFillColor(black); c.setLineWidth(0.5)
    xa, yb = T(x0, y1); xb, _ = T(x1, y1)
    yd = yb - 14
    c.line(xa, yd, xb, yd); c.line(xa, yd - 4, xa, yd + 4); c.line(xb, yd - 4, xb, yd + 4)
    c.setFont("Helvetica", 9); c.drawCentredString((xa + xb) / 2, yd - 11, f"{PW_:.0f} mm")
    xl = xa - 14; _, yt = T(x0, y0)
    c.line(xl, yt, xl, yb); c.line(xl - 4, yt, xl + 4, yt); c.line(xl - 4, yb, xl + 4, yb)
    c.saveState(); c.translate(xl - 3, (yt + yb) / 2); c.rotate(90); c.drawCentredString(0, 0, f"{PH_:.0f} mm"); c.restoreState()
    # informacija
    yi = yd - 34
    for r in res:
        led = r["gr"].get("led", "white")
        c.setFont("Helvetica", 12); c.setFillColor(black)
        nm = (r["gr"].get("name") + ":  ") if r["gr"].get("name") and len(res) > 1 else ""
        c.drawString(xa, yi, f"{nm}LED module {mod_label(r['mod'], led)}  |  {r['n']} PCS.  |  Galia: ~{r['W']:.0f}W  |  "
                             f"Depth: {spec['depth']} mm  |  Atstumas tarp centru ~{r['pitch']} mm")
        if led == "red":
            c.setFillColor(RED); c.drawString(xa, yi - 14, "RED LED Modules"); c.setFillColor(black)
        else:
            c.drawString(xa, yi - 14, "White LED Modules, 6500K")
        c.drawString(xa + 200, yi - 14, f"PSU {r['psu'][0]}  ({r['psu'][1]} W, {MODDB[r['mod']]['V']} V, IP67)")
        yi -= 34
    # apačia
    c.setFillColor(black); c.rect(10 * mm, 22 * mm, 34 * mm, 14 * mm, stroke=0, fill=1)
    c.setFillColor(white); c.setFont("Helvetica", 18); c.drawString(13 * mm, 26 * mm, f"{spec.get('qty', 1)} pcs.")
    c.setFillColor(HexColor("#F2F2F2")); c.rect(10 * mm, 10 * mm, W - 20 * mm - 30 * mm, 12 * mm, stroke=0, fill=1)
    c.setFillColor(black); c.setFont("Helvetica", 16)
    c.drawString(16 * mm, 14 * mm, spec.get("title") or f"{spec.get('order_no', '')}_LED")
    c.setFont("Helvetica", 11); c.drawRightString(W - 42 * mm, 25 * mm, f"M 1:{M:g}")
    c.setFillColor(ORANGE); c.rect(W - 40 * mm, 10 * mm, 30 * mm, 18 * mm, stroke=0, fill=1)
    c.setFillColor(black); c.setFont("Helvetica-Bold", 20); c.drawCentredString(W - 25 * mm, 15 * mm, "LED")
    c.showPage(); c.save()
    return out


def sim(spec, res, out):
    """v128 švietimo patikra (ne gamybai): santykinė apšvieta raidėse (1 = tiesios linijos etalonas), tamsios dėmės - mėlynai"""
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    L = [(r, x) for r in res for x in r["letters"]]
    fig, axs = plt.subplots(1, len(L), figsize=(2.6 * len(L), 3.6)); axs = np.atleast_1d(axs)
    for ax, (r, x) in zip(axs, L):
        st = _cov_state(x["g"], r["pitch"]); h = COV_S * max(r["pitch"], r["plx"])
        er = _e_ref(st, max(r["pitch"], r["plx"]), h); E = illum(st, x["pts"], h) / er
        ext = [st["ox"], st["ox"] + st["m"].shape[1] * st["res"], st["oy"] + st["m"].shape[0] * st["res"], st["oy"]]
        ax.imshow(np.where(st["m"], E, np.nan), cmap="inferno", vmin=0.3, vmax=1.1, extent=ext)
        ax.contour(st["X"], st["Y"], st["ev"] & (E < COV_E), levels=[0.5], colors="cyan", linewidths=0.8)
        ax.plot([q[0] for q in x["pts"]], [q[1] for q in x["pts"]], "w.", ms=4)
        ax.set_title(f"{len(x['pts'])} vnt., min {E[st['ev']].min():.2f}", fontsize=8); ax.axis("off")
    plt.tight_layout(); plt.savefig(out, dpi=80); plt.close(fig)
    return out


if __name__ == "__main__":
    sp = json.load(open(sys.argv[1], encoding="utf-8"))
    r = run(sp)
    if len(sys.argv) > 2:
        print("OK", sheet(sp, r, sys.argv[2]))
    if len(sys.argv) > 3:
        print("OK", sim(sp, r, sys.argv[3]))
