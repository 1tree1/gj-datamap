"""V0 사용자 러프 배치(라이노 aardvark 선택 222개) 확인용 평면 — 로컬 좌표(X0,Y0) 격자 표시"""
import json, os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "..", "data")
plt.rcParams["font.family"] = "Malgun Gothic"
d = json.load(open(os.path.join(D, "rough_sel.json"), encoding="utf-8"))
X0, Y0 = 1166600, 1761100
fig, ax = plt.subplots(figsize=(14, 36), dpi=110)
for i, c in enumerate(d["curves"]):
    P = [(p[0] - X0, p[1] - Y0) for p in c["pts"]]
    if len(P) < 2: continue
    xs, ys = zip(*P)
    col = "#1f5fbf" if c["layer"] == "B0014112" else ("#c00" if "::" in c["layer"] else "#333")
    ax.plot(xs, ys, color=col, lw=0.8)
    if c["closed"] or len(P) > 2:
        ax.text(sum(xs) / len(xs), sum(ys) / len(ys), str(i), fontsize=6, color="#888")
for t in d["texts"]:
    ax.text(t["x"] - X0, t["y"] - Y0, t["text"].replace("\r", ""), fontsize=7, color="#a05000", va="bottom")
ax.set_xlim(90, 470); ax.set_ylim(15, 1010); ax.set_aspect("equal")
ax.set_xticks(range(100, 470, 20)); ax.set_yticks(range(20, 1010, 20)); ax.grid(lw=0.3, color="#ddd")
ax.tick_params(labelsize=6)
fig.savefig(os.path.join(HERE, "..", "sheets", "v0_rough_plot.png"), bbox_inches="tight")
