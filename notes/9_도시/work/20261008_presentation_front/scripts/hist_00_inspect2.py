# -*- coding: utf-8 -*-
import os, sys, glob, warnings
warnings.filterwarnings("ignore")
import rasterio, tifffile
BASE = "C:/Users/OFFICE/Desktop/9_도시/대지/과거사진/경주 위성지도/"
files = sorted(set(os.path.normpath(f) for f in glob.glob(BASE + "*(B120)*")))
for f in files:
    print("=" * 80)
    print(os.path.basename(f), round(os.path.getsize(f) / 1e6, 1), "MB")
    if f.lower().endswith(('.tif', '.tiff')):
        try:
            with rasterio.open(f) as ds:
                print(" size", ds.width, ds.height, "bands", ds.count, ds.dtypes[0], "crs", ds.crs, "bounds", tuple(ds.bounds))
        except Exception as e:
            print(" rasterio error", e)
        try:
            with tifffile.TiffFile(f) as tf:
                p = tf.pages[0]
                print(" tifffile:", p.shape, p.dtype, "photometric", p.photometric, "compression", p.compression)
                for k in ('ModelPixelScaleTag', 'ModelTiepointTag', 'GeoKeyDirectoryTag', 'GeoAsciiParamsTag', 'GeoDoubleParamsTag', 'ModelTransformationTag', 'GDAL_METADATA', 'ImageDescription'):
                    if k in p.tags:
                        print("  ", k, str(p.tags[k].value)[:600])
        except Exception as e:
            print(" tifffile error", e)
    else:
        from PIL import Image
        Image.MAX_IMAGE_PIXELS = None
        im = Image.open(f)
        print(" PIL", im.size, im.mode, im.info.get('dpi'))
