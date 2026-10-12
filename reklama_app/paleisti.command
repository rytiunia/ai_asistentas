#!/bin/bash
# Dukart spustelk Finder'yje. Pirmą kartą įdiegia viską (~2-5 min), vėliau tik paleidžia.
cd "$(dirname "$0")" || exit 1

if ! command -v python3 >/dev/null 2>&1; then
  echo "Nerastas python3. Įdiek iš https://www.python.org/downloads/ ir paleisk dar kartą."
  read -r -p "Enter - uždaryti"; exit 1
fi

if [ ! -d .venv ]; then
  echo "Kuriama Python aplinka..."
  python3 -m venv .venv || { read -r -p "Klaida. Enter - uždaryti"; exit 1; }
  ./.venv/bin/pip install --upgrade pip -q
  ./.venv/bin/pip install -r requirements.txt || { read -r -p "Klaida diegiant. Enter - uždaryti"; exit 1; }
fi

# reklama skill'as iš iCloud (įdiegia tik jei versija pasikeitė)
./.venv/bin/python skill_setup.py

if ! command -v pdftoppm >/dev/null 2>&1; then
  echo "(pdftoppm nėra - PNG patikrai bus naudojamas pymupdf; jei nori: brew install poppler)"
fi

./.venv/bin/streamlit run app.py --server.headless false --browser.gatherUsageStats false
