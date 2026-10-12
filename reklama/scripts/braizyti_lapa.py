#!/usr/bin/env python3
"""A3 techninis lapas CAD stiliumi: P-profilio raidės ant folded plokštės.

Naudojimas:  python3 braizyti_lapa.py spec.json isvestis.pdf
Laukai - žr. assets/spec_pavyzdys.json. Reikšmė "?" arba su "PATIKSLINTI" rodoma raudonai.
Geometrija (raidės, matmenys, perimetras) imama iš kliento PDF automatiškai.
"""
import re
import json, math, os, sys, tempfile
import pymupdf as fitz
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.colors import HexColor, Color, white, black
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FD = "/usr/share/fonts/truetype/dejavu/"
SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ISO = os.path.join(SKILL, "assets", "osifont.ttf")   # ISO 3098 šriftas (LGPL, font exception)
_GOST = os.path.join(SKILL, "assets", "gost_common.ttf")   # GOST Common (Rytio šriftas, Rytis patvirtino 2026-10-07)
if os.path.exists(_GOST):
    pdfmetrics.registerFont(TTFont("F", _GOST)); pdfmetrics.registerFont(TTFont("FB", _GOST))
elif os.path.exists(_ISO):
    pdfmetrics.registerFont(TTFont("F", _ISO)); pdfmetrics.registerFont(TTFont("FB", _ISO))
else:
    pdfmetrics.registerFont(TTFont("F", FD + "DejaVuSansCondensed.ttf"))
    pdfmetrics.registerFont(TTFont("FB", FD + "DejaVuSansCondensed-Bold.ttf"))
# GOST Common: kai kurių simbolių kodai šrifte sumaišyti (Ø -> Ý, ° -> ¹, ± -> ¼) - pakeičiami tinkamais glifais
_GFIX = str.maketrans({"Ø": "⌀", "ø": "⌀", "°": "˚", "±": "+/-"}) if os.path.exists(_GOST) else {}
RAL = {"6039": "#8FB03E", "8001": "#9D622B", "4010": "#BC4077", "2008": "#F75E25", "1011": "#8A6642", "5003": "#1D334A", "5002": "#1E2460", "5015": "#2271B3", "3000": "#A72920", "6005": "#114232", "7021": "#23282B", "7024": "#474A51", "9003": "#F4F4F4", "9001": "#FDF4E3", "1003": "#F9A800", "2004": "#F44611", "3005": "#5E2129", "6029": "#20603D", "8017": "#45322E", "1019": "#A08F7A", "6024": "#308446", "5005": "#154889", "5010": "#0E4C8C", "3020": "#C1121C", "1023": "#F7B500", "6018": "#57A639", "9005": "#0E0E10", "7044": "#CAC4B0", "3009": "#642424", "9010": "#F1EDE1", "9016": "#F1F0EA", "7016": "#383E42", "5013": "#25314B", "9006": "#A5A8A6", "8014": "#4A3526", "8011": "#5A3826"}
RED = HexColor("#C8102E")
GREY = HexColor("#6E6E6E")
EXT = HexColor("#7A7A7A")
MM = 72 / 25.4  # pt viename popieriaus mm

spec = json.load(open(sys.argv[1]))
OUT = sys.argv[2]
W, H = landscape(A3)
tmp_pdf = tempfile.mktemp(suffix=".pdf")
c = canvas.Canvas(tmp_pdf, pagesize=(W, H))
c.setTitle(spec.get("file_code", "drawing"))


def ralhex(code):
    return RAL.get(str(code).replace("RAL", "").strip(), "#888888")


def unk(s):
    s = str(s)
    return "PATIKSLINTI" in s or s.strip() == "?" or s.strip().endswith("?")


def Y(y):
    return H - y


# ============================================================ geometrija iš kliento PDF
page = fitz.open(spec["client_pdf"])[spec.get("page", 0)]
fills = [d for d in page.get_drawings() if d.get("fill") is not None]
bg = max(fills, key=lambda d: d["rect"].width * d["rect"].height)
_bp = [q for it in bg["items"] for q in it[1:] if hasattr(q, "x")]
for it in bg["items"]:
    if it[0] == "re":
        _bp += [it[1].tl, it[1].tr, it[1].br, it[1].bl]
    if it[0] == "qu":
        _bp += [it[1].ul, it[1].ur, it[1].lr, it[1].ll]
B = fitz.Rect(min(q.x for q in _bp), min(q.y for q in _bp), max(q.x for q in _bp), max(q.y for q in _bp))
S = (spec["scale"] * 25.4 / 72) if spec.get("scale") else spec["ref_mm"] / B.width


def tomm(p):
    return ((p[0] - B.x0) * S, (p[1] - B.y0) * S)


elements = []
for d in fills:
    r, (cr, cg, cb) = d["rect"], d["fill"][:3]
    if d is bg or (cr > 0.75 and cg < 0.25 and cb > 0.35) or max(r.width, r.height) * S < 30:
        continue  # fonas, magenta matmenų rodyklės, smulkmė
    subs, cur, last = [], [], None
    for it in d["items"]:
        k_ = it[0]
        if k_ in ("re", "qu"):
            pts = ([(it[1].x0, it[1].y0), (it[1].x1, it[1].y0), (it[1].x1, it[1].y1), (it[1].x0, it[1].y1)]
                   if k_ == "re" else [(q.x, q.y) for q in (it[1].ul, it[1].ur, it[1].lr, it[1].ll)])
            if cur:
                subs.append(cur); cur = []
            subs.append([("M", pts[0])] + [("L", q) for q in pts[1:]]); last = None
            continue
        p0 = (it[1].x, it[1].y)
        if last is None or math.dist(p0, last) > 0.01:
            if cur:
                subs.append(cur)
            cur = [("M", p0)]
        if k_ == "l":
            cur.append(("L", (it[2].x, it[2].y))); last = (it[2].x, it[2].y)
        elif k_ == "c":
            cur.append(("C", (it[2].x, it[2].y), (it[3].x, it[3].y), (it[4].x, it[4].y))); last = (it[4].x, it[4].y)
    if cur:
        subs.append(cur)
    elements.append({"fill": tuple(d["fill"][:3]), "sub": [[(s[0],) + tuple(tomm(q) for q in s[1:]) for s in sp] for sp in subs],
                     "bb": ((r.x0 - B.x0) * S, (r.y0 - B.y0) * S, (r.x1 - B.x0) * S, (r.y1 - B.y0) * S)})
PW, PH = B.width * S, B.height * S
from shapely.geometry import Polygon as _Poly, LineString as _LS, Point as _Pt
from shapely.geometry.polygon import orient as _orient
# fono kontūras (gali būti ne stačiakampis, pvz. lygiagretainis)
_pp = []
for q in _bp:
    m_ = ((q.x - B.x0) * S, (q.y - B.y0) * S)
    if not _pp or math.dist(_pp[-1], m_) > 0.5:
        _pp.append(m_)
PANEL_G = _orient(_Poly(_pp).buffer(0).simplify(0.5), 1.0)
PANEL = list(PANEL_G.exterior.coords)[:-1]
EDGES = []
for i_ in range(len(PANEL)):
    a_, b_ = PANEL[i_], PANEL[(i_ + 1) % len(PANEL)]
    L_ = math.dist(a_, b_)
    if L_ < 1:
        continue
    u_ = ((b_[0] - a_[0]) / L_, (b_[1] - a_[1]) / L_)
    EDGES.append({"a": a_, "b": b_, "len": L_, "u": u_, "n": (u_[1], -u_[0])})   # n - išorinė normalė
IS_RECT = len(EDGES) == 4 and all(abs(e["u"][0]) < 1e-3 or abs(e["u"][1]) < 1e-3 for e in EDGES)


def _vcut(x):
    g_ = PANEL_G.intersection(_LS([(x, -1e5), (x, 1e5)]))
    ys_ = [c_[1] for c_ in getattr(g_, "coords", [])] or [c_[1] for gg in getattr(g_, "geoms", []) for c_ in gg.coords]
    return (min(ys_), max(ys_)) if ys_ else (0, PH)


def top_y(x):
    return _vcut(min(max(x, 0.01), PW - 0.01))[0]


def bot_y(x):
    return _vcut(min(max(x, 0.01), PW - 0.01))[1]


def edge_of(pos):
    cand = [e for e in EDGES if (e["n"][1] < -0.5 if pos == "top" else e["n"][1] > 0.5)]
    return max(cand, key=lambda e: e["len"]) if cand else None


LEFT_TOP, LEFT_BOT = top_y(0), bot_y(0)
TOP_E = edge_of("top")
SLOPE_DEG = abs(math.degrees(math.atan2(TOP_E["u"][1], TOP_E["u"][0]))) if TOP_E else 0
if SLOPE_DEG > 90:
    SLOPE_DEG = 180 - SLOPE_DEG


def _flat(sp, n=8):
    pts, cur = [], None
    for s_ in sp:
        if s_[0] in ("M", "L"):
            cur = s_[1]; pts.append(cur)
        else:
            p0, (p1, p2, p3_) = cur, s_[1:]
            for i in range(1, n + 1):
                t = i / n
                pts.append(tuple((1 - t) ** 3 * a + 3 * (1 - t) ** 2 * t * b + 3 * (1 - t) * t * t * cc + t ** 3 * dd
                                 for a, b, cc, dd in zip(p0, p1, p2, p3_)))
            cur = p3_
    return pts


from shapely.geometry import Polygon as _Poly, Point as _Pt
_letters = []
for e in elements:  # vienas kelias gali turėti kelias raides - skaidom: išoriniai kontūrai + jų skylės
    polys = []
    for sp in e["sub"]:
        f = _flat(sp)
        if len(f) >= 3:
            polys.append((_Poly(f).buffer(0), sp, f))
    polys.sort(key=lambda t: -t[0].area)
    groups = []
    for pg, sp, f in polys:
        host = None
        for g in groups:
            if g["outer"].contains(pg.representative_point()) and g["outer"].area > pg.area:
                host = g; break
        if host:
            host["sub"].append(sp); host["pts"] += f
        else:
            groups.append({"outer": pg, "sub": [sp], "pts": list(f)})
    for g in groups:
        xs_, ys_ = [q[0] for q in g["pts"]], [q[1] for q in g["pts"]]
        _letters.append({"fill": e.get("fill"), "sub": g["sub"], "bb": (min(xs_), min(ys_), max(xs_), max(ys_))})
elements = _letters

elements.sort(key=lambda e: e["bb"][1])
rows = []
for e in elements:
    if rows and e["bb"][1] < rows[-1]["ymax"] - 1:
        rows[-1]["els"].append(e); rows[-1]["ymax"] = max(rows[-1]["ymax"], e["bb"][3])
    else:
        rows.append({"els": [e], "ymax": e["bb"][3]})


