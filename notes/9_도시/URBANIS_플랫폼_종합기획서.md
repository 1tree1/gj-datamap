# URBANIS — AI 기반 도시계획 통합 플랫폼 종합 기획서

> **버전**: v1.0 | **작성일**: 2026-03-24
> **프로젝트명**: URBANIS (Urban Analysis & Intelligence System)
> **대상 시장**: 한국 도시계획 및 건축설계 분야

---

## 1. 프로젝트 비전 및 포지셔닝

### 1.1 핵심 비전

URBANIS는 한국의 도시계획자, 건축가, 공공기관이 **데이터 기반 의사결정**을 내릴 수 있도록 지원하는 AI 통합 웹 플랫폼이다. 단순한 데이터 시각화를 넘어, 자연어로 도시를 질의하고, AI가 배치안을 생성하며, 시뮬레이션으로 검증하는 **End-to-End 도시설계 워크플로우**를 제공한다.

### 1.2 경쟁 포지셔닝

| 플랫폼 | 데이터 시각화 | AI 생성 | 시뮬레이션 | 한국 데이터 | IFC/BIM |
|---------|:---:|:---:|:---:|:---:|:---:|
| UrbanGPT (Pebblous) | - | ★★★ | - | - | ★★ |
| UrbanFootprint | ★★★ | - | ★★ | - | - |
| Morphocode Explorer | ★★★ | - | - | - | - |
| 서울 S-Map | ★★ | - | ★★ | ★★★ | - |
| Replica | ★★ | - | ★★★ | - | - |
| **URBANIS (목표)** | **★★★** | **★★★** | **★★★** | **★★★** | **★★★** |

URBANIS의 차별점은 **한국 공공데이터에 최적화된 데이터 파이프라인**, **자연어 기반 도시 분석 AI 에이전트**, **생성형 AI 배치 설계**, **IFC 기반 BIM 연동**을 하나의 플랫폼에 통합하는 것이다.

### 1.3 타겟 유저 페르소나

- **P1 — 도시계획 컨설턴트**: 수주 프로젝트의 현황분석 보고서를 빠르게 생성하고 싶다
- **P2 — 지자체 도시계획 담당자**: 관할 구역의 도시 건강도를 실시간 모니터링하고 싶다
- **P3 — 건축/도시설계 사무소**: AI가 초기 매스스터디 대안을 생성해주면 거기서 시작하고 싶다
- **P4 — 연구자/학생**: 도시 데이터를 쉽게 수집·가공·시각화하여 논문에 활용하고 싶다

---

## 2. 핵심 기능 아키텍처

### 2.1 기능 모듈 전체 구조

```
┌─────────────────────────────────────────────────────────────────────┐
│                        URBANIS Web Platform                         │
├─────────┬─────────┬──────────┬──────────┬──────────┬───────────────┤
│ Module 1│ Module 2│ Module 3 │ Module 4 │ Module 5 │   Module 6    │
│ Urban   │ AI City │ Generati-│ Simulati-│ Report & │   Community   │
│ Data    │ Analyst │ ve Design│ on Engine│ Export   │   & Collab    │
│ Hub     │ Agent   │ Studio   │          │          │               │
├─────────┴─────────┴──────────┴──────────┴──────────┴───────────────┤
│                     Shared Infrastructure Layer                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐│
│  │ 3D Globe │ │ Data     │ │ Auth &   │ │ Task     │ │ Storage  ││
│  │ Renderer │ │ Pipeline │ │ User Mgmt│ │ Queue    │ │ & Cache  ││
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘│
└─────────────────────────────────────────────────────────────────────┘
```

---

### 2.2 Module 1 — Urban Data Hub (도시 데이터 허브)

**목적**: 한국 공공데이터를 자동 수집·정제·통합하여 분석 가능한 형태로 제공

#### 2.2.1 데이터 소스 통합

**Layer 1 — 공공 구조화 데이터**
| 소스 | API | 제공 데이터 | 갱신 주기 |
|------|-----|-------------|-----------|
| KOSIS (국가통계포털) | REST API | 인구, 가구, 경제, 도시계획현황통계 | 연/분기 |
| SGIS (통계지리정보) | Map API + Data API | 인구밀도, 사업체, 주택 그리드 데이터 | 연 |
| 공공데이터포털 (data.go.kr) | REST/XML | 토지이용계획도, 건물통합정보, 실거래가 | 실시간~월 |
| 국토정보플랫폼 | WMTS/WFS | 지적도, 용도지역지구, 도시계획시설 | 수시 |
| LX 한국국토정보공사 | REST API | 연속지적도, 지번주소 | 수시 |
| 건축행정시스템 (세움터) | REST API | 건축물대장, 인허가 정보 | 일 |

**Layer 2 — 공간 데이터**
| 소스 | 포맷 | 제공 데이터 |
|------|------|-------------|
| V-World (공간정보 오픈플랫폼) | 2D/3D Map API, 3D Tiles | 배경지도, 영상지도, 3D 건물, DEM |
| Overture Maps Foundation | GeoParquet | 전세계 20억+ 건물 풋프린트, 교통망, POI |
| OpenStreetMap | PBF/GeoJSON | 도로망, 건물, 편의시설, 토지이용 |
| 국가공간정보포털 (NSDI) | SHP/GeoJSON | 수치지도, 정밀도로지도 |

**Layer 3 — 실시간 민간 빅데이터**
| 소스 | 데이터 | 활용 |
|------|--------|------|
| SKT GeoVision / KT 빅데이터 | 유동인구, 생활이동 | 도시 활력도 분석 |
| Kakao Local API | POI, 키워드 검색량, 경로 | 상권분석, 접근성 |
| Naver 부동산 / 직방 | 매물, 시세, 리뷰 | 부동산 시장 동향 |
| 기상청 API | 기상관측, 미세먼지 | 환경 시뮬레이션 입력 |
| IoT 센서 (스마트시티 허브) | 교통량, 소음, 대기질 | 실시간 도시 모니터링 |

**Layer 4 — 국제 벤치마킹 데이터**
| 소스 | 데이터 |
|------|--------|
| UN-Habitat | 글로벌 도시지표 |
| OECD Metropolitan Database | 대도시권 비교통계 |
| Google Earth Engine | 위성영상, NDVI, 야간광 |
| AlphaEarth (Google DeepMind) | 64밴드 위성 임베딩 (10m 해상도) |

#### 2.2.2 데이터 통합 키 체계

