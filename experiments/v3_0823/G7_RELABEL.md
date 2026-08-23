# G7_RELABEL — boost 라운드 미융합 결함 수리 + 티어 재분류 원장

**작업**: v3 창 P-2. 결함 G7(= `260820_boost_*` 라운드가 `fuse_heightmap.py`를 건너뜀) 수리 →
재융합 → 재라벨 → 교정 GT 매니페스트.
**날짜**: 2026-08-23 · **CPU 전용**(융합·라벨링 전부 numpy, GPU 0) · `PYTHONNOUSERSITE=1`
**원본 무수정 원칙**: 기존 라벨·매니페스트 파일은 **읽기만** 했다. 산출물은 전부 신규 경로다.
git 명령은 실행하지 않았다.

---

## 0. 매핑 규칙 (교정 GT 매니페스트가 어떤 프레임을 어디로 가리키는가)

> **한 문장**: `(boost 밴드, 씬)`이 **미융합 5쌍** — `boost_e × {scene07, scene08, scene12}`,
> `boost_e2 × {scene07, scene12}` — 중 하나인 프레임만 **교정 라벨**을 가리키고,
> 코퍼스의 나머지 프레임은 **동결된 08-20 라벨을 바이트 그대로** 유지한다.

| 항목 | 값 |
|---|---|
| 베이스(무수정) | `experiments/dayrun_0820/dataset_manifest_v2_full.json` (2,832프레임) |
| 교정 대상 | 240프레임 (on 120 · off 120) = 전체의 8.5 % |
| 교체 필드 | `polar_gt` · `polar_gt_pregate` · `gate_excluded` · `raw_vis` · `tier` |
| 보존 필드 | `rgb` · `depth` · `round` · `cam` · `cond` — **픽셀은 한 장도 안 바뀌었다** (동결 렌더 경로 그대로) |
| 신규 프레임 필드 | `label_source` = `original` / `g7fix-B` / `g7fix-A`, 교정 프레임엔 `tier_before` · `g7_note` 추가 |
| 게이트 메타 | 파이프라인이 원래 내보내는 그대로 (`gate_excluded`, `polar_gt_pregate`, `footprint.hm_cells_excluded`) |
| off 팔 | 교정 대상에 포함되나 내용 불변 (off 팔 footprint는 정의상 0, tier `off`) |

교정본은 **두 벌**이다(§3.3 참조). 정본은 B다.

| 변형 | 참조 높이맵 | 매니페스트 | 라벨 |
|---|---|---|---|
| **B (정본)** | `260819_main_*`의 융합 높이맵 (씬 지오메트리 동일 · 커버리지 최대) | `experiments/v3_0823/dataset_manifest_v2corr.json` | `annotations/labels_v1_full_g7fix.json` |
| A (민감도) | boost 라운드 **자기 depth**로 새로 융합 | `experiments/v3_0823/dataset_manifest_v2corr_roundown.json` | `annotations/labels_v1_full_g7fix_roundown.json` |

---

## 1. 결함 확정

### 1.1 본 라운드가 융합을 부른 방식 (재현 대상)

`experiments/mainrun_0819/code/labeling/README_LABELING.md` 1b단계:

```
$PY fuse_heightmap.py --on-round $D/260819_main_on --off-round $D/260819_main_off \
      --scenes scene02,scene07,scene08,scene12,scene16 --workers 6
$PY labeler.py --on-round ... --off-round ... --grid gridspec_v1.json --out ...
```

`fuse_heightmap.py`는 `heightmap_fused.npy`를 **씬 디렉터리 안에** 쓰고,
`labeler.load_heightmap`(labeler.py:199)이 그 파일이 있으면 AABB 높이맵보다 **우선** 읽는다.
즉 **사이드카의 존재 자체가 스위치**다. 팔별 채택 규칙(`fuse_heightmap.py` 도크스트링):

| 씬 | 본 라운드 채택 | 이유 |
|---|---|---|
| scene02 / scene07 / scene12 / scene16 | `fused / fused` | AABB가 지붕·데크·수면 위를 읽음 |
| scene08 | `aabb ON / fused OFF` | ON은 건전, OFF만 제거된 지형을 계속 들고 있음 |

디스크 실측 — 본 라운드에는 사이드카가 있고 boost에는 **하나도 없다**:

| 라운드 | `heightmap.npy` | `heightmap_fused.npy` | `.depth.npy` |
|---|---|---|---|
| `260819_main_on` | 33 | **4** (s02·s07·s12·s16) | 792 |
| `260819_main_off` | 33 | **5** (s02·s07·s08·s12·s16) | 791 |
| `260820_boost_h_on/off` | 4 / 4 | **0 / 0** | 96 / 96 |
| `260820_boost_e_on/off` | 14 / 14 | **0 / 0** | 336 / 336 |
| `260820_boost_e2_on/off` | 8 / 8 | **0 / 0** | 192 / 192 |

