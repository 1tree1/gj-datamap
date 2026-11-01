# front_pages_c — 07 도시구조적 문제 · 08 대지분석 MACRO · 09 대지분석 MICRO

# 8개 구역 유동(명/ha) — 데이터 계열 확정 전 기본값. 값은 research/data_series/footfall_8zones.csv 로 대체한다.


# ═════════════════════════ 07 도시구조적 문제 ═════════════════════════
# ═════════════════════════ 09 대지분석 MICRO ═════════════════════════
@slide("micro")
def _(d):
    s = std(d, "micro", "대지분석 : MICRO", "대지분석 MICRO", "대지는 높이와 지하로 대응하기 어려운 조건이며, 양쪽 도시조직과의 접속점이 설계의 출발점입니다.", scale=["대상지"])
    # 사진 6컷
    pw = 2.72; ph_ = 1.62; gx = 0.1; gy = 0.1
    shots = [(PH + r"\ph57_site_tracks_south.jpg", "① 육교에서 본 폐선로와 승강장(남향)", (0.5, 0.5)), (PH + r"\ph56_site_overpass.jpg", "② 동서를 잇는 유일한 보행 육교", (0.5, 0.5)),
             (PH + r"\ph59_site_remnants_ne.jpg", "③ 선로 잔재와 식생(북동향)", (0.5, 0.55)), (PH + r"\ph65_site_from_west_roof_wide.jpg", "④ 서측 건물에서 본 대상지와 원도심", (0.5, 0.5)),
             (PH + r"\ph03_west_wonhwaro_bus.jpg", "⑤ 서측 원화로 변의 상업 가로", (0.5, 0.45)), (PH + r"\ph62_east_lane_paved.jpg", "⑥ 동측 황오동의 낮은 골목", (0.5, 0.5))]
    for i, (p, cap, al) in enumerate(shots):
        x = LM + (i % 2) * (pw + gx); y = 1.5 + (i // 2) * (ph_ + gy)
        pic_or_ph(s, p, x, y, pw, ph_, cap, align=al)
        photo_credit(s, x, y, pw, ph_, cap + "  (답사 2026.09)", size=7)
    # 규제 4겹
    x0 = 6.2; w = SW - RM - x0
    text(s, x0, 1.5, w, 0.26, "규제와 유산 4겹", size=11.5, bold=True, tag="mi-h"); line(s, x0, 1.8, x0 + w, 1.8, INK, 1.0)
    layers = [("용도지역", "자연녹지 77.5% · 2종일반주거 16.2% · 일반상업 6.4%", "자연녹지의 법정 건폐율은 20%입니다 [T1]", MP + r"\m6a_zoning.png"),
              ("고도지구", "도심 20m 지구 87.5% · 15m 지구 11.3% (본 계획 경계 기준)", "20m는 삼층석탑 현상변경 허용기준을 수용한 값이어서 공공청사도 예외가 아닙니다 [T1]", MP + r"\m6b_height.png"),
              ("문화유산", "시굴 대상 145,879㎡ — 고시 구역 대비 93%", "1단계 지하 개발은 불가하며, 발굴 유예 조건은 2m 미만 성토와 성토 후 공원·주차장입니다 [T2]", MP + r"\m6c_heritage.png"),
              ("지구단위계획", "고시 2026-8호 — 근린공원 35% · 상업 27% · 공공청사 16% · 도로 12% · 문화 6% · 주차 4%", "주거용지는 없으며, 가구·획지·용도는 참고로 두고 새로 계획합니다 [T1]", MP + r"\m6d_plan.png")]
    ly = 1.9; lh = 0.93
    for i, (nm, a, b, img) in enumerate(layers):
        y = ly + i * lh
        rect(s, x0, y, w, lh - 0.07, fill=TINT, radius=0.05)
        pic_or_ph(s, img, x0 + 0.06, y + 0.06, 0.64, lh - 0.19, nm)
        num_chip(s, x0 + 0.8, y + 0.07, 0.24, i + 1, fill=BLUE, size=8.5)
        text(s, x0 + 1.1, y + 0.05, w - 1.2, 0.26, nm, size=10, bold=True, anchor="m", tag="mi-ln")
        text(s, x0 + 0.8, y + 0.31, w - 0.9, 0.34, a, size=8.5, bold=True, color=INK, anchor="t", line=1.04, tag="mi-la")
        text(s, x0 + 0.8, y + 0.62, w - 0.9, 0.26, b, size=7.6, color=INK2, anchor="t", line=1.02, tag="mi-lb")
    # 접속 조건
    cy = ly + 4 * lh + 0.0
    text(s, x0, cy, w, 0.26, "접속 조건", size=11.5, bold=True, tag="mi-ch"); line(s, x0, cy + 0.3, x0 + w, cy + 0.3, INK, 1.0)
    cw3 = (w - 0.2) / 3
    kpi(s, x0, cy + 0.36, cw3, 0.98, "37곳", "부지에 닿는 도로 끝", "서 9 · 동 18 · 남 7 · 북 3 [T2]", color=BLUE, big_size=17, desc_size=7.8)
    kpi(s, x0 + cw3 + 0.1, cy + 0.36, cw3, 0.98, "28m", "동측 골목의 간격", "황오동 골목이 부지에 닿는 리듬 [T2]", color=BLUE, big_size=17, desc_size=7.8)
    kpi(s, x0 + 2 * (cw3 + 0.1), cy + 0.36, cw3, 0.98, "16%", "서측 3층 이상 비율", "원화로 변은 상업 가로 [T2]", color=BLUE, big_size=17, desc_size=7.8)
    takeaway(s, LM, 7.1, CW, 0.78, "높이와 지하의 규모로는 대응하기 어려운 땅이므로, 기능과 연결, 되돌릴 수 있는 단계가 설계의 중심이 됩니다.",
             "동측은 1층 중심의 골목 조직, 서측은 상업 가로로 성격이 달라 접속 지점마다 스케일을 이어받는 방식이 필요합니다.", bar=BLUE, lead_size=10, body_size=8.8)
    notes(s, "MICRO는 대상지(S1) 단위입니다. 규제 4겹은 용도지역(V-World), 고도지구(경북고시 제2020-479호, 도심 20m·15m), 역사문화환경 보존지역·매장문화재(시굴조사 추진계획, 김권일 2026.02), 지구단위계획(고시 2026-8호)을 필지 단위로 중첩한 것이며 세계유산 완충구역·신라왕경 특별법 해당 여부는 판정 전입니다('해당 없음'으로 쓰지 않음). 고도지구·허용기준은 고시 원문 대조 전 값입니다. 동측 황오동의 1층 건물 93%·교차 31m, 서측 원화로의 3층 이상 16%는 경계 거리별 스케일 프로파일(연속수치지도 실측)이며 동측 골목 28m 간격은 부지 동쪽 가장자리 638m 구간의 걷기 가시 면적 분석입니다. 사진은 2026.09.14 현장 답사입니다(위치는 촬영 GPS로 확인).")
