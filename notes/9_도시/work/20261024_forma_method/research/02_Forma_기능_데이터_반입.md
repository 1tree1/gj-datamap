# 02. Autodesk Forma 기능·데이터·반입 조건 조사

- 작성일·확인일: 2026-10-24 (모든 웹 출처는 이 날짜에 확인)
- 대상 제품: Forma Site Design (구 Autodesk Forma, 구 Spacemaker). 2025.09 AU에서 개명. 관련 제품 Forma Building Design·Forma Carbon Insights·Revit 2027 Connected Client는 경계 지점만 다룹니다.
- 적용 스케일: S1 부지(계획 경계 228,025㎡ / 고시 폐역 부지 79,438㎡), S2 원도심 보행권 반경 1 km, S3 경주시 전역. Forma는 S1·S2용 도구이며 S3에는 쓰지 않습니다.
- 출처 등급: [T1] 법정문서 / [T2] 공공발간·통계 / [T3] 학술 / [T4] 언론·2차·업체 자료(Autodesk 공식 블로그·도움말·포럼의 Autodesk 직원 답변 포함) / [산정] 자체 계산 / [가정].
- 조사의 한계: Forma 공식 도움말(help.autodeskforma.com)은 2026-10-24 현재 Autodesk 로그인으로 리디렉션되어 비로그인 조회가 불가합니다. autodesk.com 제품·구매·학습 페이지 다수는 자동 조회가 차단(HTTP 403)되었습니다. 따라서 Autodesk 공식 블로그, APS 개발자 문서 검색 결과, Autodesk 커뮤니티 포럼의 직원 답변, Esri 공식 문서를 주 출처로 삼았고, 확인하지 못한 항목은 「확인 대기」로 적었습니다.

---

## 0. 결론 요약

1. Forma Site Design은 한국에서 사용 가능하나, 자동 컨텍스트 데이터는 전 세계 공통 기본 소스(건물·도로 OpenStreetMap, 지형 ASTER GDEM 30 m)로 떨어질 가능성이 높습니다. 한국 전용 지역 데이터 제공자 유무는 Forma 데이터 커버리지 앱에서 직접 확인해야 합니다(확인 대기).
2. 반입 형식은 UI 기준 IFC·OBJ(3D), DXF(2D), PNG·JPG(이미지), 파일 100 MB 이하입니다. DWG·SKP·RVT는 직접 반입 불가이며 Revit·Rhino 애드인을 경유합니다. GLB·GeoJSON은 API(Integrate·Geometry HTTP API) 경로로만 들어갑니다. [T4]
3. 지형은 OBJ·IFC로 반입한 뒤 「convert to terrain」으로 기본 지형을 대체합니다. 제안(proposal)당 지형 요소는 1개만 허용됩니다. [T4]
4. 좌표계는 프로젝트 생성 시 UTM이 자동 선택됩니다(경주는 WGS84/UTM 52N = EPSG:32652로 추정 [산정]). 사용자 지정 좌표계는 Revit 2027 「Scenario」(Tech Preview)에서만 설정 가능합니다. 우리 처리본 EPSG:5187은 반입 전 변환이 필요합니다.
5. 최대 작업 영역은 약 1.9 km × 1.9 km(3.61 km²)의 하드 리밋입니다. S1(0.228 km²)은 여유가 있으나 S2 반경 1 km 원은 네 모서리가 잘립니다. 바람·소음 상세 분석은 반경 150~350 m 원 단위라 S1 전체에 2개 이상의 원이 필요합니다. [T4, 산정]
6. 지표 계산은 Area metrics(GFA·RA·BC·FAR)로 하며 지역별 기본 규칙이 다릅니다. 한국 건축법 정의(용적률·건폐율)와 일치하는 기본 규칙 존재 여부는 확인 대기이며, 사용자 정의 규칙으로 맞추는 것이 안전합니다.
7. 환경 분석은 일조(6분 간격 샘플), 일광(VSC, CIE 담천공), 태양광, 바람(rapid AI / detailed CFD), 소음(도로 중심, rapid는 철도 포함), 미기후(UTCI), 내재탄소(ML, 미국계 데이터), 운영탄소(EnergyPlus 기반 → 2026년 Forma Carbon Insights)입니다. 홍수 분석은 존재 근거를 찾지 못했습니다(확인 대기).
8. 규제 4겹(용도지역·고도지구·역사문화환경 허용기준·지구단위계획)을 Forma가 판정하는 기능은 없습니다. 제약 판정은 `gjplan/constraints`의 buildable 마스크가 담당하고, Forma는 매스 검토·환경 분석·발표용으로 역할을 한정하는 것이 맞습니다.

---

## 1. 2026년 기준 제품 체계

| 항목 | 내용 | 등급·출처 |
|---|---|---|
| Forma industry cloud | 기존 Autodesk Forma와 Autodesk Construction Cloud를 포괄하는 상위 브랜드. ACC는 2026.03 Forma 브랜드로 편입 | [T4] Autodesk Construction Blog 2026.03; cad-notes.com |
| Forma Site Design | 구 Autodesk Forma(2023)·Spacemaker. 2025.09 AU에서 개명. 본 조사의 대상 | [T4] ENR 2025.09 |
| Forma Building Design | 2026.04.08 출시. 기본설계(schematic) 단계, 지오로케이션 부지·건물 옵션·파사드·평면·세대, 일광·일조·탄소 분석. Revit 구독자에게 Site Design과 함께 포함 | [T4] IT Brief UK 2026.04.08 |
| Forma Carbon Insights | 2026.04.07 발표. 내재+운영 총탄소 분석, Forma Building Design과 Revit 2027에서 사용. 구조 내재탄소 확장은 Tech Preview | [T4] Autodesk AEC Blog 2026.04.07 |
| Revit 2027 Forma Connected Client | Revit 2027이 첫 Connected Client(Tech Preview). 「Scenario」 컨테이너로 Forma Site Design과 지형·주변 건물·바람 분석을 교환. 2027.2에서 미기후 분석 추가 | [T4] Autodesk AEC Blog 2026.07.22; Symetri |
| Forma Street Design (Beta) | AU 2026(2026.09) 발표, 초기 토목 설계용 | [T4] Architosh 2026.09.16 |
| Forma Bid (Beta), Forma Data Management | 시공 입찰·데이터 관리. 본 과제와 무관 | [T4] Architosh 2026.09.16 |

