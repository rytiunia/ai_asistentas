---
name: baldai
description: "Virtuvės korpusinių baldų parametrinis generatorius Ryčio baldininkams: iš sienos matmenų ir korpusų sekos (tekstas, eskizas ar lentelė) vienu paleidimu padaro 3D peržiūrą klientui su dekoro keitimu, priekinę projekciją su matmenimis ir pjovimo lapą Excel pjaustymo centrui (detalės, kantai, raštas, furnitūra, medžiagų suvestinė). Naudok VISADA, kai pokalbyje yra virtuvė, korpusai, spintelės, apatiniai / viršutiniai, fasadai, stalčiai, pjovimo lapas, detalių sąrašas, LMDP / HDF, kantavimas, Egger / Kronospan dekorai, konfigūratorius ar baldininkui reikia vaizdo klientui ir detalių skaičiavimo."
---

# Baldai – PALEIDIKLIS

Šis paskyros SKILL.md yra TIK paleidiklis. Tikrasis skill'as (SKILL.md, `scripts/`, `assets/`, `references/`) yra
VIENOJE vietoje – Ryčio iCloud:

`~/Library/Mobile Documents/com~apple~CloudDocs/AI_ASISTENTAS/baldai.zip`

Taip paskyroje ir iCloud visada ta pati, naujausia versija. Variklio (engine.py), standarto ar puslapio šablono iš
atminties neatkurti – be zip darbas nedaromas.

## Paleidimas (PRIEŠ bet kokį darbą)

1. **Pokalbis susietas su Ryčio kompiuteriu:** `device_stage_files` → zip aukščiau (jei aplankas `AI_ASISTENTAS`
   neprijungtas – `device_request_folder_access` jam). Išarchyvuoti į NAUJĄ tuščią darbo aplanką (scratchpad),
   perskaityti `baldai/SKILL.md` ir dirbti TIK pagal jį ir jo failus.
2. **Nesusietas / kompiuteris nepasiekiamas:** PRIEŠ darbą paprašyti Ryčio įkelti zip į pokalbį (arba susieti pokalbį
   su kompiuteriu).
3. Atsakyme nurodyti versiją iš zip SKILL.md „Versija" eilutės (pvz. „baldai v1, iCloud zip").
4. **Pakeitus skill'ą:** pakelti „Versija", senąjį zip → `AI_ASISTENTAS/_archyvas/baldai_vNN_YYYY-MM-DD.zip`, naują zip
   įrašyti į tą pačią vietą (`device_commit_files`). Šio paleidiklio NEKEISTI – jis visada paima naujausią zip.
   Failų vardai zip'e – tik ASCII.

Su Ryčiu kalbėti lietuviškai, tiesiai, be komplimentų.
