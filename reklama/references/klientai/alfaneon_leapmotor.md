# Alfa Neon AB / LEAPMOTOR - kliento taisyklės (v228, Rytis 2026-10-14)

Raktažodžiai: Leapmotor, Leap Motors, LEAP26-, Purchase order 33577, goods label „33577 LEAPMOTOR 53811".
Užsakovas: **Alfa Neon AB** (Årstidsvägen 8, 66535 Kil, SE), pirkėjo atstovas Anders Sjösten, mūsų - Paulius Baubonis;
tiekėjas UAB ALT reklama. Pristatymas DAP, „Direktleverans", pakuotė - paletė; pristatymo data = išsiuntimas iš sandėlio.
Bendri Alfa Neon dalykai (CE lipdukas, Alfa Neon lipdukas 45x20) - `alfaneon_volvo.md` 2 skyrius (Mean Well Volvo standartas
Leapmotor NETAIKOMAS - čia 12 V 1,5 m + TRAFO BOX, Rytis).
Šaltinis: `Leap_Motors_signs_2026-10-14.pdf` (vektorinis, 1:1 pt - kontūrai tiesiai iš PDF), PO 33577.

## Spalvos / LED
- Šonai / korpusas - **RAL 7021** (tamsiai pilka); priekiai - balti akrilo; LED **6500K**.

## Gaminiai (PO 33577)
| Poz. | Kodas | Gaminys | Kiekis | Sprendimas (Rytis 2026-10-14) |
|---|---|---|---|---|
| 10 | LEAP26-01002 | Outdoor Logo 4500 x 585 (tekstas 294) | 40 | **P6, tūris 60 mm**, šonai RAL 7021, balti priekiai, 6500K; **12 V 1,5 m + TRAFO BOX**; sumontuota ant **skaidraus orgstiklo rėmo** |
| 20 | LEAP26-06002 | Indoor Logo 1730 x 225 (tekstas 113) | 20 | kaip 10; **P6 tik jei padarius dugną lieka >= 16 mm raidžių ploto tarp kraštinių** (PO eilutės „Size 4500 x 585" - kliento klaida, tikras 1730 x 225) |
| 30 | LEAP26-02002-1 | Ljusdåda 1+10, 750 x 750 | 20 | **P10_lightbox_singlesided** (`moduliai_p10_lightbox_singlesided.md`): įdėklas 8 mm (išsikišimas 6), RAL 7021 |

## Skaidrus orgstiklo rėmas (poz. 10 / 20)
- Rėmas iš **skaidraus orgstiklo 20 mm**; dalys tarpusavyje jungiamos **„puzzle" tipo jungtimis, laisvumas 0,2 mm**.
- Rėme - **grioveliai laidams** (skaidrūs), **tvirtinimo skylės Ø8**.

## Įgyvendinimas (v229)
- Projektas `scripts/projektai/leapmotor_33577/` (PO, kliento PDF, `spec_LEAP26-01002.json`).
- Poz. 10: `braizyti_begeliai.py` su **"mounting": "acrylic"**, **"rail": {"type": "acrylic", "size": "40x20"}**, `"acrylic"`
  ({"thk": 20, "sheet": [3050, 2050], "joint_clear": 0.2, "hole_d": 8, "holes_every_gap": 2, "groove": {"w": 8, "d": 10}}); priekis
  `"front": "P6"` (buv. "8mm"; balta akrilo priekis frezuota - PATIKSLINTI su Ryčiu, PO: „white acrylic fronts").
  Rezultatai: lapas, 1:1 PDF, `_akrilinis_remas.dxf` (ACRYLIC_20_CUT dalys su puzzle, HOLES_D8, GROOVE_BACK_AXIS).
- Rytis 2026-10-14: ALT numeris - blank `ALT0000_00.00_RS`; akriliniam rėmui PAPILDOMI statmenys po raidėmis; puzzle -
  kiek įmanoma po raidėmis; Ø8 skylės tarp raidžių, bet dvigubai mažiau (kas antrame tarpe); bėgelis 40 mm; simbolis ant
  to paties rėmo kaip raidės (vientisa reklama).
- v231 (Rytis 2026-10-14): **per daug statmenų** -> žingsnis 1000 mm per stiebus (5 statmenys + 1 įstrižas 4466 ilgiui);
  **jungtys pagal medžiagos ilgį nurodomos** (J1, dalys 1499 + 2967 iš lakšto 3050); **griovelis 8 pločio x 10 gylio**.
  Poz. 30: priekis prisukamas per perimetrą; LED ant dugno galinės plokštumos; LED tipas - paliekamas „?", tikrinama gamyboje;
  varžtų tipas neaktualus.
- v232-v233 (Rytis 2026-10-14): statmenys / įstrižai - **atskiros detalės, į bėgelius jungiami puzzle** (taupoma medžiaga);
  profilio pjūvis - etaloninis **P6** (ne senas `p6_typical`), akrilo bėgelis pilnaviduris; priekio kodas `"front": "P6"`
  (buv. P6_8mm). Poz. 10 dokumentas - **2 lapai**: 2 lapas „ACRYLIC FRAME - PARTS & JOINTS" (R1-R4, V1-V5, J1, DETAIL C / D,
  SECTION E, blokas „WHY / WHERE THE FRAME JOINS", dalių BOM); 1 lape nuorodos C / D.
  Poz. 30: LED moduliai matomi pjūvyje A-A ir DETAIL B; exploded view - dešinė kolona per visą aukštį, top view - 2 eilėje.
- Neatsakyta: poz. 20 profilis (P6 netinka - štrichas ~16,2, dugnas -3 iš kiekvienos pusės -> ~10 < 16).
