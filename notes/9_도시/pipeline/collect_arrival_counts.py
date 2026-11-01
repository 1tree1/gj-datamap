"""경주시로 들어오는 사람·차량의 수단별 공급측 실측량 — 철도 승하차 · 고속도로 IC 진출 · 항공 · (버스·전세버스 시도 기록).

목적: 설문 기반 수단분담률이 경주 단위로 없으므로, 운영기관이 센 실측 총량(공급측 카운트)으로 수단 구성을 역추정한다.
전부 '관광 목적 미구분 총량'이다 — 시민 통근·통학·업무·화물 포함. 관광객만 따로 센 자료는 없다.
스케일: S3(경주시 전역). 부지(S1) 프로그램 근거로 직접 쓰지 않는다.

  python collect_arrival_counts.py            # fetch + build
  python collect_arrival_counts.py fetch      # 원자료만 (이미 받은 파일은 건너뜀)
  python collect_arrival_counts.py build      # 집계만

원자료  archive/C_data/raw/arrival_counts/   (받은 바이트 그대로 보존, _manifest.json 에 URL·크기·sha256)
집계    archive/C_data/processed/arrival_counts.json

수집원 (2026-10-01 확인)
  철도  data.go.kr 파일 15029727(코레일 역별 승하차 연간)·15144454(코레일 간선 일별 2024)·15108119(KTX 상하행 월별 2010–2023)
        ·15131754(SR SRT 월별역별 승하차 2019.01–2025.09) + KOSIS 357 한국철도통계 LD008·LD009(2016–2024)
        + KOSIS 762 경주시 기본통계 철도수송(교차검증)
  도로  고속도로 공공데이터포털 data.ex.co.kr 파일 — TCS 34 영업소별 교통량(1일 집계·월 파일), 96 요일별 영업소 교통량(연),
        39 전체 영업소간 교통량 매트릭스(일, 표본일), ETC 75 영업소 기준정보(코드표)
  항공  KOSIS 381 항공통계 DT_920005_B001 공항별 통계(포항경주, 월)
  버스  data.go.kr OpenAPI 15142072(고속시외버스·도시철도 이용 OD)·15098522/15098541(TAGO) — 활용신청 전이라 403. 탐침 결과만 기록.

주의
  - API 키는 load_env()로만 읽고 출력·저장하지 않는다. manifest 의 URL 은 키 파라미터를 뺀 공개 URL.
  - data.ex.co.kr 파일 다운로드는 로그인 불요(사이트 goLoginCheck()=true). 활용 설문 필드는 '연구 및 학술분석'만 넣고 인적사항은 비운다.
  - 요청 간 sleep 으로 속도 제한 (ex 포털 1.0s, data.go.kr 0.5s). 총 70여 콜이라 동기 urllib 으로 충분(_common 과 동일 방식).
"""
import os, sys, io, re, csv, json, gzip, time, hashlib, datetime, collections, urllib.request, urllib.parse, http.cookiejar
from _common import load_env, get_json, RAW, PROCESSED, ROOT, _CTX

OUT_RAW = RAW / "arrival_counts"
OUT_RAW.mkdir(parents=True, exist_ok=True)
MANIFEST = OUT_RAW / "_manifest.json"
UA = {"User-Agent": "Mozilla/5.0"}

# 경주 관내 한국도로공사 영업소 (ETC 75 영업소 기준정보 2026-09-30, 가동영업소여부=Y). 주소는 data.go.kr 15085269·15043758.
EX_UNITS = {"135": "경주", "133": "서경주(구 건천)", "706": "남경주", "708": "동경주"}
EX_UNIT_NOTE = {"135": "경부선 · 경주시 서라벌대로 464", "133": "경부선 · 경주시 건천읍 단석로 1805-21 (2026 무인수납 현황에서 '서경주'로 표기)",
                "706": "동해선(부산포항선) · 경주시 외동읍 산업로 2563-38", "708": "동해선(부산포항선) · 경주시 문무대왕면 지저남동길 109-64"}
# 경주 관내 현존 여객역 (2024 코레일 역별 승하차 238개 역 중 경주시 소재)
RAIL_STATIONS = ["경주", "서경주", "안강", "아화"]
TCS_MONTHS = [f"{y}{m:02d}" for y in (2024, 2025) for m in range(1, 13)] + [f"2026{m:02d}" for m in range(1, 9)]
TCS_YEARS_DOW = ["2024", "2025"]

# 관공서의 공휴일에 관한 규정(T1) + 대체·임시공휴일. 코드 내 수기 입력 — 인사혁신처 공고 원문 대조 전.
HOLIDAYS = {
    "2024": ["0101", "0209", "0210", "0211", "0212", "0301", "0410", "0505", "0506", "0515", "0606", "0815", "0916", "0917", "0918", "1001", "1003", "1009", "1225"],
    "2025": ["0101", "0127", "0128", "0129", "0130", "0301", "0303", "0505", "0506", "0603", "0606", "0815", "1003", "1005", "1006", "1007", "1008", "1009", "1225"],
}
DOW_KO = ["월", "화", "수", "목", "금", "토", "일"]


# ───────────────────────── 공통 ─────────────────────────
def _manifest():
    return json.load(open(MANIFEST, encoding="utf-8")) if MANIFEST.exists() else {}


def _record(fname, url, body, **meta):
    m = _manifest()
    m[fname] = {"url": url, "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest(),
                "fetched": datetime.datetime.now().isoformat(timespec="seconds"), **meta}
    MANIFEST.write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")


def _save_raw(fname, body, url, **meta):
    (OUT_RAW / fname).write_bytes(body)
    _record(fname, url, body, **meta)
    print(f"  저장 raw/arrival_counts/{fname}  ({len(body):,} B)")


def _get_bytes(url, headers=None, data=None, opener=None, timeout=180):
    req = urllib.request.Request(url, data=data, headers=headers or UA)
    r = (opener.open(req, timeout=timeout) if opener else urllib.request.urlopen(req, timeout=timeout, context=_CTX))
    return r.read(), r.headers


def _strip_key(url):
    """manifest 용: serviceKey/apiKey 값을 제거한 URL."""
    return re.sub(r"(serviceKey|apiKey|key)=[^&]+", r"\1=***", url)


