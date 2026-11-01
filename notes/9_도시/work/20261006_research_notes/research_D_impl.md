# 과제 D 연구노트 — 슬라이더 → 지오메트리 → KPI → 대시보드 구현 레퍼런스와 대안 탐색 UI

작성 2026-10-06 (조기 종결: 코디네이터 지시로 신규 검색 중단). 프로젝트 폴더 파일은 읽기만 했고 수정하지 않았다. 실험물(PoC)은 전부 스크래치패드에 있다.

표기: [확인] 이번 세션에서 1차 출처(공식 페이지·문서·저장소·논문 초록/원문·로컬 실측)를 직접 열어 확인 / [스니펫] 검색 결과 요약만 봄 / [추정] 내 판단 / [미확인].
출처 등급: 제품 공식 문서·GitHub README는 T2(공식 문서), 논문은 T3, 벤더 마케팅·블로그·포럼은 T4.

---

## 0. 요약 (8줄)

1. 권고: 마감 기준 최단 경로는 안A(Python 사전계산 → JSON → 단일 HTML, three.js + ECharts). 안B(FastAPI 실시간)는 "임의 지오메트리를 즉석 생성"이 심사 요건일 때만 추가한다. 두 안 모두 오픈소스 조합이라 추가 비용 0 USD [확인: 라이선스].
2. 실측 PoC(이 PC i9-13900K, headless Chrome 154): three.js + ECharts + 실제 계획 데이터(건물 57·획지 19) 단일 HTML = 1.29 MB(gzip 382 KB), file://로 열림. 슬라이더 1회 갱신 3.4 ms(KPI 닫힌식 0.05 ms + 차트 9개 3.2 ms), 저해상 일조 레이캐스트 2.2만 선 포함 17 ms. LightGBM→JSON→JS 추론 3.2 µs/회, FastAPI 로컬 왕복 2.4 ms.
3. 서비스 상태 변동 [확인]: ShapeDiver 공식 요금표에 Free 카드가 없고 14일 체험 → Startup €199/월~; Pollination 클라우드 시뮬레이션 종료(2026-03); Speckle 무료 = 1프로젝트·3명·버전 100개, Automate는 유료; Delve sunset; Wallacei 사이트 'Soon'·F4R는 Rhino 6/7용; Design Explorer는 2024-02 이후 정체(MIT).
4. 5목적 시각화 3가지: ① 평행좌표(브러시, A–E·기존 18건 오버레이) ② 레이더/페탈 소배열 + 숫자표 ③ 산점도 행렬 10패널 + 지배 표. 근거 Tušar–Filipič 평가표·Gao 외 2019·Miettinen 2014·Li 외 2008. A–E 선정은 pymoo의 ASF·pseudo-weights·high trade-off.
5. 실시간 원칙: 닫힌식·대리모델·저해상 레이캐스트만 슬라이더에 연결하고, r5py 등시선·1 m 조망·Ladybug는 사전계산(최종 5안 × 밀도 3단계)으로 얹는다.
6. 공수 [추정]: 안A 6–9일(MVP 3–4일), 안B 8–12일. `gjplan/constraints/compile.py`는 현재 스텁(`raise SystemExit`) [확인] → 안B는 엔진 완성에 종속.
7. 지금 당장: 기존 산출물(규제 적용안·규제 미적용 깔끔안)을 'Design Option' 2개로 넣어 안A MVP를 먼저 만들고, gjplan 결과가 나오면 A–E로 교체.
8. 한계: WebSearch 한도(200/200) 소진으로 후반부는 직접 fetch만 사용. 미확인 항목은 §8.

---

## 1. 구현 방식 비교 (a)–(h)

### 1-A. 기능·난이도·오프라인

| 방식 | 장점 | 단점·주의 | 1인 난이도 | 오프라인 단일 HTML |
|---|---|---|---|---|
| (a) ShapeDiver | GH 정의를 그대로 슬라이더 앱·3D 뷰어로 공개(App Builder, 공유 URL) | 엔진이 Python(gjplan)이라 GH로 재구현 필요. 연산 30–60초 상한·크레딧 과금. 클라우드 필수 | 낮음~중(GH 숙련 전제) | 불가(서버 연산) |
| (b) Speckle | Rhino/GH 커넥터, 속성별 필터·색, 버전·코멘트로 A–E 공유 | 재계산 엔진이 아님(슬라이더→지오메트리 없음). Automate는 유료 | 중 | 비추천 [추정](뷰어가 서버에서 객체를 로드하는 구조) |
| (c) Rhino.Compute / Hops | GH를 REST로 호출. 로컬 구동 시 데이터 반출 없음. Ladybug 등 GH 생태계 그대로. McNeel appserver(Node, 결과 메모리 캐시·Server-Timing) 예제 | 슬라이더마다 GH 솔브(정의 크기에 비례; 포럼 보고 3 MB 정의 2–8초/요청 [T4 단일 사례]). Windows 상시 구동. REST·rhino3dm.js 배선 | 중~높음 | 불가(Compute 프로세스 필요). 로컬 노트북 시연은 가능 |
| (d) three.js / deck.gl / Cesium + JSON | 완전 오프라인·0원·지연 최소. gj-datamap(Vite·MapLibre·ECharts) 자산 재사용 | 슬라이더로 "새 지오메트리 생성" 불가(이산 시나리오 + 닫힌식 변형). 프런트 코드 필요 | 중 | three.js 가능(PoC 1.29 MB). deck.gl 조건부(dist.min.js 2.07 MB, 배경지도 별도). Cesium 비현실적(Cesium.js만 6.1 MB + 에셋·워커) |
| (e) Streamlit·Dash·Panel·Observable·marimo + pydeck/plotly | gjplan 함수 직접 호출(코드 재사용), 로컬 서버라 지연 작음 | 서버 프로세스 필요. 3D 뷰포트 표현력 제한. WASM 계열은 로딩 큼·인터넷 필요 | 낮음 | 불가. marimo는 기본 file:// 불가, `--single-file`도 "Internet access is required to load marimo, Pyodide, and Python packages" [확인] |
| (f) Pollination·Ladybug + Design Explorer/Colibri | Design Explorer가 평행좌표·레이더·산점도 행렬·3D 뷰어를 이미 제공(MIT). 입력은 CSV | Pollination 클라우드 종료. DE는 2024-02 이후 정체·D3 구버전. KPI 링·NPV 없음 | 낮음(DE 단독) | 정적 사이트라 로컬 서버로 가능 [추정], 로컬 구동은 미테스트 [미확인] |
| (g) Unity / Unreal | 표현력·XR | 공수 최대, 빌드 크기, 데이터 파이프라인 직접 구현 | 높음 | 불가(실행파일 또는 대용량 WebGL) |
| (h) GH 내부 UI(Human UI) | Rhino 안에서 완결(WPF: 슬라이더·탭·3D 뷰포트·웹브라우저 컴포넌트), 오프라인 | Rhino 8 호환 [미확인](F4R 문구는 Rhino 6 시기). 웹 공유 불가 | 중 | 불가(GH 안) |

