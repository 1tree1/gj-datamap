# 대구광역시 도시 데이터 기반 재개발 전략 가이드

## Data-Driven Redevelopment Strategy for Daegu Metropolitan City

---

## PART 0. 대구, 왜 지금 재개발인가?

### 대구의 5대 도시 위기

대구는 현재 한국 광역시 중에서도 가장 복합적인 도시 위기에 직면해 있다. 이 위기는 단순한 노후화가 아니라 인구·기후·경제·공간이 동시에 붕괴하는 **시스템적 쇠퇴(Systemic Decline)**이다.

**① 인구 붕괴** — 2024년 인구 236.9만 명, 5년간 6.1만 명(-2.5%) 감소. 연평균 약 1만 명씩 줄어 2044년 200만 명 이하 전망. 인구소멸위험지수 0.52로 '소멸주의' 단계 진입. 20대 순유출 6,300명(특·광역시 중 최대). 전출 사유: 직업 41.4% → 일자리 문제가 핵심.

**② 초고령화** — 2024년 노인인구 비중 20.9%로 초고령사회 진입. 노령화지수 197.5 (어린이 100명당 노인 197명). 중위연령 47.8세(전국 46.2세보다 높음). 2052년 고령인구 42.5% 전망, 생산연령인구 46.9% 감소 예상.

**③ 극한 폭염 도시 — "대프리카"** — 분지 지형(팔공산-비슬산-앞산)으로 열기 가둠 현상 극심. 1942년 40.0℃ 기록(76년간 한반도 최고). 도심 중심부에 열원 집중 + 콘크리트 건물 밀집 → 열섬효과 극대화. 주요 바람길(팔공산, 가창골, 앞산, 금호강변, 낙동강변) 대부분 아파트 숲으로 차단. 21세기 후반 현재 기온 대비 +4.7℃, 열대야 연 60.5일 예상.

**④ 경제 기반 약화** — 전통 섬유·기계산업 쇠퇴, 새로운 산업기반 미형성. GRDP 성장률 전국 하위권. 20대 유출의 핵심 원인이 '직업(41.4%)'인 악순환 구조.

**⑤ 도시 공간 노후화** — 원도심(중구·서구·남구·동구) 건물 노후화 심각. 기반시설 노후 + 도시공간 비효율 + 보행환경 열악이 복합적으로 작용.

### 재개발의 방향: "축소하되 농축하는 도시"

대구의 재개발은 단순히 낡은 건물을 새로 짓는 것이 아니다. 인구가 줄어드는 도시에서 필요한 것은 **스마트 축소(Smart Shrinkage)** — 줄어드는 만큼 더 촘촘하고 쾌적하며 회복력 있는 도시를 만드는 것이다. 이하 이 전략을 데이터 기반으로 수립하기 위한 전 과정을 정리한다.

---

## PART 1. 어디서 무엇을 모을 것인가 — 데이터 소스 & 수집 전략

대구 재개발을 위한 데이터를 10대 카테고리별로 **어디서(Source)**, **무엇을(Dataset)**, **어떤 형식(Format)**으로 수집할 수 있는지 정리한다.

### 1-1. 자연환경 (Natural Environment)

| 데이터 | 소스 | URL | 형식 |
|--------|------|-----|------|
| DEM 수치표고모델 (1m/5m) | 국토지리정보원 | ngii.go.kr | GeoTIFF |
| 경사도·향 분석 | 국토정보플랫폼 | map.ngii.go.kr | SHP/GeoTIFF |
| 지질도 (1:50,000) | 한국지질자원연구원 KIGAM | mgeo.kigam.re.kr | SHP/PDF |
| 기상관측 (기온/강수/풍향/풍속/일사량) | 기상자료개방포털 | data.kma.go.kr | CSV/API |
| 대구 AWS 미기후 관측 | 기상청 | data.kma.go.kr | CSV |
| 위성 LST 지표면온도 | NASA MODIS/Landsat | earthdata.nasa.gov / USGS EarthExplorer | GeoTIFF |
| NDVI 식생지수 | Sentinel-2 / Landsat | Copernicus Hub / GEE | GeoTIFF |
| 대기질 (PM2.5/PM10/O₃/NO₂) | 에어코리아 + 대구 대기측정망 | airkorea.or.kr / data.go.kr | CSV/API |
| 수계·유역 | 국가수자원관리종합정보 | wamis.go.kr | SHP |
| 홍수위험지도 | 국토교통부 홍수지도정보 | floodmap.go.kr | SHP/PDF |
| 생태자연도 | 환경부 환경공간정보 | egis.me.go.kr | SHP |
| 토양도 | 국립농업과학원 흙토람 | soil.rda.go.kr | SHP |

