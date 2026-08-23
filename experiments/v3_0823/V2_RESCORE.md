# V2_RESCORE — 교정 GT(정본 B) 기준 v2 체크포인트 9개 전수 재채점 · 공표표 대비 델타

*P-2 후속 (DZ §12-1 / ACCOUNTING §2-1). 측정일 2026-08-23. 이 문서는 **공표표(구 GT) ↔ 교정 GT의
델타 전용 리포트**이며, A/B 표가 아니다. A/B는 앞으로 **양측 공히 교정 GT**로만 낸다(§2-1).*

---

## 승용 요약 (5문장)

1. **v2 체크포인트 9개(rgb·depth·b2 × s42/43/44)를 교정 GT(`dataset_manifest_v2corr.json`)로
   전수 재채점했고, 예측 확률은 9개 런 전부에서 공표 덤프와 `max|Δp| = 0.000e+00`으로 비트 동일**
   — 바뀐 것은 정답지뿐이고 픽셀·모델·τ는 하나도 안 움직였다는 뜻이다.
2. **H 행은 9/9 런에서 완전 동일**(frame_recall_H·cell_recall_H·twin ΔH 전부) — test H 96프레임이
   불변이라는 G7 예측이 실측으로 확인됐고, **논문 헤드라인 H 주장은 한 자리도 안 움직인다.**
3. **움직이는 것은 V 계열과 셀 계열뿐이고, 원인은 전부 "분모가 커진 것"이다** — scene07의
   boost_e/e2 온팔 **42프레임(V 39 · H_weak 3)** 이 `none_in_fov`에서 양성으로 들어오면서 recall 분모가
   327 → **369**로 늘고, 양성 셀이 2,691 → 2,856으로 늘었다. **구 분모 327 위에서 교정 GT로 다시 재면
   9개 런 × 전 tier가 공표치와 소수 4자리까지 동일**하다(§1.3).
4. **시드 σ를 넘는 이동은 depth 2건뿐**(cell_precision +0.051 > σ 0.031, H_weak recall +0.333 — 후자는
   n=9 · σ=0 인 퇴화 행). V recall은 rgb −0.037 · depth −0.017 · b2 +0.006으로 **전부 σ 이내**이고,
   FA·cell_fpr_off·E·H는 정의상 **정확히 0** 이동이다.
5. **"FA를 맞추면 전 지점에서 Depth ≥ RGB"는 살아남는다 — 그것도 수치가 완전히 동일하게**
   (.359 / .20 / .10 / .05 네 지점 모두 H가 소수 3자리까지 불변; off팔과 H팔 어느 쪽도 교정 대상이
   아니기 때문). 다만 **같은 표의 V 열은 움직인다**(rgb .809→.784 등).

> **분모 정정 (읽기 전 필독).** `ACCOUNTING.md` §4.2가 test-core를 `none_in_fov 81→36 · 분모 327→372`로
> 적었으나 **이는 산술 오류**다(219+45+96+9+36 = 405 ≠ 408). 원장
> `dataset_manifest_v2corr.json` 실측과 `G7_RELABEL.md:240` 표가 일치하는 정답은
> **`none_in_fov 81→39` · 분모 `327→369`** 이다. 본 문서는 전부 **369**를 쓴다.
> 재검산: `code/rescore_tables.py` → `eval_v2corr/rescore_tables.json` 의 `census` 블록.

---

## 0. 프로비넌스 · 재생성 명령

**입력 (읽기 전용)**

| 역할 | 경로 |
|---|---|
| 교정 GT 매니페스트 (정본 B) | `experiments/v3_0823/dataset_manifest_v2corr.json` |
| 구 GT 매니페스트 (공표 기준) | `experiments/dayrun_0820/dataset_manifest_v2_full.json` |
| split (양측 공통 · 변경 없음) | `experiments/dayrun_0820/split_v2_full.json` |
| 체크포인트 9개 | `experiments/dayrun_0820/runs/v2/{rgb,depth,b2}_s{42,43,44}/best.pt` |
| 공표 표 | `experiments/dayrun_0820/runs/v2/SEED_TABLE.md` |
| 공표 덤프 | `.../runs/v2/<run>/eval_test/{metrics.json,per_frame.csv}` · `.../twin/twin_pairs.csv` |
| 씬 분류 (C/D) | `experiments/v3_0823/CUE_COVERAGE.md` §0-6 · §2.1 · 원장 `code/hazgate.json` |

**출력 (신규 · 전부 `experiments/v3_0823/` 하위)**

| 산출 | 경로 |
|---|---|
| 재채점 결과 9세트 | `eval_v2corr/<run>/{metrics.json,per_frame.csv,per_frame_{on,off}.csv,METRICS_SECTION.md,DONE}` |
| 트윈 재분석 9세트 | `eval_v2corr/<run>/twin/{twin_pairs.csv,twin_analysis.md}` |
| 집계 원장 | `eval_v2corr/rescore_tables.json` |
| 로그 · 마커 | `eval_v2corr/logs/{rescore.log,twin.log,<run>.log}` · `eval_v2corr/{ALL_DONE,TWIN_DONE}` |
| 드라이버 | `code/rescore_v2corr.sh` · `code/rescore_twin.sh` · `code/rescore_tables.py` |

**재생성 (전체)**

```bash
R=/home/vislab/Desktop/work_sy/Practice_NegObs
# ① GPU 재채점 9런 — tmux 세션 v2rescore 안에서, 매 런 flock -o /tmp/negobs_gpu.lock 홀드
tmux new-session -d -s v2rescore
tmux send-keys -t v2rescore "bash $R/experiments/v3_0823/code/rescore_v2corr.sh" Enter
# ② 트윈 재분석 (CPU, GPU 락 불필요)
bash $R/experiments/v3_0823/code/rescore_twin.sh
# ③ 집계 · 게이트 · 전 표
PYTHONNOUSERSITE=1 CUDA_VISIBLE_DEVICES= /home/vislab/miniconda3/envs/env_seg/bin/python \
  $R/experiments/v3_0823/code/rescore_tables.py
```

**공표 호출과의 차이는 정확히 두 줄.** 나머지(`--subset test --tau-op 0.5 --tau-sweep 0.3,0.5,0.7
--n-boot 10000 --grid gridspec_v1.json`, rgb/depth는 `eval_polar.py` · b2는 `b2_polar/eval_b2_polar.py
--route auto`)는 `mainrun_0819/code/run_queue_v2.sh` 그대로다.

| # | 공표 (`run_queue_v2.sh`) | 본 재채점 |
|---|---|---|
| 1 | `--manifest .../dataset_manifest_v2_full.json` | `--manifest .../v3_0823/dataset_manifest_v2corr.json` |
| 2 | `--tau-star auto` (val에서 재적합) | `--tau-star <공표 고정값>` — **재적합 금지**(DZ 지시). 고정값: rgb .63/.71/.31 · depth .36/.21/.60 · b2 .45/.45/.45 (출처 = 각 런의 공표 `eval_test/metrics.json:tau_star`) |

τ_op = **0.5 동결**. b2 역시 공표 eval config의 τ_op 0.5 · τ\* 0.45를 그대로 물려받았다(재적합 없음).
런타임: GPU 재채점 9런 **2분 33초**(14:48:37→14:51:10, 런당 11–21 s), 트윈 재분석 9런 CPU **≈40 s**.

---

## 0.1 무결성 게이트 — 4건 전항 통과

| 게이트 | 기대 | 실측 | 판정 |
|---|---|---|---|
| G-1 픽셀 불변 → 확률 불변 | 공표 `per_frame.csv`의 `p_*`와 재채점 `p_*`가 동일 | **9/9 런 `max|Δp| = 0.000e+00`** (비트 동일) | ✅ |
| G-2 frame_id 집합 동일 | 816 프레임 id 완전 일치 | 9/9 True | ✅ |
| G-3 **H 행 불변** | `frame_recall_H`·`cell_recall_H` 공표와 동일 | **9/9 완전 동일** (아래 표) | ✅ |
| G-4 off팔 불변 | `frame_fa_off`·`cell_fpr_off` 공표와 동일 | **9/9 Δ = 0.0000** | ✅ |

**G-3 상세 (요구된 STOP 조건 검사 — 불일치 0건)**

| run | frame_recall_H 공표 → 교정 | cell_recall_H 공표 → 교정 | twin ΔH 공표 → 교정 |
|---|---|---|---|
| rgb_s42 | 0.5938 → 0.5938 | 동일 | 0.170 → 0.170 |
| rgb_s43 | 0.8750 → 0.8750 | 동일 | 0.359 → 0.359 |
| rgb_s44 | 0.5938 → 0.5938 | 동일 | 0.327 → 0.327 |
| depth_s42 | 0.4062 → 0.4062 | 동일 | 0.413 → 0.413 |
| depth_s43 | 0.4688 → 0.4688 | 동일 | 0.440 → 0.440 |
| depth_s44 | 0.4375 → 0.4375 | 동일 | 0.367 → 0.367 |
| b2_s42 | 0.0833 → 0.0833 | 동일 | 0.073 → 0.073 |
| b2_s43 | 0.3958 → 0.3958 | 동일 | 0.069 → 0.069 |
| b2_s44 | 0.2083 → 0.2083 | 동일 | 0.187 → 0.187 |

> H 행 불일치가 하나라도 났으면 즉시 중단·보고하라는 지시였다. **불일치 0건**이며, 이는 G7 수리가
> test H 96프레임(scene14 60 + scene15 36)을 건드리지 않았다는 `G7_RELABEL.md:248`의 주장을
> 모델 출력 층에서 독립 확인한 것이다.

---

## 1. 교정 GT 헤드라인 표 (τ_op = 0.5)

### 1.1 분모 회계 — 두 규약을 같은 표에 인쇄 (ACCOUNTING §2-4 준수)

**평가 정의는 하나도 바뀌지 않았다.** recall 분모 이동은 **마스킹이 아니라 GT tier 재배정**의 결과다
(교정 전 `none_in_fov`였던 프레임이 양성 칸을 얻어 hazard 모집단으로 들어왔다).

| 항목 | 구 GT (공표) | 교정 GT (정본 B) | Δ |
|---|---|---|---|
| 총 프레임 / on / off | 816 / 408 / 408 | 816 / 408 / 408 | 0 / 0 / **0** |
| V | 180 | **219** | **+39** |
| E | 45 | 45 | 0 |
| H (strict) | **96** | **96** | **0** |
| H_weak | 6 | **9** | **+3** |
| none_in_fov | 81 | **39** | **−42** |
| **헤드라인 recall 분모** (`n_hazard_frames`) | **327** | **369** | **+42** |
| 조건화 탈락 공개 의무 (§3.1) | 81/408 = **19.9 %** | 39/408 = **9.6 %** | −10.3 pp |
| 양성 칸 수 (`n_pos_cells`, 816프레임) | 2,691 | **2,856** | **+165** |

**들어온 42프레임의 정체 — 전수 추적** (`rescore_tables.json:census.entering_frames`)

| 라운드 | 씬 | n | 교정 후 tier | 교정 전 tier |
|---|---|---|---|---|
| `260820_boost_e_on` | scene07 | 18 | V 18 | `none_in_fov` |
| `260820_boost_e2_on` | scene07 | 24 | V 21 · **H_weak 3** | `none_in_fov` |
| **합** | — | **42** | V 39 · H_weak 3 | — |

* **나가는 프레임 0건** — 구 분모 327은 새 분모 369의 **진부분집합**이다(검산:
  `census.old_haz_subset_of_new = true`, `leaving_frames = []`). 델타 해석이 순수 "추가"로 닫힌다.
* **tier 이동은 `none_in_fov → V` 39 · `none_in_fov → H_weak` 3 두 종류뿐**. V→H, H→V 같은
  기존 tier 간 재배치는 test-core에 **0건**이다(scene12의 H→V 48장은 **train** 소속).
* `E 45 불변`은 **정본 B**의 성질이다. 변형 A(`dataset_manifest_v2corr_roundown.json`)에서는
  E 45→48 · H_weak 9→6이 되지만, 본 재채점은 **정본 B 단독**이다.
* **참고 — 코퍼스 2,832프레임 전체**(재채점 범위 밖이나 인용이 자주 붙는 수):
  V 693→**801** · E 72 불변 · H 243→**195**(전량 scene12, **train**) · H_weak 30→**33** ·
  none 378→**315** · off 1416 불변 ⇒ **코퍼스 hazard 분모 1038 → 1101**.
  `ACCOUNTING.md` §4.2의 코퍼스 표와 일치한다(실측 재검산 완료).

