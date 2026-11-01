# -*- coding: utf-8 -*-
"""05·06장 2차 수정 — 그림 제작 C: 차트·도식
05: 축 근거(유동 밀도 · 끝점 거리) · 가로 단면 구성 · 가구 면적 구성 · 토지이용 구성
06: 앵커 재편 · 후보 7개 평가 · 이전안→수요 기반안 변화 · 권역 규모 · 세 존 조감 · 용도·획지별 연면적
수치는 05·06장 본문 표의 값(최종 모델 2026-10-12, 2파트 프로그램 산정)만 쓴다."""
from figkit_46 import *

GREEN = "#9CCF78"; BEIGE = "#EEE3CC"
LOTC = {"공공업무": "#6E8FC9", "업무·창업": "#EE8A62", "문화·집회": "#7FC0D6", "창작·공방": "#AE93D6", "근린생활": "#F09AB0",
        "체육·복지": "#6FC6AA", "주거": "#F1CF7E", "역사유산": "#B97A4E", "관광·방문": "#B9C3CD", "주차·교통": "#A3A8AE"}


def sub(fig, W, H, x, y, w, h):
    a = fig.add_axes([x / W, 1 - (y + h) / H, w / W, h / H]); return a


def clean(a, left=False):
    for s in ("top", "right", "bottom") + (() if left else ("left",)): a.spines[s].set_visible(False)
    a.set_facecolor("none"); a.tick_params(length=0)


# ───────── 05 · 축 근거 ─────────
def axes_evidence():
    W, H = WIDE, 92
    fig, ax = new(W, H)
    T(ax, 4, 6, "동서 방향 일평균 유동 밀도(명/ha)", 12, INK, w="bold"); T(ax, 204, 6, "대지 축 끝점까지의 거리(m)", 12, INK, w="bold")
    line(ax, [4, 184], [11, 11], G4, 0.8); line(ax, [204, 376], [11, 11], G4, 0.8)
    # 좌: 유동 밀도
    names = ["성동시장 반경 200 m", "폐역 구역", "행복황촌"]; v = [1174.6, 79.3, 80.3]; cols = [RED, G3, G3]
    x0 = 46; sc = 100.0 / 1174.6
    for i, (n, vv, c) in enumerate(zip(names, v, cols)):
        y = 20 + i * 17
        T(ax, x0 - 3, y + 6, n, 11.5, INK, "right", w="medium")
        rect(ax, x0, y, vv * sc, 12, fc=c); T(ax, x0 + vv * sc + 2.5, y + 6, "{:,.1f}".format(vv), 12, INK, w="bold")
    T(ax, x0, 74, "폐역 구역의 약 14.8배 · 행복황촌의 약 14.6배", 11, RED, w="semibold")
    T(ax, 4, 86, "통신 추정, 구역 일부 중첩 · 2025.06~2026.06", 10, G2)
    # 우: 끝점 거리
    lab = ["② 동서축 서측 끝 → 성동시장", "② 동서축 동측 끝 → 전랑지(사적 88호)", "④ 조망로 서측 끝 → 경주읍성 향일문", "③ 사선축 연장선 → 미추왕릉", "① 남북축 북측 끝 → 황성공원"]
    d = [210, 320, 310, 680, 1000]; cc = [RED, RED, G2, G1, INK]
    sc2 = 130.0 / 1000
    for i, (ll, dd, c) in enumerate(zip(lab, d, cc)):
        y = 15 + i * 13.5
        T(ax, 204, y + 2.6, ll, 10.5, G1, w="medium")
        rect(ax, 204, y + 5.2, dd * sc2, 5.2, fc=c); T(ax, 204 + dd * sc2 + 2.5, y + 7.8, "약 {:,}".format(dd), 11.5, INK, w="bold")
    T(ax, 204, 86, "설계팀 도면 측정, 황성공원은 북천을 지나 약 1 km", 10, G2)
    return save(fig, "05_axes_evidence.png")