판단: 「Forma」라는 이름이 2026년에는 플랫폼 전체를 가리키므로, 산출물·문서에서는 반드시 「Forma Site Design」으로 적습니다.

---

## 2. ① 핵심 기능

### 2.1 부지 설정과 자동 컨텍스트 데이터

| 데이터 | 기본(글로벌) 소스 | 해상도 | 비고 | 등급·출처 |
|---|---|---|---|---|
| 건물 외곽선 | OpenStreetMap | 가변 | 높이 정보 없는 건물은 층당 3 m, 최소 1층으로 추정. 기여자 의존이라 지역별 품질 편차 | [T4] Autodesk Forma Blog 2023.12.11 |
| 도로 | OpenStreetMap | 가변 | 소음 분석의 교통량·설계속도 속성을 도로 중심선에 입력 | [T4] 같은 글; Autodesk Learn |
| 지형 | ASTER GDEM(글로벌) / EU-DEM(유럽) | 30 m / 25 m | 한국은 지역 제공자가 없으면 ASTER 30 m | [T4] 같은 글 |
| 지도 질감·위성영상 | Mapbox | 가변 | | [T4] 같은 글 |
| 기상 | ERA5(C3S) | 시간별 | 미기후·바람 분석의 기초 | [T4] 같은 글 |
| 필지 경계 | 지역 제공자(기본 소스 없음) | - | 「Order data」에서 건물·지형·도로·필지 선택 주문. 국가별 가용성 상이 | [T4] Autodesk Learn 퀵스타트 |
| 지역 데이터 | Data Marketplace / Library Panel | - | 무료·유료 데이터셋. 독일 등 일부 국가 고품질 PoC(2024.01). 미국·일부 유럽이 가장 양호 | [T4] Autodesk Forma Blog 2024.01.12; Autodesk Learn 2023 |
| 커버리지 확인 | app.autodeskforma.eu/data-provider-map | - | 2026-10-24 비로그인 조회 시 본문 미표시. 한국 항목 **확인 대기** | [T4] |

작업 영역 제한
- Revit 도움말: 지도 영역 「약 2 × 2 km 최대」 [T4] Autodesk Revit 2026 Help(Have You Tried).
- 커뮤니티 매니저 답변: 최대 작업 영역 1.9 × 1.9 km(3.61 km²), 구독 종류와 무관한 하드 리밋, 사이트 병합 불가 [T4] Autodesk 포럼.
- 사용자 보고: DXF 반입 시 지형이 약 4 km²로 잘림 [T4] 포럼.

### 2.2 건물 매스 도구

| 도구 | 내용 | 등급·출처 |
|---|---|---|
| Basic / Line buildings | 층수·층고 파라메트릭 매스. Revit 전환 시 벽·바닥·지붕 | [T4] Autodesk Revit Help |
| 3D Sketch | 자유 모델링, 2D 평면→3D, 경사 지붕·기울어진 벽, 인스턴스, OBJ 반입 후 편집 | [T4] Autodesk Forma Blog 2025.04.24 |
| Zones | 분석 영역·생성 설계 하위 구역 정의 | [T4] 같은 글; Autodesk Learn |
| Site limits | 부지 경계. 분석 범위 지정에 사용 | [T4] Autodesk Learn |
| Roads / Parking / Vegetation | 도로(교통 속성), 건물 층 주차(Revit 주차 패밀리로 전환), 식생 | [T4] Autodesk Revit Help |

### 2.3 대지 지표(Area metrics)

| 지표 | Forma 명칭 | 정의(확인된 범위) | 등급·출처 |
|---|---|---|---|
| 연면적 | GFA (Gross Floor Area) | 각 층 외곽 면적의 합. 내부 코어·복도 분할은 반영 안 함(「gross area only」) | [T4] Autodesk 포럼 직원 답변 |
| 임대면적 | RA (Rentable Area) | GFA × 함수별 승수(예: Commercial 0.8) | [T4] Autodesk Learn(Rhino 연계 강좌) |
| 건폐율 | BC (Building Coverage) | 건축면적/대지면적으로 추정. 공식 산식 **확인 대기** | [T4] ARKANCE(cadforum.cz) |
| 용적률 | FAR (Floor Area Ratio) | GFA / 대지면적 | [T4] ARKANCE; Autodesk Learn |
| 함수(Function) | Residential / Commercial / Unspecified 기본 | 사용자 정의 함수 추가 가능 | [T4] Autodesk Learn |
| 지역 규칙 | 프로젝트 위치별 기본 지표 세트 | 생성·숨김·삭제·계산 규칙 변경 가능. 한국 기본 세트 존재 여부 **확인 대기** | [T4] Autodesk Learn |
| 세대수 | - | Forma Building Design에 「units」 조정 기능. Site Design 내 세대수 지표 **확인 대기** | [T4] IT Brief 2026.04 |

### 2.4 환경 분석

