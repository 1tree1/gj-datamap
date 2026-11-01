"""1:1500 형상을 회전·이동만으로 160mm 판에 배치하고 검증한다."""
import os,sys,json,time,math,random,hashlib,csv,zipfile
HERE=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,os.path.join(HERE,'vendor'))
import numpy as np,trimesh,shapely,rhino3dm as r3
from shapely import wkt,affinity
from scipy.signal import fftconvolve
SIZE=160.;MARGIN=3.;GAP=2.;STEP=.5;N=int((SIZE-2*MARGIN)/STEP)

def build_options(row):
    poly=wkt.loads(row['footprint_wkt'])
    rect=poly.minimum_rotated_rectangle
    xy=np.array(rect.exterior.coords);diff=xy[1]-xy[0]
    base=-math.degrees(math.atan2(diff[1],diff[0]))
    angles=sorted(set(round(x%360,5) for x in [0,90,180,270,base,base+90,base+180,base+270]))
    opts=[]
    for angle in angles:
        p=affinity.rotate(poly,angle,origin=(0,0));bb=p.bounds
        p=affinity.translate(p,-bb[0],-bb[1]);buf=p.buffer(GAP/2+.12,join_style=2)
        b=buf.bounds;buf=affinity.translate(buf,-b[0],-b[1]);p=affinity.translate(p,-b[0],-b[1])
        b=buf.bounds;W=int(math.ceil(b[2]/STEP));H=int(math.ceil(b[3]/STEP))
        if W>N or H>N:continue
        xx,yy=np.meshgrid((np.arange(W)+.5)*STEP,(np.arange(H)+.5)*STEP)
        mask=shapely.contains_xy(buf,xx,yy).astype(float)
        opts.append(dict(angle=angle,offset=[-bb[0]-b[0],-bb[1]-b[1]],mask=mask,poly=p,W=W,H=H,
                         translation=[-bb[0]-float(p.bounds[0])+float(p.bounds[0]),-bb[1]]))
        # p の最終変換を明示して保存する。
        original_rot=affinity.rotate(poly,angle,origin=(0,0))
        opts[-1]['offset']=[p.bounds[0]-original_rot.bounds[0],p.bounds[1]-original_rot.bounds[1]]
    return opts

def fit(occ,options,rng):
    fits=[]
    for op in options:
        hits=fftconvolve(occ,op['mask'][::-1,::-1],mode='valid')
        y,x=np.nonzero(hits<.1)
        if not len(y):continue
        # 下端から詰め、同じ高さでは左に寄せる。
        score=y*(N+1)+x
        pos=np.argmin(score)
        fits.append((float(y[pos])+op['H']*.006+rng.random()*.003,int(x[pos]),int(y[pos]),op))
    return min(fits,key=lambda x:x[0]) if fits else None

def pack_order(order,options,rng):
    occs=[np.zeros((N,N))];placed=[]
    for row in order:
        chosen=None
        for board,occ in enumerate(occs):
            hit=fit(occ,options[row['id']],rng)
            if hit:chosen=(board,hit);break
        if chosen is None:
            occs.append(np.zeros((N,N)));hit=fit(occs[-1],options[row['id']],rng)
            if hit is None:raise ValueError('한 판보다 큰 부품 '+row['id'])
            chosen=(len(occs)-1,hit)
        board,(_,x,y,op)=chosen
        occs[board][y:y+op['H'],x:x+op['W']]+=op['mask']
        tx=op['offset'][0]+MARGIN+x*STEP;ty=op['offset'][1]+MARGIN+y*STEP
        poly=affinity.translate(op['poly'],MARGIN+x*STEP,MARGIN+y*STEP)
        placed.append(dict(id=row['id'],plate=board+1,rotation_deg=op['angle'],translation_mm=[tx,ty,0.],poly=poly))
    first=[p for p in placed if p['plate']==1]
    score=(len(occs),-len(first),-sum(p['poly'].area for p in first))
    return score,placed

