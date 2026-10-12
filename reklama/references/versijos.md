# reklama (iki 2026-10-10 - iskabu-techninis-lapas) - versijų istorija (iki v42)

Taisyklės perkeltos į SKILL.md skyrius (v43). Čia tik istorija.

## v119 (2026-10-12)

v119, Rytis 2026-10-12 („led dėliojimas vis dar blogas“, 7 pavyzdžiai, tarp jų jo perdaryti ALT8873 225978_1 / _2):
naujas `scripts/led_km.py` - KM-P2 / KM-P2-R, žingsnis pagal gylį (50 100, 70 120, 80 130, 100 140), led_sim skeletas +
galai p/2 + round(L / p), plati linija > 2p - tinklelis, PSU KPS <= 75 %, Ryčio lapo stilius. Patikra Åpn496 20 = 20,
Åpn894 35 / 36. Pavyzdžiai `assets/led_pavyzdziai/*_v2.jpg`, `*_RYCIO.jpg`, `ALT8869_coop_prix...`.

## v118 (2026-10-12)

v118, Rytis 2026-10-12 („kadangi h1800 pažymėti kur dedasi X tvirtinimo rėmai - tada vaizdas iš priekio ... kai nėra rėmo
žymėjimo, galinėje pusėje daroma C tipo žymėjimas"): `p6_dxf.py --plate-front` (plokštė iš priekio, be C), numatyta -
veidrodis + C žyma (ARC R6 45-315°, `--c-mark-r`, sluoksnis `5_C_ZYMA`, plokštės centre >= 15 mm nuo skylių).
EXTRA 225978 FAS700 / FAS1000 DXF perdaryti.

## v117 (2026-10-12)

v117, Rytis 2026-10-12 („skill: extra h1800 gamybos principas", failas extra_H1800.pdf - Extra Order 225818, ALT8852):
`references/klientai/extra.md` skyrius „EXTRA H1800 - gamybos principas" (išmatuota iš 1:1: X 1410x1226, Ø1800, 60x60x2 X
rėmas, 8 x Ø3.2 ant įstrižainių ašių, Ø11 šalia profilio), etalonas `assets/etalonai/extra_H1800_ALT8852_gamyba.pdf`.
Kodas nekeistas (p6_dxf X rėmo 60x60 automatiškai dar nedaro).

## v116 (2026-10-12)

v116, Rytis 2026-10-12 („p1 taisyklė: inside kontūras 0.7mm, nereikia drenažo skylių, kadangi led nesideda"): `p6_dxf.py --p1`
(inset 0,7, be drenažo, be D11; `--inset` numatyta 3 P6 / 0,7 P1), `braizyti_begeliai.py` 1:1 PDF P1 `back_inset_mm` 0,7.
EXTRA 225978 FAS1000 P1 DXF perdarytas.

## v115 (2026-10-12)

v115, Rytis 2026-10-12 („kai extra naudojama ant vieno rėmo, X tvirtinimas atitinka raidžių tvirtinimą - eina per rėmo profilio
horizontalų centrą", pavyzdys pzs_a.pdf): `p6_dxf.py` - raidės ant plokštės skylės `holes_on_rail()` kiekvieno X kertančio
bėgelio ašyje, D11 apatinio bėgelio ašyje; be bėgelių - senas „centras + 4 galai". EXTRA 225978: FAS700 X 6 x Ø4, FAS1000 8 x Ø4.

## v114 (2026-10-12)

Rytis: „įtrauk į skill medžiagų matmenų biblioteką - Alu, ACM, profiliai, patikrink Lietuvos tiekėjus ... kad nebūtų, kad
parašai 25x25x2mm Alu, o atsakymas, kad tokio nėra". `assets/medziagos.json` -> `profiliu_katalogas` (132 pozicijos: Heliopolis
visas katalogas, Lankava, Proplastik), Alu lakštai (Lankava 0,5-3 mm), AKP (Heliopolis visi, Proplastik ACP Bond / Dibond,
Plastena ACM) su RAL; `medziagos.py` - `parse_profile`, `profile_check`, `profile_warn`, `sheet_check`, CLI `profilis` / `lakstas`;
`braizyti_begeliai.py`, `braizyti_lapa.py` - automatinis perspėjimas. `references/medziagos.md` §0.

## v113 (2026-10-12)

v113, Rytis 2026-10-12 („labai daug nodes ant lenktų linijų, reikia kiekvieną kartą paspausti reduce nodes"): `p6_dxf.py` -
`fit_ring()` / `add_ring()` - kontūrai tiesėmis + lankais (bulge), `--fit-tol 0.02`. Patikra: VH400 PRIEKIS 8097 -> 397 mazgai,
FAS700 2371 -> 228; Hausdorff <= 0,03 mm.

## v112 (2026-10-12)

v112, Rytis 2026-10-12 („nėra extra dxf failų, tik darbo laiko dxf"; pavyzdys extra_darbiniai.pdf): `p6_dxf.py` - `--plate-fill`,
kelių spalvų `--fill`, `--spacer-d` / `--spacer-edge` / `--plate-gap`, sluoksnis `4_PLOKSTE`; X atskirai, apskritimas veidrodiškai
su Ø4 + Ø11. EXTRA 225978 FAS700 / FAS1000 P1 DXF.

## v111 (2026-10-12)

v111, Rytis 2026-10-12 („pataisymai extra: turi būti pažymėta kur kokie led dedasi“, pavyzdys EXTRA 223315 lapas 1):
`braizyti_begeliai.py` - galiniame vaizde virš grupės spec `"led"` užrašas (virš matmenų eilučių, balionas 5 jo nekerta);
SKILL.md LED skyriuje taisyklė; etalonas `assets/etalonai/led_zymejimas_galiniame_EXTRA_223315.pdf`.

## v110 (2026-10-12)

v110, Rytis 2026-10-12: šaltinis - GitHub repo `rytiunia/ai_asistentas` (iCloud zip'ai archyvuoti).

## v109 (2026-10-12)

EXTRA 225978 patvirtinimas (ALT8873_10.12_RS): `braizyti_begeliai.py` - rail_fills spalvos ne-bėgelio formos praleidžiamos
(A / 7 kojų blokai darė A ir 7 „plokštėmis"), spec `client_vert_rails: false`. `references/patvirtinimas.md` papildyta.

## v108 (2026-10-12)

v108, Rytis 2026-10-12 („jeigu darant dugną P6 gaunasi siauros vietos iki ~11mm, kampas pakoreguojamas, vietoje taško
uždedama 2 ir padaroma bukas kampas"): `lapas_core.dugnas_inset()` (mitre + smailių įlinkių nukirtimas `inset` mm už stiklo
viršūnės, kai mitre smaigalys > `blunt_len` 12 mm), `p6_dxf.py --blunt-len`, `braizyti_begeliai.py` spec `back_blunt_mm`.
Patikra: Joker MAN-FRE (patvirtinta_ALT8872) M - kojelių įpjovos nukirstos ~3 mm virš stiklo viršūnės (kaip Ryčio pavyzdyje),
vidurio V (~11,6 mm) paliktas; E / F statūs kampai nepakito.

## v107 (2026-10-11)

v107, Rytis 2026-10-11 („įdomesnis pilonas ateities mokymams... pasidaryk atmintį, kad panašiais atvejais būtų galima panaudoti
panašius sprendimus“): `references/etalonas_pilonas_prisma_alt8826.md` (ALT8826 Prisma Skejby, 9 lapai), nuorodos SKILL.md /
`moduliai_pilonai.md`.

## v106 (2026-10-11)

v106, Rytis 2026-10-11 („jei kliento pateiktame faile bėgis netvarkingas, netinkamoje vietoje, per trumpas ar neatitinka
naudojamo standarto, pataisoma pagal skill, nebent nurodoma kad naudoti kliento pateiktą rėmo struktūrą“): `braizyti_begeliai.py`
`client_frame_issues()` + spec `client_frame` / `client_frame_tol_mm`. Bandymai: bandymas_aa spec.json (client_rails.pdf, ašys
82-86 mm nuo centro) -> auto rėmas = spec_auto rezultatas; su `client_frame: true` - kliento 7645 / 7575 / 4260 / 4345;
TESTAS, POWER, Joker LØR-SØN - tvarkingi (nekeičiami); Joker MAN-FRE - auto nepavyko, lieka kliento.

## v105 (2026-10-11)

v105, Rytis 2026-10-11 („pateik tik PDF su maketu, pdf su led dėliojimu, ir vientisus dxf failus. reklama.zip nepridėk, tik
atnaujink į iCloud jei yra kazkokių pakeitimų“): patvirtinimo paketas - 3 rūšys failų; DXF `--no-letters`.

## v104 (2026-10-11)

v104, Rytis 2026-10-11: „įkeliu dokumentą, parašau patvirtinta, ALT5432_10.12_RS, ir tada sukuriamas dokumentas su parašytu ALT
numeriu, dxf failas 1:1, ir led dėliojimo lapas“ - `references/patvirtinimas.md`. Joker 226001 (ALT8872_10.12_RS) - pirmas.
`led_sim.py`: spec `page`; `feed_at` „letter:N-top“ (laidas iš raidės). `p6_dxf.py`: kontūrai < 20 mm (ausėlių Ø mūsų lape) - ne raidės.

## v103 (2026-10-11)

v103, Rytis 2026-10-11 („kad ateityje nebūtų nesusipratimų, tai vadinsis prie rėmo prierašas + hangers“):
rėmo aprašo prierašas „+ hangers“ = U laikikliai (`mounting: brackets`), „+ ears“ = ausėlės. `braizyti_begeliai.py`: jei spec
neturi `mounting`, o MAIN DATA Rails / `frame` tekste yra „+ hangers“ - režimas brackets.

## v102 (2026-10-11)

v102, Rytis 2026-10-11 („pataisyk: rėmas su hangers“, „prieš tai padarytas kabinimas, vadinosi U laikikliai“):
HANGER = U laikiklis (`mounting: brackets`), NE ausėlė. Lapo užrašai: BOM „Hanger U HxW, fl. F“, MAIN DATA „+ hangers“,
2 lapas „Hangers (U)“ / „BILL OF MATERIALS - HANGERS“, NOTES. `_hang()` seną „Wall bracket“ tekstą perrašo.
Pataisyta klaida: brackets režime BOM dingdavo bėgelio eilutė („Rail U ... with ears“ kliūdavo už ausėlių filtro) - dabar
lieka be „with ears“. POWER 3a: 3 hangers H 313 (rėmas 305 + 2), DXF `3_REMAS` su jais.

## v101 (2026-10-11)

v101, Rytis 2026-10-11 („dxf faile nėra tvirtinimo auselių, tik rėmas, jos turi būti kartu kaip rėmo dalis“):
`braizyti_begeliai.py` `RAILS_JSON` eksportuoja `ears` (kontūras + skylės centras, d) ir `brackets` (kontūras + skylės),
įstrižų bėgelių `poly`; `p6_dxf.py` juos braižo `3_REMAS` sluoksnyje kartu su bėgeliais. POWER 3a: 8 ausėlės DXF.

## v100 (2026-10-11)

v100, Rytis 2026-10-11: MAIN DATA - „Wall" tik nestandartiniam fasadui, „Drainage" niekada (skriptas šalina); BOM
„Letter back" FINISH = šonų RAL (`back_ral` - kitokia), `braizyti_begeliai.py` ir `braizyti_lapa.py`.

## v99 (2026-10-11)

v99, Rytis 2026-10-11: drenažo Ø8 skylutė visa dugno viduje (centras r + 1 virš žemiausio taško, `drain_points(r=)`);
rėmo matmenys apvalinami 5 mm (`RND`, spec `frame_round_mm`): bėgelių ilgiai (strypų skaičiaus nedidinant), tarpai
tarp bėgelių; esami statmenys (auto rėmas) perkeliami kartu. POWER: 2970 / 3020, statmenys 245; BB 850 / 610 / 490.

## v98 (2026-10-11)

v98, Rytis 2026-10-11: (1) 6 m strypai - visam užsakymui (`QTY` iš spec, `medziagos.trim_to_stock(..., qty)`), renkamas
mažiausias patrumpinimas su mažiausiu strypų kiekiu (didesnis - tik jei likutis +500 mm); POWER 2 vnt.: 4 -> 3 strypai
[3019+2972] x 2 + statmenys. (2) DRENAŽAS exterior - `p6_dxf.drain_points`: dugno išorinio kontūro lokalūs žemiausi
taškai (pakilimas >= 5 mm abiem kryptimis, virš taško medžiaga, po juo tuščia), Ø8 `2_GALAS`; `--interior`, `--drain-d`.
Bandymas_A: a 3, m 3, n 2, d 2, s 2, y 1, B 1.

## v97 (2026-10-11)

v97: POWER Brotorvet 3a (Imagon) - `scripts/projektai/power_brotorvet_3a/`; `p6_dxf.py --crop --fill` (lapas su keliais
vaizdais); `lapas_core.FOIL` ORACAL 8500-034 (#EB690F).

## v96 (2026-10-11)

v96, Rytis 2026-10-11 (vizualinė patikra): statmuo po E REIKALINGAS - v95 „artimi nededami" atšaukta, tarpiniai statmenys
pagal kiekio taisyklę (min tarpas 300). TESTAS: [T 525, E 1370, T 3820, A įstrižas 5157].

## v95 (2026-10-11)

v95, Rytis 2026-10-11 („nuimti nuo E ir įdėti įstrižą ant A kaip EXTRA"): `place_verticals` - kandidatai = stiebų centrai +
įstrižos kojelės (`_leg_line`, raidėms be stiebo); galiniai statmenys arčiausiai rėmo galų, tarpiniai tolygiai, ne arčiau
nei 0,5 žingsnio (min 300) nuo kito. TESTAS: [T 525, T 3820, A įstrižas 5157].

## v94 (2026-10-11)

v94, Rytis 2026-10-11: rėmo gale dvi ausėlės greta (< 0,5 Smax) -> viena arčiausiai galo (tarpas iki 1,5 Smax); konsolėje
spausdinamos ausėlių x kiekvienam bėgeliui; perspėjimas, kai apkrova ausėlei > inkaro; U laikiklis P6 pjūvyje
(`p6_ref.draw(bracket=)`, `lapas_core.p6_reference(bracket=)`), pjūvis braižomas po BOM pernumeravimo.

## v93 (2026-10-11)

v93, Rytis 2026-10-11: horizontalus bėgelis > 6 m pirmiausia trumpinamas iki strypo (TESTAS 6500 / 6114 -> 6000 / 6000,
be sandūrų); jungiama tik kai galų laisvumo (raidžių išorinė pusė, 10 mm) neužtenka (BB 7,35 m).

## v92 (2026-10-11)

v92, Rytis 2026-10-11: v91 „rėmas per centrą ± 0,25 H" ATŠAUKTA (nesusikalbėjimas) - horizontalūs bėgeliai kaip įprasta (per
E viršutinės / apatinės kojelės centrą). Per RAIDĖS CENTRĄ - statmenys (`place_verticals`: galimų vietų atkarpos -> vidurys)
ir U laikikliai (stiebo vidurys; S / A - raidės gabarito vidurys). Ryčio skaičiai (1000/1080, 33, 200/100) - pavyzdžiai.

## v91 (2026-10-11)

v91, Rytis 2026-10-11: `"brackets"` - (bėgeliai per centrą ± 0,25 H - atšaukta v92), H >= 1000 - laikikliai tolygiai
(gali matytis, rekomenduojamas stambesnis rėmas); laikiklio vidus = rėmas + 2 (rėmas ant apatinės plokštumos), skylės į
fasadą žingsniu p, nuo galų p / 2, rėmas >= 1000 - 3 skylės; BOM be ausėlių. `"none"` - BOM / MAIN DATA be rėmo
(net 0 m), laido eilutė pagal `letters_power`, šone tik raidės gylis.

## v90 (2026-10-11)

v90, Rytis 2026-10-11: P6 priekiai - `scripts/p6_front.py` (3mm / 3mm+foil / 3mm color / 8mm / 8mm+foil / 8mm color /
10-15-20-30mm (+foil), frezuoti kaip 8 mm; kantelis baltas, išskyrus color; svoris pagal storį). Montavimas
(`references/moduliai_montavimas.md`): `"mounting": "brackets"` - U laikikliai (vidus = rėmas + 2, rėmas guli ant apatinės plokštumos, plotis 50,
plokštumos profilis + 3, Al 3 / plienas 3, skylės į fasadą žingsniu p ir p/2 nuo galų, rėmas >= 1000 - 3 skylės; rėmas per
raidžių centrą, didelėms raidėms - tolygiai ir stambiau), 2 lapas - laikiklio brėžinys; `"none"` - atskiros raidės, ašys skylėms
į DXF (`separate`), D11 vienoje linijoje, WAGO / 12V 1,5 m. Fasadas nenurodytas = betonas (`tvirtinimas.json`
wall_default). BOM - tik bendros sumos (`subst` šalina `{RAIL_LIST_M} = `). `medziagos.nest_bars`: > 6 m bėgelis -
dalys mažiausioms atliekoms (`LAST_SPLITS`), <= 6 m nedalijamas. Įtampa nenurodyta - klausti; varžtai - teorija.

## v85-v89 (perkelta iš SKILL.md v90)

v89, Rytis 2026-10-11: PILONAI / TOTEMAI - naujas modulis `references/moduliai_pilonai.md` (rėmas 60x60x3 = skarda - 6, 1 tarpinis skersinis, mėlyna lovelė 2 x 40 / 2 x 43, L 25 + balta su apverstu U viršumi, csk varžtai, segmentas prie rėmo per mėlynos šonus, flanšai Alu 20 arba paslėptas balkis 80x40x4 + įvorės + 4 x M16; grafika - full-face wrap; dokumentas klientui be išklotinių, 3D tik išoriniai kūnai, nesikertantys balionai, klausimų blokas užsakovui), kodas `scripts/projektai/thales_d059422/`; RAL 5022 / 5012 - `lapas_core`. v88, Rytis 2026-10-10: rėmo PRINCIPAS - struktūra pagal formą ir dydį, taisyklės ne mechaniškai; nauja situacija - analogiškas sprendimas iš turimų žinių. v87, Rytis 2026-10-10: rėmas - KONSTRUKCIJA, statmenų kiekis pagal dydį ir svorį: ceil(L / 2500) + 1, masyvioms raidėms (>= 0,5 m² / m) ceil(L / 2000) + 1. v86, Rytis 2026-10-10: P6 DXF - VIENAS failas (visa iškaba), laido variantas pagal užsakymą (`--no-letters --cable bottom|top`); po raidę ir abu variantai - tik paprašius. v85: P6 DXF su rėmu IŠ LAPO - `braizyti_begeliai.py` (RAILS_JSON) -> `p6_dxf.py --rails-json` (auto rėmas, kelios eilutės, akcentų laikikliai). Ankstesnės (v73-v84: medžiagos / 6 m, auto rėmas, pakopos, akcentai, ausėlės poromis, platus galas) - `references/versijos.md`.

## v89 (2026-10-11)

v89, Rytis 2026-10-11: pilonų modulis (`references/moduliai_pilonai.md`, CEOS D059422 Thales Campus Velizy, rev B) - žr. SKILL.md.

## v73-v84 (perkelta iš SKILL.md v87)

v84, Rytis 2026-10-10: didelis apskritimas / plokštė gale - pagal užsakymą: vientisa iškaba -> ant bendrų bėgelių, atskira -> savo kabinimas kaip EXTRA X (Z profiliai). v83, Rytis 2026-10-10: PLATUS GALINIS ELEMENTAS (plati raidė, kvadratas, apskritimas) - rėmas pratęsiamas iki raidės galo, ausėlė rėmo gale IŠSIKIŠUSI už raidės. v82, Rytis 2026-10-10 eskizas: PAKOPINIS GALAS - nesutampant eilučių galams trumpesnės eilutės artimesnis bėgelis pratęsiamas iki ilgesnės eilutės galinio statmens, tas statmuo vientisas per tarpą. v81, Rytis 2026-10-10: ausėlės - kai poromis su Smax neišeina, NE atskiri bėgeliai, o Smax +10/20/30 % ir (siena unknown) be fizikos - PORŲ logika lieka. v80, Rytis 2026-10-10: eilutės sujungiamos ABIEJUOSE galuose (jungiamasis statmuo tarpe); ausėlės ant KIEKVIENO bėgelio - nėra sprendinio <= Smax -> godus išdėstymas per visą bėgelį; rėmo galas be ausėlės -> ausėlė ant galinio statmens laisvoje vietoje. v79, Rytis 2026-10-10: GALINIAI statmenys VISADA abiejuose eilutės rėmo galuose; sutampant eilučių galams - vienas VIENTISAS galinis statmuo per abi reklamas; horizontalus bėgis vientisas, baigiasi ties statmens vidine plokštuma, niekada nekertamas. v78, Rytis 2026-10-10: RĖMO VIRINIMO / SURINKIMO TVARKA auto rėme - horizontalūs ištisiniai, statmenys pjaunami tarp bėgelių (per abi eilutes = 3 dalys), kampai švarūs (kyšulys už kraštinio statmens < 300 mm nupjaunamas), statmuo nekyšo už bėgelio galo. v77, Rytis 2026-10-10: AKCENTAMS (Ė taškas, Ū brūkšnys, i taškas) auto rėme LAIKIKLIS nuo eilutės viršutinio bėgelio (LED maitinimui); kelių eilučių rėme AUSĖLĖS IR TARP UŽRAŠŲ - kiekvienos eilutės bėgelių pora gauna savo ausėles (viduriniai bėgeliai irgi), antros eilutės tarpinės ausėlės ŠACHMATIŠKAI (`auseles.py` avoid_x). v76, BB „LIETUVA / TĖVYNE MŪSŲ": auto rėmas - akcentai (Ė, Ū) ne atskira eilutė; eilutės statmuo šalia (<= 400 mm) per abi eilutes einančio šalinamas. v75, Rytis 2026-10-10, aa_remas.pdf: RĖMAS IŠ RAIDŽIŲ, kai kliento faile bėgelių nėra - spec `"auto_frame": true`, `scripts/auto_remas.py`: bėgelių ašys ir galai per raidės TVIRTINIMO PLOTO (štricho) CENTRĄ, statmenys per stiebus, per abi eilutes kur stiebai sutampa. v74, Rytis 2026-10-10, „Bandymas / antras": kelios eilutės ant VIENO rėmo - spec `"merge_rows": true` (eilutės -> viena grupė, 4+ bėgeliai, statmenys kiekvienos eilutės porai, jungiamieji statmenys tarp eilučių iš kliento failo, ausėlės tik kraštiniuose bėgeliuose, viena laido išvestis); bėgelis > 6 m strypų plane skaidomas 6000 + likutis + perspėjimas „jungti iš 2 dalių". v73, Rytis 2026-10-10: TIEKĖJŲ MEDŽIAGŲ FORMATAI ir 6 m STRYPŲ TAISYKLĖ - `assets/medziagos.json` (Heliopolis, Plastena: profiliai 6 m, PMMA / PVC / AKP / Alu / PC / PS lakštai), `scripts/medziagos.py`, `references/medziagos.md`; rėmas po raidėmis, kuris gaunasi pvz. 6,05 m, patrumpinamas, kad tilptų į 6 m strypą, nepažeidžiant 10 mm / išorinės pusės taisyklių (`braizyti_begeliai.py`); folded L profilių strypai ir išklotinės lakšto patikra (`braizyti_lapa.py`, `folded_dxf.py`); BOM `{RAIL_BARS}` `{RAIL_PLAN}` `{L_BARS}`; senos „Žinomos klaidos" -> `references/klaidos.md`. v72: pervadinta į `reklama` (zip `reklama.zip`, aplankas `reklama/`). v71: SKILL.md < 48 KB - istorija v43-v70 -> `references/versijos.md`, moduliai -> `references/moduliai_folded.md` / `references/moduliai_kiti.md`. v67-v70 - `references/versijos.md`.

## v71-v72 (perkelta iš SKILL.md v73)

v72 (2026-10-10): skill'as pervadintas į `reklama` - iCloud zip `reklama.zip`, paskyros skill'as `reklama` (senas
`iskabu-techninis-lapas` paskyroje ištrinamas), zip vidinis aplankas `reklama/`; projektų skriptų nuorodos į skill'ą -
santykinės; taisyklės nepakeistos. v71: SKILL.md sutrumpintas iki < 48 KB paskyrai - versijų istorija v43-v70 -> čia,
folded moduliai -> `references/moduliai_folded.md`, □ profilis / P1 / stogas / senų brėžinių perdarymas ->
`references/moduliai_kiti.md`; taisyklės nepakeistos.

## v43-v70 (perkelta iš SKILL.md v71)

**Versija: 2026-10-09 v70** (v70, Rytis 2026-10-09: P6 DXF - TRYS NEPRIKLAUSOMOS GRUPĖS (priekis, galas, rėmas), ne viena; kiekvienas sluoksnis savo BLOCK (PRIEKIS / GALAS / REMAS) + INSERT (0, 0) + DXF GROUP; v69, Rytis 2026-10-09, AAA „s": dugno dalis ant bėgelio, kurios neprispaudžia jokia skylė (už R nuo visų to bėgelio skylių), VIS TIEK gauna tvirtinimo skylę - jei ašyje netelpa, U sienelėje iki 8 mm nuo ašies (`--off-axis`), >= 7 nuo dugno krašto, >= 8 nuo bėgelio galo; v68, Rytis 2026-10-09, AAA „d": D11 TIK PLAČIOJE VIETOJE - siauri ruožai (jungtys, lankų galai) skirti LED; D11 ieškoma VISOJE bėgelio ašyje (kairėje / dešinėje raidės dalyje) su pilnu 20 mm iki dugno krašto, mažinama tik kai plačios vietos ant to bėgelio NĖRA (`p6_dxf.py`); v67, Rytis 2026-10-09, AAA „Bandymas": BĖGELIS TURI PASIEKTI KRAŠTINĖS RAIDĖS IŠORINĘ DALĮ - galas 10 mm nuo kraštinės raidės IŠORINIO krašto; jei tame aukštyje kraštinė raidė per plona (pvz. „s" apačia) ir galas sustoja raidės pradžioje / tarpe - bėgelis pastumiamas aukštyn / žemyn (>= 11 mm taisyklė lieka), kol galas pasiekia raidės išorinę pusę; v66, Rytis 2026-10-09: P6 DXF galutinės taisyklės - R 100, skylė štricho ploto CENTRE (ne galuose),
štrichas = tikras dugno ruožas ant ašies, vienodos raidės - vienodi tvirtinimai, kojelė prieš pilvelį (a / d), kojelės skylė
per jungties plotą, D11 VISADA bėgelio ašyje poroje su varžtu (2 variantai: viršus / apačia), rėmas RAUDONAS; v65 (lygiagretus
pokalbis, R 200, mėlyna, be D11) - pakeista. v65: P6 DXF 1:1 su TVIRTINIMO SKYLĖMIS - `scripts/p6_dxf.py`, bandymas TESTAS. v64: Rytis - atnaujinti IR paskyrą (Claude), IR iCloud zip; paskyroje - tas pats SKILL.md, skriptai / assets - iš iCloud zip. v63: VISŲ PROJEKCIJŲ (priekis, šonas, galas, 3D) linijos - HAIRLINE 0.1 pt (`_lw`: viskas > HAIR projekcijoje -> HAIR; r3d / View3D / folded 3D kraštai - HAIR); išimtis - laidas (raudonas 0.9). v62: realus P6 ir GALINIAME vaizde - stiklo kraštas aplink 1.5 mm mažesnį dugną (`p6_vaizdas.rear_view`). v61: galinio vaizdo balionas 5 - ne ant priekio vaizdo pavadinimo; EXTRA 225978 perdaryta su realiu P6. v60: realus P6 vaizdavimas įdiegtas VISUR - `braizyti_begeliai.py` ir `braizyti_lapa.py` šoninis vaizdas + 3D, be papildomų užrašų lape. v59: P6 REALUS VAIZDAVIMAS - stiklas = kliento kontūras, kraštas 3 mm, korpusas 1.5 mm mažesnis; šone / 3D: korpuso spalva | baltas kantelis | plėvelė (`scripts/p6_vaizdas.py`, bandymas S). v58: SPAR back plate 2700 x 2100 - STANDARTINĖ sandūra 1400 + 700, nepriklausomai nuo grafikos (v57 „2100 x 2700" - klaida, atšaukta). v57: kliento grafika be iškraipymo (cover); Day/Night plėvelės langelis spalvotas; bėgelio atstumo patikra - raidės >= 0.6 grupės aukščio. v56: SPAR 226004 - `rail_strokes` (kliento bėgeliai kontūrais), back plate + FOTO spauda: sandūra linijoje, kurios nekerta objektai; RAL 8011. v55: Joker 226001 spec - 1 pcs., laidas 1.5 m. v54: Joker = order 226001 (drawing no.). v53: laidas iš raidės - pagal nutylėjimą `out: up` (aukštyn virš matmenų ir į šoną), vienodai visuose lapuose. v52: laido išvestis iš RAIDĖS - VISADA VIRŠ RĖMO (virš viršutinio bėgelio), raidės viduryje, niekada po rėmu. v51: LAIDAS NIEKADA NEKERTA IR NEUŽSTOJA MATMENŲ / užrašų / išvadinių - trasa patraukiama į šoną (`cable.out: left|right`), D11 ne ausėlių juostoje; balionas 5 ne per bėgelio ilgio užrašą. v50: laidas iš RAIDĖS (D11) virš rėmo - `"cable": {"from": "letter", "x_pt": .., "out": "up"}`;
trafo box užrašas `trafo_box.label` (be PWM, kai modelis nežinomas). v49, Joker Reinslettveien: bėgelių modulis - `rail_fills` (kliento bėgelių spalva už
pilkos ribų), nulis / gabaritai pagal RAIDES (ne kliento bėgelio grafiką), bėgelis pastumiamas >= 11 mm nuo pilno aukščio
raidžių viršaus / apačios, tame pačiame aukštyje esančių bėgelių ašis - viena (be „0"), išdėstyme 3D plotas ribojamas
2 x priekio (ilgos siauros iškabos), RAL 8014. v48: EXTRA 225978 FAS 700 - □ 30x30x3 be ausėlių, 2 laido išvestys - kliento faile. v47: PROFILIO FORMA VISUR VIENODA - U visuose vaizduose U, stačiakampis - stačiakampis (`lapas_core.rail_section`). v46: EXTRA 225978 kiekiai ir viena laido išvestis FAS 700 - kliento faile. v45: vientiso rėmo DETAIL A - VISI bėgeliai (viršus + apačia) jų padėtyse kaip priekio vaizde, P1 varžtai ne ties bėgeliais. v44: VIENTISAS RĖMAS `"one_frame"` - plokštė (apskritimas) ant tų pačių bėgelių kaip
raidės; P1 raidė tiesiai ant plokštės `plate.gap_mm: 0`; EXTRA 225978 rev B. v43, Rytis 2026-10-09: STRUKTŪRA - BENDRINĖS produktų taisyklės (folded plate,
P6_3mm, P6_8mm, P1, bėgeliai, folded + plėvelė, kelių dalių folded, išklotinės DXF, nesting, 3D, matmenys) taikomos
VISIEMS tokio tipo užsakymams; KLIENTO RAKTAŽODIS (SPAR, EXTRA, Clas Ohlson, OKQ8 ...) tik prideda to kliento
taisykles iš `references/klientai/*.md`. Versijų istorija v8-v42 - `references/versijos.md`.)


v64: paskyra ir iCloud - tas pats SKILL.md; skriptai iš zip.

v63: projekcijų linijos hairline. v62: galinis vaizdas - dugnas -1.5. v61: balionas 5.

v60: realus P6 vaizdavimas įdiegtas į braizyti_begeliai / braizyti_lapa (šonas + 3D).

v59: P6 realus vaizdavimas (stiklas 3 mm kraštas, korpusas -1.5, baltas kantelis) - p6_vaizdas.py, bandymas S.

v58: SPAR back plate 2700 x 2100, standartinė sandūra 1400 + 700 nepriklausomai nuo grafikos (v57 matmuo atšauktas).

v57: (atšaukta dalis - 2100 x 2700) grafika cover, Day/Night FOIL, bėgelio patikra 0.6.

v56: SPAR 226004 - rail_strokes, back plate + foto spauda (sandūra be objektų), RAL 8011.

v52: laido išvestis iš raidės - visada virš rėmo, raidės viduryje.

v51: laidas nekerta matmenų - trasa į šoną; D11 ne ausėlių juostoje; balionas 5 ne per užrašą.

v50: laidas iš raidės virš rėmo (cable.from letter), trafo_box.label.

v49: Joker - rail_fills, nulis pagal raides, bėgelio atstumas nuo raidžių krašto, ašių grandinė be 0, 3D ribojimas išdėstyme, RAL 8014.

v48: EXTRA 225978 FAS 700 - □ 30x30x3, be ausėlių, 7-23 išvestis.

v47: profilio forma visur vienoda (U / stačiakampis) - DETAIL A, šoninis, 3D.

v46: EXTRA 225978 kiekiai, viena laido išvestis.

v45: vientiso rėmo DETAIL A - 2 bėgeliai priekio vaizdo padėtyse (Rytis 2026-10-09).

v44: vientisas rėmas `one_frame` (plokštė ant raidžių bėgelių), P1 be distancerių `plate.gap_mm: 0`, galinio vaizdo
pavadinimas šalia trafo dėžės, kai netelpa; EXTRA 225978 rev B.

v43: struktūra - bendrinės taisyklės vs `references/klientai/*.md`.

v42: FOLDED PLATE + PJAUSTYTA PLĖVELĖ (Rytis 2026-10-09, OKQ8 Väster S, `scripts/projektai/okq8_vaster/`): lapas - FRONT su kliento grafika, SIDE, REAR (L, Ø3.2 7 nuo krašto), DETAIL A (briauna + plėvelė 1:2), 3D (r3d), juostoje pjūvis; BOM: plokštė RAL, plėvelė ORACAL (spalvotas langelis), L, varžtai, tvirtinimas į sieną ?; + vinilo 1:1 PDF (sluoksniai: pjovimas / plokštė / sandūra) + išklotinių DXF. Spalvos klausti (kliento CMYK - tik vaizdui). FOLDED IŠ KELIŲ DALIŲ (back plate): sandūra dedama GRAFIKOS TARPE (didžiausio tarpo viduryje, apvalinti 5 mm; grafika sandūros nekerta), L 30x30x2 TIK viso skydo viršuje ir apačioje, sandūroje Ø6 skylės, žingsnis ~500 pagal apkrovas (lygūs tarpai, 50 nuo galų, 20 nuo briaunos krašto), varžtai + veržlės; DETAIL B - sandūros pjūvis. Lūžtančio fasado dalys (Horten) - atskiri segmentai be jungimo varžtų. DXF IŠKLOTINĖS: `scripts/folded_dxf.py PLOTIS AUKŠTIS out.dxf [GYLIS]` (R2, K0.44, 4 x 90°, šonai tarp viršaus ir apačios, Ø3.2 7 nuo krašto), daliai su sandūra - `okq8.flat_dxf(..., holes_top/bot, bolts_top/bot)`; sluoksniai CUT / BEND_UP_90_R2 / HOLES_D3.2 / HOLES_D6_JOINT / HOLE_D11_CABLE / LETTER_FIX_POINTS / TEXT; išklotinė - vaizdas iš priekio (FACE OUT).

v41: Clas Ohlson laido išvestis - Ø11 KAIRĖJE ŠONINĖJE užlenktoje briaunoje (ne viršutinėje), D11 aukštyje, laidas nuo D11 horizontaliai prie briaunos (Rytis 2026-10-09).

v40: ORIENTACIJA (Rytis 2026-10-09, Horten 3 klaida): kliento PLANO eskizas gali būti nupieštas ne iš gatvės pusės - prieš braižant PATIKRINTI ir lape rašyti iš kairės ŽIŪRINT IŠ PRIEKIO (Horten 3: kairėje trumpesnė 3684, dešinėje 6397); dalių numeracija, fold'ai, logotipo dalis, laidas (kairėje viršuje) - skaičiuojami iš PLANES tvarkos, ne ranka.

v39: CLAS OHLSON standartas papildytas (Rytis 2026-10-09): LAIDAS - baltas 12V, 5 m, KAIRĖJE VIRŠUJE: D11 logotipo lanke (>= 30 nuo kontūro, >= 20 nuo Ø4, kuo arčiau viršaus, `data.d11_point`) -> už plokštės -> Ø11 KAIRĖJE ŠONINĖJE briaunoje D11 aukštyje (v41 pataisa; 20 nuo briaunos krašto, matmuo nuo viršaus) -> TRAFO BOX RAL 7044 -> 230V; galiniame vaizde ir išklotinėje; 1:1 sluoksnis 7_CABLE_D11. FOLDED ant lūžtančio fasado, kai KAMPAI NEPATEIKTI - visos dalys su 90° šoniniais flanšais (standartinės dalys, nominalūs ilgiai), kampuose dalys susiliečia priekiniu kraštu; kampai lape tik informaciniai („sketch, not measured"). 3D ANT FASADO prekybos centro viduje: grindų plytelės, kaimyninės parduotuvės, karnizas, kolonos, vazonai, suolas (`sheet2v.environment`), platesnis vaizdas. RAL 7044 įrašytas į RAL lenteles.

v38: CLAS OHLSON P8 SPECIAL (Rytis 2026-10-09, Horten 3 / Horten 1, `scripts/projektai/clasohlson_horten/`): raidė = Al 3 priekis (didesnis už plexi, išsikišimas - klausti) + plexi 20 išfrezuotas apvalkalas (galas 7 + ertmė 13, sienelė ~7.5), LED Baltled Crown Mini 0.3 W 6500K ant priekio per vidurį, spaceriai Ø16x20 į plexi galą; TVIRTINIMAI PAGAL DYDĮ - `assets/clasohlson_proporcijos.pdf` (3 dydžiai 1:1): artimiausio aukščio etalonas, skylių centrai proporcingai, Ø4 / išilginė 6.1x3.7 / Ø8 diametrai NEKINTA (`refholes.py`); 1:1 - 6 sluoksniai. 3D: `scripts/r3d.py` - persidengiančių paviršių gylis lyginamas TAME PAČIAME taške + topologinis rikiavimas (nebėra prasišvietimo / dingimo); `View3D.solid` rikiavimas pagal centroidą - netikslus, naujiems lapams naudoti r3d. MATMENYS: DETAIL A 1:2 lūžęs vaizdas (briauna | lūžis | raidė), viena aiški grandinė eilutėje, maži užrašai už grandinės, tankių grandinių (n x žingsnis) - tik `50 | n x p = L | 50` + ašys.

v37: FOLDED tvirtinimo skylės (Rytis 2026-10-09, Clas Ohlson Horten 3): fonas -> L varžtams VISADA Ø3.2 skylės viršutinėje / apatinėje užlenktoje briaunoje, 7 mm nuo briaunos krašto (`SCR.hole_d`, `SCR.hole_edge_mm`), išdėstymas kaip anksčiau (50 nuo galų, ~300); išklotinėse - skylės; NESTING lakštuose - pildoma nuo lapo krašto per AUKŠTĮ (juostos viena virš kitos), tada link lapo galo.

v36: LED testas „Lietuva tėvyne mūsų": PDF tik su kontūrais (`fill_rgb: null`), diakritikai (`min_area_mm2`, taškai / brūkšneliai - prie raidės „3+1"), netelpantys moduliai šalinami (plonas „e" skersinis), užraitai / smailės nevertinami, tolerancija 5 %, grupės pagal plotį 1,5 x, papildomos eilės tik > 1,2 x žingsnio, ilgas užrašas - žodžiai eilutėmis.

v35: LED MAITINIMAS per VIENĄ tašką grupei nurodytoje vietoje (`feed_at`), viršijus tiekėjo grandinės ribą - neskaidoma, pastaba „stipresnis PSU kompensuoja įtampą" (Rytis 2026-10-09).

v34: LED COOP ALT8869 - grupės žingsnyje raidė gali imti p - 10 („~p", mažiau modulių), lape žingsnių intervalas (pvz. 120-170 mm).

v33: LED 24V moduliai P320L / P170L / P120 ir NAUJESNĖ tiekėjo P320L lentelė - 3 žingsniai / ryškumai kiekvienam gyliui 80-200 mm (`references/led_lens.md`, `assets/led_lens.json` `modules_24v` / `lux_table_24v`); šviesdėžės skaičiuoklė `scripts/led_box.py` (visi tiekėjo variantai, tinklelis, vnt., W, ~lx, grandinės).

v32: LED pagal GAMYBOS PAVYZDŽIUS (Rytis 2026-10-09, `references/led_gamybos_pavyzdziai.md`, `assets/led_pavyzdziai/`): aplink modulį apskritimas = žingsnis, statūs linijų galai - modulis per pusę žingsnio nuo krašto (linija dalijama nuo krašto iki krašto), smailėse modulių nėra, kiekis virš raidės; ploto tolygumo riba - viena eilė 1,25 x žingsnio pločio linijoje.

v31: LED - KIWI order 225955: žingsnis PAGAL LINIJOS PLOČIO GRUPĘ (±30 %), MODULIS PAGAL GRUPĘ (tinka tik telpantis >= 3 mm nuo šono; plačios raidės P190L, siauros / taškai P65L; vienas tipas, jei <= 10 % daugiau), skirtingi moduliai - atskiros grandinės; netelpantis modulis pastumiamas / pasukamas; 2 lapo žemėlapis - pagal raidės vidurkį.

v30: LED IŠDĖSTYMAS PERRAŠYTAS NUO 0 - apšviestumo simuliacija `scripts/led_sim.py`, `references/led_sim.md`; senas `led_layout.py` / `led_lens.py` ištrinti.

v29: EXTRA order 225978 (Rytis 2026-10-08): P1 NEŠVIEČIANČIOS raidės ant bėgelių `"front": "P1"` - priekis Alu 2 mm RAL, šonai Alu 1, dugnas PVC 10, be LED / plexi / A-B, pjūviai `lapas_core.p1_typical` (juosta + DETAIL A X ant plokštės); `"power_note"` (užrašas be laidų); pasviręs statmuo po VIENU stiebu (`"single": true`, pvz. „7"); STOGO ATRAMOS - atskiras lapas `scripts/projektai/extra_225978/roof_sheet.py` (kojos □30x30x2, kicker ~45° prie viršutinio bėgelio, plokštė 120x120x5, vėjas EN 1991-1-4); DETAIL A „30 / 25" užrašai 8 pt.

v28: SPAR TYPE 670 (Rytis 2026-10-08): folded fonas iš KELIŲ DALIŲ `"panel_joints": [x_mm]` - kiekviena dalis savo L viršus+apačia ir varžtai, „PANEL JOINT" - TIK pastaba UŽ reklamos ribų (ne ant fasado / raidžių); DETAIL A braižomas pagal `front` (P6_8mm - plexi 8 su frezuota briauna, be PVC ir A/B); LAIDAS folded fone - TIK iš raidės galo (D11) -> už fono -> pro Ø11 skylę UŽLENKTOJE BRIAUNOJE kliento nurodytoje vietoje ir įtampa (`"cable"`), laidas 0,9 pt raudonas (ne hairline); projektas `scripts/projektai/spar_type670/`.

v23-v27: LED dėliojimo bandymai - IŠTRINTI (Rytis 2026-10-08: netinkami, pradėti nuo 0).

v22: VIENAS ŠALTINIS - paskyroje tik paleidiklis (`references/paleidiklis_SKILL.md`), kuris kaskart ima iCloud zip; paskyros nebeatnaujinti.

v21: LED DĖLIOJIMAS - Lens moduliai P65L / P130L / P190L: `references/led_lens.md`, `assets/led_lens.json`, skaičiuoklė `scripts/led_lens.py` (žingsnis, lx, kiekis, W, grandinės).

v20: PDF -> CorelDRAW: tekstas lieka TEKSTU - šrifto vardas PDF'e „GOST Common" (`lapas_core.pdf_fix_fonts`, automatiškai `K.save` ir `braizyti_lapa`); patikrinta CorelDRAW 2026.

v19: ETALONAS - SPAR order 225960 komplektas (18 lapų) = SPAR etalonas ir pagrindas daugumai dokumentų: `references/etalonas_spar_225960.md`, `assets/etalonai/SPAR_225960_komplektas_18_lapu.pdf`, kodas `scripts/projektai/spar_225960/`.

v18: ŠRIFTO DYDŽIAI visur pagal taisyklę - pagr. matmenys 12 pt, kiti >= 8 pt, vaizdų pavadinimai 13 / mastelis 9, juostos eilutė 11 pt; netelpantis tekstas NEmažinamas < 8 pt - skriptas spausdina „! NETELPA", trumpinti tekstą; folded lapas naudoja lapas_core BOM / MAIN DATA.

v17: BOM - VISI plėvelių kodai (ORACAL, Avery, PMS, 3M, sandblast) spalvotame langelyje, FINISH ir MATERIAL stulpeliuose, `lapas_core.FOIL` / `code_hex`.

v16: bėgelis neišsikiša už pirmos raidės (S) kontūro ir logotipo apskritimo; portalo viršus iš 2 dalių su DETAIL C.

v15: LAIDAS - raudona stora ištisinė linija (`K.CABLE`, `K.cable_line`), nesutampa su matmenų išvadinėmis / balionais; `cable: false`; trafo box - po iškaba; BOM MATERIAL platesnis, MAIN DATA siauresnis; dekoras be fono.

v14: laidai 12V 3 m, prie dėžės tik „220V"; `joints` - rėmo sujungimo punktyras; bėgelis neišsikiša už apskritimo; KAFFEPAUSE kompozitas = apskritimas + rėmo atkartojimas (`logo_replica`); folded BOM / antraštė - naujas stilius; decals po raidėmis, jei grupė `behind`.

v13: laido išvestys ir ausėlės TIKSLIAI pagal kliento failą - `cable.x_pt`, `cable.out`, `ears_pt`, `ears: false`; folded `callouts`, `cable_exit`. v12 = v11 + Ottersøy 2-oji pataisa: SPAR 2 dalys - tik horizontalūs bėgeliai, jungtis tarp A ir R;
laido išvestis `cable.rail: "top"`; `decals` 3D su skylėmis; PANT - vientisa reklama ant vieno rėmo, apskritimas -
balta plexi + pjaustyta plėvelė; back plate 1 arba 2 dalys, varžtų skylių grandinė
