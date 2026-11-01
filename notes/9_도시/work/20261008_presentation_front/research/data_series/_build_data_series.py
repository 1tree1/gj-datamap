"""발표 앞부분(현황 파트) 차트용 데이터 계열 S01~S18 CSV 생성.

실행: export PYTHONUTF8=1 PYTHONIOENCODING=utf-8
      <venv>/python.exe _build_data_series.py
원칙: 값은 archive/·work/·원문 PDF에서 읽거나 계산한 것만 쓴다. 손으로 옮긴 값(전사)은 주석에 출처 쪽을 적었다.
출력: 같은 폴더의 S##_*.csv (UTF-8, BOM 없음), MANIFEST.csv
원본은 읽기만 한다.
"""
import ast
import collections
import csv
import json
import math
import re
import statistics
import sys
import warnings
from pathlib import Path

from pyproj import Transformer
from shapely.geometry import Point, shape
from shapely.ops import transform as shp_transform
from shapely.ops import unary_union

warnings.filterwarnings("ignore")

ROOT = Path("C:/Users/OFFICE/Desktop/9_도시")
ARC = ROOT / "archive"
RAW = ARC / "C_data" / "raw"
PROC = ARC / "C_data" / "processed"
DER = ARC / "90_derived"
OUT = ROOT / "work" / "20261008_presentation_front" / "research" / "data_series"

MANIFEST = []  # (file, 설명, 원자료 경로, 쪽/연도, 비고)


def rel(p):
    return str(Path(p)).replace("\\", "/").replace(str(ROOT).replace("\\", "/") + "/", "")


def jload(p):
    return json.load(open(p, encoding="utf-8"))


def w(name, header, rows, desc, src, period, note=""):
    """CSV 저장(UTF-8, BOM 없음) + 매니페스트 기록."""
    p = OUT / name
    with open(p, "w", encoding="utf-8", newline="") as f:
        cw = csv.writer(f)
        cw.writerow(header)
        for r in rows:
            assert len(r) == len(header), (name, len(r), len(header), r)
            cw.writerow(["" if v is None else v for v in r])
    MANIFEST.append((name, desc, src, period, note))
    print(f"  {name}: {len(rows)}행")


def pct(a, b, nd=1):
    return round((a - b) / b * 100, nd)


# ---------------------------------------------------------------- 공통 로드
POP = jload(PROC / "pop_emd_table.json")
KO5 = jload(RAW / "kosis_pop_emd_5age.json")
HW = jload(PROC / "hwango_report.json")
SRC_KOSIS = "KOSIS DT_1B04005N 행정안전부 주민등록인구(2011년~)"


# ================================================================ S01
def s01():
    y = POP["47130"]["yearly"]
    years = sorted(y)
    rows = []
    prev = None
    for yr in years:
        v = y[yr]
        rows.append([yr, "연간(연말 기준 추정, 파일에 기준월 미표기)", v, None if prev is None else v - prev,
                     None if prev is None else pct(v, prev), pct(v, y["2015"]) if int(yr) >= 2015 else None,
                     SRC_KOSIS, "T2",
                     "경주시 합계 행(47130) 값. 2015→2025 증감률 -6.1%(정리본 '10년 전 대비')가 이 계열"])
        prev = v
    v = POP["47130"]["sex"]["total"]
    rows.append(["2026-08", "월(2026-08)", v, None, None, pct(v, y["2015"]),
                 SRC_KOSIS + " 2026-08(최종수정 2026-09-02)", "T2",
                 "2015년(연말) 대비 -6.6%이나 정리본의 -6.1%는 2015→2025. 시점 혼용 주의"])
    w("S01_경주시_주민등록인구_연도별.csv",
      ["기준", "구분", "총인구_명", "전년대비_증감_명", "전년대비_증감률_퍼센트", "2015년대비_증감률_퍼센트", "출처", "등급", "비고"],
      rows, "경주시 주민등록 총인구 2011~2025 연간 + 2026-08",
      "archive/C_data/processed/pop_emd_table.json(47130.yearly) ← raw/kosis_pop_emd_yearly.json, raw/kosis_pop_emd_5age.json", "2011~2026-08",
      "아카이브에 연도별 연령 3구분 없음(2026-08만). 웹리포트 report_stats.json의 pop_actual(읍면동 합)은 2011~2020이 4천 명 낮아 쓰지 않음")

    # S01b 5세별(경주시 + 4개 동) 2026-08
    def ko(code):
        d = collections.defaultdict(dict)
        for r in KO5:
            if r["C1"] == code and r["C2"] != "0":
                d[r["C2_NM"]][{"T2": "계", "T3": "남", "T4": "여"}[r["ITM_ID"]]] = int(r["DT"])
        return d

    def lo(k):
        return int(k.replace("+", "").split("-")[0].strip().replace("세", ""))

    names = {"47130": "경주시", "4713053000": "황오동(현, 옛 중부동 포함)", "4713057000": "황남동", "4713055000": "성건동", "4713060500": "월성동"}
    rows = []
    for code, nm in names.items():
        d = ko(code)
        tot = sum(v["계"] for v in d.values())
        for k in sorted(d, key=lo):
            v = d[k]
            rows.append([nm, "2026-08", k.replace(" ", ""), v["남"], v["여"], v["계"], round(v["계"] / tot * 100, 2),
                         SRC_KOSIS + " 2026-08", "T2"])
    w("S01b_5세별_인구_2026-08_경주시_원도심4동.csv",
      ["지역", "기준", "연령_5세구간", "남_명", "여_명", "계_명", "비율_퍼센트", "출처", "등급"],
      rows, "5세별 주민등록 인구(인구 피라미드용) 경주시·황오·황남·성건·월성, 2026-08",
      "archive/C_data/raw/kosis_pop_emd_5age.json", "2026-08", "황오동은 2025년 행정동 통합 후 값(옛 중부동 포함)")

    # S01c 3구분
    rows = []
    for code, nm in names.items():
        d = ko(code)
        tot = sum(v["계"] for v in d.values())
        a = sum(v["계"] for k, v in d.items() if lo(k) <= 10)          # 0-14
        b = sum(v["계"] for k, v in d.items() if 15 <= lo(k) <= 60)    # 15-64
        c = sum(v["계"] for k, v in d.items() if lo(k) >= 65)
        yth = sum(v["계"] for k, v in d.items() if 20 <= lo(k) <= 35)  # 20-39
        y2034 = sum(v["계"] for k, v in d.items() if 20 <= lo(k) <= 30)
        rows.append([nm, "2026-08", tot, a, round(a / tot * 100, 1), b, round(b / tot * 100, 1), c, round(c / tot * 100, 1),
                     yth, round(yth / tot * 100, 1), y2034, round(y2034 / tot * 100, 1), SRC_KOSIS + " 2026-08(5세별 합산)", "T2",
                     "연령 구분은 5세 구간 합(0~14/15~64/65+, 20~39, 20~34)"])
    w("S01c_연령3구분_2026-08_경주시_원도심4동.csv",
      ["지역", "기준", "총인구_명", "0~14세_명", "0~14세_퍼센트", "15~64세_명", "15~64세_퍼센트", "65세이상_명", "65세이상_퍼센트",
       "20~39세_명", "20~39세_퍼센트", "20~34세_명", "20~34세_퍼센트", "출처", "등급", "비고"],
      rows, "연령 3구분·20~39세·20~34세, 2026-08", "archive/C_data/raw/kosis_pop_emd_5age.json", "2026-08")

    # S01d 65+ 장기(통계연보, 2030 도시기본계획 인쇄쪽 31 · 123)
    rs = jload(PROC / "report_stats.json")
    rows = []
    ag = rs["aging"]
    for yr, p, n in zip(ag["years"], ag["pct65"], ag["n65"]):
        rows.append([yr, "실적(경주시 통계연보)", p, int(n), "2030 경주도시기본계획 인쇄쪽 31 「노인인구(65세 이상) 변화」", "T1(문서 전사)",
                     "통계연보 기준. KOSIS 주민등록(2026-08)과 정의·기준이 달라 이어 붙이지 말 것"])
    rows.append(["2026-08", "실적(주민등록 KOSIS)", 30.0, 72747, "KOSIS DT_1B04005N 2026-08", "T2", "2014~2025 연도별 65세 이상 비율은 아카이브에 없음(미확보)"])
    pj = rs["age_projection"]
    for yr, p in zip(pj["years"], pj["p65"]):
        rows.append([yr.replace("년", ""), "계획추정(자연적증가, 외국인 제외)", p, None, "2030 경주도시기본계획 인쇄쪽 123 「연령별·성별 계획인구 설정」", "T1(계획 추정값)", "실적 아님"])
    w("S01d_65세이상_비율_장기_통계연보와_계획추정.csv",
      ["연도", "구분", "65세이상_퍼센트", "65세이상_명", "출처", "등급", "비고"], rows,
      "65세 이상 비율 장기 참고(2004~2013 통계연보, 2026-08 주민등록, 2030 계획 추정). 서로 다른 출처라 한 선으로 잇지 말 것",
      "archive/C_data/processed/report_stats.json(aging, age_projection)", "2004~2013, 2026-08, 2013~2030(추정)")


# ================================================================ S02
def s02():
    src = open(ROOT / "pipeline" / "pipeline" / "build_tourist_viz.py", encoding="utf-8").read()

    def grab(name):
        i = src.index(name + " = {")
        j = src.index("{", i)
        depth = 0
        for k in range(j, len(src)):
            if src[k] == "{":
                depth += 1
            elif src[k] == "}":
                depth -= 1
                if depth == 0:
                    return ast.literal_eval(src[j:k + 1])

    ann = grab("ANNUAL")
    daily = jload(RAW / "visitors_gyeongju_daily.json")
    api = collections.defaultdict(lambda: [0.0, 0.0, 0])
    for k, v in daily.items():
        if v.get("외지인") is not None:
            api[k[:4]][0] += v["외지인"]
            api[k[:4]][1] += v.get("외국인") or 0
            api[k[:4]][2] += 1
    rows = []
    for i, yr in enumerate(ann["years"]):
        o = ann["outsider"][i]
        f = ann["foreign"][i]
        chk = None
        if yr == "2025":
            chk = round(api["2025"][0])
        rows.append([yr, o, round(o / (366 if yr == "2024" else 365)), f, chk,
                     "한국관광 데이터랩(KT 이동통신 기반 추정) 외지인 연인원. 2023·2024는 경주시 보도자료(2025-01·2026-01)와 원값 대조, 2025는 보도(2026-01-12)와 일치, 2019·2022는 스크립트 전사값(보도 대조 없음)",
                     "T2", "연인원(같은 사람을 날짜마다 다시 셈), 총량 아님" + ("; 보도 '4,709만'은 내림, 반올림하면 4,710만" if yr == "2024" else "")
                     + ("; 일별 API 합계(2025-01-01~12-31, 365일)로 재현됨" if yr == "2025" else "")])
    w("S02_경주시_외지인방문_연인원_연도별.csv",
      ["연도", "외지인_연인원_명", "일평균_명(연인원÷일수)", "외국인_연인원_명(근사)", "일별API합계_검증_명", "정의", "등급", "비고"],
      rows, "경주시 외지인(내국인 관광객) 방문 연인원 2019·2022~2025",
      "pipeline/pipeline/build_tourist_viz.py(ANNUAL 딕셔너리, 경주시 보도자료 대조값) + archive/C_data/raw/visitors_gyeongju_daily.json(2025 합계 검증)",
      "2019, 2022~2025", "2024=47,098,236→2025=50,203,225 (+%.1f%%). 연도별 값은 스크립트 전사; 2025는 일별 API 합계로 직접 확인" % pct(ann["outsider"][4], ann["outsider"][3]))

    s = jload(PROC / "visitors_gyeongju_summary.json")
    rows = []
    for m in sorted(s["monthly"]):
        v = s["monthly"][m]
        rows.append([f"{m[:4]}-{m[4:]}", v["days"], v["외지인"], round(v["외지인"] / v["days"]), v["외국인"], round(v["외국인"] / v["days"]),
                     "Y" if v["완전한달"] else "N(2026-08-01~18만)",
                     "한국관광 데이터랩 DataLabService/locgoRegnVisitrDDList 일별 합산(KT 이동통신 추정)", "T2"])
    w("S02b_경주시_외지인방문_월별_2024-09_2026-08.csv",
      ["월", "집계일수", "외지인_연인원_명", "외지인_일평균_명", "외국인_연인원_명", "외국인_일평균_명", "완전한달", "출처", "등급"],
      rows, "경주시 외지인·외국인 월별 방문 연인원(일별 API 합산)",
      "archive/C_data/processed/visitors_gyeongju_summary.json(monthly) ← raw/visitors_gyeongju_daily.json", "2024-09~2026-08(18일)",
      "2024-01~08 월별은 미확보(수집 범위 2024-09-01~). 정의: 외지인=경주시 거주자 아닌 내국인")


