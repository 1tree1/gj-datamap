"""V-World 수집 — 경주시 전역 용도지역(LT_C_UQ111)·문화유산 보호 구역(LT_C_UO301).
일반인용 '경주시 한눈에' 지도의 시가지(주거·상업·공업)와 문화유산 구역 표시용.

collect_vworld.py 는 부지 주변 창만 받는다. 여기서는 시 경계 상자를 4×4로 나눠 받고,
타일 경계에 걸친 폴리곤은 여러 번 돌아오므로 (구역명 + 도형) 해시로 중복을 지운다.
출력(EPSG:4326, 원본 그대로 — 이웃 시군 폴리곤도 섞여 있으므로 쓸 때 sigg_name으로 거른다):
  archive/C_data/raw/vworld_uq111_city.geojson
  archive/C_data/raw/vworld_uo301_city.geojson
"""
import hashlib
import json
import os

from _common import RAW, load_env, save
from collect_vworld import wfs

CITY_BBOX = (128.97, 35.64, 129.53, 36.09)   # vworld_emd_gj.geojson 56개 동·읍·면 합집합 범위 + 여유
N = 4
LAYERS = [("LT_C_UQ111", "uq111_city", "용도지역"), ("LT_C_UO301", "uo301_city", "문화유산 보호 구역")]


def fetch(layer, key, headers):
    x0, y0, x1, y1 = CITY_BBOX
    dx, dy = (x1 - x0) / N, (y1 - y0) / N
    seen, feats = set(), []
    for i in range(N):
        for j in range(N):
            box = (x0 + i * dx, y0 + j * dy, x0 + (i + 1) * dx, y0 + (j + 1) * dy)
            got, total = wfs(layer, key, headers, bbox=box, size=1000, cap=20)
            new = 0
            for f in got:
                h = hashlib.md5((f["properties"].get("uname", "") + json.dumps(f["geometry"], sort_keys=True)).encode()).hexdigest()
                if h not in seen:
                    seen.add(h); feats.append(f); new += 1
            print(f"  타일 {i},{j}: 서버 {total} · 받음 {len(got)} · 새것 {new}")
    return feats


def main():
    load_env()
    key = os.environ["VWORLD_KEY"]
    headers = {"Referer": os.environ.get("VWORLD_DOMAIN", ""), "User-Agent": "Mozilla/5.0"}
    for layer, slug, name in LAYERS:
        out = RAW / f"vworld_{slug}.geojson"
        if out.exists():
            print(f"[{name}] 이미 있음 — 건너뜀 ({out.name})"); continue
        print(f"[{name}] {layer}")
        feats = fetch(layer, key, headers)
        fc = {"type": "FeatureCollection", "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}}, "features": feats}
        save(fc, out, f"경주시 전역 {name} {len(feats)}개(이웃 시군 포함)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