# ───────── 05 · 가로 단면 구성 ─────────
def street_sections():
    W, H = WIDE, 116
    fig, ax = new(W, H)
    T(ax, 4, 6, "도로 · 보행 가로 단면 구성(폭 m, 동일 축척)", 12, INK, w="bold")
    line(ax, [4, W - 4], [11, 11], G4, 0.8)
    C = {"보도": G4, "차도": "#3a3a3a", "식재": GREEN, "광장": BEIGE, "보행": BEIGE}
    rows = [("북측 차도", "차도 13 m", [("보도", 5), ("차도", 13), ("보도", 5)]),
            ("동서 도로", "차도 20 m", [("보도", 5), ("차도", 20), ("보도", 5)]),
            ("동·남측 외곽도로", "차도 10~12 m", [("보도", 8), ("차도", 10)]),
            ("동서 선형공원", "40 m", [("식재", 12), ("광장", 16), ("식재", 12)]),
            ("남북 중앙 보행축", "30 m", [("식재", 7), ("보행", 16), ("식재", 7)]),
            ("관문광장 · 사선 보행축", "20 m", [("식재", 6), ("보행", 8), ("식재", 6)]),
            ("향일문 조망로", "8 m", [("보행", 8)]),
            ("외곽 보도", "5 m", [("보도", 5)])]
    s = 5.8; xc = 252.0; y0 = 15; rh = 10.4
    for i, (nm, w, segs) in enumerate(rows):
        y = y0 + i * rh
        T(ax, 5, y + 3.0, nm, 11.5, INK, w="semibold"); T(ax, 5, y + 7.6, w, 10, G2)
        tot = sum(v for _, v in segs); x = xc - tot * s / 2
        for t, v in segs:
            rect(ax, x, y, v * s, 8.6, fc=C[t], ec="white", lw=0.6)
            T(ax, x + v * s / 2, y + 4.4, "%s %d" % (t, v), 10.5, "white" if t == "차도" else INK, "center", w="medium")
            x += v * s
    # 축척 · 범례
    yb = y0 + 8 * rh + 3
    line(ax, [xc - 5 * s, xc + 5 * s], [yb + 2, yb + 2], INK, 1.2); T(ax, xc, yb + 7.2, "10 m", 10.5, INK, "center")
    xl = 5
    for t, c in (("보도", G4), ("차도", "#3a3a3a"), ("식재", GREEN), ("광장 · 보행", BEIGE)):
        rect(ax, xl, yb + 0.5, 7, 4.6, fc=c, ec=G3, lw=0.3); T(ax, xl + 9, yb + 3, t, 10.5, INK); xl += 34
    return save(fig, "05_street_sections.png")


# ───────── 05 · 가구 9개 면적 구성 ─────────
def block_areas():
    W, H = COL, 92
    fig, ax = new(W, H)
    T(ax, 4, 6, "가구별 면적 구성(㎡)", 12, INK, w="bold"); line(ax, [4, W - 4], [11, 11], G4, 0.8)
    plots = [5571, 18157, 18123, 12662, 7938, 11998, 16781, 20419, 26440]; parks = [12191, 3865, 0, 0, 9201, 0, 0, 0, 0]
    tot = [17762, 22022, 18123, 12662, 17139, 11998, 16781, 20420, 26442]
    a = sub(fig, W, H, 24, 14, 150, 64); clean(a)
    y = np.arange(9)[::-1]
    a.barh(y, plots, color=G1, height=0.62); a.barh(y, parks, left=plots, color=GREEN, height=0.62)
    a.set_xlim(0, 33000); a.set_ylim(-0.6, 8.6); a.set_yticks(y); a.set_yticklabels(["가구 %d" % k for k in range(1, 10)], fontsize=11); a.set_xticks([])
    for yy, p, q, t in zip(y, plots, parks, tot): a.text(p + q + 400, yy, "{:,}".format(t), fontsize=11, va="center", fontweight=700, color=INK)
    rect(ax, 24, 83, 7, 4.6, fc=G1); T(ax, 33, 85.3, "건축 획지", 10.5, INK); rect(ax, 66, 83, 7, 4.6, fc=GREEN); T(ax, 75, 85.3, "공원", 10.5, INK)
    T(ax, 100, 85.3, "합계 163,348 (획지 138,089 + 공원 25,257)", 10, G2)
    return save(fig, "05_block_areas.png")


