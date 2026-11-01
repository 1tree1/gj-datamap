# front_pages_b2 — 06 사회적 문제 (검증된 자료 계열로 교체한 판; front_pages_b.py 의 같은 이름 슬라이드를 덮어쓴다)

@slide("social")
def _(d):
    s = std(d, "social", "대지분석 : 사회적 문제", "사회적 문제", "방문은 늘고 있으나 원도심의 거주·고용·야간 활동은 줄거나 부족합니다.", scale=["경주시", "원도심"])
    gap = 0.155; cw = (CW - gap * 2) / 3
    X = [LM + i * (cw + gap) for i in range(3)]
    heads = [("거주·고용", "원도심 · 황오동", RED), ("방문", "경주시 · 황오동 설문", ZS), ("정주·야간", "원도심 8개 분석 구역", YEL)]
    for x, (h, u, col) in zip(X, heads):
        rect(s, x, 1.5, 0.07, 0.34, fill=col)
        text(s, x + 0.15, 1.5, 1.7, 0.34, h, size=12, bold=True, anchor="m", tag="so-h")
        text(s, x + cw - 1.9, 1.5, 1.9, 0.34, u, size=8.5, color=GRAY, align="r", anchor="m", tag="so-u")
        line(s, x, 1.88, x + cw, 1.88, LINE, 0.75)
    y0 = 2.0; kw = (cw - 0.1) / 2
    # ── 열 1: 감소율
    x = X[0]
    text(s, x, y0, cw, 0.22, "감소율(%)  ※ 기간·범위가 다른 지표를 함께 보입니다", size=8.5, color=GRAY, tag="so-cap")
    rows = [("인구", "2015→2025 · 옛 중부동 합산", 32.7, RED), ("20~39세 인구", "2018→2025.07 · 옛 황오동 단독", 44.0, RED), ("종사자", "2018→2023 · 사업지 격자 32셀", 23.1, "#E67A7C"), ("주택", "2018→2023 · 격자 32셀", 12.6, "#F0B1B2"), ("사업체", "2018→2023 · 격자 32셀", 2.9, "#F0B1B2")]
    for i, (lab, per, v, col) in enumerate(rows):
        yy = y0 + 0.32 + i * 0.4
        text(s, x, yy - 0.03, 1.7, 0.22, lab, size=9.5, bold=(i in (0, 1, 2)), anchor="m", tag="so-r")
        text(s, x, yy + 0.17, 1.8, 0.17, per, size=7.3, color=GRAY, anchor="m", tag="so-p")
        bw = 1.0 * v / 44.0
        rect(s, x + 1.85, yy + 0.02, bw, 0.22, fill=col)
        text(s, x + 1.85 + bw + 0.05, yy - 0.02, 0.7, 0.3, "−%.1f" % v, size=10, bold=True, color=INK, anchor="m", tag="so-v")
    kpi(s, x, 4.45, kw, 0.98, "−32.7%", "황오동 인구", "최근 10년 [T2]", color=RED, fill="#FBEDED", big_size=19, desc_size=8)
    kpi(s, x + kw + 0.1, 4.45, kw, 0.98, "43.8%", "65세 이상 비율", "황오동, 2026-08 [T2]", color=RED, fill="#FBEDED", big_size=19, desc_size=8)
    text(s, x, 5.5, cw, 0.4, [dict(text="사업지 격자에서 종사자가 사업체 수보다 크게 줄었습니다.", size=9.3, bold=True, space_after=1),
                              dict(text="전략계획이 원도심 쇠퇴의 원인으로 든 문단입니다 [T1, 2022 p.16]", size=8.3, color=INK2)], tag="so-f1")
    qimg = qcrop(DOC + r"\D06_strat_p26_center_weakening_hl.png", [(0, 0, 1835, 365)], "q_strat_p16")
    if have(qimg):
        qw_, qh_ = Image.open(qimg).size; fw = cw - 0.06; fh = fw * qh_ / qw_
        rect(s, x, 5.92, fw + 0.06, fh + 0.06, fill="#FFFFFF", line="#C7CDD4", line_w=0.75)
        picture(s, qimg, x + 0.03, 5.95, fw, fh, mode="contain")
    else: pic_or_ph(s, None, x, 5.93, 2.9, 0.95, "전략계획 원문 발췌")
    # ── 열 2: 방문
    x = X[1]
    text(s, x, y0, cw, 0.22, "외지인 방문 연인원 [경주시, T2]", size=8.5, color=GRAY, tag="so-cap")
    for i, (yr, v) in enumerate([("2024", 4710), ("2025", 5020)]):
        yy = y0 + 0.28 + i * 0.3
        text(s, x, yy, 0.5, 0.24, yr, size=9.5, anchor="m", tag="so-r")
        bw = 1.7 * v / 5020
        rect(s, x + 0.55, yy + 0.03, bw, 0.2, fill=(ZS if i == 1 else "#F6C6DB"))
        text(s, x + 0.55 + bw + 0.05, yy, 1.0, 0.26, "%s만" % format(v, ","), size=9.5, bold=True, anchor="m", tag="so-v")
    text(s, x + cw - 0.7, y0 + 0.28, 0.7, 0.3, "+6.6%", size=10, bold=True, color=BLUE, align="r", anchor="m", tag="so-d")
    text(s, x, y0 + 0.98, cw, 0.22, "황오동 방문객 설문(2024, n=188) [T2]", size=8.5, color=GRAY, tag="so-cap")
    tw = cw - 0.9
    yy = y0 + 1.24
    text(s, x, yy, 0.85, 0.26, "체류 시간", size=9, anchor="m", tag="so-r")
    rect(s, x + 0.88, yy + 0.02, tw * 0.79, 0.22, fill=RED); rect(s, x + 0.88 + tw * 0.79, yy + 0.02, tw * 0.21, 0.22, fill="#D8DCE1")
    text(s, x + 0.92, yy, 1.8, 0.26, "3시간 미만 79%", size=8.5, bold=True, color="#FFFFFF", anchor="m", tag="so-in")
    yy = y0 + 1.58
    text(s, x, yy, 0.85, 0.26, "1인 소비액", size=9, anchor="m", tag="so-r")
    segs = [(10.1, "#D8DCE1"), (64.9, "#C7CDD4"), (22.3, "#8FA9CF"), (2.7, BLUE)]
    xx = x + 0.88
    for v, col in segs:
        rect(s, xx, yy + 0.02, tw * v / 100, 0.22, fill=col); xx += tw * v / 100
    text(s, x + 0.9, yy + 0.25, tw, 0.2, "5만 원 미만 75%  ·  10만 원 이상 2.7%", size=8, bold=True, color=BLUE, anchor="m", tag="so-in2")
    text(s, x, y0 + 2.12, cw, 0.22, "황오동 업종군 실질 순증(2024, 점포형 중 최대 증감) [T2]", size=8.5, color=GRAY, tag="so-cap")
    ox = x + 2.35                                       # 영점: 라벨은 왼쪽, 감소(음수)는 영점 왼쪽, 증가는 오른쪽
    line(s, ox, y0 + 2.36, ox, y0 + 2.86, "#8F8F8F", 0.75)
    text(s, x, y0 + 2.36, 1.25, 0.24, "숙박·체류", size=9, anchor="m", tag="so-r"); rect(s, ox, y0 + 2.4, 0.75 * 5 / 9, 0.17, fill=ZS); text(s, ox + 0.75 * 5 / 9 + 0.05, y0 + 2.36, 0.5, 0.24, "+5", size=9.5, bold=True, anchor="m", tag="so-v")
    text(s, x, y0 + 2.62, 1.25, 0.24, "생활소매·식품제조", size=8.5, anchor="m", tag="so-r"); rect(s, ox - 0.75, y0 + 2.66, 0.75, 0.17, fill="#8F8F8F"); text(s, ox - 0.75 - 0.4, y0 + 2.62, 0.38, 0.24, "−9", size=9.5, bold=True, anchor="m", align="r", tag="so-v")
    kpi(s, x, 4.92, kw, 1.0, "5,020만", "방문 연인원(2025)", "연인원, 총량 아님 [T2]", color=BLUE, big_size=17, desc_size=7.8)
    kpi(s, x + kw + 0.1, 4.92, kw, 1.0, "79%", "체류 3시간 미만", "2024 설문, 축제 현장 포함 [T2]", color=RED, fill="#FBEDED", big_size=17, desc_size=7.8)
    text(s, x, 6.0, cw, 0.84, [dict(text="방문은 늘었지만 체류와 소비는 크지 않습니다.", size=9.8, bold=True, space_after=2),
                                dict(text="점포형 업종에서는 숙박·체류가 가장 크게 늘고 생활소매·식품제조가 가장 크게 줄어, 방문 증가가 생활 기반으로 이어지지 않는 징후입니다 [T2].", size=8.5, color=INK2)], tag="so-f2")
    # ── 열 3: 야간
    x = X[2]
    text(s, x, y0, cw, 0.22, "시간대별 유동 비중(%)  [소상공인365, 2026-06, T2]", size=8.5, color=GRAY, tag="so-cap")
    text(s, x + 1.5, y0 + 0.24, 0.9, 0.18, "저녁 18~23시", size=7.5, color=GRAY, tag="so-zh"); text(s, x + 2.62, y0 + 0.24, 0.9, 0.18, "야간 23~05시", size=7.5, color=GRAY, tag="so-zh")
    for i, (nm, ev, ng) in enumerate(SOCIAL_ZONES):
        yy = y0 + 0.44 + i * 0.255
        hl = nm.startswith("시청"); pd = nm.startswith("폐역")
        text(s, x, yy, 1.5, 0.22, nm, size=8.3, bold=(hl or pd), color=(RED if pd else INK), anchor="m", tag="so-zn")
        c1 = YEL if hl else ("#F0A5A6" if pd else "#D8DCE1")
        rect(s, x + 1.5, yy + 0.04, 0.62 * ev / 30, 0.14, fill=c1); text(s, x + 1.5 + 0.62 * ev / 30 + 0.03, yy, 0.45, 0.22, "%.1f" % ev, size=7.5, bold=(hl or pd), anchor="m", tag="so-zv")
        rect(s, x + 2.62, yy + 0.04, 0.42 * ng / 7, 0.14, fill=c1); text(s, x + 2.62 + 0.42 * ng / 7 + 0.03, yy, 0.4, 0.22, "%.1f" % ng, size=7.5, bold=(hl or pd), anchor="m", tag="so-zv")
    kpi(s, x, 4.92, kw, 1.0, "0", "결정도 주거용지", "고시 2026-8호 [T1]", color=RED, fill="#FBEDED", big_size=17, desc_size=7.8)
    kpi(s, x + kw + 0.1, 4.92, kw, 1.0, "73.8%", "1~2인 가구", "원도심 4개 동 82.6%(성건동 포함) [T2]", color=BLUE, big_size=17, desc_size=7.8)
    text(s, x, 6.0, cw, 0.84, [dict(text="폐역 구역의 주거 인구는 27명, 직장 인구는 117명으로 추정됩니다.", size=9.3, bold=True, space_after=2),
                                dict(text="시청 반경 500m만 주거(9,145명)와 직장(8,374명)이 균형을 이루고 저녁 비중이 가장 높습니다. 경주시 20~34세는 2020~2025년 7,249명 순유출입니다(연도별 −1,951명에서 −349명으로 감소) [T2].", size=8.3, color=INK2)], tag="so-f3")
    takeaway(s, LM, 6.9, CW, 0.88, "방문 지표는 늘고 있으나 거주·고용 지표는 줄고 저녁 이후의 활동은 약합니다.",
             "방문 확대만으로는 원도심의 쇠퇴 구조를 바꾸기 어렵습니다. 근로·정주 인구를 확보하고 방문을 체류로 전환하는 것이 과제입니다.", bar=RED, lead_size=10.5, body_size=9)
    notes(s, "수치 근거와 주의. (1) 황오동 인구 −32.7%(2015→2025, 옛 중부동 합산, 행안부 주민등록, T2)와 법정 쇠퇴진단의 −43.0%(2022 전략계획, T1)는 기간·경계가 달라 하나만 씁니다. 20~39세 −44%는 옛 황오동 단독 연령 구조(1,414명→787명, 2018→2025.07, 황오동 모니터링 보고서)입니다. (2) 격자 32셀(도시재생 사업지) 2018→2023은 인구 −14.4%, 사업체 −2.9%, 종사자 −23.1%, 주택 −12.6%입니다. 같은 기간 황오동 전체 종사자는 −4.8%(6,192→5,893)이므로 '고용 감소'는 사업지 격자에 한정한 값입니다. 보고서의 '창업 70건 +45.8%'는 임시영업 27건(축제 영업신고 포함)이 섞인 값이라 인용하지 않습니다. (3) 방문 연인원은 한국관광 데이터랩(KT 이동통신 추정) 외지인 연인원이며 2024년 47,098,236(보도 '4,709만'은 내림), 2025년 50,203,225로 +6.6%입니다. 총량이 아니라 같은 사람을 날짜마다 다시 센 값입니다(공식 다운로드로 치환 예정). (4) 방문객 설문 2024(n=188)는 체류 1~3시간 79.1%(보고서 종합표의 '3시간 미만' 표기), 1인 소비 1만 원 미만 10.1%·1~5만 원 64.9%·5~10만 원 22.3%·10만 원 이상 2.7%입니다. 방문 계기의 50%가 축제이고 응답자의 56%가 경주 시민이며 조사 장소가 해마다 달라 시계열 비교는 하지 않습니다. (5) 업종군 순증은 2024 황오동 사업지의 실질 건수(임시영업 27건 제외)로, 점포형 업종 중 숙박·체류 +5가 가장 크고 생활소매·식품제조 −9가 가장 작습니다(무점포 통신판매는 +10). (6) 시간대별 유동은 소상공인365 통신사 체류 추정치(2026-06 단월), 8개 구역은 서로 겹칩니다. 폐역 구역의 주거 27명·직장 117명은 2026 상반기 값입니다. 청년 순유출은 KOSIS 국내인구이동통계(20~34세, 2020~2025).")
