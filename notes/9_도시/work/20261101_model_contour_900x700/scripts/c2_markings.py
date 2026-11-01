# 색지 각인용 노면표시(중앙선·차선·정지선·횡단보도·진행방향 화살표·교통섬 빗금)
#  도로망·유형 : 국토지리정보원 1:5000 수치지형도 2025(도엽 35901069) 도로중심선(차로수·도로폭·분리대·일방통행)
#                도엽 밖(북쪽 띠)은 표준노드링크(방향별 차로수)
#  실재 확인   : 2025 항공사진 모자이크(c1_mosaic.py) — 횡단보도(줄무늬 주기)·중앙선(황색) 검출
#  모양·치수   : 노면표시 실무 기준값(가정, 원문 대조 필요) — 중앙선 15 cm, 차선 3 m/5 m, 정지선 45 cm, 횡단보도 줄무늬 50 cm
# 출력: data/markings.json, qa_*.jpg
import json
import math
from collections import Counter, defaultdict

import cv2
import numpy as np
import shapefile
from scipy.spatial import cKDTree
from shapely.geometry import LineString, MultiLineString, Point, Polygon, box
from shapely.ops import linemerge, substring, unary_union
from shapely.prepared import prep

from c0_common import ARC, D, MM, NG, W, Mosaic, imwrite, m_from_5187, m_from_ll

# ------------------------------------------------------------------ 기준값(실제 m)
CL_W, CL_GAP = 0.15, 0.12          # 중앙선 선폭·복선 간격(선 중심 간 0.27 m)
DASH, GAP = 3.0, 5.0               # 차선 점선(도시부)
SOLID_NEAR_JCT = 20.0              # 교차로 앞 진로변경제한(실선) 구간
STOP_W, STOP_GAP = 0.45, 3.0       # 정지선 폭, 횡단보도와의 간격
STRIPE_W = 0.5                     # 횡단보도 줄무늬 폭
ARROW_L, ARROW_BACK = 5.0, 4.0     # 화살표 길이, 정지선에서 떨어진 거리
MAJOR_W = 5.5                      # 이 폭 이상이면 '주요 도로'(교차로 판정·표시 대상)
STEP = 0.5                         # 횡단보도 탐색 간격(m)

m = lambda v: v * MM              # 실제 m → 모델 mm
_np = lambda o: o.item() if hasattr(o, "item") else str(o)

p2 = json.load(open(D / "plan2d.json", encoding="utf-8"))
src = json.load(open(D / "frame_src.json", encoding="utf-8"))
F = Polygon(p2["frame"]["ext"])
S = Polygon(p2["site"]["ext"])
roads = [Polygon([l[1] for l in it["loops"] if l[0]][0], [l[1] for l in it["loops"] if not l[0]])
         for it in src["items"] if it["cat"] == "도로"]
bridge_plans = [Polygon(p["ext"], p["holes"]) for b in p2["bridge_models"] for p in b["plan"]]
ROAD = unary_union([g.buffer(0) for g in roads] + bridge_plans).intersection(F).difference(S)
PRINT = unary_union([Polygon(p["ext"], p["holes"]) for p in p2["land"] + p2["sidewalk"]])
ROAD_IN = prep(ROAD.buffer(-m(0.25)))
print("road area %.0f mm2" % ROAD.area)

# ------------------------------------------------------------------ 영상
mos = Mosaic()
rgb = mos.rgb
gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype(np.float32)
rr, gg, bb = [rgb[..., i].astype(np.int16) for i in range(3)]
yel = np.clip(np.minimum(rr, gg) - bb, 0, 255).astype(np.float32)
yel[np.maximum(rr, gg) < 110] = 0
del rr, gg, bb
road_mask = np.zeros((mos.h, mos.w), np.uint8)


def fill(poly, val):
    for p in getattr(poly, "geoms", [poly]):
        cv2.fillPoly(road_mask, [np.round(mos.to_px(np.array(p.exterior.coords))).astype(np.int32)], val)
        for h in p.interiors:
            cv2.fillPoly(road_mask, [np.round(mos.to_px(np.array(h.coords))).astype(np.int32)], 0)


fill(ROAD, 255)
valid = (mos.valid.astype(np.uint8) * 255)


def sample(img, xy, interp=cv2.INTER_LINEAR):
    """모델 좌표 배열(...,2) 위치의 화소값"""
    xy = np.asarray(xy, np.float64)
    shp = xy.shape[:-1]
    uv = mos.to_px(xy.reshape(-1, 2)).astype(np.float32)
    out = np.empty(len(uv), np.float32)
    CH = 30000
    for i in range(0, len(uv), CH):
        mu = uv[i:i + CH, 0].reshape(1, -1); mv = uv[i:i + CH, 1].reshape(1, -1)
        out[i:i + CH] = cv2.remap(img, mu, mv, interp, borderMode=cv2.BORDER_CONSTANT, borderValue=0).ravel()
    return out.reshape(shp)


