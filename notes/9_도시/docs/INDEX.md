# docs/ 인덱스

claude.ai 프로젝트 **"city plan"** 에서 이관한 정본 지식 33건.
원본은 프로젝트에도 그대로 남아 있다. 이 폴더는 **읽기 전용**으로 취급한다 — 수정이 필요하면 새 파일을 만들고 여기에 한 줄 추가한다.

이관일: 2026-09-13

---

## 00_foundation — 방법론·이론·기술 레퍼런스 (9)

| 파일 | 내용 | 언제 읽나 |
|---|---|---|
| `01_Data_Ontology_and_Sources.md` | 도시 데이터 온톨로지 설계 + 하이브리드 수집 체계 (V-World/NSDI/OpenSky/Sentinel), Pydantic 검증 | 데이터 스키마를 정할 때 |
| `02_Urban_Analysis_Theories.md` | 공간구문론(통합도·선택도·VGA), 도시형태학, 심볼릭+연결주의 하이브리드 AI, GNN | 분석 방법을 고를 때 |
| `03_AI_Simulation_and_Prediction.md` | Hybrid AI(Claude=Architect / Gemini=Eyes), Panoptic Detection, 행위기반 모델링 | 실시간 분석 레이어 설계 |
| `04_Program_Design_and_UIUX.md` | FastAPI + WebSocket 허브, React + Mapbox GL, 시나리오 플레이어, LUI+GUI | 프론트엔드/백엔드 구조 |
| `city_planning_data_taxonomy.md` | **10대 데이터 분류 체계** + 계획단계×데이터 매트릭스 + 핵심 도구 요약 | 무엇을 모아야 하는지 막힐 때 |
| `city_planning_learning_roadmap.md` | 거장들의 학습 DNA(Howard·Jacobs·McHarg·Gehl) + 5단계 커리큘럼 + 시대별 필독서 | 이론 배경 보강 |
| `gemini_claude_hybrid_ai_stack.md` | 두 모델 연결 3가지 방법(clink / bash wrapper / Composio MCP), 비용 분석 | 모델 라우팅 설계 |
| `URBANIS_기술레퍼런스_14개_분석전통.md` | **14개 분석 전통 총람** — 공간구문론부터 실시간 파이프라인까지, 도구·논문·한국 사례 | 기법 선택의 1차 레퍼런스 |
| `연구_강접약접_창의적데이터조합_프로그램기획.md` | 도시의 강접/약접을 4축으로 재정의 → urbanis 스키마 확장 → 통합 인덱스 | 진단 프레임을 짤 때 |

## 10_gyeongju — 구경주역 부지 직접 자료 (2)

| 파일 | 내용 |
|---|---|
| `구경주역_부지_자료_아카이브_설계.md` | **가장 먼저 읽을 것.** 현황 앵커 타임라인, T1–T4 출처 등급, 3중 스케일(S1/S2/S3), 5개 코퍼스(A–E), 아카이브 폴더 구조, 8주 로드맵, 자동화 스크립트 목록, 함정 |
| `구경주역_4대전략_벤치마킹_김민승.md` | 4-2 STUDIO-B 학생 보고서 분석 — 4대 전략(선형축/앵커/P+R/저층입체) + 짚어야 할 긴장 5가지 |

## 20_cases — 사례 데이터베이스·심층 분석 (4)

| 파일 | 내용 |
|---|---|
| `구경주역_사례_데이터베이스.md` | **E 코퍼스 전체** — 국내 폐선·폐역 21 / 도심공동화 13 / 역사도시 6 / 근린재생 실패 4 / 해외 폐선·역세권 24 / 해외 역사도시 7 / 산업유산·실패 11. 유사도 ●●●~● + 검증 [S]/[K] |
| `구경주역_참조사례_안동_우메코지.md` | 구 안동역(1단계 문법) · 교토 우메코지(29년 4단계 순서) 심층 + 세 부지 비교표 |
| `구경주역_도심공동화_사례_부산_전주_울산.md` | 부산(공동화를 만들지 않은 설계) / 전주(되돌림) / 울산(반례) + 경주에 주는 5가지 |
| `사례심층_광주_푸른길공원.md` | 축(軸)의 사례 — "건물이 방향을 바꿨다", 연속성 지표, 운영 조직((사)푸른길) |

## 30_data — 데이터 소스·지표 구현 (9)

