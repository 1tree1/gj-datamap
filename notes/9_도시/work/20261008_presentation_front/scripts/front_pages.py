# front_pages — build_front.py 가 exec 로 불러 쓰는 본문 쪽 정의 (전역: slide, std, PAGE, 부품 함수)
# 문체: 제목·소제목 명사형 / 문장 합니다체 / 극적·구어·번역투 금지 / 수치마다 [T1~T4]
def pic_or_ph(s, path, x, y, w, h, label="", mode="cover", align=(0.5, 0.5), border=None):
    if path and have(path): return picture(s, path, x, y, w, h, mode=mode, align=align, border=border)
    rect(s, x, y, w, h, fill="#E6E8EB")
    text(s, x, y + h / 2 - 0.15, w, 0.3, "[이미지 대기] " + label, size=9, color=GRAY, align="c", anchor="m", tag="ph")


# F1 틀(1800×2400px, 중심 219,780/360,850, 1,200×1,600m)의 사진에서 정사영상 도엽 밖 무자료 띠(위 236px)를 잘라 3:4로 맞춘다.
FR_V = dict(cx=219780.0, cy=360771.25, W=1082.0, H=1442.5)       # 잘라낸 사본의 지리 범위(EPSG:5187)
def vimg(path, gray=False, contrast=1.05, brightness=1.08, ratio=0.75):
    """사진에서 단색(무자료) 가장자리 띠를 잘라 내고 3:4(가로:세로)로 중앙 맞춤한 사본을 charts/ 에 만든다."""
    if not path or not have(path): return None
    base = os.path.splitext(os.path.basename(path))[0]
    dst = CH + "\\" + base + ("_vg" if gray else "_v") + ".jpg"
    if (not have(dst)) or os.path.getmtime(dst) < os.path.getmtime(path):
        from PIL import ImageEnhance
        import numpy as np
        im = Image.open(path).convert("RGB"); a = np.asarray(im); W, H = im.size
        rs = a.reshape(H, -1).std(axis=1)
        top = 0
        while top < H - 1 and rs[top] < 1.0: top += 1
        bot = H
        while bot > top + 1 and rs[bot - 1] < 1.0: bot -= 1
        cs = a[top:bot].transpose(1, 0, 2).reshape(W, -1).std(axis=1)
        l = 0
        while l < W - 1 and cs[l] < 1.0: l += 1
        r = W
        while r > l + 1 and cs[r - 1] < 1.0: r -= 1
        h = bot - top; w = r - l
        if w / h > ratio:
            nw = int(round(h * ratio)); l += (w - nw) // 2; w = nw
        else:
            nh = int(round(w / ratio)); top += (h - nh) // 2; h = nh
        im = im.crop((l, top, l + w, top + h))
        if gray:
            im = ImageEnhance.Contrast(im.convert("L")).enhance(contrast); im = ImageEnhance.Brightness(im).enhance(brightness).convert("RGB")
        os.makedirs(CH, exist_ok=True); im.save(dst, quality=92)
    return dst

def pick(cands):
    """[(경로, 크레딧)] 중 처음으로 존재하는 것을 (경로, 크레딧)으로 돌려준다."""
    for p, c in cands:
        if p and have(p): return p, c
    return None, cands[-1][1] if cands else ""


# 소상공인365 8개 분석 구역(통신사 추정). S07: ha당 일평균 유동(2025.06~2026.06 13개월 평균), S08b: 시간대 비중(2026-06 단월)
DENSITY = [("성동시장 반경 200m", 1175), ("황리단길 반경 300m", 757), ("황오동 활성화구역", 715), ("시청 반경 500m", 596), ("구역 중심 반경 300m", 390), ("구역 경계+300m", 350), ("행복황촌 구역", 80), ("폐역 구역(고시)", 79)]
SOCIAL_ZONES = [("시청 반경 500m", 27.2, 6.1), ("행복황촌 구역", 23.1, 4.4), ("구역 경계+300m", 21.9, 4.9), ("구역 중심 반경 300m", 21.7, 4.8), ("황오동 활성화구역", 21.4, 4.9), ("성동시장 반경 200m", 21.2, 5.0), ("황리단길 반경 300m", 21.0, 5.5), ("폐역 구역(고시)", 19.4, 3.7)]


