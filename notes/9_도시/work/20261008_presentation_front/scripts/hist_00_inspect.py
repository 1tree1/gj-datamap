# -*- coding: utf-8 -*-
"""과거 항공사진·지도 TIF 메타 점검 (읽기 전용)"""
import os, sys, glob
import rasterio
from rasterio.errors import NotGeoreferencedWarning
import warnings
warnings.filterwarnings("ignore")
import tifffile

BASE = "C:/Users/OFFICE/Desktop/9_도시/대지/과거사진/경주 위성지도/"
files = sorted(glob.glob(BASE + "*.tif") + glob.glob(BASE + "*.TIF"))
files += sorted(glob.glob("C:/Users/OFFICE/Desktop/9_도시/대지/항공사진2025/*.tif"))
for f in files:
    print("=" * 100)
    print(os.path.basename(f), round(os.path.getsize(f) / 1e6, 1), "MB")
    try:
        with rasterio.open(f) as ds:
            print(" size", ds.width, ds.height, "bands", ds.count, "dtype", ds.dtypes[0], "crs", ds.crs)
            print(" transform", ds.transform)
            print(" bounds", ds.bounds)
            print(" overviews", ds.overviews(1) if ds.count else None)
            tags = ds.tags()
            if tags:
                print(" tags", dict(list(tags.items())[:10]))
            print(" compression", ds.compression, "block", ds.block_shapes[:1], "photometric", ds.photometric if hasattr(ds, 'photometric') else None)
    except Exception as e:
        print(" rasterio error:", e)
    try:
        with tifffile.TiffFile(f) as tf:
            p = tf.pages[0]
            print(" tifffile:", p.shape, p.dtype, "compression", p.compression, "tiled", p.is_tiled, "res", p.tags.get('XResolution').value if 'XResolution' in p.tags else None)
            for k in ('ModelPixelScaleTag', 'ModelTiepointTag', 'GeoKeyDirectoryTag', 'GeoAsciiParamsTag', 'ModelTransformationTag'):
                if k in p.tags:
                    print("  ", k, p.tags[k].value)
            print(" nPages", len(tf.pages))
    except Exception as e:
        print(" tifffile error:", e)
