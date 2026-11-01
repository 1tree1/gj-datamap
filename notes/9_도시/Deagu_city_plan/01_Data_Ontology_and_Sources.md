# 01. 도시 데이터 온톨로지 및 수집 전략 가이드 (Updated)

이 문서는 대한민국의 도시 분석을 위한 데이터 종류와 수집 방법, 그리고 이를 의미론적으로 구조화하기 위한 온톨로지 설계 및 **실시간 데이터 파이프라인** 구축 전략을 다룹니다.

## 1. 도시 데이터 온톨로지 (Urban Data Ontology) 설계
데이터를 단순한 테이블이 아닌 **의미론적 연결망(Knowledge Graph)**으로 구성하여, AI가 도시의 상관관계를 추론할 수 있게 합니다.

### 1.1 핵심 클래스 및 속성
*   **Spatial Object:** 건물(Building), 도로(Road), 공원(Park), 필지(Parcel)
*   **Real-time Moving Object:** 항공기(Aircraft), 차량(Vehicle), 보행자(Pedestrian) - *New: 실시간 추적 객체 추가*
*   **Relationship:** `isLocatedIn`, `connectsTo`, `observedBy` (카메라-객체 관계)

## 2. 데이터 소스 및 수집 체계 (Hybrid Sourcing)

| 데이터 유형 | 주요 소스 | 수집 방식 | 특징 |
| :--- | :--- | :--- | :--- |
| **3D 건물/지형** | Vworld API | REST API / WFS | 국가 표준 3D 모델 및 DEM |
| **토지/도시계획** | NSDI | Open API / Bulk | 용도지역, 지적도, 공시지가 |
| **실시간 항공** | [OpenSky Network](https://opensky-network.org/) | REST API | 항공기 ICAO24, 위경도, 고도, 속도 (무료) |
| **실시간 교통** | DOT Traffic Cams | JPEG Snapshot | 교통 카메라 프레임 (Gemini Vision 분석 필요) |
| **실시간 위성** | Sentinel Hub | WMS (GetMap) | 위성 영상 타일 (토지이용 변화 감지용) |

## 3. 수집 및 유지보수 자동화 (ETL & Validation)

### 3.1 Hybrid AI Routing 수집 전략
*   **Claude (Architect):** 비동기 수집 파이프라인(`httpx`, `asyncio`) 설계 및 백엔드 로직 리팩토링.
*   **Gemini (Analyst):** 교통 카메라나 위성 영상 등 **비정형 이미지 데이터**를 실시간 분석하여 구조화된 JSON으로 변환.

### 3.2 Pydantic을 통한 데이터 무결성 보장
AI(Gemini)가 생성한 자유 형식의 JSON 응답이 시스템을 크래시시키지 않도록 **Pydantic 스키마**로 엄격하게 검증합니다.
*   `DetectionResponse`: 카테고리, 좌표(lat/lon), 신뢰도(confidence), Bounding Box 포함.
*   **유지보수:** 10초 주기 브로드캐스트 루프를 통해 데이터 최신성 유지.

## 4. 데이터 유형 분류
1.  **Vector Data:** GeoJSON FeatureCollection (항공기 위치, 차량 감지 좌표)
2.  **Semantic Data:** RDF/OWL (도시 구성 요소 간의 의미 관계)
3.  **Real-time Stream:** WebSocket (ws://) 기반의 실시간 위치 데이터 스트림

---
*Next: 02_Urban_Analysis_Theories.md (변경 없음) / 03_AI_Simulation_and_Prediction.md 에서 Hybrid AI 분석을 다룹니다.*
