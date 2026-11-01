# gjplan — 구경주역 지구단위계획 최적화 엔진

설계 정본: `../docs/40_engine/구경주역_최적화엔진_Part5.md`
**설계는 확정되어 있다. 재설계하지 말고 구현 순서를 따른다.**

## 파이프라인

```
S0 제약 컴파일 → S1 가로망 위상 → S2 가구 분할 → S3 획지 세분 → S4 용도·밀도
                                   ↓
                    f₁~f₅ 평가 (cheap / mid / surrogate)
                                   ↓
                      NSGA-III → 파레토 전선 → 대안 A–E
                                   ↓
                      phasing MILP → export (dxf/xlsx/3dm)
```

## CLI

```bash
gjplan compile   --boundary ../archive/C_data/processed/site.shp --layer BOUNDARY
gjplan surrogate --samples 500
gjplan optimize  --pop 200 --gen 300
gjplan phase     --option E
gjplan export    --option E --formats dxf,xlsx,3dm
```

## 목적함수

| | 정의 | 방향 |
|---|---|---|
| f₁ 접근성 | 통합도 회복 Δ + 15분 등시선 도달 인구·시설. **연속성 + 최약점 통과 폭**(최소값 지배) | ↑ |
| f₂ 유산영향 | 조망 차단 픽셀 + 완충구역 초과 볼륨 + 유존지역 침범 | ↓ |
| f₃ 사업성 | Σ(용도별 단위수익×연면적) − (토지+정화+공사×cost_factor+기반시설) | ↑ |
| f₄ 조직정합 | W(생성 획지 분포, 인근 원도심 실제 분포) + 기존 가로축 연장 실패율 | ↓ |
| f₅ 공공성·환경 | 300m 공원 도달인구 + 투수면적 + 저층부 활성길이 + 열섬 저감 | ↑ |

**가중치를 넣지 않는다.** 파레토 전선 전체를 내고 A(보존)–B(사업성)–C(접근성)–D(조직정합)–E(균형)로 제시한다.

## 규칙

- 제약은 페널티가 아니라 **불가능**이다 → `buildable` 마스크
- 차원을 낮게 유지한다. 50차원 초과 시 NSGA-III가 수렴하지 않는다
- 대리모델 없이 정직 평가로 루프를 돌지 않는다
- 대리모델 오차를 반드시 보고한다 (R², MAE, 최종 5개 대안 비교표)
- Ladybug 일조·열환경은 루프에서 제외, 최종 5개만 검증
- `compile`은 경계 면적을 즉시 출력한다 — 좌표계 오류를 여기서 잡는다
- Rhino는 루프 밖. 3dm 내보내 검토·수정 → 파라미터를 config.yaml에 반영 → 재실행
