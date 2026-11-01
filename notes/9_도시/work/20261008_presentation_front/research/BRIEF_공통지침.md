# 공통 지침 — 발표 앞부분(현황·계획 방향) 제작용 하위 작업

작성 2026-10-08. 이 문서는 하위 작업자(에이전트)가 가장 먼저 읽는다. 모르는 것은 추측하지 말고 "확인 불가"로 적는다.

## 0. 무엇을 만드는가

구 경주역 폐역 부지 도시계획 발표자료의 **앞부분(실제 계획안 설명 이전: 경주 맥락 · 대상지 개요 · 현황 진단 · 상위계획 · 선례 · 계획 방향)**을 PPT로 만든다. 목적은 "본 계획의 방향이 현황 자료에서 자연스럽게 도출된다"는 점을 근거로 보이는 것이다.
- 통영 폐조선소 응모안(보고서 59쪽 + PT 89쪽)의 구조·설득 방식을 분석한 문서가 있다: `work/20261005_tongyeong_ref_analysis_v1.md`
- 스타일은 5주차 PPT v3(`work/20261005_ppt_refine/5주차_과제_다듬기v3.pdf`, 코드는 `work/20261005_ppt_refine/scripts/pptkit.py`, `build_deck.py`)를 따른다.
- 방향·컨셉·문제 6개·수치는 `work/20261008_presentation_front/20261008_방향컨셉_및_현황파트_정리_v1.md`에 정리되어 있다. **이 문서의 수치와 [T1~T4] 꼬리표, §6 인용 주의 목록을 우선한다.**
- 프로젝트 규칙은 `CLAUDE.md`(루트)에 있다. 특히 §3(출처 등급 T1~T4, 숫자는 출처 없이 쓰지 않는다, 스케일 S1/S2/S3를 섞지 않는다, EPSG:5187) 준수.

## 1. 지켜야 할 것

1. **원본은 건드리지 않는다.** 루트의 PDF·TIF·SHP, `docs/`, `archive/` 원본, `work/` 기존 산출물은 읽기만 한다. 쓰는 곳은 각자 지정된 출력 폴더뿐이다.
2. **수치를 만들지 않는다.** 문서·데이터에서 확인한 값만 쓴다. 두 문서의 값이 다르면 둘 다 적고 어느 쪽이 원문에 가까운지 표시한다. 등급(T1 법정문서 / T2 공공발간·통계 / T3 학술 / T4 언론·2차)을 항상 붙인다.
3. **사용 금지 수치**(정리본 §6): 부산 대연 "2,300가구→1,300명 정착", 황오동 "창업 70건 +45.8%"·"고용 +16.7%", 행복황촌 유동 5,431명(+396%), 주차 "99%가 부설", 비교 대상 수 15/16/18/24. 위 값이 자료에서 보이면 "사용 금지 목록에 해당"이라고 적고 쓰지 않는다.
4. **구 경주역 역사는 등록문화유산이 아니다**(코레일 철도기념물 2013). 대상지 면적은 세 가지다: 시 구상 79,438㎡ [T4, 원문 미확인] / 고시 구역 156,460㎡ [T1] / 본 계획 경계 218,478㎡. 섞어 쓰지 않는다.
5. **좌표계는 EPSG:5187**(Korea 2000 동부원점)이다. 읽자마자 변환한다. 지도는 북쪽이 위(north-up).
6. **문체**: 슬라이드·설명 문장은 통영 보고서 같은 합니다체, 제목·표 머리글은 명사형. 극적·구어 표현(예: "갈랐고", "죽는 구역"), 영어를 직역한 어색한 문장 금지.
7. 한글 콘솔(cp949)에서 유니코드 출력 오류가 난다. 실행 전에 `export PYTHONUTF8=1 PYTHONIOENCODING=utf-8`.
8. 쉘은 Git Bash(POSIX)다. 경로는 슬래시. 한글 경로는 따옴표로 감싼다.

## 2. 환경