한국 도시 데이터의 유니버설 키로 **법정동코드 (10자리)** 와 **PNU 코드 (19자리)**를 사용한다.

```
법정동코드: [시도2] + [시군구3] + [읍면동3] + [리2]
PNU 코드:   [법정동코드10] + [산여부1] + [본번4] + [부번4]

예) 대구광역시 수성구 범어동 123-4
    법정동: 2720010300
    PNU:    2720010300010123004
```

모든 데이터 소스를 이 키 체계로 정규화하여 크로스 분석을 가능하게 한다.

#### 2.2.3 Creative Data Recipes (창의적 데이터 조합)

단일 데이터셋으로는 보이지 않는 도시 특성을 드러내는 조합 분석:

| Recipe 이름 | 입력 데이터 조합 | 산출 인사이트 |
|-------------|------------------|---------------|
| **유령도시 탐지** | 야간위성광도 × 주간유동인구 × 건축물대장 | 건물은 있으나 비어있는 지역 식별 |
| **젠트리피케이션 예측** | 임대료 변화율 × 신규 카페/갤러리 POI × 20-30대 유입률 | 향후 3년 내 젠트리피케이션 가능 지역 |
| **보행 사막 탐지** | 도로중심선 × 인도유무 × 가로수 밀도 × 여름 표면온도 | 걷기 불편한 도시 공간 식별 |
| **생활SOC 사각지대** | 인구밀도 × 노인/어린이 비율 × 공공시설 보행접근성 | 공공서비스 공백 지역 |
| **소음·대기질 복합** | 도로 교통량 × 대기질 센서 × 녹지율 × 건물밀도 | 환경 취약지구 |

#### 2.2.4 UI/UX — 데이터 카탈로그

- **데이터 마켓플레이스**: 카테고리별 브라우징, 키워드 검색, 인기 데이터셋 추천
- **원클릭 불러오기**: 데이터 선택 → 법정동 범위 설정 → 지도 위에 즉시 시각화
- **데이터 레시피 갤러리**: 사전 정의된 조합 분석을 템플릿으로 제공
- **커스텀 데이터 업로드**: CSV, GeoJSON, SHP, GeoParquet 지원

---

### 2.3 Module 2 — AI City Analyst Agent (AI 도시분석 에이전트)

**목적**: 자연어로 도시를 질의하면 AI가 데이터를 분석하고 인사이트를 생성

#### 2.3.1 핵심 기능

**자연어 도시 질의 (Chat Interface)**

```
사용자: "대구 수성구의 인구 고령화 추세를 분석하고,
        노인복지시설 접근성이 떨어지는 동을 찾아줘"

AI Agent:
1. KOSIS에서 수성구 동별 연령별 인구 데이터 수집 (2015-2025)
2. 고령화율 시계열 트렌드 차트 생성
3. 공공데이터포털에서 노인복지시설 위치 데이터 조회
4. 네트워크 분석으로 도보 15분 접근 커버리지 계산
5. 접근 사각지대 히트맵 생성 + 우선순위 동 리스트 산출
→ 인터랙티브 지도 + 차트 + 요약 보고서 생성
```

**AI Agent 아키텍처 (ReAct 패턴)**

```
┌──────────────────────────────────────────────┐
│              AI City Analyst Agent            │
├──────────────────────────────────────────────┤
│  ┌─────────┐   ┌──────────┐   ┌──────────┐  │
│  │ LLM Core│──→│ Planning │──→│ Execution│  │
│  │ (GPT-4o │   │ Module   │   │ Module   │  │
│  │  / Local│   │ (ReAct)  │   │          │  │
│  │  LLM)   │   └──────────┘   └──────────┘  │
│  └─────────┘                                 │
│       ↕                                       │
│  ┌─────────────────────────────────────────┐ │
│  │              Tool Registry               │ │
│  ├─────────┬──────────┬──────────┬─────────┤ │
│  │ Data    │ Spatial  │ Viz      │ Report  │ │
│  │ Fetcher │ Analyzer │ Generator│ Writer  │ │
│  │         │ (PostGIS │ (deck.gl │ (Markdown│ │
│  │         │  + Turf) │  + Chart)│  + DOCX)│ │
│  └─────────┴──────────┴──────────┴─────────┘ │
└──────────────────────────────────────────────┘
```

#### 2.3.2 UrbanGPT 스타일 시공간 예측 모듈

HKU의 UrbanGPT 논문 아키텍처를 참고한 시공간 예측 엔진:

- **Spatio-Temporal Encoder**: 다중 레벨 TCN(Temporal Convolutional Network)으로 시계열 의존성 캡처
- **Alignment Module**: 시공간 표현을 LLM의 의미 공간으로 프로젝션
- **Instruction-Tuning**: 한국 도시 데이터 (교통량, 유동인구, 부동산 시세)로 파인튜닝
- **Zero-shot 전이**: 대구에서 학습 → 부산, 광주 등 타 도시로 전이 가능

**예측 가능 항목**:

| 예측 유형 | 입력 | 출력 |
|-----------|------|------|
| 유동인구 예측 | 과거 유동인구 + 날씨 + 이벤트 | 향후 1주일 시간대별 유동인구 |
| 부동산 시세 예측 | 거래이력 + 개발계획 + 인구변화 | 6개월 후 예상 시세 |
| 교통량 예측 | 교통량 센서 + 도로 네트워크 | 시간대별 교통 혼잡도 |
| 도시 성장 패턴 | 위성영상 시계열 + 인허가 데이터 | 향후 도시 확산 방향 |

#### 2.3.3 도시 건강진단 대시보드

대구시를 시범 타겟으로 한 도시 건강도 종합 지표:

```
도시건강지수 = Σ(Wi × Indicatori) / Σ(Wi)

카테고리별 지표:
├── 인구역학 (가중치 0.15): 인구증감률, 고령화율, 사회적이동
├── 경제활력 (0.15): 사업체 증감, 고용률, 창업률
├── 주거환경 (0.15): 노후주거비율, 주택보급률, 임대료 부담
├── 교통접근성 (0.12): 대중교통 커버리지, 통근시간, 도로밀도
├── 생활인프라 (0.12): 의료/교육/문화 접근성
├── 환경 (0.12): 녹지율, 대기질, 소음, 열섬효과
├── 안전 (0.10): 범죄율, 재해 취약도, 교통사고
└── 도시활력 (0.09): 야간활동, 보행량, 문화이벤트
```

---