| 분석 | 입력 | 출력 | 방법·해상도 | 상태 | 제한 | 등급·출처 |
|---|---|---|---|---|---|---|
| Sun hours(일조) | 날짜 선택, 분석 영역(전체·site limit·zone) | 지표·건물면 직달 일조 시간 지도 | 데카르트 격자 측정점, 6분 간격(1일 240회) 판정 후 시간 합산 | 정식 | 구름·기상 미반영, 복잡 형상에서 회색 미계산 점 발생 | [T4] Autodesk Forma Blog; APS 문서 |
| Daylight potential(일광) | site limit·zone 선택 | Sky Component %(수직면은 VSC) | CIE 표준 담천공, VSC 임계 27/15/5 % | 정식 | 직사광 미포함, 창 설계 전 매스 단계용. 「컨설팅사·학술 벤치마크」 주장만 있고 수치 미공개 | [T4] Autodesk Forma Blog 2023.08.28(2025.10 갱신) |
| Solar energy(태양광) | 표면 필터(기본 지붕), 패널 피복률·효율 슬라이더 | 연간 일사량 kWh/㎡, 연간 발전 잠재량 | Copernicus 일사 데이터, 평판·등방성 천공 가정 | 정식(베타 해제) | 시스템 손실 미모델, 추정치 | [T4] Autodesk Blog(포르투갈어) 2023.11 |
| Wind(바람) | 풍배도(ERA5), 분석 원(150~350 m) | 풍속 분포, 유선, 보행자 쾌적도(Lawson LDDC 등) | rapid = AI 대리모델(즉시), detailed = CFD(수 분~) | 정식 | 쾌적도는 전 방향 종합만 제공, 방향별 쾌적도 불가. 원 반경 상한 350 m. 검증 수치 미공개 | [T4] Autodesk Learn; 포럼 직원 답변 |
| Noise(소음) | 도로 중심선 교통량(ADT)·속도 | 지표 소음 색지도(녹·황·적) | rapid = 수만 건 시뮬레이션으로 학습한 신경망(도로+철도), detailed = 수 분 계산(2023 베타) | rapid 정식 / detailed 상태 확인 대기 | 도로 소음만 시뮬레이션(직원 답변), dB 수치·계산 표준(Nord2000·CNOSSOS 등) **확인 대기** | [T4] Autodesk Forma Blog 2023.07.03; 포럼 |
| Microclimate(미기후) | 월·시간, 기온, 풍속·풍향·풍고 조정 | 체감온도(UTCI) 지도, 쾌적 시간 비율 | 일조·일광·바람 + 지역 기상 결합 | 정식(Revit 2027은 Tech Preview) | 「초기·지시적 결과」로 명시, 해상도 미공개 | [T4] Autodesk Forma Blog 2023.05.08; Revit 2027 Help |
| Embodied carbon(내재탄소) | 건물 용도, 구조 시스템, 외피 재료, WWR, 범위(외피·구조·내장·설비) | tCO₂e 총량, kgCO₂e/㎡ | ML 기반 예측, EHDD C.Scale 데이터, Quartz·CLF·EC3·ICE·Ökobaudat 계수 | 정식 | 계수가 북미·유럽 기반. 한국 계수 적용 가능성 **확인 대기** | [T4] Autodesk Community Blog; ARKANCE; Symetri |
| Operational energy/carbon(운영) | 형태·방위·재료 | 운영 에너지·탄소 | EnergyPlus 기반(AU 2023) → 2026년 Forma Carbon Insights(Revit 2027·Building Design) | Site Design 내 현재 제공 범위 **확인 대기** | | [T4] AU 2023; Autodesk AEC Blog 2026.04.07 |
| Flood(홍수) | - | - | - | **근거 없음 → 확인 대기** | Autodesk 홍수 도구는 InfoDrainage·ICM 등 별도 제품 | [T4] 검색 결과 부재 |
| Area analysis | - | 면적 집계 | | 정식 | | [T4] Autodesk 제품 페이지 |

### 2.5 시나리오(proposal) 비교와 생성 설계

| 기능 | 내용 | 상태 | 등급·출처 |
|---|---|---|---|
| Proposals | 한 사이트 안에 복수 제안. 「Send to Revit」, IFC 내보내기 등은 제안 단위 메뉴 | 정식 | [T4] Autodesk Revit Help |
| Site Automation(구 Explore) | 격자·셋백 조정, 유형(블록·선형·타워·혼합), 구역별 층수·층고·건물 폭·타워 폭. 결과를 zone·line building으로 변환(비가역). Area metrics 실시간 갱신 | 정식 | [T4] Autodesk Forma Blog 2025.04.24 |
| Building Layout Explorer | 매스에서 평면 안 생성(오피스·다세대). 건물 유형·주 구조재 입력 | 실험 기능. 미국 데이터 저장 상업 사용자 한정(2026.06.02) | [T4] Autodesk News 2026.06.02; AI Transparency Cards |
| 주차 생성 | TestFit Parking Generator 확장(제3자) | 확장 | [T4] 2차 자료 |
| Grasshopper 스크립트 실행 | ShapeDiver 확장으로 Forma 안에서 GH 정의 실행 | 확장 | [T4] Autodesk 포럼 직원 답변 |

판단: 우리 규칙기반 생성 + NSGA-III는 Forma 밖(`gjplan`)에서 돌리고, Site Automation은 「상용 도구 대비 비교군」으로만 1회 돌려 기록합니다(판단 §4 「생성 결과를 그대로 제출하지 않는다」).

---

## 3. ② 반입(Import)과 연결

### 3.1 지원 파일 형식(UI 반입)

| 형식 | 지원 | 비고 | 등급·출처 |
|---|---|---|---|
| IFC | 3D 반입 지원 | Library → Import → 캔버스 배치 | [T4] Autodesk 포럼 직원 답변(2024); Autodesk Learn |
| OBJ | 3D 반입 지원 | 3D Sketch에서 편집 가능 | [T4] 같은 출처 |
| DXF | 2D 반입 지원 | 과거(Spacemaker Next-gen) 미지원 → 현재 지원 | [T4] 같은 출처 |
| PNG / JPG | 참조 이미지 지원 | 기준점 2개로 축척·위치 지정 | [T4] Autodesk Learn |
| DWG | 직접 반입 불가 | Revit·Rhino에서 열어 애드인으로 전달 | [T4] 포럼 직원 답변 |
| SKP / RVT | 직접 반입 불가 | RVT는 Revit 애드인·Scenario 경로 | [T4] |
| PDF | 미지원 | | [T4] 포럼 직원 답변 |
| GLB / glTF | UI 반입 근거 없음. API(Integrate)로만 | GLB는 Y-up, Forma는 Z-up이라 회전 필요 | [T4] APS 문서 검색 결과; 포럼 |
| GeoJSON | UI 반입 근거 없음. Geometry HTTP API(백엔드) 또는 ArcGIS 확장 | 폴리곤·라인 | [T4] 포럼 직원 답변 |
| 파일 크기 | 최대 100 MB | | [T4] 포럼 직원 답변 |

내보내기: OBJ, IFC 4.3(「Export as IFC to Docs」, ACC Docs 저장, 2025.08), Revit(애드인), Rhino(애드인). 기본 지형 내보내기 시 readme에 지오로케이션 값 포함. [T4] ARKANCE 2025.08.01; 포럼.

### 3.2 지형(terrain) 반입

| 단계 | 내용 | 등급·출처 |
|---|---|---|
| 형식 | OBJ 또는 IFC 메시 | [T4] 포럼 직원 답변 |
| 원칙 | 제안당 지형 요소 1개. 기본 지형을 숨겨도 분석은 기본 지형을 사용 → 반드시 「대체」 | [T4] Autodesk 엔지니어 답변 |
| 절차(사용자 보고) | ① 기본 지형 내보내기 → ② readme의 지오로케이션 값 확인 → ③ 같은 값으로 OBJ 반입 → ④ 반입 요소 메뉴(⋯) 「convert to terrain」 | [T4] 포럼 사용자 보고(공식 문서 미확인) |
| 알려진 문제 | OSM 주변 건물이 새 지형에 자동 스냅되지 않음. 반입 지형이 rapid wind에 반영되지 않은 사례 | [T4] 포럼 |
| 지형 편집 | 전면 지형 편집 미지원, 국소 terrain pad 정도 | [T4] 포럼 직원 답변 |

