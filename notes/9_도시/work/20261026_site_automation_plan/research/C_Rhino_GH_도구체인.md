# C. Rhino 8 + Grasshopper + Python 도구체인 조사·비교 — 구경주역 대지 자동화

- 작성일 2026-10-26. 위치 `C:\Users\OFFICE\Desktop\9_도시\work\20261026_site_automation_plan\research\C_Rhino_GH_도구체인.md`
- 이 문서가 답하는 질문: Forma로 할 수 없는 단계(사용자 축 → 도로망 → 가구 → 획지 → 용도별 매스 → 환경 평가 → 다목적 최적화 → 대안 여러 개)를 **Rhino 8 + Grasshopper + Python**으로 구현할 때 어떤 도구를 어떤 구조로 묶어야 하는가.
- 함께 읽은 저장소 문서: `work/20261024_forma_method/데이터기반_도시설계_실행모델_v1.md`(§2 결정변수·§3 목적·§7 역할 분담), `research/02_Forma_기능_데이터_반입.md`, `work/20261011_masterplan_rough/README.md`(D0 사용자 축), `CLAUDE.md` §3·§4·§7.
- 등급: [T1] 법령·고시 / [T2v] 개발사·배포처 공식 문서(McNeel 개발자 문서, Ladybug 문서, PyPI 메타데이터, GitHub 릴리스, 배포 페이지) / [T3] 학술 / [T4] 포럼·food4rhino 목록·2차 자료 / [산정] 이 문서에서 직접 계산·측정 / [가정] / [판단] / 「확인 대기」. 웹 자료 확인일은 모두 **2026-10-26**입니다. food4rhino는 직접 열람이 막혀(403) 검색 요약을 경유했으며, 그 경우 「검색 요약 경유」라고 적었습니다.
- 원본 파일은 읽기만 했습니다. 이 문서와 측정 스크립트 `research/bench_shapely_25d_20261026.py` 외에 새로 만든 파일은 없습니다.

---

## 0. 결론 요약

1. **권장 1안 — 「Python 엔진 + Rhino 검토」 구조입니다.** 생성(축 → 도로·가구 → 획지 → 매스)·평가(f₁~f₅, 2.5D 일조)·최적화(pymoo NSGA-III)를 시스템 Python 3.12에서 돌리고, Rhino 8은 ① 입력 정리(경계선·사용자 축 레이어) ② 대안 A–E 3dm 검토·손 조정 ③ 최종 5안 정밀 환경 검증(Ladybug·Eddy3D 또는 Forma·NoiseModelling)만 맡습니다. 저장소 판단 「Rhino는 최적화 루프 밖」「제약 = 불가능」「가중치 금지」를 구조적으로 지키는 유일한 조합입니다 [판단].
2. **대안 1안 — 「Grasshopper + Tunny(NSGA-III)」입니다.** Tunny는 Optuna 기반 GH 최적화 컴포넌트로 NSGA-III 샘플러와 제약 처리를 갖추고 Rhino 8(net7.0) 빌드가 있습니다 [T4]. 다만 Rhino가 루프 안에 들어가므로 저장소 판단과 어긋나며, v1은 비공개·상용(기본 기능 무료) [T2v]입니다. 사용자가 GH 화면에서 직접 실험할 때의 **비교·교육용**으로 둡니다.
3. **측정값 [산정].** 실제 경계선(228,024.8 단위²)에서 shapely 2.5D 파이프라인 1회: 축 → 도로·가구 2.7 ms, 획지 분할(OBB 재귀 + 접도 검사) 39.6 ms, 용도별 매스 22.1 ms, **생성 합계 중앙 62 ms**. 동지 09–15시 옥외 일조(격자 5 m·10분 간격, 37 벡터·약 6~7천 점) 1.27 s, 정밀(격자 2 m·5분, 73 벡터·40,915점) 2.27 s. 6만 회(개체 200 × 세대 300) 환산 시 생성만 약 62분, 일조 포함 단일 프로세스 약 22시간 → 병렬이면 하룻밤 안입니다.
4. **Rhino 8 내장 CPython은 3.9.10입니다** [산정, 로컬 확인]. 최신 pymoo 0.6.2(Python ≥3.10)·shapely 2.2(≥3.11)·cityseer 5.8(≥3.10)·momepy 1.0(≥3.12)은 Rhino 8 안에서 설치되지 않습니다 [T2v, PyPI]. Rhino 안에서 쓰려면 pymoo 0.6.1.5·shapely 2.0.7로 고정해야 하고, 이것이 엔진을 Rhino 밖에 두는 실무적 이유이기도 합니다.
5. **대지 3dm의 단위 설정이 「밀리미터」인데 좌표값은 미터입니다** [산정]. 경계 면적 228,024.8 단위², 긴 변 약 948 단위. 이 상태로 Ladybug를 돌리면 기본 오프셋이 `0.1 / conversion_to_meters()` = 100 단위(= 실제 100 m)가 됩니다 [산정, 설치된 LB Direct Sun Hours 코드 확인]. Forma Rhino add-in·Eddy3D도 단위를 따르므로 **작업 사본에서 단위를 미터로(축척 변경 없이) 바꾸는 것이 첫 작업**입니다. 원본은 건드리지 않습니다.
6. **GH 안의 다목적 최적화기는 모두 Rhino 8 상태가 불완전합니다.** Wallacei X는 배포 페이지가 Rhino 6·7 기준이고 Rhino 8 사용자 보고는 「대체로 동작·일부 표시 오류」 [T4]. Octopus는 Rhino 8 설치 문의에 답이 없습니다 [T4]. Opossum 3.1.1은 Rhino 8 완전 호환을 공지했으나 NSGA-III는 없습니다 [T4·개발자 공지]. Galapagos(내장)는 단일 목적이고 제약을 페널티로만 넣을 수 있어 저장소 판단과 정면으로 어긋납니다 [T4·개발자 답변].
7. **획지 분할은 새 설치 없이 가능합니다.** OBB 재귀 분할은 shapely만으로 구현했고(측정 39.6 ms), straight skeleton 방식은 이미 설치된 Ladybug Tools에 `ladybug_geometry_polyskel`(Felkel–Obdržálek 알고리즘, Python 2.7/3 겸용)이 들어 있습니다 [산정, 로컬 확인; T2v PyPI]. DeCodingSpaces PLOT GENERATION은 마지막 배포 2021.10·요구사항 Rhino 6이라 Rhino 8은 확인 대기입니다 [T2v].
8. **환경 평가의 공백은 바람·소음·공간 UTCI입니다.** Ladybug Direct Sun Hours·View Percent(Sky View)는 CAD 광선 교차라 Radiance 없이 돌고, Direct Sun Hours는 벡터별 0/1 행렬(int_mtx)을 내므로 「동지 연속 2시간」 판정이 가능합니다 [T2v]. Incident Radiation은 하늘 행렬에 Radiance `gendaymtx`가 필요한데 이 컴퓨터의 Ladybug Tools에는 Radiance·OpenStudio가 설치돼 있지 않습니다 [산정, 로컬 확인]. Butterfly는 2019년 이후 유지보수가 끊겨 Rhino 8 비지원 [T4]. 바람은 Eddy3D(Rhino 8 Win 설치본 2026-02-10 [T4, 검색 요약 경유]) 또는 Forma 위임, 소음은 GH 안 표준 도구가 없어 NoiseModelling(CNOSSOS-EU, Java) 외부 실행입니다 [T2v].

---

## 1. 전제 — 저장소 판단·설치 상태·입력 파일

### 1.1 저장소 판단을 도구 평가 기준으로 옮긴 것

| 저장소 판단(CLAUDE.md §3·§4) | 도구 평가에서의 뜻 | 표의 열 |
|---|---|---|
| 규칙기반 생성 + NSGA-III | 생성은 파라미터로 추적되는 규칙, 최적화기는 다목적(4~5목적) 지원 | 다목적·NSGA-III |
| 목적함수 가중치 금지 | 단일 목적 최적화기(가중합 필요)는 본 루프에 쓸 수 없음 | 가중치 |
| 제약 = 불가능(buildable 마스크) | 생성 단계에서 잘라내거나, 최적화기가 「실현 가능 우선(feasibility first)」으로 비교해야 함. 페널티만 받는 도구는 부적합 | 제약 |
| Rhino는 최적화 루프 밖 | GH 정의를 매 평가마다 푸는 구조는 원칙 위반. 예외는 비교 실험 | 루프 위치 |
| 생성 결과 그대로 제출 금지 | 3dm 왕복(내보내기 → 손 수정 → 파라미터 역반영)과 추적표가 가능해야 함 | 왕복 |
| 차원 ≤50 | 사용자 축을 유전자에 넣을 때 차원 증가를 셈 | §2.5 |

