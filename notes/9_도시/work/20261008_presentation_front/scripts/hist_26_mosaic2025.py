# -*- coding: utf-8 -*-
"""2025 항공사진 3장(62/64/65) 모자이크(aerial_2025_*) + 정사영상 빈 곳 채움(ortho_2025_*_filled)"""
import sys
sys.path.insert(0, "C:/Users/OFFICE/Desktop/9_도시/work/20261008_presentation_front/scripts")
from histlib import *
frames_keys = ["a2025_62", "a2025_64", "a2025_65"]
cache = {k: load_full(k) for k in frames_keys}
Ho, _ = load_transform("o2025")
ao = load_full("o2025")
cov_out = {}
for fr in ["F1", "F2"]:
    f = FRAMES[fr]; O2G, s = frame_out2geo(fr)
    imgs = []; masks = []; ctrs = []
    for k in frames_keys:
        H, info = load_transform(k)
        gsd = float(np.sqrt(abs(np.linalg.det(H[:2, :2]))))
        p = pick_prescale(gsd, fr)
        src = prescale(cache[k], p)
        out, m = warp_to_frame(src, H, fr, gsd, prescaled=p)
        imgs.append(out.astype(np.float32)); masks.append(m)
        w, h = info["size_px"]
        c = apply_H(H, [[w / 2, h / 2]])[0] + np.array([CX, CY])
        ctrs.append(c)
    # 출력 틀 픽셀의 geo 좌표
    vv, uu = np.mgrid[0:f["h"], 0:f["w"]]
    gx = f["x0"] + (uu + 0.5) * s; gy = f["y1"] - (vv + 0.5) * s
    # 천저(중심) 근접 보로노이 + 가장자리 거리 가중
    dist_c = np.stack([np.hypot(gx - c[0], gy - c[1]) for c in ctrs])
    wts = []
    feather = 14
    for i, m in enumerate(masks):
        dt = cv2.distanceTransform(m.astype(np.uint8), cv2.DIST_L2, 3)
        wi = np.clip(dt / feather, 0, 1)
        wts.append(wi)
    # 각 픽셀: 유효한 프레임 중 중심에 가장 가까운 프레임을 우선 -> soft 선택
    big = 1e9
    dcm = np.where(np.stack(masks), dist_c, big)
    best = np.argmin(dcm, axis=0)
    # 경계 부드럽게: 최단 거리와 2위 거리 차이가 작으면 혼합
    sorted_d = np.sort(dcm, axis=0)
    gap = (sorted_d[1] - sorted_d[0])
    alpha_blend = np.clip(gap / (feather * s * 2.0), 0, 1)   # 0: 경계(혼합), 1: 단독
    acc = np.zeros((f["h"], f["w"], 3), np.float32); wsum = np.zeros((f["h"], f["w"]), np.float32)
    order = np.argsort(dcm, axis=0)
    first = order[0]; second = order[1]
    anym = np.any(np.stack(masks), axis=0)
    mosaic = np.zeros((f["h"], f["w"], 3), np.float32)
    for i in range(len(imgs)):
        w1 = np.where(first == i, 1.0, 0.0) * alpha_blend[..., None].squeeze() if False else None
    # 단순 구현: 1위 프레임 이미지와 2위 프레임 이미지를 혼합
    img_stack = np.stack(imgs)   # (n,h,w,3)
    hh, ww = f["h"], f["w"]
    idx1 = first; idx2 = second
    I1 = np.take_along_axis(img_stack, idx1[None, ..., None].repeat(3, -1), axis=0)[0]
    I2 = np.take_along_axis(img_stack, idx2[None, ..., None].repeat(3, -1), axis=0)[0]
    valid2 = sorted_d[1] < big / 2
    a_ = np.where(valid2, 0.5 + 0.5 * alpha_blend, 1.0)[..., None]   # 1위 가중 0.5~1
    mosaic = I1 * a_ + I2 * (1 - a_)
    mosaic = np.clip(mosaic, 0, 255).astype(np.uint8)
    mmask = anym
    # 정사영상 렌더
    p = pick_prescale(0.25, fr)
    oimg, omask = warp_to_frame(prescale(ao, p), Ho, fr, 0.25, prescaled=p)
    # 색 보정: 겹치는 영역에서 채널별 이득/오프셋(중앙값 기반)
    ov = omask & mmask
    adj = mosaic.astype(np.float32)
    if ov.sum() > 5000:
        for c in range(3):
            x = cv2.GaussianBlur(mosaic[..., c].astype(np.float32), (0, 0), 3)[ov]
            y = cv2.GaussianBlur(oimg[..., c].astype(np.float32), (0, 0), 3)[ov]
            gain = (np.percentile(y, 90) - np.percentile(y, 10)) / max(1.0, (np.percentile(x, 90) - np.percentile(x, 10)))
            off = np.median(y) - gain * np.median(x)
            adj[..., c] = adj[..., c] * gain + off
            print(fr, "channel", c, "gain", round(float(gain), 3), "offset", round(float(off), 1))
    adj = np.clip(adj, 0, 255).astype(np.uint8)
    # (1) 항공사진 모자이크 단독
    save_jpg(HIST + f"aerial_2025_{fr}.jpg", fill_nodata(mosaic, mmask))
    # (2) 정사영상 + 채움: 정사영상 우선, 빈 곳은 보정한 모자이크, 경계 12px 페더
    dt = cv2.distanceTransform(omask.astype(np.uint8), cv2.DIST_L2, 3)
    wo = np.clip(dt / 12.0, 0, 1)[..., None]
    filled = np.where(omask[..., None], oimg.astype(np.float32) * wo + adj.astype(np.float32) * (1 - wo) * mmask[..., None] + oimg.astype(np.float32) * (1 - wo) * (~mmask[..., None]), adj.astype(np.float32))
    fmask = omask | mmask
    filled = np.clip(filled, 0, 255).astype(np.uint8)
    save_jpg(HIST + f"ortho_2025_{fr}_filled.jpg", fill_nodata(filled, fmask))
    cov_out[fr] = dict(mosaic=float(mmask.mean()), ortho=float(omask.mean()), filled=float(fmask.mean()))
    print(fr, cov_out[fr])
json.dump(cov_out, open(SCR + "cov_2025.json", "w"))
