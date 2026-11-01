# 08. 선례 조사 — Autodesk Forma(구 Spacemaker) 고객 사례·적용 연구

- 작성일·확인일: 2026-10-24 (모든 URL은 이 날짜에 확인)
- 대상 제품: Spacemaker(2016 오슬로 창업, 2020.11 Autodesk 인수 $240M) → Autodesk Forma(2023.05) → Forma Site Design(2025.09 개명). 이 문서에서는 시기에 따라 Spacemaker / Forma / Forma Site Design을 원문대로 적습니다.
- 조사 질문: 어떤 분석(일조·일광·바람·소음·미기후·밀도 지표)이 어떤 결정(배치·층수·용도·세대 수)을 바꿨는가, 그 성과 주장은 검증되었는가, 그리고 구경주역(S1 계획 경계 228,025㎡ / 고시 폐역 부지 79,438㎡)에 무엇을 가져올 수 있는가.
- 출처 등급: [T1] 법정·공식문서 / [T2] 공공발간·기관 보고서·업체 공식 사례집 / [T3] 학술 / [T4] 언론·블로그·2차 / [산정] 자체 계산 / [가정].
  - 주의: 과업 규칙에 따라 Autodesk 공식 고객 사례(blogs.autodesk.com/forma, AU 강의 초록, 보도자료, 업체 PDF 사례집)는 [T2]로 분류했습니다. 다만 CLAUDE.md §3.1 기준으로는 업체 자료가 [T4]에 해당하므로, 공모 대응·지구단위계획 문서에 인용할 때는 「[T2, 업체 자료]」로 성격을 함께 적어야 합니다. 이 문서에서는 이를 **[T2v]** 로 표기합니다(v = vendor).
  - 수치 성과 중 방법·기준선·제3자 확인이 없는 것은 모두 **「검증 없는 마케팅 주장」** 으로 표시했습니다.
- 조사의 한계: autodesk.com 본사 도메인(고객 사례 원문, AU 강의 페이지, 캠페인 페이지, 학습 페이지)은 자동 조회가 차단(HTTP 403)되어 blogs.autodesk.com 요약판·검색 스니펫·PDF 사례집으로 대체했습니다. spacemakerai.com(SSL 오류), medium.com·rebild.life(403/503), ScienceDirect·Springer·ResearchGate(접속 차단)는 원문을 읽지 못해 「원문 미확인」을 붙였습니다.

---

## 0. 결론 요약

1. **공개된 Forma/Spacemaker 사례는 약 40건이며, 그중 「분석 → 설계 결정 변경 → 수치 결과」 세 단계가 모두 적힌 것은 10건 안팎입니다.** 나머지는 시간 절감 주장(40시간→4시간, 2일→1.5시간, 1주→1일 등)이나 도구 소개에 그칩니다.
2. **결정을 바꾼 분석은 거의 전부 소음과 일조·일광입니다.** ARCO 말미(헬싱키)·PKA 트론헤임·Cobe 알베르츨룬·AFRY 예테보리·BPD 뉘른베르크·Malmö 엘리네룬드·Oramai 런던이 그렇습니다. 바람은 중정·광장의 쾌적성 보조 지표로, 미기후·내재탄소는 2024년 이후 미국 사례에서만 결정 근거로 등장합니다.
3. **바뀐 결정의 유형은 네 가지로 수렴합니다.** ① 소음원 쪽에 폐쇄형·선형 매스를 세워 완충(ARCO·Cobe·Oramai·Malmö) ② 일조가 확보되는 쪽에 층수 추가·세대 추가(ARCO +20세대, AFRY 100→108, BPD +22%) ③ 그늘진 자리에 도로를 두고 양지를 공공공간으로(Cobe) ④ 중정 크기·건물 높이를 일조로 조정(Bergen Dokken·Vantaa). 모두 **매스 배치 수준**의 결정이며, 용도 구성·가구 분할·단계별 개발순서를 바꾼 사례는 없습니다.
4. **독립 검증은 사실상 부재합니다.** Forma 분석값을 Radiance·CFD·실측과 비교해 오차를 보고한 동료심사 논문을 찾지 못했습니다. Autodesk 스스로 rapid(ML 대리모델) 결과를 「교육된 추측(educated guess)」으로 부르고 detailed 분석을 검증용으로 두고 있습니다. 유일한 학술 평가인 Kolbjørnsrud & Sannes(2022, BI Norwegian Business School)는 조직·프로세스 효과(반복 횟수 증가·조기 평가·참여 확대)를 다루며 물리값 정확도는 다루지 않습니다.
5. **학술 비판은 두 갈래입니다.** Sourek(2024, *Architectural Intelligence*)은 「공공공간 구조를 먼저 설계하는 워크플로를 Forma가 지원도 허용도 하지 않는다」고 지적하고, Harvard D3 사례분석(2021)은 「다세대 주거 전용·공공데이터 품질 의존·기존 배치 반복(echo chamber)」을 한계로 적었습니다.
6. **한국 적용 사례는 공개된 것이 없습니다**(한국어·영어 3회 검색). 아시아는 일본(日建設計·JR東日本建築設計), 싱가포르(RSP), 태국(A49), 중동(Jacobs·Stantec)이 있고, JR東日本建築設計 사례가 일본 사선제한·건폐율·용적률을 Dynamo 도구로 끼워 넣은 점에서 구경주역 규제 4겹 처리의 직접 참고가 됩니다.
7. **구경주역에 주는 결론**: Forma는 ① 공모 심의용 매스 대안 3~5개의 일조·소음·바람 비교 ② 지자체·주민 설득용 「시각 증명(visual proof)」 ③ 성동동 도로·동해선 폐선 소음에 대한 완충 매스 배치 검토에 쓰고, 가구·획지 분할·용도 배분·단계화·규제 판정은 `gjplan`(NSGA-III + buildable 마스크 + MILP)이 맡는 분업이 맞습니다. 이는 §9 「잘하는 결정 / 못 하는 결정」 표와 §8 기존 판단(CLAUDE.md §4)과 일치합니다.

---

## 1. 사례 모집단과 분류

### 1.1 조사 범위에서 확인한 공개 사례 (2026-10-24 기준)

| 구분 | 건수 | 출처 | 비고 |
|---|---|---|---|
| Autodesk Forma 블로그 「Customer Stories」 카테고리 | 49건(5쪽) | https://blogs.autodesk.com/forma/category/customer-stories/ [T2v] | 2023.05~2026.10. 대부분 1~3분 분량 요약판이며 「full story」는 autodesk.com(403) |
| Spacemaker 시기 사례집·블로그(2017~2022) | 7건 | casestudies.com, damassets.autodesk.net PDF, spacemakerai.com, Dezeen, Estate Nyheter, Realtid | NREP, T2H, Steen & Strøm/Storebrand, Cobe, Bouygues Immobilier, DigiGrow, 2017 익명 파일럿 |
| Autodesk University 강의 초록 | 5건 | AU 2021·2024·2025 | 발표 회사명은 대부분 초록에 없음(403으로 확인 불가) |
| 학술·독립 평가 | 5건 | Praktisk Økonomi & Finans 2022, Architectural Intelligence 2024, Harvard D3 2021, ScienceDirect 2022(원문 미확인), Studio Matrx 2026 | 물리값 검증 연구는 0건 |
| 아시아 사례 | 6건 | 일본 2, 싱가포르 1, 태국 1, 중동 2 | 한국·중국·대만·홍콩 0건 |

### 1.2 사례 선별 기준
여섯 칸(설계 질문 → 수집 데이터 → 분석 방법·도구 → 바뀐 설계 결정 → 결과·검증 여부 → 구경주역에 주는 교훈)을 채울 수 있는 사례를 §2~§6에 정리했습니다. 「바뀐 설계 결정」이 원문에 없는 사례는 §7에 한 줄씩만 적고 이유를 밝혔습니다.

---

## 2. 북유럽 개발사·설계사 사례 — Spacemaker 시기(2017~2022)

### 2.1 익명 주거 프로젝트(2017, 노르웨이) — 최초 공개 파일럿
출처: Estate Nyheter 「Vil revolusjonere eiendomsbransjen」 2017-10-12, https://www.estatenyheter.no/aktuelt/vil-revolusjonere-eiendomsbransjen/227702 [T4]

| 칸 | 내용 |
|---|---|
| 설계 질문 | 소음원에서 차폐되면서 가능한 많은 세대가 좋은 일조·조망을 갖는 배치는 무엇인가 |
| 수집 데이터 | 일조, 조망, 소음, 공공 규제(zoning), 공사비. 세부 데이터 소스 미기재 |
| 분석 방법·도구 | Spacemaker 초기 생성 엔진. 「수십억 개 해를 테스트하고 상위 0.00005%만 남긴다」, 서로 크게 다른 해를 골라 제시(설계자는 통상 5~10개, 많아야 50개 검토) |
| 바뀐 설계 결정 | 세대당 평균 일조 수 시간 증가, 소음 노출 구역 세대 수 감소, 외부공간 일조 증가 |
| 결과·검증 여부 | **동일 규제 안에서 20세대 추가** — 개발사 미공개, 기준선 미공개 → **검증 없는 마케팅 주장** |
| 구경주역 교훈 | 「동일 규제 안에서」가 핵심입니다. 규제 상한을 넘기지 않고 배치만으로 세대·일조를 늘렸다는 논리 구조는 우리 추적표의 「규제는 불가능 조건, 목적함수는 배치 품질」 구분과 같습니다. 단, 수치는 인용하지 않습니다 |

### 2.2 NREP — UN17 Village(코펜하겐 Ørestad, 35,000㎡) 및 스톡홀름 북부 프로젝트
출처: ① AU 2021 강의 핸드아웃 AS500351(Daniel Silva Gameiro, Spacemaker/Autodesk) https://static.au-uw2-stg.autodesk.com/Class_Handout_AS500351_ClassHandout-AS500351-Gameiro-AU2021.pdf [T2v, PDF 원문 확보] ② Realtid 2020-12-15 https://www.realtid.se/nrep-tar-hjalp-av-spacemaker-ai-att-bygga-mer-hallbart [T4] ③ casestudies.com NREP https://www.casestudies.com/company/spacemaker/case-study/nrep-pioneers-artificial-intelligence-in-real-estate-using-spacemaker [T4, 날짜 없음] ④ Levery 2026-03 https://www.levery.it/insights/ai-03-26/ [T4] ⑤ Dezeen 2018-12-10 UN17 Village 개요 https://www.dezeen.com/2018/12/10/un17-village-eco-housing-copenhagen-lendager-group-arstiderne-arkitekter/ [T4]

