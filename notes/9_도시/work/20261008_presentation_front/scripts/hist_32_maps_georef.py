import sys
sys.path.insert(0, "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/scripts")
from histlib import *
fr = json.load(open(SCR + "frames_m1969_m1972_m1998.json"))
box25 = (129 + 7.5 / 60, 129 + 15 / 60, 35 + 45 / 60, 35 + 52.5 / 60)
box50 = (129.0, 129.25, 35.75, 36.0)
for key, box in [("m1969", box25), ("m1972", box25), ("m1998", box50)]:
    H, rms, r = georef_from_frame(key, fr[key], box, "EPSG:4162", "affine")
    print(key, "affine RMS (m) of 4 corners:", round(rms, 2), "px size", np.hypot(H[0, 0], H[1, 0]).round(3), np.hypot(H[0, 1], H[1, 1]).round(3), "rot deg", np.degrees(np.arctan2(H[1, 0], H[0, 0])).round(3))
