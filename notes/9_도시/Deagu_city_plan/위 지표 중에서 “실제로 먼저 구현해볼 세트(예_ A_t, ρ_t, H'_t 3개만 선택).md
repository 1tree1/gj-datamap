<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# 위 지표 중에서 “실제로 먼저 구현해볼 세트(예: A_t, ρ_t, H'_t 3개만 선택)”를 골라서, 구체 공식 + Python 레벨의 계산 순서까지 쪼개서 pseudo-code 형태로 정리해 줄 수도 있다.

연구시작해

먼저 구현하기 좋은 세트는 말씀하신 것처럼 **A_t(도시화 권역 면적), ρ_t(평균 인구밀도), H′_t(상대 엔트로피)** 이 3개다. SGIS 도시화 분석지도는 1㎢ 격자 상주인구를 기준으로 도시·준도시 권역을 구분하고, 권역별 격자 통계(면적·인구 등)를 제공하므로 이 세 지표를 비교적 깔끔하게 뽑아낼 수 있다.[^1][^2][^3][^4][^5]

아래는 이 3개 지표를 위한 **수식 정의 + 데이터 가정 + Python 스타일 pseudo-code**를 한 번에 돌아가는 파이프라인 형태로 정리한 것이다.

***

## 1. 데이터·모형 가정

### 1.1 데이터 구조 가정

연도 t마다 다음과 같은 1km 격자 단위 테이블을 확보한다고 가정한다.

- `grid_id`: 1km 격자 ID (SGIS/NGII 기준 격자 코드)[^6][^7]
- `year`: 연도
- `pop`: 격자 상주인구 (SGIS 격자 통계)[^2][^8]
- `urban_class`: 해당 격자가 도시화 권역 유형인지 (예: `'urban'`, `'semi_urban'`, `'non_urban'`) – SGIS 도시화 분석지도 기준[^3][^2]
- `city_id`: 분석 대상 도시 식별자 (시군구 코드나 “도시권 ID” 등; 격자↔도시 폴리곤 공간조인으로 채움)[^3]
- `area_km2`: 격자 면적(1km 격자이면 1.0 로 고정, 혹은 SHP에서 실제 면적으로 계산)[^6]

도시별·연도별로 **도시+준도시 격자만 필터링**해서 분석한다.

```text
조건: city_id == 대상도시, year == t, urban_class ∈ {'urban', 'semi_urban'}
```


***

## 2. 지표 정의 (수식)

### 2.1 A_t: 도시화 권역 면적

도시 i, 연도 t에서 도시+준도시로 분류된 1km 격자의 총 면적.

- $\mathcal{G}_{i,t}$: 도시 i, 연도 t에서 도시/준도시 격자 집합.
- 각 격자 g의 면적을 $a_g$라고 할 때 (이론상 1㎢).

$$
A_{i,t} = \sum_{g \in \mathcal{G}_{i,t}} a_g
$$

1km 정방형 격자를 쓴다면 단순히 “격자 수 × 1.0”이다.[^2][^6]

### 2.2 ρ_t: 평균 인구밀도

도시화 권역 전체 인구를 전체 면적으로 나눈 값.

- $P_{i,t} = \sum_{g \in \mathcal{G}_{i,t}} pop_g$

$$
\rho_{i,t} = \frac{P_{i,t}}{A_{i,t}}
$$

단위는 “명/㎢”.

### 2.3 H′_t: 상대 셰넌 엔트로피 (compact vs sprawl)

도시화 권역 내부 인구의 **공간 분산 정도**를 나타내는 지표로, 스프롤 연구에서 널리 쓰이는 상대 셰넌 엔트로피를 사용한다.[^4][^9][^10]

- 각 격자의 인구 비중 $p_g = pop_g / P_{i,t}$.
- 셰넌 엔트로피:

$$
H_{i,t} = -\sum_{g \in \mathcal{G}_{i,t}} p_g \log(p_g)
$$

- 상대 엔트로피(0~1로 정규화):

$$
H'_{i,t} = \frac{H_{i,t}}{\log(n_{i,t})}
$$

여기서 $n_{i,t}$는 도시화 권역에 속한 격자 수.

- $H'_{i,t} \approx 0$: 인구가 몇 개 격자에 매우 집중(매우 콤팩트).
- $H'_{i,t} \approx 1$: 인구가 모든 격자에 거의 균등(매우 분산, 스프롤 경향).[^11][^4]

***

## 3. Python 스타일 전체 파이프라인 pseudo-code

아래는 `pandas` + `geopandas`를 쓴다고 가정한 **구조 설계용 pseudo-code**다.
(실제로는 파일 구조(SHP/CSV)와 필드명을 SGIS/NGII 다운로드 결과에 맞게 조정해야 함.)[^1][^2][^6]

### 3.1 사전 준비: 데이터 적재·도시 매핑

```python
import pandas as pd
import geopandas as gpd
import numpy as np

# 1) 연도별 1km 격자 + 인구 + 도시화 권역 + city_id 정보를 하나의 GeoDataFrame으로
def load_grid_data(years, grid_shp_paths, pop_csv_paths, urban_class_paths, city_boundary_shp):
    # city_boundary_shp: 시군구 경계 (시군구 코드 포함)
    city_gdf = gpd.read_file(city_boundary_shp)  # columns: ['city_id', 'geometry', ...]
    
    all_list = []
    for year in years:
        grid = gpd.read_file(grid_shp_paths[year])   # 1km 그리드 geometry + grid_id
        pop = pd.read_csv(pop_csv_paths[year])      # grid_id, pop, ...
        urban = pd.read_csv(urban_class_paths[year])# grid_id, urban_class
        
        df = grid.merge(pop, on="grid_id").merge(urban, on="grid_id")
        df["year"] = year
        
        # 시군구 경계와 공간조인하여 city_id 부여
        df = gpd.sjoin(df, city_gdf[["city_id", "geometry"]], how="left", predicate="intersects")
        
        # 면적(km2) 계산 (투영 좌표계로 변환 후)
        df = df.to_crs(epsg=5186)  # 예: 중부원점 TM
        df["area_km2"] = df.geometry.area / 1e6
        
        all_list.append(df)
    
    all_gdf = pd.concat(all_list, ignore_index=True)
    return all_gdf
```


### 3.2 코어: A_t, ρ_t, H′_t 계산 함수

```python
def compute_metrics_for_city_year(df_city_year):
    """
    df_city_year: 하나의 도시(city_id) + 연도(year)에 대한 행만 필터링된 DataFrame
                  columns: ['grid_id', 'pop', 'urban_class', 'area_km2', ...]
    """
    # 1) 도시 + 준도시 격자만 사용
    mask_urban = df_city_year["urban_class"].isin(["urban", "semi_urban"])
    d = df_city_year[mask_urban].copy()
    
    # 인구 0이고 면적 0인 격자는 제외
    d = d[(d["area_km2"] > 0) & (d["pop"] >= 0)]
    
    # 2) A_t: 도시화 권역 면적
    A_t = d["area_km2"].sum()
    
    # 3) P_t: 도시화 권역 인구
    P_t = d["pop"].sum()
    
    # 인구가 0이면 밀도와 엔트로피는 정의 불가 → NaN 처리
    if P_t <= 0 or A_t <= 0:
        return {
            "A_t": A_t,
            "P_t": P_t,
            "rho_t": np.nan,
            "H_t": np.nan,
            "H_rel_t": np.nan,
            "n_cells": len(d)
        }
    
    # 4) rho_t: 평균 인구밀도
    rho_t = P_t / A_t  # 명/㎢
    
    # 5) H_t, H'_t: 엔트로피
    # p_i = pop_i / P_t
    d["p"] = d["pop"] / P_t
    # p == 0 인 경우는 log에서 제외
    d_nonzero = d[d["p"] > 0].copy()
    H_t = - (d_nonzero["p"] * np.log(d_nonzero["p"])).sum()
    
    n_cells = len(d_nonzero)
    if n_cells > 1:
        H_rel_t = H_t / np.log(n_cells)
    else:
        H_rel_t = 0.0  # 격자 1개면 완전 집중
    
    return {
        "A_t": A_t,
        "P_t": P_t,
        "rho_t": rho_t,
        "H_t": H_t,
        "H_rel_t": H_rel_t,
        "n_cells": n_cells
    }
```


### 3.3 도시·연도 전체 루프

```python
def compute_metrics_all(all_gdf):
    results = []
    # 분석 대상 도시·연도 리스트
    for (city_id, year), sub in all_gdf.groupby(["city_id", "year"]):
        metrics = compute_metrics_for_city_year(sub)
        metrics["city_id"] = city_id
        metrics["year"] = year
        results.append(metrics)
    
    return pd.DataFrame(results)
```

이렇게 하면 결과 테이블은 다음과 같은 형태가 된다.

```text
columns:
- city_id
- year
- A_t      (도시+준도시 권역 면적, km2)
- P_t      (도시+준도시 권역 인구)
- rho_t    (평균 인구밀도, 명/km2)
- H_t      (엔트로피)
- H_rel_t  (상대 엔트로피, 0~1)
- n_cells  (도시화 격자 수)
```

이 테이블만 있어도 **도시별·연도별 스프롤 vs 콤팩트 궤적 시각화**(A_t–rho_t–H′_t 시계열/산점도)까지 바로 들어갈 수 있다.[^9][^4]

***

## 4. 실무에서 손봐야 할 포인트

- **도시 경계 정의**: `city_id`를 시군구 기준으로 할지, 광역도시권(예: 수도권)으로 묶을지에 따라 `city_boundary_shp`를 다르게 쓴다.[^12][^3]
- **urban_class 필드**: 실제 SGIS 다운로드 파일의 필드명/코드(예: 1=도시, 2=준도시)를 확인해 매핑 테이블을 하나 둔다.[^5][^3]
- **격자 면적**: 1km 격자 SHP의 좌표계가 경위도일 경우, 반드시 투영계(EPSG:5186 등)로 변환한 뒤 area를 km²로 환산해야 한다.[^13][^6]

***

원하면, 다음 단계로 이 결과 테이블을 가지고

- 도시별 A_t–ρ_t–H′_t 궤적을 시각화하는 패턴(예: 스캐터 + 화살표, 레이더 차트),
- 혹은 두 도시(예: 서울 vs 대구)를 비교하는 최소 예제 워크플로우
까지도 pseudo-code로 이어서 정리해 줄게.
<span style="display:none">[^14][^15][^16][^17]</span>

<div align="center">⁂</div>

[^1]: https://www.data.go.kr/data/15130220/fileData.do

[^2]: https://sgis.kostat.go.kr/view/newhelp/us_help_20_22

[^3]: https://sgis.mods.go.kr/view/newhelp/urBan_help_10_0

[^4]: https://pmc.ncbi.nlm.nih.gov/articles/PMC7513086/

[^5]: https://blog.naver.com/taenafit/222649943324

[^6]: https://www.data.go.kr/data/15062736/fileData.do?recommendDataYn=Y

[^7]: https://www.data.go.kr/data/15141768/fileData.do

[^8]: https://data.edmgr.kr/dataView.do?id=www-data-go-kr-data-filedata-15144253

[^9]: https://isprs-archives.copernicus.org/articles/XLII-3-W11/59/2020/isprs-archives-XLII-3-W11-59-2020.pdf

[^10]: https://www.memphis.edu/fedex/research/smartcities/documents/presentations/banai_kwon_presentation.pdf

[^11]: https://www.asprs.org/wp-content/uploads/pers/2001journal/january/2001_jan_83-90.pdf

[^12]: https://kosis.kr/civilComplaint/qnaDetail.do?boardIdx=23066

[^13]: https://www.law.go.kr/LSW/admRulLsInfoP.do?admRulSeq=2100000212121

[^14]: https://sgis.mods.go.kr/view/catchmentArea/main

[^15]: https://www.data.go.kr/data/15130220/fileData.do?recommendDataYn=Y

[^16]: https://sgis.kostat.go.kr/view/catchmentArea/main

[^17]: https://law.go.kr/LSW/admRulLsInfoP.do?admRulSeq=2100000212121

