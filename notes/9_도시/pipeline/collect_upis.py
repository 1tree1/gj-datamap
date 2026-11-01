"""V-World UPIS 도시계획시설·용도지구 계열 레이어 — 부지 창. 출력 4326 GeoJSON (레이어명 속성 추가)."""
import os, sys, json, collections
from _common import load_env, get_json, save, RAW
from collect_vworld import wfs, BBOX

LAYERS = {  # 코드: (슬러그, 추정 명칭 — 속성으로 검증)
    "LT_C_UPISUQ151": "도시계획시설_도로",
    "LT_C_UPISUQ152": "도시계획시설_교통(주차장·철도)",
    "LT_C_UPISUQ153": "도시계획시설_공원·광장",
    "LT_C_UPISUQ155": "도시계획시설_학교·공공청사",
    "LT_C_UPISUQ161": "도시계획시설_기타(지구단위·대안지구)",
    "LT_C_UQ141": "지구단위계획구역",
}


def main():
    load_env(); key = os.environ["VWORLD_KEY"]; h = {"Referer": os.environ["VWORLD_DOMAIN"], "User-Agent": "Mozilla/5.0"}
    allf = []
    for code, name in LAYERS.items():
        try: feats, total = wfs(code, key, h, bbox=BBOX)
        except Exception as e: print(f"  {code} 실패 {str(e)[:100]}"); continue
        for f in feats: f["properties"]["_layer"] = code; f["properties"]["_layer_nm"] = name
        keys = list(feats[0]["properties"].keys()) if feats else []
        vals = collections.Counter((f["properties"].get("dgm_nm") or f["properties"].get("ucb_nm") or f["properties"].get("uname") or f["properties"].get("name") or "?") for f in feats)
        print(f"  {code} {name}: {len(feats)}건  속성 {keys[:10]}  값 {vals.most_common(6)}")
        allf += feats
    save({"type": "FeatureCollection", "features": allf}, RAW / "vworld_upis.geojson")
    return 0


if __name__ == "__main__":
    sys.exit(main())