| 칸 | 내용 |
|---|---|
| 설계 질문 | (UN17) 35,000㎡ 공모 당선안(Lendager Group + Årstiderne Arkitekter, 약 400세대·830명 규모 [T4, 자료 간 상충])의 바람·일조·일광·소음·외부공간을 전 팀이 한 모델에서 검토·개선할 수 있는가. (스톡홀름) 기존 건축 제안을 소음·일조·일광 기준으로 재평가하면 더 나은 볼륨이 나오는가 |
| 수집 데이터 | Spacemaker 자동 컨텍스트(지형·인접 건물·도로·철도 소음·토지 데이터), 기존 설계안 3D(IFC/OBJ 반입), 규제 요구사항 |
| 분석 방법·도구 | Spacemaker 「outcome-driven design」: 바람·일조·일광(VSC)·소음·외부공간 분석 + 규제 제약 검토, 3D 모델을 「single source of truth」로 공유 [T2v ①]. 「며칠 동안 전 이해관계자가 이전 제안을 검토」 [T4 ②] |
| 바뀐 설계 결정 | UN17: 건물 하나를 수정·최적화해 **중정 일조 0시간 → 6시간 초과** (Stefan Wallander, NREP Sweden CEO 인용) [T4 ②③]. 스톡홀름: 기존 제안 재배치로 개선 볼륨 생성 [T4 ②]. 핸드아웃: 「일광이 매우 제한된 구역(진파랑)과 상업 전략에 맞지 않는 조망을 확인 → 건물 유형 위치와 형상을 현장에서 변경, 각 대안 성능 검증 후 트레이드오프 합의」 [T2v ①] |
| 결과·검증 여부 | 「6% 세대 증가」(약 12,500㎡ 스튜디오 아파트 파일럿) [T4 ③④] — 어느 프로젝트인지·기준선 미공개 → **검증 없는 마케팅 주장**. 「환경인증 달성이 쉬워졌다」 — 인증 명칭 없음. 중정 일조 0→6시간은 CEO 인용이며 분석 조건(날짜·시각) 없음 |
| 구경주역 교훈 | ① 「전 팀이 한 3D 모델 위에서 규제·환경을 동시에 본다」는 운영 형식은 경주시–국가철도공단–설계사 협의에 바로 쓸 수 있습니다. ② 중정 일조 「0→6시간」 같은 **전·후 비교값**은 추적표의 조정 내역 열에 들어갈 형식의 전형입니다. 우리는 분석 날짜(동지·춘추분)와 시각 범위를 반드시 적어 이 사례의 결함을 피합니다 |

### 2.3 「대형 북유럽 개발사」 등 3건 — Autodesk 인수 보도자료의 익명 성과
출처: Autodesk 보도자료 「Autodesk Completes Acquisition of Spacemaker」 2020-11-24, 원문 investors.autodesk.com(403) → Nasdaq 전재 https://www.nasdaq.com/press-release/autodesk-completes-acquisition-of-spacemaker-provider-of-ai-and-generative-design [T2v, 익명]

| 사례 | 주장 | 판정 |
|---|---|---|
| 대형 북유럽 개발사 | 밀도 +16%, 바다 조망 세대 +33%, 가치 €8M 이상 | 프로젝트·기준선·방법 없음 → **검증 없는 마케팅 주장** |
| 대형 건설사 | 밀도 약 +4%, 추가 900㎡, €4.5M | 같음 |
| 대형 유럽 개발사 | 주거 프로젝트 계획 단계 1년 단축 | 같음 |
| 대형 유럽 설계사(Levery 재인용) | 초기 단계 생산성 50% 향상 | 같음 |

구경주역 교훈: 이 네 수치는 Forma 관련 2차 자료(리뷰 사이트·블로그)에 가장 자주 재인용되는 값입니다. **공모·계획 문서에서는 쓰지 않습니다.** 「밀도 +16% / 조망 +33%」는 밀도와 조망을 동시에 올렸다는 다목적 트레이드오프 서사이지만, 파레토 전선을 보여주지 않으므로 우리 방법(목적공간에 18개 비교 대상을 찍는 방식)의 반례 설명용으로만 씁니다.

### 2.4 Steen & Strøm + Storebrand — Økern Sentrum(오슬로)
출처: Spacemaker 블로그 「How Steen & Strøm and Storebrand use Spacemaker for site development」 Per Wessel Nore, 2021-03-26, https://www.spacemakerai.com/blog/how-steen-strom-and-storebrand-use-spacemaker-for-site-development [T4, **원문 접속 실패(SSL 오류)** — 검색 스니펫과 Harvard D3 사례분석의 인용으로 재구성]; Autodesk 블로그 「The 'city within a city' taking shape in Oslo」 2023-08-17 https://blogs.autodesk.com/forma/2023/08/17/the-city-within-a-city-taking-shape-in-oslo/ [T2v]; Steen & Strøm 보도 https://www.steenstrom.com/news/updated-okern-project-will-create-space-for-more-culture-and-activity [T4]

| 칸 | 내용 |
|---|---|
| 설계 질문 | 쇼핑센터 부지를 주거 최대 1,500세대 복합으로 전환할 때 소음·일광·공공공간 쾌적성을 어떻게 동시에 확보하는가 |
| 수집 데이터 | 도로 교통 소음, 일광, 공공공간 쾌적성(바람·일조) — 스니펫 수준 |
| 분석 방법·도구 | 개발사·설계사 합동 **워크숍** 형식으로 Spacemaker 분석을 실시간 사용 |
| 바뀐 설계 결정 | 「가장 소음이 심한 주거 파사드 면적 10% 감소」, 「고품질 주거 공간을 추가로 찾아 판매 면적이 줄지 않고 늘었다」 [T4, 원문 미확인] |
| 결과·검증 여부 | 수치 근거 미확인. Oslo 계획당국(PBE)에 갱신안 제출 [T4]. 2023년 Autodesk 글은 같은 지구(Økern S, Skanska·KLP Eiendom·Bane NOR Eiendom)를 「최대 40,000세대·일자리 5~10만」의 광역 재생으로 소개하나 분석 내용은 없음 [T2v] |
| 구경주역 교훈 | 「워크숍에서 분석을 돌리며 결정한다」는 형식이 핵심입니다. 구경주역 공모 TF가 경주시·공단·설계사와 **한 자리에서 대안 3~5개를 비교하는 반일 워크숍**을 열 때 쓸 수 있는 선례입니다. 수치(10%)는 원문 확인 전까지 인용 보류 |

### 2.5 T2H Rakennus Oy(핀란드 Vantaa) — 부지 취득 단계 파일럿
출처: Autodesk 고객 사례 PDF 「T2H successfully pilots Spacemaker to assess sites faster and more accurately」 2021-09 제작, https://damassets.autodesk.net/content/dam/autodesk/www/pdfs/adk_21123_sm_customerstory_r2(1)(3)-1.pdf [T2v, PDF 원문 확보]

| 칸 | 내용 |
|---|---|
| 설계 질문 | 「Lovely Homes」 전략(높은 천장·큰 창·일광·조망·발코니)에 맞는 부지를 짧은 시간에 많이 평가할 수 있는가 |
| 수집 데이터 | 자동 컨텍스트 + 소음·일광 분석 + 주차 도구(Parking tool) |
| 분석 방법·도구 | 부지별 3D 매스 대안 비교, 소음·일광 분석으로 세대·놀이터를 최적 방향으로 배치 |
| 바뀐 설계 결정 | 「건물을 최적화해 더 많은 세대와 놀이터를 최적 방향으로 열고 소음 문제를 최소화」 — 구체 프로젝트·수치 없음 |
| 결과·검증 여부 | **4개월 70개 부지 평가, 부지당 내부 검토 시간 약 50% 절감**(Samuel Tuomivaara, 프로젝트 개발자 추정치) → 자체 추정 → **검증 없는 마케팅 주장**. 2021년 1,400세대 건설 예정 회사 |
| 구경주역 교훈 | 구경주역은 부지가 하나라 「부지 스크리닝」 용도는 해당 없습니다. 다만 폐선축 80.3km·폐역 17개소(CLAUDE.md §1)를 **S3 스케일에서 1차 선별**할 때 이 방식이 쓰입니다. 폐역별 소음·일광·접근성 스크리닝 → 구경주역이 왜 우선인지 근거 제시 |

### 2.6 Cobe(덴마크) — Vridsløse 마스터플랜(Albertslund) 외
출처: Dezeen 「Cobe uses Spacemaker's AI software to future-proof its designs」 2022-05-31, https://www.dezeen.com/2022/05/31/cobe-spacemakers-ai-software/ [T4, **「Partnership content」= Spacemaker 광고 기사**]

| 칸 | 내용 |
|---|---|
| 설계 질문 | 옛 교도소 부지를 6개 주거지구로 재생하면서 밀도를 높이고 거주성(일조·바람·소음)을 지킬 수 있는가 |
| 수집 데이터 | 일조·일광·바람·미기후·소음·밀도·옥상 태양광 잠재량·조망. 「100개 기준으로 부지 테스트」(업체 주장) |
| 분석 방법·도구 | Spacemaker로 매스가 가로·중정의 일조·바람에 미치는 영향 신속 테스트. 간선도로변 소음 완화 필요 구역 식별 |
| 바뀐 설계 결정 | ① **간선도로변에 더 조밀하게 건물을 세워 소음 완충**으로 삼음 ② Vridsløse 남측 매스 옵션 다중 테스트 ③ **도로를 부지의 그늘진 쪽에 두어 양지인 북측 광장을 공공용으로 확보** — 「이해관계자 설득에 도움」(Mads Birgens, Cobe 도시설계 책임) |
| 결과·검증 여부 | 수치 없음. 광고 기사이므로 한계 언급 없음 |
| 구경주역 교훈 | 두 결정이 모두 구경주역에 전이됩니다. ① 원화로·북측 간선 쪽에 **완충 매스**(상업·공공청사)를 두고 그 뒤를 보행·공원으로 ② 신설 도로를 **일조 분석의 음영 구역**에 맞춰 긋고 양지는 광장으로. 특히 ②는 「도로를 자유롭게 그리게 하지 말라」(CLAUDE.md §10)와 양립하는 **저차원 도로 배치 규칙**이 됩니다. 매장문화재 유존지역과 겹치지 않는지 buildable 마스크로 먼저 자릅니다 |

### 2.7 Bouygues Immobilier(프랑스 추정) — 2개 프로젝트
출처: casestudies.com https://www.casestudies.com/company/spacemaker/case-study/how-spacemaker-is-helping-bouygues-immobilier-design-more-efficient-sustainable-projects [T4, 날짜 없음]

| 칸 | 내용 |
|---|---|
| 설계 질문 | 밀도·일광·일조·음향·도시 조건을 동시에 만족하는 배치 |
| 수집 데이터 | 3D 모델 반입·정제, 개발사·설계사·지자체 공유 워크플로 |
| 분석 방법·도구 | Spacemaker 일광·일조·음향 분석 |
| 바뀐 설계 결정 | **건물 레이아웃 변경**으로 세대 일광 개선, 음향 문제 해소, **Venturi 효과(건물 사이 풍속 증가) 회피** |
| 결과·검증 여부 | 수치 없음. Paul Eydaleine(직함 없음) 이름만. → 정성 주장 |
| 구경주역 교훈 | Venturi 효과 회피는 구경주역처럼 **동서로 긴 선형 부지에 판상형 매스가 나란히 놓일 때** 발생하는 전형적 문제입니다. 바람 분석을 중정·보행축 통과 폭 결정에 쓰는 근거 사례 |

### 2.8 Voss(노르웨이) 도심 개념안 — 개인 설계자 검증기
출처: Medium, Arne Bassøe-Eriksen 「How I put my assumptions for an urban concept to test with Spacemaker's AI platform」 https://medium.com/@arne.bassoeeriksen/how-i-put-my-assumptions-for-an-urban-concept-to-test-with-spacemakers-ai-platform-b97aa7493e0c [T4, **원문 접속 실패(403)** — 검색 스니펫만]

스니펫 기준: 산지에 갇힌 소도시 Voss의 밀도 증가 개념에 대해 소음 분석이 「인접 도로 소음이 주거 복합 여러 세대에서 기준을 넘는다」는 것을 밝혔고, 이웃을 위한 조망 분석도 수행. 설계자 자신의 가정을 검증·기각하는 데 쓴 드문 1인 사용 기록입니다. 구경주역 교훈: Forma의 가장 정직한 용도는 「내 가정이 틀렸음을 빨리 아는 것」입니다. 상세는 원문 확인 대기.

---

## 3. 북유럽·유럽 사례 — Forma 시기(2023~2026)

### 3.1 ARCO Architecture Company — 말미(Malmi) 학생주택, 헬싱키
출처: Autodesk Forma 블로그 「How ARCO used Forma Site Design's data-driven insights…」 Jeanne Tan, 2023-05-08, https://blogs.autodesk.com/forma/2023/05/08/how-arco-used-formas-data-driven-insights-to-transform-a-challenging-urban-site-into-valuable-student-housing/ [T2v]; 같은 날 「ARCO: Embracing the promise of data」 https://blogs.autodesk.com/forma/2023/05/08/arco-forma-data-sustainability/ [T2v]

