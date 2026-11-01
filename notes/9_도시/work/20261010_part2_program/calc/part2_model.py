# -*- coding: utf-8 -*-
"""2파트 프로그램 규모 산정 모델 (2026-10-10)
입력값은 research/R1~R4의 계산 입력표에서 가져온다. 값의 성격은 주석에 법정/관측/가정으로 적는다.
실행: PYTHONUTF8=1 python part2_model.py  → part2_results.md, part2_results.csv
"""
import math, csv, io, json

CASES = ["보수", "기준", "적극"]
B = 217876.0  # 계획 경계 ㎡ (Rhino 측정 2026-10-10)

def tri(a, b, c):
    return dict(zip(CASES, (a, b, c)))

# ---------------- 입력 (보수, 기준, 적극) ----------------
P = dict(
    # 방문 인구
    V_day=tri(140085, 140085, 140085),          # 외지인 일평균(13개월 평균), R4 S02b
    alpha=tri(0.059, 0.079, 0.106),             # 포획률(가정). 5.9%=거주·직장 차감 근사, 7.9%=구역중심 r300, 10.6%=성동시장급 (R4 §4)
    K_pk=tri(1.48, 1.48, 1.65),                 # 설계일/평균 (P90, P95) R4
    K_hr=tri(0.065, 0.070, 0.078),              # 피크 1시간 비율 R4
    P_car=tri(0.769, 0.769, 0.769),             # 자가용 분담 R4 G1
    # 정주·근로 목표
    outflow_20_34=7249 / 6.0,                   # 20~34세 순유출 연평균 2020~25 (R4/B2) = 1,208
    jobs_share=tri(0.5, 0.75, 1.0),             # 연 순유출 중 대상지 일자리로 상쇄할 몫 (정책 가정)
    desk_m2=7.2,                                # 청사 설계표준 1인당 (R2 S04) -> 업무 원단위 준용
    office_gross=tri(1.30, 1.35, 1.40),         # 공용 가산 (R2 S04)
    support_addon=tri(1.15, 1.25, 1.35),        # 창업지원·회의·교육 가산 (가정)
    # 문화
    share_h=tri(0.05, 0.08, 0.12),              # 대상지 연 방문자 중 헤리티지 센터 이용 비율 (가정)
    gfa_per_visitor_h=tri(0.031, 0.037, 0.038), # ㎡/(연 방문자) 교토철도박물관 (R3 C01 △)
    old_station_gfa=2807.0,                     # 구 역사 1,404㎡x2F 실측 (R1)
    # 창작
    artists=675,                                # 예술활동증명 (R1/AR)
    studio_share=tri(0.06, 0.12, 0.20),         # 입주 비율 (가정)
    studio_gross=tri(50.0, 69.0, 90.0),         # ㎡/실 공용 포함 (R3 N02 △, 최대는 가정)
    # 청년주거
    H=tri(450, 600, 750),                       # 세대 (R1 Y문서)
    youth_ratio=0.80,                           # 청년 공급비율 (R2 S10, 70~90%)
    unit_net_youth=tri(21.83, 26.58, 36.70),    # 전용 ㎡ (R2 S16 포항블루밸리 관측)
    unit_net_newly=36.0,                        # 신혼 최소 전용 (R2 S09)
    net_to_gross=tri(0.655, 0.606, 0.606),      # 전용/지상연면적 (R2 S16)
    community_per_unit=tri(1.875, 2.5, 3.125),  # 주민공동시설 ㎡/세대 (R2 S06)
    local_fac=tri(200.0, 350.0, 500.0),         # 지역편의시설 ㎡ (세대 구간별, R2 S09)
    persons_youth=1.0, persons_newly=2.65,      # 인/호 (R2 S09)
    park_youth=0.70, park_newly=1.00,           # 대/세대 (R2 S09)
    # 숙박
    stay_ratio=0.169,                           # 숙박자 비율 (데이터랩 △, R1/A1)
    s_bed=tri(0.0025, 0.005, 0.010),            # 도시 숙박 인원 중 대상지 몫 (가정)
    persons_room=2.0,
    hotel_gfa_room=tri(43.0, 50.0, 52.0),       # ㎡/실 (R3 N04 △)
    # 상업
    g_comm=tri(0.6, 1.0, 1.5),                  # ㎡/(일 방문 유동) 성동시장 587점포 x 25㎡ ÷ 14,761 ≈ 1.0 로 보정 (가정, 판매·음식 원단위 근거 ✘)
    # 허브·커뮤니티
    hub_per_Ud=tri(0.15, 0.25, 0.35),           # ㎡/(설계일 방문자) 환승·관광지원 (가정)
    community=tri(1500.0, 2500.0, 4000.0),      # 청년·주민 커뮤니티·생활문화·도서관 (R3 N05 기준 943~1,963 + 가정)
    # 시나리오 B 청사
    hall_main_cap=tri(13965.0, 17759.0, 18907.0),   # 법정 상한 (R2 S01)
    hall_council_cap=tri(2257.0, 3351.0, 3429.0),
    hall_addon=tri(0.10, 0.15, 0.25),               # 주민편의·법정시설 가산 (가정)
    b_anchor_office_share=0.5,                      # B에서 청년오피스 축소 비율 (가정)
    # 주차 (경주시 조례 별표 8, R3)
    m2_per_stall_main=100.0,                        # 문화·집회·판매·업무
    m2_per_stall_lodging=200.0,                     # 근생·숙박
    stall_gross=tri(30.0, 32.0, 35.0),              # 주차전용건축물 ㎡/대 (가정)
    car_occupancy=2.8, turnover=3.3,                # 가정 (방문 수요 점검용)
    # 필지·층수
    parcel_ratio=0.60,                              # 획지율(대지/경계). strata 최종 59.6%, clean 67.2%
    park_ratio=0.16, road_ratio=0.24,
    floors=dict(office=5, hall=5, culture=3, studio=3, resid=6, lodging=4, comm=3, hub=2, civic=3, parking=5),
    floor_h=dict(office=3.9, hall=4.0, culture=5.0, studio=4.2, resid=3.0, lodging=3.3, comm=4.2, hub=4.2, civic=4.2, parking=3.0),
)

