# -*- coding: utf-8 -*-
"""2파트 실(室) 단위 면적표 모델 v2 (2026-10-11). 사용자 프로그램 리스트 기준.
공공청사·의회(R2 법정 상한)와 청년주거(R2/R1, 600세대)는 기존 조사값을 고정해 쓴다.
원단위는 research/R2~R5 계산 입력표. 근거 없는 실은 '설계 가정'으로 표시한다.
실행: PYTHONUTF8=1 python part2_model_v2.py -> part2_v2_results.md / .csv / .xlsx
"""
import io, csv, math
CASES = ["보수", "기준", "적극"]
B = 217876.0; PARCEL = 0.60; PARK = 0.16; ROAD = 0.24
def t(a, b, c): return (a, b, c)

# ---- 인구·이용자 ----
V = 140085.0; ALPHA = t(.059, .079, .106); KPK = t(1.48, 1.48, 1.65); KHR = t(.065, .07, .078)
OUTFLOW = 7249 / 6.0; JOBS_SHARE = t(.5, .75, 1.0)
H = t(450, 600, 750); NET_Y = t(21.83, 26.58, 36.70); NET_N = 36.0; NTG = t(.655, .606, .606)
YR = .8; PERS_Y, PERS_N = 1.0, 2.65; PARK_Y, PARK_N = .70, 1.0
COMM_PU = t(1.875, 2.5, 3.125); LOCAL_FAC = t(200., 350., 500.)
POP_S2 = 30261; CHILD_S2 = 219
DEN_CLASS = t(1.9, 3.33, 4.6)      # 소방 산정 1.9 / 교습소 3.33 / 집회 4.6 (R5 L22·L23 ✔)
DEN_HALL = t(1.9, 3.0, 4.6)

