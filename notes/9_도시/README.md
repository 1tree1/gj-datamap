# city plan — URBANIS / 구경주역 지구단위계획

Claude Code 작업 저장소.

- **컨텍스트**: `CLAUDE.md` (세션 시작 시 자동 로드)
- **정본 지식**: `docs/` — 무엇이 어디에 있는지는 `docs/INDEX.md`
- **자료 아카이브**: `archive/` — 채우는 방법은 `docs/10_gyeongju/구경주역_부지_자료_아카이브_설계.md`
- **최적화 엔진**: `gjplan/` — 설계는 `docs/40_engine/구경주역_최적화엔진_Part5.md`
- **산출물**: `work/`

## 시작하기

```bash
claude          # 이 폴더에서 실행
```

자주 쓰는 슬래시 커맨드:

| 커맨드 | 하는 일 |
|---|---|
| `/근거` | 주장·수치의 출처를 docs에서 찾아 T등급과 함께 제시 |
| `/사례` | 주어진 쟁점에 맞는 사례를 E 코퍼스에서 골라 코딩 항목으로 정리 |
| `/규제` | 규제 4겹 중첩 검토 체크리스트 |
| `/아카이브` | 수집한 자료를 index.csv 형식으로 편입 |
| `/추적표` | 계획 결정 하나를 추적표 한 행으로 |
| `/엔진` | gjplan 구현 다음 단계 |

서브에이전트: `archive-curator`, `case-analyst`, `regulation-checker`, `data-engineer`.

> ⚠️ 처음 한 번: `claude_config` 폴더를 `.claude` 로 이름만 바꿔 주세요 (`claude_config/READ_ME_FIRST.md` 참조). 원격 도구가 `.claude`에 직접 쓸 수 없어 그렇게 두었습니다.
