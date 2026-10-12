# Reklama - užsakymų programa (v0.1, 2026-10-11)

Kliento failas + aprašymas -> **reklama skill'as** (tas pats kaip pokalbyje) -> gamybiniai dokumentai (A3 lapas, 1:1 PDF, DXF, spec.json).
Viduje veikia Claude Agent SDK: agentas skaito skill'o taisykles, leidžia skill'o Python skriptus, žiūri PNG ir klausia, ko trūksta.

## Įdiegimas (Mac, vieną kartą)
1. Programa yra repo aplanke `reklama_app/`. Paleisk ją iš klono: `~/ai_asistentas/reklama_app/paleisti.command`.
2a. Vieną kartą Terminale: `git clone https://github.com/rytiunia/ai_asistentas ~/ai_asistentas`
    (repo privatus - GitHub paprašys prisijungti; paprasčiausia per `gh auth login` arba GitHub Desktop).
2. Turi būti Python 3.10+ (`python3 --version` Terminale; jei nėra - https://www.python.org/downloads/).
3. Dukart spustelk `paleisti.command`. Pirmą kartą įdiegia bibliotekas (2-5 min), įdiegia reklama skill'ą iš
   GitHub repo klono `~/ai_asistentas` (žr. 2a) ir atidaro programą naršyklėje (http://localhost:8501).
   - macOS neleidžia atidaryti? Dešinys pelės mygtukas -> Open, arba Terminale: `bash ~/reklama_app/paleisti.command`.
4. Šoninėje juostoje įvesk **Anthropic API raktą** (https://console.anthropic.com -> API Keys). Jis išsaugomas `.env`
   faile programos aplanke ir niekur nesiunčiamas, tik Anthropic.
5. Nebūtina: `brew install poppler` (pdftoppm PNG patikrai; be jo naudojamas pymupdf).

## Naudojimas
- **Naujas užsakymas**: failai, užsakovas, order pavadinimas, aprašymas santrumpomis -> „Pradėti". Įmonės kodą (RK-YYMM-NNN) išduoda programa.
- Agentas atsako pokalbyje: ką rado, ko trūksta (klausimai), kokie failai paruošti. Atsakai apačioje - jis tęsia tą patį darbą.
- **Rezultatai** skirtuke: failai atsisiuntimui ir PDF peržiūra. Visi failai taip pat `jobs/<kodas>/out/`.
- Seni užsakymai - šoninėje juostoje, galima tęsti bet kada.

## Skill'o atnaujinimas
Vienas šaltinis - GitHub repo `rytiunia/ai_asistentas`. Atnaujinus skill'ą pokalbyje - programoje spausk „Atnaujinti skill'ą iš GitHub"
(arba tiesiog paleisk programą iš naujo - `paleisti.command` patikrina versiją pats).

## Kaina
Mokama pagal Anthropic API naudojimą (atskirai nuo Claude prenumeratos). Bandymas (P6 „TESTAS", lapas + 1:1 PDF):
1-as žingsnis ~1,95 USD / 8 min, pataisymas ~2,26 USD / 30 s. Viršuje rodoma užsakymo kaina iki šiol,
šoninėje juostoje - biudžeto riba vienam žingsniui (numatyta 5 USD).

## Saugumas
Agentas turi teisę leisti komandas kompiuteryje (Python skriptus) - kaip Claude Code. Jam nurodyta dirbti tik užsakymo
aplanke ir skill'o failų nekeisti. Nenaudok programos su failais, kuriais nepasitiki.

## Failai
- `app.py` - langas (Streamlit)
- `agentas.py` - agento paleidimas, užsakymų aplankai, instrukcijos agentui
- `skill_setup.py` - skill'o diegimas iš GitHub repo klono (arba iš zip)
- `.claude/skills/reklama/` - įdiegtas skill'as (sukuriamas automatiškai)
- `jobs/` - užsakymai
