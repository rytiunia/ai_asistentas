"""Agento paleidimas su reklama skill'u (Claude Agent SDK).

Vienas užsakymas = vienas darbo aplankas jobs/<kodas>/:
  inputs/   - kliento failai
  out/      - rezultatai (PDF, DXF, PNG, spec.json)
  job.json  - antraštė, pokalbis, session_id, kaina
"""
import asyncio
import json
import os
import sys
import time
from pathlib import Path

from claude_agent_sdk import (
    AssistantMessage, ClaudeAgentOptions, ResultMessage, SystemMessage,
    TextBlock, ToolUseBlock, query,
)

APP_DIR = Path(__file__).resolve().parent
JOBS = APP_DIR / "jobs"
SKILL_DIR = APP_DIR / ".claude" / "skills" / "reklama"


# ---------- darbai ----------
def new_code():
    JOBS.mkdir(exist_ok=True)
    seq_f = JOBS / "seq.txt"
    n = int(seq_f.read_text().strip() or 0) + 1 if seq_f.exists() else 1
    seq_f.write_text(str(n))
    return time.strftime("RK-%y%m-") + f"{n:03d}"


def job_dir(code):
    return JOBS / code


def load_job(code):
    p = job_dir(code) / "job.json"
    return json.loads(p.read_text()) if p.exists() else None


def save_job(job):
    d = job_dir(job["code"])
    d.mkdir(parents=True, exist_ok=True)
    (d / "job.json").write_text(json.dumps(job, ensure_ascii=False, indent=2))


def list_jobs():
    if not JOBS.exists():
        return []
    out = []
    for d in sorted(JOBS.iterdir(), reverse=True):
        j = load_job(d.name) if d.is_dir() else None
        if j:
            out.append(j)
    return out


def create_job(client, order, description, files):
    """files: [(vardas, bytes)]"""
    code = new_code()
    d = job_dir(code)
    (d / "inputs").mkdir(parents=True, exist_ok=True)
    (d / "out").mkdir(exist_ok=True)
    names = []
    for name, data in files:
        safe = "".join(c if c.isalnum() or c in "._-" else "_" for c in name)
        (d / "inputs" / safe).write_bytes(data)
        names.append(safe)
    job = {"code": code, "client": client, "order": order, "description": description,
           "files": names, "created": time.strftime("%Y-%m-%d %H:%M"),
           "session_id": None, "history": [], "cost_usd": 0.0}
    save_job(job)
    return job


def skill_version():
    p = SKILL_DIR / "SKILL.md"
    if not p.exists():
        return None
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.startswith("**Versija:"):
            return line.split("**")[1].replace("Versija:", "").strip()
    return "?"


# ---------- instrukcijos agentui ----------
def system_append(job):
    d = job_dir(job["code"])
    return f"""
TU DIRBI RYČIO IŠKABŲ GAMYBOS PROGRAMOJE (ne pokalbyje claude.ai).
- Darbui VISADA naudok skill'ą `reklama`. Jis jau išpakuotas: {SKILL_DIR} (versija {skill_version()}).
  Tai ir yra šaltinis: iCloud zip, paskyros skill'o ir device_* įrankių NETIKRINK ir nenaudok. Skill'o failų NEKEISK.
  Skriptai: {SKILL_DIR}/scripts, assets: {SKILL_DIR}/assets, taisyklės: {SKILL_DIR}/references.
- Darbo aplankas (cwd): {d}
  Kliento failai: {d}/inputs . VISUS rezultatus (lapų PDF, 1:1 PDF, DXF, patikros PNG, spec.json) rašyk į {d}/out
  (vietoj /mnt/user-data/outputs). Tarpinius failus - į {d}/tmp.
- Python: `{sys.executable}` (bibliotekos įdiegtos; nieko nediek be būtinybės).
  PNG patikrai: `pdftoppm`, jei jo nėra - pymupdf (fitz) `page.get_pixmap(dpi=80).save(...)`.
- Užsakymo antraštė lapui (title block): užsakovas „{job['client']}", orderis „{job['order']}", įmonės kodas {job['code']}.
- Rytis mato tik tavo tekstą ir failus out/ aplanke. Kalbėk lietuviškai, tiesiai.
- Jei trūksta informacijos - NIEKO NEIŠGALVOK: užduok tikslius klausimus sąrašu ir sustok, lauk atsakymo.
- Kiekvieno atsakymo pabaigoje trumpai: kas padaryta, kokie failai out/, kas lieka neaišku.
"""