# ================================================================ S03
def s03():
    t = POP
    y = t["4713053000"]["yearly_raw"]      # 황오동 단독(2025는 통합 후)
    j = json.load(open(RAW / "kosis_pop_emd_yearly_중부동.json", encoding="utf-8"))
    jb = {r["PRD_DE"]: int(r["DT"]) for r in j}
    rows = []
    base = None
    for yr in sorted(y):
        a = y[yr]
        b = jb.get(yr)
        tot = a + b if b is not None else a
        if yr == "2015":
            base = tot
        rows.append([yr, a, b, tot, pct(tot, base) if base and int(yr) >= 2015 else None,
                     "황오동(구)+중부동(구) 합산" if b is not None else "황오동(현, 2025 행정동 통합 후 — 옛 중부동 포함)",
                     SRC_KOSIS, "T2"])
    v = t["4713053000"]["sex"]["total"]
    rows.append(["2026-08", v, None, v, pct(v, base), "황오동(현, 옛 중부동 포함), 월 기준", SRC_KOSIS + " 2026-08", "T2"])
    w("S03_황오동_주민등록인구_연도별_중부동합산.csv",
      ["기준", "황오동_명(연도별: 구 황오동 단독, 2025·2026-08: 통합 후)", "중부동(구)_명", "황오동+중부동_합산_명", "2015년대비_증감률_퍼센트", "범위_정의", "출처", "등급"],
      rows, "황오동 주민등록 인구(옛 중부동 합산) 2011~2025, 2026-08. 정리본 -32.7% = 2015→2025 합산 기준",
      "archive/C_data/processed/pop_emd_table.json(4713053000.yearly_raw) + raw/kosis_pop_emd_yearly_중부동.json", "2011~2026-08",
      "2025년 황오동 값(9,662)은 중부동 통합 후. 2024 이전 '황오동 단독' 열과 이어 읽으면 +70% 점프처럼 보임")

    hp = HW["pop_hwango"]
    ages = hp["age"]
    keys = list(ages)
    rows = []
    for i, yr in enumerate(hp["years"]):
        tot = hp["total"][i]
        a = sum(ages[k][yr] for k in ["0~4", "5~9", "10~14"])
        b = sum(ages[k][yr] for k in ["15~19", "20~24", "25~29", "30~34", "35~39", "40~44", "45~49", "50~54", "55~59", "60~64"])
        c = tot - a - b
        n2039 = sum(ages[k][yr] for k in ["20~24", "25~29", "30~34", "35~39"])
        n75 = sum(ages[k][yr] for k in ["75~79", "80~84", "85~89", "90~94", "95~99", "100+"])
        assert n2039 == hp["n_20_39"][i], (yr, n2039)
        assert n75 == hp["n_75"][i], (yr, n75)
        rows.append([yr, tot, a, b, c, round(c / tot * 100, 1), n2039, round(n2039 / tot * 100, 1), n75, hp["share_65"][i],
                     "황오동(구, 옛 중부동 제외)", "행안부 주민등록(각 연도 12월, 2025는 7월)을 보고서가 인용 · 보고서 인쇄쪽 81", "T2"])
    w("S03b_황오동_연령구조_2018_2025.07_보고서.csv",
      ["기준", "총인구_명", "0~14세_명", "15~64세_명", "65세이상_명", "65세이상_퍼센트", "20~39세_명", "20~39세_퍼센트", "75세이상_명", "보고서_65세이상_퍼센트_대조",
       "범위_정의", "출처", "등급"],
      rows, "황오동(구) 연령 구조 2018→2025.07. 20~39세 1,414→787(-44.3%), 65세 이상 28.3→42.2%. 범위가 옛 황오동 단독이라 -32.7%(중부동 합산)와 범위 다름",
      "archive/C_data/processed/hwango_report.json(pop_hwango) ← 황오동 모니터링 보고서(2025.09) 인쇄쪽 81 (PDF 89쪽)", "2018~2025.07",
      "합계·20~39·75+는 5세 구간에서 재계산해 보고서 값과 일치 확인")

    rows = []
    for code, nm in [("4713053000", "황오동(현, 옛 중부동 포함)"), ("4713057000", "황남동"), ("4713055000", "성건동"), ("4713060500", "월성동"), ("47130", "경주시")]:
        d = t[code]
        yy = d["yearly"]
        rows.append([nm, yy["2015"], yy["2025"], d["chg_10y_pct"], d["sex"]["total"], d["pct_65"], d["pct_20_39"],
                     "2015·2025 연말, 65+·20~39는 2026-08", SRC_KOSIS, "T2"])
    w("S03c_원도심4동_인구비교_10년변화_2026-08.csv",
      ["지역", "2015_명", "2025_명", "10년변화_퍼센트(2015→2025)", "2026-08_명", "65세이상_퍼센트_2026-08", "20~39세_퍼센트_2026-08", "기준", "출처", "등급"],
      rows, "황오·황남·성건·월성 인구 10년 변화와 연령 비율 비교", "archive/C_data/processed/pop_emd_table.json", "2015~2026-08",
      "황오동 -32.7%는 옛 중부동 합산(2015 14,359). 성건동은 대학가라 20~39세 비율이 높음")

    rows = []
    for code, nm in [("4713053000", "황오동(현)"), ("4713057000", "황남동"), ("4713055000", "성건동"), ("4713060500", "월성동")]:
        yy = t[code]["yearly"]
        for yr in sorted(yy):
            rows.append([nm, yr, yy[yr], "황오동은 2011~2024 옛 중부동 합산, 2025 통합 후" if code == "4713053000" else "", SRC_KOSIS, "T2"])
    w("S03d_원도심4동_인구_연도별.csv", ["지역", "연도", "인구_명", "비고", "출처", "등급"], rows,
      "원도심 4개 동 연도별 인구 2011~2025(꺾은선용)", "archive/C_data/processed/pop_emd_table.json", "2011~2025")


# ================================================================ S04
def s04():
    p = DER / "gj_decline_diagnosis_2022_by_dong.csv"
    lines = open(p, encoding="utf-8-sig").read().splitlines()
    comment = lines[0]
    rd = csv.DictReader(lines[1:])
    rows = []
    focus = {"황오동", "중부동", "성건동", "황남동"}
    for r in rd:
        m = re.match(r"([\d.]+)%\s*(감소|증가)", r["인구_과거대비"])
        popv = (-1 if m.group(2) == "감소" else 1) * float(m.group(1))
        m2 = re.match(r"([\d.]+)%\s*(감소|증가)", r["사업체_과거대비"]) if r["사업체_과거대비"] else None
        bizv = None if not m2 else (-1 if m2.group(2) == "감소" else 1) * float(m2.group(1))
        rows.append([r["행정구역"], "Y" if r["행정구역"] in focus else "", popv, r["인구_최근5년"], bizv, r["사업체_최근5년"] or "",
                     float(r["노후건축물비율(20년↑)"].rstrip("%")), r["법정기준충족"],
                     "경주시 도시재생 전략계획(변경) 최종보고서 2022.01 인쇄쪽 251 (PDF 261쪽)", "T1(승인계획 부속)",
                     "'과거대비' 기준연도는 원문 미기재. 2022년 당시 행정동(황오동·중부동 분리)"])
    w("S04_도시재생_법정쇠퇴진단_2022_행정동별.csv",
      ["행정구역", "원도심4동_표시", "인구_과거대비_증감률_퍼센트", "인구_최근5년", "사업체_과거대비_증감률_퍼센트", "사업체_최근5년", "노후건축물비율_20년이상_퍼센트",
       "법정기준충족", "출처", "등급", "비고"],
      rows, "도시재생 법정 쇠퇴진단(2022) 23개 행정구역. 황오동 인구 -43.0%·노후 87.9% (전략계획 원문 쪽 대조 완료)",
      "archive/90_derived/gj_decline_diagnosis_2022_by_dong.csv ← 22-0124) 경주시 도시재생전략계획 최종보고서.pdf PDF 261쪽(인쇄쪽 251)", "2022.01 고시 기준(기준연도 미기재)",
      "법정 기준: 인구 과거대비 20% 이상 감소 또는 최근 5년 중 3년 연속 감소 / 사업체 동일 / 노후건축물 50% 이상(표 머리글 기준)")


# ================================================================ S05
def s05():
    s = HW["series"]
    yrs = s["years"]
    rows = []
    for i, yr in enumerate(yrs):
        rows.append([yr] + [s["site"][k][i] for k in ["pop", "hh", "biz", "emp", "house"]] + [s["dong"][k][i] for k in ["pop", "hh", "biz", "emp", "house"]]
                    + ["SGIS 100m 격자(국가지점번호 '마마' 블록) 32셀 = 황오동 원도심 활성화구역(보고서 정의) / 황오동(구 행정동, 중부동 제외)",
                       "황오동 모니터링 보고서(2025.09) 인쇄쪽 10~12·64", "T2",
                       "2020 사업체 급증(격자 1,028·동 1,782)은 조사방식 변경(보고서 주). 종합성과지표표(인쇄쪽 64)의 2020 사업체는 '-'" if yr == "2020" else ""])
    w("S05_황오동_모니터링격자32셀_2018_2023.csv",
      ["연도", "격자32셀_인구_명", "격자32셀_가구", "격자32셀_사업체_개", "격자32셀_종사자_명", "격자32셀_주택_호",
       "황오동전체(구)_인구_명", "황오동전체(구)_가구", "황오동전체(구)_사업체_개", "황오동전체(구)_종사자_명", "황오동전체(구)_주택_호", "범위_정의", "출처", "등급", "비고"],
      rows, "황오동 도시재생 사업지 격자 32셀 5지표 2018~2023(+황오동 전체 비교). 정리본 -14.4/-2.9/-23.1/-12.6% 재현",
      "archive/C_data/processed/hwango_report.json(series) · hwango_grid_4326.geojson ← 보고서 PDF 인쇄쪽 10~12 (PDF 18~20쪽)", "2018~2023",
      "황오동 전체 종사자는 -4.8%(6,192→5,893)로 격자 -23.1%와 크게 다름: '고용 선행' 해석은 사업지 32셀 한정")
    rows = []
    for lab, key in [("인구", "pop"), ("가구", "hh"), ("사업체", "biz"), ("종사자", "emp"), ("주택", "house")]:
        a = s["site"][key]
        b = s["dong"][key]
        rows.append([lab, a[0], a[-1], pct(a[-1], a[0]), b[0], b[-1], pct(b[-1], b[0]), "2018→2023", "T2"])
    w("S05b_격자32셀_증감요약_2018_2023.csv",
      ["지표", "격자32셀_2018", "격자32셀_2023", "격자32셀_증감률_퍼센트", "황오동전체(구)_2018", "황오동전체(구)_2023", "황오동전체(구)_증감률_퍼센트", "기간", "등급"],
      rows, "격자 32셀과 황오동(구) 전체의 2018→2023 증감 비교", "archive/C_data/processed/hwango_report.json(series)", "2018→2023",
      "정리본 값(인구 -14.4, 사업체 -2.9, 종사자 -23.1, 주택 -12.6)은 격자 32셀 값")

    k = HW["kpi"]
    rows = []
    for i, yr in enumerate(k["years"]):
        if k["footfall"][i] is not None:
            rows.append([yr, k["footfall"][i], "보고서 종합성과지표(인쇄쪽 63): 소상공인365 주요 상권 일평균 유동인구" + ("; 2023은 황오동 값×0.504 보정(보고서 주2)" if yr == "2023" else ""),
                         "황오동 모니터링 보고서 인쇄쪽 63", "T2(통신사 추정, 보고서 전사)"])
    rows.append(["2025-06~2026-06(13개월 평균)", 22874, "같은 32셀을 소상공인365에서 재추출한 13개월 평균(2025.06~2026.06)", "work/20260920_소상공인365_유동인구_재추출.md · footfall_sbiz365_summary.csv", "T2(재추출)"])
    rows.append(["2026-06(단월)", 22092, "같은 32셀 2026-06 일평균", "archive/C_data/processed/footfall_sbiz365_monthly.csv", "T2(재추출)"])
    w("S05c_황오동_유동인구_보고서2020_2024와_재추출.csv",
      ["기준", "일평균_유동인구_명", "정의", "출처", "등급"], rows,
      "황오동 사업지 유동인구(통신사 추정): 보고서 2020~2024와 재추출 13개월 평균. 정리본 -13.8% = 26,536→22,874(출처가 다른 두 값의 비교)",
      "archive/90_derived/hwango_kpi_2018_2024.csv, footfall_sbiz365_summary.csv", "2020~2024, 2025.06~2026.06",
      "-13.8% = (22,874-26,536)/26,536. 2020은 보고서 전사값, 2025.06~2026.06은 재추출값이라 같은 방식이라는 보장은 '2024 보고서값 22,646과 같은 자리'라는 간접 확인뿐")


# ================================================================ S06
def s06():
    k = HW["kpi"]
    rows = []
    cmp_ = k["compare"]
    for lab, key_s, key_c in [("황오동 사업대상지", k["startups"], k["closures"]), ("황오동(행정동)", cmp_["황오동"]["startups"], cmp_["황오동"]["closures"]),
                              ("경주시", cmp_["경주시"]["startups"], cmp_["경주시"]["closures"]), ("경상북도", cmp_["경상북도"]["startups"], cmp_["경상북도"]["closures"])]:
        for i, yr in enumerate(k["years"]):
            rows.append([lab, yr, key_s[i], key_c[i], key_s[i] - key_c[i],
                         "보고서 원자료(행안부 지방행정인허가데이터 2025-05-31, localdata 전 업종)",
                         "2024 대상지 창업 70·폐업 66에는 축제 임시영업 27건씩 포함(S06b 참조)" if (lab == "황오동 사업대상지" and yr == "2024") else ""])
    w("S06_황오동_창업폐업_2018_2024_보고서원값.csv",
      ["범위", "연도", "창업_건_보고서원값", "폐업_건_보고서원값", "창업-폐업_건", "출처_정의", "비고"], rows,
      "황오동 사업대상지·황오동·경주시·경북의 창업·폐업 건수 2018~2024(보고서 원값). 임시영업·무점포 정리 전 값",
      "archive/90_derived/hwango_startup_closure_2018_2024.csv ← 황오동 모니터링 보고서 인쇄쪽 57 (PDF 65쪽, 원문 대조 완료)", "2018~2024",
      "보고서의 '선정연도 대비 창업 증가율'과 '고용 증가율'은 사용 금지 목록(README §5)이라 이 CSV에 넣지 않음. 민간 고용자 수 계열은 창업 건수×종사자/사업체 추정치라 제외")

    b = HW["biz2024"]
    o_all, o_real = b["open"]["by_group_all"], b["open"]["by_group"]
    c_all, c_real = b["close"]["by_group_all"], b["close"]["by_group"]
    groups = ["숙박·체류", "생활소매·식품제조", "생활서비스·의료", "음식점·제과", "카페·휴게음식", "유흥·오락", "통신판매(무점포)"]
    rows = []
    for g in groups:
        oa, ora, ca, cra = o_all.get(g, 0), o_real.get(g, 0), c_all.get(g, 0), c_real.get(g, 0)
        rows.append([g, oa, oa - ora, ora, ca, ca - cra, cra, ora - cra, oa - ca,
                     "보고서 인쇄쪽 82~86 창업·폐업 목록을 인허가일→폐업일로 재분류(임시영업=인허가 후 30일 내 폐업+성동동 40·396-4·43-5)",
                     "T2(원자료 재분석)"])
    assert sum(r[1] for r in rows) == 70 and sum(r[3] for r in rows) == 43 and sum(r[4] for r in rows) == 66 and sum(r[6] for r in rows) == 39
    rows.append(["합계", 70, 27, 43, 66, 27, 39, 4, 4, "", ""])
    w("S06b_황오동_2024_창업폐업_재분석_업종군.csv",
      ["업종군", "창업_보고서원값", "창업중_임시영업", "창업_실질", "폐업_보고서원값", "폐업중_임시영업", "폐업_실질", "순증_실질(창업-폐업)", "순증_원값(동일)", "분류_방법", "등급"],
      rows, "2024 황오동 사업지 창업 70 = 임시영업 27 + 실질 43(무점포 12·점포형 31), 폐업 66 = 27 + 39. 업종군별 순증(숙박·체류 +5, 생활소매·식품제조 -9 ...)",
      "archive/C_data/processed/hwango_report.json(biz2024) ← 보고서 인쇄쪽 82~86 목록, work/20260921_황오동_모니터링보고서_재분석.md", "2024",
      "정리본 '플러스인 업종군은 숙박·체류(+5)뿐'은 이 표와 불일치: 통신판매(무점포) +10, 생활서비스·의료 +1도 플러스. 무점포 제외 시에도 +1(생활서비스·의료)이 남음. 임시영업은 창업·폐업 양쪽에 같은 건이 들어 순증에 영향 없음")
    rows = [
        ["임시영업(축제·야시장 영업신고)", 27, 27, "구 경주역 부지(성동동 40) 21 · 성동시장 상인회(396-4) 4 · 성동동 43-5 2", "T2"],
        ["실질", 43, 39, "", "T2"],
        ["  그중 무점포(통신판매)", 12, 2, "", "T2"],
        ["  그중 점포형", 31, 37, "", "T2"],
    ]
    w("S06c_황오동_2024_창업폐업_임시영업_분해.csv", ["구분", "창업_건", "폐업_건", "비고", "등급"], rows,
      "2024 창업 70·폐업 66의 임시영업/무점포/점포형 분해", "archive/C_data/processed/hwango_report.json(biz2024.open/close, popup_by_site)", "2024",
      "실질 창업 43건 < 2018년 48건이라는 비교는 동일 기준이 아님(2018 48건은 같은 정리를 하지 않은 원값). 슬라이드에는 '2024 창업 70건 중 27건이 임시영업' 사실만 쓰는 편이 안전")


