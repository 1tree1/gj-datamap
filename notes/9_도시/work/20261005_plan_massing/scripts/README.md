# scripts — 도시계획안 구획·매스 v1 재현

모든 스크립트 맨 위의 `SP`(중간 산출물 폴더)는 작업 세션의 임시 폴더다. 다른 곳에서 돌리려면 `SP`를 바꾼다. 필요 라이브러리: shapely, pyproj, numpy, matplotlib, scipy, opencv-python-headless, pyshp (가상환경 사용 권장).

| 순서 | 파일 | 하는 일 |
|---|---|---|
| 0 | `s0_context.py` | NGII 건물·도로, 고도지구, 필지를 EPSG:5187로 모음 |
| 1 | `s1_anchors.py` | 경계에 닿는 기존 가로(앵커) 추출 |
| 2 | `s2_basesheet.py`, `s2b_zscale.py` | 설계 기준 시트, 모형 z 단위(층당 1.75) 확인 |
| 3 | `plan_def.py` → `s3_network.py` | 가로·골목·녹지띠 정의 → 가구 19개로 구획(면적 합계 검증) |
| 4 | `geomkit.py`, `plan_meta.py` → `s4_massing.py` | 가구별 유형 규칙으로 매스 생성, 높이 포락, 겹침·도로 침범 검증 |
| 4b | `s4b_connect.py` | 앵커 연결 검사 + 관통 통로 보정 |
| 5 | `s6_overlay.py` | 가구별 현행 용도지역·고시구역·고도지구·보존지역·기존 건물 |
| 6 | `s7_tables.py` | 표(CSV)와 규제 점검 |
| 7 | `s5_render.py`, `s7_figures.py`, `plan_calls.py` | 도면 6종 |
| 8 | `s8_export.py` + Rhino 쓰기 | `plan_rhino.json` → 3dm (모형좌표 = (5179 + C)/2, z·높이도 1/2) |
| 9 | `s9_tracking.py` | 결정 추적표 |

정합(스케치 → 3dm 경계)은 `work/20261005_plan_sketch/scripts/fit.py`.