**핵심 수집 포인트**: 대구의 **분지 지형 + 바람길** 데이터가 가장 중요. DEM으로 분지 구조 분석 → 풍향·풍속 데이터로 바람길 매핑 → LST(지표면온도)로 열섬 취약지 식별. 이 3개가 대구 재개발의 기후 전략 핵심.

### 1-2. 인구·사회 (Demographics & Social)

| 데이터 | 소스 | URL | 형식 |
|--------|------|-----|------|
| 주민등록인구 (읍면동별 연령/성별) | 행정안전부 주민등록인구통계 | jumin.mois.go.kr | CSV |
| 인구주택총조사 (가구구성/주거형태) | 통계청 KOSIS | kosis.kr | CSV/API |
| 인구이동통계 (전입·전출 OD) | 통계청 KOSIS | kosis.kr | CSV |
| 장래인구추계 (시도편) | 통계청 | kosis.kr | CSV |
| 생활인구 (유동인구) | KT 빅데이터 / SKT 지오비전 | bigdata.kt.com | CSV (유료) |
| 소득·소비 | 국세청 / 신용카드 빅데이터 | data.go.kr | CSV |
| 1인가구·독거노인 | 통계청 인구총조사 | kosis.kr | CSV |
| 대구통계 종합 | 대구통계포털 | stat.daegu.go.kr | CSV/PDF |
| 대구정책연구원 보고서 | 대구정책연구원 DPI | dpi.re.kr | PDF |

**핵심 수집 포인트**: 읍면동 단위 **연령별 인구피라미드** + **전입·전출 OD 매트릭스** + **1인가구 비율** + **독거노인 분포**. 이 4개가 재개발 우선순위 결정의 인구학적 근거.

### 1-3. 경제·산업 (Economy & Industry)

| 데이터 | 소스 | URL | 형식 |
|--------|------|-----|------|
| 사업체조사 (산업별/종사자규모별) | 통계청 KOSIS | kosis.kr | CSV |
| GRDP (지역내총생산) | 통계청 | kosis.kr | CSV |
| 상가 업종 데이터 | 소상공인시장진흥공단 상권정보 | sg.sbiz.or.kr | CSV/SHP |
| 공시지가 | 국토교통부 부동산공시가격 | realtyprice.kr | CSV/API |
| 실거래가 (아파트/주택) | 국토교통부 실거래가 공개시스템 | rt.molit.go.kr | CSV/API |
| 전통시장 현황 | 소상공인시장진흥공단 | semas.or.kr | CSV |
| 산업단지 현황 | 한국산업단지공단 | kicox.or.kr | CSV/SHP |

**핵심 수집 포인트**: **상권 업종별 개폐업률** + **공시지가 변화 추이** + **사업체 밀도** 3개로 경제활력도 매핑. 특히 대구 원도심의 폐업률과 공실률이 재개발 시급성의 경제적 근거.

### 1-4. 토지이용·공간 (Land Use & Spatial)

| 데이터 | 소스 | URL | 형식 |
|--------|------|-----|------|
| 용도지역지구 | 토지이용규제정보서비스 | luris.molit.go.kr | SHP/API |
| 지적도 (필지 경계) | 국가공간정보포털 V-World | vworld.kr | SHP/API |
| 건축물대장 (용도/연면적/층수/준공연도) | 세움터 / 공공데이터포털 | open.eais.go.kr / data.go.kr | CSV/API |
| 토지피복지도 | 환경부 환경공간정보 | egis.me.go.kr | SHP |
| 위성영상 (고해상도) | 아리랑위성 / Sentinel-2 | arirang.kari.re.kr | GeoTIFF |
| 항공사진·정사영상 | 국토지리정보원 | map.ngii.go.kr | JPEG/TIFF |
| 3D 건물모델 | V-World 3D | vworld.kr | 3DS/OBJ |
| 대구 도시계획 (용도지역 결정도) | 대구지도포털 | gis.go.kr (대구) | SHP/WMS |

**핵심 수집 포인트**: **건축물대장의 준공연도**가 재개발의 핵심 데이터. 준공 30년 이상 건물 비율로 노후도 맵 생성 → 용도지역과 교차분석하여 재개발 가능구역 식별.

### 1-5. 교통·모빌리티 (Transportation & Mobility)

| 데이터 | 소스 | URL | 형식 |
|--------|------|-----|------|
| 교통카드 OD (대중교통 승하차) | TAGO 국가대중교통정보센터 | tago.go.kr | CSV/API |
| 대구 버스 노선·정류장·실시간위치 | 대구버스정보시스템 | businfo.daegu.go.kr / data.go.kr API | JSON/API |
| 대구 도시철도 (1·2·3호선) | 대구교통공사 | dtro.or.kr | CSV |
| 도로 네트워크 | V-World 도로중심선 | vworld.kr | SHP |
| 교통량 조사 | 국토교통부 도로교통량 | roadtraf.ex.co.kr | CSV |
| 주차장 정보 | 공공데이터포털 | data.go.kr | CSV/API |
| 자전거도로 현황 | 대구시 | data.daegu.go.kr | SHP/CSV |
| 보행자 도로 현황 | V-World | vworld.kr | SHP |