def v(key, c):
    x = P[key]
    return x[c] if isinstance(x, dict) and c in x else x

def model(c, scenario):
    r = {}
    F = v('V_day', c) * v('alpha', c)            # 평균일 방문 유동(명/일)
    Ud = F * v('K_pk', c)                         # 설계일
    Ph = Ud * v('K_hr', c)                        # 피크 1시간 도착
    r['방문유동_평균일'] = F; r['방문유동_설계일'] = Ud; r['피크1시간'] = Ph
    # A1 청년창업·기업지원
    W = v('outflow_20_34', c) * v('jobs_share', c)
    a1 = W * P['desk_m2'] * v('office_gross', c) * v('support_addon', c)
    r['청년일자리_목표(명)'] = W
    # A2 K-헤리티지
    Nh = F * 365 * v('share_h', c)
    a2_new = Nh * v('gfa_per_visitor_h', c)
    a2 = a2_new + P['old_station_gfa']
    r['헤리티지_연방문(명)'] = Nh
    # A3 창작
    ns = P['artists'] * v('studio_share', c)
    a3 = ns * v('studio_gross', c)
    r['스튜디오(실)'] = ns
    # A4 청년주거
    H = v('H', c); yr = P['youth_ratio']
    Hy, Hn = H * yr, H * (1 - yr)
    net = Hy * v('unit_net_youth', c) + Hn * P['unit_net_newly']
    a4_units = net / v('net_to_gross', c)
    a4 = a4_units + H * v('community_per_unit', c) + v('local_fac', c)
    pop_res = Hy * P['persons_youth'] + Hn * P['persons_newly']
    park_res = Hy * P['park_youth'] + Hn * P['park_newly']
    r['주거_세대'] = H; r['주거_인구(명)'] = pop_res
    # A5 숙박
    N_stay = v('V_day', c) * P['stay_ratio']
    rooms = N_stay * v('s_bed', c) / P['persons_room']
    a5 = rooms * v('hotel_gfa_room', c)
    r['객실(실)'] = rooms
    # A6 상업
    a6 = F * v('g_comm', c)
    # A7 허브, A8 커뮤니티
    a7 = Ud * v('hub_per_Ud', c)
    a8 = v('community', c)
    prog = {
        '청년창업·기업지원': a1, 'K-헤리티지·역사문화예술': a2, '창작 스튜디오·공방': a3,
        '청년주거(주거+공동시설)': a4, '숙박(마을호텔)': a5, '상업·시장 연계': a6,
        '모빌리티 허브·관광지원': a7, '커뮤니티·생활문화': a8,
    }
    kind = {
        '청년창업·기업지원': 'office', 'K-헤리티지·역사문화예술': 'culture', '창작 스튜디오·공방': 'studio',
        '청년주거(주거+공동시설)': 'resid', '숙박(마을호텔)': 'lodging', '상업·시장 연계': 'comm',
        '모빌리티 허브·관광지원': 'hub', '커뮤니티·생활문화': 'civic',
    }
    hall = 0.0
    if scenario == 'B':
        prog['청년창업·기업지원'] = a1 * P['b_anchor_office_share']
        hall = (v('hall_main_cap', c) + v('hall_council_cap', c)) * (1 + v('hall_addon', c))
        prog['시청·의회 캠퍼스'] = hall
        kind['시청·의회 캠퍼스'] = 'hall'
    # 주차 소요(경주시 조례): 면적/㎡당 대수 합 + 주거
    stalls_leg = 0.0
    main_kinds = ('청년창업·기업지원', 'K-헤리티지·역사문화예술', '창작 스튜디오·공방', '상업·시장 연계', '모빌리티 허브·관광지원', '시청·의회 캠퍼스')
    for k, a in prog.items():
        if k in main_kinds:
            stalls_leg += a / P['m2_per_stall_main']
        elif k in ('숙박(마을호텔)', '커뮤니티·생활문화'):
            stalls_leg += a / P['m2_per_stall_lodging']
    stalls_leg += park_res
    stalls_dem = Ud * v('P_car', c) / P['car_occupancy'] / P['turnover']
    if c == '적극':
        stalls = max(stalls_leg, 0.5 * stalls_dem)
    else:
        stalls = stalls_leg
    pk_gfa = stalls * v('stall_gross', c)
    prog['주차전용건축물'] = pk_gfa; kind['주차전용건축물'] = 'parking'
    r['주차_법정소요(대)'] = stalls_leg; r['주차_방문수요점검(대)'] = stalls_dem; r['주차_계획(대)'] = stalls
    total = sum(prog.values())
    nonpark = total - pk_gfa
    # 건축면적(바닥 수직투영) = 연면적/층수 (구 역사는 1,404㎡ 실측 1층분)
    foot = 0.0; maxh = 0.0
    rows = []
    for k, a in prog.items():
        fl = P['floors'][kind[k]]
        if k == 'K-헤리티지·역사문화예술':
            fp = (a - P['old_station_gfa']) / fl + 1404.0
        else:
            fp = a / fl
        h = fl * P['floor_h'][kind[k]]
        rows.append((k, a, fl, h, fp))
        foot += fp; maxh = max(maxh, h)
    site = B * P['parcel_ratio']
    r['대지면적'] = site
    r['공원·광장'] = B * P['park_ratio']; r['도로'] = B * P['road_ratio']
    r['연면적'] = total; r['연면적(주차전용 제외)'] = nonpark
    r['건축면적'] = foot
    r['건폐율'] = foot / site; r['용적률(주차전용 포함)'] = total / site; r['용적률(주차전용 제외)'] = nonpark / site
    r['최고높이(m)'] = maxh
    # 일자리 산출(참고): 업무 W, 상업 GFA/15㎡(2030 계획 도심상업 종업원 1인당 건물연상면적, T1)
    r['일자리_상업(명)'] = a6 / 15.0
    r['일자리_청년오피스(명)'] = prog['청년창업·기업지원'] / (P['desk_m2'] * v('office_gross', c) * v('support_addon', c))
    r['rows'] = rows
    r['판매음식비율'] = a6 / total
    return r

