import flat
from flat import *

P1 = "/home/claude/w/t/clean_p1.pdf"
ORIG = "/home/claude/w/in/otter.pdf"


def logo_spar_paths(clip=(612.9, 201.3, 641.5, 206.4)):
    return client_paths(P1, clip)


def backplate(out, sheet, W, H, ral, title, code, print_img=None, logo=None, parts=True, H1=1400):
    """2 mm Alu folded plate (box lid 40 mm) W x H; parts=True - iš 2 dalių (H1 + H-H1), suvaržomos per užlenktus kraštus.
    Pagal 225767 / 225776: L 30x30x2 viršus + apačia, varžtai DIN 7504 per užlenkimą į L (50 mm nuo kraštų, ~300)."""
    begin(code, 11)
    n = 15
    s = MM / n
    RED = HexColor("#C00000")
    nsc = round((W - 100) / 300); pitch = (W - 100) / nsc
    fp = f"{pitch:.0f}" if abs(pitch - round(pitch)) < 0.05 else f"{pitch:.1f}"
    xs_h = [50 + i * pitch for i in range(nsc + 1)]           # varžtų / skylių vietos nuo krašto
    fw, fh = W * s, H * s
    fx = VX0 + 70; fy = VY0 + 70
    face = RALC(ral) if not print_img else HexColor("#2B2B2B")
    # ---- TOP VIEW: užlenktas kraštas 40 mm su skylėmis varžtams į L profilį (apačia - ta pati)
    ty = VY0 + 26; e = 40 * s
    rect(fx, ty, fw, e, fill=face, lw=0.3)
    for xh in xs_h:
        K.circle(fx + xh * s, ty + e / 2, 1.1, fill=white, stroke=black, lw=0.2)
        K.centerline(fx + xh * s, ty - 2, fx + xh * s, ty + e + 2)
    hchain(ty - 6, [fx] + [fx + x * s for x in xs_h] + [fx + fw], [ty] * (len(xs_h) + 2),
           ["50"] + [fp] * nsc + ["50"], 8)
    hdim(fx, fx + fw, ty - 18, f"{W}", ty, ty, size=12)
    T(fx + fw + 8, ty + e / 2 + 2.5, f"TOP VIEW - {nsc + 1} holes for screws into L profile (bottom edge the same)",
      8, color=K.GREY, auto_red=False)
    # ---- FRONT VIEW
    gp = 1.2
    yp = fy + H1 * s
    if parts:
        if print_img:
            rect(fx, fy, fw, fh, fill=face, lw=0.4)
            over(*("img", (fx, fy, fx + fw, fy + fh), print_img))
            over(*("rect", (fx, yp - gp / 2, fx + fw, yp + gp / 2)))
        else:
            rect(fx, fy, fw, H1 * s - gp / 2, fill=face, lw=0.4)
            rect(fx, yp + gp / 2, fw, (H - H1) * s - gp / 2, fill=face, lw=0.4)
    else:
        rect(fx, fy, fw, fh, fill=face, lw=0.4)
        if print_img:
            over(*("img", (fx, fy, fx + fw, fy + fh), print_img))
    if logo:
        lx, ly, lw_, lh = logo
        draw_client(logo_spar_paths(), (612.9, 201.3, 641.5, 206.4), fx + lx * s, fy + ly * s, lw_ * s, lh * s)
        hchain(fy - 10, [fx, fx + lx * s, fx + (lx + lw_) * s, fx + fw], [fy] * 4, [f"{lx:.0f}", f"{lw_:.0f}", f"{W - lx - lw_:.0f}"], size=12)
        vchain(fx + fw + 14, [fy, fy + ly * s, fy + (ly + lh) * s], [fx + (lx + lw_) * s] * 3, [f"{ly:.0f}", f"{lh:.0f}"], size=12)
    if parts:
        vchain(fx - 16, [fy, yp, fy + fh], [fx] * 3, [f"{H1}", f"{H - H1}"], size=12)
        T(fx + 8, fy + 14, f"PART 1  -  {W} x {H1}", 8, font="FB", color=white, auto_red=False)
        T(fx + 8, yp + 14, f"PART 2  -  {W} x {H - H1}", 8, font="FB", color=white, auto_red=False)
    vchain(fx - 34, [fy, fy + fh], [fx] * 2, [f"{H}"], size=12)
    view_title(fx + fw / 2, fy + fh + 22, "FRONT VIEW", f"SCALE 1:{n}")
    # ---- SIDE VIEW (be L profilių)
    sx = fx + fw + max(50, 0.11 * fw) + 10
    if parts:
        rect(sx, fy, e, H1 * s - gp / 2, fill=face, lw=0.4)
        rect(sx, yp + gp / 2, e, (H - H1) * s - gp / 2, fill=face, lw=0.4)
        K.c.saveState(); K.c.setStrokeColor(RED); K.c.setLineWidth(0.5); K.c.circle(sx + e / 2, K.Y(yp), 13); K.c.restoreState()
        T(sx + e + 12, yp - 10, "B", 9, font="FB")
    else:
        rect(sx, fy, e, fh, fill=face, lw=0.4)
    hdim(sx, sx + e, fy - 10, "40", fy, fy, size=12)
    T(sx + e + 6, fy + 10, "A", 9, font="FB")
    view_title(sx + e / 2, fy + fh + 22, "SIDE VIEW (RIGHT)", f"SCALE 1:{n}")
    # ---- REAR VIEW (MIRRORED): L profiliai su varžtais, jungtis
    r_n = 25; rs = MM / r_n
    rx = sx + 60; ry = fy
    rw, rh = W * rs, H * rs
    ryp = ry + H1 * rs
    if parts:
        rect(rx, ry, rw, H1 * rs, fill=HexColor("#E6E6E6"), lw=0.4)
        rect(rx, ryp, rw, (H - H1) * rs, fill=HexColor("#E6E6E6"), lw=0.4)
        for xh in xs_h:
            K.circle(rx + xh * rs, ryp, 0.9, fill=RED, stroke=None)
        T(rx + rw / 2, ryp + 10, f"joint: {nsc + 1} bolts through folded edges, same positions", 8, color=RED, align="c", auto_red=False)
    else:
        rect(rx, ry, rw, rh, fill=HexColor("#E6E6E6"), lw=0.4)
    for yy in (ry + 2, ry + rh - 2 - 30 * rs):
        rect(rx + 25 * rs, yy, (W - 50) * rs, 30 * rs, fill=HexColor("#8C8C8C"), lw=0.1)
        for xh in xs_h:
            K.circle(rx + xh * rs, yy + 15 * rs, 0.8, fill=black, stroke=None)
    hchain(ry - 8, [rx, rx + 50 * rs, rx + (W - 50) * rs, rx + rw], [ry] * 4, ["50", f"{nsc} x {fp} = {W - 100}", "50"], 8)
    hchain(ry + rh + 12, [rx, rx + 25 * rs, rx + (W - 25) * rs, rx + rw], [ry + rh] * 4, ["25", f"{W - 50} (L30x30x2)", "25"], 8)
    view_title(rx + rw / 2, ry + rh + 36, "REAR VIEW (MIRRORED)", f"SCALE 1:{r_n}")
    y_next = ry + rh + 60
    if parts:
        # ---- DETAIL B - JOINT
        k = 2.0
        bx, by = rx + 215, y_next + 6
        K.set_view(True)
        rect(bx, by, 2 * k, 40 * k, fill=black, lw=0.3)
        rect(bx + 2 * k, by + 38 * k, 40 * k, 2 * k, fill=black, lw=0.3)
        rect(bx, by + 41 * k, 2 * k, 40 * k, fill=black, lw=0.3)
        rect(bx + 2 * k, by + 41 * k, 40 * k, 2 * k, fill=black, lw=0.3)
        rect(bx + 22 * k, by + 33 * k, 3 * k, 15 * k, fill=HexColor("#9A9A9A"), lw=0.25)
        rect(bx + 19 * k, by + 31 * k, 9 * k, 2 * k, fill=HexColor("#6E6E6E"), lw=0.25)
        rect(bx + 19 * k, by + 48 * k, 9 * k, 2 * k, fill=HexColor("#6E6E6E"), lw=0.25)
        K.set_view(False)
        K.centerline(bx + 23.5 * k, by + 28 * k, bx + 23.5 * k, by + 53 * k)
        hdim(bx, bx + 42 * k, by - 4, "40", by, by)
        T(bx + 46 * k, by + 41 * k, "bolt", 8, color=K.GREY, auto_red=False)
        view_title(bx + 21 * k, by + 81 * k + 14, "DETAIL B - JOINT", "SCALE 1:5")
        rect(rx, y_next, 200, 34, stroke=RED, lw=1.2)
        T(rx + 100, y_next + 14, "Plate from 2 parts!", 10, color=RED, align="c", auto_red=False)
        T(rx + 100, y_next + 28, "Fitting together with bolts.", 10, color=RED, align="c", auto_red=False)
        y3, x3 = y_next + 50, rx - 10
        w3 = 205
    else:
        y3, x3, w3 = y_next, rx - 10, VX1 - rx + 10
    # ---- 3D
    V3 = K.View3D()
    sol = ([(sbox(0, H - H1 + 6, W, H), 0, 40, face, face if not print_img else HexColor("#5A4A3A")),
            (sbox(0, 0, W, H - H1 - 6), 0, 40, face, face if not print_img else HexColor("#5A4A3A"))] if parts else
           [(sbox(0, 0, W, H), 0, 40, face, face if not print_img else HexColor("#5A4A3A"))])
    iso_box(V3, (x3, y3, w3, flat.VY1 - y3 - 22), sol)
    view_title(x3 + w3 / 2, flat.VY1 - 6, "3D VIEW", "ILLUSTRATIVE - NOT TO SCALE")
    # ---- band
    kg = (W + 80) * (H + 80 + (80 if parts else 0)) * 2 * 2.7 / 1e6 + 2 * (W - 50) * 58 * 2 * 2.7 / 1e6
    if parts:
        bom = [[1, f"Part 1 - box lid 40 mm, {W} x {H1}", "Alu 2 mm folded", f"RAL {ral}", "1 pcs."],
               [1, f"Part 2 - box lid 40 mm, {W} x {H - H1}", "Alu 2 mm folded", f"RAL {ral}", "1 pcs."]]
    else:
        bom = [[1, f"Back plate - box lid 40 mm, {W} x {H}", "Alu 2 mm folded", f"RAL {ral}", "1 pcs."]]
    if print_img:
        bom.append(["", "Print Gel'UV + laminate, front + edges", "original file", "-", f"{W * H / 1e6:.2f} m²"])
    if logo:
        bom.append(["", "Logo SPAR, graphics foil", "ORACAL 551 010 gloss", "ORACAL 8500 614", f"{logo[2]:.0f} x {logo[3]:.0f}"])
    bom += [[2, "L profile 30x30x2", "Aluminium", "-", f"2 x {(W - 50) / 1000:.2f} = {2 * (W - 50) / 1000:.2f} m"],
            [3, "Screw DIN 7504 N 4.2x16 T20", "Steel, hard.", "-", f"{2 * (nsc + 1)} pcs. ({nsc + 1}/L)"],
            [4, "Wall fixing", "?", "-", "?"]]
    if parts:
        bom.append([5, "Bolts + nuts, joint of 2 parts", "?", "-", f"{nsc + 1} pcs."])
    md = [["Quantity", "1 pcs."], ["Overall size", f"{W} x {H}"], ["Parts", f"2: {H1} + {H - H1}, bolted" if parts else "1 (one piece)"],
          ["Edge (box lid)", "40"], ["Material", "Alu 2 mm folded"], ["Finish", f"RAL {ral}"],
          ["Graphics", "print, original file" if print_img else "logo SPAR, ORACAL foil"],
          ["Mounting", "L30x30x2 top + bottom"], ["Screw holes", f"50 | {nsc} x {fp} | 50"], ["Wall", "?"],
          ["Weight (calc.)", f"≈ {kg:.0f} kg / pcs"]]
    band({"title": title, "file_code": code, "sheet": f"{sheet} / 18"}, "BACK PLATE - TYPICAL SECTION (A)", section_backplate,
         bom, md, f"1:{n} / 1:{r_n}")
    finish(out)


