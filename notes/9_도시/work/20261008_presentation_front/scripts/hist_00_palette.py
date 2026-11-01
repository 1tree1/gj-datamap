# -*- coding: utf-8 -*-
import glob, os, warnings
warnings.filterwarnings("ignore")
import numpy as np, tifffile
BASE = "C:/Users/OFFICE/Desktop/9_도시/대지/과거사진/경주 위성지도/"
for f in sorted(set(os.path.normpath(x) for x in glob.glob(BASE + "*(B120)*.tif"))):
    with tifffile.TiffFile(f) as tf:
        p = tf.pages[0]
        print(os.path.basename(f)[:30].encode('ascii','replace').decode(), p.photometric, p.dtype, p.shape, p.bitspersample)
        if 'ColorMap' in p.tags:
            cm = np.array(p.tags['ColorMap'].value).reshape(3, -1)
            n = cm.shape[1]
            print("   colormap entries", n, "first 4:", (cm[:, :4] // 257).T.tolist(), "last 2:", (cm[:, -2:] // 257).T.tolist())
        a = p.asarray()
        if a.ndim == 2:
            vals, cnt = np.unique(a[::8, ::8], return_counts=True)
            print("   unique values", len(vals), "top:", sorted(zip(cnt.tolist(), vals.tolist()), reverse=True)[:5])