# ================================================================ S07 ~ S09 (소상공인365 8구역)
AREA_DEF = {
    "A_hwango_grid32": ("A 황오동 원도심 활성화구역", "SGIS 100m 격자 32셀(모니터링 보고서와 같은 정의)"),
    "B_haengbok_hwangchon_digitized": ("B 경주역동편(행복황촌) 활성화구역", "2020 활성화계획 위치도를 디지타이징한 근사 경계(±20m)"),
    "C_zone_buffer300": ("C 지구단위계획구역+300m", "지구단위계획구역 경계에서 300m 버퍼(반경 300m 원이 아님)"),
    "D_zone": ("D 폐역 구역(지구단위계획구역)", "고시 지구단위계획구역 경계 158,721㎡(고시 조서 156,460㎡ 대비 +1.4%; 시 구상 79,438㎡와는 다른 범위)"),
    "E_center_r300": ("E 구역 중심 반경 300m", "구역 중심(129.218919, 35.8458367) 반경 300m 원"),
    "F_cityhall_r500": ("F 동천동 시청 반경 500m", "경주시청(동천동 800) 중심 반경 500m 원"),
    "G_seongdong_market_r200": ("G 성동시장 반경 200m", "경주성동시장(성동동 51-1) 중심 반경 200m 원"),
    "H_hwangridan_r300": ("H 황리단길 반경 300m", "황리단길 중심(129.2098, 35.8384) 반경 300m 원"),
}
SRC_SBIZ = "소상공인시장진흥공단 소상공인365(bigdata.sbiz.or.kr) 상권분석 인구분석, 통신사 휴대전화 통화량 기반 50m 셀 추정, 2026-09-20 수집"
LIFE_CODES = {"G20404", "G20405", "S20701", "G20503", "G20509", "G21501", "I20101"}


def rcsv(p):
    return list(csv.DictReader(open(p, encoding="utf-8-sig")))


def zone_geoms():
    """8구역 도형(EPSG:5187): A~D는 footfall_areas_5187.geojson, E~H는 build_localdata_turnover.py와 같은 중심·반경 원."""
    fc = jload(PROC / "footfall_areas_5187.geojson")
    g = {f["properties"]["id"]: shape(f["geometry"]) for f in fc["features"]}
    tt = Transformer.from_crs(4326, 5187, always_xy=True).transform
    g["E_center_r300"] = Point(tt(129.218919, 35.8458367)).buffer(300)
    g["F_cityhall_r500"] = Point(tt(129.2247816627553, 35.85621665939485)).buffer(500)
    g["G_seongdong_market_r200"] = Point(tt(129.216354826459, 35.84534371000188)).buffer(200)
    g["H_hwangridan_r300"] = Point(tt(129.2098, 35.8384)).buffer(300)
    return g


def s07():
    summ = rcsv(DER / "footfall_sbiz365_summary.csv")
    d79 = next(float(r["per_ha"]) for r in summ if r["area_id"] == "D_zone")
    zg = zone_geoms()
    rows = []
    for r in summ:
        a = r["area_id"]
        ha = float(r["area_m2"]) / 10000
        m13 = float(r["footfall_13mo_avg"])
        m06 = float(r["footfall_2606"])
        ov = zg[a].intersection(zg["D_zone"]).area if a != "D_zone" else zg[a].area
        rows.append([a, AREA_DEF[a][0], AREA_DEF[a][1], int(float(r["area_m2"])), round(ha, 2), int(m13), round(m13 / ha, 1), int(m06), round(m06 / ha, 1),
                     round(float(r["per_ha"]) / d79, 1), round(ov), round(ov / zg[a].area * 100, 1), round(ov / zg["D_zone"].area * 100, 1),
                     "2025-06~2026-06(월별 일평균의 13개월 평균) / 2026-06 단월", SRC_SBIZ, "T2(추정치)",
                     "정리본: 성동시장 200m 1,175명/ha, 폐역 구역 79명/ha, 약 15배(=14.8배)" if a in ("G_seongdong_market_r200", "D_zone") else ""])
    w("S07_소상공인365_8구역_ha당_일평균유동인구.csv",
      ["구역ID", "구역", "구역_정의", "면적_㎡", "면적_ha", "일평균유동_13개월평균_명", "ha당_13개월평균_명", "일평균유동_2026-06_명", "ha당_2026-06_명",
       "폐역구역(D)_대비_배수(13개월ha당)", "폐역구역(D)과_겹치는_면적_㎡", "그_구역_면적_대비_겹침_퍼센트", "폐역구역(D)_면적_대비_겹침_퍼센트", "집계기간", "출처", "등급", "비고"],
      rows, "소상공인365 8구역 ha당 일평균 유동인구(통신사 추정, 13개월 평균). 성동시장 200m 1,175 vs 폐역 구역 79명/ha",
      "archive/90_derived/footfall_sbiz365_summary.csv ← archive/C_data/raw/sbiz365_footfall_20260920.json · work/20260920_소상공인365_8구역_유동인구_업종_매출.md", "2025-06~2026-06",
      "구역들은 서로 겹침(C⊃D·E 등). '폐역 구역'은 고시 구역 폴리곤이며 79,438㎡ 구상 범위가 아님. 통신사 체류 추정치이지 보행량이 아님")
    rows = []
    for r in rcsv(PROC / "footfall_sbiz365_monthly.csv"):
        rows.append([r["area_id"], AREA_DEF[r["area_id"]][0], r["month"], int(float(r["footfall_daily_avg"])), float(r["per_ha"]), SRC_SBIZ, "T2(추정치)"])
    w("S07b_소상공인365_8구역_월별_일평균유동인구.csv",
      ["구역ID", "구역", "월", "일평균유동_명", "ha당_명", "출처", "등급"], rows,
      "8구역 월별 일평균 유동인구 13개월(꺾은선·계절성 확인용)", "archive/C_data/processed/footfall_sbiz365_monthly.csv", "2025-06~2026-06",
      "8월 피크·1월 저점, 13개월 안에 추세 없음(재추출 문서). 황리단길(H)은 4월·2월 피크, 6월 저점")


def s08():
    hr = rcsv(PROC / "footfall_sbiz365_hourly.csv")
    defs = {"05~09시": "새벽·출근 05~09시", "09~12시": "오전 09~12시", "12~14시": "점심 12~14시", "14~18시": "오후 14~18시", "18~23시": "저녁 18~23시", "23~05시": "야간 23~05시(익일)"}
    rows = []
    for r in hr:
        rows.append([r["area_id"], AREA_DEF[r["area_id"]][0], r["band"], defs[r["band"]], int(float(r["footfall"])), float(r["pct"]),
                     "2026-06 단월 일평균(시간대 합 = 2026-06 일평균)", SRC_SBIZ, "T2(추정치)"])
    w("S08_소상공인365_8구역_시간대별_유동.csv",
      ["구역ID", "구역", "시간대", "구간_정의", "일평균유동_명", "비율_퍼센트", "집계기간", "출처", "등급"], rows,
      "8구역 시간대별(6구간) 유동 비중. 저녁=18~23시, 야간=23~05시. 시청 500m 저녁 27.2%·야간 6.1%, 나머지 7구역 야간 3.7~5.5%·저녁 19.5~23.1%",
      "archive/C_data/processed/footfall_sbiz365_hourly.csv ← raw/sbiz365_footfall_20260920.json(hourly)", "2026-06 단월",
      "비율은 13개월 평균이 아니라 2026-06 단월. 정리본 §1.2의 '야간(18시 이후)'은 저녁+야간(18~05시)을 뜻하므로 슬라이드 표기를 구간 정의와 맞출 것")

    summ = {r["area_id"]: r for r in rcsv(DER / "footfall_sbiz365_summary.csv")}
    rw = rcsv(PROC / "footfall_sbiz365_resident_worker.csv")
    rwd = {(r["area_id"], r["kind"], r["half"]): int(float(r["value"])) for r in rw}
    sa = rcsv(PROC / "footfall_sbiz365_sexage.csv")
    sad = {(r["area_id"], r["group"]): (int(float(r["footfall"])), float(r["pct"])) for r in sa}
    rows = []
    for a, r in summ.items():
        hrs = {x["band"]: float(x["pct"]) for x in hr if x["area_id"] == a}
        eve, night = hrs["18~23시"], hrs["23~05시"]
        res, wk = rwd[(a, "주거인구", "2026H1")], rwd[(a, "직장인구", "2026H1")]
        tot26 = sad[(a, "일일")][0]
        rows.append([a, AREA_DEF[a][0], eve, night, round(eve + night, 1), res, wk, res + wk,
                     float(r["pct_60plus"]), round((sad[(a, "20대")][0] + sad[(a, "30대")][0]) / tot26 * 100, 1), float(r["weekend_to_weekday"]),
                     "시간대·연령: 2026-06 단월 / 주거·직장: 2026 상반기 / 주말·주중: 2026-06", SRC_SBIZ, "T2(추정치)"])
    w("S08b_8구역_저녁야간_주거직장_60대이상_요약.csv",
      ["구역ID", "구역", "저녁_18~23시_퍼센트", "야간_23~05시_퍼센트", "저녁+야간_18~05시_퍼센트", "주거인구_명(2026H1)", "직장인구_명(2026H1)", "주거+직장_명",
       "60대이상_퍼센트(유동 건수 기준 계산)", "20~30대_퍼센트(20대+30대 건수 기준 계산)", "주말/주중_비", "기간", "출처", "등급"],
      rows, "8구역 저녁·야간 비중과 주거·직장 인구, 60대 이상 비중. 시청 500m 주거 9,145·직장 8,374",
      "archive/C_data/processed/footfall_sbiz365_{hourly,resident_worker,sexage}.csv", "2026-06 / 2026H1",
      "시청 500m의 야간 효과는 주거 9,145명 효과와 분리되지 않음(원문 한계). 구경주역 구역(D)은 주거 27·직장 117")
    rows = []
    for r in rw:
        rows.append([r["area_id"], AREA_DEF[r["area_id"]][0], r["kind"], r["half"], int(float(r["value"])), SRC_SBIZ, "T2(추정치)"])
    w("S08c_8구역_주거직장인구_반기별.csv", ["구역ID", "구역", "구분", "반기", "인구_명", "출처", "등급"], rows,
      "8구역 주거인구·직장인구 2025H1~2026H1", "archive/C_data/processed/footfall_sbiz365_resident_worker.csv", "2025H1~2026H1")
    rows = []
    for r in sa:
        tot = sad[(r["area_id"], "일일")][0]
        rows.append([r["area_id"], AREA_DEF[r["area_id"]][0], r["group"], int(float(r["footfall"])), float(r["pct"]), round(float(r["footfall"]) / tot * 100, 1), "2026-06 단월", SRC_SBIZ, "T2(추정치)"])
    w("S08d_8구역_성연령별_유동_2026-06.csv", ["구역ID", "구역", "구분", "유동_명", "비율_원자료표기_퍼센트(플랫폼, 연령은 정수 반올림)", "비율_계산_퍼센트(유동÷일일)", "기간", "출처", "등급"], rows,
      "8구역 성별·연령별 유동(60대+ 비율 등)", "archive/C_data/processed/footfall_sbiz365_sexage.csv", "2026-06 단월")


