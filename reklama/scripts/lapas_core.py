#!/usr/bin/env python3
"""Etaloninio techninio lapo stiliaus biblioteka (references/stilius.md).

Visi produktų moduliai (folded plokštė, bėgeliai, plokštė ant distancerių, ...) naudoja šias funkcijas,
kad lapas visada atrodytų vienodai: rėmelis, šriftas, hairline kontūrai, matmenys, balionai, lentelės,
antraštė, 3D. Naudojimas:
    import lapas_core as K
    K.init(out_pdf_tmp, title)
    ... K.T(...), K.rect(...), K.set_view(True) ...
    K.save(out_pdf)
"""
import math
import os
from functools import reduce

import pymupdf as fitz
from reportlab.lib.colors import Color, HexColor, black, white
from reportlab.lib.pagesizes import A3, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from shapely.geometry import Point, Polygon
from shapely.geometry.polygon import orient

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ISO = os.path.join(SKILL, "assets", "osifont.ttf")
_FD = "/usr/share/fonts/truetype/dejavu/"
_GOST = os.path.join(SKILL, "assets", "gost_common.ttf")   # GOST Common (Rytio šriftas, Rytis patvirtino 2026-10-07)
if os.path.exists(_GOST):
    pdfmetrics.registerFont(TTFont("F", _GOST)); pdfmetrics.registerFont(TTFont("FB", _GOST))
elif os.path.exists(_ISO):
    pdfmetrics.registerFont(TTFont("F", _ISO)); pdfmetrics.registerFont(TTFont("FB", _ISO))
else:
    pdfmetrics.registerFont(TTFont("F", _FD + "DejaVuSansCondensed.ttf"))
    pdfmetrics.registerFont(TTFont("FB", _FD + "DejaVuSansCondensed-Bold.ttf"))

# GOST Common: kai kurių simbolių kodai šrifte sumaišyti (Ø -> Ý, ° -> ¹, ± -> ¼) - pakeičiami tinkamais glifais
_GFIX = str.maketrans({"Ø": "⌀", "ø": "⌀", "°": "˚", "±": "+/-"}) if os.path.exists(_GOST) else {}
RAL = {"6039": "#8FB03E", "8001": "#9D622B", "4010": "#BC4077", "2008": "#F75E25", "1011": "#8A6642", "3009": "#642424", "5003": "#1D334A", "5022": "#222D5A", "5012": "#3B83BD", "5002": "#1E2460", "5015": "#2271B3", "3000": "#A72920", "6005": "#114232", "7021": "#23282B", "7024": "#474A51", "9003": "#F4F4F4", "9001": "#FDF4E3", "1003": "#F9A800", "2004": "#F44611", "3005": "#5E2129", "6029": "#20603D", "8017": "#45322E", "1019": "#A08F7A", "1023": "#F7B500", "3020": "#C1121C", "5005": "#154889", "5010": "#0E4C8C",
       "5013": "#25314B", "6018": "#57A639", "6024": "#308446", "7016": "#383E42", "7035": "#CBD0CC",
       "9005": "#0E0E10", "7044": "#CAC4B0", "9006": "#A5A8A6", "9010": "#F1EDE1", "9016": "#F1F0EA", "8014": "#4A3526", "8011": "#5A3826"}
GREY = HexColor("#6E6E6E")
EXT = HexColor("#7A7A7A")
SECTION_C = HexColor("#111111")
VINYL = {"3630-33": "#C8102E", "3630-125": "#FFC20E"}
PMS = {"297": "#71C5E8", "185": "#E4002B"}          # Pantone C - BOM FINISH langelio užpildui; naują kodą įrašyti čia
# v17 (Rytis 2026-10-08): VISI plėvelių kodai BOM lentelėje - spalvotas langelis (FINISH ir MATERIAL stulpeliai)
FOIL = {"8500 614": "#00A859", "8500-614": "#00A859", "8500 034": "#EB690F", "8500-034": "#EB690F", "551 010": "#FFFFFF", "551-010": "#FFFFFF",
        "551-035": "#F75E25", "551 035": "#F75E25", "777-002": "#E4002B", "SANDBLAST": "#C4C5C9",
        "DAY/NIGHT": "#1C1C1C"}     # v57: Day/Night perforuota plėvelė, juoda spauda (SPAR 226004)


_FILMS = None


def films():
    """v142: plėvelių biblioteka assets/pleveles.json (ORACAL 8500 / 551, Avery 4500 / 5500 / 777, 3M 3630)"""
    global _FILMS
    if _FILMS is None:
        import json
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "pleveles.json")
        try:
            _FILMS = json.load(open(p, encoding="utf-8"))
        except Exception:
            _FILMS = {}
    return _FILMS


def film_lookup(v):
    """'ORACAL 8500 034' / '8500-034' / 'ORACAL 551 702' / '3M 3630-33' / 'Avery 4506' / 'Avery 5510-01' / 'Avery 777-002CF'
    -> (serija, kodas, {name, hex, approx, ...}) arba None"""
    import re
    u = str(v).upper().replace("ORALITE", "ORACAL")
    F = films()
    m = re.search(r"\b(8500|551)[\s\-]+(\d{3})", u)
    if m:
        s = "ORACAL " + m.group(1); e = F.get(s, {}).get("colors", {}).get(m.group(2))
        return (s, m.group(2), e) if e else None
    m = re.search(r"\b3630[\s\-]+(\d{1,3})\b", u)
    if m:
        k = "3630-" + m.group(1); e = F.get("3M 3630", {}).get("colors", {}).get(k)
        return ("3M 3630", k, e) if e else None
    m = re.search(r"\b777[\s\-]+(\d{3})", u)
    if m:
        k = "777-" + m.group(1); e = F.get("AVERY 777", {}).get("colors", {}).get(k)
        return ("AVERY 777", k, e) if e else None
    for s_ in ("AVERY 4500", "AVERY 5500"):
        for k, e in F.get(s_, {}).get("colors", {}).items():
            if re.search(r"(?<![\d])" + re.escape(k) + r"(?![\d])", u.replace(" TF", "").replace(" QM", "")):
                if k in ("4500", "5500") and not re.search(k + r"[\s\-]*(WHITE|BALT|$)", u):
                    continue                          # '4500 TF 4506' - serijos pavadinimas, ne baltas
                return s_, k, e
    return None


def code_hex(v, ral=True):
    """langelio spalva pagal kodą: RAL / 3M / PMS / ORACAL / Avery / sandblast; None - nežinoma"""
    v0 = str(v).split("\n")[0].strip()
    u = v0.upper()
    if ral and u.startswith("RAL") and len(v0.split()) > 1:
        return ralhex(v0.split()[1].rstrip(","))
    f_ = film_lookup(v0)
    if f_:
        return f_[2]["hex"]
    if u.startswith("3M") and len(v0.split()) > 1:
        return VINYL.get(v0.split()[1])
    if u.startswith("PMS") and len(v0.split()) > 1:
        return PMS.get(v0.split()[1].rstrip("C").strip())
    for k_, h_ in FOIL.items():
        if k_ in u:
            return h_
    return None
MM = 72 / 25.4
HAIR = 0.1
W, H = landscape(A3)
c = None
VIEW_MODE = False
_tmp = None


# ------------------------------------------------------------------ bazė
# Šrifto dydžiai (Rytis 2026-10-07): pagrindiniai matmenys 12 pt, rėmo matmenys >= 8 pt, apatinės juostos
# informaciniai blokai >= 8 pt, vaizdų pavadinimai / mastelis - proporcingai
F_DIM_MAIN, F_DIM_FRAME, F_INFO, F_VIEW, F_SCALE = 12, 8, 8, 13, 9


def init(tmp_pdf, title=""):
    global c, _tmp
    _tmp = tmp_pdf
    TEXT_BOXES.clear(); EXT_REG.clear()
    c = canvas.Canvas(tmp_pdf, pagesize=(W, H))
    c.setTitle(title)
    return c


_PLACE = []
ART = []          # v182: įdėtos kliento grafikos sritys (pymupdf koord. + psl.) -> <lapas>.pdf.art.json, patikra_lapas jas praleidžia


def place_pdf(src_pdf, pno, clip, tl, tr, bl, outline=0.3, under=False):
    """v151 (Rytis 2026-10-13, Thales: "labai daug neatitikimų" perpiešiant kliento grafiką kontūrais): TIKSLUS kito PDF
    fragmento įdėjimas - vektorius + gyvas tekstas + paveikslėliai + gradientai, kaip kliento faile. clip - šaltinio puslapio
    sritis (pymupdf koord.), tl / tr / bl - tikslo lygiagretainio kampai (reportlab koord.; 2D - stačiakampis, 3D - afininis).
    Įdedama save() metu VIRŠ lapo turinio."""
    # v171: under=True - fragmentas PO lapo turiniu (ant jo rašomi GOST užrašai reportlab šriftu, ne papildomi Type0 šriftai)
    _PLACE.append((c.getPageNumber() - 1, src_pdf, pno, tuple(clip), tuple(tl), tuple(tr), tuple(bl), outline, under))


def _apply_place(doc):
    srcs = {}
    for it_ in _PLACE:
        pi, src, pno, clip, tl, tr, bl, ol = it_[:8]
        und = it_[8] if len(it_) > 8 else False
        srcs.setdefault(src, fitz.open(src))
        pg = doc[pi]; Hp = pg.rect.height
        old = {x[0] for x in pg.get_xobjects()}
        pg.show_pdf_page(fitz.Rect(0, 0, 100, 100), srcs[src], pno, clip=fitz.Rect(clip), keep_proportion=False,
                         overlay=not und)
        xr = next(x[0] for x in pg.get_xobjects() if x[0] not in old)
        m0 = [float(v) for v in doc.xref_get_key(xr, "Matrix")[1].strip("[]").split()]
        # rect (0,0,100,100) pymupdf = PDF x 0..100, y Hp-100..Hp -> lygiagretainis
        a_, b_ = (tr[0] - tl[0]) / 100, (tr[1] - tl[1]) / 100
        c_, d_ = (tl[0] - bl[0]) / 100, (tl[1] - bl[1]) / 100
        e_, f_ = tl[0] - Hp * c_, tl[1] - Hp * d_
        a0, b0, c0, d0, e0, f0 = m0
        mn = (a0 * a_ + b0 * c_, a0 * b_ + b0 * d_, c0 * a_ + d0 * c_, c0 * b_ + d0 * d_,
              e0 * a_ + f0 * c_ + e_, e0 * b_ + f0 * d_ + f_)
        doc.xref_set_key(xr, "Matrix", "[" + " ".join(f"{v:.6f}" for v in mn) + "]")
        br = (tr[0] + bl[0] - tl[0], tr[1] + bl[1] - tl[1])
        xs_ = [q[0] for q in (tl, tr, br, bl)]; ys_ = [Hp - q[1] for q in (tl, tr, br, bl)]
        ART.append([min(xs_), min(ys_), max(xs_), max(ys_), pi])
        if ol:                                                       # kontūras virš įdėtos grafikos (lapo detalės kraštas)
            pg.draw_polyline([fitz.Point(q[0], Hp - q[1]) for q in (tl, tr, br, bl)], color=(0, 0, 0), width=ol, closePath=True)
    _PLACE.clear()


def save(out_pdf):
    c.save()
    doc = fitz.open(_tmp)
    if _PLACE:
        _apply_place(doc)
    doc.save(out_pdf, garbage=3, deflate=True)
    doc.close()
    pdf_fix_fonts(out_pdf)                        # v20: CorelDRAW atpažįsta GOST Common - tekstas lieka tekstu
    art_json(out_pdf)


def art_json(out_pdf, pages_offset=0):
    """v182: kliento grafikos sritys šalia lapo (`<lapas>.pdf.art.json`) - patikra_lapas.py jų netikrina (kliento grafika
    neliečiama, v162); sąrašas išvalomas."""
    import json
    if ART:
        with open(out_pdf + ".art.json", "w") as fh:
            json.dump({"art": [a[:4] + [a[4] + pages_offset] for a in ART]}, fh)
    elif os.path.exists(out_pdf + ".art.json"):
        os.remove(out_pdf + ".art.json")
    ART.clear()


def set_view(on):
    global VIEW_MODE
    VIEW_MODE = on


def ralhex(code):
    return RAL.get(str(code).replace("RAL", "").strip().split()[0] if str(code).strip() else "", "#888888")


def unk(s):
    s = str(s)
    return "PATIKSLINTI" in s or s.strip() == "?" or s.strip().endswith("?")


def Y(y):
    return H - y


def mix(col, k):
    return Color(min(1, col.red * k), min(1, col.green * k), min(1, col.blue * k))


def _lw(w):
    return HAIR if VIEW_MODE and w > HAIR else w      # v63: projekcijose VISOS linijos hairline


# ------------------------------------------------------------------ tekstas ir primityvai
OVERFLOW = []


