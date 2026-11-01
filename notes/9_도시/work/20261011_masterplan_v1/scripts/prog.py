"""P0 프로그램 → 획지 배분표. 2파트 v2 면적표(기준)의 실별 연면적을 사용자 도면의 획지 성격에 맞춰 나눈다.
입력: ../../20261010_part2_program/calc/part2_model_v2.py 의 run_case(1)=기준안 실 목록(권역, 프로그램, 실, 면적, kind, ...)
출력: LOT_PROG(획지별 구성 요소: 이름·연면적·층수·높이·색 범주), 주차 소요, 총량 점검. (config 가정은 ASSUME 에 모았다)
배분 가정(사용자 획지 이름 근거): 식음·판매(선택 제안 3,320㎡)는 사용자 획지에 '팝업스토어·상가·근린시설'이 명시돼 있어 포함, 소규모 숙박은 해당 획지가 없어 제외,
모빌리티 대합실 200㎡는 '관광지원시설' 획지에 둔다. 생활체육시설 2,500㎡는 이전 리스트에 없던 행이라 새 가정이다(사용자 라이노 획지 '생활편의체육시설')."""
import os, sys, math, json
CALC = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "20261010_part2_program", "calc"))
sys.path.insert(0, CALC)
import part2_model_v2 as M

ASSUME = dict(
    sports_gfa=2500.0,          # 생활체육시설(다목적체육관·피트니스·생활편의) 연면적 가정 — 공식 원단위 없음(R5 ✘)
    retail_total=None,          # 식음·판매 총량은 모델 값(선택 제안 행)
    retail_split=dict(문3=0.50, 상1=0.30, 업1=0.08, 업2=0.12),   # 식음·판매 3,320㎡ 배분 비율 가정
    office_split=dict(업1=0.40, 업2=0.60),                          # 청년 업무 연면적 배분(획지 면적비에 가깝게)
    d_split=dict(문4=0.4117, 문5=0.5883),                            # 레지던시·체험 배분(문4 8,396㎡ : 문5 11,998㎡)
    stall_gross=32.0,           # 주차 1대당 총면적(㎡) — 기준안 가정
    park_floors=5,
)

FL = dict(hall=5, resid=6, civic=3, office=5, studio=3, culture=3, oldst=2, hub=2, comm=3, lodging=4, parking=5)
HT = dict(hall=19.5, resid=18.0, civic=12.6, office=19.5, studio=12.6, culture=15.0, oldst=7.0, hub=8.4, comm=12.6, lodging=13.2, parking=15.0)


