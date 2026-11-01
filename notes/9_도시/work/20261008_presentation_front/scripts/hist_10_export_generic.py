# -*- coding: utf-8 -*-
"""저장된 변환으로 F1/F2 크롭 내보내기 (정사영상·항공사진 공용)
사용: python hist_10_export_generic.py KEY PREFIX YEAR FRAMES(F1,F2) [outline_frames] [mode]
mode: color | gray_clahe | gray_raw
"""
import sys
sys.path.insert(0, "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/scripts")
from histlib import *

def export(key, prefix, year, frames, outline_frames=(), mode="color", valid_poly=None, clahe_clip=2.0, ext="jpg", a=None):
    H, info = load_transform(key)
    gsd = float(np.sqrt(abs(np.linalg.det(H[:2, :2]))))
    if a is None:
        a = load_full(key, gray=(mode != "color"))
    cov = {}
    for fr in frames:
        p = pick_prescale(gsd, fr)
        src = prescale(a, p)
        out, mask = warp_to_frame(src, H, fr, gsd, prescaled=p, valid_poly=valid_poly)
        if mode == "gray_clahe":
            # 유효 영역 안에서만 대비 보정
            out = clahe_gray(out, clahe_clip, 8)
        out2 = fill_nodata(out, mask)
        if ext == "jpg":
            save_jpg(HIST + f"{prefix}_{year}_{fr}.jpg", out2)
        else:
            save_png(HIST + f"{prefix}_{year}_{fr}.png", out2)
        if fr in outline_frames:
            if ext == "jpg":
                save_jpg(HIST + f"{prefix}_{year}_{fr}_outline.jpg", draw_outline(out2, fr))
            else:
                save_png(HIST + f"{prefix}_{year}_{fr}_outline.png", draw_outline(out2, fr))
        cov[fr] = float(mask.mean())
        print(f"{prefix}_{year}_{fr}: gsd {gsd:.3f} m prescale {p} coverage {mask.mean():.3f}")
    return cov

if __name__ == "__main__":
    key, prefix, year = sys.argv[1:4]
    frames = sys.argv[4].split(",")
    ol = sys.argv[5].split(",") if len(sys.argv) > 5 and sys.argv[5] != "-" else []
    mode = sys.argv[6] if len(sys.argv) > 6 else "color"
    export(key, prefix, year, frames, ol, mode)
