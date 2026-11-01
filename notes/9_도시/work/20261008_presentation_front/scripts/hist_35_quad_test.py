import sys
sys.path.insert(0, "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/scripts")
from histlib import *
fr_prev = json.load(open(SCR + "frames_m1969_m1972_m1998.json"))
for key in sys.argv[1:]:
    a = load_full(key)
    q = content_quad(a, open_k=25, verbose=False)
    print(key, "quad:", None if q is None else q.round(1).tolist())
    if key in fr_prev:
        print("    prev fit:", np.array(fr_prev[key]).round(1).tolist())