라벨 파일이 이를 자백한다 — `experiments/dayrun_0820/annotations/labels_boost_{h,e,e2}.json`의
`scene_footprint[].hm_source`가 **44개 씬-팔 전부 `aabb`**다. 융합 출력이 놓였어야 할 자리는
`dataset/260820_boost_<band>_<arm>/<split>/<scene>/heightmap_fused.npy`이고, **부재**다(stale이 아니라 미생성).

### 1.2 결함 범위 — 26개 (밴드, 씬) 쌍 전수 스캔

AABB 높이맵은 카메라 독립(`variation_kit.AabbPrefilter.ground_z`)이라 본 라운드와 boost 라운드에서
**바이트 동일**함을 먼저 확인했다(`logs/pairing_audit.log`, `aabb==main:True` 5/5).
따라서 본 라운드의 융합 판단이 boost에 그대로 이월된다. 그 위에서 전 boost 쌍을 스캔했다
(`code/g7_scan_all_boost.py` → `logs/scan_all_boost.log`). 판정식:
`fused 대안이 500셀 이상인데 실제 사용 instrument가 그 10 % 미만이면 결함`.

| 밴드 | 씬 | 분할 | aabb/aabb (실사용) | fused/fused | aabbON/fusedOFF | 판정 |
|---|---|---|---|---|---|---|
| e | **scene07** | test | **0** | 19,274 | 71,910 | **G7 결함** |
| e | **scene08** | val | **0** | 458 | 64,461 | **G7 결함** |
| e | **scene12** | train | **50** | 24,920 | 55,385 | **G7 결함** |
| e2 | **scene07** | test | **0** | 12,950 | 51,139 | **G7 결함** |
| e2 | **scene12** | train | **50** | 1,172 | 38,772 | **G7 결함** |
| h | s09·s14·s15·s17 | — | 87,954 / 54,213 / 2,750 / 65,833 | 1 / 0 / 281 / 0 | — | ok |
| e | 나머지 11씬 | — | 2,750–88,179 | 0–32,450 | — | ok |
| e2 | 나머지 6씬 | — | 220–88,179 | 0–9,140 | — | ok |

**결함 = 정확히 5쌍 · 3개 씬 · 라운드 2개**(`boost_e`, `boost_e2`).
`boost_h`는 **영향 없음**(4씬 모두 AABB가 옳은 씬) → `labels_boost_h.json`은 무수정 이월.
카메라 범위는 해당 씬-팔의 **전 컷 24개**(8캠 × 3조건)다 — 부분 손상이 아니다.

> **문서와의 차이 1건(정직 기록)**: `DECISIONS.md` D42는 "오라클 **6씬**"이라 적었으나,
> 실측 결함 씬은 **3개**(s07·s08·s12), (밴드, 씬) 쌍으로는 **5개**다. D42가 인용한 개별 수치
> (s07 test 0셀 · s08 val 0셀 · s12 50셀)는 위 표와 **정확히 일치**한다 — 씬 수 표기만 어긋난다.

### 1.3 결함의 메커니즘 (재확인)

`scene12`: AABB 레이가 강물을 **통과해 바닥(−2.40 m)**을 읽고 카메라는 **수면(−1.80 m)**을 본다 →
0.6 m 기기 오프셋. 양팔 모두 AABB면 트윈 차분이 상쇄되어 **50셀 = 5 cm × 2.45 m 조각**만 남는다
(계단 라이저 1개의 양자화 잔여, `max_diff` 0.3394 m). 그 조각 위에는 픽셀이 떨어질 자리가 없으므로
`int_px = 0` → `tier_of`가 **strict-H**를 준다. **H가 은닉의 증거가 아니라 GT 부재의 증거였다.**

---

## 2. 재융합 — 무엇을, 어디에

### 2.1 출력 규약 (신규 경로, 동결본 무접촉)

`fuse_heightmap.py`는 사이드카를 씬 디렉터리 안에 쓰고 `labeler`도 거기서 읽으므로,
동결 코퍼스를 건드리지 않으려면 **평행 트리**가 필요하다. 규약:

```
dataset/260820_boost_<band>_<arm>_g7fix/<split>/<scene>/    # 변형 A (라운드 자기 융합)
dataset/260820_boost_<band>_<arm>_g7fixM/<split>/<scene>/   # 변형 B (본 라운드 융합 참조)
```

* 원본 씬 디렉터리의 **모든 항목**(png · `.depth.npy` · `variation.json` · `heightmap.npy` ·
  `heightmap_meta.json` · `.negobs_env.json`)이 **심링크**다 → 변형 A 트리 2,292개 +
  변형 B 트리 538개 = 심링크 2,830개, 실데이터 복제 0바이트.
* **실파일은 융합 사이드카 18개뿐**(변형 A의 `.npy` 9 + `_meta.json` 9).
  변형 B는 본 라운드 사이드카를 심링크한다.
* `dataset/`는 `.gitignore:85`로 통째 무시되므로 리포에 들어가지 않는다.
* 생성기: `experiments/v3_0823/code/g7_make_shadow.py` · `code/g7_variantB.py`.

동결 트리 재확인: `find dataset/260820_boost_*_{on,off} -name 'heightmap_fused*' | wc -l` → **0**.

