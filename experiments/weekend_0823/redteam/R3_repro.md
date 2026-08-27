# R3_repro — 레드팀 3파 (재현성·회계 감사)

작성 2026-08-23 · 감사자 RED TEAM R3 (Opus, 독립 재계산) · 작업방 `experiments/weekend_0823/redteam/`
읽은 것: `Docs/archive/campaign_status/PROJECT_STATE_0823.md` §1–3·§8·§12 · `experiments/mainrun_0819/METRICS.md`
(정의·Night·Resume 절) · `experiments/mainrun_0819/code/labeling/labeler.py` CONSTANTS ·
`experiments/dayrun_0820/code/merge_corpus.py` · `experiments/dayrun_0820/SPLIT_PROPOSAL_v2_full.md` +
`split_v2_full.json` · `experiments/nightrun_0820/MORNING_REPORT_0821.md` · `DECISIONS.md` D1–D32 ·
`realworld/PROTOCOL_SHOOT.md` · `code/infer_photo.py` · `code/gridspec.py` · `code/README_CODE.md`

**감사 방식**: 문서를 읽고 옮겨 적은 게 아니라, 매니페스트·라벨 JSON에서 **직접 재계산**했다.
실행 가능한 주장은 실제로 실행해서 확인했다(`infer_photo.py` 3회 호출 포함).

> **한 줄 요약.** 숫자 회계는 **깨끗하다** — 5범주 2832 회계가 매니페스트에서 정확히 재현되고,
> 중복 프레임 0, 라벨↔매니페스트 항등, 티어 규칙이 raw_vis에서 위반 0으로 재파생된다.
> 무너지는 건 **회계가 아니라 배포**다: 헤드라인 표의 정본 원장(`SEED_TABLE.md`)과 런별
> 증거 파일 77개가 `.gitignore`의 `runs/` 한 줄에 통째로 잡혀 git에 없다. 그리고 **실측 프로토콜은
> 오늘 실행 불가** — 셀 명명 규약이 폐기된 15칸 V0 그리드에 머물러 있고, 문서화된
> `infer_photo.py` 실행줄 2개는 그대로 치면 fatal로 죽는다.

---

## 1. 분모 회계 검증 — **성립 (PASS, 이의 없음)**

### 1.1 5범주 재계산 (매니페스트 직접 집계)

`experiments/dayrun_0820/dataset_manifest_v2_full.json`, 2,832 프레임을 `tier` 필드로 집계:

| 범주 | PS §1-3 주장 | **재계산** | 판정 |
|---|---|---|---|
| V | 693 | **693** | ✓ |
| E | 72 | **72** | ✓ |
| H (strict) | 243 | **243** | ✓ |
| H_weak | 30 | **30** | ✓ |
| none_in_fov | 378 | **378** | ✓ |
| off | 1416 | **1416** | ✓ |
| **합** | 2832 | **2832** | ✓ |

on팔 = 693+72+243+30+378 = **1416** = off팔 1416 → 트윈 짝이 정확히 맞는다.
v1 코퍼스도 동일하게 성립: **V438·E36·H45·H_weak12·none261·off792 = 1584** (재계산 일치, 33씬×48컷,
(scene,arm,cond) 그룹 크기 전부 8 = 8캠).

### 1.2 `::round` 접미사 이중계상 감사 — **이중계상 0**

의심 지점: `merge_corpus.py`가 boost 라운드에만 `::<round>`를 붙여 frame_id를 유일화한다.
동일 프레임이 접미사만 달리해 두 번 세어지는가?

| 검사 | 결과 |
|---|---|
| frame_id 유일성 | 2832/2832 유일, 중복 0 |
| **rgb 파일 경로** 유일성 | 2832/2832 유일, 중복 0 |
| (scene, arm, cond, cam d/h_rel/yaw/pitch/hfov) 동일 튜플 | **0쌍** — 물리적으로 같은 컷이 두 번 들어온 사례 없음 |
| 라운드 분포 | main 1584 / boost_h 192 / boost_e 672 / boost_e2 384 = 2832 ✓ |

