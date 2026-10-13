import json
SC = 40 * 25.4 / 72
def P(pts, o): return [[round((x - o[0]) * SC, 1), round((y - o[1]) * SC, 1)] for x, y in pts]
def R(x0, y0, x1, y1): return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
def rail(pts, o, kind): return {"kind": kind, "poly": P(pts, o)}
GREEN, BLACK = "#A6CE39", "#231F20"
ORG = __import__("sys").argv[2]
base = {"scale": 40, "qty": "3 pcs.", "order_no": "ALT0000_10.13_RS", "rev": "A", "date": "2026-10-13",
        "client": "BrandFactory", "drawing_no": "Order 226023 KIWI 640 BYGNES", "client_pdf": __import__("sys").argv[1],
        "depth_mm": 100, "front": "3mm+foil", "export_1to1": False, "trafo_box": False, "client_frame": True,
        "frame_round_mm": 0, "rail": {"size": "40x20x2", "depth": 20, "ral": "7024", "type": "square"},
        "ears": {"hole_d": 8, "enabled": False}, "fit_plate_size": 40, "led_label_gap_pt": 61,
        "section_labels": {"1": "6", "2": "7", "3": "5", "4": "9", "5": "3", "A": "14"},
        "bom_cols": [["POS", 20], ["Detail name", 0.22], ["Materials", 0.38], ["Qty", 0.09], ["Mat. qn.", 0.07], ["Notes", None]]}