| 칸 | 내용 |
|---|---|
| 설계 질문 | 남측에 철도와 간선도로, 주위를 고가 램프(하부 주차)가 감싼 저이용 부지에 핀란드 주간 소음 기준 55 dB를 만족하는 학생주택(22~25㎡ 150~170세대 + 가족형 수 세대, 8층 약 8,400㎡)을 넣을 수 있는가 |
| 수집 데이터 | 다른 설계 소프트웨어에서 만든 3D 모델을 Forma로 반입(「준비 거의 없이」), 자동 컨텍스트(도로·철도 소음), 지자체의 랜드마크 높이 허용 |
| 분석 방법·도구 | 소음 분석(폐쇄 원통 볼륨의 중정 소음 확인), 일조 분석(상층 추가가 중정 일조를 줄이지 않는지, 데크의 양지 위치), 일광 잠재력(VSC) |
| 바뀐 설계 결정 | ① **원통형 볼륨 + 외부 복도형 폐쇄 파사드를 소음 완충으로** 삼고 세대는 조용한 중정으로 개방 ② **양지인 남측에 7·8층 추가 → 약 20세대 증가** ③ 기계실을 7·8층에서 6층으로 이동 ④ 남향 경사 지붕(태양광·중정 반사광) ⑤ 중정 데크를 부분적으로 1층 높임 |
| 결과·검증 여부 | 세대 **71%가 VSC 27% 이상**(양호 일광 기준) [T2v]. 소음 전후 dB값·일조 시간 미공개. 시공사 Hoas, 음향 Promethor(별도 컨설턴트 참여 — 즉 Forma 소음값이 최종 검증값은 아님). 준공 후 성과 미보고 |
| 구경주역 교훈 | 구경주역 북측 획지(원화로·동해선 폐선 노반 인접)에 가장 직접적인 선례입니다. ① 소음원 쪽 **폐쇄 파사드 + 내향 중정**은 청년·신혼 1~2인 주거 600세대(work/20261008_youth_housing)의 배치 원형 후보 ② 「VSC ≥ 27% 세대 비율」은 우리 목적함수의 주거 품질 지표로 바로 채택 가능 ③ 음향 전문 컨설턴트가 별도로 있었다는 사실은 「Forma 소음값 = 설계 탐색, 법정 검토 = 전문 소프트웨어」 분업을 확인해 줍니다 |

### 3.2 Per Knudsen Arkitektkontor(PKA) — Fridheimskvartalet·Nidelven, 트론헤임
출처: Autodesk Forma 블로그 「Forma contributes to PKA's competition wins」 Marthe Brøndbo, 2023-05-08, https://blogs.autodesk.com/forma/2023/05/08/forma-contributes-to-pkas-competition-wins/ [T2v]

| 칸 | 내용 |
|---|---|
| 설계 질문 | 도심 인필(Fridheimskvartalet, GFA 약 33,500㎡·약 380세대)과 옛 산업부지(Nidelven, 500~600세대)의 **고밀도와 주변 질 유지**를 심사위원에게 어떻게 증명하는가 |
| 수집 데이터 | 자동 컨텍스트, 초기 개념을 개발사와 공유해 피드백 반영 |
| 분석 방법·도구 | **소음 분석 전·후 비교**(기존 부지 vs 제안안), 일광·일조 통계를 회의 자료로 사용 |
| 바뀐 설계 결정 | 원문에 구체 변경 없음. 「신축 건물 사이 음환경 개선, 북측 이웃 소음 감소」를 제안안의 효과로 제시. 심사위원은 「건축 가능 면적을 줄이지 않고 높이를 조정할 수 있다」고 평함(Forma 귀속 아님) |
| 결과·검증 여부 | 두 공모 당선. 「8~10명 상근 설계자 분량, 최대 15% 성장」은 PKA 추정 → **검증 없는 마케팅 주장**. 당선과 Forma의 인과는 PKA 자체 평가 |
| 구경주역 교훈 | 「소음 전·후 비교 지도」는 **구경주역 결정도(2026.01)와 우리 대안의 비교**에 그대로 쓰는 형식입니다. 「Forma 통계를 가리키며 이것이 좋은 일광 상황이라고 말할 수 있다」(Axel Kristoffersen)는 심의 대응 화법은 T1·T2 근거 위에서만 성립하므로, 우리 문서에서는 분석 조건(날짜·격자·기준)을 각주로 붙입니다 |

### 3.3 AFRY — Fjällbogatan, 예테보리(지자체 소유 부지)
출처: Autodesk Forma 블로그 「AFRY uses Autodesk Forma for Sweden city planning」 2024-01-26, https://blogs.autodesk.com/forma/2024/01/26/afry-uses-autodesk-forma-for-sweden-city-planning/ [T2v]; Autodesk 고객 사례 PDF https://damassets.autodesk.net/content/dam/autodesk/www/pdfs/afry-uses-autodesk-forma-for-sweden-city-planning-001.pdf [T2v, 미열람]

| 칸 | 내용 |
|---|---|
| 설계 질문 | 예테보리시 부동산부가 **사전 승인한 배치안을 개발사에 매각**하려는 좁은 교외 부지(2층 연립 인접, 높이 증가·건폐 축소 불가)에서, 우수 조사로 드러난 **홍수 취약성**(대규모 유역 하류, 기존 배수 용량 초과)을 해결하면서 사업성을 지킬 수 있는가 |
| 수집 데이터 | 외부 DB 지형 모델(「수 분 내」 반입), 우수 조사 결과(Forma 외부), 소음·바람·일영 |
| 분석 방법·도구 | Forma에서 **수십 개 배치안** 테스트(이전에는 4~5안). 소음·바람·일영 측정. **홍수·우수 분석은 Forma 기능이 아니라 별도 조사**였음 |
| 바뀐 설계 결정 | 기존 건폐·높이 한계 안에서 **모든 건물을 재배치**, 주거·상업·휴양 구성 |
| 결과·검증 여부 | **세대 100 → 108(+8%)**, 판매 면적 유지 [T2v]. 지자체 1차 검토 통과 후 주민 의견 수렴 단계(승인 아님). 홍수 성능·시간·비용의 독립 데이터 없음 → 세대 수치는 업체 사례, **홍수 해결 주장은 검증 없음** |
| 구경주역 교훈 | ① **「지자체가 배치안을 먼저 확정하고 민간에 매각」** 구조는 경주시–국가철도공단 MOU(2026.01) 아래 공단 소유 부지를 혁신지구로 공모하는 구경주역과 같은 거버넌스입니다. ② Forma가 홍수를 다루지 못한다는 점(우리 02 조사와 일치)은 구경주역의 **철도 노반 성토·배수·토양오염 제약을 외부 조사 → buildable 마스크**로 넣어야 함을 재확인합니다 |

### 3.4 BPD(Bouwfonds) — 뉘른베르크 남동부 옛 사무소 부지 5,290㎡
출처: Autodesk Forma 블로그 「BPD: 'When you can show that a certain density is viable, the municipality is open to discussing it'」 Jeanne Tan, 2023-07-04, https://blogs.autodesk.com/forma/2023/07/04/bpd-when-you-can-show-that-a-certain-density-is-viable-the-municipality-is-open-to-discussing-it/ [T2v]

| 칸 | 내용 |
|---|---|
| 설계 질문 | 기존 13층 타워가 있는 부지에 주거 전환 승인은 있으나, **지자체·주민이 받아들일 밀도 상한**은 어디인가 |
| 수집 데이터 | 자동 컨텍스트, 기존 조건 vs 제안 조건 비교 모델 |
| 분석 방법·도구 | 일조(인접 주택 추가 그림자 유무), 바람(새 풍동 발생·남쪽 냉풍 차단 여부), 소음(문제 파사드 식별 → 방음벽·창호·외장 대안) |
| 바뀐 설계 결정 | ① **제2 주거 타워 추가**(주변 고층 존재를 근거로) ② 기존 타워 층수 추가 ③ 결과적으로 **원안 대비 밀도 +22%**, 대형 세대·혼합 개선 ④ 공모 당선안(Gräßel ARCHITEKTEN)을 다시 Forma로 검증해 신규 문제 없음 확인 |
| 결과·검증 여부 | 「인접 주택에 추가 그림자 없음」「남쪽 냉풍 차단 없음」은 BPD 자체 분석. 지자체 문서·독립 검토 없음. 「visual proof」가 협상에 유효했다는 것은 개발자(Fabian Kuusik) 진술 → **밀도 +22%는 업체 사례, 환경 무영향 주장은 검증 없음** |
| 구경주역 교훈 | 구경주역 결정도에는 주거가 없고(CLAUDE.md §5-5), 우리는 주거를 넣는 대안을 냅니다. 이때 BPD처럼 **「이 밀도가 인접 성동동 저층 주거에 추가 그림자·바람 피해를 주지 않는다」는 전·후 비교 지도**가 지자체·주민 설득의 핵심 산출물입니다. 역사문화환경 보존지역 허용기준(고도)이 밀도 상한을 먼저 자르므로, Forma 비교는 그 상한 **아래**의 배치 선택에만 씁니다 |

### 3.5 Oramai Studio(런던) — 50~300세대 인필·브라운필드, 950세대 복합
출처: Autodesk Forma 블로그 「'The enemy at this early stage is time': How Oramai Studio creates space to explore beyond the first sketch idea」 Jeanne Tan, 2026-09-28, https://blogs.autodesk.com/forma/2026/09/28/how-oramai-studio-creates-space-to-explore-beyond-the-first-sketch-idea/ [T2v]

| 칸 | 내용 |
|---|---|
| 설계 질문 | 첫 스케치 하나에 갇히지 않고 매스 대안을 여럿 비교할 시간을 어떻게 확보하는가 |
| 수집 데이터 | Forma 부지 설정 → Revit 전송(「최대 반일 절감」), 자체 부지 평가 플랫폼 Plangen, Revit 자동 검사(면적·NIA·단면/양면 개방 세대) |
| 분석 방법·도구 | **Site Automation(생성)으로 매스 옵션 생성 → Forma에서 지표 실시간 비교**, rapid 소음·바람(초 단위), 일조 |
| 바뀐 설계 결정 | ① **철도 소음을 더 많이 막는 선형 매스 선택** → 조용한 출입구·놀이공간 ② 고층 프로젝트에서 매스 위치가 보행자 풍환경에 미치는 영향 확인 ③ 3개 매스 옵션 중 **파사드·포디움 중정 일조가 가장 좋은 3안 선택** |
| 결과·검증 여부 | 시간 절감 자체 보고, 준공 성과 없음 → 결정 변경은 구체적이나 **수치 검증 없음** |
| 구경주역 교훈 | 2026년 최신 워크플로의 표본입니다. **생성(Site Automation) → 비교(Forma) → 설계(Revit) → 재검증(Forma)** 순환이 우리 `gjplan` 생성 → 평가 → Rhino 수정 → config 반영 → 재실행(CLAUDE.md §7)과 같은 구조입니다. 차이는 생성기의 투명성: Forma Site Automation은 파라미터가 비공개이고, 우리는 모든 결정을 파라미터로 추적합니다(§4 판단) |

### 3.6 Patriarche(프랑스·스위스·캐나다, 약 400명) — 볼륨 스터디 시간
출처: Autodesk Forma 블로그 2023-05-08 https://blogs.autodesk.com/forma/2023/05/08/how-forma-enhances-patriarches-augmented-architecture/ [T2v]

