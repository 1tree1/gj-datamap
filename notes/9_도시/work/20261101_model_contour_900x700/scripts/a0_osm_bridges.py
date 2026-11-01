# OSM에서 북천(알천) 위 다리(bridge=*) 형상을 받아 모델 좌표로 저장
import json, sys, time, urllib.parse, urllib.request
from pathlib import Path
import numpy as np
from pyproj import Transformer
sys.stdout.reconfigure(encoding="utf-8")
W = Path(__file__).resolve().parents[1]
UA = {"User-Agent": "gyeongju-model-research/1.0 (study use)"}
q = ('[out:json][timeout:60];(way["bridge"](35.846,129.212,35.858,129.232);'
     'way["waterway"](35.846,129.212,35.858,129.232););out geom tags;')
d = None
for url in ("https://overpass-api.de/api/interpreter", "https://overpass.private.coffee/api/interpreter", "https://overpass.kumi.systems/api/interpreter"):
    try:
        req = urllib.request.Request(url, data=urllib.parse.urlencode({"data": q}).encode(), headers=UA)
        d = json.load(urllib.request.urlopen(req, timeout=90)); break
    except Exception as e:
        print("fail", url, e); time.sleep(2)
xf = json.load(open(W / "data/xf_5179.json")); s = xf["s"]; R = np.array(xf["R"]); t = np.array(xf["t"])
T = Transformer.from_crs(4326, 5179, always_xy=True)
m = lambda lon, lat: (s * (R @ np.array(T.transform(lon, lat))) + t).tolist()
out = []
for e in d["elements"]:
    tg = e.get("tags", {})
    pts = [m(p["lon"], p["lat"]) for p in e["geometry"]]
    out.append({"id": e["id"], "tags": tg, "pts": pts})
    if "bridge" in tg:
        print(e["id"], tg.get("name"), tg.get("bridge:name"), tg.get("highway"), tg.get("railway"), tg.get("bridge"), tg.get("layer"), tg.get("lanes"), tg.get("width"), "len %.1f mm" % sum(np.hypot(*np.diff(np.array(pts), axis=0).T)))
    else:
        print("WATER", e["id"], tg.get("name"), tg.get("waterway"))
json.dump(out, open(W / "data/osm_bridges_model.json", "w", encoding="utf-8"), ensure_ascii=False)
