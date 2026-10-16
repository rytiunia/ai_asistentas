"""Ne-iškabų lapai (back plate, spauda, plėvelės, portalas) etaloniniu iškabų techninio lapo stiliumi (lapas_core)."""
import sys, math, tempfile, json
sys.path.insert(0, '/home/claude/v9/scripts')
import lapas_core as K
from lapas_core import T, line, rect, poly, hdim, vchain, hchain, leader, view_title, balloon, MM
from reportlab.lib.colors import HexColor, white, black, Color
import pymupdf as fitz
from shapely.geometry import box as sbox, Polygon
from shapely.ops import unary_union

CLIENT = "BrandFactory"
DATE = "2026-10-08"
VX0, VY0 = K.IX0 + 8, K.IY0 + 6
VX1 = K.IX1 - 8
VY1 = K.VIEW_BOT - 4
OVER = []
RALC = lambda c: HexColor(K.ralhex(c))
SV = json.load(open('/home/claude/w/assets/svoris.json'))


def over(*o):
    OVER.append(o)


def begin(file_code, n_rows=10):
    global TMP, VY1
    OVER.clear()
    K.set_band(n_rows)
    VY1 = K.VIEW_BOT - 4
    TMP = tempfile.mktemp(suffix=".pdf")
    K.init(TMP, file_code)
    K.frame()


def band(spec, first_title, first_fn, bom, md, scales):
    BY0 = K.BAND_Y; BH = K.IY1 - BY0                 # v9: vientisas blokas iki rėmelio, be tarpų
    W_P6, W_MD, W_TB = 214, 172, 272
    X_P6 = K.IX0; X_TB = K.IX1 - W_TB; X_MD = X_TB - W_MD
    X_BOM = X_P6 + W_P6; W_BOM = X_MD - X_BOM
    K.header(X_P6, BY0, W_P6, first_title)
    rect(X_P6, BY0 + 12, W_P6, BH - 12, lw=0.6)
    first_fn(X_P6, BY0 + 12, W_P6, BH - 12)
    K.bom_table(X_BOM, BY0, W_BOM, BH, bom, title="BILL OF MATERIALS  (per 1 pcs.)")
    K.main_data(X_MD, BY0, W_MD, BH, md, lab_w=58)
    sp = dict(spec); sp["title"] = "SPAR order 225960 - " + sp["title"]; sp.setdefault("client", CLIENT); sp.setdefault("drawing_no", "SPAR order 225960"); sp.setdefault("date", DATE); sp.setdefault("company", "BrandFactory")
    sp.setdefault("rev", "A"); sp.setdefault("order_no", "ALT0000_00.00_RS")
    K.title_block(X_TB, W_TB, sp, scales)


def finish(out):
    K.save(out)
    if OVER:
        d = fitz.open(out); p = d[0]
        for o in OVER:
            if o[0] == "pdf":
                _, r, src, pno, clip = o
                # v307: tik iškarpos objektai (K.clip_source) - faile ne visas šaltinio puslapis
                p.show_pdf_page(fitz.Rect(r), K.clip_source(src, pno, clip), 0, clip=fitz.Rect(clip), keep_proportion=False)
            elif o[0] == "rect":
                p.draw_rect(fitz.Rect(o[1]), color=None, fill=(1, 1, 1))
            else:
                _, r, img = o
                p.insert_image(fitz.Rect(r), filename=img, keep_proportion=False)
        d.save(out + ".tmp.pdf", garbage=3, deflate=True); d.close()
        import os; os.replace(out + ".tmp.pdf", out)


# ------------------------------------------------------------------ dalys
def client_paths(src, clip, filt=None):
    """kliento vektoriai (užpildyti) iš clip -> [(subpaths pt, fill)]"""
    p = fitz.open(src)[0]; out = []
    for d in p.get_drawings():
        if d.get("fill") is None or not fitz.Rect(clip).contains(d["rect"]):
            continue
        if filt and not filt(d):
            continue
        out.append((K.drawing_to_subpaths(d, lambda q: q), tuple(d["fill"][:3])))
    return out


def draw_client(paths, clip, x, y, w, h, outline=None):
    """kliento vektorius į stačiakampį (x, y, w, h) - y žemyn"""
    clip = fitz.Rect(clip)
    sx, sy = w / clip.width, h / clip.height
    tf = lambda px, py: (x + (px - clip.x0) * sx, K.Y(y + (py - clip.y0) * sy))
    for sub, f in paths:
        K.draw_shape(sub, tf, fill=Color(*f), stroke=outline, lw=0.1)


