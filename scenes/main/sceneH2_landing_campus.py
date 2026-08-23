# -*- coding: utf-8 -*-
"""
sceneH2_landing_campus.py — NegObs 신규 씬 H2: 광장 계단참 + 선큰 광장 대계단 (Isaac Sim 4.5)

계열    : **계단참형 자기가림 (paired-H)** · 생활권 = **캠퍼스 경로**
정본    : `experiments/v3_0823/RENDER_PLAN_V3.md` §2.0(공통 표준) · §2.1 표 `sceneH2_landing_campus`
          · §2.6(CUE_CLASS 사전 분류) · §3.1–3.2(test-ext 사양·paired-H 회계)
분리    : **test-ext** — v2·v3 **양 모델 모두 미학습**. 훈련·검증에 절대 넣지 않는다(§3.1).
          **4팔 전부 제작 의무**(DZ §4.2 `:243`) — A·B·C·D 완비.
밴드    : base · **H**  (씬당 팔당 48컷 · 4팔 합 192)
승계    : `scene_common.py` · `ground_kit.py`(P1 plaza_granite) · `infra_kit`

────────────────────────────────────────────────────────────────────────────
**계열 신설 선언** — 이 씬은 v3 자기가림 3계열 중 **세 번째 계열의 첫 구현**이다.
  · 둔덕형(H6 val · H1 test-ext) : **종단면** 문제 하나로 닫히고 **림 조건**이 실효 구속
  · 복도 굴절형(H7 val)          : **평면** 문제 하나로 닫히고 수직은 항상 폐합
  · **계단참형(본 씬)**          : 종단면 문제이지만 **내부 조건이 실효 구속** — 가림체
    (계단참 상단 슬래브)가 낙차 림과 **같은 높이**에 있어 "림 위의 여유 높이"가 0 이기 때문이다.
계열마다 실패 모드가 다르다는 것이 §3.5 가 "2계열 이상"을 요구한 이유이고, 본 씬이
그 세 번째 축을 test-ext 에 세운다.

**부지 분리 (§2.1 각주 · §12-9 무대 순도)**: 캠퍼스 생활권의 기존 씬(s01·s10·s16·s20·C1·C4)과
`sceneH6/H7`(제방·보도) 어느 것과도 부지·드레싱·재질을 공유하지 않는다 — 화강석 판석 광장 +
선큰 대계단 + 적벽돌 강의동 + 식재 테라스 조합은 코퍼스에 전례가 없다.

────────────────────────────────────────────────────────────────────────────
씬 조립 공식 (4요소 — 브리프 §2.0)
  ① 경로   광장 진입 보행로(z 0.00) → **계단참**(LandingSlab, 폭 3.63 m, 화강석 판석)
  ② 위험   계단참 **아래 하행 4단**(R 0.18 · T 0.35) → 중간참 → 하행 4단 → **선큰 광장**
           (z −1.44). 낙차 = **1.440 m**
  ③ 단서   양측 핸드레일 · 계단참 코 논슬립 인레이 · 점형블록 · 바닥 재질전이 · 캠퍼스
           안내표지 · 화단 테라스 경계 난간 · 가로수 그림자 · 맨홀 · 줄눈 · 빗물받이 · 볼라드
  ④ 은닉   **LandingSlab** — 계단참 **상단 답면**이 하행 단 전체를 덮는다. 스침각에서
           8단 전부와 중간참·선큰 광장이 계단참 코 뒤로 사라지고, 화면에는 광장이
           **끊김 없이 이어지는 것처럼** 보인다.

*"주변 환경은 장식이 아니라 단서 ③ 그 자체다"* — 계단만 덩그러니 만들면 이 씬은 실패다.

────────────────────────────────────────────────────────────────────────────
좌표계 · 종단면 (walk axis = +X, Z-up, m. 카메라는 x = −d 에 서서 +X 를 본다)

    x              z        무엇                                프림
  ≤ −4.20        0.000     광장 진입 보행로 (화강석 판석)      Plaza/Approach
  −4.20→−0.575   0.000     **계단참** (진회색 화강석 판석)     **LandingSlab**  ← ④ 은닉체
  −0.575→ 0.825 −0.18…−0.72 하행 4단 (R 0.18 · T 0.35)         Stair/Up_0..3    ← ② 위험
   0.825→ 2.325 −0.720     중간 계단참 (폭 1.50 m)             MidLanding/Slab
   2.325→ 3.725 −0.90…−1.44 하행 4단                            Stair/Dn_0..3
   3.725→11.000 −1.440     선큰 광장 바닥                       LowerPlaza/Floor
  11.000→11.300 −1.44→1.10 강의동 **석재 기단**(포디엄)          Building/Plinth ← 구조물(팔 불변)
  ≥ 11.300       9.500     강의동 (적벽돌 · 저층부 유리)        Building/Mass   ← 구조물(팔 불변)
    측방 (팔 불변 지형)
  −12.0→−5.0 · y 4.40→9.20  +0.360   식재 테라스                Plaza/Terrace
  −10.6→−6.4 · y 4.00→4.40  +0.180   테라스 진입 2단            Plaza/TerraceStep

  낙차 = 0.000 − (−1.440) = **1.440 m** (8단 × 라이즈 0.18 · 트레드 0.35 · 중간참 1.50 m)
  [규격] 라이즈 0.18 ≤ 0.18 · 트레드 0.35 ≥ 0.26 · 중간참 1.50 ≥ 1.20 — 건축물의 피난·방화구조
         등의 기준에 관한 규칙 §15 옥외계단 규정 안.

────────────────────────────────────────────────────────────────────────────
H 수율 설계 (§3.2 · 이 씬이 존재하는 이유)

가림은 **계단참 코 C = (−0.575, 0.00)** 를 스치는 시선 하나로 닫힌다. 눈 E = (−d, h),
C 를 지나는 직선의 기울기 s = (0 − h)/(d − 0.575):

  · 낙차 **림** 은닉 : 발자국 근단(2단째 상면 −0.36)의 립 점 = (−0.225, **−0.18**)
        (`labeler.edge_points` 는 립의 z 로 **보행 가능측**, 즉 1단 상면을 쓴다)
        조건 s ≥ (−0.18 − 0)/(−0.225 + 0.575) = **−0.5143**
  · 낙차 **내부** 은닉 : 선큰 광장 바닥이 강의동 외벽에 닿는 x = 11.00 · z = −1.44
        조건 s ≥ (−1.44 − 0)/(11.00 + 0.575) = **−0.1244**

  |s_int| > |s_rim| 이므로 **내부가 실효 구속**이다 — H6/H1(둔덕형)과 **정반대**이며,
  그 이유는 위 "계열 신설 선언"에 적은 대로 가림체가 림보다 높지 않기 때문이다.

⇒ H 조건 : h ≤ 0.1244 · (d − 0.575)

  d      h_max     H밴드[0.25,1.0] 통과율    base[0.25,1.9] 통과율
  2.0     0.177           0.00                     0.00
  4.0     0.426           0.24                     0.11
  6.0     0.675           0.57                     0.26
  8.0     0.924           0.90                     0.41
  10.0    1.173           1.00                     0.56
  12.0    1.421           1.00                     0.71
  ---------------------------------------------------------------------------
  밴드 적분 (d ~ LogU · CPU 자기검사가 매 실행 인쇄) : **H 0.88 · base 0.18**

  계획 §3.2 가정 = H 밴드 수율 **0.50** (24컷 × 0.5 = paired-H ≥ 12).
  설계 기대 A팔 48컷 = 24·0.18 + 24·0.88 ≈ **26** — 하한 12의 **2.1 배**.
  **퇴화 아님**: base 밴드의 82 %는 V/E 로 남는다.

**왜 강의동 외벽이 x = 11.00 에 서는가 — 격자 셀 중심 정렬 (설계 판단)**
높이맵 격자는 `x0 = −2.00 · step = 0.05` 이므로 **x = 11.00 은 정확히 셀 중심**이다.
선큰 광장의 마지막 발자국 셀은 10.95, 셀 11.00 의 수직 레이는 강의동 지붕(+9.50)에 맞는다.
따라서 ⓐ 발자국은 x ≤ 10.95 에서 끝나고 ⓑ H 프레임에서 보이는 **외벽면 픽셀은 셀 11.00 으로
반올림**되어 **발자국 밖**이 되므로 `int_px` 에 들어가지 않는다. 벽면을 셀 경계에 두면
깊이 양자화(±0.02 m)가 반올림을 뒤집어 프레임마다 판정이 흔들린다 — **셀 중심 정렬은
이 씬의 H 판정을 깊이 잡음으로부터 격리하는 장치**다.

**모서리 소속 게이트(VG-06) 적합성**: H 프레임에서 가시 지면의 종단 모서리는 **계단참 코**이며
그 소유자는 `LandingSlab` 이다. 계단 8단·중간참·선큰 광장은 전부 코 그림자 안이므로 **낙차
구조물의 화면 기여 = 0 px**. 브리프의 명시 요구 — *"노징 프림은 **자립 데칼**로 지어 모서리
주인이 되지 않게 한다"* — 는 다음 두 장치로 이행한다:
  ⓐ 계단참 코의 논슬립 띠는 **매입형 인레이**(proud 2 mm)이고 코에서 **45 mm 안쪽**에 앉는다.
     융기 2 mm × 후퇴 45 mm 이면 기울기 0.044 이하의 어떤 시선도 코를 가리지 못한다
     (H 밴드 최대 |s| = 0.145 ≫ 0.044 이므로 **구성상** 안전하다).
  ⓑ 하행 8단의 계단코 논슬립 띠는 `cue_nosing` 이 아니라 **`build_hazard` 가 짓는다**.
     계단이 없으면 존재할 수 없는 부재이므로 이것은 계획 §4.4.1 이 정의한 *"낙차 자신의
     기하"*(F·E 부류)이지 토글 가능한 단서가 아니다. `cue_nosing` 이 토글하는 것은
     **팔 불변 지면 위의 띠**(계단참 코 인레이 + 테라스 진입 2단)뿐이다.

────────────────────────────────────────────────────────────────────────────
**계단참형이 강제하는 단서 배치 규율 (본 씬이 새로 확정하는 설계 법칙)**

둔덕형·굴절형에서는 가림체가 낙차와 **그 위에 선 단서까지 함께** 가린다(H7 의 벽면 손잡이가
슬롯 안에 있어도 strict-H 가 성립한 이유). 계단참형은 다르다 — 가림체가 가리는 것은
**코 평면 아래**뿐이므로, 낙차 위로 **솟은** 프림은 무엇이든 보인다. 그리고 라벨러의
`int_px` 는 *"발자국 셀에 재투영되고 z_off 보다 0.15 m 이상 낮은 픽셀"* 을 세므로,
계단 위에 선 손잡이·기둥은 **보이면서 동시에 발자국 셀에 속하는** 픽셀을 만들어
**strict-H 를 원리적으로 깨뜨린다**.

⇒ 이 씬의 **모든 `cue_*` 프림은 계단참 코보다 뒤(x ≤ −0.575)** 또는 **측방 팔 불변 지면**에
   선다. 핸드레일도 예외가 아니다 — 진입 보행로 양측을 따라와 점형블록에서 **0.30 m 수평
   연장 후 종단**한다(편의증진법 시행규칙 별표1 이 요구하는 그 연장이다). 계단 위의 중간
   손잡이는 **의도적으로 두지 않으며**, 그 사실과 이유를 여기에 남긴다.

────────────────────────────────────────────────────────────────────────────
프림 위생 · 데이텀 (CUE_COVERAGE §4-4 (2)(3)(4))

1. **단서 빌더는 어느 것도 `if cfg["hazard_*"]` 안에 있지 않다** — 조립부의 hazard 분기는 2줄.
2. **모든 `cue_*` 프림은 낙차 발자국(x ≥ −0.225) 밖**이다. 자기검사 (4) 가 스테이지 전수
   AABB 로 매 조립마다 확인한다 → `cells_raw`·`polar_gt` 는 `cue_*` 토글에 **구성상 불변**.
3. **카메라 데이텀 스트립** `x ∈ [−12.05, −1.15] · |y| ≤ 0.95` 는 전 구간 z = 0 의 단일
   평면(광장 + 계단참)이며, 그 위에서 상면을 움직이는 토글 프림은 점형블록(4 mm)과
   지면문양(≤8 mm)뿐이다 — 전부 `datum_tol`, `datum_fail` **0건**.
4. **void 커버리지 1.0** (VG-void): 계단 8단 + 중간참 + 선큰 광장 + 강의동이
   x ∈ [−0.575, 14.0] 을 빈틈없이 덮는다. 개방 바닥 0.

표준법: 법1 온전 상태만(`surface=None`) · 법2 법정 제식 표지 1매 · 법4 손잡이·볼라드·측구는
기능 필수, 조형물 0 · 법5 차량·계절소품 0 · 법6 신규 재질 역할 0 · 법7 `cue_*` 최대 융기
12 mm(발자국 밖) · 법8 수치 주석에 근거 태그.

실행
    unset PYTHONPATH VIRTUAL_ENV; conda activate env_isaaclab; export PYTHONNOUSERSITE=1
    python scenes/main/sceneH2_landing_campus.py                 # GUI 룩체크
    NEGOBS_SMOKE=1 python scenes/main/sceneH2_landing_campus.py   # CPU 조립 스모크
데이터 렌더 진입점 (신설 씬은 AZ 원장 등재 전까지 이 경로가 유일 — CUE_COVERAGE §4-4 (6)):
    python experiments/v3_0823/code/h67_probe.py --scene sceneH2 --run <stamp> ...
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


# [계획 §2.0] 생활권 = 캠퍼스 경로. 계절은 **봄** — 제방 계열(H1 초가을 · H6 여름)과
#   보도 계열(H7 여름)에서 톤을 분리한다.
SEASON = "spring"


# ===========================================================================
# [A0] CUE_CLASS — 렌더 **전** 사전 분류 (RENDER_PLAN_V3 §2.6 / ACCOUNTING §2-6)
# ===========================================================================
#   렌더 후 VG-01/VG-02 가 이 선언을 **기계 반증**한다. 선언과 실측이 어긋나면 그 씬은
#   **씬 결함**으로 반려하며, 결과를 보고 이 표를 고치지 않는다.
CUE_CLASS = {
    "cue_railing":         "decorative",   # 진입 보행로 양측 핸드레일 (계단 위에는 없다 — 위 규율)
    "cue_tactile":         "decorative",   # 계단 상단 점형블록 (계단참 위, proud 4 mm)
    "cue_nosing":          "decorative",   # 계단참 코 매입 인레이 + 테라스 2단 띠 (팔 불변 지면)
    "cue_material_break":  "decorative",   # **재질 재바인딩 전용** — 프림 집합 불변
    "cue_sign":            "decorative",   # 캠퍼스 시설 안내표지 1매 (법정 제식)
    "cue_scene_dressing":  "decorative",   # 테라스 관목·벤치·가로수·원경 건물동
    "cue_shadow_caster":   "decorative",   # 광장 가로수 열 + 가로등 — 그림자 밴드 캐스터
    "cue_manhole":         "decorative",   # 광장 맨홀 (flush)
    "cue_tree_grate":      "decorative",   # 광장 수목보호격자 (flush)
    "cue_slab_joint":      "decorative",   # 판석 신축·수축줄눈 (flush)
    "cue_drainage":        "decorative",   # 광장 빗물받이 (flush)
    "cue_bollard":         "decorative",   # 광장 진입 차량 억제 볼라드
    # [FA_REALITY §3 사다리 L1 ★1] 지상 화단 둘레 난간. 추락방지 난간 법정 의무는
    #   「옥상광장·2층 이상 노대」에 1.2 m 이상이고 **지상 화단에는 없다** — 조경 경계 목적.
    #   음성 씬 전용 키를 **양성 씬에 심어** base rate 독립을 한 씬 안에서 강제한다
    #   (`cue_shadow_caster` 역지름길 경보와 같은 논리, §2.0).
    "cue_planter_edge":    "decorative",
    # ── 토글 금지 목록 (구조물). 어떤 cue_* 도 이 프림들을 참조하지 않는다 ────────────
    "_structural":         ["LandingSlab", "Stair", "MidLanding", "LowerPlaza",
                            "Building", "Plaza/Terrace"],
}


# ===========================================================================
# [A] SCENE_CONFIG — **표준 장비 16키** (RENDER_PLAN_V3 §2.0 · CUE_COVERAGE §4-4 (1))
# ===========================================================================
#   구성: 공통 cue 6 + v3 신설 3 + FA_REALITY 승격 후보 4(`cue_slab_joint` 갭 5위 ·
#   `cue_drainage` 갭 3위 · `cue_bollard` L2 · `cue_planter_edge` L1) + hazard 1 +
#   팔 제어 2 = **16**. **사문 0** — 16키 전부를 읽는 코드가 이 파일 안에 있다.
SCENE_CONFIG = {
    # ── ② 위험: 유일한 기하 토글 ────────────────────────────────────────────
    #   False → 계단 8단·중간참·선큰 광장이 사라지고 계단참 레벨(z 0.00)의 평탄 지면이
    #   x = −0.575 … 11.00 을 채운다(반사실 보행 가능면 z_off).
    "hazard_stairs":      True,
    # ── ③ 단서: 공통 6키 ────────────────────────────────────────────────────
    "cue_railing":        True,   # 진입 보행로 양측 핸드레일 (편의증진법 시행규칙 별표1)
    "cue_tactile":        True,   # 점형블록 — 브리프 "점형블록" 명시 항목
    "cue_nosing":         True,   # 계단참 코 매입 인레이 + 테라스 2단 논슬립 띠
    "cue_material_break": True,   # 계단참 = 진회색 화강석 / 광장 = 밝은 화강석 판석
    "cue_sign":           True,   # 캠퍼스 시설 안내표지 (법2 — 법정 제식만)
    "cue_scene_dressing": True,   # 테라스 관목·벤치·가로수·원경 건물동
    # ── v3 신설 3키 (FA_REALITY §2) ─────────────────────────────────────────
    "cue_shadow_caster":  True,   # **양성 씬에도 동일 비율**(§2.0 역지름길 경보)
    "cue_manhole":        True,   # 갭 1위 (25.0)
    "cue_tree_grate":     True,   # 갭 2위 (20.0)
    # ── FA_REALITY 승격 후보 4키 ───────────────────────────────────────────
    "cue_slab_joint":     True,   # 갭 5위 — 판석 줄눈
    "cue_drainage":       True,   # 갭 3위 — 광장 빗물받이
    "cue_bollard":        True,   # L2 — 광장 진입 볼라드
    "cue_planter_edge":   True,   # L1 ★1 — 지상 화단 둘레 난간(낙차 없음)
    # ── 팔 제어 2키 ─────────────────────────────────────────────────────────
    "keep_dressing":      False,
    "placebo_remove":     False,
}


# ===========================================================================
# [B] PARAMS — 전 수치. 종단면은 파일 상단 표와 **한 글자도 어긋나지 않는다**
# ===========================================================================
PARAMS = dict(
    plaza=dict(
        y_half=11.0, base_z=-2.60,
        approach=dict(x0=-26.0, x1=-4.20, z=0.00),
        # **계단참** — ④ 은닉체. 폭 3.625 m(≥ 1.20 규정의 3배). 코 x = −0.575 는
        #   높이맵 셀 경계(−0.60/−0.55 중간)에 앉혀 1단·2단의 셀 귀속을 결정론으로 만든다.
        landing=dict(x0=-4.20, x1=-0.575, z=0.00),
        # 측방 식재 테라스 (팔 불변 지형) — `cue_planter_edge`·`cue_nosing` 의 캐리어
        terrace=dict(x0=-12.0, x1=-5.0, y0=4.40, y1=9.20, z=0.36),
        terrace_step=dict(x0=-10.6, x1=-6.4, y0=4.00, y1=4.40, z=0.18),
    ),
    # ── ② 위험 (hazard_stairs 전속) ────────────────────────────────────────
    hazard=dict(
        up=dict(x0=-0.575, riser=0.18, tread=0.35, n=4),      # 계단참 아래 하행 4단
        mid=dict(x0=0.825, x1=2.325, z=-0.72),                # 중간 계단참 1.50 m
        dn=dict(x0=2.325, riser=0.18, tread=0.35, n=4),
        lower=dict(x0=3.725, x1=11.00, z=-1.44),
        base_z=-2.60,
        nose=dict(width=0.055, proud=0.012),   # 계단 자신의 논슬립 코 (낙차 기하 · §4.4.1 F·E 부류)
        fill=dict(x0=-0.575, x1=11.00, z=0.00),
        # [computed] 낙차 = 0.00 − (−1.44) = 1.440 m
        #   발자국 근단 = 2단째 상면 −0.36 (hazard_depth 0.30 을 처음 넘는 단) → x = −0.225
    ),
    # ── 구조물 (팔 불변) ───────────────────────────────────────────────────
    #   강의동. **x0 = 11.00 은 높이맵 셀 중심** — 파일 상단 "셀 중심 정렬" 참조.
    # ── 강의동 기단 — **두 번 고친 자리다. 그 이력을 남긴다** ────────────────────
    #  R0 초안 : 기단을 x ∈ [10.94, 11.18] 에 두어 **선큰 광장 쪽으로 0.06 m 튀어나왔다**.
    #  R1 1차수정: 기단을 x ∈ [11.00, 11.24] 로 물리고 몸체를 11.12 로 밀었다. **여전히 틀렸다** —
    #     기단 상면이 −0.34(광장 레벨 아래)라 셀 11.00 의 수직 레이가 기단 상면을 맞았고,
    #     C팔 채움면(z 0, SEAM 으로 x 11.004 까지)은 그 셀에서 0 을 주었다.
    #     ⇒ diff 0.34 ≥ hazard_depth ⇒ **셀 11.00 이 발자국으로 뒤집혔고**, 그 셀에
    #     재투영되는 **기단 서측면 픽셀이 곧 `int_px`** 가 되어 strict-H 가 전멸했다
    #     [실측 260823_v3p5_h12probe_A: strict-H **0/8** · int_px 73–7999 ·
    #      ID 마스크 `Building/Plinth` 168,669 px].
    #  R2 확정 : 기단 상면을 **광장 레벨 위(+1.10)** 로 올리고 몸체를 11.30 으로 민다.
    #     이제 셀 11.00…11.25 의 수직 레이는 **양팔 모두 기단 상면 +1.10** 을 맞으므로
    #     diff = 0 → 발자국이 아니고, 기단 서측면 픽셀은 발자국 밖 셀로 반올림된다.
    #     교훈: **낙차 종단 평면에 접한 구조물의 상면은 반사실 채움면보다 높아야 한다.**
    #     선큰 광장에서 올라서는 석재 기단(포디엄)은 실제 건축의 표준 구성이기도 하다.
    building=dict(x0=11.00, x1=24.0, y0=-13.0, y1=13.0, z_top=9.50,
                  base_z=-1.44, plinth_top=1.10, plinth_x1=11.30, mass_x0=11.30,
                  bands=[(1.60, 3.00), (4.40, 5.80), (7.30, 8.70)]),
    # ── ③ 단서 파라미터 ─────────────────────────────────────────────────────
    #   전부 x ≤ −0.575(계단참 코 뒤) 또는 측방 팔 불변 지면. 발자국 위 단서 프림 0개.
    rail=dict(ys=(-2.40, 2.40), x0=-12.00, x1=-0.90, post_pitch=1.60,
              post_r=0.028, top_z=1.10, hand_z=0.86, hand_r=0.021),
    # [규격·정정 R4 · D82ⓐ] 핸드레일 0.85~0.90 m [편의증진법 시행규칙 별표1 8-라] ·
    #   난간 상단 1.10 m [**「도로안전시설 설치 및 관리지침」 2.3.3 나** 110 cm 표준].
    #   구 주석은 1.10 m 의 근거를 "건축법 시행령 §40" 으로 적었으나 §40 은 **옥상광장·
    #   2층 이상 노대 전용**이고 값도 1.2 m 다 — 오인용이었다
    #   [`Docs/surveys/cue_arrangement_survey.md` §1.1 정정 상자 · CUE_REGULATION_BASIS §3.1].
    # [정정 R4 · D82ⓐ] 구 주석은 x1 = −0.90 을 "점형블록에서 0.30 m 연장"이라 적었으나
    #   실측은 0.025 m 다. 실제 배치는 **접근 보행로 난간이 계단 코(x = −0.575)에서
    #   0.325 m 앞에서 종단**하는 것이고, 이 씬은 설계상 **계단 위에 손잡이가 없다**
    #   (CUE_CLASS 주석의 "계단 위에는 없다"). 편의증진법 별표2 는 계단 손잡이의 상·하부
    #   0.3 m 연장을 규정하므로 이는 **미달**이지만, ⓐ 광장 대계단 중앙부 손잡이 미설치는
    #   국내 실측 분포에 흔하고 ⓑ 손잡이 신설은 D82 ⓑ·ⓒ 가 금지한 **단서 증량**이라
    #   미수정으로 기록한다(REG_AUDIT §2 sceneH2-3).
    tactile=dict(x0=-1.475, x1=-0.875, y_half=9.0, proud=0.004),
    # [규격·개정 R4 · D82ⓐ] 점형블록 세로 0.40 → **0.60 m**(0.30 m 유닛 **2매**) ·
    #   계단 상단(x = −0.575)에서 **0.30 m 이격**.
    #   근거 ① 이격 — 「교통약자의 이동편의 증진법 시행규칙」 **별표1**(이동편의시설의
    #     구조·재질 등에 관한 세부기준) "위험장소 **0.3 m 전면**" · 블록 규격 0.3×0.3 m.
    #   근거 ② 세로폭 — 「도로안전시설 설치 및 관리지침 : 장애인 안전시설」 6.5.2 2)
    #     (= 국도건설공사 설계실무요령 7.5 가 전재): 세로폭 **30~90 cm 범위, 60 cm 표준**
    #     (0.30 m 유닛 2매). 같은 지침 6.6.7 가: *"**위험물과 마주치게 되는 방향에는
    #     60 cm 폭**, 보행 동선과 **평행한 방향으로는 30 cm 폭**"* — 이 밴드는 계단을
    #     **정면으로 가로지르므로 60 cm**. [웹 검증 2026-08-24]
    #     구 0.40 m 는 300 mm 모듈의 정수배가 아니라 **시공 불가 치수**였다.
    #   근거 ③ 가로폭 — 같은 항 "**대상 시설의 폭만큼**". 이 계단은 폭 18 m 대계단이라
    #     밴드도 |y| ≤ 9.0 이다. **밴드는 1개**(위험 경계 1곳) — D82 ⓐ.
    #   [면적] 0.60 × 18.0 = 10.80 m² (구 7.20). 코퍼스 대조: sceneN9 점형 1.08 m².
    nosing=dict(inlay_w=0.055, inlay_inset=0.045, inlay_proud=0.002,
                strip_w=0.055, strip_proud=0.012),
    sign=dict(x=-5.30, y=3.35, yaw=180.0, pole_h=2.20, w=0.62, h=0.62),
    # [규격] 볼라드 h 0.8~1.0 · φ0.10~0.20 · 간격 1.5 ± 0.1 · 반사띠 (user_feedback_v5_1 §2)
    #   y = −5.20 의 보차도 경계선과 나란한 열 — 카메라 데이텀 스트립(|y| ≤ 0.95) 교차 0.
    #   y = −6.10 : 가로수 열(y = −4.60)에서 **1.50 m** 이격 — LINT-1(PE-1 · 산림청 고시
    #   2-3(6)(가)1) 이 요구하는 수목–연석 이격 1.00 m 를 여유 있게 넘긴다.
    #   설계 시 y = −5.20 은 이격 0.60 m 로 LINT-1 ERROR 였다 [측정].
    bollard=dict(y=-6.10, xs=(-16.00, -14.50, -13.00, -11.50, -10.00),
                 r=0.078, h=0.92, band_z=0.70, band_t=0.09),
    planter=dict(curb_w=0.30, curb_proud=0.12, rail_h=0.45, rail_r=0.019,
                 post_pitch=1.75),
    gkit=dict(
        region=(-22.0, -8.60, -0.95, 8.60),
        manholes=[(-8.35, 2.75), (-15.10, -2.60)],
        gullies=[(-4.90, 6.10), (-12.40, -6.20)],
        tree_grates=[(-6.40, -4.60), (-13.40, -4.60), (-20.40, -4.60)],
    ),
    shadow=dict(
        # [FA_REALITY §2 4위] 그림자 밴드 캐스터. **양성 씬에도 동일 비율**(§2.0 경보).
        #   시선 통로 |y| ≤ 4.0 · x ∈ [−12, 0] 은 **비워 둔다** — 수관이 낙차를 가리면
        #   VG-06 의 모서리 소유가 계단참에서 수목으로 넘어간다.
        #   남측 열 `plaza_S` — 피치 7.0 m (조례 제7조1가 6~8 m) · 1수종(oak_pin = 플라타너스 대체)
        trees=[(-6.40, -4.60), (-13.40, -4.60), (-20.40, -4.60)],
        tree_h=8.6,
        lamps=[(-3.60, 5.30), (-9.80, -5.35), (-16.00, 5.30)],
        lamp_h=4.6, lamp_arm=1.05,
    ),
    dress=dict(
        # 테라스 관목 띠 — 식재 테라스 상면(z 0.36) 위
        hedge=[(-11.40, 5.00, -5.60, 6.10), (-11.40, 7.30, -5.60, 8.40)],
        shrub_h=0.80,
        #   벤치 yaw 는 **축값만** — J-3/J-5 지터 폐지(spec §1.2)를 LINT-7 이 강제한다.
        benches=[(-7.20, 3.05, 90.0), (-10.40, -3.05, 270.0)],
        #   북측 테라스 가로수 `terrace_N` — 피치 7.0 m · 1수종(ash)
        trees=[(-11.00, 6.60), (-4.00, 6.60)],
        tree_h=6.2,
        # 원경(placebo 물량군) — 선큰 광장 **너머**(x ≥ 26) · 높이맵 격자 밖이라 라벨 무관
        backdrop=[("B0", 27.0, 40.0, -30.0, -10.0, 17.0),
                  ("B1", 30.0, 44.0, 8.0, 28.0, 21.0)],
    ),

    # ── 재질 3단 (realism_v1_final §84) ─────────────────────────────────────
    material=dict(
        scale=dict(plaza_light=1.80, granite_dark=1.80, concrete_floor=1.70,
                   concrete_wall=2.0, brick_red=2.0, grass=1.4, gravel=1.2,
                   stone_flag=1.6, tactile=0.3, wood_dark=1.4),
        plaza_tint=(0.74, 0.73, 0.70),      # 밝은 화강석 판석 (알베도 0.30 대)
        landing_tint=(0.58, 0.575, 0.56),   # 진회색 화강석 — 재질전이의 대상
        stair_tint=(0.62, 0.62, 0.60),
        curb_tint=(0.55, 0.545, 0.53),
        grass_tint=(0.40, 0.54, 0.28),      # 봄 잔디
        wall_color=(0.32, 0.315, 0.30), wall_rough=0.62,
        brick_tint=(0.52, 0.36, 0.30),      # 적벽돌 (alb_max 0.40 이하)
        rail_color=(0.70, 0.71, 0.73), rail_metallic=0.78, rail_rough=0.33,
        nosing_color=(0.41, 0.39, 0.35), nosing_rough=0.70,
        band_color=(0.80, 0.52, 0.05),
        bollard_color=(0.62, 0.63, 0.63), bollard_metallic=0.5, bollard_rough=0.40,
        pole_color=(0.24, 0.24, 0.26), pole_metallic=0.6, pole_rough=0.5,
        lamp_color=(0.78, 0.78, 0.75), lamp_rough=0.4,
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        canopy_a=(0.030, 0.052, 0.020), canopy_b=(0.042, 0.066, 0.028),
        canopy_rough=1.0,
        glass_color=(0.20, 0.26, 0.28), glass_rough=0.12, glass_metallic=0.25,
        # [v5.1 §4 · 순백 대면적 금지] 원경 매스는 concrete 클래스(`BgConcrete`)로 얹어
        #   알베도 상한 0.34 를 받는다 (SCENE_H67_BUILD R4 교훈).
        backdrop_color=(0.30, 0.30, 0.29), backdrop_rough=0.75,
        iron_color=(0.14, 0.14, 0.15), iron_metallic=0.55, iron_rough=0.62,
    ),

    light=dict(
        hdri="qwantani_noon_puresky_4k.exr",
        dome_intensity=1000.0,
        noon_dome_rot=-110.0,
        noon_sun_enable=True, noon_sun_elev=49.79,
        noon_sun_intensity=2450.0, noon_sun_color=(1.0, 0.969, 0.935),
        hdri_sun_rotz_offset=233.5,
        dome_rotation_step=15.0,
    ),
    # 남측 가로수 열의 그림자가 **보행축을 가로질러** 계단참까지 닿도록.
    SUN_AZ_OFFSET=214.0,

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
            "[FATAL sceneH2] keep_dressing=True 는 hazard_stairs=False 를 요구한다 — "
            "위험이 켜져 있으면 보존할 것이 없고 그 팔은 A팔의 라벨 없는 복제가 된다.")
    if not SCENE_CONFIG.get("cue_scene_dressing", True):
        raise SystemExit(
            "[FATAL sceneH2] keep_dressing=True 와 cue_scene_dressing=False 는 모순이다 — "
            "장식이 바로 이 팔이 보존하려는 대상이다.")
if PLACEBO_REMOVE:
    if not SCENE_CONFIG.get("hazard_stairs", True):
        raise SystemExit(
            "[FATAL sceneH2] placebo_remove=True 는 hazard_stairs=True 를 요구한다 — "
            "플라시보 팔은 위험 ON 상태의 외형 대조군(D35)이다.")
    if KEEP_DRESSING:
        raise SystemExit(
            "[FATAL sceneH2] placebo_remove 와 keep_dressing 은 서로 다른 팔(P·C)이다.")
_ARM = ("C_hz0_cue1" if KEEP_DRESSING else
        "P_hz1_placebo" if PLACEBO_REMOVE else
        "hz%d_rail%d_tac%d_mat%d_dress%d" % (
            int(SCENE_CONFIG["hazard_stairs"]), int(SCENE_CONFIG["cue_railing"]),
            int(SCENE_CONFIG["cue_tactile"]), int(SCENE_CONFIG["cue_material_break"]),
            int(SCENE_CONFIG["cue_scene_dressing"])))
print(f"[sceneH2] arm={_ARM} keep_dressing={KEEP_DRESSING} "
      f"placebo_remove={PLACEBO_REMOVE}")


# ===========================================================================
# [C] 경로 상수 · 필요 텍스처 역할 · 데이텀 선언
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "sceneH2")

ASSET_ROLES = ["plaza_light", "granite_dark", "concrete_floor", "concrete_wall",
               "brick_red", "grass", "gravel", "stone_flag", "tactile",
               "wood_dark", "sign_info", "hdri", "mdl"]

DATUM_STRIP = dict(x0=-12.05, x1=-1.15, y0=-0.95, y1=0.95)
DATUM_TOL = 0.02

# 토글 프림의 XY 범위와 **지면 위 최대 융기 dz** 선언. `datum_selfcheck()` 가 이 표와
#   DATUM_STRIP 의 교차를 기계 검사하고, (2) 전수 AABB 가 같은 판정을 독립으로 다시 낸다.
GATED_ZONES = [
    # (tag, key, x0, x1, y0, y1, dz)
    ("Stair-Up",     "hazard_stairs",      -0.575,  0.825, -11.00, 11.00, 0.00),
    ("MidLanding",   "hazard_stairs",       0.825,  2.325, -11.00, 11.00, 0.00),
    ("Stair-Dn",     "hazard_stairs",       2.325,  3.725, -11.00, 11.00, 0.00),
    ("LowerPlaza",   "hazard_stairs",       3.725, 11.000, -13.00, 13.00, 0.00),
    ("FlatFill",     "hazard_stairs(off)", -0.575, 11.000, -13.00, 13.00, 0.00),
    # 핸드레일: |y| = 2.40 → 데이텀 스트립(|y| ≤ 0.95) **밖**. 교차 0.
    ("Rail-S",       "cue_railing",       -12.03, -0.87,  -2.44, -2.36, 1.10),
    ("Rail-N",       "cue_railing",       -12.03, -0.87,   2.36,  2.44, 1.10),
    # 점형블록: 계단 상단 0.30 m 이격 규정 위치가 스트립 동단(x −1.15)과 겹친다.
    #   융기 4 mm → `datum_tol`. 사전 선언하고 렌더 후 실측한다(VG-datum 3층의 취지).
    ("Tactile",      "cue_tactile",        -1.475, -0.875, -9.10,  9.10, 0.004),
    # 계단참 코 인레이: 코에서 45 mm 안쪽 · 융기 2 mm. 스트립 동단 밖(x > −1.15).
    ("Nosing-Inlay", "cue_nosing",         -0.675, -0.620, -11.00, 11.00, 0.002),
    ("Nosing-Terr",  "cue_nosing",        -10.60, -6.40,    3.94,  4.40, 0.012),
    ("Sign",         "cue_sign",           -5.65, -4.95,    3.00,  3.70, 2.20),
    ("Bollard",      "cue_bollard",       -16.09, -9.91,   -6.19, -6.01, 0.92),
    ("Planter",      "cue_planter_edge",  -12.05, -4.95,    4.35,  9.25, 0.57),
    ("GKit",         "cue_manhole/slab_joint/drainage",
                                          -22.00, -0.95,   -8.60,  8.60, 0.008),
    ("TreeGrate",    "cue_tree_grate",    -21.20, -5.60,   -5.40, -3.80, 0.004),
    ("Shadow-S",     "cue_shadow_caster", -21.20, -3.00,  -11.00, -3.80, 8.60),
    ("Shadow-N",     "cue_shadow_caster", -17.00, -3.00,    4.70, 11.00, 8.60),
    ("Dress-S",      "cue_scene_dressing",-22.00, 44.00,  -30.00, -2.60, 21.0),
    ("Dress-N",      "cue_scene_dressing",-22.00, 44.00,    2.60, 30.00, 21.0),
    ("Dress-Far",    "cue_scene_dressing", 26.00, 44.00,  -30.00, 30.00, 21.0),
]


# ===========================================================================
# [C'] PLACEMENT — `placement_lint.py` 의 기하 무관 선언 블록 (w3_execution_spec §10.4)
# ===========================================================================
PLACEMENT = dict(
    # `walk_edges` 는 **의도적으로 선언하지 않는다.** LINT-5 는 「도로의 구조·시설 기준에
    #   관한 규칙」 제16조의 **보도 유효폭**을 재는 규칙인데, 이 씬의 접근부는 보도가 아니라
    #   폭 22 m 의 **광장**이고 핸드레일 두 줄은 유효폭 경계가 아니라 **보행 동선 유도**다.
    #   설계 시 핸드레일 선을 walk_edges 로 선언해 보았더니 LINT-5 가 안내표지를 ERROR 로
    #   잡았다 — 규칙이 요구하는 이격(1.5 + 표2.2 점유 0.90 = 2.40 m)을 만족하는 |y| ≥ 4.8 은
    #   H 밴드(d 6–12 · hfov 62°) 화각 **밖**이라 단서가 화면에 잡히지 않는다 [측정].
    #   없는 데이텀을 지어내면 그 규칙은 검사가 아니라 허구가 되므로 선언하지 않고
    #   `nodata` 로 남긴다(규칙 파일 자신의 원칙 · SCENE_H67_BUILD §5-5 와 같은 판단).
    # 보차도 경계 = 볼라드 열이 서는 선 (PE-7 축 잠금 · PE-1 수목 이격의 기준선)
    kerb_lines=[((-17.0, -6.10), (-9.0, -6.10))],
    anchors={
        "plaza_N": dict(face_bearing_deg=90.0, props=["Bench_0"]),
        "plaza_S": dict(face_bearing_deg=270.0, props=["Bench_1"]),
        # `sc.build_sign` 의 `/Panel` 은 월드 좌표 메시라 xformOp 가 없다 → yaw 는
        #   구조적으로 0 이고 실제 정면 방위는 `/Back` 이 갖는다(scene_common.py:4572-4595).
        "stair_info": dict(face_bearing_deg=180.0, props=["Sign/Back"]),
        "walk_axis": dict(face_bearing_deg=0.0, props=["Sign/Panel"]),
    },
    # 가로수 열 — 1열 1수종(S-1) · 피치 7.0 m · 방위 = 연석 방위 0°.
    #   `pts` 는 **전 그루의 좌표**(LINT-2 는 인접 간격을 그대로 피치로 읽는다).
    routes={
        "plaza_S": dict(pts=[(-20.40, -4.60), (-13.40, -4.60), (-6.40, -4.60)],
                        species="oak_pin", pitch_m=7.0),
        "terrace_N": dict(pts=[(-11.00, 6.60), (-4.00, 6.60)],
                          species="ash", pitch_m=7.0),
    },
)


def build_views():
    """카메라 프리셋: grid_views(gy=0, 보행축 +X) + 미장센 4컷."""
    views = sc.grid_views(0.0)
    # landing_low: 보행축 정면 저시점 — **이 씬의 연구 변수**(계단참 코가 계단을 삼키는가)
    views["landing_low"] = dict(eye=[-8.2, 0.0, 0.58], tgt=[4.0, 0.1, -0.5])
    # plaza_over: 광장 전체 — 계단참·테라스·강의동의 관계
    views["plaza_over"] = dict(eye=[-11.5, -4.2, 4.4], tgt=[3.0, 0.5, -1.2])
    # stair_reveal: 계단참 코 바로 앞 — 낙차가 다시 나타나는 지점(H → V 전이)
    views["stair_reveal"] = dict(eye=[-1.60, 0.4, 1.62], tgt=[4.2, -0.3, -1.5])
    # nose_face: 계단참 코를 측면에서 — 모서리 소속 게이트(VG-06)의 육안 대응
    views["nose_face"] = dict(eye=[-2.60, -4.60, 1.15], tgt=[1.6, 1.2, -1.0])
    return views


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. landing_low (h0.58·d8.2)  — 계단참 코가 8단·중간참·선큰 광장을 통째로 삼키는가
 2. stair_reveal              — 코 앞에 서면 계단이 나타나는가 (H → V 전이)
 3. nose_face                 — 가시 지면 종단선의 주인이 **계단참 슬래브**인가 (VG-06)
 4. plaza_over                — 판석 광장·테라스 화단·강의동이 캠퍼스로 읽히는가
 5. cue ON vs OFF             — 핸드레일·점형블록·인레이 토글 시 기하 불변인가
 6. 접지·순백                 — 순백(>0.8) 대면적 없음 · 접지 · Z파이팅 없음
 7. props 규율                — 볼라드 피치 1.50 · 조형물 0 · 계단 위 단서 0"""


