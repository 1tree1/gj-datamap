# 07. 선례 조사 — Foster + Partners: 데이터·시뮬레이션이 도시설계 결정을 바꾼 경우

- 작성일 2026-10-24. 조사 대상: Foster + Partners(이하 F+P)가 관측 데이터 또는 시뮬레이션을 근거로 도시설계 결정을 내렸거나 바꿨다고 주장되는 선례 — World Squares for All/Trafalgar Square(1996–2003), King's Cross Railway Lands(1987–), Masdar City(2006–), South Sabah Al-Ahmad City(쿠웨이트, 2020년대), Duisburg Inner Harbour(1991–), Specialist Modelling Group(SMG)·Applied R+D(ARD) 방법, 홍콩(West Kowloon, 2011).
- 목적: 「도시설계를 데이터로 최적화한다」는 말이 모호하다는 사용자 지적에 대해, 실제 사무소 선례에서 **어떤 질문에 어떤 데이터를 모아 어떤 도구로 분석했고, 그 결과 어느 결정이 어떻게 바뀌었으며, 사후에 검증되었는지**를 사례마다 여섯 칸으로 고정해 적습니다. 그리고 「데이터가 실제로 결정을 바꾼 증거」와 「과장된 부분」을 사례마다 분리합니다.
- 등급 표기(공통 규칙): [T1] 법정·공식문서 / [T2] 공공발간·기관 보고서·업체 공식 사례집 / [T3] 학술 / [T4] 언론·블로그·2차 / [산정] / [가정] / 「확인 대기」. 업체(F+P·Space Syntax·Transsolar·Atkins·Oasys·Esri) 공식 문서는 규칙대로 [T2]로 적되, 자사 성과 주장은 **[T2, 업체 자체 주장]**으로 구분합니다. CLAUDE.md §3.1 기준(업체=T4)으로 읽을 때는 그 항목을 한 등급 내려 읽으면 됩니다.
- 접근 제한 기록: `fosterandpartners.com`(모든 프로젝트·뉴스 페이지), `world-architects.com`, `designweek.co.uk`, `architectmagazine.com`, UCL Bartlett 행사 페이지, Wiley(`onlinelibrary.wiley.com`), `web.archive.org`는 자동 수집에 403/차단으로 응답했습니다. 이들 페이지의 문구는 **검색 엔진 요약을 경유해서만** 확인했고 「원문 미확인」을 붙였습니다. PDF 6건(Foster 1997 개회연설, Penn & Turner 2001, Abid et al. 2014, Goncharova & Perkova 2022, Stonor & Rosenberg 1999 초록, Marshalls 사례집)은 원문 전문을 추출해 읽었습니다. 웹 검색 한도 소진으로 마지막 2건(AD 2013 권호, Hillier 1998 서지)은 미확인입니다.
- 모든 URL의 확인일은 2026-10-24입니다.

---

## 0. 요약

1. **Trafalgar Square(World Squares for All, 1996–2003)가 유일하게 「데이터 → 결정 변경 → 사후 측정」 세 단계가 모두 문서로 남은 선례입니다.** 306개 지점 보행량 계수·1만 명 궤적 추적·정적 활동 지도·무단횡단 기록·지하철 출구 10분 추적 [T3]을 Space Syntax 축선·가시영역 모델과 대조해 모델이 관측 패턴의 약 3/4을 설명함을 확인하고 [T3], 약 100개 안을 시험해 8유형 → 4개념안으로 압축한 뒤 [T3], 북측 도로 폐쇄·중앙 대계단·Charles I 섬 타원 교차로(원안 폐기)를 결정했습니다 [T2·T3]. 차량 처리량은 모델(SATURN·TRANSYT·VISSIM)로 약 40% 감소를 사전에 수용했습니다 [T2]. 사후 수치는 보행량 13배 [T2, 업체 자체 주장] vs 보행활동 +250%·통과동선 이용 +900% [T2, 영국 교통부 사례집 경유]로 **서로 맞지 않으며**, 둘 다 기준선·측정법이 공개되지 않았습니다.
2. **Masdar City(2006–)는 환경 시뮬레이션이 가로 폭·길이·향·포디움·풍탑을 정한 사례로 홍보되지만, 2010년 마스터플랜 재검토에서 포디움·PRT를 파일럿 구역으로 한정한 결정은 비용 때문이었고 [T2], 외부 공간 온도 저감 주장은 5–10°C, 15°C, 20°F(MRT), 20°C로 출처마다 다르고 비교 기준(사막/도심, 공기온도/복사온도)이 바뀝니다** [T2·T4]. 제3자 현장 계측 논문은 찾지 못했고, 유일한 학술 검증(2D CFD)은 정오 협곡 약 35°C와 오염물·습기 정체를 보고합니다 [T3].
3. **South Sabah Al-Ahmad City(쿠웨이트)는 F+P의 최근 데이터 기반 마스터플랜 방법(ArcGIS CityEngine 가로망·「도시 라이브러리」, Oasys MassMotion 근접 분석)을 가장 구체적으로 보여 주지만**, 결정 변경(보도 폭 ≥3 m 차양 확장 → 근접시간 −50%)은 업체 사례집의 자체 보고이고 최종 반영 여부와 사후 검증이 없습니다 [T2, 업체 자체 주장].
4. **Duisburg Inner Harbour(1991–)는 데이터·시뮬레이션이 결정을 바꾼 근거가 전혀 발견되지 않았습니다.** 유연한 프레임워크·공공 기반시설·산책로 선행이라는 단계 전략 선례로만 유효합니다 [T2 원문 미확인·T4].
5. **King's Cross(1987–)는 Foster 본인이 1997년에 「축선 분석이 경쟁안과 전혀 다른 배치를 낳았고 개발사가 남측 상업 잔여지를 포기하도록 설득했다」고 진술한 가장 직접적인 1차 증언**이지만 [T3], 그 안은 실현되지 않았습니다.
6. 구경주역에 주는 교훈은 §4에 정리했습니다. 핵심은 (a) 모델보다 **현장 관측(게이트 카운트·추적·정적 활동)이 먼저**이고 모델은 관측과의 상관으로 보정·설득에 쓴다, (b) 결정 주체(설계/교통공학/정치)를 추적표에 적는다, (c) 사후 성과를 주장하려면 **착공 전 기준선과 측정법을 공표**한다, (d) 환경 지표는 **지표 종류·비교 기준·측정 시각**을 고정하지 않으면 Masdar처럼 숫자가 흩어진다, (e) 비가역 요소는 파일럿 구역으로 한정한다 — 는 다섯 가지입니다.

---

## 1. 조사 방법과 판정 기준

### 1.1 「데이터가 결정을 바꿨다」의 인정 조건

세 가지가 모두 문서로 확인될 때만 「증거 있음」으로 적습니다.

| 조건 | 내용 |
|---|---|
| (a) 선후 | 데이터 수집·분석 시점이 결정보다 앞선다는 기록 |
| (b) 반사실 | 데이터가 없었다면 나왔을 결정(원안·경쟁안·관행)과 다른 결정이 문서에 있다 |
| (c) 진술 | 결정 주체의 진술 또는 제3자(학술·공공) 기록 |

하나라도 빠지면 「부분 증거」, 전부 업체 자체 자료이면 「업체 자체 주장」으로 적습니다.

### 1.2 여섯 칸의 정의

사례마다 「설계 질문 → 수집 데이터 → 분석 방법·도구 → 바뀐 설계 결정 → 결과·검증 여부 → 구경주역에 주는 교훈」을 고정 순서로 적습니다. 가독성을 위해 여섯 칸을 세로 표(항목 | 내용)로 놓았고, 각 표 뒤에 「증거 vs 과장」 표를 붙였습니다.

---

## 2. 사례별 여섯 칸 정리

### 2.1 World Squares for All — Trafalgar Square(런던, 1996–2003) — 증거 등급 최상

