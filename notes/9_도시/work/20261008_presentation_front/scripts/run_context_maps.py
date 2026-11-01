# -*- coding: utf-8 -*-
"""맥락 지도 5종(M1·M2·M3·M7·M9) + M3 대안(m3b)을 한꺼번에 다시 만든다.

사용: export PYTHONUTF8=1 PYTHONIOENCODING=utf-8 ; (선택) export MAPKIT_CACHE=<캐시 폴더> ; python run_context_maps.py
출력: assets/maps/*.png · assets/maps/MANIFEST_context.csv · research/context_maps_checks.csv(문서 값 ↔ 지도 재산정 값)
끝에서 PNG 크기·모드(RGB 불투명)·흰 바탕을 확인하고 MANIFEST를 파일명 순서로 정리한다.
"""
import csv
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
PRJ = HERE.parent
OUT = PRJ / "assets" / "maps"
CHK = PRJ / "research" / "context_maps_checks.csv"
MAN = OUT / "MANIFEST_context.csv"

JOBS = [("m1_gyeongju_city.py", []), ("m2_oldcore_1km.py", []), ("m3_site_distance.py", []), ("m3_site_distance.py", ["alt"]),
        ("m7_boundaries.py", []), ("m9_rail_axis_S3.py", [])]
EXPECT = {"m1_gyeongju_city.png": (1800, 2250), "m2_oldcore_1km.png": (2000, 2000), "m3_site_distance.png": (2000, 2000),
          "m3b_site_distance_station_building.png": (2000, 2000), "m7_boundaries.png": (1800, 2400), "m9_rail_axis_S3.png": (2000, 1500)}


def main():
    for p in (CHK, MAN):                       # 이름이 바뀐 옛 행이 남지 않게 새로 쓴다
        p.unlink(missing_ok=True)
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8", PYTHONDONTWRITEBYTECODE="1")
    for script, args in JOBS:
        print(f"=== {script} {' '.join(args)}")
        subprocess.run([sys.executable, "-W", "ignore", str(HERE / script), *args], check=True, env=env)
    # MANIFEST 정렬
    with open(MAN, encoding="utf-8-sig", newline="") as f:
        rd = csv.DictReader(f)
        head, rows = rd.fieldnames, list(rd)
    order = list(EXPECT)
    rows.sort(key=lambda r: order.index(r["file"]) if r["file"] in order else 99)
    with open(MAN, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=head)
        w.writeheader()
        w.writerows(rows)
    # 검증
    bad = 0
    for fn, size in EXPECT.items():
        im = Image.open(OUT / fn)
        a = np.asarray(im.convert("RGB"))
        white = float((a == 255).all(axis=2).mean())         # 순백 픽셀 비율(흰 바탕 확인; 창 지도는 가장자리가 건물로 덮여 있어 모서리 한 점으로는 못 본다)
        ok = im.size == size and im.mode == "RGB" and white > 0.05
        bad += not ok
        print(f"{'OK ' if ok else 'BAD'} {fn} {im.size} {im.mode}(알파 없음) dpi={tuple(round(v) for v in im.info.get('dpi', (0, 0)))} 순백 픽셀 {white * 100:.0f}%")
    print("MANIFEST 행", len(rows), "· 검증 실패", bad)
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
