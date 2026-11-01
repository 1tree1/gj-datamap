"""PDF 쪽 썸네일 컨택트 시트. 사용: thumbs.py <pdf> <out_prefix> <쪽,쪽,...> [cols] [thumb_w]"""
import sys, os
import pymupdf
from PIL import Image, ImageDraw, ImageFont
pdf, prefix = sys.argv[1], sys.argv[2]
pages = [int(x) for x in sys.argv[3].split(",")]
cols = int(sys.argv[4]) if len(sys.argv) > 4 else 4
tw = int(sys.argv[5]) if len(sys.argv) > 5 else 520
doc = pymupdf.open(pdf)
ims = []
for p in pages:
    pg = doc[p - 1]
    r = pg.rect; s = tw / r.width
    pix = pg.get_pixmap(matrix=pymupdf.Matrix(s, s), alpha=False)
    im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    d = ImageDraw.Draw(im); d.rectangle([0, 0, 60, 22], fill=(255, 255, 0)); d.text((4, 4), "p%d" % p, fill=(0, 0, 0))
    ims.append(im)
th = max(i.height for i in ims)
rows = (len(ims) + cols - 1) // cols
sheet = Image.new("RGB", (cols * tw, rows * th), "white")
for k, im in enumerate(ims): sheet.paste(im, ((k % cols) * tw, (k // cols) * th))
out = prefix + ".png"; sheet.save(out); print(out, sheet.size)