### 1-B. 비용·라이선스·2026-10 상태 (모두 2026-10-06 직접 수신)

| 방식 | 비용(무료 한도) | 데이터 반출·라이선스 | 상태·근거 |
|---|---|---|---|
| (a) ShapeDiver | 14일 체험(카드 불필요, 연산 60초). Startup €199/월~(연간결제; 월 2,000 credits, 연산 30초, GH 50 MB, 출력 20 MB, 2석, EU 공유서버, "연매출 €1M 미만·비핵심 앱"). Business €499/월~(10,000 credits, 60초, 5석, 백엔드 API). 초과 4¢/credit. 학생·교수 최대 50% 할인 또는 체험 최대 3개월 연장(상업활동 불가, 영업팀 개별 판단) [확인: shapediver.com/pricing, faq.shapediver.com] | GH 파일·모델이 ShapeDiver 서버(EU/북미/아시아)에 업로드. 공유시스템 가동률 best effort(98%) [확인] | Free 플랜: 2025-07-23 공식 블로그는 "Free 2025 = 연산 30초·모델 10 MB·출력 10 MB·월 50 credits·스크립트 허용, 웹 퍼블리싱 불가" 기술. 그러나 2026-10 pricing 페이지에는 Free 카드가 없고 헬프센터는 "Free users can start a trial"을 남겨 문서 간 불일치 → 존속 여부 [미확인]. 주의: shapediver.co(점 co)는 TLS 인증서가 saaspages.xyz로 불일치하는 비공식 도메인이며, 검색에 노출된 "Designer €99 / Business €699" 요금표는 공식 .com과 맞지 않아 신뢰하지 않는다 |
| (b) Speckle | Explore(무료): 1 프로젝트·사용자 3명·버전 100개(워크스페이스 전체)·이력 30일·기본 저장 리전 UK. Custom Plans(유료, 가격 비공개): 무제한·Automate·화이트라벨 임베드 [확인: speckle.systems/pricing]. docs의 'new-plans-faq'는(WebFetch 요약 기준) Explore 10명·Team $99/월 등 다른 값을 적고 있어 불일치(문서가 구버전으로 보임, 갱신 시점 [미확인]) | speckle-server = Apache-2.0(단 workspaces·gatekeeper 디렉터리는 EE 라이선스), @speckle/viewer(npm 2.31.14) = Apache-2.0, 셀프호스트용 docker-compose 파일 존재 [확인: 저장소] | Automate: docs "Enterprise-only" [확인] |
| (c) Rhino.Compute | 로컬 일반 Windows PC = 추가 비용 없음(Rhino 라이선스 확인). Windows Server 계열은 $0.10/코어/시간(분 단위), 서비스 계정 팀 필요 [확인: McNeel 문서 2026-03-16 갱신] | 로컬이면 반출 없음. 타임아웃 기본 100초, 요청 본문 기본 약 50 MB [확인: FAQ] | compute.rhino3d 저장소 최근 push 2026-10-02(활발), appserver는 2025-08-11 [확인: GitHub API]. Windows·Linux(Ubuntu 24.04, Amazon Linux 2023 테스트) 지원, macOS 불가 [확인] |
| (d) three.js 등 | 전부 무료 오픈소스. Cesium ion: Community 무료(개인·비상업), Commercial $149/월(개인)~$524(팀), Premium $499~$874 [확인: cesium.com 가격 페이지] | three.js r186(2026-09-24, MIT), deck.gl v9.4.0(2026-09-05, MIT), CesiumJS 1.146(2026-10-01, Apache-2.0), ECharts 6.1.0(Apache-2.0), vite-plugin-singlefile 2.3.0(2025-07-02, MIT), three-mesh-bvh 0.9.15(MIT) [확인: GitHub API·npm] | 모두 활발히 유지 |
| (e) Python UI | 전부 무료. Streamlit 1.65.0(2026-10-02, Apache-2.0), Dash 4.4.1(2026-07-21, MIT), Panel 1.9.4(2026-08-17, BSD-3), marimo 0.25.1(2026-10-01, Apache-2.0), Observable Framework 1.13.4(2026-03-02, ISC; 저장소 마지막 push 2026-05-15) [확인: GitHub API] | 로컬 실행이면 반출 없음 | pydeck의 오프라인 HTML export 옵션은 [미확인] |
| (f) Pollination 등 | Pollination: Grasshopper 플러그인 $0, Rhino 플러그인 $1,375/년 또는 $125/월, Revit $2,750/년, 30일 체험, 학생·강사 개인 90% 할인 [확인: pollination.solutions/pricing]. Design Explorer·Wallacei·Octopus 무료 | Ladybug·Honeybee 코어는 AGPL-3.0(ladybug v0.44.62 2026-09-22, honeybee-core v1.64.76 2026-10-05) [확인]. Design Explorer MIT [확인]. Wallacei 독점·무료, Octopus "Other"·무료 [확인: F4R] | Pollination 클라우드 시뮬레이션 종료(아래 §1-C). Design Explorer 마지막 push 2024-02-19, Colibri.Grasshopper 마지막 push 2022-06-22 [확인]. wallacei.com은 'Soon'(© 2022) 자리표시, F4R는 "designed for Rhino 6 and 7" [확인] |
| (g) Unity/Unreal | Unity Personal: 직전 12개월 매출·조달 자금 $200K 미만이면 무료. Pro $2,310/년/석($210/월). 비게임 용도이고 회사 재무가 $1M 초과면 Industry(견적) [확인: unity.com/products/compare-plans]. Unreal: 로열티 5%(누적 $1M 초과분) [스니펫: T4 블로그], Epic 1차 약관은 403으로 못 열음 [미확인] | 로컬 | 마감 대비 비추천 |
| (h) Human UI | 무료·오픈소스(Bitbucket), WPF 기반 [확인: F4R] | 로컬 | Rhino 8 호환 [미확인] |

