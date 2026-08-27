# P0_CODE_SKELETON — 새 라벨링 파이프라인 골격 보고

- 작성 2026-08-28 · 근거: `Docs/briefs/edge_relabel_brief_v6.md` Phase 0 항목 4 (신규 라벨링 코드 골격)
- 위치: `experiments/e1_0827/code/` · 상수 대장 `experiments/e1_0827/CONST_LEDGER.md` · 자답 `reports/P0_SELFCHECK.md`
- 실행 환경: 시스템 `python3.10.12` + `PYTHONNOUSERSITE=1` (numpy 1.21.5 · scipy 1.8.0 · Pillow 9.0.1).
  **GPU·Isaac 불필요** — 이 골격은 전부 CPU 후처리다.

---

## 0. 승용 요약 (5문장)

1. §5 스키마를 그대로 뱉는 라벨링 골격을 새로 짰다(14개 모듈, 2,422줄). **구 `labeler.py`·폴라그리드·구 티어 로직은 한 줄도 import 하지 않는다** — 파일 형식을 배우려고 읽기만 했다.
2. 카메라 모델이 맞다는 것을 **수치로 증명**했다: 렌더 depth 를 3D로 되돌려 씬 높이장과 비교했을 때 근거리(6 m 이내) 오차 중앙값이 **0.000062 m(scene01) · 0.000176 m(scene03)** — 0.1 mm 미만이다.
3. 스모크 3프레임을 실제로 돌렸고, 같은 입력 재실행 시 정본 json 이 **바이트 동일**(프로세스를 따로 띄워도 sha256 `ead9497e…` 동일)이며 **대장 미기재 상수 0건**(44개 전수 등재)이다.
4. 그런데 **골격이 아직 못 하는 것이 있고, 그걸 좋게 보이게 만들지 않았다**: scene02(지하도)는 높이장이 구덩이를 덮어 버려서 route (a) 가 낙차를 못 보고 `NEG` 로 나온다 — RGB 에는 구덩이가 명백한데도. 있는 그대로 인쇄했다(❓B-1).
5. 작업 중 **내 코드의 결함 1건을 스스로 잡아 고쳤고**(도달 앵커가 격자 가장자리 조각에 앉는 문제, §4-1), 고친 뒤에도 scene02 결론이 그대로임을 확인했다. 결재가 필요한 갈림길 9개를 §6 에 ❓B-1 ~ ❓B-9 로 모았다. **아무것도 채택하지 않았다.**

---

## 1. 모듈 지도

| 모듈 | 줄 | 하는 일 | 상태 |
|---|---:|---|---|
| `e1_const.py` | 341 | **상수 정본.** 44개 상수 각각의 값·태그·근거·민감도 대안. `fingerprint()` 가 상수 세트의 sha16 을 만들어 모든 매니페스트에 찍힌다 | 완성 |
| `e1_schema.py` | 253 | §5 레코드 dataclass · `derive_tier_now` (§5 문면 그대로, 이 규칙이 코드에 적힌 유일한 곳) · 정본 JSON 덤프(키 정렬·고정 4자리) · csv 미러(1 edge 1행) · 검증기 | 완성 |
| `e1_camera.py` | 234 | `variation.json` 에서 카메라 복원(투영·역투영), `HeightMap` 로더, **검증 함수 `verify()`** | 완성·검증됨 |
| `e1_data.py` | 96 | 라운드/씬/프레임 찾기(`variation_kit.round_dir` 경유 — 경로 직접 표기 금지), depth·idseg 로더 | 완성 |
| `e1_geometry.py` | 392 | **route (a)**: 보행면 → 도달 가능 영역 → 낙차 → 국소 턱 → 인스턴스 → 폴리라인, 그리고 '속' 마스크 | 동작·일부 결재대기 |
| `e1_visibility.py` | 144 | 가시성 판정 + 가림 분류(`PrimClassifier`). 자기가림 vs 외부 프림 | 동작·분류표 **비어 있음(의도)** |
| `e1_depth_edges.py` | 123 | **route (b)**: depth 불연속 → Zhang-Suen 세선화 → 성분. 전 프레임 공통 단일 파라미터 세트 | 완성 |
| `e1_compare.py` | 41 | 인스턴스별 (a)–(b) 이탈 px {mean, median, p90} (거리변환 기반) | 완성 |
| `e1_label_frame.py` | 149 | 프레임 1장 → 레코드 1개 (위 전부를 순서대로 엮는 곳) | 완성 |
| `e1_overlay.py` | 83 | 검수용 오버레이 PNG (폴리라인 · 속 마스크 윤곽 · H_cand/미해결 표시 · 수치 주석) | 동작·조판 개선 여지 |
| `e1_run.py` | 177 | CLI. `--frame`/`--list` · `--camera-check` · `--prim-census` | 완성 |
| `e1_selftest.py` | 192 | `--scan-consts` · `--schema` · `--ledger` · `--determinism` | 완성 |
| `e1_hm_screen.py` | 74 | 높이장만 보는 보고 전용 선별(프레임·카메라 무관) — ❓B-1 의 근거표 | 완성 |
| `e1_sensitivity.py` | 124 | 상수 대안값으로 같은 프레임을 다시 돌려 수치 변화를 인쇄(P1 민감도의 실행 형태) | 완성 |
| `prim_class_rules.json` | — | 가림 prim 분류표. **`rules: []` 로 비어 있다(의도)** | 결재대기 |
| `smoke_frames.txt` | — | 스모크 3프레임 목록 + 왜 이 3장인지 | — |

