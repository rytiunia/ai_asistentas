"""v157 (Rytis 2026-10-13: „kliento tekstus visada padaryk vektorinius" + „pasikeitė spalvos ... kliento grafika VISADA turi
atitikti"): PDF tekstas -> kreivės TIESIAI turinio sraute. Keičiami TIK teksto rodymo operatoriai (Tj / TJ / ' / ") - jų vietoje
glifų kontūrai (m / l / c / h + f) iš įterpto šrifto; spalvos (cs / scn / k), ICC, overprint (OP / OPM), skaidrumas (gs, SMask),
gradientai ir paveikslėliai lieka BAITAS Į BAITĄ. Ghostscript NENAUDOTI (v156 klaida: išmetė OP / OPM, perrašė ICC -> spalvos).

Palaikoma: Type0 Identity-H (CIDFontType0 CFF / CIDFontType2 TrueType), paprasti TrueType / Type1C / OpenType šriftai.
Nepalaikomas šriftas (Type3, Type1 be CFF, vertikalus) - tas BT..ET blokas paliekamas nepakeistas ir pranešama.
Naudojimas: python3 pdf_outline.py in.pdf [out.pdf]   arba   pdf_outline.outline(in, out) -> (paversta, palikta)."""
import io
import sys

import pikepdf
from fontTools.agl import toUnicode
from fontTools.cffLib import CFFFontSet
from fontTools.pens.basePen import BasePen
from fontTools.ttLib import TTFont

Op = pikepdf.Operator
STD_ENC = None


class Unsupported(Exception):
    pass


def _mul(a, b):
    return [a[0] * b[0] + a[1] * b[2], a[0] * b[1] + a[1] * b[3], a[2] * b[0] + a[3] * b[2], a[2] * b[1] + a[3] * b[3],
            a[4] * b[0] + a[5] * b[2] + b[4], a[4] * b[1] + a[5] * b[3] + b[5]]


class _Pen(BasePen):
    def __init__(self, M, out):
        super().__init__(None)
        self.M, self.o = M, out

    def _t(self, p):
        M = self.M
        return [round(p[0] * M[0] + p[1] * M[2] + M[4], 4), round(p[0] * M[1] + p[1] * M[3] + M[5], 4)]

    def _moveTo(self, p):
        self.o.append((self._t(p), Op("m")))

    def _lineTo(self, p):
        self.o.append((self._t(p), Op("l")))

    def _curveToOne(self, a, b, c):
        self.o.append((self._t(a) + self._t(b) + self._t(c), Op("c")))

    def _closePath(self):
        self.o.append(([], Op("h")))


def _num(v):
    return float(v)


