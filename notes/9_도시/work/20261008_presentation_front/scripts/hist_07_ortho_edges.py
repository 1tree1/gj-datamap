import sys
sys.path.insert(0, "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/scripts")
from histlib import *
for k in ["o2025", "o2021", "o2015"]:
    a = load_full(k)
    print(k, a.shape)
    for nm, sl in [("top", a[:30]), ("bottom", a[-30:]), ("left", a[:, :30]), ("right", a[:, -30:])]:
        print("  ", nm, "mean", sl.reshape(-1, 3).mean(0).round(1), "min", sl.min(), "frac zero", float((sl.sum(-1) == 0).mean()), "frac 255", float((sl.min(-1) == 255).mean()))
    # 완전 검정/흰 행·열 길이
    zr = np.where((a.sum(-1) == 0).mean(1) > 0.99)[0]; zc = np.where((a.sum(-1) == 0).mean(0) > 0.99)[0]
    print("  black rows", zr[:5], zr[-5:], len(zr), "cols", zc[:5], zc[-5:], len(zc))
