"""P6_3mm+foil - S raidės vaizdavimo bandymas (Rytis 2026-10-09)."""
import sys
sys.path.insert(0, "/tmp/claude-0/-home-claude/454aabe4-a26e-51a4-90bd-3f68e4f6d938/scratchpad/co")
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))  # reklama/scripts
import common as C
from common import *
import r3d, p6_vaizdas as PV
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
from shapely.geometry import Polygon
from shapely.affinity import scale as sscale, translate as stranslate

C.PROJECT = "P6 profile - representation test"
C.CLIENT = "BrandFactory"
H_S, DEPTH = 500.0, 100.0
RET = HexColor(K.ralhex("3020")); FOIL = HexColor("#C8102E")      # šonai RAL 3020, plėvelė 3M 3630-33

tp = TextPath((0, 0), "S", size=100, prop=FontProperties(fname="/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"))
polys = [Polygon(p).buffer(0) for p in tp.to_polygons() if len(p) > 2]
g = polys[0]
for p_ in polys[1:]:
    g = g.symmetric_difference(p_)
x0, y0, x1, y1 = g.bounds
k = H_S / (y1 - y0)
g = sscale(stranslate(g, -x0, -y0), k, k, origin=(0, 0))          # y aukštyn, mm
W_S = g.bounds[2]
gd = sscale(g, 1, -1, origin=(0, H_S / 2))                        # y žemyn (lapui)
L = PV.layers(g, DEPTH)

begin(11)
s = MM / 5                                                        # 1:5
FX, FY = K.IX0 + 60, 70
# ---------------- FRONT VIEW
def pth(geom, col, lw=0.4, dash=None):
    for gg in getattr(geom, "geoms", [geom]):
        for ring in [gg.exterior] + list(gg.interiors):
            pts = [(FX + x * s, FY + y * s) for x, y in ring.coords]
            if dash:
                for a, b in zip(pts[:-1], pts[1:]):
                    line(a[0], a[1], b[0], b[1], 0.3, K.GREY, dash=dash)
            else:
                poly(pts, fill=None, stroke=col, lw=lw)
K.set_view(True)
for gg in getattr(gd, "geoms", [gd]):
    poly([(FX + x * s, FY + y * s) for x, y in gg.exterior.coords], fill=FOIL, lw=0.4)
    for r_ in gg.interiors:
        poly([(FX + x * s, FY + y * s) for x, y in r_.coords], fill=white, lw=0.4)
