# -*- coding: utf-8 -*-
"""연속수치지도(B020) 레이어 목록·개수·범위·속성 점검."""
import glob, os, warnings
warnings.filterwarnings("ignore")
import geopandas as gpd
import pyogrio
D = "C:/Users/OFFICE/Desktop/9_도시/대지/(B020)연속수치지도_202609132098/"
for f in sorted(glob.glob(D + "*.shp")):
    try:
        info = pyogrio.read_info(f, encoding="cp949")
        cols = list(info["fields"])
        n = info["features"]
        gt = info["geometry_type"]
        # 샘플 속성
        df = gpd.read_file(f, encoding="cp949", rows=3)
        sample = df.drop(columns="geometry").head(2).to_dict("records") if len(df) else []
        print(os.path.basename(f), n, gt, cols[:8])
        print("     ", str(sample)[:260])
    except Exception as e:
        print(os.path.basename(f), "ERR", e)