def T(x, y, s, size=7.5, font="F", color=black, align="l", rot=0, auto_red=True, fit=None, fit_min=None):
    """Tekstas. Nežinoma reikšmė (?) - tuščia vieta; jei baigiasi ':' - rašymo linija."""
    s = str(s)
    if any(ch in s for ch in "ÅåÆæøÄäÖö") and os.path.exists(_ISO) and font in ("F", "FB"):
        # v11: GOST Common neturi Å/Æ/Ø (norvegų pavadinimai) - visa eilutė osifont šriftu
        # v146: Ä / Ö (švedų, pvz. OKQ8 „Biltvätt", „FRI HÖJD") GOST faile sumaišyti glifai - taip pat osifont
        if "FI" not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont("FI", _ISO))
        font = "FI"
    else:
        s = s.translate(_GFIX)
    if fit and s and pdfmetrics.stringWidth(s, font, size) > fit:      # netelpa langelyje - mažinti šriftą
        size = max(size * 0.72, size * fit / pdfmetrics.stringWidth(s, font, size), fit_min or 0)
        if pdfmetrics.stringWidth(s, font, size) > fit + 0.5:          # v18: netelpa ir su min. šriftu - trumpinti tekstą
            OVERFLOW.append(s); print(f"  ! NETELPA ({size:.1f} pt): {s}")
    blank_line = False
    if auto_red and unk(s):
        s = s.replace("PATIKSLINTI", "").replace("?", "").rstrip(" ,;-")
        blank_line = s.endswith(":")
    c.saveState()
    c.setFillColor(color); c.setStrokeColor(color)
    c.translate(x, Y(y)); c.rotate(rot)
    w_ = pdfmetrics.stringWidth(s, font, size)
    x0_ = {"l": 0, "c": -w_ / 2, "r": -w_}[align]
    if s.strip():                                       # v172: visų lapo tekstų plotai - matmenų užrašai jų nedengia
        if rot % 180 == 0:
            TEXT_BOXES.append((c.getPageNumber(), x + x0_, y - size * 0.75, x + x0_ + w_, y + size * 0.1))
        else:
            TEXT_BOXES.append((c.getPageNumber(), x - size * 0.75, y - x0_ - w_, x + size * 0.1, y - x0_))
    t_ = c.beginText(x0_, 0); t_.setFont(font, size)
    if font == "FB":
        t_.setTextRenderMode(2); c.setLineWidth(size * 0.045)
    t_.textOut(s); c.drawText(t_)
    if blank_line:
        c.setLineWidth(0.3); c.setStrokeColor(black); c.line(x0_ + w_ + 3, -1, x0_ + w_ + 90, -1)
    c.restoreState()


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


def poly(pts, fill=None, stroke=black, lw=0.5, close=True, dash=None):
    c.saveState()
    if fill is not None:
        c.setFillColor(fill)
    if stroke is not None:
        c.setStrokeColor(stroke); c.setLineWidth(_lw(lw))
    if dash:
        c.setDash(*dash)
    p = c.beginPath(); p.moveTo(pts[0][0], Y(pts[0][1]))
    for q in pts[1:]:
        p.lineTo(q[0], Y(q[1]))
    if close:
        p.close()
    c.drawPath(p, stroke=stroke is not None, fill=fill is not None)
    c.restoreState()


def circle(x, y, r, fill=None, stroke=black, lw=0.5, dash=None):
    c.saveState()
    if fill is not None:
        c.setFillColor(fill)
    if stroke is not None:
        c.setStrokeColor(stroke); c.setLineWidth(_lw(lw))
    if dash:
        c.setDash(*dash)
    c.circle(x, Y(y), r, stroke=stroke is not None, fill=fill is not None)
    c.restoreState()


def arrowhead(x, y, ang):
    c.saveState(); c.setFillColor(black); c.translate(x, Y(y)); c.rotate(ang)
    p = c.beginPath(); p.moveTo(0, 0); p.lineTo(-5.5, 1.3); p.lineTo(-5.5, -1.3); p.close()
    c.drawPath(p, stroke=0, fill=1); c.restoreState()


EXT_REG = {}                                             # v182: nubrėžtos išvadinės (psl., ašis, koord.) -> [(a, b)]


def ext_line(x1, y1, x2, y2):
    """v182 (patikra_lapas „MATMENYS VIENAS ANT KITO"): išvadinė linija - jei toje pačioje tiesėje jau yra išvadinė
    (grandinės ir gabarito matmenys iš to paties taško), brėžiama TIK trūkstama dalis, linijos viena ant kitos nekartojamos."""
    pg = c.getPageNumber()
    if abs(x1 - x2) < 0.05:
        key, a, b = (pg, "v", round(x1, 1)), min(y1, y2), max(y1, y2)
    elif abs(y1 - y2) < 0.05:
        key, a, b = (pg, "h", round(y1, 1)), min(x1, x2), max(x1, x2)
    else:
        line(x1, y1, x2, y2, 0.25, EXT); return
    segs = [(a, b)]
    for (p, q) in EXT_REG.get(key, []):
        nxt = []
        for (s0, s1) in segs:
            if q <= s0 or p >= s1:
                nxt.append((s0, s1)); continue
            if s0 < p:
                nxt.append((s0, p))
            if q < s1:
                nxt.append((q, s1))
        segs = nxt
    for (s0, s1) in segs:
        if s1 - s0 > 0.3:
            if key[1] == "v":
                line(x1, s0, x1, s1, 0.25, EXT)
            else:
                line(s0, y1, s1, y1, 0.25, EXT)
    EXT_REG.setdefault(key, []).append((a, b))


def hdim(x1, x2, y, label, e1=None, e2=None, size=8, small_side="r", avoid=None):
    for x, e in ((x1, e1), (x2, e2)):
        if e is not None:
            sgn = 1 if e > y else -1
            ext_line(x, e - 2 * sgn, x, y - 3 * sgn)
    line(x1, y, x2, y, 0.3)
    if x2 - x1 > max(16, pdfmetrics.stringWidth(str(label), "F", size) + 4):
        arrowhead(x1, y, 180); arrowhead(x2, y, 0)
        cx_ = _dodge((x1 + x2) / 2, x1, x2, label, size, avoid)
        w_ = pdfmetrics.stringWidth(str(label), "F", size)
        if avoid and any(cx_ - w_ / 2 - 3 <= ax <= cx_ + w_ / 2 + 3 for ax in avoid):
            # v172: matmens ribose vietos be kirtimų nėra - tekstas UŽ matmens galo (linija pratęsiama), ne ant išvadinių
            for side in (("l", "r") if small_side == "l" else ("r", "l")):
                for d_ in range(10, 160, 2):                 # artimiausia laisva vieta už galo
                    if side == "l" and not any(x1 - d_ - w_ - 3 <= ax <= x1 - d_ + 3 for ax in avoid):
                        line(x1 - d_ - w_ - 2, y, x1, y, 0.3); T(x1 - d_, y - 2.5, label, size, align="r"); return
                    if side == "r" and not any(x2 + d_ - 3 <= ax <= x2 + d_ + w_ + 3 for ax in avoid):
                        line(x2, y, x2 + d_ + w_ + 2, y, 0.3); T(x2 + d_, y - 2.5, label, size, align="l"); return
        T(cx_, y - 2.5, label, size, align="c")
    else:
        arrowhead(x1, y, 0); arrowhead(x2, y, 180)
        line(x1 - 8, y, x1, y, 0.3); line(x2, y, x2 + 8, y, 0.3)
        w_ = pdfmetrics.stringWidth(str(label), "F", size)
        fl = text_free(x1 - 10 - w_, y - size * 0.4, x1 - 10, y + size * 0.45)
        fr = text_free(x2 + 10, y - size * 0.4, x2 + 10 + w_, y + size * 0.45)
        if (small_side == "l" and (fl or not fr)) or (small_side != "l" and fl and not fr):   # v172: į laisvą pusę
            T(x1 - 10, y + size * 0.35, label, size, align="r")
        else:
            T(x2 + 10, y + size * 0.35, label, size)


def _bg(x, y, s, size, align="c", rot=0):
    """baltas fonas po tekstu (skaitomumas ant spalvotų raidžių)"""
    w_ = pdfmetrics.stringWidth(str(s), "F", size)
    x0 = {"l": 0, "c": -w_ / 2, "r": -w_}[align]
    c.saveState(); c.translate(x, Y(y)); c.rotate(rot); c.setFillColor(white)
    c.rect(x0 - 1.2, -1.6, w_ + 2.4, size * 0.9, stroke=0, fill=1); c.restoreState()


def _dodge(cx, a, b, lab, size, avoid):
    """Rytis 2026-10-07 / v172: matmens tekstas nekertamas JOKIOS išvadinės / žymos / laido linijos - ieškoma artimiausia
    centrui vieta matmens ribose, kur nė viena `avoid` x nepatenka į teksto plotą (+3 pt); nėra - mažiausiai kirtimų."""
    if not avoid:
        return cx
    w_ = pdfmetrics.stringWidth(str(lab), "F", size)
    lo, hi = a + w_ / 2 + 3, b - w_ / 2 - 3
    best = None
    k = 0.0
    while k <= max(hi - lo, 0) + 1:
        for c_ in ((cx + k, cx - k) if k else (cx,)):
            if lo <= c_ <= hi or (hi < lo and abs(c_ - (a + b) / 2) < 1):
                hits = sum(1 for ax in avoid if c_ - w_ / 2 - 3 <= ax <= c_ + w_ / 2 + 3)
                if best is None or hits < best[0]:
                    best = (hits, c_)
                if hits == 0:
                    return c_
        k += 1.0
    return best[1] if best else cx


def _Tbg(x_, y_, s_, size_, align="l", rot=0, **kw):
    _bg(x_, y_, s_, size_, align, rot)
    T(x_, y_, s_, size_, align=align, rot=rot, **kw)


def hchain(y, xs, ext_from_y, labels, size=8, bg=False, avoid=None):
    """horizontali grandinė; xs - x (pt), ext_from_y - y, iš kurio kyla kiekviena išvadinė.
    Rytis 2026-10-07 / v152 (2026-10-13 "lipama vienas ant kito, suspaudžiama"): matmenų tekstai NESIDENGIA ir neužlipa ant
    rodyklių / kitų tarpų: mažo tarpo užrašas - tik kraštinio tarpo IŠORĖJE (už grandinės galo), vidurinių - eilėje TOLIAU
    nuo objekto, virš savo tarpo, su trumpa išvadine; eilės stumiamos, kol laisva."""
    TX = _Tbg if bg else T
    for x, ey in zip(xs, ext_from_y):
        sgn = 1 if ey > y else -1
        ext_line(x, ey - 2 * sgn, x, y - 3 * sgn)
    line(xs[0], y, xs[-1], y, 0.3)
    away = -1 if sum(ey - y for ey in ext_from_y) >= 0 else 1      # kryptis nuo objekto (puslapio y)
    placed = []                                            # (x0, x1, y) užimti tekstų plotai

    def free(x0, x1, yy):
        return all(x1 + 3 <= a or x0 - 3 >= b or abs(yy - c_) >= size + 1 for a, b, c_ in placed) and \
            text_free(x0, yy - size * 0.75, x1, yy + size * 0.1)
    smalls, n = [], len(labels)
    for i, (a, b, lab) in enumerate(zip(xs[:-1], xs[1:], labels)):
        if str(lab) == "":
            arrowhead(a, y, 180); arrowhead(b, y, 0)
            continue
        w_ = pdfmetrics.stringWidth(str(lab), "F", size)
        if b - a > max(16, w_ + 10):
            arrowhead(a, y, 180); arrowhead(b, y, 0)
            cx = _dodge((a + b) / 2, a, b, lab, size, avoid)
            TX(cx, y - 2.5, lab, size, align="c"); placed.append((cx - w_ / 2, cx + w_ / 2, y - 2.5))
        else:
            arrowhead(a, y, 0); arrowhead(b, y, 180)
            smalls.append((i, a, b, lab, w_))
    for i, a, b, lab, w_ in smalls:
        yl = y - 2.5
        opts = []
        if i == 0:
            opts.append(("l", a - 10 - w_, a - 10, a - 8, a))
        if i == n - 1:
            opts.append(("r", b + 10, b + 10 + w_, b, b + 8))
        done = False
        for side, x0, x1, l0, l1 in opts:
            if free(x0, x1, yl):
                line(l0, y, l1, y, 0.3)
                TX(x0 if side == "r" else x1, yl, lab, size, align="l" if side == "r" else "r")
                placed.append((x0, x1, yl)); done = True; break
        if not done:                                        # eile toliau nuo objekto, virš tarpo, su išvadine
            k = 1
            cx = (a + b) / 2
            while True:
                yy = y - 2.5 + away * k * (size + 2)
                if free(cx - w_ / 2, cx + w_ / 2, yy):
                    break
                k += 1
            yt = yy - size * 0.75 if away < 0 else yy - size * 0.75
            line(cx, y, cx, yy + (2 if away < 0 else -size * 0.8), 0.2, EXT)
            TX(cx, yy, lab, size, align="c"); placed.append((cx - w_ / 2, cx + w_ / 2, yy))


