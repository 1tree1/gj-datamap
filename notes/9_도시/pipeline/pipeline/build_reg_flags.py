"""토지이용계획 속성(raw/vworld_landuse_attr.json, PNU별 {nm, cnf}) → 필지 규제 플래그 + 규제 겹 수.
출력: processed/parcels_lu_4326.geojson (속성 갱신)

판정 규칙
  - cnf '포함'·'저촉'만 규제로 인정. '접함'(경계에 닿기만 함)은 제외 → lu_touch에 따로 기록.
  - 겹 수(reg_layers)는 CLAUDE.md §1 의 4겹 정의를 그대로 따른다:
      ① 용도지역·지구      — 항상 1 (고도지구·방화지구·경관지구·역사문화환경보호지구 등 국토계획법 용도지구 포함)
      ② 고도보존육성지구    — 「고도 보존 및 육성에 관한 특별법」: 역사문화환경 특별보존지구 ∨ 역사문화환경 보존육성지구
      ③ 역사문화환경 보존지역 — 「문화유산법」: 역사문화환경보존지역(반경 500m 허용기준) ∨ 국가지정문화유산구역(지정·보호구역)
      ④ 지구단위계획         — 지구단위계획구역 ∨ 제1종지구단위계획구역
  - 개별 플래그(reg_*)는 규제 영역 dissolve(build_reg_areas.py)용.
2026-09-17 이전 버전은 접함을 포함했고 겹 수 공식이 1+고도+(특별∨보존지역∨보호)+지구단위였다(인라인, 미저장) → 이 스크립트로 대체.
"""
import sys, json, collections
from _common import RAW, PROCESSED, save

FLAGS = {  # key: 항목명 정확 일치 목록
    "reg_godo":     ["고도지구"],
    "reg_special":  ["역사문화환경 특별보존지구"],
    "reg_boyuk":    ["역사문화환경 보존육성지구"],
    "reg_heritage": ["역사문화환경보존지역"],
    "reg_boho":     ["역사문화환경보호지구"],
    "reg_fire":     ["방화지구"],
    "reg_scenic":   ["중점경관관리구역"],
    "reg_cult":     ["국가지정문화유산구역", "문화유산보호구역"],
    "reg_jdp":      ["지구단위계획구역", "제1종지구단위계획구역"],
}
LAYER2 = ("reg_special", "reg_boyuk")
LAYER3 = ("reg_heritage", "reg_cult")
LAYER4 = ("reg_jdp",)
REGULATED = {"포함", "저촉"}


def main():
    fc = json.load(open(PROCESSED / "parcels_lu_4326.geojson", encoding="utf-8"))
    cache = json.load(open(RAW / "vworld_landuse_attr.json", encoding="utf-8"))
    cnt = collections.Counter(); dist = collections.Counter(); touch_only = collections.Counter()
    for f in fc["features"]:
        p = f["properties"]; rows = cache.get(p.get("pnu")) or []
        incl = [r["nm"] for r in rows if r.get("cnf") in REGULATED and r.get("nm")]
        touch = [r["nm"] for r in rows if r.get("cnf") == "접함" and r.get("nm")]
        p["lu_list"] = " · ".join(dict.fromkeys(incl)); p["lu_touch"] = " · ".join(dict.fromkeys(touch)); p["lu_n"] = len(rows)
        inc_set = set(incl); touch_set = set(touch) - inc_set
        for k, names in FLAGS.items():
            p[k] = any(n in inc_set for n in names); cnt[k] += p[k]
            if not p[k] and any(n in touch_set for n in names): touch_only[k] += 1
        p["reg_layers"] = 1 + int(any(p[k] for k in LAYER2)) + int(any(p[k] for k in LAYER3)) + int(any(p[k] for k in LAYER4))
        p["reg_l2"] = any(p[k] for k in LAYER2); p["reg_l3"] = any(p[k] for k in LAYER3); p["reg_l4"] = any(p[k] for k in LAYER4)
        dist[p["reg_layers"]] += 1
    save(fc, PROCESSED / "parcels_lu_4326.geojson", "규제 플래그(접함 제외, 4겹 정의)")
    print("  플래그 필지 수:", dict(cnt))
    print("  접함만 있어 제외된 필지:", dict(touch_only))
    print("  겹 수 분포:", dict(sorted(dist.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