def med(v):
    v = sorted(v); return v[len(v) // 2]


for r in rows:  # nominalus eilutės aukštis = mediana (O/S apvalumų išsikišimas neįskaičiuojamas)
    r["x0"] = min(e["bb"][0] for e in r["els"]); r["x1"] = max(e["bb"][2] for e in r["els"])
    r["y0"] = med([e["bb"][1] for e in r["els"]]); r["y1"] = med([e["bb"][3] for e in r["els"]])
    r["h"] = r["y1"] - r["y0"]; r["thin"] = r["h"] < 25


def perim(sub):
    L = 0
    for sp in sub:
        cur = start = None
        for s in sp:
            if s[0] == "M":
                cur = start = s[1]
            elif s[0] == "L":
                L += math.dist(cur, s[1]); cur = s[1]
            else:
                p0, (p1, p2, p3), prev = cur, s[1:], cur
                for i in range(1, 17):
                    t = i / 16
                    q = tuple((1 - t) ** 3 * a + 3 * (1 - t) ** 2 * t * b + 3 * (1 - t) * t * t * cc + t ** 3 * dd
                              for a, b, cc, dd in zip(p0, p1, p2, p3))
                    L += math.dist(prev, q); prev = q
                cur = p3
        if cur and start:
            L += math.dist(cur, start)
    return L


PER_L = sum(perim(e["sub"]) for r in rows if not r["thin"] for e in r["els"]) / 1000
PER_T = sum(perim(e["sub"]) for r in rows if r["thin"] for e in r["els"]) / 1000
from functools import reduce as _red
_A = 0.0
for r in rows:
    if r["thin"]:
        continue
    for e in r["els"]:
        _ps = [_Poly(_flat(sp)).buffer(0) for sp in e["sub"] if len(_flat(sp)) >= 3]
        if _ps:
            _A += _red(lambda a, b: a.symmetric_difference(b), _ps).area
A_FACE = _A / 1e6                                       # raidžių priekio plotas, m2
A_RET = PER_L * spec["depth_mm"] / 1000                # raidžių šonų plotas, m2

# ============================================================ piešimo primityvai


def path_of(sub, tf):
    p = c.beginPath()
    for sp in sub:
        for s in sp:
            if s[0] == "M":
                p.moveTo(*tf(*s[1]))
            elif s[0] == "L":
                p.lineTo(*tf(*s[1]))
            else:
                a, b, d = tf(*s[1]), tf(*s[2]), tf(*s[3]); p.curveTo(a[0], a[1], b[0], b[1], d[0], d[1])
        p.close()
    return p


def draw_letters(tf, fill=None, stroke=None, lw=0.3, dash=None):
    c.saveState()
    if fill is not None:
        c.setFillColor(fill)
    if stroke is not None:
        c.setStrokeColor(stroke); c.setLineWidth(HAIR if VIEW_MODE else lw)
    if dash:
        c.setDash(*dash)
    for e in sorted(elements, key=lambda e: -(e["bb"][2] - e["bb"][0]) * (e["bb"][3] - e["bb"][1])):
        if fill is not None and spec.get("element_colors") and e.get("fill"):   # v10: kiekvienas elementas savo spalva
            c.setFillColor(Color(*e["fill"]))
        c.drawPath(path_of(e["sub"], tf), stroke=stroke is not None, fill=fill is not None, fillMode=0)
    c.restoreState()


def T(x, y, s, size=7.5, font="F", color=black, align="l", rot=0, auto_red=True, fit=None):
    s = str(s)
    if any(ch in s for ch in "ÅåÆæø") and os.path.exists(_ISO) and font in ("F", "FB"):
        # v11: GOST Common neturi Å/Æ/Ø (norvegų pavadinimai) - visa eilutė osifont šriftu
        if "FI" not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont("FI", _ISO))
        font = "FI"
    else:
        s = s.translate(_GFIX)
    if fit and s and pdfmetrics.stringWidth(s, font, size) > fit:      # netelpa langelyje - mažinti šriftą
        size = max(size * 0.72, size * fit / pdfmetrics.stringWidth(s, font, size))
    blank_line = False
    if auto_red and unk(s):          # nežinoma reikšmė - tuščia vieta įrašymui pagal faktą
        s = s.replace("PATIKSLINTI", "").replace("?", "").rstrip(" ,;-")
        blank_line = s.endswith(":")
    c.saveState()
    col = color
    c.setFillColor(col); c.setStrokeColor(col)
    c.translate(x, Y(y)); c.rotate(rot)
    w_ = pdfmetrics.stringWidth(s, font, size)
    x0_ = {"l": 0, "c": -w_ / 2, "r": -w_}[align]
    t_ = c.beginText(x0_, 0); t_.setFont(font, size)
    if font == "FB":
        t_.setTextRenderMode(2); c.setLineWidth(size * 0.045)
    t_.textOut(s); c.drawText(t_)
    if blank_line:
        c.setLineWidth(0.3); c.setStrokeColor(black); c.line(x0_ + w_ + 3, -1, x0_ + w_ + 90, -1)
    c.restoreState()


HAIR = 0.1          # hairline - visų objektų kontūrai projekcijose ir pjūviuose
VIEW_MODE = False   # True - piešiamos projekcijos / pjūviai (storesni kontūrai -> hairline)


def _lw(w):
    return HAIR if VIEW_MODE and w > HAIR else w      # v63: projekcijose VISOS linijos hairline


def line(x1, y1, x2, y2, w=0.3, col=black, dash=None):
    c.saveState(); c.setStrokeColor(col); c.setLineWidth(_lw(w))
    if dash:
        c.setDash(*dash)
    c.line(x1, Y(y1), x2, Y(y2)); c.restoreState()


def rect(x, y, w, h, fill=None, stroke=black, lw=0.5, dash=None):
    c.saveState()
    if fill is not None:
        c.setFillColor(fill)
    if stroke is not None:
        c.setStrokeColor(stroke); c.setLineWidth(_lw(lw))
    if dash:
        c.setDash(*dash)
    c.rect(x, Y(y + h), w, h, stroke=stroke is not None, fill=fill is not None)
    c.restoreState()


def poly(pts, fill=None, stroke=black, lw=0.5, close=True):
    c.saveState()
    if fill is not None:
        c.setFillColor(fill)
    if stroke is not None:
        c.setStrokeColor(stroke); c.setLineWidth(_lw(lw))
    p = c.beginPath(); p.moveTo(pts[0][0], Y(pts[0][1]))
    for q in pts[1:]:
        p.lineTo(q[0], Y(q[1]))
    if close:
        p.close()
    c.drawPath(p, stroke=stroke is not None, fill=fill is not None)
    c.restoreState()


def arrowhead(x, y, ang):
    c.saveState(); c.setFillColor(black); c.translate(x, Y(y)); c.rotate(ang)
    p = c.beginPath(); p.moveTo(0, 0); p.lineTo(-5.5, 1.3); p.lineTo(-5.5, -1.3); p.close()
    c.drawPath(p, stroke=0, fill=1); c.restoreState()


def hdim(x1, x2, y, label, e1=None, e2=None, size=8, small_side="r"):
    """horizontalus matmuo; e1/e2 - y, iš kurio kyla išvadinė linija (None = be jos)"""
    for x, e in ((x1, e1), (x2, e2)):
        if e is not None:
            sgn = 1 if e > y else -1
            line(x, e - 2 * sgn, x, y - 3 * sgn, 0.25, EXT)
    line(x1, y, x2, y, 0.3)
    if x2 - x1 > 16:
        arrowhead(x1, y, 180); arrowhead(x2, y, 0)
        T((x1 + x2) / 2, y - 2.5, label, size, align="c")
    else:
        arrowhead(x1, y, 0); arrowhead(x2, y, 180)
        line(x1 - 8, y, x1, y, 0.3); line(x2, y, x2 + 8, y, 0.3)
        if small_side == "l":
            T(x1 - 10, y + 2.5, label, size, align="r")
        else:
            T(x2 + 10, y + 2.5, label, size)


def vchain(x, ys, ext_to, labels, size=8):
    """vertikali grandininė matmenų eilė; ys - y (pt), ext_to - x, iki kurio eina išvadinės"""
    for y, ex in zip(ys, ext_to):
        line(x - 3, y, ex - 2, y, 0.25, EXT)
    line(x, ys[0], x, ys[-1], 0.3)
    for a, b, lab in zip(ys[:-1], ys[1:], labels):
        if b - a > 14:
            arrowhead(x, a, 90); arrowhead(x, b, -90)
            T(x - 2.5, (a + b) / 2, lab, size, align="c", rot=90)
        else:
            arrowhead(x, a, -90); arrowhead(x, b, 90)
            T(x + 3, (a + b) / 2 + 2.6, lab, size)


def balloon(x, y, n, r=6.5):
    c.saveState(); c.setFillColor(white); c.setStrokeColor(black); c.setLineWidth(0.5)
    c.circle(x, Y(y), r, stroke=1, fill=1); c.restoreState()
    T(x, y + 2.8, n, 8, font="FB", align="c")                      # v18: >= 8 pt


def leader(x1, y1, x2, y2, n, halo=False):
    if halo:                                    # v13: matoma ir ant tamsaus fono (baltas apvadas)
        line(x1, y1, x2, y2, 1.4, white)
    line(x1, y1, x2, y2, 0.3)
    c.saveState(); c.setFillColor(black); c.circle(x1, Y(y1), 1.1, stroke=0, fill=1); c.restoreState()
    balloon(x2, y2, n)


def view_title(xc, y, title, scale):                 # v18: kaip lapas_core - pavadinimas 13 pt, mastelis 9 pt
    T(xc, y, title, 13, font="FB", align="c")
    w = pdfmetrics.stringWidth(title, "FB", 13)
    line(xc - w / 2, y + 3, xc + w / 2, y + 3, 0.7)
    T(xc, y + 15, scale, 9, align="c", color=GREY)


def hatch(x, y, w, h, step=5):
    c.saveState()
    p = c.beginPath(); p.rect(x, Y(y + h), w, h); c.clipPath(p, stroke=0, fill=0)
    c.setStrokeColor(GREY); c.setLineWidth(0.25)
    for i in range(-int(h), int(w) + int(h), step):
        c.line(x + i, Y(y + h), x + i + h, Y(y))
    c.restoreState()
    rect(x, y, w, h, lw=0.4)


# ============================================================ rėmelis + zonos (kairė paraštė 20 mm)
OX0, OY0, OX1, OY1 = 20 * MM, 10 * MM, W - 10 * MM, H - 10 * MM
B5 = 5 * MM
IX0, IY0, IX1, IY1 = OX0 + B5, OY0 + B5, OX1 - B5, OY1 - B5
rect(OX0, OY0, OX1 - OX0, OY1 - OY0, lw=0.5)
rect(IX0, IY0, IX1 - IX0, IY1 - IY0, lw=1.0)
for i in range(8):
    x0, x1 = IX0 + (IX1 - IX0) * i / 8, IX0 + (IX1 - IX0) * (i + 1) / 8
    for yb in ((OY0 + IY0) / 2 + 2.5, (OY1 + IY1) / 2 + 2.5):
        T((x0 + x1) / 2, yb, i + 1, 8, align="c", color=GREY)
    if i:
        line(x0, OY0, x0, IY0, 0.3); line(x0, IY1, x0, OY1, 0.3)
for j in range(6):
    y0, y1 = IY0 + (IY1 - IY0) * j / 6, IY0 + (IY1 - IY0) * (j + 1) / 6
    for xb in ((OX0 + IX0) / 2, (OX1 + IX1) / 2):
        T(xb, (y0 + y1) / 2 + 2.5, "ABCDEF"[j], 8, align="c", color=GREY)
    if j:
        line(OX0, y0, IX0, y0, 0.3); line(IX1, y0, OX1, y0, 0.3)

RCX = IX1              # vaizdai naudoja visą plotį
BAND_H = max(172, 32 + 11 * max(len(spec.get("bom", [])), 14))   # v18: eilutė >= 11 pt (8 pt tekstas, nesugrūsta)
BAND_Y = IY1 - BAND_H   # apatinė informacijos juosta
VIEW_BOT = BAND_Y - 14  # vaizdų zonos apačia

# v28: fono plokštė iš kelių dalių (box lid joints) - tik stačiakampiam fonui
JOINTS = sorted(float(j) for j in spec.get("panel_joints", []))
JTOP = 32 if JOINTS else 0
VIEW_MODE = True
# ============================================================ VAIZDAS IŠ PRIEKIO 1:10
STD = [2, 5, 10, 15, 20, 25, 50, 100]   # ISO 5455 eilė + praktikoje naudojami 1:15, 1:25
depth, bend = spec["depth_mm"], spec["bend_mm"]
# ---------------- automatinis išdėstymas: projekcijos panašaus dydžio, be didelių tuščių plotų
VX0, VY0 = IX0 + 8, IY0 + 6
W_AV, H_AV = IX1 - IX0 - 16, VIEW_BOT - IY0 - 10
_leg = spec.get("l_profile", {}).get("leg", 30)
_TM = rows[0]["y0"] - top_y((rows[0]["x0"] + rows[0]["x1"]) / 2)
_SEG1 = _leg + 2 + 8
_dk = MM / 2
_core = (_SEG1 * _dk + 16 + 62 * _dk) if _TM > _SEG1 + 20 else (_TM + 52) * _dk
D_W = (bend + depth) * _dk + 40 + 15 * _dk + 34
D_H = 26 + _core + 16 + 60


