#!/usr/bin/env python3
"""Produkto modulis: P6 raidės ant U bėgelių + (nebūtina) P6+3 raidės ant Alu plokštės su distanceriais.
Stilius - lapas_core (references/stilius.md).

Naudojimas:  python3 braizyti_begeliai.py spec.json isvestis.pdf
Žr. assets/spec_begeliai_extra.json.
"""
import re
import json, math, os, sys, tempfile
from functools import reduce

import pymupdf as fitz
from reportlab.lib.colors import HexColor, white, black
from shapely.geometry import Polygon, Point, box as sbox
from shapely.ops import unary_union

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lapas_core as K
import auseles as AUS
import p6_vaizdas as PV
import medziagos as MEDZ                     # v73: tiekėjų formatai, 6 m strypų taisyklė
from lapas_core import MM, T, line, rect, poly, hdim, hchain, vchain, leader, tag, view_title, hatch

spec = json.load(open(sys.argv[1]))
OUT = sys.argv[2]
depth = spec["depth_mm"]
# priekis: "5S+foil" (buv. P6_3mm+foil: polikarbonatas 3 FR + plėvelė, PVC bortelis), "5S color" (spalvotas 3, PVC), "8mm+foil" (balta 8, frezuota briauna)
import p6_front as P6F   # v90: visi priekio variantai (3/8/10/15/20/30 mm, +foil, color)
FRONT = P6F.kind(spec.get("front", "5S"))
# v276: PVC bortelio (A) / varžto (B) eilutės - jei BENT VIENA grupė 5S (mišrūs priekiai vienoje iškaboje)
_NO3 = all(P6F.kind(sg.get("front") or spec.get("front", "5S")) == "8mm" for sg in spec.get("groups", [{}])) if spec.get("groups") else FRONT == "8mm"
_PNAME = "5S" if FRONT == "3mm" else ("P10" if FRONT == "P10" else "P6")   # v210: P6_3mm -> 5S; v242: P10 blokas   # "3mm" (PVC) / "8mm" (frezuota, >= 8 mm) / "P1"
if P6F.parse(spec.get("front", "5S"))["warn"]:
    print(P6F.parse(spec.get("front", "5S"))["warn"])
RAIL = {"size": "30x30x2", "depth": 30, "ral": "7035"}; RAIL.update(spec.get("rail", {}))
# v183: rėmo RAL nežinomas („?") - FINISH langelis tuščias (ne „RAL ? matt")
def _ral_txt(v):                                          # v281: NCS / PMS / kitas kodas - be „RAL" priešdėlio
    v = str(v).strip()
    return v if re.match(r"(NCS|PMS|RAL|3M|ORACAL|AVERY)\b", v, re.I) else f"RAL {v}"


RAIL_FIN = "" if str(RAIL.get("ral", "")).strip() in ("", "?") else (_ral_txt(RAIL['ral']) + (" matt" if _ral_txt(RAIL['ral']).startswith("RAL") else ""))


def _rail_pos():
    """v184: galutinė bėgelio (rėmo) BOM pozicija - brackets / none režime pozicijos pernumeruojamos (buvo fiksuota 5)"""
    rows_ = [r_ for r_ in spec.get("bom", []) if not (_NO3 and str(r_[0]).upper() in ("A", "B"))]
    if MOUNTING in ("none", "brackets"):
        drop_ = r"\bear\b|ears\b|mounting ear|ausėl"
        rows_ = [r_ for r_ in rows_ if re.match(r"\s*rail", str(r_[1]), re.I) or re.search(r"bracket|hanger", str(r_[1]), re.I)
                 or not re.search(drop_, str(r_[1]), re.I)]
        n_, out_ = 0, []
        for r_ in rows_:
            if str(r_[0]).strip().isdigit():
                n_ += 1; out_.append([str(n_)] + list(r_[1:]))
            else:
                out_.append(list(r_))
        rows_ = out_
    return next((str(r_[0]) for r_ in rows_ if re.search(r"\brail|wallframe|\bframe\b|bėgel", str(r_[1]), re.I)
                 and not re.search(r"ear|hanger|bracket|plate|tube|\bZ\b", str(r_[1]), re.I)), "5")


RAIL_POS = None
PLATE = {"thk": 3, "gap_mm": 30, "recess_mm": 25, "ral": "1023"}; PLATE.update(spec.get("plate", {}))
# v47 (Rytis 2026-10-09): profilio forma VISUOSE vaizduose pagal tipą - U visur U, stačiakampis visur stačiakampis
RAIL_SQ = str(RAIL.get("type", "u")).lower().startswith(("sq", "box", "kv"))
# v229 (Rytis 2026-10-14, Leapmotor): AKRILINIS rėmas - "rail": {"type": "acrylic", "size": "40x20"} (plotis x storis),
#  skaidrus orgstiklas 20 mm, CNC pjaunamas iš lakšto: puzzle jungtys (0,2), laidų grioveliai, Ø8 skylės tarp raidžių,
#  statmuo po KIEKVIENA raide; ausėlių / 6 m strypų nėra (lakštas spec "acrylic": {"sheet": [3050, 2050]})
RAIL_ACR = str(RAIL.get("type", "")).lower().startswith("acr")
ACRY = {"thk": 20, "sheet": [3050, 2050], "joint_clear": 0.2, "hole_d": 8, "holes_every_gap": 2, "groove": None, "v_edge": 3,
        "v_pitch": 1000, "single_w": 55, "stud": {"d": 5, "cb_d": 12, "cb_depth": 15, "edge": 8, "two_if": 400}, "cable_slot": None}
# v241 (Rytis 2026-10-15, etalonas P10 Boots): raidės prisukamos per ATSKIRAS ĮLEISTAS SKYLES bėgelyje (iš priekio Ø5, iš galo
#  Ø12 x 15 - veržlė nesitrukdo), smeigės privirintos raidės nugaroje; laidų griovelis nugaroje PASLINKTAS nuo ašies (šalia skylių
#  eilės), prie kiekvienos raidės ovali skylė kiaurai laidui
# v231 (Rytis 2026-10-14: „per daug statmenų"): statmenys NE po kiekviena raide, o žingsniu v_pitch (1000 mm) per stiebus;
#  griovelis "groove": {"w": 8, "d": 10} (nugaroje); jungtys pagal lakšto ilgį - vaizduose brūkšn. taškinė linija + dalių grandinė
ACRY.update(spec.get("acrylic", {}))
if P6F.kind(spec.get("front", "5S")) == "P10":            # v244: P10 - smeigė ant įleisto Alu dugnelio (kraštas rim) -> nuo raidės krašto >= rim + 1
    ACRY["stud"] = dict(ACRY["stud"], edge=max(float(ACRY["stud"].get("edge", 8)), float((spec.get("p10") or {}).get("rim", 5)) + 1))
RAIL_W = float(str(RAIL["size"]).lower().split("x")[0]) if RAIL_ACR else None


def _acr_studs(letters, hs_, ST, g_off, gw, cuts=(), holes=(), vjoints=(), grid=None, vlines=()):
    """v245 (Rytis 2026-10-15): smeigės pagal RAIDĖS FORMĄ - kvadratas 4, trikampis 3 ... (supaprastinto gaubto kampų sk.,
    2..6, ilgoms + kas 500); taškai ARTI RAIDĖS CENTERLINE (štricho, kertančio bėgelio liniją, vidurys), ne prie krašto;
    ant vieno bėgelio - VIENA HORIZONTALI LINIJA (y parenkamas bendras visoms raidėms, ne griovelio zonoje).
    Grąžina (studs [(x, y, id)], nepavykę [x])."""
    from shapely.geometry import Point as _P, LineString as _L
    cbr = ST["cb_d"] / 2
    rr_ = ST["edge"] + ST["d"] / 2
    ins = [o["geom"].buffer(-rr_) for o in letters]

    def _near_knob(x, y, v_):
        """v246: tikslus statmens puzzle galvutės užimtas plotas (galvutė + kaklelis) + įleidimo spindulys + 2"""
        ex, ey, sg = v_[0], v_[1], v_[2]
        wv = v_[3] if len(v_) > 3 else 40
        hr = 0.2 * wv
        kx, ky = ex, ey + sg * hr * 1.6
        if (x - kx) ** 2 + (y - ky) ** 2 < (hr + cbr + 2) ** 2:
            return True
        return abs(x - ex) < 0.12 * wv + cbr + 2 and min(ey, ky) - cbr - 2 < y < max(ey, ky) + cbr + 2

    def cands_on(y, r_):
        """raidžių kandidatai linijoje y: kiekvieno kertančio štricho vidurys (ilgame - kas ~150)"""
        out_ = {}
        for o, inn in zip(letters, ins):
            if inn.is_empty or not (o["bb"][1] < y < o["bb"][3]):
                continue
            ix = inn.intersection(_L([(max(o["bb"][0], r_["x0"] + 15) - 1, y), (min(o["bb"][2], r_["x1"] - 15) + 1, y)]))
            pts = []
            for q in getattr(ix, "geoms", [ix]):
                if q.is_empty or not hasattr(q, "coords"):
                    continue
                a_, b_ = sorted((q.coords[0][0], q.coords[-1][0]))
                if b_ - a_ < max(40, 2.2 * rr_ + 30):             # kertamas štrichas - jo vidurys (centerline)
                    pts.append((a_ + b_) / 2)
                else:                                             # v246: išilginis štrichas - GALUOSE (ten stiebai / kampai,
                    n_ = int((b_ - a_) // 400)                    #  P kaip R), ilgame + kas ~400
                    pts += [a_ + 3, b_ - 3] + [a_ + (b_ - a_) * k / (n_ + 1) for k in range(1, n_ + 1)]
            pts = [x for x in pts if all(abs(x - c_["x"]) > 30 for c_ in cuts)
                   and all((x - h_[0]) ** 2 + (y - h_[1]) ** 2 > 15 ** 2 for h_ in holes)
                   and all(not _near_knob(x, y, v_) for v_ in vjoints)]
            if pts:
                out_[id(o)] = [(x, y) for x in pts]
        return out_

    # kiekvienam bėgeliui - viena linija y (leistina juosta be griovelio zonos), daugiausiai raidžių su >= 2 taškais
    per = {id(o): [] for o in letters}
    for r_ in hs_:
        ax = (r_["y0"] + r_["y1"]) / 2
        gy = ax - g_off
        ys = [y_ / 2 for y_ in range(int(2 * (r_["y0"] + cbr + 2)), int(2 * (r_["y1"] - cbr - 2)) + 1)
              if not (gy - gw / 2 - cbr - 1 < y_ / 2 < gy + gw / 2 + cbr + 1)]
        best = None
        for y in ys:
            c_ = cands_on(y, r_)
            sc = (sum(1 for v in c_.values() if len(v) >= 2), sum(len(v) for v in c_.values()), -abs(y - ax))
            if best is None or sc > best[0]:
                best = (sc, c_)
        if best:
            for k_, v in best[1].items():
                per[k_] += v
    # raidė, kuriai bendroje linijoje < 2 taškų (pvz. L - tik stiebas) - papildoma linija TIK jai (artimiausia bendrai)
    for o in letters:
        if len(per[id(o)]) >= 2:
            continue
        y0_ = per[id(o)][0][1] if per[id(o)] else None
        best = None
        for r_ in hs_:
            ax = (r_["y0"] + r_["y1"]) / 2
            gy = ax - g_off
            for y2 in range(int(2 * (r_["y0"] + cbr + 2)), int(2 * (r_["y1"] - cbr - 2)) + 1):
                y = y2 / 2
                if gy - gw / 2 - cbr - 1 < y < gy + gw / 2 + cbr + 1:
                    continue
                c_ = [q for q in cands_on(y, r_).get(id(o), []) if all(abs(q[0] - p_[0]) > 20 or abs(q[1] - p_[1]) > 20
                                                                    for p_ in per[id(o)])]
                # v249: antra linija - kuo TOLIAU nuo jau esančių taškų (siaura raidė l / i - stiebo kitame gale)
                sc = (min(len(c_), 2 - len(per[id(o)])), abs(y - y0_) if y0_ is not None else -abs(y - ax))
                if c_ and (best is None or sc > best[0]):
                    best = (sc, c_)
        if best:
            per[id(o)] += best[1]
    # v246: smeigės ir STATMENYSE (pvz. L stiebas, kurį užima statmuo) - x = ašis + vs_off (griovelis statmenyje - ašis - g_off)
    for vx, vy0, vy1 in vlines:
        sx = vx + ST.get("vs_off", 5)
        for o, inn in zip(letters, ins):
            if inn.is_empty or not (o["bb"][0] < sx < o["bb"][2]):
                continue
            ix = inn.intersection(_L([(sx, vy0 + 26), (sx, vy1 - 26)]))
            for q in getattr(ix, "geoms", [ix]):
                if q.is_empty or not hasattr(q, "coords"):
                    continue
                a_, b_ = sorted((q.coords[0][1], q.coords[-1][1]))
                c_ = (a_ + b_) / 2
                if all((sx - p_[0]) ** 2 + (c_ - p_[1]) ** 2 > 30 ** 2 for p_ in per[id(o)]):
                    per[id(o)].append((sx, c_))
    out, fail = [], []
    for o in letters:
        pts = per[id(o)]
        if len(pts) < 2:
            fail.append(round(o["bb"][0]))
            out += [(x, y, id(o)) for x, y in pts]
            continue
        hull = o["geom"].convex_hull.simplify(0.12 * max(o["bb"][2] - o["bb"][0], o["bb"][3] - o["bb"][1]))
        nh = len(hull.exterior.coords) - 1 if hasattr(hull, "exterior") else 2
        n_t = max(min(max(nh, 2), 6), 2 + int((o["bb"][2] - o["bb"][0]) // 500))
        if max(o["bb"][2] - o["bb"][0], o["bb"][3] - o["bb"][1]) < 200:   # v246: maža raidė (M ~170) - užtenka 3
            n_t = min(n_t, 3)
        cx, cy = o["geom"].centroid.x, o["geom"].centroid.y
        sel = [max(pts, key=lambda q: (q[0] - cx) ** 2 + (q[1] - cy) ** 2)]   # toliausiai nuo centro, toliau - FPS
        while len(sel) < min(n_t, len(pts)):
            q_ = max(pts, key=lambda q: min((q[0] - s_[0]) ** 2 + (q[1] - s_[1]) ** 2 for s_ in sel))
            if min((q_[0] - s_[0]) ** 2 + (q_[1] - s_[1]) ** 2 for s_ in sel) < max(20, 0.25 * min(o["bb"][2] - o["bb"][0], o["bb"][3] - o["bb"][1])) ** 2:
                break
            sel.append(q_)
        out += [(x, y, id(o)) for x, y in sel]
    return out, fail




def _rail_t(sz):
    try:
        return float(str(sz["size"]).lower().split("x")[-1])
    except Exception:
        return 2.0
PRAIL = PLATE.get("rail")     # plokštės (6+3) bėgelis, pvz. {"size": "40x40x2", "depth": 40}
PZ0 = PRAIL["depth"] if PRAIL else 0
# EXTRA apskritimo Z kabinimo rėmas (Rytis 2026-10-07): ant plokštės nugaros 2 horizontalios Z juostos,
# sieninis rėmas - 2 Z (kabliai aukštyn) + 2 vertikalūs kvadratiniai vamzdeliai už Z juostų galų
ZF = PLATE.get("zframe")
if ZF:
    ZF = dict({"z": "30x30x30x2", "tube": "20x20x2", "inset": 0.22, "edge_mm": 10, "gap_mm": 20, "circle_margin": 10}, **ZF)
    _zp = [float(v) for v in ZF["z"].lower().split("x")]       # flanšas x sienelė x flanšas x storis (arba a x b x t)
    ZF["zf"], ZF["zw"], ZF["zt"] = (_zp[0], _zp[1], _zp[3]) if len(_zp) == 4 else (_zp[0], _zp[1], _zp[2])
    ZF["tb"], _, ZF["tt"] = (float(v) for v in ZF["tube"].lower().split("x"))
    PZ0 = ZF["zw"]                    # plokštės nugara nuo sienos = Z sienelės gylis
# v114 (Rytis 2026-10-12): profiliai tikrinami pagal LT tiekėjų katalogą (assets/medziagos.json -> profiliu_katalogas):
#  nėra sandėlyje -> perspėjimas su artimiausiais variantais; lape / BOM tokio profilio nerašyti be Ryčio patvirtinimo
for _pt, _pk in (([] if RAIL_ACR else [(RAIL["size"], "O" if RAIL_SQ else "U")]) + ([(PRAIL["size"], "U")] if PRAIL and PRAIL.get("size") else [])
                 + ([(ZF["z"], "Z"), (ZF["tube"], "O")] if ZF else [])):
    _w = MEDZ.profile_warn(_pt, _pk)
    if _w:
        print(_w)

# v44 (Rytis 2026-10-09, EXTRA 225978 „one frame"): VIENTISAS RĖMAS - plokštės grupės (X apskritimas) neturi savo
# kabinimo; rails grupės (EXTRA) horizontalūs bėgeliai tęsiami už plokštės iki 10 mm nuo jos krašto, plokštė
# prisukama prie bėgelių priekio (nugara = bėgelio gylis). spec: "one_frame": {"plate": "X", "rails": "EXTRA"}
OF = spec.get("one_frame")
if OF:
    ZF = None
    PZ0 = RAIL["depth"]

# ============================================================ kliento geometrija
page = fitz.open(spec["client_pdf"])[spec.get("page", 0)]
S = spec["scale"] * 25.4 / 72
cx0, cy0, cx1, cy1 = spec["crop_pt"]


def true_rect(d):
    pts = [q for it in d["items"] for q in it[1:] if hasattr(q, "x")]
    for it in d["items"]:
        if it[0] == "re":
            pts += [it[1].tl, it[1].br]
        if it[0] == "qu":
            pts += [it[1].ul, it[1].lr]
    return fitz.Rect(min(q.x for q in pts), min(q.y for q in pts), max(q.x for q in pts), max(q.y for q in pts))


raw = []
SRAILS = []          # bėgeliai kaip storos pilkos linijos (stroke) kliento faile
for d in page.get_drawings():
    col_ = d.get("color")
    if d.get("fill") is None and col_ and (d.get("width") or 0) * S >= 15:
        rr, gg, bb = col_[:3]
        its_ = [it for it in d["items"] if it[0] == "l"]
        if abs(rr - gg) < 0.06 and abs(gg - bb) < 0.06 and 0.3 < rr < 0.85 and len(its_) == 1:
            a_, b_ = its_[0][1], its_[0][2]; w2 = d["width"] / 2
            if cx0 <= min(a_.x, b_.x) and max(a_.x, b_.x) <= cx1 and cy0 <= min(a_.y, b_.y) and max(a_.y, b_.y) <= cy1:
                vert_ = abs(a_.x - b_.x) < abs(a_.y - b_.y)
                SRAILS.append(fitz.Rect(min(a_.x, b_.x) - (w2 if vert_ else 0), min(a_.y, b_.y) - (0 if vert_ else w2),
                                        max(a_.x, b_.x) + (w2 if vert_ else 0), max(a_.y, b_.y) + (0 if vert_ else w2)))
    if d.get("fill") is None and spec.get("rail_strokes") and len(d["items"]) == 1 and d["items"][0][0] == "re":
        # v56 (SPAR 226004): kliento bėgeliai - neužpildyti stačiakampiai (tik kontūras)
        r0 = d["items"][0][1]
        if cx0 <= r0.x0 and r0.x1 <= cx1 and cy0 <= r0.y0 and r0.y1 <= cy1 and \
                max(r0.width, r0.height) / max(min(r0.width, r0.height), 0.1) > 6 and max(r0.width, r0.height) * S > 150:
            SRAILS.append(fitz.Rect(r0))
        continue
    if d.get("fill") is None:
        continue
    r = true_rect(d)
    if any(max(abs(a - b) for a, b in zip(d["fill"][:3], f_)) < 0.05 for f_ in spec.get("ignore_fills", [])):
        continue
    if r.x0 < cx0 or r.y0 < cy0 or r.x1 > cx1 or r.y1 > cy1 or max(r.width, r.height) * S < 30:
        continue
    raw.append((d, r))
OX = min(r.x0 for _, r in raw); OY = min(r.y0 for _, r in raw)
SRAILS_U = []
for r in SRAILS:                                  # tos pačios linijos dublikatai (kelios pilkos spalvos)
    if not any(abs(r.x0 - q.x0) < 2 and abs(r.x1 - q.x1) < 2 and abs(r.y0 - q.y0) < 2 for q in SRAILS_U):
        SRAILS_U.append(r)


CABLES_RAW = spec.get("cable_exits", [])
# v11: lipdukai / iškirpti piešiniai ant grupės priekio (pvz. balta piktograma ant PANT apskritimo) - kliento spalva,
# pašalinama iš geometrijos per ignore_fills ir piešiama priekyje bei 3D ant grupės priekio
DECALS_RAW = []
for _dc in spec.get("decals", []):
    for d in page.get_drawings():
        if d.get("fill") is not None and max(abs(a - b) for a, b in zip(d["fill"][:3], _dc["client_fill"])) < 0.05:
            r_ = d["rect"]
            if cx0 <= r_.x0 and r_.x1 <= cx1 and cy0 <= r_.y0 and r_.y1 <= cy1:
                DECALS_RAW.append((d, _dc))


def tomm(p):
    return ((p[0] - OX) * S, (p[1] - OY) * S)


def parse_client():
    global rails, shapes
    rails, shapes = [], []
    for r in SRAILS_U:
        rails.append({"x0": (r.x0 - OX) * S, "y0": (r.y0 - OY) * S, "x1": (r.x1 - OX) * S, "y1": (r.y1 - OY) * S})
    for d, r in raw:
        rr, gg, bb = d["fill"][:3]
        grey = abs(rr - gg) < 0.06 and abs(gg - bb) < 0.06 and 0.3 < rr < 0.85
        # v49: kliento bėgelių spalva už pilkos ribų (pvz. Joker - šviesiai pilki 0.9) - spec "rail_fills"
        grey = grey or any(max(abs(a - b) for a, b in zip((rr, gg, bb), f_)) < 0.03 for f_ in spec.get("rail_fills", []))
        if grey and max(r.width, r.height) / max(min(r.width, r.height), 0.1) > 6:
            if spec.get("client_vert_rails") is False and r.height > r.width:
                continue                 # v109: statmenys iš spec "verticals" (patvirtinto lapo statmenys - nedubliuoti)
            rails.append({"x0": (r.x0 - OX) * S, "y0": (r.y0 - OY) * S, "x1": (r.x1 - OX) * S, "y1": (r.y1 - OY) * S})
            continue
        # v109 (EXTRA 225978 patvirtinimas): rail_fills spalvos blokas (statmens / kojos „stem" plotas mūsų lape) - NE raidė
        if any(max(abs(a - b) for a, b in zip((rr, gg, bb), f_)) < 0.03 for f_ in spec.get("rail_fills", [])):
            continue
        for L_ in K.split_letters(K.drawing_to_subpaths(d, tomm)):
            L_["fill"] = tuple(d["fill"][:3]); L_["geom"] = K.shape_geom(L_["sub"])
            shapes.append(L_)


parse_client()


def _dedupe():
    """kliento failuose tas pats kontūras dažnai dubliuojamas (užpildas + apvadas + kopija) - paliekamas vienas"""
    global shapes
    out = []
    for s_ in shapes:
        b_ = s_["geom"].bounds
        if any(max(abs(a - c) for a, c in zip(b_, o["geom"].bounds)) < 1.0 and abs(s_["geom"].area - o["geom"].area)
               < 0.002 * max(o["geom"].area, 1) for o in out):
            continue
        out.append(s_)
    if len(out) < len(shapes):
        print(f"  dublikatai pašalinti: {len(shapes) - len(out)}")
    shapes = out


_dedupe()
# Bezier valdymo taškai išsikiša už kontūro -> nulis ties TIKRA geometrija (kitaip gabaritai per dideli)
for s_ in shapes:
    b_ = s_["geom"].bounds
    s_["bb"] = (b_[0], b_[1], b_[2], b_[3])
# v49 (Joker 2026-10-09): nulis ir gabaritai - pagal RAIDES (kliento bėgelio grafika gali išsikišti 1-2 mm už raidžių,
# bėgeliai vis tiek apkerpami 10 mm raidės viduje); senas elgesys - spec "origin_with_rails": true
_RW = bool(spec.get("origin_with_rails"))
_gx0 = min([s_["bb"][0] for s_ in shapes] + ([r_["x0"] for r_ in rails] if _RW else []))
_gy0 = min([s_["bb"][1] for s_ in shapes] + ([r_["y0"] for r_ in rails] if _RW else []))
if abs(_gx0) > 0.3 or abs(_gy0) > 0.3:
    OX += _gx0 / S; OY += _gy0 / S
    parse_client()
    _dedupe()
    for s_ in shapes:
        b_ = s_["geom"].bounds
        s_["bb"] = (b_[0], b_[1], b_[2], b_[3])
PW = max([s_["bb"][2] for s_ in shapes] + ([r_["x1"] for r_ in rails] if _RW else []))
PH = max([s_["bb"][3] for s_ in shapes] + ([r_["y1"] for r_ in rails] if _RW else []))

# plokštės: forma, kurios viduje yra kitų formų
plates = []
for s_ in shapes:
    inside = [o for o in shapes if o is not s_ and s_["geom"].area > o["geom"].area * 1.5
              and s_["geom"].buffer(1).contains(o["geom"].representative_point())]
    if inside:
        plates.append((s_, inside))
if spec.get("no_plates"):          # v11: forma su raidėmis ant jos NĖRA 6+3 plokštė (pvz. P00 apskritimas už raidžių)
    plates = []
plate_ids = {id(p) for p, _ in plates}
on_plate = {id(o) for _, ins in plates for o in ins}

# grupės: plokštė + jos raidės; likusios - pagal spalvą ir eilutes
groups = []
for p, ins in plates:
    for o in ins:   # raidė apkerpama plokštės kontūru (kaip kliento faile)
        g_ = o["geom"].intersection(p["geom"]).buffer(0)
        if g_.area < o["geom"].area - 1:
            o["geom"] = g_
            o["clipped"] = True
            xs_, ys_ = g_.bounds[0::2], g_.bounds[1::2]
            o["bb"] = (g_.bounds[0], g_.bounds[1], g_.bounds[2], g_.bounds[3])
            o["sub"] = [[("M", q)] + [("L", q2) for q2 in list(ring.coords)[1:]]
                        for gg in getattr(g_, "geoms", [g_]) for ring in [gg.exterior] + list(gg.interiors)
                        for q in [list(ring.coords)[0]]]
    groups.append({"plate": p, "letters": ins, "on_plate": True})
rest = [s_ for s_ in shapes if id(s_) not in plate_ids and id(s_) not in on_plate]
rest.sort(key=lambda s_: (s_["bb"][1], s_["bb"][0]))
for s_ in rest:
    host = None
    for g in groups:
        if g["on_plate"]:
            continue
        gy0 = min(o["bb"][1] for o in g["letters"]); gy1 = max(o["bb"][3] for o in g["letters"])
        same_col = max(abs(a - b) for a, b in zip(g["letters"][0]["fill"], s_["fill"])) < 0.1
        if same_col and s_["bb"][1] < gy1 - 1 and s_["bb"][3] > gy0 + 1:
            host = g; break
    if host:
        host["letters"].append(s_)
    else:
        groups.append({"plate": None, "letters": [s_], "on_plate": False})
# atskiri smulkūs elementai (i / j taškai, akcentai) - prie tos pačios spalvos grupės po / virš jų
def _gbb(g):
    return (min(o["bb"][0] for o in g["letters"]), min(o["bb"][1] for o in g["letters"]),
            max(o["bb"][2] for o in g["letters"]), max(o["bb"][3] for o in g["letters"]))
for g in list(groups):
    if g["on_plate"] or len(g["letters"]) > 2:
        continue
    a = _gbb(g)
    for h in groups:
        if h is g or h["on_plate"] or len(h["letters"]) <= len(g["letters"]):
            continue
        b = _gbb(h)
        same_col = max(abs(x - y) for x, y in zip(h["letters"][0]["fill"], g["letters"][0]["fill"])) < 0.1
        gap = max(b[1] - a[3], a[1] - b[3])
        if same_col and a[0] >= b[0] - 1 and a[2] <= b[2] + 1 and gap < 0.6 * (b[3] - b[1]) \
                and (a[3] - a[1]) < 0.6 * (b[3] - b[1]):
            h["letters"] += g["letters"]; groups.remove(g); break
# v74 (Rytis 2026-10-10, „Bandymas / antras"): kelios tos pačios spalvos EILUTĖS ant VIENO rėmo - `"merge_rows": true`:
#  eilutės sujungiamos į vieną grupę (4+ horizontalūs bėgeliai, jungiamieji statmenys tarp eilučių - iš kliento failo),
#  statmenys po raidėmis - kiekvienos eilutės bėgelių porai, ausėlės - tik kraštiniuose (viršutiniame / apatiniame) bėgeliuose,
#  viena laido išvestis, viena BOM eilutė.
if spec.get("merge_rows"):
    _mg = {}
    for g in list(groups):
        if g["on_plate"]:
            continue
        key = tuple(round(c, 1) for c in g["letters"][0]["fill"])
        if key in _mg:
            _mg[key]["letters"] += g["letters"]; groups.remove(g)
        else:
            _mg[key] = g
for g in groups:
    els = g["letters"] + ([g["plate"]] if g["plate"] else [])
    g["x0"] = min(o["bb"][0] for o in els); g["x1"] = max(o["bb"][2] for o in els)
    g["y0"] = min(o["bb"][1] for o in els); g["y1"] = max(o["bb"][3] for o in els)
    g["lx0"] = min(o["bb"][0] for o in g["letters"]); g["lx1"] = max(o["bb"][2] for o in g["letters"])
    g["ly0"] = min(o["bb"][1] for o in g["letters"]); g["ly1"] = max(o["bb"][3] for o in g["letters"])
    g["geom"] = unary_union([o["geom"] for o in g["letters"]])
    g["rails"] = [r_ for r_ in rails if not g["on_plate"] and r_["y0"] >= g["y0"] - 5 and r_["y1"] <= g["y1"] + 5
                  and r_["x1"] > g["x0"] and r_["x0"] < g["x1"]]
    g["per"] = sum(K.perim(o["sub"]) for o in g["letters"]) / 1000
    g["area"] = g["geom"].area / 1e6
# spec grupių priskyrimas: plokštės grupė <-> on_plate; kitos - pagal artimiausią kliento spalvą
for g in groups:
    cands = [sg for sg in spec["groups"] if bool(sg.get("on_plate")) == g["on_plate"]]
    col = g["letters"][0]["fill"]
    g["spec"] = min(cands, key=lambda sg: sum((a - b) ** 2 for a, b in zip(sg.get("client_fill", col), col)))
    g["name"] = g["spec"]["name"]
# bėgeliai: iš kliento failo (stačiakampiai) arba iš spec (Rytio detalizacija: rėmas + tvirtinimo plokštelės)
for g in groups:
    for r_ in g["rails"]:
        r_["poly"] = [(r_["x0"], r_["y0"]), (r_["x1"], r_["y0"]), (r_["x1"], r_["y1"]), (r_["x0"], r_["y1"])]
        r_["len"] = max(r_["x1"] - r_["x0"], r_["y1"] - r_["y0"])
        r_["kind"] = "h" if r_["x1"] - r_["x0"] >= r_["y1"] - r_["y0"] else "v"
    g["fplates"] = []
    if g["spec"].get("no_rails"):          # v10: grupė be savo rėmo (pvz. P00 apskritimas už raidžių)
        g["rails"] = []
    if g["spec"].get("rails"):
        ox_, oy_ = (g["x0"], g["y0"]) if g["plate"] else (g["lx0"], g["ly0"])
        nr = []
        for it in g["spec"]["rails"]:
            pts = [(ox_ + x, oy_ + y) for x, y in it["poly"]]
            xs_, ys_ = [q[0] for q in pts], [q[1] for q in pts]
            L_ = max(math.dist(pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts)))
            nr.append({"x0": min(xs_), "y0": min(ys_), "x1": max(xs_), "y1": max(ys_), "poly": pts, "len": it.get("len", L_),   # v160: originalo ilgis
                       "kind": it.get("kind", "h")})
        g["rails"] = nr
        g["fplates"] = [(ox_ + x, oy_ + y) for x, y in g["spec"].get("fit_plates", [])]
    g["fpl_sz"] = g["spec"].get("fit_plate_size", 30)
    g["rsz"] = (PRAIL if (g["plate"] and PRAIL) else RAIL)
PLATE_SZ = 30


def zframe_geom(g):
    """Z juostos ir sieninis rėmas plokštės grupei. y - nuo viršaus (mm), d - gylis nuo plokštės nugaros."""
    zf, zw, zt, tb = ZF["zf"], ZF["zw"], ZF["zt"], ZF["tb"]
    pg = g["plate"]["geom"]
    X = g["geom"]
    D = g["y1"] - g["y0"]
    fp = 2 * zf - zt                                   # Z juostos aukštis vaizde iš galo (flanšas + kablys)
    yA = g["y0"] + ZF["inset"] * D                     # viršutinės juostos viršus
    yB = g["y1"] - ZF["inset"] * D - fp                # apatinės juostos viršus
    inner = X.buffer(-ZF["edge_mm"])
    xs = range(int(g["x0"]), int(g["x1"]) + 1)

    def xfit(ya, yb):                                  # flanšo juostos galai: abu kampai >= edge_mm X viduje
        ok = [x for x in xs if inner.covers(Point(x, ya)) and inner.covers(Point(x, yb))]
        return (ok[0], ok[-1]) if ok else (None, None)
    fits = [xfit(yA, yA + zf), xfit(yB, yB + zf)]     # tvirtinama flanšo dalis (prie plokštės)
    # rėmas (Z + vamzdeliai) - apskritimo viduje, >= circle_margin nuo krašto
    fy0, fy1 = yA + zf, yB + fp + zf
    cx_, cy_ = (g["x0"] + g["x1"]) / 2, (g["y0"] + g["y1"]) / 2
    R_ = D / 2

    def chord(y):
        h_ = math.sqrt(max(0.0, R_ ** 2 - (y - cy_) ** 2)); return cx_ - h_, cx_ + h_
    cl = max(chord(y)[0] for y in (fy0, fy1)) + ZF["circle_margin"] + ZF["gap_mm"] + tb
    cr = min(chord(y)[1] for y in (fy0, fy1)) - ZF["circle_margin"] - ZF["gap_mm"] - tb
    lefts = [f[0] for f in fits if f[0] is not None]; rights = [f[1] for f in fits if f[1] is not None]
    sx0 = max(lefts + [cl]); sx1 = min(rights + [cr])
    sx0, sx1 = math.ceil(sx0 / 5) * 5, math.floor(sx1 / 5) * 5      # apvalinama 5 mm į vidų
    for yy_ in (yA, yB):                               # galų patikra: abu flanšo kampai X viduje (>= edge_mm)
        for xx_ in (sx0, sx1):
            if not (inner.covers(Point(xx_, yy_)) and inner.covers(Point(xx_, yy_ + zf))):
                print(f"  ! Z juostos galas x{xx_:.0f} y{yy_:.0f} ne X viduje - tvirtinimai matysis, tikrinti")
    print(f"  Z rėmas: X ribos {fits}, apskritimo riba {cl:.0f}/{cr:.0f} -> Z juostos {sx0:.0f}..{sx1:.0f} = {sx1 - sx0:.0f} mm")
    fx0, fx1 = sx0 - ZF["gap_mm"] - tb, sx1 + ZF["gap_mm"] + tb
    return {"D": D, "yA": yA, "yB": yB, "fp": fp, "sx0": sx0, "sx1": sx1, "L": sx1 - sx0,
            "fx0": fx0, "fx1": fx1, "fy0": fy0, "fy1": fy1, "LF": fx1 - fx0 - 2 * tb, "LT": fy1 - fy0,
            "W": fx1 - fx0, "fits": fits}


def zsection(y0, frame):
    """Z skerspjūvis (d - gylis nuo plokštės nugaros, y nuo viršaus): plokštės Z - flanšas prie plokštės aukštyn,
    sienelė, kablys žemyn; rėmo Z - tas pats, nuleistas per flanšą (flanšas aukštyn už plokštės Z kablio)."""
    zf, zw, zt = ZF["zf"], ZF["zw"], ZF["zt"]
    y = y0 + (zf if frame else 0)
    return [(0, y), (zt, y), (zt, y + zf - zt), (zw, y + zf - zt), (zw, y + 2 * zf - zt), (zw - zt, y + 2 * zf - zt),
            (zw - zt, y + zf), (0, y + zf)]


def ear4(g, fp):
    """(px, py) iš spec fit_plates arba (px, py, h, hole_y) iš auseles.py"""
    if len(fp) == 4:
        return fp
    return fp[0], fp[1], g["fpl_sz"], fp[1] + g["fpl_sz"] / 2
# ---------------- Rytio standartas (kai bėgelių rėmas neduotas detalizacijoje):
#  raidės (P6) su "frame": "verticals" - viršutinis + apatinis bėgelis, sujungti >= 2 statmenais bėgeliais;
#  "frame": "horizontal" - tik horizontalūs bėgeliai (darbo valandos). Ausėlės pagal ilgį, min 4 grupėje.
# ---------------- Rytio taisyklė: nuskaityto bėgelio galas - 10 mm nuo raidės krašto toje vietoje, kur eina
#  bėgelis (abu galo kampai raidės viduje, >= 10 mm nuo kontūro); per trumpas - pailginamas, per ilgas - trumpinamas.
#  Vertikalus (pvz. i taškui) - prasideda nuo viršutinio bėgelio viršutinės plokštumos (apatinio - apatinės),
#  galas - pagal tą pačią 10 mm taisyklę; tarpas, kur bėgelis matosi tarp formų, leidžiamas.
RAIL_EDGE = spec.get("rail_edge_mm", 10)


def _fit_h_end(r_, geoms, side):
    """galo raidė = raidė, kurioje galas yra; jei galas tarpe - artimiausia raidė į išorę (pailginti),
    jei išorėje nėra - artimiausia į vidų (patrumpinti). Galas = kraštinė padėtis, kur abu kampai
    >= RAIL_EDGE tos raidės viduje."""
    y0, y1 = r_["y0"], r_["y1"]
    cy = (y0 + y1) / 2
    band = sbox(-1e6, y0, 1e6, y1)
    cand = [o for o in geoms if o.intersects(band)]
    if not cand:
        return None
    xe = r_["x1"] if side == "r" else r_["x0"]
    # Rytis 2026-10-07: galas raidės SKYLĖJE (pvz. „6" akutė) - bėgelis eina tik iki skylės: galas patrumpinamas
    # į skylę ribojančią liniją, 10 mm nuo skylės krašto (raidės nekerta per visą)
    pe = Point(xe, cy)
    for o in cand:
        parts = list(getattr(o, "geoms", [o]))
        if not o.covers(pe) and any(Polygon(q.exterior).contains(pe) for q in parts if hasattr(q, "exterior")):
            inner = o.buffer(-RAIL_EDGE)
            rng_ = range(int(xe), int(r_["x0"]), -1) if side == "r" else range(int(xe), int(r_["x1"]))
            for x in rng_:
                if inner.covers(Point(x, y0)) and inner.covers(Point(x, y1)):
                    return float(x)
            break
    inside = [o for o in cand if o.bounds[0] - 1 <= xe <= o.bounds[2] + 1 and o.intersection(band).distance(Point(xe, cy)) < 1]
    if inside:
        term = max(inside, key=lambda o: o.bounds[2]) if side == "r" else min(inside, key=lambda o: o.bounds[0])
    else:
        outw = [o for o in cand if (o.bounds[0] > xe if side == "r" else o.bounds[2] < xe)]
        if outw:
            term = min(outw, key=lambda o: o.bounds[0]) if side == "r" else max(outw, key=lambda o: o.bounds[2])
        else:
            term = max(cand, key=lambda o: o.bounds[2]) if side == "r" else min(cand, key=lambda o: o.bounds[0])
    inner = term.buffer(-RAIL_EDGE)
    if inner.is_empty:
        return None
    if inside:
        # Rytis 2026-10-07: galas raidės linijoje - bėgelis tęsiamas tik iki TOS PAČIOS linijos krašto (pvz. iki
        # „6" akutės), ne per visą raidę: einama išorėn kol bėgelio pjūvis raidėje, tada atgal iki 10 mm taisyklės
        from shapely.geometry import LineString as _LSx
        st = 1 if side == "r" else -1
        x = int(xe)
        while term.covers(_LSx([(x + st, y0), (x + st, y1)])) and term.bounds[0] - 1 <= x + st <= term.bounds[2] + 1:
            x += st
        for xx in range(x, int(xe) - st * 2000, -st):
            if inner.covers(Point(xx, y0)) and inner.covers(Point(xx, y1)):
                return float(xx)
    rng_ = range(int(term.bounds[2]), int(term.bounds[0]) - 1, -1) if side == "r" else \
        range(int(term.bounds[0]), int(term.bounds[2]) + 1)
    for x in rng_:
        if inner.covers(Point(x, y0)) and inner.covers(Point(x, y1)):
            return float(x)
    return None


def _fit_v_end(v_, geoms, y_from, up):
    """vertikalaus bėgelio galas formoje virš (up) / po bėgeliu: abu kampai >= RAIL_EDGE formos viduje"""
    x0, x1 = v_["x0"], v_["x1"]
    reg = sbox(x0, v_["y0"], x1, y_from) if up else sbox(x0, y_from, x1, v_["y1"])
    cand = [o for o in geoms if o.intersects(reg)]
    if not cand:
        return None
    term = min(cand, key=lambda o: o.bounds[1]) if up else max(cand, key=lambda o: o.bounds[3])
    inner = term.buffer(-RAIL_EDGE)
    if inner.is_empty:
        return None
    rng_ = range(int(term.bounds[1]), int(term.bounds[3]) + 1) if up else range(int(term.bounds[3]), int(term.bounds[1]) - 1, -1)
    for y in rng_:
        if inner.covers(Point(x0, y)) and inner.covers(Point(x1, y)):
            return float(y)
    return None


def _rail(x0, y0, x1, y1, kind):
    return {"x0": x0, "y0": y0, "x1": x1, "y1": y1, "kind": kind, "len": max(x1 - x0, y1 - y0),
            "poly": [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]}


V_CLEAR = spec.get("vertical_ear_clear_mm", 30)     # statmuo - min. tarpas iki ausėlės x ribos


def place_verticals(g, LET, es, frame=None):
    """Rytis 2026-10-07: rėmo statmenys - TIK po raidėmis (visą statmenį dengia raidė, >= RAIL_EDGE nuo kontūro
    šonuose), jų x NESUTAMPA su ausėlėmis (tarpas >= V_CLEAR); statmuo - papildomas elementas, ausėlių ir
    bėgelių sprendimų nekeičia. Kiekis max(2, ceil(ilgis/2500)+1), padėtys - artimiausios tolygiam išdėstymui."""
    top, bot, t_ = frame or g["_vframe"]
    y0, y1 = top["y1"], bot["y0"]
    xa, xb = max(top["x0"], bot["x0"]), min(top["x1"], bot["x1"]) - t_
    cover = LET.buffer(-RAIL_EDGE)
    ear_x = [(fp[0], fp[0] + es) for fp in g["fplates"]]
    feas = []
    x = xa
    while x <= xb:
        ok = cover.covers(sbox(x, y0 + 0.5, x + t_, y1 - 0.5)) and \
            all(x + t_ + V_CLEAR <= e0 or x >= e1 + V_CLEAR for e0, e1 in ear_x)
        if ok:
            feas.append(x)
        x += 5
    VR = g["spec"].get("verticals")
    if len(feas) < 2 and not (VR and all(v_.get("mode") == "leg" for v_ in VR)):   # v29: tik pasvirę - tikrinama kitaip
        print(f"  ! {g['name']}: statmenims nėra vietos po raidėmis (ne ausėlių vietose) - spręsti ranka")
        return
    if VR:                                               # aiškiai nurodytos vietos (EXTRA standartas)
        place_verticals_rule(g, VR, feas, y0, y1, t_)
        return
    nv = max(2, math.ceil((xb - xa) / 2500) + 1)
    # v91 (Rytis 2026-10-11): statmuo per RAIDĖS (stiebo) CENTRĄ, ne prie krašto - galimos vietos grupuojamos į
    #  ištisines atkarpas (stiebus), statmuo dedamas atkarpos viduryje.
    # v95 (Rytis 2026-10-11, TESTAS): raidė be tiesaus stiebo (A) - ĮSTRIŽAS statmuo per kojelės vidurį (kaip EXTRA);
    #  GALINIAI statmenys - arčiausiai rėmo galų (stiebas arba įstrižas), tarpiniai - tolygiai (kiekis pagal taisyklę;
    #  v96 po vizualinės patikros: E po T reikalingas - TESTAS: T, E, T, įstrižas ant A).
    runs, cur = [], [feas[0]]
    for f in feas[1:]:
        if f - cur[-1] > 5.5:
            runs.append(cur); cur = [f]
        else:
            cur.append(f)
    runs.append(cur)
    cands = [{"x": round((r_[0] + r_[-1]) / 2 / 5) * 5 + t_ / 2 if len(r_) > 1 else r_[0] + t_ / 2, "k": "v"} for r_ in runs]
    for o in g["letters"]:
        bx0_, _, bx1_, _ = o["bb"]
        if o["bb"][1] > y0 + 1 or o["bb"][3] < y1 - 1 or any(bx0_ <= c_["x"] <= bx1_ for c_ in cands if c_["k"] == "v"):
            continue
        for sd_ in ("left", "right"):
            ln_ = _leg_line(o, y0, y1, sd_)
            if ln_:
                cands.append({"x": (ln_[0] + ln_[1]) / 2, "k": "d", "line": ln_})
    if not cands:
        return
    sp_ = (xb - xa) / max(nv - 1, 1)
    gap_ = 300                                          # v96: kiekis pagal taisyklę lieka (E po T reikalingas - Rytis)
    left_ = min(cands, key=lambda c_: c_["x"])
    right_ = max(cands, key=lambda c_: c_["x"])
    chosen = [left_] + ([right_] if right_["x"] - left_["x"] >= gap_ else [])
    for i in range(1, nv - 1):
        tx = xa + sp_ * i
        c_ = [c for c in cands if all(abs(c["x"] - q["x"]) >= gap_ for q in chosen)]
        if not c_:
            continue
        chosen.append(min(c_, key=lambda c: (c["k"] != "v", abs(c["x"] - tx))))
    chosen.sort(key=lambda c_: c_["x"])
    if len(chosen) < nv:
        print(f"  {g['name']}: statmenų {len(chosen)} (taisyklė {nv}) - per raidžių centrus / įstrižus, artimi (< {gap_:.0f} mm) nededami")
    for c_ in chosen:
        if c_["k"] == "v":
            x = c_["x"] - t_ / 2
            g["rails"].append({"x0": x, "x1": x + t_, "y0": y0, "y1": y1, "kind": "v", "len": y1 - y0,
                               "poly": [(x, y0), (x + t_, y0), (x + t_, y1), (x, y1)]})
        else:
            xc0, xc1, b = c_["line"]
            wh = t_ / 2 * math.sqrt(1 + b * b)
            poly_ = [(xc0 - wh, y0), (xc0 + wh, y0), (xc1 + wh, y1), (xc1 - wh, y1)]
            g["rails"].append({"x0": min(q[0] for q in poly_), "x1": max(q[0] for q in poly_), "y0": y0, "y1": y1,
                               "kind": "d", "len": math.hypot(xc1 - xc0, y1 - y0), "poly": poly_,
                               "ang": math.degrees(math.atan(b))})
    chosen = [c_["x"] - t_ / 2 for c_ in chosen]
    print(f"  {g['name']}: statmenys {len(chosen)} vnt. x = {[round(c - g['lx0']) for c in sorted(chosen)]} "
          f"(nuo grupės kairės, per raidžių stiebų centrą, >= {V_CLEAR} mm nuo ausėlių)")


def _leg_line(o, y0, y1, side="right", single=False):
    """pasvirusios kojelės (A, V ...) vidurio tiesė tarp y0 ir y1 -> (x ties y0, x ties y1, nuolydis) arba None"""
    geo, (bx0, _, bx1, _) = o["geom"], o["bb"]
    pts = []
    for k in range(8):
        y = y0 + (y1 - y0) * (0.4 + 0.075 * k)
        iv = _stroke_centers(geo, y, bx0, bx1)
        if len(iv) >= 2 or (iv and single):
            a_, b_ = iv[-1] if side == "right" else iv[0]
            pts.append(((a_ + b_) / 2, y))
    if len(pts) < 4:
        return None
    n_ = len(pts); my = sum(q[1] for q in pts) / n_; mx = sum(q[0] for q in pts) / n_
    b = sum((q[1] - my) * (q[0] - mx) for q in pts) / max(sum((q[1] - my) ** 2 for q in pts), 1e-9)
    if abs(b) < 0.08:                                    # beveik vertikalus - ne kojelė
        return None
    xc0, xc1 = mx + b * (y0 - my), mx + b * (y1 - my)
    if not (bx0 - 5 <= min(xc0, xc1) and max(xc0, xc1) <= bx1 + 5):
        return None
    return xc0, xc1, b


def _stroke_centers(geom, y, bx0, bx1):
    """raidės pjūvio intervalų centrai horizontalėje y: [(xa, xb), ...]"""
    from shapely.geometry import LineString as _L
    ix = geom.intersection(_L([(bx0 - 10, y), (bx1 + 10, y)]))
    segs = [q for q in getattr(ix, "geoms", [ix]) if not q.is_empty and q.length > 1]
    return sorted((min(q.coords[0][0], q.coords[-1][0]), max(q.coords[0][0], q.coords[-1][0])) for q in segs)


def place_verticals_rule(g, VR, feas, y0, y1, t_):
    """Rytis 2026-10-07 (EXTRA standartas): statmenys nurodytose vietose -
    {"at": "start"} - pirmoji galima vieta po pirmąja raide (rėmo pradžia);
    {"under": i, "mode": "stem"} - po i-tąja raide (pagal x, nuo 0) per jos stiebo vidurį (pvz. T);
    {"under": i, "mode": "leg", "side": "right"|"left"} - pasviręs, atkartoja raidės kojelės pasvirimą per jos vidurį (A)."""
    lets = sorted(g["letters"], key=lambda o: o["bb"][0])
    for it in VR:
        if it.get("at") == "start":
            x = feas[0]
            g["rails"].append({"x0": x, "x1": x + t_, "y0": y0, "y1": y1, "kind": "v", "len": y1 - y0,
                               "poly": [(x, y0), (x + t_, y0), (x + t_, y1), (x, y1)]})
            continue
        o = lets[min(it["under"], len(lets) - 1)]
        geo, (bx0, _, bx1, _) = o["geom"], o["bb"]
        if it.get("mode", "stem") == "stem":
            cs = []
            for f in (0.2, 0.35, 0.5, 0.65, 0.8):
                y = y0 + (y1 - y0) * f
                iv = _stroke_centers(geo, y, bx0, bx1)
                if iv:
                    a_, b_ = min(iv, key=lambda q: abs((q[0] + q[1]) / 2 - (bx0 + bx1) / 2))
                    cs.append((a_ + b_) / 2)
            if not cs:
                print(f"  ! {g['name']}: statmuo po raide {it['under']} - stiebas nerastas"); continue
            xc = sorted(cs)[len(cs) // 2]
            x = xc - t_ / 2
            g["rails"].append({"x0": x, "x1": x + t_, "y0": y0, "y1": y1, "kind": "v", "len": y1 - y0,
                               "poly": [(x, y0), (x + t_, y0), (x + t_, y1), (x, y1)]})
        else:                                            # pasvirusi kojelė - tiesė per kojelės vidurį
            pts = []
            for k in range(8):
                y = y0 + (y1 - y0) * (0.4 + 0.075 * k)
                iv = _stroke_centers(geo, y, bx0, bx1)
                if len(iv) >= 2 or (iv and it.get("single")):   # v29: "single" - vienas pasviręs stiebas (pvz. „7")
                    a_, b_ = iv[-1] if it.get("side", "right") == "right" else iv[0]
                    pts.append(((a_ + b_) / 2, y))
            if len(pts) < 2:
                print(f"  ! {g['name']}: pasviręs statmuo po raide {it['under']} - kojelė nerasta"); continue
            n_ = len(pts); my = sum(q[1] for q in pts) / n_; mx = sum(q[0] for q in pts) / n_
            b = sum((q[1] - my) * (q[0] - mx) for q in pts) / max(sum((q[1] - my) ** 2 for q in pts), 1e-9)
            xc0, xc1 = mx + b * (y0 - my), mx + b * (y1 - my)
            wh = t_ / 2 * math.sqrt(1 + b * b)
            poly_ = [(xc0 - wh, y0), (xc0 + wh, y0), (xc1 + wh, y1), (xc1 - wh, y1)]
            g["rails"].append({"x0": min(q[0] for q in poly_), "x1": max(q[0] for q in poly_), "y0": y0, "y1": y1,
                               "kind": "d", "len": math.hypot(xc1 - xc0, y1 - y0), "poly": poly_,
                               "ang": math.degrees(math.atan(b))})
    vv = [r_ for r_ in g["rails"] if r_["kind"] in ("v", "d")]
    print(f"  {g['name']}: statmenys pagal taisyklę {len(vv)} vnt.: " +
          ", ".join(f"{r_['kind']} x{round((r_['x0'] + r_['x1']) / 2 - g['lx0'])} L{round(r_['len'])}" for r_ in vv))


EARS = {"inset": 50, "size": None, "hole_d": 6, "min_edge": 15, "end_window": 300}
EARS.update(spec.get("ears", {}))
# Rytis 2026-10-07: ausėlės skylė - Ø6 ant 30 mm profilio, Ø8 ant 40 mm ir didesnių (jei spec nenurodo kitaip)
if "hole_d" not in spec.get("ears", {}):
    EARS["hole_d"] = 6 if float(RAIL.get("depth", 30)) <= 30 else 8
EAR_HOLE = EARS["hole_d"]
# v90 (Rytis 2026-10-11): montavimo būdas - "ears" (standartas, ausėlės), "brackets" (be ausėlių: U laikikliai per
#  viršutinį ir apatinį bėgelį, assets/tvirtinimas.json "brackets"), "none" (atskiros raidės be rėmo - kitas modulis)
MOUNTING = str(spec.get("mounting", "ears")).lower()
# v103 (Rytis 2026-10-11): sutartinis užrašas - rėmo aprašas "+ hangers" (pvz. "frame 30x30x2 + hangers RAL 7024") = U laikikliai,
#  "+ ears" = ausėlės. Jei spec "mounting" nenurodytas - imamas iš rėmo aprašo (MAIN DATA "Rails" / "frame").
if "mounting" not in spec:
    _ftxt = " ".join(str(b_) for a_, b_ in spec.get("main_data", []) if re.match(r"rail|frame", str(a_), re.I)) + " " + str(spec.get("frame", ""))
    if re.search(r"\+\s*hangers?\b", _ftxt, re.I):
        MOUNTING = "brackets"
        print("  montavimas: rėmo aprašas '+ hangers' -> U laikikliai (mounting=brackets)")
BRK = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "tvirtinimas.json")))["brackets"]
BRK.update(spec.get("brackets", {}))
for g in groups:
    if g["plate"] and ZF:
        g["zfr"] = zframe_geom(g)
        g["rails"] = []
def client_frame_issues(g, t_):
    """v106: kliento horizontalūs bėgeliai lyginami su skill rėmu (auto_remas - ašys per tvirtinimo ploto centrą,
    per visą eilutę). Grąžina priežasčių sąrašą (tuščias - kliento rėmas tvarkingas)."""
    import auto_remas as AR
    try:
        hs_a, _ = AR.build(g, t_, RAIL_EDGE, log=lambda *a_, **k_: None)
    except Exception as ex_:
        return []
    ch = [r_ for r_ in g["rails"] if (r_["x1"] - r_["x0"]) >= (r_["y1"] - r_["y0"])]
    if not hs_a:
        return []
    why = []
    tol = spec.get("client_frame_tol_mm", max(15.0, 1.5 * t_))
    gw = max(o["bb"][2] for o in g["letters"]) - min(o["bb"][0] for o in g["letters"])
    if any((a_["x1"] - a_["x0"]) < 0.5 * gw for a_ in hs_a) and len(AR.rows_of(g["letters"])) == 1:
        print(f"  {g['name']}: skill rėmo (auto) sudaryti nepavyko - paliekamas kliento rėmas, PATIKRINTI ranka")
        return []
    longs = [r_ for r_ in ch if (r_["x1"] - r_["x0"]) >= 0.5 * gw / max(1, len(AR.rows_of(g["letters"])))]
    for a_ in hs_a:
        acy = (a_["y0"] + a_["y1"]) / 2
        near = min(longs, key=lambda r_: abs((r_["y0"] + r_["y1"]) / 2 - acy), default=None)
        if near is None:
            why.append(f"trūksta bėgelio ties y{acy:.0f}"); continue
        d_ = abs((near["y0"] + near["y1"]) / 2 - acy)
        if d_ > tol:
            why.append(f"bėgelis y{(near['y0'] + near['y1']) / 2:.0f} ne per tvirtinimo ploto centrą (skill y{acy:.0f}, {d_:.0f} mm)")
        al = a_["x1"] - a_["x0"]
        if (near["x1"] - near["x0"]) < 0.6 * al:
            why.append(f"bėgelis y{(near['y0'] + near['y1']) / 2:.0f} per trumpas ({near['x1'] - near['x0']:.0f} < {al:.0f})")
    if len(longs) > len(hs_a) + 1:
        why.append(f"per daug ilgų bėgelių ({len(longs)} vietoj {len(hs_a)})")
    return why


def _attach_plates(g):
    """v179 (Rytis 2026-10-13: „tvirtinimo ausėlės kai kur kabo ore, taip neturėtų būti") - originalo fitting plate taškas
    (skylė) lieka vietoje, o plokštelė (fit_plate_size x fit_plate_len, numatyta 40 x 75) visada PRIVIRINTA prie
    artimiausio bėgelio: tęsiama nuo skylės iki bėgelio (užeina ant jo iki ašies). Jokia plokštelė nekabo ore."""
    sz = g["fpl_sz"]; Lp = g["spec"].get("fit_plate_len", 75)
    out = []
    for fp in g["fplates"]:
        px, py = fp[0], fp[1]
        hx, hy = px + sz / 2, (fp[3] if len(fp) == 4 else py + sz / 2)
        best = None
        for r_ in g["rails"]:
            if r_["x1"] - r_["x0"] < r_["y1"] - r_["y0"]:            # vertikalus - plokštelė tęsiama vertikaliai, netinka
                continue
            if not (r_["x0"] - 1 <= hx <= r_["x1"] + 1):
                continue
            d_ = 0 if r_["y0"] <= hy <= r_["y1"] else min(abs(hy - r_["y0"]), abs(hy - r_["y1"]))
            if best is None or d_ < best[0]:
                best = (d_, r_)
        if best is None:
            out.append(fp); print(f"  ! ausėlė x{hx:.0f} y{hy:.0f}: šalia nėra horizontalaus bėgelio - tikrinti"); continue
        r_ = best[1]; mid = (r_["y0"] + r_["y1"]) / 2
        if hy <= mid:                                    # skylė virš bėgelio - plokštelė žemyn iki bėgelio
            y0_ = hy - sz / 2; y1_ = min(max(y0_ + Lp, mid), r_["y1"])
        else:                                            # skylė po bėgeliu - plokštelė aukštyn
            y1_ = hy + sz / 2; y0_ = max(min(y1_ - Lp, mid), r_["y0"])
        out.append((px, y0_, y1_ - y0_, hy))
    return out


for g in groups:
    fr = g["spec"].get("frame")
    if g["plate"] or (not fr and not g["spec"].get("rails")) or g["spec"].get("no_rails"):
        continue
    if EARS.get("enabled", True) is False and g["spec"].get("rails"):   # rėmas be ausėlių (pvz. kvadratinis wallframe)
        # v160: detalizacijos ausėlės (fit_plates) paliekamos - tik automatinis išdėstymas išjungtas
        g["fplates"] = _attach_plates(g) if g["spec"].get("fit_plates") else []
        g["fp_rows"], g["fp_ext"], g["fp_missing"], g["ear_max"] = [], 0, 0, 0.0
        g["wall"] = spec.get("wall", "concrete")   # v90: fasadas nenurodytas = betonas (Rytis)
        continue
    t_ = g["rsz"]["depth"]
    # v106 (Rytis 2026-10-11): kliento rėmas netvarkingas (ne vietoje, per trumpas, ne pagal standartą) - perdaromas pagal
    #  skill (auto_remas), NEBENT nurodyta naudoti kliento struktūrą: spec / grupės "client_frame": true (arba "ears_pt" -
    #  kliento ausėlės = kliento rėmas, SPAR)
    if g["rails"] and not g["spec"].get("rails") and not (spec.get("client_frame") or g["spec"].get("client_frame")
                                                           or g["spec"].get("ears_pt") or spec.get("auto_frame") is False):
        _why = client_frame_issues(g, t_)
        if _why:
            print(f"  ! {g['name']}: kliento rėmas netvarkingas ({'; '.join(_why)}) -> perdaromas pagal skill"
                  f" (palikti kliento - spec \"client_frame\": true)")
            g["rails"] = []; g["_auto_reason"] = _why
    if (spec.get("auto_frame") or g.get("_auto_reason")) and not g["rails"] and not g["spec"].get("rails"):   # v75: rėmas iš raidžių (auto_remas.py)
        import auto_remas as AR
        if RAIL_ACR:                                  # v229: akrilinis - bėgelio plotis (ne gylis), statmuo po kiekviena raide
            hs, vs = AR.build(g, RAIL_W, RAIL_EDGE, pitch=ACRY["v_pitch"], pitch_heavy=ACRY["v_pitch"],
                              every_letter=bool(ACRY.get("every_letter")), v_edge=ACRY["v_edge"])
            # v243 (Rytis 2026-10-15: „kai raidės tokios mažos - bėgelis paplatinamas iki 60 mm (galimas ir platesnis, jei trukdo
            #  tvirtinimui ar laidams) ir naudojamas VIENAS"): jei tarp dviejų bėgelių lieka < bėgelio pločio - vienas platus
            #  bėgelis per abiejų ašių vidurį, statmenų nėra
            _hs2 = sorted(hs, key=lambda r_: r_["y0"])
            if len(_hs2) == 2 and _hs2[1]["y0"] - _hs2[0]["y1"] < RAIL_W:
                _cy = ((_hs2[0]["y0"] + _hs2[0]["y1"]) / 2 + (_hs2[1]["y0"] + _hs2[1]["y1"]) / 2) / 2
                _x0, _x1 = min(r_["x0"] for r_ in _hs2), max(r_["x1"] for r_ in _hs2)
                _ST, _gw0 = ACRY["stud"], float((ACRY.get("groove") or {}).get("w", 6) or 6)
                _go0 = _ST["cb_d"] / 2 + _gw0 / 2 + 2
                for _W1 in range(int(ACRY.get("single_w", 55)), 141, 5):    # v244/v245: platinti, kol visos dalys gauna >= 2 smeiges
                    _tr = [{"x0": _x0, "x1": _x1, "y0": _cy - _W1 / 2, "y1": _cy + _W1 / 2}]
                    if not _acr_studs(g["letters"], _tr, _ST, _go0, _gw0)[1]:
                        break
                _W1 = float(_W1)
                hs = [{"x0": _x0, "x1": _x1, "y0": _cy - _W1 / 2, "y1": _cy + _W1 / 2, "kind": "h", "auto": True, "len": _x1 - _x0,
                       "poly": [(_x0, _cy - _W1 / 2), (_x1, _cy - _W1 / 2), (_x1, _cy + _W1 / 2), (_x0, _cy + _W1 / 2)]}]
                vs = []
                print(f"  akrilinis rėmas {g['name']}: mažos raidės (tarpas tarp bėgelių {_hs2[1]['y0'] - _hs2[0]['y1']:.0f} < "
                      f"{RAIL_W:g}) - VIENAS bėgelis {_W1:g} mm, ašis y{_cy:.0f}")
                RAIL_W = _W1
                RAIL["size"] = f"{_W1:g}x{ACRY['thk']:g}"
        else:
            hs, vs = AR.build(g, t_, RAIL_EDGE)
            if MOUNTING == "l_hang":                  # v269: L profiliai (BILB26-01001) - tik horizontalūs, statmenų nėra
                vs = []
        g["rails"] = hs + vs
        g["_geoms"] = [o["geom"] for o in g["letters"]]
        g["_vframe"], g["_vframes"], g["_vfi"] = None, [], []
        g["_hs"], g["_ears_pending"] = hs, not RAIL_ACR
        if RAIL_ACR:                                  # ausėlių nėra - tvirtinama per Ø8 skyles akrile
            g["fplates"], g["fp_rows"], g["fp_ext"], g["fp_missing"], g["ear_max"] = [], [], 0, 0, 0.0
            g["wall"] = spec.get("wall", "concrete")
        continue
    if g["spec"].get("rails"):          # rėmas iš detalizacijos - tik ausėlės pagal taisykles
        hs = sorted([r_ for r_ in g["rails"] if r_["kind"] == "h"], key=lambda r_: r_["y0"])
        vs = [r_ for r_ in g["rails"] if r_["kind"] != "h"]
        fr = None
    else:
        hs, vcl = [], []
        for r_ in sorted(g["rails"], key=lambda r_: r_["y0"]):          # kliento grafika -> tikras profilio storis
            if (r_["y1"] - r_["y0"]) > (r_["x1"] - r_["x0"]):        # vertikalus (pvz. i taško laikiklis)
                cx = (r_["x0"] + r_["x1"]) / 2
                vcl.append({"x0": cx - t_ / 2, "x1": cx + t_ / 2, "y0": r_["y0"], "y1": r_["y1"], "kind": "v",
                            "len": r_["y1"] - r_["y0"], "poly": [(cx - t_ / 2, r_["y0"]), (cx + t_ / 2, r_["y0"]),
                                                                 (cx + t_ / 2, r_["y1"]), (cx - t_ / 2, r_["y1"])]})
                continue
            cy = (r_["y0"] + r_["y1"]) / 2
            # v49 (Joker 2026-10-09): bėgelis per arti raidžių viršaus / apačios (< 10 mm) - galai neranda vietos
            # raidėje; pastumiamas į vidų, kad iki raidžių krašto liktų >= RAIL_EDGE + 1
            _row = [o for o in g["letters"] if o["bb"][1] < cy < o["bb"][3]] or g["letters"]   # v74 merge_rows: tik bėgelio eilutės raidės
            _ry0, _ry1 = min(o["bb"][1] for o in _row), max(o["bb"][3] for o in _row)
            _big = [o["bb"] for o in _row if (o["bb"][3] - o["bb"][1]) >= 0.6 * (_ry1 - _ry0)]   # v57: 0.6 - skliaustai aukštesni už skaitmenis
            _big = _big or [o["bb"] for o in _row]
            _lo = max(b_[1] for b_ in _big) + RAIL_EDGE + 1 + t_ / 2      # žemiausias pilno aukščio raidžių viršus
            _hi = min(b_[3] for b_ in _big) - RAIL_EDGE - 1 - t_ / 2
            if _lo < _hi and not (_lo <= cy <= _hi):
                _ncy = min(max(cy, _lo), _hi)
                print(f"  {g['name']} bėgelis y{cy:.0f} -> y{_ncy:.0f} (>= {RAIL_EDGE + 1:.0f} mm nuo raidžių krašto)")
                cy = _ncy
            y0, y1 = cy - t_ / 2, cy + t_ / 2
            hs.append({"x0": r_["x0"], "x1": r_["x1"], "y0": y0, "y1": y1, "kind": "h", "len": r_["x1"] - r_["x0"],
                       "poly": [(r_["x0"], y0), (r_["x1"], y0), (r_["x1"], y1), (r_["x0"], y1)]})
        geoms_ = [o["geom"] for o in g["letters"]]
        OFP = next((h for h in groups if OF and h["plate"] and h["name"] == OF["plate"]), None) \
            if OF and g["name"] == OF["rails"] else None
        if OFP:                                          # v44: bėgeliai tęsiami už plokštės (vientisas rėmas)
            pgeo = OFP["plate"]["geom"]
            for i_, r_ in enumerate(hs):
                if pgeo.intersects(sbox(-1e6, r_["y0"], 1e6, r_["y1"])):
                    if OFP["x1"] <= g["lx0"] + 1:
                        hs[i_] = _rail(OFP["x0"] + 1, r_["y0"], r_["x1"], r_["y1"], "h")
                    elif OFP["x0"] >= g["lx1"] - 1:
                        hs[i_] = _rail(r_["x0"], r_["y0"], OFP["x1"] - 1, r_["y1"], "h")
            geoms_ = geoms_ + [pgeo]
            g["of_plate"] = OFP
        for i_, r_ in enumerate(hs):                     # horizontalių galai: 10 mm nuo raidės krašto
            nx0, nx1 = _fit_h_end(r_, geoms_, "l"), _fit_h_end(r_, geoms_, "r")
            if nx0 is not None and nx1 is not None and nx1 - nx0 > 100:
                print(f"  {g['name']} bėgelis y{r_['y0']:.0f}: galai {r_['x0']:.0f}/{r_['x1']:.0f} -> {nx0:.0f}/{nx1:.0f} (10 mm nuo raidės)")
                hs[i_] = _rail(nx0, r_["y0"], nx1, r_["y1"], "h")
        vs = []
        for v_ in vcl:                                   # vertikalūs (i taškas): nuo bėgelio plokštumos iki formos - 10 mm
            if hs and v_["y0"] < hs[0]["y0"] - 1:
                ny0 = _fit_v_end(v_, geoms_, hs[0]["y0"], True)
                v_ = _rail(v_["x0"], ny0 if ny0 is not None else v_["y0"], v_["x1"], hs[0]["y0"], "v")
            elif hs and v_["y1"] > hs[-1]["y1"] + 1:
                ny1 = _fit_v_end(v_, geoms_, hs[-1]["y1"], False)
                v_ = _rail(v_["x0"], hs[-1]["y1"], v_["x1"], ny1 if ny1 is not None else v_["y1"], "v")
            vs.append(v_)
        # statmenys dedami PO ausėlių (papildomas elementas - ausėlių sprendimo neįtakoja), žr. place_verticals
        g["_vframe"] = (hs[0], hs[-1], t_) if (fr == "verticals" and len(hs) >= 2) else None
        # v74 merge_rows: statmenys kiekvienos eilutės bėgelių porai (bėgeliai, tarp kurių yra raidžių)
        g["_vfi"] = [i for i in range(len(hs) - 1)
                     if fr == "verticals" and len(hs) >= 4 and spec.get("merge_rows")
                     and any(o["bb"][1] < hs[i]["y1"] and o["bb"][3] > hs[i + 1]["y0"]
                             and o["bb"][1] > hs[i]["y0"] - 0.5 * (o["bb"][3] - o["bb"][1]) for o in g["letters"])]
        g["_vframes"] = [(hs[i], hs[i + 1], t_) for i in g["_vfi"]]
        if g["_vframes"]:
            g["_vframe"] = None
        g["rails"] = hs + vs
        g["_geoms"] = geoms_
    g["_hs"], g["_ears_pending"] = hs, True


# ============================================================ v73 (Rytis 2026-10-10): 6 m STRYPŲ TAISYKLĖ
# Profiliai perkami 6 m strypais (assets/medziagos.json - Heliopolis: „Profilių ilgis - 6 metrai"). Rėmas, kuris
# sudėliotas gaunasi pvz. 6,05 m (2 x 3025), netelpa į vieną strypą - horizontalūs bėgeliai PATRUMPINAMI tiek, kad
# tilptų (su pjūklo prapjova), bet TIK nepažeidžiant kitų taisyklių: abu galo kampai >= RAIL_EDGE raidės viduje
# (ta pati kraštinė raidė), galas lieka kraštinės raidės IŠORINĖJE pusėje (v67), galas prie skylės nejuda.
# Detalizacijos rėmas (`groups[].rails`) ir statmenys - nekeičiami. Patrumpinimas - prieš ausėles (jos dedamos ant
# galutinio bėgelio). Išjungti / keisti: spec `"stock": {"enabled": false, "bar_mm": 6000, "kerf_mm": 3, "trim_max_mm": 100}`.
STOCK = MEDZ.cfg(spec.get("stock"))
if RAIL_ACR:
    STOCK["enabled"] = False                          # v229: akrilinis rėmas - iš lakšto, ne 6 m strypai
try:                                              # v98: strypai planuojami visam užsakymui (spec qty)
    QTY = max(1, int(str(spec.get("qty", 1)).split()[0]))
except (ValueError, IndexError):            # v203: tuščias qty (nežinoma - tuščias langelis)
    QTY = 1


def _h_slack(r_, geoms, side, cap_over=None):
    """kiek mm galima patrumpinti bėgelio galą nepažeidžiant 10 mm / išorinės pusės taisyklių"""
    y0, y1 = r_["y0"], r_["y1"]
    cy = (y0 + y1) / 2
    xe = r_["x1"] if side == "r" else r_["x0"]
    st = -1 if side == "r" else 1
    pe = Point(xe + st, cy)
    term = [o for o in geoms if o.intersects(sbox(-1e6, y0, 1e6, y1)) and o.buffer(0.5).covers(pe)]
    if not term:
        return 0.0
    term = min(term, key=lambda o: o.area)
    inner = term.buffer(-RAIL_EDGE)
    mid = (term.bounds[0] + term.bounds[2]) / 2
    s = 0
    cap = min(STOCK["trim_max"], r_["stroke"] / 2 - 15) if r_.get("auto") else STOCK["trim_max"]   # v75: auto rėmas - galas lieka stiebe
    if cap_over is not None:                          # v92: > 6 m bėgelis - be 100 mm ribos (galas lieka raidės išorinėje pusėje)
        cap = min(cap_over, r_["stroke"] / 2 - 15) if r_.get("auto") else cap_over
    while s < cap:
        x = xe + st * (s + 1)
        if (side == "r" and x < mid) or (side == "l" and x > mid):
            break
        if not (inner.covers(Point(x, y0)) and inner.covers(Point(x, y1))):
            break
        s += 1
    return float(s)


def _verticals_est(g):
    """statmenų kiekis ir ilgis PRIEŠ jų išdėstymą (place_verticals) - strypų skaičiavimui"""
    out = []
    for top, bot, t_ in ([g["_vframe"]] if g.get("_vframe") else []) + g.get("_vframes", []):
        VR = g["spec"].get("verticals")
        xa, xb = max(top["x0"], bot["x0"]), min(top["x1"], bot["x1"]) - t_
        n_ = len(VR) if VR else max(2, math.ceil((xb - xa) / 2500) + 1)
        out += [bot["y0"] - top["y1"]] * n_
    return out


STOCK_NOTE = {}                                   # profilis -> tekstas atsakymui / BOM
if STOCK["enabled"]:
    _byp = {}
    for g in groups:
        if not g.get("_ears_pending") or g["plate"]:
            continue
        _byp.setdefault(g["rsz"]["size"], []).append(g)
    # v92 (Rytis 2026-10-11): horizontalus bėgelis, ilgesnis už strypą, PIRMIAUSIA trumpinamas iki strypo ilgio (pvz.
    #  6500 -> 6000), jei galai lieka kraštinių raidžių viduje ir išorinėje pusėje - konstrukcija nesusilpnėja, o profilis
    #  sutaupomas (be sandūros). Tik jei netelpa - jungiama iš dalių (mažiausios atliekos).
    _use = STOCK["stock"] - STOCK["end"]
    for _gs in _byp.values():
        for g in _gs:
            if g["spec"].get("rails"):
                continue
            for i_, r_ in enumerate(g["_hs"]):
                ex_ = r_["len"] - _use
                if ex_ <= 0:
                    continue
                sl_, sr_ = _h_slack(r_, g["_geoms"], "l", ex_ + 5), _h_slack(r_, g["_geoms"], "r", ex_ + 5)
                if sl_ + sr_ + 1e-6 < ex_:
                    print(f"  6 m taisyklė: {g['name']} bėgelis y{r_['y0']:.0f} {r_['len']:.0f} - iki {_use:.0f} sutrumpinti negalima "
                          f"(galų laisvumas {sl_:.0f}/{sr_:.0f}) - jungiamas iš dalių")
                    continue
                l_, rr_ = MEDZ._split(math.ceil(ex_), sl_, sr_)
                nr_ = _rail(r_["x0"] + l_, r_["y0"], r_["x1"] - rr_, r_["y1"], "h")
                nr_.update({k_: r_[k_] for k_ in ("auto", "stroke") if k_ in r_})
                g["rails"][g["rails"].index(r_)] = nr_
                g["_hs"][i_] = nr_
                print(f"  6 m taisyklė: {g['name']} bėgelis y{r_['y0']:.0f}: {r_['len']:.0f} -> {nr_['len']:.0f} mm "
                      f"(-{l_:.0f} kairė / -{rr_:.0f} dešinė) - telpa į vieną {STOCK['stock'] / 1000:g} m strypą, be sandūros")
                STOCK_NOTE.setdefault(g["rsz"]["size"], f"rails trimmed to {STOCK['stock'] / 1000:g} m bars")
            if g.get("_vframe"):
                g["_vframe"] = (g["_hs"][0], g["_hs"][-1], g["_vframe"][2])
            if g.get("_vframes"):
                g["_vframes"] = [(g["_hs"][i], g["_hs"][i + 1], g["rsz"]["depth"]) for i in g["_vfi"]]
    for _sz, _gs in _byp.items():
        fixed_, adj_ = [], []
        for g in _gs:
            fixed_ += [r_["len"] for r_ in g["rails"] if r_["kind"] != "h"] + _verticals_est(g)
            for i_, r_ in enumerate(g["_hs"]):
                if g["spec"].get("rails"):                     # detalizacijos rėmas - nekeičiamas
                    fixed_.append(r_["len"])
                else:
                    adj_.append({"id": (g["name"], i_), "len": r_["len"],
                                 "slack": (_h_slack(r_, g["_geoms"], "l"), _h_slack(r_, g["_geoms"], "r"))})
        base_ = MEDZ.nest_bars((fixed_ + [a["len"] for a in adj_]) * QTY, STOCK["stock"], STOCK["kerf"], STOCK["end"])
        res_ = MEDZ.trim_to_stock(fixed_, adj_, STOCK, QTY)
        if res_:
            for g in _gs:
                for i_, r_ in enumerate(g["_hs"]):
                    l_, rr_ = res_["trims"].get((g["name"], i_), (0.0, 0.0))
                    if l_ + rr_ <= 0:
                        continue
                    nr_ = _rail(r_["x0"] + l_, r_["y0"], r_["x1"] - rr_, r_["y1"], "h")
                    nr_.update({k_: r_[k_] for k_ in ("auto", "stroke") if k_ in r_})
                    g["rails"][g["rails"].index(r_)] = nr_
                    g["_hs"][i_] = nr_
                    print(f"  6 m taisyklė: {g['name']} bėgelis y{r_['y0']:.0f}: {r_['len']:.0f} -> {nr_['len']:.0f} mm (-{l_:.0f} kairė / -{rr_:.0f} dešinė)")
            for g in _gs:
                if g.get("_vframe"):
                    g["_vframe"] = (g["_hs"][0], g["_hs"][-1], g["_vframe"][2])
                if g.get("_vframes"):
                    g["_vframes"] = [(g["_hs"][i], g["_hs"][i + 1], g["rsz"]["depth"]) for i in g["_vfi"]]
            STOCK_NOTE[_sz] = f"rails trimmed to fit {res_['bars']} x {STOCK['stock'] / 1000:g} m bars"
            print(f"  6 m taisyklė ({_sz}): {res_['bars0']} -> {res_['bars']} strypai; {MEDZ.bars_text(res_['plan'], STOCK['stock'])}")
        else:
            n0_ = len(base_)
            n_free = len(MEDZ.nest_bars((fixed_ + [max(a["len"] - STOCK["trim_max"], 1) for a in adj_]) * QTY,
                                        STOCK["stock"], STOCK["kerf"], STOCK["end"]))
            if adj_ and n_free < n0_:
                print(f"  ! 6 m taisyklė ({_sz}): rėmas {n0_} strypai, patrumpinus <= {STOCK['trim_max']:.0f} mm tilptų į {n_free}, "
                      f"bet trumpinti neleidžia 10 mm / išorinės pusės taisyklės (galų laisvumas: " +
                      ", ".join(f"{a['id'][0]} {a['slack'][0]:.0f}/{a['slack'][1]:.0f}" for a in adj_) + ") - Rytis sprendžia")
                STOCK_NOTE[_sz] = f"check: {n0_} bars (trim blocked)"
            else:
                print(f"  strypai ({_sz}): {MEDZ.bars_text(base_, STOCK['stock'])}")

# ---------------- v99 (Rytis 2026-10-11): RĖMO MATMENYS - APVALŪS (žingsnis 5 mm): gamybininkui sunku matuoti 3017 / 17 -
#  lengviau 3020 / 15. Horizontalių bėgelių ilgiai apvalinami iki 5 mm (abu galai po pusę; jei strypų daugėtų - žemyn),
#  tarpai tarp bėgelių (statmenų ilgiai) - iki 5 mm, paslenkant žemesnį bėgelį <= 2,5 mm. Detalizacijos rėmas nekeičiamas.
RND = float(spec.get("frame_round_mm", 5) or 0)


def _set_rail(r_, x0, y0, x1, y1):
    r_.update({"x0": x0, "y0": y0, "x1": x1, "y1": y1, "len": max(x1 - x0, y1 - y0),
               "poly": [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]})


if RND:
    _hs_all = [(g, r_) for g in groups if g.get("_ears_pending") and not g["plate"] and not g["spec"].get("rails")
               for r_ in g["_hs"]]
    if _hs_all:
        def _plan(fn):
            ls_ = [fn(r_["len"]) for _, r_ in _hs_all] + [r_["len"] for g in {id(g_): g_ for g_, _ in _hs_all}.values()
                                                           for r_ in g["rails"] if r_["kind"] != "h"]
            return len(MEDZ.nest_bars(ls_ * QTY, STOCK["stock"], STOCK["kerf"], STOCK["end"]))
        _near = lambda L: RND * round(L / RND)
        _down = lambda L: RND * math.floor(L / RND + 1e-9)
        _fn = _near if _plan(_near) <= _plan(lambda L: L) else _down
        _old = {id(r_): (r_["x0"], r_["y0"], r_["x1"], r_["y1"]) for _, r_ in _hs_all}
        for g, r_ in _hs_all:
            L0 = r_["len"]; L1 = _fn(L0); d_ = (L1 - L0) / 2
            if abs(L1 - L0) > 1e-6:
                _set_rail(r_, r_["x0"] - d_, r_["y0"], r_["x1"] + d_, r_["y1"])
        for g in {id(g_): g_ for g_, _ in _hs_all}.values():
            hs_ = g["_hs"]
            for i_ in range(1, len(hs_)):
                gap0 = hs_[i_]["y0"] - hs_[i_ - 1]["y1"]
                dy_ = RND * round(gap0 / RND) - gap0
                if abs(dy_) > 1e-6:
                    for r2_ in hs_[i_:]:
                        _set_rail(r2_, r2_["x0"], r2_["y0"] + dy_, r2_["x1"], r2_["y1"] + dy_)
            # jau esantys vertikalūs (auto rėmas: galiniai / tarpiniai statmenys, akcentų laikikliai) - paskui bėgelius
            for v_ in [q_ for q_ in g["rails"] if q_["kind"] == "v"]:
                nx0, ny0, nx1, ny1 = v_["x0"], v_["y0"], v_["x1"], v_["y1"]
                for r_ in hs_:
                    ox0, oy0, ox1, oy1 = _old[id(r_)]
                    if abs(v_["y0"] - oy1) < 0.6: ny0 = r_["y1"]
                    if abs(v_["y0"] - oy0) < 0.6: ny0 = r_["y0"]
                    if abs(v_["y1"] - oy0) < 0.6: ny1 = r_["y0"]
                    if abs(v_["y1"] - oy1) < 0.6: ny1 = r_["y1"]
                    if oy0 - 1 <= (v_["y0"] + v_["y1"]) / 2 <= oy1 + 1 or ny0 != v_["y0"] or ny1 != v_["y1"]:
                        if abs(v_["x1"] - ox0) < 0.6 or abs(v_["x0"] - ox0) < 0.6:      # galinis kairėje
                            dx_ = r_["x0"] - ox0; nx0, nx1 = v_["x0"] + dx_, v_["x1"] + dx_
                        elif abs(v_["x0"] - ox1) < 0.6 or abs(v_["x1"] - ox1) < 0.6:    # galinis dešinėje
                            dx_ = r_["x1"] - ox1; nx0, nx1 = v_["x0"] + dx_, v_["x1"] + dx_
                _set_rail(v_, nx0, ny0, nx1, ny1)
                v_["kind"] = "v"
            if g.get("_vframe"):
                g["_vframe"] = (hs_[0], hs_[-1], g["_vframe"][2])
            if g.get("_vframes"):
                g["_vframes"] = [(hs_[i], hs_[i + 1], g["rsz"]["depth"]) for i in g["_vfi"]]
            print(f"  {g['name']}: rėmo matmenys apvalinti iki {RND:g} mm - bėgeliai "
                  + ", ".join(f"{r_['len']:.0f}" for r_ in hs_) + "; tarpai "
                  + ", ".join(f"{hs_[i]['y0'] - hs_[i - 1]['y1']:.0f}" for i in range(1, len(hs_))))

for g in groups:
    if not g.pop("_ears_pending", False):
        continue
    hs, t_, fr = g["_hs"], g["rsz"]["depth"], g["spec"].get("frame")
    # tvirtinimo plokštelės (4A) - Rytio taisyklės iš sign_technical_workshop (fitting_plate_rules):
    #  dydis = profilis, Ø6 skylė centre, VISA skylė neužstota raidžių (prisukama iš priekio tarp raidžių),
    #  min. 2 viršutiniam + 2 apatiniam bėgeliui, ~1000 mm orientacinis žingsnis, vidurinis bėgis plokštelių negauna
    es = EARS["size"] or g["rsz"]["depth"]          # ausėlė = profilio dydis (30 arba 40)
    # Rytio taisyklė (references/auseles.md): galinės - lange 300 mm, geriausia laisva zona, pailginta tik be vietos;
    # tarpinės - pagal Smax lentelę (profilis, raidžių aukštis, script); viršus ir apačia - nepriklausomai.
    LET = unary_union([o["geom"] for o in g["letters"]])
    LET_V = LET                                      # statmenims - tik raidės (EXTRA: „po E", ne po apskritimu)
    if g.get("of_plate"):                            # v44: ausėlės ne už apskritimo (užstotų plokštė)
        LET = unary_union([LET, g["of_plate"]["plate"]["geom"]])
    # v77 (Rytis 2026-10-10): kelios eilutės ant vieno rėmo - ausėlės IR tarp užrašų: kiekvienos eilutės bėgelių pora
    #  gauna savo ausėles (viršutinis - žemyn, apatinis - aukštyn, už raidžių), t. y. ir viduriniai bėgeliai; eilučių
    #  poros tarpinės ausėlės dedamos ŠACHMATIŠKAI (antros eilutės tikslai paslinkti puse žingsnio).
    _pairs = [(hs[i], hs[i + 1]) for i in range(0, len(hs) - 1, 2)] if (spec.get("merge_rows") or spec.get("auto_frame")) and len(hs) >= 4 and len(hs) % 2 == 0 else [None]
    g["fplates"], g["fp_missing"], g["fp_rows"], g["fp_ext"] = [], 0, [], 0
    g["ear_max"] = 0.0
    _LET_ALL = LET
    for _pi, _pair in enumerate(_pairs):
        LET = _LET_ALL if _pair is None else unary_union([o["geom"] for o in g["letters"] if o["bb"][1] < _pair[1]["y1"] + 5 and o["bb"][3] > _pair[0]["y0"] - 5] or [_LET_ALL])
        _stagger = (_pi % 2 == 1)
        carriers = (list(_pair) if _pair else ([hs[0], hs[-1]] if len(hs) >= 2 else hs))
        if g["spec"].get("ears_rails") == "top":         # v11: vidaus iškabos - tvirtinama tik per viršutinį bėgelį
            carriers = [hs[0]]
        if g["spec"].get("ears") is False or MOUNTING != "ears":   # v13 / v90: be ausėlių (kliento faile nėra; U laikikliai)
            carriers = []
        _hs = sorted(o["bb"][3] - o["bb"][1] for o in g["letters"])
        H_ = _hs[len(_hs) // 2]                          # tipinis raidės aukštis (mediana; be p uodegų ir i taškų)
        smax_, skey_ = AUS.smax_lookup(g["rsz"]["depth"], g["spec"].get("font_style", "regular"), H_,
                                       g["spec"].get("ears_smax") or EARS.get("smax"))
        # apkrova: vėjas (EN 1991-1-4) + savasis svoris raidžių priekio plotui; dalinama tarp nešančių bėgelių
        PP_ = AUS.load_params(spec.get("mount"))
        qp_ = AUS.wind_qp(**PP_["wind"])
        qa_ = math.hypot(qp_ * PP_["wind"]["cf"], PP_["self_weight_kN_m2"])          # kN/m²
        wall_ = spec.get("wall", PP_["anchor"]["wall_default"])
        NR_ = PP_["anchor"]["N_rec_kN"].get(wall_, PP_["anchor"]["N_rec_kN"]["unknown"])
        share_ = 1.0 / max(1, len(carriers))
        from shapely.geometry import LineString as _LS
        gx0_, gx1_ = g["lx0"], g["lx1"]
        xs_g = [gx0_ + i * 10 for i in range(int((gx1_ - gx0_) // 10) + 2)]
        cum_ = [0.0]
        for xa_, xb_ in zip(xs_g, xs_g[1:]):
            hh = LET.intersection(_LS([((xa_ + xb_) / 2, g["ly0"] - 10), ((xa_ + xb_) / 2, g["ly1"] + 10)])).length
            cum_.append(cum_[-1] + hh * (xb_ - xa_) / 1e6 * qa_ * share_)                # kN

        def _cum(x):
            if x <= xs_g[0]:
                return 0.0
            if x >= xs_g[-1]:
                return cum_[-1]
            i = int((x - xs_g[0]) // 10)
            return cum_[i] + (cum_[i + 1] - cum_[i]) * (x - xs_g[i]) / 10
        g["ear_N"], g["wall"] = NR_, wall_
        # script šriftui Smax (0,65 x paprasto) - rekomendacija: leidžiama +15 %, jei sutaupoma pora
        # (Rytis 2026-10-07: MATKROKEN užtenka 8 ausėlių, ne 10); fizikos patikros lieka griežtos
        tol_ = EARS.get("smax_tol", 0.15 if g["spec"].get("font_style") == "script" else 0.05)   # Rytis 2026-10-07: +5 % jei sutaupoma pora (FAS1800 R)
        rinfo = []
        for k, r_ in enumerate(carriers):
            is_top = (k == 0 and len(carriers) > 1)
            base_, inw_ = (r_["y1"], 1) if is_top else (r_["y0"], -1)        # VISADA į rėmo vidų
            rx0, rx1 = r_["x0"], r_["x1"]

            def _LD(a, b, rx0=rx0, rx1=rx1):                  # raidės už bėgelio galų - prie galinio segmento
                return _cum(math.inf if b >= rx1 else b) - _cum(-math.inf if a <= rx0 else a)
            phys_ = {"load": _LD, "N": NR_, "size": g["rsz"]["size"], "P": PP_}
            ext_max_ = EARS.get("ext_max", 250)
            if len(carriers) > 1:                              # pailginta ausėlė - ne toliau nei rėmo vidaus vidurys
                other_ = carriers[-1] if is_top else carriers[0]
                gap_ = (other_["y0"] - r_["y1"]) if is_top else (r_["y0"] - other_["y1"])
                ext_max_ = max(0.0, min(ext_max_, gap_ / 2 - es))
            rinfo.append({"r": r_, "top": is_top, "x0": rx0, "x1": rx1, "base": base_, "inward": inw_,
                          "ext_max": ext_max_, "phys": phys_, "LD": _LD})
        res_, wfr_ = (None, [])
        _EPT = g["spec"].get("ears_pt")                   # v13: ausėlės kliento faile nurodytose vietose (x, pt)
        if _EPT is not None:
            res_ = []
            for ri in rinfo:
                xs_pt = _EPT.get("top" if ri["top"] else "bottom", []) if isinstance(_EPT, dict) else _EPT
                lst_ = []
                for xp_ in xs_pt:
                    x_ = (xp_ - OX) * S
                    x_ = min(max(x_, ri["x0"] + es / 2), ri["x1"] - es / 2)
                    h_, hy_ = es, ri["base"] + ri["inward"] * es / 2
                    while AUS._free(LET, x_, hy_, AUS.DEFAULTS["min_edge"]) is None and h_ < es + ri["ext_max"]:
                        h_ += 5; hy_ = ri["base"] + ri["inward"] * (h_ - es / 2)
                    if AUS._free(LET, x_, hy_, AUS.DEFAULTS["min_edge"]) is None:
                        h_, hy_ = es, ri["base"] + ri["inward"] * es / 2
                        print(f"  ! {g['name']}: kliento ausėlė x {x_:.0f} užstota raidės - tikrinti")
                    lst_.append({"x": x_, "hy": hy_, "h": h_, "ext": h_ > es + 1})
                res_.append(sorted(lst_, key=lambda e_: e_["x"]))
        elif len(rinfo) == 2:                                    # viršus + apačia kartu: tarpinės poromis vienoje linijoje
            n_min_ = PP_["redundancy"]["min_ears_long_rail"] if max(ri["x1"] - ri["x0"] for ri in rinfo) > \
                PP_["redundancy"]["long_rail_mm"] else 2
            _ax = [fp[0] + es / 2 for fp in g["fplates"]] if _stagger else []
            # v191: kraštinių ausėlių zona - tarp pilno aukščio raidžių (ne po kableliu / taškais už paskutinės raidės)
            # v238 (OMODA / EXLANTIX): trafaretinio šrifto raidė iš kelių dalių (E iš 3 juostų, O iš 2 pusių) - dalys, kurios
            #  persidengia x ir kartu užima >= 0,65 H, yra VIENA pilno aukščio raidė (anksčiau E juostos buvo „ne raidė" ->
            #  kraštinės ausėlės atsidurdavo po E juostomis, ne tarpe tarp raidžių)
            _cl = []
            for o in sorted(g["letters"], key=lambda o: o["bb"][0]):
                c_ = next((c for c in _cl if o["bb"][0] < c[1] - 1 and o["bb"][2] > c[0] + 1), None)
                if c_:
                    c_[0] = min(c_[0], o["bb"][0]); c_[1] = max(c_[1], o["bb"][2])
                    c_[2] = min(c_[2], o["bb"][1]); c_[3] = max(c_[3], o["bb"][3])
                else:
                    _cl.append([o["bb"][0], o["bb"][2], o["bb"][1], o["bb"][3]])
            _boxes = [(c[0], c[1]) for c in _cl if c[3] - c[2] >= 0.65 * H_]
            _ez = (min(b[0] for b in _boxes), max(b[1] for b in _boxes)) if _boxes else None
            res_, wfr_ = AUS.place_frame(LET, rinfo, es, smax_, dict(EARS, n_min=n_min_, smax_tol=tol_, avoid_x=_ax, end_zone=_ez,
                                                                            letter_boxes=_boxes))
            # v81 (Rytis 2026-10-10, LIETUVA apačia „per daug ausėlių, nesuprantama logika"): kai poromis su Smax neišeina,
            # NEPEREINAMA prie atskirų bėgelių (ten ausėlės sukrenta be logikos, pvz. 3861 + 4171) - Smax didinamas
            # pakopomis (+10 % iki +30 %) ir lieka PORŲ logika: tarpinės viršus / apačia vienoje linijoje, tolygiai.
            if res_ is None:
                _rg = [dict(ri, phys=None) for ri in rinfo]           # fizika (siena unknown) - tik perspėjimas, geometrija lieka
                for _t2, _ri in [(t_, rinfo) for t_ in (0.10, 0.20, 0.30)] + [(t_, _rg) for t_ in (tol_, 0.10, 0.20, 0.30)]:
                    if _ri is rinfo and _t2 <= tol_:
                        continue
                    res_, w2_ = AUS.place_frame(LET, _ri, es, smax_, dict(EARS, n_min=n_min_, smax_tol=_t2, avoid_x=_ax, end_zone=_ez,
                                                                         letter_boxes=_boxes))
                    if res_ is not None:
                        wfr_ = [f"poros sudėtos su Smax +{_t2 * 100:.0f} % ({smax_ * (1 + _t2):.0f} mm)"
                                + (", be fizikos patikros (siena / inkaras - tikrinti)" if _ri is _rg else "")
                                + " - laisvų vietų tarp raidžių mažai"] + w2_
                        break
            for w_ in wfr_:
                print(f"  ! {g['name']} rėmas: {w_}")
        for k, ri in enumerate(rinfo):
            r_, is_top, base_, _LD = ri["r"], ri["top"], ri["base"], ri["LD"]
            if res_ is not None:
                ears_, warn_ = res_[k], []
            else:
                cfg_ = dict(EARS, ext_max=ri["ext_max"], smax_tol=tol_)
                ears_, warn_ = AUS.place_rail(LET, ri["x0"], ri["x1"], base_, ri["inward"], es, smax_, cfg_, ri["phys"])
                if not ears_:                                  # fizikos patikros neišlaiko - geometrinis išdėstymas + perspėjimas
                    ears_, w2_ = AUS.place_rail(LET, ri["x0"], ri["x1"], base_, ri["inward"], es, smax_, cfg_, None)
                    if ears_:
                        warn_ = warn_ + ["fizikos patikros (konsolė / apkrova ausėlei) neišlaikytos - ausėlės sudėtos tik "
                                         "pagal geometriją ir Smax; tvirtinimą tikrinti (papildomos vertikalės?)"] + w2_
            rx0, rx1 = ri["x0"], ri["x1"]
            # v94 (Rytis 2026-10-11, TESTAS prie „S"): dvi ausėlės VIENA ŠALIA KITOS rėmo gale (< 0,5 Smax) - nelogiška;
            #  paliekama VIENA, leistinoje vietoje kuo arčiau galinės reklamos dalies (kraštinė), tarpas iki kitos gali
            #  būti didesnis už Smax (iki 1,5 Smax); bėgelis > 1500 mm lieka su >= 3 ausėlėmis
            if smax_ and len(ears_) >= 3:
                _e = sorted(ears_, key=lambda q: q["x"])
                _min_n = 3 if (rx1 - rx0) > 1500 else 2
                for _side in ("l", "r"):
                    if len(_e) <= _min_n:
                        break
                    a_, b_, c_ = (_e[0], _e[1], _e[2]) if _side == "l" else (_e[-1], _e[-2], _e[-3])
                    if abs(b_["x"] - a_["x"]) < 0.5 * smax_ and abs(c_["x"] - a_["x"]) <= 1.5 * smax_:
                        _e.remove(b_)
                        print(f"  {g['name']} {'viršus' if is_top else 'apačia'}: gale dvi ausėlės šalia ({abs(b_['x'] - a_['x']):.0f} mm) - "
                              f"paliekama viena prie galo x{a_['x'] - g['lx0']:.0f}, tarpas {abs(c_['x'] - a_['x']):.0f} mm (> Smax leidžiama)")
                ears_ = _e
            xs_e = [e_["x"] for e_ in ears_]
            for i_, x_ in enumerate(xs_e):                    # apkrova ausėlei (pusė tarpų + konsolė)
                lo = rx0 if i_ == 0 else (xs_e[i_ - 1] + x_) / 2
                hi = rx1 if i_ == len(xs_e) - 1 else (x_ + xs_e[i_ + 1]) / 2
                g["ear_max"] = max(g["ear_max"], _LD(lo, hi))
            print(f"  {g['name']} {'viršus' if is_top else 'apačia'} ausėlių apkrovos kN: " + ", ".join(
                f"{_LD(rx0 if i_ == 0 else (xs_e[i_ - 1] + x_) / 2, rx1 if i_ == len(xs_e) - 1 else (x_ + xs_e[i_ + 1]) / 2):.3f}"
                for i_, x_ in enumerate(xs_e)))
            for w_ in warn_:
                print(f"  ! {g['name']} {'viršus' if is_top else 'apačia'}: {w_}")
            g["fp_missing"] += max(0, 2 - len(ears_))
            g["fp_ext"] += sum(e_["ext"] for e_ in ears_)
            for e_ in ears_:
                py_ = base_ if is_top else base_ - e_["h"]
                g["fplates"].append((e_["x"] - es / 2, py_, e_["h"], e_["hy"]))
            g["fp_rows"].append((r_, sorted(e_["x"] for e_ in ears_), is_top))
            print(f"  {g['name']} {'viršus' if is_top else 'apačia'} ausėlės x: "
                  + ", ".join(f"{e_['x'] - g['lx0']:.0f}{'e' if e_['ext'] else ''}" for e_ in sorted(ears_, key=lambda q: q['x']))
                  + f"  (bėgelis {rx0 - g['lx0']:.0f}..{rx1 - g['lx0']:.0f})")
    LET = _LET_ALL
    # v193 (Rytis 2026-10-13, eskizas „Alytus,"): bėgelis, pratęstas iki smulkaus elemento su laikikliu (kablelis), - AUSĖLĖ prie
    #  laikiklio: laisvoje vietoje tarp laikiklio ir rėmo galo (artimiausia laikikliui), bėgelio vidinėje pusėje
    for v_ in [q_ for q_ in g["rails"] if q_.get("ext_holder")]:
        eh_ = v_["ext_holder"]
        for i_, (r_, xs_, t__) in enumerate(g["fp_rows"]):
            if abs((r_["y0"] + r_["y1"]) / 2 - eh_["rail_y"]) > 6:
                continue
            base_ = r_["y1"] if t__ else r_["y0"]
            hy_ = base_ + (es / 2 if t__ else -es / 2)
            md_ = AUS.DEFAULTS["min_edge"]
            if eh_["side"] == "r":
                xs_try = [v_["x0"] - es / 2 - x for x in range(0, 400, 5)]
            else:
                xs_try = [v_["x1"] + es / 2 + x for x in range(0, 400, 5)]
            hit_ = next((x for x in xs_try if AUS._free(LET, x, hy_, md_) is not None), None)
            if hit_ is None:
                print(f"  ! {g['name']}: ausėlei prie elemento laikiklio x{(v_['x0'] + v_['x1']) / 2:.0f} vietos nėra - tikrinti"); continue
            if any(abs(x_ - hit_) < es for x_ in xs_):
                continue
            g["fplates"].append((hit_ - es / 2, base_ if t__ else base_ - es, es, hy_))
            g["fp_rows"][i_] = (r_, sorted(xs_ + [hit_]), t__)
            print(f"  {g['name']}: ausėlė prie elemento laikiklio x{hit_ - g['lx0']:.0f} ({'viršus' if t__ else 'apačia'})")
    # v80 (Rytis 2026-10-10): ausėlė RĖMO GALE - jei ant viršutinio / apatinio bėgelio per 300 mm nuo galo ausėlės nėra
    # (pvz. „A" viršūnė, „L" stiebas užimtas statmens), ausėlė dedama ANT GALINIO STATMENS (kvadratinė es x es plokštelė
    # prie statmens vidinės plokštumos, už raidės stiebo), aukštyje, kur yra laisva vieta už raidės.
    # v83: ausėlė rėmo gale, IŠSIKIŠUSI UŽ RAIDĖS (platus galinis elementas) - kvadratinė es x es plokštelė už raidės krašto
    #  (+ 5 mm), bėgelio aukštyje; pritvirtinta prie galinio statmens / bėgelio galo (jungtis po raide).
    for h_ in hs:
        for sd_ in ("l", "r"):
            ex_ = h_.get("out_" + sd_)
            if ex_ is None:
                continue
            px_ = ex_ - 5 - es if sd_ == "l" else ex_ + 5
            hy_ = (h_["y0"] + h_["y1"]) / 2
            if any(abs(fp[0] - px_) < 1 and abs(fp[3] - hy_) < 1 for fp in g["fplates"]):
                continue
            g["fplates"].append((px_, hy_ - es / 2, es, hy_))
            for i_, (r_, xs_, t__) in enumerate(g["fp_rows"]):
                if r_ is h_ or (abs(r_["y0"] - h_["y0"]) < 1 and abs(r_["x0"] - h_["x0"]) < 1):
                    g["fp_rows"][i_] = (r_, sorted(xs_ + [h_["x0"] if sd_ == "l" else h_["x1"]]), t__)
            print(f"  {g['name']}: ausėlė rėmo gale už raidės x{px_ + es / 2:.0f}, y{hy_:.0f} (platus galinis elementas)")
    for v_ in [r_ for r_ in g["rails"] if r_.get("end")]:
        vx0, vx1 = v_["x0"], v_["x1"]
        for r_, xs_, is_top_ in g["fp_rows"]:                      # kiekvienas bėgelis, kurio galas remiasi į šį statmenį
            if not (v_["y0"] - 1 <= r_["y0"] and r_["y1"] <= v_["y1"] + 1):
                continue
            side_l = abs(r_["x0"] - vx1) < 2
            side_r = abs(r_["x1"] - vx0) < 2
            if not (side_l or side_r):
                continue
            xe_ = r_["x0"] if side_l else r_["x1"]
            if any(abs(x_ - xe_) <= EARS["end_window"] for x_ in xs_):
                continue
            ex = vx1 if side_l else vx0 - es
            yin = (r_["y0"] + r_["y1"]) / 2
            ys_ = sorted(range(int(v_["y0"] + es), int(v_["y1"] - es), 10), key=lambda y: abs(y - yin))   # visas statmuo, arčiausiai bėgelio
            done_ = [fp for fp in g["fplates"] if abs(fp[0] - ex) < 1]
            if any(abs(fp[3] - yin) < abs(yin - y) + 1 for fp in done_ for y in ys_[:1]):
                continue
            hit = next((y for y in ys_ if AUS._free(LET, ex + es / 2, y, AUS.DEFAULTS["min_edge"]) is not None
                        and not any(abs(fp[3] - y) < 100 for fp in done_)), None)
            if hit is not None and any(abs(fp[3] - hit) < 400 for fp in done_):
                continue
            if hit is None:
                print(f"  ! {g['name']}: rėmo galui x{xe_:.0f} (bėgelis y{(r_['y0'] + r_['y1']) / 2:.0f}) ausėlei vietos nei ant bėgelio, nei ant statmens nėra - tikrinti")
                continue
            g["fplates"].append((ex, hit - es / 2, es, hit))
            print(f"  {g['name']}: ausėlė ant galinio statmens x{(vx0 + vx1) / 2:.0f}, y{hit:.0f} (bėgelio y{(r_['y0'] + r_['y1']) / 2:.0f} galas be ausėlės per {EARS['end_window']} mm)")
    print(f"  {g['name']}: H {H_:.0f} mm, qp {qp_:.2f} kN/m², siena {wall_} (N {NR_} kN), ausėlės {len(g['fplates'])}"
          f" ({g['fp_ext']} extended), max {g['ear_max']:.2f} kN/ausėlei, Smax lentelė {smax_ if smax_ else '-'}")
    if g["fplates"] and g["ear_max"] > NR_:
        print(f"  ! {g['name']}: apkrova ausėlei {g['ear_max']:.2f} kN > inkaro {NR_} kN ({wall_}) - tvirtesnis inkaras / papildoma ausėlė (Rytis sprendžia)")
    g["fpl_sz"] = es
    if g.get("_vframe"):
        place_verticals(g, LET_V, es)
    for fr_ in g.get("_vframes", []):
        place_verticals(g, LET_V, es, fr_)

# v297 (Rytis 2026-10-16, EXLANTIX: „E brūkšnelis kabo ore, taip negalima, kiekviena dalis turi tvirtintis prie rėmo"):
#  KIEKVIENA raidės / elemento dalis turi liesti rėmą. Dalis be rėmo -> statmuo per jos vidurį tarp artimiausių bėgelių
#  (viršuje ir apačioje); jei bėgelis tik iš vienos pusės - T forma (v193): statmuo nuo bėgelio per visą dalį (iki krašto - 10).
#  Neišsprendus - lapo klaida (K.SHEET_ERR -> patikra 18 KABO ORE).
def wall_span(g, r_):
    """v300 (Rytis 2026-10-16: „L wall profilis po 50 mm trumpesnis, skaičiuojant tarp rėmo statmenų"): sienos L galai -
    50 mm į vidų nuo kraštinių statmenų AŠIŲ (statmenys per visą rėmo aukštį); be statmenų - nuo bėgelio galų."""
    hs_ = [q for q in g["rails"] if q["kind"] == "h" and not q.get("support")]
    if hs_:
        yt_, yb_ = min(q["y0"] for q in hs_), max(q["y1"] for q in hs_)
        vs_ = [(q["x0"] + q["x1"]) / 2 for q in g["rails"] if q["kind"] == "v" and q["y0"] <= yt_ + 1 and q["y1"] >= yb_ - 1]
        if len(vs_) >= 2:
            return min(vs_) + 50, max(vs_) - 50
    return r_["x0"] + 50, r_["x1"] - 50


def _rail_geom(r_):
    return Polygon(r_["poly"]) if r_.get("poly") else sbox(r_["x0"], r_["y0"], r_["x1"], r_["y1"])


if MOUNTING != "none":
    for g in groups:
        if g["plate"] or not g["rails"]:
            continue
        t_v = float(g["rsz"]["size"].lower().split("x")[0]) if g.get("rsz") else 30.0
        for o in g["letters"]:
            geo_ = o["geom"]
            if any(geo_.intersects(_rail_geom(r_)) for r_ in g["rails"]):
                continue
            xc_ = geo_.representative_point().x
            c_ = geo_.centroid
            if geo_.contains(Point(c_.x, c_.y)):
                xc_ = c_.x
            hs_ = [r_ for r_ in g["rails"] if r_["kind"] == "h" and r_["x0"] - 1 <= xc_ <= r_["x1"] + 1]
            up_ = [r_ for r_ in hs_ if r_["y1"] <= o["bb"][1] + 1]
            dn_ = [r_ for r_ in hs_ if r_["y0"] >= o["bb"][3] - 1]
            a_ = max(up_, key=lambda r_: r_["y1"]) if up_ else None
            b_ = min(dn_, key=lambda r_: r_["y0"]) if dn_ else None
            if a_ and b_:
                y0_, y1_ = a_["y0"], b_["y1"]
            elif a_:
                y0_, y1_ = a_["y0"], o["bb"][3] - 10
            elif b_:
                y0_, y1_ = o["bb"][1] + 10, b_["y1"]
            else:
                msg_ = f"{g['name']}: dalis x{o['bb'][0]:.0f}-{o['bb'][2]:.0f} KABO ORE - nėra bėgelio virš / po ja"
                print("  ! " + msg_); K.SHEET_ERR.append(msg_)
                continue
            x_ = xc_ - t_v / 2
            g["rails"].append({"x0": x_, "x1": x_ + t_v, "y0": y0_, "y1": y1_, "kind": "v", "len": y1_ - y0_, "support": True,
                               "poly": [(x_, y0_), (x_ + t_v, y0_), (x_ + t_v, y1_), (x_, y1_)]})
            print(f"  {g['name']}: dalis x{o['bb'][0]:.0f}-{o['bb'][2]:.0f} be rėmo -> statmuo x{xc_:.0f} L{y1_ - y0_:.0f} (v297)")
            # v299 (Rytis 2026-10-16: „po E reikia dar vieno horizontalaus rėmo, kad vidurinė dalis turėtų 2 taškus ir laido
            #  išvestį"): pailga dalis (plotis >= 2 x aukštis) - horizontalus bėgelis per jos ašį (galai - 10 nuo krašto, v193),
            #  prijungtas prie statmens: >= 2 tvirtinimo taškai + D11 bėgelio ašyje
            bw_, bh_ = o["bb"][2] - o["bb"][0], o["bb"][3] - o["bb"][1]
            if bw_ >= 2 * bh_ and bh_ >= t_v * 0.8:
                yc_ = (o["bb"][1] + o["bb"][3]) / 2
                # v300 (Rytis: „rėmas po E neatitinka rėmo tvirtinimo taisyklės, per ilgas"): galai - kaip auto rėmo (taisyklė:
                #  bėgelio galas kraštinio štricho VIDURYJE = kraštas + pusė štricho storio), abu galo kampai >= 10 mm dalies viduje
                hx0_, hx1_ = o["bb"][0] + bh_ / 2, o["bb"][2] - bh_ / 2
                _in = geo_.buffer(-10)
                for _k in range(60):
                    ok0 = all(_in.contains(Point(hx0_, yy)) for yy in (yc_ - t_v / 2, yc_ + t_v / 2))
                    ok1 = all(_in.contains(Point(hx1_, yy)) for yy in (yc_ - t_v / 2, yc_ + t_v / 2))
                    if ok0 and ok1:
                        break
                    hx0_ += 0 if ok0 else 5
                    hx1_ -= 0 if ok1 else 5
                g["rails"].append({"x0": hx0_, "x1": hx1_, "y0": yc_ - t_v / 2, "y1": yc_ + t_v / 2, "kind": "h", "len": hx1_ - hx0_,
                                   "support": True, "poly": [(hx0_, yc_ - t_v / 2), (hx1_, yc_ - t_v / 2), (hx1_, yc_ + t_v / 2),
                                                             (hx0_, yc_ + t_v / 2)]})
                print(f"  {g['name']}: dalis x{o['bb'][0]:.0f}-{o['bb'][2]:.0f} - + horizontalus bėgelis y{yc_:.0f} L{hx1_ - hx0_:.0f} (v299)")

# v298 (Rytis 2026-10-16: „jei dedasi statmenys, jų turi būti 2 vnt., negali būti vienas - 2 ilgi profiliai, sujungti tik
#  vienu statmeniu, neduoda stabilumo; šituo atveju antras dedasi po I raide gale"): rėmas iš >= 2 horizontalių bėgelių su
#  VIENU statmeniu -> antras statmuo per TIESŲ raidės stiebą (I, L, T, N ...), kuo toliau nuo pirmojo (kitame rėmo gale).
if MOUNTING != "none":
    for g in groups:
        if g["plate"] or not g["rails"]:
            continue
        hs_ = [r_ for r_ in g["rails"] if r_["kind"] == "h"]
        vs_ = [r_ for r_ in g["rails"] if r_["kind"] in ("v", "d")]
        if len(hs_) < 2 or len(vs_) != 1:
            continue
        v0_ = vs_[0]
        t_v = v0_["x1"] - v0_["x0"] if v0_["kind"] == "v" else 30.0
        xv_ = (v0_["x0"] + v0_["x1"]) / 2
        top_ = min(hs_, key=lambda r_: r_["y0"]); bot_ = max(hs_, key=lambda r_: r_["y1"])
        ya_, yb_ = top_["y1"], bot_["y0"]                    # tarpas tarp bėgelių
        # v299 (Rytis 2026-10-16: „statmenas rėmas nuo I dedasi po X, taisyklė - kad kuo mažiau matytųsi"): antras statmuo -
        #  po TOLIAUSIA (kraštine) raide, abiejų bėgelių siekiančia; joje - x, kur raidė uždengia didžiausią statmens dalį
        cands_ = []
        lets_ = [o for o in g["letters"] if o["bb"][1] <= ya_ + 1 and o["bb"][3] >= yb_ - 1]
        if lets_:
            o_far = max(lets_, key=lambda o: abs((o["bb"][0] + o["bb"][2]) / 2 - xv_))
            best_ = None
            xx_ = o_far["bb"][0] + t_v / 2
            while xx_ <= o_far["bb"][2] - t_v / 2:
                strip_ = sbox(xx_ - t_v / 2, ya_, xx_ + t_v / 2, yb_)
                cov_ = o_far["geom"].intersection(strip_).area / max(strip_.area, 1e-9)
                if not best_ or cov_ > best_[0] + 1e-6:
                    best_ = (cov_, xx_)
                xx_ += 5
            if best_:
                cands_.append((best_[1], o_far))
                print(f"  {g['name']}: antras statmuo po kraštine raide, uždengta {best_[0] * 100:.0f} % (v299)")
        if not cands_:
            m_ = f"{g['name']}: rėmas su vienu statmeniu, antram tiesaus stiebo nėra - spręsti ranka"
            print("  ! " + m_); K.SHEET_ERR.append(m_)
            continue
        xc_, o_ = max(cands_, key=lambda c_: abs(c_[0] - xv_))
        x_ = xc_ - t_v / 2
        g["rails"].append({"x0": x_, "x1": x_ + t_v, "y0": top_["y0"], "y1": bot_["y1"], "kind": "v", "len": bot_["y1"] - top_["y0"],
                           "support": True, "poly": [(x_, top_["y0"]), (x_ + t_v, top_["y0"]), (x_ + t_v, bot_["y1"]), (x_, bot_["y1"])]})
        print(f"  {g['name']}: antras statmuo (stabilumas, v298) x{xc_:.0f} per stiebą (raidė x{o_['bb'][0]:.0f}-{o_['bb'][2]:.0f})")

# v85: rėmo eksportas P6 DXF moduliui (p6_dxf.py --rails-json) - tas pats rėmas kaip lape (auto rėmas, pakopos, akcentai)
# v90 (Rytis 2026-10-11): atskiros raidės (mounting "none") - rėmo nėra; apskaičiuoti horizontalūs bėgeliai lieka TIK
#  kaip tvirtinimo skylių ašys DXF moduliui (raidė tvirtinama į fasadą per dugną), lape / BOM / svoryje jų nėra.
SEP_AXES = []
if MOUNTING == "none":
    for g in groups:
        if not g["plate"]:
            SEP_AXES += [r_ for r_ in g["rails"] if r_["kind"] == "h"]
            g["rails"], g["fplates"] = [], []
# kiekiai
GZ = next((g for g in groups if g.get("zfr")), None)
G6 = [g for g in groups if g["spec"]["profile"] == "6"]
G63 = [g for g in groups if g["spec"]["profile"] == "6+3"]
P6, A6 = sum(g["per"] for g in G6), sum(g["area"] for g in G6)
P63, A63 = sum(g["per"] for g in G63), sum(g["area"] for g in G63)
rail_len = [round(r_["len"]) for g in groups if not g["plate"] for r_ in g["rails"]]
prail_len = [round(r_["len"]) for g in groups if g["plate"] for r_ in g["rails"]]
# ---------------- v90: U laikikliai (montavimas be ausėlių)
def _lut(tbl, v):
    return next(n_ for lim_, n_ in tbl if v <= lim_)


BRACKETS = []                                       # {g, x, y0, y1, H, fl, hd, nw, mat}
if MOUNTING == "brackets":
    for g in groups:
        if g["plate"]:
            continue
        hs_ = sorted([r_ for r_ in g["rails"] if r_["kind"] == "h"], key=lambda r_: r_["y0"])
        if len(hs_) < 2:
            print(f"  ! {g['name']}: U laikikliams reikia viršutinio ir apatinio bėgelio - laikikliai nededami")
            continue
        top_, bot_ = hs_[0], hs_[-1]
        fx0, fx1 = max(top_["x0"], bot_["x0"]), min(top_["x1"], bot_["x1"])
        Lf = fx1 - fx0
        Hf = bot_["y1"] - top_["y0"]                  # rėmo aukštis: viršutinio viršus - apatinio apačia
        # v90 (Rytis 2026-10-11): vidinis matmuo = rėmas + 2 (rėmas guli ant apatinės plokštumos, laisvumas įstatyti)
        Hb = Hf + BRK["clear_mm"] + 2 * BRK["thk_mm"]
        n_ = _lut(BRK["n_by_len_mm"], Lf)
        dep_ = float(g["rsz"]["depth"])
        fl_ = dep_ + BRK["flange_add_mm"]
        hd_ = 6 if dep_ <= 30 else 8
        nw_ = _lut(BRK["wall_holes_by_frame_h_mm"], Hf)
        heavy_ = (g["area"] / max(Lf / 1000, 1e-6)) >= BRK["steel_if_area_m2_per_m"]
        _Hl = sorted(o["bb"][3] - o["bb"][1] for o in g["letters"])[len(g["letters"]) // 2]
        large_ = _Hl >= BRK["large_h_mm"]               # v90: didelės raidės - konstrukcija svarbiau už paslėpimą
        mat_ = ("Steel" if heavy_ else "Alu") + f" {BRK['thk_mm']:g} mm"
        LETU = unary_union([o["geom"] for o in g["letters"]])
        # v187 (Rytis 2026-10-13): laikiklių POZICIJOS - ta pati formulė kaip laikiklio tvirtinimo skylių: žingsnis p = L / n,
        #  nuo rėmo galų iki pirmo / paskutinio - p / 2 (pvz. 2 vnt.: L/4, 3L/4). Prie raidžių centrų nebetraukiama.
        tg_ = [fx0 + Lf * (2 * i_ + 1) / (2 * n_) for i_ in range(n_)]
        if large_:
            print(f"  {g['name']}: didelės raidės (H {_Hl:.0f} >= {BRK['large_h_mm']:.0f}) - rekomenduojamas stambesnis rėmas (pvz. 40x40) - Rytis sprendžia")
        for t_x in tg_:
            BRACKETS.append({"g": g, "x": t_x, "y0": top_["y0"] - BRK["clear_mm"] - BRK["thk_mm"], "y1": bot_["y1"] + BRK["thk_mm"],
                             "H": Hb, "Hf": Hf, "fl": fl_, "hd": hd_, "nw": nw_, "mat": mat_, "Lf": Lf, "fx0": fx0})
        print(f"  {g['name']}: U laikikliai {n_} vnt. (rėmas {Lf:.0f} ilgio, {Hf:.0f} aukščio) H {Hb:.0f} x {BRK['width_mm']:.0f}, "
              f"plokštumos {fl_:.0f}, {mat_}, sienoje {nw_} x D{hd_}, plokštumose 2 x D6; x: "
              + ", ".join(f"{b_['x'] - fx0:.0f}" for b_ in BRACKETS if b_["g"] is g)
              + "  [kiekis / skylės / plienas - PASIŪLYMAS, assets/tvirtinimas.json]")
    if BRACKETS and not any("{BRK_" in str(c_) for r_ in spec["bom"] for c_ in r_):
        _pos = max([int(r_[0]) for r_ in spec["bom"] if str(r_[0]).isdigit()] or [0]) + 1
        spec["bom"].append([str(_pos), "Hanger U {BRK_DIM}", "{BRK_MAT}",
                            RAIL_FIN, "{BRK_N} pcs."])
_bk = sorted({(round(b_["H"]), round(b_["fl"]), b_["mat"]) for b_ in BRACKETS})
BRK_SUBS = {"{BRK_N}": str(len(BRACKETS)),
            "{BRK_DIM}": " / ".join(f"{h_}x{BRK['width_mm']:.0f}, fl. {f_}" for h_, f_, _ in _bk),
            "{BRK_MAT}": " / ".join(sorted({m_ for _, _, m_ in _bk})),
            "{BRK_H}": " / ".join(str(h_) for h_, _, _ in _bk)}
# v85 / v101 (Rytis 2026-10-11): rėmas DXF moduliui - bėgeliai, statmenys (įstrižų poligonas), AUSĖLĖS su skyle ir
#  U laikikliai kaip rėmo dalis (3_REMAS)
_RJ = spec.get("rails_json") or os.environ.get("RAILS_JSON")
if _RJ:
    _ears_j = []
    for g in groups:
        if g["plate"]:
            continue
        for fp_ in g.get("fplates", []):
            px_, py_, ph_, hy_ = ear4(g, fp_)
            _ears_j.append({"x0": px_, "y0": py_, "x1": px_ + g["fpl_sz"], "y1": py_ + ph_,
                            "hx": px_ + g["fpl_sz"] / 2, "hy": hy_, "d": EARS.get("hole_d", 6)})
    _brk_j = [{"x0": b_["x"] - BRK["width_mm"] / 2, "x1": b_["x"] + BRK["width_mm"] / 2, "y0": b_["y0"], "y1": b_["y1"],
               "holes": [[b_["x"], b_["y0"] + b_["H"] * (2 * k_ + 1) / (2 * b_["nw"]), b_["hd"]] for k_ in range(b_["nw"])]}
              for b_ in BRACKETS]
    json.dump({"origin_pt": [OX, OY], "scale": S, "separate": MOUNTING == "none",
               "rails": [{"x0": r_["x0"], "y0": r_["y0"], "x1": r_["x1"], "y1": r_["y1"], "kind": r_["kind"],
                          "acc": bool(r_.get("acc")), "end": bool(r_.get("end")),
                          "poly": [list(q_) for q_ in r_["poly"]] if r_["kind"] == "d" else None}
                         for r_ in ([q_ for g in groups if not g["plate"] for q_ in g["rails"]] + SEP_AXES)],
               "ears": [] if MOUNTING == "none" else _ears_j, "brackets": _brk_j},
              open(_RJ, "w"), indent=1)
    print(f"  rėmas eksportuotas DXF moduliui: {_RJ} (ausėlės {len(_ears_j)}, laikikliai {len(_brk_j)})")
# v73: galutinis strypų planas (su tikrais statmenimis) - konsolei ir BOM `{RAIL_BARS}` / `{RAIL_PLAN}`
_bars_by = {}
for g in groups:
    if not g["plate"] and g["rails"]:
        _bars_by.setdefault(g["rsz"]["size"], []).extend(r_["len"] for r_ in g["rails"])
RAIL_BARS, RAIL_PLAN = [], []
for _sz, _ls in (_bars_by.items() if not RAIL_ACR else []):   # v229: akrilinis rėmas - lakštas, ne strypai
    _b = MEDZ.nest_bars(_ls * QTY, STOCK["stock"], STOCK["kerf"], STOCK["end"])
    RAIL_BARS.append(len(_b)); RAIL_PLAN.append(MEDZ.bars_text(_b, STOCK["stock"]))
    print(f"  strypai {_sz} (užsakymui {QTY} vnt.): {MEDZ.bars_text(_b, STOCK['stock'])} | atlieka {MEDZ.bars_waste(_b, STOCK['stock']) / 1000:.2f} m"
          + (f" | {STOCK_NOTE[_sz]}" if _sz in STOCK_NOTE else ""))
    for _L in _ls:
        if _L > STOCK["stock"]:
            _sp = MEDZ.LAST_SPLITS.get(float(_L)) or MEDZ.LAST_SPLITS.get(_L)
            print(f"  ! bėgelis {_L:.0f} mm ilgesnis už strypą {STOCK['stock']:.0f} - jungiamas iš dalių"
                  + (": " + " + ".join(f"{x:.0f}" for x in _sp) if _sp else "") + " (sandūra laisva - parinkta mažiausioms atliekoms)")
_prb = MEDZ.nest_bars(prail_len, STOCK["stock"], STOCK["kerf"], STOCK["end"]) if prail_len else []
SUBS = {"{PER_6}": f"{P6:.2f}", "{A_6}": f"{A6:.2f}", "{RET_6}": f"{P6 * depth / 1000:.2f}",
        "{PER_63}": f"{P63:.2f}", "{A_63}": f"{A63:.2f}", "{RET_63}": f"{P63 * depth / 1000:.2f}",
        "{PER_ALL}": f"{P6 + P63:.2f}", "{RAIL_N}": str(len(rail_len)),
        "{RAIL_LIST}": " + ".join(str(v) for v in rail_len), "{RAIL_TOTAL}": str(sum(rail_len)),
        "{WALL_L_M}": f"{sum(wall_span(g, r_)[1] - wall_span(g, r_)[0] for g in groups if not g['plate'] for r_ in g['rails'] if r_['kind'] == 'h' and not r_.get('support')) / 1000:.2f}",   # v300: tarp statmenų - 2 x 50
        "{RAIL_H_M}": f"{sum(r_['len'] for g in groups if not g['plate'] for r_ in g['rails'] if r_['kind'] == 'h') / 1000:.2f}",   # v297: tik horizontalūs (sienos L)
        "{RAIL_LIST_M}": " + ".join(f"{v / 1000:.2f}" for v in rail_len), "{RAIL_TOTAL_M}": f"{sum(rail_len) / 1000:.2f}",
        **{f"{{PER_{g['name']}}}": f"{g['per']:.2f}" for g in groups},
        **{f"{{A_{g['name']}}}": f"{g['area']:.2f}" for g in groups},
        **{f"{{RET_{g['name']}}}": f"{g['per'] * depth / 1000:.2f}" for g in groups},
        **{f"{{RAILS_{g['name']}}}": " + ".join(str(round(r_["len"])) for r_ in g["rails"]) for g in groups},
        **{f"{{RAILS_M_{g['name']}}}": f"{sum(r_['len'] for r_ in g['rails']) / 1000:.2f}" for g in groups},   # v276: grupės bėgelių m
        "{RAIL_SIZE}": RAIL["size"], "{EAR_HOLE}": f"{EAR_HOLE:.0f}", "{PLATES_N}": str(sum(len(g["fplates"]) for g in groups if not g["plate"])),
        "{RAIL_BARS}": " + ".join(str(v) for v in RAIL_BARS) if RAIL_BARS else "0", "{RAIL_PLAN}": "; ".join(RAIL_PLAN),
        "{BAR_M}": f"{STOCK['stock'] / 1000:g}", "{PRAIL_BARS}": str(len(_prb)),
        "{EAR_CHECK}": " / ".join(f"{g['ear_max']:.2f}" for g in groups if g.get("ear_N")) + " kN max/ear, wall: "
                       + ", ".join(sorted({g["wall"] for g in groups if g.get("wall")})),
        "{WIND_QP}": f"{AUS.wind_qp(**AUS.load_params(spec.get('mount'))['wind']):.2f}",
        "{PLATES_EXT}": str(sum(g.get("fp_ext", 0) for g in groups if not g["plate"])),
        "{EARS_N}": str(sum(len(g["fplates"]) for g in groups if g["plate"])),
        "{PRAIL_SIZE}": (PRAIL or {}).get("size", ""), "{PRAIL_LIST}": " + ".join(str(v) for v in prail_len),
        "{PRAIL_TOTAL}": str(sum(prail_len)), "{PRAIL_TOTAL_M}": f"{sum(prail_len) / 1000:.2f}", "{PW}": f"{PW:.0f}", "{PH}": f"{PH:.0f}", "{A_ALL}": f"{A6 + A63:.2f}",
        "{PLATE_AREA}": " / ".join(f"{g['plate']['geom'].area / 1e6:.2f}" for g in groups if g["plate"]),
        "{PLATE_PER}": " / ".join(f"{g['plate']['geom'].length / 1000:.2f}" for g in groups if g["plate"]),
        **({"{ZP_LEN}": f"{GZ['zfr']['L']:.0f}", "{ZP_TOTAL_M}": f"{2 * GZ['zfr']['L'] / 1000:.2f}",
            "{ZF_LEN}": f"{GZ['zfr']['LF']:.0f}", "{ZF_TOTAL_M}": f"{2 * GZ['zfr']['LF'] / 1000:.2f}",
            "{ZT_LEN}": f"{GZ['zfr']['LT']:.0f}", "{ZT_TOTAL_M}": f"{2 * GZ['zfr']['LT'] / 1000:.2f}",
            "{ZW}": f"{GZ['zfr']['W']:.0f}", "{Z_SIZE}": ZF["z"], "{ZT_SIZE}": ZF["tube"]} if GZ else {}),
        "{PLATE}": " / ".join(f"{(g['plate']['bb'][2] - g['plate']['bb'][0]):.0f}" for g in groups if g["plate"])}


SUBS.update(BRK_SUBS)


def subst(v):
    v = str(v)
    # v90 (Rytis 2026-10-11): BOM - tik bendras rezultatas, be sudėties (ne "1 + 1 + 2 = 4")
    v = re.sub(r"\{(RAIL_LIST_M|RAIL_LIST|PRAIL_LIST|PRAIL_LIST_M|L_LIST_M)\}\s*=\s*", "", v)
    v = v.replace("{RAIL_LIST_M}", "{RAIL_TOTAL_M}").replace("{RAIL_LIST}", "{RAIL_TOTAL}")
    for k_, r_ in SUBS.items():
        v = v.replace(k_, r_)
    return v


# ============================================================ išdėstymas (kaip folded modulyje)
STD = [2, 5, 10, 15, 20, 25, 50, 100]
# Rytis 2026-10-07: apatinės juostos aukštis - pagal eilučių kiekį (BOM / MAIN DATA), kad nebūtų sugrūsta
_nb = len([row for row in spec["bom"] if not (_NO3 and str(row[0]).upper() in ("A", "B"))])
_nm = len(spec["main_data"]) + (0 if any(str(a).lower().startswith("weight") for a, _ in spec["main_data"]) else 1)
K.set_band(max(_nb, _nm))
VX0, VY0 = K.IX0 + 8, K.IY0 + 6
W_AV, H_AV = K.IX1 - K.IX0 - 16, K.VIEW_BOT - K.IY0 - 10
Z_PLATE_L = PZ0 + PLATE["thk"] + PLATE["gap_mm"]       # raidės ant plokštės: šonų galinė briauna nuo sienos
Z_RAIL_L = 0 if MOUNTING == "none" else RAIL["depth"]   # v90: atskiros raidės - tiesiai ant fasado
ZMAX = max([Z_PLATE_L + depth] * bool(G63) + [Z_RAIL_L + depth] * bool(G6)
           + [g["spec"].get("z0", Z_RAIL_L) + g["spec"].get("depth_mm", depth) for g in groups if not g["plate"]])
D_W, D_H = 250, 250
ZSEC = 2                                                   # Z pjūvio mastelis 1:2


def z_box(n):
    if not GZ:
        return (0, 0)
    s_ = MM / n; zr = GZ["zfr"]
    return 26 + zr["W"] * s_ + 52, 24 + zr["LT"] * s_ + 56


NZ = None
if GZ:
    for n_ in (5, 10, 15, 20, 25, 50):
        if GZ["zfr"]["W"] * MM / n_ <= 150:
            NZ = n_; break


def fs_box(n):
    s_ = MM / n; fw_ = PW * s_; fh_ = PH * s_; g_ = max(90, 0.13 * fw_)   # v280 (Rytis: labai sugrusta) priekis - sonas
    return 70 + fw_ + g_ + ZMAX * s_ + 50, 46 + fh_ + 58


def _stack(g):
    """grupės padėtis tarp kitų (galinio vaizdo matmenims): (užstota viršuje, užstota apačioje, tarpas iki žemiau
    esančios grupės mm). Rytis 2026-10-07: grupės viena po kita (pvz. 7-23 po EXTRA)."""
    if g["plate"]:
        return False, False, None
    ov = [h for h in groups if not h["plate"] and h is not g and min(h["x1"], g["x1"]) - max(h["x0"], g["x0"]) > 50]
    below = [h["ly0"] - g["ly1"] for h in ov if h["y0"] >= g["y1"] - 5]
    return (any(h["y1"] <= g["y0"] + 5 for h in ov), bool(below), min(below) if below else None)


def _rail_n(g):
    return len([r_ for r_ in g["rails"] if r_["kind"] == "h"])


def r_box(n):
    s_ = MM / n
    top_x, bot_x = 0, 0
    for g in groups:
        bt, bb, gap = _stack(g)
        if bb and not bt and _rail_n(g) > 1:
            top_x = max(top_x, 20)
        if bt and _rail_n(g) > 1:
            bot_x = max(bot_x, 20)
    _tb = 40 if spec.get("trafo_box") is not False and (spec.get("cable_exits") or spec.get("trafo_box")) else 0
    _lx = (36 + 30) if spec.get("led_fragment") else 0     # v162: virš galinio - žymų eilės, po juo - laidų nuleidimai
    return 70 + PW * s_ + 60, 46 + top_x + PH * s_ + 62 + 34 + bot_x + _tb + _lx


V3 = K.View3D(spec.get("view_yaw", 32), spec.get("view_pitch", 17))
_WM = 0
_ip = [V3.rot(x, y, 0)[:2] for x in (-_WM, PW + _WM) for y in (-_WM * 0.8, PH + _WM * 0.8)]
_ip += [V3.rot(x, y, ZMAX)[:2] for x in (0, PW) for y in (0, PH)]
ISO_EW = max(p[0] for p in _ip) - min(p[0] for p in _ip); ISO_EH = max(p[1] for p in _ip) - min(p[1] for p in _ip)
HAS_D = bool(G63)
LAYS = [[["FS"], ["D", "R", "I"]], [["FS", "D"], ["R", "I"]], [["FS", "I"], ["D", "R"]], [["FS", "R"], ["D", "I"]],
        [["FS", "R", "D"], ["I"]], [["FS", "D", "I"], ["R"]],
        [["FS"], ["R"], ["D", "I"]]]                       # v295 TAISYKLĖ 33: ilga žema iškaba - trys eilės (didesnis mastelis)
if not HAS_D:
    LAYS = [[[b for b in r if b != "D"] for r in lay] for lay in LAYS]
if spec.get("layout") == "rows":                          # v279 (Rytis 2026-10-15): kairėje priekis, dešinėje galas, apačioje DIDELIS 3D
    LAYS = [[["FS", "R"], ["I"]]]
LEDF = spec.get("led_fragment")                            # v162 (Rytis): LED dėliojimas iš originalo - lapo kairė apačia
if LEDF:
    # Rytis 2026-10-13: „kairė viršus - front view / dešinė viršus - rear view / kairė apačia - led / dešinė apačia - 3d view"
    LAYS = [[["FS", "R"], ["L", "I"]]]
    _lc = LEDF["clip"]; LED_ASP = (_lc[2] - _lc[0]) / (_lc[3] - _lc[1])
Z_PREF = None
if GZ:                                                      # Z rėmo detalė - bet kurioje eilutėje
    # Rytis 2026-10-07: WALLFRAME - šalia šoninio vaizdo (tęstinumas), 3D - apačioje didesnis
    Z_PREF = [["FS", "Z"], ["D", "R", "I"]]
    LAYS = [Z_PREF] + [[r + ["Z"] if i == k else r for i, r in enumerate(lay)] for lay in LAYS for k in range(len(lay))]
    D_W = 175                                               # P6+3 schema siauresnė, kad tilptų Z detalė
ISO_MIN_W = 130 if GZ else 170
best = None
for lay, n1, n2, nz, dh in [(l_, a_, b_, c_, d_) for l_ in LAYS for a_ in STD for b_ in STD
                             for c_ in ((10, 15, 20, 25, 50) if GZ else (None,)) for d_ in (250, 220, 190, 170, 150)]:
    if True:
        if True:
            if n2 < n1 or n2 > n1 * 2.5 or (spec.get("layout") == "rows" and n2 != n1):   # rows: priekis = galas
                continue
            if spec.get("view_scale") and n1 != spec["view_scale"]:                      # v279: nurodytas vaizdų mastelis
                continue
            sz = {"FS": fs_box(n1), "R": r_box(n2), "D": (D_W, dh), "Z": z_box(nz) if GZ else (0, 0)}
            if LEDF:
                _r1 = max(sz["FS"][1], sz["R"][1])
                _lh = H_AV - _r1 - 14 - 6
                _lw = min(W_AV * 0.58 - 7, (_lh - 34) * LED_ASP)
                if _lw < 150:
                    continue
                sz["L"] = (_lw, _lw / LED_ASP + 34)
            ok, rows_h, iso = True, [], None
            fixed_h = [max([sz[b][1] for b in r if b != "I"], default=0) for r in lay]
            for ri, r in enumerate(lay):
                ws = sum(sz[b][0] for b in r if b != "I") + 14 * (len(r) - 1)
                if ws > W_AV:
                    ok = False; break
                h_ = fixed_h[ri]
                if "I" in r:
                    if h_ == 0:
                        h_ = H_AV - sum(fixed_h) - 14 * (len(lay) - 1)
                    iso = (W_AV - ws - (14 if len(r) > 1 else 0), h_)
                rows_h.append(h_)
            if not ok or sum(rows_h) + 14 * (len(lay) - 1) > H_AV or not iso or iso[0] < ISO_MIN_W or iso[1] < 140:
                continue
            kk = min(iso[0] / ISO_EW, (iso[1] - 30) / ISO_EH)
            a_iso = kk * kk * ISO_EW * ISO_EH
            # v49 (Joker 1947x208): ilgai siaurai iškabai 3D užima visą lapą, o priekis lieka smulkus - 3D naudingas
            # plotas ribojamas 2 x priekio vaizdo plotu (vaizdai panašaus dydžio)
            a_iso = min(a_iso, (3.5 if spec.get("layout") == "rows" else 2.0) * (PW * MM / n1) * (PH * MM / n1))
            s1, s2 = MM / n1, MM / n2
            a_f, a_r = (PW * s1) * (PH * s1), (PW * s2) * (PH * s2)
            used = sum(sz[b_][0] * sz[b_][1] for r in lay for b_ in r if b_ != "I") + a_iso
            score = 3 * (a_f * a_r * a_iso) ** (1 / 3) + 0.3 * used + (1.0 * a_iso if spec.get("layout") == "rows" else 0) + (3000 if n1 == n2 else 0) + \
                (6 * a_f if GZ else 0)                              # su Z detale - pirmenybė didesniam priekiui
            # galinis vaizdas su rėmo matmenimis turi likti skaitomas: mastelis ne smulkesnis nei 1,5 x priekio
            score -= 60000 if n2 > n1 * 1.5 else 0
            # Rytis 2026-10-07: pirmenybė - galinis vaizdas ne smulkesnis nei 1:50 (rėmo matmenys skaitomi),
            # tada WALLFRAME šalia šoninio (Z_PREF), tada didesnė DETAIL A ir rėmo mastelis
            score += (-1e8 if n2 > 50 else 0) + (3e5 if lay is Z_PREF else 0) + (200 * dh) + (2000 / nz if nz else 0)
            if not best or score > best[0]:
                best = (score, lay, n1, n2, rows_h, sz, iso, nz)
_, LAY, SC1, SC2, ROWS_H, SZ, ISO_CELL, _NZ = best
if GZ:
    NZ = _NZ
POS = {}
vg = (H_AV - sum(ROWS_H)) / (len(LAY) + 1)
yy_ = VY0 + vg
for r, rh_r in zip(LAY, ROWS_H):
    ws = [SZ[b][0] if b != "I" else ISO_CELL[0] for b in r]
    hg = (W_AV - sum(ws)) / (len(r) + 1)
    xx_ = VX0 + hg
    for b, w_ in zip(r, ws):
        h_ = SZ[b][1] if b != "I" else rh_r
        POS[b] = (xx_, yy_ + (rh_r - h_) / 2, w_, h_)
        xx_ += w_ + hg
    yy_ += rh_r + vg
# v276 (Rytis 2026-10-15, Securitas: „kairėje viršuje Front view, po juo rear view, dešinėje padidintas 3D view"):
#  spec "layout": "columns" - kairysis stulpelis FRONT (+ šoninis) / REAR tame pačiame mastelyje, dešinėje - visas aukštis 3D
if spec.get("layout") == "columns" and not HAS_D and not LEDF and not GZ:
    _bestc = None
    for n_ in STD:
        _fs, _rb = fs_box(n_), r_box(n_)
        _lw = max(_fs[0], _rb[0]); _lh = _fs[1] + _rb[1] + 14
        _iw = W_AV - _lw - 14
        if _lh > H_AV + 30 or _iw < 0.30 * W_AV:       # r_box / fs_box paraštės dosnios - iki 30 pt sutraukiama
            continue
        _kk = min(_iw / ISO_EW, (H_AV - 30) / ISO_EH)
        _sc = (PW * MM / n_) * (PH * MM / n_)          # v276 (Rytis: „priekio ir galo didesnės, 3D mažesnė") - didžiausias priekis
        if not _bestc or _sc > _bestc[0]:
            _bestc = (_sc, n_, _fs, _rb, _lw, _iw)
    if _bestc:
        _, SC1, _fs, _rb, _lw, _iw = _bestc
        SC2 = SC1
        LAY = [["FS", "I"], ["R"]]
        _vg = (H_AV - _fs[1] - _rb[1]) / 3
        _lw = max(_lw, 0.56 * W_AV)                     # tolygus lapo užpildymas: kairė sritis ~56 %, vaizdai jos centre
        _iw = W_AV - _lw - 14
        _xl = VX0 + (_lw - _fs[0]) / 2
        # 3D - MAŽESNIS už priekį / galą: projekcijos plotis ~0,85 priekio vaizdo pločio, centre dešinėje
        _k3 = min(0.85 * PW * MM / SC1 / ISO_EW, (_iw - 34) / ISO_EW, (H_AV - 54) / ISO_EH)
        _w3, _h3 = _k3 * ISO_EW + 20, _k3 * ISO_EH + 50
        _x3 = VX0 + _lw + 14 + (_iw - _w3) / 2
        _yf = VY0 + max(_vg, 12)                        # priekio viršutinė matmenų eilė - ne ant lapo rėmo
        _yr = max(_yf + _fs[1] + max(_vg, 0), VY0 + H_AV - _rb[1] + 24) if _vg < 12 else VY0 + 2 * _vg + _fs[1]
        POS = {"FS": (_xl, _yf, _fs[0], _fs[1]),
               "R": (VX0 + (_lw - _rb[0]) / 2, _yr, _rb[0], _rb[1]),
               "I": (_x3, VY0 + (H_AV - _h3) / 2, _w3, _h3)}
if LEDF:                                                   # v167 (Rytis): objektai centruojami savo ketvirtyje, simetriškai
    _hw = W_AV / 2
    for (b1, b2), rh_r in zip(LAY, ROWS_H):
        for b, cx in ((b1, VX0 + _hw / 2), (b2, VX0 + 1.5 * _hw)):
            x_, y_, w_, h_ = POS[b]
            if b == "I":
                w_ = _hw - 10
            POS[b] = (cx - w_ / 2, y_, w_, h_)

# v172 (Rytis: „nuorodų linijos lipa ant skaičių, fono, kitų linijų"): balionai - AUTOMATINIS 2 praėjimų išdėstymas
#  (K.balloon_auto): 1 praėjimas surenka taikinius, `K.auto_place` randa vietą su mažiausiai susikirtimų, 2 - piešia
_AUTO_FILE = os.environ.get("BB_AUTO")
_AUTO = json.load(open(_AUTO_FILE)) if _AUTO_FILE else {}
K.auto_begin("draw", _AUTO["place"]) if _AUTO_FILE else K.auto_begin("collect")
tmp = tempfile.mktemp(suffix=".pdf")
K.init(tmp, spec.get("file_code", "drawing"))
K.frame()
if LEDF:                                                   # v162: originalo LED dėliojimo fragmentas (kiekiai, 230V)
    _lx, _ly, _lw, _lh = POS["L"]
    _fh = _lh - 34
    _lk = _lw / (LEDF["clip"][2] - LEDF["clip"][0])
    if LEDF.get("rules_py"):                              # v176: perbraižoma mūsų stiliumi su LED miniatiūromis
        import importlib.util as _iu, led_mini as _LM
        _sp_ = _iu.spec_from_file_location("led_rules", LEDF["rules_py"]); _LR = _iu.module_from_spec(_sp_)
        _sp_.loader.exec_module(_LR)
        _pn = LEDF.get("pno", 0)
        _LRES = _LM.redraw(K, LEDF["src"], _pn, LEDF["clip"], _lx, _ly, _lk, _LR.RULES[_pn])
        for _x, _y, _ru in getattr(_LR, "LEGEND", {}).get(_pn, []):
            _LM.legend_icon(K, _lx + (_x - LEDF["clip"][0]) * _lk, _ly + (_y - LEDF["clip"][1]) * _lk, _ru, _lk, 1.6)
        LED_BALLOONS = [(_lx + (_x - LEDF["clip"][0]) * _lk, _ly + (_y - LEDF["clip"][1]) * _lk, _n)
                        for _x, _y, _n in getattr(_LR, "BALLOONS", {}).get(_pn, [])]
        print(f"  LED (originalas, perbraižyta): {len(_LRES['modules'])} moduliai, PSU {len(_LRES['psu'])}")
    else:
        LED_BALLOONS = []
        K.place_pdf(LEDF["src"], LEDF.get("pno", 0), LEDF["clip"], (_lx, K.H - _ly), (_lx + _lw, K.H - _ly),
                    (_lx, K.H - _ly - _fh), outline=0, under=True)
    if LEDF.get("texts"):                                  # v171: originalo užrašai GOST (gost_frag.draw)
        import gost_frag as _GF
        _GF.draw(K, LEDF["clip"], _lx, _ly, _lk, LEDF["texts"])
    VIEW_BOX_L = (_lx, _ly, _lx + _lw, _ly + _fh)
    view_title(_lx + _lw / 2, _ly + _fh + 22, "LED INSTALLATION", LEDF.get("note", "as original drawing"))
    json.dump({"clip": list(LEDF["clip"]), "X0": _lx, "Ytop": _ly, "k": _lw / (LEDF["clip"][2] - LEDF["clip"][0])},
              open(OUT + ".ledfrag.json", "w"))                   # v167: GOST tekstų overlay (gost_frag.py)

RAILC = HexColor("#CFE6F5") if RAIL_ACR else HexColor(K.ralhex(RAIL["ral"]))   # v229: akrilas - skaidrus (šviesiai melsvas)
ZPC, ZFC = HexColor("#C4C7CA"), HexColor("#8E9295")      # Z ant plokštės (Alu natūralus) / sieninis rėmas
PLATEC = HexColor(K.ralhex(PLATE["ral"]))


def facecol(g):
    return HexColor(g["spec"].get("face_hex")) if g["spec"].get("face_hex") else \
        __import__("reportlab.lib.colors", fromlist=["Color"]).Color(*g["letters"][0]["fill"])


def retcol(g):
    if g["spec"].get("return_hex"):                      # v249: nedažyti šviečiantys šonai (P10 balta plexi)
        return HexColor(g["spec"]["return_hex"])
    return HexColor(K.ralhex(g["spec"]["return_ral"]))


PVC_RAW = HexColor("#E9E9E6")                     # v186: nedažytas PVC (P1 dugnas)


def backcol(g):
    """v186 (Rytis 2026-10-13): galinis vaizdas - DUGNO spalva. P1 dugnas PVC 10 mm nedažytas (back_ral - tik nurodžius)"""
    br_ = g["spec"].get("back_ral") or spec.get("back_ral")
    if br_:
        return HexColor(K.ralhex(br_))
    return PVC_RAW if FRONT == "P1" else retcol(g)


def gfront(g):
    """v276 (Rytis 2026-10-15, Securitas): grupės priekis - `groups[i].front` (pvz. apskritimai P6 color, raidės 5S+foil
    VIENOJE iškaboje), kitaip bendras spec `front`"""
    return g["spec"].get("front") or spec.get("front", "5S+foil")


def rcol(g):
    """v276: grupės bėgelių spalva - `groups[i].rail_ral` (RAL / NCS / kodas), kitaip bendra RAIL ral"""
    c_ = g["spec"].get("rail_ral")
    if c_ and not RAIL_ACR:
        h_ = K.code_hex(c_) or (K.ralhex(c_) if K.ralhex(c_) != "#888888" else None)
        if h_:
            return HexColor(h_)
    return RAILC


def P6_REAL(g):
    """v59: realus P6 vaizdavimas (stiklas 3 mm kraštas, korpusas -1,5) - visoms šviečiančioms P6 / P6+3 raidėms"""
    return FRONT not in ("P1", "P10") and not g["spec"].get("behind") and g["spec"].get("lit", True) is not False \
        and g["spec"].get("depth_mm", depth) >= 20


def extreme(geom, which, near=None):
    """kraštinis taškas; v276 (ISO, Rytis „linija ant linijos"): plokščiame krašte (keli taškai ±0,5 mm) imamas taškas,
    ARČIAUSIAI matmens eilės (near: "l" / "r" / "t" / "b"; numatyta - miny/maxy -> kairė, minx -> viršus, maxx -> viršus),
    kad iškeltinė nebėgtų išilgai raidės krašto (linija ant linijos)."""
    pts = [q for gg in getattr(geom, "geoms", [geom]) for q in gg.exterior.coords]
    f = {"minx": lambda p: p[0], "maxx": lambda p: -p[0], "miny": lambda p: p[1], "maxy": lambda p: -p[1]}[which]
    v0 = f(min(pts, key=f))
    cand = [q for q in pts if f(q) - v0 <= 0.5]
    near = near or ("l" if which in ("miny", "maxy") else "t")
    g_ = {"l": lambda p: p[0], "r": lambda p: -p[0], "t": lambda p: p[1], "b": lambda p: -p[1]}[near]
    return min(cand, key=g_)


ALL_G = unary_union([g["geom"] for g in groups] + [g["plate"]["geom"] for g in groups if g["plate"]])

# ============================================================ FRONT VIEW
K.set_view(True)
s1 = MM / SC1
fw, fh = PW * s1, PH * s1
FVX, FVY = POS["FS"][0] + 70, POS["FS"][1] + 50


def FV(x, y):
    return FVX + x * s1, FVY + y * s1


for g in groups:
    for fp_ in g["fplates"]:                            # ausėlės: hairline + skylė (matoma plokštuma)
        px_, py_, ph_, hy_ = ear4(g, fp_)
        rect(FVX + px_ * s1, FVY + py_ * s1, g["fpl_sz"] * s1, ph_ * s1, fill=K.mix(rcol(g), 0.85), lw=K.HAIR)
        hc_ = FV(px_ + g["fpl_sz"] / 2, hy_)
        K.c.saveState(); K.c.setFillColor(white); K.c.setLineWidth(K.HAIR)
        K.c.circle(hc_[0], K.Y(hc_[1]), max(0.5, EARS.get("hole_d", 6) / 2 * s1), stroke=1, fill=1); K.c.restoreState()
    for r_ in g["rails"]:
        poly([FV(*q) for q in r_["poly"]], fill=rcol(g), lw=0.4)
def _front_decals(gname):
    for d_, dc_ in DECALS_RAW:                           # v11: lipdukai priekyje (v13: iškart po savo grupe)
        if dc_.get("group") == gname or (gname is None and not any(g2["name"] == dc_.get("group") for g2 in groups)):
            K.draw_shape(K.drawing_to_subpaths(d_, tomm), lambda x, y: (FVX + x * s1, K.Y(FVY + y * s1)),
                         fill=HexColor(dc_["hex"]), stroke=black)


for g in sorted(groups, key=lambda g: not g["spec"].get("behind")):     # v10: "behind" grupė - po raidėmis
    if g["plate"]:
        K.draw_shape(g["plate"]["sub"], lambda x, y: (FVX + x * s1, K.Y(FVY + y * s1)), fill=PLATEC, stroke=black)
    for o in g["letters"]:
        K.draw_shape(o["sub"], lambda x, y: (FVX + x * s1, K.Y(FVY + y * s1)), fill=facecol(g), stroke=black)
    _front_decals(g["name"])
_front_decals(None)
for g in groups:
    zr = g.get("zfr")
    if zr:                                              # Z juostos už plokštės - nematomos, punktyru
        for yy in (zr["yA"], zr["yB"]):
            a_, b_ = FV(zr["sx0"], yy), FV(zr["sx1"], yy + ZF["zf"])
            rect(a_[0], a_[1], b_[0] - a_[0], b_[1] - a_[1], stroke=HexColor("#333333"), lw=0.3, dash=(2, 1.2))
K.set_view(False)


def chain_marks(pairs):
    """pairs: (mm reikšmė, objekto taškas mm) -> surūšiuoti, be dublikatų"""
    out = []
    for v, p in sorted(pairs, key=lambda t: t[0]):
        if out and abs(v - out[-1][0]) < 1.5:
            continue
        out.append((v, p))
    return out


top_gs = [g for g in groups if (g["y0"] + g["y1"]) / 2 < PH / 2]
bot_gs = [g for g in groups if (g["y0"] + g["y1"]) / 2 >= PH / 2] + [g for g in groups if g["plate"]]
pmin, pmax = extreme(ALL_G, "minx"), extreme(ALL_G, "maxx")
# viršus: bendras plotis + grupių pločiai
hdim(FVX, FVX + fw, FVY - 44, f"{PW:.0f}", FV(*pmin)[1], FV(*pmax)[1], size=K.F_DIM_MAIN)
pr = [(0, pmin), (PW, pmax)]
for g in top_gs:
    gg = unary_union([g["geom"]] + ([g["plate"]["geom"]] if g["plate"] else []))
    pr += [(g["x0"], extreme(gg, "minx")), (g["x1"], extreme(gg, "maxx"))]
m = chain_marks(pr)
if len(m) > 2:                                   # grandinė, kartojanti bendrą matmenį, nededama
    hchain(FVY - 20, [FV(v, 0)[0] for v, _ in m], [FV(*p)[1] for _, p in m],
           [f"{round(b[0]) - round(a[0])}" for a, b in zip(m[:-1], m[1:])], K.F_DIM_MAIN)
# apačia: plokštės raidė + apatinės grupės
pr = [(0, pmin), (PW, pmax)]
for g in bot_gs:
    pr += [(g["lx0"], extreme(g["geom"], "minx", "b")), (g["lx1"], extreme(g["geom"], "maxx", "b"))]
    if g["plate"]:
        pr += [(g["x0"], extreme(g["plate"]["geom"], "minx", "b")), (g["x1"], extreme(g["plate"]["geom"], "maxx", "b"))]
m = chain_marks(pr)
yb = FVY + fh + 20
if len(m) > 2:                                   # v172: išvadinės nuo objekto -> hchain žino kryptį (maži tarpai - toliau nuo objekto)
  hchain(yb, [FV(v, 0)[0] for v, _ in m], [FV(*p)[1] for _, p in m], [f"{round(b[0]) - round(a[0])}" for a, b in zip(m[:-1], m[1:])], K.F_DIM_MAIN)
# kairė: plokštės grupė (plokštė, raidė) + bendras aukštis
pmn_y, pmx_y = extreme(ALL_G, "miny"), extreme(ALL_G, "maxy")
pr = [(0, pmn_y), (PH, pmx_y)]
for g in groups:
    if g["plate"]:
        pr += [(g["y0"], extreme(g["plate"]["geom"], "miny")), (g["y1"], extreme(g["plate"]["geom"], "maxy")),
               (g["ly0"], extreme(g["geom"], "miny")), (g["ly1"], extreme(g["geom"], "maxy"))]
if not any(g["plate"] for g in groups):          # be plokštės: kairiausios grupės raidžių viršai / apačios
    gl = min(groups, key=lambda g: g["lx0"])
    _h = sorted(o["bb"][3] - o["bb"][1] for o in gl["letters"]); _hm = _h[len(_h) // 2]
    lv = [(gl["ly0"], extreme(gl["geom"], "miny"), 0), (gl["ly1"], extreme(gl["geom"], "maxy"), 0)]
    for o in gl["letters"]:
        if o["bb"][3] - o["bb"][1] < 0.5 * _hm:      # i taškai, brūkšniai - tik gabaritas
            continue
        lv += [(o["bb"][1], extreme(o["geom"], "miny"), o["geom"].area),
               (o["bb"][3], extreme(o["geom"], "maxy"), o["geom"].area)]
    lv.sort(key=lambda q: q[0])
    cl = []                                       # klasteriai 20 mm; atstovas - didžiausios raidės kraštas
    for q in lv:
        if cl and q[0] - cl[-1][0][0] <= 20:
            cl[-1].append(q)
        else:
            cl.append([q])
    # Rytis 2026-10-07 (Clas Ohlson): kelios teksto eilutės + logotipas -> kairė grandinė pagal EILUTES
    #  (eilutės viršus / apačia), logotipas (> 1,3 x mediana) ir i taškai neįskaičiuojami
    _big = [o for o in gl["letters"] if 0.5 * _hm <= o["bb"][3] - o["bb"][1] <= 1.3 * _hm]
    _rows = []
    for o in sorted(_big, key=lambda o: o["bb"][1]):
        if _rows and o["bb"][1] < _rows[-1][1] - 0.3 * _hm:
            _rows[-1][0].append(o); _rows[-1][1] = max(_rows[-1][1], o["bb"][3])
        else:
            _rows.append([[o], o["bb"][3]])
    if len(_rows) >= 2:
        pr = [(0, pmn_y), (PH, pmx_y)]
        for r_o, _ in _rows:
            top_ = min(r_o, key=lambda o: o["bb"][1]); bot_ = max(r_o, key=lambda o: o["bb"][3])
            pr += [(top_["bb"][1], extreme(top_["geom"], "miny")), (bot_["bb"][3], extreme(bot_["geom"], "maxy"))]
    else:
        pr += [(rep[0], rep[1]) for rep in (max(c_, key=lambda q: q[2]) for c_ in cl)]
m = chain_marks(pr)


def first_hit(p, side="l"):
    """v276 (ISO 129-1 / cad_matmenavimas_ISO.md 5 sk.): iškeltinė baigiasi PIRMAME objekte nuo matmens eilės pusės
    (ne toliau esančios raidės taške - kitaip bėga per / išilgai kitų raidžių kraštų = linija ant linijos)."""
    from shapely.geometry import box as _box
    y = p[1]
    tol = 1.0 / s1                                    # ±1 pt juosta - lėkšti kreivių viršai irgi „pataikomi"
    hit = ALL_G.intersection(_box(-1e5, y - tol, 1e5, y + tol))
    if not hit.is_empty:
        b_ = hit.bounds
        return (b_[0] if side == "l" else b_[2], y)
    return p


if len(m) > 2:
    vchain(FVX - 24, [FV(0, v)[1] for v, _ in m], [FV(*first_hit(p))[0] for _, p in m],
           [f"{round(b[0]) - round(a[0])}" for a, b in zip(m[:-1], m[1:])], K.F_DIM_MAIN)
vchain(FVX - 48, [FVY, FVY + fh], [FV(*first_hit(pmn_y))[0], FV(*first_hit(pmx_y))[0]], [f"{PH:.0f}"], K.F_DIM_MAIN)
# dešinė: grupės ant bėgelių
pr = [(0, pmn_y)]
for g in groups:
    if not g["plate"]:
        pr += [(g["ly0"], extreme(g["geom"], "maxx")), (g["ly1"], extreme(g["geom"], "maxx"))]
m = chain_marks(pr)
if len(m) > 2:
  vchain(FVX + fw + 20, [FV(0, v)[1] for v, _ in m], [FV(*first_hit(p, "r"))[0] for _, p in m],
         [f"{round(b[0]) - round(a[0])}" for a, b in zip(m[:-1], m[1:])], K.F_DIM_MAIN)
# profilių žymos
for g in groups:
    o = max(g["letters"], key=lambda o_: o_["geom"].area)
    cp = o["geom"].representative_point()
    tx = FV(g["lx0"], g["ly1"])[0]
    T(FV(g["x0"], 0)[0], FV(0, g["y1"])[1] + 9 if not g["plate"] else FV(0, g["y1"])[1] + 9, "", 6)
# v13 (Rytis 2026-10-08): rėmo sujungimo vieta - punktyrinė linija per visą aukštį + užrašas
JOINTS = [((j_["x_pt"] - OX) * S if "x_pt" in j_ else j_["x_mm"], j_.get("label", "FRAME JOINT")) for j_ in spec.get("joints", [])]


def _joint(x_, y0_, y1_, lab_):
    line(x_, y0_, x_, y1_, 0.5, black, dash=([6, 2, 1.5, 2], 0))
    K._Tbg(x_ + 3, (y0_ + y1_) / 2, lab_, 8, align="c", rot=90, font="FB", auto_red=False)


for xj_, lj_ in JOINTS:
    _joint(FV(xj_, 0)[0], FVY - 8, FVY + fh + 8, lj_)


def _callouts(view, F):
    """v13: BOM pozicijų balionai vaizde - spec callouts.<view> = [[x_mm, y_mm, poz, dx_pt, dy_pt]] (priekio koord.)"""
    for co_ in spec.get("callouts", {}).get(view, []):
        x_, y_ = F(co_[0], co_[1])
        K.balloon_auto(x_, y_, co_[2], avoid=[VIEW_BOX[view]])   # v176 (Rytis): balionai TIK už vaizdo ribų


VIEW_BOX = {"front": (FVX, FVY, FVX + fw, FVY + fh)}
_callouts("front", FV)
view_title(FVX + fw / 2, FVY + fh + 52, "FRONT VIEW", f"SCALE 1:{SC1}")

# ============================================================ SIDE VIEW (RIGHT)
GAPV = max(90, 0.13 * fw)                                   # v280: = fs_box tarpas
SVW = FVX + fw + GAPV + ZMAX * s1          # sienos plokštuma


def SZx(z):
    return SVW - z * s1


K.set_view(True)
order = sorted(groups, key=lambda g: g["x0"])
for g in order:
    for r_ in g["rails"]:
        rd_ = g["rsz"]["depth"]
        if r_["kind"] == "h":                           # v47: horizontalus - matomas PJŪVIS: U (anga į sieną) arba □
            K.rail_section(SZx(rd_), FVY + r_["y0"] * s1, rd_ * s1, (r_["y1"] - r_["y0"]) * s1,
                           max(_rail_t(g["rsz"]) * s1, 0.7), "sq" if RAIL_SQ else "u", "right", fill=rcol(g))
        else:
            rect(SZx(rd_), FVY + r_["y0"] * s1, rd_ * s1, (r_["y1"] - r_["y0"]) * s1, fill=rcol(g), lw=0.4)
    if g["plate"]:
        rect(SZx(PZ0 + PLATE["thk"]), FVY + g["y0"] * s1, PLATE["thk"] * s1, (g["y1"] - g["y0"]) * s1, fill=PLATEC, lw=0.5)
        zr = g.get("zfr")
        if zr:                                          # sieninis rėmas + Z juostos (pjūvio kontūras galuose)
            rect(SZx(ZF["tb"]), FVY + zr["fy0"] * s1, ZF["tb"] * s1, zr["LT"] * s1, fill=ZFC, lw=0.4)
            for yy in (zr["yA"], zr["yB"]):
                for fr_, col_ in ((True, ZFC), (False, ZPC)):
                    poly([(SZx(ZF["zw"] - d), FVY + y * s1) for d, y in zsection(yy, fr_)], fill=col_, lw=0.4)
        z0 = Z_PLATE_L
    else:
        z0 = g["spec"].get("z0", Z_RAIL_L)                      # v11: grupės z (pvz. P00 apskritimas, tiesiai ant sienos)
    ivs = sorted((o["bb"][1], o["bb"][3]) for o in g["letters"])
    mg = []
    for a_, b_ in ivs:
        if mg and a_ <= mg[-1][1] + 0.5:
            mg[-1][1] = max(mg[-1][1], b_)
        else:
            mg.append([a_, b_])
    gd_ = g["spec"].get("depth_mm", depth)                       # v10: grupės gylis (pvz. P00 3 mm)
    for a_, b_ in mg:
        if P6_REAL(g):                                   # v59: korpusas -1,5 | stiklo kraštas 3 | plėvelė
            PV.side_view(SZx(z0), FVY + a_ * s1, s1, a_, b_, gd_, K.mix(retcol(g), 0.9), facecol(g),
                         front=gfront(g))
            continue
        rect(SZx(z0 + gd_), FVY + a_ * s1, gd_ * s1, (b_ - a_) * s1, fill=K.mix(retcol(g), 0.9), lw=0.5)
        rect(SZx(z0 + gd_), FVY + a_ * s1, 0.9, (b_ - a_) * s1, fill=facecol(g) if (g["spec"].get("behind") or FRONT == "P1") else white, lw=0.4)
K.set_view(False)
gp = next((g for g in groups if g["plate"]), None)
grr = next((g for g in groups if not g["plate"]), None)
if gp:
    yt_ = FVY + gp["ly0"] * s1
    zz = [0, Z_PLATE_L, Z_PLATE_L + depth]
    parts = ([f"{PZ0:.0f}"] if PZ0 else []) + [f"{PLATE['thk']:.0f}"] + ([f"{PLATE['gap_mm']:.0f}"] if PLATE["gap_mm"] else [])
    hchain(FVY - 20, [SZx(z) for z in reversed(zz)], [yt_] * 3,
           [f"{depth:.0f}", f"{Z_PLATE_L:.0f} ({'+'.join(parts)})"], K.F_DIM_MAIN)
if grr:
    yb_ = FVY + max(g_["ly1"] for g_ in groups if not g_["plate"]) * s1   # v276: iškeltinė nuo ŽEMIAUSIOS grupės (ne per kitą)
    if Z_RAIL_L:
        zz = [0, Z_RAIL_L, Z_RAIL_L + depth]
        hchain(FVY + fh + 18, [SZx(z) for z in reversed(zz)], [yb_] * 3, [f"{depth:.0f}", f"{RAIL['depth']:.0f}"], K.F_DIM_MAIN)
    else:                                           # v90: be rėmo - tik raidės gylis
        hchain(FVY + fh + 18, [SZx(depth), SZx(0)], [yb_] * 2, [f"{depth:.0f}"], K.F_DIM_MAIN)
if gp:   # detalės A žyma ant X raidės šoninio vaizdo
    zc = (Z_PLATE_L + PZ0 + PLATE["thk"]) / 2
    K.c.saveState(); K.c.setLineWidth(0.4); K.c.setDash(3, 1.5)
    K.c.circle(SZx(zc), K.Y(FVY + gp["ly0"] * s1 + 10), 11); K.c.restoreState()
    T(SZx(zc) - 15, FVY + gp["ly0"] * s1 + 2, "A", 9, font="FB", align="c")
stw = K.pdfmetrics.stringWidth("SIDE VIEW (RIGHT)", "FB", K.F_VIEW)
view_title((SZx(ZMAX) + SVW) / 2, FVY + fh + 52, "SIDE VIEW (RIGHT)", f"SCALE 1:{SC1}")

CABLES = [{"x": (c_["pt"][0] - OX) * S, "y": (c_["pt"][1] - OY) * S, "label": c_.get("label", ""),
           "voltage": c_.get("voltage", "?"), "point": c_.get("point", False), "up_mm": c_.get("up_mm"), "side": c_.get("side")}
          for c_ in CABLES_RAW]
# ============================================================ v229: AKRILINIS RĖMAS (Leapmotor) - dalys, puzzle jungtys, Ø8, grioveliai
ACR_GEO = {}
if RAIL_ACR:
    from shapely.geometry import Polygon as _APoly, box as _abox, Point as _APt, LineString as _ALn
    from shapely.ops import unary_union as _aun
    _cl, _hd = float(ACRY["joint_clear"]), float(ACRY["hole_d"])
    _smax = float(max(ACRY["sheet"])) - 30                     # dalies ilgis su atsarga pjovimui
    for g in groups:
        if g["plate"] or not g["rails"]:
            continue
        hs_ = sorted([r_ for r_ in g["rails"] if r_["kind"] == "h"], key=lambda r_: r_["y0"])
        vs_ = [r_ for r_ in g["rails"] if r_["kind"] != "h"]
        F = _aun([_APoly(r_["poly"]) for r_ in g["rails"]]).buffer(0)
        # v232 (Rytis 2026-10-14): statmenys / įstrižai - ATSKIROS detalės (taupoma medžiaga), į bėgelius jungiami puzzle
        FH = _aun([_APoly(r_["poly"]) for r_ in hs_]).buffer(0)
        vparts, vknobs, vjoints = [], [], []
        for v_ in vs_:
            pq = v_["poly"]
            VP = _APoly(pq).buffer(0)
            ends_ = [(((pq[0][0] + pq[1][0]) / 2, pq[0][1]), pq[2][1]), (((pq[2][0] + pq[3][0]) / 2, pq[2][1]), pq[0][1])]
            wv_ = min(math.hypot(pq[1][0] - pq[0][0], pq[1][1] - pq[0][1]), RAIL_W)
            hr_, nk_ = 0.2 * wv_, 0.12 * wv_
            kn_ = []
            for (ex_, ey_), oy_ in ends_:
                sg_ = -1 if ey_ < oy_ else 1                   # į bėgelį (nuo statmens vidaus)
                vjoints.append((ex_, ey_, sg_, wv_, abs(pq[0][0] - pq[3][0]) > 1))
                kn_.append(_aun([_abox(ex_ - nk_, min(ey_ - sg_, ey_ + sg_ * hr_ * 1.2), ex_ + nk_, max(ey_ - sg_, ey_ + sg_ * hr_ * 1.2)),
                                 _APt(ex_, ey_ + sg_ * hr_ * 1.6).buffer(hr_, 24)]))
            vparts.append(_aun([VP] + kn_).buffer(0)); vknobs += kn_
        LETG = unary_union([o["geom"] for o in g["letters"]])
        X0, _, X1, _ = F.bounds
        # pjūvio vietos: dalys <= lakšto ilgis; pjūvis KUO LABIAU PO RAIDĖMIS (abiejų bėgelių juosta ±30 raidėje),
        #  >= 60 mm nuo statmenų / įstrižų
        cuts, start = [], X0
        while X1 - start > _smax:
            lo_, hi_ = max(start + 300, X1 - _smax * (math.ceil((X1 - start) / _smax) - 1)), start + _smax
            best = None
            for k_ in range(int(lo_), int(hi_) + 1, 2):
                if any(min(abs(k_ - v_["x0"]), abs(k_ - v_["x1"])) < 60 for v_ in vs_):
                    continue
                cov = sum(LETG.intersection(_abox(k_ - 30, r_["y0"], k_ + 30, r_["y1"])).area for r_ in hs_) / (60 * sum(r_["y1"] - r_["y0"] for r_ in hs_))
                sc_ = (cov, -abs(k_ - (lo_ + hi_) / 2))
                if best is None or sc_ > best[0]:
                    best = (sc_, k_)
            x_ = best[1] if best else (lo_ + hi_) / 2
            cuts.append({"x": x_, "under": best[0][0] if best else 0.0})
            start = x_
        # puzzle: kiekvienam bėgeliui ant pjūvio - galvutė Ø0.5w ant kaklelio 0.3w; galvutė - kairės dalies, įlenda į dešinę
        #  (dešinėje dalyje - išpjova su laisvumu joint_clear)
        parts_b = [X0 - 1] + [c_["x"] for c_ in cuts] + [X1 + 1]
        kn_by = []
        knobs = []
        for c_ in cuts:
            kk = []
            for r_ in hs_:
                w_ = r_["y1"] - r_["y0"]; cy_ = (r_["y0"] + r_["y1"]) / 2
                hr_, nk_ = 0.25 * w_, 0.15 * w_
                kk.append(_aun([_abox(c_["x"] - 1, cy_ - nk_, c_["x"] + hr_ * 1.2, cy_ + nk_),
                                _APt(c_["x"] + hr_ * 1.6, cy_).buffer(hr_, 24)]))
            kn_by.append(_aun(kk)); knobs += kk
        parts = []
        for i in range(len(parts_b) - 1):
            P_ = FH.intersection(_abox(parts_b[i], -1e5, parts_b[i + 1], 1e5))
            if i < len(cuts):                                  # dešinysis pjūvis - galvutė prie šios dalies
                P_ = _aun([P_, kn_by[i]])
            if i > 0:                                          # kairysis pjūvis - išpjova galvutei
                P_ = P_.difference(kn_by[i - 1].buffer(_cl, 24))
            if vknobs:
                P_ = P_.difference(_aun(vknobs).buffer(_cl, 24))
            parts.append(P_.buffer(0))
        # Ø8 skylės - tarpuose tarp raidžių ant horizontalių bėgelių, kas antrame tarpe (Rytis: dvigubai mažiau)
        xs_ = sorted((o["bb"][0], o["bb"][2]) for o in g["letters"])
        gaps_, cur_ = [], None
        for a_, b_ in xs_:
            if cur_ is not None and a_ - cur_ > 2 * _hd + 10:
                gaps_.append((cur_ + a_) / 2)
            cur_ = b_ if cur_ is None else max(cur_, b_)
        gaps_ = gaps_[::max(1, int(ACRY["holes_every_gap"]))]
        holes = []
        for r_ in hs_:
            cy_ = (r_["y0"] + r_["y1"]) / 2
            for gx_ in gaps_:
                if r_["x0"] + 20 < gx_ < r_["x1"] - 20 and all(abs(gx_ - c_["x"]) > 40 for c_ in cuts) \
                        and not LETG.intersects(_APt(gx_, cy_).buffer(_hd / 2 + 2)):
                    holes.append((gx_, cy_))
        # v244 (Rytis 2026-10-15: „raidės tvirtinasi tik ant vieno varžto - negerai, logotipo dalis net neturi tvirtinimo"):
        #  KIEKVIENA raidė / dalis - >= 2 smeigės (ilgoms - kas ~400), bet kur bėgelio juostoje (ne tik ašyje), toliausiai
        #  viena nuo kitos; ne laidų griovelio zonoje, ne prie jungčių / Ø8 / statmenų galvučių
        ST = ACRY["stud"]
        _gw_ = float((ACRY.get("groove") or {}).get("w", 6) or 6)
        g_off = ST["cb_d"] / 2 + _gw_ / 2 + 2
        _vl = [(((v_["poly"][0][0] + v_["poly"][1][0]) / 2), v_["poly"][0][1], v_["poly"][2][1]) for v_ in vs_
               if abs(v_["poly"][0][0] - v_["poly"][3][0]) < 1]                    # tik statmenys (ne įstrižai)
        studs, STUD_FAIL = _acr_studs(g["letters"], hs_, ST, g_off, _gw_, cuts, holes, vjoints, vlines=_vl)
        if os.environ.get("STUD_DEBUG"):
            for o in g["letters"]:
                print(f"    smeigės x{o['bb'][0]:.0f}-{o['bb'][2]:.0f}: " + ", ".join(f"({x_:.0f},{y_:.0f})" for x_, y_, i_ in studs if i_ == id(o)))
        for nm_ in STUD_FAIL:
            print(f"  ! akrilinis rėmas {g['name']}: dalis {nm_} - mažiau nei 2 smeigės (bėgelis per siauras / nepasiekia) - PATIKRINTI")
        # laidų griovelis - nugaroje, bėgeliuose PASLINKTAS nuo ašies (įleistos skylės Ø12 ašyje), statmenyse - ašyje
        grooves = [((r_["x0"] + 10, (r_["y0"] + r_["y1"]) / 2 - g_off), (r_["x1"] - 10, (r_["y0"] + r_["y1"]) / 2 - g_off)) for r_ in hs_]
        # ovali skylė kiaurai laidui - po kiekviena raide ant viršutinio bėgelio griovelio
        slots = []
        CS = ACRY.get("cable_slot") or [_gw_, _gw_ / 2]
        r0_ = hs_[0] if hs_ else None
        for o in (g["letters"] if r0_ else []):
            gy_ = (r0_["y0"] + r0_["y1"]) / 2 - g_off
            inn = o["geom"].buffer(-(CS[0] / 2 + 3))
            seg = inn.intersection(_ALn([(o["bb"][0] - 1, gy_), (o["bb"][2] + 1, gy_)]))
            segs = [(min(c[0] for c in q.coords), max(c[0] for c in q.coords)) for q in getattr(seg, "geoms", [seg])
                    if not q.is_empty and hasattr(q, "coords")]
            segs = [(a_, b_) for a_, b_ in segs if r0_["x0"] + 15 < (a_ + b_) / 2 < r0_["x1"] - 15]
            if segs:
                a_, b_ = max(segs, key=lambda q: q[1] - q[0])
                x_ = (a_ + b_) / 2
                while any(abs(x_ - sx_) < 12 for sx_, _, _ in studs) and x_ < b_:
                    x_ += 2
                slots.append((x_, gy_))
        for v_ in vs_:
            pq = v_["poly"]
            _vo = -g_off if abs(pq[0][0] - pq[3][0]) < 1 else 0.0      # v246: statmenyje griovelis šalia ašies (smeigės kitoje pusėje)
            grooves.append((((pq[0][0] + pq[1][0]) / 2 + _vo, pq[0][1]), ((pq[2][0] + pq[3][0]) / 2 + _vo, pq[2][1])))
        ACR_GEO[g["name"]] = dict(F=F, parts=parts, vparts=vparts, cuts=cuts, holes=holes, grooves=grooves, knobs=knobs,
                                  studs=studs, slots=slots, g_off=g_off, cslot=CS,
                                  vjoints=vjoints, hs=hs_, vs=vs_, krail=(0.25, 0.15), kvert=(0.2, 0.12))
        print(f"  akrilinis rėmas {g['name']}: {len(parts)} dalys ({', '.join(f'{p_.bounds[2] - p_.bounds[0]:.0f}' for p_ in parts)} mm), "
              f"puzzle x {', '.join(f'{c_['x']:.0f} (po raide {c_['under'] * 100:.0f} %)' for c_ in cuts)}, Ø{_hd:g} skylių {len(holes)}, "
              f"statmenų / įstrižų atskirų detalių {len(vparts)} (puzzle į bėgelius)")


SUBS["{STUDS}"] = str(sum(len(AG_["studs"]) for AG_ in ACR_GEO.values())) if ACR_GEO else "?"     # v241
P10N_STUDS = []
P10_ROD = dict({"d": 6, "label": "M6"}, **(spec.get("p10_rod") or {}))
SEP_PTS = []


# ============================================================ REAR VIEW (MIRRORED)
WALL_BAL = None                                            # v299: sienos rėmo (l_hang) balionas
WALL_DIM = []
s2 = MM / SC2
_TOPX = 20 if any(_stack(g)[1] and not _stack(g)[0] and _rail_n(g) > 1 for g in groups) else 0
RVX, RVY = POS["R"][0] + 70, POS["R"][1] + 40 + _TOPX + (36 if LEDF else 0) + _AUTO.get("shift_r", 0)
rw, rh = PW * s2, PH * s2


def RV(x, y):
    return RVX + (PW - x) * s2, RVY + y * s2


def RVtf(x, y):
    p = RV(x, y); return p[0], K.Y(p[1])


def draw_zrear(zr, F, strips=True, frame="dash"):
    """Z kabinimas vaizde iš galo: F(x, y) -> lapo taškas (veidrodinis).
    Rytis 2026-10-07: apskritimo Z juostos ir sieninis rėmas - ATSKIROS detalės. strips - plokštės Z juostos
    (flanšas + kablys); frame: "solid" - rėmas (wallframe), "dash" - tik punktyrinis kontūras orientacijai, None."""
    zf, zt, tb = ZF["zf"], ZF["zt"], ZF["tb"]

    def R_(x0, y0, x1, y1, col, dash=None):
        a_, b_ = F(x0, y0), F(x1, y1)
        rect(min(a_[0], b_[0]), min(a_[1], b_[1]), abs(b_[0] - a_[0]), abs(b_[1] - a_[1]), fill=col,
             stroke=HexColor("#333333") if dash else black, lw=0.3 if dash else K.HAIR, dash=dash)
    if frame == "solid":
        for yy in (zr["yA"], zr["yB"]):
            R_(zr["fx0"] + tb, yy + zf, zr["fx1"] - tb, yy + 2 * zf - zt, K.mix(ZFC, 1.12))
            R_(zr["fx0"] + tb, yy + 2 * zf - zt, zr["fx1"] - tb, yy + 3 * zf - zt, ZFC)
        for x0 in (zr["fx0"], zr["fx1"] - tb):
            R_(x0, zr["fy0"], x0 + tb, zr["fy1"], K.mix(ZFC, 0.9))
    if strips:
        for yy in (zr["yA"], zr["yB"]):
            R_(zr["sx0"], yy, zr["sx1"], yy + zf - zt, K.mix(ZPC, 1.06))                      # flanšas prie plokštės
            R_(zr["sx0"], yy + zf - zt, zr["sx1"], yy + 2 * zf - zt, ZPC)                     # kablys
    if frame == "dash":
        R_(zr["fx0"], zr["fy0"], zr["fx1"], zr["fy1"], None, dash=(3, 1.5))


K.set_view(True)
for g in sorted(groups, key=lambda g: bool(g["spec"].get("behind"))):   # v10: iš galo "behind" grupė arčiau
    if g["plate"]:
        K.draw_shape(g["plate"]["sub"], RVtf, fill=PLATEC, stroke=black)
    for o in g["letters"]:
        if g["plate"]:      # X už plokštės - nematoma, punktyru
            K.draw_shape(o["sub"], RVtf, stroke=HexColor("#555555"), dash=(2, 1.2))
        elif P6_REAL(g):    # v62: iš galo matosi stiklo kraštas aplink 1,5 mm mažesnį dugną
            PV.rear_view(o["geom"], RVtf, retcol(g), facecol(g), front=gfront(g))
        else:               # tikras vaizdas iš galo: raidžių dugnas (P1 - nedažytas PVC, v186)
            K.draw_shape(o["sub"], RVtf, fill=backcol(g), stroke=black)
for g in groups:
    if g["name"] in ACR_GEO:                            # v229: akrilinis rėmas - dalys, puzzle, Ø8, griovelis
        AG = ACR_GEO[g["name"]]
        for P_ in AG["parts"] + AG["vparts"]:
            for gg in getattr(P_, "geoms", [P_]):
                _sub = [[("M", rg[0])] + [("L", q) for q in rg[1:]] for rg in
                        [list(gg.exterior.coords)] + [list(r.coords) for r in gg.interiors]]
                K.draw_shape(_sub, RVtf, fill=rcol(g), stroke=black, lw=0.4)
        _gw = float((ACRY.get("groove") or {}).get("w", 0) or 0)
        for (xa_, ya_), (xb_, yb_) in AG["grooves"]:
            if _gw:                                     # v231: griovelis 8 mm pločio - dvi linijos (nugaroje, matosi iš galo)
                _dl = math.hypot(xb_ - xa_, yb_ - ya_) or 1
                _nx, _ny = -(yb_ - ya_) / _dl * _gw / 2, (xb_ - xa_) / _dl * _gw / 2
                for _sg in (1, -1):
                    pa_, pb_ = RV(xa_ + _sg * _nx, ya_ + _sg * _ny), RV(xb_ + _sg * _nx, yb_ + _sg * _ny)
                    line(pa_[0], pa_[1], pb_[0], pb_[1], 0.25, HexColor("#1F7A1F"))
            else:
                pa_, pb_ = RV(xa_, ya_), RV(xb_, yb_)
                line(pa_[0], pa_[1], pb_[0], pb_[1], 0.3, HexColor("#1F7A1F"), dash=(3, 1.5))
        for hx_, hy_ in AG["holes"]:
            cc_ = RV(hx_, hy_)
            K.c.saveState(); K.c.setFillColor(white); K.c.setStrokeColor(HexColor("#1F5FD0")); K.c.setLineWidth(0.3)
            K.c.circle(cc_[0], K.Y(cc_[1]), max(0.6, ACRY["hole_d"] / 2 * s2), stroke=1, fill=1); K.c.restoreState()
        for sx_, sy_, _ in AG["studs"]:                 # v241: įleistos skylės (Ø12 iš galo + Ø5)
            cc_ = RV(sx_, sy_)
            K.c.saveState(); K.c.setStrokeColor(black); K.c.setLineWidth(0.25); K.c.setFillColor(white)
            K.c.circle(cc_[0], K.Y(cc_[1]), max(0.9, ACRY["stud"]["cb_d"] / 2 * s2), stroke=1, fill=1)
            K.c.circle(cc_[0], K.Y(cc_[1]), max(0.4, ACRY["stud"]["d"] / 2 * s2), stroke=1, fill=0); K.c.restoreState()
        for ox_, oy_ in AG["slots"]:                    # v241: ovali skylė laidui (kiaurai)
            cc_ = RV(ox_, oy_)
            rect(cc_[0] - max(1.2, AG["cslot"][0] / 2 * s2), cc_[1] - max(0.6, AG["cslot"][1] / 2 * s2),
                 2 * max(1.2, AG["cslot"][0] / 2 * s2), 2 * max(0.6, AG["cslot"][1] / 2 * s2), fill=white, lw=0.25)
        for _ci, c_ in enumerate(AG["cuts"]):           # v231: jungtis pagal lakšto ilgį - brūkšn. taškinė linija + žyma
            _jx = RV(c_["x"], 0)[0]
            _jy0, _jy1 = RV(0, AG["F"].bounds[1])[1] - 10, RV(0, AG["F"].bounds[3])[1] + 10
            line(_jx, _jy0, _jx, _jy1, 0.5, HexColor("#C00000"), dash=([6, 2, 1.5, 2], 0))
            K._Tbg(_jx + 3, _jy0 - 4, f"J{_ci + 1}", 7, align="c", font="FB", auto_red=False)
        # v233: detalių nuorodos (2 lapas): C - bėgelių puzzle (J1), D - statmuo -> bėgelis
        _refs = []
        if AG["cuts"]:
            _refs.append(("C", AG["cuts"][0]["x"], (AG["hs"][0]["y0"] + AG["hs"][0]["y1"]) / 2))
        if AG["vjoints"]:
            _vj = min(AG["vjoints"], key=lambda q: (q[4], q[1], abs(q[0] - (AG["F"].bounds[0] + AG["F"].bounds[2]) / 2)))
            _refs.append(("D", _vj[0], _vj[1]))
        for _rn, _rx, _ry in _refs:
            _cc = RV(_rx, _ry)
            K.circle(_cc[0], _cc[1], 7, stroke=HexColor("#C00000"), lw=0.5)
            K.leader(_cc[0] + 5, _cc[1] - 5, _cc[0] + 16, _cc[1] - 26, _rn)
            T(_cc[0] + 25, _cc[1] - 24, "sheet 2", 6, color=K.GREY)
        continue
    for r_ in g["rails"]:
        poly([RV(*q) for q in r_["poly"]], fill=rcol(g), lw=0.4)
    if MOUNTING == "l_hang":                            # v299 (Rytis): sienos rėmas (7) - PUNKTYRU, po 50 mm trumpesnis nuo galų
        _wl = [r_ for r_ in g["rails"] if r_["kind"] == "h" and not r_.get("support")]
        for r_ in _wl:                                  # kontūras 4 mm platesnis už raidžių L - matomas šalia jo
            _wa, _wb = wall_span(g, r_)
            a_, b_ = RV(_wb, r_["y0"] - 4), RV(_wa, r_["y1"] + 4)
            rect(min(a_[0], b_[0]), min(a_[1], b_[1]), abs(b_[0] - a_[0]), abs(b_[1] - a_[1]), stroke=HexColor("#333333"), lw=0.5,
                 dash=([3, 2], 0))
        if _wl:
            _bw = max(_wl, key=lambda r_: r_["y1"])
            _pp = RV(wall_span(g, _bw)[0], _bw["y1"] + 4)
            WALL_BAL = (_pp[0], _pp[1])
            WALL_DIM = [wall_span(g, r_) for r_ in _wl]
    if g.get("zfr"):
        draw_zrear(g["zfr"], RV, strips=True, frame="dash")
    for fp_ in g["fplates"]:                            # ausėlės / plokštelės su skyle (pailgintos - aukštesnės)
        px_, py_, ph_, hy_ = ear4(g, fp_)
        a_, b_ = RV(px_ + g["fpl_sz"], py_), RV(px_, py_ + ph_)
        rect(a_[0], a_[1], b_[0] - a_[0], b_[1] - a_[1], fill=K.mix(rcol(g), 0.85), lw=K.HAIR)
        cc_ = RV(px_ + g["fpl_sz"] / 2, hy_)
        K.c.saveState(); K.c.setFillColor(white); K.c.setLineWidth(K.HAIR)
        K.c.circle(cc_[0], K.Y(cc_[1]), max(0.5, EARS.get('hole_d', 6) / 2 * s2), stroke=1, fill=1); K.c.restoreState()
for b_ in BRACKETS:                                     # v90: U laikikliai (arčiausiai žiūrovo iš galo)
    hw_ = BRK["width_mm"] / 2
    a_, c_ = RV(b_["x"] + hw_, b_["y0"]), RV(b_["x"] - hw_, b_["y1"])
    # v184 (Rytis 2026-10-13): galiniame vaizde laikiklis - TIK punktyru (kontūras ir skylės), be užpildo
    rect(a_[0], a_[1], c_[0] - a_[0], c_[1] - a_[1], fill=None, lw=K.HAIR, dash=([3, 1.5], 0))
    for k_ in range(b_["nw"]):
        yy_ = b_["y0"] + b_["H"] * (2 * k_ + 1) / (2 * b_["nw"])     # v90: žingsnis p, nuo galų p/2
        cc_ = RV(b_["x"], yy_)
        K.c.saveState(); K.c.setLineWidth(K.HAIR); K.c.setDash(1.5, 1)
        K.c.circle(cc_[0], K.Y(cc_[1]), max(0.6, b_["hd"] / 2 * s2), stroke=1, fill=0); K.c.restoreState()
SEP_LINE = None
SEP_END = None
if MOUNTING == "none":                                  # v90: atskiros raidės - laidų išvestys vienoje horizontalioje linijoje
    from shapely.geometry import LineString as _LS
    _ls = [o for g in groups if not g["plate"] for o in g["letters"]]
    _H = sorted(o["bb"][3] - o["bb"][1] for o in _ls)[len(_ls) // 2] if _ls else 0
    _main = [o for o in _ls if (o["bb"][3] - o["bb"][1]) >= 0.5 * _H] or _ls
    if _main:
        _y0, _y1 = min(o["bb"][1] for o in _main), max(o["bb"][3] for o in _main)
        for _e in (23, 18, 15, 13, 11):                  # dugnas -3 + D11 centras 20 / 15 / 12 / 10 / 8 nuo dugno krašto
            _sf = [o["geom"].buffer(-_e, join_style=2) for o in _main]
            _best, y = None, _y0 + 1
            while y < _y1:
                _seg = []
                for o, sf in zip(_main, _sf):
                    q = sf.intersection(_LS([(o["bb"][0] - 1, y), (o["bb"][2] + 1, y)]))
                    _p = [g_ for g_ in getattr(q, "geoms", [q]) if not g_.is_empty and g_.length > 0]
                    if not _p:
                        _seg = None; break
                    _seg.append(max(_p, key=lambda g_: g_.length))
                if _seg and (_best is None or min(g_.length for g_ in _seg) > _best[0]):
                    _best = (min(g_.length for g_ in _seg), y, _seg)
                y += 2
            if _best:
                break
        if _best:
            SEP_LINE = _best[1]
            a_, b_ = RV(min(o["bb"][0] for o in _main) - 40, SEP_LINE), RV(max(o["bb"][2] for o in _main) + 40, SEP_LINE)
            line(a_[0], a_[1], b_[0], b_[1], 0.4, HexColor("#D0021B"), dash=([4, 2], 0))
            SEP_END = (max(a_[0], b_[0]), a_[1], max(RV(0, o["bb"][3])[1] for o in _main))   # v302: -> trafo box
            for sg in _best[2]:
                xm = (sg.coords[0][0] + sg.coords[-1][0]) / 2
                SEP_PTS.append((xm, SEP_LINE))
                cc_ = RV(xm, SEP_LINE)
                K.c.saveState(); K.c.setFillColor(HexColor("#D0021B")); K.c.circle(cc_[0], K.Y(cc_[1]), 1.6, stroke=0, fill=1); K.c.restoreState()
            _xtra = [o for o in _ls if o not in _main]          # v268: kiekviena dalis turi išvestį (P6 / P10)
            for o in _xtra:            # v250: smulkios dalys (i taškas) - irgi išvestis (centre)
                from shapely.ops import polylabel as _pl
                _g = max(getattr(o["geom"], "geoms", [o["geom"]]), key=lambda g_: g_.area)
                _c = _g.centroid if _g.buffer(-8).contains(_g.centroid) else _pl(_g, 0.5)   # v268: centre, ne galas
                SEP_PTS.append((_c.x, _c.y))
                cc_ = RV(_c.x, _c.y)
                K.c.saveState(); K.c.setFillColor(HexColor("#D0021B")); K.c.circle(cc_[0], K.Y(cc_[1]), 1.6, stroke=0, fill=1); K.c.restoreState()
            _nx = len(_main) + len(_xtra)
            _pw = str(spec.get("letters_power", "per_letter")).lower()
            _lbl = ("WAGO inside letters, one supply cable" if _pw.startswith("wago")
                    else f"12V cable 1.5 m from each letter, exits on one line ({_nx} pcs."
                    + (", small parts - exit in the part" if _xtra else "") + ")")
            _ty = RV(0, min(o["bb"][1] for o in _main))[1] - 8      # virš galinio vaizdo
            T(min(a_[0], b_[0]), _ty, "- - -  " + _lbl, 7.5, color=HexColor("#D0021B"))
            print(f"  atskiros raidės: laidų linija y{SEP_LINE:.0f} (nuo viršaus), {_nx} išvestys; {_lbl}")
        else:
            print("  ! atskiros raidės: bendros horizontalios laidų linijos nėra - dėti ranka")
# v249/v250 (Rytis 2026-10-15, BN danbolig): P10 BE BĖGIO (mounting "none") - Alu dugnelyje ilgasriegiai į fasadą +
#  popierinis šablonas. Bėgio nėra -> horizontalios linijos nereikia; taškai LABIAU Į PLOTO CENTRĄ (ne krašte): raidės plotas
#  dalijamas į n dalių (k-means), kiekvienos dalies centras pritraukiamas į štricho vidurį. n: raidė 4 (ne 5), siaura / smulki
#  dalis (i stiebas, l, i taškas) 2; g kojelė gauna savo tašką; ne ant laidų išvesčių.
def _p10_rods(lets, rim, d, exits, exd_min=0.0):
    import numpy as np
    import shapely as _sh
    out, fail = [], []
    for o in lets:
        g = o["geom"]; x0, y0, x1, y1 = o["bb"]; w, h = x1 - x0, y1 - y0
        n = 2 if (min(w, h) < 0.35 * max(w, h) or max(w, h) < 120) else 4
        inner = g.buffer(-(rim + 1 + d / 2))
        if max(w, h) < 120 and min(w, h) > 0.6 * max(w, h) and not inner.is_empty:
            # v252 (Rytis): smulki kvadratinė dalis (i taškas) - 2 taškai ĮSTRIŽAI (priešingi kampai), išvestis centre
            cs_ = list(inner.exterior.coords) if hasattr(inner, "exterior") else list(max(inner.geoms, key=lambda q: q.area).exterior.coords)
            a_, b_ = min(cs_, key=lambda q: q[0] + q[1]), max(cs_, key=lambda q: q[0] + q[1])
            out += [(float(a_[0]), float(a_[1]), len(out)), (float(b_[0]), float(b_[1]), len(out) + 1)]
            continue
        st = max(1.0, min(w, h) / 60)
        X, Y = np.meshgrid(np.arange(x0, x1, st), np.arange(y0, y1, st))
        X, Y = X.ravel(), Y.ravel()
        A = np.c_[X, Y][_sh.contains_xy(g, X, Y)]                    # raidės plotas
        C = np.c_[X, Y][_sh.contains_xy(inner, X, Y)] if not inner.is_empty else np.zeros((0, 2))
        if len(C) == 0:
            fail.append(round(x0)); continue
        bd = _sh.distance(g.boundary, _sh.points(C))                # atstumas iki krašto (štricho vidurys = max)
        rng = np.random.default_rng(0)
        cen = A[rng.choice(len(A), n, replace=False)] if len(A) >= n else A
        for _ in range(60):                                         # k-means (ploto dalys)
            lab = np.argmin(((A[:, None] - cen[None]) ** 2).sum(-1), 1)
            new = np.array([A[lab == k].mean(0) if (lab == k).any() else cen[k] for k in range(len(cen))])
            if np.allclose(new, cen): break
            cen = new
        sep = max(15.0, 0.25 * min(w, h))
        exs = [e for e in exits if g.buffer(5).contains(_sh.points(e))]
        exd = max(exd_min, min(20.0, 0.3 * min(w, h))) if exs else 0
        got = []
        order = np.argsort([-(lab == k).sum() for k in range(len(cen))])
        for k in order:
            sc = np.hypot(*(C - cen[k]).T) - 1.5 * bd               # arti ploto dalies centro IR štricho vidurio
            for e in exs:
                sc = sc + np.where(np.hypot(*(C - e).T) < exd + d / 2, 1e6, 0)
            for q in got:
                sc = sc + np.where(np.hypot(*(C - q).T) < sep, 1e6, 0)
            b_ = int(np.argmin(sc))
            if sc[b_] < 1e5:
                got.append(C[b_])
        if len(got) < 2:
            fail.append(round(x0))
        out += [(float(q[0]), float(q[1]), len(out) + i_) for i_, q in enumerate(got)]
    return out, fail


def _p10_rods_lines(lets, rim, d, exits, sep_y, exd_min=0.0):
    """v251 (Rytis 2026-10-15: „tvirtinimo taškus stengtis išlaikyti vienoje linijoje tiek viršuje, tiek apačioje"):
    dvi BENDROS horizontalios linijos per x aukščio raides (viršutinė ~30 %, apatinė ~70 % x aukščio - į ploto centrą, ne krašte),
    taškai - štrichų sankirtų viduriai (plati raidė - kairysis ir dešinysis štrichas = 4, siaura - 1 + 1 = 2);
    kojelė žemiau bazinės linijos (g) - papildomas taškas; smulkios dalys (i taškas) ir raidės be 2 taškų - _p10_rods."""
    import numpy as np
    from shapely.geometry import LineString as _L
    from shapely.ops import polylabel as _pl
    hs = sorted(o["bb"][3] - o["bb"][1] for o in lets)
    main = [o for o in lets if (o["bb"][3] - o["bb"][1]) >= 0.5 * hs[len(hs) // 2]]
    yb = sorted(o["bb"][3] for o in main)[len(main) // 2]
    yt = sorted(o["bb"][1] for o in main)[len(main) // 2]
    H = yb - yt
    cl = rim + 1 + d / 2
    inn = {id(o): o["geom"].buffer(-cl) for o in main}
    def segs(o, y):
        q = inn[id(o)].intersection(_L([(o["bb"][0] - 1, y), (o["bb"][2] + 1, y)]))
        return sorted([g_ for g_ in getattr(q, "geoms", [q]) if not g_.is_empty and g_.length > 0], key=lambda g_: g_.bounds[0])
    strk = np.median([sg.length for o in main for sg in segs(o, yt + 0.5 * H)] or [30]) + 2 * cl
    def pick(o, y):
        mids = []
        hw = max((strk - 2 * cl) / 2, 0)
        for g_ in segs(o, y):
            x0_, x1_ = g_.bounds[0], g_.bounds[2]
            if g_.length <= 2.2 * strk:                      # kertamas štrichas - vidurys
                mids.append(((x0_ + x1_) / 2, y))
            else:                                            # v252: linija eina išilgai lanko / skersinio - taškai GALUOSE
                mids += [(x0_ + hw, y), (x1_ - hw, y)]       #  (štricho vidurio atstumu nuo krašto)
        if not mids:
            return []
        mids.sort()
        wide = (o["bb"][2] - o["bb"][0]) > 0.45 * H
        return [mids[0], mids[-1]] if (wide and len(mids) >= 2) else [mids[len(mids) // 2]]
    def best(lo, hi, tgt):
        res = None
        for y in np.arange(yt + lo * H, yt + hi * H, 2.0):
            if sep_y is not None and abs(y - sep_y) < 15:
                continue
            sc = sum(len(pick(o, y)) for o in main) - abs(y - (yt + tgt * H)) / H
            if res is None or sc > res[0]:
                res = (sc, float(y))
        return res[1] if res else None
    # v252 (Rytis 2026-10-15, sudėliota ranka DB-0002): viršutinė linija ~12 % x aukščio nuo viršaus, apatinė ~82 %
    #  (~15-20 mm virš laidų išvesčių linijos) - arti raidės viršaus / apačios, bet štricho viduryje
    y1, y2 = best(0.10, 0.14, 0.12), best(0.79, 0.86, 0.82)
    print(f"  P10 ilgasriegių linijos: y{y1} / y{y2}; x aukštis {yt:.0f}-{yb:.0f} (H {H:.0f}), laidų linija {sep_y}")
    out, fail, rest = [], [], [o for o in lets if o not in main]
    for o in main:
        pts = [p for y in (y1, y2) if y is not None for p in pick(o, y)]
        if len(pts) < 2:
            rest.append(o); continue
        if o["bb"][3] > yb + 0.15 * H:                         # kojelė (g, p, y) - papildomas taškas
            from shapely.geometry import box as _box
            lg = o["geom"].buffer(-cl).intersection(_box(o["bb"][0] - 1, yb - 0.02 * H, o["bb"][2] + 1,
                                                         yb + 0.55 * (o["bb"][3] - yb)))   # v252: kojelės viršutinė dalis
            if not lg.is_empty:
                lg = max(getattr(lg, "geoms", [lg]), key=lambda g_: g_.area)
                c_ = _pl(lg, 0.5)
                pts.append((c_.x, c_.y))
        out += [(float(x), float(y), len(out) + i_) for i_, (x, y) in enumerate(pts)]
    o2, f2 = _p10_rods(rest, rim, d, exits, exd_min)
    return out + [(x, y, len(out) + i_) for i_, (x, y, _) in enumerate(o2)], fail + f2


if FRONT == "P10" and MOUNTING == "none":
    _lets = [o for g in groups if not g["plate"] for o in g["letters"]]
    _rim = float((spec.get("p10") or {}).get("rim", 5))
    P10N_STUDS, _f = _p10_rods_lines(_lets, _rim, float(P10_ROD["d"]), SEP_PTS, SEP_LINE)
    for _x in _f:
        print(f"  ! P10 ilgasriegiai: raidė x{_x} - mažiau nei 2 taškai - PATIKRINTI")
    SUBS["{STUDS}"] = str(len(P10N_STUDS))
    print(f"  P10 ilgasriegiai (be bėgio): {len(P10N_STUDS)} vnt.")
P6N_FIX = False
if FRONT != "P10" and MOUNTING == "none" and spec.get("back_fix_holes", True):
    # v268 (Rytis 2026-10-15, OMODA PO 33580: „tvirtinimo ir laido skylės dugne (nurodyti dokumente)"): atskiros P6 raidės -
    #  tvirtinimo skylės dugne į fasadą ta pačia logika kaip P10 ilgasriegiai (dvi bendros linijos, štricho vidurys, kiekviena
    #  dalis >= 2, ne ant laidų išvesčių); centras >= `back_hole_edge` (10) nuo DUGNO kontūro (dugnas = stiklas - inset 3)
    _lets = [o for g in groups if not g["plate"] for o in g["letters"]]
    _hd = float(spec.get("back_hole_d", 3.2))
    _cl = float(spec.get("back_inset_mm", 3)) + float(spec.get("back_hole_edge", 10))
    P10_ROD = {"d": _hd, "label": f"D{_hd:g}"}
    P10N_STUDS, _f = _p10_rods_lines(_lets, _cl - 1 - _hd / 2, _hd, SEP_PTS, SEP_LINE, exd_min=25.0)   # D11 >= 25 nuo varžtų
    P6N_FIX = True
    for _x in _f:
        print(f"  ! P6 tvirtinimo skylės: dalis x{_x} - mažiau nei 2 - PATIKRINTI")
    SUBS["{STUDS}"] = str(len(P10N_STUDS))
    print(f"  P6 tvirtinimo skylės dugne (atskiros raidės): {len(P10N_STUDS)} vnt. Ø{_hd:g}, laido išvestys {len(SEP_PTS)}")
if _RJ and MOUNTING == "none":                            # v268: skylės -> p6_dxf (tos pačios kaip lape)
    try:
        _rjd = json.load(open(_RJ))
        _rjd["fix_holes"] = [[x_, y_, P10_ROD["d"]] for x_, y_, _ in P10N_STUDS] if P6N_FIX else []
        _rjd["cable_holes"] = [[x_, y_, 11] for x_, y_ in SEP_PTS]
        json.dump(_rjd, open(_RJ, "w"), indent=1)
    except Exception as _e:
        print("  ! rails json skylių įrašymas:", _e)
K.set_view(False)
# bėgelių ilgiai (žymos) + vertikali grandinė (bėgelių ašys) kairėje
def TL(x, y, txt, size, align="c", rot=0, color=None):
    """užrašas su baltu fonu (skaitomas ant spalvotų raidžių galiniame vaizde)"""
    w_ = K.pdfmetrics.stringWidth(str(txt), "F", size)
    x0 = {"l": 0, "c": -w_ / 2, "r": -w_}[align]
    K.c.saveState(); K.c.translate(x, K.Y(y)); K.c.rotate(rot); K.c.setFillColor(white)
    K.c.rect(x0 - 1.5, -1.8, w_ + 3, size + 1.6, stroke=0, fill=1); K.c.restoreState()
    T(x, y, txt, size, align=align, rot=rot, color=color or black, auto_red=False)


# Rytis 2026-10-07: TRAFO BOX - VISI laidai (po vieną kiekvienai šviečiančiai grupei: raidės, X) eina į vieną
# trafo dėžę (spalva = rėmo spalva); prie kiekvieno laido - įtampa ir ilgis. Laidas išeina iš grupės apatinio
# horizontalaus bėgelio (X - apatinės Z juostos) galo, atsuktо į dėžę. Ilgis = |dx| + |dy| iki dėžės (už iškabos,
# apačioje, ties dėžės vieta) + atsarga, apvalinta aukštyn 0,5 m.
TB = spec.get("trafo_box", {}) if spec.get("trafo_box") is not False else None
TB_ON = TB is not None and (bool(CABLES) or bool(TB))
TB_V = (TB or {}).get("voltage") or next((c_["voltage"] for c_ in CABLES if not K.unk(c_["voltage"])), "12V")
TB_X = (TB or {}).get("x", PW / 2)                     # dėžės vieta (iškabos koord., mm)
TB_RES = (TB or {}).get("reserve_m", 1.0)
TB_LEN = (TB or {}).get("cable_len_m", 3.0)               # Rytis 2026-10-08 (v13): visi laidai 12V 3 m


def _grp_ends(g):
    """galimi laido išėjimai. Rytis 2026-10-07:
      * raidės ant plokštės (X) - iš RAIDĖS apatinio kampo (ne iš Z profilio), laidas plokštės nugara žemyn;
      * raidės ant bėgelių - apatinis bėgelis; jei grupė yra PO kita grupe (pvz. darbo valandos po EXTRA) -
        viršutinis bėgelis; spec grupėje "cable": {"rail": "bottom|top|auto", "end": "first|last"}
        (EXTRA - "first": prie E raidės)."""
    cs = g["spec"].get("cable", {}) or {}
    if g["plate"]:
        pts = [p_ for o in g["letters"] for sp in o["sub"] for p_ in K.flatten(sp, 16)]
        if pts:
            # Rytis 2026-10-08: VISADA X kojelės IŠORINIS APATINIS KAMPAS - kojelė, kuri galiniame (veidrodiniame)
            # vaizde yra KAIRĖJE (= dešinė kojelė iš priekio); laidas iš kampo tiesiai žemyn
            ymax, ymin = max(p_[1] for p_ in pts), min(p_[1] for p_ in pts)
            bot = [p_ for p_ in pts if p_[1] >= ymax - 0.03 * (ymax - ymin)]
            c_ = max(bot, key=lambda p_: p_[0])
            return [(c_[0], c_[1], 1, g, None)]
        return []
    hs_ = sorted([r_ for r_ in g["rails"] if r_["kind"] == "h"], key=lambda r_: r_["y0"])
    if cs.get("from") == "letter" and cs.get("x_pt") is not None:
        # v52 (Rytis 2026-10-09, Joker): laidas iš RAIDĖS galo (D11) - VISADA VIRŠ RĖMO (virš viršutinio bėgelio),
        # niekada po juo; raidė ties x_pt, taškas - raidės viduryje (x) tarp raidės viršaus ir bėgelio; jei juosta
        # siaura - mažinamas atstumas iki kontūro / bėgelio (8 -> 5 -> 3 / 8 -> 4 -> 2 mm). Toliau trasa pagal "out".
        xq = (cs["x_pt"] - OX) * S
        let_ = min(g["letters"], key=lambda o: o["geom"].distance(Point(xq, (o["bb"][1] + o["bb"][3]) / 2)))
        bx0_, by0_, bx1_, by1_ = let_["bb"]
        xc_ = (bx0_ + bx1_) / 2
        ytop_ = min([r_["y0"] for r_ in hs_ if r_["x0"] < bx1_ and r_["x1"] > bx0_] or [by1_])
        best_ = None
        for m_, c_ in ((8, 8), (5, 4), (3, 2), (1.5, 1)):
            inner_ = let_["geom"].buffer(-m_).intersection(sbox(bx0_, by0_, bx1_, ytop_ - c_))
            if inner_.is_empty:
                continue
            # arčiausiai raidės vidurio (x), tada - kuo aukščiau (ne į užraitus / smailes kraštuose)
            from shapely.ops import nearest_points as _np
            _ln = __import__("shapely.geometry", fromlist=["LineString"]).LineString([(xc_, by0_ - 1), (xc_, ytop_)])
            if inner_.intersects(_ln):
                _seg = inner_.intersection(_ln)
                best_ = (xc_, _seg.bounds[1] + 0.5 * min(4, _seg.bounds[3] - _seg.bounds[1]))
            else:
                _p = _np(inner_, _ln)[0]
                best_ = (_p.x, _p.y)
            break
        if best_:
            dir_ = {"left": -1, "right": 1}.get(cs.get("out")) or (-1 if best_[0] - g["x0"] < g["x1"] - best_[0] else 1)
            return [(best_[0], best_[1], dir_, g, None)]
        print(f"  ! {g['name']}: laido išvesčiai virš rėmo raidėje vietos nėra - spręsti ranka")
    if not hs_ and g["spec"].get("no_rails"):      # v11: forma be rėmo (pvz. PANT apskritimas ant fasado) - D11 apačioje
        pts = [p_ for o in g["letters"] for sp in o["sub"] for p_ in K.flatten(sp, 16)]
        if pts:
            ymax = max(p_[1] for p_ in pts)
            cx_ = sum(p_[0] for p_ in pts) / len(pts)
            return [(cx_, ymax - 40, 1, g, None)]
        return []
    if not hs_:
        return []
    mode = cs.get("rail", "auto")
    if mode == "auto":
        mode = "top" if _stack(g)[0] else "bottom"
    r_ = hs_[0] if mode == "top" else hs_[-1]
    yy = (r_["y0"] + r_["y1"]) / 2
    if cs.get("x_pt") is not None:                  # v13: išvestis kliento faile nurodytoje vietoje ant bėgelio
        x_ = min(max((cs["x_pt"] - OX) * S, r_["x0"] + 15), r_["x1"] - 15)
        d_ = cs.get("dir") or (-1 if x_ - r_["x0"] < r_["x1"] - x_ else 1)
        return [(x_, yy, d_, g, r_)]
    _in = max(60.0, 9.0 / s2) if cs.get("out") in ("up", "down") else 0.0   # v15: ne ant matmens išvadinės
    ends = [(r_["x0"] + _in, yy, -1, g, r_), (r_["x1"] - _in, yy, 1, g, r_)]
    if cs.get("end") == "first":
        ends = ends[:1]
    elif cs.get("end") == "last":
        ends = ends[1:]
    return ends


def cable_exit_pos(cb):
    ends = [(r_["x0"], (r_["y0"] + r_["y1"]) / 2, -1, g, r_) for g in groups for r_ in g["rails"] if r_["kind"] == "h"] + \
           [(r_["x1"], (r_["y0"] + r_["y1"]) / 2, 1, g, r_) for g in groups for r_ in g["rails"] if r_["kind"] == "h"]
    return min(ends, key=lambda e: math.dist((e[0], e[1]), (cb["x"], cb["y"]))) if ends else None


if TB_ON:
    # Rytis 2026-10-07: laidų galų parinkimas - perrenkami visi deriniai (<= 2^n); bauda už: nuleidimą per kitą
    # grupę / jos matmenis, nuleidimą per kitos grupės ašių grandinę, dviejų grandinių susidūrimą tame pačiame
    # tarpe, grandinę ant kitos grupės; po to - artumas dėžei.
    import itertools as _it
    _lit = [g for g in groups if g["letters"] and g["spec"].get("lit") is not False and g["spec"].get("cable") is not False
            and _grp_ends(g)]

    def _gx(g2):
        return min(RV(g2["x0"], 0)[0], RV(g2["x1"], 0)[0]), max(RV(g2["x0"], 0)[0], RV(g2["x1"], 0)[0])

    def _gy(g2):
        return RV(0, g2["y0"])[1], RV(0, g2["y1"])[1]

    def _chain_zone(g2, cside):
        hs2 = [r_ for r_ in g2["rails"] if r_["kind"] == "h"]
        if g2.get("zfr"):
            x_ = RV(g2["x0"], 0)[0] + 14
            return (x_ - 12, x_ + 26, RV(0, g2["zfr"]["yA"])[1], RV(0, g2["zfr"]["yB"] + g2["zfr"]["fp"])[1])
        if len(hs2) < 2 or g2["plate"]:
            return None
        ys2 = [RV(0, (r_["y0"] + r_["y1"]) / 2)[1] for r_ in hs2]
        if (id(g2), 1) in cside and (id(g2), -1) not in cside:
            x_ = RV(g2["x0"], 0)[0] + 14; return (x_ - 12, x_ + 26, min(ys2), max(ys2))
        x_ = RV(g2["x1"], 0)[0] - 14; return (x_ - 26, x_ + 12, min(ys2), max(ys2))

    def _drop_x(e):
        if e[4] is None and (e[3]["plate"] or e[3]["spec"].get("no_rails")):   # X / forma be rėmo: tiesiai žemyn
            return RV(e[0], 0)[0]
        return (_gx(e[3])[0] - 10) if e[2] > 0 else (_gx(e[3])[1] + 10)   # galas x1 -> lape kairėje

    def _score(combo):
        cside = {(id(e[3]), e[2]) for e in combo}
        zones = {id(g2): _chain_zone(g2, cside) for g2 in groups}
        pen = 0.0
        for e in combo:
            xd, ys = _drop_x(e), RV(0, e[1])[1]
            for g2 in groups:
                z_ = zones[id(g2)]
                if z_ and z_[0] - 6 <= xd <= z_[1] + 6 and z_[3] + 10 > ys:
                    pen += 100                                  # per (bet kurios) grupės ašių grandinę
                if g2 is e[3]:
                    continue
                xa, xb = _gx(g2); ya, yb = _gy(g2)
                if xa - 4 <= xd <= xb + 4 and yb + (60 if not _stack(g2)[1] else 0) > ys:   # kita grupė / jos matmenys žemiau
                    pen += 50                                   # per kitą grupę / jos matmenis
                z_ = None
                if z_ and z_[0] - 6 <= xd <= z_[1] + 6 and z_[3] + 10 > ys:
                    pen += 100                                  # per kitos grupės ašių grandinę
            pen += abs(e[0] - TB_X) / max(PW, 1)               # artumas dėžei (mažas svoris)
        dx_ = sorted(_drop_x(e) for e in combo)
        pen += 40 * sum(1 for u, v in zip(dx_[:-1], dx_[1:]) if v - u < 12)   # nuleidimai per arti vienas kito
        zl = [(id(g2), z_) for g2 in groups for z_ in [zones[id(g2)]] if z_]
        for (i1, z1), (i2, z2) in _it.combinations(zl, 2):
            if z1[0] < z2[1] + 4 and z2[0] < z1[1] + 4 and z1[2] < z2[3] + 6 and z2[2] < z1[3] + 6:
                pen += 100                                      # dvi grandinės susiduria
        for i1, z1 in zl:
            for g2 in groups:
                if id(g2) == i1:
                    continue
                xa, xb = _gx(g2); ya, yb = _gy(g2)
                if z1[0] < xb and xa < z1[1] and z1[2] < yb and ya < z1[3]:
                    pen += 30                                   # grandinė ant kitos grupės
        return pen
    _best = min(_it.product(*[_grp_ends(g) for g in _lit]), key=_score) if _lit else ()
    if os.environ.get("CABDBG"):
        for _c in _it.product(*[_grp_ends(g) for g in _lit]):
            print("CAB", [(e[3]["name"], e[2]) for e in _c], round(_score(_c), 2), [round(_drop_x(e)) for e in _c])
    CEX = []
    for e in _best:
        CEX.append(({"x": e[0], "y": e[1], "voltage": TB_V, "label": "", "len_m": 0, "group": e[3]["name"]}, e))
    CABLES = [cb for cb, _ in CEX]
else:
    CEX = [(cb, cable_exit_pos(cb)) for cb in CABLES]
CAB_SIDE = {(id(ce[3]), ce[2]) for _, ce in CEX if ce}           # (grupė, galas) su laidu
CH_BOT = [0]
# Rytis 2026-10-07: rėmo matmenys NEUŽSTOJA galinio vaizdo - visi už raidžių gabarito:
#  viršuje / apačioje: 1 eilė - ausėlių grandinė (nuo bėgelio galų), 2 eilė - bėgelio ilgis „L (U..)",
#  3 eilė - kiti elementai (vidurinis bėgelis, statmenys, i taško laikiklis) - žyma su išvadine;
#  bėgelių ašių grandinė - šone už grupės. Skaičiai ant raidžių nededami.
ROW = [16, 36, 56]
DIM_ROWS = []                                           # v172: galinio vaizdo matmenų eilės (side, row, x0, x1)
TAG_BOXES = []                                          # v157: padėtų galinio vaizdo žymų dėžutės (x0, x1, y)
UPR = [0]                                               # v13: matmenų eilių virš galinio vaizdo skaičius
_PFX = "□" if str(spec.get("rail", {}).get("type", "u")).lower().startswith(("sq", "box", "kv")) else ("acrylic " if RAIL_ACR else ("L" if str(spec.get("rail", {}).get("type", "u")).upper() == "L" else "U"))
_vt, _vb = RVY, RVY + rh                                # vaizdo viršus / apačia (lapo koord.)


_CAB_UPX = [RV(e_[0], 0)[0] for g_ in groups if ((g_["spec"].get("cable") or {}).get("out") == "up")
            for e_ in _grp_ends(g_)]                    # v50: laidas aukštyn kerta matmenų eilutes - tekstas pasitraukia


def _rail_len_dim(r_, y_, from_y, g, avoid=None, n=1):
    xa_, xb_ = RV(r_["x1"], 0)[0], RV(r_["x0"], 0)[0]
    avoid = list(avoid or []) + _CAB_UPX + AV_ALL               # v172: VISŲ grupių žymų išvadinės ir laidai
    hdim(xa_, xb_, y_, (f"{n}× " if n > 1 else "") + f"{round(r_['len'])}  ({_PFX}{g['rsz']['size']})", from_y, from_y, size=K.F_DIM_FRAME, avoid=avoid,
         small_side="l" if (xa_ + xb_) / 2 < RVX + rw / 2 else "r")


# Rytis 2026-10-07: galiniame vaizde TIK bendriniai matmenys - rėmo profilių ilgiai (pagrindas), statmenų / kitų
# profilių ilgių žymos, bėgelių ašių atstumai; ausėlių grandinių NĖRA (ausėlės - 1:1 faile ir priekio vaizde);
# X Z juostos - tik plotis (ilgis) ir aukštis tarp centrų.
AV_ALL = []                                             # v172: x visų statmenų / vidurinių (jų žymų išvadinės)
for g in groups:
    _hs = sorted([r_ for r_ in g["rails"] if r_["kind"] == "h"], key=lambda r_: r_["y0"])
    _car = [_hs[0], _hs[-1]] if len(_hs) >= 2 else _hs
    AV_ALL += [RV((r_["x0"] + r_["x1"]) / 2, 0)[0] for r_ in g["rails"] if not any(r_ is q for q in _car)]
AV_ALL += [RV(c_["x"], c_["y"])[0] for c_ in CABLES if c_.get("point")]
AXIS_TXT = []                                           # v172: (y vidurys, teksto ilgis) - laidas nekerta užrašo
AXIS_X = []                                             # v172: bėgelių ašių grandinių x (laidai nekerta jų užrašų)
for g in groups:
    hs_ = sorted([r_ for r_ in g["rails"] if r_["kind"] == "h"], key=lambda r_: r_["y0"])
    car_ = [hs_[0], hs_[-1]] if len(hs_) >= 2 else hs_
    AV_ = [RV((r_["x0"] + r_["x1"]) / 2, 0)[0] + d_ for r_ in g["rails"] if not any(r_ is q for q in car_)
           for d_ in (range(-32, 33, 4) if (r_["kind"] != "v" or spec.get("vert_labels")) else (0,))]                   # v276: įstriža žymos išvadinė (±0,36·dy) - tekstas laisvas visoje juostoje
    blk_top, blk_bot, gap_ = _stack(g)
    used = {"up": 0, "dn": 0}
    # v276 (ISO 129-1, Rytis „linija ant linijos"): vienodi nešantieji bėgeliai (tas pats x ruožas) - VIENAS matmuo „n× L";
    #  antro matmens iškeltinės eitų per pirmo bėgelio galą (linija ant linijos)
    _dup = {}
    for k_, r_ in enumerate(car_):
        for j_ in range(k_):
            q_ = car_[j_]
            if abs(q_["x0"] - r_["x0"]) < 1.5 and abs(q_["x1"] - r_["x1"]) < 1.5 and j_ not in _dup:
                _dup[k_] = j_; break
    _ncar = {j_: 1 + sum(1 for v_ in _dup.values() if v_ == j_) for j_ in range(len(car_))}
    for k_, r_ in enumerate(car_):
        if k_ in _dup:
            continue
        is_top = len(car_) > 1 and r_["y0"] <= min(q_["y0"] for q_ in car_) + 0.5   # v276: pagal tikrą padėtį
        if is_top:
            side = "dn" if blk_top else "up"
        else:
            side = "up" if (blk_bot and not blk_top) else "dn"
        if _ncar[k_] > 1:                                # dubliuotų grupė - iškeltinė iki artimiausio bėgelio krašto
            _grp = [car_[k_]] + [car_[i_] for i_, j_ in _dup.items() if j_ == k_]
            ey_ = RV(0, min(q_["y0"] for q_ in _grp))[1] if side == "up" else RV(0, max(q_["y1"] for q_ in _grp))[1]
        else:                                            # iškeltinė - nuo artimiausio matmeniui bėgelio krašto (ne per kito galą)
            _ov = [q_ for q_ in car_ if q_["x1"] > r_["x0"] and q_["x0"] < r_["x1"]]
            ey_ = RV(0, min(q_["y0"] for q_ in _ov))[1] if side == "up" else RV(0, max(q_["y1"] for q_ in _ov))[1]
        # v172 (Rytis: „matmenų linijos sugrūdamos viena ant kitos"): eilė - GLOBALI visam galiniam vaizdui; matmuo, kurio
        #  x ruožas persidengia su kitos grupės matmeniu toje pačioje eilėje, keliamas į kitą eilę (20 pt)
        _xa_, _xb_ = sorted((RV(r_["x0"], 0)[0], RV(r_["x1"], 0)[0]))
        row = used[side]
        while any(rw_ == row and _xa_ < xb2 + 6 and xa2 - 6 < _xb_ for (sd2, rw_, xa2, xb2) in DIM_ROWS if sd2 == side):
            row += 1
        used[side] = row + 1
        DIM_ROWS.append((side, row, _xa_, _xb_))
        UPR[0] = max(UPR[0], row + 1) if side == "up" else UPR[0]
        yy_ = (_vt - ROW[0] - 20 * row) if side == "up" else (_vb + ROW[0] + 20 * row)
        _rail_len_dim(r_, yy_, ey_, g, AV_, n=_ncar[k_])
        if side == "dn":
            CH_BOT[0] = max(CH_BOT[0], yy_ + 4)
    if g["name"] in ACR_GEO and ACR_GEO[g["name"]]["cuts"]:
        # v231 (Rytis 2026-10-14: „nėra nurodyti jungimai pagal medžiagos ilgį"): dalių grandinė virš galinio vaizdo -
        #  rėmo galai + jungtys J1.. ; dalis <= lakšto ilgis
        AG_ = ACR_GEO[g["name"]]
        _bx0, _, _bx1, _ = AG_["F"].bounds
        _xs = sorted(RV(x_, 0)[0] for x_ in [_bx0, _bx1] + [c_["x"] for c_ in AG_["cuts"]])
        _row = used["up"]
        while any(sd2 == "up" and rw_ == _row for (sd2, rw_, xa2, xb2) in DIM_ROWS):
            _row += 1
        DIM_ROWS.append(("up", _row, _xs[0], _xs[-1])); used["up"] = _row + 1; UPR[0] = max(UPR[0], _row + 1)
        _yy = _vt - ROW[0] - 20 * _row
        _xm = [x_ for x_ in _xs]
        _lens = [f"{abs(b_ - a_) / s2:.0f}" for a_, b_ in zip(_xm[:-1], _xm[1:])]
        hchain(_yy, _xs, [_vt] * len(_xs), [f"{l_} (part)" for l_ in _lens], size=K.F_DIM_FRAME)
        T((_xs[0] + _xs[-1]) / 2, _yy - 13, f"acrylic sheet {ACRY['sheet'][0]:g} x {ACRY['sheet'][1]:g} -> parts <= "
          f"{max(ACRY['sheet']) - 30:g}, puzzle joints J1..", 6.5, align="c", color=K.GREY)
    # kiti profiliai (statmenys, vidurinis, įstrižas) - žymos su išvadine
    tags_ = []
    for r_ in g["rails"]:
        if any(r_ is q for q in car_):
            continue
        # v191 (Rytis 2026-10-13): statmenų ilgis NEŽYMIMAS („tik apkrauna dokumentą, nauda 0") - užtenka rėmo aukščio
        #  matmens (viršus - apačia); statmenys pjaunami tarp bėgelių, ilgis aiškus iš rėmo matmenų
        if r_["kind"] == "v" and not spec.get("vert_labels"):      # originalo perdarymas su jo žymomis - "vert_labels": true
            continue
        if r_["kind"] == "h" and r_.get("support"):     # v299: papildomas bėgelis dalies ašyje - matmuo virš jo (ne išvadinė per rėmą)
            _ty = RV(0, r_["y0"])[1]
            _xa, _xb = sorted((RV(r_["x0"], 0)[0], RV(r_["x1"], 0)[0]))
            _av = [RV(xv, 0)[0] for q_ in g["rails"] if q_["kind"] in ("v", "d") for xv in (q_["x0"], (q_["x0"] + q_["x1"]) / 2, q_["x1"])]
            hdim(_xa, _xb, _ty - 7, f"{round(r_['len'])}", _ty, _ty, size=K.F_DIM_FRAME, avoid=_av)   # tekstas - ne ant statmens
            continue
        a_ = RV((r_["x0"] + r_["x1"]) / 2, (r_["y0"] + r_["y1"]) / 2)
        txt_ = f"{round(r_['len'])}" + {"h": "", "v": " vert.", "d": " diag."}.get(r_["kind"], "")
        w_ = K.pdfmetrics.stringWidth(txt_, "F", K.F_DIM_FRAME)
        tags_.append({"a": a_, "t": txt_, "x0": a_[0] - w_ / 2 - 3, "x1": a_[0] + w_ / 2 + 3,
                      "up": (bool(hs_) and r_["y1"] <= hs_[0]["y0"] + 1) or (blk_bot and not blk_top), "row": 0})
    # v172: kelios žymos toje pačioje vertikalėje (pvz. i taško laikiklis 130 + statmuo 226) - VIENA žyma, viena išvadinė
    _mg = []
    for t_ in sorted(tags_, key=lambda t_: t_["a"][0]):
        if _mg and abs(_mg[-1]["a"][0] - t_["a"][0]) < 1.0 and _mg[-1]["up"] == t_["up"]:
            k_ = _mg[-1]
            sfx = " vert." if t_["t"].endswith(" vert.") and k_["t"].endswith(" vert.") else ""
            k_["t"] = (k_["t"][:-len(sfx)] if sfx else k_["t"]) + " / " + t_["t"]
            if (t_["a"][1] < k_["a"][1]) == k_["up"]:
                k_["a"] = t_["a"]
            w_ = K.pdfmetrics.stringWidth(k_["t"], "F", K.F_DIM_FRAME)
            k_["x0"], k_["x1"] = k_["a"][0] - w_ / 2 - 3, k_["a"][0] + w_ / 2 + 3
            continue
        _mg.append(t_)
    tags_ = _mg
    UPR[0] = max(UPR[0], used["up"] + (1 if any(t_["up"] for t_ in tags_) else 0))
    for up_ in (True, False):
        side_ = sorted([t_ for t_ in tags_ if t_["up"] == up_], key=lambda t_: -t_["a"][0])
        for k_, t_ in enumerate(side_):
            x_ = t_["a"][0]; w_ = t_["x1"] - t_["x0"]
            t_["row"] = max([u_["row"] + 1 for u_ in side_[:k_] if x_ - 2 <= u_["a"][0] <= x_ + w_ + 6] + [0])
    for t_ in tags_:
        a_, up_ = t_["a"], t_["up"]
        base_ = ROW[0] + 20 * used["up" if up_ else "dn"]
        ty_ = (_vt - base_ - 12 * t_["row"]) if up_ else (_vb + base_ + 12 * t_["row"])
        w_ = t_["x1"] - t_["x0"]
        _cx = []
        for _cb, _ce in CEX:
            if _ce:
                _gg = _ce[3]; _dx = -_ce[2]
                _ed = min(RV(_gg["x0"], 0)[0], RV(_gg["x1"], 0)[0]) if _dx < 0 else max(RV(_gg["x0"], 0)[0], RV(_gg["x1"], 0)[0])
                _cx += [_ed + _dx * (10 + 9 * rk) for rk in range(3)]
        _left = any(a_[0] - 2 <= x_ <= a_[0] + w_ + 4 for x_ in _cx)
        # v157: žymos iš skirtingų grupių / krypčių nesidengia - kol kerta jau padėtą žymą, eilė toliau nuo vaizdo
        # v276 (ISO 128-22 / cad_matmenavimas_ISO.md 5 sk.): išvadinė ĮSTRIŽA (~70°), ne vertikali - nesusilieja su iškeltinėmis,
        #  matmens liniją kerta statmenai-įstrižai; lentynėlė ir tekstas - už matmenų eilių
        _off = lambda: (-1 if _left else 1) * 0.36 * abs(ty_ + 1.5 - a_[1])
        for _try in range(8):
            _ax = a_[0] + _off()
            _bx = (_ax - w_ - 2, _ax + 2) if _left else (_ax - 2, _ax + w_ + 2)
            if not any(_bx[0] < b_[1] and b_[0] < _bx[1] and abs(ty_ - b_[2]) < 11 for b_ in TAG_BOXES):
                break
            t_["row"] += 1
            ty_ = (_vt - base_ - 12 * t_["row"]) if up_ else (_vb + base_ + 12 * t_["row"])
        _ax = a_[0] + _off()
        TAG_BOXES.append((_bx[0], _bx[1], ty_))
        line(a_[0], a_[1], _ax, ty_ + 1.5, 0.3)
        line(_ax, ty_ + 1.5, _ax + (-w_ if _left else w_), ty_ + 1.5, 0.3)
        K.c.saveState(); K.c.setFillColor(black); K.c.circle(a_[0], K.Y(a_[1]), 1.0, stroke=0, fill=1); K.c.restoreState()
        T(_ax + (-2 if _left else 2), ty_, t_["t"], K.F_DIM_FRAME, align="r" if _left else "l")
        if not up_:
            CH_BOT[0] = max(CH_BOT[0], ty_ + 4)
    if g.get("zfr"):                                    # X Z juostos: tik plotis ir aukštis tarp centrų
        zr = g["zfr"]
        yc1, yc2 = zr["yA"] + zr["fp"] / 2, zr["yB"] + zr["fp"] / 2
        ey_ = RV(0, zr["yA"])[1]
        hdim(RV(zr["sx1"], 0)[0], RV(zr["sx0"], 0)[0], _vt - ROW[0], f"{zr['L']:.0f}  (Z{ZF['z']})", ey_, ey_,
             size=K.F_DIM_FRAME)
        xv_ = RV(g["x0"], 0)[0] + 14
        vchain(xv_, [RV(0, yc1)[1], RV(0, yc2)[1]], [RV(zr["sx0"], 0)[0]] * 2, [f"{round(yc2 - yc1)}"], K.F_DIM_FRAME)
    if len(hs_) >= 2 and not g["plate"]:               # bėgelių ašių atstumai - šone, už grupės
        ys_ = []
        for y_ in sorted((r_["y0"] + r_["y1"]) / 2 for r_ in hs_):   # v49: tame pačiame aukštyje - viena ašis (be „0")
            if not ys_ or y_ - ys_[-1] > 1:
                ys_.append(y_)
        xg = RV(g["x1"], 0)[0] - 14
        ex_ = RV(g["x1"], 0)[0]
        if (id(g), 1) in CAB_SIDE and (id(g), -1) not in CAB_SIDE:
            xg = RV(g["x0"], 0)[0] + 14; ex_ = RV(g["x0"], 0)[0]
        # v172: taškinė laido išvestis (raidėje) prie grandinės - grandinė perkeliama į kitą grupės pusę
        _pcx = [RV(c_["x"], c_["y"])[0] for c_ in CABLES if c_.get("point")]
        if any(abs(xg - px_) < 22 for px_ in _pcx):
            _alt = RV(g["x0"], 0)[0] + 14 if ex_ == RV(g["x1"], 0)[0] else RV(g["x1"], 0)[0] - 14
            if not any(abs(_alt - px_) < 22 for px_ in _pcx):
                ex_ = RV(g["x0"], 0)[0] if ex_ == RV(g["x1"], 0)[0] else RV(g["x1"], 0)[0]
                xg = _alt
        _yv = [RV(0, y)[1] for y in ys_]
        AXIS_X.append(xg)
        AXIS_TXT.extend(((a + b) / 2, K.pdfmetrics.stringWidth(f"{round(b1 - a1)}", "F", K.F_DIM_FRAME))
                        for a, b, a1, b1 in zip(_yv[:-1], _yv[1:], ys_[:-1], ys_[1:]))
        vchain(xg, [RV(0, y)[1] for y in ys_], [ex_] * len(ys_),
               [f"{round(b - a)}" for a, b in zip(ys_[:-1], ys_[1:])], K.F_DIM_FRAME)
r_first = next((r_ for g in groups if not g["plate"] for r_ in g["rails"]), None)
if r_first:
    _R5 = r_first                                  # v15: balionas 5 piešiamas PO laidų (išvadinė nekerta laido)
r_pl = next((r_ for g in groups if g["plate"] for r_ in g["rails"]), None)
if r_pl:   # plokštės (6+3) bėgelis su ausėlėmis
    a_ = RV(r_pl["x0"] + 20, r_pl["y0"])
    leader(a_[0], a_[1], RVX + rw + 18, RVY - 10, 9)
# bendri matmenys - tik priekiniame vaizde (Rytis patvirtino 2026-10-07); čia tik rėmas ir jo komponentai
CAB_Y = [max(RVY + rh, CH_BOT[0]) + 18]
BUS = 11                                                          # laidų eilių žingsnis (užrašas telpa)


def _edge(g, dirx):
    return min(RV(g["x0"], 0)[0], RV(g["x1"], 0)[0]) if dirx < 0 else max(RV(g["x0"], 0)[0], RV(g["x1"], 0)[0])


def _bolt(bx, by, col=HexColor("#D0021B")):
    bolt = [(0, -5.5), (2.4, -0.6), (0.6, -0.6), (2.0, 5.5), (-2.4, 0.6), (-0.6, 0.6)]
    poly([(bx + q[0], by + q[1]) for q in bolt], fill=col, stroke=col, lw=0.2)


def _wiggle(x0, y0, td, n=33):
    pts = [(x0 + td * (i * 1.4), y0 + 2.0 * math.sin(i / 8 * math.pi)) for i in range(n)]
    poly(pts, stroke=K.CABLE, lw=K.CABLE_LW, close=False)
    return pts[-1]


# v302 (Rytis 2026-10-16, Order 33580 Sheet 1: „jei naudojamas trafo box, tai punktyrinė laido linija nueina į trafo box,
#  kuris atvaizduojamas"): atskiros raidės (vienos linijos laidų išvestys) - linija tęsiama iki TRAFO BOX šalia galinio vaizdo
if SEP_END and TB and not (TB_ON and CEX):
    _trow = next((r_ for r_ in spec["bom"] if str(r_[1]).lower().startswith(("trafo", "transformer"))), None)
    _tfin = str(_trow[3]) if _trow else ""
    _tcol = HexColor(K.code_hex(_tfin) or (K.ralhex(_tfin) if re.search(r"\d{4}", _tfin) else "#8A8A8A"))
    _tlab = ", ".join((["PWM"] if TB.get("pwm") else []) + ([_tfin] if _tfin.strip() not in ("", "-", "?") else []))
    _tw = max(80, K.pdfmetrics.stringWidth("TRAFO BOX", "FB", K.F_INFO + 1) + 16, K.pdfmetrics.stringWidth(_tlab, "F", K.F_INFO) + 12)
    _xe, _ye, _yl = SEP_END
    _xb = _xe + 18
    _yb = _yl + 16
    line(_xe, _ye, _xb, _ye, 0.4, HexColor("#D0021B"), dash=([4, 2], 0))
    line(_xb, _ye, _xb, _yb, 0.4, HexColor("#D0021B"), dash=([4, 2], 0))
    rect(_xb - _tw / 2, _yb, _tw, 30, fill=_tcol, lw=K.HAIR)
    _tc2 = white if (0.299 * _tcol.red + 0.587 * _tcol.green + 0.114 * _tcol.blue) < 0.55 else black
    T(_xb, _yb + 12, "TRAFO BOX", K.F_INFO + 1, font="FB", align="c", color=_tc2, auto_red=False)
    T(_xb, _yb + 23, _tlab, K.F_INFO, align="c", color=_tc2, auto_red=False)
    if _trow and str(_trow[0]).strip():
        leader(_xb + _tw / 2 - 4, _yb + 8, _xb + _tw / 2 + 20, _yb + 2, str(_trow[0]))
    line(_xb, _yb + 30, _xb, _yb + 38, K.CABLE_LW, K.CABLE)
    _ex, _ey = _wiggle(_xb, _yb + 38, 1, 25)
    _bolt(_ex + 6, _ey)
    TL(_ex + 11, _ey + 3, f"{TB.get('mains', '230V')}", K.F_INFO + 1, align="l", color=K.CABLE)
    print(f"  atskiros raidės: laidų linija -> TRAFO BOX ({_tlab}) (v302)")

_ranks = {}
_bottom = [CAB_Y[0]]
if TB_ON and CEX:
    # v205 (Rytis 2026-10-14): PWM naudojamas ne visur - ant dėžės rašomas TIK kai nurodyta (spec trafo_box.pwm: true)
    _tbt = (TB or {}).get("label") or ", ".join(([ "PWM"] if (TB or {}).get("pwm") else [])
                                                 + ([_ral_txt(RAIL['ral'])] if not K.unk(RAIL.get("ral", "")) else []))
    TBW = max(80, K.pdfmetrics.stringWidth("TRAFO BOX", "FB", K.F_INFO + 1) + 16,
              K.pdfmetrics.stringWidth(_tbt, "F", K.F_INFO) + 12)
    # laidų nuleidimo vietos - už grupės krašto, link dėžės; tarp dviejų artimų grupių - tarpo trečdaliuose
    # nuleidimai tarpuose tarp grupių (Rytis 2026-10-08): tame pačiame tarpe - iš kairės grupės ateinantys laidai
    # kairėje (žemesnis išėjimas - arčiau grupės), iš dešinės - dešinėje; tolygiai, >= 7 pt - laidai nesikerta
    _drops, _gaps = {}, {}
    for cb, ce in CEX:
        if ce[4] is None and (ce[3]["plate"] or ce[3]["spec"].get("no_rails")):
            _drops[id(cb)] = RV(ce[0], 0)[0]; continue
        d_ = -ce[2]; e_ = _edge(ce[3], d_)
        nb_ = [_edge(g2, -d_) for g2 in groups if g2 is not ce[3] and (_edge(g2, -d_) - e_) * d_ > 0]
        o_ = min(nb_, key=lambda v: abs(v - e_)) if nb_ else e_ + d_ * 1e4
        key_ = (round(min(e_, o_)), round(max(e_, o_)))
        _gaps.setdefault(key_, []).append((cb, ce, d_))
    # v13 (Rytis 2026-10-08): laidas išeina iš rėmo kliento nurodyta kryptimi ("out": up|down|left|right, priekio
    # vaizdo kryptimis) ir eina APLINK iškabą (šoninė juosta už gabarito) iki dėžės - per raides nekerta
    _OUT, _pre = {}, {}
    _gl = [g2 for g2 in groups if g2["letters"]]
    _SX0, _SX1 = min(_edge(g2, -1) for g2 in _gl), max(_edge(g2, 1) for g2 in _gl)
    _lanes = {-1: [], 1: []}
    for cb, ce in CEX:
        o_ = ((ce[3]["spec"].get("cable") or {}).get("out"))
        if not o_:
            continue
        px_, py_ = RV(ce[0], ce[1])
        _OUT[id(cb)] = o_
        if o_ == "down":
            _drops[id(cb)] = px_; _pre[id(cb)] = [(px_, py_)]
            _gaps = {k_: [q for q in v_ if q[0] is not cb] for k_, v_ in _gaps.items()}
            continue
        sd_ = {"left": 1, "right": -1}.get(o_) or (-1 if px_ - _SX0 < _SX1 - px_ else 1)   # galinis vaizdas - veidrodis
        _lanes[sd_].append((cb, ce, px_, py_))
        _gaps = {k_: [q for q in v_ if q[0] is not cb] for k_, v_ in _gaps.items()}
    _yu0 = _vt - ROW[0] - 20 * max(UPR[0], 1) + 6
    for sd_, lst in _lanes.items():
        edge_ = _SX0 if sd_ < 0 else _SX1
        lst.sort(key=lambda q: abs(q[2] - edge_))
        for k_, (cb, ce, px_, py_) in enumerate(lst):
            xl_ = edge_ + sd_ * (12 + 7 * k_)
            _drops[id(cb)] = xl_
            if _OUT[id(cb)] == "up":
                yu_ = _yu0 - 7 * k_
                _pre[id(cb)] = [(px_, py_), (px_, yu_), (xl_, yu_)]
            else:
                _pre[id(cb)] = [(px_, py_), (xl_, py_)]
    _gaps = {k_: v_ for k_, v_ in _gaps.items() if v_}
    for (gl, gr), lst in _gaps.items():
        yof = lambda q: RV(0, q[1][1])[1]
        L_ = sorted([q for q in lst if q[2] > 0], key=lambda q: -yof(q))        # iš kairės grupės
        R_ = sorted([q for q in lst if q[2] < 0], key=yof)                        # iš dešinės grupės
        seq = L_ + R_
        n_ = len(seq)
        if gr - gl >= 10 * (n_ + 1) or gr - gl > 5e3:
            for k_, q in enumerate(L_):
                _drops[id(q[0])] = gl + 10 + 7 * k_
            for k_, q in enumerate(reversed(R_)):
                _drops[id(q[0])] = gr - 10 - 7 * k_
        else:
            for k_, q in enumerate(seq):
                _drops[id(q[0])] = gl + (gr - gl) * (k_ + 1) / (n_ + 1)
    xs_ = sorted(_drops.values())
    if xs_[-1] - xs_[0] >= TBW + 60:
        bxc = (xs_[0] + xs_[-1]) / 2
        if any(abs(x_ - bxc) < TBW / 2 + 25 for x_ in xs_):          # dėžė - didžiausiame tarpe
            prs_ = max(zip(xs_[:-1], xs_[1:]), key=lambda q: q[1] - q[0])
            bxc = (prs_[0] + prs_[1]) / 2
    else:
        # v15: dėžė - po iškaba (galinio vaizdo ribose), į iškabos vidų nuo laido nuleidimo; nelenda į kitus vaizdus
        if (xs_[0] + xs_[-1]) / 2 < RVX + rw / 2:
            bxc = xs_[-1] + TBW / 2 + 24
        else:
            bxc = xs_[0] - TBW / 2 - 24
    bx0, bx1 = bxc - TBW / 2, bxc + TBW / 2
    sides_ = {-1: [], 1: []}
    for cb, ce in CEX:
        sides_[1 if _drops[id(cb)] > bxc else -1].append(cb)
    _entry = {}
    for sd, lst in sides_.items():
        lst.sort(key=lambda cb: abs(_drops[id(cb)] - bxc))          # artimiausias - aukščiausia eilė, vidinis įėjimas
        for k_, cb in enumerate(lst):
            _ranks[id(cb)] = k_
        for k_, cb in enumerate(reversed(lst)):                       # tolimiausias - kraštinis įėjimas
            _entry[id(cb)] = (bx0 + 10 + 12 * k_) if sd < 0 else (bx1 - 10 - 12 * k_)
    nmax = max(_ranks.values()) + 1
    by0 = CAB_Y[0] + BUS * (nmax - 1) + 12
    _bx_real = PW - (bxc - RVX) / s2                                 # dėžės vieta (už iškabos, apačioje)
    for cb, ce in CEX:                    # Rytis 2026-10-08: visi laidai 5 m (spec trafo_box.cable_len_m); None - skaičiuoti
        L_ = TB_LEN if TB_LEN else math.ceil(((abs(ce[0] - _bx_real) + abs(PH - ce[1])) / 1000 + TB_RES) * 2) / 2
        cb["len_m"] = L_; cb["label"] = f"{L_:g} m"
    TBH = 32
    for cb, ce in CEX:
        px, py = RV(ce[0], ce[1])
        xo, xe = _drops[id(cb)], _entry[id(cb)]
        yb = CAB_Y[0] + BUS * _ranks[id(cb)]
        K.c.saveState(); K.c.setFillColor(K.CABLE); K.c.circle(px, K.Y(py), 1.8, stroke=0, fill=1); K.c.restoreState()
        _pp = _pre.get(id(cb)) or [(px, py), (xo, py)]
        K.cable_line(_pp + [(xo, yb), (xe, yb), (xe, by0)])
        txt_ = f"{cb['voltage']}, {cb['label']}"
        tw_ = K.pdfmetrics.stringWidth(txt_, "F", K.F_INFO + 1)
        sd = 1 if xo > bxc else -1
        if abs(xo - xe) >= tw_ + 8:
            TL((xo + xe) / 2, yb - 3, txt_, K.F_INFO + 1, align="c", color=K.CABLE)
        else:                                                          # trumpa atkarpa - už nuleidimo linijos
            TL(xo + sd * 3, yb - 3, txt_, K.F_INFO + 1, align="l" if sd > 0 else "r", color=K.CABLE)
    _TBC = HexColor("#8A8A8A") if RAIL_ACR else RAILC          # v229: akrilinis rėmas - trafo dėžės spalva nežinoma (pilka)
    rect(bx0, by0, TBW, TBH, fill=_TBC, lw=K.HAIR)          # v63: hairline                                  # trafo dėžė - rėmo spalva
    _tc = white if (0.299 * _TBC.red + 0.587 * _TBC.green + 0.114 * _TBC.blue) < 0.55 else black
    T(bxc, by0 + 13, "TRAFO BOX", K.F_INFO + 1, font="FB", align="c", color=_tc, auto_red=False)
    T(bxc, by0 + 24, _tbt, K.F_INFO, align="c", color=_tc, auto_red=False)
    _tbpos = next((str(r_[0]) for r_ in spec["bom"] if str(r_[1]).lower().startswith(("trafo", "transformer"))),
                  next((str(r_[0]) for r_ in spec["bom"] if "trafo" in str(r_[1]).lower()), ""))   # v205: ne „... -> trafo box" laido eilutė
    if _tbpos:
        leader(bx0 + 4, by0 + TBH - 4, bx0 - 14, by0 + TBH + 10, _tbpos)
    # maitinimas 230 V - iš dėžės apačios
    my_ = by0 + TBH
    line(bxc, my_, bxc, my_ + 8, K.CABLE_LW, K.CABLE)
    ex, ey = _wiggle(bxc, my_ + 8, 1, 25)
    _bolt(ex + 6, ey)
    _ml = (TB or {}).get('mains_len')                # Rytis 2026-10-08: prie dėžės ilgio nereikia - tik nuoroda 220V
    TL(ex + 11, ey + 3, f"{(TB or {}).get('mains', '220V')}" + (f", {_ml}" if _ml else ""), K.F_INFO + 1, align="l", color=K.CABLE)
    _bottom[0] = ey + 10
else:
    def draw_cable(px, py, dirx, cb, g, rank):
        xo = _edge(g, dirx) + dirx * (10 + 9 * rank)
        yd = CAB_Y[0] + 13 * rank
        K.c.saveState(); K.c.setFillColor(black); K.c.circle(px, K.Y(py), 1.3, stroke=0, fill=1); K.c.restoreState()
        K.cable_line([(px, py), (xo, py), (xo, yd)])
        td = -dirx
        ex, ey = _wiggle(xo, yd, td)
        bx = ex + td * 6
        _bolt(bx, ey)
        v_ = cb["voltage"] if not K.unk(cb["voltage"]) else "___ V"
        TL(bx + td * 5, ey + 3, f"{v_}, {cb['label']}", K.F_INFO + 1, align="l" if td > 0 else "r")
        _bottom[0] = max(_bottom[0], ey + 6)

    for cb, ce in sorted(CEX, key=lambda q: -(q[1][1] if q[1] else 0)):
        if ce:
            key_ = ("side", ce[2])
            _ranks[id(cb)] = _ranks.get(key_, 0)
            _ranks[key_] = _ranks.get(key_, 0) + 1
    _pt_rank = [0]
    for cb, ce in CEX:
        if cb.get("point"):
            # v169 (Rytis 2026-10-13: „laikytis org faile numatytų laido išvesčių"): išvestis TIKSLIAI originalo vietoje
            #  (taškas raidėje virš rėmo), laidas į viršų; up_mm - iki užrašo (tarp eilučių), kitaip - virš galinio vaizdo
            px_, py_ = RV(cb["x"], cb["y"])
            K.c.saveState(); K.c.setFillColor(K.CABLE); K.c.circle(px_, K.Y(py_), 1.6, stroke=0, fill=1); K.c.restoreState()
            if cb.get("up_mm") is not None:
                yt_ = py_ - cb["up_mm"] * s2
                for _ym, _tw in AXIS_TXT:                  # v172: horizontali atkarpa - ne per grandinės užrašą
                    if _ym - _tw / 2 - 4 < yt_ < _ym + _tw / 2 + 4:
                        yt_ = _ym + _tw / 2 + 5 if yt_ > _ym else _ym - _tw / 2 - 5
            else:
                yt_ = _vt - ROW[0] - 20 * max(UPR[0], 1) - 8 - 12 * _pt_rank[0]
                _pt_rank[0] += 1
            td = {"left": -1, "right": 1}.get(cb.get("side")) or (-1 if px_ < RVX + rw / 2 else 1)   # galinio vaizdo kryptimi
            if cb.get("up_mm") is not None:          # v172: tarp eilučių - horizontaliai UŽ vaizdo krašto, užrašas ne ant rėmo
                xo_ = min([RVX - 8] + [ax_ - 22 for ax_ in AXIS_X]) if td < 0 else \
                    max([RVX + rw + 8] + [ax_ + 22 for ax_ in AXIS_X])
                K.cable_line([(px_, py_), (px_, yt_), (xo_, yt_)])
                ex, ey = _wiggle(xo_, yt_, td, n=18)
            else:
                K.cable_line([(px_, py_), (px_, yt_)])
                ex, ey = _wiggle(px_, yt_, td, n=18)
            _bolt(ex + td * 6, ey)
            v_ = cb["voltage"] if not K.unk(cb["voltage"]) else "___ V"
            TL(ex + td * 11, ey + 3, f"{v_}, {cb['label']}", K.F_INFO + 1, align="l" if td > 0 else "r")
            continue
        if ce:
            x_, y_ = RV(ce[0], ce[1])
            draw_cable(x_, y_, -ce[2], cb, ce[3], _ranks[id(cb)])
            continue
        cx_, cy_ = RV(cb["x"], cb["y"])
        r_ = max(2.2, 5.5 * s2)
        K.c.saveState(); K.c.setFillColor(white); K.c.setStrokeColor(black); K.c.setLineWidth(0.5)
        K.c.circle(cx_, K.Y(cy_), r_, stroke=1, fill=1); K.c.restoreState()
        line(cx_ - r_ - 2, cy_, cx_ + r_ + 2, cy_, 0.2); line(cx_, cy_ - r_ - 2, cx_, cy_ + r_ + 2, 0.2)
        v_ = cb["voltage"] if not K.unk(cb["voltage"]) else "___ V"
        TL(cx_, cy_ + r_ + 9, f"D11 cable exit, {v_}, {cb['label']}", K.F_INFO + 1, align="c")
    if not CABLES and spec.get("letters_power") != "per_letter":    # v295: per_letter - laidų legenda jau yra (ne tuščia eilutė)
        T(RVX, min(RVY - 34, RVY - ROW[0] - 20 * max(UPR[0], 1) - 6), spec.get("power_note", "Power / PSU / cable exits:"), K.F_INFO + 1)   # v29 / v276: virš matmenų eilių: pvz. „NO LIGHTS - no cable / PSU"
for xj_, lj_ in JOINTS:
    _joint(RV(xj_, 0)[0], RVY - 8, RVY + rh + 8, lj_)
for _sx, _sy, _ in P10N_STUDS:                           # v249: ilgasriegiai Alu dugnelyje
    _cc = RV(_sx, _sy)
    K.circle(_cc[0], _cc[1], max(1.2, P10_ROD["d"] / 2 * s2), fill=white, lw=0.3)
    line(_cc[0] - 3, _cc[1], _cc[0] + 3, _cc[1], 0.2); line(_cc[0], _cc[1] - 3, _cc[0], _cc[1] + 3, 0.2)
VIEW_BOX["rear"] = (RVX, RVY, RVX + rw, RVY + rh)
_callouts("rear", RV)
if WALL_DIM:                                               # v299: sienos rėmo ilgis - po raidžių rėmo matmenimis
    _wls = sorted(set(round(b - a) for a, b in WALL_DIM))
    _xa, _xb = min(a for a, b in WALL_DIM), max(b for a, b in WALL_DIM)
    _yb = max(VIEW_BOX["rear"][3], max(RV(0, r_["y1"])[1] for g in groups for r_ in g["rails"])) + 30
    hdim(RV(_xb, 0)[0], RV(_xa, 0)[0], _yb, " / ".join(str(v) for v in _wls) + f"  (wall {_PFX}{RAIL['size']})",
         RV(0, max(r_["y1"] for g in groups for r_ in g["rails"] if r_["kind"] == "h") + 4)[1],
         RV(0, max(r_["y1"] for g in groups for r_ in g["rails"] if r_["kind"] == "h") + 4)[1], size=K.F_DIM_FRAME)
if WALL_BAL:                                               # v299: sienos rėmas (punktyras) - BOM pozicija pagal spec lhang.balloons
    K.balloon_auto(WALL_BAL[0], WALL_BAL[1], str(spec.get("lhang", {}).get("balloons", {}).get("7", 7)), avoid=[VIEW_BOX["rear"]])
if LEDF:
    for _bx, _by, _bn in LED_BALLOONS:                    # v176: originalo LED / PSU balionai - už LED vaizdo
        K.balloon_auto(_bx, _by, _bn, avoid=[VIEW_BOX_L])
# v111 (Rytis 2026-10-12, etalonas EXTRA 223315 lapas 1): GALINIAME VAIZDE virš kiekvienos šviečiančios grupės - kokie LED
#  dedami (spalva / temperatūra; plokštei X - vidus ir galas). spec grupės "led": "White LED modules, 6500K" arba eilučių
#  sąrašas; nenurodyta šviečiančiai grupei - perspėjimas (neišgalvoti).
LED_GAP = spec.get("led_label_gap_pt", 26)
LED_BUSY = []                                      # balionas 5 ir laidai - ne per LED užrašus
for g in groups:
    if FRONT == "P1" or g["spec"].get("lit") is False or not g["letters"]:
        continue
    led_ = g["spec"].get("led")
    if not led_:
        print(f"  ! {g['name']}: LED tipas nenurodytas (spec grupės \"led\") - galiniame vaizde nepažymėta")
        continue
    lines_ = [led_] if isinstance(led_, str) else list(led_)
    bbs_ = [o["bb"] for o in g["letters"]] + ([g["plate"]["bb"]] if g["plate"] else [])
    gx0_, gx1_, gy0_ = min(b_[0] for b_ in bbs_), max(b_[2] for b_ in bbs_), min(b_[1] for b_ in bbs_)
    xc_ = (RV(gx0_, gy0_)[0] + RV(gx1_, gy0_)[0]) / 2
    sz_ = K.F_INFO + 2
    # virš visų galinio vaizdo matmenų eilučių (bėgelių ilgiai), kad nekirstų matmenų linijų
    if MOUNTING != "none":
        y_ = min(_vt - ROW[0] - 20 * max(UPR[0], 1) + 2, RV(0, gy0_)[1] - LED_GAP) - (len(lines_) - 1) * (sz_ + 2.5)
    else:                                          # v295: be rėmo (atskiros raidės) - PO grupe, ne prie FRONT VIEW pavadinimo
        y_ = max(RV(0, b_[3])[1] for b_ in bbs_) + 16
    w_ = max(K.pdfmetrics.stringWidth(str(ln_), "F", sz_) for ln_ in lines_)
    LED_BUSY.append((xc_ - w_ / 2 - 4, xc_ + w_ / 2 + 4))
    for i_, ln_ in enumerate(lines_):
        TL(xc_, y_ + i_ * (sz_ + 2.5), ln_, sz_, align="c")
if r_first:
    _hs1 = sorted([r_ for r_ in groups[0]["rails"] if r_["kind"] == "h"] or [r_first], key=lambda r_: r_["y0"])
    _top_r = min((r_ for g2 in groups if not g2["plate"] for r_ in g2["rails"] if r_["kind"] == "h"),
                 key=lambda r_: r_["y0"], default=r_first)
    _busy = []                                     # laidų atkarpų x intervalai (galinis vaizdas)
    _busy += LED_BUSY                              # v111
    for _cb in CABLES:                             # v169: taškinės išvestys ir jų užrašai - ne po balionu
        if _cb.get("point"):
            _px = RV(_cb["x"], _cb["y"])[0]
            _sd = {"left": -1, "right": 1}.get(_cb.get("side")) or (-1 if _px < RVX + rw / 2 else 1)
            _busy.append((min(_px, _px + _sd * 110) - 12, max(_px, _px + _sd * 110) + 12))
    for _cb, _ce in CEX:
        _pts = (_pre.get(id(_cb)) if TB_ON and CEX else None) or []
        _xs = [q[0] for q in _pts] + ([_drops[id(_cb)]] if TB_ON and CEX and id(_cb) in _drops else [])
        if _xs:
            _busy.append((min(_xs) - 10, max(_xs) + 10))
    _xa, _xb = sorted((RV(_top_r["x0"], 0)[0], RV(_top_r["x1"], 0)[0]))
    _cands = [_xa + (_xb - _xa) * f_ for f_ in (0.25, 0.75, 0.2, 0.8, 0.3, 0.7, 0.12, 0.88, 0.5, 0.95, 0.05, 0.98)]   # v160: + galai   # v50: ne per bėgelio ilgio užrašą (centre)
    _tcx = FVX + fw / 2                            # v61: balionas ne ant priekio vaizdo pavadinimo / mastelio
    _x5 = next((x_ for x_ in _cands if not any(a_ <= x_ <= b_ for a_, b_ in _busy) and abs(x_ + 22 - _tcx) > 75),
               next((x_ for x_ in _cands if not any(a_ <= x_ <= b_ for a_, b_ in _busy)), _cands[0]))
    _y5 = RV(0, (_top_r["y0"] + _top_r["y1"]) / 2)[1]
    _yb5 = max((_vt - ROW[0] - 20 * max(UPR[0], 1) + 6) - 7 * max(1, len(CEX)) - 14, K.IY0 + 14)
    if not any(b_[0] - 30 < _x5 < b_[1] + 30 and b_[2] < _vt for b_ in TAG_BOXES):   # v160: virš balionui žymų nėra - arčiau vaizdo
        _x5, _yb5 = (_xb - 40 if RAIL_ACR else _xb - 8), None                  # balionas dešinėje už galinio vaizdo, bėgelio aukštyje
    _dx5 = 22                                      # v50: išvadinė nekerta laido - pasvyra nuo artimiausio laido
    if any(_x5 < a_ <= _x5 + 60 for a_, b_ in _busy):
        _dx5 = -22
    K.balloon_auto(_x5, _y5, spec.get("section_labels", {}).get("5", _rail_pos()), avoid=[(RVX, RVY, RVX + rw, RVY + rh)])
_rty, _rtx = max(RVY + rh + 56, CH_BOT[0] + 26, _bottom[0] + 24), RVX + rw / 2
if _rty + 4 + K.F_SCALE * 1.25 > K.VIEW_BOT and TB_ON and CEX:      # v44: netelpa po dėže - šalia trafo dėžės
    _rtw = K.pdfmetrics.stringWidth("REAR VIEW (MIRRORED)", "FB", K.F_VIEW) / 2 + 30
    _rtx = bx0 - 24 - _rtw if bx0 - 24 - 2 * _rtw > K.IX0 else bx1 + 24 + _rtw
    _rty = by0 + 12
if _rty + 4 + K.F_SCALE * 1.25 > K.VIEW_BOT:      # v157: netelpa po vaizdu (laidų / žymų eilės) - į laisvą dešinę pusę virš juostos
    _rty = K.VIEW_BOT - 4 - K.F_SCALE * 1.25 - 3
    _rtx = RVX + rw * 0.72
view_title(_rtx, _rty, "REAR VIEW (MIRRORED)", f"SCALE 1:{SC2}  |  true view from the back")
for _gi, (_gn, AG) in enumerate(ACR_GEO.items()):      # v229: akrilinio rėmo pastaba
    T(_rtx, _rty + 26 + 10 * _gi, f"frame: clear acrylic {ACRY['thk']:g} mm, {len(AG['parts'])} parts "
      f"({' + '.join(f'{p_.bounds[2] - p_.bounds[0]:.0f}' for p_ in AG['parts'])}) + {len(AG['vparts'])} verticals (separate, puzzle into rails), "
      f"puzzle joints (clearance {ACRY['joint_clear']:g}) "
      f"under letter (J1..), {len(AG['holes'])} x Ø{ACRY['hole_d']:g} between letters, "
      f"cable groove {(ACRY.get('groove') or {}).get('w', '?')} x {(ACRY.get('groove') or {}).get('d', '?')} deep (back), DXF", 7, align="c", color=K.GREY)

# ============================================================ DETAIL B - P6+3 ant plokštės (tipinis pjūvis)
if HAS_D and "D" in POS:
    dx, dy, dw, dh = POS["D"]
    _PRF = None                                    # v44: vientisas rėmas - bėgelių padėtys kaip priekio vaizde
    if OF:
        _gp = next((g for g in groups if g["plate"] and g["name"] == OF["plate"]), None)
        _gr = next((g for g in groups if g["name"] == OF["rails"]), None)
        if _gp and _gr:
            _PRF = sorted(((r_["y0"] + r_["y1"]) / 2 - _gp["ly0"]) / (_gp["ly1"] - _gp["ly0"])
                          for r_ in _gr["rails"] if r_["kind"] == "h" and r_["x0"] < _gp["x1"] and r_["x1"] > _gp["x0"])
            print("  DETAIL A bėgelių padėtys (dalis nuo X viršaus):", [round(f_, 2) for f_ in _PRF])
    if FRONT == "P1":
        K.p1_typical(dx, dy - 12, dw, dh - 30, depth, variant="plate", numbers={"plate": 8, "spacer": 7, "prail": 5},
                     boxed=False, plate_z=bool(GZ), plate_rail=RAIL["size"] if OF else None, spacer_mm=PLATE["gap_mm"], plate_rail_f=_PRF, rail_kind="sq" if RAIL_SQ else "u")
    else:
        K.p6_typical(dx, dy - 12, dw, dh - 30, depth, variant="plate", show_magnifier=False, front=FRONT,
                     numbers={"plate": 8, "spacer": 7, "prail": 5 if OF else 9}, boxed=False,
                     plate_rail=(PRAIL or {}).get("size") or (RAIL["size"] if OF else None), plate_z=bool(GZ), plate_rail_f=_PRF,
                     rail_kind="sq" if str((PRAIL or RAIL).get("type", "u")).lower().startswith(("sq", "box", "kv")) else "u")
    view_title(dx + dw / 2, dy + dh - 14, "DETAIL A - SECTION",
               ("X - P1 ON ALU SHEET" if FRONT == "P1" else "X - P6+3 ON ALU SHEET") + (" + Z HANG FRAME" if GZ else "") + (" ON RAILS" if OF else "") + "  |  SCHEMATIC")

# ============================================================ WALLFRAME - sieninis rėmas X apskritimui (atskira detalė)
# Rytis 2026-10-07: Z-Z pjūvio NEREIKIA; apskritimo Z juostų matmenys - galiniame vaizde; čia tik suvirintas
# sieninis rėmas (Z + stačiakampis profilis) su savo matmenimis.
if GZ and "Z" in POS:
    zx, zy, zw_, zh_ = POS["Z"]
    zr = GZ["zfr"]
    sz_ = MM / NZ
    ZT_, ZF_, TB_ = ZF["zt"], ZF["zf"], ZF["tb"]
    FS7 = K.F_DIM_FRAME
    fx_, fy_ = zx + 26, zy + 24
    W_, LT_ = zr["W"], zr["LT"]

    def FVz(x, y):
        return fx_ + x * sz_, fy_ + y * sz_
    K.set_view(True)
    fp_ = 2 * ZF_ - ZT_
    for y0_ in (0, LT_ - fp_):
        a_, b_ = FVz(TB_, y0_), FVz(W_ - TB_, y0_ + ZF_ - ZT_)
        rect(a_[0], a_[1], b_[0] - a_[0], b_[1] - a_[1], fill=K.mix(ZFC, 1.12), lw=K.HAIR)
        a_, b_ = FVz(TB_, y0_ + ZF_ - ZT_), FVz(W_ - TB_, y0_ + fp_)
        rect(a_[0], a_[1], b_[0] - a_[0], b_[1] - a_[1], fill=ZFC, lw=K.HAIR)
    for x0_ in (0, W_ - TB_):
        a_, b_ = FVz(x0_, 0), FVz(x0_ + TB_, LT_)
        rect(a_[0], a_[1], b_[0] - a_[0], b_[1] - a_[1], fill=K.mix(ZFC, 0.9), lw=K.HAIR)
    K.set_view(False)
    hchain(FVz(0, 0)[1] - 10, [FVz(TB_, 0)[0], FVz(W_ - TB_, 0)[0]], [FVz(0, 0)[1]] * 2, [f"{zr['LF']:.0f}"], FS7)
    hdim(FVz(0, 0)[0], FVz(W_, 0)[0], FVz(0, LT_)[1] + 12, f"{W_:.0f}", FVz(0, LT_)[1], FVz(0, LT_)[1], size=FS7)
    vchain(FVz(W_, 0)[0] + 12, [FVz(0, y)[1] for y in (0, fp_, LT_ - fp_, LT_)], [FVz(W_, 0)[0]] * 4,
           [f"{fp_:.0f}", f"{LT_ - 2 * fp_:.0f}", f"{fp_:.0f}"], FS7)
    vchain(FVz(W_, 0)[0] + 30, [FVz(0, 0)[1], FVz(0, LT_)[1]], [FVz(W_, 0)[0]] * 2, [f"{LT_:.0f}"], FS7)
    leader(*FVz(W_ * 0.2, fp_ * 0.7), FVz(0, 0)[0] - 14, FVz(0, LT_ * 0.3)[1], 12, 6)   # žemiau - nelenda į kaimyninio vaizdo pavadinimą
    leader(*FVz(TB_ / 2, LT_ * 0.6), FVz(0, 0)[0] - 14, FVz(0, LT_ * 0.8)[1], 13, 6)
    view_title(fx_ + W_ * sz_ / 2, zy + zh_ - 16, "WALLFRAME X", f"1:{NZ} | Z {ZF['z']} + {ZF['tube']}, welded")

# ============================================================ 3D VIEW
ix, iy, iw, ih = POS["I"]
if LEDF:                                                   # v162: po galinio vaizdo pavadinimu (laidų užrašai jį nustumia žemyn)
    _d3 = max(0.0, _rty + 4 + K.F_SCALE * 1.25 + 8 - iy)
    iy, ih = iy + _d3, ih - _d3
ih -= 30
NOTE3D = spec.get("note_3d")                              # v251: aiški nuoroda 3D vaizde (pvz. dažymo sluoksniai)
if NOTE3D:
    iy, ih = iy + 26, ih - 26
up = lambda geom: __import__("shapely.affinity", fromlist=["scale"]).scale(geom, 1, -1, origin=(0, PH / 2))
fit = [(x, y, 0) for x in (-_WM, PW + _WM) for y in (-_WM * 0.8, PH + _WM * 0.8)] + \
      [(x, y, ZMAX) for x in (0, PW) for y in (0, PH)]
V3.fit(fit, (ix, iy, iw, ih))
objs = []
for g in groups:
    for r_ in g["rails"]:
        _d3, _t3 = g["rsz"]["depth"], _rail_t(g["rsz"])
        if RAIL_SQ or r_["kind"] == "d":
            objs.append((up(Polygon(r_["poly"])), 0, _d3, rcol(g), K.mix(rcol(g), 1.05)))
        else:                                           # v47: U 3D - sienelė prie raidžių + 2 lentynos į sieną
            objs.append((up(Polygon(r_["poly"])), _d3 - _t3, _d3, rcol(g), K.mix(rcol(g), 1.05)))
            if r_["kind"] == "h":
                fl_ = [sbox(r_["x0"], r_["y0"], r_["x1"], r_["y0"] + _t3), sbox(r_["x0"], r_["y1"] - _t3, r_["x1"], r_["y1"])]
            else:
                fl_ = [sbox(r_["x0"], r_["y0"], r_["x0"] + _t3, r_["y1"]), sbox(r_["x1"] - _t3, r_["y0"], r_["x1"], r_["y1"])]
            for f_ in fl_:
                objs.append((up(f_), 0, _d3 - _t3, rcol(g), K.mix(rcol(g), 0.92)))
    for fp_ in g["fplates"]:                            # ausėlės (L vertikali kojelė sienos plokštumoje)
        px_, py_, ph_, _ = ear4(g, fp_)
        objs.append((up(sbox(px_, py_, px_ + g["fpl_sz"], py_ + ph_)), 0, 2, K.mix(rcol(g), 0.85), K.mix(rcol(g), 0.85)))
    if g["plate"]:
        objs.append((up(g["plate"]["geom"]), PZ0, PZ0 + PLATE["thk"], PLATEC, PLATEC))
    zr = g.get("zfr")
    if zr:
        for yy in (zr["yA"], zr["yB"]):
            objs.append((up(sbox(zr["sx0"], yy, zr["sx1"], yy + zr["fp"])), 0, ZF["zw"], ZPC, ZPC))
            objs.append((up(sbox(zr["fx0"] + ZF["tb"], yy + ZF["zf"], zr["fx1"] - ZF["tb"], yy + ZF["zf"] + zr["fp"])), 0,
                         ZF["zw"], ZFC, ZFC))
        for x0 in (zr["fx0"], zr["fx1"] - ZF["tb"]):
            objs.append((up(sbox(x0, zr["fy0"], x0 + ZF["tb"], zr["fy1"])), 0, ZF["tb"], ZFC, ZFC))
for g in groups:
    z0 = Z_PLATE_L if g["plate"] else g["spec"].get("z0", Z_RAIL_L)
    gd_ = g["spec"].get("depth_mm", depth)
    for o in g["letters"]:
        if P6_REAL(g):                                   # v59: realus P6 - korpusas -1,5 + stiklas 3 mm
            _ug = up(o["geom"]); _ub = _ug.buffer(-PV.body_inset(gfront(g)), join_style=2)
            _foil = PV.white_edge(gfront(g))   # v90: balta plexi (su / be plėvelės)
            if not _ub.is_empty:
                objs.append((_ub, z0, z0 + gd_ - PV.GLASS_EDGE, retcol(g), retcol(g), None))   # v190: korpuso priekis po stiklu - be kontūro
            objs.append((_ug, z0 + gd_ - PV.GLASS_EDGE, z0 + gd_, PV.GLASS_WHITE if _foil else facecol(g), facecol(g)))
            continue
        objs.append((up(o["geom"]), z0, z0 + gd_, retcol(g), facecol(g)))
for d_, dc_ in DECALS_RAW:                               # v11: lipdukai 3D ant grupės priekio (v13: tarp sluoksnių)
    _g = next((g for g in groups if g["name"] == dc_.get("group")), None)
    _zf = (_g["spec"].get("z0", Z_RAIL_L) + _g["spec"].get("depth_mm", depth)) if _g else ZMAX
    _dg = up(K.shape_geom(K.drawing_to_subpaths(d_, tomm)))          # su skylėmis (iškirpta piktograma)
    if not _dg.is_empty:
        _hc = HexColor(dc_["hex"])
        if _g and _g["spec"].get("behind"):
            objs.append((_dg, _zf - 0.4, _zf + 0.1, _hc, _hc, _hc))     # po raidėmis
        else:
            objs.append((_dg, _zf + 0.1, _zf + 0.6, _hc, _hc, _hc))
objs.sort(key=lambda t: (t[1], V3.depth_key(t[0], (t[1] + t[2]) / 2)))
for ob_ in objs:
    if len(ob_) == 6:
        V3.solid(*ob_[:5], face_stroke=ob_[5])
    else:
        V3.solid(*ob_)
view_title(ix + iw / 2, iy + ih + 16, "3D VIEW", "ILLUSTRATIVE - NOT TO SCALE")
if NOTE3D:
    _lm = [o for g in groups if not g["plate"] for o in g["letters"]]
    _o = min(_lm, key=lambda o: o["bb"][0]) if _lm else None
    if NOTE3D.get("at"):
        _ax, _ay = NOTE3D["at"]
    else:                                                # pirmos raidės priekio vidus (štricho vidurys)
        _c = _o["geom"].representative_point(); _ax, _ay = _c.x, _c.y
    _gz = next((g for g in groups if not g["plate"]), None)
    _zf = (_gz["spec"].get("z0", Z_RAIL_L) + _gz["spec"].get("depth_mm", depth)) if _gz else ZMAX
    _px, _py = V3.S(_ax, PH - _ay, _zf); _py = K.Y(_py)      # S - reportlab (y aukštyn) -> lapo y
    _tx, _ty = ix + 6, iy - 18
    _lines = NOTE3D["text"] if isinstance(NOTE3D["text"], list) else [NOTE3D["text"]]
    for _i, _t in enumerate(_lines):
        T(_tx, _ty + _i * 10, _t, 8 if _i == 0 else 7.5, color=HexColor("#D0021B") if _i == 0 else HexColor("#000000"))
    line(_px, _py, _tx + 2, _ty + 10 * len(_lines) - 6, 0.3)
    K.c.saveState(); K.c.setFillColor(HexColor("#000000")); K.c.circle(_px, K.Y(_py), 1.1, stroke=0, fill=1); K.c.restoreState()

# ============================================================ APATINĖ JUOSTA
BY0 = K.BAND_Y
BH = K.IY1 - BY0                                       # Rytis 2026-10-07: juosta - vientisas blokas iki rėmelio
W_P6, W_MD, W_TB = 214, 172, 272                       # v15: MAIN DATA siauresnis, BOM platesnis
X_P6 = K.IX0                                           # stulpeliai be tarpų, bendros kraštinės
X_TB = K.IX1 - W_TB
X_MD = X_TB - W_MD
X_BOM = X_P6 + W_P6
W_BOM = X_MD - X_BOM
# v102 (Rytis 2026-10-11): U laikikliai (mounting "brackets") lape angliškai = HANGERS ("frame with hangers");
#  ausėlės lieka "ears". Seni spec tekstai "Wall bracket" -> "Hanger" normalizuojami.
def _hang(t_):
    if not isinstance(t_, str):
        return t_
    t_ = re.sub(r"\b[Ww]all bracket", "Hanger", t_)
    m_ = {"brackets": "hangers", "bracket": "hanger", "Brackets": "Hangers", "Bracket": "Hanger", "BRACKETS": "HANGERS", "BRACKET": "HANGER"}
    return re.sub(r"\b(brackets|bracket|Brackets|Bracket|BRACKETS|BRACKET)\b", lambda q: m_[q.group(1)], t_)


import p6_ref as _P6R                                 # Rytio etaloninis pjūvis (U / square wallframe)
# Rytis 2026-10-07: A (PVC bortelis) ir B (varžtas 2.9) žymėjimas - tik 5S (buv. P6_3mm); P6_8mm BOM jų NĖRA
_BOM_ROWS = [row for row in spec["bom"] if not (_NO3 and str(row[0]).upper() in ("A", "B"))]
# v100 (Rytis 2026-10-11): „Letter back" visada su spalva - standartas = šonų (return) spalva; kitokia - tik nurodžius
#  (spec "back_ral" / grupės "back_ral")
_g0 = next((g for g in groups if not g["plate"]), None)
_back_ral = spec.get("back_ral") or (_g0["spec"].get("back_ral") or _g0["spec"].get("return_ral") if _g0 else None)
if FRONT == "P1":
    # v184 (Rytis 2026-10-13): P1 dugnas PVC 10 mm dedamas NEDAŽYTAS - v100 („back = šonų spalva") P1 netaikoma
    _back_ral = None
    _BOM_ROWS = [([r_[0], r_[1], r_[2], "-", r_[4]] if re.search(r"letter back|\bback\b", str(r_[1]), re.I)
                  and re.search(r"pvc", str(r_[2]), re.I) else r_) for r_ in _BOM_ROWS]
if _back_ral:
    _BOM_ROWS = [([r_[0], r_[1], r_[2], f"RAL {_back_ral}", r_[4]] if re.search(r"letter back|\bback\b", str(r_[1]), re.I)
                  and not re.search(r"plate|foil|sheet", str(r_[1]), re.I) and str(r_[3]).strip() in ("", "-") else r_)
                 for r_ in _BOM_ROWS]
if MOUNTING in ("none", "brackets"):
    # v90 (Rytis 2026-10-11): ko brėžinyje nėra - BOM NĖRA (net su 0 m). none: be bėgelių / ausėlių / sienos tvirtinimo eilučių,
    #  vietoj jų - raidžių tvirtinimas per dugną; brackets: be ausėlių. Pozicijos pernumeruojamos.
    _drop = (r"\brail|\bear\b|ears\b|mounting ear|wall fix|bėgel|ausėl" if MOUNTING == "none" else r"\bear\b|ears\b|mounting ear|ausėl")
    _kept, _ins = [], None
    for row in _BOM_ROWS:
        if MOUNTING == "none" and re.search(r"cable", str(row[1]), re.I):     # laidas lieka - pagal raidžių maitinimą
            _wg = str(spec.get("letters_power", "per_letter")).lower().startswith("wago")
            row = [row[0], "WAGO connectors inside letters + supply cable" if _wg else "Cable 12V 1.5 m from each letter (one line)",
                   row[2], row[3], "?" if _wg else f"{sum(len(g['letters']) for g in groups if not g['plate'])} pcs."]
            _kept.append(list(row)); continue
        if MOUNTING == "brackets" and re.match(r"\s*rail", str(row[1]), re.I):   # v102: bėgelis lieka, tik be "with ears"
            row = [row[0], re.sub(r"\s*(with|\+)\s*ears\b", "", str(row[1]), flags=re.I)] + list(row[2:])
            _kept.append(row); continue
        if re.search(_drop, str(row[1]), re.I) and not re.search(r"bracket|hanger", str(row[1]), re.I):
            if _ins is None:
                _ins = len(_kept)
            continue
        _kept.append(list(row))
    if MOUNTING == "none" and _ins is not None:
        _kept.insert(_ins, ["0", "Fixing through back to facade (DXF)", "screws + anchors", "-", "?"])
    _n = 0
    for row in _kept:
        if str(row[0]).strip().isdigit():
            _n += 1; row[0] = str(_n)
    _BOM_ROWS = _kept
_BOM_ROWS = [([r_[0], r_[1], r_[2] or "Alu box", RAIL_FIN, ((f"1 pcs. ({len(CEX)} cables x {TB_LEN:g} m, {TB_V})" if TB_LEN else f"1 pcs. (cables {', '.join(f'{c_[0]['len_m']:.1f}' for c_ in CEX)} m, {TB_V})") if TB_ON and CEX else r_[4])]
              if "trafo" in str(r_[1]).lower() and not str(r_[3]).strip() else r_) for r_ in _BOM_ROWS]
_BOM_ROWS = [[_hang(c_) for c_ in r_] for r_ in _BOM_ROWS]
_EAR_POS = next((str(r_[0]) for r_ in _BOM_ROWS if "ear" in str(r_[1]).lower() and not str(r_[1]).lower().startswith("rail")), "")
_HAS_EARS = any(g.get("fplates") for g in groups)
import p6_ref as _P6REF
try:                                                       # v162: □ profilio gylis / aukštis pjūvyje (40x20x2 -> 0.5)
    _rs = [float(v) for v in str(RAIL["size"]).lower().split("x")]
    _P6REF.RAIL_RATIO = (float(RAIL.get("depth", _rs[1])) / _rs[0]) if RAIL_SQ else 1.0
except Exception:
    _P6REF.RAIL_RATIO = 1.0
_P6REF.LABEL_MAP.update({str(k_): str(v_) for k_, v_ in spec.get("section_labels", {}).items()})
def _blk(x_, w_, name_, f_):                              # v293 TAISYKLĖ 5 / 34: pjūvis - bloko centre (patikra 12)
    K.centered(x_, BY0, w_, BH, f_, name_, frame=True)


if FRONT == "P1":
    _blk(X_P6, W_P6, "PROFILE P1", lambda x_, y_, w_, h_: K.p1_typical(x_, y_, w_, h_, depth, variant="rail", title="PROFILE P1 ON RAILS - TYPICAL SECTION",
                 numbers={"fit": _EAR_POS or 6, "mount": _rail_pos()}, ears=_HAS_EARS,
                 bracket=(next((str(r_[0]) for r_ in _BOM_ROWS if re.search(r"bracket|hanger", str(r_[1]), re.I)), "") if BRACKETS else None)))
elif FRONT == "P10":                                     # v242: P10 blokas ant akrilinio rėmo (etalonas Boots ALT6739)
    import p10_raides as _P10R
    import auto_remas as _ARs
    _strk = sorted(_ARs.stroke_t(o["geom"]) for g in groups for o in g["letters"])
    _blk(X_P6, W_P6, "PROFILE P10", lambda x_, y_, w_, h_: _P10R.section(K, x_, y_, w_, h_, spec, ACRY if RAIL_ACR else None, RAIL_W if RAIL_ACR else None, rod=P10_ROD,
                  stroke=_strk[len(_strk) // 2] if _strk else None,
                  title=(f"PROFILE P10 ON {'CLEAR ACRYLIC FRAME ' + RAIL['size'] if RAIL_ACR else 'FRAME'}" if MOUNTING != "none"
                         else "PROFILE P10 - THREADED RODS TO FACADE")))
elif MOUNTING == "l_hang":                               # v269 (Rytis 2026-10-15): P6 ant L profilių kaip VOLVO BILB26-01001
    import p6_lhang as _LH
    _blk(X_P6, W_P6, "PROFILE L", lambda x_, y_, w_, h_: _LH.section(K, x_, y_, w_, h_, depth, spec,
                                                                     title=f"PROFILE {_PNAME} ON L-PROFILES - TYPICAL SECTION"))
elif RAIL_ACR:                                           # v232 (Rytis: „kodėl senas pjūvis?"): etaloninis P6 pjūvis
    _P6REF.ACRYLIC = True                                #  (square wallframe) su skaidriu pilnaviduriu akrilo bėgeliu 40x20
    _P6REF.RAIL_RATIO = float(ACRY["thk"]) / RAIL_W
    _blk(X_P6, W_P6, "PROFILE ACRYLIC", lambda x_, y_, w_, h_: K.p6_reference(x_, y_, w_, h_, depth, kind="square", front=FRONT,
                   title=f"PROFILE {_PNAME} ON CLEAR ACRYLIC FRAME {RAIL['size']}"))
else:
    # v276 (Rytis 2026-10-15, Securitas): VIENOJE iškaboje skirtingi priekiai (pvz. P6 color + 5S+foil) - po pjūvį kiekvienam,
    #  pusė pjūvio langelio kiekvienam, pavadinimas su grupe
    _fr_list = []
    for g in groups:
        _k = P6F.kind(gfront(g))
        if _k not in [q[0] for q in _fr_list]:
            _fr_list.append((_k, P6F.parse(gfront(g))["code"], [g["name"]]))
        else:
            next(q for q in _fr_list if q[0] == _k)[2].append(g["name"])
    if len(_fr_list) < 2:
        _fr_list = [(FRONT, _PNAME, None)]
    _wq = W_P6 / len(_fr_list)
    _P6REF.K_FIX = None
    if len(_fr_list) > 1:                               # v276: vienodas mastelis visiems pjūviams
        _kind_r = ("folded" if MOUNTING == "none" else _P6R.kind_of("rail", spec.get("rail", {}).get("type")))
        _P6REF.K_FIX = min(K.p6_reference(X_P6, BY0, _wq, BH, depth, kind=_kind_r, front=_k, probe=True,
                                          ears=(_EAR_POS if _HAS_EARS else None)) for _k, _, _ in _fr_list)
    for _iq, (_k, _code, _names) in enumerate(_fr_list):
        _pn = _code.split()[0].split("+")[0] if _names else _PNAME
        _who = f" ({', '.join(_names)})" if _names else ""
        _blk(X_P6 + _iq * _wq, _wq, f"PROFILE {_k}", lambda x_, y_, w_, h_, _k=_k, _pn=_pn, _who=_who, _names=_names:
             K.p6_reference(x_, y_, w_, h_, depth, kind=("folded" if MOUNTING == "none" else _P6R.kind_of("rail", spec.get("rail", {}).get("type"))), front=_k,
                       title=(f"PROFILE {_pn} - FIXED TO FACADE (SEPARATE LETTERS)" if MOUNTING == "none" else
                              (f"PROFILE {_pn}{_who}" if _names else f"PROFILE {_pn} ON RAILS - TYPICAL SECTION")),
                       ears=(_EAR_POS if _HAS_EARS else None),
                       ear_hole=EAR_HOLE / float(RAIL.get("depth", 30)),
                       bracket=(next((str(r_[0]) for r_ in _BOM_ROWS if re.search(r"bracket|hanger", str(r_[1]), re.I)), "") if BRACKETS else None)))
    _P6REF.K_FIX = None
if spec.get("bom_cols"):                                   # v160: originalo lentelės stulpeliai (perkeliama iš org. dokumento)
    K.bom_table(X_BOM, BY0, W_BOM, BH, [[subst(x) for x in row] for row in spec["bom"]],
                title=spec.get("bom_title", "BILL OF MATERIALS  (per 1 pcs.)"),
                cols=tuple((c_[0], c_[1]) for c_ in spec["bom_cols"]))
else:
    K.bom_table(X_BOM, BY0, W_BOM, BH, [[subst(x) for x in row] for row in _BOM_ROWS],
                title=f"BILL OF MATERIALS  (per 1 pcs.)")
# bendras svoris (Rytis patvirtino - visada MAIN DATA); prielaidos - assets/svoris.json
_SV = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "svoris.json")))
_rho, _t = _SV["density_kg_dm3"], dict(_SV["thk_mm"])
if str(spec.get("rail", {}).get("type", "u")).lower().startswith(("sq", "box", "kv")):
    _t["ear"] = 3.0                                         # stačiakampiam profiliui - privirinta 3 mm Alu ausėlė
_t.update(spec.get("thk_mm", {}))                          # užsakymo storiai (pvz. nugara 2 mm)


def _u_area(size):                                         # profilio skerspjūvis mm2: U (b + 2(h - t)) * t, □ 2(b + h - 2t) * t
    b_, h_, t_ = (float(v) for v in str(size).lower().split("x"))
    if str(spec.get("rail", {}).get("type", "u")).lower().startswith(("sq", "box", "kv")):
        return 2 * (b_ + h_ - 2 * t_) * t_
    return (b_ + 2 * (h_ - t_)) * t_


_A_all = sum(g["area"] for g in groups) * 1e6              # mm2
_P_all = sum(g["per"] for g in groups) * 1000              # mm
_kg = {
    "face": (_A_all * 2.0 * _rho["al"]) if FRONT == "P1" else sum(g["area"] * 1e6 * spec.get("face_thk", P6F.thk(gfront(g))) for g in groups) * _rho["pmma"],
    "return": 0.0 if FRONT == "P10" else _P_all * depth * _t["return"] * _rho["al"],
    "back": (_A_all * 10.0 * _rho["pvc"]) if FRONT == "P1" else _A_all * _t["back"] * _rho["al"],
    "pvc": sum(g["per"] * 1000 for g in groups if P6F.kind(gfront(g)) == "3mm") * _SV["pvc_edge_section_mm2"] * _rho["pvc"],
    "rails": (sum(r_["len"] * RAIL_W * ACRY["thk"] for g in groups for r_ in g["rails"]) * _rho["pmma"] if RAIL_ACR else
              sum(r_["len"] * _u_area(g["rsz"]["size"]) for g in groups for r_ in g["rails"]) * _rho["al"]),   # v229: akrilas
    "ears": sum((g["fpl_sz"] * ear4(g, fp_)[2] + g["fpl_sz"] ** 2) * _t["ear"] for g in groups for fp_ in g["fplates"]) * _rho["al"],
    "plate": sum(g["plate"]["geom"].area * PLATE["thk"] for g in groups if g["plate"]) * _rho["al"],
    "zframe": ((2 * GZ["zfr"]["L"] + 2 * GZ["zfr"]["LF"]) * (2 * ZF["zf"] + ZF["zw"] - 2 * ZF["zt"]) * ZF["zt"]
               + 2 * GZ["zfr"]["LT"] * (4 * ZF["tb"] * ZF["tt"] - 4 * ZF["tt"] ** 2)) * _rho["al"] if GZ else 0.0,
}
if BRACKETS:                                             # v90: U laikikliai
    _kg["brackets"] = sum((b_["H"] + 2 * b_["fl"]) * BRK["width_mm"] * BRK["thk_mm"]
                          * (7.85 if b_["mat"].startswith("Steel") else _rho["al"]) for b_ in BRACKETS)
WEIGHT = sum(_kg.values()) / 1e6
SUBS["{WEIGHT}"] = f"≈ {WEIGHT:.0f} kg" if WEIGHT >= 10 else f"≈ {WEIGHT:.1f} kg"
_md = [(a, subst(b)) for a, b in spec["main_data"]]
# v100 (Rytis 2026-10-11): MAIN DATA - tik tai, kas ne pagal standartą: „Wall" - tik kai fasadas ne įprastas (ne betonas /
#  nurodyti niuansai), „Drainage" - niekada (privaloma exterior opcija, nežymima)
_wall_std = str(spec.get("wall", "concrete")).lower() in ("concrete", "", "none")
_md = [(a, b) for a, b in _md if not re.match(r"drain", a, re.I) and not (_wall_std and re.match(r"wall|siena|facade", a, re.I))]
if MOUNTING in ("none", "brackets"):                      # v90: be neegzistuojančių elementų
    _md = [(a, b) for a, b in _md if not (MOUNTING == "none" and re.match(r"rail|ear|frame", a, re.I))]
    _md = [(a, (re.sub(r"\s*\+\s*ears", " + hangers", b) if MOUNTING == "brackets" else b)) for a, b in _md]
    if MOUNTING == "none":
        _md.append(("Mounting", "separate letters, no frame"))
_md = [(_hang(a), _hang(b)) for a, b in _md]
if not any(a.lower().startswith("weight") for a, _ in _md):
    _md.append(("Weight (calc.)", SUBS["{WEIGHT}"] + " / pcs, excl. PSU"))
print("  svoris:", ", ".join(f"{k} {v / 1e6:.1f}" for k, v in _kg.items()), f"= {WEIGHT:.1f} kg")
K.main_data(X_MD, BY0, W_MD, BH, _md, lab_w=58)
if BRACKETS or ACR_GEO:
    spec["sheet"] = "1 / 2"
K.title_block(X_TB, W_TB, spec, f"1:{SC1} / 1:{SC2}")


def draw_bracket_sheet():
    """v90: 2 lapas - U laikiklio gamybinis brėžinys (vaizdas nuo sienos, šonas su įstatytu rėmu, vaizdas iš viršaus)"""
    K.c.showPage()
    K.frame()
    b0 = max(BRACKETS, key=lambda b_: sum(1 for q_ in BRACKETS if round(q_["H"]) == round(b_["H"])))
    Hb, fl, hd, nw, Wb, tb = b0["H"], b0["fl"], b0["hd"], b0["nw"], BRK["width_mm"], BRK["thk_mm"]
    dep = fl - BRK["flange_add_mm"]
    avail = K.BAND_Y - K.IY0 - 120
    n_sc = next(n_ for n_ in (1, 2, 2.5, 5, 10, 15, 20, 25, 50) if Hb * MM / n_ <= avail)
    s = MM / n_sc
    y0 = K.IY0 + 60
    # vaizdas nuo sienos (sienos plokštuma); v183: objektų kontūrai - hairline (patikra_lapas)
    x0 = K.IX0 + 150
    K.set_view(True)
    rect(x0, y0, Wb * s, Hb * s, fill=K.mix(RAILC, 0.85), lw=0.6)
    hy = [y0 + Hb * s * (2 * k_ + 1) / (2 * nw) for k_ in range(nw)]          # v90: žingsnis p, galai p/2
    for yy_ in hy:
        K.circle(x0 + Wb * s / 2, yy_, max(1.2, hd / 2 * s), fill=white, lw=0.4)
    K.set_view(False)
    for yy_ in hy:
        K.centerline(x0 - 6, yy_, x0 + Wb * s + 6, yy_)
    K.centerline(x0 + Wb * s / 2, y0 - 8, x0 + Wb * s / 2, y0 + Hb * s + 8)
    hdim(x0, x0 + Wb * s, y0 - 16, f"{Wb:.0f}", y0, y0)
    ys_ = [y0] + hy + [y0 + Hb * s]
    hv_ = [Hb * (2 * k_ + 1) / (2 * nw) for k_ in range(nw)]
    lab_ = [f"{v_:.0f}" for v_ in [hv_[0]] + [b_ - a_ for a_, b_ in zip(hv_[:-1], hv_[1:])] + [Hb - hv_[-1]]]
    vchain(x0 - 26, ys_, [x0] * len(ys_), lab_)
    vchain(x0 - 52, [y0, y0 + Hb * s], [x0, x0], [f"{Hb:.0f}"], size=12)
    T(x0 + Wb * s + 10, hy[len(hy) // 2] + 3, f"{nw} x Ø{hd} (facade)", 8)
    view_title(x0 + Wb * s / 2, y0 + Hb * s + 30, "VIEW FROM FACADE", f"SCALE 1:{n_sc:g}")
    # šonas: U (siena kairėje), plokštumos fl, įstatytas rėmas - punktyru
    x1 = x0 + Wb * s + 190
    K.set_view(True)
    rect(x1, y0, tb * s, Hb * s, fill=K.mix(RAILC, 0.7), lw=0.5)
    rect(x1, y0, fl * s, tb * s, fill=K.mix(RAILC, 0.7), lw=0.5)
    rect(x1, y0 + (Hb - tb) * s, fl * s, tb * s, fill=K.mix(RAILC, 0.7), lw=0.5)
    gap_ = BRK["clear_mm"]
    ext = tb + gap_                                         # rėmo viršus nuo laikiklio viršaus
    for ry_ in (ext, ext + b0["Hf"] - dep):                 # rėmo bėgeliai (punktyras), apatinis guli ant plokštumos
        rect(x1 + tb * s, y0 + ry_ * s, dep * s, dep * s, lw=0.35, dash=(3, 1.5))
    K.set_view(False)
    K.centerline(x1 + (tb + dep / 2) * s, y0 - 10, x1 + (tb + dep / 2) * s, y0 + tb * s + 6)
    K.centerline(x1 + (tb + dep / 2) * s, y0 + (Hb - tb) * s - 6, x1 + (tb + dep / 2) * s, y0 + Hb * s + 10)
    K.set_view(True)
    hatch(x1 - 12, y0 - 6, 10, Hb * s + 12, 6)
    line(x1 - 2, y0 - 6, x1 - 2, y0 + Hb * s + 6, 0.6)
    K.set_view(False)
    hdim(x1, x1 + fl * s, y0 - 16, f"{fl:.0f}", y0, y0)
    vchain(x1 + fl * s + 26, [y0 + tb * s, y0 + (Hb - tb) * s], [x1 + fl * s] * 2,
           [f"{Hb - 2 * tb:.0f} (frame {b0['Hf']:.0f} + {gap_:g})"])
    T(x1 + fl * s + 40, y0 + 10, "Ø6 top / bottom: screw into rail", 8)
    T(x1 + fl * s + 40, y0 + Hb * s * 0.5, f"frame {RAIL['size']} (dashed) inserted", 8, color=K.GREY)
    view_title(x1 + fl * s / 2, y0 + Hb * s + 30, "SIDE VIEW", f"SCALE 1:{n_sc:g}")
    # vaizdas iš viršaus 1:1
    s1 = MM
    x2 = x1 + fl * s + 230
    y2 = y0 + 20
    K.set_view(True)
    rect(x2, y2, Wb * s1, fl * s1, fill=K.mix(RAILC, 0.85), lw=0.6)
    rect(x2, y2, Wb * s1, tb * s1, fill=K.mix(RAILC, 0.6), lw=0.4)
    K.circle(x2 + Wb * s1 / 2, y2 + (tb + dep / 2) * s1, 3 * s1, fill=white, lw=0.4)
    K.set_view(False)
    hdim(x2, x2 + Wb * s1, y2 - 16, f"{Wb:.0f}", y2, y2)
    vchain(x2 + Wb * s1 + 22, [y2, y2 + tb * s1, y2 + fl * s1], [x2 + Wb * s1] * 3, [f"{tb:g}", f"{dep:.0f}"])
    T(x2 + Wb * s1 / 2, y2 + fl * s1 + 14, "Ø6", 8, align="c")
    T(x2 - 6, y2 + 4, "facade", 7, align="r")
    view_title(x2 + Wb * s1 / 2, y2 + fl * s1 + 40, "TOP VIEW", "SCALE 1:1")
    # juosta
    K.header(X_P6, BY0, W_P6, "NOTES")
    _nt = ["1. Hangers fixed to facade first (facade = concrete",
           "   unless specified), frame inserted, screwed",
           "   to each hanger at top and bottom (Ø6).",
           f"2. Material {b0['mat']} (steel for heavy signs).",
           f"3. Inside = frame {b0['Hf']:.0f} + {gap_:g}; frame rests on bottom flange.",
           "4. Final screw positions - by production.",
           f"5. Positions: see rear view, sheet 1."]
    for i_, t_ in enumerate(_nt):
        T(X_P6 + 5, BY0 + 26 + i_ * 11, t_, 8)
    rect(X_P6, BY0 + 12, W_P6, BH - 12, lw=0.6)
    nb_ = len(BRACKETS)
    rows_ = []
    for i_, (h_, f_, m_) in enumerate(_bk):
        q_ = sum(1 for b_ in BRACKETS if round(b_["H"]) == h_ and round(b_["fl"]) == f_ and b_["mat"] == m_)
        rows_.append([str(i_ + 1), f"Hanger U {h_} x {Wb:.0f}, flanges {f_}", m_, RAIL_FIN, f"{q_} pcs."])
    rows_.append([str(len(rows_) + 1), f"Facade anchor for Ø{hd} hole", "-", "-", f"{sum(b_['nw'] for b_ in BRACKETS)} pcs."])
    rows_.append([str(len(rows_) + 1), "Screw flange -> rail (Ø6)", "-", "-", f"{2 * nb_} pcs."])
    K.bom_table(X_BOM, BY0, W_BOM, BH, rows_, title="BILL OF MATERIALS - HANGERS  (per 1 sign)")
    _w1 = (Hb + 2 * fl) * Wb * tb * (7.85 if b0["mat"].startswith("Steel") else 2.7) / 1e6
    md_ = [("Height", f"{Hb:.0f} (inside frame {b0['Hf']:.0f} + {gap_:g})"), ("Width", f"{Wb:.0f}"),
           ("Flanges", f"{fl:.0f} (rail {dep:.0f} + {BRK['flange_add_mm']:g})"), ("Material", b0["mat"]),
           ("Facade holes", f"{nw} x Ø{hd}"), ("Flange holes", "1 x Ø6 top, 1 x Ø6 bottom"),
           ("Quantity", f"{nb_} pcs."), ("Weight (calc.)", f"≈ {_w1:.2f} kg / pcs")]
    K.main_data(X_MD, BY0, W_MD, BH, md_, lab_w=58)
    sp2 = dict(spec, sheet="2 / 2", title="Hangers (U) - " + str(spec.get("title", "")))
    K.title_block(X_TB, W_TB, sp2, f"1:{n_sc:g} / 1:1")



def draw_acrylic_sheet():
    """v233 (Rytis 2026-10-14): 2 lapas - AKRILINIO RĖMO DALYS IR JUNGTYS: rėmo dalių vaizdas (iš galo), DETAIL C (bėgelių
    puzzle jungtis pagal lakšto ilgį), DETAIL D (statmuo -> bėgelis puzzle), SECTION E (bėgelis, griovelis, Ø8);
    juostoje - paaiškinimas kur ir kodėl jungiasi, dalių BOM, duomenys."""
    from shapely.geometry import box as _b2
    K.c.showPage()
    K.frame()
    gn_, AG = next(iter(ACR_GEO.items()))
    F = AG["F"]
    X0, Y0, X1, Y1 = F.bounds
    GW = (ACRY.get("groove") or {})
    blue = HexColor("#CFE6F5")

    def subs_of(geo):
        out = []
        for gg in getattr(geo, "geoms", [geo]):
            if not hasattr(gg, "exterior"):
                continue
            out += [[("M", rg[0])] + [("L", q) for q in rg[1:]] for rg in
                    [list(gg.exterior.coords)] + [list(r.coords) for r in gg.interiors]]
        return out
    # dalys: bėgelių juostos R.., statmenys V..
    rp = []
    for P_ in AG["parts"]:
        rp += [q for q in getattr(P_, "geoms", [P_]) if q.area > 1]
    rp.sort(key=lambda q: (round(q.bounds[1]), -q.bounds[2]))          # iš galo (veidrodis): kairėje - dešinysis galas
    vp = sorted(AG["vparts"], key=lambda q: -q.bounds[0])
    # ---------------- rėmo dalys (iš galo)
    aw = K.IX1 - K.IX0 - 120
    n1 = next(n_ for n_ in (5, 10, 15, 20, 25, 30, 40, 50) if (X1 - X0) * MM / n_ <= aw)
    s_ = MM / n1
    ox, oy = K.IX0 + 60 + (aw - (X1 - X0) * s_) / 2, K.IY0 + 110
    Fm = lambda x, y: (ox + (X1 - x) * s_, oy + (y - Y0) * s_)
    Ftf = lambda x, y: (Fm(x, y)[0], K.Y(Fm(x, y)[1]))
    K.set_view(True)
    for q in rp + vp:
        K.draw_shape(subs_of(q), Ftf, fill=blue, stroke=black, lw=0.3)
    for hx_, hy_ in AG["holes"]:
        cc_ = Fm(hx_, hy_)
        K.circle(cc_[0], cc_[1], max(0.6, ACRY["hole_d"] / 2 * s_), fill=white, stroke=HexColor("#1F5FD0"), lw=0.3)
    for sx_, sy_, _ in AG["studs"]:                     # v241: įleistos skylės raidžių smeigėms
        cc_ = Fm(sx_, sy_)
        K.circle(cc_[0], cc_[1], max(0.9, ACRY["stud"]["cb_d"] / 2 * s_), fill=white, lw=0.25)
        K.circle(cc_[0], cc_[1], max(0.4, ACRY["stud"]["d"] / 2 * s_), lw=0.25)
    for a_, b_ in AG["grooves"]:
        pa_, pb_ = Fm(*a_), Fm(*b_)
        line(pa_[0], pa_[1], pb_[0], pb_[1], 0.25, HexColor("#3B3BB0"))
    for ox_, oy_ in AG["slots"]:
        cc_ = Fm(ox_, oy_)
        rect(cc_[0] - max(1.2, AG["cslot"][0] / 2 * s_), cc_[1] - max(0.6, AG["cslot"][1] / 2 * s_),
             2 * max(1.2, AG["cslot"][0] / 2 * s_), 2 * max(0.6, AG["cslot"][1] / 2 * s_), fill=white, lw=0.25)
    K.set_view(False)
    for i_, q in enumerate(rp):
        c_ = q.representative_point(); p_ = Fm(c_.x, c_.y)
        L_ = q.bounds[2] - q.bounds[0]
        K._Tbg(p_[0], p_[1] + 2.4, f"R{i_ + 1}  {L_:.0f}", 6.5, align="c", font="FB", auto_red=False)
    for i_, q in enumerate(vp):
        b_ = q.bounds; p_ = Fm((b_[0] + b_[2]) / 2, b_[3])
        T(p_[0], p_[1] + 10, f"V{i_ + 1}", 6.5, align="c", font="FB")
    for ci_, c_ in enumerate(AG["cuts"]):
        jx_ = Fm(c_["x"], 0)[0]
        line(jx_, Fm(0, Y0)[1] - 12, jx_, Fm(0, Y1)[1] + 12, 0.5, HexColor("#C00000"), dash=([6, 2, 1.5, 2], 0))
        T(jx_ + 4, Fm(0, Y0)[1] - 6, f"J{ci_ + 1}", 7, font="FB")
    xs_ = sorted(Fm(x_, 0)[0] for x_ in [X0, X1] + [c_["x"] for c_ in AG["cuts"]])
    if AG["cuts"]:
        _jxs = [Fm(c_["x"], 0)[0] for c_ in AG["cuts"]]   # v276 ISO: ties jungtimi iškeltinė = J linijos tęsinys (ne ant jos)
        hchain(Fm(0, Y0)[1] - 30, xs_, [Fm(0, Y0)[1] - (12 if any(abs(x_ - j_) < 0.5 for j_ in _jxs) else 0) for x_ in xs_],
               [f"{abs(b - a) / s_:.0f}" for a, b in zip(xs_, xs_[1:])], size=K.F_DIM_FRAME)
    hdim(xs_[0], xs_[-1], Fm(0, Y0)[1] - 50, f"{X1 - X0:.0f}", Fm(0, Y0)[1], Fm(0, Y0)[1], size=K.F_DIM_FRAME)
    vchain(Fm(X0, 0)[0] + 16, [Fm(0, Y0)[1], Fm(0, Y1)[1]], [Fm(X0, 0)[0]] * 2, [f"{Y1 - Y0:.0f}"], size=K.F_DIM_FRAME)
    # detalių nuorodos
    refs = []
    if AG["cuts"]:
        refs.append(("C", AG["cuts"][0]["x"], (AG["hs"][0]["y0"] + AG["hs"][0]["y1"]) / 2))
    vj = min(AG["vjoints"], key=lambda q: (q[4], q[1], abs(q[0] - (X0 + X1) / 2))) if AG["vjoints"] else None
    if vj:
        refs.append(("D", vj[0], vj[1]))
    if AG["holes"]:
        hE = AG["holes"][0]
        refs.append(("E", hE[0], hE[1]))
    for rn_, rx_, ry_ in refs:
        cc_ = Fm(rx_, ry_)
        K.circle(cc_[0], cc_[1], 7, stroke=HexColor("#C00000"), lw=0.5)
        K.leader(cc_[0] + 5, cc_[1] + 5, cc_[0] + 18, cc_[1] + 26, rn_)
    view_title(ox + (X1 - X0) * s_ / 2, Fm(0, Y1)[1] + 52, "ACRYLIC FRAME - PARTS & JOINTS (VIEW FROM BACK)",
               f"SCALE 1:{n1}  |  R - rail parts, V - verticals (separate), J - joint by sheet length")
    # ---------------- detalės 1:1
    dy0 = Fm(0, Y1)[1] + 110
    dh = K.VIEW_BOT - dy0 - 40
    dsc = 1.0 if dh >= 72 * MM else 0.5
    sd = MM * dsc
    dw_ = (K.IX1 - K.IX0) / 3

    def detail(k_, cx_, cy_, win, title, sub):
        x0d = K.IX0 + k_ * dw_ + (dw_ - win[0] * sd) / 2
        y0d = dy0 + (dh - win[1] * sd) / 2
        D_ = lambda x, y: (x0d + (cx_ + win[0] / 2 - x) * sd, y0d + (y - (cy_ - win[1] / 2)) * sd)
        Dtf = lambda x, y: (D_(x, y)[0], K.Y(D_(x, y)[1]))
        W_ = _b2(cx_ - win[0] / 2, cy_ - win[1] / 2, cx_ + win[0] / 2, cy_ + win[1] / 2)
        K.set_view(True)
        for iq_, q in enumerate(rp + vp):                 # gretimos dalys - skirtingi atspalviai (matosi jungtis)
            qq = q.intersection(W_)
            if not qq.is_empty:
                K.draw_shape(subs_of(qq), Dtf, fill=(blue if iq_ % 2 == 0 else HexColor("#9CC8E6")), stroke=black, lw=0.4)
        K.set_view(False)
        rect(x0d, y0d, win[0] * sd, win[1] * sd, lw=0.3, dash=(3, 2))
        view_title(x0d + win[0] * sd / 2, y0d + win[1] * sd + 30, title, sub)
        return D_
    if AG["cuts"]:
        r0 = AG["hs"][0]; w_ = r0["y1"] - r0["y0"]; cy_ = (r0["y0"] + r0["y1"]) / 2; cx_ = AG["cuts"][0]["x"]
        hr_, nk_ = AG["krail"][0] * w_, AG["krail"][1] * w_
        D_ = detail(0, cx_ + 10, cy_, (90, 70), "DETAIL C - RAIL JOINT J1 (PUZZLE)", f"SCALE {'1:1' if dsc == 1 else '1:2'}")
        a_, b_ = D_(cx_, r0["y0"]), D_(cx_, r0["y1"])
        line(a_[0], a_[1] - 8, b_[0], b_[1] + 8, 0.3, HexColor("#C00000"), dash=([6, 2, 1.5, 2], 0))
        vchain(D_(cx_ - 35, 0)[0] + 16, [D_(0, r0["y0"])[1], D_(0, r0["y1"])[1]], [D_(cx_ - 35, 0)[0] + 1] * 2, [f"{w_:g}"], size=K.F_DIM_FRAME)   # v276: iškeltinė nuo lango krašto (ne išilgai bėgio krašto)
        hc_ = D_(cx_ + hr_ * 1.6, cy_)
        T(hc_[0], D_(0, r0["y0"])[1] - 8, f"head Ø{2 * hr_:g}, neck {2 * nk_:g}", 6.5, align="c")
        T(hc_[0], D_(0, r0["y1"])[1] + 12, f"clearance {ACRY['joint_clear']:g} all round", 6.5, align="c", color=K.GREY)
    if vj:
        ex_, ey_, sg_, wv_, _dg = vj
        hr_, nk_ = AG["kvert"][0] * wv_, AG["kvert"][1] * wv_
        D_ = detail(1, ex_, ey_ - sg_ * 5, (90, 70), "DETAIL D - VERTICAL -> RAIL (PUZZLE)", f"SCALE {'1:1' if dsc == 1 else '1:2'}")
        p_ = D_(ex_, ey_ + sg_ * hr_ * 1.6)
        T(p_[0] + 30, p_[1] + 2, f"head Ø{2 * hr_:g}, neck {2 * nk_:g}", 6.5)
        T(p_[0] + 30, p_[1] + 11, f"clearance {ACRY['joint_clear']:g}", 6.5, color=K.GREY)
    # SECTION E - bėgelio pjūvis per raidės smeigę (v241): įleista skylė Ø12 x 15 iš galo + Ø5 į priekį (ašyje), laidų griovelis
    #  nugaroje paslinktas g_off nuo ašies; priekyje - raidės nugara su privirinta smeige (punktyru)
    if AG["hs"]:
        w_ = AG["hs"][0]["y1"] - AG["hs"][0]["y0"]; th_ = float(ACRY["thk"])
        ST = ACRY["stud"]; gw_, gd_ = float(GW.get("w", 6)), float(GW.get("d", 3.5)); go_ = AG["g_off"]
        _sc = 2 if w_ * MM * 2 + 100 <= dh else 1           # v243: platus bėgelis (60) - 1:1
        se = MM * _sc
        x0e = K.IX0 + 2 * dw_ + (dw_ - th_ * se) / 2
        y0e = dy0 + 6
        yc_ = y0e + w_ / 2 * se
        K.set_view(True)
        rect(x0e, y0e, th_ * se, w_ * se, fill=blue, lw=0.4)
        rect(x0e, yc_ - ST["cb_d"] / 2 * se, ST["cb_depth"] * se, ST["cb_d"] * se, fill=white, lw=0.4)          # įleidimas iš galo
        rect(x0e + ST["cb_depth"] * se, yc_ - ST["d"] / 2 * se, (th_ - ST["cb_depth"]) * se, ST["d"] * se, fill=white, lw=0.4)
        rect(x0e, yc_ - (go_ + gw_ / 2) * se, gd_ * se, gw_ * se, fill=white, lw=0.4)                            # laidų griovelis
        K.set_view(False)
        K.centerline(x0e - 6, yc_, x0e + th_ * se + 8, yc_)
        rect(x0e + th_ * se, y0e - 4, 4, w_ * se + 8, lw=0.3, dash=(2, 1.5))
        T(x0e + th_ * se + 7, y0e - 6, "letter back + welded stud", 6, color=K.GREY)
        line(x0e - 14, y0e - 6, x0e - 14, y0e + w_ * se + 6, 1.2, HexColor("#888888"))
        T(x0e - 20, y0e + w_ * se / 2, "FACADE", 6.5, rot=90, align="c", color=K.GREY)
        hdim(x0e, x0e + th_ * se, y0e - 14, f"{th_:g}", y0e, y0e, size=K.F_DIM_FRAME)
        hdim(x0e, x0e + ST["cb_depth"] * se, y0e + w_ * se + 16, f"{ST['cb_depth']:g}", y0e + w_ * se, y0e + w_ * se, size=K.F_DIM_FRAME)
        hdim(x0e, x0e + gd_ * se, y0e + w_ * se + 34, f"{gd_:g} (groove)", y0e + w_ * se, y0e + w_ * se, size=K.F_DIM_FRAME)
        ys_ = sorted({y0e, yc_ - (go_ + gw_ / 2) * se, yc_ - (go_ - gw_ / 2) * se, yc_ - ST["cb_d"] / 2 * se,
                      yc_ + ST["cb_d"] / 2 * se, y0e + w_ * se})
        vchain(x0e + th_ * se + 22, ys_, [x0e + th_ * se] * len(ys_), [f"{(b - a) / se:g}" for a, b in zip(ys_, ys_[1:])],
               size=K.F_DIM_FRAME)
        T(x0e + th_ * se + 60, yc_ + 3, f"Ø{ST['d']:g} / Ø{ST['cb_d']:g} x {ST['cb_depth']:g}", 6.5)
        T(x0e + th_ * se / 2, y0e + w_ * se + 58, f"stud holes under letters (nut in counterbore), cable slots {AG['cslot'][0]:g} x "
          f"{AG['cslot'][1]:g} through, Ø{ACRY['hole_d']:g} fixing holes between letters", 6.5, align="c", color=K.GREY)
        view_title(x0e + th_ * se / 2, y0e + w_ * se + 82, "SECTION E - RAIL AT LETTER STUD", f"SCALE {_sc}:1")
    # ---------------- juosta: paaiškinimas, BOM, duomenys
    K.header(X_P6, BY0, W_P6, "WHY / WHERE THE FRAME JOINS")
    rect(X_P6, BY0 + 12, W_P6, BH - 12, lw=0.6)
    smax = max(ACRY["sheet"]) - 30
    if AG["cuts"]:
        nt_ = [f"1. Clear acrylic sheet {ACRY['sheet'][0]:g} x {ACRY['sheet'][1]:g} -",
               f"   rail {X1 - X0:.0f} longer than sheet -> rails cut",
               f"   in {len(AG['parts'])} parts (<= {smax:g}), joint J1 (detail C).",
               "2. J1 placed UNDER LETTER (clear frame -",
               "   joint hidden behind letter), >= 60 from verticals."]
    else:
        nt_ = [f"1. Rail {X1 - X0:.0f} fits in sheet {ACRY['sheet'][0]:g} x {ACRY['sheet'][1]:g} -",
               "   one part, no joints."]
    if AG["vparts"]:
        nt_ += ["3. Verticals / diagonals - SEPARATE parts (V),",
                "   nested from offcuts - saves material;",
                "   puzzle into rails (detail D)."]
    elif len(AG["hs"]) == 1:
        nt_ += [f"2. Small letters - ONE rail {RAIL_W:g} wide, no verticals."]
    nt_ += [f"{len([q for q in nt_ if q[:1].isdigit()]) + 1}. Puzzle clearance {ACRY['joint_clear']:g}; cable groove on back"
            if AG["cuts"] or AG["vparts"] else f"{len([q for q in nt_ if q[:1].isdigit()]) + 1}. Cable groove on back",
            f"   {GW.get('w', '?')} x {GW.get('d', '?')} deep (section E); Ø{ACRY['hole_d']:g} fixings.",
            f"{len([q for q in nt_ if q[:1].isdigit()]) + 2}. Letters: welded studs through Ø{ACRY['stud']['d']:g}, nut in "
            f"Ø{ACRY['stud']['cb_d']:g} x {ACRY['stud']['cb_depth']:g}",
            "   counterbore from back - nut does not touch facade."]
    for i_, t_ in enumerate(nt_):
        T(X_P6 + 5, BY0 + 25 + i_ * 9.6, t_, 7)
    rows_ = []
    for i_, q in enumerate(rp):
        rows_.append([str(len(rows_) + 1), f"R{i_ + 1} rail part {q.bounds[2] - q.bounds[0]:.0f} x {RAIL_W:g}",
                      f"Clear acrylic {ACRY['thk']:g} mm", "clear", "1 pc."])
    vl_ = {}
    for i_, q in enumerate(vp):
        k_ = (round(q.bounds[2] - q.bounds[0]), round(q.bounds[3] - q.bounds[1]))
        vl_.setdefault(k_, []).append(f"V{i_ + 1}")
    for (w2, h2), nm_ in vl_.items():
        rows_.append([str(len(rows_) + 1), f"{'Diagonal' if w2 > RAIL_W + 5 else 'Vertical'} {h2} incl. puzzle heads", f"Clear acrylic {ACRY['thk']:g} mm",
                      "clear", f"{len(nm_)} pcs. ({', '.join(nm_)})"])
    K.bom_table(X_BOM, BY0, W_BOM, BH, rows_, title="BILL OF MATERIALS - ACRYLIC FRAME PARTS  (per 1 sign, DXF)")
    md_ = [("Material", f"clear acrylic {ACRY['thk']:g} mm"), ("Sheet", f"{ACRY['sheet'][0]:g} x {ACRY['sheet'][1]:g}"),
           ("Rails", f"{RAIL_W:g} wide, {len(rp)} parts"), ("Verticals", f"{len(vp)} pcs., separate"),
           ("Joints", f"puzzle, clearance {ACRY['joint_clear']:g}" if (AG["cuts"] or AG["vparts"]) else "none (1 part)"), ("Groove", f"{GW.get('w', '?')} x {GW.get('d', '?')} (back)"),
           ("Holes", f"{len(AG['holes'])} x Ø{ACRY['hole_d']:g}; studs {len(AG['studs'])} x Ø{ACRY['stud']['d']:g}/{ACRY['stud']['cb_d']:g}"),
           ("Quantity", f"{spec.get('qty', '?')} signs")]
    K.main_data(X_MD, BY0, W_MD, BH, md_, lab_w=58)
    sp2 = dict(spec, sheet="2 / 2", title=f"{spec.get('drawing_no', '')} Acrylic frame - parts & joints")
    K.title_block(X_TB, W_TB, sp2, f"1:{n1} / 1:1 / 2:1")

if BRACKETS:
    draw_bracket_sheet()
elif ACR_GEO:
    draw_acrylic_sheet()
K.save(OUT)
if K.AUTO["mode"] == "collect" and K.AUTO["reqs"]:           # v172: 2 praėjimas su rastomis balionų vietomis
    import subprocess as _sp
    _af = OUT + ".auto.json"
    # v172: galinio vaizdo viršutinės eilės (žymos, laidai) neturi išlįsti už rėmelio - 2 praėjime vaizdas nuleidžiamas
    _pg = fitz.open(OUT)[0]
    _rx0, _rx1 = POS["R"][0], POS["R"][0] + POS["R"][2]
    _ys = [d_["rect"].y0 for d_ in _pg.get_drawings() if _rx0 - 40 < d_["rect"].x0 < _rx1 + 40 and d_["rect"].width < 600]
    _ys += [b_["bbox"][1] for b_ in _pg.get_text("dict")["blocks"] if _rx0 - 40 < b_["bbox"][0] < _rx1 + 40]
    _shift = max(0.0, K.IY0 + 8 - min(_ys)) if _ys else 0.0
    json.dump({"place": K.auto_place(OUT), "shift_r": _shift}, open(_af, "w"))
    _r = _sp.run([sys.executable] + sys.argv, env=dict(os.environ, BB_AUTO=_af), capture_output=True, text=True)
    sys.stdout.write(_r.stdout); sys.stderr.write(_r.stderr)
    sys.exit(_r.returncode)
print("OK", OUT, f"1:{SC1}/1:{SC2}", "layout", LAY, "size", round(PW), "x", round(PH))
for g in groups:
    print(" ", g["name"], g["spec"]["profile"], "letters", len(g["letters"]), "box", round(g["lx1"] - g["lx0"]), "x",
          round(g["ly1"] - g["ly0"]), "per", round(g["per"], 2), "area", round(g["area"], 3), "rails",
          [round(r_["len"]) for r_ in g["rails"]], "plates", len(g["fplates"]))


# ------------------------------------------------------------ 1:1 failas (Rytis 2026-10-07)
# Prie techninio lapo - atskiras PDF: tik raidžių (ir plokštės) kontūrai 1:1, be matmenų, rėmelio, bėgelių ir užrašų.
# Lapas = elementų gabaritas, mm -> pt 1:1. Kreivės išlaikomos (Bezier iš kliento failo).
def export_1to1(path):
    """Rytis 2026-10-07: 1:1 PDF - TRYS atskiri sluoksniai (OCG; Illustrator / Corel - atskiri sluoksniai / grupės),
    skirtingomis spalvomis: 1 raidės (juoda, kreivės iš kliento failo), 2 dugnas - raidės kontūras 3 mm į vidų
    (raudona, `back_inset_mm`), 3 rėmas - bėgeliai, statmenys, ausėlės su Ø skyle (mėlyna). Tik kontūrai, hairline."""
    items = []
    for g in groups:
        if g.get("plate"):
            items.append(g["plate"])
        items += list(g["letters"])
    seen, uniq = set(), []
    for o in items:
        if id(o) not in seen:
            seen.add(id(o)); uniq.append(o)
    rails_ = [r_ for g in groups for r_ in g["rails"]]
    ears_ = [(g, ear4(g, fp_)) for g in groups for fp_ in g["fplates"]]
    xs_ = [o["geom"].bounds[0] for o in uniq] + [min(q[0] for q in r_["poly"]) for r_ in rails_]
    ys_ = [o["geom"].bounds[1] for o in uniq] + [min(q[1] for q in r_["poly"]) for r_ in rails_]
    xe_ = [o["geom"].bounds[2] for o in uniq] + [max(q[0] for q in r_["poly"]) for r_ in rails_]
    ye_ = [o["geom"].bounds[3] for o in uniq] + [max(q[1] for q in r_["poly"]) for r_ in rails_]
    for g, (px_, py_, ph_, hy_) in ears_:
        xs_.append(px_); ys_.append(py_); xe_.append(px_ + g["fpl_sz"]); ye_.append(py_ + ph_)
    bx0, by0, bx1, by1 = min(xs_), min(ys_), max(xe_), max(ye_)
    k = K.MM
    doc = fitz.open()
    pg = doc.new_page(width=(bx1 - bx0) * k, height=(by1 - by0) * k)
    doc.set_metadata({"title": f"{spec.get('file_code', '')} 1:1"})
    inset = spec.get("back_inset_mm", 0.7 if FRONT == "P1" else (float((spec.get("p10") or {}).get("rim", 5)) if FRONT == "P10" else 3))   # v116 / v249
    L_LET, L_BACK, L_FRAME = (doc.add_ocg("1_LETTERS"), doc.add_ocg(f"2_BACK_inset_{inset:g}mm"), doc.add_ocg("3_FRAME"))
    C_LET, C_BACK, C_FRAME = (0, 0, 0), (0.85, 0, 0), (0, 0.35, 0.85)
    HW = 0.1

    def P(q):
        return fitz.Point((q[0] - bx0) * k, (q[1] - by0) * k)
    # 1 - raidės
    for o in uniq:
        sh = pg.new_shape()
        for sp in o["sub"]:
            cur = None
            for s_ in sp:
                if s_[0] == "M":
                    cur = P(s_[1]); start = cur
                elif s_[0] == "L":
                    q = P(s_[1]); sh.draw_line(cur, q); cur = q
                else:
                    q = P(s_[3]); sh.draw_bezier(cur, P(s_[1]), P(s_[2]), q); cur = q
            if cur is not None and abs(cur.x - start.x) + abs(cur.y - start.y) > 1e-3:
                sh.draw_line(cur, start)
        sh.finish(width=HW, color=C_LET, fill=None, closePath=False, oc=L_LET); sh.commit()
    # 2 - dugnas: raidės kontūras 3 mm į vidų (smulkiai išlygintos kreivės)
    for o in uniq:
        ps = [Polygon(K.flatten(sp, 32)).buffer(0) for sp in o["sub"] if len(K.flatten(sp, 32)) >= 3]
        if not ps:
            continue
        geo = ps[0]
        for q in ps[1:]:
            geo = geo.symmetric_difference(q)
        if o.get("geom") is not None and o["geom"].area < geo.area - 1:      # apkirpta (plokštė)
            geo = geo.intersection(o["geom"])
        bk = K.dugnas_inset(geo, inset, spec.get("back_blunt_mm", 12))   # v108: smailios įpjovos nukertamos
        if bk.is_empty:
            continue
        sh = pg.new_shape()
        for poly_ in getattr(bk, "geoms", [bk]):
            for ring in [poly_.exterior] + list(poly_.interiors):
                sh.draw_polyline([P(c_) for c_ in ring.coords])
        sh.finish(width=HW, color=C_BACK, fill=None, closePath=True, oc=L_BACK); sh.commit()
    # 3 - rėmas
    sh = pg.new_shape()
    if ACR_GEO:                                         # v229: akrilinio rėmo dalys su puzzle, Ø8, griovelio ašys
        for AG in ACR_GEO.values():
            for P_ in AG["parts"] + AG["vparts"]:
                for gg in getattr(P_, "geoms", [P_]):
                    for ring in [gg.exterior] + list(gg.interiors):
                        sh.draw_polyline([P(c_) for c_ in ring.coords])
            for hx_, hy_ in AG["holes"]:
                sh.draw_circle(P((hx_, hy_)), ACRY["hole_d"] / 2 * k)
            for a_, b_ in AG["grooves"]:
                sh.draw_line(P(a_), P(b_))
    for r_ in (rails_ if not ACR_GEO else []):
        sh.draw_polyline([P(q) for q in r_["poly"]] + [P(r_["poly"][0])])
    for g, (px_, py_, ph_, hy_) in ears_:
        sh.draw_rect(fitz.Rect(P((px_, py_)), P((px_ + g["fpl_sz"], py_ + ph_))))
        sh.draw_circle(P((px_ + g["fpl_sz"] / 2, hy_)), EARS.get("hole_d", 6) / 2 * k)
    sh.finish(width=HW, color=C_FRAME, fill=None, closePath=False, oc=L_FRAME); sh.commit()
    if P10N_STUDS:                                      # v249: ilgasriegiai - montavimo šablonas (gręžimo taškai)
        L_ST = doc.add_ocg(f"4_FIXING_HOLES_{P10_ROD['label']}" if P6N_FIX else f"4_THREADED_RODS_{P10_ROD['label']}")
        sh = pg.new_shape()
        for _sx, _sy, _ in P10N_STUDS:
            sh.draw_circle(P((_sx, _sy)), P10_ROD["d"] / 2 * k)
            sh.draw_line(P((_sx - 8, _sy)), P((_sx + 8, _sy))); sh.draw_line(P((_sx, _sy - 8)), P((_sx, _sy + 8)))
        sh.finish(width=HW, color=(0.85, 0, 0.6), fill=None, closePath=False, oc=L_ST); sh.commit()
    if MOUNTING == "none" and SEP_PTS:                  # v268: laido išvestys (D11) šablone
        L_CB = doc.add_ocg("5_CABLE_EXITS_D11")
        sh = pg.new_shape()
        for _sx, _sy in SEP_PTS:
            sh.draw_circle(P((_sx, _sy)), 11 / 2 * k)
            sh.draw_line(P((_sx - 10, _sy)), P((_sx + 10, _sy))); sh.draw_line(P((_sx, _sy - 10)), P((_sx, _sy + 10)))
        sh.finish(width=HW, color=(0.85, 0.0, 0.0), fill=None, closePath=False, oc=L_CB); sh.commit()
    doc.save(path, garbage=3, deflate=True)
    print("OK 1:1", path, f"{bx1 - bx0:.0f} x {by1 - by0:.0f} mm, sluoksniai: raidės / dugnas -{inset} mm / rėmas")


if spec.get("export_1to1", True):
    export_1to1(os.path.splitext(OUT)[0].replace("_tech", "") + "_1-1.pdf")
if ACR_GEO:                                             # v229: akrilinio rėmo CNC DXF (dalys su puzzle, Ø8, griovelio ašys)
    import ezdxf as _ez
    _doc = _ez.new("R2010"); _doc.units = _ez.units.MM
    _GD = ACRY.get("groove") or {}
    _GL = f"GROOVE_BACK_{_GD.get('w', '?')}x{_GD.get('d', '?')}_DEEP"
    _ST = ACRY["stud"]
    _L5, _L12 = f"STUD_HOLE_D{_ST['d']:g}_THROUGH", f"COUNTERBORE_D{_ST['cb_d']:g}_DEPTH{_ST['cb_depth']:g}_BACK"
    for _ln, _cl in (("ACRYLIC_20_CUT", 7), ("HOLES_D%g" % ACRY["hole_d"], 3), ("GROOVE_BACK_AXIS", 2), (_GL, 4), (_L5, 1), (_L12, 6),
                     ("CABLE_SLOT_THROUGH", 30), ("TEXT", 8)):
        _doc.layers.add(_ln, color=_cl)
    _m = _doc.modelspace()
    _oy = 0.0
    for _gn, AG in ACR_GEO.items():
        _ymax = AG["F"].bounds[3]
        Q = lambda q, _y=_ymax, _o=_oy: (round(q[0], 3), round(_y - q[1] + _o, 3))       # y aukštyn
        for P_ in AG["parts"] + AG["vparts"]:
            for gg in getattr(P_, "geoms", [P_]):
                for ring in [gg.exterior] + list(gg.interiors):
                    _m.add_lwpolyline([Q(c_) for c_ in ring.coords], close=True, dxfattribs={"layer": "ACRYLIC_20_CUT"})
        for hx_, hy_ in AG["holes"]:
            _m.add_circle(Q((hx_, hy_)), ACRY["hole_d"] / 2, dxfattribs={"layer": "HOLES_D%g" % ACRY["hole_d"]})
        for sx_, sy_, _ in AG["studs"]:
            _m.add_circle(Q((sx_, sy_)), _ST["d"] / 2, dxfattribs={"layer": _L5})
            _m.add_circle(Q((sx_, sy_)), _ST["cb_d"] / 2, dxfattribs={"layer": _L12})
        for ox_, oy_ in AG["slots"]:
            _sl = _APt(ox_, oy_).buffer(AG["cslot"][1] / 2, 16)
            _sl = _aun([_sl, _APt(ox_ - (AG["cslot"][0] - AG["cslot"][1]) / 2, oy_).buffer(AG["cslot"][1] / 2, 16),
                        _APt(ox_ + (AG["cslot"][0] - AG["cslot"][1]) / 2, oy_).buffer(AG["cslot"][1] / 2, 16),
                        _abox(ox_ - (AG["cslot"][0] - AG["cslot"][1]) / 2, oy_ - AG["cslot"][1] / 2,
                              ox_ + (AG["cslot"][0] - AG["cslot"][1]) / 2, oy_ + AG["cslot"][1] / 2)])
            _m.add_lwpolyline([Q(c_) for c_ in _sl.exterior.coords], close=True, dxfattribs={"layer": "CABLE_SLOT_THROUGH"})
        _gw = float((ACRY.get("groove") or {}).get("w", 0) or 0)
        for a_, b_ in AG["grooves"]:
            _m.add_line(Q(a_), Q(b_), dxfattribs={"layer": "GROOVE_BACK_AXIS"})
            if _gw:                                     # v231: griovelio kontūras (plotis w, gylis d - nugaroje)
                _gp = _ALn([a_, b_]).buffer(_gw / 2, cap_style=2).intersection(AG["F"])
                for _gg in getattr(_gp, "geoms", [_gp]):
                    if hasattr(_gg, "exterior"):
                        _m.add_lwpolyline([Q(c_) for c_ in _gg.exterior.coords], close=True, dxfattribs={"layer": _GL})
        _m.add_text(f"{_gn}: CLEAR ACRYLIC {ACRY['thk']:g} mm frame, {len(AG['parts'])} parts (puzzle joints, clearance "
                    f"{ACRY['joint_clear']:g}), {len(AG['holes'])} x D{ACRY['hole_d']:g}, {len(AG['studs'])} x stud hole D{_ST['d']:g} + counterbore "
                    f"D{_ST['cb_d']:g} x {_ST['cb_depth']:g} from back, {len(AG['slots'])} cable slots through, cable groove on the back "
                    f"{_GD.get('w', '?')} wide x {_GD.get('d', '?')} deep; view FROM FRONT", dxfattribs={"layer": "TEXT", "height": 12}).set_placement((0, _oy - 40))
        _oy -= (AG["F"].bounds[3] - AG["F"].bounds[1]) + 200
    _dp = os.path.splitext(OUT)[0].replace("_tech", "") + "_akrilinis_remas.dxf"
    _doc.saveas(_dp)
    print("OK akrilinis rėmas DXF", _dp)
