"""경주시 버스 관련 정보_GW (data.go.kr 15158687) — 노선·정류장·실시간 위치.
host: apis.data.go.kr/5050000/openapi  (getRouteNoList / getSttnNoList / getRouteAcctoBusLcList)
2026-09-17 현재 경주시 백엔드 504 SERVICETIMEOUT — 정류장은 국토부 전국 파일(busstops_gj.geojson)로 대체 중. 서버 복구 시 실행."""
import os, sys, json
from _common import load_env, get_json, RAW

B = "https://apis.data.go.kr/5050000/openapi"


def main():
    load_env(); key = os.environ["DATA_GO_KR_KEY"]
    for path, slug in [("/getRouteNoList", "bus_routes"), ("/getSttnNoList", "bus_stops_gj_api")]:
        rows, page = [], 1
        while True:
            j = get_json(f"{B}{path}?serviceKey={key}&pageNo={page}&numOfRows=500&type=json", retries=2)
            body = j.get("response", {}).get("body", {}); items = (body.get("items") or {}).get("item") or []
            items = [items] if isinstance(items, dict) else items; rows += items
            if len(rows) >= int(body.get("totalCnt") or body.get("totalCount") or 0) or not items: break
            page += 1
        json.dump(rows, open(RAW / f"{slug}.json", "w", encoding="utf-8"), ensure_ascii=False)
        print(f"{slug}: {len(rows)}건", list(rows[0].keys()) if rows else "")
    return 0


if __name__ == "__main__":
    sys.exit(main())
