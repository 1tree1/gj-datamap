def sub(path, pairs):
    s = open(path, encoding="utf-8").read()
    for a, b in pairs:
        if a not in s: print("MISSING in", path, ":", a[:70])
        s = s.replace(a, b)
    open(path, "w", encoding="utf-8").write(s)

# 표지: 2025 정사영상(본 계획 경계 표시)
sub("build_front.py", [
    ('img = first(HI + r"\\cover_ortho2025.jpg", V3 + r"\\hero_before.jpg")', 'img = first(vimg(first(HI + r"\\ortho_2025_F1_outline.jpg")), HI + r"\\cover_ortho2025_outline.jpg", V3 + r"\\hero_before.jpg")'),
])
# 12쪽 결론 문장: 시민 요구와의 관계를 밝힌다
sub("front_pages_d.py", [
    ('''"원칙의 색은 11쪽 문제 번호, 13쪽 목표, 14쪽 전략에서 같은 색으로 이어집니다.", bar=BLUE, lead_size=10, body_size=8.8)''',
     '''"시민 요구(설문 응답 58건)는 문화·쇼핑 37, 교통 거점 16이었고 주거는 1건이었습니다. 문화·교통 요구는 남측·중앙에 반영하고, 정주 기능은 가구 구조와 야간 활동 자료를 근거로 추가합니다 [T2]. 원칙의 색은 13쪽 목표, 14쪽 전략으로 이어집니다.", bar=BLUE, lead_size=10, body_size=8.5)'''),
])
print("patched4")
