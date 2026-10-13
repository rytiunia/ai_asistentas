#!/usr/bin/env python3
"""v167 (Rytis 2026-10-13: „visur turi būti naudojamas GOST šriftas") - originalo fragmentas su GOST tekstais.

Originalo (ankstesnio ALT lapo) fragmente tekstai dažnai Arial ir KREIVĖMIS. Įdedant fragmentą (`lapas_core.place_pdf`):
  1) `prep(src, pno, redacts, out)` - šaltinio kopija, iš kurios pašalinti (redakcija, tik pilnai uždengti vektoriai)
     nurodyti Arial užrašai (`redacts` - stačiakampiai šaltinio pt koord.); likusi grafika nepakinta;
  2) lapas išsaugomas kaip įprasta (fragmentas įdedamas `K.save()` metu);
  3) `overlay(pdf, page, clip, X0, Ytop, k, texts)` - tie patys užrašai ta pačia vieta GOST Common šriftu, VIRŠ fragmento.
     `texts` - [x0, y_baseline, tekstas, cap_aukštis, "#RRGGBB", align("l"|"r"|"c"), rot(0|90)] šaltinio koord.
     (dydis = cap / 0,715, mastelis k - kaip fragmento įdėjime).
Po overlay - `lapas_core.pdf_fix_fonts()` (šrifto vardas „GOST Common" Corel'iui).
"""
import os

import pymupdf as fitz

GOST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "gost_common.ttf")
CAP = 0.715


def prep(src, pno, redacts, out, pad=0.6):
    d = fitz.open(src)
    pg = d[pno]
    for r in redacts:
        pg.add_redact_annot(fitz.Rect(r[0] - pad, r[1] - pad, r[2] + pad, r[3] + pad), fill=False)
    pg.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_REMOVE_IF_COVERED,
                        text=fitz.PDF_REDACT_TEXT_REMOVE)
    d.save(out, garbage=3, deflate=True)
    return out


def _hex(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def overlay(pdf, page, clip, X0, Ytop, k, texts, out=None, min_size=8.0):
    """min_size - lapo taisyklė (>= 8 pt); pasukti užrašai siaurose detalėse (pvz. PSU 100W) - originalo dydžio"""
    d = fitz.open(pdf)
    pg = d[page]
    font = fitz.Font(fontfile=GOST)
    groups = {}                                          # viena TextWriter spalvai / pasukimui - vienas šrifto resursas
    for x, y, s, cap, col, al, rot in texts:
        size = cap / CAP * k
        if rot != 90:
            size = max(size, min_size)
        segs = s if isinstance(s, list) else [(s, col)]        # eilutė iš kelių spalvų dalių - be tarpų tarp jų
        w = sum(font.text_length(t_, size) for t_, _ in segs)
        px, py = X0 + (x - clip[0]) * k, Ytop + (y - clip[1]) * k
        if rot == 90:                                    # skaitoma iš apačios į viršų
            py += {"c": w / 2, "r": w}.get(al, 0)
        else:
            px -= {"c": w / 2, "r": w}.get(al, 0)
        for t_, c_ in segs:
            groups.setdefault((c_, rot), []).append((px, py, t_, size))
            px += font.text_length(t_, size) if rot != 90 else 0
    for (col, rot), items in groups.items():
        if rot == 90:
            for px, py, s, size in items:                # pasuktas - atskirai (morph aplink savo tašką)
                tw = fitz.TextWriter(pg.rect)
                tw.append((px, py), s, font=font, fontsize=size)
                tw.write_text(pg, color=_hex(col), morph=(fitz.Point(px, py), fitz.Matrix(90)))
            continue
        tw = fitz.TextWriter(pg.rect)
        for px, py, s, size in items:
            tw.append((px, py), s, font=font, fontsize=size)
        tw.write_text(pg, color=_hex(col))
    tmp = (out or pdf) + ".gost.pdf"
    d.save(tmp, garbage=3, deflate=True)
    d.close()
    os.replace(tmp, out or pdf)
