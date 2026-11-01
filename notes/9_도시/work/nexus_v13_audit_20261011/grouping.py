import Rhino,json,re
from pathlib import Path
from collections import defaultdict
from System.Collections.Generic import List
doc=__rhino_doc__;sel=list(doc.Objects.GetSelectedObjects(False,False))
root=Path(r'C:\Users\OFFICE\Desktop\9_도시\work\nexus_v13_audit_20261011')
data=json.loads((root/'rhino_measurements.json').read_text(encoding='utf-8'))
def category(name):
 if name in ['공공청사 본관','공공청사 민원·시민홀동']:return '청사'
 if name in ['공공기관 업무동','청년창업지원센터']:return '기관·청년창업'
 if name=='공공청사·기관 직원 주차장동':return '북측 주차'
 if re.match(r'^주거동 \d+$',name):return '주거'
 if name=='생활체육관·편의시설':return '스포츠·생활편의'
 if name in ['복합문화센터','생활가로 상가']:return '중앙 북측 복합문화·상가'
 if name=='건강·돌봄센터':return '건강·돌봄'
 if name in ['실내 공예마켓·운영동','전통문화 공방·체험·전시동']:return '서측 공예전시·마켓·공방'
 if name=='작가 교류·행사동':return '작가 교류'
 if name.startswith('레지던시 거주동') or name.startswith('레지던시 제작동'):return '레지던시'
 if name=='실내 체험관':return '실내 체험'
 if name in ['근대역사관','지역문화원 본동','소상공인 상생동(남)','소상공인 상생동(북)']:return '남측 역사문화·상생'
 if name=='관광지원센터':return '관광지원'
 if name=='공유주차장':return '남측 공유주차'
 if name=='모빌리티 허브':return '모빌리티 허브'
 if name in ['레지던시 가로상가','관문 가로상가']:return '별도 가로상가'
 return name
caps=defaultdict(list);records={r['id']:r for r in data['records']}
volume_check=[]
for o in sel:
 if str(o.Id) not in records:continue
 r=records[str(o.Id)];g=o.Geometry
 b=g.ToBrep() if isinstance(g,Rhino.Geometry.Extrusion) else g.DuplicateBrep()
 bb=b.GetBoundingBox(True);b.Transform(Rhino.Geometry.Transform.Translation(-1166700,-1761100,0))
 v=Rhino.Geometry.VolumeMassProperties.Compute(b)
 area_from_volume=abs(v.Volume)/(bb.Max.Z-bb.Min.Z) if v else None
 volume_check.append({'id':str(o.Id),'name':r['building'],'bottom_area':r['bottom_area'],'volume_over_height':area_from_volume,'error':abs(area_from_volume-r['bottom_area']) if area_from_volume is not None else None})
 for f in b.Faces:
  fb=f.GetBoundingBox(True)
  if abs(fb.Max.Z-fb.Min.Z)<1e-5 and abs(fb.Min.Z-bb.Min.Z)<1e-5:
   face=f.DuplicateFace(False);face.Transform(Rhino.Geometry.Transform.Translation(0,0,-bb.Min.Z))
   caps[(category(r['building']),round(bb.Min.Z,5),round(bb.Max.Z,5))].append(face)
group_sums=defaultdict(float);group_floors=[]
for (name,z1,z2),parts in caps.items():
 merged=Rhino.Geometry.Brep.CreatePlanarUnion(List[Rhino.Geometry.Brep](parts),Rhino.Geometry.Plane.WorldXY,0.0001)
 area=sum(Rhino.Geometry.AreaMassProperties.Compute(x).Area for x in merged)
 group_sums[name]+=area;group_floors.append({'group':name,'zmin':z1,'zmax':z2,'area':area})
site_rows=[]
for o in sel:
 l=doc.Layers[o.Attributes.LayerIndex].FullPath;g=o.Geometry
 if isinstance(g,Rhino.Geometry.Curve) and g.IsClosed and ('00_' in l or '01_' in l or '02_' in l or '03_' in l or '08_' in l):
  crv=g.DuplicateCurve();crv.Transform(Rhino.Geometry.Transform.Translation(-1166700,-1761100,0))
  ap=Rhino.Geometry.AreaMassProperties.Compute(crv)
  if ap:site_rows.append({'id':str(o.Id),'name':o.Attributes.Name,'layer':l,'area':ap.Area})
result={'group_gfa':dict(group_sums),'group_floors':group_floors,'group_sum_before_cross_group_overlap':sum(group_sums.values()),'global_union_gfa':data['global_union_gfa'],'remaining_cross_group_overlap':sum(group_sums.values())-data['global_union_gfa'],'volume_checks':volume_check,'max_volume_check_error':max(v['error'] for v in volume_check if v['error'] is not None),'site_rows':site_rows}
(root/'comparison_groups.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'group_gfa':dict(group_sums),'group_sum':sum(group_sums.values()),'global_union_gfa':data['global_union_gfa'],'remaining_cross_group_overlap':result['remaining_cross_group_overlap'],'max_volume_check_error':result['max_volume_check_error'],'volume_nonprismatic':[v for v in volume_check if v['error'] is not None and v['error']>0.01],'site_rows':site_rows},ensure_ascii=False))
