# -*- coding: utf-8 -*-
"""등록 검증: 임의 사진의 저장 변환으로 지정 구역(5187)을 렌더링 -> [참조 | 대상 | 합성] 저장.
python hist_20_check_blend.py KEY REFKEY x0 y0 x1 y1 res OUT [mode gray|color]
KEY, REFKEY: 저장된 변환 키 (예: a1982, a2009, o2025)"""
import sys
sys.path.insert(0, "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/scripts")
from histlib import *
_cache = {}
def render_region(key, x0, y0, x1, y1, res, valid=None, gray=True):
    H, info = load_transform(key)
    gsd = float(np.sqrt(abs(np.linalg.det(H[:2, :2]))))
    if key not in _cache:
        _cache[key] = load_full(key, gray=gray)
    a = _cache[key]
    f = max(1, int(np.floor(res / gsd * 0.999)))
    src = prescale(a, f)
    w = int(round((x1 - x0) / res)); h = int(round((y1 - y0) / res))
    Hg = grid_H(x0, y1, res)
    out = warp_to_grid(src, H @ prescale_matrix(f), Hg, (w, h), interp=cv2.INTER_CUBIC)
    one = np.zeros(src.shape[:2], np.uint8)
    if valid is None:
        one[:] = 255
    else:
        cv2.fillPoly(one, [np.round((np.array(valid) - (f - 1) / 2.0) / f).astype(np.int32)], 255)
    m = warp_to_grid(one, H @ prescale_matrix(f), Hg, (w, h), interp=cv2.INTER_NEAREST) > 127
    return out, m
if __name__ == "__main__":
    key, rkey = sys.argv[1], sys.argv[2]
    x0, y0, x1, y1, res = [float(v) for v in sys.argv[3:8]]
    outn = sys.argv[8]
    vps = json.load(open(SCR + "valid_polys.json"))
    a, ma = render_region(key, x0, y0, x1, y1, res, valid=vps.get(key))
    b, mb = render_region(rkey, x0, y0, x1, y1, res, valid=vps.get(rkey))
    cl = cv2.createCLAHE(2.0, (8, 8))
    a2 = cl.apply(a); b2 = cl.apply(b)
    comp = np.dstack([b2, a2, a2])
    trip = np.concatenate([np.dstack([b2] * 3), np.dstack([a2] * 3), comp], axis=1)
    Image.fromarray(trip).save(SCR + f"prev/{outn}.png")
    print(trip.shape, "valid frac", ma.mean(), mb.mean())
