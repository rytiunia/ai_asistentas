#!/usr/bin/env python3
"""medziagos.py - tiekėjų medžiagų formatai ir 6 m profilių taisyklė (v73, Rytis 2026-10-10).

Duomenys - `assets/medziagos.json` (keisti TIK ten): profilių strypas 6000 mm (Heliopolis: „Profilių ilgis - 6 metrai"),
pjūklo prapjova, galo atsarga, lakštų formatai (PMMA, PVC, AKP, Alu, PC, PS).

Funkcijos:
  cfg()                                   - profilių parametrai (stock, kerf, end, trim_max, trim_step)
  nest_bars(lengths, stock, kerf, end)    - FFD: kiek 6 m strypų reikia ir kas į kurį strypą pjaunama
  bars_text(bars, stock)                  - „2 x 6 m: [2998+2998] [600+600+600]"
  trim_to_stock(fixed, adj, cfg)          - 6 m taisyklė: mažiausias horizontalių bėgelių patrumpinimas, po kurio
                                            rėmas užima vienu strypu mažiau; None - nėra ką trumpinti / neverta
  sheet_fit(w, h, material, thk)          - ar detalė telpa į tiekėjo lakštą (su parašte), kokie formatai tinka

  is_standard_profile(m)                  - v161: rėmo profilių standartas 20/30/40/60/80 x 2
  profile_check(text, kind)               - v114: ar profilis yra LT tiekėjų sandėlyje (Heliopolis, Lankava, Proplastik)
                                            + artimiausi variantai; profile_warn() - perspėjimas konsolei
  sheet_check(material, thk, ral)         - v114: ar lakštas / AKP spalva yra pas tiekėjus

CLI: python3 medziagos.py profilis "U 30x30x2" "Alu vamzdis 25x25x2" "Z 30x30x30x2"
     python3 medziagos.py lakstas akp 3 9005
     python3 medziagos.py bars 3025 3025 600 600 [--stock 6000 --kerf 3]
     python3 medziagos.py sheet 2400 1200 alu [2]
"""
import json
import math
import re
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_JSON = os.path.join(_HERE, "..", "assets", "medziagos.json")


def data():
    with open(_JSON, encoding="utf-8") as f:
        return json.load(f)


def cfg(over=None):
    """profilių parametrai iš medziagos.json + spec `"stock": {...}` perrašymai (bar_mm, kerf_mm, end_mm, trim_max_mm, trim_step_mm, enabled)"""
    p = data()["profiliai"]
    c = {"stock": float(p.get("strypas_mm", 6000)), "kerf": float(p.get("prapjova_mm", 3)),
         "end": float(p.get("galo_atsarga_mm", 0)), "trim_max": float(p.get("trim_max_mm", 100)),
         "trim_step": float(p.get("trim_step_mm", 5)), "enabled": True}
    o = over or {}
    if "bar_mm" in o: c["stock"] = float(o["bar_mm"])
    if "kerf_mm" in o: c["kerf"] = float(o["kerf_mm"])
    if "end_mm" in o: c["end"] = float(o["end_mm"])
    if "trim_max_mm" in o: c["trim_max"] = float(o["trim_max_mm"])
    if "trim_step_mm" in o: c["trim_step"] = float(o["trim_step_mm"])
    if "enabled" in o: c["enabled"] = bool(o["enabled"])
    return c


# ------------------------------------------------------------------ strypai
def _fits(bar, p, stock, kerf, end):
    """į strypą su dalimis `bar` telpa dar `p`: sum + p + kerf * (n dalių - 1) + end <= stock"""
    return sum(bar) + p + kerf * len(bar) + end <= stock + 1e-6


LAST_SPLITS = {}   # v90: {ilgis: (a, b)} - paskutinio nest_bars ilgų dalių padalijimas


def _ffd(pieces, stock, kerf, end):
    bars = []
    for p in sorted(pieces, reverse=True):
        for b in bars:
            if _fits(b, p, stock, kerf, end):
                b.append(p)
                break
        else:
            bars.append([p])
    return bars


def _score(bars, stock):
    """mažiau strypų; tada - kuo didesnis vienas likutis (tinkamas panaudoti), ne smulkūs gabalai"""
    left = [stock - sum(b) for b in bars]
    return (len(bars), -max(left) if left else 0)


