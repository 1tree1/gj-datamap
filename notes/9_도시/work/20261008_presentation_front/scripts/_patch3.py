def sub(path, pairs):
    s = open(path, encoding="utf-8").read()
    for a, b in pairs:
        if a not in s: print("MISSING in", path, ":", a[:60])
        s = s.replace(a, b)
    open(path, "w", encoding="utf-8").write(s)

sub("front_pages_c_macro.py", [
    ("            iw_, ih_ = Image.open(img).size; fh = w3 * ih_ / iw_\n            rect(s, xs[2], ey, w3, fh + 0.04, fill=\"#FFFFFF\", line=\"#C7CDD4\", line_w=0.75)\n            picture(s, img, xs[2] + 0.02, ey + 0.02, w3 - 0.04, fh, mode=\"contain\"); ey += fh + 0.06",
     "            iw_, ih_ = Image.open(img).size; cwid = w3 if ih_ / iw_ < 0.3 else 3.0; fh = cwid * ih_ / iw_\n            rect(s, xs[2], ey, cwid, fh + 0.04, fill=\"#FFFFFF\", line=\"#C7CDD4\", line_w=0.75)\n            picture(s, img, xs[2] + 0.02, ey + 0.02, cwid - 0.04, fh, mode=\"contain\"); ey += fh + 0.06"),
])
sub("front_pages_c.py", [
    ("ly = 1.9; lh = 0.95", "ly = 1.9; lh = 0.93"),
    ('kpi(s, x0, cy + 0.38, cw3, 0.92, "37곳"', 'kpi(s, x0, cy + 0.36, cw3, 0.98, "37곳"'),
    ('kpi(s, x0 + cw3 + 0.1, cy + 0.38, cw3, 0.92, "28m"', 'kpi(s, x0 + cw3 + 0.1, cy + 0.36, cw3, 0.98, "28m"'),
    ('kpi(s, x0 + 2 * (cw3 + 0.1), cy + 0.38, cw3, 0.92, "16%"', 'kpi(s, x0 + 2 * (cw3 + 0.1), cy + 0.36, cw3, 0.98, "16%"'),
])
print("patched3")