def fs_box(n):
    s_ = MM / n; fw_ = PW * s_; fh_ = PH * s_; g_ = max(50, 0.11 * fw_)
    mL = 46 if IS_RECT else 64
    right = max(fw_ + g_ + (depth + bend) * s_ + 12, fw_ + g_ + (depth + bend) * s_ / 2 + 48)
    return mL + right, 46 + JTOP + fh_ + 60


def r_box(n):
    s_ = MM / n
    return 20 + PW * s_ + (30 if IS_RECT else 48), 44 + PH * s_ + 64


# 3D turinio proporcija (su siena), kad būtų galima įvertinti jo dydį langelyje
_TH, _PHI = math.radians(spec.get("view_yaw", 32)), math.radians(spec.get("view_pitch", 17))


def _rot0(x, y, z):
    x1, z1 = x * math.cos(_TH) + z * math.sin(_TH), -x * math.sin(_TH) + z * math.cos(_TH)
    return x1, y * math.cos(_PHI) - z1 * math.sin(_PHI)


_WM = 0
_ip = [_rot0(x, y, -bend) for x in (-_WM, PW + _WM) for y in (-_WM * 0.8, PH + _WM * 0.8)]
_ip += [_rot0(x, y, depth) for x in (0, PW) for y in (0, PH)]
ISO_EW = max(p[0] for p in _ip) - min(p[0] for p in _ip)
ISO_EH = max(p[1] for p in _ip) - min(p[1] for p in _ip)

LAYS = [[["FS"], ["D", "R", "I"]], [["FS", "R", "D"], ["I"]], [["FS", "R"], ["D", "I"]],
        [["FS", "D"], ["R", "I"]], [["FS", "I"], ["D", "R"]], [["FS", "D", "I"], ["R"]]]
best = None
for lay in LAYS:
    for n1 in STD:
        for n2 in STD:
            if n2 < n1 or n2 > n1 * 2.5:
                continue
            sz = {"FS": fs_box(n1), "R": r_box(n2), "D": (D_W, D_H)}
            ok, rows_h, iso = True, [], None
            fixed_h = [max([sz[b][1] for b in r if b != "I"], default=0) for r in lay]
            for ri, r in enumerate(lay):
                ws = sum(sz[b][0] for b in r if b != "I") + 14 * (len(r) - 1)
                if ws > W_AV:
                    ok = False; break
                h_ = fixed_h[ri]
                if "I" in r:
                    if h_ == 0:   # 3D vienas eilutėje - gauna likusį aukštį
                        h_ = H_AV - sum(fixed_h) - 14 * (len(lay) - 1)
                    iso = (W_AV - ws - (14 if len(r) > 1 else 0), h_)
                rows_h.append(h_)
            if not ok or sum(rows_h) + 14 * (len(lay) - 1) > H_AV or not iso or iso[0] < 170 or iso[1] < 140:
                continue
            kk = min(iso[0] / ISO_EW, (iso[1] - 30) / ISO_EH)
            a_iso = kk * kk * ISO_EW * ISO_EH
            s1, s2 = MM / n1, MM / n2
            a_f, a_r = (PW * s1) * (PH * s1), (PW * s2) * (PH * s2)
            used = sum(sz[b_][0] * sz[b_][1] for r in lay for b_ in r if b_ != "I") + a_iso
            # didesni vaizdai + panašus jų dydis + kuo mažiau tuščios vietos
            score = 3 * (a_f * a_r * a_iso) ** (1 / 3) + 0.3 * used + (3000 if n1 == n2 else 0)
            if not best or score > best[0]:
                best = (score, lay, n1, n2, rows_h, sz, iso)
_, LAY, SC1, SC2, ROWS_H, SZ, ISO_CELL = best
TALL = LAY[0] != ["FS"]
# pozicijos: laisva vieta paskirstoma tolygiai tarp eilučių ir blokų
POS = {}
free_v = H_AV - sum(ROWS_H)
vg = free_v / (len(LAY) + 1)
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
s10 = MM / SC1
GAPV = max(50, 0.11 * PW * s10)                         # tarpas tarp priekio ir šono vaizdų
FVX, FVY = POS["FS"][0] + (46 if IS_RECT else 64), POS["FS"][1] + 46 + JTOP
fw, fh = PW * s10, PH * s10
bgc = HexColor(ralhex(spec["background_ral"]))
facec = HexColor(spec.get("face_hex", "#FFFFFF"))
retc = HexColor(ralhex(spec["return_ral"]))
poly([(FVX + x * s10, FVY + y * s10) for x, y in PANEL], fill=bgc, lw=0.7)
draw_letters(lambda x, y: (FVX + x * s10, Y(FVY + y * s10)), fill=facec)

hdim(FVX, FVX + fw, FVY - 36, f"{PW:.0f}", FVY + top_y(0) * s10, FVY + top_y(PW) * s10, size=12)
top = rows[0]
hdim(FVX + top["x0"] * s10, FVX + top["x1"] * s10, FVY - 18, round(top['x1']) - round(top['x0']),
     FVY + top["y0"] * s10, FVY + top["y0"] * s10, size=12)
bot = rows[-1]
xs = [0, round(bot["x0"]), round(bot["x1"]), round(PW)]
yb = FVY + fh + 16
for xx, ey in zip(xs, (FVY + bot_y(0) * s10, FVY + bot["y1"] * s10, FVY + bot["y1"] * s10, FVY + bot_y(PW) * s10)):
    line(FVX + xx * s10, ey + 2, FVX + xx * s10, yb + 3, 0.25, EXT)
line(FVX, yb, FVX + fw, yb, 0.3)
for a, b in zip(xs[:-1], xs[1:]):
    arrowhead(FVX + a * s10, yb, 180); arrowhead(FVX + b * s10, yb, 0)
    T(FVX + (a + b) / 2 * s10, yb - 2.5, b - a, 12, align="c")

marks = [round(LEFT_TOP)]
for r in rows:
    marks += [round(r["y0"]), round(r["y1"])]
marks.append(round(LEFT_BOT))
ext_x = [FVX] + sum(([FVX + r["x0"] * s10] * 2 for r in rows), []) + [FVX]
vchain(FVX - 16, [FVY + m * s10 for m in marks], ext_x, [str(b - a) for a, b in zip(marks[:-1], marks[1:])], size=12)
if IS_RECT:
    vchain(FVX - 34, [FVY, FVY + fh], [FVX, FVX], [f"{PH:.0f}"], size=12)
else:
    # bendras aukštis (iki aukščiausio / žemiausio taško) + pakilimas + nuolydžio kampas
    ytop_x = min((x for x, y in PANEL if abs(y) < 0.5), default=0)
    ybot_x = min((x for x, y in PANEL if abs(y - PH) < 0.5), default=0)
    vchain(FVX - 34, [FVY, FVY + LEFT_TOP * s10], [FVX + ytop_x * s10, FVX], [f"{LEFT_TOP:.0f}"], size=12)
    vchain(FVX - 52, [FVY, FVY + fh], [FVX + ytop_x * s10, FVX + ybot_x * s10], [f"{PH:.0f}"], size=12)
    # dešinės vertikalios kraštinės ilgis
    rx_e = max(EDGES, key=lambda e: e["n"][0])
    ry0_, ry1_ = sorted((rx_e["a"][1], rx_e["b"][1]))
    vchain(FVX + fw + 16, [FVY + ry0_ * s10, FVY + ry1_ * s10], [FVX + fw, FVX + fw], [f"{ry1_ - ry0_:.0f}"], size=12)
    # kampas prie kairio viršutinio kampo
    ax_, ay_ = FVX, FVY + LEFT_TOP * s10
    line(ax_, ay_, ax_ + 40, ay_, 0.25, EXT)
    c.saveState(); c.setLineWidth(0.3)
    _sg = 1 if LEFT_TOP > top_y(PW) else -1
    p_ = c.beginPath(); p_.arc(ax_ - 30, Y(ay_) - 30, ax_ + 30, Y(ay_) + 30, 0, _sg * SLOPE_DEG); c.drawPath(p_, stroke=1, fill=0)
    c.restoreState()
    T(ax_ + 33, ay_ - 3, f"{SLOPE_DEG:.0f}°", 12)
if JOINTS:   # v28: dalių jungtys - punktyras per foną + dalių grandinė viršuje
    _jx = [0] + JOINTS + [PW]
    for j_ in JOINTS:
        line(FVX + j_ * s10, FVY - 2, FVX + j_ * s10, FVY + fh + 2, 0.5, HexColor("#BDBDBD"), dash=(4, 2))
        line(FVX + j_ * s10, FVY - 62, FVX + j_ * s10, FVY - 2, 0.25, EXT)
        T(FVX + j_ * s10, FVY - 66, "PANEL JOINT", 8, align="c", auto_red=False)   # pastaba už reklamos ribų
    for xx in (0, PW):
        line(FVX + xx * s10, FVY - 52, FVX + xx * s10, FVY - 38, 0.25, EXT)
    _yj = FVY - 54
    line(FVX, _yj, FVX + fw, _yj, 0.3)
    for a, b in zip(_jx[:-1], _jx[1:]):
        arrowhead(FVX + a * s10, _yj, 180); arrowhead(FVX + b * s10, _yj, 0)
        T(FVX + (a + b) / 2 * s10, _yj - 2.5, f"{b - a:.0f}", 12, align="c")
view_title(FVX + fw / 2, FVY + fh + 46, "FRONT VIEW", f"SCALE 1:{SC1}")
# v13: pozicijų balionai priekio vaizde (pvz. P1 apskritimas) - [x_mm, y_mm, poz., dx_pt, dy_pt]
for _co in spec.get("callouts", {}).get("front", []):
    _x, _y = FVX + _co[0] * s10, FVY + _co[1] * s10
    leader(_x, _y, _x + _co[3], _y + _co[4], _co[2], halo=True)

# ============================================================ ŠONINIS VAIZDAS 1:10 (tikras vaizdas iš dešinės, ne pjūvis)
depth, bend = spec["depth_mm"], spec["bend_mm"]
SVF = FVX + fw + GAPV + depth * s10   # fono priekio plokštuma (raidės priekis - GAPV nuo priekio vaizdo)
lf = SVF - depth * s10
bx = SVF + bend * s10
# folded fono dešinysis užlenktas kraštas - matomas kaip pilnas paviršius
rect(SVF, FVY, bend * s10, fh, fill=HexColor("#2C2D31"), lw=0.7)
line(SVF + 0.9, FVY, SVF + 0.9, FVY + fh, 0.25, HexColor("#6A6B70"))   # lenkimo briauna
if not IS_RECT:   # dešinės kraštinės pabaiga - toliau matomas pasviręs užlenkimas
    _re = max(EDGES, key=lambda e: e["n"][0])
    for yy_ in (_re["a"][1], _re["b"][1]):
        if 0.5 < yy_ < PH - 0.5:
            line(SVF, FVY + yy_ * s10, SVF + bend * s10, FVY + yy_ * s10, 0.5, HexColor("#8A8B90"))
# raidžių siluetas iš šono: visų elementų aukščio intervalų sąjunga
ivs = sorted((e["bb"][1], e["bb"][3]) for r in rows for e in r["els"]
             if not (r["thin"] and spec.get("thin_row_flat")))
merged = []
for a_, b_ in ivs:
    if merged and a_ <= merged[-1][1] + 0.5:
        merged[-1][1] = max(merged[-1][1], b_)
    else:
        merged.append([a_, b_])