> `code/p0_edge_distance.py` 는 같은 Phase 0 의 **센서스/파일럿 후보 담당분**이 쓴 보고 전용 프로브다(내 산출물 아님).
> 이 골격의 `e1_const.py` 를 상수 원천으로 import 한다 — 두 트랙이 같은 대장을 쓴다는 뜻이다.
> 그쪽이 `reports/P0_CONST_ADDENDUM.md` 로 요청한 `EDGE_WINDOW_SHAPE` 를 **대장에 등재하고 이 파이프라인에도 구현**했다
> (현행 `disc`, 그쪽 프로브는 `chebyshev`). 두 도구의 거리 수치가 왜 직접 비교 불가인지가 그 항목에 적혀 있다.

### 실행 순서 (한 프레임)

```
variation.json ──► e1_camera.CameraModel ──┐
heightmap.npy  ──► e1_camera.HeightMap  ───┤
                                           ├─► e1_geometry.route_a
*.depth.npy    ────────────────────────────┤     1 walkable → 2 reachable → 3 drop → 4 break
*.idseg.npz    ──► e1_visibility ──────────┘     5 instances → 투영 → 가시 구간 → 속 마스크
                                                 └─ 인스턴스별 occluder 판정
*.depth.npy    ──► e1_depth_edges.extract ──► e1_compare.deviation ──► src_disagree_px
                                                 ▼
                                    e1_schema.FrameRecord + derive_tier_now
                                                 ▼
                        edge_manifest_v1.json (바이트 결정론) + .csv + 속 마스크 PNG + 오버레이
```

---

## 2. 검증된 것 — 카메라 증명

브리프가 요구한 증명은 "높이장 표면과 비교해 |dz| 를 인쇄"다. 세 가지를 각각 쟀다.

| 검사 | 무엇을 증명하나 | scene01 | scene02 | scene03 |
|---|---|---|---|---|
| 내부 파라미터 정합 | 저장된 `hfov` 와 `focal`·`aperture` 가 같은 카메라인가 | 4.5e-06 deg | 4.5e-06 deg | 1.2e-05 deg |
| A. 높이장 색인 | `x0/y0/step/z[y,x]` 해석이 맞는가 (`hm(eye)` vs 렌더러가 적은 `cam.ground_z`) | 6.0e-09 m | 0 m | 1.5e-03 m |
| B. 투영 대수 | `project(unproject(depth))` 픽셀 왕복 오차 | median **1.3e-13 px** (n=112,393) | 5.7e-14 px (n=129,600) | 5.7e-14 px (n=121,610) |
| C. 카메라↔월드 | 역투영 3D 점의 z 와 높이장 표면의 \|dz\| — **이게 본 증명** | r6m median **0.000062** / p90 0.000122 m | 표본 0 (아래) | r6m median **0.000176** / p90 0.206059 m |

읽는 법:
- **B 가 1e-13 px** 라는 것은 투영/역투영이 서로의 정확한 역이라는 뜻이고, **C 가 0.1 mm 미만**이라는 것은
  그 좌표계가 씬의 월드 좌표계와 같다는 뜻이다. 기저(right/up/forward)나 depth 규약(z-depth vs 광선 길이)이
  틀렸다면 C 는 거리에 따라 커지는 계통 오차로 나타난다 — 나타나지 않았다.