# ------------------------------------------------------------------ 도로 링크
def lines_of(g):
    if g.is_empty:
        return []
    if g.geom_type == "LineString":
        return [g]
    return [x for h in getattr(g, "geoms", []) for x in lines_of(h)]


sheet = Polygon(m_from_5187(np.array(shapefile.Reader(str(NG / "N3A_H0010000"), encoding="euc_kr").shape(0).points)))
links = []
r = shapefile.Reader(str(NG / "N3L_A0020000"), encoding="euc_kr")
for sh, rec in zip(r.shapes(), r.records()):
    g = LineString(m_from_5187(np.array(sh.points)))
    if not g.intersects(F):
        continue
    lanes = int(rec[7] or 1)
    links.append({"g": g, "src": "ngii", "lanes": lanes, "width_attr": float(rec[8] or 0),
                  "oneway": rec[9] == "일방통행", "median": rec[6] == "유", "kind": rec[2], "name": rec[1]})
# 도엽 밖: 표준노드링크(방향별 링크 → 양방향 묶기)
nl = json.load(open(ARC / "nodelink_gj_4326.geojson", encoding="utf-8"))
nlk = []
for f in nl["features"]:
    g = LineString(m_from_ll(np.array(f["geometry"]["coordinates"])))
    if g.intersects(F) and g.difference(sheet.buffer(m(2))).length > 0.3 * g.length:
        nlk.append((g, int(f["properties"].get("LANES") or 1), f["properties"].get("ROAD_NAME")))
used = set()
for i, (g, ln, nm) in enumerate(nlk):
    if i in used:
        continue
    pair = None
    for j in range(i + 1, len(nlk)):
        if j in used:
            continue
        h = nlk[j][0]
        if g.hausdorff_distance(h) < m(4.0):
            pair = j; break
    if pair is not None:
        used.add(pair)
        links.append({"g": g, "src": "nodelink", "lanes": ln + nlk[pair][1], "width_attr": 0, "oneway": False,
                      "median": g.hausdorff_distance(nlk[pair][0]) > m(1.5), "kind": "", "name": nm})
    else:
        links.append({"g": g, "src": "nodelink", "lanes": ln, "width_attr": 0, "oneway": True,
                      "median": False, "kind": "", "name": nm})
    used.add(i)
# 프레임·사이트 밖, 도로 밖 구간 제거
kept = []
for L in links:
    for g in lines_of(L["g"].intersection(F).difference(S)):
        if g.length < m(3):
            continue
        inside = g.intersection(ROAD).length / g.length
        if inside < 0.6:
            continue
        L2 = dict(L); L2["g"] = g; kept.append(L2)
links = kept
print("links", len(links), Counter(L["src"] for L in links))

# ------------------------------------------------------------------ 폭 실측(도로 마스크 광선)
def measure_halfwidth(g):
    hl, hr = [], []
    n = max(3, int(g.length / m(4)))
    for t in np.linspace(0.05, 0.95, n):
        p = g.interpolate(t, normalized=True)
        a, b = g.interpolate(max(t - 0.01, 0), normalized=True), g.interpolate(min(t + 0.01, 1), normalized=True)
        v = np.array([b.x - a.x, b.y - a.y]); nv = np.linalg.norm(v)
        if nv == 0:
            continue
        v /= nv; nrm = np.array([-v[1], v[0]])
        offs = np.arange(0, m(25), m(0.15))
        for side, acc in ((1, hl), (-1, hr)):
            pts = np.array([p.x, p.y]) + side * nrm * offs[:, None]
            ins = sample(road_mask, pts, cv2.INTER_NEAREST) > 0
            k = np.argmin(ins) if not ins.all() else len(ins)
            if k > 0:
                acc.append(offs[k - 1])
    if not hl or not hr:
        return 0.0, 0.0
    return float(np.median(hl)), float(np.median(hr))


for L in links:
    L["hl"], L["hr"] = measure_halfwidth(L["g"])
    L["width"] = (L["hl"] + L["hr"]) / MM
major = [L for L in links if L["width"] >= MAJOR_W]
print("major links", len(major), "of", len(links))

# ------------------------------------------------------------------ 교차로(주요 도로 끝점 3개 이상)
ends = []
for i, L in enumerate(major):
    c = list(L["g"].coords)
    ends.append((c[0], i, 0)); ends.append((c[-1], i, 1))
pts = np.array([e[0] for e in ends])
tree = cKDTree(pts)
grp = -np.ones(len(ends), int); gid = 0
for i in range(len(ends)):
    if grp[i] >= 0:
        continue
    for j in tree.query_ball_point(pts[i], m(2.0)):
        if grp[j] < 0:
            grp[j] = gid
    gid += 1