**핵심 수집 포인트**: **대중교통 승하차 OD** + **도시철도역 위치** + **도로네트워크**로 접근성 분석. 역세권(500m) 재개발이 대구에서 가장 효과적인 전략이므로 도시철도 역 중심 Isochrone 분석이 핵심.

### 1-6. 인프라·유틸리티 (Infrastructure & Utilities)

| 데이터 | 소스 | URL | 형식 |
|--------|------|-----|------|
| 상수도 관로 현황 | 대구상수도사업본부 | data.go.kr API | JSON |
| 하수도 관로·처리 | 대구시 하수도과 | data.daegu.go.kr | CSV |
| 전력 사용량 (읍면동별) | 한국전력 전력데이터개방 | bigdata.kepco.co.kr | CSV |
| 가스 공급 | 대구도시가스 | data.go.kr | CSV |
| 통신 기지국 | 과학기술정보통신부 | data.go.kr | CSV |

### 1-7. 공공시설·서비스 (Public Facilities & Services)

| 데이터 | 소스 | URL | 형식 |
|--------|------|-----|------|
| 학교 (유·초·중·고) | 학교알리미 | schoolinfo.go.kr | CSV |
| 의료기관 | 건강보험심사평가원 | hira.or.kr | CSV |
| 소방서·안전센터 | 소방청 | data.go.kr | CSV |
| 경찰서·지구대 | 경찰청 | data.go.kr | CSV |
| 공원·녹지 | 대구시 / 국가공간정보 | data.daegu.go.kr | SHP/CSV |
| 복지시설 (노인·장애인·아동) | 사회서비스 전자바우처 / 복지로 | bokjiro.go.kr | CSV |
| 무더위쉼터 | 대구시 | data.daegu.go.kr | CSV |
| 도서관·문화시설 | 대구시 | data.daegu.go.kr | CSV |

### 1-8. 도시설계·경관 (Urban Design & Landscape)

| 데이터 | 소스 | URL | 형식 |
|--------|------|-----|------|
| Street View 이미지 | Kakao/Naver/Google Street View | API | JPEG |
| 건물 높이·스카이라인 | 건축물대장 + 3D 모델 | data.go.kr + vworld.kr | CSV/3D |
| 녹지율·녹시율 | Sentinel-2 NDVI + Street View AI | GEE + API | GeoTIFF/CSV |
| 보행환경 (보도폭/가로수) | 대구시 | 현장조사 필요 | 수동수집 |
| CCTV 위치 | 대구시 | data.daegu.go.kr | CSV |

### 1-9. 법·제도·계획 (Legal & Planning)

| 데이터 | 소스 | URL | 형식 |
|--------|------|-----|------|
| 2025 대구 도시재생전략계획 | 대구 창의도시재생지원센터 | dgucenter.or.kr | PDF |
| 대구 도시기본계획 (2035) | 대구시 도시주택건설국 | daegu.go.kr/build | PDF |
| 도시주거환경정비 기본계획 | 대구시 | daegu.go.kr | PDF |
| 도시재생활성화지역 현황 | 대구시 | daegu.go.kr/build | PDF/SHP |
| 경관계획 | 대구시 도시디자인과 | daegu.go.kr | PDF |
| 기후변화 적응대책 | 대구시 | daegu.go.kr | PDF |

### 1-10. 디지털·스마트시티 (Digital & Smart City)

| 데이터 | 소스 | URL | 형식 |
|--------|------|-----|------|
| D-데이터허브 (대구 종합) | 대구시 | data.daegu.go.kr | 다양 |
| 대구빅데이터활용센터 | 대구디지털산업진흥원 | bigdata.dip.or.kr | 다양 |
| 공공데이터포털 (대구 필터) | 행정안전부 | data.go.kr (대구 검색) | CSV/API |
| 대구지도포털 (GIS) | 대구시 | gis.go.kr | WMS/SHP |
| 대구통계 | 대구시 | stat.daegu.go.kr | CSV/PDF |

---

## PART 2. 어떻게 전처리할 것인가 — 데이터 파이프라인

### 2-1. 전체 파이프라인 아키텍처

