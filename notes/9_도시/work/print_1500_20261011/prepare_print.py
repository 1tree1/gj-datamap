"""원본을 보존하고 1:1500 매스, 층간 홈, 연결 목을 생성한다."""
import sys,os,json,collections,time
HERE=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,os.path.join(HERE,'vendor'))
import numpy as np,trimesh,manifold3d as md
from shapely.geometry import Polygon
from shapely.ops import unary_union
SCALE=2/3
DEPTH=.25
HEIGHT=.4

def as_manifold(mesh):
    mesh.merge_vertices(digits_vertex=6);mesh.fix_normals(multibody=True)
    if not mesh.is_watertight:raise ValueError('열린 메쉬')
    out=md.Manifold(md.Mesh64(np.asarray(mesh.vertices,dtype=np.float64),np.asarray(mesh.faces,dtype=np.uint64)))
    if out.status()!=md.Error.NoError:raise ValueError(str(out.status()))
    return out

def as_trimesh(m):
    p=m.to_mesh64()
    return trimesh.Trimesh(np.asarray(p.vert_properties)[:,:3],np.asarray(p.tri_verts),process=False)

def cs_shape(cs):
    rings=[Polygon(p) for p in cs.to_polygons() if len(p)>=3]
    if not rings:return Polygon()
    result=Polygon()
    for p in sorted(rings,key=lambda p:-p.area):result=result.symmetric_difference(p)
    return result.buffer(0)

def thicken_surface(mesh,thickness):
    # 위쪽 표면과 아래로 이동한 복사본 사이를 경계면으로 닫는다.
    v=np.asarray(mesh.vertices);f=np.asarray(mesh.faces)
    normals=trimesh.triangles.normals(v[f])[0]
    f=f.copy();f[normals[:,2]<0]=f[normals[:,2]<0][:,::-1]
    mesh=trimesh.Trimesh(v,f,process=True)
    edge_count=np.bincount(mesh.edges_unique_inverse)
    boundary=mesh.edges_unique[edge_count==1]
    n=len(mesh.vertices);low=np.asarray(mesh.vertices).copy();low[:,2]-=thickness
    faces=[np.asarray(mesh.faces),np.asarray(mesh.faces)[:,::-1]+n]
    side=[]
    for a,b in boundary:side.extend([[a,b,b+n],[a,b+n,a+n]])
    faces.append(np.array(side))
    return trimesh.Trimesh(np.vstack([mesh.vertices,low]),np.vstack(faces),process=True)

def close_hip_roof(mesh):
    # 원본 모임지붕의 경계는 수평이다. 실제 경계에 바닥 캡을 추가한다.
    count=np.bincount(mesh.edges_unique_inverse);edges=mesh.edges_unique[count==1]
    zs=mesh.vertices[np.unique(edges),2]
    lines=[mesh.vertices[e,:2] for e in edges]
    from shapely.geometry import LineString
    from shapely.ops import polygonize
    poly=unary_union(list(polygonize([LineString(x) for x in lines])))
    v,f=trimesh.creation.triangulate_polygon(poly,engine='earcut')
    floor_z=float(np.min(zs))-.02
    vv=np.c_[v,np.full(len(v),floor_z)]
    cap=trimesh.Trimesh(vv,f[:,::-1],process=False)
    side_v=[];side_f=[]
    for a,b in edges:
        p,q=mesh.vertices[a],mesh.vertices[b]
        k=len(side_v);side_v.extend([p,q,[q[0],q[1],floor_z],[p[0],p[1],floor_z]])
        side_f.extend([[k,k+1,k+2],[k,k+2,k+3]])
    sides=trimesh.Trimesh(side_v,side_f,process=False)
    result=trimesh.util.concatenate([mesh,cap,sides]);result.merge_vertices(digits_vertex=5);result.fix_normals(multibody=True)
    return result

