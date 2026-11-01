"""국가교통정보센터(ITS) 교통소통정보 — 링크별 속도 스냅샷 누적.

한 번 실행 = 5분 단위 현재 소통 1회 저장. 혼잡시간대는 여러 스냅샷을 모아 시간대별로 집계한다.
  python collect_its.py            # 1회
  python collect_its.py loop 5 288 # 5분 간격 288회(=24h)
출력: raw/its_traffic/<YYYYMMDD_HHMM>.json  (linkId, speed, travelTime, roadName)
키: .env DATA_GO_KR_KEY_CAR (its.go.kr 인증키). 필요 서비스: 교통소통정보 (돌발·CCTV·VDS는 마이페이지에서 항목 추가)
"""
import os, sys, json, time, datetime
from _common import load_env, get_json, RAW, S2_BBOX

OUT = RAW / "its_traffic"; OUT.mkdir(exist_ok=True)
# S2보다 넓게: 원도심 + 진입 국도까지 (약 7km × 6km)
BBOX = (129.17, 35.80, 129.27, 35.89)


def snapshot(key):
    j = get_json(f"https://openapi.its.go.kr:9443/trafficInfo?apiKey={key}&type=all&minX={BBOX[0]}&maxX={BBOX[2]}&minY={BBOX[1]}&maxY={BBOX[3]}&getType=json")
    if j.get("header", {}).get("resultCode") != 0: raise RuntimeError(j.get("header"))
    items = j["body"]["items"]
    ts = items[0]["createdDate"] if items else datetime.datetime.now().strftime("%Y%m%d%H%M00")
    rows = [{"linkId": it["linkId"], "speed": float(it["speed"]) if it["speed"] else None, "tt": float(it["travelTime"]) if it["travelTime"] else None,
             "road": it.get("roadName"), "s": it.get("startNodeId"), "e": it.get("endNodeId")} for it in items]
    p = OUT / f"{ts[:8]}_{ts[8:12]}.json"
    json.dump({"ts": ts, "bbox": BBOX, "n": len(rows), "rows": rows}, open(p, "w", encoding="utf-8"), ensure_ascii=False)
    return p, rows, ts


def main():
    load_env(); key = os.environ["DATA_GO_KR_KEY_CAR"]
    if len(sys.argv) > 1 and sys.argv[1] == "loop":
        every, n = int(sys.argv[2]), int(sys.argv[3])
        for i in range(n):
            try:
                p, rows, ts = snapshot(key); print(f"[{i+1}/{n}] {ts} {len(rows)} links → {p.name}", flush=True)
            except Exception as e: print("  오류", str(e)[:120], flush=True)
            time.sleep(every * 60)
        return 0
    p, rows, ts = snapshot(key)
    import collections
    roads = collections.Counter(r["road"] for r in rows); sp = [r["speed"] for r in rows if r["speed"]]
    print(f"{ts} 링크 {len(rows)} 저장 {p.name} | 속도 있음 {len(sp)} 평균 {sum(sp)/len(sp):.1f} km/h | 도로명 상위 {roads.most_common(8)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
