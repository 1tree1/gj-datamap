import sys
sys.path.insert(0, "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/scripts")
from histvec import *
V = get()
for k, g in V.items():
    print(k, len(g), g.total_bounds.round(1).tolist())
