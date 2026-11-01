# -*- coding: utf-8 -*-
"""앞부분(현황·문제) 차트 — 적색+흑백. 수치는 20261011_visual_front/build/build_visual_deck.mjs 와 evidence.json 에서 옮겼다(출처는 각 슬라이드 캡션).
출력: assets/charts/*.png (투명 배경 없음, 흰 배경)"""
import os, sys, json
import numpy as np
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from deck_style import *

ROOT = r"C:\Users\OFFICE\Desktop\9_도시\work"
OUT = ROOT + r"\20261011_final_deck\assets\charts"; os.makedirs(OUT, exist_ok=True)
E = json.load(open(ROOT + r"\20261011_visual_front\build\evidence.json", encoding="utf-8"))

def ax_clean(ax, left=True):
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    ax.spines["left"].set_visible(left); ax.spines["bottom"].set_color(G4); ax.spines["left"].set_color(G4)
    ax.tick_params(length=0, labelsize=8.5, colors=G1)

def hbar(name, cats, vals, fmt="{:,.0f}", unit="", hl=None, w=4.2, h=2.6, color=G2, title=None, vmax=None):
    """가로 막대: hl=강조 인덱스(적색)"""
    fig, ax = plt.subplots(figsize=(w, h)); n = len(cats); y = np.arange(n)[::-1]
    cols = [RED if (hl is not None and i in (hl if isinstance(hl, (list, tuple)) else [hl])) else color for i in range(n)]
    ax.barh(y, vals, color=cols, height=0.62)
    ax.set_yticks(y); ax.set_yticklabels(cats); ax.set_xticks([]); ax_clean(ax, left=False); ax.spines["bottom"].set_visible(False)
    lo = min(0, min(vals)); vm = vmax or max(vals) * 1.22
    ax.set_xlim(lo * 1.35 if lo < 0 else 0, vm if max(vals) > 0 else abs(lo) * 0.1)
    if lo < 0: ax.axvline(0, color=G3, lw=0.6)
    span = (vm - lo * 1.35) if lo < 0 else vm
    for yi, v in zip(y, vals):
        if v >= 0: ax.text(v + span * 0.015, yi, fmt.format(v) + unit, va="center", ha="left", fontsize=8.5, color=INK, family=FONT_NUM, fontweight="bold")
        else: ax.text(v - span * 0.015, yi, fmt.format(v) + unit, va="center", ha="right", fontsize=8.5, color=INK, family=FONT_NUM, fontweight="bold")
    if title: ax.set_title(title, loc="left", fontsize=9, color=G1, pad=6)
    fig.tight_layout(pad=0.4); fig.savefig(OUT + "\\" + name + ".png"); plt.close(fig)

def vbar(name, cats, vals, fmt="{:,.0f}", unit="", hl=None, w=4.2, h=2.8, color=G2, title=None, ymin=None, ymax=None, zero=False):
    fig, ax = plt.subplots(figsize=(w, h)); n = len(cats); x = np.arange(n)
    cols = [RED if (hl is not None and i in (hl if isinstance(hl, (list, tuple)) else [hl])) else color for i in range(n)]
    ax.bar(x, vals, color=cols, width=0.62)
    ax.set_xticks(x); ax.set_xticklabels(cats, fontsize=8); ax.set_yticks([]); ax_clean(ax, left=False)
    lo = min(0, min(vals)); hi = max(0, max(vals)); rng = hi - lo
    ax.set_ylim(ymin if ymin is not None else lo - rng * 0.18, ymax if ymax is not None else hi + rng * 0.22)
    if zero: ax.axhline(0, color=G3, lw=0.6)
    for xi, v in zip(x, vals): ax.text(xi, v + (rng * 0.03 if v >= 0 else -rng * 0.03), fmt.format(v) + unit, ha="center", va="bottom" if v >= 0 else "top", fontsize=8.5, color=INK, family=FONT_NUM, fontweight="bold")
    if title: ax.set_title(title, loc="left", fontsize=9, color=G1, pad=6)
    fig.tight_layout(pad=0.4); fig.savefig(OUT + "\\" + name + ".png"); plt.close(fig)