### 1.2 헤드라인 — 교정 GT · 새 분모(369) 기준 · 3시드 `mean ± range/2`

| model | n seeds | cell_f1 | frame_det_rate | recall V | recall E | recall H | recall **H_weak** | frame_fa_off (off) | cell_fpr_off |
|---|---|---|---|---|---|---|---|---|---|
| rgb | 3 | 0.456 ± 0.117 | 0.717 ± 0.199 | 0.760 ± 0.203 | 0.556 ± 0.378 | **0.688 ± 0.141** | 0.815 ± 0.222 | **0.359 ± 0.127** | 0.047 ± 0.016 |
| depth | 3 | 0.704 ± 0.030 | 0.729 ± 0.016 | 0.900 ± 0.041 | 0.600 ± 0.000 | **0.438 ± 0.031** | 0.333 ± 0.000 | **0.042 ± 0.029** | 0.009 ± 0.008 |
| b2 | 3 | 0.367 ± 0.087 | 0.526 ± 0.149 | 0.735 ± 0.119 | 0.178 ± 0.267 | **0.229 ± 0.156** | 0.333 ± 0.500 | **0.238 ± 0.143** | 0.035 ± 0.029 |

*분모*: V 219 · E 45 · H 96 · H_weak 9 · det 369 · off 408.
*굵은 칸*은 공표치와 **완전 동일**한 열(H · FA · cell_fpr_off).
*H_weak 열은 공표표에 없던 열이다* — 분모 9(≤10)이므로 **본문 인용 금지 · 회계용**으로만 둔다.
`frame_det_rate` 분모에는 H_weak 9프레임이 포함된다(eval_polar의 `haz = on & pos.any(1)` 정의 그대로).

**보조 참고: cell_recall / cell_precision** (셀 계열은 양성 칸 2,691→2,856의 직접 영향을 받는다)

| model | cell_recall 공표 → 교정 | cell_precision 공표 → 교정 |
|---|---|---|
| rgb | 0.385 ± 0.125 → **0.381 ± 0.133** | 0.566 ± 0.021 → **0.592 ± 0.039** |
| depth | 0.652 ± 0.031 → **0.659 ± 0.029** | 0.705 ± 0.031 → **0.756 ± 0.031** |
| b2 | 0.276 ± 0.121 → **0.292 ± 0.131** | 0.527 ± 0.108 → **0.590 ± 0.115** |

### 1.3 같은 표, **구 분모(327) 규약** — 결정적 대조

구 hazard 327프레임에만 한정하고 **라벨은 교정본을 쓴** 값이다(= "분모 성장분을 뺀" 교정 GT).

| run | det | V | E | H | H_weak | ← 공표치와 대조 |
|---|---|---|---|---|---|---|
| rgb_s42 | 0.731 | 0.828 | 0.600 | 0.594 | 1.000 | **전 칸 소수 4자리까지 공표와 동일** |
| rgb_s43 | 0.908 | 0.944 | 0.911 | 0.875 | 0.333 | 〃 |
| rgb_s44 | 0.550 | 0.617 | 0.156 | 0.594 | 0.833 | 〃 |
| depth_s42 | 0.734 | 0.967 | 0.600 | 0.406 | 0.000 | 〃 |
| depth_s43 | 0.706 | 0.883 | 0.600 | 0.469 | 0.000 | 〃 |
| depth_s44 | 0.706 | 0.900 | 0.600 | 0.438 | 0.000 | 〃 |
| b2_s42 | 0.391 | 0.667 | 0.000 | 0.083 | 0.000 | 〃 |
| b2_s43 | 0.688 | 0.872 | 0.533 | 0.396 | 1.000 | 〃 |
| b2_s44 | 0.419 | 0.650 | 0.000 | 0.208 | 0.000 | 〃 |

> **이것이 이 리포트의 핵심 회계 사실이다.** 구 327프레임 위에서는 교정 GT가 공표치를 **완벽 재현**한다
> ⇒ G7 수리는 **기존 프레임의 라벨을 하나도 바꾸지 않았고**, 프레임 recall의 모든 델타는
> **42프레임 유입(분모 성장) 단 하나의 기전**으로 100 % 설명된다. 셀 계열(f1/recall/precision)만은
> 816프레임 전체 위에서 계산되므로 구 분모 규약이 없고, 이쪽은 양성 칸 +165가 직접 원인이다.

---

## 2. 델타 표 — 공표 SEED_TABLE(구 GT) 대비

기준: `experiments/dayrun_0820/runs/v2/SEED_TABLE.md` §1(구 GT, τ_op 0.5).
Δ = 교정 − 공표(3시드 평균). **σ = 교정 GT 3시드 표본표준편차(ddof = 1)** — DZ §7.2대로 σ는
**런 재현성의 잣대**이지 씬-모집단 신뢰구간이 아니다. `±`는 공표표 관례를 따라 range/2다.

### 2.1 모델별 델타 · σ 초과 플래그

| model | metric | 공표 | 교정 | **Δ** | **σ(교정)** | \|Δ\| > σ |
|---|---|---|---|---|---|---|
| rgb | cell_f1 | 0.4500 | 0.4560 | +0.0059 | 0.1200 | — |
| rgb | cell_recall | 0.3847 | 0.3812 | −0.0036 | 0.1381 | — |
| rgb | cell_precision | 0.5658 | 0.5922 | +0.0263 | 0.0416 | — |
| rgb | frame_det_rate | 0.7299 | 0.7173 | −0.0126 | 0.1992 | — |
| rgb | **frame_recall_V** | 0.7963 | 0.7595 | **−0.0368** | 0.2037 | — |
| rgb | frame_recall_E | 0.5556 | 0.5556 | **0.0000** | 0.3797 | — |
| rgb | **frame_recall_H** | 0.6875 | 0.6875 | **0.0000** | 0.1624 | — |
| rgb | frame_recall_H_weak | 0.7222 | 0.8148 | +0.0926 | 0.2313 | — |
| rgb | frame_fa_off | 0.3587 | 0.3587 | **0.0000** | 0.1282 | — |
| rgb | cell_fpr_off | 0.0467 | 0.0467 | **0.0000** | 0.0169 | — |
| depth | cell_f1 | 0.6772 | 0.7038 | +0.0265 | 0.0302 | — (0.88 σ) |
| depth | cell_recall | 0.6518 | 0.6586 | +0.0068 | 0.0312 | — |
| depth | **cell_precision** | 0.7049 | 0.7557 | **+0.0508** | 0.0307 | **★ 1.65 σ** |
| depth | frame_det_rate | 0.7156 | 0.7290 | +0.0134 | 0.0169 | — |
| depth | **frame_recall_V** | 0.9167 | 0.8995 | **−0.0171** | 0.0419 | — |
| depth | frame_recall_E | 0.6000 | 0.6000 | **0.0000** | 0.0000 | — |
| depth | **frame_recall_H** | 0.4375 | 0.4375 | **0.0000** | 0.0312 | — |
| depth | **frame_recall_H_weak** | 0.0000 | 0.3333 | **+0.3333** | 0.0000 | **★ (퇴화 — 아래 주)** |
| depth | frame_fa_off | 0.0417 | 0.0417 | **0.0000** | 0.0306 | — |
| depth | cell_fpr_off | 0.0089 | 0.0089 | **0.0000** | 0.0088 | — |
| b2 | cell_f1 | 0.3397 | 0.3670 | +0.0273 | 0.0899 | — |
| b2 | cell_recall | 0.2759 | 0.2924 | +0.0165 | 0.1434 | — |
| b2 | cell_precision | 0.5273 | 0.5904 | +0.0631 | 0.1149 | — |
| b2 | frame_det_rate | 0.4995 | 0.5257 | +0.0263 | 0.1669 | — |
| b2 | **frame_recall_V** | 0.7296 | 0.7352 | **+0.0055** | 0.1310 | — |
| b2 | frame_recall_E | 0.1778 | 0.1778 | **0.0000** | 0.3079 | — |
| b2 | **frame_recall_H** | 0.2292 | 0.2292 | **0.0000** | 0.1573 | — |
| b2 | frame_recall_H_weak | 0.3333 | 0.3333 | **0.0000** | 0.5774 | — |
| b2 | frame_fa_off | 0.2377 | 0.2377 | **0.0000** | 0.1453 | — |
| b2 | cell_fpr_off | 0.0347 | 0.0347 | **0.0000** | 0.0302 | — |

**σ를 넘는 공표 주장은 2건, 둘 다 depth.**

1. **depth `cell_precision` 0.705 → 0.756 (+0.051, 1.65 σ).** 유일한 실질적 σ 초과다. 기전은
   명확하다 — scene07 boost 프레임에 양성 칸 165개가 새로 생기면서, depth가 이미 켜고 있던
   칸 일부가 **FP → TP로 재분류**됐다. 즉 모델이 좋아진 게 아니라 **정답지가 모델 쪽으로 온 것**이며,
   "구 GT가 그 칸들을 음성이라 우겼다"는 G7 결함의 직접 흔적이다. rgb(+0.026, 0.63 σ)와
   b2(+0.063, 0.55 σ)도 같은 방향이지만 시드 산포에 묻힌다.
2. **depth `frame_recall_H_weak` 0.000 → 0.333.** σ = 0인 건 3시드가 전부 같은 값이라서지
   정밀해서가 아니다. **분모 9**(사전등록 하한 10 미달)이고 공표표에 없던 열이다 —
   **인용 금지**. 실체는 "새로 들어온 scene07 H_weak 3장 중 1장을 depth가 잡는다"뿐이다.

**정확히 0인 칸들(정의상 필연).** `frame_recall_H` · `frame_recall_E` · `frame_fa_off` ·
`cell_fpr_off`는 9/9 런에서 Δ = 0.0000이다. H·E 프레임과 off팔 408프레임이 교정 대상이 아니었고,
확률이 비트 동일하기 때문이다(G-1). **이 네 열은 "재채점해도 안 바뀐다"가 아니라
"재채점 결과 안 바뀌는 것이 확인됐다"로 써야 한다.**

### 2.2 요구된 기전 검증 2건

| 검증 항목 | 기대 | 실측 | 판정 |
|---|---|---|---|
| V recall이 움직이는 이유 = s07 e/e2의 신규 양성 39프레임이 분모에 진입 | +39 | **+39 V (+3 H_weak, 합 42), 전량 scene07 · boost_e 18 / boost_e2 24, 이탈 0** | ✅ 일치 |
| H 행은 공표와 **동일**해야 함 (test H 96 불변) | 완전 동일 | **9/9 런 frame·cell·twin 전부 동일** | ✅ 일치 · **STOP 조건 미발동** |

**V가 내려간 이유의 산술** — 새 39프레임은 "그리드 안 낙차가 있는데 구 GT가 놓쳤던" 프레임이므로
모델이 잘 못 맞힌다. rgb_s42 실측: 구 180프레임 **149/180 = 0.8278** → 신규 39프레임에서
**21/39 = 0.538** 검출 → 합쳐서 **170/219 = 0.7763**. **분자도 늘었지만 분모가 더 빨리 늘었다.**
depth는 이미 V를 잘 잡아 낙폭이 작고(−0.017), b2는 신규 프레임 검출률이 기존과 비슷해 사실상
안 움직인다(+0.006).

### 2.3 정직 기록 — σ 기준의 한계

rgb의 σ는 V 0.204 · det 0.199 · E 0.380으로 **어떤 델타든 삼켜버릴 만큼 크다**(3시드 · s43가 홀로 튐).
따라서 "rgb에서 σ 초과 없음"은 **"움직이지 않았다"가 아니라 "3시드로는 판정 불가"**로 읽어야 한다.
판정력이 있는 건 σ가 작은 depth(0.017–0.042)뿐이고, 실제로 σ 초과도 depth에서만 났다.

---

## 3. FA-정합 재실행 — 교정 GT 위 4지점 {.359, .20, .10, .05}

**방법**: `weekend_0823/rt_response/F1_FA_MATCHED.md` §2 절차를 그대로 복제 —
off팔 프레임별 max-prob의 경험 순서통계에서 τ를 뽑아 목표 FA 바로 아래에 붙이고(exact 규칙,
해상도 1/408 = 0.0025), 그 τ에서 H/E/V frame recall을 읽는다. 검증용으로 R1의 0.01 격자 규칙(grid)도
같이 계산했다. **GPU 재실행 없음** — §0의 재채점이 만든 `eval_v2corr/<run>/per_frame.csv`
확률 덤프 위의 CPU 재계산이다(F1 원본은 공표 덤프를 읽지만, 확률이 비트 동일하므로 입력이 같다).