- 파이썬(패키지 설치됨): `C:/Users/OFFICE/AppData/Local/Temp/claude/C--Users-OFFICE-Desktop-9---/b98333f0-4ddf-4213-a0db-66cb837b3d35/scratchpad/venv/Scripts/python.exe` — python-pptx, Pillow, numpy, matplotlib, shapely, pyproj, rasterio, tifffile, imagecodecs, PyMuPDF(`import pymupdf`)가 들어 있다. 추가 설치가 필요하면 같은 venv에 `-m pip install`로 한다(네트워크 가능).
- 한글 서체: `Pretendard`(사용자 폰트 폴더 `C:/Users/OFFICE/AppData/Local/Microsoft/Windows/Fonts/Pretendard-*.otf`), 대체 `C:/Windows/Fonts/malgun.ttf`. matplotlib는 `font_manager.fontManager.addfont(경로)`로 등록해 쓴다.
- 대용량 TIF(최대 1.1GB)는 통째로 읽지 말고 rasterio 윈도 읽기·decimated read·`PIL.Image.MAX_IMAGE_PIXELS=None` + draft/축소를 쓴다.
- 작업 폴더(전부 `C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/` 아래):
  - `assets/hist/` 과거 항공사진·지도 크롭 · `assets/doc/` 문서 도판 크롭 · `assets/maps/` 지도 · `assets/photos/` 사진 · `assets/charts/` · `research/` 자료 조사 · `scripts/` 스크립트

## 3. 시각 어휘 (v3 덱과 같게)

| 용도 | 색 |
|---|---|
| 글자 | INK #231F20 · INK2 #4D4D4D · GRAY #6D6E71 · 선 LINE #D1D3D4 · 바탕 TINT #F5F7FA |
| 대상지 경계·강조 | RED #D7191C (경계선은 항상 이 색, 선 굵기 2~3pt) |
| 수치 강조 | BLUE #1F5AA6 |
| 북측·중앙·남측 | #6F9FDC · #A98BD3 · #F4A0C2 |
| 5대 원칙 | 연결 #1F5AA6 · 관문 #F4A0C2 · 근로 #6F9FDC · 정주 #F1D247 · 확산 #A98BD3 |
| 지도 바탕 | 흰색~연회색(#EFEFEF~#D9D9D9) 건물, 하천 #BFD7EA, 녹지 #CFE3B8 — 채도 낮게. 한 장에 색은 3~4개까지 |
| 용도 범주 | 문화·교육·공공 #6f9fdc · 상업·업무 #e4573a · 창조산업 #a98bd3 · 여가·체육 #2fab9d · 주거 #f1d247 · 판매·음식 #f4a0c2 · 교통·방문자 #c6c6c6 · 역사유산 #c9742f · 오픈스페이스 #9fd36b |

지도 라벨은 한글 Pretendard 계열, 슬라이드에서 읽히도록 **지도가 슬라이드의 절반 크기로 놓여도 본문 라벨이 9pt 이상으로 보이게** 크게 쓴다(그림 폭 약 6in 기준). 범례·축척·방위(N 화살표)를 넣고, 하단 출처 줄은 그림 안에 넣지 않는다(슬라이드에서 따로 올린다).

## 4. 부지 기하 (EPSG:5187)

- 계획 경계 218,478㎡: `work/20261005_boundary_check/user_boundary_current_5187.geojson` (남북 약 945m × 동서 약 300m, 중심 약 x=219,780 / y=360,850)
- 고시 구역 156,460㎡: `archive/C_data/processed/gosi2026-8_zone_5187.geojson`, 결정도 블록 `gosi2026-8_blocks_5187.geojson`
- 가공된 공간 자료 대부분이 `archive/C_data/processed/*.geojson`(4326 또는 5187)에 있다. 건물·도로·철도·유산·고도지구·용도지역·유동인구 구역 등. `pipeline/`의 `build_public_maps.py`·`build_report_map_stats.py`가 이 자료로 지도를 그린 선례다. 이름이 비슷한 자료가 여럿이면 가장 최근 것을 쓰고 어느 것인지 기록한다.
- 국토지리정보원 연속수치지도: `대지/(B020)연속수치지도_202609132098`, 수치지도 DXF: `대지/수치지도/`
- 기존 분석 지도: `work/maps/map10~map20_*.png`(참고용, 팔레트가 다르므로 그대로 쓰지 않는다)

## 5. 결과 보고

작업이 끝나면 최종 응답에 (1) 만든 파일 목록과 각 파일이 무엇인지, (2) 만들지 못한 것과 이유, (3) 사용 시 주의(정합 오차, 등급, 확인 필요 항목)를 400단어 안으로 적는다. 파일 목록은 출력 폴더의 `MANIFEST.csv`(file, 설명, 원자료 경로, 쪽/연도, 가로x세로 px, 비고)에도 남긴다.