- **A 가 clamped=True** 인 이유: 이 코퍼스의 카메라는 높이장 격자 **밖**에 서 있는 일이 흔하다
  (scene01 컷0 eye x = −3.269, 격자 x_range = [−2.0, 14.0]). 격자는 씬을 덮지 진입로를 덮지 않는다.
  그래서 격자 안쪽으로 잘라서 표본하고, 잘랐다는 사실을 레코드에 같이 적는다.
- **scene02 의 C 는 median 0.805 m** 이고 r3/r6 표본이 0이다. 이건 카메라 오차가 아니라
  (i) 카메라가 격자에서 6 m 넘게 떨어져 있고 (ii) **그 씬 높이장이 AABB 포락면이라 실제 표면과 다르다**는 뜻이다.
  숫자를 고치지 않고 그대로 실었다.

재현: `PYTHONNOUSERSITE=1 python3 code/e1_run.py --list code/smoke_frames.txt --out annotations/_smoke --camera-check`
(로그: `logs/p0_smoke.log`)

---

## 3. 스모크 결과 — 3프레임, 있는 그대로

프레임 선택 이유(`code/smoke_frames.txt` 에도 적어 둠): **depth + heightmap + idseg 사이드카가 모두 있고 계단형 낙차가 있는 씬**.
지시받은 후보 중 scene18 은 이 라운드에 **idseg 사이드카가 0개**라 가림 판정을 아예 못 하고, scene02 는 아래 이유로 route (a) 가 못 본다.
그래서 scene01(캠퍼스 계단) + scene03(제방) 을 넣고, **scene02 는 "안 되는 것을 보여주려고" 일부러 남겼다.**

| 프레임 | tier_now | edges | 인스턴스별 실측 |
|---|---|---:|---|
| `scene01/L0__0000` | VE_raw | 5 | e00 dist 3.29/3.45 m · 속 0 px · **(a)–(b) 0.90/1.00/1.00 px** · occl False<br>e01 dist 4.07/4.24 m · 속 13,339 px (h102 w532) · occl **null** (`/World/Scene01/UpperPlaza`)<br>e02 dist 4.91/4.91 m · 속 12,821 px (h80 w747) · occl **null** (동일)<br>e03 dist —/— · 속 85,985 px (h214 w998) · occl False<br>e04 dist —/— · 속 45,151 px (h168 w1052) · occl False |
| `scene02/L0__0000` | **NEG** | 0 | route (a) 보행 가능 102,651 / 도달 83,896 / 낙차≥0.3 인 셀 10,168 / **턱 셀 0** → 인스턴스 0 |
| `scene03/L0__0000` | VE_raw | 5 | e00 dist 5.12/5.14 m · 속 0 px · **(a)–(b) 0.86/1.00/1.00 px** · occl False<br>e01 dist 8.67/9.80 m · 속 173,552 px · occl **null** (`/World/Scene03/Bollard_1`)<br>e02 dist 11.82/11.94 m · 속 7,879 px (h243 w68) · occl False<br>e03 dist 11.80/11.92 m · 속 7,977 px (h242 w63) · occl False<br>e04 dist 8.63/9.28 m · 속 158,712 px · occl **null** (`/World/Scene03/Bollard_0`) |

route (b) 쪽 수치: scene01 점프 66,466 px → 세선화 26,217 px(7회 반복) → 성분 42 · scene02 51,476 → 21,853(8회) → 54 ·
scene03 86,055 → 38,217(9회) → 50.

결정론: 같은 3프레임을 **프로세스를 따로 띄워** 같은 인자로 두 번 돌린 `edge_manifest_v1.json` 이 sha256
`ead9497e2b613b0fc8c51a8a1b9c85269abab1259277b2c6116a2d1e22ddeeef` 로 동일했다(csv 는 `914d9f93…`).
프레임별 자체 검사도 3장 모두 `byte-identical=True`.

셀프테스트 3종:
```
[selftest] unledgered numeric literals: 0
[selftest] schema failures: 0
[selftest] ledger: 44 constants, missing from CONST_LEDGER.md: 0, named there but absent from code: 0
```

**여기서 좋게 보이려고 손댄 파라미터는 없다.** 위 수치는 상수 지문 `e1bc1c63af9ffe98` 하나로 나온 결과다.

---

## 4. 이 골격이 지금 못 하는 것 (정직 표기)

### 4-1. 높이장이 AABB 포락면이다 — route (a) 의 뿌리 문제, 그리고 내가 잡은 결함 1건

