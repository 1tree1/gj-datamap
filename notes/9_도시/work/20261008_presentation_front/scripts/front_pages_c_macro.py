# front_pages_c_macro — 08 대지분석 MACRO (원문 발췌 도판을 넣은 판; front_pages_c.py 의 같은 이름 슬라이드를 덮어쓴다)

@slide("macro")
def _(d):
    s = std(d, "macro", "대지분석 : MACRO", "대지분석 MACRO", "대상지는 원도심 자산이 도보 5~15분에 모이는 위치이며, 폐선축과 환승·행정 기능 계획이 만나는 자리입니다.", scale=["경주시", "원도심"])
    gap = 0.145; w1, w2, w3 = 2.95, 4.15, 3.443
    xs = [LM, LM + w1 + gap, LM + w1 + w2 + 2 * gap]
    ys = 1.5
    heads = [("경주시", "도시의 틀"), ("원도심", "보행권 자산"), ("폐선축", "철도 체계와 상위계획")]
    for x, w, (a, b) in zip(xs, (w1, w2, w3), heads):
        text(s, x, ys, w, 0.28, [(( a + "  ", {"bold": True, "size": 11.5}), (b, {"bold": False, "size": 9, "color": GRAY}))], anchor="m", tag="ma-h")
        line(s, x, ys + 0.3, x + w, ys + 0.3, INK, 1.0)
    my = ys + 0.4
    # P1 경주시
    mh1 = w1 * 5 / 4
    pic_or_ph(s, first(MP + r"\m1_gyeongju_city.png"), xs[0], my, w1, mh1, "경주시 지도", mode="cover", align=(0.5, 0.35))
    text(s, xs[0], my + mh1 + 0.1, w1, 1.5, [dict(text=t, size=8.8, color=INK2, bullet=True, space_after=2.5) for t in
                                              ["건물이 모인 땅은 시 면적의 4.4%, 문화유산 구역·보존지역은 10.5% [T1]", "세계유산 구성요소 4건 [T1]", "인구 24.3만 명, 10년간 −6.1%, 65세 이상 30% [T2]"]], line=1.1, tag="ma-b1")
    # P2 원도심
    pic_or_ph(s, first(MP + r"\m3_site_distance.png", MP + r"\m2_oldcore_1km.png"), xs[1], my, w2, w2, "원도심 보행권 지도")
    text(s, xs[1], my + w2 + 0.1, w2, 1.0, [dict(text=t, size=8.8, color=INK2, bullet=True, space_after=2.5) for t in
                                             ["구 경주역 기준점에서 황오동 고분 345m · 성동시장 355m · 경주읍성 497m · 대릉원 523m · 황리단길 994m · 첨성대 1,030m(직선거리) [T2]", "반경 1km(고시 구역 무게중심 기준)의 건물 79%가 1층이고, 4m 미만 골목이 길의 40%, 땅의 69%가 문화유산 구역·보존지역입니다 [T2]"]], line=1.1, tag="ma-b2")
    # P3 폐선축·상위계획
    mh3 = 1.9
    pic_or_ph(s, first(MP + r"\m9_rail_axis_S3.png"), xs[2], my, w3, mh3, "폐선축 지도", mode="cover", align=(0.5, 0.5))
    text(s, xs[2], my + mh3 + 0.06, w3, 0.62, [dict(text=t, size=8.6, color=INK2, bullet=True, space_after=1.5) for t in
                                                ["2023년 폐철도 기본구상은 폐선축 80.3km, 폐역 17개소로 정리합니다(원문 미확인). 지도는 위치가 확인된 폐역 3개소만 표시합니다 [T2]", "KTX 경주역(건천읍)은 원도심에서 직선 8.6km [T2]"]], line=1.08, tag="ma-b3")
    ey = my + mh3 + 0.72
    for img, cap in [(DOC + r"\D06_plan30_p239_transfer_center_hl.png", "2030 경주도시기본계획 [T1] — 복합환승센터를 경주역에 설치"),
                     (DOC + r"\D06_plan30_p304_downtown_multicomplex_hl.png", "2030 경주도시기본계획 [T1] — 경주 역사부지에 행정·문화·상업·업무 멀티복합타운")]:
        if have(img):
            iw_, ih_ = Image.open(img).size; cwid = w3 if ih_ / iw_ < 0.3 else 2.6; fh = cwid * ih_ / iw_
            rect(s, xs[2], ey, cwid, fh + 0.04, fill="#FFFFFF", line="#C7CDD4", line_w=0.75)
            picture(s, img, xs[2] + 0.02, ey + 0.02, cwid - 0.04, fh, mode="contain"); ey += fh + 0.06
        text(s, xs[2], ey, w3, 0.2, cap, size=7.5, color=GRAY, anchor="m", tag="ma-cap"); ey += 0.24
    takeaway(s, LM, 7.0, CW, 0.88, "문화유산이 개발지를 제한하는 도시에서, 원도심의 한가운데에 쓰임을 새로 정할 수 있는 연속 공지가 놓여 있습니다.",
             "걸어서 닿는 자산이 많고, 폐선축·환승·행정 기능이 상위계획에서 이미 이 자리를 가리킵니다. 문제는 자산과 부지 사이의 연결과 기능입니다.", bar=BLUE, lead_size=10.3, body_size=8.8)
    notes(s, "MACRO는 경주시(S3)와 원도심(S2) 단위의 분석입니다. 경주시 수치는 도시의 틀을 설명하는 배경이며 대상지 시설 규모를 정당화하는 데 쓰지 않습니다. 건물이 모인 땅 4.4%는 V-World 용도지역(주거·상업·공업) 58.1㎢/1,318.9㎢(지도 재산정 4.40%), 문화유산 구역·보존지역 10.5%는 V-World 문화유산 보호 구역 138.4㎢(10.50%)입니다(T1). 인구 24.3만 명(2026-08 242,512명), 10년 −6.1%, 65세 이상 30.0%는 행정안전부 주민등록(KOSIS, T2). 거리는 지도의 구 경주역 기준점(OSM '구경주역' 점, 연속수치지도의 역사 건물 중심에서 61m 남서쪽) 기준 직선거리이며, 역사 건물 중심 기준으로 다시 재면 황오동 고분 400m, 대릉원 584m, 황리단길 1,055m로 6~16% 늘어납니다(나머지 5곳은 ±5% 이내). 두 기준의 값을 섞어 쓰지 않습니다. 거리는 넓은 유적은 가장 가까운 경계까지입니다(대릉원은 지오코딩값 2.7km가 아니라 523m). 폐선축 80.3km·폐역 17개소는 2023.04 경주시 폐철도 기본구상 인용(원문 미확보)입니다. 지도의 폐선은 OSM(T4) 선분 합 78.1km(병행선 포함, 단선 환산 약 63km)이고 영천·안강·울산 쪽 끝이 자료 범위에서 끊겨 80.3km를 검증할 수 없으며, 위치가 확인된 폐역은 구 경주역·옛 서경주역(금장)·불국사역 3개소입니다. 2030 기본계획은 복합환승센터를 경주역·시외버스터미널·KTX역에 두고(p.225), 이전적지에 행정·문화·상업·업무 멀티복합타운을 조성한다고 적습니다(p.290). 신경주역~보문 신교통을 원도심 경유로 계획하는 내용은 같은 계획의 시가지정비·교통계획입니다(T1).")