def portal(out, sheet):
    """Portalas pagal 225809 / 202293 (Jølstraholmen): šviesdėžės rėmas 300 x 100, plexi GS 3H25 3 mm RAL 3020,
    galas 2 mm Alu, apačioje 10 mm PVC; nerūdijančio plieno 1 mm apsauga (bumper) 160 mm - TIK priekyje ir šonuose."""
    code = "SPAR_225960_06_portal"
    begin(code, 12)
    W, H, L, B, F, D = 4700, 3050, 300, 300, 160, 100
    n = 25; s = MM / n
    red = RALC("3020"); grey = HexColor("#C9CACE")
    fx, fy = VX0 + 70, VY0 + 48                      # v18: vieta 12 pt matmenims viršuje
    X = lambda mm: fx + mm * s; Yv = lambda mm: fy + mm * s
    K.set_view(True)
    for a in (0, W - L):
        rect(X(a), Yv(0), L * s, (H - F) * s, fill=red, lw=0.4)
        rect(X(a), Yv(H - F), L * s, F * s, fill=grey, lw=0.4)
    rect(X(L), Yv(0), (W - 2 * L) * s, B * s, fill=red, lw=0.4)
    K.set_view(False)
    hdim(X(0), X(W), fy - 36, "4700", fy, fy, size=12)
    hchain(fy - 14, [X(0), X(L), X(W - L), X(W)], [fy] * 4, ["300", "4100", "300"], size=12)
    vchain(fx - 34, [Yv(0), Yv(H)], [fx] * 2, ["3050"], size=12)
    vchain(fx - 16, [Yv(0), Yv(B), Yv(H - F), Yv(H)], [fx] * 4, ["300", "2590", "160"], size=12)
    vchain(X(W * 0.3), [Yv(B), Yv(H)], [X(W * 0.3)] * 2, ["2750"], size=12)
    # Rytis 2026-10-08: viršutinė dalis per ilga medžiagai - iš 2 dalių (pagal 217482 Ål / 218194: plexi priekis iš 2 dalių)
    XJ = W / 2
    line(X(XJ), Yv(0) - 6, X(XJ), Yv(B) + 6, 0.5, black, dash=([6, 2, 1.5, 2], 0))
    hchain(Yv(B) + 14, [X(L), X(XJ), X(W - L)], [Yv(B)] * 3, [f"{XJ - L:.0f}", f"{W - L - XJ:.0f}"], size=12)
    K.c.saveState(); K.c.setStrokeColor(black); K.c.setLineWidth(0.4); K.c.setDash(3, 1.5)
    K.c.circle(X(XJ), K.Y(Yv(B / 2)), B * s * 0.9); K.c.restoreState()
    T(X(XJ) + B * s * 0.75, Yv(B) + 8, "C", 9, font="FB", auto_red=False)
    T(X(XJ), Yv(B) + 30, "TOP FROM 2 PARTS - JOINT", 8, font="FB", align="c", auto_red=False)
    leader(X(W - L / 2), Yv(H - F / 2), X(W - L) - 40, Yv(H - F / 2) - 30, 3)
    view_title(fx + W * s / 2, fy + H * s + 22, "FRONT VIEW", f"SCALE 1:{n}")
    # side
    sx = X(W) + max(50, 0.11 * W * s)
    K.set_view(True)
    rect(sx, Yv(0), D * s, (H - F) * s, fill=red, lw=0.4)
    rect(sx, Yv(H - F), D * s, F * s, fill=grey, lw=0.4)
    K.set_view(False)
    hdim(sx, sx + D * s, fy - 12, "100", fy, fy, size=12)
    view_title(sx + D * s / 2, fy + H * s + 22, "SIDE VIEW (RIGHT)", f"SCALE 1:{n}")
    # rear - be apsaugos (ji tik priekyje / šonuose)
    rn = 50; rs = MM / rn
    rx, ry = sx + 60, fy
    K.set_view(True)
    for a in (0, W - L):
        rect(rx + a * rs, ry, L * rs, H * rs, fill=red, lw=0.4)
    rect(rx + L * rs, ry, (W - 2 * L) * rs, B * rs, fill=red, lw=0.4)
    K.set_view(False)
    T(rx + W * rs / 2, ry + 40, "Backside 2 mm Alu, painted RAL 3020", 8, align="c")
    line(rx + (W - XJ) * rs, ry - 4, rx + (W - XJ) * rs, ry + B * rs + 4, 0.5, black, dash=([6, 2, 1.5, 2], 0))
    # Rytis 2026-10-08: laido išvestis kaip kliento faile - priekyje viršuje KAIRĖJE, išeina į kairę
    # (galiniame veidrodiniame vaizde - dešinio stulpo viršus, į dešinę)
    cxp, cyp = rx + (W - L / 2) * rs, ry + 150 * rs
    K.c.saveState(); K.c.setFillColor(white); K.c.setStrokeColor(black); K.c.setLineWidth(0.5)
    K.c.circle(cxp, K.Y(cyp), 3, stroke=1, fill=1); K.c.restoreState()
    line(cxp - 5, cyp, cxp + 5, cyp, 0.2); line(cxp, cyp - 5, cxp, cyp + 5, 0.2)
    xe = rx + W * rs + 16
    K.cable_line([(cxp + 3, cyp), (xe, cyp)])
    T(xe + 3, cyp - 3, "D11 cable exit", 8)
    T(xe + 3, cyp + 7, "top left (front view)", 8)
    T(xe + 3, cyp + 19, "12V, 3 m + dimming", 8, color=K.CABLE, auto_red=False)
    T(xe + 3, cyp + 29, "-> trafo box (220V)", 8, color=K.CABLE, auto_red=False)
    view_title(rx + W * rs / 2, ry + H * rs + 22, "REAR VIEW (MIRRORED)", f"SCALE 1:{rn}")
    # 3D
    V3 = K.View3D()
    solids = [(sbox(0, F, L, H), 0, D, red, red), (sbox(W - L, F, W, H), 0, D, red, red), (sbox(L, H - B, XJ - 4, H), 0, D, red, red),
              (sbox(XJ + 4, H - B, W - L, H), 0, D, red, red), (sbox(0, 0, L, F), 0, D, grey, grey), (sbox(W - L, 0, W, F), 0, D, grey, grey)]
    y3 = ry + H * rs + 50
    iso_box(V3, (rx - 20, y3, VX1 - rx + 20, flat.VY1 - y3 - 22), solids)
    view_title(rx + (VX1 - rx) / 2, flat.VY1 - 6, "3D VIEW", "ILLUSTRATIVE - NOT TO SCALE")
    # ---- DETAIL: nerūdijančio plieno 1 mm apsauga (pagal 202293 Jølstraholmen, sheet 6)
    k = MM / 5
    dx, dy = fx + 10, fy + H * s + 70
    T(dx, dy - 8, "(3)  STAINLESS STEEL BUMPER 1 mm  -  2 pcs.  (front + 2 sides, front view only)", 8, font="FB", auto_red=False)
    # išklotinė 505 x 160
    ux = dx; uy = dy + 18
    rect(ux, uy, 505 * k, 160 * k, fill=HexColor("#E3E4E8"), lw=0.4)
    for bl in (101.5, 403.5):
        line(ux + bl * k, uy, ux + bl * k, uy + 160 * k, 0.3, K.GREY, dash=([4, 1, 1, 1], 0))
    hdim(ux, ux + 505 * k, uy - 6, "505", uy, uy)
    vchain(ux - 10, [uy, uy + 160 * k], [ux] * 2, ["160"])
    T(ux + 505 * k / 2, uy + 160 * k + 12, "FLAT PATTERN  (bend lines dash-dot)", 8, color=K.GREY, align="c", auto_red=False)
    # vaizdas iš viršaus (U)
    tx = ux + 505 * k + 40; tyy = uy + 6
    t1 = 1.0 * k + 0.6
    poly([(tx, tyy), (tx + 304 * k, tyy), (tx + 304 * k, tyy + 102 * k), (tx + 304 * k - t1, tyy + 102 * k), (tx + 304 * k - t1, tyy + t1),
          (tx + t1, tyy + t1), (tx + t1, tyy + 102 * k), (tx, tyy + 102 * k)], fill=HexColor("#8C8C8C"), lw=0.3)
    hdim(tx, tx + 304 * k, tyy - 6, "304", tyy, tyy)
    vchain(tx + 304 * k + 10, [tyy, tyy + 102 * k], [tx + 304 * k] * 2, ["102"])
    T(tx + 152 * k, tyy + 102 * k + 12, "TOP VIEW  (inner 302 x 101)", 8, color=K.GREY, align="c", auto_red=False)
    # ---- DETAIL C - viršutinės dalies jungtis (plexi priekis iš 2 dalių, kaip 217482 / 218194)
    # Rytis 2026-10-08: DETAIL C - priekio vaizdo angoje, po pastaba „TOP FROM 2 PARTS - JOINT"
    cw_, ch_ = 170, 150
    cx0 = X(XJ) - cw_ / 2; cy0 = Yv(B) + 40
    V3c = K.View3D()
    dk_ = HexColor("#8E1018")
    sol_c = [(sbox(0, 0, 220, 300), 0, 100, red, red), (sbox(360, 0, 580, 300), 0, 100, red, red),
             (sbox(270, 10, 360, 290), 0, 88, dk_, dk_)]
    iso_box(V3c, (cx0, cy0, cw_, ch_ - 24), sol_c)
    view_title(cx0 + cw_ / 2, cy0 + ch_ - 10, "DETAIL C - TOP JOINT", "plexiglas front 2 parts, inner sleeve")

    def sec(x, y, w, h):
        K.set_view(True)
        s2 = (w - 60) / 300.0
        ox, oy = x + 30, y + 40
        tt = 3 * s2 * 2.2
        rect(ox, oy, 300 * s2, 100 * s2, fill=None, lw=0.3)
        K.hatch(ox, oy + 100 * s2 - tt, 300 * s2, tt, 2)
        K.hatch(ox, oy, tt, 100 * s2, 2); K.hatch(ox + 300 * s2 - tt, oy, tt, 100 * s2, 2)
        rect(ox + tt, oy, 300 * s2 - 2 * tt, 2.5, fill=black, lw=0.3)
        for f_ in (0.25, 0.5, 0.75):
            rect(ox + 300 * s2 * f_ - 7, oy + 2.5, 14, 4.5, fill=white, lw=0.35)
        K.set_view(False)
        hdim(ox, ox + 300 * s2, oy - 10, "300", oy, oy)
        K.vchain(ox + 300 * s2 + 14, [oy, oy + 100 * s2], [ox + 300 * s2] * 2, ["100"])
        leader(ox + 300 * s2 * 0.6, oy + 100 * s2 - tt / 2, ox + 300 * s2 * 0.6, oy + 100 * s2 + 16, 1)
        leader(ox + 60, oy + 1.2, ox + 40, oy - 16, 4)
        leader(ox + 300 * s2 * 0.5, oy + 5, ox + 300 * s2 * 0.5 + 24, oy + 30, 5)
        T(x + w / 2, y + h - 6, "section through leg / beam - wall side up", 8, color=K.GREY, align="c", auto_red=False)
    A_front = (2 * L * (H - F) + (W - 2 * L) * B) / 1e6
    A_side = (2 * (H - F) * D * 2 + (W - 2 * L) * D * 2) / 1e6
    kg = (A_front + A_side) * 3 * 1.19 + A_front * 2 * 2.7 + 2 * 0.505 * 0.16 * 7.9
    bom = [[1, "Body, red plexiglas (front + sides)", "PLEXIGLAS GS 3H25, 3 mm", "RAL 3020", f"{A_front + A_side:.2f} m²"],
           [2, "TOP, red plexiglas - 2 parts (joint C)", "PLEXIGLAS GS 3H25, 3 mm", "RAL 3020", "2 pcs. (2 x 2050)"],
           [3, "Bumper 505 x 160, bent 304 x 102", "Stainless steel 1 mm", "-", "2 pcs."],
           [4, "Backside", "Alu 2 mm", "RAL 3020", f"{A_front:.2f} m²"],
           [5, "LED modules + dimmer", "", "", "?"],
           [6, "Bottom", "PVC 10 mm", "-", "2 pcs."],
           [7, "Trafo box 12V + dimming (cable 12V, 3 m)", "Alu box", "-", "1 pcs."],
           [8, "Wall / floor fixing", "?", "-", "?"]]
    md = [["Quantity", "1 pcs."], ["Overall size", "4700 x 3050"], ["Profile width", "300"], ["Depth", "100"],
          ["Clear opening", "4100 x 2750"], ["Top", "2 parts 2050 + 2050, joint C"], ["Face", "PLEXIGLAS GS 3H25, RAL 3020"], ["Backside", "Alu 2 mm, RAL 3020"],
          ["Bumper", "stainless 1 mm, h 160, front only"], ["Illumination", "LED + dimming"], ["Power", "12V 3 m -> trafo box 220V"],
          ["Weight (calc.)", f"≈ {kg:.0f} kg / pcs, excl. PSU"]]
    band({"title": "Portal - entrance, illuminated", "file_code": code, "sheet": f"{sheet} / 18"},
         "PORTAL - TYPICAL SECTION", sec, bom, md, f"1:{n} / 1:{rn}")
    finish(out)