`heightmap.npy` 의 출처는 `variation_kit.AabbPrefilter.ground_z(top=60.0)`, 즉 **월드 AABB 집합에 위에서 광선을 쏴서 처음 맞는 높이**다.
박스 위주 씬에서는 기하와 정확히 일치하지만(`heightmap_meta.aabb_grid.worst_abs = 0.0`), 두 가지가 따라온다.

**(가) 난간·파라펫·옥상이 '표면'으로 들어온다.**
scene01/scene02 의 `z_max` 는 6.0 m(건물 지붕)이라, 아무 필터 없이 규칙 1을 적용하면 지붕 모서리가 6 m 낙차의 edge 인스턴스가 된다.
그래서 **보행 가능성 검사**(발자국 평탄도 + 지지 비율)와 **도달 가능성 flood fill**(단차 ≤ `MAX_TRAVERSE_STEP_M`)을 넣었다.
이 두 장치는 **전부 `[임시-결재대기]` 상수** 위에 서 있다(❓B-3, ❓B-7, ❓B-9).

**(나) 바닥 개구부가 메워진다.**
높이장만 놓고(카메라 무관, 프레임 0장) "보행 가능 ∧ 낙차 ≥ 0.3 m ∧ 국소 턱" 셀을 세는 선별을 33씬 전수로 돌려 봤다
(`python3 code/e1_hm_screen.py --round 260819_main_on`, 로그 `logs/p0_hm_screen.log`):

| 결과 | 씬 |
|---|---|
| 턱 셀 **0** | `sceneD4`(z 일정) · `sceneN2` · `sceneN5` — 원래 낙차 없는 음성 씬 3개 |
| 턱 셀 1개 이상 | 나머지 30씬 (예: scene01 2,046 · scene02 **670** · scene03 1,143 · scene09 8,876) |

즉 scene02 도 높이장에는 턱 셀이 670개 **있다** — 그런데 그 중 **지면에서 도달할 수 있는 것은 0개**다(도달 집합 83,896셀과의 교집합 0, 실측). 위치상 건물·화단 쪽으로 보이지만 그건 관찰이지 실측이 아니다.
카메라 앵커까지 붙여 실제로 돌리면 **보행 가능 102,651 / 도달 83,896 / 낙차≥0.3 셀 10,168 / 턱 셀 0** 이다.
지하도의 20단 3.2 m 계단은 높이장 `z_min = −0.0136 m` 이 말해 주듯 **아예 없다**(사각형 AABB 가 개구부를 덮었다).
`R_RUN_M` 을 0.5/1.0/2.0 으로 바꿔도 0이다 — 상수 문제가 아니다. → ❓B-1.

**(다) 작업 중 잡은 내 코드의 결함 — 도달 앵커.**
처음 규칙은 "카메라 셀을 격자 안으로 잘라서 그 근처 보행 셀에서 flood fill 시작"이었다.
그런데 이 코퍼스의 카메라는 격자 **밖**에 서는 일이 흔하고(scene02 컷0 eye x = −8.62, x_range [−2.0, 14.0]),
잘라 붙인 앵커가 격자 왼쪽 끝의 **29셀짜리 지면 조각**에 떨어졌다 — 바로 옆이 2.84 m 벽이라 더 못 나간다.
지면 셀이 83,925개인 씬에서 도달 셀 29개, 즉 route (a) 가 **씬의 99.97%를 못 본 채** 0을 보고하고 있었다.
숨기지 않고 상수 `REACH_ANCHOR_MODE` 로 규칙 두 개를 나란히 두고 둘 다 쟀다:

| 앵커 규칙 | scene01 도달셀 | scene02 도달셀 / 턱셀 | scene03 도달셀 |
|---|---:|---|---:|
| `camera_cell_clamped` (처음) | 93,090 | **29** / 0 | 34,552 |
| `largest_ground_component` (현행) | 93,090 | **83,896** / **0** | 34,552 |

- 고친 뒤 scene01·scene03 은 **한 셀도 안 변한다** — 원래 제대로 앉던 씬이라서다.
- scene02 는 도달 지면이 정상화됐는데도 **턱 셀은 여전히 0**이다. 즉 (나)의 결론은 이 결함과 무관하게 성립한다.
  결함을 고친 다음에도 같은 결론이 나오는지 확인한 것이 이 항목의 핵심이다. → 채택은 ❓B-9.

