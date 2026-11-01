"""한국관광공사 지역별 방문자수(KT 이동통신) — 경주시(47130) 일별 현지인/외지인/외국인, 기간 지정 수집.

collect_visitors.py 의 범위 확장판. 기존 raw/visitors_gyeongju_daily.json 에 이어 쓰고(값이 있는 날짜는 건너뜀),
월별·요일별·구분별 집계를 processed/visitors_gyeongju_summary.json 으로 낸다.

  python collect_visitors_range.py 20240901 20260818
  python collect_visitors_range.py sum          # 재집계만

주의
  - API는 지역 파라미터가 없어 전국(1일 약 750행)을 받아 경주만 남긴다. 1일 = 1콜. 개발계정 1,000콜/일.
  - '현지인'은 경주시 거주자이고 관광객이 아니다. 관광객 = 외지인 + 외국인으로 본다.
  - 최신 2주가량은 값이 비어 온다(집계 지연). 빈 날은 저장하되 집계에서 제외한다.
  - 통신 기반 추정치(T2)이며 시군구 총량이다. 부지(S1) 하나의 근거로 쓰지 않는다.
"""
import os, sys, json, time, datetime, collections
from _common import load_env, get_json, RAW, PROCESSED

SIG = "47130"
SRC = "한국관광공사 한국관광 데이터랩 DataLabService/locgoRegnVisitrDDList (KT 이동통신 기반 추정 방문자, 시군구 일별, T2)"
KEYS = ["현지인", "외지인", "외국인"]


def day(key, ymd):
    rows, page = [], 1
    while True:
        j = get_json(f"https://apis.data.go.kr/B551011/DataLabService/locgoRegnVisitrDDList?serviceKey={key}&numOfRows=1000&pageNo={page}&MobileOS=ETC&MobileApp=gj&_type=json&startYmd={ymd}&endYmd={ymd}")
        b = j["response"]["body"]; items = (b.get("items") or {}).get("item") or []
        if isinstance(items, dict): items = [items]
        rows += [r for r in items if r.get("signguCode") == SIG]
        if page * 1000 >= int(b.get("totalCount", 0)) or not items: break
        page += 1
    return rows


def summarize(out):
    days = sorted(d for d in out if any(k != "요일" for k in out[d]))
    mon = collections.defaultdict(lambda: collections.defaultdict(float)); mon_n = collections.Counter()
    dow = collections.defaultdict(lambda: collections.defaultdict(float)); dow_n = collections.Counter()
    for d in days:
        m = d[:6]; mon_n[m] += 1
        for k in KEYS: mon[m][k] += out[d].get(k, 0.0)
        w = out[d].get("요일")
        if w:
            dow_n[w] += 1
            for k in KEYS: dow[w][k] += out[d].get(k, 0.0)
    res = {
        "src": SRC, "days": len(days), "range": [days[0], days[-1]] if days else None,
        "daily": {d: {k: round(out[d].get(k, 0.0)) for k in KEYS} | {"요일": out[d].get("요일")} for d in days},
        "monthly": {m: {**{k: round(mon[m][k]) for k in KEYS}, "days": mon_n[m],
                        "관광객": round(mon[m]["외지인"] + mon[m]["외국인"]),
                        "일평균_관광객": round((mon[m]["외지인"] + mon[m]["외국인"]) / mon_n[m]),
                        "일평균_외국인": round(mon[m]["외국인"] / mon_n[m]),
                        "외국인_비율": round(mon[m]["외국인"] / (mon[m]["외지인"] + mon[m]["외국인"]) * 100, 2) if mon_n[m] else None,
                        "완전한달": mon_n[m] >= 28} for m in sorted(mon)},
        "dow_avg": {w: {k: round(dow[w][k] / dow_n[w]) for k in KEYS} | {"n": dow_n[w]} for w in dow},
        "avg": {k: round(sum(out[d].get(k, 0.0) for d in days) / len(days)) for k in KEYS} if days else {},
    }
    if days:
        res["avg"]["관광객"] = res["avg"]["외지인"] + res["avg"]["외국인"]
        res["avg"]["외국인_비율"] = round(res["avg"]["외국인"] / res["avg"]["관광객"] * 100, 2)
    json.dump(res, open(PROCESSED / "visitors_gyeongju_summary.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"\n저장: {len(days)}일 {res['range']}  일평균 외지인 {res['avg'].get('외지인'):,} · 외국인 {res['avg'].get('외국인'):,} (관광객의 {res['avg'].get('외국인_비율')}%)")
    for m, r in res["monthly"].items():
        if r["완전한달"]: print(f"  {m}  관광객 {r['관광객']:>10,}  일평균 {r['일평균_관광객']:>8,}  외국인 {r['외국인']:>8,} ({r['외국인_비율']}%)")


def main():
    load_env(); key = os.environ["DATA_GO_KR_KEY"]
    a = datetime.datetime.strptime(sys.argv[1], "%Y%m%d").date()
    b = datetime.datetime.strptime(sys.argv[2], "%Y%m%d").date()
    p = RAW / "visitors_gyeongju_daily.json"
    out = json.load(open(p, encoding="utf-8")) if p.exists() else {}
    todo = [(a + datetime.timedelta(days=i)).strftime("%Y%m%d") for i in range((b - a).days + 1)]
    todo = [d for d in todo if d not in out or not any(k != "요일" for k in out[d])]
    print(f"수집 대상 {len(todo)}일 ({a}~{b}), 기존 {len(out)}일", flush=True)
    t0 = time.time()
    for i, d in enumerate(todo):
        try:
            rows = day(key, d)
        except Exception as e:
            print("  실패", d, str(e)[:80], flush=True); continue
        out[d] = {r["touDivNm"].split("(")[0]: float(r["touNum"]) for r in rows} | {"요일": rows[0]["daywkDivNm"] if rows else None}
        if i % 25 == 0:
            el = time.time() - t0
            print(f"  [{i+1}/{len(todo)}] {d} {out[d]}  {el:.0f}s (남은 예상 {el/(i+1)*(len(todo)-i-1)/60:.0f}분)", flush=True)
            json.dump(out, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    json.dump(out, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    summarize(out)
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "sum":
        summarize(json.load(open(RAW / "visitors_gyeongju_daily.json", encoding="utf-8"))); sys.exit(0)
    sys.exit(main())