### 1.2 이 컴퓨터의 설치 상태(2026-10-26 확인)

| 항목 | 상태 | 근거 |
|---|---|---|
| Rhino | 8.35.26251.13001 | [산정] `C:\Program Files\Rhino 8\System\Rhino.exe` 파일 버전 |
| Rhino 8 내장 CPython | 3.9.10, 추가 패키지 없음(pip·setuptools·wheel·certifi만). 가상환경 2개(`default-…`, `pointcloud_fit-…`) | [산정] `~/.rhinocode/py39-rh8` |
| GH 내장 | Galapagos, Kangaroo2, GhPython(IronPython), RhinoCode(Python 3·C#) | [산정] `Plug-ins/Grasshopper/Components` |
| GH 라이브러리 | Ladybug Tools 1.8(컴포넌트 메시지 1.8.0, ladybug-rhino 1.42.11; honeybee·dragonfly 포함), Anemone, Pufferfish, LunchBox, Human, Bifocals, treesloth, Sasquatch, Blindfold, BlueOrange, atit, podghbutton | [산정] `%APPDATA%/Grasshopper/Libraries` |
| Ladybug 엔진 | `~/ladybug_tools`에 `python`·`resources`만 있음 → **Radiance·OpenStudio(EnergyPlus) 없음** | [산정] |
| Ladybug 동봉 Python 패키지 | `ladybug_geometry_polyskel`(straight skeleton), `numpy 1.26.4`, `uwg` 등 | [산정] |
| yak 패키지 | Weaverbird, PetersTools, eleFront legacy, Rhino-MCP-Platform, PRKNG_sqr, byRhinoGadget. **Hops 없음** | [산정] |
| 다목적 최적화 플러그인 | 없음(Wallacei·Octopus·Opossum·Tunny 모두 미설치) | [산정] |
| 시스템 Python | 3.12.10, numpy 2.5.3, shapely 2.2.0(GEOS 3.14.1), rhino3dm 8.35.0. pymoo·scipy·networkx·geopandas·lightgbm·ortools 없음 | [산정] |
| CPU | 논리 32개(i9) | [산정] |

### 1.3 입력 파일 상태 — 단위 불일치

`구경주역_최종대지_대지경계선.3dm`(36 MB)을 rhino3dm으로 읽은 결과입니다 [산정].

| 항목 | 값 | 뜻 |
|---|---|---|
| 레이어 | 대지경계선 / 지형_대지 / 지형_도로 / 지형_인도 / 지형_경계석 / 지형_하천 | 저장소 레이어 규약(`BOUNDARY`·`FIXED_*`·`ANCHOR_*`, CLAUDE.md §7)과 이름이 다름 → 읽기 단계에서 별칭 표로 대응 |
| 경계선 | PolylineCurve 1개, 꼭짓점 126, 닫힘·유효 | 면적 228,024.8 단위², 둘레 2,368.4 단위 |
| 경계 bbox | x 1,166,702.2–1,167,013.2, y 1,761,153.7–1,762,101.7 | rough 프레임(로컬 + (1,166,600, 1,761,100)) 값과 일치 |
| 긴 변 방향 | 최소 외접 직사각형 긴 변이 x축에서 90.69° | 거의 정남북 |
| **모델 단위** | **Millimeters**, 절대 허용오차 0.001 | 좌표값은 미터 상당(면적 228,025㎡ 일치) → 단위 설정만 잘못됨 |
| 지형_대지 z | −63.8 ~ 3.5 단위 | plan 0 ↔ ctx 144.1 상대 표고로 추정 [가정] |
| EarthAnchorPoint | 미설정 | Forma·Ladybug 지리 위치 자동 설정 불가 → 위도·경도 수동 입력 |

**영향.** Ladybug는 문서 단위를 읽어 미터 환산을 합니다. 설치된 `LB Direct Sun Hours.py` 109–110행은 오프셋 기본값을 `0.1 / conversion_to_meters()`로 정하므로 mm 문서에서는 100 단위가 되고, 좌표가 미터이므로 실제 100 m 위에서 일조를 재게 됩니다 [산정, 코드 확인]. Forma Rhino add-in·Eddy3D·IFC 내보내기도 단위를 따릅니다 [가정]. 처리: 원본은 그대로 두고, 작업 사본에서 `Units` 명령으로 미터로 바꾸되 「축척 변경 안 함」을 선택합니다. 1.48 GB 콘타 모델(1/2 축척)의 단위 설정은 열지 않아 **확인 대기**입니다.

### 1.4 Python 버전 제약 — Rhino 안과 밖

| 패키지 | 최신(확인일) | 최신의 Python 요구 | Rhino 8(3.9)에서 쓸 수 있는 마지막 판 | 근거 |
|---|---|---|---|---|
| pymoo | 0.6.2 (2026-06-28) | ≥3.10 | 0.6.1.5 (2025-05-26, cp39 win_amd64 휠 있음) | [T2v] PyPI |
| shapely | 2.2.0 | ≥3.11 | 2.0.7 (2025-01-31, cp39 휠 있음). 2.1.0부터 ≥3.10 | [T2v] PyPI |
| cityseer | 5.8.0 | 3.10–3.14 | 확인 대기(구판) | [T2v] PyPI |
| momepy | 1.0.0 (2026-07-02) | ≥3.12 | 확인 대기(구판) | [T2v] PyPI |

- Rhino 8 ScriptEditor는 스크립트 머리의 `# r: 패키지==버전`으로 pip 설치, `# venv: 이름`으로 스크립트별 환경을 씁니다. 설치 실패 시 환경이 Invalid로 표시되고 Rhino 재시작이 필요합니다 [T2v, developer.rhino3d.com Python Package Environments]. 시스템 pip로 설치한 패키지는 Rhino에서 보이지 않습니다 [T4].
- Rhino 9(WIP/BETA)는 Python 3.13(`~/.rhinocode/py313-rh9`)로 옮겼고 3.13.x에 고정됩니다 [T4, McNeel 직원 공지 2025-05-29·2026-07]. Rhino 8이 3.13을 받는다는 공지는 없습니다(확인 대기).
- **판단**: 엔진 코드를 Rhino 8 안에서 돌리려면 구판 고정이 필요하고, 그 상태로는 최신 cityseer·momepy를 못 씁니다. 엔진은 시스템 Python 3.12 가상환경에 둡니다 [판단].

---

## 2. 단계 (1) 축 기반 도로망 — 축 곡선 → 폭별 오프셋 → 도로 면·가구 면

### 2.1 입력: 사용자 축과 도로 위계

README D0·v11에 적힌 사용자 축과 폭입니다(설계 결정, 이 문서는 바꾸지 않음).

| 축·도로 | 성격 | 폭 | 출처 |
|---|---|---|---|
| ① 남북축(대릉원 ↔ 북천·황성공원) | 중앙 남북 보행축 | 30 m(단면 v5 실폭) | README v5·D0 |
| ② 동서축(성동시장 ↔ 성동리 전랑지) | 40 m 선형공원 | 40 m | README D0 |
| ③ 역사유적축(사선, 미추왕릉 방향) | 사선 보행축 | 확인 대기(연장 286 m) | README D0·v11 |
| ④ 향일문 조망 보행로 | 가구 사이 보행로 | 8 m | README D0 |
| 화랑로 연결 동서 도로 | 차도 | 20 m | README D0·v11 |
| 북측 차도 | 차도 | 13 m(폴리곤 실측 12.8 m) | README v11 |
| 동·남측 외곽도로 | 차도 | 10~12 m | 사용자 요청 요지 |
| 차량 진입 7곳 | 접속점 | — | README v11 |

**레이어 규약 제안 [판단].** 작업 사본에 `BOUNDARY`(= 대지경계선) 1개, `FIXED_AXIS_NS`·`FIXED_AXIS_EW`·`FIXED_AXIS_HIST`·`FIXED_PATH_VIEW8`·`FIXED_ROAD_*`(축 중심선, 사용자 문자열 `width`·`class`), `ANCHOR_ENTRY`(진입 7점)를 둡니다. 원본 레이어명은 `config.yaml`의 별칭 표로 읽습니다.

### 2.2 오프셋·도로 면·가구 면 만드는 방법 네 가지

| 방법 | 절차 | 교차부 처리 | 장점 | 약점 | 근거 |
|---|---|---|---|---|---|
| A. GH 기본 컴포넌트 | 축 Extend → Offset ±W/2 → Loft 또는 Boundary → Split Surface/Region Difference로 대지 분할 → 면 중심과 도로의 거리로 도로·가구 분류(거리 0 = 도로) | Split 결과에 교차부 면이 따로 생기고 거리 분류로 도로에 포함 | 시각적, 사용자 숙련 | 축이 많으면 정의가 커지고 분류 규칙이 깨지기 쉬움 | Columbia CDP 튜토리얼 [T4] |
| B. Clipper2GH | 축 폴리라인 → Offset(open, 끝 처리 butt) → Union → 대지와 Difference | 합집합에서 자동 생성 | 빠름(같은 작업 Rhino 8 Offset 4분 vs Clipper2 0.5초 보고) | 폴리라인 전용, 오프셋 「스파이크」 버그 보고, Clipper1과 JoinType·EndType 값이 다름 | food4rhino 1.3.2(2026-03-26, Rhino 8 Win·Mac) [T4, 검색 요약 경유]; 포럼 [T4] |
| C. RhinoCommon(ScriptEditor) | `Curve.Offset` 양쪽 → 닫힌 띠 → `Curve.CreateBooleanUnion` → `CreateBooleanDifference`(대지) 또는 `CreateBooleanRegions` | 불리언 합집합에서 자동 | NURBS 축(곡선 축)도 그대로 | Rhino 8 초기 Offset 지연 버그(RH-84100)는 SR14에서 수정 | 포럼 McNeel 직원 답변 [T4] |
| D. shapely(Rhino 밖) | `LineString.buffer(W/2, cap_style="flat", join_style="mitre")` → `union_all` → `site.difference(roads)` → 가구 폴리곤 | 합집합에서 자동. 가각전제는 가구에 `buffer(-r).buffer(+r)` 또는 모서리 삼각형 차감 | **2.7 ms**(측정), 벡터·수치 출력이 바로 면적표로 | 곡선 축은 폴리라인 근사(0.5 m 간격이면 충분 [가정]) | [산정] 측정 스크립트 |

- **교차부 규칙**: 도로 띠를 합집합으로 만들면 교차부가 자동으로 생기므로 별도 교차 처리 로직이 필요 없습니다. 남는 일은 ① 가각전제(건축법 시행령 제31조①의 도로 너비·교차각별 길이 [T1, 표 값 대조 대기]) ② 보행축(30·40·8 m)과 차도의 구분(면 속성) ③ 경계 밖 원화로·화랑로 횡단점과의 연속성 검사(실행모델 §2.9 「횡단 통과폭」 제약)입니다.
- **곡선 축**: ③ 역사유적축이 직선이면 D로 충분합니다. 곡선이면 Rhino에서 0.5 m 간격 폴리라인으로 내보내 D에서 씁니다 [판단].

### 2.3 판정

권장은 **D(shapely)**, Rhino 검토 화면의 재현은 C입니다. A·B는 사용자가 GH에서 대안을 직접 그릴 때의 보조 수단입니다 [판단].

---

## 3. 단계 (2) 가구 → 획지 분할

### 3.1 알고리즘

| 방식 | 내용 | 강점 | 약점 | 근거 |
|---|---|---|---|---|
| OBB 재귀 분할 | 가구의 최소 외접 직사각형(OBB) 긴 변에 수직으로 자르기를 목표 면적 이하가 될 때까지 반복. 분할선 위치에 ±10% 지터 | 구현 단순, 정형 가구에 자연스러운 직사각 획지 | 사선·삼각 가구에서 접도 없는 안쪽 획지가 생길 수 있음 → 접도 검사로 거부 | Vanegas 외 2012, Computer Graphics Forum 31(2pt3):681–690 [T3] |
| Straight skeleton 분할 | 가구 경계의 straight skeleton으로 각 가로변에 붙은 띠(strip)를 만들고, 띠를 전면 폭 규칙으로 잘라 획지화 | 모든 획지가 가로에 접함(접도 자동 보장), 불규칙 가구에 강함 | 띠 경계가 사선으로 꺾여 획지 모양이 나쁠 수 있음 → 모서리 정리 규칙 필요 | 같은 논문(skeleton 방식) [T3]; Felkel·Obdržálek 1998 알고리즘 [T3, polyskel 설명 경유] |
| 격자·Voronoi | 고정 격자 또는 점 생성 후 Voronoi | 빠름 | 법적 접도·전면폭 통제가 어려움 | [판단] — 채택 안 함 |

- Vanegas 2012는 두 방식 모두 **사용자 지정 분할 속성(면적·전면 폭·방향)**으로 통제하고, 편집 전후에 개별 획지를 대응시키는 「지속성(persistence)」을 장점으로 듭니다 [T3]. 이 지속성은 §9.3의 3dm 왕복(손 수정 → 파라미터 역반영)에서 획지 ID를 유지하는 데 필요한 성질입니다.
- **규칙(제약으로 둘 것)**: 접도 2 m 이상(건축법 제44조 [T1]); 전면 폭 하한·깊이/전면 비 상한 [가정, θ_lot 범위]; 획지 면적 하한. 위반 분할은 「거부 후 다른 축으로 재시도 → 실패하면 분할 정지」로 처리해 페널티가 생기지 않게 합니다 [판단].

### 3.2 도구

| 도구 | 기능 | Rhino 8 | 설치·비용 | 판단 | 근거 |
|---|---|---|---|---|---|
| shapely OBB 재귀(자체) | 위 OBB 방식 + 접도 길이 검사 | 무관(Rhino 밖) | 설치 없음 | **채택**. 측정 39.6 ms(최대 75.6 ms), 가구 6–13개 → 획지 50–121개 | [산정] |
| `ladybug_geometry_polyskel` | straight skeleton, core/perimeter 다각형 추출 | Ladybug 동봉(설치됨) / 시스템 Python엔 `pip install ladybug-geometry-polyskel` | 무료(라이선스 확인 대기, Q8) | **skeleton 방식 채택 후보** | [T2v] PyPI; [산정] 로컬 |
| Honeybee Straight Skeleton 컴포넌트 | 위 패키지의 GH 컴포넌트 | 설치된 LBT 1.8에 포함 | 무료 | Rhino 검토 화면용 | [T2v] docs.ladybug.tools |
| CGAL(compas_cgal 등) | straight skeleton·오프셋 | — | 휠 제공 여부 확인 대기 | 보류 | [T2v] CGAL 6.1 문서 |
| DeCodingSpaces PLOT GENERATION | 다각형을 접도·최소 폭을 지키는 획지로 분할 | **확인 대기**(배포 페이지 요구사항 Rhino 6, 마지막 2021.10) | 무료, GPL-3.0 | 비교용. 파라미터는 공개 | [T2v] toolbox.decodingspaces.net |
| Urbano | OSM 반입·Walkscore 등. 획지 분할 기능 없음 | 목록 불일치 | 무료 | 해당 없음 | [T4] |
| Heron | GIS 반입(SHP·래스터·REST). v0.5.x는 Rhino 8 이상 전용 | ● | 무료 | 입력 보조(필요 시) | [T2v] GitHub 릴리스 |
| Elk·Bison | OSM 반입·지형 | 확인 생략 | 무료 | 불필요(NGII·3dm 지형 보유) | [판단] |
| Kangaroo2 | 물리 기반 형태 탐색 | 내장 | — | 분할 도구 아님. 매스 간격 이완 등 보조 | [산정] 로컬 |

---

## 4. 단계 (3) 용도별 매스 유형 — 파라메트릭 규칙과 높이·건폐율 반영

### 4.1 공통 규칙

- 높이: `H = min(L × 4.0 m, height_max(획지))`. `height_max`는 고도지구 20 m, 도로 인접 15 m·3층(경관 가이드라인 해석 A·B 두 벌), 조망 금지면 [T1·가정, 실행모델 §2.6·§2.8]. 층고 4.0 m [가정].
- 건폐율: 밀도 등급표(저 0.45·L2 / 중 0.50·L3 / 고 0.55·L_max)에서 목표 GSI를 받고 [가정, 실행모델 §2.6], 유형별 「깊이·간격」 파라미터를 이분 탐색해 목표에 맞춥니다. 목표가 **상한(GSI_max, 용도지역 조회표)**을 넘는 조합은 생성 단계에서 버립니다(불가능). 목표에 못 미치는 것은 허용하고 결과 GSI를 기록합니다 [판단].
- 공동주택 인동 0.5H(건축법 시행령 제86조③ [T1, 실행모델 §2.9]), 정북 방향 일조 높이 제한(시행령 제86조①, 전용·일반주거지역; 기준 높이 값은 현행 조문 대조 대기 [T1])은 판상·중정형 생성식에 직접 넣습니다.
- 건축선 후퇴 3 m [가정](지구단위계획에서 정할 값).

### 4.2 유형별 생성식

| 유형 | 생성식(획지 P, 후퇴 내접 P′) | 조정 파라미터 | GSI 맞추는 방식 | 주 용도(실행모델 §2.7 u) |
|---|---|---|---|---|
| 가로변 블록 | P′ − P′.buffer(−d), 가로에 접한 변만 남기려면 접도 변 띠와 교집합 | 깊이 d 6–30 m | d 이분 탐색(12회) | u4 상업·업무, u7 혼합 |
| 중정형 | 가로변 블록과 같은 고리, 중정 최소 폭 ≥ H(인동 근사) | d, 중정 최소 폭 | d 이분 탐색 + 중정 폭 하한 검사 | u6 주거, u5 숙박 |
| 판상 | P′의 OBB 장변 평행 바(깊이 12 m), 간격 max(0.5H, 8 m) | 바 깊이, 간격 | 간격이 법정 하한으로 묶이므로 바 수로 맞춤 | u6 주거 |
| 포인트 | P′ 안 18×18 m 정방형 격자, 간격 18 + max(0.5H, 10 m) | 평면 크기, 간격 | 평면 크기 조정 | u5 숙박, u8 모빌리티 허브 |
| 저층 공공 | P′의 축소 사본(√(GSI·A/A′) 배율), L 1–2 | 배율 | 닫힌 식 | u2 공공청사, u3 문화·전시 |

- 측정: 위 5유형을 획지 50–121개에 적용하는 데 **22.1 ms**(최대 43.6 ms) [산정]. 측정 표본의 대지 기준 GSI 0.21–0.36·FSI 0.56–0.97은 **임의 유전자에서 나온 값이라 설계 수치로 인용하지 않습니다**.
- 1층 용도(활성 가로면)는 실행모델 §2.2대로 가로 위계에서 파생합니다. 매스 생성기는 각 동에 `use_ground`·`use_upper` 속성만 붙입니다.
- Rhino 쪽 재현: 같은 규칙을 GH(Offset·Region·Extrude)로 짤 수 있으나, 규칙이 두 군데 있으면 어긋납니다. Rhino에는 엔진이 낸 매스(속성 포함)를 그대로 받아 보여 주는 쪽을 권장합니다 [판단].

---

## 5. 단계 (4) 환경 평가 — 지표별 도구와 1회 소요 시간

### 5.1 지표별 비교

| 지표 | GH 안 도구 | Rhino 밖 도구 | 이 컴퓨터 상태 | 1회 시간 | 루프 위치 | 근거 |
|---|---|---|---|---|---|---|
| 직달 일조 시간 | LB Direct Sun Hours: SunPath 벡터 × 격자점 CAD 광선 교차, `cpu_count`, **int_mtx(점별·벡터별 0/1)** 출력 | shapely 2.5D 그림자(각기둥 그림자 = 바닥면 ∪ 이동면 ∪ 변 스윕 사각형) | LB 설치됨(Radiance 불필요). 2.5D는 측정 완료 | 2.5D: **1.27 s**(5 m·10분, 37벡터·6~7천 점), **2.27 s**(2 m·5분, 73벡터·40,915점) [산정]. LB: 실측 대기 — 문서상 「단순 형상은 빠르나 점·형상이 많으면 확장성 나쁨」 [T2v] | 2.5D는 루프 안(또는 대리모델), LB는 최종 5안 | [T2v] LB 문서; [산정] |
| 일조권 판정(동지 연속 2시간·총 4시간, 인동 0.5H) | int_mtx를 Deconstruct Matrix로 풀어 연속 1의 최대 길이 계산 | 같은 계산을 numpy로(측정 스크립트 `max_run`) | 가능 | 판정 자체는 ms | 루프 안(제약 또는 KPI) | 판정 기준 [판례·T1, 실행모델 §7 승계, 사건번호 확인 대기] |
| 일사량 | LB Incident Radiation(CAD 광선 + 하늘 행렬) | — | **하늘 행렬(LB Cumulative Sky Matrix)이 Radiance `gendaymtx` 필요 → Radiance 미설치** | 실측 대기 | 최종 5안 | [T2v] LB 문서 |
| 하늘 조망률(Sky View) | LB View Percent(view_type 3 SkyExposure·4 SkyView), CAD 광선, Radiance 불필요 | numpy 반구 광선(자체 구현 가능) | 설치됨 | 실측 대기 | 최종 5안(보고 KPI) | [T2v] LB 문서 |
| UTCI | 점 단위: LB UTCI Comfort(EPW 기온·습도·풍속 + MRT). 공간 지도: HB UTCI Comfort Map 레시피(EnergyPlus 표면온도 + Radiance 복사) | — | 점 단위 가능. 공간 지도는 Radiance·OpenStudio 설치 필요 | 공간 지도 수십 분~수 시간 [가정] | 최종 5안(KPI) | [T2v] LB·HB 문서(검색 요약 경유 일부) |
| 바람 | Eddy3D(OpenFOAM, BlueCFD-Core 필요, 원통·상자 영역, 연간 통풍·UTCI) / Butterfly(2019 이후 유지보수 중단, Rhino 8 비지원 → **기각**) | Forma rapid(AI 대리모델, 즉시) / detailed(CFD, 수 분~) — 상대 비교만 | 모두 미설치 | Eddy3D 풍향당 수십 분~수 시간 [가정, 실측 대기]; Forma rapid 즉시 [T4, 02 §2.4] | 최종 5안. 루프 안 불가 | [T3] Kastner·Dogan 2021; [T4] food4rhino·포럼 |
| 도로 교통소음 | **표준 산정식(CNOSSOS 등) 구현 GH 도구 없음**. DeCodingSpaces는 격자 채색만, Pachyderm은 실내 음향 중심 | NoiseModelling(Java 라이브러리, v4.0부터 CNOSSOS-EU, H2GIS/PostGIS) / 루프용 거리 감쇠 근사(numpy) | 미설치(Java 필요) | NoiseModelling 수 분 [가정, 실측 대기]; 근사식 ms | 근사식만 루프 안, NoiseModelling은 최종 5안 | [T2v] NoiseModelling 문서; [T4] 포럼 |
| 보행 네트워크(f₁ NACH Δ, f₅ 300 m 공원 도달) | DeCodingSpaces 중심성(Rhino 6 기준, 8 확인 대기), sDNA_GH(MIT, Rhino 6·7 표기, Windows, IronPython 불가), SpiderWeb(8 확인 대기) | cityseer 5.8(Py ≥3.10), momepy 1.0(Py ≥3.12), networkx | 모두 미설치 | 캐싱 시 0.05 s [Part 5 추정, 실행모델 §3.2]; 실측 대기 | 루프 안 | [T2v] PyPI; [T4] food4rhino·포럼 |

### 5.2 1회 평가 시간 합산과 6만 회 환산 [산정]

| 구성 | 1회(중앙값) | 6만 회 단일 프로세스 | 비고 |
|---|---|---|---|
| 생성 S1·S3·S4 + 면적 KPI | 62 ms | 약 62분 | 측정 |
| + 2.5D 일조(5 m·10분) | 1.34 s | 약 22시간 | 측정 |
| + 보행 네트워크(0.05 s 가정) | 약 1.4 s | 약 23시간 | 네트워크는 [가정] |
| + 조망 f₂ 정직 평가(5–30 s) | 6–31 s | 4–22일 | Part 5 추정. **대리모델(LightGBM) 필수** |

- 병렬: 평가는 독립이라 프로세스 병렬이 됩니다. 논리 32개 중 16 프로세스·효율 70%를 가정하면 일조 포함 약 2시간입니다 [가정].
- GH 루프 안 평가 시간은 정의 구성에 따라 크게 달라 이 문서에서 숫자를 정하지 않습니다(실측 대기). §9.4 첫 주 측정 항목입니다.

### 5.3 판정

- **루프 안**: 2.5D 일조(연속 2시간 판정 포함), 보행 네트워크, 면적·밀도, 소음 거리 감쇠 근사 — 전부 Python.
- **루프 밖(최종 5안)**: LB Direct Sun Hours(1 m 격자·건물 입면 포함 정밀 판정), View Percent, (Radiance 설치 후) Incident Radiation·UTCI 지도, 바람(Eddy3D 또는 Forma), 소음(NoiseModelling 또는 Forma). 2.5D와 LB 결과의 차이는 대안 5개에서 비교해 2.5D 근사의 오차를 보고합니다 [판단].

---

## 6. 단계 (5) 최적화기 비교

### 6.1 GH 안 최적화기

| 도구 | 알고리즘 | 다목적 | 제약 처리 | Rhino 8 | 설치·비용 | 저장소 판단과의 관계 | 근거 |
|---|---|---|---|---|---|---|---|
| Galapagos | GA·담금질(단일 목적) | × | **없음 — 페널티로만**(개발자 답변: 「Galapagos is not a constraint-solver」) | ● 내장 | 없음 | 가중치·페널티가 강제됨 → **본 루프 부적합** | [T4] 포럼(Rutten) |
| Wallacei X | NSGA-II(+ K-means 군집, jMetal) | ○ | 확인 대기(페널티 사용 사례 다수 [T4]) | ◐ 배포 페이지는 Rhino 6·7 기준. Rhino 8에서 Wallacei 2.7 동작·평행좌표 표시 오류 보고 | 무료 | 루프 안. NSGA-III 아님 | [T4] food4rhino 검색 요약; 포럼 |
| Octopus | SPEA-2·HypE | ○ | 확인 대기 | ○ Rhino 8 설치 문의에 확인된 답 없음 | 무료 | 루프 안 | [T4] |
| Opossum 3.1.1 | 단일: RBFOpt·CMA-ES / 다목적: RBFMOpt·MACO·MOEA/D·NSGA-II·NSPSO | ○ | 확인 대기 | ● 「fully compatible with Rhino 8」(2024-07-08) | 무료(라이선스 문구 확인 대기) | 루프 안. 평가가 비쌀 때 모형 기반(RBF) 탐색이 강점 | [T4] 개발자 공지 |
| Tunny | Optuna 샘플러: TPE·GP·**NSGA-II·NSGA-III**·MOEA/D·HypE·SPEA-II·CMA-ES 등 | ○ | ○ 「다목적 + 제약」 지원 표기 | ● Rhino 8은 net7.0 빌드(yak) | v0(오픈, MIT) / **v1 비공개·상용, 기본 기능 무료** — 유료 범위·가격 확인 대기 | 루프 안. NSGA-III·제약은 충족 | [T4] food4rhino 검색 요약; [T2v] GitHub README |
| Anemone | 반복 루프 | — | — | ◐ 「Rhino 8에서 동작」 포럼 답변 | 설치됨 | 최적화기 아님. 배치 실행용 | [T4] |

**Tunny의 알려진 문제.** Python 3 컴포넌트가 든 정의에서 Rhino 내장 `Python.Runtime`과 Tunny 동봉판이 충돌해 최적화가 멈추는 문제가 보고됐고(v1.4.2), 개발자가 2026-08-18 「v1.5.0에서 해결」이라 답했습니다 [T4, 포럼]. 홈페이지는 v1.5.0의 「Run in Separate Process」 옵션을 언급합니다 [T2v]. 실제 동작은 설치 후 확인 대기입니다.

### 6.2 Python 쪽 연결 방식

| 방식 | 구조 | 속도·안정성 | 제약 | 근거 |
|---|---|---|---|---|
| ① 외부 pymoo + 순수 Python 엔진 | pymoo(0.6.2, Py 3.12)가 생성·평가 함수를 직접 호출 | 프로세스 병렬 가능, Rhino 무관. 측정 1.34 s/회 | NSGA-III는 참조 방향(Das-Dennis) 필요. 대부분의 pymoo 알고리즘은 **실현 가능 해를 항상 앞에 두는 parameter-less(feasibility first)** 방식 | [T2v] pymoo.org; [산정] |
| ② pymoo → Rhino.Compute(GH 정의 평가) | Python이 `compute_rhino3d.Grasshopper.EvaluateDefinition`으로 GH 정의를 REST 호출 | HTTP·직렬화 비용 + GH 해석 시간. 같은 정의 반복 호출 시 서버 메모리 증가·시간 초과 보고 | 로컬 Compute는 Hops 설치 시 GH 실행과 함께 뜸. Windows Server 배포는 코어시간 과금 $0.10/코어·시간(교육·상용 라이선스와 병용 불가) | [T2v] Hops 문서·Licensing & Billing; [T4] 포럼 |
| ③ Hops(GH → CPython 함수) | GH가 `ghhops_server`(CPython ≥3.8)의 함수를 컴포넌트처럼 호출 | 자식 프로세스 수·메모리 캐시·비동기 옵션. 오버헤드 수치 공개 없음 | 호출 방향이 GH → Python이라 **최적화 드라이버가 GH 쪽**(Galapagos·Tunny 등)에 남음. Hops 미설치(PackageManager로 무료 설치) | [T2v] developer.rhino3d.com Hops |
| ④ ScriptEditor CPython 안 pymoo | GH Python 3 컴포넌트에 `# r: pymoo==0.6.1.5`, `# venv: gjplan` | GH 해석 스레드를 점유해 UI가 멈춤, 컴포넌트 재진입·취소 처리 필요 [가정]. 3.9 고정 | pymoo 0.6.1.5 cp39 휠 있음. shapely 2.0.7 이하 | [T2v] PyPI·developer.rhino3d.com |

### 6.3 판정

- 본 루프: **① 외부 pymoo NSGA-III**. 저장소 판단 네 가지(NSGA-III·가중치 금지·제약 = 불가능·Rhino 루프 밖)를 모두 충족하는 유일한 선택지입니다 [판단].
- 비교 실험(방법론 비교): Tunny NSGA-III로 같은 문제를 GH에서 돌려 파레토 전선이 같은지 확인하면 「도구를 바꿔도 결론이 같다」는 검증이 됩니다 [판단].
- Galapagos는 쓰지 않습니다. 쓰는 순간 목적을 가중합해야 하고 제약을 페널티로 넣어야 합니다.

---

## 7. 단계 (6) 구조 비교 — GH 중심 vs Python 엔진 + Rhino 검토

| 기준 | (A) GH 중심(GH 정의 + Tunny/Wallacei) | (B) 혼합(pymoo → Rhino.Compute → GH 정의) | (C) **Python 엔진(shapely 2.5D) + Rhino 검토** |
|---|---|---|---|
| 루프 위치 | Rhino 안 | Rhino(headless) 안 | Rhino 밖 |
| 제약 = 불가능 | Tunny는 제약 지원, Wallacei·Galapagos는 페널티 | pymoo feasibility first + GH 생성 단계 마스크 | 생성 단계 마스크 + pymoo feasibility first + 리페어 |
| 가중치 | Tunny·Wallacei 없음 / Galapagos 필요 | 없음 | 없음 |
| 평가 1회 | 실측 대기(GH 해석 + LB 광선) | GH 해석 + HTTP. 메모리 누적 위험 | 측정 1.34 s(일조 포함), 생성만 62 ms |
| 병렬 | 단일 Rhino 인스턴스 | Compute 자식 프로세스 다수 | 프로세스 병렬 자유 |
| 추적성 | 슬라이더 값 기록은 가능, 규칙은 GH 정의 안에 흩어짐 | 같음 | 유전자·규칙·결과가 코드와 CSV로 남음(추적표 직결) |
| 3dm 왕복 | GH 베이크 → 수정 → 슬라이더로 역반영(수동) | 같음 | rhino3dm으로 속성 달린 3dm 출력 → 수정본을 다시 읽어 차이 → `config.yaml`·추적표 |
| 정밀 환경 평가 | 같은 화면에서 LB 바로 | 가능 | 최종 5안만 Rhino로 가져가 LB·Eddy3D |
| Python 버전 | 3.9(Rhino 8) | 3.12 가능 | 3.12 |
| 학습 비용 | 사용자 숙련(낮음) | 높음(Compute·REST·GH 입력 이름 규약 `RH_IN:`) | 중간(코드 작성, Claude 보조) |
| 저장소 판단 정합 | 부분(루프 위치 위반) | 부분(Rhino가 headless로 루프 안) | **전부** |

---

## 8. 종합 비교표 — 설치·비용·Rhino 8 호환·학습 비용·평가 1회 시간·저장소 판단 정합

기호: Rhino 8 호환 ● 공식 확인 / ◐ 사용자 보고 / ○ 확인 대기 / × 비지원 / — 무관. 정합 ● 충족 / ◐ 조건부 / × 위반. 학습 비용은 [판단].

| 단계 | 선택지 | 설치 필요 | 비용 | Rhino 8 | 학습 비용 | 평가 1회 시간 | 저장소 판단 정합 |
|---|---|---|---|---|---|---|---|
| (1) 도로·가구 | GH Offset·Region·Split | 없음 | 0 | ● | 낮음 | 실측 대기 | ◐ 검토용 |
| | Clipper2GH | 필요 | 0 | ◐(1.3.2 Rhino 8 표기) | 낮음 | 빠름(보고 0.5 s/96회 오프셋) | ◐ 검토용 |
| | RhinoCommon(ScriptEditor) | 없음 | 0 | ● | 중간 | 실측 대기 | ◐ 검토용 |
| | **shapely buffer·difference** | 없음 | 0 | — | 중간 | **2.7 ms** [산정] | ● |
| (2) 획지 | **shapely OBB 재귀 + 접도 검사** | 없음 | 0 | — | 중간 | **39.6 ms** [산정] | ● |
| | ladybug_geometry_polyskel(skeleton) | 시스템 Python엔 pip 1개 | 0 | ●(LBT 동봉) | 중간 | 실측 대기 | ● |
| | DeCodingSpaces PLOT GENERATION | 필요 | 0(GPL-3) | ○(Rhino 6 기준) | 낮음 | 실측 대기 | ◐ 비교용 |
| (3) 매스 | **shapely 유형 생성식 5종** | 없음 | 0 | — | 중간 | **22.1 ms** [산정] | ● |
| | GH Offset·Extrude 재현 | 없음 | 0 | ● | 낮음 | 실측 대기 | ◐ 규칙 이중화 위험 |
| (4) 일조 | **shapely 2.5D 그림자 + 연속 2시간** | 없음 | 0 | — | 중간 | **1.27 s**(5 m) / 2.27 s(2 m) [산정] | ● 루프 안 |
| | LB Direct Sun Hours(int_mtx) | 없음(설치됨) | 0 | ● | 낮음 | 실측 대기 | ● 최종 5안 |
| (4) 일사·UTCI 지도 | LB Incident Radiation / HB UTCI Map | Radiance·OpenStudio 설치 | 0 | ● | 중간 | 수십 분~[가정] | ● 최종 5안 |
| (4) Sky View | LB View Percent | 없음 | 0 | ● | 낮음 | 실측 대기 | ● 최종 5안 |
| (4) 바람 | Eddy3D + BlueCFD | 필요 | 0 [T4, 확인 대기] | ●(2026-02-10 설치본) | 높음 | 풍향당 수십 분~수 시간 [가정] | ● 최종 5안 |
| | Butterfly | 필요 | 0 | × | 높음 | — | × 기각 |
| | Forma rapid/detailed | 계정 | 교육용 무료(상업 사용 불가) [T2v] | — | 낮음 | 즉시 / 수 분 [T4] | ◐ 상대 비교만 |
| (4) 소음 | NoiseModelling(CNOSSOS-EU) | Java·H2GIS | 0(GPL-3) | — | 높음 | 수 분 [가정] | ● 최종 5안 |
| | 거리 감쇠 근사(numpy) | 없음 | 0 | — | 낮음 | ms [가정] | ● 루프 안(KPI) |
| (4) 보행 | cityseer / momepy / networkx | pip | 0 | — | 중간 | 0.05 s 캐싱 [Part 5 추정] | ● |
| | sDNA_GH / DeCodingSpaces / SpiderWeb | 필요 | 0 | ○ | 중간 | 실측 대기 | ◐ 교차 확인용 |
| (5) 최적화 | Galapagos | 없음 | 0 | ● | 낮음 | GH 정의에 종속 | × 가중치·페널티 |
| | Wallacei X | 필요 | 0 | ◐ | 낮음 | GH 정의에 종속 | ◐ NSGA-II, 루프 안 |
| | Octopus | 필요 | 0 | ○ | 낮음 | GH 정의에 종속 | ◐ 루프 안 |
| | Opossum 3.1.1 | 필요 | 0 | ● | 중간 | GH 정의에 종속 | ◐ NSGA-III 없음, 루프 안 |
| | Tunny | 필요(yak, Python 환경 자동 설치) | 기본 무료, 고급 유료(확인 대기) | ● | 중간 | GH 정의에 종속 | ◐ NSGA-III·제약 충족, 루프 안 |
| | pymoo via Rhino.Compute | Hops 설치 | 0(로컬) | ● | 높음 | GH 해석 + HTTP | ◐ headless Rhino가 루프 안 |
| | pymoo in ScriptEditor(3.9) | `# r:` | 0 | ● | 중간 | GH 정의에 종속 | ◐ 구판 고정·UI 점유 |
| | **pymoo 0.6.2 외부** | pip | 0 | — | 중간 | 엔진 시간과 같음(1.34 s) | ● |
| (6) 구조 | **Python 엔진 + Rhino 검토** | pip 몇 개 | 0 | — | 중간 | 1.34 s(측정) | ● |
| | GH 중심 + Tunny | Tunny | 기본 무료 | ● | 낮음 | 실측 대기 | ◐ |

---

## 9. 권장 도구체인 1안과 대안 1안

### 9.1 권장안 P — Python 엔진 + Rhino 검토

```
[Rhino 8 · 작업 사본(단위 m)]                [시스템 Python 3.12 venv: gjplan]
 BOUNDARY / FIXED_AXIS_* / ANCHOR_ENTRY  ──▶ io/read_3dm.py (rhino3dm, 별칭 표)
 (ScriptEditor 또는 rhino3dm로 읽기)           constraints/compile.py → buildable·height_max(20/15 m)·anchors
                                              generate/ S1 축→도로·가구(shapely) · S3 획지(OBB/skeleton) · S4 매스 5유형
                                              evaluate/ f1 cityseer · f2 시선면(대리모델) · f3 numpy · f4 분위 · f5 networkx
                                                        + 2.5D 일조 연속 2h(제약/KPI) + 소음 근사
                                              optimize/ pymoo NSGA-III(참조 방향, feasibility first, 리페어)
                                              export/ 대안 A–E → 3dm(rhino3dm, 동·획지 속성 문자열) + xlsx 면적표
 대안 3dm 열기 → 검토·손 수정  ◀───────────
 수정본 저장 ─────────────────────────────▶ io/diff_3dm.py → config.yaml 파라미터 갱신 + trace_table.csv 행 추가 → 재실행
 최종 5안: LB Direct Sun Hours(1 m·입면) · View Percent · (Radiance 설치 후) Incident Radiation·UTCI
          바람 Eddy3D 또는 Forma · 소음 NoiseModelling 또는 Forma   → 판정은 Python 스크립트
```

| 구성 | 도구 | 설치 | 비고 |
|---|---|---|---|
| 기하·생성 | shapely 2.2, numpy | 있음 | 2.5D(평면 + 높이 속성) |
| skeleton 분할 | ladybug-geometry-polyskel | pip 1개 | OBB와 둘 다 구현해 θ_lot의 범주 유전자로 [판단] |
| 최적화 | pymoo 0.6.2 | pip | NSGA-III, 참조 방향 수에 맞춘 개체 수 |
| 네트워크 | networkx, cityseer | pip | f₁·f₅ |
| 대리모델 | lightgbm | pip | f₂ 조망 정직 평가 300–1,000개 학습(CLAUDE.md §7) |
| 단계 MILP | ortools | pip | CP-SAT |
| 3dm 입출력 | rhino3dm 8.35 | 있음 | 속성 문자열로 획지 ID·용도·밀도 등급 전달 |
| Rhino 검토 | Rhino 8 + LBT 1.8 | 있음 | Radiance·OpenStudio는 최종 5안 단계에서 LBT 설치기로 추가 |
| 자동화 보조 | Rhino-MCP-Platform | 있음 | Claude가 3dm 열기·레이어 정리·화면 캡처를 대신할 수 있음(루프 밖) |

- 추가 지출 0원 [산정]. 설치는 pip 패키지와 (최종 단계의) Radiance·OpenStudio·Eddy3D·BlueCFD·Java뿐입니다.
- **설계 규칙**: `gjplan/generate`는 결정론적이어야 합니다(같은 유전자 + 같은 시드 → 같은 획지 ID). 그래야 3dm 손 수정의 차이를 획지 단위로 계산할 수 있습니다(Vanegas 2012의 지속성 개념 [T3]).

### 9.2 대안 G — Grasshopper + Tunny(NSGA-III)

| 구성 | 도구 |
|---|---|
| 생성 | GH: Offset/Region(또는 Clipper2GH) → Honeybee Straight Skeleton 또는 GH Python 3 컴포넌트(shapely 2.0.7) → Extrude |
| 평가 | LB Direct Sun Hours(int_mtx → 연속 2시간), View Percent, GH 안 면적 계산 |
| 최적화 | Tunny NSGA-III(제약 출력 연결), 결과는 Tunny의 Optuna 저장소 |
| 쓰는 경우 | ① 방법론 비교(같은 문제에서 권장안 P와 파레토 전선 비교) ② 사용자가 GH 화면에서 규칙을 직접 바꿔 보며 감을 잡는 단계 |
| 한계 | Rhino가 루프 안(저장소 판단 위반 → 최종안 근거로 쓰지 않음), 평가 시간 실측 대기, v1 비공개·상용(유료 범위 확인 대기), Python 3 컴포넌트 충돌은 v1.5.0에서 해결 공지(실동작 확인 대기) |

### 9.3 3dm 왕복과 추적표

1. `export`가 대안마다 3dm을 냅니다. 레이어 `ALT_E::ROAD`·`::BLOCK`·`::LOT`·`::MASS_u4` 등, 객체 속성에 `lot_id`·`zone`·`use`·`d_level`·`gsi`·`L`·`h_max`.
2. 사용자가 Rhino에서 매스를 옮기거나 획지 선을 고칩니다.
3. `io/diff_3dm.py`가 `lot_id` 기준으로 원본과 수정본을 비교해 「무엇을 왜 바꿨는가」 행을 `trace_table.csv`에 쓰고(사유는 사용자가 입력), 파라미터로 되돌릴 수 있는 변경(용도·밀도 등급·축 폭)은 `config.yaml`에 반영해 재실행합니다. 되돌릴 수 없는 손 수정(형태 다듬기)은 최종안의 「손 조정」 열로 남깁니다(CLAUDE.md §3.5).

### 9.4 첫 2주 확인 항목

| # | 항목 | 완료 기준 |
|---|---|---|
| 1 | 작업 사본 단위 교정(m, 축척 변경 없음)·레이어 별칭 표 | 사본 경계 면적 228,024.8㎡·긴 변 948 m 재확인 |
| 2 | 사용자 축을 `FIXED_AXIS_*` 곡선으로 정리(폭 속성) | 축 6개·진입점 7개가 3dm에 있음 |
| 3 | LB Direct Sun Hours 실측(같은 대안, 5 m·2 m 격자) | 2.5D와 시간·충족률 차이 표 |
| 4 | GH 정의 1회 해석 시간 실측(대안 G용) | 6만 회 환산 시간 |
| 5 | Tunny v1.5 설치·NSGA-III 시험(무료 범위 확인) | 10세대 시험 완료, 라이선스 문구 기록 |
| 6 | pymoo 0.6.2·networkx·cityseer·lightgbm·ortools 설치(시스템 venv) | `gjplan compile` 경계 면적 출력 |

---

## 10. 확인 대기·위험·사용자 결정 대기

### 10.1 확인 대기

| # | 항목 | 확인 방법 |
|---|---|---|
| Q1 | 1.48 GB 콘타 모델의 단위 설정 | Rhino에서 사본 열어 `Units` 확인 |
| Q2 | Tunny v1 무료·유료 범위와 가격, NSGA-III가 무료 범위인지 | 설치 후 LicenseManager·이용약관 |
| Q3 | Wallacei·Octopus·Opossum의 제약 처리 방식 | 각 매뉴얼 |
| Q4 | DeCodingSpaces·sDNA_GH·SpiderWeb의 Rhino 8(.NET Core) 동작 | 설치 시험(필요할 때만) |
| Q5 | Eddy3D 라이선스·BlueCFD 버전·풍향당 계산 시간 | Kastner·Dogan 2021 본문, 설치 시험 |
| Q6 | 가각전제(시행령 제31조)·정북 일조(제86조①) 현행 수치 | 법제처 원문 |
| Q7 | 「동지 연속 2시간·총 4시간」 판례 사건번호 | 실행모델 §7 원 출처 |
| Q8 | ladybug-geometry-polyskel 라이선스 | PyPI·GitHub LICENSE |
| Q9 | NoiseModelling S1 규모 1회 계산 시간 | 시험 실행 |

### 10.2 위험

- **단위 불일치**: 사본 교정 전 Ladybug·Forma 결과를 쓰면 오프셋 100 m·축척 1/1000 오류가 납니다(§1.3).
- **2.5D 근사 오차**: 평지 그림자 근사라 지형(성토층·노반 단차)과 입면 일조를 반영하지 않습니다. 최종 5안에서 LB와 비교해 오차를 보고합니다.
- **GH 플러그인 .NET 전환**: Rhino 8은 .NET Core 기본이고, 갱신되지 않은 플러그인은 `SetDotNetRuntime`로 .NET Framework로 바꿔야 할 수 있습니다 [T4]. 이 경우 다른 플러그인이 깨질 수 있습니다.
- **Rhino.Compute 반복 호출 메모리 누적**(대안 B 계열) [T4].
- **측정 스크립트의 지위**: `bench_shapely_25d_20261026.py`의 축 위치·폭·용도는 시간 측정용 임의값입니다. GSI·FSI·충족률은 설계 근거가 아닙니다.

### 10.3 사용자 결정 대기

| # | 쟁점 | 선택지 | 이 문서의 제안 |
|---|---|---|---|
| D1 | 사용자 축을 고정 입력으로 둘지 | (a) `FIXED_AXIS_*`로 위치·폭 고정 (b) 위치 ±범위·폭 후보를 유전자로 | (a) 위치 고정 + 폭만 유전자. CLAUDE.md §2 「고정 입력은 경계선 하나」와 다르므로 사용자 확인 필요. 레이어 규약 `FIXED_*`(§7)는 이미 허용 |
| D2 | ③ 역사유적축(사선) 유전자 | 실행모델 43유전자 표에 사선 축 항목이 없음 | (a)면 0차원, (b)면 각도·폭 +2 → 45차원(≤50 유지) |
| D3 | 획지 분할 방식 | OBB만 / skeleton만 / 둘 다(범주 유전자 1개) | 둘 다 구현, θ_lot에 방식 범주 포함 |
| D4 | 일조 「연속 2시간」을 제약으로 둘지 KPI로 둘지 | 주거 획지 옥외·입면 충족률 하한 = 제약 / 보고 KPI | 주거 동 입면 기준은 제약(불가능), 옥외 충족률은 KPI |
| D5 | 대안 G(Tunny)의 범위 | 방법론 비교만 / 사용자 탐색까지 | 방법론 비교 + 사용자 탐색, 최종안 근거로는 쓰지 않음 |

---

## 11. 출처(확인일 2026-10-26)

### 11.1 로컬 확인 [산정]

- `C:\Program Files\Rhino 8\System\Rhino.exe` 버전, `Plug-ins\Grasshopper\Components` 목록
- `C:\Users\OFFICE\.rhinocode\py39-rh8\python.exe`(3.9.10), `config.json`
- `C:\Users\OFFICE\AppData\Roaming\Grasshopper\Libraries`, `...\McNeel\Rhinoceros\packages\8.0`
- `C:\Users\OFFICE\ladybug_tools\python\Lib\site-packages`(dist-info 목록), `ladybug_rhino\config.py`, `...\UserObjects\ladybug_grasshopper\src\LB Direct Sun Hours.py` 95–131행
- `C:\Users\OFFICE\Desktop\9_도시\구경주역_최종대지_대지경계선.3dm`(rhino3dm 읽기 전용)
- 측정: `C:\Users\OFFICE\Desktop\9_도시\work\20261026_site_automation_plan\research\bench_shapely_25d_20261026.py`(실행 `python -I -X utf8 … 20`)

### 11.2 웹 자료

| 내용 | URL | 등급 | 확인 방식 |
|---|---|---|---|
| Hops 설치·로컬 Rhino.Compute·ghhops_server(CPython ≥3.8)·캐시·Windows 전용 | https://developer.rhino3d.com/guides/compute/hops-component/ | T2v | 원문 열람 |
| Rhino.Compute 코어시간 과금 $0.10/코어·시간 | https://developer.rhino3d.com/guides/compute/core-hour-billing/ | T2v | 검색 요약 경유 |
| Rhino 8 Python 패키지 환경(`# venv:`, `# r:`) | https://developer.rhino3d.com/guides/scripting/advanced-pyvenvs/ | T2v | 검색 요약 경유 |
| Rhino 9 Python 3.13(py313-rh9) | https://discourse.mcneel.com/t/rhino-beta-feature-python-3-13/205209 | T4(McNeel 직원) | 원문 열람 |
| Rhino 8 Offset 지연 RH-84100, SR14 수정, Clipper2 비교 | https://discourse.mcneel.com/t/curve-offset-in-r8-gh-long-run-time/192970 | T4 | 원문 열람 |
| Clipper2GH 1.3.2(Rhino 8), 오프셋 스파이크 보고 | https://www.food4rhino.com/en/app/clipper2gh · https://discourse.mcneel.com/t/clipper2-offset-bug-and-solution/213189 | T4 | 검색 요약 경유 |
| Columbia CDP 가로·가구·획지 GH 절차 | https://smorgasbord.cdp.arch.columbia.edu/modules/5-computational-design-modeling-in-grasshopper/5-4-street-grid/ | T4 | 원문 열람 |
| Vanegas 외 2012 Procedural Generation of Parcels in Urban Modeling(CGF 31(2pt3):681–690, doi:10.1111/j.1467-8659.2012.03047.x) | https://diglib.eg.org/handle/10.1111/v31i2pp681-690 | T3 | 초록·서지 |
| ladybug-geometry-polyskel(Felkel·Obdržálek straight skeleton) | https://pypi.org/project/ladybug-geometry-polyskel | T2v | 검색 요약 경유 |
| Honeybee Straight Skeleton 컴포넌트 | https://docs.ladybug.tools/honeybee-primer/components/0_create/straight_skeleton | T2v | 검색 요약 경유 |
| CGAL 2D Straight Skeleton | https://doc.cgal.org/6.1/Straight_skeleton_2/group__PkgStraightSkeleton2SkeletonFunctions.html | T2v | 검색 요약 경유 |
| DeCodingSpaces Toolbox 기능·배포(2021.10, Rhino 6, GPL-3) | https://toolbox.decodingspaces.net/ · https://toolbox.decodingspaces.net/download-decodingspaces-toolbox/ | T2v | 원문 열람 |
| Heron 릴리스(v0.5.x Rhino 8+ 전용) | https://github.com/blueherongis/Heron/releases | T2v | 원문 열람 |
| Urbano | https://www.food4rhino.com/en/app/urbano | T4 | 검색 요약 경유 |
| LB Direct Sun Hours(int_mtx·cpu_count·확장성) | https://docs.ladybug.tools/ladybug-primer/components/3_analyzegeometry/direct_sun_hours | T2v | 원문 열람 |
| LB Incident Radiation | https://docs.ladybug.tools/ladybug-primer/components/3_analyzegeometry/incident_radiation | T2v | 원문 열람 |
| LB Cumulative Sky Matrix(gendaymtx) | https://docs.ladybug.tools/ladybug-primer/components/2_visualizedata/cumulative_sky_matrix | T2v | 원문 열람 |
| LB View Percent(SkyView·SkyExposure) | https://docs.ladybug.tools/ladybug-primer/components/3_analyzegeometry/view_percent | T2v | 원문 열람 |
| LB UTCI Comfort | https://docs.ladybug.tools/ladybug-primer/components/1_analyzedata/utci_comfort | T2v | 원문 열람 |
| HB UTCI Comfort Map(EnergyPlus·Radiance) | https://docs.ladybug.tools/hb-energy-primer/components/7_thermalmap/utci_comfort_map | T2v | 검색 요약 경유 |
| Butterfly 유지보수 중단·Rhino 8 비지원 | https://discourse.ladybug.tools/t/can-butterfly-be-still-used/20829 · https://discourse.ladybug.tools/t/using-butterfly-in-rhino-8-thesis-topic/24870 | T4 | 검색 요약 경유 |
| Eddy3D(Rhino 8 Win 설치본 2026-02-10, BlueCFD) | https://es.aap.cornell.edu/research/eddy · https://discourse.mcneel.com/c/grasshopper/eddy3d/149 | T4 | 검색 요약 경유 |
| Kastner·Dogan 2021 Eddy3D, Building and Environment 108639 | https://ecommons.cornell.edu/entities/publication/f712a775-966f-46bf-a292-aed4339a9037 | T3 | 서지 |
| NoiseModelling(CNOSSOS-EU, Java, H2GIS/PostGIS) | https://noisemodelling.readthedocs.io/ | T2v | 검색 요약 경유 |
| GH 교통소음 도구 부재(포럼) | https://discourse.mcneel.com/t/noise-level-map-traffic-db/66318 | T4 | 검색 요약 경유 |
| sDNA_GH(MIT, Rhino 6·7, Windows) | https://pypi.org/project/sDNA-GH · https://sdna.cardiff.ac.uk/sdna/?p=1148 | T2v·T4 | 검색 요약 경유 |
| SpiderWeb | https://www.grasshopper3d.com/group/spiderweb | T4 | 검색 요약 경유 |
| cityseer 5.8.0(Py 3.10–3.14) | https://pypi.org/pypi/cityseer/json | T2v | 원문 열람 |
| momepy 1.0.0(Py ≥3.12, 2026-07-02) | https://pypi.org/pypi/momepy/json | T2v | 원문 열람 |
| pymoo 0.6.2(Py ≥3.10, 2026-06-28) / 0.6.1.5(cp39) | https://pypi.org/pypi/pymoo/0.6.2/json · https://pypi.org/pypi/pymoo/0.6.1.5/json | T2v | 원문 열람 |
| shapely 2.2.0(≥3.11) / 2.1.0(≥3.10) / 2.0.7(cp39) | https://pypi.org/pypi/shapely/json · https://pypi.org/pypi/shapely/2.1.0/json · https://pypi.org/pypi/shapely/2.0.7/json | T2v | 원문 열람 |
| pymoo NSGA-III(참조 방향, Deb·Jain 2014) | https://pymoo.org/algorithms/moo/nsga3.html | T2v | 원문 열람 |
| pymoo 제약 처리(feasibility first) | https://pymoo.org/constraints/index.html | T2v | 원문 열람 |
| Galapagos 제약 미지원·페널티(Rutten) | https://www.grasshopper3d.com/xn/detail/2985220:Comment:827477 | T4 | 검색 요약 경유 |
| Wallacei(Rhino 6·7 표기, NSGA-II) / Rhino 8 사용 보고 | https://www.food4rhino.com/app/wallacei · https://discourse.mcneel.com/t/wallacei-parallel-coordinate-analysis/220290 | T4 | 검색 요약 경유 |
| Octopus Rhino 8 설치 문의 | https://discourse.mcneel.com/t/how-to-install-octopus-in-rhino-8/212252 | T4 | 검색 요약 경유 |
| Opossum 3.1.1 Rhino 8 완전 호환·알고리즘 | https://discourse.mcneel.com/t/opossum-release-for-rhino-8/187731 | T4(개발자 공지) | 원문 열람 |
| Tunny(Optuna, NSGA-II/III, 제약, Rhino 8 net7.0) | https://www.food4rhino.com/en/app/tunny · https://tunny.hrntsm.com/ · https://github.com/hrntsm/Tunny | T4·T2v | 검색 요약·원문 열람 |
| Tunny Python 3 충돌, v1.5.0 해결 공지(2026-08-18) | https://discourse.mcneel.com/t/tunny-python-3-compatibility-error/218448 | T4 | 원문 열람 |
| Anemone Rhino 8 동작 | https://discourse.mcneel.com/t/anemone-or-other-plugin-to-do-grasshopper-procedural-loops-in-rhino-8/198464 | T4 | 검색 요약 경유 |
| Rhino 8 .NET Core 전환과 구 플러그인 | https://www.dlubal.com/en/support-and-learning/support/faq/005764 | T4 | 검색 요약 경유 |
| compute_rhino3d 반복 호출 메모리 누적 | https://discourse.mcneel.com/t/prevent-caching-in-rhino-compute/135009 | T4 | 검색 요약 경유 |
| Forma 교육용(상업 사용 불가) | 실행모델 부록 B.2 승계 | T2v | 재확인 안 함 |

---

## 변경 이력

- 2026-10-26 v1 작성. 웹 조사, 로컬 설치 상태 확인, 대지 3dm 읽기 전용 확인, shapely 2.5D 파이프라인 20표본 측정.
