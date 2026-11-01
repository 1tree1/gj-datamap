# -*- coding: utf-8 -*-
import pymupdf, os
BASE = "C:/Users/OFFICE/Desktop/9_도시/대지/과거사진/경주 위성지도/"
for name in ["위성지도.pdf", "종이지도.pdf"]:
    d = pymupdf.open(BASE + name)
    print(name, "pages", d.page_count)
    for i in range(min(d.page_count, 40)):
        p = d[i]
        imgs = p.get_images(full=True)
        txt = p.get_text()[:120].replace("\n", " | ")
        print("  p", i + 1, "size", [round(v) for v in p.rect[2:]], "images", [(im[2], im[3]) for im in imgs][:4], "text:", txt)
