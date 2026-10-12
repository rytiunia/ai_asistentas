#!/usr/bin/env python3
"""6 m strypų taisyklės bandymas (v73): 2 bėgeliai po 3025 mm (rėmas 6050 - netelpa į vieną 6 m strypą).
Kuria kliento PDF 1:1 (pt = mm): raidės H I I I H (juoda), bėgeliai pilki 30 mm.
python3 make_test.py  ->  strypai_6050.pdf ; tada:
python3 ../../braizyti_begeliai.py spec_6050.json out_6050.pdf"""
import pymupdf as fitz

W, H = 3100, 460
doc = fitz.open(); page = doc.new_page(width=W, height=H)
Y0 = 30                                            # raidžių apačia (pt, y žemyn)
def P(pts):                                        # mm (y aukštyn) -> pt
    return [fitz.Point(x, H - Y0 - y) for x, y in pts]
def h_letter(x0):                                  # H: 300 x 400, stiebai 60, skersinis 60
    pts = [(0, 0), (60, 0), (60, 170), (240, 170), (240, 0), (300, 0), (300, 400), (240, 400), (240, 230), (60, 230), (60, 400), (0, 400)]
    return [(x0 + x, y) for x, y in pts]
def shape(pts=None, rect=None, fill=(0, 0, 0)):   # kiekviena forma - atskiras kelias (kaip Illustrator / Corel)
    sh = page.new_shape()
    if pts: sh.draw_polyline(P(pts + [pts[0]]))
    else: sh.draw_rect(rect)
    sh.finish(color=None, fill=fill, closePath=True); sh.commit()
for x0 in (0, 2745):
    shape(h_letter(x0))
for x0 in (700, 1500, 2300):                       # I: 80 x 400
    shape([(x0, 0), (x0 + 80, 0), (x0 + 80, 400), (x0, 400)])
for y in (60, 310):                                # bėgeliai 3025 mm: x 10..3035 (pilki 0.53)
    shape(rect=fitz.Rect(10, H - Y0 - y - 30, 3035, H - Y0 - y), fill=(0.53, 0.53, 0.53))
doc.save("strypai_6050.pdf")
print("strypai_6050.pdf")
