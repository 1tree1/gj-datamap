# 대시보드 PoC v0 — 이미지의 5요소를 우리 계획안 도형으로 한 파일에 구현해 본 것

- 만든 때: 2026-10-06. 조사 에이전트 D가 "슬라이더 → 지오메트리 → KPI → 대시보드"가 마감 안에 가능한지 **실측하려고** 만든 것을 이 폴더로 옮겼다. 내용은 고치지 않았다.
- 보고서: `../20261006_데이터기반_파라메트릭_마스터플랜_플랫폼_리서치_v1.md` §3.6

## 열기

`dashboard_poc_v0.html`을 더블클릭한다. 인터넷이 필요 없다(JS·CSS·도형 데이터 전부 인라인, 1.29 MB). `file://`로 열리는 것을 headless Chrome 렌더로 확인했다(`poc_screenshot.png`).

## 이미지 5요소와의 대응

| 이미지 | 이 PoC |
|---|---|
| (1) KPI 링 8개 | 우측 링 8개 (FAR 사용 · 거주인구 · 일자리 · IRR · 탄소 · 공원 · 공공 비중 · 일조) |
| (2) 공간유형별 동적 지오메트리 | 용도 분류(`cat`)별 색 압출 매스. 층수 배율 슬라이더로 높이가 바뀐다 |
| (3) 인터랙티브 3D 뷰포트 | 중앙 three.js 뷰(궤도 회전) |
| (4) 사용자 입력 옵션 + Design Option | 좌측 드롭다운 + 슬라이더 5개(층수 배율 · 주거 비중 · 공사비 · 할인율 · 수익 배율) |
| (5) 동적 인포그래픽 | 하단 NPV·IRR·손익분기 현금흐름, 5목적 레이더, 평행좌표(파레토 탐색) |

도형은 `work/20261005_plan_clean/gis`(규제 미적용 개념안 v1)의 사본이다(건물 57 · 획지 19 · 도로 16 · 공원 4).

## ⚠ 이 PoC의 수치는 쓰면 안 된다

- 거주인구·일자리·IRR·탄소·NPV 등 **모든 KPI 값은 속도 측정용 가정치**이고 출처가 없다. 화면 하단에도 같은 문구가 있다. 계획 수치·공모 자료·PT에 넣지 말 것.
- 파레토 200점과 Design Option A–E는 **합성 데이터**다. gjplan이 만든 해가 아니다.
- 알려진 결함: KPI 라벨 일부(공원 단위 등)가 틀리고, 현금흐름 차트의 범례가 겹친다. 규제 clamp(슬라이더가 고도지구 상한을 넘지 않게 막는 장치)가 없다.
- 이 PoC가 증명하는 것은 *형식*이다. 입력이 바뀌면 형태와 숫자가 함께 움직이는 구조가 우리 도형·우리 스택 수준에서 한 파일로 가능하다는 것.

## 실측 (에이전트 D, i9-13900K, headless Chrome 154, WebGL은 소프트웨어 렌더)

| 항목 | 값 |
|---|---|
| 단일 HTML 크기 | 1,294,036 B (gzip 약 382 KB) |
| 슬라이더 1회 갱신 (높이 + KPI 닫힌식 + 차트 setOption 9개 + 렌더) | **3.4 ms** (KPI 닫힌식 0.054 ms, setOption 3.17 ms) |
| 저해상 일조 레이캐스트 (22,420선, BVH 재구축 포함) | 14.1 ms — 속도 측정용이고 실제 일조 지표가 아니다 |
| LightGBM → JSON → JS 추론 | 3.2 µs/회 (합성 목표 R² 0.922 — 프로젝트 R²가 아님) |
| FastAPI 로컬 왕복 | 2.4 ms (gjplan S1–S4 생성 비용은 미포함, 미측정) |

스크린샷의 "합계 104.6 ms"는 일조 재계산과 소프트웨어 WebGL 렌더를 포함한 값이다. 렌더 시간은 대표성이 없다.

## 재빌드

```bash
cd build
npm install
npm run build        # → dist/index.html (vite-plugin-singlefile)
```

의존성: three r186 · echarts 6.1 · three-mesh-bvh · suncalc · vite · vite-plugin-singlefile. 이 중 suncalc는 npm에 라이선스 표기가 없다 [미확인] — 태양 위치는 직접 구현해도 된다.

## 파일

| 파일 | 내용 |
|---|---|
| `dashboard_poc_v0.html` | 결과물(단일 HTML) |
| `poc_screenshot.png` | headless Chrome 렌더 캡처 |
| `build/` | 소스(`src/main.js`, `src/plan.json`, `index.html`, `package.json`, `vite.config.js`) |
