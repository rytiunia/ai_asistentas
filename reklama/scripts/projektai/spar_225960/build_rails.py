"""SPAR order 225960 - raidžių ant rėmo lapai (skill reklama, buv. iskabu-techninis-lapas v11, braizyti_begeliai.py)."""
import sys, json, subprocess
sys.path.insert(0, '/home/claude/w/lib'); sys.path.insert(0, '/home/claude/v9/scripts')
from mkclient2 import make
import pymupdf as fitz, lapas_core as K

DATE = "2026-10-08"
WHITE = [1, 1, 1]
G2 = [0.85, 0.85, 0.85]           # antros raidžių grupės spalva kliento faile (tik atskyrimui)
PICT = [0.7, 0.9, 0.7]            # piktogramos (lipduko) spalva kliento faile
COMP = (0.17, 0.17, 0.17)         # KAFFEPAUSE: juodas kompozitas (apskritimas + rėmo atkartojimas) kliento faile
ORG = (1.0, 0.4, 0.0)             # KAFFEPAUSE: plėvelė ant apskritimo
SC = "/home/claude/v9/scripts"


def run(key, sheet, title, scale, view, src, groups, rail, cables, md, bom, depth=80, client=None, extra=None):
    make(src, view, f"sk/{key}_client.pdf", **(client or {}))
    sg = []
    for g in groups:
        d = {"name": g["name"], "profile": "6", "on_plate": False, "return_ral": g["ret"], "face_hex": g["face_hex"],
             "client_fill": g["fill"], "frame": g.get("frame", "verticals")}
        for k in ("rails", "behind", "no_rails", "depth_mm", "z0", "ears_rails", "ears_smax", "lit", "cable", "ears", "ears_pt"):
            if k in g: d[k] = g[k]
        sg.append(d)
    spec = {"scale": scale, "qty": "1 pcs.", "order_no": "ALT0000_00.00_RS", "rev": "A", "date": DATE,
            "client": "BrandFactory", "title": f"SPAR order 225960 - {title}", "drawing_no": "SPAR order 225960",
            "file_code": f"SPAR_225960_{sheet:02d}_{key}", "sheet": f"{sheet} / 18",
            "client_pdf": f"/home/claude/w/sk/{key}_client.pdf", "crop_pt": list(view), "depth_mm": depth, "front": "8mm",
            "rail": rail, "cable_exits": cables, "groups": sg, "bom": bom, "main_data": md, "export_1to1": False,
            "trafo_box": {"voltage": "12V", "mains": "220V", "cable_len_m": 3.0}}
    spec.update(extra or {})
    json.dump(spec, open(f"sk9/{key}.json", "w"), ensure_ascii=False, indent=1)
    r = subprocess.run(["python3", "braizyti_begeliai.py", f"/home/claude/w/sk9/{key}.json", f"/home/claude/w/sk9/{key}.pdf"],
                       cwd=SC, capture_output=True, text=True)
    print(key, "\n".join(l for l in r.stdout.splitlines() if "ausėl" in l or l.startswith("OK") or "!" in l)[-1500:], r.stderr[-1500:])


def letters_mm(src, view, scale, split=None):
    """raidžių bbox mm (nuo visų raidžių + logotipo kairės / viršaus) - rėmo bėgeliams"""
    import sys; sys.path.insert(0, '/home/claude/w/lib')
    from rails import pick, classify, bbox
    cp = fitz.open(src)[0]
    f, l, p, r, m = classify(pick(cp, view, keep_small_squares=False))
    S = scale * 25.4 / 72
    out = []
    for d in f:
        for L in K.split_letters(K.drawing_to_subpaths(d, lambda q: q)):
            out.append([v * S for v in L["bb"]])
    for d in l:
        out.append([v * S for v in (d["rect"].x0, d["rect"].y0, d["rect"].x1, d["rect"].y1)])
    return out


