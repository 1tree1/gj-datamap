"""구경주역 청년·신혼 1~2인 주거 — 규모 산정 계산 (재현용).
입력: archive/C_data/processed/hadm_pop_4326.geojson (주민등록 2026-08, T2), work/20261008_youth_housing/kosis_*.json (KOSIS 2025 등록센서스, T2)
출력: 표준출력. 모든 '가정'은 아래 PARAMS에 모아 두었다 — 숫자를 바꾸면 결과가 바뀐다.
"""
import json, io, collections

ROOT = r"C:\Users\OFFICE\Desktop\9_도시"
W = ROOT + r"\work\20261008_youth_housing"

# ---------- 가정(변경 가능) ----------
PARAMS = {
    "efficiency": [0.65, 0.70, 0.75],      # 전용률(전용/주거 연면적) — 계획 가정, 설계로 확정
    "types": {                              # 유형: (대표 전용㎡, 세대당 인원)
        "A 스튜디오(청년 1인)": (22, 1.0),
        "B 1.5룸(청년 1~2인·예비신혼)": (33, 1.3),
        "C 신혼 2룸(무자녀~영유아1)": (44, 2.3),
        "D 신혼 확장(영유아 1~2)": (58, 3.0),
    },
    "mix": {                                # 세대 구성비
        "P 풀 비례(청년 중심)": {"A": 0.40, "B": 0.25, "C": 0.27, "D": 0.08},
        "Q 정착 지향(신혼 확대)": {"A": 0.25, "B": 0.20, "C": 0.40, "D": 0.15},
    },
}

# ---------- 1. 풀(수요 모집단) ----------
def pools():
    k = {}
    d = json.load(io.open(W + r"\kosis_DT_1JC1502.json", encoding="utf-8"))
    tmp = collections.defaultdict(dict)
    for r in d:
        try: v = int(r["DT"])
        except ValueError: continue
        tmp[r["C1_NM"]][r["ITM_NM"]] = v
    core = ["황오동", "성건동", "황남동", "월성동"]
    tot = sum(tmp[n]["일반가구_계"] for n in core)
    one = sum(tmp[n]["1인"] for n in core); two = sum(tmp[n]["2인"] for n in core)
    k["원도심4동 가구/1인/2인"] = (tot, one, two, round((one + two) / tot * 100, 1))
    c = tmp["경주시"]; k["경주 가구/1인/2인"] = (c["일반가구_계"], c["1인"], c["2인"], round((c["1인"] + c["2인"]) / c["일반가구_계"] * 100, 1))
    h = json.load(io.open(W + r"\kosis_DT_1JC1511.json", encoding="utf-8"))
    ag = collections.defaultdict(dict)
    for r in h:
        try: ag[r["C2_NM"]][r["ITM_NM"]] = int(r["DT"])
        except ValueError: pass
    yb = ["20~24세", "25~29세", "30~34세", "35~39세"]
    k["가구주 20~39 가구/1인/2인"] = tuple(sum(ag[a].get(i, 0) for a in yb) for i in ("일반가구", "1인", "2인"))
    k["가구주 20~34 1인/2인"] = tuple(sum(ag[a].get(i, 0) for a in yb[:3]) for i in ("1인", "2인"))
    return k

# ---------- 2. 격차 회복법 (S2) ----------
def gap():
    d = json.load(io.open(ROOT + r"\archive\C_data\processed\hadm_pop_4326.geojson", encoding="utf-8"))["features"]
    P = {f["properties"]["hadm"]: f["properties"] for f in d}
    city_pop = sum(p["pop"] for p in P.values()); city_y39 = sum(p["n_youth"] for p in P.values()); city_y34 = sum(p["n_y2034"] for p in P.values())
    r39, r34 = city_y39 / city_pop, city_y34 / city_pop
    out = {"시 평균 20~39": round(r39 * 100, 2), "시 평균 20~34": round(r34 * 100, 2), "동": {}}
    s39 = s34 = 0
    for n in ("황오동", "황남동", "월성동"):   # 성건동은 대학가라 제외
        p = P[n]; g39 = r39 * p["pop"] - p["n_youth"]; g34 = r34 * p["pop"] - p["n_y2034"]
        out["동"][n] = (p["pop"], p["n_youth"], round(p["n_youth"] / p["pop"] * 100, 1), round(g39), p["n_y2034"], round(p["n_y2034"] / p["pop"] * 100, 1), round(g34))
        s39 += g39; s34 += g34
    out["격차 합계(20~39, 20~34)"] = (round(s39), round(s34))
    out["원도심(성건 제외) 인구"] = sum(P[n]["pop"] for n in ("황오동", "황남동", "월성동"))
    return out, s39, s34

# ---------- 3. 면적 역산 ----------
def area_table(ns=(300, 450, 600, 750, 900)):
    ty = PARAMS["types"]; keys = list(ty.keys())
    rows = []
    for mname, m in PARAMS["mix"].items():
        avg = sum(m[k[0]] * ty[k][0] for k in keys); ppl = sum(m[k[0]] * ty[k][1] for k in keys)
        for n in ns:
            net = n * avg
            rows.append((mname, round(avg, 1), round(ppl, 2), n, round(net), [round(net / e) for e in PARAMS["efficiency"]], round(n * ppl)))
    return rows

def community(n):   # 주택건설기준 등에 관한 규정 제55조의2 — 검색 요약(원문 미확인)
    if n < 100: return 0
    return 2.5 * n if n < 1000 else 500 + 2.0 * n

# ---------- 4. 저량-유량(stock-flow) 민감도 ----------
def stock_flow():
    flow_marry = 858          # 경주 혼인 2025 (T2 KOSIS INH_1B83A35)
    rows = []
    for s in (0.05, 0.10, 0.15):
        for T in (3, 5, 7):
            rows.append((s, T, round(flow_marry * s * T)))
    return rows

if __name__ == "__main__":
    print("== 풀"); [print(" ", k, v) for k, v in pools().items()]
    g, s39, s34 = gap(); print("== 격차 회복(S2)"); print(json.dumps(g, ensure_ascii=False, indent=1))
    for per in (1.3, 1.4, 1.6, 1.75):
        print("  격차 인원 %d~%d명 ÷ 20~39세 인원/세대 %.2f → %d~%d세대" % (s34, s39, per, s34 / per, s39 / per))
    print("== 면적 역산 (믹스, 평균전용, 인원/세대, 세대수, 전용합, 주거GFA@65/70/75%, 주거 인구)")
    for r in area_table(): print(" ", r)
    print("== 주민공동시설 최소면적(㎡)", {n: community(n) for n in (300, 450, 600, 750, 900)})
    print("== 신혼 stock-flow (점유율 s, 평균체류 T년 → 쌍)"); [print(" ", r) for r in stock_flow()]
    print("== 현행 플랜 환산: 46,528㎡ x 0.70 / 평균전용")
    for mname, avg, *_ in [(r[0], r[1]) for r in area_table(ns=(1,))]: print(" ", mname, avg, round(46528 * 0.70 / avg))
    print("   규제적용v1 634세대@36㎡ → 전용", 634 * 36, "GFA@70%", round(634 * 36 / 0.7))
