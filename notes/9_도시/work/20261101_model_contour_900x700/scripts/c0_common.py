# 노면표시 작업 공통: 경로, 좌표 변환(EPSG:5187/5179 ↔ 모델 mm), 모자이크 화소 ↔ 모델
import json
import sys
from pathlib import Path

import numpy as np
from pyproj import Transformer

sys.stdout.reconfigure(encoding="utf-8")
W = Path(__file__).resolve().parents[1]
D = W / "data"
NG = D / "ngii_2025"
ARC = W.parents[1] / "archive" / "C_data" / "processed"
SCR = Path(r"C:\Users\OFFICE\AppData\Local\Temp\claude\C--Users-OFFICE--claude-spares-spare-o8WlFN\7cb8f9e5-ee1b-4ce3-84a0-6e9f9e66ec43\scratchpad")
MOS = SCR / "mosaic"
MM = 1000.0 / 1500.0                      # 실제 1 m → 모델 mm

_xf = json.load(open(D / "xf_5179.json"))
_s, _R, _t = _xf["s"], np.array(_xf["R"]), np.array(_xf["t"])
_T87_79 = Transformer.from_crs(5187, 5179, always_xy=True)
_T4326_79 = Transformer.from_crs(4326, 5179, always_xy=True)


def m_from_5179(xy):
    xy = np.atleast_2d(np.asarray(xy, float))
    return (_s * (_R @ xy.T)).T + _t


def m_from_5187(xy):
    xy = np.atleast_2d(np.asarray(xy, float))
    x, y = _T87_79.transform(xy[:, 0], xy[:, 1])
    return m_from_5179(np.c_[x, y])


def m_from_ll(xy):
    xy = np.atleast_2d(np.asarray(xy, float))
    x, y = _T4326_79.transform(xy[:, 0], xy[:, 1])
    return m_from_5179(np.c_[x, y])


class Mosaic:
    def __init__(self, aligned=True):
        import cv2
        meta = json.load(open(MOS / "mosaic_015.json"))
        self.x0, self.y1, self.res = meta["x0"], meta["y1"], meta["res_mm"]
        tag = "_aligned" if (aligned and (MOS / "mosaic_015_aligned.jpg").exists()) else ""
        self.rgb = cv2.cvtColor(cv2.imread(str(MOS / f"mosaic_015{tag}.jpg")), cv2.COLOR_BGR2RGB)
        self.valid = cv2.imread(str(MOS / f"mosaic_015{tag}_src.png"), cv2.IMREAD_GRAYSCALE) != 255
        self.h, self.w = self.valid.shape

    def to_px(self, xy):
        xy = np.atleast_2d(np.asarray(xy, float))
        return np.c_[(xy[:, 0] - self.x0) / self.res - 0.5, (self.y1 - xy[:, 1]) / self.res - 0.5]

    def to_m(self, uv):
        uv = np.atleast_2d(np.asarray(uv, float))
        return np.c_[self.x0 + (uv[:, 0] + 0.5) * self.res, self.y1 - (uv[:, 1] + 0.5) * self.res]


def imwrite(path, rgb):
    """한글 경로에도 저장(cv2.imwrite는 비ASCII 경로에서 조용히 실패한다)"""
    import cv2
    ok, buf = cv2.imencode(Path(path).suffix, cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))
    Path(path).write_bytes(buf.tobytes())
