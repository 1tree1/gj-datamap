"""PDF 여러 쪽을 한 장의 접촉 시트로. 사용: pdf_sheet.py <pdf> <out.png> <쪽 목록 1,2,3> [cols=2] [쪽당 가로 px=820]"""
import sys
import pymupdf
from PIL import Image, ImageDraw, ImageFont
pdf, out = sys.argv[1], sys.argv[2]
nums = [int(x) for x in sys.argv[3].split(",")]
cols = int(sys.argv[4]) if len(sys.argv) > 4 else 2
W = int(sys.argv[5]) if len(sys.argv) > 5 else 820
doc = pymupdf.open(pdf)
tiles = []
for n in nums:
    pg = doc[n - 1]; z = W / pg.rect.width
    pix = pg.get_pixmap(matrix=pymupdf.Matrix(z, z), alpha=False)
    im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    d = ImageDraw.Draw(im); d.rectangle([0, 0, 64, 24], fill="#000000"); d.text((6, 4), "p.%d" % n, fill="#ffffff")
    tiles.append(im)
H = max(t.height for t in tiles)
rows = (len(tiles) + cols - 1) // cols
sheet = Image.new("RGB", (cols * W + (cols - 1) * 8, rows * H + (rows - 1) * 8), "#888888")
for i, t in enumerate(tiles): sheet.paste(t, ((i % cols) * (W + 8), (i // cols) * (H + 8)))
sheet.save(out); print(out, sheet.size)