접미사 없이 병합하면 **정확히 192건**이 충돌한다(D24 주장과 일치, §4 참조). 충돌 조합은 전부
`boost_h ↔ boost_e`, 씬은 s09·s14·s15·s17 각 48건 — 두 라운드가 같은 seed(20260820)·같은 파일명을
쓰되 샘플러 밴드(h 0.25–1.0 vs 1.2–1.9)가 달라 **다른 포즈의 다른 컷**이다. 접미사는 필요했고,
그 결과 이중계상은 없다. **basename은 최대 66회 반복되지만(파일명 재사용) 경로·포즈는 전부 다르다.**

### 1.3 라벨 무결성 (추가 검사, 요구 밖)

| 검사 | 결과 |
|---|---|
| `labels_v1_full.json` ↔ 매니페스트 frame_id 집합 | **완전 일치** (2832 = 2832) |
| 두 파일의 `polar_gt` 벡터 불일치 | **0건** |
| `none_in_fov`인데 양성 칸 있음 / `V·E·H·H_weak`인데 양성 0 / `off`인데 양성 있음 | **전부 0건** |
| 티어 규칙(V:int_px≥50 → E:edge≥0.05 → H_weak:0<int_px<50 → H:기여 0)을 `raw_vis`에서 재파생 | **위반 0건** |
| D26 기록 `split_v2_full sha 9bc44d4efbe6e83e` | sha256[:16] **일치** ✓ |

**결론: 분모 회계는 방어 가능하다.** 심사자가 프레임 수를 검산해도 매니페스트에서 그대로 나온다.
단 아래 1.4의 문서 결함 두 개는 심사자가 실제로 걸릴 지점이므로 고쳐야 한다.

### 1.4 회계가 **문서에서** 깨지는 지점 2건 (데이터가 아니라 표기 문제)

**(a) `SPLIT_PROPOSAL_v2_full.md` §Tier distribution 의 `frames` 열이 실제 분할 크기가 아니다 — 심각.**

그 표는 `frames` 열에 train 1368 / val 231 / test 729 / global 2328을 적지만, 이건 **V+E+H+off 소계**이지
분할 크기가 아니다. 실제(재계산):

| split | V | E | H | H_weak | none_in_fov | off | **실제 프레임** | 문서의 `frames` |
|---|---|---|---|---|---|---|---|---|
| train | 438 | 21 | 141 | 21 | 147 | 768 | **1536** | 1368 |
| val | 75 | 6 | 6 | 3 | 54 | 144 | **288** | 231 |
| test | 180 | 45 | 96 | 6 | 81 | 408 | **816** | 729 |
| HOLD | 0 | 0 | 0 | 0 | 96 | 96 | **192** | (192) |
| 비-HOLD 합 | 693 | 72 | 243 | 30 | 282 | 1320 | **2640** | 2328 |

같은 문서 안에서 `PROOF-4`는 "every non-held frame resolves to exactly one split: 0 bad of **2640**"이라고
쓴다. 즉 **한 문서가 2640과 2328을 둘 다 주장**하고, 차이 312 = H_weak 30 + none_in_fov 282다.
per-scene 표도 같은 병이 있다(예: scene03 `frames` 144인데 V57+E0+H0+off72 = 129, 나머지 15 = none_in_fov).
→ 이건 정확히 PS §12.3-⑥이 "심사자가 프레임 수 검산할 때 걸리는 지점"이라 예고한 함정인데,
**우리 자신의 분할 문서가 그 함정에 빠져 있다.** `frames` 열 이름을 `V+E+H+off`로 바꾸고
`H_weak`·`none_in_fov` 열을 추가하면 끝난다(기존 파일 무수정 규칙 때문이면 append 절로).
`test 816 = 408 on + 408 off`는 `METRICS.md` N절이 이미 옳게 쓰고 있으므로 분할 문서만 뒤처져 있다.

**(b) `METRICS.md` §2.4의 τ_edge 값이 코드·매니페스트와 모순 — 경미(수치 무영향).**

