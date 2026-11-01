from pyproj import CRS, Transformer
for src in ["EPSG:5176", "EPSG:2096", "EPSG:5174"]:
    t = Transformer.from_crs(src, "EPSG:5187", always_xy=True)
    print(src, "->5187:", t.description, "| accuracy", t.accuracy)
    try:
        print("   ops:", [ (o.name, o.accuracy) for o in t.operations ] if t.operations else None)
    except Exception as e:
        print("   ", e)
    # 지도 범위 모서리와 중심 변환
    for (x, y) in [(217584.6, 261703.2), (220290.8, 261703.2), (217584.6, 257744.2), (220290.8, 257744.2), (219000.0, 260000.0)]:
        print("   ", (x, y), "->", [round(v, 1) for v in t.transform(x, y)])
# 위경도 기준(Korean 1985 = EPSG:4162, 도 단위): 지도 중심에서 5176 -> 4162 -> 4326
t2 = Transformer.from_crs("EPSG:5176", "EPSG:4326", always_xy=True)
print("5176 center -> wgs84", t2.transform(219000, 260000), t2.description)
t3 = Transformer.from_crs("EPSG:4162", "EPSG:4326", always_xy=True)
print("4162->4326 shift at 129.2,35.84:", t3.transform(129.2, 35.84), t3.description)