def print_sheet(out, sheet):
    code = "SPAR_225960_10_print_3000x2300"
    begin(code)
    W, H = 3000, 2300; n = 15; s = MM / n
    fx, fy = VX0 + 80, VY0 + 50
    rect(fx, fy, W * s, H * s, fill=HexColor("#2B2B2B"), lw=0.4)
    over(*("img", (fx, fy, fx + W * s, fy + H * s), "/home/claude/w/t/print88.png"))
    hdim(fx, fx + W * s, fy - 20, "3000", fy, fy, size=12)
    vchain(fx - 20, [fy, fy + H * s], [fx] * 2, ["2300"], size=12)
    view_title(fx + W * s / 2, fy + H * s + 30, "FRONT VIEW", f"SCALE 1:{n}  |  client preview, print from original file")
    T(fx + W * s + 60, fy + 20, "Print only - no back plate.", 9, font="FB")
    T(fx + W * s + 60, fy + 36, "Original print forwarded - separate files for printing.", 8)
    T(fx + W * s + 60, fy + 50, "Material / laminate: ?", 8)
    bom = [[1, "Print 3000 x 2300", "?", "?", "6.90 m²"], ["", "Laminate", "?", "-", "6.90 m²"]]
    md = [["Quantity", "1 pcs."], ["Size", "3000 x 2300"], ["Product", "print only"], ["Artwork", "original file (forwarded)"],
          ["Material", "?"], ["Finish", "?"], ["Weight (calc.)", "-"]]
    band({"title": "Print 3000 x 2300 mm (separate files for printing)", "file_code": code, "sheet": f"{sheet} / 18"},
         "MATERIAL", material_block([("PRINT", "#3A3A3A", "original file - forwarded"), ("LAMINATE", None, "?")]), bom, md, f"1:{n}")
    finish(out)


