---
name: baldai
description: "Virtuvės korpusinių baldų parametrinis generatorius Ryčio baldininkams: iš sienos matmenų ir korpusų sekos (tekstas, eskizas ar lentelė) vienu paleidimu padaro 3D peržiūrą klientui su dekoro keitimu, priekinę projekciją su matmenimis ir pjovimo lapą Excel pjaustymo centrui (detalės, kantai, raštas, furnitūra, medžiagų suvestinė). Naudok VISADA, kai pokalbyje yra virtuvė, korpusai, spintelės, apatiniai / viršutiniai, fasadai, stalčiai, pjovimo lapas, detalių sąrašas, LMDP / HDF, kantavimas, Egger / Kronospan dekorai, konfigūratorius ar baldininkui reikia vaizdo klientui ir detalių skaičiavimo."
---

# Baldai - PALEIDIKLIS

Šis paskyros SKILL.md yra TIK paleidiklis. Tikrasis skill'as (SKILL.md, `scripts/`, `assets/`, `references/`) yra
VIENOJE vietoje - Ryčio privačiame GitHub repo **`rytiunia/ai_asistentas`**, aplanke `baldai/`
(https://github.com/rytiunia/ai_asistentas). iCloud zip'ai nebenaudojami (archyvuoti 2026-10-12).

## Paleidimas (PRIEŠ bet kokį darbą)

1. `add_repo` (owner `rytiunia`, repo `ai_asistentas`, access `push`), tada
   `git clone --depth 1 https://github.com/rytiunia/ai_asistentas <darbo_aplankas>/ai_asistentas`
   (jei klonas jau yra - `git pull --ff-only`). Perskaityti `ai_asistentas/baldai/SKILL.md` ir dirbti TIK pagal jį ir
   jo failus. Kompiuterio (Mac) tam nereikia.
2. **Repo nepasiekiamas** (nėra `add_repo`, GitHub neprijungtas): PRIEŠ darbą pasakyti Ryčiui ir paprašyti prijungti
   GitHub (claude.ai -> Settings -> Connectors) arba įkelti `baldai` aplanką zip'u į pokalbį. Be skill'o failų darbo
   nedaryti ir taisyklių neatkurti iš atminties.
3. Atsakyme VISADA nurodyti versiją iš `baldai/SKILL.md` „Versija" eilutės ir trumpą commit'o hash (pvz. „baldai vNN, GitHub abc1234").
4. **Pakeitus skill'ą:** pakelti „Versija", commit'inti į `main` su žinute „baldai vNN: ką pakeitė" ir `git push`
   (prieš push - `git pull --rebase`). Zip'ų ir archyvo nebereikia - istoriją saugo git. Šio paleidiklio NEKEISTI,
   nebent keičiasi repo vieta. Failų vardai - tik ASCII.

Su Ryčiu kalbėti lietuviškai, tiesiai, be komplimentų.
