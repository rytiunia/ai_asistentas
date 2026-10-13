"""Kliento PDF imitacija: tekstas Times New Roman (Liberation Serif - metrikomis identiškas TNR),
kontūrai kreivėmis, 1 pt = 1 mm (spec scale 2.8346). Nurodyto simbolio (W) aukštis = cap_mm."""
import sys
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.boundsPen import BoundsPen
from reportlab.pdfgen import canvas

FONT = sys.argv[5] if len(sys.argv) > 5 else "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
text, out, ref_ch, ref_mm = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])   # ref_ch "LEN" - bendras ilgis
MARGIN = 50

tt = TTFont(FONT)
gs = tt.getGlyphSet()
cmap = tt.getBestCmap()
k = None
if ref_ch != "LEN":
    bp = BoundsPen(gs)
    gs[cmap[ord(ref_ch)]].draw(bp)
    k = ref_mm / (bp.bounds[3] - bp.bounds[1])      # font units -> mm

blob = hb.Blob.from_file_path(FONT)
font = hb.Font(hb.Face(blob))
buf = hb.Buffer()
buf.add_str(text)
buf.guess_segment_properties()
hb.shape(font, buf, {"kern": True, "liga": False})
order = tt.getGlyphOrder()

glyphs, x = [], 0
for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
    rp = RecordingPen()
    gs[order[info.codepoint]].draw(rp)
    glyphs.append((x + pos.x_offset, rp.value))
    x += pos.x_advance

# bendras gabaritas
xs, ys = [], []
for ox, rec in glyphs:
    for op, pts in rec:
        for px, py in pts:
            xs.append(ox + px); ys.append(py)
x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
if k is None:
    k = ref_mm / (x1 - x0)
W, H = (x1 - x0) * k + 2 * MARGIN, (y1 - y0) * k + 2 * MARGIN

c = canvas.Canvas(out, pagesize=(W, H))
# spalva (6 argumentas, hex) - ne pilka, kad stačiakampės raidės (l, I) nebūtų atpažintos kaip kliento bėgeliai
_fh = sys.argv[6] if len(sys.argv) > 6 else "1A1A1A"
c.setFillColorRGB(*[int(_fh[i:i + 2], 16) / 255 for i in (0, 2, 4)])
for ox, rec in glyphs:
    p = c.beginPath()
    T = lambda pt: ((ox + pt[0] - x0) * k + MARGIN, (pt[1] - y0) * k + MARGIN)
    cur = None
    for op, pts in rec:
        if op == "moveTo":
            p.moveTo(*T(pts[0])); cur = pts[0]
        elif op == "lineTo":
            p.lineTo(*T(pts[0])); cur = pts[0]
        elif op == "qCurveTo":
            # TrueType kvadratinės -> kubinės (su numanomais taškais)
            q = list(pts)
            if q[-1] is None:
                q = q[:-1]
            ctrl, end = q[:-1], q[-1]
            seg_start = cur
            for i, cp in enumerate(ctrl):
                e = end if i == len(ctrl) - 1 else ((cp[0] + ctrl[i + 1][0]) / 2, (cp[1] + ctrl[i + 1][1]) / 2)
                c1 = (seg_start[0] + 2 / 3 * (cp[0] - seg_start[0]), seg_start[1] + 2 / 3 * (cp[1] - seg_start[1]))
                c2 = (e[0] + 2 / 3 * (cp[0] - e[0]), e[1] + 2 / 3 * (cp[1] - e[1]))
                p.curveTo(*T(c1), *T(c2), *T(e))
                seg_start = e
            cur = end
        elif op == "curveTo":
            p.curveTo(*T(pts[0]), *T(pts[1]), *T(pts[2])); cur = pts[2]
        elif op in ("closePath", "endPath"):
            p.close()
    c.drawPath(p, fill=1, stroke=0, fillMode=0)   # even-odd: e, o akutės
c.showPage()
c.save()
print(f"{text}: {(x1 - x0) * k:.1f} x {(y1 - y0) * k:.1f} mm, {ref_ch} = {ref_mm} mm, {FONT.split('/')[-1]}, puslapis {W:.0f} x {H:.0f} pt")