### 1-C. 서비스 상태 변동 요약 (요청: 종료·인수·요금 변경 확인)

- Pollination Cloud: 종료. 2026-03-08 Ladybug Tools 포럼 답변(사용자 mostapha)이 "most recently we stopped offering Pollination cloud simulation as a service", 2026-03-09 답변(사용자 chris)이 "cloud computing is not longer a service that we offer ... invest in a good desktop with an Intel i9 CPU (at least 20 processors) ... we do not use the GPU in comfort mapping simulation" [확인: discourse.ladybug.tools/t/speed-up-the-process/40072]. Pollination 문서 FAQ도 "cloud simulation, which we don't offer anymore" [확인]. pollination.cloud는 pollination.solutions로 리다이렉트되며 현 상품은 CAD 플러그인이다 [확인]. 따라서 "Pollination Cloud 병렬 run + Pollination Design Explorer" 경로는 쓸 수 없고, Ladybug는 로컬(i9)에서 돌린다.
- ShapeDiver: 요금 구조 변경 가능성 높음(위 표). 공식 .com 기준으로 판단하고 .co 사이트·제3자 요금 비교 사이트는 제외.
- Speckle: 무료 한도 축소·Team 카드 소멸(pricing 페이지 기준), docs와 불일치.
- Delve(Sidewalk Labs): delve.sidewalklabs.com이 302로 Google Earth 페이지(utm_campaign=sunset)로 리다이렉트 → 종료 [확인: curl -I].
- Wallacei: 사이트 'Soon', F4R는 Rhino 6/7용, Octopus는 Wallacei·Biomorpher와 HelixToolkit 충돌로 크래시하는 known issue [확인: F4R]. 두 도구 모두 사용자의 Rhino 8 환경 호환 [미확인].
- Design Explorer: 2024-02-19 이후 push 없음, 아카이브는 아님 [확인]. EPFL Building2050 그룹이 연구 결과 호스팅에 계속 사용 [확인: design-explorer.epfl.ch].
- pandana(UrbanSim): README 상 "Status: LTS / Compatibility", 라이선스 AGPL-3.0 [확인].
- ArcGIS Urban: 상태 [미확인](검색 한도 소진).
- CityFinder / "Intelligent Urban Development Modelling Platform": 제품명으로 1회 검색했으나 무결과 [미확인]. 화면 요소만으로 구현 방식을 유추했다.

---

## 2. 다목적 최적화 결과 탐색 UI

### 2-A. 사례와 상태

| 도구/자료 | 제공 뷰 | 상태·비고 |
|---|---|---|
| Design Explorer (CORE studio, Thornton Tomasetti) | 평행좌표(D3), 레이더, 산점도 행렬, 3D 뷰어(Spectacles), 범위 슬라이더, 별점 [확인: README] | 데이터 = CSV: `in:<이름>`(입력) · `out:<이름>`(출력) · `img` · `threeD` 열 + settings.json [확인: 샘플 CSV]. MIT. 2024-02 이후 정체. Colibri.Grasshopper가 GH → DE 내보내기 |
| Pollination Design Explorer | (클라우드 연동) | 클라우드 종료로 사용 불가 [확인] |
| Wallacei X / Analytics | NSGA-II + K-means 군집, 선택·재구성·출력 [확인: F4R] | 무료·독점. Rhino 6/7 표기, 사이트 'Soon'. 도시 형태 MOO의 해 선택 프레임워크 논문(Showkatbakhsh & Makki 2022, Buildings 12(9):1473)이 선택 메커니즘을 객관·주관 두 갈래로 정리 [확인: 초록] |
| Octopus | SPEA-2·HypE, 목적공간에서 해의 3D 모델 미리보기, 탐색 중 선호 해 선택·목적 변경 [확인: F4R] | 무료. 위 충돌 이슈 |
| pymoo 0.6.2 시각화 | Scatter(2D/3D/ND 쌍), PCP, Heatmap, Petal, Radar, Radviz, Star Coordinate [확인: pymoo.org] | 전부 matplotlib 래퍼(정적 이미지) → HTML 대시보드에서는 ECharts로 재구현. MCDM 모듈: Compromise Programming(ASF), Pseudo-Weights, High Trade-off Points [확인] |
| VIDEO(Kollat & Reed 2007, Environ. Model. Softw.) | 3개 이상 목적 해집합을 시각적으로 탐색(지하수 모니터링 4목적 사례) | [스니펫] 원문 미열람 |

### 2-B. many-objective 시각화 연구에서 확인한 근거

- Tušar & Filipič(IEEE TEVC 19(2):225–245, 2015)의 GECCO'20 튜토리얼 슬라이드(Filipič & Tušar)에 기법별 평가표가 있다 [확인: PDF 슬라이드를 직접 판독; 저자의 정성 판단이며 사용자 실험이 아님]. 열: 지배관계 보존 / 전선 형상 / 목적 범위 / 해 분포 / 강건성 / 대규모 집합 / 동시 시각화 / 확장성 / 단순성 (✓ 좋음, ≈ 부분, × 약함).

| 기법 | 지배관계 | 전선형상 | 목적범위 | 분포 | 강건성 | 대규모 | 동시 | 확장성 | 단순성 |
|---|---|---|---|---|---|---|---|---|---|
| 평행좌표(PCP) | ≈ | × | ✓ | ≈ | ✓ | × | × | ✓ | ✓ |
| 산점도 행렬(3-D 변형 슬라이드 기준) | × | ≈ | ✓ | ≈ | ✓ | ≈ | ✓ | × | ✓ |
| RadViz | × | × | × | ≈ | ✓ | ≈ | ✓ | ✓ | ✓ |
| Level diagrams | × | ≈ | ✓ | × | ✓ | ≈ | ✓ | ✓ | ✓ |
| Interactive decision maps | × | ≈ | ✓ | ≈ | ✓ | ✓ | × | × | ≈ |
| Prosection | ✓ | ✓ | ≈ | ✓ | ✓ | ✓ | ✓ | × | ≈ |

  지배관계를 완전히 보존하는 것은 prosection뿐인데 확장성이 약하다(4목적 안팎에 적합). 5목적에서는 어느 한 기법도 만능이 아니다.