```
[Raw Data Sources]
     │
     ├── CSV/Excel  ──→  pandas read_csv/read_excel
     ├── SHP/GeoJSON ──→ geopandas read_file
     ├── GeoTIFF ──────→ rasterio open
     ├── API (JSON) ───→ requests + json_normalize
     ├── PDF 보고서 ───→ PyMuPDF/pdfplumber 텍스트 추출
     └── 위성영상 ─────→ Google Earth Engine (GEE) Python API
             │
             ▼
     [Staging Layer - 원본 보존]
     /data/raw/daegu/{category}/{source}/{date}/
             │
             ▼
     [Cleaning & Standardization]
     ├── 좌표계 통일: EPSG:5186 (Korean 2000 Central Belt) or EPSG:4326
     ├── 행정코드 통일: 법정동코드 10자리 → 읍면동 매핑 테이블
     ├── 시간 통일: KST → UTC, 연도/월 기준 정렬
     ├── 결측치 처리: 보간법/최근접 대체/삭제
     ├── 이상치 탐지: IQR/Z-score/LOF
     └── 형식 통일: Parquet(정형) / GeoParquet(공간) / Cloud Optimized GeoTIFF(래스터)
             │
             ▼
     [Feature Engineering Layer]
     ├── 공간 집계: H3 hexagonal grid (resolution 8~9, ~460m~174m)
     ├── 지표 산출: 노후도 지수, 접근성 지수, 열취약성 지수 등
     ├── 시계열: 인구변화율, 지가변화율, 업종 개폐업률 등
     └── 정규화: Min-Max or Z-score (지표 간 비교용)
             │
             ▼
     [Analysis-Ready Dataset]
     /data/processed/daegu/
     ├── daegu_hex_grid.geoparquet     ← H3 격자별 통합 데이터
     ├── daegu_buildings.geoparquet    ← 건물별 속성 (노후도/용도/면적)
     ├── daegu_population.parquet      ← 읍면동별 인구 시계열
     ├── daegu_thermal.tif             ← 열환경 래스터
     └── daegu_accessibility.geoparquet ← 접근성 분석 결과
             │
             ▼
     [Visualization & Modeling]
     ├── Kepler.gl / Deck.gl (웹 인터랙티브 맵)
     ├── QGIS / ArcGIS (GIS 분석·출력)
     ├── Grasshopper + Ladybug (파라메트릭 환경 시뮬레이션)
     ├── Rhino + CityEngine (3D 도시모델)
     ├── Unity (XR 시각화)
     ├── PyTorch (예측 모델)
     └── Plotly / D3.js (대시보드)
```

### 2-2. Python 전처리 코드 예시 — 핵심 3개

#### (A) 건축물대장 → 노후도 맵

```python
import pandas as pd
import geopandas as gpd
from datetime import datetime

# 1. 건축물대장 로드 (공공데이터포털 API or CSV)
buildings = pd.read_csv("daegu_buildings.csv", encoding="cp949")

# 2. 준공연도 추출 & 노후도 계산
buildings["사용승인일자"] = pd.to_datetime(buildings["사용승인일자"], format="%Y%m%d", errors="coerce")
buildings["건물연령"] = (datetime.now() - buildings["사용승인일자"]).dt.days / 365.25
buildings["노후등급"] = pd.cut(
    buildings["건물연령"],
    bins=[0, 15, 20, 30, 40, 200],
    labels=["양호", "보통", "노후", "심각", "재건축대상"]
)

# 3. 지적도(필지) 공간 조인
parcels = gpd.read_file("daegu_parcels.shp")  # EPSG:5186
parcels = parcels.to_crs(epsg=4326)
# PNU(필지고유번호) 기준 조인
merged = parcels.merge(buildings, left_on="PNU", right_on="대지위치PNU", how="left")

# 4. 읍면동별 노후도 집계
aging_stats = merged.groupby("읍면동코드").agg(
    avg_age=("건물연령", "mean"),
    pct_over_30=("건물연령", lambda x: (x > 30).sum() / len(x) * 100),
    total_buildings=("건물연령", "count")
).reset_index()

# 5. 저장
merged.to_file("daegu_building_age.gpkg", driver="GPKG")
aging_stats.to_parquet("daegu_aging_by_dong.parquet")
```

#### (B) 열환경 분석 — Landsat LST + 바람길

```python
import rasterio
import numpy as np
from rasterio.warp import reproject, Resampling

# 1. Landsat 8/9 열적외선(Band 10) → LST 변환
with rasterio.open("LC09_B10_daegu_summer.tif") as src:
    thermal = src.read(1).astype(float)
    # DN → Radiance → Brightness Temperature (K) → ℃
    radiance = thermal * 0.0003342 + 0.1  # 스케일링 계수
    K1, K2 = 774.8853, 1321.0789  # Landsat 9 상수
    bt_kelvin = K2 / np.log((K1 / radiance) + 1)
    lst_celsius = bt_kelvin - 273.15

# 2. NDVI (Band 4 Red, Band 5 NIR)
with rasterio.open("LC09_B4_daegu.tif") as red_src:
    red = red_src.read(1).astype(float)
with rasterio.open("LC09_B5_daegu.tif") as nir_src:
    nir = nir_src.read(1).astype(float)
ndvi = (nir - red) / (nir + red + 1e-10)

# 3. LST 보정 (Emissivity correction using NDVI)
emissivity = np.where(ndvi < 0.2, 0.97,
             np.where(ndvi > 0.5, 0.99,
             0.004 * ((ndvi - 0.2) / 0.3)**2 + 0.986))
lst_corrected = lst_celsius / emissivity

# 4. 열섬강도(UHI Intensity) = 도심 LST - 교외 평균 LST
rural_mask = ndvi > 0.6  # 산림지역 마스크
rural_mean = np.nanmean(lst_corrected[rural_mask])
uhi_intensity = lst_corrected - rural_mean

# 5. GeoTIFF 저장
profile = src.profile.copy()
profile.update(dtype="float32", count=1)
with rasterio.open("daegu_uhi_intensity.tif", "w", **profile) as dst:
    dst.write(uhi_intensity.astype("float32"), 1)
```

