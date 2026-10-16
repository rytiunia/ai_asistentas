#!/usr/bin/env python3
"""ŽINIŲ PAIEŠKA prieš kiekvieną užsakymą (v264, Rytis 2026-10-15: „padaryk, kad ieškotų geriausio sprendimo tarp jau
darytų rezultatų ir pasiektų optimalų rezultatą panaudojant teisingas žinias").

Ką daro:
  1. Iš raktažodžių nustato produkto ŠEIMĄ (šviesdėžė, raidės, P10, akrilinis rėmas, folded, pilonas ...) ir išvardija
     VISUS tos šeimos generatorius, aprašus (PRIVALOMA perskaityti) ir patvirtintus etalonus - taisyklė, priimta viename
     šeimos modulyje, galioja visiems (SKILL taisyklė 26).
  2. Randa SKILL.md taisykles ir references/*.md pastraipas pagal raktažodžius; rikiuoja pagal atitikimą ir NAUJUMĄ
     (didžiausia vNNN pastraipoje) - naujesnė taisyklė viršesnė už senesnę.
  3. Randa jau darytus projektus (scripts/projektai/*: spec, PDF) ir etalonus (assets/etalonai) - pradėti nuo geriausio
     (naujausio / patvirtinto) analogo, ne nuo nulio.
  4. Primena klaidų sąrašą (references/klaidos.md) - atitinkančias eilutes.

Naudojimas:  python3 scripts/ziniu_paieska.py <raktažodžiai...> [--n 25]
  pvz.  python3 scripts/ziniu_paieska.py dvipuse sviesdeze kojos nuo fasado
        python3 scripts/ziniu_paieska.py P10 raides be begio ilgasriegiai
"""
import glob
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# produkto šeimos: raktažodžiai -> generatoriai, aprašai, etalonai (taisyklės galioja visai šeimai)
FAMILIES = {
    "sviesdeze": {
        "keys": ["sviesdez", "lightbox", "light box", "dvipus", "vienpus", "flagsign", "flag sign", "projecting", "pendant",
                 "udhaeng", "udhæng", "nasekylt", "kabanti", "p10_lightbox", "push-through"],
        "gen": ["scripts/sviesdeze.py", "scripts/p10_lightbox_doublesided.py", "scripts/p10_lightbox_singlesided.py",
                "scripts/koju_uzdengimas.py"],
        "refs": ["references/moduliai_p10_lightbox_doublesided.md", "references/moduliai_p10_lightbox_singlesided.md",
                 "references/moduliai_pendant.md"],
        "skill_rules": "19-24, 26-28",
    },
    "raides": {
        "keys": ["raid", "letter", "p6", "p1", "p5", "5s", "begel", "rail", "rem", "ausel", "statmen", "logo"],
        "gen": ["scripts/braizyti_begeliai.py", "scripts/p6_dxf.py", "scripts/auto_remas.py", "scripts/auseles.py"],
        "refs": ["references/auseles.md", "references/moduliai_montavimas.md", "references/stilius.md"],
        "skill_rules": "P6 moduliai, 25, 27-28",
    },
    "p10_raides": {
        "keys": ["p10", "blokin", "30mm", "plexi blok", "ilgasrieg", "threaded rod", "akrilin", "acrylic"],
        "gen": ["scripts/braizyti_begeliai.py", "scripts/p10_raides.py", "scripts/griovelis_b.py", "scripts/griovelis_sim.py"],
        "refs": ["references/moduliai_p10_raides.md"],
        "skill_rules": "25, 27-28",
    },
    "folded": {
        "keys": ["folded", "lankstin", "padekl", "fonas", "plate"],
        "gen": ["scripts/braizyti_lapa.py", "scripts/folded_dxf.py"],
        "refs": ["references/moduliai_folded.md"],
        "skill_rules": "Folded plate",
    },
    "pilonas": {
        "keys": ["pilon", "pylon", "totem", "stela"],
        "gen": ["scripts/projektai/thales_d059422/thales_pylons.py"],
        "refs": ["references/moduliai_pilonai.md", "references/etalonas_pilonas_prisma_alt8826.md"],
        "skill_rules": "Pilonai",
    },
    "led": {
        "keys": ["led", "psu", "trafo", "maitinim", "laid", "cable"],
        "gen": ["scripts/led_km.py", "scripts/led_box.py", "scripts/led_sim.py"],
        "refs": ["references/led_lens.md", "references/led_sim.md", "references/led_gamybos_pavyzdziai.md"],
        "skill_rules": "28 (LED / PSU be modelių), LED - NUMATYTA",
    },
    "plevele": {
        "keys": ["pleve", "film", "oracal", "avery", "3m ", "decal", "lipduk", "folie"],
        "gen": ["scripts/plevele.py", "scripts/pleveles.py"],
        "refs": ["references/medziagos.md"],
        "skill_rules": "Plėvelių biblioteka, 28",
    },
}
SYN = {"sviesdeze": ["lightbox"], "lightbox": ["sviesdeze"], "kojos": ["legs", "leg"], "legs": ["kojos"],
       "raides": ["letters"], "letters": ["raides"], "padas": ["plate", "flange"], "plokste": ["plate"],
       "stiklas": ["glass", "face"], "varztai": ["screws", "screw"], "trafas": ["psu", "trafo"], "psu": ["trafo"],
       "laidas": ["cable"], "spalva": ["ral", "ncs", "color", "finish"], "dazymas": ["painted", "finish"],
       "ilgasriegiai": ["threaded", "rod"], "begelis": ["rail"], "remas": ["frame"]}