def section_backplate(x, y, w, h, edge=40):
    """BACK PLATE - TYPICAL SECTION: folded 2 mm Alu (dangtis), L 30x30x2, varžtas DIN 7504, tvirtinimas į sieną"""
    K.set_view(True)
    s = (h - 40) / 120.0                    # 120 mm aukščio fragmentas
    fx = x + w * 0.62                       # priekio plokštuma
    wall = fx - edge * s * 1.0
    y0, y1 = y + 22, y + h - 16
    t = 2 * s
    # priekis (pjūvis - juodas) + viršutinis užlenkimas į sienos pusę
    rect(fx, y0, t, y1 - y0, fill=black, lw=0.35)
    rect(wall, y0, fx - wall, t, fill=black, lw=0.35)
    line(fx + t + 3, y1 - 6, fx + t + 3 + 0, y1 - 6, 0.3)
    # lūžio linija apačioje
    poly([(fx - 6, y1), (fx - 2, y1 - 3), (fx + 2, y1 + 3), (fx + t + 6, y1)], close=False, lw=0.3)
    # L profilis 30x30x2 (prie sienos, po užlenkimu)
    L = 30 * s; lt = 2 * s
    ly = y0 + t + 0.4
    poly([(wall, ly), (wall + L, ly), (wall + L, ly + lt), (wall + lt, ly + lt), (wall + lt, ly + L), (wall, ly + L)],
         fill=HexColor("#3A3A3A"), lw=0.35)
    # varžtas DIN 7504 per užlenkimą į L
    bx = wall + L * 0.6
    rect(bx - 4, y0 - 3.5, 8, 3.5, fill=HexColor("#6E6E6E"), lw=0.3)
    rect(bx - 1.2, y0, 2.4, t + lt + 6, fill=HexColor("#9A9A9A"), lw=0.25)
    K.centerline(bx, y0 - 6, bx, y0 + t + lt + 10)
    # tvirtinimas į sieną per L vertikalią kojelę
    ay = ly + L * 0.6
    rect(wall - 14, ay - 1.6, 14 + lt + 6, 3.2, fill=HexColor("#9A9A9A"), lw=0.25)
    rect(wall + lt + 2, ay - 4, 3, 8, fill=HexColor("#6E6E6E"), lw=0.3)
    K.centerline(wall - 18, ay, wall + lt + 10, ay)
    K.set_view(False)
    hdim(wall, fx + t, y0 - 10, f"{edge}", y0, y0)
    leader(fx + t / 2, y0 + (y1 - y0) * 0.6, fx + 26, y0 + (y1 - y0) * 0.6, 1)
    leader(wall + lt / 2, ly + L * 0.85, wall - 26, ly + L * 1.2, 2)
    leader(bx, y0 - 2, bx + 30, y0 - 4, 3)
    leader(wall - 10, ay, wall - 26, ay + 8, 4)
    T(x + w / 2, y + h - 5, "1 plate  2 L 30x30x2  3 screw  4 wall fixing", 8, color=K.GREY, align="c", auto_red=False)


def material_block(items):
    """items: [(label, hex, text)]"""
    def fn(x, y, w, h):
        yy = y + 14
        for lab, col, txt in items:
            rect(x + 12, yy, 46, 30, fill=HexColor(col) if col else None, lw=0.4)
            T(x + 66, yy + 12, lab, 9, font="FB", fit=w - 72, fit_min=8)
            T(x + 66, yy + 24, txt, 8, color=K.GREY, fit=w - 72, fit_min=8)
            yy += 40
    return fn


def iso_box(V3, box_xywh, solids):
    """solids: [(shapely geom y-up mm, z0, z1, side, face)]"""
    pts = []
    for g, z0, z1, *_ in solids:
        x0, y0, x1, y1 = g.bounds
        pts += [(x, yv, z) for x in (x0, x1) for yv in (y0, y1) for z in (z0, z1)]
    V3.fit(pts, box_xywh)
    for g, z0, z1, side, face in sorted(solids, key=lambda t: (t[1], V3.depth_key(t[0], (t[1] + t[2]) / 2))):
        V3.solid(g, z0, z1, side, face)