#### (C) 접근성 분석 — Isochrone (도보 15분)

```python
import osmnx as ox
import networkx as nx
import geopandas as gpd
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union

# 1. 대구 도로 네트워크 다운로드 (보행자)
G = ox.graph_from_place("대구광역시, South Korea", network_type="walk")

# 2. 도시철도역 좌표 (예: 1호선 주요역)
stations = {
    "반월당": (35.8583, 128.5933),
    "중앙로": (35.8681, 128.5946),
    "동대구역": (35.8793, 128.6281),
    # ... 전체 역 좌표
}

# 3. 각 역에서 도보 15분(900초) Isochrone 생성
walk_speed = 4.5  # km/h (보행 속도)
isochrones = []

for name, (lat, lon) in stations.items():
    center_node = ox.nearest_nodes(G, lon, lat)
    # 15분(=1.125km) 내 도달 가능 노드
    subgraph = nx.ego_graph(G, center_node,
                            radius=900,  # 초
                            distance="travel_time")
    node_points = [Point(data["x"], data["y"])
                   for node, data in subgraph.nodes(data=True)]
    bounding_poly = unary_union(node_points).convex_hull
    isochrones.append({"station": name, "geometry": bounding_poly,
                        "walk_minutes": 15})

iso_gdf = gpd.GeoDataFrame(isochrones, crs="EPSG:4326")
iso_gdf.to_file("daegu_station_isochrone_15min.gpkg", driver="GPKG")

# 4. 접근성 사각지대 = 대구시 경계 - 모든 Isochrone 합집합
daegu_boundary = ox.geocode_to_gdf("대구광역시, South Korea")
all_covered = unary_union(iso_gdf.geometry)
blind_spots = daegu_boundary.geometry.iloc[0].difference(all_covered)
```

### 2-3. 통합 데이터셋 구축 — H3 헥사그리드 방식

모든 데이터를 하나의 분석 단위로 통합하기 위해 **H3 Hexagonal Grid**를 사용한다. 읍면동 경계는 행정 목적이라 크기와 형태가 불규칙하지만, H3 헥사곤은 균일한 면적으로 공정한 비교가 가능하다.

```python
import h3
import pandas as pd
import geopandas as gpd

# Resolution 8 ≈ 약 460m 변 길이, 0.74 km² 면적 → 도시 분석 적정 스케일
RESOLUTION = 8

# 대구 범위의 모든 H3 셀 생성
daegu_h3_cells = h3.polyfill_geojson(
    daegu_boundary.__geo_interface__["features"][0]["geometry"],
    res=RESOLUTION
)

# 각 H3 셀에 데이터 집계
hex_data = []
for cell in daegu_h3_cells:
    lat, lon = h3.h3_to_geo(cell)
    hex_data.append({
        "h3_id": cell,
        "lat": lat, "lon": lon,
        # 인구 (공간 조인으로 할당)
        # 건물 노후도 (해당 셀 내 건물 평균 연령)
        # LST (래스터 zonal statistics)
        # 대중교통 접근성 (최근접 역까지 거리)
        # 공시지가 평균
        # 공원 접근성 (최근접 공원까지 거리)
        # ...
    })
```

---

## PART 3. 어떻게 시각화할 것인가 — 7대 분석 맵

수집·전처리한 데이터를 7개의 핵심 분석 맵으로 시각화한다. 각 맵은 재개발 의사결정의 하나의 '레이어'이며, McHarg의 레이어 오버레이(Overlay) 방식으로 최종 통합한다.

### MAP 1. 건물 노후도 맵 (Building Age Heatmap)

- **데이터**: 건축물대장 준공연도
- **시각화**: 건물 폴리곤을 연령별 색상 그라데이션 (초록→노랑→빨강)
- **기준**: 15년 미만 (양호) / 15-20년 (보통) / 20-30년 (노후) / 30-40년 (심각) / 40년+ (재건축대상)
- **도구**: QGIS Categorized Symbol / Kepler.gl GeoJSON Layer / Grasshopper + Hops
- **인사이트**: 중구·서구·남구 원도심에 30년+ 건물 밀집 → 재개발 물리적 근거

