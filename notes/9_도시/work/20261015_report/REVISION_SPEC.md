# 보고서 2차 수정 규격 (2026-10-16, 사용자 요청)

사용자 의견: 「너무 하이 레벨이다. 실무가 아니라 학부생 중간마감용이다. 글자 수를 조금 줄이고, 글자 크기를 키우고, 이미지·다이어그램을 많이 넣어라. 내용 구성은 좋다.」

## 할 일 (각 장 파일 `chapters/NN_*.html`에서)
1. **원본 보존**: 고치기 전에 `chapters/_v1/`에 같은 이름으로 복사한다(이미 있으면 덮어쓰지 않는다).
2. **구성 유지**: 장·절 제목(h1·h2)과 순서, 소결 상자, 핵심 수치·표는 유지한다. `REPORT_SPEC.md`의 문체(합니다체·명사형 제목)·등급 규칙은 그대로.
3. **글자 수 약 35% 감축**: 문단을 짧게(한 문단 2~4문장), 같은 말 반복·방법론 세부·한계의 장문 설명을 줄인다. 필요하면 짧은 목록(ul)으로 바꾼다. 부차적인 표는 합치거나 핵심 행만 남긴다(표 개수 약 25% 감축). 숫자를 새로 만들지 않는다.
4. **본문 출처 표기 단순화**: `<span class="src">`는 `[등급] 짧은 자료명`만 남긴다(예: `[T2] 소상공인365`, `[T1] 도시재생 전략계획`). 쪽번호·확인 상태·설명 문구는 지운다(전체 목록은 부록 A). 그림 캡션의 출처도 같은 방식으로 짧게.
5. **그림·다이어그램 늘리기**: 장마다 그림 수를 **1.5~2배**로. 절마다 최소 1개(가능한 곳). 큰 그림 위주(`figure.wide` 또는 `figure.col`), 사진은 2~4장을 PIL로 한 장에 붙인 묶음으로. 새 그림은 `fig/NN_슬러그.png`.
   - 그림 후보(직접 열어 보고 고른다):
     - 답사 사진 66장 `C:\Users\OFFICE\Desktop\9_도시\경주답사\*.jpg`(2026.09 현장)
     - `work/20261011_analysis_redesign/`(분석 지도·차트 다수), `work/20261011_visual_front/`, `work/20261008_presentation_front/`, `work/20261010_nexus_front/`, `work/20261011_final_deck/`, `work/20261011_history_aerial/`, `work/maps/`
     - 최종 마스터플랜 렌더 `work/20261011_masterplan_rough/sheets/`(조감·단면·확대 png), 도면 `work/20261011_masterplan_rough/diagrams/`
     - 덱 자산 `work/20261011_midterm_deck/build/assets/`, 발표자료 쪽 이미지 `work/20261015_report/pt_pages/`(crop은 원본 PDF를 pymupdf clip 200 dpi)
   - 본문 수치로 간단한 차트·도식을 matplotlib로 새로 만들어도 된다(서체 `%LOCALAPPDATA%\Microsoft\Windows\Fonts\Pretendard-*.otf`, 글자 10 pt 이상, 흰 바탕, 색은 보고서 붉은색 #C8102E와 회색 계열). 자료에 없는 수치는 그리지 않는다.
   - 이미 다른 장이 쓴 그림과 같은 것은 피한다(파일명 접두 번호로 구분).
   - 캡션은 `그림 N-k 제목 · [등급] 짧은 출처`. 그림 번호는 장 안에서 다시 매긴다.
6. 인라인 스타일·`<style>` 금지(조립 CSS가 글자 크기를 키운다: 본문 12 pt).
7. 끝나면 `chapters/NN_*.notes.md`에 「2차 수정」 절을 덧붙인다(줄인 글자 수 전→후, 그림 수 전→후, 새 그림 목록).

파이썬: `C:/Users/OFFICE/AppData/Local/Temp/claude/C--Users-OFFICE-Desktop-9---/e41d5223-5c21-4861-920c-a956fe5d1188/scratchpad/venv_plan/Scripts/python.exe` (`PYTHONIOENCODING=utf-8`).