`METRICS.md:101`: "Operating point used everywhere below: τ_int = 50, **τ_edge = 0.02**".
그런데 `labeler.py`의 `TAU_INT_DEF, TAU_EDGE_DEF = 50, 0.05`, 매니페스트 `meta.tau_strict =
{tau_int:50, tau_edge:0.05}`, PS §1-3·§12.3-④도 0.05다. 다만 아래 §1.5 때문에 **수치는 실제로 같다** —
표기만 고치면 된다.

### 1.5 [신규 발견] τ_edge 민감도 근거가 **공허하다** — §12.3-④ 결재에 직접 영향

`METRICS.md` §2.4의 "strict-H는 9조합 전부에서 45프레임, V/E 경계만 V 417–453 / E 33–42로 움직인다"를
raw_vis에서 재파생해 검증했다 — **정확히 재현된다**:

```
tau_int=  1 → V453 E33 H45 Hw0    tau_int= 50 → V438 E36 H45 Hw12    tau_int=200 → V417 E42 H45 Hw27
(위 세 줄은 tau_edge = 0.02 / 0.05 / 0.10 **어느 값에서도 완전히 동일**)
```

즉 **9조합이 아니라 실질 3조합**이다. τ_edge는 결과를 전혀 움직이지 못한다. 이유를 데이터에서 확인했다:

| edge_ratio 분포 (V가 아닌 hazard-on 프레임) | v1 (n=93) | v2_full (n=345) |
|---|---|---|
| `== 0` | 57 | 273 |
| `(0, 0.02)` / `[0.02, 0.05)` / `[0.05, 0.10)` | **0 / 0 / 0** | **0 / 0 / 0** |
| `≥ 0.10` (실제 최소 비영값) | 36 (min 0.505) | 72 (**min 0.44**) |

**edge_ratio는 0 아니면 0.44 이상인 완전 이봉 분포다.** 스윕 격자 {0.02, 0.05, 0.10}은 데이터가
하나도 없는 빈 구간 안에 통째로 놓여 있다. 따라서 "9조합 무민감"은 strict-H에 대해서는 참이지만,
**τ_edge라는 상수 자체는 이 코퍼스가 전혀 제약하지 못한다**(0 초과 0.44 미만 어느 값이든 동일).

> **권고 (§12.3-④ 문안 교체)**: "τ_edge = 0.05 채택, 근거는 9조합 무민감" → 이렇게 쓰면 심사자가
> 스윕 격자를 데이터 분포와 대조하는 순간 무너진다. 정직한 문장은
> **"이 코퍼스에서 립 가시성은 사실상 이진(edge_ratio = 0 또는 ≥ 0.44)이므로 E/H 경계는 τ_edge에
> 무관하다 — 0.05는 (0, 0.44) 구간의 임의 대표값이며 미세조정 여지가 없다"**이다.
> τ_int(50)만이 실제로 결과를 움직이는 상수이고, 그건 V/E 경계를 ±15/±6프레임 움직인다.

---

## 2. 낯선 사람이 헤드라인 행을 재현할 수 있는가 — **불가. git만으로는 못 한다.**

`dataset/`(31 GB 렌더)이 미추적인 건 의도된 설계이고 문서화돼 있다. 문제는 **그 외에도 빠져 있는
것들**이다. 실제로 `git check-ignore`로 전수 확인했다.

### 2.1 치명 — 헤드라인의 정본 원장이 git에 없다

`.gitignore`에 `runs/`(디렉토리명 무한정 매칭) 한 줄이 있어, 다음이 **전부 미추적**이다:

| 경로 | PS 상 지위 | 상태 |
|---|---|---|
| `experiments/dayrun_0820/runs/v2/SEED_TABLE.md` | **PS §8이 지정한 본 표 4행의 정본 원장** | **git에 없음** |
| `experiments/*/runs/**/eval_test/METRICS_SECTION.md` (14개) | 런별 CI·지표 정본 | 없음 |
| `experiments/*/runs/**/{metrics.json, per_frame*.csv, config.json, metrics.csv}` | 재계산의 유일 입력 | 없음 |
| `experiments/*/runs/**/twin/twin_analysis.md`·`twin_pairs.csv` | 인과 주장 원장 | 없음 |
| `*.pt` 체크포인트 18개 (2.7 GB) | zero-shot·실측 추론에 필수 | 없음(용량상 타당) |

