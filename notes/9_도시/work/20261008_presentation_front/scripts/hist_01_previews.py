# -*- coding: utf-8 -*-
"""모든 원본 영상의 축소 미리보기 생성 (scratchpad/prev). 읽기 전용."""
import os, glob, warnings, sys
warnings.filterwarnings("ignore")
import numpy as np
import rasterio
from rasterio.enums import Resampling
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

SCR = "C:/Users/OFFICE/AppData/Local/Temp/claude/C--Users-OFFICE-Desktop-9---/b98333f0-4ddf-4213-a0db-66cb837b3d35/scratchpad/"
OUT = SCR + "prev/"
BASE = "C:/Users/OFFICE/Desktop/9_도시/대지/과거사진/경주 위성지도/"
ALT = "C:/Users/OFFICE/Desktop/9_도시/대지/항공사진2025/"

items = {
 "a1954": BASE + "(B040)항공사진_195402001900010114.tif",
 "a1968": BASE + "(B040)항공사진_196800000200110024.tif",
 "a1982": BASE + "(B040)항공사진_198206000100180074.tif",
 "a2009": BASE + "(B040)항공사진_200903001200330066.TIF",
 "a2024": BASE + "(B040)항공사진_202402505C00370049.tif",
 "a2025_62": BASE + "(B040)항공사진_202504507C03060062.tif",
 "a2025_64": ALT + "(B040)항공사진_202504507C03070064.tif",
 "a2025_65": ALT + "(B040)항공사진_202504507C03070065.tif",
 "o2015": BASE + "(B060)정사영상_2015_35901069s.tif",
 "o2021": BASE + "(B060)정사영상_2021_35901069.tif",
 "o2025": BASE + "(B060)정사영상_2025_35901069.tif",
 "m1916": BASE + "(B120)종이지도_1916_경주_O00000016108_10000.tif",
 "m1956": BASE + "(B120)종이지도_1956_경주_SH0359015605_050k.tif",
 "m1969": BASE + "(B120)종이지도_1969_경주_SH3590146901_025k.tif",
 "m1972": BASE + "(B120)종이지도_1972_경주_L03590147201_025k.tif",
 "m1976": BASE + "(B120)종이지도_1976_경주_359010697601_005k.tif",
 "m1984": BASE + "(B120)종이지도_1984_경주_359010698401_005k.tif",
 "m1998": BASE + "(B120)종이지도_1998_경주_SH0359019803_050k.tif",
 "m2005": BASE + "(B120)종이지도_2005_경주_359014_2007_18200469615173_025k.tif",
 "m2024": BASE + "(B120)종이지도_2024_경주_35901_050k.tif",
}
maxdim = int(sys.argv[1]) if len(sys.argv) > 1 else 2400
only = sys.argv[2:] 
for k, f in items.items():
    if only and k not in only: continue
    if not os.path.exists(f):
        print("missing", k, f); continue
    with rasterio.open(f) as ds:
        w, h = ds.width, ds.height
        s = max(w, h) / maxdim
        ow, oh = int(w / s), int(h / s)
        if ds.count >= 3:
            arr = ds.read([1, 2, 3], out_shape=(3, oh, ow), resampling=Resampling.average)
            img = np.transpose(arr, (1, 2, 0))
        else:
            arr = ds.read(1, out_shape=(oh, ow), resampling=Resampling.average)
            if arr.dtype == bool or ds.dtypes[0] == 'bool':
                arr = (arr.astype(np.uint8) * 255)
            img = arr
        Image.fromarray(img.astype(np.uint8)).save(OUT + k + f"_{maxdim}.png")
        print(k, (w, h), "->", (ow, oh), "scale", round(s, 3))