shade_ret = Color(retc.red * 0.86, retc.green * 0.86, retc.blue * 0.86)
_STACK = 0
if spec.get("element_colors"):          # v11: papildomi tūriniai elementai (pvz. P1 apskritimas + P6 „&" ant jo)
    _lays = []
    for e in elements:
        _on = any(o is not e and o["bb"][0] < e["bb"][0] and o["bb"][2] > e["bb"][2] and o["bb"][1] < e["bb"][1]
                  and o["bb"][3] > e["bb"][3] for o in elements)
        _rk = ",".join(str(round(v, 1)) for v in e["fill"])
        _rc = HexColor(ralhex(spec.get("element_return", {}).get(_rk, spec["return_ral"])))
        _lays.append((depth if _on else 0, e, _rc))
    _STACK = max(z for z, _, _ in _lays)
    for z_, e, _rc in sorted(_lays, key=lambda t: t[0]):
        y0_, h_ = FVY + e["bb"][1] * s10, (e["bb"][3] - e["bb"][1]) * s10
        x_ = lf - z_ * s10
        rect(x_, y0_, depth * s10, h_, fill=Color(_rc.red * 0.86, _rc.green * 0.86, _rc.blue * 0.86), lw=0.6)
        rect(x_, y0_, 0.9, h_, fill=Color(*e["fill"]), lw=0.4)
    if _STACK:
        _top = min(e["bb"][1] for z_, e, _ in _lays if z_)
        hdim(lf - _STACK * s10, lf, FVY + _top * s10 - 10, f"{_STACK:.0f}", FVY + _top * s10, FVY + _top * s10,
             small_side="l", size=12)
else:
    import p6_vaizdas as PV
    for a_, b_ in merged:                                    # v59: korpusas -1,5 | stiklo kraštas 3 | plėvelė
        PV.side_view(lf + depth * s10, FVY + a_ * s10, s10, a_, b_, depth, shade_ret, facec,
                     front=spec.get("front", "3mm+foil"), rect_fn=rect)
# matmenys
hdim(lf, SVF, FVY - 18, f"{depth:.0f}", FVY + merged[0][0] * s10, FVY, small_side="l", size=12)
hdim(SVF, bx, FVY - 18, f"{bend:.0f}", FVY, FVY, size=12)
hdim(lf - _STACK * s10, bx, FVY + fh + 16, f"{depth + bend + _STACK:.0f}", FVY + merged[-1][1] * s10, FVY + fh, size=12)
c.saveState(); c.setStrokeColor(black); c.setLineWidth(0.4); c.setDash(3, 1.5)
c.circle((SVF + bx) / 2 + 2, Y(FVY + 6), 12); c.restoreState()
T((SVF + bx) / 2 - 16, FVY - 4, "A", 9, font="FB", align="c")
# v13: balionai šoniniame vaizde - [atstumas nuo fono priekio mm, y_mm, poz., dx_pt, dy_pt]
for _co in spec.get("callouts", {}).get("side", []):
    _x, _y = SVF - _co[0] * s10, FVY + _co[1] * s10
    leader(_x, _y, _x + _co[3], _y + _co[4], _co[2], halo=True)
stw = pdfmetrics.stringWidth("SIDE VIEW (RIGHT)", "FB", 9)
view_title(min((lf + bx) / 2, RCX - 12 - stw / 2), FVY + fh + 46, "SIDE VIEW (RIGHT)", f"SCALE 1:{SC1}")

# ============================================================ L profiliai (standartas: 30x30x2 Alu, 25 mm nuo kraštų)
LP = {"size": "30x30x2", "leg": 30, "thk": 2, "offset_mm": 25, "positions": ["top", "bottom"]}
LP.update(spec.get("l_profile", {}))
L_EDGES = {pos: edge_of(pos) for pos in LP["positions"] if edge_of(pos)}
L_LENS = {pos: round(e["len"] - 2 * LP["offset_mm"]) for pos, e in L_EDGES.items()}
L_QTY = len(L_LENS)
L_TOTAL = sum(L_LENS.values())
L_LEN = list(L_LENS.values())[0] if L_LENS else 0
# varžtai fonas -> L: 50 mm nuo kraštų, žingsnis ~300 mm, tolygiai (simetriškai) per visą ilgį
SCR = {"spec": "DIN 7504 N 4.2x16 T20", "material": "Steel, hard.", "edge_mm": 50, "pitch_mm": 300,
       "hole_d": 3.2, "hole_edge_mm": 7}     # v37 (Rytis 2026-10-09): skylė Ø3.2 užlenktoje briaunoje, 7 mm nuo briaunos krašto
SCR.update(spec.get("screw", {}))
S_LAY = {}
for pos, e in L_EDGES.items():
    span_ = e["len"] - 2 * SCR["edge_mm"]
    n_ = max(1, round(span_ / SCR["pitch_mm"]))
    S_LAY[pos] = {"span": span_, "n": n_, "pitch": span_ / n_, "t": [SCR["edge_mm"] + i * span_ / n_ for i in range(n_ + 1)]}
PARTS = list(zip([0] + JOINTS, JOINTS + [PW])) if JOINTS else [(0, PW)]
L_SEGS, S_SEGS = [], []          # v28: L profiliai ir varžtai kiekvienai daliai atskirai
if JOINTS:
    for pos in L_EDGES:
        for x0_, x1_ in PARTS:
            L_SEGS.append((pos, x0_, x1_, round(x1_ - x0_ - 2 * LP["offset_mm"])))
            span_ = x1_ - x0_ - 2 * SCR["edge_mm"]
            n_ = max(1, round(span_ / SCR["pitch_mm"]))
            S_SEGS.append((pos, x0_, x1_, {"span": span_, "n": n_, "pitch": span_ / n_,
                                            "t": [SCR["edge_mm"] + i * span_ / n_ for i in range(n_ + 1)]}))
    L_QTY = len(L_SEGS); L_TOTAL = sum(l_[3] for l_ in L_SEGS)
_s0 = list(S_LAY.values())[0] if S_LAY else {"span": 0, "n": 1, "pitch": 0, "t": []}
S_SPAN, S_N, S_PITCH = _s0["span"], _s0["n"], _s0["pitch"]
S_POS = _s0["t"]
S_PER = S_N + 1
S_QTY = sum(len(v["t"]) for v in S_LAY.values())
if JOINTS:
    S_QTY = sum(len(v[3]["t"]) for v in S_SEGS)
    S_PER = "/".join(str(len(v[3]["t"])) for v in S_SEGS if v[0] == S_SEGS[0][0])
    from collections import Counter as _Cn
    _lc = _Cn(l_[3] for l_ in L_SEGS)
    L_LIST_M = " + ".join(f"{n_} x {l_ / 1000:.2f}" for l_, n_ in sorted(_lc.items()))
else:
    L_LIST_M = f"{L_QTY} x {L_LEN / 1000:.2f}"
f_p = (f"{S_PITCH:.0f}" if abs(S_PITCH - round(S_PITCH)) < 0.05 else f"{S_PITCH:.1f}")
# ---- v73 (Rytis 2026-10-10): tiekėjų formatai - L profiliai 6 m strypais, folded išklotinė į Alu lakštą (assets/medziagos.json)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import medziagos as MEDZ
_STK = MEDZ.cfg(spec.get("stock"))
_w = MEDZ.profile_warn(LP["size"], "L")          # v114: L profilis LT tiekėjų kataloge?
if _w:
    print(_w)
_L_ALL = [l_[3] for l_ in L_SEGS] if JOINTS else list(L_LENS.values())
_LB = MEDZ.nest_bars(_L_ALL, _STK["stock"], _STK["kerf"], _STK["end"])
L_BARS = len(_LB)
print(f"  L {LP['size']} strypai: {MEDZ.bars_text(_LB, _STK['stock'])} | atlieka {MEDZ.bars_waste(_LB, _STK['stock']) / 1000:.2f} m")
if _L_ALL and L_BARS > math.ceil(sum(_L_ALL) / _STK["stock"]):
    # L ilgis - standartas (plokštės plotis - 50), jo NETRUMPINAME; tik pasakome (pvz. 2 x 3000 + prapjova > 6000)
    print(f"  ! L profiliai {' + '.join(f'{v:.0f}' for v in _L_ALL)} netelpa į {math.ceil(sum(_L_ALL) / _STK['stock'])} strypą(-us) "
          f"(prapjova {_STK['kerf']:g} mm) - reikia {L_BARS}; L ilgis standartinis (plotis - 50) - nekeičiamas, Rytis sprendžia")
_SHEET = spec.get("sheet_material", "alu"); _SHT = spec.get("sheet_thk_mm", 2)
for _a, _b in PARTS:
    _fl = MEDZ.sheet_fit((_b - _a) + 2 * depth, PH + 2 * depth, _SHEET, _SHT)     # išklotinė ~ (L + 2·gylis) x (H + 2·gylis), paraštė 10
    print(f"  išklotinė {(_b - _a) + 2 * depth:.0f} x {PH + 2 * depth:.0f} ({_SHEET} {_SHT} mm): {MEDZ.sheet_text(_fl)}")
SUBS = {"{L_BARS}": str(L_BARS), "{BAR_M}": f"{_STK['stock'] / 1000:g}",
        "{L_LEN}": str(L_LEN), "{L_QTY}": str(L_QTY), "{L_TOTAL}": str(L_TOTAL), "{L_SIZE}": LP["size"],
        "{L_LEN_M}": f"{L_LEN / 1000:.2f}", "{L_TOTAL_M}": f"{L_TOTAL / 1000:.2f}",
        "{S_SPEC}": SCR["spec"], "{PER_L}": f"{PER_L:.2f}", "{A_FACE}": f"{A_FACE:.2f}", "{A_RET}": f"{A_RET:.2f}", "{S_QTY}": str(S_QTY), "{L_LIST_M}": L_LIST_M, "{PARTS}": " + ".join(f"{b - a:.0f}" for a, b in PARTS), "{N_PARTS}": str(len(PARTS)), "{S_PER}": str(S_PER), "{S_MAT}": SCR["material"]}


def subst(v):
    v = str(v)
    # v90 (Rytis 2026-10-11): BOM - tik bendras rezultatas, be sudėties (ne "1 + 1 + 2 = 4")
    v = re.sub(r"\{(RAIL_LIST_M|RAIL_LIST|PRAIL_LIST|PRAIL_LIST_M|L_LIST_M)\}\s*=\s*", "", v)
    v = v.replace("{RAIL_LIST_M}", "{RAIL_TOTAL_M}").replace("{RAIL_LIST}", "{RAIL_TOTAL}")
    for k_, r_ in SUBS.items():
        v = v.replace(k_, r_)
    return v


spec["bom"] = [[subst(x) for x in row] for row in spec["bom"]]
# v100 (Rytis 2026-10-11): „Letter back" - spalva = šonų spalva (standartas), kitokia - tik nurodžius (spec "back_ral")
_back_ral = spec.get("back_ral") or spec.get("return_ral")
if _back_ral:
    spec["bom"] = [([r_[0], r_[1], r_[2], f"RAL {_back_ral}", r_[4]] if re.search(r"letter back|\bback\b", str(r_[1]), re.I)
                    and not re.search(r"plate|foil|sheet", str(r_[1]), re.I) and str(r_[3]).strip() in ("", "-") else r_)
                   for r_ in spec["bom"]]
spec["notes"] = [subst(n) for n in spec.get("notes", [])]
spec["mounting"] = subst(spec["mounting"])

# ============================================================ DETALĖ A - PJŪVIS (CAD, pagal P6 profilio pjūvį)
LOW = FVY + fh + 58      # apatinės zonos pradžia priklauso nuo priekinio vaizdo aukščio
SECTION_C = HexColor("#111111")
tP = spec.get("panel_thk_nominal", 2.0)       # brėžiama nominaliai, tikras storis - BOM
tB, tR, tF = 1.5, 1.0, 3.0                     # P6: galas, šonas, priekis (nominaliai, pagal profilio pjūvį)
TM = rows[0]["y0"] - top_y((rows[0]["x0"] + rows[0]["x1"]) / 2)   # fono viršus -> raidės viršus (pjūvio vietoje)
SEG1 = LP["leg"] + tP + 8                     # viršutinis segmentas (fono kraštas + L)
SEG2_A, SEG2_B = TM - 10, TM + 52              # apatinis segmentas (raidės viršus)
BREAK = TM > SEG1 + 20
DSC = 2
DWX = POS["D"][0] + (bend + depth) * MM / DSC + 40   # sienos plokštuma
dk = MM / DSC
GAP = 16
DTOP = POS["D"][1] + 26


def du(u):
    return DWX - u * dk


def dv(v):
    if not BREAK or v <= SEG1:
        return DTOP + v * dk
    return DTOP + SEG1 * dk + GAP + (v - SEG2_A) * dk


V_END = SEG2_B if BREAK else TM + 62


