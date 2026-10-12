#!/usr/bin/env python3
"""Plėvelių spalvų biblioteka (v142, Rytis 2026-10-12): ORACAL 8500 / 551, Avery 4500 TF / 5500 QM / 777, 3M 3630.

  python3 scripts/pleveles.py "ORACAL 551 702"     -> serija, kodas, pavadinimas, hex
  python3 scripts/pleveles.py 8500 red             -> paieška serijoje pagal pavadinimą
  python3 scripts/pleveles.py --series             -> serijos ir spalvų skaičius
Duomenys: assets/pleveles.json. Hex - ekrano artinys (Avery / 3M - "approx": true), ne spalvų atitikimui.
"""
import sys

import lapas_core as K

SER = {"8500": "ORACAL 8500", "551": "ORACAL 551", "4500": "AVERY 4500", "5500": "AVERY 5500",
       "777": "AVERY 777", "3630": "3M 3630"}


def main(a):
    F = K.films()
    if not a or a[0] == "--series":
        for s, d in F.items():
            if not s.startswith("_"):
                print(f"{s:12s} {len(d['colors']):4d}  {d.get('type', '')}")
        return
    r = K.film_lookup(" ".join(a))
    if r and (len(a) == 1 or a[1][:1].isdigit()):
        s, k, e = r
        print(f"{s} {k}  {e['name']}  {e['hex']}{'  (approx)' if e.get('approx') else ''}")
        return
    s = SER.get(a[0]); q = " ".join(a[1:]).lower()
    for k, e in (F.get(s, {}).get("colors", {}) if s else {}).items():
        if q in e["name"].lower() or q == k:
            print(f"{s} {k}  {e['name']}  {e['hex']}{'  (approx)' if e.get('approx') else ''}")


if __name__ == "__main__":
    main(sys.argv[1:])