### 3.1 답: **살아남는다. 그것도 수치가 완전히 동일하게.**

**3시드 평균 H frame recall @ 정합 off팔 FA** (± range/2 · exact 규칙)

| 정합 FA | 달성 FA (R/D/B) | RGB H 공표→교정 | Depth H 공표→교정 | B2 H 공표→교정 | Δ(Depth−RGB) 교정 |
|---|---|---|---|---|---|
| 0.359 | .358 / .353 / .358 | 0.729 → **0.729** ±0.135 | 0.781 → **0.781** ±0.078 | 0.399 → **0.399** ±0.078 | **+0.052** |
| 0.200 | .199 / .199 / .199 | 0.483 → **0.483** ±0.172 | 0.562 → **0.562** ±0.031 | 0.198 → **0.198** ±0.141 | **+0.080** |
| 0.100 | .098 / .096 / .098 | 0.326 → **0.326** ±0.229 | 0.510 → **0.510** ±0.078 | 0.097 → **0.097** ±0.099 | **+0.184** |
| 0.050 | .049 / .044 / .049 | 0.243 → **0.243** ±0.208 | 0.479 → **0.479** ±0.094 | 0.031 → **0.031** ±0.036 | **+0.236** |

격자 규칙(R1 공표 규칙)도 동일: .359 = 0.719/0.740/0.385 · .20 = 0.476/0.552/0.198 ·
.10 = 0.319/0.510/0.097 · .05 = 0.236/0.479/0.031 — 교정 전후 소수 3자리까지 불변.

**왜 필연인가.** τ는 **off팔 408프레임에서만** 뽑히고(교정 무관), 읽는 값은 **H 96프레임의 recall**이다
(교정 무관). FA-정합 표는 구조적으로 G7 결함면과 **교집합이 없다**. 즉 "Depth ≥ RGB at every matched FA"는
교정 GT에서도 **같은 숫자로** 성립하며, `SEED_TABLE.md:9`의 읽는 법 배너는 **수정 불필요**다.

### 3.2 같은 표의 V·E 열 — 여기는 움직인다

| 정합 FA | RGB V 공표→교정 | Depth V 공표→교정 | B2 V 공표→교정 | E (R/D/B) |
|---|---|---|---|---|
| 0.359 | 0.809 → **0.784** | 0.994 → **0.995** | 0.800 → **0.823** | 0.570 / 0.733 / 0.193 (전부 불변) |
| 0.200 | 0.669 → **0.632** | 0.983 → **0.973** | 0.746 → **0.760** | 0.296 / 0.600 / 0.126 (불변) |
| 0.100 | 0.530 → **0.496** | 0.956 → **0.941** | 0.646 → **0.647** | 0.081 / 0.600 / 0.089 (불변) |
| 0.050 | 0.443 → **0.399** | 0.939 → **0.927** | 0.552 → **0.556** | 0.015 / 0.600 / 0.022 (불변) |

`F1_FA_MATCHED.md` §4를 인용할 때는 **V 열만 교체**하면 된다. **Depth V ≥ RGB V는 네 지점 모두에서
교정 후에도 유지**(격차 오히려 확대: +0.185→+0.211 @.359, +0.496→+0.528 @.05).

---

## 4. off팔 FA 비균질 분해 — v2 최초의 FA_C/FA_D 성격 분해

**근거**: ACCOUNTING §4.1 — v2 off팔은 단일 세대가 아니다. 단서 빌더가 `hazard_*` 분기에 묶이지 않은
**8씬은 위험만 사라지고 단서가 그대로 서 있고(≈C팔)**, **25씬은 단서가 위험과 함께 소멸한다(≈D팔)**.
분류 원장은 `CUE_COVERAGE.md` §0-6 · §2.1(마스터 표 "C팔 결속" 열), 기계 판정은 `code/hazgate.json`.

### 4.1 test-core 7씬 분류 (재현: `rescore_tables.py:classify_scenes`)

**1차(정본) 규칙** = CUE_COVERAGE의 "C팔 결속" 열 = *배선된 `cue_*` 키 중 hazard 게이트에 걸린 것이
하나도 없어야 C*. 이 규칙을 33씬 라이브러리에 돌리면 C팔 8씬
(`scene01 scene04 scene09 sceneC2 sceneN1 sceneN3 sceneN4 sceneN5`)이 정확히 재현된다 ✅.

| 씬 | off 프레임 | **1차 분류** | 2차(기본값 ON 단서만) | 판정 근거 |
|---|---|---|---|---|
| sceneC2 | 24 | **C-like** | C | railing·tactile·nosing·dressing 전부 `자유` |
| sceneN3 | 24 | **C-like** | C | material_break·dressing 전부 `자유` |
| scene05 | 72 | D-like | D | `material_break` = `hz?`(LipCurb만 게이트) |
| scene07 | 72 | D-like | D | railing·tactile·nosing·**dressing 전부 HZ** — 가장 순수한 D |
| scene14 | 72 | D-like | **C** | railing·tactile·nosing이 HZ이나 **전부 기본값 off** |
| scene15 | 72 | D-like | **C** | railing만 HZ이고 기본값 off · dressing은 자유 |
| scene18 | 72 | D-like | **C** | railing·tactile·nosing HZ이나 전부 기본값 off |
| — | **C 48 / D 360** | | (C 264 / D 144) | |

> **분류가 두 개인 이유를 감추지 않는다.** 1차 규칙은 "배선된 키 중 하나라도 HZ면 D"이므로
> **기본값이 off라 실제로는 렌더에 등장하지도 않는 단서** 때문에 s14·s15·s18을 D로 보낸다.
> 실제 렌더에서 hazard=False가 지우는 단서만 세면(2차 규칙) 이 셋은 C가 된다. 1차를 정본으로 쓰되
> **두 값을 병기**한다.

### 4.2 프레임 FA(off) @ τ 0.5 — C-like / D-like 분리 (교정 GT 덤프 기준; off팔은 공표와 동일)

| model | **FA_C-like** (1차, n=48) | **FA_D-like** (1차, n=360) | C−D | FA_C (2차, n=264) | FA_D (2차, n=144) | C−D |
|---|---|---|---|---|---|---|
| rgb | **0.438** ±0.125 | **0.348** ±0.144 | **+0.089** | 0.439 | 0.211 | +0.229 |
| depth | **0.167** ±0.094 | **0.025** ±0.025 | **+0.142** | 0.057 | 0.014 | +0.043 |
| b2 | **0.451** ±0.177 | **0.209** ±0.151 | **+0.242** | 0.202 | 0.303 | **−0.101** |

시드별: rgb FA_C [.604 .354 .354] / FA_D [.344 .494 .206] · depth FA_C [.250 .063 .188] /
FA_D [.025 .000 .050] · b2 FA_C [.271 .625 .458] / FA_D [.203 .364 .061].

### 4.3 씬별 원자료 — 그리고 왜 이 결과를 방향 증거로만 써야 하는가

프레임 FA(off) @0.5, 씬별 (n_off: s05/07/14/15/18 = 72씩, C2/N3 = 24씩)

| run | scene05 | scene07 | scene14 | scene15 | scene18 | **sceneC2** | **sceneN3** |
|---|---|---|---|---|---|---|---|
| rgb_s42 | 0.236 | 0.000 | 0.181 | 0.889 | 0.417 | 0.208 | **1.000** |
| rgb_s43 | 0.778 | 0.097 | 0.542 | 0.500 | 0.556 | 0.000 | **0.708** |
| rgb_s44 | 0.153 | 0.000 | 0.083 | 0.708 | 0.083 | 0.000 | **0.708** |
| depth_s42 | 0.042 | 0.000 | 0.000 | 0.083 | 0.000 | 0.375 | 0.125 |
| depth_s43 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.125 | 0.000 |
| depth_s44 | 0.042 | 0.000 | 0.000 | 0.208 | 0.000 | 0.375 | 0.000 |
| b2_s42 | 0.542 | 0.333 | 0.125 | 0.014 | 0.000 | 0.167 | 0.375 |
| b2_s43 | 0.236 | 0.417 | 0.069 | 0.986 | 0.111 | 0.333 | **0.917** |
| b2_s44 | 0.292 | 0.000 | 0.000 | 0.014 | 0.000 | 0.708 | 0.208 |

**해석 주의 (필수 병기) — 이것은 반사실 쌍이 아니라 서로 다른 씬의 비교다.**

* **결과 요약**: 1차 분류에서 세 모델 모두 **FA_C-like > FA_D-like**. 방향은 "단서가 서 있는 팔에서
  오경보가 더 난다"는 §2-3의 예측과 일치한다.
* **그러나 rgb의 신호는 sceneN3 한 씬이 전담한다.** sceneN3는 **trompe-l'œil(가짜 계단 그림)** — 즉
  설계상 하드 네거티브다. C군에서 N3를 빼면 rgb는 **FA(C2만) 0.069 vs FA_D 0.348 = −0.279로 부호가
  뒤집힌다.** depth(+0.267)·b2(+0.194)는 N3를 빼도 부호가 유지된다.
* **표본이 심하게 불균형하다** — C군 48프레임 대 D군 360프레임, 그리고 C군은 **씬 2개**뿐이다.
  씬-클러스터 관점에서 유효 표본은 사실상 n = 2다(§RT.5 정신).
* **v2 off팔은 진짜 D팔이 아니다.** "D-like"라 부른 5씬 중에서도 `cue_scene_dressing`이 자유인 씬
  (s05·s14·s15·s18)은 드레싱이 남는다. **무위험·무단서의 순수 FA_D 표본은 v2에 존재하지 않으며**
  (§2-3), 그것을 만드는 것이 v3 D팔의 존재 이유다.
* **⇒ 결론 등급: 방향 증거(directional evidence) 전용.** 이 표로 "단서가 FA를 유발한다"를
  **주장하지 않는다**. FA_C/FA_D의 정량 분해는 v3의 반사실 쌍(A,C)/(A,D)에서만 가능하다.

---

## 5. 트윈 Δ tier 재층화 — **수행 완료** (GPU 재실행 없음)

**덤프 가용성**: F2(`rt_response/f2_twin_conditional.json`, `code/f2_twin_conditional.py`)는
`runs/v2/<run>/twin/twin_pairs.csv`만 읽는다. 그 원본 9개가 모두 디스크에 있고, 더욱이 §0에서
교정 GT 기준 `per_frame_{on,off}.csv`를 만들었으므로 **공표 도구(`twin_analysis.py`)를 교정 매니페스트로
그대로 다시 돌릴 수 있었다** — 재층화가 아니라 **정식 재계산**이다. **GPU 미사용 · CPU numpy 전용.**
재생성: `code/rescore_twin.sh`(§0). 결과: `eval_v2corr/<run>/twin/`.

포즈 필터·`--tol 0.15`·`--n-boot 10000` 모두 공표와 동일. **kept 366 / excluded 42는 교정 전후 동일**
(포즈 필터는 GT와 무관하므로 당연).

### 5.1 tier별 twin Δ(`delta_score`) — 공표 → 교정

| run | Δ all | Δ **H** (n) | Δ V (n) | Δ E (n) | Δ H_weak (n) |
|---|---|---|---|---|---|
| rgb_s42 | 0.310 → **0.331** | 0.170 → **0.170** (96→96) | 0.442 → 0.462 (165→177) | 0.164 → 0.164 (45) | 0.029 → 0.311 (6→9) |
| rgb_s43 | 0.309 → **0.332** | 0.359 → **0.359** (96→96) | 0.315 → 0.347 (165→177) | 0.212 → 0.212 (45) | 0.078 → 0.343 (6→9) |
| rgb_s44 | 0.323 → **0.335** | 0.327 → **0.327** (96→96) | 0.408 → 0.418 (165→177) | 0.049 → 0.049 (45) | −0.020 → 0.240 (6→9) |
| depth_s42 | 0.621 → **0.620** | 0.413 → **0.413** (96→96) | 0.776 → 0.760 (165→177) | 0.574 → 0.574 (45) | 0.025 → 0.317 (6→9) |
| depth_s43 | 0.680 → **0.678** | 0.440 → **0.440** (96→96) | 0.868 → 0.848 (165→177) | 0.593 → 0.593 (45) | 0.002 → 0.294 (6→9) |
| depth_s44 | 0.524 → **0.522** | 0.367 → **0.367** (96→96) | 0.627 → 0.616 (165→177) | 0.537 → 0.537 (45) | 0.105 → 0.263 (6→9) |
| b2_s42 | 0.186 → **0.179** | 0.073 → **0.073** (96→96) | 0.307 → 0.287 (165→177) | 0.005 → 0.005 (45) | 0.008 → 0.038 (6→9) |
| b2_s43 | 0.263 → **0.269** | 0.069 → **0.069** (96→96) | 0.399 → 0.398 (165→177) | 0.200 → 0.200 (45) | 0.096 → 0.205 (6→9) |
| b2_s44 | 0.253 → **0.249** | 0.187 → **0.187** (96→96) | 0.370 → 0.358 (165→177) | −0.001 → −0.001 (45) | 0.001 → 0.004 (6→9) |