### 2.4 Module 3 — Generative Design Studio (생성형 설계 스튜디오)

**목적**: AI가 대지 조건과 요구사항을 이해하고 도시 배치안을 자동 생성

#### 2.4.1 텍스트-to-Urban Layout

Pebblous의 UrbanGPT 2.0에서 영감을 받되, **웹 브라우저에서 직접 구동**되는 생성형 설계 도구:

```
입력 인터페이스:
┌─────────────────────────────────────────────────┐
│ 📍 대지: 대구 수성구 범어동 산 50-1 일대          │
│ 📐 면적: 45,000 m²                               │
│ 📋 용도지역: 제2종일반주거지역                     │
│                                                   │
│ 💬 "주거 70%, 근린상업 20%, 공원 10% 배분으로     │
│     남향 위주 배치, 용적률 200% 목표,              │
│     중앙에 커뮤니티 공원 배치해줘"                  │
│                                                   │
│  [🎲 대안 생성]  [⚙️ 상세 설정]  [📊 법규 확인]   │
└─────────────────────────────────────────────────┘
```

**AI 생성 파이프라인**:

```
1. 대지 분석
   ├── 경계 파싱 (지적도 API)
   ├── 용도지역/지구/구역 조회 (토지이용계획도 API)
   ├── 주변 맥락 분석 (건물 높이, 도로 패턴, 녹지)
   └── 법규 제약 조건 추출 (건폐율, 용적률, 높이제한, 일조권)

2. 레이아웃 생성 (Diffusion Model)
   ├── 조건부 확산 모델 (ControlNet 변형)
   ├── 입력: 대지 경계 + 제약조건 + 사용자 텍스트 프롬프트
   ├── 출력: 2D 토지이용 배치도 + 건물 풋프린트 + 높이필드
   └── 다중 대안 동시 생성 (4~8개 옵션)

3. 3D 매스 모델 생성
   ├── 2D 배치 → 3D 매스 자동 변환
   ├── 파라메트릭 조절 (층수, 세대수, 주차대수)
   └── 법규 검증 (건폐율, 용적률, 일조, 이격거리)

4. 대안 비교 & 최적화
   ├── KPI 매트릭스 (용적률, 세대수, 녹지율, 일조시간)
   ├── 사용자 피드백 루프 (스케치 수정 → 재생성)
   └── 최적 대안 선정 → Module 4 시뮬레이션으로 전달
```

#### 2.4.2 참고 학습 데이터

- **CityGen (CVPR 2025)**: 무한 확장 가능한 도시 레이아웃 생성 모델
- **한국 도시설계 데이터셋**: 기존 도시계획 승인 도면 (지구단위계획, 택지개발계획)을 학습 데이터로 활용
- **건축물대장 + 3D 건물 데이터**: V-World 3D 건물 + 건축물대장 매칭으로 한국형 도시 패턴 학습

#### 2.4.3 Rhino/Grasshopper 연동

알렉산더님의 기존 워크플로우와 연결:

- **웹 → Grasshopper**: 생성된 배치안을 GeoJSON/IFC로 내보내기 → Grasshopper에서 상세 설계
- **Grasshopper → 웹**: Grasshopper에서 설계한 결과를 다시 웹 플랫폼에 업로드하여 시뮬레이션
- **API 연동**: REST API를 통한 양방향 데이터 교환
- **Hops/Compute 연동**: Rhino Compute 서버를 통한 실시간 파라메트릭 변형

---

### 2.5 Module 4 — Simulation Engine (시뮬레이션 엔진)

**목적**: 생성된 설계안의 환경·교통·에너지 성능을 검증

#### 2.5.1 시뮬레이션 유형

| 시뮬레이션 | 엔진 | 입력 | 출력 |
|------------|------|------|------|
| **일조 분석** | Three.js Raycasting + SunCalc | 3D 매스 모델, 위치, 날짜 | 일조시간 히트맵, 일영도 |
| **풍환경** | OpenFOAM (서버사이드) | 3D 모델, 기상데이터 | 보행자 높이 풍속 맵 |
| **에너지** | EnergyPlus (서버사이드) | 건물 모델, 기상, 재료 | 에너지 사용량, 탄소배출 |
| **교통** | SUMO / 자체 네트워크 분석 | 도로망, O/D 매트릭스 | 교통량, LOS, 통행시간 |
| **보행자** | 자체 Agent-Based Model | 보행 네트워크, 인구 | 보행량 히트맵, 접근성 |
| **소음** | NoiseModelling (오픈소스) | 도로, 건물, 지형 | 소음 등고선 맵 |
| **침수** | 자체 GIS 분석 | DEM, 강우데이터, 배수망 | 침수 위험 지역 맵 |

#### 2.5.2 실시간 경량 시뮬레이션 vs 정밀 시뮬레이션

```
                     실시간 (WebGL/WASM)          정밀 (서버사이드)
일조분석              ✅ Three.js 실시간           ✅ Radiance/Daysim
풍환경                ✅ 간이 CFD (WASM)           ✅ OpenFOAM
에너지                ⚡ 간이 열부하 계산           ✅ EnergyPlus
교통                  ✅ 네트워크 분석              ✅ SUMO 풀시뮬레이션
보행자                ✅ 실시간 ABM                 ✅ 대규모 ABM

⚡ = 간이 모델로 즉시 피드백, 정밀 분석은 비동기 실행
```

사용자 경험: 설계 변경 시 실시간 경량 시뮬레이션으로 즉시 피드백 → 확정 후 정밀 시뮬레이션 비동기 실행 → 결과 알림

---

### 2.6 Module 5 — Report & Export (보고서 및 내보내기)

**목적**: 분석 결과를 실무에서 바로 쓸 수 있는 형태로 출력

#### 2.6.1 출력 형식

| 출력 | 포맷 | 용도 |
|------|------|------|
| **현황분석 보고서** | DOCX/PDF | 도시계획 수주 프로젝트 현황분석 첨부 |
| **인터랙티브 대시보드** | 웹 URL (공유 가능) | 클라이언트/의뢰인에게 공유 |
| **3D 모델** | IFC, glTF, OBJ, 3DM | Rhino, Revit, Unity에서 후속 작업 |
| **GIS 데이터** | GeoJSON, SHP, GeoParquet | QGIS, ArcGIS에서 후속 분석 |
| **시각화 이미지** | PNG/SVG (고해상도) | 보고서/프레젠테이션 삽입 |
| **데이터 테이블** | CSV, XLSX | 스프레드시트 분석 |