def s09():
    b = HW["biz2024"]
    o_real, c_real = b["open"]["by_group"], b["close"]["by_group"]
    rows = []
    for g in ["숙박·체류", "생활서비스·의료", "카페·휴게음식", "음식점·제과", "유흥·오락", "생활소매·식품제조", "통신판매(무점포)"]:
        rows.append([g, o_real.get(g, 0), c_real.get(g, 0), o_real.get(g, 0) - c_real.get(g, 0), "무점포" if g.startswith("통신판매") else "점포형",
                     "황오동 사업대상지 2024, 임시영업 27건 제외한 실질 건수", "황오동 모니터링 보고서 인쇄쪽 82~86 재분석", "T2"])
    w("S09_황오동_2024_업종군_실질순증.csv",
      ["업종군", "창업_실질_건", "폐업_실질_건", "순증_건", "점포구분", "정의", "출처", "등급"], rows,
      "황오동 사업지 업종군별 실질 순증(2024): 숙박·체류 +5, 생활소매·식품제조 -9 등",
      "archive/C_data/processed/hwango_report.json(biz2024)", "2024",
      "플러스인 업종군: 통신판매(무점포) +10, 숙박·체류 +5, 생활서비스·의료 +1. 정리본의 '숙박·체류뿐'은 부정확")

    rows = []
    for r in rcsv(DER / "biz_sbiz365_summary.csv"):
        a = r["area_id"]
        sub = r["substituted"]
        life = r["tpbiz_cd"] in LIFE_CODES
        rows.append([a, AREA_DEF[a][0], r["tpbiz"], "생활" if life else "관광·체류", int(r["stores_2606"]), int(r["stores_chg_13mo"]),
                     None if r["sales_per_store_avg"] == "" else int(float(r["sales_per_store_avg"])),
                     None if r["sales_yoy_pct"] == "" else float(r["sales_yoy_pct"]), sub,
                     "인용 금지: 업소 3개 이하라 플랫폼이 황오동 평균으로 대체한 매출" if sub == "Y" else "",
                     "업소수 2026-06 / 13개월 증감(2025-06→2026-06) / 업소당 매출 13개월 평균(만원/월) / 매출 증감은 2026-06÷2025-06 단월 비교",
                     SRC_SBIZ, "T2(추정치)"])
    w("S09b_소상공인365_11업종_8구역_업소수_매출.csv",
      ["구역ID", "구역", "업종", "생활_관광구분", "업소수_2026-06", "업소수_13개월증감", "업소당매출_13개월평균_만원/월", "업소당매출_2026-06대2025-06_증감_퍼센트(단월비교)",
       "매출대체여부(Y=인용금지)", "주의", "정의", "출처", "등급"],
      rows, "소상공인365 11개 업종(슈퍼·편의점·미용·정육·반찬·약국·백반 = 생활 / 카페·여관·호텔·펜션 = 관광·체류) 업소수와 매출",
      "archive/90_derived/biz_sbiz365_summary.csv ← raw/sbiz365_biz_20260920.txt", "2025-06~2026-06",
      "황리단길 펜션 업소당 매출 -27.9%(≈-28%)는 2025-06 362 → 2026-06 261 단월 비교(원문도 잡음 큼으로 명시). 월별은 S09d")

    rows = []
    for r in rcsv(DER / "biz_sbiz365_area_summary.csv"):
        a = r["area_id"]
        rows.append([a, AREA_DEF[a][0], float(r["area_ha"]), int(r["life_stores_2606"]), int(r["tour_stores_2606"]), float(r["life_share_pct"]), int(r["life_chg_13mo"]),
                     int(r["tour_chg_13mo"]), float(r["stores_per_ha"]),
                     "생활=슈퍼·편의점·미용실·정육·반찬·약국·백반 / 관광·체류=카페·여관·호텔·펜션(11개 업종만)", SRC_SBIZ, "T2(추정치)",
                     "정리본: 성동시장 200m 생활 87.8%; 부지 인접 'C(구역+300m)' 펜션 +13·생활 +6 (E 구역중심 반경 300m는 펜션 +3·생활 +1)" if a in ("G_seongdong_market_r200", "C_zone_buffer300") else ""])
    w("S09c_구역별_생활관광_업종구성과_13개월변화.csv",
      ["구역ID", "구역", "면적_ha", "생활업종_개(2026-06)", "관광체류업종_개(2026-06)", "생활비중_퍼센트", "생활_13개월증감_개", "관광체류_13개월증감_개", "업소_개/ha", "정의", "출처", "등급", "비고"],
      rows, "8구역 생활·관광 업종 구성과 13개월 증감. 성동시장 200m 생활 비중 87.8%(8구역 최고)",
      "archive/90_derived/biz_sbiz365_area_summary.csv", "2025-06~2026-06",
      "11개 업종 표본(전체 상권 아님). '부지 반경 300m'로 쓰면 오해: +13/+6은 C(구역 경계 300m 버퍼) 값이며 E(구역 중심 반경 300m)는 +3/+1")

    cnt = {(r["area_id"], r["month"]): int(float(r["stores"])) for r in rcsv(PROC / "biz_sbiz365_count_monthly.csv") if r["tpbiz"] == "펜션"}
    rows = []
    for r in rcsv(PROC / "biz_sbiz365_sales_monthly.csv"):
        if r["tpbiz"] != "펜션" or r["area_id"] not in AREA_DEF:
            continue
        a = r["area_id"]
        rows.append([a, AREA_DEF[a][0], r["month"], cnt.get((a, r["month"])), None if r["sales_per_store_10kwon"] == "" else int(float(r["sales_per_store_10kwon"])),
                     r["substituted_by_dong"], SRC_SBIZ, "T2(추정치)"])
    w("S09d_펜션_업소수_업소당매출_월별_8구역.csv",
      ["구역ID", "구역", "월", "펜션_업소수", "펜션_업소당매출_만원/월", "매출대체여부(Y=인용금지)", "출처", "등급"], rows,
      "펜션(게스트하우스 포함) 월별 업소수와 업소당 매출. 황리단길 36→40, 매출 362→261(2025-06→2026-06)",
      "archive/C_data/processed/biz_sbiz365_count_monthly.csv, biz_sbiz365_sales_monthly.csv", "2025-06~2026-06",
      "H(황리단길) 업소당 매출 최고 497(2025-08), 최저 258(2026-03). 8월 성수기 때문에 단월 증감률은 해석 주의")


# ================================================================ S10
def s10():
    # 원자료(localdata 파일·lodging_permits_*.csv)는 이 PC에 없다. 아래는 전체기록 v1 3절(황촌 숙박 인허가 시계열, 약 4223~4242행) 전사값.
    src = "20261005_구경주역_프로젝트_전체기록_v1.md 3절(황촌 숙박 인허가 시계열, 약 4202~4268행) ← 행안부 지방행정인허가(localdata) 경주시 파일 2026-10-01 수집(원자료 CSV는 이 PC에 없음)"
    stock = [("2020-12-31", 1, 1, ""), ("2022-12-31", 2, 2, ""), ("2023-12-31", 3, 2, ""), ("2024-03-11", 4, 2, "현판식 4곳(B-007 p.10)과 일치"),
             ("2024-12-31", 13, 3, "B-007 '12개소'와 1곳 차이"), ("2025-10-31", 21, 3, "B-007 '21개(도시민박 19+한옥 2)'"), ("2026-06-30", 27, 3, ""),
             ("2026-09-30", 33, 3, "경계 ±20m 민감도: 안쪽 26(+한옥 1) ~ 바깥 33(+한옥 3). 인용 시 '26~33곳' 병기")]
    rows = [[d, a, b, a + b, n, "행복황촌(B, 16.5ha 근사경계) 안 영업 중 재고", src, "T1(인허가 대장 개방본, 전사)"] for d, a, b, n in stock]
    w("S10_행복황촌_숙박인허가_영업중재고_2020_2026.csv",
      ["기준일", "외국인관광도시민박업_곳", "한옥체험업_곳", "합계_곳", "비고", "정의", "출처", "등급"], rows,
      "행복황촌 구역 영업 중 도시민박업: 2020-12-31 1곳 → 2026-09-30 33곳(경계 민감도 26~33)", "20261005_구경주역_프로젝트_전체기록_v1.md (원자료 CSV 부재)", "2020-12-31~2026-09-30",
      "원자료(localdata CSV, lodging_permits_stock.csv)가 PC에 없어 전체기록 전사값 사용. 경계는 근사(±20m)")
    yearly = [("2024", 11, 23, 48), ("2025", 9, 33, 27), ("2026(1~9월)", 12, 34, 35)]
    rows = [[y, a, b, c, "외국인관광 도시민박업 신규 인허가", src, "T1(전사)"] for y, a, b, c in yearly]
    w("S10b_도시민박업_연도별_신규인허가_행복황촌_경주시.csv",
      ["연도", "행복황촌_건", "경주시전체_건", "행복황촌_비중_퍼센트", "정의", "출처", "등급"], rows, "도시민박업 신규 인허가(행복황촌 vs 경주시 전체)",
      "20261005_구경주역_프로젝트_전체기록_v1.md 3절", "2024~2026-09")
    city = [("2015", 17), ("2022", 52), ("2023", 43), ("2024", 64), ("2026-09", 123)]
    rows = [[y, n, "경주시 전체 영업 중 외국인관광 도시민박업(기준일은 해당 연도 말, 2026은 9월 30일)", src, "T1(전사)",
             "2023은 폐업 12 반영. 2026-09: 황오동 50·성동동 15 = 65곳(53%), 행복황촌 구역 33곳(27%)" if y == "2026-09" else ""] for y, n in city]
    w("S10c_경주시_영업중_도시민박업_2015_2026.csv", ["기준", "영업중_곳", "정의", "출처", "등급", "비고"], rows, "경주시 전체 영업 중 도시민박업 곳수",
      "20261005_구경주역_프로젝트_전체기록_v1.md 3절", "2015~2026-09")

    lines = open(DER / "haengbok_hwangchon_footfall_2019_2025.csv", encoding="utf-8-sig").read().splitlines()[1:]
    rd = csv.DictReader(lines)
    rows = []
    for r in rd:
        if r["연도"] in ("2024", "2025"):
            continue     # 5,431명(+396%) 사용 금지 — CSV에 넣지 않는다
        rows.append([r["연도"], int(r["연평균(명)"]), int(r["월수"]), "보고서 표(소상공인365, 사업구역 기준) 연평균 일평균 유동인구",
                     "참고용 — 표 오류 의심(2021·2023 월별 동일), 그대로 인용 금지" if r["비고"] else "참고용",
                     "2025 행복황촌 모니터링 보고서(2025.12) 인쇄쪽 93", "T2(보고서 전사)"])
    mon = [r for r in rcsv(PROC / "footfall_sbiz365_monthly.csv") if r["area_id"] == "B_haengbok_hwangchon_digitized"]
    avg = round(sum(float(r["footfall_daily_avg"]) for r in mon) / len(mon))
    rows.append(["2025-06~2026-06(13개월 평균)", avg, 13, "같은 구역을 소상공인365에서 재추출한 일평균", "재추출 — 보고서의 2019~2023 값(1,096~1,544)과 같은 자리",
                 "work/20260920_소상공인365_유동인구_재추출.md", "T2(재추출)"])
    w("S10d_행복황촌_유동인구_보고서2019_2023과_재추출.csv",
      ["기준", "일평균_유동인구_명", "집계월수", "정의", "신뢰", "출처", "등급"], rows,
      "행복황촌 구역 일평균 유동(보고서 2019~2023 참고 + 재추출 1,321명/일). 보고서 표의 2024·2025 행은 사용 금지 목록(README §5)이라 제외",
      "archive/90_derived/haengbok_hwangchon_footfall_2019_2025.csv, footfall_sbiz365_monthly.csv", "2019~2023, 2025.06~2026.06",
      "원자료 표에 2024·2025 행이 있으나(연도 라벨 불일치) 재현되지 않아 사용 금지 목록에 해당 — 이 CSV에 넣지 않음(README §5)")
    rows = [[r["month"], int(float(r["footfall_daily_avg"])), float(r["per_ha"]), SRC_SBIZ, "T2(추정치)"] for r in mon]
    w("S10e_행복황촌_월별_일평균유동_2025-06_2026-06.csv", ["월", "일평균유동_명", "ha당_명", "출처", "등급"], rows, "행복황촌(B) 월별 일평균 유동 13개월",
      "archive/C_data/processed/footfall_sbiz365_monthly.csv", "2025-06~2026-06")


# ================================================================ S11
def s11():
    src = "2024년 황오동 원도심(중심시가지형) 도시재생뉴딜사업 성과지표 및 모니터링 용역 결과보고서(수정중), 공공도시 2025.09 (PDF 렌더링으로 쪽 확인)"
    rows = []

    def add(item, cat, basis, cnt, p, page):
        rows.append([item, cat, basis, cnt, p, page, src, "T2", ""])
    stay = [("1~3시간(보고서 종합표 라벨 '3시간 미만')", 148, 79.14), ("3~6시간 미만", 28, 14.97), ("6~9시간 미만", 6, 3.21), ("9~12시간 미만", 0, 0.00), ("12~24시간 미만", 0, 0.00), ("24시간 이상", 5, 2.67)]
    assert sum(c for _, c, _ in stay) == 187
    for cat, c, p in stay:
        add("문항7 황오동 방문 체류시간", cat, "응답 187명", c, p, "인쇄쪽 44")
    spend = [("1만원 미만", 19, 10.11), ("1~5만원 미만", 122, 64.89), ("5~10만원 미만", 42, 22.34), ("10~20만원 미만", 5, 2.66), ("20만원 이상", 0, 0.00)]
    assert sum(c for _, c, _ in spend) == 188
    for cat, c, p in spend:
        add("문항6 황오동 방문 소비금액", cat, "응답 188명", c, p, "인쇄쪽 43")
    prev = [("성동시장", 93, 47.69), ("경주대릉원", 11, 5.64), ("보문관광단지", 12, 6.15), ("황리단길", 24, 12.31), ("경주읍성", 4, 2.05), ("감포", 1, 0.51), ("경주KTX역", 6, 3.08), ("기타", 44, 22.56)]
    assert sum(c for _, c, _ in prev) == 195
    for cat, c, p in prev:
        add("문항5 황오동 방문 이전 방문지(복수응답)", cat, "응답 195건(복수응답, 응답자 188명)", c, p, "인쇄쪽 43")
    for cat, c, p in [("오전", 9, 4.79), ("오후", 179, 95.21)]:
        add("문항8 황오동 방문시간", cat, "응답 188명", c, p, "인쇄쪽 44")
    res = [("황오동", 25, 13.30), ("경주시(황오동 제외)", 106, 56.38), ("서울/경기/인천", 13, 6.91), ("대전/세종/충청", 3, 1.60), ("대구/경북", 20, 10.64), ("부산/울산/경남", 21, 11.17),
           ("광주/전라", 0, 0.00), ("강원", 0, 0.00), ("제주", 0, 0.00)]
    assert sum(c for _, c, _ in res) == 188
    for cat, c, p in res:
        add("응답자 거주지역", cat, "응답 188명", c, p, "인쇄쪽 40")
    for cat, c, p in [("남자", 77, 40.96), ("여자", 111, 59.04)]:
        add("응답자 성별", cat, "응답 188명", c, p, "인쇄쪽 40")
    for cat, c, p in [("10대", 6, 3.19), ("20대", 41, 21.81), ("30대", 47, 25.00), ("40대", 34, 18.09), ("50대", 37, 19.68), ("60대", 17, 9.04), ("70대 이상", 6, 3.19)]:
        add("응답자 연령대", cat, "응답 188명", c, p, "인쇄쪽 40")
    for cat, p in [("쇼핑", 11.5), ("업무", 4.7), ("지인 방문", 12.0), ("시설 방문", 7.3), ("축제", 50.0), ("단순 경로", 14.6)]:
        rows.append(["방문 계기(2024)", cat, "종합표 비율만 표기", None, p, "인쇄쪽 46", src, "T2", "건수 미확인(비율 전사)"])
    w("S11_황오동_방문객설문_2024_문항별분포.csv",
      ["문항", "구분", "응답수_기준", "응답_건/명", "비율_퍼센트", "쪽", "출처", "등급", "비고"], rows,
      "황오동 방문객 설문 2024(n=188): 체류 1~3시간 79.1%, 소비 10만 원 이상 2.7%(1만 원 이상 아님), 경주시 거주 56.4%(황오동 13.3% 별도)",
      "경주역 관련 경주시민 인식조사 결과 데이터/…/결과보고서(수정중)_2024년 황오동 원도심….pdf PDF 48·51·52·54쪽(인쇄쪽 40·43·44·46)", "2024(축제 현장 조사 비중 큼)",
      "소비금액 '2.7%'는 10~20만 원 미만 5명(2.66%)이며 1만 원 이상은 89.9%. 경주 시민 합계는 56.38+13.30=69.7%(황오동 거주 포함). 연도별 조사 장소가 달라 시계열 비교 금지(보고서 주)")
    sv = HW["survey_vis"]
    rows = []
    for i, y in enumerate(sv["years"]):
        rows.append([y, sv["awareness"][i], sv["stay"]["3h 미만"][i], round(100 - sv["spend_over_10"][i], 1), sv["spend_over_10"][i], sv["time_pm"][i], sv["motive"]["축제"][i], sv["satis"][i],
                     "표본·조사 장소가 해마다 다름(2024는 축제 현장 비중 큼) — 시계열 비교 금지", "보고서 종합 표 인쇄쪽 46 (PDF 54쪽)", "T2"])
    w("S11b_황오동_방문객설문_2020_2024_요약지표.csv",
      ["연도", "사업_인지도_퍼센트", "체류_3시간미만_퍼센트", "소비_10만원미만_퍼센트", "소비_10만원이상_퍼센트", "방문시간_오후_퍼센트", "방문계기_축제_퍼센트", "방문만족도_점수", "주의", "출처", "등급"],
      rows, "방문객 설문 2020~2024 요약지표(해마다 조사 장소 상이)", "archive/C_data/processed/hwango_report.json(survey_vis)", "2020~2024",
      "소비는 '10만원 이상' 비율: 13.9/7.4/77.2/40.4/2.7. 2024 2.7%는 같은 열의 값")


