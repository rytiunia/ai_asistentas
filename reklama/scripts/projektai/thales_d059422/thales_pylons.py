"""Thales Campus Velizy (CEOS D059422) - pilonų gamybinis komplektas.
Principas (Rytis 2026-10-10):
 - rėmas Al 60x60x3: plotis / aukštis = skarda - 6 (po 3: 2 mm skarda + 1 mm laisvumas)
 - mėlyna skarda (lovelė) 2 mm RAL 5022: šonai + viršus lankstomi 40; apačioje kraštinė išpjauta ties kojomis,
   tarp kojų tik 20 mm standumo briauna
 - prie mėlynos skardos kniedijamas L 25x25x2; prie L su įleidžiamais (csk) varžtais prisukama balta skarda
 - balta skarda 2 mm RAL 9016: šonai + apačia 30, viršus apverstas L 70, ausės 70x30
 - visas segmentas (mėlyna + balta) prisukamas csk varžtais per mėlynos šonų / viršaus atlankus prie rėmo
 - įėjimo pilonas: kairė koja +60 (nuolydis), flanšai 300x300 ant esamų inkarų (ašys 1000)
 - pastatų pilonai: vienpusiai, integruota pagrindo plokštė."""
import sys, os, math, tempfile, re, io
SK = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))   # skill scripts/
sys.path.insert(0, SK)
import lapas_core as K
from lapas_core import T, line, rect, poly, hdim, vchain, hchain, leader, view_title, balloon, MM, tag
import r3d
import pymupdf as fitz
from reportlab.lib.colors import HexColor, white, black, Color
from reportlab.lib.utils import ImageReader

K.RAL.setdefault("5022", "#222D5A"); K.RAL.setdefault("5012", "#3B83BD")
CLIENT, PROJECT, DRAWING_NO, DATE, REV = "CEOS Groupe", "Thales Campus Velizy", "CEOS D059422", "2026-10-13", "D"
SRC = os.environ.get("THALES_SRC", "APS_Communication_-_Thales_Campus_v5_phase_2.pdf")   # kliento PDF (CEOS D059422)
OUT = os.environ.get("THALES_OUT", "out"); os.makedirs(OUT, exist_ok=True)
BLUE, WHITE_ = HexColor("#2B2B5C"), HexColor("#F4FBF7")   # v163: kliento lapo RAL 5022 / RAL 9016 pavyzdžių spalvos
                                                             # (CEOS D059422 p.2 / p.9 legenda; buvo #222D5A / #F1F0EA)
AL, LCOL, GREYF, DECAL = HexColor("#C9CCCF"), HexColor("#8C8C8C"), HexColor("#9A9A9A"), HexColor("#CFE3F2")
RED, SCREW = HexColor("#C00000"), HexColor("#E2001A")
t, FR, FT, CL = 2, 60, 3, 3
TB, TW, PL, LP, LT = 40, 30, 200, 25, 2
RIB, NOTCH = 20, 3 + 60 + 2              # standumo briauna 20; išpjova ties koja 65 nuo krašto
HO_W, HO_B = 17, 25                      # varžtų ašis: balta 17 nuo balto priekio lenkimo; mėlyna 25 nuo mėlyno priekio lenkimo
EAR = 70
DIM = K.F_DIM_MAIN                        # rev C (Rytis 2026-10-13): VISI matmenys vieno dydžio - 12 pt (stilius.md v145)
SHEETS = []


class Pyl:
    def __init__(s, key, W, H, sides, legs, qty, title):
        s.key, s.W, s.H, s.sides, s.legs, s.qty, s.title = key, W, H, sides, legs, qty, title
        s.short = ("Entrance pylon" if legs == "ext" else "Building pylon") + f" {W}x{H}"
        s.HB = H - 30; s.OVH = H - PL; s.BODY = 2 * TB; s.D = s.BODY + TW * sides
        s.FX0, s.FX1 = CL, W - CL; s.FW = W - 2 * CL
        s.FY1 = s.HB - CL
        s.HL = s.FW - 2 * FR
        s.LONG = 60                            # ext: kairė koja +60 (nuolydis); int: abi kojos 60 po grindiniu
        s.LONG_R = 0
        if legs != "ext":
            s.LONG = 0                         # int: plokštė iškart po korpusu, ant žemės
        s.rib = RIB if legs == "ext" else 0    # int: mėlyna apačioje be lenkimo (dengia plokštę)
        s.BP = (600, 300, 10)                  # int: pagrindo plokštė Alu 10 (Rytis 2026-10-11)
        s.BPH = (500, 220, 14)                 # skylės 500 x 220, D14, 4 vnt. (M12 chem.)
        s.RAILS = [CL, (CL + s.FY1 - FR) / 2, s.FY1 - FR]       # Rytis 2026-10-11: tik 1 tarpinis skersinis (centre)
        s.BG = 0; s.PLC = GREYF
        if legs != "ext":                      # Rytis 2026-10-11: apatinis skersinis guli ant plokštės, privirintas;
            s.BM = (s.FW, 80, 40, 4)           # Rytis 2026-10-11: apačioje balkis Alu 80x40x4, rėmas ankeruojamas per jį
            s.RAILS = [(40 + s.FY1 - FR) / 2, s.FY1 - FR]
            s.BG = 5; s.PLC = BLUE
            L_ = s.FW; s.BH = [(95, 20), (225, -20), (L_ - 225, 20), (L_ - 95, -20)]   # šachmatine tvarka (x nuo balkio galo, z)
        s.V0L, s.V0R = (-s.LONG, -s.LONG_R) if legs == "ext" else (40, 40)
        s.VR_L, s.VR_R = s.FY1 - s.V0L, s.FY1 - s.V0R
        s.LV = s.OVH - 40                     # L vertikalė (205 .. HB-5)
        s.LH = W - 2 * 4 - 2 * LP
        s.FL, s.FLT, s.FAX = 300, 20, 25          # ext: flanšai Alu 20 (Rytis 2026-10-11)

    # varžtų vietos (mm)
    def pitch(s, L, p=300, e=50):
        n = max(1, round((L - 2 * e) / p)); return n, (L - 2 * e) / n, [e + i * (L - 2 * e) / n for i in range(n + 1)]

    def w_side_holes(s):                      # balta šoninis atlankas: y nuo PL
        return s.pitch(s.OVH - 30, 300, 50)
    def w_bot_holes(s):
        return s.pitch(s.W, 300, 50)
    def b_side_holes(s):                      # mėlyna šoninis atlankas -> rėmo vertikalė
        return s.pitch(s.HB, 400, 100)
    def b_top_holes(s):                       # mėlyna viršus -> viršutinis skersinis
        return s.pitch(s.W, 400, 100)
    def rivets_v(s):
        return s.pitch(s.LV, 300, 30)


# ======================================================================== bendri
def begin(code, n_rows):
    global VY1, VX0, VY0, VX1
    K.set_band(n_rows); VX0, VY0, VX1 = K.IX0 + 8, K.IY0 + 6, K.IX1 - 8; VY1 = K.VIEW_BOT - 4
    K.init(tempfile.mktemp(suffix=".pdf"), code); K.frame()


def band(title, sheet, sec_title, sec, rows, md, scales, mdw=200):
    BY0 = K.BAND_Y; BH = K.IY1 - BY0
    W_P6, W_MD, W_TB = 214, mdw, 272
    X_P6 = K.IX0; X_TB = K.IX1 - W_TB; X_MD = X_TB - W_MD; X_BOM = X_P6 + W_P6; W_BOM = X_MD - X_BOM
    K.header(X_P6, BY0, W_P6, sec_title); rect(X_P6, BY0 + 12, W_P6, BH - 12, lw=0.6); sec(X_P6, BY0 + 12, W_P6, BH - 12)
    K.bom_table(X_BOM, BY0, W_BOM, BH, rows, title="BILL OF MATERIALS  (per 1 pcs.)")
    K.main_data(X_MD, BY0, W_MD, BH, md, lab_w=62)
    K.title_block(X_TB, W_TB, {"title": PROJECT + " - " + title, "sheet": sheet, "client": CLIENT, "drawing_no": DRAWING_NO,
                               "date": DATE, "rev": REV, "order_no": os.environ.get("THALES_ORDER", "ALT0000_00.00_RS"),
                               "revisions": [["D", "3D as client, RAL colours", DATE, ""]]}, scales)


def save(fn):
    K.save(fn); SHEETS.append(fn)


def client_paths(pno, clip, skip_big=0.5):
    p = fitz.open(SRC)[pno]; clip = fitz.Rect(clip); out = []
    # rev C: spalvoti stačiakampiai (ikonų fonai) - baltas stačiakampis JŲ VIDUJE yra grafika (kryžius), kitur - maskavimas
    _col = [d["rect"] for d in p.get_drawings() if d.get("fill") and min(d["fill"][:3]) < 0.8 and clip.intersects(d["rect"])
            and d["rect"].width * d["rect"].height < 0.05 * clip.width * clip.height]
    for d in p.get_drawings():
        r = d["rect"]
        if not clip.intersects(r) or r.width * r.height > skip_big * clip.width * clip.height:
            continue
        if r.width > 0.9 * clip.width and r.height > 0.03 * clip.height:
            continue
        f = d.get("fill"); s_ = d.get("color")
        if f is None and s_ is None:
            continue
        if f and min(f[:3]) > 0.9 and all(it[0] == "re" for it in d["items"]) and not any(c_.contains(r) for c_ in _col):
            # balti maskavimo kvadratai - ne grafika; rev C: smulkūs balti (kryžius žaliame kvadrate) - grafika, paliekami
            continue
        out.append((K.drawing_to_subpaths(d, lambda q: q), tuple(f[:3]) if f else None, tuple(s_[:3]) if (s_ and f is None) else None, d.get("width") or 0.3))
    return out


# rev C (Rytis 2026-10-13: "labai daug neatitikimų, tekstai su pakeitimais"): kliento grafika NEBEPERPIEŠIAMA kontūrais
#  (get_drawings praranda gyvą tekstą, paveikslėlius, gradientus, permatomumą) - dedamas TIKSLUS kliento PDF fragmentas
#  VEKTORIUMI (lapas_core.place_pdf), 2D ir 3D (afininė transformacija). Kliento matmenų linijos / užrašai (CMYK 0.8 0.4 0 0.2)
#  iš kopijos pašalinami prieš rastrą.
_CLEAN, _IMGS = None, {}
GUIDE = r"0\.8 0\.4 0 0\.2"


def clean_src():
    global _CLEAN
    if _CLEAN:
        return _CLEAN
    d = fitz.open(SRC)
    for pg in d:
        for xr in pg.get_contents():
            s0 = d.xref_stream(xr).decode("latin1")
            s1 = re.sub(r"(" + GUIDE + r" SCN\n(?:(?!S\n)[^\n]*\n){0,8}?)S\n", r"\1n\n", s0)          # linijos - nepiešiamos
            if s1 != s0:
                d.update_stream(xr, s1.encode("latin1"))
    _CLEAN = os.path.join(tempfile.gettempdir(), "thales_client_clean.pdf"); d.save(_CLEAN)
    return _CLEAN


_FRAG = {}
GUIDE_RGB = 0x1C6FA8                                   # kliento matmenų užrašų spalva (CMYK 0.8 0.4 0 0.2)


def clip_src(pno, clip):
    """v154 (Rytis 2026-10-13 "kodėl dokumente šriftas kitoks"): įdedamas fragmentas - ATSKIRAS 1 psl. PDF, kuriame
    lieka TIK matoma kliento grafika: visa, kas už iškarpos (kliento antraštės, užrašai Arial, kiti vaizdai) ir kliento
    matmenų užrašai fiziškai pašalinami (redakcija), ne tik paslepiami - CorelDRAW importuojant nerodo svetimo teksto."""
    key = (pno, tuple(round(v, 2) for v in clip))
    if key in _FRAG:
        return _FRAG[key]
    nd = fitz.open(); nd.insert_pdf(fitz.open(clean_src()), from_page=pno, to_page=pno)
    pg = nd[0]; c = fitz.Rect(clip); R = pg.rect
    for r in (fitz.Rect(R.x0, R.y0, R.x1, c.y0), fitz.Rect(R.x0, c.y1, R.x1, R.y1),
              fitz.Rect(R.x0, c.y0, c.x0, c.y1), fitz.Rect(c.x1, c.y0, R.x1, c.y1)):
        if r.width > 0.1 and r.height > 0.1:
            pg.add_redact_annot(r, fill=False)
    for b in pg.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            for sp in l["spans"]:
                if sp["color"] == GUIDE_RGB:
                    pg.add_redact_annot(fitz.Rect(sp["bbox"]), fill=False)
    pg.apply_redactions(images=fitz.PDF_REDACT_IMAGE_PIXELS, graphics=fitz.PDF_REDACT_LINE_ART_REMOVE_IF_COVERED,
                        text=fitz.PDF_REDACT_TEXT_REMOVE)
    fn = os.path.join(tempfile.gettempdir(), f"thales_frag_{pno}_{abs(hash(key)) % 10 ** 8}.pdf")
    nd.save(fn, garbage=3, deflate=True)
    K.pdf_explicit_colors(fn)                                # v166: CorelDRAW - spot spalvos su aiškiu atspalviu (žr. lapas_core)
    if nd[0].get_text().strip():                             # v162: tik jei fragmente LIKO gyvas tekstas (Thales - nėra,
        K.pdf_text_to_paths(fn)                              # kliento maketų tekstai jau kreivės) - kitaip failas neliečiamas
    _FRAG[key] = fn
    return fn


