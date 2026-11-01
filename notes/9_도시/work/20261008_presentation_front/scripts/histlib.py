# -*- coding: utf-8 -*-
"""공용 유틸: 원본 영상 읽기(팔레트 적용), 경로, 변환."""
import os, glob, warnings
warnings.filterwarnings("ignore")
import numpy as np
import tifffile
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

ROOT = "C:/Users/OFFICE/Desktop/9_도시/"
WORK = ROOT + "work/20261008_presentation_front/"
HIST = WORK + "assets/hist/"
SCR = "C:/Users/OFFICE/AppData/Local/Temp/claude/C--Users-OFFICE-Desktop-9---/b98333f0-4ddf-4213-a0db-66cb837b3d35/scratchpad/"
PREV = SCR + "prev/"
BASE = ROOT + "대지/과거사진/경주 위성지도/"
ALT = ROOT + "대지/항공사진2025/"

SRC = {
 "a1954": BASE + "(B040)항공사진_195402001900010114.tif",
 "a1968": BASE + "(B040)항공사진_196800000200110024.tif",
 "a1982": BASE + "(B040)항공사진_198206000100180074.tif",
 "a2009": BASE + "(B040)항공사진_200903001200330066.TIF",
 "a2024": BASE + "(B040)항공사진_202402505C00370049.tif",
 "a2025_62": BASE + "(B040)항공사진_202504507C03060062.tif",
 "a2025_64": ALT + "(B040)항공사진_202504507C03070064.tif",
 "a2025_65": ALT + "(B040)항공사진_202504507C03070065.tif",
 "o2015": BASE + "(B060)정사영상_2015_35901069s.tif",
 "o2021": BASE + "(B060)정사영상_2021_35901069.tif",
 "o2025": BASE + "(B060)정사영상_2025_35901069.tif",
 "m1916": BASE + "(B120)종이지도_1916_경주_O00000016108_10000.tif",
 "m1916j": BASE + "1916축도.jpg",
 "m1918": BASE + "(B120)종이지도_1918_경주_O03590115601_050k.jpg",
 "m1918gb": BASE + "(B120)종이지도_1918_경상북도_O00000018003_500000.tif",
 "m1918gn": BASE + "(B120)종이지도_1918_경상남도_O00000018002_500000.tif",
 "m1956": BASE + "(B120)종이지도_1956_경주_SH0359015605_050k.tif",
 "m1969": BASE + "(B120)종이지도_1969_경주_SH3590146901_025k.tif",
 "m1972": BASE + "(B120)종이지도_1972_경주_L03590147201_025k.tif",
 "m1976": BASE + "(B120)종이지도_1976_경주_359010697601_005k.tif",
 "m1984": BASE + "(B120)종이지도_1984_경주_359010698401_005k.tif",
 "m1998": BASE + "(B120)종이지도_1998_경주_SH0359019803_050k.tif",
 "m2005": BASE + "(B120)종이지도_2005_경주_359014_2007_18200469615173_025k.tif",
 "m2024": BASE + "(B120)종이지도_2024_경주_35901_050k.tif",
}

def load_full(key, gray=False):
    """원본 전체를 RGB(또는 gray) ndarray로 읽는다 (큰 파일 주의). 팔레트·1bit는 변환."""
    f = SRC[key]
    if f.lower().endswith(('.jpg', '.jpeg', '.png')):
        im = Image.open(f)
        im = im.convert('L' if gray else 'RGB')
        return np.asarray(im)
    with tifffile.TiffFile(f) as tf:
        p = tf.pages[0]
        a = p.asarray()
        if p.photometric == 3 and 'ColorMap' in p.tags:
            cm = (np.array(p.tags['ColorMap'].value).reshape(3, -1) // 257).astype(np.uint8)
            a = np.stack([cm[0][a], cm[1][a], cm[2][a]], axis=-1)
        elif a.dtype == bool or p.bitspersample == 1:
            a = np.where(a, 0, 255).astype(np.uint8) if p.photometric == 0 else np.where(a, 255, 0).astype(np.uint8)
    if gray and a.ndim == 3:
        a = (0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]).astype(np.uint8)
    return a

def load_reduced(key, factor, gray=False):
    """정수 배율로 평균 축소해서 읽는다. (큰 파일은 줄 단위 처리)"""
    a = load_full(key, gray=gray)
    return block_mean(a, factor)