def nest_bars(lengths, stock=6000.0, kerf=3.0, end=0.0, step=50.0):
    """First-Fit-Decreasing. Grąžina sąrašą strypų (kiekvienas - dalių ilgių sąrašas, ilgiausios pirmos).
    v90 (Rytis 2026-10-11): dalis <= strypo ilgio NIEKADA nedalijama (horizontalaus bėgelio nevirinti iš dalių vien
    dėl taupymo). Dalis ilgesnė už strypą jungiama iš 2 (3 ...) dalių; SANDŪROS VIETA LAISVA - dalių ilgiai parenkami
    taip, kad liktų MAŽIAUSIAI ATLIEKŲ (mažiau strypų, tada didesnis vientisas likutis). Padalijimas - LAST_SPLITS."""
    global LAST_SPLITS
    LAST_SPLITS = {}
    usable = stock - end
    short, longs = [], []
    for v in lengths:
        v = float(v or 0)
        if v <= 0:
            continue
        (longs if v > usable + 1e-6 else short).append(v)
    pieces = list(short)
    for L in sorted(longs, reverse=True):
        n = int(math.ceil(L / usable))                    # mažiausias dalių skaičius
        best = None
        a = usable
        while a >= L / n - 1e-6:                          # pirmos dalies ilgis: nuo pilno strypo iki lygių dalių
            rest = L - a
            parts = [a] + ([rest / (n - 1)] * (n - 1) if n > 1 else [])
            if all(x <= usable + 1e-6 for x in parts):
                sc = _score(_ffd(pieces + parts, stock, kerf, end), stock)
                if best is None or sc < best[0]:
                    best = (sc, parts)
            a -= step
        parts = best[1] if best else [usable, L - usable]
        LAST_SPLITS[L] = tuple(round(x) for x in parts)
        pieces += parts
    return _ffd(pieces, stock, kerf, end)


def bars_text(bars, stock=6000.0):
    if not bars:
        return "-"
    return f"{len(bars)} x {stock / 1000:g} m: " + " ".join("[" + "+".join(f"{v:.0f}" for v in b) + "]" for b in bars)


def bars_waste(bars, stock=6000.0):
    """atlieka (mm); dalis ilgesnė už strypą - atlieka 0 (jungiama iš 2 - perspėjama atskirai)"""
    return sum(max(0.0, stock - sum(b)) for b in bars)


def _split(d, sl, sr):
    """patrumpinimą d padalinti galams: simetriškai, trūkstant - į kitą galą; grąžina (l, r)"""
    l_ = min(math.ceil(d / 2), sl)
    r_ = min(d - l_, sr)
    if l_ + r_ < d:
        l_ = min(d - r_, sl)
    return float(l_), float(r_)