- Gao, Nie, Li(arXiv:1903.01768, 2019): 대표 기법 6개를 DTLZ 벤치마크로 실증 비교하고 "no single visualisation technique is able to provide a comprehensive understanding" 결론 [확인: 초록] → 상보적 다중 뷰가 근거.
- Miettinen(OR Spectrum 36(1):3–37, 2014; 저자 수용본 열람): "None of the graphical representations can be claimed to be better than the others", "not to leave the decision maker alone with too many visualization possibilities", "the data of the alternatives in the good old table format should not be forgotten". 인용된 실험(표·막대·star 비교)에서 표가 가장 정확·빠르고 대안 순위 매기기는 star 표현이 가장 쉬웠다고 하되 "개별 실험으로 과도한 결론을 내리지 말라"는 단서를 붙인다 [확인].
- Li, Martens, van Wijk(Information Visualization, DOI 10.1057/ivs.2008.13): 25명 실험에서 산점도가 PCP보다 2배 많은 상관 수준을 구별하게 했고 PCP는 음의 상관 쪽 편향 → "산점도가 PCP보다 상관 판단에 효과적" [확인: 초록] → 트레이드오프(음의 상관)를 읽히려면 PCP 단독은 위험.
- Waibel, Wortmann, Evins, Carmeliet(Energy and Buildings 187:218–240, 2019): 모델 기반(RBFOpt)은 수렴이 매우 빠르지만 국소해에 갇힐 위험, 모든 지표에서 우세한 알고리즘은 없음 [확인: 초록] → 대리모델 루프는 최종 정직평가 재검증으로 보완(프로젝트 설계와 일치).

### 2-C. 추천 3가지 (5목적 NSGA-III 결과를 의사결정자에게)

1. 평행좌표 + 브러시 필터(탐색용)
   - 구성: 5축 모두 "위쪽이 좋음"으로 방향 통일(f2·f4는 반전 표기), 회색 = 파레토 해 200개, 굵은 컬러 = 대안 A–E, 점선 = 기존 제안 15건 + 공고안 + 참조사례 2건(비교 18건; 파레토 해와 같은 평가함수·같은 정규화로 평가한 값만). 축 브러시로 "사업성 ≥ X, 유산영향 ≤ Y" 같은 필터 → 남은 해 개수 실시간 표시. 축 순서는 417쪽 연구의 5방향 순서로 고정하고 재배열 버튼 제공.
   - 근거: PCP는 확장성·단순성·목적범위 ✓(Tušar–Filipič), pymoo 문서의 "higher-dimensional data ... how dense solutions are distributed in different ranges regarding each coordinate", Design Explorer의 기본 뷰.
   - 한계: 대규모 집합 ×, 인접 축 쌍만 상관이 읽힘(Li 외) → ③과 병행.
2. 레이더(스타)/페탈 소배열 + 정규화 값 표(비교·결정용)
   - 구성: A–E 5안을 같은 극좌표에 겹치거나 소배열로 나열하고, 기존 안 중 대표 1–2건과 비교. 하단에 정규화 값 표(정확도 확보). 기존 안의 "가장 낮은 축"을 붉게 표시해 "어느 축을 희생했는가"를 직접 보인다(논증 구조의 핵심 문장).
   - 근거: Miettinen(소수 대안에는 표 + star), pymoo Petal("compare one solution with another ... trade-offs")·Radar(ideal/nadir 경계, 척도가 다르면 정규화 권장), 레이더는 Design Explorer에도 포함.
   - 주의: 다각형 면적이 축 순서에 좌우되므로 면적 채우기는 약하게 하고 윤곽선과 값 라벨 중심. ideal/nadir 기준을 화면에 명시.
3. 산점도 행렬(5목적 → 10패널) + 지배 표(트레이드오프·논증용)
   - 구성: 모든 2D 쌍 10개 패널에 파레토 해(회색)·A–E(컬러)·기존 18건(마름모) 겹침. 각 패널에서 기존 안이 전선 안쪽(지배됨)인지 한눈에 확인. 별도 표: "기존 18건 각각 몇 개의 파레토 해에 지배되는가 / 가장 큰 격차 축". 지배 여부는 산점도로 완전 보존되지 않으므로(Tušar–Filipič ×) 계산해서 표로 제시한다.
   - 근거: 산점도는 목적범위·강건성·단순성 ✓, 패널 수는 m(m−1)/2라 m=5에서 10으로 허용 범위, Li 외(상관 판단 우수), Gao 외(단일 기법 불충분).
   - 구현: ECharts는 평행좌표·레이더·산점도·히트맵을 내장(PoC에서 gauge·radar·parallel·line 동작 확인). 산점도 행렬은 다중 grid로 직접 구성 [추정].
   - 보류한 대안: RadViz(해석 난도, 전선형상·목적범위 보존 ×), Prosection(확장성 ×), Level diagrams(균형해 탐색에 유리하나 학습 필요 → 필요 시 보조).

A–E 선정 규칙(추적표에 기록): E(균형)는 정규화 후 이상점까지 Chebyshev 거리가 최소인 해(= pymoo ASF에 균등 가중). 이는 사후 선택 규칙의 정의일 뿐 목적함수에 가중치를 넣는 것이 아님을 추적표에 명시한다. A–D는 해당 목적 극단 근방(다른 목적 하한 제약 포함), 보조로 pseudo-weights·high trade-off points(knee) [확인: pymoo MCDM 문서].

---

## 3. 실시간 갱신(<1초) — 닫힌식·대리모델·저해상도

### 3-A. 상용·연구 사례 (지연·정확도)

