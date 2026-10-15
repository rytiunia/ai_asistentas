#!/usr/bin/env python3
"""P6 raidžių DXF 1:1 su tvirtinimo skylėmis (v66, Rytis 2026-10-09). Iš kliento PDF (raidės + pilki bėgeliai):

  SLUOKSNIAI (3, visuose failuose):
    1_PRIEKIS  juoda   (ACI 7) - STIKLAS = originalus kliento kontūras (raidės dydis = stiklo dydis)
    2_GALAS    geltona (ACI 2) - DUGNAS = kontūras `--inset` (3) mm į vidų + Ø`--hole-d` (3.2) tvirtinimo skylės
    3_REMAS    raudona (ACI 1) - bėgeliai: kliento pilka grafika -> tikras profilio plotis (`--rail` 30 / 40),
                                 ašis išlaikoma, galai 10 mm raidės viduje (rail_edge)

  TVIRTINIMO SKYLĖS (dugne, ten kur už raidės eina bėgelis) - PRISPAUDIMO LOGIKA (Rytis 2026-10-09):
    varžtas prispaudžia dugną prie bėgelio zonoje spinduliu R = `--press-r` (100 mm, Rytis 2026-10-09); skylės paskirstomos
    taip, kad prispaustų KUO DIDESNĮ dugno plotą - ne tik kraštus, bet ir vidurį.
    Kandidatų linija = bėgelio ašis, `--rail-end-clear` (15) nuo bėgelio galų, SUKIRSTA su dugnu, įtrauktu
    `--hole-edge` (10) mm (skylės centras >= 10 mm nuo dugno kontūro, t. y. >= 11,5 mm nuo šono) -> ruožai.
    Gretimi ruožai (statinis + lankas per akutę), tarpas < R - VIENA zona (a, n, m - ne po skylę kiekvienam ruožui).
    Zona dalijama į n = ceil(L / 2R) lygių dalių, skylė - KIEKVIENOS
    DALIES CENTRE (Rytis 2026-10-09, test_A.pdf: ne galuose - T juosta 367 -> 2 skylės ketvirčiuose ~92 / 275;
    T kojelė, A kojos -> 1 viduryje). KOJELĖ + PILVELIS vienoje zonoje (a, d apačia / viršus): varžtas KOJELĖJE
    (statinis, kuris tęsiasi už bėgelio į raidės vidų), pilvelis gauna varžtą tik kaip antrą skylę; kojelės skylė
    centruojama per kojelę + su ja sujungtą dugno plotą VISOJE bėgelio juostoje (iki kojelės pločio už jos) - m / n jungtyje
    su lanku skylė traukiama nuo krašto į didesnį tvirtinimo plotą. Minimumai: ant bėgelio >= 2, raidei >= 4 - kol trūksta, ILGIAUSIAS vienos
    skylės ruožas (L >= 2 x `--min-gap`) gauna 2 skyles ketvirčiuose (A viršūnė, T kojelė). Jei vis tiek < 4 -
    perspėjimas (siaura raidė: hole-edge mažinamas iki 7). Ataskaitoje - prispausto dugno ploto %.
    VISŲ VIENODŲ RAIDŽIŲ TVIRTINIMAI VIENODI (Rytis 2026-10-09): skylės iš pirmos tokios raidės perkeliamos
    kitoms; išimtis - raidė ant kitokio rėmo (bėgelio galas / ašis neleidžia tų pačių vietų) - skaičiuojama atskirai.

  D11 LAIDO IŠVESTIS (`--cable top|bottom|both|none`, Rytis 2026-10-09): viena skylė raidei bėgelio ašyje (laidas pro
    dugną į U profilio vidų), >= `--d11-edge` (20) nuo dugno kontūro, >= `--d11-fix-clear` (25) nuo D3.2 centrų;
    vieta (Rytis 2026-10-09, pavyzdžiai Bandymas): štrichas ant bėgelio su 1 varžtu - varžtas ir D11 PORA, centruota
    per štricho plotą ant bėgelio (varžtas c-12,5 / D11 c+12,5, D11 raidės centro pusėje); platus ruožas su >= 2 varžtais -
    D11 centre tarp dviejų arčiausiai raidės centro varžtų; zona renkama arčiausia raidės centrui. Vienodoms raidėms vienoda.
    Netelpa (siaura kojelė) - D11 ruožo centre, to bėgelio varžtai tame ruože perstumiami simetriškai į šalis.
    v68 (Rytis): visi variantai pirma tikrinami su PILNU --d11-edge visoje ašyje; mažinama tik kai plačios vietos nėra.
    Vis tiek netelpa (test_B „s") - D11 VISADA BĖGELIO AŠYJE (Rytis): dedama ašyje arčiausiai raidės centro,
    o tos zonos varžtai perstatomi į likusias saugias vietas. Šalia bėgelio - NIEKADA.
    `both` - DU rinkiniai: *_laidas_virsus.dxf (viršutinis bėgelis) ir *_laidas_apacia.dxf (apatinis).
  IŠVESTIS: <prefix>_P6_1-1.dxf (visa iškaba, nulis - raidžių kairė apačia, y aukštyn) + <prefix>_L01_T.dxf ...
    (po vieną raidei, nulis - raidės kairė apačia, bėgeliai apkirpti ±30 mm už raidės) + <prefix>_patikra.png.
    Kontūrai - uždaros LWPOLYLINE (kreivės išlygintos 0,01 mm tikslumu - CNC / lazeris / Corel), skylės - CIRCLE.

Naudojimas:
  python3 p6_dxf.py klientas.pdf out_dir --scale 1 --names TESTAS [--rail 30] [--inset 3] [--hole-d 3.2]
  python3 p6_dxf.py klientas.pdf out_dir --ref-mm 2328 ...     (ref-mm = raidžių grupės plotis mm)
Reikia: pip install pymupdf shapely ezdxf matplotlib --break-system-packages
"""
import argparse, json, warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import math
import os
import sys

import pymupdf as fitz
from shapely.geometry import LineString, Point, Polygon, box as sbox
from shapely.ops import unary_union
import ezdxf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lapas_core as K  # noqa: E402  (drawing_to_subpaths, split_letters, bez)

ap = argparse.ArgumentParser()
ap.add_argument("pdf")
ap.add_argument("out_dir")
ap.add_argument("--page", type=int, default=0)
g_ = ap.add_mutually_exclusive_group()
g_.add_argument("--scale", type=float, default=None, help="brėžinio mastelis (1 = 1:1, 10 = 1:10)")
g_.add_argument("--ref-mm", type=float, default=None, help="raidžių grupės bendras plotis mm")
ap.add_argument("--names", default="", help="raidžių vardai iš kairės, pvz. TESTAS (failų pavadinimams)")
ap.add_argument("--prefix", default=None, help="failų prefiksas (numatyta - PDF vardas)")
ap.add_argument("--stems", action="store_true", help="v195: senas režimas - skylė traukiama į kojelę (a / d / m); numatyta - tolygiai per zoną")
ap.add_argument("--rail", type=float, default=30, help="bėgelio profilio plotis mm (U30 / U40)")
ap.add_argument("--p1", action="store_true", help="v116: P1 NON-LIT - dugnas (inside kontūras) -0,7 mm, be drenažo, be D11 (LED nėra)")
ap.add_argument("--inset", type=float, default=None, help="dugnas mažesnis už stiklą, mm į vidų (back_inset)")
ap.add_argument("--blunt-len", type=float, default=12, help="v108: dugno smaili įpjova ilgesnė nei tiek mm nuo stiklo viršūnės -> nukertama (2 taškai, buki kampai)")
ap.add_argument("--hole-d", type=float, default=3.2)
ap.add_argument("--hole-edge", type=float, default=10, help="skylės centras nuo DUGNO kontūro, mm")
ap.add_argument("--rail-end-clear", type=float, default=15, help="skylės centras nuo bėgelio galo, mm")
ap.add_argument("--min-gap", type=float, default=40, help="vienos skylės ruožas plečiamas į galus tik jei L >= šis")
ap.add_argument("--off-axis", type=float, default=8, help="v69: papildomos skylės nuokrypis nuo bėgelio ašies (U sienelėje), mm")
ap.add_argument("--press-r", type=float, default=100, help="varžto prispaudimo zonos spindulys mm (žingsnis <= 2R)")
ap.add_argument("--rail-edge", type=float, default=10, help="bėgelio galas raidės viduje, mm")
ap.add_argument("--interior", action="store_true", help="v98: vidaus iškaba - be drenažo išpjovų (numatyta - exterior, su drenažu)")
ap.add_argument("--drain-d", type=float, default=8, help="v98: drenažo išpjovos skersmuo, mm")
ap.add_argument("--crop", default=None, help="v97: sritis pt x0,y0,x1,y1 (kaip spec crop_pt) - visas lapas su keliais vaizdais")
ap.add_argument("--fill", default=None, help="v97: raidžių spalva r,g,b (kaip spec client_fill), kitos spalvos ignoruojamos; v112: kelios - 'r,g,b;r,g,b'")
ap.add_argument("--plate-fill", default=None, help="v112: PLOKŠTĖS spalva r,g,b (pvz. EXTRA geltonas apskritimas po X) - plokštė + jos raidė(s) atskirai")
ap.add_argument("--spacer-d", type=float, default=4, help="v112: raidės ant plokštės distancerių / varžtų skylės Ø (EXTRA X - Ø4)")
ap.add_argument("--spacer-edge", type=float, default=15, help="v112: distancerio skylės centras nuo dugno krašto, mm")
ap.add_argument("--plate-front", action="store_true", help="v118: plokštėje pažymėti X tvirtinimo rėmai (H1800 60x60) - plokštė VAIZDAS IŠ PRIEKIO, be C žymos")
ap.add_argument("--c-mark-r", type=float, default=6, help="v118: C žymos (galinė pusė) spindulys mm")
ap.add_argument("--plate-gap", type=float, default=100, help="v112: raidė ant plokštės DXF'e perkeliama kairiau plokštės, tarpas mm")
ap.add_argument("--separate", action="store_true", help="v90: atskiros raidės be rėmo - bėgeliai tik skylių ašys, 3_REMAS nėra, D11 vienoje horizontalioje linijoje")
ap.add_argument("--rails-json", default=None, help="v85: rėmas iš braizyti_begeliai.py (RAILS_JSON) - bėgeliai kaip lape, galai nekeičiami")
ap.add_argument("--tol", type=float, default=0.01, help="kreivių išlyginimo tikslumas mm")
ap.add_argument("--fit-tol", type=float, default=0.02, help="v113: kontūrai DXF'e - tiesės + lankai, nuokrypis mm (mažai mazgų)")
ap.add_argument("--no-letters", action="store_true", help="tik bendras failas, be failų po raidę")
ap.add_argument("--cable", default="both", choices=["top", "bottom", "both", "none"],
                help="D11 laido išvestis: viršutiniame bėgelyje / apatiniame / abu variantai (atskiri failai) / be")
ap.add_argument("--d11", type=float, default=11, help="laido skylės skersmuo")
ap.add_argument("--d11-edge", type=float, default=20, help="D11 centras nuo dugno kontūro, mm")
ap.add_argument("--d11-fix-clear", type=float, default=25, help="D11 centras nuo D3.2 centrų, mm")
A = ap.parse_args()
# v116 (Rytis 2026-10-12): P1 - inside kontūras 0,7 mm, drenažo skylių nereikia (LED nesideda), laido skylių nėra
if A.inset is None:
    A.inset = 0.7 if A.p1 else 3.0
if A.p1:
    A.interior = True        # be drenažo
    A.cable = "none"         # be D11

page = fitz.open(A.pdf)[A.page]


# ------------------------------------------------------------------ kliento geometrija
def true_rect(d):
    pts = [q for it in d["items"] for q in it[1:] if hasattr(q, "x")]
    for it in d["items"]:
        if it[0] == "re":
            pts += [it[1].tl, it[1].br]
        if it[0] == "qu":
            pts += [it[1].ul, it[1].lr]
    return fitz.Rect(min(q.x for q in pts), min(q.y for q in pts), max(q.x for q in pts), max(q.y for q in pts))


def is_grey(fill):
    r, g, b = fill[:3]
    return abs(r - g) < 0.06 and abs(g - b) < 0.06 and 0.3 < r < 0.85


