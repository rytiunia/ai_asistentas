"""ALT8901 (SPAR 225960) v310: patvirtinto Corel PDF ORDER NO. keitimas BE naujo šrifto ir be pymupdf perrašymo.
v308 klaida (Rytis 2026-10-16: „CorelDRAW: file corrupted"): pymupdf insert_text įterpė antrą GOST Type0 šriftą + perrašė
failo struktūrą. DABAR: originalo GOSTCommon (Type0 Identity-H) glifų ID iš jo ToUnicode; turinio sraute pakeičiama TIK
užrašo glifų seka (tas pats ilgis - 16 simbolių); failas: qpdf --qdf -> baitų keitimas -> fix-qdf -> qpdf (be object streams).
python3 order_no.py in.pdf out.pdf ALT8901_10.16_RS"""
import os, re, subprocess, sys, tempfile
import pymupdf as fitz
src, dst, new = sys.argv[1:4]
OLD = "ALT0000_00.00_RS"
assert len(new) == len(OLD), "naujas ORDER NO. turi būti to paties ilgio"
d = fitz.open(src)
maps = {}                                              # font xref -> {char: gid hex}
for p in d:
    for fx, ext, typ, name, *_ in p.get_fonts():
        if fx in maps or typ != "Type0":
            continue
        tu = d.xref_get_key(fx, "ToUnicode")
        if tu[0] != "xref":
            continue
        cm = d.xref_stream(int(tu[1].split()[0])).decode("latin1"); m = {}
        for a, b in re.findall(r"<([0-9A-Fa-f]{4})>\s*<([0-9A-Fa-f]{4})>", cm):
            m.setdefault(chr(int(b, 16)), a.lower())
        for a, b, c in re.findall(r"<([0-9A-Fa-f]{4})>\s*<([0-9A-Fa-f]{4})>\s*<([0-9A-Fa-f]{4})>", cm):
            for k in range(int(a, 16), int(b, 16) + 1):
                m.setdefault(chr(int(c, 16) + k - int(a, 16)), "%04x" % k)
        maps[fx] = m
pairs = []
for fx, m in maps.items():
    if all(ch in m for ch in OLD + new):
        pairs.append(("".join(m[ch] for ch in OLD).encode(), "".join(m[ch] for ch in new).encode()))
assert pairs, "šrifte nėra visų simbolių"
tmp = tempfile.mkdtemp()
q1, q2 = os.path.join(tmp, "a.qdf"), os.path.join(tmp, "b.qdf")
subprocess.run(["qpdf", "--qdf", "--object-streams=disable", src, q1], check=True)
b = open(q1, "rb").read(); n = 0
for o, w in pairs:
    for v in (o, o.upper()):
        n += b.count(v); b = b.replace(v, w)
open(q1, "wb").write(b)
subprocess.run(["fix-qdf", q1], stdout=open(q2, "wb"), check=True)
subprocess.run(["qpdf", "--object-streams=disable", "--compress-streams=y", q2, dst], check=True)
out = fitz.open(dst)
fn_in = sorted({x[3] for p in d for x in p.get_fonts()}); fn_out = sorted({x[3] for p in out for x in p.get_fonts()})
ok = sum(new in p.get_text() for p in out)
print(f"OK {dst}: pakeista {n}, lapų su {new}: {ok}/{len(out)}, šriftai {'tie patys' if fn_in == fn_out else f'SKIRIASI {fn_in} -> {fn_out}'}")
