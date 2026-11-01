"""K12 GIS(GeoJSON, EPSG:5187) + 추적표 CSV — 획지·공원·도로·건물 폴리곤과, 각 획지가 어떻게 정해졌는지 기록한 추적표."""
import json, csv, os, sys
from shapely.geometry import mapping
from plotkit import *

os.makedirs(OUT + r"\gis", exist_ok=True)
TR = TC["lot_rows"]; RR = TC["road_rows"]; RN = TC["RNAME"]
def fc(feats): return {"type": "FeatureCollection", "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::5187"}}, "features": feats}
def feat(g, props): return {"type": "Feature", "properties": props, "geometry": mapping(g)}
def dump(name, feats): json.dump(fc(feats), open(OUT + r"\gis\%s.geojson" % name, "w", encoding="utf-8"), ensure_ascii=False)

dump("lots", [feat([l for l in LOTS if l["no"] == r["no"]][0]["geom"], {"plot": r["no"], "name": r["name"], "use": r["use"], "cat": r["cat"], "area_m2": round(r["area"], 1), "footprint_m2": round(r["fp"], 1),
                                                                         "bcr": round(r["bcr"], 4), "gfa_m2": round(r["gfa"], 1), "far": round(r["far"], 4), "max_floors": r["maxf"], "max_h_m": round(r["maxh"], 1), "godo_ref": r["godo_txt"]}) for r in TR])
dump("parks", [feat(d["geom"], {"name": d["name"], "kind": d["kind"], "area_m2": round(d["area"], 1)}) for d in PARKS])
roads = dict(NET["streets"]); roads.update(NET["lanes"]); used = []; rf = []
for r in RR:
    g = roads[r["key"]]; ex = g.difference(unary_union(used)) if used else g; used.append(g)
    rf.append(feat(ex, {"road": RN[r["key"]], "group": r["group"], "kind": r["kind"], "width_m": r["w"], "length_m": round(r["L"]), "area_m2": round(r["area_excl"], 1), "mode": r["mode"], "cross_assumed": r["cross"]}))
dump("roads", rf)
dump("buildings", [feat(b["geom"], {"plot": b["lot_no"], "lot": b["lot"], "name": b["name"], "use": b["use"], "cat": b["cat"], "role": b["role"], "floors": b["floors"], "floor_h_m": b["floor_h"], "height_m": b["h"],
                                    "footprint_m2": round(b["area"], 1), "gfa_m2": round(b["area"] * b["floors"], 1), "retail_ground": bool(b["retail_ground"])}) for b in BUILD])

# ── 추적표 ──
blk = {}
for d in LOTS:
    p = d["geom"].representative_point(); blk[d["no"]] = next((b["id"] for b in NET["blocks"] if b["geom"].buffer(0.5).contains(p)), "")
