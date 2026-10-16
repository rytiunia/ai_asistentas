"""ALT8901: patvirtinto lapo BOM / MAIN DATA lentelės -> eilutės (pagal stulpelių antraščių x ir eilučių y) - duomenų perkėlimui
be iškraipymų (taisyklė: info iš originalo, stilius - dabartinis)."""
import sys
import pymupdf as fitz


def table(page, head_words, x0, x1, y0, y1):
    W = [w for w in page.get_text("words") if x0 <= w[0] < x1 and y0 <= w[1] < y1]
    hy = min(w[1] for w in W if w[4] == head_words[0])
    cols = []
    for h in head_words:
        c = min((w for w in W if w[4] == h and abs(w[1] - hy) < 3), key=lambda w: w[0])
        cols.append(c[0] - 2)
    rows = {}
    for w in W:
        if w[1] <= hy + 3:
            continue
        key = round((w[1] + w[3]) / 2 / 3)
        rows.setdefault(key, []).append(w)
    out = []
    for k in sorted(rows):
        cells = [""] * len(cols)
        for w in sorted(rows[k], key=lambda w: w[0]):
            ci = max(i for i, cx in enumerate(cols) if w[0] >= cx - 1) if w[0] >= cols[0] - 1 else 0
            cells[ci] = (cells[ci] + " " + w[4]).strip()
        out.append(cells)
    return out


def bands(page):
    bom = page.search_for("BILL OF MATERIALS")[0]; md = page.search_for("MAIN DATA")[0]; rv = page.search_for("REVISIONS")[0]
    b = table(page, ["POS", "PART", "MATERIAL", "FINISH", "QTY"], bom.x0 - 2, md.x0 - 1, bom.y0, page.rect.height - 20)
    m = table(page, ["MAIN"], md.x0 - 2, rv.x0 - 1, md.y0 - 1, page.rect.height - 20)
    return b, m


if __name__ == "__main__":
    d = fitz.open(sys.argv[1])
    for pn in [int(v) - 1 for v in sys.argv[2:]]:
        b, m = bands(d[pn])
        print("=== lapas", pn + 1); [print("  BOM", r) for r in b]; [print("  MD ", r) for r in m]