### 2.2 변형 A — boost 라운드 자기 depth로 융합

```
PYTHONNOUSERSITE=1 $PY fuse_heightmap.py \
  --on-round  dataset/260820_boost_e_on_g7fix  --off-round dataset/260820_boost_e_off_g7fix \
  --scenes scene07,scene08,scene12 --grid gridspec_v1.json --workers 6
# e2: --scenes scene07,scene12
```
로그: `logs/fuse_boost_e.log` · `logs/fuse_boost_e2.log` (+ `.json` 요약)

| 사이드카 | views | finite/103,041 | 커버리지 | z 범위 | 초 | 결측 depth |
|---|---|---|---|---|---|---|
| `boost_e_on/scene07` | 24 | 36,737 | 0.357 | [−6.004, 4.500] | 1.72 | 0 |
| `boost_e_off/scene07` | 24 | 85,294 | 0.828 | [−0.001, 0.001] | 2.36 | 0 |
| `boost_e_off/scene08` | 24 | 82,725 | 0.803 | [−0.001, 0.450] | 2.15 | 0 |
| `boost_e_on/scene12` | 24 | 69,158 | 0.671 | [−1.802, 1.133] | 2.16 | 0 |
| `boost_e_off/scene12` | 24 | 88,188 | 0.856 | [−1.802, 0.001] | 2.34 | 0 |
| `boost_e2_on/scene07` | 24 | 30,874 | 0.300 | [−6.004, 4.500] | 1.29 | 0 |
| `boost_e2_off/scene07` | 24 | 60,942 | 0.591 | [−0.000, 0.000] | 1.39 | 0 |
| `boost_e2_on/scene12` | 24 | 28,526 | **0.277** | [−1.801, 0.524] | 1.20 | 0 |
| `boost_e2_off/scene12` | 24 | 58,229 | 0.565 | [−1.801, 0.000] | 1.40 | 0 |

**결측 융합 입력 0건** — 전수 스캔(§1.2)에서도 26쌍 × 2팔 전부 `missing_depth = 0`.
**재렌더 필요 없음.**

### 2.3 팔별 채택 감사 (README_LABELING "혼합 페어링은 자체 감사 필요")

`code/g7_pairing_audit.py` → `logs/pairing_audit.log`. 규칙 (a) 두 기기가 함께 채운 셀에서
`median |fused − aabb|`:

| 밴드 | 씬 | med on | med off | 본 라운드 med (도크스트링) | 채택 |
|---|---|---|---|---|---|
| e | scene07 | 0.0027 | **1.8198** | on 0.004 / off 1.967 | `fused / fused` |
| e | scene08 | 0.0061 | **2.2500** | on 0.002 / off 2.400 | `aabb ON / fused OFF` |
| e | scene12 | 0.0010 | **0.6000** | on 0.001 / off 0.600 | `fused / fused` |
| e2 | scene07 | 0.0041 | **1.7997** | 〃 | `fused / fused` |
| e2 | scene12 | 0.1496 | **0.5999** | 〃 | `fused / fused` |

on 팔은 0.001–0.006(scene12·e2만 0.15), off 팔은 0.6–2.25 — **본 라운드와 같은 진단**이 나온다.
따라서 팔별 채택도 본 라운드와 **동일**하게 적용했다. scene08의 ON 융합 사이드카는 생성 후
**삭제**하여 `aabb ON / fused OFF`를 만들었다(본 라운드가 한 것과 같은 조치).
혼합 페어링을 다른 씬에 쓰면 안 되는 이유도 재확인된다 — scene12에 `aabbON/fusedOFF`를 쓰면
0.6 m 기기 오프셋이 **55,385셀**(fused/fused 24,920의 2.2배)의 유령 footprint가 된다.

### 2.4 변형 B — 본 라운드 융합 높이맵을 참조로

융합 높이맵은 **카메라가 아니라 씬 지오메트리의 측정치**다. AABB 바이트 동일성(§1.2)이
두 라운드가 같은 지면을 렌더했음을 증명하므로, 본 라운드 사이드카를 boost 프레임의 참조로
쓰는 것이 유효하다. boost 카메라는 밴드 편향(e = 원거리+고高, e2 = 근거리+저低)이라 자기 융합의
커버리지가 얇다 — scene12 ON이 `e2`에서 **0.277** vs 본 라운드 **0.748**. 변형 B는 코퍼스 안에서
가장 완전한 참조로 D50 질문을 묻는다. 생성: `code/g7_variantB.py`.

---

## 3. 재라벨 결과

### 3.1 실행

```
PYTHONNOUSERSITE=1 $PY labeler.py --on-round dataset/260820_boost_<band>_on_g7fix{,M} \
   --off-round dataset/260820_boost_<band>_off_g7fix{,M} \
   --grid gridspec_v1.json --workers 8 --out experiments/v3_0823/annotations/labels_boost_<band>_g7fix{,M}.json
```
그리드 · 게이트 정책은 08-20과 **동일**(`PROVISIONAL-GRID-V1`, 20칸, `train-on-gated; pregate preserved per D14`).
변형 A는 라운드 전체(672 + 384프레임), 변형 B는 결함 씬만(144 + 96프레임). 총 소요 **< 10 s**(8워커).
로그: `logs/label_boost_{e,e2}{,_M}.log`.

