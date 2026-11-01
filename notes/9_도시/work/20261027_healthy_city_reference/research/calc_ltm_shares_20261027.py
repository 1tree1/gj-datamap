# -*- coding: utf-8 -*-
"""
생활(L)·관광(T)·혼합(M)·업무(B) 업종 분류표 v0 적용 — 횡단면 예시 산정 (2026-10-27)
입력: archive/C_data/processed/stores_merged_4326.geojson (소진공 상가(상권)정보 2026-03 스냅샷 + 경주시 게스트하우스 현황, 저장소 C-006 계열)
S2: 고시 구역 중심(EPSG:5187 219776.9, 360961.0, calc_fabric_metrics_20261024.py ZONE_C) 반경 1 km
실행: python -I calc_ltm_shares_20261027.py <stores_merged_4326.geojson 경로>
주의: 분류표 v0는 [판단]이며 사용자 확정 전. 파일 범위는 경주시 전역이 아니므로 '파일 범위' 값을 시 기준선으로 쓰지 않는다.
"""
import json, sys, collections
import pyproj

# 중분류 단위 분류 (상가(상권)정보 표준산업분류 10차 기반 중분류명)
L = {'식료품 소매', '종합 소매', '이용·미용', '세탁', '욕탕·신체관리', '가전·통신 소매', '철물·건설자재 소매',
     '기타 생활용품 소매', '안경·정밀기기 소매', '가구 소매', '연료 소매', '애완동물·용품 소매', '의원', '병원',
     '기타 보건', '수의', '일반 교육', '교육 지원', '기타 교육', '부동산 서비스', '가전제품 수리', '컴퓨터 수리',
     '기타 가정용품 수리', '자동차 수리·세차', '통신장비 수리', '모터사이클 수리', '자동차 부품 소매', '모터사이클 소매',
     '구내식당·뷔페', '담배 소매', '장례식장', '스포츠 서비스', '회계·세무', '법무관련', '중고 상품 소매'}
T = {'일반 숙박', '게스트하우스', '기타 숙박', '여행사·보조', '사진 촬영'}
M = {'한식', '기타 간이', '비알코올', '주점', '서양식', '일식', '중식', '동남아시아', '섬유·의복·신발 소매',
     '시계·귀금속 소매', '오락용품 소매', '식물 소매', '기타 상품 소매', '음료 소매', '의약·화장품 소매',
     '도서관·사적지', '기타 개인'}
# 소분류 우선 규칙 (중분류가 섞여 있는 경우)
SOV = {'약국': 'L', '의료기기 소매업': 'L', '화장품 소매업': 'M', '노래방': 'M', 'PC방': 'M', '복권 발행/판매업': 'L',
       '비디오방': 'M', '바둑/장기/체스 경기 운영업': 'L', '전자 게임장': 'M', '기타 오락장': 'T',
       '기타 오락관련 서비스업': 'T', '의류 대여업': 'T', '기념품점': 'T', '예술품 소매업': 'M', '만화방': 'M'}


def cls(mcls, scls=None):
    if scls in SOV:
        return SOV[scls]
    m = (mcls or '').strip()
    if m in L: return 'L'
    if m in T: return 'T'
    if m in M: return 'M'
    return 'B'  # 생산자 서비스·임대 등: R3 분모에서 제외


def main(path):
    tr = pyproj.Transformer.from_crs(4326, 5187, always_xy=True)
    g = json.load(open(path, encoding='utf-8'))
    cx, cy = 219776.9, 360961.0
    res = {'S2(반경 1 km)': collections.Counter(), '황남동(법정동)': collections.Counter(),
           '파일 범위 전체(시 기준선 아님)': collections.Counter()}
    for f in g['features']:
        p = f['properties']
        c = cls(p.get('indsMclsNm'), p.get('indsSclsNm'))
        x, y = f['geometry']['coordinates'][:2]
        X, Y = tr.transform(x, y)
        res['파일 범위 전체(시 기준선 아님)'][c] += 1
        if (X - cx) ** 2 + (Y - cy) ** 2 <= 1000 ** 2:
            res['S2(반경 1 km)'][c] += 1
        if p.get('ldongNm') == '황남동':
            res['황남동(법정동)'][c] += 1
    out = []
    for k, v in res.items():
        n = sum(v.values()); nlm = v['L'] + v['T'] + v['M']
        out.append(f"{k}: n={n} L={v['L']} T={v['T']} M={v['M']} B={v['B']} | "
                   f"R3=L/(L+T+M)={v['L']/nlm:.3f} | T/(L+T)={v['T']/(v['L']+v['T']):.3f}")
    sys.stdout.buffer.write(('\n'.join(out) + '\n').encode('utf-8'))


if __name__ == '__main__':
    main(sys.argv[1])
