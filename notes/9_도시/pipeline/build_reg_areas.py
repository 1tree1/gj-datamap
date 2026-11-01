"""규제별 영역 — v2 (2026-09-17): 법정 경계 폴리곤(V-World) 우선, 없는 종류만 필지 외곽(dissolve)으로 근사.

  법정 경계 (V-World 2D 데이터 API, 토지이용규제 원본)
    LT_C_UO301  역사문화환경보존지역 · 국가지정문화재구역 · 문화재보호구역 · 시도지정문화재구역 · 문화재(지정물) · 등록문화재구역
    LT_C_UQ126  역사문화환경보호지구 (국토계획법 용도지구)
    LT_C_UQ124  방화지구
    LT_C_UQ123  고도지구 (최고고도; 높이별은 godo 레이어)
    LT_C_UQ141  지구단위계획구역 (제1·2종 포함)
  필지 외곽 근사 (processed/parcels_lu_4326.geojson 의 reg_* 플래그 dissolve, 포함·저촉만)
    역사문화환경 특별보존지구 · 역사문화환경 보존육성지구 (고도보존육성 특별법) · 중점경관관리구역 — V-World에 레이어 없음

v1(필지 외곽만)과의 차이: 필지 합집합은 도로·하천·미등록지에서 끊기고 수집 창(7,616필지) 밖은 아예 없다.
법정 폴리곤은 지정 경계 그대로이고 창 밖까지 이어지며, 문화유산 이름(alias/remark)과 마지막 고시번호가 붙는다.
출력: processed/reg_areas_4326.geojson  (피처 속성: reg 종류 · name · geom_src · gosi · area_ha · lbl)"""
import sys, json, re
from shapely.geometry import shape, mapping
from shapely.ops import unary_union, transform as stf
from shapely.geometry.polygon import orient
from pyproj import Transformer
from _common import RAW, PROCESSED

LEGAL = [  # (파일, uname 매핑 {원 uname: 표시 종류})
    ("vworld_uo301_heritage.geojson", {"역사문화환경보존지역": "역사문화환경보존지역", "국가지정문화재구역": "국가지정문화유산구역", "지정문화재구역": "국가지정문화유산구역",
                                       "문화재보호구역": "문화유산 보호구역", "시도지정문화재구역": "시도지정문화유산구역", "문화재": "문화유산(지정물)", "등록문화재구역": "등록문화유산구역"}),
    ("vworld_uq126_boho.geojson", {"역사문화환경보호지구": "역사문화환경보호지구"}),
    ("vworld_uq124_fire.geojson", {"방화지구": "방화지구"}),
    ("vworld_uq123_godo.geojson", {"고도지구": "고도지구"}),
    ("vworld_uq141_jdp.geojson", {"지구단위계획구역": "지구단위계획구역", "제1종지구단위계획구역": "지구단위계획구역", "제2종지구단위계획구역": "지구단위계획구역"}),
]
APPROX = [("reg_special", "역사문화환경 특별보존지구", "고도보존육성 특별법 — V-World 레이어 없음"),
          ("reg_boyuk", "역사문화환경 보존육성지구", "고도보존육성 특별법 — V-World 레이어 없음"),
          ("reg_scenic", "중점경관관리구역", "경관법 경관계획 — V-World 레이어 없음")]
NOLABEL = {"고도지구", "방화지구", "역사문화환경보호지구", "국가지정문화유산구역", "문화유산 보호구역", "시도지정문화유산구역", "등록문화유산구역", "문화유산(지정물)"}  # 조각이 많아 이름 없는 건 라벨 생략
ORDER = ["역사문화환경보존지역", "역사문화환경 특별보존지구", "역사문화환경 보존육성지구", "역사문화환경보호지구", "국가지정문화유산구역", "문화유산 보호구역",
         "시도지정문화유산구역", "등록문화유산구역", "문화유산(지정물)", "고도지구", "방화지구", "중점경관관리구역", "지구단위계획구역"]


