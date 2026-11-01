# A. Autodesk Forma 단계별 가능성 판정 — 구경주역 대지 자동화 파이프라인

- 작성일·웹 확인일: 2026-10-26 (아래 웹 출처는 모두 이 날짜에 확인)
- 범위: 사용자 요청 ①~⑥ 여섯 단계 + 전제 ⓪(대지·경계 반입)·후속 ⑦(결과 반출)
- 대상: Forma Site Design(구 Autodesk Forma·Spacemaker), Forma Embedded View SDK **0.96.0**, Forma HTTP API, Forma Rhino 플러그인, Forma Site Design Add-In for Revit(Beta), DynamoForma(Dynamo Player), Revit Generative Design 2025
- 선행 원고: `work/20261024_forma_method/research/02_Forma_기능_데이터_반입.md`(2026-10-24). 이 문서는 02를 갱신·보강하며, 바뀐 항목은 §0.2에 모았습니다.
- 대지 기준값: 계획 경계 228,025㎡, 경계 bbox 311.1 × 947.9 m(러프 프레임) [산정, 01 원고 §3]
- 등급 표기
  - [T4·SDK] Autodesk가 npm에 배포한 SDK 타입 정의(.d.ts). **함수가 있는지**의 1차 근거이며, 분석 정확도의 근거는 아닙니다.
  - [T4·공식] Autodesk 블로그·Learn·마켓플레이스·APS 문서·Dynamo 공식 문서
  - [T4·포럼] Autodesk 커뮤니티 포럼(직원·사용자) / [T4·언론] 언론·제3자
  - [T3] 학술 / [산정] 본 조사 계산 / [가정] / [판단]
  - 저장소 규칙상 Autodesk 자료도 T4이므로 공모·지구단위계획 문서에는 인용하지 않습니다(CLAUDE.md §3.1). 이 문서는 **도구 선택 근거**로만 씁니다.
- 조사 한계: 공식 도움말(help.autodeskforma.com)과 autodesk.com Learn 다수가 로그인 리디렉션 또는 HTTP 403이고, APS 문서는 JavaScript 렌더링이라 본문이 수집되지 않았습니다. 그래서 SDK 기능은 **npm 패키지의 타입 정의 파일을 직접 읽어** 확인했습니다. 검색 요약만으로 확인한 항목은 「검색 요약 경유」로 표시했습니다.

---

## 0. 결론 요약

1. **여섯 단계 가운데 Forma 단독으로 요구 수준을 채우는 것은 ④ 환경 평가(화면 검증) 하나입니다.** ① 도로와 ② 획지는 수동 작도만 되고, ③ 매스는 Site Automation이 「비교군」 수준이며, ⑤ 밀도 도출과 ⑥ 최적화는 기능이 없습니다 [판단, §2].
2. **SDK 0.96.0은 02 원고가 본 것보다 넓습니다.** 네이티브 건물 생성(`elements.floorStack`, 세대 단위 `functionId`), 요소 일괄 생성(1회 1,000개, GLB·삼각형 메시·GeoJSON), 지형 고도 조회·패드·교체, 면적지표 계산(사용자 정의 지표 포함), 일조·소음 실행과 격자 수치 조회, 바람 rapid 예측 격자가 있습니다 [T4·SDK]. Forma에서 **수치를 꺼내는 통로**가 생긴 것이 이번 조사의 가장 큰 변화입니다.
3. **그러나 Forma를 최적화 루프 안에 넣을 수는 없습니다.** SDK는 Forma 브라우저 화면 안의 확장(iframe)에서만 돌고 쓰기에는 편집 권한이 필요합니다. 일광·상세 바람·미기후·태양광·탄소는 실행·결과 API가 없습니다 [T4·SDK]. 개체 200 × 세대 300 = 60,000회 평가(CLAUDE.md §8)를 회당 30초로 잡아도 500시간입니다 [산정, 회당 시간은 가정].
4. **도로·획지·매스 생성 알고리즘은 SDK로 짜도 결국 우리가 쓰는 코드입니다.** 같은 알고리즘을 JavaScript로 Forma 안에 두는 것보다 Python(`gjplan`)·Rhino에 두는 편이 추적·재현·면적표 산출에 유리합니다. Forma가 더해 주는 것은 생성이 아니라 **적재와 측정**입니다 [판단].
5. **최적화는 Forma 불가입니다.** Spacemaker의 목표 기반 생성(Explore)은 2023년 Forma 전환 때 빠졌고, 후속 Site Automation은 목적함수·파레토가 없는 파라미터 생성기입니다 [T4·포럼, T4·공식]. 설치된 Revit Generative Design 2025(NSGA-II)는 대체 가능하지만, 목적 5개에는 NSGA-III가 적합하고(Deb & Jain 2014 [T3]) Dynamo 기하 평가가 느려 차선입니다 [판단, §7].
6. **Rhino 연동에는 두 가지 사고 위험이 있습니다.** ① Rhino 8용 Forma 플러그인은 2025.12까지 「관리자 권한 필요·미동작」 사용자 보고가 남아 있습니다 [T4·포럼, 검색 요약 경유]. ② 대지 3dm(`구경주역_최종대지_대지경계선.3dm`)은 파일 단위가 **mm로 저장**돼 있으나 실제 1단위 = 1 m입니다 [산정, rhino3dm 판독]. 단위를 읽어 환산하는 경로에서는 대지가 1/1,000로 줄어들 수 있습니다. 플러그인 경로와 별도로 OBJ 반입 또는 SDK·HTTP 적재 경로를 함께 준비합니다.
7. **계정 조건이 기능을 자릅니다.** 교육용은 교육 목적 전용이고, 총탄소 분석은 2026-08-01부터 미국 소재 데이터 허브에서만, Building Layout Explorer는 미국 저장 상용 계정에서만 열립니다 [T4·공식]. 공모 신청서에 교육용 Forma 결과를 쓰는 것이 허용되는지는 **확인 대기**입니다(실행모델 v1 전제 ③과 같음).
8. **제안: Forma는 「루프 밖 검증 계측기 + 컨텍스트·발표 무대」로 둡니다.** 최종 파레토 5안(A–E)과 비교군 일부를 SDK로 네이티브 건물로 적재 → 면적지표로 건폐율·용적률 교차 검증 → 일조·소음·바람 rapid 격자 수치 추출 → 일광·미기후·상세 바람 화면 비교 → 이해관계자 워크숍. 도로·획지·매스 생성, 밀도 도출, 최적화, 규제 판정, 면적표 정본은 Python·Rhino가 맡습니다(§9). 실행모델 v1 §7과 같은 방향이며, SDK 수치화 통로를 더한 것입니다.

### 0.1 단계별 판정 한 줄

| 단계 | 판정 | 한 줄 이유 |
|---|---|---|
| ⓪ 대지·경계 반입 | Forma 단독 가능(조건부) | OBJ 지형 반입·지형 대체는 됨. 단위·원점·100 MB 한도를 맞춰야 함 |
| ① 축 기반 도로계획 | Forma 불가 → Rhino·Python (고정 축 1회 수동 작도만 Forma 단독 부분) | 축에서 도로망을 파생하는 기능 없음. 도로 요소에 폭 속성 없음 |
| ② 획지 분할 | Forma 불가 → Rhino·Python (수동 빼기 분할만 부분) | 분할 규칙·면적표·접도 조건 없음 |
| ③ 프로그램별 매스 생성 | 생성: Forma 불가 → Rhino·Python / 적재: SDK 확장으로 가능 / Site Automation: 비교군 | 용도별 규칙·규제 상한을 넣을 수 없음. 파라미터 비공개·변환 비가역 |
| ④ 환경 평가 | Forma 단독 가능(화면) + 일조·소음·바람 rapid는 SDK로 수치화 | 루프 안 평가는 불가. 나머지 분석은 화면·지점값만 |
| ⑤ 용적률·건폐율 도출 | Forma 불가 → Python (측정·교차검증만 Forma 단독 가능) | 면적지표는 「계산」이지 「도출」이 아님 |
| ⑥ 최적화·복수 대안 | Forma 불가 → Python(NSGA-III)·Rhino 검토 | 목적함수·파레토 없음 |
| ⑦ 결과 반출 | 형상은 Forma 단독 가능 / 분석 수치는 SDK 확장으로만 | UI에 분석 내보내기 없음 |

### 0.2 02 원고(2026-10-24) 대비 갱신

