---
name: "reklama"
description: Rytio iškabų gamybos techninė dokumentacija - iš kliento PDF/DXF ir trumpo aprašymo (pvz. "P6 ant folded pl., 40mm, RAL9010") sugeneruoja A3 techninį lapą etaloniniu CAD stiliumi ir patikrina gamybos tinkamumą. Etaloninis lapo stilius galioja VISIEMS produktams (raidės ant folded plokštės, raidės ant sienos / bėgelių, pylonai, šviesdėžės, plokščios iškabos). Naudok VISADA, kai pokalbyje yra iškaba, tūrinės/šviečiančios raidės, profilis (P6, Profile 6 ir kt.), folded pl. / lankstyta plokštė, plėvelė / vinilas (sunaudojimas, ploteris), pylonas, šviesdėžė, RAL spalvos, raidžių storis, tvirtinimas, LED, D3.2/D11, arba užklausoje yra kliento raktažodis (SPAR, EXTRA, Clas Ohlson, OKQ8, Skyltkoncept, BrandFactory, Volvo, DSV, BN Skilte, ChopChop, MENY, KIWI, prancūzai), arba vartotojas įkelia kliento logotipo ar iškabos PDF ir prašo brėžinio, matmenų, specifikacijos ar pasiūlymo - net jei žodis "skill" ar "lapas" neištartas.
---

# Iškabų techninis lapas