### MAP 2. 열환경 취약도 맵 (Thermal Vulnerability Map)

- **데이터**: Landsat LST + NDVI + DEM + 바람길 + 불투수면적률
- **시각화**: UHI 강도 래스터 오버레이 + 바람길 벡터 화살표
- **분석**: CFD 또는 Ladybug/Butterfly로 바람길 시뮬레이션
- **도구**: QGIS Raster Layer / Rhino+Grasshopper+Ladybug / ENVI-met
- **인사이트**: 도심 중심부(중구·동구 일부) UHI +3~5℃ → 바람길 차단 건물군 식별 → 재개발 시 바람길 확보 우선

### MAP 3. 인구 변화·고령화 맵 (Demographic Change Map)

- **데이터**: 읍면동별 인구 시계열 (5년간) + 연령별 분포 + 독거노인 비율
- **시각화**: 이중 코로플레스 (bivariate choropleth) — x축: 인구변화율, y축: 고령화율
- **도구**: Python (matplotlib/plotly) / Kepler.gl / QGIS
- **인사이트**: 인구 감소 + 고령화 동시 진행 지역 = 최우선 재개발 대상. 특히 서구·남구·중구 일부.

### MAP 4. 대중교통 접근성 맵 (Transit Accessibility Map)

- **데이터**: 도시철도 역 위치 + 버스정류장 + 도로네트워크
- **시각화**: Isochrone (도보 5분/10분/15분 등시선) + 접근성 사각지대 빨간색
- **분석**: Network Analysis (osmnx) — 보행자 기준 실제 도로 경유 거리
- **도구**: QGIS Network Analysis / Python osmnx / Grasshopper Shortest Walk
- **인사이트**: 도시철도 역세권(도보 10분, ~800m) 내 재개발이 가장 효과적. 접근성 사각지대에는 BRT/공유모빌리티 보완.

### MAP 5. 경제활력도 맵 (Economic Vitality Map)

- **데이터**: 상권 업종별 개폐업률 + 공시지가 변화 + 유동인구
- **시각화**: 버블맵 (공시지가 크기) + 코로플레스 (폐업률 색상)
- **도구**: Kepler.gl / Deck.gl / Python plotly
- **인사이트**: 원도심 상권 폐업률 높은 지역 vs 신시가지 활력 지역 대비 → 재개발을 통한 경제거점 재배치 근거

### MAP 6. 공공서비스 결핍도 맵 (Service Gap Map)

- **데이터**: 학교·병원·소방서·공원·복지시설 위치 + 서비스권역
- **시각화**: Service Area Buffer (초등학교 400m, 공원 300m, 의료 500m 등) → 미충족 지역 빨강
- **분석**: Location-Allocation Model (QGIS / Python PuLP)
- **도구**: QGIS Service Area / Grasshopper Isovists
- **인사이트**: 대구 원도심의 학교 학생 수 급감(폐교 위험) vs 노인복지시설 부족 → 시설 전환(학교→복합커뮤니티) 근거

### MAP 7. 통합 재개발 우선순위 맵 (Composite Priority Map)

위 6개 맵을 McHarg 방식으로 오버레이하여 최종 재개발 우선순위를 산출한다.

```
재개발 우선순위 점수 = 
    w₁ × 건물노후도(정규화) +
    w₂ × 열취약도(정규화) +
    w₃ × 인구감소율(정규화) +
    w₄ × 고령화율(정규화) +
    w₅ × 대중교통접근성(정규화, 역수) +
    w₆ × 경제쇠퇴도(정규화) +
    w₇ × 공공서비스결핍도(정규화)
```

**가중치 설정 방안**: AHP(Analytic Hierarchy Process) 또는 전문가 델파이 + 시민 참여 워크숍. 예시 가중치 — 건물노후도 0.20 / 열취약도 0.20 / 인구감소 0.15 / 고령화 0.10 / 접근성 0.15 / 경제쇠퇴 0.10 / 서비스결핍 0.10. 대구의 경우 열취약도 가중치를 높이는 것이 타 도시 대비 차별점.

---

## PART 4. 어떤 방향으로 재개발할 것인가 — 대구형 재개발 5대 전략

### 전략 1: "바람길 도시" — 기후적응형 도시구조 개편

**문제**: 분지 지형 + 바람길 차단 건물군 → 열섬효과 극대화

**데이터 근거**: LST 맵에서 도심 UHI +3~5℃ / 바람길 분석에서 4대 바람길(팔공산·가창골·앞산·금호강변) 대부분 아파트 밀집지로 차단

