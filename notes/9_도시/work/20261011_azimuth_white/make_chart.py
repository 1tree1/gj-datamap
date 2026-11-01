# 가로 방위 분포 — 흰 배경 재제작 (원본 이미지의 막대 높이를 픽셀에서 복원한 값 사용)
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm

for f in ("Malgun Gothic", "NanumGothic", "AppleGothic"):
    if any(f == x.name for x in fm.fontManager.ttflist):
        plt.rcParams["font.family"] = f
        break
plt.rcParams["axes.unicode_minus"] = False

h = json.load(open("heights.json", encoding="utf-8"))
h = [min(v, 11.6) for v in h]

INK, SUB, GRID = "#1a1d1e", "#6b7377", "#e3e6e8"
BAR, GREEN, BLUE = "#4a5256", "#1f9d6b", "#3b63d6"

fig = plt.figure(figsize=(6.4, 5.0), dpi=220, facecolor="white")
fig.text(0.04, 0.93, "가로 방위 분포", fontsize=16, fontweight="bold", color=INK, va="center")

ax = fig.add_axes([0.075, 0.43, 0.89, 0.43], facecolor="white")
ax.bar([i + 0.5 for i in range(180)], h, width=0.85, color=BAR, linewidth=0)
ax.set_xlim(0, 180)
ax.set_ylim(0, 12.6)
ax.set_yticks([0, 3, 6, 9])
ax.set_xticks([0, 45, 90, 135, 180])
ax.set_xticklabels([f"{t}°" for t in (0, 45, 90, 135, 180)])
ax.grid(axis="y", color=GRID, linewidth=0.8)
ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color("#b9bfc2")
ax.tick_params(colors=SUB, labelsize=7, length=0, pad=4)
ax.set_xlabel("가로 방위 (동=0°, 반시계, mod 180) · 세로축 km", fontsize=7, color=SUB, labelpad=6)

def vline(x, c, ls=":"):
    ax.axvline(x, color=c, linestyle=ls, linewidth=1.0, ymax=0.97)

vline(42, GREEN); ax.text(43.5, 9.3, "사선 A", color=GREEN, fontsize=7.5, va="center")
vline(148, GREEN); ax.text(149.5, 11.9, "사선 B", color=GREEN, fontsize=7.5, va="center")
vline(88, BLUE); ax.text(91.5, 11.9, "주 격자 남북", color=INK, fontsize=7.5, va="center")
ax.text(91.5, 10.7, "읍성 동맥", color=BLUE, fontsize=7.5, va="center")
vline(180, "#8a9195"); ax.text(178.5, 10.7, "주 격자 동서", color=INK, fontsize=7.5, va="center", ha="right")

cap = ("도로중심선 212 km의 방위(길이가중, 1° 간격). 0°·90°에 가까운\n"
       "두 봉우리가 한 축의 남북·동서 가로다. 사선 A는 동천동 회전 격자,\n"
       "사선 B는 북천 변 도로.")
fig.text(0.04, 0.27, cap, fontsize=10.5, color=INK, va="top", linespacing=1.6)

fig.savefig("azimuth_distribution_white.png", facecolor="white")
fig.savefig("azimuth_distribution_white.svg", facecolor="white")
