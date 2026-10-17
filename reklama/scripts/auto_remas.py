#!/usr/bin/env python3
"""auto_remas.py - rėmas iš raidžių, kai kliento faile bėgelių nėra (v75, Rytis 2026-10-10, „Bandymas / antras" pavyzdys
aa_remas.pdf). Taisyklė: RĖMO VIETA - PER RAIDĖS TVIRTINIMO PLOTO CENTRĄ.
- Horizontalūs bėgeliai: kiekvienai eilutei 2 - ašis per eilutės raidžių apatinių / viršutinių horizontalių štrichų
  VIDURĮ (x-aukščio kraštas ± pusė štricho storio: „B" apačia, „a" „t" „s" „d" viršus / apačia).
- Bėgelio galai: kraštinės raidės stiebo (štricho) VIDURYJE (kraštas ± pusė štricho storio), ne 10 mm nuo krašto.
- Statmenys: per raidžių STIEBUS (vertikalius štrichus), kuo labiau paslėpti po raide; jei stiebas yra ir kitoje eilutėje
  toje pačioje x - VIENAS statmuo per abi eilutes (jungia rėmą); apatinės eilutės statmenys visada pratęsiami aukštyn iki
  viršutinės eilutės apatinio bėgelio (rėmas vientisas). Kiekis eilutei max(2, ceil(L / 4500) + 1): kraštiniai stiebai +
  tarpiniai artimiausi tolygiam išdėstymui; pirmenybė stiebams, bendriems abiem eilutėms.
Naudojimas: braizyti_begeliai.py spec `"auto_frame": true` (kai kliento faile bėgelių nėra; veikia ir su `merge_rows`).
"""
import math
from shapely.geometry import LineString, Point, box as sbox
from shapely.ops import unary_union


def stroke_t(geom, hi=400):
    """štricho storis ~ 2 x didžiausias r, kuriam buffer(-r) netuščias (storiausia vieta); čia reikia tipinio -
    imamas r, kuriam lieka >= 15 % ploto (ploni elementai nuleidžiami)"""
    lo_, hi_ = 0.0, hi
    for _ in range(14):
        m = (lo_ + hi_) / 2
        if geom.buffer(-m).area >= 0.15 * geom.area:
            lo_ = m
        else:
            hi_ = m
    return 2 * lo_


def rows_of(letters):
    # v238 (Rytis 2026-10-15 „kodėl vėl rėmai ne pagal taisykles?", OMODA | JAECOO / EXLANTIX): eilutės renkamos pagal
    #  AUKŠČIO INTERVALŲ PERSIDENGIMĄ, aukščiausi elementai pirmi. Anksčiau eilutę „sėdavo" pirmas pagal y elementas -
    #  trafaretinio šrifto dalys (O pusės, E juostos, J pėda) tapdavo atskiromis eilutėmis -> netikri bėgeliai / auto rėmo klaida.
    rows = []
    for o in sorted(letters, key=lambda o: -(o["bb"][3] - o["bb"][1])):
        a, b = o["bb"][1], o["bb"][3]
        best = None
        for r in rows:
            ov = min(b, r["y1"]) - max(a, r["y0"])
            if ov >= 0.5 * min(b - a, r["y1"] - r["y0"]) and (best is None or ov > best[0]):
                best = (ov, r)
        if best:
            r = best[1]; r["letters"].append(o)
        else:
            rows.append({"y0": a, "y1": b, "h": b - a, "letters": [o]})
    for r in rows:
        r["cy"] = (r["y0"] + r["y1"]) / 2
    rows.sort(key=lambda r: r["cy"])                 # viršutinė (mažesnis y) pirma
    hmax = max(r["h"] for r in rows)
    big = [r for r in rows if r["h"] >= 0.5 * hmax]
    for r in rows:                                   # akcentai (Ė taškas, Ū brūkšnys, i taškai) - prie artimiausios eilutės
        if r["h"] < 0.5 * hmax:
            host = min(big, key=lambda b: abs(b["cy"] - r["cy"]))
            host["letters"] += r["letters"]
    # v229 (Leapmotor): eilutės aukštis - raidžių aukščių MEDIANA (ne pirmos raidės): aukštas simbolis (logotipo ženklas
    #  2 x teksto aukščio) neturi tapti eilutės matu - bėgeliai per TEKSTO štrichų vidurį, simbolis - ant to paties rėmo
    for r in big:
        _hs = [o["bb"][3] - o["bb"][1] for o in r["letters"]]
        # v238: trafaretų dalys (E juostos) - ne eilutės matas; v241 (Leapmotor): ir aukštas logotipo ženklas (2 x teksto) -
        #  ne matas: eilutės aukštis - DAŽNIAUSIO aukščio grupės (±15 %) mediana
        _best = max(_hs, key=lambda h: (sum(1 for q in _hs if abs(q - h) <= 0.15 * h), h))
        r["h"] = _median([q for q in _hs if abs(q - _best) <= 0.15 * _best] or _hs)
    return big


