"""S4 네 장의 A3 시트 — 01 획지구획도+획지계획표 / 02 조감도 Site Anchors / 03 면적표 Summary+Site Plan / 04 도로계획도+도로계획표 (통영 보고서 형식, 이전 안 k6~k9와 같은 체재)."""
import pickle, sys, os, math, textwrap
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.path import Path
from matplotlib.patches import PathPatch, Circle, Rectangle
import matplotlib.patheffects as pe
from matplotlib.image import imread
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union, polylabel
from shapely import affinity
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "..", "data"); OUT = os.path.join(HERE, "..")
sys.path.insert(0, r"C:\Users\OFFICE\Desktop\9_도시\work\20261005_plan_massing\scripts"); sys.path.insert(0, HERE)
from geomkit import polys
import s3_axo as K
for f in ("malgun.ttf", "malgunbd.ttf"):
    try: fm.fontManager.addfont(r"C:\Windows\Fonts\%s" % f)
    except Exception: pass
plt.rcParams["font.family"] = "Malgun Gothic"; plt.rcParams["axes.unicode_minus"] = False
P = pickle.load(open(os.path.join(D, "design.pkl"), "rb")); TC = pickle.load(open(os.path.join(D, "tables.pkl"), "rb"))
U, LOTS, PARKS, BUILD, ROADS, COURTS, OPEN, DECKS, RAILS, WEDGE, ROOFG = P["U"], P["LOTS"], P["PARKS"], P["BUILD"], P["ROADS"], P["COURTS"], P["OPEN"], P["DECKS"], P["RAILS"], P["WEDGE"], P["ROOFG"]
TR, S, F, SM, RR = TC["lot_rows"], TC["site"], TC["fac"], TC["summary"], TC["road_rows"]
CATCOL = {"문화·교육·공공": "#6f9fdc", "상업·업무": "#e4573a", "창조산업": "#a98bd3", "여가·오락·체육": "#2fab9d", "주거": "#f1d247", "판매·음식": "#f4a0c2", "교통·방문자": "#c6c6c6", "역사유산": "#c9742f", "오픈스페이스": "#9fd36b"}
CATEN = {"문화·교육·공공": "Cultural / Edu / Civic", "상업·업무": "Office / Commercial", "창조산업": "Creative Industry", "여가·오락·체육": "Leisure / Recreation", "주거": "Residential", "판매·음식": "Retail / F&B", "교통·방문자": "Mobility / Visitor", "역사유산": "Heritage", "오픈스페이스": "Open Space"}
CATORDER = ["상업·업무", "창조산업", "문화·교육·공공", "판매·음식", "여가·오락·체육", "주거", "역사유산", "교통·방문자", "오픈스페이스"]
INK = "#222222"; GREY = "#ececec"; RED = "#d7191c"
LOTBY = {d["no"]: d for d in LOTS}
def tint(h, t):
    c = np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], float) * (1 - t) + 255 * t; return "#%02x%02x%02x" % tuple(int(round(v)) for v in c)
def path_of(p):
    verts, codes = [], []
    for ring in [p.exterior] + list(p.interiors):
        cs = list(ring.coords); verts += cs; codes += [Path.MOVETO] + [Path.LINETO] * (len(cs) - 2) + [Path.CLOSEPOLY]
    return Path(verts, codes)
def fill(ax, geom, fc="none", ec="none", lw=0.0, z=1, alpha=1.0, **kw):
    for p in polys(geom):
        if not p.is_empty: ax.add_patch(PathPatch(path_of(p), fc=fc, ec=ec, lw=lw, zorder=z, alpha=alpha, **kw))
def halo(w=2.2, c="white"): return [pe.withStroke(linewidth=w, foreground=c)]
def num_circle(ax, x, y, s, r=9.0, fs=8, fc="white", ec=INK, tc=INK, z=20, lw=0.8):
    ax.add_patch(Circle((x, y), r, fc=fc, ec=ec, lw=lw, zorder=z)); ax.text(x, y, s, fontsize=fs, ha="center", va="center", color=tc, zorder=z + 1, fontweight="bold")
class Page:
    def __init__(self, W=420.0, H=297.0, dpi=150):
        self.W, self.H = W, H; self.fig = plt.figure(figsize=(W / 25.4, H / 25.4), dpi=dpi, facecolor="white")
        self.ax = self.fig.add_axes([0, 0, 1, 1]); self.ax.set_xlim(0, W); self.ax.set_ylim(H, 0); self.ax.axis("off")
    def t(self, x, y, s, fs=8, c=INK, ha="left", va="center", bold=False, z=5, **kw): return self.ax.text(x, y, s, fontsize=fs, color=c, ha=ha, va=va, fontweight="bold" if bold else "normal", zorder=z, **kw)
    def line(self, x0, y0, x1, y1, c=INK, lw=0.6, z=3, **kw): self.ax.plot([x0, x1], [y0, y1], color=c, lw=lw, zorder=z, solid_capstyle="butt", **kw)
    def rect(self, x, y, w, h, fc="none", ec="none", lw=0.0, z=2, **kw): self.ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec=ec, lw=lw, zorder=z, **kw))
    def sub(self, x, y, w, h, **kw): return self.fig.add_axes([x / self.W, 1 - (y + h) / self.H, w / self.W, h / self.H], **kw)
    def save(self, path, dpi=170, pdf=None):
        self.fig.savefig(path, dpi=dpi, facecolor="white")
        if pdf: self.fig.savefig(pdf, facecolor="white")
def title_block(pg, label, en, ko, x=16, y=20, sub=None):
    pg.t(x, y, label, fs=11, c=RED); t = pg.t(x, y + 9.5, en, fs=21, bold=True)
    pg.fig.canvas.draw(); wmm = t.get_window_extent(pg.fig.canvas.get_renderer()).width / pg.fig.dpi * 25.4
    pg.line(x + wmm + 3.5, y + 5.5, x + wmm + 3.5, y + 13.5, c="#555", lw=0.8); pg.t(x + wmm + 7, y + 9.8, ko, fs=14, c="#444")
    if sub: pg.t(x, y + 19, sub, fs=8.2, c="#555")
def ctx_draw(ax, ext, fcb="#dcdcd8"):
    x0, y0, x1, y1 = ext; win = box(x0, y0, x1, y1)
    for r in K.CTX_R:
        if r.intersects(win): fill(ax, r, fc="#ffffff", z=0.4)
    pats = []
    for b in K.CTX_B:
        if b["geom"].buffer(2).intersects(U) or not b["geom"].intersects(win): continue
        for p in polys(b["geom"]): pats.append(PathPatch(path_of(p)))
    from matplotlib.collections import PatchCollection
    ax.add_collection(PatchCollection(pats, fc=fcb, ec="none", lw=0, zorder=0.8))