프로젝트명 없음. 도시계획 부문이 **타당성 볼륨 스터디를 기존 약 2일 → 1.5시간**으로 단축(Etienne Guyot, 도시계획 부문장). 조망·음향·바람·일조는 「테스트하고 싶다」 단계. 프로젝트 이력(history)으로 선택 근거를 고객·공공에 설명. → **시간 수치는 일화적, 결정 변경 없음.** 구경주역 교훈: 「선택 이력을 남겨 설명한다」는 우리 추적표(CLAUDE.md §3.5)와 같은 요구이며, Forma 자체 이력만으로는 파라미터 추적이 안 되므로 추적표를 별도로 둡니다.

### 3.7 Cobe·Sweco·Nordic Office of Architecture·A-lab 등 — 결정 변경이 적히지 않은 설계사 사례
Sweco(2023-05-08), Nordic Office of Architecture(2023-05-08·10-18 영상), A-lab(2024-07-09), Club(2023-09-28), CUBE 3(2023-05-08), Egis Group 디자인 챌린지(2024-09-26), Architectus Q&A(2024-09-04), Weston Williamson + Partners(2024-07-17: 바람·일조·탄소를 「검증이 아니라 설계의 한 형태」로, 고객이 Forma 기반 안을 선택) — 모두 [T2v], 도입 소감·도구 철학 중심이며 바뀐 설계 결정·수치 없음. 목록만 기록합니다.

---

## 4. 지자체(계획 당국) 사례 — 북유럽

출처(공통): Autodesk Forma 블로그 「Nordic municipalities are embracing data-driven urban planning」 Raoul Lindberg, 2024-04-23, https://blogs.autodesk.com/forma/2024/04/23/nordic-municipalities-embracing-data-driven-urban-planning/ [T2v]; AEC Magazine 「Danish municipality adopts Autodesk Spacemaker」 2023-02-24, https://aecmag.com/concept-design/danish-municipality-adopts-autodesk-spacemaker/ [T4]; Autodesk 블로그 Rødovre 2023-06-22 https://blogs.autodesk.com/forma/2023/06/22/rodovre-first-danish-municipality-to-collaborate-with-forma/ [T2v]; casestudies.com DigiGrow https://www.casestudies.com/company/spacemaker/case-study/spacemaker-successfully-trialled-to-help-municipalities-innovate-during-digigrow-pilot [T4]; rebild.life(503, 원문 미확인) [T4]

### 4.1 Rødovre(덴마크) — 3개 사업 약 200,000㎡, Bykernen 포함

| 칸 | 내용 |
|---|---|
| 설계 질문 | 12㎢·42,000명의 고밀 소도시에서 사회주택 포함 주거 중심 3개 사업의 **개발사 제안을 어떻게 비교·선택**하는가. Motorring 3 등 통과 교통 소음이 상시 쟁점 |
| 수집 데이터 | 자동 컨텍스트 + 교통 소음 |
| 분석 방법·도구 | 일조·바람·소음의 「측정 가능한 데이터」를 개발 단계에서 제시, 정치인·개발사·컨설턴트 대상 시각화 |
| 바뀐 설계 결정 | 「제안 비교 후 선택」 — 구체 변경 미기재 |
| 결과·검증 여부 | 덴마크 최초 지자체 도입(2023). 수치 없음. 인용: Jesper Pagh 전 시 건축가 「개발 단계에서도 일조·바람·소음의 측정 가능한 데이터를 준다」 |
| 구경주역 교훈 | 지자체가 **심사 도구**로 쓰는 모형입니다. 경주시가 공모 응모안·향후 민간제안을 같은 분석 조건으로 비교하려면, 우리가 **분석 조건표(날짜·격자·소음 입력)**를 먼저 공개 표준으로 제안할 수 있습니다 |

### 4.2 Malmö(스웨덴) — Elinelund 약 2,000세대·학교·유치원·체육관

| 칸 | 내용 |
|---|---|
| 설계 질문 | 시가 토지 소유자이자 **detaljplan(상세계획) 작성 주체**인 자연 민감 지구에서 학교 구역의 소음과 바람을 어떻게 줄이는가 |
| 수집 데이터 | 자동 컨텍스트, 사회적 공간·자연 보호 구역 |
| 분석 방법·도구 | 소음·바람·일조(「주·월 단위 걸리던 연구를 빠르게」— Annie Altengård, 계획건축가) |
| 바뀐 설계 결정 | **바람에 실려 학교 구역에 닿는 소음을 줄이기 위해 건물을 엇갈려(staggered) 배치**, 건물 위치·높이 변화 |
| 결과·검증 여부 | 수치 없음. 3단계 계획 마무리 단계 |
| 구경주역 교훈 | 「소음 + 바람」을 **결합 지표**로 본 드문 사례입니다. 구경주역의 겨울 북서풍과 원화로 소음이 겹치는 북서측 획지에 같은 검토가 필요합니다. 또 지자체가 계획 작성 주체로 Forma를 쓴 선례는 **지구단위계획 변경 제안서**에 분석 도면을 넣는 근거가 됩니다 |

### 4.3 Vantaa(핀란드) — Kivistö 지구 Onnenkivi 50,000㎡·Lumikvartsi 60,000㎡

중정 계획을 바람 감소와 양지 테라스 배치로 다듬고, **교통 속도제한이 소음에 미치는 영향**을 함께 검토 [T2v]. 수치 없음. 구경주역 교훈: 원화로 설계속도·교통량은 Forma 소음 입력값이므로, **도로 속도 하향(예: 50→30 km/h) 시나리오**를 소음 지도로 비교하는 것은 비용 0의 대안 변수입니다.

### 4.4 Bergen(노르웨이) — Dokken 비전·전략계획, 첫 지구계획(zoning plan), 민간 계획 검토

**일조 조건에 맞춰 건물 높이와 중정 크기 조정** [T2v]. 민간 제출 계획 검토에도 사용(Knut Knutsen, 시 계획가). 구경주역 교훈: 「높이·중정 크기 ↔ 일조」는 고도보존육성지구 높이 상한 아래에서 **중정 폭을 결정하는 규칙**으로 번역할 수 있습니다(예: 동지 정오 중정 지면 일조 ≥ 2시간).

### 4.5 Bodø·Norrköping — 보조
Bodø: 개발사 Clemens Eiendom가 사용, 시는 계획당국·토지소유자로 참여, 「시간 절감」만 언급. Norrköping: 2035년 140,000→175,000명·15,000세대 대비 도시구조 스케치와 소음·일조·일광·바람 분석 테스트 중 [T2v]. 결정 변경 없음.

### 4.6 DigiGrow(스웨덴 Umeå·Linköping) — 실데이터 테스트랩

| 칸 | 내용 |
|---|---|
| 설계 질문 | 지자체 실데이터로 계획 대안 비교와 이해관계자 대화를 디지털화할 수 있는가 |
| 수집 데이터 | 지자체 실데이터 |
| 분석 방법·도구 | Spacemaker 생성 설계·도시계획 도구, 소음·일조·일광·건물 볼륨 |
| 바뀐 설계 결정 | 미기재 |
| 결과·검증 여부 | 「사용 쉬움, 기존 도구 보완, 투명성·대화·정확도 향상」(정성). **「계획~준공 총 기간 33% 단축」은 DigiGrow 프로세스 전체 수치이며 Spacemaker 단독 귀속 아님** → 재인용 금지 |
| 구경주역 교훈 | 「33% 단축」을 Forma 효과로 쓰는 2차 자료가 있으므로 주의. 우리 문서에서는 쓰지 않습니다 |

### 4.7 Rebild(덴마크) — 「계획 1년 단축」 [T4, 원문 미확인]
rebild.life 글이 Spacemaker로 지자체 성장 계획을 세우면 1년을 절약할 수 있다고 주장하나, 두 차례 접속 모두 503. 근거 미확인 → **검증 없는 마케팅 주장**, 확인 대기.

---

## 5. 생성 설계(Explore → Site Automation) 사용례

### 5.1 기능의 변천과 작동 방식
| 시기 | 명칭 | 작동 | 출처 |
|---|---|---|---|
| 2017 | (초기 엔진) | 「수십억 해 테스트, 상위 0.00005% 보존, 서로 다른 해 제시」 | Estate Nyheter 2017-10-12 [T4] |
| 2019~2021 | Spacemaker v1.0 → v2.0 | v1.0은 사용자 조정 여지가 적어 「직관을 배제」 → 피드백으로 v2.0에서 사용자 입력 확대 | Harvard D3 2021-04-21 [T3-/T4] |
| 2023.03 | Explore | 부지 선택 → 건물 치수(높이·폭·최소 이격)·배치 형식·층수 입력 → 바람·일사·조망 등 목표 → 「런던 예시: 30초 내 95개 제안」 → 하나를 골라 바람·일조로 다듬고 Revit 플러그인으로 왕복 | Symetri 블로그 2023-03-01 https://symetri.co.uk/insights/blog/ai-and-generative-urban-design-you-can-start-using-today-with-spacemaker [T4] |
| 2025~ | Site Automation(구 Explore) | 사용자 파라미터로 가구형·선형·탑상형·혼합 배치 생성·평가, 건물 바닥 직접 조정 | Autodesk 블로그 2025-04-24 https://blogs.autodesk.com/forma/2025/04/24/how-to-use-generative-design-ai-and-3d-modeling-for-improved-site-planning/ [T2v] |
| 2025~ | Building Layout Explorer(실험) | 평면 생성 AI, 미국 데이터 저장 상용 사용자 한정 | Autodesk News https://adsknews.autodesk.com/en/news/building-layout-explorer-in-autodesk-forma/ [T2v] |

### 5.2 생성 기능이 결정을 바꾼 공개 사례
| 사례 | 생성 사용 | 바뀐 결정 | 검증 |
|---|---|---|---|
| Oramai Studio(§3.5) | Site Automation으로 매스 옵션 생성 | 선형 매스(철도 소음 차단), 3안 중 일조 최적안 | 수치 없음 |
| HMC Architects(§7.1) | 생성 아닌 **수동 3안**(Bar/Square/Courtyard) | RFP가 지정한 Bar 대신 Courtyard 권고 | 자체 수치만 |
| Istanbul 미개발지(§6.4) | Spacemaker 생성 도구로 블록 변형 | SU +31.58%, FAR +125.21%, CFI +35.54% | 학술 북챕터, 원문 미확인 |
| NREP·2017 파일럿(§2.1·2.2) | 초기 생성 엔진 | 세대 증가·일조 증가 | 마케팅 |

판단: **생성 기능이 「어떤 파라미터로 무엇을 생성했는지」를 공개한 사례는 없습니다.** 모든 사례가 결과(선택된 안)만 적습니다. 이는 우리가 확산모델·이미지 학습을 기각하고 규칙기반 생성 + NSGA-III를 채택한 이유(CLAUDE.md §4 「모든 결정이 파라미터로 추적됨」)와 정확히 대응합니다. Forma Site Automation은 **대안 아이디어 소스**로만 쓰고, 추적표에 들어가는 대안은 `gjplan/generate`가 만듭니다.

---

## 6. 학술·독립 평가 [T3] 및 비판

### 6.1 Kolbjørnsrud & Sannes(2022) — 유일한 현장 연구
- 서지: Kolbjørnsrud, V. & Sannes, R. (2022). *Problemløsing med kunstig intelligens: Bruk av Spacemaker i tidligfase eiendomsutvikling*. **Praktisk Økonomi & Finans** 38(1), 47–64. https://doi.org/10.18261/pof.38.1.4 [T3, **원문 미확인(403)** — BI 교수 프로필 서지 https://www.bi.no/en/about-bi/employees/department-of-strategy-and-entrepeneurship2/vegard-kolbjornsrud/ 및 SSE 세미나 초록 2023-01-24 https://www.hhs.se/en/about-us/calendar/hoi-events/2023/24-jan-2023---research-seminar-vegard-kolbjornsrud 으로 재구성]
- 영어판 작업논문: *Solving Problems with Artificial Intelligence: Augmenting Design Work in Architecture and Property Development* (2023, 5th Nordic Workshop on Digital Foundations… 및 SSE House of Innovation 세미나)

