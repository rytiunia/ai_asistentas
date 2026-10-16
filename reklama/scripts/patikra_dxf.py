"""v302 (Rytis 2026-10-16, Joker 226057: „failai ne pagal mastelį, įkelti reikia 1:1000"): gamybos DXF VIENETAI.
Geometrija visada mm; antraštėje $INSUNITS turi būti 4 (mm). ezdxf.new() numatyta 6 (metrai) -> CorelDRAW / CAD importuoja
1000 kartų per didelį. Kiekvienas generatorius po ezdxf.new() nustato doc.units = ezdxf.units.MM.
python3 scripts/patikra_dxf.py failas.dxf [...]  ->  0 klaidų arba sąrašas; exit 1 jei yra klaidų."""
import os
import sys
import ezdxf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def check(fn):
    d = ezdxf.readfile(fn); err = []
    if d.header.get("$INSUNITS") != 4:
        err.append(f"DXF VIENETAI: $INSUNITS {d.header.get('$INSUNITS')} (turi būti 4 = mm)")
    if d.header.get("$MEASUREMENT", 1) != 1:
        err.append("DXF VIENETAI: $MEASUREMENT ne metrinė (turi būti 1)")
    # v312 (Rytis 2026-10-16: „daug taškų, tarp kurių tiesios linijos, nors apvalus - kampuotas"): KAMPUOTA KREIVĖ -
    #  laužtė (LWPOLYLINE / POLYLINE / LINE grandinė be lankų), kurioje >= 6 iš eilės trumpos atkarpos su mažais posūkiais.
    #  Generatoriai rašo per kreives.saveas (tiesės + lankai); pataisyti esamą: python3 scripts/kreives_fit.py failas.dxf
    import kreives as KR
    bad = {}
    for lay in [d.modelspace()] + [b_ for b_ in d.blocks if not b_.name.startswith("*")]:
        for e in lay.query("LWPOLYLINE POLYLINE"):
            if e.dxftype() == "LWPOLYLINE":
                pts = list(e.get_points("xyb"))
                if any(abs(p[2]) > 1e-12 for p in pts):
                    continue
                closed = bool(e.closed)
            else:
                pts = [tuple(v.dxf.location)[:2] for v in e.vertices]
                if any(abs(v.dxf.get("bulge", 0)) > 1e-12 for v in e.vertices):
                    continue
                closed = e.is_closed
            if KR.angular_runs(pts, closed) >= 6:
                bad[e.dxf.layer] = bad.get(e.dxf.layer, 0) + 1
    for ly_, n_ in bad.items():
        err.append(f"KAMPUOTA KREIVĖ: sluoksnis {ly_} - {n_} kontūr. iš trumpų tiesių be lankų (kreives.saveas / kreives_fit.py)")
    # v318 (Rytis 2026-10-16): P6 ant rėmo drenažas - PUSLANKIS dugno kontūre (išpjaunamas kartu), ne atskira Ø8 skylutė.
    #  P6 DXF (2_GALAS dugnas) su Ø8 apskritimais - senas būdas (p6_dxf --drain-hole tik paprašius). Folded plate - netikrinama.
    n8 = 0
    for lay in [d.modelspace()] + [b_ for b_ in d.blocks if not b_.name.startswith("*")]:
        n8 += sum(1 for e in lay.query("CIRCLE") if e.dxf.layer == "2_GALAS" and abs(e.dxf.radius - 4.0) < 0.05)
    if n8 and "--drain-hole" not in str(d.header.get("$PROJECTNAME", "")):
        err.append(f"DRENAŽAS SKYLUTE: 2_GALAS - {n8} x Ø8 apskritimai; P6 ant rėmo drenažas - puslankis dugno kontūre (v318)")
    return err


if __name__ == "__main__":
    bad = 0
    for f in sys.argv[1:]:
        e = check(f); bad += len(e)
        print(f"{f}: " + ("0 klaid." if not e else "; ".join(e)))
    print("IŠ VISO:", bad); sys.exit(1 if bad else 0)