**전략**:
- 재개발 시 건물 배치를 **바람길 방향으로 정렬** (남-북 또는 금호강변에서 도심 방향)
- 건물 높이를 바람길 입구에서 점진적으로 높아지는 **스텝다운(Step-down) 스카이라인** 적용
- 바람길 축(금호강~도심) 따라 **녹색 회랑(Green Corridor)** 조성 — 최소 폭 100m
- D/H ratio (도로폭/건물높이) 규제: 바람길 축 도로에서 최소 1.5 이상 확보
- 옥상녹화 의무화 (연구: 대구 인동촌에서 옥상녹화 시 평균 0.9℃ 저감 효과)

**도구**: Rhino+Grasshopper+Ladybug(풍환경 시뮬레이션) → 건물 배치 대안 생성 → Butterfly(CFD)로 바람길 효과 검증 → Honeybee(UTCI 열쾌적성) 평가

### 전략 2: "15분 축소도시" — 역세권 압축 재개발

**문제**: 인구 감소 중인데 도시 면적은 그대로 → 인프라 유지비 증가, 서비스 밀도 저하

**데이터 근거**: 인구 연평균 1만 명 감소 / 2044년 200만 명 이하 / 20대 6,300명 순유출

**전략**:
- 대구 도시철도 1·2·3호선 역 중심 **도보 10분(800m) 역세권에 도시 기능 압축**
- Carlos Moreno의 15분 도시 6대 기능(주거·일자리·상업·의료·교육·여가) 모두 도보권 내 배치
- 역세권 복합용도개발(MXD): 지상층 상업+문화, 중간층 업무+의료, 상층 주거
- 역세권 밖 저밀도 지역은 **관리형 축소** — 자연환원(녹지화) 또는 도시농업 전환
- 대구 중구(2024년 인구 9.7% 증가 — 유일한 증가 구) 사례를 벤치마크하여 원도심 압축 강화

**도구**: Python osmnx(Isochrone) → Grasshopper(파라메트릭 역세권 마스터플랜) → Revit+Dynamo(BIM 상세설계) → Unity(XR 시민참여)

### 전략 3: "초고령 친화 재개발" — 에이징 인 플레이스(Aging in Place)

**문제**: 노인인구 20.9%, 노령화지수 197.5, 독거노인 급증

**데이터 근거**: 2052년 고령인구 42.5% / 돌봄 수요 폭발 예상 / 학교 학생 수 급감

**전략**:
- **학교→복합커뮤니티센터 전환**: 학생 감소 학교를 노인복지+평생교육+어린이집+마을카페 복합시설로 전환 (세대 통합형)
- **무장애(Barrier-free) 보행환경**: 재개발 지역 보도 최소 2m 확보, 경사 5% 이하, 벤치 50m 간격
- **돌봄 인프라 접근성 최적화**: Location-Allocation Model로 노인복지시설 최적 입지 산출
- **고령친화 주거**: 1~2인 소형, 엘리베이터 필수, 스마트홈 IoT(낙상감지·건강모니터링)
- **무더위쉼터 네트워크 고도화**: 열취약도 맵 + 독거노인 분포 맵 교차 → 폭염 사각지대에 쿨링 거점 배치

**도구**: QGIS Location-Allocation / Grasshopper Accessibility Analysis / Revit 유니버설디자인 템플릿

### 전략 4: "청년 앵커 전략" — 일자리·주거 결합형 거점

**문제**: 20대 연간 6,300명 순유출 (전출 사유 1위: 직업 41.4%)

**데이터 근거**: 경제기반 취약 / GRDP 성장 하위 / 대학은 많으나 졸업 후 수도권 이탈

**전략**:
- 원도심 유휴 산업시설(구 염색산업단지, 제3산업단지 등)을 **청년 혁신지구**로 전환
- 앵커 시설: 디지털 콘텐츠(게임·XR·AI), 헬스케어, 로봇 등 대구 전략산업 연계
- **직주근접형 청년주택**: 산업시설 상층에 저렴한 청년 임대주택 배치
- 대구 대학(경북대·계명대·영남대·대구가톨릭대 등) 연계 **캠퍼스타운** — 판교 모델 축소판
- 원격근무 거점(코워킹스페이스) 네트워크 → 수도권 유출 방어

**도구**: 상권분석(소상공인 데이터 + 유동인구) → 경제기반분석(LQ) → Grasshopper 산업지구 마스터플랜 → 재무분석(Python NPV/IRR)

### 전략 5: "데이터 기반 적응형 관리" — 디지털 트윈 + AI

**문제**: 재개발 이후에도 지속적 관리와 적응이 필요

**데이터 근거**: 기후변화 가속 + 인구구조 지속 변화 + 기술 환경 급변

