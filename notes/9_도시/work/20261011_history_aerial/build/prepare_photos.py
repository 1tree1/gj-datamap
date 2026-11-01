from pathlib import Path
from PIL import Image
import numpy as np
import json

Image.MAX_IMAGE_PIXELS = None
ROOT = Path(r'C:\Users\OFFICE\Desktop\9_도시')
OUT = ROOT / 'work/20261011_history_aerial/build'
RAW = ROOT / '대지/과거사진/경주 위성지도'
TRANS = ROOT / 'work/20261008_presentation_front/research/hist_transforms'
O = np.array([[2/3,0,-600+1/3],[0,-2/3,800-1/3],[0,0,1.]])
H0 = np.array([[.2,-.015,-1243],[-.015,-.2,2937.5],[0,0,1.]])
# Approximate historical registration, using surviving street intersections.
# Coordinates below refer to the initial 1200 x 1600 comparison preview.
src = np.array([[216,838],[492,848],[505,1142],[182,1230]],float)
dst = np.array([[133,838],[435,838],[465,1140],[138,1258]],float)
A = np.column_stack([src,np.ones(len(src))])
X = np.linalg.lstsq(A,dst,rcond=None)[0]
K = np.vstack([X.T,[0,0,1]])
# Source -> initial preview -> manually registered preview -> geographic relative metres.
geo_to_preview = np.array([[1,0,600],[0,-1,800],[0,0,1.]])
H1954 = np.linalg.inv(geo_to_preview) @ K @ geo_to_preview @ H0
records = []
for year, filename, H in [
    (1954,'(B040)항공사진_195402001900010114.tif',H1954),
    (2009,'(B040)항공사진_200903001200330066.TIF',np.array(json.loads((TRANS/'a2009.json').read_text())['H_src2geo_rel']))
]:
    inverse = np.linalg.inv(H) @ O
    inverse /= inverse[2,2]
    photo = Image.open(RAW / filename)
    result = photo.transform((1800,2400),Image.Transform.PERSPECTIVE,tuple(inverse.flat)[:8],Image.Resampling.BICUBIC)
    result.save(OUT / f'aerial_{year}_F1.jpg',quality=97)
    result.crop((0,350,1800,2150)).save(OUT / f'aerial_{year}_square.jpg',quality=97)
    result.resize((1200,1600)).save(OUT / f'{year}_registered_preview.jpg',quality=94)
    records.append({'year':year,'source':str(RAW/filename),'H_src2geo_rel':H.tolist()})
    print(year,photo.size,flush=True)

photo = Image.open(ROOT/'work/20261008_presentation_front/assets/hist/ortho_2025_F1.jpg')
photo.crop((0,350,1800,2150)).save(OUT/'aerial_2025_square.jpg',quality=97)
records.append({'year':2025,'source':str(RAW/'(B060)정사영상_2025_35901069.tif'),'processing':'existing north-up official orthophoto crop'})
(OUT/'aerial_provenance.json').write_text(json.dumps({'photos':records,'extent_5187':[219180,220380,360216.6667,361416.6667],'common_crop_pixels':[0,350,1800,2150],'historical_registration':'1954 surviving street intersections, approximate affine registration; no precision measurement claims'},ensure_ascii=False,indent=2),encoding='utf-8')
print('DONE',flush=True)