# ───────────────────────── data.go.kr 파일데이터 ─────────────────────────
def dg_file(did, fname, desc):
    """data.go.kr 파일데이터 현재본 다운로드. contentUrl(atchFileId)은 갱신 때 바뀌므로 매번 상세 페이지에서 읽는다."""
    if (OUT_RAW / fname).exists():
        print(f"  있음 {fname}"); return
    page = _get_bytes(f"https://www.data.go.kr/data/{did}/fileData.do")[0].decode("utf-8", "replace")
    urls = re.findall(r'"contentUrl":\s*"([^"]+)"', page)
    if not urls:
        raise RuntimeError(f"{did} contentUrl 없음 (링크형 데이터일 수 있음)")
    body, h = _get_bytes(urls[0], {**UA, "Referer": f"https://www.data.go.kr/data/{did}/fileData.do"})
    cd = h.get("Content-Disposition", "")
    orig = urllib.parse.unquote(cd.encode("latin-1").decode("utf-8", "replace")).split("filename=")[-1].strip('"') if cd else ""
    _save_raw(fname, body, urls[0], dataset=f"data.go.kr {did}", desc=desc, original_filename=orig)
    time.sleep(0.5)


# ───────────────────────── KOSIS ─────────────────────────
def kosis(fname, org, tbl, params, desc):
    if (OUT_RAW / fname).exists():
        print(f"  있음 {fname}"); return
    k = os.environ["KOSIS_KEY"]
    q = "&".join(f"{a}={b}" for a, b in params.items())
    url = f"https://kosis.kr/openapi/Param/statisticsParameterData.do?method=getList&apiKey={k}&format=json&jsonVD=Y&orgId={org}&tblId={tbl}&{q}"
    rows = get_json(url, retries=2)
    if not isinstance(rows, list):
        raise RuntimeError(f"KOSIS {tbl}: {rows}")
    body = json.dumps(rows, ensure_ascii=False, indent=0).encode("utf-8")
    _save_raw(fname, body, _strip_key(url), dataset=f"KOSIS {org} {tbl}", desc=desc, rows=len(rows))
    time.sleep(0.5)


# ───────────────────────── data.ex.co.kr 파일 ─────────────────────────
class ExPortal:
    """고속도로 공공데이터포털 파일 다운로드 (view → search → log). 로그인 불요."""
    B = "https://data.ex.co.kr"

    def __init__(self):
        self.op = urllib.request.build_opener(urllib.request.HTTPSHandler(context=_CTX), urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))

    def _post(self, path, data, ref=None):
        h = {**UA, "Referer": ref or self.B}
        return _get_bytes(self.B + path, h, urllib.parse.urlencode(data).encode(), self.op)[0]

    def view(self, typ, num):
        _get_bytes(f"{self.B}/portal/fdwn/view?type={typ}&num={num}", UA, None, self.op)

    def fetch(self, typ, num, service_id, cc, sc, fname, ym="", ymd="", year="", desc=""):
        if (OUT_RAW / fname).exists():
            print(f"  있음 {fname}"); return True
        ref = f"{self.B}/portal/fdwn/view?type={typ}&num={num}"
        d = dict(collectType=typ, dataType=num, collectCycle=cc, supplyCycle=sc, dataSupplyDate=ymd,
                 dataSupplyYear=ym[:4], dataSupplyMonth=ym[4:6], dataSupplyYearQ="", dataSupplyQuater="", dataSupplyYearY=year)
        s = json.loads(self._post("/portal/fdwn/search", d, ref) or b"[]")
        if not s:
            print(f"  파일 없음 {typ}{num} {ym or ymd or year}"); return False
        d.update(outFileName=s[0]["outFileName"], deptCd="", regionCd="", genderCd="", userAgeCd="", pouCd="0",
                 deptName="", regionName="", gender="", userAgeName="", pouName="연구 및 학술분석", emailAddress="-", serviceId=service_id)
        body = self._post("/portal/fdwn/log", d, ref)
        time.sleep(1.0)
        if not body:
            print(f"  0바이트 응답 {typ}{num} {ym or ymd or year} (서버 측 거부 — 월 단위 대용량 파일에서 발생)"); return False
        _save_raw(fname, body, ref, dataset=f"data.ex.co.kr {typ} {num}", desc=desc, ex_file=s[0]["outFileName"],
                  standard_date=s[0].get("standardDate", "").strip(), created=s[0].get("createDate"), raw_size=s[0].get("fileSize"))
        return True


def second_weekday(y, m, wd):
    d = datetime.date(y, m, 1)
    first = d + datetime.timedelta(days=(wd - d.weekday()) % 7)
    return first + datetime.timedelta(days=7)


# ───────────────────────── data.go.kr OpenAPI 탐침 ─────────────────────────
PROBES = [
    ("15141028", "한국철도공사_발권/이동유형 통계정보 · 간선열차 역별 승하차(일별)",
     "https://apis.data.go.kr/B551457/issueStatistics/mainLineStationPer", {"pageNo": 1, "numOfRows": 5, "returnType": "json", "cond[stn_nm::EQ]": "경주"}),
    ("15125733", "한국철도공사_열차수송통계정보 · 간선 여객열차 수송실적(일별·역별)",
     "https://apis.data.go.kr/B551457/carriageStatistics/mainLineTravelerTrain", {"pageNo": 1, "numOfRows": 5, "returnType": "json", "cond[stn_nm::EQ]": "경주", "cond[run_ymd::GTE]": "20250801", "cond[run_ymd::LTE]": "20250802"}),
    ("15142072", "국토교통부_고속시외버스·도시철도이용 OD · 월별(도착 시군구=경주)",
     "https://apis.data.go.kr/1613000/ODUsageforExpressIntercityBusesandUrbanRail/getMonthlyODUsageforExpressIntercityBusesandUrbanRailways",
     {"pageNo": 1, "numOfRows": 10, "opr_ym": "202508", "arvl_ctpv_cd": "47", "arvl_sgg_cd": "47130", "dataType": "JSON"}),
    ("15098522", "국토교통부_(TAGO)_고속버스정보 · 터미널 목록",
     "https://apis.data.go.kr/1613000/ExpBusInfo/GetExpBusTrminlList", {"pageNo": 1, "numOfRows": 10, "_type": "json", "terminalNm": "경주"}),
    ("15098541", "국토교통부_(TAGO)_시외버스정보 · 터미널 목록",
     "https://apis.data.go.kr/1613000/SuburbsBusInfo/GetSuberbsBusTrminlList", {"pageNo": 1, "numOfRows": 10, "_type": "json", "terminalNm": "경주"}),
]