def trim_to_stock(fixed, adj, c, qty=1):
    """6 m taisyklė (Rytis 2026-10-10): rėmas, kuris sudėliotas gaunasi pvz. 6,05 m (netelpa į 6 m strypą), trumpinamas,
    kad tilptų - bet TIK tiek, kiek leidžia kitos taisyklės (galo laisvumas `slack` iš geometrijos).
    fixed - nekeičiamų dalių ilgiai (statmenys, vertikalūs bėgeliai, detalizacijos rėmas, kitų grupių dalys);
    adj   - [{"id", "len", "slack": (kairė, dešinė)}] horizontalūs bėgeliai, kuriuos galima trumpinti;
    c     - cfg(); qty - užsakymo kiekis (v98: strypai planuojami VISAM užsakymui - 2 vnt. po 2 x 3,05 m bėgelius
            be patrumpinimo užimtų 4 strypus, patrumpinus iki 2 x 2995 - 2). Grąžina {"d": d, "trims": {id: (l, r)}, "bars0": n0, "bars": n, "plan": bars} arba None."""
    stock, kerf, end = c["stock"], c["kerf"], c["end"]
    fixed = [float(v) for v in fixed if v and v > 0] * max(1, int(qty))
    _q = max(1, int(qty))
    if not adj:
        return None
    base = nest_bars(fixed + [a["len"] for a in adj] * _q, stock, kerf, end)
    n0 = len(base)
    tot = sum(fixed) + sum(a["len"] for a in adj) * _q
    if n0 <= 1 or n0 <= math.ceil(tot / stock):        # ir idealiai sudėjus mažiau strypų nebūtų
        if n0 <= 1:
            return None
    step = max(1.0, c["trim_step"])
    d = step
    found = None
    cands = []
    while d <= c["trim_max"] + 1e-6:
        trims = {}
        lens = []
        for a in adj:
            sl, sr = a["slack"]
            l_, r_ = _split(min(d, sl + sr), sl, sr)
            trims[a["id"]] = (l_, r_)
            lens.append(a["len"] - l_ - r_)
        sc = _score(nest_bars(fixed + lens * _q, stock, kerf, end), stock)
        if sc[0] < n0:
            cands.append((d, trims, sc))
        if all(a["slack"][0] + a["slack"][1] <= d for a in adj):     # daugiau trumpinti negalima
            break
        d += step
    # v98: mažiausiai strypų ir MAŽIAUSIAS patrumpinimas; didesnis trumpinimas - tik jei vientisas likutis padidėja
    #  >= 500 mm (pvz. 2 x ~3 m bėgeliai poromis, statmenys atskirame strype - likutis tinkamas panaudoti)
    if cands:
        bmin = min(c_[2][0] for c_ in cands)
        cb = [c_ for c_ in cands if c_[2][0] == bmin]
        found = cb[0]
        for c_ in cb[1:]:
            if -c_[2][1] >= -found[2][1] + 500:
                found = c_
                break
    if not found:
        return None
    d, trims, _ = found
    # mažiausias rinkinys: bėgelis, kurio patrumpinimas nereikalingas (strypų kiekis nesikeičia be jo), lieka pilnas
    # v98: patrumpinimas paliekamas, jei be jo blogiau: daugiau strypų ARBA mažesnis vientisas likutis (pvz. 2 x ~3 m
    #  bėgeliai poromis viename strype, statmenys - atskirame, likutis tinkamas panaudoti)
    sc_target = _score(nest_bars(fixed + [a["len"] - sum(trims[a["id"]]) for a in adj] * _q, stock, kerf, end), stock)
    for a in sorted(adj, key=lambda q: q["len"]):
        t_ = trims[a["id"]]
        trims[a["id"]] = (0.0, 0.0)
        if _score(nest_bars(fixed + [q["len"] - sum(trims[q["id"]]) for q in adj] * _q, stock, kerf, end), stock) > sc_target:
            trims[a["id"]] = t_
    plan = nest_bars(fixed + [q["len"] - sum(trims[q["id"]]) for q in adj] * _q, stock, kerf, end)
    return {"d": d, "trims": trims, "bars0": n0, "bars": len(plan), "plan": plan, "base": base}


# ------------------------------------------------------------------ lakštai
def _mat(material):
    d = data()
    m = str(material or "").strip().lower()
    return d["zodynas"].get(m, m), d


def sheet_formats(material, thk=None):
    key, d = _mat(material)
    rows = d["lakstai"].get(key, [])
    out = []
    for r in rows:
        if thk is not None and abs(float(r.get("storis_mm", -1)) - float(thk)) > 0.051:
            continue
        fm = [tuple(r["formatas_mm"])] + [tuple(x) for x in r.get("kiti_formatai_mm", [])]
        for f in fm:
            out.append({"tiekejas": r.get("tiekejas", "?"), "preke": r.get("preke", ""), "storis_mm": r.get("storis_mm"),
                        "formatas_mm": (max(f), min(f)), "pastaba": r.get("pastaba", "")})
    return out