raw_letters, raw_rails = [], []
_CROP = fitz.Rect(*[float(v) for v in A.crop.split(",")]) if A.crop else None
_FILLS = [[float(v) for v in f_.split(",")] for f_ in A.fill.split(";")] if A.fill else None
_PFILL = [float(v) for v in A.plate_fill.split(",")] if A.plate_fill else None
raw_plates = []
for d in page.get_drawings():
    if d.get("fill") is None:
        continue
    if _CROP is not None and not _CROP.contains(d["rect"]):        # v97: tik nurodyta lapo sritis
        continue
    r = true_rect(d)
    if max(r.width, r.height) < 1:
        continue
    if _PFILL and max(abs(a_ - b_) for a_, b_ in zip(d["fill"][:3], _PFILL)) <= 0.03:
        raw_plates.append(d)                                        # v112: plokštė (ne raidė)
        continue
    if is_grey(d["fill"]) and max(r.width, r.height) / max(min(r.width, r.height), 0.1) > 6:
        raw_rails.append(r)
    elif _FILLS is None or any(max(abs(a_ - b_) for a_, b_ in zip(d["fill"][:3], f_)) <= 0.06 for f_ in _FILLS):
        raw_letters.append(d)
if not raw_letters:
    sys.exit("raidžių (užpildytų ne pilkų kontūrų) nerasta")

# mastelis: --scale (1 = 1:1) arba --ref-mm (raidžių grupės plotis)
lx0 = min(true_rect(d).x0 for d in raw_letters); lx1 = max(true_rect(d).x1 for d in raw_letters)
if A.ref_mm:
    S = A.ref_mm / (lx1 - lx0)
else:
    S = (A.scale or 1.0) * 25.4 / 72
# v103 (Joker 226001): mūsų lapo vaizde ausėlių Ø skylės - balti mažyčiai apskritimai -> ne raidės (< 20 mm)
_n0 = len(raw_letters)
raw_letters = [d for d in raw_letters if max(true_rect(d).width, true_rect(d).height) * S >= 20]
if len(raw_letters) < _n0:
    print(f"  smulkūs kontūrai (< 20 mm) praleisti: {_n0 - len(raw_letters)}")
    lx0 = min(true_rect(d).x0 for d in raw_letters)
OX = lx0; OY = min(true_rect(d).y0 for d in raw_letters)


def tomm(p):                      # pt -> mm, y žemyn (kaip PDF); į DXF verčiama pabaigoje (y aukštyn)
    return ((p[0] - OX) * S, (p[1] - OY) * S)


def flat_fine(sp, tol):
    """subpath (M/L/C, mm) -> taškai; Bezier dalijama adaptyviai pagal sagitta <= tol"""
    pts, cur = [], None
    for s_ in sp:
        if s_[0] in ("M", "L"):
            cur = s_[1]; pts.append(cur)
        else:
            p0, (p1, p2, p3) = cur, s_[1:]
            # kontrolinio daugiakampio ilgis -> segmentų skaičius (sagitta ~ L^2/(8 n^2 R); saugus įvertis)
            L_ = math.dist(p0, p1) + math.dist(p1, p2) + math.dist(p2, p3)
            n = max(4, min(400, int(math.sqrt(L_ / (8 * tol)) * 2) + 1))
            for i in range(1, n + 1):
                pts.append(K.bez(p0, p1, p2, p3, i / n))
            cur = p3
    out = [pts[0]]
    for q in pts[1:]:
        if math.dist(q, out[-1]) > 1e-4:
            out.append(q)
    if len(out) > 2 and math.dist(out[0], out[-1]) < 1e-4:
        out.pop()
    return out


letters = []
for d in raw_letters:
    for L_ in K.split_letters(K.drawing_to_subpaths(d, tomm)):
        rings = [flat_fine(sp, A.tol) for sp in L_["sub"]]
        rings = [r_ for r_ in rings if len(r_) >= 3]
        polys = sorted([Polygon(r_).buffer(0) for r_ in rings], key=lambda p: -p.area)
        geom = polys[0]
        for p in polys[1:]:
            geom = geom.symmetric_difference(p)
        geom = geom.buffer(0)
        letters.append({"geom": geom, "rings": rings, "fill": tuple(d["fill"][:3])})
# dublikatai (užpildas + apvadas + kopija)
uniq = []
for o in letters:
    b_ = o["geom"].bounds
    if any(max(abs(a - c) for a, c in zip(b_, u["geom"].bounds)) < 1.0 and abs(o["geom"].area - u["geom"].area)
           < 0.002 * max(u["geom"].area, 1) for u in uniq):
        continue
    uniq.append(o)
letters = sorted(uniq, key=lambda o: (o["geom"].bounds[0], o["geom"].bounds[1]))
# v112 (Rytis 2026-10-12, EXTRA darbiniai): PLOKŠTĖ (apskritimas) ir raidė ant jos (X) - atskiros detalės, ne ant bėgelių
PLATES = []
for d in raw_plates:
    for L_ in K.split_letters(K.drawing_to_subpaths(d, tomm)):
        rings = [r_ for r_ in (flat_fine(sp, A.tol) for sp in L_["sub"]) if len(r_) >= 3]
        polys = sorted([Polygon(r_).buffer(0) for r_ in rings], key=lambda p: -p.area)
        geom = polys[0]
        for p in polys[1:]:
            geom = geom.symmetric_difference(p)
        PLATES.append({"geom": geom.buffer(0), "rings": rings, "fill": tuple(d["fill"][:3])})
for pl_ in PLATES:
    pl_["let"] = [o for o in letters if pl_["geom"].buffer(1).contains(o["geom"].representative_point())]
# plokštės spalvos forma BE raidės viduje - paprasta raidė (pvz. FAS1000: 7-23 tos pačios geltonos kaip apskritimas)
letters += [{"geom": pl_["geom"], "rings": pl_["rings"], "fill": pl_["fill"]} for pl_ in PLATES if not pl_["let"]]
PLATES = [pl_ for pl_ in PLATES if pl_["let"]]
letters = sorted(letters, key=lambda o: (o["geom"].bounds[0], o["geom"].bounds[1]))
_on_pl = {id(o) for pl_ in PLATES for o in pl_["let"]}
letters = [o for o in letters if id(o) not in _on_pl]
if PLATES:
    print(f"  plokštės: {len(PLATES)}, raidžių ant jų: {len(_on_pl)} (atskirai, ne ant bėgelių)")