**Versija: 2026-10-16 v299** (v299, Rytis 2026-10-16: „statmenas rėmas nuo I dedasi po X, kad kuo mažiau matytųsi; po E dar vienas horizontalus rėmas (2 taškai + laido išvestis); wall frame (7) punktyru, po 50 mm trumpesnis nuo galų" - braizyti_begeliai: antras statmuo po kraštine raide su didžiausiu uždengimu, horizontalus bėgelis pailgai daliai, l_hang sienos rėmas punktyru + matmuo + {WALL_L_M}. v298, Rytis 2026-10-16: „jei dedasi statmenys, jų turi būti 2 vnt. - rėmas turi būti stabilus; antras po I raide gale" + „atnaujink RAL spalvų paletę, RAL 5008 labiau pilka nei mėlyna" - braizyti_begeliai: vienas statmuo -> antras per tiesų stiebą kitame gale; assets/ral_classic.json (visa RAL Classic, 213 spalvų; 5008 buvo nepaletėje -> pilka #888888), nežinomas RAL -> patikra 18; Order 33580 EXLANTIX pataisytas. v297, Rytis 2026-10-16: „E brūkšnelis kabo ore, taip negalima, kiekviena dalis turi tvirtintis prie rėmo" - braizyti_begeliai: kiekviena dalis tikrinama, ar liečia rėmą; jei ne - statmuo per dalies vidurį tarp artimiausių bėgelių (T forma, jei bėgelis iš vienos pusės); patikra 18 KONSTRUKCIJA (K.SHEET_ERR); {RAIL_H_M}; Order 33580 EXLANTIX pataisytas. v296, Rytis 2026-10-16: „dokumente turi būti abidvi reklamos" - Order 33580: OMODA | JAECOO (1 / 2) + EXLANTIX (2 / 2) viename ALT0000_Order_33580.pdf (K.merge_sheets); vieno užsakymo kelios iškabos - vienas dokumentas; patikra: skaičius be vieneto lentelėje; p6_lhang pastaba su mm. v295, Rytis 2026-10-16: Alfa Neon Order 33580 OMODA | JAECOO 6712 x 375 (P6 atskiros raidės) pergeneruota pagal dabartines taisykles - lapas ALT0000_Order_33580_OMJE26-01001.pdf; braizyti_begeliai: trijų eilių išdėstymas ilgoms žemoms iškaboms (didelis 3D), be tuščios Power eilutės per_letter, LED užrašas po grupe be rėmo. v294, Rytis 2026-10-16: Securitas Order 226030 pataisymai - rėmas □30x30x2 stačiakampis su ausėlėmis, ausėlių skylės Ø8, RAL 9006 (spec_226030.json); patikra 16 NETELPA LANGELYJE (K.OVERFLOW -> .art.json). v293, Rytis 2026-10-16: „išsaugok taisykles ir naudojimo logiką, kad kitą kartą nebūtų daroma su senomis taisyklėmis" - references/lapo_taisykles.md (galiojančių taisyklių suvestinė + darbo eiga), scripts/taisykliu_lint.py (seni šablonai generatoriuje), patikra 13 BLOKAS NECENTRUOJAMAS / 14 SENA TAISYKLĖ / 15 SUVESTINĖ PASENUSI, K.section_block / K.centered(frame=True) / K.merge_sheets, scripts/versija.py; braizyti_begeliai profilių blokai ir folded_vinyl pjūvis centruojami. v292, Rytis 2026-10-15: Bodø 226045 - laido išvestis Ø11 PAČIAME VIRŠUJE (kairė šoninė briauna, 50 nuo viršaus; `references/klientai/clasohlson.md`); didesnė paraštė DEŠINĖJE: `LE.distribute(margin=(0.5, 1.0))`, stulpelio plotis >= vaizdo pavadinimo / mastelio eilutės (`LE.title_w`) - užrašai neišlenda prie rėmo. v291, v291, Rytis 2026-10-15: „kodėl neimama naujausia informacija? ... paaiškink ir sutvarkyk, kad nesikartotų" - TAISYKLĖ 34: taisyklės vykdomos KODU, ne tik tekstu: `K.centered` (pjūvis bloko centre, matuojant tikrą turinį), `leader` balionų atitraukimas, `T` dešimtainis kablelis, `cell_units` vienetai lentelėse; patikra 9 BALIONAI PERSIDENGIA, 10 DEŠIMTAINIS TAŠKAS, 11 VIENETAS NENURODYTAS, 12 NECENTRUOTA / NETELPA BLOKE; Bodø 226045, Joker 226057, Securitas 226030 pergeneruoti - 0. v290, v290, Rytis 2026-10-15: „proporcijos vis dar netinkamos" - TAISYKLĖ 33 papildyta: detalių zona (tarp galo ir 3D) skaidoma į stulpelius pagal turinį (Bodø: [TRAFO BOX prie laido + DETAIL A apačioje] | [LOGO DETAIL centruota]), ne viskas į vieną stulpelį; DETAIL mastelis - didžiausias ISO, bet detalė ne aukštesnė nei 0,6 projekcijų (`pick_scale(cap_pt=)`, hierarchija - Bodø logo 1:5 atmestas, 1:10). v289, v289, Rytis 2026-10-15: TAISYKLĖ 33 - ADAPTIVE CAD DRAWING LAYOUT (privaloma): masteliai / stulpeliai / tarpai skaičiuojami iš geometrijos + anotacijų (`scripts/layout_engine.py`), jokių fiksuotų koordinačių; pilnas tekstas `references/adaptive_layout.md`; pirmas taikymas - Bodø 226045. v288, v288, Rytis 2026-10-15: papildomos detalės (LOGO DETAIL ir pan.) dedamos PO esama detale tame pačiame stulpelyje (ne įsprausti tarp vaizdų); visi vaizdai su paraštėmis - laisvas plotas skirstomas VIENODAIS tarpais tarp stulpelių (bodo.py G_), vaizdų pavadinimai vienoje eilėje; Bodø 226045. v287, v287, Rytis 2026-10-15: „trūksta detalesnių logotipo matmenų" - prie logotipo iškabos pridėti LOGO DETAIL 1:10: ženklo / žiedo / eilučių aukščiai ir tarpai, žiedo Ø ir padėtis, pločiai; matmenys matuojami iš logotipo kontūro (nieko neišgalvoti); vertikalios grandinės toje pusėje, kur jų nekerta kitų detalių išvadinės; Bodø Order 226045. v286, v286, Rytis 2026-10-15: vertikaliai (aukštai siaurai) iškabai 3D VIEW - dešinėje, praktiškai TOKIO PAT dydžio kaip priekio / galo projekcijos (tas pats aukštis), ne mažas po detale; Bodø Order 226045. v285, v285, Rytis 2026-10-15: Clas Ohlson Bodø Order 226045 - P8 special ant vertikalios folded plokštės 515 x 2380, 2 vnt. (`scripts/projektai/clasohlson_226045_bodo/`, analogas Horten 1); proporcijų etalonas - `assets/clasohlson_proporcijos.pdf` (ne seno pokalbio įkėlimas); P8 detalių geometrija hairline. v284, v284, Rytis 2026-10-15: „didelė skarda: viršutinės dalies išklotinė turi tilpti į 3000x1500 lapą" - folded dalys skaidomos taip, kad tilptų MAŽIAUSIAME lakšte (3000x1500, tik tada 4000x2000); sandūra grafikos tarpe, >= 50 nuo grafikos (`folded_vinyl.split_rows`, spec `sheets_mm`); Joker 226057 A: 1400 + 800. v283, v283, Rytis 2026-10-15: TAISYKLĖ 32 - `scripts/folded_vinyl.py` bendras folded plate + lipdukai generatorius (Joker order 226057 eskelokk A 2400x2200 su sandūra, B 1200x2200); RAL 1020 bibliotekoje. v282, v282, Rytis 2026-10-15: TAISYKLĖ 31 - mišrūs priekiai vienoje iškaboje ant U bėgelių (Securitas, BF Order 226030) - katalogas A, šablonas `assets/spec_misrus_priekiai_U.json`, etalonas. v281, v281, Rytis 2026-10-15: BOM kiekyje - TIK rezultatas (sunaudojimas su atliekomis, be lakšto matmenų); bėgelių / trafo box apdaila su NCS / PMS kodu - be „RAL" priešdėlio ir be „matt"; Order 226030: apskritimų rėmas NCS S 6005-R80B kaip raidžių, plėvelė „Perforated foil, Gel'UV print Day/Night, black" (spalva langelyje - `lapas_core.PLEXI`). v280, v280, Rytis 2026-10-15: tarpas tarp FRONT ir SIDE VIEW >= 90 pt (0,13 priekio pločio) - nebesugrūsta; spalvota plexi (pvz. Plexiglas GS 3H67) BOM MATERIAL langelyje su spalva (`lapas_core.PLEXI` - naują kodą įrašyti ten); trafo laidų ilgis BOM be apvalinimo (1.5 m, ne 2 m); Order 226030: 12V 1.5 m iš apskritimų apatinio ir raidžių viršutinio bėgelio + trafo box, 1 vnt. v279, v279, Rytis 2026-10-15, BrandFactory Order 226030 Securitas: `"layout": "rows"` - viršuje kairėje FRONT (+ šoninis), dešinėje REAR (tas pats mastelis), apačioje per visą plotį DIDESNIS 3D; `"view_scale"` - priverstinis vaizdų mastelis (pvz. 20); plokštesnis 3D kampas `"view_yaw": 22, "view_pitch": 12` plačioms iškaboms. Projektas `scripts/projektai/brandfactory_226030_securitas/`. v278, v278, Rytis 2026-10-15: „visos 3 projekcijos proporcingai plote: priekio ir galo didesnės, 3D mažesnė" - `"layout": "columns"` renkasi DIDŽIAUSIĄ priekio / galo mastelį (vienodas abiem), 3D ~0,85 priekio pločio, kairė sritis ~56 % lapo su vaizdais centre, 3D - dešinės srities centre. v277, v277, Rytis 2026-10-15, Securitas pataisymai: rėmas „tik U profilis" = grupės `"ears": false` (ausėlių nededama, kol nenurodyta); kliento bėgeliai ignoruojami - rėmas pagal taisyklę (`auto_frame`), PILNAVIDURIŲ elementų (apskritimai, blokai) bėgelių galai kuo arčiau krašto (abu kampai >= 10 mm viduje, `auto_remas.py`); keli pjūviai lape - VIENODAS mastelis (`p6_ref.K_FIX`); `"layout": "columns"` - kairėje FRONT virš REAR, dešinėje didelis 3D; mišrūs priekiai - A/B (PVC bortelis) eilutės lieka, jei bent viena grupė 5S. v276, v276, Rytis 2026-10-15, Securitas Sarpsborg: VIENOJE iškaboje skirtingi priekiai - `braizyti_begeliai.py` grupės `"front"` (pvz. apskritimai `P6 color`, raidės `5S+foil`) ir grupės bėgelių spalva `"rail_ral"`; pjūvio langelyje po pjūvį kiekvienam priekiui; BOM `{RAILS_M_<grupė>}`; vienodi nešantieji bėgeliai galiniame vaizde - vienas matmuo `n× L`; projektas `scripts/projektai/securitas_sarp/`. v275, v275, Rytis 2026-10-15: TAISYKLĖ 30 - CAD matmenavimas pagal ISO 129-1 (`references/cad_matmenavimas_ISO.md`): kablelis, `n× v (= L)`, taškai tarp mažų tarpų, be dubliavimo, jokios linijos ant linijos, pjūvio žymės už matmenų eilių; `patikra_lapas.py` 6-8 patikros. v274, v274, Rytis 2026-10-15: šviesdėžės rėmas pagal dydį - 1550 x 470 -> □40x40x2, kojos kaip rėmas (`moduliai_pendant.md`). v273, Rytis 2026-10-15: `scripts/pdf1to1_dxf.py` - 1:1 PDF sluoksniai -> CAD DXF (+ griovelio sluoksniai iš `griovelis_b.py`); 1:1 dugno sluoksnio vardas pagal tikrą įleidimą (P10 - 5 mm). v272, Rytis 2026-10-15: `sviesdeze.py` - siauro pjūvio A-A gylio matmuo nuleidžiamas (grandinės žymos laiptuotos), 2 eilė paslenkama; danbolig DB-0001 1550 x 470 x 100. v271, Rytis 2026-10-15: taisyklė 29 - pavyzdys perimamas tik jo tema, visa kita - patvirtinti standartai; P6 ant L profilių pjūvis = etaloninis P6 (`p6_ref` no_rail + after) + L rėmas; OMJE BOM pozicijos = pjūvio balionai. v269, Rytis 2026-10-15: P6 ant L profilių kaip VOLVO BILB26-01001 - `"mounting": "l_hang"` (L 40x40x2 rėmas užkabinamas ant fasado L 40x40x2, U 15x15x2 laidams, be statmenų), pjūvis `p6_lhang.py`, etalonas `BILB26-01001_P6_ant_L_profiliu.pdf` (žr. `moduliai_montavimas.md` 4 sk.); katalogo B: P6 ant L profilių, P6 palaidos raidės. v268, Rytis 2026-10-15: P6 atskiros raidės - tvirtinimo Ø3.2 ir laido D11 skylės dugne skaičiuojamos lape ir tos pačios perduodamos į `p6_dxf.py` (rails json `fix_holes` / `cable_holes`) ir 1:1 šabloną; kiekviena dalis turi laido išvestį (žr. `references/moduliai_montavimas.md` 3 sk.). v267, Rytis 2026-10-15: produktų katalogas `references/produktu_katalogas.md` - tikslūs raktažodžiai paruoštiems produktams (A), produktai su patikslinimais (B), seni pavadinimai (C); `ziniu_paieska.py` rodo katalogą pirmą. v265, Rytis 2026-10-15: TAISYKLĖ 0 - prieš kiekvieną užsakymą `scripts/ziniu_paieska.py` (šeima, visi generatoriai / aprašai, taisyklės pagal naujumą, jau daryti projektai ir etalonai, klaidos); pagrindu - geriausias analogas, naujesnė taisyklė viršesnė, generatorius pirmiausia atnaujinamas, rezultatas ne prastesnis už patvirtintą; Ryčio pataisa = bendra taisyklė visai šeimai. v263, Rytis 2026-10-15: LED ir PSU lapuose - tik „LED" / „PSU" + kiekis ir išdėstymas, be modelių ir specifikacijų (konkrečiai - tik paklausus; taisyklė 28). v261, Rytis 2026-10-15: taisyklė 28 - spalvų kodai BOM visada nuspalvinti (NCS artinys `ncs_hex`, 3M 100-54 / PMS 872), plėvelė - MATERIAL kodas, FINISH „-" (be Pantone); šviesdėžėse LED be pavadinimų. v259, Rytis 2026-10-15: šviesdėžės stiklo varžtai per perimetrą pagal folded plate formulę (50 nuo kraštų, ~300); laido išvestis ~230 V 1,5 m, trafas ant pado po kojų uždengimais (`"psu": "plate"`). v257, Rytis 2026-10-15: taisyklė 27 - 3D vaizdų žymos (SIDE A / B) šalia objekto, niekada ant jo - `lapas_core.side_label_3d`, `sviesdeze.py` ir `p10_lightbox_doublesided.py`. v255, Rytis 2026-10-15: taisyklė 26 - šviesdėžių taisyklės bendros visiems generatoriams (prieš darbą skaityti visus šviesdėžių modulius); `sviesdeze.py`: kojos PER galinį statmenį (1.4 tarp kojų), TOP VIEW po FRONT VIEW A + didelis EXPLODED, stiklo varžtai pagal dydį. v253, Rytis 2026-10-15: šviesdėžė - `"psu": false` (trafo nereikia, 12 V tiekia klientas), kojos kaip rėmas □30x30x2, įvirintos į galinį statmenį (suvirinimo žymos + pastaba lape), pastaba klientui kur išeina laidas (`cable_note`). v252, Rytis 2026-10-15: P10 be bėgio - ilgasriegiai pagal Rytio etaloną `assets/etalonai/P10_be_begio_ilgasriegiai_danbolig_Rytis.pdf` (linijos ~12 % / ~82 % x aukščio, lanko ruože - galuose, g kojelė, i taškas įstrižai); šviesdėžė - kojos ĮVIRINTOS Į GALINĘ RĖMO DALĮ (`leg_in` 0, galinis statmuo 1.4), tarpas iki pado 100 mm (žr. `references/moduliai_pendant.md`). v251, Rytis 2026-10-15: P10 be bėgio - ilgasriegiai VIENOJE LINIJOJE viršuje ir apačioje (bendros visoms raidėms, į ploto centrą); 3D vaizde nuoroda `note_3d` (dažymas 2 sluoksniais); pjūvio balionai pagal aukštį - linijos nesikerta; `sviesdeze.py`: kiekis juodame bloke, `sheets` (vienas dokumentas su kitomis pozicijomis), `frame_hex` / `cover_hex` / `cover_finish` (NCS spalvos), logo `finish`; vieno užsakymo pozicijos - VIENAME PDF. v250, Rytis 2026-10-15: P10 be bėgio - ilgasriegiai LABIAU Į PLOTO CENTRĄ (ne krašte, ne horizontalia linija), raidei 4 (ne 5), siaurai / smulkiai daliai 2, g kojelėje papildomas, i taške 2 + sava laido išvestis; maitinimas „12V per letter + trafo box". v249, Rytis 2026-10-15: P10 BE BĖGIO (blokinė reklama, `"mounting": "none"`) - Alu dugnelyje ilgasriegiai `p10_rod` dviem horizontaliomis linijomis, ne ant laidų išvesčių, + popierinis šablonas, 1:1 sluoksnis `4_THREADED_RODS_*`; šviečiantys šonai `return_hex`, dažytas priekis `face_hex`; BN PO 3295 danbolig (žr. `references/moduliai_p10_raides.md`, `references/klientai/bn_skilte.md`). v248, Rytis 2026-10-15: NAUJAS DOKUMENTO BLANKAS - antraštės lentelės apačia: DATE | DIDELIS JUODAS blokas su kiekiu („40 pcs.", balta) | DIDELĖ „Sheet 1 / 2"; DRAWN / CHECKED nebėra, REV. - eilutėje su SCALE / FORMAT / PROJECTION (`lapas_core.title_body`, visi generatoriai, ir `braizyti_lapa.py`); tuščias blankas `assets/blankas_A3.pdf` (`scripts/blankas.py`). v247, Rytis 2026-10-15: Leapmotor kliento failas papildytas 2026-10-15 sprendimais (poz. 20 P10 ant vieno akrilinio bėgelio, įleistos skylės, smeigės pagal formą, LED griovelio simuliacija; neatsakyti klausimai). v246, Rytis 2026-10-15: smeigės - PANAŠIOS RAIDĖS tvirtinamos vienodai (P kaip R: stiebas + dešinė pusė / koja); išilginiame štriche taškai GALUOSE (ten stiebai / kampai); MAŽA raidė (< 200 mm, pvz. M ~170) - užtenka 3; smeigės ir STATMENYSE (L stiebą užima statmuo -> taškas statmenyje, griovelis statmenyje šalia ašies); tiksli statmens puzzle galvutės zona. v245, Rytis 2026-10-15: akrilinio rėmo smeigės PAGAL RAIDĖS FORMĄ (kvadratas 4, trikampis 3 - supaprastinto gaubto kampai, 2..6, ilgoms + kas 500), ARTI CENTERLINE (kertančio štricho vidurys, ne prie krašto), ant bėgelio - VIENA HORIZONTALI LINIJA (papildoma linija tik raidei, kuriai bendroje < 2); vienas bėgelis mažoms reklamoms nuo 55 mm (platinamas po 5). v244, Rytis 2026-10-15: akrilinis rėmas - KIEKVIENA raidė / logotipo dalis tvirtinama >= 2 smeigėmis (ilgos - kas ~400), smeigės bet kur bėgelio juostoje toliausiai viena nuo kitos (ne griovelio zonoje); vienas platus bėgelis platinamas (60 -> +10), kol visos dalys gauna >= 2; P10 pjūvis - Alu 1,5 dugnelis ĮLEISTAS į 30 mm bloką (kraštas ~5 mm pagal etaloną), smeigė nuo raidės krašto >= kraštas + 1. v243, Rytis 2026-10-15: akrilinis rėmas MAŽOMS raidėms - jei tarp dviejų bėgelių lieka mažiau nei bėgelio plotis, naudojamas VIENAS bėgelis 60 mm (platesnis, jei trukdo tvirtinimui ar laidams), statmenų nėra (`"single_w"`). v242, Rytis 2026-10-15: P10 raidės `braizyti_begeliai.py` - spec `"front": "P10"` (30 mm plexi blokas, šonai RAL, be Alu šonų), pjūvis `scripts/p10_raides.py` (rėmas su įleista skyle, Alu 1,5 nugara su smeige, LED griovelis iš galo `"p10_groove"`), gylis 30 + rėmas; Leapmotor poz. 20 juodraštis. v241, Rytis 2026-10-15: AKRILINIS RĖMAS - raidės prisukamos per ATSKIRAS ĮLEISTAS SKYLES (bėgelio ašyje po raidėmis Ø5 kiaurai + Ø12 x 15 iš galo veržlei; ne T griovelis), laidų griovelis nugaroje paslinktas nuo ašies, ovalios skylės kiaurai laidui prie raidžių; 2 lapo SECTION E - bėgelis ties smeige. auto_remas: eilutės aukštis - dažniausio aukščio grupės mediana (v238 trafaretai + Leapmotor ženklas). v240, Rytis 2026-10-15: P10 raidės - gylis VISADA 30 + rėmo storis; laidų griovelis akriliniame rėme 6 x 3,5 + ovalios skylės kiaurai (kaip etalone); akrilinis rėmas - T griovelis (ištisinis ar įleistos skylės - tikslinama), `moduliai_p10_raides.md`). v239, Rytis 2026-10-15: P10 RAIDŽIŲ (30 mm plexi) ant akrilinių bėgelių ETALONAS - `assets/etalonai/P10_Boots_ALT6739_akriliniai_begeliai.pdf`, aprašas `references/moduliai_p10_raides.md` (LED linija per vidurį aštriomis sankirtomis iki galų, plačios dalys - lygiagrečios eilės; bėgelis 20 mm su T-grioveliu 5x5 + 12x15, laidų griovelis 6 x 3,5, puzzle klijuojamos jungtys). v238, Rytis 2026-10-15 'kodėl vėl rėmai ne pagal taisykles?' (OMODA / EXLANTIX): PRIEŽASTIS - auto rėmas trafaretinio šrifto dalis (E juostos, O pusės, J pėda) laikė atskiromis eilutėmis (klaida / netikri bėgeliai), o vietoj generatoriaus taisymo rėmas buvo sudėtas RANKA (bėgeliai netęsti iki kraštinių raidžių, statmenys savo nuožiūra - pažeistos taisyklės 1, 2, 12). DABAR: `auto_remas.rows_of` - eilutės pagal aukščio intervalų persidengimą (aukščiausi pirmi), eilutės matas - tik pilno aukščio raidės; `braizyti_begeliai` - kelių dalių raidė (dalys persidengia x) = viena raidė kraštinių ausėlių zonai. RANKINIO rėmo (`groups[].rails`) NEDARYTI be Ryčio nurodymo - taisyti generatorių. v237, 2026-10-15: Alfa Neon PO 33580 poz. 20 EXLANTIX (P6 ant rėmo RAL 5008, stiklo fasadas) + kliento failas `references/klientai/alfaneon_rsa_drammen.md` (OMODA | JAECOO / EXLANTIX). v236, 2026-10-15 Alfa Neon PO 33580 OMODA | JAECOO (trafaretinis šriftas, P6 atskiros raidės ant L profilių): `led_km.py` - kiekio užrašas ne ant raidės, kai raidė iš kelių dalių vienoje x juostoje (O iš 2 dalių, E iš 3 juostų): virš -> po -> dešinėje; kiekiams po raidėmis matmens linija nuleidžiama; projektas `scripts/projektai/omoda_33580/`. v235, Rytis 2026-10-15: P10 (30 mm plexi) raidžių LED griovelis - „kampai lieka tušti, netolygus apšvietimas": `scripts/griovelis_sim.py` - APŠVIETIMO SIMULIACIJA (difuzija opaliniame akrile, šviesa tik akrile, šonų nuostoliai; U = P5 / mediana, tamsu < 0.6 kiekvienai raidei); `scripts/griovelis_b.py` - griovelio VARIANTAS B (griovelio zonos skeletas: aštrūs kampai, galai iki sienelės; plačios dalys >= 40 mm - kontūro žiedas w/4 nuo krašto, 2 eilės). Leapmotor poz. 20: A U 0.38 / tamsu 16 %, B 0.41 / 15 %, B + balti (atspindintys) šonai viduje 0.55 / 7 % - šonų atspindys svarbiausias; modelis kokybinis, kalibruoti pavyzdine raide. v234, Rytis 2026-10-14: Leapmotor kliento failas papildytas v232-v233 sprendimais (atskiri statmenys su puzzle, P6 pjūvis, 2 lapas, poz. 30 LED / exploded). v233, Rytis 2026-10-14: P6_8mm / P6_8mm+foil / P6_8mm color PERVADINTI į **P6 / P6+foil / P6 color** - profilis P6 VIENAS, tvirtinimai įvairūs (bėgeliai U / □, akrilinis rėmas, folded, į fasadą); senas kodas - sinonimas (`p6_front.py`). Akrilinis rėmas - 2 LAPAS „ACRYLIC FRAME - PARTS & JOINTS": dalių vaizdas iš galo (R - bėgelių dalys, V - statmenys, J - jungtys), DETAIL C (bėgelių puzzle J1), DETAIL D (statmuo -> bėgelis), SECTION E (griovelis), juostoje blokas „WHY / WHERE THE FRAME JOINS" + dalių BOM; 1 lape nuorodos C / D. v232, Rytis 2026-10-14: akrilinio rėmo statmenys / įstrižai - ATSKIROS detalės, į bėgelius jungiami PUZZLE (taupoma medžiaga); P6 ant akrilinio rėmo pjūvis - ETALONINIS (`p6_reference` square, akrilo bėgelis pilnaviduris skaidrus, `p6_ref.ACRYLIC`), ne senas `p6_typical`; P10_lightbox_singlesided - LED moduliai matomi pjūvyje A-A ir DETAIL B, EXPLODED VIEW - kuo didesnis (dešinė kolona per visą aukštį), TOP VIEW - 2 eilėje. v231, Rytis 2026-10-14: akrilinis rėmas - statmenys NE po kiekviena raide, o žingsniu `v_pitch` 1000 mm per stiebus; jungtys pagal lakšto ilgį pažymėtos (J1.. + dalių grandinė); griovelis 8 x 10; P10_lightbox_singlesided - priekis prisukamas PER PERIMETRĄ (4 atlankai), LED ant dugno galinės plokštumos, varžtų tipas nebraižomas (standartas). v230: P10_lightbox_singlesided generatorius `scripts/p10_lightbox_singlesided.py` (2 lapai + gamybos DXF, logotipas iš kliento vektorinio PDF) - Leapmotor poz. 30. v229, Rytis 2026-10-14: AKRILINIS raidžių rėmas (Leapmotor) - `braizyti_begeliai.py` mounting "acrylic": statmuo po kiekviena raide, puzzle po raidėmis, Ø8 kas antrame tarpe, griovelis, DXF; „Bendrinės taisyklės" 25. v228, Rytis 2026-10-14: naujas klientas Alfa Neon / Leapmotor (PO 33577) - `klientai/alfaneon_leapmotor.md`: P6 tūris 60, 12 V 1,5 m + TRAFO BOX, skaidrus orgstiklo 20 mm rėmas su puzzle jungtimis (0,2), laidų grioveliais ir Ø8; P10_lightbox_singlesided parametrai atsakyti. v227, Rytis 2026-10-14: P10_lightbox -> P10_lightbox_doublesided (visur: kodas, dokumentai, testai); nauja pozicija P10_lightbox_singlesided (patvirtintas eskizas, `moduliai_p10_lightbox_singlesided.md`). v226, Rytis 2026-10-14: šviesdėžių dokumentų forma PATVIRTINTA - etalonai TEST_P10_lightbox_doublesided(_B), TEST_sviesdeze_700x370_kojos, TEST_sviesdeze_500_logo (+ gamybos DXF) įrašyti į repo; „Bendrinės taisyklės" 24. v225, Rytis 2026-10-14: šviesdėžių 1 lape nebėra rėmo ir plate / flange vaizdų (jie 2 lape) - 1 eilė per visą plotį, didesnis mastelis. v224, Rytis 2026-10-14: visų šviesdėžių dokumentuose 2 lapas - detalus CAD rėmo brėžinys: šonas, galas su mounting plate matmenimis, izometrija („Bendrinės taisyklės" 24); `sviesdeze.py` ir `p10_lightbox_doublesided.py`; r3d `flat`. v223, Rytis 2026-10-14: visų šviesdėžių dokumentai - VIENAS A3 lapas pagal TEST_P10_lightbox_doublesided_B („Bendrinės taisyklės" 23); `sviesdeze.py` perdarytas į 1 lapą, korpuso juostos išklotinė - gamybos DXF. v222, Rytis 2026-10-14: taisyklė 21 - exploded view rodo dažymą (rėmas viduje / korpuso vidus balti, kojos spalva; sviesdeze + p10_lightbox_doublesided); taisyklė 22 - 2 lapo projekcijos centruojamos savo blokuose. v221, Rytis 2026-10-14: šviesdėžės skyriuje (sviesdeze) įrašytos v220 taisyklės - 2 lapas CAD be spalvų, dažymas tik kojos / išorė, viduje balta; `frame_finish` = kojų spalva. v220, Rytis 2026-10-14: šviesdėžių 2 lapas kaip CAD - be spalvų, tik linijos; dažymas - tik kojos (ir išorė), rėmas viduje ir korpuso vidus balti - „Bendrinės taisyklės" 21-22. v219, Rytis 2026-10-14: šviesdėžės 2 lapas - be SECTION C-C, rėmas didesnis (automatinis mastelis) + vaizdas iš galo su tvirtinimo plokštėmis ir matmenimis. v218, Rytis 2026-10-14: visuose šviesdėžių dokumentuose EXPLODED VIEW ir pozicijos pjūvyje - P10_lightbox_doublesided 3 vietos (stiklas), 5S tipo (`sviesdeze.py`) VIRŠUS / APAČIA; „Bendrinės taisyklės" 20. v217, Rytis 2026-10-14: „uždengimai galioja visose situacijose kur yra kojų uždengimas" - bendras modulis `koju_uzdengimas.py`, naudoja `sviesdeze.py` (inset: plotis kojos + 10, aukštis kojų matmuo + 2t, briaunos su išpjovomis, BOM, `_gamyba.dxf` išklotinė) ir `p10_lightbox_doublesided.py`; „Bendrinės taisyklės" 19. v216, Rytis 2026-10-14: kojų uždengimo taisyklė (ilgis -5, plotis +10, Ø3.2, briaunos 10 su išpjovomis ties kojomis, exploded view atitraukti) įrašyta į „Bendrinės taisyklės" 19. v215, Rytis 2026-10-14: P10_lightbox_doublesided kojų uždengimo standumo briaunos ties kojomis IŠPJAUTOS (gylis = kojos/2 + tarpas - (plotis/2 - briauna), □30 -> 6 mm), atlankai remiasi į kojas (aukštis = kojų matmuo + 2t); exploded view uždengimai atitraukti nuo rėmo. v214, Rytis 2026-10-14: P10_lightbox_doublesided kojų uždengimas - plotis kojų profilis + 10 (20 + 20), viršuje 2 x Ø3.2, priekyje / gale standumo briaunos 10 mm; exploded view ir DXF išklotinė. v213, Rytis 2026-10-14: P10_lightbox_doublesided DETAIL B - pjūvis per visą gylį trijose vietose VIRŠUS / STIKLAS / APAČIA, ilgasriegiai prišaudyti iš vidinės Alu pusės (ne kiaurai priekį) - `moduliai_p10_lightbox_doublesided.md` 5b. v212, Rytis 2026-10-14: kojų uždengimas 5 mm mažesnis už kojų tarpą - po 2.5 mm iš abiejų galų (sviesdeze ir P10_lightbox_doublesided B); P10_lightbox_doublesided B - uždengimas A + B, BOM 11. v211, Rytis 2026-10-14: P10_lightbox_doublesided RĖMO VARIANTAS B - kojos siauresnės už dėžę, eina per galinį statmenį (jis iš dalių), vientisa montavimo plokštė = kojų matmuo, skylės min 4, siaurame pade šachmatine tvarka; spec `"legs": {"spacing": ...}` - `references/moduliai_p10_lightbox_doublesided.md` 3. v210, Rytis 2026-10-14: profilis P6_3mm PERVADINTAS į 5S visur (kodas, BOM, MAIN DATA, dokumentai, specai); 5S konstrukcija pagal Ryčio detalę `assets/konstrukcijos/5S_profilis.pdf` - priekis polikarbonatas 3 mm FR, PVC 3 mm bortelis ~15 įleistas 1 mm, šonas Alu 1 mm 2 mm nuo priekio krašto, tarpas 1 mm, varžtas 2.9 per Ø3; `p6_front.py`, `p6_vaizdas.body_inset`. v209, Rytis 2026-10-14 Thales: įėjimo pilono balta lovelė apačioje lenkiasi tik 20 mm (`Pyl.WBOT`), lapų MAIN DATA / pastabos - iš parametrų. v208, Rytis 2026-10-14 Thales: baltos lovelės (visos projekte) - viršus / apačia lenkiasi į vidų tarp šonų (folded --tb-inside), mėlynos - šonai į vidų; `thales_dxf.py`, `moduliai_pilonai.md`. v207, Rytis 2026-10-14 Thales: visi lankstiniai pagal folded v173, skylės Ø3.2 7 mm nuo krašto ir csk - „Bendrinės taisyklės" 18; `thales_dxf.py` / `thales_pylons.py` perrašyti. v206, Rytis 2026-10-14: v204 rėmo ir v205 TRAFO BOX taisyklės įrašytos į „Bendrinės taisyklės" (12, 17). v205, Rytis 2026-10-14: „PWM naudojamas ne visur" - ant TRAFO BOX „PWM" tik kai nurodyta (`trafo_box.pwm: true`), kitaip tik RAL - `references/moduliai_kiti.md` TRAFO BOX. v204, Rytis 2026-10-14 „LIETUVA": rėmas per visą ilgį, galiniai statmenys tik panaudojami (stiebas / įstrižas ant A kaip EXTRA), bėgeliai iki kraštinės raidės krašto atskirai - „Bendrinės taisyklės" 12, `auto_remas.single_verticals`. v203, Rytis 2026-10-14 testas „LIETUVA" 5S+foil, □40x40x2 + ears, 12V + TRAFO BOX: `braizyti_begeliai.py` - tuščias spec `qty` (nežinomas kiekis = tuščias langelis) nebelaužia strypų plano; testas `scripts/projektai/lietuva_p6_test/`. v202, Rytis 2026-10-13: „bus versija su kitokiu rėmu, P10_lightbox_doublesided, bet rėmo principas kitoks" - `moduliai_p10_lightbox_doublesided.md` 3: dabartinis rėmas = variantas A, kitas rėmo principas laukia aprašymo. v201, Rytis 2026-10-13: „reikia viską sutalpinti į vieną lapą" - P10_lightbox_doublesided VIENAS lapas: FRAME + LED, PLATE 1A ir EXPLODED VIEW perkelti į GA lapą, kitų projekcijų mastelis sumažintas (auto `scale_ga`), 2 lapas pašalintas - `references/moduliai_p10_lightbox_doublesided.md` 5a. v200, Rytis 2026-10-13: „sheet 2 išimti stiklą ir iš sheet 3 įdėti exploded view, turi likti tik 2 lapai" - P10_lightbox_doublesided vėl 2 lapai: 2 lape vietoj BASE + INSERT vaizdo - EXPLODED VIEW, 3 lapas ir surinkimo eiga pašalinti. v199, Rytis 2026-10-13: „reikia exploded view, nes niekas neaišku" - `p10_lightbox_doublesided.py` 3 lapas ASSEMBLY: sprogstamasis 3D vaizdas (`exploded()`, r3d, abi plonų detalių plokštumos `_slab`), balionai = BOM, STEP 1-6 surinkimo eiga, DETAIL B juostoje - `references/moduliai_p10_lightbox_doublesided.md` 5a. v198, Rytis 2026-10-13: „nėra detalizacijos ir suprantamo pjūvio" - `p10_lightbox_doublesided.py` perdarytas pagal `sviesdeze.py`: 2 lapai (GA: FRONT A / sienos / FRONT B, SECTION A-A per logotipą, 3D, TOP VIEW, DETAIL B išpjovos kraštas; FRAME + LED + PARTS: rėmas, C-C, plokštė 1A, Alu išklotinė, pagrindas + įdėklas) - `references/moduliai_p10_lightbox_doublesided.md` 5a; `sviesdeze.py` HM - matmens tekstas nebebraižomas dvigubai. v197, Rytis 2026-10-13: profilis pervadintas `P10_lightbox_doublesided` (yra ir P10 raidės); Ø8 žingsnis 100; spalvos pagal klientą, plėvelė pagal užklausą; GENERATORIUS `scripts/p10_lightbox_doublesided.py` - A3 lapas (SIDE A / sienos / SIDE B, pagrindas + ilgasriegiai, 3D A / B, pjūvis per išpjovą, Parts List) + gamybinis DXF (padėklai su išpjova, D3.2, D6 žymės, kojų išpjovos; pagrindai su Ø8; įdėklai); testas pagal etaloną `scripts/projektai/p10_lightbox_doublesided_test/`. v196, Rytis 2026-10-13: NAUJAS PROFILIS P10 - dvipusė šviesdėžė Alu korpusu (priekis / galas - folded plate principu, pusė tūrio) su išpjova ir 3 mm pagrindu + iškištu 8 / 10 mm plexi, tarpas 0,7, ilgasriegiai per Ø8 skyles, D6 mėlynos žymės, rėmas □30-60, DUOLITE - `references/moduliai_p10.md` (generatorius dar nesukurtas). v195, Rytis 2026-10-13: „kodėl toks netolygus tvirtinimo taškų dėliojimas?" - `p6_dxf.py` skylės tolygiai per zoną (p/2 principas), kojelės traukimas tik `--stems`, papildomos skylės tik reikšmingai neprispaustai daliai - „Bendrinės taisyklės" 16. v194, „Alytus," gamybinis DXF + LED: `p6_dxf.py` - elementui su laikikliu (kablelis) skylės IR ant laikiklio ašies (tolimame gale, ilgam - ir viduryje), ne tik 2 bėgelyje; `led_km.py` lapas - GOST šriftas, hairline (apskritimai, moduliai, laidai 0,1), turinys centruojamas vertikaliai, `patikra_lapas.py` 0 klaidų. v193, Ryčio eskizas „Alytus,": kablelio tvirtinimas T forma - bėgelis per visą kablelio plotį, laikiklis per jo vidurį, ausėlė prie laikiklio; plėvelės nesting PDF + DXF pateikiami kartu su lapu - „Bendrinės taisyklės" 2, 15. v192, Rytis 2026-10-13: „statmuo nuo apatinio bėgelio tik po kableliu, o ne pratęstas viršutinis" - kablelis / taškas už rėmo galo: tik artimiausias bėgelis tęsiamas iki jo + laikiklis per elementą (`auto_remas.py`), „Bendrinės taisyklės" 2. v191, Rytis 2026-10-13 „Alytus," pastabos: plėvelė ant atskirų raidžių - NESTING (`plevele.py --separate`); rėmas - bėgeliai per visą ilgį, VISI statmenys tarp bėgelių (ne galuose); po kableliu - statmuo (rėmo galas iki kablelio, abu bėgeliai); kraštinės ausėlės - pora tarp raidžių (tarp „u" ir „s"), ne po raidės snapeliu; statmenų ilgio žymos panaikintos - „Bendrinės taisyklės" 2, 12-15. v190, Rytis 2026-10-13 „Alytus," pastabos: „pasikartojančios klaidos: ne hairline projekcijose" - DVIGUBOS hairline linijos (P6 galinis vaizdas, 3D korpuso priekis) pašalintos + `patikra_lapas.py` tikrina „DVIGUBA LINIJA"; plėvelės FINISH langelis nuspalvinamas pagal plėvelės kodą eilutėje; kraštinės ausėlės prie rėmo kampo, kai bėgelis pratęstas konsole (`auseles.place_frame`), per-ausėlę apkrovos konsolėje - skyrius „Bendrinės taisyklės" 9-11. v189, testas „Alytus," P6_8mm+foil: `auto_remas.py` - kraštinė raidė v185 taisyklei tik iš pilno aukščio raidžių (kablelis tempė viršutinį bėgelį į orą); kablelis / taškas už rėmo galo, kertantis bėgelio juostą - bėgelis tęsiamas iki jo, galinis statmuo baigiasi ant bėgelio; testo kliento PDF iš šrifto - `scripts/projektai/welcome_p1_test/make_client.py` (tekstas, ilgis LEN arba raidės aukštis, šriftas, ne pilka spalva - kitaip stačiakampė „l" atpažįstama kaip bėgelis). v188, Rytis 2026-10-13: „įrašyk šitus atnaujinimus į skill, taisyklės pritaikomos visoms pozicijoms pagal situaciją" - v183-v187 taisyklės perkeltos į bendrinį skyrių „Bendrinės taisyklės v183-v187" + `references/moduliai_kiti.md` (P1), `references/stilius.md` (pjūvis centre), `references/moduliai_montavimas.md` (hangers). v187, Rytis 2026-10-13: HANGERS POZICIJOS - ta pati formulė kaip jų tvirtinimo skylių: žingsnis p = rėmo ilgis / n, nuo galų p / 2; prie raidžių centrų nebetraukiama - `references/moduliai_montavimas.md`. v186, Rytis 2026-10-13: P1 GALINIS VAIZDAS - dugnas NEDAŽYTAS PVC (šviesiai pilkas `PVC_RAW`), ne korpuso RAL; `backcol(g)` - `back_ral` tik nurodžius. v185, Rytis 2026-10-13: PROFILIO PJŪVIS VISADA CENTRUOJAMAS savo bloke (`K.p1_typical`; P6 etalonas jau centruojamas); RĖMAS IKI KRAŠTINĖS RAIDĖS GALO - raidė be stiebo (e, c, o) turi tvirtintis stabiliai, bėgelis tęsiamas iki jos galo (pvz. „e" uodegytės), rėmas gali dalinai matytis (`auto_remas.py`, Welcome spec); HANGERS kiekis: iki 2,5 m - 2, iki 4 m - 3, iki 7 m - 4, toliau ribų prieaugis +1,5 m (11,5 / 17,5 ...) - `assets/tvirtinimas.json`, `references/moduliai_montavimas.md`. v184, Rytis 2026-10-13 („Welcome" P1 pastabos): **P1 dugnas PVC 10 mm dedamas NEDAŽYTAS** - BOM FINISH „-" (v100 „back = šonų spalva" P1 netaikoma); **HANGERS galiniame vaizde - TIK punktyru** (kontūras ir skylės, be užpildo); **hangers ir P1 pjūvyje** (`K.p1_typical(..., bracket=pos)` - plokštumos virš / po bėgeliais, sienelė prie fasado, Ø6 ašinės, balionas); bėgelio balionas - galutinė (pernumeruota) BOM pozicija `_rail_pos()`, ne fiksuota 5. Rėmas „Welcome" - pagal Ryčio nurodymą (rėmas per visą užrašą, statmenys po pirma „e" ir „m" vidurine kojele) spec `groups[].rails`; v183 bėgelio aukščio paieška auto rėme PAŠALINTA (savo sugalvota taisyklė), lieka v49 11 mm ir apsauga nuo apversto rėmo. v183, Rytis 2026-10-13, patikrimas „Welcome", P1, Times New Roman, U 30x30x2 + hangers: `auto_remas.py` - bėgelio kraštas >= 11 mm nuo raidžių viršaus / apačios (v49 ir auto rėmui); antikvos mažųjų raidžių viršus apvalus / su serifu - jei ties štricho centru bėgelio galai kraštinėse raidėse netelpa (ilgis < 85 % geriausio), bėgelio aukštis ieškomas iki 30 % eilutės aukščio į vidų; galų vietos nerasta - perspėjimas, ne apverstas rėmas (buvo „rėmas -2280 ilgio"); BB / aa auto rėmai nepakito. Laikiklių (hangers) 2 lapas - objektų kontūrai hairline, `lapas_core.hatch` brūkšniai apkerpami geometriškai (patikra_lapas 16 -> 0 klaidų); rėmo RAL nežinomas - FINISH tuščias, ne „RAL ? matt". Testas `scripts/projektai/welcome_p1_test/` (`make_client.py` - tekstas iš šrifto kreivėmis 1 pt = 1 mm). v182, Rytis 2026-10-13: „atnaujink dokumentą pagal paskutinį skill" (Thales ALT8879): `patikra_lapas.py` - atkarpos už savo iškarpos (clip) netikrinamos, kliento grafikos sritys (`<lapas>.pdf.art.json`, rašo `lapas_core.save` per `place_pdf`) netikrinamos (v162 - neliečiama); `lapas_core.ext_line` - išvadinės toje pačioje tiesėje nebrėžiamos viena ant kitos (grandinė + gabaritas); `vchain(..., small="side")`; `pdf_drop_unused_fonts` - tušti kliento teksto blokai ir Type0 šriftai pašalinami (v171 - tik GOST); `pdf_explicit_colors` - ir įdėtinės formos; Thales: objektų kontūrai hairline, žemės linija 0,5, `gen_thales.sh` (art.json, qpdf) - patikra 0 klaidų. v181, Rytis 2026-10-13: KIWI - PAVADINIMAS tik „KIWI order NNNNNN" (FILE / DRAWING NO. ir failas `Drawing_KIWI order NNNNNN.pdf`), užklausos pavadinimas (pvz. „ALT Reklama KIWI 640 BYGNES") NERAŠOMAS; naujas užsakymas - VISOS kliento pastabos iš užsakymo PDF (rėmo spalva, laido spalva, vieta Outside, divided, apšvietimas, kitos) perkeliamos į dokumentą (MAIN DATA / BOM / užrašai), etalono reikšmės pakeičiamos - `references/etalonas_kiwi_226023.md` §0. v180, Rytis 2026-10-13: kolonos (Lanterne) FRONT VIEW laido išvesties NĖRA - ji vaizduojama kitoje projekcijoje (originalo 3D); `kiwi_226023/lanterne.py`, etalonas atnaujintas. v179, Rytis 2026-10-13: „tvirtinimo ausėlės kai kur kabo ore, taip neturėtų būti" - ausėlė / fitting plate VISADA privirinta prie bėgelio: skylė lieka originalo vietoje, plokštelė (`fit_plate_size` x `fit_plate_len`, 40 x 75) tęsiama iki artimiausio horizontalaus bėgelio ašies (`braizyti_begeliai._attach_plates`); nėra bėgelio šalia - perspėjimas. v178, Rytis 2026-10-13: folded išklotinės taisyklė galioja BET KOKIEMS matmenims; NUMATYTA „sides inside" (šonai į vidų, viršus / apačia ant viršaus), „top/bottom inside" - tik nurodžius (`folded_dxf.py --tb-inside`). v177, Rytis 2026-10-13: „balionai už vaizdo ribų; pataisyk LED atvaizdavimą profesionaliau su LED miniatiūromis" - LED INSTALLATION vaizdas PERBRAIŽOMAS iš originalo (`scripts/led_mini.py redraw`, spec `led_fragment.rules_py` - projekto spalvų taisyklės, pvz. `projektai/kiwi_226023/led_rules.py`): kontūrai / rėmas hairline, moduliai - MINIATIŪROS (korpusas + LED / lęšis, kryptis iš originalo), aprėptis - šviesūs apskritimai, PSU - pilkas stačiakampis, laidas 0,9 raudonas; moduliai, kiekiai, laidų vietos - tik iš originalo (kiekis tikrinamas). BALIONAI TIK UŽ VAIZDO RIBŲ (`balloon_auto(..., avoid=[vaizdo dėžė])`); `patikra_lapas.py` leidžia išvadinei kirsti VIENĄ matmens liniją statmenai (>= 45°, ne prie teksto), kai objektas iš visų pusių apsuptas matmenų. v176, Rytis 2026-10-13: folded gamybos išklotinė (v173-v174, `folded_dxf.py`, `--tb-inside`) PATVIRTINTA - testai 1000x1000x40, 1350x560x35, 1350x230x20 TB inside įrašyti `references/moduliai_folded.md`. v175, Rytis 2026-10-13: „matmenų linijos sugrūdamos viena ant kitos; nuorodų linijos lipa ant skaičių, fono, kitų linijų; kai kur ne hairline - buvo aptarta, vėl kartojasi. Kodėl?" - PRIEŽASTIS: taisyklės buvo tik tekste, generatoriai jų nevykdė, galutinės patikros nebuvo. DABAR: `scripts/patikra_lapas.py` (hairline, tekstas ant teksto, linija per tekstą, matmenys vienas ant kito, išvadinė per liniją) - PRIVALOMA, 0 klaidų; braizyti_begeliai: balionai 2 praėjimais (`K.balloon_auto`, be balto apvado), galinio vaizdo matmenų eilės globalios, žymos vienoje vertikalėje sujungiamos, matmens tekstas nekertamas išvadinių (už galo, jei viduje vietos nėra), apatinė grandinė - maži tarpai toliau nuo objekto, ašių grandinė ir laidai nesikerta; lapas_core: `TEXT_BOXES` / `text_free` - matmenų užrašai nededami ant jau parašytų tekstų, vchain kraštiniai maži tarpai - virš / po galu; įdėtų fragmentų linijos -> hairline (`gost_frag.hairline`). v174, Rytis 2026-10-13: folded „top/bottom edge inside" - viršus / apačia tarp šonų (W - 2t), šonai per visą H; `folded_dxf.py --tb-inside`, `references/moduliai_folded.md`. v173, Rytis 2026-10-13: FOLDED IŠKLOTINĖ PAGAL GAMYBOS ETALONĄ `assets/etalonai/folded_1000x1000x40_isklotine_gamyba.dxf` - lenkimo linijos = W x H, visi flanšai nuo lenkimo linijos gylis - t (40 -> 38), šonai (tarp skardų) iš galų t trumpesni (996), stačiakampė kampo išpjova, K faktoriaus nėra; 1000x1000x40 -> 1076 x 1076 (atitinka etaloną 0,0 mm²); `folded_dxf.py` perrašytas, `okq8.flat_dxf`, `references/moduliai_folded.md`; v172 šonų „38 gylio" aiškinimas atšauktas. v172, Rytis 2026-10-13: FOLDED - įsilenkiantys tarp skardų (šoniniai) flanšai t = 2 mm SEKLESNI (gylis 40 -> šonai 38, viršus / apačia 40) - gamybos lankstymo praktika; `folded_dxf.py`, `okq8.flat_dxf`, `references/moduliai_folded.md` (1000x1000x40 -> išklotinė 1069.05 x 1073.05). v171, Rytis 2026-10-13: „negaliu atsidaryti su CorelDRAW - corrupted file" - priežastis: pymupdf TextWriter įterpti Type0 (Identity-H) GOST šriftai, pervadinti `pdf_fix_fonts`; DABAR originalo fragmento GOST užrašai rašomi lapo reportlab sraute (`gost_frag.draw`, vienas TrueType „GOST Common"), fragmentas `K.place_pdf(..., under=True)` - po lapo turiniu; `gost_frag.overlay` NENAUDOTI galutiniams lapams; galutinis PDF - `qpdf --object-streams=disable`. Patikra: kiekviename puslapyje tik „GOST Common" TrueType (+ nenaudojamas Helvetica). v170, Rytis 2026-10-13: „laikytis org faile numatytų laido išvesčių, dabar 2 skirtingi variantai" - perdarant originalą laido išvestys TIKSLIAI originalo vietose: `cable_exits[].point: true` (taškas raidėje virš rėmo, kliento koord. perskaičiuotos iš originalo LED brėžinio), laidas į viršų, `up_mm` (tarp eilučių), `side` - užrašo pusė; skripto „bėgelio galo" variantas tada nenaudojamas. v169, 2026-10-13: `medziagos.sheet_fit` - rifliuotas (checker) Alu lakštas nesiūlomas, jei yra lygaus formato (folded 1000x1000x40 siūlė 2500x1250 rifliuotą). v168, Rytis 2026-10-13: „visur turi būti naudojamas GOST šriftas. visada objektus centruoti pagal projekcijų plotą, laikytis simetriškumo ir lapo užpildymo pagrindų" - originalo fragmentų Arial užrašai (kreivės) pašalinami redakcija ir perrašomi GOST Common ta pačia vieta (`scripts/gost_frag.py` prep / overlay, >= 8 pt; tekstai - projekto `frag_gost.py`); ketvirčių išdėstymas - kiekvienas vaizdas centruojamas savo ketvirtyje, pilono lape projekcijos centruojamos kairėje pusėje, fragmentas - dešinėje (vertikaliai irgi). v167, Rytis 2026-10-13: „atidarius su CorelDRAW vaizdas kardinaliai skiriasi, fonas mėlynas ir tekstas ne toks" - kliento PDF spot spalvos (RAL 9016 / RAL 5022 / PANTONE) nustatomos `/CSn cs` be `scn` (standartas: atspalvis 1), CorelDRAW importas to nepalaiko -> spalvos sumaišomos; `lapas_core.pdf_explicit_colors` po kiekvieno `cs` / `CS` įrašo aiškią pradinę spalvą (atvaizdas nepakinta), Thales `clip_src` naudoja - `references/stilius.md`. v166, Rytis 2026-10-13 (KIWI 226023): raidžių lapo išdėstymas FRONT | REAR / LED INSTALLATION | 3D - spec `led_fragment` {src, pno, clip}; □ profilio pjūvis pagal `rail.size` + `depth` (`p6_ref.RAIL_RATIO`, 40x20x2 rodomas 20 gylio); kolonos / pilono Parts List: Part Number | Description | Qty | FINISH (RAL pagal detalę), originalo aprašai - lentelėje. v165, Rytis 2026-10-13: „didelio pilono sheet 1 vaizdas neatitinka kliento užklausos" - 3D vaizdas KAIP KLIENTO „Principe" (tas pats žiūrėjimo kampas: iš kairės, šonas kairėje), korpuso spalvos - iš kliento lapo RAL legendos pavyzdžių (Thales RAL 5022 #2B2B5C, RAL 9016 #F4FBF7) - `references/stilius.md`. v164, Rytis 2026-10-13: Volvo spalvos - pagal užklausą (`klientai/alfaneon_volvo.md`); DSV nugara WN770 arba GS Wh14 - pagal tiekimą (`klientai/alfaneon_dsv.md`); PVC banner šviesdėžės STANDARTINIS GYLIS 200 mm (`moduliai_pvc_banner.md`); kiti v161 atviri klausimai - klausti tik kai iškyla projekte. v163, Rytis 2026-10-13: „linija centre, kad griovelis tolygiai eitų raidės viduje" - centerline STATMENA SIMETRIJA: statmenai linijai sienelė kairėje = dešinėje (`--perp` 8 iteracijos, iki mazgo šerdies 0,5 R); patikra `--asym` -> `<out>_asym.pdf` (žalia < 0,5 mm, oranžinė < 1,5, raudona > 1,5, pilka - sankirta / užbaiga). v162, Rytis 2026-10-13: „susigadino viskas - tekstai, grafika, gražink grafikos atpažinimą į pirminį tašką" - kliento grafikos įdėjimas GRĄŽINTAS į v155 (patvirtintas ALT8878): fragmentas = redakcija + `place_pdf`, failas po to NELIEČIAMAS (jokio kreivinimo / perrašymo), korpuso spalvos - kaip v155; `pdf_text_to_paths` tik jei fragmente liko gyvas tekstas - `references/stilius.md`. v161, Rytis 2026-10-13: DARBŲ ANALIZĖ (`DARBAI/uzsienio reklama` 2024-2026, 616 CDR) -> BENDRINIAI STANDARTAI (skyrius „Standartai (v161)": rėmo profiliai 20/30/40/60/80 x 2, kiti - tik pagal užklausą (`medziagos.is_standard_profile`); spalvos RAL / PANTONE / NCS; LED K - pagal klientą, kitaip 6500K; Mean Well - tik nurodžius; trafo dėžė su WAGO / PWM; WN770 - Volvo ir BN Skilte; B1 PC - tik BN Skilte; `ALT0000_00.00_RS` - pirminis dokumentas su order numeriu; gamyba dirba tiesiai iš .cdr) + KLIENTŲ STANDARTAI `references/klientai/alfaneon_volvo.md`, `alfaneon_dsv.md`, `bn_skilte.md`, `skyltkoncept.md`, `brandfactory.md`, `prancuzai.md` + MODULIAI `references/moduliai_pvc_banner.md` (STANDARTAS), `moduliai_termoformavimas.md`, `moduliai_pendant.md`. v160, Rytis 2026-10-13: „visa informacija ir paaiškinimai imami iš originalaus dokumento kuo mažiau iškraipant, pritaikomas tik pats dokumento stilius, lentelės, aprašymai perkeliami iš org. dokumento“ - ORIGINALO PERDARYMAS: rėmas (`groups[].rails` + `fit_plates`, `len`), lentelės su originalo stulpeliais (`bom_cols`, `bom_title`, spalvos pavyzdėlis `#RRGGBB` langelyje), pjūvio balionai pagal originalo BOM (`section_labels`), aprašymai / užrašai - originalo tekstu; nieko nepridėti iš savęs; KIWI 226023 `scripts/projektai/kiwi_226023/`. v159, Rytis 2026-10-13: KIWI order 226023 (3362 + 7-23 + Lanterne 6800) mūsų stiliumi - `scripts/projektai/kiwi_226023/`; `braizyti_begeliai.py`: galinio vaizdo žymos (vert.) iš skirtingų grupių nesidengia (`TAG_BOXES`), REAR VIEW pavadinimas netelpantis po vaizdu - dešinėje virš juostos. (v158, Rytis 2026-10-13: centerline LED grioveliui - „šviesti turi tolygiai VISA raidės plokštuma": po pagrindinių linijų APRĖPTIS - kiekviena zona, kuri nuo linijos toliau nei vietinis pusplotis + `--reach` (12 mm), gauna šaką (serifai, uodegėlės, kojelės) keliu per ploto keterą; galai - iki griovelio + sienelės ribos (`--wall`), be kilpų / zigzagų. v157, Rytis 2026-10-13: „pasikeitė spalvos didelio pilono, stovelio grafika vėl neatitinka ... kliento grafika VISADA turi atitikti visose projekcijose, vaizduose ir failuose" - Ghostscript kreivinimas atšauktas (perrašė ICC, išmetė overprint -> spalvos); tekstas -> kreivės savo moduliu `scripts/pdf_outline.py` (keičia tik teksto operatorius, likusi grafika baitas į baitą); korpuso spalvos (balta / mėlyna) imamos IŠ KLIENTO PDF (`client_fill`), ne ranka parinktas hex - `references/stilius.md`. v156, Rytis 2026-10-13: „kliento tekstus visada padaryk vektorinius, ne tekstą" - įdedamo kliento fragmento tekstai paverčiami KREIVĖMIS (`lapas_core.pdf_text_to_paths`, Ghostscript `-dNoOutputFonts`, spalvos nekeičiamos; jei nėra - `apt-get install -y ghostscript`) - `references/stilius.md`; Thales ALT8879 rev D: vienpusio pilono 3D baltas viršus per visą gylį. v155, Rytis 2026-10-13: „kodėl dokumente šriftas kitoks“ - lapo tekstas visur GOST Common; įdedamas kliento fragmentas dabar - atskiras PDF tik su matoma grafika (už iškarpos kliento antraštės / Arial užrašai ir matmenų užrašai pašalinami redakcija), kad Corel nerodytų svetimų šriftų - `references/stilius.md`. v154, 2026-10-13: centerline.py - jungtys tik tos pačios raidės viduje (Laba diena: i -> e šuolis), liestinė mazge iš trumpo ruožo (`--twin` 0.5; storiems šriftams - e kilpa). v153, Rytis 2026-10-13: patvirtinimas ALT8878 Thales - nešviečiančių gaminių paketas: lapai su ALT + DXF išklotinės (`thales_dxf.py`: lovelės su lenkimo atskaita, flanšai, PMMA), LED nėra - `references/patvirtinimas.md`. v152, Rytis 2026-10-13: ŽYMĖJIMAS IR MATMENYS - visi matmenys 12 pt (`DIM = K.F_DIM_MAIN`), grandinė 16 / gabaritas 36 pt, `lapas_core.hchain / vchain` maži užrašai be persidengimų, netelpanti grandinė - į pjūvį / DETAIL, tekstų ant projekcijų nėra - `references/stilius.md` (CAD žymėjimai, v152). v151, Rytis 2026-10-13: KLIENTO GRAFIKA LAPE - tik `lapas_core.place_pdf` (tikslus kliento PDF fragmentas, vektorius, 2D ir 3D), NE perpiešimas kontūrais - `references/stilius.md`; Thales rev C: tikslūs maketų rėmai, kliento matmenų linijos pašalintos. v150, Rytis 2026-10-13: Thales rev C - vienpusio pilono baltas viršus iki pilono galo, flanšo skylės 4 x Ø14 / 237, kliento ikonų balti elementai (kryžius) nebeišmetami - `references/moduliai_pilonai.md`. v149, Rytis 2026-10-13: CENTERLINE raidėms - `scripts/centerline.py kontūrai.pdf out` - linija per tikrą ploto vidurį kaip rašiklio brėžis: galai prasideda ploto viduryje (ne iš kampo), sankirtose be deformacijos (r, n, a - šaka tiesiai į kamieną, t - 2 tęstinės poros), DXF splainai. v148, Rytis 2026-10-13: ALT8877 - kai įkeltas GAMYBINIS failas (1:1 išklotinės / rėmas) - jo duomenys pakeičia ALT pasiūlymus (*), neatitikimai su kliento lapu - į QUESTIONS. v147, Rytis 2026-10-13: „neaišku kur kokios medžiagos, nėra vidinio rėmo, nėra paaiškinimų kaip pasidaro konstrukcija ... turėtų būti exploded view" - konstrukciniams gaminiams (portalai, pilonai su rėmu) PRIVALOMAS 2 lapas STRUCTURE: EXPLODED VIEW su pozicijomis, rėmo vaizdas su matmenimis, pjūviai per dėžę ir pagrindą (kabelio kelias), MATERIALS KEY, CONSTRUCTION / ASSEMBLY žingsniai, QUESTIONS TO CLIENT; ko nėra kliento brėžinyje - pažymėti „*" (ALT pasiūlymas) ir klausti; pavyzdys `scripts/projektai/okq8_alt8877/`. v146, 2026-10-13: OKQ8 height restriction ALT8877 - kliento brėžinys perdarytas į mūsų stilių (`scripts/projektai/okq8_alt8877/`); `lapas_core.T` - Ä / Ö (švedų) rašomi osifont, nes GOST Common glifai sumaišyti („Biltvätt", „FRI HÖJD"). v145, Rytis 2026-10-12: „bendras matmuo arčiausiai, jį kerta pagalbinių išvadinės - turėtų būti atvirkščiai; keli matmenys vienoje linijoje; nereikia matmenų tarp LED; šriftai nepataisyti; kojų uždengimas 5 mm siauresnis už tarpą tarp kojos plokštės ir korpuso" - grandinė arčiausiai, gabaritas už jos, viena linija - viena prasmė, visi matmenys 12 pt (`references/stilius.md`), `cover_gap` 5. v144, Rytis 2026-10-12: dvipusė šviesdėžė su ŽEMESNĖMIS kojomis ir kojų uždengimais - `sviesdeze.py` `"legs_type": "inset"` (rėmas 40x20x2, kojos □40x40x4 po skersiniais 50°, viena plokštė 140x340x5, trafo plokštelė, uždengimai 2 mm), etalonas `sviesdeze_dvipuse_kojos_zemesnes.pdf`. v143, Rytis 2026-10-12: opaque plėvelė (ORACAL 551 702) ant šviečiančio veido - sąmoningas nepersišviečiantis siluetas, neperspėti. v142, Rytis 2026-10-12: „įtrauk į skill plėveles: oracal 8500, oracal 551, avery, 3m 3630" - PLĖVELIŲ SPALVŲ BIBLIOTEKA `assets/pleveles.json` (ORACAL 8500 - 54, ORACAL 551 - 86, Avery 4500 TF - 38, 5500 QM - 65, 777 - 100, 3M 3630 - 78), `lapas_core.film_lookup / code_hex` - BOM langelių spalvos pagal kodą, CLI `scripts/pleveles.py`; skyrius „Plėvelių spalvų biblioteka". v141, Rytis 2026-10-12: „pagrindinis matmuo uždengiamas papildomais - paprasčiausias matmuo turi būti pirmas, po juo papildomi; šrifto dydžiai nevienodi; rėmas ir korpusas RAL 7024, grafika ORACAL 551 702" - matmenų eiliškumas ir šriftai `references/stilius.md`, šviesdėžės spalvos pagal RAL spec (`body_finish`, `frame_finish`). v140, Rytis 2026-10-12: šviesdėžės TŪRIS 500 x 500 dydžiui - 140 mm („kitaip labai sunku iššviesti pačius kraštus, kadangi LED pasikelia ant rėmo - kuo mažesnis tūris, tuo sunkiau tolygiai apšviesti foną"); logotipas iš kliento PNG abiejose pusėse (`scripts/vektorius.py` - potrace, `pip install potracer`; spec `"logo": {"file", "width", "color", "material"}`), logotipo matmenys priekio vaizduose, 3D. v139, Rytis 2026-10-12: „tvirtinimo varžtų per daug - 3 vnt. kraštinei; nuorodų linijos chaotiškos - optimalesnis sprendimas; LED apačioje ir viršuje; stiklas 3D pilkas, ne baltas; varžtai 3D kvadratiniai - turi būti apvalūs; vizualinė dalis gamyboje labai svarbi" - AUTOMATINIS ŽYMĖJIMAS 2 praėjimais (`lapas_core.balloon_auto / auto_place`, `references/stilius.md`), šviesdėžė: 3 varžtai kraštinei (24 vnt.), LED 2 eilės (12 x DS15, KPS-V12-36W), 3D baltas stiklas ir apvalios galvutės. v138, Rytis 2026-10-12: „projekcijose nesimato varžtų; 3D montavimo plokštės vientisos - nėra skylių nei rėmo kiaurymės; nuorodinės linijos turi būti įstrižos - dabar maišosi su matmenų linijomis" - išvadinės įstrižos (`lapas_core.balloon_column / tag_column`), šviesdėžė: varžtai vaizde iš sienos, TOP VIEW (nauja), pjūvyje A-A ir 3D, padai 3D su 4 x Ø10 ir vamzdžio anga. v137, Rytis 2026-10-12: „žymėjimai lipa ant projekcijų, pjūvio linijos ir žymėjimai sugrūsti, nuorodos linijos kertasi - atsinaujink CAD žymėjimus" - `lapas_core.cut_plane / balloon_column / tag_column` (taisyklės `references/stilius.md` „CAD žymėjimai"): pjūvio plokštuma tik už vaizdo, balionai stulpelyje už vaizdo surikiuoti (išvadinės nesikerta), tekstų ant projekcijų nėra; šviesdėžės juosta VIRINAMA prie rėmo - skylių per centrą nėra (D3.2 tik į PVC, 32 vnt.). v136, Rytis 2026-10-12, šviesdėžė: priekio vaizde pastabos „stiklas didesnis" nereikia (yra pjūvyje); turi matytis SIDE A ir SIDE B (skirtinga informacija pusėse) - abu priekio vaizdai (B veidrodinis) ir 3D iš abiejų pusių su užrašais; mastelis laisvai dėl lapo dizaino (GA 1:8); korpuso varžtų skylės D3.2 - juostos išklotinėje (2 lapas) ir vaizde iš sienos. v135, Rytis 2026-10-12: šviesdėžė „reikia detaliau - nėra rėmo matmenų, nėra bendrų matmenų tarp montavimo plokščių skylių x/y, neaišku kaip LED dedasi ir kokie; 5S - stiklas VISADA didesnis už korpusą, korpusas mažesnis 1,5-2 mm" - `sviesdeze.py` 2 lapai: GA (gręžimo schema iš sienos su visais skylių x / y ir bendrais matmenimis) + FRAME + LED (visi rėmo matmenys, LED vietos su žingsniu, pjūvis C-C, padas, pjaustymo sąrašas); korpusas = stiklas - 2 x `face_over` (1,5); LED - Kaisen DUOLITE (dvipusėms dėžėms) pagal lentelę `kaisen_led.json` -> `duolite`. v134, Rytis 2026-10-12: DVIPUSĖ ŠVIESDĖŽĖ NUO FASADO - `scripts/sviesdeze.py spec.json out.pdf` (etalonas `assets/etalonai/sviesdeze_dvipuse_nuo_sienos.pdf`, spec `assets/spec_sviesdeze_500x500.json`): kojos - pailginti rėmo □30x30x2 skersiniai su padais 100x100x8 (4 x Ø10 / 64), korpusas - 1,5 mm Alu juosta, 3 mm plexi abiejose pusėse kaip 5S (PVC juosta 3 x 15, savisriegiai). v133, Rytis 2026-10-12: „öppet t viršus, brūkšnelio kairė pusė, apatinis galas - šviesos pritruks; EXTRA E galiukai nešvies; 7 ir 3 bendroje grandinėje blankiau" - `ilp()`: LINIJOS GALAI (sienelės taškai, kurių 0,5 p aplinkoje < 42 % raidės ploto) - modulis <= 0,64 p (= taisyklė p/2 nuo galo); VIENODAS RYŠKUMAS GRUPĖJE - kiekvienos raidės modulių tankis (vnt. / veido plotas) >= 0,9 x grupės medianos, trūksta - ILP su min. kiekiu. v132, Rytis 2026-10-12: „LED dėliojama lovyje ... įdėjus į tūrį kampas blokuoja šviesą" - `ilp()`: taškas apšviestas tik jei linija modulis -> taškas (iš viršaus) eina raidės viduje (sienelės užstoja), visas veidas iki sienelės (0,03 p) turi matyti modulį <= 0,85 p; testuose išdėstymų nepakeitė - laukiama Ryčio patikslinimo, kurios vietos nešviečia. v131, Rytis 2026-10-12: „vistiek keletoje vietų nedėti LED, nors jie ten turėtų būti ... rekomenduok gamybos lygio sprendimą" -> „bandyk": `led_km.py ilp()` NUMATYTAS - LED išdėstymas kaip aprėpties optimizavimas (HiGHS): kiekvienas raidės taškas <= 0,6 p nuo modulio, moduliai >= 0,75 p vienas nuo kito, mažiausiai modulių, arčiau ašies; tuščių vietų nelieka. v130, LED testas „Alltid öppet" (Rytis 2026-10-12, P6, gylis 80): LED lape kiekis raidei, virš kurios yra kita forma (ö / i taškai) - rašomas PO raide, kad nesidengtų. v129, Rytis 2026-10-12: „vistiek dėliojimas labai keistas, neatitinka nei gamybinių, nei teorinių planų" - `led_km.py pack()` NUMATYTAS: APSKRITIMŲ PAKAVIMAS kaip Ryčio gamybos lapuose - Ø = žingsnis, apskritimai raidės viduje liečia vienas kitą ir kraštus, galas - apskritimas liečia raidės galą, siaura linija - ašyje; po to tolygus išdėstymas (stūmimas); senas `chain` + `coverage` - tik spec `"layout": "chain"`. v128, Rytis 2026-10-12: „taisyklės tik rekomendacijos ... labiau žiūrimas švietimo padengimas ... švietimas turi būti tolygus miksuojant taisyklių ir formos algoritmą" - `led_km.py coverage()`: po taisyklių išdėstymo - šviesos modelis veide, tamsios dėmės užpildomos papildomais moduliais, moduliai pastumiami tolygumui, perteklius šalinamas; `led_km.py spec.json out.pdf patikra.png` - švietimo patikros vaizdas. v127, Rytis 2026-10-12: LED - NAUJA VERSIJA pagal gamybos failus: Kaisen Electric kainoraštis + ryškumo (Depth) lentelės `assets/kaisen_led.json`; `led_km.py` modulis pagal gylį (KM-P0 / P1 / P2 0,72W / P2 1W / P3 / P4, raudoni KM-P*-R, plonos linijos MINI3), žingsnis - didžiausias su >= 2200 lx, PSU Kaisen KPS IP67 <= 75 %; BaltLED / Lens - nenumatyti. v126, Rytis 2026-10-12: „kodėl čia taip keistai nepridėti LED?" (A kojos, 7 kampas tušti) - `led_km.py` grandinė: galinis modulis p/2 nuo krašto NEŠALINAMAS dėl sankirtos, aštrus lenkimas (>= 45°) - mazgas su moduliu, šaka galas -> mazgas dalijama lygiai; plonos linijos - žingsnis <= 1,6 x linijos plotis; laidas - artimiausias kaimynas + 2-opt. v125, Rytis 2026-10-12: „P120 klaida. naudojami LED moduliai ir transformatoriai iš https://baltled.com" - `led_km.py` moduliai ir PSU iš `assets/baltled_led.json` (BaltLED katalogas): raidėms < 30 MINI HE, 30-49 PRISMA S1+, 50-100 PRISMA S2+ (= KM-P2 0,72W), 101-125 S3+, > 125 S4+; PSU BaltLED BPS (IP67, 12V, apkrova <= 75 %); Lens lentelė (`led_lens.json`, P65L / P130L / P190L / P120 ...) - NE mūsų tiekėjas. v124, Rytis 2026-10-12 patvirtino DĖLIOJIMO PRINCIPĄ (plevele_test 1190): grafika netelpa į rulono plotį -> skaidoma į VISUS bendrus objektus (užrašo eilutė, automobilis, kiekvienas dušas; riba - ryškus tarpas >= 3 x tarpų mediana) ir jie sudėliojami kompaktiškai (pvz. dušai pasukti šalia užrašo); telpa - visa, neskaidant; `plevele.logical_objects`. v123, Rytis 2026-10-12, plėvelės testas OKQ8 „Alltid öppet“: `plevele.py` - visa grafika viename compound path skaidoma į salas (skylės - even-odd), objektas kito viduje (rato centras) - kartu, diakritikai tik prie teksto eilučių; testas `scripts/projektai/plevele_test/`. v122, Rytis 2026-10-12: PLĖVELĖ - UŽRAŠAS VIENOJE LINIJOJE NESKAIDOMAS (nei į žodžius, nei į raides) vien taupant plėvelę: gamybininkui klijuoti kelias dalis į vieną liniją, matuoti tarpus - brangiau už plėvelę ir klaidų rizika; `plevele.text_lines`. v121, Rytis 2026-10-12: PLĖVELĖ SKAIČIUOJAMA PAGAL SUNAUDOJIMĄ (rulono darbinis plotis x ilgis), ne pagal grafikos plotą; spalvota 1190 mm (standartas), balta / spauda 1320 mm, 1500 mm - tik išimtis su pastaba; pjaustymo failas - forma skaidoma kuo mažiau: telpa - visa, netelpa - tik bendrais objektais; `scripts/plevele.py`, skyrius „Plėvelė - sunaudojimas ir pjaustymo failas“. v120, Rytis 2026-10-12: `led_km.py` moduliai - IŠ MŪSŲ LED LENTELĖS (`assets/led_lens.json`: 12V P65L / P130L / P190L, 24V P120 / P170L / P320L), raidėms numatyta P120 0,72W 24V (gylis < 50 - P65L); lape LED IMITACIJA - modulio korpusas su LED pagal ašies kryptį + grandinės laidas + apskritimas. v119, Rytis 2026-10-12: „led dėliojimas vis dar blogas“ - NUMATYTAS LED įrankis `scripts/led_km.py` (Kaizen KM-P2 HE 0,72 W / KM-P2-R, viena eilė per ašį, žingsnis pagal gylį 50->100, 70->120, 80->130, 100->140, apskritimas = žingsnis, galai p/2 nuo krašto, PSU KPS <= 75 %); Lens `led_sim.py` - tik paprašius; pavyzdžiai `assets/led_pavyzdziai/*_v2.jpg`, `*_RYCIO.jpg`. v118, Rytis 2026-10-12: PLOKŠTĖS PUSĖ DXF - pažymėti X tvirtinimo rėmai (H1800 60x60) -> vaizdas IŠ PRIEKIO (`--plate-front`); rėmo žymėjimo nėra (vienas rėmas FAS700 / FAS1000) -> plokštė veidrodiškai (iš galo) + **C žyma** galinėje pusėje (sluoksnis `5_C_ZYMA`), kad būtų aišku, kur priekis, kur galas. v117, Rytis 2026-10-12: EXTRA H1800 gamybos principas - X ant Ø1800 apskritimo su SAVO 60x60x2 X formos rėmu (įstrižainės per X šakų ašis), 8 x Ø3.2 ant profilio ašies + Ø11; EXTRA / 7-23 atskirai ant U30; `references/klientai/extra.md`, etalonas `assets/etalonai/extra_H1800_ALT8852_gamyba.pdf`. v116, Rytis 2026-10-12: P1 - inside kontūras (dugnas) 0,7 mm, be drenažo skylių ir be D11, nes LED nesideda (`p6_dxf.py --p1`; 1:1 PDF `back_inset_mm` P1 numatyta 0,7). v115, Rytis 2026-10-12: VIENAS RĖMAS - X (raidė ant plokštės) tvirtinimas kaip raidžių: Ø4 skylės ant bėgelio profilio HORIZONTALIOS AŠIES (`holes_on_rail`), D11 - apatinio bėgelio ašyje; plokštėje tos pačios skylės veidrodiškai; etalonas `assets/etalonai/extra_X_tvirtinimas_rems_asis.pdf`. v114, Rytis 2026-10-12: MEDŽIAGŲ BIBLIOTEKA - LT tiekėjų sandėliniai Alu profiliai (Heliopolis visas katalogas, Lankava Alytus, Proplastik Kaunas), Alu lakštai ir AKP formatai / RAL (Heliopolis, Proplastik, Plastena) `assets/medziagos.json` -> `profiliu_katalogas`; `medziagos.profile_check` / `sheet_check`, CLI `python3 scripts/medziagos.py profilis "U 30x30x2"`; rėmo / L / Z profiliai tikrinami automatiškai - nėra sandėlyje -> perspėjimas su artimiausiais, lape nerašyti be patvirtinimo. v113, Rytis 2026-10-12: DXF kontūrai - TIESĖS + LANKAI (LWPOLYLINE bulge, `--fit-tol 0.02`), ne tūkstančiai taškų - Corel be „Reduce nodes" (VH400: 8097 -> ~400 mazgų, nuokrypis <= 0,03 mm). v112, Rytis 2026-10-12: EXTRA DXF su PLOKŠTE - `p6_dxf.py --plate-fill` + kelių spalvų `--fill`: X atskirai kairiau apskritimo, apskritimas `4_PLOKSTE` su tomis pačiomis skylėmis veidrodiškai; etalonas `assets/etalonai/extra_darbiniai_DXF_pateikimas.pdf`. v111, Rytis 2026-10-12: LAPE PAŽYMĖTA, KOKIE LED KUR DEDASI - galiniame vaizde spec grupės `"led"`; etalonas `assets/etalonai/led_zymejimas_galiniame_EXTRA_223315.pdf`. v110, Rytis 2026-10-12: šaltinis - GitHub repo `rytiunia/ai_asistentas` vietoj iCloud zip. v109, EXTRA 225978 patvirtinimas: `braizyti_begeliai.py` - `rail_fills` spalvos blokai (statmens / kojos plotas) niekada ne raidės; spec `"client_vert_rails": false` - patvirtinto lapo statmenys nedubliuojami su spec `verticals`. v108, Rytis 2026-10-12: P6 DUGNAS - smailus raidės vidinis kampas (M viršus tarp kojelės ir įstrižainės) -> siaura įpjova nukertama: vietoj 1 taško 2, buki kampai (`K.dugnas_inset`, `--blunt-len 12`). v107, Rytis 2026-10-11: šviečiančių pilonų etalonas Prisma Skejby ALT8826 - `references/etalonas_pilonas_prisma_alt8826.md` (plieno / Alu rėmas, šviesdėžės „žvynais“, plexi įdėklai, padai, kėlimo ąsos). v106, Rytis 2026-10-11: KLIENTO RĖMAS NETVARKINGAS (ne per tvirtinimo ploto centrą, per trumpas, trūksta / per daug bėgelių, ne pagal standartą) - PERDAROMAS PAGAL SKILL (auto rėmas), nebent nurodyta naudoti kliento struktūrą - spec `"client_frame": true`. v105, Rytis 2026-10-11: patvirtinimo pakete siųsti TIK PDF su maketu, PDF su LED ir vientisus DXF (be failų po raidę); `reklama.zip` vartotojui nesiųsti (nuo 2026-10-12 - tik commit į GitHub). v104, Rytis 2026-10-11: „Patvirtinta, ALT…“ -> gamybos paketas: lapas su ALT numeriu + DXF 1:1 + LED lapas - `references/patvirtinimas.md`; `led_sim.py` `page` ir `feed_at: letter:N-top`; `p6_dxf.py` praleidžia < 20 mm kontūrus. v103, Rytis 2026-10-11: SUTARTINIS UŽRAŠAS - rėmo apraše „+ hangers“ (pvz. „frame 30x30x2mm + hangers RAL 7024“) = U laikikliai, „+ ears“ = ausėlės; skriptas `mounting` ima iš rėmo aprašo, jei spec jo nenurodo. v102, Rytis 2026-10-11: „rėmas su hangers“ = U laikikliai (`"mounting": "brackets"`); lape angliškai HANGER (BOM „Hanger U ...“, MAIN DATA „+ hangers“, 2 lapas „Hangers (U)“), ausėlės lieka „ears“; bėgelio eilutė BOM lieka. v101, Rytis 2026-10-11: P6 DXF `3_REMAS` - rėmas KARTU su ausėlėmis (kontūras + Ø6 skylė) ir U laikikliais (su skylėmis), įstrižai bėgeliai - tikru poligonu. v100, Rytis 2026-10-11: MAIN DATA be „Wall" (tik kai fasadas ne įprastas) ir be „Drainage"; BOM „Letter back" spalva = šonų spalva (kitokia - tik nurodžius, `back_ral`). v99: drenažo Ø8 skylutė VISA dugno viduje; rėmo matmenys apvalūs - 5 mm žingsniu (3017 -> 3020, 17 -> 15). v98: 6 m strypai visam užsakymui (qty); exterior DXF su Ø8 drenažu. v90-v97 (P6 priekiai, montavimas: ausėlės / U laikikliai / atskiros raidės, statmenys per raidžių centrą + įstrižas ant A, > 6 m bėgelis trumpinamas, viena ausėlė rėmo gale, POWER) ir ankstesnės - `references/versijos.md`.)

**!!! VIENAS ŠALTINIS - GitHub repo `rytiunia/ai_asistentas`, aplankas `reklama/` (nuo 2026-10-12; iCloud zip'ai archyvuoti) !!!**
1. Pilnas skill'as (SKILL.md + `scripts/`, `assets/`, `references/`) - https://github.com/rytiunia/ai_asistentas , `reklama/`.
   Paskyroje (Claude) - tik paleidiklis (`references/paleidiklis_SKILL.md`); paskyroje likę seni failai - NENAUDOTI.
2. Prieš darbą: `add_repo` (rytiunia/ai_asistentas) -> `git clone --depth 1` (ar `git pull --ff-only`) -> dirbti TIK iš klono.
3. Repo nepasiekiamas - PRIEŠ darbą pasakyti Ryčiui (prijungti GitHub arba įkelti aplanką zip'u į pokalbį).
4. Atsakyme VISADA nurodyti versiją ir commit'ą (pvz. „reklama vNN, GitHub abc1234").
5. Pakeitus skill'ą: pakelti „Versija", `git pull --rebase`, commit (žinutė „reklama vNN: ...") ir `git push` į `main`.
   Zip'ų ir `_archyvas` nebereikia. Failų vardai - tik ASCII.

**!!! PRADŽIA - GALIOJANČIOS TAISYKLĖS (v293, Rytis 2026-10-16: „išsaugok taisykles ir naudojimo logiką ir padaryk, kad kitą
kartą vėl nebūtų daroma su senomis taisyklėmis ir nustatymais") !!!**
6. PRIEŠ bet kokį lapą perskaityti **`references/lapo_taisykles.md`** - VIENA galiojančių lapo taisyklių suvestinė + darbo eiga
   (išdėstymas, matmenys, lentelės, blokai, ką tikrina automatika). Žemiau esančios numeruotos taisyklės - istorija su
   priežastimis; prieštaravime galioja naujesnė, o suvestinė atnaujinama tame pačiame commit'e.
7. Seno projekto skriptas (`scripts/projektai/...`) - TIK duomenų analogas: koordinatės, masteliai, užrašai nekopijuojami;
   braižoma tik per `lapas_core` / `layout_engine` funkcijas. `patikra_lapas.py` tai užtikrina: 14 SENA TAISYKLĖ
   (`taisykliu_lint.py` lapo generatoriui), 13 BLOKAS NECENTRUOJAMAS, 15 SUVESTINĖ PASENUSI.
8. Ryčio pataisa -> tame pačiame commit'e: SKILL įrašas + suvestinė + kodas + patikros / lint punktas + pergeneruoti atviri
   lapai; versija - `python3 scripts/versija.py "aprašas"` (SKILL ir suvestinė kartu).

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
   **KIWI (v178, Rytis 2026-10-13): VISI KIWI dokumentai - pagal ETALONĄ KIWI order 226023** (iki atskiro nurodymo):
   PRIVALOMA `references/etalonas_kiwi_226023.md`, lapai `assets/etalonai/KIWI_226023_komplektas_3_lapai.pdf`,
   kodas `scripts/projektai/kiwi_226023/`.
**PRODUKTŲ KATALOGAS - TIKSLŪS RAKTAŽODŽIAI (v266, Rytis 2026-10-15): `references/produktu_katalogas.md`** - A: paruošti produktai
(>= 90 % be patikslinimų: raktažodis -> generatorius, šablonas, etalonas, būtina įvestis), B: reikia patikslinimų (klausti prieš
braižant), C: SENI / klaidingi pavadinimai - NENAUDOTI (versti į naujus). Užklausos raktažodį pirmiausia sutapatinti su katalogu
(`ziniu_paieska.py` rodo jį pirmą); jei raktažodis katalogo C dalyje - naudoti naują pavadinimą ir tai pasakyti Ryčiui.
Naujas produktas pereina į A tik Ryčiui patvirtinus etaloną.
0. **GERIAUSIAS SPRENDIMAS IŠ JAU DARYTŲ REZULTATŲ + TEISINGOS ŽINIOS (v264, Rytis 2026-10-15 - PRIVALOMA PRIEŠ KIEKVIENĄ
   UŽSAKYMĄ / POZICIJĄ):** `python3 scripts/ziniu_paieska.py <produktas> <raktažodžiai>` (pvz. `dvipuse sviesdeze kojos`,
   `P10 raides be begio`). Skriptas parodo: produkto ŠEIMĄ ir VISUS jos generatorius / aprašus (perskaityti visus - taisyklė,
   priimta viename šeimos modulyje, galioja visai šeimai, taisyklė 26), atitinkančias SKILL / references taisykles surikiuotas
   pagal NAUJUMĄ (vNNN), jau darytus projektus ir patvirtintus etalonus, žinomas klaidas. Toliau:
   a) pagrindu imti GERIAUSIĄ analogą - patvirtintą etaloną arba naujausią to paties tipo projektą (ne seną generatoriaus
      numatytąjį variantą, ne „nuo nulio");
   b) taisyklėms prieštaraujant - galioja NAUJESNĖ (didesnė vNNN) ir konkretesnė (kliento > produkto > bendra);
   c) jei pasirinktas generatorius neturi naujesnių šeimos taisyklių - PIRMIAUSIA pataisyti generatorių, tik tada braižyti;
   d) rezultatą palyginti su analogu / etalonu (`patikra_lapas.py` = 0 + akimis) - naujas lapas negali būti prastesnis už
      jau Ryčio patvirtintą; skirtumus įvardyti atsakyme;
   e) Ryčio pataisa = nauja taisyklė: įrašyti į SKILL (bendra, ne vieno projekto), `references/klaidos.md` (jei klaida) ir
      pritaikyti VISIEMS tos šeimos generatoriams (regresija - visi šeimos testai `patikra_lapas.py` = 0).
