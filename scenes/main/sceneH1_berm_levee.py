# -*- coding: utf-8 -*-
"""
sceneH1_berm_levee.py — NegObs 신규 씬 H1: 제방 성토 둔덕 + 호안 파라펫 낙차 (Isaac Sim 4.5)

계열    : **둔덕형 자기가림 (paired-H)** · 생활권 = **제방·수변(뚝방)**
정본    : `experiments/v3_0823/RENDER_PLAN_V3.md` §2.0(공통 표준) · §2.1 표 `sceneH1_berm_levee`
          · §2.6(CUE_CLASS 사전 분류) · §3.1–3.2(test-ext 사양·paired-H 회계)
분리    : **test-ext** — v2·v3 **양 모델 모두 미학습**. 훈련·검증에 절대 넣지 않는다(§3.1).
          **4팔 전부 제작 의무**(DZ §4.2 `:243`) — A·B·C·D 완비.
밴드    : base · **H**  (씬당 팔당 48컷 · 4팔 합 192)
승계    : `scene_common.py` · `ground_kit.py`(P5 alley_concrete) · `props_kit`
          조립 공식 = `Docs/briefs/NegObs_인공씬1호_계단_구현지시서.md:20-22`
          재질 3단 = `Docs/reports/realism_v1_final.md:84` (rev.1 우선 `realism_brief_v1.md:64-130`)
          조명 L0–L7 = `Docs/briefs/lighting_camera_variation_spec_v1.md:359-393`
          props 규율 = `Docs/audit_v4/user_feedback_v5_1.md:6-20, 46-49`

────────────────────────────────────────────────────────────────────────────
**부지 분리 선언 (§2.1 각주 · §12-9 무대 순도)**

계획 §2.1은 *"H1–H4는 test-ext, H5는 train, H6·H7은 val이며 **부지·드레싱·재질을 공유하지
않는다**"* 를 명령한다. 같은 **둔덕형** 계열의 val 공급원 `sceneH6_berm_levee2` 와의 분리는
다음 8개 축에서 **구성상** 확보된다 — 어느 하나도 우연이 아니다:

| 축 | sceneH6 (val) | **sceneH1 (test-ext)** |
|---|---|---|
| 부지 | 한강 둔치 · 진입 광장 → 관리통로 | **소하천 제방 관리도로** → 호안 점검로 |
| 상부 포장 | 인터로킹 200×100 (`levee_paved`) | **콘크리트 타설 포장 + 수축줄눈** (`alley_concrete`) |
| 마루 → 하부 이행 | 화강석 3단 (라이즈 0.1667) | **콘크리트 4단** (라이즈 0.13 · 트레드 0.40) |
| 낙차 구조물 | 화강석 갓돌 + **사석 호안** + 수면 | **콘크리트 파라펫 + 계단식 호안 2단 + 자갈 여울 + 저수로** |
| 난간 | 화강석 **동자기둥**(원형 캡) 2단 횡대 · 피치 1.50 | **화강석 각기둥** 3단 횡대 · 피치 1.80 |
| 표지 | 하천구역 안내(`sign_info`) | **관계자외 출입금지**(`sign_no_entry`) |
| 드레싱 | 억새 밴드 · 양버들 · 아파트 실루엣 | **갈대 군락 · 미루나무(느티) · 대안 강변 고가도로 + 둔치** |
| 계절/톤 | 여름 (`grass_tint` 0.42/0.55/0.30) | **초가을** (0.46/0.50/0.27) · 자갈·콘크리트 회색조 |

────────────────────────────────────────────────────────────────────────────
씬 조립 공식 (4요소 — 브리프 §2.0)
  ① 경로   제방 마루 **관리도로**(z 0.00) → 성토 **잔디 둔덕**을 넘어 → 콘크리트 4단 →
           **호안 상단 점검로**(z 0.62, 폭 1.83 m)
  ② 위험   점검로 끝 **호안 파라펫** — 노출면 2.24 m, 저수로 수면까지 **2.57 m** 낙차
  ③ 단서   화강석 난간 · 점형블록 · 재질 전이 · 출입금지 표지 · 갈대 군락 · 배수 맨홀 ·
           U형 측구 · 수목보호격자 · 볼라드 · 수축줄눈 · 시선유도봉 — 전부 **토글형 자립 프림**
  ④ 은닉   **BermCrest** (성토 둔덕 마루 z 1.14) — 마루가 낙차 개구보다 카메라에 **가깝고 높다**.
           스침각에서 점검로·파라펫 갓돌·호안·수면이 통째로 마루 뒤로 사라진다.

*"주변 환경은 장식이 아니라 단서 ③ 그 자체다"* — 둔덕만 덩그러니 만들면 이 씬은 실패다.

────────────────────────────────────────────────────────────────────────────
좌표계 · 종단면 (walk axis = +X, Z-up, m. 카메라는 x = −d 에 서서 +X 를 본다)

    x            z         무엇                                   프림
  ≤ −9.60      0.000      제방 마루 관리도로 (콘크리트 포장)      Ground/Crown
  −9.60→−4.80  0.00→1.14  성토 둔덕 사면 (1:4.21) — **중앙 4.6 m  Ground/BermRise{S,C,N}_00..47
                          콘크리트 관리 램프 + 잔디 어깨**
  −4.80→−4.05  1.140      **성토 둔덕 마루** (폭 0.75)            **BermCrest/{S,C,N}**  ← ④ 은닉체
  −4.05→−2.45  1.14→0.62  콘크리트 4단 (R 0.13 · T 0.40)          Ground/ShoulderStep_0..3
  −2.45→−0.62  0.620      호안 상단 점검로 (폭 1.83)              Ground/InspectWalk
  −0.62→−0.20  0.620      파라펫 갓돌 — 점검로와 **동일 z**       RetainWall/Coping ← 낙차 지지 구조물
  −0.20→ 0.95 −1.620      계단식 호안 1단                         Revet/T0
   0.95→ 2.10 −1.900      계단식 호안 2단                         Revet/T1
   2.10→26.0  −2.050      자갈 여울(하상)                         Bed/Gravel
   3.40→26.0  −1.950      저수로 수면                             Water/Surface
  ≥ 26.0       0.700      대안 둔치 — **높이맵 격자 밖**          FarBank/*
   35.2        5.200      대안 강변 고가도로 — **격자 밖**        Dress/Viaduct*

  낙차 = 0.620 − (−1.950) = **2.570 m** (브리프 "하천측 옹벽 낙차 2.5–3.0 m" 준수)
  파라펫 노출면 = 0.620 − (−1.620) = **2.240 m**

────────────────────────────────────────────────────────────────────────────
H 수율 설계 (§3.2 · 이 씬이 존재하는 이유)

**SCENE_H67_BUILD §2.2 의 확정 교훈을 설계 입력으로 삼는다** — *"실효 구속은 **림 조건**이다.
내부 조건이 아니다."* 갓돌 상면의 깊이 불연속이 라벨러 3×3 깊이 창(RIM_TOL 0.35 m)에
먹히지 않기 때문이며, 이 씬의 갓돌도 화강석 상면(H6)이 아니라 **콘크리트 파라펫 갓돌**이라
불연속은 오히려 더 크다. 따라서 `_h_max(d)` 의 기본 판정은 `crit="rim"` 이다.

가림은 **마루 모서리 C = (−4.05, 1.14)** 를 스치는 시선 하나로 닫힌다. 눈 E = (−d, z(−d)+h),
C 를 지나는 직선의 기울기 s = (cz − z_eye) / (d + cx), cx = −4.05:

  · 낙차 **림**(갓돌 상면 z 0.62 · x −0.20) 은닉 : s ≥ (0.62 − 1.14)/3.85 = **−0.1351**
  · 낙차 **내부**(수면 z −1.95 · 격자 동단 x 14.0) 은닉 : s ≥ (−1.95 − 1.14)/18.05 = **−0.1712**

  |s_rim| < |s_int| 이므로 **림이 실효 구속**이다 — H6 실측이 지목한 그 관계가 이 씬에서는
  설계 시점부터 성립한다(H6 는 −0.1420 / −0.1849 로 같은 부호 관계였다).

⇒ H 조건 (림, 실효)  :  h ≤ 1.14 + 0.1351·(d − 4.05) − z(−d)
⇒ H 조건 (내부, 상한) :  h ≤ 1.14 + 0.1712·(d − 4.05) − z(−d)

  d      z(−d)    h_max(림)   H밴드[0.25,1.0] 통과율   base[0.25,1.9] 통과율
  4.5    1.140      0.061            0.00                    0.00
  5.0    1.093      0.176            0.00                    0.00
  6.0    0.855      0.548            0.40                    0.18
  7.0    0.618      0.921            0.89                    0.41
  8.0    0.380      1.294            1.00                    0.63
  ≥9.6   0.000       ↑               1.00                    1.00
  ---------------------------------------------------------------------------
  밴드 적분 (d ~ LogU · CPU 자기검사가 매 실행 인쇄) : **H 0.91 · base 0.22**

  계획 §3.2 가정 = H 밴드 수율 **0.50** (24컷 × 0.5 = paired-H ≥ 12).
  설계 기대 A팔 48컷 = 24·0.22 + 24·0.91 ≈ **27** — 하한 12의 **2.3 배**.
  **퇴화 아님**: base 밴드의 78 %는 V/E 로 남는다(근거리 d ≲ 4.8 에서 카메라가 마루 위에
  올라서면 낙차가 그대로 보인다). 전 프레임 H 인 씬은 H 통계가 아니라 상수다.

**모서리 소속 게이트(VG-06) 적합성**: H 프레임에서 가시 지면은 **BermCrest** 상면에서 끝난다.
점검로·갓돌·파라펫·호안·자갈 여울·수면은 전부 마루 그림자 안이므로 **낙차 구조물의 화면
기여 = 0 px**. `BermCrest` 는 `hazard_*` 밖에서 지어지는 자립 지형 솔리드이며 `_structural` 등재.

────────────────────────────────────────────────────────────────────────────
프림 위생 · 데이텀 (CUE_COVERAGE §4-4 (2)(3)(4) · SCENE_H67_BUILD §5 승계)

1. **단서 빌더는 어느 것도 `if cfg["hazard_*"]` 안에 있지 않다** — s14 파라펫 사고 재발 방지.
   `grep 'cfg\\["hazard_stairs"\\]'` 이 이 파일에서 잡는 줄은 **조립부 2줄 + 자기검사**뿐이다.
2. **모든 `cue_*` 프림은 x ≤ −0.62 (보행 가능측)** 에 선다. 낙차 발자국(x ≥ −0.20)을 덮는
   단서 프림이 **0개**이므로 라벨러 `cells_raw`·`polar_gt` 는 `cue_*` 토글에 **구성상 불변**이다
   (VG-01 의 실효 내용). 자기검사 (4) 가 스테이지 전수 AABB 로 이것을 매 조립마다 확인한다.
3. **카메라 데이텀 스트립** `x ∈ [−12.05, −1.15] · |y| ≤ 0.95` 안에서 상면을 움직이는 토글
   프림은 점형블록(4 mm)·나이징(12 mm)·지면문양(≤8 mm)뿐 — 전부 `datum_tol`(≤0.02 m)이고
   `datum_fail` 은 **0건**이다. `datum_selfcheck()` 가 조립 직후 기계 검사한다.
4. **void 커버리지 1.0** (VG-void): 낙차 발자국 전역(x ∈ [−0.20, 14.0])에 실제 바닥 프림 —
   호안 2단 + 자갈 여울이 빈틈없이 덮고 그 위에 수면이 얹힌다. 개방 바닥 0.

────────────────────────────────────────────────────────────────────────────
표준법 (법1–법8) 준수 메모
  법1 손상·노후 금지  — 파라펫·난간·포장 전부 **온전한 신품 상태**. `surface=None` 로
                         잡초·균열·오염 데칼도 끈다.
  법2 임의 경고판 금지 — 표지는 `sign_no_entry`(법정 제식, 하천 점검로 출입 제한) 1매뿐.
  법4 기능 필수성      — 난간(2.57 m 낙차 · **법정 의무는 아니다** — 하천설계기준에 제방·
                         호안 난간 조문 부재 `[확인]`. 높이만 도로안전시설 지침 2.3.3 나의
                         110 cm 표준. 관행 설치이며 그래서 낙차의 지표가 아니다) · 볼라드(제방 진입
                         차량 억제) · 맨홀·U형 측구(관리도로 배수) · 점형블록(교통약자법).
                         조형물 0. `cue_delineator` 는 기본 OFF("비움이 기본값").
  법5 차량·계절소품 금지 — 차량 0, 계절 소품 0. `SEASON` 은 재질 톤 선언일 뿐이다.
  법6 재질 동결        — 신규 재질 역할 0. 전부 기존 TEX 역할의 재조합.
  법7 `cue_*` 기하 불변 — 최대 융기는 나이징 12 mm · 맨홀 7.7 mm · 점형블록 4 mm 로 전부
                         hazard_depth 0.30 m 의 1/25 이하이고 **낙차 발자국 밖**이다.
  법8 근거 태그        — 수치 주석에 `[계획]`/`[규격]`/`[computed]`/`[측정]` 표기.

실행
    unset PYTHONPATH VIRTUAL_ENV; conda activate env_isaaclab; export PYTHONNOUSERSITE=1
    python scenes/main/sceneH1_berm_levee.py                 # GUI 룩체크
    NEGOBS_SMOKE=1 python scenes/main/sceneH1_berm_levee.py   # CPU 조립 스모크(부팅 전 종료)
데이터 렌더 진입점 (신설 씬은 AZ 원장 등재 전까지 이 경로가 유일 — CUE_COVERAGE §4-4 (6)):
    python experiments/v3_0823/code/h67_probe.py --scene sceneH1 --run <stamp> ...
"""