def grid_table(pg, x, y, cols, rows, hdr_h=9.0, row_h=9.5, hdr_fs=6.8, shade_rows=(), line_c="#c8c8c8"):
    xs = [x]
    for _, w, _ in cols: xs.append(xs[-1] + w)
    pg.line(x, y, xs[-1], y, lw=0.9)
    for (title, w, al), x0 in zip(cols, xs[:-1]):
        tx = x0 + (w / 2 if al == "c" else (w - 1.5 if al == "r" else 1.5)); pg.t(tx, y + hdr_h / 2, title, fs=hdr_fs, bold=True, ha={"c": "center", "r": "right", "l": "left"}[al], linespacing=1.15)
    pg.line(x, y + hdr_h, xs[-1], y + hdr_h, lw=0.5); yy = y + hdr_h
    for i, r in enumerate(rows):
        rh = row_h[i] if isinstance(row_h, list) else row_h
        if i in shade_rows: pg.rect(x, yy, xs[-1] - x, rh, fc=GREY, z=1)
        for (title, w, al), x0, cell in zip(cols, xs[:-1], r):
            lines = cell if isinstance(cell, list) else [cell]; n = len(lines)
            for j, ln in enumerate(lines):
                sty = {}
                if isinstance(ln, tuple): ln, sty = ln
                ty = yy + rh / 2 + (j - (n - 1) / 2) * (rh * 0.40 if n > 1 else 0); tx = x0 + (w / 2 if al == "c" else (w - 1.5 if al == "r" else 1.5))
                pg.t(tx, ty, ln, fs=sty.get("fs", 7.0), c=sty.get("c", INK), bold=sty.get("bold", False), ha={"c": "center", "r": "right", "l": "left"}[al])
        yy += rh; pg.line(x, yy, xs[-1], yy, c=line_c, lw=0.35)
    pg.line(x, yy, xs[-1], yy, lw=0.9); return yy
def fm_(v): return format(int(round(v)), ",") + "㎡"
def pc(v, tot): return "%d%%" % round(v / tot * 100)
def lot_pt(d, depth=2.0):
    bl = unary_union([b["geom"] for b in BUILD if b["lot_no"] == d["no"]]).buffer(depth) if any(b["lot_no"] == d["no"] for b in BUILD) else Polygon()
    free = d["geom"].difference(bl); free = max(polys(free), key=lambda g: g.area) if not free.is_empty else d["geom"]
    return polylabel(free, 1.0) if free.area > 60 else d["geom"].representative_point()
PN = {"Park A": "북단 수변공원·삼각 녹지", "Park B": "문화공원(고분 언덕·곡선 띠)", "Park C": "역전광장·근린공원", "Park D": "종축 녹지띠"}
NOTE_TOP = "규제 미적용 개념안 — 사용자 수정 도로·경계(라이노 모형, 1단위 = 1.339 m 환산) 기준. 북측(시청·청년주거·복합문화·청년창업·커뮤니티)은 TIME STRATA로 새로 구성, 나머지는 이전 안의 프로그램·매스 유형을 유지."

