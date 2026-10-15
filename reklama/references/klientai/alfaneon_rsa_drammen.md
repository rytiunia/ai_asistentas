# Alfa Neon AB / RSA HK Drammen - OMODA | JAECOO + EXLANTIX (PO 33580, 2026-10-14)

Raktažodžiai: OMODA, JAECOO, EXLANTIX, OMJE26-, EXLA26-, RSA HK Drammen, PO 33580, goods label „33580 RSA HK 53818".
Užsakovas Alfa Neon AB (Anders Sjösten), mūsų - Paulius Baubonis; pristatymas DAP, „Direktleverans", paletė, data 2026-11-11 (= atvykimas į Kil sandėlį).
Bendri Alfa Neon dalykai - `alfaneon_volvo.md` 2 skyrius. Šaltiniai: `OMJE26-01001...pdf` (1:1 pt), `RSA_HK_Drammen_2026-10-12.pdf`
(„Sammanställning" - abu užrašai vektoriais, EXLANTIX 1 pt = 9,7976 mm; „Bildförslag" - fasado nuotraukos).

| Poz. | Kodas | Gaminys | Sprendimas lape (v236-v237) |
|---|---|---|---|
| 10 | OMJE26-01001 | OMODA \| JAECOO 6712 x 375 | P6, balti akrilo priekiai, šonai / nugara RAL 9003, ATSKIROS raidės („separatmonteras på befintlig fasadplåt" - tamsi esama fasado plokštė) ant mažų L profilių, šablonas 1:1, pritemdomas LED driveris dėžėje RAL 5008. Trafaretinis šriftas - 24 atskiros dalys (O iš 2, E iš 3) |
| 20 | EXLA26-01001 | EXLANTIX 5205 x 375 | P6 kaip 10, „förmonterade på ram lackerad i RAL 5008" - rėmas U 30x30x2 RAL 5008 su L profiliais (ausėlės) ant STIKLO fasado |

Projektas `scripts/projektai/omoda_33580/` (spec, LED spec, rails JSON). Rėmas - AUTO (v238; rankinis rėmas v236-v237 buvo klaida). E vidurinė juosta (atskira dalis tarp bėgelių) be tvirtinimo - KLAUSTI Ryčio. ATVIRA: gylis (lape 80 - prielaida), L kampo profilis ir kiekis poz. 10, pritemdomo driverio modelis, EXLANTIX maitinimas (lape 12V + TRAFO BOX - prielaida), tvirtinimas į stiklo fasadą.

## 2026-10-15 - Ryčio nurodymai (v268)
- Poz. 10 OMJE26-01001: **P6 palaidos (atskiros) raidės**, tvirtinimo ir laido skylės DUGNE (lape + DXF + šablone), iš kiekvienos dalies
  12V 1,5 m laidas + trafo box (RAL 5008), montavimo šablonas 1:1. L profilių nėra. Gylis 80 - vis dar prielaida.
- Poz. 20 EXLA26-01001: **P6 ant L profilio** - kaip VOLVO užsakyme **BILB26-01001** (Rytis atsiuntė etaloną -
  `assets/etalonai/BILB26-01001_P6_ant_L_profiliu.pdf`; `"mounting": "l_hang"`, L 40x40x2 x2 + U 15x15x2 + fasado L 40x40x2 x2, RAL 5008);
  naujas kliento failas `EXLA26-01001_v2.pdf` (5205 x 375; „mounted on L-profiles for wall mounting on glass facade painted darkblue RAL 5008").