def sheet_fit(w, h, material, thk=None, margin=None):
    """Ar detalė w x h (mm) telpa į tiekėjo lakštą. Grąžina {"fits": [...tinkami formatai, mažiausias pirmas], "all": [...],
    "split": patarimas, jei netelpa, "margin": paraštė}."""
    d = data()
    p = float(d["lakstai"].get("parastė_mm", 10)) if margin is None else float(margin)
    fm = sheet_formats(material, thk)
    a, b = max(w, h) + 2 * p, min(w, h) + 2 * p
    fits = [f for f in fm if a <= f["formatas_mm"][0] + 1e-6 and b <= f["formatas_mm"][1] + 1e-6]
    fits.sort(key=lambda f: f["formatas_mm"][0] * f["formatas_mm"][1])
    res = {"fits": fits, "all": fm, "margin": p, "w": w, "h": h}
    if not fits and fm:
        big = max(fm, key=lambda f: f["formatas_mm"][0] * f["formatas_mm"][1])
        L, S = big["formatas_mm"]
        n1 = math.ceil(a / (L - 0)) if b <= S else None               # dalijama išilgai
        n2 = math.ceil(b / S) if a <= L else None
        n = min(v for v in (n1, n2, math.ceil(a / L) * math.ceil(b / S)) if v)
        res["split"] = f"netelpa į didžiausią formatą {L:.0f}x{S:.0f} ({big['tiekejas']}) - dalyti į {n} dalis " \
                       f"(detalė {max(w, h):.0f}x{min(w, h):.0f} + paraštė {p:.0f})"
    elif not fm:
        res["split"] = f"medžiagai '{material}' {('storis ' + str(thk) + ' mm ') if thk else ''}formatų medziagos.json nėra - klausti Ryčio"
    return res


def sheet_text(res):
    if res["fits"]:
        f = res["fits"][0]
        return f"telpa: {f['formatas_mm'][0]:.0f}x{f['formatas_mm'][1]:.0f} ({f['tiekejas']}, {f['preke']}, {f['storis_mm']} mm)"
    return "! " + res.get("split", "netelpa")


# ------------------------------------------------------------------ v114: profilių katalogas (LT tiekėjai)
_TIPAS = [("U", r"\bu\b|u[- ]?prof|lovin|channel|hanger"), ("Z", r"\bz\b|z[- ]?prof"), ("T", r"\bt\b|t[- ]?prof"),
          ("R", r"apval|round|\bd\s*\d|ø|⌀|\bfi\b"), ("FB", r"juost|flat|\bfb\b|strip"),
          ("L", r"\bl\b|l[- ]?prof|kamp|angle"), ("O", r"\bo\b|o[- ]?prof|vamzd|tube|box|\bsq|kvadrat|stačiakamp|rect|\brhs\b|\bshs\b")]


def _nums(text):
    return [float(v.replace(",", ".")) for v in re.findall(r"\d+(?:[.,]\d+)?", str(text))]


def parse_profile(text, kind=None):
    """'U 30x30x2', 'Alu vamzdis 25x25x2', 'kampuotis 30x30x3', '30x30x30x2' (U), 'D25x2' -> (tipas, matmenys katalogo forma).
    kind - priverstinis tipas (L/U/O/R/T/FB/Z), kai tekste jo nėra (pvz. spec rail.size -> U arba O)."""
    t = str(text).lower().replace("×", "x")
    tp = kind
    if not tp:
        for k, rx in _TIPAS:
            if re.search(rx, t):
                tp = k
                break
    dims = re.findall(r"\d+(?:[.,]\d+)?(?:\s*x\s*\d+(?:[.,]\d+)?)+", t)
    n = _nums(dims[0]) if dims else _nums(t)
    if not n:
        return tp, None
    if tp == "U":
        if len(n) >= 4:
            a, b, c, th = n[:4]
            if abs(a - c) < 0.01:                       # Lankava H x B x H x t
                return tp, [b, a, th]
            if abs(a - (b - 2 * th)) < 0.6:             # Heliopolis vidus x B x H x t
                return tp, [b, c, th]
            return tp, [b, a, th]
        if len(n) == 3:
            return tp, [n[0], n[1], n[2]]
        return tp, [n[0], None, n[-1]]
    if tp == "Z":
        return tp, n[:4]
    if tp in ("L", "O", "T") or (tp is None and len(n) == 3):
        if len(n) == 2:                                  # '25x2' - lygiakraštis
            n = [n[0], n[0], n[1]]
        a, b, th = n[:3]
        return tp, ([max(a, b), min(a, b), th] if tp != "T" else [a, b, th])
    if tp == "R":
        if len(n) >= 3:                                  # Heliopolis D x d x t
            return tp, [n[0], n[2]]
        return tp, n[:2]
    if tp == "FB":
        return tp, [max(n[:2]), min(n[:2])] if len(n) >= 2 else n
    return tp, n


def _eq(a, b):
    return a is None or b is None or abs(a - b) < 0.051


