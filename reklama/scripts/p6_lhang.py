"""P6 raidės ant L profilių (Alfa Neon / Volvo BILB26-01001 būdas) - tipinis pjūvis lapo juostoje (v269-v270, Rytis 2026-10-15).

v270 (Rytis: „P6 turi atitikti standartą, įkeltas brėžinys buvo išskirtinai rėmo - brėžinyje P6 patvirtintas profilis + naujo
tipo montavimo rėmas"): raidė - ETALONINIS P6 pjūvis (`p6_ref`, Rytio `assets/p6_profiliai.pdf`, U wallframe variantas BE
bėgelio), prie jo tame pačiame mastelyje pridedamas L rėmas iš etalono assets/etalonai/BILB26-01001_P6_ant_L_profiliu.pdf:
  5 Frame - Al L 40x40x2 (x2, ties bėgelių ašimis: vertikali lentyna AUKŠTYN prie raidžių nugaros, horizontali - į fasadą),
  6 Wire frame - Al U 15x15x2 (x1, laidams, viršutinio L kampe, anga į fasadą),
  7 Wall side frame - Al L 40x40x2 (x2, ant fasado: horizontali lentyna PO rėmo L, vertikali - žemyn prie fasado);
  raidžių rėmas užkabinamas ant fasado L. Nugara -> fasadas ~ L + gap (etalone ~48 mm su L 40).
Balionai: 1-4 - kaip etalone (priekis, šonas, nugara, LED), 5 / 6 / 7 - spec `lhang.balloons` (= BOM poz.)."""
from reportlab.lib.colors import HexColor

ALU = HexColor("#B4B4B4")
U8_DEPTH_UNITS = 42.3                                        # p6_profiliai.pdf U 8 mm skydelis: galas -> priekis


def section(K, x, y, w, h, depth, spec, title="PROFILE P6 ON L-PROFILES - TYPICAL SECTION"):
    from lapas_core import poly, rect, T, hdim
    L = dict({"l": 40.0, "t": 2.0, "u": 15.0, "ut": 2.0, "gap": 8.0, "balloons": {}}, **(spec.get("lhang") or {}))
    ral = (spec.get("rail") or {}).get("ral")
    COL = HexColor(K.ralhex(str(ral))) if ral and str(ral).strip("?") else ALU
    l, t, u, ut, gap = (float(L[k_]) for k_ in ("l", "t", "u", "ut", "gap"))
    B = {"5": 5, "6": 6, "7": 7}
    B.update({str(a): b for a, b in (L["balloons"] or {}).items()})
    upm0 = float(depth) / U8_DEPTH_UNITS
    extra = (l + gap + 10) / upm0 + 18

    def after(G):
        X, Yp, upm, k = G["X"], G["Yp"], G["upm"], G["k"]
        bx = G["back_x"]
        mm = lambda v: v / upm                                 # mm -> etalono vienetai
        wx = bx - mm(l + gap)                                  # fasadas
        top, bot = G["top"], G["bottom"]
        hgt = bot - top
        cys = [top + hgt * 0.3]          # kaip etalone - pjūvis per VIENĄ (viršutinį) L porą; BOM - x2
        P = lambda pts: poly([(X(a), Yp(b)) for a, b in pts], fill=COL, lw=0.3)
        rect(X(wx - mm(8)), Yp(top - mm(10)), mm(8) * k, (hgt + mm(20)) * k, fill=HexColor("#DCEBF5"), lw=0.3)
        anchors = []
        for n_, cy in enumerate(cys):
            yh = cy + mm(l) / 2                                # rėmo L horizontalios lentynos apačia
            P([(bx, yh - mm(l)), (bx - mm(t), yh - mm(l)), (bx - mm(t), yh - mm(t)), (bx - mm(l), yh - mm(t)),
               (bx - mm(l), yh), (bx, yh)])                    # 5 rėmo L
            yw = yh + mm(1)
            P([(wx + mm(l), yw), (wx, yw), (wx, yw + mm(l)), (wx + mm(t), yw + mm(l)), (wx + mm(t), yw + mm(t)),
               (wx + mm(l), yw + mm(t))])                      # 7 fasado L
            if n_ == 0:                                        # 6 laidų U - viršutinio L kampe, anga į fasadą
                yu0, xu1 = yh - mm(t) - mm(u) - mm(1), bx - mm(t)
                P([(xu1, yu0), (xu1 - mm(u), yu0), (xu1 - mm(u), yu0 + mm(ut)), (xu1 - mm(ut), yu0 + mm(ut)),
                   (xu1 - mm(ut), yu0 + mm(u) - mm(ut)), (xu1 - mm(u), yu0 + mm(u) - mm(ut)), (xu1 - mm(u), yu0 + mm(u)),
                   (xu1, yu0 + mm(u))])
                anchors += [((X(bx - mm(l) * 0.6), Yp(yh - mm(t) / 2)), B["5"]),
                            ((X(xu1 - mm(u)), Yp(yu0 + mm(u) / 2)), B["6"]),
                            ((X(wx + mm(t) / 2), Yp(yw + mm(l) * 0.7)), B["7"])]
        anchors = sorted([a for a in anchors if a[1]], key=lambda q: q[0][1])
        bxl = X(wx - mm(8)) - 14
        prev = -1e9
        for (px, py), n in anchors:                            # balionai kairėje, horizontaliai (nesikerta)
            by = max(py, prev + 15)
            prev = by
            K.leader(px, py, bxl, by, n, 6)
        hdim(X(wx), X(bx), Yp(top - mm(10)) - 6, f"~{l + gap:g}", Yp(top - mm(10)), Yp(top), size=7)
        T(G["x0"] + 4, G["y0"] + 9,
          f"L {l:g}x{l:g}x{t:g} (letters) hooks onto L {l:g}x{l:g}x{t:g} (facade); U {u:g}x{u:g}x{ut:g} - wires", 5.5,
          color=K.GREY)

    K.p6_reference(x, y, w, h, depth, kind="u", front=spec.get("front", "P6"), title=title, no_rail=True,
                   extra_left=extra, after=after)
