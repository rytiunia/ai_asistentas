# SPAR TYPE 670 FRISK & SUNN (BrandFactory, 2026-10-08) - folded box lid iš 2 dalių

Kliento failas: `SPAR_TYPE_670_Frisk__Sunn.pdf` (1:10, 3600 x 670, dalys 1500 + 2100).
Analogas etalone - SPAR 225960 18 lapas (FRISK & SUNN 3000 x 1000).

## Eiga
1. `python3 mkclean.py <kliento.pdf> t/frisk670_client.pdf` - švarus kliento failas: VIENAS fono stačiakampis
   (kliento faile fonas iš 2 užpildų - skriptas imtų tik didžiausią dalį), apskritimas, raidės.
   Kitam failui pakeisti piešinių indeksus (52/53 fonas, 54 apskritimas, 55-64 raidės) ir fono ribas pt.
2. `python3 ../../braizyti_lapa.py spec670.json Drawing_<projektas>.pdf` (`panel_joints`, `cable`, `front: 8mm`).
3. `python3 one2one.py Drawing_<projektas>_1-1.pdf t/frisk670_client.pdf` - 1:1 (3 sluoksniai: raidės + dalys /
   dugnas -3 mm / L + D11). Folded skriptas 1:1 dar nedaro pats.