nodes = defaultdict(list)
for k, e in enumerate(ends):
    nodes[grp[k]].append(e)
junctions = []
for k, es in nodes.items():
    if len({e[1] for e in es}) + sum(1 for e in es if False) >= 3 or len(es) >= 3:
        c = np.mean([e[0] for e in es], axis=0)
        wmax = max(major[e[1]]["width"] for e in es)
        junctions.append({"c": c, "ends": es, "r": m(0.5 * wmax + 1.5)})
for L in major:
    L["jct"] = [None, None]
for ji, J in enumerate(junctions):
    for (_, li, which) in J["ends"]:
        major[li]["jct"][which] = ji
JZ = unary_union([Point(J["c"]).buffer(J["r"]) for J in junctions]).intersection(ROAD) if junctions else Polygon()
print("junctions", len(junctions))


# ------------------------------------------------------------------ 링크별 단면 탐색
def frames_along(g, step):
    n = max(2, int(g.length / step) + 1)
    ss = np.linspace(0, g.length, n)
    P = np.array([g.interpolate(s).coords[0] for s in ss])
    T = np.gradient(P, axis=0); T /= np.linalg.norm(T, axis=1, keepdims=True) + 1e-12
    N = np.c_[-T[:, 1], T[:, 0]]
    return ss, P, T, N


def autocorr_peak(b, lags):
    b = b - b.mean()
    den = (b * b).sum()
    if den <= 1e-6:
        return 0.0, 0
    best, bl = -1.0, 0
    for L in lags:
        if L >= len(b) - 4:
            break
        v = (b[:-L] * b[L:]).sum() / den
        if v > best:
            best, bl = v, L
    return best, bl