# ════ 01 획지구획도 + 획지계획표 ═══════════════════════════════════════════════════════════════
def sheet01():
    pg = Page(); title_block(pg, "Lot Plan : Parcel Layout", "Lot Plan + Lot Schedule", "획지 구획도 + 획지계획표", x=16, y=16, sub=NOTE_TOP + "  계획 경계 %s㎡" % format(round(S["U"]), ","))
    x0, y0, x1, y1 = U.buffer(30).bounds; PX, PY, PW, PH = 10, 42, 108, 250
    ax = pg.sub(PX, PY, PW, PH); ax.axis("off"); ax.set_aspect("equal"); cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; sc = max((x1 - x0) / PW, (y1 - y0) / PH)
    ax.set_xlim(cx - PW * sc / 2, cx + PW * sc / 2); ax.set_ylim(cy - PH * sc / 2, cy + PH * sc / 2); ext = (cx - PW * sc / 2, cy - PH * sc / 2, cx + PW * sc / 2, cy + PH * sc / 2)
    ax.add_patch(Rectangle((ext[0], ext[1]), ext[2] - ext[0], ext[3] - ext[1], fc="#f6f6f4", ec="none", zorder=0)); ctx_draw(ax, ext)
    fill(ax, U, fc="#cfcfcb", z=2)
    for k, r in ROADS.items(): fill(ax, r["g"], fc=("#aebfe0" if r["grp"] == "차량" else "#f0bdb3"), z=2.5)
    for d in PARKS: fill(ax, d["geom"], fc="#c3e3a4", ec="#6aa84f", lw=0.35, z=3)
    for d in LOTS: fill(ax, d["geom"], fc=tint(CATCOL[d["cat"]], 0.62), ec="#555", lw=0.45, z=3)
    for lid, nm, g in COURTS: fill(ax, g, fc="#e1f0cf", z=3.5)
    for lid, nm, g, col in OPEN: fill(ax, g, fc={"#cfe6b4": "#e1f0cf", "#d98a6a": "#e2a58a", "#cfcfcf": "#dddddd"}.get(col, col), z=3.5)
    for r in RAILS: ax.plot(*r.xy, color="#8b887f", lw=0.3, zorder=3.6)
    for b in BUILD: fill(ax, b["geom"], fc=CATCOL[b["cat"]], ec="#3a3a3a", lw=0.3, z=4)
    for b in BUILD:
        if b.get("lift"):
            for q in polys(b["lift"]["geom"]): ax.add_patch(PathPatch(path_of(q), fc="none", ec="#2e7d32", lw=0.35, ls=(0, (2, 1.5)), zorder=5))
    for dk in DECKS:
        xs = [p[0] for p in dk["pts"]]; ys = [p[1] for p in dk["pts"]]; ax.plot(xs, ys, color="#2e7d32", lw=1.6 if dk["kind"] == "main" else 0.9, alpha=0.8, zorder=6, solid_capstyle="butt")
    ax.add_patch(PathPatch(path_of(Polygon(U.exterior)), fc="none", ec="#7a2bd6", lw=1.0, ls=(0, (4, 2)), zorder=6))
    for k, r in ROADS.items():
        c = r["g"].representative_point() if r["g"].area < 2500 else polylabel(max(polys(r["g"]), key=lambda g: g.area), 1.0)
        ax.text(c.x, c.y, "%s %gm" % (r["nm"], r["w"]), fontsize=4.2, ha="center", va="center", color="#333", zorder=8, path_effects=halo(1.4, "#d9d9d4"))
    for d in LOTS: pt = lot_pt(d); num_circle(ax, pt.x, pt.y, str(d["no"]), r=6.5, fs=6.4, z=10)
    for d in PARKS: pt = polylabel(max(polys(d["geom"]), key=lambda g: g.area), 1.0); ax.text(pt.x, pt.y, d["name"], fontsize=5.6, ha="center", va="center", color="#2d5a1b", fontweight="bold", zorder=9, path_effects=halo(1.6, "#c3e3a4"))
    ax.annotate("", xy=(ext[0] + 12 * sc, ext[3] - 6 * sc), xytext=(ext[0] + 12 * sc, ext[3] - 20 * sc), arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.8), zorder=12)
    ax.text(ext[0] + 12 * sc, ext[3] - 4 * sc, "N", fontsize=7, ha="center", va="top", fontweight="bold", zorder=12)
    sb0 = ext[0] + 28 * sc; sby = ext[1] + 8 * sc
    for i in range(2): ax.add_patch(Rectangle((sb0 + i * 50, sby), 50, 5, fc=INK if i == 0 else "white", ec=INK, lw=0.5, zorder=12))
    for dx, s in ((0, "0"), (50, "50"), (100, "100 m")): ax.text(sb0 + dx, sby + 7, s, fontsize=5.5, ha="center", va="bottom", zorder=12)
    pg.t(PX, PY - 2.5, "획지 구획도 (북쪽 위, 1:%s @A3)" % format(int(round(sc * 1000 / 100) * 100), ","), fs=7, c="#555")
    cols = [("획지", 9, "c"), ("획지명 / 시설 구성", 62, "l"), ("용도(계획)", 32, "l"), ("획지면적\n(㎡)", 16, "r"), ("건축면적\n(㎡)", 16, "r"), ("건폐율\n(%)", 11, "r"), ("연면적\n(㎡)", 16, "r"), ("용적률\n(%)", 11, "r"), ("층수 /\n높이", 15, "c"), ("접도(면한 도로)", 38, "l")]
    rows = []; shade = []
    for r in TR:
        fr = " · ".join("%s %g" % (ROADS[k]["nm"].replace("가로", "").replace("축", ""), w) for k, w in r["frontage"][:4])
        if r["parkfront"]: fr += " · " + "/".join(p.replace("Park ", "Pk ") for p in r["parkfront"])
        hh = [("%dF" % r["maxf"], dict(fs=6.6)), ("%.1f m" % r["maxh"], dict(fs=5.8, c=RED if r["maxh"] > 20.0001 else "#666"))]
        rows.append([(str(r["no"]), dict(fs=8, bold=True)), [(r["name"], dict(fs=7.2, bold=True)), (r["short"], dict(fs=5.6, c="#666"))], (r["use_txt"], dict(fs=6.4)), format(round(r["area"]), ","), format(round(r["fp"]), ","),
                     "%.0f" % (r["bcr"] * 100), format(round(r["gfa"]), ","), "%.0f" % (r["far"] * 100), hh, (fr, dict(fs=5.8))])
    ta = sum(r["area"] for r in TR); tf = sum(r["fp"] for r in TR); tg = sum(r["gfa"] for r in TR)
    rows.append([("", {}), ("합계 (획지 %d개)" % len(TR), dict(fs=7.4, bold=True)), "", (format(round(ta), ","), dict(bold=True)), (format(round(tf), ","), dict(bold=True)), ("%.1f" % (tf / ta * 100), dict(bold=True)),
                 (format(round(tg), ","), dict(bold=True)), ("%.1f" % (tg / ta * 100), dict(bold=True)), "", ("건폐율·용적률 = 획지면적(가용지) 기준", dict(fs=5.8, c="#666"))]); shade.append(len(rows) - 1)
    TX = 124; rh = min(10.3, 196.0 / (len(rows) + 1)); yend = grid_table(pg, TX, 44, cols, rows, hdr_h=9.5, row_h=rh, shade_rows=shade)
    for i, r in enumerate(TR): pg.rect(TX + 0.9, 44 + 9.5 + i * rh + rh * 0.2, 1.6, rh * 0.6, fc=CATCOL[r["cat"]], z=4)
    lx, ly = TX, yend + 6; pg.t(lx, ly, "범례", fs=7, bold=True); ex = lx + 11
    for cat in CATORDER[:-1]:
        pg.rect(ex, ly - 2, 5, 4, fc=CATCOL[cat], ec="#555", lw=0.25); pg.t(ex + 6.2, ly, cat, fs=6.2); ex += 6.2 + len(cat) * 2.15 + 5
    pg.rect(ex, ly - 2, 5, 4, fc="#c3e3a4", ec="#6aa84f", lw=0.25); pg.t(ex + 6.2, ly, "공원·녹지", fs=6.2)
    notes = ["· 건폐율·용적률은 획지면적(가용지) 기준. 연면적은 지상층 단순 합산(지하층·주차장 별도 산정 전). 1층을 판매·음식으로 쓰는 매스는 면적표(03)에서 판매·음식 행으로 옮겨 집계.",
             "· 초록 실선 = 공중가로·상층 데크(종축 위 +4.5~16.5 m 경사 데크, 가지 데크, 스카이브리지), 초록 점선 = 들어 올린 지붕(캐노피). 데크 면적은 연면적에 넣지 않았다.",
             "· 높이는 층수 × 층고(주거 3.3 m, 업무 3.8 m, 공공 4.0 m, 문화 4.5 m, 판매 4.2 m, 체육 6.5 m, 주차 3.0 m) — 계획 가정. 높이 20 m를 넘는 매스(청년창업 모서리 6F)는 붉게 표시, 규제 적용 단계에서 낮춘다.",
             "· 청년주거(Plot %d)는 2026.1 결정도에 주거용지가 없으므로 신규 용도 — 용도지역 변경 또는 허용용도 협의 필요 [T1 고시 대조 필요]. 계획 경계는 사용자가 수정한 선(이전 경계 218,478㎡와 거의 같은 선)이며 고시 구역·시 구상 면적과 직접 비교하지 않는다." % [r["no"] for r in TR if "주거" in r["name"]][0]]
    for i, s in enumerate(notes): pg.t(TX, ly + 8 + i * 4.6, s, fs=5.9, c="#444")
    pg.t(412, 291, "01", fs=8, c="#666", ha="right"); pg.save(os.path.join(OUT, "01_획지구획도_획지계획표.png"), pdf=os.path.join(OUT, "01_획지구획도_획지계획표.pdf")); print("saved 01")

