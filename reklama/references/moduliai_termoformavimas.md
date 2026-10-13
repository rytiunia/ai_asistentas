# Termoformavimas (thermoformed / vacuum formed) - modulis

> v161, 2026-10-13: surinkta iš darbų aplanko `DARBAI/uzsienio reklama` (2024-2026) analizės; Rytis patvirtino, kad tai STANDARTAS. „(spėjimas)" - nepatvirtinta, prieš naudojant lape - klausti. Skyrius „Klausimai Ryčiui" - dar neatsakyta.

Raktažodžiai: thermoformed, thermoformated, termoforma, termoformavimas, vacuum formed, vakuumformet, vakuumformad,
3d forma, forma termoformavimui, Profile 1+10 / 01+6 vakuumformet (MENY Gen. 3), BK lightbox, Teboil fronts.
Rytis: „atskira tema". Lapo užrašai angliškai (kaip lapuose: „Thermoformated cover", „Thermoforming mold").

## Kada naudojama (iš failų)
| Atvejis | Pavyzdys | Kas formuojama |
|---|---|---|
| Lenktas logotipo dangtis su nuožulniais kraštais, ant jo P-raidės | MENY Gen. 3 (L950 / 1500 / 2000 / 2500 / 3000 / 4000 / 5000) | Thermoformated cover, 3 mm PLEXIGLAS GS (raudonas) |
| Iškilus logotipo priekis (reljefas) šviesdėžėje | Burger King H400 / 550 / 700 / 760 / 1220 / 1520 / 1830 | 3 mm (H1830 - 4 mm) plexi, grafika plėvelėmis arba spauda |
| Spausdintas priekis, termoformuotas po spaudos | Alfa Romeo „milano service" (ALT8134), Iris Galerie akis (ALT4490), Teboil segmentai | 2-3 mm skaidrus plexi + UV/solvent spauda |
| Tūrinių raidžių priekiai pilone | VOLVO 7,5 m / 9,3 m pilonams, VOLV24-03004 | raidžių V-O-L-V-O priekiai (spėjimas: 3 mm opal plexi) |
| Dvipusė kabanti (pendant) iškaba | MENY Trekanten 218475 (ALT7759) | 2 vnt. termoformuotų dangčių - žr. `moduliai_pendant.md` |
| Termoformuotos raidės | MENY Konnerud 203262 (ALT6058) | „Letters, thermoformated, 2 mm white plexiglas"; dangtis „3 mm RED ABS plastic, RAL 3020" |

## Medžiagos
- **MENY dangtis: 3 mm PLEXIGLAS GS Rot 3H25** (naujesni lapai ALT6967, Hovenga ALT7255, Haderslev); senas MENY 991 (2019) -
  „PLEXIGLAS GS Rot 3H01". Visada **GS (liejamas)** - XT termoformavimui lapuose nenaudotas.
- BK: „3 mm thermoformated plexiglas" (H1220, H1520), „4 mm thermoformated plexiglas" (H1830 ALT4610); 3 mm skaidrus
  („3mm skaidrus org stiklas", BK_Termoformavimas_20240828) arba 3 mm baltas (ALT2581 „Thermoformated front, 3mm white plexiglas").
- Alfa Romeo: 3 mm transparent plexiglass + Gel'UV print on transparent vinyl + white translucent vinyl background
  („Alfa romeo termo spauda etalonas": „solventine spauda 2 overprint / skaidri poli gloss").