class Font:
    """kodai -> glifų kontūrai (glifo vienetais) + plotis (1/1000)"""

    def __init__(self, fo):
        self.fo = fo
        st = str(fo.get("/Subtype"))
        self.type0 = st == "/Type0"
        if st == "/Type3":
            raise Unsupported("Type3")
        if self.type0:
            if str(fo.get("/Encoding")) != "/Identity-H":
                raise Unsupported(f"Type0 encoding {fo.get('/Encoding')}")
            df = fo.DescendantFonts[0]
            self.dw = _num(df.get("/DW", 1000))
            self.w = {}
            W = list(df.get("/W", []))
            i = 0
            while i < len(W):
                c0 = int(W[i])
                if isinstance(W[i + 1], pikepdf.Array):
                    for k, v in enumerate(W[i + 1]):
                        self.w[c0 + k] = _num(v)
                    i += 2
                else:
                    for c in range(c0, int(W[i + 1]) + 1):
                        self.w[c] = _num(W[i + 2])
                    i += 3
            fd = df.FontDescriptor
            self.cid2gid = None
            m = df.get("/CIDToGIDMap")
            if isinstance(m, pikepdf.Stream):
                b = m.read_bytes()
                self.cid2gid = [b[k] << 8 | b[k + 1] for k in range(0, len(b) - 1, 2)]
        else:
            self.fc = int(fo.get("/FirstChar", 0))
            self.ws = [_num(v) for v in fo.get("/Widths", [])]
            fd = fo.get("/FontDescriptor")
            if fd is None:
                raise Unsupported("standard 14 font be įterpto failo")
            self.mw = _num(fd.get("/MissingWidth", 0))
        self.fd = fd
        self._load(fd)

    def _load(self, fd):
        self.cff = self.tt = None
        if "/FontFile3" in fd:
            s = fd.FontFile3
            data = s.read_bytes()
            if str(s.get("/Subtype")) == "/OpenType":
                self._tt(data)
            else:
                cs = CFFFontSet()
                cs.decompile(io.BytesIO(data), None)
                top = cs[cs.fontNames[0]]
                self.cff = top
                self.cs = top.CharStrings
                self.cid_keyed = hasattr(top, "ROS")
                self.order = top.charset
                fm = list(getattr(top, "FontMatrix", [0.001, 0, 0, 0.001, 0, 0]))
                self.fm = fm
        elif "/FontFile2" in fd:
            self._tt(fd.FontFile2.read_bytes())
        else:
            raise Unsupported("šriftas be FontFile2 / FontFile3 (Type1)")

    def _tt(self, data):
        self.tt = TTFont(io.BytesIO(data), lazy=True)
        self.gs = self.tt.getGlyphSet()
        self.order = self.tt.getGlyphOrder()
        u = self.tt["head"].unitsPerEm
        self.fm = [1 / u, 0, 0, 1 / u, 0, 0]
        if "CFF " in self.tt:
            top = self.tt["CFF "].cff[0]
            self.fm = list(getattr(top, "FontMatrix", self.fm))

    def codes(self, b):
        if self.type0:
            return [(b[k] << 8 | b[k + 1], 2) for k in range(0, len(b) - 1, 2)]
        return [(c, 1) for c in b]

    def width(self, code):
        if self.type0:
            return self.w.get(code, self.dw)
        k = code - self.fc
        return self.ws[k] if 0 <= k < len(self.ws) else self.mw

    def _simple_name(self, code):
        enc = self.fo.get("/Encoding")
        if isinstance(enc, pikepdf.Dictionary) and "/Differences" in enc:
            cur = None
            for v in enc.Differences:
                if isinstance(v, pikepdf.Name):
                    if cur == code:
                        return str(v)[1:]
                    cur += 1
                else:
                    cur = int(v)
        return None

    def glyph(self, code):
        """grąžina (glifo vardas / None, piešimo funkcija(pen))"""
        if self.cff is not None:
            if self.type0:
                name = f"cid{code:05d}" if self.cid_keyed else (self.order[code] if code < len(self.order) else None)
            else:
                name = self._simple_name(code)
                if name is None:
                    enc = getattr(self.cff, "Encoding", None)
                    if isinstance(enc, list) and code < len(enc):
                        name = enc[code]
            if name is None or name not in self.cs:
                return None
            return lambda pen: self.cs[name].draw(pen)
        # TrueType / OpenType
        if self.type0:
            gid = self.cid2gid[code] if self.cid2gid and code < len(self.cid2gid) else code
            name = self.order[gid] if gid < len(self.order) else None
        else:
            name = None
            cmap = self.tt["cmap"] if "cmap" in self.tt else None
            dn = self._simple_name(code)
            if dn and dn in self.gs:
                name = dn
            if name is None and cmap is not None:
                for pid, eid, cc in ((3, 0, 0xF000 + code), (3, 0, code), (1, 0, code)):
                    t = cmap.getcmap(pid, eid)
                    if t and cc in t.cmap:
                        name = t.cmap[cc]
                        break
                if name is None and dn:
                    u = toUnicode(dn)
                    t = cmap.getcmap(3, 1)
                    if t and u and ord(u[0]) in t.cmap:
                        name = t.cmap[ord(u[0])]
            if name is None and code < len(self.order):
                name = self.order[code]
        if name is None or name not in self.gs:
            return None
        return lambda pen: self.gs[name].draw(pen)


