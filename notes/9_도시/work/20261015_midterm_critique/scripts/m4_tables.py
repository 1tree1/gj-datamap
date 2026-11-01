"""M4 매스 재작업 v1 표 — 획지별 면적표 · 건축물표 · 추적표(CSV, utf-8-sig)
합계 검증: 획지 합 + 공원 + 도로·보행 = 구역 경계"""
from k0 import *
import csv

VAR = os.environ.get("MASSVAR", "v1"); VDIR = {"v1": "mass_v1", "v1b": "mass_v1b"}[VAR]; SUF = {"v1": "v1", "v1b": "v1b"}[VAR]
MV = pickle.load(open(os.path.join(K0DIR, "..", VDIR, "data", "mass_%s.pkl" % VAR), "rb"))
OD = os.path.join(K0DIR, "..", VDIR); TT = MV["TOT"]; S2 = MV["S"]
CATN = {k: v[1] for k, v in S["CATS"].items()}
T0 = {r["no"]: r for r in lot_targets()}


def w(name, head, rows):
    with open(os.path.join(OD, name), "w", newline="", encoding="utf-8-sig") as fh_:
        cw = csv.writer(fh_); cw.writerow(head); cw.writerows(rows)
    print("saved", name, len(rows))


# 1 획지별 면적표
rows = []
for r in MV["RES"]:
    rows.append([r["no"], [l["name"] for l in S["LOTS"] if l["no"] == r["no"]][0], r["form"] if r["no"] not in (2, 8) else "유지", round(r["A"], 1), round(r.get("opA", T0[r["no"]]["opA"]), 1),
                 round(r["ba0"], 1), round(r["ba_t"], 1), round(r["ba"], 1), round(r["ba0"] / r.get("A0", r["A"]), 3), round(r["ba"] / r["A"], 3), round(r["gfa0"], 1), round(r["gfa"], 1),
                 round(r["gfa"] / r["A"], 3), r["n0"], r["n"], round(r["gfa"] / r["ba"], 2), r["f0max"], r["fmax"], round(r["hmax"], 1), r["note"]])
parks = sum(p["g"].area for p in S["PARKS"])
rest = sum(g.area for g in S2["ROADS"].values()) + S2["WALK"].area + sum(o["g"].area for o in S["OPEN"]) + S["PATH8"].area + (MV["CORR"].area if "CORR" in MV else (EWB.area if "EW" not in S2["ROADS"] else 0.0))   # 도로 + 보도 + 보행축 + 조망로(+ v1-b 통경축), 따로 더함
rows.append(["합계", "", "", round(TT["lot"], 1), round(sum(r.get("opA", T0[r["no"]]["opA"]) for r in MV["RES"]), 1), round(TT["ba0"], 1), "", round(TT["ba"], 1), round(TT["ba0"] / TOT["lot"], 3),
             round(TT["ba"] / TT["lot"], 3), round(TT["gfa0"], 1), round(TT["gfa"], 1), round(TT["gfa"] / TT["lot"], 3), sum(r["n0"] for r in MV["RES"]), sum(r["n"] for r in MV["RES"]),
             round(TT["gfa"] / TT["ba"], 2), max(r["f0max"] for r in MV["RES"]), max(r["fmax"] for r in MV["RES"]), max(round(r["hmax"], 1) for r in MV["RES"]), ""])
rows.append(["검증", "획지 + 공원 + 도로·보도·보행축(각각 더함) = 구역", "", round(TT["lot"], 1), "공원 %.1f" % parks, "도로·보행 %.1f" % rest, "구역 %.1f" % TOT["boundary"],
             "차 %.3f" % (TOT["boundary"] - TT["lot"] - parks - rest), "구역 기준 건폐율 %.3f" % (TT["ba"] / TOT["boundary"]), "구역 기준 용적률 %.3f" % (TT["gfa"] / TOT["boundary"]),
             "", "", "", "", "", "", "", "", "", ""])
w("면적표_획지별_%s.csv" % SUF, ["획지", "획지명", "형태", "면적㎡", "지정비움㎡", "건축면적_지금㎡", "건축면적_목표㎡", "건축면적_v1㎡", "건폐율_지금", "건폐율_v1",
                       "연면적_지금㎡", "연면적_v1㎡", "용적률_v1", "동수_지금", "동수_v1", "평균층_v1", "최고층_지금", "최고층_v1", "최고높이_v1m", "메모"], rows)

# 2 건축물표
rows = []
for b in MV["BLD"]:
    by = b.get("gfa_by", {})
    rows.append([b["lot"], b["name"], "v1 생성" if b.get("gen") else "중간마감 유지", CATN.get(b["main"], b["main"]), "근린생활" if b.get("retail") else "",
                 b["floors"], round(b["h"], 2), round(b["g"].area, 1), round(b["gfa"], 1), " · ".join("%s %.0f" % (CATN.get(k, k), v) for k, v in by.items())])
w("건축물표_%s.csv" % SUF, ["획지", "동명", "구분", "주용도", "1층", "층수", "높이m", "건축면적㎡", "연면적㎡", "용도별 연면적㎡"], rows)

