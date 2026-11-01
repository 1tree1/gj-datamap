import pickle, collections
import os as _os; SP = _os.environ.get("PLAN_SP", r"C:\Users\OFFICE\AppData\Local\Temp\claude\C--Users-OFFICE-Desktop-9---\7c29478d-a6a9-42d3-ba5c-23abaf5c1032\scratchpad")   # 입력 pkl 폴더. 재현 시 PLAN_SP=<work/20261005_plan_clean/data>
M = pickle.load(open(SP + r"\clean_mass.pkl", "rb")); LP = pickle.load(open(SP + r"\lots.pkl", "rb"))
by = collections.defaultdict(lambda: [0, 0.0, 0.0, 0])
for b in M["BUILD"]:
    a = by[(b["lot_no"], b["lot"])]; a[0] += 1; a[1] += b["area"]; a[2] += b["area"] * b["floors"]; a[3] = max(a[3], b["floors"])
print("%-8s %-22s %5s %8s %8s %8s %6s %5s" % ("획지", "이름", "동", "획지㎡", "건축면적", "연면적", "BCR%", "FAR%"))
for d in LP["LOTS"]:
    a = by.get((d["no"], d["id"]), [0, 0, 0, 0])
    print("%-8s %-22s %5d %8.0f %8.0f %8.0f %6.1f %5.0f  최고%dF" % (d["id"], d["name"], a[0], d["area"], a[1], a[2], a[1] / d["area"] * 100, a[2] / d["area"] * 100, a[3]))

