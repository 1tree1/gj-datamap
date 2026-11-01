# 과제 B — '데이터 기반 + 파라메트릭 마스터플래닝' 플랫폼·방법론 지형도

- 작성일: 2026-10-06 (코디네이터 지시에 따라 신규 검색을 멈추고, 이미 열어본 원문 기준으로 마무리)
- 대상: 구경주역 지구단위계획 마스터플랜(계획경계 218,478㎡ / 시 구상 면적 79,438㎡ — 두 수치가 다름)

## 요약 (8줄)

1. 지형: '유형 라이브러리 × 원단위 × 시나리오 × KPI' 구조는 UrbanFootprint v1.0(2012; Place Type 35+, Building Type 50~90+, 5.5에이커 격자 셀)과 ArcGIS Urban(space types·building types·metrics)에서 문서로 확인된다. CityFinder형 설계는 이 계열이다. 다만 의뢰인이 참조한 'Intelligent Urban Development Modelling Platform / CityFinder' 자체의 공개 문서는 찾지 못했다 [미확인].
2. 파레토·최적화를 제공하는 상용 도구는 확인되지 않았다. Forma(2025.04 블로그)는 생성→평가→사용자 필터, Delve는 우선순위 기반 순위화 후 2026.05 종료, DBF는 '순위화된 시나리오'(벤더 주장). 의뢰인의 NSGA-III + hard constraint + 파레토 구성은 상용 도구에 없다.
3. 공급 지속성이 약하다: Delve 종료, Cityzenith 사실상 중단 추정, UrbanFootprint는 2025.06 LightBox 인수 후 데이터·분석 앱 중심으로 재편된 것으로 보임, ArcGIS Urban은 2026.07 릴리스에서 구 메트릭 폐기를 예고.
4. 불확실성 표기·hard constraint·결정 근거 추적·한국 법정 지표는 확인한 공개 자료에서 거의 비어 있다. 예외는 UrbanSim 문서(개별 예측은 맞을 가능성이 낮으니 집계·다회 실행 분포를 쓰라는 서술)와 UrbanSim의 zoning·보호지 '개발 불가' 처리(MTC 2017).
5. 학술(a): PSS의 보고된 가치는 학습·소통·협업(Pelzer 2014, Goodspeed 2016)이고, 정량 정보가 많다고 결과가 좋아지지 않았다(Arciniegas 2013 [스니펫]). 지표·대시보드는 조작·방법론 미명시 위험(Kitchin 2015), 목표화 시 게이밍(Bevan & Hood 2006), 인증 점수와 실측 불일치(Newsham 2009), 추정치 상위 선택의 사후 실망(Smith & Winkler 2006)이 확인된다. 단, 도시설계 대시보드가 설계를 왜곡했다는 직접 실증 연구는 확인하지 못했다 [미확인].
6. 학술(b): IPCC 2006 식 3.1(독립·변동계수 약 0.3 이하)은 곱의 상대 불확실성을 제곱합 제곱근으로 합산 → ±30% 원단위 4개의 곱은 약 ±60% [계산: 본 보고자]. 대응은 범위 + 계보(NUSAP/pedigree) + Monte Carlo.
7. 결론: 1인 최소 구성 = 유형 라이브러리 8~12종 + 원단위 표(low/mode/high·T등급·출처) + 대안 A–E 비교(Monte Carlo P10–P90·순위 역전 확률) + 단순 현금흐름 + 추적 열. 상용 도구는 일조·바람·소음 검증 보조로만 쓰는 편이 낫다.
8. 제약: 세션 WebSearch 예산(200/200) 소진 이후 신규 검색 불가. Autodesk 제품 페이지·Elsevier·Nature·일부 국내 포털은 403/리다이렉트/404로 열리지 않아 해당 항목은 [스니펫] 또는 [미확인].

---

## 0. 기존 정리와의 관계 · 표기 규칙 · 조사 한계

**기존 정리와의 관계 (한 줄씩)**
- `work/20260928_데이터기반_도시설계_기법_사례_검증_v1.md`: 분석 기법(공간구문론·ABM·HIA·최적화)과 해외 사례 수치 검증이 중심이라 이번 조사(플랫폼 구조·PSS 문헌)와 거의 겹치지 않는다. 겹친 2건만 재확인: (1) Forma는 파레토 최적화기가 아님 — 2025.04 Autodesk 블로그가 생성·평가·사용자 필터만 서술(§1 표 A). (2) Delve 종료 — delve.sidewalklabs.com이 sunset 파라미터를 단 302 리다이렉트로 Google Earth 페이지로 넘어감 [확인]. 라벨 차이 1건: 기존 정리 B4가 Forma–Stantec 사례를 T2로 표기했으나, 이번 규칙(벤더 자료=T4)으로는 T4.
- `docs/00_foundation/URBANIS_기술레퍼런스_14개_분석전통.md`: §13 도시 대사(Kennedy 등 7개 흐름: 물·에너지·폐기물·이동·재료·기후/배출·생물/식량)가 CityFinder형 입력 탭(Carbon/Water/Food/Waste/Transport/Materials)의 이론적 모체. §9 디지털트윈(Seoul S-Map 등)과 일부 겹치며, S-Map은 이번에 2021.04 서울시 보도자료로 재확인. (이 문서의 수치는 이번 세션에서 재검증하지 않음)

**표기 규칙**
- 출처등급: T1 법정문서 / T2 공공발간·기관 공식 문서 / T3 학술 / T4 언론·회사 홍보·블로그·벤더(벤더 기술 문서 포함).
- 확인수준: [확인] 직접 열어본 1차 출처에서 확인 / [확인-초록] 논문 초록·서지DB(Crossref·OpenAlex·PubMed·기관 저장소)에서 확인, 본문 미열람 / [스니펫] 검색 결과 요약·2차 요약만 본 것 / [추정] 보고자 판단 / [미확인].
- "계산:"은 원문 수치로 본 보고자가 계산한 값.
- 저작권 때문에 원문은 인용하지 않고 전부 의역했다.

**조사 한계**
- 세션 WebSearch 예산(200/200)이 중간에 소진되어 이후 항목(Newsham 외 일부 논문의 보강 검색 등)은 직접 URL 열람·서지 API(Crossref/OpenAlex/Semantic Scholar/PubMed)로만 확인했다.
- 외부 API·웹 요청에 사용자 이메일을 넣은 건수: 0건 (Crossref·OpenAlex·Semantic Scholar·PubMed 호출은 일반 UA 문자열만 사용, mailto 파라미터 없음).
- 열리지 않은 것: Autodesk 제품 페이지(403), Elsevier 논문 페이지(JS 리다이렉트), Nature 본문(인증 리다이렉트), smartcity.go.kr 일부(404), Saltelli 원문(저장소 403), LH 보도자료 원문, delve 종료일 1차 공지.

---

## 1. 도구별 비교표

### 1.0 지형 군집 (읽는 법)
- 정책·계획 시나리오형(유형 × 원단위 × 지표): UrbanFootprint, ArcGIS Urban, UrbanSim(시장 시뮬레이션형)
- 사업성·배치 생성형: TestFit, Giraffe, Forma Site Design, Delve(종료), DBF, Modelur, Hypar(층·방 단위)
- 참여·대화형: MIT CityScope, KPF Scout
- 절차적 3D: CityEngine
- 디지털트윈: Cityzenith(중단 추정), Seoul S-Map

### 1.1 표 A — ① 기능 · ② 입력 레버 · ③ 출력 KPI · ④ 엔진 · ⑤ 지오메트리

