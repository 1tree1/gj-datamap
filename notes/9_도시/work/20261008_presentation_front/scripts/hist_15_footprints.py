import sys
sys.path.insert(0, "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/scripts")
from histlib import *
import glob
for f in sorted(glob.glob(WORK + "research/hist_transforms/*.json")):
    key = os.path.basename(f)[:-5]
    H, info = load_transform(key)
    w, h = info["size_px"]
    corners = np.array([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]], float)
    g = apply_H(H, corners) + np.array([CX, CY])
    ctr = apply_H(H, [[w / 2, h / 2]])[0] + np.array([CX, CY])
    print(key, "gsd", round(float(np.sqrt(abs(np.linalg.det(H[:2, :2])))), 3), "center", ctr.round(0), "x", g[:, 0].min().round(0), g[:, 0].max().round(0), "y", g[:, 1].min().round(0), g[:, 1].max().round(0), " rms", info.get("rms_m"))