`runs/` 트리 아래 **.md/.json/.csv/.yaml 합계는 9.8 MB**다. 2.7 GB는 전부 `.pt` 가중치다.
즉 **한 줄짜리 규칙이 10 MB의 증거를 2.7 GB의 가중치와 함께 버리고 있다.** 이건 용량 판단이 아니라
사고다 — `.gitignore`에 `!experiments/*/runs/**/*.md` 류의 예외 3줄이면 해결된다.

부수 피해 실측: `METRICS.md` §13 "Links" 표 **20개 대상 중 8개가 클론에서 죽은 링크**다
(`runs/rgb_s42/eval_test/METRICS_SECTION.md`, 같은 폴더의 `metrics.json`·`per_frame.csv`,
`runs/depth_s42/...`, `runs/compare_rgb_depth/...`, `runs/*/twin/twin_analysis.md`,
`runs/*/metrics.csv`, `audit_samples/`). 논문이 근거 파일을 가리키는 표의 40%가 공개 저장소에서
404가 된다.

### 2.2 중대 — 매니페스트에 절대경로가 박혀 있다

`dataset_manifest_v2_full.json`의 `rgb`/`depth` 필드 **2832/2832 전부**가
`/home/vislab/Desktop/work_sy/Practice_NegObs/dataset/...` 절대경로다. 다른 기계에서는 한 프레임도
안 열린다. 경로 재작성 도구·규약이 문서 어디에도 없다. (라벨 JSON은 경로 비의존이라 무사.)

### 2.3 중대 — 환경 고정 파일이 없다

- 저장소 루트에 `requirements.txt`/`environment.yml` **없음**. U-Net 스택 버전은 산문에만 있다
  (`HARNESS_NOTES.md` 표: torch 2.5.1, smp 0.5.0, timm 1.0.28, transformers 5.15).
- YOLO만 `code/yolo/requirements_yolo.txt`가 있다(ultralytics 8.4.123 · torch 2.13.0+cu130) —
  **U-Net 스택과 torch 메이저가 다르다**. 두 개의 서로 다른 파이썬 환경이 필요하다는 사실이
  README 어디에도 한 곳에 정리돼 있지 않다.
- 실행 커맨드가 기계 절대경로에 묶여 있다: `README_CODE.md`의 `$PY` =
  `/home/vislab/miniconda3/envs/env_seg/bin/python`.
- 환경 이름도 문서 간 충돌: PS §8은 `conda activate env_isaaclab`(렌더용), 코드 계열은
  `env_seg`(훈련용), `infer_photo.py` docstring도 `env_seg`. 어느 트랙이 어느 환경인지
  한 줄로 명시된 곳이 없다.

### 2.4 재현 사슬 판정표

git 클론만 가진 낯선 사람 기준:

| 단계 | 필요 산출물 | git에 있나 | 판정 |
|---|---|---|---|
| 렌더 → `dataset/` | Isaac Sim + NVIDIA USD 에셋 | 없음(**재배포 금지 라이선스**, 문서화됨) | **불가** — 원리적 |
| 렌더 → 라벨 | `labeler.py`, `gridspec_v1.json`, 하이트맵·depth 사이드카 | 코드 ✓ / 사이드카 ✗ | 불가 |
| 라벨 → 훈련 입력 | `labels_v1_full.json`, `dataset_manifest_v2_full.json`, `split_v2_full.json` | **전부 ✓** | 가능(단 이미지 없음) |
| 훈련 | `train_polar.py` + 레시피 v2 플래그 | ✓ (README_CODE에 전문) | 이미지만 있으면 가능 |
| 평가 → 헤드라인 | 체크포인트, `eval_polar.py`, `aggregate_seeds.py` | 코드 ✓ / ckpt ✗ | **불가** |
| 헤드라인 대조 | `SEED_TABLE.md` | **✗** | **불가 — 대조할 정답이 없다** |

**요약: 라벨+매니페스트+분할 사슬은 완전하다(이건 잘 돼 있다). 끊긴 건 ① 결과 원장 ② 체크포인트
③ 환경 고정 ④ 경로 이식성이다.** ①③④는 합쳐서 10 MB 이하이고 오늘 안에 고칠 수 있다.
②는 최소 3개(rgb/depth/b2 s42) ≈ 300 MB — 릴리스 첨부나 외부 호스팅으로 가는 게 맞다.

