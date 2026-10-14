# Patvirtinimas -> gamybos paketas (v104, Rytis 2026-10-11)

Ryčio komanda: įkeliamas (kliento patvirtintas) dokumentas + žinutė **„Patvirtinta, ALT5432_10.12_RS"**.
Tada BE papildomų klausimų sukuriama:
1. **Gamybinis dokumentas** - tas pats lapas(-ai), ORDER NO. = ALT numeris (`spec "order_no"`), visi lapai į vieną PDF
   `<ALT>_<užsakymas>.pdf`;
2. **DXF 1:1** (`p6_dxf.py --no-letters`, su `--rails-json` - rėmas, ausėlės / hangers, D3.2, D11, drenažas) -
   TIK VIENTISI failai `<ALT>_<lapas>_P6_1-1_*.dxf` po vieną lapui (be failų po raidę, be ZIP, be patikros PNG);
3. **LED dėliojimo lapas** (v119: `led_km.py` - KM-P2; `led_sim.py` tik paprašius) - visi lapai į `<ALT>_..._LED.pdf`.

## ALT numerio normalizavimas
- Formatas `ALT<nr>_<MM.DD>_<inicialai>` (lapo šablonas `ALT0000_00.00_RS`).
- „ALT 8872_10.12" -> `ALT8872_10.12_RS` (tarpas šalinamas; be inicialų - `_RS`, Rytis). Failų prefiksas - tas pats.

## Eiga
1. Rasti projektą `scripts/projektai/<...>/` (README, spec). Spec kopija -> `order_no` = ALT.
2. **Kliento originalo nėra** (senas sesijos kelias) - šaltinis = PATVIRTINTAS mūsų lapas:
   `client_pdf` = įkeltas PDF, `"page"` = lapo nr. (nuo 0), `crop_pt` = FRONT VIEW sritis, `scale` = vaizdo mastelis,
   raidės `client_fill` [1,1,1] (balta), `rail_fills` = mūsų bėgelių spalva tame lape (pvz. RAL 8014 -> [0.29, 0.208, 0.149]),
   `ignore_fills` = [[0,0,0]]. DĖMESIO: ausėlių spalva (tamsesnė) +-0.05 ribose nuo bėgelių - į `ignore_fills` NEDĖTI
   (ignoruotų bėgelius); ausėlės ir taip < 30 mm - praleidžiamos.
3. `RAILS_JSON=rails_N.json braizyti_begeliai.py spec_N.json N.pdf` kiekvienam lapui. Palyginti su patvirtintu:
   perimetras / plotas, bėgelių ilgiai, ausėlių kiekis. Skirtumai dėl naujesnių taisyklių (5 mm apvalinimas, Letter back RAL)
   - leidžiami, PRANEŠTI Ryčiui sąraše.
4. `p6_dxf.py patvirtintas.pdf dxf --page N --scale S --crop ... --fill 1,1,1 --names ... --prefix <ALT>_<lapas>
   --rail <profilis> --cable top --rails-json rails_N.json` (ausėlių Ø baltos skylės < 20 mm praleidžiamos, v104).
5. `led_sim.py` spec: `pdf` = patvirtintas, `"page"`, `crop_pt`, `scale_mm_per_pt` = mastelis x 0.35278, `fill_rgb` [1,1,1],
   `order_no` = ALT; laidas iš raidės - `"feed_at": ["letter:<indeksas>-top"]` (v104).
6. Sujungti PDF, perkelti į outputs. **Siųsti TIK 3 rūšis (Rytis v105):** PDF su maketu, PDF su LED dėliojimu,
   vientisus DXF. `reklama.zip` NESIŲSTI - tik atnaujinti iCloud, jei skill'as keitėsi. Ataskaitoje: kas pakeista nuo patvirtinto, DXF perspėjimai
   (rankiniai taisymai), LED modulis / kiekis / W (LED į gamybinį lapą - tik Ryčiui patvirtinus modulį), PSU / trafo modelis.