def vchain(x, ys, ext_to, labels, size=8, bg=False, small=None):
    """vertikali grandinė; ext_to - x, iki kurio eina išvadinė (abi pusės palaikomos).
    v152: mažo tarpo užrašas - kraštinio tarpo IŠORĖJE (virš / po grandinės galu, pasuktas kaip kiti), vidurinių -
    šone TOLIAU nuo objekto (horizontalus tekstas su išvadine), vienas kito neliečia."""
    TX = _Tbg if bg else T
    for y, ex in zip(ys, ext_to):
        sgn = 1 if ex > x else -1
        ext_line(x - 3 * sgn, y, ex - 2 * sgn, y)
    line(x, ys[0], x, ys[-1], 0.3)
    out = -1 if all(ex > x for ex in ext_to) else 1          # maži užrašai - į pusę nuo išvadinių
    n = len(labels); top, bot = min(ys), max(ys)
    placed = []                                              # (y0, y1, x0, x1)

    def free(y0, y1, x0, x1):
        return all(y1 + 2 <= a or y0 - 2 >= b or x1 + 2 <= c_ or x0 - 2 >= d for a, b, c_, d in placed) and \
            text_free(x0, y0, x1, y1)
    for i, (a, b, lab) in enumerate(zip(ys[:-1], ys[1:], labels)):
        w_ = pdfmetrics.stringWidth(str(lab), "F", size)
        lo, hi = min(a, b), max(a, b)
        if hi - lo > max(14, w_ + 6):
            arrowhead(x, a, 90 if a < b else -90); arrowhead(x, b, -90 if a < b else 90)
            TX(x - 2.5, (a + b) / 2, lab, size, align="c", rot=90)
            placed.append(((a + b) / 2 - w_ / 2, (a + b) / 2 + w_ / 2, x - size, x))
            continue
        arrowhead(x, a, -90 if a < b else 90); arrowhead(x, b, 90 if a < b else -90)
        # v172 (Rytis: „matmenų linijos sugrūdamos"): kraštinis mažas tarpas - VIRŠ / PO grandinės galu (ne šone, kur
        #  jį kerta išorinio matmens išvadinė); vidurinis - šone, toliau nuo objekto
        end = "top" if i == 0 else ("bot" if i == n - 1 else "side")
        if small == "side":                                  # v182: lapo krašte (virš / po galu nėra vietos) - šone
            end = "side"
        if end == "top" and not free(top - 10 - w_, top - 8, x - size, x) and i == n - 1:
            end = "bot"                                      # viršuje užimta (kiti matmenys) - po apačios galu
        if end == "top" and free(top - 10 - w_, top - 8, x - size, x):
            line(x, top - 8, x, top, 0.3)
            TX(x - 2.5, top - 10 - w_ / 2, lab, size, align="c", rot=90); placed.append((top - 10 - w_, top - 8, x - size, x)); continue
        if end == "bot" and free(bot + 8, bot + 10 + w_, x - size, x):
            line(x, bot, x, bot + 8, 0.3)
            TX(x - 2.5, bot + 10 + w_ / 2, lab, size, align="c", rot=90); placed.append((bot + 8, bot + 10 + w_, x - size, x)); continue
        yy = (a + b) / 2 + size * 0.35
        off = 4
        while True:
            x0, x1 = (x + off, x + off + w_) if out > 0 else (x - off - w_, x - off)
            if free(yy - size * 0.8, yy + 1, x0, x1):
                break
            off += w_ + 4
        line(x, (a + b) / 2, (x0 - 1) if out > 0 else (x1 + 1), (a + b) / 2, 0.2, EXT)
        TX(x0 if out > 0 else x1, yy, lab, size, align="l" if out > 0 else "r")
        placed.append((yy - size * 0.8, yy + 1, x0, x1))


def _ang(dx, dy):
    return math.degrees(math.atan2(-dy, dx))


def balloon(x, y, n, r=6.5):
    c.saveState(); c.setFillColor(white); c.setStrokeColor(black); c.setLineWidth(0.5)
    c.circle(x, Y(y), r, stroke=1, fill=1); c.restoreState()
    T(x, y + F_INFO * 0.36, n, F_INFO, font="FB", align="c")


def leader(x1, y1, x2, y2, n, r=6.5):
    line(x1, y1, x2, y2, 0.3)
    c.saveState(); c.setFillColor(black); c.circle(x1, Y(y1), 0.9 if r < 5 else 1.1, stroke=0, fill=1); c.restoreState()
    balloon(x2, y2, n, r)


def tag(x1, y1, x2, y2, text, size=8, align="l"):
    """žyma su tekstu (vietoj baliono)"""
    line(x1, y1, x2, y2, 0.3)
    c.saveState(); c.setFillColor(black); c.circle(x1, Y(y1), 1.0, stroke=0, fill=1); c.restoreState()
    T(x2 + (2 if align == "l" else -2), y2 + size * 0.35, text, size, align=align)


def view_title(xc, y, title, scale):
    T(xc, y, title, F_VIEW, font="FB", align="c")
    w = pdfmetrics.stringWidth(title, "FB", F_VIEW)
    line(xc - w / 2, y + 3, xc + w / 2, y + 3, 0.7)
    T(xc, y + 4 + F_SCALE * 1.25, scale, F_SCALE, align="c", color=GREY)


def hatch(x, y, w, h, step=5):
    c.saveState()
    p = c.beginPath(); p.rect(x, Y(y + h), w, h); c.clipPath(p, stroke=0, fill=0)
    c.setStrokeColor(GREY); c.setLineWidth(0.25)
    for i in range(-int(h), int(w) + int(h), step):
        # v183: brūkšniai apkerpami geometriškai (ne tik clipPath) - patikra_lapas nemato ilgų nematomų atkarpų per tekstus
        t0, t1 = max(0.0, -i / h), min(1.0, (w - i) / h)
        if t1 <= t0:
            continue
        c.line(x + i + t0 * h, Y(y + h - t0 * h), x + i + t1 * h, Y(y + h - t1 * h))
    c.restoreState()
    rect(x, y, w, h, lw=0.4)


# v15 (Rytis 2026-10-08): laidas - RAUDONA ištisinė stora linija (ISO 128: elektros laidas - atskira spalva / storis),
# niekada nesutampa su matmenų / kontūro linijomis; užrašai - ta pačia spalva
CABLE = HexColor("#E2001A")
CABLE_LW = 0.9


def cable_line(pts):
    poly(pts, stroke=CABLE, lw=CABLE_LW, close=False)


def centerline(x1, y1, x2, y2):
    line(x1, y1, x2, y2, 0.2, GREY, dash=([4, 1, 1, 1], 0))


# ------------------------------------------------------------------ keliai (kliento geometrija)
def bez(p0, p1, p2, p3, t):
    return tuple((1 - t) ** 3 * a + 3 * (1 - t) ** 2 * t * b + 3 * (1 - t) * t * t * cc + t ** 3 * dd
                 for a, b, cc, dd in zip(p0, p1, p2, p3))


def flatten(sp, n=10):
    pts, cur = [], None
    for s_ in sp:
        if s_[0] in ("M", "L"):
            cur = s_[1]; pts.append(cur)
        else:
            p0, (p1, p2, p3) = cur, s_[1:]
            for i in range(1, n + 1):
                pts.append(bez(p0, p1, p2, p3, i / n))
            cur = p3
    return pts


def path_of(sub, tf):
    p = c.beginPath()
    for sp in sub:
        for s_ in sp:
            if s_[0] == "M":
                p.moveTo(*tf(*s_[1]))
            elif s_[0] == "L":
                p.lineTo(*tf(*s_[1]))
            else:
                a, b, d = tf(*s_[1]), tf(*s_[2]), tf(*s_[3]); p.curveTo(a[0], a[1], b[0], b[1], d[0], d[1])
        p.close()
    return p


def draw_shape(sub, tf, fill=None, stroke=None, lw=0.3, dash=None):
    """tf(x_mm, y_mm) -> reportlab (x, y)"""
    c.saveState()
    if fill is not None:
        c.setFillColor(fill)
    if stroke is not None:
        c.setStrokeColor(stroke); c.setLineWidth(HAIR if VIEW_MODE else lw)
    if dash:
        c.setDash(*dash)
    c.drawPath(path_of(sub, tf), stroke=stroke is not None, fill=fill is not None, fillMode=0)
    c.restoreState()


def drawing_to_subpaths(d, tomm):
    """PyMuPDF drawing -> subpath'ai mm"""
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
    return [[(s_[0],) + tuple(tomm(q) for q in s_[1:]) for s_ in sp] for sp in subs]


def split_letters(subs):
    """vienas kelias gali turėti kelias raides: išoriniai kontūrai + jų skylės"""
    polys = []
    for sp in subs:
        f = flatten(sp, 8)
        if len(f) >= 3:
            polys.append((Polygon(f).buffer(0), sp, f))
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
    out = []
    for g in groups:
        xs_, ys_ = [q[0] for q in g["pts"]], [q[1] for q in g["pts"]]
        out.append({"sub": g["sub"], "bb": (min(xs_), min(ys_), max(xs_), max(ys_))})
    return out


def shape_geom(sub):
    ps = [Polygon(flatten(sp)).buffer(0) for sp in sub if len(flatten(sp)) >= 3]
    return reduce(lambda a, b: a.symmetric_difference(b), ps) if ps else Polygon()


def perim(sub):
    L = 0
    for sp in sub:
        f = flatten(sp, 16)
        L += sum(math.dist(a, b) for a, b in zip(f, f[1:] + f[:1]))
    return L


# ------------------------------------------------------------------ lapas: rėmelis, juosta, lentelės
# Rytis 2026-10-07: A3 paraštės - minimalios (5 mm iki išorinio rėmelio, 4 mm zonų juosta), daugiau darbinės erdvės
OX0, OY0, OX1, OY1 = 5 * MM, 5 * MM, W - 5 * MM, H - 5 * MM
B5 = 4 * MM
IX0, IY0, IX1, IY1 = OX0 + B5, OY0 + B5, OX1 - B5, OY1 - B5
BAND_H = 172
BAND_Y = IY1 - BAND_H
VIEW_BOT = BAND_Y - 14
ROW_H = 11                     # v18: BOM / MAIN DATA eilutė >= 11 pt (8 pt tekstas, nesugrūsta)


def set_band(n_rows):
    """Rytis 2026-10-07: apatinės informacijos juostos aukštis kinta pagal eilučių kiekį (BOM / MAIN DATA),
    eilutė >= ROW_H; minimumas 172 pt (antraštės lentelė + revizijos)."""
    global BAND_H, BAND_Y, VIEW_BOT
    BAND_H = max(172, 12 + 10 + ROW_H * n_rows + 10)
    BAND_Y = IY1 - BAND_H
    VIEW_BOT = BAND_Y - 14


def frame():
    rect(OX0, OY0, OX1 - OX0, OY1 - OY0, lw=0.5)
    rect(IX0, IY0, IX1 - IX0, IY1 - IY0, lw=1.0)
    for i in range(8):
        x0, x1 = IX0 + (IX1 - IX0) * i / 8, IX0 + (IX1 - IX0) * (i + 1) / 8
        for yb in ((OY0 + IY0) / 2 + 2.5, (OY1 + IY1) / 2 + 2.5):
            T((x0 + x1) / 2, yb - 0.5, i + 1, 8, align="c", color=GREY)
        if i:
            line(x0, OY0, x0, IY0, 0.3); line(x0, IY1, x0, OY1, 0.3)
    for j in range(6):
        y0, y1 = IY0 + (IY1 - IY0) * j / 6, IY0 + (IY1 - IY0) * (j + 1) / 6
        for xb in ((OX0 + IX0) / 2, (OX1 + IX1) / 2):
            T(xb, (y0 + y1) / 2 + 2, "ABCDEF"[j], 8, align="c", color=GREY)
        if j:
            line(OX0, y0, IX0, y0, 0.3); line(IX1, y0, OX1, y0, 0.3)
    pass                                                  # juostos viršų formuoja patys blokai (vientisas blokas)


def header(x, y, w, title):
    rect(x, y, w, 12, fill=HexColor("#EDEDED"), stroke=black, lw=0.7)
    T(x + 4, y + 9.0, title, 8.5, font="FB", auto_red=False)


def cell(x, y, w, h, label, val, size=8.5, font="F"):
    rect(x, y, w, h, lw=0.4)
    if label:
        T(x + 3, y + 7.5, label, F_INFO, color=GREY, auto_red=False)
    T(x + 4, y + h - 4, val, max(size, F_INFO), font=font, fit=w - 7, fit_min=F_INFO)


def main_data(x, y, w, h, rows_, title="MAIN DATA", lab_w=56):
    header(x, y, w, title)
    rh = max(ROW_H, (h - 12) / len(rows_))              # eilutės užpildo visą bloko aukštį
    ry = y + 12
    for lab, val in rows_:
        rect(x, ry, w, rh, lw=0.3)
        line(x + lab_w, ry, x + lab_w, ry + rh, 0.3)
        T(x + 3, ry + rh / 2 + 2.9, lab, F_INFO, color=GREY, auto_red=False)
        T(x + lab_w + 3, ry + rh / 2 + 2.9, val, F_INFO, fit=w - lab_w - 5, fit_min=F_INFO)
        ry += rh
    rect(x, y + 12, w, h - 12, lw=0.6)


