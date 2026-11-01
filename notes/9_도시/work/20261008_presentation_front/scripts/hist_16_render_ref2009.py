import sys
sys.path.insert(0, "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/scripts")
from histlib import *
vp = json.load(open(SCR + "valid_polys.json"))
# 2009 참조 격자: x 216000-223500, y 357000-364200, 2 m/px
x0, y1, res = 216000.0, 364200.0, 2.0
w, h = int(7500 / res), int(7200 / res)
out, mask, Hg = render_ref_from_photo("a2009", x0, y1, w, h, res, valid=vp["a2009"], name="p2009_2m")
print(out.shape, mask.mean())
Image.fromarray(out).save(SCR + "prev/ref_p2009_2m.png")