**모델 평균**: Δ all rgb 0.314→**0.333** · depth 0.608→**0.607** · b2 0.234→**0.232** ·
Δ H rgb 0.285→**0.285** · depth 0.407→**0.407** · b2 0.110→**0.110** (**전부 동일**).

### 5.2 s12·"Depth H 96/96" 확인 — 요구된 검증

* **s12의 48프레임 H→V 이동은 test-core에 영향이 0이다.** scene12는 `split_v2_full.json`의
  **train** 소속이며 test 7씬에 없다. 따라서 공표 twin H tier의 근거 씬은 교정 전후 모두
  **scene14 60 + scene15 36 = 96**으로 동일하다 — 씬별 재계산에서 프레임 수·Δ·plain recall이
  전 런에서 소수 3자리까지 일치했다.
* **"Depth H 96/96"의 실체와 판정**: F2 규칙(`hit = max_on_gt ≥ τ ∧ max_off_gt < τ`)에서 depth의
  **off팔 트윈 발화율이 H tier 96쌍 전부에서 0.000**이라는 뜻이다 — 즉 twin-conditional recall이
  plain recall과 **정확히 같다**. 교정 후 재계산에서도 **그대로**:

  | run | H plain 공표→교정 | H twin-cond 공표→교정 | off팔 트윈 발화 |
  |---|---|---|---|
  | depth_s42 | 0.406 → 0.406 | 0.406 → 0.406 | 0.000 → 0.000 |
  | depth_s43 | 0.469 → 0.469 | 0.469 → 0.469 | 0.000 → 0.000 |
  | depth_s44 | 0.438 → 0.438 | 0.438 → 0.438 | 0.000 → 0.000 |

  ⇒ **`F2_TWIN_CONDITIONAL.md` §1 H 표와 §2 검증표는 교정 GT에서 수정 불필요.** rgb(0.375)·
  b2(0.122)의 H twin-conditional도 동일하게 불변이다.

### 5.3 움직이는 것 — V·H_weak, 그리고 왜

* **V tier kept가 165 → 177(+12)**. 새 V 39프레임 중 **12쌍만 포즈 필터를 통과**했고 **27쌍은
  `ground_z` 불일치로 excluded**다(D15/D17의 알려진 기전 — 토글이 카메라 자체 지면을 움직인다).
  excluded 42쌍은 교정 전 "V 15 + none_in_fov 27"에서 교정 후 **"V 42"** 로 바뀐다.
  **트윈 V 분모는 219가 아니라 177**임을 인용 시 반드시 밝힐 것.
* **Δ V의 이동은 모델별로 부호가 다르다** — rgb +0.010~+0.032(신규 프레임의 on−off 격차가 큼),
  depth −0.011~−0.020, b2 −0.020~−0.001. 어느 쪽도 시드 산포를 넘지 않는다.
* **Δ H_weak는 크게 뛴다**(예: rgb_s42 0.029 → 0.311). **분모가 6 → 9인 행이다. 인용 금지.**
* **Δ all(전 tier pooled)은 rgb에서만 +0.02 수준으로 오른다** — 신규 39 V프레임의 Δ가 rgb 평균보다
  높기 때문. `SEED_TABLE.md:21` "twin delta (all) rgb 0.314"를 인용하는 문장은 **0.333**으로 바뀐다.

---

## 6. 체감 카드 · 움직이는 공표 문장 목록

### 6.1 체감 카드

* **결정** — v2 체크포인트 9개를 교정 GT로 전수 재채점하고, 공표표와의 델타를 **A/B 표와 분리된 별도
  리포트**로 확정했다. 앞으로의 모든 v2↔v3 A/B는 **양측 교정 GT** 기준선(이 문서의 §1.2 표)에서 출발한다.
* **이유** — "test-core 프레임 불변"은 **이미지 불변이지 정답지 불변이 아니다**(§2-1). 한쪽만 교정 GT로
  채점하면 A/B가 무효가 된다. 특히 **recall 분모가 327→369(+12.8 %), V 분모가 180→219(+21.7 %)로
  커진 채로** v3만 그 분모에서 채점되면 v3가 구조적으로 불리해진다.
* **안 했으면 깨지는 것** — ① v3 헤드라인이 369 분모, v2 공표치가 327 분모로 **분모가 다른 두 수를
  같은 표에 인쇄**하게 된다(V 열에서 모델 평균 최대 **3.7 pp**, 시드 단위 최대 **6.9 pp**의 가짜 격차).
  ② `none_in_fov` 조건화 공개 의무를
  **19.9 %로 계속 인쇄**하게 된다(실제 9.6 %). ③ depth `cell_precision` 0.705가 계속 인용되는데,
  이는 **G7 결함 GT가 만든 과소평가**(교정치 0.756)다. ④ 역으로, 재채점을 안 했으면
  "H와 FA-정합 결론은 안 바뀐다"는 것도 **주장이지 사실이 아닌 채로** 남았다 — 지금은 실측이다.
* **증거 경로** — `experiments/v3_0823/eval_v2corr/rescore_tables.json`(집계 원장 · 게이트 4건) ·
  `eval_v2corr/<run>/{metrics.json,per_frame.csv,twin/}`(9세트 원자료) ·
  `eval_v2corr/logs/{rescore.log,twin.log}`(전 명령·타임스탬프) ·
  드라이버 `code/{rescore_v2corr.sh,rescore_twin.sh,rescore_tables.py}`.

### 6.2 움직이는 공표 문장 — **목록만 제출. 본 작업은 어떤 기존 파일도 수정하지 않았다.**

*(파일:행 포인터. Δ가 0인 문장은 "확인됨(불변)"으로 따로 묶었다.)*

> **행 번호 기준 시각: 2026-08-23 15:03.** `SEED_TABLE.md`(07:29 고정) · `METRICS.md`(09:20 고정) ·
> `RESULTS_DRAFT.md`(09:23 고정) · `F1/F2_*.md`(03:39/03:40 고정)는 안정적이지만,
> **`v3_0823/ACCOUNTING.md`는 다른 트랙이 append-only로 계속 늘리고 있다**(본 작업 중에도
> 14:44 → 14:53에 ≈14행 증가). ACCOUNTING 행 번호를 쓸 때는 **먼저 grep으로 재확인**할 것 —
> 앵커 문자열: `tier (on팔 408)` · `헤드라인 recall 분모` · `탈락 **81/408` · `test 81/408 = 19.9` ·
> `교정 GT 기준 v2 재채점 분모` · `none 81→**36**`.

**A. 반드시 갱신해야 하는 것 — 분모·V·셀 계열**

| file:line | 인용구 (요약) | 왜 움직이나 | 교정치 |
|---|---|---|---|
| `dayrun_0820/runs/v2/SEED_TABLE.md:13` | rgb 행 `frame_recall_V 0.796 ± 0.164`, `frame_det_rate 0.730 ± 0.179`, `cell_f1 0.450`, `cell_precision 0.566` | V 분모 180→219 · 양성 칸 +165 | 0.760 ± 0.203 · 0.717 ± 0.199 · 0.456 · 0.592 |
| `dayrun_0820/runs/v2/SEED_TABLE.md:14` | depth 행 `frame_recall_V 0.917 ± 0.042`, `frame_det_rate 0.716`, `cell_f1 0.677`, **`cell_precision 0.705`** | 〃 (precision은 유일한 σ 초과) | 0.900 ± 0.041 · 0.729 · 0.704 · **0.756** |
| `dayrun_0820/runs/v2/SEED_TABLE.md:15` | b2 행 `frame_recall_V 0.730 ± 0.111`, `frame_det_rate 0.499`, `cell_f1 0.340`, `cell_precision 0.527` | 〃 | 0.735 ± 0.119 · 0.526 · 0.367 · 0.590 |
| `dayrun_0820/runs/v2/SEED_TABLE.md:31-39` | §3 per-seed 표의 `frame_recall_V` · `frame_det_rate` · `cell_f1` · `cell_recall` · `cell_precision` 9행 | 〃 | 본 문서 §1.2 / `rescore_tables.json:runs.*.corrected` |
| `dayrun_0820/runs/v2/SEED_TABLE.md:21-23` | §2 `twin delta (all)` rgb 0.314 / depth 0.608 / b2 0.234 | V tier kept 165→177 | 0.333 / 0.607 / 0.232 |
| `dayrun_0820/runs/v2/SEED_TABLE.md:60,69-71` | §4 YOLO 행 `frame_recall_V 0.150 ± 0.028`(및 per-seed .117/.161/.172) | **같은 V 분모 문제** — YOLO 런은 본 재채점 범위 밖 | **미측정 — YOLO 3런도 교정 GT 재채점 필요(후속 큐)** |
| `dayrun_0820/runs/v2/SEED_TABLE.md:93-95` | "V recall 0.150 with cell precision 0.472 …" 해설 문단 | 위와 동일 | 재채점 후 갱신 |
| `dayrun_0820/runs/v2/SEED_TABLE.md:116-119` | §5 aux 부록 표의 `frame_recall_V`(0.828 / 0.639) · `cell_f1` · `cell_precision` | `rgb_s42_aux`는 본 재채점 9런에 없음 | **미측정 — aux 런 1개 추가 재채점 필요(후속 큐)** |
| `weekend_0823/rt_response/F1_FA_MATCHED.md:5` | "H n=96, E n=45, **V n=180**, off n=408" | V 분모 | **V n=219** |
| `weekend_0823/rt_response/F1_FA_MATCHED.md:87-92` | §4 "V and E at matched FA" 표의 V 3열 | V 분모 | 본 문서 §3.2 |
| `weekend_0823/rt_response/F1_FA_MATCHED.md:38-73` | §2 per-seed 표의 **V 열**(τ·FA·H·E는 불변) | V 분모 | `rescore_tables.json:runs.*.fa_matched.corrected` |
| `weekend_0823/rt_response/F1_FA_MATCHED.md:79-81` | §3 대조표의 `V` 열 0.796 / 0.917 / 0.730 | V 분모 | 0.760 / 0.900 / 0.735 |
| `weekend_0823/rt_response/F2_TWIN_CONDITIONAL.md:33` | "**V tier** (n = 165 kept pairs per run)" | kept V 165→177 | **n = 177** |
| `weekend_0823/rt_response/F2_TWIN_CONDITIONAL.md:37-39` | V tier 표 (plain / twin-cond / off-fire / share) 3행 | 〃 | rgb .859/.508 · depth .898↓ · b2 계열 — `rescore_tables.json:twin` |
| `weekend_0823/rt_response/F2_TWIN_CONDITIONAL.md:55,58,61,64,67,70,73,76,79` | §3 per-run 표의 **V 행** 9줄 | 〃 | 〃 |
| `v3_0823/ACCOUNTING.md:276,279` (§3.1 표) | `tier (on팔 408) V 180 · H_weak 6 · none_in_fov 81` · `헤드라인 recall 분모 … 408 − 81 = 327` | 구 GT 회계 행 — **유지하되 "구 GT"로 명시**하고 교정 행 병기 | V 219 · H_weak 9 · none 39 · 분모 **369** |
| `v3_0823/ACCOUNTING.md:280` | "탈락 **81/408 = 19.9 %**를 같은 표에 인쇄" | 조건화 공개 의무 수치 | **39/408 = 9.6 %** |
| `v3_0823/ACCOUNTING.md:359-360` (§4.2 말미) | "none 81→**36** → 헤드라인 recall 분모 327→**372**" | **산술 오류** (§0 정정 배너) | **none 81→39 · 분모 327→369** |
| `v3_0823/ACCOUNTING.md:198` (§2-3 분모 구멍) | "test 81/408 = 19.9 %" + `METRICS.md:1105` 포인터 | 〃 | 39/408 = 9.6 % |
| `v3_0823/ACCOUNTING.md:324` (§3.4 행 6) | "교정 GT 기준 v2 재채점 분모 (test-core 816 위) — 미기입" | **본 문서로 확정** | 369 (V 219·E 45·H 96·Hw 9) · 원장 `eval_v2corr/rescore_tables.json` · 2026-08-23 |

