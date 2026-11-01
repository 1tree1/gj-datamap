<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# SGIS 실제 다운로드 포맷(도시화정도권역매핑 CSV/SHP)을 기준으로 df_metrics를 만드는 “파일 파서 pseudo‑code”까지 이어서 짜줘

먼저 짚고 갈 점부터 말하면,
`통계청_SGIS_도시화정도권역매핑`(15130220)은 **격자 단위 인구 데이터가 아니라 “권역 대분류 ↔ 시도 매핑”용 메타데이터**다.[^1]
실제 df_metrics(A_t, ρ_t, H′_t)를 만들려면, 이 매핑 + **도시화지역 격자 데이터(예: 도시화지역가구/인구)** + **1km 격자 경계**를 함께 써야 한다.[^2][^3][^4]

그래서 pseudo‑code는 아래 세 층을 전제로 짜보겠다.

1. `도시화지역*` CSV/SHP: 도시/준도시 격자별 인구(또는 가구) 값.[^3][^2]
2. 1km 격자 경계(SHP): grid_id, geometry, (필요시) 면적.[^4]
3. `도시화정도권역매핑` CSV: “권역대분류명–시도명–사용여부” 매핑(도시권/대분류 필터용).[^1]

***

## 1. SGIS 데이터 구조 가정 정리

### 1) 도시화정도권역매핑 CSV (15130220)[^1]

컬럼(요약):

- `dstrct_lclas_cd` : 권역대분류명 (예: ‘도시권_대분류A’ 같은 코드/명)
- `sido_cd`         : 시도명 (혹은 시도 코드)
- `use_yn`          : 사용여부(Y/N)

→ “어느 시도가 어떤 도시화 대분류권역에 속하는지”를 매핑하는 용도.

### 2) 도시화지역 격자 데이터 (예: 도시화지역가구)[^2][^3]

데이터 명세는 파일마다 조금씩 다르겠지만, 격자별로 대략 이런 필드를 가진다고 가정:

- `grid_id`      : 1km 격자 ID (SGIS 기준)
- `year`         : 기준 연도
- `urban_class`  : 도시화 권역 유형 (예: 1: 도시, 2: 준도시, 0: 비도시 등)
- `ppltn` 혹은 `households` : 인구 또는 가구 수
- `sido_cd`      : 시도 코드(혹은 명칭) – 권역매핑과 조인 가능

실제 컬럼명은 데이터 사양서 확인 후 매핑 테이블로 정리하는 게 안전하다.[^3][^2]

### 3) 1km 격자 경계(SHP)[^4]

- `grid_id` : 1km 격자 ID
- `geometry`: Polygon
- (없으면) 면적은 나중에 CRS 변환 후 직접 계산

***

## 2. 전체 워크플로우 개요

1. `권역매핑 CSV`를 읽어 **어떤 시도/도시권을 분석에 포함할지** 정한다.
2. 연도별 `도시화지역*`(CSV/SHP)를 읽어서 1km 격자 경계와 조인 → 연도별 GeoDataFrame.
3. 시도/도시권 경계(SHP)와 공간조인해서 `city_id` 부여.
4. 도시+준도시 격자만 필터링해서 **A_t, ρ_t, H′_t** 계산 → `df_metrics`.

***

## 3. 파일 파서 pseudo‑code (연도별 grid 레벨 GDF 만들기)

### 3.1 권역매핑 읽고 “분석 대상 시도/도시권” 정하기

```python
import pandas as pd
import geopandas as gpd

# 1) 권역 매핑 CSV 읽기 (15130220)
def load_region_mapping(mapping_csv_path):
    m = pd.read_csv(mapping_csv_path)  # dstrct_lclas_cd, sido_cd, use_yn 등
    # 사용 여부가 Y 인 것만
    m = m[m["use_yn"] == "Y"]
    return m  # 필요시 dstrct_lclas_cd 로 필터링 가능
```

예: 특정 권역대분류(예: 수도권형 도시권)만 선택하고 싶으면 `dstrct_lclas_cd`를 필터로 사용.

### 3.2 연도별 도시화 격자 + 1km 격자 SHP 조인

```python
def load_urban_grid_for_year(
    year,
    urban_csv_path,      # 도시화지역* CSV 또는 SHP
    grid1km_shp_path,    # 1km 격자 SHP
    city_boundary_shp    # 시군구 or 도시권 경계
):
    # 1) 1km 격자 경계
    grid = gpd.read_file(grid1km_shp_path)  # grid_id, geometry
    # 좌표계 통일
    grid = grid.to_crs(epsg=5186)

    # 2) 도시화 격자 통계 (CSV 기준)
    urban = pd.read_csv(urban_csv_path)     # grid_id, year, urban_class, ppltn, sido_cd ...
    # 연도 필터
    urban = urban[urban["year"] == year]

    # 3) 1km 격자와 조인
    df = grid.merge(urban, on="grid_id", how="inner")

    # 4) 면적 계산 (1km 격자면 대부분 1km² 근처이지만, 실제 값으로 계산)
    df["area_km2"] = df.geometry.area / 1e6

    # 5) 시군구/도시권 경계와 공간조인해서 city_id 부여
    city_gdf = gpd.read_file(city_boundary_shp)  # city_id, geometry
    city_gdf = city_gdf.to_crs(df.crs)

    df = gpd.sjoin(df, city_gdf[["city_id", "geometry"]], how="left", predicate="intersects")

    # 6) 필요한 컬럼만 정리
    #   ppltn 컬럼명은 실제 파일에 맞춰 조정 (예: 'tot_ppltn', 'hh_cnt' 등)
    df = df.rename(columns={
        "ppltn": "pop"   # 인구 기준 분석이면
        # "hh_cnt": "pop"  # 가구 기준 분석으로 바꾸고 싶으면 여기 수정
    })

    return df  # columns: grid_id, pop, urban_class, area_km2, city_id, year, geometry ...
```