def probe_apis():
    """활용신청 여부 확인. 결과는 raw/arrival_counts/api_probe_YYYYMMDD.json (키 미기록)."""
    out = []
    for kn in ("DATA_GO_KR_KEY", "DATA_GO_KR_KEY_CAR"):
        k = os.environ.get(kn)
        if not k: continue
        for did, name, ep, q in PROBES:
            url = f"{ep}?serviceKey={k}&{urllib.parse.urlencode(q)}"
            try:
                j = get_json(url, retries=1)
                res = {"ok": True, "sample": json.dumps(j, ensure_ascii=False)[:400]}
            except Exception as e:
                msg = str(e).replace(k, "***")
                code = re.search(r'"errMsg":\s*"([^"]+)"', msg); rc = re.search(r'"returnReasonCode":\s*"(\d+)"', msg)
                res = {"ok": False, "http": (re.match(r"HTTP (\d+)", msg) or [None, None])[1],
                       "errMsg": code.group(1) if code else msg[:120], "returnReasonCode": rc.group(1) if rc else None}
            out.append({"dataset": did, "name": name, "endpoint": ep, "key_name": kn, **res})
            print(f"  탐침 {did} {kn}: {'OK' if res['ok'] else res.get('errMsg')}")
            time.sleep(0.5)
    fname = f"api_probe_{datetime.date.today():%Y%m%d}.json"
    body = json.dumps(out, ensure_ascii=False, indent=1).encode("utf-8")
    (OUT_RAW / fname).write_bytes(body)
    _record(fname, "(복수 엔드포인트, 키 미기록)", body, desc="data.go.kr OpenAPI 활용신청 여부 탐침")
    return out


# ───────────────────────── fetch ─────────────────────────
def fetch():
    load_env()
    print("[철도] data.go.kr 파일")
    dg_file("15029727", "korail_15029727_station_annual_2024.csv", "한국철도공사_역별 승하차 현황 — 철도통계연보 수록, 2024 연간 누계, 간선여객열차(광역전철·ITX-청춘 제외), 승차·하차 인원")
    dg_file("15144454", "korail_15144454_mainline_daily_2024.csv", "한국철도공사_간선 여객 승하차인원수 — 2024.01.01–12.31 일자별·역별, 승차+하차 합계")
    dg_file("15108119", "korail_15108119_ktx_updown_monthly_2010_2023.csv", "한국철도공사_KTX 상하행 역별 승하차 — 2010.01–2023.12 월별, 상행·하행별 승차·하차 (KTX만)")
    dg_file("15131754", "sr_15131754_srt_station_monthly.csv", "(주)에스알_월별역별 승하차 인원수 — 2019.01–2025.09 SRT 역별 월간 승차·하차")
    print("[철도] KOSIS")
    kosis("kosis_357_LD008_station_total_2022_2024.json", "357", "DT_357001_LD008", {"itmId": "ALL", "objL1": "ALL", "objL2": "ALL", "prdSe": "Y", "newEstPrdCnt": "3"},
          "한국철도통계 역별 여객승하차 실적(총계) — 연간, 하행·상행별 승차·하차·인거리")
    kosis("kosis_357_LD009_station_ktx_srt_2022_2024.json", "357", "DT_357001_LD009", {"itmId": "ALL", "objL1": "ALL", "objL2": "ALL", "prdSe": "Y", "newEstPrdCnt": "3"},
          "한국철도통계 역별 여객 승하차 실적(KTX,SRT) — 연간")
    kosis("kosis_762_J001017_gyeongju_rail_2021_2023.json", "762", "DT_76201_J001017", {"itmId": "ALL", "objL1": "ALL", "objL2": "ALL", "objL3": "ALL", "prdSe": "Y", "newEstPrdCnt": "3"},
          "경주시 기본통계 철도수송 — 역별·월별 승차·하차·여객수입 (교차검증용)")
    print("[항공] KOSIS")
    kosis("kosis_381_B001_pohang_gyeongju_monthly.json", "381", "DT_920005_B001", {"itmId": "T001+T002", "objL1": "A15", "objL2": "ALL", "prdSe": "M", "newEstPrdCnt": "32"},
          "항공통계 공항별 통계 — 포항경주공항 월별 운항(편)·여객(명), 도착·출발")
    print("[도로] data.ex.co.kr")
    ex = ExPortal()
    ex.view("ETC", "75")
    ex.fetch("ETC", "75", "154", "04", "01", "ex_etc75_unit_master_20260930.csv.gz", ymd="20260930",
             desc="영업소 기준정보(C_COMD_영업소) — 영업소코드·영업소명·노선·가동여부")
    ex.view("TCS", "34")
    for ym in TCS_MONTHS:
        ex.fetch("TCS", "34", "144", "04", "02", f"ex_tcs34_unit_daily_{ym}.csv.gz", ym=ym,
                 desc="영업소별 교통량 — 1일 집계·1개월 파일, 입출구·TCS/하이패스·1~6종")
    ex.view("TCS", "96")
    for y in TCS_YEARS_DOW:
        ex.fetch("TCS", "96", "722", "07", "04", f"ex_tcs96_unit_dow_{y}.csv.gz", year=y,
                 desc="요일별 영업소 교통량 — 연간 요일별 합계 (헤더 없음)")
    ex.view("TCS", "39")
    for m in range(1, 13):   # 2025년 월별 둘째 수요일·둘째 토요일 표본
        for wd in (2, 5):
            d = second_weekday(2025, m, wd).strftime("%Y%m%d")
            ex.fetch("TCS", "39", "149", "04", "01", f"ex_tcs39_od_matrix_{d}.csv.gz", ymd=d,
                     desc="전체 영업소간 교통량 매트릭스 — 1일, 출발영업소(행)×도착영업소(열), 총교통량")
    print("[버스·OpenAPI] 활용신청 탐침")
    probe_apis()


# ───────────────────────── build ─────────────────────────
def _read_csv_bytes(p, enc="cp949"):
    b = p.read_bytes()
    if b[:2] == b"\x1f\x8b": b = gzip.decompress(b)
    try:
        s = b.decode(enc)
    except UnicodeDecodeError:
        s = b.decode("utf-8-sig")
    return list(csv.reader(io.StringIO(s)))


def _num(x):
    x = (x or "").strip()
    return int(float(x)) if x not in ("", "-", "...", "NULL") else None


def _is_holiday(ymd):
    return ymd[4:] in HOLIDAYS.get(ymd[:4], [])


def _dow_stats(daily):
    """daily: {YYYYMMDD: value} → 요일 평균, 평일/주말 비, 공휴일 반영 비."""
    by = collections.defaultdict(list); wk, we, wk_nh, we_h = [], [], [], []
    for d, v in daily.items():
        if v is None: continue
        wd = datetime.date(int(d[:4]), int(d[4:6]), int(d[6:])).weekday()
        by[DOW_KO[wd]].append(v)
        (we if wd >= 5 else wk).append(v)
        (we_h if (wd >= 5 or _is_holiday(d)) else wk_nh).append(v)
    avg = lambda a: round(sum(a) / len(a)) if a else None
    r = {"dow_avg": {k: avg(by[k]) for k in DOW_KO}, "n_days": sum(len(v) for v in by.values()),
         "weekday_avg": avg(wk), "weekend_avg": avg(we),
         "weekend_to_weekday": round(avg(we) / avg(wk), 3) if wk and we else None,
         "nonholiday_weekday_avg": avg(wk_nh), "weekend_or_holiday_avg": avg(we_h),
         "weekend_holiday_to_nonholiday_weekday": round(avg(we_h) / avg(wk_nh), 3) if wk_nh and we_h else None}
    return r