#### 2.6.2 AI 자동 보고서 생성

```
사용자: "대구 수성구 범어동 일대 현황분석 보고서 만들어줘"

AI 자동 생성 보고서 목차:
1. 위치 및 대상지 개요
2. 상위계획 검토 (도시기본계획, 용도지역)
3. 인구 및 사회경제 현황
4. 토지이용 현황 분석
5. 교통 및 접근성 분석
6. 생활인프라 현황
7. 환경 분석 (녹지, 대기질, 소음)
8. 부동산 시장 동향
9. 도시건강진단 종합 평가
10. 시사점 및 개선 방향 제언
```

---

### 2.7 Module 6 — Community & Collaboration (커뮤니티 및 협업)

- **프로젝트 공유**: 분석 결과 및 설계안을 팀원과 공유, 코멘트, 버전 관리
- **데이터 레시피 공유**: 사용자가 만든 데이터 조합 분석을 커뮤니티에 공개
- **템플릿 마켓플레이스**: 보고서 템플릿, 분석 워크플로우 공유
- **실시간 협업**: 같은 프로젝트를 여러 사용자가 동시에 편집 (Figma 스타일)

---

## 3. 기술 아키텍처

### 3.1 시스템 아키텍처 전체도

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Client Layer                               │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Next.js 14+ (App Router, React Server Components)           │  │
│  │  ┌─────────┐ ┌─────────┐ ┌──────────┐ ┌──────────────────┐  │  │
│  │  │ MapLibre│ │ Deck.gl │ │ CesiumJS │ │ React Three      │  │  │
│  │  │ GL JS   │ │ (GPU    │ │ (3D Tiles│ │ Fiber (3D Model) │  │  │
│  │  │ (2D Map)│ │ Layers) │ │ Globe)   │ │                  │  │  │
│  │  └─────────┘ └─────────┘ └──────────┘ └──────────────────┘  │  │
│  │  ┌─────────┐ ┌─────────────────┐ ┌────────────────────────┐ │  │
│  │  │ Recharts│ │ AI Chat Panel   │ │ Design Canvas          │ │  │
│  │  │ / D3.js │ │ (Streaming)     │ │ (Fabric.js / Konva)    │ │  │
│  │  └─────────┘ └─────────────────┘ └────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────────┤
│                         API Gateway (Kong / Nginx)                  │
├─────────────────────────────────────────────────────────────────────┤
│                        Backend Services Layer                       │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐               │
│  │  API Server   │ │  AI Agent    │ │  Simulation  │               │
│  │  (FastAPI)    │ │  Service     │ │  Worker      │               │
│  │  - REST API   │ │  (Python)    │ │  (Celery)    │               │
│  │  - WebSocket  │ │  - LangChain │ │  - OpenFOAM  │               │
│  │  - GraphQL    │ │  - LangGraph │ │  - EnergyPlus│               │
│  │               │ │  - RAG       │ │  - SUMO      │               │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘               │
│         │                │                 │                        │
│  ┌──────┴────────────────┴─────────────────┴───────┐               │
│  │              Message Queue (Redis / RabbitMQ)    │               │
│  └──────────────────────┬──────────────────────────┘               │
│                         │                                           │
│  ┌──────────────┐ ┌─────┴────────┐ ┌──────────────┐               │
│  │  Data        │ │  ML Model    │ │  File        │               │
│  │  Pipeline    │ │  Server      │ │  Storage     │               │
│  │  (Airflow/   │ │  (vLLM /     │ │  (MinIO /    │               │
│  │   Prefect)   │ │   TorchServe)│ │   S3)        │               │
│  └──────────────┘ └──────────────┘ └──────────────┘               │
├─────────────────────────────────────────────────────────────────────┤
│                        Data Layer                                   │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌───────────┐│
│  │  PostgreSQL   │ │  Redis       │ │  Qdrant /    │ │ DuckDB    ││
│  │  + PostGIS    │ │  (Cache +    │ │  Weaviate    │ │ (Analytics││
│  │  (Primary DB) │ │   Session)   │ │  (Vector DB) │ │  Engine)  ││
│  └──────────────┘ └──────────────┘ └──────────────┘ └───────────┘│
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 Frontend 기술 스택 상세

| 영역 | 기술 | 선정 사유 |
|------|------|-----------|
| **프레임워크** | Next.js 14+ (App Router) | RSC로 초기 로딩 최적화, API Route로 BFF 패턴 |
| **언어** | TypeScript 5.x | 타입 안전성, 대규모 프로젝트 유지보수 |
| **상태관리** | Zustand + React Query (TanStack) | 경량 글로벌 상태 + 서버 상태 캐싱 |
| **2D 지도** | MapLibre GL JS | 오픈소스, 벡터 타일, 경량 (FCP 0.8s) |
| **GPU 시각화 레이어** | Deck.gl v9 | GPU 기반 대규모 포인트/폴리곤 렌더링, WebGPU 지원 |
| **3D 글로브** | CesiumJS | 3D Tiles 스트리밍, 글로벌 스케일 시각화 |
| **3D 모델 뷰어** | React Three Fiber + Three.js | 건축 매스 모델 인터랙션, IFC 뷰잉 |
| **차트** | Recharts + D3.js | React 네이티브 차트 + 커스텀 시각화 |
| **UI 컴포넌트** | shadcn/ui + Tailwind CSS | 일관된 디자인 시스템, 빠른 개발 |
| **실시간 통신** | Socket.io | AI 스트리밍 응답, 협업 기능 |
| **2D 캔버스** | Fabric.js 또는 Konva | 대지 스케치, 설계 캔버스 |
| **IFC 파서** | web-ifc + IFC.js | 브라우저에서 IFC 파일 직접 파싱·렌더링 |

### 3.3 Backend 기술 스택 상세