| 사례 | 지연 | 정확도·한계 | 근거 |
|---|---|---|---|
| Autodesk Forma(Spacemaker 후신) Rapid wind | "instantaneously" | ML이 상세(CFD) 분석을 보완, 검증용 정확 결과는 별도 분석 | [확인: Autodesk 블로그 2023-06-06]. 상세 풍 분석 "30–90분"은 [스니펫: BIM Chapters 블로그 T4], Autodesk 학습 페이지는 "can take a while"로만 표기 [스니펫], 정확도 수치 공개 [미확인] |
| Forma Rapid noise | instantaneous / 일반 소음 분석은 "several minutes" | "tens of thousands of noise simulations"로 신경망 학습 | [확인: Autodesk 블로그 2023-07-03] |
| Esri CityEngine | 파라미터 변경 시 FAR·GFA 보고값 갱신 | `report()`가 생성 중 값을 수집해 Inspector Reports에 표시 | [확인: report 연산 문서] / 슬라이더 연동은 [스니펫: Esri 튜토리얼] |
| TestFit | "real-time deal prototyping", 설계와 연동되는 Pro Forma 애드온 | 지연·정확도 수치 없음 | [확인: 공식 사이트 문구, T4 마케팅]. 요금: Parking Solver $195/월, Site Solver $15,000/년~, Pro Forma +$170/월 [확인] |
| Delve | 종료 | - | [확인: 리다이렉트] |
| FastFlow(Low 외, arXiv:2211.12035, 2022) | CNN 추론(초 단위 이하) [추정] | 미학습 도시 레이아웃에서 시험 오차 0.1 m/s 미만 | [확인: 초록] |
| Wang·Ma·Niu·You(Building and Environment 269:112426, 2025) | CFD 대비 3–4 orders of magnitude 빠름 | 4,000 시뮬레이션 학습, 미학습 구성(건물 1–4동) MAPE 1.74–12.49%, 밀집 다건물에서는 취약(domain transferability 제한) | [확인: 초록] |
| Kastner & Dogan(Building and Environment 242:110384, 2023) | "instantaneous" | cGAN 기반 | 서지만 [확인], 수치 [미확인] |
| pandana(UrbanSim) | contraction hierarchies, C++ | "hundreds of thousands of network queries in under a second" | 요지는 [스니펫], README의 "super-fast ... C++"만 [확인] |
| three-mesh-bvh | 500 rays vs 80,000 polygon 모델을 60 fps | 브라우저 레이캐스트 가능 | [확인: README] |

교훈: 상용 도구도 "즉시 = 근사(ML·닫힌식), 검증 = 별도 정밀 분석"의 2단 구조이고, 근사 모델은 학습 분포 밖(밀집 배치 등)에서 오차가 커진다. 따라서 UI에 값의 출처(surrogate / exact)와 오차를 항상 표시한다.

### 3-B. 무거운 평가를 실시간 대시보드에 얹는 3가지 방법과 프로젝트 적용

| 평가 | 정직 비용(설계서 Part5 §5.3) | 대시보드 전략 |
|---|---|---|
| 면적·연면적·FAR·인구·일자리·탄소·NPV/IRR/손익분기 | ~3 ms (numpy) | 닫힌식을 JS로 이식(슬라이더 입력마다). PoC 0.05 ms |
| f1 15분 등시선(r5py 10–60 s) | 10–60 s | 사전계산 룩업(해·옵션별 값) + LightGBM 대리(JS 3 µs). 가로망 변경이 없는 슬라이더(프로그램·밀도)와는 연동하지 않고 "대안 선택 시 표시" |
| f2 조망 차단(5–30 s) | 5–30 s | 사전계산 + 저해상 근사. 시점별 방위각 지평선각 캐시와 신규 매스의 최대 고각 비교(O(건물수 × 방위수)) 방식을 제안 [추정, 문헌 미확인]. 최종 5안만 1 m 정직평가 |
| Ladybug 일조·열환경 | 분 단위 | 루프·슬라이더에서 제외. 최종 5안 × 밀도 3단계(15조합)만 로컬 사전계산 → 센서격자 값 배열(JSON/base64)을 정점 색으로. 슬라이더 이동 중에는 "마지막 정밀값(stale)" 배지 + 저해상 레이캐스트 근사치를 따로 표시 |

### 3-C. 로컬 실측(PoC) — 모두 [확인], 단 한계 명시

환경: Windows 11, i9-13900K, 32 GB, Chrome 154 headless(WebGL은 SwiftShader 소프트웨어 렌더라 렌더 시간은 대표성 없음).

| 항목 | 결과 |
|---|---|
| 단일 HTML 번들(three r186 + OrbitControls + three-mesh-bvh + suncalc + ECharts 6.1 gauge/radar/parallel/line/bar + 실제 계획 데이터 21 KB) | 1,294,036 B, gzip 약 382 KB. file://로 열림 |
| 슬라이더 입력 1회(층수 배율·할인율) | 높이 갱신 0.002 ms, KPI 닫힌식(건물 57개·8 KPI·30년 현금흐름 NPV/IRR) 0.054 ms, ECharts 9개 setOption 3.17 ms, 렌더 0.21 ms, 합계 3.44 ms |
| 일조 저해상 재계산(동지 5시각 × 8 m 격자 4,484점 = 22,420선, 병합 1,212삼각형 BVH 재구축 포함) | 14.1 ms, 합계 17.4 ms. 속도 측정용이며 실제 일조 지표 아님(DoubleSide 사용) |
| LightGBM(300트리·15리프·14유전자·500샘플, 합성 목표 R² 0.922) → JSON | 196 KB(gzip 44 KB). JS 추론 3.2 µs/회(Node 24), 파이썬 단건 1.1 ms, JS-파이썬 최대 오차 1.3e-5. R²는 합성 데이터 값이며 프로젝트 R²가 아님 |
| FastAPI 로컬 왕복(shapely buffer 19획지·교차 연산 + numpy KPI + LightGBM 1건) | 중앙값 2.4 ms(p95 2.6 ms), 서버 계산 1.4 ms, 응답 2.4 KB. gjplan S1–S4 생성 비용은 포함하지 않음 [미측정] |
| 시나리오 1개 지오메트리(획지 19·건물 57·도로 16·공원 4 = 722정점) | JSON 21,088 B(gzip 4,658 B). 0.1 m 정수 델타 int16 2,888 B(gzip 1,906 B, base64 2.5 KB) → 1,000개 ≈ 2.5 MB(base64) |

참고: Rhino.Compute는 정의에 따라 다르며 3 MB 정의에서 2–8초/요청 보고 [T4 단일 사례]. 즉 "슬라이더마다 GH 솔브"는 정의가 가볍지 않으면 <1초를 보장하기 어렵다.

