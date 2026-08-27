# P0-3 라벨 모집단 센서스 — 씬 41개 × 렌더 라운드 196개

- 작성 2026-08-28 · 브리프 `Docs/briefs/edge_relabel_brief_v6.md` §4 Phase 0-3 · 게이트 **G0** 상신용
- 원자료: `experiments/e1_0827/reports/census.csv` (779행 = 라운드×split×씬)
- 성격: **읽기 전용 실측.** 렌더·라벨링·학습 없음(P3). 프레임 이미지는 한 장도 열지 않았다 — 사이드카 개수와 `heightmap*`·`variation.json` 만 읽었다.

---

## 승용 요약 (5문장)

1. 실물 데이터는 **라운드 196개 · 프레임 13,515장**이고, 이 중 브리프의 기본 제안(**위험-ON · 단서 미제거**)에 해당하는 것은 **씬 41개 · 라운드 62개 · 프레임 4,575장**이다.
2. 가장 큰 문제는 **씬-버전 정합**이다 — 4,575장 중 **2,679장(58.6%)이 렌더 이후에 씬 코드가 바뀐** 프레임이라 재렌더 대상이고, 정합이 확인된 것은 **1,896장(41.4%)** 뿐이다. 원인은 08-24의 두 커밋(`50de4892` 05:44 · `bc200b95` 11:28)이 씬 20개의 코드를 고친 것이다.
3. seg 사이드카(`*.idseg.npz`)는 **2,407장에만 있고 2,168장에 없다.** 없으면 H_cand의 "무엇이 가렸는가"를 물을 수 없어 가림물이 `unknown` 이 된다.
4. **정합 + seg + depth·heightmap을 모두 갖춘 씬은 41개 중 11개**(scene01·04·09 / H1·H2·H3·H6·H7·L1·N9·N11)뿐이다. 나머지 30개 씬은 파일럿에 쓰려면 재렌더가 필요하다.
5. NEG 공급원(위험-OFF 팔) 3,946장은 **같은 카메라 포즈의 쌍둥이**임을 실측으로 확인했다(포즈 24/24 완전 일치) — 근사중복 누수 위험이 크다. ❓G0-4 참조.

---

## 1. 모집단 정의와 총계

### 1.1 씬 목록의 근거

정본 렌더 진입점 `scripts/run_data_render.py:60` 이 씬을 색인하는 코드는 이것뿐이다:

```python
for sub in ("main", "batch1"):
    for f in sorted(glob.glob(os.path.join(REPO, "scenes", sub, "scene*.py"))):
```

→ **`scenes/main` 29개 + `scenes/batch1` 12개 = 41개**가 렌더 가능한 전부다. `scenes/archive_v3`(7개)와 `scenes/probe`(3개)는 이 색인에 없어 **정본 렌더로 도달할 수 없다**(archive_v3는 브리프의 기본 제외와 일치, probe는 별도 경로로 렌더된 3개 라운드가 데이터에 남아 있다 — §5에서 별도 취급).

`scenes/archive_v3` 의 7개 씬은 `scene06/07/08/10/11/12/13` 이라는 **id가 `scenes/main` 과 충돌**한다. 데이터의 `scene06` 이 어느 쪽인지 헷갈릴 수 있으나, 위 색인 코드에 의해 **항상 `scenes/main` 쪽**이다.

### 1.2 팔(arm) 해독 — 실측

`heightmap_meta.json` 의 `arm_config` 필드가 팔의 정답이다. 프레임 수로 집계한 실측 프로필:

| 라운드명 접미 | `hazard_*` | `cue_* = false` | `keep_dressing` | 프레임 | 뜻 |
|---|---|---|---|---:|---|
| `_on` (v2) | True | 없음 | 없음 | 2,144 | 위험O·단서O |
| `_off` (v2) | False | 없음 | 없음 | 2,144 | 위험X (단서는 자동으로 함께 사라짐) |
| `_A` (v3) | True | 없음 | 없음 | 1,091 | A = 위험O·단서O |
| `_B` (v3) | True | 있음 | 없음 | 1,136 | B = 위험O·단서X |
| `_C` (v3) | False | 없음 | True | 1,336 | C = 위험X·단서O |
| `_D` (v3) | False | 있음 | 없음 | 1,304 | D = 위험X·단서X |
| 접미 없음 | 혼합 | 혼합 | 혼합 | 3,284 | boost·probe·cuecls·segfill 계열 |

