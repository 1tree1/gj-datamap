from pathlib import Path
import json
from PIL import Image

ROOT=Path('C:/Users/OFFICE/Desktop/9_도시')
B=ROOT/'work/20261011_visual_front/build'
A=B/'assets'
OLD=ROOT/'work/20261010_nexus_front/build'
def crop(src, box, name):
    Image.open(src).crop(box).save(A/name)

crop(OLD/'final_renders/08.png',(54,253,744,886),'site_diagram.png')
crop(OLD/'final_renders/09.png',(54,254,712,912),'city_relations.png')
crop(OLD/'final_renders/13.png',(54,254,548,864),'anchors.png')
for i in range(4):
    crop(OLD/'final_renders/12.png',(54+i*315,315,344+i*315,697),f'reg_{i}.png')
crop(ROOT/'work/maps/map10_모델범위_분석신뢰반경_철도횡단.png',(590,490,1160,1190),'crossing_detail.png')
crop(ROOT/'work/maps/map12_경주조직_반복특성.png',(910,185,1810,1038),'street_orientation.png')
crop(ROOT/'work/maps/map18_원도심_한눈에.png',(195,254,1360,1418),'core_fabric.png')

def read(f):return json.loads((B/'web_data'/f).read_text(encoding='utf-8'))
pop=read('hadm_pop.geojson')
y=read('youth.json'); w=read('web_extras.json'); h=read('hwango_report.json')
known=[]
parcels=json.loads((ROOT/'gj-datamap/public/data/parcels.geojson').read_text(encoding='utf-8'))
for f in parcels['features']:
    age=f['properties'].get('bldg_age')
    if isinstance(age,(int,float)):known.append(age)
age_counts=[sum(a<10 for a in known),sum(10<=a<20 for a in known),sum(20<=a<30 for a in known),sum(30<=a<40 for a in known),sum(a>=40 for a in known)]
e={'population':[f['properties'] for f in pop['features']],'youth':y,'footfall':w['footfall'],'biz_area':w['biz_area'],'biz2024':{'open':h['biz2024']['open']['by_group'],'close':h['biz2024']['close']['by_group']},'age_counts':age_counts,'age_known':len(known)}
(B/'evidence.json').write_text(json.dumps(e,ensure_ascii=False,indent=2),encoding='utf-8')
print('Prepared crops and evidence',len(known),age_counts)
