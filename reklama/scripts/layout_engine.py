"""TAISYKLĖ 33 - ADAPTIVE CAD DRAWING LAYOUT (Rytis 2026-10-15, pilnas tekstas - references/adaptive_layout.md).

Išdėstymas prisitaiko prie gaminio geometrijos, ne atvirkščiai: masteliai, stulpelių pločiai ir tarpai
skaičiuojami KIEKVIENĄ kartą iš realių gabaritų + anotacijų zonų. Jokių fiksuotų koordinačių.

    import layout_engine as LE
    d   = LE.pick_scale((W_mm, H_mm), (avail_w_pt, avail_h_pt), annot=(l, r, t, b))   # ortogonalios - BENDRAS
    asp = LE.proj_aspect(corners_mm, yaw, pitch)                                          # 3D matomo kontūro w/h
    xs, g = LE.distribute(K.IX0, K.IX1, [w1, w2, ...])                                    # vienodi tarpai
    LE.report(...)                                                                        # užpildymo ataskaita
"""
import math
from reportlab.lib.units import mm as MM

ISO = (1, 2, 5, 10, 20, 50, 100, 200)        # ISO 5455 rekomenduojami (mažinimo vardikliai)
INTER = (15, 25)                              # tarpiniai - tik aiškiai nurodant mastelį (SCALE 1:15)


def pick_scale(size_mm, avail_pt, annot=(0, 0, 0, 0), iso=ISO, inter=INTER, cap_pt=None):
    """Didžiausias mastelis (mažiausias vardiklis), kuriam geometrija + anotacijos telpa zonoje.
    annot = (kairė, dešinė, viršus, apačia) pt - matmenų / pozicijų / pavadinimo juostos (nemastelinamos).
    cap_pt = (w, h) - vizualinė hierarchija: DETAIL negali būti didesnė už pagrindines projekcijas
    (nedidinti detalės vien dėl tuščios vietos - TAISYKLĖ 33 p.6); siūloma 0,6 x ortogonalių aukščio."""
    w, h = size_mm
    aw, ah = avail_pt
    for d in sorted(set(iso) | set(inter or ())):
        k = MM / d
        if cap_pt and (w * k > cap_pt[0] + 1e-6 or h * k > cap_pt[1] + 1e-6):
            continue
        if w * k + annot[0] + annot[1] <= aw + 1e-6 and h * k + annot[2] + annot[3] <= ah + 1e-6:
            return d
    raise ValueError(f"netelpa net 1:{max(iso)} - siūlyti papildomą lapą / didesnį formatą (TAISYKLĖ 33 p.9)")


def proj_aspect(pts3, yaw, pitch):
    """3D matomo kontūro (po projekcijos) plotis / aukštis - tas pats sukimas kaip lapas_core.View3D."""
    th, ph = math.radians(yaw), math.radians(pitch)
    ct, st, cp, sp = math.cos(th), math.sin(th), math.cos(ph), math.sin(ph)
    xs, ys = [], []
    for x, y, z in pts3:
        x1, z1 = x * ct + z * st, -x * st + z * ct
        xs.append(x1); ys.append(y * cp - z1 * sp)
    return (max(xs) - min(xs)) / (max(ys) - min(ys))


def box_corners(w, h, d):
    return [(x, y, z) for x in (0, w) for y in (0, h) for z in (0, d)]


def distribute(x0, x1, widths, margin=0.5):
    """Stulpeliai (pločiai su anotacijomis IR pavadinimais) per [x0, x1] VIENODAIS tarpais; kraštų paraštė = margin * tarpas
    (margin - skaičius arba (kairė, dešinė)). Grąžina (kairiųjų kraštų sąrašas, tarpas)."""
    ml, mr = margin if isinstance(margin, (tuple, list)) else (margin, margin)
    free = (x1 - x0) - sum(widths)
    if free < 0:
        raise ValueError(f"stulpeliai netelpa: trūksta {-free:.0f} pt - mažinti bendrą mastelį / pertvarkyti zonas")
    g = free / (len(widths) - 1 + ml + mr)
    xs, x = [], x0 + ml * g
    for w in widths:
        xs.append(x); x += w + g
    return xs, g


def title_w(title, scale):
    """vaizdo pavadinimo + mastelio eilutės plotis (stulpelio plotis >= jo, kad užrašas neišlįstų už paraštės)"""
    import lapas_core as K
    from reportlab.pdfbase.pdfmetrics import stringWidth
    return max(stringWidth(title, "FB", K.F_VIEW), stringWidth(scale, "F", K.F_SCALE))


def report(name, sc_ortho, gap, fills):
    """fills: {vaizdas: (užimta, zona)} - spausdina užpildymą (3D tikslas 85-100 % dominuojančio matmens)."""
    s = ", ".join(f"{k} {100 * a / b:.0f}%" for k, (a, b) in fills.items())
    print(f"LAYOUT {name}: ortho 1:{sc_ortho}, tarpas {gap:.0f} pt, {s}")
