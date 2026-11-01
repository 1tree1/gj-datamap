# 과제 A — 'Intelligent Urban Development Modelling'(CityFinder) 출처 식별과 해부

작성 2026-10-06. 코디네이터 지시(마감 임박)에 따라 이미 열어 본 원문만으로 마무리했다. 새 검색은 하지 않았다.

**범례** — 등급: T1 법정 · T2 공공발간(국책·공공기관 보고서, CORDIS 등) · T3 학술 · T4 언론·회사 자료·벤더·위키.
확인 상태: **[확인]** 원문 텍스트를 직접 열람(PDF 텍스트 추출 또는 원문 HTML) / **[확인·요약]** 원문 URL을 열었으나 WebFetch 요약기를 거쳐 받음(수치는 재확인 권장) / **[스니펫]** 검색결과 요약만 봄 / **[추정]** 근거로부터의 추론 / **[미확인]**.
표기: 원문 직접 인용은 문서 전체에서 Oreskes 1994 한 문장뿐이고 나머지는 모두 바꿔 쓴 요약이다.

---

## 요약 (8줄)

1. **출처 식별: 특정 불가.** "Intelligent Urban Development Modelling", "CityFinder", 영문 본문 문장은 영·한 쿼리 수십 개로 찾았으나 일치하는 페이지가 0건이었다. 회사·프로젝트·연도·발주처 모두 [미확인].
2. **구조상 가장 가까운 공개 계보는 Arup의 IRM(Integrated Resource Management) 모델과 Imperial 대학 HierSynth·Unity3D 프런트엔드(2006–2018).** 토지이용표 → 8개 분야 하위모델 → 수백 개 산출을 8 KPI로 요약, 40개 이상 전략을 켜고 끄기, 3D 뷰 위에 KPI 표시. 이미지의 5요소와 대응하지만 **같은 도구라는 증거는 없다** [추정].
3. **데이터 모델 핵심: 토지이용표(유형별 연면적·세대·인구) × 원단위(분야별 가정) → 흐름 → KPI.** Arup IRM의 1인당 탄소 계산 슬라이스는 입력 약 1,200개 중 설계 입력이 약 37%, 나머지 약 63%가 분석 가정(원단위)이다 [확인, T3].
4. **KPI·재무: IRM 공개 8 KPI는 절대량(탄소·에너지·상수·하수·매립·교통탄소·OPEX·CAPEX)이고, NPV·IRR·손익분기는 IRM 공개자료에 없다.** 이미지의 % KPI 8개와 재무 3종의 산식은 어느 자료에서도 확인되지 않았다 [미확인].
5. **같은 계열 공개 사례 11건**(표 §3): Arup IRM, AECOM SSIM, SUNtool/CitySim, URBio, BRIDGE, Geodesign DSE, Hammarby ELP, 톈진 KPI, KPF Scout·Sasaki Magpie·AECOM Para-Form, MUtopia, Arup Expo 2020 폐기물 모델.
6. **비판 근거(§4):** 수치모형은 검증 불가능하고 발견적 가치만 있다(Oreskes 1994) · 입력 가정 의존과 스프레드시트 오류(Birch 2013 외) · 지표와 장기 성과를 잇는 연구가 없다(LBNL 2013) · 수치·다이어그램은 설득 도구로 쓰인다(Rapoport 2014) · 단일 점수·최적해는 상충관계를 가린다(Vandevyvere 2013, Schüler 2018) · Dongtan은 거의 지어지지 않은 채 중단.
7. **실제 설계 의사결정에 미친 영향의 증거**는 회사 자료와 익명 사례뿐이다(CommunityB: 밀도를 높이는 근거로 쓰임; SSIM: 양곤 3개안 선택은 AECOM 주장). 독립적 사후 검증은 찾지 못했다 [미확인].
8. **작업 제약:** 세션 WebSearch 한도(200/200) 소진으로 후반은 직접 열람과 OpenAlex API만 썼다. introba.com 보안확인과 DuckDuckGo CAPTCHA는 우회하지 않았다. 한국 사례(송도·부산 EDC·세종 5-1) 지표 체계는 조사하지 못했다 [미확인].

---

## 1. 출처 식별 — 특정 불가

