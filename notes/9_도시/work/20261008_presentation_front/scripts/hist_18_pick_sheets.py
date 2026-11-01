import sys
sys.path.insert(0, "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/scripts")
from histlib import *
# 참조: 2009 (4 m/px 로 줄여 사용)
ref = np.load(SCR + "ref_p2009_2m.npy"); rinfo = json.load(open(SCR + "ref_p2009_2m.json"))
Hg = np.array(rinfo["H"])
im, tr = geo_grid_preview(ref, Hg, 217000, 222600, 358200, 363000, step_m=500, scale=0.5, label_scale=0.5)
cv2.imwrite(SCR + "prev/pick_ref2009.png", im)
print(im.shape, tr)
# 1982: 픽셀 격자
key = "a1982"; f = 6
a = load_full(key, gray=True)
ds = cv2.resize(a, (a.shape[1] // f, a.shape[0] // f), interpolation=cv2.INTER_AREA)
ds = cv2.createCLAHE(2.0, (8, 8)).apply(ds)
g = draw_grid_px(ds, 200, label_scale=0.5, origin=(0, 0), val_scale=1)
cv2.imwrite(SCR + "prev/pick_1982.png", g)
print(g.shape)