DX = 0.075                                   # 단면 표본 간격(m)
LAGS = list(range(int(0.8 / DX), int(1.45 / DX) + 1))
crosswalks, cl_info = [], []
for li, L in enumerate(major):
    g = L["g"]
    ss, P, T, N = frames_along(g, m(STEP))
    offs = np.arange(-(L["hr"] + m(0.5)), L["hl"] + m(0.5), m(DX))
    if len(offs) < 20:
        continue
    along = np.array([-m(0.45), 0.0, m(0.45)])
    grid = P[:, None, None, :] + N[:, None, None, :] * offs[None, :, None, None] + T[:, None, None, :] * along[None, None, :, None]
    prof = sample(gray, grid).mean(axis=2)                      # (stations, offs)
    inr = sample(road_mask, grid[:, :, 1, :], cv2.INTER_NEAREST) > 0
    okv = sample(valid, grid[:, :, 1, :], cv2.INTER_NEAREST) > 0
    have = (okv & inr).sum(1) > 0.6 * inr.sum(1).clip(1)
    med = np.median(prof[inr & okv]) if (inr & okv).any() else 90.0
    thr = float(np.clip(med + 50, 130, 215))
    # --- 횡단보도: 단면이 밝은 줄무늬(주기 0.8~1.45 m)로 차도 폭을 덮는 구간
    #     단면마다 지표를 구한 뒤, (1) 교차로 입구(-2~+14 m)는 완화 기준, (2) 단일로는 엄격 기준(수치지형도 링크만)
    nS = len(ss)
    frac_a = np.zeros(nS); ac_a = np.zeros(nS); lag_a = np.zeros(nS); span_a = np.zeros(nS); gap_ok = np.zeros(nS, bool)
    for k in range(nS):
        sel = inr[k]
        if not have[k] or sel.sum() < 20:
            continue
        b = (prof[k] > thr) & sel
        frac_a[k] = b[sel].mean()
        if frac_a[k] <= 0.05:
            continue
        gap_ok[k] = prof[k][sel & ~b].mean() <= med + 28      # 줄무늬 사이는 아스팔트처럼 어두워야 한다
        idx = np.where(sel)[0]
        ac_a[k], lag = autocorr_peak(b[idx[0]:idx[-1] + 1].astype(np.float32), LAGS)
        lag_a[k] = lag * DX
        bi = np.where(b)[0]
        span_a[k] = (offs[bi[-1]] - offs[bi[0]]) / max(offs[idx[-1]] - offs[idx[0]], 1e-6)
    strict = (frac_a >= 0.18) & (frac_a <= 0.8) & (ac_a >= 0.17) & (span_a >= 0.45) & gap_ok
    relax = (frac_a >= 0.12) & (frac_a <= 0.85) & (ac_a >= 0.10) & (span_a >= 0.35) & gap_ok
    win = np.zeros(nS, bool)                                     # 교차로 입구 탐색 창
    for which in (0, 1):
        ji = L["jct"][which]
        if ji is None:
            continue
        r = junctions[ji]["r"]
        dist = ss if which == 0 else (g.length - ss)
        win |= (dist >= r - m(10.0)) & (dist <= r + m(14.0))
    mode = np.where(win, relax, strict if L["src"] == "ngii" else False)

    def add_runs(flag, min_d, max_d, tag, best_only):
        f2 = flag.copy(); f2[1:-1] |= flag[:-2] & flag[2:]
        runs = []
        k = 0
        while k < len(f2):
            if not f2[k]:
                k += 1; continue
            j = k
            while j + 1 < len(f2) and f2[j + 1]:
                j += 1
            depth = (ss[j] - ss[k]) / MM + STEP
            if min_d <= depth <= max_d:
                runs.append((k, j, depth, float(np.mean(ac_a[k:j + 1]))))
            k = j + 1
        if best_only and runs:
            runs = [max(runs, key=lambda r_: r_[3] * r_[2])]
        for k, j, depth, _ in runs:
            kk = [q for q in range(k, j + 1) if flag[q]] or list(range(k, j + 1))
            sc = (ss[k] + ss[j]) / 2
            c = np.array(g.interpolate(sc).coords[0])
            ti = int(np.argmin(abs(ss - sc)))
            crosswalks.append({"link": li, "s0": ss[k] - m(STEP / 2), "s1": ss[j] + m(STEP / 2), "c": c,
                               "t": T[ti], "n": N[ti], "a": -L["hr"], "b": L["hl"],      # 차도 전폭(교통섬은 뒤에서 잘림)
                               "period": float(np.clip(np.median(lag_a[kk]), 0.9, 1.3)), "depth_m": max(depth, 3.0), "how": tag})

    # 교차로 입구: 각 끝에서 가장 그럴듯한 1개
    for which in (0, 1):
        ji = L["jct"][which]
        if ji is None:
            continue
        r = junctions[ji]["r"]
        dist = ss if which == 0 else (g.length - ss)
        w1 = (dist >= r - m(10.0)) & (dist <= r + m(14.0))
        add_runs((relax if L["src"] == "ngii" else strict) & w1, 1.5, 9.0, "교차로 입구", True)
    add_runs(strict & ~win & (L["src"] == "ngii"), 2.0, 10.0, "단일로", False)
    # --- 중앙선: 이 항공사진은 색이 빠져 황색이 구분되지 않는다(황색 지수 최대 10).
    #     대신 차도 중앙 ±1.2 m 안의 '좁고 밝은 연속선' 비율로 실재를 확인한다.
    near = np.abs(offs) <= m(1.2)
    pk = prof[:, near]
    thr_l = med + 35
    wid = (pk > thr_l).sum(1) * DX
    present = (pk.max(1) > thr_l) & (wid <= 0.9) & have
    off_y = offs[near][np.argmax(pk, 1)]
    usable = have.sum()
    ratio = present.sum() / usable if usable > 10 else None
    cidx = int(np.argmin(np.abs(offs)))
    island = float((~inr[:, cidx]).mean())                      # 링크 중심이 도로 밖 = 화단형 분리대
    cl_info.append({"link": li, "ratio": ratio, "island": island,
                    "off": float(np.median(off_y[present])) if present.sum() > 5 else 0.0,
                    "off_mad": float(np.median(abs(off_y[present] - np.median(off_y[present])))) if present.sum() > 5 else 9})
print("crosswalks detected", len(crosswalks))

# ------------------------------------------------------------------ 횡단보도 정리: 영상 확인 + 주요 교차로 규칙 배치
def link_frame(L, sc):
    g = L["g"]
    a_, b_ = g.interpolate(max(sc - m(0.5), 0)), g.interpolate(min(sc + m(0.5), g.length))
    t_ = np.array([b_.x - a_.x, b_.y - a_.y]); t_ /= np.linalg.norm(t_) + 1e-12
    return np.array(g.interpolate(sc).coords[0]), t_, np.array([-t_[1], t_[0]])


final_cw = []
for ji, J in enumerate(junctions):
    widths = sorted([major[li]["width"] for _, li, _ in J["ends"]], reverse=True)
    significant = len(widths) >= 3 and widths[1] >= 9.0
    for (_, li, which) in J["ends"]:
        L = major[li]
        if L["width"] < 6.0:
            continue
        depth = 6.0 if L["width"] >= 15.0 else 4.0
        w_other = max([major[lj]["width"] for _, lj, _ in J["ends"] if lj != li] or [L["width"]])
        d_mouth = m(0.5 * w_other + 1.0) + m(depth) / 2
        if d_mouth > L["g"].length - m(2):
            continue
        s_c = d_mouth if which == 0 else L["g"].length - d_mouth
        det = [cw for cw in crosswalks if cw["link"] == li and cw.get("how") == "교차로 입구"
               and abs((cw["s0"] + cw["s1"]) / 2 - s_c) <= m(8.0)]
        if det:
            cw = dict(det[0]); cw["how"] = "영상 확인"; final_cw.append(cw)
        elif significant and L["src"] == "ngii":
            c_, t_, n_ = link_frame(L, s_c)
            final_cw.append({"link": li, "s0": s_c - m(depth) / 2, "s1": s_c + m(depth) / 2, "c": c_, "t": t_, "n": n_,
                             "a": -L["hr"], "b": L["hl"], "period": 1.0, "depth_m": depth, "how": "규칙 배치"})