def build_rail():
    out = {}
    # ① KOSIS 한국철도통계 연간 (코레일 간선, 역코드 001xxx). 002xxx(SRT)는 아래 이상치 때문에 SR 자체 자료로 대체.
    rows = json.load(open(OUT_RAW / "kosis_357_LD008_station_total_2022_2024.json", encoding="utf-8"))
    ann = collections.defaultdict(lambda: collections.defaultdict(dict))
    for x in rows:
        if x["C1_NM"] not in ("경주", "신경주", "서경주", "안강", "아화") or not x["C1"].startswith("001"): continue
        if x["ITM_NM"] not in ("승차", "하차"): continue
        v = _num(x["DT"]) or 0
        st = x["C1_NM"]
        ann[x["PRD_DE"]][st][x["ITM_NM"]] = ann[x["PRD_DE"]][st].get(x["ITM_NM"], 0) + v
    korail_annual = {y: {st: {"승차": d.get("승차"), "하차": d.get("하차")} for st, d in sorted(v.items()) if (d.get("승차") or d.get("하차"))} for y, v in sorted(ann.items())}
    # SRT 이상치 기록: KOSIS LD008·LD009 의 SRT 신경주는 SR 자체 공개자료의 약 2배(2022–2023) — 원인 미상
    srt_kosis = collections.defaultdict(lambda: collections.defaultdict(int))
    for x in rows:
        if x["C1"].startswith("002") and x["C1_NM"] in ("신경주", "경주") and x["ITM_NM"] in ("승차", "하차"):
            srt_kosis[x["PRD_DE"]][x["ITM_NM"]] += _num(x["DT"]) or 0
    rows9 = json.load(open(OUT_RAW / "kosis_357_LD009_station_ktx_srt_2022_2024.json", encoding="utf-8"))
    ktx = collections.defaultdict(lambda: collections.defaultdict(int)); srt9 = collections.defaultdict(lambda: collections.defaultdict(int))
    for x in rows9:
        if x["C1_NM"] not in ("경주", "신경주") or x.get("C2_NM") not in ("승차", "하차"): continue
        tgt = ktx if x["C1"].startswith("001") else srt9
        tgt[x["PRD_DE"]][x["C2_NM"]] += _num(x["DT"]) or 0
    # ② SR 월별 (T2, SR 자체 공개)
    sr = _read_csv_bytes(OUT_RAW / "sr_15131754_srt_station_monthly.csv")
    srt_m = {}
    for r in sr[1:]:
        if len(r) >= 5 and r[2].strip() in ("신경주", "경주"):
            srt_m[f"{r[0]}{int(r[1]):02d}"] = {"승차": _num(r[3]), "하차": _num(r[4])}
    srt_y = collections.defaultdict(lambda: {"승차": 0, "하차": 0, "months": 0})
    for ym, v in srt_m.items():
        srt_y[ym[:4]]["승차"] += v["승차"] or 0; srt_y[ym[:4]]["하차"] += v["하차"] or 0; srt_y[ym[:4]]["months"] += 1
    # ③ 코레일 2024 역별 연간 파일 (KOSIS 와 동일해야 함 — 검증)
    st24 = {r[0].strip(): {"승차": _num(r[2]), "하차": _num(r[3])} for r in _read_csv_bytes(OUT_RAW / "korail_15029727_station_annual_2024.csv")[1:] if len(r) >= 4}
    check24 = {st: {"file": st24.get(st), "kosis": korail_annual.get("2024", {}).get(st)} for st in RAIL_STATIONS}
    # ④ 코레일 2024 일별 (승+하 합계) → 월 합계, 요일 패턴
    daily = collections.defaultdict(dict)
    for r in _read_csv_bytes(OUT_RAW / "korail_15144454_mainline_daily_2024.csv")[1:]:
        if len(r) >= 3 and r[1].strip() in RAIL_STATIONS:
            daily[r[1].strip()][r[0].replace("-", "")] = _num(r[2])
    rail_daily = {}
    for st, dd in daily.items():
        mon = collections.defaultdict(int)
        for d, v in dd.items(): mon[d[:6]] += v or 0
        rail_daily[st] = {"year_sum_board_plus_alight": sum(v or 0 for v in dd.values()), "monthly_board_plus_alight": dict(sorted(mon.items())), **_dow_stats(dd)}
    # ⑤ KTX 상하행 월별 2022–2023 (경주=신경주 KTX만). 하차 = 하행_하차 + 상행_하차
    ktx_m = {}
    for r in _read_csv_bytes(OUT_RAW / "korail_15108119_ktx_updown_monthly_2010_2023.csv")[1:]:
        if len(r) >= 6 and r[1].strip() in ("경주", "신경주") and r[0][:4] in ("2022", "2023"):
            ktx_m[r[0].replace("-", "")] = {"승차": (_num(r[2]) or 0) + (_num(r[4]) or 0), "하차": (_num(r[3]) or 0) + (_num(r[5]) or 0)}
    # ⑥ 경주시 기본통계 교차검증 (SRT 2021–2022)
    gj = json.load(open(OUT_RAW / "kosis_762_J001017_gyeongju_rail_2021_2023.json", encoding="utf-8"))
    gj_srt = {x["PRD_DE"]: {} for x in gj}
    for x in gj:
        if "SRT" in (x.get("C3_NM") or "") and x.get("C2_NM") in ("승차인원", "하차인원"):
            gj_srt[x["PRD_DE"]][x["C2_NM"]] = _num(x["DT"])
    # ⑦ 유입(하차) 합계 — 코레일(SRT 미포함: 코레일 역별 파일에 수서·동탄·지제 없음) + SR 합산
    alight = {}
    for y, nd in (("2023", 365), ("2024", 366)):
        a = korail_annual.get(y, {})
        src = {f"코레일 {st}": a.get(st, {}).get("하차") for st in RAIL_STATIONS}
        src["SRT 경주"] = srt_y[y]["하차"]
        t = sum(v or 0 for v in src.values())
        alight[y] = {"by_source": src, "total": t, "per_day": round(t / nd)}
    out = {
        "unit": "명(인원)",
        "definition": "역 개찰 기준 승차·하차 인원(발권 실적). '하차'를 경주 유입으로 본다. 경주 관내 역 간 이동(예: 서경주→경주)은 양쪽에 중복 계상되나 규모는 작다. "
                      "KTX 경주역(건천읍, 원도심 약 9 km)은 포항 남부·울산 북부 이용자도 쓴다 → 경주 목적 통행만이 아님.",
        "korail_annual_by_station": korail_annual,
        "ktx_only_annual_경주역": {y: dict(v) for y, v in sorted(ktx.items())},
        "srt_annual_경주역_SR자료": {y: dict(v) for y, v in sorted(srt_y.items())},
        "srt_monthly_경주역": {k: v for k, v in sorted(srt_m.items()) if k >= "202401"},
        "ktx_monthly_경주역_2022_2023": ktx_m,
        "korail_daily_2024": rail_daily,
        "alight": alight,
        "alight_2024": alight["2024"],
        "checks": {
            "korail_2024_file_vs_kosis": check24,
            "korail_excludes_srt": "코레일 역별 승하차 2024 파일(238역)에 SRT 전용역(수서·동탄·평택지제) 없음, KTX 상하행 파일 2022 경주 승차 884,477 = KOSIS LD009 KTX 884,465 → 코레일 집계는 SRT 미포함, 합산이 맞다.",
            "gyeongju_city_stat_flaw": "경주시 기본통계(KOSIS 762) 2022 '신경주①철도공사' 승차 617,899 는 KTX 단독(884,465)보다 작아 성립 불가. '①+②' 1,082,554 가 코레일 총계(1,082,460)와 같다 → 시 통계가 코레일 총계를 SRT 포함으로 오인해 ①을 역산한 것으로 보임. ①값 미사용.",
            "srt_kosis_anomaly": {"kosis_LD008_002xxx": {y: dict(v) for y, v in sorted(srt_kosis.items())},
                                  "kosis_LD009_002xxx": {y: dict(v) for y, v in sorted(srt9.items())},
                                  "sr_own_file": {y: {"승차": v["승차"], "하차": v["하차"]} for y, v in sorted(srt_y.items()) if y in ("2022", "2023", "2024")},
                                  "gyeongju_city_stat": gj_srt,
                                  "verdict": "KOSIS 한국철도통계의 SRT 신경주(002xxx)는 2022·2023(LD008·LD009)과 2024(LD008)에서 SR 자체 공개자료의 약 2배. "
                                             "SR 자료는 경주시 기본통계(2021·2022)와 정확히 일치 → SR 자료 채택, KOSIS SRT 값은 쓰지 않는다."},
        },
    }
    return out