def fmt(x, d=0):
    return f"{x:,.{d}f}"

def run():
    out = io.StringIO(); csvrows = []
    for sc, label in (('A', '시나리오 A — 청년·문화 앵커형(NEXUS)'), ('B', '시나리오 B — 시청·의회 + 청년주거형(기존 덱)')):
        res = {c: model(c, sc) for c in CASES}
        out.write(f"\n## {label}\n\n")
        out.write("### 인구·이용자\n\n| 항목 | 보수 | 기준 | 적극 |\n|---|---:|---:|---:|\n")
        for k, d in (('방문유동_평균일', 0), ('방문유동_설계일', 0), ('피크1시간', 0), ('청년일자리_목표(명)', 0), ('주거_세대', 0), ('주거_인구(명)', 0), ('객실(실)', 0), ('스튜디오(실)', 0), ('헤리티지_연방문(명)', 0)):
            out.write(f"| {k} | " + " | ".join(fmt(res[c][k], d) for c in CASES) + " |\n")
        out.write("\n### 프로그램별 연면적(㎡)\n\n| 프로그램 | 보수 | 기준 | 적극 | 층수 | 높이(m) |\n|---|---:|---:|---:|---:|---:|\n")
        names = [r[0] for r in res['기준']['rows']]
        for n in names:
            vals = []
            for c in CASES:
                row = [x for x in res[c]['rows'] if x[0] == n][0]
                vals.append(row[1])
            row = [x for x in res['기준']['rows'] if x[0] == n][0]
            out.write(f"| {n} | " + " | ".join(fmt(x) for x in vals) + f" | {row[2]} | {row[3]:.1f} |\n")
            csvrows.append([sc, n] + [round(x) for x in vals])
        out.write("| **합계(연면적)** | " + " | ".join(f"**{fmt(res[c]['연면적'])}**" for c in CASES) + " | | |\n")
        out.write("\n### 규모 지표\n\n| 항목 | 보수 | 기준 | 적극 |\n|---|---:|---:|---:|\n")
        out.write(f"| 계획 경계(㎡) | {fmt(B)} | {fmt(B)} | {fmt(B)} |\n")
        for k, d in (('대지면적', 0), ('공원·광장', 0), ('도로', 0), ('건축면적', 0), ('연면적', 0), ('연면적(주차전용 제외)', 0)):
            out.write(f"| {k}(㎡) | " + " | ".join(fmt(res[c][k], d) for c in CASES) + " |\n")
        for k in ('건폐율', '용적률(주차전용 포함)', '용적률(주차전용 제외)', '판매음식비율'):
            out.write(f"| {k}(%) | " + " | ".join(fmt(res[c][k] * 100, 1) for c in CASES) + " |\n")
        out.write(f"| 최고 높이(m) | " + " | ".join(fmt(res[c]['최고높이(m)'], 1) for c in CASES) + " |\n")
        for k in ('주차_법정소요(대)', '주차_방문수요점검(대)', '주차_계획(대)', '일자리_상업(명)', '일자리_청년오피스(명)'):
            out.write(f"| {k} | " + " | ".join(fmt(res[c][k]) for c in CASES) + " |\n")
        # 획지율 민감도
        out.write("\n### 대지면적(획지율) 민감도 — 기준안\n\n| 획지율 | 대지면적(㎡) | 건폐율(%) | 용적률 포함(%) | 용적률 제외(%) |\n|---|---:|---:|---:|---:|\n")
        base = res['기준']
        for g in (0.58, 0.60, 0.67):
            s = B * g
            out.write(f"| {g:.2f} | {fmt(s)} | {fmt(base['건축면적']/s*100,1)} | {fmt(base['연면적']/s*100,1)} | {fmt(base['연면적(주차전용 제외)']/s*100,1)} |\n")
    return out.getvalue(), csvrows

if __name__ == '__main__':
    md, rows = run()
    with io.open('part2_results.md', 'w', encoding='utf-8') as f:
        f.write("# 2파트 규모 산정 결과 (part2_model.py 출력)\n\n계획 경계 217,876㎡, 획지율 0.60 기준. 값의 성격과 출처는 모델 파일 주석과 research/R1~R4 계산 입력표를 따른다.\n" + md)
    with io.open('part2_results.csv', 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f); w.writerow(['시나리오', '프로그램', '보수', '기준', '적극']); w.writerows(rows)
    print(md)