- Iris Galerie: 2 mm transparent plexi, UV print CMYK 3 overprint + ORACAL 8800 white („KLIJUOTI SAUSAI !!!"), Ø~482 x 474, iškilimas 50.
- Teboil: UV print on 3 mm transparent plexiglas + white vinyl foil; segmentai 1800 x 595 (510 + 2 x 45 kraštai), gylis 40-80.
- Formos medžiaga: **MDF** (40 mm plokštė - MENY L950 / 3 m / 4 m; 30 mm - Volvo raidės; 20 mm „medžio dulkių plokštė" -
  MENY Konnerud raidės, 5 m forma); papildomas „pastorinimas" 5 mm MDF (priklijuojamas vidurinės dalies storinimas).

## Forma (mould) - kaip braižoma ir frezuojama
- Forma modeliuojama 3D (Fusion; failai `.stl` / `.obj` / `.skp` / `forma fusion dxf`) -> frezuojama CNC iš MDF.
  „Frezuojas su radiusine freza kaip 3D forma" (Volvo); „KAMPUS KAIP VISADA SU SFERINE FREZA" (MENY Konnerud);
  BK 1520: „nusifrezuoja gyliai / paskui su radiusine freza pagal kontura".
- **Formos offset'as = gaminio kontūras atėmus medžiagos storį:** Alfa „mazinta -3mm" (3 mm plexi); MENY Konnerud
  „raides -3mm nuo formos fusion dxf."; Volvo „forma TERMOFORMAVIMUI -6mm" (`VOL_termoformos_pjovimui.cdr`, sluoksnis
  OUTER_PROFILES - tik kontūrai pjovimui). Kodėl Volvo -6 (o ne -3) - lape nepasakyta (klausimas).
- Volvo raidžių forma: aukštis 30, šonų nuolydis 4° (86°), viršutinė briauna R3, vidiniai kampai R6 (detalė C 1:1).
  7,5 m pilonui V 559 x 282, O 410 x 297, L 400 x 282; 9,3 m - V 692 x 351, O 509 x 370, L 496 x 351;
  VOLV24-03004 - V 405 x 204, O 298 x 215, L 290 x 204.
- MENY L950 forma (ALT6967 lapas 2): 887 x 348, aukštis 37, nuožulnus kraštas 135°, briauna Ø20, plokštė 40 mm.
  Gaminys 950 x 409 (forma ~31 mm siauresnė iš kiekvienos pusės - dangtis įeina į „Front cover" rėmą).
- MENY Trekanten (pendant 700): forma 655 x 271, aukštis 20, nuožulnumas 32 mm / 148°.
- Dideli logotipai dalijami į dalis: 3 m - 2 dalys po 1444 x 1192 + 5 mm pastorinimas 1500 x 1293; 4 m - 3 dalys
  (40 mm MDF, „Isfrezavus forma, pritvirtinti kad gautusi kaip vientisa detale"); 5 m forma 1532 pločio dalimis.
- Formų lapai: atskiras A3 lapas „<projektas>_TERMOFORMA" / „forma termoformavimui" / „FORMOS TERMOFORMAVIMUI",
  rodomi 3D vaizdai, pagrindiniai gabaritai, pjūvis su nuolydžiu, užrašas „Plokste 40mm.". Šablonas `ALT0000_00.00_rycka`.

## Grafika ant termoformuojamo lakšto
- Plėvelės / spauda klijuojamos ANT PLOKŠČIO lakšto PRIEŠ formavimą. BK 1520: lakštas 2000 x 2050, grafika
  VEIDRODINĖ, užrašai „GRAZUS 3MM SKAIDRUS STIKLAS / PAZYMETI LINIJAS", „ANT STIKLO SUZYMETI CENTRUS"
  (pozicionavimui ant formos); viršuje / apačioje 265 mm laisvos juostos (spėjimas: įtvirtinimui mašinoje).
- BK plėvelės: 3M 3630-84 (oranžinė), 3M 3630-143 (raudona), ORAJET 3850-010 (balta); „At the joint, the films overlap 5mm".
- Po formavimo matmenys keičiasi - BK H1830 atskiras failas „matmenys po termoformavimo ... pleveles korekcijos".

## Kaip termoformuota detalė tvirtinama (konstrukcija)
**MENY Gen. 3 „Profile 1+10 vacuum formed"** (ALT6967 - etalonas, Hovenga ALT7255, MENY 991):
1. Thermoformated cover, 3 mm PLEXIGLAS GS 3H25;
2. Front cover (Cover edge), 2 mm Alu, dažyta RAL (7047 / 7024 / pagal užsakymą);
3. Bottom 2 mm / side 1,5 mm Alu su WHITE (raidėms) arba RED (dangčiui) LED moduliais;
4. Plexiglass fitting edge, 1,5 mm Alu;
5. Raidės - 15 mm white plexiglas, įklijuotos į raudoną plexi su išfrezuotu įdubimu („The letters are pasted into red
   plexiglass with a milled indentation": įleidimas 2 mm, raidės kraštas 2 mm, iškyša 10 mm) ARBA P6 raidės
   (MENY 991 / Hovenga: „Letters, profile 6, front white plexiglas", 8 mm priekis).
- Gylis: L950 - 100 (korpusas 50 + dangtis 40 + raidės 10); 1500 / 2000 - 50 + 45 + 35 (+raidės, iš viso 150).
- Drainage hole apačioje. Kabinimas: rėmas 20x20 Alu (MENY 991), Z 30x30x3 + wallframe Z (Hovenga, 220667),
  lifting hooks dideliems. El.: „+1,5m ~230V El. Output", trafo viduje (MENY 991) arba converter box (Hovenga 12 V).
**BK šviesdėžė** (H1220 / 1520 / 1830): Front - thermoformated plexi; Backside Al 1,5; Side Al 1,5; Aluminium hem 1,5
(„2mm aliumas lankelis ant stiklo", „1.5mm aliumas lankelis po stiklu" - plexi kraštas suspaudžiamas tarp dviejų lankelių);
gylis 35 + 80; RAL 9006; LED 5100K (imagon) / 6500K; trafo ir 5 m 230 V kabelis viduje, „no exit holes".
Formuoto lakšto kraštas ~25-30, iškilimas ~15-20, kontūro R16 / R20.

## Failai
- Aplankai: `ALFA_thermoformated/` (+ `3d forma/*.obj`, `info/`), `BK_termoform/` (H-aukščio PDF rinkinys),
  `imagon/BURGER KING/...` (`thermoform.stl`, `BK 1220.stl`), `Brandfactory/MENY/ETALONAI/MENY_L____/<2m|3m|4m> 3d forma/`
  (`*.stl`, `1 dalis.dxf`, `pastorinimas.dxf`, PDF), `AlfaNeon/VOLVO/.../Pagalbiniai_failai/TERMOFORMAVIMAS/3D_VOLVO <7.5m|9.3m> pilonui/`
  (`V/O/L_*.stl`), `.../sukelti frezavimui/<projektas>/forma termoformavimui/` (`.stl` + `VOL_termoformos_pjovimui.cdr`).
- Klientų failai: `vakuumformet` / `vacuum formed` / `Vakuumformad.DXF` (DSV) - info aplanke.
- Užsakymuose atskiras `..._TERMOFORMA.cdr/.pdf` arba aplankas `termoformavimas/`, `FORMA/` (`ALT6967_MENY_L950_forma.stl`).

## Etalonai
- `Brandfactory/MENY/MENY - Logo Gen. 3 type 950 - Inside the store - Profile 1+10 vacuum formed/ALT6967_03.12_...pdf` (konstrukcija + forma)
- `BK_termoform/H1220_Burger King thermoformed tool for 1220mm.pdf` ir `Brandfactory/Burger King/BK-Borås.../termoformavimas/BK_Termoformavimas_20240828.pdf`
- `AlfaNeon/VOLVO/VOLVO_darbiniai failai/Pagalbiniai_failai/TERMOFORMAVIMAS/VOLVO_termoformavimas.pdf`
- `ALFA_thermoformated/Drawing_Maten_Alfa Romeo milano service logo.pdf` (spauda + formavimas)
- `Brandfactory/MENY/ETALONAI/MENY_L____/3m 3d forma/3.pdf` (dalijama forma)

## Neišspręsta - klausti Ryčio, kai klausimas iškyla darant projektą (ne iš anksto)
1. Formos offset'as: taisyklė „- medžiagos storis" (3 mm -> -3) teisinga? Kodėl Volvo forma -6 mm?
2. Kas termoformuoja (savo mašina ar subrangovas) ir koks max lakšto / formos dydis (dėl dalijimo 3 m+ logotipams)?
3. Volvo raidžių priekių medžiaga ir storis (lapuose nenurodyta)?
4. Ar MENY dangtis visada PLEXIGLAS GS Rot 3H25 (ABS RAL 3020 - tik Konnerud išimtis)?
5. Ar formos lape privaloma rodyti nuolydį / R (4°, R3, R6) - ar tai Jūsų standartas visoms formoms?
