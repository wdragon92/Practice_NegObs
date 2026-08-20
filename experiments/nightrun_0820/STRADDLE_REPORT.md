# STRADDLE_REPORT — B4 걸침·점유 진단 (nightrun_0820)

grid **PROVISIONAL-GRID-V1** · 5 sectors x 4 bands [0,2)/[2,5)/[5,8)/[8,12) m · cell index = band*5 + sector

inputs (all read-only, frozen): `experiments/dayrun_0820/annotations/labels_v1_full.json` · `split_v2_full.json` · `dataset_manifest_v2_full.json` · `runs/v2/rgb_s{42,43,44}/eval_test/per_frame.csv`

script: `experiments/nightrun_0820/code/b4_straddle.py` (env_seg, CPU only)

frame set = **on-arm frames carrying >=1 GT-positive cell**: test 327 / corpus 1038 (off-arm frames and on-arm frames with an empty GT set are outside every table below — they have no hazard instance to straddle with).

---

## (i) 위험 인스턴스 걸침률 — per-boundary

*Frame basis* = fraction of the frames above whose GT-positive set has cells on BOTH sides of that boundary, adjacent across it (same band for a sector boundary, same sector for a band boundary). *Unit basis* = the DAYRUN ②ⓒ basis generalised: for a band boundary the unit is a (frame, sector) pair with >=1 of the two cells positive, for a sector boundary a (frame, band) pair; the rate is the share of those units where BOTH cells are positive.

| boundary | test: frames crossing | test rate | test unit basis | corpus: frames | corpus rate | corpus unit basis |
|---|---|---|---|---|---|---|
| sector A/B | 249/327 | 76.1% | 486/612 = 79.4% | 702/1038 | 67.6% | 1311/1716 = 76.4% |
| sector B/C | 276/327 | 84.4% | 570/660 = 86.4% | 840/1038 | 80.9% | 1581/1914 = 82.6% |
| sector C/D | 258/327 | 78.9% | 528/624 = 84.6% | 855/1038 | 82.4% | 1524/1866 = 81.7% |
| sector D/E | 225/327 | 68.8% | 438/537 = 81.6% | 687/1038 | 66.2% | 1230/1623 = 75.8% |
| band 2 m (1/2) | 27/327 | 8.3% | 117/378 = 31.0% | 84/1038 | 8.1% | 330/1113 = 29.6% |
| band 5 m (2/3a) | 93/327 | 28.4% | 375/873 = 43.0% | 270/1038 | 26.0% | 1053/2382 = 44.2% |
| band 8 m (3a/3b) | 213/327 | 65.1% | 855/1341 = 63.8% | 579/1038 | 55.8% | 2148/4089 = 52.5% |

| summary | test | rate | corpus | rate |
|---|---|---|---|---|
| spans >=2 sectors | 303/327 | 92.7% | 1002/1038 | 96.5% |
| spans >=2 bands | 213/327 | 65.1% | 591/1038 | 56.9% |
| spans >=2 sectors OR >=2 bands (= *straddling* frame) | 306/327 | 93.6% | 1005/1038 | 96.8% |
| crosses >=1 boundary with ADJACENT cells | 306/327 | 93.6% | 1002/1038 | 96.5% |
| crosses the NEW 8 m boundary (3a & 3b positive in the same sector) | 213/327 | 65.1% | 579/1038 | 55.8% |
| has 3a and 3b positive anywhere (loose 8 m) | 213/327 | 65.1% | 582/1038 | 56.1% |

median GT-positive cells per frame: test 8 / corpus 6 · median sectors spanned 5 / 5 · median bands spanned 2 / 2