# ════ 02 조감도 Site Anchors ═════════════════════════════════════════════════════════════════════
def sheet02():
    META = pickle.load(open(os.path.join(D, "axo_sheet_meta.pkl"), "rb")); cam = K.Cam(META["az"], META["el"], META["W"], META["H"], META["ps"], META["xc"], META["yc"])
    def mm(x, y, z=0.0): px, py = cam.xy(x, y, z); return px * 420.0 / META["W"], py * 297.0 / META["H"]
    pg = Page(); pg.ax.imshow(imread(os.path.join(D, "axo_sheet.png")), extent=[0, 420, 297, 0], aspect="auto", zorder=0, interpolation="bilinear"); pg.ax.set_xlim(0, 420); pg.ax.set_ylim(297, 0)
    pg.rect(0, 0, 420, 42.5, fc="white", ec="none", z=1, alpha=0.72)
    title_block(pg, "Masterplan : Site Anchors", "Site Anchors", "획지별 앵커·용도 구성", x=16, y=14, sub="TIME STRATA — 시간의 층위를 걷는 도시. " + NOTE_TOP)
    pg.t(16, 38.5, "연면적 %s㎡ · 용적률 %d%% · 건폐율 %d%% (획지 %s㎡ 기준) · 공원·녹지 %s㎡(%.1f%%) · 도로 %s㎡(%.1f%%) · 공중가로·상층 데크 연장 %s m" % (
        format(round(F["total"]), ","), round(F["far"] * 100), round(F["coverage"] * 100), format(round(S["lot_total"]), ","), format(round(S["park_total"]), ","), S["park_total"] / S["planned"] * 100,
        format(round(S["road_total"]), ","), S["road_total"] / S["planned"] * 100, format(round(SM["deck_len"]), ",")), fs=7.2, c="#444")
    mk = {}
    for r in TR:
        d = LOTBY[r["no"]]; pt = lot_pt(d); x, y = mm(pt.x, pt.y, 6.0 + r["maxh"] * 0.55)
        if "구경주역" in r["name"]: c15 = unary_union([b["geom"] for b in BUILD if b["lot_no"] == d["no"]]).centroid; x, y = mm(c15.x, c15.y, r["maxh"] + 8.0)
        mk[r["no"]] = (x, y); pg.ax.add_patch(Circle((x, y), 3.0, fc="white", ec=INK, lw=0.7, zorder=8)); pg.t(x, y + 0.1, str(r["no"]), fs=7.4, bold=True, ha="center", z=9)
    pmk = {}
    for d in PARKS:
        pt = polylabel(max(polys(d["geom"]), key=lambda g: g.area), 1.0); x, y = mm(pt.x, pt.y, 8.0); lab = d["name"].replace("Park ", ""); pmk[d["name"]] = (x, y)
        pg.ax.add_patch(Circle((x, y), 3.0, fc="#2e7d32", ec="white", lw=0.8, zorder=8)); pg.t(x, y + 0.1, lab, fs=7.4, bold=True, c="white", ha="center", z=9)
    no = {r["name"]: r["no"] for r in TR}
    dkx, dky = mm(111.5 * P["SC"], 450 * P["SC"], 10.5)
    CALL = [(no["시청·의회 캠퍼스"], "시청 · Plot %d" % no["시청·의회 캠퍼스"], "사용자 ∩자 형태 그대로 5층 본청(지상 약 %s㎡). 개구부는 남향 시민마당, 북쪽 지붕은 들어 올림." % format(round(SM["city_gfa"], -2), ",")),
            (no["청년주거(남향 판상)"], "청년주거 · Plot %d" % no["청년주거(남향 판상)"], "남향 평행 4동 6F. 1층 생활상가, 5층 스카이브리지, 약 %d~%d세대(전용 70%%, 33.6~38.4㎡)." % (round(SM["units_Q"], -1), round(SM["units_P"], -1))),
            ("T", "공중가로 T · 종축 상층 데크", "종축 위 +4.5~16.5 m로 완만히 오르는 1:16 데크. 가지 데크가 문화·시청·주거로 이어진다."),
            (no["복합문화·영화관"], "복합문화 · Plot %d" % no["복합문화·영화관"], "2~4층 분동과 들어 올린 지붕. 쐐기 녹지(Park B) 위 데크와 연결."),
            (no["구경주역·근대역사관"], "구 역사 이전 · Plot %d" % no["구경주역·근대역사관"], "기존 건물 형상(1,404㎡·2층)을 그대로 이전. 앞 광장이 철도 방향을 잇는다."),
            (no["성동시장 클러스터"], "성동시장 · Plot %d" % no["성동시장 클러스터"], "2층 장옥 바(체험판매 포함) + 삼층석탑 마당. 위 중앙 보행가로와 맞닿는다.")]
    BW = 41.0; YT = 264.0; pg.rect(0, YT - 3.2, 420, 29.0, fc="white", ec="none", z=5, alpha=0.66)
    def pos(k): return (dkx, dky) if k == "T" else mk[k]
    order = sorted(range(len(CALL)), key=lambda i: pos(CALL[i][0])[0]); XS = {}
    for i in order: XS[i] = min(max(pos(CALL[i][0])[0], 12.0), 420 - BW - 6)
    for a, b in zip(order, order[1:]): XS[b] = max(XS[b], XS[a] + BW + 1.5)
    lim = 420 - BW - 6
    for a, b in zip(order[::-1], order[::-1][1:]):
        if XS[a] > lim: XS[a] = lim
        XS[b] = min(XS[b], XS[a] - BW - 1.5)
    for ci, (key, ttl, desc) in enumerate(CALL):
        x, y = pos(key); xs = XS[ci]
        pg.line(x, y + 3.0, x, YT, c="#333", lw=0.6, z=6); pg.line(x, YT, xs + 2.6, YT, c="#333", lw=0.6, z=6); pg.line(xs + 2.6, YT, xs + 2.6, YT + 2.4, c="#333", lw=0.6, z=6)
        pg.ax.add_patch(Circle((x, YT), 0.55, fc="#333", ec="none", zorder=7)); pg.t(xs + 4.0, YT + 3.6, ttl, fs=7.4, bold=True, path_effects=halo(1.8, "white"))
        for j, ln in enumerate(textwrap.wrap(desc, 17)[:4]): pg.t(xs + 4.0, YT + 7.9 + j * 3.5, ln, fs=6.3, c="#333", path_effects=halo(1.6, "white"))
    px0, py0 = 12, 44.5; pg.rect(px0, py0, 282, 29.5, fc="white", ec="none", z=6, alpha=0.80)
    ent = [(str(r["no"]), r["name"], "%s㎡ · %dF" % (format(round(r["area"]), ","), r["maxf"]), CATCOL[r["cat"]]) for r in TR]
    ent += [(d["name"].replace("Park ", ""), PN[d["name"]], "%s㎡" % format(round(d["area"]), ","), "#2e7d32") for d in PARKS]
    for i, (n, nm, ar, col) in enumerate(ent):
        c, rr = divmod(i, 6); x = px0 + 3 + c * 70; y = py0 + 3.5 + rr * 4.4
        pg.ax.add_patch(Circle((x + 2.0, y), 1.75, fc=col if n.isalpha() else "white", ec=INK if not n.isalpha() else "white", lw=0.45, zorder=8)); pg.t(x + 2.0, y + 0.1, n, fs=5.6, bold=True, ha="center", c="white" if n.isalpha() else INK, z=9)
        if not n.isalpha(): pg.rect(x + 4.6, y - 1.6, 1.3, 3.2, fc=col, z=8)
        pg.t(x + 7.0, y, nm, fs=5.8, z=9); pg.t(x + 69 - 2.5, y, ar, fs=5.4, c="#555", ha="right", z=9)
    ly = 292.0; pg.rect(0, ly - 4.2, 420, 8.4, fc="white", ec="none", z=6, alpha=0.86); pg.t(16, ly, "범례", fs=7, bold=True, z=9); ex = 28
    for cat in CATORDER[:-1]:
        pg.rect(ex, ly - 2, 5, 4, fc=CATCOL[cat], ec="#555", lw=0.25, z=9); pg.t(ex + 6.5, ly, cat, fs=6.5, z=9); ex += 6.5 + len(cat) * 2.3 + 6
    pg.rect(ex, ly - 2, 5, 4, fc="#9fd36b", ec="#555", lw=0.25, z=9); pg.t(ex + 6.5, ly, "옥상녹화·공원", fs=6.5, z=9); ex += 6.5 + 13 * 2.3 + 6
    pg.rect(ex, ly - 2, 5, 4, fc="#3fae4a", ec="#555", lw=0.25, z=9); pg.t(ex + 6.5, ly, "공중가로·상층 데크", fs=6.5, z=9)
    pg.t(404, ly, "02", fs=8, c="#666", ha="right", z=9); pg.save(os.path.join(OUT, "02_조감도_SiteAnchors.png"), pdf=os.path.join(OUT, "02_조감도_SiteAnchors.pdf")); print("saved 02")

