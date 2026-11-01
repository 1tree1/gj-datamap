import sys
sys.path.insert(0, "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/scripts")
from histlib import *
key = sys.argv[1]; f = int(sys.argv[2]); name = sys.argv[3]
crop = tuple(int(v) for v in sys.argv[4].split(",")) if len(sys.argv) > 4 else None
ref1, Hr1 = ref_ortho2025_gray(1.0)
a = load_full(key, gray=True)
H, info = load_transform(key)
ds = cv2.resize(a, (a.shape[1] // f, a.shape[0] // f), interpolation=cv2.INTER_AREA)
H_ds2geo = H @ prescale_matrix(f)
print(check_overlay(key, ref1, Hr1, ds, H_ds2geo, name, crop=crop, scale=0.6))
