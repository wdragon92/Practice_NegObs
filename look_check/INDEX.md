# `look_check/` INDEX — 디스크 실측 목록

> **generated from disk on 2026-08-27 by `scripts/make_lookcheck_index.py`** — 손으로 고치지 말고 스크립트를 다시 돌릴 것. 라운드를 추가·이동·삭제했으면 매번.

`look_check/` 는 `README.md` 와 이 파일만 빼고 전부 `.gitignore` 대상이다. 그래서 **이 파일이 렌더 머신에 무엇이 있었는지를 남기는 유일한 커밋 기록**이다. 라운드 이름은 절대 바뀌지 않는다(`README.md` §3). 배치 규칙은 `README.md` §1.

## 0. 구조

```
look_check/
  <scene>/<round>/          현행 — 판정 그리드 · 코퍼스 · 앵커 · baseline-of-record
  _archive/<wave>/<scene>/<round>/   지난 웨이브의 증거 라운드 (w2 · w2d · w3 · w3fix)
  _experiments/<topic>/     크롭 · 게이트 · 트윈 · 스파이크 · 진단
  _review/<wave>/<round>/   검수 갤러리 (w2 · w3 · w4)
  logs/                     렌더 저널 (*.log · *_times.tsv · spike_results.json)
  _t0_spike   -> _experiments/t0_spike               (심볼릭 링크, 사양 인용)
  spike_probe -> _experiments/spike_p1/spike_probe   (심볼릭 링크, 사양 인용)
```

**씬 폴더 안에는 심볼릭 링크를 만들지 않는다.** 링크는 mtime 이 새로 찍히므로 `ls -t <scene>/*/ | head -1` 최신 라운드 탐색(§5)이 즉시 깨진다. 옮겨간 라운드는 §6 이동 지도로 찾는다.

## 1. 롤업

### 1.1 웨이브별

| 웨이브 | 라운드 | GB | 현행(scene root) | 아카이브 |
|---|---:|---:|---:|---:|
| W2-P2 | 42 | 1.39 | 37 | 5 |
| W2-P3/P4 | 64 | 2.81 | 47 | 17 |
| W2-ladder | 72 | 3.49 | 54 | 18 |
| W2-ctx | 30 | 1.27 | 24 | 6 |
| W2-mode | 4 | 0.04 | 4 | 0 |
| W2-nearfield | 7 | 0.42 | 7 | 0 |
| W2 | 4 | 0.21 | 4 | 0 |
| W2-D | 74 | 3.73 | 66 | 8 |
| W3 | 105 | 4.89 | 34 | 71 |
| W3R | 1 | 0.15 | 0 | 1 |
| W3-fix | 135 | 4.46 | 4 | 131 |
| W4 | 96 | 5.11 | 96 | 0 |
| special | 5 | 0.25 | 0 | 5 |
| **합계** | **639** | **28.23** | **377** | **262** |

### 1.2 씬별

| 씬 | 현행 | 현행 GB | 아카이브 | 아카이브 GB |
|---|---:|---:|---:|---:|
| `scene01` | 24 | 0.95 | 10 | 0.34 |
| `scene02` | 13 | 0.48 | 12 | 0.45 |
| `scene03` | 14 | 0.79 | 7 | 0.32 |
| `scene04` | 10 | 0.55 | 6 | 0.33 |
| `scene05` | 13 | 0.65 | 12 | 0.54 |
| `scene06` | 11 | 0.59 | 19 | 0.82 |
| `scene07` | 19 | 0.98 | 5 | 0.23 |
| `scene08` | 10 | 0.52 | 8 | 0.34 |
| `scene09` | 14 | 0.53 | 6 | 0.18 |
| `scene10` | 12 | 0.79 | 10 | 0.57 |
| `scene11` | 12 | 0.65 | 10 | 0.48 |
| `scene12` | 10 | 0.48 | 10 | 0.41 |
| `scene13` | 24 | 1.15 | 16 | 0.71 |
| `scene14` | 8 | 0.28 | 11 | 0.33 |
| `scene15` | 11 | 0.57 | 6 | 0.23 |
| `scene16` | 15 | 0.69 | 10 | 0.39 |
| `scene17` | 10 | 0.51 | 8 | 0.25 |
| `scene18` | 10 | 0.40 | 7 | 0.22 |
| `scene19` | 8 | 0.39 | 9 | 0.37 |
| `scene20` | 7 | 0.38 | 9 | 0.50 |
| `scene21` | 11 | 0.47 | 5 | 0.15 |
| `sceneC1` | 9 | 0.40 | 9 | 0.16 |
| `sceneC2` | 13 | 0.79 | 3 | 0.10 |
| `sceneC4` | 7 | 0.36 | 6 | 0.15 |
| `sceneD1` | 7 | 0.35 | 3 | 0.08 |
| `sceneD2` | 7 | 0.38 | 7 | 0.31 |
| `sceneD3` | 18 | 0.71 | 9 | 0.33 |
| `sceneD4` | 12 | 0.30 | 8 | 0.16 |
| `sceneN1` | 8 | 0.39 | 6 | 0.22 |
| `sceneN2` | 8 | 0.46 | 4 | 0.15 |
| `sceneN3` | 8 | 0.43 | 3 | 0.09 |
| `sceneN4` | 7 | 0.33 | 5 | 0.17 |
| `sceneN5` | 7 | 0.35 | 3 | 0.08 |

## 2. 현행 트리 — 씬 루트에 남은 라운드

`역할`: baseline-of-record(다음 회귀의 비교 대상) · corpus(`valset.py` 검증 코퍼스) · regr-chain(`README.md` §4 `--before-round` 체인) · anchor(발표 수치 재현) · current(W4 현행 웨이브) · evidence(보고서 증거). `왜 남았나` 열은 **코드에서 다시 뽑은 근거**다 — 이 중 하나라도 걸리면 옮기면 안 된다.

### `scene01` — 24 라운드 / 0.95 GB

| 라운드 | 웨이브 | 컷 | 역할 | 왜 남았나 |
|---|---|---:|---|---|
| `260730_w2d_fix` | W2-D | 13 | regr-chain | 회귀 체인 |
| `260730_w2d_judge` | W2-D | 13 | regr-chain | 회귀 체인 |
| `260731_w3_cb2` | W3 | 5 | regr-chain | 회귀 체인 |
| `260731_w3_mb24` | W3 | 5 | regr-chain | 회귀 체인 |
| `260731_w3_s01` | W3 | 13 | baseline-of-record | 회귀 체인 · stamp:BoR |
| `260813_w4_s01k5` | W4 | 13 | current | W4 현행 웨이브 |
| `260816_w4_final33_on` | W4 | 13 | current | W4 현행 웨이브 |
| `p2c_a` | W2-P2 | 3 | corpus | valset.py 코퍼스 |
| `p2c_b` | W2-P2 | 3 | corpus | valset.py 코퍼스 |
| `p2g1_off` | W2-P2 | 13 | corpus | valset.py 코퍼스 |
| `p2g1_on` | W2-P2 | 13 | corpus | valset.py 코퍼스 |
| `p2g2_off` | W2-P2 | 13 | corpus | valset.py 코퍼스 |
| `p2g2_on` | W2-P2 | 13 | corpus | valset.py 코퍼스 |
| `p2g3_off` | W2-P2 | 13 | corpus | valset.py 코퍼스 |
| `p2g3_on` | W2-P2 | 13 | corpus | valset.py 코퍼스 |
| `p2mat_after` | W2-P2 | 3 | corpus | valset.py 코퍼스 |
| `p2mat_before` | W2-P2 | 3 | corpus | valset.py 코퍼스 |
| `p2rf_off` | W2-P2 | 13 | corpus | valset.py 코퍼스 |
| `p2rf_on` | W2-P2 | 13 | corpus | valset.py 코퍼스 |
| `r1_on` | W2-P3/P4 | 13 | corpus | valset.py 코퍼스 |
| `r2_on` | W2-P3/P4 | 13 | corpus | valset.py 코퍼스 · 회귀 체인 |
| `v6_rt` | W2-ladder | 13 | corpus | valset.py 코퍼스 |
| `v7_pt` | W2-ladder | 13 | evidence | 판정 그리드(현행 보관) |
| `v7_rt` | W2-ladder | 13 | corpus | valset.py 코퍼스 |

### `scene02` — 13 라운드 / 0.48 GB

| 라운드 | 웨이브 | 컷 | 역할 | 왜 남았나 |
|---|---|---:|---|---|
| `260730_w2d_fix` | W2-D | 13 | regr-chain | 회귀 체인 |
| `260730_w2d_judge` | W2-D | 13 | regr-chain | 회귀 체인 |
| `260731_w3_gt25` | W3 | 13 | baseline-of-record | 회귀 체인 · stamp:BoR |
| `260731_w3_mb24` | W3 | 5 | regr-chain | 회귀 체인 |
| `260815_w4_hzbatch` | W4 | 13 | current | W4 현행 웨이브 |
| `260816_w4_final33_on` | W4 | 13 | current | W4 현행 웨이브 |
| `p2dark_fast256` | W2-P2 | 3 | corpus | valset.py 코퍼스 |
| `p2dark_fast64` | W2-P2 | 3 | corpus | valset.py 코퍼스 |
| `p2dark_legacy` | W2-P2 | 3 | corpus | valset.py 코퍼스 |
| `r1_on` | W2-P3/P4 | 13 | corpus | valset.py 코퍼스 |
| `r2_on` | W2-P3/P4 | 13 | corpus | valset.py 코퍼스 · 회귀 체인 |
| `v6_rt` | W2-ladder | 13 | corpus | valset.py 코퍼스 |
| `v7_rt` | W2-ladder | 13 | corpus | valset.py 코퍼스 |

### `scene03` — 14 라운드 / 0.79 GB

| 라운드 | 웨이브 | 컷 | 역할 | 왜 남았나 |
|---|---|---:|---|---|
| `260730_w2d_fix` | W2-D | 16 | regr-chain | 회귀 체인 |
| `260730_w2d_judge` | W2-D | 16 | regr-chain | 회귀 체인 |
| `260731_w3_cb2` | W3 | 5 | regr-chain | 회귀 체인 |
| `260731_w3_p03` | W3 | 16 | baseline-of-record | stamp:BoR |
| `260731_w3_s03` | W3 | 16 | regr-chain | 회귀 체인 |
| `260815_w4_hzbatch` | W4 | 16 | current | W4 현행 웨이브 |
| `260815_w4_physpilot` | W4 | 16 | current | W4 현행 웨이브 |
| `260816_w4_final33_on` | W4 | 16 | current | W4 현행 웨이브 |
| `260816_w4_micropilot` | W4 | 16 | current | W4 현행 웨이브 |
| `260817_w4_regfix` | W4 | 16 | current | W4 현행 웨이브 |
| `r1_on` | W2-P3/P4 | 16 | corpus | valset.py 코퍼스 |
| `r2_on` | W2-P3/P4 | 16 | corpus | valset.py 코퍼스 · 회귀 체인 |
| `v6_rt` | W2-ladder | 13 | corpus | valset.py 코퍼스 |
| `v7_rt` | W2-ladder | 16 | corpus | valset.py 코퍼스 |

### `scene04` — 10 라운드 / 0.55 GB

| 라운드 | 웨이브 | 컷 | 역할 | 왜 남았나 |
|---|---|---:|---|---|
| `260730_w2d_fix` | W2-D | 13 | regr-chain | 회귀 체인 |
| `260730_w2d_judge` | W2-D | 13 | regr-chain | 회귀 체인 |
| `260731_w3_s04` | W3 | 13 | baseline-of-record | 회귀 체인 · stamp:BoR |
| `260806_w3_allview5` | W3-fix | 4 | anchor | 앵커 |
| `260814_w4_r0probe` | W4 | 0 | current | W4 현행 웨이브 |
| `260816_w4_final33_on` | W4 | 13 | current | W4 현행 웨이브 |
| `r1_on` | W2-P3/P4 | 13 | corpus | valset.py 코퍼스 |
| `r2_on` | W2-P3/P4 | 13 | corpus | valset.py 코퍼스 · 회귀 체인 |
| `v6_rt` | W2-ladder | 13 | corpus | valset.py 코퍼스 |
| `v7_rt` | W2-ladder | 13 | corpus | valset.py 코퍼스 |

### `scene05` — 13 라운드 / 0.65 GB

| 라운드 | 웨이브 | 컷 | 역할 | 왜 남았나 |
|---|---|---:|---|---|
| `260730_w2d_fix` | W2-D | 13 | regr-chain | 회귀 체인 |
| `260730_w2d_judge` | W2-D | 13 | regr-chain | 회귀 체인 |
| `260731_w3_l05` | W3 | 13 | baseline-of-record | stamp:BoR |
| `260815_w4_r4batch` | W4 | 13 | current | W4 현행 웨이브 |
| `260816_w4_final33_on` | W4 | 13 | current | W4 현행 웨이브 |
| `260817_w4_regfix` | W4 | 13 | current | W4 현행 웨이브 |
| `facade` | W2-nearfield | 13 | corpus | valset.py 코퍼스 · 회귀 체인 |
| `r1_on` | W2-P3/P4 | 13 | corpus | valset.py 코퍼스 |
| `r2_on` | W2-P3/P4 | 13 | corpus | valset.py 코퍼스 · 회귀 체인 |
| `shrub` | W2-nearfield | 13 | corpus | valset.py 코퍼스 |
| `v6_rt` | W2-ladder | 13 | corpus | valset.py 코퍼스 |
| `v7_rt` | W2-ladder | 13 | corpus | valset.py 코퍼스 |
| `v8_rt` | W2-ladder | 13 | corpus | valset.py 코퍼스 |

### `scene06` — 11 라운드 / 0.59 GB

| 라운드 | 웨이브 | 컷 | 역할 | 왜 남았나 |
|---|---|---:|---|---|
| `260730_w2d_fix` | W2-D | 15 | regr-chain | 회귀 체인 |
| `260730_w2d_judge` | W2-D | 15 | regr-chain | 회귀 체인 |
| `260731_w3_s06` | W3 | 15 | baseline-of-record | 회귀 체인 · stamp:BoR |
| `260816_w4_final33_on` | W4 | 15 | current | W4 현행 웨이브 |
| `260816_w4_w8deck` | W4 | 15 | current | W4 현행 웨이브 |
| `260817_w4_regfix` | W4 | 15 | current | W4 현행 웨이브 |
| `r1_on` | W2-P3/P4 | 15 | corpus | valset.py 코퍼스 |
| `r2_on` | W2-P3/P4 | 15 | corpus | valset.py 코퍼스 · 회귀 체인 |
| `v6_rt` | W2-ladder | 14 | corpus | valset.py 코퍼스 |
| `v7_rt` | W2-ladder | 15 | corpus | valset.py 코퍼스 |
| `v8_rt` | W2-ladder | 15 | corpus | valset.py 코퍼스 |

### `scene07` — 19 라운드 / 0.98 GB

| 라운드 | 웨이브 | 컷 | 역할 | 왜 남았나 |
|---|---|---:|---|---|
| `260730_w2d_fix` | W2-D | 14 | regr-chain | 회귀 체인 |
| `260730_w2d_judge` | W2-D | 14 | regr-chain | 회귀 체인 |
| `260731_w3_cb2` | W3 | 5 | regr-chain | 회귀 체인 |
| `260731_w3_s07` | W3 | 14 | baseline-of-record | 회귀 체인 · stamp:BoR |
| `260816_w4_final33_on` | W4 | 14 | current | W4 현행 웨이브 |
| `p2g1_off` | W2-P2 | 14 | corpus | valset.py 코퍼스 |
| `p2g1_on` | W2-P2 | 14 | corpus | valset.py 코퍼스 |
| `p2g2_off` | W2-P2 | 14 | corpus | valset.py 코퍼스 |
| `p2g2_on` | W2-P2 | 14 | corpus | valset.py 코퍼스 |
| `p2g3_off` | W2-P2 | 14 | corpus | valset.py 코퍼스 |
| `p2g3_on` | W2-P2 | 14 | corpus | valset.py 코퍼스 |
| `r1_on` | W2-P3/P4 | 14 | corpus | valset.py 코퍼스 |
| `r2_on` | W2-P3/P4 | 14 | corpus | valset.py 코퍼스 · 회귀 체인 |
| `scene07_ptfast` | W2-mode | 3 | corpus | valset.py 코퍼스 |
| `scene07_ptlegacy` | W2-mode | 3 | corpus | valset.py 코퍼스 |
| `v6_rt` | W2-ladder | 14 | corpus | valset.py 코퍼스 |
| `v7_rt` | W2-ladder | 14 | corpus | valset.py 코퍼스 |
| `v8_pt` | W2-ladder | 14 | corpus | valset.py 코퍼스 |
| `v8_rt` | W2-ladder | 14 | corpus | valset.py 코퍼스 |

