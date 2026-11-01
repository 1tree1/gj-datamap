# -*- coding: utf-8 -*-
"""04장 2차 수정 — 그림 제작 B: 개념 도식(컨셉 위계 · 명칭 3시점 · 목표-전략-근거 · 성립 가설 3고리 · 성과지표 3축 · 선례 교훈)
자료는 본문 표·문장에 이미 있는 값만 쓴다."""
import textwrap
from figkit_46 import *


# ───────── 그림 4-1 컨셉 위계 ─────────
def concept_hierarchy():
    W, H = WIDE, 112
    fig, ax = new(W, H)
    T(ax, 8, 6, "위계", 11, G2, "left", w="semibold"); T(ax, 78, 6, "명칭 · 내용", 11, G2, w="semibold")
    T(ax, 262, 6, "공간 · 계획 번역(최종 마스터플랜)", 11, G2, w="semibold")
    line(ax, [4, W - 4], [10, 10], G4, 0.8)
    rows = [
        ("프로젝트", RED, "NEXUS 1918", "멈춘 역, 경주를 다시 연결하는 중심", "폐역 부지를 동서·남북 연결의 결절점으로 설정", None),
        ("설계 컨셉", INK, "CULTURAL INTERCHANGE", "도시의 흐름을 바꾸는 문화환승 · 방문 동선과 주민 생활이 교차하는 환승점", "남북 관광 축과 동서 생활 축이 만나는 교차광장", None),
        ("전략", G1, "CONNECT  ·  EXCHANGE  ·  SPREAD", "접속(동서·남북 연결) · 교차·전환(관광과 일상, 문화·창작의 접점) · 확산(성동시장·원도심으로 활동 확산, 일자리·주거)", "4.3절 전략의 공간 배치", None),
        ("건축 표현", G2, "ELEVATED CULTURAL PLATFORM", "저층 1~3층 분동 문화시설 + 중앙 오픈스페이스 + 공중광장·상층 녹지산책로, 매장유산 조건에 맞는 지상 구성", None,
         [("반영", "저층 분동 · 건축물 41동 2~5층", RED), ("반영", "중앙 오픈스페이스 · 교차광장", RED), ("미반영", "공중광장 · 상층 녹지산책로", G3)]),
    ]
    y0, rh, gap = 13, 21, 3.2
    for i, (tier, col, name, desc, trans, chips) in enumerate(rows):
        y = y0 + i * (rh + gap)
        box(ax, 4, y, 62, rh, fc=col, ec=col, r=2)
        T(ax, 35, y + rh / 2, tier, 15, "white", "center", w="bold")
        T(ax, 78, y + 5.6, name, 16, col if col != G2 else G1, w="bold")
        lines = textwrap.wrap(desc, width=64)
        for j, l in enumerate(lines[:2]): T(ax, 78, y + 12.4 + j * 5.0, l, 10.5, G1)
        if trans: T(ax, 262, y + rh / 2, trans, 12, INK, va="center")
        if chips:
            for j, (st, tx, cc) in enumerate(chips):
                yy = y + 1.6 + j * 6.5
                box(ax, 262, yy, 17, 5.6, fc=cc, ec=cc, r=1.0); T(ax, 270.5, yy + 2.9, st, 10, "white", "center", w="semibold")
                T(ax, 282, yy + 2.9, tx, 10.5, INK)
        if i < 3: arrow(ax, 35, y + rh + 0.3, 35, y + rh + gap - 0.3, G1, 1.4, 9)
    return save(fig, "04_concept_hierarchy.png")


# ───────── 그림 4-2 명칭의 세 시점 ─────────
def name_timeline():
    W, H = COL, 72
    fig, ax = new(W, H)
    x0, x1, y = 12, W - 12, 32
    line(ax, [x0, x1], [y, y], INK, 1.6, 2)
    pts = [(24, "1918", "경주역 개업", "첫 역은 사정동", RED, "up"),
           (96, "1936", "현 위치로 이전", "대상지 위의 역", INK, "down"),
           (156, "2021", "폐역", "2021.12 동해선 이설", G2, "up")]
    for x, a, b, c, col, side in pts:
        ax.add_patch(Circle((x, y), 2.2, fc=col, ec="white", lw=1.0, zorder=5))
        if side == "up":
            T(ax, x, y - 20, a, 16, col, "center", w="bold"); T(ax, x, y - 12.5, b, 11, INK, "center", w="medium"); T(ax, x, y - 6.3, c, 10, G2, "center")
        else:
            T(ax, x, y + 9, a, 16, col, "center", w="bold"); T(ax, x, y + 16.2, b, 11, INK, "center", w="medium"); T(ax, x, y + 22, c, 10, G2, "center")
    box(ax, 5, 60.5, 66, 8, fc=XRED, ec=RED, r=1.2, lw=0.8)
    T(ax, 38, 64.6, "NEXUS 1918 = 경주역의 출발", 10.5, RED, "center", w="semibold")
    return save(fig, "04_name_timeline.png")