# ================================================================ S12 방문 이동 수단
def s12():
    src = open(ROOT / "pipeline" / "pipeline" / "build_tourist_viz.py", encoding="utf-8").read()

    def grab(name):
        i = src.index(name + " = {")
        j = src.index("{", i)
        depth = 0
        for k in range(j, len(src)):
            if src[k] == "{":
                depth += 1
            elif src[k] == "}":
                depth -= 1
                if depth == 0:
                    return ast.literal_eval(src[j:k + 1])

    S = grab("SURVEY")
    modes = S["modes"]
    ssrc = "경주시 관광실태조사 제5회(2025.11 보고) 내국인 p.22·23·24·37 — build_tourist_viz.py의 SURVEY 딕셔너리 전사(원문 PDF는 이 PC에 없음)"
    rows = []
    for yr, n, vals in S["trend"]:
        assert abs(sum(vals) - 100) < 0.11, (yr, sum(vals))
        rows.append([yr, n] + vals + [round(vals[3] + vals[4] + vals[5], 1), ssrc, "T2(국가승인통계, 전사)",
                                      "2024년 조사(제5회). 2024부터 황리단길·첨성대(원도심) 지점 제외, 조사 지점 6곳(불국사·동궁과월지·대릉원·양동마을·경주월드·동궁원)" if yr == "2024" else
                                      ("2021은 코로나 영향(전세·관광버스 0.4%)" if yr == "2021" else "")])
    w("S12_경주방문_교통수단_내국인_연도별.csv",
      ["조사연도", "표본_n"] + [m + "_퍼센트" for m in modes] + ["시외·고속·일반열차_합_퍼센트(철도·노선버스)", "출처", "등급", "비고"], rows,
      "경주 방문 교통수단 분담(내국인, 관광실태조사): 자가용 2013 60.0% → 2024 76.9%(중간 2021 84.2%). KTX/SRT 5.2→8.5%",
      "pipeline/pipeline/build_tourist_viz.py(SURVEY.trend) ← 경주시 관광실태조사 제5회(2025.11)", "2013, 2014, 2017, 2021, 2024",
      "자가용 '60→77%'는 양 끝만 본 값(2017 74.6, 2021 84.2). 조사 지점이 해마다 같지 않음")
    rows = []
    for g, n, vals in S["by_group"]:
        rows.append([g, n] + vals + [ssrc, "T2(전사)"])
    w("S12b_경주방문_교통수단_내국인_거주지권역_연령별_2024.csv",
      ["구분", "표본_n"] + [m + "_퍼센트" for m in modes] + ["출처", "등급"], rows,
      "교통수단 분담(내국인 2024) 거주지 권역·연령별. 수도권 출발 KTX/SRT 21.1%", "pipeline/pipeline/build_tourist_viz.py(SURVEY.by_group)", "2024")
    rows = []
    for yr, n, vals in S["foreign"]:
        rows.append([yr, n] + vals + ["경주시 관광실태조사 제5회 외국인 p.55(불국사 조사, 개별 서구 관광객 위주) — SURVEY 전사", "T2(전사)",
                                      "보고서 본문이 25.1%를 '자가용'으로 적은 것은 표 열 순서상 택시의 오기(전체기록 §5.3). 문항은 '경주 여행 시 주된 수단'" if yr == "2024" else ""])
    w("S12c_경주방문_교통수단_외국인_2017_2024.csv",
      ["조사연도", "표본_n"] + [m + "_퍼센트" for m in S["foreign_modes"]] + ["출처", "등급", "비고"], rows,
      "외국인 경주 여행 시 주된 수단(불국사 조사)", "pipeline/pipeline/build_tourist_viz.py(SURVEY.foreign)", "2017, 2024",
      "국적별 표본 작음(중국 n=25). 외국인 전체의 대표값으로 쓰지 말 것")

    esrc = "전체기록 v1 §5.5 전사(코레일·SR·한국도로공사; 원자료 arrival_counts.json 부재)"
    rows = [
        ["철도 하차(명/년)", "코레일 경주역(KTX·동해선)", "2023", 1317261, None, esrc, "T2"],
        ["철도 하차(명/년)", "SRT 경주역", "2023", 529193, None, esrc, "T2"],
        ["철도 하차(명/년)", "서경주·안강·아화", "2023", 51104, None, esrc, "T2"],
        ["철도 하차(명/년)", "계", "2023", 1897558, 5199, esrc, "T2"],
        ["철도 하차(명/년)", "코레일 경주역(KTX·동해선)", "2024", 1494130, None, esrc, "T2"],
        ["철도 하차(명/년)", "SRT 경주역", "2024", 506358, None, esrc, "T2"],
        ["철도 하차(명/년)", "서경주·안강·아화", "2024", 48691, None, esrc, "T2"],
        ["철도 하차(명/년)", "계", "2024", 2049179, 5599, esrc, "T2"],
        ["고속도로 4개 영업소 출구 진출(대/일평균)", "경주", "2024", None, 18526, esrc, "T2"],
        ["고속도로 4개 영업소 출구 진출(대/일평균)", "남경주", "2024", None, 5916, esrc, "T2"],
        ["고속도로 4개 영업소 출구 진출(대/일평균)", "서경주(구 건천)", "2024", None, 4776, esrc, "T2"],
        ["고속도로 4개 영업소 출구 진출(대/일평균)", "동경주", "2024", None, 3482, esrc, "T2"],
        ["고속도로 4개 영업소 출구 진출(대/일평균)", "계", "2024", None, 32700, esrc, "T2"],
        ["고속도로 4개 영업소 출구 진출(대/일평균)", "경주", "2025", None, 17952, esrc, "T2"],
        ["고속도로 4개 영업소 출구 진출(대/일평균)", "남경주", "2025", None, 5692, esrc, "T2"],
        ["고속도로 4개 영업소 출구 진출(대/일평균)", "서경주(구 건천)", "2025", None, 4410, esrc, "T2"],
        ["고속도로 4개 영업소 출구 진출(대/일평균)", "동경주", "2025", None, 3395, esrc, "T2"],
        ["고속도로 4개 영업소 출구 진출(대/일평균)", "계", "2025", None, 31450, esrc, "T2"],
    ]
    assert 1494130 + 506358 + 48691 == 2049179 and 1317261 + 529193 + 51104 == 1897558
    assert round(2049179 / 366) == 5599 and round(1897558 / 365) == 5199
    w("S12d_실측이용량_철도하차_고속도로IC출구.csv",
      ["구분", "항목", "연도", "연간합계_명", "일평균", "출처", "등급"], rows,
      "경주 유입 실측 이용량: 철도 하차 2024 일평균 5,599명, 4개 영업소 출구 진출 2025 일평균 31,450대(승용 87.1%)",
      "20261005_구경주역_프로젝트_전체기록_v1.md §5.5 (원자료 arrival_counts.json 부재)", "2023~2025",
      "관광 목적 미구분 총량(시민 귀가 포함). 2025 영업소별 합 31,449 vs 계 31,450은 원문 반올림. 정리본의 'arrival_transport.json'에는 이 값이 없음(다른 파일). IC 값은 국도 유입 제외, 버스 미확보")
    rows = [["TS 원값(관광실태조사 2024)", 76.9, 8.5, 8.3, 3.8, 1.7, "추정 아님(조사 원값)"],
            ["DL 거주지 가중(TS×DL 보정)", 79.3, 6.5, 7.5, 4.4, 1.6, "추정 — 범위로만 사용"],
            ["민감도(수도권 비중 1/2)", 80.7, 5.0, 7.5, 4.4, 1.5, "추정 — 범위로만 사용"]]
    w("S12e_교통수단_거주지가중_보정추정.csv",
      ["구분", "자가용_퍼센트", "KTX/SRT_퍼센트", "전세·관광버스_퍼센트", "시외+고속버스_퍼센트", "일반열차_퍼센트", "성격"], rows,
      "교통수단 분담의 거주지 구성 보정 추정(자가용 77~81%·KTX/SRT 5~9% 범위의 근거). 추정치 — 슬라이드에는 범위로만",
      "20261005_구경주역_프로젝트_전체기록_v1.md §5.2", "2024",
      "TS 표본 구성(수도권 27·대경 30.5·동남 24.4·그 외 18.2%)과 데이터랩 거주지 분포(18.0·34.2·39.0·8.8%)의 차이를 보정한 조사자 계산")


# ================================================================ S13 2030 기본계획 설문 + 공영주차
def s13():
    src = "2030 경주도시기본계획(T1) 인쇄쪽 79 (PDF 93쪽, 쪽 이미지 직접 확인)"
    meta = "2015.9.18~10.17, 회수 1,408부(71.5%), 시민·공무원·근로자·전문가(인쇄쪽 72~74)"
    rows = []
    for q, items in [("경주역 부지 이전 활용방안", [("복합위락공간(쇼핑센터·영화관 등)", 44.5), ("행정복합타운(공공청사·복지시설 등)", 26.2), ("공원·광장", 22.9),
                                                    ("문화·예술공간", 5.1), ("기타", 0.7), ("무응답", 0.7)]),
                     ("교통문제 개선사항(보고서 제목 '교통부문 문제점')", [("대규모 주차시설 확충", 38.8), ("대중교통 서비스 개선", 25.6), ("도로망 확충 정비", 20.3),
                                                        ("쾌적한 보행환경 조성", 14.3), ("무응답", 0.7), ("기타", 0.4)])]:
        for i, (a, v) in enumerate(items, 1):
            rows.append([q, i, a, v, "응답 비율(합 100.1%, 반올림 오차)", meta, src, "T1(승인계획 부속 조사)",
                         "표본 1,408부는 시민·공무원·근로자·전문가 합산. 2015년 조사로 현재(2026)의 시민 의견이 아님" if i == 1 else ""])
    w("S13_2030기본계획_시민의식설문_경주역부지활용_교통문제_2015.csv",
      ["문항", "순위", "응답", "비율_퍼센트", "비율_정의", "조사_개요", "출처", "등급", "비고"], rows,
      "2030 기본계획 시민의식 설문(2015.9~10, 회수 1,408부): 대규모 주차시설 확충 38.8%(교통 1위), 경주역 부지 복합위락 44.5% / 행정복합타운 26.2% / 공원·광장 22.9%",
      "2030경주도시기본계획/refined/P1-C02-S04_시민의식설문조사.md · 2030 경주도시기본계획.pdf PDF 93쪽(인쇄쪽 79)", "2015.9.18~10.17",
      "archive/90_derived/citizen_preference_surveys_station_site.csv 의 '2016~2017 추정·표본 미확인·교통 인쇄쪽 78'은 오기(실제 2015년·1,408부·인쇄쪽 79)")

    t = Transformer.from_crs(4326, 5187, always_xy=True)
    g = jload(PROC / "parking_pub_4326.geojson")
    zc = (219776.9, 360961.0)
    st = (219649.2, 360746.0)
    rows = []
    for f in g["features"]:
        p = f["properties"]
        x, y = t.transform(*f["geometry"]["coordinates"])
        d_z = math.hypot(x - zc[0], y - zc[1])
        d_s = math.hypot(x - st[0], y - st[1])
        rows.append([p["name"], p["addr"], p["spaces"], round(d_z), round(d_s), "Y" if (d_z <= 1000 and p["spaces"]) else "N",
                     "임시" if "임시" in p["name"] else "", "경주시시설관리공단 교통운영 시설안내(gjfmc.or.kr, 2026-09-21 열람, T2), 좌표 V-World 지오코딩. 노상·민영 제외", "T2"])
    rows.sort(key=lambda r: r[3])
    tot1 = sum(r[2] for r in rows if r[5] == "Y")
    tot15 = sum(r[2] for r in rows if r[3] <= 1500 and r[2])
    tot2 = sum(r[2] for r in rows if r[3] <= 2000 and r[2])
    assert (tot1, tot15, tot2) == (1297, 1463, 2232), (tot1, tot15, tot2)
    rows.append(["합계(구역 중심 1km)", "", tot1, None, None, "", "", "1.5km 1,463면 · 2km 2,232면(같은 중심 기준)", "T2"])
    w("S13b_공영주차장_구역중심1km_1297면.csv",
      ["주차장", "주소", "면수", "구역중심까지_직선거리_m", "옛_역사점까지_직선거리_m", "구역중심_1km_이내", "임시여부", "출처", "등급"], rows,
      "부지 반경 1km 공영주차장 1,297면(성동시장 221·제2공영 78·중심상가 209·제1공영 198·봉황대 95·쪽샘 496) — 구역 중심(219776.9, 360961.0) 기준",
      "archive/C_data/processed/parking_pub_4326.geojson (거리는 EPSG:5187로 직접 계산)", "2026-09-21 열람",
      "쪽샘지구 임시공영주차장 496면(38%)은 '임시'. 옛 역사점(219649, 360746) 기준 1km 이내는 1,341면(중앙시장 제1·포석로 추가). 노상·민영 제외")