**대조군(회귀 검증)**: 융합 사이드카를 **추가하지 않은** 씬-팔의 프레임 **816개 전수**가
08-20 라벨과 **JSON 바이트 동일**(`code/g7_s12_detail.py` → `logs/g7_s12_detail.log`).
파이프라인이 융합 이외의 이유로 라벨을 움직이지 않았다는 증거다.

### 3.2 씬 × 팔 footprint — BEFORE → AFTER

on 팔 행만(off 팔은 정의상 0셀·tier `off`·전 변형 불변):

| 밴드 | 씬 | 분할 | hm BEFORE | hm AFTER | raw b | raw A | raw B | kept b | kept A | kept B | max_diff b | AFTER |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| e | scene07 | test | aabb/aabb | fused/fused | 0 | 19,274 | 18,874 | 0 | 7,657 | 9,931 | 0.000 | 6.004 |
| e | scene08 | val | aabb/aabb | **aabb/fused** | 0 | 64,461 | 66,547 | 0 | 60,420 | 64,968 | 0.001 | 4.507 |
| e | scene12 | train | aabb/aabb | fused/fused | **50** | 24,920 | 33,605 | 50 | 23,702 | 32,797 | 0.339 | 1.362 |
| e2 | scene07 | test | aabb/aabb | fused/fused | 0 | 12,950 | 18,874 | 0 | 4,624 | 9,931 | 0.000 | 6.004 |
| e2 | scene12 | train | aabb/aabb | fused/fused | **50** | **1,172** | 33,605 | 50 | **9** | 32,797 | 0.339 | 1.362 |

scene12 배율: `50 → 33,605`셀 = **672배**(변형 B). CUEOFF v2 배너의 `50 → 50,278 = 1006배`와
같은 현상이며, 배율 차이는 참조 라운드가 다르기 때문이다(배너는 08-23 cueoff C팔 기준).

### 3.3 씬 × 팔 티어 — BEFORE → AFTER

| 밴드 | 씬 | 분할 | BEFORE | AFTER **B (정본)** | AFTER A (민감도) |
|---|---|---|---|---|---|
| e | scene07 | test | `none_in_fov 24` | `V 18 · none_in_fov 6` | `V 18 · none_in_fov 6` |
| e | scene08 | val | `none_in_fov 24` | `V 21 · none_in_fov 3` | `V 21 · none_in_fov 3` |
| e | **scene12** | train | **`H 24`** | **`V 24`** | `V 9 · none_in_fov 15` |
| e2 | scene07 | test | `none_in_fov 24` | `V 21 · H_weak 3` | `V 21 · E 3` |
| e2 | **scene12** | train | **`H 24`** | **`V 24`** | `V 3 · H_weak 3 · none_in_fov 18` |
| h | 4씬 전부 | — | 불변 | 불변(대상 아님) | 불변 |
| — | 나머지 21쌍 | — | 불변 | 바이트 동일 | 바이트 동일 |

**프레임 단위 이동(변형 B)**: 111프레임이 티어를 바꿨다(on 120 중 111, 나머지 9는 `none_in_fov` 유지).
off 120프레임은 내용 불변.

### 3.4 코퍼스 전체 티어 인구 (2,832프레임, `split_v2_full.json`)

| 분할 | 출처 | V | E | H | H_weak | none_in_fov | off |
|---|---|---|---|---|---|---|---|
| train | BEFORE | 438 | 21 | **141** | 21 | 147 | 768 |
| train | **AFTER B** | **486** | 21 | **93** | 21 | 147 | 768 |
| train | AFTER A | 450 | 21 | 93 | 24 | 180 | 768 |
| val | BEFORE | 75 | 6 | 6 | 3 | 54 | 144 |
| val | **AFTER B** | **96** | 6 | 6 | 3 | 33 | 144 |
| test | BEFORE | 180 | 45 | **96** | 6 | 81 | 408 |
| test | **AFTER B** | **219** | 45 | **96** | **9** | 39 | 408 |
| test | AFTER A | 219 | 48 | 96 | 6 | 39 | 408 |
| hold | 전부 | 0 | 0 | 0 | 0 | 96 | 96 |
| **전체** | BEFORE | 693 | 72 | **243** | 30 | 378 | 1,416 |
| **전체** | **AFTER B** | **801** | 72 | **195** | 33 | 315 | 1,416 |
| 전체 | AFTER A | 765 | 75 | 195 | 33 | 348 | 1,416 |

**헤드라인**: strict-H 코퍼스 **243 → 195 (−48, −19.8 %)**, 전부 scene12에서 나왔다.
**test의 H 96은 불변**(scene14 60 + scene15 36) — 논문 헤드라인 H 행의 분모는 흔들리지 않는다.
근거: `logs/corpus_census.log`.

씬별 strict-H 인구(BEFORE → AFTER B):

