"""P6 priekio variantai (v90, Rytis 2026-10-11) - vienas parseris visiems skriptams.

Kodai (spec "front", su arba be "P6_"):
  3mm          balta plexi 3, PVC 3 mm bortelis, varžtas per šoną
  3mm+foil     balta plexi 3 + plėvelė
  3mm color    spalvota plexi 3
  8mm          balta plexi 8, frezuota su kanteliu (matomas kraštelis 3 mm, liežuvis korpuse)
  8mm+foil     balta plexi 8 + plėvelė
  8mm color    spalvota plexi 8, frezuota kaip balta
  10mm / 15mm / 20mm / 30mm [+foil]   balta plexi, frezuota su kanteliu kaip 8 mm (tik balta arba balta + plėvelė)
  P1           nešviečianti (Al priekis) - ne šio modulio
Konstrukcija: 3 mm -> "3mm" (PVC bortelis); >= 8 mm -> "8mm" (frezuota briauna)."""
import re

THK_ALLOWED = (3, 8, 10, 15, 20, 30)
COLOR_ALLOWED = (3, 8)


def parse(front):
    s = str(front or "3mm").strip()
    u = s.upper().replace("P6_", "").replace("P6 ", "").replace(" ", "")
    if u == "P1":
        return {"code": "P1", "thk": 2.0, "milled": False, "foil": False, "color": False, "kind": "P1", "warn": None}
    m = re.match(r"(\d+(?:[.,]\d+)?)", u)
    thk = float(m.group(1).replace(",", ".")) if m else 3.0
    foil = "FOIL" in u
    color = "COLOR" in u or "SPALV" in u
    warn = None
    if int(thk) not in THK_ALLOWED:
        warn = f"! priekis {thk:g} mm - ne standartinis (3/8/10/15/20/30), patikrinti"
    if color and int(thk) not in COLOR_ALLOWED:
        warn = f"! spalvota plexi {thk:g} mm - standartiškai tik 3 ir 8 mm, patikrinti"
    milled = thk >= 8
    code = f"P6_{thk:g}mm" + (" color" if color else ("+foil" if foil else ""))
    return {"code": code, "thk": thk, "milled": milled, "foil": foil, "color": color,
            "kind": "8mm" if milled else "3mm", "warn": warn}


def kind(front):
    """konstrukcijos tipas brėžiniams: '3mm' (PVC) / '8mm' (frezuota) / 'P1'"""
    return parse(front)["kind"]


def milled(front):
    return parse(front)["milled"]


def thk(front):
    return parse(front)["thk"]


def bom_face(front, face_txt="?"):
    """BOM priekio eilutė (EN)"""
    p = parse(front)
    if p["kind"] == "P1":
        return "Letter face Al"
    base = f"Acrylic {p['thk']:g} mm"
    if p["color"]:
        return f"{base} {face_txt}"
    return f"{base} white" + (f" + front foil {face_txt}" if p["foil"] else "")


if __name__ == "__main__":
    for t in ("3mm", "P6_3mm+foil", "3mm color", "8mm", "8mm+foil", "P6_8mm color", "10mm", "15mm+foil", "20mm", "30mm+foil", "5mm", "15mm color"):
        print(t, "->", parse(t), bom_face(t, "RAL 3020"))