def srect(u0, u1, v0, v1, fill=SECTION_C, lw=0.35, stroke=black):
    """pjūvio stačiakampis modelio mm (u - nuo sienos, v - žemyn nuo fono viršaus); tarpas ties lūžiu praleidžiamas"""
    segs = [(v0, v1)]
    if BREAK and v0 < SEG2_A and v1 > SEG1:
        segs = [(v0, SEG1), (SEG2_A, v1)]
    for a_, b_ in segs:
        if b_ <= a_:
            continue
        x0_, x1_ = sorted((du(u0), du(u1)))
        rect(x0_, dv(a_), max(x1_ - x0_, 0.6), max(dv(b_) - dv(a_), 0.6), fill=fill, stroke=stroke, lw=lw)


def zig(x0_, x1_, y_):
    n_ = max(2, int((x1_ - x0_) / 6))
    pts = [(x0_ - 3, y_)]
    for i in range(n_ + 1):
        pts.append((x0_ + (x1_ - x0_) * i / n_, y_ + (2 if i % 2 else -2)))
    pts.append((x1_ + 3, y_))
    poly(pts, stroke=black, lw=0.35, close=False)


# siena
wall_bot = dv(V_END) + 4
# folded fonas: viršutinis kraštas + priekinė plokštė
srect(0, bend, 0, tP)
srect(bend - tP, bend, 0, V_END)
# L profilis
srect(0, LP["leg"], tP, tP + LP["thk"])
srect(0, LP["thk"], tP, tP + LP["leg"])
# varžtas fonas -> L (iš viršaus)
su = SCR["hole_edge_mm"]                      # v37: varžto ašis 7 mm nuo užlenktos briaunos krašto
rect(du(su) - 4 * dk, dv(-2.5), 8 * dk, 2.5 * dk, fill=white, lw=0.4)
rect(du(su) - 2.1 * dk, dv(0), 4.2 * dk, (tP + LP["thk"] + 9) * dk, fill=white, lw=0.4)
line(du(su), dv(-4), du(su), dv(tP + LP["thk"] + 11), 0.2, GREY, dash=([4, 1, 1, 1], 0))
# tvirtinimas į sieną per L stovą
wv = tP + LP["leg"] * 0.6
rect(du(LP["thk"] + 2.5), dv(wv) - 4 * dk, 2.5 * dk, 8 * dk, fill=white, lw=0.4)
rect(du(LP["thk"]), dv(wv) - 3 * dk, 15 * dk, 6 * dk, fill=white, lw=0.4)
line(du(LP["thk"] + 4), dv(wv), DWX + 15 * dk + 3, dv(wv), 0.2, GREY, dash=([4, 1, 1, 1], 0))
# P6 raidė: galas, viršutinis šonas, priekis (plexi), PVC kraštas + varžtas, LED, tvirtinimas prie fono
srect(bend, bend + tB, TM, V_END)
import p6_front as P6F   # v90
F8_D = P6F.milled(spec.get("front", "3mm"))
if F8_D:   # v28: P6_8mm - plexi 8 mm, frezuota briauna (liežuvis šonų viduje), varžtas per šoną į liežuvį
    tLip = 3.0                                             # matomas kantelis 3 mm
    tTg = max(5.0, P6F.thk(spec.get("front", "8mm")) - tLip)   # liežuvis: storis - 3 (8 mm -> 5; 30 mm -> 27)
    uR = bend + depth - tLip                               # šono galas
    srect(bend + tB, uR, TM, TM + tR)
    srect(uR, bend + depth, TM, V_END, fill=white, lw=0.5)                 # plexi priekis
    srect(uR - tTg, uR, TM + tR, V_END, fill=white, lw=0.5)                # liežuvis šonų viduje
    c.saveState(); c.setStrokeColor(GREY); c.setLineWidth(0.2)
    for vv in range(int(TM + 2), int(V_END), 3):          # plexi žymėjimas (45°)
        if not BREAK or vv > SEG2_A:
            if vv + 2.7 < V_END:
                c.line(du(bend + depth - 0.3), Y(dv(vv)), du(uR + 0.3), Y(dv(vv + 2.7)))
            if vv > TM + tR + 1 and vv + 4.7 < V_END:
                c.line(du(uR - 0.3), Y(dv(vv)), du(uR - tTg + 0.3), Y(dv(vv + 4.7)))
    c.restoreState()
    ub = uR - tTg / 2                                      # varžtas per šoną į liežuvį
    rect(du(ub + 3.2), dv(TM - 1.8), 6.4 * dk, 1.8 * dk, fill=white, lw=0.35)
    rect(du(ub + 1.0), dv(TM), 2.0 * dk, (tR + 5.0) * dk, fill=white, lw=0.35)
    line(du(ub), dv(TM - 3.5), du(ub), dv(TM + tR + 7.5), 0.2, GREY, dash=([4, 1, 1, 1], 0))
else:
    srect(bend + tB, bend + depth - tF, TM, TM + tR)
    srect(bend + depth - tF, bend + depth, TM, V_END, fill=white, lw=0.5)
    c.saveState(); c.setStrokeColor(GREY); c.setLineWidth(0.2)
    for vv in range(int(TM + 4), int(V_END), 6):          # plexi žymėjimas
        if not BREAK or vv > SEG2_A:
            c.line(du(bend + depth - 0.3), Y(dv(vv)), du(bend + depth - tF + 0.3), Y(dv(vv + 2)))
    c.restoreState()
    srect(bend + depth - tF - 14, bend + depth - tF, TM + tR, TM + tR + 3, fill=HexColor("#9E9E9E"), lw=0.35)  # PVC bortelis statmenai plexi
    ub = bend + depth - tF - 7                                                                              # varžtas per šoną į PVC
    rect(du(ub + 3.2), dv(TM - 1.8), 6.4 * dk, 1.8 * dk, fill=white, lw=0.35)
    rect(du(ub + 1.4), dv(TM), 2.8 * dk, (tR + 5.5) * dk, fill=white, lw=0.35)
    line(du(ub), dv(TM - 3.5), du(ub), dv(TM + tR + 8.5), 0.2, GREY, dash=([4, 1, 1, 1], 0))
srect(bend + tB, bend + tB + 7, TM + 20, TM + 34, fill=HexColor("#E8C640"), lw=0.35)                     # LED
srect(bend + tB + 7, bend + tB + 8.5, TM + 23, TM + 31, fill=white, lw=0.3)
fv = TM + 48                                                                                            # raidė -> fonas
rect(du(bend + tB + 3), dv(fv) - 3.5 * dk, 3 * dk, 7 * dk, fill=white, lw=0.4)
rect(du(bend + tB), dv(fv) - 2 * dk, (tB + tP + 8) * dk, 4 * dk, fill=white, lw=0.4)
line(du(bend + tB + 5), dv(fv), du(bend - tP - 10), dv(fv), 0.2, GREY, dash=([4, 1, 1, 1], 0))
# lūžio linijos
zig(du(bend + depth), du(bend - tP), dv(V_END))
if BREAK:
    zig(du(bend), du(bend - tP), dv(SEG1)); zig(du(bend), du(bend - tP), dv(SEG2_A))
    zig(DWX, DWX + 15 * dk, dv(SEG1) + GAP / 2)
# matmenys
hdim(du(bend), du(0), DTOP - 14, f"{bend:.0f}", DTOP, DTOP)
hdim(du(bend + depth), du(bend), dv(V_END) + 16, f"{depth:.0f}", dv(V_END), dv(V_END))
xv = du(bend + depth) - 12   # balionų stulpelio atskaita (matmuo raidė -> fono viršus detalėje nenaudojamas)
hdim(du(LP["leg"]), du(0), dv(tP + LP["leg"]) + 10, f"L{LP['size']}", dv(tP + LP["thk"]), dv(tP + LP["leg"]), 8)
# balionai kairėje
bx_ = xv - 22
items = [(du(bend) + 1, dv(SEG1 * 0.55), 5), (du(LP["leg"] * 0.8), dv(tP + LP["thk"] / 2), 6),
         (du(su), dv(-1.5), 9), (du(LP["thk"] + 1), dv(wv), 7),
         (du(bend + depth - 1.5), dv(TM + 12), 1), (du(bend + depth * 0.5), dv(TM + tR / 2), 2),
         (du(bend + tB / 2), dv(TM + 40), 3), (du(bend + tB + 3.5), dv(TM + 27), 4), (du(bend - tP / 2), dv(fv), 8),
         ] + ([] if F8_D else [(du(bend + depth - tF - 11.5), dv(TM + tR + 1.5), "A"), (du(ub), dv(TM - 1), "B")])
y_top = DTOP - 6
ys_b = [y_top + i * ((dv(V_END) - y_top) / (len(items) - 1)) for i in range(len(items))]
for (x_, y_, n_), yb_ in zip(sorted(items, key=lambda t: t[1]), ys_b):
    leader(x_, y_, bx_, yb_, n_)
view_title((bx_ + DWX + 15 * dk) / 2, dv(V_END) + 36, "DETAIL A - SECTION",
           f"SCALE 1:{DSC}  |  bottom fixing mirrored")

# ============================================================ GALINIS VAIZDAS (bet kokios formos fonas)
s20 = MM / SC2
RVX, RVY = POS["R"][0] + 20, POS["R"][1] + 44
rw, rh = PW * s20, PH * s20


def RP(x, y):            # veidrodinis (iš galo) modelio mm -> lapo pt
    return RVX + (PW - x) * s20, RVY + y * s20


def _ang(dx, dy):        # lapo kryptis -> reportlab kampas
    return math.degrees(math.atan2(-dy, dx))


def achain(P, u, nrm, ts, ext_from, labels, off, mid=None, ticks=()):
    """Lygiagretus (aligned) grandininis matmuo išilgai krypties u nuo taško P.
    ts - žymių atstumai (pt) nuo P; ext_from - objekto taškai išvadinėms; labels - segmentų užrašai (None = be);
    mid = (i0, i1, tekstas) - bendras užrašas per kelis segmentus; ticks - žymių indeksai, žymimi įstrižu brūkšniu."""
    D = [(P[0] + u[0] * t + nrm[0] * off, P[1] + u[1] * t + nrm[1] * off) for t in ts]
    for (ox, oy), (dx_, dy_) in zip(ext_from, D):
        line(ox + nrm[0] * 2, oy + nrm[1] * 2, dx_ + nrm[0] * 3, dy_ + nrm[1] * 3, 0.25, EXT)
    line(D[0][0] - u[0] * 8, D[0][1] - u[1] * 8, D[-1][0] + u[0] * 8, D[-1][1] + u[1] * 8, 0.3)
    fwd, bwd = _ang(u[0], u[1]), _ang(-u[0], -u[1])
    rot = _ang(u[0], u[1])
    if rot > 90:
        rot -= 180
    if rot <= -90:
        rot += 180
    up = (-math.sin(math.radians(rot)), -math.cos(math.radians(rot)))
    if up[0] * nrm[0] + up[1] * nrm[1] < 0:      # tekstas visada į išorę nuo objekto
        pass
    for i in range(len(D) - 1):
        a_, b_ = D[i], D[i + 1]
        seg = math.dist(a_, b_)
        if i in ticks or (i + 1) in ticks:
            pass
        if i not in ticks:
            if seg > 12:
                arrowhead(a_[0], a_[1], bwd); 
            else:
                arrowhead(a_[0], a_[1], fwd)
        if (i + 1) not in ticks:
            if seg > 12:
                arrowhead(b_[0], b_[1], fwd)
            else:
                arrowhead(b_[0], b_[1], bwd)
        if labels and labels[i] is not None:
            if seg > 12:
                mx_, my_ = (a_[0] + b_[0]) / 2, (a_[1] + b_[1]) / 2
                T(mx_ + up[0] * 2.5, my_ + up[1] * 2.5, labels[i], 8, align="c", rot=rot)
            else:
                end = b_ if i == len(D) - 2 else a_
                sgn = 1 if i == len(D) - 2 else -1
                T(end[0] + u[0] * 10 * sgn + up[0] * 2.5, end[1] + u[1] * 10 * sgn + up[1] * 2.5, labels[i], 8,
                  align="l" if sgn > 0 else "r", rot=rot)
    for i in ticks:
        x_, y_ = D[i]
        c.saveState(); c.setLineWidth(0.6)
        c.line(x_ - 1.6, Y(y_ - 1.6), x_ + 1.6, Y(y_ + 1.6)); c.restoreState()
    if mid:
        i0, i1, txt_ = mid
        mx_, my_ = (D[i0][0] + D[i1][0]) / 2, (D[i0][1] + D[i1][1]) / 2
        T(mx_ + up[0] * 2.5, my_ + up[1] * 2.5, txt_, 8, align="c", rot=rot)