| 분할 | 씬 | H b | H a |
|---|---|---|---|
| test | scene14 | 60 | 60 |
| test | scene15 | 36 | 36 |
| train | scene09 | 60 | 60 |
| train | **scene12** | **48** | **0** |
| train | scene17 | 33 | 33 |
| val | scene20 | 6 | 6 |

---

## 4. scene12 판정 — 48개 "strict-H" 프레임은 무엇이 되는가

**판정: 48/48이 strict-H를 잃는다. 정본(변형 B)에서 48/48이 티어 V로 재분류된다 — D50 예측 그대로다.**

| 참조 | H | V | H_weak | none_in_fov |
|---|---|---|---|---|
| BEFORE (동결 08-20) | **48** | 0 | 0 | 0 |
| **AFTER B (본 라운드 융합, 정본)** | **0** | **48** | 0 | 0 |
| AFTER A (boost 자기 융합) | **0** | 12 | 3 | 33 |

**두 참조가 합의하는 것**: 48프레임 중 strict-H로 살아남는 것은 **0**개다.
증거는 `tier_of`(labeler.py:385)의 정의 자체다 — `H ⟺ int_px == 0 ∧ edge_visible == 0`.
교정 후 실측:

| 밴드 | 변형 | int_px (48프레임 범위) | edge_visible | polar GT+ 칸 |
|---|---|---|---|---|
| e | A | 2,458 – 9,098 | 0 | 0 – 3 |
| e | B | 2,739 – 9,322 | 0 | 2 – 7 |
| e2 | A | 26 – 71 | 0 – 1 | 0 – 1 |
| e2 | B | 177 – 1,537 | 0 – 1 | 3 – 9 |

낙차 **내부에 떨어진 재투영 픽셀이 모든 프레임에서 0이 아니다** → H 불가.
BEFORE에서 `int_px = 0`이었던 이유는 은닉이 아니라 **떨어질 footprint가 50셀뿐**이어서다.

**두 참조가 갈리는 곳(정직 기록)**: 변형 A에서는 33/48이 `none_in_fov`로 간다.
`none_in_fov`는 "낙차가 폴라 그리드(12 m · ±31.1°) 밖"이라는 뜻이지 "안 보인다"가 아니다 —
같은 프레임들이 `int_px` 수천을 갖는다(위 표). 원인은 은닉이 아니라 **커버리지**다:
`boost_e2`의 근거리·저고도 카메라는 ON 팔 그리드의 **27.7 %**만 덮어 융합 footprint가
raw 1,172 / kept 9셀까지 얇아지고, 그 조각이 그리드 웨지 밖에 놓인다.
변형 B(본 라운드 융합, ON 74.8 % 커버리지)에서는 이 얇아짐이 사라지고 48/48이 V가 된다.
**→ D50의 "H→V" 예측은 충분한 커버리지의 참조에서 정확히 재현된다.** A는 커버리지 하한,
B는 코퍼스 내 최선 참조로 읽으면 된다.

---

## 5. 게이트 — "s12류 아티팩트 0"

### 5.1 왜 순진한 형태로는 안 되는가 (먼저 밝힌다)

"strict-H인데 위험이 픽셀을 기여하는 프레임 수"를 **한 라벨 파일 안에서** 세면 항상 0이다.
`tier_of`가 strict-H를 `int_px == 0 ∧ edge_visible == 0`으로 **정의**하기 때문이다.
실측으로도 그렇다:

| 라벨 집합 | strict-H 프레임 | 그중 `int_px>0` 또는 `edge_visible>0` 또는 `int_px_fallback>0` |
|---|---|---|
| BEFORE (결함본) | 243 | **0** |
| AFTER B | 195 | **0** |
| AFTER A | 195 | **0** |

(`int_px_fallback`은 `tier_of`가 **읽지 않는** 카운터라 이 검사에서 유일하게 비자명한 항인데,
세 집합 모두 0이다.) 결함본조차 통과하므로 **이 형태는 게이트가 아니다.**
근거: `code/g7_corpus_census.py` → `logs/corpus_census.log`.

### 5.2 실질 게이트 — footprint 퇴화 재측정 (**통과, 위반 0**)

scene12의 H를 거짓으로 만든 것은 라벨 파일 내부 모순이 아니라 **footprint가 조각이라 픽셀이
떨어질 자리가 없었다**는 사실이다. 그래서 교정 코퍼스에서 **strict-H를 아직 하나라도 들고 있는
모든 (라운드, 씬) 쌍**에 대해, 사용 중인 instrument의 footprint를 **다른 instrument(depth 융합,
메모리 내 계산 · 디스크 무기록)**로 다시 재고 비교했다.

> 판정식: `ratio = 사용 instrument 셀 / 융합 instrument 셀`.
> 융합이 500셀 이상인데 `ratio < 0.10`이면 **FLAG**.
> (수리 전 scene12 = 50 / 33,605 = **0.0015** → 이 식이 잡아내는 바로 그 형태.)