---

## 3. 프로토콜 실행 가능성 — **오늘은 불가. 랩메이트가 반드시 질문하게 된다.**

### 3.1 차단급 — 셀 명명 규약이 폐기된 V0 그리드다

`PROTOCOL_SHOOT.md` §⑤:
> 방위 A–E 5등분 / 거리 **1 = 0–3 m, 2 = 3–7 m, 3 = 7–15 m** / 셀 = `A1`…`E3`, **총 15칸**

현행 정본은 `gridspec_v1.json` = 5섹터 × **4밴드 [0,2)/[2,5)/[5,8)/[8,12) = 20칸**,
셀 id는 `A1..E1, A2..E2, A3a..E3a, A3b..E3b`(도구 출력으로 실측 확인).
프로토콜은 스스로 "⚠ 잠정 — 레포의 실제 grid 상수가 확정되면 교체할 것"이라 적어뒀지만
**D19(08-20, 그리드 V1 채택) 이후 교체되지 않았다.** 결과:

- `sites.csv` 예시 12행의 `gt_cells`가 전부 무효다(`C1;C2`, `C2;C3`, `D2;D3`, `E1;E2`…).
  `C3`는 V1에서 3a인지 3b인지 **결정 불가능**하다.
- 밴드 경계 자체가 다르다: 예시 `EX_SUNKEN01` dist 3.0 m는 프로토콜상 `C1;C2`지만 V1에서는 밴드 2 단독.
- 프로토콜의 밴드 3 상한 15 m는 **그리드 밖**이다. 예시 `EX_RIVERBANK04` dist **12.0 m**는 V1
  최외곽 [8,12) 밖 → 그 프레임은 `none_in_fov`가 되고 GT를 부여할 수 없다.
- §12.6 V2S(10섹터)가 채택되면 A–E 5개가 10개가 되어 **또 한 번 전면 교체**된다.

### 3.2 차단급 — "프레임을 세로로 5등분"은 폴라 섹터가 아니다

프로토콜은 섹터를 **이미지 5등분**으로 정의한다. 그런데 그리드 섹터는 월드 방위각 ±31.1°(=62.2°)
고정이고, PS §12.3-①이 스스로 "폰 화각 ≠ 62.2°이므로 그리드 각은 카메라 화각과 독립"이라 못박았다.
폰 hfov가 62.2°가 **아닌 한** 이미지 5등분 ≠ 섹터 5등분이다(EXIF 없으면 `infer_photo.py`는
69°를 가정한다 — 실측 확인). **주석 규칙과 투영 규약이 서로 모순**이며, 어느 쪽이 정본인지 없다.

### 3.3 차단급 — 문서화된 `infer_photo.py` 실행줄이 그대로 죽는다 (실행으로 확인)

`README_CODE.md:29–30`은 `--ckpt $W/runs/rgb_s42/best.pt --grid gridspec_v1.json`을 예시로 준다
($W = `experiments/mainrun_0819`). 실제로 돌려봤다:

```
(a) README_CODE 29줄 그대로:
    [fatal] checkpoint best.pt was trained on 15 cells but --grid says 20 (PROVISIONAL-GRID-V1)
(c) --grid 생략(기본값 = gridspec_v0.json):
    [fatal] checkpoint best.pt was trained on 20 cells but --grid says 15 (PROVISIONAL-GRID-V0)
(b) 교정판 --ckpt experiments/dayrun_0820/runs/v2/rgb_s42/best.pt --grid gridspec_v1.json --pitch -15:
    [infer_photo] PROVISIONAL-GRID-V1: 4 bands x 5 sectors = 20 cells · A1..E3b     ← 정상
```

원인: `mainrun_0819/runs/rgb_s42/best.pt`는 **15칸 V0 체크포인트**다(head 20 아님 — 직접 확인).
V1 체크포인트는 `dayrun_0820/runs/v2/{rgb,depth,b2}_s{42,43,44}/best.pt`다.
도구가 조용히 틀리지 않고 fatal로 죽는 건 **설계상 좋은 점**이지만, 문서화된 두 줄이 모두 틀렸으므로
랩메이트는 100% 막힌다. 게다가 정답 ckpt는 §2.1대로 **git에 없다**.