# ================================================================ S14 417쪽 연구 시민설문
def s14():
    src = "경주시 원도심 미래구상 기획 연구(동국대·가천대, 경주시 미래전략실, 2025.07), 417쪽 연구 인쇄쪽 쪽수(PDF = 인쇄쪽 +1)"
    rows = []

    def add(q, n_resp, item, cnt, page, note=""):
        rows.append([q, n_resp, item, cnt, page, src, "T2", note])
    add("표본 개요", "65(전체)/63(유효)", "응답자 전체 65명·유효 63명(설문 2025-03-16·04-24 2차, 네이버폼+대면)", None, "33")
    add("표본 개요", "63", "거주지 원도심 30 · 교외 33 · 미확인 2", None, "34", "합 65")
    add("표본 개요", "63", "청년층(10~30대) 원도심 10·교외 21 = 31 / 중장년층(40대+) 원도심 20·교외 12 = 32", None, "35", "미확인 2")
    add("원도심 대중교통 평가(5점 만점)", 54, "평균 2.7점", None, "65·67", "청년층 27명 2.48 / 중장년층 28명 3.03 (두 군 합 55 ≠ 전체 54: 원문 불일치)")
    add("원도심 대중교통 평가(5점 만점)", 27, "청년층 평균 2.48점", None, "65·67")
    add("원도심 대중교통 평가(5점 만점)", 28, "중장년층 평균 3.03점", None, "65·67")
    for item, c in [("자율주행 무료버스", 18), ("보행공간 개선", 13), ("폐철도(옛철도) 재개통", 10), ("트램", 8), ("버스 전용 차선", 1)]:
        add("원도심 대중교통 문제해결 방법", 51, item, c, "65·66·67", "청년 26+중장년 25=51. 이 외 자가용 이용으로 미답변 6")
    add("원도심 대중교통 문제해결 방법", 51, "미답변(자가용 이용)", 6, "65·66", "원문: 중장년층 6")
    for item, c in [("버스터미널", 30), ("기차역", 22), ("자가용", 19)]:
        add("다른 도시로 나갈 때 이용 교통(복수)", 49, item, c, "67")
    for item, c in [("시내와 연결성 부족", 12), ("도로혼잡", 11), ("고속·시외버스터미널 기능 분리", 9), ("(도보)대중교통 환승 어려움", 5), ("(자차)주차장 협소", 5), ("로컬콘텐츠(경주 대표 상업시설) 부족", 4),
                    ("주변 숙박업소 협소·시설 낙후", 3), ("주변 편의시설 협소", 2)]:
        add("버스터미널 이용 불편점(복수)", 46, item, c, "67", "항목 합 51 > 응답자 46 → 복수응답")
    for item, c in [("쇼핑여가", 26), ("대중교통", 24), ("문화예술", 24), ("의료보건", 8), ("하천정보", 6), ("학교교육", 5), ("관광시설", 2), ("편의시설", 1), ("주차", 1)]:
        add("원도심에 필요한 시설(복수)", 52, item, c, "33·68", "'주차'는 52명 중 1건")
    for item, c in [("관광도시", 35), ("힐링도시", 28), ("역사도시", 23), ("시민을 위한 도시(기타 의견)", 11)]:
        add("경주의 미래 방향성(복수)", 52, item, c, "33·68")
    for item, c in [("보전", 29), ("개발", 26)]:
        add("보전 vs 개발", 55, item, c, "69")
    for item, c in [("울산", 40), ("포항", 40), ("대구", 32), ("부산", 11)]:
        add("경주와 친한 도시(복수)", 56, item, c, "36")
    for item, c in [("문화·쇼핑(원문 '문화쇼핑', 백화점을 뜻함)", 37), ("교통거점", 16), ("지식기술센터", 3), ("공공기관", 3), ("주거(청년층 응답에서만 언급)", 1)]:
        add("(옛)경주역에 들어왔으면 하는 기능(복수)", 55, item, c, "63·64", "원문은 '응답자 55명, 총 58개 응답'이라 적었으나 항목 합은 4개 59 / 주거 포함 60 — 내부 불일치(S14b 참조)")
    w("S14_417쪽연구_시민설문_문항별_응답수.csv",
      ["문항", "응답자수_n", "응답/항목", "건수", "쪽(인쇄쪽)", "출처", "등급", "비고"], rows,
      "417쪽 연구 시민설문(2025.03·04, 전체 65명·유효 63명) 문항별 응답. 문항마다 n이 다름(46~56). 대중교통 평가 2.7/5, 대안 선호 18>13>10>8",
      "#경주시 원도심 미래구상 기획 연구 0804 최종본.pdf PDF 34~37·64~70쪽(인쇄쪽 33~36·63~69, 쪽 이미지·텍스트 직접 확인)", "2025-03-16, 2025-04-24",
      "표본이 작고(63) 장소(원도심 30·교외 33)·성별(여 59%)이 치우침. 청년층 교외·중장년층 원도심 비율이 높음")
    rows = [
        ["문화·쇼핑", 16, 21, 37, "31명(56.3%, 55명 기준)", "정리본·원문 37건과 일치(16+21)"],
        ["교통거점", 12, 4, 16, "16명(25%)", "16건과 일치(12+4); 25%는 16÷63(유효 응답자)으로 보이고 문화쇼핑 56.3%는 31÷55라 분모가 다름(원문 미설명)"],
        ["지식기술센터", 0, 3, 3, "", ""],
        ["공공기관", 0, 3, 3, "", ""],
        ["주거", 1, 0, 1, "", "본문 4항목 나열에서는 빠지고 청년층 설명에만 등장"],
        ["합계(항목 합)", 29, 31, 60, "", "원문 '총 58개 응답'과 불일치(60). 본문 4항목 합은 59"],
        ["응답자 수", 27, 28, 55, "", "청년층 27 + 중장년층 28 = 55명(문항 응답자). 유효 63명 중 55명이 답함"],
    ]
    w("S14b_옛경주역_기능기대_Q6.1_연령별_대조.csv",
      ["기능", "청년층_건", "중장년층_건", "합계_건", "원문_인원표기", "대조·비고"], rows,
      "정리본 '시민 요구(응답 58건): 문화·쇼핑 37, 교통 거점 16, 지식·기술센터 3, 공공기관 3, 주거 1(55명, 청년 27·중장년 28)'은 417쪽 연구 Q6.1과 같은 조사·같은 문항(복수응답). 전체 n=63의 하위 응답자 55명",
      "#경주시 원도심 미래구상 기획 연구 0804 최종본.pdf PDF 64·65쪽(인쇄쪽 63·64)", "2025-03·04",
      "정리본은 '58건'과 항목 5개(합 60)를 함께 적어 원문의 불일치를 그대로 옮김. 슬라이드에는 '응답자 55명, 복수응답'과 항목별 건수만 쓰고 합계는 쓰지 않는 편이 안전")


# ================================================================ S15 가구 구조
def s15():
    d = jload(ROOT / "work" / "20261008_youth_housing" / "kosis_DT_1JC1502.json")
    tab = collections.defaultdict(dict)
    for r in d:
        tab[r["C1_NM"]][r["ITM_NM"]] = None if r["DT"] == "X" else int(r["DT"])
    ksrc = "KOSIS DT_1JC1502 가구원수별 가구-읍면동, 인구총조사(등록센서스) 2025, 최종수정 2026-07-24"
    cols = ["일반가구_계", "1인", "2인", "3인", "4인", "5인", "6인 이상"]
    rows = []

    def row(nm, v, note=""):
        tot = v["일반가구_계"]
        if v["6인 이상"] is None:
            note = (note + " " if note else "") + "6인 이상 가구 수는 통계청 비공개(X)"
        rows.append([nm, tot, v["1인"], v["2인"], v["3인"], v["4인"], v["5인"], v["6인 이상"], round(v["1인"] / tot * 100, 1), round(v["2인"] / tot * 100, 1),
                     round((v["1인"] + v["2인"]) / tot * 100, 1), ksrc, "T2", note])
    for nm in ["경주시", "황오동", "성건동", "황남동", "월성동"]:
        row(nm, tab[nm], "원도심 4개 동 중 하나" if nm not in ("경주시",) else "")
    four = {c: sum(tab[n][c] for n in ["황오동", "성건동", "황남동", "월성동"]) for c in cols}
    row("원도심 4개 동 합(황오·성건·황남·월성)", four, "정리본 82.6%")
    three = {c: sum(tab[n][c] for n in ["황오동", "황남동", "월성동"]) for c in cols}
    row("원도심 3개 동 합(성건동 제외)", three, "성건동은 대학가라 1인 가구 60.1%: 제외 시 비율이 낮아짐")
    for nm in sorted(k for k in tab if k not in ("경주시", "황오동", "성건동", "황남동", "월성동")):
        row(nm, tab[nm])
    for r in rows:
        if r[7] is not None:
            assert r[1] == sum(r[2:8]), r[0]
    w("S15_가구원수별_가구_2025_경주시_읍면동.csv",
      ["지역", "일반가구_계", "1인_가구", "2인_가구", "3인_가구", "4인_가구", "5인_가구", "6인이상_가구", "1인_퍼센트", "2인_퍼센트", "1~2인_퍼센트", "출처", "등급", "비고"], rows,
      "가구원수별 가구(2025): 경주시 1인 46,606·2인 39,602 → 1~2인 73.8%, 원도심 4개 동 82.6%(성건동 제외 79.6%)",
      "work/20261008_youth_housing/kosis_DT_1JC1502.json (KOSIS 직접 조회 2026-10-08)", "2025",
      "황오동은 2025 행정동 통합 후 구역(옛 중부동 포함). 성건동은 동국대 인근 1인 가구 비중이 매우 높음")
    d = jload(ROOT / "work" / "20261008_youth_housing" / "kosis_DT_1JC1511.json")
    t2 = collections.defaultdict(dict)
    for r in d:
        t2[r["C2_NM"]][r["ITM_NM"]] = r["DT"]
    order = ["15~19세", "20~24세", "25~29세", "30~34세", "35~39세", "40~44세", "45~49세", "50~54세", "55~59세", "60~64세", "65~69세", "70~74세", "75~79세", "80~84세", "85세이상"]
    rows = []
    csrc = "KOSIS DT_1JC1511 가구주의 연령 및 가구원수별 가구(일반가구)-시군구, 인구총조사(등록센서스) 2025"

    def num(x):
        return None if x in ("X", "", None) else int(float(x))
    for a in order:
        v = t2[a]
        rows.append([a, num(v["일반가구"]), num(v["1인"]), num(v["2인"]), num(v["3인"]), num(v["4인"]), num(v["5인"]), num(v["6인"]), num(v["7인 이상"]),
                     v["평균 가구원 수"], csrc, "T2", "X=통계청 비공개(표시 생략)" if any(v[k] == "X" for k in v) else ""])
    def sub(keys, col):
        vals = [num(t2[k][col]) for k in keys]
        return None if any(v is None for v in vals) else sum(vals)   # 비공개(X) 칸이 하나라도 있으면 합계를 만들지 않는다
    for lab, keys in [("합계 20~39세(가구주)", order[1:5]), ("합계 20~34세(가구주)", order[1:4])]:
        rows.append([lab, sub(keys, "일반가구"), sub(keys, "1인"), sub(keys, "2인"), sub(keys, "3인"), sub(keys, "4인"), sub(keys, "5인"), sub(keys, "6인"), sub(keys, "7인 이상"), "", csrc, "T2", "5세 구간 합산(조사자 계산). 구간 중 비공개(X) 칸이 있는 열은 합계를 비움"])
    assert rows[-2][1] == 18052 and rows[-2][2] + rows[-2][3] == 14122
    w("S15b_가구주연령별_가구원수_경주시_2025.csv",
      ["가구주_연령", "일반가구", "1인", "2인", "3인", "4인", "5인", "6인", "7인이상", "평균_가구원수", "출처", "등급", "비고"], rows,
      "가구주 연령별 가구원수(경주시 2025): 가구주 20~39세 18,052가구 중 1~2인 14,122(1인 11,094+2인 3,028)",
      "work/20261008_youth_housing/kosis_DT_1JC1511.json", "2025", "가구주 20~39세 = 가구 단위. 주민등록 '20~39세 인구(42,617명)'와는 다른 지표")
    d = jload(ROOT / "work" / "20261008_youth_housing" / "kosis_DT_1JC1521.json")
    hh = collections.defaultdict(dict)
    for r in d:
        hh[r["C2_NM"]][r["ITM_NM"]] = float(r["DT"])
    rows = []
    for k in ["계", "단독주택", "아파트", "연립주택", "다세대주택", "비주거용 건물 내 주택", "오피스텔"]:
        v = hh[k]
        rows.append([k, int(v["일반가구"]), round(v["일반가구"] / hh["계"]["일반가구"] * 100, 1), int(v["가구원"]), v["가구당 주거면적"], v["1인당 주거면적"],
                     "KOSIS DT_1JC1521 주택(오피스텔 포함)의 종류 및 주거면적별 가구(일반가구) 시군구, 2025", "T2",
                     "분모 113,733은 '주택(오피스텔 포함)에 사는 일반가구'로 DT_1JC1502의 일반가구 116,834와 모집단이 다름" if k == "계" else ""])
    w("S15c_주택유형별_가구_경주시_2025.csv",
      ["주택유형", "일반가구", "구성비_퍼센트", "가구원_명", "가구당_주거면적_㎡", "1인당_주거면적_㎡", "출처", "등급", "비고"], rows,
      "주택 유형별 가구(경주시 2025): 단독 45.8%·아파트 43.9%·오피스텔 1.3%(1,476가구)", "work/20261008_youth_housing/kosis_DT_1JC1521.json", "2025")