def bom_table(x, y, w, h, rows_, title="BILL OF MATERIALS",
              cols=(("POS", 20), ("PART", 0.33), ("MATERIAL", 0.25), ("FINISH", 0.15), ("QTY  (PERIMETER / AREA)", None))):
    """eilutės: [pos, part, material, finish, qty]; qty gali turėti '\\n' - dvi eilutės"""
    header(x, y, w, title)
    free = w - 20
    cw = [20 if n_ == "POS" else (w_ * free if w_ else None) for n_, w_ in cols]
    cw[-1] = w - sum(v for v in cw[:-1])
    by = y + 12
    nlines = sum(max(1, str(r[-1]).count("\n") + 1, str(r[1]).count("\n") + 1) for r in rows_)
    lh = max(ROW_H, (h - 12 - 10) / max(nlines, 1))      # eilutės užpildo visą bloko aukštį
    cx_ = x
    for (n_, _), w_ in zip(cols, cw):
        rect(cx_, by, w_, 10, fill=HexColor("#F6F6F6"), lw=0.4); T(cx_ + 3, by + 7.6, n_, F_INFO, font="FB", fit=w_ - 5, fit_min=F_INFO); cx_ += w_
    by += 10
    for row in rows_:
        k = max(1, str(row[-1]).count("\n") + 1, str(row[1]).count("\n") + 1)
        rh = lh * k
        cx_ = x
        for (n_, _), w_, val in zip(cols, cw, row):
            # Rytis 2026-10-07: spalva - užpildomas VISAS FINISH langelis, jame - spalvos kodas
            cf_ = None
            if isinstance(val, str) and len(val) == 7 and val.startswith("#"):   # v160: originalo spalvos pavyzdėlis langelyje
                cf_, val = val, ""
            elif n_ == "FINISH":
                cf_ = code_hex(val)
            elif n_ == "MATERIAL":                     # plėvelė medžiagos stulpelyje (pvz. Avery 777-002CF)
                cf_ = code_hex(val, ral=False)
            rect(cx_, by, w_, rh, fill=HexColor(cf_) if cf_ else None, lw=0.3)
            if n_ == "POS":
                if str(val).strip():
                    balloon(cx_ + w_ / 2, by + rh / 2, val, max(5.0, min(5.6, lh / 2 - 0.4)))
            else:
                parts = str(val).split("\n")
                for li, pv in enumerate(parts):
                    yy = by + lh * li + lh / 2 + 2.9
                    tc_ = black
                    if cf_:
                        hc_ = HexColor(cf_)
                        if 0.299 * hc_.red + 0.587 * hc_.green + 0.114 * hc_.blue < 0.55:
                            tc_ = white
                    T(cx_ + 3, yy, pv, F_INFO, color=tc_, fit=w_ - 5, fit_min=F_INFO)
            cx_ += w_
        by += rh
    rect(x, y + 12, w, h - 12, lw=0.6)


def title_block(x, w, spec, scales):
    """Rytis 2026-10-07 (pavyzdys): CLIENT - užsakovas (pvz. BrandFactory), didelis paryškintas ORDER NO.,
    FILE / DRAWING NO. - užsakovo užsakymo Nr. (`drawing_no`), įmonės pavadinimo langelio apačioje NĖRA."""
    rows_h = (30, 24, 30, 24, 28)
    tbh = sum(rows_h)
    ty = IY1 - tbh
    revs = spec.get("revisions", [[spec.get("rev", "A"), "First issue", spec["date"], ""]])
    rvy = BAND_Y
    header(x, rvy, w, "REVISIONS")
    rc = [("REV", 24), ("DESCRIPTION", w - 24 - 58 - 40), ("DATE", 58), ("BY", 40)]
    yy = rvy + 12
    for i, rowv in enumerate([[n for n, _ in rc]] + revs):
        xx = x
        for (n, cw_), v in zip(rc, rowv):
            rect(xx, yy, cw_, 10 if i == 0 else 11, fill=HexColor("#F6F6F6") if i == 0 else None, lw=0.35)
            T(xx + 2.5, yy + 7.8 if i == 0 else yy + 8.2, v, F_INFO, font="FB" if i == 0 else "F")
            xx += cw_
        yy += 10 if i == 0 else 11
    # Rytis 2026-10-07: tuščios revizijų eilutės iki antraštės lentelės - be tuščių plotų
    while yy + 11 <= ty - 0.5:
        hh_ = 11 if yy + 22 <= ty else ty - yy
        xx = x
        for _, cw_ in rc:
            rect(xx, yy, cw_, hh_, lw=0.35); xx += cw_
        yy += hh_
    if yy < ty - 0.5:
        xx = x
        for _, cw_ in rc:
            rect(xx, yy, cw_, ty - yy, lw=0.35); xx += cw_
    rect(x, rvy + 12, w, ty - rvy - 12, lw=0.6)
    y0 = ty
    cell(x, y0, w, rows_h[0], "CLIENT", spec["client"], 14, "FB"); y0 += rows_h[0]
    cell(x, y0, w, rows_h[1], "TITLE", spec["title"], 9.5); y0 += rows_h[1]
    _on = spec.get("order_no", "")                      # Rytis 2026-10-07: formatas ALT0000_00.00_RS, paryškintas
    if unk(_on) or not str(_on).strip():
        _on = "ALT0000_00.00_RS"
    cell(x, y0, w * 0.4, rows_h[2], "ORDER NO.", _on, 14, "FB")
    cell(x + w * 0.4, y0, w * 0.6, rows_h[2], "FILE / DRAWING NO.", spec.get("drawing_no", spec.get("file_code", "")), 12)
    y0 += rows_h[2]
    fr_ = (0.27, 0.16, 0.16, 0.16, 0.25)
    xx_ = x
    for f_, (lab, val) in zip(fr_, (("SCALE (DIM. mm)", scales), ("FORMAT", "A3"), ("SHEET", spec.get("sheet", "1 / 1")),
                                    ("REV.", spec.get("rev", "A")), ("PROJECTION", ""))):
        cell(xx_, y0, w * f_, rows_h[3], lab, val, 9.5)
        xx_ += w * f_
    px_, py_ = x + w * (1 - fr_[-1] / 2), y0 + 15
    poly([(px_ - 13, py_ - 3), (px_ - 4, py_ - 5.5), (px_ - 4, py_ + 5.5), (px_ - 13, py_ + 3)], lw=0.5)
    c.saveState(); c.setLineWidth(0.5)
    c.circle(px_ + 6, Y(py_), 5.5); c.circle(px_ + 6, Y(py_), 3); c.restoreState()
    line(px_ - 15, py_, px_ + 13, py_, 0.2, black, dash=([4, 1, 1, 1], 0))
    y0 += rows_h[3]
    cell(x, y0, w * 0.22, rows_h[4], "DRAWN", spec.get("drawn", ""), 9.5)
    cell(x + w * 0.22, y0, w * 0.22, rows_h[4], "CHECKED", spec.get("checked", ""), 9.5)
    cell(x + w * 0.44, y0, w * 0.22, rows_h[4], "DATE", spec["date"], 9.5)
    cell(x + w * 0.66, y0, w * 0.34, rows_h[4], "", "", 9.5)
    rect(x, ty, w, tbh, lw=1.0)


# ------------------------------------------------------------------ P6 tipinis pjūvis (juostai)
def p6_reference(x, y, w, h, depth, kind="u", front="3mm", title=None, ears=None, ear_hole=0.15, bracket=None):
    """P6 pjūvis iš Rytio etaloninio brėžinio (vektorinis įterpimas, scripts/p6_ref.py) + gylio matmuo.
    kind: 'folded' / 'u' / 'square'. Variantui 'plate' (6+3) etalono nėra - naudoti p6_typical."""
    import p6_ref
    header(x, y, w, title or "PROFILE P6 - TYPICAL SECTION")
    rect(x, y + 12, w, h - 12, lw=0.6)
    p6_ref.draw(c, H, x, y + 12, w, h - 12, kind, front, depth, leader=leader, balloon=balloon, T=T, hdim=hdim,
                hair=HAIR, ears=ears, ear_hole=ear_hole, bracket=bracket)


def rail_section(x, y, w, h, t, kind="u", opening="left", fill=None, lw=0.4):
    """v47 (Rytis 2026-10-09): profilio PJŪVIS - forma pagal tipą VISUOSE vaizduose: 'u' - U (anga `opening` pusėje:
    left/right/up/down), 'sq' - stačiakampis vamzdis (tuščiaviduris). x, y - kairys viršutinis kampas."""
    fill = fill or HexColor("#9A9A9A")
    t = max(min(t, w / 3, h / 3), 0.5)
    if kind == "sq":
        rect(x, y, w, h, fill=fill, lw=lw)
        rect(x + t, y + t, w - 2 * t, h - 2 * t, fill=white, lw=lw * 0.6)
        return
    x1, y1 = x + w, y + h
    if opening == "left":
        pts = [(x, y), (x1, y), (x1, y1), (x, y1), (x, y1 - t), (x1 - t, y1 - t), (x1 - t, y + t), (x, y + t)]
    elif opening == "right":
        pts = [(x1, y), (x, y), (x, y1), (x1, y1), (x1, y1 - t), (x + t, y1 - t), (x + t, y + t), (x1, y + t)]
    elif opening == "up":
        pts = [(x, y), (x, y1), (x1, y1), (x1, y), (x1 - t, y), (x1 - t, y1 - t), (x + t, y1 - t), (x + t, y)]
    else:
        pts = [(x, y1), (x, y), (x1, y), (x1, y1), (x1 - t, y1), (x1 - t, y + t), (x + t, y + t), (x + t, y1)]
    poly(pts, fill=fill, lw=lw)


def _plate_rails(plx, wall, yt, yb, py0, ph_, fs, num, kind="u"):
    """v44: bėgeliai už plokštės (vientisas rėmas) - padėtys fs = dalis nuo raidės viršaus (kaip priekio vaizde).
    v47: forma pagal profilį - U (sienelė prie plokštės, anga į sieną) arba stačiakampis."""
    fs = fs or [None]
    for k_, f_ in enumerate(fs):
        ry_ = py0 + ph_ * 0.5 if f_ is None else yt + (yb - yt) * f_
        ry_ = min(max(ry_, py0 + 18), py0 + ph_ - 12)
        rail_section(wall, ry_ - 8, plx - wall, 16, 1.0, kind, "left", fill=HexColor("#9A9A9A"), lw=0.35)
        if k_ == len(fs) - 1:
            leader(wall + 0.4, ry_ + 4, wall - 10, ry_ + 18, num, 5)


