"""도면의 파란 지적선 ↔ V-World 필지 경계선 상호상관으로 평행이동 잔차 보정.

입력: georef_jihyeong.py 산출물(PNG+PGW, 5187) + vworld_parcel.geojson
출력: 보정된 PGW (원본은 *.pgw.orig 로 보존), manifest에 refine 기록
"""
import json, sys, shutil
import numpy as np
from PIL import Image, ImageDraw
from pyproj import Transformer
from _common import RAW, PROCESSED

DS = 4          # 다운샘플 배수
SEARCH = 60     # ±픽셀(다운샘플 기준) = ±44m


def load_pgw(p):
    a, d, b, e, c, f = [float(x) for x in open(p).read().split()]
    return a, e, c, f  # px, -py, x0(center of first px), y0


def main():
    man = json.load(open(PROCESSED / "gosi2026-8_georef_manifest.json", encoding="utf-8"))
    feats = json.load(open(RAW / "vworld_parcel.geojson", encoding="utf-8"))["features"]
    t = Transformer.from_crs("EPSG:4326", "EPSG:5187", always_xy=True).transform
    for m in man:
        slug = m["slug"]; png = PROCESSED / f"gosi2026-8_{slug}_5187.png"; pgw = PROCESSED / f"gosi2026-8_{slug}_5187.pgw"
        px, npy, cx0, cy0 = load_pgw(pgw); py = -npy
        ox, oy = cx0 - px/2, cy0 + py/2          # 좌상 모서리
        img = np.asarray(Image.open(png).convert("RGB"))
        H, W = img.shape[:2]
        # 1) 도면 파란 선 추출
        r, g, b = img[..., 0].astype(int), img[..., 1].astype(int), img[..., 2].astype(int)
        blue = (b > 140) & (r < 130) & (g < 130)
        h, w = H // DS, W // DS
        e1 = blue[:h*DS, :w*DS].reshape(h, DS, w, DS).any(axis=(1, 3)).astype(np.float32)
        # 2) V-World 경계선 래스터화 (같은 격자)
        canvas = Image.new("L", (w, h), 0); dr = ImageDraw.Draw(canvas)
        for f in feats:
            g_ = f["geometry"]; rings = [g_["coordinates"][0]] if g_["type"] == "Polygon" else [p[0] for p in g_["coordinates"]]
            for ring in rings:
                pts = []
                for lon, lat in ring:
                    x, y = t(lon, lat); pts.append(((x - ox) / px / DS, (oy - y) / py / DS))
                if any(-SEARCH <= u <= w + SEARCH and -SEARCH <= v <= h + SEARCH for u, v in pts):
                    dr.line(pts, fill=255, width=1)
        e2 = (np.asarray(canvas) > 0).astype(np.float32)
        # 3) FFT 상호상관
        e1c = e1 - e1.mean(); e2c = e2 - e2.mean()
        F = np.fft.rfft2(e1c) * np.conj(np.fft.rfft2(e2c))
        cc = np.fft.irfft2(F, s=e1.shape)
        cc = np.fft.fftshift(cc)
        cy, cx = h // 2, w // 2
        win = cc[cy-SEARCH:cy+SEARCH+1, cx-SEARCH:cx+SEARCH+1]
        iy, ix = np.unravel_index(np.argmax(win), win.shape)
        dv, du = (iy - SEARCH) * DS, (ix - SEARCH) * DS     # e2를 (du,dv) 만큼 옮기면 e1과 맞음
        peak = win.max(); second = np.partition(win.flatten(), -2)[-2]
        # V-World가 (du,dv)px 만큼 이동해야 도면과 일치 ⇒ 도면 원점을 반대로 보정
        dx_m, dy_m = -du * px, dv * py
        print(f"[{slug}] 상관 피크 du={du:+d}px dv={dv:+d}px → 원점 보정 ({dx_m:+.1f}m, {dy_m:+.1f}m)  peak/2nd={peak/second:.2f}")
        shutil.copy(pgw, str(pgw) + ".orig")
        nox, noy = ox + dx_m, oy + dy_m
        pgw.write_text(f"{px:.6f}\n0.0\n0.0\n{-py:.6f}\n{nox + px/2:.4f}\n{noy - py/2:.4f}\n")
        m["refine"] = dict(method="blue-line xcorr vs V-World parcels", shift_m=[dx_m, dy_m], peak_ratio=float(peak/second))
        m["out_bbox"] = [nox, noy - H*py, nox + W*px, noy]
    json.dump(man, open(PROCESSED / "gosi2026-8_georef_manifest.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
