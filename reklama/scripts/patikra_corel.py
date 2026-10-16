"""v310 (Rytis 2026-10-16, SPAR 225960 ALT8901: „bandant atidaryti su CorelDRAW: file corrupted"): PDF atidarymo CorelDRAW patikra.
Priežastis: į patvirtintą Corel PDF pymupdf insert_text įterpė ANTRĄ GOST Type0 šriftą (be ToUnicode / kitais glifų ID) ir
pymupdf perrašė failą -> Corel „file corrupted". Taisyklės (taip pat v171):
  1. viename lape - VIENAS GOST šrifto objektas (tekstą keičiant esamame PDF - originalo šriftu / glifais, ne naujas šriftas);
  2. šrifto vardas „GOST Common" (ne „GOST-Common" - pdf_fix_fonts);
  3. qpdf --check be klaidų; galutinis failas rašomas qpdf (--object-streams=disable).
python3 patikra_corel.py failas.pdf [...] -> 0 klaidų arba sąrašas; exit 1 jei klaidų yra."""
import subprocess
import sys

import pymupdf as fitz


def check(fn):
    err = []
    d = fitz.open(fn)
    for i, p in enumerate(d):
        g = [f for f in p.get_fonts() if "GOST" in f[3].upper()]
        if len({f[0] for f in g}) > 1:
            err.append(f"lapas {i + 1}: {len(g)} GOST šriftai ({', '.join(sorted({f[3] for f in g}))}) - turi būti vienas")
        if any("GOST-Common" in f[3] for f in g):
            err.append(f"lapas {i + 1}: šriftas 'GOST-Common' (pdf_fix_fonts -> 'GOST Common')")
    r = subprocess.run(["qpdf", "--check", fn], capture_output=True, text=True)
    if r.returncode != 0:                                   # 0 - be klaidų; 2 - klaidos; 3 - įspėjimai
        err.append("qpdf --check: " + (r.stdout + r.stderr).strip().splitlines()[-1])
    return err


if __name__ == "__main__":
    bad = 0
    for f in sys.argv[1:]:
        e = check(f); bad += len(e)
        print(f"{f}: " + ("0 klaid." if not e else "; ".join(e[:6]) + (f" ... (+{len(e) - 6})" if len(e) > 6 else "")))
    print("IŠ VISO:", bad); sys.exit(1 if bad else 0)