def inset(clip, d=0.6):
    c = fitz.Rect(clip)
    return (c.x0 + d, c.y0 + d, c.x1 - d, c.y1 - d)                                       # be kliento rėmelio linijos


def place_img(pno, clip, tl, tr, bl, ol=0.3):
    """kliento fragmentas VEKTORIUMI (K.place_pdf) į lygiagretainį (reportlab koord.)"""
    br = (tr[0] + bl[0] - tl[0], tr[1] + bl[1] - tl[1])                                   # po grafika - grynai balta
    K.c.saveState(); K.c.setFillColor(white); pth = K.c.beginPath(); pth.moveTo(*tl); pth.lineTo(*tr); pth.lineTo(*br)
    pth.lineTo(*bl); pth.close(); K.c.drawPath(pth, stroke=0, fill=1); K.c.restoreState()      # (kliento balti maskavimo kv.)
    K.place_pdf(clip_src(pno, inset(clip)), 0, inset(clip), tl, tr, bl, outline=ol)


def draw_client(pno, clip, x, y, w, h, mirror=False):
    tl, tr, bl = (x, K.Y(y)), (x + w, K.Y(y)), (x, K.Y(y + h))
    if mirror:
        tl, tr, bl = tr, tl, (x + w, K.Y(y + h))
    place_img(pno, clip, tl, tr, bl)


def cut(x, y, w, h, col):
    rect(x, y, w, h, fill=col, lw=0.3)


def csk_h(x, y, k, length, head="l"):
    """csk varžtas horizontaliai: x - galvutės plokštuma; y - ašis; k pt/mm"""
    if head == "l":
        poly([(x, y - 3.8 * k), (x + 2 * k, y - 1.6 * k), (x + 2 * k, y + 1.6 * k), (x, y + 3.8 * k)], fill=SCREW, lw=0.2)
        rect(x + 2 * k, y - 1.6 * k, (length - 2) * k, 3.2 * k, fill=SCREW, lw=0.2)
    else:
        poly([(x, y - 3.8 * k), (x - 2 * k, y - 1.6 * k), (x - 2 * k, y + 1.6 * k), (x, y + 3.8 * k)], fill=SCREW, lw=0.2)
        rect(x - length * k, y - 1.6 * k, (length - 2) * k, 3.2 * k, fill=SCREW, lw=0.2)


def csk_v(x, y, k, length, head="t"):
    if head == "t":
        poly([(x - 3.8 * k, y), (x - 1.6 * k, y + 2 * k), (x + 1.6 * k, y + 2 * k), (x + 3.8 * k, y)], fill=SCREW, lw=0.2)
        rect(x - 1.6 * k, y + 2 * k, 3.2 * k, (length - 2) * k, fill=SCREW, lw=0.2)
    else:
        poly([(x - 3.8 * k, y), (x - 1.6 * k, y - 2 * k), (x + 1.6 * k, y - 2 * k), (x + 3.8 * k, y)], fill=SCREW, lw=0.2)
        rect(x - 1.6 * k, y - length * k, 3.2 * k, (length - 2) * k, fill=SCREW, lw=0.2)


def rivet_v(x, y, k, length):
    rect(x - 1.2 * k, y, 2.4 * k, length * k, fill=HexColor("#555555"), lw=0.2)


# ======================================================================== 3D
def frame3d(S, p, cut_x=None):
    X = cut_x or p.W
    def B(o, u, v, w, c):
        S.box(o, u, v, w, c)
    B((p.FX0, p.V0L, -FR / 2), (FR, 0, 0), (0, p.VR_L, 0), (0, 0, FR), AL)
    if X >= p.W:
        B((p.FX1 - FR, p.V0R, -FR / 2), (FR, 0, 0), (0, p.VR_R, 0), (0, 0, FR), AL)
    for yy in p.RAILS:
        B((p.FX0 + FR, yy, -FR / 2), (min(p.HL, X - p.FX0 - FR), 0, 0), (0, FR, 0), (0, 0, FR), AL)
    if p.legs == "ext":
        for fx, fy in ((p.FAX, -p.LONG - p.FLT), (p.W - p.FAX, -p.FLT)):
            if fx < X:
                B((fx - p.FL / 2, fy, -p.FL / 2), (p.FL, 0, 0), (0, p.FLT, 0), (0, 0, p.FL), GREYF)
    else:
        B((p.FX0, 0, -40), (min(p.FW, X - p.FX0), 0, 0), (0, 40, 0), (0, 0, 80), AL)


def blue3d(S, p, sign, dz=0, X=None, Y0=0, Y1=None):
    X = X or p.W; Y1 = Y1 or p.HB
    zf = sign * TB + dz
    zp = zf - t if sign > 0 else zf
    S.box((0, Y0, zp), (X, 0, 0), (0, Y1 - Y0, 0), (0, 0, t), BLUE)                      # priekis
    z0 = dz if sign > 0 else zf
    S.box((0, Y0, z0), (t, 0, 0), (0, Y1 - Y0, 0), (0, 0, TB), BLUE)                    # kairys šonas 40
    if X >= p.W:
        S.box((p.W - t, Y0, z0), (t, 0, 0), (0, Y1 - Y0, 0), (0, 0, TB), BLUE)
    if Y1 >= p.HB:
        S.box((0, p.HB - t, z0), (X, 0, 0), (0, t, 0), (0, 0, TB), BLUE)                # viršus 40
    if Y0 <= 0 and p.rib > 0:
        zr = zf - p.rib if sign > 0 else zf
        S.box((NOTCH, 0, zr), (min(X, p.W - NOTCH) - NOTCH, 0, 0), (0, t, 0), (0, 0, p.rib), BLUE)   # briauna 20 tarp kojų


def L3d(S, p, sign, dz=0, X=None, Y0=0, Y1=None):
    X = X or p.W; Y1 = Y1 or p.HB
    zf = sign * TB + dz
    za = zf if sign > 0 else zf - LT
    zb = zf if sign > 0 else zf - LP
    y0, y1 = max(PL + 5, Y0), min(p.HB - 5, Y1)
    for x0 in ([4] + ([p.W - 4 - LP] if X >= p.W else [])):
        S.box((x0, y0, za), (LP, 0, 0), (0, y1 - y0, 0), (0, 0, LT), LCOL)
        xs = x0 if x0 < p.W / 2 else x0 + LP - LT
        S.box((xs, y0, zb), (LT, 0, 0), (0, y1 - y0, 0), (0, 0, LP), LCOL)
    if Y0 <= PL + 5:
        S.box((4 + LP, PL + 5, za), (min(p.LH, X - 4 - LP), 0, 0), (0, LP, 0), (0, 0, LT), LCOL)
        S.box((4 + LP, PL + 5, zb), (min(p.LH, X - 4 - LP), 0, 0), (0, LT, 0), (0, 0, LP), LCOL)
    if Y1 >= p.HB:                                                                       # kampiniai L ant mėlyno viršaus
        zc = (5 if sign > 0 else -5 - 30) + dz
        for x0 in ([4] + ([p.W - 4 - LT] if X >= p.W else [])):
            S.box((x0, p.HB, zc), (LT, 0, 0), (0, LP, 0), (0, 0, 30), LCOL)
            S.box((x0 if x0 < p.W / 2 else x0 - LP + LT, p.HB, zc), (LP, 0, 0), (0, LT, 0), (0, 0, 30), LCOL)


def white3d(S, p, sign, dz=0, X=None, Y0=None, Y1=None):
    X = X or p.W; Y0 = max(Y0 or PL, PL); Y1 = Y1 or p.H
    zf = sign * (TB + TW) + dz
    zp = zf - t if sign > 0 else zf
    zr0 = zf - TW if sign > 0 else zf
    S.box((0, Y0, zp), (X, 0, 0), (0, Y1 - Y0, 0), (0, 0, t), WHITE_)
    S.box((0, Y0, zr0), (t, 0, 0), (0, Y1 - Y0, 0), (0, 0, TW), WHITE_)
    if X >= p.W:
        S.box((p.W - t, Y0, zr0), (t, 0, 0), (0, Y1 - Y0, 0), (0, 0, TW), WHITE_)
    if Y0 <= PL:
        S.box((0, PL, zr0), (X, 0, 0), (0, t, 0), (0, 0, TW), WHITE_)
    if Y1 >= p.H:
        ze0 = zf - EAR + 0.5 if sign > 0 else zf
        S.box((0, p.H - t, ze0), (X, 0, 0), (0, t, 0), (0, 0, EAR - 0.5), WHITE_)
        S.box((0, p.HB, ze0), (t, 0, 0), (0, 30, 0), (0, 0, EAR - 0.5), WHITE_)
        if X >= p.W:
            S.box((p.W - t, p.HB, ze0), (t, 0, 0), (0, 30, 0), (0, 0, EAR - 0.5), WHITE_)


def leaders(items, xc, side="r", gap=17):
    """balionai viename stulpelyje, eilės tvarka pagal taikinio y - nuorodų linijos nesikerta
    items: [(n, x, y)]; xc - balionų stulpelio x"""
    it = sorted(items, key=lambda q: q[2])
    ys = [q[2] for q in it]
    for i in range(1, len(ys)):
        ys[i] = max(ys[i], ys[i - 1] + gap)
    over = ys[-1] - max(q[2] for q in it) if it else 0
    if over > 0:                                          # centruoti grupę ties taikiniais
        sh = over / 2
        ys = [y - sh for y in ys]
        for i in range(1, len(ys)):
            ys[i] = max(ys[i], ys[i - 1] + gap)
    sg = 1 if side == "r" else -1
    for (n_, x_, y_), yb in zip(it, ys):
        xe = xc - sg * 14
        line(x_, y_, xe, yb, 0.3) if abs(yb - y_) > 0.5 else line(x_, y_, xe, y_, 0.3)
        line(xe, yb, xc - sg * 6.5, yb, 0.3)
        K.c.saveState(); K.c.setFillColor(black); K.c.circle(x_, K.Y(y_), 1.0, stroke=0, fill=1); K.c.restoreState()
        balloon(xc, yb, n_)


def ext3d(S, p):
    """3D klientui: tik išoriniai kūnai (be vidinių detalių) - teisingas užstojimas"""
    W, H, HB = p.W, p.H, p.HB
    zb0 = -TB; zb1 = TB
    S.box((0, p.BG, zb0), (W, 0, 0), (0, HB - p.BG, 0), (0, 0, zb1 - zb0), BLUE)                    # mėlynas korpusas
    S.box((0, PL, TB), (W, 0, 0), (0, H - PL, 0), (0, 0, TW), WHITE_)                     # balta priekis (30)
    if p.sides == 2:
        S.box((0, PL, -TB - TW), (W, 0, 0), (0, H - PL, 0), (0, 0, TW), WHITE_)
    S.box((0, HB, -TB), (W, 0, 0), (0, H - HB, 0), (0, 0, 2 * TB), WHITE_)                # v156: baltas viršus per visą gylį
                                                                                           # (ir vienpusiam - EAR iki galo)
    if p.legs == "ext":
        S.box((p.FX0, -p.LONG, -FR / 2), (FR, 0, 0), (0, p.LONG, 0), (0, 0, FR), AL)
        for fx, fy in ((p.FAX, -p.LONG - p.FLT), (W - p.FAX, -p.FLT)):
            S.box((fx - p.FL / 2, fy, -p.FL / 2), (p.FL, 0, 0), (0, p.FLT, 0), (0, 0, p.FL), GREYF)


def overlay_graphic(S, p, graphic):
    """kliento grafika ant balto priekio 3D vaizde (ortografinė projekcija - afininė)"""
    if not graphic:
        return
    pno, clip = graphic
    zf = TB + TW
    tl, tr, bl = S.V.S(0, p.H, zf), S.V.S(p.W, p.H, zf), S.V.S(0, p.H - p.OVH, zf)
    place_img(pno, clip, tl, tr, bl, K.HAIR)


