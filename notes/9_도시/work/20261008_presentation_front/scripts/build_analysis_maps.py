# -*- coding: utf-8 -*-
"""발표 슬라이드용 분석 지도 일괄 재생성 (M4·M5·M6a~d·M8) + MANIFEST_analysis.csv 갱신.

실행: export PYTHONUTF8=1 PYTHONIOENCODING=utf-8; python build_analysis_maps.py   (약 15초, 네트워크 불필요)
필요 패키지: numpy · matplotlib · shapely 2.x · pyproj · pyshp · scipy · rasterio · PyMuPDF(pymupdf) · Pillow. 글꼴 Pretendard(없으면 맑은 고딕).
출력: assets/maps/m4_walk_barrier.png, m5_footfall_zones.png, m6a~d_*.png, m8_decision_map.png, MANIFEST_analysis.csv
      research/data_series/*.csv (detour_ratio_18sections, footfall_8zones, m4_metrics_check, m6_regulation_check, m8_blocks_check),
      siguel_digitized_5187.geojson
"""
import csv
import subprocess
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
PRJ = HERE.parent
OUT = PRJ / "assets" / "maps"

for script in ("m4_walk_barrier.py", "m5_footfall_zones.py", "m6_regulation.py", "m8_decision_map.py"):
    print("==", script)
    subprocess.run([sys.executable, "-X", "utf8", str(HERE / script)], check=True, cwd=str(HERE))
subprocess.run([sys.executable, "-X", "utf8", str(HERE / "siguel_digitize.py")], check=True, cwd=str(HERE))