| 항목 | 내용 |
|---|---|
| **설계 질문** | Trafalgar Square–Whitehall–Parliament Square 일대(지정 건축물 170건, 그중 약 30%가 Grade I [T3, Foster 1997 개회연설])에서 차량이 지배하는 공간을 보행자에게 되돌리되, 모든 접근 도로의 차량 연결은 유지해야 한다는 조건. 두 광장을 Whitehall로 연결하는 것이 핵심 과제 [T3, Goncharova & Perkova 2022]. 1996년 공모 인터뷰에서 F+P는 「디자인이 아니라 접근 방법(기존 보행·교통 흐름의 정밀 분석)」을 제시해 선정됨 [T3, 같은 글]. Space Syntax의 초기 보행 분석이 공모안을 뒷받침했다는 것은 업체 기록 [T2, Space Syntax 프로젝트 페이지, 업체 자체 주장]. |
| **수집 데이터** | ① 보행량 게이트 카운트 **300개 이상 지점**, 시간대·요일·계절 변화 [T3, Hillier·Stonor·Major·Spende 1998, 검색 요약 경유·원문 미확인]; Goncharova는 **306개 지점, 1만 명의 이동 궤적** 추적으로 기록 [T3]. ② 정적 활동 지도(여름 점심시간 체류자 분포; 정장 착용자=런던 거주자로 가정해 관광객과 구분) [T3, Foster 1997 Fig.11]. ③ 무단횡단 기록 — 신호·횡단보도가 없는 Charles I 교통섬으로 다수가 건너감 [T3, Foster 1997 Fig.12]. ④ 지하철 출구에서 나온 사람을 10분간 추적 — Whitehall 중간에서 포기하고 되돌아오는 패턴 [T3, Foster 1997; Goncharova]. ⑤ 교통량 모델 — Atkins가 인접 Strand 재정비로 보유한 최신 교통 모델 [T3, Goncharova]. ⑥ 공공 협의 — 2001년 2월 4일간 전시·설문, 약 1,600건 응답, 75% 지지 [T3, Goncharova]. |
| **분석 방법·도구** | ① 축선 분석(Axman) — 통합도로 가장 접근성 높은 경로 예측(적→청 색 척도) [T3, Goncharova]. ② 가시영역(isovist) 비교 — 광장 기하 중심에서의 시야 vs Charles I 섬에서의 시야; 섬이 「전체 파노라마 사진 촬영의 최적 지점」임을 확인 [T3, Foster 1997 Fig.13a·b; Goncharova Fig.4]. ③ 모델–관측 대조 — 다른 변수(용도·건물 높이·차량·밀도) 투입 전에 공간 구성만으로 관측 보행 패턴의 **약 3/4**을 설명 [T3, Goncharova, Hillier 1998 재인용]. 일반 Space Syntax 연구에서 구성 변수의 설명력은 50–80% [T3, Penn & Turner 2001]. ④ 안 시험 — **약 100개 변형안**을 시험(통합도가 약한 안 제외) → 8유형의 개선 가능성 → 장기 협의 후 **4개 개념안**으로 통합 [T3, Goncharova]. ⑤ 사후 예측 다이어그램 — 모서리 벽 제거 전후 축선 분석으로 대각 횡단 잠재력 변화를 예측 [T3, Foster 1997 Fig.19a·b, 20]. ⑥ 교통 — SATURN·TRANSYT·VISSIM으로 광범위 모델링 [T2, Karmaili & Earl 2004 ETC, SWOV 초록 경유]; 접근로 핵심 지점 용량 삭감 + 버스 우선 + 신호주기 단축·보행 녹색 연장·전적색 보행 단계 [T2, Cotton(TfL), SWOV 초록 경유]. |
| **바뀐 설계 결정** | ① **북측 도로(National Gallery 전면) 폐쇄 → North Terrace 보행화**, 특별 방문객 임시 접근만 허용 — 교통 엔지니어의 결정으로 기록 [T3, Goncharova]; 프로젝트 목표로 명시 [T2, Marshalls 사례집]. ② **중앙 대계단** — 가장 이용이 적은 두 공간(광장 북측 하부·상부 테라스)을 직결, 북벽·난간 절단 반대를 넘어 **대각 하강이 가능한 폭**으로 결정 [T3, Goncharova]. Foster는 「벽을 제거한 것을 그림에서 거의 놓치지만 대각 횡단 잠재력이 극적으로 바뀐다, 예측이 보여 준다」고 진술 [T3, Foster 1997]. ③ **원안(광장 남측 확장·신규 횡단보도) 폐기 → Charles I 섬을 타원형 신호 교차로로 확대하고 그 중앙을 관통하는 횡단보도 설치** — Atkins 제안; Atkins 자체 회고는 「원 마스터플랜의 주교차로 처리 아이디어는 틀렸다(mistaken)」고 기록 [T2, AtkinsRéalis; T3, Goncharova]. ④ **차량 처리량 약 40% 감소를 수용** — 「중앙 런던에서 전례 없는」 수준 [T2, Cotton, SWOV 초록 경유]. ⑤ 조직 결정 — Foster가 「건축가가 아니라 도로 엔지니어가 앞에 서야 정치적으로 맞다」고 판단, Halcrow Fox 대신 Atkins 선정 [T3, Goncharova]. ⑥ 부수 — Edith Cavell 상 동측 차로 폐쇄, 동·서측 2차로 정리, 4모서리 횡단보도, 지체장애인 승강기·지하 화장실·카페(GLA 제안) [T3, Goncharova]. |
| **결과·검증 여부** | 마스터플랜 1998.08 공표, 1999 후속 컨설턴트 지정, 2002 인허가 완료, 예산 £25M, 1.5년 공사, **2003.07.02 개방** [T3, Goncharova; T2, AtkinsRéalis]. 사후 수치: (가) 보행량 **13배** — 기준선·기간·방법 미기재 [T2, Space Syntax 프로젝트 페이지, 업체 자체 주장; Goncharova도 Stonor 2013 발표를 재인용]. (나) 보행활동 **+250%**, 통과동선 이용 **+900%** — 영국 교통부 『Encouraging Walking and Cycling: Success Stories』 pp.20–21을 인용한 UCL REF 2014 영향 사례 [T2, 측정 기간·방법 미기재, 원문 미확인]. (다) 피크 시 약 7,000명/시 횡단, 대기·소음 약 −25%, Heritage Wardens 도입 후 범죄 약 −55% [T2, AtkinsRéalis, 자체 보고·기준 기간 없음]. (라) RIBA/English Heritage Building in Context Award 2004 [T3, Goncharova]. (마) Parliament Square 단계는 미실현 [T3]. (바) 2026년 학술 발표에 Trafalgar Square 포함 4개 영국 프로젝트의 장기 예측력 사후 검증이 예고됨 — 결과 미공개 [확인 대기]. |
| **구경주역에 주는 교훈** | ① **관측이 먼저, 모델은 보정·설득용.** 결정적 발견(남동 모서리 비둘기 먹이, Charles I 섬이 사진 촬영 최적점, Whitehall 중간 포기)은 모두 모델이 아니라 현장 관측에서 나왔고, 모델은 그 패턴의 3/4을 재현해 신뢰를 얻었습니다. 구경주역 S1·S2에서도 **경계 접점 게이트 카운트 + 정적 활동 지도 + 유입점(버스 정류장·대릉원/황리단길 방향) 10분 추적**을 먼저 하고, 그 뒤에 축선·세그먼트 모델(depthmapX·cityseer·momepy)과의 상관을 보고해야 합니다. ② **최약 지점이 축을 지배** — Whitehall 연결은 Charles I 섬 하나의 횡단으로 결정됐습니다. CLAUDE.md §5-8의 f₁ 정의(연속성 + 최약 지점 통과 폭)와 정확히 일치하며, 원화로 횡단점이 구경주역의 Charles I 섬입니다. ③ **결정 주체를 적는다.** 도로 폐쇄는 교통 엔지니어가, 교차로 형태는 Atkins가, 승강기·카페는 GLA가 결정했습니다. 추적표(CLAUDE.md §3.5)에 「누가 결정했는가(설계/교통공학/정치/협의)」 열을 두어야 「모델이 그렸다」는 오해를 피할 수 있습니다. ④ **기준선 없는 성과는 숫자가 흩어진다** — 13배와 250%의 불일치가 그 결과입니다. 착공 전 보행량·업종·야간활동 기준선과 측정법(지점·시각·계절)을 공표해야 합니다(CLAUDE.md §5-6·7). ⑤ **100개 안 → 4개 개념안 → 1,600건 협의**라는 숫자를 그대로 쓸 수 있습니다. 우리 파레토 전선(대안 A–E)도 「시험한 안의 수, 걸러낸 기준, 협의 응답 수·지지율」을 함께 적어야 합니다. |

