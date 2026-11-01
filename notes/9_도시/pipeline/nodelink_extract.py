"""전국 표준노드링크 zip → 경주 창 링크만 GeoJSON(4326). ITS trafficInfo의 linkId와 조인 키(LINK_ID)."""
import sys, json, zipfile, io
import shapefile
from pyproj import Transformer, CRS
from _common import RAW, PROCESSED
from collect_its import BBOX

Z = RAW / "nodelink_20260914.zip"


def main():
    z = zipfile.ZipFile(Z)
    prj = z.read("MOCT_LINK.prj").decode("utf-8", "replace")
    crs = CRS.from_wkt(prj); print("SHP CRS:", crs.name, "| EPSG:", crs.to_epsg())
    tr = Transformer.from_crs(crs, "EPSG:4326", always_xy=True)
    # bbox를 원 좌표계로
    inv = Transformer.from_crs("EPSG:4326", crs, always_xy=True)
    x0, y0 = inv.transform(BBOX[0], BBOX[1]); x1, y1 = inv.transform(BBOX[2], BBOX[3])
    r = shapefile.Reader(shp=io.BytesIO(z.read("MOCT_LINK.shp")), shx=io.BytesIO(z.read("MOCT_LINK.shx")), dbf=io.BytesIO(z.read("MOCT_LINK.dbf")), encoding="cp949")
    fields = [f[0] for f in r.fields[1:]]; print("필드:", fields)
    feats = []
    for i in range(len(r)):
        s = r.shape(i)
        bx = s.bbox
        if bx[2] < x0 or bx[0] > x1 or bx[3] < y0 or bx[1] > y1: continue
        rec = dict(zip(fields, r.record(i)))
        pts = [tr.transform(x, y) for x, y in s.points]
        # 멀티파트 처리
        parts = list(s.parts) + [len(s.points)]
        lines = [[[round(x, 6), round(y, 6)] for x, y in pts[parts[k]:parts[k + 1]]] for k in range(len(parts) - 1)]
        geom = {"type": "LineString", "coordinates": lines[0]} if len(lines) == 1 else {"type": "MultiLineString", "coordinates": lines}
        props = {k: (v.strip() if isinstance(v, str) else v) for k, v in rec.items() if k in ("LINK_ID", "F_NODE", "T_NODE", "LANES", "ROAD_RANK", "ROAD_TYPE", "ROAD_NO", "ROAD_NAME", "MAX_SPD", "LENGTH", "REST_VEH", "REST_W", "REST_H")}
        feats.append({"type": "Feature", "geometry": geom, "properties": props})
    fc = {"type": "FeatureCollection", "features": feats}
    p = PROCESSED / "nodelink_gj_4326.geojson"; p.write_text(json.dumps(fc, ensure_ascii=False), encoding="utf-8")
    print(f"경주 창 링크 {len(feats)}개 → {p.name}")
    import collections
    print("  ROAD_RANK:", collections.Counter(f["properties"].get("ROAD_RANK") for f in feats).most_common())
    return 0


if __name__ == "__main__":
    sys.exit(main())