| 영역 | 기술 | 선정 사유 |
|------|------|-----------|
| **API 서버** | FastAPI (Python 3.12+) | 비동기, 자동 문서화, ML 생태계와 동일 언어 |
| **GraphQL** | Strawberry (Python) | 복잡한 도시 데이터의 유연한 쿼리 |
| **인증** | NextAuth.js + OAuth 2.0 | 소셜 로그인 + JWT |
| **AI 에이전트** | LangGraph + LangChain | 멀티스텝 추론, 도구 호출, 상태 관리 |
| **LLM 서빙** | vLLM (자체 호스팅) + OpenAI API (폴백) | 비용 최적화, 한국어 성능 |
| **ML 서빙** | TorchServe / Triton Inference Server | 생성 모델 (Diffusion), 예측 모델 서빙 |
| **태스크 큐** | Celery + Redis | 시뮬레이션 등 장시간 작업 비동기 처리 |
| **데이터 파이프라인** | Apache Airflow 또는 Prefect | 공공데이터 주기적 수집·정제 자동화 |
| **파일 저장소** | MinIO (S3 호환) | 3D 모델, 보고서, 데이터셋 저장 |
| **컨테이너** | Docker + Kubernetes | 마이크로서비스 오케스트레이션 |

### 3.4 Database 설계

#### 3.4.1 PostgreSQL + PostGIS (Primary)

```sql
-- 핵심 테이블 구조

-- 1. 공간 데이터 기본 테이블
CREATE TABLE districts (
    id SERIAL PRIMARY KEY,
    bjd_code VARCHAR(10) UNIQUE NOT NULL,  -- 법정동코드
    name VARCHAR(100) NOT NULL,
    province VARCHAR(50),
    city VARCHAR(50),
    dong VARCHAR(50),
    geom GEOMETRY(MultiPolygon, 4326),     -- WGS84 경계
    geom_5179 GEOMETRY(MultiPolygon, 5179), -- UTM-K 투영
    area_sqm DOUBLE PRECISION,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_districts_geom ON districts USING GIST(geom);
CREATE INDEX idx_districts_bjd ON districts(bjd_code);

-- 2. 도시 지표 시계열 데이터
CREATE TABLE urban_indicators (
    id BIGSERIAL PRIMARY KEY,
    district_id INT REFERENCES districts(id),
    indicator_type VARCHAR(50) NOT NULL,   -- 'population', 'aging_rate', etc.
    value DOUBLE PRECISION,
    unit VARCHAR(20),
    measured_at DATE NOT NULL,
    source VARCHAR(100),
    metadata JSONB,
    UNIQUE(district_id, indicator_type, measured_at)
);
CREATE INDEX idx_indicators_type_date ON urban_indicators(indicator_type, measured_at);

-- 3. 건물 데이터
CREATE TABLE buildings (
    id BIGSERIAL PRIMARY KEY,
    pnu VARCHAR(19),                       -- PNU 코드
    district_id INT REFERENCES districts(id),
    geom GEOMETRY(MultiPolygon, 4326),
    height DOUBLE PRECISION,               -- 건물 높이 (m)
    floors_above INT,
    floors_below INT,
    gross_area DOUBLE PRECISION,           -- 연면적
    building_use VARCHAR(100),             -- 건물용도
    built_year INT,
    structure_type VARCHAR(50),
    source VARCHAR(50),                    -- 'vworld', 'overture', 'building_registry'
    properties JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_buildings_geom ON buildings USING GIST(geom);
CREATE INDEX idx_buildings_district ON buildings(district_id);

-- 4. 프로젝트 (사용자 작업)
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID REFERENCES users(id),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    site_geom GEOMETRY(Polygon, 4326),     -- 대상지 경계
    zoning_type VARCHAR(50),               -- 용도지역
    config JSONB,                          -- 프로젝트 설정
    status VARCHAR(20) DEFAULT 'draft',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. 생성된 설계 대안
CREATE TABLE design_alternatives (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id),
    version INT NOT NULL,
    prompt TEXT,                            -- 생성 프롬프트
    layout_geojson JSONB,                  -- 2D 배치 GeoJSON
    model_url VARCHAR(500),                -- 3D 모델 파일 경로 (MinIO)
    ifc_url VARCHAR(500),                  -- IFC 파일 경로
    kpi JSONB,                             -- {far: 198, bcr: 45, units: 320, ...}
    simulation_results JSONB,              -- 시뮬레이션 결과 요약
    is_selected BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. AI 대화 이력
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id),
    user_id UUID REFERENCES users(id),
    messages JSONB[],                      -- [{role, content, tools_used, ...}]
    context JSONB,                         -- 대화 컨텍스트 (분석 범위 등)
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### 3.4.2 Qdrant (Vector DB)

```
용도:
- 도시 데이터 임베딩 저장 (법규 텍스트, 계획 문서, 사례)
- RAG 검색: "이 대지에 적용되는 건폐율 규정은?" → 관련 법규 문서 검색
- 유사 사례 검색: "이 대지와 비슷한 조건의 성공적인 개발 사례는?"

컬렉션:
├── korean_urban_laws    (도시계획법, 건축법, 조례 임베딩)
├── planning_cases       (기존 도시계획 승인 사례 임베딩)
├── research_papers      (도시계획 연구논문 임베딩)
└── data_descriptions    (데이터셋 메타데이터 임베딩)
```

#### 3.4.3 Redis

```
용도:
- API 응답 캐시 (공공데이터 API 결과 TTL 캐싱)
- 실시간 세션 관리
- Celery 메시지 브로커
- Rate Limiting (공공데이터 API 호출 제한 관리)
- 지오펜싱 (GEOADD/GEOSEARCH로 실시간 공간 쿼리)
```

#### 3.4.4 DuckDB (Analytics)

```
용도:
- 대규모 시계열 데이터 분석 (Parquet 파일 직접 쿼리)
- Overture Maps 데이터 가공 (GeoParquet 네이티브 지원)
- 대시보드 집계 쿼리 가속
- 사용자 커스텀 데이터 분석 (업로드된 CSV 실시간 쿼리)
```

### 3.5 AI/ML 모델 파이프라인

```
┌─────────────────────────────────────────────────────────────────┐
│                     ML Model Registry                           │
├──────────────┬──────────────┬──────────────┬───────────────────┤
│  LLM 서비스   │  생성 모델     │  예측 모델    │  비전 모델        │
├──────────────┼──────────────┼──────────────┼───────────────────┤
│ • GPT-4o     │ • Layout     │ • UrbanGPT   │ • 위성영상 분류   │
│   (범용 질의) │   Diffusion  │   (시공간     │ • 건물 탐지       │
│ • SOLAR /    │   Model      │    예측)      │ • 토지피복 분류   │
│   EXAONE     │ • ControlNet │ • 부동산 시세 │ • 변화 감지       │
│   (한국어    │   (조건부     │   예측 모델   │                   │
│    특화)     │    생성)      │ • 교통량     │                   │
│ • Llama 3.1  │              │   예측 모델   │                   │
│   (자체호스팅)│              │              │                   │
└──────────────┴──────────────┴──────────────┴───────────────────┘