### 3.3 좌표계·원점·단위

| 항목 | 내용 | 등급·출처 |
|---|---|---|
| 기본 CRS | 프로젝트·사이트 생성 시 UTM 자동 선택 | [T4] 포럼 Autodesk 직원 답변(2025~26) |
| 경주 적용 | 경도 약 129.2°E → UTM 52N. WGS84 기준이면 EPSG:32652 | [산정] UTM 존 정의. Forma의 실제 선택값은 내보낸 readme로 **확인 대기** |
| 단위 | 미터(지형 readme·OBJ 기준) | [가정] 공식 문서 미확인 |
| 사고 사례 | 호주 사용자: MGA56(EPSG:7856)으로 들어오던 내보내기가 일부 프로젝트에서 WGS84/UTM 56S로 바뀌어 수 km 어긋남 | [T4] 포럼 |
| 사용자 지정 CRS | Revit 2027 「Scenario」에서 좌표·좌표계 지정(Tech Preview). Site Design 단독 UI에서는 불가 | [T4] 포럼 직원 답변 |
| Revit 전달 | Forma 원점 = Revit Project Base Point, UTM 지오레퍼런스 유지. Forma 위치가 Revit 위치 정보를 덮어씀 → 빈 프로젝트에 로드 후 링크 권고 | [T4] Autodesk Revit Help |
| API | Integrate 요소의 root에 geoReference(좌표계·기준점) 지정, 로컬 좌표는 기준점 기준 | [T4] APS 문서 검색 결과 |
| 우리 처리본 | 전량 EPSG:5187 → Forma 반입 전 EPSG:32652(또는 readme가 지정한 CRS)로 재투영. 원본은 변환하지 않음(CLAUDE.md §1) | [산정] |

### 3.4 Rhino / Grasshopper / Revit / Dynamo 연결

| 연결 | 내용 | 상태 | 등급·출처 |
|---|---|---|---|
| Forma Rhino add-in | Forma 프로젝트 ↔ Rhino 파일 연결, 레이어·함수·형상 선택 동기화. Rhino→Forma 형상 전송, Forma→Rhino 지형·주변 건물 수신. Rhino 객체의 area metrics 확인 | 정식(2024.06) | [T4] Autodesk Forma Blog 2024.06.03 |
| Rhino 8 지원 | 초기 .NET 변경으로 비호환 → v0.7.0 베타에서 Rhino 8 동작(관리자 권한 필요 보고). 현재 지원 버전·설치 경로 **확인 대기** | | [T4] 포럼 |
| Grasshopper | Rhino 플러그인이 GH 포함(AU 2024 강좌). GH 컴포넌트 명세 **확인 대기**. 대안: ShapeDiver 확장 | | [T4] AU 2024; 포럼 |
| Revit add-in | Revit 2022~2025, Massing & Site 탭 Load Proposal. 지형→Toposolid(2024+)/Toposurface, 건물→벽·바닥·지붕·매스·제네릭, 도로·site limit→모델선·토포솔리드 분할, 주차→주차 패밀리. 미전환: zone·철도·generic 면·선·2D 반입. 제한: 다중 로드 불가, Revit에서 수정한 지형·도로는 Forma로 역갱신 안 됨 | 정식 | [T4] Autodesk Revit Help(2024.04 기준) |
| Revit 2027 Scenario | Connected Client, 클라우드 모델 + Scenario 컨테이너, 내보내기 없이 교환, 바람·미기후 분석을 Revit 안에서 실행. Tech Preview | | [T4] Autodesk AEC Blog 2026.07.22 |
| Dynamo Player 확장 | 클라우드(Dynamo as a Service, Python 불가) / 데스크톱(Dynamo 2.18+, Python 가능). Forma 형상·지형·area metrics 접근, Watch 3D 출력으로 Forma에 형상 반입 | 베타(2024.01) | [T4] Autodesk Forma Blog 2024.01.08; dynamobim.org |

### 3.5 API / Extensions

| 구성 | 내용 | 등급·출처 |
|---|---|---|
| Embedded View SDK | npm `forma-embedded-view-sdk`(0.x), 확장 패널(좌·우)에서 Forma 요소·지형·분석 접근. 샘플 저장소 spacemakerai/forma-extensions-samples | [T4] app.autodeskforma.com SDK 문서; GitHub |
| Integrate API | GLB 기반 요소 계층 생성(createElementHierarchy, v1alpha → v2 전환 안내), geoReference 포함 | [T4] APS 문서 검색 결과 |
| Geometry HTTP API | 서버에서 GeoJSON 폴리곤·라인 추가 | [T4] 포럼 Autodesk 직원 답변 |
| 확장 유형 | custom views, data providers, HTTP APIs, WebAssembly 실시간 분석 | [T4] AU 2024 |
| WMS / WMTS | 직접 반입 근거 없음 → **확인 대기**. 우회: ArcGIS Online에 WMS 아이템 등록 후 ArcGIS for Forma로 표시 [가정, 미검증] | |
| 데이터 요금 | Library Panel 지역 소스는 현재 무료, 민간 제공자는 향후 유료 가능성 | [T4] Autodesk Forma Blog 2023.12.11 |

### 3.6 ArcGIS for Autodesk Forma(Esri 확장)

| 항목 | 내용 | 등급·출처 |
|---|---|---|
| 요건 | ArcGIS Online 또는 Enterprise 계정, Contributor 이상 | [T4] Esri 제품 페이지 |
| 지원 레이어 | 호스팅 피처 레이어(선·면. 점 미지원), 웹맵·웹씬, 동적·타일 이미지 레이어(스타일 적용 이미지 미지원) | [T4] Esri 문서 |
| 표시 방식 | 이미지 레이어 → Forma 이미지 요소. 그 외 → view-only 레이어. 사이트 경계 안쪽만 표시 | [T4] Esri 문서 |
| 요소 변환 | Generic / Roads / Buildings / Property Boundaries로 Import. Buildings는 높이 필드 지정(기본 3 m) | [T4] Esri 문서 |
| 제한 | 2,000 피처 초과를 네이티브 요소로 반입 시 413 오류 → Generic으로 우회 | [T4] Esri What's new 1.1.1(2026.09) |
| 버전 | 1.1.0(2026.05.26) Enterprise 네이티브 로그인, 한국어 UI 포함 17개 언어. 1.1.1(2026.09) | [T4] Esri Blog; Esri 문서 |
| 미확인 | 고도(elevation)·3D 객체 씬 레이어 지원 **확인 대기** | |