K.set_view(False)
pth(gd.buffer(-PV.BODY_INSET, join_style=2), None, dash=([2, 1.5], 0))
hdim(FX, FX + W_S * s, FY - 16, f"{W_S:.0f}", FY, FY, size=12)
vchain(FX - 20, [FY, FY + H_S * s], [FX, FX], [f"{H_S:.0f}"], size=12)
T(FX + W_S * s / 2, FY + H_S * s + 14, "glass = client contour (foil colour); dashed - body 1.5 smaller", 8, align="c")
view_title(FX + W_S * s / 2, FY + H_S * s + 38, "FRONT VIEW", "SCALE 1:5")
# ---------------- SIDE VIEW (right)
SXW = FX + W_S * s + 40 + DEPTH * s + 10
PV.side_view(SXW, FY, s, 0, H_S, DEPTH, RET, FOIL)
hdim(SXW - DEPTH * s, SXW, FY - 16, f"{DEPTH:.0f}", FY, FY, size=12)
hchain(FY + H_S * s + 12, [SXW - DEPTH * s, SXW - (DEPTH - 3) * s, SXW], [FY + H_S * s] * 3, ["3", f"{DEPTH - 3:.0f}"], size=8)
leader(SXW - DEPTH * s + 0.4, FY + H_S * s * 0.3, SXW - DEPTH * s - 26, FY + H_S * s * 0.22, 1)
leader(SXW - (DEPTH - 1.5) * s, FY + H_S * s * 0.5, SXW - DEPTH * s - 26, FY + H_S * s * 0.45, "A")
leader(SXW - 40 * s, FY + H_S * s * 0.6, SXW + 20, FY + H_S * s * 0.7, 2)
view_title(SXW - DEPTH * s / 2, FY + H_S * s + 38, "SIDE VIEW (RIGHT)", "SCALE 1:5")
# ---------------- DETAIL A 2:1 (edge)
DX, DY = SXW + 70, FY + 10
sa = MM / 0.5
K.set_view(True)
rect(DX, DY, 3 * sa, 40 * sa, fill=PV.GLASS_WHITE, lw=0.5)                        # stiklas 3 mm
rect(DX - 0.8, DY, 0.8, 40 * sa, fill=FOIL, stroke=None, lw=0)                    # plėvelė
rect(DX + 3 * sa, DY + 1.5 * sa, 30 * sa, 1.0 * sa, fill=RET, lw=0.4)             # šonas 1 mm, 1.5 į vidų
K.set_view(False)
zig(DX - 6, DX + 40 * sa, DY + 40 * sa)
vchain(DX - 14, [DY, DY + 1.5 * sa], [DX, DX + 3 * sa], ["1.5"], size=8)
hchain(DY - 10, [DX, DX + 3 * sa], [DY, DY], ["3"], size=8)
leader(DX - 0.4, DY + 22 * sa, DX - 28, DY + 26 * sa, 3)
leader(DX + 1.5 * sa, DY + 30 * sa, DX + 30, DY + 34 * sa, 1)
leader(DX + 15 * sa, DY + 2 * sa, DX + 30, DY + 10 * sa, 2)
view_title(DX + 15 * sa, DY + 40 * sa + 22, "DETAIL A", "SCALE 2:1  |  glass edge")
# ---------------- 3D (2 kampai)
for i, (yaw, pitch) in enumerate(((32, 17), (-48, 12))):
    S3 = r3d.Scene(yaw=yaw, pitch=pitch)
    PV.add_3d(S3, g, DEPTH, RET, FOIL)
    bx = 700; by = 50 + i * 300; bw, bh = 450, 245
    S3.render((bx, by, bw, bh))
    view_title(bx + bw / 2, by + bh + 16, "3D VIEW" + (" - FRONT LEFT" if i == 0 else " - FRONT RIGHT"), "ILLUSTRATIVE")
# ---------------- 3D DETAIL - S galo iškarpa (kantelio sluoksniai matosi aiškiai)
from shapely.geometry import box as sbox
cut = g.intersection(sbox(W_S * 0.62, H_S * 0.62, W_S * 1.01, H_S * 0.86))
cut = max(getattr(cut, "geoms", [cut]), key=lambda q: q.area)
S4 = r3d.Scene(yaw=40, pitch=24)
PV.add_3d(S4, cut, 30.0, RET, FOIL, z0=DEPTH - 30.0)          # tik priekinė 30 mm dalis - kantelis matosi aiškiai
S4.render((70, 425, 540, 175))
view_title(340, 618, "3D DETAIL - EDGE (front 30 mm)", "RAL 3020 body | white glass edge 3 mm | foil 3M 3630-33")
bom = [["1", "Face P6_3mm, client contour", "Plexi 3 mm white", "-", "edge 3 mm visible"],
       ["2", "Letter return (body) - contour -1.5 mm", "Alu 1 mm", "RAL 3020", f"depth {DEPTH - 3:.0f}"],
       ["3", "Front foil", "Vinyl foil, cast", "3M 3630-33", "on face"]]
md = [["Profile", "P6_3mm + foil"], ["Glass", "client contour, 3 mm"], ["Body", "1.5 mm smaller"],
      ["Depth", f"{DEPTH:.0f} (to face)"], ["Side / 3D", "RAL | white 3 | foil"], ["P6_8mm", "edge milled to 3"]]
def sect(x, y, w, h):
    T(x + w / 2, y + h / 2, "see DETAIL A", 9, align="c", color=K.GREY, auto_red=False)
band("P6 EDGE", sect, bom, md, "P6_3mm + foil - letter S, representation test", "1 / 1", "1:5 / 2:1")
K.save(sys.argv[1])
print("ok", round(W_S), H_S)