학습 파이프라인:
├── 데이터 수집 (Airflow DAG)
├── 전처리 (Pandas + GeoPandas + DuckDB)
├── 학습 (PyTorch + Hugging Face Transformers)
├── 평가 (MLflow Tracking)
├── 배포 (vLLM / TorchServe → K8s)
└── 모니터링 (Prometheus + Grafana)
```

---

## 4. 인프라 및 배포

### 4.1 클라우드 아키텍처

```
┌───────────────────────────────────────────────────────┐
│                    AWS / NCP (네이버 클라우드)          │
├───────────────────────────────────────────────────────┤
│                                                        │
│  ┌──────────────┐   ┌──────────────┐                  │
│  │ CloudFront/  │   │ ALB          │                  │
│  │ CDN          │   │ (Load        │                  │
│  │ (정적 자산)   │   │  Balancer)   │                  │
│  └──────┬───────┘   └──────┬───────┘                  │
│         │                   │                          │
│  ┌──────┴───────────────────┴──────────────────────┐  │
│  │              Kubernetes Cluster (EKS)            │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐           │  │
│  │  │ Frontend│ │ API     │ │ AI      │           │  │
│  │  │ (Next.js│ │ (FastAPI│ │ (vLLM + │           │  │
│  │  │  SSR)   │ │  pods)  │ │ Torch   │           │  │
│  │  │  x2-4   │ │  x2-4   │ │ Serve)  │           │  │
│  │  └─────────┘ └─────────┘ │  GPU x1-2│          │  │
│  │                           └─────────┘           │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐           │  │
│  │  │ Celery  │ │ Airflow │ │ Sim     │           │  │
│  │  │ Workers │ │ Scheduler│ │ Workers │           │  │
│  │  │  x2-4   │ │  x1     │ │ (GPU)   │           │  │
│  │  └─────────┘ └─────────┘ └─────────┘           │  │
│  └─────────────────────────────────────────────────┘  │
│                                                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐│
│  │ RDS      │ │ ElastiC- │ │ S3/MinIO │ │ Redis    ││
│  │ (Post-   │ │ ache     │ │ (File    │ │ (Cache)  ││
│  │  greSQL) │ │ (Redis)  │ │  Store)  │ │          ││
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘│
└───────────────────────────────────────────────────────┘
```

### 4.2 한국 특화 인프라 고려사항

- **데이터 주권**: 한국 내 데이터 저장 필수 → NCP (네이버 클라우드) 또는 AWS 서울 리전
- **공공데이터 API 접근**: 서버가 한국 IP여야 접근 가능한 API 존재
- **GPU 인스턴스**: NCP GPU Server (V100/A100) 또는 AWS p4d 인스턴스
- **비용 최적화**: 시뮬레이션/AI 워크로드는 Spot/선점형 인스턴스 활용

---

## 5. 개발 로드맵

### Phase 0 — Foundation (1-2개월)

> 프로젝트 기반 구축

- [ ] 모노레포 세팅 (Turborepo: Next.js + FastAPI)
- [ ] Docker Compose 로컬 개발 환경
- [ ] PostgreSQL + PostGIS 스키마 설계 및 마이그레이션
- [ ] 인증 시스템 (NextAuth.js)
- [ ] CI/CD 파이프라인 (GitHub Actions → K8s)
- [ ] 디자인 시스템 구축 (shadcn/ui 커스텀 테마)

### Phase 1 — Data Hub MVP (2-3개월)

> 데이터 수집 + 기본 시각화

- [ ] 한국 공공데이터 API 커넥터 개발 (KOSIS, V-World, data.go.kr)
- [ ] 법정동코드 기반 데이터 통합 파이프라인
- [ ] MapLibre GL + Deck.gl 기반 2D 지도 뷰어
- [ ] 데이터 카탈로그 UI
- [ ] 기본 코로플레스 맵, 히트맵, 포인트 맵 시각화
- [ ] 대구시 시범 데이터 로딩 (인구, 건물, 토지이용)

**MVP 산출물**: 대구시 행정동별 인구·토지이용·건물 데이터를 지도 위에 시각화하는 웹앱

### Phase 2 — AI Agent + 3D Globe (2-3개월)

> AI 분석 에이전트 + 3D 시각화

- [ ] CesiumJS 3D 글로브 통합 (V-World 3D Tiles)
- [ ] LangGraph 기반 AI Agent 프레임워크 구축
- [ ] 자연어 도시 질의 → 데이터 조회 → 시각화 파이프라인
- [ ] RAG 시스템 (도시계획법규, 조례 검색)
- [ ] 도시건강진단 대시보드 (대구시 시범)
- [ ] Creative Data Recipes 5종 구현

**MVP 산출물**: 대구시에 대해 자연어로 질문하면 AI가 분석하고 3D 지도 위에 시각화하는 시스템

### Phase 3 — Generative Design (3-4개월)

> AI 배치 생성 + 시뮬레이션

- [ ] 한국 도시설계 데이터셋 구축 (지구단위계획 도면 수집·정제)
- [ ] 조건부 확산 모델 학습 (2D 배치 생성)
- [ ] 2D 배치 → 3D 매스 자동 변환 엔진
- [ ] 법규 검증 모듈 (건폐율, 용적률, 일조, 이격거리)
- [ ] 실시간 일조 시뮬레이션 (Three.js)
- [ ] React Three Fiber 기반 3D 모델 인터랙션
- [ ] IFC 내보내기 (web-ifc)
- [ ] Grasshopper 연동 API

**MVP 산출물**: 대지를 선택하고 조건을 입력하면 AI가 배치안을 생성하고 법규를 검증하는 시스템

### Phase 4 — Advanced Simulation & Reports (2-3개월)

> 정밀 시뮬레이션 + 보고서

- [ ] 서버사이드 시뮬레이션 워커 (OpenFOAM, EnergyPlus, SUMO)
- [ ] 시뮬레이션 결과 3D 시각화 오버레이
- [ ] AI 자동 보고서 생성 (DOCX/PDF)
- [ ] 시공간 예측 모델 (UrbanGPT 아키텍처)
- [ ] 위성영상 분석 모듈 (토지피복 분류, 변화 감지)

### Phase 5 — Platform & Scale (2-3개월)

> 커뮤니티, 협업, 확장

- [ ] 실시간 협업 기능 (Yjs CRDT)
- [ ] 프로젝트 공유 및 권한 관리
- [ ] 데이터 레시피 마켓플레이스
- [ ] 전국 확장 (서울, 부산, 인천 등)
- [ ] 모바일 반응형 최적화
- [ ] Unity WebGL XR 뷰어 연동

### 총 개발 기간: 약 12-18개월

```
Phase 0  ██░░░░░░░░░░░░░░░░░░ (1-2m)
Phase 1  ░░███░░░░░░░░░░░░░░░ (2-3m)
Phase 2  ░░░░░███░░░░░░░░░░░░ (2-3m)
Phase 3  ░░░░░░░░████░░░░░░░░ (3-4m)
Phase 4  ░░░░░░░░░░░░███░░░░░ (2-3m)
Phase 5  ░░░░░░░░░░░░░░░███░░ (2-3m)
```

---

## 6. 데이터 플로우 상세

### 6.1 공공데이터 수집 파이프라인

```
[Airflow DAG: daily_data_sync]