poly([RP(x, y) for x, y in PANEL], fill=HexColor("#F2F2F2"), lw=0.7)
_in = PANEL_G.buffer(-0.7 / s20, join_style=2)
if not _in.is_empty:
    poly([RP(x, y) for x, y in list(_in.exterior.coords)[:-1]], stroke=GREY, lw=0.3)
draw_letters(lambda x, y: (lambda q: (q[0], Y(q[1])))(RP(x, y)), stroke=HexColor("#777777"), lw=0.3, dash=(2, 1.2))
REDGE = {}
if JOINTS:
    for j_ in JOINTS:     # dalių sandūra: abiejų dalių užlenkimai
        for dj in (-tP, tP):
            line(*RP(j_ + dj, 0), *RP(j_ + dj, PH), 0.3, GREY)
        line(*RP(j_, 0), *RP(j_, PH), 0.7, black)
    for pos, x0_, x1_, Lmm_ in L_SEGS:
        ya, yb_ = (tP, tP + LP["leg"]) if pos == "top" else (PH - tP - LP["leg"], PH - tP)
        poly([RP(x0_ + LP["offset_mm"], ya), RP(x1_ - LP["offset_mm"], ya), RP(x1_ - LP["offset_mm"], yb_),
              RP(x0_ + LP["offset_mm"], yb_)], fill=HexColor("#B8B8B8"), lw=0.4)
    for pos, x0_, x1_, lay in S_SEGS:
        ye_, sg_ = (0, -1) if pos == "top" else (PH, 1)
        for t in lay["t"]:
            x_, y_ = RP(x0_ + t, ye_)
            line(x_, y_ + sg_ * 4, x_, y_ - sg_ * 5, 0.2, black, dash=([3, 1, 1, 1], 0))
            c.saveState(); c.setFillColor(black); c.circle(x_, Y(y_), 0.9, stroke=0, fill=1); c.restoreState()
    for pos, x0_, x1_, lay in S_SEGS:     # varžtų grandinė - viršuje
        if pos != "top":
            continue
        a_ = RP(x1_, 0); Lp = (x1_ - x0_) * s20
        ts = [0] + [t * s20 for t in lay["t"]] + [Lp]
        pts = [(a_[0] + t, a_[1]) for t in ts]
        fp_ = f"{lay['pitch']:.0f}" if abs(lay["pitch"] - round(lay["pitch"])) < 0.05 else f"{lay['pitch']:.1f}"
        labs = [f"{SCR['edge_mm']:.0f}"] + [None] * (len(ts) - 3) + [f"{SCR['edge_mm']:.0f}"]
        achain(a_, (1, 0), (0, -1), ts, pts, labs, 14, mid=(1, len(ts) - 2, f"{lay['n']} x {fp_} = {lay['span']:.0f}"),
               ticks=tuple(range(2, len(ts) - 2)))
    for pos, x0_, x1_, Lmm_ in L_SEGS:    # L ilgiai + dalių pločiai - apačioje
        if pos != "bottom":
            continue
        a2 = RP(x1_, PH); Lp2 = (x1_ - x0_) * s20
        t0, t1 = LP["offset_mm"] * s20, Lp2 - LP["offset_mm"] * s20
        dl = (tP + LP["leg"]) * s20
        pts = [a2, (a2[0] + t0, a2[1] - dl), (a2[0] + t1, a2[1] - dl), (a2[0] + Lp2, a2[1])]
        achain(a2, (1, 0), (0, 1), [0, t0, t1, Lp2], pts,
               [f"{LP['offset_mm']:.0f}", f"{Lmm_}  (L{LP['size']})", f"{LP['offset_mm']:.0f}"], 13)
        achain(a2, (1, 0), (0, 1), [0, Lp2], [pts[0], pts[-1]], [f"{x1_ - x0_:.0f}"], 27)
    for j_ in JOINTS:   # pastaba už gaminio ribų (viršuje)
        _jl = RP(j_, 0)
        line(_jl[0], _jl[1] - 2, _jl[0], _jl[1] - 28, 0.25, EXT)
        T(_jl[0], _jl[1] - 31, "PANEL JOINT", 8, align="c", auto_red=False)
    # balionai: varžtas (paskutinis dešinėje) ir L
    _pr = PARTS[0]; _ls = [v for v in S_SEGS if v[0] == "top" and v[1] == _pr[0]][0][3]
    sx_, sy_ = RP(_pr[0] + _ls["t"][0], 0)
    lx_, ly_ = RP(_pr[0] + LP["offset_mm"] + 40, tP + LP["leg"] / 2)
    _cl = (spec.get("cable") or {}).get("edge") == "left"      # laidas modelio kairėje = galinio vaizdo dešinėje
    if _cl:
        _pr = PARTS[-1]; _ls = [v for v in S_SEGS if v[0] == "top" and v[1] == _pr[0]][0][3]
        sx_, sy_ = RP(_pr[0] + _ls["t"][-1], 0)
        lx_, ly_ = RP(_pr[1] - LP["offset_mm"] - 40, tP + LP["leg"] / 2)
        bxr = min(RP(0, 0)[0], RP(PW, 0)[0]) - 18
    else:
        bxr = max(RP(0, 0)[0], RP(PW, 0)[0]) + 18
    leader(sx_, sy_, bxr, sy_ - 8, 9)
    leader(lx_, ly_, bxr, sy_ + 10, 6)
for pos, e in ({} if JOINTS else L_EDGES).items():
    a_ = RP(*e["a"]); b_ = RP(*e["b"])
    Lp = math.dist(a_, b_)
    u_ = ((b_[0] - a_[0]) / Lp, (b_[1] - a_[1]) / Lp)
    n_ = (-e["n"][0], e["n"][1])                                   # veidrodinė išorinė normalė (lapo koord.)
    if u_[0] < 0:                                                  # matmenys visada iš kairės į dešinę
        a_, b_, u_ = b_, a_, (-u_[0], -u_[1])
    REDGE[pos] = (a_, u_, n_, Lp, e["len"])
    k_ = s20
    t0, t1 = LP["offset_mm"] * k_, (e["len"] - LP["offset_mm"]) * k_
    i0, i1 = LP["thk"] * 0 + tP * k_, (tP + LP["leg"]) * k_
    pts = [(a_[0] + u_[0] * t - n_[0] * d, a_[1] + u_[1] * t - n_[1] * d) for t, d in ((t0, i0), (t1, i0), (t1, i1), (t0, i1))]
    poly(pts, fill=HexColor("#B8B8B8"), lw=0.4)                     # L profilis
    for t in S_LAY[pos]["t"]:                                       # varžtų ašys
        tp_ = t * k_
        x_, y_ = a_[0] + u_[0] * tp_, a_[1] + u_[1] * tp_
        line(x_ + n_[0] * 4, y_ + n_[1] * 4, x_ - n_[0] * 5, y_ - n_[1] * 5, 0.2, black, dash=([3, 1, 1, 1], 0))
        c.saveState(); c.setFillColor(black); c.circle(x_, Y(y_), 0.9, stroke=0, fill=1); c.restoreState()

if REDGE and not JOINTS:
    pos_s = "top" if "top" in REDGE else list(REDGE)[0]
    a_, u_, n_, Lp, Lmm = REDGE[pos_s]
    lay = S_LAY[pos_s]
    ts = [0] + [t * s20 for t in lay["t"]] + [Lp]
    pts = [(a_[0] + u_[0] * t, a_[1] + u_[1] * t) for t in ts]
    fp_ = f"{lay['pitch']:.0f}" if abs(lay["pitch"] - round(lay["pitch"])) < 0.05 else f"{lay['pitch']:.1f}"
    labs = [f"{SCR['edge_mm']:.0f}"] + [None] * (len(ts) - 3) + [f"{SCR['edge_mm']:.0f}"]
    achain(a_, u_, n_, ts, pts, labs, 14, mid=(1, len(ts) - 2, f"{lay['n']} x {fp_} = {lay['span']:.0f}"),
           ticks=tuple(range(2, len(ts) - 2)))
    pos_l = "bottom" if "bottom" in REDGE else pos_s
    a2, u2, n2, Lp2, Lmm2 = REDGE[pos_l]
    off_l = 13 if pos_l != pos_s else 30
    t0, t1 = LP["offset_mm"] * s20, Lp2 - LP["offset_mm"] * s20
    dl = (tP + LP["leg"]) * s20
    ts = [0, t0, t1, Lp2]
    pts = [a2, (a2[0] + u2[0] * t0 - n2[0] * dl, a2[1] + u2[1] * t0 - n2[1] * dl),
           (a2[0] + u2[0] * t1 - n2[0] * dl, a2[1] + u2[1] * t1 - n2[1] * dl), (a2[0] + u2[0] * Lp2, a2[1] + u2[1] * Lp2)]
    achain(a2, u2, n2, ts, pts, [f"{LP['offset_mm']:.0f}", f"{L_LENS[pos_l]}  (L{LP['size']})", f"{LP['offset_mm']:.0f}"], off_l)
    achain(a2, u2, n2, [0, Lp2], [pts[0], pts[-1]], [f"{Lmm2:.0f}"], off_l + 14)
    # balionai
    a_, u_, n_, Lp, _ = REDGE[pos_s]
    tlast = S_LAY[pos_s]["t"][-1] * s20
    sx_, sy_ = a_[0] + u_[0] * tlast, a_[1] + u_[1] * tlast
    ls_ = (LP["offset_mm"] + 40) * s20
    lx_, ly_ = (a_[0] + u_[0] * (Lp - ls_) - n_[0] * (tP + LP["leg"] / 2) * s20,
                a_[1] + u_[1] * (Lp - ls_) - n_[1] * (tP + LP["leg"] / 2) * s20)
    bxr = max(RP(0, 0)[0], RP(PW, 0)[0]) + (18 if IS_RECT else 34)
    leader(sx_, sy_, bxr, sy_ + (-8 if IS_RECT else 6), 9)
    leader(lx_, ly_, bxr, sy_ + (10 if IS_RECT else 24), 6)
_rv_top = min(RP(x, y)[1] for x, y in PANEL)
_CB = spec.get("cable")
_CE = None if _CB else spec.get("cable_exit")
def _cpoly(pts):   # laidas - VISADA 0,9 pt raudona (VIEW_MODE hairline netaikomas)
    global VIEW_MODE
    _vm = VIEW_MODE; VIEW_MODE = False
    poly(pts, stroke=HexColor("#E2001A"), lw=0.9, close=False)
    VIEW_MODE = _vm