TYPO = {
    1: ("가구 {b} 전체", "독립 박스 + 부속동 + 옥외 운동장", "체육센터 56×38 m 2F(층고 6.5), 생활SOC 38×14 m 3F, 운동장 2면", "스케치 '공공운동/생활시설'. 수변공원과 시청 사이 완충"),
    2: ("가구 {b} 전체", "ㄷ자 둘레형(통경 1)", "후퇴 4 m, 깊이 12.5 m, 5F, 1층 근생", "스케치 '청년주거zone'. 수변공원 남변"),
    3: ("가구 {b} 전체", "ㄷ자 + 박스 + 3F 가로벽(통경 2)", "깊이 15 m, 북·남 5F, 서 3F, 의회 4F 36×31 m, 시민동 3F 19 m 폭", "스케치 '시청/의회부지'. 서변 원화로 가로벽·앵커(361,160·361,188) 통경"),
    4: ("가구 {b} 전체", "ㅁ자 둘레형(통경 2)", "후퇴 4 m, 깊이 12.5 m, 6F, 1층 근생", "종축 S 서변. 긴 변(≥52 m) 중 가장 긴 2곳에 통경 12 m"),
    5: ("가구 {b} 전체", "ㄷ자 둘레형(통경 1)", "후퇴 4 m, 깊이 12 m, 4F", "스케치 '청년주거zone' 동측"),
    6: ("가구 {b} 전체", "평행 바 2열(3F)", "깊이 13 m, 간격 8 m, 통경 7 m", "연립형 — 소규모 획지"),
    7: ("가구 {b} 전체", "ㄱ자 + 박스 + 3F 가로상점", "문화센터 4F, 영화관 48×34 m 3F(층고 5.5), 가로상점 17 m 폭 3F(통경 2)", "스케치 '복합문화공간/영화관'"),
    8: ("가구 {b} 전체", "ㅁ자 둘레형(통경 1) + 모서리 8F", "깊이 14 m, 둘레 6F, 북서 30×30 m 8F, 1층 판매", "스케치 '청년창업/경주기업지원zone'. 8F는 S·B 모서리 랜드마크"),
    9: ("가구 {b} 전체", "소형 박스 2×3 + 마을마당", "20×18 m 3F 6동", "스케치 '청년주민커뮤니티zone'"),
    10: ("가구 {b}의 서쪽(x<219,737) 분할", "평행 바(2F) + 서변 3F 가로상점 + 석탑 마당", "바 폭 10 m, 간격 6 m, 서변 14 m는 3F, 삼층석탑 중심 반경 22 m 비움", "스케치 '성동시장활성화클러스터'. 삼층석탑 점(219,660;360,816) — 허용기준 원문 미확인"),
    11: ("가구 {b}의 동쪽 분할(서쪽은 Plot 10)", "2열 점포 + 체험 거리", "폭 (W−12)/2 m 2F 두 열", "스케치 '체험판매'"),
    12: ("가구 {b} 전체", "사선(56.1°) 평행 바", "깊이 11 m, 간격 6 m, 3F", "스케치 '아티스트레지던시/오픈스튜디오/체험공방'. R6 사선과 평행"),
    13: ("가구 {b} 전체", "사선 평행 바", "깊이 10 m, 간격 5 m, 3F", "위와 동일"), 14: ("가구 {b} 전체", "사선 평행 바", "깊이 10 m, 간격 5 m, 3F", "위와 동일"),
    15: ("가구 {b}에서 R6 중심선 ±63 m 띠(나머지는 Park C)", "기존 건물 1동(구 역사, 근대역사관 겸용) + 역사 광장", "구 역사 = NGII 기존 건물 폴리곤 1,404㎡(22꼭짓점) 2F 형상 그대로, 장축을 획지 장축(56.06°)에 맞춰 -33.27° 회전", "스케치 '구경주역 옮김', '경주근대역사관&전시장'(구 역사가 겸함). 구 역사 등록문화유산 여부 자료 상충(미확인)"),
    16: ("가구 {b} 전체", "주동 + 남·북 동 + 라이너 + 임시 평면주차", "주동 34 m 폭 5F, 남·북 동 4F, 판매·공방 라이너 2F", "스케치 '주차타워'. 지하주차는 매장문화재로 1단계 불가 → 지상 주차전용건축물"),
    17: ("가구 {b}의 서쪽(x<219,798) 분할(동쪽은 Plaza D)", "3층 바 + 승강장 앞마당", "20 m 폭 3F", "스케치 '경주관광지원시설'. 환승광장 Plaza D와 접함"),
    18: ("가구 {b} 전체", "ㄱ자 둘레형(통경 1)", "후퇴 4 m, 깊이 13 m, 3F", "스케치 '관광객중심 휴게판매상가'"), 19: ("가구 {b} 전체", "ㄱ자 둘레형(통경 1)", "후퇴 4 m, 깊이 13 m, 3F", "위와 동일")}
with open(OUT + r"\추적표_획지매스_규제미적용v1.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerow(["획지", "획지명", "원 가구(네트워크)", "획지 근거", "매스 유형", "주요 파라미터(계획 가정)", "스케치·프로그램 근거", "연면적(㎡)", "최고층수", "최고높이(m)", "고도지구 참고", "고도 초과(참고)", "사람 손 조정 내역"])
    for r in TR:
        t = TYPO[r["no"]]; t = (t[0].format(b=blk[r["no"]]),) + t[1:]
        hand = ("2026-10-05 사용자 지시: 생성 매스(76×18.5 m 띠 + 75×26 m 4F 근대역사관 블록)가 부자연스러워 삭제하고, 기존 구 경주역 건물 형상(NGII 1,404㎡ 2F)으로 교체. "
                "근대역사관·전시장 별동은 두지 않고 이전한 구 역사가 겸함. 위치·회전은 획지 안 최대 이격으로 산정(가정)") if r["no"] == 15 else "없음(규칙기반 생성 그대로) — 아직 파레토 선택·수동 다듬기 전"
        w.writerow([r["no"], r["name"], blk[r["no"]], t[0], t[1], t[2], t[3], round(r["gfa"]), r["maxf"], round(r["maxh"], 1), r["godo_txt"], ("초과 %d동" % r["over_n"]) if r["over_n"] else "-", hand])
print("saved gis + tracking")

