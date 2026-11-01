"""종교시설 레이어에 공식 현황(경주시 종교시설현황 2025-02-06)에 없는 시설을 추가한다.
경주시 현황 파일에는 '이슬람' 구분 자체가 없다 — 외국인주민 22,467명 중 이슬람권 국적이 3,000명 이상인데 시설이 0으로 보이는 문제.
collect_schools_religion.py 실행 뒤에 돌린다(덮어써도 다시 붙일 수 있게 분리). 이름이 이미 있으면 건너뛴다.
좌표: V-World 지오코더(도로명 → 지번). 등급: 시설 존재는 현장·언론 확인(T4), 좌표는 지오코딩."""
import sys, json, re, urllib.parse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import load_env, get_json, PROCESSED

EXTRA = [
    {"name": "경주이슬람센터", "religion": "이슬람", "kind_raw": "이슬람(추가)", "addr": "원화로281번길 22", "dong": "성건동", "phone": "",
     "source": "경주시 종교시설현황 2025-02-06에 항목 없음 → 수동 추가 (2026-09-21, 시설 존재 T4, 좌표 V-World 지오코더)"},
]


def geocode(addr, VK, H):
    a = re.sub(r"\(.*?\)", "", addr).strip()
    for typ in ("ROAD", "PARCEL"):
        try:
            r = get_json(f"https://api.vworld.kr/req/address?service=address&request=getcoord&version=2.0&crs=EPSG:4326&type={typ}&address={urllib.parse.quote('경상북도 경주시 ' + a)}&format=json&key={VK}", H, retries=1)["response"]
            if r["status"] == "OK": return float(r["result"]["point"]["x"]), float(r["result"]["point"]["y"]), "V-World " + typ
        except Exception: pass
    return None


def main():
    env = load_env(); VK = env["VWORLD_KEY"]; H = {"Referer": env.get("VWORLD_DOMAIN", ""), "User-Agent": "Mozilla/5.0"}
    p = PROCESSED / "poi_religion_4326.geojson"; fc = json.load(open(p, encoding="utf-8"))
    have = {f["properties"]["name"] for f in fc["features"]}; n = 0
    for e in EXTRA:
        if e["name"] in have: print("  이미 있음:", e["name"]); continue
        g = geocode(e["addr"], VK, H)
        if not g: print("  지오코딩 실패:", e["name"], e["addr"]); continue
        lon, lat, note = g[0], g[1], ""
        # 같은 주소의 기존 시설(예: 세움교회, 원화로281번길 22 동일 건물)과 점이 완전히 겹치면 라벨 하나가 숨는다 → 동쪽으로 8m 비켜 놓고 기록
        if any(abs(f["geometry"]["coordinates"][0] - lon) < 1e-6 and abs(f["geometry"]["coordinates"][1] - lat) < 1e-6 for f in fc["features"]):
            lon += 8 / (111320 * 0.81); note = "동일 주소 시설과 겹쳐 8m 동측 표시"
        fc["features"].append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [round(lon, 6), round(lat, 6)]}, "properties": {**e, "geocode": g[2] + (" · " + note if note else "")}})
        print(f"  추가: {e['name']} {e['addr']} → {g[0]:.6f},{g[1]:.6f} ({g[2]})"); n += 1
    json.dump(fc, open(p, "w", encoding="utf-8"), ensure_ascii=False)
    print("religion", len(fc["features"]), "건, 추가", n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