for cw in crosswalks:
    if cw.get("how") != "단일로":
        continue
    sc = (cw["s0"] + cw["s1"]) / 2
    if any(f["link"] == cw["link"] and abs((f["s0"] + f["s1"]) / 2 - sc) < m(8) for f in final_cw):
        continue
    cw = dict(cw); cw["how"] = "영상 확인"; final_cw.append(cw)


def local_extent(c_, n_, cap_l, cap_r):
    offs_ = np.arange(0, m(25), m(0.15))
    res_ = []
    for side in (1, -1):
        pts_ = c_ + side * n_ * offs_[:, None]
        ins_ = sample(road_mask, pts_, cv2.INTER_NEAREST) > 0
        k_ = np.argmin(ins_) if not ins_.all() else len(ins_)
        res_.append(offs_[k_ - 1] if k_ > 0 else 0.0)
    return -min(res_[1], cap_r), min(res_[0], cap_l)


kept = []
drop = Counter()
for cw in sorted(final_cw, key=lambda c: 0 if c["how"] == "영상 확인" else 1):
    L = major[cw["link"]]
    a_, b_ = local_extent(cw["c"], cw["n"], L["hl"] * 1.3 + m(0.5), L["hr"] * 1.3 + m(0.5))
    lim = min(max(1.6 * L["width"], L["width"] + 6.0), 40.0)
    if (b_ - a_) / MM > lim:                       # 그 자리 폭이 교차로 쪽으로 새면 링크 차도 폭으로
        a_, b_ = -L["hr"], L["hl"]
    if b_ - a_ < m(4.0) or (b_ - a_) / MM > lim:
        drop["폭 이상"] += 1; continue
    # 더 넓은 다른 도로의 차도 안에 들어간 횡단보도(골목 끝 짧은 링크 등)는 버린다
    cpt = Point(cw["c"])
    def crossing_wider(o):
        if o is L or o["width"] < 1.5 * L["width"] or o["g"].distance(cpt) >= m(0.35 * o["width"]):
            return False
        d0 = o["g"].project(cpt)
        p0, p1 = o["g"].interpolate(max(d0 - m(1), 0)), o["g"].interpolate(min(d0 + m(1), o["g"].length))
        to = np.array([p1.x - p0.x, p1.y - p0.y]); to /= np.linalg.norm(to) + 1e-12
        return abs(float(to @ cw["t"])) < math.cos(math.radians(30))     # 방향이 다른(교차하는) 도로만
    if L["g"].length < m(15.0):                    # 골목 끝 짧은 링크(교차로 안에 박힌 조각)
        drop["짧은 링크"] += 1; continue
    cw["a"], cw["b"] = a_, b_
    half_ = (cw["s1"] - cw["s0"]) / 2
    poly = Polygon([cw["c"] + cw["t"] * u + cw["n"] * v for u, v in ((-half_, a_), (half_, a_), (half_, b_), (-half_, b_))])
    if any(poly.intersection(k["_poly"]).area > 0.2 * min(poly.area, k["_poly"].area) for k in kept):
        drop["겹침"] += 1; continue
    cw["_poly"] = poly
    kept.append(cw)
crosswalks = kept
print("crosswalks final", len(crosswalks), Counter(c["how"] for c in crosswalks), "dropped", dict(drop), "candidates", len(final_cw))

# ------------------------------------------------------------------ 중앙선 결정
CW_ZONE = unary_union([
    Polygon([cw["c"] + cw["t"] * (cw["s0"] - (cw["s0"] + cw["s1"]) / 2 - m(0.5)) + cw["n"] * (cw["a"] - m(1)),
             cw["c"] + cw["t"] * (cw["s1"] - (cw["s0"] + cw["s1"]) / 2 + m(0.5)) + cw["n"] * (cw["a"] - m(1)),
             cw["c"] + cw["t"] * (cw["s1"] - (cw["s0"] + cw["s1"]) / 2 + m(0.5)) + cw["n"] * (cw["b"] + m(1)),
             cw["c"] + cw["t"] * (cw["s0"] - (cw["s0"] + cw["s1"]) / 2 - m(0.5)) + cw["n"] * (cw["b"] + m(1))])
    for cw in crosswalks]) if crosswalks else Polygon()
