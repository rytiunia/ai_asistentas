# Konstrukcinis standartas – parametrų prasmė ir klausimynas gamintojui

Standartas yra `assets/standartas.json`. Čia – ką kiekvienas skaičius reiškia variklyje ir ko klausti baldininko,
kai jo standartas dar nesurašytas. Kiekvienas cechas skiriasi dėl 2–3 mm; neteisinga prielaida pjaustymo centre
kainuoja visą užsakymą, todėl nežinomos reikšmės neatspėjamos.

## Parametrai

| Raktas | Reikšmė variklyje | Prototipas |
|---|---|---|
| `korpuso_ploksta.storis` | Šonų, dugnų, viršų, lentynų, juostų storis (T). | 18 |
| `korpuso_ploksta.dekoras` | Korpusų dekoras pjovimo lape (tiekėjo kodas). | W980 ST2 |
| `fasadas.storis / dekoras` | Fasadų ir cokolio plokštė; atskiras lapas Excel'yje. | 18, H1180 ST37 |
| `nugarele.storis` | HDF storis. **Užleista** nugarėlė: šonai ir dugnai trumpinami per TB, nugarėlė = korpuso išorinis gabaritas. | 3 |
| `stalvirsis.storis / gylis` | Stalviršis per visą apatinių liniją; atskiras tiekėjas, lapų neskaičiuoja. | 38 / 600 |
| `apatinis.korpuso_aukstis` | Apatinio korpuso aukštis be cokolio ir stalviršio. | 720 |
| `apatinis.gylis` | Korpuso gylis su nugarėle, be fasado. | 560 |
| `apatinis.cokolis` | Cokolio aukštis = korpuso apačia nuo grindų. | 100 |
| `apatinis.cokolio_atitraukimas` | Cokolio juosta atitraukta nuo fasado plokštumos. | 50 |
| `virsutinis.korpuso_aukstis / gylis` | Viršutinio korpuso aukštis ir gylis. | 720 / 320 |
| `virsutinis.apacia_nuo_grindu` | Viršutinių apačia nuo grindų (1400 → tarpas iki stalviršio 542 mm). | 1400 |
| `fasadai.tarpas_krastuose` | Fasado atitraukimas nuo korpuso krašto iš visų pusių. | 2 |
| `fasadai.tarpas_tarp` | Tarpas tarp dviejų fasadų (durų pora, stalčiai). | 4 |
| `fasadai.lentynos_atitraukimas` | Apatinio korpuso lentyna trumpesnė už šoną per tiek (gyliu). | 40 |
| `stalcius.tarpas_sone` | Tarpas tarp korpuso šono ir dėžės šono – priklauso nuo bėgelių (Tandem 12,5–13, Legrabox 21–22). | 13 |
| `stalcius.dezes_storis / aukstis / ilgis` | Dėžės plokštė ir gabaritai. Ilgis = bėgelio nominalas. | 16 / 150 / 500 |
| `kantas.matomas` | ABS storis matomiems kraštams (fasadai – 4 pusės, korpuso priekis). | 2,0 |
| `kantas.dezes` | ABS storis stalčių dėžėms. | 0,8 |
| `furnitura.*` | Pavadinimai furnitūros lape (lankstas, kojelė, pakaba). | Blum CLIP top 110° … |
| `rankena.ilgis` | Rankenėlės ilgis; durims – vertikali prie atidarymo krašto, stalčiams – horizontali per vidurį. | 160 |
| `rankena.atitraukimas_nuo_krasto / nuo_virsaus` | Padėtis ant fasado. Apatinės durys – viršuje, viršutinės – apačioje. | 40 / 60 |
| `lapas.plotis / aukstis / iseiga` | Lapo formatas ir išeigos koeficientas lapų įverčiui (tikslų duoda nestingas). | 2800 × 2070, 0,72 |
| `lapas.kanto_atsarga` | Kantų metrų atsarga. | 5 % |
| `orkaite.nisa_aukstis` | Orkaitės niša nuo orkaitės lentynos iki korpuso viršaus (60 cm orkaitė – 595). | 595 |
| `orkaite.stalciaus_dezes_aukstis` | Žemo stalčiaus po orkaite dėžės aukštis. | 70 |
| `nisa.aukstis / gylis / virsutines_aukstis` | Niša laisvai stovinčiam šaldytuvui: bendras aukštis, šoninės plokštės gylis, viršutinės spintelės aukštis (projektas perrašo). | 2000 / 600 / 400 |
| `hpl.storis / dekoras` | HPL siena tarp stalviršio ir viršutinių; atskiras tiekėjas. | 10 / ? |

## Ką variklis daro iš šių reikšmių (kad būtų aišku, kur ieškoti klaidos)

- Šonas: L = korpuso aukštis, W = gylis − TB; kantas tik priekyje (L1).
- Dugnas / viršus: L = plotis − 2T, W = gylis − TB; kantas priekyje.
- Apatinio viršus – dvi juostos 100 mm (priekyje ir gale), ne pilna plokštė.
- Lentyna: L = plotis − 2T − 2 (laisvumas), W = šono gylis − atitraukimas.
- Durys: aukštis = korpusas − 2·tarpas_krastuose; plotis vienoms = plotis − 2·tarpas, dvejoms = (plotis − 2·tarpas − tarpas_tarp) / 2.
- Stalčių fasadai: aukštis = (korpusas − 2·tarpas − (n−1)·tarpas_tarp) / n, lygiai.
- Dėžė: plotis = korpuso vidus − 2·tarpas_sone, 16 mm dugnas, šonai ant dugno, priekis/galas tarp šonų.
- Stalviršis ir cokolis – vienas gabalas per visą apatinių liniją.
- Furnitūra: 2 lankstai durims (iki 900 mm aukščio), 4 kojelės apatiniam, 2 pakabos viršutiniam, 8 konfirmatai korpusui,
  4 lentynos laikikliai, bėgelių komplektas stalčiui, rankenėlė kiekvienam fasadui.

Korpusų tipų konstrukcija – `korpusai.md`.

## Klausimynas gamintojui (surašyti prieš pirmą tikrą užsakymą)

1. Plokštė: korpusų storis ir dekoras; fasadų medžiaga (LMDP / MDF dažytas / Fenix) – ar tas pats tiekėjas?
2. Nugarėlė: užleista prisukama ar į griovelį? Storis. (Griovelis – variklis dar nemoka, žr. SKILL.md.)
3. Korpusų aukščiai ir gyliai: apatinis, viršutinis, aukštas; cokolio aukštis; viršutinių apačia nuo grindų arba tarpas nuo stalviršio.
4. Fasadų tarpai: kraštuose, tarp fasadų; ar fasadas dengia korpusą pilnai (full overlay) – variklis daro tik pilną.
5. Stalčiai: sistema (Tandem / Legrabox / Hettich), tarpas šone, dėžės plokštė, standartiniai aukščiai.
6. Lankstai: tipas, kiek vnt. nuo kokio aukščio (2 iki 900, 3 iki 1500 …).
7. Kantai: ABS storiai matomiems / nematomiems kraštams; ar kantuoja korpuso galą.
8. Pjaustymo centras: matmenys su kantu ar be; kantų žymėjimas; rašto žymėjimas; ar reikia jų Excel šablono (žr. `pjovimo_lapas.md`).
9. Stalviršis: storis, gylis, užleidimas per fasadą, tiekėjas.
10. Lapas: formatas, kokia išeiga jų patirtyje.
