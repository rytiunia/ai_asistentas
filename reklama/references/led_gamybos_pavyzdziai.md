# LED išdėstymas - GAMYBOS PAVYZDŽIAI (Rytis 2026-10-09: „pavyzdžiai algoritmui tobulinti")

Paveikslai: `assets/led_pavyzdziai/` (8 lapai, ALT8847-ALT8855, Kaizen KM-P0 / P2 / P3, Prizma P0).
Tai įmonės patvirtintas, gamyboje naudojamas stilius - algoritmo rezultatas turi atrodyti taip pat.

## Duomenys
| Lapas | Modulis | Gylis | Tarp centrų | Vnt. | Pastaba |
|---|---|---|---|---|---|
| ALT8847 alain afflelou (2651 x 280) | KM-P0 HE 0,36 W | 40 | ~60 | 128 | viena eilė, siauros raidės |
| ALT8850 Maisons du Monde (1250 x 447) | Prizma P0 HE 0,36 W | 60 | ~90 | 84 | apskritimai dengia raides, plexi 8 mm; PSU KPS-V12-60W |
| ALT8852 EXTRA 225818 l.1 | KM-P3-R 1,2 W / KM-P3 1,5 W | 100 | ~130 / ~150 | 32 + 61 + 34 | X - 2 eilės įstrižainėse |
| ALT8852 EXTRA 225818 l.2 | KM-P3-R 1,2 W, KM-P2 0,72 W | 100 | ~140, 7-23 ~100 | 63 + 66 + 43 + 31 | didelis X - tinklelis per visą plotą; 200 W + 120 W PWM |
| ALT8853 EXTRA 225923 | KM-P2-R / KM-P2 0,72 W | 100 | ~110-130 | 52 + 61 + 41 + 27 | |
| ALT8854 SJOKOLADE | KM-P2 0,72 W | 50 | ~100 | 85 | KPS-100W |
| ALT8854 GODTERI / SMÅGODT | KM-P2 0,72 W | 100 | ~100 | 62 / 78 | |
| ALT8855 Matkroken (rankraštis) | KM-P2 0,72 W | 100 | ~140 | 90 | |

## Taisyklės, kurias rodo pavyzdžiai (įtrauktos į `led_sim.py` v32)
1. **Apskritimas = žingsnis.** Aplink kiekvieną modulį braižomas apskritimas, kurio skersmuo = „tarp centrų".
   Linijoje apskritimai liečiasi (žingsnis = skersmuo); apskritimas gali išeiti už raidės ribų.
2. **Status linijos galas** (I, L, E, T galai) - apskritimas liečia galo kraštą: modulis per PUSĘ žingsnio nuo krašto
   („ląstelės": linija nuo krašto iki krašto dalijama į lygias dalis, modulis - dalies centre).
   Smailė (A viršus, V apačia) - modulis ne į pačią smailę.
3. **Kampas / lenkimas** (L, 7, E kampai) - modulis kampe (įbrėžtas apskritimas), toliau lygiu žingsniu.
4. **Sankirta** (T, E vidurys, K, A skersinis) - vienas modulis sankirtoje, šakos nuo jos lygiu žingsniu.
5. **Žiedai** (O, D, G) - tolygiai aplink, simetriškai (O: 10-12).
6. **Plačios linijos** - kelios lygiagrečios eilės (X: 2 eilės įstrižainėse), labai plačios - tinklelis per plotą.
   Kaizen pavyzdžiuose - viena eilė, kol linija ne platesnė už ~1,2 x žingsnį; Lens - pagal tiekėjo tinklelį (1,25 x) ir simuliaciją.
7. **Lapas:** kiekis virš kiekvienos raidės (stambiai), bendras matmuo, tekstas: Depth / Tarp centrų ~N mm /
   Module, vnt. / Power / PSU; skirtingi moduliai (RED / White) - skirtingų spalvų apskritimai.
8. Žingsnis nurodomas apytiksliai („~100 mm") - faktinis dalies ilgis gali būti keliais % didesnis / mažesnis.

## Lens moduliams
Kaizen pavyzdžių žingsniai (P2 0,72 W - ~100 mm prie 50-100 mm gylio) Lens moduliams netaikomi tiesiogiai:
Lens žingsnis - iš tiekėjo gido ir simuliacijos (`references/led_sim.md`), forma ir lapo stilius - iš šių pavyzdžių.