def _median(v):
    v = sorted(v); return v[len(v) // 2]


def stems(letters, y0, y1, w_min):
    """vertikalūs štrichai tarp y0..y1: intervalai (xa, xb), esantys visuose 7 pjūviuose su bendra dalimi >= w_min"""
    ys = [y0 + (y1 - y0) * f for f in (0.08, 0.2, 0.35, 0.5, 0.65, 0.8, 0.92)]
    out = []
    for o in letters:
        geo, (bx0, _, bx1, _) = o["geom"], o["bb"]
        if o["bb"][3] - o["bb"][1] < 0.5 * (y1 - y0):   # akcentai - ne stiebai
            continue
        segs_by_y = []
        for y in ys:
            ix = geo.intersection(LineString([(bx0 - 10, y), (bx1 + 10, y)]))
            segs = sorted((min(q.coords[0][0], q.coords[-1][0]), max(q.coords[0][0], q.coords[-1][0]))
                          for q in getattr(ix, "geoms", [ix]) if not q.is_empty and q.length > 1)
            segs_by_y.append(segs)
        for a, b in segs_by_y[3]:                       # vidurio pjūvio intervalai - kandidatai
            lo_, hi_ = a, b
            ok = True
            for segs in segs_by_y:
                m = [s for s in segs if s[0] < hi_ and s[1] > lo_]
                if not m:
                    ok = False; break
                s = max(m, key=lambda s: min(s[1], hi_) - max(s[0], lo_))
                lo_, hi_ = max(lo_, s[0]), min(hi_, s[1])
            if ok and hi_ - lo_ >= w_min:
                out.append((lo_, hi_, o))
    return sorted(out)


def _stroke_iv(geom, y, bx0, bx1):
    ix = geom.intersection(LineString([(bx0 - 10, y), (bx1 + 10, y)]))
    segs = [q for q in getattr(ix, "geoms", [ix]) if not q.is_empty and q.length > 1]
    return sorted((min(q.coords[0][0], q.coords[-1][0]), max(q.coords[0][0], q.coords[-1][0])) for q in segs)


def leg_line(o, y0, y1, side):
    """pasvirusios kojelės (A, V ...) vidurio tiesė tarp y0 ir y1 -> (x ties y0, x ties y1, nuolydis dx/dy) arba None"""
    geo, (bx0, _, bx1, _) = o["geom"], o["bb"]
    pts = []
    for k in range(9):
        y = y0 + (y1 - y0) * (0.3 + 0.075 * k)
        iv = _stroke_iv(geo, y, bx0, bx1)
        if len(iv) >= 2:
            a_, b_ = iv[-1] if side == "right" else iv[0]
            pts.append(((a_ + b_) / 2, y))
    if len(pts) < 4:
        return None
    n_ = len(pts); my = sum(q[1] for q in pts) / n_; mx = sum(q[0] for q in pts) / n_
    b = sum((q[1] - my) * (q[0] - mx) for q in pts) / max(sum((q[1] - my) ** 2 for q in pts), 1e-9)
    if abs(b) < 0.08:
        return None
    return mx + b * (y0 - my), mx + b * (y1 - my), b


def _cover_cand(o, ya, yb, t_rail, hx0, hx1, min_cov=0.5):
    """v311: statmuo per raidę be stiebo - x, kur raidė dengia statmenį daugiausia (statmuo tarp bėgelių galų)"""
    from shapely.geometry import box as _bx
    best = None
    for k_ in range(0, int(o["bb"][2] - o["bb"][0] - t_rail) + 1, 2):
        x_ = o["bb"][0] + k_
        if not (hx0 <= x_ and x_ + t_rail <= hx1):
            continue
        cov = o["geom"].intersection(_bx(x_, ya, x_ + t_rail, yb)).area / max(t_rail * (yb - ya), 1e-6)
        if best is None or cov > best[0]:
            best = (cov, x_ + t_rail / 2)
    if best and best[0] >= min_cov:
        return {"x": best[1], "k": "v", "o": o, "partial": best[0]}
    return None


ENDS_MID_L = 4000      # v337: ilgesnis rėmas - + vienas statmuo per vidurį


def single_verticals(r, t_rail, edge, pitch, pitch_heavy, heavy_m2_m, log, every_letter=False, ends_only=True):
    """v204 (Rytis 2026-10-14, „LIETUVA"): vienos eilutės rėmas - bėgeliai per VISĄ ilgį (kiekvienas iki kraštinės raidės
    krašto - edge), GALINIAI statmenys TIK ten, kur jie panaudojami: per kraštinei artimiausios raidės stiebą (L, T, E ...);
    raidės be stiebo (V, A) - ĮSTRIŽAS per kojelės vidurį kaip EXTRA (v95). Tarpiniai - per stiebus tolygiai, kiekis
    ceil(L / žingsnis) + 1. Statmenys / įstrižai - tarp bėgelių."""
    from shapely.geometry import Polygon
    top, bot = r["rails"][0], r["rails"][1]
    ya, yb = top["y1"], bot["y0"]
    hx0, hx1 = max(top["x0"], bot["x0"]), min(top["x1"], bot["x1"])
    cands = []
    for lo_, hi_, o in r["stems"]:
        xc = (lo_ + hi_) / 2
        if hx0 + t_rail / 2 <= xc <= hx1 - t_rail / 2:
            cands.append({"x": xc, "k": "v", "o": o})
    with_stem = {id(c["o"]) for c in cands}
    for o in r["letters"]:
        if id(o) in with_stem or o["bb"][3] - o["bb"][1] < 0.6 * r["h"]:
            continue
        inner = o["geom"].buffer(-edge)
        for sd in ("left", "right"):
            ln = leg_line(o, ya, yb, sd)
            if not ln:
                continue
            xc0, xc1, b = ln
            wh = t_rail / 2 * math.sqrt(1 + b * b)
            poly = Polygon([(xc0 - wh, ya), (xc0 + wh, ya), (xc1 + wh, yb), (xc1 - wh, yb)])
            mid = poly.intersection(Polygon([(-1e6, ya + 15), (1e6, ya + 15), (1e6, yb - 15), (-1e6, yb - 15)]))
            if not inner.covers(mid):
                continue
            # galai turi remtis į bėgelius
            if not (top["x0"] <= xc0 - wh and xc0 + wh <= top["x1"] and bot["x0"] <= xc1 - wh and xc1 + wh <= bot["x1"]):
                continue
            cands.append({"x": (xc0 + xc1) / 2, "k": "d", "line": ln, "o": o})
    if not cands:
        log("  ! auto rėmas: statmenims / įstrižams vietos po raidėmis nerasta - spręsti ranka")
        return []
    L = max(top["x1"], bot["x1"]) - min(top["x0"], bot["x0"])
    _a = sum(o["geom"].area for o in r["letters"]) / 1e6
    _p = pitch_heavy if _a / max(L / 1000, 1e-6) >= heavy_m2_m else pitch
    nv = max(2, math.ceil(L / _p) + 1)
    gap_ = 300
    left_ = min(cands, key=lambda c: (c["x"], c["k"] != "v"))
    right_ = max(cands, key=lambda c: (c["x"], c["k"] == "v"))
    # v311 (Rytis 2026-10-16, LEAP26-01002: „papildoma statmena po R raide gale"; TAISYKLĖ v299): GALINIS statmuo - po
    #  KRAŠTINE pilno aukščio raide. Jei ji be stiebo / kojelės (R, P šiame šrifte) - ten, kur raidė jį dengia daugiausia
    #  (>= 50 %); ankstesnis kraštinis kandidatas lieka tarpiniu.
    _full = [o for o in r["letters"] if o["bb"][3] - o["bb"][1] >= 0.6 * r["h"]]
    _extra = []
    for side_, o_ in (("l", min(_full, key=lambda o: o["bb"][0], default=None)),
                      ("r", max(_full, key=lambda o: o["bb"][2], default=None))):
        cur_ = left_ if side_ == "l" else right_
        if o_ is None or cur_["o"] is o_:
            continue
        c_ = _cover_cand(o_, ya, yb, t_rail, hx0, hx1)
        if c_:
            _extra.append(cur_)
            if side_ == "l":
                left_ = c_
            else:
                right_ = c_
            log(f"  auto rėmas: galinis statmuo po kraštine raide x{c_['x']:.0f} ({c_['partial'] * 100:.0f} % po raide)")
    chosen = [left_] + ([right_] if right_["x"] - left_["x"] >= gap_ else [])
    if ends_only:
        # v337 (Rytis 2026-10-17: „per daug rėmo statmenų - jų turi būti tik priekyje ir gale, jei ilgesnė nei 4 m - papildomas
        #  per vidurį; taikoma visiems rėmams išskyrus EXTRA"): tik 2 galiniai (+ 1 per vidurį, kai rėmas > 4 m) - be ankstesnio
        #  kraštinio kandidato (v311), be žingsnio (v87), be statmens po kiekviena raide (v229)
        if L > ENDS_MID_L:
            xm_ = (left_["x"] + right_["x"]) / 2
            c_ = [c for c in cands if all(abs(c["x"] - q["x"]) >= gap_ for q in chosen)]
            if c_:
                chosen.append(min(c_, key=lambda c: (abs(c["x"] - xm_) + (0 if c["k"] == "v" else 150))))
        nv = len(chosen)
        every_letter = False
    else:
        chosen += [c for c in _extra if all(abs(c["x"] - q["x"]) >= gap_ for q in chosen)]
    if every_letter:                                 # v229 (Rytis 2026-10-14, Leapmotor): AKRILINIS rėmas - statmuo po KIEKVIENA raide
        for o in r["letters"]:
            if o["bb"][3] - o["bb"][1] < 0.6 * r["h"] or any(c["o"] is o for c in chosen):
                continue
            c_ = [c for c in cands if c["o"] is o]
            if c_:
                xm = (o["bb"][0] + o["bb"][2]) / 2
                chosen.append(min(c_, key=lambda c: (c["k"] != "v", abs(c["x"] - xm))))
            else:                                    # raidė be ištiso stiebo (P, R šiame šrifte) - statmuo ten, kur raidė
                from shapely.geometry import box as _bx     #  dengia daugiausia (rėmas skaidrus - dalis gali matytis)
                best = None
                for k_ in range(0, int(o["bb"][2] - o["bb"][0] - t_rail) + 1, 2):
                    x_ = o["bb"][0] + k_
                    cov = o["geom"].intersection(_bx(x_, ya, x_ + t_rail, yb)).area / max(t_rail * (yb - ya), 1e-6)
                    if best is None or cov > best[0]:
                        best = (cov, x_ + t_rail / 2)
                if best and best[0] >= 0.5:
                    chosen.append({"x": best[1], "k": "v", "o": o, "partial": best[0]})
        nv = len(chosen)
    sp_ = (right_["x"] - left_["x"]) / max(nv - 1, 1)
    for i in range(1, (nv - 1) if not (every_letter or ends_only) else 1):
        tx = left_["x"] + sp_ * i
        c_ = [c for c in cands if all(abs(c["x"] - q["x"]) >= gap_ for q in chosen)]
        if not c_:
            break
        chosen.append(min(c_, key=lambda c: (c["k"] != "v", abs(c["x"] - tx))))
    out = []
    for c in sorted(chosen, key=lambda c: c["x"]):
        if c["k"] == "v":
            x0 = c["x"] - t_rail / 2
            out.append({"x0": x0, "x1": x0 + t_rail, "y0": ya, "y1": yb, "kind": "v", "auto": True, "len": yb - ya,
                        "end_v": c is left_ or c is right_,
                        "poly": [(x0, ya), (x0 + t_rail, ya), (x0 + t_rail, yb), (x0, yb)]})
            log(f"  auto rėmas: statmuo x{c['x']:.0f} per stiebą ({yb - ya:.0f} mm)" + (" - galinis" if c is left_ or c is right_ else "")
                + (f" - po raide {c['partial'] * 100:.0f} % (dalis matysis)" if c.get("partial") else ""))
        else:
            xc0, xc1, b = c["line"]
            wh = t_rail / 2 * math.sqrt(1 + b * b)
            poly = [(xc0 - wh, ya), (xc0 + wh, ya), (xc1 + wh, yb), (xc1 - wh, yb)]
            out.append({"x0": min(q[0] for q in poly), "x1": max(q[0] for q in poly), "y0": ya, "y1": yb, "kind": "d",
                        "auto": True, "len": math.hypot(xc1 - xc0, yb - ya), "poly": poly, "ang": math.degrees(math.atan(b)),
                        "end_v": c is left_ or c is right_})
            log(f"  auto rėmas: ĮSTRIŽAS per kojelę x{xc0:.0f}->{xc1:.0f} ({math.hypot(xc1 - xc0, yb - ya):.0f} mm, "
                f"{math.degrees(math.atan(b)):.0f}°)" + (" - galinis (raidė be stiebo, kaip EXTRA)" if c is left_ or c is right_ else ""))
    if len(out) < nv:
        log(f"  auto rėmas: statmenų {len(out)} (taisyklė {nv}) - tik panaudojamose vietose")
    return out


def build(g, t_rail, edge=10, pitch=2500, pitch_heavy=2000, heavy_m2_m=0.5, log=print, every_letter=False, v_edge=None,
          ends_only=True):
    """v337: ends_only (numatyta, visi rėmai išskyrus EXTRA) - statmenys tik galuose (+ 1 per vidurį, kai > 4 m);
    ends_only=False - senas žingsnio principas (EXTRA: ceil(L / žingsnis) + 1, v87 / v204 / v311)."""
    """g - grupė (letters su geom / bb); grąžina (hs, vs) bėgelių dict'ų sąrašus (x0, y0, x1, y1, kind, len, poly, auto)"""
    rows = rows_of(g["letters"])
    for r in rows:
        L = r["letters"]
        hs_ = [o for o in L if (o["bb"][3] - o["bb"][1]) >= 0.6 * r["h"]]
        r["xb"] = _median([o["bb"][1] for o in hs_]); r["xt"] = _median([o["bb"][3] for o in hs_])
        r["t"] = _median([stroke_t(o["geom"]) for o in hs_])
        r["x0"] = min(o["bb"][0] for o in L); r["x1"] = max(o["bb"][2] for o in L)
        lo_ = r["xb"] + r["t"] / 2; hi_ = r["xt"] - r["t"] / 2
        # v183: bėgelio kraštas >= 11 mm nuo raidžių viršaus / apačios (v49 taisyklė ir auto rėmui) - kitaip štrichas
        # plonesnis už bėgelį + 2 x 10 (antikva / serifai: apačia - tik serifas) ir galų vietos raidėje nerandama
        lo_ = max(lo_, r["xb"] + 11 + t_rail / 2); hi_ = min(hi_, r["xt"] - 11 - t_rail / 2)
        r["rails"] = [{"cy": lo_}, {"cy": hi_}]      # [0] - viršutinis (mažesnis y), [1] - apatinis
        # galai - kraštinių raidžių stiebo viduryje (kraštas +/- t/2), bet abu kampai >= edge raidės viduje
        geoms = [o["geom"] for o in L]
        inner = [o.buffer(-edge) for o in geoms]

        def ends(cy):
            y0, y1 = cy - t_rail / 2, cy + t_rail / 2
            lx, rx = r["x0"] + r["t"] / 2, r["x1"] - r["t"] / 2
            def okx(x):
                return any(i.covers(Point(x, y0)) and i.covers(Point(x, y1)) for i in inner)
            if r["t"] > 0.35 * (r["xt"] - r["xb"]):
                # v276 (Rytis 2026-10-15, Securitas apskritimai: „rėmas nesivadovauja taisykle, per trumpas"): PILNAVIDURIAI
                #  elementai (apskritimai, blokai - štrichas >= 0,35 aukščio) - galai kuo arčiau krašto: nuo išorės į vidų,
                #  kol abu bėgelio kampai >= edge elemento viduje
                lx, rx = r["x0"] + edge, r["x1"] - edge
                while not okx(lx) and lx < r["x1"]: lx += 1
                while not okx(rx) and rx > r["x0"]: rx -= 1
            while not okx(lx) and lx < r["x0"] + r["t"] * 2: lx += 2
            while not okx(rx) and rx > r["x1"] - r["t"] * 2: rx -= 2
            # v83: galinis elementas be stiebo prie krašto (apskritimas) - ieškoti toliau, kol abu kampai raidėje
            while not okx(lx) and lx < r["x1"]: lx += 2
            while not okx(rx) and rx > r["x0"]: rx -= 2
            ok = okx(lx) and okx(rx) and rx - lx >= 3 * t_rail
            return lx, rx, ok
        for rr in r["rails"]:
            cy = rr["cy"]
            lx, rx, ok = ends(cy)
            if not ok:      # v183: galų vietos nerasta - ne apversti rėmo
                lx, rx = r["x0"] + r["t"] / 2, r["x1"] - r["t"] / 2
                log(f"  ! auto rėmas: bėgeliui y{cy:.0f} galų raidėje (kampai >= {edge} mm) nerasta - galai ties kraštinių raidžių centru, PATIKRINTI ranka")
            # v185 (Rytis 2026-10-13): kraštinė raidė be stiebo (e, c, o ...) turi STABILIAI tvirtintis - bėgelis tęsiamas iki
            #  raidės galo (pvz. „e" uodegytės galo, edge mm nuo krašto), net jei rėmas dalinai matysis
            lt_ = min(hs_, key=lambda o: o["bb"][0]); rt_ = max(hs_, key=lambda o: o["bb"][2])   # akcentai (kablelis, taškas) - ne kraštinė raidė
            if lx > (lt_["bb"][0] + lt_["bb"][2]) / 2:
                lx = lt_["bb"][0] + edge
                log(f"  auto rėmas: bėgelis y{cy:.0f} pratęstas iki kraštinės raidės galo kairėje (x{lx:.0f}) - stabilus tvirtinimas, rėmas dalinai matysis")
            if rx < (rt_["bb"][0] + rt_["bb"][2]) / 2:
                rx = rt_["bb"][2] - edge
                log(f"  auto rėmas: bėgelis y{cy:.0f} pratęstas iki kraštinės raidės galo dešinėje (x{rx:.0f}) - stabilus tvirtinimas, rėmas dalinai matysis")
            rr.update({"x0": lx, "x1": rx, "y0": cy - t_rail / 2, "y1": cy + t_rail / 2})
        lo_, hi_ = r["rails"][0]["cy"], r["rails"][1]["cy"]
        log(f"  auto rėmas: eilutė y{r['xb']:.0f}-{r['xt']:.0f} štrichas ~{r['t']:.0f} mm -> bėgelių ašys y{lo_:.0f} / y{hi_:.0f}, "
            f"galai {r['rails'][0]['x0']:.0f}..{r['rails'][0]['x1']:.0f}")
    # statmenys
    w_min = t_rail + 2 * (edge if v_edge is None else v_edge)    # v229: akrilinis rėmas - statmuo po štrichu, kraštas v_edge
    for r in rows:
        top, bot = r["rails"][0], r["rails"][1]
        r["stems"] = stems(r["letters"], top["y1"], bot["y0"], w_min)
        r["in"] = (top["y1"], bot["y0"])             # tarp bėgelių (y žemyn)
    vs = []
    # v79 (Rytis 2026-10-10): GALINIAI statmenys - VISADA abiejuose kiekvienos eilutės rėmo galuose. Statmens IŠORINĖ
    # plokštuma = bėgelio galas (stiebo centras), bėgeliai baigiasi ties statmens VIDINE plokštuma - horizontalus bėgis
    # visada vientisas, niekada nekertamas statmens. Jei viršutinės ir apatinės eilutės galai sutampa (<= end_tol) -
    # VIENAS vientisas galinis statmuo per abi reklamas (nepjaunamas).
    end_tol = 150
    for r in rows:
        r["xl"] = max(rr["x0"] for rr in r["rails"]); r["xr"] = min(rr["x1"] for rr in r["rails"])
    # v83 (Rytis 2026-10-10): PLATUS GALINIS ELEMENTAS (plati raidė, didelis kvadratas / apskritimas) - jei ausėlės juostoje
    # (bėgelio vidinėje pusėje) nuo bėgelio galo į vidų ištisai raidė >= wide_min (600 mm), ausėlei vietos nėra: rėmas
    # PRATĘSIAMAS IKI RAIDĖS GALO (abu bėgelio kampai >= edge raidės viduje, kuo arčiau krašto), o rėmo gale - ausėlė,
    # IŠSIKIŠUSI UŽ RAIDĖS (pažymima `out_l` / `out_r` - raidės krašto x; ausėlę deda braizyti_begeliai.py).
    wide_min = 600
    for r in (rows if len(rows) > 1 else []):        # v204: vienai eilutei bėgelių galai jau iki kraštinės raidės krašto
        geo = unary_union([o["geom"] for o in r["letters"]])
        inner = geo.buffer(-edge)
        for side in ("l", "r"):
            xe = r["xl"] if side == "l" else r["xr"]
            st_ = 1 if side == "l" else -1                       # kryptis į vidų
            # sąlyga (tik kai ausėlei TIKRAI nėra vietos): 1) ant abiejų bėgelių per end_window (300) nuo galo ausėlės juosta
            # ištisai po raide; 2) galinio statmens vidinė juosta tarp bėgelių ištisai po raide (ir eilutė galu nesijungia su
            # kaimyne - per tarpą einančiame statmenyje vieta yra); 3) galinis elementas SOLIDUS PLATUS - juostos ruožas >= 2 x štrichas
            gb = geo.buffer(0.5)
            nb = [q for q in rows if q is not r and abs(((q["xl"] if side == "l" else q["xr"]) - xe)) <= end_tol]
            hit = not nb
            wide_ = False
            for k, rr in enumerate(r["rails"]):
                if not hit:
                    break
                b0, b1 = (rr["y1"], rr["y1"] + t_rail) if k == 0 else (rr["y0"] - t_rail, rr["y0"])
                yb = (b0 + b1) / 2
                if not gb.covers(LineString([(xe, yb), (xe + st_ * 300, yb)])):
                    hit = False; break
                ix = gb.intersection(LineString([(xe - st_ * 3000, yb), (xe + st_ * 3000, yb)]))
                segs = [(min(c[0] for c in g_.coords), max(c[0] for c in g_.coords)) for g_ in getattr(ix, "geoms", [ix])
                        if not g_.is_empty and hasattr(g_, "coords")]
                seg = next(((a_, b_) for a_, b_ in segs if a_ - 1 <= xe <= b_ + 1), None)
                if seg and seg[1] - seg[0] >= 2 * r["t"]:
                    wide_ = True
            if hit:
                xv = xe + st_ * (t_rail + t_rail / 2)
                if not gb.covers(LineString([(xv, r["rails"][0]["y1"] + t_rail / 2), (xv, r["rails"][1]["y0"] - t_rail / 2)])):
                    hit = False
            hit = hit and wide_
            if not hit:
                continue
            ys = [(rr["y0"], rr["y1"]) for rr in r["rails"]]
            x = xe
            while True:                                          # į išorę, kol abu bėgelių kampai >= edge raidės viduje
                nx = x - st_ * 2
                if all(inner.covers(Point(nx, y0)) and inner.covers(Point(nx, y1)) for y0, y1 in ys):
                    x = nx
                else:
                    break
            ln = LineString([(x, (ys[0][0] + ys[0][1]) / 2), (x - st_ * 3000, (ys[0][0] + ys[0][1]) / 2)])
            ix = geo.intersection(ln)
            ex = min(p[0] for p in ix.coords) if side == "l" and not ix.is_empty and hasattr(ix, "coords") else None
            pts = [c for g_ in getattr(ix, "geoms", [ix]) for c in getattr(g_, "coords", [])]
            ex = (min(c[0] for c in pts) if side == "l" else max(c[0] for c in pts)) if pts else x - st_ * edge
            if side == "l": r["xl"] = x
            else: r["xr"] = x
            r["out_" + side] = ex
            log(f"  auto rėmas: platus galinis elementas {'kairėje' if side == 'l' else 'dešinėje'} - rėmas pratęstas {abs(x - xe):.0f} mm iki raidės galo (x{x:.0f}), ausėlė išsikiša už raidės (kraštas x{ex:.0f})")
    SINGLE = len(rows) == 1                              # v204: vienos eilutės rėmas - galiniai statmenys tik panaudojami
    for side in (("l", "r") if not SINGLE else ()):
        i = 0
        while i < len(rows):
            r = rows[i]
            xe = r["xl"] if side == "l" else r["xr"]
            grp = [r]
            while i + 1 < len(rows):
                nx = rows[i + 1]["xl"] if side == "l" else rows[i + 1]["xr"]
                if abs(nx - xe) <= end_tol:
                    grp.append(rows[i + 1]); i += 1
                    xe = max(xe, nx) if side == "l" else min(xe, nx)     # giliau stiebe - tinka abiem
                else:
                    break
            for q in grp:
                if side == "l": q["xl"] = xe
                else: q["xr"] = xe
            x0 = xe if side == "l" else xe - t_rail
            y0, y1 = grp[0]["rails"][0]["y0"], grp[-1]["rails"][1]["y1"]
            vs.append({"x0": x0, "x1": x0 + t_rail, "y0": y0, "y1": y1, "kind": "v", "auto": True, "end": True,
                       "len": y1 - y0, "poly": [(x0, y0), (x0 + t_rail, y0), (x0 + t_rail, y1), (x0, y1)]})
            log(f"  auto rėmas: galinis statmuo {'kairėje' if side == 'l' else 'dešinėje'} x{x0 + t_rail / 2:.0f}, {y1 - y0:.0f} mm"
                + (" - VIENTISAS per abi eilutes" if len(grp) > 1 else ""))
            i += 1
    # v82 (Rytis 2026-10-10, eskizas „pasiūlymas rėmui gale"): PAKOPINIS GALAS - jei eilučių galai nesutampa, trumpesnės
    # eilutės ARTIMESNIS kitai eilutei bėgelis (viršutinės - apatinis, apatinės - viršutinis) PRATĘSIAMAS iki ilgesnės eilutės
    # galinio statmens, o tas statmuo pratęsiamas per tarpą iki to bėgelio (vientisas). Trumpesnės eilutės galinis statmuo
    # baigiasi ant pratęsto bėgelio (bėgis nekertamas). Jungtis tarpe (v80) tada nereikalinga.
    for i in range(1, len(rows)):
        up_, dn_ = rows[i - 1], rows[i]
        for side in ("l", "r"):
            xu, xd = (up_["xl"], dn_["xl"]) if side == "l" else (up_["xr"], dn_["xr"])
            if abs(xu - xd) <= end_tol:
                continue
            up_longer = (xu < xd) if side == "l" else (xu > xd)
            L_, S_ = (up_, dn_) if up_longer else (dn_, up_)
            xL = xu if up_longer else xd
            xS = xd if up_longer else xu
            frail = S_["rails"][0] if up_longer else S_["rails"][1]       # trumpesnės eilutės bėgelis, artimesnis ilgesnei
            frail["ext_" + side] = xL                                      # bėgelio galas - iki ilgesnės eilutės statmens
            vL = next(v for v in vs if v.get("end") and abs((v["x0"] if side == "l" else v["x1"]) - xL) < 2
                      and v["y0"] <= L_["rails"][0]["y0"] + 1 and v["y1"] >= L_["rails"][1]["y1"] - 1)
            vS = next(v for v in vs if v.get("end") and abs((v["x0"] if side == "l" else v["x1"]) - xS) < 2
                      and v["y0"] <= S_["rails"][0]["y0"] + 1 and v["y1"] >= S_["rails"][1]["y1"] - 1)
            if up_longer:                                                  # ilgesnė viršuje: statmuo žemyn iki S viršutinio bėgelio apačios
                vL["y1"] = frail["y1"]; vS["y0"] = frail["y1"]
            else:                                                          # ilgesnė apačioje: statmuo aukštyn iki S apatinio bėgelio viršaus
                vL["y0"] = frail["y0"]; vS["y1"] = frail["y0"]
            for v in (vL, vS):
                v["len"] = v["y1"] - v["y0"]; v["poly"] = [(v["x0"], v["y0"]), (v["x1"], v["y0"]), (v["x1"], v["y1"]), (v["x0"], v["y1"])]
            vL["step"] = True
            log(f"  auto rėmas: pakopinis galas {'kairėje' if side == 'l' else 'dešinėje'} - bėgelis y{(frail['y0'] + frail['y1']) / 2:.0f} pratęstas "
                f"{abs(xL - xS):.0f} mm iki galinio statmens x{(vL['x0'] + vL['x1']) / 2:.0f}, statmuo {vL['len']:.0f} mm vientisas")
    # v80 (Rytis 2026-10-10: „apatinė reklama kabo tik ant dviejų statmenų"): eilutės sujungiamos ABIEJUOSE galuose -
    # jei galai nesutampa (vientiso galinio nėra), prie trumpesnės eilutės galo dedamas JUNGIAMASIS statmuo per bendrą abiejų
    # eilučių stiebą (artimiausias galui, iki 1000 mm į vidų); jis pjaunamas tarp bėgelių (kaip tarpinis).
    for i in range(1, len(rows)):
        up_, dn_ = rows[i - 1], rows[i]
        for side in ("l", "r"):
            if any(v.get("end") and v["y0"] <= up_["rails"][1]["y1"] + 1 and v["y1"] >= dn_["rails"][0]["y0"] - 1
                   and ((side == "l" and v["x0"] < min(up_["xl"], dn_["xl"]) + 200) or (side == "r" and v["x1"] > max(up_["xr"], dn_["xr"]) - 200))
                   for v in vs):
                continue
            xe = max(up_["xl"], dn_["xl"]) if side == "l" else min(up_["xr"], dn_["xr"])
            best = None
            for a, b, _ in up_["stems"]:
                for c, d, _ in dn_["stems"]:
                    lo_, hi_ = max(a, c), min(b, d)
                    if hi_ - lo_ < w_min:
                        continue
                    xc = (lo_ + hi_) / 2
                    dist = (xc - xe) if side == "l" else (xe - xc)
                    if t_rail + 50 <= dist <= 1000 and (best is None or dist < best[0]):
                        best = (dist, xc)
            if best is None:
                # bendro stiebo nėra - jungtis TIK TARPE tarp eilučių (nuo viršutinės apatinio bėgelio iki apatinės viršutinio),
                # galinio statmens linijos tęsinys (trumpesnės eilutės galas), jei ten yra kitos eilutės bėgelis
                ends_ = [v for v in vs if v.get("end") and (
                    (side == "l" and abs(v["x0"] - xe) < 2) or (side == "r" and abs(v["x1"] - xe) < 2))]
                if not ends_:
                    log(f"  ! auto rėmas: {'kairėje' if side == 'l' else 'dešinėje'} eilutės nesujungtos - spręsti ranka"); continue
                v = ends_[0]; xc = (v["x0"] + v["x1"]) / 2
                y0, y1 = up_["rails"][1]["y1"], dn_["rails"][0]["y0"]
                vs.append({"x0": xc - t_rail / 2, "x1": xc + t_rail / 2, "y0": y0, "y1": y1, "kind": "v", "auto": True, "conn": True,
                           "len": y1 - y0, "poly": [(xc - t_rail / 2, y0), (xc + t_rail / 2, y0), (xc + t_rail / 2, y1), (xc - t_rail / 2, y1)]})
                log(f"  auto rėmas: jungiamasis statmuo {'kairėje' if side == 'l' else 'dešinėje'} x{xc:.0f} tarpe tarp eilučių ({y1 - y0:.0f} mm, galinio statmens tęsinys)")
                continue
            xc = best[1]; y0, y1 = up_["in"][0], dn_["in"][1]
            vs.append({"x0": xc - t_rail / 2, "x1": xc + t_rail / 2, "y0": y0, "y1": y1, "kind": "v", "auto": True, "conn": True,
                       "len": y1 - y0, "poly": [(xc - t_rail / 2, y0), (xc + t_rail / 2, y0), (xc + t_rail / 2, y1), (xc - t_rail / 2, y1)]})
            log(f"  auto rėmas: jungiamasis statmuo prie {'kairio' if side == 'l' else 'dešinio'} galo x{xc:.0f} (per abi eilutes, pjaunamas tarp bėgelių)")
    # v191 (Rytis 2026-10-13: „rėmas niekada nedaromas, kai pirma ir paskutinė statmena dedasi prie rėmo; statmenos visada
    #  dedasi tarp apatinės ir viršutinės profilio dalių, niekada iš galų"): bėgeliai - per VISĄ rėmo ilgį (iki statmens išorinės
    #  plokštumos), VISI statmenys (ir galiniai) - įvirinti TARP bėgelių (pjaunami žemiau)
    # v192 (Rytis 2026-10-13: „statmuo nuo apatinio bėgelio tik po kableliu, o ne pratęstas viršutinis"): smulkus elementas
    #  už rėmo galo (kablelis, taškas) - ARTIMIAUSIAS jam bėgelis (kablelis - apatinis) tęsiamas iki elemento, o nuo jo - LAIKIKLIS
    #  (statmuo) per elementą (abu kampai >= edge elemento viduje, kuo ilgesnis); kitas bėgelis ir galinis statmuo - kaip buvo
    for r in rows:
        for o in r["letters"]:
            if o["bb"][3] - o["bb"][1] >= 0.5 * r["h"]:
                continue
            side_ = "r" if o["bb"][0] >= r["xr"] - 1 else ("l" if o["bb"][2] <= r["xl"] + 1 else None)
            if not side_:
                continue
            inner_ = o["geom"].buffer(-edge)
            if inner_.is_empty:
                continue
            ocy = (o["bb"][1] + o["bb"][3]) / 2
            top_r, bot_r = r["rails"][0], r["rails"][1]
            down = abs(ocy - (bot_r["y0"] + bot_r["y1"]) / 2) <= abs(ocy - (top_r["y0"] + top_r["y1"]) / 2)
            rr = bot_r if down else top_r
            yr = rr["y1"] if down else rr["y0"]                    # bėgelio plokštuma elemento pusėje
            # v193 (Rytis 2026-10-13, eskizas): laikiklis per elemento VIDURĮ (ne kur ilgiausias), bėgelis - per visą elemento
            #  plotį (T forma: bėgelio galas iki elemento išorinio krašto - edge), ausėlė - prie laikiklio (braizyti_begeliai)
            from shapely.geometry import box as _box
            _below = o["geom"].intersection(_box(o["bb"][0] - 1, yr, o["bb"][2] + 1, o["bb"][3] + 1)) if down else \
                o["geom"].intersection(_box(o["bb"][0] - 1, o["bb"][1] - 1, o["bb"][2] + 1, yr))
            _cx = _below.centroid.x if not _below.is_empty else (o["bb"][0] + o["bb"][2]) / 2
            best = None
            for xc in sorted(range(int(o["bb"][0] + t_rail / 2), int(o["bb"][2] - t_rail / 2) + 1, 2), key=lambda x: abs(x - _cx)):
                ys_ = range(int(o["bb"][3]), int(yr), -2) if down else range(int(o["bb"][1]), int(yr) + 1, 2)
                ye = next((y for y in ys_ if inner_.covers(Point(xc - t_rail / 2, y)) and inner_.covers(Point(xc + t_rail / 2, y))), None)
                if ye is None:
                    continue
                L_ = (ye - yr) if down else (yr - ye)
                if L_ >= 0.5 * (o["bb"][3] - o["bb"][1]) * 0.6:      # pirmoji vieta arčiausiai vidurio su pakankamu ilgiu
                    best = (L_, xc, ye); break
                if L_ > 0 and (best is None or L_ > best[0]):
                    best = (L_, xc, ye)
            if best is None:
                log(f"  ! auto rėmas: elementui x{(o['bb'][0] + o['bb'][2]) / 2:.0f} laikiklis netelpa - spręsti ranka"); continue
            L_, xc, ye = best
            # bėgelio galas - per elemento plotį iki išorinio krašto (- edge) bėgelio ašies aukštyje, ne trumpiau už laikiklį
            _ix = o["geom"].intersection(LineString([(o["bb"][0] - 1, (rr["y0"] + rr["y1"]) / 2), (o["bb"][2] + 1, (rr["y0"] + rr["y1"]) / 2)]))
            _xs = [c_[0] for g_ in getattr(_ix, "geoms", [_ix]) for c_ in getattr(g_, "coords", [])]
            if side_ == "r":
                rr["ext_r"] = max(xc + t_rail / 2, (max(_xs) - edge) if _xs else 0)
            else:
                rr["ext_l"] = min(xc - t_rail / 2, (min(_xs) + edge) if _xs else 1e9)
            y0, y1 = (yr, ye) if down else (ye, yr)
            vs.append({"x0": xc - t_rail / 2, "x1": xc + t_rail / 2, "y0": y0, "y1": y1, "kind": "v", "auto": True, "acc": True,
                       "ext_holder": {"side": side_, "rail_y": (rr["y0"] + rr["y1"]) / 2, "down": down,
                                      "elem_x": (o["bb"][0], o["bb"][2])},
                       "len": y1 - y0, "poly": [(xc - t_rail / 2, y0), (xc + t_rail / 2, y0), (xc + t_rail / 2, y1), (xc - t_rail / 2, y1)]})
            log(f"  auto rėmas: {'apatinis' if down else 'viršutinis'} bėgelis tęsiamas iki elemento, laikiklis x{xc:.0f} {L_:.0f} mm "
                f"{'žemyn' if down else 'aukštyn'} per elementą (stabilus tvirtinimas)")
    for r in rows:
        for rr in r["rails"]:
            if SINGLE:                                  # v204: kiekvienas bėgelis - savo galai (abu kampai >= edge kraštinėje raidėje)
                rr["x0"], rr["x1"] = rr.get("ext_l", rr["x0"]), rr.get("ext_r", rr["x1"])
            else:
                rr["x0"], rr["x1"] = rr.get("ext_l", r["xl"]), rr.get("ext_r", r["xr"])
    hs = []
    for r in rows:
        for rr in r["rails"]:
            hs.append({"x0": rr["x0"], "y0": rr["y0"], "x1": rr["x1"], "y1": rr["y1"], "kind": "h", "auto": True,
                       "out_l": r.get("out_l") if "ext_l" not in rr else None, "out_r": r.get("out_r") if "ext_r" not in rr else None,
                       "stroke": r["t"], "len": rr["x1"] - rr["x0"],
                       "poly": [(rr["x0"], rr["y0"]), (rr["x1"], rr["y0"]), (rr["x1"], rr["y1"]), (rr["x0"], rr["y1"])]})
    if SINGLE:
        vs += single_verticals(rows[0], t_rail, edge if v_edge is None else v_edge, pitch, pitch_heavy, heavy_m2_m, log,
                               every_letter=every_letter, ends_only=ends_only)
    # tarpiniai statmenys - per stiebus; per abi eilutes, jei stiebas sutampa (pjaunami tarp bėgelių - bėgis vientisas)
    for i, r in enumerate(rows if not SINGLE else []):
        st = [s for s in r["stems"] if r["xl"] + t_rail + 300 < (s[0] + s[1]) / 2 < r["xr"] - t_rail - 300]
        L = r["xr"] - r["xl"]
        # v87 (Rytis 2026-10-10): rėmas - KONSTRUKCIJA, statmenų kiekis pagal iškabos dydį ir svorį: statmenų (su galiniais)
        # ceil(L / žingsnis) + 1; žingsnis 2500 mm, MASYVIOMS raidėms (raidžių plotas >= 0,5 m² bėgiminiam metrui) - 2000 mm
        # (BB: LIETUVA 7,05 m masyvios -> 5, TĖVYNE MŪSŲ 7,35 m -> 4; ~7 m iškaba paprastai 4 statmenys)
        _a = sum(o["geom"].area for o in r["letters"]) / 1e6
        _m2m = _a / max(L / 1000, 1e-6)
        _p = pitch_heavy if _m2m >= heavy_m2_m else pitch
        n_mid = max(0, math.ceil(L / _p) - 1)
        if ends_only:                                    # v337: tik galuose (+ 1 per vidurį, kai eilutė > 4 m)
            n_mid = 1 if L > ENDS_MID_L else 0
            log(f"  auto rėmas: eilutė y{r['xb']:.0f} - L {L:.0f} -> {n_mid + 2} statmenys (galuose" + (" + vidurys)" if n_mid else ")"))
        else:
            log(f"  auto rėmas: eilutė y{r['xb']:.0f} - {_m2m:.2f} m²/m ({'masyvios' if _p == pitch_heavy else 'įprastos'}), žingsnis {_p} -> {n_mid + 2} statmenys su galiniais")
        up = rows[i - 1] if i > 0 else None

        def common(s):
            if not up: return None
            for a, b, _ in up["stems"]:
                lo_, hi_ = max(a, s[0]), min(b, s[1])
                if hi_ - lo_ >= w_min: return (lo_, hi_)
            return None
        down = rows[i + 1] if i + 1 < len(rows) else None

        def common_down(s):                              # bendras stiebas su apatine eilute (statmuo per abi daromas iš karto)
            if not down: return None
            for a, b, _ in down["stems"]:
                lo_, hi_ = max(a, s[0]), min(b, s[1])
                if hi_ - lo_ >= w_min: return (lo_, hi_)
            return None
        taken = [(v["x0"] + v["x1"]) / 2 for v in vs if not v.get("end") and v["y1"] >= r["in"][0] and v["y0"] <= r["in"][1]]
        st = [s for s in st if all(abs((s[0] + s[1]) / 2 - t) > 300 for t in taken)]
        n_mid = max(0, n_mid - len(taken))
        if n_mid and not st:
            log(f"  ! auto rėmas: eilutėje y{r['xb']:.0f} tarpiniams statmenims stiebų nerasta - spręsti ranka")
        targets = [r["xl"] + L * (k + 1) / (n_mid + 1) for k in range(n_mid)]
        chosen = []
        for tx in targets:
            cand = [s for s in st if all(abs((s[0] + s[1]) / 2 - (c[0] + c[1]) / 2) > 300 for c in chosen)]
            if not cand: break
            chosen.append(min(cand, key=lambda s: abs((s[0] + s[1]) / 2 - tx) - (1500 if (common(s) or common_down(s)) else 0)))
        for s in sorted(chosen):
            c = common(s)
            cd = common_down(s)
            if c:
                xc = (c[0] + c[1]) / 2; y0, y1 = up["in"][0], r["in"][1]; kind = "per abi eilutes"
            elif cd:
                xc = (cd[0] + cd[1]) / 2; y0, y1 = r["in"][0], down["in"][1]; kind = "per abi eilutes (su apatine)"
            else:
                xc = (s[0] + s[1]) / 2; y1 = r["in"][1]
                if up and up["rails"][1]["x0"] + t_rail <= xc <= up["rails"][1]["x1"] - t_rail:
                    y0, kind = up["rails"][1]["y1"], "iki viršutinės eilutės bėgelio"
                else:
                    y0, kind = r["in"][0], "eilutėje"
            vs.append({"x0": xc - t_rail / 2, "x1": xc + t_rail / 2, "y0": y0, "y1": y1, "kind": "v", "auto": True,
                       "len": y1 - y0, "poly": [(xc - t_rail / 2, y0), (xc + t_rail / 2, y0), (xc + t_rail / 2, y1), (xc - t_rail / 2, y1)]})
            log(f"  auto rėmas: tarpinis statmuo x{xc:.0f} ({kind}, {y1 - y0:.0f} mm)")
    # v77 (Rytis 2026-10-10): akcentai (Ė taškas, Ū brūkšnys, i taškas) kabo ore - jiems LAIKIKLIS nuo eilutės
    # viršutinio bėgelio viršutinės plokštumos iki akcento (abu kampai >= edge akcento viduje), x - akcento centras;
    # per jį eina ir LED maitinimas. Akcentas po eilute (Ą / Ų uodega - atskiras elementas) - nuo apatinio bėgelio žemyn.
    for r in rows:
        top, bot = r["rails"][0], r["rails"][1]
        for o in r["letters"]:
            if o["bb"][3] - o["bb"][1] >= 0.5 * r["h"]:
                continue
            xc = (o["bb"][0] + o["bb"][2]) / 2
            inner = o["geom"].buffer(-edge)
            above = o["bb"][3] <= top["y0"] + 1
            below = o["bb"][1] >= bot["y1"] - 1
            if not (above or below) or inner.is_empty:
                continue
            ys_ = range(int(o["bb"][1]), int(o["bb"][3]) + 1) if above else range(int(o["bb"][3]), int(o["bb"][1]) - 1, -1)
            ye = next((y for y in ys_ if inner.covers(Point(xc - t_rail / 2, y)) and inner.covers(Point(xc + t_rail / 2, y))), None)
            if ye is None:
                log(f"  ! auto rėmas: akcentui x{xc:.0f} laikiklis netelpa (per siauras) - spręsti ranka"); continue
            y0, y1 = (ye, top["y0"]) if above else (bot["y1"], ye)
            vs.append({"x0": xc - t_rail / 2, "x1": xc + t_rail / 2, "y0": y0, "y1": y1, "kind": "v", "auto": True,
                       "len": y1 - y0, "acc": True,
                       "poly": [(xc - t_rail / 2, y0), (xc + t_rail / 2, y0), (xc + t_rail / 2, y1), (xc - t_rail / 2, y1)]})
            log(f"  auto rėmas: akcento laikiklis x{xc:.0f}, {y1 - y0:.0f} mm ({'virš' if above else 'po'} eilute)")
    # viršutinės eilutės statmuo, sutampantis su apatinės „per abi" - nedubliuoti
    out = []
    for v in vs:      # eilutės statmuo šalia (<= 400 mm) ilgesnio, dengiančio jo aukštį - perteklinis (L stiebas: 259 ir 320 per abi)
        if any(abs(((o["x0"] + o["x1"]) / 2) - ((v["x0"] + v["x1"]) / 2)) < 400 and o["y0"] <= v["y0"] + 1 and o["y1"] >= v["y1"] - 1
               and o["len"] > v["len"] and not v.get("acc") for o in vs if o is not v):
            log(f"  auto rėmas: statmuo x{(v['x0'] + v['x1']) / 2:.0f} ({v['len']:.0f}) šalinamas - šalia ilgesnio")
            continue
        out.append(v)
    # v78 (Rytis 2026-10-10) - VIRINIMO / SURINKIMO TVARKA: horizontalūs bėgeliai ištisiniai, statmenys pjaunami TARP jų
    # (tarpinis per abi eilutes einantis statmuo = 3 dalys vienoje linijoje: eilutėje, tarpe, eilutėje); galiniai statmenys
    # už bėgelių galų - nepjaunami (vientisi per abi eilutes, kai galai sutampa).
    segs = []
    for v in out:
        if v.get("kind") == "d":                       # įstrižas - jau tarp bėgelių
            segs.append(v); continue
        cuts = sorted((h["y0"], h["y1"]) for h in hs if h["y0"] >= v["y0"] - 1 and h["y1"] <= v["y1"] + 1
                      and h["x0"] - 1 <= (v["x0"] + v["x1"]) / 2 <= h["x1"] + 1)
        ya = v["y0"]
        parts = []
        for c0, c1 in cuts:
            parts.append((ya, c0)); ya = c1
        parts.append((ya, v["y1"]))
        for y0, y1 in parts:
            if y1 - y0 < 5:
                continue
            seg = dict(v); seg.update({"y0": y0, "y1": y1, "len": y1 - y0,
                                       "poly": [(v["x0"], y0), (v["x1"], y0), (v["x1"], y1), (v["x0"], y1)]})
            segs.append(seg)
        if len(parts) > 1:
            log(f"  auto rėmas: statmuo x{(v['x0'] + v['x1']) / 2:.0f} pjaunamas tarp bėgelių: " + " + ".join(f"{b - a:.0f}" for a, b in parts if b - a >= 5))
    out = segs
    return hs, out
