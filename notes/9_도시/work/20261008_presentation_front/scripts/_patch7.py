p="front_pages.py"; s=open(p,encoding="utf-8").read()
s=s.replace("(시 구상 79,438㎡ [T4, 범위 미정의]","(시 구상 79,438㎡ — 경주시 보도자료 2025-12-18·2026-01-02 [T2], 범위 미정의")
open(p,"w",encoding="utf-8").write(s); print("ok")