---

## 4. ③ 한국 데이터로 컨텍스트를 만드는 현실적 경로

| 데이터 | 출처·형식 | Forma 반입 경로 후보 | 한계·주의 | 등급·출처 |
|---|---|---|---|---|
| 지형 DEM | 국토지리정보원 국토정보플랫폼(map.ngii.go.kr) 무상 다운로드. 1 m·5 m·10 m 격자, ERDAS IMG·GeoPDF 3D 형식 표시 | QGIS/Rhino에서 EPSG:5187→UTM 52N 재투영 → 메시(OBJ) → Forma Import → convert to terrain | 반입 범위는 작업 영역(≤1.9×1.9 km) 안으로 자름. 격자 간격 5 m면 S2 전체 메시 정점 약 16만 개 [산정] → 100 MB 이내 가능성 높음. 다운로드 화면·로그인 조건은 직접 확인 | [T2] NGII 홍보자료·국토영상정보서비스 |
| 연속수치지도 1:5,000 | NGII(국토정보플랫폼). 건물·도로·하천·등고선 레이어 | ① DXF(2D)로 참조 반입 ② ArcGIS Online 호스팅 피처 레이어 → Roads/Buildings/Property Boundaries ③ Rhino에서 돌출 후 애드인 동기화 | DXF는 2D만. 건물 층수 속성이 있으면 ×3 m로 높이 부여(Forma 기본과 동일 가정) | [T2] NGII |
| 3D 건물 | V-World 「3차원 건물(LOD1)」 shp, 구축기관 NGII, 수치지형도 층수 × 3 m. 다운로드 「-」, 구축기관 문의. LoD3~4는 주요 도심만 | ArcGIS 또는 Rhino 경유(위와 동일) | 형태·높이 부정확 명시(V-World). 경주 원도심 LoD3~4 유무 **확인 대기** | [T2] V-World 데이터 정보; [T4] 나무위키 2026.05 |
| 건물 높이 보정 | 건축물대장(공공데이터포털) 층수·높이, PNU 조인 | 피처 속성 → Buildings 높이 필드 | OSM 3 m/층 추정을 대체하는 핵심 보정 | [T2] 공공데이터포털 |
| 필지 | V-World 지적도(연속지적) | ArcGIS → Property Boundaries 또는 DXF | 2,000 피처 제한 → S2 범위는 Generic 또는 분할 | [T2] V-World |
| 항공·위성영상 | NGII 국토영상 / Mapbox 기본 | PNG 참조 이미지(기준점 2개) 또는 ArcGIS 이미지 레이어 | 대축척 정사영상은 참조용 | [T2] NGII |
| 규제 경계(용도지역·고도지구·역사문화환경 보존지역·세계유산 완충구역) | 토지이용규제정보, 경주시 고시 | DXF(2D) 참조 반입 또는 Generic 레이어 | Forma는 규제 판정 기능 없음. 참고선으로만 사용 | [T1] 고시 원문 필요 |
| V-World WMS/WFS | 오픈API(인증키) | Forma 직접 연결 근거 없음 → QGIS에서 캐시 후 반입, 또는 ArcGIS Online 경유 [가정] | | [T2] V-World 개발자센터 |

권장 작업 순서(가정, 검증 전):
1. Forma에서 경주 사이트 생성 → 기본 데이터 주문 → 기본 지형·건물을 내보내 readme의 CRS·기준점을 기록합니다.
2. NGII 5 m DEM을 그 CRS로 재투영해 OBJ 지형으로 대체합니다.
3. 건물은 연속수치지도 또는 V-World LOD1 + 건축물대장 층수로 Rhino에서 돌출해 Rhino add-in으로 동기화합니다(OSM 건물은 숨김 또는 삭제).
4. `gjplan` 산출 대안(3dm)을 같은 Rhino 파일의 별도 레이어로 넣어 제안(proposal) 단위로 동기화하고 분석을 돌립니다.

---

## 5. ④ 라이선스·요금·학생 접근

| 항목 | 내용 | 등급·출처 |
|---|---|---|
| Forma Site Design 단독 | 검색 스니펫(Autodesk 개요 페이지, 캐시): 월 85 USD / 연 700 USD / 3년 2,100 USD. 같은 페이지의 「59 USD/월부터」 문구와 불일치. 2차 자료: 연 1,445~1,500 USD, 월 185 USD. 공식 페이지 직접 조회 불가(403) → **확인 대기** | [T4] |
| AEC Collection | 월 460 / 연 3,675 / 3년 11,030 USD. Forma Site Design 포함 | [T4] Autodesk 제품 페이지(스니펫) |
| Revit 구독자 | 2026.04부터 Forma Site Design·Building Design·Board·Data Management Essentials 포함 | [T4] IT Brief 2026.04.08 |
| 무료 체험 | 30일, 연장 불가 | [T4] Autodesk |
| 교육용 | Autodesk Education 플랜: 학생·교육자 1년 무료, 자격 유지 시 갱신. Forma는 학생·교육자 무료(Autodesk 커뮤니티 매니저 답변, 2024) | [T4] Autodesk Education; 포럼 |
| 한국 가격 | 원화 가격·리셀러 조건 미확인 → **확인 대기** | |
| 실험 기능 제한 | Building Layout Explorer는 미국 저장 상업 계정만 → 교육용·한국 계정은 사용 불가 가능성 | [T4] Autodesk News 2026.06.02 |

---

## 6. ⑤ 알려진 한계