if _CB:   # v28 (Rytis 2026-10-08): laidas išeina TIK po raide (D11), už fono iki užlenktos briaunos, pro Ø11 skylę briaunoje
    _CC = HexColor("#E2001A")
    dx_, dy_ = _CB["d11_mm"]
    ed_, ey_ = _CB.get("edge", "left"), _CB["edge_mm"]
    runx = _CB.get("run_x_mm", 12)
    if ed_ == "left":
        path_m = [(dx_, dy_), (runx, dy_), (runx, ey_), (0, ey_)]
    elif ed_ == "right":
        path_m = [(dx_, dy_), (PW - runx, dy_), (PW - runx, ey_), (PW, ey_)]
    elif ed_ == "top":
        path_m = [(dx_, dy_), (ey_, dy_), (ey_, 0)] if abs(dx_ - ey_) > 1 else [(dx_, dy_), (dx_, 0)]
    else:
        path_m = [(dx_, dy_), (ey_, dy_), (ey_, PH)] if abs(dx_ - ey_) > 1 else [(dx_, dy_), (dx_, PH)]
    pp_ = [RP(*q) for q in path_m]
    _cpoly(pp_)
    px_, py_ = pp_[0]; r_ = 3.2
    c.saveState(); c.setFillColor(white); c.setStrokeColor(black); c.setLineWidth(0.5)
    c.circle(px_, Y(py_), r_, stroke=1, fill=1); c.restoreState()
    line(px_ - r_ - 2, py_, px_ + r_ + 2, py_, 0.2); line(px_, py_ - r_ - 2, px_, py_ + r_ + 2, 0.2)
    T(px_, py_ + r_ + 10, f"D11 ({_CB.get('letter', 'letter')})", 8, align="c")
    hx_, hy_ = pp_[-1]                                   # skylė užlenktoje briaunoje
    c.saveState(); c.setFillColor(white); c.setStrokeColor(black); c.setLineWidth(0.6)
    c.circle(hx_, Y(hy_), 2.2, stroke=1, fill=1); c.restoreState()
    # laidas už gaminio ribų + uodega + prierašas
    _rx = max(RP(0, 0)[0], RP(PW, 0)[0]); _lx = min(RP(0, 0)[0], RP(PW, 0)[0])
    _sd = 1 if hx_ > RVX + rw / 2 else -1
    if ed_ in ("left", "right"):
        _xo = hx_ + _sd * 26                       # už varžtų grandinės galo - laidas nekerta matmenų užrašų
        _yt = _rv_top - 50
        _cpoly([(hx_, hy_), (_xo, hy_), (_xo, _yt), (_xo + _sd * 10, _yt)])
        T(_xo + _sd * 13, _yt + 2.5, _CB.get("label", ""), 8, align="l" if _sd > 0 else "r", color=_CC, auto_red=False)
        T(_xo + _sd * 13, _yt + 13, f"via Ø11 hole in folded edge ({ed_})", 8, align="l" if _sd > 0 else "r")
        # skylės padėtis briaunoje (nuo fono viršaus)
        _vx = hx_ + _sd * 10
        line(hx_ + _sd * 2, RVY, _vx + _sd * 3, RVY, 0.25, EXT); line(hx_ + _sd * 3, hy_, _vx + _sd * 3, hy_, 0.25, EXT)
        line(_vx, RVY - 8, _vx, hy_ + 8, 0.3)
        arrowhead(_vx, RVY, -90); arrowhead(_vx, hy_, 90)
        T(_vx + _sd * 3, hy_ + 9, f"{ey_:.0f}", 8, align="l" if _sd > 0 else "r")
    else:
        _yt = _rv_top - 50
        _cpoly([(hx_, hy_), (hx_, _yt), (hx_ + 10, _yt)])
        T(hx_ + 13, _yt + 2.5, _CB.get("label", ""), 8, color=_CC, auto_red=False)
elif _CE:   # v13 (Rytis 2026-10-08): laido išvestis kliento nurodytoje vietoje - D11 + laidas už gabarito
    px_, py_ = RP(_CE["x_mm"], _CE["y_mm"])
    r_ = 3.2
    c.saveState(); c.setFillColor(white); c.setStrokeColor(black); c.setLineWidth(0.5)
    c.circle(px_, Y(py_), r_, stroke=1, fill=1); c.restoreState()
    line(px_ - r_ - 2, py_, px_ + r_ + 2, py_, 0.2); line(px_, py_ - r_ - 2, px_, py_ + r_ + 2, 0.2)
    _rx = max(RP(0, 0)[0], RP(PW, 0)[0])
    _yu = _rv_top - 50
    _sd = 1 if px_ > RVX + rw / 2 else -1
    _xe = (_rx + 14) if _sd > 0 else (min(RP(0, 0)[0], RP(PW, 0)[0]) - 14)
    _CC = HexColor("#E2001A")                         # v15: laidas raudonas, storesnis (kaip lapas_core.CABLE)
    poly([(px_, py_ - r_), (px_, _yu), (_xe, _yu)], stroke=_CC, lw=0.9, close=False)
    T(px_ - 5 * _sd, py_ + r_ + 10, f"D11 cable exit ({_CE.get('where', '')})", 8, align="r" if _sd > 0 else "l")
    T(_xe + 3 * _sd, _yu + 2.5, _CE.get("label", ""), 8, align="l" if _sd > 0 else "r", color=_CC, auto_red=False)
else:
    T(RVX, _rv_top - 32, f"LED / PSU / cable exits: {spec['power']}", 8)
view_title(RVX + rw / 2, RVY + rh + 50, "REAR VIEW (MIRRORED)", f"SCALE 1:{SC2}  |  letters hidden - dashed")

# ============================================================ 3D VAIZDAS (aksonometrija, plokštuminis šešėliavimas)
from functools import reduce
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient


def flatten(sp, n=10):
    pts, cur = [], None
    for s in sp:
        if s[0] in ("M", "L"):
            cur = s[1]; pts.append(cur)
        else:
            p0, (p1, p2, p3_) = cur, s[1:]
            for i in range(1, n + 1):
                t = i / n
                pts.append(tuple((1 - t) ** 3 * a + 3 * (1 - t) ** 2 * t * b + 3 * (1 - t) * t * t * cc + t ** 3 * dd
                                 for a, b, cc, dd in zip(p0, p1, p2, p3_)))
            cur = p3_
    return pts


solids = []
SOLMETA = {}       # v10: id(solid) -> (kliento spalva, z pradžia; elementas ant kito elemento - virš jo)
for e in elements:
    polys = []
    for sp in e["sub"]:
        f = flatten(sp)
        if len(f) >= 3:
            polys.append(Polygon([(x, PH - y) for x, y in f]).buffer(0))
    if not polys:
        continue
    g = reduce(lambda a, b: a.symmetric_difference(b), polys)  # even-odd taisyklė
    _on = spec.get("element_colors") and any(o is not e and o["bb"][0] < e["bb"][0] and o["bb"][2] > e["bb"][2]
                                             and o["bb"][1] < e["bb"][1] and o["bb"][3] > e["bb"][3] for o in elements)
    for gg in getattr(g, "geoms", [g]):
        if gg.area > 1:
            sg_ = orient(gg, 1.0)
            solids.append(sg_); SOLMETA[id(sg_)] = (e.get("fill"), depth if _on else 0)

TH, PHI = math.radians(spec.get("view_yaw", 32)), math.radians(spec.get("view_pitch", 17))
ct, st_, cp, sp_ = math.cos(TH), math.sin(TH), math.cos(PHI), math.sin(PHI)


def rot(x, y, z):
    x1, z1 = x * ct + z * st_, -x * st_ + z * ct
    return x1, y * cp - z1 * sp_, y * sp_ + z1 * cp


LV = (-0.45, 0.75, 0.55)
ln = math.sqrt(sum(v * v for v in LV)); LV = tuple(v / ln for v in LV)


def shade(col, n, amb=0.52):
    k = amb + (1 - amb) * max(0.0, n[0] * LV[0] + n[1] * LV[1] + n[2] * LV[2])
    return Color(min(1, col.red * k), min(1, col.green * k), min(1, col.blue * k))


WM = 0
ISO_X, ISO_Y, ISO_W, ISO_H = POS["I"][0], POS["I"][1], POS["I"][2], POS["I"][3] - 30
fit_pts = [rot(x, y, z) for x in (-WM, PW + WM) for y in (-WM * 0.8, PH + WM * 0.8) for z in (-bend,)]
fit_pts += [rot(x, y, depth) for x in (0, PW) for y in (0, PH)]
xs_ = [p[0] for p in fit_pts]; ys_ = [p[1] for p in fit_pts]
k3 = min(ISO_W / (max(xs_) - min(xs_)), ISO_H / (max(ys_) - min(ys_)))
offx = ISO_X + (ISO_W - (max(xs_) - min(xs_)) * k3) / 2 - min(xs_) * k3
offy = Y(ISO_Y + ISO_H) + (ISO_H - (max(ys_) - min(ys_)) * k3) / 2 - min(ys_) * k3


def S3(x, y, z):
    r_ = rot(x, y, z); return offx + r_[0] * k3, offy + r_[1] * k3


def fpoly(pts3, fill, stroke=None, lw=0.2, alpha=None):
    c.saveState()
    c.setFillColor(fill); c.setStrokeColor(stroke or fill); c.setLineWidth(HAIR)
    if alpha is not None:
        c.setFillAlpha(alpha)
    p = c.beginPath(); q0 = S3(*pts3[0]); p.moveTo(*q0)
    for q in pts3[1:]:
        p.lineTo(*S3(*q))
    p.close(); c.drawPath(p, stroke=1 if (stroke is not None or alpha is None) else 0, fill=1)
    c.restoreState()


# be sienos ir fono (Rytio etalonas)
from shapely.affinity import translate as _tr
PU_G = _Poly([(x, PH - y) for x, y in PANEL])          # fonas y-aukštyn koordinatėmis


def _mix(col, k):
    return Color(min(1, col.red * k), min(1, col.green * k), min(1, col.blue * k))


# folded fonas: matomi užlenkimai (pagal kiekvieną kontūro kraštinę), tada priekis
PU = list(PU_G.exterior.coords)[:-1]
rets = []
for i_ in range(len(PU)):
    a3, b3 = PU[i_], PU[(i_ + 1) % len(PU)]
    L_ = math.dist(a3, b3)
    if L_ < 1:
        continue
    n3 = ((b3[1] - a3[1]) / L_, -(b3[0] - a3[0]) / L_, 0.0)
    mx_, my_ = (a3[0] + b3[0]) / 2 + n3[0], (a3[1] + b3[1]) / 2 + n3[1]
    if PU_G.contains(_Pt(mx_, my_)):
        n3 = (-n3[0], -n3[1], 0.0)
    if rot(*n3)[2] <= 0:
        continue
    qd = [(a3[0], a3[1], -bend), (b3[0], b3[1], -bend), (b3[0], b3[1], 0), (a3[0], a3[1], 0)]
    rets.append((sum(rot(*v)[2] for v in qd) / 4, qd, n3, (a3, b3)))
for _, qd, n3, _e in sorted(rets, key=lambda t: t[0]):
    fpoly(qd, shade(_mix(bgc, 1.25), n3, 0.62))
c.saveState()
fp = c.beginPath(); q0 = S3(PU[0][0], PU[0][1], 0); fp.moveTo(*q0)
for q in PU[1:]:
    fp.lineTo(*S3(q[0], q[1], 0))
fp.close(); c.clipPath(fp, stroke=0, fill=0)
a_, b_ = S3(0, PH, 0), S3(PW, 0, 0)
c.linearGradient(a_[0], a_[1], b_[0], b_[1], (_mix(bgc, 1.22), _mix(bgc, 0.78)), extend=True)
c.restoreState()
for _, qd, n3, (a3, b3) in rets:  # šviesios briaunos
    p1_, p2_ = S3(a3[0], a3[1], 0), S3(b3[0], b3[1], 0)
    c.saveState(); c.setStrokeColor(_mix(bgc, 1.6)); c.setLineWidth(HAIR); c.line(*p1_, *p2_); c.restoreState()

for j_ in JOINTS:   # v28: dalių sandūra 3D
    p1_, p2_ = S3(j_, 0, 0), S3(j_, PH, 0)
    c.saveState(); c.setStrokeColor(_mix(bgc, 0.45)); c.setLineWidth(HAIR); c.line(*p1_, *p2_); c.restoreState()
    c.saveState(); c.setStrokeColor(_mix(bgc, 1.6)); c.setLineWidth(HAIR); c.line(p1_[0] + 0.6, p1_[1], p2_[0] + 0.6, p2_[1]); c.restoreState()
# raidės: toliausios pirmos, kiekvienai - šonai (tik matomi), tada priekis
def depth_of(poly_):
    cx_, cy_ = poly_.centroid.x, poly_.centroid.y
    return rot(cx_, cy_, depth / 2)[2]


