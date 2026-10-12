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
    rows = []
    for o in sorted(letters, key=lambda o: (o["bb"][1] + o["bb"][3])):      # y ŽEMYN (skripto koordinatės): viršutinė eilutė - mažesnis y
        cy = (o["bb"][1] + o["bb"][3]) / 2
        for r in rows:
            if abs(r["cy"] - cy) < 0.5 * r["h"]:
                r["letters"].append(o); break
        else:
            rows.append({"cy": cy, "h": o["bb"][3] - o["bb"][1], "letters": [o]})
    rows.sort(key=lambda r: r["cy"])                 # viršutinė (mažesnis y) pirma
    hmax = max(r["h"] for r in rows)
    big = [r for r in rows if r["h"] >= 0.5 * hmax]
    for r in rows:                                   # akcentai (Ė taškas, Ū brūkšnys, i taškai) - prie artimiausios eilutės
        if r["h"] < 0.5 * hmax:
            host = min(big, key=lambda b: abs(b["cy"] - r["cy"]))
            host["letters"] += r["letters"]
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


def build(g, t_rail, edge=10, pitch=2500, pitch_heavy=2000, heavy_m2_m=0.5, log=print):
    """g - grupė (letters su geom / bb); grąžina (hs, vs) bėgelių dict'ų sąrašus (x0, y0, x1, y1, kind, len, poly, auto)"""
    rows = rows_of(g["letters"])
    for r in rows:
        L = r["letters"]
        hs_ = [o for o in L if (o["bb"][3] - o["bb"][1]) >= 0.6 * r["h"]]
        r["xb"] = _median([o["bb"][1] for o in hs_]); r["xt"] = _median([o["bb"][3] for o in hs_])
        r["t"] = _median([stroke_t(o["geom"]) for o in hs_])
        r["x0"] = min(o["bb"][0] for o in L); r["x1"] = max(o["bb"][2] for o in L)
        lo_ = r["xb"] + r["t"] / 2; hi_ = r["xt"] - r["t"] / 2
        r["rails"] = [{"cy": lo_}, {"cy": hi_}]      # [0] - viršutinis (mažesnis y), [1] - apatinis
        # galai - kraštinių raidžių stiebo viduryje (kraštas +/- t/2), bet abu kampai >= edge raidės viduje
        geoms = [o["geom"] for o in L]
        for rr in r["rails"]:
            cy = rr["cy"]; y0, y1 = cy - t_rail / 2, cy + t_rail / 2
            lx, rx = r["x0"] + r["t"] / 2, r["x1"] - r["t"] / 2
            inner = [o.buffer(-edge) for o in geoms]
            def okx(x):
                return any(i.covers(Point(x, y0)) and i.covers(Point(x, y1)) for i in inner)
            while not okx(lx) and lx < r["x0"] + r["t"] * 2: lx += 2
            while not okx(rx) and rx > r["x1"] - r["t"] * 2: rx -= 2
            # v83: galinis elementas be stiebo prie krašto (apskritimas) - ieškoti toliau, kol abu kampai raidėje
            while not okx(lx) and lx < r["x1"]: lx += 2
            while not okx(rx) and rx > r["x0"]: rx -= 2
            rr.update({"x0": lx, "x1": rx, "y0": y0, "y1": y1})
        log(f"  auto rėmas: eilutė y{r['xb']:.0f}-{r['xt']:.0f} štrichas ~{r['t']:.0f} mm -> bėgelių ašys y{lo_:.0f} / y{hi_:.0f}, "
            f"galai {r['rails'][0]['x0']:.0f}..{r['rails'][0]['x1']:.0f}")
    # statmenys
    w_min = t_rail + 2 * edge
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
    for r in rows:
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
    for side in ("l", "r"):
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
    for r in rows:                                           # bėgeliai - iki statmenų vidinės plokštumos
        for rr in r["rails"]:
            rr["x0"], rr["x1"] = rr.get("ext_l", r["xl"]) + t_rail, rr.get("ext_r", r["xr"]) - t_rail
    hs = []
    for r in rows:
        for rr in r["rails"]:
            hs.append({"x0": rr["x0"], "y0": rr["y0"], "x1": rr["x1"], "y1": rr["y1"], "kind": "h", "auto": True,
                       "out_l": r.get("out_l") if "ext_l" not in rr else None, "out_r": r.get("out_r") if "ext_r" not in rr else None,
                       "stroke": r["t"], "len": rr["x1"] - rr["x0"],
                       "poly": [(rr["x0"], rr["y0"]), (rr["x1"], rr["y0"]), (rr["x1"], rr["y1"]), (rr["x0"], rr["y1"])]})
    # tarpiniai statmenys - per stiebus; per abi eilutes, jei stiebas sutampa (pjaunami tarp bėgelių - bėgis vientisas)
    for i, r in enumerate(rows):
        st = [s for s in r["stems"] if r["xl"] + t_rail + 300 < (s[0] + s[1]) / 2 < r["xr"] - t_rail - 300]
        L = r["xr"] - r["xl"]
        # v87 (Rytis 2026-10-10): rėmas - KONSTRUKCIJA, statmenų kiekis pagal iškabos dydį ir svorį: statmenų (su galiniais)
        # ceil(L / žingsnis) + 1; žingsnis 2500 mm, MASYVIOMS raidėms (raidžių plotas >= 0,5 m² bėgiminiam metrui) - 2000 mm
        # (BB: LIETUVA 7,05 m masyvios -> 5, TĖVYNE MŪSŲ 7,35 m -> 4; ~7 m iškaba paprastai 4 statmenys)
        _a = sum(o["geom"].area for o in r["letters"]) / 1e6
        _m2m = _a / max(L / 1000, 1e-6)
        _p = pitch_heavy if _m2m >= heavy_m2_m else pitch
        n_mid = max(0, math.ceil(L / _p) - 1)
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
        cuts = sorted((h["y0"], h["y1"]) for h in hs if h["y0"] > v["y0"] + 1 and h["y1"] < v["y1"] - 1
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
