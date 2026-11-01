import sys
sys.path.insert(0, "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/scripts")
from histlib import *
for key in ["m1984", "m1976", "m1916", "m1956", "m1969", "m1972", "m1998", "m2005", "m2024", "m1918"]:
    try:
        a = load_full(key, gray=True)
    except Exception as e:
        print(key, "load fail", e); continue
    nl, (cp, rp) = detect_neatline(a, ds=4, verbose=False)
    print(key, a.shape[::-1], "neatline", nl)
