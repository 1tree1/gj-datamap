"""한국관광공사 지역별 방문자수(KT 이동통신) — 경주시(47130) 일별 현지인/외지인/외국인.
API는 지역 파라미터가 없어 전국을 받아 경주만 남긴다(1일 ≈ 750행). 개발계정 1,000회/일 한도 → 한 호출에 numOfRows=1000."""
import os, sys, json, datetime
from _common import load_env, get_json, RAW

SIG = "47130"


def day(key, ymd):
    rows, page = [], 1
    while True:
        j = get_json(f"https://apis.data.go.kr/B551011/DataLabService/locgoRegnVisitrDDList?serviceKey={key}&numOfRows=1000&pageNo={page}&MobileOS=ETC&MobileApp=gj&_type=json&startYmd={ymd}&endYmd={ymd}")
        b = j["response"]["body"]; items = (b.get("items") or {}).get("item") or []
        rows += [r for r in items if r["signguCode"] == SIG]
        if page * 1000 >= int(b.get("totalCount", 0)) or not items: break
        page += 1
    return rows


def main():
    load_env(); key = os.environ["DATA_GO_KR_KEY"]
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    out_p = RAW / "visitors_gyeongju_daily.json"
    out = json.load(open(out_p, encoding="utf-8")) if out_p.exists() else {}
    end = datetime.date(2026, 8, 31)
    for i in range(n):
        d = (end - datetime.timedelta(days=i)).strftime("%Y%m%d")
        if d in out: continue
        rows = day(key, d)
        out[d] = {r["touDivNm"].split("(")[0]: float(r["touNum"]) for r in rows} | {"요일": rows[0]["daywkDivNm"] if rows else None}
        if i % 10 == 0: print(" ", d, out[d])
    json.dump(out, open(out_p, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    days = sorted(out); tot = [sum(v for k, v in out[d].items() if k != "요일") for d in days]
    print(f"저장 {out_p.name}: {len(days)}일 ({days[0]}~{days[-1]})  일평균 방문자 {sum(tot)/len(tot):,.0f}  최대 {max(tot):,.0f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