| 라운드 | 씬 | H | 사용 | 사용 셀 | 융합 셀 | ratio | 판정 |
|---|---|---|---|---|---|---|---|
| `260819_main_on` | scene09 | 15 | aabb | 87,954 | 14,825 | 5.93 | ok |
| `260819_main_on` | scene14 | 18 | aabb | 54,213 | 15,864 | 3.42 | ok |
| `260819_main_on` | scene15 | 3 | aabb | 2,750 | 2,650 | 1.04 | ok |
| `260819_main_on` | scene17 | 9 | aabb | 65,833 | 33,104 | 1.99 | ok |
| `260820_boost_h_on` | scene09 | 24 | aabb | 87,954 | 1 | 87,954 | ok |
| `260820_boost_h_on` | scene14 | 21 | aabb | 54,213 | 0 | ∞ | ok |
| `260820_boost_h_on` | scene15 | 18 | aabb | 2,750 | 281 | 9.79 | ok |
| `260820_boost_h_on` | scene17 | 24 | aabb | 65,833 | 0 | ∞ | ok |
| `260820_boost_e_on` | scene09 | 21 | aabb | 87,954 | 0 | ∞ | ok |
| `260820_boost_e_on` | scene14 | 21 | aabb | 54,213 | 0 | ∞ | ok |
| `260820_boost_e_on` | scene15 | 15 | aabb | 2,750 | 521 | 5.28 | ok |
| `260820_boost_e2_on` | scene20 | 6 | aabb | 60,659 | 3,503 | 17.32 | ok |

> **`s12류 아티팩트 = 0`. FLAG 0 / 12쌍.**

부호가 결정적이다. 진짜 strict-H 씬은 **`ratio ≥ 1.0`** — 카메라가 낙차를 못 보니 융합이 오히려
적게(H 부스트 라운드에서는 0셀까지) 잰다. **그것이 은닉의 물리적 서명**이다.
scene12는 정반대(`ratio = 0.0015`)였다 — 카메라는 잘 봤고 **AABB 레이가 눈이 멀었다**.
구현: `code/g7_gate_degenerate.py` → `logs/gate_degenerate.log`.

### 5.3 보조 게이트 — 교차 참조 재유도 (**통과, 불일치 0**)

수리된 240프레임을 **두 교정 참조(A, B) 모두에서** 다시 티어 유도했을 때,
한쪽에서 strict-H이고 다른 쪽에서 아닌 프레임: **0개**.
H 지위는 참조 선택에 의존하지 않는다 — 즉 §4의 판정은 커버리지 선택의 산물이 아니다.

---

## 6. 영향 지도 — 옛 boost 라벨을 참조하는 하류 산출물 (**수정하지 않았다**)

### 6.1 왜 영향이 있는가 (수치)

교정된 240프레임 중 GT가 실제로 바뀐 것은 on 팔 120프레임이다:

| 분할 | 씬 | 팔 | 프레임 | GT+ 칸 b | GT+ 칸 a | hazard 프레임 b | a |
|---|---|---|---|---|---|---|---|
| test | scene07 | on | 48 | 0 | **165** | 0 | **42** |
| val | scene08 | on | 24 | 0 | **108** | 0 | **21** |
| train | scene12 | on | 48 | 126 | **252** | 48 | 48 |
| (각 씬 off 팔 120프레임) | | off | 120 | 0 | 0 | 0 | 0 |

`eval_polar.py:161`의 `haz = on & pos.any(1)` 때문에 **평가 분모가 움직인다**:

| 분할 | BEFORE | AFTER B |
|---|---|---|
| train | V 438 · E 21 · H 141 · H_weak 21 | V 486 · E 21 · **H 93** · H_weak 21 |
| val | V 75 · E 6 · H 6 · H_weak 3 | **V 96** · E 6 · H 6 · H_weak 3 |
| test | V 180 · E 45 · H 96 · H_weak 6 | **V 219** · E 45 · **H 96** · **H_weak 9** |

* **H 행(논문 헤드라인)**: test H 96 불변 — D42/D50의 "recall 분모 미오염"은 **H 행에 한해 참**이다.
* **V 행**: test V 분모 **180 → 219 (+21.7 %)**, val V **75 → 96 (+28 %)**. 미오염이 아니다.
  옛 표의 V recall은 **다른 분모** 위 숫자다.
* **훈련**: scene12의 48프레임이 train에 **잘못된 GT**(프레임당 2–3칸 vs 올바른 4–8칸)로 들어갔고,
  scene07·scene08의 72프레임은 GT 0칸(=음성)으로 들어갔다. → 재훈련 전에는 아래 산출물의
  수치를 교정 GT로 재해석할 수 없다.

### 6.2 참조 파일 목록 (경로만 — 무수정)

카테고리별. 검색식
`grep -rIl -e 'labels_boost_' -e 'manifest_boost_' -e 'dataset_manifest_v2_full' -e 'labels_v1_full' -e 'split_v2_full'`
가 잡은 **113파일**(`.git` · `v3_0823` 제외)을 아래로 갈음한다.