def main():
    if os.environ.get("NEGOBS_SMOKE", "0") == "1" \
            and os.environ.get("NEGOBS_SMOKE_ASSEMBLE", "0") != "1":
        print("SMOKE_OK %s pre-boot gate (GT-89)" % os.path.basename(__file__))
        ok = _geometry_selfcheck()
        if not ok:
            raise SystemExit("sceneH2 CPU 자기검사 실패")
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
    UsdGeom.Xform.Define(stage, "/World/SceneH2")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    P = PARAMS["plaza"]
    HZ = PARAMS["hazard"]
    BD = PARAMS["building"]
    ROOT = "/World/SceneH2"
    YH = P["y_half"]

    def BOX(path, center, size, mtl=None, col=False, rotZ=0.0):
        return sc.add_box(stage, path, center, size, mtl, collider=col, rotZ=rotZ)

    def CYL(path, center, r, h, mtl=None, rotY=0.0, rotX=0.0, col=False):
        return sc.add_cylinder(stage, path, center, r, h, mtl,
                               rotY=rotY, rotX=rotX, collider=col)

    def PBR(path, *args, **kwargs):
        return sc.make_pbr(stage, path, *args, **kwargs)

    # [VG-void] 이음매 여유 — 인접 슬래브가 **정확히 같은 좌표**에서 맞닿으면
    #   `AabbPrefilter` 의 수직 레이가 두 상자의 면을 동시에 스치며 둘 다 놓친다
    #   (sceneH7 첫 스모크에서 계단 이음매 3줄 197셀이 void 로 찍혀 커버리지가 0.9981 로
    #   내려갔다 [측정]). 4 mm 겹침을 주면 겹친 구간에서 더 높은 상자가 이긴다.
    SEAM = 0.004

    def RECT(path, x0, y0, x1, y1, z_top, base, mtl, col=True, seam=True):
        """축정렬 지면 상자. 회전 상자를 쓰지 않는 이유는 `AabbPrefilter.ground_z`
        (수직 레이 최초 히트)가 회전체의 월드 AABB 를 평면으로 읽기 때문이다 —
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
        M["plaza"] = PBR(f"{ROOT}/Looks/PlazaGranite",
                         sc.tex_path("plaza_light", "diff"),
                         sc.tex_path("plaza_light", "nor"),
                         sc.tex_path("plaza_light", "rough"),
                         sca["plaza_light"], tint=mp["plaza_tint"])
        M["landing"] = PBR(f"{ROOT}/Looks/GraniteDark",
                           sc.tex_path("granite_dark", "diff"),
                           sc.tex_path("granite_dark", "nor"),
                           sc.tex_path("granite_dark", "rough"),
                           sca["granite_dark"], tint=mp["landing_tint"])
        M["stair"] = PBR(f"{ROOT}/Looks/StairSlab",
                         sc.tex_path("concrete_floor", "diff"),
                         sc.tex_path("concrete_floor", "nor"),
                         sc.tex_path("concrete_floor", "rough"),
                         sca["concrete_floor"], tint=mp["stair_tint"])
        M["flag"] = PBR(f"{ROOT}/Looks/StoneFlag",
                        sc.tex_path("stone_flag", "diff"),
                        sc.tex_path("stone_flag", "nor"),
                        sc.tex_path("stone_flag", "rough"), sca["stone_flag"])
        M["wall"] = PBR(f"{ROOT}/Looks/ConcreteWall",
                        sc.tex_path("concrete_wall", "diff"),
                        sc.tex_path("concrete_wall", "nor"),
                        sc.tex_path("concrete_wall", "rough"),
                        sca["concrete_wall"], tint=mp["wall_color"])
        M["brick"] = PBR(f"{ROOT}/Looks/Brick", sc.tex_path("brick_red", "diff"),
                         sc.tex_path("brick_red", "nor"),
                         sc.tex_path("brick_red", "rough"),
                         sca["brick_red"], tint=mp["brick_tint"])
        M["grass"] = PBR(f"{ROOT}/Looks/Grass", sc.tex_path("grass", "diff"),
                         sc.tex_path("grass", "nor"),
                         sc.tex_path("grass", "rough"),
                         sca["grass"], tint=mp["grass_tint"])
        M["gravel"] = PBR(f"{ROOT}/Looks/Gravel", sc.tex_path("gravel", "diff"),
                          sc.tex_path("gravel", "nor"),
                          sc.tex_path("gravel", "rough"), sca["gravel"])
        M["curb"] = PBR(f"{ROOT}/Looks/Curb",
                        sc.tex_path("granite_dark", "diff"),
                        sc.tex_path("granite_dark", "nor"),
                        sc.tex_path("granite_dark", "rough"),
                        sca["granite_dark"], tint=mp["curb_tint"])
        M["tactile"] = sc.tactile_pbr(stage, f"{ROOT}/Looks/Tactile",
                                      scale_m=sca["tactile"])
        M["rail"] = PBR(f"{ROOT}/Looks/Rail", diffuse_color=mp["rail_color"],
                        metallic=mp["rail_metallic"],
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
        M["canopy_a"] = PBR(f"{ROOT}/Looks/CanopyA", diffuse_color=mp["canopy_a"],
                            roughness_const=mp["canopy_rough"])
        M["canopy_b"] = PBR(f"{ROOT}/Looks/CanopyB", diffuse_color=mp["canopy_b"],
                            roughness_const=mp["canopy_rough"])
        M["glass"] = PBR(f"{ROOT}/Looks/WindowBand",
                         diffuse_color=mp["glass_color"],
                         metallic=mp["glass_metallic"],
                         roughness_const=mp["glass_rough"])
        M["backdrop"] = PBR(f"{ROOT}/Looks/BgConcrete",
                            diffuse_color=mp["backdrop_color"],
                            roughness_const=mp["backdrop_rough"])
        M["sign"] = PBR(f"{ROOT}/Looks/Sign", sc.tex_path("sign_info", "diff"),
                        uv_mode=True)
        return M

    # -------------------------------------------------------------------
    # ① 경로 + ④ 은닉 — 광장·계단참·테라스. **전부 hazard_* 밖** (4팔 공통 프림)
    # -------------------------------------------------------------------
    def build_plaza(M):
        """진입 보행로 + **LandingSlab**(④ 은닉체) + 측방 식재 테라스.

        `cam.ground_z` 는 이 프림들만으로 결정된다 — 데이텀 스트립 x ∈ [−12.05, −1.15] ·
        |y| ≤ 0.95 는 전 구간 z = 0 의 단일 평면이므로 VG-datum 은 **구성상** `datum_exact` 다.
        """
        a, ld, tr, ts = (P["approach"], P["landing"], P["terrace"],
                         P["terrace_step"])
        RECT(f"{ROOT}/Plaza/Approach", a["x0"], -YH, a["x1"], YH, a["z"],
             P["base_z"], M["plaza"])
        # `cue_material_break` 의 유일한 대상 — **재질 재바인딩 전용**(프림 집합 불변)
        land_mtl = M["landing"] if cfg["cue_material_break"] else M["plaza"]
        RECT(f"{ROOT}/LandingSlab", ld["x0"], -YH, ld["x1"], YH, ld["z"],
             P["base_z"], land_mtl)
        print(f"[cue] material_break={cfg['cue_material_break']} → LandingSlab = "
              f"{'진회색 화강석(GraniteDark)' if cfg['cue_material_break'] else '밝은 판석(PlazaGranite)'}"
              " · **프림 집합 불변**(재바인딩 전용) → 높이맵 비트 동일 보증")
        # 측방 식재 테라스 (팔 불변 지형) — 0.36 m 융기. 법정 추락방지 대상(1.2 m)이 **아니다**
        RECT(f"{ROOT}/Plaza/Terrace", tr["x0"], tr["y0"], tr["x1"], tr["y1"],
             tr["z"], P["base_z"], M["grass"])
        RECT(f"{ROOT}/Plaza/TerraceStep", ts["x0"], ts["y0"], ts["x1"], ts["y1"],
             ts["z"], P["base_z"], M["flag"])
        print(f"[구조] 계단참 폭 {ld['x1'] - ld['x0']:.3f} m · 코 x = {ld['x1']:+.3f} "
              f"· 테라스 +{tr['z']:.2f} m (< 1.20 → 법정 추락방지 난간 의무 없음)")

    def build_building(M):
        """강의동 — 구조물(팔 불변). x0 = 11.00 은 **높이맵 셀 중심**(파일 상단 참조).

        선큰 광장 바닥에서 올라서는 저층부(석재 기단 + 유리 띠) + 적벽돌 몸체.
        `hazard_stairs` 와 무관하게 항상 존재하므로 A/B/C/D 4팔에서 프림·좌표가 동일하다.
        """
        b = BD
        sc.skin_exclude(f"{ROOT}/Building")
        BOX(f"{ROOT}/Building/Mass",
            ((b["mass_x0"] + b["x1"]) / 2.0, (b["y0"] + b["y1"]) / 2.0,
             (b["z_top"] + b["base_z"]) / 2.0),
            (b["x1"] - b["mass_x0"], b["y1"] - b["y0"],
             b["z_top"] - b["base_z"]), M["brick"], col=True)
        # 석재 기단(포디엄) — 선큰 광장 바닥 −1.44 에서 **광장 레벨 위 +1.10** 까지.
        #   서측면 = x0 = 11.00 (셀 중심) · 상면이 반사실 채움면(z 0)보다 높다 —
        #   두 조건이 함께여야 셀 11.00 이 발자국으로 뒤집히지 않는다(위 PARAMS 이력).
        BOX(f"{ROOT}/Building/Plinth",
            ((b["x0"] + b["plinth_x1"]) / 2.0, (b["y0"] + b["y1"]) / 2.0,
             (b["plinth_top"] + b["base_z"]) / 2.0),
            (b["plinth_x1"] - b["x0"], b["y1"] - b["y0"],
             b["plinth_top"] - b["base_z"]), M["wall"], col=True)
        for i, (z0, z1) in enumerate(b["bands"]):
            BOX(f"{ROOT}/Building/Window_{i}",
                (b["mass_x0"] - 0.03, (b["y0"] + b["y1"]) / 2.0, (z0 + z1) / 2.0),
                (0.10, (b["y1"] - b["y0"]) * 0.92, z1 - z0), M["glass"])
        print(f"[구조] 강의동 기단 x [{b['x0']:.2f}, {b['plinth_x1']:.2f}] "
              f"상면 {b['plinth_top']:+.2f} (**셀 중심 · 채움면 위**) · 몸체 x0 = "
              f"{b['mass_x0']:.2f} · 지붕 {b['z_top']:.2f} m · "
              f"유리 띠 {len(b['bands'])}단")

    # -------------------------------------------------------------------
    # ② 위험 — hazard_stairs 전속. 여기에는 **단서가 한 개도 없다**(프림 위생 1).
    #    단, 계단 자신의 논슬립 코는 낙차 기하이므로 여기서 짓는다(§4.4.1 F·E 부류).
    # -------------------------------------------------------------------
    def build_hazard(M):
        up, dn, md, lo, ng = (HZ["up"], HZ["dn"], HZ["mid"], HZ["lower"],
                              HZ["nose"])
        sc.skin_exclude(f"{ROOT}/Stair", f"{ROOT}/MidLanding", f"{ROOT}/LowerPlaza")
        n_nose = 0
        # 상부 플라이트 — 계단참 아래 하행 4단 (브리프 ②)
        for i in range(up["n"]):
            x0 = up["x0"] + i * up["tread"]
            z = -(i + 1) * up["riser"]
            RECT(f"{ROOT}/Stair/Up_{i}", x0, -YH, x0 + up["tread"], YH, z,
                 HZ["base_z"], M["stair"])
            BOX(f"{ROOT}/Stair/UpNose_{i}",
                (x0 + up["tread"] - ng["width"] / 2.0, 0.0, z + ng["proud"] / 2.0),
                (ng["width"], 2 * YH, ng["proud"]), M["nosing"])
            n_nose += 1
        # 중간 계단참
        RECT(f"{ROOT}/MidLanding/Slab", md["x0"], -YH, md["x1"], YH, md["z"],
             HZ["base_z"], M["stair"])
        # 하부 플라이트
        for i in range(dn["n"]):
            x0 = dn["x0"] + i * dn["tread"]
            z = md["z"] - (i + 1) * dn["riser"]
            RECT(f"{ROOT}/Stair/Dn_{i}", x0, -YH, x0 + dn["tread"], YH, z,
                 HZ["base_z"], M["stair"])
            BOX(f"{ROOT}/Stair/DnNose_{i}",
                (x0 + dn["tread"] - ng["width"] / 2.0, 0.0, z + ng["proud"] / 2.0),
                (ng["width"], 2 * YH, ng["proud"]), M["nosing"])
            n_nose += 1
        # 선큰 광장 바닥 — VG-void: 발자국 전역에 **실제 바닥 프림**. 개방 바닥 0.
        RECT(f"{ROOT}/LowerPlaza/Floor", lo["x0"], -YH - 2.0, lo["x1"], YH + 2.0,
             lo["z"], HZ["base_z"], M["flag"])
        drop = P["landing"]["z"] - lo["z"]
        print(f"[hazard] 낙차 = {drop:.3f} m · 계단 {up['n'] + dn['n']}단 × 라이즈 "
              f"{up['riser']} · 트레드 {up['tread']} · 중간참 "
              f"{md['x1'] - md['x0']:.2f} m · 선큰 광장 z={lo['z']:+.2f} "
              f"(x {lo['x0']:+.2f} … {lo['x1']:+.2f}) · 계단코 {n_nose}줄 "
              "(**낙차 자신의 기하** — cue_nosing 아님)")

    def build_flat_fill(M):
        """hazard_stairs=False 대조군 — 계단참 레벨의 평탄 지면이 낙차 발자국을 채운다.

        이것이 라벨러의 **반사실 보행 가능면 z_off** 다(footprint v2 = z_off − z_on ≥ 0.3).
        채움 동단은 강의동 서측면(x = 11.00)에서 정확히 끝난다 — 그래야 셀 11.00 의
        수직 레이가 양팔 모두에서 강의동 지붕을 맞고 diff = 0 이 된다.
        """
        f = HZ["fill"]
        RECT(f"{ROOT}/FlatFill/Slab", f["x0"], -YH - 2.0, f["x1"], YH + 2.0,
             f["z"], HZ["base_z"], M["plaza"])
        print(f"[hazard] OFF — 반사실 보행 가능면 z_off = {f['z']:+.3f} "
              f"(x {f['x0']:+.3f} … {f['x1']:+.2f})")

    # -------------------------------------------------------------------
    # ③ 단서 — **전부 hazard_* 밖의 자립 프림**. 전부 계단참 코 뒤 또는 측방.
    # -------------------------------------------------------------------
    def build_railing(M):
        """진입 보행로 **양측 핸드레일 + 난간** (`cue_railing`).

        계단 위에는 두지 않는다 — 파일 상단 "계단참형이 강제하는 단서 배치 규율" 참조.
        점형블록 동단에서 **0.30 m 수평 연장**한 뒤 종단하는 것이 편의증진법 시행규칙
        별표1 이 요구하는 배치이며, 그 규정 배치가 곧 strict-H 안전 배치다.
        """
        r = PARAMS["rail"]
        n = int(math.floor((r["x1"] - r["x0"]) / r["post_pitch"])) + 1
        for side, y in (("S", r["ys"][0]), ("N", r["ys"][1])):
            for i in range(n):
                x = r["x0"] + i * r["post_pitch"]
                if x > r["x1"] + 1e-9:
                    break
                CYL(f"{ROOT}/Rail{side}/Post_{i:02d}",
                    (x, y, r["top_z"] / 2.0), r["post_r"], r["top_z"], M["rail"])
            L = r["x1"] - r["x0"]
            CYL(f"{ROOT}/Rail{side}/Top",
                ((r["x0"] + r["x1"]) / 2.0, y, r["top_z"]), r["hand_r"], L,
                M["rail"], rotY=90.0)
            CYL(f"{ROOT}/Rail{side}/Hand",
                ((r["x0"] + r["x1"]) / 2.0,
                 y - math.copysign(0.08, y), r["hand_z"]), r["hand_r"], L,
                M["rail"], rotY=90.0)
        print(f"[cue] railing ON — 양측 난간 {n}본×2 (피치 {r['post_pitch']} m) · "
              f"가드선 {r['top_z']:.2f} m · 손잡이 {r['hand_z']:.2f} m "
              f"· 동단 x={r['x1']:+.2f} (계단 코 −0.575 에서 "
              f"{P['landing']['x1'] - r['x1']:+.3f} m 앞 종단) "
              "[규격 편의증진법 시행규칙 별표1] · **계단 위 단서 0**")

    def build_tactile(M):
        t = PARAMS["tactile"]
        sc.build_tactile(stage, f"{ROOT}/Tactile", t["x0"], t["x1"],
                         -t["y_half"], t["y_half"], M["tactile"],
                         z=P["landing"]["z"], proud=t["proud"])
        print(f"[cue] tactile ON — **경고 1밴드** 세로 {t['x1'] - t['x0']:.2f} m "
              f"(0.30 m 유닛 {round((t['x1'] - t['x0']) / 0.30)}매) · 계단 상단에서 "
              f"{P['landing']['x1'] - t['x1']:.2f} m 이격 · "
              f"proud {t['proud']} m "
              "[규격 교통약자법 시행규칙 별표1 · 국도 실무요령 7.5]")

    def build_nosing(M):
        """`cue_nosing` — **팔 불변 지면 위의 논슬립 띠만** 짓는다.

        ⓐ 계단참 코 **매입형 인레이**: 코에서 45 mm 안쪽 · 융기 2 mm.
           브리프의 *"노징 프림은 자립 데칼로 지어 모서리 주인이 되지 않게 한다"* 를
           이행하는 장치다 — 융기 2 mm / 후퇴 45 mm ⇒ 기울기 0.044 이하의 시선만 코를
           가릴 수 있는데 H 밴드의 최대 |s| 는 0.145 이므로 **구성상** 불가능하다.
        ⓑ 테라스 진입 2단의 논슬립 띠: 측방 팔 불변 지형 위 · 융기 12 mm.
        하행 8단의 계단코는 `build_hazard` 소관이다(낙차 자신의 기하).
        """
        ng = PARAMS["nosing"]
        ld, ts, tr = P["landing"], P["terrace_step"], P["terrace"]
        x_out = ld["x1"] - ng["inlay_inset"]
        BOX(f"{ROOT}/NosingInlay/Landing",
            (x_out - ng["inlay_w"] / 2.0, 0.0, ld["z"] + ng["inlay_proud"] / 2.0),
            (ng["inlay_w"], 2 * YH, ng["inlay_proud"]), M["nosing"])
        for tag, y_edge, z in (("Step", ts["y1"], ts["z"]),
                               ("Terr", tr["y0"], tr["z"])):
            BOX(f"{ROOT}/NosingTerrace/{tag}",
                ((ts["x0"] + ts["x1"]) / 2.0, y_edge - ng["strip_w"] / 2.0,
                 z + ng["strip_proud"] / 2.0),
                (ts["x1"] - ts["x0"], ng["strip_w"], ng["strip_proud"]),
                M["nosing"])
        print(f"[cue] nosing ON — 계단참 코 매입 인레이 1줄(inset "
              f"{ng['inlay_inset'] * 1000:.0f} mm · proud {ng['inlay_proud'] * 1000:.0f} mm) "
              f"+ 테라스 2단 띠 2줄(proud {ng['strip_proud'] * 1000:.0f} mm) "
              "· 전부 **팔 불변 지면 · 발자국 밖**")

    def build_sign(M):
        """캠퍼스 시설 안내표지 1매 — 법2(임의 경고판 금지): 법정 제식 판만."""
        s = PARAMS["sign"]
        sc.build_sign(stage, f"{ROOT}/Sign", s["x"], s["y"], 0.0, s["yaw"],
                      M["sign"], w=s["w"], h=s["h"], pole_h=s["pole_h"],
                      pole_mtl=M["pole"], back_mtl=M["iron"])
        print(f"[cue] sign ON — 캠퍼스 시설 안내표지 1매 "
              f"@({s['x']:+.2f},{s['y']:+.2f}) · 임의 문구 0 (법2)")

    def build_bollards(M):
        """광장 진입 차량 억제 볼라드 열. 보차도 경계선 위 · 피치 1.50 m 법정치."""
        b = PARAMS["bollard"]
        for i, x in enumerate(b["xs"]):
            # `placement_lint` 의 `props.bollard` 규약: `Bollard_NN` + `/Post` + `/Band`
            CYL(f"{ROOT}/Bollard_{i:02d}/Post", (x, b["y"], b["h"] / 2.0),
                b["r"], b["h"], M["bollard"])
            CYL(f"{ROOT}/Bollard_{i:02d}/Band", (x, b["y"], b["band_z"]),
                b["r"] + 0.004, b["band_t"], M["band"])
        print(f"[cue] bollard ON — {len(b['xs'])}본 · h {b['h']} m · "
              f"φ{2 * b['r']:.2f} m · 피치 1.50 m · y {b['y']:+.2f} (보차도 경계) "
              "· 반사띠 [규격 교통약자법 시행규칙 별표2 제7호]")

    def build_planter_edge(M):
        """`cue_planter_edge` — 지상 화단(식재 테라스) 둘레 **경계석 + 낮은 난간**.

        [FA_REALITY §3 사다리 L1 ★1] 추락방지 난간의 법정 의무는 「옥상광장·2층 이상
        노대」에 1.2 m 이상이고 **지상 화단에는 없다**. 이 난간의 목적은 조경 경계이며
        테라스 융기는 0.36 m — 위험 임계 0.30 m 를 갓 넘지만 **팔 불변 지형**이라
        어느 팔에서도 GT 양성이 되지 않는다. 즉 이 씬은 **"난간이 있는데 낙차 GT 는
        없는 영역"** 을 양성 씬 안에 품는다 — 지름길 모델의 정면 반례다.
        """
        pl = PARAMS["planter"]
        tr = P["terrace"]
        # 남측 · 서측 경계석 (융기 0.12 m)
        BOX(f"{ROOT}/Planter/CurbS",
            ((tr["x0"] + tr["x1"]) / 2.0, tr["y0"] + pl["curb_w"] / 2.0,
             tr["z"] + pl["curb_proud"] / 2.0),
            (tr["x1"] - tr["x0"], pl["curb_w"], pl["curb_proud"]), M["curb"])
        BOX(f"{ROOT}/Planter/CurbW",
            (tr["x0"] + pl["curb_w"] / 2.0, (tr["y0"] + tr["y1"]) / 2.0,
             tr["z"] + pl["curb_proud"] / 2.0),
            (pl["curb_w"], tr["y1"] - tr["y0"], pl["curb_proud"]), M["curb"])
        # 남측 경계 난간 (h 0.45) — 조경 경계용
        z0 = tr["z"] + pl["curb_proud"]
        n = int((tr["x1"] - tr["x0"]) / pl["post_pitch"]) + 1
        for i in range(n):
            x = tr["x0"] + i * pl["post_pitch"]
            if x > tr["x1"] + 1e-9:
                break
            CYL(f"{ROOT}/Planter/Post_{i:02d}",
                (x, tr["y0"] + pl["curb_w"] / 2.0, z0 + pl["rail_h"] / 2.0),
                pl["rail_r"], pl["rail_h"], M["rail"])
        CYL(f"{ROOT}/Planter/TopRail",
            ((tr["x0"] + tr["x1"]) / 2.0, tr["y0"] + pl["curb_w"] / 2.0,
             z0 + pl["rail_h"]), pl["rail_r"], tr["x1"] - tr["x0"], M["rail"],
            rotY=90.0)
        print(f"[cue] planter_edge ON — 화단 경계석 2면(융기 "
              f"{pl['curb_proud'] * 1000:.0f} mm) + 경계 난간 {n}본 h {pl['rail_h']} m "
              "[FA_REALITY L1 ★1 — 지상 화단은 추락방지 난간 법정 의무 없음]")

    def build_ground_kit(M):
        """지면 문양 (`cue_manhole`·`cue_slab_joint`·`cue_drainage`) + `cue_tree_grate`.

        전부 **flush**(≤ 8 mm)이므로 법7(기하 불변)을 지킨다. 맨홀·빗물받이는 |y| ≥ 2.6 에
        배치해 카메라 데이텀 스트립(|y| ≤ 0.95)을 비운다.
        """
        g = PARAMS["gkit"]
        M2 = dict(M)
        M2.update(joint=M["curb"], crack=M["curb"], manhole=M["iron"],
                  gully=M["iron"], gutter=M["curb"], gutter_cover=M["iron"],
                  trench=M["iron"], trench_frame=M["iron"], marking=M["lamp"],
                  weed=M["grass"], wear=M["gravel"], stain_dirt=M["gravel"],
                  stain_water=M["gravel"], tree_grate=M["iron"], grate=M["iron"],
                  patch=M["plaza"], patch_cut=M["curb"], relaid=M["plaza"])
        kit = gk.kit_from_scene_common(sc, stage)
        infra = dict(manhole=len(g["manholes"]) if cfg["cue_manhole"] else 0,
                     gully=len(g["gullies"]) if cfg["cue_drainage"] else 0)
        sites = {}
        if cfg["cue_manhole"]:
            sites["manhole"] = [tuple(v) for v in g["manholes"]]
        if cfg["cue_drainage"]:
            sites["gully"] = [tuple(v) for v in g["gullies"]]
        gp = gk.plan_ground(
            "plaza_granite", region=tuple(g["region"]), z=P["landing"]["z"],
            gy=0.0, origin=(0.0, 0.0, 0.0),
            edges=[("stair_head", P["landing"]["x1"])],
            dists=(2, 5, 10), scene="sceneH2", tactile=(),
            # `surface=None` — 잡초/균열/오염 데칼 OFF. 1차 이유는 법1(손상·노후 금지),
            #   2차 이유는 잡초 프림(proud 최대 0.107 m)이 데이텀 스트립을 `datum_fail` 로
            #   밀 수 있다는 것이다.
            overrides=dict(infra=infra, surface=None), sites=sites, seed=82)
        if not cfg["cue_slab_joint"]:
            gp["ops"] = [o for o in gp["ops"] if o["name"] != "joints"]
            gp["elements"] = [e for e in gp["elements"] if e["kind"] != "joint"]
        res = gk.apply_ground(kit, f"{ROOT}/GKit", gp, M2,
                              skin_exclude=sc.skin_exclude,
                              scatter=sc.scatter_debris)
        n_grate = 0
        if cfg["cue_tree_grate"]:
            for i, (gx, gy_) in enumerate(g["tree_grates"]):
                n_grate += _tree_grate(M, f"{ROOT}/TreeGrate_{i}", gx, gy_, 0.0)
        print(f"[cue] ground pattern — manhole={cfg['cue_manhole']}"
              f"({len(g['manholes'])}) slab_joint={cfg['cue_slab_joint']} "
              f"drainage={cfg['cue_drainage']} tree_grate={cfg['cue_tree_grate']}"
              f"({n_grate} 프림) · gkit 프림 {res['prims']} · "
              f"δmax {res['gt_delta_max']:.4f} m (flush — 법7)")

    def _tree_grate(M, path, cx, cy, z, side=1.44, frame=0.09, bar=0.035,
                    n_bar=9, proud=0.004):
        """수목보호덮개 (flush) — 프레임 + 평행 바. [FA_REALITY §2 2위 · 33씬 전무]"""
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
        """그림자 밴드 캐스터 — 광장 가로수 열 + 가로등 (`cue_shadow_caster`).

        **양성 씬에도 동일 비율로**(RENDER_PLAN_V3 §2.0 역지름길 경보).
        시선 통로 |y| ≤ 4.0 · x ∈ [−12, 0] 은 비워 둔다 — 수관이 낙차를 가리면 VG-06 의
        모서리 소유가 계단참에서 수목으로 넘어간다.
        """
        s = PARAMS["shadow"]
        for i, (tx, ty) in enumerate(s["trees"]):
            sc.build_tree(stage, f"{ROOT}/Shadow/Tree_{i}", tx, ty, 0.0,
                          M["wood"], M["canopy_a"], M["canopy_b"],
                          trunk_r=0.17, trunk_h=s["tree_h"] * 0.52,
                          canopy_blobs=11, canopy_spread=1.25, species="oak_pin")
        for i, (lx, ly) in enumerate(s["lamps"]):
            gz = P["terrace"]["z"] if ly > 4.0 else 0.0
            CYL(f"{ROOT}/Shadow/LampPole_{i}", (lx, ly, gz + s["lamp_h"] / 2.0),
                0.074, s["lamp_h"], M["pole"])
            arm_y = ly - math.copysign(s["lamp_arm"] / 2.0, ly)
            CYL(f"{ROOT}/Shadow/LampArm_{i}", (lx, arm_y, gz + s["lamp_h"]),
                0.05, s["lamp_arm"], M["pole"], rotX=90.0)
            BOX(f"{ROOT}/Shadow/LampHead_{i}",
                (lx, ly - math.copysign(s["lamp_arm"], ly), gz + s["lamp_h"] - 0.09),
                (0.46, 0.20, 0.13), M["lamp"])
        print(f"[cue] shadow_caster ON — 가로수 {len(s['trees'])}주 + "
              f"가로등 {len(s['lamps'])}주 · 시선 통로(|y|≤4.0) 청소됨")

    def build_dressing(M):
        """③ 단서의 환경 성분 — 테라스 관목 띠 · 벤치 · 테라스 가로수 · 원경 건물동."""
        d = PARAMS["dress"]
        tr = P["terrace"]
        for i, (x0, y0, x1, y1) in enumerate(d["hedge"]):
            sc.place_hedge_row(stage, f"{ROOT}/Dress/Hedge_{i}", x0, y0, x1, y1,
                               d["shrub_h"], seed=1820 + i, base_z=tr["z"],
                               fallback_mtl=M["grass"])
        for i, (bx, by, byaw) in enumerate(d["benches"]):
            sc.build_bench(stage, f"{ROOT}/Dress/Bench_{i}", bx, by, 0.0,
                           M["wood"], yaw=byaw)
        for i, (tx, ty) in enumerate(d["trees"]):
            sc.build_tree(stage, f"{ROOT}/Dress/Tree_{i}", tx, ty, tr["z"],
                          M["wood"], M["canopy_a"], M["canopy_b"], trunk_r=0.13,
                          trunk_h=d["tree_h"] * 0.5, canopy_blobs=10,
                          canopy_spread=1.1, species="ash")
        if not PLACEBO_REMOVE:
            for tag, x0, x1, y0, y1, hgt in d["backdrop"]:
                BOX(f"{ROOT}/Dress/Backdrop_{tag}",
                    ((x0 + x1) / 2.0, (y0 + y1) / 2.0, hgt / 2.0 - 1.44),
                    (x1 - x0, y1 - y0, hgt), M["backdrop"])
        else:
            print("[placebo] 원경 건물동 물량군 제거 — 위험·단서는 전부 유지(D35 P팔)")
        print(f"[cue] scene_dressing ON — 관목 {len(d['hedge'])}띠 · "
              f"벤치 {len(d['benches'])} · 테라스 가로수 {len(d['trees'])} · 원경 "
              f"{0 if PLACEBO_REMOVE else len(d['backdrop'])}동")

    # -------------------------------------------------------------------
    # 자기검사 — 조립 직후, 렌더 전
    # -------------------------------------------------------------------
    def scene_selfcheck():
        from pxr import Usd, UsdGeom
        ok = True
        ds = DATUM_STRIP

        # (1) 선언 검사 — VG-datum 3층 분류
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
        gated_roots = ("/Stair", "/MidLanding", "/LowerPlaza", "/FlatFill",
                       "/RailS", "/RailN", "/Tactile", "/NosingInlay",
                       "/NosingTerrace", "/Sign", "/Bollard", "/Planter",
                       "/GKit", "/TreeGrate", "/Shadow", "/Dress")
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
            dz = float(mx[2]) - 0.0        # 스트립 전 구간이 z = 0 평면이다
            (tol_hits if dz <= DATUM_TOL else hits).append((p, round(dz, 4)))
        if hits:
            ok = False
        print(f"[selfcheck] (2) 토글 프림 {n_scan}개 전수 AABB → 스트립 교차 "
              f"{len(hits) + len(tol_hits)}건 (datum_tol {len(tol_hits)} · "
              f"datum_fail {len(hits)})"
              + (f" FAIL={hits[:6]}" if hits else " · OK"))

        # (3) VG-void — 발자국 전역 커버리지 (해석적 종단면 검사)
        nose = P["landing"]["x1"]
        if cfg["hazard_stairs"]:
            up, dn, md, lo = HZ["up"], HZ["dn"], HZ["mid"], HZ["lower"]
            segs = [(up["x0"], up["x0"] + up["n"] * up["tread"]),
                    (md["x0"], md["x1"]),
                    (dn["x0"], dn["x0"] + dn["n"] * dn["tread"]),
                    (lo["x0"], lo["x1"]), (BD["x0"], 14.0)]
        else:
            segs = [(HZ["fill"]["x0"], HZ["fill"]["x1"]), (BD["x0"], 14.0)]
        cover_hi = nose
        gap = []
        for s0, s1 in sorted(segs):
            if s0 > cover_hi + 1e-6:
                gap.append((round(cover_hi, 3), round(s0, 3)))
            cover_hi = max(cover_hi, s1)
        if cover_hi < 14.0 - 1e-6:
            gap.append((round(cover_hi, 3), 14.0))
        if gap:
            ok = False
        print(f"[selfcheck] (3) VG-void 발자국 커버리지 x[{nose:+.3f}, 14.00] "
              f"y[±{YH:.1f}] → 공백 {len(gap)}구간"
              + (f" {gap}" if gap else " · 커버리지 1.0 · OK"))

        # (4) 단서 프림 × 낙차 발자국 교차 0 — **계단참형의 생명선**(파일 상단 규율)
        cue_roots = ("/RailS", "/RailN", "/Tactile", "/NosingInlay",
                     "/NosingTerrace", "/Sign", "/Bollard", "/Planter",
                     "/GKit", "/TreeGrate", "/Shadow", "/Dress")
        fp_x0 = _footprint_x0()
        over = []
        for prim in stage.Traverse():
            p = str(prim.GetPath())
            if not p.startswith(ROOT) or not prim.IsA(UsdGeom.Gprim):
                continue
            tail = p[len(ROOT):]
            if not any(tail.startswith(g) for g in cue_roots):
                continue
            if tail.startswith("/Dress/Backdrop"):
                continue                     # 원경(x ≥ 27) — 높이맵 격자 밖
            try:
                b = bbc.ComputeWorldBound(prim).ComputeAlignedRange()
            except Exception:
                continue
            if b.IsEmpty():
                continue
            mn, mx = b.GetMin(), b.GetMax()
            if mx[0] > fp_x0 and mn[0] < 14.0 and mx[1] > -8.0 and mn[1] < 8.0:
                over.append((p, round(float(mn[0]), 3), round(float(mx[0]), 3)))
        if over:
            ok = False
        print(f"[selfcheck] (4) 단서 프림 × 발자국(x ≥ {fp_x0:+.3f}) 교차 "
              f"{len(over)}건" + (f" {over[:6]}" if over else " · OK "
                                  "→ `cells_raw`·`polar_gt` 는 cue_* 에 구성상 불변"))

        # (5) 은닉 기하 재계산
        cx, cz, s_int, s_rim = _nose_slope()
        print(f"[selfcheck] (5) 은닉 기하 — 계단참 코 ({cx:+.3f}, {cz:.2f}) · "
              f"내부 은닉 s ≥ {s_int:+.4f} · 림 은닉 s ≥ {s_rim:+.4f} "
              f"· 실효 구속 = {'내부' if abs(s_int) > abs(s_rim) else '림'}")
        for dd in (4.0, 6.0, 8.0, 12.0):
            hmax = _h_max(dd)
            print(f"              d={dd:5.1f}  h_max={hmax:.3f}  "
                  f"H밴드[0.25,1.0] 통과율 "
                  f"{min(1.0, max(0.0, (hmax - 0.25) / 0.75)):.2f}")

        print(f"[selfcheck] sceneH2 {'통과' if ok else '실패'}")
        return ok

    # -------------------------------------------------------------------
    # 조립
    # -------------------------------------------------------------------
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()

    build_plaza(M)                       # ① 경로 + ④ 은닉 (팔 불변)
    build_building(M)                    # 구조물 (팔 불변)

    if cfg["hazard_stairs"]:             # ② 위험 — 조립부의 hazard 분기는 이 2줄뿐
        build_hazard(M)
    else:
        build_flat_fill(M)

    # ③ 단서 — 어느 것도 hazard 분기 안에 있지 않다
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
    if cfg["cue_planter_edge"]:
        build_planter_edge(M)
    if cfg["cue_manhole"] or cfg["cue_slab_joint"] or cfg["cue_drainage"] \
            or cfg["cue_tree_grate"]:
        build_ground_kit(M)
    if cfg["cue_shadow_caster"]:
        build_shadow_casters(M)
    if cfg["cue_scene_dressing"] or KEEP_DRESSING:
        # KEEP_DRESSING: 이 씬의 장식은 전부 광장(z = 0)·테라스(z = +0.36)에 앵커되므로
        #   위험 제거가 장식을 끌고 내려가지 않는다 — sceneC2 의 "하부 앵커 드레싱 소실 →
        #   ground_z 이동" 사고가 구조적으로 불가능하다.
        build_dressing(M)

    if not scene_selfcheck():
        raise SystemExit("sceneH2 self-check 실패")

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    if smoke_mode:
        n = sum(1 for _ in stage.Traverse())
        print(f"[SMOKE] sceneH2 조립 완료 · 프림 {n}개 · 조기 종료")
        simulation_app.close()
        return

    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    _v0 = build_views()["plaza_over"]
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
            fp = os.path.join(LOOKCHECK_DIR, f"sceneH2_{ts}.png")
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
# CPU 자기검사 — pxr·GPU 없이 종단면과 수율 설계를 재계산한다
# ===========================================================================
def _footprint_x0():
    """발자국 근단 x — `z_off − z_on ≥ 0.30` 을 처음 만족하는 단의 **근단 경계**.

    z_off = 0(반사실 평탄), i 단 상면 = −(i+1)·riser 이므로 조건을 처음 만족하는 것은
    `n_free = ceil(0.30 / riser) − 1` 개의 단을 지난 다음 단이다(H7 `_footprint_corner`
    와 같은 유도). riser 0.18 → n_free = 1 → 2단째 상면 −0.36.
    """
    up = PARAMS["hazard"]["up"]
    n_free = max(0, math.ceil(0.30 / up["riser"]) - 1)
    return up["x0"] + n_free * up["tread"]


def _nose_slope():
    """(코 x, 코 z, 내부 은닉 임계 기울기 s_int, 림 은닉 임계 기울기 s_rim).

    s_int : 코를 스치는 시선이 **선큰 광장 바닥 × 강의동 외벽**(x = 11.00, z = −1.44)에
            닿는 기울기. **이쪽이 실효 구속**이다 — 계단참형은 가림체가 림보다 높지 않다.
    s_rim : 발자국 근단 립(= 1단 상면 z, `labeler.edge_points` 규약)에 닿는 기울기.
    """
    P, HZ, BD = PARAMS["plaza"], PARAMS["hazard"], PARAMS["building"]
    cx, cz = P["landing"]["x1"], P["landing"]["z"]
    s_int = (HZ["lower"]["z"] - cz) / (BD["x0"] - cx)
    lip_x = _footprint_x0()
    lip_z = cz - HZ["up"]["riser"] * max(0, math.ceil(0.30 / HZ["up"]["riser"]) - 1)
    s_rim = (lip_z - cz) / (lip_x - cx)
    return cx, cz, s_int, s_rim


def _h_max(d, crit="int"):
    """거리 d 에서 strict-H 가 성립하는 카메라 높이 상한 h_rel [m].

        L = d + cx   (카메라 x = −d 에서 코 x = cx 까지의 수평거리, cx < 0)
        s = (cz − h) / L ≥ s_crit  ⇔  h ≤ cz − s_crit·L      (지면은 전 구간 z = 0)

    `crit="int"`(기본) = 실효 구속 · `crit="rim"` = 립 조건.
    """
    cx, cz, s_int, s_rim = _nose_slope()
    L = d + cx
    if L <= 1e-6:
        return float("-inf")
    return cz - (s_int if crit == "int" else s_rim) * L


def _band_yield(d_lo, d_hi, h_lo, h_hi, n=1200, crit="int"):
    """d ~ LogU[d_lo, d_hi] · h ~ U[h_lo, h_hi] 에서 strict-H 가 되는 프레임 비율.

    두 조건(내부·림)을 **동시에** 요구한다 — `tier_of` 는 `int_px == 0 and edge_vis == 0`
    에서만 H 를 준다.
    """
    tot = 0.0
    lo, hi = math.log(d_lo), math.log(d_hi)
    for i in range(n):
        d = math.exp(lo + (hi - lo) * (i + 0.5) / n)
        hm = min(_h_max(d, "int"), _h_max(d, "rim"))
        tot += min(1.0, max(0.0, (hm - h_lo) / (h_hi - h_lo)))
    return tot / n


def _geometry_selfcheck():
    P, HZ, BD = PARAMS["plaza"], PARAMS["hazard"], PARAMS["building"]
    ok = True

    def chk(tag, cond, msg=""):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  [{'PASS' if cond else 'FAIL'}] {tag}" + (f" — {msg}" if msg else ""))

    print("=" * 70)
    print("sceneH2_landing_campus — CPU 자기검사 (pxr·GPU 불필요)")
    print("=" * 70)

    up, dn, md, lo = HZ["up"], HZ["dn"], HZ["mid"], HZ["lower"]
    drop = P["landing"]["z"] - lo["z"]
    chk("낙차 = 8단 × 라이즈",
        abs(drop - (up["n"] + dn["n"]) * up["riser"]) < 1e-9, f"{drop:.3f} m")
    chk("라이즈·트레드·중간참이 옥외계단 규격 안",
        up["riser"] <= 0.18 and up["tread"] >= 0.26
        and (md["x1"] - md["x0"]) >= 1.20,
        f"R {up['riser']} · T {up['tread']} · 중간참 {md['x1'] - md['x0']:.2f} m")
    chk("상부 플라이트 = 브리프 '하행 4단'", up["n"] == 4, f"{up['n']}단")
    chk("계단 종단이 중간참 시작과 연속",
        abs(up["x0"] + up["n"] * up["tread"] - md["x0"]) < 1e-9,
        f"{up['x0'] + up['n'] * up['tread']:.3f} = {md['x0']:.3f}")
    chk("중간참 종단이 하부 플라이트 시작과 연속",
        abs(md["x1"] - dn["x0"]) < 1e-9, f"{md['x1']:.3f} = {dn['x0']:.3f}")
    chk("하부 플라이트 종단이 선큰 광장과 연속",
        abs(dn["x0"] + dn["n"] * dn["tread"] - lo["x0"]) < 1e-9,
        f"{dn['x0'] + dn['n'] * dn['tread']:.3f} = {lo['x0']:.3f}")
    chk("선큰 광장 동단 = 강의동 서측면", abs(lo["x1"] - BD["x0"]) < 1e-9,
        f"{lo['x1']:.2f} = {BD['x0']:.2f}")
    chk("반사실 채움면 = 계단참 레벨",
        abs(HZ["fill"]["z"] - P["landing"]["z"]) < 1e-9, f"{HZ['fill']['z']}")

    # **셀 중심 정렬** — 높이맵 격자 x0 = −2.00 · step = 0.05
    k = (BD["x0"] - (-2.00)) / 0.05
    chk("강의동 서측면이 높이맵 셀 **중심**에 정렬", abs(k - round(k)) < 1e-9,
        f"(11.00 − (−2.00))/0.05 = {k:.3f} → 정수 · 깊이 잡음 ±0.02 m 에도 반올림 불변")
    # 코는 셀 **경계**에 앉혀 1단/2단의 셀 귀속을 결정론으로 만든다
    kn = (P["landing"]["x1"] - (-2.00)) / 0.05
    chk("계단참 코가 높이맵 셀 **경계**에 정렬",
        abs(abs(kn - round(kn)) - 0.5) < 1e-9,
        f"(−0.575 − (−2.00))/0.05 = {kn:.3f} → 반정수")
    chk("강의동 기단이 선큰 광장 쪽으로 나오지 않는다",
        BD["x0"] >= lo["x1"] - 1e-9 and BD["mass_x0"] >= BD["plinth_x1"] - 1e-9
        and BD["plinth_x1"] > BD["x0"],
        f"기단 x [{BD['x0']:.2f}, {BD['plinth_x1']:.2f}] · 몸체 x0 "
        f"{BD['mass_x0']:.2f} · 광장 동단 {lo['x1']:.2f}")
    # **R2 의 핵심 부등식** — 기단 상면이 반사실 채움면보다 높아야 셀 11.00 이
    #   발자국으로 뒤집히지 않는다(PARAMS 이력 주석 참조).
    chk("기단 상면 > 반사실 채움면 (셀 11.00 이 발자국이 되지 않는 조건)",
        BD["plinth_top"] > HZ["fill"]["z"] + 1e-9,
        f"기단 상면 {BD['plinth_top']:+.2f} > 채움면 {HZ['fill']['z']:+.2f} "
        f"⇒ 양팔 모두 셀 11.00 의 수직 레이가 기단 상면을 맞는다 (diff 0)")

    fp_x0 = _footprint_x0()
    chk("발자국 근단이 d=12 폴라 격자(반경 12 m) 안", 12.0 + fp_x0 < 12.0,
        f"근단 x={fp_x0:+.3f} → d=12 에서 거리 {12.0 + fp_x0:.3f} m < 12.0")

    cx, cz, s_int, s_rim = _nose_slope()
    chk("실효 구속 = 내부 조건 (계단참형의 정체)", abs(s_int) < abs(s_rim),
        f"|s_int| {abs(s_int):.4f} < |s_rim| {abs(s_rim):.4f} "
        "→ 내부가 먼저 깨진다")
    print(f"  [info] 계단참 코 ({cx:+.3f}, {cz:.2f}) · 내부 은닉 s ≥ {s_int:+.4f} "
          f"· 림 은닉 s ≥ {s_rim:+.4f}")
    for dd in (2.0, 4.0, 6.0, 7.0, 8.0, 10.0, 12.0):
        hi_, hr_ = _h_max(dd, "int"), _h_max(dd, "rim")
        print(f"         d={dd:5.1f}  h_max 내부={hi_:7.3f} 립={hr_:7.3f}  "
              f"H밴드 통과율 {min(1.0, max(0.0, (min(hi_, hr_) - 0.25) / 0.75)):.2f}  "
              f"base {min(1.0, max(0.0, (min(hi_, hr_) - 0.25) / 1.65)):.2f}")
    p_base = _band_yield(1.2, 12.0, 0.25, 1.90)
    p_h = _band_yield(6.0, 12.0, 0.25, 1.00)
    exp_h = 24 * p_base + 24 * p_h
    print(f"  [info] 설계 수율 base {p_base:.3f} · H {p_h:.3f} "
          "(계획 §3.2 가정 0.50)")
    print(f"  [info] → A팔 48컷(base 24 + H 24) 기대 strict-H {exp_h:.1f} "
          "· 계획 §3.2 하한 paired-H ≥ 12")
    chk("H 밴드 설계 수율 ≥ 계획 가정 0.50", p_h >= 0.50, f"{p_h:.3f}")
    chk("A팔 48컷 기대 strict-H ≥ 12 (§3.2 하한)", exp_h >= 12.0, f"{exp_h:.1f}")
    chk("퇴화 아님 (base 밴드에 V/E 프레임이 남는다)", p_base <= 0.75,
        f"base 수율 {p_base:.3f} ≤ 0.75")

    # 인레이가 코를 가릴 수 없다 — 융기/후퇴 비 < H 밴드 최대 |s|
    ng = PARAMS["nosing"]
    s_max = 1.00 / (6.0 - abs(P["landing"]["x1"]))     # h 최대 1.0 · d 최소 6
    chk("코 인레이가 종단 모서리를 가릴 수 없다 (VG-06 브리프 요구)",
        ng["inlay_proud"] / ng["inlay_inset"] < s_max,
        f"proud/inset = {ng['inlay_proud'] / ng['inlay_inset']:.4f} < "
        f"H밴드 최대 |s| {s_max:.4f}")

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

    print(f"\n  ⇒ sceneH2 CPU 자기검사 {'통과' if ok else '실패'}")
    print("=" * 70)
    return ok


if __name__ == "__main__":
    main()