def exploded3d(S, p, g=420):
    """sprogdintas vaizdas: detalės atskirai (nesiliečia) -> teisingas užstojimas"""
    W, HB, H = p.W, p.HB, p.H
    # rėmas
    S.box((p.FX0, p.V0L, -FR / 2), (FR, 0, 0), (0, p.VR_L, 0), (0, 0, FR), AL)
    S.box((p.FX1 - FR, p.V0R, -FR / 2), (FR, 0, 0), (0, p.VR_R, 0), (0, 0, FR), AL)
    for yy in p.RAILS:
        S.box((p.FX0 + FR, yy, -FR / 2), (p.HL, 0, 0), (0, FR, 0), (0, 0, FR), AL)
    if p.legs == "ext":
        for fx, fy in ((p.FAX, -p.LONG - p.FLT), (W - p.FAX, -p.FLT)):
            S.box((fx - p.FL / 2, fy, -p.FL / 2), (p.FL, 0, 0), (0, p.FLT, 0), (0, 0, p.FL), GREYF)
    else:
        S.box((p.FX0, 0, -40), (p.FW, 0, 0), (0, 40, 0), (0, 0, 80), AL)
    def tray(z_face, sign, depth, y0, y1, col, cap=0):
        zf = z_face
        zp = zf - t if sign > 0 else zf
        S.box((0, y0, zp), (W, 0, 0), (0, y1 - y0, 0), (0, 0, t), col)
        zr0, zr1 = (zf - depth, zf - t) if sign > 0 else (zf + t, zf + depth)
        S.box((0, y0, zr0), (t, 0, 0), (0, y1 - y0 - t, 0), (0, 0, zr1 - zr0), col)
        S.box((W - t, y0, zr0), (t, 0, 0), (0, y1 - y0 - t, 0), (0, 0, zr1 - zr0), col)
        zc0, zc1 = (zf - (cap or depth), zf - t) if sign > 0 else (zf + t, zf + (cap or depth))
        S.box((0, y1 - t, zc0), (W, 0, 0), (0, t, 0), (0, 0, zc1 - zc0), col)
    tray(TB + g, 1, TB, p.BG, HB, BLUE); tray(-TB - g, -1, TB, p.BG, HB, BLUE)
    def wtop(zf, sign):
        zr = zf - sign * (EAR - 0.5)
        S.box((0, HB, min(zr, zr + sign * t)), (W, 0, 0), (0, H - HB - t, 0), (0, 0, t), WHITE_)            # galinė plokštuma 30
        za, zb = sorted((zf - sign * TW, zr + sign * t))
        S.box((0, HB, za), (t, 0, 0), (0, H - HB - t, 0), (0, 0, zb - za), WHITE_)                            # ausės
        S.box((W - t, HB, za), (t, 0, 0), (0, H - HB - t, 0), (0, 0, zb - za), WHITE_)
    tray(TB + TW + 2.6 * g, 1, TW, PL, H, WHITE_, cap=EAR); wtop(TB + TW + 2.6 * g, 1)
    if p.sides == 2:
        tray(-TB - TW - 2.6 * g, -1, TW, PL, H, WHITE_, cap=EAR); wtop(-TB - TW - 2.6 * g, -1)


def build(S, p, dz=(0, 0, 0, 0)):
    frame3d(S, p)
    blue3d(S, p, +1, dz[0]); blue3d(S, p, -1, -dz[0])
    L3d(S, p, +1, dz[1]); white3d(S, p, +1, dz[2])
    if p.sides == 2:
        L3d(S, p, -1, -dz[1]); white3d(S, p, -1, -dz[2])


# ======================================================================== GA lapas
def ga(p, sheet, graphic, decals=None):
    begin(f"Thales_{p.key}_GA", 12)
    n = 20 if p.H > 2300 else 15
    s = MM / n
    W, H, D = p.W, p.H, p.D
    fw, fh = W * s, H * s
    fx = VX0 + 96
    ty = VY0 + 18
    fy = ty + D * s + 60
    ybase = fy + H * s
    # TOP VIEW
    zfront = ty
    rect(fx, ty, fw, D * s, fill=WHITE_, lw=0.3)          # rev C: balta viršus per visą gylį (vienpusiame - iki galo)
    if p.sides == 2:
        line(fx, ty + (TW + TB) * s, fx + fw, ty + (TW + TB) * s, 0.25)
    if p.legs == "ext":
        for xf in (p.FAX, W - p.FAX):
            rect(fx + (xf - p.FL / 2) * s, ty + (TW + TB) * s - p.FL / 2 * s, p.FL * s, p.FL * s, lw=0.3, dash=([2, 1.5], 0))
    if p.legs != "ext":
        yc = ty + (TW + TB) * s
        rect(fx + p.FX0 * s, yc - 40 * s, p.FW * s, 80 * s, lw=0.3, dash=([2, 1.2], 0))
        for hx, hz in p.BH:
            K.circle(fx + (p.FX0 + hx) * s, yc - hz * s, 0.9, fill=white, stroke=black, lw=0.25)
    vchain(fx + fw + 16, [ty, ty + D * s], [fx + fw] * 2, [f"{D}"], DIM)
    view_title(fx - 40, ty + D * s / 2 + 2, "TOP VIEW", f"SCALE 1:{n}")
    # FRONT VIEW
    rect(fx, fy, fw, p.OVH * s, fill=WHITE_, lw=0.3)
    rect(fx, fy + p.OVH * s, fw, (PL - p.BG) * s, fill=BLUE, lw=0.3)
    if graphic:
        pno, clip = graphic
        draw_client(pno, clip, fx, fy, fw, p.OVH * s)
    if p.legs == "ext":
        rect(fx + p.FX0 * s, ybase, FR * s, p.LONG * s, fill=AL, lw=0.3)
        for xf, yb in ((p.FAX, p.LONG), (W - p.FAX, 0)):
            rect(fx + (xf - p.FL / 2) * s, ybase + yb * s, p.FL * s, p.FLT * s, fill=GREYF, lw=0.3)
            K.centerline(fx + xf * s, ybase + yb * s - 8, fx + xf * s, ybase + (yb + p.FLT) * s + 8)
        gl, gr = ybase + (p.LONG + p.FLT) * s, ybase + p.FLT * s
        line(fx - 30, gl + 0.3, fx + fw + 30, gr + 0.3, 0.4, black, dash=([6, 2], 0))
        T(fx + fw + 34, gr + 13, "ground (slope)", 8, color=K.GREY, auto_red=False)
        vchain(fx - 52, [ybase, ybase + p.LONG * s, gl], [fx + p.FX0 * s] * 3, [f"{p.LONG}", f"{p.FLT}"], DIM)
        hchain(gl + 20, [fx, fx + p.FAX * s, fx + (W - p.FAX) * s, fx + fw], [ybase + p.FLT * s] * 4, [f"{p.FAX}", "1000 (existing anchors)", f"{p.FAX}"], DIM)
        T(fx + fw / 2, gl + 34, "flanges 300x300x20, 4 x Ø14 holes 237 x 237 (existing anchors), sheet 2", 8, color=K.GREY, align="c", auto_red=False)
        yb_end = gl + 40
    else:
        rect(fx + p.FX0 * s, ybase - 40 * s, p.FW * s, 40 * s, lw=0.3, dash=([2, 1.2], 0))   # balkis 80x40 (paslėptas)
        for hx, hz in p.BH:
            K.centerline(fx + (p.FX0 + hx) * s, ybase - 46 * s, fx + (p.FX0 + hx) * s, ybase + 6)
        line(fx - 30, ybase, fx + fw + 30, ybase, 0.4, black, dash=([6, 2], 0))
        gl = ybase
        xs_h = [fx] + [fx + (p.FX0 + hx) * s for hx, _ in p.BH] + [fx + fw]
        # rev C: ankerių grandinė 1:15 su 12 pt netelpa - matmenys DETAIL H (sheet 4, 1:5)
        T(fx + fw / 2, gl + 16, "hidden base beam 80x40x4, 4 anchors (staggered) - see DETAIL H, sheet 4", 8, color=K.GREY, align="c", auto_red=False)
        yb_end = gl + 40
    vchain(fx - 16, [fy, fy + p.OVH * s, ybase], [fx] * 3, [f"{p.OVH}", f"{PL}"], DIM)
    vchain(fx - 36, [fy, ybase], [fx] * 2, [f"{H}"], DIM)
    hdim(fx, fx + fw, fy - 16, f"{W}", fy, fy, DIM)
    leader(fx + fw * 0.85, fy + p.OVH * s * 0.92, fx + fw + 50, fy + p.OVH * s * 0.92 + 12, 5)
    leader(fx + fw * 0.6, fy + (p.OVH + PL / 2) * s, fx + fw + 50, fy + (p.OVH + PL / 2) * s + 14, 2)
    view_title(fx + fw / 2, yb_end + 26, "FRONT VIEW" + (" (side A = side B)" if p.sides == 2 else ""), f"SCALE 1:{n}")
    if p.legs == "ext":                                           # grafikos elementų padėtis (iš kliento BAT)
        # rev C: tik grafikos BLOKAI (logotipas, BIENVENUE / WELCOME) - smulkūs aukščiai tekste (Print layout), 12 pt telpa
        ys_ = [0, 106, 294 + 65, 968, 1115 + 93, p.OVH]
        vchain(fx + fw + 16, [fy + v * s for v in ys_], [fx + fw - 2] * len(ys_), [f"{b - a}" for a, b in zip(ys_[:-1], ys_[1:])], DIM)
    gl_ = ["GRAPHICS (5): digital print on polymeric film + matt laminate,",
           "full-face wrap: applied over the whole white face, trimmed" ,
           "to the sheet edges" + (" - both sides." if p.sides == 2 else "."),
           "RAL 5022 / RAL 5012 matched in print - colour proof to client."]
    gl_ += (["Print layout W x H (centred): THALES 852x101, Campus VELIZY 852x65,", "BIENVENUE 733x91, WELCOME 657x93."] if p.legs == "ext"
            else ["4 different decals - sizes see DECALS; position per client BAT."])
    gx_, gy_ = (VX0 + 4, yb_end + 52) if p.legs == "ext" else (fx + fw + 70, VY0 + 14)
    for i_, tx_ in enumerate(gl_):
        T(gx_, gy_ + i_ * 10, tx_, 8, font="FB" if i_ == 0 else "F", auto_red=False)
    # SIDE VIEW (RIGHT) - su varžtais
    sx = fx + fw + 90
    zW = lambda z: sx + (D / 2 + (z if p.sides == 2 else z - TW / 2)) * s if False else None
    # x vaizde: priekis kairėje (z max) -> z = +(TB+TW) ties sx
    zmax = TB + TW
    X = lambda z: sx + (zmax - z) * s
    rect(X(TB), fy + 30 * s, p.BODY * s, (p.HB - p.BG) * s, fill=BLUE, lw=0.3)
    rect(X(TB + TW), fy, TW * s, p.OVH * s, fill=WHITE_, lw=0.3)
    rect(X(TB + TW), fy, EAR * s, 30 * s, fill=WHITE_, lw=0.3)
    if p.sides == 2:
        rect(X(-TB), fy, TW * s, p.OVH * s, fill=WHITE_, lw=0.3)
        rect(X(0), fy, EAR * s, 30 * s, fill=WHITE_, lw=0.3)
    line(X(0), fy + 30 * s, X(0), ybase, 0.25, white)
    Yv = lambda y: ybase - y * s
    for q in p.w_side_holes()[2]:
        yv = Yv(PL + q)
        K.circle(X(TB + TW - HO_W), yv, 0.9, fill=SCREW, stroke=None)
        if p.sides == 2:
            K.circle(X(-(TB + TW - HO_W)), yv, 0.9, fill=SCREW, stroke=None)
    for q in p.b_side_holes()[2]:
        yv = Yv(q)
        for z in (TB - HO_B, -(TB - HO_B)):
            K.circle(X(z), yv, 0.9, fill=SCREW, stroke=None)
    if p.legs == "ext":
        rect(X(0) - p.FL / 2 * s, ybase, p.FL * s, p.FLT * s, fill=GREYF, lw=0.3)
    else:
        rect(X(40), ybase - 40 * s, 80 * s, 40 * s, lw=0.3, dash=([2, 1.2], 0))
        line(X(TB + TW) - 20, ybase, X(-TB) + 20, ybase, 0.4, black, dash=([6, 2], 0))
    labs = ["30", f"{TB}", f"{TB}"] + (["30"] if p.sides == 2 else [])
    xs = [X(TB + TW), X(TB), X(0), X(-TB)] + ([X(-TB - TW)] if p.sides == 2 else [])
    hdim(xs[0], xs[-1], fy - 16, f"{D}", fy, fy, DIM)          # rev C: sluoksniai 30 / TB - pjūvyje A (1:2), čia tik gylis
    nwb = p.w_side_holes(); nbb = p.b_side_holes()
    leader(X(TB + TW - HO_W), Yv(PL + nwb[2][2]), xs[-1] + 30, Yv(PL + nwb[2][2]) - 20, 6)
    leader(X(TB - HO_B), Yv(nbb[2][2]), xs[-1] + 30, Yv(nbb[2][2]) + 10, 9)
    view_title((xs[0] + xs[-1]) / 2, yb_end + 26, "SIDE VIEW (RIGHT)", f"SCALE 1:{n}")
    # FRAME VIEW
    gx = xs[-1] + 110
    by = fy + 30 * s
    rect(gx, by, fw, p.HB * s, lw=0.3, dash=([3, 2], 0))
    rect(gx + p.FX0 * s, Yv(p.FY1), FR * s, p.VR_L * s, fill=AL, lw=0.3)
    rect(gx + (p.FX1 - FR) * s, Yv(p.FY1), FR * s, p.VR_R * s, fill=AL, lw=0.3)
    for yy in p.RAILS:
        rect(gx + (p.FX0 + FR) * s, Yv(yy + FR), p.HL * s, FR * s, fill=AL, lw=0.3)
    if p.legs == "ext":
        for xf, yb in ((p.FAX, p.LONG), (W - p.FAX, 0)):
            rect(gx + (xf - p.FL / 2) * s, ybase + yb * s, p.FL * s, p.FLT * s, fill=GREYF, lw=0.3)
    else:
        rect(gx + p.FX0 * s, Yv(40), p.FW * s, 40 * s, fill=AL, lw=0.3)
        for hx, hz in p.BH:
            K.centerline(gx + (p.FX0 + hx) * s, Yv(46), gx + (p.FX0 + hx) * s, ybase + 4)
    hdim(gx + p.FX0 * s, gx + p.FX1 * s, by - 16, f"{p.FW}", by, by, DIM)        # rev C: laisvumas 3 - raudona pastaba
    ys_ax = [ybase - (y + FR / 2) * s for y in sorted(p.RAILS, reverse=True)] + ([] if p.legs == "ext" else [ybase - 20 * s])
    ys = [Yv(p.FY1 + CL)] + ys_ax + [ybase]
    vchain(gx + fw + 16, ys, [gx + fw] * len(ys), [f"{(b - a) / s:.0f}" for a, b in zip(ys[:-1], ys[1:])], DIM)
    if p.legs == "ext":
        vchain(gx - 16, [Yv(p.FY1), ybase], [gx] * 2, [f"{p.FY1}"], DIM)
    else:
        vchain(gx - 16, [Yv(p.FY1), ybase], [gx] * 2, [f"{p.FY1}"], DIM)
    leader(gx + (p.FX1 - FR / 2) * s, Yv(p.HB * 0.8), gx + fw + 44, Yv(p.HB * 0.8) - 10, 1)
    leader(gx + fw * 0.5 - 30, ybase + (p.FLT / 2) * s if p.legs == "ext" else ybase - 10 * s, gx + fw + 44, ybase - 40, 7)   # rev C: ne ant pavadinimo
    T(gx + fw / 2, yb_end + 44, "frame = sheet - 6 (2 sheet + 1 clearance per side)", 8, color=RED, align="c", auto_red=False)
    view_title(gx + fw / 2, yb_end + 18, "FRAME VIEW (sheets removed)", f"SCALE 1:{n}")
    # 3D / dekorai
    x3 = gx + fw + 70
    if decals:
        dn = 25; ds = MM / dn
        ddw, ddh = W * ds, p.OVH * ds
        gap = 14
        ddx = VX1 - (4 * ddw + 3 * gap); ddy = VY0 + 12
        for i, (name, pno, clip, dw_, dh_) in enumerate(decals):
            x_ = ddx + i * (ddw + gap)
            rect(x_, ddy, ddw, ddh, fill=WHITE_, lw=0.3); rect(x_, ddy + ddh, ddw, PL * ds, fill=BLUE, lw=0.3)
            draw_client(pno, clip, x_, ddy, ddw, ddh)
            T(x_ + ddw / 2, ddy + ddh + PL * ds + 11, name, 8, font="FB", align="c")
            T(x_ + ddw / 2, ddy + ddh + PL * ds + 21, f"{dw_} x {dh_}", 8, color=K.GREY, align="c")
        view_title(ddx + (4 * ddw + 3 * gap) / 2, ddy + ddh + PL * ds + 40, "DECALS (4) - 1 per pylon", f"SCALE 1:{dn}")
        y3 = ddy + ddh + PL * ds + 60
    else:
        y3 = VY0 + 16
    S = r3d.Scene(yaw=32, pitch=15)                       # v163: kaip kliento „Principe" - iš kairės (šonas kairėje)
    ext3d(S, p)
    w3 = VX1 - x3; h3 = VY1 - 26 - y3
    S.render((x3, y3, w3, h3))
    overlay_graphic(S, p, graphic)
    view_title(x3 + w3 / 2, VY1 - 6, "3D VIEW", "ILLUSTRATIVE - NOT TO SCALE")
    # juosta
    sides = p.sides
    def sec(x, y, w, h):
        k = MM / 3.2
        typical_hsec(x + 50, y + 24, k, p, 110, labels=False)
        T(x + w / 2, y + 12, "horizontal section at side edge, 1:3", 8, color=K.GREY, align="c", auto_red=False)
    rows, md = bom(p)
    band(p.short + " - general arrangement", sheet, "TYPICAL SECTION", sec, rows, md, f"1:{n}")
    save(f"{OUT}/{p.key}_1_GA.pdf")


