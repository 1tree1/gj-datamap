# 지도 PNG를 레드+흑백 팔레트로 바꾼다. mode: all(채색 전부 → 붉은 램프) / split(적·주황·노랑만 붉은 램프, 나머지 회색) / graynonred(순수 적색만 유지, 나머지 회색)
import sys, numpy as np
from PIL import Image
RED=np.array([200,16,46],float); DARK=np.array([90,0,18],float); WHITE=np.array([255,255,255],float)
def to_hsv(a):
    r,g,b=a[...,0],a[...,1],a[...,2]; mx=a.max(-1); mn=a.min(-1); d=mx-mn+1e-9
    h=np.where(mx==r,((g-b)/d)%6,np.where(mx==g,(b-r)/d+2,(r-g)/d+4))*60
    s=np.where(mx>0,d/(mx+1e-9),0); return h,s,mx
def ramp(L):
    # L in 0..1 luminance; light → near white, mid → RED, dark → DARK
    t=np.clip(1-L,0,1)[...,None]
    c1=WHITE*(1-t*1.25)+RED*(t*1.25); c2=RED*(1-(t-0.8)*5)+DARK*((t-0.8)*5)
    return np.where(t<0.8,c1,c2)
def recolor(src,dst,mode='all',smin=0.22,boost=1.0):
    im=Image.open(src).convert('RGB'); a=np.asarray(im).astype(float)/255
    h,s,v=to_hsv(a); L=0.299*a[...,0]+0.587*a[...,1]+0.114*a[...,2]
    gray=np.repeat((L*255)[...,None],3,-1)
    colored=(s>smin)&(v>0.12)
    redhue=((h<55)|(h>325))
    if mode=='all': target=colored
    elif mode=='split': target=colored&redhue
    elif mode=='graynonred': target=colored&redhue&(s>0.55)
    else: raise SystemExit(mode)
    Lt=np.clip(L*boost,0,1)
    out=np.where(target[...,None],ramp(Lt),gray)
    if mode=='graynonred': out=np.where(target[...,None],a*255,gray)
    Image.fromarray(np.clip(out,0,255).astype('uint8')).save(dst)
if __name__=='__main__':
    recolor(sys.argv[1],sys.argv[2],sys.argv[3] if len(sys.argv)>3 else 'all')