# ════ 03 면적표 ══════════════════════════════════════════════════════════════════════════════════
def pdf_table(pg, x, y, widths, rows, row_h=7.0, hdr=None, fs_en=8.0, fs_ko=7.0, fs_val=8.0):
    xs = [x]
    for w in widths: xs.append(xs[-1] + w)
    gap = 0.5
    if hdr:
        pg.line(x, y, xs[-1], y, c="#777", lw=0.5); t = pg.t(x + 1.5, y + 5.2, hdr[0], fs=10, bold=True)
        pg.fig.canvas.draw(); wmm = t.get_window_extent(pg.fig.canvas.get_renderer()).width / pg.fig.dpi * 25.4; pg.t(x + 1.5 + wmm + 2.2, y + 5.4, hdr[1], fs=8, c="#444"); y += 9.5
    yy = y
    for r in rows:
        sub = r.get("sub", False); span = r.get("span", False); cells = [(xs[0], xs[1]), (xs[1], xs[2]), (xs[2], xs[3]), (xs[3], xs[4])]
        if span: cells = [cells[0], cells[1], (xs[2], xs[4])]
        for a, b in cells:
            if sub: pg.rect(a + gap / 2, yy + gap / 2, b - a - gap, row_h - gap, fc="#ececec", z=1)
            else: pg.line(a + gap, yy + row_h, b - gap, yy + row_h, c="#b5b5b5", lw=0.4)
        pg.t(xs[0] + 1.6, yy + row_h / 2, r["en"], fs=fs_en, linespacing=1.15); pg.t(xs[1] + 1.6, yy + row_h / 2, r["ko"], fs=fs_ko, c="#444", linespacing=1.15)
        if span: pg.t(xs[4] - 1.8, yy + row_h / 2, r["val"], fs=fs_val, ha="right")
        else:
            pg.t(xs[3] - 1.8, yy + row_h / 2, r["val"], fs=fs_val, ha="right")
            if r.get("pct"): pg.t(xs[4] - 1.8, yy + row_h / 2, r["pct"], fs=fs_val, ha="right")
        yy += row_h
    return yy
