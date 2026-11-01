import sys
sys.path.insert(0, "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/scripts")
from histlib import *
for key in ["m1969", "m1972", "m2005", "m1956", "m1998", "m2024", "m1918", "m1916j"]:
    g = load_full(key, gray=True)
    fr = auto_content_frame(g)
    print(key, g.shape[::-1], "auto content frame (x0,y0,x1,y1):", fr, "size", fr[2] - fr[0], fr[3] - fr[1])
