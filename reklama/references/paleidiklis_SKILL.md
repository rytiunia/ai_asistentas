---
name: reklama
description: Rytio iškabų gamybos techninė dokumentacija - iš kliento PDF/DXF ir trumpo aprašymo (pvz. "P6 ant folded pl., 40mm, RAL9010") sugeneruoja A3 techninį lapą etaloniniu CAD stiliumi ir patikrina gamybos tinkamumą; LED (Lens) dėliojimas. Naudok VISADA, kai pokalbyje yra iškaba, tūrinės/šviečiančios raidės, profilis (P6), folded pl., pylonas, šviesdėžė, RAL, tvirtinimas, LED, D3.2/D11, arba įkeliamas kliento logotipo ar iškabos PDF ir prašoma brėžinio, matmenų, specifikacijos ar pasiūlymo.
---

# Iškabų techninis lapas - PALEIDIKLIS

Šis paskyros SKILL.md yra TIK paleidiklis. Tikrasis skill'as (SKILL.md, `scripts/`, `assets/`, `references/`) yra
VIENOJE vietoje - Ryčio privačiame GitHub repo **`rytiunia/ai_asistentas`**, aplanke `reklama/`
(https://github.com/rytiunia/ai_asistentas). iCloud zip'ai nebenaudojami (archyvuoti 2026-10-12).

## Paleidimas (PRIEŠ bet kokį darbą)

1. `add_repo` (owner `rytiunia`, repo `ai_asistentas`, access `push`), tada
   `git clone --depth 1 https://github.com/rytiunia/ai_asistentas <darbo_aplankas>/ai_asistentas`
   (jei klonas jau yra - `git pull --ff-only`). Perskaityti `ai_asistentas/reklama/SKILL.md` ir dirbti TIK pagal jį ir
   jo failus. Kompiuterio (Mac) tam nereikia.
2. **Repo nepasiekiamas** (nėra `add_repo`, GitHub neprijungtas): PRIEŠ darbą pasakyti Ryčiui ir paprašyti prijungti
   GitHub (claude.ai -> Settings -> Connectors) arba įkelti `reklama` aplanką zip'u į pokalbį. Be skill'o failų darbo
   nedaryti ir taisyklių neatkurti iš atminties.
3. Atsakyme VISADA nurodyti versiją iš `reklama/SKILL.md` „Versija" eilutės ir trumpą commit'o hash (pvz. „reklama vNN, GitHub abc1234").
4. **Pakeitus skill'ą:** pakelti „Versija", commit'inti į `main` su žinute „reklama vNN: ką pakeitė" ir `git push`
   (prieš push - `git pull --rebase`). Zip'ų ir archyvo nebereikia - istoriją saugo git. Šio paleidiklio NEKEISTI,
   nebent keičiasi repo vieta. Failų vardai - tik ASCII.

Su Ryčiu kalbėti lietuviškai, tiesiai, be komplimentų.
