---
name: "reklama"
description: Rytio iškabų gamybos techninė dokumentacija - iš kliento PDF/DXF ir trumpo aprašymo (pvz. "P6 ant folded pl., 40mm, RAL9010") sugeneruoja A3 techninį lapą etaloniniu CAD stiliumi ir patikrina gamybos tinkamumą. Etaloninis lapo stilius galioja VISIEMS produktams (raidės ant folded plokštės, raidės ant sienos / bėgelių, pylonai, šviesdėžės, plokščios iškabos). Naudok VISADA, kai pokalbyje yra iškaba, tūrinės/šviečiančios raidės, profilis (P6, Profile 6 ir kt.), folded pl. / lankstyta plokštė, plėvelė / vinilas (sunaudojimas, ploteris), pylonas, šviesdėžė, RAL spalvos, raidžių storis, tvirtinimas, LED, D3.2/D11, arba užklausoje yra kliento raktažodis (SPAR, EXTRA, Clas Ohlson, OKQ8, Skyltkoncept, BrandFactory), arba vartotojas įkelia kliento logotipo ar iškabos PDF ir prašo brėžinio, matmenų, specifikacijos ar pasiūlymo - net jei žodis "skill" ar "lapas" neištartas.
---

# Iškabų techninis lapas

**Versija: 2026-10-12 v132** (v132, Rytis 2026-10-12: „LED dėliojama lovyje ... įdėjus į tūrį kampas blokuoja šviesą" - `ilp()`: taškas apšviestas tik jei linija modulis -> taškas (iš viršaus) eina raidės viduje (sienelės užstoja), visas veidas iki sienelės (0,03 p) turi matyti modulį <= 0,85 p; testuose išdėstymų nepakeitė - laukiama Ryčio patikslinimo, kurios vietos nešviečia. v131, Rytis 2026-10-12: „vistiek keletoje vietų nedėti LED, nors jie ten turėtų būti ... rekomenduok gamybos lygio sprendimą" -> „bandyk": `led_km.py ilp()` NUMATYTAS - LED išdėstymas kaip aprėpties optimizavimas (HiGHS): kiekvienas raidės taškas <= 0,6 p nuo modulio, moduliai >= 0,75 p vienas nuo kito, mažiausiai modulių, arčiau ašies; tuščių vietų nelieka. v130, LED testas „Alltid öppet" (Rytis 2026-10-12, P6, gylis 80): LED lape kiekis raidei, virš kurios yra kita forma (ö / i taškai) - rašomas PO raide, kad nesidengtų. v129, Rytis 2026-10-12: „vistiek dėliojimas labai keistas, neatitinka nei gamybinių, nei teorinių planų" - `led_km.py pack()` NUMATYTAS: APSKRITIMŲ PAKAVIMAS kaip Ryčio gamybos lapuose - Ø = žingsnis, apskritimai raidės viduje liečia vienas kitą ir kraštus, galas - apskritimas liečia raidės galą, siaura linija - ašyje; po to tolygus išdėstymas (stūmimas); senas `chain` + `coverage` - tik spec `"layout": "chain"`. v128, Rytis 2026-10-12: „taisyklės tik rekomendacijos ... labiau žiūrimas švietimo padengimas ... švietimas turi būti tolygus miksuojant taisyklių ir formos algoritmą" - `led_km.py coverage()`: po taisyklių išdėstymo - šviesos modelis veide, tamsios dėmės užpildomos papildomais moduliais, moduliai pastumiami tolygumui, perteklius šalinamas; `led_km.py spec.json out.pdf patikra.png` - švietimo patikros vaizdas. v127, Rytis 2026-10-12: LED - NAUJA VERSIJA pagal gamybos failus: Kaisen Electric kainoraštis + ryškumo (Depth) lentelės `assets/kaisen_led.json`; `led_km.py` modulis pagal gylį (KM-P0 / P1 / P2 0,72W / P2 1W / P3 / P4, raudoni KM-P*-R, plonos linijos MINI3), žingsnis - didžiausias su >= 2200 lx, PSU Kaisen KPS IP67 <= 75 %; BaltLED / Lens - nenumatyti. v126, Rytis 2026-10-12: „kodėl čia taip keistai nepridėti LED?" (A kojos, 7 kampas tušti) - `led_km.py` grandinė: galinis modulis p/2 nuo krašto NEŠALINAMAS dėl sankirtos, aštrus lenkimas (>= 45°) - mazgas su moduliu, šaka galas -> mazgas dalijama lygiai; plonos linijos - žingsnis <= 1,6 x linijos plotis; laidas - artimiausias kaimynas + 2-opt. v125, Rytis 2026-10-12: „P120 klaida. naudojami LED moduliai ir transformatoriai iš https://baltled.com" - `led_km.py` moduliai ir PSU iš `assets/baltled_led.json` (BaltLED katalogas): raidėms < 30 MINI HE, 30-49 PRISMA S1+, 50-100 PRISMA S2+ (= KM-P2 0,72W), 101-125 S3+, > 125 S4+; PSU BaltLED BPS (IP67, 12V, apkrova <= 75 %); Lens lentelė (`led_lens.json`, P65L / P130L / P190L / P120 ...) - NE mūsų tiekėjas. v124, Rytis 2026-10-12 patvirtino DĖLIOJIMO PRINCIPĄ (plevele_test 1190): grafika netelpa į rulono plotį -> skaidoma į VISUS bendrus objektus (užrašo eilutė, automobilis, kiekvienas dušas; riba - ryškus tarpas >= 3 x tarpų mediana) ir jie sudėliojami kompaktiškai (pvz. dušai pasukti šalia užrašo); telpa - visa, neskaidant; `plevele.logical_objects`. v123, Rytis 2026-10-12, plėvelės testas OKQ8 „Alltid öppet“: `plevele.py` - visa grafika viename compound path skaidoma į salas (skylės - even-odd), objektas kito viduje (rato centras) - kartu, diakritikai tik prie teksto eilučių; testas `scripts/projektai/plevele_test/`. v122, Rytis 2026-10-12: PLĖVELĖ - UŽRAŠAS VIENOJE LINIJOJE NESKAIDOMAS (nei į žodžius, nei į raides) vien taupant plėvelę: gamybininkui klijuoti kelias dalis į vieną liniją, matuoti tarpus - brangiau už plėvelę ir klaidų rizika; `plevele.text_lines`. v121, Rytis 2026-10-12: PLĖVELĖ SKAIČIUOJAMA PAGAL SUNAUDOJIMĄ (rulono darbinis plotis x ilgis), ne pagal grafikos plotą; spalvota 1190 mm (standartas), balta / spauda 1320 mm, 1500 mm - tik išimtis su pastaba; pjaustymo failas - forma skaidoma kuo mažiau: telpa - visa, netelpa - tik bendrais objektais; `scripts/plevele.py`, skyrius „Plėvelė - sunaudojimas ir pjaustymo failas“. v120, Rytis 2026-10-12: `led_km.py` moduliai - IŠ MŪSŲ LED LENTELĖS (`assets/led_lens.json`: 12V P65L / P130L / P190L, 24V P120 / P170L / P320L), raidėms numatyta P120 0,72W 24V (gylis < 50 - P65L); lape LED IMITACIJA - modulio korpusas su LED pagal ašies kryptį + grandinės laidas + apskritimas. v119, Rytis 2026-10-12: „led dėliojimas vis dar blogas“ - NUMATYTAS LED įrankis `scripts/led_km.py` (Kaizen KM-P2 HE 0,72 W / KM-P2-R, viena eilė per ašį, žingsnis pagal gylį 50->100, 70->120, 80->130, 100->140, apskritimas = žingsnis, galai p/2 nuo krašto, PSU KPS <= 75 %); Lens `led_sim.py` - tik paprašius; pavyzdžiai `assets/led_pavyzdziai/*_v2.jpg`, `*_RYCIO.jpg`. v118, Rytis 2026-10-12: PLOKŠTĖS PUSĖ DXF - pažymėti X tvirtinimo rėmai (H1800 60x60) -> vaizdas IŠ PRIEKIO (`--plate-front`); rėmo žymėjimo nėra (vienas rėmas FAS700 / FAS1000) -> plokštė veidrodiškai (iš galo) + **C žyma** galinėje pusėje (sluoksnis `5_C_ZYMA`), kad būtų aišku, kur priekis, kur galas. v117, Rytis 2026-10-12: EXTRA H1800 gamybos principas - X ant Ø1800 apskritimo su SAVO 60x60x2 X formos rėmu (įstrižainės per X šakų ašis), 8 x Ø3.2 ant profilio ašies + Ø11; EXTRA / 7-23 atskirai ant U30; `references/klientai/extra.md`, etalonas `assets/etalonai/extra_H1800_ALT8852_gamyba.pdf`. v116, Rytis 2026-10-12: P1 - inside kontūras (dugnas) 0,7 mm, be drenažo skylių ir be D11, nes LED nesideda (`p6_dxf.py --p1`; 1:1 PDF `back_inset_mm` P1 numatyta 0,7). v115, Rytis 2026-10-12: VIENAS RĖMAS - X (raidė ant plokštės) tvirtinimas kaip raidžių: Ø4 skylės ant bėgelio profilio HORIZONTALIOS AŠIES (`holes_on_rail`), D11 - apatinio bėgelio ašyje; plokštėje tos pačios skylės veidrodiškai; etalonas `assets/etalonai/extra_X_tvirtinimas_rems_asis.pdf`. v114, Rytis 2026-10-12: MEDŽIAGŲ BIBLIOTEKA - LT tiekėjų sandėliniai Alu profiliai (Heliopolis visas katalogas, Lankava Alytus, Proplastik Kaunas), Alu lakštai ir AKP formatai / RAL (Heliopolis, Proplastik, Plastena) `assets/medziagos.json` -> `profiliu_katalogas`; `medziagos.profile_check` / `sheet_check`, CLI `python3 scripts/medziagos.py profilis "U 30x30x2"`; rėmo / L / Z profiliai tikrinami automatiškai - nėra sandėlyje -> perspėjimas su artimiausiais, lape nerašyti be patvirtinimo. v113, Rytis 2026-10-12: DXF kontūrai - TIESĖS + LANKAI (LWPOLYLINE bulge, `--fit-tol 0.02`), ne tūkstančiai taškų - Corel be „Reduce nodes" (VH400: 8097 -> ~400 mazgų, nuokrypis <= 0,03 mm). v112, Rytis 2026-10-12: EXTRA DXF su PLOKŠTE - `p6_dxf.py --plate-fill` + kelių spalvų `--fill`: X atskirai kairiau apskritimo, apskritimas `4_PLOKSTE` su tomis pačiomis skylėmis veidrodiškai; etalonas `assets/etalonai/extra_darbiniai_DXF_pateikimas.pdf`. v111, Rytis 2026-10-12: LAPE PAŽYMĖTA, KOKIE LED KUR DEDASI - galiniame vaizde spec grupės `"led"`; etalonas `assets/etalonai/led_zymejimas_galiniame_EXTRA_223315.pdf`. v110, Rytis 2026-10-12: šaltinis - GitHub repo `rytiunia/ai_asistentas` vietoj iCloud zip. v109, EXTRA 225978 patvirtinimas: `braizyti_begeliai.py` - `rail_fills` spalvos blokai (statmens / kojos plotas) niekada ne raidės; spec `"client_vert_rails": false` - patvirtinto lapo statmenys nedubliuojami su spec `verticals`. v108, Rytis 2026-10-12: P6 DUGNAS - smailus raidės vidinis kampas (M viršus tarp kojelės ir įstrižainės) -> siaura įpjova nukertama: vietoj 1 taško 2, buki kampai (`K.dugnas_inset`, `--blunt-len 12`). v107, Rytis 2026-10-11: šviečiančių pilonų etalonas Prisma Skejby ALT8826 - `references/etalonas_pilonas_prisma_alt8826.md` (plieno / Alu rėmas, šviesdėžės „žvynais“, plexi įdėklai, padai, kėlimo ąsos). v106, Rytis 2026-10-11: KLIENTO RĖMAS NETVARKINGAS (ne per tvirtinimo ploto centrą, per trumpas, trūksta / per daug bėgelių, ne pagal standartą) - PERDAROMAS PAGAL SKILL (auto rėmas), nebent nurodyta naudoti kliento struktūrą - spec `"client_frame": true`. v105, Rytis 2026-10-11: patvirtinimo pakete siųsti TIK PDF su maketu, PDF su LED ir vientisus DXF (be failų po raidę); `reklama.zip` vartotojui nesiųsti (nuo 2026-10-12 - tik commit į GitHub). v104, Rytis 2026-10-11: „Patvirtinta, ALT…“ -> gamybos paketas: lapas su ALT numeriu + DXF 1:1 + LED lapas - `references/patvirtinimas.md`; `led_sim.py` `page` ir `feed_at: letter:N-top`; `p6_dxf.py` praleidžia < 20 mm kontūrus. v103, Rytis 2026-10-11: SUTARTINIS UŽRAŠAS - rėmo apraše „+ hangers“ (pvz. „frame 30x30x2mm + hangers RAL 7024“) = U laikikliai, „+ ears“ = ausėlės; skriptas `mounting` ima iš rėmo aprašo, jei spec jo nenurodo. v102, Rytis 2026-10-11: „rėmas su hangers“ = U laikikliai (`"mounting": "brackets"`); lape angliškai HANGER (BOM „Hanger U ...“, MAIN DATA „+ hangers“, 2 lapas „Hangers (U)“), ausėlės lieka „ears“; bėgelio eilutė BOM lieka. v101, Rytis 2026-10-11: P6 DXF `3_REMAS` - rėmas KARTU su ausėlėmis (kontūras + Ø6 skylė) ir U laikikliais (su skylėmis), įstrižai bėgeliai - tikru poligonu. v100, Rytis 2026-10-11: MAIN DATA be „Wall" (tik kai fasadas ne įprastas) ir be „Drainage"; BOM „Letter back" spalva = šonų spalva (kitokia - tik nurodžius, `back_ral`). v99: drenažo Ø8 skylutė VISA dugno viduje; rėmo matmenys apvalūs - 5 mm žingsniu (3017 -> 3020, 17 -> 15). v98: 6 m strypai visam užsakymui (qty); exterior DXF su Ø8 drenažu. v90-v97 (P6 priekiai, montavimas: ausėlės / U laikikliai / atskiros raidės, statmenys per raidžių centrą + įstrižas ant A, > 6 m bėgelis trumpinamas, viena ausėlė rėmo gale, POWER) ir ankstesnės - `references/versijos.md`.)

