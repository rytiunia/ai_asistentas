"""reklama skill'o diegimas į programą iš iCloud zip (vienas šaltinis).

python skill_setup.py [kelias/iki/reklama.zip]
"""
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
SKILL_DIR = APP_DIR / ".claude" / "skills" / "reklama"
ICLOUD_ZIP = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/AI_ASISTENTAS/reklama.zip"


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


def install(zip_path=None):
    """Grąžina (ar_pakeista, pranešimas)."""
    zp = Path(zip_path) if zip_path else ICLOUD_ZIP
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
        if SKILL_DIR.exists():
            shutil.rmtree(SKILL_DIR)
        SKILL_DIR.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src, SKILL_DIR)
    return True, f"Įdiegta: {installed_version()} (buvo: {iv or 'nėra'})"


if __name__ == "__main__":
    ok, msg = install(sys.argv[1] if len(sys.argv) > 1 else None)
    print(msg)