def _tcs_rows(p):
    for r in _read_csv_bytes(p)[1:]:
        if len(r) < 13: continue
        code = r[1].strip()
        if code in EX_UNITS:
            yield r[0].replace("-", ""), code, r[2].strip(), [_num(x) or 0 for x in r[6:13]]   # 1~6종, 총


def build_highway():
    # 일별 × 영업소 × 입출구 × 차종 (TCS+하이패스 합산)
    day = collections.defaultdict(lambda: [0] * 7)   # key (ymd, code, io)
    months_ok = []
    for ym in TCS_MONTHS:
        p = OUT_RAW / f"ex_tcs34_unit_daily_{ym}.csv.gz"
        if not p.exists(): continue
        months_ok.append(ym)
        for ymd, code, io_, v in _tcs_rows(p):
            acc = day[(ymd, code, io_)]
            for i in range(7): acc[i] += v[i]
    cls = ["1종", "2종", "3종", "4종", "5종", "6종(경차)", "총"]
    # 월별 출구(진출)
    mon = collections.defaultdict(lambda: collections.defaultdict(lambda: [0] * 7)); ndays = collections.defaultdict(set)
    for (ymd, code, io_), v in day.items():
        ndays[ymd[:6]].add(ymd)
        if io_ != "1": continue
        for key in (code, "계"):
            a = mon[ymd[:6]][key]
            for i in range(7): a[i] += v[i]
    monthly = {}
    for ym in sorted(mon):
        n = len(ndays[ym])
        monthly[ym] = {"days": n, **{EX_UNITS.get(k, k): {"exit_total": a[6], "exit_per_day": round(a[6] / n), "by_class": dict(zip(cls[:6], a[:6]))} for k, a in mon[ym].items()}}
    # 연간 (2024, 2025 완전 연도)
    annual = {}
    for y in ("2024", "2025"):
        tot = collections.defaultdict(lambda: [0] * 7); ent = collections.defaultdict(int); n = set()
        for (ymd, code, io_), v in day.items():
            if ymd[:4] != y: continue
            n.add(ymd)
            if io_ == "1":
                for key in (code, "계"):
                    for i in range(7): tot[key][i] += v[i]
            else:
                ent[code] += v[6]; ent["계"] += v[6]
        if not n: continue
        nd = len(n)
        annual[y] = {"days": nd, **{EX_UNITS.get(k, k): {
            "exit_total": a[6], "exit_per_day": round(a[6] / nd), "entry_total": ent[k],
            "by_class": dict(zip(cls[:6], a[:6])),
            "share": {"1종+6종(승용·16인이하 승합·2.5t미만 화물·경차)": round((a[0] + a[5]) / a[6], 4),
                      "2종(17~32인 승합·2.5~5.5t 화물)": round(a[1] / a[6], 4),
                      "3종(33인이상 승합=대형버스·5.5t이상 2축 화물)": round(a[2] / a[6], 4),
                      "4~5종(3축이상 화물·특수)": round((a[3] + a[4]) / a[6], 4)}} for k, a in tot.items()}}
    # 요일 패턴 (2025, 출구 합계 및 3종)
    ex_tot = collections.defaultdict(int); ex_c3 = collections.defaultdict(int); ex_c1 = collections.defaultdict(int)
    per_unit = collections.defaultdict(lambda: collections.defaultdict(int))
    for (ymd, code, io_), v in day.items():
        if io_ == "1" and ymd[:4] == "2025":
            ex_tot[ymd] += v[6]; ex_c3[ymd] += v[2]; ex_c1[ymd] += v[0] + v[5]; per_unit[code][ymd] += v[6]
    dow = {"exit_total_4IC": _dow_stats(ex_tot), "exit_class1_6": _dow_stats(ex_c1), "exit_class3": _dow_stats(ex_c3),
           "by_unit_exit_total": {EX_UNITS[c]: _dow_stats(d) for c, d in per_unit.items()}}
    # 요일별 영업소 교통량(96) 교차검증 — 2025 출구 연합계
    chk96 = {}
    p96 = OUT_RAW / "ex_tcs96_unit_dow_2025.csv.gz"
    if p96.exists():
        s96 = collections.defaultdict(int)
        for r in _read_csv_bytes(p96):
            if len(r) >= 15 and r[3].strip() in EX_UNITS and r[4].strip() == "1":
                s96[EX_UNITS[r[3].strip()]] += _num(r[14]) or 0
        chk96 = {u: {"tcs96_dow_file": s96[u], "tcs34_daily_sum": annual.get("2025", {}).get(u, {}).get("exit_total")} for u in EX_UNITS.values()}
    # OD 표본 (39): 경주 4개 IC 도착 차량의 출발지
    od = {"days": [], "internal_share_by_day": {}, "top_origins": []}
    orig = collections.Counter(); internal = 0; total = 0
    for p in sorted(OUT_RAW.glob("ex_tcs39_od_matrix_*.csv.gz")):
        rows = _read_csv_bytes(p)
        hdr = [h.strip() for h in rows[0]]
        cols = [i for i, h in enumerate(hdr) if h in EX_UNITS]
        d_int = d_tot = 0
        for r in rows[1:]:
            if len(r) < max(cols) + 1: continue
            o = r[1].strip(); oname = r[2].strip()
            v = sum(_num(r[i]) or 0 for i in cols)
            d_tot += v
            if o in EX_UNITS: d_int += v
            else: orig[oname] += v
        ymd = p.stem.split("_")[-1].split(".")[0]
        tcs_exit = sum(day[(ymd, c, "1")][6] for c in EX_UNITS)
        od["days"].append(ymd)
        od["internal_share_by_day"][ymd] = {"arrivals_in_matrix": d_tot, "tcs34_exit_same_day": tcs_exit,
                                             "matrix_coverage": round(d_tot / tcs_exit, 3) if tcs_exit else None,
                                             "internal_from_gyeongju_ic": d_int, "share": round(d_int / d_tot, 4) if d_tot else None,
                                             "dow": DOW_KO[datetime.date(int(ymd[:4]), int(ymd[4:6]), int(ymd[6:])).weekday()]}
        internal += d_int; total += d_tot
    if total:
        ext = total - internal
        cov = [v["matrix_coverage"] for v in od["internal_share_by_day"].values() if v["matrix_coverage"]]
        od["internal_share_all_sample_days"] = round(internal / total, 4)
        od["matrix_coverage_mean"] = round(sum(cov) / len(cov), 3)
        od["note"] = ("매트릭스는 도로공사 폐쇄식 구간에서 진입·진출이 짝지어진 통행만 담는다(민자 구간·개방식 진입분 일부 미식별) → 열 합이 TCS34 출구보다 작다. "
                      "출발지는 '진입 영업소'이며 실제 출발 시군구가 아니다(본선 영업소 대동·부산·울산 등 포함).")
        od["top_origins"] = [{"origin_unit": k, "vehicles": v, "share_of_external": round(v / ext, 4)} for k, v in orig.most_common(20)]
    return {
        "unit": "대(차량)",
        "definition": "한국도로공사 TCS·하이패스 영업소 통과 차량. 입출구구분 1=출구(진출)=경주에서 고속도로를 내린 차량. 폐쇄식 영업소라 출구 = 해당 IC에서 끝난 통행. "
                      "본선 통과량(AADT)과 다르다. 국도·지방도로 들어오는 차량(국도 4·7·20·35·28호선, 포항·영천·울산 방면)은 포함되지 않는다. 사람 수가 아니라 차량 수.",
        "units": {EX_UNITS[c]: EX_UNIT_NOTE[c] for c in EX_UNITS},
        "not_in_master": "북경주IC·외동IC — 도로공사 영업소 기준정보(2026-09-30, 민자 포함 전 영업소)에 해당 이름 없음. 남경주IC가 외동읍 소재. 북경주는 미개통·명칭 상이 여부 미확인.",
        "class_definition": "고속도로 통행료 차종: 1종 2축 윤폭279.4mm이하(승용·16인이하 승합·2.5t미만 화물), 2종 2축 윤폭초과·윤거1800mm이하(17~32인 승합·2.5~5.5t 화물), "
                            "3종 2축 윤거1800mm초과(33인이상 승합·5.5t이상 화물), 4종 3축, 5종 4축이상, 6종 경차. → 버스는 2·3종에 화물과 섞여 있어 분리 불가.",
        "months_collected": months_ok,
        "monthly_exit": monthly,
        "annual": annual,
        "dow_2025": dow,
        "check_tcs96_vs_tcs34_2025": chk96,
        "od_sample_2025": od,
    }