### 3.4 누락 상수·규약 전수 목록 (랩메이트가 물어볼 것들)

| # | 없는 것 | 지금 어떻게 되나 | 어디서 결정돼야 하나 |
|---|---|---|---|
| 1 | **정본 체크포인트 지정** | 9개 런 중 무엇을 실측에 쓸지 아무 데도 없음. 시드 43은 H .875, 44는 .594 — 고르기에 따라 결론이 바뀐다 | 결재 필요. 권고: 시드 42 고정 + 3시드 전부 돌려 병기 |
| 2 | **피치 추정 규약** | PS §12.3-①은 "수평선 기준 피치 추정"이라 쓰는데 **그런 코드가 없다**. `--pitch` 기본 0이고 도구가 "try --pitch -15"라고 힌트만 준다 | 수평선 기반 추정 구현 or "−15° 고정" 선언 |
| 3 | **`--fit` 판정** | 기본 letterbox, 훈련은 squash. 같은 프레임에서 max p **0.759(letterbox) vs 0.821(squash)** — squash가 per_frame.csv를 1.6e-4로 재현 | squash 채택 선언 권고(훈련 기하와 일치) |
| 4 | **hfov 처리 규약** | EXIF 없으면 69° 가정. 그리드 각은 62.2° 고정 | "EXIF 우선, 없으면 촬영 금지" or 69° 가정 명시 |
| 5 | **`cam_height_m` → `--height` 연결** | sites.csv에 높이를 적으라 하지만 그 값을 추론에 넣으라는 지시가 없음 | 프로토콜 ⑥에 한 줄 |
| 6 | **`dist_m` → 밴드 매핑표** | 프로토콜 밴드(0–3/3–7/7–15)와 V1 밴드(0–2/2–5/5–8/8–12)가 다름 | §3.1과 함께 교체 |
| 7 | **`azimuth` → 섹터 매핑표** | ±31.1°를 5등분하면 12.44°씩인데 프로토콜에 없음 | 표 한 개 추가(A: +31.1~+18.66 … E: −18.66~−31.1) |
| 8 | **PROTOCOL에 `infer_photo` 실행줄 없음** | 프로토콜 어디에도 도구 호출법이 없다. README_CODE에만 있고 그건 틀렸다(§3.3) | 프로토콜 ⑥에 교정된 3줄 |
| 9 | **환경 지정** | `PYTHONNOUSERSITE=1`은 docstring에만 | 프로토콜에 명시 |
| 10 | **주석자 2인 교차 절차** | PS §12.3-②가 "일치율 기록"을 권고하지만 절차·양식 없음 | 결재 #②와 함께 |
| 11 | **FA 대조컷 규약** | 프로토콜 ④-4는 "몸만 돌려 2–3장"인데 PS §12.3-③은 "같은 지점·같은 높이 짝 1장" — **수가 다르다** | 둘 중 하나로 통일 |

**판정: 랩메이트는 §⑤ 셀 이름을 쓰는 순간, 그리고 추론 도구를 처음 돌리는 순간, 두 번 막힌다.
파일럿 20장 촬영 자체는 가능하지만 GT 주석은 불가능하고 추론도 문서대로는 안 돌아간다.**

---

## 4. DECISIONS D1–D31 무작위 5건 대조

추첨: `random.seed(20260823)` → `random.sample(13개 수치 주장, 5)` (재현 가능, 사전 등록)
→ **D28 · D24 · D17 · D20 · D2**