def lines(name, xs, series, w=5.2, h=3.0, ymin=None, ymax=None, fmt="{:.0f}", title=None, hl_last=False, ylabel=None, step=None):
    """series=[(label, values, color, lw)]"""
    fig, ax = plt.subplots(figsize=(w, h))
    for lab, vals, col, lw in series:
        ax.plot(xs, vals, color=col, lw=lw, marker="o", ms=3.2, mfc=col, mec=col)
        ax.text(xs[-1] + (xs[-1] - xs[0]) * 0.015, vals[-1], lab, va="center", ha="left", fontsize=8, color=col, fontweight="bold")
    ax_clean(ax); ax.grid(axis="y", color=G5, lw=0.6); ax.set_axisbelow(True)
    if ymin is not None: ax.set_ylim(ymin, ymax)
    ax.set_xticks(xs); ax.set_xticklabels([str(x) for x in xs], fontsize=7.5)
    if step: ax.set_yticks(np.arange(ymin, ymax + 1e-9, step))
    ax.tick_params(axis="y", labelsize=7.5)
    if ylabel: ax.set_ylabel(ylabel, fontsize=8, color=G2)
    if title: ax.set_title(title, loc="left", fontsize=9, color=G1, pad=6)
    ax.set_xlim(xs[0] - 0.3, xs[-1] + (xs[-1] - xs[0]) * 0.22)
    fig.tight_layout(pad=0.4); fig.savefig(OUT + "\\" + name + ".png"); plt.close(fig)

def donut(name, labels, vals, cols, center_text, w=3.2, h=3.2):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.pie(vals, colors=cols, startangle=90, counterclock=False, wedgeprops=dict(width=0.34, edgecolor=WHITE, linewidth=1.5))
    ax.text(0, 0.06, center_text[0], ha="center", va="center", fontsize=13, fontweight="bold", color=INK, family=FONT_NUM)
    ax.text(0, -0.16, center_text[1], ha="center", va="center", fontsize=8, color=G2)
    fig.tight_layout(pad=0.2); fig.savefig(OUT + "\\" + name + ".png"); plt.close(fig)

ps = lambda n: next(p for p in E["population"] if p["hadm"] == n)