def foil_sheet(out, sheet, code, title, W, H, colhex, name, mat_txt, n, md_extra=(), fin_txt=None):
    begin(code)
    s = MM / n
    fx, fy = VX0 + 70, VY0 + 80
    rect(fx, fy, W * s, H * s, fill=HexColor(colhex), lw=0.4)
    hdim(fx, fx + W * s, fy - 20, f"{W}", fy, fy, size=12)
    vchain(fx - 20, [fy, fy + H * s], [fx] * 2, [f"{H}"], size=12)
    view_title(fx + W * s / 2, fy + H * s + 30, "FOIL - FLAT", f"SCALE 1:{n}")
    bom = [[1, name, mat_txt, fin_txt or mat_txt, f"{W} x {H} / {W * H / 1e6:.2f} m²"]]
    md = [["Quantity", "1 pcs."], ["Size", f"{W} x {H}"], ["Material", mat_txt]] + list(md_extra) + [["Weight (calc.)", "-"]]
    band({"title": title, "file_code": code, "sheet": f"{sheet} / 18"}, "MATERIAL",
         material_block([(name.upper(), colhex, mat_txt)]), bom, md, f"1:{n}")
    finish(out)


def decor(out, sheet):
    code = "SPAR_225960_13_white_decor"
    begin(code)
    W, H = 769, 131.3; n = 5; s = MM / n
    fx, fy = VX0 + 120, VY0 + 120
    # Rytis 2026-10-08: be fono - tik baltas logotipas su juoda hairline kontūro linija
    _pp = [(sub, (1, 1, 1)) for sub, _ in client_paths(P1, (591.6, 658.2, 613.6, 662.1))]
    draw_client(_pp, (591.6, 658.2, 613.6, 662.1), fx, fy, W * s, H * s, outline=black)
    hdim(fx, fx + W * s, fy - 34, "769", fy, fy, size=12)
    vchain(fx - 34, [fy, fy + H * s], [fx] * 2, ["131.3"], size=12)
    view_title(fx + W * s / 2, fy + H * s + 50, "FRONT VIEW", f"SCALE 1:{n}  |  white, outline = cut line")
    bom = [[1, "White decor SPAR logo", "white foil / print ?", "white", "7 pcs."]]
    md = [["Quantity", "7 pcs."], ["Size", "769 x 131.3"], ["Colour", "white"], ["Material", "?"], ["Weight (calc.)", "-"]]
    band({"title": "White decor SPAR logo 769 x 131.3 mm", "file_code": code, "sheet": f"{sheet} / 18"}, "MATERIAL",
         material_block([("WHITE DECOR", "#FFFFFF", "material ?")]), bom, md, f"1:{n}")
    finish(out)