### 1.1 시도한 쿼리 (대표)
- 도구명·제목: "Intelligent Urban Development Modelling" + CityFinder / masterplan / platform; "Intelligent Urban Development Modeling|Model"; "Urban Development Modelling Platform"; "CityFinder" + Arup·Atkins·AECOM·Mott MacDonald·Rhino·Grasshopper·KPI·design option.
- 본문 문장: "keeps track of the flow of resources in and out of the masterplan"; "flow of resources in and out of the masterplan"; "facilitate discussions and ultimately drive sustainable design"; "aim of the software is to facilitate".
- 캡션·UI: "Dynamic Geometry by Space Type", "Dynamic Infographics", "Interactive 3D Viewport", "User Input Options"; "Combined Real Estate Value" NPV break-even; "Anaerobic Digestion Plant" "Recycling Rates".
- KPI 문자열: "Car-Free" "Carbon Reduction" "Landfill Diversion" "Internal Rate of Return" "Job Creation" "Community Provision" "Resiliency" "Ecological Footprint".
- 한국어: "지능형 도시 개발 모델링 플랫폼", "지능형 도시 개발 모델링", 시티파인더/CityFinder + 마스터플랜·KPI, 자원 흐름·혐기성 소화·재활용률·영한 병기·제안서.
- 회사 한정: arup.com / aecom.com·atkinsrealis.com·mottmac.com / burohappold·som·kpf·sasaki·gensler·fosterandpartners·cundall·wsp 도메인 제한 검색; AECOM SSIM + Korea·Songdo; Arup + 부산 EDC·세종·송도·광교·화성·마곡; Yongsan IBD 2007 + resource flow.
- 프로젝트 내부 파일 검색(`CityFinder|Intelligent Urban|지능형 도시|자원 흐름|SSIM`): 매치된 12개 파일 중 `work/20261006_데이터기반_파라메트릭_마스터플랜_플랫폼_리서치_v1.md`(오늘 작성 중인 문서)만 열어 봤고 출처 단서는 없었다. 나머지(docs/·work/tongyeong_ref 등)는 내용을 열지 않았다 [미확인].

### 1.2 나온 것 (이미지와 일치하지 않는다고 판단)
- 벤더형 도구: ModelMe3D, DBF Engine(Digital Blue Foam), ArchiVinci, 3D CityPlanner, Tygron, UrbanSim, Modelur, SMARTPLANS(윈저대) [스니펫]. 이름·구성(자원흐름 + 공간유형 + 재무) 불일치.
- Introba(구 Integral/Elementa) 「Confidential Masterplan, Istanbul」: Sefaira 기반 동적 대시보드, 에너지·탄소·물만 다룸 [스니펫]. 원문은 Cloudflare 보안확인으로 못 열었고 우회하지 않았다.
- Buro Happold 「Intelligent masterplanning」: 베를린-브란덴부르크 2070(2020)·New Gartenfeld 사례, 자원흐름 시각화와 GIS 데이터모델 언급, 플랫폼 아님 [확인·요약, T4]. https://www.burohappold.com/articles/intelligent-masterplanning/
- Foster + Partners 「Eternal Seoul」(2009, 인천경제자유구역 확장, 300㎢): 한국 프로젝트이나 도구·KPI 언급 없음 [확인·요약, T4].
- 용산 IBD 2007(Libeskind + Arup): 지속가능성 언급만 있고 도구 언급 없음 [스니펫].
- Arup 「Masterplanning and urban design」 서비스 페이지: Adelaide City Plan의 디지털 트윈만 언급, 자원흐름·KPI 도구명 없음 [확인·요약, T4].

### 1.3 구조상 가장 가까운 후보 = Arup IRM 계보 (동일 도구 아님)

| 이미지 요소 | Arup IRM 계보에서 확인된 것 | 대응도 |
|---|---|---|
| 입력 탭 8개(Carbon·Water·Food·Waste·Transport·Materials·Social·Financial) | IRM 분야: 토지이용·에너지수요·에너지공급·물·폐기물·여객교통·물류·사회경제(Birch 2013 박사논문); 탄소회계·에너지·물·폐기물·교통·재료·경제(Birch 2018); Dongtan 2006 슬라이드는 식량생산 포함 [확인] | 높음 |
| KPI 링 8개 | 수백 개 KPI를 8개로 요약해 3D 화면 HUD에 표시(Birch 2018) [확인] | 개수 일치, 항목은 다름 |
| 전략 입력(재활용률·혐기소화) | 40개 이상 전략을 켜고 끄며 강도 가변(Birch 2013·2018) [확인] | 높음 |
| 3D 뷰포트·구역별 색 | Unity3D 웹·데스크톱 뷰, 구역 위 빌보드를 적-녹으로 채색(Birch 2018) [확인] | 높음 |
| Design Option | 시나리오 토글→제출→직전 시나리오 대비 KPI 차이 표시(Birch 2018) [확인] | 높음 |
| 재무(NPV·IRR·손익분기) | OPEX·CAPEX($/년)와 단계표만 확인, NPV·IRR 없음 [확인] | 낮음 |
| 'CityFinder'·'Intelligent Urban Development Modelling' | 어떤 자료에도 없음 | 없음 |

