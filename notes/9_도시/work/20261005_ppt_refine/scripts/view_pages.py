"""PDF 쪽(또는 쪽의 일부 영역)을 PNG 로 렌더. 사용: view_pages.py <pdf> <쪽> <out.png> [dpi] [x0,y0,x1,y1 (0~1 비율)]"""
import sys
import pymupdf
pdf, page, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
dpi = float(sys.argv[4]) if len(sys.argv) > 4 else 110
doc = pymupdf.open(pdf); pg = doc[page - 1]; r = pg.rect
clip = None
if len(sys.argv) > 5:
    a = [float(v) for v in sys.argv[5].split(",")]; clip = pymupdf.Rect(r.x0 + a[0] * r.width, r.y0 + a[1] * r.height, r.x0 + a[2] * r.width, r.y0 + a[3] * r.height)
z = dpi / 72.0
pix = pg.get_pixmap(matrix=pymupdf.Matrix(z, z), clip=clip, alpha=False); pix.save(out); print(out, pix.width, pix.height)