---

## 4. 현실적 최소 구조 2안

### 4-0. 공통 원칙
- 프런트는 `evaluate(state) → {layout, kpi, obj, fin}` 인터페이스 하나로 추상화한다. 안A는 이 함수가 JSON 조회 + 닫힌식, 안B는 fetch('/evaluate')다. 데이터원만 바꾸면 A → B 확장이 된다.
- 제약은 페널티가 아니라 불가능: 슬라이더 범위를 시나리오별 `max_floors/max_h_m`(규제 4겹 min)로 clamp한다. PoC에는 clamp가 없다.
- 모든 원단위·단위수익은 `assumptions` 블록에 T등급·가정 여부와 함께 두고 UI 툴팁에 표시한다(CLAUDE.md §3.1–3.2). PoC의 값은 속도 측정용 가정치다.
- 비교 18건과 파레토 해는 같은 5목적 함수로 평가한 값만 같은 화면에 올린다. 대리값(surr)과 정직값(exact)은 `obj_src`로 구분한다.
- 스케일(S1/S2/S3)을 KPI마다 명시해 혼용을 막는다(CLAUDE.md §3.3).

### 4-1. 안A — 정적 시나리오 라이브러리 + 단일 HTML

파이프라인: `gjplan optimize` → 파레토 해 N개(예 200) + 비교 18건 + A–E → `export_scenarios.py` → `scenarios.json` → Vite + vite-plugin-singlefile → `dashboard.html` 1개(오프라인).

필요 라이브러리: Python — numpy, shapely, pymoo 0.6.2, lightgbm(이미 설계에 포함). JS — three 0.186(MIT), echarts 6.1(Apache-2.0), vite + vite-plugin-singlefile(MIT); 선택 three-mesh-bvh 0.9.15(MIT). suncalc 라이선스는 npm 레지스트리에 표기가 없어 [미확인](태양 위치는 직접 구현해도 수 줄).

슬라이더의 의미: (i) 지오메트리를 바꾸지 않는 슬라이더(층수 배율, 주거 비중, 공사비, 할인율, 수익 배율)는 닫힌식 + scale.y로 즉시 반영, (ii) 지오메트리를 바꾸는 변수(횡축 개수·획지 후퇴 등)는 상위 민감도 3–4개를 격자/LHS로 미리 샘플링해 두고 슬라이더가 가장 가까운 시나리오로 스냅(Design Explorer의 `in:`/`out:` 전수 샘플 방식과 같은 발상). 4변수 × 5수준 = 625시나리오 ≈ 1.6 MB(base64) [추정].

JSON 스키마 예시(`scenarios.json`, 프로젝트 기존 필드 plot/name/use/cat/area_m2/max_floors/max_h_m/floors/floor_h_m/footprint_m2를 축약해 사용):

```json
{
  "meta": {
    "schema": "gj-scenarios/1", "site": "구경주역", "crs": "EPSG:5187",
    "origin": [219720.0, 361300.0], "site_area_m2": 79438, "site_area_tier": "T4",
    "built": "2026-10-06", "gjplan_commit": "<hash>", "config_sha1": "<sha1>"
  },
  "objectives": [
    {"id": "f1", "name": "접근성", "dir": "max", "scale": "S2", "ideal": 0.92, "nadir": 0.35,
     "src": "surrogate", "r2": 0.88, "mae": 0.04, "tier": "T2"},
    {"id": "f2", "name": "유산영향", "dir": "min", "scale": "S1", "ideal": 0.0, "nadir": 1.0, "src": "exact"}
  ],
  "assumptions": [
    {"id": "rev_housing", "label": "주거 연 수익 원단위", "value": 0.09, "unit": "억원/천㎡·년",
     "tier": "가정", "source": null},
    {"id": "discount", "label": "할인율", "value": 0.05, "tier": "가정"}
  ],
  "sliders": [
    {"id": "fm", "label": "층수 배율", "min": 0.5, "max": 1.6, "step": 0.05, "default": 1.0,
     "clamp": "max_floors", "affects": ["kpi.gfa", "kpi.far", "fin.*", "geom.height"]},
    {"id": "discount", "label": "할인율", "min": 0.02, "max": 0.12, "step": 0.0025, "default": 0.05,
     "affects": ["fin.*"]}
  ],
  "options": [
    {"id": "E", "label": "균형", "kind": "pareto", "scenario": "s0137",
     "rule": "ASF(ideal-nadir)", "preset": {"fm": 1.1}}
  ],
  "scenarios": [
    {
      "id": "s0137", "kind": "pareto",
      "genes": [0.31, 0.77],
      "obj": [0.71, 0.22, 0.54, 0.31, 0.63],
      "obj_src": ["surr", "exact", "exact", "exact", "surr"],
      "layout": {
        "lots": [{"id": "L01", "use": "주거", "cat": "주거", "area": 7109,
                  "max_floors": 5, "max_h_m": 16.0, "ring_q": "<base64 int16 delta, 0.1 m>"}],
        "buildings": [{"lot": "L01", "floors": 5, "fh": 3.2, "fp": 3148, "ring_q": "<...>"}],
        "roads": [{"id": "A", "w_m": 15, "ring_q": "<...>"}],
        "parks": [{"id": "P1", "ring_q": "<...>"}]
      },
      "kpi": {"gfa": 227493, "far": 2.86, "res": 1701, "jobs": 3109, "co2_t": 123000},
      "pre": {"iso15_pop": 18450, "view_block_px": 1210,
              "sun_grid": {"res_m": 5, "n": 3800, "q": "<base64>"}}
    }
  ]
}
```

예상 공수(1인, 일 단위, [추정]):

| 작업 | 일 |
|---|---|
| `export_scenarios.py` + 스키마·검증(처음엔 plan_clean/plan_massing 산출물로) | 1–1.5 |
| 3D 뷰포트(three.js, 팔레트, 선택·툴팁) | 1–1.5 |
| KPI 링 8 + 입력 탭·슬라이더 + 옵션 드롭다운 + clamp | 1–1.5 |
| 재무 인포그래픽(NPV·IRR·손익분기·민감도) | 1 |
| Pareto 탐색 3뷰 + 비교 18건 오버레이 + 지배 표 | 1.5–2 |
| 단일 HTML 빌드·오프라인 점검·PPT용 캡처 | 0.5 |
| 합계 | 6–9 (MVP: 3D + 링 + 옵션 + NPV = 3–4) |