def build_air():
    rows = json.load(open(OUT_RAW / "kosis_381_B001_pohang_gyeongju_monthly.json", encoding="utf-8"))
    m = collections.defaultdict(dict)
    for x in rows:
        m[x["PRD_DE"]][f"{x['C2_NM']}_{x['ITM_NM']}"] = _num(x["DT"])
    yr = collections.defaultdict(lambda: collections.defaultdict(int)); yn = collections.Counter()
    for ym, v in m.items():
        yn[ym[:4]] += 1
        for k, x in v.items(): yr[ym[:4]][k] += x or 0
    return {"unit": "명(여객)·편(운항)", "definition": "포항경주공항(포항시 남구) 도착·출발 여객. 경주 방문 목적 미구분, 대부분 포항 수요로 추정 — 경주 유입의 상한 참고값.",
            "monthly": dict(sorted(m.items())), "annual": {y: {**dict(v), "months": yn[y]} for y, v in sorted(yr.items())}}


DATASETS = [
    {"mode": "철도", "name": "한국철도공사_역별 승하차 현황", "provider": "한국철도공사(철도통계연보)", "url": "https://www.data.go.kr/data/15029727/fileData.do",
     "period": "2024 연간(현재본; 2021–2023 과거본 있음)", "unit": "명", "definition": "역별 연간 승차·하차 누계, 간선여객열차(광역전철·ITX-청춘 제외)", "grade": "T2", "status": "수집"},
    {"mode": "철도", "name": "한국철도공사_간선 여객 승하차인원수", "provider": "한국철도공사", "url": "https://www.data.go.kr/data/15144454/fileData.do",
     "period": "2024.01.01–12.31 일별", "unit": "명", "definition": "역별 일별 승차+하차 합계(분리 안 됨)", "grade": "T2", "status": "수집"},
    {"mode": "철도", "name": "한국철도공사_KTX 상하행 역별 승하차", "provider": "한국철도공사", "url": "https://www.data.go.kr/data/15108119/fileData.do",
     "period": "2010.01–2023.12 월별", "unit": "명", "definition": "KTX만, 상행·하행별 승차·하차", "grade": "T2", "status": "수집"},
    {"mode": "철도", "name": "(주)에스알_월별역별 승하차 인원수", "provider": "(주)에스알", "url": "https://www.data.go.kr/data/15131754/fileData.do",
     "period": "2019.01–2025.09 월별", "unit": "명", "definition": "SRT 역별 월간 승차·하차. 경주역은 2025.08까지 '신경주' 표기", "grade": "T2", "status": "수집"},
    {"mode": "철도", "name": "한국철도통계 역별 여객승하차 실적(총계)/(KTX,SRT)", "provider": "한국철도공사 → KOSIS 357 DT_357001_LD008·LD009", "url": "https://kosis.kr (orgId=357)",
     "period": "2016–2024 연간", "unit": "명", "definition": "하행·상행별 승차·하차. SRT(002xxx) 값은 SR 자료의 약 2배 이상치 → 미사용", "grade": "T2", "status": "수집"},
    {"mode": "철도", "name": "경주시 기본통계 철도수송", "provider": "경주시 → KOSIS 762 DT_76201_J001017", "url": "https://kosis.kr (orgId=762)",
     "period": "2011–2023 연간(역별·월별)", "unit": "명·천원", "definition": "역별 승차·하차·여객수입. 교차검증용 — SRT 값은 SR 자료와 일치, 2022 '신경주①철도공사'는 오류(KTX 단독보다 작음)", "grade": "T2", "status": "수집(검증)"},
    {"mode": "고속도로", "name": "영업소별 교통량 (TCS 34)", "provider": "한국도로공사", "url": "https://data.ex.co.kr/portal/fdwn/view?type=TCS&num=34 (data.go.kr 15043774 링크)",
     "period": "2024.01–2026.08 일별(월 파일)", "unit": "대", "definition": "영업소 입구·출구 통과 차량, 1~6종, TCS·하이패스 구분. 출구=진출", "grade": "T2", "status": "수집"},
    {"mode": "고속도로", "name": "요일별 영업소 교통량 (TCS 96)", "provider": "한국도로공사", "url": "https://data.ex.co.kr/portal/fdwn/view?type=TCS&num=96 (data.go.kr 15084035 링크)",
     "period": "2024·2025 연간 요일별 합계", "unit": "대", "definition": "영업소·요일·입출구·차종별 연 합계. TCS 34 일별 합과 교차검증", "grade": "T2", "status": "수집(검증)"},
    {"mode": "고속도로", "name": "전체 영업소간 교통량 매트릭스 (TCS 39)", "provider": "한국도로공사", "url": "https://data.ex.co.kr/portal/fdwn/view?type=TCS&num=39 (data.go.kr 15043754 링크)",
     "period": "2025 표본 24일(월별 둘째 수·토)", "unit": "대", "definition": "출발영업소×도착영업소 총교통량. 경주 IC 간 내부통행 비율·출발지 분포", "grade": "T2", "status": "수집(표본)"},
    {"mode": "고속도로", "name": "영업소 기준정보 (ETC 75)", "provider": "한국도로공사", "url": "https://data.ex.co.kr/portal/fdwn/view?type=ETC&num=75 (data.go.kr 15087176 링크)",
     "period": "2026-09-30", "unit": "-", "definition": "영업소코드↔영업소명 코드표", "grade": "T2", "status": "수집"},
    {"mode": "항공", "name": "항공통계 공항별 통계", "provider": "한국공항공사·국토교통부 → KOSIS 381 DT_920005_B001", "url": "https://kosis.kr (orgId=381)",
     "period": "2024.01–2026.08 월별", "unit": "명·편", "definition": "포항경주공항 도착·출발 여객·운항. 경주 목적 미구분(포항 수요 중심)", "grade": "T2", "status": "수집"},
]
FAILED = [
    {"mode": "버스(고속·시외)", "name": "국토교통부_고속시외버스·도시철도이용 OD (일·월·연, 시군구·읍면동)", "endpoint": "apis.data.go.kr/1613000/ODUsageforExpressIntercityBusesandUrbanRail",
     "dataset": "15142072", "error": "HTTP 403 SERVICE_KEY_IS_NOT_REGISTERED_ERROR (returnReasonCode 30)", "action": "사용자 활용신청 필요 — 경주 도착 고속·시외버스·철도 통행건수를 출발 시군구별로 주는 유일한 공개 API. 최우선"},
    {"mode": "버스(고속)", "name": "국토교통부_(TAGO)_고속버스정보 (터미널·출도착 배차)", "endpoint": "apis.data.go.kr/1613000/ExpBusInfo", "dataset": "15098522",
     "error": "HTTP 403 SERVICE_KEY_IS_NOT_REGISTERED_ERROR (30)", "action": "활용신청 필요 — 운행횟수(배차)만, 이용객 아님"},
    {"mode": "버스(시외)", "name": "국토교통부_(TAGO)_시외버스정보", "endpoint": "apis.data.go.kr/1613000/SuburbsBusInfo", "dataset": "15098541",
     "error": "HTTP 403 SERVICE_KEY_IS_NOT_REGISTERED_ERROR (30)", "action": "활용신청 필요 — 운행횟수(배차)만"},
    {"mode": "철도", "name": "한국철도공사_발권/이동유형 통계정보 · 간선열차 역별 승하차(일별)", "endpoint": "apis.data.go.kr/B551457/issueStatistics/mainLineStationPer", "dataset": "15141028",
     "error": "HTTP 403 SERVICE_KEY_IS_NOT_REGISTERED_ERROR (30)", "action": "활용신청 필요 — 2025–2026 코레일 일별 승하차(승·하 분리)는 이 API에만 있음"},
    {"mode": "철도", "name": "한국철도공사_열차수송통계정보 · 간선 여객열차 수송실적", "endpoint": "apis.data.go.kr/B551457/carriageStatistics/mainLineTravelerTrain", "dataset": "15125733",
     "error": "HTTP 403 SERVICE_KEY_IS_NOT_REGISTERED_ERROR (30)", "action": "활용신청 필요 (15141028 대체 경로)"},
    {"mode": "버스", "name": "한국교통안전공단_지역 간 대중교통 요일별·시간대별·버스유형별 이용인원", "endpoint": "data.go.kr 15119713·15119715·15119717", "dataset": "15119717",
     "error": "수집은 되나 전국 합계만(시군구·터미널 구분 없음)", "action": "경주 단위 불가 — 스케일 혼용 금지로 미사용"},
    {"mode": "버스(고속)", "name": "KOBUS 배차조회 웹", "endpoint": "kobus.co.kr/oprninfo/alcnSrch", "dataset": "-",
     "error": "자동 요청에 오류 페이지 반환", "action": "미사용. 2015 운행횟수는 arrival_transport.json(기본계획 전사)에 있음"},
    {"mode": "고속도로", "name": "전체 영업소간 교통량 매트릭스 월 파일", "endpoint": "data.ex.co.kr TCS 39 (1개월 제공)", "dataset": "-",
     "error": "/portal/fdwn/log 응답 0바이트 (일 파일은 정상)", "action": "일 파일 표본으로 대체"},
    {"mode": "전세(관광)버스", "name": "경주 진입 관광버스 대수 / 보문·불국사 주차장 대형차 입차", "endpoint": "data.go.kr·KOSIS·경주시 공개자료 검색", "dataset": "-",
     "error": "공개 통계 없음 (data.go.kr 경주시 데이터셋 36종·KOSIS 경주시 기본통계 J001xxx 전수 확인)", "action": "경주시 관광정책과·시설관리공단 정보공개청구. 대용 지표 = 고속도로 3종 진출(대형버스+대형화물)의 주말 값"},
]