def first_prompt(job):
    files = "\n".join(f"- inputs/{n}" for n in job["files"]) or "- (failų nėra)"
    return (f"Naujas užsakymas {job['code']}.\nUžsakovas: {job['client']}\nOrderis: {job['order']}\n"
            f"Kliento failai:\n{files}\n\nAprašymas:\n{job['description'] or '(nėra)'}\n\n"
            "Išanalizuok pagal reklama skill'ą. Jei informacijos pakanka - paruošk gamybinius dokumentus į out/. "
            "Jei ne - pirmiausia paklausk, ko trūksta.")


# ---------- vienas pokalbio žingsnis ----------
def _tool_label(b: ToolUseBlock):
    i = b.input or {}
    if b.name == "Bash":
        return "Vykdo: " + (i.get("description") or i.get("command", "")[:90])
    if b.name in ("Read", "Write", "Edit"):
        word = {"Read": "Skaito", "Write": "Rašo", "Edit": "Taiso"}[b.name]
        return f"{word}: {Path(i.get('file_path', '')).name}"
    if b.name == "Skill":
        return "Įkelia skill'ą: " + str(i.get("skill", ""))
    return b.name


async def _run(job, prompt, opts_extra, on_event):
    d = job_dir(job["code"])
    (d / "tmp").mkdir(exist_ok=True)
    env = {}
    if opts_extra.get("api_key"):
        env["ANTHROPIC_API_KEY"] = opts_extra["api_key"]
    opts = ClaudeAgentOptions(
        cwd=str(d),
        add_dirs=[str(APP_DIR)],
        setting_sources=["project"],
        skills=["reklama"],
        allowed_tools=["Skill", "Read", "Write", "Edit", "Bash", "Glob", "Grep"],
        permission_mode="acceptEdits",
        system_prompt={"type": "preset", "preset": "claude_code", "append": system_append(job)},
        resume=job.get("session_id"),
        model=opts_extra.get("model") or None,
        max_budget_usd=opts_extra.get("budget") or None,
        env=env,
    )
    texts, result = [], None
    async for m in query(prompt=prompt, options=opts):
        if isinstance(m, SystemMessage) and m.subtype == "init":
            sk = m.data.get("skills") or []
            on_event("init", "reklama skill'as įkeltas" if "reklama" in sk else "! reklama skill'as NERASTAS")
        elif isinstance(m, AssistantMessage):
            for b in m.content:
                if isinstance(b, ToolUseBlock):
                    on_event("tool", _tool_label(b))
                elif isinstance(b, TextBlock) and b.text.strip():
                    texts.append(b.text)
                    on_event("text", b.text)
        elif isinstance(m, ResultMessage):
            result = m
    return texts, result


def run_turn(job, user_text, opts_extra, on_event=lambda k, v: None):
    """Paleidžia vieną žingsnį, atnaujina job (history, session_id, cost) ir grąžina atsakymo tekstą."""
    job["history"].append({"role": "user", "text": user_text, "t": time.strftime("%H:%M")})
    save_job(job)
    try:
        texts, res = asyncio.run(_run(job, user_text, opts_extra, on_event))
    except Exception as e:  # CLI / tinklo / rakto klaidos
        msg = f"Agento klaida: {type(e).__name__}: {e}"
        job["history"].append({"role": "assistant", "text": msg, "error": True})
        save_job(job)
        return msg
    if res is not None:
        job["session_id"] = res.session_id or job.get("session_id")
        job["cost_usd"] = round(job.get("cost_usd", 0) + (res.total_cost_usd or 0), 4)
    answer = (res.result if res is not None and res.result else "\n\n".join(texts[-1:])) or "(be teksto)"
    if res is not None and res.is_error:
        answer = f"Klaida ({res.subtype}): {answer}"
    job["history"].append({"role": "assistant", "text": answer, "t": time.strftime("%H:%M"),
                           "cost": res.total_cost_usd if res else None})
    save_job(job)
    return answer