def bom(p):
    W, sides = p.W, p.sides
    frame_m = (p.VR_L + p.VR_R + 4 * p.HL) / 1000
    Lm = sides * (2 * p.LV + p.LH + (W - 8)) / 1000
    nws, _, _ = p.w_side_holes(); nwb, _, _ = p.w_bot_holes()
    n_w = sides * (2 * (nws + 1) + 2 * (nwb + 1))
    nbs, _, _ = p.b_side_holes(); nbt, _, _ = p.b_top_holes()
    n_b = 2 * 2 * (nbs + 1)
    nr, _, _ = p.rivets_v()
    n_r = sides * (2 * (nr + 1) + max(2, round(p.LH / 300) + 1) + 4)
    A_blue = (W * p.HB + 2 * TB * p.HB + TB * W + p.rib * (W - 2 * NOTCH)) / 1e6
    A_white = (W * p.OVH + 2 * TW * p.OVH + TW * W + EAR * W + 2 * (EAR - TW) * 30) / 1e6
    kg = frame_m * 1.85 + (2 * A_blue + sides * A_white) * 2 * 2.7 + Lm * 0.26 + \
         (2 * p.FL * p.FL * p.FLT / 1e6 * 2.7 if p.legs == "ext" else p.FW * (2 * 80 + 2 * 32) * 4 / 1e6 * 2.7)
    rows = [[1, f"Frame tube 60x60x3, welded, {p.FW} wide", "Alu 6082-T6", "-" if p.legs == "ext" else "RAL 5022", f"{p.VR_L} + {p.VR_R} + 4 x {p.HL} = {frame_m:.2f} m"],
            [2, f"Blue tray {W}x{p.HB}x{TB}" + (f", rib {p.rib}" if p.rib else ", open bottom"), "Alu 2 mm folded", "RAL 5022", f"2 pcs. / {2 * A_blue:.2f} m²"],
            [3, "L 25x25x2 riveted to blue tray", "Aluminium", "-", f"{Lm:.2f} m ({sides} side{'s' if sides == 2 else ''})"],
            [4, f"White tray {W}x{p.OVH}, top 70, ears", "Alu 2 mm folded", "RAL 9016", f"{sides} pcs. / {sides * A_white:.2f} m²"],
            [5, "Decal full-face wrap, trimmed to edges", "Polymeric film + matt lam.", "print", f"{sides} pcs. / {sides * W * p.OVH / 1e6:.2f} m²"],
            [6, "Csk screw white -> L", "?", "RAL 9016", f"{n_w} pcs."],
            [7, f"Base flange {p.FL}x{p.FL}x{p.FLT}, 4xØ14" if p.legs == "ext" else f"Base beam 80x40x4, L {p.FW}, 4 sleeves", "Alu 6060-T66", "-" if p.legs == "ext" else "RAL 5022",
             "2 pcs. (1 on long leg)" if p.legs == "ext" else "1 pcs."],
            [8, "Anchors - existing base" if p.legs == "ext" else "Chem. anchor M16 A4, hef >= 125", "?" if p.legs == "ext" else "e.g. HIT-HY 200 + HAS-U", "-", "?" if p.legs == "ext" else "4 pcs."],
            [9, "Csk screw blue sides -> frame", "?", "RAL 5022", f"{n_b} pcs."],
            [10, "Blind rivet L -> blue tray", "?", "-", f"{n_r} pcs."]]
    md = [["Quantity", f"{p.qty} pcs."], ["Overall", f"{W} x {p.H} x {p.D}"], ["Type", "non-illum., " + ("double-sided" if sides == 2 else "single-sided")],
          ["Frame", f"{p.FW} x {p.FY1 - CL} (60x60x3), sheet - 6"], ["Blue", f"2 trays x {TB}, " + (f"bottom rib {p.rib}" if p.rib else "bottom open (no fold)")],
          ["White", "sides / bottom 30, top 70, ears 70x30"], ["Graphics", "full-face wrap, print + matt lam."], ["Fixing", "csk screws, perimeter"],
          ["Base", f"2 x flange {p.FL}, left leg +{p.LONG}" if p.legs == "ext" else "hidden beam 80x40x4 + 4 x M16"],
          ["Weight (calc.)", f"≈ {kg:.0f} kg / pcs"]]
    return rows, md


# ======================================================================== pjūviai
def typical_hsec(ox, oy, k, p, L_=150, labels=True):
    """horizontalus pjūvis per šoninį kraštą (x į dešinę = pilono vidus, y žemyn = gylis nuo priekio)"""
    sides = p.sides
    yW1 = oy; yB1 = yW1 + TW * k; yC = yB1 + TB * k; yB2 = yC + TB * k; yW2 = yB2 + (TW * k if sides == 2 else 0)
    K.set_view(True)
    fx = ox + CL * k; fy = yB1 + t * k + (p.BODY - 2 * t - FR) / 2 * k
    cut(fx, fy, FR * k, FR * k, black); cut(fx + FT * k, fy + FT * k, (FR - 2 * FT) * k, (FR - 2 * FT) * k, white)
    cut(ox, yB1, L_ * k, t * k, BLUE); cut(ox, yB1, t * k, TB * k, BLUE)
    cut(ox, yB2 - t * k, L_ * k, t * k, BLUE); cut(ox, yC, t * k, TB * k, BLUE)
    lx = ox + 4 * k
    cut(lx, yB1 - LT * k, LP * k, LT * k, LCOL); cut(lx, yB1 - LP * k, LT * k, LP * k, LCOL)
    cut(ox, yW1, L_ * k, t * k, WHITE_); cut(ox, yW1, t * k, TW * k, WHITE_)
    if sides == 2:
        cut(lx, yB2, LP * k, LT * k, LCOL); cut(lx, yB2, LT * k, LP * k, LCOL)
        cut(ox, yW2 - t * k, L_ * k, t * k, WHITE_); cut(ox, yW2 - TW * k, t * k, TW * k, WHITE_)
    xr = ox + L_ * k
    poly([(xr, yW1 - 6), (xr - 4, yW1 + 20), (xr + 4, yW1 + 40), (xr, yW2 + 6)], close=False, lw=0.3)
    K.set_view(False)
    # varžtai
    csk_h(ox, yW1 + HO_W * k, k, 12)                       # balta -> L
    if sides == 2:
        csk_h(ox, yW2 - HO_W * k, k, 12)
    csk_h(ox, yB1 + HO_B * k, k, 16)                       # mėlyna -> rėmas
    csk_h(ox, yB2 - HO_B * k, k, 16)
    rivet_v(lx + (LP * 0.55) * k, yB1 - LT * k - 1.5 * k, k, 7)
    if sides == 2:
        rivet_v(lx + (LP * 0.55) * k, yB2 - 5.5 * k, k, 7)
    ys = [yW1, yB1, yC, yB2] + ([yW2] if sides == 2 else [])
    vchain(ox - 34, ys, [ox] * len(ys), ["30", f"{TB}", f"{TB}"] + (["30"] if sides == 2 else []), DIM)
    if labels:
        vchain(ox - 56, [yW1, yW2], [ox] * 2, [f"{p.D}"], DIM)
        hdim(ox, fx, fy + FR * k + 12, "3", None, None, DIM, small_side="l")
        hdim(ox, ox + t * k, yW1 - 12, "2", yW1, yW1, DIM, small_side="l")
        hdim(lx, lx + LP * k, yB1 - LP * k - 30, "25 (L 25x25x2)", yB1 - LP * k, yB1 - LP * k, DIM)
        hdim(ox, lx, yB1 + 6 * k, "4", None, None, DIM, small_side="l") if False else None
        vchain(fx + FR * k + 16, [yB1, yB1 + HO_B * k], [ox + 30] * 2, [f"{HO_B}"], DIM)
        vchain(ox + L_ * k + 16, [yW1, yW1 + HO_W * k], [ox + L_ * k] * 2, [f"{HO_W}"], DIM)
    ln = [(1, fx + FR * k / 2, fy + FR * k / 2), (2, ox + 70 * k, yB1 + t * k / 2), (3, lx + 15 * k, yB1 - LT * k / 2),
          (4, ox + 90 * k, yW1 + t * k / 2), (6, ox - 1, yW1 + HO_W * k), (9, ox - 1, yB1 + HO_B * k)]
    tx = ox + L_ * k + (40 if labels else 30)
    ln = [(n_, x_, y_) for n_, x_, y_ in ln if n_ not in (6, 9)]
    leaders(ln, tx, "r", gap=15 if labels else 13)
    for n_, yy_ in ((6, yW1 + HO_W * k), (9, yB1 + HO_B * k)):          # varžtai - kairėje, horizontaliai
        line(ox - 2 * k, yy_, ox - 12, yy_, 0.3); balloon(ox - 18.5, yy_, n_)
    return yW2