# 출처 측 갱신일(2026-10-01 확인: data.go.kr catalog dateModified · KOSIS LST_CHN_DE · ex 파일 createDate)과 공간 해상도
DS_META = {
    "한국철도공사_역별 승하차 현황": ("2025-09-04", "역"), "한국철도공사_간선 여객 승하차인원수": ("2025-07-14", "역"),
    "한국철도공사_KTX 상하행 역별 승하차": ("2025-09-03", "역"), "(주)에스알_월별역별 승하차 인원수": ("2026-01-22", "역"),
    "한국철도통계 역별 여객승하차 실적(총계)/(KTX,SRT)": ("KOSIS 2024년 자료", "역"), "경주시 기본통계 철도수송": ("KOSIS 2023년 자료", "역"),
    "영업소별 교통량 (TCS 34)": ("월 파일 익월 15일 전후 생성(2026-08분 확인)", "영업소(IC)"), "요일별 영업소 교통량 (TCS 96)": ("2026-01-02(2025분)", "영업소(IC)"),
    "전체 영업소간 교통량 매트릭스 (TCS 39)": ("일 파일 익월 생성", "영업소 OD"), "영업소 기준정보 (ETC 75)": ("2026-10-01", "영업소"),
    "항공통계 공항별 통계": ("2026-09-08(2026-08분)", "공항"),
}