### `scene08` — 10 라운드 / 0.52 GB

| 라운드 | 웨이브 | 컷 | 역할 | 왜 남았나 |
|---|---|---:|---|---|
| `260730_w2d_fix` | W2-D | 15 | regr-chain | 회귀 체인 |
| `260730_w2d_judge` | W2-D | 15 | regr-chain | 회귀 체인 |
| `260731_w3_s08d` | W3 | 15 | baseline-of-record | 회귀 체인 · stamp:BoR |
| `260815_w4_hzbatch` | W4 | 15 | current | W4 현행 웨이브 |
| `260815_w4_r4batch` | W4 | 15 | current | W4 현행 웨이브 |
| `260816_w4_final33_on` | W4 | 15 | current | W4 현행 웨이브 |
| `r1_on` | W2-P3/P4 | 15 | corpus | valset.py 코퍼스 |
| `r2_on` | W2-P3/P4 | 15 | corpus | valset.py 코퍼스 · 회귀 체인 |
| `v6_rt` | W2-ladder | 15 | corpus | valset.py 코퍼스 |
| `v7_rt` | W2-ladder | 15 | corpus | valset.py 코퍼스 |

### `scene09` — 14 라운드 / 0.53 GB

| 라운드 | 웨이브 | 컷 | 역할 | 왜 남았나 |
|---|---|---:|---|---|
| `260730_w2d_fix` | W2-D | 14 | regr-chain | 회귀 체인 |
| `260730_w2d_judge` | W2-D | 14 | regr-chain | 회귀 체인 |
| `260731_w3_cb1` | W3 | 17 | regr-chain | 회귀 체인 |
| `260731_w3_mb24` | W3 | 5 | regr-chain | 회귀 체인 |
| `260731_w3_p09` | W3 | 18 | baseline-of-record | stamp:BoR |
| `260731_w3_s09` | W3 | 18 | baseline-of-record | 회귀 체인 · stamp:BoR |
| `260815_w4_r4batch` | W4 | 18 | current | W4 현행 웨이브 |
| `260816_w4_final33_on` | W4 | 18 | current | W4 현행 웨이브 |
| `r1_on` | W2-P3/P4 | 14 | corpus | valset.py 코퍼스 |
| `r2_on` | W2-P3/P4 | 14 | corpus | valset.py 코퍼스 · 회귀 체인 |
| `v6_rt` | W2-ladder | 13 | corpus | valset.py 코퍼스 |
| `v7_rt` | W2-ladder | 14 | corpus | valset.py 코퍼스 |
| `v8_pt` | W2-ladder | 14 | evidence | 판정 그리드(현행 보관) |
| `v8_rt` | W2-ladder | 14 | corpus | valset.py 코퍼스 |

### `scene10` — 12 라운드 / 0.79 GB

| 라운드 | 웨이브 | 컷 | 역할 | 왜 남았나 |
|---|---|---:|---|---|
| `260730_w2d_fix` | W2-D | 14 | regr-chain | 회귀 체인 |
| `260730_w2d_judge` | W2-D | 14 | regr-chain | 회귀 체인 |
| `260731_w3_s10c` | W3 | 14 | baseline-of-record | 회귀 체인 · stamp:BoR |
| `260815_w4_hzbatch` | W4 | 14 | current | W4 현행 웨이브 |
| `260815_w4_r4batch` | W4 | 14 | current | W4 현행 웨이브 |
| `260816_w4_final33_on` | W4 | 14 | current | W4 현행 웨이브 |
| `260817_w4_regfix` | W4 | 14 | current | W4 현행 웨이브 |
| `r1_on` | W2-P3/P4 | 14 | corpus | valset.py 코퍼스 |
| `r2_on` | W2-P3/P4 | 14 | corpus | valset.py 코퍼스 · 회귀 체인 |
| `v6_rt` | W2-ladder | 14 | corpus | valset.py 코퍼스 |
| `v7_rt` | W2-ladder | 14 | corpus | valset.py 코퍼스 |
| `v8_rt` | W2-ladder | 14 | corpus | valset.py 코퍼스 |

### `scene11` — 12 라운드 / 0.65 GB

| 라운드 | 웨이브 | 컷 | 역할 | 왜 남았나 |
|---|---|---:|---|---|
| `260730_w2d_fix` | W2-D | 14 | regr-chain | 회귀 체인 |
| `260730_w2d_judge` | W2-D | 14 | regr-chain | 회귀 체인 |
| `260731_w3_p11` | W3 | 15 | baseline-of-record | stamp:BoR |
| `260731_w3_s11` | W3 | 15 | baseline-of-record | 회귀 체인 · stamp:BoR |
| `260811_w3_s11clean` | W3-fix | 15 | anchor | 앵커 |
| `260813_w4_s11tone` | W4 | 15 | current | W4 현행 웨이브 |
| `260816_w4_final33_on` | W4 | 15 | current | W4 현행 웨이브 |
| `r1_on` | W2-P3/P4 | 14 | corpus | valset.py 코퍼스 |
| `r2_on` | W2-P3/P4 | 14 | corpus | valset.py 코퍼스 · 회귀 체인 |
| `v6_rt` | W2-ladder | 14 | corpus | valset.py 코퍼스 |
| `v7_rt` | W2-ladder | 14 | corpus | valset.py 코퍼스 |
| `v8_rt` | W2-ladder | 14 | corpus | valset.py 코퍼스 |

### `scene12` — 10 라운드 / 0.48 GB

| 라운드 | 웨이브 | 컷 | 역할 | 왜 남았나 |
|---|---|---:|---|---|
| `260730_w2d_fix` | W2-D | 16 | regr-chain | 회귀 체인 |
| `260730_w2d_judge` | W2-D | 16 | regr-chain | 회귀 체인 |
| `260731_w3_l12c` | W3 | 16 | baseline-of-record | stamp:BoR |
| `260815_w4_r4batch` | W4 | 16 | current | W4 현행 웨이브 |
| `260816_w4_final33_on` | W4 | 16 | current | W4 현행 웨이브 |
| `r1_on` | W2-P3/P4 | 16 | corpus | valset.py 코퍼스 |
| `r2_on` | W2-P3/P4 | 16 | corpus | valset.py 코퍼스 · 회귀 체인 |
| `v6_rt` | W2-ladder | 15 | corpus | valset.py 코퍼스 |
| `v7_rt` | W2-ladder | 16 | corpus | valset.py 코퍼스 |
| `v8_rt` | W2-ladder | 16 | corpus | valset.py 코퍼스 |

### `scene13` — 24 라운드 / 1.15 GB

| 라운드 | 웨이브 | 컷 | 역할 | 왜 남았나 |
|---|---|---:|---|---|
| `260730_w2d_fix` | W2-D | 15 | regr-chain | 회귀 체인 |
| `260730_w2d_judge` | W2-D | 15 | regr-chain | 회귀 체인 |
| `260730_w3_s13b` | W3 | 15 | baseline-of-record | 회귀 체인 · stamp:BoR |
| `260811_w3_s13frost_c` | W3-fix | 15 | anchor | 앵커 |
| `260813_w4_s13tone` | W4 | 15 | current | W4 현행 웨이브 |
| `260814_w4_r1r2pilot` | W4 | 15 | current | W4 현행 웨이브 |
| `260815_w4_physpilot` | W4 | 15 | current | W4 현행 웨이브 |
| `260815_w4_r4batch` | W4 | 15 | current | W4 현행 웨이브 |
| `260816_w4_base_dnoff` | W4 | 15 | current | W4 현행 웨이브 |
| `260816_w4_dn_off128` | W4 | 15 | current | W4 현행 웨이브 |
| `260816_w4_dn_off256` | W4 | 15 | current | W4 현행 웨이브 |
| `260816_w4_dn_on64` | W4 | 15 | current | W4 현행 웨이브 |
| `260816_w4_final33_on` | W4 | 15 | current | W4 현행 웨이브 |
| `260816_w4_micro_dnoff` | W4 | 15 | current | W4 현행 웨이브 |
| `260816_w4_micropilot` | W4 | 15 | current | W4 현행 웨이브 |
| `260816_w4_micropilot2` | W4 | 15 | current | W4 현행 웨이브 |
| `p2dark_fast256` | W2-P2 | 3 | corpus | valset.py 코퍼스 |
| `p2dark_fast64` | W2-P2 | 3 | corpus | valset.py 코퍼스 |
| `p2dark_legacy` | W2-P2 | 3 | corpus | valset.py 코퍼스 |
| `r1_on` | W2-P3/P4 | 2 | corpus | valset.py 코퍼스 |
| `r2_on` | W2-P3/P4 | 15 | corpus | valset.py 코퍼스 · 회귀 체인 |
| `v6_rt` | W2-ladder | 15 | corpus | valset.py 코퍼스 |
| `v7_rt` | W2-ladder | 15 | corpus | valset.py 코퍼스 |
| `w2_pilot` | W2 | 15 | regr-chain | 회귀 체인 |

### `scene14` — 8 라운드 / 0.28 GB

| 라운드 | 웨이브 | 컷 | 역할 | 왜 남았나 |
|---|---|---:|---|---|
| `260730_w2d_fix` | W2-D | 13 | regr-chain | 회귀 체인 |
| `260730_w2d_judge` | W2-D | 13 | regr-chain | 회귀 체인 |
| `260731_w3_l14` | W3 | 13 | baseline-of-record | stamp:BoR |
| `260815_w4_r4batch` | W4 | 13 | current | W4 현행 웨이브 |
| `260816_w4_final33_on` | W4 | 13 | current | W4 현행 웨이브 |
| `r2_on` | W2-P3/P4 | 13 | corpus | valset.py 코퍼스 · 회귀 체인 · 앵커 |
| `v6_rt` | W2-ladder | 13 | corpus | valset.py 코퍼스 |
| `v7_rt` | W2-ladder | 13 | corpus | valset.py 코퍼스 |

### `scene15` — 11 라운드 / 0.57 GB

| 라운드 | 웨이브 | 컷 | 역할 | 왜 남았나 |
|---|---|---:|---|---|
| `260730_w2d_fix` | W2-D | 13 | regr-chain | 회귀 체인 |
| `260730_w2d_judge` | W2-D | 13 | regr-chain | 회귀 체인 |
| `260731_w3_l15` | W3 | 13 | baseline-of-record | stamp:BoR |
| `260813_w4_s15villa` | W4 | 13 | current | W4 현행 웨이브 |
| `260815_w4_hzbatch` | W4 | 13 | current | W4 현행 웨이브 |
| `260816_w4_final33_on` | W4 | 13 | current | W4 현행 웨이브 |
| `260817_w4_regfix` | W4 | 13 | current | W4 현행 웨이브 |
| `r2_on` | W2-P3/P4 | 13 | corpus | valset.py 코퍼스 · 회귀 체인 |
| `v6_rt` | W2-ladder | 13 | corpus | valset.py 코퍼스 |
| `v7_rt` | W2-ladder | 13 | corpus | valset.py 코퍼스 |
| `w2_pilot` | W2 | 13 | regr-chain | 회귀 체인 · 앵커 |

### `scene16` — 15 라운드 / 0.69 GB

| 라운드 | 웨이브 | 컷 | 역할 | 왜 남았나 |
|---|---|---:|---|---|
| `260730_w2d_fix` | W2-D | 13 | regr-chain | 회귀 체인 |
| `260730_w2d_judge` | W2-D | 13 | regr-chain | 회귀 체인 |
| `260731_w3_mb24` | W3 | 5 | regr-chain | 회귀 체인 |
| `260731_w3_s16` | W3 | 13 | baseline-of-record | 회귀 체인 · stamp:BoR |
| `260811_w3_s16under` | W3-fix | 13 | anchor | 앵커 |
| `260813_w4_s16tone` | W4 | 13 | current | W4 현행 웨이브 |
| `260814_w4_r1r2pilot` | W4 | 13 | current | W4 현행 웨이브 |
| `260815_w4_hzbatch` | W4 | 13 | current | W4 현행 웨이브 |
| `260815_w4_physpilot` | W4 | 13 | current | W4 현행 웨이브 |
| `260815_w4_r4batch` | W4 | 13 | current | W4 현행 웨이브 |
| `260816_w4_final33_on` | W4 | 13 | current | W4 현행 웨이브 |
| `260816_w4_micropilot` | W4 | 13 | current | W4 현행 웨이브 |
| `r2_on` | W2-P3/P4 | 13 | corpus | valset.py 코퍼스 · 회귀 체인 |
| `v6_rt` | W2-ladder | 13 | corpus | valset.py 코퍼스 |
| `v7_rt` | W2-ladder | 13 | corpus | valset.py 코퍼스 |

### `scene17` — 10 라운드 / 0.51 GB

| 라운드 | 웨이브 | 컷 | 역할 | 왜 남았나 |
|---|---|---:|---|---|
| `260730_w2d_fix` | W2-D | 14 | regr-chain | 회귀 체인 |
| `260730_w2d_judge` | W2-D | 14 | regr-chain | 회귀 체인 |
| `260731_w3_s17` | W3 | 14 | baseline-of-record | 회귀 체인 · stamp:BoR |
| `260815_w4_hzbatch` | W4 | 14 | current | W4 현행 웨이브 |
| `260815_w4_r4batch` | W4 | 14 | current | W4 현행 웨이브 |
| `260816_w4_final33_on` | W4 | 14 | current | W4 현행 웨이브 |
| `r2_on` | W2-P3/P4 | 14 | corpus | valset.py 코퍼스 · 회귀 체인 |
| `v6_rt` | W2-ladder | 14 | corpus | valset.py 코퍼스 |
| `v7_rt` | W2-ladder | 14 | corpus | valset.py 코퍼스 |
| `v8_rt` | W2-ladder | 14 | corpus | valset.py 코퍼스 |

### `scene18` — 10 라운드 / 0.40 GB

| 라운드 | 웨이브 | 컷 | 역할 | 왜 남았나 |
|---|---|---:|---|---|
| `260730_w2d_fix` | W2-D | 14 | regr-chain | 회귀 체인 |
| `260730_w2d_judge` | W2-D | 14 | regr-chain | 회귀 체인 |
| `260731_w3_s18` | W3 | 14 | regr-chain | 회귀 체인 |
| `260815_w4_r4batch` | W4 | 14 | current | W4 현행 웨이브 |
| `260816_w4_final33_on` | W4 | 14 | current | W4 현행 웨이브 |
| `260816_w4_w8deck` | W4 | 14 | current | W4 현행 웨이브 |
| `r2_on` | W2-P3/P4 | 14 | corpus | valset.py 코퍼스 · 회귀 체인 |
| `v6_rt` | W2-ladder | 13 | corpus | valset.py 코퍼스 |
| `v7_pt` | W2-ladder | 14 | anchor | 앵커 |
| `v7_rt` | W2-ladder | 14 | corpus | valset.py 코퍼스 |

### `scene19` — 8 라운드 / 0.39 GB

| 라운드 | 웨이브 | 컷 | 역할 | 왜 남았나 |
|---|---|---:|---|---|
| `260730_w2d_fix` | W2-D | 16 | regr-chain | 회귀 체인 |
| `260730_w2d_judge` | W2-D | 16 | regr-chain | 회귀 체인 |
| `260731_w3_l19` | W3 | 16 | baseline-of-record | stamp:BoR |
| `260815_w4_r4batch` | W4 | 16 | current | W4 현행 웨이브 |
| `260816_w4_final33_on` | W4 | 16 | current | W4 현행 웨이브 |
| `r2_on` | W2-P3/P4 | 16 | corpus | valset.py 코퍼스 · 회귀 체인 |
| `v6_rt` | W2-ladder | 16 | corpus | valset.py 코퍼스 |
| `v7_rt` | W2-ladder | 16 | corpus | valset.py 코퍼스 |

### `scene20` — 7 라운드 / 0.38 GB

