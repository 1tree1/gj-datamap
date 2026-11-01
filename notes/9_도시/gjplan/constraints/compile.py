"""제약 컴파일 (S0). 1회 실행 후 constraints.npz로 캐시.

산출:
  height_max[H,W]  규제 4겹(+2)의 min
  buildable[H,W]   유존지역·오염·보존 제외
  cost_factor[H,W] 지반N값·오염·노반 재활용
  anchors[]        경계와 만나는 기존 도로·보행로 끝점 — S1 탐색공간을 정의한다
  fixed[]          등록문화유산 구 역사

원칙: 규제 위반은 페널티가 아니라 불가능이다. buildable로 잘라낸다.
"""

raise SystemExit("구현 순서 1~2주차. gjplan/README.md 참조")