**(a) 코퍼스 조립 · 스크립트**
```
experiments/dayrun_0820/code/merge_corpus.py
experiments/dayrun_0820/code/run_aux.sh
experiments/dayrun_0820/code/run_yolo_all.sh
experiments/weekend_0823/v2s/code/merge_corpus_v2s.py
experiments/weekend_0823/v2s/run_v2s_queue.sh
experiments/weekend_0823/code/run_newmodels.sh
experiments/weekend_0823/code/run_ctrl_eval_depth.sh
experiments/weekend_0823/cue_audit/eval_cueoff.sh
experiments/weekend_0823/fusion/code/run_fusion_eval.sh
experiments/nightrun_0820/ctrl_dressing/run_ctrl_eval.sh · sync_on_arm.py
```

**(b) 코퍼스·분할 산출물 (옛 boost 라벨을 그대로 담고 있음)**
```
experiments/dayrun_0820/dataset_manifest_v2_full.json        ← 본 작업의 교정 대상
experiments/dayrun_0820/annotations/labels_v1_full.json
experiments/dayrun_0820/annotations/labels_boost_{h,e,e2}.json
experiments/dayrun_0820/manifest_boost_{h,e,e2}.json
experiments/dayrun_0820/split_v2_full.json · SPLIT_PROPOSAL_v2_full.md
experiments/dayrun_0820/GATES_REPORT_v2full.md
experiments/weekend_0823/v2s/dataset_manifest_v2s_full.json
experiments/weekend_0823/v2s/annotations/labels_v2s.json
experiments/nightrun_0820/ctrl_dressing/manifest_ctrl.json · split_ctrl.json
```

**(c) 훈련/평가 런 (config.json이 `dataset_manifest_v2_full.json`을 가리킴)**
```
experiments/dayrun_0820/runs/v2/{rgb,depth,b2}_s4{2,3,4}/config.json  (+ rgb_s42_aux)  9+1런
experiments/weekend_0823/v2s/runs/{rgb,depth,b2}_s4{2,3,4}/config.json               9런
experiments/weekend_0823/newmodels/runs/{resnet50,tu-convnext_tiny}_s4{2,3,4}/config.json  6런
experiments/dayrun_0820/runs/yolo_s4{2,3,4}/cells_{val,test}/det2cell.json
experiments/dayrun_0820/runs/yolo_oracle_ceiling_full/det2cell.json
experiments/weekend_0823/v2s/runs/yolo_s4{2,3,4}/cells_{val,test}/det2cell.json
```

**(d) 트윈·층화 분석 산출물**
```
experiments/dayrun_0820/runs/v2/*/twin/twin_analysis.md                   (10)
experiments/weekend_0823/v2s/runs/*/twin/... · fusion/s4*/fused_{or,max}/twin/twin_analysis.md
experiments/nightrun_0820/ctrl_dressing/twin_old{,_depth}_s4{2,3,4}/twin_analysis.md
experiments/nightrun_0820/{STRADDLE_REPORT.md,TWIN_STRATIFICATION.md}
experiments/nightrun_0820/code/{b4_straddle.py,b5_twin_strat.py}
experiments/nightrun_0820/narrative/diag_v2/{DIAG_V2.md,diag_v2.py}
```

**(e) 공개 표·보고서 (수치가 옛 GT 위에 있음)**
```
experiments/mainrun_0819/METRICS.md · RESULTS_DRAFT.md · DECISIONS.md
experiments/dayrun_0820/DAYRUN_REPORT.md
experiments/weekend_0823/MORNING_REPORT_0823.md
experiments/weekend_0823/cue_audit/{CUEOFF_RESULT_v2.md,H_CUE_AUDIT.md,PREREGISTRATION.md,build_h_cue_table.py}
experiments/weekend_0823/fusion/FUSION_ROW.md
experiments/weekend_0823/a3_viewpoint/{3A_VIEWPOINT_AUDIT.md,a3_viewpoint.py}
experiments/weekend_0823/c2_rootcause/{C2_ROOTCAUSE.md,c2_audit.py}
experiments/weekend_0823/photometric/{PHOTOMETRIC_STRESS.md,PHOTO_NUMBERS.json,code/*.py}
experiments/weekend_0823/v2s/V2S_ADOPTION.md
experiments/weekend_0823/redteam/{R1_novelty,R2_method,R3_repro,R6_line_edits,REDTEAM_0823}.md
experiments/weekend_0823/rt_response/{APPEND_METRICS.md,README.md,code/*.py,f7_hpair_pixdiff.json}
experiments/mainrun_0819/realworld/REALWORLD_GRID_PROTOCOL.md
```

**우선 재판정 후보 3건**(재훈련 없이 지금 다시 셀 수 있는 것):
`cue_audit/CUEOFF_RESULT_v2.md` §4.1(scene12 = 이제 V 씬 → paired-H 0 확정),
`a3_viewpoint/3A_VIEWPOINT_AUDIT.md`(티어 층화가 바뀜),
`fusion/FUSION_ROW.md`(E/H 행 분모).

---

## 7. 교정 GT 매니페스트