**기본 제안 모집단 = `hazard_* 가 참이고 cue_* 를 끄지 않은` 프레임** = **4,575장 / 62 라운드 / 41 씬**.
(더 엄격하게 `arm_config` 에 `hazard_*` 키 하나만 있는 것으로 좁히면 4,431장 — 차이 144장은 `cue_scene_dressing` 등 부가 키가 붙은 boost 계열이다.)

### 1.3 총계

| 항목 | 값 |
|---|---:|
| 데이터 라운드 (dataset/ 전체, `_archive` 포함) | **196** (+ 빈 라운드 `260816_dataall` 1개 = `ROUNDS.json` 197행) |
| 프레임 (RGB png) 총계 | **13,515** |
| depth(`*.depth.npy`) 있는 프레임 | 13,065 |
| seg(`*.idseg.npz`) 있는 프레임 | 8,071 |
| 경로 (a)+(b) 가능 프레임 (depth 전량 + heightmap 존재) | **13,027** |
| — 기본 제안 모집단(위험-ON·단서 미제거) | **4,575** (씬 41 · 라운드 62) |
| — 그중 (a)+(b) 가능 | **4,575** (100%) |
| — 그중 seg 있음 / 없음 | **2,407 / 2,168** |
| — 그중 씬-버전 정합 / 불일치 | **1,896 / 2,679** |
| NEG 후보(위험-OFF·단서 미제거) | **3,946** (라운드 44) |

## 2. 사이드카 실물 형식 (v2·v3 라운드 실사)

라운드 디렉터리 구조는 두 세대가 같다: `dataset/<그룹>/<라운드>/<split>/<씬>/`.
씬 디렉터리 안:

| 파일 | v2 (`260819_main_on`) | v3 (`260824_v3w3_extbase_A`) | 내용 |
|---|---|---|---|
| RGB | `L0__s20260819__0000.png` | `L0__s20260823__0000.png` | `<조건>__s<시드>__<번호>.png` |
| depth | `….depth.npy` | 있음 | float 배열 |
| **seg** | `….idseg.npz` | 있음 | `idseg`(1080×1920 uint16) + `idToLabels`(id→USD 프림 경로 JSON) + `annotator="instance_id_segmentation"` |
| 높이장 | `heightmap.npy` + `heightmap_meta.json` | 있음 | **씬 디렉터리당 1개** (프레임당 아님). 격자 0.05 m · 321×321 · x[-2,14] y[-8,8] |
| 카메라 | `variation.json` | 있음 | `cuts[].cam = {eye, ground_z, d, h_rel, yaw, pitch, roll, hfov, focal, aperture, tier}` + `light`·`expo`·`render` |
| 라운드 매니페스트 | `manifest.json` (라운드 루트) | **없음** (v3 라운드에는 루트 매니페스트가 없다) | v2는 `run`·`started`·`git_head`·씬별 split 을 담는다 |

**H_cand에 필요한 프림 신원은 `idToLabels` 에 있다** — 예: `{"6": "/World/Scene01/Band_0", "393": "/World/Scene01/Step_1", …}`. 이것이 없는 프레임에서는 §2 규칙 3의 "지면·계단이 아닌 외부 프림" 판정이 불가능해 가림물이 `unknown` 이 된다.

> **주의 (seg 백필)**: v2 라운드 30개 씬-디렉터리의 `.idseg.npz` 는 **원 렌더의 산출이 아니라 08-23 재렌더(`260826_v3a_segfill`)에서 옮겨 심은 것**이다(`idseg_backfill.json` 이 그 사실을 기록한다). 기하 대응(heightmap sha · n_prims · arm_config · 포즈 7키 · 컷별 depth sha)은 확인됐지만 **RGB PNG sha는 일치하지 않는다**(경로추적 렌더는 프로세스 간 비트 재현이 되지 않는다 — 대조 76건 중 0건 일치). 해당 30개: `260819_main_on` 16 · `260820_boost_e_on` 8 · `260820_boost_e2_on` 4 · `260820_boost_h_on` 1 · `260820_boost_e_on_g7fixM` 1. **파일럿 후보 scene01/val · scene04/train · scene09/train 이 전부 여기 해당한다** — ❓G0-5.

## 3. 씬-버전 정합 검사

### 3.1 방법 [방법]

씬 파일의 mtime은 08-27 독스트링 편집으로 전부 갱신됐으므로 **쓸 수 없다.** 대신 git 을 썼다:

1. `git log --format="%H %cI" dfeb9f3 -- <씬파일>` 로 그 파일을 건드린 커밋을 최신순으로 얻는다.
2. 각 커밋에서 **부모와 이 커밋의 파일 내용을 AST로 파싱해 독스트링을 제거한 뒤 비교**한다.
3. 다르면 그것이 **마지막 코드 변경 커밋**이다(같으면 독스트링만 바뀐 커밋이므로 건너뛴다).
4. 라운드의 **실제 렌더 개시 시각**(`experiments/v3_0823/ROUND_LEDGER.md` — 라운드명 접두 날짜가 아니라 실측 mtime 기반)과 비교해 **렌더 개시 < 마지막 코드 변경**이면 `정합 불일치 → 재렌더 대상`.

> **⚠ 한계**: 커밋 시각은 실제 편집 시각의 **상한**이다. 편집이 커밋보다 며칠 앞설 수 있으므로, "불일치" 판정은 **보수적(과다 검출 쪽)** 이다. 반대로 "정합" 판정은 안전한 쪽이다. 커밋 이력에 없는 편집(미커밋 상태로 렌더)은 이 방법으로 잡히지 않는다.

### 3.2 정합을 깬 두 커밋

| 커밋 | 시각(KST) | 메시지 | 코드가 바뀐 씬 |
|---|---|---|---|
| `50de4892` | 2026-08-24 05:44 | C 웨이브 완주(D88): 수리 3종+15씬 포트+816컷 | scene02·03·06·08·10·12·16·17·20·21 (10개) |
| `bc200b95` | 2026-08-24 11:28 | 정리 커밋 … batch1 keep_dressing 포트 5씬(D88 누락분) | sceneC1·C4·D1·D2·D3 (5개) |
| `ef78600b` | 2026-08-24 01:59 | 규정 감사 완료(D85): 6씬 수정 | sceneH1·H3·H6·L1 (+H2·H7 은 다음 줄) |
| `82d22cf5` | 2026-08-24 02:35 | 규정 마감(D86) | sceneH2·H7·N9·N11 |

`50de4892`·`bc200b95` 이후에 렌더된 라운드는 **하나도 없다**(실측: `ROUND_LEDGER` 의 최신 렌더 종료가 08-24 07:29). 따라서 **그 15개 씬은 정합 라운드가 0개**다.

### 3.3 씬별 센서스 표 (기본 제안 모집단 기준)