크론: 0 3 * * *  (매일 새벽 3시)

Step 1: API 호출
├── KOSIS 인구통계 → JSON
├── V-World 건물 3D → 3D Tiles
├── data.go.kr 건축물대장 → XML
├── 실거래가 → JSON
└── 기상청 → JSON

Step 2: 정제 & 변환
├── XML/JSON → Pandas DataFrame
├── 좌표계 변환 (EPSG:5174/5179 → 4326)
├── 법정동코드 매칭 & 정규화
├── 이상치 탐지 & 처리
└── GeoParquet 변환 (대용량 데이터)

Step 3: 적재
├── PostGIS (구조화 데이터)
├── MinIO (원본 파일, 3D 모델)
├── DuckDB (분석용 Parquet)
└── Qdrant (텍스트 임베딩)

Step 4: 캐시 갱신
├── Redis 캐시 무효화
└── 프리컴퓨팅 (인기 데이터 조합)
```

### 6.2 AI Agent 실행 플로우

```
사용자 입력
    │
    ▼
[Input Parser] ─── 자연어 의도 분석
    │
    ▼
[Planner (LangGraph)] ─── 실행 계획 수립
    │                       ├── 어떤 데이터가 필요한가?
    │                       ├── 어떤 분석을 수행할 것인가?
    │                       └── 어떤 시각화를 생성할 것인가?
    │
    ▼
[Tool Executor] ──┬── data_fetcher(district="수성구", type="population")
                  ├── spatial_analyzer(method="accessibility", params={...})
                  ├── viz_generator(type="choropleth", data={...})
                  └── report_writer(template="analysis", sections=[...])
    │
    ▼
[Response Synthesizer]
    │
    ▼
스트리밍 응답 + 인터랙티브 시각화 + 다운로드 링크
```

---

## 7. API 설계 (주요 엔드포인트)

### 7.1 REST API

```
# 데이터 허브
GET    /api/v1/data/catalog                    # 데이터셋 목록
GET    /api/v1/data/{dataset_id}               # 데이터셋 상세
GET    /api/v1/data/{dataset_id}/query          # 데이터 조회 (필터, 집계)
POST   /api/v1/data/upload                      # 커스텀 데이터 업로드

# 공간 분석
GET    /api/v1/spatial/districts                # 행정구역 목록
GET    /api/v1/spatial/districts/{bjd_code}     # 행정구역 상세 (기하 포함)
POST   /api/v1/spatial/analysis                 # 공간 분석 실행
GET    /api/v1/spatial/buildings                 # 건물 데이터 (bbox 필터)
POST   /api/v1/spatial/accessibility            # 접근성 분석

# AI 에이전트
POST   /api/v1/ai/chat                          # AI 대화 (SSE 스트리밍)
GET    /api/v1/ai/sessions/{session_id}         # 대화 이력
POST   /api/v1/ai/predict                       # 시공간 예측

# 생성형 설계
POST   /api/v1/design/generate                  # 레이아웃 생성
GET    /api/v1/design/alternatives/{id}         # 대안 조회
POST   /api/v1/design/validate                  # 법규 검증
POST   /api/v1/design/export                    # 모델 내보내기 (IFC, glTF)

# 시뮬레이션
POST   /api/v1/simulation/run                   # 시뮬레이션 시작
GET    /api/v1/simulation/{job_id}/status        # 진행 상태
GET    /api/v1/simulation/{job_id}/result        # 결과 조회

# 프로젝트
POST   /api/v1/projects                         # 프로젝트 생성
GET    /api/v1/projects/{id}                     # 프로젝트 상세
PUT    /api/v1/projects/{id}                     # 프로젝트 수정

# 보고서
POST   /api/v1/reports/generate                  # 보고서 자동 생성
GET    /api/v1/reports/{id}/download             # 보고서 다운로드
```

### 7.2 WebSocket

```
ws://api/v1/ws/chat/{session_id}       # AI 실시간 스트리밍
ws://api/v1/ws/collab/{project_id}     # 실시간 협업
ws://api/v1/ws/simulation/{job_id}     # 시뮬레이션 진행 업데이트
```

### 7.3 GraphQL (복잡 쿼리용)

```graphql
type Query {
  district(bjdCode: String!): District
  buildings(bbox: BBox!, filters: BuildingFilter): BuildingConnection
  indicators(
    districts: [String!]!
    types: [IndicatorType!]!
    dateRange: DateRange!
  ): [IndicatorTimeSeries!]!

  projectAnalysis(projectId: ID!): ProjectAnalysis
}

