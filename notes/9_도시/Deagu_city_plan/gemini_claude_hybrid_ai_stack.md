# 🚀 The Ultimate AI Stack: Gemini 3.1 + Claude 4.6

> **원문 출처**: bilawalsidhu (ex-Google PM) on X
> **핵심 주제**: 두 AI 모델을 결합한 실시간 지리공간 추적 시스템 구축

---

## 1. 핵심 아이디어: Hybrid AI Workflow

2026년 현재 **단일 모델 만능주의**가 아닌 **Hybrid AI Routing** — 각 모델의 강점에 맞게 태스크를 분배하는 접근이 주류.

| 역할 | 모델 | 강점 |
|------|------|------|
| **Architect / Engineer** | **Claude 4.6** | 소프트웨어 엔지니어링, 로직, 백엔드 아키텍처, 리팩토링, 디버깅 |
| **Eyes & Ears (Analyst)** | **Gemini 3.1** | 멀티모달 (비전), 1M+ 토큰 컨텍스트, 비주얼 웹 스크래핑, 실시간 데이터 분석 |

> **분업 원리**: Claude가 시스템 아키텍처를 설계하고, Gemini가 대규모 라이브 지리공간 데이터를 처리하는 "눈과 귀" 역할

---

## 2. 두 모델을 연결하는 3가지 방법

### Method 1: `clink` CLI Bridge (PAL MCP Server)