Pirmas bandymas: Joker 226001 (`scripts/projektai/joker_reinslettveien/`, „Patvirtinta, ALT 8872_10.12").

## v109 (EXTRA 225978, ALT8873_10.12_RS, 2026-10-12)
- Mūsų lape bėgeliai / statmenys / ausėlės - `rail_fills` [0.796, 0.816, 0.8] (RAL 7035), ausėlės [0.677, 0.693, 0.68] ir
  jų skylės [1,1,1] - į `ignore_fills` (ausėlės nuo bėgelių > 0.05 - bėgelių neužkliudo). Platūs statmenų blokai
  (kojos „stem") rail spalvos - automatiškai ne raidės (v109).
- `one_frame` lapai su spec `verticals` - `"client_vert_rails": false` (statmenys generuojami iš spec, ne iš lapo).
- `client_frame: true` - rėmas kaip patvirtintame (be auto perdarymo); 6 m strypų taisyklė vis tiek taikoma - PRANEŠTI.
- v112: vieno rėmo lapai su plokšte (EXTRA X ant apskritimo) - `p6_dxf.py --plate-fill <apskritimo spalva> --fill
  "<raudona>;<geltona>"`, crop be šoninio vaizdo; P1 NON-LIT - `--cable none`, failas `<ALT>_<lapas>_P1_1-1.dxf`.
  DXF reikia VISIEMS gaminiams (Rytis: „nėra extra dxf failų, tik darbo laiko").
- LED kelioms spalvoms - `fill_rgb` sąrašas + `groups` / `feed_at` po grupę; P1 NON-LIT - LED lapo nėra.
- v111: kiekvienai šviečiančiai grupei spec `"led"` (galiniame vaizde užrašas, kokie LED) - be jo lapas negamybinis
  (braizyti_begeliai rašo perspėjimą).
- v112 EXTRA 225978: FAS700 `--page 2 --scale 20 --crop 125,100,715,225 --fill "0.784,0.063,0.18;1,0.761,0.055"
  --plate-fill 0.969,0.71,0 --names "EXTRA723-"`; FAS1000 P1 `--p1 --page 3 --scale 25 --crop 95,115,822,250 --fill
  "0.757,0.071,0.11" --plate-fill 0.969,0.71,0` (v116: P1 dugnas -0,7, be drenažo / D11).
- v113: DXF kontūrai tiesėmis + lankais (mažai mazgų) - nieko papildomai daryti nereikia.
- v119: LED dėliojimas - `led_km.py` (KM-P2 / KM-P2-R, žingsnis pagal gylį), NE `led_sim.py`.

- v120: `led_km.py` moduliai iš LED lentelės (raidėms P120 24V), lape LED imitacija.
- v127: LED moduliai / PSU / žingsnis - Kaisen (`assets/kaisen_led.json`, ryškumo lentelės, lx >= 2200), ne BaltLED / Lens.

## v153 - NEŠVIEČIANTYS gaminiai / pilonai (Thales D059422, ALT8878_10.13_RS, 2026-10-13)
- Patvirtinimas be inicialų ("ALT8878_10.13_") -> `ALT8878_10.13_RS`.
- Lapų skriptas su ORDER NO. iš aplinkos: `THALES_ORDER=<ALT> THALES_OUT=... python3 thales_pylons.py all`, sujungti -> `<ALT>_<projektas>.pdf`.
- DXF = GAMYBINĖS IŠKLOTINĖS (ne P6 raidės): `PREFIX=<ALT> THALES_OUT=... python3 thales_dxf.py` - skardos lovelės (v207: folded v173 - atlankas = gylis - t,
  šonai įsilenkia, Ø3.2 7 nuo krašto; sluoksniai CUT / BEND_UP_90 / HOLES_D3.2), flanšai, PMMA plokštė; failo vardas su kiekiu (`_x8`).
  Skylių Ø, kurių kliento lape nėra (csk / kniedės) - PRIELAIDA atskirame sluoksnyje, ataskaitoje paprašyti patvirtinti.
- LED lapo NĖRA (nešviečiantis) - ataskaitoje pasakyti.
