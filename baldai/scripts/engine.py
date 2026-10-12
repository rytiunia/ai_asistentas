"""
Parametrinis virtuves korpusu variklis - standartine korpusu biblioteka.

    python scripts/engine.py <projektas.json> [--std assets/standartas.json] [--dekorai assets/dekorai.json] --out <dir>

Vienas duomenu modelis (model.json) -> export_xlsx.py (pjovimo lapas) ir build_page.py (3D, projekcija, lenteles).

Koordinates: x isilgai sienos nuo kairio kampo, y aukstyn nuo grindu, z nuo sienos i patalpa. mm.
L (ilgis) visada isilgai rasto, kai rastas yra; W - skersai. Kantai [L1, L2, W1, W2] - ABS storis mm, 0 = be kanto.

Korpusu tipai (projekto "tipas"), eile = kuria eile uzima (apatine / virsutine / abi):
"""
import argparse
import copy
import json
from collections import OrderedDict
from pathlib import Path

TIPAI = OrderedDict([
    ("apatinis_durys",     ("apatinis",   "Apatinis su durimis")),
    ("apatinis_stalciai",  ("apatinis",   "Apatinis su stalčiais")),
    ("apatinis_plautuve",  ("apatinis",   "Plautuvės korpusas")),
    ("apatinis_indaplove", ("apatinis",   "Indaplovės frontas")),
    ("apatinis_orkaite",   ("apatinis",   "Orkaitės korpusas su kaitlente")),
    ("virsutinis",         ("virsutinis", "Viršutinis su durimis")),
    ("aukstas_nisa",       ("abu",        "Niša šaldytuvui su viršutine spintele")),
    ("aukstas_durys",      ("abu",        "Aukštas korpusas su durimis")),
])
__doc__ += "\n".join(f"  {k:<20} {v[0]:<10} {v[1]}" for k, v in TIPAI.items())