def p6_typical(x, y, w, h, depth, variant="rail", title=None, show_magnifier=True, numbers=None, boxed=True,
               plate_rail=None, front="3mm", plate_z=False, plate_rail_f=None, rail_kind="u"):
    """P6 sandara: variant 'rail' (ant U bėgelio su L tvirtinimu), 'folded' (ant folded plokštės),
    'plate' (6+3: galas įleistas 25 mm, ant Alu plokštės su distanceriais 30 mm).
    front: '3mm' - plexi 3 mm + PVC bortelis (A) ir varžtas (B) per šoną į bortelį;
           '8mm' - plexi 8 mm su frezuota briauna (A, liežuvis šonų viduje), varžtas (B) per šoną į liežuvį."""
    nm = {"face": 1, "ret": 2, "back": 3, "led": 4, "mount": 5, "fit": 6, "plate": 8, "spacer": 9}
    nm.update(numbers or {})
    if boxed:
        header(x, y, w, title or "PROFILE P6 - TYPICAL SECTION")
        rect(x, y + 12, w, h - 12, lw=0.6)
    set_view(True)
    px0, py0, pw_, ph_ = x, y + 12, w, h - 12
    C5, C3, C2, CA = HexColor("#E2E2E2"), HexColor("#B4B4B4"), HexColor("#6E6E6E"), HexColor("#C8C8C8")
    wall = px0 + 16
    yt, yb = py0 + 28, py0 + ph_ - 14
    RT = 3.6
    if variant == "plate":
        plx = wall + (16 if (plate_rail or plate_z) else 0)   # plokštė (ant bėgelio / Z rėmo, jei yra)
        bgx = plx + 3 + 14                # šonų galinė briauna (30 mm atstumas)
        recess = 10                       # galas įleistas (25 mm)
        Dp = min(76, pw_ * 0.40)
    else:
        bgx = wall + (18 if variant == "rail" else 12)
        recess = 0
        Dp = min(80, pw_ * 0.42)
    xf = bgx + Dp
    if variant == "folded":
        rect(bgx - 9, py0 + 14, 9, ph_ - 20, fill=C5, lw=0.45)
    if variant == "plate":
        rect(plx, py0 + 10, 3, ph_ - 14, fill=C5, lw=0.45)                         # plokštė
    backx = bgx + recess
    rect(backx, yt + RT, 4, yb - yt - 2 * RT, fill=C3, lw=0.45)                    # galas
    rect(bgx, yt, xf - bgx, RT, fill=C2, lw=0.45)                                   # šonai
    rect(bgx, yb - RT, xf - bgx, RT, fill=C2, lw=0.45)
    F8 = front == "8mm"
    TF = 7.0 if F8 else 3.2                                                          # plexi storis
    if F8:                                                                           # 8 mm: liežuvis šonų viduje
        tg = 6.0
        rect(xf - tg, yt + RT, tg, yb - yt - 2 * RT, fill=white, lw=0.45)            # frezuota briauna (A)
        rect(xf, yt, TF, yb - yt, fill=white, lw=0.5)                                # plexi 8 mm (lygiai su šonais)
        for yy_, sg in ((yt, 1), (yb, -1)):                                          # B varžtas per šoną į liežuvį
            bxv = xf - tg / 2
            hy = yy_ - 2.2 if sg > 0 else yy_
            rect(bxv - 2.6, hy, 5.2, 2.2, fill=HexColor("#3A3A3A"), lw=0.3)
            s0 = yy_ if sg > 0 else yy_ - RT - 4
            rect(bxv - 0.9, s0, 1.8, RT + 4, fill=HexColor("#3A3A3A"), lw=0.2)
    else:
        rect(xf, yt - 1.5, 3.2, yb - yt + 3, fill=white, lw=0.5)                    # plexi
    for yy_, sg in (() if F8 else ((yt + RT, 1), (yb - RT, -1))):                   # A PVC + B varžtas
        pvh = 1.8
        rect(xf - 10, yy_ if sg > 0 else yy_ - pvh, 10, pvh, fill=CA, lw=0.35)
        bxv = xf - 5
        hy = yt - 2.2 if sg > 0 else yb
        rect(bxv - 2.6, hy, 5.2, 2.2, fill=HexColor("#3A3A3A"), lw=0.3)
        s0 = yt if sg > 0 else yb - RT - pvh - 1
        rect(bxv - 0.9, s0, 1.8, RT + pvh + 1, fill=HexColor("#3A3A3A"), lw=0.2)
    for f_ in (0.27, 0.5, 0.73):                                                     # LED
        ly_ = yt + (yb - yt) * f_
        rect(backx + 4, ly_ - 7, 4.5, 14, fill=white, lw=0.4)
        for d_ in (-4, 0, 4):
            rect(backx + 8.5, ly_ + d_ - 1.2, 1.6, 2.4, fill=white, lw=0.3)
    if variant == "plate":                                                           # 6+3: LED ir gale (į plokštę)
        for f_ in (0.36, 0.64):
            ly_ = yt + (yb - yt) * f_
            rect(backx - 4.5, ly_ - 7, 4.5, 14, fill=white, lw=0.4)
            for d_ in (-4, 0, 4):
                rect(backx - 6.1, ly_ + d_ - 1.2, 1.6, 2.4, fill=white, lw=0.3)
    line(backx + 13, yt + (yb - yt) * 0.27, backx + 13, yt + (yb - yt) * 0.73, 0.35)
    for f_ in (0.27, 0.5, 0.73):
        line(backx + 8.5, yt + (yb - yt) * f_, backx + 13, yt + (yb - yt) * f_, 0.35)
    if variant == "rail":
        # U bėgelis (sienelė prie raidės galo, anga į sieną) + ausėlė (L): horizontali kojelė U viduje ant
        # flanšo, vertikali - sienos plokštumoje, VISADA į rėmo vidų (viršutinis - žemyn, apatinis - aukštyn)
        t_, Uh = 1.2, 16.0
        ux0 = wall + t_ + 0.4
        for k_, yc in enumerate((yt + (yb - yt) * 0.13, yt + (yb - yt) * 0.87)):
            uy = yc - Uh / 2
            poly([(ux0, uy), (bgx, uy), (bgx, uy + Uh), (ux0, uy + Uh), (ux0, uy + Uh - t_), (bgx - t_, uy + Uh - t_),
                  (bgx - t_, uy + t_), (ux0, uy + t_)], fill=HexColor("#B4B4B4"), lw=0.4)
            hx1 = bgx - t_ - 1.5
            if k_ == 0:                                   # viršutinis bėgelis - ausėlė žemyn
                hy0 = uy + Uh - 2 * t_
                pts = [(wall, hy0), (hx1, hy0), (hx1, hy0 + t_), (wall + t_, hy0 + t_), (wall + t_, uy + Uh + 18),
                       (wall, uy + Uh + 18)]
                hc = uy + Uh + 10
            else:                                         # apatinis bėgelis - ausėlė aukštyn
                hy0 = uy + t_
                pts = [(wall, hy0 + t_), (hx1, hy0 + t_), (hx1, hy0), (wall + t_, hy0), (wall + t_, uy - 18), (wall, uy - 18)]
                hc = uy - 10
            poly(pts, fill=HexColor("#8C8C8C"), lw=0.4)
            line(wall - 4, hc, wall + t_ + 4, hc, 0.2, GREY, dash=([3, 1, 1, 1], 0))   # Ø6 skylės ašis
    if variant == "plate":                                                           # distanceriai
        for yc in (yt + (yb - yt) * 0.18, yt + (yb - yt) * 0.82):
            rect(plx + 3, yc - 1.2, backx - plx - 3, 2.4, fill=HexColor("#D9D9D9"), lw=0.3)
            rect(backx + 4, yc - 2.2, 1.6, 4.4, fill=HexColor("#3A3A3A"), lw=0.2)
        hchain(py0 + 20, [plx + 3, bgx, backx], [yt, yt, yt + RT], ["30", "25"], 8)   # v29: >= 8 pt
        if plate_z:          # Rytis 2026-10-07: TIK apskritimo Z juostos - viršuje ir apačioje ties varžtais (7)
            zt_, zf_ = 0.9, 10.0
            for k_, fy_ in enumerate((0.18, 0.82)):
                y_ = yt + (yb - yt) * fy_ - zf_ / 2
                poly([(plx, y_), (plx - zt_, y_), (plx - zt_, y_ + zf_ - zt_), (wall + zt_, y_ + zf_ - zt_),
                      (wall + zt_, y_ + 2 * zf_ - zt_), (wall, y_ + 2 * zf_ - zt_), (wall, y_ + zf_), (plx, y_ + zf_)],
                     fill=HexColor("#C4C7CA"), lw=0.35)
                if k_ == 0:
                    leader(plx - 2, y_ + 3, wall - 10, y_ - 8, nm.get("zp", 11), 5)
        if plate_rail:                                                             # U bėgelis(-iai) už plokštės
            _plate_rails(plx, wall, yt, yb, py0, ph_, plate_rail_f, nm.get("prail", 9), rail_kind)
    c.saveState(); c.setLineWidth(0.4); c.circle(xf - 1, Y(yt + 1), 9); c.restoreState()
    hdim(bgx, xf + TF, py0 + 10, f"{depth:.0f}", yt, yt - (0 if F8 else 1.5))
    bcol = px0 + pw_ - 12 if not show_magnifier else xf + 22
    leader(xf + TF / 2, yt + (yb - yt) * 0.40, xf + TF + 15, yt + (yb - yt) * 0.40, nm["face"])
    leader(bgx + Dp * 0.55, yt + RT / 2, bgx + Dp * 0.55, py0 + 20 if variant == "plate" else py0 + 14, nm["ret"])
    leader(backx + 2, yt + (yb - yt) * 0.86, xf - 18, yt + (yb - yt) * 0.86, nm["back"])
    leader(backx + 13, yt + (yb - yt) * 0.62, backx + 32, yt + (yb - yt) * 0.62, nm["led"])
    if variant == "rail":
        leader(wall + 10, yt + (yb - yt) * 0.13 - 8, wall + 4, py0 + 14, nm["mount"], 5)
        leader(wall + 0.6, yt + (yb - yt) * 0.13 + 22, wall - 10, yt + (yb - yt) * 0.40, nm["fit"], 5)
    elif variant == "plate":
        sy_ = py0 + ph_ * (0.32 if plate_rail else (0.62 if plate_z else 0.5))
        leader(plx + 1.5, sy_, wall - 4, sy_, nm["plate"], 5)
        leader(plx + 8, yt + (yb - yt) * 0.82, plx + 12, yb + 7, nm["spacer"], 5)
        leader(backx - 3, yt + (yb - yt) * 0.36, backx - 3 + 0.01, py0 + ph_ * 0.5 - 4, nm["led"], 5) if False else None
    else:
        leader(bgx - 4.5, py0 + ph_ * 0.5, px0 + 10, py0 + ph_ * 0.5, nm["mount"], 5)
    if show_magnifier:
        mcx, mcy, MR = px0 + pw_ - 40, py0 + 46, 30
        c.saveState()
        cp_ = c.beginPath(); cp_.circle(mcx, Y(mcy), MR); c.clipPath(cp_, stroke=0, fill=0)
        rect(mcx - MR, mcy - 9, MR + 12, 9, fill=C2, lw=0.5)
        PWm = 16 if F8 else 8
        rect(mcx + 12, mcy - (9 if F8 else MR), PWm, 2 * MR, fill=white, lw=0.7)
        for k_ in range(-12, 13):
            line(mcx + 12 + PWm - 0.4, mcy + k_ * 3, mcx + 12.4, mcy + k_ * 3 + 3, 0.2, GREY)
        if F8:                                    # frezuota briauna - plexi liežuvis po šonu
            rect(mcx - 16, mcy, 28, 12, fill=white, lw=0.5)
            for k_ in range(-6, 6):
                line(mcx - 16 + k_ * 3 + 3, mcy + 12, mcx - 16 + k_ * 3 + 9, mcy, 0.2, GREY)
        else:
            rect(mcx - 16, mcy, 28, 5.5, fill=CA, lw=0.5)
        rect(mcx - 6.5, mcy - 13.5, 11, 4.5, fill=HexColor("#3A3A3A"), lw=0.4)
        rect(mcx - 3, mcy - 9, 4, 17, fill=HexColor("#D9D9D9"), lw=0.4)
        for k_ in range(6):
            yk = mcy - 7 + k_ * 2.6
            line(mcx - 3, yk, mcx + 1, yk + 1.3, 0.3)
        centerline(mcx - 1, mcy - 16, mcx - 1, mcy + 11)
        c.restoreState()
        c.saveState(); c.setLineWidth(0.5); c.circle(mcx, Y(mcy), MR); c.restoreState()
        leader(mcx - 11, mcy + 2.8, mcx - 14, mcy + MR + 9, "A")
        leader(mcx - 3, mcy - 11, mcx - 22, mcy - 22, "B")
        T(mcx - 24, mcy - 12, "2", 6.5, auto_red=False)
        T(mcx + 24, mcy + 22, "1", 6.5, auto_red=False)
        T(mcx, mcy + MR + 24, "A - milled edge   B - bolt" if F8 else "A - PVC edge   B - bolt", 5.4, color=GREY,
          align="c", auto_red=False)
    set_view(False)