CUT = unary_union([JZ, CW_ZONE])
center_lines, lane_lines, stats = [], [], Counter()
for ci in cl_info:
    L = major[ci["link"]]
    # 규칙: 양방통행 · 차로수 2 이상 · 차도 폭 6 m 이상 · 화단형 분리대 아님
    rule = (not L["oneway"]) and L["lanes"] >= 2 and L["width"] >= 6.0 and ci["island"] < 0.5
    wide = L["width"] >= 9.0 or L["lanes"] >= 4
    seen = ci["ratio"] is not None and ci["ratio"] >= 0.3
    if ci["ratio"] is None:
        has = rule; stats["규칙만(영상 없음)"] += int(has)
    else:
        has = rule and (wide or seen)              # 좁은 2차로는 영상에서 중앙선이 보일 때만
        stats["규칙+영상 확인" if (has and seen) else ("규칙(넓은 도로, 영상 불명확)" if has else ("규칙 충족·영상 없음→제외" if rule else "대상 아님"))] += 1
    L["has_cl"] = has
    off = ci["off"] if (seen and ci["off_mad"] < m(0.4) and abs(ci["off"]) < m(1.2)) else 0.0
    L["cl_off"] = off
    if not has:
        continue
    double = L["lanes"] >= 4 or L["median"] or L["width"] >= 13.0
    base = L["g"].offset_curve(off) if abs(off) > 1e-6 else L["g"]
    for oo in ((-m((CL_W + CL_GAP) / 2), m((CL_W + CL_GAP) / 2)) if double else (0.0,)):
        ln = base.offset_curve(oo) if oo else base
        for q in lines_of(ln.difference(CUT)):
            q = q.intersection(ROAD.buffer(-m(0.3)))
            for qq in lines_of(q):
                if qq.length > m(2):
                    center_lines.append({"pts": list(map(list, qq.coords)), "double": double})
