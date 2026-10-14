"""v59 (Rytis 2026-10-09): P6 profilio REALUS vaizdavimas (>= 95 % realaus vaizdo) - šoninis vaizdas ir 3D.
Sandara (visiems P6 priekio variantams):
  * STIKLAS (plexi) = ORIGINALUS kliento failo kontūras (raidės dydis = stiklo dydis), matomas kraštas 3 mm
    (5S, buv. P6_3mm - 3 mm polikarbonatas FR; P6_8mm - 8 mm plexi frezuojama taip, kad išorinis kraštelis liktų 3 mm, liežuvis - korpuse);
  * KORPUSAS (šonai) = kontūras 1,5 mm MAŽESNIS už stiklą (offset -1,5; v210 5S - 2 mm), gylis = bendras gylis - 3;
  * +foil variantuose iš šono / 3D matosi: korpuso spalva | BALTAS stiklo kantelis 3 mm | plėvelės spalva priekyje;
    color variante (5S color) kantelis = plexi spalva.
Naudojimas: layers(geom, depth, front) -> sluoksniai; add_3d(scene, ...) - r3d; side_view(...) - šoninis vaizdas."""
import lapas_core as K
from reportlab.lib.colors import HexColor, white

GLASS_EDGE = 3.0         # matomas stiklo kraštas, mm
BODY_INSET = 1.5         # korpusas mažesnis už stiklą, mm (frezuoti 8+ mm)
BODY_INSET_5S = 2.0      # v210: 5S - šonas 2 mm nuo priekio krašto (assets/konstrukcijos/5S_profilis.pdf)


def body_inset(front):
    import p6_front as P6F
    return BODY_INSET_5S if P6F.parse(front)["kind"] == "3mm" else BODY_INSET
GLASS_WHITE = HexColor("#F7F7F2")


def white_edge(front):
    """v90: kantelis baltas, jei plexi balta (su plėvele arba be); spalvotas - tik 'color' variantuose"""
    import p6_front as P6F
    p = P6F.parse(front)
    return p["foil"] or not p["color"]


def layers(geom, depth, front="5S+foil"):
    """-> dict: body (geom, z0, z1), glass (geom, z0, z1). z = 0 sienos / galo plokštuma, +z į žiūrovą."""
    body = geom.buffer(-body_inset(front), join_style=2)
    return {"body": (body, 0.0, depth - GLASS_EDGE), "glass": (geom, depth - GLASS_EDGE, depth),
            "foil": ("foil" in str(front)), "white_edge": white_edge(front), "front": front}


def add_3d(S, geom, depth, ret_col, face_col, front="5S+foil", glass_col=None, xf=None, z0=0.0):
    """r3d.Scene: korpusas (šonų spalva) + stiklas 3 mm (baltas kantelis arba plexi spalva) + priekis (plėvelė)"""
    L = layers(geom, depth, front)
    b, bz0, bz1 = L["body"]
    g, gz0, gz1 = L["glass"]
    edge_col = glass_col or (GLASS_WHITE if L["white_edge"] else face_col)
    S.extrude_xy(b, z0 + bz0, z0 + bz1, ret_col, ret_col, xf=xf)
    S.extrude_xy(g, z0 + gz0, z0 + gz1, edge_col, face_col, xf=xf)


def side_view(x_wall, y_top, s, geom_y0, geom_y1, depth, ret_col, face_col, front="5S+foil", glass_col=None,
              wall_right=True, rect_fn=None):
    """Šoninis vaizdas (iš dešinės): siena x_wall, z didėja į kairę (wall_right) ; y_top - raidės viršaus y lape,
    s - mastelis pt/mm, geom_y0..1 - raidės aukštis (mm). Piešia korpusą (inset 1,5), stiklą 3 mm, plėvelę."""
    R = rect_fn or K.rect
    sg = -1 if wall_right else 1
    X = lambda z: x_wall + sg * z * s
    H = geom_y1 - geom_y0
    foil = "foil" in str(front)
    edge_col = glass_col or (GLASS_WHITE if white_edge(front) else face_col)
    zb = depth - GLASS_EDGE
    xa, xb = sorted((X(0), X(zb)))
    bi = body_inset(front)
    R(xa, y_top + bi * s, xb - xa, (H - 2 * bi) * s, fill=ret_col, lw=0.4)
    xa, xb = sorted((X(zb), X(depth)))
    R(xa, y_top, xb - xa, H * s, fill=edge_col, lw=0.4)
    if foil:                                         # plėvelė - spalvota linija priekyje (perdidinta 0,8 pt)
        xf_ = X(depth)
        R(xf_ - (0.8 if wall_right else 0), y_top, 0.8, H * s, fill=face_col, stroke=None, lw=0)


def draw_geom(geom, tf, fill, stroke=None, lw=None, canvas=None):
    """shapely (su skylėmis) -> užpildytas kelias (even-odd); tf(x, y) -> canvas koordinatės"""
    c = canvas or K.c
    c.saveState()
    if fill is not None:
        c.setFillColor(fill)
    if stroke is not None:
        c.setStrokeColor(stroke); c.setLineWidth(K.HAIR if lw is None else lw)
    p = c.beginPath()
    for g in getattr(geom, "geoms", [geom]):
        if g.is_empty:
            continue
        for ring in [g.exterior] + list(g.interiors):
            pts = [tf(x, y) for x, y in ring.coords]
            p.moveTo(*pts[0])
            for q in pts[1:]:
                p.lineTo(*q)
            p.close()
    c.drawPath(p, stroke=stroke is not None, fill=fill is not None, fillMode=0)
    c.restoreState()


def rear_view(geom, tf, ret_col, face_col, front="5S+foil", glass_col=None, canvas=None, stroke=None):
    """Galinis vaizdas: aplink dugną matosi stiklo kraštas (1,5 mm) - stiklas (kliento kontūras) baltas / plexi spalvos,
    ant jo dugnas / korpusas 1,5 mm mažesnis (šonų spalva)."""
    from reportlab.lib.colors import black
    edge_col = glass_col or (GLASS_WHITE if white_edge(front) else face_col)
    draw_geom(geom, tf, edge_col, stroke or black, None, canvas)
    # v190 (Rytis 2026-10-13: „pasikartojančios klaidos: ne hairline projekcijose") - smulkiame mastelyje 1,5 mm kraštas
    #  < 0,8 pt: dvi hairline linijos susilieja į storą liniją -> vidinis kontūras be linijos (tik užpildas)
    (ax_, ay_), (bx_, by_) = tf(0.0, 0.0), tf(1.0, 0.0)
    s_ = ((bx_ - ax_) ** 2 + (by_ - ay_) ** 2) ** 0.5
    bi = body_inset(front)
    inner_stroke = (stroke or black) if bi * s_ >= 0.8 else None
    draw_geom(geom.buffer(-bi, join_style=2), tf, ret_col, inner_stroke, None, canvas)
