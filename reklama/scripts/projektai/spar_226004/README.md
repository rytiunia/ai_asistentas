# SPAR order 226004 - Sundvollen (BrandFactory, 2026-10-09) - 3 lapai

| Lapas | Gaminys | Kaip |
|---|---|---|
| 1 | Åpningstider VH 400, 3090x522 | `braizyti_begeliai.py spec/1_VH400.json` |
| 2 | Åpningstider VH 500, 3861x653 | `braizyti_begeliai.py spec/2_VH500.json` |
| 3 | Back plate 2700 (plotis) x 2100 (aukštis) + spauda, sandūra 1400 + 700 | `backplate.py` (okq8.py pagrindu) |

- P6_8mm: opal plexi 8 + Day/Night perforuota plėvelė (black Gel'UV print), gylis 80, šonai RAL 9016,
  rėmas U 30x30x2 + ausėlės RAL 8011 (kliento „Rails RAL 9006" - Rytis: 8011), ausėlės kliento kvadratėliuose (`ears_pt`).
- Kliento bėgeliai - neužpildyti stačiakampiai -> `"rail_strokes": true`.
- Laidas 220V, 1.5 m, PSU iškaboje (`trafo_box: false`), bėgelio gale kliento pusėje (VH400 - dešinėje, VH500 - kairėje).
- Back plate (Rytis 2026-10-09): 2700 x 2100, SPAR STANDARTAS - 2 dalys 1400 (viršus) + 700 (apačia), NEPRIKLAUSOMAI nuo
  grafikos (išklotinės 2773 x 1473 / 773). Grafika pritraukta prie 2700 x 2100. L tik viršuje / apačioje, sandūroje Ø6 ~500;
  plokštė RAL 9005 + spauda Gel'UV + laminatas priekyje ir briaunose. DXF TOP / BOTTOM.
- VH400 apatinis bėgelis - po "7" (iki 10 mm "7" kojelės viduje); VH500 - 8 ausėlės (Rytis) -> `ears_smax: 1300`.
- Plėvelės FINISH langelis spalvotas: `lapas_core.FOIL["DAY/NIGHT"]`.
- Keliai: `backplate.py` importuoja `co/common.py`, `data.py`, `r3d.py` (clasohlson_horten projektas) ir okq8 struktūrą - pakeisti sys.path ir W_.