# ───────── 그림 4-3 목표 · 전략 · 근거 강도 ─────────
def goal_strategy():
    W, H = WIDE, 98
    fig, ax = new(W, H)
    T(ax, 4, 6, "계획 목표(03장)", 11, G2, w="semibold"); T(ax, 150, 6, "전략", 11, G2, w="semibold")
    T(ax, 207, 6, "대응하는 공간 수단", 11, G2, w="semibold"); T(ax, 318, 6, "근거 강도", 11, G2, w="semibold")
    line(ax, [4, W - 4], [10, 10], G4, 0.8)
    goals = [("01", "동서/남북 생활권 연계 강화", "CONNECT", RED, "동서 선형공원 · 남북 보행축 · 횡단 가로 5곳", 4, "강함"),
             ("02", "원도심 중심기능 회복", "SPREAD", G1, "북측 공공청사 · 공공업무", 3, "중간"),
             ("03", "지역경제 활성화", "EXCHANGE", DRED, "중앙 접점 장치 · 남측 관문", 2, "약함~중간"),
             ("04", "청년 정주기반 확충", "SPREAD", G1, "청년·신혼 공공임대 · 청년창업지원 · 생활문화·돌봄", 1, "문제는 강함, 해법은 약함")]
    y0, rh, gap = 14, 16.5, 2.6
    for i, (no, g, st, col, means, lvl, lab) in enumerate(goals):
        y = y0 + i * (rh + gap)
        box(ax, 4, y, 132, rh, fc=G6, ec=G4, r=1.5)
        T(ax, 11, y + rh / 2, no, 18, RED, w="bold"); T(ax, 26, y + rh / 2, g, 13.5, INK, w="semibold")
        box(ax, 148, y + 2.6, 46, rh - 5.2, fc=col, ec=col, r=1.5); T(ax, 171, y + rh / 2, st, 12.5, "white", "center", w="bold")
        arrow(ax, 136.5, y + rh / 2, 147.5, y + rh / 2, G2, 1.2, 10)
        T(ax, 207, y + rh / 2, means, 11.5, INK)
        for k in range(4):
            rect(ax, 318 + k * 15.5, y + 2.2, 14, 4.4, fc=RED if k < lvl else G5, ec="none")
        T(ax, 318, y + 11.4, lab, 10.5, INK, w="medium")
    T(ax, 4, H - 3, "근거 강도는 승인계획 · 측정 자료의 유무에 따른 설계팀 판정이며 막대는 상대 표시입니다.", 10, G2)
    return save(fig, "04_goal_strategy.png")


# ───────── 그림 4-8 관광–정주 가설 3고리 + 성립 조건 5개 ─────────
def hypothesis_chain():
    W, H = WIDE, 106
    fig, ax = new(W, H)
    T(ax, 4, 5.5, "관광–정주 가설의 세 고리와 문헌 판정", 11.5, INK, w="bold")
    line(ax, [4, W - 4], [10, 10], G4, 0.8)
    links = [("A", "관광 확대", "→ 지역 소득·일자리", "찬성", RED, 3, "유럽 179개 지역 1인당 GDP 성장(+) · 경주 사적지 1개소당 연 생산유발 148.46억 원"),
             ("B", "소득이 주민에게 남는가", "(지역 잔류)", "조건부", "#d36a7a", 2, "지역 소유 소기업 밀도는 소득 성장(+) · 지역 잔류 지출은 체류일수만이 예측"),
             ("C", "주민 소득·일자리", "→ 정주 인구", "직접 검증 없음", G3, 1, "체류인구는 늘었으나 정주 순유입은 미증가(3건) · 황남동 2015→2025 −44.8%")]
    bw, bg = 110, 20
    for i, (k, a, b, st, col, lv, ev) in enumerate(links):
        xx = 4 + i * (bw + bg)
        box(ax, xx, 14, bw, 22, fc="white", ec=col, lw=1.8, r=2)
        ax.add_patch(Circle((xx + 8, 25), 5.2, fc=col, ec="none", zorder=4)); T(ax, xx + 8, 25.3, k, 13, "white", "center", w="bold")
        T(ax, xx + 17, 21, a, 12.5, INK, w="semibold"); T(ax, xx + 17, 29.5, b, 11, G1)
        if i < 2: arrow(ax, xx + bw + 1, 25, xx + bw + bg - 1, 25, G1, 1.6, 12)
        T(ax, xx + 2, 42, "판정", 10.5, G2); T(ax, xx + 14, 42, st, 11.5, col if col != G3 else G2, w="bold")
        for j in range(3): rect(ax, xx + 2 + j * 36, 46, 34, 3.6, fc=col if j < lv else G5, ec="none")
        T(ax, xx + 2, 54.5, ev[: ev.index(" · ")], 10, G1); T(ax, xx + 2, 60, ev[ev.index(" · ") + 3:], 10, G1)
    line(ax, [4, W - 4], [68, 68], G4, 0.8)
    T(ax, 4, 74, "따라서 가설을 전제로 쓰지 않고, 성립 조건 5개를 설계 요구사항으로 둠", 11.5, RED, w="bold")
    conds = ["01 소득의 지역 잔류", "02 일자리의 질", "03 주거 공급과 관광 수요의 비경합", "04 관광 구역과 생활권의 완충", "05 규모의 한계"]
    xs = 4; wid = [62, 46, 88, 82, 52]
    for c, w_ in zip(conds, wid):
        box(ax, xs, 80, w_ - 3, 11, fc=XRED, ec=RED, lw=0.8, r=1.5); T(ax, xs + (w_ - 3) / 2, 85.6, c, 11.5, INK, "center", w="medium"); xs += w_ + 1.5
    T(ax, 4, 99, "조건 5개는 개별 논문의 결론이 아니라 문헌을 종합한 설계팀 해석입니다.", 10, G2)
    return save(fig, "04_hypothesis_chain.png")