# 3 추적표(조정 내역) — 「CLAUDE.md」 §3.5
R_ = {r["no"]: r for r in MV["RES"]}
rows = [
    ["D01", "구역", "화랑로 연결", "동서 도로 20 m(차량 관통)", "A안 — 차는 역전광장에서 멈추고 같은 띠는 보행 통경축(비상·조업만 시간제)", "경관계획 통경축 '반드시 반영' [T1 A-009 p.206] / 발주 연구 '화랑로 차량이 원도심 분리' [T2 인쇄쪽 51]", "확정(2026-10-15 사용자)"],
    ["D02", "구역", "948 m 플랫폼", "없음(남북 보행축 지상)", "판 3구간: ① 관문 캐노피 +6.5 m ② 화랑로 게이트 +6.0 m ③ 교차광장 공중 회랑 +4.0 m", "매장문화재 — 굴착 대신 들어 올림 / 높이는 허용기준 ⑤ 8 m 아래(적용 구역 확인 필요)", "구간 확정 · 높이 제안"],
    ["D03", "구역", "획지 건폐율", "%.2f (동 바닥 합집합)" % (TT["ba0"] / TT["lot"]), "%.2f" % (TT["ba"] / TT["lot"]), "R3 규칙 — 순획지 목표 서측·중앙 0.65 · 동측 0.55 · 주차 0.85 · 구 역사 0.50, 평균 층수 하한", "확정(2026-10-15 사용자)"],
    ["D04", "구역", "구 역사 배치", "계획 모델 배치(실제 위치와 63 m·34° 차이)", "계획 모델 배치 유지" if VAR == "v1" else "실제 위치(콘타 모델·지적 정합) — 변형안 v1-b", "사용자 결정 — v1은 유지, v1-b는 사용자 요청으로 실제 위치", "확정(2026-10-15 사용자)"],
    ["D05", "구역", "층수 상한", "최고 7층 28 m(공공청사)", "최고 5층 20 m, 동측 경계 30 m 안 3층", "고도지구 20 m [T1] · 동측 경계 띠 1층 93% [자체 산출]", "제안"],
    ["D06", "구역", "연면적", f0(TT["gfa0"]), "%s (%+d, 획지 13 라이닝 상가)" % (f0(TT["gfa"]), round(TT["gfa"] - TT["gfa0"])), "획지별 연면적 고정, 끝수는 꼭대기 셋백", "제안"],
]
for no in sorted(R_):
    r = R_[no]
    rows.append(["L%02d" % no, "획지 %d %s" % (no, SHORT[no]), r["form"] if no not in (2, 8) else "유지",
                 "%d동 · 건축면적 %s㎡ · 최고 %d층" % (r["n0"], f0(r["ba0"]), r["f0max"]),
                 "%d동 · 건축면적 %s㎡ · 최고 %d층 %.0f m · 연면적 %s㎡" % (r["n"], f0(r["ba"]), r["fmax"], r["hmax"], f0(r["gfa"])), r["note"], "제안(v1 생성)" if no not in (2, 8) else "유지"])
rows.append(["N01", "획지 7", "삼층석탑 이격", "-", "석탑 중심 12 m 안 건축 없음", "문화재자료 8호 보호구역(21㎡) 밖 여유 — 12 m는 제안값", "제안"])
rows.append(["N02", "획지 2 → 1", "목표 부족분 이전", "-", "%s㎡를 획지 1 목표에 더함" % f0(T0[2]["ba1"] - T0[2]["ba0"]), "획지 2 남은 땅이 주차장동 둘레의 좁은 띠", "제안"])
if VAR == "v1b":
    P9 = [r for r in MV["RES"] if r["no"] == 9][0]; P7 = [r for r in MV["RES"] if r["no"] == 7][0]
    rows[6:6] = [
        ["D07", "획지 7·9", "획지선", "획지 9 %s㎡ · 획지 7 %s㎡" % (f0(P9["A0"]), f0(P7["A0"])), "획지 9 %s㎡ · 획지 7 %s㎡ (옛 동서 도로·보도 x 114–190, 획지 7 남서 모서리를 획지 9로)" % (f0(P9["A"]), f0(P7["A"])), "역사·역 앞마당·옛 1번 승강장을 한 획지에", "제안(v1-b)"],
        ["D08", "획지 9", "역 앞마당·통로", "역전광장 3,809㎡ · 그레이트 코트", "역 앞마당 %s㎡ · 대합실 관통 통로 8 m · 옛 1번 승강장 %s㎡ · 플랫폼 광장 %s㎡, 그레이트 코트·유리 지붕 삭제" % (f0(MV["TERM"].area), f0(MV["PLAT1"].area), f0(MV["PPLZ"].area)), "9월 지구단위계획안 E-W2(화랑로 → 구 역사 대합실 → 플랫폼광장 → 황오동)", "제안(v1-b)"],
        ["D09", "판 ①", "캐노피 위치", "사선 보행축 위", "구 역사 동쪽 옛 1번 승강장(폭 14 m, +6.5 m)", "구 역사 7 m보다 낮게", "제안(v1-b)"],
        ["D10", "획지 9", "건폐율 목표", "순획지 0.50", "순획지 %.2f — 전체 0.50을 맞추는 나머지, 역사 25 m 안 2층·그 밖 3층, 평균 층수 하한 1.5" % (P9["ba"] / (P9["A"] - P9["opA"])), "획지 7·9 밖은 v1 그대로", "제안(v1-b)"]]
rows.append(["D07" if VAR == "v1" else "D11", "구역", "안 선택", "v1 · v1-b(구 역사 실제 위치)", "v1 채택 — v1-b는 검토안(mass_v1b/)", "사용자 결정", "확정(2026-10-15 사용자)"])
w("추적표_매스재작업_%s.csv" % SUF, ["번호", "대상", "항목", "이전", "이후", "규칙·근거", "상태"], rows)
