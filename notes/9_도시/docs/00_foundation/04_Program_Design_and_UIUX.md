# 04. 지능형 도시 분석 도구 UI/UX 및 프로그램 설계 (Updated)

이 문서는 Hybrid AI Stack(Gemini + Claude)을 기반으로 한 **실시간 지리공간 추적 및 도시 분석 시스템**의 아키텍처와 사용자 경험을 정의합니다.

## 1. 시스템 아키텍처 (Hybrid AI Stack)

### 1.1 Backend: FastAPI + WebSocket Hub
*   **Broadcast Loop:** 10초 주기로 수집 및 분석 사이클을 실행합니다.
*   **Async Ingestion:** `OpenSky`(항공), `DOT Cams`(교통), `Sentinel`(위성) 데이터를 병렬 비동기로 수집.
*   **Detection Orchestrator:** Gemini 3.1 Pro Vision API를 호출하여 이미지 내 객체를 탐지하고 GeoJSON으로 병합.
*   **Validation:** Pydantic 스키마를 통해 맵으로 전달되기 전 데이터 무결성을 강제합니다.

### 1.2 Frontend: React + Mapbox GL JS
*   **WebSocket Interface:** `/ws/live` 엔드포인트를 통해 10초마다 갱신된 GeoJSON 수신.
*   **Real-time Rendering:**
    *   **Aircraft Layer:** 고도(Altitude)에 따른 색상 보간 (지상: 초록 → 고고도: 빨강).
    *   **Vehicle Layer:** 실시간 감지된 차량을 청록색 포인트로 표시.
    *   **HUD Overlay:** 추적 객체 수, 시스템 상태, AI 분석 신뢰도를 실시간 표시.

## 2. 핵심 UI 기능 (Program Features)

### 2.1 인터랙티브 시나리오 플레이어
*   **Time-Travel Control:** 실시간 데이터뿐만 아니라 과거 로그 데이터를 재생하며 도시 변화 양상을 관찰.
*   **AI Routing Control:** 사용자가 특정 카메라를 지정하여 Gemini에게 정밀 분석(예: "차종 분류 및 번호판 인식")을 요청하는 기능.

### 2.2 하이브리드 인터페이스 (LUI + GUI)
*   **Command Bar (Claude-powered):** 자연어로 시스템 설정을 변경하거나 복잡한 질의 수행.
*   **Visual Web Scraper (Gemini-powered):** 지도 상의 특정 영역을 캡처하여 즉시 도시 계획적 관점에서 분석 보고서 생성.

## 3. 기술 스택 요약

| 계층 | 기술 | 비고 |
| :--- | :--- | :--- |
| **언어/로직** | Python 3.10+, TypeScript | Claude 4.6이 주로 코드 생성 및 관리 |
| **웹 프레임워크** | FastAPI | WebSocket 브로드캐스트 전용 |
| **AI 모델** | Gemini 3.1 Pro + Claude 4.6 | **Hybrid AI Routing** 적용 |
| **지도 엔진** | Mapbox GL JS (Dark-v11) | 실시간 GeoJSON 소스 업데이트 |
| **데이터 검증** | Pydantic | AI 응답 유효성 강제 |
| **브리지 도구** | MCP (Model Context Protocol) | 모델 간 서브에이전트 통신 및 툴 라우팅 |

## 4. 확장성 및 실무 연계 (Stage 10: Smart City)
*   **Digital Twin 연동:** WebSocket으로 수신된 데이터를 Unity 또는 Grasshopper로 중계하여 실시간 파라메트릭 설계 피드백 루프 구축.
*   **Cost Efficiency:** 프레임당 약 $0.002 수준의 비용으로 커피 한 잔 가격에 실시간 도시 감시 대시보드 운영 가능.

---
*본 가이드는 대구 도시 계획 프로젝트의 실시간 데이터 분석 레이어 구현을 위한 최종 설계도로 활용됩니다.*