위험: ① 슬라이더로 임의 지오메트리를 만들 수 없어 "데이터에 따라 파라메트릭"이라는 인상이 약해질 수 있음 → 스냅 샘플링과 "유전자 → 지오메트리" 표시로 보완. ② 시나리오 수 × 2.5–5 KB로 용량 증가 → 정점 양자화. ③ 가정치 남용 → assumptions 분리·등급 배지. ④ 대리모델 오차 표기 누락 → obj_src·r2 필수 필드. ⑤ 규제 clamp 누락 시 불법 높이 노출.

### 4-2. 안B — 로컬 Python 서버(FastAPI) + 실시간 슬라이더

구성: `gjplan serve`(FastAPI + uvicorn). 요청 → S1–S4 규칙기반 생성 → evaluate(cheap + surrogate, 놓을 때 mid) → JSON. 프런트는 안A와 동일하고 `evaluate()`만 fetch로 교체. "현재 상태를 안A 형식으로 내보내기(freeze)" 버튼을 반드시 둔다(오프라인 단일 HTML 요건 보전).

라이브러리(PoC에서 설치·동작 확인): fastapi 0.142.2, uvicorn 0.54.0, httpx 0.28.1(테스트), shapely 2.1.2, lightgbm 4.7.0, numpy, pymoo 0.6.2.

요청/응답 스키마 예시:

```json
POST /evaluate
{ "option": "E", "genes": [0.31, 0.77],
  "params": {"fm": 1.1, "res": 1.2, "cx": 1.0, "discount": 0.05, "rev": 1.05},
  "mode": "fast" }

200 OK
{ "scenario_key": "sha1(genes+params)",
  "layout": { "lots": [], "buildings": [], "roads": [], "parks": [] },
  "kpi": {"gfa": 227493, "far": 2.86, "res": 1701, "jobs": 3109, "co2_t": 123000},
  "obj": [0.71, 0.22, 0.54, 0.31, 0.63], "obj_src": ["surr","exact","exact","exact","surr"],
  "fin": {"npv": 412000, "irr": 0.061, "breakeven_year": 14, "cum": []},
  "timing_ms": {"generate": 3.1, "evaluate": 1.0, "surrogate": 1.1},
  "warnings": ["clamp: L07 floors 7 -> 5 (max_floors)"] }

GET  /scenarios/{id}   안A의 사전계산 시나리오 조회
POST /freeze           현재 상태 → scenarios.json 조각(안A 형식)
```

운영 원칙: input 이벤트 중에는 mode=fast(cheap + surrogate, 디바운스 100 ms), 슬라이더를 놓을 때 mode=full(mid + 위상 해시 캐시). 설계서 수치(mid 0.3 s, 캐시 시 ~0.05 s)는 설계 목표치이며 실측 아님 [미확인].

예상 공수 [추정]: 서버 래핑 1.5–2일(엔진 모듈 완성 전제), 프런트 공통부 5–7일(안A와 공유), 캐시·디바운스·에러처리 1일, freeze·리허설·안정화 1일 → 8–12일. 엔진(generate/evaluate) 미완성분은 별도(compile.py 스텁 [확인]).

위험: ① 발표 노트북에서 서버 구동 실패. ② gjplan 모듈 미완성 시 일정 전체가 엔진에 종속. ③ 생성·mid 평가 지연이 0.3 s 이상이면 슬라이더 체감 저하. ④ 오프라인 단일 HTML 요건 미충족(freeze로 완화). ⑤ 포트·방화벽·CORS 같은 운영 변수. 참고: LightGBM은 단건 예측에서 `n_jobs=1`로 고정해 측정했다. PoC에서 요청이 처음 멈춘 원인은 500 에러(MultiPolygon 처리 버그)의 트레이스백이 소비되지 않는 stderr 파이프에 쌓인 것으로 추정되며 [추정], LightGBM 스레드 문제는 확인하지 못했다.

### 4-3. 이미지 속 5요소 → 모듈 대응표

| 이미지 요소 | 안A 모듈 | 안B 차이 | 데이터 |
|---|---|---|---|
| (1) KPI 링 게이지 8개 | `kpi.js`(닫힌식) + ECharts gauge ×8(PoC 동작 확인). 링 8 제안: f1–f5 + 거주인구·야간활동 + 내재탄소 | 값만 서버 응답 | `kpi`, `obj`, `assumptions` |
| (2) 공간유형별 색 지오메트리 | `palette.js`(cat/use → 색) + 평면(획지·도로·공원) + 압출 매스 | layout을 서버가 반환 | `layout.*` |
| (3) 인터랙티브 3D 뷰포트 | `viewport.js`: three.js + OrbitControls, scale.y로 층수 갱신, 선택·툴팁, (선택) three-mesh-bvh 일조 근사 | 동일 | `layout`, `floors` |
| (4) 입력 옵션 탭 + Design Option 드롭다운 | `controls.js`: 탭(Carbon…Financial를 프로젝트 지표로 재정의) + `<select>` = `options[]` + 슬라이더 `affects` 맵 | 변경 시 /evaluate(디바운스) | `sliders`, `options` |
| (5) NPV·IRR·손익분기 인포그래픽 | `finance.js`: 현금흐름 → NPV·IRR(이분법)·손익분기, ECharts line + markLine(PoC 동작 확인) | 동일 | `assumptions`, `kpi` |
| 추가: 대안 탐색 | `explore.js`: PCP·레이더+표·산점도 행렬 | 동일 | `scenarios[].obj`, 비교 18건 |

### 4-4. 권고 일정(마감 대응)
1. 이틀: 안A MVP — 옵션 2개(규제 적용안 v1, 규제 미적용 깔끔안 v1; 기존 work/ 산출물)로 3D + 링 + NPV까지.
2. 이후: Pareto 탐색 3뷰, assumptions 정리(T등급 열), 대리모델 오차 표.
3. gjplan 결과가 나오면 옵션을 A–E로 교체하고 `export_scenarios.py` 재실행.
4. 안B는 심사에서 "실시간 생성"을 요구할 때만, 프런트를 그대로 두고 서버만 추가.

---

