"""D3 조감도 시트 'Site Anchors'(A3 가로) — 렌더 위에 획지 번호·호출선·획지 목록·범례를 얹는다
입력: sheets/axo_sheet.png(+_meta.pkl), data/design.pkl → 출력: 구경주역_마스터플랜_러프정리_v1.png/pdf (폴더 루트)"""
import os, sys, pickle, textwrap
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Circle, Rectangle
import matplotlib.patheffects as pe
from matplotlib.image import imread
from shapely.ops import unary_union, polylabel
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "..", "data"); SH = os.path.join(HERE, "..", "sheets"); OUT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
from d2_axo import Cam, polys
for f in ("malgun.ttf", "malgunbd.ttf"):
    try: fm.fontManager.addfont(r"C:\Windows\Fonts\%s" % f)
    except Exception: pass
plt.rcParams["font.family"] = "Malgun Gothic"; plt.rcParams["axes.unicode_minus"] = False
INK = "#222222"; RED = "#d7191c"; PARKC = "#2e7d32"

S = pickle.load(open(os.path.join(D, "design.pkl"), "rb"))
LOTS, PARKS, OPEN, MASS, CATS, SUM = S["LOTS"], S["PARKS"], S["OPEN"], S["MASS"], S["CATS"], S["SUM"]
IMG = os.path.join(SH, "axo_sheet.png"); META = pickle.load(open(os.path.join(SH, "axo_sheet_meta.pkl"), "rb"))
cam = Cam(META["az"], META["el"], META["W"], META["H"], META["ps"], META["xc"], META["yc"])
def mm(x, y, z=0.0):
    px, py = cam.xy(x, y, z); return px * 420.0 / META["W"], py * 297.0 / META["H"]


class Page:
    def __init__(self, W=420.0, H=297.0, dpi=150):
        self.fig = plt.figure(figsize=(W / 25.4, H / 25.4), dpi=dpi, facecolor="white")
        self.ax = self.fig.add_axes([0, 0, 1, 1]); self.ax.set_xlim(0, W); self.ax.set_ylim(H, 0); self.ax.axis("off")
    def t(self, x, y, s, fs=8, c=INK, ha="left", va="center", bold=False, z=5, **kw):
        return self.ax.text(x, y, s, fontsize=fs, color=c, ha=ha, va=va, fontweight="bold" if bold else "normal", zorder=z, **kw)
    def line(self, x0, y0, x1, y1, c=INK, lw=0.6, z=3, **kw): self.ax.plot([x0, x1], [y0, y1], color=c, lw=lw, zorder=z, solid_capstyle="butt", **kw)
    def rect(self, x, y, w, h, fc="none", ec="none", lw=0.0, z=2, **kw): self.ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec=ec, lw=lw, zorder=z, **kw))


def halo(w=2.2, c="white"): return [pe.withStroke(linewidth=w, foreground=c)]
def f0(v): return format(int(round(v)), ",")


pg = Page()
pg.ax.imshow(imread(IMG), extent=[0, 420, 297, 0], aspect="auto", zorder=0, interpolation="bilinear"); pg.ax.set_xlim(0, 420); pg.ax.set_ylim(297, 0)

# ── 머리글 ──
x, y = 16, 14
pg.t(x, y, "Masterplan : Site Anchors", fs=11, c=RED)
tt = pg.t(x, y + 9.5, "Site Anchors", fs=21, bold=True)
pg.fig.canvas.draw(); bb = tt.get_window_extent(pg.fig.canvas.get_renderer()); wmm = bb.width / pg.fig.dpi * 25.4
pg.line(x + wmm + 3.5, y + 5.5, x + wmm + 3.5, y + 13.5, c="#555", lw=0.8)
pg.t(x + wmm + 7, y + 9.8, "획지별 용도·건축물 구성", fs=14, c="#444")
pg.t(x, y + 19, "러프 배치 정리안 — 공공청사 최고 7층, 그 외 건축물 4~5층(구 경주역사 존치 2층). 규모 총량·고도지구·역사문화환경 허용기준은 반영하지 않은 개념안", fs=8.0, c="#555")
B_ = SUM["boundary"]
pg.t(x, y + 24.5, "구역 %s㎡ · 획지 %s㎡(%.1f%%) · 공원 %s㎡(%.1f%%) · 보행녹지축·광장 %s㎡(%.1f%%) · 도로 %s㎡(%.1f%%) · 보도 %s㎡(%.1f%%) · 건축물 %d동 · 연면적 %s㎡(참고)" % (
    f0(B_), f0(SUM["lot_total"]), SUM["lot_total"] / B_ * 100, f0(SUM["park_total"]), SUM["park_total"] / B_ * 100, f0(SUM["open_total"]), SUM["open_total"] / B_ * 100,
    f0(SUM["road_total"]), SUM["road_total"] / B_ * 100, f0(SUM["walk_total"]), SUM["walk_total"] / B_ * 100, SUM["n_mass"], f0(SUM["gfa"])), fs=7.0, c="#444")