def main():
    t=time.time()
    src=json.load(open(os.path.join(HERE,'selected_mesh_inspection.json'),encoding='utf-8'))
    attrs={r['id']:r for r in src}
    raw=json.load(open(os.path.join(HERE,'rhino_meshes.json'),encoding='utf-8'))
    bodies=[];roofs=[];aux=[];edits=[]
    for rec in raw:
        a=attrs[rec['id']];mesh=trimesh.Trimesh(rec['vertices'],rec['faces'],process=True)
        mesh.apply_scale(SCALE);mesh.fix_normals(multibody=True)
        ly=a['layer'];nm=a['name']
        if '유리 볼트' in nm:
            mesh=thicken_surface(mesh,.6)
            aux.append(dict(a=a,m=as_manifold(mesh),kind='glass_roof'))
            edits.append(dict(id=a['id'],kind='glass_thickness',thickness_mm=.6))
            continue
        if '모임지붕' in nm:
            mesh=close_hip_roof(mesh)
            roofs.append(dict(a=a,m=as_manifold(mesh),kind='hip_roof'))
            edits.append(dict(id=a['id'],kind='hip_roof_cap'))
            continue
        if '태양광' in nm:
            # 0.013mm 원본은 출력할 수 없어 기존 평면 그대로 0.20mm로 연결한다.
            mm=as_manifold(mesh);z=mesh.bounds[0,2];floor_top=round(z/.01)*.01-.03
            cs=mm.slice(z+1e-5)
            mm=cs.extrude(.22).translate((0,0,floor_top-.02))
            roofs.append(dict(a=a,m=mm,kind='solar'))
            edits.append(dict(id=a['id'],kind='solar_thickness',thickness_mm=.22))
            continue
        mm=as_manifold(mesh)
        if '층' in a['us']:
            lo=round(float(mesh.bounds[0,2]),3);hi=round(float(mesh.bounds[1,2]),3)
            cs=mm.slice(float(mesh.bounds[:,2].mean()))
            contours=[np.round(p,3) for p in cs.to_polygons()]
            cs=md.CrossSection(contours,md.FillRule.NonZero).simplify(.001)
            original_project=mm.project()
            rebuilt=cs.extrude(hi-lo).translate((0,0,lo))
            difference_area=(cs-original_project).area()+(original_project-cs).area()
            edits.append(dict(id=a['id'],kind='prismatic_precision_normalization',coordinate_tolerance_mm=.001,footprint_difference_mm2=difference_area))
            mm=rebuilt
            mesh=as_trimesh(mm)
        bodies.append(dict(a=a,m=mm,projection=mm.project(),lo=float(mesh.bounds[0,2]),hi=float(mesh.bounds[1,2]),level='층' in a['us']))
    print('준비',len(bodies),'매스',len(roofs),'지붕',len(aux),'별도 부품',flush=True)
    # 매스의 층 속성으로 실제 상하 연결을 찾는다. 1.5m 들뜬 층은 inset 목으로 연결한다.
    connections=[]
    for i,a in enumerate(bodies):
        if not a['level']:continue
        for j,b in enumerate(bodies):
            if i==j or not b['level']:continue
            gap=b['lo']-a['hi']
            if -1e-4<=gap<=1.01:
                shared=a['projection']^b['projection']
                if shared.area()>.1:
                    connections.append((i,j,max(gap,0),shared))
    top={i for i,j,g,c in connections};bottom={j for i,j,g,c in connections}
    groove_log=[]
    for i,b in enumerate(bodies):
        mm=b['m'];lo=b['lo'];hi=b['hi']
        h_top=HEIGHT/2 if i in top else 0
        h_bottom=HEIGHT/2 if i in bottom else 0
        if h_top or h_bottom:
            cs=mm.slice((lo+hi)/2);inside=cs.offset(-DEPTH,md.JoinType.Miter,3).simplify(.001)
            if inside.area()<.05:raise ValueError('셋백 후 너무 얇아짐')
            slices=[cs.extrude(hi-lo-h_top-h_bottom).translate((0,0,lo+h_bottom))]
            if h_top:
                slices.append(inside.extrude(h_top+.002).translate((0,0,hi-h_top-.002)))
                groove_log.append(dict(id=b['a']['id'],edge='top',z_mm=hi,depth_mm=DEPTH,height_mm=h_top))
            if h_bottom:
                slices.append(inside.extrude(h_bottom+.002).translate((0,0,lo)))
                groove_log.append(dict(id=b['a']['id'],edge='bottom',z_mm=lo,depth_mm=DEPTH,height_mm=h_bottom))
            mm=md.Manifold.batch_boolean(slices,md.OpType.Add)
        b['m']=mm
    fillers=[]
    for i,j,gap,shared in connections:
        if gap>.001:
            neck=shared.offset(-DEPTH,md.JoinType.Miter,3)
            if neck.area()<.05:raise ValueError('층간 연결 목 없음')
            fillers.append(neck.extrude(gap+.02).translate((0,0,bodies[i]['hi']-.01)))
            edits.append(dict(kind='gap_neck',lower_id=bodies[i]['a']['id'],upper_id=bodies[j]['a']['id'],gap_mm=gap,depth_mm=DEPTH))
    # 프로그램마다 Boolean Union을 먼저 수행하고, 맞닿은 서로 다른 용도의 층도 이어 출력 조립체로 만든다.
    programs=collections.defaultdict(list)
    for b in bodies:
        a=b['a'];key=tuple(a['color'][:3]);programs[key].append(b['m'])
    program_unions={str(k):md.Manifold.batch_boolean(v,md.OpType.Add) for k,v in programs.items()}
    # 서로 다른 건물을 연결하는 브리지는 별도 부품으로 둔다. 프로그램과 건물 경계를 보존해 판에 배치한다.
    units=collections.defaultdict(list)
    unit_attrs=collections.defaultdict(list)
    id_unit={}
    by_name=collections.defaultdict(list)
    for b in bodies:
        if b['a']['us'].get('건축물'):by_name[b['a']['us']['건축물']].append(b)
    name_program={}
    for name,bs in by_name.items():
        eligible=[b for b in bs if '1층 가로상점' not in b['a']['layer']] or bs
        volume_by_color=collections.defaultdict(float)
        for b in eligible:volume_by_color[tuple(b['a']['color'][:3])]+=b['m'].volume()
        name_program[name]=max(volume_by_color,key=volume_by_color.get)
    for i,b in enumerate(bodies):
        a=b['a'];nm=a['us'].get('건축물')
        key=str(name_program[nm]) if nm else 'link_'+a['id']
        units[key].append(b['m']);unit_attrs[key].append(a);id_unit[i]=key
    parents={k:k for k in units}
    def find(k):
        while parents[k]!=k:k=parents[k]
        return k
    for i,j,gap,shared in connections:
        if gap>.001:parents[find(id_unit[i])]=find(id_unit[j])
    merged=collections.defaultdict(list);merged_attrs=collections.defaultdict(list)
    for key,items in units.items():merged[find(key)].extend(items);merged_attrs[find(key)].extend(unit_attrs[key])
    units=merged;unit_attrs=merged_attrs
    for neck,(i,j,gap,shared) in zip(fillers,[c for c in connections if c[2]>.001]):
        units[find(id_unit[i])].append(neck)
    for b in roofs:
        nm='구 경주역사' if b['kind']=='hip_roof' else b['a']['name'].split(' 옥상')[0]
        key=str(name_program[nm]);units[key].append(b['m']);unit_attrs[key].append(b['a'])
    components=[]
    for key,items in units.items():
        united=md.Manifold.batch_boolean(items,md.OpType.Add).set_tolerance(.001).simplify(.001)
        if united.status()!=md.Error.NoError:raise ValueError(str(united.status()))
        for component in united.decompose():components.append((component,unit_attrs[key],key))
    print('Union',len(components),'연결 부품','홈',len(groove_log),'연결목',len(fillers),flush=True)
    pieces=[]
    os.makedirs(os.path.join(HERE,'parts'),exist_ok=True)
    for component,unit_ref,key in components:
        if abs(component.volume())<.01:
            edits.append(dict(kind='numerical_sliver_removed',volume_mm3=component.volume(),bounds=component.bounding_box()))
            continue
        if component.volume()<0:raise ValueError('내부 공동 분리 검사 필요 '+str(component.volume()))
        bbox=np.array(component.bounding_box()).reshape(2,3)
        refs=[]
        for b in bodies+roofs:
            if b['a'] in unit_ref and (component^b['m']).volume()>.001:refs.append(b['a'])
        names=list(dict.fromkeys(a['us'].get('건축물') or a['name'] for a in refs if a['us'].get('건축물') or a['name']))
        cats=list(dict.fromkeys(a['layer'].split('::')[-1] for a in refs))
        dom=max(refs,key=lambda a:((component^next(b['m'] for b in bodies+roofs if b['a']['id']==a['id'])).volume()),default=None)
        mm=component.translate(tuple(-bbox[0]))
        pieces.append(dict(m=mm,names=names or ['연결 브리지·캐노피'],programs=cats,source_ids=[a['id'] for a in refs],source_origin_mm=bbox[0].tolist(),color=dom['color'][:3] if dom else [160,160,160],kind='mass',grounded=bool(bbox[0,2]<.01)))
    for b in aux:
        bb=np.array(b['m'].bounding_box()).reshape(2,3)
        pieces.append(dict(m=b['m'].translate(tuple(-bb[0])),names=[b['a']['name']],programs=[b['a']['layer'].split('::')[-1]],source_ids=[b['a']['id']],source_origin_mm=bb[0].tolist(),color=b['a']['color'][:3],kind=b['kind'],grounded=False))
    pieces.sort(key=lambda b:(b['kind'],-b['m'].project().area(),','.join(b['names'])))
    manifest=[]
    for k,b in enumerate(pieces,1):
        part_id=f'part_{k:02d}'
        b['m']=md.Manifold(b['m'].to_mesh()).set_tolerance(.001).simplify(.001)
        m=as_trimesh(b['m']);path=os.path.join(HERE,'parts',part_id+'.stl')
        if not (m.is_watertight and m.is_winding_consistent and m.volume>0):
            print('FAILED',part_id,b['names'],'watertight',m.is_watertight,'winding',m.is_winding_consistent,'vol',m.volume,'mstatus',b['m'].status(),flush=True)
        assert m.is_watertight and m.is_winding_consistent and m.volume>0
        m.export(path)
        footprint=cs_shape(b['m'].project())
        row={key:value for key,value in b.items() if key!='m'}
        row.update(id=part_id,stl=path,extent_mm=m.extents.tolist(),volume_mm3=float(m.volume),footprint_area_mm2=footprint.area,footprint_wkt=footprint.wkt,triangles=len(m.faces),watertight=bool(m.is_watertight))
        manifest.append(row)
        print(part_id,'size',np.round(m.extents,2).tolist(),'area',round(footprint.area),','.join(b['names']),flush=True)
    output=dict(scale_factor=SCALE,groove_depth_mm=DEPTH,groove_height_mm=HEIGHT,part_count=len(manifest),total_projected_area_mm2=sum(x['footprint_area_mm2'] for x in manifest),parts=manifest,edits=edits,grooves=groove_log,elapsed_seconds=time.time()-t)
    json.dump(output,open(os.path.join(HERE,'prepared_manifest.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=2,default=lambda x: bool(x) if isinstance(x,np.bool_) else x.item())
    print('총 투영 면적',output['total_projected_area_mm2'],'시간',round(time.time()-t),flush=True)

if __name__=='__main__':main()
