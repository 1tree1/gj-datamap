p="front_pages_b.py"; s=open(p,encoding="utf-8").read()
a=s.index("# ═════════════════════════ 06 사회적 문제")
open(p,"w",encoding="utf-8").write(s[:a]); print("cut ok", len(s[:a]))
