#!/usr/bin/env python3
"""v293: skill versijos pakėlimas - SKILL.md „Versija" ir references/lapo_taisykles.md „Atnaujinta" KARTU
(patikra_lapas.py 15 SUVESTINĖ PASENUSI - jei suvestinė atsilieka).

    python3 scripts/versija.py "Rytis 2026-10-16: <kas pakeista / nauja taisyklė>"

Prieš paleidžiant: naujas taisykles įrašyti į references/lapo_taisykles.md (B-E dalys) - šis skriptas tik pakelia numerius.
Po to: git add -A && git commit -m "reklama vNNN: ..." && git push.
"""
import datetime
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SK, DG = os.path.join(ROOT, "SKILL.md"), os.path.join(ROOT, "references", "lapo_taisykles.md")


def main(msg):
    s = open(SK, encoding="utf-8").read()
    m = re.search(r"\*\*Versija: (\S+) v(\d+)\*\* \(", s)
    v = int(m.group(2)) + 1
    d = datetime.date.today().isoformat()
    s = s[:m.start()] + f"**Versija: {d} v{v}** (v{v}, {msg}. " + s[m.end():]
    open(SK, "w", encoding="utf-8").write(s)
    g = open(DG, encoding="utf-8").read()
    g = re.sub(r"Atnaujinta: v\d+ \([^)]*\)", f"Atnaujinta: v{v} ({d})", g, count=1)
    open(DG, "w", encoding="utf-8").write(g)
    print(f"v{v}")


if __name__ == "__main__":
    main(" ".join(sys.argv[1:]) or "pakeitimas")