| 도구 | ① 하는 일 | ② 입력 레버 | ③ 출력 KPI | ④ 엔진 방식 | ⑤ 지오메트리 |
|---|---|---|---|---|---|
| **UrbanFootprint** (Calthorpe → UrbanFootprint Inc. → LightBox 2025.06) | v1.0(2012): 기존 계획을 Place Type으로 번역 → 웹 시나리오 페인팅 → 분석 엔진 [확인·T2 기술요약]. 현행 사이트는 Analyst/Explorer/Direct Data(기후위험·인구취약성·건조환경 데이터 앱) [확인·T4] | Place Type 35+ · Building Type 50~90+(문서 내 표기 상이)를 격자에 칠함. 효율·연료·수요관리 정책 가정 | 토지소비, VMT·수단분담, GHG·대기오염, 건물 에너지·물, 가구비용, 공중보건 비용, 지방재정(인프라 자본·O&M·세수) | 규칙 + 원단위 곱(건물유형·기후대별 에너지 원단위) + 회귀(교통 MXD 8D식, 보건). 최적화 아님 | v1.0: 5.5에이커 격자 셀(필지 단위는 예고) |
| **UrbanSim** (Waddell; UDST 오픈소스 + UrbanSim Inc.) | 부동산 시장·입지선택 미시시뮬레이션(연 단위, 교통모형과 반복 결합) | 정책 레버(zoning·개발부담금·UGB 등), 거시전제, 예정된 대형 개발 | 가구(소득·연령·규모), 산업별 고용, 토지이용 면적, 주택유형, 가격·임대료, 접근성 | 이산선택 위치모형 + 전이·재배치 + 확률적 개발자 pro forma(이익 최대 사업 선택) | 필지·건물·가구·일자리 개체 |
| **MIT CityScope** | 격자 위에서 대안을 바꾸며 KPI를 즉시 확인하는 공유 인터페이스(웹 CityScopeJS·TUI) | 격자 셀에 토지이용·건물·오픈스페이스·교통 노선 입력, 밀도·사용성 속성 보강 | 교통 시뮬·ABM·소음·우수·접근성 모듈의 지표(정의는 배치별로 다름 [미확인]); 웰빙지수 5지표 제안(Orii 2020) | 시뮬레이션 + ML 대리모델(CNN이 교통 ABM을 대신 예측; Zhang 2018) | 격자 셀 |
| **Autodesk Forma** (구 Spacemaker) | Site Design(부지·매싱·환경분석), Building Design(2025 발표, LOD200/300), Carbon Insights(구 Autodesk Insight) | Site Automation 파라미터(그리드 간격·세트백·건물유형·층수·폭), 수동 편집 | 풍환경·소음(AI 빠른 분석) [확인·T4 블로그], 일조·채광 [스니펫·architosh 등], 총탄소(2026.04 기준 미국 한정) [확인·T4] | 파라메트릭 옵션 생성 + 빠른 분석. 2025.04 블로그는 순위·점수·최적화 서술 없이 '생성·평가·필터'만 기술 → 파레토 최적화기 아님 | 매스(압출 볼륨) + 지형; Building Design은 LOD200/300 BIM |
| **Esri ArcGIS Urban** | 계획(토지이용·조닝)·프로젝트 작성, 영향 분석, 참여 | 조닝 규칙(3D 엔벨로프), 계획 대안 시나리오, 프로젝트 스케치·외부 3D 업로드, 기성 space types·building types | 메트릭(현황·타 시나리오와 비교), 2026.07 일조 분석 추가, 시나리오 비교 보고서(피벗 표) | 규칙기반 조닝 엔벨로프 + 집계 지표. 생성·최적화 서술 없음 | 필지·3D 건물(space use 단위)·엔벨로프 |
| **Esri CityEngine** | 절차적 3D 도시 모델 | CGA 규칙 속성(층수·용도·스타일), 필지·가로 | 조닝 요건·자연자원 보전·가시권(viewshed) 분석과 개발 영향 평가(Esri 설명 [T4]), 대안 시나리오. 면적 등 리포트 기능의 세부는 [미확인] | 규칙기반 형상문법(CGA), Python 3 API(2026.0에서 정식) | 필지·가로 → 절차 생성 건물 |
| **Sidewalk Labs Delve** (종료) | 근린 단위 생성설계(건물·오픈스페이스·편의시설·가로·에너지 인프라) | 입력(전략)·제약(높이 등)·우선 성과·벤치마크안 | 일조·보행성·조망·공사비·에너지·물·폐기물 추정·유닛 수·임대료 | ML 기반 생성·평가 후 우선순위에 따른 순위화. 파레토 전선 제시 아님 [확인·T4 engineering.com 2020] | 건물·오픈스페이스·가로·인프라 요소 |
| **TestFit** | 부동산 타당성·부지 계획 생성(다세대·주차·산업·데이터센터 등) | 필지·경계, 유닛 믹스, 주차비율, 도로·회전반경, 지형, 세트백·조닝 | 유닛 수·yield, NRSF, 주차, 절성토, 비용·pro forma(애드온) | 생성설계(알고리즘 비공개) | 필지 위 파라메트릭 건물 프리셋·주차 스톨 |
| **Modelur** | SketchUp/Rhino용 파라메트릭 도시설계 매싱 + 지표 실시간 계산 | FAR·부지 피복·녹지·최고높이 규정, 층수·GFA, 사용자 정의 용도 | 도시 지표 실시간, 규정 위반 경고, Excel LiveSync | 규칙·직접조작(최적화 서술 없음) | 층수 파라미터 매스 |
| **KPF Urban Interface** | KPF 내부 도시 데이터 분석 + 공개 웹도구(Scout·CityBot) | Scout: 격자 유형·녹지·공원 유인체 유형 등 조절 | CityBot: 쾌적·에너지·채광; Urbane(논문): 신축이 주변 조망에 주는 영향 + 안전·교통·학교 등 데이터 층 | 데이터 탐색 + 입출력 임계값 필터(Filter 모드). 최적화 [미확인] | 격자·3D(Urbane은 다해상도 3D) |
| **Hypar** | 클라우드 설계 자동화; 현행 제품은 층·방 단위 공간계획 | 프로그램·부지에 맞춘 방·동선 배치 | 프로그램 대비 면적 등 실시간 지표(구체 KPI [미확인]) | 함수(Functions) 조합. 최적화 여부 [미확인] | 방·벽·문·창(BREP/CSG 커널 Elements, C#) |
| **Digital Blue Foam (DBF)** | 기관·정부 대상 AI 도시개발 시나리오 생성·검증(별도 제품 Hikari: 일본 유닛수익 분석) | 부지 경계·GIS·인구통계·계획정책 제약 | 벤더 주장: 계획·거주성·지속가능성·인프라 KPI, 45+ KPI, 50+ 시나리오, ROI·열섬·교통·배출·홍수 | AI 생성 + 순위화(방식 비공개); 확률적 단계화는 벤더 주장 [미확인] | 토지이용 구성·밀도 구배(세부 비공개); BIM-ready 출력 |
| **Giraffe.build** | 웹 GIS + 작도 + 재무를 묶은 부동산 계획·타당성 | 지도 위에서 매스·도로·주차·유닛 평면·구조 그리드를 직접 작도 | 그림자, 임차율, 바닥판 효율, 맥락, 재무 지표 | 사용자 작도 중심 + 생성설계 도구. 최적화 [미확인] | 지도 위 피처(매스·도로·주차·유닛) |
| **Cityzenith SmartWorldOS** | 건물·도시 디지털트윈(AEC·CRE) | — [미확인] | — [미확인] | — | 3D 트윈 |

### 1.2 표 B — ⑥ 필요 데이터 · ⑦ 스케일 · ⑧ 비용·개방성 · ⑨ 사례·정량 효과

| 도구 | ⑥ 필요 데이터 | ⑦ 스케일 | ⑧ 비용·개방성 (Rhino/GH) | ⑨ 공개 사례와 정량 효과 |
|---|---|---|---|---|
| **UrbanFootprint** | 센서스, 필지·토지이용, 토지피복, 에너지 조사(CEC) 등 미국 전제 | 도시~광역·주 | v1.0 기술요약은 전부 오픈소스 스택(Django·PostGIS 등)이라 명시; 현행은 상용 SaaS(가격 비공개), LightBox 통합 예정. Rhino/GH [미확인] | 개발 재원: CA 고속철도청·Strategic Growth Council. 기저연도 VMT를 5개 지역 모형과 대조: 새크라멘토 +7.2%, 베이에어리어 +0.07%, 남가주 약 0%, 샌디에이고 +2.3%, 샌와킨밸리 −2.9% [확인·계산]. 비교 기준이 다른 모형이며 불확실성 구간은 없음. 의사결정 개선 효과는 정량 효과 미공개 |
| **UrbanSim** | 매우 큼: Bay Area 기저 DB(2010)가 가구 약 260만·일자리 340만·건물 190만·필지 200만 [확인·T2 MTC 2017] | 광역·도시 | 파이썬 라이브러리 BSD-3, README 상태 표기 'Active' [확인]; 클라우드 도구는 UrbanSim Inc.(가격 비공개). Rhino/GH 해당 없음 | MTC/ABAG Plan Bay Area(2040 EIR 5개 대안; 2050+는 2026.03 채택) [확인·T2]. 벤더 주장: 8,180만 명이 UrbanSim 기반 광역계획 지역에 거주 [T4]. 문서는 개별 필지 단위 장기 예측은 맞을 가능성이 낮다고 스스로 명시 [확인·T4]. 의사결정 개선 정량 효과 미공개 |
| **MIT CityScope** | 지구별 교통·인구·건물 데이터, cityIO 클라우드 | 지구~도시 | 오픈소스(저장소별 라이선스 [미확인]; 프로젝트 페이지 콘텐츠는 CC BY-NC 4.0 표기). Rhino/GH [미확인] | 배치: Volpe(Cambridge), Andorra, Boston BRT, Shanghai, Kharkiv, Champs-Élysées [확인·T4 MIT 페이지]; Hamburg은 HCU CityScienceLab이 운영 [확인·T4 HCU 페이지]. 20개 이상 도시 네트워크는 [스니펫]. 정량 효과 미공개 |
| **Forma** | 컨텍스트 데이터 마켓플레이스; 총탄소·Building Layout Explorer는 미국 데이터 한정 [확인·T4] | 부지~지구(유닛 레이아웃까지) | Site Design은 AEC Collection 포함(기존 구독자) [스니펫]; 단독가는 공식 페이지 403으로 [미확인](2023 보도의 $1,445/년은 현재가 아님 가능). ShapeDiver 확장으로 GH 정의를 Forma 안에서 실행 [확인·T4]; Rhino 플러그인 [스니펫] | Stantec 밴쿠버 TOD(타워 20+): 723,000 → 681,000 tCO₂(−42,000, 약 −5.8%), 구조 변경은 저층 타워 3동의 하이브리드 콘크리트→목구조(재료 선택 효과이지 형태 최적화가 아님), 반복 약 1.5시간·분석 5~10초 [확인·T4 벤더 블로그]. 원단위 394 vs 409 kg/㎡(−3.7%)와 총량 −5.8%가 서로 맞는지는 원문에서 확인 불가 [계산·미확인]. Spacemaker 인수 약 2.4억 달러(2020.11) [스니펫] |
| **ArcGIS Urban** | 3D 건물·조닝·필지·인구; Urban model 구성 필요 | 도시·구 | ArcGIS Online/Enterprise의 Urban 라이선스(가격 비공개), Urban API 있음 [확인·T4]. 2026.07 릴리스에서 구 메트릭·Living Atlas 지표 폐기 예고 [확인]. Rhino/GH [미확인] | Esri 소개 사례: Vienna, Kauai, Washington DC, Nottingham, Maryland 카운티, Atlanta [T4]. 정량 효과 미공개 |
| **CityEngine** | shapefile·geodatabase·CAD·BIM, 지형 | 블록~도시 | ArcGIS Pro 구독 전용: Professional $2,200/년, Professional Plus $4,200/년 [확인·T4 CG Channel 2026.07]; Houdini·Unreal 연동. Rhino/GH [미확인] | 사용처: Foster + Partners, 취리히 계획부서(Esri 소개) [T4]. 정량 효과 미공개 |
| **Delve** | 부지·개발 프로그램 | 근린(수 ha) | 2026-05-04 중단(Wikipedia 기재 [스니펫급·T4]; delve.sidewalklabs.com이 sunset 파라미터로 Google Earth 기능 페이지에 리다이렉트 [확인]), 일부 기능은 Google Earth로 이관 | Wembley Park(Quintain, 12에이커): 8주 동안 40,000개 변형 → 우수안 24개 [스니펫·벤더 측]. 개발사 증언: 임대료 9.8% 프리미엄, 주택 200호 추가·유닛 13% 확대 [T4 engineering.com, 독립 검증 아님] |
| **TestFit** | 부지 경계·조닝(Site Intelligence 애드온) | 필지~단지 | 2026.05 가격: Parking Solver $195/월, Site Solver $15,000/년~, Portfolio $20,000/년~; 애드온 Site Intelligence $150/월·Pro Forma $170/월·MCP $100/월 [확인·T4]. Revit·SketchUp·AutoCAD·Excel·API 연동. GH 플러그인 [미확인] | 벤더 주장: 3~4주 → 수 시간, 15분 vs 1일, 활성 사용자 6,200+ [T4]. 독립 검증 [미확인] |
| **Modelur** | 사용자 입력(OSM·GIS 가져오기 가능) | 필지~지구 | €0(비상업·파일 1개) / €149(월) / €98(분기) / €74(연) 좌석당 월, 부가세 별도; SketchUp 완전 지원·Rhino 부분 지원(Windows) [확인·T4] | 고객 목록: AECOM, Oslo Kommune, City of Ljubljana 등 [T4]. 정량 효과 미공개 |
| **KPF Urban Interface** | 공공 도시 데이터(Urbane은 NYU 협업) | 건물~도시 | KPF 내부 도구; Scout는 scout.build에서 공개(상업 조건 미기재) [확인·T4] | Hawai'i Housing Lab 적용; 2020 Fast Company Innovation by Design(데이터 디자인) 수상 [T4]. 정량 효과 미공개 |
| **Hypar** | 사용자 프로그램·부지 | 층~건물(도시 마스터플랜 스케일 아님) | Elements 라이브러리 MIT 오픈소스(GitHub) [확인·T4]; 플랫폼 가격 미공개; PDF·Excel·Revit·Rhino 내보내기 [확인·T4 docs] | 벤더 주장: 상업 테스트핏 시간 90% 절감 [스니펫]. 독립 검증 [미확인] |
| **DBF** | 벤더: 100+ 데이터셋 | 건물~에미리트 단위(벤더: 4,000㎢) | 맞춤 견적(1,000명 이상 조직 대상); Revit·Rhino·Archicad·SketchUp 호환 출력 [확인·T4 2차 dossier] | 고객 로고(MODON, Emaar, Dubai Municipality, EGIS, Jacobs, McKinsey, Takenaka)만 공개; 벤더 주장 '2주→수 분'·'규정검토 90~99% 정확도' [T4]. 정량 효과는 벤더 주장뿐 |
| **Giraffe** | GIS·조닝 DB·태양·비용 레이어 + 사용자 업로드 | 필지~도시 포트폴리오 | 무료 셀프서브 + 구성형 데이터팩 + 엔터프라이즈(SDK) [확인·T4]; 제3자 목록상 Core $1,000/사용자·년, Portfolio $3,000(API 포함) [스니펫·T4, 공식 미확인] | 벤더 인용: Trammell Crow 주→시간, NSW 정부 주·월→일, Mortenson Revit 대비 10배·1% 이내 [T4]. 독립 검증 [미확인] |
| **Cityzenith** | — | — | 2023.06 Twinmaster 인수(CB Insights) [확인·T4]; 투자자 추적 사이트는 '폐업'·IP가 TwinMaster/Twinup으로 이전이라 기재(출처가 LinkedIn·Reddit 글, 미검증) [스니펫]; www.cityzenith.com 도메인이 2026-10-06 조회 시 해석되지 않음 [확인] → 서비스 중단 추정 [추정] | 라스베이거스 다운타운 트윈 등 보도 [스니펫]. 정량 효과 미공개 |

### 1.3 한국 쪽 (실제 확인되는 것만)

| 항목 | 내용 | 확인수준·등급 |
|---|---|---|
| **서울시 디지털트윈 S-Map** | 서울 605.23㎢ 3D 복제, 건물·시설 약 60만 개, 일조·바람길 등 시뮬레이션, 도시계획·교통영향평가 등 7개 위원회 심의에 활용, 오픈 API 제공(2021.04.01 서울시 보도자료). 생성·최적화가 아니라 심의 검증용. 정량 효과는 보도자료에 없음 → 정량 효과 미공개. 2025.12 헤럴드경제는 '사후대응→사전예측' 전환과 100m 격자 분석을 서술하나 수치 없음 | [확인·T2] / 기사 [확인·T4] |
| **국토부·LX 노후계획도시정비 디지털플랫폼**(2024.11) | 디지털트윈 시뮬레이션으로 단지계획·조망·일조 분석을 지자체 기본계획 수립에 제공, 2025년 둔산·송촌 적용 예정. 정량 효과 미공개 | [스니펫·T2 포털 요약; 원문 404] |
| **LH AI 토공설계 자동화 SW**(2026.06) | 강화학습으로 단지 계획고·토공 운반 설계를 최적화·자동화, 평균 약 7% 토공 운반량 절감 '예상'(실측 아님), LH 발주 BIM 설계사에 무상 배포 예정. 마스터플랜 배치가 아니라 부지 조성 설계용 | [확인·T4 헤럴드경제 2026-06-24; LH 원문 [미확인]] |
| **세종 5-1·부산 EDC 스마트시티** | 2018 국토부 기본구상: 세종 5-1 274만㎡·부산 EDC 219만㎡, 데이터 흐름 기반 통합 운영체계, E8IGHT 디지털트윈 실증. 계획 단계에서 파라메트릭·최적화 도구를 쓴 근거는 확인하지 못함 | [스니펫·T2/T4]; 도구 사용 [미확인] |
| **LH·국토연구원 PSS/도시계획 시뮬레이션** | 운영 중인 PSS는 확인하지 못함 [미확인]. 학술 수준: 김한준·최홍준(2013, 한국산학기술학회논문지 14(5):2465–2473)이 PSS를 리뷰하고 저탄소도시계획 지원 포털 프로토타입을 제안 | [확인-초록·T3] |

### 1.4 참고: 인접 오픈·Rhino 계열
- Umi(Reinhart 외 2013, IBPSA): Rhino 기반, EnergyPlus·Radiance/Daysim + Grasshopper·Python 스크립트로 근린의 운영 에너지·채광·보행성 평가 [확인-초록·T3].
- City Energy Analyst(Fonseca 외 2016, Energy and Buildings 113:202–226): 근린·지구 건물 에너지 시스템 분석·최적화 프레임워크 [서지 확인·초록 미열람].
- Urban Model Platform(Herzog·Degkwitz·Verma 2025, arXiv:2506.10964): 함부르크 시와 함께 만든 도시 디지털트윈용 개방형 모델 연동 백본 [확인-초록·T3 프리프린트].
- Tygron·Ratio.City: 검색에서만 확인 [스니펫], 이번 비교에서는 제외.

---

## 2. 공통 해부도

### 2.1 구성요소 × 확인된 도구

| 구성요소 | 확인된 곳 | 비고 |
|---|---|---|
| 공간·건물 유형 라이브러리 | UrbanFootprint(Place/Building Type; 건물 유형은 300여 개 실제 건물 조사 기반 [확인]), ArcGIS Urban(space types·building types), CityScope(격자 셀 유형), Modelur(사용자 정의 용도), TestFit(건물 프리셋·유닛 유형) | 모두 '유형 → 원단위·형태 파라미터 묶음'이라는 같은 패턴 |
| 원단위(벤치마크) 표 | UrbanFootprint(건물유형·기후대별 에너지·물 원단위, 정책 기반 효율계수로 시계열 보정) [확인], UrbanSim(개발 비용·임대료 계수), Forma(탄소 계산; 데이터 출처 비공개) | 공개 문서에서 범위·불확실성이 함께 제시된 곳은 못 찾음 |
| 시나리오 관리 | UrbanFootprint(Base+Future, 페인팅), ArcGIS Urban(plans·projects·scenarios), UrbanSim(baseline vs 대안), Scout(Collection), DBF·Giraffe | |
| KPI 스코어카드 | ArcGIS Urban(메트릭 대시보드; 2026.07 개발상태·space use 필터), CityScope, DBF(벤더 45+), UrbanFootprint 분석 엔진 | |
| 옵션 비교 | ArcGIS Urban(비교 보고서·피벗), Scout(Compare 모드), Forma(생성안 필터), Delve·DBF(순위화) | 가중 없는 파레토 제시는 확인되지 않음 |
| 단계(phasing)·현금흐름 | UrbanFootprint(재정 영향: 자본·O&M·세수), UrbanSim(연 단위 진행 + pro forma), TestFit(Pro Forma 애드온), Giraffe(재무 지표), DBF(ROI·투자수익 목표) | NPV/IRR/Break-even 인포그래픽 구조는 공개 자료에서 확인하지 못함 [미확인] |
| 제약 | UrbanSim(조닝 반영, 보호지·정부용지·교통회랑을 개발 불가로 조정 [확인·T2 MTC 2017]), ArcGIS Urban(조닝 엔벨로프), Modelur(위반 경고), Scout(입출력 임계값 필터) | 문서화된 방식은 대부분 경고·필터. 불가능 영역으로 잘라내는 hard constraint를 명시한 곳은 UrbanSim뿐 |
| 확장·API | Urban API, Forma(ShapeDiver 확장·API [스니펫]), Giraffe SDK, TestFit API·MCP, UrbanSim Python, Hypar Elements(MIT) | |

### 2.2 빠진 요소 (확인한 공개 자료 범위에서)
1. **불확실성 표기**: 구간·분포를 기본 출력으로 두는 상용 도구를 확인하지 못했다. UrbanSim 문서가 유일하게 개별 예측의 한계를 명시. UrbanFootprint v1.0의 검증은 기저연도 총량 대조(+7.2%~−2.9%)와 장소유형별 범위 비교이며, 예측 구간은 없다. DBF의 확률적 단계화는 벤더 주장 [미확인].
2. **규제 hard constraint**: 한국형 4겹(용도·고도보존·역사문화환경 허용기준·지구단위계획)과 시점장 표고면 같은 층을 내장한 도구는 없다. 미국·유럽 조닝 전제(Forma 총탄소·Building Layout Explorer는 미국 데이터 한정, UrbanFootprint는 미국 전제).
3. **결정 근거 추적**: 확인한 문서에서 '왜 이 가정·이 안인가'를 기록하는 기능 언급은 없다(버전·비교 기능만). [추정: 공개 자료에 언급이 없다는 뜻이며 기능 부재의 증명은 아님]
4. **한국 법정 지표·원단위**: 주차(주차장법·조례), 오수발생량, 일조, 공원·녹지, 학교용지, 용적률·건폐율·높이 등은 확인한 도구에 내장돼 있지 않다 [추정: 언급 없음 기반]. 의뢰인은 이미 `work/20260928_구경주역_주차대수_산정_v1.md`에서 가정 3개가 결과를 좌우하므로 1,400~2,000면 범위로 쓰라는 방식을 쓰고 있어 같은 원칙의 연장선.
5. **원단위 계보(pedigree)·출처등급 표시**: 도구에서 확인하지 못함.

### 2.3 의뢰인 KPI 8개와 확인된 선례 [추정: 대응은 보고자 판단]
| KPI | 선례 | 비고 |
|---|---|---|
| Car-Free | UrbanFootprint VMT·수단분담(MXD 8D식), CityScope 이동 모듈 | 한국 적용은 교통영향평가 원단위 확인 필요 [미확인] |
| Carbon Reduction | UrbanFootprint GHG, Forma 총탄소(미국 한정) | 국내 배출계수 별도 |
| Landfill Diversion | UrbanFootprint 분석 목록에는 폐기물 없음; 도시 대사 7개 흐름에는 포함(docs §13) | 직접 선례 약함 |
| IRR | UrbanSim 개발자 pro forma, TestFit Pro Forma, Giraffe 재무 | |
| Job Creation | UrbanSim 고용, ArcGIS Urban 메트릭 | |
| Community Provision | CityScope 웰빙지수(Orii 2020) | |
| Resiliency | UrbanFootprint 기후·재해 레이어 | |
| Ecological Footprint | CitySim·SUNtool 계보(자원 흐름 모델링; Robinson 외) | 학술 프로토타입 |

---

## 3. 학술 근거

표기: [확인-초록]=초록·서지DB에서 확인(본문 미열람). '한계' 열은 논문 서술이 아니라 본 보고자의 읽기인 경우 [추정] 표시.

### 3.1 PSS(계획지원시스템)의 실무 채택과 효과

| 저자·연도 | 저널/출판사 | 핵심 발견 | 한계 |
|---|---|---|---|
| Lee, D.B. (1973) | J. American Institute of Planners 39(3):163–178 | 대형 모형이 내세운 목표 중 달성된 것이 없고, 각 목표마다 더 나은 방법이나 더 가치 있는 질문이 있다고 평가. 장기계획 방법이 바뀌어야 영향력을 가진다 [확인-초록] | 1970년대 대형 모형 비판; 현재 도구에 직접 적용은 제한적 [추정] |
| Klosterman, R.E. (1999) | Environment and Planning B 26(3):393–408 | What if?: 시나리오·정책 지향 PSS. 토지 적합성 분석·수요 투영·배분, 쉬운 사용과 지도·보고서 출력 [확인-초록] | 초록은 도구 소개이며 의사결정 효과 검증은 없음 [확인-초록 기준] |
| Vonk, Geertman & Schot (2005) | Environment and Planning A 37(5):909–924 | PSS 전문가 약 100명 온라인 설문: 저활용 원인은 인적·조직·제도·기술 요인의 복합, 특히 PSS에 대한 인지·경험 부족과 가치 인식 부족. 사례·편익 정보 확산을 권고 [확인-초록] | 전문가(공급 측 포함) 설문이라 편향 가능 [추정] |
| Vonk & Geertman (2008) | Applied Spatial Analysis and Policy 1(3):153–173 | 공급과 수요의 불일치가 악순환을 만든다는 진단과 개발자·계획가·연구자용 교훈 [확인-초록] | 정성적 교훈 정리 [추정] |
| Te Brömmelstroet (2010) | J. Transport and Land Use 3(1) | 네덜란드 토지이용·교통 실무자 웹 설문(2007): 도구가 실무에 박히는 방식이 중요하며 기술 개선만으로는 불충분 [확인-초록(일부 잘림)] | 네덜란드·LUT 한정 [추정] |
| Te Brömmelstroet, Pelzer & Geertman (2014) | Environment and Planning B 41(3):381–387 | Lee(1973)의 '일곱 가지 죄'를 40년 뒤 시점에서 재평가하는 논평 [서지 확인; 초록은 서두만 확인, 결론 [미확인]] | — |
| Pelzer, Geertman, van der Heijden & Rouwette (2014) | Computers, Environment and Urban Systems 48:16–27 | MapTable 사례: 인터뷰 15건 + 그룹의사결정룸 워크숍. 실무자는 협업·소통 개선을 가장 큰 가치로, '더 나은 정보에 기반한 결과'는 상대적으로 낮게 평가 [확인-초록] | 단일 도구·소규모 [추정] |
| Arciniegas, Janssen & Rietveld (2013) | Environmental Modelling & Software 39:159–175 | 이탄 초지 토지이용 배분 통제 실험(참가자 30명), 세 가지 표현(인쇄 지도 색상 / 단일 디지털 지도 정성 / 단일 디지털 지도 정량) 비교. 정량 도구가 정보는 가장 많았으나 가장 유용하다고 평가받지 못했고 결과도 최선이 아니었음 [스니펫: 검색 요약 + Semantic Scholar 요약이 일치; 원문 미열람] | 단일 사례·소규모 [추정] |
| Goodspeed (2016) | Environment and Planning B 43(3):444–463 | 오스틴 현장연구: 학습·대화 품질이 높게 보고되고, 두 성과는 PSS가 참여자의 인식을 바꾸는 능력과 관련. PSS 제작 참여는 덜 중요 [확인-초록] | 자기보고 성과이며 설계 결과 개선과의 연결은 없음 [추정] |
| Geertman & Stillwell (2020) | Environment and Planning B 47(8):1326–1342 | 2003·2009 리뷰 이후 갱신: 전문가 종합으로 PSS가 'planning support science'로 성숙 중이라는 전망 [확인-초록] | 저자 전망·전문가 의견 종합 [추정] |
| Jiang, Geertman & Witte (2020) | Environment and Planning B 47(8):1343–1360 | PSS 구현 격차에서 얻은 교훈: 사용자의 기대·능력과 과업 특성·맥락에 맞춘 기술이어야 한다 [확인-초록] | 개념적 논의 [추정] |

### 3.2 지표·KPI 대시보드의 부작용, Goodhart·Campbell, 가짜 정밀도

| 저자·연도 | 저널/출판사 | 핵심 발견 | 한계 |
|---|---|---|---|
| Kitchin, Lauriault & McArdle (2015) | Regional Studies, Regional Science 2(1):6–28 | 도시 지표·벤치마킹·대시보드가 '시각화된 사실로서의 도시'라는 좁은 실재론적 인식론을 강화하고, 순진한 도구적 합리성에 기대며, 이해관계자의 조작에 열려 있고, 방법론·기술 문제가 종종 인정되지 않는다. 데이터 어셈블리지로 재개념화할 것을 주장 [확인-초록] | 개념·질적 논증이며 설계 의사결정 효과의 정량 실증은 아님 [추정] |
| Batty (2015) | Regional Studies, Regional Science 2(1):29–32 | 도시 대시보드에 대한 관점 논평 [서지 확인; 초록 앞부분만] | 결론 [미확인] |
| Bevan & Hood (2006) | Public Administration 84(3):517–538 | 영국 보건 부문 목표 체계: 보고된 성과에 측정 문제와 게이밍이 동반됨을 증거로 검토, 감사 장치 보완책 논의 [확인-초록] | 의료 부문; 도시계획 직접 증거 아님 |
| Strathern (1997) | European Review 5(3):305–321 | 평가·감사 장치가 자체 생명을 얻어 감사 대상의 삶을 위협. 측정치가 목표가 되면 좋은 측정이 아니게 된다는 정식화의 출처로 널리 인용 [확인-초록] | 고등교육 사례 |
| Campbell (1979) | Evaluation and Program Planning 2(1):67–90 | 정량 사회지표가 의사결정에 많이 쓰일수록 부패 압력과 왜곡이 커진다는 'Campbell's law'의 출처 [서지 확인; 문구는 Wikipedia 인용으로 확인(T4), 본문 미열람] | — |
| Manheim & Garrabrant (2018) | arXiv:1803.04585 | 지표에 대한 과최적화가 실패하는 서로 다른 메커니즘을 최소 4가지로 정리 [확인-초록; 4가지 명칭은 원문 확인 필요] | 프리프린트; 도시 맥락 아님 |
| Smith & Winkler (2006) | Management Science 52(3):311–322 | 가치 추정치가 비편향이어도 추정치 기준으로 최상위를 고르면 선택된 대안의 실제 가치는 추정보다 낮을 것으로 기대('optimizer's curse'). 베이즈 보정 제안 [확인-초록] | 의사결정분석 일반론; NSGA 파레토 선택에의 적용은 [추정] |
| Newsham, Mancini & Birt (2009) | Energy and Buildings 41(8):897–905 | LEED 인증 건물 100개: 평균 18~39% 적은 에너지를 쓰지만 28~35%는 비교 건물보다 더 썼고, 실측 성능은 인증 등급·에너지 크레딧과 상관이 낮다 [확인-초록·NRC 저장소] | 상업·공공 건물; 비교군 선택의 영향 [추정] |
| Janiszewski & Uy (2008) | Psychological Science 19(2):121–127 | 5개 실험: 정밀한 숫자 앵커가 반올림된 앵커보다 조정 폭이 작다 → 소수점이 긴 숫자는 판단을 더 강하게 붙잡는다 [확인-초록] | 실험실 수치 판단; 도시설계 검증 아님 |
| Parasuraman & Manzey (2010) | Human Factors 52(3):381–410 | 의사결정 보조가 불완전할 때 자동화 편향이 누락·작위 오류를 낳고, 전문가에서도 나타나며 훈련·지시로 막기 어렵다 [확인-초록] | 항공·산업 자동화 맥락; 외삽은 [추정] |
| Rydin (2007) | Environment and Planning D 25(4):610–624 | 지역 지속가능성 지표를 통치기술로 해석: 지표 사용은 주체·객체 구성보다 중앙–지방 관계를 더 드러낸다 [확인-초록] | 단일 사례 |
| Innes & Booher (2000) | Planning Theory & Practice 1(2):173–186 | 지표가 유용하려면 사용자 참여로 개발되어야 하며, 시스템 성과·정책/프로그램·신속 피드백의 세 유형을 제안 [확인-초록] | 개념 제안 |

### 3.3 불확실성과 원단위 곱셈 모델

| 저자·연도 | 저널/출판사 | 핵심 발견 | 한계 |
|---|---|---|---|
| IPCC (2006), Vol.1 Ch.3 Uncertainties | IPCC National GHG Inventories Guidelines (T2) | 식 3.1: 독립인 양들의 곱은 각 상대 불확실성의 제곱합의 제곱근(95% 구간 반폭/평균, %). 변동계수 약 0.3 이하에서 근사가 맞고 나눗셈에는 쓸 수 없다. 범주별 불확실성이 수 %에서 자릿수 단위까지 다양하고 상관될 수 있어 가정이 깨지면 Monte Carlo(Approach 2) [확인·원문 PDF] | 온실가스 인벤토리 맥락 |
| van der Sluijs et al. (2005) | Risk Analysis 25(2):481–492 | NUSAP(수치·단위·분산·평가·계보)이 단순·복잡 모형 모두에 적용 가능; 파라미터 민감도(정량)와 계보(정성)를 합친 진단 도표; 문제 설정·가치 가정까지 확장하면 성찰·집단 학습을 촉진 [확인-초록] | 환경평가 4개 사례 |
| Walker et al. (2003) | Integrated Assessment 4(1):5–17 | 불확실성을 위치·수준·성질 세 차원으로 분류하고 불확실성 매트릭스를 제안 [확인-초록] | 개념틀 |
| Ciroth, Muller, Weidema & Lesage (2016) | Int. J. Life Cycle Assessment 21(9):1338–1348 | ecoinvent pedigree matrix의 불확실성 계수에 경험적 근거를 제공 [스니펫: Semantic Scholar 요약; 초록 미열람] | LCA 맥락 |
| Heijungs & Lenzen (2014) | Int. J. Life Cycle Assessment 19(7):1445–1461 | 해석적 오차 전파와 표본(몬테카를로) 방식을 비교하고 둘 다 쓸 것을 권고 [스니펫: Semantic Scholar 요약] | LCA 맥락 |
| Flyvbjerg, Holm & Buhl (2005) | J. American Planning Association 71(2):131–146 | 14개국 210개 교통 프로젝트(590억 달러): 철도 10건 중 9건에서 승객 과대예측(평균 +106%), 도로의 절반은 ±20% 초과 오차, 30년간 정확도 개선 없음. 해법은 투명성·책임·새 예측방법 [확인-초록] | 교통수요; 다른 KPI로의 일반화는 [추정] |
| Reinhart & Cerezo Davila (2016) | Building and Environment 97:196–202 | 도시 건물에너지모델(UBEM) 리뷰: 입력 구성·열모델 생성·결과 검증 논의 [확인-초록] | 리뷰 |
| Cerezo et al. (2017) | Energy and Buildings 154:321–334 | 쿠웨이트시티 주거 사례에서 건물 원형(archetype) 특성화 방법 4가지 비교 [서지 확인; 결과 수치 [미확인]] | — |
| Saltelli et al. (2020) | Nature 582:482–484 | 모형이 사회에 봉사하도록 하는 다섯 가지 제안(성명) [서지 확인; 본문 미열람 — 항목 인용 전 원문 확인] | — |

### 3.4 다목적 최적화·생성적 도시설계

| 저자·연도 | 저널/출판사 | 핵심 발견 | 한계 |
|---|---|---|---|
| Deb & Jain (2014) | IEEE Trans. Evolutionary Computation 18(4):577–601 | NSGA-III: 기준점 기반 비지배 정렬로 3~15개 목적 테스트 문제에서 만족스러운 결과. 이 논문은 박스 제약만 다루고 제약 처리는 후속편 [확인-초록] | 도시 문제 아님; 의뢰인의 마스크 방식은 제약 처리 문제를 우회 [추정] |
| Cao, Batty, Huang, Liu, Yu & Chen (2011) | Int. J. Geographical Information Science 25(12):1949–1969 | NSGA-II-MOLU: 통저우 신도시에서 전환비용 최소·접근성 최대·용도 적합성 최대 3목적으로 수만 해를 탐색해 파레토 전선 산출, 토지이용계획 지원 시스템의 핵심으로 제안 [확인-초록] | 토지이용 배분 스케일; 3목적 |
| Makki, Showkatbakhsh, Tabony & Weinstock (2019; 온라인 2018) | Int. J. Architectural Computing 17(1):5–35 | 단일 최적해가 없고 탐색 공간이 큰 도시 형태 문제에 확률적 메타휴리스틱(Wallacei)을 적용하는 근거와 실험 [확인-초록] | 방법 제시·실험 중심; 실제 계획 채택 [미확인] |
| Koenig, Miao, Aichinger, Knecht & Konieva (2020) | Environment and Planning B 47(6):997–1013 | 가로망·필지·건물을 포괄하는 도시 조직 데이터 표현(Grasshopper)을 진화 최적화와 결합. 설계자에게 옵션 공간을 채워주는 반자동 과정 [확인-초록] | 의사결정 효과 검증 없음 [추정] |
| Nagy, Villaggi & Benjamin (2018) | SimAUD 2018 (SCS) | 네덜란드 알크마르 실제 주거 단지에 생성설계 적용: 개발자 수익성과 옥상 PV 발전 잠재 두 목적. 후속 연구 필요라고 서술 [확인-초록] | 2목적 |
| Li, Zhang, Niu & Zhang (2025) | Sustainability 17(21):9724 | 우한 블록 형태 NSGA-II(Wallacei + Honeybee/EnergyPlus), 목적 3개(평균 일조시간·EUI·UTCI). 일조시간은 4.30~7.93h로 크게 변하나(약 +84%) EUI는 91.69~93.36 kWh/㎡(약 +1.8%)로 거의 안 변함 [확인-초록; 변동률은 계산] | 목적함수 변별력 차이는 본 보고자의 해석 [추정]. 블록 스케일 NSGA-II가 환경성능 목적에 몰려 있다는 기존 정리와 일치 |
| Parish & Müller (2001) | SIGGRAPH 2001, pp.301–308 | 절차적 도시 모델링(CityEngine의 계보) [서지 확인; 초록 미열람] | — |
| Vanegas et al. (2012) | ACM Trans. Graphics 31(6):1–11 | 목표 지표를 지정하면 시스템이 절차적 도시 모델의 파라미터를 역으로 찾는 '역설계' [확인-초록] | 그래픽스 맥락 |
| Zhang, Grignard, Lyons, Aubuchon & Larson (2018) | AAMAS 2018 확장초록, pp.2171–2173 | CityMatrix: 얕은 CNN이 교통 ABM을 원 ABM보다 훨씬 빠르게 예측하며 의사결정에 충분한 정확도라고 주장 [확인-초록; 정확도 수치 [미확인]] | 확장초록 |

### 3.5 플랫폼 계보 문헌
- Waddell (2002), JAPA 68(3):297–314, UrbanSim — 토지이용·교통·환경 계획용 모델 시스템, 유진–스프링필드 적용 [확인-초록]. Waddell 외(2003), Networks and Spatial Economics 3(1):43–67 [서지 확인].
- Robinson 외(2007), Solar Energy 81(9):1196–1211, SUNtool — 도시 지속가능성 시뮬레이션·최적화 패러다임 [서지 확인; 초록 미열람]. Robinson(2016) 노팅엄 'Sustaining Urban Habitats'(2015–2020, 보조금 175만 파운드) 발표자료는 자원 흐름 통합 모델링 프레임워크를 계획 단계로 제시(상용 제품 아님) [확인·발표자료].
- Alonso 외(2018), ICCS pp.253–261, CityScope Volpe [서지 확인]. Orii·Alonso·Larson(2020), Sustainability 12(22):9458, 웰빙지수 5지표 [확인-초록].
- Ferreira 외(2015), IEEE VAST pp.97–104, Urbane — KPF 소속 저자 포함, 신축이 주변에 미치는 영향(예: 조망)을 3D 다층 데이터로 평가 [확인-초록].
- Geertman & Stillwell 단행본 2003(Planning Support Systems in Practice)·2009(Planning Support Systems: Best Practice and New Methods), Springer [서지 확인].

### 3.6 쟁점별 정리 — 확인된 것과 못 찾은 것
**(a) PSS·KPI 대시보드가 의사결정에 미치는 효과·부작용**
- 확인: 보고된 가치는 학습·대화·협업 쪽에 몰려 있고(Pelzer 2014; Goodspeed 2016), '더 나은 정보에 기반한 결과'는 상대적으로 낮게 평가(Pelzer 2014). 정량 도구의 정보량이 많다고 결과가 좋아지지 않은 실험(Arciniegas 2013 [스니펫]).
- 부작용의 근거: 지표·대시보드의 인식론적 편향과 조작 가능성(Kitchin 2015, 개념적), 목표화에 따른 게이밍(Bevan & Hood 2006), 인증 점수와 실측 성능의 불일치(Newsham 2009), 추정치 상위 선택의 사후 실망(Smith & Winkler 2006), 정밀한 숫자가 판단을 붙잡는 효과(Janiszewski & Uy 2008), 자동화 편향(Parasuraman & Manzey 2010).
- 못 찾은 것: '도시설계 의사결정에서 대시보드·KPI가 설계를 왜곡했다'를 직접 측정한 실증 연구 [미확인]. 위 근거는 타 분야 실증 + 도시 지표의 개념적 비판의 조합이다.
**(b) 원단위(벤치마크) 곱셈 모델의 불확실성 정량화**
- 확인: 방법론 근거(IPCC 식 3.1과 Monte Carlo 대안, NUSAP·pedigree, 해석 vs 표본 오차 전파).
- 계산 예(식은 IPCC 확인, 입력값은 가정): 각 원단위 ±20% 4개 곱 ≈ ±40%, ±30% 4개 ≈ ±60%, ±30% 6개 ≈ ±73.5%. ±30%는 식의 유효 조건(변동계수 약 0.3 이하) 경계라서 그 이상이면 Monte Carlo가 필요하다.
- 못 찾은 것: 도시 마스터플랜 원단위 곱셈 모델의 불확실성을 직접 정량화한 연구 [미확인]. 가장 가까운 것은 UBEM 원형 방법 비교(Cerezo 2017, 수치 미확인)와 UrbanFootprint의 총량 대조(+7.2%~−2.9%, 모형 대 모형).

---

## 4. 결론 (한 단락)

1인 설계자가 마감 안에 구현할 수 있는 최소 구성은 다음과 같다. (1) 공간유형 라이브러리 8~12종 — 형태 파라미터(용적률·층수·건폐율·획지 규모)와 용도별 거주·종사 인원, 주차, 에너지·물·폐기물·통행 원단위를 low/mode/high와 출처·T등급과 함께 CSV로 보관하고, (2) 의뢰인의 기존 획지·매스에 유형을 배정하되 규제는 점수가 아니라 buildable 마스크로 제외하며, (3) KPI 6~8개를 곱셈식으로 계산하고 원단위 범위를 Monte Carlo(수천 회)로 전파해 P10–P90과 대안 간 순위 역전 확률을 함께 보이고, (4) 대안 A–E를 같은 지표로 비교하되 링 게이지는 '목표선 대비 구간'으로만 그리고 가중합·단일 점수는 쓰지 않으며, (5) 단계별 현금흐름은 단순 NPV/IRR로, (6) 모든 숫자에서 원단위 행과 출처로 이어지는 추적 열을 둔다(작업 시간은 하루 안팎씩 4~5개 덩어리 [추정]). 이 구성은 UrbanFootprint v1.0(유형 × 원단위 × 격자 시나리오 + 소수의 회귀식)과 ArcGIS Urban(space/building types + metrics)이 실제로 쓰는 구조와 같고, 대형·복잡한 모형일수록 실무에서 저활용·불일치가 크다는 PSS 문헌(Lee 1973; Vonk 2005)과 정량 정보량이 곧 결과 품질이 아니라는 실험(Arciniegas 2013 [스니펫])에 맞는 규모다. 자체 구현해야 하는 이유는 다섯 가지다. 첫째, 한국 4겹 규제·시점장 표고면·한국 원단위·추적표를 내장한 상용 도구를 확인하지 못했고 일부 기능은 미국 데이터 한정이다. 둘째, 파레토 전선을 제시하는 상용 도구가 확인되지 않아 의뢰인 논증(경계 하나 고정 → 동일 목적함수로 측정 → 파레토)을 상용 도구가 대신할 수 없다. 셋째, 공급 지속성이 불안정하다(Delve 종료, Cityzenith 중단 추정, UrbanFootprint 재편, ArcGIS Urban 메트릭 개편). 넷째, 비용 구조가 1회성 마감과 맞지 않는다(TestFit Site Solver $15,000/년~, CityEngine $2,200~4,200/년). 다섯째, 지표·목표를 보여주는 것만으로도 왜곡(Goodhart·Campbell·가짜 정밀도)이 생기므로, 구간 표기·출처등급·계산식 공개를 직접 통제해야 심의에서 방어된다. 반대로 쓰는 편이 나은 부분은 일조·풍환경·소음 같은 물리 시뮬레이션이다. 이는 직접 구현할 이유가 약하므로 최종 5개 대안에 한해 Forma(이미 AEC Collection 구독이 있다면 추가비용 없음; 풍·소음은 AI 근사 분석)나 Ladybug·Honeybee, Umi 같은 Rhino 계열 개방 도구로 검증하는 보조 용도로 쓰는 것이 합리적이다.

---

## 5. 미확인 · 접근 실패 · 출처

**미확인/접근 실패**
- 'Intelligent Urban Development Modelling Platform / CityFinder' 공개 문서(웹 검색·Crossref·OpenAlex에서 식별 안 됨) [미확인]
- Autodesk Forma 제품 페이지(403): 가격·기능 일부는 제3자·벤더 블로그로만 확인
- Delve 종료일 1차 공지: 리다이렉트로 종료 사실만 확인, 2026-05-04는 Wikipedia 기재
- UrbanSim Inc. 가격, ArcGIS Urban 라이선스 가격, DBF 가격, Hypar 플랫폼 가격
- Rhino/GH 연동: Forma(ShapeDiver 확장 외), CityScope, ArcGIS Urban, CityEngine, TestFit, Giraffe, UrbanFootprint [미확인]
- 국토부·LX 노후계획도시 디지털플랫폼 원문(404), LH 보도자료 원문, 세종·부산 계획 단계 도구 사용 여부
- 논문 본문 미열람: 대부분 [확인-초록]; Saltelli 2020·Campbell 1979·Cerezo 2017 결과·Te Brömmelstroet 2014 결론·Batty 2015 결론 [미확인]
- Octopus 사용 사례 논문은 확인하지 못함(Wallacei 사례만 확인)

**주요 URL (실제 열람/조회)**
- UrbanFootprint v1.0 기술요약(SCAG 호스팅): https://sp.scag.ca.gov/sites/default/files/2024-05/urbanfootprint_technical_summary.pdf
- LightBox 보도: https://www.lightboxre.com/news/lightbox-acquires-urbanfootprint-expanding-market-leading-location-intelligence-with-climate-infrastructure-demographic-data/
- UrbanFootprint 현행: https://urbanfootprint.com/
- UrbanSim 문서: https://cloud.urbansim.com/docs/general/documentation/urbansim.html / https://github.com/UDST/urbansim / MTC 2017: https://files.mtc.ca.gov/library/pub/29736.pdf / ABAG: https://abag.ca.gov/our-work/land-use/forecasts-projections / https://www.urbansim.com/
- CityScope: https://www.media.mit.edu/projects/cityscope/ / https://cityscope.media.mit.edu/cityscopejs/Introduction / https://www.media.mit.edu/projects/cityscope/publications/
- Forma: https://blogs.autodesk.com/forma/2025/04/24/how-to-use-generative-design-ai-and-3d-modeling-for-improved-site-planning/ / https://blogs.autodesk.com/forma/2025/08/22/stantec-forma-case-study-how-to-reduce-embodied-carbon/ / https://blogs.autodesk.com/forma/2026/04/07/total-carbon-analysis-in-forma-building-design-a-step-by-step-guide/ / https://adsknews.autodesk.com/en/news/building-layout-explorer-in-autodesk-forma/ / https://architosh.com/2025/09/au25-autodesk-introduces-forma-building-design/ / https://shapediver.com/blog/shapediver-x-autodesk-forma-or-live-webinar
- ArcGIS Urban: https://www.esri.com/en-us/arcgis/products/arcgis-urban/overview / https://doc.esri.com/en/arcgis-urban/latest/get-started/get-started-what-is-urban.html / https://doc.esri.com/en/arcgis-urban/latest/get-started/get-started-release-notes.html
- CityEngine: https://www.cgchannel.com/2026/07/esri-releases-cityengine-2026/ / https://www.esri.com/en-us/arcgis/products/arcgis-cityengine/overview
- Delve: https://delve.sidewalklabs.com (302 리다이렉트) / https://en.wikipedia.org/wiki/Sidewalk_Labs / https://www.engineering.com/sidewalk-labs-brings-machine-learning-to-urban-planning/
- TestFit: https://www.testfit.io/pricing-may-2026-updates / https://www.testfit.io/
- Modelur: https://modelur.com/ / https://modelur.com/pricing/
- KPF: https://www.kpf.com/news/kpf-launches-kpf-urban-interface / https://www.kpf.com/news/kpfui-launches-new-tools-for-public-engagement-with-urban-design / https://www.kpf.com/story/from-complexity-to-clarity-scout
- Hypar: https://github.com/hypar-io/Elements / https://docs.hypar.io/
- DBF: https://digitalbluefoam.com/industries/city-development / https://www.digitalbluefoam.com/test-page / https://www.digitalbluefoam.com/pricing / https://www.bryanboyer.com/chaindrain/research/dossier/digital-blue-foam/
- Giraffe: https://www.giraffe.build/ / https://aecmag.com/concept-design/giraffe-for-urban-planning/
- Cityzenith: https://www.cbinsights.com/company/cityzenith / https://www.fundwisdom.com/investors/companies/cityzenith-holdings-twinup
- 서울 S-Map: https://mediahub.seoul.go.kr/archives/2001139 / https://www.heraldk.com/article/2025121118220954825
- LH 토공설계 AI: https://www.heraldk.com/article/2026062416142279903
- 국내 PSS 논문: https://koreascience.or.kr/article/JAKO201318552673279.pdf
- IPCC 2006 Vol.1 Ch.3: https://www.ipcc-nggip.iges.or.jp/public/2006gl/pdf/1_Volume1/V1_3_Ch3_Uncertainties.pdf
- Newsham 2009(NRC): https://nrc-publications.canada.ca/eng/view/object/?id=367e8a94-0f06-49e1-ab61-f76a968063df
- Pelzer 2014(UU): https://research-portal.uu.nl/en/publications/the-added-value-of-planning-support-systems-a-practitioners-persp/
- Manheim & Garrabrant: https://arxiv.org/abs/1803.04585 / Urban Model Platform: https://arxiv.org/abs/2506.10964
- 논문 서지·초록: api.crossref.org, api.openalex.org, api.semanticscholar.org, PubMed(eutils)