# ── 획지 번호 마커 ──
BLD = {l["no"]: unary_union([m["g"] for m in MASS if m["lot"] == l["no"]]) for l in LOTS}
mk = {}
for l in LOTS:
    free = l["g"].difference(BLD[l["no"]].buffer(2.5))
    free = max(polys(free), key=lambda g: g.area) if not free.is_empty else l["g"]
    pt = polylabel(free, 1.0) if free.area > 80 else l["g"].representative_point()
    if l["no"] in (1, 4, 5, 6, 13):                                      # 건물이 큰 획지는 가장 높은 동 위에 둔다
        top = max([m for m in MASS if m["lot"] == l["no"]], key=lambda m: (m["h"], m["g"].area)); c = polylabel(max(polys(top["g"]), key=lambda g: g.area), 0.5)
        mk[l["no"]] = mm(c.x, c.y, top["h"] + 7.0)
    else:
        mk[l["no"]] = mm(pt.x, pt.y, 6.0 + l["maxh"] * 0.5)
pmk = {}
for p in PARKS + OPEN:
    g = max(polys(p["g"]), key=lambda g: g.area)
    if p["key"] == "E": pt = polylabel(g.intersection(__import__("shapely").geometry.box(250, 650, 290, 770)), 0.5)
    elif p["key"] == "F": pt = polylabel(g, 0.5)
    else: pt = polylabel(g, 1.0)
    pmk[p["key"]] = mm(pt.x, pt.y, 8.0)
for no, (xx, yy) in mk.items():
    pg.ax.add_patch(Circle((xx, yy), 3.0, fc="white", ec=INK, lw=0.7, zorder=8)); pg.t(xx, yy + 0.1, str(no), fs=7.2, bold=True, ha="center", z=9)
for k, (xx, yy) in pmk.items():
    pg.ax.add_patch(Circle((xx, yy), 3.0, fc=PARKC, ec="white", lw=0.8, zorder=8)); pg.t(xx, yy + 0.1, k, fs=7.4, bold=True, c="white", ha="center", z=9)

# ── 호출선 ──
units = 8 * 32
CALL = [
    ("F", "관문광장·사선 보행축 · F", "남서 관광객 주출입구에서 중앙 보행축까지 폭 20 m 사선 보행로. 관광안내소(10)·관문 가로상가(11)가 양측에 면함."),
    (9, "구 경주역사·지역문화 · Plot 9", "구 역사 존치(2층). 지역문화원·소상공인 상생 클러스터 4층이 ㄷ자로 역전 마당을 둘러쌈."),
    (13, "공유주차장·모빌리티 허브 · Plot 13", "공유주차장 5층·모빌리티 허브 4층, 옥상 태양광. 동서 도로(폭 20 m) 직접 접속."),
    (8, "창작·체험 레지던시 · Plot 8", "제작동 3·거주동 3, 작가 교류·행사동, 실내 체험관. 1층 가로상가가 보행녹지축에 면함."),
    ("D", "동서 보행녹지축 · D", "폭 40 m 녹도 %s㎡. 남북 중앙 보행축(폭 30 m)과 교차광장에서 만남." % f0([o for o in OPEN if o["key"] == "D"][0]["area"])),
    (1, "공공청사 · Plot 1", "동측 본관 7층·북측 민원·시민홀동 5층 ㄱ자. 청사 앞 시민광장이 중앙 보행축에 면함."),
    (4, "청년·신혼 공공임대 · Plot 4", "판상 8동·5층, 인동간격 24 m. 동당 32세대(러프 메모) 가정 시 %d세대." % units),
]
BW = 47.0; YT = 262.0
pg.rect(0, YT - 3.2, 420, 31.0, fc="white", ec="none", z=5, alpha=0.70)
def pos(k): return pmk[k] if isinstance(k, str) else mk[k]
order = sorted(range(len(CALL)), key=lambda i: pos(CALL[i][0])[0])
# 글 시작 x: 마커 x에 가장 가깝게(제곱오차 최소), 이웃 글과 최소 간격 PITCH — 간격 제약 등조회귀(PAV)
PITCH = BW + 1.5
ideal = [pos(CALL[i][0])[0] - 3.0 for i in order]
z = [ideal[k] - k * PITCH for k in range(len(order))]
blocks = [[v, 1] for v in z]; out = []
for v in z:
    out.append([v, 1])
    while len(out) > 1 and out[-2][0] / out[-2][1] > out[-1][0] / out[-1][1]:
        a = out.pop(); out[-1][0] += a[0]; out[-1][1] += a[1]
