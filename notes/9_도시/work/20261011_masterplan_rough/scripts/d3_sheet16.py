"""D3 v2 조감도 시트(16:9) — 참고 스타일: 여천역 조감도(색 박스 호출·번호 마커·용지명 라벨·녹색 띠 이름)
입력: sheets/axo16.png(+_meta.pkl), sheets/court16.png(그레이트 코트 확대), data/design.pkl
출력: 구경주역_마스터플랜_v2.png/pdf (폴더 루트)"""
import os, sys, pickle, math
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Circle, Rectangle, FancyBboxPatch
import matplotlib.patheffects as pe
from matplotlib.image import imread
from shapely.geometry import box, Point
from shapely.ops import unary_union, polylabel
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "..", "data"); SH = os.path.join(HERE, "..", "sheets"); OUT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
from d2_axo import Cam, polys
for f in ("malgun.ttf", "malgunbd.ttf"):
    try: fm.fontManager.addfont(r"C:\Windows\Fonts\%s" % f)
    except Exception: pass
plt.rcParams["font.family"] = "Malgun Gothic"; plt.rcParams["axes.unicode_minus"] = False
INK = "#333333"; GREY = "#666666"

S = pickle.load(open(os.path.join(D, "design.pkl"), "rb"))
LOTS, PARKS, OPEN, MASS, CATS, SUM, GL = S["LOTS"], S["PARKS"], S["OPEN"], S["MASS"], S["CATS"], S["SUM"], S["GLASS"]
META = pickle.load(open(os.path.join(SH, "axo16_meta.pkl"), "rb"))
cam = Cam(META["az"], META["el"], META["W"], META["H"], META["ps"], META["xc"], META["yc"])
PW, PH = 400.0, 225.0
def mm(x, y, z=0.0):
    px, py = cam.xy(x, y, z); return px * PW / META["W"], py * PH / META["H"]
def halo(w=2.0, c="white"): return [pe.withStroke(linewidth=w, foreground=c)]
def f0(v): return format(int(round(v)), ",")


fig = plt.figure(figsize=(PW / 25.4, PH / 25.4), dpi=240, facecolor="white")
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, PW); ax.set_ylim(PH, 0); ax.axis("off")
ax.imshow(imread(os.path.join(SH, "axo16.png")), extent=[0, PW, PH, 0], aspect="auto", zorder=0, interpolation="bilinear"); ax.set_xlim(0, PW); ax.set_ylim(PH, 0)
def T(x, y, s, fs=8, c=INK, ha="left", va="center", bold=False, z=10, **kw):
    return ax.text(x, y, s, fontsize=fs, color=c, ha=ha, va=va, fontweight="bold" if bold else "normal", zorder=z, **kw)
def L(xs, ys, c=INK, lw=0.6, z=8, **kw): ax.plot(xs, ys, color=c, lw=lw, zorder=z, solid_capstyle="butt", **kw)
def wmm(t):
    fig.canvas.draw(); return t.get_window_extent(fig.canvas.get_renderer()).width / fig.dpi * 25.4

# ── 용지명 라벨(획지 위, 흰 테두리 글씨) ──
BLD = {l["no"]: unary_union([m["g"] for m in MASS if m["lot"] == l["no"]]) for l in LOTS}
for l in LOTS:
    if l["no"] == 9: continue                                       # 9번은 ② 호출이 설명
    free = l["g"].difference(BLD[l["no"]].buffer(3.0))
    fp = max(polys(free), key=lambda g: g.area) if not free.is_empty else l["g"]
    pt = polylabel(fp, 1.0) if fp.area > 60 else l["g"].representative_point()
    x, y = mm(pt.x, pt.y, 0.5)
    T(x, y, l["use"], fs=5.6, c="#3a3a3a", ha="center", path_effects=halo(1.8), z=12)
for p in PARKS:
    pt = polylabel(max(polys(p["g"]), key=lambda g: g.area), 1.0); x, y = mm(pt.x, pt.y, 0.5)
    T(x, y, "근린공원", fs=5.6, c="#2e6b2a", ha="center", path_effects=halo(1.8), z=12)

