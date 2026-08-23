# -*- coding: utf-8 -*-
"""
sceneL1_lateral_canal.py — NegObs 신규 씬 L1: 제방 마루 산책로 + **양측 개거 수로 낙차**
                            (Isaac Sim 4.5)

계열    : **측방 위험 (lateral)** · 생활권 = **제방·수변(뚝방)**
정본    : `experiments/v3_0823/RENDER_PLAN_V3.md` §2.0(공통 표준) · §2.3 표
          `sceneL1_lateral_canal` · §2.6(CUE_CLASS 사전 분류) · §3.1–3.2(test-ext 사양)
분리    : **test-ext** — v2·v3 **양 모델 모두 미학습**. 훈련·검증에 절대 넣지 않는다(§3.1).
          **4팔 전부 제작 의무**(DZ §4.2 `:243`) — A·B·C·D 완비.
밴드    : base · **LAT** = `d LogU[3,10] · h U[0.4,1.4]`  (씬당 팔당 48컷 · 4팔 합 192)

**이 씬이 존재하는 이유** (계획 §2.3 · 승용 결재 1 룰링):
  *"현 test 에 측방 씬이 **0개**라 섹터 분해능(5→10)·밴드 세분을 '실용 정보량' 기준으로
    재론할 측정 기반이 원리적으로 없다."*
  ⇒ 이 씬의 산출물은 **폴라 GT 의 섹터 분포**다. `gridspec_v1` 의 5섹터는
  A [+18.66°, +31.10°] · B [+6.22°, +18.66°] · C [−6.22°, +6.22°] ·
  D [−18.66°, −6.22°] · E [−31.10°, −18.66°] 이고, **A·E 가 측방 섹터**다.
  이 씬은 위험 질량을 **A·E 에 몰아넣고 C 를 구성상 비운다**(아래 §섹터 설계).

────────────────────────────────────────────────────────────────────────────
씬 조립 공식 (4요소 — 브리프 §2.0)
  ① 경로   제방 진입 광장 → 2단 오름 → **제방 마루 산책로**(유효폭 3.60 m, z 0.00)
  ② 위험   산책로 **양 측방**의 콘크리트 **개거(開渠) 수로** — 낙차 **1.500 m**
           남측 = 농업용 **도수로**(상시 통수 · 수심 0.12) / 북측 = 제방 **배수 구거**(자갈 바닥)
  ③ 단서   양측 스테인리스 난간 · **잔디 풀 경계** · 점형블록 · 나이징 · 재질전이 ·
           수로 관리 표지 · 광장 가로수/수목보호격자 · 맨홀 · 빗물받이 · 줄눈 · 볼라드 · 시선유도봉
  ④ 은닉   **없다 — 이 씬은 은닉 씬이 아니다.** 낙차는 보인다. 연구 변수는 *"보이는 낙차가
           폴라 격자의 **어느 섹터**에 실리는가"* 이며, 그것이 §2.3 이 요구한 측정 기반이다.

*"주변 환경은 장식이 아니라 단서 ③ 그 자체다"* — 수로만 파 놓으면 이 씬은 실패다.

**왜 양측인가** (설계 판단 · 보고에 명시): 브리프 문면은 *"경로 **측방** 수로 낙차 1.5 m"*
로 수로를 단수로 적지만, 같은 표의 **섹터 목표는 "A·E"** 다. 한쪽만 파면 위험 질량이
E(또는 A) **한 섹터에만** 실려 좌우 대칭 측정이 불가능하고, yaw 지터(trunc-N(0,8,±20))가
그 한 섹터를 격자 밖으로 밀 때 표본이 통째로 사라진다. **제방 마루는 원래 양쪽이 다
사면·수로**이므로(하천측 배수 구거 + 제내지측 용수 도수로) 양측 개거는 부지의 실제 구성이며,
그렇게 지어야 A·E 두 섹터가 동시에 채워진다. 두 수로는 **재질·바닥·통수 상태를 달리해**
좌우 거울상으로 읽히지 않게 했다(남 = 물 있는 콘크리트 라이닝 / 북 = 마른 자갈 바닥).

────────────────────────────────────────────────────────────────────────────
좌표계 · 횡단면 (walk axis = +X, Z-up, m. 카메라는 x = −d, |y| ≤ 0.90 에서 +X 를 본다)

   y
  +40.0 ┌──────────────────────────────────────────────────────┐
        │  하천 둔치 (갈대 군락 |y| 6.2…8.6)          z = 0.000 │  FarBankN
  +5.70 ├──────────────────────────────────────────────────────┤
        │  **북측 배수 구거** — 자갈 바닥 z = −1.500            │  CanalN  ← ② 위험
  +3.54 ├──────────────────────────────────────────────────────┤
  +3.30 │  개거 갓돌 z = 0.000 (flush)   · 난간 |y| = 3.16      │
        │  잔디 녹지대 (**풀 경계**)      z = 0.000             │  VergeN
  +1.80 ├──────────────────────────────────────────────────────┤
   0.00 │  ① 제방 마루 산책로 유효폭 3.60   z = 0.000          │  Walk
  −1.80 ├──────────────────────────────────────────────────────┤
        │  잔디 녹지대                    z = 0.000            │  VergeS
  −3.30 │  개거 갓돌 z = 0.000 (flush)   · 난간 |y| = 3.16      │
  −3.54 ├──────────────────────────────────────────────────────┤
        │  **남측 용수 도수로** — 수면 z = −1.500 (수심 0.12)   │  CanalS  ← ② 위험
  −5.70 ├──────────────────────────────────────────────────────┤
        │  논 지반 · 밭 경계 관목                    z = 0.000 │  FarBankS
  −40.0 └──────────────────────────────────────────────────────┘

  종단(보행축): x ≤ −8.40 → z = −0.32 (제방 진입 광장) · x −8.40…−7.70 → **2단 오름**
                (라이즈 0.16 · 트레드 0.35) · x ≥ −7.70 → z = 0.000 (제방 마루)

  **낙차 = 0.000 − (−1.500) = 1.500 m** (브리프 "측방 수로 낙차 1.5 m" 준수 · 양측 동일)
  개거 개구 폭 = 5.46 − 3.54 = **1.92 m** (콘크리트 3면 개거의 표준 폭대)

────────────────────────────────────────────────────────────────────────────
**섹터 설계** — 이 씬의 유일한 설계 자유도이자 §2.3 의 요구 그 자체

카메라 E = (−d, y_c), 발자국 셀 (x, y). u ≡ x + d 로 두면 방위각 az = atan2(y − y_c, u).
`gridspec_v1` 의 경계는 tan(18.66°) = 0.3378 · tan(31.10°) = 0.6036 이므로

    A·E (측방)  ⇔  |y| / u ∈ [0.3378, 0.6036]
    B·D         ⇔  |y| / u ∈ [0.1090, 0.3378]
    C  (정면)   ⇔  |y| / u ≤ 0.1090
    그리고 반경 √(u² + y²) < 12.0 (격자 외반경)

발자국이 |y| ∈ [3.54, 5.46] 이므로 (y_c ≈ 0 근사):

  | 섹터 | u 범위 (기하) | 반경 < 12 로 잘린 뒤 | 폭 |
  |---|---|---|---|
  | **A·E** | [3.54/0.6036, 5.46/0.3378] = [5.87, 16.16] | **[5.87, 10.9]** | **5.0 m** |
  | B·D | [3.54/0.3378, 5.46/0.1090] = [10.48, 50.1] | [10.48, 11.5] | 1.0 m |
  | **C** | u ≥ 3.54/0.1090 = **32.5** | **∅** (반경 32.7 > 12) | **0** |

⇒ **C 섹터는 씬 기하로는 영구히 비어 있다** — *"경로 정면은 무해"*(브리프)가 기하
   항등식으로 보장된다. 단 위 표는 **카메라가 보행축을 정확히 향할 때**(yaw = 0)의 것이고,
   실제 샘플러는 yaw ~ trunc-N(0, 8°, ±20°) 를 뽑으므로 카메라 회전만큼 측방 위험이
   중앙 쪽으로 밀려 들어온다. CPU 자기검사가 **yaw≡0 과 yaw 지터 두 판**을 나란히 인쇄해
   그 구분을 기계가 보이게 한다 `[설계 시 MC 실측: C 셀 점유율 yaw≡0 **0.0000** ·
   yaw 지터 0.036]`. **C 에 실리는 몫은 씬 기하가 아니라 카메라 자세의 기여**이며, 그것을
   섹터 분해능 재론(5→10)의 교란으로 분리해 읽는 것이 이 씬이 제공하는 측정 기반의 일부다.
   그리고 측방 A·E 의 u 폭이 B·D 의 **5 배**이므로 위험 질량이 A·E 에 집중한다.
   LAT 밴드 d ∈ [3, 10] · 격자 x ∈ [−2, 14] ⇒ u ∈ [d−2, d+14] 이므로 A·E 창
   u ∈ [5.87, 10.9] 는 **d 전 구간에서 격자 안에 존재한다**
   (d = 3 → x ∈ [2.87, 7.90] · d = 10 → x ∈ [−2.00, 0.90]).

`_sector_hist()` 가 이 예측을 **실제 샘플러**로 몬테카를로 재계산하고 CPU 자기검사가
매 실행 인쇄한다 — 횡단면을 만지면 즉시 드러난다. 렌더 후에는 `h12_gates.py --lateral`
이 **라벨의 `polar_gt` 로 같은 표를 실측**해 이 예측을 기계 반증한다.

**은닉 없음 선언**: 이 씬에는 `BermCrest`·`BendWall` 같은 가림체가 **없다**. strict-H 수율
목표도 없다(계획 §3.2 표의 paired-H 열이 "—"). `h67_yield.py` 를 이 씬에 돌리면
*"미달 — 씬 기하 개정 필요"* 를 인쇄하는데 **그 문장은 이 씬에 대해 무의미하다** —
이 씬의 판정은 섹터 분포와 4팔 VG 게이트다.

────────────────────────────────────────────────────────────────────────────
**스텝 게이트** — 이 씬이 라벨러에서 발견한 것 (개정 R2 의 사유 · 계획 반영 필요)

`labeler.step_gate` (D10) 는 발자국 성분을 **근접 경계**(near boundary)로만 살린다:
경계 셀 = *"카메라 쪽 4-이웃이 보행 가능 지면인 발자국 셀"* 이고, "카메라 쪽"은
`_outward()` 가 `rint(dx/n), rint(dy/n)` 로 **8이웃에 양자화**한 방향이다
(`labeler.py:285-309`). 경계가 하나도 없으면 그 성분은 통째로 버려진다.

**측방 위험은 이 양자화에 걸린다.** 개거는 보행축과 **나란히** 달리므로, 카메라에서
개거 안쪽 립까지의 방향은 |dy| / n < 0.5 가 되는 순간 `oy = 0` 으로 반올림되고 이웃이
**같은 개거 셀**이 되어 경계가 사라진다. 임계는 닫힌 식으로 나온다 — 격자 서단
x₀ = −2 에서

    n ≤ 2·|y_lip|   ⇔   (d + x₀)² + y_lip² ≤ 4·y_lip²   ⇔   **d ≤ −x₀ + √3·y_lip**

    y_lip = 3.54 ⇒ **d ≤ 8.13 m**

**실측이 이 식과 정확히 맞았다** `[260823_v3p5_h3l1probe_A · sceneL1 · 8포즈]`:
    d 4.98 / 7.15 / 7.32 / 7.70 → `cells_kept` **25,038** (양측 전부)
    d 8.67 (y_c +0.76)         → `cells_kept` **12,519** (한쪽만 — y 오프셋이 남측만 살렸다)
    d 8.50 · 8.69 (y_c ≈ 0)    → `cells_kept` **0** ⇒ tier `none_in_fov`, **GT 전무**
즉 LAT 밴드(d 3–10)의 상단 25 % 가 *"낙차가 3.5 m 옆에 있는데 GT 가 0"* 인 프레임이 된다.
이것은 씬 결함이 아니라 **계기의 사각**이며, 방치하면 **거짓 음성 GT** 를 만든다.

**조치 (개정 R2)**: 개거를 가로지르는 **횡단 농로 복개 2개소**(x = −1.40 · 7.60 · 폭 1.20 m)를
둔다. 복개 상면은 마루와 같은 z = 0.000 이므로 발자국이 아니고 `~fp` 이며, 그 **동쪽
가장자리**가 −x 방향(= 카메라 쪽) 이웃이 보행 가능한 셀을 만든다 ⇒ 근접 경계가 **d 와
무관하게** 존재한다. 스텝 게이트의 안쪽 레이는 그 립에서 1.0 m 안으로 −1.50 m 를 보므로
0.30 m 임계를 여유 있게 넘긴다. 제방을 가로지르는 농로가 양측 수로를 복개하고 지나가는
것은 농업용 개거의 **표준 구성**이므로 이 장치는 계기를 위한 소품이 아니라 부지의 사실이다.

> **계획 반영 필요**: 이 사각은 `sceneL2_lateral_ditch` 를 포함한 **모든 측방 씬**에
> 그대로 적용된다. 씬마다 복개를 두는 것은 대증요법이므로, `_outward` 를 8이웃 양자화
> 대신 **성분 경계 전수 스캔**으로 바꾸는 것이 근본 해법이다(비용은 CPU 뿐이다).

────────────────────────────────────────────────────────────────────────────
**개거 가시성** — 가림체가 없는데도 낙차 내부는 거의 보이지 않는다 (설계 확인)

눈 E = (−d, y_c, h) 에서 개거 안의 점 (x, y_t, z_t) 로 가는 시선은 **근단 갓돌**
(|y| = 3.54, z = 0) 을 반드시 지난다. 그 교차점의 z 가 0 이상이어야 갓돌에 막히지 않는다:

    frac = (3.54 − y_c) / (|y_t| − y_c)  ≈ 0.648  (y_t = 5.46 · y_c ≈ 0 · **x 와 무관**)
    z_cross = h + (z_t − h)·frac ≥ 0   ⇔   z_t ≥ −0.543·h

    h 0.4 → 보이는 깊이 **0.22 m** · h 1.0 → 0.54 m · h 1.4 → **0.76 m**  (낙차는 1.50 m)
    바닥(−1.50)이 보이려면 h ≥ **2.77 m** — 이 씬의 어느 밴드에도 없는 눈높이다.

⇒ **보행 눈높이에서 개거는 "먼 벽 상단 0.2–0.8 m + 그 아래 폐영역"으로만 나타난다.**
   낙차의 14–51 % 만 화면에 있고 나머지는 어둠이다. 가림체 없이도 낙차가 저역 어두운
   슬롯으로 축약되는 이 현상이 **음성 장애물의 정의 그 자체**이며, 그래서 이 씬은
   "은닉 씬이 아니지만 쉬운 씬도 아니다". CPU 자기검사가 위 수치를 매 실행 인쇄한다.

────────────────────────────────────────────────────────────────────────────
프림 위생 · 데이텀 (CUE_COVERAGE §4-4 (2)(3)(4))

1. 단서 빌더가 `if cfg["hazard_*"]` 안에 있는 것은 **0개**. 조립부 hazard 분기는 2줄뿐이다.
2. **모든 `cue_*` 프림은 |y| ≤ 3.22 또는 |y| ≥ 6.20 에 선다.** 낙차 발자국
   (|y| ∈ [3.54, 5.46])을 덮는 단서 프림이 **0개**이므로 라벨러 `cells_raw`·`polar_gt` 는
   `cue_*` 토글에 **구성상 불변**이다(VG-01 의 실효 내용). 자기검사 (4) 가 스테이지 전수
   AABB 로 매 조립마다 확인한다.
   — 특히 **수관(canopy)을 개거 위에 두지 않는다**: 높이맵은 수직 레이의 최초 히트이므로
     개거 위를 덮은 수관은 그 셀의 z 를 수관 top 으로 만들어 **발자국을 지워 버린다**.
     가로수는 전부 진입 광장(x ≤ −8.4)에, 갈대는 전부 |y| ≥ 6.20 에 있다.
3. 카메라 데이텀 스트립 `x ∈ [−12.05, −1.15] · |y| ≤ 0.95` 안에서 상면을 움직이는 토글
   프림은 점형블록(4 mm)·나이징(12 mm)·지면문양(≤ 8 mm)뿐 — 전부 `datum_tol`(≤ 0.02 m)이고
   `datum_fail` 은 **0건**이다.
4. **void 커버리지 1.0** — 개거는 벽체·인버트·통수면/자갈이, 그 밖은 산책로·녹지대·갓돌·
   외안 지반이 x ∈ [−2, 14] × y ∈ [−8, 8] 을 빈틈없이 덮는다. 개방 바닥 0.
5. **반사실 채움면은 정확히 z = 0.000** 이고 외안 지반도 z = 0.000 이다 ⇒ hazard OFF 팔에서
   횡단면이 **완전 평탄**해지고 `z_off − z_on` 이 개거 개구에서만 0.30 을 넘는다.
   (SCENE_TEXT_BUILD §6 「법칙 2」의 반대 방향 적용 — 채움면보다 낮은 구조물을 두지 않았다.)

표준법: 법1 온전 상태만 · 법2 법정 제식 표지 1매 · 법4 난간(낙차 1.5 m > 1.2 m 법정 의무)·
볼라드·측구는 기능 필수, `cue_delineator` 기본 OFF · 법5 차량·계절소품 0 · 법6 신규 재질
역할 0 · 법7 `cue_*` 최대 융기 12 mm · 법8 수치 주석에 근거 태그.

실행
    unset PYTHONPATH VIRTUAL_ENV; conda activate env_isaaclab; export PYTHONNOUSERSITE=1
    python scenes/main/sceneL1_lateral_canal.py                 # GUI 룩체크
    NEGOBS_SMOKE=1 python scenes/main/sceneL1_lateral_canal.py  # CPU 조립 스모크
데이터 렌더 진입점 (신설 씬은 AZ 원장 등재 전까지 이 경로가 유일 — CUE_COVERAGE §4-4 (6)):
    python experiments/v3_0823/code/h67_probe.py --scene sceneL1 --run <stamp> ...
"""