def run_case(i):
    F = V * ALPHA[i]; Ud = F * KPK[i]; Ph = Ud * KHR[i]
    W = OUTFLOW * JOBS_SHARE[i]; Wf = W / 906.0
    dc = DEN_CLASS[i]; dh = DEN_HALL[i]
    hh = H[i]; hy = hh * YR; hn = hh - hy
    ctx = dict(F=F, Ud=Ud, Ph=Ph, W=W, H=hh, pop_res=hy * PERS_Y + hn * PERS_N)
    rows = []   # (권역, 프로그램, 실, 면적, kind, 산정 근거, 상태, optional)
    def R(g, p, r, a, kind, basis, st, opt=False): rows.append((g, p, r, a, kind, basis, st, opt))
    # A 공공청사·의회 (R2: 공유재산법 시행령 별표 상한 + 가산)
    main = t(13965., 17759., 18907.)[i]; cnc = t(2257., 3351., 3429.)[i]; add = t(.10, .15, .25)[i]
    R('A 공공청사·의회', '공공청사·의회', '본청+의회 청사', (main + cnc) * (1 + add), 'hall', '법정 상한(본청+의회)×(1+편의·법정시설 가산). 시 구상 2단계 사안', '✔법정/가산 가정')
    # B 일상생활
    net = hy * NET_Y[i] + hn * NET_N
    R('B 일상생활', '청년·신혼 주거', '주거(세대+주거 공용)', net / NTG[i], 'resid', f'{hh:.0f}세대, 청년 80%(전용 {NET_Y[i]}㎡)·신혼 20%(36㎡) ÷ 전용률 {NTG[i]}', '✔법정·관측 R2')
    R('B 일상생활', '생활 편의', '생활편의점', 72., 'civic', '사례 72㎡(출처 불명)', '△가정')
    R('B 일상생활', '생활 편의', '카페(1~3개소)', t(100., 200., 300.)[i], 'civic', '개소 × 100㎡', '△가정')
    comm = hh * 0 + t(190., 450., 920.)[i]
    cap_hall = t(100, 150, 200)[i]
    R('B 일상생활', '주민 공동시설', '주민 커뮤니티홀', cap_hall * dh, 'civic', f'{cap_hall}인 × {dh}㎡/인', '△가정 용량, ✔밀도')
    R('B 일상생활', '주민 공동시설', '작은도서관', t(99., 120.1, 148.)[i], 'civic', '2025 전국 평균 120.1㎡(중위 99, 공립 148)', '✔ R5 D08')
    R('B 일상생활', '주민 공동시설', '공동부엌', t(26., 52.29, 100.)[i], 'civic', '사례 26~196㎡(행복황촌 52.29)', '△')
    ch = t(40, 60, 80)[i]
    R('B 일상생활', '주민 공동시설', '보육실', ch * t(4.29, 5.0, 6.0)[i], 'civic', f'정원 {ch}명 × 4.29㎡(법정 하한)~6.0㎡. 정원=신혼 20%×0.5+인근 영유아 10% 가정, 옥외놀이터 3.5㎡/명 별도', '✔법정 하한/가정')
    R('B 일상생활', '주민 공동시설', '생활관리실', t(60., 100., 150.)[i], 'civic', '가정', '△가정')
    R('B 일상생활', '생활 편의', '그늘쉼터 파빌리온(건축)', t(60., 90., 150.)[i], 'civic', '3~5동 × 30㎡', '△가정')
    planned = sum(r[3] for r in rows if r[2] in ('주민 커뮤니티홀', '작은도서관', '공동부엌', '보육실', '생활관리실'))
    need = hh * COMM_PU[i] + LOCAL_FAC[i]
    R('B 일상생활', '주민 공동시설', '법정 주민공동시설 보충(운동·휴게·다목적 등)', max(0., need - planned), 'civic', f'법정 소요 {need:,.0f}㎡(세대당 {COMM_PU[i]}㎡+지역편의 {LOCAL_FAC[i]:.0f}㎡) − 계획 실 합', '✔법정 R2')
    # C 청년 업무권
    core = W * 7.2 * t(1.30, 1.35, 1.40)[i]
    R('C 청년 업무권', '업무', '청년 창업 입주사무실', core * .6, 'office', f'일자리 {W:.0f}명 × 7.2㎡ × 공용 가산, 60%', '✔청사 설계표준 준용')
    R('C 청년 업무권', '업무', '공유 오피스', core * .4, 'office', '같은 총량의 40%', '△가정 비율')
    R('C 청년 업무권', '지원', '창업 상담·멘토링실', max(3, 6 * Wf) * 15., 'office', '6실×15㎡ (업무량 비례)', '△가정')
    R('C 청년 업무권', '지원', '직무교육실', max(1, 2 * Wf) * 40 * dc, 'office', f'2실 × 40인 × {dc}㎡/인', '△ 용량 가정, ✔밀도')
    R('C 청년 업무권', '지원', '공동회의실', max(2, 4 * Wf) * 12 * dc, 'office', f'4실 × 12인 × {dc}㎡/인', '△')
    cap_col = t(15, 20, 25)[i]
    R('C 청년 업무권', '지원', '분야별 협업실(건축·디자인·관광·문화유산)', 4 * cap_col * dc, 'office', f'4종 × {cap_col}인 × {dc}㎡/인', '△')
    R('C 청년 업무권', '지원', '공동 작업 쉼터(건축)', t(60., 80., 120.)[i], 'civic', '가정', '△가정')
    # D 창작·체험권
    ns = 675 * t(.06, .12, .20)[i]
    R('D 창작·체험권', '창작 레지던시', '개인 작업실', ns * t(23., 33., 49.)[i], 'studio', f'예술인 675명의 6/12/20% = {ns:.0f}실 × 23~49㎡(금천예술공장)', '✔사례/가정 비율')
    R('D 창작·체험권', '창작 레지던시', '작가 체류실', ns * .4 * 21.83, 'lodging', f'작업실의 40% × 21.83㎡(청년주거 최소 전용)', '△가정')
    R('D 창작·체험권', '창작 레지던시', '공동 제작공방', ns * 5., 'studio', '작업실 1실당 5㎡(목공·미디어 등 공용 7종 반영)', '△가정')
    R('D 창작·체험권', '창작 레지던시', '오픈스튜디오(작품 발표)', t(100., 150., 250.)[i], 'studio', '가정', '△')
    R('D 창작·체험권', '창작 레지던시', '작가 교류실', t(60., 80., 120.)[i], 'studio', '가정', '△')
    R('D 창작·체험권', '창작 레지던시', '재료·완성작품 보관실', ns * 6., 'studio', '작업실 1실당 6㎡', '△가정')
    s_exp = t(.05, .08, .12)[i]; fexp = F * s_exp; conc = fexp * .2
    R('D 창작·체험권', '역사·공예 체험관', '철도·원도심 체험전시실', conc * t(3.33, 4.6, 6.0)[i], 'culture', f'체험관 이용 {fexp:.0f}명/일(방문 유동의 {s_exp:.0%}), 동시 {conc:.0f}명 × 3.3~6.0㎡/인', '△가정')
    nr = t(2, 3, 4)[i]
    R('D 창작·체험권', '역사·공예 체험관', '전통공예 체험실', nr * 20 * dc, 'culture', f'{nr}실 × 20인 × {dc}㎡/인', '△ 용량, ✔밀도')
    R('D 창작·체험권', '역사·공예 체험관', '문화유산 디지털 기록 체험실', t(60., 100., 150.)[i], 'culture', '가정', '△')
    nk = t(2, 2, 3)[i]
    R('D 창작·체험권', '역사·공예 체험관', '어린이·가족 체험교실', nk * 30 * dc, 'culture', f'{nk}실 × 30인 × {dc}㎡/인', '△ 용량, ✔밀도')
    R('D 창작·체험권', '역사·공예 체험관', '체험 결과물 전시실', t(100., 150., 250.)[i], 'culture', '가정(군산 어린이체험실 126㎡ 참고)', '△')
    R('D 창작·체험권', '시장 접점', '성동시장 상인 공동 쇼케이스', t(60., 80., 120.)[i], 'comm', '참여 점포 20개 × 4㎡', '△가정')
    R('D 창작·체험권', '시장 접점', '지역 공예품 전시·판매실', t(80., 120., 200.)[i], 'comm', '가정', '△')
    R('D 창작·체험권', '시장 접점', '시장 상품 픽업·배송 거점', t(40., 60., 100.)[i], 'comm', '가정', '△')
    # E 역사문화예술권
    R('E 역사문화예술권', '1 구 역사·철도기억관', '구 역사 보존·활용(대합실·승강장 해설·상설전시 포함)', 2807., 'oldst', '1,404㎡ × 2F 실측. 이전 여부 미정', '✔실측')
    R('E 역사문화예술권', '1 구 역사·철도기억관', '철도 사진·지도·구술기록 아카이브', t(110., 160., 250.)[i], 'culture', '서고 50~125㎡/실(경남 기록관) + 열람·정리', '△')
    R('E 역사문화예술권', '1 구 역사·철도기억관', '철도 시설물 보존·복원 작업실', t(80., 120., 200.)[i], 'studio', '2실 × 40~100㎡', '△가정')
    perm = 3 * t(200., 300., 450.)[i]
    R('E 역사문화예술권', '2 경주 근대역사 전시관', '상설전시(원도심 변천·철도 전후·생활사 3주제)', perm, 'culture', '3주제 × 200~450㎡(군산 상설전시실 509~617㎡ 참고)', '△')
    R('E 역사문화예술권', '2 경주 근대역사 전시관', '순환형 기획전시실', t(150., 231., 300.)[i], 'culture', '군산 특별전시실 231㎡', '△')
    R('E 역사문화예술권', '2 경주 근대역사 전시관', '지역 예술가 전시실', t(100., 150., 250.)[i], 'culture', '가정', '△')
    R('E 역사문화예술권', '2 경주 근대역사 전시관', '전시관 공용(로비·화장실 등)', .12 * (perm + t(150., 231., 300.)[i] + t(100., 150., 250.)[i]), 'culture', '전시 면적의 12%(해외 박물관 공용 9~13%)', '✔초록 비율')
    seat_u = t(6.69, 8.58, 10.7)[i]
    R('E 역사문화예술권', '3 공연·시민문화시설', '공연장 350석(무대·분장·백스테이지·로비 포함)', 350 * seat_u, 'culture', f'350석 × {seat_u}㎡/석(단독 사례 6.69~9.72, 복합 7.95~15.7)', '△사례 3~8건')
    R('E 역사문화예술권', '3 공연·시민문화시설', '연습실·리허설실', 2 * t(60., 80., 100.)[i], 'culture', '2실', '△가정')
    cap_md = t(100, 150, 200)[i]; den_md = t(1.9, 1.9, 3.0)[i]
    R('E 역사문화예술권', '3 공연·시민문화시설', '시민 발표·강연용 다목적실', cap_md * den_md, 'culture', f'{cap_md}석 × {den_md}㎡/석', '△')
    R('E 역사문화예술권', '4 문화유산 창작·교육', '문화유산 보존·복원 교육실', 2 * t(15, 20, 25)[i] * dc, 'culture', f'2실 × 15~25인 × {dc}㎡/인', '△ 용량, ✔밀도')
    R('E 역사문화예술권', '4 문화유산 창작·교육', '공개 공방', t(80., 120., 200.)[i], 'studio', '관람형 공방 1개소', '△가정')
    nc = t(4, 6, 8)[i]
    R('E 역사문화예술권', '4 문화유산 창작·교육', '지역 공예 제작실', nc * 33., 'studio', f'{nc}실 × 33㎡', '△')
    ng = t(2, 2, 3)[i]
    R('E 역사문화예술권', '4 문화유산 창작·교육', '학교·단체 교육실(학교 연계 역사교육실+단체 교육실 통합)', ng * 35 * dc, 'culture', f'{ng}실 × 35인 × {dc}㎡/인. D 단체 교육실과 통합', '△ 용량, ✔밀도')
    nl = t(2, 3, 4)[i]
    R('E 역사문화예술권', '4 문화유산 창작·교육', '시민 강좌실', nl * 30 * dc, 'culture', f'{nl}실 × 30인 × {dc}㎡/인', '△')
    vc = t(173., 338., 820.)[i]
    for nm, sh in (('경주 원도심·문화유산 안내센터', .40), ('보행코스 출발 안내소', .10), ('방문자 라운지·휴게실', .30), ('성동시장·황오동 연결 안내 공간', .10), ('물품보관·편의시설', .10)):
        R('E 역사문화예술권', '5 방문자 관문', nm, vc * sh, 'hub', f'방문자센터 사례 173/338/820㎡(영등포·명동·강남)의 {sh:.0%}', '✔/△ 사례')
    R('E 역사문화예술권', '6 운영시설', '전시품 수장고', 87. * t(1, 2, 3)[i], 'culture', '실당 78~87㎡(남양주시립박물관)', '△')
    R('E 역사문화예술권', '6 운영시설', '시설 운영실', t(60., 100., 150.)[i], 'civic', '가정', '△가정')
    # 선택 제안
    R('I 선택 제안', '체류 연장', '식음·판매(카페 외 레스토랑·푸드코트)', F * t(.2, .3, .45)[i], 'comm', '방문 유동 × 0.2~0.45㎡(성동시장 보정치 1.0의 20~45%, 시장 경쟁 회피)', '✘가정', True)
    rooms = V * .169 * t(.0025, .005, .01)[i] / 2.0
    R('I 선택 제안', '체류 연장', '소규모 숙박(마을호텔형)', rooms * t(43., 50., 52.)[i], 'lodging', f'{rooms:.0f}실 × 43~52㎡', '△가정', True)
    R('I 선택 제안', '모빌리티', '환승·셔틀 대합실·공유모빌리티 보관', t(100., 200., 300.)[i], 'hub', '시 구상 3대 전략(모빌리티 허브) 반영', '△가정', True)
    return ctx, rows