def sheet03():
    pg = Page(); IMX = 283.0; img = imread(os.path.join(D, "axo_strip.png")); pg.ax.imshow(img, extent=[IMX, 420, 297, 0], aspect="auto", zorder=0, interpolation="bilinear"); pg.ax.set_xlim(0, 420); pg.ax.set_ylim(297, 0)
    title_block(pg, "Overview : Overall Siteplan", "Summary + Site Plan", "개요 + 전체배치도", x=16, y=14, sub="규제 미적용 개념안 — 고도제한·용도지역·보존지역 허용기준 미반영. 면적은 도면에서 직접 산정(㎡)하며 합계가 계획 경계에 닫힘")
    RH = 6.0; W1 = [43, 36, 33, 12]
    rows1 = [dict(en="Station Site (Announced)", ko="폐역 부지(공고 면적)†", val=fm_(79438), sub=True), dict(en="Planning Boundary", ko="계획 경계(사용자 수정 경계, 환산)", val=fm_(S["U"]), sub=True),
             dict(en="Park A", ko="공원 A · 북단 수변·삼각 녹지", val=fm_(S["park_A"])), dict(en="Park B", ko="공원 B · 문화공원(언덕·곡선 띠)", val=fm_(S["park_B"])),
             dict(en="Park C", ko="공원 C · 역전광장·근린공원", val=fm_(S["park_C"])), dict(en="Park D", ko="공원 D · 종축 녹지띠", val=fm_(S["park_D"])), dict(en="Water Area", ko="수공간(해당 없음)", val="-"),
             dict(en="Subtotal of Park", ko="공원면적 소계", val=fm_(S["park_total"]), pct=pc(S["park_total"], S["planned"]), sub=True),
             dict(en="Vehicle Road", ko="차량도로(보차공존 포함)", val=fm_(S["road_veh"])), dict(en="Pedestrian Road", ko="보행자전용·보행골목(종축·사선 등)", val=fm_(S["road_ped"])),
             dict(en="E-W Central Promenade", ko="동서 중앙 보행가로(45 m)", val=fm_(S["plaza"])), dict(en="Subtotal of Road", ko="도로면적 소계", val=fm_(S["road_total"]), pct=pc(S["road_total"], S["planned"]), sub=True)]
    for no_, a in S["lots"]: rows1.append(dict(en="Plot %d" % no_, ko="획지 %d" % no_, val=fm_(a)))
    rows1 += [dict(en="Subtotal of Usable Land", ko="획지면적 소계", val=fm_(S["lot_total"]), pct=pc(S["lot_total"], S["planned"]), sub=True), dict(en="Planned Site Area", ko="계획부지 면적합계", val=fm_(S["planned"]), sub=True)]
    y1 = pdf_table(pg, 16, 42, W1, rows1, row_h=RH, hdr=("Site Area", "대상지 면적"))
    W2 = [42, 34, 29, 12]; tot = F["total"]; rows2 = []
    for k, e, kr, v in F["rows"]: rows2.append(dict(en=e, ko=kr, val=fm_(v) if v > 0 else "-", pct=("%d%%" % round(v / tot * 100)) if v > 0 else "0%"))
    rows2 += [dict(en="Total GFA", ko="연면적 합계", val=fm_(tot), sub=True, span=True), dict(en="FAR (Usable Land)", ko="용적률(가용부지기준)", val="%d%%" % round(F["far"] * 100), sub=True, span=True),
              dict(en="Coverage (Usable Land)", ko="건폐율(가용부지기준)", val="%d%%" % round(F["coverage"] * 100), sub=True, span=True),
              dict(en="Sky Decks (Aerial Streets)", ko="공중가로·상층 데크(연장·면적, 연면적 제외)", val="%s m · %s" % (format(round(SM["deck_len"]), ","), fm_(SM["deck_area"])), span=True),
              dict(en="Green Roofs & Decks", ko="옥상 녹지(주요 매스 지붕)", val=fm_(SM["roofg_area"]), span=True)]
    y2 = pdf_table(pg, 150, 42, W2, rows2, row_h=RH, hdr=("Facility Area", "시설별 면적"))
    pg.t(151.5, y2 + 4.6, "참고 · 주차전용건축물 제외 연면적 %s (용적률 %d%%)" % (fm_(F["total_excl_parking"]), round(F["far_excl_parking"] * 100)), fs=6.6, c="#555")
    pg.t(151.5, y2 + 9.4, "참고 · 시청·의회 지상 %s · 청년주거 주거층 %s → 약 %d~%d세대(전용 70%%·33.6~38.4㎡, 36㎡ 기준 %d세대)" % (fm_(SM["city_gfa"]), fm_(SM["housing_gfa"]), round(SM["units_Q"]), round(SM["units_P"]), round(SM["units36"])), fs=6.3, c="#555")
    pg.t(151.5, y2 + 14.0, "참고 · 주차전용건축물 %s → 약 %d면(32㎡/대 가정)" % (fm_(SM["parking_gfa"]), round(SM["park_spaces"])), fs=6.3, c="#555")
    KX, KY, KW, KH = 150, 186, 118, 74; rot = lambda g: affinity.affine_transform(g, [0, 1, -1, 0, 0, 0])
    ax = pg.sub(KX, KY, KW, KH); ax.axis("off"); ax.set_aspect("equal"); Ur = rot(U); bx0, by0, bx1, by1 = Ur.bounds
    sc = max((bx1 - bx0) / (KW - 4), (by1 - by0) / (KH - 4)); cx, cy = (bx0 + bx1) / 2, (by0 + by1) / 2
    ax.set_xlim(cx - KW * sc / 2, cx + KW * sc / 2); ax.set_ylim(cy - KH * sc / 2, cy + KH * sc / 2); fill(ax, Ur, fc="#a9a9a9", z=1)
    for r in ROADS.values(): fill(ax, rot(r["g"]), fc="#a9a9a9", z=1.5)
    for d in LOTS: fill(ax, rot(d["geom"]), fc="#ececec", ec="white", lw=0.3, z=2)
    for d in PARKS: fill(ax, rot(d["geom"]), fc="#8cc63f", ec="white", lw=0.3, z=2)
    for d in LOTS: p = rot(d["geom"]); pt = polylabel(max(polys(p), key=lambda g: g.area), 1.0); ax.text(pt.x, pt.y, str(d["no"]), fontsize=6.4, fontweight="bold", ha="center", va="center", zorder=5)
    for d in PARKS: p = rot(d["geom"]); pt = polylabel(max(polys(p), key=lambda g: g.area), 1.0); ax.text(pt.x, pt.y, d["name"], fontsize=5.4, fontweight="bold", ha="center", va="center", zorder=5, color="#1d3b0f")
    pg.t(KX + KW + 1, KY + KH - 3, "Keymap", fs=8.5, bold=True, ha="right", va="bottom")
    pg.ax.annotate("", xy=(KX + KW - 4, KY + 4), xytext=(KX + KW - 18, KY + 4), arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.8)); pg.t(KX + KW - 2, KY + 4, "N", fs=7, bold=True)
    fy = y1 + 5
    foot = ["† 경주시 공개 구상(2026.02) 기준 면적 — 언론 경유 [T4, 원문 미확인]. 계획 경계는 사용자가 수정한 선(이전 경계 218,478㎡와 거의 같은 선, 고시 구역·시 구상 면적과 직접 비교하지 않는다).",
            "· 연면적 = 지상층 건축면적 × 층수의 단순 합. 1층을 판매·음식으로 쓰는 매스는 해당 1층만 Retail / F&B 행에 집계(총합 불변). 용적률·건폐율은 획지면적(가용지) 기준.",
            "· 숙박(Hotel)은 스케치에 없어 0 — 구상 프로그램의 'STAY'는 미반영(결정 필요). 공중가로·데크는 지상 연면적에 넣지 않았다(건축법상 처리 별도 검토).",
            "· 공원면적 비율은 %d%% (이전 안 15.6%%). 플랫폼 광장(보행 우선, 포장)은 도로로 집계." % round(S["park_total"] / S["planned"] * 100)]
    for i, s in enumerate(foot): pg.t(16, fy + i * 4.2, s, fs=5.8, c="#555")
    meta = pickle.load(open(os.path.join(D, "axo_strip_meta.pkl"), "rb")); cam = K.Cam(meta["az"], meta["el"], meta["W"], meta["H"], meta["ps"], meta["xc"], meta["yc"])
    def mm_of(px, py): return IMX + px * (420 - IMX) / meta["W"], py * 297.0 / meta["H"]
    for r in TR:
        d = LOTBY[r["no"]]; pt = lot_pt(d); xm, ym = mm_of(*cam.xy(pt.x, pt.y, r["maxh"] * 0.6 + 1.0))
        pg.ax.add_patch(Circle((xm, ym), 2.6, fc="white", ec=INK, lw=0.6, zorder=8)); pg.t(xm, ym + 0.1, str(r["no"]), fs=6.2, bold=True, ha="center", z=9)
    for d in PARKS:
        pt = polylabel(max(polys(d["geom"]), key=lambda g: g.area), 1.0); xm, ym = mm_of(*cam.xy(pt.x, pt.y, 1.0)); lab = d["name"].replace("Park ", "")
        pg.ax.add_patch(Circle((xm, ym), 2.6, fc="#2e7d32", ec="white", lw=0.6, zorder=8)); pg.t(xm, ym + 0.1, lab, fs=6.2, bold=True, c="white", ha="center", z=9)
    lgx, lgy = IMX + 6, 262; pg.rect(lgx - 3, lgy - 5.5, 131, 38, fc="white", ec="none", z=6, alpha=0.78)
    for i, cat in enumerate(CATORDER[:-1]):
        cx0 = lgx + (i % 2) * 64; cy0 = lgy + (i // 2) * 6.0; pg.rect(cx0, cy0 - 2, 5, 4, fc=CATCOL[cat], ec="#555", lw=0.25, z=7); pg.t(cx0 + 6.5, cy0, cat, fs=6.4, z=7); pg.t(cx0 + 6.5 + len(cat) * 2.25 + 1, cy0, CATEN[cat], fs=4.8, c="#666", z=7)
    pg.rect(lgx + 64, lgy + 24, 5, 4, fc="#3fae4a", ec="#555", lw=0.25, z=7); pg.t(lgx + 70.5, lgy + 26, "공중가로·상층 데크", fs=6.4, z=7)
    pg.ax.annotate("", xy=(412, 24), xytext=(412, 38), arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.0), zorder=7); pg.t(412, 21, "N", fs=8, bold=True, ha="center", z=7)
    pg.t(IMX - 6, 291, "03", fs=8, c="#666", ha="right"); pg.save(os.path.join(OUT, "03_면적표.png"), pdf=os.path.join(OUT, "03_면적표.pdf")); print("saved 03")