import os
import sys
import math
import json
import random
import datetime

import scene_common as sc
import ground_kit as gk
import infra_kit as ik


# [계획 §2.0] 생활권 = 제방·수변. 계절은 **한여름** — 같은 생활권의 sceneH1(초가을)·
#   sceneH6(여름 한강 둔치)와 톤·부지를 분리한다(아래 부지 분리 표).
SEASON = "midsummer"


# ===========================================================================
# [A0] CUE_CLASS — 렌더 **전** 사전 분류 (RENDER_PLAN_V3 §2.6 / ACCOUNTING §2-6)
# ===========================================================================
CUE_CLASS = {
    "cue_railing":         "decorative",   # 양측 스테인리스 파이프 난간 (낙차는 개거가 정의)
    "cue_tactile":         "decorative",   # 볼라드 전면 + 2단 상단 점형블록 (proud 4 mm)
    "cue_nosing":          "decorative",   # 2단 오름 논슬립 띠 (proud 12 mm) — 팔 불변 지형
    "cue_material_break":  "decorative",   # **재질 재바인딩 전용** — 프림 집합 불변
    "cue_sign":            "decorative",   # 수로 관리 통로 출입 제한 법정 표지 1매
    "cue_scene_dressing":  "decorative",   # 갈대 군락·밭 경계 관목·벤치·배수펌프장·마을 원경
    "cue_shadow_caster":   "decorative",   # 광장 가로수 + 녹지대 가로등주 — 그림자 밴드
    "cue_manhole":         "decorative",   # 광장 배수 맨홀 (flush)
    "cue_tree_grate":      "decorative",   # 광장 수목보호격자 (flush)
    "cue_slab_joint":      "decorative",   # 콘크리트 수축줄눈 (recess 3 mm)
    "cue_drainage":        "decorative",   # 빗물받이 (광장 2 + **산책로 2**, flush)
    "cue_bollard":         "decorative",   # 제방 진입 차량 억제 볼라드 4본 (피치 1.50)
    "cue_delineator":      "decorative",   # 반사 시선유도봉 (기본 OFF — 법4 "비움이 기본값")
    # ── 토글 금지 목록 (구조물). 어떤 cue_* 도 이 프림들을 참조하지 않는다 ──────────
    "_structural":         ["CanalS", "CanalN", "FarBankS", "FarBankN",
                            "Ground/Walk", "Ground/Verge"],
}


# ===========================================================================
# [A] SCENE_CONFIG — **표준 장비 16키** (RENDER_PLAN_V3 §2.0 · CUE_COVERAGE §4-4 (1))
# ===========================================================================
SCENE_CONFIG = {
    # ── ② 위험: 유일한 기하 토글 ────────────────────────────────────────────
    #   False → 양측 개거(갓돌·벽체·인버트·통수면·자갈)가 사라지고 산책로 레벨(z 0.000)의
    #   평탄 지면이 |y| ∈ [3.30, 5.70] 를 채운다(반사실 보행 가능면 z_off = 0.000).
    "hazard_stairs":      True,
    # ── ③ 단서: 공통 6키 ────────────────────────────────────────────────────
    "cue_railing":        True,   # 낙차 1.50 m > 1.20 m ⇒ 난간 법정 의무 (법4 통과)
    "cue_tactile":        True,   # 점형블록 — 볼라드 전면 0.30 m + 2단 상단
    "cue_nosing":         True,   # 2단 오름 논슬립 띠
    "cue_material_break": True,   # 산책로 = 컬러 콘크리트 판석 / 광장 = 콘크리트 타설
    "cue_sign":           True,   # 수로 관리 통로 표지 (법2 — 법정 제식만)
    "cue_scene_dressing": True,   # 갈대·관목·벤치·원경을 한 번에
    # ── v3 신설 3키 (FA_REALITY §2) ─────────────────────────────────────────
    #   `cue_shadow_caster` 부작용 경보(§2.0): 음성 씬에만 넣으면 "그림자 = 안전"이라는
    #   역지름길이 생긴다. **양성 씬인 이 씬에도 동일 비율로** 배치한다.
    "cue_shadow_caster":  True,
    "cue_manhole":        True,   # 갭 1위 (25.0)
    "cue_tree_grate":     True,   # 갭 2위 (20.0)
    # ── FA_REALITY §2 승격 후보 4키 ────────────────────────────────────────
    "cue_slab_joint":     True,   # 갭 5위 — 콘크리트 수축줄눈
    "cue_drainage":       True,   # 갭 3위 — 빗물받이
    "cue_bollard":        True,   # L2 — 제방 진입 차량 억제 볼라드
    "cue_delineator":     False,  # L12 — 반사 시선유도봉. 기본 OFF(법4), 코드 경로 상시 보유
    # ── 팔 제어 2키 ─────────────────────────────────────────────────────────
    "keep_dressing":      False,
    "placebo_remove":     False,
}