결론: 같은 설계 철학의 도구라는 수준에서만 말할 수 있고, 회사를 지목할 근거는 없다. J. Page라는 저자명이 SUNtool(Robinson 2007), Arup IRM 지침 논문(PLEA08), URBio(Schüler 2018)에 공통으로 나오는 점은 계보 단서이나 동일인 여부는 [미확인].

### 1.4 확정하려면 (제안)
이미지가 실린 문서의 PDF 속성(작성자·제작 프로그램), 표지·판권·쪽 하단의 회사명·프로젝트 코드, 영문 단락의 한국어 번역 의뢰처, 같은 문서의 다른 쪽에 나오는 프로젝트명, 이미지 역검색(Google Lens 등)이 가장 빠르다.

---

## 2. 해부

### (a) 데이터 모델
- **Arup IRM(2006–2018)** [확인, T3·T4]
  - 구현: Excel 통합문서, 5만 셀 이상. 분야마다 입력 모델·출력 모델을 두고, 중앙에 프로젝트 지표 대시보드 한 장(Birch 2013 박사논문, EuSpRIG 2013).
  - 분야: 토지이용, 에너지수요, 에너지공급, 물, 폐기물, 여객교통, 물류, 사회경제(박사논문). Dongtan 2006 슬라이드에는 마스터플랜(토지이용표)에서 물·에너지·식량·하수·교통·경제·폐기물·물류로 가지가 뻗고 하위모델 간 피드백을 본다고 그렸다.
  - 입력: 토지이용표(구역별·용도별 연면적). CommunityB 사례는 6개 용도(주거·기존 업무·신규 업무·신규 연구시설·체력단련·중앙설비), 14개 구역, 10개 건설단계, 3개 밀도안.
  - 입력의 성격: 1인당 탄소 계산 슬라이스는 수치 입력 약 1,200개, 이 중 설계 입력이 약 37%이고 나머지는 분석 가정이다(자동차 1km당 탄소, 업무 ㎡당 물 사용량 등). EuSpRIG는 같은 슬라이스에서 933개 변수에 범위를 줬다. 2018년 논문은 "수천 개의 입력과 가정, 수백 개의 KPI"라고 쓴다.
  - 건물유형별 에너지 사용 원단위(W/㎡)를 산출·사용한다(박사논문).
  - IRM은 형태를 평가하지 않고 연면적 같은 통계만 받는다(Birch 2018).
- **일반화한 계산 구조 [추정, 위 사실을 정리한 내 정식화]:** 흐름(분야 i, 시점 t) = Σ(공간유형 k) 수량(k,t) × 원단위(i,k) × (1 − 전략 효과) + 공급측 변환. KPI는 흐름의 합산·비율. 이 식 자체를 적은 문헌은 찾지 못했다.
- **SUNtool(EU FP5)** 은 "통합 자원흐름 모델링 및 교육 도구"로 용도 구성·부지 배치·건물 설계·자원관리 옵션을 빠르게 정의해 경제 제약 안에서 지속가능성을 최적화하는 목적이다 [확인·요약, T2 CORDIS].

### (b) 입력 전략이 흐름·KPI를 바꾸는 방식, BAU 정의
- IRM 전략은 모델 안에 켜고 끄는 스위치로 들어 있고, 영향이 여러 분야에 동시에 반영된다. 40개 이상. 예: 저유량 기기, 물 절약 조경, 지역에너지 공급. 교차효과 예: 물 절약은 펌핑 전력을 줄이고, 지역난방은 에너지·탄소를 줄이나 물 소비를 늘릴 수 있다 [확인, Birch 2018].
- 사례 전략명: 대중교통역 300m 내 거주자 최대화, 4개 생활서비스 300m 내 거주자 최대화, 주거 주차 요구량 최소화, 소매 주차 요구량 최소화, 수요측 능동·수동 전략(전기·열), 재생에너지 공급(전기·열) [확인].
- **BAU(기준) 정의:** 공개 정의문은 찾지 못했다. 박사논문은 에너지 전략을 Good(= BAU) · Better(합리적) · Best(열망적)로 세 단계 두고 밀도 3안과 짝지었다. Better·Best는 Good 대비 비용지표가 절반이었고 인구가 늘어도 탄소가 거의 일정했다 [확인]. 즉 기준선은 **같은 모델 안에서 모델러가 정한 시나리오**다. Dongtan은 "기존 방식 도시"를 기준선으로 에너지 수요 1,650 GWh/년 대 600 GWh/년, 생태발자국 5.8 대 2.6 gha/인으로 비교했다(Arup 2006 슬라이드 [확인, T4]). Hammarby ELP는 기술·계획 선택을 BAU 기본안과 비교한다(LBNL 2013 [확인, T2]).
- 감축률 %의 산식은 1 − 옵션/BAU로 읽히나 이미지 도구의 정의는 [미확인] [추정].