FLOORS = dict(hall=5, resid=6, civic=3, office=5, studio=3, culture=3, oldst=2, hub=2, comm=3, lodging=4, parking=5)
HEIGHT = dict(hall=20.0, resid=18.0, civic=12.6, office=19.5, studio=12.6, culture=15.0, oldst=9.0, hub=8.4, comm=12.6, lodging=13.2, parking=15.0)
MAIN100 = ('hall', 'office', 'culture', 'comm', 'hub', 'oldst', 'studio')   # 문화·집회·판매·업무: 100㎡/대(경주시 조례)

def summarize(i, with_opt):
    ctx, rows = run_case(i)
    rows2 = [r for r in rows if with_opt or not r[7]]
    gfa = sum(r[3] for r in rows2)
    # 주차(경주시 조례): 문화·집회·판매·업무 100㎡/대, 근생·숙박 200㎡/대, 주거 0.7/1.0대
    hy = ctx['H'] * YR; hn = ctx['H'] - hy
    stalls = sum(r[3] / 100. for r in rows2 if r[4] in MAIN100) + sum(r[3] / 200. for r in rows2 if r[4] in ('civic', 'lodging')) + hy * PARK_Y + hn * PARK_N
    stall_gross = t(30., 32., 35.)[i]
    pk = stalls * stall_gross
    foot = 0.0; maxh = 0.0
    for r in rows2:
        k = r[4]
        if k == 'oldst': foot += 1404.; maxh = max(maxh, HEIGHT[k]); continue
        if k == 'resid' or True:
            foot += r[3] / FLOORS[k]
        maxh = max(maxh, HEIGHT[k])
    foot += pk / FLOORS['parking']
    site = B * PARCEL
    tot = gfa + pk
    return ctx, rows2, dict(gfa=gfa, stalls=stalls, pk=pk, total=tot, foot=foot, site=site, bcr=foot / site, far_in=tot / site, far_ex=gfa / site, maxh=max(maxh, 15.0))