# ===========================================================================
# [B] PARAMS — 전 수치. 횡단면은 파일 상단 표와 **한 글자도 어긋나지 않는다**
# ===========================================================================
PARAMS = dict(
    terrain=dict(
        y_far=40.0, base_z=-2.60,
        # 진입 광장 (전부 높이맵 격자 x ≥ −2 **밖**이라 GT 와 무관하다)
        approach=dict(x0=-34.0, x1=-7.70, z=-0.34),
        plaza=dict(x0=-24.20, x1=-8.40, y_half=4.60, z=-0.32),
        # [규격] 라이즈 0.16 · 트레드 0.35 — 조경설계기준 완경사 계단(R 0.12~0.18 · T 0.30~0.60)
        step=dict(x0=-8.40, riser=0.16, tread=0.35, n=2, y_half=4.60),
        # 제방 마루 산책로 — 유효폭 3.60 m [규격 보도 유효폭 ≥ 2.0 m · 자전거 겸용 3.0 m]
        walk=dict(x0=-7.70, x1=40.0, y_half=1.80, z=0.00),
        verge=dict(y0=1.80, y1=3.30),                  # 잔디 **풀 경계** (브리프 명시)
        farbank=dict(y0=5.70, z=0.00),
    ),
    # ── 위험 (hazard_stairs 전속) — 양측 개거 ───────────────────────────────
    hazard=dict(
        x0=-7.94, x1=40.0,
        coping=dict(w=0.24),          # 갓돌 폭 (내측 3.30…3.54 · 외측 5.46…5.70)
        y_lip=3.54, y_toe=5.46,       # 개구 폭 1.92 m
        invert_z=-1.62,               # 콘크리트 인버트 상면
        fill_top=-1.50,               # 통수면(남) · 자갈 바닥(북) 상면 = **낙차 바닥**
        wall_bot=-2.30,
        head_x=-7.94,                 # 개거 시점 흉벽
        # [개정 R2] **횡단 농로 복개 2개소** — x = −1.40 · 7.60 (폭 1.20 m).
        #   제방을 가로질러 남측 농지에서 북측 둔치로 넘어가는 농로가 양측 개거를
        #   복개하고 지나간다. 실제 농업용 개거의 표준 구성이고, **동시에 라벨러
        #   D10 스텝 게이트가 이 씬을 볼 수 있게 하는 유일한 장치**다 — 사유는 파일
        #   상단 §스텝 게이트 참조. 복개 슬래브 상면은 마루와 같은 z = 0.000 이므로
        #   그 셀은 어느 팔에서도 발자국이 아니다.
        culverts=(-1.40, 7.60), culvert_w=1.20,
        # [computed] 낙차 = 0.000 − (−1.500) = **1.500 m** (양측 동일)
        fill=dict(y0=3.30, y1=5.70, z=0.00),   # hazard=False 반사실 채움면
    ),
    # ── ③ 단서 파라미터 ─────────────────────────────────────────────────────
    #   전부 |y| ≤ 3.22 또는 |y| ≥ 6.20. 낙차 발자국(|y| ∈ [3.54, 5.46])을 덮는 단서 0개.
    # [개정 R1] `post_a` 0.12 → **0.075**(75 mm 각관) · `cap_t` 0.05 → 0.04.
    #   1차 스모크에서 12 cm 각기둥 + 금속 알베도 0.70 이 **흰 기둥 열**로 읽혔다.
    #   실제 개거 난간은 50~75 mm 각관/파이프다. 기하 여유는 그대로다 —
    #   난간 외측 |y| 가 3.22 → 3.1975 로 오히려 발자국에서 더 멀어진다.
    rail=dict(y=3.16, x0=-7.60, x1=34.0, post_a=0.075, post_pitch=2.00,
              post_h=1.10, cap_t=0.04, rail_r=0.024, top_z=1.10, mid_z=0.62),
    # [규격·정정 R4 · D82ⓐ] 난간 방호면 상단 **1.10 m** — 근거는 **「도로안전시설 설치 및
    #   관리지침」 2.3.3 나**(난간 높이 **110 cm 표준**). **구 주석의 "건축법 시행령 §40"
    #   은 오인용**이다(§40 은 옥상광장·2층 이상 노대 전용, 값 1.2 m)
    #   [`Docs/surveys/cue_arrangement_survey.md` §1.1 정정 상자].
    #   또한 **측구(L·U형) 개거에는 난간 규정이 없다** [동 §1.3 (g) `[확인 — 부재]`:
    #   안전 대책은 전적으로 *"덮개 + 격자 2 cm 이하"*]. 이 난간은 법정 의무가 아니라
    #   **관행**이고, 그래서 "난간 = 낙차" 지름길을 만들지 않는다.
    #   [CUE_REGULATION_BASIS §3.1 · §5]
    #   스테인리스 각기둥 + Ø0.048 2단 횡대. sceneH1(화강석 각기둥 3단 · 피치 1.80)과
    #   재질·단수·피치가 모두 다르다.
    # ── [개정 R4 · D82ⓐ 설치-규정 감사] 점형(경고) 2밴드 — **서로 다른 위험 경계 2곳**
    #   이므로 밴드 수는 정합이다(볼라드 열 / 2단 상단). 두 밴드 모두 치수를 고쳤다.
    #   근거 ① 이격 — 「교통약자의 이동편의 증진법 시행규칙」 **별표1**(이동편의시설의
    #     구조·재질 등에 관한 세부기준) "위험장소 **0.3 m 전면**" · 블록 규격 0.3×0.3 m ·
    #     점형 = **경고**(돌출점 36개) / 선형 = **유도**(돌출선 4줄) 역할 구분.
    #   근거 ② 세로폭 — 「도로안전시설 설치 및 관리지침 : 장애인 안전시설」 6.5.2 2):
    #     점형블록 세로폭 **30~90 cm 범위, 60 cm 표준**(0.30 m 유닛 2매). 같은 지침
    #     6.6.7 가 는 더 구체적이다 — *"보행 동선에서 **위험물과 마주치게 되는 방향에는
    #     60 cm 폭**으로 점형블록을 설치하고, 보행 동선과 **평행한 방향으로는 30 cm 폭**"*.
    #     이 두 밴드는 **접근 동선을 정면으로 가로지르므로 60 cm** 가 표준값이다.
    #     구 0.40 m 는 300 mm 모듈의 정수배가 아니라 **시공 불가 치수**였다.
    #   근거 ③ 볼라드 전면 — 「**보행안전 및 편의증진에 관한 법률 시행규칙**」 별표1
    #     제10호 바: 자동차 진입억제용 말뚝의 **0.3 m 앞쪽**에 점형블록 `[의무]`.
    #     (구 「교통약자법 시행규칙」 별표2 제7호 바에 있던 조항이 **삭제·이관**된 것으로,
    #      수치는 동일하고 문구만 "전면 → 앞쪽"으로 바뀌었다. 웹 검증 2026-08-24.)
    #
    #   (a) 볼라드 전면 밴드: 세로 0.40 → **0.60 m** (y −4.00…−3.40, 볼라드 열
    #       y = −4.30 에서 0.30 m 전면). 광장 y_half 4.60 안이라 여유 있게 앉는다.
    #   (b) 2단 상단 밴드: **이격 0.00 → 0.30 m** — 구 배치(x −7.70…−7.30)는 계단 코
    #       x = −7.70 **에서 곧바로** 시작해 별표1 의 "0.3 m 전면"을 **위반**했다.
    #       세로 0.40 → **0.60 m** ⇒ x −7.40…−6.80.
    #       가로폭도 |y| 2.60 → **1.80** 으로 줄인다: 구 밴드는 |y| ∈ [1.80, 2.60] 구간이
    #       `Ground/Verge{S,N}`(잔디 녹지대) **위**에 얹혀 있었다. 점자블록은 포장면에만
    #       시공되고 잔디 위에는 시공되지 않는다 — 산책로 유효폭(±1.80)이 곧 "대상
    #       시설의 폭"이다(국도 실무요령 7.5 가로폭 조항).
    tactile=dict(bollard=(-13.85, -4.00, -8.85, -3.40),   # 볼라드 전면 0.30 m · 세로 0.60
                 crest=(-7.40, -1.80, -6.80, 1.80),        # 2단 상단 0.30 이격 · 세로 0.60
                 proud=0.004),
    nosing=dict(width=0.055, proud=0.012),          # [계획] 노징 12 mm
    sign=dict(x=-10.20, y=3.40, yaw=180.0, pole_h=2.05, w=0.56, h=0.56),
    # [규격] 볼라드 h 0.8~1.0 · φ0.10~0.20 · 간격 ~1.5 m · 반사띠 (user_feedback_v5_1 §2)
    #   광장 남측 보차도 경계선(y = −4.30) 위 4본. 피치 **1.50 m** 법정치를 한 번도 깨지
    #   않으며 카메라 데이텀 스트립(|y| ≤ 0.95)을 한 본도 침범하지 않는다.
    #   위치 지터 없음 — J-3/J-5(07-30) 배치 지터 폐지 · LINT-10 정적 검사 대상.
    bollard=dict(y=-4.30, xs=(-13.60, -12.10, -10.60, -9.10),
                 r=0.075, h=0.90, band_z=0.68, band_t=0.09),
    delineator=dict(x=-13.20, ys=(-2.40, 2.40), r=0.041, h=0.80),
    gkit=dict(
        # (a) 제방 진입 광장 — 맨홀 · 빗물받이 · 수축줄눈. 격자(x ≥ −2) 밖이다.
        plaza_region=(-24.10, -4.50, -8.45, 4.50),
        plaza_manholes=[(-11.20, 2.40), (-12.90, -2.40)],
        plaza_gullies=[(-9.60, -2.60), (-13.10, 1.30)],
        tree_grates=[(-22.90, 3.50), (-15.90, 3.50), (-8.90, 3.50)],
        # (b) 제방 마루 산책로 — 수축줄눈 + **빗물받이 2**(격자 안, flush).
        #     `plan_ground` 의 `edges` 는 **횡단 낙차 모서리**의 선언인데 이 씬의 낙차
        #     모서리는 보행축과 **나란한 종단선**(|y| = 3.54)이다. 없는 횡단 모서리를
        #     지어내면 B7(GT-E2)은 검사가 아니라 허구가 되므로 `edges=()` 로 남긴다 —
        #     그리고 실제로 이 씬의 횡줄눈은 낙차 모서리와 **직교**하므로 대리선이
        #     될 수 없다(대리선 위험은 종단선에 있고, 종단 줄눈은 이 프로파일이 만들지 않는다).
        walk_region=(-7.66, -1.76, 13.90, 1.76),
        walk_gullies=[(2.40, -1.55), (8.60, 1.55)],
    ),
    shadow=dict(
        # [FA_REALITY §2 4위] 그림자 밴드 캐스터. **양성 씬에도 동일 비율**(§2.0 경보).
        #   가로수는 전부 **진입 광장**(x ≤ −8.4)에 — 녹지대에 심으면 수관이 개거 위를
        #   덮어 그 셀의 높이맵이 수관 top 이 되고 **발자국이 지워진다**(위생 2).
        #   녹지대에는 수관 없는 **가로등주**만 세운다(φ0.144 · |y| = 2.50).
        trees=[(-22.90, 3.50), (-15.90, 3.50), (-8.90, 3.50)],
        tree_h=6.8,
        lamps=[(-3.60, -2.50), (4.40, 2.50), (12.40, -2.50)],
        lamp_h=4.4, lamp_arm=0.95,
    ),
    dress=dict(
        # [개정 R1] 갈대·관목을 |y| ∈ [6.20, 8.60] → **[9.20, 13.0]** 으로 물린다.
        #   1차 스모크에서 두 띠가 개거 **바로 뒤에 붙은 초록 벽**으로 읽혀 (ⓐ) 개거가
        #   낙차가 아니라 화단 경계처럼 보이고 (ⓑ) 두 수로의 좌우 차이가 초록에 묻혔다.
        #   9.20 은 높이맵 격자(|y| ≤ 8) **밖**이므로 VG-01 의 off-print 셀도 함께 사라진다.
        #   갈대 — 북측 하천 둔치 / 관목 — 남측 논 경계.
        reed_bands=[(-6.0, 9.20, 34.0, 13.0)],
        reed_h=1.10,
        hedge=[(-6.0, -13.0, 34.0, -9.20)],
        shrub_h=0.85,
        #   벤치 yaw 는 **축값만** — J-3/J-5 지터 폐지(spec §1.2)를 LINT-7 이 강제한다.
        benches=[(-12.60, -2.20, 90.0), (-9.80, 2.20, 270.0)],
        # 원경(placebo 물량군) — **전부 높이맵 격자(x ≤ 14 · |y| ≤ 8) 밖**이라 라벨 무관.
        # [개정 R1] 원경 물량을 줄이고 뒤로 물린다 — 1차 스모크에서 볕받은 콘크리트
        #   매스가 화면 상단의 큰 흰 판으로 읽혔다(v5.1 §4 순백 대면적 취지).
        #   높이·폭을 줄이고 x 를 밀어 화각 점유를 낮춘다. 전부 격자 밖이라 GT 영향 0.
        pumphouse=[("P0", 34.0, 40.0, -14.0, -8.0, 4.8)],
        village=[("V0", 44.0, 56.0, 11.0, 24.0, 6.4),
                 ("V1", 50.0, 62.0, -30.0, -17.0, 5.6)],
    ),

    # ── 재질 3단 (realism_v1_final §84) ─────────────────────────────────────
    material=dict(
        scale=dict(concrete_floor=1.70, plaza_lower=1.60, concrete_wall=2.0,
                   granite_dark=1.80, grass=1.4, gravel=1.10, tactile=0.3),
        grass_tint=(0.38, 0.52, 0.24),      # 한여름 (H1 초가을 0.46/0.50/0.27 과 다름)
        plaza_tint=(0.60, 0.595, 0.58),     # 진입 광장 콘크리트 타설
        walk_tint=(0.64, 0.62, 0.58),       # 산책로 컬러 콘크리트 판석
        # [개정 R1] 남·북 갓돌을 **다른 재질**로 나눈다. 통수면은 스침각에서 보이지
    #   않으므로(아래 §개거 가시성) 두 수로의 차이가 갓돌·바닥 재질에만 남는다 —
    #   남측 용수 도수로 = 화강석 갓돌 / 북측 배수 구거 = 콘크리트 갓돌. 실제 구성이다.
        coping_tint=(0.62, 0.615, 0.60),    # 남측 개거 갓돌 (화강석)
        coping_tint_n=(0.545, 0.545, 0.535),  # 북측 개거 갓돌 (콘크리트)
        wall_color=(0.300, 0.300, 0.292), wall_rough=0.66,   # alb_max 0.34 이하
        invert_tint=(0.52, 0.515, 0.50),
        gravel_tint=(0.49, 0.48, 0.455),
        water_color=(0.058, 0.076, 0.070), water_rough=0.17,
        # [v7 ruling · scene12] 수면 rough 하한 0.14 — 무풍 완전거울("인피니티 풀") 방지.
        # [look 층] 재질 프림 이름이 클래스를 정한다 — `RailStone`/`GranitePost` 가 metal
        #   로 분류된 사고가 두 번 있었다(H67 R3 · H12 R1). 이 씬의 난간은 **실제로
        #   스테인리스**이므로 `Looks/RailSteel` 이 metal 로 떨어지는 것이 옳다.
        # [개정 R1] 0.70 → 0.58. look 층 metal 클래스 상한은 0.50 이지만 1차 스모크의
        #   난간 열이 화면에서 가장 밝은 대면적이었다.
        rail_color=(0.58, 0.59, 0.61), rail_metal=0.82, rail_rough=0.33,
        nosing_color=(0.41, 0.39, 0.35), nosing_rough=0.70,
        band_color=(0.80, 0.52, 0.05),      # 볼라드 반사띠 = 안전 황색(면적 小)
        bollard_color=(0.60, 0.61, 0.62), bollard_metallic=0.55, bollard_rough=0.38,
        pole_color=(0.24, 0.24, 0.26), pole_metallic=0.6, pole_rough=0.5,
        lamp_color=(0.78, 0.78, 0.75), lamp_rough=0.4,
        wood_color=(0.31, 0.21, 0.13), wood_rough=0.85,
        reed_tint=(0.46, 0.50, 0.26),
        canopy_a=(0.029, 0.050, 0.018), canopy_b=(0.040, 0.064, 0.024),
        canopy_rough=1.0,
        # [v5.1 §4 · 순백 대면적 금지] 원경은 concrete 클래스(`BgConcrete`)에 얹어
        #   알베도 상한 0.34 아래로 내린다(H6 R4 교훈).
        backdrop_color=(0.235, 0.235, 0.232), backdrop_rough=0.74,
        iron_color=(0.14, 0.14, 0.15), iron_metallic=0.55, iron_rough=0.62,
    ),

    # ── 조명 (L0–L7 카탈로그. 생산 3종 = L0·L5·L7) ─────────────────────────
    light=dict(
        hdri="qwantani_noon_puresky_4k.exr",
        dome_intensity=1000.0,
        noon_dome_rot=-110.0,
        noon_sun_enable=True, noon_sun_elev=49.79,
        noon_sun_intensity=2450.0, noon_sun_color=(1.0, 0.969, 0.935),
        hdri_sun_rotz_offset=233.5,
        dome_rotation_step=15.0,
    ),
    # 녹지대 가로등주의 그림자가 **보행축을 가로질러** 산책로 포장에 떨어지도록.
    SUN_AZ_OFFSET=172.0,

    render=dict(pt_total_spp=512, pt_max_bounces=8),
)


def _deep_update(dst, src):
    for k, v in src.items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            _deep_update(dst[k], v)
        else:
            dst[k] = v


_ov = os.environ.get("NEGOBS_PARAMS_OVERRIDE", "")
if _ov:
    _deep_update(PARAMS, json.loads(_ov))
    print(f"[PARAMS] override 적용: {_ov}")

_sc_ov = os.environ.get("NEGOBS_SCENE_CONFIG", "")
if _sc_ov:
    _deep_update(SCENE_CONFIG, json.loads(_sc_ov))
    print(f"[SCENE_CONFIG] override 적용: {_sc_ov}")


# ===========================================================================
# [B'] 팔 제어 2키 — 모듈 스코프에서 **한 번** 확정 (sceneC2:496-520 패턴)
# ===========================================================================
KEEP_DRESSING = bool(SCENE_CONFIG.get("keep_dressing", False))
PLACEBO_REMOVE = bool(SCENE_CONFIG.get("placebo_remove", False))
if KEEP_DRESSING:
    if SCENE_CONFIG.get("hazard_stairs", True):
        raise SystemExit(
            "[FATAL sceneL1] keep_dressing=True 는 hazard_stairs=False 를 요구한다 — "
            "위험이 켜져 있으면 보존할 것이 없고 그 팔은 A팔의 라벨 없는 복제가 된다.")
    if not SCENE_CONFIG.get("cue_scene_dressing", True):
        raise SystemExit(
            "[FATAL sceneL1] keep_dressing=True 와 cue_scene_dressing=False 는 모순이다 — "
            "장식이 바로 이 팔이 보존하려는 대상이다.")
if PLACEBO_REMOVE:
    if not SCENE_CONFIG.get("hazard_stairs", True):
        raise SystemExit(
            "[FATAL sceneL1] placebo_remove=True 는 hazard_stairs=True 를 요구한다 — "
            "플라시보 팔은 위험 ON 상태의 외형 대조군(D35)이다.")
    if KEEP_DRESSING:
        raise SystemExit(
            "[FATAL sceneL1] placebo_remove 와 keep_dressing 은 서로 다른 팔(P·C)이며 "
            "동시에 설정될 수 없다.")
_ARM = ("C_hz0_cue1" if KEEP_DRESSING else
        "P_hz1_placebo" if PLACEBO_REMOVE else
        "hz%d_rail%d_tac%d_mat%d_dress%d" % (
            int(SCENE_CONFIG["hazard_stairs"]), int(SCENE_CONFIG["cue_railing"]),
            int(SCENE_CONFIG["cue_tactile"]), int(SCENE_CONFIG["cue_material_break"]),
            int(SCENE_CONFIG["cue_scene_dressing"])))
print(f"[sceneL1] arm={_ARM} keep_dressing={KEEP_DRESSING} "
      f"placebo_remove={PLACEBO_REMOVE}")


# ===========================================================================
# [C] 경로 상수 · 필요 텍스처 역할 · 데이텀 선언
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "sceneL1")

ASSET_ROLES = ["concrete_floor", "plaza_lower", "concrete_wall", "granite_dark",
               "grass", "gravel", "tactile", "sign_no_entry", "hdri", "mdl"]

# 카메라 데이텀 스트립 — 이 씬의 밴드는 base(d ∈ LogU[1.2,12]) + LAT(d ∈ LogU[3,10])
#   이므로 지지집합은 base 가 결정한다. x = −d ∈ [−12.00, −1.20] · |y| ≤ 0.90 에
#   각 방향 0.05 m 여유.
DATUM_STRIP = dict(x0=-12.05, x1=-1.15, y0=-0.95, y1=0.95)
DATUM_TOL = 0.02

