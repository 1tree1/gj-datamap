def sub(path, pairs):
    s = open(path, encoding="utf-8").read()
    for a, b in pairs:
        if a not in s: print("MISSING in", path, ":", a[:70])
        s = s.replace(a, b)
    open(path, "w", encoding="utf-8").write(s)
sub("front_pages_c_macro.py", [
    ("    mh3 = 2.15\n", "    mh3 = 1.9\n"),
    ("cwid = w3 if ih_ / iw_ < 0.3 else 3.0;", "cwid = w3 if ih_ / iw_ < 0.3 else 2.6;"),
])
sub("build_front.py", [
    ("img_align=(0.5, 0.5))\n\n@slide(\"div2\")", "img_align=(0.0, 0.5))\n\n@slide(\"div2\")"),
])
print("ok")
