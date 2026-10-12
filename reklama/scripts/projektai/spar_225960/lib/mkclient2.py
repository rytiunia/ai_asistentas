"""Kliento faile paruošimas skill'o skriptui: raidės (spalva pagal x ribas -> atskiros grupės), logotipai,
pilki bėgeliai, piktogramos (atskira spalva -> decals)."""
import sys; sys.path.insert(0, '/home/claude/w/lib'); sys.path.insert(0, '/home/claude/v9/scripts')
from rails import *
import lapas_core as K

def path_pts(sub):
    out = []
    for sp in sub:
        out.append([fitz.Point(*q) for q in K.flatten(sp, 10)])
    return out

def make(src, view, out, splits=(), split_cols=(), pict_col=None, rail_col=(0.5, 0.5, 0.5), logo_cut=False,
         drop_pict_bigger=True, logo_col=None, logo_foil=None, logo_replica=None):
    cp = fitz.open(src)[0]
    ds = pick(cp, view, keep_small_squares=False)
    faces, logos, pict, rails, marks = classify(ds)
    rails = [d for d in rails if d['rect'].width > 6 * max(d['rect'].height, 0.1) or d['rect'].height > 6 * max(d['rect'].width, 0.1)]
    o = fitz.open(); pg = o.new_page(width=cp.rect.width, height=cp.rect.height)
    draw(pg, rails, fitz.Identity, recolor=lambda d, f, c: (rail_col, None))
    from shapely.ops import unary_union
    F = unary_union([K.shape_geom(K.drawing_to_subpaths(d, lambda q: q)) for d in faces]).buffer(0.15)
    def poly_fill(geom, fill):
        sh = pg.new_shape()
        for gg in getattr(geom, "geoms", [geom]):
            for ring in [gg.exterior] + list(gg.interiors):
                sh.draw_polyline([fitz.Point(*q) for q in ring.coords])
        sh.finish(fill=fill, color=None, even_odd=True, closePath=True); sh.commit()
    if logo_foil is not None:
        # logotipas = balta plexi forma (kaip raidės) + plėvelė: žalias diskas - baltas kraštas - piktograma (iškirpta)
        geo = lambda d: K.shape_geom(K.drawing_to_subpaths(d, lambda q: q))
        big = max((d['rect'].width * d['rect'].height for d in logos), default=0)
        ring = [d for d in pict if d['rect'].width * d['rect'].height > 0.6 * big]
        small = [d for d in pict if d not in ring]
        for d in logos:
            outer = geo(d)
            for r_ in ring: outer = outer.union(geo(r_))
            from shapely.geometry import Polygon as _P
            disc = unary_union([_P(gg.exterior) for gg in getattr(outer, "geoms", [outer])])
            poly_fill(disc, (1, 1, 1))
            foil = geo(d)
            for r_ in ring: foil = foil.difference(geo(r_))
            for p_ in small: foil = foil.difference(geo(p_))
            poly_fill(foil, logo_foil)
        logos_drawn = True
    elif logo_replica is not None:
        # Rytis 2026-10-08 (pagal pagamintą 225721 KAFFEBAR): apskritimas - 2 mm juodas Alu kompozitas, išpjautas kaip
        # apskritimas + RĖMO ATKARTOJIMAS (juostos ant bėgelių per visą ilgį); ant apskritimo - plėvelė (decal)
        comp_col, foil_col, strip_h = logo_replica
        from shapely.geometry import box as _box
        geo = lambda d: K.shape_geom(K.drawing_to_subpaths(d, lambda q: q))
        rep = [geo(d) for d in logos]
        for d in rails:
            r_ = d['rect']
            if r_.width > r_.height:
                yc = (r_.y0 + r_.y1) / 2
                rep.append(_box(r_.x0, yc - strip_h / 2, r_.x1, yc + strip_h / 2))
        poly_fill(unary_union(rep), comp_col)
        for d in logos:
            poly_fill(geo(d), foil_col)
        logos_drawn = True
    else:
        logos_drawn = False
    for d in (logos if not logos_drawn else []):
        g = K.shape_geom(K.drawing_to_subpaths(d, lambda q: q))
        if logo_cut: g = g.difference(F)
        poly_fill(g, logo_col or d['fill'])
    for d in faces:
        for L in K.split_letters(K.drawing_to_subpaths(d, lambda q: q)):
            cx = (L["bb"][0] + L["bb"][2]) / 2
            col = d['fill']
            for i, xs in enumerate(splits):
                if cx > xs: col = split_cols[i]
            sh = pg.new_shape()
            for pts in path_pts(L["sub"]): sh.draw_polyline(pts)
            sh.finish(fill=col, color=None, even_odd=True, closePath=True); sh.commit()
    if pict_col is not None and logo_foil is None:
        big = max((d['rect'].width * d['rect'].height for d in logos), default=1e9)
        for d in pict:
            if drop_pict_bigger and d['rect'].width * d['rect'].height > 0.6 * big: continue
            draw(pg, [d], fitz.Identity, recolor=lambda d_, f, c: (pict_col, None))
    o.save(out)
    return faces, logos, pict, rails