**B. 확인됨 — 움직이지 않는 것(재채점으로 실측 확인, 수정 불필요)**

| file:line | 인용구 | 실측 |
|---|---|---|
| `SEED_TABLE.md:13-15` | `frame_recall_H` 0.688 / 0.438 / 0.229 · `frame_recall_E` 0.556 / 0.600 / 0.178 · `frame_fa_off` 0.359 / 0.042 / 0.238 · `cell_fpr_off` 0.047 / 0.009 / 0.035 | **Δ = 0.0000 (9/9 런)** |
| `SEED_TABLE.md:9` | 읽는 법 배너 — "FA를 맞추면 전 지점에서 Depth ≥ RGB(.359 .781/.729 · .10 .510/.326 · .05 .479/.243)" | **네 지점 전부 동일 수치로 성립** |
| `SEED_TABLE.md:21-23` | §2 `twin delta (H tier)` 0.285 / 0.407 / 0.110 · `tau*` 열 | **동일** (τ\*는 동결값) |
| `SEED_TABLE.md:25` | "twin delta (H tier)는 2개 씬(scene14 60 · scene15 36) 위의 pooled 값" | **교정 후에도 60 + 36 = 96 그대로** |
| `SEED_TABLE.md:60` | YOLO `frame_recall_H = 0.000`, `frame_recall_E = 0.000` (D22 어댑터 천장) | H·E 분모 불변 ⇒ **논리적으로 불변**(단, 실측은 YOLO 재채점 대기) |
| `F1_FA_MATCHED.md:14-19` | §1 R1 공표표 검증 (0.719/0.740/0.385 등 4행) | **격자 규칙 재현치 소수 3자리까지 동일** |
| `F1_FA_MATCHED.md:27-32` | §2 권장표 H 열 + Δ(Depth−RGB) | **완전 동일** |
| `F1_FA_MATCHED.md:83` | "RGB는 FA .359에서, Depth는 .042에서 H를 읽는다 — 8.6배" | off팔 불변 ⇒ **동일** |
| `F2_TWIN_CONDITIONAL.md:17-23` | H tier 표 (n=96) 3행 전부 | **완전 동일** |
| `F2_TWIN_CONDITIONAL.md:25-31` | E tier 표 (n=45) 3행 | **완전 동일** |
| `F2_TWIN_CONDITIONAL.md:43-47` | §2 R2 검증표 (0.375 / 0.438 / 0.121) | **동일** |
| `F2_TWIN_CONDITIONAL.md:85-102` | §4 H tier by scene 표 18행 전부 | **완전 동일** |
| `G7_RELABEL.md:240,248` | test AFTER B 행 (V 219 · E 45 · H 96 · Hw 9 · none 39) · "test의 H 96은 불변" | **원장 실측과 일치 — 정본** |

### 6.3 `METRICS.md` · `RESULTS_DRAFT.md` 정밀 색인

**범위 주의 (오인용 방지).** `RESULTS_DRAFT.md` §5.1–§5.6과 `METRICS.md` §1–§13은 **v1 336프레임
코퍼스**(V 111 · E 9 · H 21 · none 27 · 981칸 · 15칸 그리드)다. G7은 v2 매니페스트 위에서 정의되고
그 42프레임은 scene07 `boost_e/boost_e2` 라운드에서 오는데 **이 라운드는 v1에 존재하지 않는다.**
⇒ **v1 스코프 수치는 전부 불변**이다. 아래는 v2 스코프만 나열한다.

**B-1. `mainrun_0819/METRICS.md` — 갱신 대상**

| file:line | 인용구 (요약) | 원인 |
|---|---|---|
| `METRICS.md:440-441` | "v2 test = 816 frames = 408 on (**V 180 · E 45 · H 96 · H_weak 6 · none_in_fov 81**)" | 정본 census |
| `METRICS.md:720-721` | "Denominators unchanged from the night section: … V 180 · E 45 · H 96 · H_weak 6 · none_in_fov 81" | 정본 census |
| `METRICS.md:628` | "Frame set = on-arm frames carrying ≥1 GT-positive cell (**test 327 / corpus 1038**)" | recall 분모 → **369 / 1101** |
| `METRICS.md:636-644` | N.7 경계-교차 7행 전부 `…/327` + 파생 % (65.1 % · 93.6 % 포함) | 위 줄의 하류 |
| `METRICS.md:656-664` | miss×straddle 표 `42/43/44 | 327` · pooled 981 · "flat stratum 21/327" | 〃 |
| `METRICS.md:671-677` | 점유율 표 `n GT+ cells (test) 117/378/870/1326/ all **2691**` + Q1/median/Q3 | 양성 칸 → 2,856 |
| `METRICS.md:698-699` | "test's **96/327 (29.4 %)**" | 분모 → 96/369 = **26.0 %** |
| `METRICS.md:1103-1131` | **RT.4 `FA_in-scene` 절 전체** — 헤딩 · `n` 열 81×9행 · 3시드 평균 0.798/0.494/0.638 · 씬별 표 `scene07 n=51` | none_in_fov 81→**39**, scene07 51→**9** |
| `METRICS.md:1105` | "**81 of the 816 test rows, 19.9 % of the 408 hazard-ON rows**" | → 39/816 · **9.6 %** |
| `METRICS.md:1082-1083` | RT.3 `H_weak | 6` · `none_in_fov | 81` 행 | H_weak 6→9 · none 81→39 |
| `METRICS.md:1079,1090,1094,1100` | RT.3 `V | 180 | …` 3행 + "adapter ceiling … V 0.514" | V 분모 |
| `METRICS.md:1029-1034` | RT.1 FA-정합 표의 **RGB V / Depth V / B2 V 3열**(E 열은 불변) | V 분모 → 본 문서 §3.2 |
| `METRICS.md:1060,1064-1066` | RT.2 "**V tier** (n = **165** kept pairs)" + V 3행 | kept V → **177** |
| `METRICS.md:766,1098` | "twin-conditional … H −0.010 vs **V +0.337**" | V 분모 |
| `METRICS.md:734,737,744,756-758` | YOLO 행 `frame_recall_V` · `frame_det_rate` · `cell_recall_V` · "0.028 vs 0.029" | V 분모 · YOLO 재채점 대기 |
| `METRICS.md:739-741,747-750` | YOLO `cell_f1/recall/precision` · band1–4 cell recall | 양성 칸 |
| `METRICS.md:789-802,810-818` | aux 런 `cell_f1/recall/precision` · `frame_recall_V` · `frame_det_rate` · band recall · "312 carrying ≥1 GT cell" · "Δ_score V 0.4927 / all 0.3675" | V 분모 · 양성 칸 · aux 재채점 대기 |
| `METRICS.md:1189-1196` | 클러스터-CI의 `cell_f1` · `cell_precision` · `frame_det_rate` · `frame_recall_V` 행 | 〃 |
| `METRICS.md:1239-1247` | RT.7-c split 표 `test | 180 | 45 | 96 | 6 | 81` · `non-hold total | 693 | 72 | 243 | 30 | 282` · "312 = H_weak 30 + none 282" | 코퍼스 census → V 801 · H 195 · Hw 33 · none 315 |
| `METRICS.md:1235` | "corpus **V 726 → 657**, H_weak 0 → 57 (τ_int 1→200 sweep)" | 코퍼스 V |
| `METRICS.md:491-495,511-513` | N.1/N.2 all-tier Δ pool ("Published − EXACT-only +0.041/+0.001/+0.037" · "366 kept pairs" 밴드별 Δ) · "scene07 (24, Δ_rgb 0.740)" | Δ all pool이 GT+ 보유 쌍 기준이라 +12쌍 |
| `METRICS.md:462-466` | N.1 stratum 표 V 열 `132/33/15` · `H_weak/none` 열 `39/21/27` · "carries ≥1 GT+ cell 279/33/15" | V 분모 · GT+ pool |
| `METRICS.md:556-573` | *(2차)* N.4 ρ +0.848 · "FA ÷ prior 0.377→0.234 · band2 0.243→0.062" · train prior 밴드별 | **분자 FA는 불변, 분모(train prior)만 이동** — 코퍼스 V 693→801. `config.json`의 동결 bias 벡터는 훈련 산물이라 **불변** |
| `METRICS.md:360` | *(주의)* v1 문장 "`scene07` 18 fr / **39 cells**(test) … +39 positive cells (+4.0 %)" | **v1 스코프 = 불변.** 다만 같은 씬·같은 "39"라 오인 위험 1위 — 각주로 구분 표기 권고 |

**B-2. `mainrun_0819/RESULTS_DRAFT.md` — 갱신 대상**

| file:line | 인용구 (요약) | 원인 |
|---|---|---|
| `RESULTS_DRAFT.md:269` | "on-arm frames that carry at least one GT-positive cell (**test 327 / corpus 1038**)" | recall 분모 → **369 / 1101** |
| `RESULTS_DRAFT.md:271-284` | "**93.6 %** … **96.8 %** … median 8 cells / 5 sectors" · "**66–86 %** · **8.3 %** · **28.4 %** · **65.1 %**" · straddle −0.309…+0.084 · "flat stratum 21 frames" | 위 줄의 하류 |
| `RESULTS_DRAFT.md:286-291` | 점유율 중앙값 0.288/0.655/0.610/0.861 · "71 % / 34 % / 14 %" · Q1·Q3 | 양성 칸 2,691→2,856 |
| `RESULTS_DRAFT.md:330-333` | "frame recall **0.150 ± 0.028 on the V tier** (0.117/0.161/0.172)" | V 분모 · YOLO 재채점 대기 |
| `RESULTS_DRAFT.md:356-361` | "−0.010 **against +0.337 on the visible tier**" · "at **0.150** with cell **precision 0.472**" | V 분모 · 양성 칸 |
| `RESULTS_DRAFT.md:371-385` | aux "cell precision **+0.129**" · "Cell F1 **+0.040** [0.0001, 0.0786] → [−0.258, 0.205]" · "**V recall 0.828 → 0.639**, det **0.731 → 0.563**" | 양성 칸 · V 분모 · aux 재채점 대기 |
| `RESULTS_DRAFT.md:390-392` | "생존하는 건 FA/정밀도 계열만 (`frame_fa_off`·`cell_fpr_off`·**`frame_recall_V`**)" | `frame_recall_V`의 Δ·CI 재계산 |
| `RESULTS_DRAFT.md:545` | "−0.010 … **against +0.337 on the visible tier**" | V 분모 |
| `RESULTS_DRAFT.md:552` | **RT-E(a) 문단 전체** — "**19.9 % of hazard-ON test frames (81/408)**" + RGB 0.798 ± 0.160 / Depth 0.494 ± 0.074 / B2 0.638 ± 0.228 | none_in_fov → **9.6 % (39/408)**, 세 수치 전부 재계산 |
| `RESULTS_DRAFT.md:556` | RT-E(c)의 "`cell_f1` **+0.0403 [0.0001, 0.0786] → [−0.258, 0.205]**" 부분 | 양성 칸 *(같은 문장의 `cell_recall_H` 부분은 **불변**)* |
| `RESULTS_DRAFT.md:146` | "τ_int = 50 px … (**V 726 → 657**, H_weak 0 → 57)" | 코퍼스 V |
| `RESULTS_DRAFT.md:259-264` | *(2차)* N.4 ρ **+0.848** · "FA ÷ prior far row **0.234** vs v1 0.377 · band 2 **0.062**" | train prior 분모 |

**B-3. 두 파일이 **함께** 움직여야 하는 쌍 2건 (정합성 위험)**

1. **`test 327 / corpus 1038`** — `METRICS.md:628`과 `RESULTS_DRAFT.md:269` 두 곳뿐이며
   **동시에 369 / 1101로** 가야 한다. `METRICS.md:636-664`의 모든 `/327`과
   `RESULTS_DRAFT.md:271-284`의 모든 파생 %가 이 한 줄의 하류다.
2. **`V 726 → 657`** (τ_int 스윕 양끝) — `METRICS.md:1235`과 `RESULTS_DRAFT.md:146`.
   census 표 바깥에 있는 **유일한 코퍼스-V 수치**라 누락되기 쉽다.

**B-4. 확인됨 — `METRICS.md`·`RESULTS_DRAFT.md`에서 움직이지 않는 주요 문장**

* `METRICS.md:39` tier-recall 정의 ("`H_weak`·`none_in_fov` 제외") — **규칙 자체는 불변**, 소속만 이동.
* `METRICS.md:515-548` N.3 전체 — "0 of 96 H frames carry a GT cell in band 1 or 2" · "75 of 96 come
  from the boost rounds" · 21프레임 byte-identical 대조 · standoff 표.
