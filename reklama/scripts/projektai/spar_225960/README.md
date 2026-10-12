# SPAR order 225960 - kodas, kuriuo sugeneruotas etaloninis komplektas (18 lapų)

Taisyklės: `references/etalonas_spar_225960.md`. Rezultatas: `assets/etalonai/SPAR_225960_komplektas_18_lapu.pdf`.
Naudoti kaip PAGRINDĄ naujam kelių pozicijų užsakymui: nukopijuoti į darbinį aplanką, pakeisti kelius ir pozicijas.

## Eiga
1. `lib/prep.py` - kliento PDF valymas (antraštės / tekstai pašalinami) -> `t/clean_pN.pdf` (po puslapį).
2. `lib/mkclient2.py` (`make`) - kliento grafika skriptui: raidžių grupės pagal x (`splits`, `split_cols`),
   bėgeliai pilki, logotipo plėvelė (`logo_foil`), kompozitas + rėmo atkartojimas (`logo_replica`).
3. `build_rails.py` - raidės ant bėgelių (lapai 1-5, 15-17): `run(key, sheet, title, scale, view, src, groups, rail,
   cables, md, bom, ...)` -> `sk9/<key>.json` -> `scripts/braizyti_begeliai.py`. Pagalbinės: `letters_mm`,
   `rails_y_mm`, `rail_start_in` (bėgelio pradžia pagal pirmos raidės kontūrą), BOM šablonai `U30`, `SQ40`, `UTOP`.
4. `lib/flat_sheets.py` (`python3 flat_sheets.py`) - ne iškabų lapai (6-14): `portal`, `backplate`, `print_sheet`,
   `foil_sheet`, `decor`, `sandprint`; bendras karkasas `lib/flat.py` (`begin`, `band`, `finish`, `material_block`,
   `section_backplate`, `iso_box`, `draw_client`).
5. Folded (18): `spec/frisk.json` -> `scripts/braizyti_lapa.py`.
6. Sujungimas (pymupdf `insert_pdf` eilės tvarka), `lapas_core.pdf_fix_fonts(<komplektas>)` (CorelDRAW tekstas),
   patikra `scripts/patikra_sriftai.py`, įrašymas į NAS; .cdr - CorelDRAW: atidaryti PDF (Text) -> Save As.

## Keisti prieš naudojant
- Keliai `/home/claude/w/...`, `/home/claude/v9/scripts` -> darbinis aplankas / išarchyvuoto skill'o `scripts/`.
- `CLIENT`, projekto pavadinimas (`drawing_no`, TITLE prefiksas) `lib/flat.py` ir `build_rails.py`.
- Kliento pt koordinatės (`view`, `ears_pt`, `x_pt`, `clip`) - pagal naują kliento PDF.