**증거 vs 과장(Trafalgar Square)**

| 구분 | 내용 | 등급 |
|---|---|---|
| 증거 — 선후 | 1996–98 관측·분석 → 1998.08 마스터플랜 → 2001 협의 → 2003 준공. Foster 1997 연설이 관측 사진·축선도·예측도를 결정 이전 시점에 제시 | [T3] |
| 증거 — 반사실 | 남측 확장 원안이 폐기되고 타원 교차로로 바뀐 기록; 북벽 절단 반대를 「대각 횡단 잠재력」 예측으로 넘김 | [T2·T3] |
| 증거 — 진술 | Foster: 「이 연구들이 설계 결정에 영향을 준 귀중한 재료였다」; de Grey(담당 파트너): 「이 방법 없이는 그렇게 급진적인 변화를 합의할 수 없었다」 | [T3] |
| 과장 | 「보행량 13배」 — 기준선·방법 없음, 공공 출처는 +250% | [T2, 업체 자체 주장] |
| 과장 | 「당시 가장 진보한 보행 모델」 — 업체 자체 평가 | [T2, 업체 자체 주장] |
| 과장 | Space Syntax가 「결정했다」는 서술 — 실제 도로 폐쇄·교차로는 교통공학·정치 결정, 모델은 공간 구성만 다룸(어트랙터·용도·교통 미포함) | [T3] |
| 한계 | 전체 마스터플랜 3단계 중 Parliament Square 미실현; 범죄·대기 수치는 Atkins 자체 보고 | [T2·T3] |

### 2.2 King's Cross Railway Lands(런던, 1987–, 미실현) — 설득 도구로서의 분석

