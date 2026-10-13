# KIWI order 226023 KIWI 640 BYGNES (BrandFactory, 2026-10-13) - 3 lapai mūsų stiliumi

Originalas - pirmasis 226023 dokumentas (Tollnes 225948 / ALT8858 lapai): VISA informacija, lentelės ir aprašymai perkelti
iš jo (rėmo ilgiai 3219 / 3098 / 1170 / 1038 / 740, 1750 / 1032 / 1750, 14 / 4 ausėlės jų vietose, „Materials to make one unit“
ir „Medžiagų žiniaraštis vienam gaminiui“ - stulpeliai ir eilutės kaip originale, LED Installation, Parts List 1-7, užrašai
„Laido skylė turi būti virš rėmo“, „Connection point“, „Cover with adjustable position“ ...). Keičiamas tik lapo stilius.
1. `python3 mkclient.py client_clean.pdf` (kliento PDF p1 -> grupės, decal, pilki bėgeliai).
2. `python3 mkspec.py client_clean.pdf` -> spec1.json / spec2.json (`rails` + `fit_plates` iš originalo, `bom_cols`,
   `section_labels` - pjūvio numeriai pagal originalo BOM, `callouts`).
3. `python3 ../../braizyti_begeliai.py spec1.json s1.pdf`, `spec2.json s2.pdf`; `python3 led_sheets.py <ALT8858.pdf> .`
   (LED INSTALLATION lapai - originalo LED dėliojimo fragmentas + lentelė); `python3 lanterne.py s3.pdf <ALT8858.pdf>`
   (kolonai DETAIL A / B ir 3D - originalo fragmentas, Sheet 3 x 455-1142, y 38-768 pt).
   Tvarka: s1, s1led, s2, s2led, s3 (5 lapai).
4. Sujungti, `lapas_core.pdf_fix_fonts`, `Drawing_Order 226023 KIWI 640 BYGNES.pdf` užsakymo aplanke NAS.
