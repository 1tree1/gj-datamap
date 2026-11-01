# -*- coding: utf-8 -*-
"""확인용 나란히 시트: python hist_11_sheet.py OUT.png scale file1 file2 ..."""
import sys
sys.path.insert(0, "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/scripts")
from histlib import *
out = sys.argv[1]; sc = float(sys.argv[2]); files = sys.argv[3:]
ims = []
for f in files:
    im = Image.open(f if os.path.isabs(f) or ":" in f else HIST + f).convert("RGB")
    im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
    ims.append(im)
W = sum(i.width for i in ims) + 8 * (len(ims) - 1); H = max(i.height for i in ims)
sheet = Image.new("RGB", (W, H), (255, 255, 255))
x = 0
for im in ims:
    sheet.paste(im, (x, 0)); x += im.width + 8
sheet.save(SCR + "prev/" + out)
print(sheet.size)
