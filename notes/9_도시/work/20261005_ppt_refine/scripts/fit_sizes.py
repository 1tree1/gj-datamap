"""보고서 글자 크기를 '아는 문자열의 잉크 폭'으로 맞춰 본다(Arial). 사용: python fit_sizes.py"""
import numpy as np
import pymupdf
from PIL import Image, ImageFont
PDF = r"C:\Users\OFFICE\Desktop\9_도시\2_Report_HR_통영조선소.pdf"
DPI = 600; z = DPI / 72.0
doc = pymupdf.open(PDF)
AR = r"C:\Windows\Fonts\arial.ttf"; ARB = r"C:\Windows\Fonts\arialbd.ttf"

def ink_extent(pn, rect, thr=170, dark_bg=False):
    pg = doc[pn - 1]
    pix = pg.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=pymupdf.Rect(*rect), alpha=False)
    a = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3).astype(int)
    lum = a.min(axis=2) if not dark_bg else (255 - a.max(axis=2))
    ink = lum < thr
    cols = np.where(ink.any(axis=0))[0]; rows = np.where(ink.any(axis=1))[0]
    return (cols.min(), cols.max(), rows.min(), rows.max(), pix.width, pix.height)

def ink_width_px(font_path, text, size_pt):
    f = ImageFont.truetype(font_path, int(round(size_pt * z * 10)) )          # 10배 키워 소수 크기까지
    l, t, r, b = f.getbbox(text); return (r - l) / 10.0

def fit(font_path, text, meas_px):
    best = min(np.arange(5.0, 30.0, 0.05), key=lambda s: abs(ink_width_px(font_path, text, s) - meas_px)); return round(float(best), 2)

def report(label, pn, rect, text, font, dark_bg=False, thr=170):
    c0, c1, r0, r1, W, H = ink_extent(pn, rect, thr=thr, dark_bg=dark_bg)
    w = c1 - c0 + 1
    print("%-34s ink w=%4dpx (%.1fpt) h=%3dpx → 크기 추정 %.2f pt   [%s]" % (label, w, w / z, r1 - r0 + 1, fit(font, text, w), text))

# p.6: 소제목(굵게)·영문 본문 첫 줄 — 100dpi 좌표 → pt(×0.72)
report("p6 소제목 Holistic Planning", 6, (56, 125, 240, 150), "Holistic Planning", ARB)
report("p6 소제목 Connectivity", 6, (333, 125, 520, 150), "Connectivity", ARB)
report("p6 본문1줄 Our integrated…", 6, (56, 150, 304, 160), "Our integrated approach complements the anchor", AR)
# p.18 표: 영문 라벨
for lab, rect, txt in (("p18 표 Office / Commercial", (624, 79, 735, 93), "Office / Commercial"), ("p18 표 Cultural / Edu / Civic", (624, 112, 735, 126), "Cultural / Edu / Civic"),
                       ("p18 표머리 Facility Area(굵게)", (624, 66, 710, 80), "Facility Area")):
    try: report(lab, 18, rect, txt, ARB if "머리" in lab else AR)
    except Exception as e: print(lab, "fail", e)