| 라운드 | 웨이브 | 컷 | 역할 | 왜 남았나 |
|---|---|---:|---|---|
| `260730_w2d_fix` | W2-D | 13 | regr-chain | 회귀 체인 |
| `260730_w2d_judge` | W2-D | 13 | regr-chain | 회귀 체인 |
| `260731_w3_l20c` | W3 | 13 | baseline-of-record | stamp:BoR |
| `260816_w4_final33_on` | W4 | 13 | current | W4 현행 웨이브 |
| `r2_on` | W2-P3/P4 | 13 | corpus | valset.py 코퍼스 · 회귀 체인 |
| `v6_rt` | W2-ladder | 13 | corpus | valset.py 코퍼스 |
| `v7_rt` | W2-ladder | 13 | corpus | valset.py 코퍼스 |

### `scene21` — 11 라운드 / 0.47 GB

| 라운드 | 웨이브 | 컷 | 역할 | 왜 남았나 |
|---|---|---:|---|---|
| `260730_w2d_fix` | W2-D | 13 | regr-chain | 회귀 체인 |
| `260730_w2d_judge` | W2-D | 13 | regr-chain | 회귀 체인 |
| `260731_w3_l21` | W3 | 13 | baseline-of-record | stamp:BoR |
| `260813_w4_s21civic` | W4 | 13 | current | W4 현행 웨이브 |
| `260814_w4_r1r2pilot` | W4 | 13 | current | W4 현행 웨이브 |
| `260815_w4_hzbatch` | W4 | 13 | current | W4 현행 웨이브 |
| `260815_w4_r4batch` | W4 | 13 | current | W4 현행 웨이브 |
| `260816_w4_final33_on` | W4 | 13 | current | W4 현행 웨이브 |
| `r2_on` | W2-P3/P4 | 13 | corpus | valset.py 코퍼스 · 회귀 체인 |
| `v6_rt` | W2-ladder | 13 | corpus | valset.py 코퍼스 |
| `v7_rt` | W2-ladder | 13 | corpus | valset.py 코퍼스 |

### `sceneC1` — 9 라운드 / 0.40 GB

| 라운드 | 웨이브 | 컷 | 역할 | 왜 남았나 |
|---|---|---:|---|---|
| `260730_w2d_fix` | W2-D | 13 | regr-chain | 회귀 체인 |
| `260730_w2d_judge` | W2-D | 13 | regr-chain | 회귀 체인 |
| `260814_w4_r1r2pilot` | W4 | 13 | current | W4 현행 웨이브 |
| `260815_w4_hzbatch` | W4 | 13 | current | W4 현행 웨이브 |
| `260816_w4_final33_on` | W4 | 13 | current | W4 현행 웨이브 |
| `ctx1` | W2-ctx | 13 | corpus | valset.py 코퍼스 |
| `ctx2` | W2-ctx | 13 | corpus | valset.py 코퍼스 |
| `r2_on` | W2-P3/P4 | 13 | corpus | valset.py 코퍼스 · 회귀 체인 |
| `r2b_on` | W2-P3/P4 | 13 | regr-chain | 회귀 체인 |

### `sceneC2` — 13 라운드 / 0.79 GB

| 라운드 | 웨이브 | 컷 | 역할 | 왜 남았나 |
|---|---|---:|---|---|
| `260730_w2d_fix` | W2-D | 13 | regr-chain | 회귀 체인 |
| `260730_w2d_judge` | W2-D | 13 | regr-chain | 회귀 체인 |
| `260731_w3_cb2` | W3 | 5 | regr-chain | 회귀 체인 |
| `260815_w4_r4batch` | W4 | 13 | current | W4 현행 웨이브 |
| `260816_w4_final33_on` | W4 | 13 | current | W4 현행 웨이브 |
| `balust` | W2-nearfield | 13 | corpus | valset.py 코퍼스 |
| `ctx1` | W2-ctx | 13 | corpus | valset.py 코퍼스 |
| `ctx2` | W2-ctx | 13 | corpus | valset.py 코퍼스 |
| `fix1` | W2-nearfield | 13 | corpus | valset.py 코퍼스 |
| `handrail` | W2-nearfield | 13 | corpus | valset.py 코퍼스 |
| `leaf3d` | W2-nearfield | 13 | corpus | valset.py 코퍼스 |
| `r2_on` | W2-P3/P4 | 13 | corpus | valset.py 코퍼스 · 회귀 체인 |
| `w2c_g2` | W2 | 13 | regr-chain | 회귀 체인 |

### `sceneC4` — 7 라운드 / 0.36 GB

| 라운드 | 웨이브 | 컷 | 역할 | 왜 남았나 |
|---|---|---:|---|---|
| `260730_w2d_fix` | W2-D | 13 | regr-chain | 회귀 체인 |
| `260730_w2d_judge` | W2-D | 13 | regr-chain | 회귀 체인 |
| `260815_w4_r4batch` | W4 | 13 | current | W4 현행 웨이브 |
| `260816_w4_final33_on` | W4 | 13 | current | W4 현행 웨이브 |
| `ctx1` | W2-ctx | 13 | corpus | valset.py 코퍼스 |
| `ctx2` | W2-ctx | 13 | corpus | valset.py 코퍼스 |
| `r2_on` | W2-P3/P4 | 13 | corpus | valset.py 코퍼스 · 회귀 체인 |

### `sceneD1` — 7 라운드 / 0.35 GB

| 라운드 | 웨이브 | 컷 | 역할 | 왜 남았나 |
|---|---|---:|---|---|
| `260730_w2d_fix` | W2-D | 14 | regr-chain | 회귀 체인 |
| `260730_w2d_judge` | W2-D | 14 | regr-chain | 회귀 체인 |
| `260815_w4_r4batch` | W4 | 14 | current | W4 현행 웨이브 |
| `260816_w4_final33_on` | W4 | 14 | current | W4 현행 웨이브 |
| `ctx1` | W2-ctx | 14 | corpus | valset.py 코퍼스 |
| `ctx2` | W2-ctx | 14 | corpus | valset.py 코퍼스 |
| `r2_on` | W2-P3/P4 | 14 | corpus | valset.py 코퍼스 · 회귀 체인 |

### `sceneD2` — 7 라운드 / 0.38 GB

| 라운드 | 웨이브 | 컷 | 역할 | 왜 남았나 |
|---|---|---:|---|---|
| `260730_w2d_fix` | W2-D | 13 | regr-chain | 회귀 체인 |
| `260730_w2d_judge` | W2-D | 13 | regr-chain | 회귀 체인 |
| `260815_w4_r4batch` | W4 | 13 | current | W4 현행 웨이브 |
| `260816_w4_final33_on` | W4 | 13 | current | W4 현행 웨이브 |
| `ctx1` | W2-ctx | 13 | corpus | valset.py 코퍼스 |
| `ctx2` | W2-ctx | 13 | corpus | valset.py 코퍼스 |
| `r2_on` | W2-P3/P4 | 13 | corpus | valset.py 코퍼스 · 회귀 체인 |

### `sceneD3` — 18 라운드 / 0.71 GB

| 라운드 | 웨이브 | 컷 | 역할 | 왜 남았나 |
|---|---|---:|---|---|
| `260730_w2d_fix` | W2-D | 14 | regr-chain | 회귀 체인 |
| `260730_w2d_judge` | W2-D | 14 | regr-chain | 회귀 체인 |
| `260816_w4_final33_on` | W4 | 14 | current | W4 현행 웨이브 |
| `ctx1` | W2-ctx | 14 | corpus | valset.py 코퍼스 |
| `ctx2` | W2-ctx | 14 | corpus | valset.py 코퍼스 |
| `p2ctrl_a` | W2-P2 | 3 | corpus | valset.py 코퍼스 |
| `p2ctrl_b` | W2-P2 | 3 | corpus | valset.py 코퍼스 |
| `p2det_a` | W2-P2 | 3 | corpus | valset.py 코퍼스 |
| `p2det_b` | W2-P2 | 3 | corpus | valset.py 코퍼스 |
| `p2g1_off` | W2-P2 | 14 | corpus | valset.py 코퍼스 |
| `p2g1_on` | W2-P2 | 14 | corpus | valset.py 코퍼스 |
| `p2g2_off` | W2-P2 | 14 | corpus | valset.py 코퍼스 |
| `p2g2_on` | W2-P2 | 14 | corpus | valset.py 코퍼스 |
| `p2g3_off` | W2-P2 | 14 | corpus | valset.py 코퍼스 |
| `p2g3_on` | W2-P2 | 14 | corpus | valset.py 코퍼스 |
| `r2_on` | W2-P3/P4 | 14 | corpus | valset.py 코퍼스 · 회귀 체인 |
| `sceneD3_ptfast` | W2-mode | 3 | corpus | valset.py 코퍼스 |
| `sceneD3_ptlegacy` | W2-mode | 3 | corpus | valset.py 코퍼스 |

### `sceneD4` — 12 라운드 / 0.30 GB

| 라운드 | 웨이브 | 컷 | 역할 | 왜 남았나 |
|---|---|---:|---|---|
| `260730_w2d_fix` | W2-D | 13 | regr-chain | 회귀 체인 |
| `260730_w2d_judge` | W2-D | 13 | regr-chain | 회귀 체인 |
| `260814_w4_d4iter` | W4 | 13 | current | W4 현행 웨이브 |
| `260814_w4_r1r2pilot` | W4 | 13 | current | W4 현행 웨이브 |
| `260815_w4_hzbatch` | W4 | 13 | current | W4 현행 웨이브 |
| `260816_w4_final33_on` | W4 | 13 | current | W4 현행 웨이브 |
| `ctx1` | W2-ctx | 13 | corpus | valset.py 코퍼스 |
| `ctx2` | W2-ctx | 13 | corpus | valset.py 코퍼스 |
| `p2dark_fast256` | W2-P2 | 3 | corpus | valset.py 코퍼스 |
| `p2dark_fast64` | W2-P2 | 3 | corpus | valset.py 코퍼스 |
| `p2dark_legacy` | W2-P2 | 3 | corpus | valset.py 코퍼스 |
| `r2_on` | W2-P3/P4 | 13 | corpus | valset.py 코퍼스 · 회귀 체인 |

### `sceneN1` — 8 라운드 / 0.39 GB

| 라운드 | 웨이브 | 컷 | 역할 | 왜 남았나 |
|---|---|---:|---|---|
| `260730_w2d_fix` | W2-D | 13 | regr-chain | 회귀 체인 |
| `260730_w2d_judge` | W2-D | 13 | regr-chain | 회귀 체인 |
| `260815_w4_hzbatch` | W4 | 13 | current | W4 현행 웨이브 |
| `260815_w4_r4batch` | W4 | 13 | current | W4 현행 웨이브 |
| `260816_w4_final33_on` | W4 | 13 | current | W4 현행 웨이브 |
| `ctx1` | W2-ctx | 13 | corpus | valset.py 코퍼스 |
| `ctx2` | W2-ctx | 13 | corpus | valset.py 코퍼스 |
| `r2_on` | W2-P3/P4 | 13 | corpus | valset.py 코퍼스 · 회귀 체인 |

### `sceneN2` — 8 라운드 / 0.46 GB

| 라운드 | 웨이브 | 컷 | 역할 | 왜 남았나 |
|---|---|---:|---|---|
| `260730_w2d_fix` | W2-D | 13 | regr-chain | 회귀 체인 |
| `260730_w2d_judge` | W2-D | 13 | regr-chain | 회귀 체인 |
| `260730_w3_n2clean` | W3 | 13 | regr-chain | 회귀 체인 |
| `260815_w4_hzbatch` | W4 | 13 | current | W4 현행 웨이브 |
| `260816_w4_final33_on` | W4 | 13 | current | W4 현행 웨이브 |
| `ctx1` | W2-ctx | 13 | corpus | valset.py 코퍼스 |
| `ctx2` | W2-ctx | 13 | corpus | valset.py 코퍼스 |
| `r2_on` | W2-P3/P4 | 13 | corpus | valset.py 코퍼스 · 회귀 체인 |

### `sceneN3` — 8 라운드 / 0.43 GB

| 라운드 | 웨이브 | 컷 | 역할 | 왜 남았나 |
|---|---|---:|---|---|
| `260730_w2d_fix` | W2-D | 13 | regr-chain | 회귀 체인 |
| `260730_w2d_judge` | W2-D | 13 | regr-chain | 회귀 체인 |
| `260813_w4_n3wall` | W4 | 13 | current | W4 현행 웨이브 |
| `260815_w4_hzbatch` | W4 | 13 | current | W4 현행 웨이브 |
| `260816_w4_final33_on` | W4 | 13 | current | W4 현행 웨이브 |
| `ctx1` | W2-ctx | 13 | corpus | valset.py 코퍼스 |
| `ctx2` | W2-ctx | 13 | corpus | valset.py 코퍼스 |
| `r2_on` | W2-P3/P4 | 13 | corpus | valset.py 코퍼스 · 회귀 체인 |

### `sceneN4` — 7 라운드 / 0.33 GB

| 라운드 | 웨이브 | 컷 | 역할 | 왜 남았나 |
|---|---|---:|---|---|
| `260730_w2d_fix` | W2-D | 13 | regr-chain | 회귀 체인 |
| `260730_w2d_judge` | W2-D | 13 | regr-chain | 회귀 체인 |
| `260816_w4_final33_on` | W4 | 13 | current | W4 현행 웨이브 |
| `ctx1` | W2-ctx | 13 | corpus | valset.py 코퍼스 |
| `ctx2` | W2-ctx | 13 | corpus | valset.py 코퍼스 |
| `r2_on` | W2-P3/P4 | 13 | corpus | valset.py 코퍼스 · 회귀 체인 |
| `wall` | W2-nearfield | 13 | regr-chain | 회귀 체인 |

### `sceneN5` — 7 라운드 / 0.35 GB

| 라운드 | 웨이브 | 컷 | 역할 | 왜 남았나 |
|---|---|---:|---|---|
| `260730_w2d_fix` | W2-D | 13 | regr-chain | 회귀 체인 |
| `260730_w2d_judge` | W2-D | 13 | regr-chain | 회귀 체인 |
| `260816_w4_final33_on` | W4 | 13 | current | W4 현행 웨이브 |
| `ctx1` | W2-ctx | 13 | corpus | valset.py 코퍼스 |
| `ctx2` | W2-ctx | 13 | corpus | valset.py 코퍼스 |
| `r2_on` | W2-P3/P4 | 13 | corpus | valset.py 코퍼스 · 회귀 체인 |
| `w2_pilot` | W2 | 13 | regr-chain | 회귀 체인 |

## 3. 아카이브 트리 — `_archive/<wave>/<scene>/<round>`

옮기기 전 경로를 같이 적는다. 2026-08-27 이전에 쓰인 보고서는 옛 경로를 인용하므로 **라운드 이름으로 이 표를 검색**하면 지금 위치가 나온다. 여기 있는 라운드는 `valset.py`·회귀 체인·BoR 스탬프·앵커 어디에도 걸리지 않는다(그래서 옮길 수 있었다).

### `_archive/w2/` — W2 (P2 · P3/P4 · ladder · ctx · mode · nearfield · special) · 51 라운드 / 1.97 GB