def sections(p, sheet):
    begin(f"Thales_{p.key}_SEC", 10)
    k = MM / 2
    # A - horizontalus
    yend = typical_hsec(VX0 + 90, VY0 + 50, k, p, 150)
    view_title(VX0 + 90 + 75 * k, yend + 34, "SECTION A - HORIZONTAL (side edge, white zone)", "SCALE 1:2")
    # B - vertikalus viršus (pjūvis per ausę / kampinį L, x = 20)
    ox = VX0 + 470; oy = VY0 + 62
    zmax = TB + TW
    Xz = lambda z: ox + (zmax - z) * k
    Yy = lambda y: oy + (p.H - y) * k
    y_lo = p.HB - 110
    K.set_view(True)
    # rėmo viršutinis skersinis + vertikalė
    cut(Xz(FR / 2), Yy(p.FY1), FR * k, FR * k, black); cut(Xz(FR / 2) + FT * k, Yy(p.FY1) + FT * k, (FR - 6) * k, (FR - 6) * k, white)
    # mėlyna: priekis + viršus 40 (abi pusės)
    for sg in (1, -1):
        zf = sg * TB
        cut(min(Xz(zf), Xz(zf - sg * t)), Yy(p.HB), t * k, (p.HB - y_lo) * k, BLUE)
        cut(min(Xz(zf), Xz(0)), Yy(p.HB), TB * k, t * k, BLUE)
    # L ant mėlyno priekio (vertikali); balta: priekis + viršus 70 + galinė plokštuma 30 (apverstas U); L 25 ant mėlyno viršaus
    ZF = 0.5                                                                     # baltų galinių plokštumų tarpas nuo ašies
    SY = p.HB + 14                                                               # varžto aukštis
    ZR = (lambda sg: sg * ZF) if p.sides == 2 else (lambda sg: -TB)             # rev C: vienpusiame galinė plokštuma - pilono gale
    for sg in ([1, -1] if p.sides == 2 else [1]):
        zf = sg * TB
        cut(min(Xz(zf), Xz(zf + sg * LT)), Yy(p.HB - 5), LT * k, (p.HB - 5 - y_lo) * k, LCOL)
        zw = sg * (TB + TW); zr = ZR(sg)
        cut(min(Xz(zw), Xz(zw - sg * t)), Yy(p.H), t * k, (p.H - y_lo) * k, WHITE_)
        cut(min(Xz(zw), Xz(zr)), Yy(p.H), abs(zw - zr) * k, t * k, WHITE_)                          # viršus EAR
        cut(min(Xz(zr), Xz(zr + sg * t)), Yy(p.H), t * k, (p.H - p.HB) * k, WHITE_)               # galinė plokštuma 30
        z1 = zr + sg * t
        cut(min(Xz(z1), Xz(z1 + sg * LT)), Yy(p.HB + LP), LT * k, LP * k, LCOL)                      # L stati kojelė
        cut(min(Xz(z1), Xz(z1 + sg * LP)), Yy(p.HB + LT), LP * k, LT * k, LCOL)                      # L gulsčia kojelė
        rivet_v(Xz(z1 + sg * 15), Yy(p.HB + LT) - 1.5 * k, k, 6)
    K.set_view(False)
    for sg in ([1, -1] if p.sides == 2 else [1]):
        csk_h(Xz(ZR(sg)), Yy(SY), k, 10, "r" if sg > 0 else "l")
    hchain(Yy(p.H) - 16, [Xz(TB + TW), Xz(TB), Xz(0), Xz(-TB)] + ([Xz(-TB - TW)] if p.sides == 2 else []), [Yy(p.H)] * (5 if p.sides == 2 else 4),
           ["30", f"{TB}", f"{TB}"] + (["30"] if p.sides == 2 else []), DIM)
    hchain(Yy(p.H) - 36, [Xz(TB + TW), Xz(ZR(1))] + ([Xz(-TB - TW)] if p.sides == 2 else []), [Yy(p.H)] * (3 if p.sides == 2 else 2),
           [f"{EAR}"] + ([f"{EAR}"] if p.sides == 2 else []), DIM)
    vchain(Xz(TB + TW) - 14, [Yy(p.H), Yy(p.HB)], [Xz(TB + TW)] * 2, ["30"], DIM)
    vchain(Xz(-TB - (TW if p.sides == 2 else 0)) - 0 + 14, [Yy(p.HB), Yy(SY)], [Xz(-ZF)] * 2, [f"{SY - p.HB}"], DIM) if False else None
    T(Xz(TB + TW) - 58, Yy(p.H) + 3, f"{p.H}", 8, align="r", color=K.GREY, auto_red=False)
    T(Xz(TB + TW) - 58, Yy(p.HB) + 3, f"{p.HB}", 8, align="r", color=K.GREY, auto_red=False)
    xr_ = Xz(-TB - (TW if p.sides == 2 else 0)) + 34
    sgb = -1 if p.sides == 2 else 1
    leaders([(6, Xz(ZR(sgb)) + (3 if sgb < 0 else -3), Yy(SY)), (3, Xz(ZR(sgb) + sgb * (t + LT / 2)), Yy(p.HB + 20)), (1, Xz(-FR / 2 + 3), Yy(p.FY1 - FR / 2)),
             (2, Xz(-TB + 1), Yy(p.HB - 70))], xr_, "r")
    leaders([(4, Xz(TB + TW - 1), Yy(p.HB - 90)), (3, Xz(TB + 1), Yy(p.HB - 40))], Xz(TB + TW) - 46, "l")
    for i_, tx_ in enumerate([f"White top = inverted U: top {EAR} + rear plane 30" + (" (to the back edge)" if p.sides == 1 else "") + ", csk screws (6)",
                              "into L 25x25x2 riveted on blue top. White + blue pre-assembled;",
                              "segment fixed to frame through blue SIDE returns only (A, pos. 9)."]):
        T(ox - 10, Yy(y_lo) + 14 + i_ * 10, tx_, 8, color=K.GREY, auto_red=False)
    view_title((Xz(TB + TW) + Xz(-TB - (TW if p.sides == 2 else 0))) / 2, Yy(y_lo) + 58, "SECTION B - VERTICAL, TOP", "SCALE 1:2")
    # C - vertikalus apačia tarp kojų (x = W/2): briauna 20, apatinis L, balta 30
    k = MM / 3.5 if p.rib else MM / 5
    ox2 = VX0 + (790 if p.rib else 640); oy2 = VY0 + (60 if p.rib else 340)
    ytop2 = PL + 70 if p.rib else PL + 40
    Xz2 = lambda z: ox2 + (zmax - z) * k
    Yy2 = lambda y: oy2 + (ytop2 - y) * k
    K.set_view(True)
    if p.rib:
        r0 = p.RAILS[0]
        cut(Xz2(FR / 2), Yy2(r0 + FR), FR * k, FR * k, black); cut(Xz2(FR / 2) + FT * k, Yy2(r0 + FR) + FT * k, (FR - 6) * k, (FR - 6) * k, white)
    else:                                                   # balkis 80x40x4 su ankeriu (pjūvis per skylę z = +20)
        cut(Xz2(40), Yy2(40), 80 * k, 40 * k, black); cut(Xz2(36), Yy2(36), 72 * k, 32 * k, white)
        za = 20
        rect(Xz2(za + 15), Yy2(40), 30 * k, 40 * k, fill=HexColor("#8C8C8C"), lw=0.25)        # įvorė D30/D18, privirinta
        rect(Xz2(za + 9), Yy2(40), 18 * k, 40 * k, fill=white, lw=0.25)
        HB_ = 90                                                                      # rev C: ankeris nutrauktas (lūžio linija), hef 125 matmeniu
        rect(Xz2(za + 8), Yy2(40 + 3 + 16), 16 * k, (40 + 3 + 16 + HB_) * k, fill=HexColor("#B0B0B0"), lw=0.25)   # M16 strypas
        poly([(Xz2(za + 11), Yy2(-HB_) - 2), (Xz2(za + 4), Yy2(-HB_) + 2), (Xz2(za - 4), Yy2(-HB_) - 2), (Xz2(za - 11), Yy2(-HB_) + 2)],
             lw=0.4, close=False)
        rect(Xz2(za + 17), Yy2(43), 34 * k, 3 * k, fill=HexColor("#707070"), lw=0.25)         # poveržlė ant viršaus
        rect(Xz2(za + 12), Yy2(43 + 13), 24 * k, 13 * k, fill=HexColor("#555555"), lw=0.25)   # veržlė
        for zz_ in (za + 15, za - 15):                                                     # siūlės įvorė - sienelės
            for yy_, sg_ in ((40, -1), (0, 1)):
                poly([(Xz2(zz_), Yy2(yy_)), (Xz2(zz_ + (3 if zz_ > za else -3)), Yy2(yy_)), (Xz2(zz_), Yy2(yy_ + sg_ * 3))], fill=black, lw=0.2)
        K.centerline(Xz2(za), Yy2(64), Xz2(za), Yy2(-HB_ - 8))
    for sg in (1, -1):
        zf = sg * TB
        cut(min(Xz2(zf), Xz2(zf - sg * t)), Yy2(ytop2), t * k, (ytop2 - p.BG) * k, BLUE)
        if p.rib:
            cut(min(Xz2(zf), Xz2(zf - sg * p.rib)), Yy2(t), p.rib * k, t * k, BLUE)
    for sg in ([1, -1] if p.sides == 2 else [1]):
        zf = sg * TB
        cut(min(Xz2(zf), Xz2(zf + sg * LT)), Yy2(PL + 5 + LP), LT * k, LP * k, LCOL)
        cut(min(Xz2(zf), Xz2(zf + sg * LP)), Yy2(PL + 5 + LT), LP * k, LT * k, LCOL)
        zw = sg * (TB + TW)
        cut(min(Xz2(zw), Xz2(zw - sg * t)), Yy2(ytop2), t * k, (ytop2 - PL) * k, WHITE_)
        cut(min(Xz2(zw), Xz2(zw - sg * TW)), Yy2(PL + t), TW * k, t * k, WHITE_)
        csk_v(Xz2(sg * (TB + TW - HO_W)), Yy2(PL), k, 10, "b")
    K.set_view(False)
    vchain(Xz2(TB + TW) - 16, [Yy2(PL), Yy2(0)], [Xz2(TB + TW)] * 2, [f"{PL}"], DIM)
    if p.rib:
        line(Xz2(TB + TW) - 30, Yy2(0), Xz2(-TB - (TW if p.sides == 2 else 0)) + 30, Yy2(0), 0.4, black, dash=([6, 2], 0))
        hchain(Yy2(0) + 16, [Xz2(TB), Xz2(TB - p.rib)], [Yy2(0)] * 2, [f"{p.rib}"], DIM)
    else:
        line(Xz2(TB + TW) - 30, Yy2(0), Xz2(-TB) + 40, Yy2(0), 0.6, black)
        T(Xz2(TB + TW) - 34, Yy2(0) + 10, "concrete / solid base", 8, color=K.GREY, align="r", auto_red=False)
        # rev C (Rytis 2026-10-13: matmenys lipo vienas ant kito): balkio plotis - PO ankerio galu (grandinė 16, gabaritas 36),
        #  balkio aukštis / mėlyna 5 - dešinėje už dėžės, hef - kairėje (stulpelis kaip 200, kitas y ruožas)
        yb_ = Yy2(-HB_)
        hchain(yb_ + 16, [Xz2(40), Xz2(za), Xz2(-40)], [Yy2(0)] * 3, [f"{40 - za}", f"{40 + za}"], DIM)
        hdim(Xz2(40), Xz2(-40), yb_ + 36, "80", Yy2(0), Yy2(0), DIM)
        vchain(Xz2(-TB) + 16, [Yy2(40), Yy2(0)], [Xz2(-40)] * 2, ["40"], DIM)
        vchain(Xz2(TB + TW) - 16, [Yy2(0), Yy2(-HB_)], [Xz2(za)] * 2, ["hef 125"], DIM)
        tag(Xz2(za - 8), Yy2(-35), Xz2(-TB) + 40, Yy2(-50), "M16 A4, chem. anchor", 8)
        tag(Xz2(za - 12), Yy2(50), Xz2(-TB) + 64, Yy2(70), "nut + washer on top wall", 8)
        tag(Xz2(za - 15), Yy2(20), Xz2(-TB) + 64, Yy2(20), "sleeve D30/D18, welded", 8)
    if p.rib:
        vchain(Xz2(-TB) - (40 if p.sides == 2 else -20), [Yy2(CL + FR), Yy2(CL)], [Xz2(-FR / 2)] * 2, ["60"], DIM)   # rev C: laisvumas 3 - pastaboje
    else:
        vchain(Xz2(-TB) + 36, [Yy2(p.BG), Yy2(0)], [Xz2(-TB)] * 2, [f"{p.BG}"], DIM)

    hdim(Xz2(TB + TW), Xz2(TB + TW - HO_W), Yy2(PL) + 26, f"{HO_W}", Yy2(PL), Yy2(PL), DIM, small_side="l")
    if p.rib:
        T((Xz2(TB + TW) + Xz2(-TB)) / 2, Yy2(0) + 78, "rib 20 between legs;", 8, color=K.GREY, align="c", auto_red=False)
        T((Xz2(TB + TW) + Xz2(-TB)) / 2, Yy2(0) + 88, "notch at legs (no contact)", 8, color=K.GREY, align="c", auto_red=False)
        view_title((Xz2(TB + TW) + Xz2(-TB)) / 2, Yy2(0) + 40, "SECTION C - BOTTOM (between legs)", "SCALE 1:3.5")
    else:
        for i_, tx_ in enumerate(["1) frame anchored through", "beam 80x40x4 (bolt through", "both walls, welded sleeve),", "2) segments screwed on;", "blue 5 above base - hidden"]):
            T(Xz2(TB + TW) - 30, Yy2(150) + i_ * 10, tx_, 8, color=K.GREY, align="r", auto_red=False)
        view_title((Xz2(TB + TW) + Xz2(-TB)) / 2, Yy2(-HB_) + 64, "SECTION C - BOTTOM, BASE BEAM", "SCALE 1:5")
        beam_plan(p, VX0 + 40, VY0 + 330)
    if p.legs == "ext":
        flange_plan(p, VX0 + 40, VY0 + 330)
    # 3D - sprogdintas vaizdas
    dx = VX0 + (950 if p.rib else 880); dw = VX1 - dx
    S2 = r3d.Scene(yaw=-55, pitch=18)
    exploded3d(S2, p, 300 if p.sides == 2 else 260)
    S2.render((dx, VY0 + 10, dw, VY1 - VY0 - 40))
    P = S2.V.S
    g = 300 if p.sides == 2 else 260
    lab = [(1, (p.W / 2, p.RAILS[-2] + FR, 0)), (2, (p.W * 0.5, p.HB * 0.5, TB + g)), (4, (p.W * 0.5, p.H * 0.62, TB + TW + 2.6 * g))]
    if p.sides == 2:
        lab.append((4, (p.W * 0.5, p.H * 0.62, -TB - TW - 2.6 * g)))
    lab.append((2, (p.W * 0.5, p.HB * 0.5, -TB - g)))
    lab.append((7, ((p.FAX if p.legs == "ext" else p.W / 2), -10, 0)))
    for n_, (x_, y_, z_) in lab:
        px, py = P(x_, y_, z_)
        leader(px, K.H - py, px + 16, K.H - py - 20, n_)
    view_title(dx + dw / 2, VY1 - 6, "EXPLODED VIEW", "ILLUSTRATIVE, L 25 NOT SHOWN")

    def sec(x, y, w, h):
        items = [("csk screw white -> L (6)", "#E2001A"), ("csk screw blue -> frame (9)", "#E2001A"), ("blind rivet L -> blue (10)", "#555555")]
        yy = y + 18
        for lab, col in items:
            rect(x + 14, yy - 8, 30, 10, fill=HexColor(col), lw=0.3); T(x + 52, yy, lab, 8.5); yy += 22
        T(x + 14, yy + 6, f"white: {HO_W} from white face bend, pitch ~300", 8, color=K.GREY, auto_red=False)
        T(x + 14, yy + 18, f"blue: SIDE returns only, {HO_B} from bend, ~400", 8, color=K.GREY, auto_red=False)
        T(x + 14, yy + 30, "rivets: L leg centre, pitch ~300", 8, color=K.GREY, auto_red=False)
    rows, md = bom(p)
    band(p.short + " - sections, details", sheet, "FIXINGS", sec, rows, md, "1:2 / 1:3.5" if p.rib else "1:2 / 1:5 / 1:6.5")
    save(f"{OUT}/{p.key}_2_SEC.pdf")


