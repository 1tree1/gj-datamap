"""통계 리포트 카드용 경량 집계 — 지도 레이어 파일(무거운 GeoJSON)을 리포트가 직접 읽지 않도록 숫자만 뽑는다.
입력: processed/*.geojson, gj-datamap/public/data/*.geojson(다른 세션이 만든 레이어 포함)
출력: processed/report_map_stats.json  →  sync → public/data/map_stats.json"""
import sys, json, collections
from pathlib import Path
from shapely.geometry import shape
from shapely.ops import transform
from pyproj import Transformer
from _common import PROCESSED, ROOT, save

WEB = ROOT.parent / "gj-datamap" / "public" / "data"
T = Transformer.from_crs(4326, 5187, always_xy=True).transform


def load(p):
    p = Path(p)
    return json.load(open(p, encoding="utf-8")) if p.exists() else None


def main():
    out = {}
    # 1) 필지: 노후도·규제 겹 수
    pl = load(PROCESSED / "parcels_lu_4326.geojson")
    ages = [f["properties"]["bldg_age"] for f in pl["features"] if isinstance(f["properties"].get("bldg_age"), (int, float))]
    bins = [("10년 미만", 0, 10), ("10–20년", 10, 20), ("20–30년", 20, 30), ("30–40년", 30, 40), ("40년 이상", 40, 999)]
    out["bldg_age"] = {"n": len(ages), "bins": [[b, sum(1 for a in ages if lo <= a < hi)] for b, lo, hi in bins],
                       "pct20": round(sum(1 for a in ages if a >= 20) / len(ages) * 100, 1), "pct30": round(sum(1 for a in ages if a >= 30) / len(ages) * 100, 1),
                       "n_parcels": len(pl["features"]), "n_unknown": sum(1 for f in pl["features"] if "bldg_age" in f["properties"] and not isinstance(f["properties"]["bldg_age"], (int, float))),
                       "src": "건축HUB 건축물대장 표제부(성동·황오·노서·노동·성건, 2026-09) × 연속지적 PNU 조인 — 사용승인일 있는 필지만"}
    rl = collections.Counter(f["properties"].get("reg_layers") for f in pl["features"])
    flags = {k: sum(1 for f in pl["features"] if f["properties"].get(k)) for k in ["reg_godo", "reg_special", "reg_boyuk", "reg_heritage", "reg_boho", "reg_fire", "reg_scenic", "reg_cult", "reg_jdp"]}
    out["reg_layers"] = {"dist": [[k, rl.get(k, 0)] for k in (1, 2, 3, 4)], "flags": flags, "n": len(pl["features"]),
                         "src": "V-World 토지이용계획 속성(getLandUseAttr) 7,616필지 · 포함·저촉만 · 겹 = ①용도지역·지구 ②고도보존육성 ③문화유산법 ④지구단위"}
    # 2) 고도지구 높이별 면적
    gd = load(PROCESSED / "godo_4326.geojson")
    ga = collections.defaultdict(float)
    for f in gd["features"]: ga[f["properties"]["h_cls"]] += f["properties"]["area_m2"]
    order = ["36m", "25m", "20m", "15m", "12m", "10m", "7.5m", "최저고도", "미확인"]
    out["godo"] = {"rows": [[k, round(ga.get(k, 0) / 1e4, 1)] for k in order if k in ga], "src": "V-World LT_C_UQ123 × 경북고시 2020-479호 조서·도면 라벨"}
    # 3) 규제 영역 종류별
    ra = load(PROCESSED / "reg_areas_4326.geojson")
    rr = collections.defaultdict(lambda: [0, 0.0, ""])
    for f in ra["features"]:
        p = f["properties"]; r = rr[p["reg"]]; r[0] += 1; r[1] += p["area_ha"]; r[2] = p["geom_src"]
    out["reg_areas"] = {"rows": [[k, v[0], round(v[1], 1), v[2]] for k, v in sorted(rr.items(), key=lambda x: -x[1][1])], "src": "V-World UO301·UQ126·UQ124·UQ123·UQ141 (법정) + 필지 외곽 근사 3종"}
    # 4) 획지 면적 vs 고시
    bl = load(PROCESSED / "gosi2026-8_blocks_4326.geojson")
    out["blocks"] = {"rows": [[f["properties"]["name"], f["properties"]["cls"], round(f["properties"]["area_m2"]), f["properties"].get("gosi_area_m2")] for f in bl["features"]],
                     "src": "경주시 고시 제2026-8호 지형도면고시도 벡터화 vs 고시문 결정조서"}
    # 5) 상가 업종
    st = load(PROCESSED / "stores_merged_4326.geojson")
    sc = collections.Counter(f["properties"].get("indsLclsNm") for f in st["features"])
    out["stores"] = {"rows": sc.most_common(), "n": len(st["features"]), "src": "소상공인시장진흥공단 상가업소 2026-03 (S2 창) + 경주시 게스트하우스 24"}
    # 6) 학교·종교 (다른 세션 레이어)
    sch = load(WEB / "schools.geojson")
    if sch:
        kc = collections.Counter(f["properties"].get("kind") for f in sch["features"] if not f["properties"].get("closed"))
        out["schools"] = {"rows": kc.most_common(), "closed": sum(1 for f in sch["features"] if f["properties"].get("closed")), "src": sch["features"][0]["properties"].get("source", "")}
    rel = load(WEB / "religion.geojson")
    if rel:
        rc = collections.Counter(f["properties"].get("religion") for f in rel["features"])
        dc = collections.Counter(f["properties"].get("dong") for f in rel["features"])
        out["religion"] = {"rows": rc.most_common(), "by_dong": dc.most_common(8), "n": len(rel["features"]), "src": rel["features"][0]["properties"].get("source", "")}
    # 7) 쇠퇴진단 2022 · 생활권 · 관광단지 · 공영주차장 · 시청 분산
    dc_ = load(WEB / "decline_2022.geojson")
    if dc_: out["decline"] = {"rows": [{k: f["properties"].get(k) for k in ("hadm", "pop_chg", "pop_5y", "biz_chg", "biz_5y", "old_pct", "met", "n_criteria", "crit_pop", "crit_biz", "crit_old")} for f in dc_["features"]], "src": dc_["features"][0]["properties"].get("source", "")}
    lz = load(WEB / "lifezone.geojson")
    if lz: out["lifezone"] = {"rows": [{k: f["properties"].get(k) for k in ("name", "pop_2013", "pop_2030_plan", "pop_2026_actual", "gap_pct", "park_plan_count", "unbuilt_park_count")} for f in lz["features"]]}
    tc = load(PROCESSED / "tourism_complex_4326.geojson")
    if tc: out["tourism_complex"] = [[f["properties"]["name"], f["properties"]["area_ha"], f["properties"]["gosi"]] for f in tc["features"]]
    pk = load(WEB / "parking_pub.geojson")
    if pk: out["parking_pub"] = {"rows": sorted([[f["properties"]["name"], f["properties"].get("spaces")] for f in pk["features"]], key=lambda x: -(x[1] or 0)), "total": sum(f["properties"].get("spaces") or 0 for f in pk["features"]), "src": pk["features"][0]["properties"].get("source", "")}
    ch = load(WEB / "cityhall_sites.geojson")
    if ch: out["cityhall"] = {"rows": [{k: f["properties"].get(k) for k in ("name", "addr", "own", "n_depts", "cls")} for f in ch["features"]], "src": ch["features"][0]["properties"].get("source", "")}
    # 8) 행정동 요약 + 경주시 합 연령·연도 (hadm_pop 1MB를 리포트에서 안 읽도록)
    hp = load(PROCESSED / "hadm_pop_4326.geojson")
    keys = ["hadm", "pop", "area_km2", "density", "n_65", "pct_65", "n_youth", "pct_youth", "n_y2034", "pct_y2034", "chg_10y_pct", "fr_total", "fr_pct", "mc_households", "fr_worker", "fr_marriage", "fr_student", "fr_diaspora", "fr_other", "fr_naturalized", "fr_children"]
    age = collections.Counter(); yearly = collections.Counter()
    rows = []
    for f in hp["features"]:
        p = f["properties"]; rows.append({k: p.get(k) for k in keys})
        for k, v in (p.get("age") or {}).items(): age[k] += v
        for k, v in (p.get("yearly") or {}).items(): yearly[k] += v
    out["hadm"] = {"rows": rows, "city_age": dict(age), "city_yearly": dict(sorted(yearly.items())), "src": "행안부 주민등록 2026-08 (KOSIS DT_1B04005N) · 외국인주민 2024.11 (DT_110025_A033_A) · 행정동 경계 근사"}
    save(out, PROCESSED / "report_map_stats.json")
    print("  keys:", list(out.keys()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
