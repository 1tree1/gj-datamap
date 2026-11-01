"""고도지구 높이별 분류 — V-World LT_C_UQ123 폴리곤(속성은 '고도지구'뿐)에
경상북도 고시 제2020-479호(경주 도시관리계획(고도지구) 결정(변경), 2020-12-28) 결정조서·지형도면고시도의
지구명·높이를 붙인다. 출력 EPSG:5187 / 4326.

배정 근거(conf):
  label  — 2020-479 지형도면 총괄도/도면 라벨(원문자+높이)이 폴리곤 안에 떨어짐
  zone   — 고시 2026-8호 조서(구역 내 도심20m 145,364 / 도심15m 11,143㎡)와 교차면적 일치
  area   — 조서 면적 합과 ±1% 일치(도심10m: 654,156+228,252+166,934+32,580 = 1,081,922 vs 1,085,652)
  approx — 면적·위치로 추정(±5% 초과 또는 라벨 오차 범위)
  none   — 2020-479 도면 범위 밖. 높이 미확인(2023-449호 등 별도 고시 필요)
"""
import sys, json
from pyproj import Transformer
from shapely.geometry import shape, mapping
from shapely.ops import transform
from shapely.geometry.polygon import orient
from _common import RAW, PROCESSED, save

# _i(원본 인덱스) → (도면표시번호, 지구명, 높이 m, 근거)
ASSIGN = {
    2:  ("1", "도심36m지구", 36, "label"),
    1:  ("6", "도심20m지구", 20, "label"),
    47: ("6", "도심20m지구", 20, "zone"),
    14: ("2", "도심12m지구", 12, "label"),
    32: ("3", "도심7.5m지구", 7.5, "label"),
    29: ("5", "도심25m지구", 25, "label"),
    20: ("7", "도심15m지구", 15, "label"),
    6:  ("7", "도심15m지구", 15, "zone"),
    25: ("8", "도심10m지구", 10, "area"),
    5:  ("8", "도심10m지구", 10, "area"),
    18: ("8", "도심10m지구", 10, "area"),
    48: ("8", "도심10m지구", 10, "area"),
    46: ("30", "팔우정지구", 15, "approx"),
    23: ("11", "구정지구", 36, "label"),
    36: ("4", "구정12m지구", 12, "approx"),
}
# 면적으로 식별하는 것(인덱스가 수집 순서에 따라 바뀔 수 있어 면적 키 병행)
ASSIGN_BY_AREA = {  # 반올림 면적 → 배정
    4773:  ("17", "황성지구", 15, "approx"),
    49741: ("31", "구정21m지구", 21, "approx"),
    81545: ("4", "구정12m지구", 12, "approx"),
}
GOSI = {"2020-0479": "경북고시 2020-479 (고도지구 정비)", "2023-0449": "경북고시 2023-449 (용도지구 변경)",
        "2024-0241": "경주시고시 2024-241 (황오1지구 지적재조사)", "2021-0220": "경북고시 2021-220 (재정비)",
        "2010-0618": "경북고시 2010-618 (재정비)", "2022-0142": "경주시고시 2022-142 (보문천군 도시개발)"}


def main():
    t87 = Transformer.from_crs(4326, 5187, always_xy=True).transform
    t26 = Transformer.from_crs(5187, 4326, always_xy=True).transform
    src = json.load(open(RAW / "vworld_uq123_godo.geojson", encoding="utf-8"))
    out87, out26 = [], []
    stats = {}
    for f in src["features"]:
        pr = f["properties"]; g = transform(t87, shape(f["geometry"]))
        area = round(g.area)
        a = ASSIGN.get(pr["_i"]) or ASSIGN_BY_AREA.get(area)
        if pr["uname"] == "최저고도지구":
            a = ("-", "최저고도지구", None, "label")
        num, nm, h, conf = a if a else ("?", "고도지구(높이 미확인)", None, "none")
        gosi = f"{pr['dyear']}-{pr['dnum']}"
        p = {"godo_no": num, "godo_nm": nm, "h_max": h, "kind": "최저" if nm == "최저고도지구" else "최고",
             "conf": conf, "area_m2": area, "gosi_last": GOSI.get(gosi, gosi if gosi != "0000-0000" else "미기재"),
             "src": "V-World LT_C_UQ123 + 경북고시 2020-479 조서·도면",
             "h_cls": ("최저고도" if nm == "최저고도지구" else (f"{h:g}m" if h else "미확인")),
             "lbl": (f"{nm}\n{h:g}m 이하" if h else nm)}
        stats[nm] = stats.get(nm, 0) + area
        out87.append({"type": "Feature", "properties": p, "geometry": mapping(g)})
        g26 = transform(t26, g)
        if g26.geom_type == "Polygon": g26 = orient(g26, 1.0)
        else: g26 = type(g26)([orient(q, 1.0) for q in g26.geoms])
        out26.append({"type": "Feature", "properties": p, "geometry": mapping(g26)})
    save({"type": "FeatureCollection", "features": out87}, PROCESSED / "godo_5187.geojson")
    save({"type": "FeatureCollection", "features": out26}, PROCESSED / "godo_4326.geojson")
    for k, v in sorted(stats.items(), key=lambda x: -x[1]): print(f"  {k:<16} {v:>12,}㎡")
    return 0


if __name__ == "__main__":
    sys.exit(main())