| 씬 | 라운드 | 컷 | MB | 예전 경로 |
|---|---|---:|---:|---|
| `scene01` | `p2g4_on` | 13 | 50 | `look_check/scene01/p2g4_on` |
| `scene01` | `pair_cues_off` | 3 | 7 | `look_check/scene01/pair_cues_off` |
| `scene02` | `_cb7_r1_glazing_rejected` | 13 | 43 | `look_check/scene02/_cb7_r1_glazing_rejected` |
| `scene02` | `v7_pt` | 13 | 50 | `look_check/scene02/v7_pt` |
| `scene03` | `v7_pt` | 16 | 53 | `look_check/scene03/v7_pt` |
| `scene04` | `v7_pt` | 13 | 50 | `look_check/scene04/v7_pt` |
| `scene05` | `_gt6_judge_baseline` | 13 | 51 | `look_check/scene05/_gt6_judge_baseline` |
| `scene05` | `v8_pt` | 13 | 50 | `look_check/scene05/v8_pt` |
| `scene06` | `_gt6_judge_baseline` | 15 | 61 | `look_check/scene06/_gt6_judge_baseline` |
| `scene06` | `v8_pt` | 15 | 49 | `look_check/scene06/v8_pt` |
| `scene07` | `p2g4_on` | 14 | 65 | `look_check/scene07/p2g4_on` |
| `scene08` | `v7_pt` | 15 | 49 | `look_check/scene08/v7_pt` |
| `scene09` | `v8_rt2` | 14 | 36 | `look_check/scene09/v8_rt2` |
| `scene10` | `v8_pt` | 14 | 68 | `look_check/scene10/v8_pt` |
| `scene11` | `v8_pt` | 14 | 49 | `look_check/scene11/v8_pt` |
| `scene12` | `v8_pt` | 16 | 48 | `look_check/scene12/v8_pt` |
| `scene13` | `_gt6_judge_baseline` | 15 | 44 | `look_check/scene13/_gt6_judge_baseline` |
| `scene13` | `v7_pt` | 15 | 44 | `look_check/scene13/v7_pt` |
| `scene14` | `v7_pt` | 13 | 28 | `look_check/scene14/v7_pt` |
| `scene15` | `v7_pt` | 13 | 47 | `look_check/scene15/v7_pt` |
| `scene16` | `v7_pt` | 13 | 50 | `look_check/scene16/v7_pt` |
| `scene17` | `v8_pt` | 14 | 42 | `look_check/scene17/v8_pt` |
| `scene19` | `_gt6_judge_baseline` | 16 | 57 | `look_check/scene19/_gt6_judge_baseline` |
| `scene19` | `r4` | 14 | 45 | `look_check/scene19/r4` |
| `scene19` | `r5` | 15 | 38 | `look_check/scene19/r5` |
| `scene19` | `v7_pt` | 16 | 41 | `look_check/scene19/v7_pt` |
| `scene20` | `v7_pt` | 13 | 55 | `look_check/scene20/v7_pt` |
| `scene21` | `v7_pt` | 13 | 45 | `look_check/scene21/v7_pt` |
| `sceneC1` | `ctx1_pt` | 3 | 5 | `look_check/sceneC1/ctx1_pt` |
| `sceneC1` | `ctx2_pt` | 3 | 5 | `look_check/sceneC1/ctx2_pt` |
| `sceneC1` | `r3` | 13 | 26 | `look_check/sceneC1/r3` |
| `sceneC1` | `r3_pt` | 4 | 6 | `look_check/sceneC1/r3_pt` |
| `sceneC1` | `r4` | 13 | 27 | `look_check/sceneC1/r4` |
| `sceneC1` | `r4_pt` | 4 | 6 | `look_check/sceneC1/r4_pt` |
| `sceneC4` | `ctx1_pt` | 3 | 10 | `look_check/sceneC4/ctx1_pt` |
| `sceneC4` | `ctx2_pt` | 3 | 10 | `look_check/sceneC4/ctx2_pt` |
| `sceneD2` | `r1` | 13 | 58 | `look_check/sceneD2/r1` |
| `sceneD2` | `r1_pt` | 13 | 56 | `look_check/sceneD2/r1_pt` |
| `sceneD2` | `r2` | 13 | 58 | `look_check/sceneD2/r2` |
| `sceneD2` | `r2_pt` | 13 | 56 | `look_check/sceneD2/r2_pt` |
| `sceneD3` | `p0_base_pt` | 14 | 51 | `look_check/sceneD3/p0_base_pt` |
| `sceneD3` | `p2g4_on` | 14 | 63 | `look_check/sceneD3/p2g4_on` |
| `sceneD3` | `r2` | 14 | 55 | `look_check/sceneD3/r2` |
| `sceneD3` | `r3` | 14 | 55 | `look_check/sceneD3/r3` |
| `sceneD3` | `r4` | 3 | 10 | `look_check/sceneD3/r4` |
| `sceneD3` | `r5` | 2 | 6 | `look_check/sceneD3/r5` |
| `sceneD4` | `ctx1_pt` | 13 | 31 | `look_check/sceneD4/ctx1_pt` |
| `sceneD4` | `ctx2_pt` | 13 | 31 | `look_check/sceneD4/ctx2_pt` |
| `sceneD4` | `r1` | 13 | 6 | `look_check/sceneD4/r1` |
| `sceneD4` | `r1_pt` | 13 | 9 | `look_check/sceneD4/r1_pt` |
| `sceneD4` | `r2_pt` | 13 | 30 | `look_check/sceneD4/r2_pt` |

### `_archive/w2d/` — W2-D (`260730_w2d_*` · `260730_lcfreeze_*`) · 8 라운드 / 0.40 GB

| 씬 | 라운드 | 컷 | MB | 예전 경로 |
|---|---|---:|---:|---|
| `scene02` | `260730_lcfreeze_post` | 13 | 47 | `look_check/scene02/260730_lcfreeze_post` |
| `scene02` | `260730_lcfreeze_pre` | 13 | 47 | `look_check/scene02/260730_lcfreeze_pre` |
| `scene04` | `260730_lcfreeze_post` | 13 | 59 | `look_check/scene04/260730_lcfreeze_post` |
| `scene04` | `260730_lcfreeze_pre` | 13 | 59 | `look_check/scene04/260730_lcfreeze_pre` |
| `sceneN1` | `260730_lcfreeze_post` | 13 | 49 | `look_check/sceneN1/260730_lcfreeze_post` |
| `sceneN1` | `260730_lcfreeze_pre` | 13 | 49 | `look_check/sceneN1/260730_lcfreeze_pre` |
| `sceneN4` | `260730_lcfreeze_post` | 13 | 48 | `look_check/sceneN4/260730_lcfreeze_post` |
| `sceneN4` | `260730_lcfreeze_pre` | 13 | 48 | `look_check/sceneN4/260730_lcfreeze_pre` |

### `_archive/w3/` — W3 (`260730/260731_w3_*`, `w3r` 포함) · 72 라운드 / 3.52 GB

| 씬 | 라운드 | 컷 | MB | 예전 경로 |
|---|---|---:|---:|---|
| `scene01` | `260731_w3_full` | 13 | 48 | `look_check/scene01/260731_w3_full` |
| `scene01` | `260731_w3_mb24_pre` | 5 | 19 | `look_check/scene01/260731_w3_mb24_pre` |
| `scene01` | `260731_w3_s01_pre` | 13 | 52 | `look_check/scene01/260731_w3_s01_pre` |
| `scene02` | `260731_w3_cb7` | 13 | 44 | `look_check/scene02/260731_w3_cb7` |
| `scene02` | `260731_w3_cb7_pre` | 13 | 46 | `look_check/scene02/260731_w3_cb7_pre` |
| `scene02` | `260731_w3_full` | 13 | 45 | `look_check/scene02/260731_w3_full` |
| `scene02` | `260731_w3_gt25_pre` | 13 | 44 | `look_check/scene02/260731_w3_gt25_pre` |
| `scene02` | `260731_w3_mb24_pre` | 5 | 18 | `look_check/scene02/260731_w3_mb24_pre` |
| `scene03` | `260731_w3_full` | 16 | 61 | `look_check/scene03/260731_w3_full` |
| `scene04` | `260731_w3_full` | 13 | 72 | `look_check/scene04/260731_w3_full` |
| `scene04` | `260731_w3_s04b` | 13 | 69 | `look_check/scene04/260731_w3_s04b` |
| `scene05` | `260731_w3_full` | 13 | 53 | `look_check/scene05/260731_w3_full` |
| `scene05` | `260731_w3_l05_pre` | 13 | 52 | `look_check/scene05/260731_w3_l05_pre` |
| `scene05` | `260731_w3_l05b` | 13 | 50 | `look_check/scene05/260731_w3_l05b` |
| `scene05` | `260731_w3_l05c` | 13 | 53 | `look_check/scene05/260731_w3_l05c` |
| `scene06` | `260731_w3_full` | 15 | 54 | `look_check/scene06/260731_w3_full` |
| `scene07` | `260731_w3_full` | 14 | 65 | `look_check/scene07/260731_w3_full` |
| `scene08` | `260731_w3_full` | 15 | 54 | `look_check/scene08/260731_w3_full` |
| `scene08` | `260731_w3_s08` | 15 | 49 | `look_check/scene08/260731_w3_s08` |
| `scene08` | `260731_w3_s08b` | 15 | 53 | `look_check/scene08/260731_w3_s08b` |
| `scene08` | `260731_w3_s08c` | 15 | 53 | `look_check/scene08/260731_w3_s08c` |
| `scene09` | `260731_w3_full` | 18 | 48 | `look_check/scene09/260731_w3_full` |
| `scene09` | `260731_w3_mb24_pre` | 5 | 12 | `look_check/scene09/260731_w3_mb24_pre` |
| `scene10` | `260731_w3_full` | 14 | 74 | `look_check/scene10/260731_w3_full` |
| `scene10` | `260731_w3_pre10` | 5 | 23 | `look_check/scene10/260731_w3_pre10` |
| `scene10` | `260731_w3_pre10c` | 14 | 74 | `look_check/scene10/260731_w3_pre10c` |
| `scene10` | `260731_w3_s10` | 14 | 74 | `look_check/scene10/260731_w3_s10` |
| `scene11` | `260731_w3_full` | 15 | 58 | `look_check/scene11/260731_w3_full` |
| `scene11` | `260731_w3_p11_pilot0` | 15 | 58 | `look_check/scene11/260731_w3_p11_pilot0` |
| `scene12` | `260731_w3_full` | 16 | 49 | `look_check/scene12/260731_w3_full` |
| `scene12` | `260731_w3_l12` | 16 | 49 | `look_check/scene12/260731_w3_l12` |
| `scene12` | `260731_w3_l12_mat` | 16 | 49 | `look_check/scene12/260731_w3_l12_mat` |
| `scene12` | `260731_w3_l12_pre` | 16 | 47 | `look_check/scene12/260731_w3_l12_pre` |
| `scene12` | `260731_w3_l12b` | 16 | 49 | `look_check/scene12/260731_w3_l12b` |
| `scene13` | `260731_w3_full` | 15 | 53 | `look_check/scene13/260731_w3_full` |
| `scene14` | `260731_w3_full` | 13 | 36 | `look_check/scene14/260731_w3_full` |
| `scene14` | `260731_w3_l14_bk` | 13 | 35 | `look_check/scene14/260731_w3_l14_bk` |
| `scene14` | `260731_w3_l14_p1` | 13 | 36 | `look_check/scene14/260731_w3_l14_p1` |
| `scene14` | `260731_w3_l14_pre` | 13 | 36 | `look_check/scene14/260731_w3_l14_pre` |
| `scene15` | `260731_w3_full` | 13 | 52 | `look_check/scene15/260731_w3_full` |
| `scene15` | `260731_w3_l15_pre` | 13 | 52 | `look_check/scene15/260731_w3_l15_pre` |
| `scene16` | `260731_w3_full` | 13 | 49 | `look_check/scene16/260731_w3_full` |
| `scene16` | `260731_w3_mb24_pre` | 5 | 20 | `look_check/scene16/260731_w3_mb24_pre` |
| `scene17` | `260731_w3_full` | 14 | 50 | `look_check/scene17/260731_w3_full` |
| `scene17` | `260731_w3_s17_pre` | 14 | 50 | `look_check/scene17/260731_w3_s17_pre` |
| `scene17` | `260731_w3_sb17` | 5 | 20 | `look_check/scene17/260731_w3_sb17` |
| `scene17` | `260731_w3_sb17_pre` | 5 | 20 | `look_check/scene17/260731_w3_sb17_pre` |
| `scene18` | `260731_w3_full` | 14 | 41 | `look_check/scene18/260731_w3_full` |
| `scene18` | `260731_w3_s18b` | 14 | 40 | `look_check/scene18/260731_w3_s18b` |
| `scene18` | `260731_w3_s18c` | 14 | 40 | `look_check/scene18/260731_w3_s18c` |
| `scene18` | `260731_w3_s18d` | 14 | 41 | `look_check/scene18/260731_w3_s18d` |
| `scene18` | `260731_w3_s18e` | 14 | 41 | `look_check/scene18/260731_w3_s18e` |
| `scene19` | `260731_w3_full` | 16 | 57 | `look_check/scene19/260731_w3_full` |
| `scene19` | `260731_w3_l19_pre` | 16 | 57 | `look_check/scene19/260731_w3_l19_pre` |
| `scene20` | `260730_w3r_bldgab` | 0 | 156 | `look_check/scene20/260730_w3r_bldgab` |
| `scene20` | `260731_w3_full` | 13 | 54 | `look_check/scene20/260731_w3_full` |
| `scene20` | `260731_w3_l20` | 13 | 48 | `look_check/scene20/260731_w3_l20` |
| `scene20` | `260731_w3_l20b` | 13 | 54 | `look_check/scene20/260731_w3_l20b` |
| `scene21` | `260731_w3_full` | 13 | 40 | `look_check/scene21/260731_w3_full` |
| `scene21` | `260731_w3_l21_pre` | 13 | 47 | `look_check/scene21/260731_w3_l21_pre` |
| `sceneC1` | `260731_w3_full` | 13 | 53 | `look_check/sceneC1/260731_w3_full` |
| `sceneC2` | `260731_w3_full` | 13 | 65 | `look_check/sceneC2/260731_w3_full` |
| `sceneC4` | `260731_w3_full` | 13 | 51 | `look_check/sceneC4/260731_w3_full` |
| `sceneD1` | `260731_w3_full` | 14 | 52 | `look_check/sceneD1/260731_w3_full` |
| `sceneD2` | `260731_w3_full` | 13 | 54 | `look_check/sceneD2/260731_w3_full` |
| `sceneD3` | `260731_w3_full` | 14 | 63 | `look_check/sceneD3/260731_w3_full` |
| `sceneD4` | `260731_w3_full` | 13 | 31 | `look_check/sceneD4/260731_w3_full` |
| `sceneN1` | `260731_w3_full` | 13 | 49 | `look_check/sceneN1/260731_w3_full` |
| `sceneN2` | `260731_w3_full` | 13 | 57 | `look_check/sceneN2/260731_w3_full` |
| `sceneN3` | `260731_w3_full` | 13 | 55 | `look_check/sceneN3/260731_w3_full` |
| `sceneN4` | `260731_w3_full` | 13 | 48 | `look_check/sceneN4/260731_w3_full` |
| `sceneN5` | `260731_w3_full` | 13 | 50 | `look_check/sceneN5/260731_w3_full` |

### `_archive/w3fix/` — W3-fix (`260805`~`260811_w3_*`) · 131 라운드 / 4.28 GB