def flange_plan(p, x0, y0):
    """DETAIL H - įėjimo pilono flanšas (planas) 1:5 + klausimai užsakovui"""
    k = MM / 5
    F, FT_ = p.FL, p.FLT
    ox, oy = x0 + 40, y0 + 24
    K.set_view(True)
    rect(ox, oy, F * k, F * k, fill=GREYF, lw=0.3)
    lx = F / 2 - (p.FAX - p.FX0)                                 # kojos padėtis flanše (ašis 25 nuo korpuso krašto, koja 3..63)
    rect(ox + (F / 2 - (p.FAX - p.FX0)) * k, oy + (F / 2 - FR / 2) * k, FR * k, FR * k, fill=AL, lw=0.3)
    K.set_view(False)
    HD, HP = 14, 237                                             # rev C (Rytis 2026-10-13): 4 x Ø14, 237 x 237 tarp skylių
    e_ = (F - HP) / 2
    for a in (e_, F - e_):
        for b in (e_, F - e_):
            K.circle(ox + a * k, oy + b * k, HD / 2 * k, fill=white, stroke=black, lw=0.4)
            K.centerline(ox + a * k - 5, oy + b * k, ox + a * k + 5, oy + b * k); K.centerline(ox + a * k, oy + b * k - 5, ox + a * k, oy + b * k + 5)
    hchain(oy - 16, [ox, ox + e_ * k, ox + (F - e_) * k, ox + F * k], [oy + e_ * k] * 4, [f"{e_:g}", f"{HP}", f"{e_:g}"], DIM)
    vchain(ox + F * k + 16, [oy, oy + e_ * k, oy + (F - e_) * k, oy + F * k], [ox + (F - e_) * k] * 4, [f"{e_:g}", f"{HP}", f"{e_:g}"], DIM)
    T(ox + e_ * k + 7, oy + e_ * k + 14, f"4 x Ø{HD}", 8, auto_red=False)
    K.centerline(ox + F / 2 * k, oy - 6, ox + F / 2 * k, oy + F * k + 6); K.centerline(ox - 6, oy + F / 2 * k, ox + F * k + 6, oy + F / 2 * k)
    hdim(ox, ox + F * k, oy - 40, f"{F}", oy, oy, DIM)
    vchain(ox - 16, [oy, oy + F * k], [ox] * 2, [f"{F}"], DIM)
    hchain(oy + F * k + 14, [ox, ox + (F / 2 - (p.FAX - p.FX0)) * k, ox + F / 2 * k], [oy + F * k] * 3, [f"{F / 2 - (p.FAX - p.FX0):.0f}", f"{p.FAX - p.FX0:.0f}"], DIM)
    T(ox + F * k + 70, oy + F * k / 2 - 10, f"Alu 6082-T6, t = {FT_}", 8, auto_red=False)
    T(ox + F * k + 70, oy + F * k / 2 + 2, "leg 60x60x3 welded", 8, color=K.GREY, auto_red=False)
    T(ox + F * k + 70, oy + F * k / 2 + 12, f"4 holes Ø{HD}, {HP} x {HP} (existing anchors)", 8, color=K.GREY, auto_red=False)
    T(ox + F * k + 70, oy + F * k / 2 + 22, "flange axis = 1000 between flanges", 8, color=K.GREY, auto_red=False)
    view_title(ox + F * k / 2, oy + F * k + 40, "DETAIL H - BASE FLANGE x2 (plan)", "SCALE 1:5")
    # klausimai užsakovui
    qx, qy = VX0 + 440, y0 + 34
    qs = ["QUESTION TO CLIENT (CEOS) - base flanges:",
          "Level difference left / right (long leg +60 assumed)?",
          f"Anchor holes confirmed: 4 x Ø{HD}, {HP} x {HP}."]
    hq = 12 * len(qs) + 10
    rect(qx - 6, qy - 4, 270, hq, stroke=RED, lw=1.0)
    for i, q in enumerate(qs):
        T(qx, qy + 10 + i * 12, q, 8.5 if i == 0 else 8, font="FB" if i == 0 else "F", color=RED if i == 0 else black, auto_red=False, fit=258, fit_min=8)


def beam_plan(p, x0, y0):
    """DETAIL H - pagrindo balkis 80x40x4 (planas) 1:5, 4 skylės šachmatine tvarka"""
    k = MM / 5
    L_ = p.FW
    ox, oy = x0 + 30, y0 + 30
    K.set_view(True)
    rect(ox, oy, L_ * k, 80 * k, fill=AL, lw=0.3)
    for xl in (0, L_ - FR):
        rect(ox + xl * k, oy + 10 * k, FR * k, FR * k, lw=0.3, dash=([2, 1.2], 0))
    K.set_view(False)
    for hx, hz in p.BH:
        cx, cy = ox + hx * k, oy + (40 - hz) * k
        K.circle(cx, cy, 15 * k, fill=HexColor("#8C8C8C"), stroke=black, lw=0.3)
        K.circle(cx, cy, 9 * k, fill=white, stroke=black, lw=0.3)
        K.centerline(cx - 14, cy, cx + 14, cy); K.centerline(cx, cy - 14, cx, cy + 14)
    xs = [ox] + [ox + hx * k for hx, _ in p.BH] + [ox + L_ * k]
    vals = [0] + [hx for hx, _ in p.BH] + [L_]
    hchain(oy - 12, xs, [oy] * len(xs), [f"{b - a:.0f}" for a, b in zip(vals[:-1], vals[1:])], DIM)
    hdim(ox, ox + L_ * k, oy - 28, f"{L_}", oy - 14, oy - 14, DIM)
    vchain(ox + L_ * k + 14, [oy, oy + 20 * k, oy + 60 * k, oy + 80 * k], [ox + L_ * k] * 4, ["20", "40", "20"], DIM)
    T(ox + 4, oy + 80 * k + 14, "legs 60x60x3 (dashed) welded on top of the beam", 8, color=K.GREY, auto_red=False)
    for i_, tx_ in enumerate([f"Base beam Alu 6060-T66 rect. tube 80x40x4, L {L_}, welded to legs; painted RAL 5022.",
                              "4 holes staggered, D30 through both walls; sleeve Alu tube D30/D18 L40 welded top + bottom",
                              "(bolt clamps on the sleeve, not on the 4 mm wall). Anchors 4 x M16 A4 chemical, hef >= 125,",
                              "C20/25 min., edge >= 100; torque per anchor manufacturer. Wind MEd 2.5 kNm -> T ~ 22 kN / anchor."]):
        T(ox, oy + 80 * k + 30 + i_ * 10, tx_, 8, color=RED if i_ == 3 else black, auto_red=False)
    view_title(ox + L_ * k / 2, oy + 80 * k + 86, "DETAIL H - BASE BEAM (plan)", "SCALE 1:5")


def frame_cut(S, p, X1, Y0, Y1):
    """rėmo fragmentas: kairė vertikalė (+ ilga koja) ir skersiniai iki X1, aukštis Y0..Y1"""
    yb = -p.LONG if Y0 < 0 else max(Y0, -p.LONG)
    S.box((p.FX0, yb, -FR / 2), (FR, 0, 0), (0, min(Y1, p.FY1) - yb, 0), (0, 0, FR), AL)
    for yy in p.RAILS:
        if yy + FR > Y0 and yy < Y1:
            S.box((p.FX0 + FR, yy, -FR / 2), (X1 - p.FX0 - FR, 0, 0), (0, FR, 0), (0, 0, FR), AL)
    if Y0 < 0:
        if p.legs == "ext":
            S.box((p.FAX - p.FL / 2, -p.LONG - p.FLT, -p.FL / 2), (p.FL, 0, 0), (0, p.FLT, 0), (0, 0, p.FL), GREYF)
        else:
            bw, bd, bt = p.BP
            S.box(((p.W - bw) / 2, -p.LONG - bt, -bd / 2), (X1 - (p.W - bw) / 2, 0, 0), (0, bt, 0), (0, 0, bd), p.PLC)