**!!! VIENAS ŠALTINIS - GitHub repo `rytiunia/ai_asistentas`, aplankas `reklama/` (nuo 2026-10-12; iCloud zip'ai archyvuoti) !!!**
1. Pilnas skill'as (SKILL.md + `scripts/`, `assets/`, `references/`) - https://github.com/rytiunia/ai_asistentas , `reklama/`.
   Paskyroje (Claude) - tik paleidiklis (`references/paleidiklis_SKILL.md`); paskyroje likę seni failai - NENAUDOTI.
2. Prieš darbą: `add_repo` (rytiunia/ai_asistentas) -> `git clone --depth 1` (ar `git pull --ff-only`) -> dirbti TIK iš klono.
3. Repo nepasiekiamas - PRIEŠ darbą pasakyti Ryčiui (prijungti GitHub arba įkelti aplanką zip'u į pokalbį).
4. Atsakyme VISADA nurodyti versiją ir commit'ą (pvz. „reklama vNN, GitHub abc1234").
5. Pakeitus skill'ą: pakelti „Versija", `git pull --rebase`, commit (žinutė „reklama vNN: ...") ir `git push` į `main`.
   Zip'ų ir `_archyvas` nebereikia. Failų vardai - tik ASCII.

Vartotojas: Rytis, iškabų gamyba Lietuvoje. Su juo kalbėk lietuviškai, tiesiai, be komplimentų.
Lapo užrašai - angliškai.

**Trys pagrindinės taisyklės:**
1. **Nieko neišgalvok.** Ko nėra aprašyme, kliento faile ar šiame skill'e - lape palik tuščią vietą
   ir paklausk. Neteisinga reikšmė gamyboje kainuoja daugiau nei klausimas.
2. **Etaloninis stilius visiems produktams.** Bet kokio tipo lapas daromas pagal
   `references/stilius.md` (PRIVALOMA perskaityti) ir atrodo kaip `assets/etalonai/*.pdf`.
3. **ETALONAS - SPAR order 225960 (Rytis patvirtino 2026-10-08).** Tai SPAR / BrandFactory užsakymų etalonas ir
   lapo STILIAUS PAGRINDAS VISIEMS dokumentams (kelių pozicijų komplektai, ne iškabų lapai, laidai, BOM, šriftai):
   PRIVALOMA perskaityti `references/etalonas_spar_225960.md`, lapai -
   `assets/etalonai/SPAR_225960_komplektas_18_lapu.pdf`, kodas - `scripts/projektai/spar_225960/`.
   Naujame užsakyme pirmiausia žiūrėti, kaip analogiška pozicija padaryta etalone.
   Keičiasi tik produkto turinys, ne lapo stilius.
4. **Bendrinės taisyklės + kliento raktažodis** (žr. žemiau). Produkto tipo taisyklės galioja visiems klientams;
   kliento taisyklės - tik kai užklausoje yra to kliento raktažodis.

## Bendrinės taisyklės ir klientų raktažodžiai (v43)

**Bendrinės (visiems tokio tipo užsakymams, nepriklausomai nuo kliento)** - šiame faile, „Produktų moduliai":
| Produkto tipas / raktažodis užklausoje | Skyrius |
|---|---|
| folded pl. / folded plate / lankstyta plokštė / back plate | „Folded plate - bendrinės taisyklės" |
| folded + raidės (P6, P8 ...) | „Folded plate" + „P6 raidės ant folded plokštės" / „Kito profilio raidės ant folded" |
| folded + oracal / plėvelė / vinilas / grafika | „Folded plate + pjaustyta plėvelė" |
| plėvelė / vinilas / oracal / avery / 3M / lipdukas / spauda - kiekis, m², ploteris, pjaustymo failas | „Plėvelė - sunaudojimas ir pjaustymo failas" (PRIVALOMA BOM) |
| P6_3mm / P6_8mm / P6 color / +foil | „P6 priekio variantai" (+ modulis pagal foną) |
| P6 dxf / CNC failai raidėms / tvirtinimo skylės / D3.2 / D11 / gręžimas | „P6 DXF - stiklas, dugnas, rėmas, tvirtinimo ir laido skylės" |
| P6 ant bėgelių / rails / U / wallframe, P6+3 ant plokštės | „P6 raidės ant U bėgelių ..." + „Bėgeliai ir ausėlės" |
| be ausėlių / U laikikliai / laikiklis / atskiros raidės / be rėmo / WAGO / 12V 1,5 m | `references/moduliai_montavimas.md` (PRIVALOMA) |
| one frame / vientisas rėmas / bėgis per apskritimą | „Bėgeliai ir ausėlės" -> „VIENTISAS RĖMAS" |
| □ profilis / square | „P6 ant stačiakampio Alu profilio" |
| P1 / nešviečiančios | „P1 nešviečiančios raidės ant bėgelių" |
| stogas / roof / kojos | „Stogo iškaba - atramos" |
| pylonas / pilonas / totem / stovas / piloniukas / pagrindo plokštė / flanšas | `references/moduliai_pilonai.md` (PRIVALOMA) |
| LED / Lens / šviesdėžė | „LED - Lens moduliai" |
| trafo / laidas | „Maitinimas - TRAFO BOX" |
| išklotinė / flat / dxf / nesting | „Folded plate" -> „Išklotinės ir DXF", „Nesting" |
| 3D / vizualizacija ant fasado | „3D (r3d)" |
| senas brėžinys perdaryti | „Senų brėžinių perdarymas" |
| 6 m / strypas / profilių ilgis / tiekėjas (Heliopolis, Plastena) / lakšto formatas / netelpa į lakštą | „Medžiagų formatai ir 6 m strypų taisyklė" |

**Kliento raktažodis -> PRIVALOMA perskaityti kliento failą** (ten tik to kliento papildymai / išimtys; jei kliento
taisyklė prieštarauja bendrinei - galioja kliento, bet tik tam klientui):
| Raktažodis (užklausoje, kliento faile, užsakovas) | Kliento failas | Projektų kodas |
|---|---|---|
| SPAR, BrandFactory (be kito kliento vardo), KAFFEPAUSE, Ottersøy, Sundvollen 226004 | `references/klientai/spar_brandfactory.md` + `references/etalonas_spar_225960.md` | `scripts/projektai/spar_225960/`, `spar_type670/`, `spar_226004/` |
| EXTRA, Coop Extra, FAS ..., darbo valandos, H1800 / 225818 / ALT8852 (X ant 60x60 X rėmo) | `references/klientai/extra.md` | `scripts/projektai/extra_225978/` |
| Clas Ohlson, CO, Horten, ALT8857, P8 special | `references/klientai/clasohlson.md` | `scripts/projektai/clasohlson_horten/` |
| OKQ8, Q8, Skyltkoncept, Väster | `references/klientai/okq8_skyltkoncept.md` | `scripts/projektai/okq8_vaster/` |
| Joker (BrandFactory), Joker order 226001 | tik bendrinės | `scripts/projektai/joker_reinslettveien/` |
| Prisma Properties Skejby, ALT8826, Order 2439 (šviečiantys pilonai 8,8 m / 5 m) | `references/etalonas_pilonas_prisma_alt8826.md` | - |
| CEOS Groupe, Thales, D059422 (pilonai, PMMA planas) | tik bendrinės (`references/moduliai_pilonai.md`) | `scripts/projektai/thales_d059422/` |
| POWER, Imagon, Brotorvet | tik bendrinės | `scripts/projektai/power_brotorvet_3a/` |
| COOP, KIWI, MATKROKEN, Alytus ir kt. (be atskiro failo) | tik bendrinės + `assets/spec_*.json` pavyzdžiai | - |
Naujas klientas su savo standartu -> naujas `references/klientai/<klientas>.md` + eilutė šioje lentelėje. Bendrinę
taisyklę, kurią Rytis pasako dirbant su konkrečiu klientu, rašyti į BENDRINĮ skyrių (jei ji apie produkto tipą), o
į kliento failą - tik tai, kas būdinga klientui (spalvos, standartinės konstrukcijos, laido vieta, užsakovo duomenys).

## Įvestis

1. Kliento PDF (dažnai Illustrator / CorelDRAW, NE 1:1, mėgėjiškas, kartais ne vektorinis,
   kartais be jokių matmenų).
2. Trumpas aprašymas santrumpomis (žr. žodynėlį). Aprašymas svarbesnis už kliento failo vaizdą
   (spalvos, profilis) - neatitikimą paminėk atsakyme.

## Darbo eiga

1. **Mastelis.** Rask kliento matmenis ir didžiausią elementą (foną):
   `python3 scripts/matuoti.py <pdf> --ref-mm <fono plotis> [--min-stroke N]` (arba `--scale` mm/pt).
   Patikrink kitus kliento matmenis (±2 mm). **Jei faile matmenų nėra - PRIEŠ braižant paklausk
   mastelio ar vieno matmens.** Magenta trikampiai - matmenų rodyklės, ignoruok.
2. **Iššifruok aprašymą** (žodynėlis): produkto tipas, profilis, gylis, spalvos, fonas, tvirtinimas.
2a. **Kliento raktažodis** (lentelė aukščiau): jei yra - perskaityti kliento failą `references/klientai/...`.
    Bendrinės produkto taisyklės galioja visada.
3. **Gamybos patikra:** aukščiai, pločiai, min. linijos storis (raidėms per raides), tarpai,
   ar centruota. Per ploni elementai -> siūlyk sprendimą su skaičiais.
4. **Lapas.** Nustatyk produkto tipą (žr. „Produktų moduliai"):
   - **P6 ant folded plokštės** - įgyvendinta: nukopijuok `assets/spec_pavyzdys.json` (stačiakampis)
     arba `assets/spec_extra.json` (ne stačiakampis, `"scale"`), užpildyk, nežinomas reikšmes rašyk `?`:
     `pip install pymupdf shapely --break-system-packages`
     `python3 scripts/braizyti_lapa.py spec.json /mnt/user-data/outputs/<failas>.pdf`
   - **Kitas produkto tipas** - generatoriaus modulio dar nėra. Naudok tą patį skriptą kaip
     bibliotekos pagrindą (rėmelis, apatinė juosta, lentelės, matmenys, hairline, išdėstymo parinkimas,
     3D) ir pakeisk tik produkto dalis: vaizdų turinį, tipinį pjūvį, detalę A, BOM eilutes ir kiekių
     formules. Konstrukcijos detalių (tvirtinimas, medžiagos) PIRMA paklausk Ryčio. Kai modulis
     patvirtintas - įrašyk jį į skill'ą kaip naują produkto modulį.
4a. **1:1 failas (Rytis 2026-10-07):** prie techninio lapo VISADA atskiras PDF `<failas>_1-1.pdf` - tik raidžių
   (ir plokštės) kontūrai 1:1 (hairline, kreivės iš kliento failo), be matmenų, rėmelio, bėgelių, užrašų.
   TRYS atskiri sluoksniai (PDF OCG), skirtingos spalvos: 1_LETTERS (juoda, kreivės iš kliento failo),
   2_BACK_inset_3mm - dugnas 3 mm į vidų nuo raidžių (raudona, `back_inset_mm`), 3_FRAME - bėgeliai, statmenys,
   ausėlės su Ø skyle (mėlyna).
   `braizyti_begeliai.py` daro automatiškai (`"export_1to1": false` - išjungti).
4b. **P6 DXF su tvirtinimo ir laido skylėmis (v66, Rytis 2026-10-09):** kai prašoma DXF / CNC / gręžimo failų P6 raidėms -
   **Ryčiui atiduodamas VIENAS DXF failas** (visa iškaba 1:1, `--no-letters`, laido variantas pagal užsakymą `--cable bottom|top`;
   v86, Rytis 2026-10-10: „dxf vienas failas, ne išskaidytas"); failai po raidę ir abu laido variantai - tik paprašius.
   `python3 scripts/p6_dxf.py <kliento.pdf> <out_dir> --scale 1 --names TESTAS --prefix <užsakymas>` (žr. modulį
   „P6 DXF"). Visada peržiūrėti `<prefix>_patikra_laidas_*.png` ir atsakyme pateikti skripto perspėjimus (`!`).
5. **Patikra akimis:** VISADA išrenderink PNG (`pdftoppm -r 80 -png`) ir palygink su etalonu:
   ar niekas nepersidengia, ar nėra didelių tuščių plotų, ar kontūrai hairline.
6. **Atsakymas:** mastelis ir patikrinti matmenys; elementų lentelė (aukštis, plotis, min. storis);
   ką priėmei pats; tikslūs klausimai tik apie tai, kas tikrai neaišku.

## Produktų moduliai (BENDRINĖS - visiems klientams)

### P6 priekio variantai (galioja visiems P6 moduliams; spec `"front"`)
**Vaizdavimas (v59, Rytis 2026-10-09, tikslas >= 95 % realaus vaizdo):** STIKLAS = ORIGINALUS kliento failo kontūras,
matomas stiklo kraštas 3 mm (P6_8mm frezuojama taip, kad kraštelis liktų 3 mm); KORPUSAS (šonai) 1,5 mm MAŽESNIS už
stiklą (offset -1,5), gylis - 3. +foil variantuose šoniniame vaizde ir 3D matosi: korpuso spalva | BALTAS stiklo
kantelis 3 mm | plėvelės spalva priekyje (color variante kantelis = plexi spalva). Kodas `scripts/p6_vaizdas.py`
(`layers`, `add_3d` r3d scenai, `side_view`, `rear_view` - galiniame vaizde dugnas 1,5 mm mažesnis už stiklą, aplink matosi stiklo kraštas); bandymas - `scripts/projektai/p6_vaizdas_test/s_demo.py` (S, P6_3mm+foil).
Taikoma VISUOSE projektuose automatiškai (v60): `braizyti_begeliai.py` (`P6_REAL`) ir `braizyti_lapa.py` šoninis vaizdas
ir 3D; lape papildomų aprašymų apie tai NEDEDAMA - tiesiog taip atvaizduojama. P1 / „behind" / plokšti elementai - kaip anksčiau.

Užklausoje nurodoma priekio kodas (v90, Rytis 2026-10-11; vienas parseris visiems skriptams - `scripts/p6_front.py`):
| Kodas | Priekis (1) | Konstrukcija (A / B) | BOM priekio eilutė |
|---|---|---|---|
| `P6_3mm` | balta plexi 3 | PVC 3 mm bortelis, varžtas per šoną į bortelį | `Acrylic 3 mm white`; A `Fitting PVC edge` |
| `P6_3mm+foil` | balta plexi 3 + plėvelė | kaip 3mm | `Acrylic 3 mm white` + `Front foil <kodas>`; A |
| `P6_3mm color` | spalvota plexi 3 | kaip 3mm | `Acrylic 3 mm <spalva>`; A |
| `P6_8mm` | balta plexi 8 | frezuota su kanteliu (matomas kraštelis 3 mm, liežuvis korpuse), varžtas per šoną į liežuvį | `Acrylic 8 mm white`; A/B eilučių NĖRA, PVC NĖRA |
| `P6_8mm+foil` | balta plexi 8 + plėvelė | kaip 8mm | `Acrylic 8 mm white` + `Front foil <kodas>` |
| `P6_8mm color` | spalvota plexi 8 | kaip 8mm (tik spalvota) | `Acrylic 8 mm <spalva>` |
| `P6_10mm` / `15mm` / `20mm` / `30mm` (+foil) | balta plexi 10-30 (+ plėvelė) | frezuota su kanteliu kaip 8mm (liežuvis = storis - 3) | `Acrylic N mm white` (+ `Front foil`) |
Spalvota - tik 3 ir 8 mm, kiti storiai - tik balta (su plėvele arba be); kitaip skriptas perspėja. Kantelis baltas visada,
išskyrus `color`. Konstrukcijos tipas brėžiniams: 3 mm -> PVC (`"3mm"`), >= 8 mm -> frezuota (`"8mm"`); svoris - pagal tikrą storį.
Pjūvis (`p6_typical` / `p6_reference`) ir lupa braižomi pagal tipą; 8 mm konstrukcijos šaltinis -
`assets/konstrukcijos/p6_8mm_plexiglass.pdf`. Gylis matuojamas iki plexi priekio.
**Medžiagos (v90):** storiai `assets/svoris.json` - standartas (šonai Al 1, nugara Al 1,5), bet būna ir nestandartinių -
užsakyme nurodytus rašyti spec `"thk_mm"` ir BOM; kitos medžiagos galimos. **Varžtai** - tik teorinė dalis (tipinė vieta /
žingsnis); galutinę vietą nustato gamybininkas.
**Montavimas (v90):** spec `"mounting"`: `"ears"` (standartas, be nurodymo - visada), `"brackets"` (U laikikliai = **HANGERS**. SUTARTINIS UŽRAŠAS (Rytis v103): rėmo apraše „+ hangers“ -> šis režimas, „+ ears“ -> ausėlės; MAIN DATA Rails tekstą rašyti „... + hangers, RAL ...“, tada `mounting` nustatomas automatiškai; be ausėlių,
2 lapas - laikiklio brėžinys), `"none"` (atskiros raidės be rėmo, `"letters_power"`: `per_letter` / `wago`) ->
`references/moduliai_montavimas.md` (PRIVALOMA). **Įtampa / laidas nenurodyti - KLAUSTI** (standartai: 220V 1,5 m;
12V 1,5 m; 12V + TRAFO BOX).

### P6 DXF - stiklas, dugnas, rėmas, tvirtinimo ir laido skylės (v66, Rytis 2026-10-09; `scripts/p6_dxf.py`)
Iš kliento PDF (raidės + pilki bėgeliai) - 1:1 DXF gamybai (CNC / lazeris / Corel), mm, y aukštyn, uždaros LWPOLYLINE
(kreivės 0,01 mm), skylės CIRCLE. `pip install pymupdf shapely ezdxf matplotlib --break-system-packages`
`python3 scripts/p6_dxf.py klientas.pdf out_dir --scale 1 --names TESTAS [--prefix X] [--rail 30] [--cable both] [--no-letters]`
(`--ref-mm` - raidžių grupės plotis, jei PDF ne 1:1; failas 1 pt = 1 mm -> `--scale 2.8346`; v97: kliento lapas su keliais vaizdais -> `--crop x0,y0,x1,y1` (kaip spec `crop_pt`) ir `--fill r,g,b` (kaip `client_fill`), kitaip į raides patenka kitų vaizdų elementai). **Rėmas iš lapo (v85):** kai rėmas
sudarytas `braizyti_begeliai.py` (auto rėmas, `merge_rows`, pakopos) - `RAILS_JSON=rails.json python3 scripts/braizyti_begeliai.py spec.json lapas.pdf`,
tada `p6_dxf.py klientas.pdf out --rails-json rails.json` (v90: atskiros raidės `"mounting": "none"` - JSON su `"separate"`, bėgeliai tik skylių ašys, `3_REMAS` nėra, D11 vienoje linijoje, failas `_laidas_linija.dxf`) - bėgeliai ir galai TOKIE PAT kaip lape, vertikalūs (statmenys, akcentų
laikikliai) - į `3_REMAS`; kelios eilutės - raidės eilutėmis, D11 viršus / apačia - pagal tos raidės eilutės bėgelius; akcentui
(Ė taškas, Ū brūkšnys) - 2 varžtai ant laikiklio ašies + D11 centre (>= 25 mm), netelpa - perspėjimas. Išeiga: `<prefix>_P6_1-1_laidas_virsus.dxf` ir `_laidas_apacia.dxf`
(visa iškaba, nulis - raidžių kairė apačia), failai po raidę `<prefix>_L01_T_laidas_*.dxf` (be `--no-letters`; nulis -
raidės kairė apačia, bėgeliai apkirpti ±30 mm) + patikros PNG (oranžiniai skrituliai - prispaudimo zonos R, tik PNG).
VISADA peržiūrėti PNG ir atsakyme pateikti perspėjimus (`!`) - jie rodo išimtis gamybai. Bandymai ir laukiami rezultatai -
`scripts/projektai/p6_dxf_test/` (TESTAS, Bandymas A / B / test_B). Parametrus keisti tik Ryčiui nurodžius.
- **TRYS SLUOKSNIAI, visuose failuose: `1_PRIEKIS`** juoda (ACI 7) - STIKLAS = ORIGINALUS kliento kontūras; **`2_GALAS`**
  geltona (ACI 2) - DUGNAS = kontūras `--inset` 3 mm į vidų iš visų pusių (kaip 1:1 PDF `back_inset_mm`; korpusas v59
  lieka -1,5) + Ø3.2 tvirtinimo skylės + Ø11 laido skylė; **`3_REMAS` RAUDONA (ACI 1)** - bėgeliai: kliento pilka grafika
  -> tikras profilio plotis `--rail` (U30 numatyta, 40 - nurodžius; nenurodžius - klausti), ašis išlaikoma (>= 11 mm nuo
  pilno aukščio raidžių krašto), galai 10 mm raidės viduje (`rail_edge`, kaip lape). Nėra bėgelių kliento faile ->
  skylių nėra, `3_REMAS` tuščias, pasakyti. Vertikalūs bėgeliai į DXF - tik su `--rails-json` (v85). Ausėlės (kontūras + skylė) ir U laikikliai (su skylėmis) - `3_REMAS` sluoksnyje kaip rėmo dalis (v101); `separate` režime jų nėra.
- **DUGNO SMAILŪS VIDINIAI KAMPAI - NUKERTAMI (v108, Rytis 2026-10-12, etalonas `assets/etalonai/p6_dugnas_smailus_kampas_M.pdf` - Joker
  MAN-FRE, pirma M raidė):** darant dugną (`--inset` 3 mm) smailiame raidės VIDINIAME kampe (tuštumos įlinkis - pvz. M
  viršuje tarp kojelės ir įstrižainės, A / V / W / N įlinkiai, smailios skylės kampai) mitre duoda ilgą siaurą įpjovą į
  dugną. Kai įpjovos smaigalys toliau nei ~11 mm nuo stiklo viršūnės (`--blunt-len 12`; 1:1 PDF spec `back_blunt_mm`) -
  kampas pakoreguojamas: vietoj vieno taško dedami DU - įpjova nukertama statmenai pusiaukampinei `inset` mm (3) už stiklo
  viršūnės, abu kampai BUKI vietoj smailaus. Trumpesnės (~11 mm ir mažiau, pvz. M vidurio V) ir statūs / buki kampai
  (E, F, L) - nekeičiami, raidžių išoriniai smaigaliai - taip pat. Funkcija `K.dugnas_inset()` (`lapas_core.py`) - ja
  naudoja `p6_dxf.py` ir `braizyti_begeliai.py` (1:1 PDF dugnas); kitur dugną daryti TIK per ją.
- **PLOKŠTĖ + RAIDĖ ANT JOS (v112, Rytis 2026-10-12, EXTRA X ant geltono apskritimo; etalonas
  `assets/etalonai/extra_darbiniai_DXF_pateikimas.pdf`):** `--plate-fill r,g,b` (plokštės spalva) + `--fill "r,g,b;r,g,b"`
  (visos raidžių spalvos). Plokštės spalvos forma su raide viduje = plokštė; be raidės - paprasta raidė (FAS1000 7-23 tos pačios
  geltonos). DXF'e: raidė ant plokštės ATSKIRAI, kairiau plokštės (`--plate-gap` 100) - `1_PRIEKIS` stiklas, `2_GALAS` dugnas
  -3 + Ø4 distancerių / varžtų skylės (`--spacer-d`, centre + po vieną kiekviename kampiniame ketvirtyje, >= 15 mm nuo dugno
  krašto) + drenažas + Ø11 laidui (apatinis ketvirtis pagrindinių raidžių pusėje, 25 mm virš distancerio; `--cable none` - be
  jo); plokštė `4_PLOKSTE` (mėlyna) su TOMIS PAČIOMIS skylėmis VEIDRODIŠKAI (plokštė iš galo). Kitos raidės - kaip įprasta
  (rėmas iš `--rails-json`, D3.2, D11). Vieno rėmo EXTRA lapams (FAS700 / FAS1000) DXF daromas VISADA - ne tik darbo laiko.
  **v118 (Rytis 2026-10-12) - PLOKŠTĖS PUSĖ:** kai plokštėje PAŽYMĖTI X tvirtinimo rėmai (H1800 - 60x60 X rėmas) -
  plokštė brėžiama VAIZDU IŠ PRIEKIO (`--plate-front`), nes rėmo žymėjimas iškart parodo pusę; kai rėmo žymėjimo NĖRA
  (vienas rėmas, FAS700 / FAS1000) - plokštė VEIDRODIŠKAI (iš galo) ir galinėje pusėje dedama **C tipo žyma** (atviras
  lankas R6, „C" skaitoma iš galo; plokštės centre, >= 15 mm nuo skylių; sluoksnis `5_C_ZYMA`) - kad būtų galima atskirti
  priekį nuo galo.
  **v115 (Rytis 2026-10-12): kai EXTRA ant VIENO RĖMO, X tvirtinimas atitinka raidžių tvirtinimą - skylės eina per rėmo
  profilio HORIZONTALŲ CENTRĄ** (kiekvieno bėgelio, kertančio X, ašyje; dalijimas kaip raidėms - prispaudimo R, >= hole_edge
  nuo dugno krašto); D11 - apatinio bėgelio ašyje pagrindinių raidžių pusėje, >= 25 mm nuo skylių. „Centras + 4 galai" -
  tik kai X bėgelių nekerta (ne vienas rėmas). Etalonas `assets/etalonai/extra_X_tvirtinimas_rems_asis.pdf`.
- **MAŽAI MAZGŲ (v113, Rytis 2026-10-12: „labai daug nodes ant lenktų linijų, reikia kiekvieną kartą paspausti reduce
  nodes"):** stiklas, dugnas ir plokštė rašomi kaip tiesės + lankai (`fit_ring()`, LWPOLYLINE su bulge), nuokrypis nuo tikro
  kontūro <= `--fit-tol` (0,02 mm). Niekada nerašyti išlygintų kreivių taškais (0,01 mm žingsniu). Bėgeliai / skylės - kaip buvo.
- **P1 (v116, Rytis 2026-10-12):** P1 raidėms INSIDE kontūras (dugnas) - **0,7 mm** į vidų (ne 3), **drenažo skylių
  NEREIKIA**, laido D11 - nėra (LED nesideda). `p6_dxf.py --p1` (= `--inset 0.7`, be drenažo, `--cable none`; failas
  `<ALT>_<lapas>_P1_1-1.dxf`); `braizyti_begeliai.py` 1:1 PDF - `back_inset_mm` P1 numatyta 0,7. Tvirtinimo D3.2 ant bėgelių - kaip P6.
- **DRENAŽAS - LAUKO REKLAMA (v98, Rytis 2026-10-11):** exterior raidė turi Ø8 išpjovą apatinėje dalyje - PAČIOJE
  ŽEMIAUSIOJE vietoje; kiekviena atskira „kišenė" savo (pvz. „a" - 3: viršutinės dalies užlenkimo apačia, pilvelis,
  kojelė; „m" - 3 kojelės; plokščia apačia - vidurys). `p6_dxf.py` - numatyta exterior (`2_GALAS` sluoksnyje), vidaus
  iškabai `--interior`; skersmuo `--drain-d`. **v99: skylutė NIEKADA neišeina už dugno linijos - visa dugno viduje, prie pat
  žemiausio taško (centras r + 1 mm virš kontūro); netelpa - perspėjimas.** Lape MAIN DATA „Drainage: Ø8 at lowest
  points (DXF)". Užsakyme nenurodyta, ar lauko - fasado iškaba laikoma exterior.
- **TRYS NEPRIKLAUSOMOS GRUPĖS (v70, Rytis 2026-10-09):** plokščias modelspace Corel'yje importuojamas kaip VIENA
  grupė - netinka. `group_layers()`: kiekvieno sluoksnio objektai - savo BLOCK `PRIEKIS` / `GALAS` / `REMAS`, įterpti po
  vieną kartą (0, 0) tame pačiame sluoksnyje (+ DXF GROUP tuo pačiu vardu). Corel importas - be „Convert reusable objects
  into symbols" (tada blokai - grupės). Taikoma ir visos iškabos, ir po raidę failams.
- **TVIRTINIMO SKYLĖS Ø3.2 - PRISPAUDIMO LOGIKA:** varžtas prispaudžia dugną prie bėgelio zonoje **R = 100 mm**
  (`--press-r`, Rytis); skylės dedamos taip, kad prispaustų kuo didesnį dugno plotą - ne tik kraštus. Skylė VISADA
  bėgelio ašyje, >= 10 mm nuo dugno kontūro (`--hole-edge`, t. y. 11,5 nuo šono), >= 15 mm nuo bėgelio galo.
  * **Štrichas** = TIKRAS dugno ruožas ant bėgelio ašies (ne 10 mm saugios zonos gabalai - m lankas, iš kurios ašis kelis
    kartus išeina, yra VIENAS štrichas; tai buvo klaida); įpjova < 40 mm (serifas) nejungia, akutė skiria. Štrichas
    dalijamas į n = ⌈L / 2R⌉ lygių dalių, skylė - KIEKVIENOS DALIES CENTRE, perkelta į artimiausią saugią vietą
    (T juosta 367 -> 2 skylės ketvirčiuose ~92 / 275; T kojelė, A kojos, m statiniai -> po 1 viduryje). NIEKADA ruožo
    galuose ir NIEKADA po skylę kiekvienam saugios zonos gabalui (a / n / m perteklinės skylės 26 mm tarpu - klaida).
  * **Kojelė prieš pilvelį (a, d):** kojelė = statinis, kuris tęsiasi už bėgelio į raidės vidų (dugne medžiaga 20 / 45 /
    70 mm nuo bėgelio krašto tame pačiame x; s lankas - ne kojelė). Kai kojelė ir pilvelis vienoje zonoje - varžtas
    KOJELĖJE, pilvelis gauna varžtą tik kaip antrą skylę. Kojelės skylė centruojama per kojelę + su ja sujungtą dugno
    plotą visoje bėgelio juostoje (ne toliau kaip kojelės plotis už jos) - n / m jungtyje su lanku skylė traukiama nuo
    krašto į didesnį tvirtinimo plotą (riboja 10 mm iki vidinio kontūro).
  * **Minimumai:** >= 2 ant bėgelio (raidė nesisuka), >= 4 raidei; trūkstant - ilgiausias vienos skylės štrichas gauna
    2 skyles ketvirčiuose (kojelė + pilvelis: kojelės lieka, antra - pilvelio centre). Vis tiek < 4 (y, s, kai bėgelis
    kerta tik vieną štrichą) - perspėjimas, ne išgalvota skylė. Siaura vieta - hole-edge mažinamas iki 7 (perspėjimas).
  * **VISŲ VIENODŲ RAIDŽIŲ TVIRTINIMAI VIENODI (Rytis):** raidės lyginamos pagal formą (gabaritai ±0,5 mm, perkelto
    kontūro simetrinis skirtumas < 0,5 % ploto); skylės ir D11 iš pirmos tokios raidės perkeliamos kitoms. Išimtis TIK
    raidei ant kitokio rėmo (bėgelio galas / kita ašis neleidžia tų pačių vietų) - skaičiuojama atskirai su perspėjimu.
  * Ataskaitoje: skylių koordinatės (mm nuo raidžių kairės apačios), prispausto dugno ploto % (dugnas ∩ skritulių R
    sąjunga; vidurys tarp bėgelių be trečio bėgelio lieka neprispaustas - normalu), perspėjimai.
- **LAIDO IŠVESTIS Ø11 (`--cable top|bottom|both|none`, numatyta `both` - DU rinkiniai: viršutinis / apatinis bėgelis):**
  viena skylė raidei, **VISADA BĖGELIO AŠYJE** (laidas pro dugną į U profilio vidų; šalia bėgelio - NIEKADA, Rytis
  atmetė), >= 20 mm nuo dugno kontūro (`--d11-edge`; plonoms raidėms mažinama pakopomis iki 8 - perspėjimas), >= 25 mm nuo
  varžtų centrų (`--d11-fix-clear`; siauram štrichui poroje iki 12 - perspėjimas). Vieta - NE prie raidės krašto, prie
  centrinio varžto, eilės tvarka: 1) štrichas su 1 varžtu - varžtas ir D11 PORA, centruota per štricho plotą ant bėgelio
  (varžtas c-12,5 / D11 c+12,5, D11 raidės centro pusėje; Ryčio pavyzdys m / y); 2) tarp dviejų arčiausiai raidės centro
  varžtų; 3) šalia arčiausio varžto, zonos vidurio pusėje; 4) štricho centre, to bėgelio varžtai perstumiami simetriškai
  į šalis; 5) ašyje arčiausiai raidės centro, kur dugnas >= 16 mm, zonos varžtai perstatomi (test_B „s"). Vienodoms
  raidėms - vienoda. „Dėti ranka" tik kai ašyje nėra 16 mm pločio dugno. Skylės variantų failuose skiriasi tik D11 ir
  prie jos perstumtais varžtais.
- **NEPRISPAUSTA DUGNO DALIS VIS TIEK GAUNA SKYLĘ (v69, Rytis 2026-10-09, AAA „s"):** po skylių išdėstymo tikrinama
  kiekvieno bėgelio juosta: dugno dalis, kurios neprispaudžia jokia to bėgelio skylė (už R = 100), gauna papildomą Ø3.2
  (pvz. „s" lanko galas prie bėgelio galo, kai ašyje vietos nebuvo). Ašyje netelpa - skylė leidžiama U sienelėje iki
  `--off-axis` 8 mm nuo ašies, >= 7 mm nuo dugno krašto, >= 8 mm nuo bėgelio galo; perspėjimas su nuokrypiu. Visai netelpa -
  perspėjimas „neprispausta, dėti ranka". (Atsakyta į „ar varžtas gali nukrypti nuo ašies" - taip, iki 8 mm, kai būtina.)
- **D11 TIK PLAČIOJE VIETOJE (v68, Rytis 2026-10-09, AAA „d"):** siauroje vietoje (lanko ir kojelės jungtis, plonas
  ruožas) dės LED - D11 ten NETINKA. Pirmiausia ieškoma VISOJE bėgelio ašyje (kairėje / dešinėje raidės dalyje, pvz. „d"
  kojelėje ar plačioje lanko dalyje) vietos su pilnu `--d11-edge` (20 mm) iki dugno krašto; artumas raidės centrui -
  tik tarp tokių vietų. Atstumas mažinamas (15 / 12 / 10 / 8) TIK kai plačios vietos ant to bėgelio nėra - tada
  perspėjimas „plačios vietos ant bėgelio nėra" (pvz. „s"), Rytis sprendžia.
- Ryčio pavyzdžiai (test_A.pdf, Bandymas ekrano kopijos) - patariamieji; taisyklės aukščiau - privalomos.

### Folded plate ir jo variantai -> `references/moduliai_folded.md` (PRIVALOMA perskaityti folded užsakymams)
Ten: „Folded plate - bendrinės taisyklės" (konstrukcija, lenkimas, išklotinės ir DXF, nesting, BOM), „Folded iš kelių dalių",
„Folded plate + pjaustyta plėvelė", „Folded / back plate + skaitmeninė SPAUDA", „Kito profilio raidės ant folded",
„P6 raidės ant folded plokštės" (`scripts/braizyti_lapa.py`). Lentelės „Skyrius" stulpelyje šie pavadinimai = skyriai tame faile.


### P6 raidės ant U bėgelių + P6+3 raidės ant Alu plokštės (įgyvendinta: `scripts/braizyti_begeliai.py`)
Pavyzdys: `assets/spec_begeliai_extra.json` (EXTRA), etalonas `assets/etalonai/EXTRA_225923_begeliai_P6-3_1-25.pdf`.
- Skriptas pats atpažįsta kliento faile: plokštę (forma, kurioje yra kitų formų; raidė apkerpama jos
  kontūru), raidžių grupes (pagal spalvą ir eilutes), bėgelius (pilki ilgi stačiakampiai).
  Grupės priskiriamos spec `groups` pagal `client_fill` spalvą; nereikalingos piktogramos - `ignore_fills`,
  sritis - `crop_pt`.
- **Bėgeliai:** jei yra Rytio detalizacija - imti iš jos (rėmas: horizontalūs + vertikalūs / įstrižas
  bėgeliai, tvirtinimo plokštelės L 30x30 su Ø8 skyle) per spec `groups[].rails` (poly, mm nuo grupės
  raidžių kampo) ir `fit_plates`. Kliento failo pilki stačiakampiai - tik pradinis variantas.
  BOM: bėgelių ilgis bėginiais metrais `{RAIL_TOTAL_M} m` (arba `{RAIL_LIST_M} = {RAIL_TOTAL_M} m`), plokštelių kiekis `{PLATES_N}`.
- **Profile 6 ant bėgelių:** U profiliai 30x30x2 (5) pritvirtinti prie raidžių galo, L 30x30x2 su 8 mm
  skylėmis (6) - prie sienos, U užkabinamas ant L. Bėgeliai RAL 7035 matt (kliento faile - pilki).
- **Profile 6+3 ant plokštės:** galas įleistas 25 mm nuo šonų galinės briaunos, šonų briauna 30 mm nuo
  3 mm Alu plokštės, distanceriai 30 + 25 mm (7), LED abiejose galo pusėse: priekyje (raidei) ir gale
  (balta 6500K, apšviečia plokštę). Plokštė (8) - RAL pagal užsakymą.
- **Bėgeliai ir ausėlės - bendra (visi P6 / P6+3 / P1 ant bėgelių):**
  - **PROFILIO FORMA VISUOSE VAIZDUOSE VIENODA (v47, Rytis 2026-10-09):** jei profilis U - jis VISUR braižomas kaip U
    (DETAIL A, šoninis vaizdas, tipinis pjūvis, 3D: sienelė prie raidžių / plokštės, anga į sieną); jei stačiakampis
    (`rail.type: "square"`) - visur stačiakampis vamzdis; L - visur L. Uždaras stačiakampis U profiliui - KLAIDA.
    Pjūviui - `lapas_core.rail_section(x, y, w, h, t, "u"|"sq", opening)`.
  - **Statmenys (Rytis patvirtino 2026-10-07; v92 - PER RAIDĖS STIEBO CENTRĄ, ne prie krašto: T stiebo, E nugarėlės
    vidurys; v95: raidė be tiesaus stiebo (A) - ĮSTRIŽAS per kojelės vidurį kaip EXTRA; GALINIAI - arčiausiai rėmo galų
    (stiebas ar įstrižas), tarpiniai tolygiai, kiekis pagal taisyklę - pvz. TESTAS: T, E, T, įstrižas ant A (v96: E po T
    reikalingas, Rytis po vizualinės patikros); mažiau nei taisyklės kiekis - informacija konsolėje):** dedami TIK po raidėmis - visą statmenį dengia raidė
    (>= 10 mm nuo kontūro šonuose); jų x NESUTAMPA su ausėlėmis (tarpas >= 30 mm, `vertical_ear_clear_mm`);
    statmuo - papildomas elementas: parenkamas PO ausėlių ir bėgelių, jų sprendimų NEKEIČIA (`place_verticals`).
  - **Ausėlių išdėstymas:** VISADA pagal `references/auseles.md` (PRIVALOMA perskaityti), kodas
    `scripts/auseles.py`, Smax lentelė `assets/auseles_smax.json`. Ausėlės į rėmo vidų (viršutinio - žemyn,
    apatinio - aukštyn); MAŽIAUSIAS kiekis, kai tenkinama FIZIKA (vėjas EN 1991-1-4,
    inkaro apkrova pagal sieną `"wall"`, bėgelio stiprumas/įlinkis, ≥3 ant bėgelio > 1500 mm) ir praktinė Smax
    (profilis, `font_style: script`); TARPINĖS ausėlės - POROMIS vienoje vertikalėje (viršus ir apačia tame pačiame x, Rytis patvirtino 2026-10-07; jei negalima - mažiausias poslinkis ≤150 mm, `AUS.place_frame`);
    KRAŠTINĖS ausėlės (pirmoji ir paskutinė) - KUO ARČIAU bėgelio galo galimoje vietoje (≤ 300 mm, jei ten yra
    laisva vieta, kitaip artimiausia; abu galai vienodai; svarbiau už mažiausią kiekį; pvz. tarp „i" ir „x" -
    prie „x"); kraštinės nesilygiuoja - **NEPAILGINTA ausėlė VISADA pirmiau už pailgintą (Rytis 2026-10-07): jei lange nėra laisvos
    vietos - imama artimiausia standartinė už lango, jei ją išlaiko konsolės / inkaro patikra; pailginta - tik kai
    be jos sprendinio nėra** (`auseles.py`: `end_ear` 1b, `place_rail` - pirma tik standartinės vietos); vengti pailginimo: pirmiau pastumti į laisvą vietą (pvz. „c" angoje link raidės centro), jei vis tiek reikia - MAŽIAUSIAS pailginimas lange ≤300 mm; pailginta tik galinė, tik kai be jos sprendinio nėra, ne toliau nei rėmo vidaus vidurys; vidurinis bėgis ir statmenys ausėlių negauna. **Rėmo gale dvi ausėlės viena šalia kitos (< 0,5 Smax, pvz. prie „S") - NELOGIŠKA (v94, Rytis): paliekama VIENA, leistinoje vietoje kuo arčiau galinės reklamos dalies; tarpas iki kitos gali būti didesnis už Smax (iki 1,5 Smax), bėgelis > 1500 mm lieka su >= 3; apkrova ausėlei > inkaro - perspėjimas.** **Fasadas nenurodytas = BETONAS (v90, Rytis: į jį galima tvirtinti bet kurioje vietoje; niuansai nurodomi papildomai)** - `concrete`, neklausti. Galiniame vaizde - ausėlių grandinė nuo bėgelio galų; BOM `N pcs. (n extended)`.
  - **Pjūvyje (pagal Rytio pavyzdį ausele_pvz.pdf):** U sienelė prie raidės galo, anga į sieną; ausėlė - L:
    horizontali kojelė U viduje ant flanšo, vertikali kojelė sienos plokštumoje, nukreipta į rėmo vidų.
  - Kliento bėgelių grafika (storis) normalizuojama į tikrą profilį (U 30x30x2).
  - **Bėgelio galai - 10 mm nuo raidės krašto** (`rail_edge_mm`, Rytis patvirtino): nuskaitytas horizontalus
    bėgelis pailginamas arba patrumpinamas, kad abu galo kampai būtų ≥10 mm raidės viduje (ta raidė, kurioje
    yra galas; jei galas tarpe - artimiausia į išorę). **Vertikalus** (pvz. i taško laikiklis) prasideda nuo
    viršutinio bėgelio VIRŠUTINĖS plokštumos ir baigiasi 10 mm iki formos krašto, matuojant kampais (kampas
    pasislepia už formos - nuo ten 10 mm). Taikoma tik kliento nuskaitytiems, ne `rails` iš detalizacijos.
    **Galas raidės linijoje (Rytis 2026-10-07):** bėgelis tęsiamas tik iki TOS PAČIOS linijos krašto, ne per visą
    raidę - pvz. 6-24 vidurinis bėgelis baigiasi ties „6" akute (10 mm nuo skylės krašto), „6" nekerta.
  - **Ausėlės braižomos HAIRLINE su Ø skyle visuose vaizduose**, kur matoma plokštelės plokštuma
    (priekinis, galinis, 3D).
  - Jei fizikos patikros neišlaikomos (didelės raidės, ilgos konsolės) - ausėlės dedamos pagal geometriją
    ir Smax su perspėjimu „tvirtinimą tikrinti"; 0 ausėlių lape nepalikti.
  - **Bėgelis per VISĄ raidžių eilę (v67, Rytis 2026-10-09, AAA „Bandymas"):** kiekvienas horizontalus bėgelis eina
    nuo kairiausios iki dešiniausios raidės ir baigiasi 10 mm nuo kraštinės raidės IŠORINIO krašto (už raidės
    vidurio, išorinėje pusėje). Galas, sustojęs kraštinės raidės pradžioje (pvz. „s" kairiame galiuke) arba tarpe prieš
    ją, - KLAIDA: raidė lieka ant vieno bėgelio. Jei tame aukštyje raidė per plona abiem kampams 10 mm viduje -
    bėgelis pastumiamas aukštyn / žemyn mažiausiu žingsniu (5 mm), kol galas pasiekia išorinę pusę (`_fit_h_end`
    ieško iš išorės į vidų). PO GENERAVIMO patikrinti skripto eilutes „galai ... -> ..." - abiejų bėgelių galai turi būti
    kraštinių raidžių išorinėje pusėje, ilgiai panašūs (AAA: 2683 / 2523 -> klaida, 2683 / 2670 -> gerai).
  - **Bėgelio padėtis aukštyje (v49):** iki pilno aukščio raidžių viršaus / apačios >= 11 mm (10 mm taisyklė galams; pilno aukščio - raidės >= 0.6 grupės aukščio, v57);
    kliento bėgelis arčiau - pastumiamas į vidų (spausdinama). Kliento bėgeliai NE pilki (pvz. šviesūs 0.9) -
    `"rail_fills": [[r, g, b]]`; bėgeliai nupiešti tik kontūru (neužpildyti stačiakampiai) - `"rail_strokes": true` (v56). Nulis ir gabaritai - pagal raides (`"origin_with_rails": true` - senas elgesys).
  - **Smax U20 lentelėje nėra** - ausėlės tik pagal fizikos patikras; Smax klausti Ryčio.
  - Kliento bėgeliai atpažįstami ir kaip storos pilkos linijos (stroke); vertikalūs (pvz. i taško laikiklis)
    lieka vertikalūs. Smulkūs tos pačios spalvos elementai (i taškas) prijungiami prie grupės.
  - **Ausėlės skylė (Rytis 2026-10-07): Ø6 ant 30 mm profilio, Ø8 ant 40 mm ir didesnių** (`EAR_HOLE`, BOM `{EAR_HOLE}`;
    perrašyti - `"ears": {"hole_d": N}`); ausėlė = profilio dydis.
- **VIENTISAS RĖMAS raidėms + plokštei (v44, Rytis 2026-10-09; spec `"one_frame": {"plate": "X", "rails": "EXTRA"}`):**
  plokštės grupė (pvz. apskritimas su X) neturi savo kabinimo (Z rėmo nėra); `rails` grupės horizontalūs bėgeliai
  tęsiami už plokštės iki 10 mm nuo jos krašto (abu bėgelio kampai), plokštė prisukama prie bėgelių priekio
  (nugara = bėgelio gylis, BOM „Screws sheet -> rails ?"). Ausėlės - NE už plokštės (užstotų), statmenys - po
  raidėmis pagal kliento taisyklę. DETAIL A - plokštė ant ABIEJŲ U bėgelių, padėtys kaip priekio vaizde (v45, `plate_rail_f`). Kitos grupės (pvz. 7-23) - savo rėmas.
- **P1 raidė tiesiai ant plokštės (v44):** `plate.gap_mm: 0` - be distancerių, varžtas per plokštę į PVC dugną
  (DETAIL A ir šoninis vaizdas pagal tai; BOM 7 - „Screw sheet -> PVC back").
- **RĖMO PRINCIPAS (v88, Rytis 2026-10-10):** rėmo struktūra priklauso nuo iškabos FORMOS ir DYDŽIO. Žemiau esančios
  taisyklės kai kuriems atvejams tinka 100 %, kitiems - NE: tada ieškoti ANALOGIŠKO sprendimo, pritaikant turimas žinias
  (gamybos tvarka - vientisi bėgiai, statmenys į tarpus, rėmas kaip konstrukcija pagal svorį; ausėlės pagal fiziką / Smax;
  paslėpta po raidėmis; jokių niekinių detalių) prie esamos situacijos. Skriptas - pradinis variantas, ne galutinis:
  PRIEŠ atiduodant peržiūrėti rėmą gamybininko akimis (PNG), neįprastą vietą pataisyti pagal principus ir atsakyme
  aiškiai pasakyti, kur pritaikytas analogiškas sprendimas ir kodėl; jei abejoji - siūlyk variantą ir klausk.
- **KLIENTO RĖMAS - TIK JEI TVARKINGAS (v106, Rytis 2026-10-11):** kliento faile bėgis netvarkingas, netinkamoje vietoje,
  per trumpas ar neatitinka naudojamo standarto -> rėmas pataisomas pagal skill, NEBENT nurodyta naudoti kliento rėmo
  struktūrą (spec / grupės `"client_frame": true`; `ears_pt` - kliento ausėlės = kliento rėmas, SPAR). Skriptas
  (`client_frame_issues`) lygina kliento horizontalius bėgelius su auto rėmu: ašis nuo tvirtinimo ploto centro > max(15, 1,5 x
  profilis) mm (`client_frame_tol_mm`), ilgis < 60 % skill bėgelio, trūksta / per daug ilgų bėgelių -> auto rėmas +
  perspėjimas su priežastimis. Smulkūs pagalbiniai bėgeliai (brūkšnelio laikiklis) - netikrinami. Auto rėmo sudaryti
  nepavyksta (pvz. Joker MAN-FRE) - lieka kliento rėmas su perspėjimu „PATIKRINTI ranka". Atsakyme VISADA pasakyti, kad
  kliento rėmas perdarytas ir kodėl.
- **RĖMAS IŠ RAIDŽIŲ, kai kliento faile bėgelių nėra (v75, Rytis 2026-10-10, pavyzdys aa_remas.pdf; spec `"auto_frame": true`,
  `scripts/auto_remas.py`):** RĖMO VIETA - PER RAIDĖS TVIRTINIMO PLOTO CENTRĄ. Horizontalūs bėgeliai eilutei 2: ašis per
  eilutės raidžių apatinių / viršutinių horizontalių štrichų VIDURĮ (x-aukščio kraštas ± pusė štricho storio - „B" apačia,
  „a" „t" „s" „d" viršus / apačia); galai - kraštinės raidės stiebo viduryje (kraštas ± pusė štricho), ne 10 mm nuo krašto.
  Statmenys - per raidžių STIEBUS (vertikalius štrichus, >= 30 + 2x10 mm pločio per visą tarpą tarp bėgelių), kuo labiau
  paslėpti po raide; **kiekis (v87, Rytis: rėmas - konstrukcija) eilutei ceil(L / 2500) + 1 su galiniais, MASYVIOMS raidėms
  (raidžių plotas >= 0,5 m² bėgiminiam metrui) ceil(L / 2000) + 1** (~7 m iškaba - 4, BB LIETUVA masyvios - 5); tarpiniai; jei toje pačioje x stiebas
  yra ir kitoje eilutėje - VIENAS statmuo per abi eilutes (pirmenybė tokiems); apatinės eilutės statmenys visada pratęsiami
  aukštyn iki viršutinės eilutės apatinio bėgelio (rėmas vientisas). 6 m taisyklė auto rėmui: galas trumpinamas tik
  stiebo ribose (iki pusė štricho - 15 mm). **Akcentai** (Ė taškas, Ū brūkšnys, i taškas - atskiri elementai, aukštis
  < 0,5 eilutės) NIEKADA nekabo ore: ne atskira eilutė, o LAIKIKLIS - vertikalus U nuo eilutės viršutinio bėgelio viršutinės
  plokštumos iki akcento (abu kampai >= 10 mm akcento viduje, x - akcento centras); per jį eina LED maitinimas (v77).
  **Ausėlės kelių eilučių rėme - IR TARP UŽRAŠŲ (v77):** kiekvienos eilutės bėgelių pora gauna savo ausėles (viršutinis
  žemyn, apatinis aukštyn - už raidžių), t. y. ausėlės ir ant vidurinių bėgelių; antros eilutės tarpinės ausėlės -
  ŠACHMATIŠKAI (ne vienoje linijoje su pirmos eilutės, `avoid_x`, tarpas >= 250 mm), alternatyva - ant statmenų (ranka).
  **Virinimo / surinkimo tvarka (v78-v79, Rytis 2026-10-10 - „be niekinių detalių"):** GALINIAI statmenys VISADA abiejuose
  kiekvienos eilutės rėmo galuose (išorinė plokštuma = bėgelio galas = stiebo centras); HORIZONTALUS BĖGIS VISADA VIENTISAS -
  baigiasi ties galinio statmens vidine plokštuma, niekada nekertamas statmens; jei viršutinės ir apatinės eilutės galai
  sutampa (<= 150 mm), galinis statmuo VIENAS VIENTISAS per abi reklamas (nepjaunamas); tarpiniai statmenys per stiebus,
  pjaunami TARP bėgelių (per abi eilutes = 3 dalys vienoje linijoje, BOM po dalį); statmuo niekada nekyšo už bėgelio
  galo (apatinės eilutės tarpinis pratęsiamas iki viršutinės eilutės bėgelio tik ten, kur tas bėgelis yra). VIENTISI
  statmenys - TIK rėmo pradžioje ir pabaigoje; visi kiti įvirinami į tarpus tarp bėgelių (v80). Eilutės sujungiamos
  ABIEJUOSE galuose (apatinė reklama niekada nekabo tik ant 2 statmenų). Galai nesutampa (> 150 mm) -> PAKOPINIS GALAS
  (v82, Rytis eskizas): trumpesnės eilutės ARTIMESNIS kitai eilutei bėgelis (viršutinės - apatinis, apatinės - viršutinis)
  pratęsiamas iki ilgesnės eilutės galinio statmens, o tas statmuo eina VIENTISAS per tarpą iki to bėgelio; trumpesnės
  eilutės galinis statmuo baigiasi ant pratęsto bėgelio (bėgis nekertamas). Jungiamieji statmenys tarpe - tik jei pakopa negalima.
  **Ausėlės (v80-v81):** ant KIEKVIENO bėgelio (ir viršutinio), eilutės poroje - VISADA PORŲ logika (tarpinės viršus /
  apačia vienoje linijoje, tolygiai); jei poromis su Smax neišeina - Smax +10 / 20 / 30 %, tada be fizikos patikros
  (siena unknown), su perspėjimu; atskiri bėgeliai / godus išdėstymas - tik paskutinė išeitis (ausėlės sukrenta be
  logikos, pvz. LIETUVA apačia 3861 + 4171 - Rytis atmetė); jei bėgelio
  galas be ausėlės per 300 mm (galą dengia raidės stiebas) - ausėlė ant GALINIO statmens laisvoje vietoje, arčiausiai to bėgelio.
  **Platus galinis elementas (v83, Rytis 2026-10-10):** jei gale plati raidė, didelis kvadratas ar apskritimas (ausėlės juosta
  ištisai po elementu >= 300 mm nuo galo ant abiejų bėgelių, ant galinio statmens vietos irgi nėra, elementas solidus >= 2 x
  štrichas) - rėmas PRATĘSIAMAS IKI RAIDĖS GALO (abu bėgelio kampai >= 10 mm viduje, kuo arčiau krašto), o rėmo gale
  ausėlė IŠSIKIŠUSI UŽ RAIDĖS (už krašto + 5 mm, bėgelio aukštyje). Siauresniam galui (pvz. BB „A" viršūnė) - ne, ten
  priimtina ausėlė toliau nuo galo (Rytis: „gamybiškai patenkinama"). Bandymas: `scripts/projektai/bandymas_aa/spec_wide.json`.
  Didelis apskritimas / plokštė (v84, Rytis): PAGAL UŽSAKYMĄ - reikalaujama VIENTISA iškaba -> ant bendrų bėgelių (ši
  taisyklė, ausėlės išsikiša); reikalaujama ATSKIRA -> savo kabinimas kaip EXTRA X (Z profiliai ant elemento, sieninis rėmas,
  `references/klientai/extra.md`). Užsakyme nenurodyta - KLAUSTI.
  Bandymas: `scripts/projektai/bandymas_aa/` (spec_auto.json, spec_BB.json).
- **Kelios eilutės ant VIENO rėmo (v74, Rytis 2026-10-10, „Bandymas / antras"):** spec `"merge_rows": true` - tos pačios
  spalvos eilutės sujungiamos į vieną grupę; kliento faile (ar mūsų pridėtame variante) po kiekviena eilute 2 horizontalūs
  bėgeliai + jungiamieji vertikalūs bėgeliai tarp eilučių (pilki stačiakampiai tarpe, pvz. po „a" raidėmis); statmenys
  po raidėmis - kiekvienos eilutės bėgelių porai, ausėlės - tik viršutiniame ir apatiniame bėgelyje, viena laido išvestis,
  BOM viena bėgelių eilutė. Bėgelio aukščio patikra (>= 11 mm) - pagal tos eilutės raides. Bandymas: `scripts/projektai/bandymas_aa/`.
- **Kliento rėmo standartai** (statmenų kiekis / vieta, rėmo tipas pagal užrašą) - kliento faile (pvz. EXTRA ->
  `references/klientai/extra.md`).
- **Šriftas VISUR - GOST Common** (`assets/gost_common.ttf`, Rytio šriftas; Rytis patvirtino 2026-10-07).
  Šrifte sumaišyti kai kurių simbolių kodai - `T()` automatiškai keičia Ø->⌀, °->˚, ±->+/-; netelpantis tekstas
  lentelėse mažinamas (`fit=`). Jei failo nėra - osifont.
- **MAIN DATA - tik tai, kas ne pagal standartą (v100, Rytis):** „Wall" rašoma TIK kai fasadas kitoks nei įprastas
  (papildoma opcija); „Drainage" - NIEKADA (privaloma exterior opcija, nežymima). Skriptas tokias eilutes pašalina pats.
- **BOM „Letter back" VISADA su spalva (v100, Rytis):** standartas - šonų (return) spalva; kitokia tik nurodžius
  (spec / grupės `"back_ral"`). Skriptas užpildo FINISH, jei spec'e tuščias.
- **MAIN DATA VISADA turi „Weight (calc.)" ≈ N kg / pcs, excl. PSU** (`{WEIGHT}`): priekis (PMMA 8/3 mm),
  šonai Al 1 mm, nugara Al 1,5 mm, PVC bortelis, bėgeliai/ausėlės/plokštė arba folded plokštė + L profiliai.
  Tankiai ir prielaidos - `assets/svoris.json` (storiai - prielaidos, keisti ten); LED/PSU/tvirtinimai neįeina.
- **RĖMO MATMENYS - APVALŪS, 5 mm žingsniu (v99, Rytis 2026-10-11):** gamybininkui sunku fiziškai matuoti 3017 ar 17 -
  lengviau 3020 / 15. Horizontalių bėgelių ilgiai apvalinami iki 5 mm (abu galai po pusę; jei strypų daugėtų - žemyn),
  tarpai tarp bėgelių / statmenų ilgiai - iki 5 mm (žemesnis bėgelis paslenkamas <= 2,5 mm, statmenys - kartu).
  Spec `"frame_round_mm": 0` - išjungti. Detalizacijos rėmas (`groups[].rails`) nekeičiamas.
- **BOM - TIK BENDRAS REZULTATAS (v90, Rytis):** ne „1 + 1 + 1 + 2 = 5", o „5" - `{RAIL_LIST_M} = ` ir pan. skriptas pats
  pašalina, `{RAIL_LIST_M}` = bendra suma.
- **Profilių ilgiai BOM - VISADA bėginiais metrais** (Rytis patvirtino), ne mm: `{RAIL_TOTAL_M}`, `{RAIL_LIST_M}`,
  `{PRAIL_TOTAL_M}`; folded `{L_LEN_M}`, `{L_TOTAL_M}`.
- **Laidai** (nekerta matmenų v51, iš raidės virš rėmo v50/v52/v53, iš bėgelio galo, `cable_exits`, `trafo_box.label`) -> `references/moduliai_kiti.md`.
- Pavyzdžiai: `assets/spec_matkroken.json` (P6_3mm color, U30, rašytinis šriftas, 12V 2 m),
  `assets/spec_coop_prix.json` (dvi grupės, U40, i taško statmuo, 2 išvestys); etalonai `assets/etalonai/`.
- Galinis vaizdas, antraštė, rėmo matmenys, lapo vaizdai -> `references/stilius.md` (iš SKILL.md v83).
- Placeholderiai: `{PER_6} {A_6} {PER_63} {A_63} {PER_ALL} {A_ALL}`, per grupę `{PER_<vardas>}`,
  `{A_<vardas>}`, `{RET_<vardas>}`, `{RAILS_<vardas>}`; `{RAIL_TOTAL} {RAIL_LIST} {RAIL_SIZE}`,
  `{PLATE} {PLATE_PER} {PLATE_AREA}`, `{PW} {PH}`.

### MEDŽIAGŲ BIBLIOTEKA - tik tai, ką galima nusipirkti Lietuvoje (v114, Rytis 2026-10-12) -> `references/medziagos.md` §0
PRIEŠ rašant į lapą / BOM / MAIN DATA / atsakymą BET KOKĮ Alu profilį (L, U, O vamzdis, apvalus, T, juosta, Z), Alu lakštą ar
AKP (storis + formatas + RAL) - patikrinti: `python3 scripts/medziagos.py profilis "U 30x30x2" "O 25x25x2"`,
`python3 scripts/medziagos.py lakstas akp 3 9005`. Nėra kataloge -> NEIŠGALVOTI ir neperrašyti „panašiu“: pasakyti Ryčiui
„X LT tiekėjų sandėlyje nėra, artimiausi: ...“ ir laukti sprendimo (gali būti užsakomas - tik su patvirtinimu).
Rėmo (`rail.size`, `plate.rail`, `zframe.z/tube`) ir folded L profiliai tikrinami automatiškai (konsolė `! ... NĖRA`).
Žinomos spragos: **Z 30x30x30x2** ir **O 30x30x3** - sandėlyje nėra nė pas vieną; **U 40x40x2** - tik Lankava;
**Alu 3 mm** lakštas - tik Lankava 2000x1000.

### Plėvelė - sunaudojimas ir pjaustymo failas (v121, Rytis 2026-10-12) - PRIVALOMA visoms plėvelėms BOM
**Plėvelė skaičiuojama pagal SUNAUDOJIMĄ medžiagos (rulono darbinis plotis x sunaudotas ilgis), NE pagal pačios plėvelės
(grafikos) plotą.** Kodas `scripts/plevele.py` (`plan`, `bom_text`, `objects_from_pdf`, `write_dxf`, `preview_pdf`).
- **Rulonai (darbinis plotis):** spalvota plėvelė - **1190 mm** (STANDARTAS; lipdukas / dalis neturi išeiti už 1190);
  balta plėvelė arba spaudos plėvelė - **1320 mm**; **1500 mm - tik išimtiniais atvejais ir TIK su pastaba**
  (`allow_1500=True`, pastaba lape / užsakyme). Rūšis - iš pavadinimo (white / balta / spauda / print -> 1320) arba `kind`.
- **Pjaustymo failas - originali forma skaidoma KUO MAŽIAU.** Telpa visa (trumpesnė pusė <= darbinis plotis) -
  ploteriuojama VISA, neskaidant, sunaudojimas pagal failą (pvz. OKQ8 „Alltid öppet" lapas 1). Netelpa - skaidoma TIK
  bendrais objektais (lapas 2): **DĖLIOJIMO PRINCIPAS (Rytis patvirtino, `scripts/projektai/plevele_test/`)** - į VISUS
  bendrus objektus (užrašo eilutė, automobilis su ratais, kiekvienas dušas su taškais; riba - ryškus tarpas >= 3 x tarpų
  mediana) ir jie sudėliojami kompaktiškai ant rulono (galima pasukti 90°, pvz. dušai šalia užrašo). Objektas, kuris pats
  netelpa, - skeliamas per didžiausią savo tarpą; vienas kontūras (raidė, taškas) niekada nekarpomas.
  **UŽRAŠAS VIENOJE LINIJOJE = VIENAS OBJEKTAS (Rytis):** visi eilutės žodžiai (ir ö / i taškai) - viena dalis, NESKAIDOMA
  į žodžius ar raides, net jei taip sunaudojama daugiau plėvelės - gamybininkui klijuoti 2 užrašus į vieną liniją, matuoti
  tarpus brangiau ir rizikinga. Skaidoma TIK kai netelpa į rulono plotį, NIEKADA - vien taupant plėvelę. Eilutė pati
  netelpa -> perspėjimas, Rytis sprendžia (`text_lines`: panašus aukštis, bendra bazinė linija / viršus, tarpas <= 1,5 h). Dalys dėliojamos ant rulono
  (galima pasukti 90°), tarpas 10 mm (prielaida, `gap_mm`). Objektas pats platesnis už rulono darbinį plotį -
  perspėjimas (siūlė / kitas rulonas - Rytis sprendžia).
- **BOM eilutė:** `1320 mm x 2.61 m = 3.44 m²` (+ `x qty`), ne grafikos m². Konsolėje ir atsakyme - ar skaidyta ir į kiek dalių.
- CLI: `python3 scripts/plevele.py kliento.pdf --rect x0,y0,x1,y1 --width-mm 1600 --fill FFFFFF --film "ORACAL 551 101 white" --qty 6 --dxf cut.dxf --pdf cut.pdf`
  (PDF taškai; `--rect` - plokštės stačiakampis, `--width-mm` - jo tikras plotis; be jų 1 pt = 1 pt; compound path skaidomas į salas). Testas `scripts/projektai/plevele_test/`.

### Medžiagų formatai ir 6 m strypų taisyklė (v73, Rytis 2026-10-10) -> `references/medziagos.md` (PRIVALOMA rėmams)
Tiekėjų formatai - `assets/medziagos.json` (keisti TIK ten; Heliopolis: VISI profiliai 6 m; lakštai PMMA 3050x2050 /
4050x2050 (opal 8), PVC 3050x2050, AKP 3050x1500 / 4050x1500 / 3200x1500, Alu 3000x1500 / 4000x2000); kodas `scripts/medziagos.py`.
- **PAGRINDINĖ TAISYKLĖ - rėmas po raidėmis ir 6 m profilis:** visos to paties profilio dalys (bėgeliai, statmenys, visų
  grupių) dėliojamos į 6 m strypus su prapjova (3 mm, Rytis patvirtino 2026-10-10). Rėmas, kuris sudėliotas gaunasi pvz. 6,05 m (2 x 3025),
  netelpa į vieną strypą -> horizontalūs bėgeliai PATRUMPINAMI mažiausiu kiekiu (žingsnis 5, iki 100 mm), kad tilptų,
  abu galai simetriškai, bet TIK nepažeidžiant kitų taisyklių: galo kampai >= 10 mm toje pačioje kraštinėje raidėje,
  galas lieka raidės išorinėje pusėje (v67), galas prie skylės nejuda; detalizacijos rėmas, statmenys, vertikalūs
  laikikliai - nekeičiami. Daroma PRIEŠ ausėles (ausėlės, statmenys, laidas - ant galutinio bėgelio). Laisvumo
  neužtenka arba trumpinimas strypų nemažina -> NETRUMPINAMA, perspėjimas `! 6 m taisyklė` - Rytis sprendžia.
  Atsakyme VISADA pasakyti, kiek bėgeliai patrumpinti. Retas atvejis - taisyklė veikia tik kai pasitaiko atitikmuo.
- **Bėgelis ilgesnis už strypą (v92, Rytis 2026-10-11): PIRMIAUSIA TRUMPINAMAS IKI STRYPO** (pvz. 6500 -> 6000, abu galai
  simetriškai, be 100 mm ribos), jei galai lieka kraštinių raidžių viduje (10 mm) ir išorinėje pusėje - konstrukcija
  nesusilpnėja, profilis sutaupomas, sandūros nėra. Tik jei netelpa (pvz. 7,35 m) - jungiama iš dalių:
  pagrindinė taisyklė - TAUPYTI MEDŽIAGĄ: sandūros vieta nesvarbi,
  dalys parenkamos taip, kad liktų kuo mažiau atliekų (`medziagos.nest_bars` - mažiau strypų, tada didesnis vientisas likutis;
  konsolė `jungiamas iš dalių: 6000 + 500`). Bet bėgelis <= 6 m NIEKADA nevirinamas iš dalių vien dėl taupymo.
- **Strypai - VISAM UŽSAKYMUI (v98, Rytis 2026-10-11, pasikartojanti klaida):** planas ir trumpinimas skaičiuojami
  su spec `qty` (pvz. 2 vnt. po 2 bėgelius ~3,05 m: be patrumpinimo 4 strypai, patrumpinus iki 3019 + 2972 - 2 bėgelių
  poros viename strype). Renkamas MAŽIAUSIAS patrumpinimas, duodantis mažiausiai strypų; didesnis - tik jei vientisas
  likutis padidėja >= 500 mm. `{RAIL_BARS}` - visam užsakymui (BOM rašyti „(N x 6 m bars / 2 pcs)").
- Konsolė: `strypai 30x30x2 (užsakymui N vnt.): 1 x 6 m: [2995+2995] | atlieka ...`.
  BOM: `{RAIL_BARS}` `{RAIL_PLAN}` `{BAR_M}` `{PRAIL_BARS}`, folded `{L_BARS}` (naujuose spec'uose `({RAIL_BARS} x {BAR_M} m bars)`).
- Folded L (plotis - 50) netrumpinami - tik perspėjimas; išklotinė tikrinama į Alu lakštą (paraštė 10), netelpa ->
  „Folded iš kelių dalių". Kiti dideli elementai - `python3 scripts/medziagos.py sheet W H plexi 8`.
- Bandymai: `scripts/projektai/strypai_6m_test/`. Spec: `"stock": {"enabled": false, "bar_mm", "kerf_mm", "trim_max_mm"}`.

### P6 ant stačiakampio Alu profilio (Rytis patvirtino 2026-10-07) -> `references/moduliai_kiti.md`

### P1 nešviečiančios raidės ant bėgelių (v29, Rytis 2026-10-08; pirmas atvejis EXTRA order 225978) -> `references/moduliai_kiti.md`

### Stogo iškaba - atramos (v29, Rytis 2026-10-08; pirmas atvejis EXTRA FAS 700H80 takskilt) -> `references/moduliai_kiti.md`

### Matmenys priekio vaizde (bėgelių modulis) -> `references/stilius.md` (bendri + grandinės; kairė - plokštė arba raidžių viršai / apačios, NEŠALINTI)

### Matmenų taisyklės - visi lapai (v38) -> `references/stilius.md` (viena grandinė eilutėje, `50 | n x p = L | 50`, DETAIL 1:2, 12 / 8 pt)

### 3D (r3d) - visi nauji lapai (v38) -> `references/stilius.md` (`scripts/r3d.py` Scene / extrude_xy; aplinka - clasohlson sheet2v)

### Bendras branduolys `scripts/lapas_core.py` -> `references/stilius.md` (nauji moduliai - per lapas_core)

### Pilonai / totemai (v89, įgyvendinta) -> `references/moduliai_pilonai.md`; ŠVIEČIANTYS dideli pilonai (šviesdėžės / įdėklai, plieno ar Alu rėmas, padai) - etalonas `references/etalonas_pilonas_prisma_alt8826.md` (v107), kodas `scripts/projektai/thales_d059422/thales_pylons.py`

### Kiti produktai (dar neįgyvendinta) -> `references/moduliai_kiti.md` (raidės ant sienos, šviesdėžės, plokščios - konstrukciją klausti)

### Senų brėžinių perdarymas į mūsų stilių (Rytis 2026-10-07; bet kurio kliento, pvz. ALT8857 Clas Ohlson) -> `references/moduliai_kiti.md`

## Žodynėlis

| Santrumpa | Reikšmė |
|---|---|
| P6 / Profilis 6 | Tūrinė šviečianti raidė: plexi priekis, Alu šonai ir galas, LED viduje, gylis pagal užsakymą |
| tūris | raidės gylis |
| priekis / front | raidės priekinė plokštuma |
| šonai / body | raidės šonai (return) |
| folded pl. / folded plate | lankstyta Alu plokštė - fonas; „lenkimas" = užlenkimo gylis |
| bėgeliai / rails | U 30x30x2 profiliai raidžių gale, kabinami ant L 30x30x2 prie sienos |
| P6+3 | P6 raidė ant Alu plokštės: galas įleistas 25 mm, distanceriai 30+25, LED ir gale (halo) |
| profiliai tvirtinimui | L 30x30x2 profiliai folded plokštės tvirtinimui (viršus + apačia) |
| praplatinti raides | per plonus elementus storinti iki profilio minimumo |
| D3.2 / D11 | tvirtinimo skylė Ø3,2 (raidei ~4) / kabelio išvedimas Ø11 |
| P65L / P130L / P190L | LED Lens moduliai PRO65Lens (1 LED, 0,5 W) / PRO130Lens (2 LED, 1 W) / PRO190Lens (3 LED, 1,5 W) - `references/led_lens.md` |
| P8 special | Clas Ohlson šviečianti raidė: Al 3 priekis + frezuota plexi 20 (žr. `references/klientai/clasohlson.md`) |
| oracal / plėvelė ant folded | pjaustyta plėvelė ant dažytos folded plokštės - „Folded plate + pjaustyta plėvelė" |
| išklotinė / flat | sulankstomos detalės plokščias pavidalas (CNC pjovimui), DXF |
| strypas / bar | standartinis profilio ilgis 6 m (tiekėjas) - `references/medziagos.md` |

## Dar nepatvirtinta (lape - tuščia vieta)
v90 - U laikikliai (PASIŪLYMAI, `assets/tvirtinimas.json`): kiekio ribos pagal ilgį (1500 / 3000 / 4500), plieno
kriterijus (>= 0,5 m² / m), 3 skylių išdėstymas (p / 2 nuo galų kaip 2 skylėms?), „didelės" H >= 1000. Kada U, kada stačiakampis
profilis; profilis, kai aprašyme nenurodytas (dabar U30). LED - konkretus modulis užsakymui (siūlyti pagal
`references/led_lens.md`, lape - tik patvirtintą); P6 minimalus linijos storis ir raidės aukštis.
Išspręsta v90: storiai - standartas + nestandartiniai pagal užsakymą; varžtai - tik teorija; DXF dugnas -3 mm - OK.
Medžiagos (v114): U 30x30x2 / U 40x40x2 / O 20x20x2 - rasti (Lankava, Proplastik, Heliopolis A-9497); Z 30x30x30x2 ir
O 30x30x3 - LT sandėliuose nerasta (Rytis nurodo šaltinį); PVC 3 mm, Alu 3 mm > 2000x1000 lakštų formatai; spalvotos plexi formatai.

## Žinomos klaidos (nekartoti) -> PILNAS sąrašas `references/klaidos.md` (PRIVALOMA perskaityti prieš P6 DXF, bėgelių, folded ir Corel darbus)
- ŽINOMA PROBLEMA: `auseles.py` EXTRA 1800H80 (U40, H 1080) rėmui neranda sprendinio su tarpu <= Smax
  (1200) -> 0 ausėlių ant EXTRA rėmo. Kol nepataisyta - ausėles šiam atvejui spręsti ranka / klausti Ryčio.
- Skill'o failų pavadinimuose - TIK ASCII (be lietuviškų raidžių, be „+" ir tarpų), kitaip skill'o
  zip neįkeliamas („path with invalid characters").
- **Paskyros skill'o kopija buvo sena (be „Versija", 2026-10-08) - tris kartus darbas padarytas sena versija.**
  Todėl nuo v22 paskyroje tik paleidiklis, darbas - TIK iš šaltinio (nuo 2026-10-12 - GitHub repo, žr. viršuje).
- **Lygiagretūs pokalbiai (2026-10-09, v65):** du pokalbiai vienu metu keitė tą patį skriptą ir zip - versijos susimaišė
  (R 200 vs 100). Skill'o keitimus daryti viename pokalbyje; prieš push - `git pull --rebase` (konfliktas = kitas pokalbis keitė, sutikrinti).

## Ausėlių žingsnio tolerancija (v8) -> `references/auseles.md` (Smax +5 %, pora nededama „dėl gražumo")

## PATVIRTINTA -> gamybos paketas (v104) -> `references/patvirtinimas.md` (žinutė „Patvirtinta, ALT5432_10.12_RS“ + PDF: gamybinis lapas su ALT numeriu, DXF 1:1, LED dėliojimas; ALT normalizuoti, pvz. „ALT 8872_10.12“ -> `ALT8872_10.12_RS`)

**LED ŽYMĖJIMAS LAPE (v111, Rytis 2026-10-12):** kiekviename šviečiančios iškabos lape (REAR VIEW) PRIVALOMA nurodyti, kokie
LED dedami kiekvienoje grupėje - spec grupės `"led"` (eilutė arba eilučių sąrašas): spalva + temperatūra (pvz. „White LED modules,
6500K“, „RED LED modules“); 6+3 raidė ant plokštės - „Inside letter: …“ + „Backside: …“ (kaip `assets/etalonai/led_zymejimas_galiniame_EXTRA_223315.pdf`).
Užrašas - virš grupės, virš bėgelių matmenų eilučių; P1 / `lit: false` - nežymima. Iš kur imti: užsakymo aprašymas / BOM „LED …“ eilutė;
neaiškus spalvos priskyrimas grupei - KLAUSTI.

## LED - NUMATYTA: `scripts/led_km.py` (v119 / v120, Rytis 2026-10-12)
**v127 - TIEKĖJAS Kaisen Electric (Rytis 2026-10-12: „failai gauti gamyboje, todėl laikyti kaip naują versiją LED dėliojime"):**
moduliai, PSU ir ryškumo lentelės - TIK iš `assets/kaisen_led.json` (šaltiniai: `assets/kaisen_2023_price_list_alt_reklama.pdf`,
`assets/kaisen_2023_modules_depth_table.xlsx`). Raidėms pagal gylį (PRISM 12V): 30-49 **KM-P0-W** 0,36 W, 50-59 **KM-P1-W** 0,5 W,
60-100 **KM-P2-W 0,72 W**, 101-120 **KM-P2-W 1W**, 121-150 **KM-P3-W** 1,5 W, 151-250 **KM-P4-W** 2 W; raudoni - **KM-P*-R**;
plona linija (linijos pločio mediana < 35 mm) - **KM-MINI3** (0,4 W iki 59 gylio, 0,7 W 60-100). Spec `module` - kitas kodas iš kainoraščio.
**Žingsnis - iš Kaisen ryškumo lentelės (Depth table):** didžiausias žingsnis, kuriam lx >= 2200 (`lux_target`; Ryčio lapai: KM-P2 0,72W
gylis 100 -> 140 = 2250 lx, gylis 70 -> 120), ne didesnis už modulio CC; plonoms linijoms dar <= 1,6 x linijos plotis.
PSU - Kaisen **KPS-V12-…67 outdoor IP67** (24V moduliams - KPS 24V sąrašas), apkrova <= 75 % (14 W -> KPS-V12-20W67-5Y-RM, 26 W -> 36W).
BaltLED (`baltled_led.json`, v125) ir Lens (`led_lens.json`, `led_sim.py`) - NE numatyti, tik jei Rytis nurodo.
**v131 - NUMATYTAS OPTIMIZAVIMAS (`ilp()`, layout „ilp"; Rytis patvirtino krypti „bandyk"):** išdėstymas sprendžiamas kaip
aprėpties uždavinys (sveikųjų skaičių programavimas, `scipy.optimize.milp` / HiGHS, ~1-10 s raidei):
kandidatai - raidės taškai kas 0,1 p (ne prie pat krašto); SĄLYGA - kiekvienas raidės veido taškas (išskyrus krašto juostą:
max(0,1 p, 0,35 vietinio pusploto)) <= 0,6 p nuo modulio -> t skersinio galai, e skersinis / uodega, d pilvo viršus padengiami
VISADA; moduliai >= 0,75 p vienas nuo kito; tikslas - mažiausiai modulių, lygiaverčiai - arčiau ašies. Rezultatas pastovus.
Kalibruota pagal Ryčio lapus: Åpn496 19 (Ryčio 20), Åpn894 10 / 2 / 12 / 13 (Ryčio 9 / 2 / 12 / 13).
Parametrai `IL_R, IL_EDGE, IL_REL, IL_SEP` - keisti tik pagal realų švietimo testą (nuotrauka įjungtos raidės).
Senesni: `"layout": "pack"` (v129), `"chain"` (v126-v128).
**v129 - NUMATYTAS APSKRITIMŲ PAKAVIMAS (`pack()`, Rytis: „neatitinka nei gamybinių, nei teorinių planų"):** etalonas -
Ryčio lapai `assets/led_pavyzdziai/ALT8873_..._Apn894_..._RYCIO.jpg`, `ALT8852_extra_...`, `ALT8855_matkroken_...`: kiekvienas modulis -
apskritimas Ø žingsnis, apskritimai SUPAKUOTI raidėje (liečia vienas kitą, raidės kraštus ir galus), plati linija - 2 eilės,
siaura (< p) - viena eilė ašyje (apskritimas išlenda per šonus). Algoritmas: centrai A (edt >= min(p/2, 0,85 vietinio pusploto) +
ašis iki galų / kampų); pradžia - galas; frontas auga liečiančiais apskritimais (0,7-1,0 p), renkantis daugiausia nepadengto
ploto; tada stūmimas tolygumui (< 0,95 p - atstumiami, nepadengta dalis traukia), nereikalingas (< 20 % nuosavo ploto) šalinamas;
modulis pasuktas pagal vietinę raidės kryptį. Patikra: Åpn894 9 / 2 / 12 / 11 (Ryčio 9 / 2 / 12 / 13). Žemiau (v126-v128) - `layout: chain`.
**v128 - ŠVIETIMO PADENGIMAS SVARBIAU UŽ TAISYKLES (Rytis: „jei taisyklė sako, kad reikia taip, bet realiai ten nešvies - blogai"):**
taisyklės (galas p/2, mazgai, žingsnis) - tik pradinis išdėstymas. Toliau `coverage()`: modulio šviesos dėmė veide
E(d) = 1 / (1 + (d / s)²)², s = 0,6 x žingsnis pagal lx lentelę; etalonas - tiesi tos pačios raidės pločio linija su moduliais kas p
(jos krašto taškas tarp modulių = 1). Taškas tamsus, jei < 0,65 etalono (krašto juosta 0,08 p nevertinama - šonų atspindys);
tamsi dėmė >= 0,025 p² -> godžiai pridedamas modulis (ašis / gilus plotas, pagal vietinę ašį), tada moduliai pastumiami
(<= 0,3 p) link tolygios apšvietos, perteklinis (< 0,7 p nuo kito, be jo nepatamsėja) - šalinamas. Spausdinama „[padengimas: +N / -M]".
Abejojant - `python3 scripts/led_km.py spec.json out.pdf patikra.png` (santykinė apšvieta, tamsios dėmės mėlynai; ne gamybai).
**Atvaizdavimas - LED IMITACIJA** (Rytis: gamybai priimtiniau nei vieni apskritimai): kiekvienas modulis - korpusas
(lentelės matmenys) su LED / lęšiais, pasuktas pagal raidės ašį, + grandinės laidas tarp gretimų + apskritimas = žingsnis.
Korpusas imitacijoje simbolinis (0,32 x 0,12 žingsnio); LED skaičius pagal galią (<= 0,5 W - 1, <= 1 W - 2, 1,5 W - 3, 2 W - 4).
**Rytis: „led dėliojimas vis dar blogas“ - Lens modulių simuliacija (P65L / P130L / P190L) gamyboje NENAUDOJAMA, nebent
paprašyta.** Išdėstymo stilius - kaip
`assets/led_pavyzdziai/` (Ryčio perdaryti mūsų lapai `ALT8873_extra_225978_*_RYCIO.jpg` - ETALONAS).
- `python3 scripts/led_km.py spec.json out.pdf`; spec: `pdf`, `page`, `crop_pt`, `scale_mm_per_pt`, `depth`, `qty`, `title`
  („<ALT> <užsakymas>_N_LED“), `groups: [{fill_rgb, led: white|red, name, pitch?}]`.
- Viena eilė per raidės ašį; **žingsnis („atstumas tarp centrų“) pagal gylį: 50 -> ~100, 70 -> ~120, 80 -> ~130, 100 -> ~140 mm**
  (spec / grupės `pitch` - kitaip; Ryčio lapuose prie 100 gylio būna 100-140 - neaiškiu atveju klausti).
- Apskritimas aplink modulį = žingsnis, gali išeiti už raidės; status galas - modulis p/2 nuo krašto (dalių sk. = round(L / p));
  sankirtoje vienas; žiedai simetriški; linija > 2 x žingsnis - tinklelis per plotą (H1800 X).
- Galia = vnt. x 0,72 W; PSU - mažiausias KPS su apkrova <= 75 % (KPS-V12-20W67-5Y-RM, KPS-V12-36W67-5Y-RP, KPS-V12-60W...,
  KPS-100W ...).
- Lapas: kiekis virš kiekvienos raidės, aukštis + plotis, „LED module KM-P2 HE 0,72W | N PCS. | Galia: ~W | Depth | Atstumas tarp
  centru ~p“, modulių spalva + PSU, „N pcs.“, M 1:x, pavadinimas, LED ženklas. Raudoni moduliai - raudoni apskritimai.
- v126: VISI raidės galai ir kampai turi modulį (A kojos, 7 / L / Z kampai) - galinis modulis nešalinamas dėl artimos sankirtos;
  plonos linijos (mažos raidės) - žingsnis <= 1,6 x linijos plotis (FAS700 7-23 w 62 -> 100).
- Patikra (Åpn496 / Åpn894, gylis 100, p 140): 5-1-7-7 = 20 (Rytis 20), 9-2-12-12 = 35 (Rytis 36).

## LED - Lens moduliai (tiekėjo duomenys) -> `references/led_lens.md` + `references/led_sim.md` (PRIVALOMA LED darbams: `scripts/led_sim.py`, `led_box.py`, `assets/led_lens.json`; lape LED tik patvirtintas)

## Maitinimas - TRAFO BOX (v9) -> `references/moduliai_kiti.md` (visi laidai į vieną TRAFO BOX, 5 m, spec `trafo_box`; laido išėjimai / nuleidimai nesikerta)

## Daugialapis dokumentas (v10) -> `references/moduliai_kiti.md` (lapas = atskiras spec, `"sheet": "3 / 18"`, ne-iškabų pozicijos per lapas_core, `behind`, `element_colors`)

## PDF atidarymas CorelDRAW (Rytis 2026-10-08) -> `references/stilius.md` (tekstas lieka tekstu, `pdf_fix_fonts` GOST Common, Corel importas „Import text as: Text", .cdr)

## Lapas (v9) -> `references/stilius.md`