| 구분 | 한계 | 영향 | 등급·출처 |
|---|---|---|---|
| 큰 부지 | 1.9 × 1.9 km 하드 리밋, 사이트 병합 불가 | S1은 충분, S2 반경 1 km 원의 모서리 손실. S3 불가 | [T4] 포럼 |
| 분석 범위 | 바람·소음 원 150~350 m, 여러 원을 돌려 합성 | S1(약 477 m 정방형 상당 [산정])에 2개 이상 | [T4] 포럼 |
| 지형 정밀도 | 한국 기본 ASTER 30 m. 완경사 5~6 m, 급경사 최대 30 m 오차, 핏·스파이크 아티팩트 | 성토층·노반 높이 판단 불가 → NGII DEM 대체 필수 | [T3] ASTER 정확도 연구; [T4] Autodesk |
| 지형 편집 | 전면 편집 미지원 | 철도 노반 제거 등은 외부(Rhino)에서 처리 | [T4] 포럼 직원 답변 |
| 건물 높이 | OSM 높이 부재 시 3 m/층 | 원도심 저층 가로 분석 왜곡 | [T4] Autodesk |
| 지표 | GFA는 외곽 면적만, 내부 분할 미반영. 지역 규칙 불투명 | 한국식 용적률(지상 연면적)·건폐율(건축면적) 정의와 대조 필요 | [T4] 포럼 |
| 분석 검증 | rapid 분석은 「approximate」. 일광은 벤치마크 주장만. 바람·소음 계산 표준·오차 미공개 | 심의 자료에는 「상대 비교」로만 사용, 절대값 인용 금지 | [T4] Autodesk 블로그 |
| 좌표계 | UTM 자동, 사용자 지정은 Revit 2027 Scenario(Tech Preview) | EPSG:5187 왕복 시 변환 오차 관리 필요 | [T4] 포럼 |
| 문서 접근 | 공식 도움말이 로그인 뒤에 있음 | 외부 인용 시 블로그·APS 문서로 대체 | [T4] 2026-10-24 확인 |
| 실험 기능 | 미국 저장 상업 계정 한정 | 한국·교육 계정에서 미노출 가능 | [T4] Autodesk News |
| 소음 범위 | 도로 소음만(detailed), 철도는 rapid 학습에 포함 | 구경주역은 폐선이므로 영향 적음 | [T4] 포럼 |

---

## 7. 경주 부지에 적용할 때의 판단

1. 역할 분담. Forma Site Design은 「매스 검토 + 환경 분석 + 발표용 3D 컨텍스트」로 한정합니다. 규제 4겹 판정, 가구·획지 생성, NSGA-III 최적화, MILP 단계 계획은 모두 `gjplan`에서 수행하고 그 결과(3dm)를 Forma로 보냅니다. Forma의 Site Automation 결과는 비교군으로만 1회 기록합니다.
2. 영역 설정. 사이트 중심을 폐역 부지 중심에 두고 1.9 × 1.9 km 최대 영역을 잡으면 S2(반경 1 km)의 약 90 %가 들어옵니다 [산정: 원 면적 3.14 km² 중 정방형 3.61 km² 교집합]. 모서리 손실은 보행권 분석에 영향이 작으나, 접근성 f₁은 Forma가 아니라 `gjplan/evaluate`에서 계산하므로 문제가 되지 않습니다.
3. 지형. ASTER 30 m로는 성토층·노반(수 m 단차)이 보이지 않습니다. NGII 5 m(가능하면 1 m) DEM을 OBJ로 대체하는 것을 1단계 필수 작업으로 둡니다. 노반 제거 시나리오는 Rhino에서 지형 메시를 수정해 별도 제안으로 넣습니다.
4. 건물. OSM 경주 커버리지·높이는 신뢰할 수 없습니다. 연속수치지도 건물 + 건축물대장 층수(PNU 조인)로 S2 건물을 재구성하고, 등록문화유산 구 역사는 실측·도면 기반으로 별도 모델링합니다.
5. 좌표. Forma 기본 CRS(UTM 52N 추정)를 readme로 확정한 뒤, 변환 파이프라인을 `gjplan/export`에 한 줄로 고정합니다(EPSG:5187 → Forma CRS). 왕복 오차는 경계 폴리곤 면적(228,025㎡)으로 검증합니다.
6. 지표. Area metrics에 한국 정의의 사용자 정의 함수를 만듭니다: 용적률 = 지상층 GFA / 대지면적, 건폐율 = 최대 층 투영면적 / 대지면적. 지하층 제외 처리가 가능한지 **확인 대기**이며, 불가하면 Forma 수치는 참고치로 두고 `gjplan` 면적표를 정본으로 합니다.
7. 분석 선택. 일조(동지·춘분·하지 각 1회), 바람 쾌적도(겨울 북서풍·여름 남동풍 시나리오), 미기후(7월·1월), 일광 VSC는 대안 A~E 간 상대 비교에 사용합니다. 한국 일조 기준(동지 기준 연속 2시간·총 4시간 등)은 Forma 결과에서 직접 판정되지 않으므로 6분 샘플 결과를 내려받아 자체 판정합니다. 내재탄소는 북미·유럽 계수라 절대값 인용을 피하고 구조 시스템 간 상대 비교만 씁니다.
8. 소음. 폐선 이후 철도 소음원이 없으므로 도로 소음(원화로·태종로)만 유효합니다. 교통량(ADT)은 경주시 교통량 조사 자료[T2]를 도로 중심선 속성으로 입력하고, 자료 출처를 추적표에 남깁니다.
9. 홍수·지반. Forma에 홍수·지반 분석 근거가 없으므로 토양오염·양산단층·침수 이력은 `gjplan/constraints` 레이어로만 다룹니다.
10. 접근. 교육용 계정으로 시작하되, 실험 기능과 일부 데이터 마켓플레이스 항목이 제한될 수 있음을 전제합니다. 공모 제출 자료에는 Forma 화면 캡처가 아니라 벡터·수치(DXF·XLSX)를 정본으로 올립니다(CLAUDE.md §3.5, 메모리 「지도는 벡터에서 직접 렌더」).

---

## 8. 확인 대기 목록

