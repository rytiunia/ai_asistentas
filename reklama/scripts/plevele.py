#!/usr/bin/env python3
"""plevele.py - pjaustomos plėvelės sunaudojimas ir ploterio failo išdėstymas (v121, Rytis 2026-10-12).

TAISYKLĖ (Rytis): plėvelė skaičiuojama pagal SUNAUDOJIMĄ (rulono darbinis plotis x sunaudotas ilgis), NE pagal pačios
grafikos plotą.
  - spalvota plėvelė - darbinis plotis 1190 mm (STANDARTAS): lipdukas (dalis) negali išeiti už 1190;
  - balta plėvelė arba spaudos plėvelė - 1320 mm;
  - 1500 mm - TIK išimtiniais atvejais ir TIK su pastaba (`allow_1500=True`).
Pjaustymo failas: originali forma skaidoma KUO MAŽIAU. Telpa visa (trumpesnė pusė <= darbinis plotis) - ploteriuojama
visa, neskaidant (sunaudojimas = ilgesnė pusė). Netelpa - skaidoma TIK bendrais objektais (automobilis / tekstas /
dušai ...): v124 - į VISUS bendrus objektus (ryškus tarpas >= 3 x mediana), sudėliojami kompaktiškai; objektas, kuris
pats netelpa, - per didžiausią tarpą; vienas objektas (pvz. raidė, kontūras)
niekada nekarpomas. v122: UŽRAŠAS VIENOJE LINIJOJE (visi jo žodžiai) - VIENAS objektas, neskaidomas į žodžius / raides
vien dėl plėvelės taupymo: gamybininkui klijuoti kelias dalis į vieną liniją, matuoti tarpus - brangiau ir rizikinga.
Skaidoma tik tada, kai NETELPA į rulono plotį, niekada - vien taupant plėvelę. Objektas / eilutė, kuri pati netelpa, -
perspėjimas (siūlė / kitas rulonas, sprendžia Rytis).

Funkcijos:
  roll_for(film, allow_1500)             -> (darbinis plotis mm, pastaba)
  plan(objs, film, gap_mm, ...)          -> {"roll", "pieces", "placements", "length_mm", "m2", "split", "notes", "text"}
                                            objs - shapely geometrijos (vienas elementas = vienas nekarpomas objektas), mm
  bom_text(p, qty)                       -> „1190 mm x 1.46 m = 1.74 m²" (+ x qty)
  objects_from_pdf(pdf, page, rect_pt, width_mm, fill)  -> objektai iš kliento PDF (kiekvienas piešinys - objektas)
  write_dxf(p, path), preview_pdf(p, path)  -> ploterio failas / peržiūra (rulono kraštai, dalys su numeriais)

CLI: python3 plevele.py client.pdf --rect x0,y0,x1,y1 --width-mm 1600 [--fill FFFFFF] [--film "ORACAL 551 white"]
                         [--allow-1500] [--separate] [--qty 6] [--dxf out.dxf] [--pdf out.pdf]
     --separate - atskiros raidės (P6 / tūrinių raidžių priekiai): kiekviena raidė - atskiras objektas, nesting
"""
import math
import re
import sys

from shapely.geometry import Polygon, MultiPolygon, box as sbox
from shapely.ops import unary_union
from shapely.affinity import rotate as srotate, translate as stranslate

ROLL_COLOR = 1190.0     # spalvota plėvelė - standartas
ROLL_WHITE = 1320.0     # balta / spaudos plėvelė
ROLL_MAX = 1500.0       # išimtis, tik su pastaba
GAP_MM = 10.0           # tarpas tarp dalių ploterio faile (prielaida - Rytis patvirtina)

_WHITE = re.compile(r"white|balt|wei(ß|ss)|\bwit\b|\bvit\b|ral\s*90(03|10|16)|\b010\b|spaud|print|digital|ecosol|uv\b|laminat", re.I)


def roll_for(film="", allow_1500=False, kind=None):
    """darbinis plotis pagal plėvelę: kind 'color' / 'white' / 'print' arba iš pavadinimo (white, balta, spauda ...)."""
    k = (kind or "").lower()
    white = k in ("white", "balta", "print", "spauda") or (not k and bool(_WHITE.search(str(film or ""))))
    w = ROLL_WHITE if white else ROLL_COLOR
    note = "balta / spaudos plėvelė - 1320 mm" if white else "spalvota plėvelė - 1190 mm (standartas)"
    if allow_1500:
        w = ROLL_MAX
        note = "! 1500 mm rulonas - IŠIMTIS (pastaba lape / užsakyme būtina)"
    return w, note


