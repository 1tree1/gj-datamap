"""현재 원도심 가로와 과거 격자의 관계 — 판정 근거 계산.

1) 방위: 현재 도로중심선의 길이가중 방위 분포(mod 180, 1° 간격)와 주 격자축, 읍성 성벽 현존 구간 방위
2) 간격 주기: 권역별로 정남북 격자에 정렬한 가로의 위치(격자 회전 좌표)를 모아 주기 스펙트럼 R(T)
   R(T) = |Σ w·exp(2πi·x/T)| / Σ w  (w = 가로 선 길이, 같은 위치 ±1 m 조각은 한 선으로 합침)
   귀무: 각 가로 선 위치를 ±T/2 무작위로 흔든 500회
3) 표본 외 위상 검정: 원도심 중앙 3권역에서 추정한 위상을 나머지 권역에 적용해 격자선 ±6 m 안 가로 비율의 무작위 대비 배율

모듈 T 는 채미옥(2026-09-12 LOWCA 워크숍 발표 p10, 근거 채미옥 외 2007·2011 국토연구원)의 '1방 = 동서 164 m × 남북 140 m'.
입력: 연속수치지도(NGII, T2), 출력: archive/90_derived/palimpsest_evidence_20260928.json
"""
import json
import math
import warnings
from collections import defaultdict
from pathlib import Path

import numpy as np
import shapefile
import shapely
from pyproj import Transformer
from shapely.geometry import shape
from shapely.ops import transform as shp_transform
from shapely.strtree import STRtree

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "대지" / "(B020)연속수치지도_202609132098"
OUT = ROOT / "archive" / "90_derived" / "palimpsest_evidence_20260928.json"
T57 = Transformer.from_crs("EPSG:5179", "EPSG:5187", always_xy=True)
MOD_X, MOD_Y = 164.0, 140.0
TS = np.arange(30, 260.01, 0.5)
REG = {"읍성 권역(동부·서부·북부동)": ["4713010100", "4713010200", "4713010300"],
       "노동·노서동": ["4713010600", "4713010700"],
       "성동·황오동": ["4713010400", "4713010500"],
       "황남·인왕·구황동": ["4713011000", "4713011200", "4713012200"],
       "성건동": ["4713010800"], "사정동": ["4713010900"], "동천동(대조군)": ["4713012600"]}
CORE = ["읍성 권역(동부·서부·북부동)", "노동·노서동", "성동·황오동"]


def to5187(g):
    return shp_transform(lambda x, y, z=None: T57.transform(x, y), g)


segs = []
for s in shapefile.Reader(str(SRC / "N3L_A0020000")).iterShapeRecords():
    g = to5187(shape(s.shape.__geo_interface__))
    for gg in getattr(g, "geoms", [g]):
        cs = list(gg.coords)
        for p, q in zip(cs[:-1], cs[1:]):
            l = math.dist(p, q)
            if l >= 0.5:
                segs.append(((p[0] + q[0]) / 2, (p[1] + q[1]) / 2, math.degrees(math.atan2(q[1] - p[1], q[0] - p[0])) % 180, l))
S = np.array(segs)
w = S[:, 3]

# 1) 방위 분포 · 주 격자축
h180, _ = np.histogram(S[:, 2], bins=180, range=(0, 180), weights=w)
h90, e90 = np.histogram(S[:, 2] % 90, bins=180, range=(0, 90), weights=w)
AX = float((e90[h90.argmax()] + e90[h90.argmax() + 1]) / 2)
wall = []
rw = shapefile.Reader(str(SRC / "N3L_C0325315")); flw = [f[0] for f in rw.fields[1:]]
for s in rw.iterShapeRecords():
    nm = dict(zip(flw, list(s.record))).get("name") or ""
    try:
        nm = nm.encode("latin-1").decode("cp949")
    except Exception:
        pass
    g = to5187(shape(s.shape.__geo_interface__))
    cs = list(g.coords) if g.geom_type == "LineString" else [c for gg in g.geoms for c in gg.coords]
    brg = math.degrees(math.atan2(cs[-1][0] - cs[0][0], cs[-1][1] - cs[0][1])) % 180
    wall.append({"name": nm.strip(), "length_m": round(g.length, 1), "bearing_NxE": round(brg, 1)})