# ------------------------------------------------ 1 lapas: KIWI minipris 3362 (originalas: ALT8858 Sheet 1)
oK, oM = (251.627, 354.997), (422.876, 351.543)
earsK = [(274.0, 358.6), (342.2, 358.6), (371.1, 358.6), (276.1, 419.5), (326.6, 419.5), (386.2, 419.5)]
earsM = [(419.3, 364.2), (480.4, 364.2), (419.3, 377.4), (480.4, 377.4), (419.3, 401.7), (463.6, 401.7), (419.3, 413.8), (463.6, 413.8)]
fp = lambda e, o: [[round((x - o[0]) * SC, 1), round((y - o[1]) * SC, 1)] for x, y in e]
O1 = (251.627, 351.543)
cm = lambda x, y: [round((x - O1[0]) * SC), round((y - O1[1]) * SC)]
s1 = dict(base, merge_rows=True, led_fragment={"src": ORG, "pno": 0, "clip": [78, 318, 580, 572], "note": "as original drawing (ALT8858)"}, callouts={"front": [cm(300, 392) + [1, -30, 40], cm(445, 372) + [2, 30, -34],
                                                    cm(372.5, 360) + [4, 26, -36], cm(418.7, 400) + [15, 24, 44]]}, title="KIWI minipris 3362", file_code="KIWI_226023_01_logo3362", sheet="1 / 3", crop_pt=[245, 340, 500, 432],
          ignore_fills=[[0.66, 0.81, 0.27], [0.35, 0.35, 0.05]],
          decals=[{"client_fill": [0.66, 0.81, 0.27], "hex": GREEN, "group": "KIWI"},
                  {"client_fill": [0.35, 0.35, 0.05], "hex": BLACK, "group": "minipris"}],
          joints=[{"x_pt": 418.7, "label": "DIVIDED"}],
          cable_exits=[{"pt": [405, 358], "voltage": "230V", "label": "~3 m"}, {"pt": [432, 358], "voltage": "230V", "label": "~3 m"},
                       {"pt": [432, 397], "voltage": "230V", "label": "~3 m"}],
          groups=[
              {"name": "KIWI", "profile": "6", "on_plate": False, "return_ral": "9010", "face_hex": BLACK,
               "client_fill": [0.85, 0.1, 0.1], "frame": "verticals", "fit_plates": fp(earsK, oK),
               "rails": [rail(R(260.0, 361.4, 260.0 + 3219 / SC, 364.2), oK, "h"), rail(R(260.0, 416.7, 260.0 + 3098 / SC, 419.5), oK, "h"),
                         rail(R(260.0, 364.2, 262.8, 364.2 + 740 / SC), oK, "v"), rail(R(335.0, 364.2, 337.8, 364.2 + 740 / SC), oK, "v"),
                         rail(R(402.3, 364.2, 405.2, 364.2 + 740 / SC), oK, "v")]},
              {"name": "minipris", "profile": "6", "on_plate": False, "return_ral": "9010", "face_hex": "#FFFFFF",
               "client_fill": [0.22, 0.2, 0.21], "frame": "verticals", "fit_plates": fp(earsM, oM),
               "rails": [rail(R(405.2, 380.2, 405.2 + 1170 / SC, 383.0), oM, "h"), rail(R(405.2, 398.9, 405.2 + 1038 / SC, 401.7), oM, "h"),
                         rail(R(424.8, 364.2, 427.6, 380.2), oM, "v"), rail(R(485.3, 364.2, 488.1, 380.2), oM, "v"),
                         rail(R(424.8, 401.7, 427.6, 416.7), oM, "v"), rail(R(458.9, 401.7, 461.8, 416.7), oM, "v"),
                         rail(R(455.5, 352.2, 458.3, 361.4), oM, "v"), rail(R(485.3, 352.2, 488.1, 361.4), oM, "v"),
                         rail(R(458.9, 389.7, 461.8, 398.9), oM, "v")]}],
          main_data=[["Quantity", "3 pcs."], ["Overall size", "3362 x 1095"], ["Frame", "Ral 7024, divided"],
                     ["Sides", "RAL 9010"], ["Front", "3mm stiklas / 8mm stiklas"],
                     ["Vinyl", "Mactac 9849-55, Oracal 641-070"], ["Fitting plates", "14 pcs., 40 x 75, Ø 8mm"],
                     ["Cable", "Laido skylė turi būti virš rėmo"], ["Wire", "230V (black): 9 m"],
                     ["Weld. template", "3400 x 1200"], ["Perimeter", "25 m"], ["Weight (calc.)", "{WEIGHT}"]],
          bom_title="MATERIALS TO MAKE ONE UNIT",
          bom=[[1, "Vinyl", "MACTAC 9849-55 (kiwi green)", "2.4", "b/m", GREEN],
               [2, "Vinyl", "Oracal 641-070", "3.5", "b/m", BLACK],
               [3, "Frame", "Al. square prof. 40x20x2,  AW-6060/6063 T6", "12.5", "b/m", ""],
               [4, "Mounting hole", "Al. sheet t=3mm,  AW-1050A H24", "0.1", "m2", ""],
               [5, "Back", "Al. sheet t=1.5mm,  AW-1050A H24", "3.4", "m2", "vidus baltas, šl."],
               [6, "Front", "Plexiglas WH02SC, t=3mm", "3.4", "m2", ""],
               [7, "Sides", "Al. stripe t=1mm, h=100mm AW-1050A H24", "25", "b/m", "vidus baltas, šl."],
               [8, "Frame welding template", "Šabloninis popierius", "3.4", "b/m", ""],
               [9, "LED", "Module P 130 Lens (1W) green", "85", "vnt.", "#009639"],
               [10, "LED", "Module P 65 Lens (1W) white", "63", "vnt.", ""],
               [11, "Transformator", "KPS-V12 - 100 W, KPS-V12 - 20 W", "3", "vnt.", ""],
               [12, "El wire", "230 V", "9", "m", BLACK],
               [14, "PVC stripe", "", "25", "b/m", ""],
               [15, "Frame connection", "Al. square prof. 15x15x2,  AW-6060/6063 T6", "0,5", "b/m", ""]])