| 칸 | 내용 |
|---|---|
| 설계 질문(연구 질문) | AI가 조직의 복합 문제해결 과정을 어떻게 바꾸고, 인간–기계 협업은 어떤 형태인가 |
| 수집 데이터 | 북유럽·발트 **3개 회사의 복수 프로젝트**(영어판 초록) / 노르웨이판은 OBOS·Nordr 2개사로 검색 요약 [원문 미확인, 상충] |
| 분석 방법 | 사례 추적(인터뷰·관찰 추정 [가정]) |
| 발견 | Spacemaker가 설계·분석·의사결정을 지원해 **① 더 많고 빠른 반복 ② 더 열린·포용적 과정 ③ 더 이른 단계의 철저한 평가** → 「인간–기계 팀의 집단지성 증가」. 시스템의 한계와 인간 역할도 논함(내용 미확인) |
| 검증 여부 | 동료심사 저널(노르웨이 응용 경영학). 물리값 정확도·사업 성과는 측정 대상 아님 |
| 구경주역 교훈 | Forma의 효과는 **「과정」 효과**로 입증되었고 「결과(더 좋은 도시)」 효과는 입증되지 않았습니다. 공모 문서에서 Forma 사용의 근거는 「이해관계자 참여·조기 평가」로 쓰고, 설계 품질 근거는 우리 목적함수 측정값으로 씁니다 |

### 6.2 Sourek(2024) — 워크플로 비판
- 서지: Sourek, M. (2024). AI in architecture and engineering from misconceptions to game-changing prospects. **Architectural Intelligence** 3:4. https://doi.org/10.1007/s44223-023-00046-9 [T3, Open Access, **PDF 원문 확보** https://papers.cumincad.org/data/works/att/architectural_intelligence2024_4.pdf]
- Spacemaker 관련 요지(pp. 9–10, 13):
  1. 파라메트릭 평가(에너지·음향·일광 등)는 성숙한 도구이며 Spacemaker·Cove.tool·Giraffe가 이를 제공 — **긍정**.
  2. 그러나 워크플로가 문제: 주소·경계 입력 → OSM 등 공개 DB로 지형·건물 생성(「정확도는 지역별 데이터 품질에 의존」) → **도로는 수동으로만 추가, CAD 반입 불가**(2023년 당시) → 건물은 수동 배치 또는 층수·세대 믹스 조건으로 생성 → 연면적으로 평가 → 소음·바람·일조·일광·미기후 평가 → Excel·Revit·IFC 내보내기.
  3. 핵심 비판(Pavel Shaban, MS architekti 프라하 인용): 이 흐름은 「근시안적 부동산 거래자(shortsighted real estate trafficker)」에는 맞지만, **「공공공간(가로·광장·공원)의 격자와 결(grid-and-grain)을 먼저 설계하고 건물을 나중에 앉히는」 책임 있는 설계 과정을 Spacemaker는 지원하지도 허용하지도 않는다.**
  4. 「IT 라인과 설계자 라인 사이 가위가 벌어지는(scissors)」 문제의 체현. 대조 사례로 MVRDV Valley(암스테르담)의 자체 분석 도구 사용을 든다.
- 구경주역 교훈: 이 비판은 우리 설계의 **순서 원칙**과 일치합니다. 구경주역은 「연결·기반·보행 먼저」(CLAUDE.md §5-2), 선형 축 연속성 우선(§5-8)이 1단계이며, Forma는 그 가로·공원 구조가 정해진 **뒤**의 매스 검토에만 씁니다. 가로 구조 자체를 Forma에서 그리지 않습니다.

### 6.3 Harvard D3 사례분석(2021) — 한계 목록
- 서지: Kyle R. (2021-04-21). *Spacemaker: Merging AI technology with Urban Planning and Design*. Harvard Business School Digital Innovation and Transformation(학생 과제물). https://d3.harvard.edu/platform-digit/submission/spacemaker-merging-ai-technology-with-urban-planning-and-design/ [T3-/T4]
- 적시된 한계: ① **다세대 주거 설계 옵션만 지원**(사무·상업은 새 데이터·ML 조정 필요) ② 공공 건축환경 데이터가 「단편적·불일치·통제 부재·종종 부재」(4중) ③ 데이터 접근은 노르웨이에서 강하고 다른 나라에서 약함 ④ v1.0 유연성 부족 → v2.0 ⑤ 비판자들의 **「도시설계 echo chamber」**(기존 「실현 가능한」 배치의 무한 재생산) 우려.
- 구경주역 교훈: ①은 구경주역 프로그램(K-헤리티지 복합거점·모빌리티 허브·STAY·공공청사·문화)이 **주거 외 용도 중심**이라는 점에서 Forma 생성 기능의 적용 범위가 좁음을 뜻합니다. ②③은 한국 컨텍스트 데이터가 OSM·ASTER 30m로 떨어질 가능성(02 조사)과 같은 문제입니다. ⑤는 「분산 삽입형 대안」(CLAUDE.md §5-4)처럼 전례 없는 배치를 Forma가 제안하지 못할 것이라는 뜻입니다.

### 6.4 Istanbul 미개발지 북챕터(2022) [T3, 원문 미확인]
- 서지: 「Spacemaker.Ai: Using AI in developing urban block variations」, Elsevier 북챕터(ScienceDirect PII B978012823941400010X), 저자·서명 미확인(ScienceDirect·ResearchGate 모두 403). https://www.sciencedirect.com/science/article/abs/pii/B978012823941400010X
- 검색 스니펫: 이스탄불 미개발지 사례연구로 Spacemaker 생성 도구를 조사, 「다건물 수준 생성 설계의 성공 적용이 드물다」고 전제. 선정 건물 최적화 후 **공간이용률(SU) +31.58%, 용적률(FAR) +125.21%, 상업 전면 지수(CFI) +35.54%**.
- 판정: 수치가 Spacemaker 자체 출력인지, 저자의 별도 계산인지 미확인. FAR 2.25배 증가는 규제 상한 없는 미개발지라는 조건을 반영한 것으로 보임 [가정]. **구경주역에는 전이 불가**(규제 4겹이 상한을 먼저 자름). 원문 확인 대기.

### 6.5 기타 2차 학술 언급
- MDPI *Buildings* 2026, 16(4):685 「Evaluation of Building Design Variants in Early Phases…」 — Spacemaker/Forma를 「도시 매스·부지 설계 / AI 기반 환경분석」으로 분류만 함 [T3]. https://www.mdpi.com/2075-5309/16/4/685
- Springer *Architectural Research* 2026 28:4 리뷰 — Forma가 「부지·일사·조망·규제를 분석해 최적 밀도·조닝 대안을 즉시 계산」, 어느 설계사의 「타당성 검토 수 주 → 수 시간」을 재인용 [T3, 원문 접속 불가(로그인 리디렉션)] https://link.springer.com/article/10.1007/s44515-026-00006-0
- Studio Matrx Monthly 2026-09(Amogh N P) 「Forma, Spacemaker & Early Design」 — 대리모델(surrogate) 설명: 「학습 분포 안에서는 **순위 비교에 매우 좋음**, 밖에서는 **자신감이 정확도를 넘어 그럴듯한 숫자**를 낼 수 있음」, 일조·그림자·면적은 기하 계산이므로 입력만큼 신뢰 가능, 바람·운영에너지는 학습 근사라 불확실성 큼, 「보고서·승인·계약용 수치로는 부적합, Radiance·ClimateStudio·IES·EnergyPlus·CFD로 검증」 [T4, 독립 해설] https://www.studiomatrx.org/students/ai-assisted-design-workflows/forma-spacemaker-and-early-design

### 6.6 정확도 검증 상태 — 분석별
| 분석 | Autodesk 설명 | 독립 검증 | 판정 |
|---|---|---|---|
| 일조(sun hours)·그림자 | 기하 계산, 6분 간격 샘플(02 조사) | 없음(불필요에 가까움, 입력 기하 의존) | 비교용 신뢰 가능. 날짜·시각 조건 명기 필수 |
| 일광(VSC) | CIE 담천공, 수직면 무장애 ≈ 40%, 기준 27/15/5% [T2v AU2021 핸드아웃] | 없음 | 「잠재력 지표」. 창 크기·실 기능 미반영을 핸드아웃이 명시 |
| 소음 rapid | 「수만 건 시뮬레이션으로 학습한 신경망, educated guess」(Renaud Danhaive, 2023-07-03) [T2v] https://blogs.autodesk.com/forma/2023/07/03/game-changing-rapid-noise-analysis-comes-to-forma-2/ | Dan Stine 2024-11-25: 샌안토니오 고속도로변 1지점 Apple Watch 비교, 「약 72 dB로 보임」. 입력 ADT 80k vs TxDOT 150k+ 불일치, 측정값 미기재 → **비통제 일화** [T4] https://bimchapters.blogspot.com/2024/11/autodesk-forma-noise-analysis-ground.html | 탐색용. 계산 표준(Nord2000/CNOSSOS 여부) **확인 대기**(도움말 로그인 필요) |
| 소음 detailed(Beta→정식) | 「부지별 환경 데이터, 수 분, 정확한 계산」 [T2v] | 없음 | 법정 검토는 별도 소프트웨어(ARCO 사례의 Promethor 참여) |
| 바람 rapid | 「사용 데이터로 지속 재학습, detailed 실행 시 surrogate 비교로 검증」(Autodesk 직원, 포럼, 약 2024년) [T4] https://forums.autodesk.com/t5/forma-for-design-forum/machine-learning-dataset/td-p/12813948 ; 제품 페이지 「full-scale 분석과 비교 가능한 정확도」 [T2v, 미계량] | 없음 | **검증 없는 마케팅 주장**(정확도 「comparable」) |
| 바람 detailed(CFD) | 30~90분 클라우드 [T4 BIM Chapters] ; 학습 페이지 「여러 공학 레퍼런스로 벤치마크」(403, 내용 미확인) | 없음 | 보행자 쾌적성(Lawson 등) 기준 적용 여부 확인 대기 |
| 미기후(UTCI) | 일조·일광·바람·기상 결합 | 없음 | 비교용 |
| 내재탄소 | ML, 미국계 데이터(02 조사) ; Stantec 「5~10초/회」 | 없음 | 한국 자재 DB 미반영 → 수치 인용 불가 |

---

## 7. 북미·기타 지역 사례 — 미기후·탄소·업무시설

### 7.1 HMC Architects — 캘리포니아 커뮤니티칼리지 STEM 센터 제안(4주)
출처: Autodesk Forma 블로그 2025-12-04 https://blogs.autodesk.com/forma/2025/12/04/design-for-good-forma-site-design-and-hmc-architects/ [T2v]

| 칸 | 내용 |
|---|---|
| 설계 질문 | 더운 여름 기후에서 RFP가 지정한 일자형(Bar) 매스가 정말 최선인가 |
| 수집 데이터 | 자동 컨텍스트, 기존 HVAC 소음원, 캘리포니아 태양광 요건 |
| 분석 방법·도구 | 일조(여름 그늘·겨울 일사), 일광·남향 노출, 바람 쾌적성·풍동, 미기후(표면·대기 온도), HVAC 소음, 태양광 발전 |
| 바뀐 설계 결정 | **Bar·Square·Courtyard 3안 비교 → RFP의 Bar 대신 U형 Courtyard 권고** |
| 결과·검증 여부 | 「Courtyard가 여름 일조 분석에서 기준선보다 40% 더 시원」(기준선 정의 없음), 「남향 일사 33% 증가」, 팀 6명→2~3명, 「수일→수분」 → **자체 수치, 기준선 미정의** → 검증 없는 주장. 당선 여부 미보고 |
| 구경주역 교훈 | 「발주처가 지정한 형태를 데이터로 뒤집는다」는 구조는 **2026.01 결정도의 가구·획지를 100% 변경 가능한 참고로 보는 우리 전제**(CLAUDE.md §2)와 같습니다. 3안 비교 형식(지정안·대안·권고안)을 심의 자료 틀로 채택할 수 있습니다 |