def sandprint(out, sheet):
    code = "SPAR_225960_14_print_on_sandblast"
    begin(code)
    W, H = 930, 855; n = 10; s = MM / n
    fy = VY0 + 60
    for i, clip in enumerate([(596.8, 677.8, 649.5, 726.3), (652.3, 677.8, 705.1, 726.3)]):
        fx = VX0 + 160 + i * (W * s + 200)
        rect(fx, fy, W * s, H * s, fill=HexColor("#C4C5C9"), lw=0.4)
        over(*("pdf", (fx, fy, fx + W * s, fy + H * s), ORIG, 0, clip))
        hdim(fx, fx + W * s, fy - 20, "930", fy, fy, size=12)
        vchain(fx - 20, [fy, fy + H * s], [fx] * 2, ["855"], size=12)
        view_title(fx + W * s / 2, fy + H * s + 30, f"DESIGN {'AB'[i]} - 5 pcs.", f"SCALE 1:{n}  |  client preview")
    bom = [[1, "White print on sandblast foil, design A", "sandblast foil", "white print", "5 pcs."],
           [2, "White print on sandblast foil, design B", "sandblast foil", "white print", "5 pcs."]]
    md = [["Quantity", "5 + 5 pcs."], ["Size", "930 x 855"], ["Material", "sandblast foil"], ["Print", "white"],
          ["Artwork", "separate files for printing"], ["Weight (calc.)", "-"]]
    band({"title": "White print on sandblast foil 930 x 855 mm", "file_code": code, "sheet": f"{sheet} / 18"}, "MATERIAL",
         material_block([("SANDBLAST FOIL", "#C4C5C9", "white print")]), bom, md, f"1:{n}")
    finish(out)