**전략**:
- **대구 디지털 트윈** 구축: CityGML LOD2 + 건물 BIM(IFC) + IoT 센서(기온·미세먼지·소음·유동인구) → 실시간 도시 모니터링
- 재개발 사업 Before/After를 디지털 트윈에서 **시뮬레이션 후 시행** (Gehl 방법론의 디지털 버전)
- **AI 예측 모델**: PyTorch 기반 — 인구이동 예측 (LSTM), 공시지가 예측 (XGBoost/GBM), 열섬 변화 예측 (CNN-LSTM), 상권 변화 예측 (Transformer)
- **시민 참여 XR 플랫폼**: Unity로 재개발 계획 VR 체험 → 주민 피드백 수집 → 계획 수정 반영
- **LLM 활용**: 법규·계획 문서 자동 분석 (RAG), 시민 민원 텍스트 분석, 자동 보고서 생성

**도구**: CityGML + PostgreSQL/PostGIS (공간 DB) → Python PyTorch (ML/DL) → Unity (XR) → Rhino+Grasshopper (파라메트릭 자동 설계 루프) → IFC/BIM 연동 (Revit+Dynamo)

---

## PART 5. 실행 로드맵 — 3단계 접근

### Phase 1 (0-6개월): 데이터 수집 & 현황 분석
- [ ] 10대 카테고리 데이터 수집 완료
- [ ] 전처리 파이프라인 구축 (Python + PostGIS)
- [ ] 7대 분석 맵 생성
- [ ] 통합 재개발 우선순위 맵 산출
- [ ] 우선 재개발 대상 지역 3~5곳 선정

### Phase 2 (6-18개월): 전략 수립 & 시뮬레이션
- [ ] 선정 지역 상세 현장조사 (Gehl 공공생활조사 방법론)
- [ ] 바람길 CFD 시뮬레이션 (Grasshopper+Butterfly)
- [ ] 파라메트릭 마스터플랜 대안 생성 (Grasshopper)
- [ ] 환경·교통·인프라 시뮬레이션
- [ ] 디지털 트윈 프로토타입 구축
- [ ] XR 시민참여 워크숍 실시

### Phase 3 (18-36개월): 상세설계 & 실행
- [ ] 선호 대안 BIM 상세설계 (Revit+Dynamo)
- [ ] IFC 기반 데이터 연동 (건축-도시-인프라)
- [ ] AI 예측 모델 운영 (인구·경제·열환경)
- [ ] 사업 타당성 분석 (CBA, NPV/IRR)
- [ ] 정비구역 지정 및 사업 추진

---

## 부록: 핵심 데이터 소스 URL 총정리

| 분류 | 사이트명 | URL |
|------|----------|-----|
| 통합 | D-데이터허브 (대구 공공데이터) | data.daegu.go.kr |
| 통합 | 공공데이터포털 (전국) | data.go.kr |
| 통합 | 대구통계포털 | stat.daegu.go.kr |
| 통합 | 대구빅데이터활용센터 | bigdata.dip.or.kr |
| 통계 | 통계청 KOSIS | kosis.kr |
| 공간 | 국가공간정보포털 V-World | vworld.kr |
| 공간 | 대구지도포털 | gis.go.kr |
| 공간 | 토지이용규제정보 | luris.molit.go.kr |
| 건축 | 세움터 (건축물대장) | open.eais.go.kr |
| 부동산 | 실거래가 공개시스템 | rt.molit.go.kr |
| 부동산 | 부동산공시가격 | realtyprice.kr |
| 교통 | TAGO 대중교통정보 | tago.go.kr |
| 교통 | 도로교통량 통계 | roadtraf.ex.co.kr |
| 기상 | 기상자료개방포털 | data.kma.go.kr |
| 환경 | 에어코리아 (대기질) | airkorea.or.kr |
| 환경 | 환경공간정보 (생태·토지피복) | egis.me.go.kr |
| 위성 | Google Earth Engine | earthengine.google.com |
| 위성 | Copernicus (Sentinel) | scihub.copernicus.eu |
| 위성 | USGS EarthExplorer (Landsat) | earthexplorer.usgs.gov |
| 상권 | 소상공인 상권정보 | sg.sbiz.or.kr |
| 도시재생 | 대구 창의도시재생지원센터 | dgucenter.or.kr |
| 연구 | 대구정책연구원 | dpi.re.kr |
| 수자원 | 국가수자원관리 | wamis.go.kr |
| 홍수 | 홍수지도정보 | floodmap.go.kr |

---

## 결론: 대구 재개발의 한 문장 공식

> **"줄어드는 인구를 역세권에 모으고, 막힌 바람길을 열어 열섬을 깨고, 떠나는 청년에게 일자리를 만들고, 늘어나는 노인에게 걸어갈 수 있는 돌봄을 놓아라. 이 모든 것을 데이터로 증명하고, 디지털 트윈으로 미리 살아보고, 시민과 함께 결정하라."**

이것이 대구의 데이터 기반 재개발이다.
