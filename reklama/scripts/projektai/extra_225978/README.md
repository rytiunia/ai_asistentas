# EXTRA order 225978 (BrandFactory, 2026-10-08) - 5 lapų komplektas, NAS: Brandfactory/EXTRA/EXTRA H1000/EXTRA order 225978/

| Lapas | Gaminys | Kaip |
|---|---|---|
| 1 | FAS 1000H80 (7-23) 5732x1000, **P1 NON-LIT** | `braizyti_begeliai.py spec/s1_fas1000.json` (`"front": "P1"`, `power_note`, Z-frame) |
| 2 | FAS 700H80 (7-23) 4012x700, stogo iškaba | `clean_client.py` (be kliento stogo kojų: 16-23,113-116) -> `spec/s2_fas700.json` (7-23 `"single": true` statmuo po „7") |
| 3 | FAS 700H80 stogo atramos - rekomendacija | `roof_sheet.py t/fas700_be_koju.pdf out.pdf` (lapas_core, ne iškabos lapas) |
| 4 | Åpn496 7-23 1150x497 | `spec/s4_pn496.json` (U30) |
| 5 | Åpn894 7-23 2071x894 | `spec/s5_pn894.json` (U40) |

Sujungimas: pymupdf `insert_pdf` 1..5 -> `Drawing_EXTRA order 225978.pdf`, `lapas_core.pdf_fix_fonts`, `patikra_sriftai.py`.
1:1 - kiekvienam gaminiui `Drawing_EXTRA order 225978_1-1_<gaminys>.pdf` (braizyti_begeliai daro pats).

## Stogo atramos (Rytis 2026-10-08, pirmas toks lapas) - principas
- Precedentas: EXTRA order 225597 (stogo EXTRA 1953x400): kojos 25x25 Alu, plokštė 120x120x5, RAL 7035, nuimamos.
- Kojos □30x30x2 RAL 7035 kliento vietose; per paslėptas vietas (už plokštės, už E stiebo) - iki viršutinio bėgelio,
  kitur - iki apatinio bėgelio. Galinės atramos (kicker) □30x30x2 ~45°, pėda 650 už kojų, prie VIRŠUTINIO bėgelio
  (šakutė 5 mm + M8 - dirba gniuždoma ir tempiama). Kojos/atramos prie U - kampuotis L40x40x4 l=60 (M6 į flanšą, M8).
- Pagrindas 120x120x5, 4xØ9, EPDM 3 mm. Be atramų (momentinis pagrindas ant stogo) - NErekomenduoti.
- Vėjas: EN 1991-1-4, cf 1.8, qp 0.8 kN/m² (vb,0 26, II, z 5 m) - PRIELAIDA, tikrinti objekte; stogo tipą klausti.

## Rev B - „one frame" (Rytis 2026-10-09) - 4 lapai, `spec_one_frame/`
| Lapas | Gaminys | Spec |
|---|---|---|
| 1 | Åpn496 7-23 1150x497, P6_3mm | `1_Apn496.json` |
| 2 | Åpn894 7-23 2071x894, P6_3mm | `2_Apn894.json` |
| 3 | FAS 700H80 4012x700, X + EXTRA vienas rėmas, 7-23 atskirai | `3_FAS700.json` (`one_frame`) |
| 4 | FAS 1000H80 5732x1000 P1, X tiesiai ant apskritimo | `4_FAS1000_P1.json` (`one_frame`, `gap_mm: 0`) |
Sujungta: `Drawing_EXTRA order 225978_one frame.pdf` + 4 x 1:1.