json.dump(s1, open("spec1.json", "w"), ensure_ascii=False, indent=1)
# ------------------------------------------------ 2 lapas: 7-23 2037 (originalas: ALT8858 Sheet 2)
o7 = (274.669, 503.107)
s2 = dict(base, led_fragment={"src": ORG, "pno": 1, "clip": [66, 428, 664, 768], "note": "as original drawing (ALT8858)"}, section_labels={"1": "6", "2": "7", "3": "5", "4": "9", "5": "3", "A": "12"}, title="7-23  L 2037", file_code="KIWI_226023_02_723", sheet="2 / 3", crop_pt=[262, 495, 430, 562],
          ignore_fills=[[0.66, 0.81, 0.27]], decals=[{"client_fill": [0.66, 0.81, 0.27], "hex": GREEN, "group": "7-23"}],
          cable_exits=[{"pt": [366, 506], "voltage": "230V", "label": "~3 m"}],
          groups=[{"name": "7-23", "profile": "6", "on_plate": False, "return_ral": "9010", "face_hex": BLACK,
                   "client_fill": [0.1, 0.1, 0.85], "frame": "verticals",
                   "fit_plates": fp([(314.31, 511.42), (386.22, 511.42), (380.19, 542.6), (296.66, 542.6)], o7),
                   "rails": [rail(R(285.37, 508.59, 409.39, 511.42), o7, "h"), rail(R(285.37, 545.44, 409.39, 548.27), o7, "h"),
                             dict(rail([(297.39, 530.29), (368.88, 530.29), (367.25, 533.12), (295.75, 533.12)], o7, "h"), len=1032),
                             rail([(305.01, 511.42), (308.28, 511.42), (288.64, 545.44), (285.37, 545.44)], o7, "d"),
                             rail([(379.77, 511.42), (383.05, 511.42), (363.41, 545.44), (360.13, 545.44)], o7, "d"),
                             rail(R(406.55, 511.42, 409.39, 545.44), o7, "v")]}],
          main_data=[["Quantity", "3 pcs."], ["Overall size", "2037 x 709"], ["Frame", "Ral 7024"], ["Sides", "RAL 9010"],
                     ["Fitting plates", "4 pcs., 40 x 75, Ø 8mm"], ["Wire", "230V (BLACK): 3m"],
                     ["Perimeter", "9,5 m"], ["Weight (calc.)", "{WEIGHT}"]],
          bom_title="MEDŽIAGŲ ŽINIARAŠTIS VIENAM GAMINIUI",
          bom_cols=[["POS", 20], ["Detalės pavadinimas", 0.2], ["Medžiaga", 0.38], ["Kiekis", 0.09], ["Mat. vnt.", 0.08], ["Pastabos", None]],
          bom=[[1, "Plėvelė", "MACTAC 9849-55 (kiwi žalia)", "2.1", "b/m", GREEN],
               [2, "Plėvelė", "Oracal 641-070", "2.1", "b/m", BLACK],
               [3, "Rėmas", "Al. stačiakampis vamzdis 40x20x2mm", "6.5", "b/m", ""],
               [4, "Tvirtinimo auselė", "Al. Lakštas t=3mm, AW-1050A H24", "0.1", "m2", ""],
               [5, "Dugnas", "Al. lakštas t=1.5mm, AW-1050A H24", "1.2", "m2", "vidus baltas, šl."],
               [6, "Priekis", "Plexiglas WH02SC, t=3mm", "1.2", "m2", ""],
               [7, "Bortai", "Al. juosta t=1mm, h=100mm AW-1050A H24", "9.2", "b/m", "vidus baltas, šl."],
               [8, "Šablonas virinimui", "Šabloninis popierius", "1.9", "b/m", ""],
               [9, "LED", "P130 lens (1W) green", "26", "vnt.", "#009639"],
               [10, "Transformatorius", "KPS-V12-40W", "1", "vnt.", ""],
               [11, "Laidas", "230V", "3", "m", ""],
               [12, "PVC juosta", "", "9,2", "b/m", ""]])
json.dump(s2, open("spec2.json", "w"), ensure_ascii=False, indent=1)
