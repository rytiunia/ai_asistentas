"""P6 raidės ant L profilių (Alfa Neon / Volvo BILB26-01001 būdas) - tipinis pjūvis lapo juostoje (v269, Rytis 2026-10-15).

Etalonas: assets/etalonai/BILB26-01001_P6_ant_L_profiliu.pdf (Ryčio „pavyzdys iš jau daryto"):
  5 Frame - Al L 40x40x2 (x2, raidžių pusėje: vertikali lentyna prie raidžių nugaros, horizontali - į fasadą),
  6 Wire frame - Al U 15x15x2 (x1, laidams, prie rėmo),
  7 Wall side frame - Al L 40x40x2 (x2, ant fasado: vertikali lentyna prie fasado, horizontali - į raides);
  rėmo L horizontali lentyna UŽSIKABINA / guli ant fasado L horizontalios lentynos (montuojama užkabinant).
Pjūvis - vertikalus per viršutinį L: kairėje raidė (priekis, šonas, nugara, LED), dešinėje fasadas.
Balionai: 1 priekis, 2 šonas, 3 nugara, 4 LED, 5 rėmo L, 6 laidų U, 7 fasado L (BOM numeriai - spec `lhang.balloons`)."""
from reportlab.lib.colors import HexColor, white

PLEX = HexColor("#F7F7F2")
ALU = HexColor("#B4B4B4")
LED = HexColor("#F2E28C")


def section(K, x, y, w, h, depth, spec, title="PROFILE P6 ON L-PROFILES - TYPICAL SECTION"):
    from lapas_core import rect, poly, T, hdim
    L = dict({"l": 40.0, "t": 2.0, "u": 15.0, "ut": 2.0, "balloons": {}}, **(spec.get("lhang") or {}))
    ral = (spec.get("rail") or {}).get("ral")
    COL = HexColor(K.ralhex(str(ral))) if ral and str(ral).strip("?") else ALU
    side_ral = next((g.get("return_ral") for g in spec.get("groups", []) if g.get("return_ral")), None)
    SIDE = HexColor(K.ralhex(side_ral)) if side_ral else HexColor("#DADADA")
    K.header(x, y, w, title)
    rect(x, y + 12, w, h - 12, lw=0.6)
    D, l, t, u, ut = float(depth), L["l"], L["t"], L["u"], L["ut"]
    gap = float(L.get("gap", 8))                                  # nugara -> fasadas = L + gap (etalone ~ 48 su L 40)
    zb, zw = D, D + l + gap                                       # raidės nugaros išorė, fasadas
    HV = 170.0                                                    # rodomas raidės viršaus ruožas
    W_ = zw + 10
    k = min((w - 90) / W_, (h - 12 - 34) / HV)
    ox, oy = x + 40, y + 12 + 16
    X = lambda z: ox + z * k
    Y = lambda v: oy + v * k
    K.set_view(True)
    rect(X(zw), Y(-4), 8 * k, (HV + 6) * k, fill=HexColor("#DCEBF5"), lw=0.3)          # fasadas (stiklas)
    rect(X(0), Y(0), 8 * k, HV * k, fill=PLEX, lw=0.3)                               # 1 priekis
    rect(X(8), Y(0), (D - 8) * k, 1.0 * k, fill=SIDE, lw=0.2)                       # 2 šonas (viršus)
    rect(X(D - 1.5), Y(0), 1.5 * k, HV * k, fill=SIDE, lw=0.2)                      # 3 nugara
    rect(X(D - 1.5 - 3), Y(HV * 0.45), 3 * k, 14 * k, fill=LED, lw=0.2)            # 4 LED ant nugaros
    yh = 95.0                                                     # rėmo L horizontali lentyna (apačioje)
    # 5 rėmo L: vertikali lentyna AUKŠTYN prie nugaros, horizontali - į fasadą (kaip etalone)
    poly([(X(zb), Y(yh - l)), (X(zb + t), Y(yh - l)), (X(zb + t), Y(yh - t)), (X(zb + l), Y(yh - t)),
          (X(zb + l), Y(yh)), (X(zb), Y(yh))], fill=COL, lw=0.3)
    # 7 fasado L: horizontali lentyna PO rėmo L, vertikali - ŽEMYN prie fasado; rėmas užkabinamas ant jos
    yw = yh + 1.0
    poly([(X(zw - l), Y(yw)), (X(zw), Y(yw)), (X(zw), Y(yw + l)), (X(zw - t), Y(yw + l)), (X(zw - t), Y(yw + t)),
          (X(zw - l), Y(yw + t))], fill=COL, lw=0.3)
    # 6 laidų U 15x15 - ant rėmo L vertikalios lentynos, anga į fasadą
    yu = yh - l + 4
    poly([(X(zb + t), Y(yu)), (X(zb + t + u), Y(yu)), (X(zb + t + u), Y(yu + ut)), (X(zb + t + ut), Y(yu + ut)),
          (X(zb + t + ut), Y(yu + u - ut)), (X(zb + t + u), Y(yu + u - ut)), (X(zb + t + u), Y(yu + u)),
          (X(zb + t), Y(yu + u))], fill=COL, lw=0.3)
    K.circle(X(zb + t + u / 2 + 1), Y(yu + u * 0.33), 2.0 * k, fill=HexColor("#2050E0"), lw=0.1)
    K.circle(X(zb + t + u / 2 + 1), Y(yu + u * 0.68), 2.0 * k, fill=HexColor("#333320"), lw=0.1)
    K.set_view(False)
    hdim(X(0), X(D), Y(0) - 8, f"{D:g}", Y(0), Y(0), size=7)
    hdim(X(zb), X(zw), Y(yh - l) - 10, f"~{l + gap:g}", Y(yh - l), Y(-4), size=7)
    T(X(zw + 4), Y(-4) - 3, "FACADE", 5.5, align="c", color=K.GREY)
    T(x + 5, y + h - 5, f"L {l:g}x{l:g}x{t:g} (letters) hooks onto L {l:g}x{l:g}x{t:g} (facade); U {u:g}x{u:g}x{ut:g} - wires",
      5.5, color=K.GREY)
    B = {"1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7}
    B.update({str(a): b for a, b in (L["balloons"] or {}).items()})
    left = [((X(4), Y(HV * 0.55)), B["1"]), ((X(D * 0.45), Y(0.5)), B["2"])]
    right = [((X(D - 0.8), Y(HV * 0.8)), B["3"]), ((X(D - 3), Y(HV * 0.45 + 7)), B["4"]),
             ((X(zb + l * 0.6), Y(yh - t / 2)), B["5"]), ((X(zb + t + u), Y(yu + u / 2)), B["6"]),
             ((X(zw - t / 2), Y(yw + l * 0.7)), B["7"])]
    for side, pts in (("l", left), ("r", right)):         # v269: balionai anchor'o aukštyje (horizontalios nuorodos nesikerta)
        pts = sorted([p for p in pts if p[1]], key=lambda q: q[0][1])
        bx = (x + 14) if side == "l" else (X(zw + 8) + 16)
        prev = -1e9
        for (px, py), n in pts:
            by = max(py, prev + 15)
            prev = by
            K.leader(px, py, bx, by, n, 6)