for sol in sorted(solids, key=lambda p_: (SOLMETA.get(id(p_), (None, 0))[1], depth_of(p_))):
    _f, _z0 = SOLMETA.get(id(sol), (None, 0))
    _ec = bool(spec.get("element_colors") and _f)
    _fc = Color(*_f) if _ec else facec
    _rk = ",".join(str(round(v, 1)) for v in _f) if _ec else ""
    _rc = HexColor(ralhex(spec.get("element_return", {}).get(_rk, spec["return_ral"]))) if _ec else retc
    quads = []
    import p6_vaizdas as PV
    _real = not _ec                                          # v59: realus P6 - korpusas -1,5 + stiklas 3 mm
    _gc = (PV.GLASS_WHITE if PV.white_edge(spec.get("front", "3mm+foil")) else _fc)
    _parts = ([(sol.buffer(-PV.BODY_INSET, join_style=2), _z0, _z0 + depth - PV.GLASS_EDGE, _rc),
               (sol, _z0 + depth - PV.GLASS_EDGE, _z0 + depth, _gc)] if _real else [(sol, _z0, _z0 + depth, _rc)])
    for _pg, _za, _zb, _col in _parts:
      for _pp in getattr(_pg, "geoms", [_pg]):
        if _pp.is_empty:
            continue
        for ring in [_pp.exterior] + list(_pp.interiors):
            pts = list(ring.coords)
            for (x0_, y0_), (x1_, y1_) in zip(pts[:-1], pts[1:]):
                dx_, dy_ = x1_ - x0_, y1_ - y0_
                L_ = math.hypot(dx_, dy_)
                if L_ < 1e-6:
                    continue
                n = (dy_ / L_, -dx_ / L_, 0.0)
                if rot(*n)[2] <= 0:
                    continue
                qd = [(x0_, y0_, _za), (x1_, y1_, _za), (x1_, y1_, _zb), (x0_, y0_, _zb)]
                dz = sum(rot(*v)[2] for v in qd) / 4
                quads.append((dz, qd, n, _col))
    for dz, qd, n, _col in sorted(quads, key=lambda t: t[0]):
        col = shade(_col, n, 0.55)
        fpoly(qd, col, col, 0.25)
    c.saveState(); c.setFillColor(_fc); c.setStrokeColor(HexColor("#B9B9B9")); c.setLineWidth(HAIR)
    p = c.beginPath()
    for ring in [sol.exterior] + list(sol.interiors):
        pts = list(ring.coords)
        p.moveTo(*S3(pts[0][0], pts[0][1], _z0 + depth))
        for q in pts[1:]:
            p.lineTo(*S3(q[0], q[1], _z0 + depth))
        p.close()
    c.drawPath(p, stroke=1, fill=1, fillMode=0)
    c.restoreState()

view_title(ISO_X + ISO_W / 2, ISO_Y + ISO_H + 16, "3D VIEW", "ILLUSTRATIVE - NOT TO SCALE")


VIEW_MODE = False
# ============================================================ APATINĖ INFORMACIJOS JUOSTA (per visą lapo plotį)
def header(x, y, w, title):
    rect(x, y, w, 12, fill=HexColor("#EDEDED"), stroke=black, lw=0.7)
    T(x + 4, y + 8.8, title, 8, font="FB", auto_red=False)


BY0 = BAND_Y
BH = IY1 - BY0                                  # v18: vientisas blokas iki rėmelio (kaip lapas_core)
GAPB = 0
# segmentų pločiai - tokie patys kaip bėgelių lapuose
W_P6, W_MD, W_TB = 214, 172, 272
X_P6 = IX0
X_TB = IX1 - W_TB
X_MD = X_TB - W_MD
X_BOM = X_P6 + W_P6
W_BOM = X_MD - X_BOM
import lapas_core as K                          # v18: BOM / MAIN DATA - bendros lapas_core funkcijos (8 pt, eilutė >= 11 pt)
K.c = c

# --- P6 profilio pjūvis (pagal Rytio P6 pavyzdį, perpieštas dokumento CAD stiliumi)
header(X_P6, BY0, W_P6, f"PROFILE P{spec['profile_no']} - TYPICAL SECTION")
rect(X_P6, BY0 + 12, W_P6, BH - 12, lw=0.6)
# Rytio etaloninis pjūvis (assets/p6_profiliai.pdf) - vektorinis įterpimas po c.save(), scripts/p6_ref.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p6_ref as _P6R


def _ld6(x1, y1, x2, y2, n, r=6):
    line(x1, y1, x2, y2, 0.3)
    c.saveState(); c.setFillColor(black); c.circle(x1, Y(y1), 0.9 if r < 5 else 1.1, stroke=0, fill=1); c.restoreState()
    balloon(x2, y2, n, r)


_P6R.draw(c, H, X_P6, BY0 + 12, W_P6, BH - 12, "folded", spec.get("front", "3mm"), depth, leader=_ld6,
          balloon=balloon, T=T, hdim=hdim, hair=0.1)

# --- MAIN DATA
md = [("Quantity", f"{spec.get('qty', 1)} pcs."), ("Overall size", f"{PW:.0f} x {PH:.0f}" + ("" if IS_RECT else f", {SLOPE_DEG:.0f}°")),
      ("Profile", f"P{spec['profile_no']}"), ("Letter depth", f"{depth:.0f}"), ("Bg. edge", f"{bend:.0f}"),
      ("Face", spec["face"]), ("Return", f"RAL {spec['return_ral']}"), ("Background", f"RAL {spec['background_ral']}"),
      ("Environment", spec["environment"]), ("Illumination", spec["led"]),
      ("Perim. letters", f"{PER_L:.2f} m"), ("Perim. line", f"{PER_T:.2f} m" if PER_T else "-"),
      ("Mounting", spec["mounting"])]
md += [tuple(subst(x) for x in r_) for r_ in spec.get("main_data_extra", [])]
# bendras svoris (Rytis patvirtino - visada MAIN DATA); prielaidos - assets/svoris.json
_SV = json.load(open(os.path.join(SKILL, "assets", "svoris.json")))
_rho, _t = _SV["density_kg_dm3"], _SV["thk_mm"]
_lb, _lh, _lt = (float(v) for v in str(LP["size"]).lower().split("x"))
_front8 = P6F.milled(spec.get("front", "3mm"))
_kg = {
    "face": A_FACE * 1e6 * P6F.thk(spec.get("front", "3mm")) * _rho["pmma"],
    "return": PER_L * 1000 * depth * _t["return"] * _rho["al"],
    "back": A_FACE * 1e6 * _t["back"] * _rho["al"],
    "pvc": 0.0 if _front8 else PER_L * 1000 * _SV["pvc_edge_section_mm2"] * _rho["pvc"],
    "panel": (PANEL_G.area + (PANEL_G.length + 2 * PH * len(JOINTS)) * bend) * spec.get("panel_thk_nominal", _t["folded_panel"]) * _rho["al"],
    "L": L_TOTAL * (_lb + _lh - _lt) * _lt * _rho["al"],
}
WEIGHT = sum(_kg.values()) / 1e6
md.append(("Weight (calc.)", (f"≈ {WEIGHT:.0f} kg" if WEIGHT >= 10 else f"≈ {WEIGHT:.1f} kg") + " / pcs, excl. PSU"))
print("  svoris:", ", ".join(f"{k} {v / 1e6:.1f}" for k, v in _kg.items()), f"= {WEIGHT:.1f} kg")
K.main_data(X_MD, BY0, W_MD, BH, [list(r_) for r_ in md], lab_w=58)
VIEW_MODE = False
K.bom_table(X_BOM, BY0, W_BOM, BH, spec["bom"], title="BILL OF MATERIALS  (per 1 pcs.)")

# --- REVISIONS + antraštės lentelė (ISO 7200 principu, apatinis dešinys kampas)
tbh = 116
ty = IY1 - tbh
tw = W_TB
RX0 = X_TB


def cell(x, y, w, h, label, val, size=8.5, font="F"):
    rect(x, y, w, h, lw=0.4)
    if label:
        T(x + 3, y + 7, label, 5.3, color=GREY, auto_red=False)
    T(x + 4, y + h - 5, val, size, font=font, fit=w - 7)


# v13 (Rytis 2026-10-08): antraštė - TOKIA PAT kaip lapas_core.title_block (naujas stilius visuose lapuose)
rows_h = (30, 24, 30, 24, 28)
tbh = sum(rows_h)
ty = IY1 - tbh
revs = spec.get("revisions", [[spec.get("rev", "A"), "First issue", spec["date"], ""]])
rvy = BY0
header(RX0, rvy, tw, "REVISIONS")
rc = [("REV", 24), ("DESCRIPTION", tw - 24 - 58 - 40), ("DATE", 58), ("BY", 40)]
yy = rvy + 12
for i, rowv in enumerate([[n for n, _ in rc]] + revs):
    xx = RX0
    for (n, w), v in zip(rc, rowv):
        rect(xx, yy, w, 10 if i == 0 else 11, fill=HexColor("#F6F6F6") if i == 0 else None, lw=0.35)
        T(xx + 2.5, yy + 7.8 if i == 0 else yy + 8.2, v, 8, font="FB" if i == 0 else "F")
        xx += w
    yy += 10 if i == 0 else 11
while yy + 0.5 < ty:
    hh_ = min(11, ty - yy)
    xx = RX0
    for _, w in rc:
        rect(xx, yy, w, hh_, lw=0.35); xx += w
    yy += hh_
rect(RX0, rvy + 12, tw, ty - rvy - 12, lw=0.6)
y0 = ty
cell(RX0, y0, tw, rows_h[0], "CLIENT", spec["client"], 14, "FB"); y0 += rows_h[0]
cell(RX0, y0, tw, rows_h[1], "TITLE", spec["title"], 9.5); y0 += rows_h[1]
_on = spec.get("order_no") or "ALT0000_00.00_RS"
cell(RX0, y0, tw * 0.4, rows_h[2], "ORDER NO.", _on, 14, "FB")
cell(RX0 + tw * 0.4, y0, tw * 0.6, rows_h[2], "FILE / DRAWING NO.", spec.get("drawing_no", spec["file_code"]), 12)
y0 += rows_h[2]
fr_ = (0.27, 0.16, 0.16, 0.16, 0.25)
xx_ = RX0
for f_, (lab, val) in zip(fr_, (("SCALE (DIM. mm)", f"1:{SC1} / 1:{SC2}"), ("FORMAT", "A3"), ("SHEET", spec.get("sheet", "1 / 1")),
                                ("REV.", spec.get("rev", "A")), ("PROJECTION", ""))):
    cell(xx_, y0, tw * f_, rows_h[3], lab, val, 9.5)
    xx_ += tw * f_
px_, py_ = RX0 + tw * (1 - fr_[-1] / 2), y0 + 15
poly([(px_ - 13, py_ - 3), (px_ - 4, py_ - 5.5), (px_ - 4, py_ + 5.5), (px_ - 13, py_ + 3)], lw=0.5)
c.saveState(); c.setLineWidth(0.5)
c.circle(px_ + 6, Y(py_), 5.5); c.circle(px_ + 6, Y(py_), 3); c.restoreState()
line(px_ - 15, py_, px_ + 13, py_, 0.2, black, dash=([4, 1, 1, 1], 0))
y0 += rows_h[3]
cell(RX0, y0, tw * 0.22, rows_h[4], "DRAWN", spec.get("drawn", ""), 9.5)
cell(RX0 + tw * 0.22, y0, tw * 0.22, rows_h[4], "CHECKED", spec.get("checked", ""), 9.5)
cell(RX0 + tw * 0.44, y0, tw * 0.22, rows_h[4], "DATE", spec["date"], 9.5)
cell(RX0 + tw * 0.66, y0, tw * 0.34, rows_h[4], "", "", 9.5)
rect(RX0, ty, tw, tbh, lw=1.0)
line(IX0, BY0 - 6, IX1, BY0 - 6, 0.7)   # juostos skirtukas

c.save()
doc = fitz.open(tmp_pdf)
doc.save(OUT, garbage=3, deflate=True)
doc.close()
import lapas_core as _K
_K.pdf_fix_fonts(OUT)                              # v20: tekstas CorelDRAW lieka tekstu (GOST Common)
print("OK", OUT, f"scales 1:{SC1}/1:{SC2}, perimeter letters {PER_L:.2f} m, thin {PER_T:.2f} m; rows",
      [(round(r['x1'] - r['x0']), round(r['h'])) for r in rows], "marks", marks)
