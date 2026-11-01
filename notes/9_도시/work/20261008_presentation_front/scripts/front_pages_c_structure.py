# front_pages_c_structure — 07 도시구조적 문제 (원문 발췌를 가로 행으로, 6개 구역 막대; front_pages_c.py 의 같은 이름 슬라이드를 덮어쓴다)

# 서로 겹치지 않는 분석 구역 위주(A·B·D·F·G·H). S07: ha당 일평균 유동, 2025.06~2026.06 13개월 평균
DENSITY6 = [("성동시장 반경 200m", 1175), ("황리단길 반경 300m", 757), ("황오동 활성화구역", 715), ("시청 반경 500m", 596), ("행복황촌 구역", 80), ("폐역 구역(고시)", 79)]

@slide("structure")
def _(d):
    s = std(d, "structure", "대지분석 : 도시구조적 문제", "도시구조적 문제", "철도 부지가 동서 보행 흐름을 단절하고, 맞닿은 두 구역 사이에 밀도 차이가 나타납니다.", scale=["대상지", "원도심"])
    mx, my, mw = LM, 1.5, 4.1; mh = mw * 4 / 3
    pic_or_ph(s, first(MP + r"\m4_walk_barrier.png"), mx, my, mw, mh, "보행 단절 지도")
    credit_below(s, mx, my, mw, mh, "국토지리정보원 연속수치지도 기반 자체 분석 [T2]")
    x0 = 4.85; w = SW - RM - x0; kw = (w - 0.2) / 3
    kpi(s, x0, 1.5, kw, 0.92, "985m", "도로 횡단 부재 구간", "남북 923m 구역 + 양 끝 밖 포함 [T2]", color=RED, fill="#FBEDED", big_size=18, desc_size=7.6, label_size=10)
    kpi(s, x0 + kw + 0.1, 1.5, kw, 0.92, "1개", "보행 육교", "폭 3.2m · 길이 약 216m, 개방 여부 확인 전 [T2]", color=RED, fill="#FBEDED", big_size=18, desc_size=7.6, label_size=10)
    kpi(s, x0 + 2 * (kw + 0.1), 1.5, kw, 0.92, "3.5배", "동서 우회율", "폐선 양쪽 60m 지점 간 18개 단면 중앙값 [T2]", color=RED, fill="#FBEDED", big_size=18, desc_size=7.6, label_size=10)
    # 계획 문서와 연구의 진단 — 원문 발췌(강조 표시한 문장만)
    qy = 2.54
    text(s, x0, qy, w, 0.24, "계획 문서와 연구의 진단 (원문 발췌, 형광 표시)", size=9.5, bold=True, tag="st-qh")
    qs = [(qcrop(DOC + r"\D06_plan30_p299_urban_split_hl.png", [(40, 50, 1938, 300), (40, 750, 1938, 930)], "q_plan30_split"), 4.05,
           "2030 경주도시기본계획(2017) [T1]", "기존 시가지가 철도와 사적지구 지정 등으로 동서·남북으로 분리되어 있고, 경주역사가 도심기능의 저해 요인으로 기술됩니다."),
          (qcrop(DOC + r"\D06_s417_p106_border_vacuum_text_hl.png", [(0, 0, 1338, 330)], "q_s417_vacuum"), 2.7,
           "원도심 미래구상 기획연구(2025) [T2]", "철도 부지가 '경계공백지대'로 기능하여 보행 단절과 인접 구역의 쇠퇴를 유발한다고 진단합니다.")]
    y = qy + 0.28
    for img, iw_, cap_h, cap_b in qs:
        if have(img):
            wq, hq = Image.open(img).size; ih_ = iw_ * hq / wq
            rect(s, x0, y, iw_ + 0.08, ih_ + 0.08, fill="#FFFFFF", line="#C7CDD4", line_w=0.75)
            picture(s, img, x0 + 0.04, y + 0.04, iw_, ih_, mode="contain")
        else:
            ih_ = 0.9; pic_or_ph(s, None, x0, y, iw_, ih_, "원문 발췌")
        text(s, x0 + iw_ + 0.22, y, w - iw_ - 0.22, ih_ + 0.08, [dict(text=cap_h, size=8.8, bold=True, color=BLUE, space_after=2), dict(text=cap_b, size=8.4, color=INK2)], anchor="m", line=1.1, tag="st-qc")
        y += ih_ + 0.2
    # 밀도 낙차 — 6개 구역
    dy = y + 0.02
    text(s, x0, dy, w, 0.24, "동서 밀도 낙차 — 하루 평균 유동(명/ha, 통신사 추정, 2025.06~2026.06) [T2]", size=9.5, bold=True, tag="st-dh")
    vmax = max(v for _, v in DENSITY6); step = 0.215
    for i, (lab, v) in enumerate(DENSITY6):
        yy = dy + 0.32 + i * step
        hl = ("성동시장" in lab) or ("폐역" in lab)
        col = BLUE if "성동시장" in lab else (RED if "폐역" in lab else "#C7CDD4")
        hbars(s, x0, yy, [(lab, v)], 1.55, 2.5, vmax, step=step, bar_h=0.16, color=col, fmt=lambda t: format(t, ","), val_size=8.8, label_size=8.8, label_color=(INK if hl else INK2), val_w=0.8)
    box_text(s, x0 + w - 1.4, dy + 0.4, 1.4, 0.62, [dict(text="약 15배", size=16, bold=True, color=RED, align="c"), dict(text="두 구역의 거리 200m", size=7.6, color=GRAY, align="c")], fill="#FBEDED", radius=0.08, anchor="m", margin=(0.02, 0.02, 0.02, 0.02), tag="st-15")
    text(s, x0 + w - 2.6, dy + 1.06, 2.6, 0.32, "구역은 일부 겹치고, 통신사 체류 추정치이며 보행량이 아닙니다", size=7.2, color=GRAY, align="r", anchor="t", line=1.04, tag="st-dn")
    # 접근
    ay = dy + 0.32 + 6 * step + 0.08; aw = (w - 0.2) / 3
    kpi(s, x0, ay, aw, 0.72, "76.9%", "자가용 방문", "2013년 60%에서 증가, 2024 [T2]", color=BLUE, big_size=14, desc_size=7.4, label_size=9.2)
    kpi(s, x0 + aw + 0.1, ay, aw, 0.72, "38.8%", "주차시설 확충 요구", "교통 문제 1위, 2015년 조사 [T1]", color=BLUE, big_size=14, desc_size=7.4, label_size=9.2)
    kpi(s, x0 + 2 * (aw + 0.1), ay, aw, 0.72, "1,297면", "반경 1km 공영주차장", "쪽샘 임시주차장 496면 포함 [T1]", color=BLUE, big_size=14, desc_size=7.4, label_size=9.2)
    takeaway(s, LM, 7.24, CW, 0.7, "철도 부지가 동서 보행 흐름을 단절하고, 성동시장 쪽과 폐역 구역 사이에 큰 밀도 차이가 나타납니다.",
             "연결이 선행되지 않으면 성동시장의 활력이 부지로 이어지기 어렵습니다. 방문은 자가용 중심이어서 도착 지점에서의 보행 전환도 함께 필요합니다.", bar=RED, lead_size=10, body_size=8.6)
    notes(s, "단절 수치의 출처와 정의. 985m = 구역 923m + 남단 밖 31m + 북단 밖 30m(도로 횡단이 없는 구간, 연속수치지도 도로중심선·철도중심선, T2). 육교 1개는 연속수치지도 'N3A_A0063321'(폭 3.2m, 길이 216.3m)이며 개방 여부는 현장 확인 전입니다. 우회율 3.5는 폐선 양쪽 60m 지점 간, 구역 y 범위 50m 간격 18개 단면의 중앙값(최대 약 5.3, 최소 1.5, 육교 제외, 인도·횡단보도 미반영)입니다. 지도의 파랑 실선은 다른 정의의 값(부지 양쪽 두 지점 직선 601m에 대해 도로망 최단경로 1,531m, 2.55배)이므로 두 값을 섞어 말하지 않습니다. 기존 가로 끝 37곳은 경계 6m 이내에서 접촉·관통하고 경계와 직교에 가까운 도로(서 9·동 18·남 7·북 3)입니다. 원문 발췌는 2030 경주도시기본계획(2017.12) 인쇄쪽 285의 '기존 시가지의 공간적 분열'·'도심기능의 저해요인 산재', 원도심 미래구상 기획연구(2025.07) 인쇄쪽 105입니다. 밀도 낙차는 소상공인365(통신사 체류 추정, 2025.06~2026.06 13개월 평균)이며, 폐역 구역은 고시 구역 폴리곤(158,721㎡)이고 79,438㎡ 구상 범위가 아닙니다. 성동시장 반경 200m의 일부(약 18%)는 폐역 구역 안에 겹칩니다. 8개 분석 구역 중 서로 겹치는 구역(구역 중심 300m, 구역 경계+300m)은 막대에서 제외했습니다. 자가용 76.9%는 경주시 관광실태조사(2024, 조사 지점 6곳으로 원도심 제외, 2013년 60.0%, 2021년 84.2%), 주차 38.8%와 공영주차장 1,297면은 2030 기본계획 시민의식조사(2015.9~10, 1,408부, 인쇄쪽 79)와 구역 중심 반경 1km 계산입니다.")