def render_layout(placements,rows,output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon as Patch
    plt.rcParams['font.family']='Malgun Gothic';plt.rcParams['axes.unicode_minus']=False
    count=max(p['plate'] for p in placements)
    fig,axes=plt.subplots(1,count,figsize=(8*count,8),squeeze=False)
    for k in range(count):
        ax=axes[0,k];ax.set_xlim(0,SIZE);ax.set_ylim(0,SIZE);ax.set_aspect('equal');ax.set_facecolor('#f3f4f6')
        ax.plot([MARGIN,SIZE-MARGIN,SIZE-MARGIN,MARGIN,MARGIN],[MARGIN,MARGIN,SIZE-MARGIN,SIZE-MARGIN,MARGIN],color='#aaa',ls='--',lw=.5)
        local=[p for p in placements if p['plate']==k+1]
        for p in local:
            row=rows[p['id']];g=p['poly'];parts=[g] if g.geom_type=='Polygon' else list(g.geoms)
            color=np.array(row['color'])/255
            for poly in parts:
                ax.add_patch(Patch(np.array(poly.exterior.coords),facecolor=color,edgecolor='#29323a',linewidth=.6))
                for ring in poly.interiors:ax.add_patch(Patch(np.array(ring.coords),facecolor='#f3f4f6',edgecolor='#29323a',linewidth=.6))
            pt=g.representative_point();ax.text(pt.x,pt.y,p['id'][5:],ha='center',va='center',fontsize=7,color='#111')
        ax.set_title(f"출력판 {k+1:02d} | {len(local)}개 부품 | 160 × 160 mm",fontsize=13,pad=14)
        ax.set_xlabel('mm');ax.set_ylabel('mm');ax.grid(alpha=.12)
    fig.suptitle('구 경주역 매스 · 실제 1:1500 · 층간 홈 0.4mm / 셋백 0.25mm',fontsize=16,y=.985)
    fig.tight_layout(rect=(0,0,1,.955));fig.savefig(output,dpi=160);plt.close(fig)

def main():
    t=time.time();d=json.load(open(os.path.join(HERE,'prepared_manifest.json'),encoding='utf-8'))
    rows={r['id']:r for r in d['parts']};opts={r['id']:build_options(r) for r in d['parts']}
    best=None;rng=random.Random(1500)
    ordered=sorted(d['parts'],key=lambda r:r['footprint_area_mm2'])
    for trial in range(100):
        if trial==0:order=ordered
        elif trial==1:order=ordered[::-1]
        elif trial<30:
            order=sorted(d['parts'],key=lambda r:r['footprint_area_mm2']*rng.uniform(.55,1.6))
        elif trial<70:
            small=ordered[:24];large=ordered[24:];rng.shuffle(small);rng.shuffle(large);order=small+large
        else:
            reserve=3+(trial-70)%8
            primary=ordered[:-reserve];tail=ordered[-reserve:]
            primary=sorted(primary,key=lambda r:-r['footprint_area_mm2']*rng.uniform(.7,1.3))
            order=primary+tail[::-1]
        score,placed=pack_order(order,opts,rng)
        if best is None or score<best[0]:
            best=(score,placed);print('배치 후보',trial,'판',score[0],'첫 판',-score[1],'면적',round(-score[2]),flush=True)
    score,placed=best
    # 래스터 탐색 결과를 정확한 다각형으로 다시 검증한다.
    min_distance=999
    for i,p in enumerate(placed):
        bb=p['poly'].bounds
        assert min(bb[0],bb[1])>=MARGIN-1e-5 and max(bb[2],bb[3])<=SIZE-MARGIN+1e-5
        for q in placed[i+1:]:
            if p['plate']!=q['plate']:continue
            distance=p['poly'].distance(q['poly']);min_distance=min(min_distance,distance)
            assert distance>=GAP-1e-5,(p['id'],q['id'],distance)
    meshes=[];rf=r3.File3dm();rf.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters
    rf.Settings.ModelAbsoluteTolerance=.001
    sitef=r3.File3dm();sitef.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters
    sitef.Settings.ModelAbsoluteTolerance=.001
    layers={};site_layers={};by_plate=collections_default()
    for p in placed:
        row=rows[p['id']];m=trimesh.load_mesh(row['stl'],process=True)
        # 32bit STL 再読込の数値誤差だけを統合する。
        m.merge_vertices(digits_vertex=5);m.fix_normals(multibody=True)
        if not m.is_watertight:raise ValueError('STL再読込で開いたメッシュ '+p['id'])
        mat=trimesh.transformations.rotation_matrix(math.radians(p['rotation_deg']),[0,0,1])
        m.apply_transform(mat);m.apply_translation(p['translation_mm']);by_plate[p['plate']].append(m)
        display_mesh=m.copy();display_mesh.apply_translation([(p['plate']-1)*180,0,0]);add_rhino(rf,display_mesh,row,p,layers)
        sm=trimesh.load_mesh(row['stl'],process=True);sm.apply_translation(row['source_origin_mm']);add_rhino(sitef,sm,row,dict(plate=0,id=p['id']),site_layers)
    plate_report=[]
    for plate,ms in sorted(by_plate.items()):
        mesh=trimesh.util.concatenate(ms);path=os.path.join(HERE,f'plate_{plate:02d}_160mm_1_1500.stl');mesh.export(path)
        reload=trimesh.load_mesh(path,process=True);reload.merge_vertices(digits_vertex=4)
        assert reload.is_watertight and reload.is_winding_consistent and np.min(reload.bounds)>=-1e-4
        assert np.max(reload.bounds[1,:2])<=160+1e-4
        local=[p for p in placed if p['plate']==plate]
        plate_report.append(dict(plate=plate,stl=path,parts=len(ms),bounds_mm=reload.bounds.tolist(),triangles=len(reload.faces),watertight=bool(reload.is_watertight),winding_consistent=bool(reload.is_winding_consistent),volume_mm3=float(reload.volume),part_ids=[p['id'] for p in local]))
    # 判の枠は STL には入れず、3dm の参照レイヤーに置く。
    layer=r3.Layer();layer.Name='160mm_plate_reference';layer.Color=(110,110,110,255);li=rf.Layers.Add(layer)
    att=r3.ObjectAttributes();att.LayerIndex=li
    for plate in by_plate:
        x=(plate-1)*180
        rf.Objects.AddPolyline([r3.Point3d(x,0,0),r3.Point3d(x+160,0,0),r3.Point3d(x+160,160,0),r3.Point3d(x,160,0),r3.Point3d(x,0,0)],att)
    model=os.path.join(HERE,'print_layout_1_1500.3dm');rf.Write(model,8)
    site_path=os.path.join(HERE,'site_assembly_1_1500.3dm');sitef.Write(site_path,8)
    render_layout(placed,rows,os.path.join(HERE,'plate_layout.png'))
    expanded_area=sum(wkt.loads(r['footprint_wkt']).buffer(GAP/2,join_style=2).area for r in d['parts'])
    coverage=set(k for r in d['parts'] for k in r['source_ids']);raw=json.load(open(os.path.join(HERE,'rhino_meshes.json'),encoding='utf-8'))
    missing=[r['id'] for r in raw if r['id'] not in coverage]
    assert not missing,missing
    report=dict(scale='1:1500',source_units_label='mm',actual_source_unit='m',coordinate_factor=2/3,plate_size_mm=[160,160],edge_margin_mm=MARGIN,minimum_part_gap_mm=min_distance,requested_part_gap_mm=GAP,total_parts=len(placed),total_projected_area_mm2=d['total_projected_area_mm2'],area_with_2mm_spacing_mm2=expanded_area,usable_plate_area_mm2=(SIZE-2*MARGIN)**2,plates=plate_report,placements=[{k:v for k,v in p.items() if k!='poly'} for p in placed],source_geometry_coverage_count=len(coverage),missing_source_ids=missing,groove_height_mm=.4,groove_depth_mm=.25,layout_3dm=model,assembly_3dm=site_path,elapsed_seconds=time.time()-t)
    json.dump(report,open(os.path.join(HERE,'print_validation.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=2)
    with open(os.path.join(HERE,'parts_index.csv'),'w',encoding='utf-8-sig',newline='') as fp:
        writer=csv.writer(fp);writer.writerow(['부품','출력판','프로그램/건물','크기Xmm','크기Ymm','크기Zmm','원본대지Xmm','원본대지Ymm','원본대지Zmm','조립/출력 메모'])
        for p in sorted(placed,key=lambda p:p['id']):
            row=rows[p['id']];notes='유리 지붕 두께 0.6mm, 곡면 하부 서포트 필요' if row['kind']=='glass_roof' else ('연결 부품, 별도 출력 후 원래 높이에 접합' if not row['grounded'] else '상부 돌출부가 있는 경우 서포트 적용')
            writer.writerow([p['id'],p['plate'],', '.join(row['names']),*np.round(row['extent_mm'],3),*np.round(row['source_origin_mm'],3),notes])
    with open(os.path.join(HERE,'print_notes.txt'),'w',encoding='utf-8') as fp:
        fp.write(f'''구 경주역 매스 3D 출력 · 실제 1:1500\n\n원본: C:\\Users\\OFFICE\\Desktop\\구경주역_마스터플랜_최종.3dm\n원본 표기 단위는 mm이지만 25×100m 청사 매스가 25×100좌표이고, 층고 4m가 4좌표이다. 기존 정합 기록에서 최종 경계는 실제 지적과 축척 1로 정합되어 있다. 따라서 1원본단위=1m, 출력 좌표는 1000/1500=2/3배로 변환했다. 원본 파일은 수정하지 않았다.\n\n160×160mm 판 {len(plate_report)}장에 총 {len(placed)}개 부품. 첫 판 {plate_report[0]['parts']}개. 판 가장자리 여유 3mm, 부품 간 실제 최소 간격 {min_distance:.3f}mm. 전체 투영면적 {d['total_projected_area_mm2']:.1f}mm², 2mm 이격 포함 면적 {expanded_area:.1f}mm²로 한 판의 사용 가능 면적 {(SIZE-2*MARGIN)**2:.1f}mm²를 넘는다.\n\n슬라이서에서 단위를 mm로 하고 배율 100%로 가져온다. plate_01 / plate_02 파일은 같은 출력판 원점(0,0)을 사용하므로 각각 따로 가져와 출력한다. 이미 배열되어 있으므로 자동배치나 자동축소를 해제한다. 판 STL에는 기판/받침판이 포함되지 않는다.\n\n층 사이 홈: 높이 총 0.4mm, 평면 셋백 깊이 0.25mm. 실제 층 높이를 보존하고 층간 벽 부분만 후퇴시켰다. 제작동의 1.5m 수직 공백은 원래 층 위치를 유지하면서 안쪽으로 0.25mm 후퇴한 목으로 연결했다. 열린 모임지붕은 원래 지붕 면을 보존하고 하부를 닫았다. 유리 지붕은 별도 0.6mm 두께 부품으로 제작했다. 0.013mm 태양광 패널은 0.22mm로 보강해 지붕과 연결했다. 수치 오차에서 나온 0.01mm³ 미만 조각은 추적 기록에 남기고 제거했다.\n\n프로그램별로 Boolean Union하고, 다른 프로그램을 잇는 브리지·캐노피는 별도 출력 부품으로 뒀다. 출력물 위치와 번호는 plate_layout.png 및 parts_index.csv 참조. 원래 조립 위치·높이는 site_assembly_1_1500.3dm에 들어 있다.\n\n모든 STL은 닫힘·법선·양의 체적·출력판 범위·부품 간 이격을 검증했다. 원본 메쉬 {len(raw)}개 모두 산출물에 대응한다. 주변 참고 건물·수목·라벨·대지 평면은 건축 매스 출력에서 제외했다.\n\n기본 홈은 FDM 0.4mm 노즐을 고려해 생성했지만 프린터/재료가 아직 지정되지 않았다. 실제 출력 전에 슬라이서에서 레이어와 서포트를 확인한다. 상부 브리지·돌출부와 유리 지붕 하부에 서포트가 필요할 수 있다. 접촉 간격은 기하학 기준이며 서포트/브림 폭을 포함하지 않는다. 한 판을 촘촘히 쓰려면 브림 없이 출력하거나 겹치지 않도록 국부 브림을 설정한다.\n''')
    output_files=[x['stl'] for x in plate_report]+[model,site_path,os.path.join(HERE,'plate_layout.png'),os.path.join(HERE,'parts_index.csv'),os.path.join(HERE,'print_notes.txt'),os.path.join(HERE,'print_validation.json'),os.path.join(HERE,'prepared_manifest.json')]
    zpath=os.path.join(HERE,'gyeongju_print_1_1500.zip')
    with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED) as z:
        for path in output_files:z.write(path,os.path.basename(path))
        for row in d['parts']:z.write(row['stl'],'parts/'+row['id']+'.stl')
    print('완료',json.dumps(plate_report,ensure_ascii=False),'최소이격',min_distance,'소요',time.time()-t,flush=True)

def collections_default():
    from collections import defaultdict
    return defaultdict(list)

def add_rhino(file,mesh,row,placement,layers):
    root=f"plate_{placement['plate']:02d}" if placement['plate'] else 'site_assembly'
    name=root+'_'+','.join(row['programs'])[:70]
    if name not in layers:
        layer=r3.Layer();layer.Name=name;layer.Color=tuple(row['color'])+(255,);layers[name]=file.Layers.Add(layer)
    rm=r3.Mesh()
    for x,y,z in mesh.vertices:rm.Vertices.Add(float(x),float(y),float(z))
    for a,b,c in mesh.faces:rm.Faces.AddFace(int(a),int(b),int(c))
    rm.Normals.ComputeNormals();rm.Compact()
    att=r3.ObjectAttributes();att.LayerIndex=layers[name];att.Name=row['id']+' '+', '.join(row['names']);att.ObjectColor=tuple(row['color'])+(255,);att.ColorSource=r3.ObjectColorSource.ColorFromObject
    att.SetUserString('print_scale','1:1500');att.SetUserString('part_id',row['id']);att.SetUserString('source_ids',','.join(row['source_ids']));att.SetUserString('source_origin_mm',str(row['source_origin_mm']))
    file.Objects.AddMesh(rm,att)

if __name__=='__main__':main()