> **DAYRUN 62.7%와의 대조.** DAYRUN ②ⓒ의 62.7%는 *증강 이전* 라벨(`labels_v1.json`)의 **train·적격씬 on팔**에서 계산된 (프레임,섹터) 단위 값이다. 같은 파일의 on팔 전체로 넓히면 1419/2139 = 66.3%(531프레임)이고, 증강 후 전 코퍼스(`labels_v1_full.json`, 1038프레임)에서는 52.5%로 내려간다. 내려간 이유는 D21 보강 렌더가 원거리 E/H 프레임을 대량 추가했고 그중 상당수가 3b만 켜는 단일 밴드 프레임이기 때문이다 — 지표가 바뀐 게 아니라 코퍼스 구성이 바뀐 것이다. 논문에는 **범위를 명시한 하나의 수치**만 쓴다.

![straddle](../figures/b4_straddle.png)

**해석.** 걸침은 예외가 아니라 기본값이다. 온팔 위험 프레임의 93.6%(test) / 96.8%(corpus)가 두 개 이상의 섹터 또는 밴드에 걸쳐 있고, 중앙값 프레임은 8칸·5섹터를 동시에 켠다. 경계별로 보면 성격이 갈린다 — **섹터 경계는 거의 항상 걸쳐지고**(66–86%, 위험이 가로로 넓다), **밴드 경계는 거리에 따라 급격히 달라진다**: 2 m 경계 8.3% → 5 m 28.4% → **8 m 65.1%**(test). 즉 새로 만든 8 m 경계가 밴드 경계 중 압도적으로 자주 걸쳐지며, 단위(프레임x섹터) 기준으로도 63.8%(test) / 52.5%(corpus)가 3a·3b를 동시에 켠다. 이것은 격자 결함이 아니라 위험 인스턴스의 물리적 크기(도랑·계단 낭떠러지가 수 미터급)가 셀보다 크고, 원거리 웨지가 넓어 한 인스턴스가 두 밴드를 함께 덮기 때문이다. 두 가지 함의. ① '정답 칸이 하나라도 켜지면 검출'이라는 프레임 recall 정의는 관대한 규칙이 아니라 **한 인스턴스가 여러 칸에 흩어지는 이 격자에서 측정 가능한 최소 단위**다. ② 셀 단위 F1이 낮게 보이는 구조적 원인이기도 하다 — 한 인스턴스가 중앙값 8칸을 요구하는데 모델은 그중 가장 확신하는 칸만 켜기 때문이다. 본문에서 프레임 지표를 주 지표로, 셀 F1을 보조 지표로 두는 배치의 근거가 이 표다.

---

## (ii) miss x straddle 교차표 — RGB v2, tau = 0.5

`missed` = 그 프레임의 GT 양성 칸 중 어느 것도 p >= 0.5 에 도달하지 못함(= frame recall 실패). `straddling` = (i)의 straddle 정의(>=2 섹터 또는 >=2 밴드). 분모는 on-arm test 프레임 중 GT 양성 칸이 있는 것.

| seed | n | straddle&miss | straddle&hit | flat&miss | flat&hit | miss rate (straddle) | miss rate (flat) | diff [95% CI, 10k bootstrap] |
|---|---|---|---|---|---|---|---|---|
| 42 | 327 | 84 | 222 | 4 | 17 | 0.275 | 0.190 | +0.084 [-0.105, +0.249] |
| 43 | 327 | 22 | 284 | 8 | 13 | 0.072 | 0.381 | -0.309 [-0.526, -0.102] * |
| 44 | 327 | 135 | 171 | 12 | 9 | 0.441 | 0.571 | -0.130 [-0.351, +0.100] |
| **pooled** | 981 | 241 | 677 | 24 | 39 | 0.263 | 0.381 | -0.118 [-0.240, +0.005] |

`*` = CI가 0을 배제. `pooled` 행은 3시드 x 프레임을 단순 합친 것이라 독립 표본이 아니다 — 방향을 보는 용도이지 유의성 주장용이 아니다.

### 8 m 경계 한정 (신설 경계가 특별히 불리한가)

