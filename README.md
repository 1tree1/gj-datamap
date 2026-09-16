# gj-datamap — 구경주역 데이터맵

경주시 고시 제2026-8호 지구단위계획(구경주역) 벡터와 현황 데이터를 지도에 얹는 정적 웹. 데이터 파이프라인은 `../9_도시/pipeline/`.

```bash
npm install
python scripts/sync_data.py        # 9_도시 산출물(4326 GeoJSON) → data/
cp src/config.example.js src/config.js   # V-World 키 (선택)
npm run dev                        # http://localhost:5173
```

배포: `main` 푸시 → GitHub Actions → https://1tree1.github.io/gj-datamap/
(저장소 Settings → Pages → Source: GitHub Actions). V-World 배경을 쓰려면 Secret `VWORLD_KEY` 등록 + 브이월드 서비스 URL에 `https://1tree1.github.io` 추가.

레이어 추가: `src/layers.json`에 항목 하나 + `scripts/sync_data.py`에 파일 매핑 한 줄.