### (c) KPI 정의·산식
- **Arup IRM의 8 KPI**(Birch 2018 표 1) [확인]: Total primary carbon(mton/년), Energy consumption(MWh/년), Potable water(ML/년), Waste water(ML/년), Waste landfilled(mton/년), Transport carbon(mtCO2e/년), Operational expenditure($/년), Capital expenditure($/년).
- **이미지의 8 KPI는 정의·산식을 확인하지 못했다.**

| 이미지 KPI | 플랫폼 정의 | 공개 자료에서 확인된 유사 지표 | 비고 |
|---|---|---|---|
| Car-Free 90% | [미확인] | IRM: 교통 탄소(절대량), 전략 "역 300m 내 거주자 최대화" | 분모(통행·인구·면적) 불명 |
| Carbon Reduction 52% | [미확인] | IRM: 총 1차 탄소(mton/년), Good→Better/Best 비교 | BAU 대비로 추정 |
| Landfill Diversion 100% | [미확인] | IRM: 매립 폐기물(mton/년). Arup Expo 2020: 폐기물 85% 매립 전환 목표를 물질흐름 모델로 추적해 달성 [확인·요약, T4] | 일반식 1 − 매립량/발생량 [추정] |
| IRR 18% | [미확인] | IRM 공개자료에 IRR 없음(OPEX·CAPEX만) | 일반 정의 |
| Job Creation·Community Provision·Resiliency | [미확인] | IRM의 '사회경제' 분야 존재만 확인 | 지표 목록 미확인 |
| Ecological Footprint | [미확인] | Dongtan: gha/인 단위로 비교(5.8 대 2.6) [확인, T4]. REAP 사용은 [스니펫] | |

- 지표 체계 일반: LBNL이 검토한 16개 도시 지표 체계 중 순위형 9개는 평균 26개, 추적형 7개는 평균 45개 지표를 쓰고, 가중·기준값에 대한 합의가 없다 [확인, T2]. 톈진 생태도시 KPI는 2008년 26개(정량 22 + 정성 4), 2018년 개정 36개(정량 30 + 정성 6) [확인·요약, T4 위키; MND 원문은 못 열었다].
- AECOM SSIM은 새 양곤 계획에서 연결된 이웃·업무환경·지속가능 도시구조·녹색 인프라 4개 범주로 3개 대안을 평가했다 [확인·요약, T4 발주사 페이지]. "Light SSIM은 프로그램·공간 패턴으로 KPI를 계산해 결정 매트릭스로 제시"는 [스니펫].

### (d) 재무 모듈
- IRM에서 확인된 재무: OPEX·CAPEX KPI, 10개 건설단계 단계표(phasing)로 연도별 가정 변화(건축기준 강화, 기기 효율, 배출계수)를 반영해 KPI를 시계열로 산출, 지역에너지 시스템용 별도 생애주기비용(LCCA) 모델(박사논문 [확인, T3]).
- NPV·IRR·손익분기·공간유형별 가치: **IRM 공개자료에 없다.** Sasaki Magpie는 설계를 실시간으로 공간 수율·세대수·상위 수준 재무지표로 바꾼다고만 밝힌다 [확인·요약, T4].
- 이미지의 "Combined Real Estate Value (NPV B$)"는 공간유형별 가치를 합산한 NPV로 읽히나 구조는 [미확인] [추정]. NPV 0.15 B$, IRR 18%, 손익분기 11년, 누적 막대는 이미지 판독값이다.