### 4-2. 계단은 챌면마다 인스턴스가 하나씩 나온다

§2 규칙 1을 문면 그대로 읽으면 **모든 발판이 보행면**이고, 각 발판의 코(nosing)는 R_RUN 안에서 0.3 m 이상 내려가는 턱이다.
그래서 4단 계단 scene01 에서 성분 8개, 제방 scene03 에서 41개가 나온다.
합치지 않았다 — 합치는 것은 규칙을 우리가 바꾸는 일이라서다. → ❓B-2.

### 4-3. 가림 분류가 비어 있다 (의도)

`prim_class_rules.json` 이 비었으므로 **`occluder.flag` 는 스모크 전체에서 `null`** 이고, H_cand 는 아직 한 건도 안 나왔다.
막은 prim 원자료는 `annotations/_smoke/prim_blocker_census.json` 과 `unresolved_occluders.txt` 에 있다:
`/World/Scene01/UpperPlaza`(184) · `/World/Scene03/Bollard_1`(7) · `/World/Scene03/Bollard_0`(7). → ❓B-4.

또한 **이 라운드에서 idseg 사이드카가 있는 씬은 33개 중 17개뿐**이다(scene18·scene07·scene08·scene11 등은 없음).
사이드카가 없는 프레임은 `occluder = {flag: null, prim: 'no-seg-sidecar'}` 로 남고 '`seg 없음`' 목록으로 간다 — 추측하지 않는다.

### 4-4. '속' 픽셀의 주인 문제

속 픽셀은 **수평면에서 가장 가까운 인스턴스**가 가져간다(보로노이). 결합 반경을 지어내지 않아도 되는 대신,
**화면 밖 인스턴스가 속을 소유하는 일**이 생긴다 — scene01 의 e03/e04 가 화면 안 edge 점 0개인데 85,985 px·45,151 px 를 갖고 있다.
`INT_ASSIGN_INFRAME_ONLY = True` 로 바꾸면 scene01 의 속 총량이 157,296 → 65,823 px 로 줄고 인스턴스도 5 → 3 이 된다. → ❓B-5.

또 하나: 속의 정의가 "edge 너머, 보행면보다 0.3 m 이상 낮은 **보이는** 면"이므로,
계단 아래 광장이나 강 수면이 **통째로** 속으로 잡힌다(scene03 e01 = 173,552 px). 정의대로다.

### 4-5. 스텁(아직 대충인 곳)

| 항목 | 지금 | 무엇이 부족한가 |
|---|---|---|
| 폴리라인 정렬 | 주성분 축 끝점에서 시작하는 greedy 최근접 순회 | 자기 교차/분기 성분에서 최적 경로 보장 안 됨. 파일럿 오버레이 육안 검수에서 드러날 것 |
| 오버레이 조판 | PIL 기본 폰트, 좌상단 텍스트 | 1920×1080 에서 글자가 작다. 검수 편의 개선 여지(G1 전 손볼 수 있음) |
| (a)–(b) 대조 방향 | (a) → 가장 가까운 (b) 픽셀, 단방향 | (b) 에만 있는 선(물체 실루엣)은 이 수치에 안 잡힌다. 성분 수 격차로 병기 중 |
| `notes` 형식 | dict `{messages, diag}` | §5 는 "특이사항"이라고만 함. 문자열로 바꿀지 구조체 유지할지 → ❓B-6b |
| 창고 도메인 | 스키마·파일명만 준비 | route (a′)(바닥 STL 단면)은 미구현. §7/G3a 이후 일이라 P3 상 지금 손대면 안 됨 |

---

## 5. P2·P3 준수 확인

- **P2**: 씬 파일·카메라 규격·위험 기하·정본 스크립트(`scripts/`, `*_kit.py`, `scene_common.py`, 구 사이클 `code/`) 를 하나도 수정하지 않았다.
  신규 코드는 전부 `experiments/e1_0827/code/` 에만 있다.
  `labeler.py`/폴라그리드/구 티어 로직은 **import 하지 않는다** — `grep -n "import" code/e1_*.py` 의 외부 의존은
  `variation_kit`(라운드 경로 색인) 하나뿐이고, 그것도 `e1_data.py` 안에서 `round_dir()` 만 쓴다.
- **P3**: 전량 라벨링·파일럿 라벨링·학습·재렌더 **없음**. 스모크는 **3프레임**(허용 상한)이고 산출은 `_smoke` 폴더에 격리했다.
- **P1**: `--scan-consts` 0건 · `--ledger` 0건 · 채택 0건.

