"""v302 (Rytis 2026-10-16, Joker 226057: „failai ne pagal mastelį, įkelti reikia 1:1000"): gamybos DXF VIENETAI.
Geometrija visada mm; antraštėje $INSUNITS turi būti 4 (mm). ezdxf.new() numatyta 6 (metrai) -> CorelDRAW / CAD importuoja
1000 kartų per didelį. Kiekvienas generatorius po ezdxf.new() nustato doc.units = ezdxf.units.MM.
python3 scripts/patikra_dxf.py failas.dxf [...]  ->  0 klaidų arba sąrašas; exit 1 jei yra klaidų."""
import sys
import ezdxf


def check(fn):
    d = ezdxf.readfile(fn); err = []
    if d.header.get("$INSUNITS") != 4:
        err.append(f"DXF VIENETAI: $INSUNITS {d.header.get('$INSUNITS')} (turi būti 4 = mm)")
    if d.header.get("$MEASUREMENT", 1) != 1:
        err.append("DXF VIENETAI: $MEASUREMENT ne metrinė (turi būti 1)")
    return err


if __name__ == "__main__":
    bad = 0
    for f in sys.argv[1:]:
        e = check(f); bad += len(e)
        print(f"{f}: " + ("0 klaid." if not e else "; ".join(e)))
    print("IŠ VISO:", bad); sys.exit(1 if bad else 0)
