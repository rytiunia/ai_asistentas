# LED Lens moduliai - TIEKĖJO DUOMENYS (Rytis 2026-10-08)

Tik tiekėjo gido ir Ryčio pateikti faktai. Išdėstymo algoritmas - atskirai (perrašomas nuo 0).

Šaltinis: „Dėliojimo Gidas Lens moduliams.pdf" (`assets/led_lens_gidas.pdf`) + Rycio taisyklės. Duomenys - `assets/led_lens.json`. Skaičių neišgalvoti: ko nėra lentelėje ar čia - klausti Ryčio.

## Moduliai

| Kodas | Pavadinimas | LED | W/vnt. | lm/vnt. | Grandinė, maitinant iš 1 galo | iš 2 galų | Max atstumas tarp centrų | Valdikliai | Matmenys mm |
|---|---|---|---|---|---|---|---|---|---|
| P65L | PRO65Lens | 1 | 0,5 W | 65 lm | 50 vnt. | 100-120 vnt. | 100 mm | NE | 31 x 18,8 x 7,4 |
| P130L | PRO130Lens | 2 | 1 W | 128 lm | 40 vnt. | 80-100 vnt. | 200 mm | TAIP | 53 x 18,8 x 7,4 |
| P190L | PRO190Lens | 3 | 1,5 W | 190 lm | 30 vnt. | 60-70 vnt. | 270 mm | TAIP | 75 x 18,8 x 7,4 |

## Dvi pagrindinės taisyklės

1. **Valdikliai (P130L, P190L) - ilgesnės grandinės, mažiau maitinimo pravedimų.**
   1,5-2 kartus ilgesnės grandinės gale ryškumas krenta tik ~7 % (Kaizen Prisma ~15 %, Laitema E serija ~18 %).
   Tokie kritimai kitose sistemose verčia montuotojus daryti papildomus maitinimo pravedimus vienodai įtampai ir
   ryškumui išlaikyti. Valdikliai toleruoja ~2-2,5 V kritimą: nuo 12 V iki 10 V prarandama tik iki 3 % ryškumo
   (ypač aktualu po montavimo) -> mažiau maitinimų, plonesni laidai. **P65L valdiklių NETURI** - jam šis
   pranašumas negalioja, grandinės ribos (50 / 100-120) laikytis griežtai.

2. **Platus lęšis - nestandartinis naudojimas (mažesni gyliai, didesni žingsniai):**
   - **0,5W P65L** iššviečia jau **30 mm** gylį (lentelė: 70 mm tarp centrų prie 45 % plexi, 80 mm prie 30 %);
     nuo **40 mm** - montuojama per pilną (ištiestą) **100 mm** laidą.
   - **1W P130L** - raidėse nuo **50 mm**, dėliojant **kas 120 mm**, viena eile, gaunamas aukštas ryškumas
     (gide: plačiose raidėse 2000-3000 lx). Modulių 2-4 kartus mažiau nei su siauresnio kampo 1LED moduliais.
   - **1,5W P190L** - nuo **80 mm**, montuojant **kas 200 mm** (anksčiau 3LED 1,5W moduliai buvo
     rekomenduojami tik nuo 120 mm).

## Ryškumo lentelės (gylis -> atstumas tarp centrų / lx)

Testas 4 x 4 kvadratu (16 modulių), vienodas atstumas tarp modulių ir eilių. Dėliojant 1-2 eilėmis
ryškumas gali skirtis. Plexi pralaidumas 45 % / 30 %.

**P65L (0,5 W)**
| Gylis | 30 mm | 40 mm | 50 mm | 60 mm | 70 mm |
|---|---|---|---|---|---|
| 45 % | 70 mm / 5600 lx | 100 / 3000 | 100 / 2850 | 100 / 2750 | 100 / 2550 |
| 30 % | 80 mm / 4300 lx | 100 / 2800 | 100 / 2650 | 100 / 2500 | 100 / 2400 |

Idealus 40-60 mm šviesdėžėms ir plačioms raidėms; konkurencingas ir 40-50 mm siauresnėse raidėse.
40-60 mm, per ištiestą laidą (100 x 100 mm): ~2800-2500 lx, ~50 W/m².

**P130L (1 W)**
| Gylis | 60 mm | 70 mm | 80 mm | 90 mm | 100 mm |
|---|---|---|---|---|---|
| 45 % | 150 mm / 2850 lx | 170 / 2500 | 200 / 1900 | 200 / 1800 | 200 / 1700 |
| 30 % | 150 mm / 2600 lx | 170 / 2000 | 200 / 1600 | 200 / 1500 | 200 / 1400 |

Šviesdėžėse 60-70 mm - kas 150 mm; 75-80 mm - iki 200 mm tarp centrų (1500-2000 lx, mažiau modulių).
Plačiose raidėse - nuo 50 mm viena eile (2000-3000 lx).

**P190L (1,5 W)**
| Gylis | 75 mm | 80 mm | 100 mm | 120 mm | 140 mm |
|---|---|---|---|---|---|
| 45 % | 190 mm / 2700 lx | 200 / 2350 | 250 / 1800 | 270 / 1550 | 270 / 1500 |
| 30 % | 190 mm / 2250 lx | 200 / 2000 | 250 / 1500 | 270 / 1300 | 270 / 1250 |

Šviesdėžėse nuo 80 mm (~2000 lx, gerokai mažiau modulių); raidėse nuo 80-100 mm.

