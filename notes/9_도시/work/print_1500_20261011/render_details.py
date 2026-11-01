import os,sys,json
HERE=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,os.path.join(HERE,'vendor'))
import numpy as np,trimesh,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
plt.rcParams['font.family']='Malgun Gothic';plt.rcParams['axes.unicode_minus']=False
d=json.load(open(os.path.join(HERE,'prepared_manifest.json'),encoding='utf-8'))
rows={r['id']:r for r in d['parts']}
fig=plt.figure(figsize=(12,6))
for i,part_id in enumerate(['part_12','part_27']):
    r=rows[part_id];m=trimesh.load_mesh(r['stl'],process=True);ax=fig.add_subplot(1,2,i+1,projection='3d')
    view_direction=np.array([np.cos(np.radians(22))*np.cos(np.radians(-54)),np.cos(np.radians(22))*np.sin(np.radians(-54)),np.sin(np.radians(22))])
    visible=m.face_normals@view_direction>1e-6
    normals=m.face_normals[visible];light=np.array([-.6,-.3,.75]);light/=np.linalg.norm(light)
    strength=.45+.55*np.clip(normals@light,0,1)
    colors=np.clip(np.array(r['color'])[None,:]/255*strength[:,None],0,1)
    ax.add_collection3d(Poly3DCollection(m.triangles[visible],facecolors=colors,edgecolors='none',linewidths=0,zsort='average'))
    b=m.bounds;e=m.extents;c=b.mean(axis=0);span=max(e)
    ax.set_xlim(c[0]-span*.53,c[0]+span*.53);ax.set_ylim(c[1]-span*.53,c[1]+span*.53);ax.set_zlim(0,max(e[2]*1.25,span*.28))
    ax.set_box_aspect([1,1,.36]);ax.view_init(elev=22,azim=-54)
    ax.set_xlabel('mm');ax.set_ylabel('mm');ax.set_zlabel('mm')
    ax.set_title('층간 셋백 0.25mm · 홈 높이 0.4mm' if i==0 else '분리된 제작동 층을 후퇴한 목으로 연결',fontsize=12)
fig.tight_layout();fig.savefig(os.path.join(HERE,'setback_detail.png'),dpi=160);plt.close(fig)
