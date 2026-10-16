"""v326 (Rytis 2026-10-16: „sistema turi veikti stabiliai ir klaidos neturi kartotis. peržiūrėk ir patikrink nuo A iki Z").
REGRESIJA - visi etaloniniai / testiniai projektai pergeneruojami DABARTINIAIS generatoriais ir tikrinami
(`patikra_lapas.py` = 0, `patikra_corel.py` = 0, `patikra_dxf.py` = 0, `test_p6.py` = OK).

Paleisti po KIEKVIENO bendro generatoriaus / lapas_core / patikros pakeitimo, PRIEŠ commit:
    python3 scripts/regresija.py            # visi
    python3 scripts/regresija.py p6 folded  # tik atvejai, kurių pavadinime yra šie žodžiai
Repo failų NEKEIČIA: kiekvienas projektas kopijuojamas į laikiną veidrodį (scripts/, assets/, references/ - nuorodos),
generatoriai paleidžiami ten. Exit 1 - jei bent vienas atvejis ne 0."""
import concurrent.futures as CF
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))        # .../reklama
SCR = os.path.join(ROOT, "scripts")

# (vardas, projekto katalogas, komandos [cwd = projekto kopija], tikrinami PDF, tikrinami DXF (glob))
B = "../../braizyti_begeliai.py"
CASES = [
    ("p6 rails bandymas_3500", "bandymas_3500", [["python3", B, "spec.json", "out.pdf"]], ["out.pdf"], []),
    ("p6 rails alytus", "alytus_p6_test", [["python3", B, "spec.json", "out.pdf"]], ["out.pdf"], []),
    ("p6 rails lietuva", "lietuva_p6_test", [["python3", B, "spec.json", "out.pdf"]], ["out.pdf"], []),
    ("p6 rails securitas", "brandfactory_226030_securitas", [["python3", B, "spec_226030.json", "out.pdf"]], ["out.pdf"], []),
    ("p1 rails welcome", "welcome_p1_test", [["python3", B, "spec.json", "out.pdf"]], ["out.pdf"], []),
    ("p6 rails danbolig", "bnskilte_3295_danbolig", [["python3", B, "spec_DB-0002.json", "out.pdf"]], ["out.pdf"], []),
    ("lightbox danbolig", "bnskilte_3295_danbolig", [["python3", "../../sviesdeze.py", "spec_DB-0001.json", "lb.pdf"]], ["lb.pdf"],
     ["lb_gamyba.dxf"]),
    ("lightbox sviesdeze 500", "sviesdeze_500_logo", [["python3", "../../sviesdeze.py", "spec.json", "out.pdf"]], ["out.pdf"],
     ["out_gamyba.dxf"]),
    ("lightbox sviesdeze 700 kojos", "sviesdeze_700x370_kojos", [["python3", "../../sviesdeze.py", "spec.json", "out.pdf"]],
     ["out.pdf"], ["out_gamyba.dxf"]),
    ("lightbox p10 doublesided", "p10_lightbox_doublesided_test",
     [["python3", "../../p10_lightbox_doublesided.py", "spec.json", "out.pdf"]], ["out.pdf"], ["out_gamyba.dxf"]),
    ("lightbox p10 doublesided B", "p10_lightbox_doublesided_test",
     [["python3", "../../p10_lightbox_doublesided.py", "spec_B.json", "outB.pdf"]], ["outB.pdf"], ["outB_gamyba.dxf"]),
    ("folded vinyl joker", "brandfactory_226057_joker", [["python3", "../../folded_vinyl.py", "spec_ALT8900.json", "out.pdf"]],
     ["out.pdf"], ["out_*.dxf"]),
    ("order leapmotor", "leapmotor_33577", [["python3", "build_order.py"]], ["ALT0000_Order_33577.pdf"], ["*.dxf"]),
    ("order kvickly pieces", "bnskilte_3311_kvickly", [["python3", "build_order.py"]], ["ALT0000_PO_3311_Kvickly.pdf"], []),
    ("order omoda", "omoda_33580", [["python3", "build_order.py"]], ["ALT0000_Order_33580.pdf"], []),
    ("order kia", "alfaneon_kia_33597", [["python3", "kia.py"]], ["ALT0000_KIA_order_33597.pdf"], []),
    ("order bodo folded", "clasohlson_226045_bodo", [["python3", "bodo.py", "ALT0000_Order_226045.pdf"]], ["ALT0000_Order_226045.pdf"], []),
    ("p6 folded bandymas", "bandymas_3500_folded", [["python3", "folded_test.py"]], ["TEST_Bandymas_folded.pdf"],
     ["TEST_Bandymas_folded_combined.dxf"]),
    # v326: patvirtintas SPAR 225960 (18 lapų: P6 ant rėmo, folded back plate + vinyl, portalas, grafika, FRISK P6 ant folded)
    ("order spar 225960", "spar_225960", [["python3", "lapai.py"],
                                          ["python3", "../../../folded_vinyl.py", "sk/spec_bp7.json", "sk/bp7.pdf"],
                                          ["python3", "../../../folded_vinyl.py", "sk/spec_bp89.json", "sk/bp89.pdf"],
                                          ["python3", "kiti_lapai.py"], ["python3", "rinkinys.py"], ["python3", "dxf_rinkinys.py"]],
     ["out/ALT8901_10.16_RS_SPAR_order_225960.pdf"], ["out/*.dxf"], "alt8901"),
]
# žinomi, dar neišspręsti (Ryčio sprendimas) - rodomi, bet regresijos nesugadina; kiekvienas su priežastimi
KNOWN = {
    "order kia": "COREL: 5 GOST šriftai (įdėtas kliento fragmentas su savo šriftais) - laukia sprendimo",
}


