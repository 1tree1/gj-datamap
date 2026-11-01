s=open("build_front.py",encoding="utf-8").read()
s=s.replace("def have(p): return os.path.exists(p)","def have(p): return bool(p) and os.path.exists(p)")
open("build_front.py","w",encoding="utf-8").write(s); print("have patched", "bool(p)" in s)
