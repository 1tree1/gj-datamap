# SGIS 실제 다운로드 포맷 기준 df_metrics 파일 파서

> 원문 제목: "SGIS 실제 다운로드 포맷(도시화정도권역매핑 CSV/SHP)을 기준으로 df_metrics를 만드는 '파일 파서 pseudo-code'까지 이어서 짜줘"
> 출처 성격: Perplexity 기반 리서치 정리
> ※ 주의: 이 파일은 프로젝트 원본 문서를 검색 인덱스를 통해 재구성한 것이다. 원본과 미세한 차이가 있을 수 있으며, 특히 4장 이후가 축약되어 있다.

먼저 짚고 갈 점: `통계청_SGIS_도시화정도권역매핑`(15130220)은 **격자 단위 인구 데이터가 아니라 "권역 대분류 ↔ 시도 매핑"용 메타데이터**다.
실제 df_metrics(A_t, ρ_t, H′_t)를 만들려면, 이 매핑 + **도시화지역 격자 데이터(예: 도시화지역가구/인구)** + **1km 격자 경계**를 함께 써야 한다.

전제 3층:

1. `도시화지역*` CSV/SHP: 도시/준도시 격자별 인구(또는 가구) 값
2. 1km 격자 경계(SHP): grid_id, geometry, (필요시) 면적
3. `도시화정도권역매핑` CSV: "권역대분류명–시도명–사용여부" 매핑(도시권/대분류 필터용)

---

## 1. SGIS 데이터 구조 가정 정리

### 1) 도시화정도권역매핑 CSV (15130220)

컬럼(요약):

- `dstrct_lclas_cd` : 권역대분류명 (예: '도시권_대분류A' 같은 코드/명)
- `sido_cd`         : 시도명 (혹은 시도 코드)
- `use_yn`          : 사용여부(Y/N)

→ "어느 시도가 어떤 도시화 대분류권역에 속하는지"를 매핑하는 용도.

### 2) 도시화지역 격자 데이터 (예: 도시화지역가구)

데이터 명세는 파일마다 조금씩 다르지만, 격자별로 대략 이런 필드를 가진다고 가정:

- `grid_id`      : 1km 격자 ID (SGIS 기준)
- `year`         : 기준 연도
- `urban_class`  : 도시화 권역 유형 (예: 1: 도시, 2: 준도시, 0: 비도시 등)
- `ppltn` 혹은 `households` : 인구 또는 가구 수
- `sido_cd`      : 시도 코드(혹은 명칭) – 권역매핑과 조인 가능

실제 컬럼명은 데이터 사양서 확인 후 매핑 테이블로 정리하는 게 안전하다.

### 3) 1km 격자 경계(SHP)

- `grid_id` : 1km 격자 ID
- `geometry`: Polygon
- (없으면) 면적은 나중에 CRS 변환 후 직접 계산

---

## 2. 전체 워크플로우 개요

1. `권역매핑 CSV`를 읽어 **어떤 시도/도시권을 분석에 포함할지** 정한다.
2. 연도별 `도시화지역*`(CSV/SHP)를 읽어서 1km 격자 경계와 조인 → 연도별 GeoDataFrame.
3. 시도/도시권 경계(SHP)와 공간조인해서 `city_id` 부여.
4. 도시+준도시 격자만 필터링해서 **A_t, ρ_t, H′_t** 계산 → `df_metrics`.

---

## 3. 파일 파서 pseudo-code (연도별 grid 레벨 GDF 만들기)

### 3.1 권역매핑 읽고 "분석 대상 시도/도시권" 정하기

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

---

## 4. df_metrics 생성까지 전체 파이프라인

이 부분은 `연구_지표세트_At_rhot_Ht_구현.md`에서 작성한 `compute_metrics_for_city_year` / `compute_metrics_all`을 그대로 재사용하는 구조로 간다. 연도 리스트를 돌면서 `load_urban_grid_for_year`로 연도별 GDF를 만들고, concat한 뒤 `(city_id, year)` 그룹별로 A_t / P_t / ρ_t / H_t / H′_t를 계산해 `df_metrics`를 얻는다.

---

## 요약

- `도시화정도권역매핑` 자체는 지리값이 없고, **도시권/권역 대분류–시도 매핑** 역할만 한다.
- 실제 df_metrics를 만들기 위한 지리 단위는 `도시화지역*` 격자 데이터 + 1km 격자 SHP에서 가져온다.
- 위 pseudo-code처럼 연도별로 격자 GDF를 만들고 → 도시/연도별로 A_t, ρ_t, H′_t를 집계하면 된다.
- 실제 SGIS 파일을 받아본 뒤 **실제 컬럼명(예: 'tot_ppltn', 'urban_cls_cd' 등)**을 확인해서, 위 pseudo-code의 `ppltn`, `urban_class`, `year` 부분만 현행 필드명에 맞게 매핑하면 바로 돌릴 수 있다.

## 참고 출처

- data.go.kr/data/15130220 — 통계청 SGIS 도시화정도권역매핑
- sgis.kostat.go.kr/view/newhelp/us_help_20_22 — SGIS 격자통계 도움말
- data.edmgr.kr/dataView.do?id=www-data-go-kr-data-filedata-15144253 — 도시화지역 격자 데이터
- data.go.kr/data/15062736 — 1km 격자 경계