# ───────── 05 · 토지이용 면적 구성 ─────────
def landuse_share():
    W, H = COL, 84
    fig, ax = new(W, H)
    T(ax, 4, 6, "계획 경계 228,022㎡의 토지이용 구성", 12, INK, w="bold"); line(ax, [4, W - 4], [11, 11], G4, 0.8)
    x0, L = 4, W - 8
    segs = [("건축 획지(13개)", 138089, 60.6, G1, "white"), ("공원 · 녹지", 25257, 11.1, GREEN, INK), ("도로 · 보행", 64677, 28.4, RED, "white")]
    x = x0; pos = []
    for n, v, p, c, tc in segs:
        w = L * p / 100.0; rect(ax, x, 26, w, 12, fc=c, ec="white", lw=0.8); pos.append((x, w))
        T(ax, x + w / 2, 32, "%.1f%%" % p, 11.5, tc, "center", w="bold"); x += w
    for (xx, w), (n, v, p, c, tc) in zip(pos, segs):
        T(ax, xx + w / 2, 16.5, n, 10.5, INK, "center", w="medium"); T(ax, xx + w / 2, 21.6, "{:,}㎡".format(v), 10, G2, "center")
    xr, wr = pos[2]
    sub_ = [("차량 도로", 19258, 8.4, "#3a3a3a", "white"), ("보행자전용도로 · 광장", 31778, 13.9, BEIGE, INK), ("외곽 보도", 13640, 6.0, G4, INK)]
    line(ax, [xr, x0], [38, 50], G3, 0.7); line(ax, [xr + wr, x0 + L], [38, 50], G3, 0.7)
    x = x0; tot = 64677.0
    for n, v, p, c, tc in sub_:
        w = L * v / tot; rect(ax, x, 50, w, 12, fc=c, ec="white", lw=0.8)
        T(ax, x + w / 2, 56, "{:,}".format(v), 10.5, tc, "center", w="bold")
        T(ax, x + w / 2, 66, n, 10, INK, "center", w="medium"); T(ax, x + w / 2, 71.2, "구역의 %.1f%%" % p, 10, G2, "center"); x += w
    return save(fig, "05_landuse_share.png")


# ───────── 06 · 앵커 재편 ─────────
def anchor_remap():
    W, H = WIDE, 94
    fig, ax = new(W, H)
    T(ax, 4, 6, "이전 단계(앵커 3 + 보조 1, 후보 평가)", 11.5, G2, w="semibold"); T(ax, 262, 6, "본 계획(네 앵커)", 11.5, RED, w="semibold")
    line(ax, [4, W - 4], [11, 11], G4, 0.8)
    L = [("공공청사 · 의회", "후보 평가에서 확산 거점", 0), ("청년 일자리", "앵커", 1), ("청년주거", "앵커", 2), ("K-헤리티지", "앵커", 3), ("창작 스튜디오", "보조 앵커", 4)]
    Rr = [("Civic", "통합 시청 · 공공기관 · 공공업무 · 청년창업지원", 14, 27), ("Residential", "일반 공동주택 · 생활시설", 44, 13), ("Cultural", "역사 · 전시 · 관광지원", 60, 13), ("Creative", "레지던시 · 공방 · 마켓", 76, 13)]
    ly = [14, 27, 44, 60, 76]
    for (n, s, k), y in zip(L, ly):
        box(ax, 4, y, 108, 13, fc=G6, ec=G4, r=1.5); T(ax, 9, y + 6.5, n, 12.5, INK, w="semibold"); T(ax, 108, y + 6.8, s, 10.5, G2, "right")
    cols = [RED, INK, G1, G2]
    for (n, d, y, h), c in zip(Rr, cols):
        box(ax, 214, y, 162, h, fc="white", ec=c, lw=1.8, r=1.8); T(ax, 220, y + (6.5 if h < 20 else 8), n, 14, c, w="bold"); T(ax, 252, y + (6.7 if h < 20 else 8.2), d, 11, INK)
    # 화살표(좌 → 우)
    ys_r = {0: 20.5, 1: 31.5, 2: 50.5, 3: 66.5, 4: 82.5}
    ty = {0: 20, 1: 33, 2: 50.5, 3: 66.5, 4: 82.5}
    for (n, s, k), y in zip(L, ly):
        arrow(ax, 113, y + 6.5, 213, ty[k], RED if k < 2 else G1, 1.3, 11)
    T(ax, 163, 17.2, "Civic의 중심", 10.5, RED, "center", w="medium", bbox=dict(fc="white", ec="none", pad=1)); T(ax, 163, 33.0, "업무 · 창업", 10.5, RED, "center", w="medium", bbox=dict(fc="white", ec="none", pad=1))
    T(ax, 163, 47.2, "정주", 10.5, G1, "center", w="medium", bbox=dict(fc="white", ec="none", pad=1)); T(ax, 163, 63.2, "역사 · 관광", 10.5, G1, "center", w="medium", bbox=dict(fc="white", ec="none", pad=1))
    T(ax, 163, 79.2, "창작 · 공방", 10.5, G1, "center", w="medium", bbox=dict(fc="white", ec="none", pad=1))
    return save(fig, "06_anchor_remap.png")