4. **Bendrinės taisyklės + kliento raktažodis** (žr. žemiau). Produkto tipo taisyklės galioja visiems klientams;
   kliento taisyklės - tik kai užklausoje yra to kliento raktažodis.

## Bendrinės taisyklės ir klientų raktažodžiai (v43)

**Bendrinės (visiems tokio tipo užsakymams, nepriklausomai nuo kliento)** - šiame faile, „Produktų moduliai":
| Produkto tipas / raktažodis užklausoje | Skyrius |
|---|---|
| folded pl. / folded plate / lankstyta plokštė / back plate | „Folded plate - bendrinės taisyklės" (išklotinė `folded_dxf.py`: numatyta SIDES INSIDE, „top/bottom inside" - tik nurodžius `--tb-inside`) |
| folded + raidės (P6, P8 ...) | „Folded plate" + „P6 raidės ant folded plokštės" / „Kito profilio raidės ant folded" |
| folded + oracal / plėvelė / vinilas / grafika | „Folded plate + pjaustyta plėvelė" |
| plėvelė / vinilas / oracal / avery / 3M / lipdukas / spauda - kiekis, m², ploteris, pjaustymo failas | „Plėvelė - sunaudojimas ir pjaustymo failas" (PRIVALOMA BOM) |
| plėvelės spalva / kodas (oracal 8500 / 551, avery, 3M 3630) | „Plėvelių spalvų biblioteka" |
| 5S (buv. P6_3mm) / P6 (buv. P6_8mm) / color / +foil | „P6 priekio variantai" (+ modulis pagal foną) |
| P6 dxf / CNC failai raidėms / tvirtinimo skylės / D3.2 / D11 / gręžimas | „P6 DXF - stiklas, dugnas, rėmas, tvirtinimo ir laido skylės" |
| P6 ant bėgelių / rails / U / wallframe, P6+3 ant plokštės | „P6 raidės ant U bėgelių ..." + „Bėgeliai ir ausėlės" |
| be ausėlių / U laikikliai / laikiklis / atskiros raidės / be rėmo / WAGO / 12V 1,5 m | `references/moduliai_montavimas.md` (PRIVALOMA) |
| one frame / vientisas rėmas / bėgis per apskritimą | „Bėgeliai ir ausėlės" -> „VIENTISAS RĖMAS" |
| □ profilis / square | „P6 ant stačiakampio Alu profilio" |
| P1 / nešviečiančios | „P1 nešviečiančios raidės ant bėgelių" |
| stogas / roof / kojos | „Stogo iškaba - atramos" |
| pylonas / pilonas / totem / stovas / piloniukas / pagrindo plokštė / flanšas | `references/moduliai_pilonai.md` (PRIVALOMA) |
| P10_lightbox_doublesided (buv. P10_lightbox, v227) / push-through / iškištas stiklas / dvipusė šviesdėžė Alu korpusu su išpjova (v197; NE P10 raidės) | `references/moduliai_p10_lightbox_doublesided.md` (PRIVALOMA; generatorius `scripts/p10_lightbox_doublesided.py`, etalonas `assets/etalonai/P10_lightbox_dvipuse_600x600x80_kliento.pdf`) |
| P10 raidės / Profile 10 / 30 mm plexi raidės ant akrilinių bėgelių | `references/moduliai_p10_raides.md` (PRIVALOMA; etalonas `assets/etalonai/P10_Boots_ALT6739_akriliniai_begeliai.pdf`; griovelis `scripts/griovelis_b.py` + `griovelis_sim.py`) |
| P10_lightbox_singlesided / vienpusė P10 šviesdėžė (priekis P10, dugnas folded plate 30) (v227) | `references/moduliai_p10_lightbox_singlesided.md` (PRIVALOMA; generatorius `scripts/p10_lightbox_singlesided.py` (v230), eskizas `assets/konstrukcijos/P10_lightbox_singlesided_eskizas.png`) |
| PVC banner / tentinė šviesdėžė / tentas / flexface / banner lightbox (v161) | `references/moduliai_pvc_banner.md` (STANDARTAS, gylis 200 mm, PRIVALOMA) |
| termoformavimas / thermoformed / vakuumformet / forma termoformavimui (v161) | `references/moduliai_termoformavimas.md` |
| flag sign / pendant / nasekylt / dvipusė kabanti / drapeau / potence (v161) | `references/moduliai_pendant.md` |
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
| OKQ8, Q8, Skyltkoncept, Väster, height restriction, ALT8877 | `references/klientai/okq8_skyltkoncept.md` + `references/klientai/skyltkoncept.md` | `scripts/projektai/okq8_vaster/`, `okq8_alt8877/` |
| Joker (BrandFactory), Joker order 226001 | tik bendrinės | `scripts/projektai/joker_reinslettveien/` |
| Prisma Properties Skejby, ALT8826, Order 2439 (šviečiantys pilonai 8,8 m / 5 m) | `references/etalonas_pilonas_prisma_alt8826.md` + `references/klientai/bn_skilte.md` | - |
| CEOS Groupe, Thales, D059422 (pilonai, PMMA planas) | `references/klientai/prancuzai.md` + `references/moduliai_pilonai.md` | `scripts/projektai/thales_d059422/` |
| POWER, Imagon, Brotorvet | tik bendrinės | `scripts/projektai/power_brotorvet_3a/` |
| KIWI (visi: raidės, 7-23, Lanterne) - ETALONAS v178 | `references/etalonas_kiwi_226023.md` + `references/klientai/brandfactory.md` | `scripts/projektai/kiwi_226023/` |
| COOP, MATKROKEN, Alytus ir kt. (be atskiro failo) | `references/klientai/brandfactory.md` + `assets/spec_*.json` pavyzdžiai | `scripts/projektai/kiwi_226023/` |
| Volvo, Alfa Neon / AlfaNeon, VOLV24- / VOLV25-, BS module, Top sign, Mounting kit 5,5 / 7,5 / 9,3, Bilia, Bilmånsson, Helmia (v161) | `references/klientai/alfaneon_volvo.md` (STANDARTAS - `AlfaNeon/VOLVO/VOLVO_darbiniai failai`) | - |
| OMODA, JAECOO, EXLANTIX, OMJE26- / EXLA26-, RSA HK Drammen, PO 33580 (Alfa Neon) (v237) | `references/klientai/alfaneon_rsa_drammen.md` (+ `alfaneon_volvo.md` 2 sk.) | `scripts/projektai/omoda_33580/` |
| Leapmotor, Leap Motors, LEAP26-, PO 33577 (Alfa Neon) (v228) | `references/klientai/alfaneon_leapmotor.md` (+ `alfaneon_volvo.md` 2 sk. bendri Alfa Neon) | - |
| DSV, DSVL25-, 3D Logo DSV indirect, Frontlit, DSV Flexible size (v161) | `references/klientai/alfaneon_dsv.md` | - |
| BN Skilte, bn-skilte.dk, Indkøbsordre, Normal / Unik mand, Netto, Wash World, M3 / K3, Subway, SJF Bank (v161) | `references/klientai/bn_skilte.md` | - |
| ChopChop, Burger King / BK, TANKA, Rental Village (Skyltkoncept) (v161) | `references/klientai/skyltkoncept.md` | - |
| MENY, KIWI, JOKER, KFC, Boots, Norli, ALTI, OBS BYGG, ICA, Konsulent / Tiltak / Tegning (BrandFactory) (v161) | `references/klientai/brandfactory.md` (+ SPAR / EXTRA / Clas Ohlson failai) | - |
| Prancūzai, France, SGIV, IDP, Espace enseigne, Kapella, Demande de prix, Commande, BAT, support de drapeau (v161) | `references/klientai/prancuzai.md` | - |
Naujas klientas su savo standartu -> naujas `references/klientai/<klientas>.md` + eilutė šioje lentelėje. Bendrinę
taisyklę, kurią Rytis pasako dirbant su konkrečiu klientu, rašyti į BENDRINĮ skyrių (jei ji apie produkto tipą), o
į kliento failą - tik tai, kas būdinga klientui (spalvos, standartinės konstrukcijos, laido vieta, užsakovo duomenys).

