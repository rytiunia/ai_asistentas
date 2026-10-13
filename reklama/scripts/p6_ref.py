"""P6 tipinis pjūvis iš Rytio etaloninio brėžinio (assets/p6_profiliai.pdf).

Rytis patvirtino 2026-10-07: geometrija - JO brėžinio (>= 90 %), atvaizdavimas - CAD pjūvio taisyklėmis:
  * ISO 128-50: ploni pjaunami lakštai (šonai, galas, bėgelis U / kvadratinis, folded plokštės pjūvis) -
    UŽPILDYTI JUODAI, tarp gretimų - balta tarpo linija; plexi - plonas 45° štrichavimas;
  * matomi kontūrai (LED moduliai, folded kraštas vaizde, PVC juosta) - plati linija 0,35 pt;
  * spalvų nėra; juodi numerių „blynai" -> dokumento balionai (balti apskritimai) su išvadine;
  * varžtai (B) - CAD žymėjimas: galvutė, kotas, sriegio linija, ašinė;
  * mazgo detalizacija (apskritimai, 1/2/A/B, legenda) PAŠALINTA; 3 mm variante bendrame žymėjime
    pridedamas A - PVC juosta; 8 mm - jokių papildomų žymų.
6 variantai: folded / U wallframe / square wallframe  x  plexi 3 mm (PVC edge) / 8 mm (milled edge).
Numeriai kaip etalone: 1 priekis, 2 šonas, 3 galas, 4 LED, 5 fonas / bėgelis, A PVC juosta."""
import os
import pymupdf as fitz

REF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "p6_profiliai.pdf")
PANELS = {("folded", "3mm"): (1.1, 1.1, 225.1, 108.1), ("u", "3mm"): (229.5, 1.1, 453.5, 108.1),
          ("square", "3mm"): (459.5, 1.1, 709.6, 108.1), ("folded", "8mm"): (1.1, 122.5, 225.1, 229.5),
          ("u", "8mm"): (229.5, 122.5, 453.5, 229.5), ("square", "8mm"): (459.5, 122.5, 709.6, 229.5)}
LW_VIS = 0.35          # matomas kontūras
LW_THIN = 0.15         # štrichavimas, sriegis
# Rytis 2026-10-07: P6 ON RAILS pjūvis - TOS PAČIOS spalvos kaip DETAIL A (P6+3): šonai tamsiai pilki, galas ir
# bėgeliai šviesiau pilki, ausėlės vidutiniškai pilkos, plexi baltas (be štrichavimo), varžtai tamsūs.
COLOR = True
PAL = {"ret": (0x6E / 255,) * 3, "back": (0xB4 / 255,) * 3, "rail": (0xB4 / 255,) * 3, "ear": (0x8C / 255,) * 3,
       "pvc": (0xC8 / 255,) * 3, "bolt": (0x3A / 255,) * 3}
LW_SEC = 0.4


def _sheet(cv, key):
    """pjaunamo lakšto užpildas: spalvotas (kaip DETAIL A) arba juodas (ISO 128-50)"""
    if COLOR:
        cv.setFillColorRGB(*PAL[key]); cv.setStrokeColorRGB(0, 0, 0); cv.setLineWidth(LW_SEC)
    else:
        cv.setFillColorRGB(0, 0, 0); cv.setStrokeColorRGB(1, 1, 1); cv.setLineWidth(0.45)


def kind_of(variant, rail_type=None):
    if variant == "folded":
        return "folded"
    t = str(rail_type or "u").lower()
    return "square" if t.startswith(("sq", "box", "kv")) else "u"


def _dark(col, lim=0.15):
    return col is not None and max(col) <= lim


def _kinds(d):
    return "".join(it[0] for it in d["items"])


def _pts(d):
    out = []
    for it in d["items"]:
        if it[0] == "re":
            r = it[1]; out += [fitz.Point(r.x0, r.y0), fitz.Point(r.x1, r.y1)]
        elif it[0] == "qu":
            q = it[1]; out += [q.ul, q.ur, q.ll, q.lr]
        else:
            out += [p for p in it[1:] if isinstance(p, fitz.Point)]
    return out


def _load(kind, front):
    import p6_front as P6F
    front = "8mm" if P6F.milled(front) else "3mm"
    pg = fitz.open(REF)[0]
    P = fitz.Rect(PANELS[(kind, front)])
    inner = fitz.Rect(P.x0 + 1, P.y0 + 20, P.x1 - 1, P.y1 - 1)
    dr = [d for d in pg.get_drawings() if inner.contains(d["rect"])]
    spans = [s for b in pg.get_text("dict")["blocks"] for l in b.get("lines", []) for s in l["spans"]
             if inner.contains(fitz.Rect(s["bbox"])) and s["text"].strip()]
    return front, dr, spans