# v85: kelios eilutės - tvarka eilutėmis (viršutinė pirma), eilutėje iš kairės; akcentai (Ė, Ū) - prie savo raidės
_hm = sorted(o["geom"].bounds[3] - o["geom"].bounds[1] for o in letters)[len(letters) // 2]
_rows = []
for o in sorted(letters, key=lambda o: (o["geom"].bounds[1] + o["geom"].bounds[3]) / 2):
    b_ = o["geom"].bounds
    if b_[3] - b_[1] < 0.5 * _hm:
        continue
    cy_ = (b_[1] + b_[3]) / 2
    for r_ in _rows:
        if abs(r_["cy"] - cy_) < 0.5 * _hm:
            r_["L"].append(o); break
    else:
        _rows.append({"cy": cy_, "L": [o]})
_rows.sort(key=lambda r_: r_["cy"])
_host = {}
_big_l = [o for r_ in _rows for o in r_["L"]]
for a_ in letters:                                   # akcentas -> artimiausia (vertikaliai) raidė, kurios x ribose jis yra
    ab = a_["geom"].bounds
    if (ab[3] - ab[1]) >= 0.5 * _hm:
        continue
    xc_ = (ab[0] + ab[2]) / 2
    cand_ = [o for o in _big_l if o["geom"].bounds[0] - 5 <= xc_ <= o["geom"].bounds[2] + 5]
    if cand_:
        h_ = min(cand_, key=lambda o: min(abs(o["geom"].bounds[1] - ab[3]), abs(ab[1] - o["geom"].bounds[3])))
        _host.setdefault(id(h_), []).append(a_)
_ord = []
for ri, r_ in enumerate(_rows):
    for o in sorted(r_["L"], key=lambda o: o["geom"].bounds[0]):
        _ord.append(o)
        _ord += _host.get(id(o), [])
letters = _ord + [o for o in letters if o not in _ord]
for i, o in enumerate(letters):
    o["name"] = (A.names[i] if i < len(A.names) else "") or f"{i + 1}"
    o["id"] = f"L{i + 1:02d}_{o['name']}" if A.names else f"L{i + 1:02d}"
    o["bb"] = o["geom"].bounds
GX0, GY0, GX1, GY1 = (min(o["bb"][0] for o in letters), min(o["bb"][1] for o in letters),
                      max(o["bb"][2] for o in letters), max(o["bb"][3] for o in letters))
PW, PH = GX1 - GX0, GY1 - GY0
ALL = unary_union([o["geom"] for o in letters])

# ------------------------------------------------------------------ bėgeliai: tikras profilis, galai 10 mm raidėje
RE = A.rail_edge
rails = []
_big = [o["bb"] for o in letters if (o["bb"][3] - o["bb"][1]) >= 0.6 * PH]
VRAILS = []                                         # v85: vertikalūs (akcentų laikikliai, statmenys) - iš --rails-json
EARS_J, BRK_J = [], []                              # v101: ausėlės ir U laikikliai (rėmo dalis, 3_REMAS)
if A.rails_json:
    _rj = json.load(open(A.rails_json))
    if _rj.get("separate"):                                  # v90: braizyti_begeliai mounting "none"
        A.separate = True
    _ox, _oy = _rj["origin_pt"]
    _dx, _dy = (_ox - OX) * S, (_oy - OY) * S                 # tas pats nulis (raidžių min) - paprastai 0
    raw_rails = []
    for q in _rj["rails"]:
        x0, y0, x1, y1 = q["x0"] + _dx, q["y0"] + _dy, q["x1"] + _dx, q["y1"] + _dy
        if q["kind"] == "h":
            cy = (y0 + y1) / 2
            rails.append({"y0": cy - A.rail / 2, "y1": cy + A.rail / 2, "cy": cy, "x0": x0, "x1": x1, "cx0": x0, "cx1": x1, "keep": True})
        else:
            cx = (x0 + x1) / 2
            VRAILS.append({"x0": cx - A.rail / 2, "x1": cx + A.rail / 2, "cx": cx, "y0": y0, "y1": y1, "acc": q.get("acc"),
                           "poly": [(px_ + _dx, py_ + _dy) for px_, py_ in q["poly"]] if q.get("poly") else None})
    for e_ in _rj.get("ears", []):
        EARS_J.append({k_: e_[k_] + (_dx if k_ in ("x0", "x1", "hx") else _dy if k_ in ("y0", "y1", "hy") else 0)
                       for k_ in ("x0", "y0", "x1", "y1", "hx", "hy")} | {"d": e_.get("d", 6)})
    for b_ in _rj.get("brackets", []):
        BRK_J.append({"x0": b_["x0"] + _dx, "x1": b_["x1"] + _dx, "y0": b_["y0"] + _dy, "y1": b_["y1"] + _dy,
                      "holes": [(h_[0] + _dx, h_[1] + _dy, h_[2]) for h_ in b_.get("holes", [])]})
    print(f"  rėmas iš {A.rails_json}: {len(rails)} horizontalūs, {len(VRAILS)} vertikalūs (galai kaip lape)")
for r in raw_rails:
    x0, y0 = tomm((r.x0, r.y0)); x1, y1 = tomm((r.x1, r.y1))
    if (y1 - y0) > (x1 - x0):
        continue                                   # vertikalūs (i taško laikiklis) - šiame modulyje nenaudojami
    cy = (y0 + y1) / 2
    lo = max(b_[1] for b_ in _big) + RE + 1 + A.rail / 2       # v49: >= 11 mm nuo pilno aukščio raidžių krašto
    hi = min(b_[3] for b_ in _big) - RE - 1 - A.rail / 2
    if lo < hi and not (lo <= cy <= hi):
        ncy = min(max(cy, lo), hi)
        print(f"  bėgelis y{cy:.1f} -> y{ncy:.1f} (>= {RE + 1:.0f} mm nuo raidžių krašto)")
        cy = ncy
    rails.append({"y0": cy - A.rail / 2, "y1": cy + A.rail / 2, "cy": cy, "x0": x0, "x1": x1, "cx0": x0, "cx1": x1})


def fit_end(r_, side):
    """galas = kraštinė padėtis galinėje raidėje, kur abu bėgelio kampai >= RE raidės viduje
    (supaprastinta braizyti_begeliai._fit_h_end: be skylės „6" atvejo)"""
    y0, y1 = r_["y0"], r_["y1"]
    band = sbox(-1e6, y0, 1e6, y1)
    cand = [o["geom"] for o in letters if o["geom"].intersects(band)]
    if not cand:
        return None
    xe = r_["x1"] if side == "r" else r_["x0"]
    inside = [o for o in cand if o.bounds[0] - 1 <= xe <= o.bounds[2] + 1]
    if inside:
        term = max(inside, key=lambda o: o.bounds[2]) if side == "r" else min(inside, key=lambda o: o.bounds[0])
    else:
        outw = [o for o in cand if (o.bounds[0] > xe if side == "r" else o.bounds[2] < xe)]
        if outw:
            term = min(outw, key=lambda o: o.bounds[0]) if side == "r" else max(outw, key=lambda o: o.bounds[2])
        else:
            term = max(cand, key=lambda o: o.bounds[2]) if side == "r" else min(cand, key=lambda o: o.bounds[0])
    inner = term.buffer(-RE)
    if inner.is_empty:
        return None
    a, b = term.bounds[0], term.bounds[2]
    xs = [b - k * 0.5 for k in range(int((b - a) * 2) + 1)] if side == "r" else [a + k * 0.5 for k in range(int((b - a) * 2) + 1)]
    for x in xs:
        if inner.covers(Point(x, y0)) and inner.covers(Point(x, y1)):
            return float(x)
    return None


for r_ in rails:
    if r_.get("keep"):
        continue
    nx0, nx1 = fit_end(r_, "l"), fit_end(r_, "r")
    if nx0 is not None and nx1 is not None and nx1 - nx0 > 100:
        print(f"  bėgelis y{r_['cy']:.0f}: galai {r_['x0']:.0f}/{r_['x1']:.0f} -> {nx0:.0f}/{nx1:.0f} ({RE:.0f} mm nuo raidės)")
        r_["x0"], r_["x1"] = nx0, nx1
rails.sort(key=lambda r_: r_["cy"])
if not rails:
    print("  ! bėgelių (pilkų stačiakampių) kliento faile nėra - skylės nededamos, 3_REMAS tuščias")


# ------------------------------------------------------------------ tvirtinimo skylės
def holes_on_rail(back, r_, edge):
    """-> zonos [{"a","b","L","segs","xs","up","cy"}]: skylių centrai raidės dugne ant bėgelio ašies"""
    safe = back.buffer(-edge, join_style=2, mitre_limit=10)
    if safe.is_empty:
        return []
    ax0, ax1 = r_["x0"] + A.rail_end_clear, r_["x1"] - A.rail_end_clear
    if ax1 <= ax0:
        return []
    axis = LineString([(ax0, r_["cy"]), (ax1, r_["cy"])])

    def _segs(g):
        cut = axis.intersection(g)
        return sorted([(q.bounds[0], q.bounds[2]) for q in getattr(cut, "geoms", [cut])
                       if isinstance(q, LineString) and q.length > 0.5])
    full, ssegs = _segs(back), _segs(safe)          # tikri štrichai ant ašies / vietos, kur galima gręžti
    if not full or not ssegs:
        return []
    # Rytis 2026-10-09: štrichas = TIKRAS dugno ruožas ant bėgelio ašies (ne saugios zonos gabalai - m lankas su
    # išėjimais iš 10 mm zonos yra VIENAS štrichas); įpjova < min_gap (serifas) nejungia, akutė - skiria.
    zones, cur = [], []
    for a, b in full:
        if cur and a - cur[-1][1] >= A.min_gap:
            zones.append(cur); cur = []
        cur.append((a, b))
    if cur:
        zones.append(cur)
    # Rytis 2026-10-09: KOJELĖ (statinis, kuris tęsiasi už bėgelio į raidės vidų: a / d kojelė) - varžtas kojelėje,
    # ne pilvelyje; pilvelis gauna varžtą tik kai zonai priklauso daugiau skylių. Kojelė = ašies ruožas, už kurio
    # (rėmo vidaus pusėje, 20 / 45 / 70 mm nuo bėgelio krašto, tas pats x) dugne yra medžiaga - tiesus statinis.
    side = 1 if r_["cy"] < PH / 2 else -1                  # y žemyn: viršutiniam bėgeliui vidus - žemyn
    yin = [r_["cy"] + side * (A.rail / 2 + d_) for d_ in (20, 45, 70)]   # tiesus statinis >= 85 mm už bėgelio (ne s lankas)

    def _stems(zs):
        cols, out_ = [], []
        for a, b in zs:
            for k in range(int((b - a) / 2) + 1):
                x = a + 2 * k
                if all(back.covers(Point(x, y_)) for y_ in yin):
                    cols.append(x)
        for x in cols:
            if out_ and x - out_[-1][1] <= 2.1:
                out_[-1][1] = x
            else:
                out_.append([x, x])
        return [(a, b) for a, b in out_ if b - a >= 15]

    out = []
    for zs in zones:
        a, b = zs[0][0], zs[-1][1]
        L_ = b - a
        zsegs = [(max(sa, a), min(sb, b)) for sa, sb in ssegs if sb > a and sa < b]
        if not zsegs:
            continue
        n = max(1, math.ceil(L_ / (2 * A.press_r)))      # dalių skaičius: dalis <= 2R (vieno varžto zona)
        stems = _stems(zs)
        rest = []                                        # zona be kojelių (pilvelis / lankas)
        for sa, sb in zsegs:
            cur_ = [(sa, sb)]
            for ta, tb in stems:
                nxt = []
                for ca, cb in cur_:
                    nxt += [(x0_, x1_) for x0_, x1_ in ((ca, min(cb, ta - A.min_gap / 2)), (max(ca, tb + A.min_gap / 2), cb)) if x1_ - x0_ > 0]
                cur_ = nxt
            rest += cur_
        # v195 (Rytis 2026-10-13: „kodėl toks netolygus tvirtinimo taškų dėliojimas? pagal plotą mažesniame pridėta daugiau nei
        #  didesniame") - NUMATYTA: skylės TOLYGIAI per visą zoną (n = ceil(L / 2R), žingsnis L / n, nuo galų L / 2n), kojelės
        #  traukimas (v-2026-10-09, a / d / m) - tik su --stems
        if A.stems and stems and len(stems) < len(zs) + 1 and rest:  # kojelė + pilvelis vienoje zonoje
            # Rytis 2026-10-09 (m / n): kai kojelė susijungia su lanku, tvirtinimo plotas didesnis - skylė traukiama
            # nuo krašto į jungtį: centruojama per kojelę + gretimą ištisinį dugno ruožą ant ašies (`full`),
            # bet ne toliau kaip kojelės plotis už jos krašto.
            xs = []
            band = back.intersection(sbox(a - 1, r_["y0"], b + 1, r_["y1"]))     # dugnas VISOJE bėgelio juostoje
            for ta, tb in stems:
                w = tb - ta
                blob = next((g for g in getattr(band, "geoms", [band]) if g.covers(Point((ta + tb) / 2, r_["cy"]))), None)
                run = (blob.bounds[0], blob.bounds[2]) if blob is not None else (ta, tb)
                ea, eb = max(run[0], ta - w), min(run[1], tb + w)      # ne toliau kaip kojelės plotis už jos
                xs.append((ea + eb) / 2)
            xs = snap_all(xs, zsegs)
            m = n - len(xs)
            if m > 0:
                Lr = sum(b_ - a_ for a_, b_ in rest); acc, parts = 0.0, []
                for k in range(m):                       # dalių centrai likusiame plote (per ruožų ilgį)
                    t = Lr * (k + 0.5) / m
                    for a_, b_ in rest:
                        if t <= acc + (b_ - a_):
                            parts.append(a_ + (t - acc)); break
                        acc += b_ - a_
                    acc = 0.0
                xs = snap_all(xs + parts, zsegs)
            out.append({"a": a, "b": b, "L": L_, "segs": zsegs, "xs": xs, "up": len(xs) == 1 and Lr_ok(rest), "cy": r_["cy"],
                        "stems": stems, "rest": rest})
            continue
        # skylė - KIEKVIENOS prispaudžiamos dalies CENTRE, perkelta į artimiausią saugią dugno vietą
        xs = snap_all([a + L_ * (k + 0.5) / n for k in range(n)], zsegs)
        out.append({"a": a, "b": b, "L": L_, "segs": zsegs, "xs": xs, "up": n == 1 and L_ >= 2 * A.min_gap, "cy": r_["cy"]})
    ensure_min(out, 2)                           # ant bėgelio >= 2 skylės (raidė nesisuka): ilgiausia zona -> ketvirčiai
    return out


def Lr_ok(rest):
    return sum(b - a for a, b in rest) > 0


def snap(x, zs):
    """x -> artimiausias taškas zonos ruožuose (tarp akučių skylės nėra kur gręžti)"""
    for a, b in zs:
        if a <= x <= b:
            return x
    return min((q for a, b in zs for q in (a, b)), key=lambda q: abs(q - x))


def snap_all(xs, zs):
    out = []
    for x in xs:
        x = snap(x, zs)
        if all(abs(x - q) >= A.min_gap for q in out):
            out.append(x)
    return out


def ensure_min(segs, n_min):
    """kol skylių < n_min: ilgiausią plečiamą ruožą (1 skylė viduryje, L >= min_gap) perdaryti į 2 skyles galuose"""
    while sum(len(s_["xs"]) for s_ in segs) < n_min:
        cand = [s_ for s_ in segs if s_["up"]]
        if not cand:
            return False
        s_ = max(cand, key=lambda q: q["L"])
        if s_.get("stems"):                              # kojelė + pilvelis: kojelės varžtas lieka, antras - pilvelio centre
            rest = s_["rest"]; Lr = sum(b - a for a, b in rest); acc, t = 0.0, Lr / 2
            for a_, b_ in rest:
                if t <= acc + (b_ - a_):
                    s_["xs"] = snap_all(s_["xs"] + [a_ + (t - acc)], s_["segs"]); break
                acc += b_ - a_
            s_["up"] = False
            continue
        s_["xs"] = snap_all([s_["a"] + s_["L"] / 4, s_["a"] + 3 * s_["L"] / 4], s_["segs"]); s_["up"] = False   # ketvirčiuose
    return True


def seg_holes(segs):
    return [(round(x, 2), round(s_["cy"], 2)) for s_ in segs for x in s_["xs"]]


def pressed_ratio(back, holes):
    """prispausto dugno ploto dalis: dugnas ∩ (skrituliai R aplink skyles)"""
    if not holes or back.is_empty:
        return 0.0
    discs = unary_union([Point(x, y).buffer(A.press_r) for x, y in holes])
    return back.intersection(discs).area / back.area


warn = []


def same_letter(a, b):
    """vienodos raidės: tie patys gabaritai ir forma (perkelta - simetrinis skirtumas < 0,5 % ploto)"""
    ba, bb = a["geom"].bounds, b["geom"].bounds
    if abs((ba[2] - ba[0]) - (bb[2] - bb[0])) > 0.5 or abs((ba[3] - ba[1]) - (bb[3] - bb[1])) > 0.5:
        return False
    from shapely.affinity import translate
    g2 = translate(b["geom"], ba[0] - bb[0], ba[1] - bb[1])
    return a["geom"].symmetric_difference(g2).area < 0.005 * a["geom"].area


def holes_valid(o, holes):
    """perkeltos skylės tinka: dugne (>= hole_edge nuo krašto) ir ant bėgelio ašies tarp galų (rail_end_clear)"""
    safe = o["back"].buffer(-A.hole_edge, join_style=2, mitre_limit=10)
    for x, y in holes:
        if not safe.covers(Point(x, y)):
            return False
        if not any(abs(r_["cy"] - y) <= A.off_axis + 0.5 and r_["x0"] + 8 <= x <= r_["x1"] - 8 for r_ in rails):
            return False
    return True


for o in letters:
    back = K.dugnas_inset(o["geom"], A.inset, A.blunt_len)   # v108: smailios įpjovos nukertamos (2 taškai)
    o["back"] = back
# TAISYKLĖ (Rytis 2026-10-09): VISŲ VIENODŲ RAIDŽIŲ TVIRTINIMAI VIENODI - skylės skaičiuojamos pirmai raidei,
# kitoms tokioms pačioms perkeliamos; išimtis tik raidei, kuriai dėl kitokio rėmo (bėgelio galas, kita ašis) tų
# pačių vietų naudoti negalima - jai skaičiuojama atskirai ir rašomas perspėjimas.
done = []
for o in letters:
    back = o["back"]
    ref = next((d for d in done if same_letter(d, o)), None)
    if ref is not None:
        dx, dy = o["bb"][0] - ref["bb"][0], o["bb"][1] - ref["bb"][1]
        moved = [(round(x + dx, 2), round(y + dy, 2)) for x, y in ref["holes"]]
        if holes_valid(o, moved):
            o["holes"] = moved; o["same_as"] = ref["id"]
            o["zones"] = [dict(z, a=z["a"] + dx, b=z["b"] + dx, segs=[(a_ + dx, b_ + dx) for a_, b_ in z["segs"]],
                               xs=[x + dx for x in z["xs"]], cy=z["cy"] + dy) for z in ref["zones"]]
            o["pressed"] = pressed_ratio(back, o["holes"])
            done.append(o)
            continue
        warn.append(f"{o['id']}: vienoda su {ref['id']}, bet rėmas kitoks (bėgelio galas / ašis) - skylės skaičiuotos atskirai")
    segs_all = []
    for r_ in rails:
        if not (r_["y1"] > o["bb"][1] and r_["y0"] < o["bb"][3] and r_["x1"] > o["bb"][0] and r_["x0"] < o["bb"][2]):
            continue                              # v85: kelios eilutės - tik bėgeliai, kertantys šią raidę
        sg = holes_on_rail(back, r_, A.hole_edge)
        if not sg and A.hole_edge > 7:
            sg = holes_on_rail(back, r_, 7)
            if sg:
                warn.append(f"{o['id']}: bėgelis y{r_['cy']:.0f} - skylės tik su 7 mm atstumu nuo dugno krašto (siaura vieta)")
        if not sg:
            warn.append(f"{o['id']}: bėgelis y{r_['cy']:.0f} nekerta raidės dugno pakankamai - skylių nėra")
        segs_all += sg
    if not segs_all and VRAILS:                  # v85: akcentas (Ė taškas, Ū brūkšnys) - skylės ant vertikalaus laikiklio ašies
        from shapely.ops import transform as _tf
        for v_ in VRAILS:
            if not (v_["x1"] > o["bb"][0] and v_["x0"] < o["bb"][2] and v_["y1"] > o["bb"][1] and v_["y0"] < o["bb"][3]):
                continue
            bsw = _tf(lambda x, y, z=None: (y, x), back)   # noqa (shapely.ops.transform - veikia, perspėjimas ignoruojamas)
            rv = {"x0": v_["y0"], "x1": v_["y1"], "cy": v_["cx"], "y0": v_["cx"] - A.rail / 2, "y1": v_["cx"] + A.rail / 2}
            sg = holes_on_rail(bsw, rv, A.hole_edge) or holes_on_rail(bsw, rv, 7)
            for z in sg:
                z["vert"] = True
            segs_all += sg
            o["vrail"] = v_
        if segs_all:
            # akcentas mažas: D11 laikiklio ašyje akcento CENTRE (LED maitinimas per laikiklį), varžtai abipus jo
            # >= d11_fix_clear; netelpa 2 - vienas varžtas + D11 kitoje pusėje; netelpa ir tai - tik varžtas (perspėjimas)
            v_ = o["vrail"]
            ax = LineString([(v_["cx"], o["bb"][1] - 1), (v_["cx"], o["bb"][3] + 1)]).intersection(back.buffer(-A.hole_edge, join_style=2, mitre_limit=10))
            ys_ = sorted(c[1] for g_ in getattr(ax, "geoms", [ax]) for c in getattr(g_, "coords", []))
            o["holes"], o["acc_d11"] = [], None
            if ys_:
                a_, b_ = ys_[0], ys_[-1]; c_ = (a_ + b_) / 2; cl = A.d11_fix_clear
                if b_ - a_ >= 2 * cl:
                    o["holes"] = [(round(v_["cx"], 2), round(a_, 2)), (round(v_["cx"], 2), round(b_, 2))]; o["acc_d11"] = (round(v_["cx"], 2), round(c_, 2))
                elif b_ - a_ >= cl:
                    o["holes"] = [(round(v_["cx"], 2), round(a_, 2))]; o["acc_d11"] = (round(v_["cx"], 2), round(b_, 2))
                else:
                    o["holes"] = [(round(v_["cx"], 2), round(c_, 2))]
            if not o["holes"]:
                o["holes"] = [(round(s_["cy"], 2), round(x, 2)) for s_ in segs_all for x in s_["xs"]]   # atgal (x, y)
            o["zones"] = []
            o["pressed"] = pressed_ratio(back, o["holes"])
            done.append(o)
            warn.append(f"{o['id']}: akcentas - {len(o['holes'])} skylės ant vertikalaus laikiklio ašies x{o['vrail']['cx']:.0f}")
            continue
    ensure_min(segs_all, 4)                      # raidei >= 4: ilgiausi vienos skylės ruožai -> skylės galuose
    o["holes"] = seg_holes(segs_all)
    o["zones"] = segs_all
    # v194 (Rytis 2026-10-13, „Alytus," kablelis): raidė / elementas, per kurį eina LAIKIKLIS (acc statmuo nuo bėgelio), - skylės
    #  IR ant laikiklio ašies (tolimame gale ir, jei ilgas, viduryje), kad elementas nelaikytų tik ant 2 taškų bėgelyje
    for v_ in VRAILS:
        if not v_.get("acc") or not (v_["x1"] > o["bb"][0] and v_["x0"] < o["bb"][2] and v_["y1"] > o["bb"][1] and v_["y0"] < o["bb"][3]):
            continue
        ax = LineString([(v_["cx"], v_["y0"]), (v_["cx"], v_["y1"])]).intersection(back.buffer(-A.hole_edge, join_style=2, mitre_limit=10))
        ys_ = sorted(c[1] for g_ in getattr(ax, "geoms", [ax]) for c in getattr(g_, "coords", []))
        if not ys_:
            warn.append(f"{o['id']}: laikiklio x{v_['cx']:.0f} ašis nekerta dugno - skylių ant laikiklio nėra"); continue
        old_ys = [h[1] for h in o["holes"]]
        # tolimesnis nuo bėgelio galas: tas, kuris toliau nuo esamų (bėgelio) skylių
        far = max((ys_[0], ys_[-1]), key=lambda y: min([abs(y - q) for q in old_ys] or [1e9]))
        near = ys_[0] if far == ys_[-1] else ys_[-1]
        add = [far]
        if abs(far - near) >= 2 * A.d11_fix_clear + 60:
            add.append((far + near) / 2)
        for y in add:
            if all(math.hypot(v_["cx"] - hx, y - hy) >= 25 for hx, hy in o["holes"]):
                o["holes"].append((round(v_["cx"], 2), round(y, 2)))
        o["pressed"] = pressed_ratio(back, o["holes"])
        warn.append(f"{o['id']}: + {len(add)} skylės ant laikiklio ašies x{v_['cx']:.0f} (elementas ne tik ant bėgelio)")
    o["pressed"] = pressed_ratio(back, o["holes"])
    done.append(o)
    if len(o["holes"]) < 4:
        warn.append(f"{o['id']}: tik {len(o['holes'])} tvirtinimo skylės (< 4) - tikrinti / pridėti ranka")

# ------------------------------------------------------------------ D11 laido išvestis (Rytis 2026-10-09)
# Viena skylė raidei, bėgelio ašyje (laidas pro dugną į U profilio vidų -> prie sienos), dugne >= d11_edge nuo krašto,
# >= d11_fix_clear nuo D3.2 centrų. Vieta: toliausiai nuo tvirtinimo skylių, tarp lygiaverčių - arčiausiai raidės vidurio.
# Du variantai: viršutinis bėgelis ("top") / apatinis ("bottom") - atskiri DXF rinkiniai. Vienodoms raidėms - vienoda.
def d11_pos(o, r_, edge=None):
    """-> ((x, y), atstumas iki dugno krašto) arba None. Kandidatai - visos vietos su >= D11_EDGE_MIN nuo dugno
    krašto; rinktis: 1) kuo arčiau raidės centro (50 mm juostomis), 2) juostoje - kuo toliau nuo krašto (iki d11_edge)"""
    safe = o["back"].buffer(-D11_EDGE_MIN, join_style=2, mitre_limit=10)
    if safe.is_empty:
        return None
    ax0, ax1 = r_["x0"] + A.rail_end_clear + A.d11 / 2, r_["x1"] - A.rail_end_clear - A.d11 / 2
    if ax1 <= ax0:
        return None
    cut = LineString([(ax0, r_["cy"]), (ax1, r_["cy"])]).intersection(safe)
    segs = [q for q in getattr(cut, "geoms", [cut]) if isinstance(q, LineString) and q.length > 0.5]
    cx = (o["bb"][0] + o["bb"][2]) / 2
    bnd = o["back"].boundary
    best = None
    for q in segs:
        a, b = q.bounds[0], q.bounds[2]
        for k in range(int(b - a) + 1):
            x = a + k
            if any(math.hypot(x - hx, r_["cy"] - hy) < A.d11_fix_clear for hx, hy in o["holes"]):
                continue
            de = bnd.distance(Point(x, r_["cy"]))
            key = (-(abs(x - cx) // 50), min(de, A.d11_edge), -abs(x - cx))
            if best is None or key > best[0]:
                best = (key, (round(x, 2), round(r_["cy"], 2)), de)
    return (best[1], best[2]) if best else None


def d11_pair(o, r_):
    """Štrichas ant bėgelio (zona su 1 skyle centre): varžtas ir D11 - PORA, centruota per štricho centrą
    (varžtas c -/+ s/2, D11 kitoje pusėje, s = d11_fix_clear; D11 - raidės centro pusėje). Zona su >= 2 skylėmis -
    D11 centre tarp dviejų arčiausiai raidės centro esančių varžtų. Zonos tikrinamos nuo arčiausios raidės centrui.
    -> (d11, holes_v, atstumas iki dugno krašto) arba None"""
    zs = [z for z in o.get("zones", []) if abs(z["cy"] - r_["cy"]) < 0.5]
    if not zs:
        return None
    cx = (o["bb"][0] + o["bb"][2]) / 2
    safe = o["back"].buffer(-A.hole_edge, join_style=2, mitre_limit=10)
    safe11 = o["back"].buffer(-D11_EDGE_MIN, join_style=2, mitre_limit=10)
    bnd = o["back"].boundary
    ax0, ax1 = r_["x0"] + A.rail_end_clear, r_["x1"] - A.rail_end_clear
    y = r_["cy"]
    # siauram štrichui poros atstumas mažinamas pakopomis iki 12 mm (D11 r5,5 + varžtas r1,6 + >= 4 mm tiltelis)
    for sclr in [c_ for c_ in (A.d11_fix_clear, 18, 14, 12) if c_ <= A.d11_fix_clear]:
        for z in sorted(zs, key=lambda z: abs((z["a"] + z["b"]) / 2 - cx)):
            c = (z["a"] + z["b"]) / 2
            if len(z["xs"]) != 1:
                continue
            sgn = 1 if cx >= c else -1
            hx, dx_ = c - sgn * sclr / 2, c + sgn * sclr / 2
            if not (safe.covers(Point(hx, y)) and safe11.covers(Point(dx_, y)) and ax0 <= hx <= ax1
                    and ax0 + A.d11 / 2 <= dx_ <= ax1 - A.d11 / 2):
                continue
            others = [h for h in o["holes"] if not (abs(h[1] - y) < 0.5 and abs(h[0] - z["xs"][0]) < 0.5)]
            if any(math.hypot(dx_ - qx, y - qy) < sclr for qx, qy in others):
                continue
            holes_v = others + [(round(hx, 2), round(y, 2))]
            if sclr < A.d11_fix_clear:
                warn.append(f"{o['id']}: D11 pora {sclr:g} mm nuo varžto (< {A.d11_fix_clear:g}, siauras štrichas)")
            return (round(dx_, 2), round(y, 2)), holes_v, bnd.distance(Point(dx_, y))
    sclr = A.d11_fix_clear
    for z in sorted(zs, key=lambda z: abs((z["a"] + z["b"]) / 2 - cx)):
        xs = sorted(z["xs"], key=lambda x: abs(x - cx))[:2]
        if len(xs) == 2:
            m = sum(xs) / 2
            if abs(xs[0] - xs[1]) >= 2 * sclr and safe11.covers(Point(m, y)):
                return (round(m, 2), round(y, 2)), list(o["holes"]), bnd.distance(Point(m, y))
        # tarp varžtų netelpa (lankas išeina iš ašies) - D11 ŠALIA arčiausio raidės centrui varžto, zonos vidurio pusėje
        zc = (z["a"] + z["b"]) / 2
        for x in sorted(z["xs"], key=lambda x: abs(x - cx)):
            for sgn in ((1, -1) if zc >= x else (-1, 1)):
                d = x + sgn * sclr
                if (safe11.covers(Point(d, y)) and ax0 + A.d11 / 2 <= d <= ax1 - A.d11 / 2
                        and all(math.hypot(d - qx, y - qy) >= sclr for qx, qy in o["holes"])):
                    return (round(d, 2), round(y, 2)), list(o["holes"]), bnd.distance(Point(d, y))
    return None


def d11_replace(o, r_):
    """Rytis 2026-10-09: D11 VISADA bėgelio ašyje. Kai šalia esamų varžtų netelpa - D11 dedama ašyje (saugi zona
    >= D11_EDGE_MIN), o tos zonos varžtai PERSTATOMI į likusias saugias vietas (kiekis išlaikomas, dalių centrai).
    Kandidatai - nuo arčiausio raidės centrui. -> (d11, holes_v, de) arba None"""
    zs = [z for z in o.get("zones", []) if abs(z["cy"] - r_["cy"]) < 0.5]
    y = r_["cy"]; cx = (o["bb"][0] + o["bb"][2]) / 2
    safe11 = o["back"].buffer(-D11_EDGE_MIN, join_style=2, mitre_limit=10)
    if safe11.is_empty:
        return None
    bnd = o["back"].boundary
    ax0, ax1 = r_["x0"] + A.rail_end_clear + A.d11 / 2, r_["x1"] - A.rail_end_clear - A.d11 / 2
    if ax1 <= ax0:
        return None
    cut = LineString([(ax0, y), (ax1, y)]).intersection(safe11)
    cands = sorted([a + k for q in getattr(cut, "geoms", [cut]) if isinstance(q, LineString) and q.length > 0.5
                    for a, b in [(q.bounds[0], q.bounds[2])] for k in range(int(b - a) + 1)], key=lambda x: abs(x - cx))
    best = None
    for d in cands:
        z = next((z for z in zs if z["a"] - 0.5 <= d <= z["b"] + 0.5), None)
        others = [h for h in o["holes"] if not (abs(h[1] - y) < 0.5 and z and z["a"] - 0.5 <= h[0] <= z["b"] + 0.5)]
        if any(math.hypot(d - qx, y - qy) < A.d11_fix_clear for qx, qy in others):
            continue
        if z is None:
            continue
        avail = []
        for a, b in z["segs"]:                        # zonos saugūs ruožai be D11 išskirties
            for a2, b2 in ((a, min(b, d - A.d11_fix_clear)), (max(a, d + A.d11_fix_clear), b)):
                if b2 - a2 >= 0:
                    avail.append((a2, b2))
        if not avail:
            continue
        n = len(z["xs"])
        parts = [z["a"] + z["L"] * (k + 0.5) / n for k in range(n)]
        new = snap_all(parts, avail)
        if len(new) < n:                              # dalių centrai užimti - dėti tolygiai į laisvus ruožus
            new = snap_all([a + (b - a) * (k + 0.5) / max(1, n) for a, b in avail for k in range(max(1, n))], avail)[:n]
        key = (len(new) >= n, -abs(d - cx))
        if best is None or key > best[0]:
            best = (key, (round(d, 2), round(y, 2)), others + [(round(x, 2), round(y, 2)) for x in new], bnd.distance(Point(d, y)), len(new) - n)
        if key[0]:
            break
    if best is None:
        return None
    return best[1], best[2], best[3], best[4]


D11_EDGE_MIN = 8.0          # mažiausias D11 centro atstumas nuo dugno krašto (siauros raidės): kraštas 2,5 mm nuo kontūro


def d11_valid(o, pt, r_, holes=None):
    x, y = pt
    safe = o["back"].buffer(-D11_EDGE_MIN, join_style=2, mitre_limit=10)
    on_rail = abs(r_["cy"] - y) < 0.5 and r_["x0"] + A.rail_end_clear + A.d11 / 2 <= x <= r_["x1"] - A.rail_end_clear - A.d11 / 2
    return (safe.covers(Point(x, y)) and on_rail
            and all(math.hypot(x - hx, y - hy) >= A.d11_fix_clear for hx, hy in (holes if holes is not None else o["holes"])))


def d11_with_shift(o, r_, edge=None):
    """atsarginis variantas (siaura kojelė): D11 ilgiausio ruožo CENTRE, to bėgelio varžtai tame ruože perstumiami
    simetriškai į šalis (D11 +- max(fix_clear, L/4)); kiti varžtai nekeičiami. -> (d11, holes) arba None"""
    safe = o["back"].buffer(-A.hole_edge, join_style=2, mitre_limit=10)
    safe11 = o["back"].buffer(-(edge or A.d11_edge), join_style=2, mitre_limit=10)
    ax0, ax1 = r_["x0"] + A.rail_end_clear, r_["x1"] - A.rail_end_clear
    cut = LineString([(ax0, r_["cy"]), (ax1, r_["cy"])]).intersection(safe)
    segs = [q for q in getattr(cut, "geoms", [cut]) if isinstance(q, LineString) and q.length > 0.5]
    if not segs:
        return None
    q = max(segs, key=lambda q_: q_.length)
    a, b = q.bounds[0], q.bounds[2]; L_ = b - a; cx = (a + b) / 2
    on_seg = [h for h in o["holes"] if abs(h[1] - r_["cy"]) < 0.5 and a - 0.5 <= h[0] <= b + 0.5]
    others = [h for h in o["holes"] if h not in on_seg]
    d = max(A.d11_fix_clear, L_ / 4)
    new = [(round(cx - d, 2), round(r_["cy"], 2)), (round(cx + d, 2), round(r_["cy"], 2))] if len(on_seg) >= 2 \
        else ([(round(cx + d, 2), round(r_["cy"], 2))] if on_seg else [])
    pt = (round(cx, 2), round(r_["cy"], 2))
    if not safe11.covers(Point(pt)) or not all(safe.covers(Point(h)) and ax0 <= h[0] <= ax1 for h in new):
        return None
    return pt, others + new


# v69 (Rytis 2026-10-09, AAA „s"): raidės dugno dalis ant bėgelio, kurios neprispaudžia jokia skylė (už R nuo visų
# to bėgelio skylių; pvz. „s" lanko galas prie bėgelio galo), VIS TIEK gauna tvirtinimo skylę. Ašyje vietos nėra - skylė
# leidžiama U sienelėje iki --off-axis (8) nuo ašies, >= 7 mm nuo dugno krašto, >= 8 mm nuo bėgelio galo; perspėjimas.
for o in letters:
    added = []
    for r_ in rails:
        band = o["back"].intersection(sbox(r_["x0"], r_["cy"] - A.rail / 2, r_["x1"], r_["cy"] + A.rail / 2))
        if band.is_empty:
            continue
        rh = [h for h in o["holes"] if abs(h[1] - r_["cy"]) <= A.off_axis + 0.5]
        if not rh:
            continue
        cov = unary_union([Point(h).buffer(A.press_r) for h in rh])
        rest = band.difference(cov)
        for part in sorted(getattr(rest, "geoms", [rest]), key=lambda g_: -g_.area):
            # v195: tik reikšminga neprispausta dalis (>= R / 2 ilgio išilgai bėgelio), ne kampų likučiai - kitaip mažos raidės
            #  gauna daugiau skylių nei didelės
            if part.is_empty or part.area < 150 or (part.bounds[2] - part.bounds[0]) < A.press_r / 2:
                continue
            safe = o["back"].buffer(-7, join_style=2, mitre_limit=10)
            bnd = o["back"].boundary
            best = None
            px0, px1 = max(part.bounds[0], r_["x0"] + 8), min(part.bounds[2], r_["x1"] - 8)
            x = px0
            while x <= px1:
                for dy in [0, 1, -1, 2, -2, 3, -3, 4, -4, 5, -5, 6, -6, 7, -7, 8, -8]:
                    if abs(dy) > A.off_axis:
                        continue
                    q = Point(x, r_["cy"] + dy)
                    if safe.covers(q) and all(math.hypot(x - hx, q.y - hy) >= 2 * A.min_gap for hx, hy in o["holes"] + added):
                        k = (round(bnd.distance(q), 1) >= A.hole_edge, -abs(dy) // 3, bnd.distance(q))
                        if best is None or k > best[0]:
                            best = (k, (round(x, 2), round(q.y, 2)), dy, bnd.distance(q))
                x += 1
            if best:
                added.append(best[1])
                warn.append(f"{o['id']}: papildoma skylė neprispaustoje dugno dalyje prie bėgelio y{r_['cy']:.0f}"
                            + (f", {abs(best[2]):g} mm nuo ašies" if best[2] else "") + f", {best[3]:.0f} mm nuo dugno krašto")
            else:
                w_ = f"{o['id']}: dugno dalis prie bėgelio y{r_['cy']:.0f} (x ~{part.bounds[0]:.0f}) neprispausta, skylė netelpa - tikrinti / dėti ranka"
                if not any(w.startswith(w_.split(" (x")[0]) for w in warn):
                    warn.append(w_)
    if added:
        o["holes"] = o["holes"] + added
        o["pressed"] = pressed_ratio(o["back"], o["holes"])
        warn[:] = [w for w in warn if not w.startswith(f"{o['id']}: tik ")]
        if len(o["holes"]) < 4:
            warn.append(f"{o['id']}: tik {len(o['holes'])} tvirtinimo skylės (< 4) - tikrinti / pridėti ranka")


CABLE_VARIANTS = {"top": ["top"], "bottom": ["bottom"], "both": ["top", "bottom"], "none": []}[A.cable]
SEPARATE = bool(A.separate)
if SEPARATE:                                         # v90: D11 skaičiuojama atskirai (bendra linija)
    VRAILS = []
    _cv_sep, CABLE_VARIANTS = (["line"] if A.cable != "none" else []), []
if len(rails) < 2 and CABLE_VARIANTS:
    CABLE_VARIANTS = ["top"] if rails else []
for var in CABLE_VARIANTS:
    ref_pts = {}
    for o in letters:
        pt, holes_v = None, list(o["holes"])
        _cr = [q for q in rails if q["y1"] > o["bb"][1] and q["y0"] < o["bb"][3] and q["x1"] > o["bb"][0] and q["x0"] < o["bb"][2]]
        if not _cr:                               # v85: akcentas - D11 ant laikiklio ašies, akcento centre (jei telpa)
            v_ = o.get("vrail")
            if v_:
                pt = o.get("acc_d11")
                if pt is None and var == CABLE_VARIANTS[0]:
                    warn.append(f"{o['id']}: akcentas per mažas D11 su {A.d11_fix_clear:g} mm iki varžto - laidas per laikiklio galą, dėti ranka")
            o.setdefault("d11", {})[var] = pt
            o.setdefault("holes_var", {})[var] = holes_v
            ref_pts[o["id"]] = (pt, holes_v)
            continue
        r_ = min(_cr, key=lambda q: q["cy"]) if var == "top" else max(_cr, key=lambda q: q["cy"])
        ref = o.get("same_as")
        if ref and ref in ref_pts and ref_pts[ref][0]:
            (rx, ry), rh = ref_pts[ref]
            ro = next(d for d in letters if d["id"] == ref)
            dx, dy = o["bb"][0] - ro["bb"][0], o["bb"][1] - ro["bb"][1]
            cand = (round(rx + dx, 2), round(ry + dy, 2))
            cand_h = [(round(x + dx, 2), round(y + dy, 2)) for x, y in rh]
            if holes_valid(o, cand_h) and d11_valid(o, cand, r_, cand_h):
                pt, holes_v = cand, cand_h
        # v67 (Rytis 2026-10-09, AAA „d"): D11 tik PLAČIOJE vietoje - siauri ruožai skirti LED. Pirma ieškoma VISOJE
        # bėgelio ašyje (kairėje / dešinėje raidės dalyje) su pilnu d11_edge (20 mm); atstumas iki krašto mažinamas
        # tik jei pilno nėra NIEKUR ant to bėgelio (ne todėl, kad arčiau raidės centro).
        _emin0 = D11_EDGE_MIN
        for e_lvl in sorted({e for e in [A.d11_edge, 15, 12, 10, _emin0] if _emin0 <= e <= A.d11_edge}, reverse=True):
            if pt is not None:
                break
            D11_EDGE_MIN = e_lvl
            _w0 = len(warn)
            res = d11_pair(o, r_)
            if res:
                pt, holes_v, de = res
            if pt is None:
                res = d11_pos(o, r_)
                if res:
                    pt, de = res
            if pt is None:
                res = d11_with_shift(o, r_, e_lvl)
                if res:
                    pt, holes_v = res
                    warn.append(f"{o['id']}: D11 ({var}) ruožo centre ({e_lvl:g} mm nuo krašto), to bėgelio varžtai perstumti į šalis")
            if pt is None:
                res = d11_replace(o, r_)
                if res:
                    pt, holes_v, de, lost = res
                    warn.append(f"{o['id']}: D11 ({var}) ašyje, tos zonos varžtai perstatyti"
                                + (f" ({-lost} varžtu mažiau - netilpo)" if lost < 0 else "") + f", {de:.0f} mm nuo dugno krašto")
            if pt is None:
                del warn[_w0:]
            elif e_lvl < A.d11_edge:
                warn.append(f"{o['id']}: D11 ({var}) {e_lvl:g} mm nuo dugno krašto (< {A.d11_edge:g}) - plačios vietos ant bėgelio nėra")
            if pt is not None and ref:
                warn.append(f"{o['id']}: D11 ({var}) negali būti kaip {ref} (rėmas) - skaičiuota atskirai")
        D11_EDGE_MIN = _emin0
        if pt is None:
            warn.append(f"{o['id']}: D11 ({var}) bėgelio ašyje vietos nėra (dugnas < 16 mm) - dėti ranka")
        o.setdefault("d11", {})[var] = pt
        o.setdefault("holes_var", {})[var] = holes_v
        ref_pts[o["id"]] = (pt, holes_v)

# ------------------------------------------------------------------ v90: atskiros raidės - D11 vienoje horizontalioje linijoje
# Rytis 2026-10-11: atskiros raidės be rėmo; iš kiekvienos raidės 12V 1,5 m laidas, išvestys VIENOJE horizontalioje
# linijoje per visas raides (arba WAGO viduje - tada linija vis tiek žymima kaip įvado vieta). Linija parenkama taip,
# kad visose raidėse dugnas būtų kuo platesnis (>= d11_edge nuo krašto), D11 - plačiausio ruožo viduryje, >= d11_fix_clear nuo varžtų.
if SEPARATE and _cv_sep:
    _main = [o for o in letters if not o.get("vrail")] or letters
    _y0 = max(min(o["bb"][1] for o in _main), 0) + 1
    _y1 = max(o["bb"][3] for o in _main) - 1
    best_line = None
    for e_ in sorted({e for e in [A.d11_edge, 15, 12, 10, 8] if e <= A.d11_edge}, reverse=True):
        _safe = {o["id"]: o["back"].buffer(-e_, join_style=2, mitre_limit=10) for o in _main}
        y = _y0
        while y <= _y1:
            segs_ = []
            for o in _main:
                q = _safe[o["id"]].intersection(LineString([(o["bb"][0] - 1, y), (o["bb"][2] + 1, y)]))
                parts = [g_ for g_ in getattr(q, "geoms", [q]) if not g_.is_empty and g_.length > 0]
                if not parts:
                    segs_ = None
                    break
                segs_.append(max(parts, key=lambda g_: g_.length))
            if segs_:
                sc_ = min(g_.length for g_ in segs_)
                if best_line is None or sc_ > best_line[0]:
                    best_line = (sc_, y, segs_, e_)
            y += 2
        if best_line:
            break
    if best_line is None:
        warn.append("bendros horizontalios linijos per visas raides D11 nėra - laidų išvestis dėti ranka")
    else:
        _, yl, segs_, e_ = best_line
        if e_ < A.d11_edge:
            warn.append(f"D11 linija: {e_:g} mm nuo dugno krašto (< {A.d11_edge:g}) - plačios bendros vietos nėra")
        for o, sg in zip(_main, segs_):
            (ax_, _), (bx_, _) = sg.coords[0], sg.coords[-1]
            xa, xb = sorted((ax_, bx_))
            cands = sorted(range(int(xa), int(xb) + 1), key=lambda x: abs(x - (xa + xb) / 2))
            pt = next(((float(x), float(yl)) for x in cands
                       if all(math.hypot(x - hx, yl - hy) >= A.d11_fix_clear for hx, hy in o["holes"])), None)
            if pt is None:
                pt = ((xa + xb) / 2, yl)
                warn.append(f"{o['id']}: D11 linijoje arčiau nei {A.d11_fix_clear:g} mm iki varžto - tikrinti")
            o.setdefault("d11", {})["line"] = (round(pt[0], 2), round(pt[1], 2))
            o.setdefault("holes_var", {})["line"] = list(o["holes"])
        for o in letters:
            if o not in _main:
                o.setdefault("d11", {})["line"] = None
                warn.append(f"{o['id']}: akcentas - laido išvestis atskirai, dėti ranka")
        print(f"  D11 linija: y {PH - yl:.0f} nuo apačios ({yl:.0f} nuo viršaus), plačiausias bendras ruožas >= {best_line[0]:.0f} mm")
        CABLE_VARIANTS = ["line"]
# v268 (Rytis 2026-10-15, OMODA PO 33580): atskiroms raidėms tvirtinimo ir laido skylės - TOS PAČIOS kaip techniniame lape
#  (braizyti_begeliai -> rails json "fix_holes" / "cable_holes"); tada skaičiuotos ant ašių skylės ir D11 linija pakeičiamos
if A.rails_json and SEPARATE:
    _rjh = json.load(open(A.rails_json))
    _FH = [(h_[0] + _dx, h_[1] + _dy) for h_ in _rjh.get("fix_holes", [])]
    _CH = [(h_[0] + _dx, h_[1] + _dy) for h_ in _rjh.get("cable_holes", [])]
    if _FH or _CH:
        warn[:] = [w for w in warn if "tvirtinimo skyl" not in w and "D11" not in w and "akcentas" not in w]
        for o in letters:
            _bk = o["back"].buffer(0.5)
            if _FH:
                o["holes"] = [(round(x, 2), round(y, 2)) for x, y in _FH if _bk.contains(Point(x, y))]
                o.pop("holes_var", None)
                if len(o["holes"]) < 2:
                    warn.append(f"{o['id']}: tik {len(o['holes'])} tvirtinimo skylės iš lapo - tikrinti")
            _c = [(round(x, 2), round(y, 2)) for x, y in _CH if _bk.contains(Point(x, y))]
            o.setdefault("d11", {})["line"] = _c[0] if _c else None
            if not _c:
                warn.append(f"{o['id']}: laido išvesties iš lapo nėra - tikrinti")
        CABLE_VARIANTS = ["line"]
        print(f"  skylės iš lapo: tvirtinimo {len(_FH)}, laido D11 {len(_CH)}")

# ------------------------------------------------------------------ v98: drenažas (exterior)
# Rytis 2026-10-11: lauko reklamos raidė turi D8 išpjovą apatinėje dalyje kaip drenažą - PAČIOJE ŽEMIAUSIOJE vietoje;
# kiekviena atskira „kišenė" gauna savo (pvz. „a": viršutinės dalies užlenkimo apačia, pilvelis, kojelė - 3 išpjovos).
# Ieškoma dugno IŠORINIO kontūro lokalių žemiausių taškų (vanduo raidės viduje teka ant šono žemyn), kai iš abiejų
# pusių kontūras pakyla >= 5 mm; plokščia apačia - jos vidurys. Išpjova - Ø8 skylutė VISA dugno viduje prie pat žemiausio taško
# (v99: neišeina už dugno linijos). Vidaus iškabai (`--interior`) - nėra.
def drain_points(back, prom=5.0, step=1.0, merge=30.0, r=4.0, gap=1.0):
    out = []
    for poly in getattr(back, "geoms", [back]):
        if poly.is_empty or not hasattr(poly, "exterior"):
            continue
        ring = poly.exterior
        L = ring.length
        n = max(16, int(L / step))
        pts = [ring.interpolate(L * i / n) for i in range(n)]
        ys = [p.y for p in pts]                     # y žemyn: didesnis = žemiau
        for i in range(n):
            y = ys[i]
            if y < ys[i - 1] - 1e-6 or y < ys[(i + 1) % n] - 1e-6:
                continue
            ok = True
            span = [i]
            for dirn in (1, -1):                     # abiem kryptimis pakilti >= prom, nenusileidus žemiau
                j, rose = i, False
                for _ in range(n):
                    j = (j + dirn) % n
                    if ys[j] > y + 0.3:
                        ok = False; break
                    if abs(ys[j] - y) <= 0.3:
                        span.append(j)
                    if ys[j] <= y - prom:
                        rose = True; break
                if not ok or not rose:
                    ok = False; break
            if not ok:
                continue
            xs_ = sorted(pts[k].x for k in span)
            xm = (xs_[0] + xs_[-1]) / 2
            q = min((pts[k] for k in span), key=lambda p: abs(p.x - xm))
            if not (poly.contains(Point(q.x, q.y - 6)) and poly.contains(Point(q.x, q.y - 2.5))
                    and not poly.contains(Point(q.x, q.y + 2.5))):      # medžiaga virš taško, po juo - tuščia: raidės dugnas
                continue                                               # (ne iš viršaus atviros įpjovos apačia)
            # v99 (Rytis 2026-10-11): skylutė NEIŠEINA už dugno linijos - visa dugno viduje, prie pat žemiausio taško
            #  (centras r + 1 mm virš kontūro); netelpa - pastumiama aukštyn iki +4 mm, kitaip praleidžiama su perspėjimu
            c_ = None
            for up_ in (0.0, 1.0, 2.0, 3.0, 4.0):
                cand = Point(q.x, q.y - (r + gap + up_))
                if poly.buffer(-0.3).contains(cand.buffer(r)):
                    c_ = cand; break
            if c_ is None:
                warn.append(f"drenažas x{q.x - GX0:.0f}: Ø{2 * r:g} netelpa dugne prie žemiausio taško - dėti ranka")
                continue
            if all(math.hypot(c_.x - a, c_.y - b) > merge for a, b in out):
                out.append((round(c_.x, 2), round(c_.y, 2)))
    return out


DRAIN = not A.interior
if DRAIN:
    for o in letters:
        o["drain"] = drain_points(o["back"], r=A.drain_d / 2)
    print(f"  drenažas (exterior): Ø{A.drain_d:g} skylutės dugne prie žemiausių vietų - " +
          ", ".join(f"{o['id']} {len(o['drain'])}" for o in letters))
    for o in letters:
        if o["drain"]:
            print(f"    {o['id']}: " + ", ".join(f"({x - GX0:.0f}; {PH - y:.0f})" for x, y in o["drain"]))

# ------------------------------------------------------------------ v112: plokštė + raidė ant jos (EXTRA X ant apskritimo)
# Etalonas - Ryčio „extra_darbiniai" (Corel): X atskirai KAIRIAU apskritimo (stiklas + dugnas -3 + Ø4 distancerių skylės
# + Ø11 laidui), apskritimas su TOMIS PAČIOMIS skylėmis VEIDRODIŠKAI (plokštė žiūrint iš galo). Distancerių skylės:
# centre (didžiausio įbrėžto apskritimo vieta) + po vieną kiekviename kampiniame bbox ketvirtyje (X - 4 galai).
# Laido Ø11 - apatiniame ketvirtyje pagrindinių raidžių pusėje, 25 mm virš distancerio (kaip etalone).
try:
    from shapely.ops import polylabel as _polylabel
except ImportError:
    from shapely.algorithms.polylabel import polylabel as _polylabel


def _pole(g):
    g = max(getattr(g, "geoms", [g]), key=lambda q: q.area)
    p_ = _polylabel(g, tolerance=0.5)
    return (p_.x, p_.y)


if PLATES:
    _main_cx = (min(o["bb"][0] for o in letters) + max(o["bb"][2] for o in letters)) / 2 if letters else 0
    for pl_ in PLATES:
        pb_ = pl_["geom"].bounds
        pl_["holes"], pl_["d11"] = [], None
        for o in pl_["let"]:
            o["bb"] = o["geom"].bounds
            o["back"] = K.dugnas_inset(o["geom"], A.inset, A.blunt_len)
            safe_ = o["back"].buffer(-A.spacer_edge, join_style=2, mitre_limit=10)
            x0_, y0_, x1_, y1_ = o["bb"]; w_, h_ = x1_ - x0_, y1_ - y0_
            hs_ = []
            # v115 (Rytis 2026-10-12): VIENAS RĖMAS - X tvirtinimas kaip raidžių: skylės ant bėgelio profilio
            # horizontalios ašies (holes_on_rail), ne „centras + 4 galai"
            _xr = [r_ for r_ in rails if r_["x0"] < x1_ and r_["x1"] > x0_ and y0_ < r_["cy"] < y1_]
            for r_ in _xr:
                for z_ in holes_on_rail(o["back"], r_, A.hole_edge):
                    hs_ += [(x_, r_["cy"]) for x_ in z_["xs"]]
            o["on_rails"] = bool(hs_)
            if o["on_rails"]:
                print(f"  raidė ant plokštės: tvirtinimas ant bėgelių ašių ({len(_xr)} bėg.) - {len(hs_)} x Ø{A.spacer_d:g}")
            if not hs_ and not safe_.is_empty:
                hs_.append(_pole(safe_))
                for qx0, qx1 in ((x0_, x0_ + 0.4 * w_), (x1_ - 0.4 * w_, x1_)):
                    for qy0, qy1 in ((y0_, y0_ + 0.3 * h_), (y1_ - 0.3 * h_, y1_)):
                        q_ = safe_.intersection(sbox(qx0, qy0, qx1, qy1))
                        if not q_.is_empty and q_.area > 1:
                            hs_.append(_pole(q_))
            if len(hs_) < (4 if o["on_rails"] else 5):
                print(f"  ! raidė ant plokštės: tik {len(hs_)} Ø{A.spacer_d:g} skylės - tikrinti / dėti ranka")
            o["sp_holes"] = hs_
            o["d11p"] = None
            if A.cable != "none" and o["on_rails"]:          # v115: D11 - apatinio bėgelio ašyje, kaip raidėms
                rb_ = max(_xr, key=lambda r_: r_["cy"])
                ax_ = LineString([(x0_, rb_["cy"]), (x1_, rb_["cy"])]).intersection(o["back"].buffer(-A.d11_edge))
                cands_ = []
                for g_ in getattr(ax_, "geoms", [ax_]):
                    if isinstance(g_, LineString) and g_.length > 0:
                        a_, b_ = g_.bounds[0], g_.bounds[2]
                        cands_ += [a_ + (b_ - a_) * k / 20 for k in range(21)]
                cands_ = [x_ for x_ in cands_ if all(math.dist((x_, rb_["cy"]), h_) >= A.d11_fix_clear for h_ in hs_)]
                if cands_:
                    right_ = _main_cx >= (x0_ + x1_) / 2
                    o["d11p"] = (max(cands_) if right_ else min(cands_), rb_["cy"])
                else:
                    print("  ! raidė ant plokštės: Ø11 apatinio bėgelio ašyje netelpa - dėti ranka")
            elif A.cable != "none" and hs_:
                right_ = _main_cx >= (x0_ + x1_) / 2
                bot_ = [q for q in hs_[1:] if q[1] > (y0_ + y1_) / 2] or hs_[1:]
                if bot_:
                    bq = max(bot_, key=lambda q: q[0]) if right_ else min(bot_, key=lambda q: q[0])
                    for dy_ in (25, 35, 20, 45):
                        c_ = (bq[0], bq[1] - dy_)
                        if o["back"].buffer(-(A.d11 / 2 + 8)).contains(Point(c_)):
                            o["d11p"] = c_; break
                if o["d11p"] is None:
                    print("  ! raidė ant plokštės: Ø11 laido skylei vietos nerasta - dėti ranka")
            o["drain"] = drain_points(o["back"], r=A.drain_d / 2) if not A.interior else []
            # v118 (Rytis 2026-10-12): plokštėje pažymėti X tvirtinimo rėmai (H1800) -> vaizdas IŠ PRIEKIO (rėmo žymėjimas
            # iškart rodo pusę); rėmo žymėjimo nėra -> plokštė VEIDRODIŠKAI (iš galo) + C žyma galinėje pusėje
            mir_ = (lambda q: q) if A.plate_front else (lambda q: (pb_[0] + pb_[2] - q[0], q[1]))
            pl_["holes"] += [mir_(q) for q in hs_]
            if o["d11p"]:
                pl_["d11"] = mir_(o["d11p"])
            o["shift"] = pb_[0] - A.plate_gap - x1_                       # X - kairiau apskritimo
        pl_["mirror"] = (lambda q: q) if A.plate_front else (lambda q, b=pb_: (b[0] + b[2] - q[0], q[1]))
        pl_["cmark"] = None
        if not A.plate_front:                                   # C žyma - plokštės centre, toliau nuo skylių
            cx_, cy_ = (pb_[0] + pb_[2]) / 2, (pb_[1] + pb_[3]) / 2
            hs_all = pl_["holes"] + ([pl_["d11"]] if pl_["d11"] else [])
            inner_ = pl_["geom"].buffer(-(A.c_mark_r + 20))
            best_ = None
            for dx_ in range(-200, 201, 10):
                for dy_ in range(-200, 201, 10):
                    q_ = (cx_ + dx_, cy_ + dy_)
                    if not inner_.contains(Point(q_)):
                        continue
                    dmin = min([math.dist(q_, h_) for h_ in hs_all] or [1e9])
                    if dmin < A.c_mark_r + 15:
                        continue
                    k_ = math.hypot(dx_, dy_)
                    if best_ is None or k_ < best_[0]:
                        best_ = (k_, q_)
            pl_["cmark"] = best_[1] if best_ else None
            if not best_:
                print("  ! plokštė: C žymai vietos nerasta - dėti ranka")
        print(f"  plokštė {pb_[2] - pb_[0]:.0f} x {pb_[3] - pb_[1]:.0f}: Ø{A.spacer_d:g} x {len(pl_['holes'])}" +
              (f", Ø{A.d11:g} laidui" if pl_["d11"] else "") +
              (" (vaizdas iš priekio - rėmų žymėjimas)" if A.plate_front else " (veidrodiškai - plokštė iš galo, C žyma galinėje pusėje)"))
    GX0 = min([GX0] + [o["bb"][0] + o["shift"] for pl_ in PLATES for o in pl_["let"]] + [pl_["geom"].bounds[0] for pl_ in PLATES])
    GY1 = max([GY1] + [pl_["geom"].bounds[3] for pl_ in PLATES])


def put_plates(msp, var):
    """v112: plokštė (4_PLOKSTE, veidrodiškai) + raidė ant jos (perkelta kairiau, 1_PRIEKIS / 2_GALAS)"""
    for pl_ in PLATES:
        for o in pl_["let"]:
            T = lambda q, o=o: (q[0] + o["shift"] - GX0, GY1 - q[1])
            for ring in o["rings"]:
                add_ring(msp, [T(q) for q in ring], "1_PRIEKIS")
            for ring in rings_of(o["back"]):
                add_ring(msp, [T(q) for q in ring], "2_GALAS")
            for q in o["sp_holes"]:
                msp.add_circle(T(q), A.spacer_d / 2, dxfattribs={"layer": "2_GALAS"})
            for q in o.get("drain", []):
                msp.add_circle(T(q), A.drain_d / 2, dxfattribs={"layer": "2_GALAS"})
            if var and o.get("d11p"):
                msp.add_circle(T(o["d11p"]), A.d11 / 2, dxfattribs={"layer": "2_GALAS"})
        Tp = lambda q: (q[0] - GX0, GY1 - q[1])
        for ring in pl_["rings"]:
            add_ring(msp, [Tp(pl_["mirror"](q)) for q in ring], "4_PLOKSTE")
        for q in pl_["holes"]:
            msp.add_circle(Tp(q), A.spacer_d / 2, dxfattribs={"layer": "4_PLOKSTE"})
        if var and pl_["d11"]:
            msp.add_circle(Tp(pl_["d11"]), A.d11 / 2, dxfattribs={"layer": "4_PLOKSTE"})
        if pl_.get("cmark"):                                    # v118: C - galinė pusė (skaitoma iš galo)
            msp.add_arc(Tp(pl_["cmark"]), A.c_mark_r, 45, 315, dxfattribs={"layer": "5_C_ZYMA"})


# ------------------------------------------------------------------ DXF
os.makedirs(A.out_dir, exist_ok=True)
prefix = A.prefix or os.path.splitext(os.path.basename(A.pdf))[0]
LAY = (("1_PRIEKIS", 7), ("2_GALAS", 2), ("3_REMAS", 1)) + ((("4_PLOKSTE", 5), ("5_C_ZYMA", 5)) if PLATES else ())   # rėmas RAUDONAS (Rytis 2026-10-09); v112 plokštė


# ------------------------------------------------------------------ v113: kreivės - LANKAIS, ne tūkstančiais taškų
# Rytis 2026-10-12: „labai daug nodes ant lenktų linijų, reikia kiekvieną kartą paspausti reduce nodes". Kontūras
# (stiklas, dugnas, plokštė) prieš rašymą aproksimuojamas tiesėmis + lankais (LWPOLYLINE bulge), nuokrypis <= --fit-tol
# (0,02 mm). Corel / CNC - mazgai tik atkarpų galuose (kaip po „Reduce nodes").
def _circ3(a, b, c):
    ax, ay = a; bx, by = b; cx, cy = c
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if abs(d) < 1e-12:
        return None
    a2, b2, c2 = ax * ax + ay * ay, bx * bx + by * by, cx * cx + cy * cy
    ux = (a2 * (by - cy) + b2 * (cy - ay) + c2 * (ay - by)) / d
    uy = (a2 * (cx - bx) + b2 * (ax - cx) + c2 * (bx - ax)) / d
    return ux, uy, math.hypot(ax - ux, ay - uy)


def _line_ok(P, i, j, tol):
    (x0, y0), (x1, y1) = P[i], P[j]
    L = math.hypot(x1 - x0, y1 - y0)
    if L < 1e-9:
        return all(math.hypot(P[k][0] - x0, P[k][1] - y0) <= tol for k in range(i, j + 1))
    for k in range(i + 1, j):
        if abs((x1 - x0) * (y0 - P[k][1]) - (x0 - P[k][0]) * (y1 - y0)) / L > tol:
            return False
    return True


def _arc_ok(P, i, j, tol):
    if j - i < 2:
        return None
    m = (i + j) // 2
    c = _circ3(P[i], P[m], P[j])
    if c is None or c[2] > 1e5:
        return None
    ux, uy, r = c
    a0 = math.atan2(P[i][1] - uy, P[i][0] - ux)
    prev, tot, sgn = a0, 0.0, 0
    for k in range(i + 1, j + 1):
        if abs(math.hypot(P[k][0] - ux, P[k][1] - uy) - r) > tol:
            return None
        a = math.atan2(P[k][1] - uy, P[k][0] - ux)
        da = (a - prev + math.pi) % (2 * math.pi) - math.pi
        s_ = 1 if da > 0 else -1 if da < 0 else 0
        if s_ and sgn and s_ != sgn:
            return None
        sgn = sgn or s_
        tot += da; prev = a
        # tarpinė chorda neturi nukrypti nuo lanko daugiau nei tol (retai išdėstyti taškai)
        ch = math.hypot(P[k][0] - P[k - 1][0], P[k][1] - P[k - 1][1])
        if r - math.sqrt(max(r * r - ch * ch / 4, 0)) > tol:
            return None
    if abs(tot) >= math.pi * 1.98:
        return None
    return math.tan(tot / 4)


def fit_ring(pts, tol=None):
    """uždaras žiedas -> [(x, y, bulge)]; tiesės + lankai, nuokrypis <= tol"""
    tol = A.fit_tol if tol is None else tol
    P = [tuple(q) for q in pts]
    if len(P) > 1 and math.dist(P[0], P[-1]) < 1e-9:
        P = P[:-1]
    n = len(P)
    if n < 4:
        return [(x, y, 0.0) for x, y in P]
    # pradžia - aštriausiame kampe (kad pirmas segmentas neperkirstų lanko vidurio)
    def turn(k):
        a, b, c = P[k - 1], P[k], P[(k + 1) % n]
        v1 = (b[0] - a[0], b[1] - a[1]); v2 = (c[0] - b[0], c[1] - b[1])
        l1, l2 = math.hypot(*v1), math.hypot(*v2)
        if l1 < 1e-9 or l2 < 1e-9:
            return 0
        return abs(math.atan2(v1[0] * v2[1] - v1[1] * v2[0], v1[0] * v2[0] + v1[1] * v2[1]))
    k0 = max(range(n), key=turn)
    P = P[k0:] + P[:k0] + [P[k0]]
    N = len(P) - 1
    out, i = [], 0
    while i < N:
        # ilgiausia tiesė
        lo, hi = i + 1, i + 1
        step = 1
        while hi + step <= N and _line_ok(P, i, hi + step, tol):
            hi += step; step *= 2
        step //= 2
        while step >= 1:
            if hi + step <= N and _line_ok(P, i, hi + step, tol):
                hi += step
            step //= 2
        jl = hi
        # ilgiausias lankas
        ja, ba = None, 0.0
        j = i + 2
        step = 1
        best = None
        while j <= N:
            b_ = _arc_ok(P, i, j, tol)
            if b_ is None:
                break
            best = (j, b_); j += step; step *= 2
        if best:
            lo_, hi_ = best[0], min(j, N + 1)
            while hi_ - lo_ > 1:
                md = (lo_ + hi_) // 2
                b_ = _arc_ok(P, i, md, tol)
                if b_ is not None:
                    best = (md, b_); lo_ = md
                else:
                    hi_ = md
            ja, ba = best
        if ja and ja > jl:
            out.append((P[i][0], P[i][1], ba)); i = ja
        else:
            out.append((P[i][0], P[i][1], 0.0)); i = jl
    return out


def add_ring(msp, pts, layer):
    msp.add_lwpolyline(fit_ring(pts), format="xyb", close=True, dxfattribs={"layer": layer})


def new_doc():
    doc = ezdxf.new("R2010", setup=True)
    doc.units = ezdxf.units.MM
    doc.header["$INSUNITS"] = 4
    for name, col in LAY:
        doc.layers.add(name, color=col)
    return doc


def group_layers(doc):
    """v70 (Rytis 2026-10-09): TRYS NEPRIKLAUSOMOS GRUPĖS - priekis, galas, rėmas. Plokščias modelspace Corel'yje
    importuojamas kaip VIENA grupė; todėl kiekvieno sluoksnio objektai perkeliami į savo BLOCK (PRIEKIS / GALAS / REMAS),
    įterpiamą vieną kartą (0, 0) tame pačiame sluoksnyje -> Corel / AutoCAD - 3 atskiros grupės. Papildomai DXF GROUP."""
    msp = doc.modelspace()
    for lay, _ in LAY:
        ents = [e for e in msp if e.dxf.layer == lay and e.dxftype() != "INSERT"]
        if not ents:
            continue
        bname = lay.split("_", 1)[1]
        blk = doc.blocks.new(name=bname)
        for e in ents:
            blk.add_entity(e.copy())
            msp.delete_entity(e)
        ref = msp.add_blockref(bname, (0, 0), dxfattribs={"layer": lay})
        doc.groups.new(bname).extend([ref])


def rings_of(geom):
    for p in getattr(geom, "geoms", [geom]):
        if p.is_empty or not hasattr(p, "exterior"):
            continue
        yield list(p.exterior.coords)[:-1]
        for h in p.interiors:
            yield list(h.coords)[:-1]


def put(msp, o, rails_, ox, oy, clip=None, var=None):
    """o - raidė, (ox, oy) - nulis (mm, y žemyn), išvestis y aukštyn"""
    T = lambda q: (q[0] - ox, oy - q[1])
    for ring in o["rings"]:                                     # 1 stiklas - originalus kontūras
        add_ring(msp, [T(q) for q in ring], "1_PRIEKIS")
    for ring in rings_of(o["back"]):                            # 2 dugnas
        add_ring(msp, [T(q) for q in ring], "2_GALAS")
    for (x, y) in (o.get("holes_var", {}).get(var) if var else None) or o["holes"]:
        msp.add_circle(T((x, y)), A.hole_d / 2, dxfattribs={"layer": "2_GALAS"})
    for (x, y) in o.get("drain", []):                           # v98/v99: drenažo skylutė Ø8 dugne (exterior)
        msp.add_circle(T((x, y)), A.drain_d / 2, dxfattribs={"layer": "2_GALAS"})
    if var and o.get("d11", {}).get(var):                       # D11 laido išvestis (dugne, ant bėgelio ašies)
        msp.add_circle(T(o["d11"][var]), A.d11 / 2, dxfattribs={"layer": "2_GALAS"})
    for r_ in rails_:                                           # 3 rėmas
        x0, x1 = r_["x0"], r_["x1"]
        if clip:
            x0, x1 = max(x0, clip[0]), min(x1, clip[1])
            if x1 <= x0:
                continue
        pts = [(x0, r_["y0"]), (x1, r_["y0"]), (x1, r_["y1"]), (x0, r_["y1"])]
        msp.add_lwpolyline([T(q) for q in pts], close=True, dxfattribs={"layer": "3_REMAS"})


files, mains = [], []
VARS = [(v, {"top": "_laidas_virsus", "bottom": "_laidas_apacia", "line": "_laidas_linija"}[v]) for v in CABLE_VARIANTS] or [(None, "")]
for var, suf in VARS:
    doc = new_doc(); msp = doc.modelspace()
    for o in letters:
        put(msp, o, [], GX0, GY1, var=var)
    put_plates(msp, var)                                      # v112
    for r_ in ([] if SEPARATE else rails + VRAILS):          # v90: atskiros raidės - rėmo nėra
        pts = r_.get("poly") or [(r_["x0"], r_["y0"]), (r_["x1"], r_["y0"]), (r_["x1"], r_["y1"]), (r_["x0"], r_["y1"])]
        msp.add_lwpolyline([(q[0] - GX0, GY1 - q[1]) for q in pts], close=True, dxfattribs={"layer": "3_REMAS"})
    for e_ in ([] if SEPARATE else EARS_J):                  # v101: ausėlės su skyle - rėmo dalis
        pts = [(e_["x0"], e_["y0"]), (e_["x1"], e_["y0"]), (e_["x1"], e_["y1"]), (e_["x0"], e_["y1"])]
        msp.add_lwpolyline([(q[0] - GX0, GY1 - q[1]) for q in pts], close=True, dxfattribs={"layer": "3_REMAS"})
        msp.add_circle((e_["hx"] - GX0, GY1 - e_["hy"]), e_["d"] / 2, dxfattribs={"layer": "3_REMAS"})
    for b_ in ([] if SEPARATE else BRK_J):                   # v101: U laikikliai (vaizdas nuo fasado) + skylės
        pts = [(b_["x0"], b_["y0"]), (b_["x1"], b_["y0"]), (b_["x1"], b_["y1"]), (b_["x0"], b_["y1"])]
        msp.add_lwpolyline([(q[0] - GX0, GY1 - q[1]) for q in pts], close=True, dxfattribs={"layer": "3_REMAS"})
        for hx_, hy_, hd_ in b_["holes"]:
            msp.add_circle((hx_ - GX0, GY1 - hy_), hd_ / 2, dxfattribs={"layer": "3_REMAS"})
    main = os.path.join(A.out_dir, f"{prefix}_P6_1-1{suf}.dxf")
    group_layers(doc)
    doc.saveas(main); files.append(main); mains.append((var, suf, main))
    if not A.no_letters:
        for o in letters:
            d2 = new_doc(); m2 = d2.modelspace()
            put(m2, o, [] if SEPARATE else rails, o["bb"][0], o["bb"][3], clip=(o["bb"][0] - 30, o["bb"][2] + 30), var=var)
            f = os.path.join(A.out_dir, f"{prefix}_{o['id']}{suf}.dxf")
            group_layers(d2)
            d2.saveas(f); files.append(f)

# ------------------------------------------------------------------ patikra PNG (iš DXF)
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from ezdxf.addons.drawing import RenderContext, Frontend
    from ezdxf.addons.drawing.config import Configuration, BackgroundPolicy, ColorPolicy
    from ezdxf.addons.drawing.matplotlib import MatplotlibBackend

    from matplotlib.patches import Circle

    def render(path, png, w_in, h_in, zones=(), ox=0.0, oy=0.0):
        """DXF -> PNG; zones - skylių centrai (mm, y žemyn), piešiamos prispaudimo zonos R (tik patikrai, ne DXF)"""
        doc_ = ezdxf.readfile(path)
        fig = plt.figure(figsize=(w_in, h_in), dpi=120)
        ax = fig.add_axes([0, 0, 1, 1])
        ctx = RenderContext(doc_); ctx.set_current_layout(doc_.modelspace())
        cfg = Configuration(background_policy=BackgroundPolicy.WHITE, color_policy=ColorPolicy.COLOR)
        Frontend(ctx, MatplotlibBackend(ax), config=cfg).draw_layout(doc_.modelspace(), finalize=True)
        for (x, y) in zones:
            ax.add_patch(Circle((x - ox, oy - y), A.press_r, facecolor=(1, 0.6, 0, 0.18), edgecolor=(0.9, 0.4, 0, 0.5), lw=0.4))
            ax.add_patch(Circle((x - ox, oy - y), 3, facecolor="red", edgecolor="none"))
        fig.savefig(png, facecolor="white"); plt.close(fig)
        return png
    for var, suf, main in mains:
        zones_all = [h for o in letters for h in ((o.get("holes_var", {}).get(var) if var else None) or o["holes"])]
        files.append(render(main, os.path.join(A.out_dir, f"{prefix}_patikra{suf}.png"), max(8, PW / 100),
                            max(3, PH / 100 + 1), zones_all, GX0, GY1))
    if not A.no_letters and letters:                 # viena raidė stambiai (skylėms matyti)
        var, suf, _ = mains[0]
        o = max(letters, key=lambda o_: len(o_["holes"]))
        f = os.path.join(A.out_dir, f"{prefix}_{o['id']}{suf}.dxf")
        bw, bh = o["bb"][2] - o["bb"][0] + 60, o["bb"][3] - o["bb"][1]
        files.append(render(f, os.path.join(A.out_dir, f"{prefix}_patikra_{o['id']}{suf}.png"), 6 * bw / bh + 0.5, 6,
                            o["holes"], o["bb"][0], o["bb"][3]))
except Exception as e:                       # noqa: BLE001
    print("  patikros PNG nepavyko:", e)

# ------------------------------------------------------------------ ataskaita
print(f"OK P6 DXF: {prefix}, {len(letters)} raidės, {PW:.0f} x {PH:.0f} mm, mastelis {S * 72 / 25.4:.4f}:1 pt, "
      f"stiklas = kontūras, dugnas -{A.inset:g} mm, Ø{A.hole_d:g} skylės, bėgelis {A.rail:g}, prispaudimo R {A.press_r:g}")
for r_ in rails:
    print(f"  bėgelis: ašis y {PH - r_['cy']:.1f} (nuo apačios) / {r_['cy']:.1f} (nuo viršaus), "
          f"x {r_['x0'] - GX0:.1f} .. {r_['x1'] - GX0:.1f}, L {r_['x1'] - r_['x0']:.0f}")
tot_b = sum(o["back"].area for o in letters); tot_p = sum(o["back"].area * o["pressed"] for o in letters)
for o in letters:
    hs = ", ".join(f"({x - GX0:.0f}; {PH - y:.0f})" for x, y in o["holes"])
    same = f" (= {o['same_as']})" if o.get("same_as") else ""
    d11 = "; ".join(f"D11 {v}: ({pt[0] - GX0:.0f}; {PH - pt[1]:.0f})" if pt else f"D11 {v}: -" for v, pt in o.get("d11", {}).items())
    print(f"  {o['id']}: {len(o['holes'])} skylės{same}, prispausta {o['pressed'] * 100:.0f} % dugno  {hs}  {d11}")
print(f"  viso skylių {sum(len(o['holes']) for o in letters)}, prispausta {tot_p / max(tot_b, 1) * 100:.0f} % dugno ploto")
for w_ in warn:
    print("  !", w_)
print("  failai:", ", ".join(os.path.basename(f) for f in files))