### 7.2 Stantec — 밴쿠버 TOD, 20개 이상 타워, 내재탄소
출처: Autodesk Forma 블로그 2025-08-22(AU 2024 「From Concept to Carbon」 기반) https://blogs.autodesk.com/forma/2025/08/22/stantec-forma-case-study-how-to-reduce-embodied-carbon/ [T2v]

| 칸 | 내용 |
|---|---|
| 설계 질문 | 상업 인필 부지의 복합 TOD(주거·상업·호텔)에서 구조 방식 변경이 내재탄소를 얼마나 줄이는가 |
| 수집 데이터 | 기준안: 하이브리드 콘크리트, GFRC 외장, 창면적비 50% |
| 분석 방법·도구 | Forma 내장 내재탄소 계산(5~10초/회), 매스·높이는 일광·일조 조건에 맞춰 조정. 초심자 팀이 1.5시간에 반복 |
| 바뀐 설계 결정 | **가장 낮은 3개 타워(사무·주거·호텔)를 매스팀버로 전환** |
| 결과·검증 여부 | 723,000 → 681,000 tCO2(−42,000), 평균 강도 409 → 394 kg/㎡ [T2v, 단위 metric 여부 미기재]. 시스템 경계·데이터 소스 미기재 → **방법 불투명** |
| 구경주역 교훈 | 「단계별 비가역 투자는 뒤로」(CLAUDE.md §5-3)와 연결됩니다. 구경주역의 저층(역사문화환경 고도 제한 아래) 공공·문화 건물을 **목구조 대안**으로 두고 비교하는 것은 가능하나, Forma 탄소값은 미국 DB라 **한국 수치로 인용 불가**. 국내 LCA(국토부 건축물 LCA 평가 프로그램 등)로 재산정 |

### 7.3 Continental Automotive — 약 55개 공장 부지, 연 37건 타당성 검토
출처: Autodesk Forma 블로그 2024-09-20 https://blogs.autodesk.com/forma/2024/09/20/continental-automotive-planning-factory-sites-for-future-success/ [T2v]

「North Star」 단계별 마스터플랜을 Forma로 3D 시나리오화, 사무·주차·일광·생산·창고 확장 여지, 동선(작업자·자재·완제품) 검토, **확장 시 철거해야 할 태양광 배치를 회피**. 「1주 → 1일」(Daniel Zambori) → 자체 보고. 구경주역 교훈: **단계별 개발(phasing) 시나리오를 3D로 비교**한 유일한 Forma 사례입니다. 다만 Forma에는 최적 순서를 푸는 기능이 없고 사용자가 시나리오를 손으로 만듭니다 → 우리 MILP(CP-SAT) 단계화가 우위이며, Forma는 그 결과의 시각화에 씁니다.

### 7.4 Arcadis + ArcGIS — 복원력 설계 4가지 전환
출처: Autodesk Forma 블로그 2025-09-18 https://blogs.autodesk.com/forma/2025/09/18/designing-resilient-communities-arcadis-data-driven-approach-with-forma-and-arcgis/ [T2v]; 2024-07-03·2023-11-13 Arcadis 글 [T2v]

ArcGIS 「권위 레이어」(조닝·대중교통·공공공간·조망축 view cones)를 Forma 3D 모델에 결합. 전환 ① 복원력을 초기 단계로 ② **맥락별 KPI 설정** ③ 2D 지도 → 실데이터 3D ④ 환경·공간 데이터 결합. 프로젝트·수치 없음. 구경주역 교훈: 우리 EPSG:5187 처리본(지적·용도지역·고도지구·역사문화환경 허용기준·매장문화재 유존지역)을 **ArcGIS/GeoJSON 레이어로 Forma에 얹는 경로**(02 조사의 Integrate API)가 이 사례의 실무 형태입니다. 「조망축」 레이어는 향일문 조망로(8 m 보행로, work/20261011_masterplan_rough)와 대응합니다.

### 7.5 UTA 학생 스튜디오 — 사우스 다운타운 댈러스 15분 도시(Arcadis 공동 지도)
출처: Autodesk Forma 블로그 2026-04-22 https://blogs.autodesk.com/forma/2026/04/22/designing-with-data-rethinking-south-downtown-dallas-as-a-15-minute-city/ [T2v]

댈러스 GIS·조닝 레이어를 ArcGIS 연동으로 반입, 소음(rapid)·미기후·바람·일조·일광·그림자·**근접성(proximity, 15분 도보)** 분석. 결정: 대형 건물을 음향 차폐로, 그늘진 보행로·광장, 조용한 중정, I-30 상부 공원, 막다른 길 제거. 「그늘 전략으로 103°F → 약 92°F」(여름 최성기) [T2v, 학생 산출]. 구경주역 교훈: 「대형 매스 = 음향 차폐」와 「막다른 길 제거」는 선형 축 연속성(§5-8)과 같은 원칙이고, 근접성 분석은 우리 S2 보행권(반경 1 km) 지표와 겹칩니다.

### 7.6 Project Phoenix(웨스트 오클랜드, 316세대 어포더블), Lake|Flato(1920년 건물 적응재사용), Baker Barrios(40시간→4시간), Jacobs·Stantec 두바이, HNTB 공항, Drees & Sommer 데이터센터, SSOE 멕시코 공장, Gray Puksand, Scott Shields — 결정 변경 또는 수치가 없거나 근거 없음
- Project Phoenix: 「통상 사업의 절반 비용·시간·탄소」 — 기준선·방법 없음 → **검증 없는 마케팅 주장** [T2v 2023-11-24]
- Lake|Flato: 311 Third St.(1920년, 22,545 sq ft) 적응재사용에 바람·미기후 분석 사용, 결정 변경 미기재 [T2v 2023-11-24]. 구경주역의 등록문화유산 구 역사(존치) 주변 미기후 검토에 형식만 참고
- Baker Barrios: 「40시간 → 4시간 이하」 — 어떤 작업인지 블로그 요약판에 없음 → **검증 없음** [T2v 2024-06-04]
- Stantec 두바이 암병원: 바람·일조·내재탄소로 차양·LEED Gold 정렬, 수치 없음 [T2v 2025-10-22]

---

## 8. 아시아 적용 사례 — 한국 유무 포함

### 8.1 한국 — 공개 사례 없음(확인 대기)
- 검색: 한국어 3회(「오토데스크 포르마/포마 국내 사례」, 「삼우·희림·정림·해안·GS건설·LH·서울시 + Forma」, 「국내 도입 사례 2025 2026 후기」), 영어 1회. **설계사·대학·공공기관의 Forma 적용 사례를 찾지 못했습니다.**
- 확인된 것: Autodesk 한국 제품 페이지 https://www.autodesk.com/kr/products/forma/overview [T2v], 소규모 건축사사무소 대상 Forma 웨비나 안내(allshowtv.com, 일조·조망·바람 초기 분석 소개) [T4] https://www.allshowtv.com/detail.html?idx=1617, Autodesk 한국어 기사 「AI가 건축 설계를 변화」 [T2v]. AU 한국어 강의는 InfraWorks 도시 마스터플랜 사례(Forma 아님).
- 함의: 한국 건축법 정의(용적률·건폐율·일조권 사선·정북 방향 일조)와 Forma 기본 규칙의 일치 여부를 보여주는 국내 선례가 없으므로, **우리가 하는 적용이 공개 선례 1호**가 될 가능성이 있습니다. 02 조사의 「Area metrics 사용자 정의 규칙」과 아래 JR東日本建築設計의 Dynamo 사선 도구가 유일한 참고입니다.

### 8.2 일본 — 日建設計(Nikken Sekkei), Rhino–Forma 연동(2023)
출처: Autodesk Forma 블로그 2023-11-13 https://blogs.autodesk.com/forma/2023/11/13/nikken-sekkei-the-idea-is-to-find-more-ways-to-help-us-achieve-our-sustainability-goals/ [T2v]

