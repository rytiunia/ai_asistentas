# SPAR / BrandFactory - kliento taisyklės

Raktažodžiai: SPAR, BrandFactory (užsakovas), KAFFEPAUSE, Ottersøy, TYPE 670. Etalonas - SPAR order 225960:
PRIVALOMA `references/etalonas_spar_225960.md`, lapai `assets/etalonai/SPAR_225960_komplektas_18_lapu.pdf`,
kodas `scripts/projektai/spar_225960/`; folded iš kelių dalių - `scripts/projektai/spar_type670/`.
BrandFactory yra užsakovas ir kitiems klientams (EXTRA, Clas Ohlson) - tada žiūrėti to kliento failą.

## Trumpai (perkelta iš SKILL.md v42)
- Šriftai: pagr. matmenys 12 pt, visa kita >= 8 pt, pavadinimai 13 / mastelis 9; < 8 pt NEMAŽINTI - trumpinti
  tekstą („! NETELPA"); patikra `scripts/patikra_sriftai.py`. Juostos eilutė 11 pt. (galioja visiems)
- BOM: RAL ir plėvelių kodų langeliai SPALVOTI (`lapas_core.FOIL`); kiekviena pozicija - balionas bendrame brėžinyje. (visiems)
- SPAR laidas - raudona stora linija, 12V 3 m, prie trafo box tik „220V"; išvestis bėgelio gale kliento nurodytoje
  pusėje; trasa aplink gaminį, nesutampa su matmenų linijomis (`cable.out`, `cable: false`, `joints`).
- SPAR ausėlės - tik kur kliento faile (`ears_pt`, `ears: false`); bėgelių galai už raidžių ir apskritimo
  (`rail_start_in`, styga - 30 mm); 2 dalių rėmas - FRAME JOINT.
- Ilgesnės nei medžiaga plokštės / plexi (back plate, portalo viršus) - iš 2 dalių su jungties detale prie vietos
  (bendra taisyklė - SKILL.md „Folded plate" -> „Kelios dalys vienoje plokštumoje").
- Ne iškabų lapai - tas pats stilius (`scripts/projektai/spar_225960/lib/flat.py`); dekoras be fono.
- Projekto pavadinimas = užsakymas („SPAR order 225960"), failas `Drawing_<projektas>.pdf` užsakymo aplanke NAS.
- Ottersøy (v12): SPAR 2 dalys - tik horizontalūs bėgeliai, jungtis tarp A ir R; laido išvestis `cable.rail: "top"`;
  PANT - vientisa reklama ant vieno rėmo, apskritimas - balta plexi + pjaustyta plėvelė; back plate 1 arba 2 dalys.
- KAFFEPAUSE kompozitas = apskritimas + rėmo atkartojimas (`logo_replica`).
- TYPE 670 (v28): folded iš 2 dalių (1500 + 2100), atskiri padėklai, kiekvienas su savo L; laidas per Ø11 kairėje
  briaunoje (`assets/spec_folded_2parts.json`).
- SPAR order 226004 Sundvollen (2026-10-09): åpningstider VH400 / VH500 P6_8mm + Day/Night perforuota plėvelė (black
  Gel'UV print), gylis 80, šonai RAL 9016, rėmas U30 RAL 8011 + ausėlės (kliento kvadratėliai), laidas 220V 1.5 m
  (PSU iškaboje, be trafo box); back plate 2700 x 2100 + spauda, standartinė sandūra 1400 + 700; VH500 - 8 ausėlės.
  `scripts/projektai/spar_226004/`.
- SPAR back plate STANDARTAS (Rytis 2026-10-09): 2700 x 2100 (ir 2000 x 2100), 2 dalys 1400 (viršus) + 700 (apačia) -
  nepriklausomai nuo grafikos.


## (iš SKILL.md v84) SPAR / BrandFactory -> `references/klientai/spar_brandfactory.md`
Lapo stiliaus taisyklės iš SPAR etalono (šriftai, BOM spalvoti langeliai, balionai, laido linija, failo vardas) galioja
VISIEMS - `references/etalonas_spar_225960.md`. SPAR specifika (ausėlės tik kliento vietose, 12V 3 m, 2 dalių rėmas,
projekto pavadinimas) - kliento faile.