| 씬 | 라운드 | 컷 | MB | 예전 경로 |
|---|---|---:|---:|---|
| `scene01` | `260805_w3_doctrine` | 13 | 48 | `look_check/scene01/260805_w3_doctrine` |
| `scene01` | `260806_w3_allview4` | 4 | 14 | `look_check/scene01/260806_w3_allview4` |
| `scene01` | `260806_w3_allview5` | 4 | 13 | `look_check/scene01/260806_w3_allview5` |
| `scene01` | `260806_w3_fixqueue` | 13 | 48 | `look_check/scene01/260806_w3_fixqueue` |
| `scene01` | `260806_w3_fixqueue2` | 13 | 47 | `look_check/scene01/260806_w3_fixqueue2` |
| `scene02` | `260805_w3_hedgeswap` | 13 | 45 | `look_check/scene02/260805_w3_hedgeswap` |
| `scene02` | `260806_w3_allview4` | 4 | 13 | `look_check/scene02/260806_w3_allview4` |
| `scene02` | `260806_w3_allview5` | 4 | 13 | `look_check/scene02/260806_w3_allview5` |
| `scene03` | `260806_w3_allview4` | 4 | 13 | `look_check/scene03/260806_w3_allview4` |
| `scene03` | `260806_w3_allview5` | 4 | 13 | `look_check/scene03/260806_w3_allview5` |
| `scene03` | `260806_w3_fixqueue2` | 16 | 62 | `look_check/scene03/260806_w3_fixqueue2` |
| `scene03` | `260806_w3_s03probe` | 16 | 62 | `look_check/scene03/260806_w3_s03probe` |
| `scene03` | `260807_w3_fixqueue3` | 16 | 63 | `look_check/scene03/260807_w3_fixqueue3` |
| `scene04` | `260806_w3_allview4` | 4 | 22 | `look_check/scene04/260806_w3_allview4` |
| `scene05` | `260805_w3_doctrine` | 13 | 53 | `look_check/scene05/260805_w3_doctrine` |
| `scene05` | `260805_w3_hedgeswap` | 13 | 53 | `look_check/scene05/260805_w3_hedgeswap` |
| `scene05` | `260806_w3_allview4` | 4 | 16 | `look_check/scene05/260806_w3_allview4` |
| `scene05` | `260806_w3_allview5` | 4 | 16 | `look_check/scene05/260806_w3_allview5` |
| `scene05` | `260806_w3_fixqueue` | 13 | 53 | `look_check/scene05/260806_w3_fixqueue` |
| `scene05` | `260806_w3_fixqueue2` | 13 | 53 | `look_check/scene05/260806_w3_fixqueue2` |
| `scene06` | `260805_w3_doctrine` | 15 | 54 | `look_check/scene06/260805_w3_doctrine` |
| `scene06` | `260806_w3_allview4` | 4 | 12 | `look_check/scene06/260806_w3_allview4` |
| `scene06` | `260806_w3_allview5` | 4 | 12 | `look_check/scene06/260806_w3_allview5` |
| `scene06` | `260806_w3_fixqueue` | 15 | 50 | `look_check/scene06/260806_w3_fixqueue` |
| `scene06` | `260806_w3_fixqueue2` | 15 | 48 | `look_check/scene06/260806_w3_fixqueue2` |
| `scene06` | `260807_w3_fixqueue3` | 15 | 49 | `look_check/scene06/260807_w3_fixqueue3` |
| `scene06` | `260810_w3_s06collar` | 15 | 48 | `look_check/scene06/260810_w3_s06collar` |
| `scene06` | `260810_w3_s06direct` | 15 | 48 | `look_check/scene06/260810_w3_s06direct` |
| `scene06` | `260810_w3_s06endstair` | 15 | 43 | `look_check/scene06/260810_w3_s06endstair` |
| `scene06` | `260811_w3_s06bay14` | 15 | 44 | `look_check/scene06/260811_w3_s06bay14` |
| `scene06` | `260811_w3_s06ease` | 15 | 44 | `look_check/scene06/260811_w3_s06ease` |
| `scene06` | `260811_w3_s06glass` | 15 | 44 | `look_check/scene06/260811_w3_s06glass` |
| `scene06` | `260811_w3_s06sweep` | 15 | 44 | `look_check/scene06/260811_w3_s06sweep` |
| `scene06` | `260811_w3_s06trim` | 15 | 42 | `look_check/scene06/260811_w3_s06trim` |
| `scene06` | `260811_w3_s06weld` | 15 | 42 | `look_check/scene06/260811_w3_s06weld` |
| `scene06` | `260811_w3_s06wide` | 15 | 42 | `look_check/scene06/260811_w3_s06wide` |
| `scene07` | `260806_w3_allview4` | 4 | 17 | `look_check/scene07/260806_w3_allview4` |
| `scene07` | `260806_w3_allview5` | 4 | 17 | `look_check/scene07/260806_w3_allview5` |
| `scene07` | `260806_w3_fixqueue2` | 14 | 65 | `look_check/scene07/260806_w3_fixqueue2` |
| `scene08` | `260806_w3_allview4` | 4 | 15 | `look_check/scene08/260806_w3_allview4` |
| `scene08` | `260806_w3_allview5` | 4 | 15 | `look_check/scene08/260806_w3_allview5` |
| `scene08` | `260806_w3_fixqueue2` | 15 | 54 | `look_check/scene08/260806_w3_fixqueue2` |
| `scene09` | `260806_w3_allview4` | 4 | 11 | `look_check/scene09/260806_w3_allview4` |
| `scene09` | `260806_w3_allview5` | 4 | 13 | `look_check/scene09/260806_w3_allview5` |
| `scene09` | `260806_w3_fixqueue2` | 18 | 58 | `look_check/scene09/260806_w3_fixqueue2` |
| `scene10` | `260805_w3_doctrine` | 14 | 74 | `look_check/scene10/260805_w3_doctrine` |
| `scene10` | `260806_w3_allview4` | 4 | 22 | `look_check/scene10/260806_w3_allview4` |
| `scene10` | `260806_w3_allview5` | 4 | 22 | `look_check/scene10/260806_w3_allview5` |
| `scene10` | `260806_w3_fixqueue` | 14 | 74 | `look_check/scene10/260806_w3_fixqueue` |
| `scene10` | `260806_w3_fixqueue2` | 14 | 74 | `look_check/scene10/260806_w3_fixqueue2` |
| `scene11` | `260806_w3_allview4` | 4 | 15 | `look_check/scene11/260806_w3_allview4` |
| `scene11` | `260806_w3_allview5` | 4 | 15 | `look_check/scene11/260806_w3_allview5` |
| `scene11` | `260806_w3_fixqueue2` | 15 | 58 | `look_check/scene11/260806_w3_fixqueue2` |
| `scene11` | `260807_w3_fixqueue3` | 15 | 59 | `look_check/scene11/260807_w3_fixqueue3` |
| `scene11` | `260811_w3_s11flip` | 15 | 59 | `look_check/scene11/260811_w3_s11flip` |
| `scene11` | `260811_w3_s11piers` | 15 | 59 | `look_check/scene11/260811_w3_s11piers` |
| `scene11` | `260811_w3_s11ribbon` | 15 | 58 | `look_check/scene11/260811_w3_s11ribbon` |
| `scene12` | `260805_w3_doctrine` | 16 | 52 | `look_check/scene12/260805_w3_doctrine` |
| `scene12` | `260806_w3_allview4` | 4 | 12 | `look_check/scene12/260806_w3_allview4` |
| `scene12` | `260806_w3_allview5` | 4 | 12 | `look_check/scene12/260806_w3_allview5` |
| `scene12` | `260806_w3_fixqueue` | 16 | 49 | `look_check/scene12/260806_w3_fixqueue` |
| `scene13` | `260805_w3_s13fix` | 15 | 52 | `look_check/scene13/260805_w3_s13fix` |
| `scene13` | `260805_w3_s13fix2` | 15 | 51 | `look_check/scene13/260805_w3_s13fix2` |
| `scene13` | `260805_w3_s13fix3` | 15 | 49 | `look_check/scene13/260805_w3_s13fix3` |
| `scene13` | `260805_w3_s13fix4` | 15 | 52 | `look_check/scene13/260805_w3_s13fix4` |
| `scene13` | `260805_w3_s13fix5` | 15 | 51 | `look_check/scene13/260805_w3_s13fix5` |
| `scene13` | `260806_w3_allview4` | 4 | 12 | `look_check/scene13/260806_w3_allview4` |
| `scene13` | `260806_w3_allview5` | 4 | 13 | `look_check/scene13/260806_w3_allview5` |
| `scene13` | `260806_w3_s13fix6` | 15 | 50 | `look_check/scene13/260806_w3_s13fix6` |
| `scene13` | `260806_w3_s13fix7` | 15 | 54 | `look_check/scene13/260806_w3_s13fix7` |
| `scene13` | `260811_w3_s13frost_a` | 15 | 54 | `look_check/scene13/260811_w3_s13frost_a` |
| `scene13` | `260811_w3_s13frost_b` | 15 | 50 | `look_check/scene13/260811_w3_s13frost_b` |
| `scene13` | `260811_w3_s13frost_d` | 15 | 46 | `look_check/scene13/260811_w3_s13frost_d` |
| `scene13` | `260811_w3_s13frost_e` | 15 | 45 | `look_check/scene13/260811_w3_s13frost_e` |
| `scene14` | `260805_w3_doctrine` | 13 | 36 | `look_check/scene14/260805_w3_doctrine` |
| `scene14` | `260805_w3_hedgeswap` | 13 | 36 | `look_check/scene14/260805_w3_hedgeswap` |
| `scene14` | `260806_w3_allview4` | 4 | 11 | `look_check/scene14/260806_w3_allview4` |
| `scene14` | `260806_w3_allview5` | 4 | 11 | `look_check/scene14/260806_w3_allview5` |
| `scene14` | `260806_w3_fixqueue` | 13 | 36 | `look_check/scene14/260806_w3_fixqueue` |
| `scene14` | `260806_w3_fixqueue2` | 13 | 36 | `look_check/scene14/260806_w3_fixqueue2` |
| `scene15` | `260805_w3_hedgeswap` | 13 | 52 | `look_check/scene15/260805_w3_hedgeswap` |
| `scene15` | `260806_w3_allview4` | 4 | 13 | `look_check/scene15/260806_w3_allview4` |
| `scene15` | `260806_w3_allview5` | 4 | 13 | `look_check/scene15/260806_w3_allview5` |
| `scene16` | `260805_w3_hedgeswap` | 13 | 49 | `look_check/scene16/260805_w3_hedgeswap` |
| `scene16` | `260806_w3_allview4` | 4 | 14 | `look_check/scene16/260806_w3_allview4` |
| `scene16` | `260806_w3_allview5` | 4 | 14 | `look_check/scene16/260806_w3_allview5` |
| `scene16` | `260806_w3_fixqueue` | 13 | 49 | `look_check/scene16/260806_w3_fixqueue` |
| `scene16` | `260806_w3_fixqueue2` | 13 | 49 | `look_check/scene16/260806_w3_fixqueue2` |
| `scene16` | `260807_w3_fixqueue3` | 13 | 49 | `look_check/scene16/260807_w3_fixqueue3` |
| `scene16` | `260811_w3_s16road6` | 13 | 47 | `look_check/scene16/260811_w3_s16road6` |
| `scene17` | `260806_w3_allview4` | 4 | 12 | `look_check/scene17/260806_w3_allview4` |
| `scene17` | `260806_w3_allview5` | 4 | 12 | `look_check/scene17/260806_w3_allview5` |
| `scene17` | `260806_w3_fixqueue2` | 14 | 50 | `look_check/scene17/260806_w3_fixqueue2` |
| `scene18` | `260806_w3_allview4` | 4 | 11 | `look_check/scene18/260806_w3_allview4` |
| `scene18` | `260806_w3_allview5` | 4 | 11 | `look_check/scene18/260806_w3_allview5` |
| `scene19` | `260806_w3_allview4` | 4 | 13 | `look_check/scene19/260806_w3_allview4` |
| `scene19` | `260806_w3_allview5` | 4 | 13 | `look_check/scene19/260806_w3_allview5` |
| `scene19` | `260806_w3_fixqueue2` | 16 | 57 | `look_check/scene19/260806_w3_fixqueue2` |
| `scene20` | `260805_w3_hedgeswap` | 13 | 54 | `look_check/scene20/260805_w3_hedgeswap` |
| `scene20` | `260806_w3_allview4` | 4 | 16 | `look_check/scene20/260806_w3_allview4` |
| `scene20` | `260806_w3_allview5` | 4 | 16 | `look_check/scene20/260806_w3_allview5` |
| `scene20` | `260806_w3_fixqueue2` | 13 | 53 | `look_check/scene20/260806_w3_fixqueue2` |
| `scene21` | `260806_w3_allview4` | 4 | 11 | `look_check/scene21/260806_w3_allview4` |
| `scene21` | `260806_w3_allview5` | 4 | 11 | `look_check/scene21/260806_w3_allview5` |
| `sceneC1` | `260806_w3_allview4` | 4 | 15 | `look_check/sceneC1/260806_w3_allview4` |
| `sceneC1` | `260806_w3_allview5` | 4 | 15 | `look_check/sceneC1/260806_w3_allview5` |
| `sceneC2` | `260806_w3_allview4` | 4 | 20 | `look_check/sceneC2/260806_w3_allview4` |
| `sceneC2` | `260806_w3_allview5` | 4 | 21 | `look_check/sceneC2/260806_w3_allview5` |
| `sceneC4` | `260806_w3_allview4` | 4 | 14 | `look_check/sceneC4/260806_w3_allview4` |
| `sceneC4` | `260806_w3_allview5` | 4 | 15 | `look_check/sceneC4/260806_w3_allview5` |
| `sceneC4` | `260806_w3_fixqueue2` | 13 | 54 | `look_check/sceneC4/260806_w3_fixqueue2` |
| `sceneD1` | `260806_w3_allview4` | 4 | 14 | `look_check/sceneD1/260806_w3_allview4` |
| `sceneD1` | `260806_w3_allview5` | 4 | 14 | `look_check/sceneD1/260806_w3_allview5` |
| `sceneD2` | `260806_w3_allview4` | 4 | 17 | `look_check/sceneD2/260806_w3_allview4` |
| `sceneD2` | `260806_w3_allview5` | 4 | 17 | `look_check/sceneD2/260806_w3_allview5` |
| `sceneD3` | `260806_w3_allview4` | 4 | 17 | `look_check/sceneD3/260806_w3_allview4` |
| `sceneD3` | `260806_w3_allview5` | 4 | 17 | `look_check/sceneD3/260806_w3_allview5` |
| `sceneD4` | `260806_w3_allview4` | 4 | 8 | `look_check/sceneD4/260806_w3_allview4` |
| `sceneD4` | `260806_w3_allview5` | 4 | 8 | `look_check/sceneD4/260806_w3_allview5` |
| `sceneN1` | `260805_w3_hedgeswap` | 13 | 49 | `look_check/sceneN1/260805_w3_hedgeswap` |
| `sceneN1` | `260806_w3_allview4` | 4 | 15 | `look_check/sceneN1/260806_w3_allview4` |
| `sceneN1` | `260806_w3_allview5` | 4 | 15 | `look_check/sceneN1/260806_w3_allview5` |
| `sceneN2` | `260805_w3_hedgeswap` | 13 | 58 | `look_check/sceneN2/260805_w3_hedgeswap` |
| `sceneN2` | `260806_w3_allview4` | 4 | 17 | `look_check/sceneN2/260806_w3_allview4` |
| `sceneN2` | `260806_w3_allview5` | 4 | 17 | `look_check/sceneN2/260806_w3_allview5` |
| `sceneN3` | `260806_w3_allview4` | 4 | 16 | `look_check/sceneN3/260806_w3_allview4` |
| `sceneN3` | `260806_w3_allview5` | 4 | 16 | `look_check/sceneN3/260806_w3_allview5` |
| `sceneN4` | `260806_w3_allview4` | 4 | 12 | `look_check/sceneN4/260806_w3_allview4` |
| `sceneN4` | `260806_w3_allview5` | 4 | 12 | `look_check/sceneN4/260806_w3_allview5` |
| `sceneN5` | `260806_w3_allview4` | 4 | 15 | `look_check/sceneN5/260806_w3_allview4` |
| `sceneN5` | `260806_w3_allview5` | 4 | 15 | `look_check/sceneN5/260806_w3_allview5` |

## 4. `_experiments/`

경로는 **바꾸지 않았다** — 29개 파일이 `_experiments/gates` · `_experiments/twins` 를 인용한다. 2026-07-30 이후로 렌더가 한 번도 들어가지 않은 냉동 트리다. `마지막 기록` 은 **파일** 기준이다(폴더 mtime 은 삭제만으로도 갱신돼서 쓰지 않는다). `t0_spike/` 의 08-27 은 0827 재편이 그 안의 저널 한 줄을 고쳐 쓴 것이지 렌더가 아니다.

| 토픽 | 하위 항목 | GB | 마지막 기록 |
|---|---:|---:|---|
| `_experiments/diag/` | 4 | 0.13 | 2026-07-28 |
| `_experiments/gates/` | 19 | 0.89 | 2026-07-30 |
| `_experiments/spike_p1/` | 9 | 0.23 | 2026-07-29 |
| `_experiments/t0_spike/` | 34 | 1.17 | 2026-08-27 |
| `_experiments/twins/` | 19 | 0.67 | 2026-07-30 |

| 검수 갤러리 | 항목 | MB | 마지막 기록 |
|---|---:|---:|---|
| `_review/w2/` | 133 | 4 | 2026-08-05 |
| `_review/w3/` | 35 | 682 | 2026-08-11 |
| `_review/w4/` | 12 | 11 | 2026-08-16 |

## 5. 최신 라운드 탐색 (baseline hygiene)

`ls -t <scene>/*/ | head -1` 이 **판정 라운드**를 돌려주는지, `regression_check.py` 의 `resolve_round` 가 씬마다 어떤 라운드로 떨어지는지를 이 생성 시점에 실제로 확인한 값이다.