## Originalo perdarymas į mūsų stilių (v160, Rytis 2026-10-13 - PRIVALOMA)
Kai perdaromas esamas dokumentas (ankstesnis ALT lapas, kliento ar Ryčio brėžinys): VISA informacija, matmenys, rėmas,
ausėlių vietos, lentelės (stulpeliai ir eilutės), LED aprašai, užrašai ir paaiškinimai perkeliami iš ORIGINALO kuo mažiau
iškraipant - keičiamas TIK lapo stilius (rėmelis, šriftas, vaizdų išdėstymas, juosta). Nepridėti savų eilučių, ALT pasiūlymų,
klausimų lape ar „patobulinimų“ (skill taisyklės rėmui / ausėlėms netaikomos - originalo rėmas `rails` + `fit_plates` su `len`).
Lentelė - originalo pavadinimu ir stulpeliais (`bom_cols`, `bom_title`), pjūvio balionai - originalo pozicijomis (`section_labels`).
LED dėliojimas su kiekiais ir įtampa - VISADA perkeliamas (originalo fragmentas `K.place_pdf`, atskiras LED INSTALLATION lapas);
originalo detalės / 3D / sprogdintas vaizdas - originalo fragmentu, ne savo perpieštos detalės (v161).
LAIDO IŠVESTYS (v170): tik originalo vietose (`cable_exits[].point`), vienas variantas visame lape (galinis vaizdas = LED brėžinys).
GOST VISUR (v168): ir įdėtuose originalo fragmentuose - Arial užrašai keičiami GOST (`gost_frag.py`); objektai centruojami savo plote, simetriškai, lapas užpildomas tolygiai.
Raidžių lapo išdėstymas (v162): kairė viršus FRONT (+ SIDE), dešinė viršus REAR, kairė apačia LED INSTALLATION, dešinė apačia 3D.
Aprašai ir spalvos iš originalo fragmento perkeliami į lentelę (Parts List: Description, FINISH = RAL pagal detalę), fragmente jų nelieka.