class TS:
    def __init__(self):
        self.font = None; self.fs = 1.0; self.Tc = 0.0; self.Tw = 0.0; self.Th = 1.0; self.TL = 0.0; self.Ts = 0.0; self.Tr = 0

    def copy(self):
        n = TS(); n.__dict__.update(self.__dict__); return n


def _process(ops, resources, fonts_cache, stats):
    """vienas turinio srautas -> naujas operatorių sąrašas"""
    fontres = resources.get("/Font", {}) if resources is not None else {}
    out = []
    ts = TS(); stack = []
    i = 0
    n = len(ops)
    while i < n:
        operands, op = ops[i]
        o = str(op)
        if o == "q":
            stack.append(ts.copy()); out.append(ops[i]); i += 1; continue
        if o == "Q":
            ts = stack.pop() if stack else TS(); out.append(ops[i]); i += 1; continue
        if o in ("Tc", "Tw", "Tz", "TL", "Ts", "Tr", "Tf"):
            _tstate(ts, o, operands, fontres, fonts_cache)
            i += 1; continue                              # už BT ribų - būsena sekama, operatorius nebereikalingas
        if o != "BT":
            out.append(ops[i]); i += 1; continue
        j = i + 1
        while j < n and str(ops[j][1]) != "ET":
            j += 1
        block = ops[i:j + 1]
        ts0 = ts.copy()
        try:
            new, ts = _block(block, ts, fontres, fonts_cache, stats)
            out.extend(new)
        except Unsupported as e:
            stats["kept"].append(str(e))
            ts = ts0
            for operands_, op_ in block:
                if str(op_) in ("Tc", "Tw", "Tz", "TL", "Ts", "Tr", "Tf"):
                    _tstate(ts, str(op_), operands_, fontres, fonts_cache, strict=False)
            out.extend(block)
        i = j + 1
    return out


def _font(name, fontres, cache, strict=True):
    fo = fontres.get(name) if fontres is not None else None
    if fo is None:
        if strict:
            raise Unsupported(f"nėra šrifto {name}")
        return None
    key = fo.objgen if fo.is_indirect else id(fo)
    if key not in cache:
        try:
            cache[key] = Font(fo)
        except Unsupported as e:
            cache[key] = e
    f = cache[key]
    if isinstance(f, Exception):
        if strict:
            raise f
        return None
    return f


def _tstate(ts, o, a, fontres, cache, strict=False):
    if o == "Tc": ts.Tc = float(a[0])
    elif o == "Tw": ts.Tw = float(a[0])
    elif o == "Tz": ts.Th = float(a[0]) / 100
    elif o == "TL": ts.TL = float(a[0])
    elif o == "Ts": ts.Ts = float(a[0])
    elif o == "Tr": ts.Tr = int(a[0])
    elif o == "Tf":
        ts.fontname = a[0]; ts.fs = float(a[1])
        ts.font = _font(a[0], fontres, cache, strict=False)


def _block(block, ts, fontres, cache, stats):
    out = []
    clip = []
    Tm = [1, 0, 0, 1, 0, 0]; Tlm = list(Tm)
    for operands, op in block:
        o = str(op)
        if o in ("BT", "ET"):
            continue
        if o in ("Tc", "Tw", "Tz", "TL", "Ts", "Tr", "Tf"):
            _tstate(ts, o, operands, fontres, cache)
            if o == "Tf" and ts.font is None:
                _font(operands[0], fontres, cache, strict=True)
            continue                                      # teksto nebėra -> Tf / Tc ... nereikalingi (šriftai išmetami)
        if o == "Td":
            Tlm = _mul([1, 0, 0, 1, float(operands[0]), float(operands[1])], Tlm); Tm = list(Tlm); continue
        if o == "TD":
            ts.TL = -float(operands[1]); Tlm = _mul([1, 0, 0, 1, float(operands[0]), float(operands[1])], Tlm); Tm = list(Tlm); continue
        if o == "Tm":
            Tlm = [float(v) for v in operands]; Tm = list(Tlm); continue
        if o == "T*":
            Tlm = _mul([1, 0, 0, 1, 0, -ts.TL], Tlm); Tm = list(Tlm); continue
        if o in ("Tj", "TJ", "'", '"'):
            if o in ("'", '"'):
                if o == '"':
                    ts.Tw, ts.Tc = float(operands[0]), float(operands[1])
                Tlm = _mul([1, 0, 0, 1, 0, -ts.TL], Tlm); Tm = list(Tlm)
            arr = operands[0] if o == "TJ" else [operands[-1]]
            if ts.font is None:
                raise Unsupported("tekstas be šrifto")
            Tm = _show(arr, ts, Tm, out, clip, stats)
            continue
        out.append((operands, op))                        # spalvos, gs, d, w, BDC/EMC ... - nekeičiama
    if ts.Tr >= 4 and clip:
        out.extend(clip)
        out.append(([], Op("W"))); out.append(([], Op("n")))
    return out, ts