def norm(t):
    t = unicodedata.normalize("NFKD", str(t).lower())
    return "".join(ch for ch in t if not unicodedata.combining(ch))


def chunks_md(path):
    """pastraipos / numeruotos taisyklės / sąrašo punktai su eilutės numeriu"""
    out, cur, start = [], [], 1
    try:
        lines = open(path, encoding="utf-8").read().split("\n")
    except OSError:
        return out
    for i, ln in enumerate(lines, 1):
        new = (not ln.strip()) or re.match(r"^(#{1,4} |\d{1,2}[a-z]?\. |- \*\*|\* \*\*)", ln)
        if new and cur:
            out.append((start, "\n".join(cur)))
            cur = []
        if ln.strip():
            if not cur:
                start = i
            cur.append(ln)
    if cur:
        out.append((start, "\n".join(cur)))
    return out


def vmax(txt):
    v = [int(x) for x in re.findall(r"\bv(\d{2,3})\b", txt)]
    return max(v) if v else 0


def score(txt, terms):
    n = norm(txt)
    hit = sum(1 for t in terms if t in n)
    return hit


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__); return
    # v293: pirmiausia - galiojančių lapo taisyklių suvestinė (kad nebūtų daroma senomis taisyklėmis / nustatymais)
    _dg = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "references", "lapo_taisykles.md")
    if os.path.exists(_dg):
        _st = re.search(r"Atnaujinta: (v\d+)", open(_dg, encoding="utf-8").read())
        print("!" * 100)
        print(f"!! PRIVALOMA: references/lapo_taisykles.md ({_st.group(1) if _st else '?'}) - galiojančios lapo taisyklės + darbo eiga;")
        print("!! braižyti tik per lapas_core / layout_engine; seno projekto skriptas - tik duomenų analogas; patikra = 0.")
        print("!" * 100)
    N = 25
    if "--n" in argv:
        i = argv.index("--n"); N = int(argv[i + 1]); argv = argv[:i] + argv[i + 2:]
    raw = [norm(a) for a in argv]
    terms = set()
    for a in raw:
        terms.add(a[:max(4, len(a) - 2)] if len(a) > 5 else a)          # šaknis (galūnės)
        for s_ in SYN.get(a, []):
            terms.add(s_)
    q = " ".join(raw)

    # 0. katalogas (v266): tikslūs raktažodžiai -> paruoštas generatorius / šablonas / etalonas; seni pavadinimai
    kat = os.path.join(ROOT, "references", "produktu_katalogas.md")
    if os.path.exists(kat):
        sec, rows = "", []
        for ln in open(kat, encoding="utf-8").read().split("\n"):
            if ln.startswith("## "):
                sec = ln[3:4]
            elif ln.startswith("| ") and not ln.startswith("|---") and sec in ("A", "B", "C"):
                c0 = ln.split("|")[1]
                if score(c0, terms) and not c0.strip().startswith(("Raktažodis", "Senas")):
                    rows.append((sec, ln))
        if rows:
            print("=" * 100)
            print("## 0. KATALOGAS (references/produktu_katalogas.md):  A - paruošta, B - klausti prieš braižant, C - SENAS pavadinimas")
            for sec, ln in rows:
                print(f"  [{sec}] " + " | ".join(x.strip() for x in ln.split("|")[1:-1])[:330])
    fams = [k for k, f in FAMILIES.items() if any(norm(kw) in q for kw in f["keys"])]
    print("=" * 100)
    print("ŽINIŲ PAIEŠKA:", " ".join(argv), "| terminai:", ", ".join(sorted(terms)))
    print("=" * 100)
    if fams:
        print("\n## 1. PRODUKTO ŠEIMA(-OS) - PRIVALOMA PERSKAITYTI VISKĄ (taisyklė iš vieno modulio galioja visai šeimai):")
        for k in fams:
            f = FAMILIES[k]
            print(f"  [{k}] SKILL taisyklės: {f['skill_rules']}")
            for g in f["gen"]:
                p = os.path.join(ROOT, g)
                ver = vmax(open(p, encoding="utf-8").read()) if os.path.exists(p) else 0
                print(f"     generatorius: {g}  (naujausia žyma v{ver})" if os.path.exists(p) else f"     generatorius: {g} (NĖRA)")
            for r in f["refs"]:
                print(f"     aprašas:      {r}")
        print("  ! Jei šeimoje keli generatoriai - prieš braižant patikrinti, ar pasirinktame įgyvendintos NAUJAUSIOS šeimos\n"
              "    taisyklės (išdėstymas, kojos, varžtai, dažymas, LED); jei ne - pirmiausia pataisyti generatorių.")
    else:
        print("\n## 1. Produkto šeima neatpažinta - žr. SKILL „Produktų moduliai“; klausti Ryčio prieš kuriant naują.")

    # 2. taisyklės
    srcs = [os.path.join(ROOT, "SKILL.md")] + sorted(glob.glob(os.path.join(ROOT, "references", "*.md"))) + \
        sorted(glob.glob(os.path.join(ROOT, "references", "klientai", "*.md")))
    found = []
    for p in srcs:
        for ln, txt in chunks_md(p):
            s_ = score(txt, terms)
            if s_ >= max(1, min(2, len(terms) - 1)):
                found.append((s_, vmax(txt), os.path.relpath(p, ROOT), ln, txt))
    found.sort(key=lambda t: (-t[0], -t[1]))
    print(f"\n## 2. TAISYKLĖS / ŽINIOS (atitikimas, tada naujumas; rodoma {min(N, len(found))} iš {len(found)}):")
    for s_, v, p, ln, txt in found[:N]:
        first = " ".join(txt.split())[:260]
        print(f"  [{s_}] v{v:<3} {p}:{ln}  {first}")

    # 3. projektai ir etalonai
    print("\n## 3. JAU DARYTI PROJEKTAI (pradėti nuo geriausio analogo):")
    proj = []
    for d in sorted(glob.glob(os.path.join(HERE, "projektai", "*"))):
        if not os.path.isdir(d):
            continue
        txt = os.path.basename(d)
        for sp in glob.glob(os.path.join(d, "*.json")):
            try:
                txt += " " + json.dumps(json.load(open(sp, encoding="utf-8")), ensure_ascii=False)
            except Exception:
                pass
        s_ = score(txt, terms)
        if s_:
            pdfs = sorted(glob.glob(os.path.join(d, "*.pdf")), key=os.path.getmtime, reverse=True)
            mt = max([os.path.getmtime(x) for x in pdfs] or [0])
            proj.append((s_, mt, os.path.relpath(d, ROOT), [os.path.basename(x) for x in pdfs[:4]]))
    proj.sort(key=lambda t: (-t[0], -t[1]))
    for s_, mt, d, pdfs in proj[:12]:
        print(f"  [{s_}] {d}  ->  {', '.join(pdfs)}")
    et = [e for e in sorted(glob.glob(os.path.join(ROOT, "assets", "etalonai", "*"))) if score(os.path.basename(e), terms)]
    if et:
        print("  ETALONAI (patvirtinti):")
        for e in et:
            print("     ", os.path.relpath(e, ROOT))

    # 4. klaidos
    kl = os.path.join(ROOT, "references", "klaidos.md")
    if os.path.exists(kl):
        hits = [(ln, t) for ln, t in chunks_md(kl) if score(t, terms)]
        if hits:
            print("\n## 4. ŽINOMOS KLAIDOS (nekartoti):")
            for ln, t in hits[:10]:
                print(f"  references/klaidos.md:{ln}  {' '.join(t.split())[:220]}")
    print("\nToliau: perskaityti 1 dalies aprašus + 2 dalies taisykles, imti naujausią / patvirtintą 3 dalies analogą kaip pagrindą,\n"
          "sugeneruoti, `patikra_lapas.py` = 0, palyginti akimis su etalonu; konfliktuojant taisyklėms - galioja NAUJESNĖ (vNNN).")


if __name__ == "__main__":
    main(sys.argv[1:])