| 씬 | `ls -t` 머리 | 컷 | `resolve_round` 결과 | 컷 |
|---|---|---:|---|---:|
| `scene01` | `260816_w4_final33_on` | 13 | `260731_w3_s01` | 13 |
| `scene02` | `260816_w4_final33_on` | 13 | `260731_w3_gt25` | 13 |
| `scene03` | `260817_w4_regfix` | 16 | `260731_w3_s03` | 16 |
| `scene04` | `260816_w4_final33_on` | 13 | `260731_w3_s04` | 13 |
| `scene05` | `260817_w4_regfix` | 13 | `260730_w2d_fix` | 13 |
| `scene06` | `260817_w4_regfix` | 15 | `260731_w3_s06` | 15 |
| `scene07` | `260816_w4_final33_on` | 14 | `260731_w3_s07` | 14 |
| `scene08` | `260816_w4_final33_on` | 15 | `260731_w3_s08d` | 15 |
| `scene09` | `260816_w4_final33_on` | 18 | `260731_w3_s09` | 18 |
| `scene10` | `260817_w4_regfix` | 14 | `260731_w3_s10c` | 14 |
| `scene11` | `260816_w4_final33_on` | 15 | `260731_w3_s11` | 15 |
| `scene12` | `260816_w4_final33_on` | 16 | `260730_w2d_fix` | 16 |
| `scene13` | `260816_w4_dn_off256` | 15 | `260730_w3_s13b` | 15 |
| `scene14` | `260816_w4_final33_on` | 13 | `260730_w2d_fix` | 13 |
| `scene15` | `260817_w4_regfix` | 13 | `260730_w2d_fix` | 13 |
| `scene16` | `260816_w4_micropilot` | 13 | `260731_w3_s16` | 13 |
| `scene17` | `260816_w4_final33_on` | 14 | `260731_w3_s17` | 14 |
| `scene18` | `260816_w4_w8deck` | 14 | `260731_w3_s18` | 14 |
| `scene19` | `260816_w4_final33_on` | 16 | `260730_w2d_fix` | 16 |
| `scene20` | `260816_w4_final33_on` | 13 | `260730_w2d_fix` | 13 |
| `scene21` | `260816_w4_final33_on` | 13 | `260730_w2d_fix` | 13 |
| `sceneC1` | `260816_w4_final33_on` | 13 | `260730_w2d_fix` | 13 |
| `sceneC2` | `260816_w4_final33_on` | 13 | `260731_w3_cb2` | 5 |
| `sceneC4` | `260816_w4_final33_on` | 13 | `260730_w2d_fix` | 13 |
| `sceneD1` | `260816_w4_final33_on` | 14 | `260730_w2d_fix` | 14 |
| `sceneD2` | `260816_w4_final33_on` | 13 | `260730_w2d_fix` | 13 |
| `sceneD3` | `260816_w4_final33_on` | 14 | `260730_w2d_fix` | 14 |
| `sceneD4` | `260816_w4_final33_on` | 13 | `260730_w2d_fix` | 13 |
| `sceneN1` | `260816_w4_final33_on` | 13 | `260730_w2d_fix` | 13 |
| `sceneN2` | `260816_w4_final33_on` | 13 | `260730_w3_n2clean` | 13 |
| `sceneN3` | `260816_w4_final33_on` | 13 | `260730_w2d_fix` | 13 |
| `sceneN4` | `260816_w4_final33_on` | 13 | `260730_w2d_fix` | 13 |
| `sceneN5` | `260816_w4_final33_on` | 13 | `260730_w2d_fix` | 13 |

**33/33 씬이 `resolve_round` 로 해소된다** (0 unresolved). 체인은 `look_check/README.md` §4 의 26개 이름, 앞에서부터 첫 번째로 존재하는 폴더가 이긴다.

## 6. 이동 지도 (예전 경로 → 지금 경로)

2026-07-30 정리분 + 2026-08-27 재편분을 누적한다. 이 표가 있으므로 **씬 폴더 안에 back-compat 심볼릭 링크를 만들지 않는다**(§0).