| # | 주장 | 대조 소스 | 결과 |
|---|---|---|---|
| **D2** | 33씬 × 3조명 × 8캠 × 2팔 = 1584, 씬당 48컷, "거부 5쌍은 선언 치환" | `dataset_manifest_v1.json` | **CONFIRMED.** 1584 ✓ / 33씬 전부 정확히 48 ✓ / (scene,arm,cond) 그룹 크기 전부 8 ✓ / on 792 = off 792 ✓. 치환도 검산됨 — 조명이 L0·L5·L7 외에 L4 32 + L2 16 + L3 32 = 80프레임 = **정확히 5개 (씬,조명) 쌍** × 2팔 × 8캠 ✓ |
| **D17** | "s12(0.19×, **strict-H 18**)·s16(0.12×, **H 12**) → 융합 수리 2차 … (헤드라인 **H 75** 중 30 보유)" | 매니페스트 + `STATUS.md` | **SUPERSEDED (수치 자체는 당시 참, 현행 산출물과 불일치).** 최종 매니페스트의 strict-H는 45이고 **s12 = 0, s16 = 0**(H 45의 전부가 s09 15 / s14 18 / s15 3 / s17 9). 75 → 45 전이는 `STATUS.md` 01:50("strict-H 75!")과 02:35("최종 티어 V438 E36 H45")에 남아 있어 **추적은 가능**하다. 다만 D17 줄에는 "이후 융합 2차로 s12/s16의 H가 V/none으로 재분류돼 최종 45"라는 표시가 없어, D17 → 매니페스트로 직행하는 독자는 30프레임 차이에 걸린다. → **append 각주 1줄 권고** |
| **D20** | ① C2 ground_z 0.11 m 이동 ② 트윈 배제 183쌍 ③ "**배제 51쌍 회복**" | 매니페스트 페어링 재계산 | **부분 CONFIRMED / ③ 과장.** ① sceneC2 실측 `|Δground_z|` = **0.1137 m** ✓ ② 792쌍 중 **정확히 183쌍**이 불일치, 그리고 **전부 `ground_z` 단독 불일치**(d/h_rel/yaw/pitch/roll/hfov는 183쌍 모두 일치) — D20의 원인 진단까지 확증 ✓ ③ **틀림.** 51은 v1 test 트윈 분석의 배제 수(117 사용 + 51 배제 = 168, `MORNING_REPORT.md:150`)이고, 0.15 m 허용오차로 **회복되는 건 36쌍뿐**이다(나머지 15쌍은 scene07의 3.57/4.02 m 데이텀 변경이라 영구 배제). "51쌍 회복"은 **29 % 과장**. 후속 문서(`METRICS.md` N.1)는 옳게 쓴다 |
| **D24** | 병합 frame_id 충돌 **192건** · E2 seed **20260821** | 4개 부분 매니페스트 재병합 | **CONFIRMED (정확히).** 접미사 없이 병합 시 충돌 **192건**, 전부 `boost_h ↔ boost_e`, 씬 s09/s14/s15/s17 각 48건 ✓. `manifest_boost_e2.json` meta.seed = **20260821** ✓ (h/e는 20260820, main은 20260819) |
| **D28** | ρ 0.963 → 0.848 · FA÷prior 0.377 → 0.234 · C2 RGB FA 0.875 → 0.069 | `diag_v1_numbers.json`, `diag_v2_numbers.json` | **CONFIRMED (4/4).** v2 ρ(RGB) 3시드 평균 = **0.84788** (0.7999/0.9145/0.8292) ✓ · v1 ρ = **+0.9626** (`DIAG_V1.md` §표) ✓ · FA÷prior 3b = 0.13627/0.58281 = **0.2338** ✓ (3a 0.122 ✓, band2 0.062 ✓) · C2 RGB frame FA v1 **0.875** → v2 **0.06944** ✓, 셀발화 점유 **47.8 % → 0.47 %** ✓, Depth C2 점유 **76.07 %** ✓ |

**보너스 대조 2건** (추첨 밖, 저비용이라 겸사):
- **D26** `split_v2_full sha 9bc44d4efbe6e83e` → sha256[:16] **일치** ✓
- **`METRICS.md` N.1 트윈 층화** EXACT 312 / TOL 54 / EXCL 42 (test 408쌍), 티어 분해
  V 132+33+15 / E 45+0+0 / H **96+0+0** → 매니페스트에서 **전부 정확히 재현** ✓.
  "TOL 층에 H·E가 0쌍이라 항등"이라는 B5/D27 방어의 기하학적 전제가 독립 확인됐다.