* `METRICS.md:575-600` N.5 off팔 FA 씬별 표 (all off 0.359/0.042/0.238 · C2 0.069/0.292 ·
  "FA rise is not a denominator effect") — **off팔은 교정 무관**.
* `METRICS.md:602-624` N.6 τ 스윕 · `METRICS.md:685-695` N.8 val 커버리지(val split 미변경).
* `METRICS.md:1016-1036` RT.1 H 표("n = 96 H, 408 off") + FA-정합 표의 **E 열** · 읽기 문단.
* `METRICS.md:1044-1058` RT.2 **H(n=96)·E(n=45)** 블록 전부(0.688→0.375 · 0.438→0.438 · 44.7 %).
* `METRICS.md:1068` "0 of 96 pairs fire on the hazard-deleted twin" · `:1100` "all **96** test H frames
  carry a non-empty GT box" · `:768-772` "1 hazard frame of **96**".
* `METRICS.md:1133-1147` RT.4 sceneN3 정정 블록 · `:1154-1182` off팔 FA 씬-클러스터 CI · 씬별 H recall
  ("scene15가 H 분모의 **37.5 %**") · `:1203-1228` RT.6 전체 · `:1254` "test strict-H rests on 2 scenes".
* `RESULTS_DRAFT.md:21` "**all 96 test H pairs** differ optically" · `:188-199` N.1 밴드-3b H twin Δ ·
  `:203-221` N.2 EXACT/TOL 각주("54 tolerance-rescued pairs 중 H tier 0개") — 단
  **`:209-210` "they are 33 V and 21 H_weak/none"만 이동**(`METRICS.md:465` 대응).
* `RESULTS_DRAFT.md:241-257` N.4 off팔 FA 표 · `:301-309` N.6("96 frames 전부 band 3b에 GT") ·
  `:344-350` image-space 0.066 · `:372-393` aux의 FA/정밀도·E붕괴·H 미확정 서술 ·
  `:516-547` RT-A~RT-D 전부 · `:554` RT-E(b) sceneN3 null 대조 · `:561-564` RT-F 그림 표.
* `RESULTS_DRAFT.md:23-24, 36-65, 107-119, 136-137, 161-171` 및 `METRICS.md:32-342, 371-412` —
  **v1 스코프 전량 불변**. 특히 `RESULTS_DRAFT.md:136-137`의 "39 of them in the test split"은
  v1 step-gate 수치로, G7의 39와 **무관**하다(각주 권고).

### 6.4 후속 큐 (본 리포트가 만든 것)

1. **YOLO 3런(`runs/yolo_s{42,43,44}`) 교정 GT 재채점** — 본 임무 범위(9 U-Net 체크포인트) 밖이나,
   `SEED_TABLE.md` §4 본표 4행의 V 열이 같은 이유로 움직인다. τ 0.25 · `det2cell.py` 어댑터 유지.
2. **`rgb_s42_aux` 1런 재채점** — §5 부록 표(단일 시드)의 V·셀 계열.
3. **§6.3 색인대로 `RESULTS_DRAFT.md`·`METRICS.md` 실제 편집** — 본 작업은 목록 제출까지다(편집 금지).
   특히 B-3의 쌍 2건은 **동시에** 고칠 것.
4. **`ACCOUNTING.md` §4.2 산술 오류 정정 append** (test-core `none 81→39` · `분모 327→369`) —
   본 문서 §0 배너가 근거. 같은 §4.2의 **코퍼스 표(V 693→801 · H 243→195 · Hw 30→33 · none 378→315)는
   원장 실측과 일치하므로 정정 불필요**하고, 코퍼스 hazard 분모는 **1038 → 1101**이다.
5. **v3 A/B 기준선 고정**: 앞으로 v2 쪽 수치는 본 문서 **§1.2 표**를 인용한다.

---

# §7 【APPEND · 08-23 22:49】 부록 인코더 6런 재채점 (A-3 / D69)

*append-only. §0–§6은 한 자도 수정하지 않았다. 목적: 제출 INDEX 재발행 목록 A-3 —
부록 행에서 **"구 GT 측정" 태그 제거**.*

**한 줄 결론.** 부록 6런(resnet50 ×3 · tu-convnext_tiny ×3) 전부 교정 GT로 재채점 완료.
**확률 비트 동일 · H 행 6/6 완전 불변**, σ 초과는 2건(둘 다 §2와 같은 기전)이며,
**FA-정합 부록표(`newmodels/FA_MATCHED.md` §1)는 H 열이 소수 3자리까지 그대로 성립**한다.

## 7.1 프로비넌스 · 재생성

가중치는 **디스크에 존재**한다(재훈련 없음): `experiments/weekend_0823/newmodels/runs/<run>/best.pt`
(resnet50 130.6 MB × 3 · tu-convnext_tiny × 3). 공표 부록표 출처는
`experiments/weekend_0823/newmodels/FA_MATCHED.md` (§1 FA-정합 · §2 τ=0.5 무정합) ·
`newmodels/runs/<run>/eval_test/metrics.json`.

```bash
R=/home/vislab/Desktop/work_sy/Practice_NegObs
tmux new-session -d -s a3rescore
tmux send-keys -t a3rescore "bash $R/experiments/v3_0823/code/rescore_a3_appendix.sh" Enter
PYTHONNOUSERSITE=1 CUDA_VISIBLE_DEVICES= /home/vislab/miniconda3/envs/env_seg/bin/python \
  $R/experiments/v3_0823/code/rescore_a3_tables.py     # -> eval_v2corr/rescore_a3_tables.json
```

공표 호출(`weekend_0823/code/run_newmodels.sh:93-94`)과의 차이는 **§0과 동일한 두 줄뿐**:
`--manifest` → `dataset_manifest_v2corr.json`, `--tau-star auto` → **공표 고정값**
(resnet50 .72/.36/.58 · convnext .31/.30/.33). `--encoder` 플래그는 **주지 않는다** —
eval_polar가 ckpt의 `config["encoder"]`에서 되읽는다(D45). 로그에 `[model] encoder=resnet50` ·
`encoder=tu-convnext_tiny`로 정상 복원 확인. 나머지(`--input rgb --subset test --tau-op 0.5
--tau-sweep 0.3,0.5,0.7 --grid gridspec_v1.json`, n-boot = eval_polar 기본 10000) 동일.

**런타임 2분 55초** (22:46:52 → 22:48:47, 런당 19–20 s). D69 A-3 "GPU 유휴 시 실행" 지침대로
매 invocation을 `flock -o /tmp/negobs_gpu.lock`로 감싸고 201/202에 backoff·재시도하도록 짰다 —
동시 가동 중이던 씬 빌더(tmux `ncuebuild`)와 충돌 0회, 대기 0회.

산출: `eval_v2corr/{resnet50,tu-convnext_tiny}_s{42,43,44}/{metrics.json,per_frame.csv,METRICS_SECTION.md,DONE}`
· `eval_v2corr/A3_DONE` · `eval_v2corr/rescore_a3_tables.json` · 로그 `eval_v2corr/logs/rescore_a3.log`.
*(공표 부록 런과 동일하게 `per_frame_{on,off}.csv`·twin은 만들지 않았다 — 부록 트랙은 원래 없었다.)*

## 7.2 무결성 게이트 — 3/3 통과 (정본 9런과 동일 기준)

| 게이트 | 실측 | 판정 |
|---|---|---|
| 확률 불변 | **6/6 런 `max|Δp| = 0.000e+00`** | ✅ |
| frame_id 집합 동일 | 6/6 True | ✅ |
| **H 행 불변** | **6/6 `frame_recall_H`·`cell_recall_H` 완전 동일** | ✅ |
| off팔 불변 | 6/6 `frame_fa_off`·`cell_fpr_off` Δ = 0.0000 | ✅ |

| run | frame_recall_H 공표 → 교정 | frame_fa_off 공표 → 교정 |
|---|---|---|
| resnet50_s42 | 0.4688 → 0.4688 | 0.2132 → 0.2132 |
| resnet50_s43 | 0.2396 → 0.2396 | 0.3431 → 0.3431 |
| resnet50_s44 | 0.2188 → 0.2188 | 0.1912 → 0.1912 |
| tu-convnext_tiny_s42 | 0.8438 → 0.8438 | 1.0000 → 1.0000 |
| tu-convnext_tiny_s43 | 1.0000 → 1.0000 | 1.0000 → 1.0000 |
| tu-convnext_tiny_s44 | 0.6250 → 0.6250 | 0.7279 → 0.7279 |

**구 분모(327) 대조도 정본 9런과 똑같이 닫힌다** — 6/6 런 × 전 tier가 공표치와 소수 4자리까지 동일
(`rescore_a3_tables.json:runs.*.corrected_at_old_denom`). ⇒ 부록 델타도 **분모 성장 단일 기전**이다.

## 7.3 부록 헤드라인 — 교정 GT (τ_op 0.5 · 분모 V 219 · E 45 · H 96 · Hw 9 · det 369 · off 408)

| 인코더 | n | cell_f1 | frame_det_rate | recall V | recall E | recall H | recall H_weak | frame_fa_off | cell_fpr_off |
|---|---|---|---|---|---|---|---|---|---|
| resnet50 | 3 | 0.476 ± 0.073 | 0.600 ± 0.075 | 0.763 ± 0.078 | 0.430 ± 0.256 | **0.309 ± 0.125** | 0.593 ± 0.167 | **0.249 ± 0.076** | 0.033 ± 0.006 |
| tu-convnext_tiny | 3 | 0.223 ± 0.116 | 0.815 ± 0.229 | 0.798 ± 0.269 | 0.956 ± 0.067 | **0.823 ± 0.188** | 0.444 ± 0.500 | **0.909 ± 0.136** | 0.081 ± 0.054 |
| *(참고) resnet34 = 정본* | 3 | 0.456 ± 0.117 | 0.717 ± 0.199 | 0.760 ± 0.203 | 0.556 ± 0.378 | 0.688 ± 0.141 | 0.815 ± 0.222 | 0.359 ± 0.127 | 0.047 ± 0.016 |

보조: cell_recall resnet50 0.392 ± 0.075 · convnext 0.176 ± 0.128 ·
cell_precision resnet50 **0.614 ± 0.079** · convnext **0.387 ± 0.023**.

## 7.4 델타 vs 공표 부록 수치

기준: `newmodels/FA_MATCHED.md` §2(τ=0.5 무정합 표) + `newmodels/runs/<run>/eval_test/metrics.json`.
**공표치 재계산이 FA_MATCHED §1·§2와 소수 3자리까지 일치**함을 먼저 확인했다
(resnet50 H .309 · E .430 · V .778 · FA .249 / convnext H .823 · E .956 · V .824 · FA .909 ✓).

| 인코더 | metric | 공표 | 교정 | **Δ** | σ(교정) | \|Δ\|/σ |
|---|---|---|---|---|---|---|
| resnet50 | cell_f1 | 0.4595 | 0.4758 | +0.0163 | 0.0783 | 0.21 |
| resnet50 | cell_recall | 0.3868 | 0.3915 | +0.0046 | 0.0810 | 0.06 |
| resnet50 | cell_precision | 0.5720 | 0.6136 | +0.0416 | 0.0823 | 0.50 |
| resnet50 | frame_det_rate | 0.5851 | 0.5998 | +0.0147 | 0.0861 | 0.17 |
| resnet50 | **frame_recall_V** | 0.7778 | 0.7626 | **−0.0152** | 0.0780 | 0.20 |
| resnet50 | frame_recall_E | 0.4296 | 0.4296 | **0.0000** | 0.2651 | 0 |
| resnet50 | **frame_recall_H** | 0.3090 | 0.3090 | **0.0000** | 0.1387 | 0 |
| resnet50 | **frame_recall_H_weak** | 0.3889 | 0.5926 | **+0.2037** | 0.1697 | **★ 1.20** |
| resnet50 | frame_fa_off | 0.2492 | 0.2492 | **0.0000** | 0.0821 | 0 |
| resnet50 | cell_fpr_off | 0.0327 | 0.0327 | **0.0000** | 0.0060 | 0 |
| convnext_tiny | cell_f1 | 0.2106 | 0.2230 | +0.0124 | 0.1214 | 0.10 |
| convnext_tiny | cell_recall | 0.1692 | 0.1761 | +0.0069 | 0.1381 | 0.05 |
| convnext_tiny | **cell_precision** | 0.3545 | 0.3866 | **+0.0321** | 0.0231 | **★ 1.39** |
| convnext_tiny | frame_det_rate | 0.8328 | 0.8148 | −0.0180 | 0.2412 | 0.07 |
| convnext_tiny | **frame_recall_V** | 0.8241 | 0.7976 | **−0.0265** | 0.2933 | 0.09 |
| convnext_tiny | frame_recall_E | 0.9556 | 0.9556 | **0.0000** | 0.0770 | 0 |
| convnext_tiny | **frame_recall_H** | 0.8229 | 0.8229 | **0.0000** | 0.1884 | 0 |
| convnext_tiny | frame_recall_H_weak | 0.3333 | 0.4444 | +0.1111 | 0.5092 | 0.22 |
| convnext_tiny | frame_fa_off | 0.9093 | 0.9093 | **0.0000** | 0.1571 | 0 |
| convnext_tiny | cell_fpr_off | 0.0808 | 0.0808 | **0.0000** | 0.0600 | 0 |