# ───────── 그림 4-9 성과지표 3축 ─────────
def kpi_axes():
    W, H = COL, 96
    fig, ax = new(W, H)
    cols = [("방문 축", RED, ["체류시간", "숙박 비율", "소비"]), ("정주 축", INK, ["25~39세 거주 인구", "생활업종 비율", "야간 활동"]),
            ("환류 축", G2, ["지역 사업체 매출 비중", "청년 정규 일자리 수", "임대료", "도시민박 등록 수"])]
    cw = 55; g = 5
    for i, (t, c, items) in enumerate(cols):
        x = 4 + i * (cw + g)
        box(ax, x, 5, cw, 12, fc=c, ec=c, r=1.5); T(ax, x + cw / 2, 11.2, t, 14, "white", "center", w="bold")
        for j, it in enumerate(items):
            y = 21 + j * 11.5
            box(ax, x, y, cw, 9.2, fc=G6, ec=G4, r=1.2); T(ax, x + cw / 2, y + 4.8, it, 10.5, INK, "center")
    box(ax, 4, 72, W - 8, 18, fc=XRED, ec=RED, lw=0.9, r=1.5)
    T(ax, W / 2, 77.5, "세 축을 같은 정의 · 같은 범위로 나란히 보고", 12, RED, "center", w="bold")
    T(ax, W / 2, 84, "관광 업종의 증가와 생활 업종의 감소는 회복이 아니라 치환으로 읽음", 10.5, INK, "center")
    return save(fig, "04_kpi_axes.png")


# ───────── 그림 4-11 선례에서 빌리는 교훈 5개 ─────────
def lessons():
    W, H = WIDE, 100
    fig, ax = new(W, H)
    T(ax, 4, 6, "교훈", 11, G2, w="semibold"); T(ax, 168, 6, "근거 선례", 11, G2, w="semibold"); T(ax, 296, 6, "본 계획에서 반영하는 곳", 11, G2, w="semibold")
    line(ax, [4, W - 4], [10, 10], G4, 0.8)
    L = [("①", "비가역 투자는 뒤로 두는 순서", "교토 우메코지 · 구 안동역", "09장 단계별 추진"),
         ("②", "단일 대형이 아닌 분산 삽입의 대안", "부산 혁신도시 ↔ 울산 우정혁신도시", "대안 시나리오(작성 전)"),
         ("③", "조성 조직이 아닌 운영 조직의 설계", "광주 푸른길", "09장 운영 주체 · 재원"),
         ("④", "방문 · 정주 두 축의 병기", "전주 한옥마을", "4.4절 성과지표 3축"),
         ("⑤", "연속성과 최약 지점 통과 폭의 지표", "광주 푸른길", "05장 도로계획 · 횡단 간격")]
    y0, rh, gap = 13.5, 14, 2.6
    for i, (n, a, b, c) in enumerate(L):
        y = y0 + i * (rh + gap)
        box(ax, 4, y, 156, rh, fc=G6, ec=G4, r=1.5); T(ax, 10, y + rh / 2, n, 16, RED, w="bold"); T(ax, 22, y + rh / 2, a, 13, INK, w="semibold")
        arrow(ax, 160.5, y + rh / 2, 167, y + rh / 2, G2, 1.0, 9)
        box(ax, 168, y, 122, rh, fc="white", ec=G3, r=1.5); T(ax, 174, y + rh / 2, b, 12, G1)
        arrow(ax, 290.5, y + rh / 2, 295.5, y + rh / 2, G2, 1.0, 9)
        box(ax, 296, y, 80, rh, fc=XRED, ec=RED, lw=0.8, r=1.5); T(ax, 301, y + rh / 2, c, 11.5, INK, w="medium")
    return save(fig, "04_lessons.png")


if __name__ == "__main__":
    concept_hierarchy(); name_timeline(); goal_strategy(); hypothesis_chain(); kpi_axes(); lessons()