| 항목 | 내용 |
|---|---|
| **설계 질문** | 운하·가스탱크·산업 폐허에 갇힌 52 ha 철도 부지를 혼합 커뮤니티로 되살리는 개발사 공모(F+P는 우승 컨소시엄 소속) [T3, Foster 1997]. |
| **수집 데이터** | 런던 전역 축선도(Hillier)에서 부지가 「black hole」(통합도 최저)로 기록됨; F+P의 런던 녹지 지도 [T3, Foster 1997 Fig.3·4]. |
| **분석 방법·도구** | 축선 분석 통합도; 설계안 단계별 축선 재분석(「tests showed the connections were becoming much better」) [T3, Foster 1997 Fig.6·7]. |
| **바뀐 설계 결정** | 경쟁안들이 모두 「부유한 남측」 상업 집중으로 간 반면, F+P는 북측에 새 녹지 중심(「address」)을 두는 안으로 「경쟁안과 근본적으로 다른」 안을 제출. Hillier가 그 녹지가 「거대한 교통섬 같은 닫힌 체계」임을 지적 → 북측으로 통하는 도로(「Hillier's Way」) 신설, 녹지 주변 차량 제거. 분석이 **개발사를 설득해 남측 상업 잔여지에 대한 집착을 버리게** 함 [T3, Foster 1997]. |
| **결과·검증 여부** | 1987–92 안은 실현되지 않음(이후 다른 팀의 안으로 2000년대 개발; 경위 원문은 확인 대기). 사후 검증 불가. Foster는 이 프로젝트를 「Space Syntax 이론이 학계를 떠나 실제 적용될 수 있음을 보인 초기 사례」로 평가(D. Rosenberg 인용) [T3, Foster 1997]. |
| **구경주역에 주는 교훈** | 분석의 첫 효용은 **발주처 설득**입니다 — 「왜 남측(원화로변)에만 상업을 몰지 않는가」를 통합도 지도로 보일 수 있습니다. 경주시·국가철도공단(2026.01 MOU) 설득 자료로 쓸 때, 「설득 성공 ≠ 실현」(King's Cross는 미실현)을 추적표에 함께 적어야 합니다. 또 「닫힌 녹지 = 거대한 교통섬」 진단은 구경주역 근린공원 배치 검토에 그대로 적용됩니다 — 공원이 축을 끊으면 f₁이 떨어집니다. |

**증거 vs 과장(King's Cross)**: 증거는 결정 주체(Foster)의 1차 진술 하나 [T3]이며 제3자 기록이 없습니다. 과장이라기보다 **미실현**이라는 한계가 큽니다.

### 2.3 Masdar City 마스터플랜(아부다비, 2006–) — 환경 시뮬레이션과 가로 형태

| 항목 | 내용 |
|---|---|
| **설계 질문** | 사막 기후에서 차 없는 보행 도시의 외부 공간이 쾌적할 수 있는가; 에너지 수요를 UAE 표준 대비 약 80% 줄이고(「아부다비 대비 20%만 소비」) 현장 재생에너지로 공급할 수 있는가 [T2, Transsolar 프로젝트 페이지]. 발표 당시 「zero-carbon, zero-waste」, 6 km²(Transsolar는 640 ha), 약 220억 달러, 거주 4.5–5만 명·사업체 1,500·통근 4–6만 [T4, Wikipedia; T2, Transsolar]. 발주 Abu Dhabi Future Energy Company; 건축 F+P; 기후공학 Transsolar; 설비 WSP; 재생에너지 E.T.A.; 교통 Systematica [T2, Transsolar]. Abid et al.은 환경 컨설턴트로 Mott MacDonald를 기재 [T3]. |
| **수집 데이터** | ① 전통 아랍 도시 형태 참조(좁은 가로, 중정, 풍탑, 두꺼운 벽) — 「전기 이전 정주지의 수동적 환경 조절을 연구」(Evenden, F+P) [T4, ICON 2011; T4, arch2o]. ② 현지 풍속 3–8 m/s(Masdar 풍력 평가) [T3, Abid et al. 2014가 Janajreh & Talab 2010 인용]. ③ **사후** 열화상 — 2010.10.01 정오, Masdar Institute 외부공간 vs 아부다비 도심 가로 [T4, Architectural Record 2011]. ④ **사후** 현장 측정(방법·지표·시점 미기재) [T2, Transsolar, 업체 자체 주장]. |
| **분석 방법·도구** | ① Transsolar: 「엄밀한 수학적 모델링, 전산 시뮬레이션, 실물 모형 시험」 [T2, Transsolar]. ② World-Architects 프로젝트 문안(독어): **등온 유동 모델로 가로 폭·길이를 결정**, 가로 전체의 간이 모델로 PV 지붕 발열이 가로에 미치는 영향 검토, 재해석 풍탑 [T2, 업체 문안, 검색 요약 경유 — 원문 403, 미확인]. ③ 「심층 환경 분석 — 일사 연구, 풍동 시험, 에너지 시뮬레이션」 [T4, Architectural Record 2011]. ④ 제3자 검증: 2D 단면 CFD(ANSYS Fluent, k-ε, 정상상태, 풍속 3·8 m/s, 아침·정오·저녁 일사) [T3, Abid·Kolo·Janajreh 2014, AFMC]. |
| **바뀐 설계 결정** | (설계 단계) 좁고 짧은 가로 — 건물 간 최소 약 3 m(10 ft) [T4, Arch Record], 가로 길이 ≤70 m [T4, Wikipedia]; 가로축 방향 — **북동–남서** [T4, Wikipedia·arch2o] vs **남동–북서** [T2, Masdar 2021 공식 뉴스룸] — **출처 간 상충**; 전체를 **7.5 m 포디움** 위에 올리고 하부에 서비스·PRT 지하층 [T2, Masdar 2010 보도자료; Arch Record는 약 25 ft]; **45 m 풍탑**(Arch Record는 150 ft 강재, 가동 루버·상부 미스트) [T4]; 가로가 꺾여 방향을 바꾸는 배치(기류 가속) [T4, Arch Record]. (2010 재검토) **PRT를 Masdar Institute 내 파일럿으로 한정**(지하층 비용), **7.5 m 포디움·서비스 트렌치도 Institute로 한정**, 단계적 개발 확정, 1단계 100만 m² 2015년, 최종 2020–2025년, 외부 재생에너지 구매 허용, 지열·태양열 냉방 탐색 [T2, Masdar 보도자료 2010.10.11]. 예산 15% 삭감, 자체 전력망 포기·국가망 연결 [T4, Arch Record 2011]. → **가장 큰 결정 변경은 시뮬레이션이 아니라 비용·기술 재평가에서 왔습니다.** |
| **결과·검증 여부** | Masdar Institute 6개 건물 2010.09 입주 [T2]. 전기 −51%·식수 −54%(UAE 평균/표준 기준선 대비) — 설계 기준선 비교이며 계측 POE 논문 미발견 [T2, 업체 자체 주장; T4]. 외부 온도: 평균복사온도(MRT) **20°F(≈11 K) 낮음**(F+P 자체 열화상, 1일 1시점) [T4, Arch Record]; 「**최대 20°C** 쾌적 개선, 아부다비 도심 대비」(방법 없음) [T2, Transsolar 자체 주장]; 「사막 대비 **15°C**」(개발사 주장) [T4, Smithsonian·CityMonitor 2014]; 「**5–10°C**」 [T4, Wikipedia]; 「아부다비 다른 곳보다 몇 도」 [T2, Masdar 2021]. 제3자 2D CFD: 높은 H/W가 주간 일사를 차단해 아침·저녁 쾌적하나 **정오 협곡 약 35°C**, 협곡 바닥 바람 정체(0.57–2.68 m/s 상부), **내부 발생 오염물·습기 배출 곤란** [T3, Abid et al. 2014]. 규모: 2023년 거주·근무 15,000명(거주 5,000), 계획 면적의 1/6 미만 건설, 완공 시점 무기한 보류 [T4, AP 2023]; 「2018년 5만 명」 → 「2020년 3,500명」 [T4, PopSci]. 학술 비평: 경제 논리가 토대이고 사회·환경은 표층(Cugurullo 2013, J. Urban Technology 20(1)) [T3]; 기술적 조정으로 현재와 닮은 미래를 만드는 실험(Günel 2019, Duke UP) [T3]. |
| **구경주역에 주는 교훈** | ① **환경 지표는 「지표 종류·비교 기준·측정 시각」을 고정**해야 합니다. Masdar의 숫자가 5–20°C로 흩어진 이유는 MRT/공기온도, 사막/도심, 정오 1회/연중이 섞였기 때문입니다. Forma 환경분석(02·05 원고)의 결과 보고 양식에 세 항목을 필수 열로 넣어야 합니다. ② **깊은 협곡은 경주에 없다.** 고도지구 20 m·15 m(06 원고 §1-1·2)로 H/W가 낮으므로 Masdar형 자기 차양은 성립하지 않고, 그늘은 수목·캐노피(§2.4 쿠웨이트 결론과 일치)로 만들어야 합니다. 반대로 환기·오염 정체 문제는 작습니다 — 이 점은 Abid 2014를 근거로 적을 수 있습니다. ③ **가로 향은 조망축과 상충**할 수 있습니다. Masdar는 바람·일사로 향을 정했지만 경주는 향일문 조망로·고분 스카이라인(05 원고 §7.3)이 제약입니다. 향은 단일 해가 아니라 목적함수 중 하나로 두고 파레토에 맡겨야 합니다. ④ **비가역 요소는 파일럿으로 한정** — 2010년 포디움·PRT 결정은 CLAUDE.md §5-3(비가역 투자는 뒤로)의 실물 사례입니다. 구경주역의 지하주차·대형 문화시설이 이에 해당합니다. ⑤ 「−51%·−54%」처럼 **설계 기준선 대비 수치를 성과로 쓰지 않습니다.** 계측값만 성과입니다. |

**증거 vs 과장(Masdar)**

| 구분 | 내용 | 등급 |
|---|---|---|
| 증거 — 부분 | 시뮬레이션·풍동·모형 시험이 설계 과정에 있었다는 진술은 다수(Transsolar, Arch Record, World-Architects 문안) | [T2·T4] |
| 증거 — 부족 | 「어느 시뮬레이션 결과로 가로 폭이 몇 m에서 몇 m로 바뀌었다」는 반사실 기록은 어느 출처에도 없음(World-Architects 문안이 가장 근접하나 원문 미확인) | 확인 대기 |
| 증거 — 결정 변경 | 2010 재검토의 PRT·포디움 축소는 문서화된 결정 변경이지만 근거는 비용 | [T2] |
| 과장 | 「15–20°C 시원」 — 개발사·업체 주장, 비교 기준 불일치, 제3자 계측 없음 | [T2 업체 자체 주장·T4] |
| 과장 | 「zero-carbon」 — 외부 재생에너지 구매·국가망 연결로 사실상 철회 | [T2·T4] |
| 과장 | 「−51%·−54%」 — 설계 기준선 비교, 계측 POE 미발견 | [T2 업체 자체 주장] |
| 반증 | 2D CFD: 정오 35°C, 오염물·습기 정체 | [T3] |
| 규모 | 5만 명 목표 → 거주 5천 명(2023) | [T4] |

### 2.4 South Sabah Al-Ahmad City(쿠웨이트, 2020년대) — CityEngine·MassMotion

| 항목 | 내용 |
|---|---|
| **설계 질문** | 쿠웨이트시 남쪽 약 80 km, 61.5 km²(6,150 ha), 약 28만 명·14.5만 일자리의 신도시; CBD 둘레에 근린 클러스터 10개; **모든 주민이 녹지 400 m 이내**; 사막 기후에서 보행 가능한 가로와 그늘; (2020년 시점) 사회적 거리두기 상황의 공공공간 수용력 [T2, Oasys 사례집; T2, F+P 뉴스 2023.08.21 검색 요약 경유·원문 미확인]. |
| **수집 데이터** | ① 발주처 제공 근린별 인구 데이터 [T2, Oasys]. ② 「**도시 라이브러리(library of cities)**」 — 다른 도시들의 가로망·사업체 위치·밀도를 모아 교통·보행성·일자리 군집 패턴 비교 [T2, Esri UC 2023 영상 설명·F+P 뉴스, 검색 요약 경유]. ③ 교통공학 입력(설계자와 교통 엔지니어 공동 작업) [T2, Esri]. |
| **분석 방법·도구** | ① **ArcGIS CityEngine** — 근린을 연결하는 가로망 생성; 단순 가로망에 알고리즘을 돌려 **공간 위계**(「신체의 동맥」 비유)를 드러내고, 그 위에 사업체 위치를 대조해 주요 경로 주변 군집 확인; 프로젝트에 맞는 밀도를 고르면 건물 유형(topology)을 확대해 볼 수 있는 구조 [T2, F+P 뉴스, 검색 요약 경유]. 발표자 Bruno Moser(도시설계 총괄)·Mateo Neira(데이터 과학자), Esri User Conference 2023.07 샌디에이고 [T2]. ② **Oasys MassMotion** 보행 시뮬레이션 — 「근접 분석(proximity analysis)」: 사람 간 2 m 이내 체류 시간을 지표로 거주 밀도 vs 공공 오픈스페이스 검증, 여러 시나리오의 장단점 비교 [T2, Oasys, Narvaez Zertuche & Neira 인용]. |
| **바뀐 설계 결정** | 시나리오 1 — 차양 캐노피를 주요 공공공간(놀이터·소공원)에만 설치 → 거리두기 유지 상태에서 **최대 수용에 도달**. 시나리오 2 — **보행 가능 폭 ≥3 m의 보도까지 차양 확장** → 근접 체류 시간 **기준안 대비 −50%** 예측. 결론: 주요 공공공간뿐 아니라 보도를 덮는 방향으로 「이전 설계를 재검토 중」 [T2, Oasys, 업체 자체 주장]. 최종 마스터플랜에 반영됐는지는 **미확인**. |
| **결과·검증 여부** | 미건설. 기반시설 공사 착수(KACC) 보고가 있으나 날짜 미확인 [T4, ICE]. 독립 평가·사후 측정 없음. 모든 수치가 업체 사례집 자체 보고 [T2, 업체 자체 주장]. 「400 m 녹지 접근」은 목표이지 결과가 아님. |
| **구경주역에 주는 교훈** | ① **「도시 라이브러리」는 우리 비교 대상 18개(CLAUDE.md §2)와 S2 조직 지표(03 원고)의 결합**과 같은 발상입니다. 다만 F+P는 라이브러리의 구성 도시·지표를 공개하지 않았으므로, 우리는 사례 코딩(E 코퍼스 `coding.csv`)에 **가로망 지표·사업체 분포·밀도**를 열로 넣어 공개해야 설득력이 생깁니다. ② **단일 지표 시나리오 비교(−50%)는 설득력이 크지만 검증이 없습니다.** 우리는 한 지표가 아니라 파레토 전선 전체와 평가 횟수·대리모델 오차를 함께 내야 합니다(CLAUDE.md §4·§8). ③ **차양은 공공공간이 아니라 「이동 경로(보도)」에 — 폭 3 m 이상.** 고도제한으로 건물 그늘이 짧은 경주 가로에 수목·캐노피를 둘 때 적용 가능한 구체 수치입니다 [T2 업체 자체 주장이므로 설계 파라미터 후보로만]. ④ 「400 m 녹지 접근」 같은 규칙은 **목적함수가 아니라 제약(buildable 마스크)**으로 넣는 것이 CLAUDE.md §3.4와 맞습니다. ⑤ CityEngine의 절차적 생성 + 위계 분석 + 밀도→유형 열람 흐름은 gjplan의 규칙기반 생성 → 평가 → 3dm 내보내기 흐름과 같은 구조이므로, 발표용 비교 참조로 쓸 수 있습니다. |

**증거 vs 과장(South Sabah Al-Ahmad)**: 선후·반사실(시나리오 1→2)·진술(담당자 인용)이 모두 있지만 **전부 업체 자체 자료**이고 최종 반영·사후 검증이 없어 「업체 자체 주장」 등급입니다. 과장은 「최첨단 군중 시뮬레이션」류 수식어와, 미건설 도시에 대해 성과처럼 읽히는 서술입니다.

### 2.5 Duisburg Inner Harbour(독일, 1991–) — 데이터 근거 없음

| 항목 | 내용 |
|---|---|
| **설계 질문** | 세계 최대 내륙항의 폐항 구역 89 ha를 도심 생활과 연결하는 재생; IBA Emscher Park(1989–1999) 틀 안의 1991년 국제공모 [T4, Wikipedia; T4, Dwell]. 목표: 물을 도시로 되돌리고, 서비스 고용·주거·문화·여가를 결합하며 산업 상징을 유지 [T4, Wikipedia]. |
| **수집 데이터** | **발견되지 않음.** 어느 출처도 관측 데이터·시뮬레이션·정량 분석을 언급하지 않습니다. |
| **분석 방법·도구** | **발견되지 않음.** |
| **바뀐 설계 결정** | 데이터로 바뀐 결정 없음. 설계 원칙: 기존 항만 건물의 선별 재생 + 신축, **다양한 건축가가 시간을 두고 개별 요소를 개발할 수 있는 유연한 프레임워크**, **공공 기반시설과 가로수 산책로의 선행 조성** [T2, F+P 프로젝트 페이지, 검색 요약 경유·원문 미확인]. |
| **결과·검증 여부** | 실현: Hafenforum(F+P 창고 전환), Museum Küppersmühle(Herzog & de Meuron), Five Boats(Grimshaw), Eurogate(F+P, 2006–08), Landesarchiv NRW(Ortner & Ortner, 2007 위촉), 주거·식음 15개소 이상 [T4, Wikipedia]. 공공 기반시설 투자 약 €6,500만(EU 보조 일부) [T4, Dwell]; 1997년 시점 IBA 약 7,000만 달러 [T4, CSMonitor]. 고용·투자 총계 평가 자료 미발견 [확인 대기]. F+P는 2007년 Duisburg 도심 마스터플랜을 추가 수주(도심 인구 +25% 목표) [T4, e-architect]. |
| **구경주역에 주는 교훈** | 데이터 선례로는 **비해당**입니다. 대신 「프레임워크 + 공공 기반시설·산책로 선행 + 다수 건축가 단계 개발」은 CLAUDE.md §5-2(1단계는 연결·기반·보행)·§5-3(순서를 빌린다)의 유럽 선례로 쓸 수 있습니다. 조사 과제로 삼으려면 IBA Emscher Park 최종 보고서(Abschlussbericht)에서 고용·투자 수치를 받아야 합니다. |

### 2.6 Specialist Modelling Group(SMG)·Applied R+D(ARD)·Urban Design Group — 조직과 도구

| 항목 | 내용 |
|---|---|
| **설계 질문(조직의 목적)** | 프로젝트 주도형 연구개발(「project-driven research and development」): 복잡 기하·환경 분석·시뮬레이션·디지털 제작을 설계팀에 공급 [T3, Peters & De Kestelier 2006, Bridges]. |
| **수집 데이터** | SMG: 1997년 설립, 2006년까지 100개 이상 프로젝트 참여; 전문성 — 건축·수학·기하·**환경 분석·지리·프로그래밍·도시계획**·RP [T3, Bridges 2006]. Hugh Whitehead 주도(Swiss Re, GLA City Hall, Sage Gateshead, 베이징공항 자문) [T4, Architect Magazine, 검색 요약 경유]. SmartGeometry 2001년 Whitehead(F+P)·Parrish·Hesselgren 공동 설립 [T4]. 현재 SMG 책임 Irene Gallou(2006 입사): 환경 설계·건물 물리 시뮬레이션·**준공 후 성능 데이터 수집**, Masdar·Apple Park·Bloomberg [T4, 강연자 소개]. |
| **분석 방법·도구** | ARD(Martha Tsigkari, 파트너→Senior Partner): **자체 시뮬레이션 엔진**을 설계 앱 뒤에서 상시 구동 — 환경 성능·구조·CFD·조망 품질을 거의 실시간 평가; 물리 모형을 카메라로 읽어 디지털 모델에 반영하는 터치테이블, VR/AR; 파라메트릭·생성 설계, **유전 알고리즘 최적화**, 인지 컴퓨팅 [T4, Construction Management 2017]. 「분산 컴퓨팅으로 도시 규모의 최적해 공간 생성」, 「성능 기반 도시 배치」에 심층신경망·GA 적용 [T4, 강연자 소개]. Urban Design Group: Laura Narvaez Zertuche(UCL Space Syntax Lab 박사)가 2015년부터 보행·데이터 분석 리드 [T4, 강연자 소개]. CIBSE 발표자료에 사내 R&D 「Solar Irradiation Mapping」·「Pedestrian Wind Comfort(풍동 압력계수→열모델)」 기재 — 파일 10 MB 초과로 원문 미열람 [등급 미정, 확인 대기]. 출판: De Kestelier, 「Recent Developments at Foster+Partners' Specialist Modelling Group」, AD 83(2) *Computation Works*, 2013, pp.22–27 [T3, Dialnet 목차]; Aish·Davis·Tsigkari, 「Ex Silico Ad Vivo: Computational Simulation and Urban Design at Foster + Partners」, AD 2013, DOI 10.1002/ad.1626 — **권호·쪽수 확인 대기**(Computation Works 호 목차에는 없음) [T3]. |
| **바뀐 설계 결정** | 도시 규모에서 「어느 결정이 바뀌었다」는 공개 기록은 §2.1·2.3·2.4 사례 외에 없음. 건물 규모 사례(Mexico City 신공항 743,000 m² 스페이스프레임, 영국박물관 Great Court 지붕) [T4, CM 2017]은 범위 밖. |
| **결과·검증 여부** | 조직 역량의 외부 검증은 없음. 「준공 후 성능 데이터 수집」이 SMG 업무로 명시된 점은 긍정적이지만 공개된 도시 규모 POE는 발견되지 않음 [확인 대기]. |
| **구경주역에 주는 교훈** | ① F+P도 도시 규모 「최적화」를 **GA + 분산 컴퓨팅 + 자체 평가 엔진**으로 합니다 — CLAUDE.md §4(규칙기반 생성 + NSGA-III, CPU)와 방향이 같고, 차이는 평가 엔진의 속도입니다. 우리 병목이 평가 횟수(§8)라는 진단은 F+P의 「거의 실시간 피드백」 투자와 같은 문제 인식입니다 → 대리모델(LightGBM) 우선. ② **환경·구조·CFD·조망**이 F+P 엔진의 4개 평가축입니다. 우리 5개 목적함수에 조망(고분 스카이라인·향일문)이 이미 있고, 바람·일사는 Forma(02·05 원고)로 보완하는 구조가 대응됩니다. ③ 보행·데이터 분석을 **도시설계 그룹 안에 Space Syntax 출신이 상주**하는 구조는, 우리 f₁(접근성)을 외주 모델이 아니라 내부 지표로 유지해야 한다는 뜻입니다. |

### 2.7 홍콩·기타 — 확인 대기

- **West Kowloon Cultural District(홍콩, 2011)**: F+P 「City Park」안이 2011.03 선정, 40 ha, 23 ha 공원, 문화시설 17개, 1년 공공 협의, 2008년 시작된 최종 경쟁(OMA·Rocco Design·F+P), Arup 공동 [T4, F+P 뉴스 검색 요약·Arup]. **데이터·시뮬레이션이 결정을 바꿨다는 근거는 어느 출처에서도 발견되지 않았습니다.** 「Hong Kong 2030」 계획 연구와 F+P의 연결도 확인되지 않았습니다 → 확인 대기.
- **Bloomberg London(2017)**: Space Syntax가 부지 주변 이동 패턴 분석 수행 [T2, Space Syntax 브로슈어] — 건물 규모이므로 범위 밖.
- **Masdar Plaza(LAVA, 2009 공모 1등, Transsolar 기후 개념)**: 광장 체감온도 **32°C 이하** 목표, 차양으로 일사 약 10%로 제한, 바닥 냉방·마스트 송풍 [T2, LAVA 프로젝트 페이지] — F+P 안이 아니지만 **외부 공간 쾌적 목표를 체감온도 수치로 고정한 예**로 §4의 지표 고정 원칙에 참고.

---

## 3. 종합 비교

| 사례 | 데이터 종류 | 도구 | 결정 변경의 성격 | 선후·반사실·진술 | 사후 검증 | 과장 핵심 |
|---|---|---|---|---|---|---|
| Trafalgar Sq(1996–2003) | 보행 계수 306지점·궤적 1만·정적 활동·무단횡단·추적 [T3]; 교통 모델 [T2] | Axman 축선·isovist; SATURN·TRANSYT·VISSIM | 도로 폐쇄, 대계단, 원안 폐기→타원 교차로, 처리량 −40% 수용 | ○·○·○ | ○(수치 불일치) | 13배 vs 250% |
| King's Cross(1987–) | 런던 축선도 [T3] | 축선 분석 | 경쟁안과 다른 배치, 연결 도로 신설, 개발사 설득 | ○·○·○(1차 진술만) | ×(미실현) | — |
| Masdar(2006–) | 전통 형태 참조·풍속 [T3·T4]; 사후 열화상 [T4] | 유동 모델·풍동·에너지 시뮬레이션·2D CFD(제3자) | 가로 폭·길이·향·포디움·풍탑(설계); PRT·포디움 축소(비용) | ○·△·△ | △(자체 측정만) | 5–20°C, zero-carbon, −51/−54% |
| South Sabah Al-Ahmad | 발주처 인구·도시 라이브러리 [T2] | CityEngine·MassMotion | 보도 ≥3 m 차양 확장(재검토 중) | ○·○·○(업체만) | × | 미건설, 자체 보고 |
| Duisburg(1991–) | 없음 | 없음 | 없음 | ×·×·× | — | 데이터 선례 아님 |
| SMG/ARD | — | 자체 엔진(환경·구조·CFD·조망), GA | 도시 규모 공개 사례 없음 | — | × | 「실시간 최적화」 수식어 |

---

## 4. 구경주역에 주는 교훈 — 수집할 데이터·방법·절차

### 4.1 원칙 다섯 가지

1. **관측 → 모델 → 옵션 → 결정 → 기준선 → 사후 측정**의 순서를 지킵니다(Trafalgar). 모델이 관측의 몇 %를 설명하는지(Trafalgar 약 3/4, 일반 50–80% [T3])를 먼저 보고하고, 설명되지 않는 부분(어트랙터·조망점·행사)은 관측으로 채웁니다.
2. **결정 주체를 추적표에 적습니다.** 설계/교통공학/정치·협의 중 누가 결정했는지, 모델은 무엇을 예측했고 무엇을 못 했는지(Trafalgar: 공간 구성만, 교통·용도 미포함).
3. **성과를 말하려면 기준선과 측정법을 착공 전에 공표합니다.** 13배/250% 불일치는 기준선 부재의 결과입니다. CLAUDE.md §5-6(방문객·체류시간 / 거주·생활업종·야간활동 두 축)·§5-7(인접 필지 주 출입구 방향)을 기준선 항목으로 고정합니다.
4. **환경 지표는 「지표(공기온도/MRT/UTCI·PET)·비교 기준(사막/도심/현재 부지)·측정 시각(정오 1회/시간대별/계절)」을 고정**합니다(Masdar). Forma 환경분석 결과표에 세 열을 필수로 둡니다. 체감온도 상한을 수치로 두는 방식(Masdar Plaza 32°C [T2])을 참고합니다.
5. **비가역 요소는 파일럿 구역으로 한정**합니다(Masdar 2010 PRT·포디움). 구경주역의 지하주차(매장문화재 시굴 후 분기, 06 원고 §1-6)·대형 문화시설이 이에 해당합니다.

### 4.2 모아야 할 데이터(선례에서 직접 도출된 것만)

| 번호 | 데이터 | 선례 근거 | 구경주역 적용(스케일·키) | 비고 |
|---|---|---|---|---|
| D1 | **보행 게이트 카운트** — 부지 경계 접점(원화로 횡단점, 북측 도로, 황오·성동 골목 접점)·내부 통과선, 평일/주말 × 3시간대 × 2계절 | Trafalgar 306지점 [T3] | S1·S2; 지점 30–60개 [제안]; 좌표 EPSG:5187 | 현재 보유 자산에 없음(01 원고 자산표) |
| D2 | **정적 활동 지도** — 체류자 위치·행위·추정 거주/방문 구분 | Trafalgar Fig.11 [T3] | S1 + 인접 공원·정류장 | 사진 촬영 지점(고분·역사 조망) 특기 |
| D3 | **유입점 추적(10분)** — 시내버스 정류장(원화로)·대릉원/황리단길 방향 유입자 | Trafalgar 지하철 출구 추적 [T3] | S2 | 포기 지점 = 최약 지점 후보 |
| D4 | **무단횡단·위험 횡단 기록** — 원화로·북측 도로 | Trafalgar Charles I 섬 [T3] | S1 경계 | f₁ 최약 지점 통과 폭의 현황값 |
| D5 | **교통량·신호 현황·모델** — 원화로·북측 도로 ADT, 신호주기 | Trafalgar SATURN·TRANSYT·VISSIM [T2] | S2 | 06 원고 §1-17: 교통량 조사 미보유 → 경주시 교통량 조사 [T2] 확보 |
| D6 | **S2 가로망·건물 축선/세그먼트 모델** | Trafalgar Axman; King's Cross [T3] | S2 1 km(06 원고 §1-13 중심 재설정) | depthmapX·cityseer·momepy; D1과 상관 보고 |
| D7 | **기상(풍향·풍속·일사)** | Masdar 풍속 3–8 m/s [T3]; Transsolar 모델 [T2] | S3→S1 | 06 원고 §1-16 Forma 방향별 불가 모순 해결 선행 |
| D8 | **사례 라이브러리 지표** — 가로망 위계·사업체 분포·밀도 | SSA 「library of cities」 [T2] | 비교 대상 18개 + E 코퍼스 | 04 원고 밀도 공백(06 §1-7) 보완 |
| D9 | **협의 기록** — 응답 수·지지율·수정 내역 | Trafalgar 1,600건·75% [T3] | — | 추적표 열 |
| D10 | **사후 기준선** — D1·D2 + 업종·야간활동 + 인접 필지 출입구 방향 | Trafalgar 불일치 교훈 | S1·S2 | 착공 전 공표 |

### 4.3 절차(선례의 숫자를 빌린 것)

1. D1–D4 현장 관측(2계절) → D6 모델과 상관(R² 보고) → 모델이 못 설명하는 지점 목록.
2. 규칙기반 생성으로 **100개 내외 안** 평가(Trafalgar 100 → 8 → 4) → 제약(buildable) 위반 제거 → 파레토 전선 → 대안 A–E.
3. 각 대안의 f₁ **최약 지점 통과 폭**과 D5 교통 모델 결과(처리량 변화 %)를 같은 표에.
4. 협의(D9) → 결정 → **결정 주체·근거 데이터·모델 예측·실제 채택 여부**를 추적표 한 행으로.
5. 착공 전 D10 기준선 공표 → 준공 1·3·5년 재측정(같은 지점·시각·계절).

### 4.4 쓰지 말아야 할 문장

- 「Space Syntax 분석으로 보행량이 13배 증가했다」 — 기준선 없음, 공공 출처는 +250%.
- 「Masdar의 가로는 주변보다 15–20°C 시원하다」 — 개발사 주장, 지표·기준 불일치, 제3자 계측 없음.
- 「Masdar Institute는 에너지 51%·물 54%를 절감했다」 — 설계 기준선 비교.
- 「F+P는 Duisburg를 데이터로 설계했다」 — 근거 없음.
- 「CityEngine 분석으로 쿠웨이트 신도시의 보도 차양이 결정됐다」 — 재검토 중이라는 자체 보고만 있음.

---

## 5. 미해결 질문·확인 대기

1. World-Architects(독어) 문안 「등온 유동 모델로 가로 폭·길이 결정」의 원문·출처(Transsolar 제공 문안인지) — 사이트 403, 브라우저 직접 확인 필요.
2. Space Syntax 「13배」의 기준선·기간·방법; 영국 교통부 『Encouraging Walking and Cycling: Success Stories』 pp.20–21 원문(국가기록원 아카이브) — +250%/+900%의 측정법.
3. Hillier·Stonor·Major·Spende(1998) 원문(Urban Design Quarterly 68 추정) — 300+ 지점 계수 설계와 모델–관측 상관값. 웹 검색 한도 소진으로 서지 미확인.
4. Karmaili & Earl(2004, ETC) 전문 — SATURN/VISSIM 결과와 사후 교통량.
5. Masdar 제3자 현장 계측 논문 — Khalifa University 저장소 직접 검색 필요; Masdar Institute 계측 POE(−51/−54%의 계측 여부).
6. South Sabah Al-Ahmad — 보도 차양 최종 반영 여부, 건설 현황·일정, CityEngine 「위계 알고리즘」의 정체(중심성 종류), 「도시 라이브러리」 구성 도시.
7. 「Ex Silico Ad Vivo」(DOI 10.1002/ad.1626)의 AD 권호·쪽수·사례 내용; CIBSE 발표자료(10 MB 초과) 원문의 사내 R&D 도구 목록.
8. F+P 공식 사이트(Masdar·Duisburg·SSA·Trafalgar 페이지) 원문 — 전부 403. 브라우저로 직접 열어 인용문 확정 필요.
9. 홍콩 WKCD(2011) — 데이터·시뮬레이션 근거 미발견; 「Hong Kong 2030」과의 연결 미확인.
10. King's Cross 1987–92 안의 미실현 경위(원문).
11. Duisburg IBA Emscher Park 최종 보고서의 고용·투자 수치.
12. Masdar 가로축 방향 — 북동–남서 [T4] vs 남동–북서 [T2 Masdar 2021] 상충 해소.

---

## 6. 출처 목록(URL · 확인일 2026-10-24 · 등급)

**Trafalgar Square / World Squares for All**
- Foster, N. (1997). Opening Address. *Proceedings, 1st International Space Syntax Symposium*, UCL, Vol. III, pp. i–vi. PDF 전문 열람. https://www.spacesyntax.net/symposia-archive/SSS1/SpSx%201st%20Symposium%2097%20-2003%20pdf/1st%20Symposium%20Vol%20III%20pdf/Foster%20opening%20address%20300.pdf [T3]
- Stonor, T. & Rosenberg, D. (1999). Research into Practice: From Practice, Research. *2nd Int. Space Syntax Symposium*, Brasília. 초록만 열람. https://spacesyntax.net/symposia-archive/ss2abstracts/stonor.html [T3]
- Goncharova, N. A. & Perkova, M. V. (2022). Space Syntax Methodology in Trafalgar Square Reconstruction. *Architecton: Proceedings of Higher Education* 2(78). DOI 10.47055/1990-4126-2022-2(78)-1. PDF 전문 열람(러시아어). https://archvuz.ru/files/N78_1_Goncharova.pdf [T3]
- Penn, A. & Turner, A. (2001). Space Syntax Based Agent Simulation. UCL. PDF 전문 열람(구성 변수 설명력 50–80%). https://discovery.ucl.ac.uk/id/eprint/2027/1/penn.pdf [T3]
- Hillier, B., Stonor, T., Major, M. D., Spende, N. (1998). 「Space Syntax Laboratory – from research to design」(제목 추정). 검색 요약 경유, 원문 접속 실패(DNS). https://gisweb.massey.ac.nz/topic/Spatial_Syntax/wbrefs/Space%20Syntax%20Laboratory%20-%20from%20research%20to%20design.htm [T3, 원문 미확인]
- Space Syntax Ltd. Trafalgar Square 프로젝트 페이지. https://spacesyntax.com/project/trafalgar-square/ [T2, 업체 자체 주장]
- UCL REF 2014 Impact Case Study 「Space Syntax: improving national and international urban environments」(DfT 사례집 인용). https://impact.ref.ac.uk/casestudies/CaseStudy.aspx?Id=36904 [T2]
- Cotton, S. (TfL Street Management). World Squares for All: management of traffic on the approaches to Trafalgar Square. SWOV 초록 경유(원문 봇 차단). https://swov.nl/en/publicatie/world-squares-all-management-traffic-approaches-trafalgar-square [T2, 초록 경유]
- Karmaili, F. & Earl, T. (2004). The Pedestrianisation of Trafalgar Square. *European Transport Conference*, Strasbourg. SWOV 초록 경유. https://swov.nl/en/publicatie/pedestrianisation-trafalgar-square-how-do-we-deliver-sustainable-scheme-world-heritage [T2, 초록 경유]
- AtkinsRéalis. Happy Anniversary, Horatio: 20 years after redevelopment. https://www.atkinsrealis.com/en/engineering-better-future/beyond-engineering/happy-anniversary-horatio [T2, 업체 자체 주장]
- Marshalls. World Square, London 사례집(Stone Federation 게재). PDF 전문 열람. https://www.stonefed.org.uk/app/uploads/2021/02/world.pdf [T2, 업체]
- Foster + Partners. Transformation of Trafalgar Square. 403, 검색 요약 경유. https://www.fosterandpartners.com/news/transformation-of-trafalgar-square [T2, 원문 미확인]

**Masdar City**
- Transsolar. Masterplan Masdar City. https://transsolar.com/projects/abu-dhabi-masterplan-masdar-city [T2, 업체 자체 주장]
- Masdar. Press release, 2010-10-11: 마스터플랜 재검토 결론(Business Wire China 게재). https://www.businesswirechina.com/en/news/6639.html [T2]
- Masdar. 10 things you didn't know about Masdar City(2021-03-30). https://masdar.ae/en/news/newsroom/10-things-you-didnt-know-about-masdar-city [T2, 업체 자체 주장]
- Abid, N., Kolo, I., Janajreh, I. (2014). CFD Study on Wind, Solar Effect and Pollutant Dispersion in Masdar City. *19th Australasian Fluid Mechanics Conf.* PDF 전문 열람. https://people.eng.unimelb.edu.au/imarusic/proceedings/19/69.pdf [T3]
- Cugurullo, F. (2013). How to Build a Sandcastle. *Journal of Urban Technology* 20(1): 23–37. DOI 10.1080/10630732.2012.735105. https://ideas.repec.org/a/taf/cjutxx/v20y2013i1p23-37.html [T3]
- Günel, G. (2019). *Spaceship in the Desert*. Duke University Press. 서평 경유. https://merip.org/2019/12/speculating-on-climate-change-in-the-uae/ [T3, 서평 경유]
- Nambiar, S. (2011-05-16). Masdar Institute. *Architectural Record*. https://www.architecturalrecord.com/articles/7860-masdar-institute [T4]
- Murphy, D. (2011-03-28). Masdar Institute by Foster + Partners. *ICON*. https://www.iconeye.com/architecture/masdar-institute-by-foster-partners [T4]
- Dezeen (2010-11-24). Masdar Institute by Foster + Partners(F+P 공식 설명문 전재). https://www.dezeen.com/2010/11/24/masdar-institute-campus-by-foster-partners/ [T4, F+P 문안 전재]
- Speed, B. (2014-09-24). Whatever happened to Abu Dhabi's carbon-neutral city? *CityMonitor*. https://www.citymonitor.ai/analysis/whatever-happened-abu-dhabi-s-carbon-neutral-city-330/ [T4]
- AP (2023-12-08). On sidelines of COP28, Emirati 'green city' falls short of ambitions. https://www.wsls.com/business/2023/12/08/on-sidelines-of-cop28-emirati-green-city-falls-short-of-ambitions-but-still-delivers-lessons/ [T4]
- PopSci. Is Masdar City a ghost town or a green lab? https://www.popsci.com/masdar-city-ghost-town-or-green-lab/ [T4]
- Wikipedia. Masdar City. https://en.wikipedia.org/wiki/Masdar_City [T4]
- World-Architects. Masdar City Master Plan(F+P·Transsolar). 403, 검색 요약 경유. https://world-architects.com/de/projects/view/masdar-city-master-plan [T2, 원문 미확인]
- LAVA. Masdar Plaza(2009). https://l-a-v-a.com/projects/masdar-plaza [T2, 업체]
- Foster + Partners. Masdar City 프로젝트 페이지. 403. https://www.fosterandpartners.com/projects/masdar-city [T2, 원문 미확인]

**South Sabah Al-Ahmad**
- Oasys. Proximity analysis for South Sabah Al-Ahmad masterplan(Narvaez Zertuche & Neira 인용). https://www.oasys-software.com/case-study/proximity-analysis-for-south-sabah-al-ahmad-masterplan/ [T2, 업체 자체 주장]
- Foster + Partners (2023-08-21). Shaping cities and shifting minds with urban design. 403, 검색 요약 경유. https://www.fosterandpartners.com/news/shaping-cities-and-shifting-minds-with-urban-design [T2, 원문 미확인]
- Esri. Foster + Partners(Esri UC 2023 영상). 설명문 검색 요약 경유. https://mediaspace.esri.com/media/t/1_8keede0x [T2, 원문 미확인]
- ICE. Kuwait, South Sabah Al-Ahmad 기반시설 착공. https://www.ice.it/it/news/notizie-dal-mondo/247397 [T4]

**Duisburg**
- Foster + Partners. Duisburg Inner Harbour Masterplan. 403, 검색 요약 경유. https://www.fosterandpartners.com/projects/duisburg-inner-harbour-masterplan [T2, 원문 미확인]
- Wikipedia. Duisburg Inner Harbour. https://en.wikipedia.org/wiki/Duisburg_Inner_Harbour [T4]
- e-architect. Duisburg Inner Harbour Masterplan. https://www.e-architect.com/cologne/duisburg-masterplan [T4]
- Dwell. Industrial Evolution. https://www.dwell.com/article/industrial-evolution-3ce26f54 [T4]
- Christian Science Monitor (1997-12-03). Germany Greens Its 'Brownfields'. https://csmonitor.com/1997/1203/120397.intl.intl.2.html [T4]

**SMG / ARD / 조직**
- Peters, B. & De Kestelier, X. (2006). The Work of Foster and Partners Specialist Modelling Group. *Bridges London*, pp. 9–12. https://archive.bridgesmathart.org/2006/bridges2006-9.html [T3]
- Dialnet. *Architectural Design* 2013 No.2 「Computation Works」 목차(De Kestelier pp.22–27). https://dialnet.unirioja.es/ejemplar/428917 [T3]
- Aish, F., Davis, A., Tsigkari, M. (2013). Ex Silico Ad Vivo. *Architectural Design*. DOI 10.1002/ad.1626. 권호 확인 대기. https://zendy.io/title/10.1002/ad.1626 [T3]
- Construction Management (2017-12-03). Q&A: Foster + Partners' Martha Tsigkari. https://constructionmanagement.co.uk/developing-tomorrows-technology/ [T4]
- Irene Gallou 강연자 소개(Delphi Forum). https://def-viii.delphiforum.gr/speaker/31705098292 [T4]
- Laura Narvaez Zertuche 강연자 소개(SHARE Architects). https://share-architects.com/?p=51330 [T4]
- Wikipedia. SmartGeometry Group. https://en.wikipedia.org/wiki/SmartGeometry_Group [T4]
- CIBSE. Simulation of the urban environment(발표자료, 10 MB 초과·미열람). https://www.cibse.org/media/ys1caizf/03-151214-simulation-of-the-urban-environment-cbdsp-reva.pdf [등급 미정, 원문 미확인]

**홍콩**
- Foster + Partners (2011-03-04). Selected to design masterplan for West Kowloon Cultural District. 403, 검색 요약 경유. https://www.fosterandpartners.com/news/foster-plus-partners-selected-to-design-masterplan-for-west-kowloon-cultural-district-hong-kong [T2, 원문 미확인]
- Arup. West Kowloon Cultural District. https://www.arup.com/projects/west-kowloon-cultural-district [T2, 업체]
