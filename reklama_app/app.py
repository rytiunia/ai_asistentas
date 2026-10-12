"""Iškabų užsakymų programa: kliento failas -> reklama skill'as (Claude Agent SDK) -> gamybiniai dokumentai.

Paleidimas: streamlit run app.py
"""
import os
from pathlib import Path

import streamlit as st

import agentas as ag
import skill_setup as ss

st.set_page_config(page_title="Reklama - užsakymai", page_icon="📐", layout="wide")

ENV_FILE = ag.APP_DIR / ".env"


def read_key():
    if os.environ.get("ANTHROPIC_API_KEY"):
        return os.environ["ANTHROPIC_API_KEY"]
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            if line.startswith("ANTHROPIC_API_KEY="):
                return line.split("=", 1)[1].strip()
    return ""


# ---------- šoninė juosta ----------
with st.sidebar:
    st.header("Nustatymai")
    ver = ss.installed_version()
    if ver:
        st.caption(f"reklama skill'as: **{ver}**")
    else:
        st.error("reklama skill'as neįdiegtas")
    if st.button("Atnaujinti skill'ą iš GitHub"):
        ok, msg = ss.install()
        (st.success if ok else st.info)(msg)
    up_zip = st.file_uploader("arba įkelk reklama.zip", type=["zip"], key="zipup")
    if up_zip is not None and st.button("Įdiegti įkeltą zip"):
        tmp = ag.APP_DIR / "_upload_reklama.zip"
        tmp.write_bytes(up_zip.getvalue())
        ok, msg = ss.install(tmp)
        tmp.unlink(missing_ok=True)
        (st.success if ok else st.info)(msg)

    st.divider()
    key = read_key()
    if key:
        st.caption("API raktas: nustatytas")
    else:
        st.warning("API raktas nenustatytas")
        new_key = st.text_input("Anthropic API raktas", type="password")
        if new_key and st.button("Išsaugoti raktą (.env)"):
            ENV_FILE.write_text(f"ANTHROPIC_API_KEY={new_key.strip()}\n")
            st.rerun()
    model = st.selectbox("Modelis", ["(numatytas)", "claude-opus-5-5", "claude-sonnet-5-5"], index=0)
    budget = st.number_input("Biudžetas vienam žingsniui, USD", min_value=0.5, max_value=50.0, value=5.0, step=0.5)

    st.divider()
    st.subheader("Užsakymai")
    if st.button("+ Naujas užsakymas", use_container_width=True):
        st.session_state.pop("code", None)
        st.rerun()
    for j in ag.list_jobs()[:30]:
        label = f"{j['code']} · {j['client'] or '?'} · {j['order'] or ''}"[:48]
        if st.button(label, key="job_" + j["code"], use_container_width=True):
            st.session_state["code"] = j["code"]
            st.rerun()

OPTS = {"api_key": read_key() or None, "model": None if model.startswith("(") else model, "budget": budget}


def run_with_progress(job, text):
    """Agento žingsnis su eigos rodymu."""
    with st.status("Agentas dirba…", expanded=True) as stt:
        log = st.empty()
        lines = []

        def on_event(kind, val):
            if kind in ("tool", "init"):
                lines.append("• " + val)
                log.markdown("\n".join(lines[-14:]))

        ans = ag.run_turn(job, text, OPTS, on_event)
        stt.update(label="Baigta" if not ans.startswith(("Agento klaida", "Klaida")) else "Klaida",
                   state="complete" if not ans.startswith(("Agento klaida", "Klaida")) else "error", expanded=False)
    return ans