| 번호 | 항목 | 확인 방법 |
|---|---|---|
| Q1 | 한국(경주) 지역 데이터 제공자 유무(건물·지형·필지) | app.autodeskforma.eu/data-provider-map 로그인 후 경주 좌표 조회 |
| Q2 | Forma가 경주 사이트에 자동 선택하는 CRS와 기준점 | 사이트 생성 → 기본 지형 내보내기 → readme 확인 |
| Q3 | Area metrics 한국 지역 기본 규칙 존재 여부, 지하층 제외 가능 여부 | 프로젝트 Area metrics 설정 창 확인 |
| Q4 | detailed noise 계산 표준(Nord2000·CNOSSOS 등)과 dB 출력 여부, 현재 베타 상태 | 공식 도움말(로그인) 또는 Autodesk 지원 문의 |
| Q5 | 바람 쾌적도 지원 척도 전체(Lawson LDDC 외 NEN 8100 등)와 측정 높이 | 도움말 article 6994344 |
| Q6 | 홍수·침수 분석 또는 확장 존재 여부 | Forma Extensions 패널·Autodesk 지원 |
| Q7 | 운영 에너지 분석의 Site Design 내 제공 범위(2026) | 분석 메뉴 확인 |
| Q8 | Rhino add-in 현재 버전·Rhino 8 정식 지원·Grasshopper 컴포넌트 명세 | Forma Extensions → Rhino 설치 페이지 |
| Q9 | Forma Site Design 공식 단독 가격(USD·KRW) | autodesk.com/kr 구매 페이지 직접 열람 |
| Q10 | WMS/WMTS 직접 반입 가능 여부 | SDK GeoData API 레퍼런스 |
| Q11 | V-World 3D 건물(LOD1 shp) 실제 취득 절차, 경주 LoD3~4 구축 여부 | NGII 문의, V-World 데이터 정보 |
| Q12 | NGII DEM 5 m·1 m 경주 도엽 다운로드 조건·형식 | map.ngii.go.kr 로그인 후 확인 |
| Q13 | ArcGIS for Forma의 고도·씬 레이어 지원 | Esri 「Curate data」 문서 |
| Q14 | 교육용 계정에서 데이터 마켓플레이스·실험 기능 제한 범위 | 계정 생성 후 확인 |

---

## 9. 출처 목록(확인일 2026-10-24)

Autodesk 공식(블로그·도움말·개발자 문서) [T4]
- Site Context in Revit via Forma (2023.12.11): https://blogs.autodesk.com/forma/2023/12/11/site-context-in-revit-via-forma/
- What's New in Autodesk Forma – January 2024: https://blogs.autodesk.com/forma/2024/01/12/whats-new-in-autodesk-forma-january-2024-update/
- Develop early insights on the daylight potential (2023.08.28, 2025.10 갱신): https://blogs.autodesk.com/forma/2023/08/28/develop-early-insights-on-the-daylight-potential-of-your-design-projects/
- Rapid noise analysis (2023.07.03): https://blogs.autodesk.com/forma/?p=50
- Microclimate analysis (2023.05.08): https://blogs.autodesk.com/forma/2023/05/08/updated-microclimate-analysis-allows-intuitive-insights-perceived-temperature/
- How to use generative design, AI, and 3D modeling (2025.04.24): https://blogs.autodesk.com/forma/2025/04/24/how-to-use-generative-design-ai-and-3d-modeling-for-improved-site-planning/
- How to connect a Forma project to Rhino (2024.06.03): https://blogs.autodesk.com/forma/combined-forma-rhino/
- Forma's integration with Rhino and Dynamo (2023.11.03): https://blogs.autodesk.com/forma/2023/11/03/formas-integration-with-rhino-and-dynamo/
- Dynamo Player extension beta (2024.01.08): https://blogs.autodesk.com/forma/2024/01/08/power-up-your-design-with-the-dynamo-player-extension-beta/
- Sun hours analysis blog: https://blogs.autodesk.com/forma/?p=743 ; https://blogs.autodesk.com/forma/?p=1701
- Solar energy analysis (포르투갈어, 2023.11): https://blogs.autodesk.com/mundoaec/introducao-a-analise-de-energia-solar-beta
- Introducing Forma Carbon Insights (2026.04.07): https://www.autodesk.com/blogs/aec/2026/04/07/introducing-forma-carbon-insights-collaborative-total-carbon-analysis/
- What's new in Revit 2027.2 (2026.07.22): https://www.autodesk.com/blogs/aec/2026/07/22/whats-new-in-revit-2027-2/
- Autodesk Forma March 2026 Construction Releases: https://www.autodesk.com/blogs/construction/autodesk-forma-march-2026-construction-releases-built-for-whats-next/
- Building Layout Explorer 발표 (2026.06.02): https://adsknews.autodesk.com/en/?p=57478
- Autodesk AI Transparency Cards: https://www.autodesk.com/trust/trusted-ai/ai-transparency-cards
- Revit 2026 Help – Create a Contextual, Georeferenced Model with Revit and Forma: https://help.autodesk.com/cloudhelp/2026/ENU/Revit-HaveYouTried/files/GUID-FF37B9BF-C383-4D6A-B4F1-3A3CB42AD858.htm
- Revit 2027 Help – Forma Microclimate Analysis (Tech Preview): https://help.autodesk.com/cloudhelp/2027/ENU/Revit-WhatsNew/files/GUID-73C5739E-D462-46DA-B4F4-125B31E2607E.htm
- Forma 환경 분석 제품 페이지: https://www.autodesk.com/products/forma/environmental-impact-analysis
- Forma Site Design 개요·구매(403, 스니펫만): https://www.autodesk.com/products/forma-site-design/overview ; https://www.autodesk.com/products/forma-site-design/buy ; https://www.autodesk.com/kr/products/forma/overview
- Autodesk Education: https://www.autodesk.com/education/edu-software/overview
- Autodesk Learn 튜토리얼(403, 스니펫만): Area metrics / Sun hours / Wind / Microclimate / Create a project / Send a proposal to Forma from Rhino (autodesk.com/learn/ondemand/...)
- APS Forma 문서(JS 렌더링으로 본문 미수집, 검색 스니펫만): https://aps.autodesk.com/en/docs/forma/v1/working-with-forma/element-system/forma-element-specification ; https://aps.autodesk.com/en/docs/forma/v1/reference/http-reference/integrate-createelementhierarchy-POST ; https://aps.autodesk.com/en/docs/forma/v1/embedded-views/useful-concepts/analysis/sun
- Embedded View SDK 문서: https://app.autodeskforma.com/forma-embedded-view-sdk/docs/
- Forma extensions samples: https://github.com/spacemakerai/forma-extensions-samples
- Forma 데이터 커버리지 앱(비로그인 본문 없음): https://app.autodeskforma.eu/data-provider-map
- AU 강좌 페이지: Rhino + Forma: More Forms, Less Carbon (2024); Extending Autodesk Forma to Create Powerful Analysis Solutions (2024); Simplify Sustainable Design with Autodesk Forma (2023)