import os
import sys
import math
import json
import datetime

import scene_common as sc
import ground_kit as gk
import infra_kit as ik
import props_kit as pk


# [계획 §2.0] 생활권 = 제방·수변. 계절은 **초가을** — val 공급원 sceneH6(여름 한강 둔치)와
#   톤을 분리한다(부지 분리 선언 표 8행).
SEASON = "early_autumn"


# ===========================================================================
# [A0] CUE_CLASS — 렌더 **전** 사전 분류 (RENDER_PLAN_V3 §2.6 / ACCOUNTING §2-6)
# ===========================================================================
#   *"신규·개편 씬은 cue_* 토글 + 가드 구조물/장식 사전 분류를 표준 장비로 제작한다.
#     분류는 렌더 전에 끝나야 하며, 렌더 후 분류는 사후 선택이 된다."*
#   렌더 후 VG-01/VG-02 가 이 선언을 **기계 반증**한다. 선언과 실측이 어긋나면 그 씬은
#   **씬 결함**으로 반려하며, 결과를 보고 이 표를 고치지 않는다.
CUE_CLASS = {
    "cue_railing":         "decorative",   # 화강석 각기둥 난간. 낙차는 RetainWall 이 정의한다
    "cue_tactile":         "decorative",   # **계단 상단 점형블록 1밴드** (0.30 m · proud 4 mm)
                                           #   [R4] 갓돌 앞 밴드 삭제 — D82ⓐ 설치-규정 감사
    "cue_nosing":          "decorative",   # 콘크리트 4단 논슬립 띠 (proud 12 mm, 낙차 아님)
    "cue_material_break":  "decorative",   # **재질 재바인딩 전용** — 프림 집합 불변
    "cue_sign":            "decorative",   # 하천 점검로 출입 제한 법정 표지 1매
    "cue_scene_dressing":  "decorative",   # 갈대 군락·벤치·관목·고가도로·대안 둔치
    "cue_shadow_caster":   "decorative",   # 미루나무 열 + 가로등주 — 그림자 밴드 캐스터
    "cue_manhole":         "decorative",   # 관리도로 배수 맨홀 (flush)
    "cue_tree_grate":      "decorative",   # 관리도로 수목보호격자 (flush)
    "cue_slab_joint":      "decorative",   # 콘크리트 수축줄눈 (recess 3 mm)
    "cue_drainage":        "decorative",   # U형 측구(복개) — 관리도로 배수, flush 뚜껑
    "cue_bollard":         "decorative",   # 제방 진입 차량 억제 볼라드
    "cue_delineator":      "decorative",   # 반사 시선유도봉 (기본 OFF — 법4 "비움이 기본값")
    # ── 토글 금지 목록 (구조물). 이 프림들은 어떤 cue_* 도 참조하지 않는다 ──────────
    "_structural":         ["BermCrest", "RetainWall", "Revet", "Bed", "Water",
                            "Ground/ShoulderStep", "Ground/InspectWalk"],
}


# ===========================================================================
# [A] SCENE_CONFIG — **표준 장비 16키** (RENDER_PLAN_V3 §2.0 · CUE_COVERAGE §4-4 (1))
# ===========================================================================
#   구성: 공통 cue 6 + v3 신설 3(`cue_shadow_caster`·`cue_manhole`·`cue_tree_grate`) +
#   FA_REALITY §2 승격 후보 4(`cue_slab_joint`·`cue_drainage`·`cue_bollard`·`cue_delineator`) +
#   hazard 1 + 팔 제어 2 = **16**. **사문 0** — 16키 전부를 읽는 코드가 이 파일 안에 있다.
SCENE_CONFIG = {
    # ── ② 위험: 유일한 기하 토글 ────────────────────────────────────────────
    #   False → 파라펫·호안·자갈여울·수면·대안이 사라지고 점검로 레벨(z 0.62)의
    #   평탄 지면이 x = −0.62 … 26.0 을 채운다(반사실 보행 가능면 z_off).
    "hazard_stairs":      True,
    # ── ③ 단서: 공통 6키 ────────────────────────────────────────────────────
    "cue_railing":        True,   # 화강석 난간 — 2.57 m 낙차의 법정 가드(법4 통과)
    "cue_tactile":        True,   # 점형블록 1밴드 (계단 상단) — 브리프 "경고블록" 명시 항목
    "cue_nosing":         True,   # 콘크리트 4단 논슬립 띠
    "cue_material_break": True,   # 점검로 = 콘크리트 판석 / 관리도로 = 콘크리트 타설
    "cue_sign":           True,   # 출입금지 표지 (법2 — 법정 제식만)
    "cue_scene_dressing": True,   # 갈대·벤치·관목·고가도로·대안을 한 번에
    # ── v3 신설 3키 (FA_REALITY §2) ─────────────────────────────────────────
    #   `cue_shadow_caster` 부작용 경보(§2.0): 음성 씬에만 넣으면 "그림자 = 안전"이라는
    #   역지름길이 생긴다. **양성 씬인 이 씬에도 동일 비율로** 배치한다.
    "cue_shadow_caster":  True,
    "cue_manhole":        True,   # 갭 1위 (25.0) — 관리도로 배수 맨홀
    "cue_tree_grate":     True,   # 갭 2위 (20.0) — 관리도로 수목보호격자(flush)
    # ── FA_REALITY §2 승격 후보 4키 ────────────────────────────────────────
    "cue_slab_joint":     True,   # 갭 5위 — 콘크리트 수축줄눈
    "cue_drainage":       True,   # 갭 3위 — U형 측구(복개) + 빗물받이
    "cue_bollard":        True,   # L2 — 제방 진입 차량 억제 볼라드
    "cue_delineator":     False,  # L12 — 반사 시선유도봉. 기본 OFF(법4), 코드 경로 상시 보유
    # ── 팔 제어 2키 ─────────────────────────────────────────────────────────
    "keep_dressing":      False,  # C팔: 위험만 지우고 단서·장식은 ON 변환 그대로 유지
    "placebo_remove":     False,  # P팔: 위험·단서 유지, 비단서 물량군(원경 고가도로)만 제거
}


