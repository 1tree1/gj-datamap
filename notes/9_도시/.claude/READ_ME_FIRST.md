# 이 폴더를 `.claude` 로 바꾸세요

Claude Code는 프로젝트 설정을 `.claude/` 폴더에서 읽습니다.
보안상 원격 도구가 `.claude` 폴더에 직접 쓸 수 없어 `claude_config/` 로 만들어 두었습니다.

PowerShell에서 **한 줄**:

```powershell
cd "C:\Users\User\Documents\Claude\Projects\city plan"; Rename-Item claude_config .claude
```

이미 `.claude` 폴더가 있다면 내용만 옮기세요:

```powershell
cd "C:\Users\User\Documents\Claude\Projects\city plan"
robocopy claude_config .claude /E
Remove-Item claude_config -Recurse
```

바꾸고 나면 `claude` 실행 시 아래가 바로 됩니다.

| 커맨드 | 하는 일 |
|---|---|
| `/근거 3822억` | 수치의 출처를 docs에서 찾아 T등급과 함께 |
| `/사례 1단계에 무엇을 넣을까` | E 코퍼스에서 동형 사례 + 실패 사례 코딩 |
| `/규제 지하 2층 가능한가` | 규제 4겹(+2) 중첩 체크리스트 |
| `/아카이브 <파일>` | index.csv 형식으로 편입 |
| `/추적표 종축 보행로 폭 30m` | 결정 하나를 추적표 한 행으로 |
| `/엔진 다음 뭐 해야 해` | gjplan 12주 구현 순서에서 현 위치 판단 |

서브에이전트 4종도 함께 들어갑니다: `archive-curator`, `case-analyst`, `regulation-checker`, `data-engineer`.