def qcrop(src, boxes, name, gap=10):
    """원문 도판에서 필요한 줄(boxes=[(l,t,r,b)])만 잘라 세로로 쌓아 charts/ 에 저장한다."""
    if not src or not have(src): return None
    dst = CH + "\\" + name + ".jpg"
    if (not have(dst)) or os.path.getmtime(dst) < os.path.getmtime(src):
        im = Image.open(src).convert("RGB")
        strips = [im.crop(b) for b in boxes]
        W = max(t.width for t in strips); H = sum(t.height for t in strips) + gap * (len(strips) - 1)
        out = Image.new("RGB", (W, H), (255, 255, 255)); y = 0
        for t in strips: out.paste(t, (0, y)); y += t.height + gap
        os.makedirs(CH, exist_ok=True); out.save(dst, quality=92)
    return dst

def credit_below(s, x, y, w, h, label, size=7, lines=1):
    """그림 아래(바깥)에 한 줄 출처. 지도 범례를 가리지 않는다. (x,y,w,h)는 그림 틀."""
    text(s, x, y + h + 0.03, w, 0.16 * lines + 0.02, label, size=size, color=GRAY, anchor="t", line=1.0, tag="credit-b")

def tag(t): return dict(text=t, size=8.5, color=GRAY)

# ═════════════════════════ 03 대상지 개요 ═════════════════════════
@slide("overview")
def _(d):
    s = std(d, "overview", "개요 : 대상지", "대상지 개요", "구 경주역 폐역 부지는 경주 원도심 중심부에 남북으로 길게 놓인 철도 용지입니다.", scale="대상지")
    ix, iy, iw = LM, 1.5, 4.3; ih = iw * 4 / 3
    img = first(MP + r"\m7_boundaries.png", vimg(first(HI + r"\ortho_2025_F1_outline.jpg", HI + r"\ortho_2025_F1.jpg")))
    pic_or_ph(s, img, ix, iy, iw, ih, "고시 구역과 본 계획 경계")
    credit_below(s, ix, iy, iw, ih, "국토지리정보원 연속수치지도 · 경주시 고시 제2026-8호 도면 [T1·T2]")
    x0 = 5.05; w = SW - RM - x0; kw = (w - 0.12) / 2
    kpi(s, x0, 1.5, kw, 1.2, "156,460㎡", "지구단위계획 고시 구역", "남북 923m · 동서 최대 273m, 축구장 약 22개 규모 [T1]")
    kpi(s, x0 + kw + 0.12, 1.5, kw, 1.2, "2021.12.28", "폐역", "영천~신경주·울산~포항 복선전철 개통으로 선로 이설 [T1]")
    kpi(s, x0, 2.8, kw, 1.2, "103년", "경주역의 운영 기간", "1918.12.28 개업, 1936.12.01 현 위치로 이전(85년) [T1]")
    kpi(s, x0 + kw + 0.12, 2.8, kw, 1.2, "93%", "시굴조사 대상", "유존지역 145,879㎡(고시 구역 대비), 발굴 유예 조건은 2m 미만 성토 [T2]")
    rows = [("위치", "경북 경주시 성동동 일원. 황오동과 성동시장 사이의 원도심 중심부 [T1]"),
            ("소유", "철도 용지 148,770㎡ — 국가철도공단 69,790㎡ · 한국철도공사 78,864㎡ · 기재부 116㎡ [T1]"),
            ("구 역사", "건물 면적 1,404㎡, 2층. 코레일 철도기념물(2013)이며 등록문화유산은 아닙니다 [T1·T2]"),
            ("규제", "자연녹지 77.5% · 고도 20m 지구 87.5%(분석 범위 기준) · 고시 결정도에 주거용지 없음 [T1]"),
            ("추진", "2025.12 도시재생 국가시범지구 후보 선정 · 2026.01 지구단위계획 결정 고시 [T1·T2]")]
    y = 4.18
    for k, v in rows:
        text(s, x0, y, 0.75, 0.4, k, size=10, bold=True, color=BLUE, anchor="m", tag="ov-k")
        text(s, x0 + 0.8, y, w - 0.8, 0.4, v, size=9.5, color=INK, anchor="m", tag="ov-v")
        line(s, x0, y + 0.42, x0 + w, y + 0.42, LINE, 0.5); y += 0.44
    # 면적 기준 4가지
    y0 = 6.5
    text(s, x0, y0 - 0.02, w, 0.25, "면적 기준 — 대지분석은 고시 구역과 분석 범위, 계획 수치는 마스터플랜의 계획 경계를 따릅니다", size=9.3, bold=True, tag="ov-h")
    rows = [("시 구상 면적", 79438, "#C7CDD4", "경주시 보도자료, 범위 미정의 [T2]"), ("고시 구역", 156460, "#8FA9CF", "지구단위계획 고시 2026-8호 [T1]"),
            ("분석 범위", 218478, BLUE, "고시 구역 밖 60,498㎡ 포함, 지도의 붉은 선"), ("계획 경계", 120547, "#E58B8B", "마스터플랜 도면 기준 [본 계획]")]
    for i, (lab, v, col, note) in enumerate(rows):
        yy = y0 + 0.27 + i * 0.26
        text(s, x0, yy, 1.0, 0.22, lab, size=9, anchor="m", tag="ov-bl")
        rect(s, x0 + 1.0, yy + 0.02, 2.2 * v / 218478, 0.17, fill=col)
        text(s, x0 + 1.0 + 2.2 * v / 218478 + 0.05, yy, 0.85, 0.22, format(v, ",") + "㎡", size=9, bold=True, anchor="m", tag="ov-bv")
        text(s, x0 + 4.2, yy, w - 4.2, 0.22, note, size=7.8, color=GRAY, anchor="m", tag="ov-bn")
    notes(s, "대상지의 기본 사실만 제시하는 도입 쪽입니다. 면적은 세 가지 기준이 있으며(시 구상 79,438㎡ — 경주시 보도자료 2025-12-18·2026-01-02 [T2], 범위 미정의 / 고시 구역 156,460㎡ [T1] / 분석 범위 218,478㎡(이전 작업 경계, 지도의 붉은 선) / 마스터플랜의 계획 경계 120,547㎡(수정안, 1:1 좌표, 지오레퍼런싱 전)) 서로 섞어 쓰지 않습니다. 철도 용지 148,770㎡는 도시재생 전략계획(2022)의 폐철도 활용 추진사업 표(소유 구분 포함)입니다. 구 역사는 등록문화유산이 아니며 코레일이 2013년 철도기념물로 지정했습니다(지정일은 위키 [T4]에만 있음).")