---

## 6. 결재란 (❓)

| 번호 | 항목 | 지금 상태 / 실측 근거 | 담당 |
|---|---|---|---|
| ❓B-1 | 높이장(AABB 포락면)이 개구부를 덮어 route (a) 가 낙차를 못 보는 씬(scene02·scene13 등)의 처분 — 높이장 재생성 / (b) 단독 / 모집단 제외 중 무엇인가 | scene02 = NEG 0 인스턴스 (`z_min` −0.0136 m). R_RUN 3값 전부 0 | 승용 |
| ❓B-2 | 계단 **챌면마다 인스턴스 1개**를 유지할지, 맨 위 턱 하나로 묶을지 | scene01 성분 8 · scene03 성분 41 | 승용 |
| ❓B-3 | `MAX_TRAVERSE_STEP_M` 채택값 | 0.15→0.20 에서 scene01 도달 셀 17,224 → 93,090 (5.4배). 가장 민감 | 승용 |
| ❓B-4 | 가림 prim 분류표 — `/World/Scene01/UpperPlaza`(184) / `/World/Scene03/Bollard_{0,1}`(각 7) 을 `self`/`external` 로 확정 | 규칙 0개, 전부 `unknown`, H_cand 0건 | 승용 |
| ❓B-5 | 화면 밖 인스턴스가 '속' 픽셀을 소유해도 되는가 (`INT_ASSIGN_INFRAME_ONLY`) | False→True 시 scene01 속 157,296 → 65,823 px, edges 5 → 3 | 승용 |
| ❓B-6 | `VIS_TOL_M`·`B_REL_JUMP`·`B_ABS_JUMP_M` 채택값 — 스모크 3장에서는 셋 다 둔감했다(고원). G1 파일럿 분포로 정할지 | VIS_TOL 0.01~0.35 구간 결과 동일(1e-06 에서만 붕괴) | 승용 |
| ❓B-6b | `notes` 를 문자열이 아니라 dict `{messages, diag}` 로 둔 것 승인 여부 (진단 수치가 레코드에 남는다) | 현행 dict | 승용 |
| ❓B-7 | 아직 단독 스윕 안 돌린 임시 상수 4개(`WALK_FOOT_R_M`·`WALK_FLAT_TOL_M`·`MIN_INSTANCE_LEN_M`·`B_MIN_COMP_PX`) 를 파일럿에서 스윕할지 | 임시값 유지 | 승용 |
| ❓B-8 | 프레임 안이지만 **전부 가려진** 인스턴스(scene01 1건 · scene03 36건)를 NEG 로 둘지 H_cand 후보로 올릴지 | 현행 NEG 계산에 포함, 원자료는 `notes.diag.blocked_only_instances` 에 보존 | 승용 |
| ❓B-9 | 도달 앵커 규칙 `REACH_ANCHOR_MODE` 를 `largest_ground_component` 로 확정할지 | 처음 규칙에서 scene02 도달 셀 29(결함) → 고친 뒤 83,896. 다른 두 씬은 무변화 | 승용 |

---

## 7. 재현 명령

```bash
cd experiments/e1_0827
export PYTHONNOUSERSITE=1

# 셀프테스트 3종 (상수 0건 · 스키마 0건 · 대장 0건)
python3 code/e1_selftest.py --scan-consts --schema --ledger

# 스모크 3프레임 (레코드 + 오버레이 + 카메라 증명 + 가림 prim 센서스)
python3 code/e1_run.py --list code/smoke_frames.txt \
    --out annotations/_smoke --overlays overlays/_smoke --camera-check --prim-census

# 결정론 (같은 프레임 두 번 → 바이트 동일)
python3 code/e1_selftest.py --determinism --frame 260819_main_on:scene01:L0__s20260819__0000.png

# 민감도
python3 code/e1_sensitivity.py --key R_RUN_M --list code/smoke_frames.txt
python3 code/e1_sensitivity.py --key INT_ASSIGN_INFRAME_ONLY --list code/smoke_frames.txt --full
```

산출물: `annotations/_smoke/edge_manifest_v1.{json,csv}` · `annotations/_smoke/masks/*.png` ·
`annotations/_smoke/{prim_blocker_census.json, unresolved_occluders.txt}` ·
`overlays/_smoke/*.overlay.png` · `logs/p0_smoke.log`
