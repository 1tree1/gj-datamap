# "Seoul sample" end-to-end 미니 시나리오 — 15분 보행 접근성

> 원문 제목: "'Seoul sample'을 가정한 end-to-end 미니 시나리오 (데이터 파일 이름/형식을 더 구체화)"
> 출처 성격: Perplexity 기반 리서치 정리

서울을 대상으로 "접근성·네트워크 기반 도시성 평가"를 **끝까지 한 번 도는 최소 시나리오**. 실제 파일명·형식까지 가정해서 폴더 구조·테이블 스키마·pseudo-code 수준으로 정리.

---

## 1. 시나리오 개요

목표:

- 서울에서 "지하철역 + 동주민센터(또는 주민센터/공공시설)"를 생활거점으로 잡고,
- 서울시 250m 격자 생활인구를 수요점으로 사용,
- 국토부 도시계획(도로) + 보행속도를 이용해 **15분 보행 접근성**을 계산,
- "15분 안에 역 또는 주민센터를 이용할 수 있는 인구 비율 + 공백 격자 지도"를 뽑는다.

---

## 2. 데이터 준비 (파일/포맷 가정)

### 2.1 도로망 (도로 링크)

- 소스: 국토교통부 도시계획(도로) API에서 서울 영역을 WFS/SHP로 다운로드하거나, 한 번 받은 뒤 로컬에 저장
- 파일: `data/roads/seoul_roads_utm.shp`
- 주요 필드: `road_id`, `geometry` (LineString, EPSG:5186)

### 2.2 지하철역 위치

- 소스: 서울교통공사 1~8호선 역사 좌표(위경도) 파일 데이터
- 파일: `data/poi/seoul_subway_stations.csv`
- 주요 필드: `station_id`, `station_name`, `line`, `lon`, `lat` (EPSG:4326)

추가적으로 `서울교통공사_노선별 지하철역 정보` OpenAPI를 써도 되지만, 여기선 좌표 파일만 사용.

### 2.3 동주민센터 위치 (예시: 행정복지센터)

- 소스: 서울열린데이터광장 – 자치구별 주민센터 위치 데이터
- 파일: `data/poi/seoul_community_centers.csv`
- 주요 필드: `center_id`, `name`, `addr`, `lon`, `lat`

(주소만 있을 경우 국토부 지오코더 API로 좌표 변환 가능.)

### 2.4 생활인구(수요 격자)

- 소스: 서울시 250m 격자 생활인구(내국인) – 서울 열린데이터광장
- 파일: `data/pop/seoul_living_pop_250m_2024-10.csv` (시점 하나를 고정)
- 주요 필드: `cell_id`, `x`, `y` (EPSG:5186 격자 중심 좌표), `pop` (특정 시간대 평균 생활인구)

### 2.5 서울 경계 (도시 분석 범위)

- 소스: 통계청/행정구역 경계 또는 서울시 행정구역 SHP
- 파일: `data/boundary/seoul_boundary.shp`

---

## 3. 폴더 구조 예시

```text
project/
  data/
    roads/
      seoul_roads_utm.shp
    poi/
      seoul_subway_stations.csv
      seoul_community_centers.csv
    pop/
      seoul_living_pop_250m_2024-10.csv
    boundary/
      seoul_boundary.shp
  src/
    build_network.py
    accessibility_15min.py
```

---

## 4. End-to-End 워크플로우 pseudo-code

### 4.1 네트워크 구축 (도로망 → 보행 네트워크 그래프)

`src/build_network.py`:

```python
import geopandas as gpd
import networkx as nx
from shapely.geometry import Point

def build_seoul_road_network(road_shp_path):
    roads = gpd.read_file(road_shp_path)  # EPSG:5186 가정
    roads = roads.to_crs(epsg=5186)

    G = nx.Graph()

    for idx, row in roads.iterrows():
        line = row.geometry
        # 시작/끝점 좌표 (간단 버전)
        x0, y0 = line.coords[0]
        x1, y1 = line.coords[-1]
        n0 = (x0, y0)
        n1 = (x1, y1)

        length_m = line.length
        walk_time_min = length_m / 80.0  # 4.8km/h 기준

        # 노드/엣지 추가
        if n0 not in G:
            G.add_node(n0)
        if n1 not in G:
            G.add_node(n1)
        G.add_edge(n0, n1, length=length_m, walk_time=walk_time_min)

    return G
```

### 4.2 시설(역+주민센터) 좌표 → 네트워크 노드 스냅

```python
import pandas as pd
import numpy as np
import geopandas as gpd

def load_and_snap_pois(G, subway_csv, center_csv):
    # 1) 지하철역
    sub = pd.read_csv(subway_csv)  # lon, lat
    gsub = gpd.GeoDataFrame(
        sub,
        geometry=gpd.points_from_xy(sub["lon"], sub["lat"]),
        crs="EPSG:4326"
    ).to_crs(epsg=5186)

    # 2) 주민센터
    cen = pd.read_csv(center_csv)
    gcen = gpd.GeoDataFrame(
        cen,
        geometry=gpd.points_from_xy(cen["lon"], cen["lat"]),
        crs="EPSG:4326"
    ).to_crs(epsg=5186)

    # 3) 노드 GeoDataFrame
    nodes_gdf = gpd.GeoDataFrame(
        {"node": list(G.nodes())},
        geometry=[Point(xy) for xy in G.nodes()],
        crs="EPSG:5186"
    )

    def snap_points_to_nodes(points_gdf):
        snapped_nodes = []
        for idx, row in points_gdf.iterrows():
            # 가장 가까운 도로 노드 찾기 (성능은 차치)
            dists = nodes_gdf.geometry.distance(row.geometry)
            nearest_idx = dists.idxmin()
            node_id = nodes_gdf.loc[nearest_idx, "node"]
            snapped_nodes.append(node_id)
        points_gdf["node_id"] = snapped_nodes
        return points_gdf

    gsub = snap_points_to_nodes(gsub)
    gcen = snap_points_to_nodes(gcen)

    # 생활거점: 지하철역 + 주민센터
    gpoi = pd.concat([gsub.assign(type="subway"), gcen.assign(type="center")], ignore_index=True)
    return gpoi
```

