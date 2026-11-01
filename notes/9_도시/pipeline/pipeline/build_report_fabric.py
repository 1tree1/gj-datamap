"""gj-datamap 리포트 '도시 조직' 그룹과 '도시 축의 변천사' 병합 카드용 수치·그림 묶음.

입력(모두 2026-09-28 산출)
  archive/90_derived/extent_diagnosis_20260928.json   (build_extent_diagnosis.py)
  archive/90_derived/edge_scale_profile_20260928.csv  (build_edge_scale_profile.py)
  archive/90_derived/fabric_global_20260928.json      (build_fabric_patterns.py)
  archive/90_derived/gj_reading_20260928.json         (build_gyeongju_reading.py)
  archive/90_derived/palimpsest_evidence_20260928.json, palimpsest_layers_20260928.json (build_palimpsest_*.py)
  work/maps/map10~16_*.png
출력
  archive/C_data/processed/fabric_report.json   → gj-datamap/public/data/ (scripts/sync_fabric.py)
  archive/90_derived/report_fabric/*.jpg        → gj-datamap/public/fabric/
"""
import csv
import json
from pathlib import Path

import numpy as np
import shapely
from PIL import Image
from shapely.geometry import shape

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

ROOT = Path(__file__).resolve().parent.parent
DER = ROOT / "archive" / "90_derived"
PROC = ROOT / "archive" / "C_data" / "processed"
MAPS = ROOT / "work" / "maps"
IMG = DER / "report_fabric"
IMG.mkdir(parents=True, exist_ok=True)

J = lambda p: json.load(open(DER / p, encoding="utf-8"))
EXT = J("extent_diagnosis_20260928.json")
FAB = J("fabric_global_20260928.json")
READ = J("gj_reading_20260928.json")
PAL = J("palimpsest_evidence_20260928.json")

# ── 구역 안쪽 경계거리 분포 (켜1 0–40 / 켜2 40–90 / 켜3 90 m 이상) ─────────
zone = shape(json.load(open(PROC / "gosi2026-8_zone_5187.geojson", encoding="utf-8"))["features"][0]["geometry"]).buffer(0)
b = zone.bounds
gx, gy = np.meshgrid(np.arange(b[0], b[2], 2.0) + 1, np.arange(b[1], b[3], 2.0) + 1)
X, Y = gx.ravel(), gy.ravel()
m = shapely.contains_xy(zone, X, Y)
d = shapely.distance(shapely.points(X[m], Y[m]), zone.exterior)
layers = {"d0_40": round(float((d < 40).mean()), 3), "d40_90": round(float(((d >= 40) & (d < 90)).mean()), 3),
          "d90": round(float((d >= 90).mean()), 3), "d90_ha": round(float((d >= 90).sum() * 4 / 1e4), 2), "dmax_m": round(float(d.max()))}

# ── 경계 바깥 띠 (방향 × 거리띠) ─────────────────────────────────
edge = []
with open(DER / "edge_scale_profile_20260928.csv", encoding="utf-8-sig") as fo:
    for r in csv.DictReader(fo):
        f = lambda k: (None if r[k] in ("", "nan", "None") else float(r[k]))
        edge.append({"side": r["방향"], "band": r["거리띠"], "bldg": int(float(r["건물수"])), "link_p50": f("교차간격_p50"), "link_p75": f("교차간격_p75"),
                     "road_p50": f("도로폭_p50"), "lane4": f("폭4m미만_연장비"), "parcel_p25": f("필지면적_p25"), "parcel_p50": f("필지면적_p50"),
                     "parcel_p75": f("필지면적_p75"), "parcel_p90": f("필지면적_p90"), "front_p50": f("간구_p50"), "depth_p50": f("깊이_p50"),
                     "fp_p50": f("바닥면적_p50"), "fp_p90": f("바닥면적_p90"), "blen_p90": f("건물길이_p90"), "f1": f("1층비율"), "f3": f("3층이상비율"),
                     "gsi": f("GSI"), "fsi": f("FSI"), "hw_p50": f("HW_p50")})

