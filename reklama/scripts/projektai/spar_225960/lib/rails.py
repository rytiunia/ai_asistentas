from core import *

WHITE = lambda c: c is not None and min(c) > 0.85

def classify(ds):
    faces, logos, rails, marks = [], [], [], []
    for d in ds:
        f = d.get('fill') if 'f' in d['type'] else None
        r = d['rect']
        if d['type'] == 's' or (r.width < 3.2 and r.height < 3.2):
            marks.append(d)
        elif WHITE(f):
            faces.append(d)
        elif f is not None and (max(f) - min(f)) > 0.4 and not (f[0] > 0.5 and f[1] > 0.3 and f[2] > 0.2 and f[0] - f[2] < 0.45):
            logos.append(d)  # saturated colour = logo / shape face
        else:
            rails.append(d)
    # white pictograms lying inside a logo -> belong to logo face
    pict = []
    for d in faces:
        for L in logos:
            if L['rect'].contains(d['rect']) and L['rect'].width < 3 * d['rect'].width + 999:
                if L['rect'].contains(d['rect']): pict.append(d); break
    faces = [d for d in faces if d not in pict]
    return faces, logos, pict, rails, marks

def rail_sheet(out, it, sheet, total):
    bk = it.get("base", "rails")
    pg = base(out, bk, [(44, 30, 903, 772)], keeps=[(146, 498, 272, 616)] if bk == "rails" else [], touch=[(60, 445, 165, 530)] if bk == "inside" else [],
              title=TITLE, sheet=f"Sheet {sheet} of {total}", pcs=it.get("pcs", "1 pcs."))
    cp = fitz.open(it["src"])[0]
    ds = pick(cp, it["view"], it.get("drop", ()))
    faces, logos, pict, rails, marks = classify(ds)
    G = bbox(faces + logos)               # sign extent (letters + logo)
    Ds = bbox(faces) if it.get("scale_by") == "faces" else G
    mmpp = it["W"] / Ds.width               # mm per client pt (horizontal)
    mmpv = it["H"] / Ds.height              # vertical
    side = RAL[it["side"]]; frame = RAL[it["frame"]]
    lside = RAL.get(it.get("logo_side", it["side"]))

    # ---------- FRONT ----------
    FR = fitz.Rect(it.get("front_box", (95, 92, 815, 238)))
    M, s, R = fit(G, FR)
    rc = lambda d, f, c: ((frame if f is not None else None), c) if d in rails else (f, c)
    draw(pg, rails, M, recolor=lambda d, f, c: (frame, None))
    draw(pg, marks, M, maxw=0.3)
    if it.get("logo_behind"): draw(pg, logos, M)
    draw(pg, faces, M, outline=(0.25, 0.25, 0.25), maxw=0.35)
    if not it.get("logo_behind"): draw(pg, logos, M)
    draw(pg, pict, M)
    # dims
    D = Ds * M
    hdim(pg, D.x0, D.x1, R.y0 - 22, D.y0, f"{it['Wtxt']} mm", 13)
    vdim(pg, R.x0 - 22, D.y0, D.y1, D.x0, f"{it['Htxt']} mm", 13)
    if faces:
        F = bbox(faces) * M
        if logos and F.height < R.height - 3 and it.get("scale_by") != "faces":
            hmm = round(bbox(faces).height * mmpv)
            vdim(pg, F.x1 + 10 if not it.get("lh_left") else R.x0 - 8, F.y0, F.y1, None, f"{hmm} mm", 10, left=False)
        if logos:
            Lr = bbox(logos) * M
            dmm = round(bbox(logos).height * mmpv)
            hdim(pg, Lr.x0, Lr.x1, R.y1 + 16, R.y1, f"⌀{dmm} mm", 11, up=False)
    for (xmm, lab) in it.get("splits", []):
        x = R.x0 + xmm / mmpp * s
        pg.draw_line((x, R.y0 - 34), (x, R.y1 + 8), color=RED, width=0.8, dashes="[8 3 2 3] 0")
        hdim(pg, R.x0, x, R.y0 - 8, None, f"{xmm} mm", 10)
        hdim(pg, x, R.x1, R.y0 - 8, None, f"{it['W'] - xmm:g} mm", 10)
        text(pg, x + 4, R.y0 - 38, lab, 10, RED)
    # side view(s)
    dpt = it.get("depth", 80)
    sx = 848; hpx = R.height
    bars = [(it["side"], R.y0, R.y1)]
    if logos:
        bars = [(it["side"], (bbox(faces) * M).y0, (bbox(faces) * M).y1), (it.get("logo_side", it["side"]), R.y0, R.y1)]
    for i, (col, y0, y1) in enumerate(bars):
        x = sx + i * 26
        w = max((it.get("logo_depth", dpt) if i == 1 else dpt) / mmpp * s, 3 if i == 1 else 6)
        if i == 1 and it.get("logo_behind"): x = sx - 3 - w
        pg.draw_rect(fitz.Rect(x, y0, x + w, y1), color=(0.15, 0.15, 0.15), fill=RAL[col], width=0.35)
        pg.draw_rect(fitz.Rect(x - 3, y0 + (y1 - y0) * 0.12, x, y0 + (y1 - y0) * 0.2), color=None, fill=frame)
        pg.draw_rect(fitz.Rect(x - 3, y1 - (y1 - y0) * 0.2, x, y1 - (y1 - y0) * 0.12), color=None, fill=frame)
    text(pg, sx + 4, R.y0 - 26, f"{dpt} mm", 12)
    pg.draw_line((sx, R.y0 - 22), (sx + max(dpt / mmpp * s, 6), R.y0 - 22), color=(0, 0, 0), width=LW)

    # ---------- REAR (mirrored) ----------
    RB = fitz.Rect(it.get("rear_box", (95, 318, 815, 452)))
    Mr, sr, Rr = fit(G, RB, mirror=True)
    draw(pg, faces, Mr, recolor=lambda d, f, c: (side, (0.2, 0.2, 0.2)), maxw=0.35)
    for L in logos:
        q = L['rect'] * Mr
        if abs(L['rect'].width - L['rect'].height) < 0.12 * L['rect'].width:
            pg.draw_oval(q, color=(0.2, 0.2, 0.2), fill=lside, width=0.35)
        else:
            draw(pg, [L], Mr, recolor=lambda d, f, c: (lside, (0.2, 0.2, 0.2)), maxw=0.35)
    draw(pg, rails, Mr, recolor=lambda d, f, c: (frame, None))
    draw(pg, marks, Mr, maxw=0.3)
    # cable output(s) on rear: converter above rear view, lead down to top rail
    rails_bb = bbox(rails) * Mr
    ncab = len(it["cables"])
    cw = 215; ch = cw * 45 / 313
    for j, cab in enumerate(it["cables"]):
        fx = cab.get("at", (0.85,) if ncab == 1 else (0.2, 0.75)[j] if True else 0.5)
        if isinstance(fx, tuple): fx = fx[0]
        tx = rails_bb.x0 + rails_bb.width * fx
        p1 = fitz.Point(tx, rails_bb.y0 + 1)
        cx = min(max(tx - cw * 0.93, 50), 880 - cw); cy = 262
        converter(pg, (cx, cy, cx + cw, cy + ch))
        p0 = fitz.Point(cx + cw * 0.995, cy + ch * 0.5)
        sh = pg.new_shape()
        m1 = fitz.Point(p0.x + 6, p0.y); m2 = fitz.Point(p1.x, p1.y - 10)
        sh.draw_bezier(p0, p0 + (14, 0), m2 + (18, -6), m2)
        # wavy tail
        w = [m2]
        for k in range(1, 5):
            w.append(fitz.Point(p1.x + (4 if k % 2 else -4), m2.y + (p1.y - m2.y) * k / 4))
        for k in range(4): sh.draw_line(w[k], w[k + 1])
        sh.finish(color=(0.1, 0.1, 0.1), width=0.6, closePath=False); sh.commit()
        pg.draw_circle(p1, 1.6, color=None, fill=RED)
        if cab.get("note"): text(pg, cx + 30, cy + ch + 8, cab["note"], 9, RED)
    if bk != "rails":
        lines(pg, 60, 470, it.get("rear_note", []), 13)
    # mounting plates note + leader
    n = len([m for m in marks if m['type'] == 's'])
    if bk != "rails": marks_note = False
    if bk == "rails": lines(pg, 60, 476, ["Aluminium L profile", (f"mounting plates, {it.get('plates', n)} pcs." if it.get('plates', n) >= 4 else "mounting plates"), "Ø8mm holes"], 11)
    if marks and bk == "rails":
        mp = sorted([m for m in marks if m['type']=='s'] or marks, key=lambda m: m['rect'].x1)[-1]['rect'] * Mr
        pg.draw_line((250, 520), ((mp.x0 + mp.x1) / 2, (mp.y0 + mp.y1) / 2), color=(0, 0, 0), width=0.35)
        pg.draw_circle(((mp.x0 + mp.x1) / 2, (mp.y0 + mp.y1) / 2), 1.2, color=None, fill=(0, 0, 0))

    # ---------- 3D ----------
    B3 = fitz.Rect(it.get("box3d", (300, 535, 880, 765)))
    rot = math.radians(-11)
    A = fitz.Matrix(math.cos(rot), math.sin(rot), -math.sin(rot) + 0.38, math.cos(rot), 0, 0)
    corners = [fitz.Point(G.x0, G.y0) * A, fitz.Point(G.x1, G.y0) * A, fitz.Point(G.x0, G.y1) * A, fitz.Point(G.x1, G.y1) * A]
    xs = [c.x for c in corners]; ys = [c.y for c in corners]
    GA = fitz.Rect(min(xs), min(ys), max(xs), max(ys))
    M3, s3, R3 = fit(GA, fitz.Rect(B3.x0, B3.y0 + 12, B3.x1 - 14, B3.y1))
    M3 = A * M3
    depth = dpt / mmpp * s3 * 0.9
    steps = 14
    if it.get("logo_behind"):
        ld = it.get("logo_depth", 3) / mmpp * s3 * 0.9 + depth
        for k in range(steps, 0, -1):
            off = fitz.Matrix(1, 0, 0, 1, ld * k / steps * 0.55, ld * k / steps * 0.75)
            draw(pg, logos, M3 * off, recolor=lambda d, f, c: (tuple(v * 0.8 for v in lside), None))
        offl = fitz.Matrix(1, 0, 0, 1, depth * 0.55, depth * 0.75)
        draw(pg, logos, M3 * offl)
    for k in range(steps, 0, -1):
        off = fitz.Matrix(1, 0, 0, 1, depth * k / steps * 0.55, depth * k / steps * 0.75)
        draw(pg, faces, M3 * off, recolor=lambda d, f, c: (tuple(v * 0.88 for v in side) if min(side) > 0.6 else side, None))
        if not it.get("logo_behind"): draw(pg, logos, M3 * off, recolor=lambda d, f, c: (tuple(v * 0.8 for v in lside), None))
    off = fitz.Matrix(1, 0, 0, 1, depth * 0.55, depth * 0.75)
    draw(pg, faces, M3 * off, recolor=lambda d, f, c: (None, (0.2, 0.2, 0.2)), maxw=0.3)
    draw(pg, faces, M3, outline=(0.15, 0.15, 0.15), maxw=0.4)
    if not it.get("logo_behind"): draw(pg, logos, M3)
    draw(pg, pict, M3)

    # ---------- panel values ----------
    panel_rails(pg, it, faces, logos, mmpp)
    return pg