| 파일 | 내용 |
|---|---|
| `experiments/v3_0823/dataset_manifest_v2corr.json` | **정본**. 2,832프레임 · 240 교정(`label_source: g7fix-B`) · 2,592 원본 |
| `experiments/v3_0823/dataset_manifest_v2corr_roundown.json` | 민감도. 같은 240프레임을 변형 A 라벨로 |
| `experiments/v3_0823/annotations/labels_v1_full_g7fix.json` | 위 매니페스트의 짝이 되는 병합 라벨(+ `scene_footprint` 교체) |
| `experiments/v3_0823/annotations/labels_v1_full_g7fix_roundown.json` | 변형 A 짝 |
| `experiments/v3_0823/manifest_boost_{e,e2}_g7fix.json` | 변형 A 라운드 단위 매니페스트 (672 / 384프레임) |
| `experiments/v3_0823/manifest_boost_{e,e2}_g7fixM.json` | 변형 B 결함 씬 매니페스트 (144 / 96프레임) |

`meta`에 `corrects` · `defect` · `g7_mapping_rule` · `g7_affected_frames` · `g7_label_sets` ·
`g7_shadow_render_trees`가 박혀 있어 매니페스트만 읽어도 §0 규칙이 복원된다.
**`boost_h`는 교정 대상이 아니므로 원본 라벨이 그대로 흐른다.**
**원본 매니페스트 3종(`dataset_manifest_v{1,2,2_full}.json`)과 `split_*.json`은 손대지 않았다.**

분할 파일은 **재생성하지 않았다** — 교정은 씬을 옮기지 않고 티어만 바꾸며,
`split_v2_full.json`은 씬 단위이므로 그대로 유효하다. 다만 §6.1의 분모 이동 때문에
`SPLIT_PROPOSAL_v2_full.md`의 티어 균형 근거는 **재작성 대상**이다(미실행).

---

## 8. 남은 것 · 한계

1. **재훈련 미실행** — 본 작업은 CPU 전용 지시다. 교정 GT로 훈련·평가를 다시 돌리는 것이
   코퍼스 v3의 본체이고, 그 전까지 §6.2의 어떤 수치도 교정본 기준으로 인용할 수 없다.
2. **결측 입력 0** — 재렌더가 필요한 씬·카메라는 **없다**. 26개 boost 쌍 × 2팔 전부
   `missing_depth = 0`이고, 융합은 24뷰 전부를 썼다.
3. **변형 A의 커버리지 한계**는 결함이 아니라 boost 카메라 밴드 편향의 결과다(§4).
   9월 v3에서 더 나은 참조를 원하면 **main + boost_e + boost_e2의 depth를 한 번에 풀링**해
   융합하는 것이 옳다(현 `fuse_heightmap.py`는 라운드 1개만 받는다 — 소폭 확장 필요).
4. **D42의 "오라클 6씬" 표기 정정 필요**(§1.2) — 실측은 3씬 / 5쌍이다.
5. `boost_h`(4씬 · 192프레임)는 **결함 없음**이 실측으로 확인됐다 — 재라벨 불요.

---

## 부록 — 재현 명령

```bash
export PYTHONNOUSERSITE=1
PY=/home/vislab/miniconda3/envs/env_seg/bin/python      # numpy 2.2.6
R=/home/vislab/Desktop/work_sy/Practice_NegObs
cd $R/experiments/mainrun_0819/code/labeling

$PY $R/experiments/v3_0823/code/g7_make_shadow.py        # 1. 섀도 렌더 트리(심링크)
$PY fuse_heightmap.py --on-round $R/dataset/260820_boost_e_on_g7fix \
    --off-round $R/dataset/260820_boost_e_off_g7fix \
    --scenes scene07,scene08,scene12 --grid gridspec_v1.json --workers 6
$PY fuse_heightmap.py --on-round $R/dataset/260820_boost_e2_on_g7fix \
    --off-round $R/dataset/260820_boost_e2_off_g7fix \
    --scenes scene07,scene12 --grid gridspec_v1.json --workers 4
rm $R/dataset/260820_boost_e_on_g7fix/train/scene08/heightmap_fused*   # aabb ON / fused OFF
$PY $R/experiments/v3_0823/code/g7_pairing_audit.py      # 2. 팔별 채택 감사
$PY $R/experiments/v3_0823/code/g7_variantB.py           # 3. 변형 B 트리
$PY labeler.py --on-round ... --off-round ... --grid gridspec_v1.json --workers 8 --out ...
$PY build_manifest.py --labels ... --on-round ... --off-round ... --out ...
$PY $R/experiments/v3_0823/code/g7_build_v2corr.py       # 4. 교정 매니페스트
$PY $R/experiments/v3_0823/code/g7_compare.py            # 5. before/after 원장
$PY $R/experiments/v3_0823/code/g7_s12_detail.py         #    s12 프레임별 + 대조군
$PY $R/experiments/v3_0823/code/g7_corpus_census.py      #    코퍼스 인구
$PY $R/experiments/v3_0823/code/g7_scan_all_boost.py     #    결함 범위 전수 스캔
$PY $R/experiments/v3_0823/code/g7_gate_degenerate.py    # 6. 실질 게이트
```
