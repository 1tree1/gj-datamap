# -*- coding: utf-8 -*-
import pymupdf, os, io
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
BASE = "C:/Users/OFFICE/Desktop/9_도시/대지/과거사진/경주 위성지도/"
OUT = "C:/Users/OFFICE/AppData/Local/Temp/claude/C--Users-OFFICE-Desktop-9---/b98333f0-4ddf-4213-a0db-66cb837b3d35/scratchpad/prev/"
for name, pages, tag in [("위성지도.pdf", [1, 3, 4, 6], "sat"), ("종이지도.pdf", [6], "pap")]:
    d = pymupdf.open(BASE + name)
    for pg in pages:
        p = d[pg - 1]
        for im in p.get_images(full=True):
            xref = im[0]
            pix = pymupdf.Pixmap(d, xref)
            if pix.n - pix.alpha >= 4:
                pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
            mode = "RGB" if pix.n >= 3 else "L"
            img = Image.frombytes(mode, (pix.width, pix.height), pix.samples)
            s = max(img.size) / 2200
            img.resize((int(img.width / s), int(img.height / s)), Image.LANCZOS).save(OUT + f"{tag}_p{pg}.png")
            print(name, pg, img.size, mode)
