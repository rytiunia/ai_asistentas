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
| 20 | LEAP26-06002 | Indoor Logo 1730 x 225 (tekstas 113) | 20 | **P6, tūris 60 mm** (Rytis 2026-10-16; buvęs P10 30 mm sprendimas atšauktas), kaip 10 (PO eilutės „Size 4500 x 585" - kliento klaida, tikras 1730 x 225) |
| 30 | LEAP26-02002-1 | Ljusdåda 1+10, 750 x 750 | 20 | **P10_lightbox_singlesided** (`moduliai_p10_lightbox_singlesided.md`): įdėklas 8 mm (išsikišimas 6), RAL 7021; **gylis 50 mm pagal PO** („visa kita pagal užklausą", 2026-10-16; buvo 80) |

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
- 2026-10-15 (v235-v246, Rytis):
  - Poz. 20 = **P10** (30 mm balta plexi blokas, šonai RAL 7021, Alu 1,5 dugnelis įleistas į bloką) ant skaidraus akrilinio
    rėmo 20; gylis 30 + 20 = 50; `spec_LEAP26-06002.json` (`"front": "P10"`). Raidės mažos (113) -> **VIENAS bėgelis**
    (nuo 55 mm, gavosi 60); laidų griovelis rėme 6 x 3,5 + ovalios skylės kiaurai (kaip etalone Boots ALT6739).
  - Akriliniame rėme raidės prisukamos per **atskiras įleistas skyles** (Ø5 kiaurai + Ø12 x 15 iš galo veržlei);
    smeigės pagal raidės formą (kvadratas 4, trikampis 3, maža raidė - iki 3), arti centerline, ant bėgelio - viena
    horizontali linija; P tvirtinama kaip R; smeigės ir statmenyse (poz. 10 L). Poz. 10: 36 smeigės, poz. 20: 24.
  - P10 LED griovelis: simuliacija `griovelis_sim.py`, variantas B `griovelis_b.py` (`poz20/`); balti (atspindintys) šonai
    viduje tolygumui svarbiausi.
- Neatsakyta: P10 LED griovelio gylis; simbolio LED - dvi tiesios eilės ar žiedas; ar ~8 mm Alu dugnelio juostelė
  siauruose štrichuose tinka smeigei privirinti; poz. 30 kabelio skylė (y, Ø, tarpinė).

## Order 33577 dokumentas (v309, Rytis 2026-10-16: „raidės P6, tūris 60mm, visa kita pagal užklausą")
- VIENAS dokumentas `ALT0000_Order_33577.pdf`, 6 lapai: 1-2 poz. 10 (lapas + akrilo rėmo dalys), 3-4 poz. 20, 5-6 poz. 30;
  surenkama `scripts/projektai/leapmotor_33577/build_order.py`; 1:1 PDF ir DXF - kiekvienai iškabai.
- Poz. 10 / 20: P6 60 mm, priekis akrilas 8 mm baltas, šonai Alu 1 RAL 7021, dugnas Alu 1,5 (RAL 7021), LED 6500K (tipas „?"),
  12 V 1,5 m + TRAFO BOX, skaidrus akrilo rėmas 20 mm (poz. 20 - vienas bėgelis 70 mm, vientisas, be jungčių).
- BOM plotai - nesting visam kiekiui (40 / 20 vnt.), per 1 vnt.
- Neatsakyta: LED tipas (poz. 10 / 20 / 30); poz. 30 kabelio skylė (y, Ø, tarpinė); ar poz. 30 gylis tikrai 50 (PO „approx").
