"""PDF 쪽의 이미지 위치(bbox, pt)와 크기 목록. 사용: list_images.py <pdf> <쪽,쪽,...>"""
import sys
import pymupdf
pdf = sys.argv[1]; pages = [int(x) for x in sys.argv[2].split(",")]
doc = pymupdf.open(pdf)
for p in pages:
    pg = doc[p - 1]; r = pg.rect
    print("== p%d  page %.0fx%.0f pt" % (p, r.width, r.height))
    for i, im in enumerate(pg.get_image_info(xrefs=True)):
        b = im["bbox"]
        print("  [%d] xref=%s bbox=(%.0f,%.0f,%.0f,%.0f) size=%.0fx%.0f pt  px=%sx%s" % (i, im.get("xref"), b[0], b[1], b[2], b[3], b[2] - b[0], b[3] - b[1], im.get("width"), im.get("height")))