# ───────── 06 · 후보 7개 평가 ─────────
def candidate_heatmap():
    W, H = WIDE, 108
    fig, ax = new(W, H)
    crit = ["문제 대응", "시 구상 정합", "혁신지구 요건", "규제 적합", "운영 · 수요 근거"]
    T(ax, 4, 8, "후보", 11.5, G2, w="semibold")
    cx0, cw = 104, 30
    for j, c in enumerate(crit): T(ax, cx0 + j * cw + cw / 2, 8, c, 10.5, G2, "center", w="semibold")
    T(ax, 262, 8, "판정", 11.5, G2, w="semibold"); T(ax, 312, 8, "최종 모델 반영", 11.5, G2, w="semibold")
    line(ax, [4, W - 4], [13, 13], G4, 0.8)
    data = [("청년창업 · 기업지원", "●●●●◐", "앵커", "획지 5"), ("청년 · 신혼 주거", "●●●◐○", "앵커(정주)", "획지 4"), ("K-헤리티지 · 역사문화예술", "●●◐●◐", "앵커", "획지 9 · 12"),
            ("창작 스튜디오 · 공방", "◐○◐●○", "보조 앵커", "획지 7 · 8"), ("공공청사 · 의회", "●◐○◐◐", "확산 거점", "획지 1 · 2 (Civic 격상)"), ("모빌리티 허브", "◐●◐●○", "기타(필수)", "획지 13"),
            ("성동시장 연계 상업 · 소규모 숙박", "◐●○●○", "선택 제안", "획지 11, 숙박 없음")]
    rh = 11.2
    for i, (nm, sc, jd, rf) in enumerate(data):
        y = 16 + i * rh
        if i % 2 == 0: rect(ax, 4, y - 0.4, W - 8, rh, fc=G6)
        T(ax, 6, y + rh / 2 - 0.4, nm, 11.5, INK, w="medium")
        for j, ch in enumerate(sc):
            cx = cx0 + j * cw + cw / 2; cy = y + rh / 2 - 0.4
            if ch == "●": ax.add_patch(Circle((cx, cy), 3.2, fc=RED, ec=RED, lw=1.0, zorder=5))
            elif ch == "○": ax.add_patch(Circle((cx, cy), 3.2, fc="white", ec=RED, lw=1.0, zorder=5))
            else:
                ax.add_patch(Circle((cx, cy), 3.2, fc="white", ec=RED, lw=1.0, zorder=5)); ax.add_patch(Wedge((cx, cy), 3.2, 90, 270, fc=RED, ec=RED, lw=1.0, zorder=6))
        T(ax, 262, y + rh / 2 - 0.4, jd, 11, INK, w="semibold"); T(ax, 312, y + rh / 2 - 0.4, rf, 11, G1)
    yl = 16 + 7 * rh + 4
    for k, (ch, t) in enumerate((("●", "강함"), ("◐", "중간"), ("○", "약함"))):
        cx = 8 + k * 30; cy = yl + 2.5
        ax.add_patch(Circle((cx, cy), 2.6, fc=RED if ch == "●" else "white", ec=RED, lw=0.9, zorder=5))
        if ch == "◐": ax.add_patch(Wedge((cx, cy), 2.6, 90, 270, fc=RED, ec=RED, lw=0.9, zorder=6))
        T(ax, cx + 5, cy, t, 10.5, INK)
    T(ax, 104, cy, "기준 5개는 가중치 없이 정성 판정(설계팀)", 10.5, G2)
    return save(fig, "06_candidate_heatmap.png")