def f0(x): return f"{x:,.0f}"
def main():
    out = io.StringIO(); csv_rows = []
    for opt, title in ((False, '사용자 리스트 기준(선택 제안 제외)'), (True, '선택 제안 포함')):
        res = [summarize(i, opt) for i in range(3)]
        out.write(f"\n## {title}\n\n### 인구·이용자 가정\n\n| 항목 | 보수 | 기준 | 적극 |\n|---|---:|---:|---:|\n")
        for lab, key in (('방문 유동(평균일, 명)', 'F'), ('방문 유동(설계일, 명)', 'Ud'), ('피크 1시간 도착(명)', 'Ph'), ('청년 일자리(명)', 'W'), ('거주 세대', 'H'), ('거주 인구(명)', 'pop_res')):
            out.write(f"| {lab} | " + " | ".join(f0(res[i][0][key]) for i in range(3)) + " |\n")
        out.write("\n### 실별 면적표(㎡, 연면적 기준)\n\n| 권역 | 프로그램 | 실 | 보수 | 기준 | 적극 | 산정 근거(기준안) | 상태 |\n|---|---|---|---:|---:|---:|---|---|\n")
        names = [(r[0], r[1], r[2]) for r in res[1][1]]
        sub = {}
        for n in names:
            vals = [[r for r in res[i][1] if (r[0], r[1], r[2]) == n][0] for i in range(3)]
            out.write(f"| {n[0]} | {n[1]} | {n[2]} | " + " | ".join(f0(v[3]) for v in vals) + f" | {vals[1][5]} | {vals[1][6]} |\n")
            for i in range(3): sub.setdefault(n[0], [0, 0, 0])[i] += vals[i][3]
            if not opt: csv_rows.append([n[0], n[1], n[2]] + [round(v[3]) for v in vals] + [vals[1][5], vals[1][6]])
        out.write("\n### 권역별 소계(㎡)\n\n| 권역 | 보수 | 기준 | 적극 | 기준 구성비 |\n|---|---:|---:|---:|---:|\n")
        tot_gfa = [res[i][2]['gfa'] for i in range(3)]
        for g, v in sub.items(): out.write(f"| {g} | " + " | ".join(f0(x) for x in v) + f" | {v[1] / tot_gfa[1] * 100:.1f}% |\n")
        out.write("| **프로그램 연면적 합(주차 제외)** | " + " | ".join(f"**{f0(x)}**" for x in tot_gfa) + " | 100% |\n")
        out.write("\n### 개발규모 산정표\n\n| 항목 | 보수 | 기준 | 적극 |\n|---|---:|---:|---:|\n")
        out.write(f"| 계획 경계(㎡) | {f0(B)} | {f0(B)} | {f0(B)} |\n")
        for lab, key, d in (('대지면적(㎡, 경계×60%)', 'site', 0), ('건축면적(㎡)', 'foot', 0), ('프로그램 연면적(주차 제외, ㎡)', 'gfa', 0), ('주차 소요(대, 조례)', 'stalls', 0), ('주차전용건축물(㎡)', 'pk', 0), ('총 연면적(주차 포함, ㎡)', 'total', 0)):
            out.write(f"| {lab} | " + " | ".join(f0(res[i][2][key]) for i in range(3)) + " |\n")
        for lab, key in (('건폐율(%)', 'bcr'), ('용적률, 주차 포함(%)', 'far_in'), ('용적률, 주차 제외(%)', 'far_ex')):
            out.write(f"| {lab} | " + " | ".join(f"{res[i][2][key] * 100:.1f}" for i in range(3)) + " |\n")
        out.write(f"| 최고 높이(m) | " + " | ".join(f"{res[i][2]['maxh']:.1f}" for i in range(3)) + " |\n")
        out.write(f"| 공원·광장(㎡, 경계×16%) | {f0(B * PARK)} | {f0(B * PARK)} | {f0(B * PARK)} |\n")
    # 점검: 법정 주민공동시설
    out.write("\n## 점검\n\n")
    for i, c in enumerate(CASES):
        ctx, rows = run_case(i)
        civic = sum(r[3] for r in rows if r[2] in ('주민 커뮤니티홀', '작은도서관', '공동부엌', '보육실', '생활관리실', '법정 주민공동시설 보충(운동·휴게·다목적 등)'))
        need = ctx['H'] * COMM_PU[i] + LOCAL_FAC[i]
        out.write(f"- {c}: 주민 공동시설 법정 소요 {need:,.0f}㎡(세대당 {COMM_PU[i]}㎡ + 지역편의 {LOCAL_FAC[i]:.0f}㎡) vs 계획 {civic:,.0f}㎡ → {'충족' if civic >= need - 1 else '부족'}\n")
        cult = sum(r[3] for r in rows if r[1] in ('1 구 역사·철도기억관', '2 경주 근대역사 전시관', '역사·공예 체험관', '4 문화유산 창작·교육', '5 방문자 관문', '6 운영시설') and r[2] != '시설 운영실')
        nh = ctx['F'] * 365 * t(.05, .08, .12)[i]
        unit = t(.031, .037, .038)[i]
        out.write(f"  - 헤리티지 복합(구 역사·전시관·체험관·교육·관문·수장) 상향식 {cult:,.0f}㎡ vs 방문자 기준 환산 {nh * unit + 2807:,.0f}㎡(연 {nh:,.0f}명 × {unit}㎡ + 구 역사). 상향식 면적의 수용 환산 연 {max(cult - 2807, 0) / unit:,.0f}명\n")
    return out.getvalue(), csv_rows

if __name__ == '__main__':
    md, rows = main()
    with io.open('part2_v2_results.md', 'w', encoding='utf-8') as f: f.write("# 프로그램 면적표 v2 계산 결과\n\n계획 경계 217,876㎡, 획지율 0.60.\n" + md)
    with io.open('part2_v2_results.csv', 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f); w.writerow(['권역', '프로그램', '실', '보수', '기준', '적극', '산정 근거(기준)', '상태']); w.writerows(rows)
    try:
        import openpyxl
        wb = openpyxl.Workbook(); ws = wb.active; ws.title = '면적표(선택 제외)'
        ws.append(['권역', '프로그램', '실', '보수(㎡)', '기준(㎡)', '적극(㎡)', '산정 근거(기준)', '상태'])
        for r in rows: ws.append(r)
        wb.save('part2_v2_area_table.xlsx'); print('xlsx ok')
    except Exception as e:
        print('xlsx skip', e)
    print(md)