※ 실제 `urban_csv_path`가 SHP이면 `gpd.read_file`로 읽고 나머지는 동일.

***

## 4. df_metrics 생성까지 전체 파이프라인 pseudo‑code

이 부분은 이전에 작성한 `compute_metrics_for_city_year`를 그대로 재사용하는 구조로 간다.

### 4.1 도시+준도시 필터 후 지표 계산 함수 (재사용)

```python
import numpy as np

def compute_metrics_for_city_year(df_city_year):
    # 도시 + 준도시 필터 (urban_class 실제 코드에 따라 수정)
    # 예: 1=도시, 2=준도시, 0=비도시
    mask_urban = df_city_year["urban_class"].isin([1, 2])
    d = df_city_year[mask_urban].copy()

    d = d[(d["area_km2"] > 0) & (d["pop"] >= 0)]
    A_t = d["area_km2"].sum()
    P_t = d["pop"].sum()

    if P_t <= 0 or A_t <= 0:
        return {
            "A_t": A_t,
            "P_t": P_t,
            "rho_t": np.nan,
            "H_t": np.nan,
            "H_rel_t": np.nan,
            "n_cells": len(d)
        }

    rho_t = P_t / A_t

    d["p"] = d["pop"] / P_t
    d_nonzero = d[d["p"] > 0].copy()
    H_t = - (d_nonzero["p"] * np.log(d_nonzero["p"])).sum()

    n_cells = len(d_nonzero)
    if n_cells > 1:
        H_rel_t = H_t / np.log(n_cells)
    else:
        H_rel_t = 0.0

    return {
        "A_t": A_t,
        "P_t": P_t,
        "rho_t": rho_t,
        "H_t": H_t,
        "H_rel_t": H_rel_t,
        "n_cells": n_cells
    }
```


### 4.2 여러 연도·도시에 대해 df_metrics 생성

```python
def build_df_metrics(
    years,
    urban_csv_paths,      # dict: {year: path_to_urban_csv}
    grid1km_shp_path,
    city_boundary_shp
):
    all_grid_list = []
    for year in years:
        df_year = load_urban_grid_for_year(
            year=year,
            urban_csv_path=urban_csv_paths[year],
            grid1km_shp_path=grid1km_shp_path,
            city_boundary_shp=city_boundary_shp
        )
        all_grid_list.append(df_year)

    all_gdf = pd.concat(all_grid_list, ignore_index=True)

    # 도시/연도별 그룹핑
    records = []
    for (city_id, year), sub in all_gdf.groupby(["city_id", "year"]):
        metrics = compute_metrics_for_city_year(sub)
        metrics["city_id"] = city_id
        metrics["year"] = year
        records.append(metrics)

    df_metrics = pd.DataFrame(records)
    return df_metrics
```

여기까지 실행하면:

- `df_metrics`는 (city_id, year) 단위로 A_t, P_t, ρ_t, H′_t가 계산된 테이블.
- `도시화정도권역매핑` CSV는, 예를 들어 “수도권형 도시권만 골라서 도시 리스트를 뽑는다”든지, “권역 대분류별로 도시 세트를 다르게 본다”는 용도로 활용하면 된다.[^1]

***

## 5. 권역매핑을 활용해 “어떤 도시를 포함할지” 제어하는 예시

예: 권역대분류명 중에서 `dstrct_lclas_cd = '01'` (가칭: 수도권형)을 연구 대상만으로 삼고 싶다고 치면:

```python
def select_cities_by_region(mapping_csv_path, target_region_code):
    m = pd.read_csv(mapping_csv_path)  # dstrct_lclas_cd, sido_cd, use_yn
    m = m[(m["use_yn"] == "Y") & (m["dstrct_lclas_cd"] == target_region_code)]
    # 여기서 sido_cd를 city_boundary_shp 내 시도 코드와 매핑
    return m["sido_cd"].unique()
```

그리고 `build_df_metrics`를 돌린 뒤에:

```python
target_cities = select_cities_by_region("도시화정도권역매핑.csv", target_region_code="01")
df_metrics_region = df_metrics[df_metrics["city_id"].isin(target_cities)]
```

이런 식으로 “특정 권역대분류에 속하는 도시들만 골라서” A_t–ρ_t–H′_t 궤적을 비교 분석할 수 있다.[^2][^1]

***

요약하면:

- `도시화정도권역매핑` 자체는 지리값이 없고, **도시권/권역 대분류–시도 매핑** 역할만 한다.[^1]
- 실제 df_metrics를 만들기 위한 지리 단위는 `도시화지역*` 격자 데이터 + 1km 격자 SHP에서 가져오고,[^3][^4][^2]
- 위 pseudo‑code처럼 연도별로 격자 GDF를 만들고 → 도시/연도별로 A_t, ρ_t, H′_t를 집계하면 된다.

실제 SGIS 파일을 한 번이라도 받아보셨다면, 다음 단계로 **실제 컬럼명(예: ‘tot_ppltn’, ‘urban_cls_cd’ 등)**을 확인해서, 위 pseudo‑code의 `ppltn`, `urban_class`, `year` 부분만 현행 필드명에 맞게 매핑해 주면 바로 돌릴 수 있을 것이다.

<div align="center">⁂</div>

[^1]: https://www.data.go.kr/data/15130220/fileData.do

[^2]: https://sgis.kostat.go.kr/view/newhelp/us_help_20_22

[^3]: https://data.edmgr.kr/dataView.do?id=www-data-go-kr-data-filedata-15144253

[^4]: https://www.data.go.kr/data/15062736/fileData.do?recommendDataYn=Y