Autodesk 커뮤니티 포럼(직원·커뮤니티 매니저 답변 포함) [T4]
- 최대 작업 영역: https://forums.autodesk.com/t5/forma-for-design-forum/autodesk-forma-how-can-i-create-a-site-larger-than-the-current/td-p/14158418
- Forma area restriction(350 m 반경): https://forums.autodesk.com/t5/forma-forum/forma-area-restriction/m-p/13312994
- 좌표계·Scenario: https://forums.autodesk.com/t5/forma-site-design-developer/choosing-coordinate-system-and-local-project-base-point-when/td-p/14081468
- 지형 대체: https://forums.autodesk.com/t5/forma-for-design-forum/importing-a-new-topography-and-replacing-the-default-topography/m-p/13276006 ; https://forums.autodesk.com/t5/forma-forum/change-terrain-hieghts/td-p/11263713
- 반입 형식(IFC·OBJ·DXF·이미지, 100 MB): https://forums.autodesk.com/t5/forma-forum/vector-format-imports/m-p/13682998
- API로 GeoJSON·GLB 추가: https://forums.autodesk.com/t5/forma-developer-forum/add-geometry-via-the-api/m-p/13686078
- Rhino 8 플러그인: https://forums.autodesk.com/t5/forma-for-design-forum/forma-lt-gt-rhino-8-plugin-support/td-p/12522288
- 소음 분석 범위: https://forums.autodesk.com/t5/forma-forum/questions-related-to-noise-analysis/m-p/12052028
- 바람 쾌적도: https://forums.autodesk.com/t5/forma-for-design-forum/wind-analysis/m-p/12709094 ; https://forums.autodesk.com/t5/forma-forum/wind-analysis-circle/td-p/12194339
- Area metrics 산정 범위: https://forums.autodesk.com/t5/forma-forum/forma-analyse-area-metric/m-p/12341688
- 학생 라이선스: https://forums.autodesk.com/t5/forma-for-design-forum/student-license/m-p/13028372
- 내재탄소 커뮤니티 블로그: https://forums.autodesk.com/t5/community-blog/use-forma-s-embodied-carbon-analysis-for-easy-early-stage/ba-p/13260248
- 지형 정확도·편집: https://forums.autodesk.com/t5/forma-for-design-forum/topography-differs-from-survey-and-google-maps/m-p/13702221

Esri [T4]
- ArcGIS for Autodesk Forma 개요: https://www.esri.com/en-us/arcgis/products/arcgis-for-autodesk-forma/overview
- Import ArcGIS data to Forma site: https://doc.esri.com/en/arcgis-autodesk-forma/latest/workflows/import-arcgis-data-to-autodesk-forma-site.html
- Add ArcGIS layers: https://doc.esri.com/en/arcgis-autodesk-forma/latest/workflows/add-arcgis-layers-to-autodesk-forma-site.html
- What's new (1.1.1, 2026.09): https://doc.esri.com/en/arcgis-autodesk-forma/latest/get-started/what-s-new.html
- What's new May 2026 (1.1.0): https://www.esri.com/arcgis-blog/products/arcgis-for-autodesk-forma/announcements/whats-new-in-arcgis-for-autodesk-forma-may-2026

언론·2차 자료 [T4]
- ENR, Forma Building Design (2025.09): https://www.enr.com/articles/61406-forma-building-design-brings-autodesk-into-the-contest-of-browser-based-design-tools
- IT Brief UK, Forma Building Design 출시 (2026.04.08): https://itbrief.co.uk/story/autodesk-launches-forma-building-design-for-revit-links
- Architosh, AU2026 (2026.09.16): https://architosh.com/2026/09/au2026-autodesk-expands-forma-and-leverages-ai/
- Geo Week News, Forma·ArcGIS 업데이트: https://www.geoweeknews.com/articles/autodesk-forma-updates-esri-arcgis-construction-cloud-acc/
- CITA, Forma Core Capabilities Overview (2026.03): https://www.cita.ie/wp-content/uploads/2026/03/Forma-Core-Capabilities-Overview-Presentation-EN.pdf
- ARKANCE(cadforum.cz): IFC 4.3 내보내기 (2025.08.01) https://www.cadforum.cz/cz/jak-exportovat-ifc-model-z-autodesk-forma-tip14659 ; 약어 정의 https://www.cadforum.cz/cz/co-znamenaji-zkratky-gia-gfa-nebo-bc-v-analyzach-spacemakeru-tip13355 ; 내재탄소 https://www.cadforum.cz/cz/analyza-zabudovaneho-uhliku-v-autodesk-forma-design-tip14885
- Symetri, Embodied Carbon in Forma: https://www.symetri.co.uk/insights/blog/machine-learning-meets-carbon-analysis
- Symetri, What's New in Revit 2027: https://www.symetri.co.uk/insights/blog/what-s-new-in-revit-architecture-2027-a-guide-to-the-latest-features/
- IMAGINiT, What's New in Forma Site Design (본문 미수집): https://resources.imaginit.com/autodesk-forma-formerly-autodesk-construction-cloud/whats-new-in-autodesk-forma-site-design-faster-design-decisions-smarter-workflows
- 가격 2차 자료: https://illustrarch.com/articles/design-softwares/73363-autodesk-forma-review.html ; https://www.creativetoolsai.com/ai-tools/autodesk-forma-site-planning/ ; https://www.trustradius.com/products/autodesk-forma/pricing (403)
- dynamobim.org, Set Up Dynamo Player in Forma: https://primer2.dynamobim.org/dynamo-in-forma-beta/set-up-dynamo-player-in-forma
- 나무위키 V-World(2026.05.24 수정): https://namu.moe/w/V-World

한국 공공 [T2]
- 국토지리정보원 홍보자료(DEM 1·5·10 m, 국토정보플랫폼 무상 다운로드): https://www.ngii.go.kr/lib/file/pr_01.pdf
- 국토정보플랫폼 국토정보맵: https://map.ngii.go.kr/ms/map/NlipMap.do
- 국토영상정보서비스(DEM 도엽별 다운로드, ERDAS IMG·GeoPDF 3D): http://air.ngii.go.kr/gis/gisSrchInfoView.do
- V-World 데이터 정보 「3차원 건물(LOD1)」: https://www.vworld.kr/data/v4dc_svcdata_s002.do?datIde=DAT_0000000000000204
- V-World 오픈API(WMS 가이드): https://www.vworld.kr/dev/v4dv_wmsguide2_s001.do
- 국토교통부·스마트시티 보도자료, 3차원 건물 모형 서비스 (2021.06.29): https://smartcity.go.kr/2021/06/29/3차원-건물-모형-디지털-트윈으로-우리-국토를-보다/

학술 [T3]
- ASTER GDEM 정확도(경사별 5~30 m 오차, 아티팩트): https://iris.polito.it/handle/11583/2990313 ; https://www.geomorphometry.org/uploads/pdf/pdf2015/MilevskiMilevska2015geomorphometry.pdf
