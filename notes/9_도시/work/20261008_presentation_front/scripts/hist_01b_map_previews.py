# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/scripts")
from histlib import *
for k in ["m1916", "m1916j", "m1918", "m1918gb", "m1956", "m1969", "m1972", "m1976", "m1984", "m1998", "m2005", "m2024"]:
    try:
        a = load_full(k)
    except Exception as e:
        print("fail", k, e); continue
    h, w = a.shape[:2]
    s = max(h, w) / 2400.0
    im = Image.fromarray(a)
    im = im.resize((int(w / s), int(h / s)), Image.LANCZOS)
    im.save(PREV + k + "_2400.png")
    print(k, (w, h), "->", im.size, "scale", round(s, 3))