GATED_ZONES = [
    # (tag, key, x0, x1, y0, y1, dz)  — dz = 지면 위 최대 융기
    ("CanalS",       "hazard_stairs",      -7.98,  40.00,  -5.74, -3.26, 0.00),
    ("CanalN",       "hazard_stairs",      -7.98,  40.00,   3.26,  5.74, 0.00),
    ("FlatFill-S",   "hazard_stairs(off)", -7.98,  40.00,  -5.74, -3.26, 0.00),
    ("FlatFill-N",   "hazard_stairs(off)", -7.98,  40.00,   3.26,  5.74, 0.00),
    # 난간은 |y| ∈ [3.10, 3.22] → 데이텀 스트립(|y| ≤ 0.95) 밖. 교차 0.
    ("Rail-S",       "cue_railing",        -7.70,  34.10,  -3.25, -3.07, 1.15),
    ("Rail-N",       "cue_railing",        -7.70,  34.10,   3.07,  3.25, 1.15),
    # 점형블록 2밴드 — **서로 다른 위험 경계 2곳**(볼라드 열 / 2단 상단)이라 밴드 수
    #   정합. [R4] 둘 다 세로 0.60(유닛 2매) · 마루 밴드는 이격 0.30 · 가로 ±1.80(포장면).
    ("Tactile-Bol",  "cue_tactile",       -13.85,  -8.85,  -4.00, -3.40, 0.004),
    ("Tactile-Crest", "cue_tactile",       -7.40,  -6.80,  -1.80,  1.80, 0.004),
    ("Nosing",       "cue_nosing",         -8.41,  -7.69,  -4.60,  4.60, 0.012),
    ("Sign",         "cue_sign",          -10.55,  -9.85,   3.05,  3.75, 2.05),
    ("Bollard",      "cue_bollard",       -13.68,  -9.02,  -4.38, -4.22, 0.90),
    ("Delineator-S", "cue_delineator",    -13.25, -13.15,  -2.45, -2.35, 0.80),
    ("Delineator-N", "cue_delineator",    -13.25, -13.15,   2.35,  2.45, 0.80),
    # ground_kit: 줄눈 recess 3 mm(융기 0) · 맨홀 7.7 mm · 빗물받이 flush.
    #   `surface=None` 로 잡초(proud 최대 0.107 m)를 **끈다** — 법1과 VG-datum 이 같은
    #   방향을 가리키는 드문 경우다.
    ("GKitPlaza",    "cue_manhole/slab_joint/drainage",
                                          -13.90,  -8.45,  -4.50,  4.50, 0.008),
    ("GKitWalk",     "cue_slab_joint/drainage",
                                           -7.66,  13.90,  -1.76,  1.76, 0.008),
    ("TreeGrate",    "cue_tree_grate",    -23.62,  -8.18,   2.78,  4.22, 0.004),
    # 가로등주는 녹지대(|y| = 2.50) — 스트립 밖. 등기구 암이 보행축 쪽으로 0.95 m 뻗어
    #   최근접 |y| = 1.45 이고, 그래도 스트립(|y| ≤ 0.95)을 침범하지 않는다.
    #   **남·북을 한 구역으로 묶으면 안 된다** — 감싸는 최소 상자가 스트립을 삼킨다
    #   (설계 시 CPU 자기검사가 실제로 `datum_fail` 로 읽었다. sceneH3 벤치와 같은 함정).
    ("Shadow-LampS", "cue_shadow_caster",  -4.00,  12.80,  -2.60, -1.45, 4.40),
    ("Shadow-LampN", "cue_shadow_caster",  -4.00,  12.80,   1.45,  2.60, 4.40),
    ("Shadow-Tree",  "cue_shadow_caster", -24.20,  -8.00,   2.20,  4.80, 6.80),
    ("Dress-N",      "cue_scene_dressing", -24.20,  62.00,   1.90, 40.00, 12.0),
    ("Dress-S",      "cue_scene_dressing", -24.20,  62.00, -40.00, -1.90, 12.0),
    ("Dress-Far",    "cue_scene_dressing",  30.00,  62.00, -40.00, 40.00, 12.0),
]


# ===========================================================================
# [C'] PLACEMENT — `placement_lint.py` 의 기하 무관 선언 블록 (w3_execution_spec §10.4)
# ===========================================================================
PLACEMENT = dict(
    # `walk_edges` 는 **의도적으로 선언하지 않는다.** LINT-5 는 「도로의 구조·시설 기준에
    #   관한 규칙」 제16조의 **보도 유효폭**을 재는 규칙인데, 이 씬의 경로는 보도가 아니라
    #   제방 **관리 겸용 산책로**(차량 통행 가능·보도 구분 없음)이고 진입부는 광장이다.
    #   없는 데이텀을 지어내면 그 규칙은 검사가 아니라 허구가 된다 — 미선언은 `nodata`
    #   로 보고되지 거짓 통과가 아니다(SCENE_H67_BUILD §5-5 · SCENE_TEXT_BUILD §8-5 승계).
    kerb_lines=[((-13.90, -4.30), (-8.90, -4.30))],
    anchors={
        "plaza_S": dict(face_bearing_deg=90.0, props=["Bench_0"]),
        "plaza_N": dict(face_bearing_deg=270.0, props=["Bench_1"]),
        # `sc.build_sign` 의 `/Panel` 은 월드 좌표로 직접 작도되는 메시라 xformOp 자체가
        #   없다(scene_common.py:4572-4595). 인벤토리에서 읽히는 그 프림의 yaw 는
        #   **구조적으로 0** 이고, 실제 정면 방위는 `/Back` 이 갖는다.
        "canal_notice": dict(face_bearing_deg=180.0, props=["Sign/Back"]),
        "walk_axis": dict(face_bearing_deg=0.0, props=["Sign/Panel"]),
    },
    # 가로수 열 — 1열 1수종(S-1) · 피치 2.0 m(광장 소형 가로수) · 방위 = 연석 방위 0°.
    #   `pts` 는 **전 그루의 좌표**여야 한다(LINT-2 는 인접 간격을 그대로 피치로 읽는다).
    #   피치 **7.0 m** 는 PE-2(조례 제7조1가 6~8 m)의 법정 밴드다 — 설계 초안은 소형
    #   가로수 2.0 m 피치였고 LINT-2 가 ERROR 로 잡았다. 광장을 15.8 m 로 늘려 법정
    #   피치를 지켰다(광장은 높이맵 격자 x ≥ −2 밖이라 GT 영향 0).
    routes={
        "plaza_N": dict(pts=[(-22.90, 3.50), (-15.90, 3.50), (-8.90, 3.50)],
                        species="elm", pitch_m=7.0),
    },
)


# ===========================================================================
# 섹터 모형 — pxr 없이 CPU 로 돈다. **이 씬의 산출물이 여기서 예측된다.**
# ===========================================================================
SECTOR_NAMES = ("A", "B", "C", "D", "E")
SECTOR_EDGES = (31.1, 18.66, 6.22, -6.22, -18.66, -31.1)   # gridspec_v1
BAND_EDGES = (0.0, 2.0, 5.0, 8.0, 12.0)                    # gridspec_v1
GRID = dict(x0=-2.0, x1=14.0, y0=-8.0, y1=8.0)             # 높이맵 격자


def _profile_z(x):
    """보행축 종단면 z(x). 배치 전용(높이맵은 AABB 가 따로 측정한다)."""
    T = PARAMS["terrain"]
    ap, pl, st, wk = T["approach"], T["plaza"], T["step"], T["walk"]
    if x <= st["x0"]:
        return pl["z"] if x >= pl["x0"] else ap["z"]
    if x >= st["x0"] + st["n"] * st["tread"]:
        return wk["z"]
    i = min(st["n"] - 1, max(0, int((x - st["x0"]) / st["tread"])))
    return pl["z"] + (i + 1) * st["riser"]


def _cell_of(x, y, eye, yaw_deg):
    """(x, y) 가 떨어지는 폴라 셀 = (band, sector) 또는 None. `labeler.polar_cells` 와
    같은 산술이다 — 카메라 프레임으로 −yaw 회전한 뒤 방위각·반경으로 구간을 찾는다."""
    cy, sy = math.cos(math.radians(yaw_deg)), math.sin(math.radians(yaw_deg))
    dx, dy = x - eye[0], y - eye[1]
    xc, yc = dx * cy + dy * sy, -dx * sy + dy * cy
    rng = math.hypot(xc, yc)
    if rng >= BAND_EDGES[-1]:
        return None
    az = math.degrees(math.atan2(yc, xc))
    if az > SECTOR_EDGES[0] or az < SECTOR_EDGES[-1]:
        return None
    s = 0
    while s < 5 and az < SECTOR_EDGES[s + 1]:
        s += 1
    if s >= 5:
        return None
    b = 0
    while b < 4 and rng >= BAND_EDGES[b + 1]:
        b += 1
    return b, s


def _footprint_samples(step=0.25):
    """낙차 발자국(양측 개거 개구) 안의 표본점 — 격자 x ∈ [−2, 14] 로 한정한다.

    [개정 R2] 횡단 복개 구간은 상면이 마루와 같은 z 라 **발자국이 아니다** — 표본에서 뺀다.
    """
    hz = PARAMS["hazard"]
    cul = [(c, c + hz["culvert_w"]) for c in hz["culverts"]]
    pts = []
    x = GRID["x0"]
    while x <= GRID["x1"] + 1e-9:
        if not any(a <= x <= b for a, b in cul):
            y = hz["y_lip"]
            while y <= hz["y_toe"] + 1e-9:
                pts.append((x, y))
                pts.append((x, -y))
                y += step
        x += step
    return pts


def _trunc_norm(rng, mu, sd, lo, hi):
    for _ in range(64):
        v = rng.gauss(mu, sd)
        if lo <= v <= hi:
            return v
    return min(max(rng.gauss(mu, sd), lo), hi)


def _sector_hist(d_lo, d_hi, n=1500, seed=11, step=0.25, yaw_sd=8.0):
    """실제 샘플러로 **섹터별 polar_gt 양성률**을 몬테카를로 적분한다.

    `yaw_sd=0` 이면 **yaw 지터를 끈다** — 그 경우가 파일 상단의 기하 항등식이 성립하는
    조건(카메라가 보행축을 정확히 향함)이고, 기본값 8.0 은 `variation_kit` 의 실제
    샘플러(trunc-N(0, 8, ±20))다. 두 값의 차이가 곧 **"C 섹터에 위험이 실리는 것은
    씬 기하가 아니라 카메라 회전 때문"** 이라는 사실의 정량이다.

    반환 dict:
      pos_rate[s]   — 그 섹터의 셀이 **하나라도** 양성인 포즈 비율 (프레임 수준)
      cell_share[s] — 양성 셀 수의 섹터별 점유율 (셀 수준 · 20셀 중)
      any_pos       — 격자 안에 발자국이 하나라도 있는 포즈 비율 (= 1 − none_in_fov)
    """
    rng = random.Random(seed)
    pts = _footprint_samples(step)
    pos = [0] * 5
    cells_tot = 0
    cells_by_s = [0] * 5
    n_any = 0
    for _ in range(n):
        d = math.exp(rng.uniform(math.log(d_lo), math.log(d_hi)))
        y_c = _trunc_norm(rng, 0.0, 0.35, -0.90, 0.90)
        yaw = (_trunc_norm(rng, 0.0, yaw_sd, -20.0, 20.0) if yaw_sd > 0 else 0.0)
        eye = (-d, y_c)
        hit = set()
        for (x, y) in pts:
            c = _cell_of(x, y, eye, yaw)
            if c is not None:
                hit.add(c)
        if hit:
            n_any += 1
        seen = set(s for _b, s in hit)
        for s in seen:
            pos[s] += 1
        cells_tot += len(hit)
        for _b, s in hit:
            cells_by_s[s] += 1
    return dict(
        pos_rate={SECTOR_NAMES[s]: pos[s] / n for s in range(5)},
        cell_share={SECTOR_NAMES[s]: (cells_by_s[s] / cells_tot if cells_tot else 0.0)
                    for s in range(5)},
        cells_per_frame=cells_tot / n,
        any_pos=n_any / n)