# ---------- naujas užsakymas ----------
code = st.session_state.get("code")
if not code:
    st.title("Naujas užsakymas")
    st.caption("Įkelk kliento failą ir trumpą aprašymą. Ko trūks, agentas paklaus pokalbyje.")
    with st.form("new"):
        files = st.file_uploader("Kliento failai (PDF, DXF, AI, paveikslėliai)", accept_multiple_files=True)
        c1, c2, c3 = st.columns(3)
        client = c1.text_input("Užsakovas", placeholder="pvz. BrandFactory")
        order = c2.text_input("Order pavadinimas", placeholder="pvz. SPAR Sundvollen 226004")
        c3.text_input("Įmonės kodas", value="išduodamas automatiškai", disabled=True)
        desc = st.text_area("Aprašymas (santrumpos kaip įprastai)", height=110,
                            placeholder="pvz. P6_3mm color, gylis 100, U30, šonai RAL 9005, siena plytos")
        go = st.form_submit_button("Pradėti", type="primary")
    if go:
        if not ss.installed_version():
            st.error("Pirmiausia įdiek reklama skill'ą (šoninė juosta).")
            st.stop()
        if not files and not desc.strip():
            st.error("Įkelk failą arba parašyk aprašymą.")
            st.stop()
        if not client.strip() or not order.strip():
            st.info("Užsakovas ar orderis tuščias - agentas pabandys rasti faile, kitaip paklaus.")
        job = ag.create_job(client.strip(), order.strip(), desc.strip(), [(f.name, f.getvalue()) for f in files or []])
        st.session_state["code"] = job["code"]
        run_with_progress(job, ag.first_prompt(job))
        st.rerun()
    st.stop()

# ---------- esamas užsakymas ----------
job = ag.load_job(code)
if not job:
    st.session_state.pop("code", None)
    st.rerun()

d = ag.job_dir(code)
h1, h2 = st.columns([3, 1])
with h1:
    st.title(job["order"] or code)
    st.caption(f"{code} · užsakovas: {job['client'] or '?'} · sukurta {job['created']} · "
               f"failai: {', '.join(job['files']) or '-'}")
with h2:
    st.metric("Kaina iki šiol", f"${job.get('cost_usd', 0):.2f}")

outs_n = len([p for p in (d / "out").glob("*") if p.is_file()]) if (d / "out").exists() else 0
left, right = st.tabs(["Pokalbis", f"Rezultatai ({outs_n})"])

with left:
    for i, m in enumerate(job["history"]):
        if i == 0 and m["role"] == "user":
            with st.chat_message("user"):
                st.markdown("**Užsakymas pateiktas**")
                if job["description"]:
                    st.markdown(job["description"])
            continue
        with st.chat_message("user" if m["role"] == "user" else "assistant"):
            st.markdown(m["text"])

with right:
    outs = sorted((d / "out").glob("*")) if (d / "out").exists() else []
    if not outs:
        st.caption("Kol kas failų nėra.")
    for p in outs:
        if p.is_dir():
            continue
        c1, c2 = st.columns([4, 1])
        c1.markdown(f"`{p.name}` · {p.stat().st_size // 1024} KB")
        c2.download_button("⬇", p.read_bytes(), file_name=p.name, key="dl_" + p.name)
    pngs = [p for p in outs if p.suffix.lower() == ".png"]
    pdfs = [p for p in outs if p.suffix.lower() == ".pdf"]
    if pdfs:
        sel = st.selectbox("Peržiūra", [p.name for p in pdfs])
        try:
            import fitz  # pymupdf
            doc = fitz.open(d / "out" / sel)
            for pg in doc:
                st.image(pg.get_pixmap(dpi=70).tobytes("png"), use_container_width=True)
        except Exception as e:
            st.caption(f"Peržiūra nepavyko: {e}")
    elif pngs:
        for p in pngs[:4]:
            st.image(str(p), caption=p.name, use_container_width=True)
    with st.expander("Pridėti failą prie užsakymo"):
        more = st.file_uploader("Failas", key="more", accept_multiple_files=True)
        if more and st.button("Įkelti"):
            for f in more:
                (d / "inputs" / f.name).write_bytes(f.getvalue())
                job["files"].append(f.name)
            ag.save_job(job)
            st.rerun()

msg = st.chat_input("Atsakyk į klausimus arba paprašyk pataisymų…")
if msg:
    with left:
        with st.chat_message("user"):
            st.markdown(msg)
        run_with_progress(job, msg)
    st.rerun()