def build():
    ctx, rows = M.run_case(1)
    R = {}
    for g, p, r, a, kind, basis, st, opt in rows:
        R[(p, r)] = dict(g=g, a=a, kind=kind, opt=opt)
    def A(p, r): return R[(p, r)]["a"]
    retail = A("체류 연장", "식음·판매(카페 외 레스토랑·푸드코트)")
    wait = A("모빌리티", "환승·셔틀 대합실·공유모빌리티 보관")
    sp = ASSUME["retail_split"]; osp = ASSUME["office_split"]; dsp = ASSUME["d_split"]
    L = {}
    def comp(lot, name, gfa, kind, floors=None, height=None, cat=None, note=""):
        L.setdefault(lot, []).append(dict(name=name, gfa=gfa, kind=kind, floors=floors or FL[kind], height=height or HT[kind], cat=cat, note=note))
    # 공1 공공업무시설: 본청+의회
    tot_civic = A("공공청사·의회", "본청+의회 청사")
    cnc_ratio = 3351.0 / (17759.0 + 3351.0)
    comp("공1", "본청 청사", tot_civic * (1 - cnc_ratio), "hall", 5, 19.5, "공공업무")
    comp("공1", "의회 청사", tot_civic * cnc_ratio, "hall", 3, 15.0, "공공업무")
    # 주1 공동주택 + 주민 커뮤니티 + 근린시설
    comp("주1", "청년·신혼 주거(공동주택)", A("청년·신혼 주거", "주거(세대+주거 공용)"), "resid", 6, 18.0, "주거")
    comm_rooms = ["주민 커뮤니티홀", "작은도서관", "공동부엌", "보육실", "생활관리실", "법정 주민공동시설 보충(운동·휴게·다목적 등)"]
    comp("주1", "주민 공동시설(커뮤니티홀·도서관·공동부엌·보육실 등)", sum(A("주민 공동시설", r) for r in comm_rooms), "civic", 3, 12.6, "문화·교육·공공")
    comp("주1", "생활편의점·카페(근린생활시설)", A("생활 편의", "생활편의점") + A("생활 편의", "카페(1~3개소)"), "civic", 2, 8.4, "판매·음식")
    # 업1·업2 업무시설
    off_core = [A("업무", "청년 창업 입주사무실"), A("업무", "공유 오피스")]
    off_sup = sum(A("지원", r) for r in ["창업 상담·멘토링실", "직무교육실", "공동회의실", "분야별 협업실(건축·디자인·관광·문화유산)", "공동 작업 쉼터(건축)"])
    off_tot = sum(off_core) + off_sup
    for lot in ("업1", "업2"):
        comp(lot, "청년 업무(창업 입주사무실·공유오피스·지원실)", off_tot * osp[lot], "office", 5, 19.5, "상업·업무")
        comp(lot, "저층 근린상가", retail * sp[lot], "comm", 2, 8.4, "판매·음식")
    # 문4·문5 창작·체험
    res_rooms = [A("창작 레지던시", r) for r in ["개인 작업실", "작가 체류실", "공동 제작공방", "오픈스튜디오(작품 발표)", "작가 교류실", "재료·완성작품 보관실"]]
    exp_rooms = [A("역사·공예 체험관", r) for r in ["철도·원도심 체험전시실", "전통공예 체험실", "문화유산 디지털 기록 체험실", "어린이·가족 체험교실", "체험 결과물 전시실"]]
    for lot in ("문4", "문5"):
        comp(lot, "예술인 레지던시(작업실·체류실·공방·보관)", sum(res_rooms) * dsp[lot], "studio", 3, 12.6, "창조산업")
        comp(lot, "역사·공예 체험관", sum(exp_rooms) * dsp[lot], "culture", 3, 15.0, "문화·교육·공공")
    # 상1 성동시장 연계(근린생활·판매)
    mk = sum(A("시장 접점", r) for r in ["성동시장 상인 공동 쇼케이스", "지역 공예품 전시·판매실", "시장 상품 픽업·배송 거점"])
    comp("상1", "시장 접점(상인 쇼케이스·공예품 판매·픽업)", mk, "comm", 2, 8.4, "판매·음식")
    comp("상1", "식음·판매(시장 연계)", retail * sp["상1"], "comm", 2, 8.4, "판매·음식")
    # 체1 운동시설
    comp("체1", "생활체육시설(다목적체육관·피트니스)", ASSUME["sports_gfa"], "culture", 2, 10.5, "여가·오락·체육", "가정(공식 원단위 없음)")
    # 문1 공연장
    comp("문1", "공연장 350석(무대·분장·로비 포함)", A("3 공연·시민문화시설", "공연장 350석(무대·분장·백스테이지·로비 포함)"), "culture", 2, 19.0, "문화·교육·공공")
    comp("문1", "연습실·시민 발표 다목적실", A("3 공연·시민문화시설", "연습실·리허설실") + A("3 공연·시민문화시설", "시민 발표·강연용 다목적실"), "culture", 2, 9.0, "문화·교육·공공")
    # 문2 구 역사·근대역사 전시관
    old = A("1 구 역사·철도기억관", "구 역사 보존·활용(대합실·승강장 해설·상설전시 포함)")
    comp("문2", "구 역사(존치·근대역사관 리유즈)", old, "oldst", 2, 7.0, "역사유산", "실측 1,403㎡ 존치")
    ann = (A("1 구 역사·철도기억관", "철도 사진·지도·구술기록 아카이브") + A("1 구 역사·철도기억관", "철도 시설물 보존·복원 작업실")
           + sum(A("2 경주 근대역사 전시관", r) for r in ["상설전시(원도심 변천·철도 전후·생활사 3주제)", "순환형 기획전시실", "지역 예술가 전시실", "전시관 공용(로비·화장실 등)"])
           + A("6 운영시설", "전시품 수장고") + A("6 운영시설", "시설 운영실")
           + sum(A("4 문화유산 창작·교육", r) for r in ["문화유산 보존·복원 교육실", "학교·단체 교육실(학교 연계 역사교육실+단체 교육실 통합)", "시민 강좌실"]))
    comp("문2", "근대역사 전시관 별관(전시·아카이브·수장·교육)", ann, "culture", 3, 15.0, "문화·교육·공공")
    # 문3 팝업스토어·상가·공방
    comp("문3", "팝업스토어·상가(식음·판매)", retail * sp["문3"], "comm", 2, 8.4, "판매·음식")
    comp("문3", "공개 공방·지역 공예 제작실", A("4 문화유산 창작·교육", "공개 공방") + A("4 문화유산 창작·교육", "지역 공예 제작실"), "studio", 2, 8.4, "창조산업")
    # 관1 관광지원시설 + 주차전용건축물
    gate = sum(A("5 방문자 관문", r) for r in ["경주 원도심·문화유산 안내센터", "보행코스 출발 안내소", "방문자 라운지·휴게실", "성동시장·황오동 연결 안내 공간", "물품보관·편의시설"])
    comp("관1", "방문자 관문·모빌리티 대합실", gate + wait, "hub", 2, 8.4, "교통·방문자")
    # 주차 소요 (경주시 조례): 문화·집회·판매·업무·운동 100㎡/대, 근생·숙박 200㎡/대, 주거 0.7/1.0대
    stalls = 0.0
    for lot, cs in L.items():
        for c in cs:
            k = c["kind"]
            if k in M.MAIN100: stalls += c["gfa"] / 100.0
            elif k in ("civic", "lodging"): stalls += c["gfa"] / 200.0
            elif k == "resid":
                H = ctx["H"]; hy = H * M.YR; hn = H - hy; stalls += hy * M.PARK_Y + hn * M.PARK_N
    pk_gfa = stalls * ASSUME["stall_gross"]
    comp("관1", "주차전용건축물(조례 소요 %d대)" % round(stalls), pk_gfa, "parking", ASSUME["park_floors"], 15.0, "주차전용건축물")
    return ctx, L, dict(stalls=stalls, pk_gfa=pk_gfa)


if __name__ == "__main__":
    ctx, L, pk = build()
    tot = 0.0
    for lot, cs in L.items():
        g = sum(c["gfa"] for c in cs); tot += g
        print("%-3s GFA %8.0f  footprint %7.0f" % (lot, g, sum(c["gfa"] / c["floors"] if c["kind"] != "oldst" else 1403.0 for c in cs)))
        for c in cs: print("      %-40s %8.0f  %dF %.1fm  %s" % (c["name"][:40], c["gfa"], c["floors"], c["height"], c["cat"]))
    print("total GFA incl parking %.0f | parking stalls %.0f | pk gfa %.0f | program excl. parking %.0f" % (tot, pk["stalls"], pk["pk_gfa"], tot - pk["pk_gfa"]))