**σ 초과 2건 — 둘 다 §2에서 이미 본 기전, 새 현상 아님.**

1. **convnext_tiny `cell_precision` +0.032 (1.39 σ)** — §2.1의 depth `cell_precision` +0.051(1.65 σ)과
   **같은 기전**: 양성 칸 2,691→2,856으로 늘면서 이미 켜져 있던 칸이 FP→TP로 재분류된다.
   convnext는 τ=0.5에서 거의 상시 발화하므로(FA 0.909) 새 양성 칸을 **전부** 주워 담아
   σ가 유난히 작은데도(0.023) 비율이 커졌다. **모델이 좋아진 게 아니라 정답지가 온 것**이다.
   resnet50(+0.042, 0.50 σ)·resnet34(+0.026, 0.63 σ)도 같은 방향.
2. **resnet50 `frame_recall_H_weak` +0.204 (1.20 σ)** — **분모 6→9의 퇴화 행. 인용 금지**
   (§2.1의 depth H_weak 항목과 동일 취급). 실체는 신규 H_weak 3장 중 resnet50이 일부를 잡는다는 것뿐.

**정확히 0인 칸**: `frame_recall_H` · `frame_recall_E` · `frame_fa_off` · `cell_fpr_off` — 6/6 런.
정본 9런과 같은 이유(H·E 프레임과 off팔 408은 교정 대상이 아니고 확률이 비트 동일).

**FA-정합 부록표(`FA_MATCHED.md` §1)의 운명**: H 열 **전 지점 불변** —
resnet50 .479/.267/.115/.056 · convnext .358/.160/.073/.031 (교정 전후 동일), 따라서
Δ(r50−r34) −0.250/−0.215/−0.212/−0.188 · Δ(convnext−r34) −0.372/−0.323/−0.253/−0.212도 **그대로**다.
§3.1의 이유와 동일: τ는 off팔에서만, 값은 H 96프레임에서만 나온다.
**V 열만 이동** — resnet50 .819→.820 / .759→.743 / .654→.626 / .524→.493 ·
convnext .252→.213 / .104→.091 / .039→.033 / .013→.012.

## 7.5 FA 인구조사(FA census)의 부록 계층 — **이제 재생성 가능**

`code/fa_census_extract.py:70-73`은 지금 `--corr`와 `--appendix`를 **상호배타로 하드 차단**하고
있고 그 사유가 *"resnet50/convnext_tiny have no corrected-GT dumps"* 인데, **§7.1로 그 전제가
해소됐다** — 6런의 교정 GT 덤프가 `eval_v2corr/`에 정본 9런과 나란히 존재한다. 따라서 부록 계층은
**GPU 없이 재생성 가능**하며, 필요한 것은 `:71-73`의 guard 제거와 `:76-78`의 `corr` 분기에
`APPENDIX` 경로를 `eval_v2corr/<run>`으로 매핑하는 **한 곳의 수정**뿐이다(본 작업 범위 밖 —
후속 큐 6번). 참고로 census 두 계층 중 **`OFF`(2,212건)는 교정 불변**이고
**`ON_NEG`(4,713건)만 줄어든다**(온팔 음성 칸 165개/런이 양성으로 전환) — 부록 행에 붙은
"구 GT 측정" 태그가 정확히 이 `ON_NEG` 계층 때문이었다. 부록 런은 `per_frame_{on,off}.csv`를
싣지 않지만 추출기가 `:101-108`에서 결합본을 즉석 분할하므로 추가 산출물은 필요 없다.

## 7.6 §6.4 후속 큐 갱신

* ~~(신규)~~ **A-3 부록 6런 재채점 — 완료**(본 §7). 제출 INDEX의 부록 행에서 **"구 GT 측정" 태그
  제거 가능**. 인용처는 `newmodels/FA_MATCHED.md` §1(H 열 **수정 불필요**) · §2(**V·cell 열 교체**,
  H·E·FA 열 불변) · `eval_v2corr/rescore_a3_tables.json`.
* **6. (신규) `fa_census_extract.py`의 `--corr --appendix` 조합 해금** — §7.5 참조.
* §6.4의 1(YOLO 3런)·2(`rgb_s42_aux` 1런)는 **여전히 미착수**. 부록 인코더와 달리 이 둘은
  본 재채점(정본 9 + 부록 6 = 15런)에 포함되지 않았다.

---

# §8 【APPEND · 08-23 22:56】 마지막 구 GT 행 정리 — YOLO 3런 + rgb_s42_aux

*append-only. §0–§7 무수정. §6.4 후속 큐 **1·2번 마감**. 이로써 test-core 위 v2 계열
**19런(정본 9 + 부록 6 + YOLO 3 + aux 1)이 전부 교정 GT 기준**이 됐다.*

**한 줄 결론.** 4런 모두 확률 비트 동일 · **H 행 4/4 완전 불변**(YOLO는 0.000 그대로 = D22 어댑터
천장 주장 무손상), 어댑터-프리 spot-check의 H 행도 불변. σ 초과는 **YOLO `frame_recall_V`
−0.027(1.11 σ) 1건** — 이 시리즈 전체에서 **V recall이 σ를 넘은 유일한 사례**다. 부수 소득으로
aux 부록의 `cell_f1` 유의 주장이 **교정 GT에서 프레임 i.i.d. 부트스트랩만으로도 무너진다**(§8.5).

## 8.1 가중치 존재 확인 · 파이프라인 성격

**AGPL untrack 정책에도 불구하고 YOLO 가중치는 디스크에 있다**:
`dayrun_0820/runs/yolo_s{42,43,44}/weights/best.pt` (6.2 MB × 3) + 동결 예측 덤프
`pred_test/labels/` (233 / 427 / 515 txt). `rgb_s42_aux/best.pt`(97.9 MB)도 존재. **재훈련 0.**

**YOLO의 평가 경로는 순전파가 아니다.** `code/run_yolo_all.sh:20-23`:
`train → predict(txt 덤프) → det2cell.py → eval_polar --per-frame-a`.
**매니페스트는 det2cell 단계에서만** 들어간다(GT `g_*` 칸 + 지면투영용 `cam` 포즈). 교정 매니페스트는
`cam`을 바이트 동일하게 보존하므로(§0 g7_build_v2corr의 `GT_KEYS`만 교체) **투영이 불변 → `p_*`도
불변**이어야 하고, 그것이 §8.2의 게이트다. 따라서 이 절반은 **GPU 완전 불필요 · CPU 전용**이며,
공표 스크립트도 이 두 단계에 **GPU 락을 걸지 않았다** — 동일하게 재현했다(씬 빌더 배려에도 부합).
`rgb_s42_aux`만 순전파이므로 **flock 홀드**로 돌렸다.

```bash
R=/home/vislab/Desktop/work_sy/Practice_NegObs
tmux send-keys -t a3rescore "bash $R/experiments/v3_0823/code/rescore_final_rows.sh" Enter
PYTHONNOUSERSITE=1 CUDA_VISIBLE_DEVICES= $CONDA/env_seg/bin/python \
  $R/experiments/v3_0823/code/rescore_final_tables.py        # -> eval_v2corr/rescore_final_tables.json
PYTHONNOUSERSITE=1 CUDA_VISIBLE_DEVICES= $CONDA/env_seg/bin/python \
  $R/experiments/v3_0823/code/rescore_f3_adapterfree.py      # -> eval_v2corr/f3_adapterfree_v2corr.json
# aux 짝지은 CI (공표 compare_aux_vs_base_s42의 교정판, CPU)
... eval_polar.py --per-frame-a eval_v2corr/rgb_s42_aux/per_frame.csv \
    --compare eval_v2corr/rgb_s42/per_frame.csv --out eval_v2corr/compare_aux_vs_base_s42 \
    --tau-op 0.5 --tau-star 0.5 --n-boot 10000 --grid gridspec_v1.json
```

공표 호출과의 차이: **YOLO는 `--manifest` 한 줄뿐**(`--conf 0.05 --bottom-samples 3` 등 det2cell
인자와 `--tau-op 0.25 --tau-sweep 0.1,0.25,0.5` 전부 동일). **aux는 §0과 같은 두 줄**
(`--manifest`, `--tau-star auto` → 동결값 **0.43**). **런타임 44초** (22:54:21 → 22:55:05;
YOLO 3런 CPU 25 s · aux GPU 19 s · flock 대기 0회) + F3 재계층화 CPU ≈50 s + 짝지은 CI ≈30 s.

## 8.2 무결성 게이트 — 4/4 통과

| 게이트 | 실측 | 판정 |
|---|---|---|
| 확률 불변 | **4/4 `max|Δp| = 0.000e+00`** (YOLO 포함 — det2cell 투영이 `cam` 불변으로 재현) | ✅ |
| **τ_op 동결 확인** | YOLO 공표 **0.25** → 교정 **0.25** (3/3) · aux 0.5 → 0.5 · τ\* YOLO 0.25(자동 폴백) · aux **0.43** 동결 | ✅ |
| **H 행 불변** | 4/4 `frame_recall_H`·`cell_recall_H` 완전 동일 | ✅ |
| off팔 불변 | 4/4 `frame_fa_off`·`cell_fpr_off` Δ = 0.0000 | ✅ |
| 구 분모(327) 대조 | 4/4 × 전 tier 공표치와 소수 4자리까지 동일 | ✅ |

| run | frame_recall_H 공표 → 교정 | frame_fa_off 공표 → 교정 |
|---|---|---|
| yolo_s42 | **0.0000 → 0.0000** | 0.0049 → 0.0049 |
| yolo_s43 | **0.0000 → 0.0000** | 0.0245 → 0.0245 |
| yolo_s44 | **0.0000 → 0.0000** | 0.0417 → 0.0417 |
| rgb_s42_aux | **0.7188 → 0.7188** | 0.1667 → 0.1667 |

> **D22 어댑터 천장 주장은 그대로다.** `SEED_TABLE.md:60,75-84`의 "`frame_recall_E`와
> `frame_recall_H`가 42·43·44 세 시드에서 **정확히 0.000**" 및 셀 수준 `cell_recall_E` =
> `cell_recall_H` = 0.000은 **교정 GT에서도 정확히 0.000**이다. 매핑 누수 경보도 발화하지 않았다.

## 8.3 어댑터-스코프 표 — YOLO (τ_op 0.25 · 분모 V 219 · E 45 · H 96 · Hw 9 · det 369 · off 408)

| model | n seeds | frame_recall_H | frame_recall_E | **frame_recall_V** | frame_det_rate | frame_fa_off | cell_fpr_off | cell_f1 | cell_recall | cell_precision |
|---|---|---|---|---|---|---|---|---|---|---|
| yolov8n @ τ0.25 **교정** | 3 | **0.000 ± 0.000** | **0.000 ± 0.000** | **0.123 ± 0.023** | 0.073 ± 0.014 | 0.024 ± 0.018 | 0.0015 ± 0.0010 | 0.025 ± 0.002 | 0.013 ± 0.001 | 0.472 ± 0.110 |
| *(공표, 구 GT)* | 3 | 0.000 ± 0.000 | 0.000 ± 0.000 | 0.150 ± 0.028 | 0.083 ± 0.015 | 0.024 ± 0.018 | 0.0015 ± 0.0010 | 0.026 ± 0.002 | 0.014 ± 0.001 | 0.472 ± 0.110 |

**시드별 (교정)**

| seed | recall_H | recall_E | recall_V | det_rate | fa_off | cell_f1 | cell_precision |
|---|---|---|---|---|---|---|---|
| 42 | 0.000 | 0.000 | **0.0959** (공표 0.117) | 0.0569 | 0.0049 | 0.0234 | 0.6071 |
| 43 | 0.000 | 0.000 | **0.1324** (공표 0.161) | 0.0786 | 0.0245 | 0.0277 | 0.3868 |
| 44 | 0.000 | 0.000 | **0.1416** (공표 0.172) | 0.0840 | 0.0417 | 0.0238 | 0.4217 |