def _show(arr, ts, Tm, out, clip, stats):
    f = ts.font
    for it in arr:
        if not isinstance(it, (pikepdf.String, bytes)):
            Tm = _mul([1, 0, 0, 1, -float(it) / 1000 * ts.fs * ts.Th, 0], Tm)
            continue
        b = bytes(it)
        for code, nb in f.codes(b):
            Trm = _mul([ts.fs * ts.Th, 0, 0, ts.fs, 0, ts.Ts], Tm)
            M = _mul(f.fm, Trm)
            g = f.glyph(code)
            if g is None:
                if code not in (0x20, 3):
                    stats["missing"] += 1
            else:
                path = []
                g(_Pen(M, path))
                if path:
                    mode = ts.Tr % 4
                    if ts.Tr != 3 and ts.Tr != 7:
                        out.extend(path)
                        out.append(([], Op({0: "f", 1: "S", 2: "B"}[mode])))
                    if ts.Tr >= 4:
                        clip.extend(path)
                    stats["glyphs"] += 1
            w0 = f.width(code) / 1000
            tx = (w0 * ts.fs + ts.Tc + (ts.Tw if (nb == 1 and code == 32) else 0)) * ts.Th
            Tm = _mul([1, 0, 0, 1, tx, 0], Tm)
    return Tm


def _walk(pdf, obj, resources, cache, stats, seen):
    if obj.objgen in seen:
        return
    seen.add(obj.objgen)
    res = obj.get("/Resources", resources)
    ops = pikepdf.parse_content_stream(obj)
    new = _process(ops, res, cache, stats)
    if new != ops:
        obj.write(pikepdf.unparse_content_stream(new))
    xo = res.get("/XObject", {}) if res is not None else {}
    for k in list(xo.keys()):
        x = xo[k]
        if str(x.get("/Subtype")) == "/Form":
            _walk(pdf, x, res, cache, stats, seen)


def outline(src, dst=None):
    """paverčia visą tekstą kreivėmis; grąžina stats {'glyphs', 'missing', 'kept'}"""
    pdf = pikepdf.open(src, allow_overwriting_input=True)
    stats = {"glyphs": 0, "missing": 0, "kept": []}
    cache = {}
    seen = set()
    for page in pdf.pages:
        res = page.obj.get("/Resources")
        ops = pikepdf.parse_content_stream(page)
        new = _process(ops, res, cache, stats)
        page.obj.Contents = pdf.make_stream(pikepdf.unparse_content_stream(new))
        xo = res.get("/XObject", {}) if res is not None else {}
        for k in list(xo.keys()):
            if str(xo[k].get("/Subtype")) == "/Form":
                _walk(pdf, xo[k], res, cache, stats, seen)
    if not stats["kept"] and not stats["missing"]:            # šriftai nebereikalingi -> išmesti iš resursų
        for page in pdf.pages:
            _drop_fonts(page.obj.get("/Resources"), set())
    pdf.save(dst or src)
    return stats


def _drop_fonts(res, seen):
    if res is None:
        return
    if "/Font" in res:
        del res["/Font"]
    for k, x in (res.get("/XObject", {}) or {}).items():
        if str(x.get("/Subtype")) == "/Form" and x.objgen not in seen:
            seen.add(x.objgen)
            _drop_fonts(x.get("/Resources"), seen)


if __name__ == "__main__":
    s = outline(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    print(s)