# ── 녹색 띠 이름(띠 방향으로 회전) ──
def band_text(p0, p1, s, fs, c, at=0.5, dz=0.0):
    a = mm(*p0, dz); b = mm(*p1, dz)
    ang = -math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
    if ang > 90: ang -= 180
    if ang < -90: ang += 180
    x = a[0] + (b[0] - a[0]) * at; y = a[1] + (b[1] - a[1]) * at
    T(x, y, s, fs=fs, c=c, ha="center", bold=True, rotation=ang, rotation_mode="anchor", style="italic", path_effects=halo(2.6), z=13)
y0b, y1b = S["DBAND"]; ym = (y0b + y1b) / 2
band_text((-80, ym), (60, ym), "동서 선형공원 · 가로광장", 13.5, "#2f8f3a", 0.5)
band_text((470, ym), (600, ym), "도시로 이어지는 녹색 띠", 8.5, "#2f8f3a", 0.5)
# (남북 중앙 보행축 라벨은 폭 30 m 축 위에 들어가지 않아 생략)
v = np.array([0.5394, 0.842]); pa = np.array([131.2, 59.5]) + np.array([-0.842, 0.5394]) * 10.0
# (사선 보행축 라벨은 서북서 시점에서 관광지원센터에 가려 생략 — ⑤ 호출이 설명)

# ── 번호 마커 ──
COL = {1: "#3DA24B", 2: "#C2643A", 3: "#3A74C0", 4: "#C99A16", 5: "#EE7A2B"}
def lot_c(no, dz=4.0):
    top = max([m for m in MASS if m["lot"] == no], key=lambda m: (m["h"], m["g"].area)); c = polylabel(max(polys(top["g"]), key=lambda g: g.area), 0.5)
    return mm(c.x, c.y, top["h"] + dz)
o_, ua, vb = np.array(GL["o"]), np.array(GL["ua"]), np.array(GL["vb"])
st = o_ + 48.5 * ua + (-30.0) * vb                                      # 역전광장 중앙(역사 정면 앞)
MK = {1: mm(200.0, ym, 1.0), 2: mm(st[0], st[1], 2.0), 3: lot_c(1), 4: lot_c(4), 5: mm(150.0, 95.0, 1.0)}
for k, (x, y) in MK.items():
    ax.add_patch(Circle((x, y), 3.1, fc=COL[k], ec="white", lw=1.1, zorder=15)); T(x, y + 0.15, str(k), fs=9, c="white", bold=True, ha="center", z=16)

# ── 호출(작은 머리말 · 색 박스 제목 · 설명) ──
def callout(k, x, y, w, sub, title, desc):
    c = COL[k]
    T(x, y, sub, fs=10.5, c=c, bold=True, va="bottom", z=14)
    ax.add_patch(Rectangle((x, y + 1.2), w, 10.0, fc=c, ec="none", zorder=13))
    T(x + w / 2, y + 6.3, title, fs=14.5, c="white", bold=True, ha="center", z=14)
    for j, ln in enumerate(desc): T(x, y + 15.5 + j * 4.4, ln, fs=7.6, c=GREY, z=14)
    return y + 15.5 + 4.4 * (len(desc) - 1) + 2.6                              # 설명 아래 끝


def lead(k, pts):
    """박스 → 마커 직각 지시선(마지막 점 = 마커 가장자리)"""
    c = COL[k]; xs, ys = zip(*pts); L(list(xs), list(ys), c=c, lw=0.8, z=12)
    ax.add_patch(Circle(pts[0], 0.6, fc=c, ec="none", zorder=12))