## 5. 프로젝트 규칙과의 정합·함정
- CLAUDE.md §3.4: 슬라이더는 buildable·height_max 안에서만 움직인다(clamp). 페널티로 처리하지 않는다.
- CLAUDE.md §3.2·§10 "proxy_for 미기록": 에너지·공실 프록시 값에는 `proxy_for` 필드를 둔다.
- CLAUDE.md §5.6: 방문객·체류와 거주·생활업종·야간활동을 두 축으로 나란히 보이는 KPI 링 구성.
- 라이선스: ladybug·honeybee·pandana는 AGPL-3.0이므로 코드를 수정해 네트워크로 서비스하는 구성(안B 확장)이면 조건을 검토. 로컬 사용·단일 HTML 배포에는 해당 코드를 넣지 않는다. 법률 자문 아님 [추정].
- 데이터 반출: ShapeDiver·Speckle은 모델이 외부 서버에 올라간다(리전 EU/북미/아시아, UK). 공모 대응 자료가 외부 반출 제한 대상인지 확인 필요 [미확인].

---

## 6. 산출물 위치(스크래치패드, 세션 한정)
- `…\scratchpad\poc\dist\index.html` — 단일 HTML PoC(1.29 MB), `poc\src\main.js` 소스, `poc\src\plan.json`(plan_clean/gis 사본, 좌표 원점 이동·0.1 m 반올림)
- `…\scratchpad\sur\` — LightGBM 학습·JSON 내보내기·JS 추론, FastAPI PoC와 벤치마크
- `…\scratchpad\ft.py`, `gh.py`, `jsd.py`, `cr.py` — 웹 원문 추출·GitHub·jsDelivr·CrossRef 조회 보조 스크립트

---

## 7. 직접 열어본 주요 출처 (URL은 실제 접근한 것만)
- ShapeDiver: https://www.shapediver.com/pricing/ , https://www.shapediver.com/blog/what-we-got-wrong-about-shapediver-s-free-planand-how-we-fixed-it , https://faq.shapediver.com/faq/plans-pricing , https://help.shapediver.com/doc/upgrade-to-a-paid-subscription
- Speckle: https://speckle.systems/pricing/ , https://docs.speckle.systems/workspaces/new-plans-faq , https://raw.githubusercontent.com/specklesystems/speckle-server/main/LICENSE , https://docs.speckle.systems/developers/viewer/introduction
- Rhino.Compute: https://developer.rhino3d.com/en/guides/compute/compute-faq/ , https://developer.rhino3d.com/guides/compute/core-hour-billing/ , https://github.com/mcneel/compute.rhino3d.appserver , https://discourse.mcneel.com/t/computing-grasshopper-is-ultra-slow-when-errors-are-present/194886
- Pollination·Ladybug: https://www.pollination.solutions/pricing , https://docs.pollination.solutions/user-manual/getting-started/buying-pollination-products.md , https://discourse.ladybug.tools/t/speed-up-the-process/40072
- Design Explorer: https://github.com/tt-acm/DesignExplorer , https://design-explorer.epfl.ch
- F4R: https://www.food4rhino.com/en/app/wallacei , /octopus , /human-ui ; https://www.wallacei.com/
- pymoo: https://pymoo.org/visualization/index.html (+ pcp, petal, radar, radviz, heatmap, star, scatter), https://pymoo.org/mcdm/index.html
- 시각화 연구: https://dis.ijs.si/tea/Publications/GECCO2020Tutorial.pdf , https://arxiv.org/abs/1903.01768 , https://doi.org/10.1007/s00291-012-0297-0 (Miettinen), https://doi.org/10.1057/ivs.2008.13 (Li 외), https://doi.org/10.1016/j.enbuild.2019.01.048 (Waibel 외), https://doi.org/10.3390/buildings12091473 (Showkatbakhsh & Makki)
- 실시간·대리모델: https://blogs.autodesk.com/forma/2023/06/06/formas-rapid-wind-analysis-offers-instant-insights-into-wind-conditions/ , https://blogs.autodesk.com/forma/2023/07/03/game-changing-rapid-noise-analysis-comes-to-forma-2/ , https://arxiv.org/abs/2211.12035 , https://research.polyu.edu.hk/en/publications/evaluating-a-deep-learning-based-surrogate-model-for-predicting-w/ , https://doc.arcgis.com/en/cityengine/latest/cga/cga-report.htm , https://www.testfit.io/pricing , https://github.com/UDST/pandana , https://github.com/gkjohnson/three-mesh-bvh
- 기타: https://cesium.com/platform/cesium-ion/pricing/ , https://unity.com/products/compare-plans , https://docs.marimo.io/guides/exporting/webassembly_html/ , https://panel.holoviz.org/how_to/wasm/convert.html , GitHub API·npm registry·jsDelivr data API(버전·라이선스·크기)

## 8. 미확인·미해결 목록
- ShapeDiver Free 플랜의 2026-10 존속 여부, 연산 지연의 실측.
- Wallacei·Octopus·Human UI의 Rhino 8 호환.
- Design Explorer의 로컬(file:// 또는 로컬 서버) 구동과 최신 브라우저 호환(미테스트).
- Unreal Engine 1차 라이선스 문서(403), pydeck 오프라인 export, ArcGIS Urban 현재 상태, VIDEO(Kollat & Reed) 원문, Kastner & Dogan 정확도 수치, Forma 상세 풍 분석 소요시간의 1차 출처, CityFinder 제품 실체.
- 조망(지평선각 캐시) 방식의 문헌 근거, 산점도 행렬의 ECharts 구현(다중 grid)은 설계 제안 단계.
- 설계서 Part5의 평가 시간(mid 0.3 s 등)은 설계 목표치로 실측 아님. gjplan S1–S4 실제 생성 지연은 미측정.
- 사용 가능한 WebSearch 한도(200/200)가 소진되어 이후 검색을 중단했다. 추가 검색이 필요하면 CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION 상향이 필요하다.
- 사용자 이메일을 외부 요청(User-Agent·mailto·쿼리스트링)에 넣은 건수: 0건. 참고로 CrossRef 서지 조회 4건의 User-Agent에 사용자와 무관한 자리표시 문자열(`mailto:research@example.com`)을 넣었고, 이후 일반 UA("Mozilla/5.0")로 교체했다.