STD_PROFILES = [(20, 20, 2), (30, 30, 2), (40, 40, 2), (60, 60, 2), (80, 80, 2)]   # v161, Rytis 2026-10-13


def is_standard_profile(m):
    """v161: rėmo profilių STANDARTAS 20x20x2 / 30x30x2 / 40x40x2 / 60x60x2 / 80x80x2 (U / O / L);
    visi kiti - tik pagal atskirą užklausą (kliento specifikacija ar Ryčio nurodymas)."""
    if not m or len(m) != 3 or None in m:
        return None
    return any(all(_eq(a, b) for a, b in zip(m, s)) for s in STD_PROFILES)


def _std_note(m):
    st = is_standard_profile(m)
    return "" if st in (True, None) else " ! NE STANDARTAS (20/30/40/60/80 x 2) - tik pagal atskirą užklausą"


def profile_check(text, kind=None):
    """Ar profilis yra LT tiekėjų sandėlyje (assets/medziagos.json -> profiliu_katalogas).
    Grąžina {"ok", "tipas", "m", "found": [katalogo įrašai], "near": [artimiausi], "msg"}.
    ok=False - lape / BOM tokio profilio NERAŠYTI be Ryčio patvirtinimo; pasiūlyti `near`."""
    k = data().get("profiliu_katalogas", {})
    rows = k.get("sarasas", [])
    if re.search(r"plien|steel|nerūd|inox|\bst\b|s235|s355", str(text).lower()):
        return {"ok": None, "tipas": None, "m": None, "found": [], "near": [],
                "msg": f"{text}: plienas - katalogas tik Alu, tiekėją tikrinti atskirai"}
    tp, m = parse_profile(text, kind)
    if not m:
        return {"ok": None, "tipas": tp, "m": None, "found": [], "near": [], "msg": f"{text}: matmenų neatpažinau"}
    types = [tp] if tp else sorted({r["tipas"] for r in rows})
    cand = [r for r in rows if r["tipas"] in types and len(r["m"]) == len(m)]
    found = [r for r in cand if all(_eq(x, y) for x, y in zip(r["m"], m))]
    if tp == "U" and not found:                           # U: galbūt B ir H sukeisti užraše
        found = [r for r in cand if len(m) == 3 and None not in r["m"] and None not in m and _eq(r["m"][0], m[1]) and _eq(r["m"][1], m[0]) and _eq(r["m"][2], m[2])]
    def dist(r):
        return sum(abs((x if x is not None else y) - y) * (3 if i == len(m) - 1 else 1) for i, (x, y) in enumerate(zip(r["m"], m)) if y is not None)
    near = sorted([r for r in cand if r not in found], key=dist)[:3]
    name = f"{tp or '?'} " + "x".join("?" if v is None else f"{v:g}" for v in m)
    if found:
        sup = sorted({s["t"] for r in found for s in r["tiekejai"]})
        an = any(s.get("anoduotas") for r in found for s in r["tiekejai"])
        unk = any(None in r["m"] for r in found)
        if not tp:
            name = "/".join(sorted({r["tipas"] for r in found})) + " " + "x".join(f"{v:g}" for v in m) + " (tipas nenurodytas)"
        msg = f"{name}: YRA - {', '.join(sup)}" + (" (yra ir anoduotas)" if an else "") + \
              (" ! tiekėjas aukščio nenurodo - patikslinti" if unk else "")
        return {"ok": True, "tipas": tp, "m": m, "found": found, "near": near, "msg": msg + _std_note(m),
                "standartas": is_standard_profile(m)}
    alt = "; ".join(f"{r['tipas']} " + "x".join("?" if v is None else f"{v:g}" for v in r["m"]) + " (" + ", ".join(sorted({s['t'] for s in r['tiekejai']})) + ")" for r in near)
    nr = [x for x in k.get("nerasta", []) if parse_profile(x["profilis"])[1] == m]
    msg = f"! {name}: LT tiekėjų sandėlyje NĖRA (Heliopolis, Lankava, Proplastik)" + (f" - {nr[0]['pastaba']}" if nr else "") + \
          (f". Artimiausi: {alt}" if alt else "") + ". Lape nerašyti be Ryčio patvirtinimo."
    return {"ok": False, "tipas": tp, "m": m, "found": [], "near": near, "msg": msg + _std_note(m),
            "standartas": is_standard_profile(m)}