| 씬 | 모듈 | 위험 종류 (독스트링 인용) | ON 프레임 | 라운드 | seg 有 | seg 필요 | 정합 | 불일치 | 최종 코드변경 | NEG후보(OFF) |
|---|---|---|---:|---:|---:|---:|---:|---:|---|---:|
| `scene01` | `main` | upper and lower levels are the same granite family, so the stair level | 53 | 4 | 49 | 4 | 53 | 0 | 2026-08-13 18:04 | 49 |
| `scene02` | `main` | T3 underpass (fully equipped × dark lower level) | 53 | 4 | 48 | 5 | 0 | 53 | 2026-08-24 05:44 | 49 |
| `scene03` | `main` | T5 river levee **no railing × water-surface anchor**. | 221 | 11 | 144 | 77 | 0 | 221 | 2026-08-24 05:44 | 193 |
| `scene04` | `main` | an **irregular-riser sleeper stair** descending a gently sloped park bank. | 228 | 11 | 144 | 84 | 228 | 0 | 2026-08-15 02:40 | 217 |
| `scene05` | `main` | scene05_amphitheater.py — NegObs synthetic scene 5: neighbourhood-park outdoor theatre | 144 | 6 | 0 | 144 | 144 | 0 | 2026-08-16 00:27 | 120 |
| `scene06` | `main` | R1 urban pedestrian overpass, circular spiral entry (inherits the curvature self-occlusion axis) | 53 | 4 | 24 | 29 | 0 | 53 | 2026-08-24 05:44 | 49 |
| `scene07` | `main` | R2 (v5 redesign) — **discrete natural stepping stones** (large slabs set sparsely) | 192 | 8 | 0 | 192 | 192 | 0 | 2026-08-15 02:40 | 168 |
| `scene08` | `main` | circular sunken plaza (bowl) cut into a city-block plaza. **v7 is a full curved | 174 | 10 | 48 | 126 | 0 | 174 | 2026-08-24 05:44 | 145 |
| `scene09` | `main` | ultra-wide waterfront stairs **ultra-wide stone stairs x a horizontal water boundary**. | 220 | 10 | 120 | 100 | 220 | 0 | 2026-08-15 02:40 | 169 |
| `scene10` | `main` | R5 (v5 redesign) — timber deck zigzag stair (inherits the open-riser see-through cue) | 53 | 4 | 48 | 5 | 0 | 53 | 2026-08-24 05:44 | 49 |
| `scene11` | `main` | R6 steel footbridge, **H-plan** (S11-H) over 6 lanes (inherits the | 24 | 1 | 0 | 24 | 24 | 0 | 2026-08-13 18:04 | 24 |
| `scene12` | `main` | cantilever axis (inherits the geometry axis of the old T17 cliff | 362 | 17 | 144 | 218 | 0 | 362 | 2026-08-24 05:44 | 289 |
| `scene13` | `main` | T10 family redefined — the spiral parking ramp (old scene13, archive_v3) is | 24 | 1 | 0 | 24 | 24 | 0 | 2026-08-14 23:29 | 24 |
| `scene14` | `main` | T14 Potemkin-style illusory grand stair (40 steps, 3 landings, tapered widening) | 147 | 8 | 0 | 147 | 147 | 0 | 2026-08-15 02:40 | 96 |
| `scene15` | `main` | T15 alley labyrinth (wall-compressed perspective × drop hidden by a narrow field of view) | 144 | 6 | 0 | 144 | 144 | 0 | 2026-08-16 00:27 | 96 |
| `scene16` | `main` | T20 canopy stair (the inverse of T3 — the upper shadow band is the danger signal) | 53 | 4 | 48 | 5 | 0 | 53 | 2026-08-24 05:44 | 49 |
| `scene17` | `main` | T21 ramp-stair contrast pair (same 3.2 m drop — stairs vs drivable grade) | 265 | 12 | 144 | 121 | 0 | 265 | 2026-08-24 05:44 | 193 |
| `scene18` | `main` | scene18_wavy_artstair.py - NegObs synthetic scene 18: **beach access stair** | 144 | 6 | 0 | 144 | 144 | 0 | 2026-08-15 02:40 | 120 |
| `scene19` | `main` | scene19_fan_winder.py — NegObs synthetic scene 19: T7 fan corner stairs (winder) | 24 | 1 | 0 | 24 | 24 | 0 | 2026-08-14 23:29 | 24 |
| `scene20` | `main` | T8 diagonal oblique (alignment assumption breaks down) | 361 | 14 | 144 | 217 | 0 | 361 | 2026-08-24 05:44 | 265 |
| `scene21` | `main` | T2 monumental entrance grand stair (multi-step self-occlusion) | 53 | 4 | 48 | 5 | 0 | 53 | 2026-08-24 05:44 | 49 |
| `sceneC1` | `batch1` | C1 condition variant - existing straight-stair geometry + a snow environment layer (core batch1 scene) | 149 | 8 | 96 | 53 | 0 | 149 | 2026-08-24 11:28 | 121 |
| `sceneC2` | `batch1` | C2 condition variant (geometry invariant · cue buried under an environment layer) | 24 | 1 | 0 | 24 | 0 | 24 | 2026-08-21 04:19 | 48 |
| `sceneC4` | `batch1` | C4 condition variant — wide granite stair geometry + a wetness (material) layer | 221 | 11 | 144 | 77 | 0 | 221 | 2026-08-24 11:28 | 193 |
| `sceneD1` | `batch1` | D1 non-stair drop - logistics loading platform dock edge (drop 1.2 m) | 53 | 4 | 48 | 5 | 0 | 53 | 2026-08-24 11:28 | 49 |
| `sceneD2` | `batch1` | D2 non-stair drop - an unguarded opening in a frame-stage floor slab (drop 3.0 m) | 53 | 4 | 48 | 5 | 0 | 53 | 2026-08-24 11:28 | 49 |
| `sceneD3` | `batch1` | D3 non-stair drop (class extension - a roadside longitudinal open channel) | 53 | 4 | 48 | 5 | 0 | 53 | 2026-08-24 11:28 | 49 |
| `sceneD4` | `batch1` | D4 non-stair drop (platform edge → track bed, drop 1.15 m) | 24 | 1 | 0 | 24 | 24 | 0 | 2026-08-15 00:19 | 24 |
| `sceneH1` | `main` | **둔덕형 자기가림 (paired-H)** · 생활권 = **제방·수변(뚝방)** | 95 | 9 | 95 | 0 | 49 | 46 | 2026-08-24 01:59 | 92 |
| `sceneH2` | `main` | **계단참형 자기가림 (paired-H)** · 생활권 = **캠퍼스 경로** | 111 | 10 | 111 | 0 | 49 | 62 | 2026-08-24 02:35 | 108 |
| `sceneH3` | `main` | **복도 굴절형 자기가림 (paired-H)** · 생활권 = **보도** | 103 | 9 | 103 | 0 | 49 | 54 | 2026-08-24 01:59 | 100 |
| `sceneH6` | `main` | **둔덕형 자기가림 (paired-H)** · 생활권 = **제방·수변(뚝방)** | 99 | 9 | 99 | 0 | 73 | 26 | 2026-08-24 01:59 | 88 |
| `sceneH7` | `main` | **복도 굴절형 자기가림 (paired-H)** · 생활권 = **보도** | 83 | 9 | 83 | 0 | 49 | 34 | 2026-08-24 02:35 | 72 |
| `sceneL1` | `main` | **측방 위험 (lateral)** · 생활권 = **제방·수변(뚝방)** | 103 | 9 | 103 | 0 | 49 | 54 | 2026-08-24 01:59 | 100 |
| `sceneN1` | `batch1` | N1 Hard Negative - a dark band crossing a flat plaza (GT = no drop in any pixel) | 28 | 2 | 0 | 28 | 28 | 0 | 2026-08-14 23:29 | 24 |
| `sceneN11` | `main` | **N-cue (단서 有 · 위험 無)** · 생활권 = **보도** | 138 | 10 | 138 | 0 | 49 | 89 | 2026-08-24 02:35 | 136 |
| `sceneN2` | `batch1` | N2 Hard Negative - a new asphalt patch on flat pavement (GT = no drop in any pixel) | 28 | 2 | 0 | 28 | 28 | 0 | 2026-08-07 19:04 | 24 |
| `sceneN3` | `batch1` | N3 hard negative — anamorphic trompe-l'oeil · **GT = "no drop" in every pixel** | 24 | 1 | 0 | 24 | 0 | 24 | 2026-08-21 04:19 | 48 |
| `sceneN4` | `batch1` | N4 hard negative - a walkable gentle slope (5%) · **GT = "no drop" on every pixel** | 28 | 2 | 0 | 28 | 28 | 0 | 2026-08-15 02:40 | 24 |
| `sceneN5` | `batch1` | N5 Hard Negative - flush drainage grating + cast iron manholes (GT = no drop on any pixel) | 28 | 2 | 0 | 28 | 28 | 0 | 2026-08-15 02:40 | 24 |
| `sceneN9` | `main` | **N-cue (단서 有 · 위험 無)** · 생활권 = **보도** | 138 | 10 | 138 | 0 | 49 | 89 | 2026-08-24 02:35 | 136 |
| **합계 41씬** | | | **4575** | **62** | **2407** | **2168** | **1896** | **2679** | | **3946** |

**정합 라운드가 있는 씬 = 24개**, **정합 + seg + depth·heightmap이 전부 갖춰진 씬 = 11개** — `scene01` `scene04` `scene09` `sceneH1` `sceneH2` `sceneH3` `sceneH6` `sceneH7` `sceneL1` `sceneN9` `sceneN11`.

씬별 정합 라운드 목록(상위 4개까지)은 `census.csv` 의 `consistency` 열로 필터하면 그대로 나온다. 대표:

| 씬 | 정합·seg 완비 라운드 | 프레임 |
|---|---|---:|
| `scene01` | `260819_main_on/val`, `260826_v3a_segfill/val` | 24 + 24 |
| `scene04` | `260819_main_on/train`, `260820_boost_e_on/train` | 24 + 24 |
| `scene09` | `260819_main_on/train` | 24 |
| `sceneH1`·`H2`·`H3`·`L1`·`N9`·`N11` | `260824_v3w3_extbase_A/test` (+`exth_A`/`extlat_A`/`extb2_A`) | 각 24 |
| `sceneH6`·`H7` | `260824_v3w2_h67base_A/val` (+`h67h_A`, `h67h2_A`) | 각 24 |

## 4. 경로 (a)/(b) 불가 · seg 부재 라운드

### 4.1 depth 또는 heightmap이 없는 프레임

전체 13,515장 중 **488장(29개 씬-디렉터리)** 이 depth 개수가 RGB 개수와 다르거나 heightmap이 없다. **기본 제안 모집단 안에는 0장** — 즉 위험-ON 프레임은 전부 (a)/(b) 입력을 갖추고 있다.

| 라운드 | 그룹 | 미비 프레임 | 비고 |
|---|---|---:|---|
| `260815_datapilot` · `260815_datapilot_aug` | `_archive/pilots` | 120 + 120 | depth·heightmap 없음. `datapilot_aug` 는 `variation.json` 도 없음(5개 씬 120장) |
| `260730_data_mini` 외 scene_dev_2607 라운드 9개 | `_archive/scene_dev_2607` | 200 | 07-30 세대, depth 미도입 |
| `260819_main_off` | `v2_corpus` | 24 | 1개 씬 디렉터리에서 depth 개수 불일치 |
| `260823_v3p5_h3l1reg_D` | `v3_scene_build` | 16 | |
| `260824_handson` · `260827_handson` | `misc` | 2 + 4 | 실습 렌더(가이드 검증용) |
| `260819_patchprobe_noenv`·`noenv2` | `_archive/_delete_candidates` | 1 + 1 | |

### 4.2 heightmap이 있어도 **쓸모없는** 경우 — 새로 발견

`heightmap_meta.json` 의 `source` 는 `variation_kit.AabbPrefilter.ground_z(top=60.0)` 다. 즉 높이장은 **모든 프림의 AABB 상면 포락(envelope)** 이지 "보행면"이 아니다. 실측으로 두 가지 결과가 나왔다:

- **`sceneD4`(지하철 승강장, 낙차 1.15 m)의 위험-ON 높이장은 전 격자가 z = 3.7364 로 완전히 평평하다** (relief = 0.000 m, 103,041셀 전부 동일값). 이 씬은 라이브러리 유일의 완전 실내 씬이라 **천장 슬래브의 AABB가 창 전체를 덮었다.** → 경로 (a)로는 D4의 낙차를 **원리적으로 못 찾는다**(실측: edge 후보 셀 0개).
- 반대로 **낙차가 없어야 할 하드네거티브에서 edge 후보가 나온다** — `sceneN1` 248셀(거리 11.5~20 m) · `sceneN3` 872셀 · `sceneN4` 2,662셀 · `sceneN5` 394셀. 이들은 벤치·화단·옹벽·배경 건물의 AABB 상면 모서리다. (`sceneN2` 는 0셀 — 실제로 평평하다, relief 0.018 m.)

위험-ON 프레임 중 높이장 기복(z_max−z_min)이 0.30 m 미만인 것은 **52장**(`sceneD4` 24 + `sceneN2` 28)이다.

→ **경로 (a)는 "보행면"을 AABB 포락에서 분리하는 규칙을 반드시 필요로 한다.** 이것은 상수 대장의 `WALK_*` 항목(파이프라인 골격 담당)과 직결되며, 본 센서스는 그 규칙을 **정하지 않는다**(P1). ❓G0-6.

### 4.3 seg 사이드카가 없어 H_cand 가림물이 `unknown` 이 되는 프레임

기본 제안 모집단 4,575장 중 **2,168장(47.4%)에 seg가 없다.** 씬별 재렌더 필요량(§3.3 표 "seg 필요" 열)의 큰 순서:

| 씬 | seg 필요 프레임 | 씬 | seg 필요 프레임 |
|---|---:|---|---:|
| `scene12` | 218 | `scene07` | 192 |
| `scene20` | 217 | `scene14` | 147 |
| `scene05` | 144 | `scene15` | 144 |
| `scene18` | 144 | `scene17` | 121 |
| `scene08` | 126 | `scene09` | 100 |
| `scene04` | 84 | `scene03`·`sceneC4` | 각 77 |
| `sceneC1` | 53 | `scene06` | 29 |
| `sceneN1`·`N2`·`N4`·`N5` | 각 28 | `scene11`·`13`·`19`·`C2`·`D4`·`N3` | 각 24 |
| `scene02`·`10`·`16`·`21`·`D1`·`D2`·`D3` | 각 5 | `scene01` | 4 |
| `sceneH1`·`H2`·`H3`·`H6`·`H7`·`L1`·`N9`·`N11` | **0** (전량 보유) | | |

seg를 전량 보유한 그룹은 `v3_library`(3,384/3,384) · `v3_test_ext`(1,152/1,152) · `_archive/v3_scene_build`(1,168/1,168) 다. 반대로 `cueoff`(696장) · `v2_probes`(192+448장)는 seg가 **0장**이다.

## 5. NEG 공급원과 쌍둥이 근사중복 누수

위험-OFF·단서 미제거 프레임은 **3,946장 / 44 라운드**(v2 `*_off` + v3 `C` 팔 + 접미 없는 등가 라운드)이고, 그중 depth+heightmap 보유 3,922장, seg 보유 1,682장, 씬-버전 정합 1,683장이다. 씬별 수량은 §3.3 표의 마지막 열이다.

**누수 위험 (실측 근거 포함)**: 2×2 4팔 설계는 **같은 카메라 포즈를 팔마다 다시 찍는다.** 실측으로 확인했다 — `260819_main_on/train/scene03` 과 `260819_main_off/train/scene03` 은 파일명 24개가 모두 같고 `cam.eye` 좌표가 **24/24 완전히 동일**하다. v3도 같다(`260824_v3w3_extbase_A` 와 `…_C` 의 sceneH1: 24/24 동일). 즉 OFF 프레임은 ON 프레임과 **화소 수준에서 거의 같은 사진이고, 다른 것은 낙차 기하 하나뿐**이다. 이것을 NEG로 본대에 넣으면 (ⓐ) train/test 를 씬 단위로 갈라도 같은 포즈의 ON/OFF가 양쪽에 흩어져 **모델이 "이 구도는 낙차 있음/없음"을 외울 수 있고**, (ⓑ) NEG가 전부 "낙차만 지운 합성 대조군"이라 **현실의 음성 장면 분포와 다르다**(진짜 음성은 하드네거티브 N1~N5·N9·N11 쪽이다). 반대로 OFF를 버리면 NEG는 하드네거티브 7씬(위험-ON 표기이지만 실측 단차가 0.3 m 미만인 것 포함)과 "낙차가 화면 밖" 프레임에만 의존하게 된다.

**하드네거티브의 실측 단차** (참고): `sceneN9` 는 승강장 연석 0.15–0.25 m, `sceneN11` 은 함몰 0.150 m로 **둘 다 0.3 m 문턱 미만**이다(씬 독스트링). `arm_config` 에 `hazard_platform_edge: true` / `hazard_planting_bed: true` 로 적혀 있지만, 이는 **씬의 팔 스위치 이름**일 뿐 "0.3 m 이상 낙차가 있다"는 뜻이 아니다. 새 정의로는 두 씬 전부 **NEG** 가 될 가능성이 높다 — 라벨링으로 확인할 사항이다.

## 6. `scenes/archive_v3` · `scenes/probe` (기본 제외분)

| 대상 | 씬 | 데이터 | 처분 |
|---|---|---|---|
| `scenes/archive_v3/` | 7개 (`scene06/07/08/10/11/12/13` — id가 `scenes/main`과 충돌) | **없음** — 정본 렌더가 색인하지 않으므로 도달 불가 | 브리프대로 기본 제외 |
| `scenes/probe/` | 3개 (`probeH1_near_hole`·`probeH2_offpath_hole`·`probeH3_hidden_hole`) | 라운드 2개(`260821_probe_on` · `260821_probe_off`, 그룹 `v2_probes`) · 프레임 **144장**, depth 144/144 · heightmap 6/6 · **seg 0장** | ❓G0-3 |

## 7. ❓ 결재란 (G0)

| 번호 | 항목 | 담당 |
|---|---|---|
| **❓G0-1** | 모집단 = **위험-ON · 단서 미제거 4,575장(41씬·62라운드)** 로 확정하는가? [클로드 제안: 예 — 브리프 §4-3 기본 제안 그대로] 대안: (가) 더 엄격히 `arm_config`에 hazard 키만 있는 4,431장 (나) B팔(위험O·단서X) 1,136장을 더해 5,711장 — B팔은 "단서 없이 낙차만" 이라 edge 라벨 자체에는 영향이 없다 | 승용 |
| **❓G0-2** | **NEG를 off-팔에서 공급하는가?** [클로드 제안: **아니오** — §5의 쌍둥이 누수(포즈 24/24 동일 실측) 때문]. 대안 3안: (가) off-팔 전량 3,946장 사용 (나) off-팔을 쓰되 **ON과 같은 split에만** 넣어 누수 경로를 막는다 (다) NEG는 "낙차가 화면 밖" 프레임 + 하드네거티브 7씬으로만 만든다 | 승용 |
| **❓G0-3** | `scenes/probe` 3씬 144장을 모집단에 넣는가? [클로드 제안: 아니오 — seg 0장이라 H_cand 판정이 불가능하고, 브리프의 씬 목록(main·batch1)에도 없다] | 승용 |
| **❓G0-4** | **정합 불일치 2,679장(58.6%)의 처분**: (가) 전부 재렌더 대상으로 빼고 정합 1,896장으로만 파일럿·전량을 간다 (나) 불일치라도 라벨하고 "재렌더 후 재라벨" 을 예약한다 (다) 씬별로 diff를 열어 "위험 기하가 실제로 바뀐 씬"만 골라낸다 — (다)는 씬 15개의 코드 diff를 사람이 읽어야 하며 본 세션은 그 판단을 하지 않았다 | 승용 |
| **❓G0-5** | **seg 백필분(v2 30개 씬-디렉터리)** 을 정상 seg로 인정하는가? RGB PNG sha는 원 렌더와 다르고, 기하 대응만 검증됐다. [클로드: 판단 유보 — 파일럿 후보 3씬이 전부 여기 해당하므로 이 답에 따라 파일럿 씬이 바뀐다] | 승용 |
| **❓G0-6** | 높이장이 **AABB 포락**이라 (ⓐ) 실내 씬 `sceneD4` 는 천장에 덮여 낙차가 안 보이고(edge 후보 0셀) (ⓑ) 하드네거티브에서 벤치·옹벽 모서리가 edge 후보로 잡힌다. "보행면"을 포락에서 분리하는 규칙이 필요한데, 이는 **문턱을 새로 만드는 일**이라 P1상 본 세션이 정할 수 없다. 방향 결재: (가) 보행면 판정 규칙을 실측 분포로 제안받아 결재 (나) `sceneD4` 는 경로 (a) 불가로 인정하고 (b)만 쓴다 (다) `sceneD4` 를 모집단에서 제외 | 승용 |
| **❓G0-7** | `dataset/_archive/_delete_candidates/`(19라운드·87프레임)를 모집단에서 **자동 제외**해도 되는가? [클로드 제안: 예 — `dataset/README.md` 가 "지워도 되는 폴더"로 명시] | 승용 |

---

## 부록 A. 실측 명령

```bash
cd /home/vislab/Desktop/work_sy/Practice_NegObs

# (1) dataset 전수 순회 -> 라운드×split×씬 별 png/depth/idseg/heightmap/variation 개수
python3 <scratchpad>/p0/census_walk.py <scratchpad>/p0/census_raw.json
#  -> rows: 779 / rounds: 196 / scenes seen: 44 / total png: 13515

# (2) 씬 파일의 '마지막 코드 변경' 커밋 (독스트링 제거 AST 비교)
python3 <scratchpad>/p0/lastcode.py <scratchpad>/p0/lastcode.json
#  예: scenes/main/scene02_underpass.py commits=12 last_code=50de4892 2026-08-24T05:44:27+09:00

# (3) ROUND_LEDGER 의 실측 렌더 개시/종료와 조인 -> census.csv
python3 <scratchpad>/p0/build_census.py experiments/e1_0827/reports/census.csv
#  -> rows: 779

# (4) 높이장 기복(z_max - z_min) 전수
#     (752개 씬-디렉터리에서 heightmap.npy 를 열어 유한값의 min/max)
#  -> 기복 < 0.30 m 인 씬-디렉터리 135개, 그중 위험-ON 은 23개(340프레임)

# (5) 쌍둥이 포즈 동일성
python3 -c "..."   # variation.json 의 cuts[].cam.eye 비교
#  -> 260819_main_on/train/scene03 vs _off: 파일명·eye 24/24 동일
#  -> 260824_v3w3_extbase_A/test/sceneH1 vs _C: 24/24 동일

# (6) seg 사이드카 실물
python3 -c "import numpy as np; z=np.load('<..>/L0__s20260819__0000.idseg.npz', allow_pickle=True); print(list(z.keys()))"
#  -> ['idseg', 'idToLabels', 'annotator']   idseg=(1080,1920) uint16

# (7) 백필 사이드카
find dataset -name idseg_backfill.json | wc -l     # -> 30
```

라운드 경로는 한 번도 손으로 적지 않았다 — 전부 `variation_kit.round_dir("<라운드이름>")` 로 풀었다.

## 부록 B. `census.csv` 열 설명

`scene, module, group, round, render_start, render_end, prefix_mismatch, arm, arm_source, hazard, arm_config, split, frames_png, depth, seg, heightmap, hm_meta, variation, scene_last_code, scene_last_code_time, consistency, route_ab_usable, seg_complete`

- `render_start`/`render_end` = `ROUND_LEDGER.md` 의 **실측** 렌더 시각(라운드명 접두 날짜가 아님). `prefix_mismatch=Y` 는 그 원장이 ⚠ 로 표시한 라운드.
- `hazard` = `arm_config` 에서 `hazard_*` 키가 하나라도 True 면 `ON`, 전부 False 면 `OFF`, 판독 불가면 `?`.
- `consistency` ∈ {정합, 정합 불일치, 미상}. `미상` 은 `ROUND_LEDGER` 에 렌더 시각이 없는 라운드(`260824_handson`·`260827_handson`).
- `route_ab_usable` = (png>0) ∧ (depth 개수 == png 개수) ∧ (heightmap.npy 존재). **heightmap의 내용이 쓸모 있는지는 검사하지 않는다** — §4.2 참조.
- `seg_complete` = (seg 개수 == png 개수).