| seed | n | cross8&miss | cross8&hit | no8&miss | no8&hit | miss rate (8 m 걸침) | miss rate (미걸침) | diff [95% CI] |
|---|---|---|---|---|---|---|---|---|
| 42 | 327 | 31 | 182 | 57 | 57 | 0.146 | 0.500 | -0.354 [-0.456, -0.252] * |
| 43 | 327 | 13 | 200 | 17 | 97 | 0.061 | 0.149 | -0.088 [-0.163, -0.015] * |
| 44 | 327 | 89 | 124 | 58 | 56 | 0.418 | 0.509 | -0.091 [-0.203, +0.023] |

### H 티어 한정 부분표

| seed | n(H) | straddle&miss | straddle&hit | flat&miss | flat&hit | miss rate (straddle) | miss rate (flat) | diff [95% CI] |
|---|---|---|---|---|---|---|---|---|
| 42 | 96 | 35 | 49 | 4 | 8 | 0.417 | 0.333 | +0.083 [-0.230, +0.369] |
| 43 | 96 | 8 | 76 | 4 | 8 | 0.095 | 0.333 | -0.238 [-0.538, +0.036] |
| 44 | 96 | 30 | 54 | 9 | 3 | 0.357 | 0.750 | -0.393 [-0.648, -0.102] * |

**해석. 판정: '걸친 케이스를 더 놓친다'는 지지되지 않는다.** 시드별 diff(걸침 miss rate − 미걸침 miss rate)는 -0.309 ~ +0.084이고, 2/3 시드에서 음수, **CI가 0을 배제하며 양수인 시드는 0/3**, 음수 쪽으로 유의한 시드는 1/3이다. pooled 방향도 -0.118. 신설 8 m 경계만 떼어 봐도 같다(diff -0.354 ~ -0.088). 즉 어떤 시드에서도 걸침이 miss를 유의하게 **늘리지** 않는다.

이유는 (i)·(iii)이 함께 설명한다 — 걸친 프레임은 정의상 양성 칸이 많고(중앙값 8칸) 각 칸의 점유율도 높은 큰 인스턴스라, 그중 하나라도 τ를 넘길 기회가 많다. 프레임 recall은 max 규칙이므로 이 다중성이 곧 이득이다. 반대로 '걸치지 않은' 프레임은 작고 국소적인 단일 칸 인스턴스이고, 표본이 얇지만(21/327 = 6.4%) miss rate는 전반적으로 더 높다 — **진짜 취약 지점은 걸친 큰 위험이 아니라 작은 단일 칸 위험**이며, 이는 C1 hole 프로브가 겨냥하는 바로 그 형상이다.

다만 두 가지를 정직하게 남긴다. ① 미걸침 층이 21프레임뿐이라 검정력이 낮다 — CI가 넓고 시드 간 부호가 흔들린다(rgb 시드 자체의 recall 변동이 0.594~0.875로 크다는 SEED_TABLE의 사실과 같은 뿌리다). ② 따라서 이 표의 결론은 '걸침이 해롭다는 증거 없음'이지 '걸침이 이롭다'가 아니다. 결론적으로 걸침을 줄이려는 격자 재설계(더 굵은 셀 / 인스턴스 단위 라벨)는 지금 우선순위가 아니고, 8 m 분할이 걸침을 늘렸다는 사실도 recall 비용으로 이어지지 않았다.

---

## (iii) 양성 칸 내 위험 점유 면적비 · 과차단율

**추정기.** 라벨의 `cell_counts[c]` = 5 cm 하이트맵 차분 발자국 샘플 중 폴라 칸 c 안에 떨어진 개수 (labeler.py, `HM_DEFAULT step = 0.05 m`). 분모는 그 웨지가 담을 수 있는 5 cm 샘플의 해석적 개수

```
N(band) = 0.5 * dtheta * (r_out^2 - r_in^2) / step^2 ,  dtheta = 12.44 deg, step = 0.05 m
```