def heritage_name(p):
    """UO301: alias·remark에 지정번호/이름/허용기준 구역이 뒤섞여 있다 → 이름을 우선 고르고 나머지는 note."""
    a, r = (p.get("alias") or "").strip(), (p.get("remark") or "").strip()
    is_no = lambda s: bool(re.fullmatch(r"(사적|보물|국보|명승|천연기념물|유형문화재|문화재자료|등록문화재|기념물|민속문화재)\s*제?\d+호?", s))
    name = r if (r and not is_no(r) and "구역" not in r and "이내" not in r and "허용기준" not in r) else (a if (a and not is_no(a)) else "")
    note = " · ".join(x for x in (a if is_no(a) else "", r if (r and r != name) else "") if x)
    return name, note


def main():
    to5187 = Transformer.from_crs("EPSG:4326", "EPSG:5187", always_xy=True).transform
    to4326 = Transformer.from_crs("EPSG:5187", "EPSG:4326", always_xy=True).transform
    feats = []; summary = {}
    # 1) 법정 경계
    for fn, umap in LEGAL:
        fc = json.load(open(RAW / fn, encoding="utf-8"))
        for f in fc["features"]:
            p = f["properties"]
            if p.get("sigg_name") and p["sigg_name"] != "경주시": continue
            reg = umap.get(p.get("uname"))
            if not reg: continue
            g = shape(f["geometry"]); a = stf(to5187, g).area
            if a < 1: continue
            name, note = heritage_name(p) if "uo301" in fn else ("", "")
            gosi = f"{p.get('dyear')}-{p.get('dnum')}" if p.get("dyear") not in (None, "0000") else ""
            g = orient(g, 1.0) if g.geom_type == "Polygon" else type(g)([orient(q, 1.0) for q in g.geoms])
            feats.append({"type": "Feature", "geometry": mapping(g),
                          "properties": {"reg": reg, "name": name, "note": note, "geom_src": "법정 경계 (V-World)", "gosi": gosi, "area_ha": round(a / 1e4, 2),
                                         "lbl": name or ("" if reg in NOLABEL else reg), "layer": fn.split("_")[1].upper()}})
            s = summary.setdefault(reg, [0, 0.0]); s[0] += 1; s[1] += a
    # 2) 필지 외곽 근사
    pl = json.load(open(PROCESSED / "parcels_lu_4326.geojson", encoding="utf-8"))
    geoms = [(f["properties"], stf(to5187, shape(f["geometry"]))) for f in pl["features"]]
    for key, reg, note in APPROX:
        sel = [g for p, g in geoms if p.get(key)]
        if not sel: continue
        u = unary_union(sel).buffer(0.6, join_style=2).buffer(-0.6, join_style=2).simplify(0.3)
        polys = [orient(x, 1.0) for x in (u.geoms if u.geom_type == "MultiPolygon" else [u]) if x.area > 50]
        g4326 = stf(to4326, unary_union(polys))
        feats.append({"type": "Feature", "geometry": mapping(g4326),
                      "properties": {"reg": reg, "name": "", "note": note + f" · 포함·저촉 필지 {len(sel)}개 합집합(수집 창 한정)", "geom_src": "필지 외곽 (근사)", "gosi": "",
                                     "area_ha": round(u.area / 1e4, 2), "lbl": reg + " (필지 근사)", "layer": "PARCEL"}})
        summary[reg] = [1, u.area]
    feats.sort(key=lambda f: ORDER.index(f["properties"]["reg"]) if f["properties"]["reg"] in ORDER else 99)
    (PROCESSED / "reg_areas_4326.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": feats}, ensure_ascii=False), encoding="utf-8")
    for reg in ORDER:
        if reg in summary: n, a = summary[reg]; print(f"  {reg:<16} {n:>4}개 {a/1e4:>9,.1f}ha")
    print(f"저장 reg_areas_4326.geojson ({len(feats)} 피처)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