type District {
  bjdCode: String!
  name: String!
  geometry: GeoJSON!
  area: Float!
  indicators(types: [IndicatorType!]): [Indicator!]!
  buildings(limit: Int): [Building!]!
  healthScore: UrbanHealthScore
}
```

---

## 8. 보안 및 성능

### 8.1 보안

- **인증**: OAuth 2.0 (Google, Kakao 소셜 로그인) + JWT
- **인가**: RBAC (역할 기반 접근 제어) — Admin, Professional, Researcher, Free
- **API 보안**: Rate Limiting, API Key 관리, CORS
- **데이터 보호**: 개인정보 비식별화, 데이터 암호화 (AES-256)
- **공공데이터 API 키 관리**: 서버사이드에서만 API 키 사용 (클라이언트 노출 방지)

### 8.2 성능 최적화

| 영역 | 전략 |
|------|------|
| **지도 렌더링** | 벡터 타일 LOD, 뷰포트 기반 데이터 로딩, WebWorker 파싱 |
| **3D 모델** | 3D Tiles 스트리밍, DRACO 압축, 인스턴스 렌더링 |
| **데이터 쿼리** | PostGIS 공간 인덱스, DuckDB 컬럼 스토어, Redis 캐시 |
| **AI 응답** | SSE 스트리밍, KV Cache, vLLM Paged Attention |
| **시뮬레이션** | WebAssembly 경량 모델, GPU 서버 큐 관리 |
| **초기 로딩** | Next.js ISR/SSG, 코드 스플리팅, 이미지 최적화 |

### 8.3 모니터링

```
Prometheus + Grafana: 서버 메트릭
Sentry: 프론트엔드/백엔드 에러 트래킹
PostHog: 사용자 행동 분석
Uptime Kuma: 외부 API 헬스체크 (공공데이터 API 가용성 모니터링)
```

---

## 9. 비즈니스 모델 (참고)

### 9.1 SaaS 요금제 구조

| 티어 | 가격 (월) | 데이터 | AI | 시뮬레이션 | 프로젝트 |
|------|-----------|--------|-----|-----------|---------|
| **Free** | 0원 | 기본 공공데이터 | 일 5회 질의 | 실시간만 | 1개 |
| **Pro** | 99,000원 | 전체 데이터 | 무제한 질의 | 정밀 포함 | 10개 |
| **Team** | 299,000원 | 전체 + API | 무제한 + 커스텀 모델 | 우선 큐 | 무제한 |
| **Enterprise** | 별도 협의 | 온프레미스 | 전용 GPU | 전용 서버 | 무제한 |

### 9.2 추가 수익원

- **데이터 마켓플레이스**: 프리미엄 데이터셋 판매 (부동산 시세 예측 등)
- **컨설팅**: 도시계획 AI 적용 컨설팅
- **API 과금**: 외부 서비스에서 URBANIS 분석 기능 호출
- **교육**: 도시 데이터 분석 교육 프로그램

---

## 10. 리스크 및 대응 전략

| 리스크 | 영향 | 확률 | 대응 |
|--------|------|------|------|
| 공공데이터 API 변경/중단 | 높음 | 중 | 주기적 스냅샷 백업, 다중 소스 폴백 |
| LLM 비용 증가 | 중 | 중 | 자체 호스팅 LLM 확대, 캐시 적극 활용 |
| 생성 모델 품질 부족 | 높음 | 높 | 단계적 접근 (룰 기반 → AI 보조 → 완전 생성) |
| 데이터 정확도 이슈 | 높음 | 중 | 데이터 품질 대시보드, 사용자 피드백 루프 |
| GPU 인프라 비용 | 중 | 중 | Spot 인스턴스, 배치 처리, 모델 경량화 |
| 법규 변경 | 중 | 저 | RAG 기반 법규 DB 실시간 업데이트 |

---

## 11. 핵심 오픈소스 및 참고 자료 목록

### 11.1 프론트엔드

| 도구 | 용도 | 라이선스 | URL |
|------|------|----------|-----|
| Next.js | 프레임워크 | MIT | nextjs.org |
| MapLibre GL JS | 2D 벡터 지도 | BSD-3 | maplibre.org |
| Deck.gl | GPU 시각화 레이어 | MIT | deck.gl |
| CesiumJS | 3D 글로브 | Apache 2.0 | cesium.com |
| React Three Fiber | 3D 모델 렌더링 | MIT | github.com/pmndrs/react-three-fiber |
| Kepler.gl | 대규모 데이터 시각화 | MIT | kepler.gl |
| web-ifc | IFC 파서 (WASM) | MPL 2.0 | github.com/IFCjs/web-ifc |
| Turf.js | 클라이언트 공간분석 | MIT | turfjs.org |

### 11.2 백엔드 & AI

| 도구 | 용도 | URL |
|------|------|-----|
| FastAPI | API 서버 | fastapi.tiangolo.com |
| LangGraph | AI 에이전트 프레임워크 | github.com/langchain-ai/langgraph |
| vLLM | LLM 서빙 | github.com/vllm-project/vllm |
| PyTorch | ML 학습 프레임워크 | pytorch.org |
| Hugging Face Diffusers | 확산 모델 | github.com/huggingface/diffusers |
| IfcOpenShell | IFC 처리 (Python) | ifcopenshell.org |
| Apache Airflow | 데이터 파이프라인 | airflow.apache.org |

### 11.3 시뮬레이션

| 도구 | 용도 | URL |
|------|------|-----|
| SUMO | 교통 시뮬레이션 | eclipse.dev/sumo |
| OpenFOAM | CFD (풍환경) | openfoam.org |
| EnergyPlus | 건물 에너지 | energyplus.net |
| NoiseModelling | 소음 시뮬레이션 | noise-planet.org |

### 11.4 참고 플랫폼/논문

| 이름 | 유형 | 참고 사항 |
|------|------|-----------|
| UrbanGPT 2.0 (Pebblous) | 상용 서비스 | 텍스트 → 3D 도시 레이아웃 생성 |
| UrbanGPT (HKU) | 학술 논문 | 시공간 LLM, KDD 2024 |
| CityGen (CVPR 2025) | 학술 논문 | 무한 도시 레이아웃 생성 |
| 서울 S-Map | 공공 플랫폼 | 서울 디지털 트윈 |
| Morphocode Explorer | 상용 서비스 | 인터랙티브 도시 분석 |
| AlphaEarth (Google) | 연구 | 위성 임베딩 |

---

## 12. 즉시 시작 가능한 액션 아이템

### Quick Win: 대구시 데이터 대시보드 프로토타입 (2주)

```
목표: 대구시 8개 구·군의 핵심 도시 지표를 지도 위에 시각화하는 정적 웹사이트

기술: Next.js + MapLibre GL + Deck.gl + 공공데이터 API
데이터: 인구(KOSIS) + 건물(V-World) + 토지이용(data.go.kr)
배포: Vercel (무료 호스팅)

이것만으로도:
- 기술 스택 검증
- 데이터 파이프라인 프로토타이핑
- 포트폴리오 / 투자 유치 데모
```

---

> **이 기획서는 URBANIS 프로젝트의 기술적 청사진이다. 각 Phase는 독립적으로 가치를 제공하도록 설계되어 있으며, MVP부터 시작하여 점진적으로 확장하는 것을 권장한다.**