### (e) 지오메트리 연동
- **HierSynth(Imperial·Arup, 2013)** [확인, T3]: 설계 데이터(CAD, GIS DB, Excel 토지이용표)를 "설계 질의"로 읽어 개발지 → 구역 → 건물유형 → 건물의 트리로 분해하고 노드마다 분석을 돌린다. IRM을 Excel 노드로 자동 실행해 1회 0.2–1초, 한 질문당 1,188회 실행 사례. 저자는 분석 반복이 약 10배(한 자릿수 차수) 늘었다고 보고. 화면은 Unity3D.
- **Birch 2018** [확인]: Unity3D 웹·데스크톱 뷰, 8 KPI HUD, 구역별 적-녹 빌보드, 시나리오 제출 후 10–30초, 클라우드 분석 플랫폼 Concinnity, Radiance 일조 분석(BRE209) 연동. 부지 29개 구역·39ha·연면적 30만㎡ 초과 해안 신업무지구.
- **AECOM Para-Form**: Rhino + Grasshopper + Excel로 용적률·연면적·높이·인구·세대수·주차를 실시간 계산 [스니펫].
- **KPF Urban Interface Scout**: 자체 개발 웹 플랫폼, 초급·전문가 모드. 입력은 가로망, 활동 분포 "픽셀 맵", 높이 제한, 필지, 총 건축면적. 출력은 조망·일조·천공률·일사·바람·에너지. 수만 개 설계를 생성하고 큰 설계공간은 기계학습으로 다룬다. Sidewalk Toronto 협업 [확인·요약, T4].
- 이미지 도구의 CAD·Rhino·GIS 연동과 렌더 엔진은 [미확인]. 흰색 맥락 건물과 단색 블록은 웹 3D의 전형적 표현이다 [추정].

### (f) 시나리오(Design Option) 비교
- IRM(Birch 2018): 전략 조합을 사람이 탐색, 직전 시나리오 대비 차이 표시, 기준선 대비 정규화한 8축 레이더로 86개 변형 비교. 저자는 핵심 결과가 최적해가 아니라 어떤 전략이 중요한지에 대한 방향 피드백이라고 쓴다. 전략 49개면 조합 2^49개라 전수 탐색은 불가 [확인].
- URBio(EPFL): 최적해 하나가 아니라 의사결정 공간 전체를 보여준다 [확인·요약, T3].
- SSIM: 대안별 KPI를 결정 매트릭스로 비교, 양곤은 3개안 평가 [확인·요약 / 스니펫].
- 이미지의 'Design Option' 드롭다운은 옵션을 하나씩 본다 [판독].

### (g) 데이터 입력의 출처와 불확실성 처리
- IRM의 원단위는 엔지니어가 쌓은 암묵지와 프로젝트별 조정에 의존하고, 문서화가 부족하다. 신판은 지역별 데이터 표를 내장한다. 데이터 입력 비용이 도입 장벽이라고 저자들이 명시한다(EuSpRIG 2013 [확인]).
- 불확실성 처리는 도구 기본기능이 아니라 연구진이 덧붙인 방법이다: 엔지니어와 변수별 최솟값·최댓값을 정하고 Plackett–Burman 설계로 933개 변수, 2,563회 실행(1회 0.72초) [확인].
- 자동화 과정에서 드러난 문제(박사논문 [확인]): 0으로 나누기, 0을 받지 않는 셀, 누적과 연간 혼동, 500자 넘는 수식, 개발 전체 단위의 탄소 상쇄값을 구역 단위에 그대로 써서 1인당 탄소가 음수로 나온 사례. 오류 없음과 정확함은 다르다고 저자가 밝힌다.
- EuSpRIG: 버스 배출계수를 코치 버스에 같이 써서 코치 탄소가 과대일 가능성을 발견. 이전 섬 프로젝트의 가정이 이월된 것으로 추정했다 [확인].

---

## 3. 같은 계열 공개 사례 11건