fit = [b[0] / b[1] for b in out for _ in range(b[1])]
xs_ = [fit[k] + k * PITCH for k in range(len(order))]
sh = max(0.0, 8.0 - xs_[0]) - max(0.0, xs_[-1] - (420 - BW - 4))
XS = {i: xs_[k] + sh for k, i in enumerate(order)}
for ci, (key, ttl, desc) in enumerate(CALL):
    xx, yy = pos(key); xs = XS[ci]
    pg.line(xx, yy + 3.0, xx, YT, c="#333", lw=0.6, z=6); pg.line(xx, YT, xs + 2.6, YT, c="#333", lw=0.6, z=6); pg.line(xs + 2.6, YT, xs + 2.6, YT + 2.4, c="#333", lw=0.6, z=6)
    pg.ax.add_patch(Circle((xx, YT), 0.55, fc="#333", ec="none", zorder=7))
    pg.t(xs + 4.0, YT + 3.6, ttl, fs=7.2, bold=True, va="center", path_effects=halo(1.8, "white"), z=9)
    for j, ln in enumerate(textwrap.wrap(desc, 24)): pg.t(xs + 4.0, YT + 7.8 + j * 3.4, ln, fs=6.2, c="#333", va="center", path_effects=halo(1.6, "white"), z=9)

# ── 획지 목록 패널(좌상) — 번호 · 색 · 시설명 [용지] · 면적 · 최고층 ──
px0, py0 = 12, 44.0
ent = [(str(l["no"]), l["name"], l["use"], "%s㎡ · %dF" % (f0(l["area"]), l["maxf"]), CATS[l["cat"]][0]) for l in LOTS]
ent += [(p["key"], p["name"], p["kind"], "%s㎡" % f0(p["area"]), PARKC) for p in PARKS + OPEN]
NR = 5; CW = 99.0
pg.rect(px0, py0, CW * 4 + 4, NR * 5.3 + 3.5, fc="white", ec="none", z=6, alpha=0.82)
for i, (n, nm, use, ar, col) in enumerate(ent):
    c, rr = divmod(i, NR); xx = px0 + 3 + c * CW; yy = py0 + 4.2 + rr * 5.3
    isp = n.isalpha()
    pg.ax.add_patch(Circle((xx + 2.0, yy), 1.8, fc=col if isp else "white", ec="white" if isp else INK, lw=0.45, zorder=8))
    pg.t(xx + 2.0, yy + 0.1, n, fs=5.6, bold=True, ha="center", c="white" if isp else INK, z=9)
    if not isp: pg.rect(xx + 4.6, yy - 1.6, 1.3, 3.2, fc=col, z=8)
    tn = pg.t(xx + 7.0, yy, nm, fs=6.1, z=9)
    pg.fig.canvas.draw(); wb = tn.get_window_extent(pg.fig.canvas.get_renderer()).width / pg.fig.dpi * 25.4
    pg.t(xx + 7.0 + wb + 1.4, yy, use, fs=5.2, c="#8a8a8a", z=9)
    pg.t(xx + CW - 4.0, yy, ar, fs=5.6, c="#555", ha="right", z=9)

# ── 범례 ──
ly = 292.0
pg.rect(0, ly - 4.2, 420, 8.4, fc="white", ec="none", z=6, alpha=0.88)
pg.t(16, ly, "범례", fs=7, bold=True, z=9)
ex = 27
for key in ["공공업무", "업무·창업", "문화", "창작", "판매", "생활SOC", "주거", "역사", "방문자", "주차"]:
    col, lab = CATS[key]
    pg.rect(ex, ly - 2, 5, 4, fc=col, ec="#555", lw=0.25, z=9); tl = pg.t(ex + 6.5, ly, lab, fs=6.3, z=9)
    pg.fig.canvas.draw(); ex += 6.5 + tl.get_window_extent(pg.fig.canvas.get_renderer()).width / pg.fig.dpi * 25.4 + 5.0
pg.rect(ex, ly - 2, 5, 4, fc="#a9d577", ec="#555", lw=0.25, z=9); tl = pg.t(ex + 6.5, ly, "옥상녹화·공원·녹지", fs=6.3, z=9)
pg.fig.canvas.draw(); ex += 6.5 + tl.get_window_extent(pg.fig.canvas.get_renderer()).width / pg.fig.dpi * 25.4 + 5.0
pg.rect(ex, ly - 2, 5, 4, fc="#5d6b80", ec="#555", lw=0.25, z=9); pg.t(ex + 6.5, ly, "옥상 태양광", fs=6.3, z=9)
pg.t(404, ly, "건축물 1층 분홍 띠 = 가로상점(근린생활)", fs=6.0, c="#666", ha="right", z=9)

name = "구경주역_마스터플랜_러프정리_v1"
pg.fig.savefig(os.path.join(OUT, name + ".png"), dpi=200, facecolor="white")
pg.fig.savefig(os.path.join(OUT, name + ".pdf"), facecolor="white")
pg.fig.savefig(os.path.join(SH, "sheet_preview.png"), dpi=110, facecolor="white")
print("saved", name)
