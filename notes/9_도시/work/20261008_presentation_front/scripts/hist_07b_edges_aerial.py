import sys
sys.path.insert(0, "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/scripts")
from histlib import *
for k in ["a2024", "a2025_62", "a2025_64", "a2025_65"]:
    a = load_full(k)
    h, w = a.shape[:2]
    print(k, a.shape)
    z = (a.sum(-1) == 0)
    print("   frac black total", z.mean())
    rows = z.mean(1); cols = z.mean(0)
    print("   rows >50% black: first", np.where(rows > 0.5)[0][:3], "last", np.where(rows > 0.5)[0][-3:], " count", (rows > 0.5).sum())
    print("   cols >50% black: first", np.where(cols > 0.5)[0][:3], "last", np.where(cols > 0.5)[0][-3:], " count", (cols > 0.5).sum())
    # 모서리 검은 쐐기: 각 모서리 100x100 평균
    for nm, sl in [("TL", z[:200, :200]), ("TR", z[:200, -200:]), ("BL", z[-200:, :200]), ("BR", z[-200:, -200:])]:
        print("   corner", nm, round(float(sl.mean()), 3))
    # 8 방향 가장자리 20px 띠의 검은 비율
    for nm, sl in [("top", z[:20]), ("bot", z[-20:]), ("left", z[:, :20]), ("right", z[:, -20:])]:
        print("   edge", nm, round(float(sl.mean()), 3))