def profile_warn(text, kind=None):
    """trumpas perspėjimas konsolei; '' jei profilis yra"""
    r = profile_check(text, kind)
    if r.get("ok") and r.get("standartas") is False:
        return "  " + r["msg"]
    return "" if r["ok"] or r["ok"] is None and "plienas" in r["msg"] else "  " + r["msg"]


def sheet_check(material, thk, ral=None, w=None, h=None):
    """Ar lakštas (medžiaga + storis [+ RAL]) yra pas tiekėjus. Grąžina tekstą."""
    fm = sheet_formats(material, thk)
    if not fm:
        alls = sorted({r["storis_mm"] for r in data()["lakstai"].get(_mat(material)[0], [])})
        return f"! {material} {thk:g} mm: tiekėjų formatų NĖRA (yra storiai: {', '.join(f'{v:g}' for v in alls) or '-'}) - lape nerašyti be patvirtinimo"
    rows = data()["lakstai"].get(_mat(material)[0], [])
    if ral:
        rr = str(ral).upper().replace("RAL", "").strip()
        hit = [r for r in rows if abs(float(r["storis_mm"]) - float(thk)) < 0.051 and rr in r.get("ral", [])]
        if not hit:
            return f"! {material} {thk:g} mm RAL {rr}: standartinės spalvos tiekėjai neturi - dažyti / klijuoti plėvelę arba užsakyti (Proplastik nestandartinė RAL - nuo 500 m²)"
        fm = [f for f in fm if any(f["preke"] == r["preke"] for r in hit)]
    txt = "; ".join(sorted({f"{f['formatas_mm'][0]:.0f}x{f['formatas_mm'][1]:.0f} ({f['tiekejas']})" for f in fm}))
    out = f"{material} {thk:g} mm{(' RAL ' + str(ral)) if ral else ''}: YRA - {txt}"
    if w and h:
        out += " | " + sheet_text(sheet_fit(w, h, material, thk))
    return out


# ------------------------------------------------------------------ CLI
if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] in ("profilis", "profile", "p"):
        for t_ in args[1:]:
            r_ = profile_check(t_)
            print(r_["msg"])
            for f_ in r_["found"]:
                print("   ", ", ".join(s_["t"] + (" " + s_["kodas"] if s_.get("kodas") else "") + (" anod." if s_.get("anoduotas") else "") for s_ in f_["tiekejai"]))
        sys.exit(0)
    if args and args[0] in ("lakstas", "lakštas", "sheetcheck"):
        mat_, thk_ = args[1], float(args[2])
        ral_ = args[3] if len(args) > 3 else None
        print(sheet_check(mat_, thk_, ral_))
        sys.exit(0)
    if not args or args[0] not in ("bars", "sheet"):
        print(__doc__); sys.exit(0)
    if args[0] == "bars":
        c = cfg()
        vals = []
        i = 1
        while i < len(args):
            if args[i] == "--stock": c["stock"] = float(args[i + 1]); i += 2
            elif args[i] == "--kerf": c["kerf"] = float(args[i + 1]); i += 2
            elif args[i] == "--end": c["end"] = float(args[i + 1]); i += 2
            else: vals.append(float(args[i])); i += 1
        bars = nest_bars(vals, c["stock"], c["kerf"], c["end"])
        print(bars_text(bars, c["stock"]), f"| atlieka {bars_waste(bars, c['stock']) / 1000:.2f} m (prapjova {c['kerf']:g} mm)")
        for L_, parts_ in LAST_SPLITS.items():
            print(f"  ! dalis {L_:.0f} > strypas {c['stock']:.0f} - jungti: " + " + ".join(f"{x:.0f}" for x in parts_) + " (sandūra laisva, mažiausios atliekos)")
    else:
        w, h, mat = float(args[1]), float(args[2]), args[3]
        thk = float(args[4]) if len(args) > 4 else None
        r = sheet_fit(w, h, mat, thk)
        print(sheet_text(r))
        for f in r["fits"][1:]:
            print(f"  taip pat: {f['formatas_mm'][0]:.0f}x{f['formatas_mm'][1]:.0f} ({f['tiekejas']}, {f['preke']}, {f['storis_mm']} mm)")