# ════ 04 도로계획도 + 도로계획표 ═════════════════════════════════════════════════════════════════
GCOL = {"차량": "#5d7fb0", "보행": "#d1495b", "PZ": "#e58f65"}
SEGCOL = {"차도": "#707070", "식재": "#9ccc65", "보도": "#e6dcc3"}
def segcol(n):
    if "차도" in n: return SEGCOL["차도"]
    if "식재" in n and "보행" not in n and "보도" not in n: return SEGCOL["식재"]
    if "식재" in n: return "#c8d9a0"
    return SEGCOL["보도"]
def sheet04():
    pg = Page(); title_block(pg, "Road Plan : Street Character", "Road Plan + Road Schedule", "도로계획도 + 도로계획표", x=16, y=16,
                             sub="도로 형상은 사용자가 라이노에서 수정한 서피스(파랑 = 차량 주도로, 빨강 = 보행 우선). 폭원·단면은 계획값·계획 가정. 도로 규모별 구분(중로·소로 N류)은 경계값 원문 확인 후 부여 [T1, 원문 미확인].")
    x0, y0, x1, y1 = U.buffer(30).bounds; PX, PY, PW, PH = 10, 42, 108, 250
    ax = pg.sub(PX, PY, PW, PH); ax.axis("off"); ax.set_aspect("equal"); cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; sc = max((x1 - x0) / PW, (y1 - y0) / PH)
    ax.set_xlim(cx - PW * sc / 2, cx + PW * sc / 2); ax.set_ylim(cy - PH * sc / 2, cy + PH * sc / 2); ext = (cx - PW * sc / 2, cy - PH * sc / 2, cx + PW * sc / 2, cy + PH * sc / 2)
    ax.add_patch(Rectangle((ext[0], ext[1]), ext[2] - ext[0], ext[3] - ext[1], fc="#f6f6f4", ec="none", zorder=0)); ctx_draw(ax, ext, "#e3e3df"); fill(ax, U, fc="#f1f1ee", z=2)
    for d in PARKS: fill(ax, d["geom"], fc="#d9ecc3", ec="none", z=3)
    for d in LOTS: fill(ax, d["geom"], fc="#ffffff", ec="#c9c9c9", lw=0.3, z=3)
    for b in BUILD: fill(ax, b["geom"], fc="#dcdcd8", ec="none", z=3.5)
    for r in RR:
        rd = ROADS[r["key"]]; fill(ax, rd["g"], fc=(GCOL["PZ"] if r["key"] == "PZ" else GCOL[r["group"]]), ec="white", lw=0.25, z=5)
    for dk in DECKS:
        xs = [p[0] for p in dk["pts"]]; ys = [p[1] for p in dk["pts"]]; ax.plot(xs, ys, color="#2e7d32", lw=1.4 if dk["kind"] == "main" else 0.8, alpha=0.9, zorder=6, ls=(0, (3, 1.5)))
    ax.add_patch(PathPatch(path_of(Polygon(U.exterior)), fc="none", ec="#7a2bd6", lw=0.9, ls=(0, (4, 2)), zorder=7))
    for r in RR:
        rd = ROADS[r["key"]]; c = polylabel(max(polys(rd["g"]), key=lambda g: g.area), 1.0)
        ax.text(c.x, c.y, "%s %gm" % (r["name"], r["w"]), fontsize=4.8, ha="center", va="center", color="white", fontweight="bold", zorder=9, path_effects=halo(1.0, "#555555"))
    for d in LOTS: pt = d["geom"].representative_point(); ax.text(pt.x, pt.y, str(d["no"]), fontsize=5.2, color="#8a8a8a", ha="center", va="center", zorder=6)
    ax.annotate("", xy=(ext[0] + 12 * sc, ext[3] - 6 * sc), xytext=(ext[0] + 12 * sc, ext[3] - 20 * sc), arrowprops=dict(arrowstyle="-|>", color=INK, lw=0.8), zorder=12)
    ax.text(ext[0] + 12 * sc, ext[3] - 4 * sc, "N", fontsize=7, ha="center", va="top", fontweight="bold", zorder=12)
    sb0 = ext[0] + 28 * sc; sby = ext[1] + 8 * sc
    for i in range(2): ax.add_patch(Rectangle((sb0 + i * 50, sby), 50, 5, fc=INK if i == 0 else "white", ec=INK, lw=0.5, zorder=12))
    for dx, s in ((0, "0"), (50, "50"), (100, "100 m")): ax.text(sb0 + dx, sby + 7, s, fontsize=5.5, ha="center", va="bottom", zorder=12)
    pg.t(PX, PY - 2.5, "도로계획도 (북쪽 위, 1:%s @A3)" % format(int(round(sc * 1000 / 100) * 100), ","), fs=7, c="#555")
    cols = [("", 3.5, "c"), ("도로", 17, "l"), ("도로 성격", 31, "l"), ("폭원\n(m)", 9, "r"), ("연장\n(m)", 9, "r"), ("면적\n(㎡)", 12, "r"), ("통행 방식", 31, "l"), ("단면 구성 (m, 축척 약 2.4 mm/m)", 44, "l"), ("역할 · 접속", 100, "l")]
    rows = []; shade = []
    for r in RR:
        role = textwrap.wrap(r["role"], 46)[:2]; anc = textwrap.wrap(r["anchor"], 52)[:1]
        cell = [(role[0], dict(fs=5.8))] + ([(role[1], dict(fs=5.8))] if len(role) > 1 else []) + ([(anc[0], dict(fs=5.2, c="#777"))] if anc else [])
        rows.append(["", (r["name"], dict(fs=7.0, bold=True)), (r["kind"], dict(fs=6.2)), "%g" % r["w"], format(round(r["L"]), ","), format(round(r["area_excl"]), ","), [(s, dict(fs=5.9)) for s in textwrap.wrap(r["mode"], 17)[:2]], "", cell])
    tg = {g_: sum(r["area_excl"] for r in RR if r["group"] == g_) for g_ in ("차량", "보행")}
    for lab, val in (("차량 도로 소계 (A·B·C·D)", tg["차량"]), ("보행 우선 소계 (S·중앙 보행가로·쐐기 광장·R6·R8~R10)", tg["보행"]), ("도로 합계", S["road_total"])):
        rows.append(["", (lab, dict(fs=6.8, bold=True)), "", "", "", (format(round(val), ","), dict(bold=True)), "", "", ("면적표 Vehicle %s㎡ + Pedestrian %s㎡ + Promenade %s㎡ = %s㎡" % (format(round(S["road_veh"]), ","), format(round(S["road_ped"]), ","), format(round(S["plaza"]), ","), format(round(S["road_total"]), ",")) if lab == "도로 합계" else "", dict(fs=5.8, c="#555"))]); shade.append(len(rows) - 1)
    TX = 124; RH = 11.2; HH = 9.5; TY = 44; yend = grid_table(pg, TX, TY, cols, rows, hdr_h=HH, row_h=[RH] * len(RR) + [6.4] * (len(rows) - len(RR)), shade_rows=shade)
    xs = [TX]
    for _, w, _ in cols: xs.append(xs[-1] + w)
    for i, r in enumerate(RR):
        yy = TY + HH + i * RH; pg.rect(TX + 0.8, yy + 1.6, 1.9, RH - 3.2, fc=(GCOL["PZ"] if r["key"] == "PZ" else GCOL[r["group"]]), z=4); k = 2.4 if r["w"] < 30 else 0.9; sx = xs[7] + 1.5; sy = yy + RH / 2 - 2.4
        for name, wd in r["cross_list"]:
            pg.rect(sx, sy, wd * k, 4.8, fc=segcol(name), ec="white", lw=0.3, z=4)
            if wd * k >= 5: pg.t(sx + wd * k / 2, sy + 2.45, "%g" % wd, fs=4.6, c="#222" if segcol(name) != "#707070" else "white", ha="center", z=5)
            sx += wd * k
        pg.t(xs[7] + 1.5, sy + 7.6, " · ".join(n.replace("(양방 2차로)", "") for n, _ in r["cross_list"][:5]), fs=4.3, c="#666")
    ly = yend + 6; pg.t(TX, ly, "범례", fs=7, bold=True); ex = TX + 11
    for c, s in ((GCOL["차량"], "차량·보차공존 가로(파랑)"), (GCOL["보행"], "보행 우선(빨강)"), (GCOL["PZ"], "플랫폼 광장"), ("#d9ecc3", "녹지")):
        pg.rect(ex, ly - 2, 5, 4, fc=c, ec="#555", lw=0.25); pg.t(ex + 6.5, ly, s, fs=6.2); ex += 6.5 + len(s) * 2.2 + 5
    pg.line(ex, ly, ex + 8, ly, c="#2e7d32", lw=1.4, ls=(0, (3, 1.5))); pg.t(ex + 10, ly, "공중가로·상층 데크(상부)", fs=6.2)
    notes = ["· 사용자 수정 도로: 파랑 = 차량 주도로(A 동서·B 남북·C 북측·D 북동 사선), 빨강 = 보행 우선(S 종축·중앙 보행가로·쐐기 광장·R6 사선·북단 R8·동측 R9·R10).",
             "· 종축 S의 상부에 공중가로 T(+4.5~16.5 m, 1:16)가 겹친다. 지상은 보행 우선 가로, 상부는 무장애 경사 데크이며 가지 데크가 문화·시청·주거 동으로 이어진다.",
             "· 쐐기 모양 빨간 서피스는 사용자 도면 그대로 보행 우선 광장(수목 식재 포장)으로 두고 도로로 집계했다. 단면 구성(차도·보도·식재 폭)은 이 안의 계획 가정이다. 기존 가로와의 접속은 좌표 정합 후 확정한다."]
    for i, s in enumerate(notes): pg.t(TX, ly + 8 + i * 4.4, s, fs=5.9, c="#444")
    pg.t(412, 291, "04", fs=8, c="#666", ha="right"); pg.save(os.path.join(OUT, "04_도로계획도_도로계획표.png"), pdf=os.path.join(OUT, "04_도로계획도_도로계획표.pdf")); print("saved 04")

if __name__ == "__main__":
    for f in (sheet01, sheet02, sheet03, sheet04): f()