| # | 도구(주체) | 연도·프로젝트 | KPI·출력 | 입력변수 | 엔진 | 한계 | 출처(등급·상태) |
|---|---|---|---|---|---|---|---|
| 1 | **Arup IRM** (+Imperial HierSynth) | 2002 틀(EuSpRIG 참고문헌 기재) → 2005–07 Dongtan → 2008 논문 → 2013 → 2018 | 8 KPI(§2c), 수백 개 산출 | 토지이용표, 40개 이상 전략, 1,200개 안팎 입력 | Excel 5만 셀, HierSynth, Unity3D, 클라우드(Concinnity) | 데이터 요구, 복잡도, 오류, 형태 변경 불가, 실행시간 | arXiv 1401.4582; hdl.handle.net/10044/1/12683; doi.org/10.1016/j.aei.2018.07.004; cfsd.org.uk Mashford 2006 PDF (T3·T4, [확인]) |
| 2 | **AECOM SSIM** | 연도 [미확인]; Marina Bay 2012; New Yangon 2019; NASA Ames; Fort Irwin | 4개 범주(양곤), 결정 매트릭스, 에너지·물·교통·사회경제·생태 | 공개 정의 없음 | SSIMe 에너지 모듈; 엔진 [미확인] | 공개 자료에 산식·기준선 절차·비용편익 결과 없음 | aecom.com/tw/projects/6sustainability-study-marina-bay-greater-southern-waterfront/; nydc.com.mm/the-completion-of-new-yangon-city-master-planning/; sustainability.urag.org(…/integration-methodology) (T4, [확인·요약]); ScienceDirect S1877042815033431 [403으로 열람 실패, 스니펫] |
| 3 | **SUNtool / CitySim** (EU FP5, EPFL 외) | CORDIS 기재 2004-08-06~2005-12-31(FP5 시기와 어긋나 재확인 필요) | 에너지·물·폐기물 흐름(스니펫: 시간 단위) | 용도 구성·배치·건물 설계 | CitySim 시뮬레이터 | 본문 미열람 [미확인] | cordis.europa.eu/project/id/13506 (T2 [확인·요약]); Robinson 2007 doi.org/10.1016/j.solener.2007.06.002; CitySim doi.org/10.26868/25222708.2009.1083-1090 (T3 서지만 [확인]) |
| 4 | **URBio** (EPFL) | 2017–18, Les Cherpines 제네바(58ha, 필지 233) | FAR, BAR, 랜드마크 조망계수, 재생에너지 비율, 망 연결률, 총·운영비 | 건물 통계, 에너지 기준, 기술 효율·비용 선형식, 기상, 에너지 가격 | mpMILP | 선형화로 정확도 희생, 극단해, 정량화 어려운 요소 소외, 시간해상도 4단계 | frontiersin.org/articles/10.3389/fbuil.2017.00076/full (T3 [확인·요약]) |
| 5 | **BRIDGE DSS** (EU FP7) | 2008-12-01~2011-11-30, 코디네이터 FORTH, 13개 기관, 총 4.1M€(EU 3.1M€) | 에너지·물·탄소·오염물 흐름 + 투자비·주거·고용 | 다기준 분석(MCA), 5개 도시(헬싱키·아테네·런던·피렌체·글리비체) | DSS | 본문 미열람 [미확인] | cordis.europa.eu/project/id/211345 (T2 [확인·요약]); doi.org/10.1016/j.landurbplan.2012.12.005; doi.org/10.1016/j.eiar.2012.06.007 (T3 서지); MCA·도시 목록은 [스니펫] |
| 6 | **Geodesign DSE** (Arciniegas 외) | 2019, 암스테르담 광역권 | 물질흐름·순환경제 | 이해관계자 공동설계 + 영향 시뮬레이션 | 오픈소스 | 파일럿 적용, 사용자 평가 상세 미확인 | cogitatiopress.com/urbanplanning/article/view/2173; doi.org/10.17645/up.v4i3.2173 (T3 [확인·요약]) |
| 7 | **Hammarby Model / ELP** (스톡홀름시) | 1990년대~, Hammarby Sjöstad(약 1만 세대·2.5만 명) | 대기·토양·수질 배출, 화석연료, 건설·운영·해체 전 과정, 1990년대 중반 시 평균 대비 환경부하 50% 감축 목표 | 기술·계획 선택 vs BAU 기본안 | 전 과정 평가 도구 | 개발계약 협상은 기존 제도·관계에 묶여 결과에 남긴 흔적이 작았고 시간이 갈수록 학습으로 목표 충족도가 높아짐(Svane 2011). 순환 다이어그램의 설득력은 비판 대상(Rapoport) | LBNL doi.org/10.2172/1171800 (T2 [확인]); Svane doi.org/10.1080/19463138.2011.620959 (T3 초록 [확인]) |
| 8 | **톈진 생태도시 KPI** | 2008 → 2018 개정 | 26개 → 36개(정량 30·정성 6) | 목표연도 2023·2028·2035 | 지표 체계(모델 아님) | 인구 목표 2020년 35만 대 2019년 4월 약 10만(위키 인용) | en.wikipedia.org/wiki/Sino-Singapore_Tianjin_Eco-City (T4 [확인·요약]); MND 원문 [미확인] |
| 9 | **KPF Scout / Sasaki Magpie·Dashi·Visualizer / AECOM Para-Form** | 연도 [미확인]; Sidewalk Toronto 협업(KPF) | 조망·일조·바람 등(KPF), 공간 수율·세대수·상위 재무지표(Sasaki), 용적률·세대·주차(AECOM) | 가로망·활동 분포·높이·필지(KPF) | 웹 플랫폼(KPF·Sasaki), Rhino+GH+Excel(AECOM) | 공개 자료에 한계·검증 기술 없음 | ui.kpf.com/smarter-city; sasaki.com/voices/data-driven-living-masterplan/ (T4 [확인·요약]); Para-Form은 aecom.com/blog/parametric-future-cities-2/ [스니펫, SPA라 열람 실패] |
| 10 | **MUtopia** (멜버른대 Mendis·Ngo·Aye·Malano) | 2012 학회; 2016 후속 장 | 에너지·폐기물·물·교통 흐름을 토지이용에 연결, BIM·GIS 통합 [스니펫] | — | 웹 플랫폼 | 본문 미열람 [미확인] | OpenAlex 서지 [확인]; 요약은 [스니펫]. 후속: doi.org/10.1007/978-3-319-28112-4_34 |
| 11 | **Arup Expo 2020 Dubai 폐기물 모델** | Expo 2020 Dubai(6개월 행사), 발주 Expo City Dubai(HOK와 함께) | 폐기물 매립 전환 85% 목표 | 현장 점검 + 폐기물 업체 실시간 자료 | 물질흐름 컴퓨터 모델 | 운영 단계 추적 도구(설계 도구 아님) | arup.com/projects/expo-2020-dubai (T4 [확인·요약]) |

