import Rhino, json, math, re
from pathlib import Path
from collections import defaultdict, Counter
from System.Collections.Generic import List
doc=__rhino_doc__
sel=list(doc.Objects.GetSelectedObjects(False,False))
outdir=Path(r'C:\Users\OFFICE\Desktop\9_도시\work\nexus_v13_audit_20261011')
outdir.mkdir(parents=True,exist_ok=True)
origin=Rhino.Geometry.Point3d(1166700,1761100,0)
records=[]; caps=defaultdict(list); failures=[]
for o in sel:
 layer=doc.Layers[o.Attributes.LayerIndex].FullPath
 if "::06_" not in layer: continue
 g=o.Geometry
 if isinstance(g,Rhino.Geometry.Extrusion): b=g.ToBrep()
 elif isinstance(g,Rhino.Geometry.Brep): b=g.DuplicateBrep()
 else: continue
 bb=g.GetBoundingBox(True)
 us=o.Attributes.GetUserStrings()
 meta={str(k):str(us[k]) for k in us.AllKeys} if us else {}
 name=meta.get('건축물') or re.sub(r' \d+F$','',o.Attributes.Name or '(unnamed)')
 bottom=[]
 for f in b.Faces:
  fb=f.GetBoundingBox(True)
  if abs(fb.Max.Z-fb.Min.Z)<1e-5 and abs(fb.Min.Z-bb.Min.Z)<1e-5:
   c=f.DuplicateFace(False)
   c.Transform(Rhino.Geometry.Transform.Translation(-origin.X,-origin.Y,-bb.Min.Z))
   bottom.append(c)
 raw=sum(Rhino.Geometry.AreaMassProperties.Compute(c).Area for c in bottom)
 if not bottom:failures.append({'id':str(o.Id),'name':name,'reason':'no horizontal bottom'})
 key=(name,round(bb.Min.Z,5),round(bb.Max.Z,5))
 caps[key].extend(bottom)
 record={'id':str(o.Id),'object_name':o.Attributes.Name,'building':name,'layer':layer,'category':meta.get('용도분류',''),'zmin':bb.Min.Z,'zmax':bb.Max.Z,'dimensions':[bb.Max.X-bb.Min.X,bb.Max.Y-bb.Min.Y,bb.Max.Z-bb.Min.Z],'bottom_area':raw,'is_solid':bool(b.IsSolid),'metadata':meta}
 records.append(record)
floor_rows=[]; global_caps=defaultdict(list)
for key,items in caps.items():
 arr=List[Rhino.Geometry.Brep](items)
 merged=Rhino.Geometry.Brep.CreatePlanarUnion(arr,Rhino.Geometry.Plane.WorldXY,0.0001)
 if merged is None or len(merged)==0:
  merged=items; failures.append({'name':key[0],'z':key[1],'reason':'union failed; raw sum used'})
 area=sum(Rhino.Geometry.AreaMassProperties.Compute(c).Area for c in merged)
 floor_rows.append({'building':key[0],'zmin':key[1],'zmax':key[2],'raw_area':sum(Rhino.Geometry.AreaMassProperties.Compute(c).Area for c in items),'union_area':area,'parts':len(items),'union_parts':len(merged)})
 global_caps[(key[1],key[2])].extend(merged)
global_rows=[]
for key,items in global_caps.items():
 merged=Rhino.Geometry.Brep.CreatePlanarUnion(List[Rhino.Geometry.Brep](items),Rhino.Geometry.Plane.WorldXY,0.0001)
 if merged is None or len(merged)==0: merged=items;failures.append({'zrange':list(key),'reason':'global union failed'})
 global_rows.append({'zmin':key[0],'zmax':key[1],'area':sum(Rhino.Geometry.AreaMassProperties.Compute(c).Area for c in merged),'raw_area':sum(Rhino.Geometry.AreaMassProperties.Compute(c).Area for c in items)})
buildings=[]
for name in sorted(set(r['building'] for r in records)):
 rows=[r for r in floor_rows if r['building']==name]; rs=[r for r in records if r['building']==name]
 buildings.append({'building':name,'category':rs[0]['category'],'objects':len(rs),'actual_floor_count':len(rows),'z_intervals':[[r['zmin'],r['zmax']] for r in sorted(rows,key=lambda a:a['zmin'])],'floor_areas':[round(r['union_area'],4) for r in sorted(rows,key=lambda a:a['zmin'])],'gfa':sum(r['union_area'] for r in rows),'raw_gfa':sum(r['raw_area'] for r in rows),'metadata_gfa':rs[0]['metadata'].get('연면적㎡'),'metadata_floors':rs[0]['metadata'].get('층수')})
data={'document':doc.Name,'path':doc.Path,'declared_unit':str(doc.ModelUnitSystem),'physical_interpretation':'one coordinate unit interpreted as one meter based on 48x10 housing and 25x100 city hall dimensions, metadata and source program','selection_count':len(sel),'building_object_count':len(records),'records':records,'floors':floor_rows,'buildings':buildings,'global_floors':global_rows,'total_building_union_gfa':sum(r['gfa'] for r in buildings),'global_union_gfa':sum(r['area'] for r in global_rows),'failures':failures}
(outdir/'rhino_measurements.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:data[k] for k in ['document','declared_unit','selection_count','building_object_count','buildings','total_building_union_gfa','global_union_gfa','failures']},ensure_ascii=False))