if __name__ == "__main__":
    # 09 입지: 주요 자산까지 직선거리(m)
    hbar("c09_distance", ["성동시장", "경주읍성", "대릉원", "동궁과 월지", "황리단길"], [355, 497, 523, 920, 994], unit=" m", hl=None, color=G1, title="구 역사 기준 직선거리(m)")
    # 11 동서 유동 밀도
    hbar("c11_footfall", ["성동시장 반경 200m", "행복황촌(근사구역)"], [1174.6, 80.3], fmt="{:,.1f}", unit="", hl=0, color=G3, w=4.2, h=1.9, title="추정 유동 밀도(명/ha, 일평균)")
    # 14 주말/주중 비
    hbar("c14_weekend", ["시청 반경 500m", "황리단길 반경 300m"], [0.88, 1.72], fmt="{:.2f}", hl=1, color=G3, w=4.2, h=1.9, title="주말 / 주중 일평균 유동 비")
    # 20 원도심 인구 지수
    years = list(range(2015, 2026)); cols = [RED, G1, G3, G2]; ser = []
    for n, col, lw in (("황남동", RED, 2.0), ("황오동", INK, 1.6), ("성건동", G3, 1.6), ("월성동", G2, 1.6)):
        p = ps(n); ser.append((n, [100 * p["yearly"][str(y)] / p["yearly"]["2015"] for y in years], col, lw))
    lines("c20_pop_index", years, ser, ymin=50, ymax=100, step=10, title="원도심 4개 동 인구 지수(2015=100)")
    # 21 65세 이상 비율
    hbar("c21_aging", ["황남동", "황오동", "월성동", "성건동", "경주시"], [50.1, 43.8, 39.0, 36.7, 30.0], fmt="{:.1f}", unit="%", hl=[0, 1], color=G2, title="65세 이상 비율(%, 2026.08)")
    # 23 청년 순이동
    ys = E["youth"]; xs = [int(y) for y in ys["mig_years"]]
    ser = [("20–24세", ys["net"]["20-24세"], RED, 2.0), ("25–29세", ys["net"]["25-29세"], INK, 1.5), ("30–34세", ys["net"]["30-34세"], G3, 1.5)]
    lines("c23_migration", xs, ser, ymin=-1000, ymax=100, step=250, title="연령별 연간 순이동(명, 경주시)")
    # 24 체류시간 분포 / 방문 유형
    hbar("c24_stay", ["1–3시간", "3–6시간", "6–9시간", "24시간 이상"], [79.1, 15.0, 3.2, 2.7], fmt="{:.1f}", unit="%", hl=0, color=G3, title="황오동 현장 체류시간 분포(%, n=187)")
    hbar("c24_visit", ["숙박 방문", "당일 방문"], [55.3, 44.7], fmt="{:.1f}", unit="%", hl=None, color=G1, w=4.2, h=1.7, title="내국인 방문 유형(%, n=3,009)")
    # 26 야간 유동 비중
    hbar("c26_night", ["폐역 구역", "행복황촌", "성동시장", "황리단길"], [3.7, 4.4, 5.0, 5.5], fmt="{:.1f}", unit="%", hl=0, color=G2, title="23–05시 추정 유동 비중(%)")
    # 27 행복황촌 업종(2025.06 → 2026.06)
    fig, ax = plt.subplots(figsize=(4.2, 2.4)); x = np.arange(2)
    ax.bar(x - 0.17, [15, 22], width=0.32, color=G4, label="2025.06"); ax.bar(x + 0.17, [15, 29], width=0.32, color=[G1, RED], label="2026.06")
    for xi, (a, b) in enumerate([(15, 15), (22, 29)]):
        ax.text(xi - 0.17, a + 0.6, str(a), ha="center", fontsize=8.5, family=FONT_NUM, fontweight="bold", color=INK); ax.text(xi + 0.17, b + 0.6, str(b), ha="center", fontsize=8.5, family=FONT_NUM, fontweight="bold", color=INK)
    ax.set_xticks(x); ax.set_xticklabels(["생활", "관광·체류"]); ax.set_yticks([]); ax_clean(ax, left=False); ax.set_ylim(0, 36)
    ax.legend(frameon=False, fontsize=7.5, loc="upper left"); ax.set_title("선택 업종군 업소 수(개, 행복황촌 11업종)", loc="left", fontsize=9, color=G1, pad=6)
    fig.tight_layout(pad=0.4); fig.savefig(OUT + r"\c27_biz.png"); plt.close(fig)
    # 28 황오동 인허가 순증감
    groups = ["숙박·체류", "생활서비스·의료", "카페·휴게음식", "음식점·제과", "유흥·오락", "생활소매·식품제조"]
    v = [E["biz2024"]["open"][g] - E["biz2024"]["close"][g] for g in groups]
    vbar("c28_permits", groups, v, fmt="{:+d}", hl=[5], color=G2, w=5.4, h=2.8, title="점포형 업종군별 순증감(건, 2024 인허가)", zero=True)
    # 05 역사: 가로 방위 비율
    hbar("c05_azimuth", ["공통 격자 방위", "사선 1(파랑)", "사선 2(초록)", "기타"], [57, 5, 6, 33], unit="%", hl=0, color=G3, w=4.0, h=2.2, title="현재 가로의 방위 구성(%)")
    # 19 인구 변화(2015→2025)
    hbar("c19_popchg", ["현곡면", "용강동", "월성동", "성건동", "황오동", "황남동"], [33.3, 32.8, -22.3, -29.0, -32.7, -44.8], fmt="{:+.1f}", unit="%", hl=[2, 3, 4, 5], color=G3, w=4.2, h=3.0, title="인구 변화 2015→2025(%)")
    # 22 청년 비율
    hbar("c22_youth", ["황오동", "경주시", "황성·동천·용강·현곡 합"], [11.4, 12.9, 44.5], fmt="{:.1f}", unit="%", hl=0, color=G3, w=4.2, h=1.9, title="20–34세(황오·시 비율) · 4개 지역 청년 점유(%)")
    # 면적 3종
    hbar("c03_area", ["시 구상(1단계)", "고시 구역", "계획 경계(본 계획)"], [79438, 156460, 228025], unit="㎡", hl=2, color=G3, w=4.6, h=2.0, title="면적 기준 3종(㎡)")
    # 토지이용 구성 도넛
    donut("c_landuse_donut", ["획지", "공원·녹지", "도로", "보행"], [80526, 73082, 20373, 54044], [G1, G4, G3, RED], ("228,025㎡", "계획구역"))
    # 연면적 구성비(기준안 118,836㎡)
    cats = ["공공청사·의회", "공동주택·주민시설", "청년 업무", "창작·체험", "역사·문화·공연", "근생·판매", "운동", "주차·관문"]
    vals = [24276, 30304, 10335, 5965, 10888, 3234, 2500, 33312]
    hbar("c_gfa_mix", cats, vals, unit="㎡", hl=4, color=G2, w=5.0, h=3.2, title="연면적 구성(㎡, 기준안 합계 118,836)")
    print("charts ok")