# ------------------------------------------------------------------ 차선(방향별 2차로 이상)
for L in major:
    g = L["g"]
    if L["oneway"]:
        nd, sides = max(L["lanes"], 1), [("all", -L["hr"], L["hl"])]
    else:
        nd = max(L["lanes"] // 2, 1)
        off = L.get("cl_off", 0.0)
        sides = [("L", off, L["hl"]), ("R", -L["hr"], off)]
    if nd < 2:
        continue
    for nm, lo, hi in sides:
        for k in range(1, nd):
            o = lo + (hi - lo) * k / nd
            ln = g.offset_curve(o)
            for q in lines_of(ln.difference(CUT)):
                q = q.intersection(ROAD.buffer(-m(0.3)))
                for qq in lines_of(q):
                    if qq.length < m(1.5):
                        continue
                    # 교차로·횡단보도 가까운 곳은 실선, 나머지는 3/5 m 점선
                    near_zone = qq.intersection(CUT.buffer(m(SOLID_NEAR_JCT)))
                    for sol in lines_of(near_zone):
                        if sol.length > m(1):
                            lane_lines.append({"pts": list(map(list, sol.coords)), "solid": True})
                    for dq in lines_of(qq.difference(CUT.buffer(m(SOLID_NEAR_JCT)))):
                        d0 = 0.0
                        while d0 < dq.length:
                            seg = substring(dq, d0, min(d0 + m(DASH), dq.length))
                            if seg.length > m(0.8):
                                lane_lines.append({"pts": list(map(list, seg.coords)), "solid": False})
                            d0 += m(DASH + GAP)


# ------------------------------------------------------------------ 교통섬(수치지형도) — 칠한 섬만 빗금
islands = []
ri = shapefile.Reader(str(NG / "N3A_A0053326"), encoding="euc_kr")
for sh, rec in zip(ri.shapes(), ri.records()):
    if rec[0] != "교통섬":
        continue
    g = Polygon(m_from_5187(np.array(sh.points))).buffer(0)
    g = g.intersection(F).difference(S)
    if g.is_empty or g.area < m(1) * m(1):
        continue
    raised = g.intersection(PRINT).area / g.area > 0.5
    hatch = []
    if not raised:
        x0, y0, x1, y1 = g.bounds; dd = m(1.5)
        k = -((y1 - y0) // dd) - 2
        while True:
            off = k * dd
            ln = LineString([(x0 + off - 1, y0 - 1), (x1 + off + 1 + (y1 - y0), y1 + 1 + (x1 - x0))])
            ln = LineString([(x0 - 2 + off, y0 - 2), (x0 - 2 + off + (y1 - y0 + 4), y1 + 2)])
            if x0 - 2 + off > x1 + 2:
                break
            for q in lines_of(ln.intersection(g.buffer(-m(0.3)))):
                hatch.append(list(map(list, q.coords)))
            k += 1
    for p in getattr(g, "geoms", [g]):
        islands.append({"outline": list(map(list, p.exterior.coords)), "raised": raised, "hatch": hatch})

ISL = unary_union([Polygon(i["outline"]) for i in islands]) if islands else Polygon()

# ------------------------------------------------------------------ 횡단보도 줄무늬·정지선·화살표
def rect(c, t, n, s0, s1, a, b):
    return Polygon([c + t * s0 + n * a, c + t * s1 + n * a, c + t * s1 + n * b, c + t * s0 + n * b])


def arrow_glyph(kind):
    """진행방향 화살표(실제 m, x=오른쪽, y=진행방향, 길이 5 m). 반환: shapely Polygon"""
    sh, hw, hl = 0.15, 0.45, 1.2
    parts = []
    def straight(top=ARROW_L):
        return [box(-sh, 0, sh, top - hl), Polygon([(-hw, top - hl), (hw, top - hl), (0, top)])]
    def turn(sign):        # sign=-1 좌, +1 우 : 줄기 중간에서 꺾여 옆을 향함
        y = 2.6
        return [box(-sh, 0, sh, y + sh), box(min(0, sign * 0.9), y - sh, max(0, sign * 0.9), y + sh),
                Polygon([(sign * 0.9, y - hw), (sign * 0.9, y + hw), (sign * 1.6, y)])]
    if kind == "S":
        parts = straight()
    elif kind == "L":
        parts = turn(-1)
    elif kind == "R":
        parts = turn(1)
    elif kind == "SL":
        parts = straight() + turn(-1)
    elif kind == "SR":
        parts = straight() + turn(1)
    elif kind == "LR":
        parts = turn(-1) + turn(1)
    return unary_union(parts)


GLYPH = {k: arrow_glyph(k) for k in ("S", "L", "R", "SL", "SR", "LR")}


def place_glyph(kind, base_pt, fwd, right):
    g = GLYPH[kind]
    out = []
    for x, y in g.exterior.coords:
        out.append(base_pt + right * m(x) + fwd * m(y))
    return out


def movements(J, li, which):
    """교차로 J에 링크 li가 which 끝으로 들어올 때 가능한 진행(S/L/R)"""
    L = major[li]; c = list(L["g"].coords)
    p_in, p_end = (np.array(c[-2]), np.array(c[-1])) if which == 1 else (np.array(c[1]), np.array(c[0]))
    d_in = p_end - p_in; d_in /= np.linalg.norm(d_in)
    mv = set()
    for (_, lj, wj) in J["ends"]:
        if lj == li:
            continue
        cj = list(major[lj]["g"].coords)
        q0, q1 = (np.array(cj[0]), np.array(cj[1])) if wj == 0 else (np.array(cj[-1]), np.array(cj[-2]))
        d_out = q1 - q0; d_out /= np.linalg.norm(d_out)
        ang = math.degrees(math.atan2(d_in[0] * d_out[1] - d_in[1] * d_out[0], d_in @ d_out))
        if abs(ang) < 35:
            mv.add("S")
        elif 35 <= ang <= 150:
            mv.add("L")
        elif -150 <= ang <= -35:
            mv.add("R")
    return mv


cw_out, stop_out, arrow_out = [], [], []
for cw in crosswalks:
    L = major[cw["link"]]; g = L["g"]
    c, t, n = cw["c"], cw["t"], cw["n"]
    half = (cw["s1"] - cw["s0"]) / 2
    a, b = cw["a"], cw["b"]
    outline = rect(c, t, n, -half, half, a, b)
    stripes = []
    per = m(cw["period"]); sw = m(STRIPE_W)
    nst = int((b - a + per - sw) // per)
    start = (a + b) / 2 - (nst * per - (per - sw)) / 2
    for k in range(nst):
        o0 = start + k * per
        st = rect(c, t, n, -half, half, o0, o0 + sw).intersection(ROAD).difference(ISL)
        for q in getattr(st, "geoms", [st]):
            if q.geom_type == "Polygon" and q.area > 0.3 * m(STRIPE_W) * (2 * half):
                stripes.append(list(map(list, q.exterior.coords)))
    cw_out.append({"outline": list(map(list, outline.exterior.coords)), "stripes": stripes,
                   "depth_m": cw["depth_m"], "period_m": cw["period"], "how": cw["how"]})
    if not (L["has_cl"] or (L["oneway"] and L["lanes"] >= 2)):
        continue
    # 이 횡단보도에 가까운 교차로(링크 끝 25 m 이내)
    sc = (cw["s0"] + cw["s1"]) / 2
    cand = []
    if L["jct"][0] is not None and sc < m(25):
        cand.append((0, sc))
    if L["jct"][1] is not None and g.length - sc < m(25):
        cand.append((1, g.length - sc))
    off = L.get("cl_off", 0.0)
    if cand:
        which = min(cand, key=lambda x: x[1])[0]
        dirs = [(+1 if which == 1 else -1, which)]       # 교차로를 향해 달리는 방향만
    else:
        dirs = [(+1, None), (-1, None)]                  # 단일로: 양방향
    for sgn, which in dirs:
        # sgn=+1: 링크 진행방향(t)으로 달림 → 정지선은 횡단보도 '앞쪽'(-t 쪽), 차로는 오른쪽(-n 쪽)
        s_stop0 = (-half - m(STOP_GAP) - m(STOP_W)) if sgn > 0 else (half + m(STOP_GAP))
        s_stop1 = s_stop0 + m(STOP_W)
        if L["oneway"]:
            lo, hi = a, b
        else:
            lo, hi = (a, off) if sgn > 0 else (off, b)
        sp = rect(c, t, n, s_stop0, s_stop1, lo, hi).intersection(ROAD.buffer(-m(0.2)))
        if sp.is_empty or sp.area < m(0.5) * m(0.3):
            continue
        sp = max(getattr(sp, "geoms", [sp]), key=lambda q: q.area)
        if sp.intersects(ISL) or any(sp.intersects(Polygon(o["outline"])) for o in cw_out):
            continue
        stop_out.append(list(map(list, sp.exterior.coords)))
        if which is None:
            continue
        mv = movements(junctions[L["jct"][which]], cw["link"], which)
        if not mv:
            continue
        nd = max(L["lanes"] // 2, 1) if not L["oneway"] else max(L["lanes"], 1)
        fwd = t * sgn; right = -n * sgn
        lanes = []
        for k in range(nd):
            # 중앙선 쪽(1차로)부터 바깥쪽으로
            o_in = (off if not L["oneway"] else (hi if sgn > 0 else lo))
            w_tot = abs(hi - lo)
            o = o_in + (-n * sgn @ n) * 0 if False else None
            lanes.append(k)
        w_tot = abs(hi - lo); lw = w_tot / nd
        for k in range(nd):
            # 1차로(좌회전) = 중앙선에 붙은 차로
            lat_from_center = (k + 0.5) * lw
            if L["oneway"]:
                lat = (lo + lat_from_center) if sgn < 0 else (hi - lat_from_center)
            else:
                lat = (off - lat_from_center) if sgn > 0 else (off + lat_from_center)
            if nd == 1:
                kind = ("SL" if {"S", "L"} <= mv else "SR" if {"S", "R"} <= mv else "LR" if {"L", "R"} <= mv else sorted(mv)[0])
            elif k == 0:
                kind = "L" if "L" in mv else ("S" if "S" in mv else "R")
            elif k == nd - 1:
                kind = "SR" if {"S", "R"} <= mv else ("S" if "S" in mv else ("R" if "R" in mv else "L"))
            else:
                kind = "S" if "S" in mv else ("R" if "R" in mv else "L")
            s_base = (s_stop0 - m(ARROW_BACK) - m(ARROW_L)) if sgn > 0 else (s_stop1 + m(ARROW_BACK) + m(ARROW_L))
            base = c + t * s_base + n * lat
            poly = place_glyph(kind, base, fwd, right)
            if ROAD.buffer(-m(0.2)).contains(Polygon(poly)):
                arrow_out.append({"kind": kind, "pts": [list(p) for p in poly]})

out = {"center_lines": center_lines, "lane_lines": lane_lines, "crosswalks": cw_out, "stop_lines": stop_out,
       "arrows": arrow_out, "islands": islands,
       "stats": {"links": len(links), "major": len(major), "junctions": len(junctions),
                 "center_rule_vs_image": dict(stats), "crosswalks": dict(Counter(c["how"] for c in cw_out)), "stop_lines": len(stop_out),
                 "arrows": dict(Counter(a["kind"] for a in arrow_out)), "islands": len(islands),
                 "islands_painted": sum(1 for i in islands if not i["raised"])}}
json.dump(out, open(D / "markings.json", "w", encoding="utf-8"), ensure_ascii=False, default=_np)
print(json.dumps(out["stats"], ensure_ascii=False))
json.dump({"major": [{"pts": list(map(list, L["g"].coords)), "lanes": L["lanes"], "width": L["width"], "oneway": L["oneway"],
                      "median": L["median"], "has_cl": L.get("has_cl"), "src": L["src"]} for L in major],
           "junctions": [list(J["c"]) for J in junctions]}, open(D / "road_graph.json", "w", encoding="utf-8"), ensure_ascii=False, default=_np)