Gide: „Dėl plataus lęšio Lens moduliai praras daugiau ryškumo esant siauroms gilesnėms raidėms."

## 24V moduliai - NAUJESNĖ tiekėjo lentelė (Rytis 2026-10-09)

Tiekėjas: „Lentelė, kurią atsiuntėte, yra senesnė. Neringa prašė P320L pagal naują, kur kiekviename tūryje būtų
3 žingsniai / ryškumai. Jūs jau kurį laiką naudojate P320L, kurie paskaičiuoti ir šiame projekte, išskyrus 80 mm -
čia panaudotas P170L (toks pat kaip 4LED P320L, tik dviejų LED)."
Originalas: `assets/led_lens_24v_lentele_2026-10-09.png`; duomenys - `assets/led_lens.json` (`modules_24v`, `lux_table_24v`).

| Kodas | LED | W | lm | Grandinė, vnt. | Max tarp centrų | Stabili srovė | Kampas | Rekomendacija |
|---|---|---|---|---|---|---|---|---|
| P320L (24V) | 4 | 2 | 340 | 30 | 320 mm | taip | 175° | šviesdėžės |
| P170L (24V) | 2 | 1 | 170 | 40 | 240 mm | taip | 175° | šviesdėžės |
| P120 (24V) | ? | 0,72 | 120 | 30 | 180 mm | taip | 175° | raidės |

**P320L - žingsnis = tarp eilių (kvadratinis tinklelis):**
| Gylis | 80 | 100 | | 120 | | | 140 | | | 160 | | | 180 | | | 200 | | |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Žingsnis mm | 200 | 220 | 250 | 200 | 220 | 240 | 200 | 220 | 240 | 180 | 200 | 220 | 160 | 180 | 200 | 160 | 180 | 200 |
| vnt./m² | 25 | 21 | 16 | 25 | 21 | 17 | 25 | 21 | 17 | 31 | 25 | 21 | 39 | 31 | 25 | 39 | 31 | 25 |
| W/m² | 50 | 41 | 32 | 50 | 41 | 35 | 50 | 41 | 35 | 62 | 50 | 41 | 78 | 62 | 50 | 78 | 62 | 50 |
| lm/m² | 8500 | 7014 | 5440 | 8500 | 7014 | 5892 | 8500 | 7014 | 5882 | 10482 | 8500 | 7014 | 13260 | 10482 | 8500 | 13260 | 10482 | 8500 |
| lx | 4400 | 3200 | 2400 | 3300 | 2700 | 2300 | 2850 | 2350 | 2000 | 3000 | 2450 | 2100 | 3300 | 2650 | 2150 | 2900 | 2300 | 1900 |

Neaišku (klausti, neišgalvoti):
- 80 mm stulpelis: tiekėjas rašo, kad testuota su P170L, bet W/m² ir lm/m² skaičiai atitinka P320L (25 x 2 W, 25 x 340 lm).
- P170L ir P120 lentelės tuščios; modulių matmenų nėra; P120 LED skaičius nežinomas.
- Ar senesnė 12V Lens lentelė (P65L / P130L / P190L) dar galioja, ar keičiama 24V moduliais.

**Šviesdėžės skaičiuoklė:** `python3 scripts/led_box.py <plotis> <aukštis> <gylis> [P320L ...]` - visi tiekėjo
žingsniai / ryškumai tam gyliui (žemesnis lentelės stulpelis), tinklelis su kraštine eile per pusę žingsnio nuo krašto,
vnt., W, ~lx pagal faktinį tankį, grandinės (P320L <= 30 vnt.). Ryškumą renkasi Rytis / klientas - skriptas nesprendžia.
Raidėms (`led_sim.py`) 24V moduliai dar NENAUDOJAMI - trūksta matmenų ir P120 duomenų.


## (iš SKILL.md v80) LED - Lens moduliai (tiekėjo duomenys)
Modulių duomenys (12V Lens ir 24V P320L / P170L / P120) ir Ryčio / tiekėjo taisyklės - `references/led_lens.md`, `assets/led_lens.json`; ŠVIESDĖŽĖMS - `scripts/led_box.py`; gidas
`assets/led_lens_gidas.pdf`. **LED IŠDĖSTYMAS RAIDĖSE (v30, perrašyta nuo 0): `python3 scripts/led_sim.py spec.json <out>.pdf`** - PRIVALOMA
perskaityti `references/led_sim.md` ir `references/led_gamybos_pavyzdziai.md` (įmonės stilius - apskritimai, kiekiai virš raidžių). Apšviestumo simuliacija (tiesioginė šviesa su šonų užstojimu + šonų atspindys);
riba - tiekėjo raidžių eilės bangavimas (U = P5/vid, H = P95/vid ašyje); forma: moduliai ašyje, laisvame gale - modulis
gale, sankirtoje - vienas modulis, šakos per pilną žingsnį, žiedai simetriški; plačios linijos - kelios eilės (LED Wizard
Runs / Clearance); žingsnis - didžiausias (<= laido ilgis ir tiekėjo žingsnis), kuriuo VISOS raidės tenkina ribas. Lapas: 1 - išdėstymas, 2 - apšviestumo žemėlapis. Modelio parametrai patikslinti bandymu.
Lape LED - tik kai Rytis nurodė / patvirtino modulį; PSU atsargą klausti.