ROWS = [
    ("m4_walk_barrier.png",
     "M4 보행 단절(S1~S2): 도로 횡단 없는 구간 985m, 보행 육교 1개(폭 3.2m·길이 약 216m), 부지 양쪽 두 지점 최단경로 1,531m(직선 601m의 약 2.55배), "
     "폐선 양쪽 60m 지점 간 우회율 18개 단면(중앙값 3.5, 최대 약 5.3)을 점 색으로, 부지로 접근하다 끊기는 도로 끝점 37곳",
     "대지/(B020)연속수치지도_202609132098 (N3A_B0010000 건물, N3L_A0020000 도로중심선, N3L_A0171119 철도중심선, N3A_A0160024 철도경계, N3A_A0063321 육교); "
     "work/20261005_boundary_check/user_boundary_current_5187.geojson; archive/C_data/processed/gosi2026-8_zone_5187.geojson",
     "연속수치지도 2026-09-13 취득(T2), 자체 계산 2026-09-28 재현", "1800x2400",
     "중심 (219,780/360,850), 동서 1,400m x 남북 1,867m. 985m 재산정 984.4m(반올림 차). 2.55(철도 횡단 한 쌍)와 3.5(18단면 중앙값)는 정의가 달라 라벨을 분리. 육교는 우회율 계산에 불포함", "m4_walk_barrier.py"),
    ("m5_footfall_zones.png",
     "M5 유동 낙차(S2): 소상공인365 분석 구역 8곳을 ha당 일평균 유동인구로 5단계 파랑 채색(#DCE6F5→#1F5AA6). 성동시장 200m 1,175 vs 폐역 구역 79명/ha(14.8배)",
     "archive/C_data/processed/footfall_areas_5187.geojson(A~D) + 원 구역 E~H(중심·반경은 pipeline/build_web_extras.py); archive/C_data/raw/sbiz365_footfall_20260920.json; "
     "archive/90_derived/footfall_sbiz365_summary.csv",
     "2025.06~2026.06 월별 일평균 13개월 평균(T2, 통신사 추정)", "2000x2000",
     "중심 (219,730/361,010), 한 변 3,300m. footfall_areas_5187.geojson 에는 A~D 4곳뿐이라 E~H 는 원으로 재구성. 구역이 겹쳐 작은 구역을 위에 그림", "m5_footfall_zones.py"),
    ("m6a_zoning.png", "M6a 용도지역: 본 계획 경계 안 자연녹지 77.5% · 2종일반주거 16.2% · 일반상업 6.4% (도형 교차)",
     "archive/C_data/raw/vworld_uq111.geojson (V-World UQ111, 2026-09 수집); work/20261005_boundary_check/user_boundary_current_5187.geojson",
     "V-World 용도지역(T1 성격의 법정 도형, 수집본은 T2 취급)", "1200x1600",
     "중심 (219,740/360,940), 동서 900m x 남북 1,200m. 경계 밖은 옅게. 문서값 77.5/16.3/6.2는 5m 격자 표본(±1%)", "m6_regulation.py"),
    ("m6b_height.png", "M6b 고도지구: 본 계획 경계 안 도심 20m 지구 87.5% · 15m 지구 11.3% (이전 경계 기준 문서값 89/9.8과 다름)",
     "archive/C_data/processed/godo_5187.geojson (V-World UQ123 + 경북고시 2020-479 높이); 본 계획 경계",
     "경북고시 2020-479, V-World(T1 성격)", "1200x1600",
     "같은 틀. 고도지구 폴리곤이 없는 부분 1.2%, 최저고도지구 3.8%(별도 규제, 20m·15m와 겹침)는 비율에서 제외·별도 표기", "m6_regulation.py"),
    ("m6c_heritage.png", "M6c 문화유산: 시굴 대상 145,879㎡(유물산포지 104,997 + 성동동사지Ⅱ 40,882), 삼층석탑, 역사문화환경 보존지역, 문화재 지정·보호구역(주변 고분·사적)",
     "archive/C_data/raw/vworld_uo301_heritage.geojson (V-World UO301); 04 김권일 학예연구실장_발표자료 ... .pdf p.23 그림 판독(scripts/siguel_digitize.py → research/data_series/siguel_digitized_5187.geojson); "
     "연속수치지도 N3P_C0310000 지명 주기", "김권일 2026.02.27 발표자료 p.23(T2) + V-World UO301(T1 성격)", "1200x1600",
     "같은 틀. 시굴 대상 도형은 그림 판독 근사(맞춤 IoU 0.928, 위치 ±10m, 면적 +0.8%). 현상변경 허용기준 구역(1~5구역)의 도형 자료는 없어 보존지역 도형으로 대체 표시", "m6_regulation.py, siguel_digitize.py"),
    ("m6d_plan.png", "M6d 지구단위계획: 고시 2026-8호 구역(156,460㎡)과 결정도 블록 10개 — 특별계획구역 5곳 82,544㎡, 근린공원 3곳 55,415㎡, 주거용지 없음",
     "archive/C_data/processed/gosi2026-8_blocks_5187.geojson, gosi2026-8_zone_5187.geojson", "경주시 고시 제2026-8호(2026-01-22) 결정조서·지형도면(T1)", "1200x1600",
     "같은 틀. 블록 도형은 지형도면 채움색 벡터화(조서 대비 ±수 %)", "m6_regulation.py"),
    ("m8_decision_map.png", "M8 결정도: 고시 2026-8호 블록을 용도별로 채색(근린공원 55,415 · 상업 42,031 · 공공청사 24,987 · 문화 9,770 · 주차장 5,756 · 도로 18,501㎡), 주거용지 없음 메모",
     "archive/C_data/processed/gosi2026-8_blocks_5187.geojson, gosi2026-8_zone_5187.geojson; 결정조서 면적(work/20260928_구경주역_규제법령_전수리스트_v1.md §4)",
     "경주시 고시 제2026-8호(2026-01-22) 결정조서(T1)", "1800x2400",
     "M6 과 같은 틀(2 px/m). 범례 면적·비율은 조서 값(고시 구역 156,460㎡ 기준), 블록 도형 재산정값은 research/data_series/m8_blocks_check.csv", "m8_decision_map.py"),
]
with open(OUT / "MANIFEST_analysis.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["file", "설명", "원자료 경로", "쪽/연도", "가로x세로 px", "비고", "script"])
    for r in ROWS:
        im = Image.open(OUT / r[0])
        px = f"{im.size[0]}x{im.size[1]}"
        assert px == r[4], (r[0], px, r[4])
        assert im.mode == "RGB", (r[0], im.mode)
        w.writerow(r)
print("MANIFEST_analysis.csv 갱신", len(ROWS), "건")
