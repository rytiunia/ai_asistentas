"""P6 priekio variantai (v90, Rytis 2026-10-11) - vienas parseris visiems skriptams.

v210 (Rytis 2026-10-14): profilis P6_3mm PERVADINTAS į „5S" - visur rašoma 5S (5S, 5S+foil, 5S color); senas kodas
P6_3mm / 3mm priimamas kaip sinonimas. 5S: priekis 3 mm POLIKARBONATAS, antipireninis (fire retardant); PVC 3 mm tvirtinimo
bortelis (~15 mm, įleistas 1 mm į priekį), šonas Alu 1 mm - 2 mm nuo priekio krašto, tarpas iki bortelio 1 mm, varžtas 2.9 mm
per šone išgręžtą Ø3 skylę į bortelį (etalonas assets/konstrukcijos/5S_profilis.pdf).

Kodai (spec "front", su arba be "P6_"):
  5S           (buv. P6_3mm) polikarbonatas 3 FR, PVC 3 mm bortelis, varžtas 2.9 per šoną
  5S+foil      polikarbonatas 3 FR + plėvelė
  5S color     spalvotas 3 mm priekis
  v233 (Rytis 2026-10-14): P6_8mm -> „P6", P6_8mm+foil -> „P6+foil", P6_8mm color -> „P6 color" (senas kodas - sinonimas).
  PROFILIS P6 VIENAS - tvirtinimai įvairūs (ant bėgelių U / □, akrilinio rėmo, folded, tiesiai į fasadą).
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
    s = str(front or "5S").strip()
    u = s.upper().replace(" ", "")
    if u.startswith("P6_"):
        u = u[3:]
    if u.startswith("5S"):                          # v210: 5S = buv. P6_3mm
        u = "3MM" + u[2:]
    if u.startswith("P6") and not re.match(r"P6\d", u):   # v233: „P6" / „P6+foil" / „P6 color" = buv. P6_8mm
        u = "8MM" + u[2:]
    if u.startswith("P10"):                         # v242: P10 - 30 mm balta plexi BLOKAS (ne P6 su šonais), LED griovelyje
        return {"code": "P10" + ("+foil" if "FOIL" in u else ""), "thk": 30.0, "milled": False, "foil": "FOIL" in u,
                "color": False, "kind": "P10", "warn": None}
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
    code = ("5S" if thk == 3 else ("P6" if thk == 8 else f"P6_{thk:g}mm")) + (" color" if color else ("+foil" if foil else ""))
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
    base = "Polycarbonate 3 mm FR" if p["thk"] == 3 else f"Acrylic {p['thk']:g} mm"   # v210: 5S - polikarbonatas FR
    if p["color"]:
        return f"{base} {face_txt}"
    return f"{base} white" + (f" + front foil {face_txt}" if p["foil"] else "")


if __name__ == "__main__":
    for t in ("P6", "P6+foil", "P6 color", "5S", "5S+foil", "5S color", "3mm", "P6_3mm+foil", "3mm color", "8mm", "8mm+foil", "P6_8mm color", "10mm", "15mm+foil", "20mm", "30mm+foil", "5mm", "15mm color"):
        print(t, "->", parse(t), bom_face(t, "RAL 3020"))
