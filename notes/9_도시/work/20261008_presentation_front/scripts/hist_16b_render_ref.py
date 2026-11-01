import sys
sys.path.insert(0, "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/scripts")
from histlib import *
key = sys.argv[1]; name = sys.argv[2]
vp = json.load(open(SCR + "valid_polys.json")).get(key)
x0, y1, res = 216000.0, 364200.0, 2.0
w, h = int(7500 / res), int(7200 / res)
out, mask, Hg = render_ref_from_photo(key, x0, y1, w, h, res, valid=vp, name=name)
print(key, out.shape, "coverage of grid", mask.mean())
Image.fromarray(out).save(SCR + f"prev/ref_{name}.png")