def build():
    load_env()
    for d in DATASETS:
        d["source_updated"], d["spatial_res"] = DS_META.get(d["name"], (None, None))
    rail = build_rail(); hw = build_highway(); air = build_air()
    probe = sorted(OUT_RAW.glob("api_probe_*.json"))
    probe_res = json.load(open(probe[-1], encoding="utf-8")) if probe else []
    ok_now = sorted({p["dataset"] for p in probe_res if p.get("ok")})
    failed = [f for f in FAILED if f["dataset"] not in ok_now]
    # 수단별 요약 (단위가 다르다: 철도·항공=명, 고속도로=대)
    h25 = hw["annual"].get("2025", {}).get("계", {})
    summary = {
        "철도_하차(명)": {y: {"연간": v["total"], "일평균": v["per_day"], "구성": v["by_source"]} for y, v in rail["alight"].items()},
        "철도_경주역_2024_주말/평일(승+하)": rail["korail_daily_2024"].get("경주", {}).get("weekend_to_weekday"),
        "SRT_경주역_2025.01–09_하차(명)": sum(v["하차"] or 0 for k, v in rail["srt_monthly_경주역"].items() if k.startswith("2025")),
        "고속도로_4IC_2025_진출(대)": {"연간": h25.get("exit_total"), "일평균": h25.get("exit_per_day"), "차종구성": h25.get("share"),
                                  "주말/평일": hw["dow_2025"]["exit_total_4IC"]["weekend_to_weekday"],
                                  "주말·공휴일/비공휴평일": hw["dow_2025"]["exit_total_4IC"]["weekend_holiday_to_nonholiday_weekday"]},
        "항공_포항경주_도착(명)": {y: v.get("도착_여객") for y, v in air["annual"].items()},
        "버스": "공개 실측 미확보 — 15142072 활용신청 후 재실행",
        "전세버스": "공개 통계 없음 — 고속도로 3종 진출의 주말 값이 상한 대용",
    }
    out = {
        "title": "경주시 유입 수단별 공급측 실측량 (철도 승하차·고속도로 IC 진출·항공)",
        "generated": datetime.date.today().isoformat(),
        "scale": "S3 — 경주시 전역. S1 부지 프로그램 근거로 직접 쓰지 않는다.",
        "scope_note": "전부 관광 목적 미구분 총량(시민 통근·통학·업무·화물 포함). 철도·항공은 사람, 고속도로는 차량 — 수단 구성 역추정 시 재차인원(차종별) 가정이 별도로 필요.",
        "crs": "해당 없음(비공간 통계)",
        "summary": summary,
        "rail": rail, "highway": hw, "air": air,
        "bus": {"status": "실패 — 활용신청 필요", "prior": "2015 고속버스 일 운행 약 91회(기본계획 p.202, KOBUS) → processed/arrival_transport.json"},
        "datasets": DATASETS,
        "failed": failed,
        "api_probe": [{k: p.get(k) for k in ("dataset", "key_name", "ok", "http", "errMsg", "returnReasonCode")} for p in probe_res],
        "proxy_for": {"고속도로 3종 진출": "대형버스(전세·고속·시외) + 5.5t 이상 2축 화물 — 버스 단독 아님",
                      "철도 하차": "경주 관내 역 하차 = 경주 유입 사람 수의 근사 (경주역은 포항·울산 일부 이용자 포함)"},
    }
    p = PROCESSED / "arrival_counts.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"  저장 {p.relative_to(ROOT)}")
    # 콘솔 요약
    print(f"\n철도 2024 하차 {rail['alight_2024']['total']:,}명 (일 {rail['alight_2024']['per_day']:,}) {rail['alight_2024']['by_source']}")
    for y, v in hw["annual"].items():
        print(f"고속도로 {y} 4IC 진출 {v['계']['exit_total']:,}대 (일 {v['계']['exit_per_day']:,})  " + "  ".join(f"{u} {v[u]['exit_per_day']:,}" for u in EX_UNITS.values() if u in v))
    d = hw["dow_2025"]["exit_total_4IC"]
    print(f"  2025 요일평균 {d['dow_avg']}  주말/평일 {d['weekend_to_weekday']}  주말공휴/비공휴평일 {d['weekend_holiday_to_nonholiday_weekday']}")
    print(f"  OD 표본 내부통행 비율 {hw['od_sample_2025'].get('internal_share_all_sample_days')}")
    print(f"항공 포항경주 도착 {summary['항공_포항경주_도착(명)']}")
    return out


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd in ("fetch", "all"): fetch()
    if cmd in ("build", "all"): build()
