#!/usr/bin/env python3
"""v293 (Rytis 2026-10-16: „išsaugok taisykles ir naudojimo logiką ir padaryk, kad kitą kartą vėl nebūtų daroma su senomis
taisyklėmis ir nustatymais") - GENERATORIAUS LINT: randa SENŲ taisyklių / nustatymų šablonus generatoriaus kode (dažniausiai
projekto skriptas, nukopijuotas iš seno projekto). Paleidžiamas automatiškai iš patikra_lapas.py (generatorius - iš
`<lapas>.pdf.art.json` „gen"), arba ranka:  python3 scripts/taisykliu_lint.py projektai/<projektas>/<skriptas>.py

Kiekvienas radinys - klaida (lapas neatiduodamas). Galiojančios taisyklės - references/lapo_taisykles.md.
Išimtis eilutei (tik pagrįstai, su priežastimi): komentaras `# lint-ok: <priežastis>`.
"""
import os
import re
import sys

PROJ = os.sep + "projektai" + os.sep

# (id, regex, taikoma tik projektų skriptams, pranešimas)
RULES = [
    ("FIKSUOTA VIETA", re.compile(r"^\s*(X0|SX|RX|x3|ax0|bxL|LXL|DX|x_3d|X3D)\s*(,\s*\w+\s*)?=\s*[^#\n]*K\.I[XY][01]\s*[+-]\s*\d{2,}"), True,
     "vaizdo vieta fiksuota nuo rėmo - skaičiuoti LE.distribute / LE.pick_scale (TAISYKLĖ 33)"),
    ("FIKSUOTAS MASTELIS", re.compile(r"^\s*SC\s*=\s*\d+\s*(#.*)?$"), True,
     "ortogonalių vaizdų mastelis įrašytas ranka - LE.pick_scale (TAISYKLĖ 33)"),
    ("KIEKIS SU FORMULE", re.compile(r"f\"[^\"]*\d?×\s*\{[^}]*\}\s*=\s*\{"), False,
     "BOM kiekyje tik rezultatas ('0,93 m'), ne '2× 0.465 = 0.93 m' (v281 / TAISYKLĖ 34)"),
    ("BLOKAS BE CENTRAVIMO", re.compile(r"^\s*first_fn\(\s*X0\s*,"), False,
     "pjūvio blokas piešiamas tiesiai - K.centered / K.section_block (TAISYKLĖ 5 / 34)"),
    # v307 (Rytis 2026-10-16, KIA 33597: „faile tik lape esantys objektai")
    ("VISAS ŠALTINIO PUSLAPIS", re.compile(r"show_pdf_page\((?![^#\n]*clip_source)[^#\n]*clip\s*="), False,
     "show_pdf_page su clip įdeda VISĄ šaltinio puslapį (paslėptą) - K.place_pdf arba K.clip_source(src, pno, clip)"),
    ("BALTAS DANGTIS", re.compile(r"draw_rect\([^#\n]*fill\s*=\s*\(1,\s*1,\s*1\)[^#\n]*\)"), True,
     "senas turinys uždengiamas baltu (lieka faile) - ištrinti redakcija (add_redact_annot + apply_redactions)"),
]


def lint(path):
    errs = []
    if not path or not os.path.exists(path):
        return errs
    src = open(path, encoding="utf-8").read()
    proj = PROJ in os.path.abspath(path)
    for i, ln in enumerate(src.splitlines(), 1):
        if "lint-ok" in ln:
            continue
        for rid, rx, only_proj, msg in RULES:
            if only_proj and not proj:
                continue
            if rx.search(ln):
                errs.append(f"SENA TAISYKLĖ [{rid}] {os.path.basename(path)}:{i}: {msg}")
    if proj and "K.save(" in src and "layout_engine" not in src:
        errs.append(f"SENA TAISYKLĖ [BE LAYOUT_ENGINE] {os.path.basename(path)}: projekto lapas be adaptyvaus išdėstymo "
                    f"(import layout_engine as LE; LE.pick_scale / LE.distribute / LE.report) - TAISYKLĖ 33")
    return errs


if __name__ == "__main__":
    n = 0
    for p in sys.argv[1:]:
        for e in lint(p):
            print("   ", e); n += 1
    print("IŠ VISO:", n)
    sys.exit(1 if n else 0)