# ================================================================ S16 청년 순이동·혼인
def s16():
    d = jload(RAW / "kosis_netmigration_gj.json")
    by = collections.defaultdict(dict)
    for r in d:
        if r["C2_NM"] == "계":
            by[r["C3_NM"]][r["PRD_DE"]] = int(r["DT"])
    years = ["2020", "2021", "2022", "2023", "2024", "2025"]
    bands = ["15 - 19세", "20 - 24세", "25 - 29세", "30 - 34세", "35 - 39세"]
    rows = []
    src = "KOSIS DT_1B26002 국내인구이동통계 시군구/성/연령(5세)별 순이동자수, 경주시, 성별 계(순이동 = 전입 − 전출)"
    for b in bands:
        rows.append([b.replace(" ", "")] + [by[b][y] for y in years] + [sum(by[b][y] for y in years), src, "T2", "5세 구간 원자료"])
    s2034 = [sum(by[b][y] for b in bands[1:4]) for y in years]
    rows.append(["20~34세(5세 구간 합: 20~24+25~29+30~34)"] + s2034 + [sum(s2034), src, "T2", "정리본 6년 합계 -7,249 = 이 행"])
    k = by["청년층(19 - 34세)"] if "청년층(19 - 34세)" in by else by.get("청년층(19-34세)")
    if k:
        rows.append(["청년층(19~34세, KOSIS 제공 합계)"] + [k[y] for y in years] + [sum(k[y] for y in years), src, "T2", "KOSIS가 따로 제공하는 청년층 합계. 5세 구간 합과 정의가 달라 값이 다름(-7,505)"])
    rows.append(["전 연령 계"] + [by["계"][y] for y in years] + [sum(by["계"][y] for y in years), src, "T2", "2025는 +860(순유입)"])
    assert sum(s2034) == -7249, sum(s2034)
    w("S16_청년_순이동_연령별_2020_2025.csv",
      ["연령", "2020", "2021", "2022", "2023", "2024", "2025", "6년합계", "출처", "등급", "비고"], rows,
      "경주시 연령별 순이동 2020~2025: 20~34세 6년 합계 -7,249명(2020 -1,951 → 2025 -349). 정리본 '연 약 1,200명'은 6년 평균",
      "archive/C_data/raw/kosis_netmigration_gj.json (processed/youth_city.json 과 일치)", "2020~2025",
      "2025는 순유출이 -349로 급감(25~29세 +4, 30~34세 +76, 35~39세 +131): 연도별 막대로 보이는 편이 정확. 정의: 전입−전출")
    m = jload(ROOT / "work" / "20261008_youth_housing" / "kosis_INH_1B83A35.json")
    n = jload(ROOT / "work" / "20261008_youth_housing" / "kosis_INH_1NW1037.json")
    mar = {r["PRD_DE"]: int(r["DT"]) for r in m}
    nw = {r["PRD_DE"]: int(r["DT"]) for r in n}
    rows = []
    for yr in sorted(set(mar) | set(nw)):
        rows.append([yr, nw.get(yr), mar.get(yr), "KOSIS INH_1NW1037 신혼부부수(시도/시/군/구) / INH_1B83A35 혼인건수(시도/시/군/구)", "T2",
                     "신혼부부 통계는 2024까지" if yr == "2025" else ""])
    assert nw["2015"] == 6062 and nw["2024"] == 3801 and mar["2025"] == 858
    w("S16b_신혼부부_혼인건수_경주시_2015_2025.csv",
      ["연도", "신혼부부_쌍(혼인 5년 이내 추정)", "혼인건수_건", "출처", "등급", "비고"], rows,
      "경주시 신혼부부 6,062쌍(2015)→3,801쌍(2024), 혼인 858건(2025)", "work/20261008_youth_housing/kosis_INH_1NW1037.json, kosis_INH_1B83A35.json", "2015~2025",
      "신혼부부 정의(혼인 5년 이내 등)는 KOSIS 표 주석 원문 미확인")


# ================================================================ S17 연혁
def s17():
    rows = [
        ["1918-12-28", "경주역 개업(서악~경주 1.2마일 협궤선 운수 개시)", "조선총독부 관보 제1924호(1919-01-09) 휘보 '통운'", "T1", "N(관보 기재: 운수개시 인가 1918-12-28)", "A-016 (archive/A_plans/A-S1-19190109-…관보1924호…gif)",
         "첫 역은 지금 자리가 아님(사정리, 김신재 2013). 흔히 인용되는 1918-11-01은 금호~서악 개통일(관보 제1872호)", "일치"],
        ["1936-12-01", "지금 자리(성동동)로 이전·표준궤 개축", "조선총독부고시 제640호(관보 제2955호, 1936-11-18) + 김신재(2013) 387쪽", "T1(고시 날짜)·T3(이전 사실)", "Y(1936-12-01부터 울산~경주 표준궤 개축)",
         "A-017 (archive/A_plans/A-S1-19361118-…관보2955호…png)", "고시 문언에 '이전'은 없음. 이전 사실은 김신재(2013) T3. 소재지 표기 황오리(관보)↔성동리(김신재) 불일치 미해결", "일치"],
        ["2010-11-01", "KTX 신경주역 개통(경부고속철도 2단계, 건천읍, 원도심 서쪽 직선 약 8.6km)", "한국철도공사 공사연혁", "T2", "미확인(로컬 원문 없음)", "public_profile_20260928.json s1_history",
         "2026-09-28 조사 에이전트가 원문 확인했다고 기록. 로컬 아카이브에 원문 파일 없음", "일치(원문 파일 미보유)"],
        ["2021-12-28", "경주역 폐역(영천~신경주·울산~포항 복선전철 개통으로 선로 이설)", "국토교통부고시 제2021-1234호(2021-11-17) + 국토교통부 보도참고자료 2021-12-27", "T1(노선 변경)·T2(정확한 날짜)",
         "N(고시는 '2021년 12월'만 기재, 12-28은 보도참고자료)", "A-013 · B-008 (archive/A_plans, archive/B_projects)", "마지막 열차 2021-12-27 밤 11:16 무궁화호(경주시 시정뉴스 2021-12-29, T2)", "일치"],
        ["2023-12-28", "'경주역' 명칭이 건천읍 KTX역(구 신경주역)으로 변경", "국토교통부고시 제2023-45호(2023-02-06) + 경주시 보도자료 2023-12-28", "T1(고시)·T2(시행 날짜)",
         "N(고시에 시행일 조항 없음, 실제 변경일은 보도자료)", "A-014 (archive/A_plans/A-S3-20230206-…고시2023-45호…)", "신경주역→경주역 개명 '2021년'은 오류", "일치"],
        ["2025-12-18", "옛 경주역 일원 도시재생 국가시범지구 후보 선정", "경주시 보도자료 2025-12-18 「옛 경주역 부지 '도시재생 국가시범지구' 후보 선정」", "T2", "Y(보도자료 날짜)", "gaps.md 2026-09-28 (B) 79,438㎡ 항목",
         "같은 보도자료가 '사업 대상지 7만 9,438㎡'를 적었으나 범위 정의 없음", "일치"],
        ["2026-01-22", "지구단위계획 결정 고시(고시 구역 156,460㎡, 주거용지 없음)", "경주시 고시 제2026-8호", "T1", "Y", "A-001 (archive/A_plans/A-S1-20260122-…고시2026-8호…)", "고시문에서 구역 156,460·용도별 면적 직접 확인", "일치"],
    ]
    w("S17_구경주역_연혁_날짜와_근거.csv",
      ["날짜", "사건", "근거_문서", "등급", "원문에_날짜_직접_기재", "아카이브_ID·파일", "비고", "정리본(20260928 한눈에 §3.4)_대조"], rows,
      "옛 경주역 연혁 7개 날짜와 근거(관보·고시 번호). 1918-12-28 개업 / 1936-12-01 이전 / 2010-11-01 KTX / 2021-12-28 폐역 / 2023-12-28 개명 / 2025-12-18 후보 / 2026-01-22 고시",
      "work/20260928_경주와_구경주역_한눈에_v1.md §3.4 · archive/90_derived/public_profile_20260928.json(s1_history.events) · archive/00_meta/index.csv(A-013~A-017, B-008)", "1918~2026",
      "2021-12-28·2023-12-28은 고시 원문에 날짜가 없고 보도자료(T2)가 날짜의 근거. 슬라이드 출처 줄에 둘을 함께 적을 것")
    rows = [
        ["1918-11-01", "금호~서악 구간 운수 개시(경주역 개업일 아님)", "조선총독부 관보 제1872호(1918-11-04) 휘보", "T1", "경주시 시정뉴스·최무현(2012)이 이 날짜를 경주역 개업일로 씀. 사용하지 않음"],
        ["2021-11-17", "국토교통부고시 제2021-1234호 고시일(경주역 노선 제외·폐지)", "A-013", "T1", "폐역일이 아니라 고시일"],
        ["2023-02-06", "국토교통부고시 제2023-45호 고시일(신경주역 역명 개정)", "A-014", "T1", "개명 시행일이 아니라 고시일"],
        ["2013-10-01(위키만)", "코레일 철도기념물 지정일", "위키(T4)", "T4", "지정 연도 2013은 「매거진 경주」150호(T2), 정확한 날짜는 T4뿐. 구 역사는 등록문화유산이 아님(국가유산청 목록 0건)"],
    ]
    w("S17b_혼동하기쉬운_날짜.csv", ["날짜", "무엇인가", "출처", "등급", "주의"], rows, "연혁 슬라이드에서 섞이기 쉬운 날짜(사용 금지·고시일)",
      "archive/00_meta/index.csv, archive/90_derived/public_profile_20260928.json", "1918~2023")


