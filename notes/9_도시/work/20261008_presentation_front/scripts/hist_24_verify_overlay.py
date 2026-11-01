# -*- coding: utf-8 -*-
"""검증 이미지: 저장 변환으로 영상을 5187 틀에 렌더링하고 벡터 윤곽(도로 경계=주황, 철도=자홍, 건물=청록)을 얹어 저장.
python hist_24_verify_overlay.py KEY x0 y0 x1 y1 res OUT [layers: r,b,t] [color|gray]"""
import sys
sys.path.insert(0, "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/scripts")
from histlib import *
from histvec import get, geom_lines, to_px
V = get()
def render(key, x0, y0, x1, y1, res, color=True):
    H, info = load_transform(key)
    gsd = float(np.sqrt(abs(np.linalg.det(H[:2, :2]))))
    a = load_full(key, gray=not color)
    f = max(1, int(np.floor(res / gsd * 0.999)))
    src = prescale(a, f)
    w = int(round((x1 - x0) / res)); h = int(round((y1 - y0) / res))
    out = warp_to_grid(src, H @ prescale_matrix(f), grid_H(x0, y1, res), (w, h), interp=cv2.INTER_CUBIC)
    return out
def overlay(img, x0, y1, res, layers):
    im = img if img.ndim == 3 else np.stack([img] * 3, -1)
    im = np.ascontiguousarray(im.copy())
    cols = {"r": ("roadA", (255, 140, 0)), "b": ("bldg", (0, 220, 220)), "t": ("rail", (255, 0, 255))}
    for L in layers:
        nm, c = cols[L]
        for ln in geom_lines(V[nm]):
            p = to_px(ln, x0, y1, res)
            if p[:, 0].max() < 0 or p[:, 0].min() > im.shape[1] or p[:, 1].max() < 0 or p[:, 1].min() > im.shape[0]:
                continue
            cv2.polylines(im, [np.round(p * 16).astype(np.int32)], False, c, 1, cv2.LINE_AA, shift=4)
    return im
if __name__ == "__main__":
    key = sys.argv[1]
    x0, y0, x1, y1, res = [float(v) for v in sys.argv[2:7]]
    out = sys.argv[7]
    layers = sys.argv[8].split(",") if len(sys.argv) > 8 else ["r", "t"]
    color = (sys.argv[9] != "gray") if len(sys.argv) > 9 else True
    img = render(key, x0, y0, x1, y1, res, color)
    if img.ndim == 2:
        img = cv2.createCLAHE(2.0, (8, 8)).apply(img)
    im = overlay(img, x0, y1, res, layers)
    # 100 m 눈금
    for gx_ in range(int(np.ceil(x0 / 100) * 100), int(x1) + 1, 100):
        u = int((gx_ - x0) / res)
        cv2.line(im, (u, 0), (u, 10), (255, 0, 0), 1)
        cv2.putText(im, str(gx_ % 100000), (u + 2, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1, cv2.LINE_AA)
    for gy_ in range(int(np.ceil(y0 / 100) * 100), int(y1) + 1, 100):
        v = int((y1 - gy_) / res)
        cv2.line(im, (0, v), (10, v), (255, 0, 0), 1)
        cv2.putText(im, str(gy_ % 100000), (12, v + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1, cv2.LINE_AA)
    os.makedirs(HIST + "_check", exist_ok=True)
    Image.fromarray(im).save(out if (os.path.isabs(out) or ":" in out) else SCR + "prev/" + out)
    print(im.shape)