# ═════════════════════════ 13 목표설정 ═════════════════════════
@slide("goal")
def _(d):
    s = std(d, "goal", "설계방향 : 목표설정", "목표설정", "방문·근로·정주 인구가 함께 이용하는 복합 거점을 목표로 하고, 목표마다 현황 기준값과 확인 지표를 둡니다.")
    # 상단 배너
    rect(s, LM, 1.5, CW, 0.95, fill=DARK, radius=0.06)
    text(s, LM + 0.3, 1.55, 4.6, 0.55, "원도심 복합 생활거점", size=22, bold=True, color="#FFFFFF", anchor="m", tag="goal-t")
    text(s, LM + 0.3, 2.07, 4.9, 0.36, "폐역 부지를 방문·근로·정주 인구가 함께 이용하는 복합 거점으로 조성합니다.", size=9.5, color=FG2, anchor="m", tag="goal-s")
    flow = [("남측", "방문 관문", ZS, INK), ("중앙", "교류·창작", ZC, "#FFFFFF"), ("북측", "근로·정주", ZN, "#FFFFFF"), ("확산", "성동시장·황오동", "#6D6E71", "#FFFFFF")]
    fx = LM + 5.45; fw = 1.18
    for i, (a, b, col, tc) in enumerate(flow):
        box_text(s, fx + i * (fw + 0.2), 1.68, fw, 0.6, [dict(text=a, size=10, bold=True, color=tc, align="c"), dict(text=b, size=8.5, color=tc, align="c")], fill=col, radius=0.08, anchor="m", margin=(0.03, 0.02, 0.03, 0.02), tag="goal-f")
        if i < 3: text(s, fx + i * (fw + 0.2) + fw, 1.7, 0.2, 0.55, "›", size=14, bold=True, color=FG3, align="c", anchor="m")
    # 목표 표
    cols = [("원칙", 0.78), ("목표", 1.75), ("현황 기준값", 3.05), ("확인 지표", 1.95), ("본 계획 반영", 3.163)]
    x = LM; y = 2.62
    for name, w in cols:
        rect(s, x, y, w, 0.27, fill=INK); text(s, x + 0.08, y, w - 0.1, 0.27, name, size=9.5, bold=True, color="#FFFFFF", anchor="m", tag="goal-h"); x += w
    rows = [("연결", "동서 보행 흐름의 연속성 확보", "도로 횡단 부재 985m · 보행 육교 1개(폭 3.2m) · 우회율 3.5 [T2]", "횡단 가로 수 · 최대 횡단 간격 · 가장 좁은 통과 폭", "기존 가로 끝 37곳에 접속하는 동서 연결 가로, 기존 가로 틀(약 147.5m)에 맞춘 횡단 간격 [본 계획]"),
            ("관문", "방문 인구의 도착과 보행 전환", "자가용 76.9% · 체류 3시간 미만 79% · 주차시설 확충 요구 38.8% [T1·T2]", "체류 시간 · 소비 금액 · 차량 방문 분담", "남측 — 구 역사 이전·근대역사관, 관광지원시설, 주차전용건축물, 관광 상가"),
            ("근로", "주간 근로 인구의 확보", "종사자 −23.1%(2018→2023, 격자 32셀) · 시청 반경 500m만 주거·직장 균형 [T2]", "종사자 수 · 주거 대비 직장 인구", "북측 시청·의회 캠퍼스, 청년창업·기업지원"),
            ("정주", "야간 정주 인구의 확보", "결정도 주거용지 0 · 야간(23~05시) 유동 3.7~5.5% · 1~2인 가구 73.8% [T1·T2]", "거주 세대 · 야간 활동 비율", "북측 청년주거와 1층 생활 상가 (세대 규모는 가정이며 마스터플랜 면적표에서 제시)"),
            ("확산", "주변 지역으로의 활력 파급과 생활 기반 유지", "성동시장 200m 1,175명/ha(폐역 구역 79) · 생활 업종 87.8% · 업종 순증 숙박 +5, 생활소매·식품 −9 [T2]", "생활 업종 비율 · 인접 건물 주 출입구 방향", "성동시장 클러스터, 동서 보행축과 녹지"),
            ("조건", "유산·규제 안에서 되돌릴 수 있는 순서로 추진", "시굴 대상 93%(고시 구역 대비) · 고도 20m 지구 87.5% · 자연녹지 77.5% [T1·T2]", "단계별 가역·비가역 투자의 구분", "1단계 가로·광장·임시 평면주차 → 시굴 후 핵심 시설")]
    rh = 0.665; y += 0.27
    keys = ["연결", "관문", "근로", "정주", "확산", "조건"]
    for i, r in enumerate(rows):
        yy = y + i * rh
        rect(s, LM, yy, CW, rh - 0.04, fill=(TINT if i % 2 == 0 else "#FFFFFF"))
        col = PC.get(r[0], "#8F8F8F"); tc = PCT.get(r[0], "#FFFFFF")
        box_text(s, LM + 0.1, yy + (rh - 0.04) / 2 - 0.14, 0.58, 0.28, r[0], fill=col, radius=0.1, size=9.5, bold=True, color=tc, align="c", anchor="m", margin=(0.02, 0, 0.02, 0), tag="goal-chip")
        x = LM + cols[0][1]
        for j in range(1, 5):
            w = cols[j][1]
            text(s, x + 0.08, yy + 0.02, w - 0.14, rh - 0.08, r[j], size=(9.8 if j == 1 else 9), bold=(j == 1), color=(INK if j in (1, 4) else INK2), anchor="m", line=1.08, tag="goal-c%d" % j)
            x += w
    # 이중 지표
    yb = y + 6 * rh + 0.08
    bw = (CW - 0.15) / 2
    box_text(s, LM, yb, bw, 0.78, [dict(text="방문 지표", size=10.5, bold=True, space_after=2), dict(text="방문객 수 · 체류 시간 · 소비 금액", size=9.5, color=INK)], fill="#FBE3EE", radius=0.06, anchor="m", margin=(0.18, 0.05, 0.1, 0.05), tag="goal-v")
    box_text(s, LM + bw + 0.15, yb, bw, 0.78, [dict(text="정주 지표", size=10.5, bold=True, space_after=2), dict(text="거주 인구 · 생활 업종 비율 · 야간(18시 이후) 활동", size=9.5, color=INK)], fill="#FBF3CC", radius=0.06, anchor="m", margin=(0.18, 0.05, 0.1, 0.05), tag="goal-j")
    notes(s, "목표는 현황 쪽에서 확인한 문제 ①~⑥에 하나씩 대응합니다. 기준값은 06~07쪽의 수치이고, 계획 반영은 본 계획 도면에서 산출한 값입니다. 동서 연결 가로의 횡단 간격은 원도심 동서 가로 틀(약 147.5m)의 틀선에 맞춥니다(이전 개념안의 5개 가로는 간격 137~157m). 청년주거 세대 규모는 면적 배분의 결과이므로 가정으로 표시합니다. 방문 지표와 정주 지표는 항상 함께 보고합니다(관광 업종 증가·생활 업종 감소는 회복이 아니라 치환으로 판단).")