R = 3.1
yb = callout(4, 14, 14, 78, "정주 + 생활", "청년·신혼 주거 마을", ["판상 8동 5층·인동간격 24 m(동당 32세대 가정 시 256세대)", "생활체육관·건강돌봄센터·공동체텃밭"])
mx, my = MK[4]; lead(4, [(92, 20.2), (mx, 20.2), (mx, my - R)])
yb = callout(1, 150, 14, 86, "가로광장 + 선형공원", "동서 선형공원", ["폭 40 m·연장 약 290 m, 가로수 4열과 중앙 가로광장", "서측 원도심 방면에서 동측 생활권까지 녹색 띠로 연결"])
mx, my = MK[1]; lead(1, [(mx, yb), (mx, my - R)])
yb = callout(5, 302, 14, 86, "관문 + 모빌리티", "남측 관문·모빌리티 허브", ["관광객 주출입구 관문광장에서 사선 보행축(폭 20 m)으로 진입", "공유주차장 5층·모빌리티 허브 4층, 외곽도로 직접 접속"])
mx, my = MK[5]; lead(5, [(mx, yb), (mx, my - R)])
yb = callout(3, 14, 176, 78, "공공 + 업무", "공공청사·청년창업 거점", ["공공청사 본관 7층·민원·시민홀동 5층, 청사 앞 시민광장", "유관기관 업무동 5층·청년창업지원센터 4층"])
mx, my = MK[3]; lead(3, [(92, 182.2), (mx, 182.2), (mx, my + R)])
yb = callout(2, 298, 192, 96, "어댑티브 리유즈 + 유리 지붕 중정", "구 경주역 그레이트 코트",
             ["구 역사(2층·모임지붕) 존치·복원, 정면 역전광장과 중앙 축", "배후 ㄷ자 지역문화원·소상공인 상생동 5층, 유리 지붕 중정 약 %s㎡" % f0((GL["a1"] - GL["a0"]) * (GL["b1"] - GL["b0"]))])
mx, my = MK[2]; lead(2, [(298, 198.2), (mx, 198.2), (mx, my + R)])

# ── 그레이트 코트 확대도(우하단) ──
ix, iy, iw = 312.0, 130.0, 82.0
img = imread(os.path.join(SH, "court16.png")); ih = iw * img.shape[0] / img.shape[1]
ax.add_patch(Rectangle((ix - 1.0, iy - 1.0), iw + 2.0, ih + 2.0, fc="white", ec="#c9c9c9", lw=0.6, zorder=13))
ax.imshow(img, extent=[ix, ix + iw, iy + ih, iy], aspect="auto", zorder=14, interpolation="bilinear"); ax.set_xlim(0, PW); ax.set_ylim(PH, 0)
T(ix, iy + ih + 3.4, "그레이트 코트 확대 — 참고: 도쿄역 마루노우치 역사, 대영박물관 그레이트 코트", fs=5.9, c=GREY, z=14)


# ── 범례(하단 띠) ──
ly = 219.5
ax.add_patch(Rectangle((0, ly - 3.6), PW, 7.2, fc="white", ec="none", alpha=0.92, zorder=13))
ex = 14
for key in ["공공업무", "업무·창업", "문화", "창작", "판매", "생활SOC", "주거", "역사", "방문자", "주차"]:
    col, lab = CATS[key]
    ax.add_patch(Rectangle((ex, ly - 1.7), 4.2, 3.4, fc=col, ec="#9a9a9a", lw=0.25, zorder=14)); t = T(ex + 5.4, ly, lab, fs=6.0, z=14); ex += 5.4 + wmm(t) + 4.5
ax.add_patch(Rectangle((ex, ly - 1.7), 4.2, 3.4, fc="#7cc865", ec="#9a9a9a", lw=0.25, zorder=14)); t = T(ex + 5.4, ly, "공원·선형공원·보행축", fs=6.0, z=14); ex += 5.4 + wmm(t) + 4.5
ax.add_patch(Rectangle((ex, ly - 1.7), 4.2, 3.4, fc="#cfe6f3", ec="#7d98ab", lw=0.4, zorder=14)); T(ex + 5.4, ly, "유리 지붕", fs=6.0, z=14)
T(PW - 10, ly, "개념안 · 규모 총량·고도지구·허용기준 미반영", fs=5.6, c="#8a8a8a", ha="right", z=14)

name = "구경주역_마스터플랜_v2"
fig.savefig(os.path.join(OUT, name + ".png"), dpi=240, facecolor="white")
fig.savefig(os.path.join(OUT, name + ".pdf"), facecolor="white")
fig.savefig(os.path.join(SH, "sheet16_preview.png"), dpi=120, facecolor="white")
print("saved", name)