| band | range | wedge area (m^2) | N(band) samples | corpus max observed ratio |
|---|---|---|---|---|
| 1 | [0,2) m | 0.434 | 173.7 | 1.0018 |
| 2 | [2,5) m | 2.280 | 911.9 | 1.0067 |
| 3a | [5,8) m | 4.234 | 1693.5 | 1.0121 |
| 3b | [8,12) m | 8.685 | 3473.9 | 1.0101 |

관측 최대 비율이 1.00 근방(래스터화 여유 <1%)이라는 사실이 이 해석적 분모의 검증이다 — 완전히 채워진 칸이 실제로 N에 도달하고 넘지 않는다. 분위수 계산에서는 1.0으로 클립.

occupancy = 위험이 실제로 차지한 면적비 · **overblocking = 1 - occupancy** = 칸은 GT 양성으로 켜졌지만 실제로는 통행 가능한 면적의 비율.

| band | n GT+ cells (test) | occ Q1 | **occ median** | occ Q3 | **overblocking median** | n (corpus) | occ median (corpus) | overblock median (corpus) |
|---|---|---|---|---|---|---|---|---|
| 1 [0,2) | 117 | 0.115 | **0.288** | 0.472 | **0.712** | 333 | 0.121 | 0.879 |
| 2 [2,5) | 378 | 0.172 | **0.655** | 0.992 | **0.345** | 1110 | 0.625 | 0.375 |
| 3a [5,8) | 870 | 0.158 | **0.610** | 0.993 | **0.390** | 2325 | 0.521 | 0.479 |
| 3b [8,12) | 1326 | 0.306 | **0.861** | 0.999 | **0.139** | 3912 | 0.693 | 0.307 |
| **all** | 2691 | 0.204 | **0.726** | 0.998 | **0.274** | | | |

![occupancy](../figures/b4_occupancy.png)

**해석.** 점유율은 대체로 거리에 따라 올라간다 — band1 중앙값 0.29 · band2 중앙값 0.66 · band3a 중앙값 0.61 · band3b 중앙값 0.86 (band2와 3a는 사실상 같고, 근거리 band1이 뚝 떨어지고 최원거리 band3b가 뚜렷이 높다). 뒤집어 말하면 **과차단율은 근거리에서 가장 크고**(band1 71%, band2 34%) 원거리에서 가장 작다(band3b 14%). 사분위를 함께 보면 분포가 이봉성이라는 점도 중요하다 — Q3가 band2·3a·3b에서 모두 0.99 이상이라 '칸을 통째로 채우는 위험'이 다수이고, Q1은 0.16~0.31이라 '칸을 살짝 스치는 위험'도 상당수다. 중앙값 하나로 요약하면 이 이봉성이 가려진다. 원인은 기하다: 웨지 면적이 r^2로 커지는데 [8,12) m 웨지(8.7 m^2)는 우리 코퍼스의 도랑·낭떠러지형 위험이 통째로 삼키고, [0,2) m 웨지(0.43 m^2)는 위험의 가장자리만 스치는 경우가 많다. 실용적 함의 두 가지. ① **통행성 비용**: V1 격자로 예측한 위험 칸을 그대로 통행 금지로 쓰면 근거리에서는 통행 가능한 면적의 상당 부분을 함께 막는다 — 근거리 회피 판단에는 칸보다 고운 표현이 필요하다는 뜻이고, 이는 우리 격자가 '조기 경보'용이지 '국소 경로계획'용이 아니라는 위치 설정의 정량적 근거다. ② **hole 타입 일반화의 사전 경고**: 이 코퍼스의 위험은 폭이 넓어 원거리 칸을 가득 채우지만, 개구 0.5–1.5 m급 hole은 [8,12) 칸의 점유율이 1–3%대에 그친다(0.5 m x 0.5 m = 100 샘플 / 3474). 즉 hole에서는 '칸이 켜진다'는 것의 물리적 의미가 지금 코퍼스와 질적으로 다르고, C1 제로샷 프로브의 recall은 이 점유율 차이를 함께 보고해야 해석된다. 한계 절에는 이 두 문장을 그대로 넣는다.