**대조 성적: 5건 중 CONFIRMED 3 · SUPERSEDED 1(D17) · 과장 1(D20-③).**
데이터를 건드리는 오류는 0건. 두 건 다 **DECISIONS.md 산문의 표기 문제**이고 후속 원장은 옳다.

---

## 5. 권고 (비용 오름차순, 전부 동결 전 처리 가능)

| # | 조치 | 비용 | 근거 |
|---|---|---|---|
| 1 | `.gitignore`에 `!experiments/*/runs/**/*.md`, `*.json`, `*.csv` 예외 3줄 추가 → `SEED_TABLE.md` 외 76개 원장 커밋 | **10분 / 9.8 MB** | §2.1. 헤드라인 원장이 공개 저장소에 없는 상태로 논문을 낼 수 없다 |
| 2 | `SPLIT_PROPOSAL_v2_full.md`에 append 절 — 5범주 전열 표(위 §1.4-a) + `frames` 열 명칭 정정 | 10분 | §1.4-a. PS §12.3-⑥이 예고한 함정에 우리 문서가 빠져 있다 |
| 3 | `DECISIONS.md` D17·D20에 각주 2줄(초과분·최종치 표기) | 5분 | §4 |
| 4 | 루트에 `requirements-unet.txt` / `requirements-yolo.txt` + README에 "환경 2개" 명시 | 20분 | §2.3 |
| 5 | `PROTOCOL_SHOOT.md` §⑤ V1 셀 규약으로 교체 + 섹터 각도표 + `infer_photo` 교정 실행줄 + `sites.csv` 예시 재작성 | **1시간** | §3.1–3.4. **파일럿 촬영의 전제조건 — 이게 없으면 ④는 착수 불가** |
| 6 | `README_CODE.md` infer_photo 예시 ckpt 경로 교정(`dayrun_0820/runs/v2/...`) | 5분 | §3.3, 실행으로 확인 |
| 7 | §12.3-④ 문안을 "τ_edge는 (0, 0.44)에서 무영향 — 이 코퍼스에서 립 가시성은 이진"으로 교체 | 10분 | §1.5 |
| 8 | 매니페스트 경로를 리포 상대경로로 바꾸는 `relocate_manifest.py`(또는 `--dataset-root` 플래그) | 30분 | §2.2 |
| 9 | 실측 정본 체크포인트 결재(권고: s42 고정 + 3시드 병기) | 결재 | §3.4-1 |
| 10 | `METRICS.md` §2.4 τ_edge 0.02 → 0.05 표기 정정(append) | 5분 | §1.4-b |

### V2S 트랙에 대한 R3 경고 1건

§12.6 절차 1)의 불변 게이트는 "티어 5범주 카운트 V1 동일 + any-cell 양성 일치 + 폴딩 법칙"이다.
`gridspec_v1.json`의 `nesting_note`가 이미 증명하듯 **none_in_fov는 그리드 *커버리지*에만 의존**하므로
(v0·v1 매니페스트에서 none_in_fov가 261로 동일한 것이 실증), 섹터 이등분처럼 커버리지를 바꾸지 않는
세분화에서는 5범주 카운트가 **자동으로 통과한다** — 즉 이 게이트는 라벨러 버그를 잡는 힘이 거의 없다.
**진짜 판별력은 폴딩 법칙(섹터 쌍 OR = V1 셀) 위반 0에 있다.** 게이트 통과를 "검증됨"으로 읽지 말고,
폴딩 법칙 위반 카운트를 별도 숫자로 보고할 것.

---

## 부록 — 재현 명령 (이 감사의 모든 숫자)

```python
import json, collections
M = json.load(open('experiments/dayrun_0820/dataset_manifest_v2_full.json'))
collections.Counter(f['tier'] for f in M['frames'])
# -> {'off':1416,'V':693,'none_in_fov':378,'H':243,'E':72,'H_weak':30}
```

티어 규칙 재파생·트윈 층화·edge_ratio 분포·frame_id 충돌 재현 스크립트는 본문 각 절에
입력 파일과 판정 기준을 명시해 두었으므로 그대로 재실행 가능하다(외부 의존 없음, 표준 라이브러리만).
