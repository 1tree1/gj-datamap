"""S0 사용자 라이노 도면(roads·sidewalks·parcels, 평면 좌표 그대로) → shapely 정리.
입력: data/plan_objects_rhino_export.json (라이노 aardvark 슬롯에서 x>1,160,000 객체를 내보낸 것. 선택된 복사본 A는 x≈1,167,2xx)
출력: data/geo.pkl — parcels(14), roads(2), walks(4), U(통합 경계), bld(구 역사 평면 외곽선)
좌표는 라이노 평면 좌표(실측 m, 맥락 모형을 ×2·−33.79° 회전한 같은 좌표계)."""
import json, os, pickle
from shapely.geometry import Polygon
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "..", "data")
objs = json.load(open(os.path.join(D, "plan_objects_rhino_export.json"), encoding="utf-8"))
A = [o for o in objs if o["bbox"][0] > 1167190 and o["type"] == "Brep" and "loops" in o]


def poly_of(o):
    outer = [l["pts"] for l in o["loops"] if l["kind"].endswith("Outer")]
    inner = [l["pts"] for l in o["loops"] if l["kind"].endswith("Inner")]
    return Polygon([(p[0], p[1]) for p in outer[0]], [[(p[0], p[1]) for p in r] for r in inner]).buffer(0)


parcels, roads, walks, bld = [], [], [], None
for o in A:
    L = o["layer"].split("::")[-1]
    P = poly_of(o)
    if L == "도로":
        roads.append(dict(id=o["id"], g=P))
    elif L == "보도":
        walks.append(dict(id=o["id"], g=P))
    elif L == "빌딩":
        bld = dict(id=o["id"], g=P, bbox=o["bbox"], vol=o.get("volume"))
    else:
        parcels.append(dict(id=o["id"], layer=L, g=P, area=P.area, rep=P.representative_point().coords[0]))
U = unary_union([x["g"] for x in parcels] + [x["g"] for x in roads] + [x["g"] for x in walks])
out = dict(parcels=parcels, roads=roads, walks=walks, U=U, bld=bld)
pickle.dump(out, open(os.path.join(D, "geo.pkl"), "wb"))
if __name__ == "__main__":
    print("parcels %d  roads %d  walks %d" % (len(parcels), len(roads), len(walks)))
    print("parcel sum %.2f | road %.2f | walk %.2f | U %.2f (%s, holes %d)" % (
        sum(p["area"] for p in parcels), sum(r["g"].area for r in roads), sum(w["g"].area for w in walks), U.area, U.geom_type,
        len(U.interiors) if U.geom_type == "Polygon" else -1))
    for p in sorted(parcels, key=lambda p: -p["rep"][1]):
        print("%-60s %9.2f  rep(%.0f,%.0f)" % (p["layer"][:58], p["area"], p["rep"][0], p["rep"][1]))
