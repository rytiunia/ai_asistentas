# LED dėliojimo testas (v329, Rytis 2026-10-17)

„tam tikrose situacijose LED nedėdavo, nors ten reikėjo, ir A raidėje vienoje kojelėje 3 LED, o kitoje jau 4, ir nėra
brūkšnelyje tarp kojelių" - senas numatytas `ilp` (aprėpties minimumas) buvo asimetriškas ir „taupė" trumpus brūkšnius.

- `raides_sans.pdf` (Liberation Sans Bold), `raides_serif.pdf` (Liberation Serif) - AHMWBRSEKX, A = 500 mm;
  `raides_723.pdf` - „7-23" palyginimui su Ryčio lapu `assets/led_pavyzdziai/ALT8873_..._RYCIO.jpg`.
- Sukurta: `python3 ../welcome_p1_test/make_client.py "AHMWBRSEKX" raides_sans.pdf A 500 <font.ttf> 1A1A1A`.
- Tikrina `scripts/test_led.py` (ir `regresija.py`): simetrija (sans A H M W X), A / H brūkšnys su LED, kiekviena raidės
  linija <= 0,75 p nuo LED (serifų atšakos ir laisvo galo zona netikrinamos), moduliai raidėje, >= 0,45 p vienas nuo kito.
- Lapas: `python3 ../../led_km.py spec_sans.json out.pdf`.
