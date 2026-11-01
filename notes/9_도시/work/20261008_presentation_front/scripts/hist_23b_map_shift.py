import sys
sys.path.insert(0, "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/scripts")
from histlib import *
for key in ["m1976", "m1984"]:
    H, info = load_transform(key)
    H0, err = embedded_map_H(key)
    w, h = info["size_px"]
    pts = np.array([[w / 2, h / 2], [w * 0.2, h * 0.2], [w * 0.8, h * 0.2], [w * 0.2, h * 0.7], [w * 0.8, h * 0.7]], float)
    d = apply_H(H, pts) - apply_H(H0, pts)
    print(key, "shift (final - embedded+pyproj) at center:", d[0].round(1), " others:", d[1:].round(1).tolist())
    print("   rotation deg (final):", np.degrees(np.arctan2(H[1, 0], H[0, 0])), " embedded:", np.degrees(np.arctan2(H0[1, 0], H0[0, 0])), "px sizes", np.hypot(H[0, 0], H[1, 0]), np.hypot(H[0, 1], H[1, 1]))