def put_box(pg, y0, y1, s, x0=965.2, x1=1124, size=8.5):
    pg.add_redact_annot(fitz.Rect(x0 + 1, y0 + 1, x1, y1 - 1), fill=False)

ROWS = {
  "rails": {"m1": (338.7, 352.7), "m2": (354.7, 368.6), "d1": (497.9, 511.8), "d2": (513.8, 527.8), "side": (546.3, 560.2), "frame": (574.9, 588.8),
            "l2": (629.5, 643.4), "c1": (673.4, 687.4), "c2": (689.9, 703.8), "per": (723.1, 737.0)},
  "inside": {"m1": (339.7, 353.7), "m2": (355.7, 369.6), "d1": (498.9, 512.8), "d2": (514.8, 528.8), "side": (547.3, 561.2), "frame": (575.9, 589.8),
            "l2": (630.4, 644.4), "c1": (674.4, 688.4), "c2": (690.8, 704.8), "per": (724.1, 738.0)},
}
def panel_rails(pg, it, faces, logos, mmpp):
    bk = it.get("base", "rails"); R_ = ROWS[bk]
    vals = {}
    st = f"RAL {it['side']}" + (f" / RAL {it['logo_side']} ({it.get('logo_word','logo')})" if it.get("logo_side") else "")
    vals["side"] = (st, RAL[it["side"]])
    vals["frame"] = (it.get("frame_txt", f"RAL {it['frame']}"), RAL[it["frame"]])
    cols = it.get("colors", [])
    vals["c1"] = cols[0] if cols else ("", None)
    vals["c2"] = cols[1] if len(cols) > 1 else ("", None)
    per = path_len(faces) * mmpp / 1000
    if not it.get("no_logo_per"):
        for L in logos:
            if abs(L['rect'].width - L['rect'].height) < 0.1 * L['rect'].width:
                per += math.pi * L['rect'].width * mmpp / 1000
    it["perimeter_m"] = per
    vals["per"] = (f"{math.ceil(per)} meters", "center")
    vals.update(it.get("panel", {}))
    for k, v in vals.items():
        a, b = R_[k]
        pg.add_redact_annot(fitz.Rect(966.5, a + 1, 1126 if k in ("m1", "m2") else 1140.5, b - 1), fill=(1, 1, 1))
        if len(v) > 1 and v[1] is not None and v[1] != "center" or k in ("side", "frame", "c1", "c2"):
            pg.add_redact_annot(fitz.Rect(942, a - 0.5, 958.6, b + 0.5), fill=(1, 1, 1))
    pg.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_REMOVE_IF_COVERED)
    for k, v in vals.items():
        a, b = R_[k]; s_ = v[0]; c = v[1] if len(v) > 1 else None
        if c == "center": text(pg, 1053, b - 4, s_, 8.5, align="c")
        else: text(pg, 970, b - 4, s_, 8.5)
        if isinstance(c, tuple):
            pg.draw_rect(fitz.Rect(943, a, 958.1, b), color=(0.4, 0.4, 0.4), fill=c, width=0.4)
        elif k in ("side", "frame", "c1", "c2"):
            pg.draw_rect(fitz.Rect(943, a, 958.1, b), color=(0.4, 0.4, 0.4), fill=(1, 1, 1), width=0.4)

TITLE = "SPAR Ottersøy Prosjekt NO_4002894"
