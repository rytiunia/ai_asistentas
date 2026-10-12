"""reklama skill'o diegimas į programą iš GitHub repo klono (vienas šaltinis: rytiunia/ai_asistentas).

python skill_setup.py                 # git pull ~/ai_asistentas ir įdiegia reklama/
python skill_setup.py kelias/reklama.zip   # atsarginis būdas - iš zip
Repo vietą galima pakeisti aplinkos kintamuoju AI_ASISTENTAS_REPO.
"""
import os
import subprocess
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
SKILL_DIR = APP_DIR / ".claude" / "skills" / "reklama"
REPO_DIR = Path(os.environ.get("AI_ASISTENTAS_REPO", Path.home() / "ai_asistentas"))


def _version_of(text):
    m = re.search(r"\*\*Versija:\s*([^*]+)\*\*", text)
    return m.group(1).strip() if m else None


def installed_version():
    p = SKILL_DIR / "SKILL.md"
    return _version_of(p.read_text(encoding="utf-8")) if p.exists() else None


def zip_version(zip_path):
    with zipfile.ZipFile(zip_path) as z:
        name = next((n for n in z.namelist() if n.endswith("SKILL.md") and n.count("/") <= 1), None)
        return _version_of(z.read(name).decode("utf-8")) if name else None


def _copy(src, iv):
    if SKILL_DIR.exists():
        shutil.rmtree(SKILL_DIR)
    SKILL_DIR.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, SKILL_DIR, ignore=shutil.ignore_patterns(".git", "__pycache__", ".DS_Store"))
    return True, f"Įdiegta: {installed_version()} (buvo: {iv or 'nėra'})"


def install_from_repo():
    """git pull repo klone ir įdiegia reklama/. Grąžina (ar_pakeista, pranešimas)."""
    if not (REPO_DIR / ".git").exists():
        return False, (f"Repo klono nėra: {REPO_DIR}. Vieną kartą Terminale: "
                       "git clone https://github.com/rytiunia/ai_asistentas ~/ai_asistentas")
    r = subprocess.run(["git", "-C", str(REPO_DIR), "pull", "--ff-only"], capture_output=True, text=True)
    note = "" if r.returncode == 0 else f" (git pull nepavyko: {r.stderr.strip()[:200]} - naudojama turima kopija)"
    src = REPO_DIR / "reklama"
    if not (src / "SKILL.md").exists():
        return False, f"Repo'e nėra reklama/SKILL.md{note}"
    rv, iv = _version_of((src / "SKILL.md").read_text(encoding="utf-8")), installed_version()
    if rv and iv and rv == iv:
        return False, f"Jau įdiegta naujausia versija: {iv}{note}"
    ok, msg = _copy(src, iv)
    return ok, msg + note


def install(zip_path=None):
    """Be argumento - iš GitHub repo klono; su argumentu - iš zip. Grąžina (ar_pakeista, pranešimas)."""
    if not zip_path:
        return install_from_repo()
    zp = Path(zip_path)
    if not zp.exists():
        return False, f"Zip nerastas: {zp}"
    zv, iv = zip_version(zp), installed_version()
    if zv and iv and zv == iv:
        return False, f"Jau įdiegta naujausia versija: {iv}"
    with tempfile.TemporaryDirectory() as tmp:
        with zipfile.ZipFile(zp) as z:
            z.extractall(tmp)
        src = Path(tmp) / "reklama"
        if not (src / "SKILL.md").exists():
            cand = list(Path(tmp).rglob("SKILL.md"))
            if not cand:
                return False, "Zip'e nėra SKILL.md"
            src = cand[0].parent
        return _copy(src, iv)


if __name__ == "__main__":
    ok, msg = install(sys.argv[1] if len(sys.argv) > 1 else None)
    print(msg)