if __name__ == "__main__":
    import shutil
    O = "/home/claude/w/sk9/"
    from PIL import Image, ImageFilter
    d = fitz.open(ORIG)
    for x, nm in ((103, "veg"), (88, "print88")):
        open(f"/home/claude/w/t/{nm}.jpg", "wb").write(d.extract_image(x)["image"])
        Image.open(f"/home/claude/w/t/{nm}.jpg").resize((1020, 790), Image.LANCZOS).filter(ImageFilter.GaussianBlur(1.0)).save(f"/home/claude/w/t/{nm}.png")
    portal(O + "portal.pdf", 6)
    backplate(O + "bp_veg.pdf", 7, 2700, 2100, "9005", "Back plate 2700 x 2100, box lid 40 mm, print", "SPAR_225960_07_backplate_2700_print",
              print_img="/home/claude/w/t/veg.png")
    backplate(O + "bp_red2700.pdf", 8, 2700, 2100, "3020", "Back plate 2700 x 2100, box lid 40 mm, SPAR logo", "SPAR_225960_08_backplate_2700_red",
              logo=(850, 200, 1000, 170))
    backplate(O + "bp_red2000.pdf", 9, 2000, 2100, "3020", "Back plate 2000 x 2100, box lid 40 mm, SPAR logo", "SPAR_225960_09_backplate_2000_red",
              logo=(500, 200, 1000, 170))
    print_sheet(O + "print.pdf", 10)
    foil_sheet(O + "foil_red.pdf", 11, "SPAR_225960_11_foil_PMS185", "Foil PMS 185 - Avery 777-002CF or equivalent", 5000, 1220,
               "#E4002B", "Foil PMS 185", "Avery 777-002CF or equiv.", 25, fin_txt="PMS 185")
    foil_sheet(O + "foil_sand.pdf", 12, "SPAR_225960_12_sandblast_foil", "Sandblast foil 23000 x 1220 mm", 23000, 1220,
               "#C4C5C9", "Sandblast foil", "sandblast foil", 100, fin_txt="sandblast")
    decor(O + "decor.pdf", 13)
    sandprint(O + "sandprint.pdf", 14)
    print("ok")
