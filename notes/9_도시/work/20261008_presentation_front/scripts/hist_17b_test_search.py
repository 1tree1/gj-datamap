# -*- coding: utf-8 -*-
"""coarse_search 검증: 2009 사진 vs 2025 정사영상 (정답: 회전 약 -4.1°, GSD 0.453)"""
import sys, time
sys.path.insert(0, "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/scripts")
from histlib import *
vp = json.load(open(SCR + "valid_polys.json"))["a2009"]
ref1, Hr1 = ref_ortho2025_gray(1.0)
down = 4
ref = cv2.resize(ref1, (ref1.shape[1] // down, ref1.shape[0] // down), interpolation=cv2.INTER_AREA)
Hg = Hr1 @ prescale_matrix(down)
rmask = np.ones(ref.shape, bool)
a = load_full("a2009", gray=True)
f = 9
ds = cv2.resize(a, (a.shape[1] // f, a.shape[0] // f), interpolation=cv2.INTER_AREA)
mk = np.zeros(ds.shape, np.uint8)
cv2.fillPoly(mk, [np.round((np.array(vp) - (f - 1) / 2.0) / f).astype(np.int32)], 255)
# 템플릿(2009 ds)이 참조(정사영상 4 m/px = 606×731)보다 크다 → 참조를 템플릿으로 쓰는 반대 방향 필요.
print(ds.shape, ref.shape)