def p1_typical(x, y, w, h, depth, variant="rail", title=None, numbers=None, boxed=True, plate_z=False, ears=True,
                plate_rail=None, spacer_mm=30, plate_rail_f=None, rail_kind="u", bracket=None):
    """v29 (Rytis 2026-10-08, EXTRA order 225978): P1 - NEŠVIEČIANTI tūrinė raidė: priekis Alu 2 mm (RAL), šonai Alu 1 mm,
    dugnas PVC 10 mm (kaip SPAR P1 etalone), BE LED ir BE plexi. variant: 'rail' (ant U bėgelių su ausėlėmis) arba
    'plate' (ant Alu plokštės su distanceriais 30 mm, nugara - lygiai su šonais, ne įleista)."""
    nm = {"face": 1, "ret": 2, "back": 3, "mount": 5, "fit": 6, "plate": 8, "spacer": 7, "zp": 11}
    nm.update(numbers or {})
    if boxed:
        header(x, y, w, title or "PROFILE P1 - TYPICAL SECTION")
        rect(x, y + 12, w, h - 12, lw=0.6)
    set_view(True)
    px0, py0, pw_, ph_ = x, y + 12, w, h - 12
    SECT = HexColor("#111111")
    wall = px0 + 16
    yt, yb = py0 + 28, py0 + ph_ - 14
    RT, TFc, TB = 1.6, 2.4, 5.0                                  # šonas 1, priekis 2, dugnas PVC 10 (nominaliai)
    if variant == "plate":
        plx = wall + (16 if (plate_z or plate_rail) else 0)     # v44: plokštė ant vientiso rėmo U bėgelio
        bgx = plx + 3 + (14 if spacer_mm else 0)                 # 30 mm distanceriai; 0 - raidė tiesiai ant plokštės
        Dp = min(76, pw_ * 0.40)
    else:
        bgx = wall + 18
        Dp = min(80, pw_ * 0.42)
    xf = bgx + Dp
    # v185 (Rytis 2026-10-13): pjūvis VISADA centruojamas savo bloke (turinys nuo sienos štrichavimo / balionų iki priekio baliono)
    _cl, _cr = wall - 16, xf + 21
    _dx = (px0 + (pw_ - (_cr - _cl)) / 2) - _cl
    wall += _dx; bgx += _dx; xf += _dx
    if variant == "plate":
        plx += _dx
    if variant == "plate":
        rect(plx, py0 + 10, 3, ph_ - 14, fill=HexColor("#E2E2E2"), lw=0.45)
    # dugnas PVC 10 mm - štrichuotas
    rect(bgx, yt + RT + 0.5, TB, yb - yt - 2 * RT - 1, fill=HexColor("#D9D9D9"), lw=0.45)
    c.saveState(); p_ = c.beginPath(); p_.rect(bgx, Y(yb - RT - 0.5), TB, yb - yt - 2 * RT - 1); c.clipPath(p_, stroke=0, fill=0)
    c.setLineWidth(0.2); c.setStrokeColor(GREY)
    k_ = yt
    while k_ < yb + TB:
        c.line(bgx, Y(k_), bgx + TB, Y(k_ - TB)); k_ += 2.2
    c.restoreState()
    # šonai Alu 1 mm (pjūvis - juodai) ir priekis Alu 2 mm; tarp gretimų - balta linija
    rect(bgx, yt, Dp - TFc - 0.5, RT, fill=SECT, lw=0.3)
    rect(bgx, yb - RT, Dp - TFc - 0.5, RT, fill=SECT, lw=0.3)
    rect(xf - TFc, yt, TFc, yb - yt, fill=SECT, lw=0.3)
    # kniedės šonas -> dugnas
    for yy_ in (yt, yb - RT):
        rect(bgx + 1.2, yy_ - 0.8 if yy_ == yt else yy_ + RT, 2.6, 0.8, fill=HexColor("#3A3A3A"), lw=0.2)
    if variant == "rail":
        t_, Uh = 1.2, 16.0
        ux0 = wall + t_ + 0.4
        for k2, yc in enumerate((yt + (yb - yt) * 0.13, yt + (yb - yt) * 0.87)):
            uy = yc - Uh / 2
            poly([(ux0, uy), (bgx, uy), (bgx, uy + Uh), (ux0, uy + Uh), (ux0, uy + Uh - t_), (bgx - t_, uy + Uh - t_),
                  (bgx - t_, uy + t_), (ux0, uy + t_)], fill=HexColor("#B4B4B4"), lw=0.4)
            hx1 = bgx - t_ - 1.5
            if ears:
                if k2 == 0:
                    hy0 = uy + Uh - 2 * t_
                    pts = [(wall, hy0), (hx1, hy0), (hx1, hy0 + t_), (wall + t_, hy0 + t_), (wall + t_, uy + Uh + 18),
                           (wall, uy + Uh + 18)]
                    hc = uy + Uh + 10
                else:
                    hy0 = uy + t_
                    pts = [(wall, hy0 + t_), (hx1, hy0 + t_), (hx1, hy0), (wall + t_, hy0), (wall + t_, uy - 18), (wall, uy - 18)]
                    hc = uy - 10
                poly(pts, fill=HexColor("#8C8C8C"), lw=0.4)
                line(wall - 4, hc, wall + t_ + 4, hc, 0.2, GREY, dash=([3, 1, 1, 1], 0))
            if bracket is not None:
                # v184 (Rytis 2026-10-13: „hangers turi atsispindėti ir profilio pjūvyje") - U laikiklio plokštuma virš
                #  viršutinio / po apatiniu bėgeliu (rėmas + 2 mm laisvumas viršuje), Ø6 per plokštumą į bėgelį
                mm_ = Uh / 30.0; t3_ = 3 * mm_; gp_ = 2 * mm_
                fy_ = (uy - gp_ - t3_) if k2 == 0 else (uy + Uh)
                rect(wall, fy_, bgx - wall, t3_, fill=HexColor("#8C8C8C"), lw=0.4)
                ux_c = (ux0 + bgx) / 2
                ya_, yb_ = ((fy_ - 3, uy + Uh * 0.5) if k2 == 0 else (uy + Uh * 0.5, fy_ + t3_ + 3))
                line(ux_c, ya_, ux_c, yb_, 0.2, GREY, dash=([3, 1, 1, 1], 0))
                if k2 == 0:
                    _bk_top = fy_
                else:
                    _bk_bot = fy_ + t3_
            # varžtas per U sienelę į PVC dugną
            rect(bgx - t_ - 2.2, yc - 2.2, 2.2, 4.4, fill=HexColor("#3A3A3A"), lw=0.2)
            rect(bgx - t_, yc - 0.9, t_ + TB - 1, 1.8, fill=HexColor("#3A3A3A"), lw=0.2)
            line(bgx - 8, yc, bgx + TB + 3, yc, 0.2, GREY, dash=([3, 1, 1, 1], 0))
    if variant == "rail" and bracket is not None:          # v184: laikiklio sienelė prie fasado tarp plokštumų
        rect(wall, _bk_top, (Uh / 30.0) * 3, _bk_bot - _bk_top, fill=HexColor("#8C8C8C"), lw=0.4)
    if variant == "plate" and spacer_mm:
        for yc in (yt + (yb - yt) * 0.18, yt + (yb - yt) * 0.82):
            rect(plx + 3, yc - 1.2, bgx - plx - 3, 2.4, fill=HexColor("#D9D9D9"), lw=0.3)
            rect(bgx + TB, yc - 2.2, 1.6, 4.4, fill=HexColor("#3A3A3A"), lw=0.2)
        hchain(py0 + 20, [plx + 3, bgx], [yt, yt], [f"{spacer_mm:.0f}"], 8)
    elif variant == "plate":                                     # v44: raidė tiesiai ant plokštės - varžtas per plokštę į PVC dugną
        _sf = (0.18, 0.82)
        if plate_rail and plate_rail_f and any(abs(a_ - b_) < 0.12 for a_ in _sf for b_ in plate_rail_f):
            _sf = (0.38, 0.62)                                   # varžtai ne ties bėgeliais
        for yc in (yt + (yb - yt) * _sf[0], yt + (yb - yt) * _sf[1]):
            rect(plx - 2.0, yc - 2.2, 2.0, 4.4, fill=HexColor("#3A3A3A"), lw=0.2)
            rect(plx, yc - 0.9, 3 + TB - 1, 1.8, fill=HexColor("#3A3A3A"), lw=0.2)
            line(plx - 6, yc, bgx + TB + 3, yc, 0.2, GREY, dash=([3, 1, 1, 1], 0))
    if variant == "plate" and plate_rail:                        # U bėgeliai už plokštės (vientisas rėmas)
        _plate_rails(plx, wall, yt, yb, py0, ph_, plate_rail_f, nm.get("prail", 5), rail_kind)
        if plate_z:
            zt_, zf_ = 0.9, 10.0
            for k2, fy_ in enumerate((0.18, 0.82)):
                y_ = yt + (yb - yt) * fy_ - zf_ / 2
                poly([(plx, y_), (plx - zt_, y_), (plx - zt_, y_ + zf_ - zt_), (wall + zt_, y_ + zf_ - zt_),
                      (wall + zt_, y_ + 2 * zf_ - zt_), (wall, y_ + 2 * zf_ - zt_), (wall, y_ + zf_), (plx, y_ + zf_)],
                     fill=HexColor("#C4C7CA"), lw=0.35)
                if k2 == 0:
                    leader(plx - 2, y_ + 3, wall - 10, y_ - 8, nm["zp"], 5)
    set_view(False)
    hdim(bgx, xf, py0 + 10, f"{depth:.0f}", yt, yt)
    leader(xf - TFc / 2, yt + (yb - yt) * 0.40, xf + 15, yt + (yb - yt) * 0.40, nm["face"])
    leader(bgx + Dp * 0.55, yt + RT / 2, bgx + Dp * 0.55, py0 + 20 if variant == "plate" else py0 + 14, nm["ret"])
    leader(bgx + TB / 2, yt + (yb - yt) * 0.62, xf - 18, yt + (yb - yt) * 0.62, nm["back"])
    if variant == "rail":
        leader(wall + 10, yt + (yb - yt) * 0.13 - 8, wall + 4, py0 + 14, nm["mount"], 5)
        if ears:
            leader(wall + 0.6, yt + (yb - yt) * 0.13 + 22, wall - 10, yt + (yb - yt) * 0.40, nm["fit"], 5)
        elif bracket:
            leader(wall + 0.8, yt + (yb - yt) * 0.5, wall - 10, yt + (yb - yt) * 0.40, str(bracket), 5)
    else:
        sy_ = py0 + ph_ * (0.32 if plate_rail else (0.62 if plate_z else 0.5))
        leader(plx + 1.5, sy_, wall - 4, sy_, nm["plate"], 5)
        if spacer_mm:
            leader(plx + 8, yt + (yb - yt) * 0.82, plx + 12, yb + 7, nm["spacer"], 5)
        else:
            _sf2 = 0.62 if (plate_rail and plate_rail_f and any(abs(0.82 - b_) < 0.12 for b_ in plate_rail_f)) else 0.82
            leader(plx - 1, yt + (yb - yt) * _sf2, plx - 8, yb + 7, nm["spacer"], 5)
    if variant == "rail":
        T(px0 + pw_ / 2, py0 + ph_ - 3, "P1 - non-lit: Alu face 2 / return 1 / PVC back 10", F_INFO, color=GREY, align="c",
          auto_red=False)


# ------------------------------------------------------------------ 3D (aksonometrija)
class View3D:
    """Paprastas 3D: kietieji kūnai = (geometrija y-aukštyn mm, z0, z1, šono spalva, priekio spalva)."""

    def __init__(self, yaw=32, pitch=17, light=(-0.45, 0.75, 0.55)):
        self.th, self.ph = math.radians(yaw), math.radians(pitch)
        ln = math.sqrt(sum(v * v for v in light)); self.L = tuple(v / ln for v in light)
        self.k = 1; self.ox = 0; self.oy = 0

    def rot(self, x, y, z):
        ct, st, cp, sp = math.cos(self.th), math.sin(self.th), math.cos(self.ph), math.sin(self.ph)
        x1, z1 = x * ct + z * st, -x * st + z * ct
        return x1, y * cp - z1 * sp, y * sp + z1 * cp

    def fit(self, pts3, box):
        x, y, w, h = box
        r = [self.rot(*p) for p in pts3]
        xs, ys = [p[0] for p in r], [p[1] for p in r]
        self.k = min(w / (max(xs) - min(xs)), h / (max(ys) - min(ys)))
        self.ox = x + (w - (max(xs) - min(xs)) * self.k) / 2 - min(xs) * self.k
        self.oy = Y(y + h) + (h - (max(ys) - min(ys)) * self.k) / 2 - min(ys) * self.k

    def S(self, x, y, z):
        r = self.rot(x, y, z); return self.ox + r[0] * self.k, self.oy + r[1] * self.k

    def shade(self, col, n, amb=0.55):
        k = amb + (1 - amb) * max(0.0, n[0] * self.L[0] + n[1] * self.L[1] + n[2] * self.L[2])
        return Color(min(1, col.red * k), min(1, col.green * k), min(1, col.blue * k))

    def fpoly(self, pts3, fill, stroke=None, lw=0.2, alpha=None):
        c.saveState()
        c.setFillColor(fill); c.setStrokeColor(stroke or fill); c.setLineWidth(HAIR)      # v63: 3D - hairline
        if alpha is not None:
            c.setFillAlpha(alpha)
        p = c.beginPath(); p.moveTo(*self.S(*pts3[0]))
        for q in pts3[1:]:
            p.lineTo(*self.S(*q))
        p.close(); c.drawPath(p, stroke=1 if (stroke is not None or alpha is None) else 0, fill=1)
        c.restoreState()

    def wall(self, x0, y0, x1, y1, z, shadow_geoms=(), dz=60):
        c.saveState()
        wp = c.beginPath(); wp.moveTo(*self.S(x0, y0, z))
        for q in ((x1, y0, z), (x1, y1, z), (x0, y1, z)):
            wp.lineTo(*self.S(*q))
        wp.close(); c.clipPath(wp, stroke=0, fill=0)
        a_, b_ = self.S(x0, y1, z), self.S(x1, y0, z)
        c.linearGradient(a_[0], a_[1], b_[0], b_[1], (HexColor("#F7F7F7"), HexColor("#E3E3E3")), extend=True)
        sdx, sdy = -self.L[0] / self.L[2] * dz, -self.L[1] / self.L[2] * dz
        from shapely.affinity import translate
        for g in shadow_geoms:
            for grow, al in [(70 - 7 * j, 0.022) for j in range(11)]:
                sh = translate(g, sdx, sdy).buffer(grow, join_style=1)
                for gg in getattr(sh, "geoms", [sh]):
                    self.fpoly([(x, y, z) for x, y in list(gg.exterior.coords)[:-1]], black, alpha=al)
        c.restoreState()

    def solid(self, geom, z0, z1, side, face, face_stroke=HexColor("#9A9A9A")):
        """geom - shapely (y aukštyn); šonai pagal šviesą, priekis z1"""
        for g in getattr(geom, "geoms", [geom]):
            g = orient(g, 1.0)
            quads = []
            for ring in [g.exterior] + list(g.interiors):
                pts = list(ring.coords)
                for (x0_, y0_), (x1_, y1_) in zip(pts[:-1], pts[1:]):
                    L_ = math.hypot(x1_ - x0_, y1_ - y0_)
                    if L_ < 1e-6:
                        continue
                    n = ((y1_ - y0_) / L_, -(x1_ - x0_) / L_, 0.0)
                    if self.rot(*n)[2] <= 0:
                        continue
                    qd = [(x0_, y0_, z0), (x1_, y1_, z0), (x1_, y1_, z1), (x0_, y1_ * 0 + y0_, z1)]
                    qd[3] = (x0_, y0_, z1)
                    quads.append((sum(self.rot(*v)[2] for v in qd) / 4, qd, n))
            for _, qd, n in sorted(quads, key=lambda t: t[0]):
                col = self.shade(side, n)
                self.fpoly(qd, col, col, 0.25)
            c.saveState(); c.setFillColor(face); c.setStrokeColor(face_stroke); c.setLineWidth(HAIR)
            p = c.beginPath()
            for ring in [g.exterior] + list(g.interiors):
                pts = list(ring.coords)
                p.moveTo(*self.S(pts[0][0], pts[0][1], z1))
                for q in pts[1:]:
                    p.lineTo(*self.S(q[0], q[1], z1))
                p.close()
            c.drawPath(p, stroke=1, fill=1, fillMode=0)
            c.restoreState()

    def depth_key(self, geom, z):
        cp = geom.centroid
        return self.rot(cp.x, cp.y, z)[2]


# ------------------------------------------------------------------ v137 (Rytis 2026-10-12): CAD žymėjimai
# „žymėjimai lipa ant projekcijų, pjūvio linijos ir žymėjimai sugrūsti ant projekcijos, nuorodos linijos kertasi":
#  - pjūvio plokštuma (ISO 128-40 / 128-44): per vaizdą NEBRAIŽOMA; tik storos trumpos atkarpos UŽ vaizdo ribų,
#    rodyklės žiūrėjimo kryptimi ir raidės prie rodyklių (už vaizdo);
#  - balionai / žymos - STULPELYJE UŽ vaizdo (ir už matmenų), surikiuoti pagal taikinio y (išvadinės nesikerta),
#    tarpas >= 2 r + 3; ant projekcijos - tik išvadinės taškas.
def cut_plane(x, y0, y1, letter, look="right", size=10):
    """vertikali pjūvio plokštuma x per vaizdą y0..y1 (y žemyn): atkarpos virš / po vaizdu, rodyklės `look` kryptimi"""
    sg = 1 if look == "right" else -1
    for ya, yb in ((y0 - 16, y0 - 5), (y1 + 5, y1 + 16)):
        line(x, ya, x, yb, 0.8)
        ye = ya if ya < y0 else yb
        line(x, ye, x + sg * 9, ye, 0.3)
        arrowhead(x + sg * 9, ye, 0 if sg > 0 else 180)
        T(x + sg * 13, ye + size * 0.35, letter, size, font="FB", align="l" if sg > 0 else "r")