# 권역: 선분 중점에서 가장 가까운 건물의 법정동
B, BD = [], []
rb = shapefile.Reader(str(SRC / "N3A_B0010000")); fl = [f[0] for f in rb.fields[1:]]
for s in rb.iterShapeRecords():
    B.append(to5187(shape(s.shape.__geo_interface__)).centroid)
    BD.append(str(dict(zip(fl, list(s.record))).get("bjcd"))[:10])
nn = STRtree(B).query_nearest(shapely.points(S[:, :2]), all_matches=False)
sd = np.empty(len(S), dtype=object); sd[nn[0]] = [BD[i] for i in nn[1]]

rot = math.radians(90 - AX)
xr = S[:, 0] * math.cos(rot) - S[:, 1] * math.sin(rot)
yr = S[:, 0] * math.sin(rot) + S[:, 1] * math.cos(rot)
ns = np.abs(((S[:, 2] - AX) + 90) % 180 - 90) <= 5
ew = np.abs(((S[:, 2] - (AX + 90)) + 90) % 180 - 90) <= 5


def lines(pos, wt):
    agg = defaultdict(float)
    for k, v in zip(np.round(pos / 2.0).astype(int), wt):
        agg[k] += v
    return np.array(list(agg.keys())) * 2.0, np.array(list(agg.values()))


def spec(p, ww):
    z = np.exp(2j * np.pi * p[None, :] / TS[:, None]) @ ww
    return np.abs(z) / ww.sum(), np.angle(z)


rng = np.random.default_rng(0)
regions = {}
for nm, codes in REG.items():
    m = np.isin(sd, codes)
    rec = {}
    for key, mask, pos, Tm in (("ns_x", m & ns, xr, MOD_X), ("ew_y", m & ew, yr, MOD_Y)):
        p, ww = lines(pos[mask], w[mask])
        R, ph = spec(p, ww)
        i = int(np.argmin(np.abs(TS - Tm)))
        null = np.array([abs(np.exp(2j * np.pi * (p + rng.uniform(-Tm / 2, Tm / 2, len(p))) / Tm) @ ww) / ww.sum() for _ in range(500)])
        band = (TS >= 100) & (TS <= 200)
        jb = np.where(band)[0][np.argmax(R[band])]
        rec[key] = {"n_lines": int(len(p)), "km": round(float(ww.sum()) / 1000, 2), "R_at_module": round(float(R[i]), 3),
                    "p_null": round(float((null >= R[i]).mean()), 3), "phase_m": round(float((ph[i] / (2 * np.pi) * Tm) % Tm), 1),
                    "best_T_100_200": float(TS[jb]), "R_best": round(float(R[jb]), 3), "spectrum": [round(float(v), 3) for v in R]}
    regions[nm] = rec

# 3) 표본 외 위상 검정
core = np.isin(sd, sum((REG[k] for k in CORE), []))


def phase(mask, pos, Tm):
    p, ww = lines(pos[mask], w[mask])
    return float((np.angle(np.exp(2j * np.pi * p / Tm) @ ww) / (2 * np.pi) * Tm) % Tm)


phx, phy = phase(core & ns, xr, MOD_X), phase(core & ew, yr, MOD_Y)
oos = {}
for nm, codes in REG.items():
    m = np.isin(sd, codes)
    r = {}
    for key, mask, pos, Tm, ph in (("ns_x", m & ns, xr, MOD_X, phx), ("ew_y", m & ew, yr, MOD_Y, phy)):
        off = ((pos[mask] - ph) + Tm / 2) % Tm - Tm / 2
        obs = float(w[mask][np.abs(off) <= 6].sum() / w[mask].sum())
        r[key] = {"share_within_6m": round(obs, 3), "random": round(12 / Tm, 3), "lift": round(obs / (12 / Tm), 2)}
    r["in_sample"] = nm in CORE
    oos[nm] = r

# 4) 측정된 규칙선: 동서 가로 147.5 m (읍성 권역 + 성동·황오동 위상), 남북 가로 161.5 m (황남·인왕·구황동 위상)
from shapely.geometry import LineString, MultiPoint
ORIGIN = (218200.0, 359450.0)   # build_palimpsest_layers 의 지역 좌표 원점
T_EW, T_NS = 147.5, 161.5
m_ew = np.isin(sd, REG["읍성 권역(동부·서부·북부동)"] + REG["성동·황오동"]) & ew
m_ns = np.isin(sd, REG["황남·인왕·구황동"]) & ns
ph_ew = phase(m_ew, yr, T_EW)
ph_ns = phase(m_ns, xr, T_NS)