# ======================================================================== išklotinės
def flat_blue(p, sheet):
    begin(f"Thales_{p.key}_BLUE", 8)
    n = 15; s_ = MM / n
    W, Hh = p.W, p.HB
    fw, fh = W * s_, Hh * s_
    fx = VX0 + 120; fy = VY0 + TB * s_ + 40
    K.set_view(True)
    rect(fx, fy, fw, fh, fill=BLUE, lw=0.3)
    rect(fx, fy - TB * s_, fw, TB * s_, fill=BLUE, lw=0.3)
    rect(fx - TB * s_, fy, TB * s_, fh, fill=BLUE, lw=0.3)
    rect(fx + fw, fy, TB * s_, fh, fill=BLUE, lw=0.3)
    if p.rib:
        rect(fx + NOTCH * s_, fy + fh, (W - 2 * NOTCH) * s_, p.rib * s_, fill=BLUE, lw=0.3)
    K.set_view(False)
    for (a, b, c_, d) in [(fx, fy, fx + fw, fy), (fx, fy, fx, fy + fh), (fx + fw, fy, fx + fw, fy + fh)] + ([(fx + NOTCH * s_, fy + fh, fx + fw - NOTCH * s_, fy + fh)] if p.rib else []):
        line(a, b, c_, d, 0.3, RED, dash=([3, 2], 0))
    # skylės: mėlyna -> rėmas (šonuose ir viršuje), kniedės L (priekyje)
    for q in p.b_side_holes()[2]:
        yv = fy + fh - q * s_
        K.circle(fx - HO_B * s_, yv, 1.0, fill=white, stroke=black, lw=0.25)
        K.circle(fx + fw + HO_B * s_, yv, 1.0, fill=white, stroke=black, lw=0.25)
    for q in p.b_top_holes()[2]:
        K.circle(fx + q * s_, fy - HO_B * s_, 1.0, fill=white, stroke=black, lw=0.25)
    for q in p.rivets_v()[2]:
        yv = fy + fh - (PL + 5 + q) * s_
        K.circle(fx + 16 * s_, yv, 0.7, fill=white, stroke=None)
        K.circle(fx + fw - 16 * s_, yv, 0.7, fill=white, stroke=None)
    nrh = max(2, round(p.LH / 300) + 1)
    for i in range(nrh):
        xq = 4 + LP + 30 + i * (p.LH - 60) / (nrh - 1)
        K.circle(fx + xq * s_, fy + fh - (PL + 5 + 16) * s_, 0.7, fill=white, stroke=None)
    # matmenys
    hdim(fx, fx + fw, fy - TB * s_ - 14, f"{W}", fy - TB * s_, fy - TB * s_, DIM)
    hdim(fx - TB * s_, fx + fw + TB * s_, fy - TB * s_ - 32, f"{W + 2 * TB}", fy, fy, DIM)
    if p.rib:
        vchain(fx - TB * s_ - 16, [fy - TB * s_, fy, fy + fh, fy + fh + p.rib * s_], [fx - TB * s_] * 4, [f"{TB}", f"{Hh}", f"{p.rib}"], DIM)
    else:
        vchain(fx - TB * s_ - 16, [fy - TB * s_, fy, fy + fh], [fx - TB * s_] * 3, [f"{TB}", f"{Hh}"], DIM)
    vchain(fx - TB * s_ - 44, [fy, fy + fh], [fx - TB * s_] * 2, [f"{Hh}"], DIM)
    if p.rib:
        hchain(fy + fh + p.rib * s_ + 16, [fx, fx + NOTCH * s_, fx + fw - NOTCH * s_, fx + fw], [fy + fh] * 4, [f"{NOTCH}", f"{W - 2 * NOTCH} (rib {p.rib})", f"{NOTCH}"], DIM)
    else:
        T(fx + fw / 2, fy + fh + 14, "bottom open - no fold (covers base plate down to paving)", 8, color=RED, align="c", auto_red=False)
    ns, ps, _ = p.b_side_holes(); nt, pt_, _ = p.b_top_holes(); nr, pr, _ = p.rivets_v()
    T(fx + fw / 2, fy + fh / 2 - 10, f"BLUE TRAY {W} x {Hh} x {TB}", 10, align="c", color=white, auto_red=False)
    T(fx + fw / 2, fy + fh / 2 + 6, "RAL 5022, face out", 8, align="c", color=white, auto_red=False)
    view_title(fx + fw / 2, fy + fh + p.rib * s_ + 46, "BLUE TRAY - FLAT PATTERN, NOMINAL (2 per pylon)", f"SCALE 1:{n}")
    # DETAIL - apatinis kampas 1:3
    c3 = MM / 3 if p.rib else MM / 3
    cx = fx + fw + TB * s_ + 140; cy = VY0 + 40
    CW, CH = 150, 130
    ox_, oy_ = cx + TB * c3, cy
    K.set_view(True)
    rect(ox_, oy_, CW * c3, CH * c3, fill=BLUE, lw=0.3)
    rect(ox_ - TB * c3, oy_, TB * c3, CH * c3, fill=BLUE, lw=0.3)
    if p.rib:
        rect(ox_ + NOTCH * c3, oy_ + CH * c3, (CW - NOTCH) * c3, p.rib * c3, fill=BLUE, lw=0.3)
    K.set_view(False)
    line(ox_, oy_, ox_, oy_ + CH * c3, 0.3, RED, dash=([3, 2], 0))
    if p.rib:
        line(ox_ + NOTCH * c3, oy_ + CH * c3, ox_ + CW * c3, oy_ + CH * c3, 0.3, RED, dash=([3, 2], 0))
    K.circle(ox_ - HO_B * c3, oy_ + CH * c3 - 100 * c3, 1.6, fill=white, stroke=black, lw=0.3)
    if p.rib:
        hchain(oy_ + CH * c3 + p.rib * c3 + 14, [ox_ - TB * c3, ox_, ox_ + NOTCH * c3], [oy_ + CH * c3] * 3, [f"{TB}", f"{NOTCH}"], DIM)
        vchain(ox_ + CW * c3 + 14, [oy_ + CH * c3, oy_ + (CH + p.rib) * c3], [ox_ + CW * c3] * 2, [f"{p.rib}"], DIM)
    else:
        hchain(oy_ + CH * c3 + 14, [ox_ - TB * c3, ox_], [oy_ + CH * c3] * 2, [f"{TB}"], DIM)
    vchain(ox_ - TB * c3 - 14, [oy_ + CH * c3 - 100 * c3, oy_ + CH * c3], [ox_ - TB * c3] * 2, ["100"], DIM)
    hdim(ox_ - TB * c3, ox_ - HO_B * c3, oy_ - 10, f"{TB - HO_B}", oy_, oy_, DIM, small_side="l")
    T(ox_ + 4, oy_ + CH * c3 + p.rib * c3 + 36, ("notch at leg: side return full height, bottom rib only between legs" if p.rib else "bottom edge straight, no fold"), 8, color=K.GREY, auto_red=False)
    view_title(ox_ + (CW - TB) * c3 / 2, oy_ + CH * c3 + p.rib * c3 + 58, "DETAIL F - BOTTOM CORNER (flat)", "SCALE 1:3")
    # pastabos
    nx = cx; ny = oy_ + CH * c3 + p.rib * c3 + 90
    for s2 in [(f"- Alu 2 mm, RAL 5022 satin. Sides + top folded {TB}, bottom rib {p.rib} between legs." if p.rib else f"- Alu 2 mm, RAL 5022 satin. Sides + top folded {TB}, bottom open (no fold)."),
               f"- Holes for csk screws into frame: sides {HO_B} from bend, from 100, {ns} x {ps:.0f};",
               f"  top {HO_B} from bend, {nt} x {pt_:.0f}.",
               f"- Rivet holes for L 25 (centre of L leg, 16 from edge): {nr} x {pr:.0f} per L.",
               "- Corners: sides + top welded and ground (CEOS: pliees, soudees).",
               "- Nominal outside sizes; bend deduction (R2, K 0.44) in the DXF stage."]:
        T(nx, ny, s2, 8.5, fit=VX1 - nx - 4, fit_min=8); ny += 12

    def sec(x, y, w, h):
        T(x + w / 2, y + h / 2, "flat pattern - nominal", 9, align="c", color=K.GREY, auto_red=False)
    rows = [[2, f"Blue tray {W}x{Hh}x{TB}" + (f", rib {p.rib}" if p.rib else ", open bottom"), "Alu 2 mm folded", "RAL 5022", f"2 pcs. x {p.qty} = {2 * p.qty} pcs."],
            ["", f"Holes csk -> frame: sides {2 * (ns + 1)}, top {nt + 1}", "", "", "D ___ csk"],
            ["", f"Rivet holes L: {2 * (nr + 1) + nrh}", "", "", "D ___"],
            ["", "Weld + grind 2 top corners", "", "", "-"]]
    md = [["Flat (nominal)", f"{W + 2 * TB} x {Hh + TB + p.rib}"]] + ([["Notch", f"{NOTCH} at each leg"], ["Rib", f"{p.rib} between legs"]] if p.rib else [["Bottom", "open, no fold"]]) + [["Status", "nominal, DXF next"]]
    band(p.short + " - blue tray flat", sheet, "NOTE", sec, rows, md, f"1:{n} / 1:3")
    save(f"{OUT}/{p.key}_3_BLUE.pdf")


def flat_white(p, sheet):
    begin(f"Thales_{p.key}_WHITE", 8)
    n = 15; s_ = MM / n
    Wp, Hp = p.W, p.OVH
    TOP, BOT, SIDE, EAR_H = 70, TW, TW, 30
    fw, fh = Wp * s_, Hp * s_
    fx = VX0 + 120; fy = VY0 + TOP * s_ + 44
    K.set_view(True)
    rect(fx, fy, fw, fh, fill=WHITE_, lw=0.3)
    rect(fx, fy - TOP * s_, fw, TOP * s_, fill=WHITE_, lw=0.3)
    rect(fx, fy + fh, fw, BOT * s_, fill=WHITE_, lw=0.3)
    for sg in (-1, 1):
        x0 = fx - SIDE * s_ if sg < 0 else fx + fw
        rect(x0, fy + EAR_H * s_, SIDE * s_, fh - EAR_H * s_, fill=WHITE_, lw=0.3)
        xe = fx - EAR * s_ if sg < 0 else fx + fw
        rect(xe, fy, EAR * s_, EAR_H * s_, fill=WHITE_, lw=0.3)
    K.set_view(False)
    for (a, b, c_, d) in [(fx, fy, fx + fw, fy), (fx, fy + fh, fx + fw, fy + fh), (fx, fy, fx, fy + fh), (fx + fw, fy, fx + fw, fy + fh)]:
        line(a, b, c_, d, 0.3, RED, dash=([3, 2], 0))
    ns, ps, pts = p.w_side_holes(); nb, pb, ptb = p.w_bot_holes()
    for q in pts:
        yv = fy + fh - q * s_
        K.circle(fx - HO_W * s_, yv, 1.0, fill=white, stroke=black, lw=0.25); K.circle(fx + fw + HO_W * s_, yv, 1.0, fill=white, stroke=black, lw=0.25)
    for q in ptb:
        K.circle(fx + q * s_, fy + fh + HO_W * s_, 1.0, fill=white, stroke=black, lw=0.25)
    for xe in (fx - EAR * s_ + 20 * s_, fx + fw + 50 * s_):
        for yy in (fy + 18 * s_,):
            K.circle(xe, yy, 1.0, fill=white, stroke=black, lw=0.25)
    hdim(fx, fx + fw, fy - TOP * s_ - 14, f"{Wp}", fy - TOP * s_, fy - TOP * s_, DIM)
    hdim(fx - EAR * s_, fx + fw + EAR * s_, fy - TOP * s_ - 32, f"{Wp + 2 * EAR}", fy, fy, DIM)
    vchain(fx - EAR * s_ - 16, [fy - TOP * s_, fy, fy + EAR_H * s_, fy + fh, fy + fh + BOT * s_], [fx - EAR * s_] * 5, [f"{TOP}", "30", f"{Hp - 30}", f"{BOT}"], DIM)
    vchain(fx - EAR * s_ - 44, [fy, fy + fh], [fx - EAR * s_] * 2, [f"{Hp}"], DIM)
    hchain(fy + fh + BOT * s_ + 16, [fx - SIDE * s_, fx, fx + fw, fx + fw + SIDE * s_], [fy + fh] * 4, [f"{SIDE}", "", f"{SIDE}"], DIM)
    T(fx + fw / 2, fy + fh / 2, f"WHITE TRAY {Wp} x {Hp}", 10, align="c", color=K.GREY, auto_red=False)
    T(fx + fw / 2, fy + fh / 2 + 14, "RAL 9016, decal side", 8, align="c", color=K.GREY, auto_red=False)
    view_title(fx + fw / 2, fy + fh + BOT * s_ + 46, f"WHITE TRAY - FLAT PATTERN, NOMINAL ({p.sides} per pylon)", f"SCALE 1:{n}")
    # DETAIL G - viršutinis kampas 1:3
    c3 = MM / 3
    cx0 = fx + fw + EAR * s_ + 150; cy0 = VY0 + 50
    CW, CH = 150, 130
    ox_ = cx0 + EAR * c3; oy_ = cy0 + TOP * c3
    K.set_view(True)
    rect(ox_, oy_, CW * c3, CH * c3, fill=WHITE_, lw=0.3)
    rect(ox_, oy_ - TOP * c3, CW * c3, TOP * c3, fill=WHITE_, lw=0.3)
    rect(ox_ - EAR * c3, oy_, EAR * c3, EAR_H * c3, fill=WHITE_, lw=0.3)
    rect(ox_ - SIDE * c3, oy_ + EAR_H * c3, SIDE * c3, (CH - EAR_H) * c3, fill=WHITE_, lw=0.3)
    K.set_view(False)
    line(ox_, oy_, ox_ + CW * c3, oy_, 0.3, RED, dash=([3, 2], 0)); line(ox_, oy_, ox_, oy_ + CH * c3, 0.3, RED, dash=([3, 2], 0))
    K.circle(ox_ - 50 * c3, oy_ + 18 * c3, 1.6, fill=white, stroke=black, lw=0.3)
    K.circle(ox_ - HO_W * c3, oy_ + (EAR_H + 50) * c3, 1.6, fill=white, stroke=black, lw=0.3)
    hchain(oy_ - TOP * c3 - 12, [ox_ - EAR * c3, ox_ - 50 * c3, ox_], [oy_] * 3, ["20", "50"], DIM)
    vchain(ox_ - EAR * c3 - 12, [oy_ - TOP * c3, oy_, oy_ + 18 * c3, oy_ + EAR_H * c3], [ox_ - EAR * c3] * 4, [f"{TOP}", "18", "12"], DIM)
    hchain(oy_ + CH * c3 + 14, [ox_ - SIDE * c3, ox_ - HO_W * c3, ox_], [oy_ + CH * c3] * 3, [f"{SIDE - HO_W}", f"{HO_W}"], DIM)
    T(ox_ + CW * c3 / 2, oy_ + CH * c3 / 2, "front face", 8, align="c", color=K.GREY, auto_red=False)
    view_title(ox_ + (CW - EAR) * c3 / 2, oy_ + CH * c3 + 44, "DETAIL G - TOP CORNER (flat)", "SCALE 1:3")
    nx = cx0; ny = oy_ + CH * c3 + 76
    for s2 in ["- Alu 2 mm, RAL 9016 satin. Sides + bottom 30; top 70 (inverted L over blue top);",
               "  ears 70 x 30 close the side above the blue body; ear + top return welded at corner.",
               f"- Csk holes into L 25: sides / bottom {HO_W} from bend, from 50, sides {ns} x {ps:.0f}, bottom {nb} x {pb:.0f};",
               "  ears: 1 hole each into corner L 25x25x2 x 30 on blue top.",
               "- Front + back top returns meet at the pylon centre (butt joint)." if p.sides == 2 else "- Top return 70 ends at body centre; back half of blue top stays blue.",
               "- Nominal outside sizes; bend deduction (R2, K 0.44) in the DXF stage."]:
        T(nx, ny, s2, 8.5, fit=VX1 - nx - 4, fit_min=8); ny += 12

    def sec(x, y, w, h):
        T(x + w / 2, y + h / 2, "flat pattern - nominal", 9, align="c", color=K.GREY, auto_red=False)
    rows = [[4, f"White tray {Wp}x{Hp}, top 70, ears", "Alu 2 mm folded", "RAL 9016", f"{p.sides} pcs. x {p.qty} = {p.sides * p.qty} pcs."],
            ["", f"Csk holes: sides {2 * (ns + 1)}, bottom {nb + 1}, ears 2", "", "", "D ___ csk"],
            ["", "Weld + grind ear / top return corners", "", "", "2 per tray"]]
    md = [["Flat (nominal)", f"{Wp + 2 * EAR} x {Hp + TOP + BOT}"], ["Ears", "70 x 30"], ["Status", "nominal, DXF next"]]
    band(p.short + " - white tray flat", sheet, "NOTE", sec, rows, md, f"1:{n} / 1:3")
    save(f"{OUT}/{p.key}_4_WHITE.pdf")