| 항목 | 02 원고 | 이번 조사 | 근거 |
|---|---|---|---|
| SDK 버전 | `forma-embedded-view-sdk` 0.x | **0.96.0**(npm 최신) | [T4·SDK] npm registry |
| 분석 API | 「확장 패널에서 분석 접근」 | 일조 `triggerSun`·소음 `triggerNoise`(beta)·격자 `getGroundGrid`, 바람 `predictWind`(rapid 쾌적도)만. 일광·미기후·상세 바람·태양광·탄소 API 없음 | [T4·SDK] |
| 건물 생성 | Dynamo Watch 3D 출력 | `floorStack.createFromFloors(Batch)`로 네이티브 2.5D 건물, 세대 단위 `functionId`·`program` | [T4·SDK] |
| 결과 내보내기 | 「6분 샘플 결과를 내려받아 자체 판정」 | UI에는 분석 내보내기 없음(제품관리자 포럼 답변). 6분 샘플은 SDK 지면 격자로만 | [T4·포럼], [T4·공식 APS 검색 요약] |
| 내재탄소 | C.Scale ML, 북미·유럽 계수 | 2026-07-17 총탄소(Forma Carbon Insights)로 **대체**, 2026-08-01부터 미국 허브만, 타 지역은 「올해 후반 예정」 | [T4·공식] |
| Rhino 8 | v0.7.0 베타, 관리자 권한 | v0.7.14 미동작 보고, 2025.12 「아직 미해결」 사용자 보고 | [T4·포럼, 검색 요약 경유] |
| Revit 애드인 | Revit 2022~2025 | 마켓플레이스 「Revit 2026까지 호환」, 이름에 Beta, 별도 설치 프로그램 | [T4·공식] |
| 도로 설계 | Forma Street Design(Beta) 언급 | 비공개 베타 대기자 명단 단계, Site Design과 별도 제품, Civil 3D로 넘김 | [T4·공식·언론] |
| 예제 저장소 | `spacemakerai/forma-extensions-samples` | 2025-12 보관(archived). 활성 저장소는 `forma-dynamo-extension`(2026-10-23 갱신)·`public-api-examples`(C#·Node·Python) | [T4·공식] GitHub API |

---

## 1. 판정 정의

| 판정 | 뜻 |
|---|---|
| **Forma 단독 가능** | Forma Site Design 화면 기능만으로 구경주역 요구 수준을 채웁니다 |
| **Forma 단독 부분** | 화면 기능으로 되지만 수동이거나 요구 수준의 일부만 채웁니다 |
| **SDK 확장으로 가능** | Embedded View SDK 또는 HTTP API로 우리가 코드를 쓰면 됩니다. 알고리즘은 우리 몫입니다 |
| **Forma 불가 → Rhino·Python** | Forma 기능·API로 불가하거나, 가능해도 Forma에 둘 이유가 없습니다. Rhino는 입력·검토·검증, Python(`gjplan`)은 생성·평가·최적화를 맡습니다(Rhino는 최적화 루프 밖, CLAUDE.md §7) |

---

## 2. 단계별 판정표

| 단계 | 구경주역 요구 수준 | Forma 단독(화면) | SDK·API 확장 | 판정 | 근거 등급 | 대체 경로(Rhino·Python) |
|---|---|---|---|---|---|---|
| ⓪ 대지·경계 반입 | 228,025㎡ 경계 + 지형_대지/도로/인도/경계석/하천을 실좌표로 | OBJ·IFC 3D, DXF 2D, 100 MB 이하. OBJ 지형 → 「convert to terrain」, 제안당 지형 1개. 1.9 × 1.9 km 작업 한도 안(311 × 948 m) | `terrain.replace({glb})`(내부 지형만), `integrateElements`로 GeoJSON Polygon·LineString | **Forma 단독 가능(조건부)** | [T4·포럼] 형식·용량, [T4·SDK], [산정] bbox | Rhino에서 사본을 만들어 단위를 m로 재지정(축척 없이)·원점 이동 → OBJ. 메시 정점 약 59만·면 약 85만으로 OBJ 약 45 MB 추정 [산정] |
| ① 사용자 축 기반 도로계획 | 축 ①~④ + 화랑로 연결 20 m·북측 13 m·외곽 10~12 m·향일문 8 m 보행로·차량 진입 7곳을 축에서 파생, 내부 가로는 대안별 변형 | Roads & rails 도구로 중심선 수동 작도. 폭은 generic surface로 그려 site limit에서 빼는 방식이 강좌 예시. 축 → 도로망 자동 파생 없음. Site Automation의 「circulation」은 생성 배치 내부 동선이며 사용자 축 입력이 아님 | `designTool.getLine`으로 축 입력, 우리 코드로 오프셋·교차 → GeoJSON으로 적재 가능. 도로 요소 스키마에 **폭 속성 없음**(교통 속성만) | **Forma 불가 → Rhino·Python** (고정 축 1회 수동 작도만 단독 부분) | [T4·공식] 도구 목록·Learn(검색 요약), [T4·SDK] 스키마 | Rhino 레이어 `AXIS_*` 곡선을 사용자가 고정 → Python(shapely)으로 폭별 오프셋·교차·진입점 → `ROAD_*` 폴리곤·중심선 |
| ② 필지(획지) 분할 | 가구 8–20개·획지 20–40개, 획지별 면적표, 합계 = 구역 총면적, 접도 | site limit에서 도로 형상을 빼 하위 대지를 만드는 수동 절차, zone 수동 작도. Site Automation 격자·셋백은 블록을 만들지만 획지 면적표·접도 판정 없음, 변환은 비가역 | 분할 알고리즘을 JS로 직접 작성하면 가능. 획지별 면적지표는 `areaMetrics.calculate({paths})`로 계산 | **Forma 불가 → Rhino·Python** (수동 빼기 분할만 단독 부분) | [T4·공식] Learn(검색 요약)·블로그 2025.04, [T4·SDK] | Python 정수 유전자 분할(가구 깊이·획지 폭 범위) + `buildable` 마스크 → 면적표 xlsx, Rhino는 검토 |
| ③ 프로그램·용도별 매스 자동 생성 | 구 역사 존치, 문화·공공청사·상업·주차·청년 주거 약 600세대, 고도 15/20 m, 이격·향 규칙 | Site Automation: 블록·선형·탑상·혼합, 층수·층고·건물 폭·탑 폭, zone별 유형, 면적지표 실시간 갱신. 건물별 기능(상업·주거) 지정. 용도별 규칙·규제 상한 입력 없음, 생성 파라미터 비공개 | `floorStack.createFromFloors(Batch)`로 층별 폴리곤·높이 → 네이티브 건물, 세대 단위 `functionId`·`program`(CORE·CORRIDOR·LIVING_UNIT·PARKING). 실험 `housing.createFromLine`(선 → 주거동) | **생성: Forma 불가 → Rhino·Python / 적재: SDK 확장으로 가능 / Site Automation: 비교군 1회** | [T4·공식] 블로그 2025.04·2026.08, [T4·SDK] | Python 규칙기반 매스(획지별 유형·층수 유전자, 규제 상한은 마스크) → 3dm·GeoJSON → SDK 적재 |
| ④ 환경 요인 평가 | f₅ 및 보고 KPI K8–K12(소음 초과 세대, 판례 일조 미달 세대, 바람 쾌적 면적, VSC 27% 입면 비율 등) | 일조·일광·바람(rapid/detailed)·소음·미기후·태양광·총탄소 실행 가능. 결과는 화면·Inspect 지점값·PNG. 분석 내보내기 없음 | 일조 실행+지면 격자(6분 샘플), 소음 실행(beta)+지면 격자, 바람 rapid 쾌적도 예측 격자. 나머지 분석 API 없음 | **Forma 단독 가능(최종안 화면 검증) + SDK로 3종 수치화 / 루프 안 평가는 Forma 불가 → Python 근사** | [T4·SDK], [T4·포럼] 내보내기 | 루프: Python 근사(거리 감쇠 소음, 일영 근사). 최종 5안: Ladybug(판례 일조 연속성·입면), Honeybee–Radiance(VSC), NoiseModelling 또는 Forma |
| ⑤ 데이터 기반 용적률·건폐율 도출 | 경주 조직 밀도 → 사례 밀도 → 최적 GSI·FSI 밴드(잠정 GSI 0.45–0.55·FSI 0.76–1.12) | Area metrics: GFA(기능별)·Building coverage·Site area, 사용자 정의 비율 지표(GFA/Site area) 추가 가능. 설계 요소를 **재는** 기능이지 밀도를 **정하는** 기능이 아님 | `geometry.getPathsInsidePolygons`·`getFootprint`로 컨텍스트 건물 점유율 계산은 가능하나, Forma 기본 컨텍스트는 OSM(높이 없으면 3 m/층) | **Forma 불가 → Python** (산출 밀도의 측정·교차검증만 단독 가능) | [T4·공식] Learn, [T4·SDK], 방법론 v1 [산정] | Python: 연속수치지도 23,579동·건축물대장·`ctx_fixed.pkl` 22,621동으로 조직 지표 산정(03·05 원고 산식) |
| ⑥ 최적화·복수 대안 | 목적 5개(가중치 없음), 결정변수 ≤50, 제약은 불가능 마스크, 파레토 전선 → 대안 A–E, 비교 대상 18개를 같은 목적공간에 | 제안(proposal) 복수 작성·비교, Site Automation 다안 생성. 목적함수·비지배 정렬·파레토 없음 | `generators.put/list`로 입력 스키마가 있는 재실행형 생성기 등록 가능. 최적화기 없음, 브라우저 세션 밖 실행 불가 | **Forma 불가 → Python(NSGA-III)·Rhino 검토** | [T4·SDK], [T4·포럼] Explore 제거, [T4·공식] | Python pymoo NSGA-III(설치 필요, 무료) + LightGBM 대리모델. Revit GD 2025는 차선(§7) |
| ⑦ 결과 반출 | 대안 3dm·DXF·XLSX 정본, 분석 수치 표 | OBJ·IFC 4.3 내보내기, Rhino 플러그인으로 지형·주변 건물 수신, Revit 애드인. 분석 수치 내보내기 없음 | 분석 격자·면적지표를 확장에서 CSV·XLSX로(샘플 `export-to-excel`은 사용자 정의 면적지표만) | **형상: Forma 단독 가능 / 분석 수치: SDK 확장으로만** | [T4·공식], [T4·SDK] | 정본 면적표·도면은 `gjplan/export`. Forma 수치는 참고 열 |

---

## 3. 단계별 근거와 판정 이유

### 3.0 전제 ⓪ — 대지·경계 반입

- 반입 형식은 3D IFC·OBJ, 2D DXF, 이미지 PNG·JPG이며 파일 최대 100 MB입니다. DWG·3DM은 직접 반입되지 않고 Revit·Rhino 확장을 거칩니다 [T4·포럼, Autodesk 직원 답변, 검색 요약 경유].
- 지형은 OBJ·IFC 메시를 반입해 「convert to terrain」으로 기본 지형을 대체하며, 제안당 지형은 1개입니다 [T4·포럼, 02 원고 §3.2].
- SDK에는 `terrain.replace({glb})`가 있고, Forma 내부 관리 지형(`isInternal()` = true)에서만, 편집 권한이 있을 때만 됩니다 [T4·SDK].
- 대지 크기: bbox 311.1 × 947.9 m로 1.9 × 1.9 km 작업 한도 안입니다 [산정]. 한도는 커뮤니티 매니저 답변입니다 [T4·포럼].
- **본 조사 판독(읽기 전용)**: 대지 3dm은 폴리라인 1(경계) + Brep 40 + Mesh 11이고, 메시 정점 589,731·면 854,076입니다. 파일 단위는 **Millimeters**로 저장돼 있습니다 [산정, rhino3dm 8.x 판독 2026-10-26]. 01 원고는 「단위 표기 mm·1단위 = 1 m」로 기록했습니다.
  - OBJ 크기 추정: 정점 1줄 약 40 B × 59만 + 면 1줄 약 25 B × 85만 ≈ 45 MB(Brep 메시화분 별도) → 100 MB 한도 안일 가능성이 높습니다 [산정, 줄 길이는 가정].
  - 좌표가 러프 프레임(x 약 1,166,700)이라 그대로 내보내면 원점에서 1,000 km 이상 떨어집니다. 반입 전 Forma 기준점으로 옮겨야 합니다 [산정].
  - 지형 z가 절대표고가 아니라는 기록이 있습니다(−63.8~3.5, 01 원고). SDK `getElevationAt`은 해발고를 돌려주므로, 기본 지형과 섞지 말고 반드시 대체합니다 [T4·SDK, 판단].
  - 1/2 축척 콘타 모델(1.48 GB)은 100 MB 한도를 크게 넘고 축척도 다르므로 Forma 반입 대상이 아닙니다 [산정].
- 경계선을 Forma의 site limit으로 만드는 방법(DXF 반입 후 따라 그리기, Rhino 플러그인 태그, SDK GeoJSON 중 어느 것이 site limit으로 인식되는지)은 **확인 대기**입니다.
- 판정 이유: 반입 자체는 Forma 기능으로 되지만 단위·원점·지형 기준면을 우리가 맞춰야 하므로 「조건부」입니다 [판단].

### 3.1 ① 사용자 축 기반 도로계획

- Forma Site Design 설계 도구 막대에는 「Roads & rails」가 있습니다 [T4·공식, Forma 블로그 2026-08-28].
- Autodesk Learn 강좌는 도로 폭을 도로 도구가 아니라 generic surface로 그리고, 변형 도구의 빼기로 site limit에서 제거하는 방식을 보여 줍니다 [T4·공식, 검색 요약 경유]. 도로 도구가 폭·횡단 구성을 다루지 않는다는 간접 근거입니다 [판단].
- Forma 요소 스키마(`forma-elements` 2.4.0)의 도로 관련 속성은 `trafficData`(평균 속도, 연평균 일교통량 ADT, 주간·저녁·야간 분포, 대형차 비율)뿐이고 폭 속성은 없습니다. 이 속성은 소음 분석 음원으로만 쓰입니다 [T4·SDK].
- Site Automation은 「건물과 동선 배치」를 생성한다고 소개되지만, 사용자 축을 입력으로 받는다는 서술은 없습니다 [T4·공식, 블로그 2025-04-24]. 격자를 사용자 축 방향으로 회전할 수 있는지는 **확인 대기**입니다.
- Forma Street Design(차로 구성·교차로·2D 평면·단면 동기화·차량 회전 궤적)은 2026-09 AU 발표 후 비공개 베타 대기자 명단 단계이며 Site Design과 별도 제품이고 Civil 3D로 넘깁니다 [T4·공식, T4·언론].
- SDK로는 `designTool.getLine()`으로 화면에서 축을 받아, 우리 코드로 오프셋·교차를 계산해 `integrateElements`(GeoJSON LineString·Polygon)로 올릴 수 있습니다 [T4·SDK]. 그러나 오프셋·교차·진입점 알고리즘은 우리 몫입니다.
- 판정 이유: 사용자 축과 도로 폭은 이미 정해진 값(D0)이므로 **고정 골격 1회 작도**는 Forma 수동으로도 됩니다. 그러나 축에서 내부 가로와 변형 대안을 자동 파생하는 일은 Forma에 기능이 없고, SDK로 짜도 알고리즘이 우리 코드라 Python에 두는 편이 낫습니다. → **Forma 불가 → Rhino·Python** [판단].
- Forma에 남길 일: 결과 도로 중심선에 교통량 속성(원화로·화랑로·태종로 ADT·속도)을 붙여 소음 분석 음원으로 쓰는 것 [판단].

### 3.2 ② 필지(획지) 분할

- 화면에서는 site limit을 도로 형상으로 빼 하위 대지를 반복해 만드는 수동 절차가 강좌에 있습니다 [T4·공식, 검색 요약 경유].
- 제품관리자 포럼 답변: site limit은 대지 면적 지표를 결정하므로 필지 경계에 맞추는 것이 좋고, zone은 임의 영역(부지 안 작은 영역, 주변 영향 검토용 큰 원 등)입니다 [T4·포럼, 검색 요약 경유].
- Site Automation은 격자 간격·셋백을 조정해 블록을 만들고 zone별로 유형을 바꿀 수 있으나, 결과를 zone·line building으로 바꾸는 변환은 되돌릴 수 없습니다 [T4·공식, 블로그 2025-04-24].
- SDK `areaMetrics.calculate({paths})`는 지정한 요소만 계산하므로 획지별 면적지표를 따로 낼 수 있습니다 [T4·SDK].
- 판정 이유: 분할 규칙(가구 깊이·획지 폭·접도·최소 면적), 면적표 합계 검증, 정수 유전자 인코딩은 Forma에 없습니다. → **Forma 불가 → Rhino·Python** [판단]. Forma에는 결과 획지를 zone 또는 site limit으로 올려 **획지별 측정**만 맡깁니다.

### 3.3 ③ 프로그램·용도별 매스 자동 생성

- Site Automation(구 Explore): 블록·선형·탑상·혼합 유형, zone별 변형, 층수·층고·건물 폭·탑 폭, 모서리·꼭짓점 직접 편집, 면적지표 실시간 갱신 [T4·공식, 블로그 2025-04-24]. 2026-08 도구 개요에도 「배치를 빠르게 생성·검토」로 남아 있습니다 [T4·공식].
- 건물 도구: line building(폭·모서리 정렬·층수·층고·구간 길이·기능 분류), basic building(높이·층수·기능) [T4·공식, 블로그 2026-08-28].
- 생성 파라미터를 공개한 사용 사례는 찾지 못했습니다(08 원고 §5 판단 유지) [T4·공식, 판단].
- SDK `elements.floorStack.createFromFloors({floors, plans})`: 아래층부터 층별 반시계 폴리곤과 높이로 2.5D 건물(수직 벽·평지붕)을 만듭니다. `plans`의 세대(`units`)에 `functionId`(문자열, 예제는 commercial·residential)와 `program`(CORE·CORRIDOR·LIVING_UNIT·PARKING)을 줄 수 있습니다. `createFromFloorsBatch`로 여러 동을 한 번에 만듭니다 [T4·SDK].
- 실험 API `experimental.housing.createFromLine({line, buffer, placementSide, templateId})`: 선을 따라 주거동을 만듭니다. 실험 API는 예고 없이 바뀔 수 있습니다 [T4·SDK].
- Building Layout Explorer(평면 생성)는 실험 기능이며 미국 데이터 저장 상용 사용자 한정입니다 [T4·공식, 02 원고 §2.5].
- 판정 이유: 구 역사 존치, 고도지구 15/20 m 상한, 역사문화환경 허용기준, 용도별 매스 규칙은 Site Automation 입력에 없습니다. 규제를 페널티가 아닌 불가능으로 다루는 원칙(CLAUDE.md §3.4)을 Forma 안에서 구현할 수 없습니다. → **생성: Forma 불가 → Rhino·Python**. 생성 결과를 Forma 네이티브 건물로 올리는 일은 **SDK 확장으로 가능**합니다. Site Automation은 「상용 도구 대비 비교군」으로 1회 돌려 기록합니다 [판단].

### 3.4 ④ 환경 요인 평가

세부는 §5 표에 있습니다. 요점만 적습니다.

- 화면에서는 일조·일광·바람·소음·미기후·태양광·총탄소를 실행할 수 있습니다 [T4·공식].
- UI 분석 내보내기: 제품관리자가 「현재 Excel 내보내기 기능은 없다」고 답했고, 전 분석 xlsx·csv 내보내기 요청은 내부 피드백으로 등록된 상태입니다 [T4·포럼, 검색 요약 경유].
- SDK로 수치를 꺼낼 수 있는 것은 세 가지입니다 [T4·SDK].
  - 일조: `analysis.triggerSun({selectedElementPaths, month, date})` → `getSunAnalysis` → `getGroundGrid`(격자 값, 유효 마스크, 폭·높이, 좌상단 x0·y0, 해상도 m). 원시 일조 격자는 점마다 24시간 × 시간당 10회 = 240비트(6분 간격)로 저장된다고 APS 문서가 설명합니다 [T4·공식 APS, 검색 요약 경유]. **지면 격자**이므로 입면(창) 기준 판례 일조 판정에는 그대로 쓸 수 없습니다 [판단].
  - 소음: `triggerNoise`(beta)는 도로·철도 교통 데이터로 실행하고 `getNoiseAnalysis`·`getGroundGrid`로 읽습니다. 격자 값의 단위(dB 여부)·계산 표준은 **확인 대기**입니다.
  - 바람: `predictiveAnalysis.predictWind`는 rapid 모델 쾌적도만 지원합니다. 입력은 높이맵 500 × 500 화소(1.5 m/화소, 750 m 정방형), 결과는 중앙 200 × 200 화소(300 m 정방형), 쾌적도 척도는 lawson_lddc·davenport·lawson·lawson_2001·nen8100·cstb 6종, 값 0–4(낮을수록 쾌적)입니다. 풍배도는 `getWindParameters`로 Forma 값을 받거나 직접 줄 수 있습니다 [T4·SDK]. 311 × 948 m 대지를 덮으려면 300 m 타일 2열 × 4행 = 8회가 필요합니다 [산정, 타일이 정북 정렬이라는 가정].
- 일광(VSC)·상세 바람(CFD)·미기후(UTCI)·태양광·총탄소는 SDK에 실행·결과 함수가 없습니다(실험 `analysis.putCatalogItem`은 확장이 만든 결과를 분석 목록에 **올리는** 기능일 뿐입니다) [T4·SDK].
- rapid 분석은 Autodesk 스스로 근사로 소개하며 검증 수치를 공개하지 않습니다 [T4·공식, 02 원고 §6].
- 판정 이유: 최종안 검증에는 Forma 단독으로 충분하고, 세 분석은 SDK로 표 수치까지 만들 수 있습니다. 그러나 루프 안 평가(6만 회)는 브라우저 세션·편집 권한·클라우드 실행 구조상 불가합니다. → **Forma 단독 가능(최종안) + SDK 수치화 / 루프는 Forma 불가 → Python 근사** [판단].

### 3.5 ⑤ 데이터 기반 용적률·건폐율 도출

- SDK `areaMetrics.calculate`가 돌려주는 내장 지표는 연면적(GFA, 「모든 층 건물 폴리곤 면적 합」, 기능별 분해), 건축면적 비율(building coverage, 단일값), 대지면적(site area), 세대 수, 주차 대수·면적이며, 사용자 정의 지표(`customMetrics`, 기능별 분해)도 함께 옵니다. 용적률(FAR) 내장 필드는 없습니다 [T4·SDK].
- Learn 강좌는 Area metrics 설정에서 「GFA ÷ Site area」 비율 지표를 새로 만드는 절차와 기능별 임대면적 승수(상업 0.8·호텔 0.75 예시)를 보여 줍니다 [T4·공식, Learn pt 페이지].
- 한국 정의(용적률 = 지상층 연면적 ÷ 대지면적, 건폐율 = 건축면적 ÷ 대지면적)와의 일치, 지하층 제외 가능 여부는 **확인 대기**입니다(02 원고 Q3 유지).
- Forma 기본 컨텍스트 건물은 OSM이며 높이가 없으면 층당 3 m로 추정합니다 [T4·공식, 02 원고 §2.1]. 우리 저장소에는 연속수치지도 건물 23,579동(층수 속성)과 대장 조인 필지가 있어 Forma 기본보다 정확합니다 [T2 NGII, 01 원고].
- 판정 이유: Forma는 설계 요소를 **재는** 도구이고, 경주 조직·사례 밴드로부터 밀도 범위를 **정하는** 기능은 없습니다. → **Forma 불가 → Python**. Forma는 Python이 정한 밴드 안의 대안을 적재했을 때 GSI·FSI가 `gjplan` 면적표와 맞는지 **교차 검증**합니다(정본은 `gjplan`) [판단].

### 3.6 ⑥ 최적화·복수 대안

- 2023년 포럼에서 사용자들이 Spacemaker의 explore/generate 버튼이 Forma에서 사라졌다고 묻자, Autodesk 선임 UX 디자이너가 후속 기능은 다르게 동작하되 상당 부분 기능을 제공할 것이라 답했습니다 [T4·포럼, 검색 요약 경유]. 후속이 Site Automation입니다 [T4·공식].
- Site Automation 소개 글은 특정 목적함수를 명시하지 않고, 파라미터 변경에 따라 지표를 갱신하며 바람·소음 rapid 분석으로 걸러 보라고 안내합니다 [T4·공식, 블로그 2025-04-24].
- SDK `generators.put/list`는 입력 스키마(숫자·불리언·열거·문자열·색·폴리곤·폴리라인)와 실행기(확장 엔드포인트 또는 확장 스크립트)를 가진 생성기를 프로젝트에 등록합니다 [T4·SDK]. 재실행형 파라메트릭 생성기의 틀은 되지만 탐색·최적화기는 없습니다.
- 판정 이유: 목적함수 5개를 가중치 없이 비지배 정렬해 파레토 전선을 내는 기능이 없습니다. → **Forma 불가 → Python(NSGA-III) + Rhino 검토** [판단]. 비교 대상 18개를 같은 목적공간에 찍는 일도 Forma 밖에서 합니다.

### 3.7 ⑦ 결과 반출

- 형상: OBJ, IFC 4.3(「Export as IFC to Docs」), Revit 애드인, Rhino 플러그인(지형·주변 건물을 Rhino로 수신) [T4·공식, 02 원고 §3.1].
- 분석 수치: UI 내보내기 없음 [T4·포럼]. 예제 저장소의 `export-to-excel`은 `areaMetrics.calculate`의 사용자 정의 지표만 xlsx로 냅니다 [T4·공식, GitHub 소스]. 분석 격자 반출은 우리가 확장으로 구현해야 합니다.

---

## 4. Embedded View SDK 0.96.0 기능 대장

모두 [T4·SDK] `forma-embedded-view-sdk@0.96.0`의 `dist/internal/*.d.ts`를 읽어 확인했습니다. 쓰기 함수는 모두 편집 권한이 필요합니다.

| 모듈(접근 경로) | 읽기 | 쓰기 | 이 파이프라인에서의 쓰임 |
|---|---|---|---|
| `elements` | `get`(재귀), `getByPath`, `getWorldTransform` | `add`·`replace`·`remove`·`batch`(순차 일괄), `editProperties`(JSON Merge Patch, 새 URN 반환) | 대안 요소를 제안 트리에 올리고 교체. 대안 ID·유전자 값을 사용자 정의 속성으로 붙여 추적 |
| `elements.floorStack` | – | `createFromFloors`, `createFromFloorsBatch`(층별 폴리곤·높이, plans·units에 `functionId`·`program`) | `gjplan` 매스를 네이티브 건물로 적재 → 면적지표·분석이 인식 |
| `integrateElements` | – | `createElementV2`·`updateElementV2`·`batchIngestElementsV2`(1회 1,000개), `uploadFile`, `createUrn` | 도로·획지·녹지를 GeoJSON(Polygon·LineString)·삼각형 메시(m)·GLB로 적재. JSON 표현은 약 100 KiB 이하 |
| `terrain` | `getBbox`, `getElevationAt`(해발 m, 메시 밖은 최저값), `isInternal`, `getPads` | `addPads`·`applyPads`(경사각 또는 경사율), `replace({glb})`, `groundTexture.add/update/remove` | 대지 지형 대체, 노반 제거 시나리오는 패드로, 우리 분석 결과(`buildable` 마스크·f₁ 연속성)를 지면 텍스처로 표시 |
| `geometry` | `getPathsByCategory`, `getPathsForVirtualElements`, `getFootprint`, `getTriangles`, `getPathsInsidePolygons` | – | 적재 결과 검산(바닥 폴리곤·삼각형 → 면적 대조) |
| `areaMetrics` | `calculate({paths})` → GFA(기능별)·building coverage·site area·사용자 정의 지표·세대 수·주차 | – | 대안·획지별 GSI·FSI 교차 검증 |
| `analysis` | `list`, `getSunAnalysis`, `getNoiseAnalysis`(beta), `getGroundGrid` | `triggerSun({month, date})`, `triggerNoise`(beta) | 동지·춘분·하지 일조 격자, 소음 격자 수치화 |
| `predictiveAnalysis`(`Forma.prediction`) | `getWindParameters`(8방위 풍배도·와이블 매개변수·조도) | `predictWind`(높이맵 → 쾌적도 격자) | 바람 쾌적도 8타일 수치화. AWS 283(탑동) 풍배도를 직접 넣어 Forma ERA5 값과 대조 가능 |
| `designTool` | `getPoint`, `getPolygon`, `getExtrudedPolygon`, `getLine` | – | 워크숍에서 참석자 지점·선 입력(조망점 등) |
| `generators` | `list` | `put`(입력 스키마 + 실행기) | 선택: 「대안 적재기」를 생성기로 등록해 재실행 |
| `experimental` | `housing.listTemplates` | `housing.createFromLine`, `analysis.putCatalogItem`(확장 결과를 분석 목록에 등록) | 시험용. 정본 경로에 쓰지 않음 |
| `proposal` | `getAll`·`get` 등(대부분 폐기 예정 → `udm`·`elements`) | `addElement` 등(폐기 예정) | 새 코드는 `elements`·`udm` 사용 |

- 개발 등록: 프로젝트 확장 메뉴에서 「Create extension」 → 설정에 개발 서버 URL(예: localhost)을 넣으면 플로팅 패널로 열립니다. 자기 프로젝트 사용에는 APS 앱이 필요 없고, 다른 사용자와 공유할 때 APS 앱 소유·공개 URL이 필요합니다 [T4·공식 APS, 검색 요약 경유]. 추가 비용은 확인하지 못했습니다(확인 대기).
- HTTP API(헤드리스): 요소 조회(`v1alpha/elements/{urn}`, 3-legged), 요소 생성(Integrate, 2-legged 또는 3-legged, `data:read`·`data:write`, 6 MB 초과는 S3 업로드, v1alpha 폐기 → v2) [T4·공식 APS, 검색 요약 경유]. VIKTOR 연동 문서는 HTTP로 제안·리비전 조회, 지형 다운로드, 요소 생성, 새 리비전에 요소 부착까지 된다고 설명합니다 [T4·언론(제3자 문서)]. **HTTP로 분석을 실행·조회하는 엔드포인트는 찾지 못했습니다(확인 대기).** 따라서 Python에서 대안을 Forma에 바로 올리는 것은 가능성이 높지만, 분석 수치화는 브라우저 확장이 필요합니다 [판단].
- 예제: `spacemakerai/forma-extensions-samples`(2025-12 보관)에 `predictive-wind`(레이캐스팅 높이맵 → `predictWind` → 지면 텍스처)·`footprint-mask`·`terrain-slope`·`export-to-excel`·`export-stl`·`color-buildings`가 있습니다. 활성 저장소는 `forma-dynamo-extension`(2026-10-23 갱신)·`public-api-examples`(C#·Node·Python)·`forma-extension-parking-demand-calculator`입니다 [T4·공식, GitHub API].

---

## 5. 환경 분석별 입력·실행·수치 반출

| 분석 | 화면 실행 | 주요 입력 | SDK 실행 | SDK 수치 | 화면 내보내기 | 구경주역 판단 |
|---|---|---|---|---|---|---|
| 일조(sun hours) | 가능 | 날짜, 분석 영역(전체·site limit·zone) | `triggerSun(month, date)` | 지면 격자(6분 × 240회 비트) | PNG·Inspect 지점값 | 동지·춘분·하지 격자를 CSV로. 판례 일조(입면 연속 2시간·총 4시간)는 Ladybug [판단] |
| 일광(daylight potential, VSC) | 가능 | site limit·zone | 없음 | 없음 | PNG·Inspect | K11 VSC 27% 입면 비율은 화면 상대 비교 또는 Honeybee–Radiance [판단] |
| 바람 rapid | 가능 | ERA5 풍배도, 분석 원 | `predictWind`(쾌적도) | 300 m 타일 쾌적도 격자 | PNG | 8타일로 대지 전체. AWS 283 풍배도 직접 입력 가능 [T4·SDK, 산정] |
| 바람 detailed(CFD) | 가능 | 분석 원 반경 150–350 m | 없음 | 없음 | PNG | 원 반경 350 m면 311 m 폭 대지를 길이 약 627 m씩 덮어 2개 원으로 전체 [산정]. K10 최종 5안 1회 |
| 소음 rapid / detailed | 가능 | 도로 중심선 `trafficData`(속도·ADT·시간대 분포·대형차 비율) | `triggerNoise`(beta) | 지면 격자(단위 확인 대기) | PNG | 폐선이라 도로 소음만 유효. 교통량 확보 전에는 「검사 불가」(실행모델 v1 K8) |
| 미기후(UTCI) | 가능 | 월·시간, 기온, 풍속·풍향 | 없음 | 없음 | PNG | 「초기·지시적 결과」 [T4·공식]. 상대 비교만, 또는 Ladybug UTCI |
| 태양광 | 가능 | 표면 필터, 패널 피복률·효율 | 없음 | 없음 | PNG | 사업비·에너지 보조 지표. 우선순위 낮음 |
| 총탄소(내재+운영) | 미국 허브만(2026-08-01~) | 건물 유형·외벽·창면적비 | 없음 | 없음 | Carbon Insights 대시보드 | 계정 허브 지역 확인 전에는 쓸 수 없다고 봅니다. 계수도 북미·유럽 기반 [T4·공식] |

- 출처: SDK 열은 [T4·SDK], 화면 열은 [T4·공식] 02 원고 §2.4·블로그, 총탄소는 [T4·공식] 블로그 2026-07-17.

---

## 6. Rhino·Revit·Dynamo 연동 현황

| 연동 | 현재 상태 | 이 파이프라인에서 | 근거 |
|---|---|---|---|
| Forma Rhino 플러그인 | Forma 확장 패널에서 내려받고 Rhino 명령 `Forma`로 패널을 엽니다. 프로젝트 URL로 연결 → 제안 선택 → 「Send Layers to Forma」. 요소 태그·레이어(Residential·Commercial·Office·Hotel 등) 지정 후 전송, Forma 지형·주변 건물을 Rhino로 수신 | 대안 3dm을 레이어별로 보내는 가장 짧은 경로. **Rhino 8 동작을 먼저 시험**하고, 파일 단위 mm 문제를 사본에서 m로 바로잡은 뒤 씁니다 | [T4·공식] Learn·블로그 2024.06, [T4·포럼] |
| Rhino 8 호환 | v0.7.0은 관리자 권한에서만 동작, v0.7.14 미동작 보고, 2025.12 「여전히 미해결」 사용자 보고. 2025-08 McNeel·Autodesk 웨비나는 「설치 요건·지원 버전」을 다룬다고만 공지 | 실패하면 OBJ 반입 또는 SDK·HTTP 적재로 우회 | [T4·포럼, 검색 요약 경유], [T4·공식] McNeel 포럼 |
| Grasshopper | Forma 전용 GH 컴포넌트 명세를 찾지 못함. ShapeDiver 확장으로 GH 정의를 Forma 안에서 실행 가능하나 ShapeDiver Designer Plus 이상 유료 요금제 필요 | GH는 Rhino 쪽 검토·Ladybug 검증에만. ShapeDiver는 예산(0~30 USD) 밖일 가능성 → 쓰지 않음 | [T4·공식] ShapeDiver 도움말 |
| Revit 2025 + Forma | 「Autodesk Forma Site Design Add-In for Revit, Beta」: Revit 2026까지 호환, 무료, 별도 설치 프로그램, 지형·건물·기타 요소를 BIM으로 변환하고 Revit에서 Forma로 갱신. Revit 2027 Connected Client(Scenario)는 Revit 2025에 해당 없음 | 최종안의 단면·도면 작업을 Revit에서 할 때만. 파이프라인 핵심 경로 아님 | [T4·공식] 마켓플레이스, 02 원고 §3.4 |
| DynamoForma / Dynamo Player | 공개 베타. 데스크톱 연결은 Revit·Civil 3D 2024.1+ 또는 Dynamo Sandbox 2.18+. Revit 2025·Dynamo 3.x는 DynamoForma 표준판. 클라우드(DaaS)는 Python 불가·승인 패키지만 | Revit GD 쪽 결과를 Forma로 보낼 때의 경로. 우리는 Python 경로가 있어 보조 | [T4·공식] Dynamo Primer, GitHub |
| HTTP API(Python) | APS 앱 + 프로젝트별 확장 서비스 계정 설치, `authcontext`·지역 헤더(US·EMEA) | `gjplan/export`에서 대안을 Forma 제안 리비전으로 직접 적재하는 후보 경로 | [T4·공식 APS], [T4·언론] VIKTOR |
| ArcGIS for Forma | 선·면 피처, 2,000 피처 초과 시 Generic으로 우회 | 규제 경계 표시용(선택). 판정은 `constraints/compile.py` | [T4·공식] Esri, 02 원고 §3.6 |

---

## 7. Revit Generative Design 2025로 대체할 수 있는 부분

| 기능 | Revit GD | 우리 요구 | 판정 |
|---|---|---|---|
| 알고리즘 | NSGA-II 사용자 구현(엘리트 보존·비지배 정렬·혼잡 거리), 병렬 평가 [T4·공식 GD Primer] | 목적 5개 → NSGA-III. NSGA-II는 목적 4개 이상에서 혼잡 거리 기반 선택이 약해진다는 것이 NSGA-III 제안의 전제 [T3 Deb & Jain 2014] | 대체 가능하나 차선 [판단] |
| 목표 | 출력마다 최대화·최소화·무시 [T4·공식] | 가중치 없는 다목적 | 충족 |
| 제약 | 출력값 범위(최소·최대)로 「결과가 만족해야 할 조건」, Optimize에서만 [T4·공식 Revit 2023 GD 도움말]. 위반 결과를 제외하는지 벌점을 주는지 문서에 없음 → **확인 대기** | 제약은 페널티가 아닌 불가능(CLAUDE.md §3.4) | Dynamo 생성기를 `buildable` 안에서만 만들도록 짜면 원칙 유지 가능 [판단] |
| 교차·돌연변이 | 교차 0.8·돌연변이 0.4 고정(GD 23.2.19.0 기준) [T4·공식] | 정수 유전자 연산자 조정 필요 | 제약 |
| 재현성 | 같은 설정 + 같은 시드 → 같은 결과 [T4·공식] | 추적표 재현 | 충족 |
| 결과 | 전 세대 파레토 집합 보관, 폐기안 포함 내보내기 [T4·공식] | 파레토 전선 + 비교 대상 18개 | 충족(비교 대상 18개는 별도 평가 필요) |
| 평가 속도 | 개체마다 Dynamo 그래프를 실행, 대리모델 내장 없음 [판단] | 6만 회 평가 → LightGBM 대리모델 | 불리 |
| 환경 평가 | Dynamo 안에서 Forma 분석 호출 불가(분석은 브라우저 확장 API) [T4·SDK, 판단] | f₅ 근사 + 최종 검증 | 불리 |
| 라이선스 | Dynamo 경로는 Revit만 있으면 되고, Revit 화면 경로는 AEC Collection 등 자격 필요(2021–2022 도움말) [T4·공식]. 사용자 PC에 AECGenerativeDesign 2025 설치됨 | 추가 지출 0~30 USD | 충족 |

- 결론: Revit GD 2025는 **방법론 비교용 2차 최적화기**(NSGA-II 대 NSGA-III 비교)로는 쓸 수 있으나, 본 파이프라인의 최적화기로는 Python NSGA-III를 유지합니다 [판단]. 저장소 판단 「RL은 방법론 비교용으로만」과 같은 위치입니다.

---

## 8. 라이선스·계정 조건

| 항목 | 내용 | 영향 | 근거 |
|---|---|---|---|
| 교육용 | Autodesk Education 플랜: 자격 있는 학생·교육자에게 1년 무료, 자격 유지 시 갱신. Forma Site Design 교육용 페이지 존재 | 교육 목적 전용. Forma for Construction 교육 FAQ는 「전문 프로젝트에 쓸 수 없다」고 답함. **공모 신청서 사용 가부 확인 대기** | [T4·공식, 검색 요약 경유] |
| Revit 구독 포함 | 2026.04부터 Revit 구독에 Forma Site Design 포함 보도 | 사용자 Revit 2025가 상용 구독인지 교육용인지에 따라 달라짐 → **확인 대기** | [T4·언론] 02 원고 §5 |
| 지역 한정 기능 | 총탄소: 2026-08-01부터 미국 소재 Forma Data Management 허브만. Building Layout Explorer: 미국 저장 상용 사용자만 | 한국·교육 계정에서 미노출 가능 | [T4·공식] |
| 작업 영역 | 1.9 × 1.9 km, 사이트 병합 불가 | S1 대지는 충분, S2 반경 1 km 원은 모서리 손실 | [T4·포럼] |
| 개발 확장 | localhost 개발·자기 프로젝트 허용 | 추가 비용 없이 시험 가능(비용 확인 대기) | [T4·공식 APS] |

---

## 9. 제안 — Forma가 이 파이프라인에서 맡을 가장 좋은 역할

### 9.1 역할 정의

**Forma = 최적화 루프 밖의 「검증 계측기 + 컨텍스트·발표 무대」** [판단]

```
Rhino(사용자 축·고정 골격 입력, 3dm)
  → Python gjplan: 제약 컴파일(buildable) → 도로·획지·매스 규칙기반 생성 → 평가 f₁~f₅(근사·대리모델) → NSGA-III 파레토 → 대안 A–E
  → Rhino: 대안 검토·손 조정(추적표) → config.yaml 반영 → 재실행
  → Forma(최종 5안 + 공고안·대표 비교군): SDK 적재 → 면적지표 교차검증 → 일조·소음·바람 rapid 수치 → 일광·미기후·상세 바람 화면 → 워크숍
  → 수치는 gjplan으로 되돌려 보고 KPI 열(참고값)로만, 정본 면적표·도면은 gjplan/export
```

| Forma에 맡길 일 | 이유 | 근거 |
|---|---|---|
| 컨텍스트 무대: 대지 지형 대체, 주변 건물(연속수치지도 + 대장 층수) | 이해관계자가 한 화면에서 보는 3D 맥락. OSM·ASTER 30 m 대신 우리 데이터를 올림 | [T4·공식], 실행모델 v1 P12 교훈 |
| 최종안 적재: 매스를 `floorStack` 네이티브 건물로, 도로·획지·녹지는 GeoJSON 요소로 | 네이티브 건물이어야 면적지표·분석이 인식. OBJ 반입 요소가 면적지표에 잡히는지는 확인 대기 | [T4·SDK] |
| 면적지표 교차검증: 대안·획지별 GFA·건축면적·대지면적, 사용자 정의 비율 지표 | `gjplan` 면적표와 ±1% 안이면 적재가 맞다는 검산 | [T4·SDK·공식] |
| 일조·소음·바람 rapid 수치화(확장 1개) | 화면 캡처가 아니라 격자 수치로 대안 간 비교 표를 만들 수 있음 | [T4·SDK] |
| 일광·미기후·상세 바람 화면 비교 | API는 없지만 최종 5안 상대 비교에는 충분 | [T4·공식] |
| Site Automation 비교군 1회 | 「상용 도구 대비」 기록. 결과를 대안으로 쓰지 않음 | 08 원고 §5 판단 |
| 우리 분석의 표시: `buildable` 마스크·f₁ 연속성 지도를 지면 텍스처로 | 워크숍에서 「왜 여기는 비웠는가」를 같은 화면에 | [T4·SDK] |

| Forma에 맡기지 않을 일 | 맡을 곳 |
|---|---|
| 축 → 도로망 파생, 획지 분할, 용도별 매스 생성 | Python(`gjplan/generate`), Rhino 검토 |
| 규제 4겹 + 특별법·세계유산 완충구역 판정 | `gjplan/constraints/compile.py` |
| 용적률·건폐율 밴드 도출 | Python(03·05 원고 산식) |
| 다목적 최적화·파레토·비교 대상 18개 평가 | Python NSGA-III + LightGBM |
| 면적표 정본·DXF·XLSX | `gjplan/export` |
| 판례 일조 판정(입면 연속성) | Ladybug |

### 9.2 착수 전 확인 실험(소규모, 각 반나절 이내 목표 [가정])

| 번호 | 실험 | 통과 기준 | 실패 시 |
|---|---|---|---|
| X1 | 대지 3dm **사본**(`work/20261026_site_automation_plan/` 아래)에서 단위를 축척 없이 m로 재지정, 원점 이동 → OBJ 내보내기 → Forma 「convert to terrain」 | OBJ ≤100 MB, 경계 면적 228,025㎡ ±0.1%, 꼭짓점 2개 거리 일치 | 지형을 경계 bbox ±50 m 안으로 더 줄이거나 메시 감축 |
| X2 | Rhino 8에서 Forma 플러그인 설치·「Send Layers to Forma」 1회(관리자 권한 없이) | 레이어 기능 태그 유지, 면적지표 표시 | X3 경로로 우회 |
| X3 | localhost 확장: 시험 매스 10동을 `floorStack`으로 적재 → `areaMetrics.calculate` | GFA·건축면적이 Python 계산과 ±1% | 적재 방식 재검토(`integrateElements` 메시) |
| X4 | 같은 확장: `triggerSun(12, 21)` → `getGroundGrid` → CSV | 격자 좌표가 대지 좌표와 맞음, Ladybug 동일 조건과 대안 순위 일치 | 일조는 Ladybug만 사용 |
| X5 | 같은 확장: `predictWind` 8타일, AWS 283 풍배도 입력 | 대지 전체 쾌적도 격자 합성 | 바람은 화면 detailed 2개 원 + 서술 |
| X6 | Site Automation 격자를 사용자 축 방향으로 돌릴 수 있는지, zone별 유형 지정 | 비교군 1회 생성·기록 | 비교군을 정북 격자로 기록하고 한계 명시 |
| X7 | 계정 확인: 교육용 여부, 데이터 허브 지역, 총탄소·소음 detailed 메뉴 노출 | 사용 가능한 분석 목록 확정 | §5 표에서 해당 행 제외 |

---

## 10. 확인 대기 목록

| 번호 | 항목 | 확인 방법 |
|---|---|---|
| A1 | 경계선을 Forma site limit으로 만드는 경로(DXF 따라 그리기·Rhino 태그·SDK GeoJSON 중 어느 것이 site limit으로 인식되는지) | X1·X2·X3 실험 |
| A2 | Rhino 8용 Forma 플러그인 현재 버전·관리자 권한 없이 동작 여부 | X2, Forma 확장 패널 |
| A3 | Rhino 플러그인이 파일 단위(mm)를 읽어 환산하는지 | X2(사본으로) |
| A4 | OBJ로 반입한 매스가 면적지표·분석에서 「건물」로 인식되는지 | X3 대조 |
| A5 | Site Automation 격자 회전·zone별 유형·결과 개수 | X6 |
| A6 | 도로 도구의 폭·차로 속성 유무(스키마에는 없음) | Forma 화면 확인 |
| A7 | 소음 격자 값 단위(dB)·계산 표준·detailed 상태 | X4와 같은 확장으로 `getNoiseAnalysis` 확인 |
| A8 | 한국식 용적률(지상층만)·건폐율 정의와 Forma building coverage 산식 일치, 지하층 제외 | 면적지표 설정 화면 |
| A9 | HTTP API로 분석을 실행·조회할 수 있는지 | APS HTTP 레퍼런스(로그인 후) |
| A10 | Revit GD 제약 위반 결과의 처리 방식(제외·표시·벌점) | Revit 2025 GD 도움말 |
| A11 | 교육용 Forma 결과를 공모 신청서에 쓸 수 있는지, 사용자 Revit 2025 라이선스 종류 | Autodesk 교육 약관·계정 화면 |
| A12 | 계정 데이터 허브 지역(US·EMEA)과 총탄소 노출 여부 | X7 |
| A13 | 확장 개발·등록에 추가 비용이 있는지 | APS 요금 안내 |
| A14 | 대지 3dm 지형 z 기준면과 해발고 관계 | 01 원고 확인 대기 항목과 함께 |

---

## 11. 출처 목록(확인일 2026-10-26)

SDK·요소 스키마 [T4·SDK]
- npm 레지스트리, forma-embedded-view-sdk 최신 0.96.0: https://registry.npmjs.org/forma-embedded-view-sdk/latest
- 분석 API: https://unpkg.com/forma-embedded-view-sdk@0.96.0/dist/internal/analysis.d.ts
- 지형 API: https://unpkg.com/forma-embedded-view-sdk@0.96.0/dist/internal/scene/terrain.d.ts
- 요소·floorStack API: https://unpkg.com/forma-embedded-view-sdk@0.96.0/dist/internal/elements.d.ts
- Integrate API: https://unpkg.com/forma-embedded-view-sdk@0.96.0/dist/internal/integrate.d.ts
- 면적지표 API: https://unpkg.com/forma-embedded-view-sdk@0.96.0/dist/internal/areaMetrics.d.ts
- 예측 분석(바람) API: https://unpkg.com/forma-embedded-view-sdk@0.96.0/dist/internal/predictive-analysis.d.ts
- 형상 API: https://unpkg.com/forma-embedded-view-sdk@0.96.0/dist/internal/geometry.d.ts
- 생성기 API: https://unpkg.com/forma-embedded-view-sdk@0.96.0/dist/internal/generators.d.ts
- 그리기 도구 API: https://unpkg.com/forma-embedded-view-sdk@0.96.0/dist/internal/scene/design-tool.d.ts
- 제안 API: https://unpkg.com/forma-embedded-view-sdk@0.96.0/dist/internal/proposal.d.ts
- 실험 API: https://unpkg.com/forma-embedded-view-sdk@0.96.0/dist/internal/experimental/index.d.ts ; .../experimental/analysis.d.ts ; .../experimental/housing.d.ts
- 요소 스키마(forma-elements 2.4.0): https://unpkg.com/forma-elements@2.4.0/forma-element-schema.generated.ts
- SDK 문서 첫 화면: https://app.autodeskforma.com/forma-embedded-view-sdk/docs/

GitHub [T4·공식]
- spacemakerai 저장소 목록(갱신일): https://api.github.com/orgs/spacemakerai/repos?per_page=100&sort=updated
- forma-extensions-samples(보관): https://github.com/spacemakerai/forma-extensions-samples
- export-to-excel 예제: https://raw.githubusercontent.com/spacemakerai/forma-extensions-samples/main/src/misc/export-to-excel/ExportToExcel.tsx
- predictive-wind 예제: https://raw.githubusercontent.com/spacemakerai/forma-extensions-samples/main/src/analysis/predictive-wind/readme.md
- forma-dynamo-extension: https://github.com/spacemakerai/forma-dynamo-extension
- public-api-examples: https://github.com/spacemakerai/public-api-examples

APS 개발자 문서 [T4·공식, 본문 JS 렌더링으로 검색 요약 경유]
- Getting started: https://aps.autodesk.com/en/docs/forma/v1/overview/getting-started
- Sharing extensions: https://aps.autodesk.com/en/docs/forma/v1/overview/sharing-extensions
- Integrate createElementHierarchy(폐기 예정): https://aps.autodesk.com/en/docs/forma/v1/reference/http-reference/integrate-createelementhierarchy-POST
- Element GET: https://aps.autodesk.com/en/docs/forma/v1/reference/http-reference/element-getelement-GET
- Interpreting sun analysis results: https://aps.autodesk.com/en/docs/forma/v1/embedded-views/useful-concepts/analysis/sun
- Exploring the possibilities of Forma extensions API(2023-12-19): https://aps.autodesk.com/blog/exploring-possibilities-forma-extensions-api

Autodesk 블로그·Learn·마켓플레이스 [T4·공식]
- Overview of Forma Site Design tools and functions(2026-08-28): https://blogs.autodesk.com/forma/2026/08/28/forma-site-design-tools-overview/
- How to use generative design, AI, and 3D modeling(2025-04-24): https://blogs.autodesk.com/forma/2025/04/24/how-to-use-generative-design-ai-and-3d-modeling-for-improved-site-planning/
- Introducing total carbon analysis in Forma Site Design(2026-07-17): https://blogs.autodesk.com/forma/2026/07/17/introducing-total-carbon-analysis-in-forma-site-design-understand-embodied-operational-and-total-carbon-from-the-earliest-stage-of-design/
- How to connect a Forma project to Rhino(2024-06-03): https://blogs.autodesk.com/forma/2024/06/03/combined-forma-rhino/
- Send a proposal to Forma from Rhino(Learn): https://www-pt.autodesk.com/learn/ondemand/tutorial/send-a-proposal-to-forma-from-rhino
- Understand the basics of design tooling(Learn, 검색 요약 경유): https://autodesk.com/learn/ondemand/course/conceptual-design-with-autodesk-forma/unit/2ZO1fPUXog95hCzCvIXJ6w
- Forma Quick Start — constraints(Learn, 검색 요약 경유): https://www.autodesk.com/learn/ondemand/curated/forma-quick-start-guide/5V8UzFder8Zq6XfSQVtx7i
- Forma Site Design Add-In for Revit, Beta: https://marketplace.autodesk.com/apps/4fb0800c-4ad1-4d29-84be-9c2b1c3b0321
- Forma Street Design 대기자 명단(검색 요약 경유): https://www.autodesk.com/campaigns/forma-street-design
- Autodesk AU 2026 보도자료(일본어, 2026-09-17): https://digitalpr.jp/r/143600
- Forma Site Design 교육용(직접 조회 403, 검색 요약 경유): https://www.autodesk.com/education/edu-software/forma
- Forma for Construction 교육용 FAQ(검색 요약 경유): https://www.autodesk.com/in/education/edu-software/autodesk-construction-cloud

Dynamo·Revit GD [T4·공식]
- Set up Dynamo Player in Forma: https://primer2.dynamobim.org/dynamo-in-forma-beta/set-up-dynamo-player-in-forma
- GD FAQ — under the hood: https://www.generativedesign.org/02-deeper-dive/02-06_faq-under-the-hood
- Revit 2023 GD — About Design Criteria for a Study: https://help.autodesk.com/cloudhelp/2023/ENU/Revit-GDiR/files/GUID-87C3C7C3-016B-4B2C-8FDA-0009C2212BC8.htm
- Revit 2022 GD — Generation Settings(검색 요약 경유): https://help.autodesk.com/cloudhelp/2022/ENU/Revit-Model/files/GUID-710D71BE-3376-4647-822A-DA4D793DCBFA.htm
- Running Generative Design(검색 요약 경유): https://refineryprimer.dynamobim.org/03-hello-gd-for-revit/03-03_running-gd-for-revit

포럼 [T4·포럼, 직접 조회 403 → 검색 요약 경유]
- Forma <> Rhino 8 Plugin support: https://forums.autodesk.com/t5/forma-forum/forma-lt-gt-rhino-8-plugin-support/td-p/12522288
- Exporting data from Daylight and Sun hour analysis: https://forums.autodesk.com/t5/forma-developer-forum/exporting-datas-excell-from-daylight-analysis-and-sun-hour/m-p/12458162
- Data Export Function: https://forums.autodesk.com/t5/forma-for-design-forum/data-export-function/td-p/13700922
- Zone vs site limits: https://forums.autodesk.com/t5/forma-forum/zone-vs-site-limits/m-p/12354325
- Generative design features(Explore 제거): https://forums.autodesk.com/t5/forma-forum/generative-design-features/td-p/11943525
- Vector format imports(형식·100 MB): https://forums.autodesk.com/t5/forma-forum/vector-format-imports/m-p/13682998
- 최대 작업 영역: https://forums.autodesk.com/t5/forma-for-design-forum/autodesk-forma-how-can-i-create-a-site-larger-than-the-current/m-p/14158418

언론·제3자 [T4·언론]
- AEC Magazine, Autodesk pushes Forma upstream(2026-09-15): https://aecmag.com/civil-engineering/autodesk-pushes-forma-upstream-and-connects-civil-3d/
- Architosh, AU2026(2026-09-16): https://architosh.com/2026/09/au2026-autodesk-expands-forma-and-leverages-ai/
- McNeel 포럼, From Concept to Analysis: Integrating Rhino with Autodesk Forma(2025-07-29): https://discourse.mcneel.com/t/from-concept-to-analysis-integrating-rhino-with-autodesk-forma/207741
- VIKTOR, Autodesk Forma Site Design 연동: https://docs.viktor.ai/docs/create-apps/software-integrations/autodesk-forma-site-design/
- ShapeDiver for Autodesk Forma: https://help.shapediver.com/doc/shapediver-for-autodesk-forma

학술 [T3]
- Deb, K., Jain, H. (2014). An Evolutionary Many-Objective Optimization Algorithm Using Reference-Point-Based Nondominated Sorting Approach, Part I. IEEE Transactions on Evolutionary Computation 18(4). doi:10.1109/TEVC.2013.2281535

저장소 내부
- `work/20261024_forma_method/research/02_Forma_기능_데이터_반입.md`(선행 원고)
- `work/20261024_forma_method/research/01_저장소_자산_목록.md`(대지 3dm·좌표 프레임)
- `work/20261024_forma_method/research/08_선례_Forma_Spacemaker.md`(Site Automation 판단)
- `work/20261024_forma_method/데이터기반_도시설계_실행모델_v1.md`(역할 분담 §7, 보고 KPI K8–K12)
- `work/20261024_forma_method/구경주역_Forma_도시설계_방법론_v1.md`(잠정 밀도 밴드)
- 본 조사 판독: `구경주역_최종대지_대지경계선.3dm`(읽기 전용, rhino3dm, 2026-10-26)
