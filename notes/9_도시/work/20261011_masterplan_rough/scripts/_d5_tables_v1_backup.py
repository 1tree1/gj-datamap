"""D5 추적표(러프 원본 → 정리안 조정 내역)·면적표 CSV"""
import os, pickle, csv
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "..", "data"); OUT = os.path.join(HERE, "..")
S = pickle.load(open(os.path.join(D, "design.pkl"), "rb"))
LOTS = {l["no"]: l for l in S["LOTS"]}
with open(os.path.join(OUT, "추적표_러프정리_v1.csv"), "w", encoding="utf-8-sig", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["획지", "용지", "건축물", "용어(지구단위계획)", "용도분류", "층수", "층고m", "높이m", "건축면적㎡", "연면적㎡", "러프 원본", "조정 내역"])
    for m in S["MASS"]:
        l = LOTS[m["lot"]]
        w.writerow(["%d %s" % (l["no"], l["name"]), l["use"], m["name"], m["term"], S["CATS"][m["cat"]][1], m["floors"], m["fh"], m["h"],
                    round(m["g"].area), round(m["g"].area * m["floors"]), m["src"], m["adj"]])
SUM = S["SUM"]; B = SUM["boundary"]
with open(os.path.join(OUT, "면적표_러프정리_v1.csv"), "w", encoding="utf-8-sig", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["구분", "번호", "명칭", "용지·시설", "지정용도", "권장용도", "면적㎡", "비율%", "건축면적㎡", "연면적㎡", "최고층"])
    for l in S["LOTS"]:
        w.writerow(["획지", l["no"], l["name"], l["use"], l["main"], l["allow"], round(l["area"]), round(l["area"] / B * 100, 1), round(l["ba"]), round(l["gfa"]), l["maxf"]])
    w.writerow(["소계", "", "획지", "", "", "", round(SUM["lot_total"]), round(SUM["lot_total"] / B * 100, 1), round(SUM["ba"]), round(SUM["gfa"]), ""])
    for p in S["PARKS"]: w.writerow(["공원", p["key"], p["name"], p["kind"], "", "", round(p["area"]), round(p["area"] / B * 100, 1), "", "", ""])
    for p in S["OPEN"]: w.writerow(["보행녹지·광장", p["key"], p["name"], p["kind"], "", "", round(p["area"]), round(p["area"] / B * 100, 1), "", "", ""])
    for k, g in S["ROADS"].items(): w.writerow(["도로", k, {"N": "북측 진입도로(폭 13m)", "EW": "동서 도로(폭 20m)"}[k], "도로", "", "", round(g.area), round(g.area / B * 100, 1), "", "", ""])
    w.writerow(["보도", "", "외곽 보도", "보도", "", "", round(S["WALK"].area), round(S["WALK"].area / B * 100, 1), "", "", ""])
    w.writerow(["보도", "", "보행자전용도로(폭 8m)", "보행자전용도로", "", "", round(S["PATH8"].area), round(S["PATH8"].area / B * 100, 1), "", "", ""])
    w.writerow(["합계", "", "구역", "", "", "", round(B), 100.0, "", "", "닫힘 차 %.2f㎡" % SUM["closure"]])
print("ok")
