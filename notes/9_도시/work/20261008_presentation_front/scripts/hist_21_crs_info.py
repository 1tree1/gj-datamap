from pyproj import CRS, Transformer
for code in [5173, 5174, 5175, 5176, 5177, 5178, 2096, 2097, 2098, 5186, 5187, 5179, 5181, 5182, 5183, 5184, 5185, 5188, 3857]:
    try:
        c = CRS.from_epsg(code)
        p = c.to_dict()
        print(code, c.name, "|", {k: p.get(k) for k in ("lat_0", "lon_0", "k", "x_0", "y_0", "ellps", "towgs84")})
    except Exception as e:
        print(code, "ERR", e)
# 경주 중심 (5187 219780,360850) -> 각 좌표계
t = Transformer.from_crs("EPSG:5187", "EPSG:4326", always_xy=True)
lon, lat = t.transform(219780, 360850)
print("center lon/lat", lon, lat)
for code in [5176, 2096, 5174, 5186, 5179]:
    try:
        t2 = Transformer.from_crs("EPSG:5187", f"EPSG:{code}", always_xy=True)
        print(code, t2.transform(219780, 360850))
    except Exception as e:
        print(code, "ERR", e)