### 8.3.1 델타 — **σ 초과 1건**

| metric | 공표 | 교정 | **Δ** | σ(교정) | \|Δ\|/σ |
|---|---|---|---|---|---|
| **frame_recall_V** | 0.1500 | 0.1233 | **−0.0267** | 0.0242 | **★ 1.11** |
| frame_det_rate | 0.0826 | 0.0732 | −0.0094 | 0.0143 | 0.66 |
| cell_f1 | 0.0264 | 0.0250 | −0.0015 | 0.0024 | 0.62 |
| cell_recall | 0.0136 | 0.0128 | −0.0008 | 0.0013 | 0.59 |
| cell_precision | 0.4719 | 0.4719 | **0.0000** | 0.1184 | 0 |
| frame_recall_H / E / H_weak | 0.0000 | 0.0000 | **0.0000** | 0.0000 | — |
| frame_fa_off | 0.0237 | 0.0237 | **0.0000** | 0.0184 | 0 |
| cell_fpr_off | 0.0015 | 0.0015 | **0.0000** | 0.0010 | 0 |

**이 시리즈 전체(19런)에서 V recall이 σ를 넘은 유일한 사례다.** 이유는 성능이 아니라 **σ가
유난히 작아서**다 — YOLO의 시드 산포는 V에서 ±0.023(rgb의 ±0.203의 1/9)이라 −0.027이 바로
1σ를 넘긴다. `SEED_TABLE.md:62-63`이 "표본 sd 0.029"라고 부기해 둔 바로 그 행이며, **교정 후
sd는 0.024**다. 기전은 §2.2와 동일: 신규 39 V프레임을 YOLO가 거의 못 잡는다
(s42 기준 구 21/180 → 신규 0/39 → 21/219). ⇒ **"V 0.150"을 인용하는 모든 문장은 0.123으로
교체하고, 이 행만은 "σ를 넘는 이동"으로 표시**해야 한다.
`cell_precision`이 정확히 0.0000 이동인 것은 우연이 아니다 — YOLO가 켠 칸이 워낙 적고(cells_fired
157/16,320) 신규 양성 칸 165개와 **겹치지 않았다**는 뜻이다.

## 8.4 어댑터-프리 H spot-check (F3) — 교정 tier로 재계층화

공표 파이프라인에 포함돼 있다(`rt_response/F3_ADAPTER_FREE_YOLO.md`, D35/R1-F3). 지표는
**이미지 공간 IoU**라 어댑터를 안 쓰지만, **tier로 층화**하므로 교정 GT의 영향을 받는다.
검출·amodal 박스·τ_conf 전부 동결, **바뀐 건 각 프레임이 어느 tier 칸에 들어가느냐뿐**이다.
재현: `code/rescore_f3_adapterfree.py`(원본 스크립트 미수정, 규칙 동일 · 공표측 수치 전항 재현 확인).

**τ_conf = 0.25 (어댑터 작동점) — 3시드 평균**

| tier | n 공표→교정 | any detection | **IoU > 0** | mean best IoU |
|---|---|---|---|---|
| V | 180 → **219** | 0.393 → 0.377 | **0.378 → 0.311** ±0.071 | 0.239 → 0.197 |
| E | 45 → 45 | 0.259 → **0.259** | **0.259 → 0.259** | 0.182 → **0.182** |
| **H** | **96 → 96** | 0.167 → **0.167** | **0.066 → 0.066** ±0.036 | 0.016 → **0.016** |
| H_weak | 6 → **9** | 0.167 → 0.185 | 0.167 → 0.111 | 0.003 → 0.002 |
| none_in_fov | 81 → **39** | 0.214 → 0.120 | 0.012 → 0.026 | 0.002 → 0.004 |

**τ_conf = 0.05 (저장된 모든 박스)**

| tier | n | any detection | **IoU > 0** | mean best IoU |
|---|---|---|---|---|
| V | 180 → 219 | 0.672 → 0.676 | **0.615 → 0.505** | 0.368 → 0.302 |
| E | 45 → 45 | 0.696 → **0.696** | **0.593 → 0.593** | 0.393 → **0.393** |
| **H** | **96 → 96** | 0.524 → **0.524** | **0.302 → 0.302** | 0.064 → **0.064** |
| H_weak | 6 → 9 | 0.722 → 0.667 | 0.500 → 0.333 | 0.095 → 0.063 |
| none_in_fov | 81 → 39 | 0.564 → 0.436 | 0.045 → 0.094 | 0.008 → 0.017 |

**H 행 전 열 완전 불변.** ⇒ `METRICS.md` §RT.3 / `RESULTS_DRAFT.md:344-350`의 핵심 문장
— "어댑터를 걷어내도 이미지 공간 H 적중률은 **0.066**, 트윈-조건부로는 −0.010" — 은
**교정 GT에서 수정 불필요**다. 어댑터 천장 주장이 두 경로(어댑터-스코프 §8.2 · 어댑터-프리 §8.4)
**모두에서** 살아남았다.

*(정직 기록)* V 행은 내려가고(0.378 → 0.311) `none_in_fov` 행은 **올라간다**(0.012 → 0.026).
분모가 81 → 39로 줄면서 남은 39프레임이 "낙차가 그리드 밖"인 어려운 잔여집합이 아니라,
**amodal 박스를 가진 9프레임의 비중이 커진** 결과다(9/81 = 11 % → 9/39 = 23 %). 즉 이 행의 상승은
검출기가 나아진 게 아니라 **모집단 구성이 바뀐 것**이며, 인용 시 분모를 반드시 병기해야 한다.

## 8.5 rgb_s42_aux (부록 §5, n = 1 시드)

| arm | recall_V | recall_E | recall_H | det_rate | fa_off | cell_f1 | cell_recall | cell_precision | cell_fpr_off |
|---|---|---|---|---|---|---|---|---|---|
| rgb_s42 **base** (교정) | 0.7763 | 0.600 | 0.5938 | 0.7127 | 0.375 | 0.4876 | 0.4233 | 0.5749 | 0.0527 |
| rgb_s42 **+aux** (교정) | **0.5982** | **0.000** | **0.7188** | 0.5501 | **0.1667** | **0.5209** | 0.4142 | **0.7017** | **0.0230** |
| *(참고) +aux 공표* | 0.639 | 0.000 | 0.7188 | 0.5627 | 0.1667 | 0.5255 | 0.4274 | 0.6821 | 0.0230 |

**델타 (교정 − 공표, aux 단독)**: V **−0.0407** · det −0.0126 · cell_f1 −0.0046 ·
cell_recall −0.0131 · **cell_precision +0.0196** · H **0.0000** · E **0.0000** · FA **0.0000** ·
cell_fpr_off **0.0000** · H_weak 0.000 → 0.333.
**n = 1이라 자체 σ가 없다** — `SEED_TABLE.md:158-160`의 관례대로 **base rgb 팔의 3시드 σ**를
잣대로 쓴다(§2.1: V 0.204 · cell_f1 0.120 · precision 0.042). **전 항목이 그 σ 이내**이며,
**σ 초과 0건**이다.

### 8.5.1 짝지은 CI (aux − base, 95 %) — 공표 → 교정, **판정이 바뀌는 행 1건**

교정판 `eval_v2corr/compare_aux_vs_base_s42/`(816 공통 프레임 · 짝지은 percentile bootstrap
10000× · seed 42 · τ 0.5 — 공표 `runs/v2/compare_aux_vs_base_s42`와 동일 설정).

| metric | 공표 Δ [95 % CI] | **교정 Δ [95 % CI]** | CI가 0 제외: 공표 → 교정 |
|---|---|---|---|
| **cell_f1** | +0.0403 [+0.0001, +0.0786] | **+0.0333 [−0.0057, +0.0708]** | **yes → NO** ⚠ |
| cell_precision | +0.1291 [+0.0885, +0.1690] | +0.1268 [+0.0881, +0.1652] | yes → yes |
| cell_recall | −0.0048 [−0.0488, +0.0377] | −0.0091 [−0.0511, +0.0317] | no → no |
| frame_fa_off | −0.2083 [−0.2531, −0.1646] | **동일** | yes → yes |
| cell_fpr_off | −0.0297 [−0.0372, −0.0222] | **동일** | yes → yes |
| cell_fpr_on_neg | −0.0296 [−0.0450, −0.0142] | −0.0281 [−0.0431, −0.0133] | yes → yes |
| **frame_recall_H** | +0.1250 [−0.0096, +0.2526] | **동일 (비트)** | no → no |
| **cell_recall_H** | +0.3546 [+0.2768, +0.4302] | **동일 (비트)** | yes → yes |
| frame_recall_E | −0.6000 [−0.7436, −0.4528] | **동일** | yes → yes |
| cell_recall_E | −0.3592 [−0.4556, −0.2626] | **동일** | yes → yes |
| frame_recall_V | −0.1889 [−0.2551, −0.1257] | **−0.1781 [−0.2395, −0.1185]** | yes → yes |
| frame_det_rate | −0.1682 [−0.2296, −0.1064] | **−0.1626 [−0.2193, −0.1046]** | yes → yes |
| band3/band4_cell_fpr_off | −0.0441 / −0.0667 | **동일** | yes → yes |

> **주목할 결과.** `SEED_TABLE.md:125`의 `cell_f1 +0.0403 [0.0001, 0.0786]` 유의 주장은
> D41에서 **씬-클러스터 재표집** 때문에 이미 철회됐다([−0.258, 0.205]). 교정 GT에서는
> **프레임 i.i.d. 부트스트랩만으로도** CI가 0을 포함한다([−0.0057, +0.0708]) — 하한이
> 0.0001이었으니 애초에 경계선이었고, 정답지가 165칸 늘자 넘어간 것이다.
> ⇒ **철회 결정이 독립적으로 재확인됐다.** aux의 생존 효과는 여전히
> **FA/정밀도 계열 + V/E/det 하락**뿐이며, `cell_recall_H +0.3546`은 프레임 i.i.d. 기준으로는
> 교정 후에도 비트 동일하게 유의하다(단 D41의 씬-클러스터 철회는 그대로 유효).

## 8.6 §6.4·§7.6 후속 큐 최종 상태

| # | 항목 | 상태 |
|---|---|---|
| 1 | YOLO 3런 교정 GT 재채점 | **✅ 완료 (§8.3)** — `SEED_TABLE.md:60,69-71,93-95` V 열 교체 필요, H·E·FA·precision 열 불변 |
| 2 | `rgb_s42_aux` 재채점 | **✅ 완료 (§8.5)** — `SEED_TABLE.md:116-119` V·f1·recall 교체, `:125` **유의 판정 변경**, `:131-133` 불변 |
| 3 | §6.3 색인대로 `METRICS.md`·`RESULTS_DRAFT.md` 편집 | 미착수 (편집은 본 작업 범위 밖) |
| 4 | `ACCOUNTING.md` §4.2 산술 오류 정정 append | 미착수 |
| 5 | v3 A/B 기준선 = §1.2 표 | 확정 |
| 6 | `fa_census_extract.py` `--corr --appendix` 해금 (§7.5) | 미착수 — 이제 **YOLO 계층도 함께** 해금 가능 |
| — | **F3 어댑터-프리 재계층화** | **✅ 완료 (§8.4)** — H 행 불변 확인, V·none_in_fov 행 교체 |

**추가로 확정된 §6.2-B(불변) 항목**: `SEED_TABLE.md:60` YOLO H/E = 0.000 · `:75-84` §4.2
어댑터 천장 문단 전체 · `:88-92` 각주 1(τ 0.10에서 H 1프레임/96) · `METRICS.md` §RT.3
어댑터-프리 0.066 · `RESULTS_DRAFT.md:344-350` — **실측으로 불변 확인, 수정 불필요**.
**추가로 확정된 §6.2-A(이동) 항목**: `SEED_TABLE.md:125` aux `cell_f1` 유의 판정
(**yes → no**, 프레임 i.i.d. 기준) · `:118-119` aux/base V·det·f1·recall·precision 행 ·
`METRICS.md:789-802,810-818` aux 블록 · `:734,737,744,756-758` YOLO V 계열 ·
`RESULTS_DRAFT.md:330-333,356-361,371-385` YOLO·aux V 인용.

test-core 위 **v2 계열 19런 전부가 교정 GT 기준으로 정렬됐다.** 남은 "구 GT 측정" 태그는 없다.
