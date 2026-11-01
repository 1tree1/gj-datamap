import os,sys,json
HERE=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,os.path.join(HERE,'vendor'))
import numpy as np,trimesh
d=json.load(open(os.path.join(HERE,'prepared_manifest.json'),encoding='utf-8'))
log=[]
for row in d['parts']:
    m=trimesh.load_mesh(row['stl'],process=True)
    before=dict(watertight=bool(m.is_watertight),faces=len(m.faces),volume=float(m.volume))
    m.merge_vertices(digits_vertex=5)
    m.update_faces(m.nondegenerate_faces(height=1e-5))
    m.update_faces(m.unique_faces());m.remove_unreferenced_vertices();m.fix_normals(multibody=True)
    if not m.is_watertight:m.fill_holes();m.fix_normals(multibody=True)
    if not m.is_watertight:
        edges=m.edges_unique[np.bincount(m.edges_unique_inverse)!=2]
        print('FAILED',row['id'],'edges',len(edges),'length',np.linalg.norm(m.vertices[edges[:,0]]-m.vertices[edges[:,1]],axis=1),flush=True)
        raise ValueError(row['id'])
    delta=abs(m.volume-before['volume'])
    assert delta<.005,(row['id'],delta)
    if not before['watertight'] or before['faces']!=len(m.faces):
        log.append(dict(id=row['id'],before=before,after_faces=len(m.faces),volume_difference_mm3=delta))
    m.export(row['stl'])
    reread=trimesh.load_mesh(row['stl'],process=True)
    assert reread.is_watertight and reread.is_winding_consistent
    row['triangles']=len(m.faces);row['volume_mm3']=float(m.volume)
json.dump(d,open(os.path.join(HERE,'prepared_manifest.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=2)
json.dump(log,open(os.path.join(HERE,'stl_precision_repairs.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=2)
print('수치 정리',json.dumps(log,ensure_ascii=False))