RAIL_RATIO = 1.0   # v162: stačiakampio profilio gylis / aukštis pjūvyje (40x20 -> 0.5; Rytis: „turi matytis 40x20")
LABEL_MAP = {}     # v160: pjūvio balionų numeriai pagal originalo BOM (spec "section_labels")


def draw(cv, H, x, y, w, h, kind, front, depth, *, leader, balloon, T, hdim, hair=0.1, top=26, pad=8,
         line=None, ears=None, ear_hole=0.15, bracket=None):
    """Nubraižo pjūvį į sritį (x, y, w, h - bloko vidus be antraštės; lapo koord., y žemyn)."""
    front, dr, spans = _load(kind, front)
    F8 = front == "8mm"
    skip = set()
    # --- mazgo detalizacija: apskritimai + viskas padidinimo apskritimo viduje - šalinama
    circ = sorted([i for i, d in enumerate(dr) if d.get("fill") is None and d["rect"].width > 10
                   and _kinds(d) == "cccc"], key=lambda i: dr[i]["rect"].width)
    mag = dr[circ[-1]]["rect"] if circ else None
    skip.update(circ)
    if mag is not None:
        skip.update(i for i, d in enumerate(dr) if mag.contains(d["rect"]))
    # --- numeriai (juodi kvadratėliai) ir jų išvadinės
    boxes = [i for i, d in enumerate(dr) if i not in skip and _dark(d.get("fill")) and d.get("color") is None
             and 5 < d["rect"].width < 8 and 5 < d["rect"].height < 8
             and _kinds(d).count("c") == 4 and _kinds(d).count("l") == 4]
    lab = {}
    for i in boxes:
        for s in spans:
            if fitz.Rect(s["bbox"]).intersects(dr[i]["rect"]) and len(s["text"].strip()) <= 2:
                lab[i] = s["text"].strip()
    skip.update(boxes)
    leads = []
    for i, d in enumerate(dr):
        if i in skip or not _dark(d.get("fill")) or d.get("color") is not None:
            continue
        for j in boxes:
            bj = dr[j]["rect"]
            if fitz.Rect(bj.x0 - 0.6, bj.y0 - 0.6, bj.x1 + 0.6, bj.y1 + 0.6).intersects(d["rect"]):
                cx, cy = (bj.x0 + bj.x1) / 2, (bj.y0 + bj.y1) / 2
                tp = max(_pts(d), key=lambda p: (p.x - cx) ** 2 + (p.y - cy) ** 2)
                leads.append((j, tp)); skip.add(i)
                break
    # --- varžtai
    bolts = []
    for i, d in enumerate(dr):
        f_ = d.get("fill")
        if i not in skip and f_ and 0.18 < max(f_) < 0.3 and d.get("color") is None:
            r = d["rect"]
            th = [k for k, e in enumerate(dr) if k != i and _dark(e.get("fill")) and r.contains(e["rect"])]
            skip.add(i); skip.update(th)
            bolts.append((r, dr[th[0]]["rect"] if th else None))
    # --- PVC juosta (3 mm): pilka juostelė, kurią kerta varžtas
    pvc = [i for i, d in enumerate(dr) if i not in skip and d.get("fill") and not _dark(d["fill"])
           and max(d["fill"]) < 0.95 and d["rect"].height < 2 and d["rect"].width < 7
           and any(b.intersects(d["rect"]) for b, _ in bolts)]
    plex = max((i for i, d in enumerate(dr) if i not in skip and d.get("fill") == (1.0, 1.0, 1.0)
                and d["rect"].height > 40), key=lambda i: dr[i]["rect"].x1)

    # --- mastelis (be padidinimo ir legendos)
    clip = None
    for i, d in enumerate(dr):
        if i not in skip or i in boxes:
            clip = d["rect"] if clip is None else clip | d["rect"]
    clip = fitz.Rect(clip.x0 - 3, clip.y0 - 2, clip.x1 + (18 if not F8 else 6), clip.y1 + 2)
    aw, ah = w - 2 * pad, h - top - pad
    k = min(aw / clip.width, ah / clip.height)
    tx = x + pad + (aw - clip.width * k) / 2
    ty = y + top + (ah - clip.height * k) / 2

    _piv = None
    if kind == "square" and abs(RAIL_RATIO - 1.0) > 1e-3:
        _tb = [d["rect"] for i, d in enumerate(dr) if i not in skip and d.get("fill") and 0.6 < max(d["fill"]) < 0.75
               and d["rect"].width < 14 and d["rect"].height > 30 and _kinds(d).count("l") >= 16]
        if _tb:
            _piv = _tb[0].x1                              # profilio plokštuma prie raidės galo

    def X(v):
        if _piv is not None and v < _piv:                 # sienos pusė (profilis, ausėlė) - gylis pagal RAIL_RATIO
            v = _piv - (_piv - v) * RAIL_RATIO
        return tx + (v - clip.x0) * k

    def Yp(v):
        return ty + (v - clip.y0) * k

    def P(p):
        return X(p.x), H - Yp(p.y)

    def build(d):
        path = cv.beginPath()
        cur = None
        for it in d["items"]:
            if it[0] == "re":
                r = it[1]
                path.rect(X(r.x0), H - Yp(r.y1), r.width * k, r.height * k); cur = None
                continue
            if it[0] == "qu":
                q = it[1]
                path.moveTo(*P(q.ul)); path.lineTo(*P(q.ur)); path.lineTo(*P(q.lr)); path.lineTo(*P(q.ll))
                path.close(); cur = None
                continue
            p0 = it[1]
            if cur is None or abs(cur.x - p0.x) > 1e-3 or abs(cur.y - p0.y) > 1e-3:
                path.moveTo(*P(p0))
            if it[0] == "l":
                path.lineTo(*P(it[2])); cur = it[2]
            elif it[0] == "c":
                path.curveTo(*P(it[2]), *P(it[3]), *P(it[4])); cur = it[4]
        if d.get("closePath"):
            path.close()
        return path

    # --- geometrija pagal CAD pjūvio taisykles
    for i, d in enumerate(dr):
        if i in skip:
            continue
        fill, stroke = d.get("fill"), d.get("color")
        path = build(d)
        cv.saveState()
        if fill is not None and not _dark(fill) and max(fill) < 0.75 and i not in pvc:
            # pjaunamas plonas lakštas: šonai (0.435) / galas, bėgeliai (0.695)
            _sheet(cv, "ret" if abs(max(fill) - 0.435) < 0.03 else "back")
            cv.drawPath(path, stroke=1, fill=1, fillMode=0)
        elif COLOR and i in pvc:
            _sheet(cv, "pvc"); cv.drawPath(path, stroke=1, fill=1, fillMode=0)
        elif fill is not None and _dark(fill):
            cv.setFillColorRGB(0, 0, 0)
            cv.drawPath(path, stroke=0, fill=1, fillMode=0)
        else:
            cv.setFillColorRGB(1, 1, 1); cv.setStrokeColorRGB(0, 0, 0)
            cv.setLineWidth(LW_VIS if stroke is not None or fill is None else LW_VIS)
            cv.drawPath(path, stroke=1, fill=1 if fill is not None else 0, fillMode=0)
        cv.restoreState()
        if i == plex and not COLOR:                                     # plexi - plonas 45° štrichavimas
            r = d["rect"]
            x0_, x1_, y0_, y1_ = X(r.x0), X(r.x1), H - Yp(r.y1), H - Yp(r.y0)
            cv.saveState()
            cp = cv.beginPath(); cp.rect(x0_, y0_, x1_ - x0_, y1_ - y0_); cv.clipPath(cp, stroke=0, fill=0)
            cv.setStrokeColorRGB(0, 0, 0); cv.setLineWidth(LW_THIN)
            st = 2.4
            n = int((y1_ - y0_ + (x1_ - x0_)) / st) + 2
            for m in range(n):
                yy = y0_ + m * st
                cv.line(x0_, yy, x1_, yy + (x1_ - x0_))
            cv.restoreState()
            cv.saveState(); cv.setLineWidth(LW_VIS)
            cv.rect(x0_, y0_, x1_ - x0_, y1_ - y0_, stroke=1, fill=0); cv.restoreState()

    # --- CAD varžtas
    def bolt(ax, a0, a1, hd, dia, vertical, head_at_start):
        L = abs(a1 - a0)
        s_ = 1 if a1 > a0 else -1
        h0 = a0 if head_at_start else a1
        hs = s_ if head_at_start else -s_
        hw = dia * 2.2

        def R(u0, u1, v0, v1):
            if vertical:
                xa, xb, ya, yb = X(ax + v0), X(ax + v1), Yp(min(u0, u1)), Yp(max(u0, u1))
            else:
                xa, xb, ya, yb = X(min(u0, u1)), X(max(u0, u1)), Yp(ax + v0), Yp(ax + v1)
            cv.saveState(); cv.setFillColorRGB(*(PAL["bolt"] if COLOR else (1, 1, 1))); cv.setStrokeColorRGB(0, 0, 0)
            cv.setLineWidth(LW_VIS if not COLOR else 0.25)
            cv.rect(xa, H - yb, xb - xa, yb - ya, stroke=1, fill=1); cv.restoreState()

        def Lw(u0, u1, v, lw_, dash=None):
            if vertical:
                p0, p1 = (X(ax + v), H - Yp(u0)), (X(ax + v), H - Yp(u1))
            else:
                p0, p1 = (X(u0), H - Yp(ax + v)), (X(u1), H - Yp(ax + v))
            cv.saveState(); cv.setStrokeColorRGB(0, 0, 0); cv.setLineWidth(lw_)
            if dash:
                cv.setDash(*dash)
            cv.line(*p0, *p1); cv.restoreState()
        R(h0, h0 + hs * hd, -hw / 2, hw / 2)
        R(h0 + hs * hd, h0 + hs * L, -dia / 2, dia / 2)
        th0 = h0 + hs * (hd + L * 0.35)
        for v in (-dia * 0.36, dia * 0.36):
            Lw(th0, h0 + hs * L, v, LW_THIN)
        Lw(th0, th0, 0, LW_THIN)
        Lw(h0 - hs * dia * 0.8, h0 + hs * (L + dia * 0.8), 0, LW_THIN, ([2.5, 0.8, 0.5, 0.8], 0))

    for r, thr in bolts:
        if r.height > r.width:
            dia = thr.width if thr else r.width / 2.2
            tg, bg = ((thr.y0 - r.y0), (r.y1 - thr.y1)) if thr else (1, 0)
            bolt((r.x0 + r.x1) / 2, r.y0, r.y1, max(tg, bg, 0.7), dia, True, tg >= bg)
        else:
            dia = thr.height if thr else r.height / 2.2
            lg, rg = ((thr.x0 - r.x0), (r.x1 - thr.x1)) if thr else (1, 0)
            bolt((r.y0 + r.y1) / 2, r.x0, r.x1, max(lg, rg, 0.7), dia, False, lg >= rg)

    # --- ausėlės (kai užklausoje yra; Rytis 2026-10-07): L - horizontali kojelė U viduje ant rėmo vidaus flanšo,
    #     vertikali kojelė sienos plokštumoje, nukreipta į rėmo vidų; Ø6 skylė - ašinė + nematomos briaunos
    if ears is not None and kind == "square":
        # Rytis 2026-10-07 (P6_mm_staciakampis_Alu_profilis_su_3mm_tvirtinimo_auselemis.pdf): prie stačiakampio
        # Alu profilio PRIVIRINAMA 3 mm Alu ausėlė - plokštelė sienos plokštumoje (tarp profilio ir sienos), per visą
        # profilio aukštį + išsikišimas į rėmo vidų (= profilio aukštis), Ø skylė išsikišime
        tube = None
        for i, d in enumerate(dr):
            f_ = d.get("fill")
            if i not in skip and f_ and 0.6 < max(f_) < 0.75 and d["rect"].width < 14 and d["rect"].height > 30 \
                    and _kinds(d).count("l") >= 16:
                tube = d["rect"]
        if tube is not None:
            sz = tube.width
            rails = [fitz.Rect(tube.x0, tube.y0, tube.x1, tube.y0 + sz), fitz.Rect(tube.x0, tube.y1 - sz, tube.x1, tube.y1)]
            t3 = max(0.9, sz * 3 / 60)                  # 3 mm, bet pjūvyje matomas kaip juoda juosta
            tip = None
            for n_, r in enumerate(rails):
                wl, down = r.x0, (n_ == 0)
                y0_, y1_ = (r.y0, r.y1 + sz) if down else (r.y0 - sz, r.y1)
                hy = (r.y1 + sz / 2) if down else (r.y0 - sz / 2)
                cv.saveState(); _sheet(cv, "ear")
                cv.rect(X(wl - t3), H - Yp(y1_), t3 * k, (y1_ - y0_) * k, stroke=1, fill=1); cv.restoreState()
                hr = sz * ear_hole / 2
                cv.saveState(); cv.setFillColorRGB(1, 1, 1)
                cv.rect(X(wl - t3) - 0.1, H - Yp(hy + hr), t3 * k + 0.2, 2 * hr * k, stroke=0, fill=1)
                cv.setStrokeColorRGB(0, 0, 0); cv.setLineWidth(LW_THIN); cv.setDash([1.2, 0.8], 0)
                for yy in (hy - hr, hy + hr):
                    cv.line(X(wl - t3), H - Yp(yy), X(wl), H - Yp(yy))
                cv.setDash([2.5, 0.8, 0.5, 0.8], 0)
                cv.line(X(wl - t3) - 4, H - Yp(hy), X(wl) + 4, H - Yp(hy))
                cv.restoreState()
                if down:
                    tip = (wl - t3 / 2, r.y1 + sz * 0.8)
            if tip and ears:
                leader(X(tip[0]), Yp(tip[1]), X(tip[0]) - 22, Yp(tip[1]) + 4, str(ears), 6.5)
    if bracket is not None and kind != "folded":
        # v94 (Rytis 2026-10-11): U laikiklis pjūvyje - sienelė prie fasado per visą rėmo aukštį, viršutinė ir apatinė
        #  plokštuma (profilis + 3); rėmas guli ant apatinės plokštumos, viršuje 2 mm laisvumas; Ø6 per plokštumas į bėgelį
        bk = max((d["rect"] for i, d in enumerate(dr) if i not in skip and d.get("fill") and 0.6 < max(d["fill"]) < 0.75
                  and d["rect"].height > 40), key=lambda r: r.height, default=None)
        if kind == "square":
            tube = max((d["rect"] for i, d in enumerate(dr) if i not in skip and d.get("fill") and 0.6 < max(d["fill"]) < 0.75
                        and d["rect"].width < 14 and d["rect"].height > 30), key=lambda r: r.height, default=None)
            rr = [fitz.Rect(tube.x0, tube.y0, tube.x1, tube.y0 + tube.width),
                  fitz.Rect(tube.x0, tube.y1 - tube.width, tube.x1, tube.y1)] if tube else []
        else:
            rr = sorted([d["rect"] for i, d in enumerate(dr) if i not in skip and bk is not None and d.get("fill")
                         and 0.6 < max(d["fill"]) < 0.75 and d["rect"].x1 <= bk.x0 + 0.2 and d["rect"].height > 5],
                        key=lambda r: r.y0)
            rr = [rr[0], rr[-1]] if len(rr) >= 2 else []
        if rr:
            top_, bot_ = rr
            es = top_.height
            mm = es / 30.0
            t3, gp = 3 * mm, 2 * mm
            wl = min(top_.x0, bot_.x0)
            rw = max(top_.width, bot_.width)
            ya, yb = top_.y0 - gp - t3, bot_.y1 + t3
            cv.saveState(); _sheet(cv, "ear")
            pth = cv.beginPath()
            pts = [(wl - t3, ya), (wl + rw, ya), (wl + rw, ya + t3), (wl, ya + t3), (wl, yb - t3), (wl + rw, yb - t3),
                   (wl + rw, yb), (wl - t3, yb)]
            pth.moveTo(X(pts[0][0]), H - Yp(pts[0][1]))
            for px_, py_ in pts[1:]:
                pth.lineTo(X(px_), H - Yp(py_))
            pth.close(); cv.drawPath(pth, stroke=1, fill=1); cv.restoreState()
            cx_ = wl + rw / 2                                   # Ø6 per plokštumas - ašinė
            cv.saveState(); cv.setStrokeColorRGB(0, 0, 0); cv.setLineWidth(LW_THIN); cv.setDash([2.5, 0.8, 0.5, 0.8], 0)
            for y_a, y_b in ((ya - 3 * mm, top_.y0 + es * 0.5), (bot_.y1 - es * 0.5, yb + 3 * mm)):
                cv.line(X(cx_), H - Yp(y_a), X(cx_), H - Yp(y_b))
            cv.restoreState()
            if bracket:
                tip = (wl - t3 / 2, (top_.y1 + bot_.y0) / 2)
                leader(X(tip[0]), Yp(tip[1]), X(tip[0]) - 22, Yp(tip[1]) + 4, str(bracket), 6.5)
    if ears is not None and kind not in ("folded", "square"):
        bk = max((d["rect"] for i, d in enumerate(dr) if i not in skip and d.get("fill") and 0.6 < max(d["fill"]) < 0.75
                  and d["rect"].height > 40), key=lambda r: r.height, default=None)
        rails = [d["rect"] for i, d in enumerate(dr) if i not in skip and bk is not None and d.get("fill")
                 and 0.6 < max(d["fill"]) < 0.75 and d["rect"].x1 <= bk.x0 + 0.2 and d["rect"].height > 5]
        rails.sort(key=lambda r: r.y0)
        if len(rails) >= 2:
            rails = [rails[0], rails[-1]]
        t = 0.63
        ear_tip = None
        for n_, r in enumerate(rails):
            es, wl, rw = r.height, r.x0, r.width
            down = (n_ == 0)                         # viršutinis - į apačią, apatinis - į viršų
            if down:
                fy = r.y1 - t                        # flanšo vidinė plokštuma
                pts = [(wl - t, fy - t), (wl + 0.72 * rw, fy - t), (wl + 0.72 * rw, fy), (wl, fy), (wl, r.y1 + es),
                       (wl - t, r.y1 + es)]
                hy = r.y1 + es / 2
            else:
                fy = r.y0 + t
                pts = [(wl - t, fy + t), (wl + 0.72 * rw, fy + t), (wl + 0.72 * rw, fy), (wl, fy), (wl, r.y0 - es),
                       (wl - t, r.y0 - es)]
                hy = r.y0 - es / 2
            cv.saveState(); _sheet(cv, "ear")
            pth = cv.beginPath(); pth.moveTo(X(pts[0][0]), H - Yp(pts[0][1]))
            for px_, py_ in pts[1:]:
                pth.lineTo(X(px_), H - Yp(py_))
            pth.close(); cv.drawPath(pth, stroke=1, fill=1); cv.restoreState()
            hr = es * ear_hole / 2                   # skylė / profilis (Ø6/30, Ø8/40)
            cv.saveState(); cv.setStrokeColorRGB(1, 1, 1); cv.setLineWidth(0.5)
            cv.rect(X(wl - t) - 0.2, H - Yp(hy + hr), t * k + 0.4, 2 * hr * k, stroke=0, fill=0)
            cv.setFillColorRGB(1, 1, 1)
            cv.rect(X(wl - t) - 0.1, H - Yp(hy + hr), t * k + 0.2, 2 * hr * k, stroke=0, fill=1)
            cv.setStrokeColorRGB(0, 0, 0); cv.setLineWidth(LW_THIN); cv.setDash([1.2, 0.8], 0)
            for yy in (hy - hr, hy + hr):
                cv.line(X(wl - t), H - Yp(yy), X(wl), H - Yp(yy))
            cv.setDash([2.5, 0.8, 0.5, 0.8], 0)
            cv.line(X(wl - t) - 4, H - Yp(hy), X(wl) + 4, H - Yp(hy))
            cv.restoreState()
            if down:
                ear_tip = (wl - t / 2, r.y1 + es * 0.85)
        if ear_tip and ears:
            leader(X(ear_tip[0]), Yp(ear_tip[1]), X(ear_tip[0]) - 22, Yp(ear_tip[1]) + 4, str(ears), 6.5)

    # --- balionai
    for j, tp in leads:
        bj = dr[j]["rect"]
        _l = lab.get(j, "")
        leader(X(tp.x), Yp(tp.y), X((bj.x0 + bj.x1) / 2), Yp((bj.y0 + bj.y1) / 2), LABEL_MAP.get(_l, _l), 6.5)
    if not F8 and pvc:                                                  # A - PVC juosta (tik 3 mm)
        pr = min((dr[i]["rect"] for i in pvc), key=lambda r: r.y0)
        pl = dr[plex]["rect"]
        leader(X(pr.x0 + pr.width * 0.3), Yp((pr.y0 + pr.y1) / 2), X(pl.x1) + 20, Yp(pr.y1) + 16, LABEL_MAP.get("A", "A"), 6.5)

    # --- gylio matmuo: galo išorė -> plexi priekis
    def grey(f_):
        return f_ and abs(f_[0] - 0.435) < 0.03
    ret = min((d["rect"] for d in dr if grey(d.get("fill")) and d["rect"].width > 20), key=lambda r: r.y0)
    pl = dr[plex]["rect"]
    hdim(X(ret.x0), X(pl.x1), Yp(min(ret.y0, pl.y0)) - 10, f"{depth:.0f}", Yp(ret.y0), Yp(pl.y0))