**사례 공통 구조:** 공간 프로그램(면적·용도) × 원단위 → 흐름 → KPI, 옵션 비교. 차이는 (i) 산출 단위(절대량 대 %), (ii) 재무 포함 여부(Magpie·URBio·IRM의 OPEX/CAPEX), (iii) 형태 연동 여부(KPF·Para-Form 대 IRM)에 있다.

---

## 4. 이 계열 도구의 비판·한계 (근거 있는 것만)

1. **검증 불가능성.** 자연계 수치모형의 검증과 확증은 불가능하고 모형은 상대 평가와 발견적 가치로만 쓸 수 있다. "Verification and validation of numerical models of natural systems is impossible."(Oreskes 외, Science 1994 초록 [확인, T3]). 도시 자원흐름 모형에도 같은 논리가 적용되나, 이 계열 도구의 사후 검증 연구는 찾지 못했다 [미확인].
2. **원단위·가정 의존과 블랙박스.** IRM 1인당 탄소 슬라이스의 입력 약 63%가 분석 가정이다(박사논문). 암묵지 의존, 문서 부족, 인과 불명확, 데이터 요구가 도입 장벽이다(EuSpRIG 2013). 한 대형 엔지니어링 회사에서 분석 모델 약 1,000개가 쓰인다는 저자 조사도 있다. 이월된 가정으로 코치 버스 탄소가 과대로 의심되는 사례가 있다. [확인, T3]
3. **오류 위험.** 자동화 과정에서 0 나누기 전파, 구역 단위 변환 누락으로 1인당 탄소 음수, 500자 넘는 수식이 발견됐다. 오류가 없다고 정확한 것은 아니다(박사논문 [확인]).
4. **가짜 정밀도.** 수백 개 산출을 8개로 요약하고 단일 값으로 보여 주는 설계가 불확실성을 가린다. IRM 자체에는 범위 전파가 기본 기능으로 없고 연구진이 따로 민감도 분석을 얹었다 [확인]. 이미지 도구가 값에 범위를 표시하는지는 [미확인]. 건물에너지 분야의 예측-실측 격차 문헌(de Wilde 2014 Automation in Construction, doi.org/10.1016/j.autcon.2014.02.009; Menezes 외 2012 Applied Energy, doi.org/10.1016/j.apenergy.2011.11.075)이 원단위 예측의 한계를 다루나 본문은 열지 못했다 [서지만 확인, 내용 미확인].
5. **지표-성과 연결 부재.** 어떤 한 지표의 성과가 도시의 장기 지속가능성 개선과 직결된다는 연구는 없고, 지표는 쓸 수 있는 자료에 따라 골라지며, 가중·기준값 합의가 없다(LBNL 2013 [확인, T2]).
6. **수치와 도식은 설득 도구.** 자원·탄소 감축 전망 수치와 Hammarby 같은 자원 부하 다이어그램은 고객을 끌어들이는 힘으로 작동하고, 국제 컨설턴트들이 시간·비용 압박 때문에 계획 내용을 이 안에서 저 안으로 복사해 쓰며, 자기 계산상 결과가 나오니 적절하다는 결과주의 논리가 있다(Rapoport 박사논문 2014 [확인, T3]). 인구 100만 명 이상 도시의 마스터플랜을 8주 만에 쓴 사례, 계획 이행 시점에 설계사는 대개 떠나 있고, 지속가능 마스터플랜 대부분은 실제로 지어지지 않는다는 서술도 있다(Rapoport, Area 2014, doi.org/10.1111/area.12079 [확인]).
7. **단일 점수·최적해의 위험.** 하나의 점수는 상충관계를 가리므로 성찰적 거버넌스의 나침반으로 써야 한다(Vandevyvere 2013 초록 [확인]). 최적화는 극단해를 내고 정량화되지 않는 요소를 소외시킬 수 있다(Schüler 2018 [확인·요약]).
8. **도입·활용 실패.** 계획지원시스템(PSS)이 널리 쓰이지 않는 이유는 인식·경험 부족, 가치 인정 부족 등 인간·조직·제도·기술 요인이다(Vonk·Geertman·Schot 2005 초록 [확인]). "Forty Years after Lee's Requiem"(te Brömmelstroet 외 2014, doi.org/10.1068/b4103c)는 같은 쟁점의 후속이나 본문 미열람 [미확인].
9. **현실 이행 실패 사례.** Dongtan(Arup 총괄 마스터플랜, 2005 시작)은 정치 후원자 몰락, 시행사와의 비용 책임 불일치, 현지 주민 협의 부재, 습지 입지로 거의 지어지지 않았다 [확인·요약, T4 Yale e360]. 위키는 Arup가 2008 Ethical Corporation의 'Greenwasher of the Year'를 받았다고 적는다 [스니펫, 2차; 원문 미확인].
10. **실제 설계 의사결정에 미친 영향의 증거.** 긍정: CommunityB(익명)에서 분석 결과가 설계팀이 더 높은 밀도로 가도록 하는 추가 근거가 됐다(박사논문 [확인]). 양곤은 SSIM으로 3개안 중 선택을 도왔다는 AECOM 측 서술(T4). 부정·불명: 독립적 사후 평가 없음 [미확인]. 없다고 확정한 것은 아니고 찾지 못한 것이다.