def build_views():
    """카메라 프리셋: grid_views(gy=0, 보행축 +X) + 미장경 4컷."""
    views = sc.grid_views(0.0)
    # walk_axis_low: 보행축 정면 저시점 — **이 씬의 연구 변수**(낙차가 측방 섹터에 실리는가)
    views["walk_axis_low"] = dict(eye=[-6.0, 0.0, 0.90], tgt=[6.0, 0.2, -0.2])
    # canal_face: 남측 도수로를 비스듬히 — 낙차 1.5 m 와 난간의 스케일을 읽는 컷
    views["canal_face"] = dict(eye=[-1.20, -1.30, 1.55], tgt=[6.0, -4.6, -1.4])
    # levee_over: 제방 마루 전체 — 양측 개거·난간·갈대가 층을 이루는 사면 컷
    views["levee_over"] = dict(eye=[-9.5, -6.4, 4.6], tgt=[5.0, 1.0, -0.8])
    # plaza_entry: 진입 광장 — 볼라드·점형블록·가로수·표지가 한 프레임에
    views["plaza_entry"] = dict(eye=[-15.0, -2.2, 1.65], tgt=[-6.0, 1.0, 0.1])
    return views


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. walk_axis_low (h0.90·d6.0) — 낙차가 **좌우**에 있고 정면은 무해한가
 2. canal_face                 — 개거 1.50 m · 난간 1.10 m 스케일이 맞는가
 3. levee_over                 — 양측 개거가 재질·통수 상태로 **구분**되는가 (거울상 금지)
 4. plaza_entry                — 볼라드·점형블록·가로수·표지가 기능적으로 읽히는가
 5. cue ON vs OFF              — 단서 토글 시 개거 기하 **불변**인가
 6. 접지·순백                  — 순백(>0.8) 대면적 없음 · 모든 프림 접지 · Z파이팅 없음
 7. props 규율                 — 볼라드 피치 1.50 법정치 · 조형물 0"""


def main():
    # [GT-89] SMOKE 게이트 — Isaac 부팅 **전** 조기 종료 (GPU·GUI 미사용).
    if os.environ.get("NEGOBS_SMOKE", "0") == "1" \
            and os.environ.get("NEGOBS_SMOKE_ASSEMBLE", "0") != "1":
        print("SMOKE_OK %s pre-boot gate (GT-89)" % os.path.basename(__file__))
        if not _geometry_selfcheck():
            raise SystemExit("sceneL1 CPU 자기검사 실패")
        return
    capture_mode = os.environ.get("NEGOBS_CAPTURE", "0") == "1"
    smoke_mode = os.environ.get("NEGOBS_SMOKE", "0") == "1"
    sc.check_assets(ASSET_ROLES, hdri=PARAMS["light"]["hdri"])

    simulation_app = sc.boot(capture_mode or smoke_mode)

    import carb
    import carb.input
    import omni.usd
    import omni.appwindow
    from pxr import UsdGeom
    from omni.kit.viewport.utility import (get_active_viewport,
                                           capture_viewport_to_file)
    from isaacsim.core.utils.viewports import set_camera_view

    settings = carb.settings.get_settings()
    stage = omni.usd.get_context().get_stage()
    UsdGeom.Xform.Define(stage, "/World/SceneL1")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    T = PARAMS["terrain"]
    HZ = PARAMS["hazard"]
    ROOT = "/World/SceneL1"

    def BOX(path, center, size, mtl=None, col=False, rotZ=0.0):
        return sc.add_box(stage, path, center, size, mtl, collider=col, rotZ=rotZ)

    def CYL(path, center, r, h, mtl=None, rotY=0.0, rotX=0.0, col=False):
        return sc.add_cylinder(stage, path, center, r, h, mtl,
                               rotY=rotY, rotX=rotX, collider=col)

    def PBR(path, *args, **kwargs):
        return sc.make_pbr(stage, path, *args, **kwargs)

    # [VG-void] 타일 이음매 여유 — 인접 슬래브가 **정확히 같은 좌표**에서 맞닿으면
    #   `AabbPrefilter.ground_z` 의 하향 레이가 두 상자의 면을 동시에 스치며 둘 다 놓친다
    #   (sceneH7 스모크 실측: 계단 이음매 3줄 197셀이 void). 4 mm 겹침을 주면 겹친 구간에서
    #   **더 높은 상자가 이기므로** 경계가 4 mm 이동할 뿐이다(격자 피치 50 mm 의 1/12).
    SEAM = 0.004

    def RECT(path, x0, y0, x1, y1, z_top, base, mtl, col=True, seam=True):
        """축정렬 지면 상자. 회전 상자를 쓰지 않는 이유는 `AabbPrefilter.ground_z`
        (상방 레이 최초 히트)가 회전체의 월드 AABB 를 평면으로 읽기 때문이다 —
        그러면 카메라 배치(`cam.ground_z`)와 높이맵이 동시에 틀린다."""
        if seam:
            x0, y0, x1, y1 = x0 - SEAM, y0 - SEAM, x1 + SEAM, y1 + SEAM
        return BOX(path, ((x0 + x1) / 2.0, (y0 + y1) / 2.0, (z_top + base) / 2.0),
                   (x1 - x0, y1 - y0, z_top - base), mtl, col=col)

    # -------------------------------------------------------------------
    # 재질 (3단 규약)
    # -------------------------------------------------------------------
    def setup_materials():
        sca = mp["scale"]
        M = {}
        M["plaza"] = PBR(f"{ROOT}/Looks/ConcretePave",
                         sc.tex_path("concrete_floor", "diff"),
                         sc.tex_path("concrete_floor", "nor"),
                         sc.tex_path("concrete_floor", "rough"),
                         sca["concrete_floor"], tint=mp["plaza_tint"])
        M["walk"] = PBR(f"{ROOT}/Looks/PlazaLower",
                        sc.tex_path("plaza_lower", "diff"),
                        sc.tex_path("plaza_lower", "nor"),
                        sc.tex_path("plaza_lower", "rough"),
                        sca["plaza_lower"], tint=mp["walk_tint"])
        M["grass"] = PBR(f"{ROOT}/Looks/Grass", sc.tex_path("grass", "diff"),
                         sc.tex_path("grass", "nor"),
                         sc.tex_path("grass", "rough"),
                         sca["grass"], tint=mp["grass_tint"])
        M["coping"] = PBR(f"{ROOT}/Looks/GraniteDark",
                          sc.tex_path("granite_dark", "diff"),
                          sc.tex_path("granite_dark", "nor"),
                          sc.tex_path("granite_dark", "rough"),
                          sca["granite_dark"], tint=mp["coping_tint"])
        M["coping_n"] = PBR(f"{ROOT}/Looks/ConcreteCoping",
                            sc.tex_path("concrete_floor", "diff"),
                            sc.tex_path("concrete_floor", "nor"),
                            sc.tex_path("concrete_floor", "rough"),
                            sca["concrete_floor"], tint=mp["coping_tint_n"])
        M["wall"] = PBR(f"{ROOT}/Looks/ConcreteWall",
                        sc.tex_path("concrete_wall", "diff"),
                        sc.tex_path("concrete_wall", "nor"),
                        sc.tex_path("concrete_wall", "rough"),
                        sca["concrete_wall"], tint=mp["wall_color"])
        M["invert"] = PBR(f"{ROOT}/Looks/ConcreteInvert",
                          sc.tex_path("concrete_floor", "diff"),
                          sc.tex_path("concrete_floor", "nor"),
                          sc.tex_path("concrete_floor", "rough"),
                          sca["concrete_floor"], tint=mp["invert_tint"])
        M["gravel"] = PBR(f"{ROOT}/Looks/Gravel", sc.tex_path("gravel", "diff"),
                          sc.tex_path("gravel", "nor"),
                          sc.tex_path("gravel", "rough"),
                          sca["gravel"], tint=mp["gravel_tint"])
        M["tactile"] = sc.tactile_pbr(stage, f"{ROOT}/Looks/Tactile",
                                      scale_m=sca["tactile"])
        # 금속·도색·사인·수면 = OmniPBR
        M["water"] = PBR(f"{ROOT}/Looks/Water", diffuse_color=mp["water_color"],
                         roughness_const=mp["water_rough"], metallic=0.0)
        M["rail"] = PBR(f"{ROOT}/Looks/RailSteel",
                        diffuse_color=mp["rail_color"], metallic=mp["rail_metal"],
                        roughness_const=mp["rail_rough"])
        M["nosing"] = PBR(f"{ROOT}/Looks/Nosing", diffuse_color=mp["nosing_color"],
                          roughness_const=mp["nosing_rough"])
        M["band"] = PBR(f"{ROOT}/Looks/GuardBand", diffuse_color=mp["band_color"],
                        roughness_const=0.35)
        M["bollard"] = PBR(f"{ROOT}/Looks/Bollard",
                           diffuse_color=mp["bollard_color"],
                           metallic=mp["bollard_metallic"],
                           roughness_const=mp["bollard_rough"])
        M["pole"] = PBR(f"{ROOT}/Looks/Pole", diffuse_color=mp["pole_color"],
                        metallic=mp["pole_metallic"],
                        roughness_const=mp["pole_rough"])
        M["lamp"] = PBR(f"{ROOT}/Looks/Lamp", diffuse_color=mp["lamp_color"],
                        roughness_const=mp["lamp_rough"])
        M["iron"] = PBR(f"{ROOT}/Looks/Iron", diffuse_color=mp["iron_color"],
                        metallic=mp["iron_metallic"],
                        roughness_const=mp["iron_rough"])
        M["wood"] = PBR(f"{ROOT}/Looks/Wood", diffuse_color=mp["wood_color"],
                        roughness_const=mp["wood_rough"])
        M["reed"] = PBR(f"{ROOT}/Looks/Reed", sc.tex_path("grass", "diff"),
                        sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
                        1.1, tint=mp["reed_tint"])
        M["canopy_a"] = PBR(f"{ROOT}/Looks/CanopyA", diffuse_color=mp["canopy_a"],
                            roughness_const=mp["canopy_rough"])
        M["canopy_b"] = PBR(f"{ROOT}/Looks/CanopyB", diffuse_color=mp["canopy_b"],
                            roughness_const=mp["canopy_rough"])
        M["backdrop"] = PBR(f"{ROOT}/Looks/BgConcrete",
                            diffuse_color=mp["backdrop_color"],
                            roughness_const=mp["backdrop_rough"])
        M["sign"] = PBR(f"{ROOT}/Looks/Sign", sc.tex_path("sign_no_entry", "diff"),
                        uv_mode=True)
        return M

    # -------------------------------------------------------------------
    # ① 경로 — 지형. **hazard_* 밖**. 4팔 전부에서 동일 프림·동일 좌표.
    # -------------------------------------------------------------------
    def build_terrain(M):
        """진입 광장 → 2단 오름 → 제방 마루 산책로 + 녹지대 + 외안 지반.

        `cam.ground_z` 가 이 프림들만으로 결정되므로(단서·위험 프림은 데이텀 스트립 밖
        또는 융기 ≤ 12 mm), VG-datum 은 `datum_exact` 로 통과하도록 **구성상** 되어 있다.
        """
        ap, pl, st, wk, vg, fb = (T["approach"], T["plaza"], T["step"], T["walk"],
                                  T["verge"], T["farbank"])
        yf, bz = T["y_far"], T["base_z"]
        # (1) 진입 지반 (잔디) — 격자 밖. 광장 포장이 그 위에 20 mm proud 로 얹힌다.
        RECT(f"{ROOT}/Ground/Approach", ap["x0"], -yf, ap["x1"], yf,
             ap["z"], bz, M["grass"])
        # (2) 제방 진입 광장 (콘크리트 타설) — `cue_material_break` 의 대조 재질
        RECT(f"{ROOT}/Ground/Plaza", pl["x0"], -pl["y_half"], pl["x1"],
             pl["y_half"], pl["z"], bz, M["plaza"])
        # (3) 2단 오름 — 광장에서 제방 마루로 올라선다 (팔 불변 지형 · nosing 의 대상)
        for i in range(st["n"]):
            x0 = st["x0"] + i * st["tread"]
            RECT(f"{ROOT}/Ground/Step_{i}", x0, -st["y_half"], x0 + st["tread"],
                 st["y_half"], pl["z"] + (i + 1) * st["riser"], bz, M["plaza"])
        # (4) 제방 마루 산책로 — `cue_material_break` 의 유일한 대상(재바인딩 전용)
        walk_mtl = M["walk"] if cfg["cue_material_break"] else M["plaza"]
        RECT(f"{ROOT}/Ground/Walk", wk["x0"], -wk["y_half"], wk["x1"],
             wk["y_half"], wk["z"], bz, walk_mtl)
        print(f"[cue] material_break={cfg['cue_material_break']} → Walk = "
              f"{'컬러 콘크리트 판석(PlazaLower)' if cfg['cue_material_break'] else '콘크리트 타설(ConcretePave)'}"
              " · **프림 집합 불변**(재질 재바인딩 전용) → 높이맵 비트 동일 보증")
        # (5) 잔디 녹지대 = 브리프의 **"풀 경계"**. 산책로와 개거 갓돌 사이 1.50 m.
        for tag, y0, y1 in (("S", -vg["y1"], -vg["y0"]),
                            ("N", vg["y0"], vg["y1"])):
            RECT(f"{ROOT}/Ground/Verge{tag}", wk["x0"], y0, wk["x1"], y1,
                 wk["z"], bz, M["grass"])
        # (6) 외안 지반 — 개거 바깥. **채움면과 같은 z = 0.000** 이므로 hazard 토글이
        #     이 면을 건드리지 않는다(발자국이 개거 개구에서만 생긴다).
        for tag, y0, y1 in (("S", -yf, -fb["y0"]), ("N", fb["y0"], yf)):
            RECT(f"{ROOT}/FarBank{tag}", wk["x0"], y0, wk["x1"], y1,
                 fb["z"], bz, M["grass"])
        print(f"[구조] 산책로 유효폭 {2 * wk['y_half']:.2f} m · 녹지대 "
              f"{vg['y1'] - vg['y0']:.2f} m · 2단 오름(라이즈 {st['riser']}) "
              f"· 광장 z {pl['z']:+.2f} → 마루 z {wk['z']:+.2f}")

    # -------------------------------------------------------------------
    # ② 위험 — hazard_stairs 전속. 여기에는 **단서가 한 개도 없다**(프림 위생 1).
    # -------------------------------------------------------------------
    def build_hazard(M):
        """양측 콘크리트 3면 개거. 남 = 통수(수면 −1.50) · 북 = 자갈 바닥(−1.50)."""
        h = HZ
        cw = h["coping"]["w"]
        sc.skin_exclude(f"{ROOT}/CanalS", f"{ROOT}/CanalN")
        for tag, sgn in (("S", -1.0), ("N", +1.0)):
            root = f"{ROOT}/Canal{tag}"
            cop = M["coping"] if tag == "S" else M["coping_n"]
            y_in0, y_in1 = h["fill"]["y0"], h["y_lip"]          # 내측 갓돌
            y_ot0, y_ot1 = h["y_toe"], h["fill"]["y1"]          # 외측 갓돌
            for nm, a, b in (("CopingIn", y_in0, y_in1),
                             ("CopingOut", y_ot0, y_ot1)):
                lo, hi = (sgn * b, sgn * a) if sgn < 0 else (sgn * a, sgn * b)
                RECT(f"{root}/{nm}", h["x0"], lo, h["x1"], hi, 0.0,
                     h["wall_bot"], cop)
            # 벽체 — 갓돌 밑에서 인버트까지 (갓돌이 상면을 덮으므로 top 은 갓돌 밑면)
            for nm, a, b in (("WallIn", y_in0, y_in1), ("WallOut", y_ot0, y_ot1)):
                lo, hi = (sgn * b, sgn * a) if sgn < 0 else (sgn * a, sgn * b)
                RECT(f"{root}/{nm}", h["x0"], lo, h["x1"], hi, -0.18,
                     h["wall_bot"], M["wall"], seam=False)
            # 인버트 (콘크리트 바닥판) — **VG-void**: 발자국 전역에 실제 바닥 프림
            lo, hi = ((sgn * h["y_toe"], sgn * h["y_lip"]) if sgn < 0
                      else (sgn * h["y_lip"], sgn * h["y_toe"]))
            RECT(f"{root}/Invert", h["x0"], lo, h["x1"], hi,
                 h["invert_z"], h["wall_bot"], M["invert"])
            # 통수면 / 자갈 바닥 — 상면이 곧 **낙차 바닥 z_on = −1.500**
            if tag == "S":
                BOX(f"{root}/Water",
                    (0.5 * (h["x0"] + h["x1"]), 0.5 * (lo + hi),
                     h["fill_top"] - 0.06),
                    (h["x1"] - h["x0"], hi - lo, 0.12), M["water"])
            else:
                BOX(f"{root}/Bed",
                    (0.5 * (h["x0"] + h["x1"]), 0.5 * (lo + hi),
                     h["fill_top"] - 0.06),
                    (h["x1"] - h["x0"], hi - lo, 0.12), M["gravel"], col=True)
            # 시점 흉벽 — 개거가 제방 성토 끝단에서 시작한다
            RECT(f"{root}/Headwall", h["head_x"], lo, h["x0"] + 0.24, hi,
                 0.0, h["wall_bot"], M["wall"])
            # [개정 R2] 횡단 농로 복개 — 개구를 가로지르는 콘크리트 슬래브.
            #   상면이 마루와 같은 z = 0.000 이라 발자국이 아니고, 그 **동쪽 가장자리가
            #   스텝 게이트의 근접 경계(near boundary)를 만든다**(파일 상단 §스텝 게이트).
            for i, cx in enumerate(h["culverts"]):
                RECT(f"{root}/Culvert_{i}", cx, lo, cx + h["culvert_w"], hi,
                     0.0, h["wall_bot"], M["plaza"])
        print(f"[hazard] 양측 개거 — 낙차 = {0.0 - h['fill_top']:.3f} m "
              f"(마루 0.000 → 바닥 {h['fill_top']:+.3f}) · 개구 폭 "
              f"{h['y_toe'] - h['y_lip']:.2f} m · 남측 통수(수심 "
              f"{h['fill_top'] - h['invert_z']:.2f} m) · 북측 자갈 바닥 · "
              f"횡단 복개 {len(h['culverts'])}개소 @x={h['culverts']} 폭 "
              f"{h['culvert_w']:.2f} m")

    def build_flat_fill(M):
        """hazard_stairs=False 대조군 — 마루 레벨의 평탄 지면이 개거 자리를 채운다.

        이것이 라벨러의 **반사실 보행 가능면 z_off** 다(footprint v2 = z_off − z_on ≥ 0.3).
        채움면 z 는 산책로·녹지대·외안과 **모두 같은 0.000** 이므로 hazard OFF 팔의
        횡단면은 완전 평탄해지고, 발자국은 개거 개구에서만 생긴다.
        """
        f = HZ["fill"]
        for tag, sgn in (("S", -1.0), ("N", +1.0)):
            lo, hi = ((sgn * f["y1"], sgn * f["y0"]) if sgn < 0
                      else (sgn * f["y0"], sgn * f["y1"]))
            RECT(f"{ROOT}/FlatFill/{tag}", HZ["head_x"], lo, HZ["x1"], hi,
                 f["z"], T["base_z"], M["grass"])
        print(f"[hazard] OFF — 반사실 보행 가능면 z_off = {f['z']:+.3f} "
              f"(|y| {f['y0']:.2f} … {f['y1']:.2f} · 양측)")

    # -------------------------------------------------------------------
    # ③ 단서 — **전부 hazard_* 밖의 자립 프림**. 전부 |y| ≤ 3.22 또는 |y| ≥ 6.20.
    # -------------------------------------------------------------------
    def build_railing(M):
        """양측 스테인리스 파이프 난간 — 낙차 1.50 m > 1.20 m ⇒ 법정 의무(법4)."""
        r = PARAMS["rail"]
        n = int(math.floor((r["x1"] - r["x0"]) / r["post_pitch"])) + 1
        zw = T["walk"]["z"]
        for tag, sgn in (("S", -1.0), ("N", +1.0)):
            for i in range(n):
                x = r["x0"] + i * r["post_pitch"]
                # 각기둥은 **정렬해 세운다** — 난간의 실제 시공이 그러하고,
                #   J-3/J-5(07-30)가 배치 지터를 폐지했다(LINT-10 정적 검사 대상).
                BOX(f"{ROOT}/Rail{tag}/Post_{i:02d}",
                    (x, sgn * r["y"], zw + r["post_h"] / 2.0),
                    (r["post_a"], r["post_a"], r["post_h"]), M["rail"])
                BOX(f"{ROOT}/Rail{tag}/PostCap_{i:02d}",
                    (x, sgn * r["y"], zw + r["post_h"] + r["cap_t"] / 2.0),
                    (r["post_a"] + 0.03, r["post_a"] + 0.03, r["cap_t"]),
                    M["rail"])
            for nm, z in (("Top", r["top_z"]), ("Mid", r["mid_z"])):
                CYL(f"{ROOT}/Rail{tag}/{nm}Rail",
                    (0.5 * (r["x0"] + r["x1"]), sgn * r["y"], zw + z),
                    r["rail_r"], r["x1"] - r["x0"] + 0.3, M["rail"], rotY=90.0)
        print(f"[cue] railing ON — 양측 각기둥 {n}본씩(피치 {r['post_pitch']} m) "
              f"· 2단 횡대 · 가드선 {r['top_z']:.2f} m ≥ 1.10 규정 "
              f"· |y| = {r['y']:.2f} (발자국 근단 {HZ['y_lip']:.2f} 에서 "
              f"{HZ['y_lip'] - r['y'] - r['post_a'] / 2:.2f} m 밖) "
              "[규격 도로안전시설 지침 2.3.3 나 — 110 cm 표준 · 개거 난간 조문 부재]")

    def build_tactile(M):
        t = PARAMS["tactile"]
        bx0, by0, bx1, by1 = t["bollard"]
        sc.build_tactile(stage, f"{ROOT}/Tactile", bx0, bx1, by0, by1,
                         M["tactile"], z=T["plaza"]["z"], proud=t["proud"])
        cx0, cy0, cx1, cy1 = t["crest"]
        sc.build_tactile(stage, f"{ROOT}/TactileCrest", cx0, cx1, cy0, cy1,
                         M["tactile"], z=T["walk"]["z"], proud=t["proud"])
        print(f"[cue] tactile ON — **경고 2밴드(위험 경계 2곳)** · 볼라드 전면 세로 "
              f"{by1 - by0:.2f} m (유닛 {round((by1 - by0) / 0.30)}매 · 볼라드 열에서 "
              f"{abs(PARAMS['bollard']['y'] - by0):.2f} m) + 2단 상단 세로 "
              f"{cx1 - cx0:.2f} m (유닛 {round((cx1 - cx0) / 0.30)}매 · 계단 코에서 "
              f"{cx0 - T['walk']['x0']:.2f} m · 가로 {cy1 - cy0:.2f} m = 산책로 유효폭) "
              f"· proud {t['proud']} m "
              "[규격 교통약자법 시행규칙 별표1(위험장소 0.3 m 전면) · 별표2 제7호 바"
              "(볼라드 0.3 m 전면) · 국도 실무요령 7.5(세로폭 60 cm 표준)]")

    def build_nosing(M):
        """2단 오름의 논슬립 나이징 띠. 낙차 부재가 아니라 **계단 코 처리**이고
        **팔 불변 지형** 위에 있으므로 4팔 전부에 존재한다."""
        st, ng = T["step"], PARAMS["nosing"]
        for i in range(st["n"]):
            x1 = st["x0"] + (i + 1) * st["tread"]
            z = T["plaza"]["z"] + (i + 1) * st["riser"]
            BOX(f"{ROOT}/Nosing/Strip_{i}",
                (x1 - ng["width"] / 2.0, 0.0, z + ng["proud"] / 2.0),
                (ng["width"], 2 * st["y_half"], ng["proud"]), M["nosing"])
        print(f"[cue] nosing ON — {st['n']}단(팔 불변 지형) · 폭 {ng['width']} m · "
              f"proud {ng['proud'] * 1000:.0f} mm [계획 realism_v1_final §84]")

    def build_sign(M):
        """수로 관리 통로 출입 제한 표지 1매 — 법2(임의 경고판 금지): 법정 제식 판만."""
        s = PARAMS["sign"]
        sc.build_sign(stage, f"{ROOT}/Sign", s["x"], s["y"],
                      _profile_z(s["x"]), s["yaw"], M["sign"],
                      w=s["w"], h=s["h"], pole_h=s["pole_h"],
                      pole_mtl=M["pole"], back_mtl=M["iron"])
        print(f"[cue] sign ON — 수로 관리 통로 출입 제한 표지 1매 "
              f"@({s['x']:+.2f},{s['y']:+.2f}) · 임의 문구 0 (법2)")

    def build_bollards(M):
        """제방 진입 차량 억제 볼라드 열. 보차도 경계선 위 · 피치 1.50 m 법정치."""
        b = PARAMS["bollard"]
        for i, x0 in enumerate(b["xs"]):
            x, y = x0, b["y"]
            gz = _profile_z(x)
            # `placement_lint` 의 `props.bollard` 규약: `Bollard_NN` + `/Post` + `/Band`.
            CYL(f"{ROOT}/Bollard_{i:02d}/Post", (x, y, gz + b["h"] / 2.0),
                b["r"], b["h"], M["bollard"])
            CYL(f"{ROOT}/Bollard_{i:02d}/Band", (x, y, gz + b["band_z"]),
                b["r"] + 0.004, b["band_t"], M["band"])
        print(f"[cue] bollard ON — {len(b['xs'])}본 · h {b['h']} m · "
              f"φ{2 * b['r']:.2f} m · 피치 1.50 m · y {b['y']:+.2f} (보차도 경계) "
              "· 반사띠 [규격 교통약자법 시행규칙 별표2 제7호]")

    def build_delineators(M):
        """반사 시선유도봉 — 광장 진입부 차량 억제 보조. 기본 OFF(법4)."""
        d = PARAMS["delineator"]
        for i, y in enumerate(d["ys"]):
            gz = _profile_z(d["x"])
            CYL(f"{ROOT}/Delineator/D_{i}", (d["x"], y, gz + d["h"] / 2.0),
                d["r"], d["h"], M["band"])
            CYL(f"{ROOT}/Delineator/Band_{i}", (d["x"], y, gz + d["h"] - 0.16),
                d["r"] + 0.003, 0.08, M["lamp"])
        print(f"[cue] delineator ON — {len(d['ys'])}본")

    def build_ground_kit(M):
        """지면 문양 (`cue_manhole`·`cue_tree_grate`·`cue_slab_joint`·`cue_drainage`).

        전부 **flush**(융기 ≤ 8 mm · 줄눈은 recess 3 mm)이므로 법7(기하 불변)을 지킨다.
        """
        g = PARAMS["gkit"]
        M2 = dict(M)
        M2.update(joint=M["coping"], crack=M["coping"], manhole=M["iron"],
                  gully=M["iron"], gutter=M["coping"], gutter_cover=M["iron"],
                  trench=M["iron"], trench_frame=M["iron"], marking=M["lamp"],
                  weed=M["grass"], wear=M["gravel"], stain_dirt=M["gravel"],
                  stain_water=M["gravel"], tree_grate=M["iron"], grate=M["iron"],
                  patch=M["plaza"], patch_cut=M["coping"])
        kit = gk.kit_from_scene_common(sc, stage)
        n_prims = 0

        # (a) 제방 진입 광장 — 맨홀 · 빗물받이 · 수축줄눈 (격자 밖)
        infra = dict(manhole=len(g["plaza_manholes"]) if cfg["cue_manhole"] else 0,
                     gully=len(g["plaza_gullies"]) if cfg["cue_drainage"] else 0,
                     gutter_U=0, trench=0)
        sites = dict()
        if cfg["cue_manhole"]:
            sites["manhole"] = [tuple(v) for v in g["plaza_manholes"]]
        if cfg["cue_drainage"]:
            sites["gully"] = [tuple(v) for v in g["plaza_gullies"]]
        gp = gk.plan_ground(
            "alley_concrete", region=tuple(g["plaza_region"]), z=T["plaza"]["z"],
            gy=0.0, origin=(0.0, 0.0, 0.0),
            dists=(2, 5, 10), scene="sceneL1", tactile=(),
            # `surface=None` — 잡초/균열/오염 데칼 OFF. 1차 이유는 법1(손상·노후 금지),
            #   2차 이유는 잡초 프림(proud 최대 0.107 m)이 데이텀 스트립을
            #   `datum_fail` 로 밀 수 있다는 것이다.
            overrides=dict(infra=infra, surface=None), sites=sites, seed=91)
        if not cfg["cue_slab_joint"]:
            gp["ops"] = [o for o in gp["ops"] if o["name"] != "joints"]
            gp["elements"] = [e for e in gp["elements"] if e["kind"] != "joint"]
        res = gk.apply_ground(kit, f"{ROOT}/GKitPlaza", gp, M2,
                              skin_exclude=sc.skin_exclude,
                              scatter=sc.scatter_debris)
        n_prims += res["prims"]

        # (b) 제방 마루 산책로 — 수축줄눈 + 빗물받이 2 (**격자 안** · flush)
        #     `edges` 미선언 이유는 PARAMS 주석에 있다 — 이 씬의 낙차 모서리는 보행축과
        #     나란한 **종단선**이라 횡단 대리선(B7/GT-E2)의 대상이 아니다.
        infra2 = dict(manhole=0,
                      gully=len(g["walk_gullies"]) if cfg["cue_drainage"] else 0,
                      gutter_U=0, trench=0)
        sites2 = dict()
        if cfg["cue_drainage"]:
            sites2["gully"] = [tuple(v) for v in g["walk_gullies"]]
        gp2 = gk.plan_ground(
            "alley_concrete", region=tuple(g["walk_region"]), z=T["walk"]["z"],
            gy=0.0, origin=(0.0, 0.0, 0.0),
            dists=(2, 5, 10), scene="sceneL1", tactile=(),
            overrides=dict(infra=infra2, surface=None), sites=sites2, seed=92)
        if not cfg["cue_slab_joint"]:
            gp2["ops"] = [o for o in gp2["ops"] if o["name"] != "joints"]
            gp2["elements"] = [e for e in gp2["elements"] if e["kind"] != "joint"]
        res2 = gk.apply_ground(kit, f"{ROOT}/GKitWalk", gp2, M2,
                               skin_exclude=sc.skin_exclude,
                               scatter=sc.scatter_debris)
        n_prims += res2["prims"]

        # (c) 수목보호격자 — 빌더가 없으므로 flush 격자를 직접 짓는다(갭 2위 = 전무)
        n_grate = 0
        if cfg["cue_tree_grate"]:
            for i, (gx, gy_) in enumerate(g["tree_grates"]):
                n_grate += _tree_grate(M, f"{ROOT}/TreeGrate_{i}", gx, gy_,
                                       T["plaza"]["z"])
        print(f"[cue] ground pattern — manhole={cfg['cue_manhole']}"
              f"({len(g['plaza_manholes'])}) tree_grate={cfg['cue_tree_grate']}"
              f"({n_grate} 프림) slab_joint={cfg['cue_slab_joint']} "
              f"drainage={cfg['cue_drainage']}(광장 {len(g['plaza_gullies'])} + "
              f"산책로 {len(g['walk_gullies'])}) · gkit 프림 {n_prims} · δmax "
              f"{max(res['gt_delta_max'], res2['gt_delta_max']):.4f} m (flush — 법7)")
        return n_prims + n_grate

    def _tree_grate(M, path, cx, cy, z, side=1.44, frame=0.09, bar=0.035,
                    n_bar=9, proud=0.004):
        """수목보호덮개 (flush) — 사각 프레임 + 평행 바 격자. 단차 4 mm.
        [FA_REALITY §2 2위] 33씬 **전무**였던 지면 문양. 리세스형(함몰)은 hazard 로
        분리하고 여기서는 **flush 한정**(법7)."""
        n, h = 0, 0.05
        for tag, cx_, cy_, sx, sy in (
                ("FN", cx, cy + (side - frame) / 2.0, side, frame),
                ("FS", cx, cy - (side - frame) / 2.0, side, frame),
                ("FE", cx + (side - frame) / 2.0, cy, frame, side - 2 * frame),
                ("FW", cx - (side - frame) / 2.0, cy, frame, side - 2 * frame)):
            BOX(f"{path}/{tag}", (cx_, cy_, z + proud - h / 2.0), (sx, sy, h),
                M["iron"])
            n += 1
        span = side - 2 * frame
        for i in range(n_bar):
            yy = cy - span / 2.0 + span * (i + 0.5) / n_bar
            BOX(f"{path}/Bar_{i}", (cx, yy, z + proud - h / 2.0),
                (span, bar, h), M["iron"])
            n += 1
        sc.add_disc(stage, f"{path}/Soil", (cx, cy, z - 0.02), 0.22, 0.06,
                    M["gravel"], seg=18)
        return n + 1

    def build_shadow_casters(M):
        """그림자 밴드 캐스터 — 광장 가로수 + 녹지대 가로등주 (`cue_shadow_caster`).

        **양성 씬에도 동일 비율로 배치한다**(계획 §2.0 부작용 경보).
        배치 규칙 하나가 이 씬에만 있다 — **수관을 개거 위에 두지 않는다.** 높이맵은
        수직 레이의 최초 히트이므로 개거를 덮은 수관은 그 셀의 z 를 수관 top 으로
        만들어 **발자국을 지운다**(A·C 양팔 모두에서 지워지므로 조용히 GT 가 준다).
        그래서 가로수는 전부 진입 광장(x ≤ −8.4)에 서고, 녹지대에는 수관 없는
        **가로등주**(φ0.144)만 세운다.
        """
        s = PARAMS["shadow"]
        for i, (tx, ty) in enumerate(s["trees"]):
            sc.build_tree(stage, f"{ROOT}/Shadow/Tree_{i}", tx, ty,
                          _profile_z(tx), M["wood"], M["canopy_a"], M["canopy_b"],
                          trunk_r=0.14, trunk_h=s["tree_h"] * 0.52,
                          canopy_blobs=10, canopy_spread=1.05, species="elm")
        for i, (lx, ly) in enumerate(s["lamps"]):
            gz = _profile_z(lx)
            CYL(f"{ROOT}/Shadow/LampPole_{i}", (lx, ly, gz + s["lamp_h"] / 2.0),
                0.072, s["lamp_h"], M["pole"])
            arm_y = ly - math.copysign(s["lamp_arm"] / 2.0, ly)
            CYL(f"{ROOT}/Shadow/LampArm_{i}", (lx, arm_y, gz + s["lamp_h"]),
                0.05, s["lamp_arm"], M["pole"], rotX=90.0)
            BOX(f"{ROOT}/Shadow/LampHead_{i}",
                (lx, ly - math.copysign(s["lamp_arm"], ly),
                 gz + s["lamp_h"] - 0.09),
                (0.44, 0.20, 0.13), M["lamp"])
        print(f"[cue] shadow_caster ON — 광장 가로수 {len(s['trees'])}주 + "
              f"녹지대 가로등 {len(s['lamps'])}주 · **개거 상부 수관 0** "
              "(발자국 보호 규칙)")

    def build_dressing(M):
        """③ 단서의 환경 성분 — 갈대 군락 · 밭 경계 관목 · 벤치 · 원경 펌프장/마을."""
        d = PARAMS["dress"]
        fbz = T["farbank"]["z"]
        for i, (x0, y0, x1, y1) in enumerate(d["reed_bands"]):
            sc.build_hedge(stage, f"{ROOT}/Dress/Reed_{i}", x0, y0, x1, y1,
                           d["reed_h"], mtl=M["reed"], base_z=fbz,
                           rounded=True, crown_max=40)
        for i, (x0, y0, x1, y1) in enumerate(d["hedge"]):
            sc.place_hedge_row(stage, f"{ROOT}/Dress/Hedge_{i}", x0, y0, x1, y1,
                               d["shrub_h"], seed=1910 + i, base_z=fbz,
                               fallback_mtl=M["reed"])
        for i, (bx, by, byaw) in enumerate(d["benches"]):
            sc.build_bench(stage, f"{ROOT}/Dress/Bench_{i}", bx, by,
                           _profile_z(bx), M["wood"], yaw=byaw)
        if not PLACEBO_REMOVE:
            for tag, x0, x1, y0, y1, hgt in d["pumphouse"] + d["village"]:
                BOX(f"{ROOT}/Dress/Far_{tag}",
                    ((x0 + x1) / 2.0, (y0 + y1) / 2.0, fbz + hgt / 2.0),
                    (x1 - x0, y1 - y0, hgt), M["backdrop"])
        else:
            print("[placebo] 원경 배수펌프장·마을 물량군 제거 — "
                  "위험·단서는 전부 유지(D35 P팔)")
        print(f"[cue] scene_dressing ON — 갈대 {len(d['reed_bands'])}띠 · "
              f"관목 {len(d['hedge'])}띠 · 벤치 {len(d['benches'])} · 원경 "
              f"{0 if PLACEBO_REMOVE else len(d['pumphouse']) + len(d['village'])}동")

    # -------------------------------------------------------------------
    # 자기검사 — 조립 직후, 렌더 전
    # -------------------------------------------------------------------
    def scene_selfcheck():
        from pxr import Usd, UsdGeom
        ok = True
        ds = DATUM_STRIP

        # (1) 선언 검사 — 3층(VG-datum) 분류
        cross = [z for z in GATED_ZONES
                 if not (z[3] <= ds["x0"] or z[2] >= ds["x1"]
                         or z[5] <= ds["y0"] or z[4] >= ds["y1"])]
        fail = [z for z in cross if z[6] > DATUM_TOL]
        tol = [z for z in cross if z[6] <= DATUM_TOL]
        if fail:
            ok = False
        print(f"[selfcheck] (1) 데이텀 스트립 × 토글구역 {len(GATED_ZONES)}건 → "
              f"datum_exact {len(GATED_ZONES) - len(cross)} · datum_tol "
              f"{[(t[0], t[6]) for t in tol]} · datum_fail {[f[0] for f in fail]}"
              + ("" if fail else " · OK"))

        # (2) 기계 재확인 — 이 팔에서 실제로 존재하는 토글 프림의 월드 AABB
        bbc = UsdGeom.BBoxCache(Usd.TimeCode.Default(),
                                [UsdGeom.Tokens.default_, UsdGeom.Tokens.render])
        gated_roots = ("/CanalS", "/CanalN", "/FlatFill", "/RailS", "/RailN",
                       "/Tactile", "/Nosing", "/Sign", "/Bollard", "/Delineator",
                       "/GKitPlaza", "/GKitWalk", "/TreeGrate", "/Shadow", "/Dress")
        hits, tol_hits, n_scan = [], [], 0
        for prim in stage.Traverse():
            p = str(prim.GetPath())
            if not p.startswith(ROOT) or not prim.IsA(UsdGeom.Gprim):
                continue
            tail = p[len(ROOT):]
            if not any(tail.startswith(g) for g in gated_roots):
                continue
            n_scan += 1
            try:
                b = bbc.ComputeWorldBound(prim).ComputeAlignedRange()
            except Exception:
                continue
            if b.IsEmpty():
                continue
            mn, mx = b.GetMin(), b.GetMax()
            if not (mx[0] > ds["x0"] and mn[0] < ds["x1"]
                    and mx[1] > ds["y0"] and mn[1] < ds["y1"]):
                continue
            x_ref = min(max(0.5 * (mn[0] + mx[0]), ds["x0"]), ds["x1"])
            dz = float(mx[2]) - _profile_z(x_ref)
            (tol_hits if dz <= DATUM_TOL else hits).append((p, round(dz, 4)))
        if hits:
            ok = False
        print(f"[selfcheck] (2) 토글 프림 {n_scan}개 전수 AABB → 스트립 교차 "
              f"{len(hits) + len(tol_hits)}건 (datum_tol {len(tol_hits)} · "
              f"datum_fail {len(hits)})"
              + (f" FAIL={hits[:6]}" if hits else " · OK"))

        # (3) VG-void — 격자 전역 횡단면 커버리지 (해석적)
        segs = [(-T["y_far"], -T["farbank"]["y0"]),
                (-HZ["fill"]["y1"], -HZ["fill"]["y0"]),
                (-T["verge"]["y1"], -T["verge"]["y0"]),
                (-T["walk"]["y_half"], T["walk"]["y_half"]),
                (T["verge"]["y0"], T["verge"]["y1"]),
                (HZ["fill"]["y0"], HZ["fill"]["y1"]),
                (T["farbank"]["y0"], T["y_far"])]
        cover_hi, gap = -T["y_far"], []
        for a, b in sorted(segs):
            if a > cover_hi + 1e-6:
                gap.append((cover_hi, a))
            cover_hi = max(cover_hi, b)
        if cover_hi < T["y_far"] - 1e-6:
            gap.append((cover_hi, T["y_far"]))
        if gap:
            ok = False
        print(f"[selfcheck] (3) VG-void 횡단면 커버리지 |y| ≤ {T['y_far']:.0f} → "
              f"공백 {len(gap)}구간" + (f" {gap}" if gap else " · 커버리지 1.0 · OK"))

        # (4) 단서 프림 × 낙차 발자국 교차 0 (VG-01 의 실효 조건)
        cue_roots = ("/RailS", "/RailN", "/Tactile", "/Nosing", "/Sign",
                     "/Bollard", "/Delineator", "/GKitPlaza", "/GKitWalk",
                     "/TreeGrate", "/Shadow", "/Dress")
        over = []
        for prim in stage.Traverse():
            p = str(prim.GetPath())
            if not p.startswith(ROOT) or not prim.IsA(UsdGeom.Gprim):
                continue
            tail = p[len(ROOT):]
            if not any(tail.startswith(g) for g in cue_roots):
                continue
            if tail.startswith("/Dress/Far_"):
                continue                     # 원경(x ≥ 26) — 높이맵 격자 밖
            try:
                b = bbc.ComputeWorldBound(prim).ComputeAlignedRange()
            except Exception:
                continue
            if b.IsEmpty():
                continue
            mn, mx = b.GetMin(), b.GetMax()
            if not (mx[0] > GRID["x0"] and mn[0] < GRID["x1"]):
                continue
            # 발자국은 **양측** |y| ∈ [y_lip, y_toe]
            if ((mx[1] > HZ["y_lip"] and mn[1] < HZ["y_toe"])
                    or (mx[1] > -HZ["y_toe"] and mn[1] < -HZ["y_lip"])):
                over.append((p, round(float(mn[1]), 3), round(float(mx[1]), 3)))
        if over:
            ok = False
        print(f"[selfcheck] (4) 단서 프림 × 발자국(|y| ∈ [{HZ['y_lip']:.2f}, "
              f"{HZ['y_toe']:.2f}]) 교차 {len(over)}건"
              + (f" {over[:6]}" if over else " · OK "
                 "→ `cells_raw`·`polar_gt` 는 cue_* 에 구성상 불변"))

        # (5) 섹터 분포 — 이 씬의 산출물
        h = _sector_hist(3.0, 10.0, n=400, seed=13, step=0.40)
        print("[selfcheck] (5) LAT 밴드 섹터 분포 (MC 400포즈) · any_pos "
              f"{h['any_pos']:.3f} · 프레임당 양성셀 {h['cells_per_frame']:.2f}")
        print("              섹터 양성률  " + " · ".join(
            f"{k} {v:.3f}" for k, v in h["pos_rate"].items()))
        print("              셀 점유율    " + " · ".join(
            f"{k} {v:.3f}" for k, v in h["cell_share"].items()))

        print(f"[selfcheck] sceneL1 {'통과' if ok else '실패'}")
        return ok

    # -------------------------------------------------------------------
    # 조립
    # -------------------------------------------------------------------
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()

    build_terrain(M)                                   # ① 경로 (팔 불변)
    if cfg["hazard_stairs"]:                           # ② 위험 — hazard 분기 2줄
        build_hazard(M)
    else:
        build_flat_fill(M)

    # ③ 단서 — **어느 것도 hazard 분기 안에 있지 않다** (프림 위생 1 · s14 파라펫 교훈)
    if cfg["cue_railing"]:
        build_railing(M)
    if cfg["cue_tactile"]:
        build_tactile(M)
    if cfg["cue_nosing"]:
        build_nosing(M)
    if cfg["cue_sign"]:
        build_sign(M)
    if cfg["cue_bollard"]:
        build_bollards(M)
    if cfg["cue_delineator"]:
        build_delineators(M)
    if cfg["cue_manhole"] or cfg["cue_tree_grate"] or cfg["cue_slab_joint"] \
            or cfg["cue_drainage"]:
        build_ground_kit(M)
    if cfg["cue_shadow_caster"]:
        build_shadow_casters(M)
    if cfg["cue_scene_dressing"] or KEEP_DRESSING:
        # `KEEP_DRESSING` 은 hazard=False 팔에서 장식을 ON 변환 그대로 유지시킨다.
        #   이 씬의 장식은 전부 외안 지반(z = 0.000)과 광장(z = −0.32)에 앵커되고
        #   **둘 다 hazard 토글 밖**이므로 sceneC2 의 "하부 앵커 드레싱 소실 →
        #   ground_z 이동" 사고가 구조적으로 불가능하다.
        build_dressing(M)

    if not scene_selfcheck():
        raise SystemExit("sceneL1 self-check 실패")

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    if smoke_mode:
        n = sum(1 for _ in stage.Traverse())
        print(f"[SMOKE] sceneL1 조립 완료 · 프림 {n}개 · 조기 종료")
        simulation_app.close()
        return

    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    _v0 = build_views()["levee_over"]
    look_from(_v0["eye"], _v0["tgt"])

    pt_spp = int(PARAMS["render"]["pt_total_spp"])

    def set_render_mode(mode):
        if mode == "PathTracing":
            settings.set("/rtx/pathtracing/spp", 1)
            settings.set("/rtx/pathtracing/totalSpp", pt_spp)
            settings.set("/rtx/pathtracing/optixDenoiser/enabled", True)
            settings.set("/rtx/pathtracing/maxBounces",
                         int(PARAMS["render"]["pt_max_bounces"]))
            settings.set("/rtx/rendermode", "PathTracing")
        else:
            settings.set("/rtx/rendermode", "RaytracedLighting")

    os.makedirs(LOOKCHECK_DIR, exist_ok=True)

    if capture_mode:
        out_dir = os.path.join(LOOKCHECK_DIR, "auto")
        sc.capture_pipeline(simulation_app, build_views(), out_dir,
                            set_render_mode, look_from)
        simulation_app.close()
        return

    input_iface = carb.input.acquire_input_interface()
    appwindow = omni.appwindow.get_default_app_window()
    K = carb.input.KeyboardInput
    rot_step = float(PARAMS["light"]["dome_rotation_step"])
    dome_user_rot = [0.0]

    def capture(path):
        vp = get_active_viewport()
        capture_viewport_to_file(vp, file_path=path)

    def on_key(event, *args):
        if event.type != carb.input.KeyboardEventType.KEY_PRESS:
            return True
        if event.input == K.P:
            cur = settings.get("/rtx/rendermode")
            if cur == "PathTracing":
                set_render_mode("RaytracedLighting")
                print("[렌더] RTX Real-Time (이동용)")
            else:
                set_render_mode("PathTracing")
                print(f"[렌더] PathTracing (totalSpp={pt_spp})")
        elif event.input == K.C:
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            fp = os.path.join(LOOKCHECK_DIR, f"sceneL1_{ts}.png")
            capture(fp)
            print(f"[캡처] {fp}")
        elif event.input == K.LEFT_BRACKET:
            dome_user_rot[0] -= rot_step
            apply_dome_rot(dome_user_rot[0])
            print(f"[태양 방위] 오프셋 {dome_user_rot[0]:+.0f}°")
        elif event.input == K.RIGHT_BRACKET:
            dome_user_rot[0] += rot_step
            apply_dome_rot(dome_user_rot[0])
            print(f"[태양 방위] 오프셋 {dome_user_rot[0]:+.0f}°")
        return True

    keyboard_sub = input_iface.subscribe_to_keyboard_events(
        appwindow.get_keyboard(), on_key)

    print("=" * 64)
    print(BANNER)
    print("-" * 64)
    print("※ 키가 안 먹으면 Isaac Sim 창을 한 번 클릭해서 포커스를 줘!")
    print("=" * 64)

    while simulation_app.is_running():
        simulation_app.update()

    input_iface.unsubscribe_to_keyboard_events(
        appwindow.get_keyboard(), keyboard_sub)
    simulation_app.close()


# ===========================================================================
# CPU 자기검사 — pxr·GPU 없이 횡단면과 섹터 분포를 재계산한다
# ===========================================================================
def _geometry_selfcheck():
    T, HZ = PARAMS["terrain"], PARAMS["hazard"]
    ok = True

    def chk(tag, cond, msg=""):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  [{'PASS' if cond else 'FAIL'}] {tag}" + (f" — {msg}" if msg else ""))

    print("=" * 70)
    print("sceneL1_lateral_canal — CPU 자기검사 (pxr·GPU 불필요)")
    print("=" * 70)

    drop = T["walk"]["z"] - HZ["fill_top"]
    chk("측방 낙차 = 1.5 m [브리프 §2.3]", abs(drop - 1.5) < 1e-9, f"{drop:.3f} m")
    chk("반사실 채움면 = 산책로 레벨",
        abs(HZ["fill"]["z"] - T["walk"]["z"]) < 1e-9, f"{HZ['fill']['z']}")
    chk("외안 지반 = 채움면 (hazard OFF 에서 완전 평탄)",
        abs(T["farbank"]["z"] - HZ["fill"]["z"]) < 1e-9, f"{T['farbank']['z']}")
    chk("개거 개구가 갓돌 안쪽에 있다",
        HZ["fill"]["y0"] < HZ["y_lip"] < HZ["y_toe"] < HZ["fill"]["y1"],
        f"{HZ['fill']['y0']} < {HZ['y_lip']} < {HZ['y_toe']} < {HZ['fill']['y1']}")
    chk("인버트가 낙차 바닥보다 아래 (통수/자갈 12 cm)",
        HZ["invert_z"] < HZ["fill_top"],
        f"인버트 {HZ['invert_z']:+.2f} < 바닥 {HZ['fill_top']:+.2f}")

    # 개거 가시성 — 가림체가 없어도 낙차 내부는 갓돌에 잘린다 (파일 상단 §개거 가시성)
    lip0, toe0 = HZ["y_lip"], HZ["y_toe"]
    frac = lip0 / toe0
    vis = {h: round((1.0 / frac - 1.0) * h, 3) for h in (0.4, 1.0, 1.4)}
    h_need = (T["walk"]["z"] - HZ["fill_top"]) / (1.0 / frac - 1.0)
    print(f"  [info] 개거 가시 깊이 (근단 갓돌 차폐) — h 0.4 → {vis[0.4]} m · "
          f"h 1.0 → {vis[1.0]} m · h 1.4 → {vis[1.4]} m / 낙차 "
          f"{T['walk']['z'] - HZ['fill_top']:.2f} m")
    chk("바닥이 보이려면 밴드 밖 눈높이가 필요하다 (낙차는 폐영역으로 축약된다)",
        h_need > 1.9, f"바닥 가시 최소 눈높이 {h_need:.2f} m > base 밴드 상한 1.90 m")

    # ── 스텝 게이트 도달성 (파일 상단 §스텝 게이트 · 개정 R2 의 사유) ────────────
    d_reach = -GRID["x0"] + math.sqrt(3.0) * lip0
    print(f"  [info] 스텝 게이트 — 립만으로 근접 경계가 생기는 한계 거리 "
          f"d ≤ {d_reach:.2f} m (= −x₀ + √3·y_lip) · LAT 밴드 상한 10.0 m")
    cul = [(c, c + HZ["culvert_w"]) for c in HZ["culverts"]]
    in_grid = [c for c in cul if c[1] > GRID["x0"] and c[0] < GRID["x1"]]
    chk("횡단 복개가 격자 안에 **2개소 이상** (스텝 게이트 근접 경계 공급)",
        len(in_grid) >= 2,
        f"격자 안 복개 {in_grid} · 립만으로는 d > {d_reach:.2f} m 에서 GT 가 0 이 된다 "
        "[실측 260823_v3p5_h3l1probe_A: d 8.50·8.69 → cells_kept 0]")
    # 복개 동단이 만드는 경계가 LAT 밴드 상단에서도 폴라 격자 안의 성분을 살리는가 —
    #   d = 10 에서 측방 창은 x ∈ [u_lo − 10, u_hi − 10] 이고 그 구간이 복개 **동쪽**
    #   성분(= 경계를 가진 성분)과 겹쳐야 한다.
    u_lo = lip0 / math.tan(math.radians(31.10))     # 측방 창(A·E)의 u 하한
    x_lo_d10 = max(GRID["x0"], u_lo - 10.0)
    east0 = in_grid[0][1]
    chk("d = 10 에서 측방 창이 경계 보유 성분과 겹친다",
        x_lo_d10 < GRID["x1"] and east0 < 10.0 + 0.9,
        f"측방 창 x ≥ {x_lo_d10:+.2f} · 첫 복개 동단 x = {east0:+.2f}")

    # 난간이 발자국 밖인가 (VG-01 의 실효 조건 · 자기검사 (4) 의 해석판)
    r = PARAMS["rail"]
    rail_out = r["y"] + r["post_a"] / 2.0
    chk("난간이 낙차 발자국 밖", rail_out < HZ["y_lip"],
        f"난간 외측 |y| {rail_out:.3f} < 발자국 근단 {HZ['y_lip']:.2f} "
        f"(여유 {HZ['y_lip'] - rail_out:.3f} m)")

    # 종단면 연속성: 0.05 m(= 높이맵 격자 피치) 간격 인접 표고차 ≤ 계단 라이즈
    prev, worst, worst_x = None, 0.0, None
    x = -14.0
    while x <= 13.9 + 1e-9:
        z = _profile_z(x)
        if prev is not None and abs(z - prev) > worst:
            worst, worst_x = abs(z - prev), x
        prev = z
        x = round(x + 0.05, 4)
    chk("종단면 연속 (0.05 m 격자)", worst <= T["step"]["riser"] + 1e-6,
        f"최대 단차 {worst:.4f} m @x={worst_x} ≤ 라이즈 {T['step']['riser']:.4f}")

    # ── 섹터 설계 검증 — **이 씬의 핵심 산출물** ─────────────────────────────
    lip, toe = HZ["y_lip"], HZ["y_toe"]
    t_a, t_b = math.tan(math.radians(18.66)), math.tan(math.radians(31.10))
    t_c = math.tan(math.radians(6.22))
    u_ae = (lip / t_b, toe / t_a)
    u_bd = (lip / t_a, toe / t_c)
    u_c = lip / t_c
    print(f"  [info] 섹터 창 (y_c≈0 근사) — A·E u ∈ [{u_ae[0]:.2f}, {u_ae[1]:.2f}] · "
          f"B·D u ∈ [{u_bd[0]:.2f}, {u_bd[1]:.2f}] · C u ≥ {u_c:.1f}")
    chk("C 섹터가 구성상 비어 있다 (경로 정면 무해)",
        math.hypot(u_c, lip) > 12.0,
        f"C 최소 반경 {math.hypot(u_c, lip):.1f} m > 격자 외반경 12.0 m")
    chk("A·E 창이 LAT 밴드 전 구간에서 격자 안에 있다",
        u_ae[0] <= 10.0 + 14.0 and u_ae[0] >= 3.0 - 2.0,
        f"A·E 하한 u {u_ae[0]:.2f} · d=3 → x {u_ae[0] - 3.0:+.2f} · "
        f"d=10 → x {u_ae[0] - 10.0:+.2f}")

    h_lat = _sector_hist(3.0, 10.0, n=1200, seed=17, step=0.25)
    h_base = _sector_hist(1.2, 12.0, n=800, seed=19, step=0.30)
    h_ny = _sector_hist(3.0, 10.0, n=600, seed=23, step=0.25, yaw_sd=0.0)
    print(f"  [info] LAT 밴드 (d 3–10) · any_pos {h_lat['any_pos']:.3f} · "
          f"프레임당 양성셀 {h_lat['cells_per_frame']:.2f}/20")
    print("         섹터 양성률  " + " · ".join(
        f"{k} {v:.3f}" for k, v in h_lat["pos_rate"].items()))
    print("         셀 점유율    " + " · ".join(
        f"{k} {v:.3f}" for k, v in h_lat["cell_share"].items()))
    print(f"  [info] base 밴드 (d 1.2–12) · any_pos {h_base['any_pos']:.3f} · "
          f"프레임당 양성셀 {h_base['cells_per_frame']:.2f}/20")
    print("         섹터 양성률  " + " · ".join(
        f"{k} {v:.3f}" for k, v in h_base["pos_rate"].items()))

    lat = h_lat["cell_share"]["A"] + h_lat["cell_share"]["E"]
    mid = h_lat["cell_share"]["B"] + h_lat["cell_share"]["D"]
    chk("위험 질량이 측방 섹터 A·E 에 집중 [§2.3 섹터 목표]", lat > mid,
        f"A+E {lat:.3f} > B+D {mid:.3f} (C {h_lat['cell_share']['C']:.3f})")
    chk("A·E 가 **둘 다** 채워진다 (양측 개거의 이유)",
        min(h_lat["pos_rate"]["A"], h_lat["pos_rate"]["E"]) >= 0.50,
        f"A {h_lat['pos_rate']['A']:.3f} · E {h_lat['pos_rate']['E']:.3f}")
    # **C 섹터의 정체** — 파일 상단의 기하 항등식은 카메라가 보행축을 정확히 향할 때
    #   (yaw = 0) 성립한다. 실제 샘플러는 yaw ~ trunc-N(0, 8, ±20) 이므로 측방 위험이
    #   카메라 회전만큼 중앙 쪽으로 밀려 들어온다 — **씬 기하가 아니라 카메라 자세**의
    #   기여다. 두 수치를 나란히 인쇄해 그 구분을 기계가 보이게 한다.
    print(f"  [info] yaw 지터 OFF (yaw≡0) · C 셀 점유율 "
          f"{h_ny['cell_share']['C']:.4f} · A+E {h_ny['cell_share']['A'] + h_ny['cell_share']['E']:.3f}")
    chk("C 섹터는 **씬 기하로는** 비어 있다 (yaw≡0 MC 로 항등식 확인)",
        h_ny["cell_share"]["C"] == 0.0, f"yaw≡0 C {h_ny['cell_share']['C']:.4f}")
    chk("yaw 지터가 넣는 C 몫이 측방의 1/10 이하",
        h_lat["cell_share"]["C"] <= 0.10 * lat,
        f"C {h_lat['cell_share']['C']:.4f} ≤ 0.1 × (A+E {lat:.3f}) = {0.1 * lat:.4f}")
    chk("LAT 밴드에서 발자국이 격자 안에 있다 (none_in_fov 이 예외)",
        h_lat["any_pos"] >= 0.90, f"any_pos {h_lat['any_pos']:.3f}")

    ds = DATUM_STRIP
    cross = [z for z in GATED_ZONES
             if not (z[3] <= ds["x0"] or z[2] >= ds["x1"]
                     or z[5] <= ds["y0"] or z[4] >= ds["y1"])]
    dfail = [(z[0], z[6]) for z in cross if z[6] > DATUM_TOL]
    dtol = [(z[0], z[6]) for z in cross if z[6] <= DATUM_TOL]
    chk("VG-datum 선언 검사 (datum_fail 0)", not dfail,
        f"datum_tol {dtol} · datum_fail {dfail}")

    chk("표준 장비 16키", len(SCENE_CONFIG) == 16, f"{len(SCENE_CONFIG)}키")
    declared = set(CUE_CLASS) - {"_structural"}
    cue_keys = {k for k in SCENE_CONFIG if k.startswith("cue_")}
    chk("CUE_CLASS 가 모든 cue_* 를 분류", declared == cue_keys,
        f"미분류 {sorted(cue_keys - declared)} · 초과 {sorted(declared - cue_keys)}")

    print(f"\n  ⇒ sceneL1 CPU 자기검사 {'통과' if ok else '실패'}")
    print("=" * 70)
    return ok


if __name__ == "__main__":
    main()