# ================================================================ S18 대상지 규제·면적
def s18():
    U = shape(jload(ROOT / "work/20261005_boundary_check/user_boundary_current_5187.geojson")["features"][0]["geometry"])
    Z = shape(jload(PROC / "gosi2026-8_zone_5187.geojson")["features"][0]["geometry"])
    t = Transformer.from_crs(4326, 5187, always_xy=True).transform
    uq = jload(RAW / "vworld_uq111.geojson")
    by = collections.defaultdict(list)
    for f in uq["features"]:
        by[f["properties"]["uname"]].append(shp_transform(t, shape(f["geometry"])))
    godo = jload(PROC / "godo_5187.geojson")
    gby = collections.defaultdict(list)
    for f in godo["features"]:
        gby[f["properties"]["godo_nm"]].append(shape(f["geometry"]))
    rows = []
    A = "면적 정의"
    rows += [
        [A, "시 구상(혁신지구 대상) 면적", 79438, "㎡", "정의 없음(고시 구역 156,460의 50.8%)", "경주시 보도자료 2025-12-18·2026-01-02", "T2(보도자료 원문 확보, 범위 정의 없음)",
         "79,438㎡ [T4, 원문 미확인]", "부분 일치(등급 표기 갱신 필요)", "gaps.md 2026-09-28: 원문은 확보, 범위 정의만 없음. 철도도심재생과 확인 필요"],
        [A, "고시 지구단위계획구역", 156460, "㎡", "성동동 40 일원 구역(고시 결정조서)", "경주시 고시 제2026-8호(2026-01-22)", "T1", "156,460㎡ [T1]", "일치", "지형도면 쇄선 추출 158,472㎡는 참고(+1.3%)"],
        [A, "본 계획 경계", round(U.area), "㎡", "사용자가 라이노에 그린 선(최종콘타모델_v2.3dm 2026-10-05 저장)", "work/20261005_boundary_check/user_boundary_current_5187.geojson", "사용자 경계", "218,478㎡", "일치", ""],
        [A, "본 계획 경계 중 고시 구역 안", round(U.intersection(Z).area), "㎡", "고시 구역 도면추출(158,472㎡)과의 교집합", "자체 계산(shapely, EPSG:5187)", "자체 계산", "", "(참고)", ""],
        [A, "본 계획 경계 중 고시 구역 밖", round(U.difference(Z).area), "㎡", f"본 계획 경계의 {U.difference(Z).area / U.area * 100:.1f}%", "자체 계산", "자체 계산", "", "(참고)", "work/20261005_boundary_check: 60,498㎡(27.7%)와 일치"],
        [A, "2022 지표조사 대상(철도부지 성동동 169-2 외 110필지)", 148770, "㎡", "전략계획 인용(시 주요업무계획 2021)·김권일 발표(지표조사 면적)", "경주시 도시재생 전략계획(변경) 2022 인쇄쪽 138(PDF 148쪽) / 김권일 2026-02 발표 PDF 22쪽", "T1(전략계획)·T2", "148,770㎡", "일치", "고시 구역과 범위가 다름"],
        [A, "철도부지 소유: 국가철도공단", 69790, "㎡", "148,770㎡의 46.9%", "경주시 도시재생 전략계획(변경) 2022 인쇄쪽 138", "T1", "철도공단 69,790", "일치", "시 주요업무계획(2021) 인용. 지번별 내역 미확보"],
        [A, "철도부지 소유: 한국철도공사", 78864, "㎡", "148,770㎡의 53.0%", "〃", "T1", "철도공사 78,864", "일치", ""],
        [A, "철도부지 소유: 기획재정부", 116, "㎡", "148,770㎡의 0.1%", "〃", "T1", "기재부 116", "일치", "69,790+78,864+116 = 148,770"],
    ]
    assert 69790 + 78864 + 116 == 148770
    # 용도지역(정확 겹침 + 5m 격자표본 + 고시)
    L = "용도지역"
    inter = {k: unary_union(v).intersection(U).area for k, v in by.items()}
    for k, lab, s5, sp in [("자연녹지지역", "자연녹지", 169550, 77.5), ("제2종일반주거지역", "제2종일반주거", 35600, 16.3), ("일반상업지역", "일반상업", 13575, 6.2)]:
        rows.append([L, f"{lab} — 본 계획 경계(정확 폴리곤 겹침)", round(inter[k]), "㎡", f"본 계획 경계 218,478㎡의 {inter[k] / U.area * 100:.1f}%", "V-World LT_C_UQ111 폴리곤 × 본 계획 경계, 자체 계산(shapely)", "T1 데이터·자체 계산",
                     "", "", ""])
        rows.append([L, f"{lab} — 본 계획 경계(5m 격자 표본)", s5, "㎡", f"{sp}% (±1%)", "work/20261005_logic_factcheck §2.2", "T1 데이터·자체 계산", f"{lab} {sp}%",
                     "일치" if abs(sp - inter[k] / U.area * 100) < 0.3 else "근사 일치", "정리본 값은 이 표본 계산. 정확 겹침과 ±0.2%p 차이(16.3↔16.2, 6.2↔6.4)" if k != "자연녹지지역" else ""])
    for lab, v, pc in [("자연녹지", 151116, 96.6), ("제2종일반주거", 4507, 2.9), ("일반상업", 837, 0.5)]:
        rows.append([L, f"{lab} — 고시 구역(결정조서)", v, "㎡", f"고시 구역 156,460㎡의 {pc}%", "경주시 고시 제2026-8호 용도지역 결정조서(변경 없음)", "T1", "", "(참고)", "고시 구역 기준과 본 계획 경계 기준 비율이 크게 다름(96.6% vs 77.5%)"])
    for lab, v, pc in [("자연녹지", 147645, 71.8), ("제2종일반주거", 31271, 15.2), ("일반상업", 26691, 13.0)]:
        rows.append([L, f"{lab} — v3 필지편입 경계(필지 단위 귀속)", v, "㎡", f"v3 경계 205,626㎡의 {pc}%", "전체기록 v1 §경계(v3 필지 귀속 계산)", "T2(연속지적, 자체 계산)", "", "(참고)", "경계 정의가 다른 이전 값. 현재 경계와 혼용 금지"])
    # 고도지구
    G = "고도지구"
    ginter = {k: unary_union(v).intersection(U).area for k, v in gby.items() if unary_union(v).intersects(U)}
    for k in ["도심20m지구", "도심15m지구", "최저고도지구"]:
        rows.append([G, f"{k} — 본 계획 경계(재계산)", round(ginter[k]), "㎡", f"본 계획 경계 218,478㎡의 {ginter[k] / U.area * 100:.1f}%", "V-World LT_C_UQ123 + 경북 고시 제2020-479호 × 본 계획 경계, 자체 계산",
                     "T1", {"도심20m지구": "20m 89%", "도심15m지구": "15m 9.8%", "최저고도지구": ""}[k],
                     {"도심20m지구": "불일치(기준 경계 상이)", "도심15m지구": "불일치(기준 경계 상이)", "최저고도지구": ""}[k], "work/20261005_plan_massing 문서의 191,260/24,610/8,366과 일치"])
    for lab, v, pc in [("도심20m지구", 184348, 89.0), ("도심15m지구", 20248, 9.8), ("최저고도지구", 8366, 4.0)]:
        rows.append([G, f"{lab} — v2 경계(이전 정본 207,205㎡)", v, "㎡", f"v2 경계의 {pc}%", "전체기록 v1 §1.4", "T1 데이터", "도심20m 89% / 15m 9.8%" if lab != "최저고도지구" else "", "정리본 값은 이 계열(v2 경계)", "정리본 §3 ⑥은 경계를 표기하지 않음. 같은 문서의 용도지역 77.5% 등은 본 계획 경계 기준"])
    for lab, v in [("도심20m지구", 145364), ("도심15m지구", 11143)]:
        rows.append([G, f"{lab} — 고시 구역(고시 결정조서 용도지구 괄호값)", v, "㎡", f"고시 구역 156,460㎡의 {v / 156460 * 100:.1f}%", "경주시 고시 제2026-8호 용도지구 결정조서(고시문 txt 838·859행)", "T1", "", "(참고)",
                     "조서 값: 20m 지구 744,750㎡ 중 구역 내 145,364, 15m 지구 354,666.8㎡ 중 구역 내 11,143(합 156,507은 구역 156,460과 47㎡ 차이)"])
    for k in ["도심20m지구", "도심15m지구", "최저고도지구"]:
        v = unary_union(gby[k]).intersection(Z).area
        rows.append([G, f"{k} — 고시 구역(도면추출 158,472㎡, 재계산)", round(v), "㎡", f"{v / Z.area * 100:.1f}%", "V-World LT_C_UQ123 × 고시 구역 도면, 자체 계산", "T1 데이터·자체 계산", "", "(참고)", "조서 값(145,364·11,143)과 ±1% 안에서 일치"])
    # 시굴
    H = "매장문화재"
    rows += [
        [H, "시굴조사 필요 면적", 145879, "㎡", "성동동 유물산포지 104,997 + 성동동사지Ⅱ 40,882 (2022 지표조사 148,770㎡ 중, 2,891㎡ 제외)", "김권일 2026-02-27 발표 PDF 22쪽", "T2", "시굴 대상 145,879㎡", "일치", ""],
        [H, "시굴 필요 면적 ÷ 고시 구역 면적", round(145879 / 156460 * 100, 1), "퍼센트", "145,879 ÷ 156,460", "자체 계산", "T2·T1 혼합", "고시 구역의 93%", "일치(산술) · 정의 주의",
         "두 면적의 공간 범위가 같지 않음(지표조사 148,770㎡ vs 고시 구역 156,460㎡) — '구역의 93%가 시굴 대상'은 근사 표현"],
        [H, "시굴 필요 면적 ÷ 2022 지표조사 면적", round(145879 / 148770 * 100, 1), "퍼센트", "145,879 ÷ 148,770", "자체 계산", "T2", "", "(참고)", "같은 조사 안의 비율이라 정의가 일관"],
        [H, "시굴 1단계(안) 면적", 58381, "㎡", "철도공단 43,886 + 한국철도공사 14,495", "구)경주역일원 매장유산 시굴조사 추진계획 PDF 6~7쪽", "T2", "", "(참고)", "실제 트렌치는 대상 면적의 10% 이내 약 5,900㎡"],
        [H, "시굴 비용(총계)", 306273000, "원", "현장 실조사일수 54일", "김권일 발표 PDF 24쪽", "T2", "", "(참고)", ""],
        [H, "정밀발굴 비용(총계, 기준안)", 6320204000, "원", "현장 실조사일수 633일(발표 요약 63~80억·630~700일)", "김권일 발표 PDF 25쪽", "T2", "", "(참고)", ""],
        [H, "발굴 유예 조건", None, "", "2m 미만 경미한 성토(표본·시굴 유예) / 성토 후 공원 조성 또는 주차장 시설(발굴 유예)", "김권일 발표 PDF 8쪽", "T2", "2m 미만 성토 + 성토 후 공원·주차장", "일치", "지하 개발은 이 조건에 없음"],
    ]
    # 결정도 용도 면적
    D = "결정도 용도 면적(고시 2026-8호)"
    for lab, v, note_s, memo in [("근린공원", 55415, "55,415", ""),
                                 ("상업(특별계획구역 1·2·3: 14,503+14,083+13,445)", 42031, "42,031", ""),
                                 ("공공청사(특별계획구역 4: 11,583+13,404)", 24987, "24,987", ""),
                                 ("문화시설(문화1·특별계획구역5)", 9770, "9,770", "주거용지 없음. 단 문화1(9,770㎡)의 허용용도가 제2종일반주거지역 건축물이라 공동주택 가능(고시 계획지침)"),
                                 ("주차장(특별계획구역 주차장1)", 5756, "5,756", ""),
                                 ("도로", 18501, "", "")]:
        rows.append([D, lab, v, "㎡", f"고시 구역 156,460㎡의 {v / 156460 * 100:.1f}%", "경주시 고시 제2026-8호 결정조서(archive/A_plans/…고시문-v1.txt)", "T1",
                     note_s, "일치" if note_s else "(정리본 미표기)", memo])
    assert 55415 + 42031 + 24987 + 9770 + 5756 + 18501 == 156460
    rows.append([D, "특별계획구역 7개소 합", 82544, "㎡", "개발 획지 5곳 모두 특별계획구역", "고시 제2026-8호", "T1", "", "(참고)", "세부개발계획 수립 전 건축 불가, 용도지역·지구 변경 포함(고시문)"])
    w("S18_대상지_면적_규제_수치와_기준범위.csv",
      ["항목군", "항목", "값", "단위", "기준범위_분모_산출", "출처", "등급", "정리본_표기", "정리본_대조", "비고"], rows,
      "대상지 면적 정의 3종·용도지역·고도지구·시굴·결정도 용도 면적·철도부지 소유 구분. 값마다 기준 경계(고시 구역 156,460 / v2 207,205 / 본 계획 218,478)를 명시",
      "archive/A_plans(고시문 txt) · work/20261005_boundary_check · archive/C_data/raw/vworld_uq111.geojson · processed/godo_5187.geojson · 전략계획 PDF 148쪽 · 김권일 발표 PDF 8·22·24·25쪽", "2022~2026",
      "정리본 '고도 20m 89%·15m 9.8%'는 v2 경계(207,205㎡) 값이며 본 계획 경계 기준은 87.5%·11.3%. 용도지역 77.5/16.3/6.2는 본 계획 경계 기준(5m 격자 표본)")


# ================================================================ S19 (보너스) 동서 우회율
def s19():
    d = jload(DER / "extent_diagnosis_20260928.json")
    zy = d["zone_y"]
    prof = d["detour_profile"]
    rows = []
    for p in prof:
        inz = zy[0] <= p["y"] <= zy[1]
        rows.append([p["y"], p["ratio"], "Y" if inz else "N", "폐선 양쪽 60m 지점 간 도로중심선 최단경로÷직선거리(육교 미포함), 50m 간격 단면",
                     "자체 분석: 연속수치지도(NGII) 도로중심선·철도 중심선 (pipeline/build_extent_diagnosis.py)", "T2(자체 분석, 현장 확인 전)"])
    r = [p["ratio"] for p in prof if zy[0] <= p["y"] <= zy[1]]
    rows.append(["구역 구간 18개 단면 중앙값", round(statistics.median(r), 2), "Y", f"단면 {len(r)}개, 최소 {min(r)}·최대 {max(r)}", "계산", "정리본 '중앙값 3.5, 최대 약 5.3'과 일치(최대 5.35)"])
    w("S19_동서_우회율_50m간격_단면.csv",
      ["단면_y좌표_EPSG5187", "우회율", "구역구간_안(Y/N)", "정의", "출처", "등급"], rows,
      "동서 보행 우회율(S19 보너스): 구역 구간 18개 단면 중앙값 3.5, 최대 5.35. 단일 지점 쌍(직선 601m→도로 1,531m)의 2.55와 정의가 다름",
      "archive/90_derived/extent_diagnosis_20260928.json(detour_profile, zone_y)", "2026-09-28 분석",
      "보행 인도·횡단보도 미반영, 육교(폭 3.2m) 제외. 최소 1.51(구역 남단)~최대 5.35(y=361,013 부근; 지도 작업자 재계산 5.349): 중앙값 하나로 요약하면 편차가 가려짐")
    ps = None
    for f in jload(DER / "public_profile_20260928.json")["facts"]:
        if f["id"] == "s1_wall":
            ps = f
    w("S19b_횡단불가구간_985m_육교_우회율2.55.csv",
      ["항목", "값", "단위", "정의", "출처", "등급"],
      [["도로 횡단 없는 구간", ps["value"], "m", "옛 선로를 따라 차가 건널 길이 없는 구간(남쪽 원효로·북쪽 폭 20m 도로 사이)", "public_profile_20260928.json s1_wall", "T2"],
       ["육교 폭", ps["overpass"][0]["width_m"], "m", "보행 육교 1개(길이 216.3m), 개방 여부 현장 확인 전", "public_profile_20260928.json s1_wall", "T2"],
       ["부지 양쪽 두 점 직선거리", ps["straight_m"], "m", "단일 지점 쌍", "public_profile_20260928.json s1_wall", "T2"],
       ["같은 두 점 도로망 거리", ps["network_m"], "m", "도로중심선 기준", "public_profile_20260928.json s1_wall", "T2"],
       ["우회율(단일 지점 쌍)", ps["detour"], "배", "도로망 거리÷직선거리 — 18개 단면 중앙값 3.5와 다른 정의", "public_profile_20260928.json s1_wall", "T2"]],
      "횡단 불가 구간 985m, 육교 1개(3.2m), 단일 지점 쌍 우회율 2.55", "archive/90_derived/public_profile_20260928.json(s1_wall)", "2026-09-28",
      "슬라이드에는 3.5(폐선 양쪽 60m, 육교 제외)만 쓰라는 정리본 §6 지침과 일치")


def write_manifest():
    with open(OUT / "MANIFEST.csv", "w", encoding="utf-8", newline="") as f:
        cw = csv.writer(f)
        cw.writerow(["file", "설명", "원자료 경로", "쪽/연도", "가로x세로 px", "비고"])
        for fn, d, s, per, note in MANIFEST:
            cw.writerow([fn, d, s, per, "-", note])
        cw.writerow(["README_data_series.md", "계열 표·정리본 대조·불일치 목록·권고", "이 폴더의 CSV와 각 CSV 열의 출처", "-", "-", "-"])
        cw.writerow(["_build_data_series.py", "이 폴더 S##_*.csv 재생성 스크립트(원자료는 읽기만 함)", "-", "-", "-", "PYTHONUTF8=1 로 실행"])
        for fn, d in [("detour_ratio_18sections.csv", "18개 단면 우회율 상세(좌표·도로망 거리)"), ("footfall_8zones.csv", "8구역 면적·ha당 유동 지도 도형 대조"),
                      ("m4_metrics_check.csv", "문제 ① 지표(985m·육교·우회율·37곳) 재산정 대조"),
                      ("m6_regulation_check.csv", "규제 수치(용도지역·고도지구) 지도 폴리곤 재산정 대조"),
                      ("siguel_digitized_5187.geojson", "시굴 대상 구역 도면 판독 도형(김권일 발표 그림 판독, T2 근사)")]:
            if (OUT / fn).exists():
                cw.writerow([fn, d, "(다른 작업자 산출 — 지도 정합 검증용)", "-", "-", "이 작업에서 만들거나 수정하지 않음(CSV는 UTF-8 BOM 있음). 해당 S## 값과 일치 확인"])


FUNCS = [s01, s02, s03, s04, s05, s06, s07, s08, s09, s10, s11, s12, s13, s14, s15, s16, s17, s18, s19]

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for fn in FUNCS:
        print(fn.__name__.upper())
        fn()
    write_manifest()
    print("done")