---

## 5. 구경주역 이식 시 참고 (위 근거에서 직접 나오는 것만)
- 설계 입력과 원단위 가정을 분리 저장하고 가정에는 범위를 붙인다. IRM에서 가정이 입력의 약 63%였고 불확실성은 후속 연구가 덧붙였다 [확인].
- % KPI는 절대량을 계산한 뒤 BAU 대비로 파생하는 편이 IRM 방식과 맞는다(2018 정규화 레이더) [확인]. BAU의 정의문을 KPI마다 명시해야 한다 [추정].
- 시나리오는 최적해 하나가 아니라 의사결정 공간(전략 조합)으로 다룬다(Birch 2018, URBio) [확인].
- 실시간 슬라이더가 되려면 모형 1회 실행이 1초 안팎이어야 한다. IRM 자동화는 0.2–1초, 클라우드 판은 10–30초였다 [확인].
- IRM은 형태를 바꾸는 입력을 못 받았다(2018). "공간유형별 동적 지오메트리"는 별도 생성기가 필요하다 [확인 + 추정].
- 재무(NPV·IRR)는 IRM 공개자료에 구조가 없어 참고할 선례를 못 찾았다 [미확인].

## 6. 미확인·후속
- 이미지의 출처(회사·프로젝트·연도·발주처), KPI 8개 산식, 재무 모듈 구조, 렌더 엔진.
- AECOM SSIM 원문 논문(ScienceDirect, 403), SUNtool·CitySim·MUtopia·BRIDGE 본문, 톈진 KPI 원문(MND), Arup IRM 8 KPI 표의 원출처(ResearchGate 403이나 Birch 2018 표 1로 확인), Ayaz & Levitas(2008, Eco-city 학회)·Page 외(PLEA08) 원문.
- 한국 사례(송도·부산 EDC·세종 5-1 생활권)의 지표 체계와 BioRegional·Best Foot Forward 자원회계는 조사하지 못했다.
- Kennedy 외 2011(도시 대사 → 계획·설계 적용, doi.org/10.1016/j.envpol.2010.10.022), Rydin 2007(지표와 통치술, doi.org/10.1068/d72j), Lawrence·Robinson 2014(생태발자국 비판, doi.org/10.1016/j.ecolind.2014.01.026)는 서지만 확인했고 내용은 열지 못했다.

## 7. 작업 메모
- 원문 텍스트 사본(scratchpad): `irm1.txt`(EuSpRIG 2013), `crowd_irm.txt`(Birch 2018), `birch_thesis.txt`(Birch 2013 박사논문), `rap_area.txt`·`rap_mob.txt`(Rapoport 2014), 보조 스크립트 `oa.py`·`oas.py`·`spiral.py`(OpenAlex 조회, Imperial Spiral 내려받기). `tool-results/mashford.txt`(Arup 2006 슬라이드), `tool-results/lbnl.txt`(LBNL 2013).
- 개인정보: OpenAlex 첫 호출 1건의 User-Agent 헤더에 사용자 이메일이 실수로 들어갔고 이후 스크립트에서 제거했다.
