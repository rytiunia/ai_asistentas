# Plėvelės sunaudojimo testas (v123, Rytis 2026-10-12) - OKQ8 „Alltid öppet" (lapas 2 grafika)

Failas `alltid_oppet_2344x1936.pdf` - visa grafika VIENAS compound path (1 pt = 1 pt, grafika 2344 x 1936 mm).
```
python3 ../../plevele.py alltid_oppet_2344x1936.pdf --film "ORACAL 551 101 white" --pdf w.pdf --dxf w.dxf
#  -> 1320 mm: 4 dalys (užrašas | automobilis | dušas | dušas), 1320 mm x 2.81 m = 3.71 m²
python3 ../../plevele.py alltid_oppet_2344x1936.pdf --film "Oracal 641 070 black" --pdf b.pdf
#  -> 1190 mm: 4 dalys (užrašas | automobilis | dušas | dušas), 1190 mm x 2.81 m = 3.35 m²
```
Laukiama: užrašas „Alltid öppet" (su ö taškais) - VISADA viena dalis; rato centrai - su automobiliu; dušo taškai - ne
automobilio „diakritikai"; skaidoma tik kai netelpa į rulono plotį.

Dėliojimo principą Rytis patvirtino (1190 rezultatas, 2026-10-12): netelpa -> visi bendri objektai, kompaktiškai.