| 칸 | 내용 |
|---|---|
| 설계 질문 | 3,000명 규모 설계사가 2050 넷제로 목표 아래 초기 매스(형태·볼륨·향)를 더 많이 반복 검토할 수 있는가 |
| 수집 데이터 | Rhino 복잡 형상 → Forma(베타 플러그인) |
| 분석 방법·도구 | 일조(sun hours), rapid 바람, 소음, 태양광, 운영에너지 |
| 바뀐 설계 결정 | 미기재(TOKYO SKYTREE·Suzhou Modern Media Plaza·One Za'abeel는 캡션 사진만) |
| 결과·검증 여부 | 수치 없음. Kevin Walsh(도쿄 건축가) 「Forma가 오류 위험을 줄인다」「첫날이 가장 큰 실수가 나는 때」 |
| 구경주역 교훈 | Rhino 사용자인 우리에게 **Rhino → Forma → Rhino 왕복** 선례. 일본 규제·기상 데이터 문제는 다루지 않음 |

### 8.3 일본 — JR東日本建築設計(JRE設計), 신주쿠역 주변(AU 2025 고객 세션)
출처: 建設ITワールド 「JR東日本建築設計が挑む都市環境DX！ Revit×Formaによる解析から設計者が最適解を導く時代へ」 2025-12-16, https://ken-it.world/success/2025/12/revitxforma-in-jred.html [T4, Autodesk 제공 성공 사례 기사]

| 칸 | 내용 |
|---|---|
| 설계 질문 | 11개 노선·1일 약 350만 명 승하차 역세권에서 의장 설계자가 초기 단계에 환경 영향(일영·풍·지표온도·LCA)을 스스로 검증할 수 있는가 |
| 수집 데이터 | **PLATEAU(국토교통성 3D 도시모델, CityGML LOD2)** 를 Forma에 통합해 풍해석, Revit BIM, Dynamo |
| 분석 방법·도구 | ① 자체 Dynamo 도구 **JDLT(JRED Diagonal Line Tool)** 로 건축기준법 **도로사선·인지사선을 자동 생성해 볼륨 제약으로 반영**, Forma에서 **건폐율·용적률 동시 검증** ② 풍향별 풍환경(Forma 표준 모델 vs PLATEAU 모델 비교) ③ 계절·시각별 지표온도 ④ 구조 형식(목조 vs 철골) LCA 비교 ⑤ 일영 |
| 바뀐 설계 결정 | 「형상 개선 → 재해석 사이클이 당일 완결」, 해석 대기 시간을 최적화에 투입. 구체 배치 변경·LCA 수치는 기사에 없음 |
| 결과·검증 여부 | 리드타임 **1/3**, 비교안 수 **10배**, 초기안 작성 「수일 → 단시간」(二ノ宮正行·広瀬菜摘, 기술본부 IT추진부) → 자체 보고. **PLATEAU 모델 사용 시 Forma 표준 모델과 외부 기류 분포가 달랐다**는 결과가 명시됨 → 컨텍스트 모델 선택이 분석 결과를 바꾼다는 드문 증거 |
| 구경주역 교훈 | 가장 직접적인 아시아 선례입니다. ① **규제 사선을 외부 도구(Dynamo)로 생성해 Forma에 제약으로 넣는 방식**은 우리 `gjplan/constraints` buildable 마스크(고도지구·역사문화환경 허용기준 높이)를 Forma에 반입하는 경로와 같습니다 ② 「표준 OSM 컨텍스트 vs 국가 3D 모델」의 결과 차이는 한국에서 **V-World 3D 건물·국토지리정보원 DEM을 반입해야 하는 이유**를 보여줍니다(02 조사 §2.1) ③ Forma가 일본 규칙에 「대응하고 있는 중」이라는 표현 — 한국 규칙은 그 이전 단계임 |

### 8.4 일본 — AU 2025 「Democratizing Environmental Simulations and Urban Design in Japan」
출처: AU 2025 강의 초록(2025-09-16) https://www.autodesk.com/autodesk-university/class/Unlocking-the-Future-of-Architectural-Design-with-Forma-Democratizing-Environmental-Simulations-and-Urban-Design-in-Japan-2025 [T2v, 발표자·회사 **미확인**(403)]
- 주장: 도입 프로젝트 **+400%**, 시뮬레이션 다양성 **10배**, 비용 **−80%**; 일본 규제용 라이브러리·워크플로 커스터마이징으로 도입 **+300%**, 초기 산출 리드타임 **1/3 단축**. 학습 목표에 「경쟁 소프트웨어 대비 장단점」「정량화를 통한 초기 합의 형성」 포함.
- 판정: 기준선·방법 없음 → **검증 없는 마케팅 주장**. 「리드타임 1/3」이 §8.3 JRE設計 수치와 같아 동일 발표일 가능성 있음 [가정, 확인 대기].

### 8.5 싱가포르 — RSP, NUS Sustainability & Resilience Building 공모(2위)
출처: Autodesk Forma 블로그 2024-12-06 https://blogs.autodesk.com/forma/2024/12/06/rsp-uses-formas-sustainability-analyses-to-shape-the-design-of-healthy-learning-environments/ [T2v]

| 칸 | 내용 |
|---|---|
| 설계 질문 | 고온다습 열대 기후에서 BCA Green Mark Platinum을 목표로 옥외 열쾌적·도시열섬·교통 소음을 동시에 다루는 교육 건물 |
| 수집 데이터 | 자동 컨텍스트, Rhino·Revit·SketchUp 왕복 |
| 분석 방법·도구 | 일광 잠재력(교실 vs 차양 루버), 일조·태양광(지붕·파사드 패널), 바람(주풍향 정렬), 소음(교통), 옥외 열쾌적·냉각 |
| 바뀐 설계 결정 | **건물 볼륨을 주풍향에 정렬**, 수공간·수목으로 증발 냉각, 지붕·파사드 패널 각도 최적화, 셋백 추가, **가장 노출된 파사드에 공용공간을 두어 실험실 완충**, 차음 재료 |
| 결과·검증 여부 | 볼륨 스터디 시간 **−70%**, 에너지 **+6% 생산(지붕 84%·파사드 16%)**, 에너지 플러스 → 자체 수치, 방법 없음. 공모 2위(미건립) |
| 구경주역 교훈 | 「노출 파사드에 공용공간을 두어 민감 공간을 완충」은 ARCO·Cobe와 같은 완충 원칙의 **용도 배분 버전**입니다. 구경주역 북측 획지에서 원화로 쪽 1~2층을 상업·공용으로, 주거는 안쪽으로 두는 단면 조닝(work/20261015 단면 조닝 메모)의 근거 사례 |

### 8.6 태국 — Architects 49(A49), Forma API 조닝 규정 실시간 검증 플러그인
출처: Autodesk Forma 블로그 2024-09-06 https://blogs.autodesk.com/forma/2024/09/06/discover-a49s-custom-plug-in-for-autodesk-forma-that-validates-code-compliance-in-real-time/ [T2v]

A49가 **자사 서버의 조닝 규정을 Forma API로 연결**해 건물 바닥·볼륨·오픈스페이스·면적 효율을 조정하는 동안 규정 준수를 실시간 검증. 「수일 → 수초」. 어떤 규정(셋백·FAR·OSR·높이·도로폭)인지, 적용 프로젝트는 요약판에 없음. 구경주역 교훈: **규제 판정을 Forma 밖(자체 서버)에서 수행해 Forma에 표시**하는 구조로, 우리 `constraints/compile.py` → Forma Extension 표시 경로의 선례입니다. 규제 4겹을 Forma 내부 기능이 아니라 **우리 코드**가 판정해야 한다는 02 조사 결론과 일치합니다.

### 8.7 중동·기타 아시아 — Jacobs(두바이, 2024-12-03 영상), Stantec 두바이 암병원(§7.6), 중국·대만·홍콩: 사례 없음
중국어 검색에서 Forma 적용 프로젝트는 확인되지 않았고, Ladybug/Rhino 기반 일조·풍환경 자료만 나왔습니다. 확인 대기.

---

## 9. Forma가 잘하는 결정 / 못 하는 결정

| 구분 | 결정 | 사례 근거 | 구경주역에서의 담당 |
|---|---|---|---|
| **잘하는 결정** | 소음원 쪽 매스 형태 선택(폐쇄형·선형·엇갈림) | ARCO, Cobe, Oramai, Malmö, PKA | Forma 비교 → 추적표 기록 |
| | 일조가 확보되는 쪽의 층수 추가·세대 추가 여부 | ARCO +20세대, AFRY 100→108, BPD +22% | Forma 비교(고도 상한은 buildable 마스크가 먼저 자름) |
| | 중정 폭·건물 높이 ↔ 중정 지면 일조 | Bergen Dokken, Vantaa, NREP 0→6h | Forma 비교, 분석 날짜·시각 명기 |
| | 도로·광장 위치를 음영/양지에 맞추기 | Cobe Vridsløse | Forma 일조 → 저차원 도로 배치 규칙 |
| | 판상 매스 사이 풍속 증가(Venturi)·보행자 풍쾌적 확인 | Bouygues, Oramai, BPD, RSP | Forma rapid → detailed 1회 검증 |
| | 완충 용도 배분(노출면에 공용·상업, 안쪽에 주거·민감 공간) | RSP, ARCO | 단면 조닝에 반영 |
| | 지자체·주민·심의 대상 「전·후 비교 지도」 | PKA, BPD, Rødovre, Malmö | 심의 자료 표준 형식 |
| | 지정된 형태(RFP·결정도)를 대안 3안 비교로 재검토 | HMC, NREP | 결정도 vs 대안 비교 |
| | 전 이해관계자가 한 3D 모델에서 워크숍 | NREP UN17, Økern, Rødovre | 경주시–공단–설계사 워크숍 |
| | 복수 부지 1차 스크리닝 | T2H 70부지/4개월 | 폐역 17개소 S3 스크리닝 |
| **못 하는 결정** | 규제 4겹(용도지역·고도지구·역사문화환경 허용기준·지구단위계획) 판정 | A49가 외부 서버로, JRE設計가 Dynamo로 해결 — Forma 내부 기능 없음 | `gjplan/constraints` buildable 마스크 |
| | 홍수·우수·지반·토양오염·매장문화재 제약 | AFRY: 홍수는 외부 조사 | 외부 조사 → 마스크 |
| | 가로·공공공간 구조를 먼저 설계하는 순서 | Sourek 2024: 「지원도 허용도 않음」, 도로 수동 입력 | 사람이 먼저 긋고(선형 축 연속성), 그 뒤 Forma |
| | 가구·획지 분할, 면적표·획지별 용도 결정 | 모든 사례가 매스 수준에서 끝남 | `gjplan/generate` + `export`(면적표 합계 검증) |
| | 주거 외 용도(상업·공공·문화·모빌리티) 생성 | Harvard D3: 다세대 주거만 지원 | 규칙기반 생성 |
| | 다목적 트레이드오프의 파레토 전선 제시 | 「밀도 +16%·조망 +33%」식 단일 결과만 | NSGA-III 전선 → 대안 A~E |
| | 단계별 개발순서 최적화 | Continental: 시나리오 수동 작성 | MILP(CP-SAT) |
| | 생성 파라미터의 추적·재현 | Site Automation 파라미터 비공개 | 추적표 |
| | 법정 검토용 소음·풍·일조 수치 | rapid = 「educated guess」, ARCO는 별도 음향 컨설턴트 | 전문 소프트웨어·실측 |
| | 한국 컨텍스트·자재 데이터의 정확도 | OSM·ASTER 30m 기본, 탄소 DB 미국계; JRE設計의 PLATEAU 차이 | V-World·DEM 반입, 국내 LCA |
| | 야간 활동·생활업종·정주 지표(CLAUDE.md §5-6) | 어떤 사례도 측정하지 않음 | 우리 목적함수 f(거주·생활·야간) |
| | 전례 없는 배치(분산 삽입형) 제안 | echo chamber 비판 | 사람 + 규칙기반 대안 |

---

## 10. 구경주역 적용 설계 — 선례가 지정하는 Forma의 자리

1. **순서**: 가로·공원·조망로(향일문 8 m 보행로)·횡단축을 사람이 먼저 긋고 buildable 마스크로 자른 뒤, Forma에는 **매스 대안만** 올립니다(Sourek 2024, Cobe, CLAUDE.md §5-2·§5-8).
2. **대안 수**: 심의용 3안(결정도 재현안·NSGA-III 대표안·권고안) + 분산 삽입형 1안. HMC·Oramai의 3안 비교 형식.
3. **분석 조건표 공개**: 일조(동지·춘추분, 09–15시), 일광(VSC 27/15/5%), 소음(원화로 설계속도·ADT 출처, 폐선 철도는 0), 바람(경주 기상관측소 풍배도, 겨울 북서풍), 미기후(여름 UTCI). NREP·HMC 사례의 「기준선 없음」 결함을 피하는 장치.
4. **전·후 비교 지도 세트**: 결정도(2026.01) vs 각 대안의 소음·일조·VSC 지도(PKA·BPD 형식) — 성동동 인접 저층 주거에 대한 추가 그림자·풍속 변화 포함.
5. **완충 원칙**: 원화로·북측 간선 쪽에 폐쇄형·선형 상업·공공 매스, 안쪽에 주거(청년·신혼 600세대) 중정형 — ARCO·Cobe·RSP.
6. **컨텍스트 반입**: V-World 3D 건물·국토지리정보원 DEM·지적을 EPSG:5187 → UTM 52N 변환해 반입(JRE設計의 PLATEAU 교훈, 02 조사).
7. **규제 표시**: `constraints/compile.py` 결과(높이 상한면·유존지역·보존지역)를 Forma에 지형·제약 레이어로 올려 **표시만** 하고 판정은 코드가 합니다(A49·JRE設計).
8. **인용 규칙**: 공모 대응·지구단위계획 문서에는 Forma 사례의 **수치를 쓰지 않고** 결정 유형(완충 매스·양지 공공공간·중정 일조)만 선례로 적습니다. Forma 분석값은 「탐색용」으로 표기하고 법정 검토값은 전문 소프트웨어·실측으로 대체합니다.
9. **운영 효과 근거**: Forma 도입의 정당성은 Kolbjørnsrud & Sannes(2022)의 과정 효과(반복·조기 평가·참여)로 쓰고, 설계 품질은 우리 5개 목적함수 측정값으로 증명합니다.

---

## 11. 미해결 질문·확인 대기

| 번호 | 항목 | 필요한 조치 |
|---|---|---|
| 1 | Steen & Strøm/Storebrand Økern 「가장 소음 심한 파사드 10% 감소」 원문 | spacemakerai.com SSL 오류 → 브라우저 수동 접속 또는 Wayback |
| 2 | Kolbjørnsrud & Sannes(2022) 본문: 대상 회사(OBOS·Nordr vs 3개사), 방법, 한계 절 | DOI 10.18261/pof.38.1.4 기관 접속 |
| 3 | Istanbul 북챕터(ScienceDirect) 저자·서명·수치 출처 | 도서관 접속 |
| 4 | Forma 소음 계산 표준(Nord2000/CNOSSOS-EU/기타), 바람 쾌적성 기준(Lawson/NEN 8100) | help.autodeskforma.com 로그인 열람 |
| 5 | AU 2025 일본 세션 발표 회사·JRE設計 동일성 | AU 로그인 후 강의 페이지·핸드아웃 |
| 6 | AU 2024 NOVA PROJEKT(폴란드) 「좌표계·DXF 미지원, 결과는 근사치」 상세와 AutoCAD Map 3D 우회 절차 | AU 로그인 |
| 7 | AFRY·ARCO·BPD의 autodesk.com 전체 사례문(403) 및 PDF | 브라우저 수동 열람 |
| 8 | T2H·NREP 「6% 세대 증가」가 어느 프로젝트인지 | NREP 보도자료 원문 |
| 9 | Forma 분석값 vs Radiance·CFD·실측 비교 연구 존재 여부(동료심사) | Scopus·Google Scholar 재검색(「Forma」 「validation」 「VSC」 「Lawson」) |
| 10 | 한국 적용 사례(설계사·대학·LH·지자체) | Autodesk Korea 파트너·학회(대한건축학회·도시설계학회) 발표 검색 |
| 11 | Rebild(덴마크) 「1년 단축」 원문 | rebild.life 재접속 |
| 12 | Medium Voss 개념안 상세 | 수동 접속 |

---

## 12. 출처 목록(확인일 2026-10-24)

### 업체 공식 사례·발표 [T2v]
- Autodesk Forma 블로그 Customer Stories 카테고리: https://blogs.autodesk.com/forma/category/customer-stories/ (1~5쪽)
- ARCO Malmi 2023-05-08: https://blogs.autodesk.com/forma/2023/05/08/how-arco-used-formas-data-driven-insights-to-transform-a-challenging-urban-site-into-valuable-student-housing/
- PKA 2023-05-08: https://blogs.autodesk.com/forma/2023/05/08/forma-contributes-to-pkas-competition-wins/
- Patriarche 2023-05-08: https://blogs.autodesk.com/forma/2023/05/08/how-forma-enhances-patriarches-augmented-architecture/
- Rødovre 2023-06-22: https://blogs.autodesk.com/forma/2023/06/22/rodovre-first-danish-municipality-to-collaborate-with-forma/
- BPD 2023-07-04: https://blogs.autodesk.com/forma/2023/07/04/bpd-when-you-can-show-that-a-certain-density-is-viable-the-municipality-is-open-to-discussing-it/
- Oslo 「city within a city」 2023-08-17: https://blogs.autodesk.com/forma/2023/08/17/the-city-within-a-city-taking-shape-in-oslo/
- Nikken Sekkei 2023-11-13: https://blogs.autodesk.com/forma/2023/11/13/nikken-sekkei-the-idea-is-to-find-more-ways-to-help-us-achieve-our-sustainability-goals/
- Project Phoenix 2023-11-24: https://blogs.autodesk.com/forma/2023/11/24/how-project-phoenix-fulfils-their-sustainability-and-business-goals/
- Lake|Flato 2023-11-24: https://blogs.autodesk.com/forma/2023/11/24/living-the-dream-lakeflatos-adaptive-reuse-project-to-repurpose-their-100-year-old-workspace/
- AFRY 2024-01-26: https://blogs.autodesk.com/forma/2024/01/26/afry-uses-autodesk-forma-for-sweden-city-planning/ ; PDF https://damassets.autodesk.net/content/dam/autodesk/www/pdfs/afry-uses-autodesk-forma-for-sweden-city-planning-001.pdf
- Nordic municipalities 2024-04-23: https://blogs.autodesk.com/forma/2024/04/23/nordic-municipalities-embracing-data-driven-urban-planning/
- Baker Barrios 2024-06-04: https://blogs.autodesk.com/forma/2024/06/04/how-baker-barrios-architects-made-dramatic-business-gains-with-forma/
- Weston Williamson 2024-07-17: https://blogs.autodesk.com/forma/2024/07/17/weston-williamsons-approach-to-outcome-based-design-with-autodesk-forma/
- A49 2024-09-06: https://blogs.autodesk.com/forma/2024/09/06/discover-a49s-custom-plug-in-for-autodesk-forma-that-validates-code-compliance-in-real-time/
- Continental 2024-09-20: https://blogs.autodesk.com/forma/2024/09/20/continental-automotive-planning-factory-sites-for-future-success/
- RSP 2024-12-06: https://blogs.autodesk.com/forma/2024/12/06/rsp-uses-formas-sustainability-analyses-to-shape-the-design-of-healthy-learning-environments/
- Site Automation 2025-04-24: https://blogs.autodesk.com/forma/2025/04/24/how-to-use-generative-design-ai-and-3d-modeling-for-improved-site-planning/
- Stantec 내재탄소 2025-08-22: https://blogs.autodesk.com/forma/2025/08/22/stantec-forma-case-study-how-to-reduce-embodied-carbon/
- Arcadis + ArcGIS 2025-09-18: https://blogs.autodesk.com/forma/2025/09/18/designing-resilient-communities-arcadis-data-driven-approach-with-forma-and-arcgis/
- Stantec 두바이 2025-10-22: https://blogs.autodesk.com/forma/2025/10/22/how-stantec-used-formas-sustainability-analyses-to-improve-building-performance-and-patient-wellbeing/
- Sweco Design Slam 2025-12-01: https://blogs.autodesk.com/forma/2025/12/01/serious-fun-data-driven-design-hits-the-right-notes/
- HMC Architects 2025-12-04: https://blogs.autodesk.com/forma/2025/12/04/design-for-good-forma-site-design-and-hmc-architects/
- UTA Dallas 2026-04-22: https://blogs.autodesk.com/forma/2026/04/22/designing-with-data-rethinking-south-downtown-dallas-as-a-15-minute-city/
- Oramai Studio 2026-09-28: https://blogs.autodesk.com/forma/2026/09/28/how-oramai-studio-creates-space-to-explore-beyond-the-first-sketch-idea/
- Rapid wind 2023-06-06: https://blogs.autodesk.com/forma/2023/06/06/formas-rapid-wind-analysis-offers-instant-insights-into-wind-conditions/
- Rapid noise 2023-07-03: https://blogs.autodesk.com/forma/2023/07/03/game-changing-rapid-noise-analysis-comes-to-forma-2/
- T2H 사례집 PDF(2021-09): https://damassets.autodesk.net/content/dam/autodesk/www/pdfs/adk_21123_sm_customerstory_r2(1)(3)-1.pdf
- AU 2021 핸드아웃 AS500351(Gameiro): https://static.au-uw2-stg.autodesk.com/Class_Handout_AS500351_ClassHandout-AS500351-Gameiro-AU2021.pdf
- AU 2024 NOVA PROJEKT: https://www.autodesk.com/autodesk-university/class/SMART-Implementation-of-Autodesk-Forma-in-an-Architectural-Office-as-a-Game-Changer-2024 (403, 스니펫)
- AU 2024 「Leveraging Autodesk Forma to Expand the Understanding of Context and Development」: https://www.autodesk.com/autodesk-university/class/Leveraging-Autodesk-Forma-to-Expand-the-Understanding-of-Context-and-Development-2024 (403, 스니펫)
- AU 2025 「Early Design Wins」: https://www.autodesk.com/autodesk-university/class/Early-Design-Wins-How-We-Used-Forma-to-Accelerate-Sustainable-Urban-Planning-2025 (403, 스니펫)
- AU 2025 Japan: https://www.autodesk.com/autodesk-university/class/Unlocking-the-Future-of-Architectural-Design-with-Forma-Democratizing-Environmental-Simulations-and-Urban-Design-in-Japan-2025
- Autodesk 인수 완료 보도자료 2020-11-24(Nasdaq 전재): https://www.nasdaq.com/press-release/autodesk-completes-acquisition-of-spacemaker-provider-of-ai-and-generative-design
- Building Layout Explorer: https://adsknews.autodesk.com/en/news/building-layout-explorer-in-autodesk-forma/
- Autodesk 한국 제품 페이지: https://www.autodesk.com/kr/products/forma/overview

### 학술 [T3]
- Kolbjørnsrud & Sannes (2022) Praktisk Økonomi & Finans 38(1): https://doi.org/10.18261/pof.38.1.4 (원문 미확인) ; BI 프로필 https://www.bi.no/en/about-bi/employees/department-of-strategy-and-entrepeneurship2/vegard-kolbjornsrud/ ; SSE 세미나 2023-01-24 https://www.hhs.se/en/about-us/calendar/hoi-events/2023/24-jan-2023---research-seminar-vegard-kolbjornsrud
- Sourek (2024) Architectural Intelligence 3:4: https://doi.org/10.1007/s44223-023-00046-9 ; PDF https://papers.cumincad.org/data/works/att/architectural_intelligence2024_4.pdf
- Harvard D3 (2021-04-21): https://d3.harvard.edu/platform-digit/submission/spacemaker-merging-ai-technology-with-urban-planning-and-design/
- Istanbul 북챕터: https://www.sciencedirect.com/science/article/abs/pii/B978012823941400010X (원문 미확인)
- MDPI Buildings 2026 16(4):685: https://www.mdpi.com/2075-5309/16/4/685
- Springer Architectural Research 2026 28:4: https://link.springer.com/article/10.1007/s44515-026-00006-0 (접속 불가)

### 언론·블로그·2차 [T4]
- Estate Nyheter 2017-10-12: https://www.estatenyheter.no/aktuelt/vil-revolusjonere-eiendomsbransjen/227702
- Realtid 2020-12-15(NREP): https://www.realtid.se/nrep-tar-hjalp-av-spacemaker-ai-att-bygga-mer-hallbart
- casestudies.com NREP: https://www.casestudies.com/company/spacemaker/case-study/nrep-pioneers-artificial-intelligence-in-real-estate-using-spacemaker
- casestudies.com DigiGrow: https://www.casestudies.com/company/spacemaker/case-study/spacemaker-successfully-trialled-to-help-municipalities-innovate-during-digigrow-pilot
- casestudies.com Bouygues Immobilier: https://www.casestudies.com/company/spacemaker/case-study/how-spacemaker-is-helping-bouygues-immobilier-design-more-efficient-sustainable-projects
- Spacemaker 블로그 Steen & Strøm/Storebrand 2021-03-26: https://www.spacemakerai.com/blog/how-steen-strom-and-storebrand-use-spacemaker-for-site-development (SSL 오류)
- Dezeen Cobe 2022-05-31(Partnership content): https://www.dezeen.com/2022/05/31/cobe-spacemakers-ai-software/
- Dezeen UN17 Village 2018-12-10: https://www.dezeen.com/2018/12/10/un17-village-eco-housing-copenhagen-lendager-group-arstiderne-arkitekter/
- AEC Magazine Rødovre 2023-02-24: https://aecmag.com/concept-design/danish-municipality-adopts-autodesk-spacemaker/
- Symetri Explore 2023-03-01: https://symetri.co.uk/insights/blog/ai-and-generative-urban-design-you-can-start-using-today-with-spacemaker
- BIM Chapters 소음 실측 2024-11-25: https://bimchapters.blogspot.com/2024/11/autodesk-forma-noise-analysis-ground.html
- Autodesk 포럼 ML dataset(직원 답변): https://forums.autodesk.com/t5/forma-for-design-forum/machine-learning-dataset/td-p/12813948 (403, 스니펫)
- Studio Matrx 2026-09: https://www.studiomatrx.org/students/ai-assisted-design-workflows/forma-spacemaker-and-early-design
- Levery 2026-03: https://www.levery.it/insights/ai-03-26/
- 建設ITワールド JRE設計 2025-12-16: https://ken-it.world/success/2025/12/revitxforma-in-jred.html
- Medium Voss(Arne Bassøe-Eriksen): https://medium.com/@arne.bassoeeriksen/how-i-put-my-assumptions-for-an-urban-concept-to-test-with-spacemakers-ai-platform-b97aa7493e0c (403)
- rebild.life: https://www.rebild.life/plan-the-municipality-growth-using-ai-and-save-1-year-of-the-plannig-process/ (503)
- allshowtv 한국 웨비나 안내: https://www.allshowtv.com/detail.html?idx=1617