# ===========================================================================
# [B] PARAMS — 전 수치. 종단면은 파일 상단 표와 **한 글자도 어긋나지 않는다**
# ===========================================================================
PARAMS = dict(
    # ── 지형 (전부 hazard_* 밖. 4팔 공통) ────────────────────────────────────
    #   `y_half` 9.5 : 높이맵 격자 y ∈ [−8, 8] 을 1.5 m 여유로 덮는다. 격자 가장자리에서
    #   지면이 끝나면 그 칸이 void 가 되어 VG-void (b) 를 깨뜨린다.
    terrain=dict(
        y_half=9.5, base_z=-1.20,
        crown=dict(x0=-26.0, x1=-9.60, z=0.00),
        # [개정 R3] `pave_y_half` = 관리 램프 **포장 밴드 반폭**. 제방을 넘는 관리도로는
        #   실제로 포장되고 어깨만 잔디다. 이 값은 **재질 경계**일 뿐 기하가 아니다 —
        #   마루 x·z, 점검로 z, 림 x 가 전부 불변이므로 은닉 판정식과 수율 모형은
        #   한 글자도 바뀌지 않는다(개정 전후 CPU 자기검사 H 0.918 · base 0.216 동일).
        rise=dict(x0=-9.60, x1=-4.80, z0=0.00, z1=1.14, n_seg=48, thick=0.25,
                  pave_y_half=2.30),
        # [computed] 4.80 m 에 1.14 m → 1:4.21 (13.36°). 조경 성토 둔덕의 통상 구배
        #   (1:3~1:5) 안이며, H6 의 제방 어깨 잔디 사면(1:5.89)보다 가파른 **다른 형태**다.
        # **왜 48개 회전 슬래브인가** (SCENE_H67_BUILD R2 승계) — 두 요구가 충돌한다:
        #   ⓐ `AabbPrefilter.ground_z` 는 상방 레이의 최초 히트라 **회전체 하나**로 지으면
        #      경사 전체를 마루 높이 평면으로 읽는다 → `cam.ground_z` 와 높이맵이 동시에 틀린다.
        #   ⓑ 축정렬 계단으로 근사하면 라이즈 면이 그대로 보여 **가로 줄무늬 논밭**이 된다
        #      [측정: 260823_v3p5_h67smoke_A 1차].
        #   ⇒ 같은 평면 위 회전 슬래브 48장(구간 0.10 m)으로 면은 완전 연속, AABB 오차는
        #      구간당 상승 0.0238 m + 두께 회전분으로 ≤ 0.035 m 에 갇힌다. 4팔 공통 편향이라
        #      VG-datum 은 영향받지 않는다.
        crest=dict(x0=-4.80, x1=-4.05, z=1.14),
        # 마루 평탄 0.75 m. 길게 잡을수록 가림이 약해진다(마루 위 카메라가 낙차를 본다).
        steps=dict(x0=-4.05, z_top=1.14, riser=0.13, tread=0.40, n=4),
        # [규격] 라이즈 0.13 · 트레드 0.40 — 조경설계기준 완경사 계단(라이즈 0.12~0.15 ·
        #   트레드 0.35~0.60). H6 의 화강석 3단(0.1667/0.50)과 단수·치수가 모두 다르다.
        walk=dict(x0=-2.45, x1=-0.62, z=0.62),   # 호안 상단 점검로 폭 1.83 m
    ),
    # ── 위험 (hazard_stairs 전속) ───────────────────────────────────────────
    hazard=dict(
        coping=dict(x0=-0.62, x1=-0.20, z_top=0.62, thick=0.16),
        wall=dict(x0=-0.60, x1=-0.20, z_top=0.46, z_bot=-3.10),
        revet=[dict(x0=-0.20, x1=0.95, z_top=-1.62),
               dict(x0=0.95, x1=2.10, z_top=-1.90)],
        revet_base=-3.40,
        bed=dict(x0=2.10, x1=26.0, z=-2.05),
        water=dict(x0=3.40, x1=26.0, z=-1.95, thick=0.22),
        # [computed] 낙차 = 0.62 − (−1.95) = 2.570 m · 파라펫 노출면 = 0.62 − (−1.62) = 2.240 m
        farbank=dict(x0=26.0, x1=64.0, z=0.70, base_z=-3.40),
        fill=dict(x0=-0.62, x1=26.0, z=0.62, base_z=-1.20),   # hazard=False 반사실 지면
    ),
    # ── ③ 단서 파라미터 ─────────────────────────────────────────────────────
    #   전부 x ≤ −0.62 (보행 가능측). 낙차 발자국(x ≥ −0.20)을 덮는 단서 프림 0개.
    rail=dict(x=-0.80, y_half=9.0, post_pitch=1.80, post_a=0.16,
              post_h=1.06, cap_t=0.07, rail_r=0.022,
              top_z=1.72, mid_z=1.30, low_z=0.94),
    # [규격·정정 R4 · D82ⓐ] 난간 방호면 상단 **1.10 m** — 근거는 **「도로안전시설 설치 및
    #   관리지침」 2.3.3 나**("난간의 높이는 … **110 cm 를 표준**으로 한다. 높이는 노면
    #   (보도가 있는 경우 보도면)으로부터 **난간 방호면의 상단**까지").
    #   **구 주석의 "건축법 시행령 §40" 은 오인용이었다** — §40 은 *옥상광장·2층 이상
    #   노대 주위*에 한정되고 값도 1.2 m 다. 저장소 조사가 이미 잡아 둔 오류다
    #   [`Docs/surveys/cue_arrangement_survey.md` §1.1 정정 상자: *"'난간 규정 1.1 m'는
    #   한국 **법령**에 존재하지 않는다"*] — 1.10 m 는 **지침**의 표준값이다.
    #   더 근본적으로, **하천 제방·호안에는 추락방지 난간 조문이 아예 없다**
    #   [동 §1.3 (f) `[확인 — 부재]`: *"한강 둔치의 저수호안 상단 낙차선은 규정상 아무
    #   방호시설 없이 노출되는 것이 정상 상태"*]. 이 난간은 **법정 의무가 아니라 관행·
    #   발주처 지침**으로 서 있고, 그래서 이 코퍼스에서 "난간 = 낙차" 지름길을 만들지
    #   않는다(단서 ⟂ 낙차). 높이만 지침 표준을 따른다.
    #   [CUE_REGULATION_BASIS §3.1 · §5]
    #   화강석 **각기둥**(0.16각) + 스테인리스 Ø0.044 **3단** 횡대. H6 의 원형 동자기둥
    #   2단(피치 1.50)과 단면·단수·피치가 모두 다르다. 순백 대면적 금지 → 알베도 0.30 대.
    #   x = −0.80 은 카메라 데이텀 스트립(x ≤ −1.15) **밖**이므로 `datum_exact` 를 유지한다.
    # ── [개정 R4 · D82ⓐ 설치-규정 감사] 점형(경고)블록은 이 씬에 **1밴드뿐**이다 ──────
    # [규격·근거] 「교통약자의 이동편의 증진법 시행규칙」 별표2(이동편의시설의 구조·재질
    #   등에 관한 세부기준) — 점형블록은 **계단·경사로의 시작과 끝** 및 위험 지점의
    #   **0.3 m 전면**에 설치하며, 블록 규격은 **0.30 m × 0.30 m**(KS F 4561)이다.
    #   위험 경계 **1곳당 점형 밴드는 1개**다(D82 ⓐ). 밴드 **안**의 유닛 열 수는 별개
    #   문제로, 국도건설공사 설계실무요령 7.5 가 세로폭 **30~90 cm(60 cm 표준)** 를 준다.
    #   ⇒ 룩체크가 지적한 "점자블록 두 줄"은 **분리된 2밴드**(마루 + 갓돌 앞, 간격 3.2 m)
    #     를 말하며, 한 밴드 안의 유닛 2매 열과는 다른 것이다.
    #
    #   ⓐ **삭제** — 구 `Tactile`(갓돌 앞 0.30 m · 세로 0.40 m · x −1.32…−0.92 · 6.88 m²).
    #      그 자리는 `sign_no_entry`(관계자외 출입금지) **뒤쪽 호안 점검로**다. 점검로는
    #      교통약자법의 **대상시설이 아니므로** 점형블록 설치 의무가 없고, 2.57 m 낙차는
    #      난간이 가드한다(법4). 3.2 m 간격으로 노란 밴드가 두 줄 서는 그림은 실제 시공에
    #      존재하지 않는 **과잉 설치**였다 [사용자 룩체크 R7 지적 · D82 ⓐ].
    #      [실측 260823_v3p5_h12rev_A] 이 밴드는 16컷 중 **2컷에서만** 보였고 그 2컷은
    #      둘 다 **비-H(V) 프레임**이다(화면 기여 100,658 px) ⇒ strict-H 정보량 손실 0.
    #   ⓑ **유지·재배치** — 마루 **계단 상단** 1밴드. 세로 0.40 → **0.30 m**(유닛 1매),
    #      마루 코(x = −4.05) 이격 0.10 → **0.30 m**(별표1 "위험장소 0.3 m 전면").
    #      세로폭 **0.30 m 는 범위 하한**이다 — 표준은 0.60 m(유닛 2매, `sceneN9` 와 동일)
    #      이지만 **마루 평탄부가 0.75 m 뿐**이라 0.30(이격) + 0.60(밴드) = 0.90 m 가
    #      물리적으로 들어가지 않는다. 국도 실무요령 7.5 가 세로폭을 **30~90 cm 범위**로
    #      준 이유가 정확히 이런 폭 제약이다 [규격 국도건설공사 설계실무요령 7.5].
    #      0.40 m 는 300 mm 모듈의 정수배가 아니라 **시공 불가 치수**였다 — 그것이 이
    #      항목의 실제 결함이고, 0.30 m 는 유닛 1매로 시공된다.
    crest_tactile=dict(x0=-4.65, x1=-4.35, proud=0.004),
    #   [검산 VG-06] 마루 코를 스치는 시선은 x = −4.35 에서 1.140 + 0.135·0.30 = 1.1805
    #   를 지나므로 점형블록 상면 1.144 를 **항상 넘는다** ⇒ 점형블록이 코를 가릴 수
    #   없다(구성상). 이격을 0.10 → 0.30 으로 넓혔으니 여유는 R3 보다 **커졌다**.
    #   포장 밴드(|y| ≤ 2.30) 위에만 깔린다 — 잔디 위 점형블록은 시공되지 않는다.
    nosing=dict(width=0.055, proud=0.012),          # [계획] 노징 12 mm (realism_v1_final §84)
    sign=dict(x=-3.30, y=3.60, yaw=180.0, pole_h=2.05, w=0.58, h=0.58),
    # [규격] 볼라드 h 0.8~1.0 · φ0.10~0.20 · 간격 ~1.5 m · 반사띠 (user_feedback_v5_1 §2)
    #   `xs` 를 y = −4.50 의 보차도 경계선과 나란한 열로 잡는다 — 실제 볼라드 열의 기본형이고,
    #   동시에 ⓐ 피치 1.50 m 를 한 번도 깨지 않으며(LINT-6 하드 규칙) ⓑ 카메라 데이텀
    #   스트립(|y| ≤ 0.95)을 **한 본도 침범하지 않는다**(VG-datum).
    #   위치 지터는 두지 않는다 — J-3/J-5(07-30)가 배치 지터를 폐지했고 LINT-10 이 정적 검사한다.
    bollard=dict(y=-4.50, xs=(-15.20, -13.70, -12.20, -10.70, -9.20),
                 r=0.075, h=0.90, band_z=0.68, band_t=0.09),
    delineator=dict(x=-7.30, ys=(-2.20, 2.20), r=0.041, h=0.80),
    gkit=dict(
        # (a) 제방 마루 관리도로 — 맨홀 · U형 측구 · 수축줄눈. 낙차 림에서 9 m 이상
        #     떨어져 있으므로 `plan_ground` 하드 게이트 B7(GT-E2, 림 근방 대리선 금지)에
        #     걸리지 않는다.
        crown_region=(-24.0, -8.60, -9.65, 8.60),
        manholes=[(-11.35, 2.55), (-17.90, -3.05)],
        gullies=[(-13.60, 5.30), (-19.40, -5.40)],
        # `sites["gutter_U"]` 는 **y 값 하나**다(ground_kit:3199) — U형 측구는 region 의
        #   x 전 구간을 그 y 에서 종단 방향으로 달린다. 보행축과 **나란한** 선이므로
        #   낙차 림과 평행한 대리선이 아니고, region 동단이 림에서 9 m 떨어져 있어
        #   하드 게이트 B7(GT-E2)에 걸리지 않는다.
        gutter_y=-6.35,
        tree_grates=[(-11.20, 4.15), (-18.20, 4.15), (-25.20, 4.15)],
        # (b) 호안 상단 점검로 — **복개 슬래브 줄눈만**(P17 `verge_rural`).
        #     프로파일 선택 근거 두 가지: ⓐ 어휘 — 하천 점검로는 개거 복개 슬래브가
        #     정확한 시공 유형이다 ⓑ **U2 게이트** — `alley_concrete` 는 unit_cell 3.0 이라
        #     폭 1.79 m 구간에 횡줄눈이 한 줄도 들어오지 못하고 step_x 를 줄이면 U2 위반이
        #     된다(설계 시 실측: step_x 1.6 → "unit_cell 3.0 의 정수배가 아니다" 로 거부).
        #     `verge_rural` 은 unit_cell = None(무모듈)이라 step_x 1.6 이 허용되고,
        #     그 결과 x = −1.60 에 줄눈 한 줄이 들어온다. (H6 R1 교훈의 이 씬 판본)
        walk_region=(-2.45, -8.60, -0.66, 8.60),
        walk_step_x=1.6,
        # (c) [개정 R3] 관리 램프 **횡단 줄눈 6줄** — 램프 표면(경사)을 따라간다.
        #     치수 근거와 그 한계를 여기에 남긴다:
        #       · 간격 0.80 m — `alley_concrete` 의 시공줄눈 3.0 m 로는 사면 길이 4.80 m 에
        #         한 줄도 들어오지 않는다. 급경사 콘크리트 포장의 **가로 홈파기(미끄럼방지)**
        #         가 이 간격대에 있다.
        #       · 폭 0.060 m — 킷의 `groove_w` 0.010 m 보다 **6배 넓다**. 이유는 순전히
        #         가시성이다: 10 mm 는 d 5 m 스침각에서 3–4 px 라 이 씬이 회복하려는
        #         **평행 밴드 어휘**가 픽셀로 남지 않는다 [실측: R0 프레임의 단서 px = 0].
        #         **이 치수는 R7 룩체크 항목으로 올린다** — 사용자가 좁히라고 하면
        #         `ramp_joint_w` 한 값만 고치면 되고 기하·수율은 영향받지 않는다.
        #     flush(융기 2 mm) · 낙차 발자국 밖 · 팔 토글은 `cue_slab_joint`.
        ramp_joints=(-9.20, -8.40, -7.60, -6.80, -6.00, -5.20),
        ramp_joint_w=0.06,
    ),
    shadow=dict(
        # [FA_REALITY §2 4위] 그림자 밴드 캐스터. **양성 씬에도 동일 비율**(§2.0 경보).
        #   시선 통로(|y| ≤ 3.8 · x ∈ [−12, 0])는 비워 둔다 — 수목이 낙차를 가리면
        #   VG-06 의 "가림체가 종단 모서리를 소유" 판정이 둔덕이 아니라 수목으로 넘어간다.
        #   남측 열 `crown_S` — 피치 7.0 m (조례 제7조1가 6~8 m) · 1수종(느티=elm 대체)
        poplars=[(-10.40, -5.90), (-17.40, -5.90), (-24.40, -5.90)],
        poplar_h=8.4,
        lamps=[(-6.20, 4.70), (-12.40, -4.65), (-18.60, 4.70)],
        lamp_h=4.4, lamp_arm=1.00,
    ),
    dress=dict(
        # 갈대 군락 — 점검로 배후, 시선 통로 밖(|y| ≥ 4.5)
        reed_bands=[(-2.42, -8.40, -1.70, -4.50), (-2.42, 4.50, -1.70, 8.40)],
        reed_h=1.35,
        #   벤치 yaw 는 **축값만** — J-3/J-5 지터 폐지(spec §1.2)를 LINT-7 이 강제한다.
        benches=[(-6.80, 3.25, 270.0), (-9.10, -3.15, 90.0)],
        #   북측 가로수 열 `crown_N` — 피치 7.0 m · 1수종(elm)
        trees=[(-11.20, 4.15), (-18.20, 4.15), (-25.20, 4.15)],
        tree_h=5.6,
        hedge=[(-8.90, -8.40, -8.30, -4.30), (-8.90, 4.30, -8.30, 8.40)],
        # 원경(placebo 물량군) — **전부 높이맵 격자(x ≤ 14 · |y| ≤ 8) 밖**이라 라벨 무관.
        #   ① 대안 강변 **고가도로**(하천과 나란히 달리는 상부구조 + 교각열)
        #   ② 대안 둔치 방풍림 ③ 배수펌프장
        # [R2 · 1차 스모크 실측] 초안은 상부구조를 x ≈ 17.5(카메라에서 23 m · **수면 한복판**)에
        #   세웠다. 두 가지가 틀렸다: ⓐ 화면 상단 12 %를 밝은 콘크리트 띠가 채웠고(상단 200행
        #   평균 137/255 — 임계는 넘지 않았으나 v5.1 §4 "순백 대면적"의 취지에 어긋난다)
        #   ⓑ **하천을 가로지르는 교량이 아니라 하천과 나란히 선 판**이었다(이 씬의 하천은
        #   x 방향으로 폭 22.6 m 이므로 횡단교는 x 를 가로질러야 한다). 횡단교를 제대로 놓으려면
        #   상판이 격자 안(x ≤ 14)을 지나야 하는데, 그러면 **드레싱 프림이 낙차 발자국 위에
        #   서게 되어 VG-01 이 깨진다**. ⇒ 어휘를 **강변 고가도로**로 바꾸고 대안 뒤(x ≥ 34)로
        #   물렸다. 실제 한국 하천의 표준 원경이며(강변 간선도로 고가), 격자 밖이 보장된다.
        viaduct=dict(x0=34.0, x1=36.4, z=5.20, thick=0.85, y_half=33.0,
                     piers=[(35.2, -24.0), (35.2, -12.0), (35.2, 0.0),
                            (35.2, 12.0), (35.2, 24.0)], pier_w=1.5),
        far_treeline=[(29.0, -21.0), (29.0, -14.0), (29.0, -7.0),
                      (29.0, 0.0), (29.0, 7.0), (29.0, 14.0), (29.0, 21.0)],
        pumphouse=[("P0", 44.0, 52.0, -16.0, -7.0, 5.4)],
    ),

    # ── 재질 3단 (realism_v1_final §84) ─────────────────────────────────────
    #   지면·구조물 = NegObsGround.mdl 경로(텍스처 3매) / 식생·목재 = MDL 상수색 /
    #   금속·도색·사인·유리·수면 = OmniPBR
    material=dict(
        scale=dict(concrete_floor=1.70, plaza_lower=1.70, concrete_wall=2.0,
                   grass=1.4, gravel=1.15, granite_dark=1.80, stone_worn=1.6,
                   tactile=0.3, wood_dark=1.4),
        # 초가을 잔디 — H6 의 여름 톤(0.42,0.55,0.30)과 채도·색상이 다르다
        grass_tint=(0.46, 0.50, 0.27),
        crown_tint=(0.60, 0.60, 0.58),      # 콘크리트 타설 관리도로
        walk_tint=(0.66, 0.65, 0.63),       # 점검로 콘크리트 판석 (알베도 0.30 대)
        step_tint=(0.58, 0.58, 0.56),
        wall_color=(0.305, 0.305, 0.295), wall_rough=0.64,   # alb_max 0.34 이하
        coping_tint=(0.63, 0.62, 0.60),
        revet_tint=(0.55, 0.545, 0.53),
        bed_tint=(0.50, 0.49, 0.46),
        water_color=(0.062, 0.079, 0.074), water_rough=0.16,
        # [v7 ruling · scene12] 수면 rough 하한 0.14 — 무풍 완전거울("인피니티 풀") 방지.
        # [look 층] 재질 프림 이름이 클래스를 정한다 — `Looks/RailStone` 은 "rail" 토큰
        #   때문에 **metal**(alb_max 0.50)로 분류돼 화강석 기둥이 흰 금속 기둥으로
        #   렌더된다 [측정: SCENE_H67_BUILD R3]. `Looks/GranitePost` 로 두면 stone
        #   (alb_max 0.34)으로 떨어지고 텍스처 승격도 석재 계열을 탄다.
        post_color=(0.44, 0.435, 0.42), post_rough=0.56,
        bollard_color=(0.60, 0.61, 0.62), bollard_metallic=0.55, bollard_rough=0.38,
        rail_metal_color=(0.71, 0.72, 0.74), rail_metal=0.85, rail_metal_rough=0.32,
        nosing_color=(0.41, 0.39, 0.35), nosing_rough=0.70,
        band_color=(0.80, 0.52, 0.05),      # 볼라드 반사띠 = 안전 황색(면적 小)
        pole_color=(0.24, 0.24, 0.26), pole_metallic=0.6, pole_rough=0.5,
        lamp_color=(0.78, 0.78, 0.75), lamp_rough=0.4,
        wood_color=(0.31, 0.21, 0.13), wood_rough=0.85,
        reed_tint=(0.52, 0.47, 0.30),       # 초가을 갈대 이삭 톤
        canopy_a=(0.031, 0.048, 0.019), canopy_b=(0.043, 0.062, 0.026),
        canopy_rough=1.0,
        # [v5.1 §4 · 순백 대면적 금지] 고가도로 상부구조는 콘크리트 클래스로 얹어 알베도
        #   상한 0.34 아래로 내린다(H6 R4 교훈 — `Looks/Backdrop` 은 misc = 무처방 상수색).
        bridge_color=(0.26, 0.26, 0.255), bridge_rough=0.72,   # [R2] 0.30 → 0.26
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
    # 태양 방위: 미루나무 열과 가로등주의 그림자가 **보행축을 가로질러** 관리도로에 떨어지도록.
    #   과노출 금지(P-1)는 조건 카탈로그가 담당한다.
    SUN_AZ_OFFSET=169.0,

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
#   모순 설정은 **FATAL** — 자기 뜻을 말하지 못하는 팔이 컷을 찍고 나중에 지표표에서
#   발견되는 일을 막는다.
KEEP_DRESSING = bool(SCENE_CONFIG.get("keep_dressing", False))
PLACEBO_REMOVE = bool(SCENE_CONFIG.get("placebo_remove", False))
if KEEP_DRESSING:
    if SCENE_CONFIG.get("hazard_stairs", True):
        raise SystemExit(
            "[FATAL sceneH1] keep_dressing=True 는 hazard_stairs=False 를 요구한다 — "
            "위험이 켜져 있으면 보존할 것이 없고 그 팔은 A팔의 라벨 없는 복제가 된다.")
    if not SCENE_CONFIG.get("cue_scene_dressing", True):
        raise SystemExit(
            "[FATAL sceneH1] keep_dressing=True 와 cue_scene_dressing=False 는 모순이다 — "
            "장식이 바로 이 팔이 보존하려는 대상이다.")
if PLACEBO_REMOVE:
    if not SCENE_CONFIG.get("hazard_stairs", True):
        raise SystemExit(
            "[FATAL sceneH1] placebo_remove=True 는 hazard_stairs=True 를 요구한다 — "
            "플라시보 팔은 위험 ON 상태의 외형 대조군(D35)이다.")
    if KEEP_DRESSING:
        raise SystemExit(
            "[FATAL sceneH1] placebo_remove 와 keep_dressing 은 서로 다른 팔(P·C)이며 "
            "동시에 설정될 수 없다.")
_ARM = ("C_hz0_cue1" if KEEP_DRESSING else
        "P_hz1_placebo" if PLACEBO_REMOVE else
        "hz%d_rail%d_tac%d_mat%d_dress%d" % (
            int(SCENE_CONFIG["hazard_stairs"]), int(SCENE_CONFIG["cue_railing"]),
            int(SCENE_CONFIG["cue_tactile"]), int(SCENE_CONFIG["cue_material_break"]),
            int(SCENE_CONFIG["cue_scene_dressing"])))
print(f"[sceneH1] arm={_ARM} keep_dressing={KEEP_DRESSING} "
      f"placebo_remove={PLACEBO_REMOVE}")


# ===========================================================================
# [C] 경로 상수 · 필요 텍스처 역할 · 데이텀 선언
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "sceneH1")

ASSET_ROLES = ["concrete_floor", "plaza_lower", "concrete_wall", "grass",
               "gravel", "granite_dark", "stone_worn", "tactile", "wood_dark",
               "sign_no_entry", "hdri", "mdl"]

# 카메라 데이텀 스트립 — `variation_kit.sample_camera` 가 뽑는 (d, y) 의 지지집합.
#   d ∈ LogU[1.2, 12] ⇒ x = −d ∈ [−12.00, −1.20] · y ∈ trunc-N(0, 0.35) 잘림 ±0.90.
#   각 방향으로 0.05 m 여유를 더해 [−12.05, −1.15] × [−0.95, 0.95].
DATUM_STRIP = dict(x0=-12.05, x1=-1.15, y0=-0.95, y1=0.95)

# VG-datum 3층 임계 (ACCOUNTING §4.9-5): `datum_exact` < 1e-6 · `datum_tol` ≤ 0.02 m ·
#   `datum_fail` > 0.02 m(격리).
DATUM_TOL = 0.02

# 토글되는(= 팔에 따라 사라지는) 빌더가 만드는 프림의 XY 범위와 **지면 위 최대 융기 dz** 선언.
#   `datum_selfcheck()` 가 이 표와 DATUM_STRIP 의 교차를 기계 검사하고, 교차분은 dz 로
#   3층 분류한다. 표를 채우는 것은 손이고 검사하는 것은 기계다 — 손이 빠뜨려도
#   (2) 스테이지 전수 AABB 검사가 같은 판정을 독립으로 다시 낸다.
GATED_ZONES = [
    # (tag, key, x0, x1, y0, y1, dz)
    ("RetainWall",   "hazard_stairs",      -0.64,  -0.18,  -9.60,  9.60, 3.72),
    ("Revet",        "hazard_stairs",      -0.20,   2.10,  -9.60,  9.60, 1.80),
    ("Bed",          "hazard_stairs",       2.10,  26.00, -11.00, 11.00, 1.35),
    ("Water",        "hazard_stairs",       3.40,  26.00, -11.00, 11.00, 0.22),
    ("FarBank",      "hazard_stairs",      26.00,  64.00, -33.00, 33.00, 4.10),
    ("FlatFill",     "hazard_stairs(off)", -0.62,  26.00, -33.00, 33.00, 1.82),
    # 난간은 x = −0.80 → 데이텀 스트립(x ≤ −1.15) **밖**이다. 교차 0.
    ("Rail",         "cue_railing",        -0.90,  -0.70,  -9.10,  9.10, 1.10),
    # 점형블록: [개정 R4 · D82ⓐ] **1밴드**(계단 상단)만 남는다. 갓돌 앞 밴드는 출입금지
    #   점검로의 과잉 설치라 삭제했다 — 데이텀 스트립(x ≤ −1.15)과 겹치던 유일한 단서
    #   프림이 사라졌으므로 `datum_tol` 목록도 한 줄 짧아진다.
    ("TactileCrest", "cue_tactile",        -4.65,  -4.35,  -2.30,  2.30, 0.004),
    ("GKitRamp",     "cue_slab_joint",     -9.20,  -5.14,  -2.30,  2.30, 0.002),
    ("Nosing",       "cue_nosing",         -4.06,  -2.44,  -9.60,  9.60, 0.012),
    ("Sign",         "cue_sign",           -3.65,  -2.95,   3.25,  3.95, 2.05),
    ("Bollard",      "cue_bollard",       -15.28,  -9.12,  -4.58, -4.42, 0.90),
    ("Delineator-S", "cue_delineator",     -7.40,  -7.20,  -2.30, -2.10, 0.80),
    ("Delineator-N", "cue_delineator",     -7.40,  -7.20,   2.10,  2.30, 0.80),
    # ground_kit: 줄눈 recess 3 mm(융기 0) · 맨홀 7.7 mm · 측구 뚜껑 flush · wear_lane 1.2 mm.
    #   `surface=None` 로 잡초(proud 최대 0.107 m)를 **끈다** — 법1(노후·방치 표현 금지)과
    #   VG-datum 이 같은 방향을 가리키는 드문 경우다.
    ("GKitCrown",    "cue_manhole/slab_joint/drainage",
                                          -24.00,  -9.65,  -8.60,  8.60, 0.008),
    ("GKitWalk",     "cue_slab_joint",     -2.45,  -0.66,  -8.60,  8.60, 0.008),
    ("TreeGrate",    "cue_tree_grate",    -26.00, -10.40,   3.40,  4.90, 0.004),
    ("Shadow-S",     "cue_shadow_caster", -26.00,  -5.00, -10.00, -3.90, 8.40),
    ("Shadow-N",     "cue_shadow_caster", -20.00,  -5.00,   3.90, 10.00, 8.40),
    ("Dress-S",      "cue_scene_dressing", -26.00,  64.00, -33.00, -1.65, 12.0),
    ("Dress-N",      "cue_scene_dressing", -26.00,  64.00,   1.65, 33.00, 12.0),
    ("Dress-Far",    "cue_scene_dressing",  16.00,  64.00, -33.00, 33.00, 12.0),
]


# ===========================================================================
# [C'] PLACEMENT — `placement_lint.py` 의 기하 무관 선언 블록 (w3_execution_spec §10.4)
# ===========================================================================
#   *"A rule whose datum is undeclared does not silently pass."* 기존 33씬은 이 블록을
#   **0개** 선언해 LINT-1/1b/3/5/9 가 구조적으로 죽어 있었다. 신규 씬은 그 상태를 승계하지
#   않는다 — 프림을 하나도 만들지 않는 순수 선언이라 기하·GT·높이맵 영향이 **0**이다.
PLACEMENT = dict(
    # `walk_edges` 는 **의도적으로 선언하지 않는다.** LINT-5 는 「도로의 구조·시설 기준에
    #   관한 규칙」 제16조의 **보도 유효폭**을 재는 규칙인데, 이 씬의 상부 경로는 보도가
    #   아니라 제방 **관리도로**(차량 통행 가능·보도 구분 없음)다. 없는 데이텀을 지어내면
    #   그 규칙은 검사가 아니라 허구가 된다 — 미선언은 `nodata` 로 보고되지 거짓 통과가 아니다.
    #   (SCENE_H67_BUILD §5-5 가 sceneH6 에서 내린 것과 같은 판단)
    kerb_lines=[((-16.2, -4.50), (-8.2, -4.50))],
    anchors={
        "crown_N": dict(face_bearing_deg=270.0, props=["Bench_0"]),
        "crown_S": dict(face_bearing_deg=90.0, props=["Bench_1"]),
        # `sc.build_sign` 의 `/Panel` 은 월드 좌표로 직접 작도되는 메시라 xformOp 자체가
        #   없다(scene_common.py:4572-4595). 인벤토리에서 읽히는 그 프림의 yaw 는
        #   **구조적으로 0** 이고, 실제 정면 방위는 `/Back` 이 갖는다.
        "rim_notice": dict(face_bearing_deg=180.0, props=["Sign/Back"]),
        "walk_axis": dict(face_bearing_deg=0.0, props=["Sign/Panel"]),
    },
    # 가로수 열 — 1열 1수종(S-1) · 피치 7.0 m · 방위 = 연석 방위 0°.
    #   `pts` 는 **전 그루의 좌표**여야 한다 — LINT-2 는 선언된 폴리라인의 인접 간격을
    #   그대로 피치로 읽으므로 양 끝점만 적으면 14 m 로 측정된다(H6 설계 시 실측).
    routes={
        "crown_N": dict(pts=[(-25.20, 4.15), (-18.20, 4.15), (-11.20, 4.15)],
                        species="elm", pitch_m=7.0),
        "crown_S": dict(pts=[(-24.40, -5.90), (-17.40, -5.90), (-10.40, -5.90)],
                        species="poplar", pitch_m=7.0),
    },
)


def build_views():
    """카메라 프리셋: grid_views(gy=0, 보행축 +X) + 미장센 4컷."""
    views = sc.grid_views(0.0)
    # berm_over: 둔덕 마루 너머로 점검로·난간·수면이 층을 이루는 사면 컷
    views["berm_over"] = dict(eye=[-9.0, -3.8, 3.9], tgt=[1.2, 0.6, -1.2])
    # walk_axis_low: 보행축 정면 저시점 — **이 씬의 연구 변수**(마루가 낙차를 삼키는가)
    views["walk_axis_low"] = dict(eye=[-7.6, 0.0, 0.60], tgt=[3.0, 0.1, -0.6])
    # rim_face: 점검로 위에서 파라펫·난간·호안·수면을 수직으로 쌓아 스케일을 읽는 컷
    views["rim_face"] = dict(eye=[-2.10, 1.9, 1.62], tgt=[1.5, -0.4, -1.9])
    # crest_walk: 마루 위 보행 시점 — 낙차가 다시 나타나는 지점(H → V 전이 확인)
    views["crest_walk"] = dict(eye=[-4.40, -0.4, 1.72], tgt=[2.6, 0.2, -1.0])
    return views


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. walk_axis_low (h0.60·d7.6)  — 둔덕 마루가 점검로·갓돌·수면을 통째로 삼키는가
 2. crest_walk                  — 마루에 올라서면 낙차가 다시 보이는가 (H → V 전이)
 3. rim_face                    — 파라펫 2.24 m·호안 2단·수면이 하나의 스케일로 읽히는가
 4. berm_over                   — 갈대·난간·표지·고가도로가 마루 위로 층을 이루는가
 5. cue ON vs OFF               — 단서 토글 시 지형·낙차 기하 **불변**인가
 6. 접지·순백                   — 순백(>0.8) 대면적 없음 · 모든 프림 접지 · Z파이팅 없음
 7. props 규율                  — 볼라드 피치 1.50 법정치 · 조형물 0"""


def main():
    # [GT-89] SMOKE 게이트 — Isaac 부팅 **전** 조기 종료 (GPU·GUI 미사용).
    if os.environ.get("NEGOBS_SMOKE", "0") == "1" \
            and os.environ.get("NEGOBS_SMOKE_ASSEMBLE", "0") != "1":
        print("SMOKE_OK %s pre-boot gate (GT-89)" % os.path.basename(__file__))
        ok = _geometry_selfcheck()
        if not ok:
            raise SystemExit("sceneH1 CPU 자기검사 실패")
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
    UsdGeom.Xform.Define(stage, "/World/SceneH1")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    T = PARAMS["terrain"]
    HZ = PARAMS["hazard"]
    ROOT = "/World/SceneH1"
    YH = T["y_half"]

    def BOX(path, center, size, mtl=None, col=False, rotZ=0.0):
        return sc.add_box(stage, path, center, size, mtl, collider=col, rotZ=rotZ)

    def CYL(path, center, r, h, mtl=None, rotY=0.0, rotX=0.0, col=False):
        return sc.add_cylinder(stage, path, center, r, h, mtl,
                               rotY=rotY, rotX=rotX, collider=col)

    def PBR(path, *args, **kwargs):
        return sc.make_pbr(stage, path, *args, **kwargs)

    # [VG-void] 타일 이음매 여유. 인접 슬래브가 **정확히 같은 x** 에서 맞닿으면
    #   `AabbPrefilter` 의 수직 레이가 두 상자의 면을 동시에 스치며 **둘 다 놓치는** 일이
    #   생긴다(sceneH7 스모크에서 계단 이음매 3줄 197셀이 void 로 찍혔다 [측정]).
    #   4 mm 겹침을 주면 겹친 구간에서 **더 높은 상자가 이긴다** — 경계가 4 mm 이동할 뿐이고
    #   높이맵 격자 피치 50 mm 의 1/12 이라 GT 에 영향이 없다.
    SEAM = 0.004

    def SLAB(path, x0, x1, z_top, mtl, y0=None, y1=None, base=None, col=True,
             seam=True):
        """x0..x1 · y0..y1 의 축정렬 지면 슬래브. 상면이 정확히 z_top 에 온다.

        축정렬 박스만 쓰는 이유는 상단 `rise` 주석에 있다 — 회전 박스의 월드 AABB 는
        `AabbPrefilter.ground_z` 를 통째로 틀리게 만들고, 그것이 곧 카메라 배치와 높이맵이다.
        """
        y0 = -YH if y0 is None else y0
        y1 = YH if y1 is None else y1
        base = T["base_z"] if base is None else base
        if seam:
            x0, x1 = x0 - SEAM, x1 + SEAM
        return BOX(path, ((x0 + x1) / 2.0, (y0 + y1) / 2.0, (z_top + base) / 2.0),
                   (x1 - x0, y1 - y0, z_top - base), mtl, col=col)

    # -------------------------------------------------------------------
    # 재질 (3단 규약)
    # -------------------------------------------------------------------
    def setup_materials():
        sca = mp["scale"]
        M = {}
        # 지면·구조물 — 텍스처 3매 (ground 계열)
        M["crown"] = PBR(f"{ROOT}/Looks/ConcretePave",
                         sc.tex_path("concrete_floor", "diff"),
                         sc.tex_path("concrete_floor", "nor"),
                         sc.tex_path("concrete_floor", "rough"),
                         sca["concrete_floor"], tint=mp["crown_tint"])
        M["walk"] = PBR(f"{ROOT}/Looks/PlazaLower",
                        sc.tex_path("plaza_lower", "diff"),
                        sc.tex_path("plaza_lower", "nor"),
                        sc.tex_path("plaza_lower", "rough"),
                        sca["plaza_lower"], tint=mp["walk_tint"])
        M["step"] = PBR(f"{ROOT}/Looks/ConcreteStep",
                        sc.tex_path("concrete_floor", "diff"),
                        sc.tex_path("concrete_floor", "nor"),
                        sc.tex_path("concrete_floor", "rough"),
                        sca["concrete_floor"], tint=mp["step_tint"])
        M["grass"] = PBR(f"{ROOT}/Looks/Grass", sc.tex_path("grass", "diff"),
                         sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
                         sca["grass"], tint=mp["grass_tint"])
        M["gravel"] = PBR(f"{ROOT}/Looks/Gravel", sc.tex_path("gravel", "diff"),
                          sc.tex_path("gravel", "nor"),
                          sc.tex_path("gravel", "rough"),
                          sca["gravel"], tint=mp["bed_tint"])
        M["revet"] = PBR(f"{ROOT}/Looks/ConcreteRevet",
                         sc.tex_path("stone_worn", "diff"),
                         sc.tex_path("stone_worn", "nor"),
                         sc.tex_path("stone_worn", "rough"),
                         sca["stone_worn"], tint=mp["revet_tint"])
        M["coping"] = PBR(f"{ROOT}/Looks/GraniteDark",
                          sc.tex_path("granite_dark", "diff"),
                          sc.tex_path("granite_dark", "nor"),
                          sc.tex_path("granite_dark", "rough"),
                          sca["granite_dark"], tint=mp["coping_tint"])
        M["tactile"] = sc.tactile_pbr(stage, f"{ROOT}/Looks/Tactile",
                                      scale_m=sca["tactile"])
        M["wood"] = PBR(f"{ROOT}/Looks/WoodDark", sc.tex_path("wood_dark", "diff"),
                        sc.tex_path("wood_dark", "nor"),
                        sc.tex_path("wood_dark", "rough"), sca["wood_dark"])
        # 구조물 콘크리트 — 텍스처(look 층이 concrete 클래스로 상한 0.34 를 건다)
        M["wall"] = PBR(f"{ROOT}/Looks/ConcreteWall",
                        sc.tex_path("concrete_wall", "diff"),
                        sc.tex_path("concrete_wall", "nor"),
                        sc.tex_path("concrete_wall", "rough"),
                        sca["concrete_wall"], tint=mp["wall_color"])
        # 금속·도색·수면 = OmniPBR
        M["water"] = PBR(f"{ROOT}/Looks/Water", diffuse_color=mp["water_color"],
                         roughness_const=mp["water_rough"], metallic=0.0)
        # [R1 · 1차 스모크 실측] `Looks/GranitePost` 는 "Post" 토큰 때문에 look 층에서
        #   **metal**(alb_max 0.50 · OmniPBR)로 분류돼 화강석 각기둥이 흰 금속 기둥으로
        #   렌더됐다 — SCENE_H67_BUILD R3(`RailStone` → metal)의 재발이다.
        #   `GraniteColumn` 은 **stone**(alb_max 0.34 · ground MDL)로 떨어지고 석재 계열
        #   텍스처 승격을 탄다 [측정: sc._look_spec 대조표].
        M["post"] = PBR(f"{ROOT}/Looks/GraniteColumn",
                        diffuse_color=mp["post_color"],
                        roughness_const=mp["post_rough"])
        M["bollard"] = PBR(f"{ROOT}/Looks/Bollard",
                           diffuse_color=mp["bollard_color"],
                           metallic=mp["bollard_metallic"],
                           roughness_const=mp["bollard_rough"])
        M["rail"] = PBR(f"{ROOT}/Looks/Rail",
                        diffuse_color=mp["rail_metal_color"],
                        metallic=mp["rail_metal"],
                        roughness_const=mp["rail_metal_rough"])
        M["nosing"] = PBR(f"{ROOT}/Looks/Nosing", diffuse_color=mp["nosing_color"],
                          roughness_const=mp["nosing_rough"])
        M["band"] = PBR(f"{ROOT}/Looks/GuardBand", diffuse_color=mp["band_color"],
                        roughness_const=0.35)
        M["pole"] = PBR(f"{ROOT}/Looks/Pole", diffuse_color=mp["pole_color"],
                        metallic=mp["pole_metallic"],
                        roughness_const=mp["pole_rough"])
        M["lamp"] = PBR(f"{ROOT}/Looks/Lamp", diffuse_color=mp["lamp_color"],
                        roughness_const=mp["lamp_rough"])
        M["iron"] = PBR(f"{ROOT}/Looks/Iron", diffuse_color=mp["iron_color"],
                        metallic=mp["iron_metallic"],
                        roughness_const=mp["iron_rough"])
        M["reed"] = PBR(f"{ROOT}/Looks/Reed", sc.tex_path("grass", "diff"),
                        sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
                        1.1, tint=mp["reed_tint"])
        M["canopy_a"] = PBR(f"{ROOT}/Looks/CanopyA",
                            diffuse_color=mp["canopy_a"],
                            roughness_const=mp["canopy_rough"])
        M["canopy_b"] = PBR(f"{ROOT}/Looks/CanopyB",
                            diffuse_color=mp["canopy_b"],
                            roughness_const=mp["canopy_rough"])
        # `Looks/Bridge` 는 look 층에서 misc(무처방 상수색)로 떨어진다 — `BgConcrete` 로
        #   두면 concrete 클래스가 되어 알베도 상한 0.34 와 텍스처 승격을 받는다(H6 R4).
        M["bridge"] = PBR(f"{ROOT}/Looks/BgConcrete",
                          diffuse_color=mp["bridge_color"],
                          roughness_const=mp["bridge_rough"])
        M["sign"] = PBR(f"{ROOT}/Looks/Sign", sc.tex_path("sign_no_entry", "diff"),
                        uv_mode=True)
        return M

    # -------------------------------------------------------------------
    # ① 경로 + ④ 은닉 — 지형. **hazard_* 밖**. 4팔 전부에서 동일 프림·동일 좌표.
    # -------------------------------------------------------------------
    def build_terrain(M):
        """관리도로 → 성토 둔덕 사면 → **BermCrest** → 콘크리트 4단 → 점검로.

        `cam.ground_z` 가 이 프림들만으로 결정되므로(단서·위험 프림은 데이텀 스트립 밖 또는
        융기 ≤ 12 mm), VG-datum 은 `datum_exact` 로 통과하도록 **구성상** 되어 있다.
        """
        cr, r, c, st, w = (T["crown"], T["rise"], T["crest"], T["steps"], T["walk"])

        # (1) 제방 마루 관리도로 — 큰 면이므로 ground skin(±10 mm 미세기복)이 붙는다
        SLAB(f"{ROOT}/Ground/Crown", cr["x0"], cr["x1"], cr["z"], M["crown"])

        # (2) 성토 둔덕 사면 — **같은 평면 위의 회전 슬래브** (PARAMS 주석)
        #     아래에 z=0 채움 상자를 깔아 사면이 떠 있는 껍데기가 되지 않게 한다.
        #     [개정 R3] 사면을 **3밴드**로 나눈다: 잔디 어깨(S) · **콘크리트 관리 램프**(C) ·
        #     잔디 어깨(N). 제방을 넘는 관리도로의 실제 구성이고, 동시에 스침각 프레임의
        #     정보량을 회복시킨다(R0 실측: 전면 잔디 프레임 발생).
        SLAB(f"{ROOT}/Ground/BermFill", r["x0"], r["x1"], r["z0"], M["grass"])
        n = int(r["n_seg"])
        seg = (r["x1"] - r["x0"]) / n
        d_seg = (r["z1"] - r["z0"]) / n
        pyh = r["pave_y_half"]
        bands = (("S", -YH, -pyh, M["grass"]), ("C", -pyh, pyh, M["crown"]),
                 ("N", pyh, YH, M["grass"]))
        for i in range(n):
            x0 = r["x0"] + i * seg
            for tag, y0, y1, mtl in bands:
                sc.build_slope(stage, f"{ROOT}/Ground/BermRise{tag}_{i:02d}",
                               x0, r["z0"] + i * d_seg, seg, -d_seg,
                               y0, y1, r["thick"], mtl,
                               margin=0.0, collider=True)

        # (3) **BermCrest** — 이 씬의 은닉체(④). CUE_CLASS `_structural` 등재.
        #     어떤 cue_* 도 이 프림을 참조하지 않는다. 마루도 같은 3밴드 구성이며,
        #     **세 프림 모두 `BermCrest` 접두어**라 VG-06 의 가림체 집계는 그대로다.
        for tag, y0, y1, mtl in bands:
            SLAB(f"{ROOT}/BermCrest/{tag}", c["x0"], c["x1"], c["z"], mtl,
                 y0=y0, y1=y1)

        # (4) 콘크리트 4단 — 마루에서 점검로로 내려서는 완경사 계단
        for i in range(st["n"]):
            x0 = st["x0"] + i * st["tread"]
            x1 = x0 + st["tread"]
            z = st["z_top"] - (i + 1) * st["riser"]
            SLAB(f"{ROOT}/Ground/ShoulderStep_{i}", x0, x1, round(z, 4), M["step"])

        # (5) 호안 상단 점검로 — `cue_material_break` 의 유일한 대상(재바인딩 전용)
        walk_mtl = M["walk"] if cfg["cue_material_break"] else M["crown"]
        SLAB(f"{ROOT}/Ground/InspectWalk", w["x0"], w["x1"], w["z"], walk_mtl)
        print(f"[cue] material_break={cfg['cue_material_break']} → InspectWalk "
              f"= {'콘크리트 판석(PlazaLower)' if cfg['cue_material_break'] else '콘크리트 타설(ConcretePave)'}"
              " · **프림 집합 불변**(재질 재바인딩 전용) → 높이맵 비트 동일 보증")

    # -------------------------------------------------------------------
    # ② 위험 — hazard_stairs 전속. 여기에는 **단서가 한 개도 없다**(프림 위생 1).
    # -------------------------------------------------------------------
    def build_hazard(M):
        cp, wl = HZ["coping"], HZ["wall"]
        sc.skin_exclude(f"{ROOT}/RetainWall", f"{ROOT}/Revet", f"{ROOT}/Water")
        # 파라펫 몸체 (콘크리트) — 상면은 갓돌 밑면
        BOX(f"{ROOT}/RetainWall/Body",
            ((wl["x0"] + wl["x1"]) / 2.0, 0.0, (wl["z_top"] + wl["z_bot"]) / 2.0),
            (wl["x1"] - wl["x0"], 2 * YH, wl["z_top"] - wl["z_bot"]),
            M["wall"], col=True)
        # 화강석 갓돌 — 상면 z 가 점검로와 **정확히 같다**(0.62). 단차 0.
        BOX(f"{ROOT}/RetainWall/Coping",
            ((cp["x0"] + cp["x1"]) / 2.0, 0.0, cp["z_top"] - cp["thick"] / 2.0),
            (cp["x1"] - cp["x0"], 2 * YH, cp["thick"]), M["coping"], col=True)
        # 계단식 콘크리트 호안 2단 — 축정렬. (회전 사면은 AABB 를 평면으로 만든다)
        #   x 양단에 4 mm 이음매 여유 — 위 SEAM 주석과 같은 이유.
        for i, t in enumerate(HZ["revet"]):
            x0, x1 = t["x0"] - SEAM, t["x1"] + SEAM
            BOX(f"{ROOT}/Revet/T{i}",
                ((x0 + x1) / 2.0, 0.0, (t["z_top"] + HZ["revet_base"]) / 2.0),
                (x1 - x0, 2 * YH, t["z_top"] - HZ["revet_base"]),
                M["revet"], col=True)
        # 자갈 여울(하상) — VG-void: 낙차 발자국 전역에 **실제 바닥 프림**. 개방 바닥 0.
        bd = HZ["bed"]
        BOX(f"{ROOT}/Bed/Gravel",
            ((bd["x0"] - SEAM + bd["x1"]) / 2.0, 0.0,
             (bd["z"] + HZ["revet_base"]) / 2.0),
            (bd["x1"] - bd["x0"] + SEAM, 2 * YH + 3.0, bd["z"] - HZ["revet_base"]),
            M["gravel"], col=True)
        # 저수로 수면 — 자갈 여울 위에 얹힌 얇은 판
        wt = HZ["water"]
        BOX(f"{ROOT}/Water/Surface",
            ((wt["x0"] + wt["x1"]) / 2.0, 0.0, wt["z"] - wt["thick"] / 2.0),
            (wt["x1"] - wt["x0"], 2 * YH + 3.0, wt["thick"]), M["water"])
        fb = HZ["farbank"]
        # 대안(對岸) — 높이맵 격자 동단 x=14.0 **밖**(x ≥ 26)이라 라벨과 무관하다.
        #   수평 폐합용 지형이며 이 씬의 GT 에 한 칸도 기여하지 않는다.
        BOX(f"{ROOT}/FarBank/Bank",
            ((fb["x0"] + fb["x1"]) / 2.0, 0.0, (fb["z"] + fb["base_z"]) / 2.0),
            (fb["x1"] - fb["x0"], 66.0, fb["z"] - fb["base_z"]), M["grass"])
        BOX(f"{ROOT}/FarBank/Revetment",
            (fb["x0"] - 0.9, 0.0, (fb["z"] - 1.6)),
            (1.8, 66.0, 3.6), M["revet"])
        print(f"[hazard] 낙차 = {cp['z_top'] - wt['z']:.3f} m "
              f"(갓돌 {cp['z_top']:+.2f} → 수면 {wt['z']:+.2f}) · "
              f"파라펫 노출면 {cp['z_top'] - HZ['revet'][0]['z_top']:.3f} m")

    def build_flat_fill(M):
        """hazard_stairs=False 대조군 — 점검로 레벨의 평탄 지면이 낙차 발자국을 채운다.

        이것이 라벨러의 **반사실 보행 가능면 z_off** 다(footprint v2 = z_off − z_on ≥ 0.3).
        채움면의 z 는 점검로와 **같은 0.62** 여야 발자국이 파라펫 낙차 전체가 된다.
        """
        f = HZ["fill"]
        sc.skin_exclude(f"{ROOT}/FlatFill/Far")
        SLAB(f"{ROOT}/FlatFill/Near", f["x0"], 14.5, f["z"], M["crown"],
             base=f["base_z"])
        SLAB(f"{ROOT}/FlatFill/Far", 14.5, f["x1"], f["z"], M["grass"],
             y0=-33.0, y1=33.0, base=f["base_z"])
        print(f"[hazard] OFF — 반사실 보행 가능면 z_off = {f['z']:+.3f} "
              f"(x {f['x0']:+.2f} … {f['x1']:+.1f})")

    # -------------------------------------------------------------------
    # ③ 단서 — **전부 hazard_* 밖의 자립 프림**. 전부 x ≤ −0.62.
    # -------------------------------------------------------------------
    def build_railing(M):
        """화강석 **각기둥** 난간 + 스테인리스 **3단** 횡대 (H6 의 원형 2단과 다른 형식)."""
        r = PARAMS["rail"]
        n = int(math.floor(2 * r["y_half"] / r["post_pitch"])) + 1
        y0 = -r["y_half"]
        zw = T["walk"]["z"]
        for i in range(n):
            # 각기둥은 **정렬해 세운다** — 석재 난간의 실제 시공이 그러하고,
            #   J-3/J-5(07-30)가 배치 지터를 폐지했다(LINT-10 정적 검사 대상).
            y = y0 + i * r["post_pitch"]
            BOX(f"{ROOT}/Rail/Post_{i:02d}",
                (r["x"], y, zw + r["post_h"] / 2.0),
                (r["post_a"], r["post_a"], r["post_h"]), M["post"])
            BOX(f"{ROOT}/Rail/PostCap_{i:02d}",
                (r["x"], y, zw + r["post_h"] + r["cap_t"] / 2.0),
                (r["post_a"] + 0.04, r["post_a"] + 0.04, r["cap_t"]), M["coping"])
        for tag, z in (("Top", r["top_z"]), ("Mid", r["mid_z"]),
                       ("Low", r["low_z"])):
            CYL(f"{ROOT}/Rail/{tag}Rail", (r["x"], 0.0, z), r["rail_r"],
                2 * r["y_half"] + 0.4, M["rail"], rotX=90.0)
        print(f"[cue] railing ON — 화강석 각기둥 {n}본(피치 {r['post_pitch']} m) "
              f"· 3단 횡대 · 가드선 {r['top_z']:.2f} m "
              f"(유효높이 {r['top_z'] - zw:.2f} m ≥ 1.10 규정) "
              "[규격 도로안전시설 지침 2.3.3 나 — 110 cm 표준 · 제방 난간 조문 부재]")

    def build_tactile(M):
        # [개정 R4 · D82ⓐ] **점형블록은 1밴드뿐**이다 — 마루 위 계단 상단, 포장 밴드 위에만.
        #   갓돌 앞 밴드(구 `Tactile`)는 출입금지 점검로의 과잉 설치라 삭제했다(PARAMS ⓐ).
        ct = PARAMS["crest_tactile"]
        pyh = T["rise"]["pave_y_half"]
        sc.build_tactile(stage, f"{ROOT}/TactileCrest", ct["x0"], ct["x1"],
                         -pyh, pyh, M["tactile"],
                         z=T["crest"]["z"], proud=ct["proud"])
        print(f"[cue] tactile ON — **계단 상단 점형블록 1밴드** 세로 "
              f"{ct['x1'] - ct['x0']:.2f} m (KS F 4561 블록 1장) · 마루 코에서 "
              f"{T['crest']['x1'] - ct['x1']:.2f} m 이격 · 폭 {2 * pyh:.2f} m "
              f"(포장 밴드 전폭) · proud {ct['proud']} m "
              "[규격 교통약자법 시행규칙 별표2 · KS F 4561]")

    def build_nosing(M):
        """콘크리트 4단의 논슬립 나이징 띠. 낙차 부재가 아니라 **계단 코 처리**다.

        **전부 낙차 발자국 밖**(x ≤ −2.44 ≪ −0.20)이므로 이 키를 끄는 B팔에서도
        낙차 발자국의 높이맵은 한 칸도 움직이지 않는다(VG-01 의 실효 조건).
        """
        st, ng = T["steps"], PARAMS["nosing"]
        for i in range(st["n"]):
            x1 = st["x0"] + (i + 1) * st["tread"]
            z = st["z_top"] - (i + 1) * st["riser"]
            BOX(f"{ROOT}/Nosing/Strip_{i}",
                (x1 - ng["width"] / 2.0, 0.0, z + ng["proud"] / 2.0),
                (ng["width"], 2 * YH, ng["proud"]), M["nosing"])
        print(f"[cue] nosing ON — {st['n']}단 · 폭 {ng['width']} m · "
              f"proud {ng['proud'] * 1000:.0f} mm [계획 realism_v1_final §84] · "
              "발자국 밖")

    def build_sign(M):
        """하천 점검로 출입 제한 표지 1매 — 법2(임의 경고판 금지): 법정 제식 판만."""
        s = PARAMS["sign"]
        sc.build_sign(stage, f"{ROOT}/Sign", s["x"], s["y"],
                      _ground_z_ref(s["x"]), s["yaw"], M["sign"],
                      w=s["w"], h=s["h"], pole_h=s["pole_h"],
                      pole_mtl=M["pole"], back_mtl=M["iron"])
        print(f"[cue] sign ON — 관계자외 출입금지 표지 1매 "
              f"@({s['x']:+.2f},{s['y']:+.2f}) · 임의 문구 0 (법2)")

    def build_bollards(M):
        """제방 진입 차량 억제 볼라드 열. 보차도 경계선 위 · 피치 1.50 m 법정치."""
        b = PARAMS["bollard"]
        for i, x0 in enumerate(b["xs"]):
            x, y = x0, b["y"]
            gz = _ground_z_ref(x)
            # 프림 명명은 `placement_lint` 의 `props.bollard` 규약을 따른다 —
            #   인스턴스 세그먼트 `Bollard_NN` + 하중 실린더 `/Post` + 무시 접미 `/Band`.
            CYL(f"{ROOT}/Bollard_{i:02d}/Post", (x, y, gz + b["h"] / 2.0),
                b["r"], b["h"], M["bollard"])
            CYL(f"{ROOT}/Bollard_{i:02d}/Band", (x, y, gz + b["band_z"]),
                b["r"] + 0.004, b["band_t"], M["band"])
        print(f"[cue] bollard ON — {len(b['xs'])}본 · h {b['h']} m · "
              f"φ{2 * b['r']:.2f} m · 피치 1.50 m · y {b['y']:+.2f} (보차도 경계) "
              "· 반사띠 [규격 교통약자법 시행규칙 별표2 제7호]")

    def build_delineators(M):
        """반사 시선유도봉 — 관리도로 진입부 차량 억제 보조. 기본 OFF(법4)."""
        d = PARAMS["delineator"]
        for i, y in enumerate(d["ys"]):
            gz = _ground_z_ref(d["x"])
            CYL(f"{ROOT}/Delineator/D_{i}", (d["x"], y, gz + d["h"] / 2.0),
                d["r"], d["h"], M["band"])
            CYL(f"{ROOT}/Delineator/Band_{i}", (d["x"], y, gz + d["h"] - 0.16),
                d["r"] + 0.003, 0.08, M["lamp"])
        print(f"[cue] delineator ON — {len(d['ys'])}본")

    def build_ground_kit(M):
        """지면 문양 3키 (`cue_manhole`·`cue_tree_grate`·`cue_slab_joint`) + `cue_drainage`.

        전부 **flush**(융기 ≤ 8 mm · 줄눈은 recess 3 mm)이므로 법7(기하 불변)을 지킨다.
        함몰 채널은 hazard 기하이지 `cue_*` 가 아니라는 것이 `cue_drainage` 승격의
        전제 조건이었다(FA_REALITY §2 3위) — 여기서는 **복개 U형 측구**(뚜껑 flush)로 조달한다.
        """
        g = PARAMS["gkit"]
        M2 = dict(M)
        M2.update(joint=M["coping"], crack=M["coping"], manhole=M["iron"],
                  gully=M["iron"], gutter=M["coping"], gutter_cover=M["iron"],
                  trench=M["iron"], trench_frame=M["iron"], marking=M["lamp"],
                  weed=M["grass"], wear=M["gravel"], stain_dirt=M["gravel"],
                  stain_water=M["gravel"], tree_grate=M["iron"], grate=M["iron"],
                  patch=M["crown"], patch_cut=M["coping"])
        kit = gk.kit_from_scene_common(sc, stage)
        n_prims = 0

        # (a) 제방 마루 관리도로 — 맨홀 · 빗물받이 · U형 측구 · 수축줄눈
        infra = dict(manhole=len(g["manholes"]) if cfg["cue_manhole"] else 0,
                     gully=len(g["gullies"]) if cfg["cue_drainage"] else 0,
                     gutter_U=1 if cfg["cue_drainage"] else 0,
                     trench=0)
        sites = dict()
        if cfg["cue_manhole"]:
            sites["manhole"] = [tuple(v) for v in g["manholes"]]
        if cfg["cue_drainage"]:
            sites["gully"] = [tuple(v) for v in g["gullies"]]
            sites["gutter_U"] = [g["gutter_y"]]
        gp = gk.plan_ground(
            "alley_concrete", region=tuple(g["crown_region"]), z=T["crown"]["z"],
            gy=0.0, origin=(0.0, 0.0, 0.0),
            edges=[("levee_rim", HZ["coping"]["x0"])],
            dists=(2, 5, 10), scene="sceneH1", tactile=(),
            # `surface=None` — 잡초/균열/오염 데칼을 끈다. 법1(손상·노후·방치 표현 금지)이
            #   1차 이유이고, 잡초 프림이 proud 0.10 m 까지 자라 카메라 데이텀 스트립을
            #   `datum_fail` 로 밀 수 있다는 것이 2차 이유다.
            overrides=dict(infra=infra, surface=None),
            sites=sites, seed=61)
        if not cfg["cue_slab_joint"]:
            gp["ops"] = [o for o in gp["ops"] if o["name"] != "joints"]
            gp["elements"] = [e for e in gp["elements"] if e["kind"] != "joint"]
        res = gk.apply_ground(kit, f"{ROOT}/GKitCrown", gp, M2,
                              skin_exclude=sc.skin_exclude,
                              scatter=sc.scatter_debris)
        n_prims += res["prims"]

        # (b) 호안 상단 점검로 — 수축줄눈만(도시 인프라 0). 폭 1.79 m 안에 횡줄눈이 하나는
        #     들어오도록 `step_x` 를 1.6 으로 줄인다(= unit_cell 0.2 × 8, U2 게이트).
        infra2 = dict(manhole=0, gully=0, gutter_U=0, trench=0)
        gp2 = gk.plan_ground(
            "verge_rural", region=tuple(g["walk_region"]), z=T["walk"]["z"],
            gy=0.0, origin=(0.0, 0.0, 0.0),
            edges=[("levee_rim", HZ["coping"]["x0"])],
            dists=(2, 5, 10), scene="sceneH1", tactile=(),
            overrides=dict(infra=infra2, surface=None,
                           pave=dict(step_x=g["walk_step_x"])),
            seed=62)
        if not cfg["cue_slab_joint"]:
            gp2["ops"] = [o for o in gp2["ops"] if o["name"] != "joints"]
            gp2["elements"] = [e for e in gp2["elements"] if e["kind"] != "joint"]
        res2 = gk.apply_ground(kit, f"{ROOT}/GKitWalk", gp2, M2,
                               skin_exclude=sc.skin_exclude,
                               scatter=sc.scatter_debris)
        n_prims += res2["prims"]

        # (b') [개정 R3] 관리 램프 횡단 수축줄눈 — `plan_ground` 는 **평면 프로파일**이라
        #      경사면을 다룰 수 없다. 사면 각도를 그대로 따르는 얇은 회전 슬래브로 직접 짓는다.
        n_rj = 0
        if cfg["cue_slab_joint"]:
            r = T["rise"]
            slope = (r["z1"] - r["z0"]) / (r["x1"] - r["x0"])
            w = g["ramp_joint_w"]
            for i, jx in enumerate(g["ramp_joints"]):
                z0 = _profile_z(jx) + 0.002
                sc.build_slope(stage, f"{ROOT}/GKitRamp/Joint_{i}",
                               jx, z0, w, -slope * w,
                               -r["pave_y_half"], r["pave_y_half"], 0.03,
                               M["coping"], margin=0.0, collider=False)
                n_rj += 1

        # (c) 수목보호격자 — 빌더가 없으므로 flush 격자를 직접 짓는다(FA_REALITY 갭 2위 = 전무)
        n_grate = 0
        if cfg["cue_tree_grate"]:
            for i, (gx, gy_) in enumerate(g["tree_grates"]):
                n_grate += _tree_grate(M, f"{ROOT}/TreeGrate_{i}", gx, gy_,
                                       T["crown"]["z"])
        print(f"[cue] ground pattern — manhole={cfg['cue_manhole']}({len(g['manholes'])}) "
              f"tree_grate={cfg['cue_tree_grate']}({n_grate} 프림) "
              f"slab_joint={cfg['cue_slab_joint']}(램프 줄눈 {n_rj}줄) "
              f"drainage={cfg['cue_drainage']} "
              f"· gkit 프림 {n_prims} · δmax "
              f"{max(res['gt_delta_max'], res2['gt_delta_max']):.4f} m (flush — 법7)")
        return n_prims + n_grate + n_rj

    def _tree_grate(M, path, cx, cy, z, side=1.44, frame=0.09, bar=0.035,
                    n_bar=9, proud=0.004):
        """수목보호덮개 (flush) — 사각 프레임 + 평행 바 격자. 단차 4 mm.

        [FA_REALITY §2 2위] 33씬 **전무**였던 지면 문양. 리세스형(함몰)은 hazard 로 분리하고
        여기서는 **flush 한정**(법7). 어두운 폐영역 + 평행 밴드라는 낙차의 저역 문법을 갖는다.
        """
        n = 0
        h = 0.05
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
        """그림자 밴드 캐스터 — 미루나무 열 + 가로등주 (v3 신설 `cue_shadow_caster`).

        **양성 씬에도 동일 비율로 배치한다**(RENDER_PLAN_V3 §2.0 부작용 경보). 음성 씬 전용이면
        "그림자 = 안전"이라는 역지름길이 생긴다.
        배치 규칙: 시선 통로 |y| ≤ 3.8 · x ∈ [−12, 0] 은 **비워 둔다** — 수목이 낙차를 가리면
        VG-06 의 모서리 소유가 둔덕에서 수목으로 넘어가 이 씬의 은닉 계열 주장이 깨진다.
        """
        s = PARAMS["shadow"]
        for i, (tx, ty) in enumerate(s["poplars"]):
            gz = _ground_z_ref(tx)
            sc.build_tree(stage, f"{ROOT}/Shadow/Poplar_{i}", tx, ty, gz,
                          M["wood"], M["canopy_a"], M["canopy_b"],
                          trunk_r=0.16, trunk_h=s["poplar_h"] * 0.55,
                          canopy_blobs=11, canopy_spread=1.20,
                          species="poplar")
        for i, (lx, ly) in enumerate(s["lamps"]):
            gz = _ground_z_ref(lx)
            CYL(f"{ROOT}/Shadow/LampPole_{i}", (lx, ly, gz + s["lamp_h"] / 2.0),
                0.072, s["lamp_h"], M["pole"])
            arm_y = ly - math.copysign(s["lamp_arm"] / 2.0, ly)
            CYL(f"{ROOT}/Shadow/LampArm_{i}", (lx, arm_y, gz + s["lamp_h"]),
                0.05, s["lamp_arm"], M["pole"], rotX=90.0)
            BOX(f"{ROOT}/Shadow/LampHead_{i}",
                (lx, ly - math.copysign(s["lamp_arm"], ly), gz + s["lamp_h"] - 0.09),
                (0.44, 0.20, 0.13), M["lamp"])
        print(f"[cue] shadow_caster ON — 미루나무 {len(s['poplars'])}주 + "
              f"가로등 {len(s['lamps'])}주 · 시선 통로(|y|≤3.8) 청소됨")

    def build_dressing(M):
        """③ 단서의 환경 성분 — 갈대 군락 · 벤치 · 가로수 · 관목 띠 · 원경 고가도로/대안.

        *"주변 환경은 장식이 아니라 단서 ③ 그 자체다"*. 갈대 군락은 낙차 이면(수변) 환경
        신호이고, 원경 고가도로 실루엣은 수평 폐합이다(순백 대면적 금지 → 알베도 0.26).
        """
        d = PARAMS["dress"]
        # 갈대 군락 — 점검로 배후, 시선 통로 밖(|y| ≥ 4.5)
        for i, (x0, y0, x1, y1) in enumerate(d["reed_bands"]):
            sc.build_hedge(stage, f"{ROOT}/Dress/Reed_{i}", x0, y0, x1, y1,
                           d["reed_h"], mtl=M["reed"], base_z=T["walk"]["z"],
                           rounded=True, crown_max=40)
        # 관목 띠 — 둔덕 사면 하단
        for i, (x0, y0, x1, y1) in enumerate(d["hedge"]):
            sc.place_hedge_row(stage, f"{ROOT}/Dress/Hedge_{i}", x0, y0, x1, y1,
                               0.85, seed=1610 + i, base_z=_ground_z_ref(x0),
                               fallback_mtl=M["reed"])
        # 벤치 — 관리도로변
        for i, (bx, by, byaw) in enumerate(d["benches"]):
            sc.build_bench(stage, f"{ROOT}/Dress/Bench_{i}", bx, by,
                           _ground_z_ref(bx), M["wood"], yaw=byaw)
        # 가로수 — 관리도로(수목보호격자와 같은 좌표)
        for i, (tx, ty) in enumerate(d["trees"]):
            sc.build_tree(stage, f"{ROOT}/Dress/Tree_{i}", tx, ty,
                          _ground_z_ref(tx), M["wood"], M["canopy_a"],
                          M["canopy_b"], trunk_r=0.13,
                          trunk_h=d["tree_h"] * 0.5, canopy_blobs=10,
                          canopy_spread=1.1, species="elm")
        # 원경 — 강변 고가도로 + 대안 방풍림 + 배수펌프장 (placebo_remove 의 대상 물량군)
        if not PLACEBO_REMOVE:
            br = d["viaduct"]
            yl = 2.0 * br["y_half"]
            BOX(f"{ROOT}/Dress/ViaductDeck",
                ((br["x0"] + br["x1"]) / 2.0, 0.0, br["z"] + br["thick"] / 2.0),
                (br["x1"] - br["x0"], yl, br["thick"]), M["bridge"])
            BOX(f"{ROOT}/Dress/ViaductBarrier",
                (br["x0"] + 0.10, 0.0, br["z"] + br["thick"] + 0.45),
                (0.30, yl, 0.90), M["bridge"])
            for i, (px, py) in enumerate(br["piers"]):
                BOX(f"{ROOT}/Dress/ViaductPier_{i}",
                    (px, py, (br["z"] + 0.70) / 2.0),
                    (br["pier_w"], br["pier_w"] * 1.6, br["z"] - 0.70), M["bridge"])
            for i, (tx, ty) in enumerate(d["far_treeline"]):
                sc.build_tree(stage, f"{ROOT}/Dress/FarTree_{i}", tx, ty, 0.70,
                              M["wood"], M["canopy_a"], M["canopy_b"],
                              trunk_r=0.20, trunk_h=4.6, canopy_blobs=9,
                              canopy_spread=1.5, species="poplar", belt=True)
            for tag, x0, x1, y0, y1, hgt in d["pumphouse"]:
                BOX(f"{ROOT}/Dress/Pump_{tag}",
                    ((x0 + x1) / 2.0, (y0 + y1) / 2.0, hgt / 2.0 + 0.70),
                    (x1 - x0, y1 - y0, hgt), M["bridge"])
        else:
            print("[placebo] 원경 고가도로·방풍림·펌프장 물량군 제거 — "
                  "위험·단서는 전부 유지(D35 P팔)")
        print(f"[cue] scene_dressing ON — 갈대 {len(d['reed_bands'])}띠 · "
              f"벤치 {len(d['benches'])} · 가로수 {len(d['trees'])} · "
              f"관목 {len(d['hedge'])}띠 · 원경 "
              f"{'0 (placebo)' if PLACEBO_REMOVE else '고가도로 1 + 방풍림 7 + 펌프장 1'}")

    def _ground_z_ref(x):
        """지형 종단면의 해석적 z(x). 배치 전용(높이맵은 AABB 가 따로 측정한다)."""
        return _profile_z(x)

    # -------------------------------------------------------------------
    # 자기검사 — 조립 직후, 렌더 전
    # -------------------------------------------------------------------
    def datum_selfcheck():
        """VG-datum 사전검사 · 프림 위생 검사 · VG-void 발자국 검사 · 은닉 기하 재계산.

        (1) `GATED_ZONES` 의 어떤 토글 구역도 카메라 데이텀 스트립과 `datum_fail` 로 겹치지 않을 것
        (2) 스테이지 전수 AABB 로 (1) 을 재확인 — 손이 표를 빠뜨려도 기계가 잡는다
        (3) 낙차 발자국 x ∈ [rim, 14.0] 에 바닥 프림이 빈틈없이 있을 것 (VG-void (b))
        (4) 단서 프림이 낙차 발자국 위에 0개일 것 (VG-01 실효 조건)
        (5) 은닉 기하·수율 재계산 — 종단면을 만지면 즉시 드러난다
        """
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
        print(f"[selfcheck] (1) 데이텀 스트립 x[{ds['x0']}, {ds['x1']}] "
              f"y[{ds['y0']}, {ds['y1']}] × 토글구역 {len(GATED_ZONES)}건 → "
              f"datum_exact {len(GATED_ZONES) - len(cross)} · "
              f"datum_tol {len(tol)} {[(t[0], t[6]) for t in tol]} · "
              f"datum_fail {len(fail)} {[f[0] for f in fail]}"
              + ("" if fail else " · OK"))

        # (2) 기계 재확인 — 이 팔에서 실제로 존재하는 토글 프림의 월드 AABB
        bbc = UsdGeom.BBoxCache(Usd.TimeCode.Default(),
                                [UsdGeom.Tokens.default_, UsdGeom.Tokens.render])
        gated_roots = ("/Rail", "/Tactile", "/Nosing", "/Sign", "/Bollard",
                       "/Delineator", "/GKitCrown", "/GKitWalk", "/GKitRamp",
                       "/TreeGrate", "/Shadow", "/Dress", "/RetainWall",
                       "/Revet", "/Bed", "/Water", "/FarBank", "/FlatFill")
        hits, tol_hits = [], []
        n_scan = 0
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

        # (3) VG-void — 발자국 전역 바닥 커버리지 (해석적 종단면 검사)
        rim = HZ["coping"]["x1"]
        if cfg["hazard_stairs"]:
            segs = [(rim, HZ["revet"][0]["x1"]),
                    (HZ["revet"][0]["x1"], HZ["revet"][1]["x1"]),
                    (HZ["bed"]["x0"], 14.0)]
        else:
            segs = [(HZ["fill"]["x0"], 14.0)]
        cover_hi = rim if cfg["hazard_stairs"] else HZ["fill"]["x0"]
        gap = []
        for s0, s1 in sorted(segs):
            if s0 > cover_hi + 1e-6:
                gap.append((cover_hi, s0))
            cover_hi = max(cover_hi, s1)
        if cover_hi < 14.0 - 1e-6:
            gap.append((cover_hi, 14.0))
        if gap:
            ok = False
        print(f"[selfcheck] (3) VG-void 발자국 커버리지 x[{rim:+.2f}, 14.00] "
              f"y[±{YH:.1f}] → 공백 {len(gap)}구간"
              + (f" {gap}" if gap else " · 커버리지 1.0 · OK"))

        # (4) 단서 프림 × 낙차 발자국 교차 0
        cue_roots = ("/Rail", "/Tactile", "/Nosing", "/Sign", "/Bollard",
                     "/Delineator", "/GKitCrown", "/GKitWalk", "/GKitRamp",
                     "/TreeGrate", "/Shadow", "/Dress")
        fp_x0 = HZ["coping"]["x1"]
        over = []
        for prim in stage.Traverse():
            p = str(prim.GetPath())
            if not p.startswith(ROOT) or not prim.IsA(UsdGeom.Gprim):
                continue
            tail = p[len(ROOT):]
            if not any(tail.startswith(g) for g in cue_roots):
                continue
            if tail.startswith("/Dress/Viaduct") or tail.startswith("/Dress/FarTree") \
                    or tail.startswith("/Dress/Pump"):
                continue                     # 원경(x ≥ 16.6) — 높이맵 격자 밖
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
        print(f"[selfcheck] (4) 단서 프림 × 발자국(x ≥ {fp_x0:+.2f}) 교차 "
              f"{len(over)}건" + (f" {over[:6]}" if over else " · OK "
                                  "→ `cells_raw`·`polar_gt` 는 cue_* 에 구성상 불변"))

        # (5) 은닉 기하 재계산
        cx, cz, s_int, s_rim = _crest_slope()
        print(f"[selfcheck] (5) 은닉 기하 — 마루 모서리 ({cx:+.2f}, {cz:.2f}) · "
              f"내부 은닉 s ≥ {s_int:+.4f} · 림 은닉 s ≥ {s_rim:+.4f} "
              f"· 실효 구속 = {'림' if abs(s_rim) < abs(s_int) else '내부'}")
        for dd in (6.0, 7.0, 9.0, 12.0):
            hmax = _h_max(dd)
            print(f"              d={dd:5.1f}  z(-d)={_profile_z(-dd):.3f}  "
                  f"h_max={hmax:.3f}  H밴드[0.25,1.0] 통과율 "
                  f"{min(1.0, max(0.0, (hmax - 0.25) / 0.75)):.2f}")

        print(f"[selfcheck] sceneH1 {'통과' if ok else '실패'}")
        return ok

    # -------------------------------------------------------------------
    # 조립
    # -------------------------------------------------------------------
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()

    build_terrain(M)                                   # ① 경로 + ④ 은닉 (팔 불변)
    if cfg["hazard_stairs"]:                           # ② 위험 — 조립부 hazard 분기 2줄
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
        #   이 씬의 장식은 전부 z ≥ 0 의 상부 지면(관리도로·점검로)에 앵커되므로 채움면 위에
        #   그대로 선다 — sceneC2 가 겪은 "하부 앵커 드레싱이 사라지며 ground_z 가 움직인"
        #   사고가 **구조적으로 불가능**하다(GATED_ZONES 의 Dress 행이 데이텀과 교차 0).
        build_dressing(M)

    if not datum_selfcheck():
        raise SystemExit("sceneH1 self-check 실패")

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    if smoke_mode:
        n = sum(1 for _ in stage.Traverse())
        print(f"[SMOKE] sceneH1 조립 완료 · 프림 {n}개 · 조기 종료")
        simulation_app.close()
        return

    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    _v0 = build_views()["berm_over"]
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
            fp = os.path.join(LOOKCHECK_DIR, f"sceneH1_{ts}.png")
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
def _profile_z(x):
    """상부 지형 종단면 z(x) (x ≤ 점검로 동단)."""
    T = PARAMS["terrain"]
    cr, r, c, st, w = (T["crown"], T["rise"], T["crest"], T["steps"], T["walk"])
    if x <= r["x0"]:
        return cr["z"]
    if x <= r["x1"]:
        f = (x - r["x0"]) / (r["x1"] - r["x0"])
        return r["z0"] + (r["z1"] - r["z0"]) * f
    if x <= c["x1"]:
        return c["z"]
    if x < st["x0"] + st["n"] * st["tread"]:
        i = min(st["n"] - 1, max(0, int((x - st["x0"]) / st["tread"])))
        return st["z_top"] - (i + 1) * st["riser"]
    return w["z"]


def _crest_slope():
    """(마루 모서리 x, z, 내부 은닉 임계 기울기 s_int, 림 은닉 임계 기울기 s_rim).

    s_rim : 마루 모서리를 스치는 시선이 **낙차 림**(파라펫 갓돌 상면)에 닿는 기울기.
            **SCENE_H67_BUILD §2.2 가 확정한 실효 구속** — 갓돌 상면은 깊이 불연속이
            커서 라벨러의 3×3 깊이 창(RIM_TOL 0.35 m)에 먹히지 않는다.
    s_int : 같은 시선이 **높이맵 격자 동단 x = 14.0** 의 수면에 닿는 기울기(상한 모형).
    """
    T, HZ = PARAMS["terrain"], PARAMS["hazard"]
    cx, cz = T["crest"]["x1"], T["crest"]["z"]
    s_int = (HZ["water"]["z"] - cz) / (14.0 - cx)
    s_rim = (T["walk"]["z"] - cz) / (HZ["coping"]["x1"] - cx)
    return cx, cz, s_int, s_rim


def _h_max(d, crit="rim"):
    """거리 d 에서 strict-H 가 성립하는 카메라 높이 상한 h_rel [m].

        L = d + cx   (카메라 x = −d 에서 마루 모서리 x = cx 까지의 수평거리, cx < 0)
        s = (cz − z(−d) − h) / L  ≥ s_crit   ⇔   h ≤ cz − z(−d) − s_crit·L

    `crit="rim"`(기본) = 실효 구속 · `crit="int"` = 내부 조건(상한 모형).
    L ≤ 0 이면 카메라가 마루를 이미 지났다는 뜻이므로 은닉은 성립하지 않는다(−inf).
    """
    cx, cz, s_int, s_rim = _crest_slope()
    L = d + cx
    if L <= 1e-6:
        return float("-inf")
    return cz - _profile_z(-d) - (s_rim if crit == "rim" else s_int) * L


def _band_yield(d_lo, d_hi, h_lo, h_hi, n=1200, crit="rim"):
    """d ~ LogU[d_lo, d_hi] · h ~ U[h_lo, h_hi] 에서 strict-H 가 되는 프레임 비율."""
    tot = 0.0
    lo, hi = math.log(d_lo), math.log(d_hi)
    for i in range(n):
        d = math.exp(lo + (hi - lo) * (i + 0.5) / n)
        hm = _h_max(d, crit)
        tot += min(1.0, max(0.0, (hm - h_lo) / (h_hi - h_lo)))
    return tot / n


def _geometry_selfcheck():
    """부팅 전 스모크가 부르는 CPU 검사. 종단면 연속성 · 낙차 · 은닉 기하 · 데이텀 · 16키."""
    T, HZ = PARAMS["terrain"], PARAMS["hazard"]
    ok = True

    def chk(tag, cond, msg=""):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  [{'PASS' if cond else 'FAIL'}] {tag}" + (f" — {msg}" if msg else ""))

    print("=" * 70)
    print("sceneH1_berm_levee — CPU 자기검사 (pxr·GPU 불필요)")
    print("=" * 70)

    # 종단면 연속성: 0.05 m(= 높이맵 격자 피치) 간격의 인접 표고차가 계단 라이즈를
    #   넘지 않을 것. 넘으면 보행 불가능한 단차이거나 미신고 낙차다.
    prev, worst, worst_x = None, 0.0, None
    x = -12.0
    while x <= -0.66 + 1e-9:
        z = _profile_z(x)
        if prev is not None and abs(z - prev) > worst:
            worst, worst_x = abs(z - prev), x
        prev = z
        x = round(x + 0.05, 4)
    chk("종단면 연속 (0.05 m 격자)", worst <= T["steps"]["riser"] + 1e-6,
        f"최대 단차 {worst:.4f} m @x={worst_x} ≤ 라이즈 {T['steps']['riser']:.4f}")

    drop = HZ["coping"]["z_top"] - HZ["water"]["z"]
    chk("낙차 2.5–3.0 m [브리프 §2.1]", 2.5 <= drop <= 3.0, f"{drop:.3f} m")
    chk("점검로 = 갓돌 상면 동일 z",
        abs(T["walk"]["z"] - HZ["coping"]["z_top"]) < 1e-9,
        f"walk {T['walk']['z']} · coping {HZ['coping']['z_top']}")
    chk("반사실 채움면 = 점검로 레벨",
        abs(HZ["fill"]["z"] - T["walk"]["z"]) < 1e-9, f"{HZ['fill']['z']}")

    fp_x0 = HZ["coping"]["x1"]
    chk("발자국 근단이 d=12 폴라 격자(반경 12 m) 안", 12.0 + fp_x0 < 12.0,
        f"근단 x={fp_x0:+.2f} → d=12 에서 거리 {12.0 + fp_x0:.2f} m < 12.0")

    cx, cz, s_int, s_rim = _crest_slope()
    chk("실효 구속 = 림 조건 (SCENE_H67_BUILD §2.2)", abs(s_rim) < abs(s_int),
        f"|s_rim| {abs(s_rim):.4f} < |s_int| {abs(s_int):.4f}")
    print(f"  [info] 마루 모서리 ({cx:+.2f}, {cz:.2f}) · 내부 은닉 s ≥ {s_int:+.4f} "
          f"· 림 은닉 s ≥ {s_rim:+.4f}")
    for dd in (2.0, 4.5, 5.0, 6.0, 7.0, 8.0, 9.0, 12.0):
        hi_, hr_ = _h_max(dd, "int"), _h_max(dd, "rim")
        print(f"         d={dd:5.1f}  z(-d)={_profile_z(-dd):6.3f}  "
              f"h_max 내부={hi_:7.3f} 림={hr_:7.3f}  H밴드 통과율(림) "
              f"{min(1.0, max(0.0, (hr_ - 0.25) / 0.75)):.2f}  base(림) "
              f"{min(1.0, max(0.0, (hr_ - 0.25) / 1.65)):.2f}")
    p_base = _band_yield(1.2, 12.0, 0.25, 1.90)
    p_h = _band_yield(6.0, 12.0, 0.25, 1.00)
    p_h_int = _band_yield(6.0, 12.0, 0.25, 1.00, crit="int")
    exp_h = 24 * p_base + 24 * p_h
    print(f"  [info] 설계 수율(림 모형) base {p_base:.3f} · H {p_h:.3f} "
          f"(계획 §3.2 가정 0.50) · 내부 모형 H {p_h_int:.3f}")
    print(f"  [info] → A팔 48컷(base 24 + H 24) 기대 strict-H {exp_h:.1f} "
          "· 계획 §3.2 하한 paired-H ≥ 12")
    chk("H 밴드 설계 수율 ≥ 계획 가정 0.50", p_h >= 0.50, f"{p_h:.3f}")
    chk("A팔 48컷 기대 strict-H ≥ 12 (§3.2 하한)", exp_h >= 12.0, f"{exp_h:.1f}")
    chk("퇴화 아님 (base 밴드에 V/E 프레임이 남는다)", p_base <= 0.75,
        f"base 수율 {p_base:.3f} ≤ 0.75 — 근거리에서 낙차가 다시 보인다")

    ds = DATUM_STRIP
    cross = [z for z in GATED_ZONES
             if not (z[3] <= ds["x0"] or z[2] >= ds["x1"]
                     or z[5] <= ds["y0"] or z[4] >= ds["y1"])]
    dfail = [(z[0], z[6]) for z in cross if z[6] > DATUM_TOL]
    dtol = [(z[0], z[6]) for z in cross if z[6] <= DATUM_TOL]
    chk("VG-datum 선언 검사 (datum_fail 0)", not dfail,
        f"datum_tol {dtol} · datum_fail {dfail}")

    n_keys = len(SCENE_CONFIG)
    chk("표준 장비 16키", n_keys == 16, f"{n_keys}키")
    declared = set(CUE_CLASS) - {"_structural"}
    cue_keys = {k for k in SCENE_CONFIG if k.startswith("cue_")}
    chk("CUE_CLASS 가 모든 cue_* 를 분류", declared == cue_keys,
        f"미분류 {sorted(cue_keys - declared)} · 초과 {sorted(declared - cue_keys)}")

    print(f"\n  ⇒ sceneH1 CPU 자기검사 {'통과' if ok else '실패'}")
    print("=" * 70)
    return ok


if __name__ == "__main__":
    main()