def cut_plane_h(y, x0, x1, letter, look="down", size=10):
    """horizontali pjūvio plokštuma y per vaizdą x0..x1"""
    sg = 1 if look == "down" else -1
    for xa, xb in ((x0 - 16, x0 - 5), (x1 + 5, x1 + 16)):
        line(xa, y, xb, y, 0.8)
        xe = xa if xa < x0 else xb
        line(xe, y, xe, y + sg * 9, 0.3)
        arrowhead(xe, y + sg * 9, -90 if sg > 0 else 90)
        T(xe, y + sg * 9 + (size if sg > 0 else -3), letter, size, font="FB", align="c")


def _column_ys(ty, want, ymin=None, ymax=None, gap=16):
    """balionų y stulpelyje: kuo arčiau norimo (want), ne arčiau nei gap; tvarka - pagal taikinio y (nesikerta)"""
    order = sorted(range(len(ty)), key=lambda i: ty[i])
    ys = [want[i] for i in order]
    for k in range(1, len(ys)):
        ys[k] = max(ys[k], ys[k - 1] + gap)
    if ymax is not None and ys and ys[-1] > ymax:
        ys[-1] = ymax
        for k in range(len(ys) - 2, -1, -1):
            ys[k] = min(ys[k], ys[k + 1] - gap)
    if ymin is not None and ys and ys[0] < ymin:
        d = ymin - ys[0]; ys = [v + d for v in ys]
    if ymin is not None and ymax is not None and ys and ys[-1] > ymax:       # netelpa - tolygiai intervale
        n = len(ys)
        ys = [ymin + (ymax - ymin) * (k / (n - 1) if n > 1 else 0.5) for k in range(n)]
    out = [0] * len(ty)
    for k, i in enumerate(order):
        out[i] = ys[k]
    return out


# v138 (Rytis 2026-10-12: „nuorodinės skaičių linijos ... dabar labai maišosi su matmenų linijomis"): išvadinės - ĮSTRIŽOS
# (ISO 128-22: ne lygiagrečios matmenų linijoms), nuolydis ~30-40° nuo horizontalės; balionas - stulpelyje už vaizdo.
LEADER_SLOPE = 0.65
LEADER_DY_MAX = 42.0


def _want(items, x_col, up, slope):
    w = []
    for tx, ty, _ in items:
        dy = min(LEADER_DY_MAX, max(14.0, slope * abs(x_col - tx)))
        w.append(ty - dy if up else ty + dy)
    return w


def balloon_column(items, x_col, r=6.5, ymin=None, ymax=None, gap=None, up=True, slope=None):
    """items: [(tx, ty, label)] - balionai stulpelyje x_col (už vaizdo), įstrižos išvadinės, nesikerta"""
    if not items:
        return
    gap = gap or 2 * r + 3
    ys = _column_ys([it[1] for it in items], _want(items, x_col, up, slope or LEADER_SLOPE), ymin, ymax, gap)
    for (tx, ty, lab), yb in zip(items, ys):
        if abs(yb - ty) < 10:                                       # niekada horizontali
            yb = ty - 10 if yb <= ty else ty + 10
        leader(tx, ty, x_col, yb, lab, r)


def tag_column(items, x_col, size=8, ymin=None, ymax=None, gap=None, align=None, up=True, slope=None):
    """items: [(tx, ty, text)] - žymos su tekstu stulpelyje x_col (už vaizdo), įstrižos išvadinės"""
    if not items:
        return
    gap = gap or size + 5
    ys = _column_ys([it[1] for it in items], _want(items, x_col, up, slope or LEADER_SLOPE), ymin, ymax, gap)
    for (tx, ty, txt), yb in zip(items, ys):
        al = align or ("l" if x_col > tx else "r")
        tag(tx, ty, x_col, yb, txt, size=size, align=al)


# v139 (Rytis 2026-10-12: „skaičių nuorodų linijos labai chaotiškai žiūrisi, sunku suprasti kur ir kas - optimalesnis sprendimas";
# „vizualinė dalis gamyboje labai svarbi - gamybininkas pirmiausiai skaito vizualinę informaciją"):
# BALIONAI ŠALIA DETALĖS, VISOS IŠVADINĖS VIENO VAIZDO PUSĖJE - LYGIAGREČIOS 45°: balionas už vaizdo krašto (edge + d) ant 45° linijos
# iš taikinio; persidengiantis - stumiamas toliau TOJE PAČIOJE linijoje (lygiagretumas išlieka, linijos nesikerta).
def balloon_side(items, edge, side="right", up=True, d=16, r=6.5, gap=None, tags=False, size=8):
    """items: [(tx, ty, label)]; edge - vaizdo (su matmenimis) kraštas x; side 'right'/'left'; up - linijos kryptis"""
    if AUTO.get("mode"):                                     # v139: automatinis žymėjimas
        for tx, ty, lab in items:
            balloon_auto(tx, ty, lab, r=r, region=AUTO.get("region"), kind="tag" if tags else "balloon", size=size)
        return
    sx = 1 if side == "right" else -1
    sy = -1 if up else 1
    gap = gap or (2 * r + 3 if not tags else size + 6)
    placed = []
    order = sorted(items, key=lambda it: sx * (edge - it[0]))
    for tx, ty, lab in order:
        bx = edge + sx * d
        t = abs(bx - tx)
        by = ty + sy * t
        def clash(x_, y_):
            for px, py, w_ in placed:
                if abs(y_ - py) < gap and abs(x_ - px) < (w_ if tags else 2 * r + 3):
                    return True
            return False
        k = 0
        while clash(bx, by) and k < 40:
            bx += sx * gap * 0.75; by += sy * gap * 0.75; k += 1
        if tags:
            w_ = pdfmetrics.stringWidth(str(lab), "F", size) + 8
            tag(tx, ty, bx, by, lab, size=size, align="l" if sx > 0 else "r")
            placed.append((bx + sx * w_ / 2, by, w_))
        else:
            leader(tx, ty, bx, by, lab, r)
            placed.append((bx, by, 0))


# ------------------------------------------------------------------ v139: AUTOMATINIS ŽYMĖJIMAS (2 praėjimai)
# Rytis 2026-10-12: „skaičių nuorodų linijos labai chaotiškai žiūrisi ... reikia optimalesnio sprendimo; vizualinė dalis
# gamyboje labai svarbi - gamybininkas pirmiausiai skaito vizualinę informaciją". Sprendimas: lapas braižomas 2 kartus.
# 1 praėjimas - be balionų (užklausos surenkamos), PDF -> rastras (užimtumo kaukė); kiekvienam balionui ieškoma ARTIMIAUSIOS
# laisvos vietos ŠALIA detalės: trumpa ĮSTRIŽA išvadinė (30-60°, ne lygiagreti matmenims), balionas visas baltame plote,
# išvadinė kuo mažiau kerta brėžinio linijų ir nekerta kitų išvadinių; 2 praėjimas - piešiama su rastomis vietomis.
AUTO = {"mode": None, "reqs": [], "place": [], "i": 0}
TEXT_BOXES = []                                         # v172: (puslapis, x0, y0, x1, y1) - jau parašyti tekstai


def text_free(x0, y0, x1, y1, pad=2.0):
    """v172: sritis nesikerta su jau parašytais to paties puslapio tekstais"""
    pn = c.getPageNumber()
    return all(p_ != pn or x1 + pad <= a or x0 - pad >= b_ or y1 + pad <= b or y0 - pad >= d
               for p_, a, b, b_, d in TEXT_BOXES)


def auto_begin(mode, placements=None):
    AUTO["mode"] = mode; AUTO["i"] = 0
    if mode == "collect":
        AUTO["reqs"] = []
    else:
        AUTO["place"] = placements or []


def balloon_auto(tx, ty, label, r=6.5, region=None, kind="balloon", size=8, prefer=None, avoid=None):
    """balionas (kind='balloon') arba žyma su tekstu (kind='tag') - vieta parenkama automatiškai (auto_begin).
    v172: avoid - [(x0, y0, x1, y1)] sritys (vaizdo objektas), kuriose balionas NEDEDAMAS (ne ant fono / raidžių)."""
    if AUTO["mode"] == "collect":
        AUTO["reqs"].append(dict(tx=tx, ty=ty, label=str(label), r=r, region=region, kind=kind, size=size, prefer=prefer,
                                 avoid=avoid))
        return
    if AUTO["mode"] == "draw" and AUTO["i"] < len(AUTO["place"]):
        bx, by = AUTO["place"][AUTO["i"]]; AUTO["i"] += 1
        if kind == "tag":
            tag(tx, ty, bx, by, label, size=size, align="l" if bx >= tx else "r")
        else:
            leader(tx, ty, bx, by, label, r)
        return
    leader(tx, ty, tx + 20, ty - 20, label, r)                # atsarginis


def auto_place(pdf_path, page=0, zoom=2.0):
    """1 praėjimo PDF -> balionų vietos [(bx, by)] AUTO['reqs'] tvarka"""
    import numpy as np
    doc = fitz.open(pdf_path)
    pix = doc[page].get_pixmap(matrix=fitz.Matrix(zoom, zoom), colorspace=fitz.csGRAY)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
    ink = img < 250                                            # ir šviesūs užpildai (stiklas) - užimta
    Hh, Ww = ink.shape
    def px(x, y):
        return int(round(x * zoom)), int(round(y * zoom))
    def box_free(x0, y0, x1, y1):
        a0, b0 = px(x0, y0); a1, b1 = px(x1, y1)
        if a0 < 0 or b0 < 0 or a1 >= Ww or b1 >= Hh:
            return False
        return not ink[b0:b1 + 1, a0:a1 + 1].any()
    def circ_free(cx, cy, rr):
        a0, b0 = px(cx - rr, cy - rr); a1, b1 = px(cx + rr, cy + rr)
        if a0 < 0 or b0 < 0 or a1 >= Ww or b1 >= Hh:
            return False
        sub = ink[b0:b1 + 1, a0:a1 + 1]
        yy, xx = np.mgrid[b0:b1 + 1, a0:a1 + 1]
        m = (xx - cx * zoom) ** 2 + (yy - cy * zoom) ** 2 <= (rr * zoom) ** 2
        return not (sub & m).any()
    def crossings(x0, y0, x1, y1, skip=5.0):
        L = math.hypot(x1 - x0, y1 - y0)
        if L <= skip:
            return 0
        n = int(L * zoom)
        cnt, prev = 0, False
        for k in range(n):
            t = k / n
            d = t * L
            if d < skip:
                continue
            a, b = px(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t)
            if 0 <= a < Ww and 0 <= b < Hh:
                cur = bool(ink[b, a])
                if cur and not prev:
                    cnt += 1
                prev = cur
        return cnt
    def seg_x(p1, p2, p3, p4):
        def ccw(a, b, c):
            return (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])
        return ccw(p1, p3, p4) != ccw(p2, p3, p4) and ccw(p1, p2, p3) != ccw(p1, p2, p4)
    def paint_circle(cx, cy, rr):
        a0, b0 = px(cx - rr, cy - rr); a1, b1 = px(cx + rr, cy + rr)
        a0, b0 = max(a0, 0), max(b0, 0)
        yy, xx = np.mgrid[b0:b1 + 1, a0:a1 + 1]
        m = (xx - cx * zoom) ** 2 + (yy - cy * zoom) ** 2 <= (rr * zoom) ** 2
        ink[b0:b1 + 1, a0:a1 + 1] |= m
    def paint_box(x0, y0, x1, y1):
        a0, b0 = px(x0, y0); a1, b1 = px(x1, y1)
        ink[max(b0, 0):b1 + 1, max(a0, 0):a1 + 1] = True
    def paint_seg(x0, y0, x1, y1):
        L = math.hypot(x1 - x0, y1 - y0); n = max(2, int(L * zoom))
        for k in range(n + 1):
            a, b = px(x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n)
            if 0 <= a < Ww and 0 <= b < Hh:
                ink[max(b - 1, 0):b + 2, max(a - 1, 0):a + 2] = True
    angs = [45, 135, 225, 315, 30, 150, 210, 330, 60, 120, 240, 300]
    rads = [14, 18, 23, 29, 36, 44, 54, 66, 80, 96, 115, 135, 160, 190]       # v172: toliau - už vaizdo ribų
    segs, out = [], []
    for q in AUTO["reqs"]:
        tx, ty, rr = q["tx"], q["ty"], q["r"] + 1.5
        reg = q["region"] or (IX0 + 2, IY0 + 2, IX1 - 2, BAND_Y - 2)
        best = None
        for R in rads:
            for k_, a in enumerate(angs):
                if q["prefer"] and not any(abs(((a - p_ + 180) % 360) - 180) <= 50 for p_ in q["prefer"]):
                    continue
                ca, sa = math.cos(math.radians(a)), -math.sin(math.radians(a))
                bx, by = tx + R * ca, ty + R * sa
                if q["kind"] == "tag":
                    w_ = pdfmetrics.stringWidth(q["label"], "F", q["size"]) + 4
                    right = ca >= 0
                    x0b, x1b = (bx + 1, bx + w_ + 2) if right else (bx - w_ - 2, bx - 1)
                    y0b, y1b = by - q["size"] * 0.8, by + q["size"] * 0.3
                    if not (reg[0] <= x0b and x1b <= reg[2] and reg[1] <= y0b and y1b <= reg[3]):
                        continue
                    free = box_free(x0b - 1, y0b - 1, x1b + 1, y1b + 1)
                    ex, ey = bx, by
                else:
                    if not (reg[0] + rr <= bx <= reg[2] - rr and reg[1] + rr <= by <= reg[3] - rr):
                        continue
                    free = circ_free(bx, by, rr + 1.5)
                    if free and q.get("avoid"):
                        free = not any(a0 - rr - 4 < bx < a1 + rr + 4 and b0 - rr - 4 < by < b1 + rr + 4
                                       for a0, b0, a1, b1 in q["avoid"])
                    ex, ey = bx - ca * rr, by - sa * rr
                if not free:
                    continue
                cr = crossings(tx, ty, ex, ey)
                lx = sum(1 for s_ in segs if seg_x((tx, ty), (ex, ey), s_[0], s_[1]))
                score = R + 40 * cr + 200 * lx + k_ * 0.6        # v172: kiekvienas kirtimas brangesnis už atstumą
                if best is None or score < best[0]:
                    best = (score, bx, by, ex, ey, x0b if q["kind"] == "tag" else None,
                            (x1b, y0b, y1b) if q["kind"] == "tag" else None)
            if best is not None and best[0] < R + 4:              # tobulas (be kirtimų) - toliau neieškoti
                break
        if best is None:
            bx, by = tx + 24, ty - 24; ex, ey = bx, by
        else:
            _, bx, by, ex, ey, x0b, rest = best
        out.append((bx, by))
        segs.append(((tx, ty), (ex, ey)))
        paint_seg(tx, ty, ex, ey)
        if q["kind"] == "tag" and best is not None and rest:
            paint_box(x0b - 2, rest[1] - 2, rest[0] + 2, rest[2] + 2)
        else:
            paint_circle(bx, by, rr + 3)
    doc.close()
    return out