# ───────── 06 · 이전 단계안 → 수요 기반안 ─────────
def v1_v2_change():
    W, H = COL, 84
    fig, ax = new(W, H)
    T(ax, 4, 6, "이전 단계안 → 수요 기반 산정안(v1)", 12, INK, w="bold"); line(ax, [4, W - 4], [11, 11], G4, 0.8)
    pan = [("판매 · 음식 비중(%)", [23.7, 9.8], 30, ["23.7", "9.8"]), ("창조산업 비중(%)", [9.4, 5.0], 12, ["9.4", "5.0"]), ("청년주거(세대)", [816, 600], 1000, ["714~816", "600"])]
    for i, (t, v, ymax, lb) in enumerate(pan):
        x = 4 + i * 59.5
        T(ax, x + 27, 16.5, t, 10.5, INK, "center", w="semibold")
        a = sub(fig, W, H, x, 20, 54, 48); clean(a)
        a.bar([0, 1], v, color=[G3, RED], width=0.62); a.set_ylim(0, ymax * 1.12); a.set_xlim(-0.55, 1.55); a.set_yticks([]); a.set_xticks([0, 1]); a.set_xticklabels(["이전 단계", "수요 기반"], fontsize=10.5)
        if i == 2: a.bar([0], [714], color="#7d7d7d", width=0.62)
        for k, (vv, l) in enumerate(zip(v, lb)): a.text(k, vv + ymax * 0.03, l, ha="center", va="bottom", fontsize=11.5, fontweight=700, color=INK)
    T(ax, 4, 78, "청년주거 막대의 진한 부분은 714세대, 연한 부분은 816세대까지의 범위", 10, G2)
    return save(fig, "06_v1_v2_change.png")


# ───────── 06 · 권역별 규모 ─────────
def zone_chart():
    W, H = COL, 74
    fig, ax = new(W, H)
    T(ax, 4, 6, "존별 획지 면적과 연면적(㎡)", 12, INK, w="bold"); line(ax, [4, W - 4], [11, 11], G4, 0.8)
    a = sub(fig, W, H, 26, 14, 150, 50); clean(a)
    zs = ["북측 존", "중앙 존", "남측 존"]; land = [41851, 49379, 46859]; gfa = [76031, 63289, 53126]; sh = ["39.5%", "32.9%", "27.6%"]
    y = np.arange(3)[::-1]
    a.barh(y + 0.19, land, height=0.34, color=G3); a.barh(y - 0.19, gfa, height=0.34, color=RED)
    a.set_xlim(0, 100000); a.set_ylim(-0.6, 2.6); a.set_yticks(y); a.set_yticklabels(zs, fontsize=11.5, fontweight=600); a.set_xticks([])
    for yy, l, g, s in zip(y, land, gfa, sh):
        a.text(l + 1200, yy + 0.19, "{:,}".format(l), fontsize=10.5, va="center", color=G1); a.text(g + 1200, yy - 0.19, "{:,} · {}".format(g, s), fontsize=10.5, va="center", fontweight=700, color=INK)
    rect(ax, 26, 67, 7, 4.2, fc=G3); T(ax, 35, 69.2, "획지 면적", 10.5, INK); rect(ax, 70, 67, 7, 4.2, fc=RED); T(ax, 79, 69.2, "연면적 · 구성비", 10.5, INK)
    return save(fig, "06_zone_chart.png")


# ───────── 06 · 세 존 조감 ─────────
def zone_renders():
    W, H = WIDE, 108
    fig, ax = new(W, H)
    P = [("north", "북측 존 · 공공 · 정주 거점", "획지 41,851㎡ · 연면적 76,031㎡"), ("center", "중앙 존 · 생활문화 · 창작", "획지 49,379㎡ · 연면적 63,289㎡"), ("south", "남측 존 · 역사 · 관광 관문", "획지 46,859㎡ · 연면적 53,126㎡")]
    pw = 122.0; ph = pw * 330 / 500.0
    for i, (k, t, s) in enumerate(P):
        x = 4 + i * (pw + 3)
        T(ax, x, 6, t, 12.5, INK, w="bold"); T(ax, x, 12.6, s, 10.5, G2)
        im = Image.open("%s/_cache/zone_%s.png" % (REP + "/build", k)).convert("RGB")
        ax.imshow(np.asarray(im), extent=(x, x + pw, 17 + ph, 17), aspect="auto", zorder=1)
        rect(ax, x, 17, pw, ph, fc="none", ec=G4, lw=0.6, z=3)
    ax.set_xlim(0, W); ax.set_ylim(H, 0)
    T(ax, 4, 17 + ph + 5.5, "최종 모델 프로그램 구성 조감(북측 존 · 중앙 존 · 남측 존을 같은 축척으로 확대, 건물 색은 용도)", 10.5, G2)
    return save(fig, "06_zone_renders.png")