# ------------------------------------------------------------------ dalys (bendri objektai)
def _bb(g):
    x0, y0, x1, y1 = g.bounds
    return x1 - x0, y1 - y0


def _fits(g, W):
    w, h = _bb(g)
    return min(w, h) <= W + 1e-6


def _gap(a, b):
    return a.distance(b)


def _mst_edges(geoms):
    """Prim MST tarp objektų (atstumas = tarpas tarp objektų)."""
    n = len(geoms)
    if n < 2:
        return []
    inT = [False] * n
    best = [math.inf] * n
    par = [-1] * n
    best[0] = 0
    edges = []
    for _ in range(n):
        u = min((i for i in range(n) if not inT[i]), key=lambda i: best[i])
        inT[u] = True
        if par[u] >= 0:
            edges.append((best[u], par[u], u))
        for v in range(n):
            if not inT[v]:
                d = _gap(geoms[u], geoms[v])
                if d < best[v]:
                    best[v], par[v] = d, u
    return edges


def _components(n, edges):
    p = list(range(n))

    def f(x):
        while p[x] != x:
            p[x] = p[p[x]]
            x = p[x]
        return x
    for _, a, b in edges:
        p[f(a)] = f(b)
    comp = {}
    for i in range(n):
        comp.setdefault(f(i), []).append(i)
    return list(comp.values())


