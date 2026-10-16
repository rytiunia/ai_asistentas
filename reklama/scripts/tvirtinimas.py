"""v326 BENDRAS tvirtinimo pagal RAIDĖS FORMĄ principas (Rytis v245 / v317: „raides tvirtinti pagal kvadrato ir trikampio
principą") - viena vieta P6 D3.2 (p6_dxf.shape_holes) ir akrilo rėmo smeigėms (braizyti_begeliai._acr_studs), kad taisyklė
nebeišsiskirtų (v317 ji buvo „dingusi" iš p6_dxf, nes buvo įdiegta tik akrilo rėmui).

shape_n(geom, bb, simp) - taškų skaičius: supaprastinto gaubto kampai (kvadratas / stačiakampis 4, trikampis 3 ...), 2..6,
    platiems + 1 kas 500 mm; maža raidė (< 200 mm) - iki 3. simp - gaubto supaprastinimas (dalis nuo didesnio gabarito):
    P6 0,16 (a / s apvalumai - ne papildomi kampai, v317), akrilo rėmas 0,12 (v245).
fps_start(cands, geom) - pirmas taškas: toliausiai nuo raidės centro (toliau - FPS, kuo toliau vienas nuo kito)."""


def shape_n(geom, bb, simp=0.16):
    x0, y0, x1, y1 = bb
    hull = geom.convex_hull.simplify(simp * max(x1 - x0, y1 - y0))
    nh = len(hull.exterior.coords) - 1 if hasattr(hull, "exterior") else 2
    n_t = max(min(max(nh, 2), 6), 2 + int((x1 - x0) // 500))
    if max(x1 - x0, y1 - y0) < 200:
        n_t = min(n_t, 3)
    return n_t


def fps_start(cands, geom):
    cx, cy = geom.centroid.x, geom.centroid.y
    return max(cands, key=lambda q: (q[0] - cx) ** 2 + (q[1] - cy) ** 2)