# ───────── 06 · 용도별 · 획지별 연면적 ─────────
def use_share():
    W, H = WIDE, 100
    fig, ax = new(W, H)
    T(ax, 4, 6, "용도별 지상 연면적 비율(%)", 12, INK, w="bold"); T(ax, 204, 6, "획지별 연면적(㎡)", 12, INK, w="bold")
    line(ax, [4, 184], [11, 11], G4, 0.8); line(ax, [204, 376], [11, 11], G4, 0.8)
    uses = [("주차 · 교통", 22.9), ("문화 · 집회", 19.6), ("공공청사 · 공공업무", 18.4), ("판매 · 근린생활", 12.3), ("주거", 11.4), ("업무 · 청년창업", 4.6), ("창작 · 공방", 4.5), ("생활체육 · 복지", 4.2), ("역사유산(구 경주역사)", 1.5), ("관광 · 방문자", 0.7)]
    uc = ["주차·교통", "문화·집회", "공공업무", "근린생활", "주거", "업무·창업", "창작·공방", "체육·복지", "역사유산", "관광·방문"]
    a = sub(fig, W, H, 44, 14, 140, 74); clean(a)
    y = np.arange(10)[::-1]
    a.barh(y, [v for _, v in uses], color=[LOTC[k] for k in uc], height=0.66); a.set_xlim(0, 28); a.set_ylim(-0.6, 9.6)
    a.set_yticks(y); a.set_yticklabels([n for n, _ in uses], fontsize=10.5); a.set_xticks([])
    for yy, (_, v) in zip(y, uses): a.text(v + 0.35, yy, "%.1f" % v, fontsize=11, va="center", fontweight=700, color=INK)
    T(ax, 100, 93, "합계 192,447㎡ · 건물 41동", 10.5, G2)
    plots = [("1 공공청사", 29550, "g1"), ("2 청사 부설주차장", 19521, "g1"), ("3 생활체육시설", 6000, "g2"), ("4 청년·신혼 공공임대", 20960, "g2"), ("5 공공업무·청년창업", 16402, "g1"), ("6 생활문화·돌봄", 13194, "g2"),
             ("7 전통공예", 11501, "g3"), ("8 창작·체험", 22192, "g3"), ("9 구 경주역 리유즈", 12973, "g4"), ("10 관광안내", 1262, "g4"), ("11 관문 가로상가", 2403, "g4"), ("12 근대역사관", 11973, "g4"), ("13 공유주차장·허브", 24515, "g5")]
    gc = {"g1": "#6E8FC9", "g2": "#F1CF7E", "g3": "#AE93D6", "g4": "#B97A4E", "g5": "#A3A8AE"}
    a2 = sub(fig, W, H, 204, 14, 172, 70); clean(a2)
    y = np.arange(13)[::-1]
    a2.barh(y, [v for _, v, _ in plots], color=[gc[g] for _, _, g in plots], height=0.68); a2.set_xlim(0, 38000); a2.set_ylim(-0.6, 12.6)
    a2.set_yticks(y); a2.set_yticklabels([n for n, _, _ in plots], fontsize=10); a2.set_xticks([])
    for yy, (_, v, _) in zip(y, plots): a2.text(v + 500, yy, "{:,}".format(v), fontsize=10, va="center", fontweight=700, color=INK)
    xl = 204
    for g, t in (("g1", "공공행정·업무"), ("g2", "정주·생활 SOC"), ("g3", "창작·체험"), ("g4", "역사·문화·관광"), ("g5", "교통·모빌리티")):
        rect(ax, xl, 90, 5, 4, fc=gc[g]); T(ax, xl + 6.5, 92, t, 10, INK); xl += 35
    return save(fig, "06_use_share.png")


if __name__ == "__main__":
    axes_evidence(); street_sections(); block_areas(); landuse_share()
    anchor_remap(); candidate_heatmap(); v1_v2_change(); zone_chart(); zone_renders(); use_share()