def logical_objects(objs, k=3.0, min_gap=20.0):
    """v124 (Rytis 2026-10-12, „šitas dėliojimo principas"): bendri objektai (užrašas, automobilis, kiekvienas dušas ...) -
    MST kraštinės su tarpu >= max(k x tarpų mediana, min_gap) kerpamos. Grąžina [[indeksai], ...]."""
    if len(objs) < 2:
        return [list(range(len(objs)))]
    edges = _mst_edges(objs)
    gs = sorted(e[0] for e in edges)
    thr = max(k * gs[len(gs) // 2], min_gap)
    return _components(len(objs), [e for e in edges if e[0] < thr])


def split_pieces(objs, W):
    """Mažiausiai skaidymų: visa grafika telpa -> 1 dalis. Ne - dalis, kuri netelpa, skeliama per DIDŽIAUSIĄ tarpą
    tarp jos objektų (MST kraštinė), kol visos dalys telpa arba lieka vienas objektas. Grąžina [[objektų indeksai], ...]."""
    objs = [g for g in objs]
    todo = [list(range(len(objs)))]
    done = []
    while todo:
        ids = todo.pop()
        g = unary_union([objs[i] for i in ids])
        if _fits(g, W) or len(ids) == 1:
            done.append(ids)
            continue
        sub = [objs[i] for i in ids]
        edges = sorted(_mst_edges(sub), key=lambda e: e[0])
        edges = edges[:-1]                         # nukerpama didžiausio tarpo kraštinė
        for c in _components(len(sub), edges):
            todo.append([ids[i] for i in c])
    # tvarka - kaip originale (kairė -> dešinė, viršus -> apačia)
    done.sort(key=lambda ids: (unary_union([objs[i] for i in ids]).bounds[0], unary_union([objs[i] for i in ids]).bounds[1]))
    return done


def text_lines(objs, h_ratio=0.6, gap_k=1.5, align_k=0.12):
    """v122 (Rytis 2026-10-12): UŽRAŠAS VIENOJE LINIJOJE - VIENAS NEKARPOMAS OBJEKTAS. Sujungiami objektai, kurie stovi
    vienoje eilutėje: panašaus aukščio (santykis >= h_ratio: didžioji / mažoji / su nuleidimu), bendra apačia (bazinė linija)
    ARBA bendras viršus (± align_k x aukštis; „p" jungiasi per „e"), tarpas <= gap_k x didesnis aukštis (tarpas tarp
    žodžių - taip pat). Diakritikai / taškai (ö, ä, å, i, ė - < 0,35 raidės aukščio, VIRŠ raidės jos x ribose,
    <= 0,35 h) - prie raidės. Piktograma (automobilis, dušas) - ne tokio aukščio / ne toje linijoje -> atskiras objektas.
    Grąžina [[objektų indeksai], ...]."""
    n = len(objs)
    bb = [g.bounds for g in objs]
    par = list(range(n))

    def f(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x
    for i in range(n):
        x0, y0, x1, y1 = bb[i]
        for j in range(i + 1, n):
            a0, b0, a1, b1 = bb[j]
            hi, hj = y1 - y0, b1 - b0
            lo, hm = min(hi, hj), max(hi, hj)
            if hm <= 0:
                continue
            ov = min(y1, b1) - max(y0, b0)
            gap = max(a0 - x1, x0 - a1, 0)
            aligned = abs(y0 - b0) <= align_k * hm or abs(y1 - b1) <= align_k * hm
            if lo / hm >= h_ratio and ov >= 0.6 * lo and aligned and gap <= gap_k * hm:
                par[f(i)] = f(j)
                continue
    cnt = {}
    for i in range(n):
        cnt[f(i)] = cnt.get(f(i), 0) + 1
    is_text = [cnt[f(i)] >= 3 for i in range(n)]          # eilutė pagal raides (iki įdėtų objektų jungimo)
    # objektas KITO VIDUJE (rato centras rato žiede, taškas raidės skylėje) - visada su juo (v123)
    from shapely.geometry import Polygon as _P
    filled = []
    for g in objs:
        parts = getattr(g, "geoms", [g])
        filled.append(unary_union([_P(q.exterior) for q in parts if hasattr(q, "exterior")]))
    for i in range(n):
        for j in range(n):
            if i != j and objs[j].area < objs[i].area and filled[i].contains(objs[j].representative_point()):
                par[f(j)] = f(i)
    # diakritikas (ö, ä, å, i taškai): mažas objektas VIRŠ raidės, jos x ribose - TIK prie teksto eilutės (>= 3 raidės),
    #  ne prie piktogramos (v123: dušo taškai virš automobilio - ne diakritikai)
    for i in range(n):
        for j in range(n):
            if i == j or not is_text[j] or is_text[i]:
                continue
            (s0, t0, s1, t1), (L0, M0, L1, M1) = bb[i], bb[j]
            hm, lo = M1 - M0, t1 - t0
            cx = (s0 + s1) / 2
            if hm > 0 and lo < 0.35 * hm and L0 <= cx <= L1 and t0 >= M1 - 0.05 * hm and t0 - M1 <= 0.35 * hm:
                par[f(i)] = f(j)
    out = {}
    for i in range(n):
        out.setdefault(f(i), []).append(i)
    return list(out.values())


# ------------------------------------------------------------------ išdėstymas ant rulono
def _pack(sizes, W, gap, policy):
    """sizes [(w, h)] -> stulpeliai išilgai rulono: kiekvienas stulpelis - dalys viena po kitos skersai rulono
    (suma skersai + tarpai <= W); stulpelio ilgis = ilgiausia dalis. policy: 'short' - ilgis išilgai mažiausias
    (didesnė pusė skersai, jei telpa), 'long' - ilgesnė pusė išilgai."""
    items = []
    for i, (w, h) in enumerate(sizes):
        a, b = max(w, h), min(w, h)
        if policy == "short" and a <= W + 1e-6:
            across, along, rot = a, b, (w >= h)      # ilgesnė pusė skersai (y)
        else:
            across, along, rot = b, a, (w < h)       # ilgesnė pusė išilgai (x)
        items.append((along, across, i, rot))
    items.sort(key=lambda t: (-t[0], -t[1]))
    cols = []
    for along, across, i, rot in items:
        for c in cols:
            if c["used"] + gap + across <= W + 1e-6 and along <= c["len"] + 1e-6:
                c["items"].append((i, rot, c["used"] + gap, across, along))
                c["used"] += gap + across
                break
        else:
            cols.append({"len": along, "used": across, "items": [(i, rot, 0.0, across, along)]})
    total = sum(c["len"] for c in cols) + gap * max(0, len(cols) - 1)
    return total, cols


def plan(objs, film="", gap_mm=GAP_MM, allow_1500=False, kind=None, roll_mm=None, keep_lines=True, separate=False):
    """Pagrindinė funkcija. objs - shapely geometrijos mm (originalo koordinatėmis), vienas = nekarpomas objektas.
    separate=True (v191, Rytis 2026-10-13: „kadangi raidės atskiros, plėvelė skaičiuojama nesting principu") - plėvelė
    klijuojama ant ATSKIRŲ raidžių (P6 / tūrinių raidžių priekiai): kiekviena raidė (ir kablelis / taškas) - atskiras
    objektas, sudėliojamas ant rulono kompaktiškai (nesting), užrašo eilutė NEsaugoma."""
    objs = [g for g in objs if g is not None and not g.is_empty]
    if separate:
        return _plan_separate(objs, film, gap_mm, allow_1500, kind, roll_mm)
    W, note = roll_for(film, allow_1500, kind)
    if roll_mm:
        W = float(roll_mm)
    notes = [note]
    if not objs:
        return {"roll": W, "pieces": [], "placements": [], "length_mm": 0, "m2": 0, "split": False, "notes": notes,
                "text": "plėvelės nėra"}
    lines = text_lines(objs) if keep_lines else [[i] for i in range(len(objs))]
    atoms = [unary_union([objs[i] for i in ids]) for ids in lines]          # užrašų eilutės - nekarpomi objektai
    whole = unary_union(atoms)
    if _fits(whole, W):
        parts = [list(range(len(atoms)))]                  # telpa visa - ploteriuojama visa, neskaidant
    else:
        # v124: netelpa -> skaidoma į VISUS bendrus objektus ir jie dėliojami kompaktiškai (Rytis patvirtino 1190 pavyzdį);
        #  objektas, kuris pats netelpa, - dar skeliamas per didžiausią tarpą (split_pieces)
        parts = []
        for ids in logical_objects(atoms):
            sub = split_pieces([atoms[i] for i in ids], W)
            parts += [[ids[i] for i in q] for q in sub]
    groups = [[i for a in ids for i in lines[a]] for ids in parts]
    pieces = [unary_union([objs[i] for i in ids]) for ids in groups]
    for k, p in enumerate(pieces):
        if not _fits(p, W):
            w, h = _bb(p)
            notes.append(f"! dalis {k + 1} ({w:.0f} x {h:.0f}) - vienas objektas / užrašo eilutė platesnis už {W:.0f} mm rulono darbinį plotį: "
                         f"siūlė objekte arba platesnis rulonas - Rytis sprendžia")
    sizes = [_bb(p) for p in pieces]
    best = min((_pack(sizes, W, gap_mm, pol) + (pol,) for pol in ("long", "short")), key=lambda t: t[0])
    length, cols, _ = best
    # vietos: x - išilgai rulono, y - skersai (0 .. W)
    placements = []
    x = 0.0
    for c in cols:
        for i, rot, y, across, along in c["items"]:
            g = pieces[i]
            if rot:
                g = srotate(g, 90, origin=(0, 0))
            x0, y0, _, _ = g.bounds
            placements.append({"piece": i, "rot": rot, "geom": stranslate(g, x - x0, y - y0)})
        x += c["len"] + gap_mm
    m2 = W * length / 1e6
    split = len(pieces) > 1
    area = sum(g.area for g in objs) / 1e6
    txt = (f"plėvelė: rulonas {W:.0f} mm, ilgis {length / 1000:.2f} m -> {m2:.2f} m² (grafikos plotas {area:.2f} m²); "
           + ("ploteriuojama VISA, neskaidant" if not split else
              f"skaidyta į {len(pieces)} dalis bendrais objektais: " + ", ".join(f"{w:.0f}x{h:.0f}" for w, h in sizes)))
    return {"roll": W, "pieces": pieces, "groups": groups, "placements": placements, "length_mm": length, "m2": m2,
            "area_m2": area, "split": split, "notes": notes, "text": txt}


def _plan_separate(objs, film, gap_mm, allow_1500, kind, roll_mm):
    W, note = roll_for(film, allow_1500, kind)
    if roll_mm:
        W = float(roll_mm)
    notes = [note]
    pieces = [g for g in objs]
    for k, p in enumerate(pieces):
        if not _fits(p, W):
            w, h = _bb(p)
            notes.append(f"! raidė {k + 1} ({w:.0f} x {h:.0f}) platesnė už {W:.0f} mm rulono darbinį plotį - Rytis sprendžia")
    sizes = [_bb(p) for p in pieces]
    best = min((_pack(sizes, W, gap_mm, pol) + (pol,) for pol in ("long", "short")), key=lambda t: t[0])
    length, cols, _ = best
    placements, x = [], 0.0
    for c in cols:
        for i, rot, y, across, along in c["items"]:
            g = pieces[i]
            if rot:
                g = srotate(g, 90, origin=(0, 0))
            x0, y0, _, _ = g.bounds
            placements.append({"piece": i, "rot": rot, "geom": stranslate(g, x - x0, y - y0)})
        x += c["len"] + gap_mm
    m2 = W * length / 1e6
    area = sum(g.area for g in objs) / 1e6
    txt = (f"plėvelė (atskiros raidės, nesting): rulonas {W:.0f} mm, {len(pieces)} objektai, ilgis {length / 1000:.2f} m -> "
           f"{m2:.2f} m² (grafikos plotas {area:.2f} m²)")
    return {"roll": W, "pieces": pieces, "groups": [[i] for i in range(len(pieces))], "placements": placements,
            "length_mm": length, "m2": m2, "area_m2": area, "split": True, "notes": notes, "text": txt}


def bom_text(p, qty=1):
    """BOM / MAIN DATA eilutė (angliškai): '1190 mm x 1.46 m = 1.74 m² (x 6 = 10.44 m²)'"""
    s = f"{p['roll']:.0f} mm x {p['length_mm'] / 1000:.2f} m = {p['m2']:.2f} m²"
    if qty and qty > 1:
        s += f" (x {qty} = {p['m2'] * qty:.2f} m²)"
    return s


# ------------------------------------------------------------------ kliento PDF -> objektai
def _flat_items(items, steps=12):
    """fitz drawing items -> subkeliai (taškų sąrašai)."""
    subs, cur, last = [], [], None
    for it in items:
        op = it[0]
        if op == "re":
            r = it[1]
            subs.append([(r.x0, r.y0), (r.x1, r.y0), (r.x1, r.y1), (r.x0, r.y1)])
            last = None
            continue
        if op == "qu":
            q = it[1]
            subs.append([(q.ul.x, q.ul.y), (q.ur.x, q.ur.y), (q.lr.x, q.lr.y), (q.ll.x, q.ll.y)])
            last = None
            continue
        p0 = (it[1].x, it[1].y)
        if last is None or abs(p0[0] - last[0]) > 1e-3 or abs(p0[1] - last[1]) > 1e-3:
            if len(cur) > 2:
                subs.append(cur)
            cur = [p0]
        if op == "l":
            cur.append((it[2].x, it[2].y))
            last = cur[-1]
        elif op == "c":
            a, b, c, d = it[1], it[2], it[3], it[4]
            for k in range(1, steps + 1):
                t = k / steps
                mt = 1 - t
                cur.append((mt ** 3 * a.x + 3 * mt * mt * t * b.x + 3 * mt * t * t * c.x + t ** 3 * d.x,
                            mt ** 3 * a.y + 3 * mt * mt * t * b.y + 3 * mt * t * t * c.y + t ** 3 * d.y))
            last = cur[-1]
    if len(cur) > 2:
        subs.append(cur)
    return subs


def objects_from_pdf(pdf, page=0, rect_pt=None, width_mm=None, fill=None, tol=0.02):
    """Kiekviena užpildyto piešinio sala (v123: compound path skaidomas į salas su skylėmis) - vienas objektas, mm (mastelis: rect plotis = width_mm).
    fill - 'FFFFFF' (tik ta spalva) arba None (visi užpildyti)."""
    import pymupdf as fitz
    pg = fitz.open(pdf)[page]
    r = fitz.Rect(rect_pt) if rect_pt else pg.rect
    k = (width_mm / r.width) if width_mm else 25.4 / 72
    want = None
    if fill:
        h = fill.lstrip("#")
        want = tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    out = []
    for d in pg.get_drawings():
        f_ = d.get("fill")
        if f_ is None or not r.contains(d["rect"]):
            continue
        if want and max(abs(a - b) for a, b in zip(f_, want)) > tol:
            continue
        rings = []
        for s in _flat_items(d["items"]):
            pts = [((x - r.x0) * k, (r.y1 - y) * k) for x, y in s]
            if len(pts) >= 3:
                pg_ = Polygon(pts).buffer(0)
                if not pg_.is_empty and pg_.area > 1e-6:
                    rings.append(pg_)
        out += islands(rings)
    return out


def islands(rings):
    """v123: sudėtinis kontūras (visa grafika vienas compound path) -> atskiri objektai (salos). Lyginis įdėjimo gylis -
    išorinis kontūras, nelyginis - skylė artimiausiame jį gaubiančiame kontūre (even-odd: o, a, ratų žiedai)."""
    n = len(rings)
    order = sorted(range(n), key=lambda i: -rings[i].area)
    depth, parent = {}, {}
    for a, i in enumerate(order):
        rp = rings[i].representative_point()
        cont = [j for j in order[:a] if rings[j].contains(rp)]
        depth[i] = len(cont)
        parent[i] = min(cont, key=lambda j: rings[j].area) if cont else None
    shells = {i: rings[i] for i in range(n) if depth[i] % 2 == 0}
    for i in range(n):
        if depth[i] % 2 == 1 and parent[i] in shells:
            shells[parent[i]] = shells[parent[i]].difference(rings[i])
    return [g for g in shells.values() if not g.is_empty]


# ------------------------------------------------------------------ išvestis
def _rings(g):
    for p in (g.geoms if isinstance(g, MultiPolygon) else [g]):
        if p.is_empty or not hasattr(p, "exterior"):
            continue
        yield list(p.exterior.coords)
        for i in p.interiors:
            yield list(i.coords)


def write_dxf(p, path):
    """ploterio failas: sluoksnis CUT (dalys), ROLL (rulono darbinio pločio ribos, ilgis)."""
    import ezdxf
    doc = ezdxf.new("R2010")
    msp = doc.modelspace()
    doc.layers.add("CUT", color=7)
    doc.layers.add("ROLL", color=1)
    for pl in p["placements"]:
        for ring in _rings(pl["geom"]):
            msp.add_lwpolyline([(x, y) for x, y in ring], close=True, dxfattribs={"layer": "CUT"})
    L, W = p["length_mm"], p["roll"]
    msp.add_lwpolyline([(0, 0), (L, 0), (L, W), (0, W)], close=True, dxfattribs={"layer": "ROLL"})
    doc.saveas(path)
    return path


def preview_pdf(p, path, title=""):
    """peržiūra: rulono juosta, dalys su numeriais, sunaudojimas."""
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import mm as MM
    L, W = max(p["length_mm"], 1), p["roll"]
    pw = 400 * MM
    sc = min((pw - 30 * MM) / L, 200 * MM / W)
    ph = W * sc + 45 * MM
    c = canvas.Canvas(path, pagesize=(pw, ph))
    ox, oy = 15 * MM, 25 * MM
    c.setStrokeColorRGB(0.8, 0, 0)
    c.setDash(4, 3)
    c.rect(ox, oy, L * sc, W * sc)
    c.setDash()
    c.setStrokeColorRGB(0, 0, 0)
    c.setFillColorRGB(0.85, 0.85, 0.85)
    for pl in p["placements"]:
        for ring in _rings(pl["geom"]):
            path_ = c.beginPath()
            path_.moveTo(ox + ring[0][0] * sc, oy + ring[0][1] * sc)
            for x, y in ring[1:]:
                path_.lineTo(ox + x * sc, oy + y * sc)
            path_.close()
            c.drawPath(path_, stroke=1, fill=0)
        x0, y0, x1, y1 = pl["geom"].bounds
        c.setFillColorRGB(0.8, 0, 0)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(ox + x0 * sc + 2, oy + y1 * sc - 10, str(pl["piece"] + 1))
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 9)
    asc = lambda s: s.encode("ascii", "replace").decode()
    c.drawString(ox, 12 * MM, asc(f"{title}  roll {W:.0f} mm x {L / 1000:.2f} m = {p['m2']:.2f} m2 | pieces {len(p['pieces'])}"
                                  + (" (whole, not split)" if not p["split"] else " (split by whole objects)")))
    c.drawString(ox, oy + W * sc + 5 * MM, asc(f"ROLL WORKING WIDTH {W:.0f} mm"))
    c.save()
    return path


# ------------------------------------------------------------------ CLI
if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)
    opt = {"--rect": None, "--width-mm": None, "--fill": None, "--film": "", "--qty": "1", "--dxf": None, "--pdf": None,
           "--page": "0", "--gap": str(GAP_MM), "--kind": None}
    flags = set()
    pdf = a[0]
    i = 1
    while i < len(a):
        if a[i] in ("--allow-1500", "--separate"):
            flags.add(a[i]); i += 1
        else:
            opt[a[i]] = a[i + 1]; i += 2
    rect = tuple(float(v) for v in opt["--rect"].split(",")) if opt["--rect"] else None
    objs = objects_from_pdf(pdf, int(opt["--page"]), rect, float(opt["--width-mm"]) if opt["--width-mm"] else None, opt["--fill"])
    p = plan(objs, opt["--film"], float(opt["--gap"]), "--allow-1500" in flags, opt["--kind"], separate="--separate" in flags)
    print(f"objektų: {len(objs)}")
    print(p["text"])
    for n in p["notes"]:
        print("  " + n)
    print("BOM:", bom_text(p, int(opt["--qty"])))
    if opt["--dxf"]:
        print("DXF:", write_dxf(p, opt["--dxf"]))
    if opt["--pdf"]:
        print("PDF:", preview_pdf(p, opt["--pdf"]))
