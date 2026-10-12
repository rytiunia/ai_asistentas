# Joker order 226001 - Reinslettveien åpningstider (BrandFactory, 2026-10-09)

Du lapai: MAN-FRE 08-24 1947x208 (VH 200) ir LØR-SØN 10-24 2816x335 (VH 300). P6_8mm (opal plexi 8, be plėvelės),
gylis 60 (kliento 80 - neteisingas, Rytis), šonai RAL 9010, rėmas U 20x20x2 + ausėlės RAL 8014, laidas iš RAIDĖS virš
rėmo (lapas 1 - R, lapas 2 - Ø; `cable.from: letter`, `out: up`), 12V 1.5 m -> trafo box BE PWM (modelis - suskaičiavus LED).
- Kliento bėgeliai šviesiai pilki (0.9) -> spec `"rail_fills": [[0.9, 0.91, 0.91]]`.
- `python3 ../../braizyti_begeliai.py spec/1_MAN_FRE.json out.pdf` (client_pdf kelią pakeisti).
- Smax U20 lentelėje NĖRA - ausėlės tik pagal fiziką (klausti Ryčio Smax U20).

- Laidas iš raidės VIRŠ RĖMO (Rytis pažymėjo): MAN-FRE - R viršus, aukštyn ir į dešinę (`out: up`); LØR-SØN - Ø viršaus vidurys, taip pat aukštyn ir į dešinę (`out: up`) - Rytis: abu lapai vienodai, aukštesne trajektorija.
- LØR-SØN - 8 ausėlės (Rytis) -> `ears_smax: 1000`; MAN-FRE - 6.

## Patvirtinta 2026-10-11 - ALT8872_10.12_RS (v104)
`patvirtinta_ALT8872/` - spec iš patvirtinto PDF (kliento originalo nebeliko): `client_pdf` = Drawing_Joker_order_226001_patvirtinta.pdf
(pakeisti kelią), page 0 / 1, rail_fills RAL 8014 [0.29, 0.208, 0.149]; LED spec led_1/led_2 (feed `letter:5-top` - R / antroji Ø).
Rezultatas: MAN-FRE P65L 64 vnt. 32 W; LØR-SØN P65L 77 vnt. 38.5 W (P130L 81 vnt. 81 W).