# ------------------------------------------------------------------ v20: PDF -> CorelDRAW (tekstas lieka tekstu)
def pdf_fix_fonts(path_in, path_out=None):
    """Rytis 2026-10-08 (patikrinta CorelDRAW 2026): atidarant PDF su CorelDRAW tekstas turi likti TEKSTU ir
    neišsikraipyti. GOST Common šrifto PostScript vardas faile yra su tarpu („GOST Common"); reportlab / macOS PDF'e
    rašo „GOST-Common", Corel tai skaito kaip šeimą „GOST" + stilių „Common", neranda ir keičia Helvetica
    (išsibarsčiusios raidės). Pataisa: BaseFont / FontName = /GOST#20Common (be subset žymos) + FontFamily.
    Kompiuteryje turi būti įdiegtas GOST Common (assets/gost_common.ttf)."""
    import os as _os
    import pymupdf as _f
    d = _f.open(path_in)
    n = 0
    for xr in range(1, d.xref_length()):
        for key in ("BaseFont", "FontName"):
            try:
                t = d.xref_get_key(xr, key)
            except Exception:
                continue
            if t[0] == "name" and ("GOST-Common" in t[1] or "GOSTCommon" in t[1] or ("GOST" in t[1] and "Common" in t[1]
                                                                                        and t[1] != "/GOST#20Common")):
                d.xref_set_key(xr, key, "/GOST#20Common"); n += 1
                if key == "FontName":
                    d.xref_set_key(xr, "FontFamily", "(GOST Common)")
    out = path_out or path_in
    tmp = out + ".fix.pdf"
    d.save(tmp, garbage=3, deflate=True); d.close()
    _os.replace(tmp, out)
    return n


def dugnas_inset(geom, inset, blunt_len=12.0, mitre_limit=10):
    """v108 (Rytis 2026-10-12): P6 DUGNAS = raidės kontūras -inset mm į vidų (mitre - statūs kampai lieka statūs).
    Smailus raidės VIDINIS kampas (tuštumos įlinkis, pvz. M viršuje tarp kojelės ir įstrižainės) mitre būdu duoda
    ilgą siaurą įpjovą į dugną. Jei įpjovos smaigalys toliau nei `blunt_len` mm nuo stiklo viršūnės (siaura vieta,
    ~11 mm ir trumpesnės - paliekamos, pvz. M vidurio V), įpjova nukertama statmenai pusiaukampinei `inset` mm už
    stiklo viršūnės: vienas taškas -> DU, du buki kampai vietoj smailaus. Etalonas - Mraides_pataisymai.pdf (Joker MAN-FRE)."""
    import math as _m
    from shapely.geometry import Point as _Pt, Polygon as _Pg
    from shapely.ops import unary_union as _uu
    M_ = geom.buffer(-inset, join_style=2, mitre_limit=mitre_limit)
    fills = []
    for pl in getattr(geom, "geoms", [geom]):
        for ring in [pl.exterior] + list(pl.interiors):
            c = list(ring.coords)[:-1]
            n = len(c)
            for i in range(n):
                p0, p1, p2 = c[i - 1], c[i], c[(i + 1) % n]
                e1 = (p0[0] - p1[0], p0[1] - p1[1]); e2 = (p2[0] - p1[0], p2[1] - p1[1])
                l1, l2 = _m.hypot(*e1), _m.hypot(*e2)
                if l1 < 1e-6 or l2 < 1e-6:
                    continue
                e1 = (e1[0] / l1, e1[1] / l1); e2 = (e2[0] / l2, e2[1] / l2)
                ang = _m.degrees(_m.acos(max(-1.0, min(1.0, e1[0] * e2[0] + e1[1] * e2[1]))))
                if ang < 1 or ang >= 90:
                    continue
                tip = inset / _m.sin(_m.radians(ang) / 2)        # mitre smaigalio atstumas nuo stiklo viršūnės
                if tip <= blunt_len:
                    continue
                gx, gy = e1[0] + e2[0], e1[1] + e2[1]; gl = _m.hypot(gx, gy)
                g = (gx / gl, gy / gl)                            # pusiaukampinė į smailų tarpą
                eps = min(0.05, 0.2 * min(l1, l2))
                if geom.contains(_Pt(p1[0] + g[0] * eps, p1[1] + g[1] * eps)) or \
                        not geom.contains(_Pt(p1[0] - g[0] * eps, p1[1] - g[1] * eps)):
                    continue                                      # tik tuštumos įlinkis (ne raidės smaigalys)
                u = (-g[0], -g[1])                                # į medžiagą
                pts = []
                for e in (e1, e2):
                    nx, ny = -e[1], e[0]
                    if nx * u[0] + ny * u[1] < 0:
                        nx, ny = -nx, -ny
                    t = (inset - inset * (nx * u[0] + ny * u[1])) / (e[0] * u[0] + e[1] * u[1])
                    pts.append((p1[0] + inset * nx + t * e[0], p1[1] + inset * ny + t * e[1]))
                T = (p1[0] + u[0] * (tip + 0.5), p1[1] + u[1] * (tip + 0.5))
                fills.append(_Pg([pts[0], T, pts[1]]).buffer(0))
    if not fills:
        return M_
    return _uu([M_] + fills).buffer(0).simplify(0.005)


def pdf_text_to_paths(fn):
    """v157: tekstas -> kreivės savo moduliu pdf_outline (keičia TIK teksto operatorius; spalvos / ICC / overprint /
    skaidrumas - baitas į baitą). Ghostscript NENAUDOTI - v156 perrašė ICC, išmetė OP / OPM -> pasikeitė kliento spalvos."""
    import pdf_outline
    st = pdf_outline.outline(fn)
    if st["kept"] or st["missing"]:
        print("pdf_text_to_paths: liko tekstas", st)
    return st



def pdf_explicit_colors(fn):
    """v166 (Rytis 2026-10-13: „atidarius su CorelDRAW vaizdas kardinaliai skiriasi, fonas mėlynas ir tekstas ne toks"):
    kliento PDF (CorelDRAW / Illustrator eksportas) spot spalvas nustato tik `/CSn cs` - be `scn`, nes PDF standartu pradinis
    atspalvis = 1.0. Acrobat / Preview / MuPDF tai daro, CorelDRAW importas - NE (palieka ankstesnę spalvą: baltas RAL 9016
    fonas -> mėlynas, mėlyni užrašai -> balti). Čia po KIEKVIENO `cs` / `CS` įrašoma aiški pradinė spalva (Separation 1,
    DeviceN 1..1, ICCBased / Lab / Cal 0..0, Indexed 0) - tai, ką standartas ir taip numato, todėl atvaizdas nepasikeičia.
    Keičiami TIK turinio srautai (puslapio + Form XObject), kiti objektai (ICC, spalvų erdvės, OP, paveikslėliai) neliečiami."""
    import re
    doc = fitz.open(fn)

    def cs_init(doc, page_or_xref, csname):
        # surasti /ColorSpace /csname aprašą
        t, v = doc.xref_get_key(page_or_xref, f"Resources/ColorSpace/{csname}")
        if t == "null":
            return None
        obj = doc.xref_object(int(v.split()[0])) if t == "xref" else v
        if "/Pattern" in obj and "/Separation" not in obj and "/DeviceN" not in obj:
            return None
        if "/Separation" in obj:
            return "1"
        if "/DeviceN" in obj:
            m = re.search(r"/DeviceN\s*\[([^\]]*)\]", obj)
            n = len(re.findall(r"/[^\s/\[\]]+", m.group(1))) if m else 1
            return " ".join(["1"] * n)
        if "/Indexed" in obj:
            return "0"
        if "/ICCBased" in obj:
            m = re.search(r"/ICCBased\s+(\d+)\s+0\s+R", obj)
            n = int(doc.xref_get_key(int(m.group(1)), "N")[1]) if m else 4
            return " ".join(["0"] * n)
        if "/Lab" in obj or "/CalRGB" in obj:
            return "0 0 0"
        if "/CalGray" in obj:
            return "0"
        return None

    pat = re.compile(rb"(/([A-Za-z0-9_.#+-]+)\s+(cs|CS))(?=[\s/\[(<]|$)")

    def patch(owner_xref, content_xrefs):
        n = 0
        for cx in content_xrefs:
            s = doc.xref_stream(cx)
            out, last = [], 0
            for m in pat.finditer(s):
                nm, op = m.group(2).decode(), m.group(3)
                if nm in ("DeviceGray", "DeviceRGB", "DeviceCMYK", "Pattern"):
                    init = {"DeviceGray": "0", "DeviceRGB": "0 0 0", "DeviceCMYK": "0 0 0 1"}.get(nm)
                else:
                    init = cs_init(doc, owner_xref, nm)
                if not init:
                    continue
                out.append(s[last:m.end()])
                out.append((" " + init + (" scn" if op == b"cs" else " SCN")).encode())
                last = m.end(); n += 1
            if n:
                out.append(s[last:])
                doc.update_stream(cx, b"".join(out))
        return n

    total = 0
    seen = set()

    def forms_of(owner):                                     # v182: ir įdėtinės formos (forma formoje - gradientai, grupės)
        t, v = doc.xref_get_key(owner, "Resources/XObject")
        if t != "dict":
            return []
        return [int(x) for x in re.findall(r"(\d+)\s+0\s+R", v)]

    def walk(xr):
        nonlocal total
        if xr in seen or doc.xref_get_key(xr, "Subtype")[1] != "/Form":
            return
        seen.add(xr)
        total += patch(xr, [xr])
        for y in forms_of(xr):
            walk(y)
    for page in doc:
        total += patch(page.xref, page.get_contents())
        for x in page.get_xobjects():
            walk(x[0])
        for y in forms_of(page.xref):
            walk(y)
    if total:
        doc.save(fn, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
    return total


def pdf_drop_unused_fonts(fn):
    """v182 (v171 taisyklė: puslapyje tik GOST Common; Type0 šriftai - CorelDRAW „corrupted file"): kliento fragmente po
    redakcijos lieka TUŠTI teksto blokai (`BT /F51 9 Tf ... ET` be Tj / TJ) ir įterpti kliento šriftai (Gotham, Arial).
    Jei turinio srautuose NĖRA nė vieno teksto rodymo operatoriaus - `Tf` operatoriai ir /Font resursai pašalinami
    (baitų lygiu, kita grafika nepaliečiama). Yra gyvas tekstas - nieko nedaroma, grąžina False."""
    import re
    doc = fitz.open(fn)
    streams = []
    for page in doc:
        streams += [(page.xref, x) for x in page.get_contents()]
        for x in page.get_xobjects():
            if doc.xref_get_key(x[0], "Subtype")[1] == "/Form":
                streams.append((x[0], x[0]))
    show = re.compile(rb"(\)|>|\])\s*(Tj|TJ|'|\")(?=[\s/\[(<]|$)")
    for _, sx in streams:
        if show.search(doc.xref_stream(sx)):
            return False
    tf = re.compile(rb"/[A-Za-z0-9_.#+-]+\s+-?[\d.]+\s+Tf(?=[\s/\[(<]|$)")
    for owner, sx in streams:
        s = doc.xref_stream(sx)
        s2 = tf.sub(b"", s)
        if s2 != s:
            doc.update_stream(sx, s2)
        if doc.xref_get_key(owner, "Resources/Font")[0] != "null":
            doc.xref_set_key(owner, "Resources/Font", "null")
    doc.save(fn, incremental=True, encryption=fitz.PDF_ENCRYPT_KEEP)
    return True