def rail_start_in(src, view, scale, letter_bb, edges_y, margin=30):
    """v15 (Rytis 2026-10-08): bėgelio pradžia NEIŠSIKIŠA už pirmos raidės (pvz. S) - kairiausias raidės kontūro taškas
    ties bėgelio briaunomis (abs. mm) + margin; grąžina abs. mm"""
    from rails import pick, classify
    from shapely.geometry import LineString
    from shapely import affinity
    cp = fitz.open(src)[0]
    f, l, p, r, m = classify(pick(cp, view, keep_small_squares=False))
    S = scale * 25.4 / 72
    best = None
    for d in f:
        for L in K.split_letters(K.drawing_to_subpaths(d, lambda q: q)):
            bb = [v * S for v in L["bb"]]
            if max(abs(a - b) for a, b in zip(bb, letter_bb)) < 1.0:
                best = affinity.scale(K.shape_geom(L["sub"]), S, S, origin=(0, 0))
    if best is None:
        return letter_bb[0] + margin
    xs = []
    for y in edges_y:
        ln = LineString([(letter_bb[0] - 50, y), (letter_bb[2] + 50, y)])
        it = best.intersection(ln)
        xs.append(it.bounds[0] if not it.is_empty else letter_bb[0])
    return max(xs) + margin


def rails_y_mm(src, view, scale):
    """kliento horizontalių bėgelių y centrai (mm, nuo visų raidžių viršaus) ir x ribos"""
    from rails import pick, classify
    cp = fitz.open(src)[0]
    f, l, p, r, m = classify(pick(cp, view, keep_small_squares=False))
    S = scale * 25.4 / 72
    top = min([d["rect"].y0 for d in f + l])
    left = min([d["rect"].x0 for d in f + l])
    hs = [d["rect"] for d in r if d["rect"].width > 6 * max(d["rect"].height, 0.1)]
    return sorted({round(((q.y0 + q.y1) / 2 - top) * S) for q in hs}), left * S, top * S


def md(size, profile, depth, face, ret, rails, power, extra=()):
    return [["Quantity", "1 pcs."], ["Overall size", size], ["Profile", profile], ["Letter depth", str(depth)], ["Face", face],
            ["Returns", ret], ["Frame", rails], ["Illumination", "LED white"], ["Power", power], ["Wind qp", "{WIND_QP} kN/m²"],
            ["Wall", "?"], ["Perimeter", "{PER_ALL} m"]] + list(extra)


def bom(faces, rets, frame_rows, extra=()):
    rows = [[1, *f] for f in faces] + [[2, *r] for r in rets]
    rows += [[3, "Letter back", "Alu 1.5 mm", "-", "{PER_ALL} m / {A_ALL} m²"], [4, "LED modules", "", "white", "?"]]
    rows += frame_rows
    rows += [[7, "Trafo box (PSU 12V)", "", "", "1 pcs."], [8, "Wall fixing", "?", "-", "?"]]
    return rows + list(extra)


U30 = lambda ral: [[5, "Rail U {RAIL_SIZE}", "Aluminium", f"RAL {ral}", "{RAIL_TOTAL_M} m"],
                   [6, "Mounting ear {RAIL_SIZE}, Ø{EAR_HOLE} hole", "Aluminium", f"RAL {ral}", "{PLATES_N} pcs. ({PLATES_EXT} extended)"]]
SQ40 = lambda ral: [[5, "Frame, rectangular tube 40x40x2", "Aluminium", f"RAL {ral}", "{RAIL_TOTAL_M} m"],
                    [6, "Mounting ear, welded, Ø{EAR_HOLE} hole", "Alu 3 mm", f"RAL {ral}", "{PLATES_N} pcs. ({PLATES_EXT} extended)"]]
UTOP = lambda ral: [[5, "Rail U {RAIL_SIZE}", "Aluminium", f"RAL {ral}", "{RAIL_TOTAL_M} m"],
                    [6, "No ears - top rail screwed directly to wall", "", "", "-"]]
CAB = lambda x, y: {"pt": [x, y], "voltage": "12V", "label": "3 m"}
FACE_W = ("Plexi 8 mm white (opal)", "white")
FACE_LOGO = ("Plexi 8 mm white + foil", "ORACAL 8500 614")