| 예전 경로 | 지금 경로 |
|---|---|
| `look_check/_t0_spike/…` | unchanged — **symlink** to `_experiments/t0_spike/…` |
| `look_check/spike_probe/…` | unchanged — **symlink** to `_experiments/spike_p1/spike_probe/…` |
| `look_check/spike_e{1,2,3,4,5,9,10}/`, `look_check/spike_budget/` | `look_check/_experiments/spike_p1/<same>/` |
| `look_check/diag_0701/`, `diag_d3/`, `diag_scene07_temple_stone_path/`, `diag_sceneD3_drainage_channel/` | `look_check/_experiments/diag/<same>/` |
| `look_check/scene02/wininset_base/` | `look_check/_experiments/gates/scene02/wininset_base/` |
| `look_check/scene02/wininset_crop/` | `look_check/_experiments/gates/scene02/wininset_crop/` |
| `look_check/scene02/wininset_gate/` | `look_check/_experiments/gates/scene02/wininset_gate/` |
| `look_check/scene02/wininset_gate_rep/` | `look_check/_experiments/gates/scene02/wininset_gate_rep/` |
| `look_check/scene07/graze_warn_crop/` | `look_check/_experiments/gates/scene07/graze_warn_crop/` |
| `look_check/scene07/t1_crop/` | `look_check/_experiments/gates/scene07/t1_crop/` |
| `look_check/scene13/graze_warn_crop/` | `look_check/_experiments/gates/scene13/graze_warn_crop/` |
| `look_check/scene13/w2_pilot_crop/` | `look_check/_experiments/gates/scene13/w2_pilot_crop/` |
| `look_check/scene13/w2_pilot_hoff/` | `look_check/_experiments/gates/scene13/w2_pilot_hoff/` |
| `look_check/scene13/w2c_c2_crop/` | `look_check/_experiments/gates/scene13/w2c_c2_crop/` |
| `look_check/scene14/parapet_crop/` | `look_check/_experiments/gates/scene14/parapet_crop/` |
| `look_check/scene14/t1_crop/` | `look_check/_experiments/gates/scene14/t1_crop/` |
| `look_check/scene15/w2_pilot_crop/` | `look_check/_experiments/gates/scene15/w2_pilot_crop/` |
| `look_check/scene15/w2_pilot_hoff/` | `look_check/_experiments/gates/scene15/w2_pilot_hoff/` |
| `look_check/scene15/w2c_c2_crop/` | `look_check/_experiments/gates/scene15/w2c_c2_crop/` |
| `look_check/scene19/t1_crop/` | `look_check/_experiments/gates/scene19/t1_crop/` |
| `look_check/sceneC2/t1_crop/` | `look_check/_experiments/gates/sceneC2/t1_crop/` |
| `look_check/sceneN3/wininset_base/` | `look_check/_experiments/gates/sceneN3/wininset_base/` |
| `look_check/sceneN3/wininset_crop/` | `look_check/_experiments/gates/sceneN3/wininset_crop/` |
| `look_check/sceneN3/wininset_gate/` | `look_check/_experiments/gates/sceneN3/wininset_gate/` |
| `look_check/sceneN3/wininset_gate_rep/` | `look_check/_experiments/gates/sceneN3/wininset_gate_rep/` |
| `look_check/sceneN5/w2_pilot_crop/` | `look_check/_experiments/gates/sceneN5/w2_pilot_crop/` |
| `look_check/sceneN5/w2_pilot_hoff/` | `look_check/_experiments/gates/sceneN5/w2_pilot_hoff/` |
| `look_check/sceneN5/w2c_c2_crop/` | `look_check/_experiments/gates/sceneN5/w2c_c2_crop/` |
| `look_check/scene01/veg_test/` | `look_check/_experiments/twins/scene01/veg_test/` |
| `look_check/scene04/veg_test/` | `look_check/_experiments/twins/scene04/veg_test/` |
| `look_check/scene05/planterfix/` | `look_check/_experiments/twins/scene05/planterfix/` |
| `look_check/scene05/veg_test/` | `look_check/_experiments/twins/scene05/veg_test/` |
| `look_check/scene07/t1_mtl_off/` | `look_check/_experiments/twins/scene07/t1_mtl_off/` |
| `look_check/scene07/t1_mtl_on/` | `look_check/_experiments/twins/scene07/t1_mtl_on/` |
| `look_check/scene10/veg_test/` | `look_check/_experiments/twins/scene10/veg_test/` |
| `look_check/scene13/w2c_c2_goff/` | `look_check/_experiments/twins/scene13/w2c_c2_goff/` |
| `look_check/scene13/w2c_c2_gon/` | `look_check/_experiments/twins/scene13/w2c_c2_gon/` |
| `look_check/scene14/t1_mtl_off/` | `look_check/_experiments/twins/scene14/t1_mtl_off/` |
| `look_check/scene14/t1_mtl_on/` | `look_check/_experiments/twins/scene14/t1_mtl_on/` |
| `look_check/scene15/w2_pilot_r1/` | `look_check/_experiments/twins/scene15/w2_pilot_r1/` |
| `look_check/scene15/w2c_c2_goff/` | `look_check/_experiments/twins/scene15/w2c_c2_goff/` |
| `look_check/scene15/w2c_c2_gon/` | `look_check/_experiments/twins/scene15/w2c_c2_gon/` |
| `look_check/scene19/t1_mtl_off/` | `look_check/_experiments/twins/scene19/t1_mtl_off/` |
| `look_check/scene19/t1_mtl_on_nodetail/` | `look_check/_experiments/twins/scene19/t1_mtl_on_nodetail/` |
| `look_check/scene19/t1_mtl_on_s12.5/` | `look_check/_experiments/twins/scene19/t1_mtl_on_s12.5/` |
| `look_check/scene19/t1_mtl_on_s2/` | `look_check/_experiments/twins/scene19/t1_mtl_on_s2/` |
| `look_check/scene19/t1_mtl_on_s2_rg030/` | `look_check/_experiments/twins/scene19/t1_mtl_on_s2_rg030/` |
| `look_check/scene19/t1_mtl_on_s2_rg060/` | `look_check/_experiments/twins/scene19/t1_mtl_on_s2_rg060/` |
| `look_check/scene19/t1_mtl_on_s3/` | `look_check/_experiments/twins/scene19/t1_mtl_on_s3/` |
| `look_check/scene19/t1_mtl_on_s4/` | `look_check/_experiments/twins/scene19/t1_mtl_on_s4/` |
| `look_check/sceneC2/t1_mtl_off/` | `look_check/_experiments/twins/sceneC2/t1_mtl_off/` |
| `look_check/sceneC2/t1_mtl_on/` | `look_check/_experiments/twins/sceneC2/t1_mtl_on/` |
| `look_check/sceneN5/w2_pilot_r1/` | `look_check/_experiments/twins/sceneN5/w2_pilot_r1/` |
| `look_check/sceneN5/w2c_c2_goff/` | `look_check/_experiments/twins/sceneN5/w2c_c2_goff/` |
| `look_check/sceneN5/w2c_c2_gon/` | `look_check/_experiments/twins/sceneN5/w2c_c2_gon/` |
| `look_check/scene01/260731_w3_full` | `look_check/_archive/w3/scene01/260731_w3_full` |
| `look_check/scene01/260731_w3_mb24_pre` | `look_check/_archive/w3/scene01/260731_w3_mb24_pre` |
| `look_check/scene01/260731_w3_s01_pre` | `look_check/_archive/w3/scene01/260731_w3_s01_pre` |
| `look_check/scene01/260805_w3_doctrine` | `look_check/_archive/w3fix/scene01/260805_w3_doctrine` |
| `look_check/scene01/260806_w3_allview4` | `look_check/_archive/w3fix/scene01/260806_w3_allview4` |
| `look_check/scene01/260806_w3_allview5` | `look_check/_archive/w3fix/scene01/260806_w3_allview5` |
| `look_check/scene01/260806_w3_fixqueue` | `look_check/_archive/w3fix/scene01/260806_w3_fixqueue` |
| `look_check/scene01/260806_w3_fixqueue2` | `look_check/_archive/w3fix/scene01/260806_w3_fixqueue2` |
| `look_check/scene01/p2g4_on` | `look_check/_archive/w2/scene01/p2g4_on` |
| `look_check/scene01/pair_cues_off` | `look_check/_archive/w2/scene01/pair_cues_off` |
| `look_check/scene02/260730_lcfreeze_post` | `look_check/_archive/w2d/scene02/260730_lcfreeze_post` |
| `look_check/scene02/260730_lcfreeze_pre` | `look_check/_archive/w2d/scene02/260730_lcfreeze_pre` |
| `look_check/scene02/260731_w3_cb7` | `look_check/_archive/w3/scene02/260731_w3_cb7` |
| `look_check/scene02/260731_w3_cb7_pre` | `look_check/_archive/w3/scene02/260731_w3_cb7_pre` |
| `look_check/scene02/260731_w3_full` | `look_check/_archive/w3/scene02/260731_w3_full` |
| `look_check/scene02/260731_w3_gt25_pre` | `look_check/_archive/w3/scene02/260731_w3_gt25_pre` |
| `look_check/scene02/260731_w3_mb24_pre` | `look_check/_archive/w3/scene02/260731_w3_mb24_pre` |
| `look_check/scene02/260805_w3_hedgeswap` | `look_check/_archive/w3fix/scene02/260805_w3_hedgeswap` |
| `look_check/scene02/260806_w3_allview4` | `look_check/_archive/w3fix/scene02/260806_w3_allview4` |
| `look_check/scene02/260806_w3_allview5` | `look_check/_archive/w3fix/scene02/260806_w3_allview5` |
| `look_check/scene02/_cb7_r1_glazing_rejected` | `look_check/_archive/w2/scene02/_cb7_r1_glazing_rejected` |
| `look_check/scene02/v7_pt` | `look_check/_archive/w2/scene02/v7_pt` |
| `look_check/scene03/260731_w3_full` | `look_check/_archive/w3/scene03/260731_w3_full` |
| `look_check/scene03/260806_w3_allview4` | `look_check/_archive/w3fix/scene03/260806_w3_allview4` |
| `look_check/scene03/260806_w3_allview5` | `look_check/_archive/w3fix/scene03/260806_w3_allview5` |
| `look_check/scene03/260806_w3_fixqueue2` | `look_check/_archive/w3fix/scene03/260806_w3_fixqueue2` |
| `look_check/scene03/260806_w3_s03probe` | `look_check/_archive/w3fix/scene03/260806_w3_s03probe` |
| `look_check/scene03/260807_w3_fixqueue3` | `look_check/_archive/w3fix/scene03/260807_w3_fixqueue3` |
| `look_check/scene03/v7_pt` | `look_check/_archive/w2/scene03/v7_pt` |
| `look_check/scene04/260730_lcfreeze_post` | `look_check/_archive/w2d/scene04/260730_lcfreeze_post` |
| `look_check/scene04/260730_lcfreeze_pre` | `look_check/_archive/w2d/scene04/260730_lcfreeze_pre` |
| `look_check/scene04/260731_w3_full` | `look_check/_archive/w3/scene04/260731_w3_full` |
| `look_check/scene04/260731_w3_s04b` | `look_check/_archive/w3/scene04/260731_w3_s04b` |
| `look_check/scene04/260806_w3_allview4` | `look_check/_archive/w3fix/scene04/260806_w3_allview4` |
| `look_check/scene04/v7_pt` | `look_check/_archive/w2/scene04/v7_pt` |
| `look_check/scene05/260731_w3_full` | `look_check/_archive/w3/scene05/260731_w3_full` |
| `look_check/scene05/260731_w3_l05_pre` | `look_check/_archive/w3/scene05/260731_w3_l05_pre` |
| `look_check/scene05/260731_w3_l05b` | `look_check/_archive/w3/scene05/260731_w3_l05b` |
| `look_check/scene05/260731_w3_l05c` | `look_check/_archive/w3/scene05/260731_w3_l05c` |
| `look_check/scene05/260805_w3_doctrine` | `look_check/_archive/w3fix/scene05/260805_w3_doctrine` |
| `look_check/scene05/260805_w3_hedgeswap` | `look_check/_archive/w3fix/scene05/260805_w3_hedgeswap` |
| `look_check/scene05/260806_w3_allview4` | `look_check/_archive/w3fix/scene05/260806_w3_allview4` |
| `look_check/scene05/260806_w3_allview5` | `look_check/_archive/w3fix/scene05/260806_w3_allview5` |
| `look_check/scene05/260806_w3_fixqueue` | `look_check/_archive/w3fix/scene05/260806_w3_fixqueue` |
| `look_check/scene05/260806_w3_fixqueue2` | `look_check/_archive/w3fix/scene05/260806_w3_fixqueue2` |
| `look_check/scene05/_gt6_judge_baseline` | `look_check/_archive/w2/scene05/_gt6_judge_baseline` |
| `look_check/scene05/v8_pt` | `look_check/_archive/w2/scene05/v8_pt` |
| `look_check/scene06/260731_w3_full` | `look_check/_archive/w3/scene06/260731_w3_full` |
| `look_check/scene06/260805_w3_doctrine` | `look_check/_archive/w3fix/scene06/260805_w3_doctrine` |
| `look_check/scene06/260806_w3_allview4` | `look_check/_archive/w3fix/scene06/260806_w3_allview4` |
| `look_check/scene06/260806_w3_allview5` | `look_check/_archive/w3fix/scene06/260806_w3_allview5` |
| `look_check/scene06/260806_w3_fixqueue` | `look_check/_archive/w3fix/scene06/260806_w3_fixqueue` |
| `look_check/scene06/260806_w3_fixqueue2` | `look_check/_archive/w3fix/scene06/260806_w3_fixqueue2` |
| `look_check/scene06/260807_w3_fixqueue3` | `look_check/_archive/w3fix/scene06/260807_w3_fixqueue3` |
| `look_check/scene06/260810_w3_s06collar` | `look_check/_archive/w3fix/scene06/260810_w3_s06collar` |
| `look_check/scene06/260810_w3_s06direct` | `look_check/_archive/w3fix/scene06/260810_w3_s06direct` |
| `look_check/scene06/260810_w3_s06endstair` | `look_check/_archive/w3fix/scene06/260810_w3_s06endstair` |
| `look_check/scene06/260811_w3_s06bay14` | `look_check/_archive/w3fix/scene06/260811_w3_s06bay14` |
| `look_check/scene06/260811_w3_s06ease` | `look_check/_archive/w3fix/scene06/260811_w3_s06ease` |
| `look_check/scene06/260811_w3_s06glass` | `look_check/_archive/w3fix/scene06/260811_w3_s06glass` |
| `look_check/scene06/260811_w3_s06sweep` | `look_check/_archive/w3fix/scene06/260811_w3_s06sweep` |
| `look_check/scene06/260811_w3_s06trim` | `look_check/_archive/w3fix/scene06/260811_w3_s06trim` |
| `look_check/scene06/260811_w3_s06weld` | `look_check/_archive/w3fix/scene06/260811_w3_s06weld` |
| `look_check/scene06/260811_w3_s06wide` | `look_check/_archive/w3fix/scene06/260811_w3_s06wide` |
| `look_check/scene06/_gt6_judge_baseline` | `look_check/_archive/w2/scene06/_gt6_judge_baseline` |
| `look_check/scene06/v8_pt` | `look_check/_archive/w2/scene06/v8_pt` |
| `look_check/scene07/260731_w3_full` | `look_check/_archive/w3/scene07/260731_w3_full` |
| `look_check/scene07/260806_w3_allview4` | `look_check/_archive/w3fix/scene07/260806_w3_allview4` |
| `look_check/scene07/260806_w3_allview5` | `look_check/_archive/w3fix/scene07/260806_w3_allview5` |
| `look_check/scene07/260806_w3_fixqueue2` | `look_check/_archive/w3fix/scene07/260806_w3_fixqueue2` |
| `look_check/scene07/p2g4_on` | `look_check/_archive/w2/scene07/p2g4_on` |
| `look_check/scene08/260731_w3_full` | `look_check/_archive/w3/scene08/260731_w3_full` |
| `look_check/scene08/260731_w3_s08` | `look_check/_archive/w3/scene08/260731_w3_s08` |
| `look_check/scene08/260731_w3_s08b` | `look_check/_archive/w3/scene08/260731_w3_s08b` |
| `look_check/scene08/260731_w3_s08c` | `look_check/_archive/w3/scene08/260731_w3_s08c` |
| `look_check/scene08/260806_w3_allview4` | `look_check/_archive/w3fix/scene08/260806_w3_allview4` |
| `look_check/scene08/260806_w3_allview5` | `look_check/_archive/w3fix/scene08/260806_w3_allview5` |
| `look_check/scene08/260806_w3_fixqueue2` | `look_check/_archive/w3fix/scene08/260806_w3_fixqueue2` |
| `look_check/scene08/v7_pt` | `look_check/_archive/w2/scene08/v7_pt` |
| `look_check/scene09/260731_w3_full` | `look_check/_archive/w3/scene09/260731_w3_full` |
| `look_check/scene09/260731_w3_mb24_pre` | `look_check/_archive/w3/scene09/260731_w3_mb24_pre` |
| `look_check/scene09/260806_w3_allview4` | `look_check/_archive/w3fix/scene09/260806_w3_allview4` |
| `look_check/scene09/260806_w3_allview5` | `look_check/_archive/w3fix/scene09/260806_w3_allview5` |
| `look_check/scene09/260806_w3_fixqueue2` | `look_check/_archive/w3fix/scene09/260806_w3_fixqueue2` |
| `look_check/scene09/v8_rt2` | `look_check/_archive/w2/scene09/v8_rt2` |
| `look_check/scene10/260731_w3_full` | `look_check/_archive/w3/scene10/260731_w3_full` |
| `look_check/scene10/260731_w3_pre10` | `look_check/_archive/w3/scene10/260731_w3_pre10` |
| `look_check/scene10/260731_w3_pre10c` | `look_check/_archive/w3/scene10/260731_w3_pre10c` |
| `look_check/scene10/260731_w3_s10` | `look_check/_archive/w3/scene10/260731_w3_s10` |
| `look_check/scene10/260805_w3_doctrine` | `look_check/_archive/w3fix/scene10/260805_w3_doctrine` |
| `look_check/scene10/260806_w3_allview4` | `look_check/_archive/w3fix/scene10/260806_w3_allview4` |
| `look_check/scene10/260806_w3_allview5` | `look_check/_archive/w3fix/scene10/260806_w3_allview5` |
| `look_check/scene10/260806_w3_fixqueue` | `look_check/_archive/w3fix/scene10/260806_w3_fixqueue` |
| `look_check/scene10/260806_w3_fixqueue2` | `look_check/_archive/w3fix/scene10/260806_w3_fixqueue2` |
| `look_check/scene10/v8_pt` | `look_check/_archive/w2/scene10/v8_pt` |
| `look_check/scene11/260731_w3_full` | `look_check/_archive/w3/scene11/260731_w3_full` |
| `look_check/scene11/260731_w3_p11_pilot0` | `look_check/_archive/w3/scene11/260731_w3_p11_pilot0` |
| `look_check/scene11/260806_w3_allview4` | `look_check/_archive/w3fix/scene11/260806_w3_allview4` |
| `look_check/scene11/260806_w3_allview5` | `look_check/_archive/w3fix/scene11/260806_w3_allview5` |
| `look_check/scene11/260806_w3_fixqueue2` | `look_check/_archive/w3fix/scene11/260806_w3_fixqueue2` |
| `look_check/scene11/260807_w3_fixqueue3` | `look_check/_archive/w3fix/scene11/260807_w3_fixqueue3` |
| `look_check/scene11/260811_w3_s11flip` | `look_check/_archive/w3fix/scene11/260811_w3_s11flip` |
| `look_check/scene11/260811_w3_s11piers` | `look_check/_archive/w3fix/scene11/260811_w3_s11piers` |
| `look_check/scene11/260811_w3_s11ribbon` | `look_check/_archive/w3fix/scene11/260811_w3_s11ribbon` |
| `look_check/scene11/v8_pt` | `look_check/_archive/w2/scene11/v8_pt` |
| `look_check/scene12/260731_w3_full` | `look_check/_archive/w3/scene12/260731_w3_full` |
| `look_check/scene12/260731_w3_l12` | `look_check/_archive/w3/scene12/260731_w3_l12` |
| `look_check/scene12/260731_w3_l12_mat` | `look_check/_archive/w3/scene12/260731_w3_l12_mat` |
| `look_check/scene12/260731_w3_l12_pre` | `look_check/_archive/w3/scene12/260731_w3_l12_pre` |
| `look_check/scene12/260731_w3_l12b` | `look_check/_archive/w3/scene12/260731_w3_l12b` |
| `look_check/scene12/260805_w3_doctrine` | `look_check/_archive/w3fix/scene12/260805_w3_doctrine` |
| `look_check/scene12/260806_w3_allview4` | `look_check/_archive/w3fix/scene12/260806_w3_allview4` |
| `look_check/scene12/260806_w3_allview5` | `look_check/_archive/w3fix/scene12/260806_w3_allview5` |
| `look_check/scene12/260806_w3_fixqueue` | `look_check/_archive/w3fix/scene12/260806_w3_fixqueue` |
| `look_check/scene12/v8_pt` | `look_check/_archive/w2/scene12/v8_pt` |
| `look_check/scene13/260731_w3_full` | `look_check/_archive/w3/scene13/260731_w3_full` |
| `look_check/scene13/260805_w3_s13fix` | `look_check/_archive/w3fix/scene13/260805_w3_s13fix` |
| `look_check/scene13/260805_w3_s13fix2` | `look_check/_archive/w3fix/scene13/260805_w3_s13fix2` |
| `look_check/scene13/260805_w3_s13fix3` | `look_check/_archive/w3fix/scene13/260805_w3_s13fix3` |
| `look_check/scene13/260805_w3_s13fix4` | `look_check/_archive/w3fix/scene13/260805_w3_s13fix4` |
| `look_check/scene13/260805_w3_s13fix5` | `look_check/_archive/w3fix/scene13/260805_w3_s13fix5` |
| `look_check/scene13/260806_w3_allview4` | `look_check/_archive/w3fix/scene13/260806_w3_allview4` |
| `look_check/scene13/260806_w3_allview5` | `look_check/_archive/w3fix/scene13/260806_w3_allview5` |
| `look_check/scene13/260806_w3_s13fix6` | `look_check/_archive/w3fix/scene13/260806_w3_s13fix6` |
| `look_check/scene13/260806_w3_s13fix7` | `look_check/_archive/w3fix/scene13/260806_w3_s13fix7` |
| `look_check/scene13/260811_w3_s13frost_a` | `look_check/_archive/w3fix/scene13/260811_w3_s13frost_a` |
| `look_check/scene13/260811_w3_s13frost_b` | `look_check/_archive/w3fix/scene13/260811_w3_s13frost_b` |
| `look_check/scene13/260811_w3_s13frost_d` | `look_check/_archive/w3fix/scene13/260811_w3_s13frost_d` |
| `look_check/scene13/260811_w3_s13frost_e` | `look_check/_archive/w3fix/scene13/260811_w3_s13frost_e` |
| `look_check/scene13/_gt6_judge_baseline` | `look_check/_archive/w2/scene13/_gt6_judge_baseline` |
| `look_check/scene13/v7_pt` | `look_check/_archive/w2/scene13/v7_pt` |
| `look_check/scene14/260731_w3_full` | `look_check/_archive/w3/scene14/260731_w3_full` |
| `look_check/scene14/260731_w3_l14_bk` | `look_check/_archive/w3/scene14/260731_w3_l14_bk` |
| `look_check/scene14/260731_w3_l14_p1` | `look_check/_archive/w3/scene14/260731_w3_l14_p1` |
| `look_check/scene14/260731_w3_l14_pre` | `look_check/_archive/w3/scene14/260731_w3_l14_pre` |
| `look_check/scene14/260805_w3_doctrine` | `look_check/_archive/w3fix/scene14/260805_w3_doctrine` |
| `look_check/scene14/260805_w3_hedgeswap` | `look_check/_archive/w3fix/scene14/260805_w3_hedgeswap` |
| `look_check/scene14/260806_w3_allview4` | `look_check/_archive/w3fix/scene14/260806_w3_allview4` |
| `look_check/scene14/260806_w3_allview5` | `look_check/_archive/w3fix/scene14/260806_w3_allview5` |
| `look_check/scene14/260806_w3_fixqueue` | `look_check/_archive/w3fix/scene14/260806_w3_fixqueue` |
| `look_check/scene14/260806_w3_fixqueue2` | `look_check/_archive/w3fix/scene14/260806_w3_fixqueue2` |
| `look_check/scene14/v7_pt` | `look_check/_archive/w2/scene14/v7_pt` |
| `look_check/scene15/260731_w3_full` | `look_check/_archive/w3/scene15/260731_w3_full` |
| `look_check/scene15/260731_w3_l15_pre` | `look_check/_archive/w3/scene15/260731_w3_l15_pre` |
| `look_check/scene15/260805_w3_hedgeswap` | `look_check/_archive/w3fix/scene15/260805_w3_hedgeswap` |
| `look_check/scene15/260806_w3_allview4` | `look_check/_archive/w3fix/scene15/260806_w3_allview4` |
| `look_check/scene15/260806_w3_allview5` | `look_check/_archive/w3fix/scene15/260806_w3_allview5` |
| `look_check/scene15/v7_pt` | `look_check/_archive/w2/scene15/v7_pt` |
| `look_check/scene16/260731_w3_full` | `look_check/_archive/w3/scene16/260731_w3_full` |
| `look_check/scene16/260731_w3_mb24_pre` | `look_check/_archive/w3/scene16/260731_w3_mb24_pre` |
| `look_check/scene16/260805_w3_hedgeswap` | `look_check/_archive/w3fix/scene16/260805_w3_hedgeswap` |
| `look_check/scene16/260806_w3_allview4` | `look_check/_archive/w3fix/scene16/260806_w3_allview4` |
| `look_check/scene16/260806_w3_allview5` | `look_check/_archive/w3fix/scene16/260806_w3_allview5` |
| `look_check/scene16/260806_w3_fixqueue` | `look_check/_archive/w3fix/scene16/260806_w3_fixqueue` |
| `look_check/scene16/260806_w3_fixqueue2` | `look_check/_archive/w3fix/scene16/260806_w3_fixqueue2` |
| `look_check/scene16/260807_w3_fixqueue3` | `look_check/_archive/w3fix/scene16/260807_w3_fixqueue3` |
| `look_check/scene16/260811_w3_s16road6` | `look_check/_archive/w3fix/scene16/260811_w3_s16road6` |
| `look_check/scene16/v7_pt` | `look_check/_archive/w2/scene16/v7_pt` |
| `look_check/scene17/260731_w3_full` | `look_check/_archive/w3/scene17/260731_w3_full` |
| `look_check/scene17/260731_w3_s17_pre` | `look_check/_archive/w3/scene17/260731_w3_s17_pre` |
| `look_check/scene17/260731_w3_sb17` | `look_check/_archive/w3/scene17/260731_w3_sb17` |
| `look_check/scene17/260731_w3_sb17_pre` | `look_check/_archive/w3/scene17/260731_w3_sb17_pre` |
| `look_check/scene17/260806_w3_allview4` | `look_check/_archive/w3fix/scene17/260806_w3_allview4` |
| `look_check/scene17/260806_w3_allview5` | `look_check/_archive/w3fix/scene17/260806_w3_allview5` |
| `look_check/scene17/260806_w3_fixqueue2` | `look_check/_archive/w3fix/scene17/260806_w3_fixqueue2` |
| `look_check/scene17/v8_pt` | `look_check/_archive/w2/scene17/v8_pt` |
| `look_check/scene18/260731_w3_full` | `look_check/_archive/w3/scene18/260731_w3_full` |
| `look_check/scene18/260731_w3_s18b` | `look_check/_archive/w3/scene18/260731_w3_s18b` |
| `look_check/scene18/260731_w3_s18c` | `look_check/_archive/w3/scene18/260731_w3_s18c` |
| `look_check/scene18/260731_w3_s18d` | `look_check/_archive/w3/scene18/260731_w3_s18d` |
| `look_check/scene18/260731_w3_s18e` | `look_check/_archive/w3/scene18/260731_w3_s18e` |
| `look_check/scene18/260806_w3_allview4` | `look_check/_archive/w3fix/scene18/260806_w3_allview4` |
| `look_check/scene18/260806_w3_allview5` | `look_check/_archive/w3fix/scene18/260806_w3_allview5` |
| `look_check/scene19/260731_w3_full` | `look_check/_archive/w3/scene19/260731_w3_full` |
| `look_check/scene19/260731_w3_l19_pre` | `look_check/_archive/w3/scene19/260731_w3_l19_pre` |
| `look_check/scene19/260806_w3_allview4` | `look_check/_archive/w3fix/scene19/260806_w3_allview4` |
| `look_check/scene19/260806_w3_allview5` | `look_check/_archive/w3fix/scene19/260806_w3_allview5` |
| `look_check/scene19/260806_w3_fixqueue2` | `look_check/_archive/w3fix/scene19/260806_w3_fixqueue2` |
| `look_check/scene19/_gt6_judge_baseline` | `look_check/_archive/w2/scene19/_gt6_judge_baseline` |
| `look_check/scene19/r4` | `look_check/_archive/w2/scene19/r4` |
| `look_check/scene19/r5` | `look_check/_archive/w2/scene19/r5` |
| `look_check/scene19/v7_pt` | `look_check/_archive/w2/scene19/v7_pt` |
| `look_check/scene20/260730_w3r_bldgab` | `look_check/_archive/w3/scene20/260730_w3r_bldgab` |
| `look_check/scene20/260731_w3_full` | `look_check/_archive/w3/scene20/260731_w3_full` |
| `look_check/scene20/260731_w3_l20` | `look_check/_archive/w3/scene20/260731_w3_l20` |
| `look_check/scene20/260731_w3_l20b` | `look_check/_archive/w3/scene20/260731_w3_l20b` |
| `look_check/scene20/260805_w3_hedgeswap` | `look_check/_archive/w3fix/scene20/260805_w3_hedgeswap` |
| `look_check/scene20/260806_w3_allview4` | `look_check/_archive/w3fix/scene20/260806_w3_allview4` |
| `look_check/scene20/260806_w3_allview5` | `look_check/_archive/w3fix/scene20/260806_w3_allview5` |
| `look_check/scene20/260806_w3_fixqueue2` | `look_check/_archive/w3fix/scene20/260806_w3_fixqueue2` |
| `look_check/scene20/v7_pt` | `look_check/_archive/w2/scene20/v7_pt` |
| `look_check/scene21/260731_w3_full` | `look_check/_archive/w3/scene21/260731_w3_full` |
| `look_check/scene21/260731_w3_l21_pre` | `look_check/_archive/w3/scene21/260731_w3_l21_pre` |
| `look_check/scene21/260806_w3_allview4` | `look_check/_archive/w3fix/scene21/260806_w3_allview4` |
| `look_check/scene21/260806_w3_allview5` | `look_check/_archive/w3fix/scene21/260806_w3_allview5` |
| `look_check/scene21/v7_pt` | `look_check/_archive/w2/scene21/v7_pt` |
| `look_check/sceneC1/260731_w3_full` | `look_check/_archive/w3/sceneC1/260731_w3_full` |
| `look_check/sceneC1/260806_w3_allview4` | `look_check/_archive/w3fix/sceneC1/260806_w3_allview4` |
| `look_check/sceneC1/260806_w3_allview5` | `look_check/_archive/w3fix/sceneC1/260806_w3_allview5` |
| `look_check/sceneC1/ctx1_pt` | `look_check/_archive/w2/sceneC1/ctx1_pt` |
| `look_check/sceneC1/ctx2_pt` | `look_check/_archive/w2/sceneC1/ctx2_pt` |
| `look_check/sceneC1/r3` | `look_check/_archive/w2/sceneC1/r3` |
| `look_check/sceneC1/r3_pt` | `look_check/_archive/w2/sceneC1/r3_pt` |
| `look_check/sceneC1/r4` | `look_check/_archive/w2/sceneC1/r4` |
| `look_check/sceneC1/r4_pt` | `look_check/_archive/w2/sceneC1/r4_pt` |
| `look_check/sceneC2/260731_w3_full` | `look_check/_archive/w3/sceneC2/260731_w3_full` |
| `look_check/sceneC2/260806_w3_allview4` | `look_check/_archive/w3fix/sceneC2/260806_w3_allview4` |
| `look_check/sceneC2/260806_w3_allview5` | `look_check/_archive/w3fix/sceneC2/260806_w3_allview5` |
| `look_check/sceneC4/260731_w3_full` | `look_check/_archive/w3/sceneC4/260731_w3_full` |
| `look_check/sceneC4/260806_w3_allview4` | `look_check/_archive/w3fix/sceneC4/260806_w3_allview4` |
| `look_check/sceneC4/260806_w3_allview5` | `look_check/_archive/w3fix/sceneC4/260806_w3_allview5` |
| `look_check/sceneC4/260806_w3_fixqueue2` | `look_check/_archive/w3fix/sceneC4/260806_w3_fixqueue2` |
| `look_check/sceneC4/ctx1_pt` | `look_check/_archive/w2/sceneC4/ctx1_pt` |
| `look_check/sceneC4/ctx2_pt` | `look_check/_archive/w2/sceneC4/ctx2_pt` |
| `look_check/sceneD1/260731_w3_full` | `look_check/_archive/w3/sceneD1/260731_w3_full` |
| `look_check/sceneD1/260806_w3_allview4` | `look_check/_archive/w3fix/sceneD1/260806_w3_allview4` |
| `look_check/sceneD1/260806_w3_allview5` | `look_check/_archive/w3fix/sceneD1/260806_w3_allview5` |
| `look_check/sceneD2/260731_w3_full` | `look_check/_archive/w3/sceneD2/260731_w3_full` |
| `look_check/sceneD2/260806_w3_allview4` | `look_check/_archive/w3fix/sceneD2/260806_w3_allview4` |
| `look_check/sceneD2/260806_w3_allview5` | `look_check/_archive/w3fix/sceneD2/260806_w3_allview5` |
| `look_check/sceneD2/r1` | `look_check/_archive/w2/sceneD2/r1` |
| `look_check/sceneD2/r1_pt` | `look_check/_archive/w2/sceneD2/r1_pt` |
| `look_check/sceneD2/r2` | `look_check/_archive/w2/sceneD2/r2` |
| `look_check/sceneD2/r2_pt` | `look_check/_archive/w2/sceneD2/r2_pt` |
| `look_check/sceneD3/260731_w3_full` | `look_check/_archive/w3/sceneD3/260731_w3_full` |
| `look_check/sceneD3/260806_w3_allview4` | `look_check/_archive/w3fix/sceneD3/260806_w3_allview4` |
| `look_check/sceneD3/260806_w3_allview5` | `look_check/_archive/w3fix/sceneD3/260806_w3_allview5` |
| `look_check/sceneD3/p0_base_pt` | `look_check/_archive/w2/sceneD3/p0_base_pt` |
| `look_check/sceneD3/p2g4_on` | `look_check/_archive/w2/sceneD3/p2g4_on` |
| `look_check/sceneD3/r2` | `look_check/_archive/w2/sceneD3/r2` |
| `look_check/sceneD3/r3` | `look_check/_archive/w2/sceneD3/r3` |
| `look_check/sceneD3/r4` | `look_check/_archive/w2/sceneD3/r4` |
| `look_check/sceneD3/r5` | `look_check/_archive/w2/sceneD3/r5` |
| `look_check/sceneD4/260731_w3_full` | `look_check/_archive/w3/sceneD4/260731_w3_full` |
| `look_check/sceneD4/260806_w3_allview4` | `look_check/_archive/w3fix/sceneD4/260806_w3_allview4` |
| `look_check/sceneD4/260806_w3_allview5` | `look_check/_archive/w3fix/sceneD4/260806_w3_allview5` |
| `look_check/sceneD4/ctx1_pt` | `look_check/_archive/w2/sceneD4/ctx1_pt` |
| `look_check/sceneD4/ctx2_pt` | `look_check/_archive/w2/sceneD4/ctx2_pt` |
| `look_check/sceneD4/r1` | `look_check/_archive/w2/sceneD4/r1` |
| `look_check/sceneD4/r1_pt` | `look_check/_archive/w2/sceneD4/r1_pt` |
| `look_check/sceneD4/r2_pt` | `look_check/_archive/w2/sceneD4/r2_pt` |
| `look_check/sceneN1/260730_lcfreeze_post` | `look_check/_archive/w2d/sceneN1/260730_lcfreeze_post` |
| `look_check/sceneN1/260730_lcfreeze_pre` | `look_check/_archive/w2d/sceneN1/260730_lcfreeze_pre` |
| `look_check/sceneN1/260731_w3_full` | `look_check/_archive/w3/sceneN1/260731_w3_full` |
| `look_check/sceneN1/260805_w3_hedgeswap` | `look_check/_archive/w3fix/sceneN1/260805_w3_hedgeswap` |
| `look_check/sceneN1/260806_w3_allview4` | `look_check/_archive/w3fix/sceneN1/260806_w3_allview4` |
| `look_check/sceneN1/260806_w3_allview5` | `look_check/_archive/w3fix/sceneN1/260806_w3_allview5` |
| `look_check/sceneN2/260731_w3_full` | `look_check/_archive/w3/sceneN2/260731_w3_full` |
| `look_check/sceneN2/260805_w3_hedgeswap` | `look_check/_archive/w3fix/sceneN2/260805_w3_hedgeswap` |
| `look_check/sceneN2/260806_w3_allview4` | `look_check/_archive/w3fix/sceneN2/260806_w3_allview4` |
| `look_check/sceneN2/260806_w3_allview5` | `look_check/_archive/w3fix/sceneN2/260806_w3_allview5` |
| `look_check/sceneN3/260731_w3_full` | `look_check/_archive/w3/sceneN3/260731_w3_full` |
| `look_check/sceneN3/260806_w3_allview4` | `look_check/_archive/w3fix/sceneN3/260806_w3_allview4` |
| `look_check/sceneN3/260806_w3_allview5` | `look_check/_archive/w3fix/sceneN3/260806_w3_allview5` |
| `look_check/sceneN4/260730_lcfreeze_post` | `look_check/_archive/w2d/sceneN4/260730_lcfreeze_post` |
| `look_check/sceneN4/260730_lcfreeze_pre` | `look_check/_archive/w2d/sceneN4/260730_lcfreeze_pre` |
| `look_check/sceneN4/260731_w3_full` | `look_check/_archive/w3/sceneN4/260731_w3_full` |
| `look_check/sceneN4/260806_w3_allview4` | `look_check/_archive/w3fix/sceneN4/260806_w3_allview4` |
| `look_check/sceneN4/260806_w3_allview5` | `look_check/_archive/w3fix/sceneN4/260806_w3_allview5` |
| `look_check/sceneN5/260731_w3_full` | `look_check/_archive/w3/sceneN5/260731_w3_full` |
| `look_check/sceneN5/260806_w3_allview4` | `look_check/_archive/w3fix/sceneN5/260806_w3_allview4` |
| `look_check/sceneN5/260806_w3_allview5` | `look_check/_archive/w3fix/sceneN5/260806_w3_allview5` |
| `look_check/_review/260731_w3_full` | `look_check/_review/w3/260731_w3_full` |
| `look_check/_review/260805_w3_doctrine` | `look_check/_review/w3/260805_w3_doctrine` |
| `look_check/_review/260805_w3_hedgeswap` | `look_check/_review/w3/260805_w3_hedgeswap` |
| `look_check/_review/260805_w3_s13fix` | `look_check/_review/w3/260805_w3_s13fix` |
| `look_check/_review/260805_w3_s13fix2` | `look_check/_review/w3/260805_w3_s13fix2` |
| `look_check/_review/260805_w3_s13fix3` | `look_check/_review/w3/260805_w3_s13fix3` |
| `look_check/_review/260805_w3_s13fix4` | `look_check/_review/w3/260805_w3_s13fix4` |
| `look_check/_review/260805_w3_s13fix5` | `look_check/_review/w3/260805_w3_s13fix5` |
| `look_check/_review/260806_w3_allview4` | `look_check/_review/w3/260806_w3_allview4` |
| `look_check/_review/260806_w3_allview5` | `look_check/_review/w3/260806_w3_allview5` |
| `look_check/_review/260806_w3_fixqueue` | `look_check/_review/w3/260806_w3_fixqueue` |
| `look_check/_review/260806_w3_fixqueue2` | `look_check/_review/w3/260806_w3_fixqueue2` |
| `look_check/_review/260806_w3_s13fix6` | `look_check/_review/w3/260806_w3_s13fix6` |
| `look_check/_review/260806_w3_s13fix7` | `look_check/_review/w3/260806_w3_s13fix7` |
| `look_check/_review/260807_w3_fixqueue3` | `look_check/_review/w3/260807_w3_fixqueue3` |
| `look_check/_review/260810_w3_s06collar` | `look_check/_review/w3/260810_w3_s06collar` |
| `look_check/_review/260810_w3_s06direct` | `look_check/_review/w3/260810_w3_s06direct` |
| `look_check/_review/260810_w3_s06endstair` | `look_check/_review/w3/260810_w3_s06endstair` |
| `look_check/_review/260811_w3_s06bay14` | `look_check/_review/w3/260811_w3_s06bay14` |
| `look_check/_review/260811_w3_s06glass` | `look_check/_review/w3/260811_w3_s06glass` |
| `look_check/_review/260811_w3_s06sweep` | `look_check/_review/w3/260811_w3_s06sweep` |
| `look_check/_review/260811_w3_s06trim` | `look_check/_review/w3/260811_w3_s06trim` |
| `look_check/_review/260811_w3_s06weld` | `look_check/_review/w3/260811_w3_s06weld` |
| `look_check/_review/260811_w3_s06wide` | `look_check/_review/w3/260811_w3_s06wide` |
| `look_check/_review/260811_w3_s11clean` | `look_check/_review/w3/260811_w3_s11clean` |
| `look_check/_review/260811_w3_s11flip` | `look_check/_review/w3/260811_w3_s11flip` |
| `look_check/_review/260811_w3_s11piers` | `look_check/_review/w3/260811_w3_s11piers` |
| `look_check/_review/260811_w3_s11ribbon` | `look_check/_review/w3/260811_w3_s11ribbon` |
| `look_check/_review/260811_w3_s13frost_a` | `look_check/_review/w3/260811_w3_s13frost_a` |
| `look_check/_review/260811_w3_s13frost_b` | `look_check/_review/w3/260811_w3_s13frost_b` |
| `look_check/_review/260811_w3_s13frost_c` | `look_check/_review/w3/260811_w3_s13frost_c` |
| `look_check/_review/260811_w3_s13frost_d` | `look_check/_review/w3/260811_w3_s13frost_d` |
| `look_check/_review/260811_w3_s13frost_e` | `look_check/_review/w3/260811_w3_s13frost_e` |
| `look_check/_review/260811_w3_s16road6` | `look_check/_review/w3/260811_w3_s16road6` |
| `look_check/_review/260811_w3_s16under` | `look_check/_review/w3/260811_w3_s16under` |
| `look_check/_review/260813_w4_n3wall` | `look_check/_review/w4/260813_w4_n3wall` |
| `look_check/_review/260813_w4_s01k5` | `look_check/_review/w4/260813_w4_s01k5` |
| `look_check/_review/260813_w4_s11tone` | `look_check/_review/w4/260813_w4_s11tone` |
| `look_check/_review/260813_w4_s13tone` | `look_check/_review/w4/260813_w4_s13tone` |
| `look_check/_review/260813_w4_s15villa` | `look_check/_review/w4/260813_w4_s15villa` |
| `look_check/_review/260813_w4_s16tone` | `look_check/_review/w4/260813_w4_s16tone` |
| `look_check/_review/260813_w4_s21civic` | `look_check/_review/w4/260813_w4_s21civic` |
| `look_check/_review/260814_w4_r1r2pilot` | `look_check/_review/w4/260814_w4_r1r2pilot` |
| `look_check/_review/260815_w4_hzbatch` | `look_check/_review/w4/260815_w4_hzbatch` |
| `look_check/_review/260815_w4_r4batch` | `look_check/_review/w4/260815_w4_r4batch` |
| `look_check/_review/260816_w4_final33` | `look_check/_review/w4/260816_w4_final33` |
| `look_check/_review/260817_w4_regfix` | `look_check/_review/w4/260817_w4_regfix` |
| `look_check/_review_w2` | `look_check/_review/w2` |
| `look_check/finalize_v3.log` | `look_check/logs/finalize_v3.log` |
| `look_check/partial_r4.log` | `look_check/logs/partial_r4.log` |
| `look_check/scene19_r5.log` | `look_check/logs/scene19_r5.log` |
| `look_check/spike_results.json` | `look_check/logs/spike_results.json` |
| `look_check/v5_keep_pt.log` | `look_check/logs/v5_keep_pt.log` |
| `look_check/v5_keep_rt.log` | `look_check/logs/v5_keep_rt.log` |
| `look_check/v6_all_rt.log` | `look_check/logs/v6_all_rt.log` |
| `look_check/v7_all_rt.log` | `look_check/logs/v7_all_rt.log` |
| `look_check/v7_pt13.log` | `look_check/logs/v7_pt13.log` |
| `look_check/v8_fix8_rt.log` | `look_check/logs/v8_fix8_rt.log` |
| `look_check/v8_pt7.log` | `look_check/logs/v8_pt7.log` |
| `look_check/v8_rt2_scene09.log` | `look_check/logs/v8_rt2_scene09.log` |

