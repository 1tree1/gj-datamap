from pathlib import Path
import json,sys
from shapely.geometry import Polygon,mapping
from shapely.ops import unary_union
sys.stdout.reconfigure(encoding='utf8')
B=Path(__file__).parent;R=Path(r'C:/Users/OFFICE/Desktop/9_도시/work/nexus_v13_audit_20261011')
fac=json.loads((R/'facility_comparison.json').read_text('utf8'))
plan=json.loads((R/'placement-model-plan.json').read_text('utf8'))
f=[x for x in plan['features'] if x['building'] is None]
def shape(x): return unary_union([Polygon(a).buffer(0) for a in x['rings'] if len(a)>3])
b=unary_union([shape(x) for x in f if '00_구역' in x['layer']])
plots=unary_union([shape(x) for x in f if '01_획지' in x['layer']]).intersection(b)
parks0=unary_union([shape(x) for x in f if '02_공원' in x['layer']]).intersection(b)
parks=parks0.difference(plots)
walk=unary_union([shape(x) for x in f if '03_보행' in x['layer']]).intersection(b).difference(plots).difference(parks)
rest=b.difference(unary_union([plots,parks,walk]))
land=[{'name':n,'area':g.area,'pct':g.area/b.area*100,'geometry':mapping(g)} for n,g in [('건축 획지',plots),('보행축·광장',walk),('공원·녹지',parks),('차량가로·잔여 공간',rest)]]
assert abs(sum(x['area'] for x in land)-b.area)<.001
# Unique, non-overlapping groups in the prior conversation's selected-model audit.
groups=[('북측 공공',[0,1,2]),('정주·스포츠·편의',[3,4]),('생활·문화',[5,6,7]),('창작·체험',[8,9,10,11]),('역사문화·관광',[12,13,14]),('모델 별도 항목',[15,16])]
groups=[{'name':n,'target':sum(fac[i]['target'] or 0 for i in ix),'model':sum(fac[i]['model'] or 0 for i in ix),'indices':ix} for n,ix in groups]
assert sum(x['target'] for x in groups)==105560
assert abs(sum(x['model'] for x in groups)-176661.18077577112)<.001
# Explicit program footprint subtotal. Sports footprint is not specified in v13.
footprints=[5500,2200/3,5640,3840,None,1200,600,200,1750,300,1250,3000,1750,1000,1000,250,400,900,3200]
known=sum(x or 0 for x in footprints)
units=[{'type':22,'units':64,'people_per_unit':1.0},{'type':33,'units':64,'people_per_unit':1.3},{'type':44,'units':96,'people_per_unit':2.3},{'type':58,'units':32,'people_per_unit':3.0}]
assert sum(x['units'] for x in units)==256
assert sum(x['units']*x['people_per_unit'] for x in units)==464
assert sum(x['units']*x['type'] for x in units)==9600
parking=(1100*.9*.55/1.05+250*.6/1.5+30)*1.1
program=[26500,2200,22560,19200,5300,2000,1200,200,2700,300,2500,3000,3500,1000,1000,500,800,1500,9600]
assert sum(program)==105560
D={'thread_id':'01a129e7-d0c2-7d82-af3a-e333678ba0ec','program_source':'NEXUS 1918 v13, 2026-10-11','source_model_date':'2026-10-11 selected-model audit (157 objects)','land_source':'placement-model-plan.json saved-model polygons, 2026-10-11','facilities':fac,'groups':groups,'site_area':b.area,'land':land,'boundary':mapping(b),'plots':[{'name':x['name'],'area':shape(x).area,'geometry':mapping(shape(x))} for x in f if '01_획지' in x['layer']],'park_plot_overlap':parks0.intersection(plots).area,'known_program_footprint':known,'footprints':footprints,'program_areas':program,'units':units,'parking_calculated':parking,'visitors':[{'scenario':'적은 운영','rounds':2,'fill':.6,'visits':190*2*.6},{'scenario':'기준 운영','rounds':3,'fill':.7,'visits':190*3*.7},{'scenario':'확대 운영','rounds':4,'fill':.8,'visits':190*4*.8}],'area_intensity_plan':105560/plots.area*100,'area_intensity_model':176661.18077577112/plots.area*100,'site_intensity_plan':105560/b.area*100,'model_nonparking':176661.18077577112-17409.414338414615-16000,'declared_units':'Rhino file mm; calculations interpreted 1 coordinate unit=1m, prior audit basis 48x10 housing'}
(B/'revision11_evidence.json').write_text(json.dumps(D,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({k:D[k] for k in ['site_area','park_plot_overlap','known_program_footprint','parking_calculated','area_intensity_plan','area_intensity_model','model_nonparking']},ensure_ascii=False))
print('LAND',[(x['name'],round(x['area'],1),round(x['pct'],2)) for x in land])
print('GROUPS',[(x['name'],x['target'],round(x['model'],1)) for x in groups])