if __name__ == "__main__":
    which = sys.argv[1:]
    P1, P2, P3, P4 = "t/clean_p1.pdf", "t/clean_p2.pdf", "t/clean_p3.pdf", "t/clean_p4.pdf"

    # ---------------- 1: SPAR 8000 - 2 dalys (SPA | R + logo), stačiakampis rėmas 40x40x2 su privirintomis ausėlėmis
    if not which or "spar8000" in which:
        V = (100, 110, 345, 166)
        bbs = letters_mm(P1, V, 100)
        lx0 = min(b[0] for b in bbs)
        let = sorted([b for b in bbs if b[3] - b[1] < 1200], key=lambda b: b[0])     # S P A R
        logo = [b for b in bbs if b[3] - b[1] >= 1200][0]
        S_, R_ = let[0], let[3]
        ly0, ly1 = min(b[1] for b in let), max(b[3] for b in let)
        t = 40; yT, yB = 100, (ly1 - ly0) - 100
        def frame(x0, x1, verts):
            rs = [{"kind": "h", "poly": [[x0, yc - t / 2], [x1, yc - t / 2], [x1, yc + t / 2], [x0, yc + t / 2]]} for yc in (yT, yB)]
            rs += [{"kind": "v", "poly": [[xv, yT + t / 2], [xv + t, yT + t / 2], [xv + t, yB - t / 2], [xv, yB - t / 2]]} for xv in verts]
            return rs
        # Rytis 2026-10-08: statmenų NĖRA; horizontalūs bėgeliai per visą reklamą, sujungiami tarp A ir R (2 dalys)
        xj = (let[2][2] + R_[0]) / 2                                       # jungtis tarp A ir R
        # Rytis 2026-10-08 (5): rėmas ties S per ilgas - pradžia pagal S kontūrą ties abiejų bėgelių briaunomis
        xs0 = rail_start_in(P1, V, 100, S_, [ly0 + yc + e * t / 2 for yc in (yT, yB) for e in (-1, 1)]) - S_[0]
        f1 = frame(xs0, xj - S_[0] - 2, [])
        # Rytis 2026-10-08 (3): bėgelis NEIŠSIKIŠA už apskritimo - galas pagal stygą ties bėgelio išorine briauna, 30 mm į vidų
        import math as _m
        cxl, cyl, rl = (logo[0] + logo[2]) / 2, (logo[1] + logo[3]) / 2, (logo[2] - logo[0]) / 2
        def _end(yc, outer):
            ya = ly0 + yc + outer * t / 2
            return cxl + _m.sqrt(max(rl ** 2 - (ya - cyl) ** 2, 0)) - 30 - R_[0]
        f2 = []
        for yc, outer in ((yT, -1), (yB, 1)):
            x0_, x1_ = xj - R_[0] + 2, _end(yc, outer)
            f2.append({"kind": "h", "poly": [[x0_, yc - t / 2], [x1_, yc - t / 2], [x1_, yc + t / 2], [x0_, yc + t / 2]]})
        # Rytis 2026-10-08 (3): laidų išvestys ir ausėlės - tiksliai kaip kliento faile
        EP1 = [150.3, 188.6, 231.1]; EP2 = [235.4, 277.9, 299.1, 324.7]
        G = [{"name": "SPA", "ret": "9016", "face_hex": "#FFFFFF", "fill": WHITE, "rails": f1,
              "cable": False, "ears_pt": EP1},       # Rytis 2026-10-08 (4): VIENAS laidas - prie žalio apskritimo
             {"name": "R", "ret": "9016", "face_hex": "#FFFFFF", "fill": G2, "rails": f2,
              "cable": {"rail": "top", "end": "last", "out": "up"}, "ears_pt": EP2},
             {"name": "LOGO", "ret": "6029", "face_hex": "#00A859", "fill": [0, 0.66, 0.35], "no_rails": True, "lit": False}]
        run("spar8000", 1, "SPAR + logo, P6 on □ frame, 2 parts", 100, V, P1, G,
            {"size": "40x40x2", "depth": 40, "ral": "7021", "type": "square"},
            [CAB(232, 127), CAB(331, 127)],
            md("{PW} x {PH} (parts 4350 + 3650)", "P6 on rectangular frame", 80, "Opal 8 mm; logo foil 8500 614",
               "RAL 9016 / logo RAL 6029", "□ 40x40x2 + ears, RAL 7021", "12V at logo -> trafo box",
               [["Parts", "2: SPA (4350) | R + logo (3650)"]]),
            bom([("Face letters SPAR", *FACE_W, "{PER_SPA} + {PER_R} m"), ("Face logo circle", *FACE_LOGO, "{PER_LOGO} m / {A_LOGO} m²")],
                [("Return letters", "Alu 1 mm", "RAL 9016", "{PER_SPA} + {PER_R} m"), ("Return logo", "Alu 1 mm", "RAL 6029", "{PER_LOGO} m / {RET_LOGO} m²")],
                SQ40("7021")),
            client={"splits": [232], "split_cols": [tuple(G2)]},
            extra={"ears": {"hole_d": 8}, "joints": [{"x_pt": xj / (100 * 25.4 / 72), "label": "FRAME JOINT"}]})

    # ---------------- 2: 7-22 (8-21) 5264 - dvi atskiros reklamos, kiekviena savo laidu į 1 trafo box
    HOURS_BOM = lambda g: bom([(f"Face {n}", *FACE_W, f"{{PER_{n}}} m / {{A_{n}}} m²") for n in g],
                              [(f"Return {n}", "Alu 1 mm", "RAL 9005", f"{{PER_{n}}} m / {{RET_{n}}} m²") for n in g], U30("7021"))
    if not which or "h722big" in which:
        CF = {"rail": "top", "end": "first", "out": "up"}
        G = [{"name": "7-22", "ret": "9005", "face_hex": "#FFFFFF", "fill": WHITE, "frame": "horizontal", "cable": CF,
              "ears_pt": {"top": [152.3, 180.1], "bottom": [146.9, 180.1]}},
             {"name": "(8-21)", "ret": "9005", "face_hex": "#FFFFFF", "fill": G2, "frame": "horizontal", "cable": CF,
              "ears_pt": [214.6, 243.6, 276.8]}]
        run("h722big", 2, "7-22 (8-21), P6 on rails, 2 signs", 100, (128, 214, 296, 253), P1, G,
            {"size": "30x30x2", "depth": 30, "ral": "7021"}, [CAB(137, 241), CAB(282, 241)],
            md("{PW} x {PH}", "P6 on rails", 80, "Opal 8 mm", "RAL 9005", "U 30x30x2 + ears, RAL 7021",
               "2 cables 12V -> 1 trafo box"),
            HOURS_BOM(["7-22", "(8-21)"]), client={"splits": [200], "split_cols": [tuple(G2)]})

    # ---------------- 3: OLE P. FJÆR - mažiau ausėlių
    if not which or "ole" in which:
        run("ole", 3, "OLE P. FJÆR, P6 on rails", 100, (145, 266, 282, 292), P1,
            [{"name": "OLE", "ret": "9016", "face_hex": "#FFFFFF", "fill": WHITE, "frame": "horizontal",
              "cable": {"rail": "top", "end": "first", "out": "left"}}],
            {"size": "30x30x2", "depth": 30, "ral": "7021"}, [CAB(276, 287)],
            md("{PW} x {PH}", "P6 on rails", 80, "Opal 8 mm", "RAL 9016", "U 30x30x2 + ears, RAL 7021", "12V -> trafo box"),
            bom([("Face letters", *FACE_W, "{PER_OLE} m / {A_OLE} m²")], [("Return letters", "Alu 1 mm", "RAL 9016", "{PER_OLE} m / {RET_OLE} m²")],
                U30("7021")), extra={"ears": {"smax": 1450}})

    # ---------------- 4: SPAR 3500
    if not which or "spar3500" in which:
        V = (145, 316, 258, 343)
        ys, _, _ = rails_y_mm(P1, V, 100)
        bbs = letters_mm(P1, V, 100)
        let = sorted([b for b in bbs if b[3] - b[1] < 600], key=lambda b: b[0]); logo = max(bbs, key=lambda b: b[3] - b[1])
        t = 30
        top0 = min(b[1] for b in let); topA = min(b[1] for b in bbs)
        import math as _m
        cxl, cyl, rl = (logo[0] + logo[2]) / 2, (logo[1] + logo[3]) / 2, (logo[2] - logo[0]) / 2
        rr = []
        for y, outer in ((ys[0], -1), (ys[-1], 1)):
            ya = topA + y                                          # abs. mm bėgelio ašis
            # Rytis 2026-10-08 (5): pradžia pagal S kontūrą, galas - apskritimo styga (neišsikiša), 30 mm į vidų
            x0 = rail_start_in(P1, V, 100, let[0], [ya - t / 2, ya + t / 2]) - let[0][0]
            x1 = cxl + _m.sqrt(max(rl ** 2 - (ya + outer * t / 2 - cyl) ** 2, 0)) - 30 - let[0][0]
            yg = ya - top0
            rr.append({"kind": "h", "poly": [[x0, yg - t / 2], [x1, yg - t / 2], [x1, yg + t / 2], [x0, yg + t / 2]]})
        run("spar3500", 4, "SPAR letters + logo, P6 on rails", 100, V, P1,
            [{"name": "SPAR", "ret": "9016", "face_hex": "#FFFFFF", "fill": WHITE, "rails": rr, "frame": "horizontal",
              "cable": {"rail": "top", "end": "first", "out": "left"}, "ears_pt": [166.0, 204.8, 245.9]},
             {"name": "LOGO", "ret": "6029", "face_hex": "#00A859", "fill": [0, 0.66, 0.35], "no_rails": True, "lit": False}],
            {"size": "30x30x2", "depth": 30, "ral": "7021"}, [CAB(150, 322)],
            md("{PW} x {PH}", "P6 on rails", 80, "Opal 8 mm; logo foil 8500 614", "RAL 9016 / logo RAL 6029",
               "U 30x30x2 + ears, RAL 7021", "12V -> trafo box"),
            bom([("Face letters SPAR", *FACE_W, "{PER_SPAR} m / {A_SPAR} m²"), ("Face logo circle", *FACE_LOGO, "{PER_LOGO} m / {A_LOGO} m²")],
                [("Return letters", "Alu 1 mm", "RAL 9016", "{PER_SPAR} m / {RET_SPAR} m²"), ("Return logo", "Alu 1 mm", "RAL 6029", "{PER_LOGO} m / {RET_LOGO} m²")],
                U30("7021")), extra={"ears": {"smax": 1500}})

    # ---------------- 5: 7-22 (8-21) 3040 - viena reklama
    if not which or "h722small" in which:
        run("h722small", 5, "Opening hours 7-22 (8-21), P6 on rails", 100, (150, 343, 252, 368), P1,
            [{"name": "HOURS", "ret": "9005", "face_hex": "#FFFFFF", "fill": WHITE, "frame": "horizontal",
              "cable": {"rail": "top", "end": "first", "out": "left"}, "ears_pt": [169.3, 200.5, 240.7]}],
            {"size": "30x30x2", "depth": 30, "ral": "7021"}, [CAB(155, 348)],
            md("{PW} x {PH}", "P6 on rails", 80, "Opal 8 mm", "RAL 9005", "U 30x30x2 + ears, RAL 7021", "12V -> trafo box"),
            HOURS_BOM(["HOURS"]), extra={"ears": {"smax": 1500}})

    # ---------------- 15: PANT - apskritimas be rėmo, tvirtinamas per dugną tiesiai prie fasado; balta plexi + žalia pjaustyta plėvelė
    if not which or "pant" in which:
        # Rytis 2026-10-08: vientisa reklama - visi objektai (raidės + apskritimas) ant VIENO rėmo; apskritimas -
        # balta plexi + pjaustyta žalia plėvelė ORACAL 8500 614 (baltas kraštas ir piktograma - iškirpti)
        run("pant", 15, "EUROSPAR PANT, P6 on rails", 20, (385, 318, 720, 412), P2,
            [{"name": "PANT", "ret": "9005", "face_hex": "#FFFFFF", "fill": WHITE, "frame": "horizontal",
              "cable": {"rail": "top", "end": "first", "out": "left"}, "ears_pt": [480.3, 576.3, 659.6]}],
            {"size": "30x30x2", "depth": 30, "ral": "8001"}, [CAB(704, 393)],
            md("{PW} x {PH}", "P6 on rails", 80, "Opal 8; circle foil 8500 614", "RAL 9005",
               "U 30x30x2 + ears, RAL 8001", "12V -> trafo box"),
            bom([("Face letters + circle", *FACE_W, "{PER_PANT} m / {A_PANT} m²")],
                [("Return letters + circle", "Alu 1 mm", "RAL 9005", "{PER_PANT} m / {RET_PANT} m²")], U30("8001"),
                [["", "Foil on circle, cut (white edge + pictogram)", "Vinyl foil", "ORACAL 8500 614", "1 pcs."]]),
            client={"logo_foil": tuple(PICT)},
            extra={"ignore_fills": [PICT], "decals": [{"client_fill": PICT, "hex": "#00A859", "group": "PANT"}]})

    # ---------------- 16 / 17: vidaus kategorijos (pagal 225721 KAFFEBAR): U 20x20x2, tik viršutinis bėgelis į sieną
    R20 = lambda ral: {"size": "20x20x2", "depth": 20, "ral": ral}
    if not which or "smagodt" in which:
        run("smagodt", 16, "SMÅGODT, P6 on rails (indoor)", 10, (448, 305, 745, 415), P3,
            [{"name": "SMAGODT", "ret": "9003", "face_hex": "#FFFFFF", "fill": [0.9, 0.9, 0.9], "frame": "horizontal", "ears": False, "cable": {"rail": "bottom", "end": "last", "out": "right"}}],
            R20("4010"), [CAB(725, 404)],
            md("{PW} x {PH}", "P6 on rails, indoor", 50, "Opal 8 mm", "RAL 9003", "U 20x20x2, RAL 4010 matt",
               "cables at the bottom only", [["Mounting", "top rail direct to wall, no ears"]]),
            bom([("Face letters", *FACE_W, "{PER_SMAGODT} m / {A_SMAGODT} m²")],
                [("Return letters", "Alu 1 mm", "RAL 9003", "{PER_SMAGODT} m / {RET_SMAGODT} m²")], UTOP("4010")),
            depth=50, extra={"ears": {"smax": 2000},
                             "trafo_box": {"voltage": "12V", "mains": "220V", "cable_len_m": 3.0, "x": 450}})
    if not which or "kaffepause" in which:
        run("kaffepause", 17, "KAFFEPAUSE, P00+6 on rails (indoor)", 10, (446, 320, 712, 413), P4,
            [{"name": "KAFFE", "ret": "9003", "face_hex": "#FFFFFF", "fill": WHITE, "frame": "horizontal", "ears": False, "z0": 22, "cable": {"rail": "bottom", "end": "last", "out": "right"}},
             {"name": "CIRCLE", "ret": "9005", "face_hex": "#2B2B2B", "fill": list(COMP), "behind": True, "no_rails": True,
              "depth_mm": 2, "z0": 20, "lit": False}],
            R20("9005"), [CAB(707, 391)],
            md("{PW} x {PH}", "P00+6 on rails, indoor", 50, "Opal 8 mm; circle foil 551-035",
               "RAL 9003", "U 20x20x2, RAL 9005 matt", "cables at the bottom only",
               [["Mounting", "top rail direct to wall, no ears"]]),
            bom([("Face letters", *FACE_W, "{PER_KAFFE} m / {A_KAFFE} m²")],
                [("Return letters", "Alu 1 mm", "RAL 9003", "{PER_KAFFE} m / {RET_KAFFE} m²")], UTOP("9005"),
                [[9, "Circle + frame replication, 1 part", "Black alu composite 2 mm", "RAL 9005", "{A_CIRCLE} m²"],
                 [10, "Foil on circle (RAL 2008 tone)", "Vinyl foil", "ORACAL 551-035", "1 pcs."]]),
            client={"logo_replica": (COMP, ORG, 20 / (10 * 25.4 / 72))},
            depth=50, extra={"ears": {"smax": 2000}, "no_plates": True,
                             "callouts": {"front": [[450, 288, 10, -70, 34]], "rear": [[450, 150, 9, 90, -62]]},
                             "ignore_fills": [list(ORG)], "decals": [{"client_fill": list(ORG), "hex": "#F75E25", "group": "CIRCLE"}],
                              "trafo_box": {"voltage": "12V", "mains": "220V", "cable_len_m": 3.0, "x": 300}})