# ── 우회율 요약 ─────────────────────────────────────────────
zy = EXT["zone_y"]
zr = [p["ratio"] for p in EXT["detour_profile"] if zy[0] <= p["y"] <= zy[1]]
north = min((c for c in EXT["crossings"] if c["y"] > zy[1]), key=lambda c: c["y"])
gap_m = round(north["y"] - EXT["rail_gap"]["y"]) if EXT.get("rail_gap") else None

OUT = {
    "made": "2026-09-28",
    "model": {"extent_m": [3427, 3226], "area_km2": 11.06, "model_box_m": [1718.6, 1618.0], "scale": 0.5, "unit": "mm", "floor_h_model": 1.75,
              "z_fn": "z = 0.499 × 표고 + 233.85 (건물 바닥 4,000개 회귀, r 0.9998)", "bldg_n": 23579, "road_n": 10617, "road_km": 212.4},
    "margins": {"zone_m": EXT["margin_zone_to_extent_m"], "s2_m": EXT["margin_s2_to_extent_m"]},
    "detour": {"zone_y": zy, "profile": EXT["detour_profile"], "crossings": EXT["crossings"], "rail_gap": EXT.get("rail_gap"), "overpass": EXT["overpass"],
               "no_road_gap_m": gap_m, "zone_median": round(float(np.median(zr)), 2), "zone_max": round(float(max(zr)), 2)},
    "zone_layers": layers,
    "edge": edge,
    "fabric": FAB,
    "reading": READ,
    "palimpsest": {"grid_bearing": PAL["grid_bearing"], "wall": PAL["wall_segments"], "module_m": PAL["module_m"],
                   "rule_ew": {k: PAL["rule_lines"]["ew"][k] for k in ("T", "phase_m", "from")},
                   "rule_ns": {k: PAL["rule_lines"]["ns"][k] for k in ("T", "phase_m", "from")},
                   "phase_by_region": PAL["phase_by_region"], "out_of_sample": PAL["out_of_sample"],
                   # 권역별 스펙트럼: best_T/R_best = 100–200 m 안 최강 주기, R_module/p_module = 모듈 주기(남북 가로 164 m, 동서 가로 140 m)에서의 세기와
                   # 무작위 위치 500회 대비 p. p는 모듈 주기에 대한 값이지 최강 주기에 대한 값이 아니다(build_palimpsest_evidence.py §2)
                   "spectrum": {k: {ax: {"best_T": v[key]["best_T_100_200"], "R_best": v[key]["R_best"], "R_module": v[key]["R_at_module"], "p_module": v[key]["p_null"]}
                                    for ax, key in (("ns", "ns_x"), ("ew", "ew_y"))} for k, v in PAL["regions"].items()},
                   "module_source": PAL.get("module_source"),
                   # 147.5 m 위상 일관성을 잰 세 권역 — build_palimpsest_evidence.py 의 coh 계산과 같은 목록
                   "coherence_regions": ["읍성 권역(동부·서부·북부동)", "성동·황오동", "성건동"]},
    "literature": {
        "silla_modules": [["1단계(황룡사·인왕동)", "460척 = 163.3 m (택지 400척 + 도로부지 60척)"], ["2단계(원도심 포함)", "440척 = 156.2 m"],
                          ["3단계(북천 이북)", "450×350척 = 159.75×124.25 m"], ["남천 이남", "380척 = 약 135 m"]],
        "silla_src": "황인호(2011) 「新羅王京の整備における基準線と尺度」 奈良文化財研究所学報 87, pp.23–51 · Hwang In-ho(2009) IJKH 14, pp.59–90 (T3). 고구려척 1척 = 0.355 m",
        "eupseong_roads": [["북벽", "북문로"], ["동벽", "동문로"], ["남벽선", "화랑로(1936년 역 이전 때 남벽 철거·도로 개설, 김신재 2013 초록)"],
                           ["서쪽 해자", "금성로(옛 서성로)"], ["성 안 남북축", "봉황로(1915 본정통 직선 구간 포함)"], ["성 안 동서축", "북성로"]],
        "eupseong_src": "도로–성벽 대응은 위키·나무위키·언론(T4)과 좌표 대조. 네 도로 둘레 약 2.44 km ≈ 확인 석축 둘레 2,412 m(한국민족문화대백과, T3)",
    },
}
json.dump(OUT, open(PROC / "fabric_report.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("fabric_report.json", round((PROC / "fabric_report.json").stat().st_size / 1024), "KB", "| layers", layers, "| gap", gap_m, "| detour", OUT["detour"]["zone_median"], OUT["detour"]["zone_max"])

# ── 그림: 본문 JPG(가로 ≤1800) + 카드 썸네일(가로 720, 부분 잘라내기) ─────────────
FIGS = {  # key: (파일, 썸네일 잘라낼 영역 (x0, y0, x1, y1) 비율)
    "map10": ("map10_모델범위_분석신뢰반경_철도횡단.png", (0.0, 0.08, 0.68, 0.95)),
    "map11": ("map11_경계띠_스케일프로파일.png", (0.0, 0.0, 1.0, 1.0)),
    "map12": ("map12_경주조직_반복특성.png", (0.0, 0.08, 0.66, 0.70)),
    "map13": ("map13_경주_층위스택.png", (0.0, 0.05, 0.66, 0.97)),
    "map14": ("map14_경주_가시영역_6유형.png", (0.02, 0.05, 0.98, 0.37)),
    "map15": ("map15_경주_걷기_가시면적_리듬.png", (0.0, 0.05, 1.0, 0.36)),
    "map16": ("map16_경주_다익스트라_탐색.png", (0.5, 0.52, 1.0, 0.98)),
}
for k, (fn, crop) in FIGS.items():
    im = Image.open(MAPS / fn).convert("RGB")
    w, h = im.size
    big = im.resize((1800, round(h * 1800 / w)), Image.LANCZOS) if w > 1800 else im
    big.save(IMG / f"{k}.jpg", quality=85, optimize=True, progressive=True)
    c = im.crop((round(crop[0] * w), round(crop[1] * h), round(crop[2] * w), round(crop[3] * h)))
    c = c.resize((720, round(c.size[1] * 720 / c.size[0])), Image.LANCZOS)
    c.save(IMG / f"{k}_t.jpg", quality=80, optimize=True, progressive=True)
    print(k, big.size, round((IMG / f"{k}.jpg").stat().st_size / 1024), "KB · thumb", round((IMG / f"{k}_t.jpg").stat().st_size / 1024), "KB")

# ── 층위도 정지 썸네일 (밝은 판, 리포트 톤) ─────────────────────────────
L = json.load(open(DER / "palimpsest_layers_20260928.json", encoding="utf-8"))
fig = plt.figure(figsize=(9, 5.6), dpi=120)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_facecolor("#edf0ec"); fig.patch.set_facecolor("#edf0ec")
col = {"grid": "#27302d", "A": "#12806a", "B": "#12806a", "other": "#b6bfba"}
for sysk in ("other", "B", "A", "grid"):
    segs = [np.array(s["c"]) for s in L["streets"] if s["s"] == sysk]
    ax.add_collection(LineCollection(segs, colors=col[sysk], linewidths=0.9 if sysk == "grid" else 0.6))
for key in ("ew", "ns"):
    for ln in PAL["rule_lines"][key]["lines"]:
        a = np.array(ln); ax.plot(a[:, 0], a[:, 1], color="#c2267a", lw=1.1, ls=(0, (1.5, 3)))
for r in L["rail"]:
    a = np.array(r["c"]); ax.plot(a[:, 0], a[:, 1], color="#2a2e33", lw=2.2)
zc = np.array(L["zone"]); ax.fill(zc[:, 0], zc[:, 1], color="#cd3b22", alpha=0.15); ax.plot(zc[:, 0], zc[:, 1], color="#cd3b22", lw=2)
for w_ in L["wall"]:
    a = np.array(w_["c"]); ax.plot(a[:, 0], a[:, 1], color="#35589a", lw=4)
ax.set_xlim(250, 2450); ax.set_ylim(700, 2070); ax.set_aspect("equal"); ax.axis("off")
fig.savefig(IMG / "strata_t.jpg", dpi=120, facecolor="#edf0ec", pil_kwargs={"quality": 82})
print("strata_t.jpg", round((IMG / "strata_t.jpg").stat().st_size / 1024), "KB")