### 4.3 생활인구 250m 격자 → 노드 스냅

```python
def load_and_snap_pop_cells(G, pop_csv):
    pop = pd.read_csv(pop_csv)  # cell_id, x, y, pop (x,y는 EPSG:5186 좌표 가정)
    gpop = gpd.GeoDataFrame(
        pop,
        geometry=gpd.points_from_xy(pop["x"], pop["y"]),
        crs="EPSG:5186"
    )

    nodes_gdf = gpd.GeoDataFrame(
        {"node": list(G.nodes())},
        geometry=[Point(xy) for xy in G.nodes()],
        crs="EPSG:5186"
    )

    snapped = []
    for idx, row in gpop.iterrows():
        dists = nodes_gdf.geometry.distance(row.geometry)
        nearest_idx = dists.idxmin()
        node_id = nodes_gdf.loc[nearest_idx, "node"]
        snapped.append(node_id)

    gpop["node_id"] = snapped
    return gpop
```

---

## 5. 서울 15분 보행 접근성 계산

### 5.1 15분 안에 "역 또는 주민센터" 접근 가능 인구 비율

```python
import networkx as nx
import numpy as np

def compute_15min_coverage(G, pop_cells, pois, time_field="walk_time", threshold=15.0):
    # 1) 생활거점(역 + 주민센터) 노드 목록
    poi_nodes = set(pois["node_id"])

    # 2) multi-source Dijkstra: 모든 거점에서 출발해 최단시간
    lengths = nx.multi_source_dijkstra_path_length(G, poi_nodes, weight=time_field)

    # 3) 각 인구 격자의 최근접 거점까지 시간
    pop_cells["nearest_time"] = pop_cells["node_id"].map(lengths).fillna(np.inf)

    # 4) 커버 인구 비율
    covered_pop = pop_cells[pop_cells["nearest_time"] <= threshold]["pop"].sum()
    total_pop = pop_cells["pop"].sum()
    coverage_ratio = covered_pop / total_pop if total_pop > 0 else np.nan

    return coverage_ratio, pop_cells
```

### 5.2 End-to-End 실행 스크립트 예시

`src/accessibility_15min.py`:

```python
from build_network import build_seoul_road_network, load_and_snap_pois, load_and_snap_pop_cells

def main():
    road_shp = "data/roads/seoul_roads_utm.shp"
    subway_csv = "data/poi/seoul_subway_stations.csv"
    center_csv = "data/poi/seoul_community_centers.csv"
    pop_csv = "data/pop/seoul_living_pop_250m_2024-10.csv"

    # 1) 네트워크 구성
    G = build_seoul_road_network(road_shp)

    # 2) 생활거점 스냅
    pois = load_and_snap_pois(G, subway_csv, center_csv)

    # 3) 인구 격자 스냅
    pop_cells = load_and_snap_pop_cells(G, pop_csv)

    # 4) 15분 커버리지 계산
    coverage, pop_cells_with_time = compute_15min_coverage(G, pop_cells, pois)
    print(f"서울 15분 생활거점(역+주민센터) 커버 인구 비율: {coverage:.3f}")

    # 5) 공백 격자 내보내기 (시각화용)
    gap_cells = pop_cells_with_time[pop_cells_with_time["nearest_time"] > 15.0].copy()
    gap_cells.to_file("output/seoul_gap_cells_15min.shp")

if __name__ == "__main__":
    main()
```

결과:

- `coverage` → "서울에서 역 또는 주민센터를 15분 보행 이내에 이용 가능한 생활인구 비율"이라는 하나의 도시성 지표
- `seoul_gap_cells_15min.shp` → QGIS 등에서 바로 띄워볼 수 있는 "생활거점 15분 사각지대" 지도
- 이후 시설 유형(문화, 의료, 어린이집 등)을 바꾸거나, 대중교통 네트워크(ODsay API, 지하철 역간거리/소요시간, 버스노선 등)를 추가해서 "보행+대중교통 15분"으로 확장

---

## 참고 출처

- 서울 열린데이터광장 — data.seoul.go.kr (생활인구 250m 격자: OA-22784, 지하철역 정보: OA-15442)
- 국토교통부 도시계획(도로) API — data.go.kr/data/15058180
- 국토정보플랫폼 OpenAPI / 지오코더 — map.ngii.go.kr, data.go.kr/data/15101106
- 1km 격자 경계 — data.go.kr/data/15062736
- 서울교통공사 역사 좌표 — data.go.kr/data/15099316
- ODsay Lab — lab.odsay.com