def deep_merge(base, over):
    out = copy.deepcopy(base)
    for k, v in (over or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out


class Engine:
    def __init__(self, std):
        self.std = std
        self.T = std["korpuso_ploksta"]["storis"]
        self.TB = std["nugarele"]["storis"]
        self.K2 = std["kantas"]["matomas"]
        self.K08 = std["kantas"]["dezes"]
        self.TK = std["fasadai"]["tarpas_krastuose"]
        self.TT = std["fasadai"]["tarpas_tarp"]
        self.parts, self.korpusai, self.klaidos = [], [], []
        self.hardware = OrderedDict()
        self.dekorai = {"apatiniai": std["fasadas"]["dekoras"], "virsutiniai": std["fasadas"]["dekoras"]}

    # ---------------------------------------------------------------- primityvai
    def part(self, korpusas, detale, grupe, L, W, storis, kantai, rastas, pos, size, dekoras=None, eile=None):
        self.parts.append({
            "korpusas": korpusas, "detale": detale, "grupe": grupe,
            "L": int(round(L)), "W": int(round(W)), "storis": storis,
            "kantai": list(kantai), "rastas": rastas,
            "pos": [int(round(v)) for v in pos], "size": [int(round(v)) for v in size],
            "dekoras": dekoras, "eile": eile,
        })

    def prietaisas(self, korpusas, pavadinimas, pos, size):
        """Buitinis prietaisas - tik vaizdui (3D ir projekcija), i pjovimo lapa neina."""
        self.parts.append({"korpusas": korpusas, "detale": pavadinimas, "grupe": "prietaisas", "L": 0, "W": 0,
                           "storis": 0, "kantai": [0, 0, 0, 0], "rastas": "-",
                           "pos": [int(round(v)) for v in pos], "size": [int(round(v)) for v in size],
                           "dekoras": None, "eile": None})

    def hw(self, pavadinimas, kiekis, vnt="vnt", pastaba=""):
        if pavadinimas not in self.hardware:
            self.hardware[pavadinimas] = {"pavadinimas": pavadinimas, "kiekis": 0, "vnt": vnt, "pastaba": pastaba}
        self.hardware[pavadinimas]["kiekis"] += kiekis

    def fasadas(self, cid, eile, L, W, rastas, pos, size, pavadinimas="Fasadas (durys)"):
        self.part(cid, pavadinimas, "fasadas", L, W, self.std["fasadas"]["storis"], (self.K2,) * 4, rastas,
                  pos, size, dekoras=self.dekorai[eile], eile=eile)

    # ---------------------------------------------------------------- bendri elementai
    def karkasas(self, cid, x0, y0, W, H, D, virsus="juostos", lentynos=1, lentynos_atitraukimas=None):
        """Sonai, dugnas, virsus (plokste arba 2 juostos), lentynos, nugarele. Grazina (zs, Ds)."""
        T, TB, K2 = self.T, self.TB, self.K2
        Ds, zs = D - TB, TB
        self.part(cid, "Šonas", "korpusas", H, Ds, T, (K2, 0, 0, 0), "V", (x0, y0, zs), (T, H, Ds))
        self.part(cid, "Šonas", "korpusas", H, Ds, T, (K2, 0, 0, 0), "V", (x0 + W - T, y0, zs), (T, H, Ds))
        self.part(cid, "Dugnas", "korpusas", W - 2 * T, Ds, T, (K2, 0, 0, 0), "H", (x0 + T, y0, zs), (W - 2 * T, T, Ds))
        if virsus == "ploksta":
            self.part(cid, "Viršus", "korpusas", W - 2 * T, Ds, T, (K2, 0, 0, 0), "H", (x0 + T, y0 + H - T, zs), (W - 2 * T, T, Ds))
        elif virsus == "juostos":
            for z in (zs + Ds - 100, zs):
                self.part(cid, "Juosta viršutinė", "korpusas", W - 2 * T, 100, T, (0, 0, 0, 0), "-",
                          (x0 + T, y0 + H - T, z), (W - 2 * T, T, 100))
        Ls = Ds - (self.std["fasadai"]["lentynos_atitraukimas"] if lentynos_atitraukimas is None else lentynos_atitraukimas)
        for i in range(lentynos):
            ly = y0 + T + (H - 2 * T) * (i + 1) // (lentynos + 1) - T // 2
            self.part(cid, "Lentyna", "korpusas", W - 2 * T - 2, Ls, T, (K2, 0, 0, 0), "H",
                      (x0 + T + 1, ly, zs), (W - 2 * T - 2, T, Ls))
        self.part(cid, "Nugarėlė", "nugarele", H, W, TB, (0, 0, 0, 0), "-", (x0, y0, 0), (W, H, TB))
        self.hw("Konfirmatas 7×50", 8 + (4 if virsus == "ploksta" else 0))
        self.hw("Nugarėlės varžtas 3,5×16", max(10, int(2 * (W + H) / 150)))
        self.hw("Lentynos laikiklis", 4 * lentynos)
        return zs, Ds

    def durys(self, cid, eile, x0, W, y0, H, z, n, rankena_apacioje=False):
        TK, TT = self.TK, self.TT
        R, T = self.std["rankena"], self.std["fasadas"]["storis"]
        fh = H - 2 * TK
        hy = y0 + TK + R["atitraukimas_nuo_virsaus"] if rankena_apacioje else y0 + TK + fh - R["atitraukimas_nuo_virsaus"] - R["ilgis"]
        if n == 1:
            fw, xs = W - 2 * TK, [x0 + TK]
        else:
            fw = (W - 2 * TK - TT) // 2
            xs = [x0 + TK, x0 + W - TK - fw]
        out = []
        for i, fx in enumerate(xs):
            self.fasadas(cid, eile, fh, fw, "V", (fx, y0 + TK, z), (fw, fh, T))
            atid_desine = (n == 1) or (i == 0)
            hx = fx + fw - R["atitraukimas_nuo_krasto"] - 8 if atid_desine else fx + R["atitraukimas_nuo_krasto"]
            out.append({"x": fx, "y": y0 + TK, "w": fw, "h": fh, "tipas": "durys",
                        "rankena": {"x": hx, "y": hy, "w": 8, "h": R["ilgis"], "kryptis": "V"}})
            lankstai = 2 if fh <= 900 else (3 if fh <= 1500 else 4)
            self.hw(self.std["furnitura"]["lankstas"], lankstai, "vnt", "2 vnt. iki 900 mm, 3 iki 1500, 4 virš")
            self.hw("Lanksto plokštelė 0 mm", lankstai)
            self.hw(f'Rankenėlė {R["ilgis"]} mm', 1)
        return out

    def stalcius(self, cid, eile, x0, W, fy, fh, zs, Ds, dezes_aukstis=None):
        """Vienas stalcius: fasadas + deze. Grazina fronta projekcijai."""
        T, TK, K08 = self.T, self.TK, self.K08
        S, R = self.std["stalcius"], self.std["rankena"]
        fw = W - 2 * TK
        self.fasadas(cid, eile, fw, fh, "H", (x0 + TK, fy, zs + Ds), (fw, fh, self.std["fasadas"]["storis"]), "Fasadas (stalčius)")
        bw, bl, bt = W - 2 * T - 2 * S["tarpas_sone"], S["dezes_ilgis"], S["dezes_storis"]
        bh = dezes_aukstis or S["dezes_aukstis"]
        bx, bz, by = x0 + T + S["tarpas_sone"], 50, fy + 20
        self.part(cid, "Stalčiaus dugnas", "stalcius", bw, bl, bt, (0, 0, 0, 0), "-", (bx, by, bz), (bw, bt, bl))
        for sx in (bx, bx + bw - bt):
            self.part(cid, "Stalčiaus šonas", "stalcius", bl, bh, bt, (K08, 0, 0, 0), "H", (sx, by + bt, bz), (bt, bh, bl))
        for sz in (bz, bz + bl - bt):
            self.part(cid, "Stalčiaus priekis/galas", "stalcius", bw - 2 * bt, bh, bt, (K08, 0, 0, 0), "H",
                      (bx + bt, by + bt, sz), (bw - 2 * bt, bh, bt))
        self.hw(S["begeliai"], 1, "kompl.", "pora bėgelių + fiksatoriai")
        self.hw(f'Rankenėlė {R["ilgis"]} mm', 1)
        return {"x": x0 + TK, "y": fy, "w": fw, "h": fh, "tipas": "stalcius",
                "rankena": {"x": x0 + W // 2 - R["ilgis"] // 2, "y": fy + fh // 2 - 4, "w": R["ilgis"], "h": 8, "kryptis": "H"}}

    def registruoti(self, cab, x0, y0, W, H, D, frontai, prietaisai=()):
        self.korpusai.append({"id": cab["id"], "tipas": cab["tipas"], "pavadinimas": TIPAI[cab["tipas"]][1],
                              "x": x0, "y": y0, "plotis": W, "aukstis": H, "gylis": D,
                              "frontai": frontai, "prietaisai": list(prietaisai)})

    # ---------------------------------------------------------------- apatiniai
    def apatinis(self, cab, x0):
        st, T, TK, TT = self.std, self.T, self.TK, self.TT
        cid, W, tipas = cab["id"], cab["plotis"], cab["tipas"]
        H, D, y0 = st["apatinis"]["korpuso_aukstis"], st["apatinis"]["gylis"], st["apatinis"]["cokolis"]
        n_durys = cab.get("durys", 1 if W <= 600 else 2)
        frontai, prietaisai = [], []

        if tipas == "apatinis_indaplove":
            # integruota indaplove: tik fasadas, korpuso nera; kaimynu sonai - nisos sienos
            fh, fw = H - 2 * TK, W - 2 * TK
            self.fasadas(cid, "apatiniai", fh, fw, "V", (x0 + TK, y0 + TK, D), (fw, fh, st["fasadas"]["storis"]), "Fasadas (indaplovė)")
            R = st["rankena"]
            frontai.append({"x": x0 + TK, "y": y0 + TK, "w": fw, "h": fh, "tipas": "indaplove",
                            "rankena": {"x": x0 + W // 2 - R["ilgis"] // 2, "y": y0 + TK + fh - 60, "w": R["ilgis"], "h": 8, "kryptis": "H"}})
            prietaisai.append({"x": x0, "y": y0, "w": W, "h": H, "pavadinimas": "INDAPLOVĖ"})
            self.prietaisas(cid, "Indaplovė", (x0 + 5, y0, 30), (W - 10, H - 5, D - 30))
            self.hw(f'Rankenėlė {R["ilgis"]} mm', 1)
            self.hw("Indaplovės montavimo komplektas", 1, "kompl.", "iš prietaiso")
            self.registruoti(cab, x0, y0, W, H, D, frontai, prietaisai)
            return

        if tipas == "apatinis_orkaite":
            O = st["orkaite"]
            zs, Ds = self.karkasas(cid, x0, y0, W, H, D, virsus="juostos", lentynos=0)
            # orkaites lentyna: nisa O.nisa_aukstis nuo lentynos virsaus iki korpuso virsaus
            ly = y0 + H - O["nisa_aukstis"] - T
            self.part(cid, "Orkaitės lentyna", "korpusas", W - 2 * T, Ds, T, (self.K2, 0, 0, 0), "H",
                      (x0 + T, ly, zs), (W - 2 * T, T, Ds))
            self.hw("Konfirmatas 7×50", 4)
            # stalcius po orkaite
            fh = ly - y0 - TK - TT // 2
            frontai.append(self.stalcius(cid, "apatiniai", x0, W, y0 + TK, fh, zs, Ds, dezes_aukstis=O["stalciaus_dezes_aukstis"]))
            prietaisai.append({"x": x0 + T, "y": ly + T, "w": W - 2 * T, "h": O["nisa_aukstis"], "pavadinimas": "ORKAITĖ"})
            prietaisai.append({"x": x0 + 40, "y": y0 + H + st["stalvirsis"]["storis"], "w": W - 80, "h": 6, "pavadinimas": "KAITLENTĖ"})
            self.prietaisas(cid, "Orkaitė", (x0 + T + 2, ly + T, 20), (W - 2 * T - 4, O["nisa_aukstis"] - 4, D - 10))
            self.prietaisas(cid, "Kaitlentė", (x0 + 40, y0 + H + st["stalvirsis"]["storis"], 60), (W - 80, 6, 480))
            self.hw("Orkaitės tvirtinimo varžtai", 1, "kompl.", "iš prietaiso")
            self.hw("Kaitlentės išpjova stalviršyje", 1, "vnt", f"{W - 80}×480 orientacinė – pagal prietaiso šabloną")
            self.registruoti(cab, x0, y0, W, H, D, frontai, prietaisai)
            return

        zs, Ds = self.karkasas(cid, x0, y0, W, H, D, virsus="juostos", lentynos=1 if tipas == "apatinis_durys" else 0)
        if tipas in ("apatinis_durys", "apatinis_plautuve"):
            frontai = self.durys(cid, "apatiniai", x0, W, y0, H, zs + Ds, n_durys)
            if tipas == "apatinis_plautuve":
                prietaisai.append({"x": x0 + 40, "y": y0 + H + st["stalvirsis"]["storis"], "w": W - 80, "h": 6, "pavadinimas": "PLAUTUVĖ"})
                self.prietaisas(cid, "Plautuvė", (x0 + 40, y0 + H + st["stalvirsis"]["storis"] - 150, 60), (W - 80, 150 + 6, 480))
                self.hw("Plautuvės išpjova stalviršyje", 1, "vnt", "pagal plautuvės šabloną")
        if tipas == "apatinis_stalciai":
            n = cab.get("stalciai", 3)
            fh = (H - 2 * TK - (n - 1) * TT) // n
            for i in range(n):
                frontai.append(self.stalcius(cid, "apatiniai", x0, W, y0 + TK + i * (fh + TT), fh, zs, Ds))
        self.hw(st["furnitura"]["kojele"], 4)
        self.hw("Cokolio klipsas", 2)
        self.registruoti(cab, x0, y0, W, H, D, frontai, prietaisai)

    # ---------------------------------------------------------------- virsutiniai
    def virsutinis(self, cab, x0, y0=None, H=None, D=None, W=None, eile="virsutiniai"):
        st = self.std
        cid = cab["id"]
        W = W or cab["plotis"]
        H = H or cab.get("aukstis") or st["virsutinis"]["korpuso_aukstis"]
        D = D or cab.get("gylis") or st["virsutinis"]["gylis"]
        y0 = st["virsutinis"]["apacia_nuo_grindu"] if y0 is None else y0
        zs, Ds = self.karkasas(cid, x0, y0, W, H, D, virsus="ploksta", lentynos=(0 if H < 400 else 1 if H < 700 else 2), lentynos_atitraukimas=20)
        frontai = self.durys(cid, eile, x0, W, y0, H, zs + Ds, cab.get("durys", 1 if W <= 600 else 2), rankena_apacioje=True)
        self.hw(st["furnitura"]["pakaba"], 2, "vnt", "viršutiniams korpusams")
        self.registruoti(cab, x0, y0, W, H, D, frontai)

    # ---------------------------------------------------------------- aukšti
    def aukstas_nisa(self, cab, x0):
        """Nisa laisvai stovinciam saldytuvui: sonine plokste (-es) per visa auksti + virsutine spintele."""
        st, T, K2 = self.std, self.T, self.K2
        N = st["nisa"]
        cid, W = cab["id"], cab["plotis"]
        H = cab.get("aukstis", N["aukstis"])
        D = cab.get("gylis", N["gylis"])
        Hv = cab.get("virsutines_aukstis", N["virsutines_aukstis"])
        sonai = cab.get("sonai", "desine")
        xs = {"kaire": [x0], "desine": [x0 + W - T], "abu": [x0, x0 + W - T]}[sonai]
        for sx in xs:
            self.part(cid, "Šoninė plokštė (niša)", "korpusas", H, D, T, (K2, 0, K2, 0), "V", (sx, 0, 0), (T, H, D))
        vx0 = x0 + (T if sonai in ("kaire", "abu") else 0)
        vw = W - T * len(xs)
        sub = {"id": cid, "tipas": "virsutinis", "plotis": vw, "durys": cab.get("durys", 1 if vw <= 600 else 2)}
        self.virsutinis(sub, vx0, y0=H - Hv, H=Hv, D=D, W=vw, eile="virsutiniai")
        k = self.korpusai.pop()           # virsutinis uzregistravo save - sujungiame i vienos nisos irasa
        niche_h = H - Hv
        prietaisai = [{"x": vx0, "y": 0, "w": vw, "h": niche_h, "pavadinimas": "ŠALDYTUVAS"}]
        self.prietaisas(cid, "Šaldytuvas", (vx0 + 20, 0, 20), (vw - 40, niche_h - 30, D - 40))
        self.registruoti(cab, x0, 0, W, H, D, k["frontai"], prietaisai)
        self.korpusai[-1]["virsutine"] = {"x": vx0, "y": H - Hv, "plotis": vw, "aukstis": Hv}

    def aukstas_durys(self, cab, x0):
        """Aukstas sandeliukas: karkasas per visa auksti, lentynos, durys dviem aukstais (riba - virsutiniu apacia)."""
        st = self.std
        N = st["nisa"]
        cid, W = cab["id"], cab["plotis"]
        H_top = cab.get("aukstis", N["aukstis"])
        D = cab.get("gylis", st["apatinis"]["gylis"])
        y0 = st["apatinis"]["cokolis"]
        H = H_top - y0
        zs, Ds = self.karkasas(cid, x0, y0, W, H, D, virsus="ploksta", lentynos=cab.get("lentynos", 4))
        riba = cab.get("duru_riba", st["virsutinis"]["apacia_nuo_grindu"])
        n = cab.get("durys", 1 if W <= 600 else 2)
        frontai = self.durys(cid, "apatiniai", x0, W, y0, riba - y0 - self.TT // 2, zs + Ds, n)
        frontai += self.durys(cid, "virsutiniai", x0, W, riba + self.TT // 2, H_top - riba - self.TT // 2, zs + Ds, n, rankena_apacioje=True)
        self.hw(st["furnitura"]["kojele"], 4)
        self.hw("Cokolio klipsas", 2)
        self.registruoti(cab, x0, y0, W, H, D, frontai)

    # ---------------------------------------------------------------- siena
    def build(self, projektas, katalogas):
        st, T, K2 = self.std, self.T, self.K2
        siena = projektas["siena"]
        kat = {d["kodas"]: d for d in katalogas["fasado_variantai"]}
        for eile in ("apatiniai", "virsutiniai"):
            kodas = projektas.get("dekorai", {}).get(eile)
            if kodas:
                if kodas not in kat:
                    self.klaidos.append(f'dekoras "{kodas}" ({eile}) nėra assets/dekorai.json kataloge')
                self.dekorai[eile] = kodas
        for cab in projektas["korpusai"]:
            if cab["tipas"] not in TIPAI:
                self.klaidos.append(f'{cab["id"]}: nežinomas tipas "{cab["tipas"]}" (galimi: {", ".join(TIPAI)})')
        if self.klaidos:
            raise SystemExit("KLAIDA: " + "; ".join(self.klaidos))

        xa = xv = 0
        apat_range, virs_range = [None, None], [None, None]
        for cab in projektas["korpusai"]:
            eile = TIPAI[cab["tipas"]][0]
            if eile == "abu":
                if xa != xv:
                    self.klaidos.append(f'{cab["id"]}: aukštas korpusas, bet apatinė ({xa}) ir viršutinė ({xv}) eilės nesutampa prieš jį')
                getattr(self, cab["tipas"])(cab, xa)
                xa += cab["plotis"]; xv = xa
            elif eile == "apatinis":
                self.apatinis(cab, xa)
                apat_range[0] = xa if apat_range[0] is None else apat_range[0]
                xa += cab["plotis"]; apat_range[1] = xa
            else:
                self.virsutinis(cab, xv)
                virs_range[0] = xv if virs_range[0] is None else virs_range[0]
                xv += cab["plotis"]; virs_range[1] = xv
        for pav, ilgis in (("apatinės eilės", xa), ("viršutinės eilės", xv)):
            if ilgis and ilgis != siena["ilgis"]:
                self.klaidos.append(f"{pav} pločių suma {ilgis} ≠ sienos ilgis {siena['ilgis']} (skirtumas {siena['ilgis'] - ilgis} mm)")
        if self.klaidos:
            raise SystemExit("KLAIDA: " + "; ".join(self.klaidos))

        ST = st["stalvirsis"]
        if apat_range[0] is not None:
            a0, a1 = apat_range
            y_st = st["apatinis"]["cokolis"] + st["apatinis"]["korpuso_aukstis"]
            self.part("—", "Stalviršis", "stalvirsis", a1 - a0, ST["gylis"], ST["storis"], (K2, 0, 0, 0), "H",
                      (a0, y_st, 0), (a1 - a0, ST["storis"], ST["gylis"]), dekoras=ST["dekoras"])
            zc = st["apatinis"]["gylis"] - st["apatinis"]["cokolio_atitraukimas"]
            self.part("—", "Cokolis", "fasadas", a1 - a0, st["apatinis"]["cokolis"], st["fasadas"]["storis"], (K2, 0, 0, 0), "H",
                      (a0, 0, zc), (a1 - a0, st["apatinis"]["cokolis"], st["fasadas"]["storis"]), dekoras=self.dekorai["apatiniai"], eile="apatiniai")
            hpl = projektas.get("hpl")
            if hpl and virs_range[0] is not None:
                h = st["virsutinis"]["apacia_nuo_grindu"] - (y_st + ST["storis"])
                v0, v1 = max(a0, virs_range[0]), min(a1, virs_range[1])
                self.part("—", "HPL siena", "hpl", v1 - v0, h, hpl.get("storis", st["hpl"]["storis"]), (0, 0, 0, 0), "-",
                          (v0, y_st + ST["storis"], 0), (v1 - v0, h, hpl.get("storis", st["hpl"]["storis"])), dekoras=hpl.get("dekoras", st["hpl"]["dekoras"]))
        if virs_range[0] is not None:
            v0, v1 = virs_range
            self.hw("Montavimo bėgelis viršutiniams", 1, "vnt", f"{v1 - v0} mm")
            if projektas.get("led"):
                self.hw("LED juosta po viršutiniais + profilis", round((v1 - v0) / 1000, 2), "m", "maitinimo blokas ir jungiklis atskirai")

        pjovimas = self.pjovimo_eilutes()
        return {
            "projektas": {k: v for k, v in projektas.items() if not k.startswith("_")},
            "standartas": {k: v for k, v in st.items() if not k.startswith("_")},
            "fasado_variantai": katalogas["fasado_variantai"],
            "dekorai": dict(self.dekorai),
            "korpusai": self.korpusai,
            "detales": self.parts,
            "pjovimas": pjovimas,
            "suvestine": self.suvestine(pjovimas),
        }

    # ---------------------------------------------------------------- pjovimo lapas
    def grupes(self):
        st = self.std
        kp, fs = st["korpuso_ploksta"], st["fasadas"]
        g = OrderedDict()
        g["korpusas"] = {"pavadinimas": f'LMDP {kp["storis"]} mm — korpusai', "dekoras": kp["dekoras"], "dekoro_pavadinimas": kp["pavadinimas"], "storis": kp["storis"]}
        for eile, pav in (("apatiniai", "apatinių fasadai ir cokolis"), ("virsutiniai", "viršutinių fasadai")):
            g[f"fasadas:{eile}"] = {"pavadinimas": f'LMDP {fs["storis"]} mm — {pav}', "dekoras": self.dekorai[eile],
                                    "dekoro_pavadinimas": "", "storis": fs["storis"], "eile": eile}
        g["stalcius"] = {"pavadinimas": f'LMDP {st["stalcius"]["dezes_storis"]} mm — stalčių dėžės', "dekoras": kp["dekoras"], "dekoro_pavadinimas": kp["pavadinimas"], "storis": st["stalcius"]["dezes_storis"]}
        g["nugarele"] = {"pavadinimas": f'HDF {st["nugarele"]["storis"]} mm — nugarėlės', "dekoras": st["nugarele"]["dekoras"], "dekoro_pavadinimas": "balta", "storis": st["nugarele"]["storis"]}
        g["stalvirsis"] = {"pavadinimas": f'Stalviršis {st["stalvirsis"]["storis"]} mm (atskiras tiekėjas)', "dekoras": st["stalvirsis"]["dekoras"], "dekoro_pavadinimas": st["stalvirsis"]["pavadinimas"], "storis": st["stalvirsis"]["storis"], "be_lapu": True}
        g["hpl"] = {"pavadinimas": f'HPL siena {st["hpl"]["storis"]} mm (atskiras tiekėjas)', "dekoras": st["hpl"]["dekoras"], "dekoro_pavadinimas": st["hpl"]["pavadinimas"], "storis": st["hpl"]["storis"], "be_lapu": True}
        return g

    def pjovimo_eilutes(self):
        out = []
        for g, meta in self.grupes().items():
            grupe, eile = (g.split(":") + [None])[:2]
            merged = OrderedDict()
            for p in self.parts:
                if p["grupe"] != grupe or (eile and p["eile"] != eile):
                    continue
                key = (p["detale"], p["L"], p["W"], p["storis"], tuple(p["kantai"]), p["rastas"])
                m = merged.setdefault(key, {"detale": p["detale"], "L": p["L"], "W": p["W"], "storis": p["storis"],
                                            "kantai": p["kantai"], "rastas": p["rastas"], "vnt": 0, "korpusai": OrderedDict()})
                m["vnt"] += 1
                m["korpusai"][p["korpusas"]] = m["korpusai"].get(p["korpusas"], 0) + 1
            if not merged:
                continue
            if grupe == "hpl":
                meta = dict(meta, dekoras=self.parts[[i for i, p in enumerate(self.parts) if p["grupe"] == "hpl"][0]]["dekoras"] or meta["dekoras"])
            eilutes = []
            for i, m in enumerate(merged.values(), 1):
                zym = ", ".join(f"{k} ×{n}" if n > 1 else k for k, n in m["korpusai"].items())
                eilutes.append({"nr": i, "detale": m["detale"], "zymejimas": zym, "L": m["L"], "W": m["W"],
                                "vnt": m["vnt"], "kantai": m["kantai"], "rastas": m["rastas"]})
            out.append({"grupe": g, **meta, "eilutes": eilutes})
        return out

    def suvestine(self, pjovimas):
        L = self.std["lapas"]
        lapas_m2 = L["plotis"] * L["aukstis"] / 1e6
        plokstes, kantai_m = [], {}
        for grp in pjovimas:
            m2 = sum(e["L"] * e["W"] * e["vnt"] for e in grp["eilutes"]) / 1e6
            lapai = None if grp.get("be_lapu") else int(-(-m2 // (lapas_m2 * L["iseiga"])))
            plokstes.append({"grupe": grp["pavadinimas"], "grupes_id": grp["grupe"], "dekoras": grp["dekoras"], "m2": round(m2, 2), "lapai": lapai})
            for e in grp["eilutes"]:
                kL1, kL2, kW1, kW2 = e["kantai"]
                for k, ilgis in ((kL1, e["L"]), (kL2, e["L"]), (kW1, e["W"]), (kW2, e["W"])):
                    if k:
                        kantai_m[k] = kantai_m.get(k, 0) + ilgis * e["vnt"] / 1000
        kantai = [{"storis": k, "m": round(v * (1 + L["kanto_atsarga"]), 1)} for k, v in sorted(kantai_m.items(), reverse=True)]
        return {"plokstes": plokstes, "kantai": kantai, "furnitura": list(self.hardware.values()),
                "prielaidos": {"lapas": f'{L["plotis"]} × {L["aukstis"]} mm', "iseiga": L["iseiga"], "kanto_atsarga": L["kanto_atsarga"]}}


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def main():
    here = Path(__file__).resolve().parent.parent
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("projektas")
    ap.add_argument("--std", default=str(here / "assets" / "standartas.json"))
    ap.add_argument("--dekorai", default=str(here / "assets" / "dekorai.json"))
    ap.add_argument("--out", default=".")
    a = ap.parse_args()
    projektas = load(a.projektas)
    std = deep_merge(load(a.std), projektas.get("standartas"))
    model = Engine(std).build(projektas, load(a.dekorai))
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    (out / "model.json").write_text(json.dumps(model, ensure_ascii=False, indent=1), encoding="utf-8")
    n_det = sum(1 for p in model["detales"] if p["grupe"] != "prietaisas")
    print(f"model.json: detalių {n_det}, pjovimo eilučių {sum(len(g['eilutes']) for g in model['pjovimas'])}")
    for pl in model["suvestine"]["plokstes"]:
        print(f"  {pl['grupe']}: {pl['m2']} m², lapų: {pl['lapai'] if pl['lapai'] is not None else '—'}")
    print("  kantai:", ", ".join(f'{k["storis"]} mm – {k["m"]} m' for k in model["suvestine"]["kantai"]))


if __name__ == "__main__":
    main()