def mirror(proj):
    """laikinas reklama/ veidrodis: viskas - nuorodos, tik scripts/projektai/<proj> - kopija"""
    tmp = tempfile.mkdtemp(prefix="regr_")
    m = os.path.join(tmp, "reklama")
    os.makedirs(os.path.join(m, "scripts", "projektai"))
    for n in os.listdir(ROOT):
        if n != "scripts":
            os.symlink(os.path.join(ROOT, n), os.path.join(m, n))
    for n in os.listdir(SCR):
        if n != "projektai":
            os.symlink(os.path.join(SCR, n), os.path.join(m, "scripts", n))
    for n in os.listdir(os.path.join(SCR, "projektai")):
        if n != proj:
            os.symlink(os.path.join(SCR, "projektai", n), os.path.join(m, "scripts", "projektai", n))
    shutil.copytree(os.path.join(SCR, "projektai", proj), os.path.join(m, "scripts", "projektai", proj), symlinks=True)
    return tmp, os.path.join(m, "scripts", "projektai", proj), os.path.join(m, "scripts")


def run_case(case):
    name, proj, cmds, pdfs, dxfs = case[:5]
    tmp, cwd, scr = mirror(proj)
    cwd = os.path.join(cwd, case[5]) if len(case) > 5 else cwd          # projekto pakatalogis (pvz. spar_225960/alt8901)
    errs = []
    try:
        for c in cmds:
            r = subprocess.run(c, cwd=cwd, capture_output=True, text=True, timeout=900)
            if r.returncode:
                errs.append(f"rc {r.returncode}: {(r.stderr or r.stdout).strip()[-300:]}")
        for p in pdfs:
            fn = os.path.join(cwd, p)
            if not os.path.exists(fn):
                errs.append(f"{p}: nesugeneruota"); continue
            r = subprocess.run(["python3", os.path.join(scr, "patikra_lapas.py"), fn], capture_output=True, text=True, cwd=cwd)
            n = re.findall(r"IŠ VISO: (\d+)", r.stdout)
            if not n or int(n[-1]):
                errs += [f"{p}: {l.strip()}" for l in r.stdout.splitlines() if l.startswith("    ")][:12] or [f"{p}: {r.stdout[-300:]}"]
            r = subprocess.run(["python3", os.path.join(scr, "patikra_corel.py"), fn], capture_output=True, text=True, cwd=cwd)
            if "IŠ VISO: 0" not in r.stdout:
                errs.append(f"{p}: COREL {r.stdout.strip()[-200:]}")
        for g in dxfs:
            fs = glob.glob(os.path.join(cwd, g))
            if not fs:
                errs.append(f"{g}: DXF nesugeneruotas"); continue
            r = subprocess.run(["python3", os.path.join(scr, "patikra_dxf.py")] + fs, capture_output=True, text=True, cwd=cwd)
            if "IŠ VISO: 0" not in r.stdout:
                errs += [f"DXF: {l.strip()}" for l in r.stdout.splitlines() if ":" in l and "0 klaid" not in l and "IŠ VISO" not in l][:8]
    except Exception as e:
        errs.append(f"išimtis: {e}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return name, errs


def main(filt):
    cases = [c for c in CASES if all(f in c[0] for f in filt)]
    bad = 0
    with CF.ThreadPoolExecutor(max_workers=6) as ex:
        res = list(ex.map(run_case, cases))
    # test_p6 - P6 pagrindinė taisyklė (taip pat veidrodyje: jis rašo į bandymas_3500*)
    if not filt or any(f in "p6 test_p6" for f in filt):
        tmp, cwd, scr = mirror("bandymas_3500")
        os.unlink(os.path.join(os.path.dirname(cwd), "bandymas_3500_folded"))
        shutil.copytree(os.path.join(SCR, "projektai", "bandymas_3500_folded"), os.path.join(os.path.dirname(cwd), "bandymas_3500_folded"))
        r = subprocess.run(["python3", os.path.join(scr, "test_p6.py")], capture_output=True, text=True)
        res.append(("test_p6 (P6 pagrindinė taisyklė)", [] if r.returncode == 0 else r.stdout.strip().splitlines()[-8:]))
        shutil.rmtree(tmp, ignore_errors=True)
    for name, errs in res:
        if errs and name in KNOWN:
            print(f"ŽINOMA  {name}: {KNOWN[name]}")
            continue
        print(("OK     " if not errs else "KLAIDA ") + name)
        for e in errs:
            print("         ", e[:220])
        bad += bool(errs)
    print(f"REGRESIJA: {len(res) - bad} / {len(res)} OK")
    return bad


if __name__ == "__main__":
    sys.exit(1 if main(sys.argv[1:]) else 0)