def pmma_sheet(sheet):
    """Stalinis planas PMMA 297 x 210, termoformuotas L, priekis pakreiptas atgal 10 deg (stabilumas + matomumas)"""
    begin("Thales_PMMA", 8)
    Wp, Hp, tp, FOOT, ANG, Rb = 297, 210, 4, 80, 10, 10
    clip = (699.3, 276.6, 1120.2, 574.2)            # rev C: tikslus kliento maketo 297 x 210 rėmas (buvo nukirpta / pastumta)
    k = MM / 2
    fx, fy = VX0 + 70, VY0 + 40
    fw, fh = Wp * k, Hp * k * math.cos(math.radians(ANG))
    # FRONT VIEW (projekcija - aukštis sutrumpėja dėl pasvirimo)
    rect(fx, fy, fw, fh, fill=HexColor("#F4F6F8"), lw=0.3)
    draw_client(2, clip, fx, fy, fw, fh)
    hdim(fx, fx + fw, fy - 12, f"{Wp}", fy, fy, DIM)
    vchain(fx - 16, [fy, fy + fh], [fx] * 2, [f"{Hp * math.cos(math.radians(ANG)):.0f}"], DIM)
    T(fx + fw / 2, fy + fh + 14, f"print area {Wp} x {Hp} (true size on the inclined face)", 8, color=K.GREY, align="c", auto_red=False)
    view_title(fx + fw / 2, fy + fh + 40, "FRONT VIEW", "SCALE 1:2")
    # SIDE VIEW (LEFT) 1:2: žiūrovas kairėje; pėda eina atgal (į dešinę), priekis pasviręs atgal 10 deg
    sx, sy = fx + fw + 90, fy + fh            # apatinis priekinis kampas (žemė)
    a = math.radians(ANG)
    ux, uy = math.sin(a), -math.cos(a)        # priekio kryptis aukštyn (puslapio koord.)
    nx_, ny_ = math.cos(a), math.sin(a)       # normalė į galą
    pts_o, pts_i = [], []
    # išorinis kontūras: pėdos apačia nuo užpakalio iki lenkimo, lenkimas, priekio išorė
    K.set_view(True)
    face_len = Hp
    top_o = (sx + face_len * k * ux, sy + face_len * k * uy)
    prof = [(sx + (FOOT) * k, sy), (sx, sy), top_o,
            (top_o[0] + tp * k * nx_, top_o[1] + tp * k * ny_), (sx + tp * k * nx_ + 0, sy - tp * k), (sx + FOOT * k, sy - tp * k)]
    poly(prof, fill=HexColor("#DDE6EE"), lw=0.3)
    K.set_view(False)
    line(sx - 40, sy, sx + FOOT * k + 40, sy, 0.4, black, dash=([6, 2], 0))
    T(sx + FOOT * k + 44, sy + 3, "desk", 8, color=K.GREY, auto_red=False)
    # matmenys
    hdim(sx, sx + FOOT * k, sy + 16, f"{FOOT}", sy, sy, DIM)
    hdim(sx, top_o[0], top_o[1] - 14, f"{face_len * math.sin(a):.0f}", sy, top_o[1], DIM)
    vchain(sx - 16, [top_o[1], sy], [sx] * 2, [f"{face_len * math.cos(a):.0f}"], DIM)
    # kampo žymė
    r_ = 36
    K.c.saveState(); K.c.setLineWidth(0.3)
    K.c.arc(sx - r_, K.Y(sy) - r_, sx + r_, K.Y(sy) + r_, 90 - ANG, ANG); K.c.restoreState()
    line(sx, sy, sx, sy - r_ - 6, 0.25, K.EXT, dash=([3, 2], 0))
    T(sx + 10, sy - r_ - 6, f"{ANG}°", DIM, auto_red=False)                      # rev C: kampas - matmuo, 12 pt
    tag(sx + tp * k * 0.5 + 2, sy - 3, sx + 100, sy - 18, f"bend R {Rb} (inside), thermoformed", 8)       # rev C: ne ant priekio vaizdo
    T(sx, sy + 40, f"face leans back {ANG}°: centre of gravity over the foot (stable),", 8, color=K.GREY, auto_red=False)
    T(sx, sy + 50, "better reading angle for a standing visitor.", 8, color=K.GREY, auto_red=False)
    view_title(sx + 40, sy + 72, "SIDE VIEW (LEFT)", "SCALE 1:2")
    # DETAIL B - sluoksniai
    bx, by = VX0 + 70, fy + fh + 90
    kk = 8
    rect(bx, by, 140, tp * kk, fill=HexColor("#DDE6EE"), lw=0.3)
    rect(bx, by + tp * kk, 140, 0.6 * kk, fill=HexColor("#9AC4E8"), lw=0.3)
    rect(bx, by + tp * kk + 0.6 * kk, 140, 0.6 * kk, fill=white, lw=0.3)
    leaders([(1, bx + 70, by + tp * kk / 2), (2, bx + 100, by + tp * kk + 0.3 * kk), (3, bx + 120, by + tp * kk + 0.9 * kk)], bx + 180, "r", 14)
    T(bx, by - 8, "viewer side", 8, color=K.GREY, auto_red=False)
    view_title(bx + 70, by + tp * kk + 1.2 * kk + 40, "DETAIL B - LAYERS", "NOT TO SCALE")
    # 3D
    S = r3d.Scene(yaw=-35, pitch=18)
    ca, sa = math.cos(a), math.sin(a)
    S.box((0, 0, 0), (Wp, 0, 0), (0, tp, 0), (0, 0, -FOOT), HexColor("#DDE6EE"))
    S.box((0, 0, 0), (Wp, 0, 0), (0, Hp * ca, -Hp * sa), (0, -tp * sa * 0 + tp * sa, tp * ca), HexColor("#DDE6EE"))
    x3, y3 = sx + FOOT * k + 120, VY0 + 20
    w3, h3 = VX1 - x3, VY1 - 30 - y3
    S.render((x3, y3, w3, h3))
    c_ = fitz.Rect(clip); sx_, sy_ = Wp / c_.width, Hp / c_.height
    tf = lambda px, py: S.V.S((px - c_.x0) * sx_, (Hp - (py - c_.y0) * sy_) * ca + tp * sa, -(Hp - (py - c_.y0) * sy_) * sa + tp * ca)
    tl, tr, bl = tf(c_.x0, c_.y0), tf(c_.x1, c_.y0), tf(c_.x0, c_.y1)
    place_img(2, clip, tl, tr, bl, K.HAIR)
    view_title(x3 + w3 / 2, VY1 - 6, "3D VIEW", "ILLUSTRATIVE - NOT TO SCALE")
    def sec(x, y, w, h):
        items = [("PMMA clear 4 mm", "#DDE6EE", "cast, polished edges, thermoformed"),
                 ("Print on clear film", "#9AC4E8", "mirrored, applied to the rear face"),
                 ("White ink underlay", "#FFFFFF", "printed behind the graphic (opacity)")]
        yy = y + 12
        for i, (lab, col, txt) in enumerate(items):
            rect(x + 12, yy, 40, 26, fill=HexColor(col), lw=0.4)
            balloon(x + 32, yy + 13, i + 1)
            T(x + 60, yy + 11, lab, 9, font="FB", fit=w - 66, fit_min=8)
            T(x + 60, yy + 22, txt, 8, color=K.GREY, fit=w - 66, fit_min=8)
            yy += 34
    rows = [[1, f"PMMA clear {tp} mm, {Wp}x{Hp} + foot {FOOT}", "PMMA cast, clear", "-", f"1 pcs. / {Wp * (Hp + FOOT) / 1e6:.3f} m²"],
            [2, "Digital print on clear film, mirrored", "Clear PVC / PU film", "print", f"{Wp} x {Hp}"],
            [3, "White ink underlay (in print)", "-", "-", "-"]]
    md = [["Quantity", "1 pcs."], ["Face", f"{Wp} x {Hp}, leans back {ANG}°"], ["Foot", f"{FOOT}, bend R {Rb}"],
          ["Material", f"PMMA clear {tp} mm (CEOS: 5 mm)"], ["Graphics", "print on clear film, rear face"],
          ["Weight (calc.)", f"≈ {Wp * (Hp + FOOT) * tp * 1.19 / 1e6:.1f} kg"]]
    band("Reception desk plan, PMMA 297 x 210", sheet, "MATERIAL", sec, rows, md, "1:2")
    save(f"{OUT}/PMMA_5.pdf")


if __name__ == "__main__":
    E = Pyl("ENT", 1050, 2530, 2, "ext", 1, "Entrance pylon 1050 x 2530, double-sided")
    TB = 43                                    # Rytis 2026-10-11: balkis 80 + laisvumai -> mėlyna 86 (2 x 43)
    B = Pyl("BLD", 600, 2130, 1, "int", 4, "Building pylons 600 x 2130, single-sided, x4")
    dec = [("ZENITH", 9, (354.4, 205.1, 467.8, 569.8), 431, 827), ("HORIZON", 9, (498.5, 205.1, 611.9, 569.8), 450, 1117),
           ("BOREAL", 9, (646.9, 205.1, 760.3, 569.8), 425, 810), ("ATRIUM", 9, (786.3, 205.1, 899.7, 569.8), 437, 1060)]
    which = sys.argv[1:] or ["all"]
    NS = "5"
    if "all" in which or "E" in which:
        TB = 40; EAR = TW + TB                 # dvipusis: baltas viršus iki vidurio (70)
        ga(E, f"1 / {NS}", (1, (177.3, 225.6, 375.7, 665.9)))
        sections(E, f"2 / {NS}")
    if "all" in which or "B" in which:
        TB = 43; EAR = TW + 2 * TB             # rev C (Rytis 2026-10-13): vienpusis - baltas viršus iki pilono galo (116)
        ga(B, f"3 / {NS}", (9, (354.4, 205.1, 467.8, 569.8)), decals=dec)
        sections(B, f"4 / {NS}")
    if "all" in which or "P" in which:
        pmma_sheet(f"5 / {NS}")
    print("OVERFLOW:", K.OVERFLOW)