def region_hull(codes):
    m = np.isin(sd, codes)
    return MultiPoint(S[m][:, :2]).convex_hull.buffer(-40)


def rule_lines(hull, axis, T_, ph):
    """회전 좌표에서 x'=상수(남북) 또는 y'=상수(동서) 선 → 5187 → 영역 안만 → 지역 좌표"""
    c, s = math.cos(rot), math.sin(rot)
    b = hull.bounds
    lines = []
    corners = [(b[0], b[1]), (b[2], b[1]), (b[0], b[3]), (b[2], b[3])]
    vals = [(x * c - y * s) if axis == "x" else (x * s + y * c) for x, y in corners]
    k0, k1 = math.floor((min(vals) - ph) / T_), math.ceil((max(vals) - ph) / T_)
    for k in range(k0, k1 + 1):
        v = ph + k * T_
        if axis == "y":   # x·s + y·c = v
            ln = LineString([(b[0] - 50, (v - (b[0] - 50) * s) / c), (b[2] + 50, (v - (b[2] + 50) * s) / c)])
        else:             # x·c − y·s = v
            ln = LineString([((v + (b[1] - 50) * s) / c, b[1] - 50), ((v + (b[3] + 50) * s) / c, b[3] + 50)])
        seg = ln.intersection(hull)
        for gg in getattr(seg, "geoms", [seg]):
            if gg.geom_type == "LineString" and gg.length > 60:
                lines.append([[round(x - ORIGIN[0], 1), round(y - ORIGIN[1], 1)] for x, y in gg.coords])
    return lines


hull_ew = region_hull(REG["읍성 권역(동부·서부·북부동)"] + REG["노동·노서동"] + REG["성동·황오동"] + REG["성건동"])
hull_ns = region_hull(REG["황남·인왕·구황동"])
rules = {"ew": {"T": T_EW, "phase_m": round(ph_ew, 1), "lines": rule_lines(hull_ew, "y", T_EW, ph_ew),
                "from": "읍성 권역 + 성동·황오동 동서 가로"},
         "ns": {"T": T_NS, "phase_m": round(ph_ns, 1), "lines": rule_lines(hull_ns, "x", T_NS, ph_ns),
                "from": "황남·인왕·구황동 남북 가로"}}
coh = {}
for key, Tm, mk, pos in (("ew_147.5", T_EW, ew, yr), ("ns_161.5", T_NS, ns, xr)):
    zs, tot, per = 0, 0, {}
    for nm in REG:
        if "동천" in nm:
            continue
        mm = np.isin(sd, REG[nm]) & mk
        p, ww = lines(pos[mm], w[mm])
        z = np.exp(2j * np.pi * p / Tm) @ ww
        per[nm] = {"phase_m": round(float((np.angle(z) / (2 * np.pi) * Tm) % Tm), 1), "R": round(float(abs(z) / ww.sum()), 3)}
    coh[key] = per
for key, grp in (("ew_147.5", ["읍성 권역(동부·서부·북부동)", "성동·황오동", "성건동"]),):
    Tm = T_EW
    z = sum(np.exp(2j * np.pi * coh[key][g]["phase_m"] / Tm) for g in grp) / len(grp)
    coh[key + "_coherence_3regions"] = round(float(abs(z)), 3)

out = {"module_m": [MOD_X, MOD_Y], "module_source": "채미옥 2026 LOWCA 발표 p10 (근거: 채미옥 외 2007 문화재청·국토연구원, 2011 경주시·국토연구원)",
       "grid_axis_mod90": AX, "grid_bearing": f"N{90 - AX:.1f}°E",
       "orientation_hist_mod180_len_km": [round(float(v) / 1000, 3) for v in h180],
       "wall_segments": wall, "periods_T": [float(t) for t in TS], "regions": regions,
       "core_phase_m": {"x": round(phx, 1), "y": round(phy, 1)}, "out_of_sample": oos,
       "rule_lines": rules, "phase_by_region": coh, "rotation_deg": round(math.degrees(rot), 2)}
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("grid", out["grid_bearing"], "wall", wall)
for nm, r in regions.items():
    print(nm, {k: {kk: vv for kk, vv in v.items() if kk != "spectrum"} for k, v in r.items()})
for nm, r in oos.items():
    print("OOS", nm, r)
print("saved", OUT)
