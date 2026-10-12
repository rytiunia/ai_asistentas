# Pilonai / totemai (nešviečiantys, folded skardos ant Alu rėmo) - v89, Rytis 2026-10-10 / 11

Pirmas atvejis: CEOS Groupe D059422 „Thales Campus Velizy" - įėjimo pilonas 1050 x 2530 (dvipusis) ir pastatų pilonai
600 x 2130 x4 (vienpusiai). Kodas: `scripts/projektai/thales_d059422/thales_pylons.py` (parametrinis, klasė `Pyl`),
README ten. Naujam pilonui - kopijuoti, keisti `Pyl(...)` parametrus, kliento grafikos `clip` ir lapų sąrašą.

**Šviečiantys / dideli (> 3 m) pilonai** - etalonas `references/etalonas_pilonas_prisma_alt8826.md` (Prisma Skejby ALT8826:
8,8 m plieno rėmas + 14 šviesdėžių B-0313; 5 m Alu rėmas + plexi įdėklai su laipteliu). Žemiau - nešviečiantys folded.

## Konstrukcija (sluoksniai iš vidaus į išorę)
1. **Rėmas** Alu 60x60x3 (6082-T6), suvirintas: 2 vertikalės + viršutinis skersinis + apatinis (arba pagrindo balkis)
   + **TIK 1 tarpinis skersinis per centrą** (Rytis 2026-10-11 - 2 tarpinių nereikia).
2. **Laisvumai:** rėmo plotis / aukštis = skardos matmuo - 6 (po 3 mm: 2 mm skarda + 1 mm laisvumas).
3. **Mėlyna skarda** (lovelė) 2 mm, RAL pagal užsakymą: priekis + šonai ir viršus lankstomi į gylį; korpusas = 2 lovelės
   (priekinė + galinė), sandūra šono viduryje. Lovelės gylis = (rėmo / balkio gylis + 2 x 3 laisvumas) / 2
   (rėmas 60 -> 2 x 40 = 80; pagrindo balkis 80 -> 2 x 43 = 86).
   - Kojos ant flanšų: apačioje kraštinė IŠPJAUNAMA ties kojomis (65 nuo krašto), tarp kojų tik 20 mm standumo briauna.
   - Pagrindo balkis: apačia be lenkimo, skarda baigiasi 5 mm virš pagrindo, balkį paslepia.
4. **L 25x25x2** (balta skarda 30 gylio -> L 25) kniedijamas prie mėlynos skardos: šonuose ir apačioje (4 mm nuo krašto),
   viršuje - L stovi ant mėlyno viršaus, stati kojelė prie baltos galinės plokštumos.
5. **Balta skarda** 2 mm (RAL 9016): priekis, šonai + apačia 30, VIRŠUS - apverstas U: atlankas 30 + 40 (= 30 + lovelės
   gylis) iki pilono vidurio + GALINĖ PLOKŠTUMA 30 žemyn; šone viršuje AUSĖ (uždaro šoną virš mėlynos). Dvipusiame -
   priekinė ir galinė balta susitinka viduryje galinėmis plokštumomis.
6. **Tvirtinimai:** balta -> L įleidžiamais (csk) varžtais PAGAL PERIMETRĄ (šonai, apačia, viršaus galinė plokštuma;
   17 nuo lenkimo, ~300); balta + mėlyna surenkamos į SEGMENTĄ, segmentas prie rėmo - csk varžtais TIK per mėlynos ŠONŲ
   atlankus (25 nuo lenkimo, ~400). Per viršų į skersinį - NE.
7. **Grafika:** spauda ant polimerinės plėvelės + matinis laminatas, apklijuojamas VISAS baltas priekis ir apipjaunama
   pagal skardos kraštus (full-face wrap). RAL spalvos - atkartojamos spaudoje, spalvų bandinys klientui.

## Pagrindas
- **Ant esamų inkarų (flanšai):** flanšas Alu 300 x 300 x **20**, privirintas prie kojos; skylės - pagal esamus inkarus
  -> KLAUSIMAS užsakovui (išdėstymas, Ø, sriegio ilgis); nuolydis - viena koja ilgesnė (kliento brėžinyje).
- **Paslėptas (mažesni pilonai):** apačioje balkis Alu **80x40x4** (6060-T66, standartinis, 6 m - Lemu, Schiek, ...),
  kojos privirintos ant jo; **4 skylės šachmatine tvarka**, varžtas PER ABI SIENELES, įvirinta **įvorė Ø30/Ø18 L40**
  (be įvorės 4 mm sienelė įsispaudžia - priveržimas ~25 kN + vėjas); **4 x M16 A4 cheminiai**, hef >= 125, C20/25 min.;
  skylės >= 95 nuo balkio galo (poveržlė / galvutė neremia kojos). Eiga: 1) rėmas ankeruojamas, 2) prisukami segmentai.
- Vėjas (EN 1991-1-4): vb,0 pagal šalį (FR zona 2 = 24 m/s), cf 2.3 (laisvai stovinti), gamma 1.5; 600 x 2130:
  MEd ~2.5 kNm. Petys = ankerių atstumas iki gniuždomo krašto - siauram pagrindui (80) ~55 mm -> ~22 kN / ankeriui.
  Plokštė, telpanti 80 mm korpuse, su ankeriais NEVEIKIA (petys per mažas) - sakyti tiesiai.

## Dokumentas KLIENTUI (Rytis 2026-10-11)
- Lapai: kiekvienam pilono tipui GA (vaizdas iš viršaus, priekis su kliento grafika, šonas su varžtais, rėmo vaizdas,
  3D) + pjūviai (A horizontalus 1:2, B viršus 1:2, C apačia, DETAIL H pagrindas, sprogdintas 3D). **Išklotinių NEDĖTI**
  (gamybai - atskirai).
- **3D klientui** - tik IŠORINIAI kūnai (`ext3d`) + kliento grafika ant priekio (`overlay_graphic`, ortografinė
  projekcija afininė). Vidinės detalės 3D vaizde sukelia neteisingą užstojimą. Sprogdintas vaizdas - detalės
  nesiliečia (`exploded3d`), baltos viršus su galine plokštuma ir ausėmis (turi tūrį).
- **Nuorodų balionai nesikerta:** `leaders(items, xc, side)` - balionai stulpelyje taikinių y eilės tvarka.
- **Nežinomi matmenys** - lape aiškus raudonas KLAUSIMŲ UŽSAKOVUI blokas (Q1, Q2 ...) + raudoni „?" vietose.
- **Kliento grafikoje balti `re` stačiakampiai = maskavimo kvadratai** - nepiešti (`client_paths` filtras).
- Stalinis PMMA planas: priekis pasviręs atgal ~10° (stabilumas + matomumas stovinčiam), pėda atgal 80, R10.
