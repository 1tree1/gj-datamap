"""p.6 소제목 'H'(굵게)와 본문 'O' 의 대문자 높이를 비교해 소제목 크기를 정한다(본문 영문 ≈ 9.7pt 기준)."""
import numpy as np, pymupdf
PDF = r"C:\Users\OFFICE\Desktop\9_도시\2_Report_HR_통영조선소.pdf"
z = 600 / 72.0
doc = pymupdf.open(PDF); pg = doc[5]
pix = pg.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=pymupdf.Rect(56, 126, 150, 165), alpha=False)
a = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3).min(axis=2)
ink = a < 150
rows = np.where(ink.any(axis=1))[0]
# 줄 띠 나누기
bands = []; s = rows[0]; p = rows[0]
for r in rows[1:]:
    if r - p > 3: bands.append((s, p)); s = r
    p = r
bands.append((s, p)); print("띠(px)", bands, "높이(pt)", [(b - a_ + 1) / z for a_, b in bands])
# 첫 글자 열 범위(왼쪽 첫 글자)로 대문자 높이
for (r0, r1), nm in zip(bands[:2], ("소제목 H", "본문 O")):
    sub = ink[r0:r1 + 1, :]
    cols = np.where(sub.any(axis=0))[0]
    # 첫 글자: 처음 연속 열 구간
    c0 = cols[0]; c1 = c0
    for c in cols[1:]:
        if c - c1 > 1: break
        c1 = c
    g = sub[:, c0:c1 + 1]; rr = np.where(g.any(axis=1))[0]
    print(nm, "첫 글자 열", c0, c1, "높이 %d px = %.2f pt, 폭 %.2f pt" % (rr.max() - rr.min() + 1, (rr.max() - rr.min() + 1) / z, (c1 - c0 + 1) / z))