## Bendrinės taisyklės v183-v191 (Rytis 2026-10-13, testai „Welcome" P1, „Alytus," P6) - VISOMS POZICIJOMS pagal situaciją
Galioja visiems produktams ir klientams, kur situacija tinka (ne tik P1 / ne tik šiam testui):
1. **Ryčio nurodytas rėmas > skill auto taisyklės.** Kai Rytis nurodo rėmo struktūrą (pvz. „rėmas per visą užrašą, statmenys
   po pirma e ir m vidurine kojele") - rėmas daromas TIK pagal nurodymą (spec `groups[].rails`), auto rėmo taisyklės
   (galiniai statmenys, kiekis pagal ilgį ir pan.) netaikomos. Savo naujų rėmo taisyklių nesugalvoti - jei abejoji, klausk.
2. **Kraštinė raidė turi tvirtintis STABILIAI.** Raidė be stiebo kraštinėje vietoje (e, c, o, s ...) - bėgeliai tęsiami
   iki raidės galo (pvz. „e" uodegytės galo, ~10 mm nuo krašto), net jei rėmas dalinai matysis. Stabilumas > paslėpimas.
   Kodas: `auto_remas.py` (v185), rankiniam rėmui - tas pats principas spec'e. Kraštinė raidė nustatoma tik iš pilno aukščio
   raidžių (kablelis / taškas - ne kraštinė raidė). **v192: smulkus elementas už rėmo galo (kablelis, taškas) - TIK artimiausias
   jam bėgelis (kablelis - apatinis) tęsiamas iki elemento, nuo jo - LAIKIKLIS (statmuo) per elementą (žemyn / aukštyn, abu kampai
   >= 10 mm elemento viduje)** („tvirtinimas ant dviejų taškų neduos stabilumo"); viršutinis bėgelis NEpratęsiamas, rėmo galas ir
   galinis statmuo - kaip buvo; elementas visai po / virš eilutės - akcento laikiklis (v77). (v189, v191 variantai atšaukti.)
   **v193 (Ryčio eskizas): T forma** - bėgelis per VISĄ elemento plotį (iki išorinio krašto - 10 mm), laikiklis per elemento
   VIDURĮ (ne kur ilgiausias), ant pratęsto bėgelio - AUSĖLĖ prie laikiklio (laisvoje vietoje tarp laikiklio ir rėmo galo).
3. **Dugno spalva.** P1 dugnas PVC 10 mm - NEDAŽYTAS: BOM FINISH „-", REAR VIEW dugnas šviesiai pilkas (nedažytas plastikas),
   ne korpuso RAL. Dažytas dugnas - tik kai nurodyta (`back_ral`). Bet kuris nedažomas dugnas / nugara vaizduojama
   medžiagos spalva, ne korpuso (v184, v186).
4. **HANGERS (U laikikliai), `"mounting": "brackets"` / „+ hangers":**
   - kiekis pagal rėmo ilgį: iki 2,5 m - 2, iki 4 m - 3, iki 7 m - 4, toliau ribų prieaugis +1,5 m (11,5 m - 5, 17,5 m - 6 ...);
   - pozicijos - ta pati formulė kaip laikiklio tvirtinimo skylių: žingsnis p = L / n, nuo rėmo galų p / 2 (2 vnt. - L/4, 3L/4);
   - galiniame vaizde - TIK punktyru (kontūras ir skylės, be užpildo);
   - VISADA matomi profilio pjūvyje (P1 ir P6): plokštumos virš / po bėgeliais, sienelė prie fasado, Ø6 ašinės, balionas;
   - `assets/tvirtinimas.json`, `references/moduliai_montavimas.md`.
5. **Profilio pjūvis VISADA centruojamas savo bloke** (bloko centre, horizontaliai ir vertikaliai) - visi pjūviai / DETAIL.
6. **Balionų numeriai = galutinės BOM pozicijos** (po pernumeravimo), ne fiksuoti skaičiai.
7. **Nežinoma reikšmė (RAL, kiekis) - tuščias langelis**, ne „RAL ? matt" ar pusiau užpildytas tekstas.
8. **Auto rėmas:** bėgelio kraštas >= 11 mm nuo raidžių viršaus / apačios (v49 ir auto rėmui; antikvos serifai); galų vietos
   nerasta - perspėjimas, rėmas neapverčiamas.
9. **HAIRLINE projekcijose - ir DVIGUBOS LINIJOS (v190):** du hairline kontūrai arčiau nei 0,6 pt (pvz. P6 stiklo kraštas 1,5 mm
   1:15 mastelyje, korpuso priekis po stiklu 3D) spaudoje susilieja į storą liniją - smulkiame mastelyje vidinis kontūras
   be linijos (tik užpildas), 3D korpuso priekis po stiklu - be kontūro. `patikra_lapas.py` tikrina „DVIGUBA LINIJA".
10. **Plėvelės spalvos blokas BOM (v190):** FINISH langelis VISADA nuspalvinamas plėvelės spalva - kodas imamas iš FINISH arba
   iš tos pačios eilutės PART / MATERIAL („Front foil ORACAL 8500 021 Yellow" -> #FFCF00), ne baltas.
11. **Ausėlės pagal apkrovą prie rėmo galų (v190):** bėgelis, pratęstas už rėmo kampo (iki kablelio / taško, <= end_max) -
   KONSOLĖ: jo kraštinė ausėlė ieškoma prie RĖMO KAMPO (galinio statmens, kur susitinka bėgeliai), konsolės apkrova
   tikrinama iki tikro bėgelio galo; galas be ausėlės bėgelyje - ausėlė ant galinio statmens. Konsolėje - kiekvienos
   ausėlės apkrova kN (`ausėlių apkrovos kN`), max <= inkaro (`assets/tvirtinimas.json`).
12. **RĖMO SURINKIMAS (v191, Rytis 2026-10-13 - pakeičia v78-v79 „galiniai statmenys prie bėgelių galų"):** rėmas NIEKADA
   nedaromas taip, kad pirmas ir paskutinis statmuo dedasi prie bėgelių galų. Bėgeliai eina per VISĄ rėmo ilgį, VISI statmenys
   (ir galiniai) įvirinami TARP viršutinio ir apatinio bėgelio, niekada iš galų. Kelios eilutės - statmuo pjaunamas tarp
   kiekvienos bėgelių poros. (`auto_remas.py`; rankiniam rėmui - tas pats spec'e.)
   **v204 (Rytis 2026-10-14, „LIETUVA": „rėmas neina per visą ilgį, o uždaromas statmenu"):** rėmas NEUŽDAROMAS galiniais
   statmenimis bėgelių galuose. Kiekvienas bėgelis eina per VISĄ ilgį iki kraštinės raidės krašto atskirai (abu kampai >= 10 mm
   raidės viduje - viršutinis gali baigtis „A" viršūnėje, apatinis - prie dešinės kojos; bėgelių ilgiai gali skirtis).
   GALINIAI statmenys - TIK kur jie panaudojami: per kraštinei artimiausios raidės STIEBĄ (L, T, E ...); raidės be stiebo
   (V, A) - ĮSTRIŽAS per kojelės vidurį kaip EXTRA (v95), galai remiasi į bėgelius. Tarpiniai - per stiebus tolygiai,
   kiekis ceil(L / 2500) + 1. Kodas `auto_remas.single_verticals` (vienos eilutės rėmas; kelių eilučių - kol kas v79-v82).
13. **STATMENŲ ILGIS NEŽYMIMAS (v191):** galiniame vaizde statmenų („355 vert.") žymų NĖRA - užtenka rėmo aukščio matmens
   (viršus - apačia). Išimtis - originalo perdarymas, kai originale jos yra (spec `"vert_labels": true`, KIWI 226023).
14. **KRAŠTINĖS AUSĖLĖS - PORA TARP RAIDŽIŲ (v191):** rėmo gale viršutinė ir apatinė ausėlė - viena linija, TARPE tarp paskutinių
   pilno aukščio raidžių (pvz. tarp „u" ir „s"), NE raidės gabarite (po „s" snapeliu), NE ant kablelio / taško; rėmo galas už
   poros - konsolė, tikrinama apkrova (`auseles.place_frame`, `end_zone`, `letter_boxes`). Poros vietos nėra - kaip anksčiau.
16. **P6 DXF TVIRTINIMO SKYLĖS - TOLYGIAI (v195, Rytis: „mažesniame plote pridėta daugiau nei didesniame"):** kiekvienoje bėgelio
   zonoje raidėje skylės n = ceil(L / 2R) (R = 100), žingsnis L / n, nuo zonos galų L / 2n - skylių kiekis proporcingas raidės
   ruožui ant bėgelio; kojelės traukimas (a / d / m) - tik `--stems`; papildoma skylė neprispaustai daliai - tik jei ji >= R / 2
   ilgio išilgai bėgelio (ne kampų likučiai).
15. **PLĖVELĖ ANT ATSKIRŲ RAIDŽIŲ - NESTING (v191):** kai plėvelė klijuojama ant atskirų raidžių (P6 / tūrinių raidžių priekiai) -
   kiekviena raidė (ir kablelis / taškas) - atskiras objektas, sudėliojamas ant rulono kompaktiškai (`plevele.py --separate`,
   `plan(..., separate=True)`); taisyklė „užrašas vienoje linijoje - vienas objektas" galioja tik vientisam lipdukui (plokštė,
   stiklas, folded). Kartu su lapu VISADA pateikiamas plėvelės nesting PDF + DXF (`--pdf`, `--dxf`), BOM - sunaudojimas iš jo.

17. **TRAFO BOX be PWM (v205, Rytis 2026-10-14):** PWM naudojamas ne visur - ant TRAFO BOX rašoma „TRAFO BOX / RAL ...";
   „PWM" - TIK kai nurodyta užsakyme („+ PWM", potenciometras; spec `trafo_box.pwm: true`). Dėžės balionas = BOM eilutė,
   kuri PRASIDEDA „Trafo box" (ne laido eilutė „... -> trafo box"). `references/moduliai_kiti.md` TRAFO BOX.

18. **VISI LANKSTINIAI (folded plates, pilonų / šviesdėžių lovelės, padėklai) - TIK pagal folded taisyklę v173 (v207, Rytis
   2026-10-14, Thales: „kodėl folded plates lankstiniai ne pagal taisykles?"):** lenkimo linijos = išoriniai matmenys, atlankas nuo
   lenkimo linijos = gylis - t, šonai įsilenkia (t trumpesni ten, kur susitinka su viršaus / apačios atlanku), K faktoriaus / BA
   NĖRA (senas K 0.44 / R2 / BD 3.476 - NEBENAUDOTI ir senuose projektų skriptuose - perrašyti paleidžiant). **Tvirtinimo skylės
   atlankuose - Ø3.2, ašis 7 mm nuo atlanko krašto, NEPRIKLAUSOMAI ar varžtas įleidžiamas (csk) ar ne.** `references/moduliai_folded.md`.

19. **KOJŲ UŽDENGIMAS (šviesdėžės, P10_lightbox_doublesided ir kt.; v212-v216, Rytis 2026-10-14):** 2 dalys A + B (veidrodinės), Alu 2 mm,
   korpuso spalva, lankstinys pagal 18. Ilgis = kojų tarpas (korpusas - plokštė) - 5 mm (po 2.5 iš abiejų galų); plotis = kojos
   profilis + 10 (□30 -> 40 = 20 + 20); viršuje 2 x Ø3.2 prisukimui (7 nuo krašto); priekyje ir gale - standumo briaunos 10 mm.
   **Briaunos remtųsi į kojas ir uždengimas neužsidėtų - TIES KOJOMIS briaunose IŠPJOVOS** (nuo laisvo krašto, gylis = kojos/2 +
   tarpas - (plotis/2 - briauna), ilgis = kojos profilis + 2 tarpai); atlankai remiasi į kojas -> aukštis = kojų matmuo + 2t.
   Lape kojos po uždengimu - punktyru; exploded view uždengimai rodomi ATITRAUKTI nuo rėmo (ne priglausti); išklotinė - gamybos DXF.
   **GALIOJA VISOSE SITUACIJOSE, KUR YRA KOJŲ UŽDENGIMAS** (v217, Rytis) - šviesdėžės (`sviesdeze.py` inset), P10_lightbox_doublesided B,
   kliento projektai (pvz. Skyltkoncept): visada bendras modulis `scripts/koju_uzdengimas.py` (`make` / `write_flat` / `bom_desc`),
   išklotinė - `<out>_gamyba.dxf`. Naujame generatoriuje uždengimo geometrijos NErašyti iš naujo - naudoti modulį.

20. **VISI ŠVIESDĖŽIŲ DOKUMENTAI - EXPLODED VIEW + POZICIJOS PJŪVYJE (v218, Rytis 2026-10-14):** kiekviename šviesdėžės lape
   (`sviesdeze.py`, `p10_lightbox_doublesided.py`, kliento projektai) - **ASSEMBLY - EXPLODED VIEW** (detalės išskleistos išilgai gylio,
   kojų uždengimas atitrauktas nuo rėmo, balionai = BOM) ir **DETAIL B pjūvis per VISĄ gylį su pozicijomis** (balionai = BOM):
   P10_lightbox_doublesided (yra stiklas / iškištas įdėklas) - 3 vietos VIRŠUS / STIKLAS / APAČIA; **5S tipo** šviesdėžės (stiklas su PVC
   borteliu, prisukamas per korpuso juostą) - 2 vietos VIRŠUS / APAČIA. Zonos atskiriamos nutraukimo linija.

21. **ŠVIESDĖŽIŲ DAŽYMAS (v220, Rytis 2026-10-14):** spalva (RAL pagal klientą) dažosi TIK KOJOS (ir padai / montavimo plokštės,
   kojų uždengimai - korpuso spalva) ir korpuso IŠORĖ; **rėmas korpuso viduje ir korpuso vidus dažosi BALTAI** - geresniam
   švietimui. BOM / MAIN DATA: rėmo nariai - „white", rėmas su pailgintomis kojomis - „RAL ... legs" + „in body white",
   korpusas / padėklai - „RAL ... out" / „inside white". Galioja `sviesdeze.py`, `p10_lightbox_doublesided.py` ir kliento šviesdėžėms.
   **EXPLODED VIEW TAI ATVAIZDUOJA (v222):** rėmas korpuso viduje (ir kojų dalis viduje) - baltas, kojos lauke / padai - spalva,
   korpuso juosta / padėklai - išorė spalva, vidus baltas (skarda per pusę storio: išorė + vidus); paaiškinime „inside white".

22. **ŠVIESDĖŽĖS RĖMO LAPAS (2 lapas) - KAIP CAD BRĖŽINYS (v220, Rytis 2026-10-14):** be spalvų, tik linijos (balti užpildai,
   juodi kontūrai, ir LED / laidai - linijomis); `sviesdeze.py` `_CAD` režimas `sheet2`. 1 lapas (GA, 3D) - spalvotas.
   **PROJEKCIJOS CENTRUOJAMOS SAVO BLOKUOSE (v222):** FRAME | VIEW FROM WALL - laisva lapo vieta dalijama po lygiai abiem blokams,
   kiekvienas vaizdas (su matmenimis) - bloko viduryje; vertikaliai - laisvo aukščio viduryje; BODY BAND - lapo viduryje.
   (v223: šviesdėžės dabar VIENAME lape - taisyklė 23; 22 galioja, jei rėmas kada nors brėžiamas atskirame lape.)

23. **VISŲ ŠVIESDĖŽIŲ DOKUMENTAS - VIENAS A3 LAPAS PAGAL `TEST_P10_lightbox_doublesided_B` (v223, Rytis 2026-10-14):** šablonas -
   `scripts/projektai/p10_lightbox_doublesided_test/TEST_P10_lightbox_doublesided_B.pdf`. 1 eilė: FRONT VIEW - SIDE A | VIEW FROM WALL | FRONT VIEW -
   SIDE B | SECTION A-A (v225: rėmo ir plokštės vaizdai - TIK 2 lape), apačioje dešinėje TOP VIEW; 2 eilė: 3D SIDE A | 3D SIDE B | ASSEMBLY - EXPLODED VIEW; juosta: DETAIL B
   (pjūvis per visą gylį su pozicijomis) | BOM | MAIN DATA (+ Finish) | antspaudas (faktiniai masteliai). Masteliai -
   automatiškai: priekio ir rėmo subalansuoti (priekiui pirmenybė). Išklotinės (korpuso juosta / padėklai, kojų uždengimas,
   plexi) - TIK gamybos DXF `<out>_gamyba.dxf`. Įgyvendinta `p10_lightbox_doublesided.py`, `sviesdeze.py` (abu variantai).

24. **VISŲ ŠVIESDĖŽIŲ DOKUMENTUOSE - 2 LAPAS: DETALUS CAD RĖMO BRĖŽINYS (v224, Rytis 2026-10-14; papildo 23):** 1 lapas -
   kaip `TEST_P10_lightbox_doublesided_B`, 2 lapas „... - FRAME (CAD)": be spalvų, tik linijos (taisyklė 22), projekcijos centruojamos
   blokuose. Projekcijos: **FRAME (1) - SIDE VIEW** (iš A pusės: narių ilgiai, kojos, LED, pjaustymo pozicijos 1.1 / 1.2 / 1.3 ...),
   **FRAME - END VIEW (FROM WALL)** (rėmo galai, galinis statmuo / dalys, kojos punktyru, montavimo plokštė / padai SU MATMENIMIS:
   plotis, aukštis, padėtis nuo rėmo; skylių matmenys - čia, arba jei DETAIL gali būti didesnio mastelio - **DETAIL PLATE /
   FLANGE 1A** dešinėje apačioje), **FRAME - ISOMETRIC** (r3d `flat` - balti paviršiai, juodi kontūrai, balionai = 2 lapo BOM).
   Juosta: LED duomenys | BOM (rėmo pjaustymo sąrašas, plokštės, LED, PSU) | MAIN DATA (rėmas) | antspaudas.
   `sviesdeze.py` / `p10_lightbox_doublesided.py` `sheet2`, `end_view`, `frame_iso`.
   **v225 (Rytis): 1 LAPE RĖMO IR PLATE / FLANGE VAIZDŲ NEDĖTI** - tam yra 2 lapas. 1 lapo 1 eilė - FRONT A | VIEW FROM WALL
   (gręžimo schema) | FRONT B | SECTION A-A per visą plotį (didžiausias telpantis mastelis, laisva vieta - į tarpus), 2 eilė -
   3D A | 3D B | EXPLODED | TOP VIEW. BOM 1 eilutė - „cut list - sheet 2".
   **v226 - PATVIRTINTA (Rytis 2026-10-14 „labai gerai"):** etalonai (generuoti, šablonas visiems šviesdėžių dokumentams) -
   `scripts/projektai/p10_lightbox_doublesided_test/TEST_P10_lightbox_doublesided_B.pdf` (+ `TEST_P10_lightbox_doublesided.pdf`),
   `scripts/projektai/sviesdeze_700x370_kojos/TEST_sviesdeze_700x370_kojos.pdf`, `scripts/projektai/sviesdeze_500_logo/TEST_sviesdeze_500_logo.pdf`
   (+ `_gamyba.dxf`). Tvarka: 1 lapas GA (taisyklės 20, 21, 23, v225), 2 lapas CAD rėmas (22, 24), kojų uždengimas (19).

26. **ŠVIESDĖŽIŲ TAISYKLĖS - BENDROS VISIEMS ŠVIESDĖŽIŲ GENERATORIAMS (v254, Rytis 2026-10-15: „kodėl naudojami seni skill,
   nors užklausai turėtų būti pritaikomi pagal situaciją?"):** prieš bet kurią šviesdėžę (`sviesdeze.py`, `p10_lightbox_doublesided.py`,
   `p10_lightbox_singlesided.py`, kliento projektai) PERSKAITYTI taisykles 19-24, 26 IR `references/moduliai_p10_lightbox_doublesided.md`,
   `moduliai_p10_lightbox_singlesided.md`, `moduliai_pendant.md` - taisyklė, priimta viename modulyje (kojos, išdėstymas, varžtai,
   dažymas), TAIKOMA VISIEMS; senesnis generatorius pirmiausia pataisomas pagal naujausias taisykles, tik tada braižoma.
   * **Kojos per galinį statmenį** (P10_lightbox_doublesided B v211 = `sviesdeze.py` `"leg_in": 0`): kojos (kaip rėmas, pvz. □30x30x2)
     prasideda galinio statmens vidinėje briaunoje po skersiniais ir eina iki plokštės; galinis statmuo 1.4 įvirintas TARP kojų
     (ilgis = tarp kojų); lape - suvirinimo žymos ir užrašas, BOM 1.4 / 1B ilgiai.
   * **Išdėstymas: EXPLODED VIEW svarbesnis už TOP VIEW** (P10_lightbox_singlesided v232): 2 eilėje TOP VIEW - tiesiai po FRONT VIEW A
     (ta pati x skalė), po juo 3D A / 3D B, visa likusi dešinė - EXPLODED VIEW (didžiausias). (Keičia 23 / v225 2 eilės tvarką.)
   * **Stiklas (SIDE A / SIDE B) prisukamas PER PERIMETRĄ (visos 4 kraštinės) pagal FOLDED PLATE formulę** (v258, Rytis):
     50 mm nuo kraštų, žingsnis ~300, n = round((kraštinė - 100) / 300) tarpų (800 -> 3 vietos, 300 -> 2), kiekvienoje vietoje
     po 1 tašką A ir B stiklui (keičia v139 „3 vnt. kraštinei" ir v254 „kas 150"; `screws_per_edge` - tik jei nurodyta).
   * **Maitinimas:** numatyta - laido išvestis ~230 V 1,5 m; **trafas ANT PADO po kojų uždengimais** (`"psu": "plate"` - be trafo
     plokštelės 1C, PSU ant plokštės 1A tarp kojų; patikrinti, ar PSU telpa po uždengimu); `"psu": false` - be trafo (12 V tiekia
     klientas); visada raudona pastaba klientui po „WALL DRILLING", kur ir koks laidas išeina.

27. **3D VAIZDŲ ŽYMOS (SIDE A / SIDE B ir pan.) - ŠALIA OBJEKTO, NIEKADA ANT JO (v256, Rytis 2026-10-15):** jokio užrašo ant
   3D objekto paviršiaus (stiklo, korpuso, logotipo). Žyma - po objektu (žemiau žemiausio projekcijos taško) su trumpa nuorodos
   linija į žymimo paviršiaus apatinės briaunos vidurį; jei po objektu netelpa (vaizdo pavadinimas) - šalia kairėje / dešinėje.
   Bendras `lapas_core.side_label_3d(V, face_pt, obj_pts, txt, ymax=...)` - naudoti VISUOSE generatoriuose (`sviesdeze.py`,
   `p10_lightbox_doublesided.py`, nauji); savų žymų ant 3D nerašyti.

34. **TAISYKLĖS VYKDOMOS KODU, NE TEKSTU (v291, Rytis 2026-10-15: „kodėl neimama naujausia informacija? profilio pjūvis
   visada centruojamas savo bloke ... numeracijos skaičiai negali persidengti ... lentelėje nesuprasi - m ar mm? ... tai jau ne
   pirmas kartas")** - PRIEŽASTIS: taisyklės 5 (centravimas) ir 30 (mm, kablelis) buvo įrašytos tik SKILL tekste; projekto
   skriptai (kopijuoti iš senų projektų, pvz. Horten -> Bodø) rašė savo koordinates ir eilutes ranka, o patikra tikrino tik
   linijų / tekstų persidengimus - todėl pažeidimai praėjo su „0 klaidų". Dabar kiekviena lapo taisyklė privalo turėti:
   (a) vykdymą `lapas_core` (generatorius negali jos apeiti) IR (b) patikrą `patikra_lapas.py` (lapas neatiduodamas, kol ne 0):
   - pjūvio / profilio / DETAIL blokas -> `K.centered(x, y, w, h, fn, pavadinimas)` (išmatuoja tikrą turinį ir centruoja);
     patikra 12 NECENTRUOTA BLOKE (> 3 % / 3 pt) ir NETELPA BLOKE (tekstas per bloko kraštą);
   - pozicijų balionai -> `leader()` pats atitraukia naują balioną nuo esamų (>= 2 pt); BOM POS balionai mažinami pagal eilutės
     aukštį (>= 1 pt tarpas); patikra 9 BALIONAI PERSIDENGIA (visas lapas, ir lentelės);
   - dešimtainis kablelis -> `T()` automatiškai (`4.2x16` -> `4,2x16`, `1.5 m` -> `1,5 m`); patikra 10 DEŠIMTAINIS TAŠKAS;
   - vienetai lentelėse (BOM / MAIN DATA / TITLE) -> `K.cell_units`: matmenų grupė gauna „mm" („30x30x2" -> „30 x 30 x 2 mm",
     „2000 x 1063" -> „2000 x 1063 mm", „Ø6" -> „Ø6 mm"), vienas skaičius matmens laukelyje (Depth, Size...) -> „80 mm";
     kiekiai - „m" / „m²" / „pcs." (rezultatas, be „2× 0.465 ="); Ø grupė su „x" (matmuo ar kiekis?) - generatorius rašo
     aiškiai („Ø16 x 20 mm", „Ø4 mm: 41 pcs."); patikra 11 VIENETAS NENURODYTAS;
   - nauja Ryčio taisyklė -> tą pačią sesiją: įrašas SKILL + vykdymas lapas_core + patikros punktas. Projekto skriptas,
     nukopijuotas iš seno projekto, prieš naudojimą peržiūrimas pagal VISAS dabartines taisykles (ne tik pakeičiami duomenys).

33. **ADAPTIVE CAD DRAWING LAYOUT - PRIVALOMA (v289, Rytis 2026-10-15). Pilnas tekstas - `references/adaptive_layout.md`
   (perskaityti prieš kiekvieną naują lapą).** Išdėstymas prisitaiko prie gaminio geometrijos, ne geometrija prie šablono:
   - FRONT / SIDE / REAR - VIENAS bendras mastelis, didžiausias telpantis su anotacijomis (`LE.pick_scale`; ISO 5455 pirmiau,
     tarpinis 1:15 / 1:25 tik nurodant); joks vaizdas nedidinamas / nemažinamas atskirai „dėl vietos";
   - DETAIL / SECTION - savas didžiausias tinkamas mastelis (1:1, 1:2, 1:5, 1:10), visada nurodytas;
   - 3D - NOT TO SCALE, vienodas koef. visoms ašims, centruojamas pagal matomą kontūrą (`View3D.fit`), dominuojantis
     matmuo 85-100 % savo zonos; zonos plotis = `LE.proj_aspect` x aukštis (ne tuščias langelis);
   - stulpelių pločiai = geometrija + matmenų / pozicijų / užrašų juostos; laisvas plotas - VIENODAIS tarpais
     (`LE.distribute`, kraštų paraštė = 0,5 tarpo); pavadinimai vienoje eilėje; papildoma detalė - po kita detale;
   - prioritetai: tikslumas -> bendras mastelis -> įskaitomumas -> jokių kolizijų (patikra = 0) -> didžiausi vaizdai ->
     laisvo ploto panaudojimas -> balansas; netelpa - pertvarkyti zonas, mažinti mastelį, siūlyti papildomą lapą / formatą,
     NIEKADA nekirpti, neslėpti matmenų, nemažinti teksto;
   - v290: detalių zona skaidoma į stulpelius pagal turinį (mažas elementas, pvz. TRAFO BOX, nedalinasi atskiro stulpelio -
     dedamas virš / po detale); vienas stulpelis neperkraunamas, kol šalia tuščia; DETAIL ne aukštesnė nei 0,6 projekcijų
     (`pick_scale(cap_pt=(1e9, 0.6 * H_ortho))`) - vizualinė hierarchija: pagrindinės projekcijos dominuoja;
   - generatorius spausdina `LE.report` (mastelis, tarpas, zonų užpildymas %); naujas gaminys - pilnas perskaičiavimas.

32. **FOLDED PLATE + LIPDUKAI - BENDRAS GENERATORIUS (v283, Rytis 2026-10-15, BrandFactory Joker order 226057 eskelokk):**
   raktažodis `folded plate + lipdukai`, `scripts/folded_vinyl.py spec.json out.pdf` (anksčiau - tik projektų skriptai OKQ8 /
   SPAR). Taisyklės - `references/moduliai_folded.md` („bendrinės", „kelios dalys vienoje plokštumoje", „+ pjaustyta plėvelė"):
   - vienas lapas kiekvienai plokštei (`panels`); grafika - kliento vektoriai, spalva -> plėvelės kodas (`vinyl[].fills`);
     nežinoma spalva - konsolės perspėjimas; kodo nėra legendoje (pvz. logotipo juodas kontūras) - „?" + klausimas;
   - išklotinė didesnė už lakštą -> horizontali sandūra grafikos tarpe (>= 50 nuo grafikos, apvalinta 5); v284: dalių išklotinės
     turi tilpti MAŽIAUSIAME lakšte - pirmiausia 3000x1500, tik tada 4000x2000 (Rytis: „viršutinės dalies išklotinė turi tilpti
     į 3000x1500"),
     L 30x30x2 tik viso skydo viršuje / apačioje, sandūroje Ø6 ~500, DETAIL B; `joints_y` - priverstinė sandūra;
   - grafikos padėties matmenys: kairėje grandinė (objektų viršus / aukštis), viršuje / apačioje - pirmo / paskutinio objekto
     plotis ir atstumai iki kraštų; užrašo eilutė (žodžiai, skliaustai) - vienas objektas;
   - BOM: plėvelė kiekvienai spalvai, kodas MATERIAL langelyje su spalva, kiekis - SUNAUDOJIMAS (`plevele.plan`, balta 1320,
     spalvota 1190); išvestis: PDF + išklotinių DXF (dalims su Ø6) + plėvelių ploterio DXF kiekvienai spalvai;
   - detalių / galinio vaizdo geometrija - hairline (VIEW), matmenys / išvadinės - kaip visur (patikra = 0).

31. **MIŠRŪS PRIEKIAI VIENOJE IŠKABOJE ANT U BĖGELIŲ (v282, Rytis 2026-10-15, BrandFactory Order 226030 Securitas -
   „įtrauk tokią iškabą į skill"):** raktažodis `mišrūs priekiai ant U bėgelių`, šablonas `assets/spec_misrus_priekiai_U.json`,
   etalonas `assets/etalonai/BF_226030_Securitas_misrus_priekiai_5S_P6_ant_U.pdf`. Taisyklės:
   - kiekviena grupė (pvz. apskritimai / raidės) - savo `"front"` (5S color - spalvota plexi 3 mm su PVC borteliu A/B;
     P6+foil - balta 8 mm + plėvelė), BOM priekio ir šonų / dugnų eilutės - atskirai kiekvienai grupei; A/B eilutės lieka,
     jei bent viena grupė 5S;
   - pjūvio langelyje - po pjūvį kiekvienam priekiui, VIENODO mastelio;
   - rėmas „tik U profilis" = grupės `"ears": false`; kliento bėgeliai ignoruojami (`ignore_fills` + `"auto_frame": true`),
     rėmas pagal taisyklę; pilnaviduriams elementams (apskritimams) bėgelių galai iki krašto (>= 10 mm viduje);
   - vienodi nešantieji bėgeliai galiniame vaizde - vienas matmuo `n× L`;
   - išdėstymas `"layout": "rows"`: priekis (+ šonas, tarpas >= 90 pt) | galas tame pačiame mastelyje, apačioje didelis 3D;
   - BOM kiekyje - tik rezultatas (sunaudojimas su atliekomis), be lakšto matmenų; spalvota plexi / plėvelė - langelis su
     spalva (`lapas_core.PLEXI`, `FOIL`); NCS / PMS kodai - be „RAL" priešdėlio;
   - laidai: kiekvienai grupei 12V nurodyto ilgio iš nurodyto bėgelio (`"cable_exits"`) + `"trafo_box"`.

30. **CAD MATMENAVIMAS PAGAL ISO 129-1 - PRIVALOMA (v275, Rytis 2026-10-15: „kodėl vėl nesilaikoma cad matmenų pateikimo
   brėžinyje? vėl linija ant linijos, žmogaus akiai tai labai klaidinanti informacija"):** pilnos taisyklės -
   `references/cad_matmenavimas_ISO.md` (skaityti prieš kiekvieną naują vaizdą / generatorių). Svarbiausia:
   - vienetai tik mm; antraštėje „ALL DIMENSIONS IN mm UNLESS OTHERWISE SPECIFIED" (REVISIONS juostoje), prie matmenų „mm" nerašoma;
     dešimtainis KABLELIS (`15,5`), be „,0" (`lapas_core.dim_lbl` - automatiškai visose `hdim` / `hchain` / `vchain`);
   - >= 3 vienodi gretimi intervalai - `n× v (= L)` (`hchain` automatiškai; vidinės iškeltinės / rodyklės nebraižomos);
   - grandinėje tarp dviejų mažų tarpų - TAŠKAS, ne dvi rodyklės viena ant kitos;
   - hierarchija: vietiniai arčiausiai, gabaritas toliausiai; matmuo NEDUBLIUOJAMAS kitoje eilėje / projekcijoje (pvz. stiklo 1550
     viršuje -> apačioje tik 100 | 5 + gabaritas 1655; pjūvyje A-A tik gabaritai, sluoksniai - DETAIL B; plokštė = stiklo aukštis ->
     antras 470 nededamas; kojos ilgis - BOM, jei lape kirstų kitą grandinę);
   - JOKIOS LINIJOS ANT LINIJOS: iškeltinė baigiasi PIRMAME kontūre nuo matmens pusės (`braizyti_begeliai.first_hit`, `extreme(...,
     near)`), niekada neina išilgai kontūro / išpjovos / plokštės krašto; skylės centro iškeltinė - centro linijos TĘSINYS (prasideda už
     jos galo); matmens linija gali eiti nario ašyje be iškeltinių;
   - pjūvio žymės (`cut_plane(..., out=(viršus, apačia))`) - UŽ matmenų eilių, ne ant jų, be jungiančios linijos;
   - žymų išvadinės įstrižos (~70°), ne lygiagrečios iškeltinėms; matmens tekstas jų juostą aplenkia (`avoid`).
   `patikra_lapas.py` tikrina: 6 LINIJA ANT LINIJOS, 7 MATMENYS KERTASI, 8 RODYKLĖS PERSIDENGIA (+ senos LINIJA PER TEKSTĄ, IŠVADINĖ
   KERTA) - lapas atiduodamas tik su 0. Patikrinta: danbolig DB-0001 / DB-0002, OMJE / EXLA, LEAP 01002 / 02002-1 / 06002,
   šviesdėžės 700 / 500, P10_lightbox_doublesided A / B - visi 0.

29. **KLIENTO / SENO DARBO PAVYZDYS - TIK TAI, KĄ JIS RODO (v270, Rytis 2026-10-15: „P6 turi atitikti standartą, įkeltas brėžinys
   buvo išskirtinai rėmo"):** atsiųstas pavyzdys (pvz. BILB26-01001) perimamas TIK jo tema (čia - montavimo rėmas); visa kita
   lape (P6 profilis, LED, dažymas, lapo stilius) - mūsų PATVIRTINTI standartai (`p6_ref` etaloninis pjūvis ir t. t.). Naujas
   elementas braižomas KARTU su standartiniu pjūviu tame pačiame mastelyje (`p6_ref.draw(..., no_rail=True, after=...)`).
   Pjūvio balionų numeriai = BOM pozicijos (1 priekis, 2 šonas, 3 nugara, 4 LED, 5 bėgelis / fonas / fasadas - BOM rikiuoti taip).

28. **SPALVŲ KODAI BOM - VISADA SU SPALVA LANGELYJE (v260, Rytis 2026-10-15: „ir vėl nėra spalvų ant spalvų kodų lentelėje"):**
   kiekvienas spalvos kodas (RAL, **NCS** - `lapas_core.ncs_hex` artinys, plėvelė ORACAL / Avery / 3M, PMS) BOM langelyje
   nuspalvinamas; naujas kodas, kurio nėra bibliotekoje (`VINYL`, `PMS`, `assets/pleveles.json`) - PRIDĖTI su hex artiniu, ne palikti
   baltą. Patikrinti lapą akimis - balto langelio su spalvos kodu būti negali.
   **Plėvelė (lipdukas):** MATERIAL = plėvelės kodas (`3M 100-54`, nuspalvintas), FINISH = „-"; Pantone / kliento spalvų aprašų
   prie FINISH NErašyti (jie - tik kliento PO, plėvelė jau apibrėžia spalvą).
   **LED IR PSU - BE MODELIŲ IR SPECIFIKACIJŲ (v262, Rytis 2026-10-15: „LED ir PSU modelių nurodyti nereikia, konkretūs
   pavadinimai ir specifikacijos tik su paklausimu. Brėžinyje tik LED ir PSU"):** VISUOSE lapuose (visi generatoriai, BOM, MAIN DATA,
   LED lentelė, kliento spec BOM eilutės) rašoma tik „LED" ir „PSU" + kiekis ir išdėstymas (vieta, žingsnis); gamintojo, modelio,
   W, lm, lx, K, IP, spindulio kampo - NErašyti. Konkretūs pavadinimai / specifikacijos - TIK kai Rytis paklausia (vidiniai
   skaičiavimai `led_km` / Kaisen lentelė lieka kiekiui ir žingsniui parinkti). Įgyvendinta `sviesdeze.py`,
   `p10_lightbox_doublesided.py`, `p10_lightbox_singlesided.py`.

25. **AKRILINIS (SKAIDRUS ORGSTIKLO) RĖMAS raidėms (v229, Rytis 2026-10-14, Leapmotor):** `braizyti_begeliai.py` spec
   `"mounting": "acrylic"`, `"rail": {"type": "acrylic", "size": "<plotis>x<storis>"}` (pvz. 40x20), `"acrylic": {...}`.
   Rėmas = viena plokščia CNC detalė iš 20 mm skaidraus orgstiklo (bėgeliai + statmenys sujungti), padalinta į dalis pagal
   lakštą (3050 x 2050) **puzzle jungtimis (laisvumas 0,2), pjūvis kiek įmanoma PO RAIDĖMIS**; **jungtys pagal lakšto ilgį
   PAŽYMIMOS** galiniame vaizde (brūkšn. taškinė J1.., dalių ilgių grandinė + „acrylic sheet ... -> parts <= ..."; v231);
   **2 lapas „ACRYLIC FRAME - PARTS & JOINTS" (v233):** dalių vaizdas iš galo (R.., V.., J..), DETAIL C - bėgelių jungtis
   pagal lakšto ilgį, DETAIL D - statmuo -> bėgelis, SECTION E - bėgelis su grioveliu; juostoje „WHY / WHERE THE FRAME
   JOINS" (kodėl: lakštas trumpesnis už rėmą; kur: po raide; statmenys atskirai - taupoma medžiaga) + dalių BOM;
   1 lapo galiniame vaizde nuorodos C / D „sheet 2".
   **mažos raidės (tarp 2 bėgelių < bėgelio plotis): VIENAS bėgelis 60 mm** (platesnis, jei trukdo tvirtinimui / laidams;
   `"acrylic": {"single_w": 60}`), statmenų nėra (v243, Rytis 2026-10-15).
   **statmenys / įstrižai - ATSKIROS detalės, į bėgelius jungiami PUZZLE** (galvutė statmens gale, bėgelyje išpjova su
   laisvumu; v232 - taupoma medžiaga); profilio pjūvis - etaloninis P6 (`p6_reference` square + `p6_ref.ACRYLIC`, v232);
   **statmenys per stiebus žingsniu `v_pitch` 1000 mm** (v231, Rytis: „per daug statmenų" - NE po kiekviena raide;
   `"every_letter": true` - tik jei paprašyta; kraštas po štrichu `v_edge` 3 mm);
   **smeigės pagal raidės FORMĄ** (kvadratas 4, trikampis 3...; v245), **arti štricho CENTERLINE** (ne prie krašto), ant bėgelio -
   **viena horizontali linija** (kitoje y - tik raidei, kuriai bendroje linijoje < 2); vienas bėgelis mažoms - nuo **55 mm**;
   panašios raidės - vienodai (P kaip R); išilginiame štriche - galuose; maža raidė (< 200) - iki 3; smeigės ir statmenyse (v246);
   **KIEKVIENA raidė / dalis - >= 2 smeigės** (v244, Rytis: „ant vieno varžto negerai"; ilgoms - kas ~400; bet kur bėgelio
   juostoje, toliausiai viena nuo kitos; vienas bėgelis platinamas, kol visos dalys gauna >= 2);
   **raidės prisukamos per ATSKIRAS ĮLEISTAS SKYLES** bėgelio ašyje po raidėmis (Ø5 kiaurai + Ø12 x 15 iš galo veržlei,
   privirintos smeigės raidės nugaroje; `"stud"`), laidų griovelis paslinktas nuo ašies, ovalios skylės laidui prie raidžių;
   **Ø8 tvirtinimo skylės tarpuose tarp raidžių, kas antrame tarpe**; **laidų griovelis nugaroje 8 pločio x 10 gylio**
   (`"groove": {"w": 8, "d": 10}`, DXF sluoksnis GROOVE_BACK_8x10_DEEP + ašis);
   simbolis / ženklas - ant TO PATIES rėmo (bėgeliai tęsiami per tarpą - skaidrus); ausėlių / 6 m strypų nėra.
   Išvestis: lapas (rėmas skaidrus melsvas, REAR VIEW - dalys, puzzle, Ø8, griovelis), 1:1 PDF, `_akrilinis_remas.dxf`.
   `auto_remas.rows_of` - eilutės aukštis = raidžių aukščių mediana (aukštas logotipo ženklas netampa eilutės matu).

## Standartai (v161, Rytis 2026-10-13; iš darbų analizės `DARBAI/uzsienio reklama` 2024-2026)

Galioja visiems klientams, jei kliento faile (`references/klientai/*.md`) nenurodyta kitaip.
- **Darbinis failas - .cdr.** Gamyba dirba TIESIAI iš CorelDRAW failo: A3 lapas (puslapis) + 1:1 gamybinė geometrija šalia
  lapo ant Corel „stalo" tame pačiame faile. DXF - tik kai jo prašoma.
- **Pirminis dokumentas `ALT0000_00.00_RS`** - į jį įrašomas kliento ORDER numeris; ALT numeris atsiranda patvirtinus pagal
  sistemą (`references/patvirtinimas.md`). Pirminio lapo neperspėti kaip „neužpildyto".
- **Lapo blokai** - kaip skill'e (MAIN DATA / BOM, `references/stilius.md`). Seni Corel lapai su MAIN MATERIALS / COLORS /
  MOUNTING WAY / PERIMETER ir C / B / P / I juostomis - tik duomenų šaltinis, ne šablonas.
- **Rėmo profiliai: 20x20x2 / 30x30x2 / 40x40x2 / 60x60x2 / 80x80x2.** Kiti - tik pagal atskirą užklausą (kliento standartas
  ar Ryčio nurodymas); `medziagos.is_standard_profile`, `profile_check` perspėja.
- **Spalvos - RAL / PANTONE / NCS** (pagal kliento nurodymą, su blizgumu, jei duotas, pvz. „RAL 7024 70 % gloss").
  Kliento spec. kodai rašomi kaip yra (Volvo **RAL 50050** - tikras Volvo spec kodas, ne klaida).
- **Opalinė plexi Plexiglas XT WN770** - Volvo ir BN Skilte standartas. **B1 polikarbonatas** (PALSUN B1 / Exolon UV) - tik
  BN Skilte standartas.
- **LED spalvinė temperatūra** - pagal kliento nurodymą; nenurodyta - **6500K**.
- **Maitinimas:** numatyta Kaisen KPS / BaltLED BPS (abu naudojami, žr. „LED"). **Mean Well (HLG / XLG / LPV ...)** - TIK kai
  nurodo klientas (kliento specifikacija ar standartas, pvz. Volvo / DSV / BN Skilte lapai) arba Rytis.
- **Trafo dėžė:** „Plastic IP box with WAGO inside", „Trafbox", PWM / potenciometras (pritemdymui) - leistini variantai
  (`references/moduliai_kiti.md` „TRAFO BOX").

## Įvestis

1. Kliento PDF (dažnai Illustrator / CorelDRAW, NE 1:1, mėgėjiškas, kartais ne vektorinis,
   kartais be jokių matmenų).
2. Trumpas aprašymas santrumpomis (žr. žodynėlį). Aprašymas svarbesnis už kliento failo vaizdą
   (spalvos, profilis) - neatitikimą paminėk atsakyme.

## Darbo eiga

0. **Žinių paieška (v264, taisyklė 0):** `python3 scripts/ziniu_paieska.py <produktas> <raktažodžiai>` - perskaityti šeimos
   aprašus ir rastas taisykles, pasirinkti geriausią analogą (etalonas / naujausias projektas), patikrinti generatorių.
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
5. **AUTOMATINĖ PATIKRA (v175, PRIVALOMA):** `python3 scripts/patikra_lapas.py lapas.pdf [--skip x0,y0,x1,y1]` - 0 klaidų, kitaip lapas
   neatiduodamas (taisyti generatorių, ne rankomis). **Patikra akimis:** VISADA išrenderink PNG (`pdftoppm -r 80 -png`) ir palygink su etalonu:
   ar niekas nepersidengia, ar nėra didelių tuščių plotų, ar kontūrai hairline.
6. **Atsakymas:** mastelis ir patikrinti matmenys; elementų lentelė (aukštis, plotis, min. storis);
   ką priėmei pats; tikslūs klausimai tik apie tai, kas tikrai neaišku.

## Produktų moduliai (BENDRINĖS - visiems klientams)

### P6 priekio variantai (galioja visiems P6 moduliams; spec `"front"`)
**Vaizdavimas (v59, Rytis 2026-10-09, tikslas >= 95 % realaus vaizdo):** STIKLAS = ORIGINALUS kliento failo kontūras,
matomas stiklo kraštas 3 mm (P6_8mm frezuojama taip, kad kraštelis liktų 3 mm); KORPUSAS (šonai) 1,5 mm MAŽESNIS už
stiklą (offset -1,5), gylis - 3. +foil variantuose šoniniame vaizde ir 3D matosi: korpuso spalva | BALTAS stiklo
kantelis 3 mm | plėvelės spalva priekyje (color variante kantelis = plexi spalva). Kodas `scripts/p6_vaizdas.py`
(`layers`, `add_3d` r3d scenai, `side_view`, `rear_view` - galiniame vaizde dugnas 1,5 mm mažesnis už stiklą, aplink matosi stiklo kraštas); bandymas - `scripts/projektai/p6_vaizdas_test/s_demo.py` (S, 5S+foil).
Taikoma VISUOSE projektuose automatiškai (v60): `braizyti_begeliai.py` (`P6_REAL`) ir `braizyti_lapa.py` šoninis vaizdas
ir 3D; lape papildomų aprašymų apie tai NEDEDAMA - tiesiog taip atvaizduojama. P1 / „behind" / plokšti elementai - kaip anksčiau.

Užklausoje nurodoma priekio kodas (v90, Rytis 2026-10-11; vienas parseris visiems skriptams - `scripts/p6_front.py`):
| Kodas | Priekis (1) | Konstrukcija (A / B) | BOM priekio eilutė |
|---|---|---|---|
| `5S` (buv. P6_3mm, v210) | polikarbonatas 3 mm FR (antipireninis) | PVC 3 mm bortelis ~15 mm, įleistas 1 mm į priekį; šonas Alu 1 mm 2 mm nuo priekio krašto, tarpas 1 mm; varžtas 2.9 mm per Ø3 skylę šone į bortelį (`assets/konstrukcijos/5S_profilis.pdf`) | `Polycarbonate 3 mm FR white`; A `Fitting PVC edge 3 mm`; B `Screw 2.9 mm, return -> PVC edge (hole Ø3)` |
| `5S+foil` | polikarbonatas 3 FR + plėvelė | kaip 5S | `Polycarbonate 3 mm FR white` + `Front foil <kodas>`; A, B |
| `5S color` | spalvotas 3 mm priekis | kaip 5S | `Polycarbonate 3 mm FR <spalva>`; A, B |
| `P6` (buv. P6_8mm, v233) | balta plexi 8 | frezuota su kanteliu (matomas kraštelis 3 mm, liežuvis korpuse), varžtas per šoną į liežuvį | `Acrylic 8 mm white`; A/B eilučių NĖRA, PVC NĖRA |
| `P6+foil` (buv. P6_8mm+foil) | balta plexi 8 + plėvelė | kaip 8mm | `Acrylic 8 mm white` + `Front foil <kodas>` |
| `P6 color` (buv. P6_8mm color) | spalvota plexi 8 | kaip 8mm (tik spalvota) | `Acrylic 8 mm <spalva>` |
| `P6_10mm` / `15mm` / `20mm` / `30mm` (+foil) | balta plexi 10-30 (+ plėvelė) | frezuota su kanteliu kaip 8mm (liežuvis = storis - 3) | `Acrylic N mm white` (+ `Front foil`) |
**v233 (Rytis 2026-10-14): P6_8mm -> P6, P6_8mm+foil -> P6+foil. PROFILIS P6 VIENAS - naudojamas ant įvairių paviršių ir profilių,
tvirtinimai įvairūs; pjūvis - visada etaloninis P6 (`p6_reference`, tvirtinimo variantas pagal montavimą).**
**v210 (Rytis 2026-10-14): P6_3mm PERVADINTAS į 5S - lapuose, BOM, MAIN DATA, specuose ir atsakymuose rašoma 5S (5S / 5S+foil / 5S color); senas kodas P6_3mm priimamas kaip sinonimas (`p6_front.py`). Šonas 2 mm nuo priekio krašto (`p6_vaizdas.body_inset`).** Spalvota - tik 3 ir 8 mm, kiti storiai - tik balta (su plėvele arba be); kitaip skriptas perspėja. Kantelis baltas visada,
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
  **!!! v191 (Rytis 2026-10-13): galiniai statmenys - TARP bėgelių, bėgeliai per visą rėmo ilgį; statmenų ilgis nežymimas;
  ausėlė ant galinio statmens nebededama (kraštinės - pora tarp raidžių) - žr. „Bendrinės taisyklės" 12-14. Žemiau - istorija. !!!**
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
- Pavyzdžiai: `assets/spec_matkroken.json` (5S color, U30, rašytinis šriftas, 12V 2 m),
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

### Plėvelių spalvų biblioteka (v142, Rytis 2026-10-12)
`assets/pleveles.json` - pilnos gamintojų paletės: **ORACAL 8500** (translucent, šviesdėžėms, 54 sp.), **ORACAL 551**
(opaque calendered, 86 sp.; 701 - deep black gloss, **702 - deep black matt**; 070 serijoje nėra), **Avery 4500 TF**
(translucent calendered, 38), **Avery 5500 QM** (translucent cast, 65), **Avery 777** (opaque cast, 100; 777-002 - Sweet Red),
**3M 3630** (translucent, 78; 3630-22 juoda ir 3630-69 Duranodic - praktiškai nepralaidžios).
- Kodą rašyti gamintojo formatu: `ORACAL 8500 034`, `ORACAL 551 702`, `Avery 4506` / `Avery 5510-01` / `Avery 777-002`,
  `3M 3630-33`. `lapas_core.code_hex()` BOM FINISH / MATERIAL langelį nuspalvina pagal biblioteką (`film_lookup`).
- Šviečianti grafika (šviesdėžė, P6 + foil) - translucent (8500, 4500, 5500, 3630). Opaque (551, 777) ant šviečiančio
  veido - SĄMONINGAS sprendimas: grafika nepersišviečia, matosi tamsus siluetas šviesiame fone (v143, Rytis 2026-10-12:
  „juoda nepersišviečia, toks sumanymas") - neperspėti, nekeisti į translucent.
- Kodo bibliotekoje nėra -> perspėti, lape nerašyti be patikrinimo. Paieška: `python3 scripts/pleveles.py 551 702`,
  `python3 scripts/pleveles.py 8500 red`, `--series`.
- Hex - ekrano artinys: ORACAL - Orafol sRGB (8500 dar `hex_backlit`), Avery / 3M - apytiksliai (`approx: true`), ne spalvų
  atitikimui. 3M 3630 sąrašas iš US produkto biuletenio - ES prieinamumą tikrinti pas tiekėją.

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
- **ATSKIROS RAIDĖS (v191, Rytis 2026-10-13):** plėvelė ant atskirų raidžių priekių (P6 ir kt.) - NESTING: kiekviena raidė atskirai,
  sudėliojama kompaktiškai ant rulono (`--separate`); „užrašo eilutė - vienas objektas" tik vientisam lipdukui.
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

### P10_lightbox_doublesided (buv. P10_lightbox) / P10_lightbox_singlesided (v227) -> `references/moduliai_p10_lightbox_doublesided.md`, `references/moduliai_p10_lightbox_singlesided.md`
v227 (Rytis 2026-10-14): P10_lightbox PERVADINTAS į **P10_lightbox_doublesided** (generatorius `scripts/p10_lightbox_doublesided.py`,
testas `scripts/projektai/p10_lightbox_doublesided_test/`, etalonas `TEST_P10_lightbox_doublesided_B.pdf`). Nauja pozicija
**P10_lightbox_singlesided** - priekis kaip doublesided, dugnas paprasta folded plate 3 mm mažesnė, tūris 30, priekis užmaunamas ant
dugno ir prisukamas (standartas), prie fasado per dugną (skylių nebraižyti), laidas - dešinės šoninės viršuje, dugno atlanke skylė
su tarpine, centras 23 nuo dugno priekinio krašto, priekio atlanke išpjova; eskizas patvirtintas, generatorius - dar nėra
(atviri klausimai moduliai_p10_lightbox_singlesided.md 3).

### Šviesdėžė dvipusė nuo fasado (v134, įgyvendinta) -> `scripts/sviesdeze.py`
Rytis 2026-10-12: „paprasčiausia dvipusė šviesdėžė nuo fasado: kojos - pailgintos rėmo dalys, apsijuosia aliumu, stiklas abiejose
pusėse tvirtinasi kaip 5S". Pozicijos kaip etalono Parts List: 1 rėmas □30x30x2 Alu (gylio viduryje), viršutinis / apatinis
skersiniai pailginti iki sienos = kojos (ašis tb + 15 nuo krašto), 1A padas 100x100x8 R10, 4 x Ø10 / 64, centre laido anga
(vamzdžio vidus), privirintas; 2 korpusas 1,5 mm Alu juosta (gylis 100), sienos pusėje angos kojoms; 3 / 5 - 3 mm opal plexi
abiejose pusėse (užeina ant juostos krašto, bendras storis gylis + 2 x 3); 4 / 6 - PVC juosta 3 x 15 prie plexi, juosta
prisukama į ją (5S); 7 LED + PSU; 8 savisriegiai.
**v135 (Rytis): 5S tipo tvirtinimas - STIKLAS VISADA DIDESNIS UŽ KORPUSĄ, korpusas mažesnis 1,5-2 mm kiekvienoje pusėje**
(`face_over`, numatyta 1,5; gabaritas = stiklas). Lapas privalo turėti: rėmo matmenis (išorė, kiekvieno nario ilgis, kojos
išsikišimas, ašys), gręžimo schemą iš sienos su VISOMIS skylėmis x / y (grandinės + bendras atstumas tarp kraštinių skylių ir
iki stiklo), LED tipą, kiekį, vietą ir žingsnį. LED dvipusėms dėžėms - **Kaisen DUOLITE DS15 / DS20** (šviečia skersai dėžės
10° x 65°, ant rėmo skersinio gylio viduryje): lentelė `kaisen_led.json` -> `duolite` (dėžė 1000 x H, gylis, žingsnis -> lx);
LED ant APATINIO IR VIRŠUTINIO skersinio (v139, Rytis); **TŪRIS (gylis) 500 x 500 dydžiui - 140 mm** (v140, Rytis: LED pakelti
ant rėmo - mažesniame tūryje kraštai neiššviečiami; numatyta `depth` 140; didesnėms dėžėms - ne mažiau, tikslinti);
logotipas - `"logo"` spec (PNG -> `vektorius.py`), centre abiejose pusėse, abiejose skaitomas normaliai; DS15 nuo 100 gylio, DS20 nuo 140. Varžtai: PAGAL DYDĮ (v254, taisyklė 26; `screws_per_edge` - tik jei nurodyta).
Alt Reklama kainoraštyje DUOLITE nėra - tiekimą tikslinti.
**v136 (Rytis):** priekio vaizde pastabų apie stiklą / korpusą NEDĖTI (tai pjūvyje); VISADA rodyti **SIDE A ir SIDE B** (pusėse būna
skirtinga informacija): 1 lape FRONT VIEW - SIDE A | VIEW FROM WALL (gręžimo schema) | FRONT VIEW - SIDE B (veidrodinis),
3D iš abiejų pusių su užrašais SIDE A / SIDE B; mastelį rinktis pagal lapo dizainą (`scale_ga`, numatyta 1:8). Korpuso juostoje -
**D3.2 skylės savisriegiams**: kiekvienoje kraštinėje 2 eilės į PVC juostas (7,5 nuo kraštų, kas <= 150); per juostos centrą
skylių NĖRA - juosta virinama prie rėmo (v137);
2 lape - BODY BAND išklotinė 1:10 (lenkimai, skylės, kojų angos). Lapas: FRONT (A pusė, rėmas punktyru, kojos, išsikišimas),
SIDE iš sienos (padai su skylėmis), SECTION A-A, FLANGE 1:2, 3D, juostoje DETAIL B 1:1 (kraštas). Spec raktai: w, h, depth,
leg_len, flange, hole_d, hole_pitch, frame, face, body_finish, frame_finish, led, psu, cable, anchors, qty.
**v144 (Rytis 2026-10-12): KOJOS ŽEMESNĖS UŽ DĖŽĘ** - „tokio pat stiliaus, tik kitoks rėmo sprendimas, kojos žemesnės nei
šviesdėžė, kojos turi uždengimus". Etalonas `assets/etalonai/sviesdeze_dvipuse_kojos_zemesnes.pdf` (700 x 370 x 120, nuo sienos
800), spec `assets/spec_sviesdeze_700x370_kojos.json` -> `"legs_type": "inset"`. Principas (stiklas > korpusas, PVC juosta,
varžtai, DUOLITE viršuje ir apačioje, SIDE A / B) - tas pats; skiriasi rėmas: 1 rėmas 40x20x2 (`frame` [20, 40, 2] - 20 plokštumoje,
40 gylyje) - viršutinis, apatinis skersiniai + priekinis statmuo, sienos pusėje statmens NĖRA; 1B kojos □40x40x4 (`leg`) TIESIAI
PO skersiniais, įlenda į dėžę `leg_in` 53 (ilgoji briauna prie skersinio), vidinis galas nukirstas `leg_chamfer` 50°, privirintos;
1A VIENA montavimo plokštė 140 x 340 x 5 (`plate`; aukštis numatytas = kojų ašys + 40 + 16), 4 x Ø8 (`plate_hole_d`) kojų
ašyse, žingsnis 109 (`plate_pitch`), kabelio Ø11 (`cable_hole`) uždengimo viduje; 1C trafo plokštelė 1,5 mm tarp kojų
(PSU); 10 kojų uždengimas 2 mm Alu, 2 dalys (A + B veidrodinė) - PAGAL „Bendrinės taisyklės" 19 (v217: plotis kojos + 10, aukštis kojų matmuo + 2t, briaunos su išpjovomis), korpuso spalva,
ilgis 5 mm TRUMPESNIS už tarpą tarp plokštės ir korpuso (`cover_gap` 5, v145 Rytis) - v212: PO 2.5 mm iš ABIEJŲ galų (prie korpuso ir prie plokštės).
LED skersiniuose tik iki kojų (`led_b` = kojos pradžia - 10). `"proj"` - atstumas nuo sienos iki tolimo stiklo krašto
(kojos ilgis skaičiuojamas). 2 lape vietoj FLANGE - MOUNTING PLATE 1A + LEGS 1B 1:5.
**v218 (Rytis 2026-10-14):** 1 lapo 2 eilė - 3D SIDE A | 3D SIDE B | **ASSEMBLY - EXPLODED VIEW** (stiklas A + PVC 4 - korpusas 2 +
rėmas 1 + LED 7 + kojos / padai - PVC 6 + stiklas B; varžtai 8 ištraukti į viršų; uždengimas 10 virš dėžės, A / B į šonus;
balionai = BOM) | TOP VIEW. Juostoje **DETAIL B - SECTION TOP / BOTTOM** - pjūvis per VISĄ gylį (stiklas A | juosta + PVC + rėmas +
LED + varžtai | stiklas B) VIRŠUJE ir APAČIOJE (5S tipas), nutraukimo linija, pozicijos stulpeliais šonuose.
**v219 (Rytis 2026-10-14):** 2 lapas - SECTION C-C IŠIMTAS; FRAME (1) + LED (7) DIDESNIS (mastelis automatiškai pagal vietą,
`scale_fr`: 700 x 370 -> 1:4, 500 x 500 su padais -> 1:6) + šalia tame pačiame mastelyje ir aukštyje **FRAME - VIEW FROM WALL (END)**
(`end_view`): rėmo narių galai, padai / montavimo plokštė su skylėmis, kabelio anga, kojos punktyru, korpusas punktyru; matmenys -
skylės z / y nuo plokštės kraštų, plokštės plotis / aukštis, plokštės nuo rėmo išorės, rėmo aukštis, korpuso gylis. Atskiri
FLANGE / MOUNTING PLATE vaizdai nebenaudojami. Apačioje BODY BAND išklotinė 1:10. Antspaude - faktiniai masteliai.
**v223 (Rytis 2026-10-14): VIENAS LAPAS pagal TEST_P10_lightbox_doublesided_B** („Bendrinės taisyklės" 23) - 2 lapo nebėra: FRAME + LED ir
PLATE / FLANGE 1A - 1 lapo dešiniame stulpelyje, LED duomenys - rėmo pastaboje ir MAIN DATA, BODY BAND išklotinė - `_gamyba.dxf`
(lenkimai, Ø3.2, kojų angos) kartu su kojų uždengimu. Toliau v219-v222 - istorija.
**v220 (Rytis 2026-10-14):** 2 lapas - CAD stiliumi, be spalvų, tik linijos („Bendrinės taisyklės" 22); dažymas - spalva tik kojoms,
padams / plokštei ir korpuso išorei, rėmas viduje ir korpuso vidus - BALTI („Bendrinės taisyklės" 21; BOM: „white", „RAL ... legs",
„RAL ... out" / „inside white"; spec `frame_finish` = kojų / padų spalva).
### Kiti produktai (dar neįgyvendinta) -> `references/moduliai_kiti.md` (raidės ant sienos, kitos šviesdėžės, plokščios - konstrukciją klausti)

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
**v132-v133 papildymai `ilp()`:** sienelės užstoja - taškas apšviestas tik jei linija modulis -> taškas eina raidės viduje;
visas veidas iki sienelės - matomas modulis <= 0,8 p; linijos GALAI (E galiukai, t viršus / skersinis / koja) - <= 0,64 p;
grupėje kiekvienos raidės modulių tankis >= 0,9 x medianos (kitaip mažesnės / storesnės raidės - blankesnės, pvz. 7 ir 3 tarp 2).
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

## Dokumento blankas (v248, Rytis 2026-10-15) -> `lapas_core.title_body`; tuščias blankas `assets/blankas_A3.pdf` (`scripts/blankas.py`)
Antraštės lentelė: CLIENT | TITLE | ORDER NO. + FILE / DRAWING NO. | SCALE + FORMAT + REV. + PROJECTION | **DATE + DIDELIS JUODAS
kiekio blokas („N pcs.", baltas tekstas; spec `"qty"`) + DIDELĖ „Sheet x / y"**. DRAWN / CHECKED nebenaudojami.

## Lapas (v9) -> `references/stilius.md`
