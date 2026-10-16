"""v299 (2026-10-16, Joker 226057 ALT8900): patvirtinto folded plate + lipdukai užsakymo VIENTISAS DXF kiekvienai plokštei.
Ryčio taisyklė: patvirtintam užsakymui siunčiami tik maketo PDF, LED PDF ir VIENTISI DXF. folded_vinyl.py išveda atskirus
failus (išklotinės `_flat_<P>*.dxf`, plėvelės `_vinyl_<P>_<spalva>.dxf`) - šis skriptas sujungia juos į `<prefix>_<P>_combined.dxf`:
išklotinės kairėje viena po kita (CNC), plėvelės dešinėje (ploteris); sluoksniai su prefiksu FLAT_<dalis>_ / VINYL_<SPALVA>_,
geometrija tik perkeliama (be pasukimo / veidrodžio).
python3 scripts/dxf_combine.py <out_dir> <prefix> [--panels A,B] [--gap 200]
"""
import argparse, glob, os, sys, ezdxf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ezdxf import bbox
from ezdxf.math import Matrix44

ap = argparse.ArgumentParser()
ap.add_argument("out_dir"); ap.add_argument("prefix")
ap.add_argument("--panels", default=None, help="plokščių vardai (numatyta - iš _flat_ failų)")
ap.add_argument("--gap", type=float, default=200)
A = ap.parse_args()
panels = A.panels.split(",") if A.panels else sorted({f.rsplit("_flat_", 1)[1][:-4].split("_")[0]
                                                     for f in glob.glob(f"{A.out_dir}/{A.prefix}_flat_*.dxf")})


def put(doc, fn, tag, x, y_top):
    src = ezdxf.readfile(fn); sm = src.modelspace(); b = bbox.extents(sm)
    T = Matrix44.translate(x - b.extmin.x, y_top - b.extmax.y, 0)
    for e in sm:
        c = e.copy(); c.transform(T)
        lay = f"{tag}_{e.dxf.layer}"
        if lay not in doc.layers:
            sl = src.layers.get(e.dxf.layer)
            doc.layers.add(lay, color=sl.color if sl else 7)
        c.dxf.layer = lay
        doc.modelspace().add_entity(c)
    return b.size.x, b.size.y


for P in panels:
    flats = sorted(glob.glob(f"{A.out_dir}/{A.prefix}_flat_{P}.dxf") + glob.glob(f"{A.out_dir}/{A.prefix}_flat_{P}_*.dxf"))
    vin = sorted(glob.glob(f"{A.out_dir}/{A.prefix}_vinyl_{P}_*.dxf"))
    if not flats and not vin:
        print(f"  ! {P}: failų nėra"); continue
    doc = ezdxf.new("R2010"); y = 0; xmax = 0
    doc.units = ezdxf.units.MM; doc.header["$INSUNITS"] = 4; doc.header["$MEASUREMENT"] = 1   # v302: mm, ne metrai
    for f in flats:
        w, h = put(doc, f, "FLAT_" + f.rsplit("_flat_", 1)[1][:-4], 0, y); y -= h + A.gap; xmax = max(xmax, w)
    x = xmax + 2 * A.gap
    for f in vin:
        w, h = put(doc, f, "VINYL_" + f.rsplit("_vinyl_", 1)[1][:-4].split("_", 1)[1].upper(), x, 0); x += w + A.gap
    fn = f"{A.out_dir}/{A.prefix}_{P}_combined.dxf"; doc.saveas(fn)
    n_src = sum(len(ezdxf.readfile(f).modelspace()) for f in flats + vin)
    n = len(ezdxf.readfile(fn).modelspace())
    assert n == n_src, f"{fn}: objektų {n} != šaltinių {n_src}"
    import patikra_dxf
    assert patikra_dxf.check(fn) == [], f"{fn}: {patikra_dxf.check(fn)}"
    print(f"OK {fn}: {len(flats)} išklotinės + {len(vin)} plėvelės, {n} objektų")
