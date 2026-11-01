def sub(path, pairs):
    s = open(path, encoding="utf-8").read()
    for a, b in pairs:
        if a not in s: print("MISSING in", path, ":", a[:60])
        s = s.replace(a, b)
    open(path, "w", encoding="utf-8").write(s)

# 06 사회적 문제: 막대 겹침, 원문 도판 위치, KPI 높이
sub("front_pages_b_social.py", [
    ("rect(s, x + 1.5, yy + 0.04, 0.85 * ev / 30, 0.14, fill=c1); text(s, x + 1.5 + 0.85 * ev / 30 + 0.03, yy, 0.45, 0.22,", "rect(s, x + 1.5, yy + 0.04, 0.62 * ev / 30, 0.14, fill=c1); text(s, x + 1.5 + 0.62 * ev / 30 + 0.03, yy, 0.45, 0.22,"),
    ("rect(s, x + 2.5, yy + 0.04, 0.5 * ng / 7, 0.14, fill=c1); text(s, x + 2.5 + 0.5 * ng / 7 + 0.03, yy, 0.45, 0.22,", "rect(s, x + 2.62, yy + 0.04, 0.42 * ng / 7, 0.14, fill=c1); text(s, x + 2.62 + 0.42 * ng / 7 + 0.03, yy, 0.4, 0.22,"),
    ('text(s, x + 2.5, y0 + 0.24, 1.0, 0.18, "야간 23~05시"', 'text(s, x + 2.62, y0 + 0.24, 0.9, 0.18, "야간 23~05시"'),
    ("qw_, qh_ = Image.open(qimg).size; fw = 2.9; fh = fw * qh_ / qw_", "qw_, qh_ = Image.open(qimg).size; fw = 2.62; fh = fw * qh_ / qw_"),
    ("rect(s, x, 5.93, fw + 0.06, fh + 0.06,", "rect(s, x, 5.92, fw + 0.06, fh + 0.06,"),
    ("picture(s, qimg, x + 0.03, 5.96, fw, fh, mode=\"contain\")", "picture(s, qimg, x + 0.03, 5.95, fw, fh, mode=\"contain\")"),
    ('kpi(s, x, 4.98, kw, 0.9, "5,020만", "방문 연인원(2025)", "연인원, 총량 아님 [T2]", color=BLUE, big_size=17, desc_size=7.8)', 'kpi(s, x, 4.92, kw, 1.0, "5,020만", "방문 연인원(2025)", "연인원, 총량 아님 [T2]", color=BLUE, big_size=17, desc_size=7.8)'),
    ('kpi(s, x + kw + 0.1, 4.98, kw, 0.9, "79%", "체류 3시간 미만", "설문 2024, 축제 현장 비중 큼 [T2]", color=RED, fill="#FBEDED", big_size=17, desc_size=7.8)', 'kpi(s, x + kw + 0.1, 4.92, kw, 1.0, "79%", "체류 3시간 미만", "2024 설문, 축제 현장 포함 [T2]", color=RED, fill="#FBEDED", big_size=17, desc_size=7.8)'),
    ('kpi(s, x, 4.98, kw, 0.9, "0", "결정도 주거용지", "고시 2026-8호 [T1]", color=RED, fill="#FBEDED", big_size=17, desc_size=7.8)', 'kpi(s, x, 4.92, kw, 1.0, "0", "결정도 주거용지", "고시 2026-8호 [T1]", color=RED, fill="#FBEDED", big_size=17, desc_size=7.8)'),
    ('kpi(s, x + kw + 0.1, 4.98, kw, 0.9, "73.8%", "1~2인 가구", "원도심 4개 동은 82.6% [T2]", color=BLUE, big_size=17, desc_size=7.8)', 'kpi(s, x + kw + 0.1, 4.92, kw, 1.0, "73.8%", "1~2인 가구", "원도심 4개 동은 82.6% [T2]", color=BLUE, big_size=17, desc_size=7.8)'),
    ("text(s, x, 5.98, cw, 0.84, [dict(text=\"방문은 늘었지만", "text(s, x, 6.0, cw, 0.84, [dict(text=\"방문은 늘었지만"),
    ("text(s, x, 5.98, cw, 0.84, [dict(text=\"폐역 구역의 주거", "text(s, x, 6.0, cw, 0.84, [dict(text=\"폐역 구역의 주거"),
])
# 07: 인용 상자 높이, 밀도 막대 간격
sub("front_pages_c.py", [
    ("rect(s, xx, qy + 0.27, qw, 1.72, fill=\"#FFFFFF\"", "rect(s, xx, qy + 0.27, qw, 1.56, fill=\"#FFFFFF\""),
    ("text(s, xx + 0.08, qy + 1.43, qw - 0.16, 0.54, cap,", "text(s, xx + 0.08, qy + 1.29, qw - 0.16, 0.52, cap,"),
    ("fh = min(1.1, fw * ih_ / iw_)", "fh = min(0.95, fw * ih_ / iw_)"),
    ("    dy = 4.78\n", "    dy = 4.6\n"),
    ("step = min(0.27, 1.05 / max(1, n_rows))", "step = min(0.27, 1.28 / max(1, n_rows))"),
    ("bar_h=min(0.19, step - 0.05)", "bar_h=min(0.19, step - 0.04)"),
])
print("patched2")