def block_mean(a, f):
    if f == 1:
        return a
    h, w = a.shape[:2]
    h2, w2 = h // f * f, w // f * f
    a = a[:h2, :w2]
    if a.ndim == 2:
        return a.reshape(h2 // f, f, w2 // f, f).mean(axis=(1, 3)).astype(np.uint8)
    return a.reshape(h2 // f, f, w2 // f, f, a.shape[2]).mean(axis=(1, 3)).astype(np.uint8)


# ---------------------------------------------------------------------------
# 기하 도구: 모든 변환은 cv2 관례(픽셀 중심 = 정수 좌표, 좌상단 픽셀 중심 = (0,0))
# H_src2geo : 3x3, [col,row,1] -> [X,Y,1] (EPSG:5187, m).  수치 안정을 위해 (CX,CY) 기준 상대좌표로 저장.
# ---------------------------------------------------------------------------
import json, cv2
CX, CY = 219780.0, 360850.0
FRAMES = {
    "F1": dict(x0=CX - 600, x1=CX + 600, y0=CY - 800, y1=CY + 800, w=1800, h=2400),
    "F2": dict(x0=CX - 1500, x1=CX + 1500, y0=CY - 2000, y1=CY + 2000, w=1500, h=2000),
}
NODATA = (227, 227, 227)  # 자료 없는 영역 채움색 (RGB)
RED = (215, 25, 28)       # #D7191C

def frame_out2geo(fr):
    """출력 틀 픽셀(u,v) -> 5187 상대좌표(X-CX, Y-CY)"""
    f = FRAMES[fr]
    s = (f["x1"] - f["x0"]) / f["w"]
    return np.array([[s, 0, f["x0"] + 0.5 * s - CX], [0, -s, f["y1"] - 0.5 * s - CY], [0, 0, 1]], float), s

def ortho_H(ox, oy, px):
    """정사영상(좌상단 모서리 5187 좌표 ox,oy / 화소크기 px) -> H_src2geo(상대좌표)"""
    return np.array([[px, 0, ox + 0.5 * px - CX], [0, -px, oy - 0.5 * px - CY], [0, 0, 1]], float)

def apply_H(H, pts):
    pts = np.asarray(pts, float).reshape(-1, 2)
    q = np.c_[pts, np.ones(len(pts))] @ H.T
    return q[:, :2] / q[:, 2:3]

def fit_transform(src, geo, model="affine", ransac=None):
    """src(col,row) -> geo(X,Y) 절대좌표. 반환 H(상대좌표), inlier mask"""
    src = np.asarray(src, np.float64).reshape(-1, 2)
    g = np.asarray(geo, np.float64).reshape(-1, 2) - np.array([CX, CY])
    if model == "similarity":
        A, inl = cv2.estimateAffinePartial2D(src, g, method=cv2.RANSAC if ransac else cv2.LMEDS, ransacReprojThreshold=ransac or 3.0, maxIters=5000, confidence=0.999)
        H = np.vstack([A, [0, 0, 1]])
    elif model == "affine":
        if ransac:
            A, inl = cv2.estimateAffine2D(src, g, method=cv2.RANSAC, ransacReprojThreshold=ransac, maxIters=5000, confidence=0.999)
        else:
            A, _ = cv2.estimateAffine2D(src, g, method=cv2.LMEDS)
            inl = np.ones(len(src), np.uint8)
            # 최소제곱
            M = np.c_[src, np.ones(len(src))]
            sol, *_ = np.linalg.lstsq(M, g, rcond=None)
            A = sol.T
        H = np.vstack([A, [0, 0, 1]])
    elif model == "homography":
        H, inl = cv2.findHomography(src, g, cv2.RANSAC if ransac else 0, ransac or 3.0)
    else:
        raise ValueError(model)
    return H, (inl.ravel().astype(bool) if inl is not None else np.ones(len(src), bool))

def residuals(H, src, geo):
    """RMS(m) 및 개별 잔차"""
    p = apply_H(H, src) + np.array([CX, CY])
    d = p - np.asarray(geo, float).reshape(-1, 2)
    r = np.hypot(d[:, 0], d[:, 1])
    return float(np.sqrt((r ** 2).mean())), r

def prescale_matrix(p):
    """사전 축소(정수 배율 p) 영상 좌표 -> 원본 좌표 (픽셀 중심 관례)"""
    return np.array([[p, 0, (p - 1) / 2.0], [0, p, (p - 1) / 2.0], [0, 0, 1]], float)

def warp_to_frame(src, H_src2geo, fr, src_gsd_m, interp=cv2.INTER_CUBIC, valid_poly=None, prescaled=1):
    """src: ndarray(원본 또는 정수 축소본, prescaled=p). valid_poly: 원본 픽셀좌표 다각형(Nx2) 바깥은 자료 없음.
    반환: out(h,w[,3]) uint8, mask(h,w) bool"""
    f = FRAMES[fr]
    O2G, s = frame_out2geo(fr)
    Hp = H_src2geo @ prescale_matrix(prescaled)             # 축소본 픽셀 -> geo
    M = np.linalg.inv(Hp) @ O2G                              # 출력 픽셀 -> 축소본 픽셀
    w, h = f["w"], f["h"]
    out = cv2.warpPerspective(src, M, (w, h), flags=interp | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    one = np.zeros(src.shape[:2], np.uint8)
    if valid_poly is None:
        one[:] = 255
    else:
        vp = np.asarray(valid_poly, float)
        # 원본 픽셀 -> 축소본 픽셀
        vq = (vp - (prescaled - 1) / 2.0) / prescaled
        cv2.fillPoly(one, [np.round(vq).astype(np.int32)], 255)
    mask = cv2.warpPerspective(one, M, (w, h), flags=cv2.INTER_NEAREST | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_CONSTANT, borderValue=0) > 127
    return out, mask

def pick_prescale(src_gsd_m, fr):
    O2G, s = frame_out2geo(fr)
    sc = s / src_gsd_m
    return max(1, int(np.floor(sc * 0.999)))

def prescale(a, p):
    if p == 1:
        return a
    h, w = a.shape[:2]
    return cv2.resize(a, (w // p, h // p), interpolation=cv2.INTER_AREA)

def fill_nodata(out, mask, color=NODATA):
    out = out.copy()
    if out.ndim == 2:
        out[~mask] = int(round(0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]))
    else:
        out[~mask] = color
    return out

def plan_outline_px(fr):
    """계획 경계 -> 출력 틀 픽셀 좌표 목록"""
    import geopandas as gpd
    g = gpd.read_file(ROOT + "work/20261005_boundary_check/user_boundary_current_5187.geojson").to_crs(5187)
    f = FRAMES[fr]
    s = (f["x1"] - f["x0"]) / f["w"]
    res = []
    for geom in g.geometry:
        c = np.asarray(geom.exterior.coords)[:, :2]
        res.append(np.stack([(c[:, 0] - f["x0"]) / s, (f["y1"] - c[:, 1]) / s], 1))
    return res

def draw_outline(img, fr, width=3):
    """RGB(또는 gray) 영상에 계획 경계(빨강 #D7191C)를 얹는다 -> RGB"""
    if img.ndim == 2:
        img = np.stack([img] * 3, -1)
    img = np.ascontiguousarray(img.copy())
    for p in plan_outline_px(fr):
        cv2.polylines(img, [np.round(p * 16).astype(np.int32)], True, RED, width, cv2.LINE_AA, shift=4)
    return img

def clahe_gray(a, clip=2.0, tiles=8):
    c = cv2.createCLAHE(clipLimit=clip, tileGridSize=(tiles, tiles))
    return c.apply(a)

def save_jpg(path, a, q=90):
    Image.fromarray(a).save(path, quality=q, subsampling=0, optimize=True)

def save_png(path, a):
    Image.fromarray(a).save(path, optimize=True)

def save_transform(key, H, info):
    d = dict(info)
    d["H_src2geo_rel"] = H.tolist()
    d["origin"] = [CX, CY]
    os.makedirs(WORK + "research/hist_transforms", exist_ok=True)
    json.dump(d, open(WORK + f"research/hist_transforms/{key}.json", "w"), ensure_ascii=False, indent=1)

def load_transform(key):
    d = json.load(open(WORK + f"research/hist_transforms/{key}.json"))
    return np.array(d["H_src2geo_rel"]), d


# ---------------------------------------------------------------------------
# 특징점 정합 (SIFT + RANSAC)
# ---------------------------------------------------------------------------
def sift_match(img_a, img_b, nfeat=30000, ratio=0.78, contrast=0.02, clahe=True, mask_a=None, mask_b=None, verbose=True):
    """img_a, img_b: uint8 gray. 반환: (pts_a, pts_b) 대응점(ratio test 통과)"""
    if clahe:
        c = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        img_a = c.apply(img_a); img_b = c.apply(img_b)
    sift = cv2.SIFT_create(nfeatures=nfeat, contrastThreshold=contrast, edgeThreshold=12)
    ka, da = sift.detectAndCompute(img_a, mask_a)
    kb, db = sift.detectAndCompute(img_b, mask_b)
    if verbose:
        print("  sift keypoints", len(ka), len(kb))
    if da is None or db is None or len(ka) < 8 or len(kb) < 8:
        return np.zeros((0, 2)), np.zeros((0, 2))
    bf = cv2.BFMatcher(cv2.NORM_L2)
    m = bf.knnMatch(da, db, k=2)
    good = [x[0] for x in m if len(x) == 2 and x[0].distance < ratio * x[1].distance]
    pa = np.float32([ka[x.queryIdx].pt for x in good])
    pb = np.float32([kb[x.trainIdx].pt for x in good])
    if verbose:
        print("  matches after ratio test", len(good))
    return pa, pb

def ransac_model(pa, pb, model="similarity", thr=4.0):
    """pa -> pb 변환 (3x3) 과 inlier 마스크"""
    pa = np.ascontiguousarray(pa, dtype=np.float64).reshape(-1, 2)
    pb = np.ascontiguousarray(pb, dtype=np.float64).reshape(-1, 2)
    if len(pa) < 4:
        return None, None
    if model == "similarity":
        A, inl = cv2.estimateAffinePartial2D(pa, pb, method=cv2.RANSAC, ransacReprojThreshold=thr, maxIters=20000, confidence=0.9999)
        H = None if A is None else np.vstack([A, [0, 0, 1]])
    elif model == "affine":
        A, inl = cv2.estimateAffine2D(pa, pb, method=cv2.RANSAC, ransacReprojThreshold=thr, maxIters=20000, confidence=0.9999)
        H = None if A is None else np.vstack([A, [0, 0, 1]])
    else:
        H, inl = cv2.findHomography(pa, pb, cv2.RANSAC, thr, maxIters=20000, confidence=0.9999)
    if H is None:
        return None, None
    return H, inl.ravel().astype(bool)

def ref_ortho2025_gray(res_m=1.0):
    """2025 정사영상을 res_m 해상도로 축소한 참조 영상과 (참조 픽셀->geo 상대좌표) H 를 돌려준다 (캐시)."""
    f = int(round(res_m / 0.25))
    cache = SCR + f"ref_o2025_{f}.npy"
    if os.path.exists(cache):
        g = np.load(cache)
    else:
        a = load_full("o2025", gray=True)
        g = cv2.resize(a, (a.shape[1] // f, a.shape[0] // f), interpolation=cv2.INTER_AREA)
        np.save(cache, g)
    Hf, _ = load_transform("o2025")
    # ref px (축소) -> 원본 px -> geo
    Hr = Hf @ prescale_matrix(f)
    return g, Hr


def valid_polygon_photo(gray_ds, ds, erode_px=30, thr=25):
    """항공사진 스캔의 유효(사진) 영역 다각형을 원본 픽셀 좌표로 반환.
    gray_ds: 축소 gray, ds: 축소 배율. 가장 큰 밝은 연결성분 -> 구멍 메움 -> 침식 -> 근사 다각형"""
    b = cv2.GaussianBlur(gray_ds, (0, 0), 3)
    m = (b > thr).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(m, 8)
    if n < 2:
        return None, None
    k = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
    comp = (lab == k).astype(np.uint8)
    # 구멍 메움
    cnts, _ = cv2.findContours(comp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filled = np.zeros_like(comp)
    cv2.drawContours(filled, cnts, -1, 1, -1)
    er = cv2.erode(filled, np.ones((2 * erode_px + 1, 2 * erode_px + 1), np.uint8))
    cnts, _ = cv2.findContours(er, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    c = max(cnts, key=cv2.contourArea)
    eps = 0.003 * cv2.arcLength(c, True)
    ap = cv2.approxPolyDP(c, eps, True)[:, 0, :].astype(float)
    poly_full = ap * ds + (ds - 1) / 2.0
    return er, poly_full


def warp_to_grid(src, H_src2geo, H_grid2geo, size_wh, interp=cv2.INTER_LINEAR):
    """src(축소본 등) 픽셀 -> geo 변환 H_src2geo, 출력 격자 픽셀 -> geo 변환 H_grid2geo. 출력(h,w)"""
    M = np.linalg.inv(H_src2geo) @ H_grid2geo
    return cv2.warpPerspective(src, M, size_wh, flags=interp | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_CONSTANT, borderValue=0)

def refine_register(src_ds, H_ds2geo, ref, Hr, iters=3, maxdisp_px=40, ratio=0.85, model="homography", thr=3.0, mask_ds=None, nfeat=30000, verbose=True, contrast=0.015):
    """src_ds: 축소 gray, H_ds2geo: 초기 변환(축소 픽셀 -> geo 상대좌표), ref/Hr: 참조 영상과 (픽셀->geo).
    반복: src를 ref 격자에 워핑 -> SIFT 대응 -> 변위 제한 -> RANSAC -> 갱신. 반환 H_ds2geo, 마지막 대응(n, 잔차)"""
    H = H_ds2geo.copy()
    hh, ww = ref.shape
    last = None
    for it in range(iters):
        Wm = warp_to_grid(src_ds, H, Hr, (ww, hh))
        Mk = None
        if mask_ds is not None:
            Mk = warp_to_grid(mask_ds, H, Hr, (ww, hh), interp=cv2.INTER_NEAREST)
            Mk = (Mk > 127).astype(np.uint8) * 255
        pa, pb = sift_match(Wm, ref, nfeat=nfeat, ratio=ratio, contrast=contrast, mask_a=Mk, verbose=False)
        if len(pa) < 8:
            if verbose: print("   iter", it, "too few matches", len(pa))
            break
        d = np.hypot(*(pa - pb).T)
        keep = d < maxdisp_px
        pa, pb = pa[keep], pb[keep]
        if len(pa) < 8:
            if verbose: print("   iter", it, "too few after disp filter", len(pa))
            break
        Hf, inl = ransac_model(pa, pb, model, thr=thr)
        if Hf is None:
            break
        # Wm 픽셀 -> ref 픽셀 이 Hf. Wm 픽셀 q 는 src 에서 H^-1 Hr q 에 해당 -> 갱신: 새로운 src->geo = Hr Hf Hr^-1 ... 
        # Wm px q  -> geo: Hr q ; ref px p -> geo: Hr p ; 정합 후 q 는 p=Hf q 위치와 같은 점. 따라서 geo_new(src point) = Hr Hf (Wm px of that src point)
        # Wm px of src point s = (Hr^-1 H) s  =>  H_new = Hr Hf Hr^-1 H
        H = Hr @ Hf @ np.linalg.inv(Hr) @ H
        n = int(inl.sum())
        resid = np.hypot(*((apply_H(Hf, pa[inl]) - pb[inl]).T))
        if verbose:
            print(f"   iter {it}: matches {len(pa)}, inliers {n}, mean disp before {d[keep].mean():.1f}px, resid {np.sqrt((resid**2).mean()):.2f}px")
        last = (n, float(np.sqrt((resid ** 2).mean())))
    return H, last


def check_overlay(key, ref, Hr, src_gray_ds, H_ds2geo, name, crop=None, scale=1.0):
    """src를 ref 격자에 워핑한 뒤 [ref | warped | 색합성(R=ref,GB=warped)] 3면 이미지를 저장.
    crop=(x0,y0,x1,y1) ref 픽셀 범위"""
    hh, ww = ref.shape
    Wm = warp_to_grid(src_gray_ds, H_ds2geo, Hr, (ww, hh))
    if crop is None:
        crop = (0, 0, ww, hh)
    x0, y0, x1, y1 = crop
    r = ref[y0:y1, x0:x1]; w = Wm[y0:y1, x0:x1]
    r_ = cv2.createCLAHE(2.0, (8, 8)).apply(r); w_ = cv2.createCLAHE(2.0, (8, 8)).apply(w)
    comp = np.dstack([w_, w_, r_])[..., ::-1]  # BGR: B=ref? 아래에서 RGB 로 정리
    comp = np.dstack([r_, w_, w_])  # RGB: R=ref, G=B=warped
    trip = np.concatenate([np.dstack([r_] * 3), np.dstack([w_] * 3), comp], axis=1)
    if scale != 1.0:
        trip = cv2.resize(trip, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    Image.fromarray(trip).save(SCR + f"prev/{name}.png")
    return trip.shape


def _local_norm(img, sigma=12):
    f = img.astype(np.float32)
    mu = cv2.GaussianBlur(f, (0, 0), sigma)
    d = f - mu
    sd = np.sqrt(cv2.GaussianBlur(d * d, (0, 0), sigma)) + 3.0
    return d / sd

def tile_displacements(Wm, ref, T=192, stride=128, S=28, min_score=0.25, mask=None, use_edges=False, blur=1.0):
    """Wm(워핑된 src), ref: 같은 격자. 반환 배열 [cx, cy, dx, dy, score] (dx,dy: ref 에서의 위치 - Wm 위치, px)"""
    a = _local_norm(cv2.GaussianBlur(Wm, (0, 0), blur))
    b = _local_norm(cv2.GaussianBlur(ref, (0, 0), blur))
    if use_edges:
        def ed(x):
            gx = cv2.Sobel(x, cv2.CV_32F, 1, 0, ksize=3); gy = cv2.Sobel(x, cv2.CV_32F, 0, 1, ksize=3)
            return cv2.GaussianBlur(np.sqrt(gx * gx + gy * gy), (0, 0), 1.5)
        a = ed(a); b = ed(b)
    hh, ww = ref.shape
    out = []
    for y in range(S, hh - T - S, stride):
        for x in range(S, ww - T - S, stride):
            if mask is not None and mask[y:y + T, x:x + T].mean() < 0.9:
                continue
            tpl = a[y:y + T, x:x + T]
            if tpl.std() < 0.3:
                continue
            sea = b[y - S:y + T + S, x - S:x + T + S]
            r = cv2.matchTemplate(sea, tpl, cv2.TM_CCOEFF_NORMED)
            _, mx, _, ml = cv2.minMaxLoc(r)
            dx, dy = ml
            # 서브픽셀
            def para(p0, p1, p2):
                d = p0 - 2 * p1 + p2
                return 0.0 if d == 0 else 0.5 * (p0 - p2) / d
            sx = para(r[dy, dx - 1], r[dy, dx], r[dy, dx + 1]) if 0 < dx < r.shape[1] - 1 else 0
            sy = para(r[dy - 1, dx], r[dy, dx], r[dy + 1, dx]) if 0 < dy < r.shape[0] - 1 else 0
            # 두 번째 봉우리 대비 선명도
            r2 = r.copy(); r2[max(0, dy - 4):dy + 5, max(0, dx - 4):dx + 5] = -1
            sharp = mx - r2.max()
            if mx >= min_score:
                out.append((x + T / 2, y + T / 2, dx + sx - S, dy + sy - S, mx, sharp))
    return np.array(out)

def refine_dense(src_ds, H_ds2geo, ref, Hr, iters=4, model="homography", T=192, stride=128, S=28, min_score=0.25, thr=2.5, mask_ds=None, verbose=True, use_edges=False, min_sharp=0.03, blur=1.0):
    H = H_ds2geo.copy()
    hh, ww = ref.shape
    for it in range(iters):
        Wm = warp_to_grid(src_ds, H, Hr, (ww, hh))
        Mk = None
        if mask_ds is not None:
            Mk = (warp_to_grid(mask_ds, H, Hr, (ww, hh), interp=cv2.INTER_NEAREST) > 127).astype(np.float32)
        d = tile_displacements(Wm, ref, T=T, stride=stride, S=S, min_score=min_score, mask=Mk, use_edges=use_edges, blur=blur)
        if len(d) < 6:
            if verbose: print("   iter", it, "too few tiles", len(d)); 
            return H, None
        d = d[d[:, 5] >= min_sharp] if (d[:, 5] >= min_sharp).sum() >= 6 else d
        pw = d[:, :2]; pr = d[:, :2] + d[:, 2:4]
        Hf, inl = ransac_model(pw, pr, model, thr=thr)
        if Hf is None:
            return H, None
        n = int(inl.sum())
        resid = np.hypot(*((apply_H(Hf, pw[inl]) - pr[inl]).T))
        md = np.hypot(d[:, 2], d[:, 3])
        if verbose:
            print(f"   iter {it}: tiles {len(d)}, inliers {n}, median |disp| {np.median(md):.1f}px, inlier resid RMS {np.sqrt((resid**2).mean()):.2f}px, median score {np.median(d[:,4]):.2f}")
        H = Hr @ Hf @ np.linalg.inv(Hr) @ H
        if np.median(md) < 0.6 and it > 0:
            break
    return H, dict(tiles=len(d), inliers=n, rms_px=float(np.sqrt((resid ** 2).mean())), disp=d, inl=inl)


def grid_H(x0, y1, res):
    """격자(좌상단 모서리 x0,y1 / 화소 res m) 픽셀 -> geo 상대좌표"""
    return np.array([[res, 0, x0 + 0.5 * res - CX], [0, -res, y1 - 0.5 * res - CY], [0, 0, 1]], float)

def render_ref_from_photo(key, x0, y1, w, h, res, valid=None, clahe=False, name=None):
    """등록된 사진을 5187 격자로 렌더링해 참조 영상 저장(gray). 반환 (gray, mask, Hgrid)"""
    H, info = load_transform(key)
    gsd = float(np.sqrt(abs(np.linalg.det(H[:2, :2]))))
    a = load_full(key, gray=True)
    f = max(1, int(np.floor(res / gsd * 0.999)))
    src = prescale(a, f)
    Hg = grid_H(x0, y1, res)
    Hp = H @ prescale_matrix(f)
    out = warp_to_grid(src, Hp, Hg, (w, h), interp=cv2.INTER_AREA if False else cv2.INTER_LINEAR)
    one = np.zeros(src.shape, np.uint8)
    if valid is None:
        one[:] = 255
    else:
        vq = (np.array(valid) - (f - 1) / 2.0) / f
        cv2.fillPoly(one, [np.round(vq).astype(np.int32)], 255)
    mask = warp_to_grid(one, Hp, Hg, (w, h), interp=cv2.INTER_NEAREST) > 127
    if name:
        np.save(SCR + f"ref_{name}.npy", out)
        json.dump(dict(H=Hg.tolist(), x0=x0, y1=y1, w=w, h=h, res=res), open(SCR + f"ref_{name}.json", "w"))
        np.save(SCR + f"refmask_{name}.npy", mask)
    return out, mask, Hg

def coarse_search(src_ds, src_ds_gsd, mask_ds, ref, ref_mask, ref_res, Hg, angles, gsds, topk=5, norm_sigma=10, verbose=True):
    """src_ds: 축소 gray(화소 src_ds_gsd m 가정), 참조 ref(화소 ref_res m). 회전·축척 격자탐색 + 평행이동 NCC.
    반환: 점수순 후보 리스트 (score, angle, gsd, H_ds2geo)"""
    refn = _local_norm(ref, norm_sigma)
    refn[~ref_mask] = 0
    results = []
    h0, w0 = src_ds.shape
    srcn = _local_norm(src_ds, norm_sigma)
    if mask_ds is not None:
        srcn[mask_ds == 0] = 0
    c = np.array([(w0 - 1) / 2.0, (h0 - 1) / 2.0])
    for gsd in gsds:
        s = gsd / ref_res    # ds 화소 -> ref 화소 배율
        for ang in angles:
            th = np.radians(ang)
            R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]]) * s
            # src px -> ref-scale px (중심 기준 회전·축척), 출력 크기는 외접 사각형
            ow = int(np.ceil(abs(R[0, 0]) * w0 + abs(R[0, 1]) * h0)); oh = int(np.ceil(abs(R[1, 0]) * w0 + abs(R[1, 1]) * h0))
            t = np.array([ow / 2.0, oh / 2.0]) - R @ c
            A = np.hstack([R, t[:, None]]).astype(np.float32)
            tpl = cv2.warpAffine(srcn, A, (ow, oh), flags=cv2.INTER_LINEAR, borderValue=0)
            if tpl.shape[0] >= refn.shape[0] or tpl.shape[1] >= refn.shape[1]:
                # 템플릿이 더 크면 참조를 템플릿으로 보고 반대로 수행
                continue
            r = cv2.matchTemplate(refn, tpl, cv2.TM_CCOEFF_NORMED)
            _, mx, _, ml = cv2.minMaxLoc(r)
            # tpl 좌상단이 ref 의 ml 위치 -> src px p -> tpl px (R p + t) -> ref px = tpl px + ml
            Ap = np.vstack([np.hstack([R, (t + np.array(ml))[:, None]]), [0, 0, 1]])
            Hds2geo = Hg @ Ap
            results.append((float(mx), float(ang), float(gsd), Hds2geo))
    results.sort(key=lambda x: -x[0])
    if verbose:
        for r_ in results[:topk]:
            print(f"   score {r_[0]:.3f} angle {r_[1]:+.1f} ds-px {r_[2]:.2f} m")
    return results[:topk]


def draw_grid_px(img_gray, step, label_scale=0.5, color=(0, 0, 255), origin=(0, 0), val_scale=1.0, fmt="{:.0f}", thick=1):
    """px 격자 + 라벨. origin: 좌상단 픽셀의 (원본 좌표계) 좌표. 반환 BGR"""
    im = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2BGR) if img_gray.ndim == 2 else img_gray.copy()
    h, w = im.shape[:2]
    for x in range(0, w, step):
        cv2.line(im, (x, 0), (x, h), color, thick)
        cv2.putText(im, fmt.format(origin[0] + x * val_scale), (x + 2, 14), cv2.FONT_HERSHEY_SIMPLEX, label_scale, color, 1, cv2.LINE_AA)
    for y in range(0, h, step):
        cv2.line(im, (0, y), (w, y), color, thick)
        cv2.putText(im, fmt.format(origin[1] + y * val_scale), (2, y - 3), cv2.FONT_HERSHEY_SIMPLEX, label_scale, color, 1, cv2.LINE_AA)
    return im

def geo_grid_preview(gray, Hg, x_lo, x_hi, y_lo, y_hi, step_m=500, scale=1.0, label_scale=0.5):
    """격자(Hg: px->geo 상대)에서 geo 범위를 잘라 (x_lo..x_hi, y_lo..y_hi 절대좌표) 500 m 격자 라벨을 얹어 BGR 반환.
    반환: 이미지, 변환 dict(px->geo)"""
    # 격자 해상도 / 좌상단
    res = Hg[0, 0]
    gx0 = Hg[0, 2] + CX - 0.5 * res
    gy1 = Hg[1, 2] + CY + 0.5 * res
    c0 = int((x_lo - gx0) / res); c1 = int((x_hi - gx0) / res)
    r0 = int((gy1 - y_hi) / res); r1 = int((gy1 - y_lo) / res)
    c0 = max(c0, 0); r0 = max(r0, 0); c1 = min(c1, gray.shape[1]); r1 = min(r1, gray.shape[0])
    sub = gray[r0:r1, c0:c1]
    sub = cv2.createCLAHE(2.0, (8, 8)).apply(sub)
    im = cv2.cvtColor(sub, cv2.COLOR_GRAY2BGR)
    if scale != 1.0:
        im = cv2.resize(im, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA if scale < 1 else cv2.INTER_CUBIC)
    # geo 격자선
    X0 = gx0 + c0 * res; Y1 = gy1 - r0 * res
    s_eff = res / scale
    xs = np.arange(np.ceil(X0 / step_m) * step_m, X0 + (c1 - c0) * res + 1, step_m)
    ys = np.arange(np.ceil((Y1 - (r1 - r0) * res) / step_m) * step_m, Y1 + 1, step_m)
    for gx_ in xs:
        u = int((gx_ - X0) / s_eff)
        cv2.line(im, (u, 0), (u, im.shape[0]), (0, 0, 255), 1)
        cv2.putText(im, f"{gx_:.0f}", (u + 3, 14), cv2.FONT_HERSHEY_SIMPLEX, label_scale, (0, 0, 255), 1, cv2.LINE_AA)
    for gy_ in ys:
        v = int((Y1 - gy_) / s_eff)
        cv2.line(im, (0, v), (im.shape[1], v), (0, 0, 255), 1)
        cv2.putText(im, f"{gy_:.0f}", (3, v - 3), cv2.FONT_HERSHEY_SIMPLEX, label_scale, (0, 0, 255), 1, cv2.LINE_AA)
    tr = dict(X0=X0, Y1=Y1, s=s_eff)
    return im, tr


def patch_vote(src_ds, mask_ds, ref, ref_mask, angles, scales, patch=112, stride=96, min_cov=0.97, min_std=0.45, norm_sigma=7, bin_px=6, verbose=True, topn=3):
    """로컬 패치 NCC 투표로 (회전, 축척, 평행이동) 거친 추정.
    scales: src ds 화소 -> ref 화소 배율 후보. 반환: 상위 후보 리스트[(count, score_sum, angle, scale, t(x,y))] 및 해당 대응점들"""
    h0, w0 = src_ds.shape
    srcn = _local_norm(src_ds, norm_sigma)
    refn = _local_norm(ref, norm_sigma)
    if ref_mask is not None:
        refn[ref_mask == 0] = 0
    if mask_ds is not None:
        srcn[mask_ds == 0] = 0
    c0 = np.array([(w0 - 1) / 2.0, (h0 - 1) / 2.0])
    # 패치 중심 후보 (ds 좌표)
    cents = []
    for y in range(patch // 2 + 8, h0 - patch // 2 - 8, stride):
        for x in range(patch // 2 + 8, w0 - patch // 2 - 8, stride):
            if mask_ds is not None and mask_ds[y - patch // 2:y + patch // 2, x - patch // 2:x + patch // 2].mean() < 255 * min_cov:
                continue
            if srcn[y - patch // 2:y + patch // 2, x - patch // 2:x + patch // 2].std() < min_std:
                continue
            cents.append((x, y))
    cents = np.array(cents, float)
    if verbose:
        print("   patches", len(cents))
    out = []
    P2 = patch // 2
    for s in scales:
        for ang in angles:
            th = np.radians(ang)
            R = np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]]) * s
            ow = int(np.ceil(abs(R[0, 0]) * w0 + abs(R[0, 1]) * h0)) + 4
            oh = int(np.ceil(abs(R[1, 0]) * w0 + abs(R[1, 1]) * h0)) + 4
            t0 = np.array([ow / 2.0, oh / 2.0]) - R @ c0
            A = np.hstack([R, t0[:, None]]).astype(np.float32)
            srcw = cv2.warpAffine(srcn, A, (ow, oh), flags=cv2.INTER_LINEAR, borderValue=0)
            ts = []; scs = []; idx = []
            for i, c in enumerate(cents):
                cw = R @ (c - c0) + np.array([ow / 2.0, oh / 2.0])
                x0 = int(round(cw[0])) - P2; y0 = int(round(cw[1])) - P2
                if x0 < 0 or y0 < 0 or x0 + patch > ow or y0 + patch > oh:
                    continue
                tpl = srcw[y0:y0 + patch, x0:x0 + patch]
                if tpl.std() < 0.3:
                    continue
                r = cv2.matchTemplate(refn, tpl, cv2.TM_CCOEFF_NORMED)
                _, mx, _, ml = cv2.minMaxLoc(r)
                cref = np.array(ml, float) + P2 - (cw - np.array([x0 + P2, y0 + P2]))  # 패치 중심의 ref 위치
                # t: p_ref = R (p_src - c0) + t  -> t = cref - R (c - c0)
                t = cref - R @ (c - c0)
                ts.append(t); scs.append(mx); idx.append(i)
            if len(ts) < 4:
                continue
            ts = np.array(ts); scs = np.array(scs); idx = np.array(idx)
            # 2D 히스토그램 군집 (가중)
            keys = np.floor(ts / bin_px).astype(int)
            best_c = None
            from collections import defaultdict
            acc = defaultdict(list)
            for k, (kx, ky) in enumerate(keys):
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        acc[(kx + dx, ky + dy)].append(k)
            bk = max(acc.items(), key=lambda kv: (len(kv[1]), sum(scs[j] for j in kv[1])))
            members = bk[1]
            cnt = len(members); ssum = float(sum(scs[j] for j in members))
            tm = np.median(ts[members], axis=0)
            out.append((cnt, ssum, float(ang), float(s), tm, cents[idx[members]], ts[members], scs[members]))
    out.sort(key=lambda x: (-x[0], -x[1]))
    if verbose:
        for o in out[:6]:
            print(f"   count {o[0]:3d} score_sum {o[1]:.2f} angle {o[2]:+.1f} scale {o[3]:.3f}")
    return out[:topn], len(cents), c0


def embedded_map_H(key, crs="EPSG:5176"):
    """1976/1984 1:5000 지도의 내장 지리참조(미터) + 옛 좌표계 -> 5187 로 변환하는 아핀 근사 (원본 픽셀 -> geo 상대좌표).
    반환 H, 최대 근사오차(m)"""
    import rasterio
    from pyproj import Transformer
    with rasterio.open(SRC[key]) as r:
        T = r.transform; W, Hh = r.width, r.height
    tr = Transformer.from_crs(crs, "EPSG:5187", always_xy=True)
    cols = np.linspace(0, W - 1, 6); rows = np.linspace(0, Hh - 1, 8)
    C, R_ = np.meshgrid(cols, rows)
    E = T.c + T.a * (C + 0.5) + T.b * (R_ + 0.5)
    N = T.f + T.d * (C + 0.5) + T.e * (R_ + 0.5)
    X, Y = tr.transform(E, N)
    src = np.c_[C.ravel(), R_.ravel()]
    geo = np.c_[np.asarray(X).ravel(), np.asarray(Y).ravel()] - np.array([CX, CY])
    M = np.c_[src, np.ones(len(src))]
    sol, *_ = np.linalg.lstsq(M, geo, rcond=None)
    A = sol.T
    H = np.vstack([A, [0, 0, 1]])
    err = np.hypot(*((M @ sol - geo).T)).max()
    return H, float(err)


def detect_neatline(gray, ds=4, dark_thr=110, verbose=False):
    """종이지도 스캔에서 도곽(neatline) 사각형을 원본 픽셀 좌표 (x0,y0,x1,y1)로 추정한다.
    아이디어: 도곽 선은 지도 높이/너비 대부분을 가로지르는 긴 어두운 선 -> 행/열 프로필의 바깥쪽 강한 봉우리."""
    g = cv2.resize(gray, (gray.shape[1] // ds, gray.shape[0] // ds), interpolation=cv2.INTER_AREA)
    dark = (g < dark_thr).astype(np.float32)
    h, w = dark.shape
    # 열 프로필: 중앙 60% 높이 구간의 어두운 비율
    colp = dark[int(0.2 * h):int(0.6 * h), :].mean(0)
    rowp = dark[:, int(0.2 * w):int(0.8 * w)].mean(1)
    def edges(p, lo, hi, thr):
        idx = np.where(p > thr)[0]
        idx = idx[(idx > lo) & (idx < hi)]
        return idx
    # 좌/우: 가장 바깥의 강한 봉우리
    L = edges(colp, 0, int(0.5 * w), 0.6); R = edges(colp, int(0.5 * w), w, 0.6)
    T = edges(rowp, 0, int(0.4 * h), 0.6); B = edges(rowp, int(0.4 * h), h, 0.6)
    res = {}
    res["L"] = (L.min() if len(L) else None); res["R"] = (R.max() if len(R) else None)
    res["T"] = (T.min() if len(T) else None); res["B"] = (B.max() if len(B) else None)
    if verbose:
        print("neatline (ds px):", res)
    return {k: (None if v is None else int(v * ds)) for k, v in res.items()}, (colp, rowp)


def refine_neatline(gray, approx, win=18, sec=0.5):
    """대략적인 도곽(안쪽 선) 위치 approx=(x0,y0,x1,y1) 주변에서 가장 어두운 긴 선의 서브픽셀 위치를 찾는다.
    sec: 선분 길이 중 중앙 비율 구간만 사용."""
    x0, y0, x1, y1 = approx
    ink = (255 - gray.astype(np.float32))
    H, W = gray.shape
    def col_pos(xc, ya, yb):
        xs = np.arange(max(0, int(xc) - win), min(W, int(xc) + win + 1))
        prof = ink[int(ya):int(yb), xs[0]:xs[-1] + 1].mean(0)
        k = int(np.argmax(prof))
        # 서브픽셀: 질량중심(주변 ±2)
        lo, hi = max(0, k - 2), min(len(prof), k + 3)
        w = prof[lo:hi] - prof[lo:hi].min()
        return xs[0] + (lo + (w * np.arange(hi - lo)).sum() / max(w.sum(), 1e-6)) , float(prof[k])
    def row_pos(yc, xa, xb):
        ys = np.arange(max(0, int(yc) - win), min(H, int(yc) + win + 1))
        prof = ink[ys[0]:ys[-1] + 1, int(xa):int(xb)].mean(1)
        k = int(np.argmax(prof))
        lo, hi = max(0, k - 2), min(len(prof), k + 3)
        w = prof[lo:hi] - prof[lo:hi].min()
        return ys[0] + (lo + (w * np.arange(hi - lo)).sum() / max(w.sum(), 1e-6)), float(prof[k])
    ya = y0 + (y1 - y0) * (0.5 - sec / 2); yb = y0 + (y1 - y0) * (0.5 + sec / 2)
    xa = x0 + (x1 - x0) * (0.5 - sec / 2); xb = x0 + (x1 - x0) * (0.5 + sec / 2)
    L, sL = col_pos(x0, ya, yb); R, sR = col_pos(x1, ya, yb)
    T, sT = row_pos(y0, xa, xb); B, sB = row_pos(y1, xa, xb)
    return dict(L=L, R=R, T=T, B=B, strength=(sL, sR, sT, sB))

def corners_to_H(px_corners, geo_corners, model="affine"):
    """px_corners: 4x2 (TL, TR, BR, BL) 원본 픽셀(중심 관례), geo_corners: 4x2 절대좌표(5187). 반환 H(상대), RMS(m), 각 잔차"""
    H, _ = fit_transform(px_corners, geo_corners, model=model)
    rms, r = residuals(H, px_corners, geo_corners)
    return H, rms, r


def _bilinear(img, xs, ys):
    xs = np.asarray(xs, np.float32); ys = np.asarray(ys, np.float32)
    return cv2.remap(img, xs.reshape(1, -1), ys.reshape(1, -1), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE).ravel()

def fit_side(ink, p0, p1, win=25, nseg=50, seglen=80, margin=0.06, mode="line"):
    """변(p0->p1)의 근사선 주변에서 가장 어두운 선(또는 가장자리)을 구간별로 찾아 강건하게 직선 적합.
    반환: (점 c, 방향 u) 그리고 사용한 점 수/잔차"""
    p0 = np.asarray(p0, float); p1 = np.asarray(p1, float)
    d = p1 - p0; L = np.hypot(*d); u = d / L; n = np.array([-u[1], u[0]])
    offs = np.arange(-win, win + 1, 1.0)
    pts = []; strs = []
    ss = np.arange(-seglen / 2, seglen / 2 + 1, 4.0)
    for t in np.linspace(margin, 1 - margin, nseg):
        c = p0 + t * d
        prof = np.empty(len(offs), np.float32)
        for i, o in enumerate(offs):
            xs = c[0] + n[0] * o + u[0] * ss; ys = c[1] + n[1] * o + u[1] * ss
            prof[i] = _bilinear(ink, xs, ys).mean()
        if mode == "edge":
            g = np.gradient(cv2.GaussianBlur(prof.reshape(-1, 1), (1, 0), 1.5).ravel())
            k = int(np.argmax(np.abs(g)))
            sub = 0.0
            st = float(np.abs(g[k]))
        else:
            k = int(np.argmax(prof))
            lo, hi = max(0, k - 2), min(len(prof), k + 3)
            w = prof[lo:hi] - prof[lo:hi].min()
            sub = (w * np.arange(lo, hi)).sum() / max(w.sum(), 1e-6) - k
            st = float(prof[k] - np.median(prof))
        pts.append(c + n * (offs[k] + sub)); strs.append(st)
    pts = np.array(pts, np.float32); strs = np.array(strs)
    keep = strs >= np.percentile(strs, 30)
    vx, vy, x0, y0 = cv2.fitLine(pts[keep], cv2.DIST_HUBER, 0, 0.01, 0.01).ravel()
    # 재적합: 잔차 큰 점 제거
    cpt = np.array([x0, y0]); uu = np.array([vx, vy])
    nn = np.array([-uu[1], uu[0]])
    res = (pts - cpt) @ nn
    keep2 = keep & (np.abs(res) < max(2.5, 2.5 * np.median(np.abs(res[keep]))))
    if keep2.sum() >= 8:
        vx, vy, x0, y0 = cv2.fitLine(pts[keep2], cv2.DIST_L2, 0, 0.01, 0.01).ravel()
        cpt = np.array([x0, y0]); uu = np.array([vx, vy]); nn = np.array([-uu[1], uu[0]])
        res = (pts[keep2] - cpt) @ nn
    else:
        res = res[keep]
    return cpt, uu, float(np.sqrt((res ** 2).mean())), int(keep2.sum())

def intersect(l1, l2):
    c1, u1 = l1[:2]; c2, u2 = l2[:2]
    A = np.array([u1, -u2]).T
    t = np.linalg.solve(A, c2 - c1)
    return c1 + t[0] * u1

def frame_corners(gray, approx_corners, win=25, mode="line"):
    """approx_corners: TL,TR,BR,BL (x,y). 반환: 4 모서리(정밀), 각 변 적합 정보"""
    ink = (255 - gray).astype(np.float32)
    tl, tr, br, bl = [np.asarray(c, float) for c in approx_corners]
    top = fit_side(ink, tl, tr, win, mode=mode); right = fit_side(ink, tr, br, win, mode=mode)
    bottom = fit_side(ink, bl, br, win, mode=mode); left = fit_side(ink, tl, bl, win, mode=mode)
    TL = intersect(top, left); TR = intersect(top, right); BR = intersect(bottom, right); BL = intersect(bottom, left)
    info = dict(top=top[2:], right=right[2:], bottom=bottom[2:], left=left[2:])
    return np.array([TL, TR, BR, BL]), info

def auto_content_frame(gray, band=(0.30, 0.62), thr=0.18, ds=4):
    """내용(지도면) 영역의 대략적 사각형을 잉크 밀도 프로필로 추정 (원본 픽셀): (x0,y0,x1,y1)"""
    g = cv2.resize(gray, (gray.shape[1] // ds, gray.shape[0] // ds), interpolation=cv2.INTER_AREA)
    ink = (g < 235).astype(np.float32)
    h, w = ink.shape
    def longest(p, thr):
        m = cv2.GaussianBlur(p.reshape(-1, 1), (1, 0), 3).ravel() > thr
        best = (0, 0, 0); i = 0
        while i < len(m):
            if m[i]:
                j = i
                while j < len(m) and m[j]:
                    j += 1
                if j - i > best[0]:
                    best = (j - i, i, j)
                i = j
            else:
                i += 1
        return best[1], best[2]
    colp = ink[int(band[0] * h):int(band[1] * h), :].mean(0)
    x0, x1 = longest(colp, thr)
    rowp = ink[:, int(0.3 * w):int(0.7 * w)].mean(1)
    y0, y1 = longest(rowp, thr)
    return x0 * ds, y0 * ds, x1 * ds, y1 * ds


def georef_from_frame(key, corners_px, lonlat_box, src_crs="EPSG:4162", model="affine", extra_info=None, save=True, tag=None):
    """도곽 4 모서리(TL,TR,BR,BL 원본 픽셀)와 경위도 상자(lon0,lon1,lat0,lat1) -> 5187 아핀. 저장 및 H 반환."""
    from pyproj import Transformer
    lon0, lon1, lat0, lat1 = lonlat_box
    t = Transformer.from_crs(src_crs, "EPSG:5187", always_xy=True)
    geo = np.array([t.transform(lon0, lat1), t.transform(lon1, lat1), t.transform(lon1, lat0), t.transform(lon0, lat0)])
    px = np.asarray(corners_px, float)
    H, rms, r = corners_to_H(px, geo, model)
    info = dict(kind="map", source=SRC[key], model=f"neatline corners ({src_crs} lon/lat -> 5187) {model}", rms_m=rms,
                gsd_eff=float(np.sqrt(abs(np.linalg.det(H[:2, :2])))), corner_px=px.tolist(), lonlat_box=list(lonlat_box), src_crs=src_crs)
    if extra_info:
        info.update(extra_info)
    a_shape = None
    if save:
        # 이미지 크기는 호출측에서 extra_info로 주지 않으면 SRC 로 읽는다
        if "size_px" not in info:
            from PIL import Image as _I
            if SRC[key].lower().endswith((".jpg", ".jpeg")):
                w, h = _I.open(SRC[key]).size
            else:
                import tifffile as _tf
                with _tf.TiffFile(SRC[key]) as tf:
                    h, w = tf.pages[0].shape[:2]
            info["size_px"] = [w, h]
        save_transform(tag or key, H, info)
    return H, rms, r


def content_quad(img, open_k=21, white_thr=238, ds=2, verbose=False):
    """칼라/흑백 지도 스캔에서 지도면(내용) 사각형의 네 변을 추정해 모서리(TL,TR,BR,BL, 원본 픽셀)를 반환.
    아이디어: 흰 여백이 아닌 화소 -> 큰 구조 요소 열림(얇은 선·글자·액자 제거) -> 최대 연결 성분 -> 각 행/열의 양 끝 위치에 직선 적합."""
    g = img if img.ndim == 2 else img.min(axis=2)
    g = cv2.resize(g, (g.shape[1] // ds, g.shape[0] // ds), interpolation=cv2.INTER_AREA)
    m = (g < white_thr).astype(np.uint8)
    k = max(3, open_k // ds)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((k, k), np.uint8))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(m, 8)
    if n < 2:
        return None
    # 가장 큰 성분(가로·세로 모두 큰 것)
    best = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    comp = (lab == best)
    ys, xs = np.nonzero(comp)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    H, W = comp.shape
    # 각 행: 좌/우 끝
    rows = np.arange(int(y0 + 0.08 * (y1 - y0)), int(y1 - 0.08 * (y1 - y0)))
    L = []; R = []
    for r in rows:
        idx = np.flatnonzero(comp[r])
        if len(idx):
            L.append((idx[0], r)); R.append((idx[-1], r))
    cols = np.arange(int(x0 + 0.08 * (x1 - x0)), int(x1 - 0.08 * (x1 - x0)))
    T = []; B = []
    for c in cols:
        idx = np.flatnonzero(comp[:, c])
        if len(idx):
            T.append((c, idx[0])); B.append((c, idx[-1]))
    def fit(pts):
        pts = np.array(pts, np.float32)
        vx, vy, cx, cy = cv2.fitLine(pts, cv2.DIST_HUBER, 0, 0.01, 0.01).ravel()
        c = np.array([cx, cy]); u = np.array([vx, vy]); nn = np.array([-u[1], u[0]])
        res = (pts - c) @ nn
        keep = np.abs(res) < max(1.5, 2.5 * np.median(np.abs(res)))
        vx, vy, cx, cy = cv2.fitLine(pts[keep], cv2.DIST_L2, 0, 0.01, 0.01).ravel()
        return (np.array([cx, cy]), np.array([vx, vy]))
    lT, lB, lL, lR = fit(T), fit(B), fit(L), fit(R)
    TL, TR, BR, BL = intersect(lT, lL), intersect(lT, lR), intersect(lB, lR), intersect(lB, lL)
    q = np.array([TL, TR, BR, BL]) * ds + (ds - 1) / 2.0 + 0.5 * ds   # 마스크 가장자리(바깥 경계)->화소 중심 보정은 아래에서 반 화소 이동
    # 화소 경계(바깥)이므로 안쪽 화소 중심 기준으로는 0.5*ds 만큼 안쪽 -> 선의 정확한 위치는 +-1px 수준
    if verbose:
        print("content quad:", q.round(1).tolist())
    return q