| 파일 | 내용 |
|---|---|
| `구경주역_확장_소스_카탈로그.md` | **1차 목록의 누락 6개 층(G1–G6)** — 시간축 / 법정 쇠퇴진단 / 재해·지질 / 실사용 프록시 / 미시 물리 인프라 / 유산도시 제도·방법론. + 착수 순서 10가지 |
| `daegu_free_data_catalog.md` | 대구 무료 데이터 120+ (A~M 분류, URL·형식·비고) — 경주에도 대부분 그대로 적용 |
| `daegu_redevelopment_data_guide.md` | 데이터 소스 10대 카테고리 + Python 전처리 코드 3종 + 7대 분석 맵 + 5대 전략 |
| `Korean_Urban_Data.md` | 전국 공통 프레임 — 4축 설계, API vs 크롤링, 유지보수, 분류 체계, 이론 프레임워크 |
| `연구_공통공간단위_표준격자_스키마.md` | 1km 표준 격자 + 리샘플링 변환 규칙 + 도시 공통 분석 스키마(Grid/Indicator/Observation/Metadata) |
| `연구_지표세트_At_rhot_Ht_구현.md` | A_t(도시화 면적) / ρ_t(평균 밀도) / H′_t(상대 엔트로피) 수식 + Python pseudo-code |
| `연구_궤적시각화_스캐터_레이더.md` | A–ρ–H′ 궤적 스캐터+화살표, small multiples, 두 도시 레이더 비교 |
| `연구_SGIS파일파서_df_metrics.md` | SGIS 실제 다운로드 포맷 기준 파일 파서 (※ 검색 인덱스로 재구성 — 원본 대비 4장 이후 축약) |
| `연구_Seoul_sample_endtoend_15분접근성.md` | 서울 15분 보행 접근성 end-to-end 미니 시나리오 (폴더 구조·스키마·실행 스크립트) |

## 40_engine — 최적화 엔진 (1)

| 파일 | 내용 |
|---|---|
| `구경주역_최적화엔진_Part5.md` | **엔진 설계 정본.** 기각한 접근과 이유 / 생성 파이프라인 S0–S4 / 목적함수 5개 / 계산 전략(대리모델) / 예산·도구 / phasing MILP / `gjplan` 툴 구조 / 12주 구현 순서 / 실패 방식 |

## 50_artifacts — HTML 대시보드·리서치 (7)

브라우저로 직접 열어 본다.

| 파일 | 내용 |
|---|---|
| `urbanis_data_architecture.html` | **가장 실용적.** 행정코드=만능 JOIN 키, 7대 데이터 카테고리별 소스표, 통합 파이프라인, 지도 레이어 스택 8층, 필요 API 키 9종, Grasshopper/Unity 연계 |
| `urban_analysis_overview.html` | 14개 분석 기법 카드 (근거 수준·도구·대구 사례·기법 간 연결) |
| `urbanis_benchmark_analysis.html` | 벤치마크 플랫폼 12선 + 기능 매트릭스(14×8) + 갭 분석 + 포지셔닝 맵 |
| `urbanis_creative_data_research.html` | **12가지 창의적 데이터 레시피** — 프록시 데이터 조합으로 숨은 증상 드러내기 |
| `urbanis_dual_scale_feasibility.html` | 도시 스케일 + 건축물 스케일 IFC 플랫폼 실현가능성, 기술 스택, 14~20개월 로드맵 |
| `urbanis_dashboard.html` | URBANIS UI 목업 (레이어 패널·맵 HUD·분석 패널·커맨드 바) |
| `GEMINI_urbanis_dashboard.html` | Gemini가 만든 대안 UI 목업 (Tailwind 기반) |

## 90_raw — 원본 (1)

| 파일 | 내용 |
|---|---|
| `대화기록.md` | 도시ai 프로젝트 대화 기록 시스템 (2026-04-22 시작) |

---

## 이관되지 않은 것

claude.ai 프로젝트 "city plan"에는 아래 PDF 2건이 **파일 업로드**로 남아 있다. 원본 바이너리는 이 폴더로 옮기지 못했으므로, 필요하면 claude.ai 프로젝트 패널에서 직접 내려받아 `archive/D_literature/`에 넣는다.

- `내용 보강을 위한 심층 연구 방법.pdf`
- `How to Plan a New City from Scratch_ A ....pdf`

## 파일명이 바뀐 것

원본 제목이 문장형이라 파일명을 정리했다. 각 파일 상단에 원본 제목을 표기해 두었다.

| 원본 | 현재 |
|---|---|
| `첨부한 파일을와 여러 논문,웹 서치를 바탕으로 …` | `00_foundation/연구_강접약접_창의적데이터조합_프로그램기획.md` |
| `공통 공간단위·스키마 연구_연구질문_ …` | `30_data/연구_공통공간단위_표준격자_스키마.md` |
| `위 지표 중에서 "실제로 먼저 구현해볼 세트 …` | `30_data/연구_지표세트_At_rhot_Ht_구현.md` |
| `도시별 A_t–ρ_t–H′_t 궤적을 시각화하는 패턴 …` | `30_data/연구_궤적시각화_스캐터_레이더.md` |
| `SGIS 실제 다운로드 포맷 … df_metric` | `30_data/연구_SGIS파일파서_df_metrics.md` |
| `"Seoul sample"을 가정한 end‑to‑end 미니 시나리오 …` | `30_data/연구_Seoul_sample_endtoend_15분접근성.md` |
| `compass_artifact_wf-a2cc0c68-….md` | `00_foundation/URBANIS_기술레퍼런스_14개_분석전통.md` |
| `Korean Urban Data.md` | `30_data/Korean_Urban_Data.md` |
