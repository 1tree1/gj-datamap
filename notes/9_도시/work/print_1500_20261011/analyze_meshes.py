import sys, os,json,collections
HERE=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,os.path.join(HERE,'vendor'))
import numpy as np, trimesh
d=json.load(open(os.path.join(HERE,'source_inspection.json'),encoding='utf-8'))
recs={x['id']:x for x in d['records']}
ms=json.load(open(os.path.join(HERE,'rhino_meshes.json'),encoding='utf-8'))
rows=[]
for x in ms:
 r=recs[x['id']];m=trimesh.Trimesh(x['vertices'],x['faces'],process=True);m.fix_normals(multibody=True)
 bounds=np.round(m.bounds,3).tolist()
 row=dict(r,mesh_closed=bool(m.is_watertight),mesh_volume=float(m.volume),faces=len(m.faces),local_bb=bounds)
 rows.append(row)
 print(r['type'],r['layer'].split('::')[-1],r['name'],'z',bounds[0][2],bounds[1][2],'xy',np.round(m.extents[:2],2).tolist(),'rgb',r['color'][:3],'closed',m.is_watertight,'vol',round(m.volume,2))
json.dump(rows,open(os.path.join(HERE,'selected_mesh_inspection.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=2)
print('TOTAL',len(rows),'closed',sum(r['mesh_closed'] for r in rows))