- **오픈소스**: [BeehiveInnovations/gemini-mcp-server](https://github.com/BeehiveInnovations/gemini-mcp-server)
- Claude Code 세션 내에서 **Gemini 서브에이전트를 직접 생성**
- Gemini가 격리 환경에서 비주얼 분석 수행 → 구조화된 JSON만 Claude에 반환
- Claude의 컨텍스트 윈도우 오염 방지

```bash
clink with gemini panoptic_analyzer to audit live_traffic_feed.jpg for vehicle coordinates
```

### Method 2: Custom Bash Wrapper (경량 방식)

- Gemini CLI 설치 후 `/gemini` 슬래시 커맨드로 호출
- 추가 의존성 없이 Claude Code → Gemini CLI 트리거

```bash
# 1. Gemini CLI 설치
npm install -g @google/gemini-cli
export GEMINI_API_KEY=your_key_here

# 2. Wrapper 스크립트 생성 (~/.claude/bin/gemini-clean)
#!/bin/bash
output=$(gemini "$@" 2>&1)
echo "$output" | jq -r '.response' 2>/dev/null || echo "$output"
```

### Method 3: Enterprise — Composio MCP (24/7 자동화)

- Anthropic Claude Agent SDK + Gemini MCP Server + Composio 툴 라우터
- 자동화된 에이전틱 루프 (예: 24시간 항공기 좌표 스캔 봇)
- Claude가 계획 수립 → `call_gemini_vision()` 도구 호출 → Gemini 처리 → Claude가 DB 업데이트

---

## 3. Blueprint: 실시간 지리공간 추적 시스템

### 전체 아키텍처

```
┌─────────────────────────────────────────────────────┐
│                    FRONTEND                          │
│  React + Mapbox GL JS (dark-v11)                    │
│  WebSocket으로 10초마다 GeoJSON 수신                   │
│  - Aircraft Layer (고도별 색상)                        │
│  - Vehicle Layer (카메라 감지)                         │
│  - HUD 오버레이 (실시간 통계)                           │
└────────────────────┬────────────────────────────────┘
                     │ WebSocket (ws://localhost:8000/ws/live)
┌────────────────────┴────────────────────────────────┐
│                BACKEND (FastAPI)                      │
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │         broadcast_loop() — 10초 주기           │   │
│  │              run_detection_cycle()             │   │
│  └──────┬────────────────────┬──────────────────┘   │
│         │                    │                       │
│  ┌──────┴──────┐     ┌──────┴──────────────┐       │
│  │  INGESTION   │     │    ANALYSIS          │       │
│  │  (데이터 수집)  │     │    (분석 엔진)        │       │
│  │              │     │                      │       │
│  │ • OpenSky    │     │ • Gemini 3.1 Pro     │       │
│  │   (항공기 API) │     │   (Vision API)       │       │
│  │ • DOT Cams   │     │ • Panoptic Detection │       │
│  │   (교통 카메라) │     │   (물체 감지 오케스트레이터)│       │
│  │ • Sentinel   │     │                      │       │
│  │   (위성 영상)  │     │                      │       │
│  └─────────────┘     └──────────────────────┘       │
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │  SCHEMAS (Pydantic) — 데이터 유효성 검증         │   │
│  │  AircraftPosition / Detection / DetectionResponse│   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

### 프로젝트 구조

```
geospatial-tracker/
├── backend/
│   ├── main.py              # FastAPI + WebSocket 허브
│   ├── ingestion/
│   │   ├── opensky.py        # 항공기 실시간 위치 (OpenSky API)
│   │   ├── traffic_cams.py   # 교통 카메라 프레임 캡처 (DOT)
│   │   └── satellite.py      # 위성 영상 타일 (Sentinel Hub)
│   ├── analysis/
│   │   ├── gemini_client.py  # Gemini Vision API 래퍼
│   │   └── panoptic.py       # 감지 오케스트레이터
│   ├── models/
│   │   └── schemas.py        # Pydantic 데이터 모델
│   └── config.py
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── LiveMap.tsx    # Mapbox GL JS 맵
│   │   │   ├── PlaneLayer.tsx
│   │   │   ├── VehicleLayer.tsx
│   │   │   └── CameraPanel.tsx
│   │   └── hooks/
│   │       └── useWebSocket.ts
│   └── package.json
├── docker-compose.yml
└── .env
```

---

### Step 1: 데이터 수집 파이프라인 (Claude 담당)

3개 데이터 소스에서 실시간 데이터 수집:

| 데이터 소스 | API | 데이터 유형 | 비용 |
|------------|-----|-----------|------|
| **OpenSky Network** | REST API (states/all) | 항공기 위치 (ICAO24, callsign, 위경도, 고도, 속도, 방향) | **무료** (5req/10s) |
| **DOT Traffic Cameras** | JPEG Snapshot URL | 교통 카메라 프레임 (Caltrans 등 주정부 공개 피드) | **무료** |
| **Sentinel Hub** | WMS (GetMap) | Sentinel-2 위성 영상 타일 (TRUE_COLOR) | **무료** (30K req/월) |

**핵심 설계**:
- `httpx.AsyncClient`로 비동기 수집
- OpenSky → 이미 **구조화된 JSON** (Gemini 불필요)
- Traffic Cam → **JPEG 바이너리** (Gemini Vision 분석 필요)
- Sentinel → **위성 타일** (Gemini Vision 분석 가능)

---

### Step 2: Panoptic Detection (Gemini 담당)

카메라 프레임 / 위성 타일 → Gemini 3.1 Pro Vision API → 구조화된 감지 결과

**Gemini 시스템 프롬프트 핵심**:
- 감지 카테고리: vehicles, aircraft, pedestrians, infrastructure
- 각 객체별 반환: category, estimated_lat/lon, confidence, bounding_box, attributes
- 카메라 메타데이터(위치, 방향, FOV) → Gemini가 실세계 좌표 추정
- `response_mime_type: "application/json"` 강제로 JSON만 반환

**Detection Orchestrator** (핵심 로직):
```
1. OpenSky에서 항공기 데이터 수집 (구조화 API → Vision 불필요)
2. 모든 교통 카메라에서 프레임 캡처
3. 각 프레임을 Gemini에 전송 → Panoptic Detection
4. 모든 결과를 단일 GeoJSON FeatureCollection으로 병합
```

- 항공기 = `source: "opensky"`
- 차량/보행자 = `source: "camera:{cam_id}"`, `source_model: "gemini-3.1-pro"`

---

### Step 3: WebSocket 실시간 허브 (Claude 담당)

- FastAPI WebSocket 엔드포인트 (`/ws/live`)
- `broadcast_loop()`: 10초마다 → `run_detection_cycle()` → GeoJSON → 모든 연결 클라이언트에 브로드캐스트
- 연결 관리: `connected_clients` 리스트, disconnect 자동 정리

---

### Step 4: 프론트엔드 맵 (Claude 담당)

- **Mapbox GL JS** (dark-v11 스타일)
- **Aircraft Layer**: `circle` 타입, 고도별 색상 보간 (지상=초록, 5000m=주황, 12000m=빨강)
- **Vehicle Layer**: `circle` 타입, 반경 4px, 청록색
- **HUD 오버레이**: 추적 항공기 수, 감지 차량 수, 실시간 표시
- WebSocket `onmessage` → GeoJSON 소스 업데이트 + 통계 갱신

---

### Step 5: Pydantic 스키마 — 데이터 무결성 보장

Gemini의 자유 형식 JSON 응답을 **Pydantic으로 엄격하게 검증**:

| 스키마 | 역할 |
|--------|------|
| `AircraftPosition` | OpenSky 항공기 데이터 (icao24, callsign, 위치, 속도 등) |
| `Detection` | Gemini 감지 결과 단일 객체 (category, lat/lon, confidence, bbox, attributes) |
| `DetectionResponse` | Gemini 전체 응답 래퍼 — **맵 도달 전 데이터 보장** |

> **핵심**: `DetectionResponse(detections=raw_json)` — Gemini의 malformed 응답이 맵 전체를 크래시시키는 것을 방지

---

## 4. 비용 분석

| 구성요소 | 비용 |
|---------|------|
| OpenSky API | **무료** (rate limit 있음) |
| Gemini 3.1 Pro (Vision) | ~$0.002/프레임 |
| Sentinel Hub (위성) | **무료** (30K req/월) |
| Mapbox | **무료** (50K loads/월) |
| Claude 4.6 (코드 생성) | ~$0.30 (프로젝트 전체) |

> **6대 카메라 × 10초 간격 = 약 $3.10/일** — 커피 한 잔 가격으로 실시간 감시 대시보드 운영

---

## 5. 도시계획 적용 가능성

이전 연구한 **10단계 도시개발 프로세스**와 연결:

| 적용 단계 | 활용 방식 |
|----------|----------|
| **Stage 2: 현황분석** | 교통 카메라 피드 → Gemini Vision으로 실시간 교통량/보행자 패턴 자동 분석 |
| **Stage 5: 교통계획** | OpenSky + DOT 카메라 데이터 → 실시간 교통 흐름 모니터링, 병목 구간 식별 |
| **Stage 8: 도시설계** | 위성 영상 + Gemini Panoptic → 토지이용 현황 자동 분류, 변화 감지 |
| **Stage 10: 스마트시티** | 전체 파이프라인 = **디지털 트윈의 실시간 데이터 레이어** 구현 |

### Grasshopper / Unity 연계 시나리오

```
[교통 카메라] → Gemini Vision → GeoJSON
                                    ↓
                          [Python 중간 처리]
                           ↙              ↘
              Grasshopper (GHPython)    Unity (WebSocket)
              도시 형태 파라메트릭        XR 디지털 트윈
              피드백 루프               실시간 시각화
```

- **Grasshopper**: GeoJSON → GHPython 컴포넌트로 수신 → 교통 밀도 기반 도로 폭/블록 크기 파라메트릭 조절
- **Unity**: WebSocket으로 GeoJSON 실시간 수신 → 3D 도시 모델 위에 차량/항공기 실시간 오버레이 → XR 체험

---

## 6. 핵심 기술 패턴 요약

### Hybrid AI Routing 원칙

```
사용자 요청
    │
    ├── 코드 생성 / 아키텍처 / 로직 → Claude 4.6
    ├── 이미지 분석 / 대용량 컨텍스트 → Gemini 3.1
    └── 연결 → MCP Bridge (clink / Bash wrapper / Composio)
```

### 데이터 플로우 패턴

```
Raw Data Sources (API/카메라/위성)
    │
    ▼
Async Ingestion (httpx + asyncio)
    │
    ├── 구조화 데이터 → 바로 사용 (OpenSky)
    └── 비구조화 데이터 → Gemini Vision → 구조화
    │
    ▼
Pydantic Validation (스키마 강제)
    │
    ▼
GeoJSON FeatureCollection (통합)
    │
    ▼
WebSocket Broadcast (FastAPI, 10초 주기)
    │
    ▼
Mapbox GL JS 실시간 렌더링
```

### 핵심 교훈

1. **모델은 라우팅하는 것** — 하나의 모델에 모든 것을 맡기지 않음
2. **MCP가 신경계** — 모델 간 통신 인프라가 핵심
3. **Pydantic이 접착제** — AI의 자유 형식 출력을 엄격하게 검증해야 시스템이 안정적
4. **비동기가 기본** — 다수 데이터 소스 + AI 분석을 `asyncio.gather()`로 병렬 처리
5. **GeoJSON이 공용어** — 모든 이종 데이터를 하나의 FeatureCollection으로 통합
