lines = open("m7_boundaries_label.py", encoding="utf-8").read().split("\n")
i = 111
print(lines[i][:60])
lines[i] = lines[i].replace("본 계획 경계", "분석 범위", 1)
open("m7_boundaries_label.py", "w", encoding="utf-8").write("\n".join(lines))
print("after:", lines[i][:60])
