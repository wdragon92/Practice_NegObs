# -*- coding: utf-8 -*-
"""
sceneH6_berm_levee2.py — NegObs 신규 씬 H6: 제방 어깨 둔덕 + 호안 옹벽 낙차 (Isaac Sim 4.5)

계열    : **둔덕형 자기가림 (paired-H)** · 생활권 = **제방·수변(뚝방)**
정본    : `experiments/v3_0823/RENDER_PLAN_V3.md` §2.0(공통 표준) · §2.1 표 `sceneH6_berm_levee2`
          (H1 변형 · 다른 부지) · §2.6(CUE_CLASS 사전 분류) · §3.5(val strict-H ≥ 30 회계)
분리    : **val** — 이 씬은 DZ §4.3-3 선택지표 수리의 전제인 `val strict-H ≥ 30`의 1차 공급원이다.
밴드    : base · **H** · **H2**  (H2 = H 밴드 2차 draw. 씬당 A팔 72컷)
승계    : `scene_common.py` · `ground_kit.py`(P13 levee_paved) · `infra_kit` · `props_kit`
          조립 공식 = `Docs/briefs/NegObs_인공씬1호_계단_구현지시서.md:20-22`
          재질 3단 = `Docs/reports/realism_v1_final.md:84` (rev.1 우선 `realism_brief_v1.md:64-130`)
          조명 L0–L7 = `Docs/briefs/lighting_camera_variation_spec_v1.md:359-393`
          props 규율 = `Docs/audit_v4/user_feedback_v5_1.md:6-20, 46-49`

────────────────────────────────────────────────────────────────────────────
씬 조립 공식 (4요소 — 브리프 §2.0)
  ① 경로   진입 보행로(z 0.00) → 제방 어깨 **잔디 둔덕**을 넘어 → 화강석 3단 →
           **호안 상단 관리통로**(z 0.45, 폭 1.57 m)
  ② 위험   관리통로 끝 **호안 옹벽** — 노출면 2.60 m, 수면까지 **2.80 m** 낙차
  ③ 단서   화강석 난간 · 점형블록 · 재질 전이 · 하천 안내표지 · 억새 띠 · 배수 맨홀 ·
           수목보호격자 · 볼라드 · 신축이음 — 전부 **토글형**이고 전부 **자립 프림**
  ④ 은닉   **BermCrest** (둔덕 마루) — 마루가 낙차 개구보다 카메라에 **가깝고 높다**.
           스침각(grazing)에서 관리통로·옹벽 코핑·수면이 통째로 마루 뒤로 사라진다.

*"주변 환경은 장식이 아니라 단서 ③ 그 자체다"* — 둔덕만 덩그러니 만들면 이 씬은 실패다.

────────────────────────────────────────────────────────────────────────────
좌표계 · 종단면 (walk axis = +X, Z-up, m. 카메라는 x = −d 에 서서 +X 를 본다)

    x            z        무엇                                    프림
  ≤ −10.05     0.000     진입 보행로 (인터로킹 200×100)          Ground/Approach
  −10.05→−4.45 0.00→0.95 제방 어깨 잔디 사면 (1:5.9)             Ground/BermRise_00..37
  −4.45→−3.85  0.950     **둔덕 마루** (잔디, 폭 0.60)           **BermCrest**      ← ④ 은닉체
  −3.85→−2.35  0.95→0.45 화강석 3단 (라이즈 0.1667·트레드 0.50)  Ground/ShoulderStep_0..2
  −2.35→−0.78  0.450     호안 상단 관리통로 (화강석 판석)        Ground/ServiceWalk
  −0.78→−0.33  0.450     옹벽 갓돌(코핑) — 관리통로와 **동일 z** RetainWall/Coping   ← 낙차 지지 구조물
  −0.33→ 0.75 −2.150     옹벽 노출면 하단 + 사석 1단             Riprap/T0
   0.75→ 1.85 −2.420     사석 2단(잠김)                          Riprap/T1
  ≥  1.20     −2.350     수면                                    Water/Surface
  ≥ 26.0       0.600     대안(對岸) 둔치 — **높이맵 격자 밖**    FarBank/*

  낙차 = 0.450 − (−2.350) = **2.800 m** (브리프 "하천측 옹벽 낙차 2.5–3.0 m" 준수)
  옹벽 노출면 = 0.450 − (−2.150) = **2.600 m**

────────────────────────────────────────────────────────────────────────────
H 수율 설계 (§3.5 · 이 씬이 존재하는 이유)

가림 판정은 **둔덕 마루 모서리 C = (−3.85, 0.95)** 를 스치는 시선의 기울기 s 하나로 닫힌다:

      s = (0.95 − z_eye) / (d − 3.85),      z_eye = z(−d) + h_rel

  · 낙차 **내부(수면)** 은닉 조건 : 0.95 + 17.85·s ≥ −2.35  ⇒ **s ≥ −0.1849**
        (17.85 = 높이맵 격자 동단 x=14.0 까지의 수평거리. 격자 밖 기하는 라벨러가 보지 않는다)
  · 낙차 **림(코핑 상면)** 은닉 조건 : 0.95 + 3.520·s ≥ 0.45 ⇒ s ≥ −0.1420

**[측정 · 260823_v3p5_h67probe] 어느 조건이 실효 구속인가 — 예측이 틀렸고 프로브가 고쳤다.**
설계 시에는 scene14 on팔 72프레임이 전부 `edge_visible = 0` 인 것을 근거로
`[measured: dataset_manifest_v2corr]` 스침각에서는 림이 깊이 3×3 창 허용오차(RIM_TOL 0.35 m)에
먹혀 **내부 조건이 실효 구속**이라고 적었다. H 밴드 8컷 프로브 실측은 그렇지 않았다 —
8컷 중 1컷이 `int_px = 0` 인데 `edge_visible 126/149 (ratio 0.846)` 로 **E 티어**가 됐다.
이 씬의 림은 화강석 갓돌 상면이라 scene14의 계단 노즈선보다 깊이 불연속이 크고, 그래서
깊이 창에 먹히지 않는다. ⇒ **실효 구속은 림 조건(s ≥ −0.1420)** 이다. 두 모형을 병기한다:

⇒ H 조건 (내부, 상한 모형) :  h_rel ≤ 0.95 − z(−d) + 0.185·(d − 3.85)
⇒ H 조건 (림, 실효 모형)   :  h_rel ≤ 0.95 − z(−d) + 0.142·(d − 3.85)

  d      z(−d)   h_max(내부)  h_max(림)   H밴드 통과율(림)   base 통과율(림)
  5.0    0.857     0.306        0.257           0.01              0.00
  6.0    0.687     0.661        0.568           0.42              0.19
  7.0    0.517     1.016        0.880           0.84              0.38
  8.0    0.348     1.357        1.191           1.00              0.57
  ≥8.5     ↓        ↑            ↑              1.00           0.57 → 1.00
  ---------------------------------------------------------------------------
  밴드 적분 (d ~ LogU)  내부 모형 H 0.95 / base 0.23 · **림 모형 H 0.84 / base 0.19**

  **실측 (H 밴드 8컷, 260823_v3p5_h67probe_A)** : strict-H **7/8 = 0.875**
      (나머지 1컷 = E · int_px 0 · edge_ratio 0.846) — 림 모형 0.84 와 정합.
  기대 strict-H (A팔 72컷 = base 24 + H 24 + H2 24) = 24·0.19 + 48·0.84 ≈ **45**
  계획 기대치 §3.5 = 33.6 (수율 base 0.20 / H 0.60). 즉 **실측 기반 여유 1.34배**.
  덤: 림만 보이고 내부는 안 보이는 프레임이 자연히 섞여 **E 티어 표본도 함께 나온다**.
  근거리(d ≲ 4.5)는 카메라가 둔덕 위에 올라서므로 낙차가 그대로 보인다 → V.
  이것이 base 밴드가 0.22에 머무는 이유이며, **퇴화(전 프레임 H)를 피하는 장치**다.

**모서리 소속 게이트(VG-06) 적합성**: H 프레임에서 가시 지면은 **BermCrest** 상면에서 끝난다.
관리통로·코핑·사석·수면은 전부 마루 그림자 안이므로 **낙차 림의 화면 기여 = 0 px**.
`BermCrest` 는 `hazard_*` 밖에서 지어지는 **자립 지형 솔리드**이며 CUE_CLASS `_structural` 에 등재된다.

────────────────────────────────────────────────────────────────────────────
프림 위생 · 데이텀 (CUE_COVERAGE §4-4 (2)(3)(4))

1. **단서 빌더는 어느 것도 `if cfg["hazard_*"]` 안에 있지 않다** — s14 파라펫 사고(가드가
   `hazard_stairs` 블록 안에 있어 어블레이션 자체가 불가능했던 건)의 재발 방지.
   `grep 'cfg\\["hazard_stairs"\\]'` 이 이 파일에서 잡는 줄은 **조립부 3줄**뿐이다.
2. **모든 `cue_*` 프림은 x ≤ −0.78 (보행 가능측)** 에 선다. 낙차 발자국(x ≥ −0.33)을 덮는
   단서 프림이 **0개**이므로 라벨러 `cells_raw`·`polar_gt`는 `cue_*` 토글에 **구성상 불변**이다
   (VG-01 의 실효 내용).
3. **카메라 데이텀 스트립** `x ∈ [−12.5, −1.0] · |y| ≤ 0.95` 안에는 **토글되는 프림이 하나도 없다.**
   → `cam.ground_z` 는 A/B/C/D 4팔에서 **완전 동일**(VG-datum `datum_exact`).
   `datum_selfcheck()` 가 이것을 씬 조립 직후 기계 검사한다 (구 sceneC2 0.130→0.0163 사고 방지).
4. **void 커버리지 1.0** (VG-void): 낙차 발자국 전역에 실제 바닥 프림이 있다 —
   사석 2단 + 수면 슬래브가 x ∈ [−0.33, 26] 을 빈틈없이 덮는다. 개방 바닥 0.

────────────────────────────────────────────────────────────────────────────
표준법 (법1–법8) 준수 메모
  법1 손상·노후 금지  — 옹벽·난간·포장 전부 **온전한 신품 상태**. 파손 사석·기울어진 난간 없음.
  법2 임의 경고판 금지 — 표지는 `sign_info`(법정 제식 하천 안내표지) 1매뿐. 임의 문구 0.
  법4 기능 필수성      — 난간(2.80 m 낙차 · **법정 의무 아님** — 하천설계기준에 제방·호안 난간
                         조문 부재 `[확인]`. 높이만 도로안전시설 지침 2.3.3 나 110 cm 표준) ·
                         볼라드(제방 진입 차량 억제) ·
                         맨홀·트렌치(관리통로 배수) · 점형블록(교통약자법). 조형물 0.
  법5 차량·계절소품 금지 — 차량 0, 계절 소품 0. `SEASON = "summer"` 는 재질 톤 선언일 뿐이다.
  법6 재질 동결        — 신규 재질 역할 0. 전부 기존 TEX 역할의 재조합.
  법7 `cue_*` 기하 불변 — 위 프림 위생 2번. 유일한 예외적 두께는 점형블록 4 mm·나이징 12 mm·
                         맨홀 뚜껑 7.7 mm 로 전부 hazard_depth 0.30 m 의 **1/25 이하**이고 낙차
                         발자국 밖이다.
  법8 근거 태그        — 본 파일의 수치 주석에 `[계획]`/`[규격]`/`[computed]`/`[measured]` 표기.

실행
    unset PYTHONPATH VIRTUAL_ENV; conda activate env_isaaclab; export PYTHONNOUSERSITE=1
    python scenes/main/sceneH6_berm_levee2.py                 # GUI 룩체크
    NEGOBS_SMOKE=1 python scenes/main/sceneH6_berm_levee2.py  # CPU 조립 스모크(부팅 전 종료)
    NEGOBS_CAPTURE=1 ... python scenes/main/sceneH6_berm_levee2.py   # 헤드리스 캡처
데이터 렌더 진입점 (신설 씬은 AZ 원장 등재 전까지 이 경로가 유일 — CUE_COVERAGE §4-4 (6)):
    python scripts/run_data_render.py --scene-proc <this file> sceneH6 <out_dir> L0 8 <seed>
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


# [계획 §2.0] 생활권 = 제방·수변. 계절은 **여름** — scene12/17 이 공유하는 한강 둔치 세계와
#   같은 계절이어야 val 안에서 s20(가을 캠퍼스)과 계절 상관이 생기지 않는다.
SEASON = "summer"


# ===========================================================================
# [A0] CUE_CLASS — 렌더 **전** 사전 분류 (RENDER_PLAN_V3 §2.6 / ACCOUNTING §2-6)
# ===========================================================================
#   *"신규·개편 씬은 cue_* 토글 + 가드 구조물/장식 사전 분류를 표준 장비로 제작한다.
#     분류는 렌더 전에 끝나야 하며, 렌더 후 분류는 사후 선택이 된다."*
#   렌더 후 VG-01/VG-02 가 이 선언을 **기계 반증**한다. 선언과 실측이 어긋나면 그 씬은
#   **씬 결함**으로 반려하며, 결과를 보고 이 표를 고치지 않는다.
CUE_CLASS = {
    "cue_railing":         "decorative",   # 화강석 동자기둥 난간. 낙차는 RetainWall 이 정의한다
    "cue_tactile":         "decorative",   # 코핑 후방 0.37 m 점형블록 (proud 4 mm)
    "cue_nosing":          "decorative",   # 화강석 3단의 논슬립 띠 (proud 12 mm, 낙차 아님)
    "cue_material_break":  "decorative",   # **재질 재바인딩 전용** — 프림 집합 불변이 구성상 보증
    "cue_sign":            "decorative",   # 하천구역 법정 안내표지 1매
    "cue_scene_dressing":  "decorative",   # 억새 밴드·벤치·가로등·원경 수목·대안 실루엣
    "cue_shadow_caster":   "decorative",   # 양버들 열 + 가로등주 — 그림자 밴드 캐스터
    "cue_manhole":         "decorative",   # 관리통로 배수 맨홀 (flush)
    "cue_tree_grate":      "decorative",   # 진입 보행로 수목보호격자 (flush)
    "cue_slab_joint":      "decorative",   # 포장 줄눈·신축이음 (flush)
    "cue_drainage":        "decorative",   # 관리통로 flush 트렌치 (법7 — 함몰 채널 아님)
    "cue_bollard":         "decorative",   # 제방 진입 차량 억제 볼라드
    "cue_delineator":      "decorative",   # 반사 시선유도봉 (기본 OFF — 법4 "비움이 기본값")
    # ── 토글 금지 목록 (구조물). 이 프림들은 어떤 cue_* 도 참조하지 않는다 ──────────
    "_structural":         ["BermCrest", "RetainWall", "Riprap", "Water",
                            "Ground/ShoulderStep", "Ground/ServiceWalk"],
}


# ===========================================================================
# [A] SCENE_CONFIG — **표준 장비 16키** (RENDER_PLAN_V3 §2.0 · CUE_COVERAGE §4-4 (1))
# ===========================================================================
#   구성: 공통 cue 6 + v3 신설 3(`cue_shadow_caster`·`cue_manhole`·`cue_tree_grate`,
#   FA_REALITY §2 갭 1·2·4위) + FA_REALITY §2 승격 후보 4(`cue_slab_joint` 5위 ·
#   `cue_drainage` 3위 · `cue_bollard` L2 · `cue_delineator` L12) + hazard 1 +
#   팔 제어 2(`keep_dressing`·`placebo_remove`) = **16**.
#   **사문 0**: 16키 전부를 읽는 코드가 이 파일 안에 있고, 전부 프림 생성 또는 재질 재바인딩을
#   실제로 수행한다. `grep -n 'cfg\\["cue_' sceneH6_berm_levee2.py` 가 감사면 전부다.
SCENE_CONFIG = {
    # ── ② 위험: 유일한 기하 토글 ────────────────────────────────────────────
    #   False → 옹벽·코핑·사석·수면·대안이 사라지고 관리통로 레벨(z 0.45)의
    #   평탄 지면이 x = −0.78 … 26.0 을 채운다(반사실 보행 가능면).
    "hazard_stairs":      True,
    # ── ③ 단서: 공통 6키 ────────────────────────────────────────────────────
    "cue_railing":        True,   # 화강석 난간 — 2.80 m 낙차의 법정 가드(법4 통과)
    "cue_tactile":        True,   # 점형블록 — 브리프 "경고블록" 명시 항목
    "cue_nosing":         True,   # 화강석 3단 논슬립 띠
    "cue_material_break": True,   # 관리통로 = 화강석 판석 / 진입로 = 인터로킹
    "cue_sign":           True,   # 하천구역 안내표지 (법2 — 법정 제식만)
    "cue_scene_dressing": True,   # 억새·벤치·가로등·수목·대안 실루엣을 한 번에
    # ── v3 신설 3키 (FA_REALITY §2) ─────────────────────────────────────────
    #   `cue_shadow_caster` 부작용 경보(§2.0): 음성 씬에만 넣으면 "그림자 = 안전"이라는
    #   역지름길이 생긴다. **양성 씬인 이 씬에도 동일 비율로** 배치한다.
    "cue_shadow_caster":  True,
    "cue_manhole":        True,   # 갭 1위 (25.0) — 관리통로 배수 맨홀
    "cue_tree_grate":     True,   # 갭 2위 (20.0) — 진입 보행로 수목보호격자(flush)
    # ── FA_REALITY §2 승격 후보 4키 ────────────────────────────────────────
    "cue_slab_joint":     True,   # 갭 5위 — 줄눈·신축이음
    "cue_drainage":       True,   # 갭 3위 — 관리통로 flush 트렌치
    "cue_bollard":        True,   # L2 — 제방 진입 차량 억제 볼라드
    "cue_delineator":     False,  # L12 — 반사 시선유도봉. 기본 OFF(법4), 코드 경로 상시 보유
    # ── 팔 제어 2키 ─────────────────────────────────────────────────────────
    "keep_dressing":      False,  # C팔: 위험만 지우고 단서·장식은 ON 변환 그대로 유지
    "placebo_remove":     False,  # P팔: 위험·단서 유지, 비단서 물량군(원경 대안)만 제거
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
        approach=dict(x0=-26.0, x1=-10.05, z=0.00),
        rise=dict(x0=-10.05, x1=-4.45, z0=0.00, z1=0.95, n_seg=48, thick=0.25),
        # [computed] 5.60 m 에 0.95 m → 1:5.89 (9.63°). 공원 진입 잔디 사면의 통상 구배
        #   (1:5~1:8) 안.
        # **왜 48개 회전 슬래브인가** — 두 요구가 정면으로 충돌하기 때문이다:
        #   ⓐ `AabbPrefilter.ground_z` 는 상방 레이의 최초 히트라 **회전체 하나**로 지으면
        #      경사 전체를 마루 높이 평면으로 읽는다 → `cam.ground_z` 와 높이맵이 동시에 틀린다.
        #   ⓑ 반대로 **축정렬 계단**으로 근사하면 라이즈 면이 그대로 보인다 — 첫 스모크
        #      (pitch 0.15 · 라이즈 25 mm)에서 h 0.80 · d 10.2 스침각 프레임이 잔디 사면을
        #      **가로 줄무늬 논밭**으로 렌더했다 [측정: 260823_v3p5_h67smoke_A 1차].
        #   ⇒ 절충: 같은 평면 위의 회전 슬래브 48장(구간 0.117 m)으로 **면은 완전 연속**,
        #      AABB 오차는 구간당 상승 0.0198 m + 두께 회전분 0.042 m 로 **≤ 0.034 m** 에 갇힌다.
        #      이 편향은 4팔 공통이므로 VG-datum 은 영향받지 않고, H 수율 모형에는
        #      d=6 에서 h_max 0.66 → 0.63 (5 %) 정도로만 들어온다.
        crest=dict(x0=-4.45, x1=-3.85, z=0.95),
        # 마루 평탄 0.60 m. 길게 잡을수록 가림이 약해진다(마루 위 카메라가 낙차를 본다).
        steps=dict(x0=-3.85, z_top=0.95, riser=0.166667, tread=0.50, n=3),
        # [규격] 라이즈 0.1667·트레드 0.50 — 조경설계기준 완경사 계단(라이즈 0.15±·트레드 0.35~0.60)
        walk=dict(x0=-2.35, x1=-0.78, z=0.45),   # 호안 상단 관리통로 폭 1.57 m
    ),
    # ── 위험 (hazard_stairs 전속) ───────────────────────────────────────────
    hazard=dict(
        coping=dict(x0=-0.78, x1=-0.33, z_top=0.45, thick=0.14),
        wall=dict(x0=-0.75, x1=-0.33, z_top=0.31, z_bot=-2.95),
        riprap=[dict(x0=-0.33, x1=0.75, z_top=-2.15),
                dict(x0=0.75, x1=1.85, z_top=-2.42)],
        riprap_base=-3.30,
        water=dict(x0=1.20, x1=26.0, z=-2.35, thick=0.25),
        # [computed] 낙차 = 0.45 − (−2.35) = 2.800 m · 옹벽 노출면 = 0.45 − (−2.15) = 2.600 m
        farbank=dict(x0=26.0, x1=62.0, z=0.60, base_z=-3.30),
        fill=dict(x0=-0.78, x1=26.0, z=0.45, base_z=-1.20),   # hazard=False 반사실 지면
    ),
    # ── ③ 단서 파라미터 ─────────────────────────────────────────────────────
    #   전부 x ≤ −0.78 (보행 가능측). 낙차 발자국(x ≥ −0.33)을 덮는 단서 프림 0개.
    rail=dict(x=-1.00, y_half=9.0, post_pitch=1.50, post_r=0.09,
              post_h=1.02, cap_t=0.08, rail_r=0.024, top_z=1.55, mid_z=1.05),
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
    #   화강석 동자기둥(Ø0.18) + 스테인리스 Ø0.048 2단 횡대. 격자·등간격 금지(v5.1 §2)에 따라
    #   기둥 yaw 를 ±6° 지터. 순백 대면적 금지 → 화강석 알베도 0.30 대.
    tactile=dict(x0=-1.70, x1=-1.10, y_half=8.6, proud=0.004),
    # [규격·개정 R4 · D82ⓐ] 점형블록 세로 0.40 → **0.60 m**(0.30 m 유닛 2매) ·
    #   코핑 앞 이격 **0.32 m** (≥ 0.30 규정치).
    #   근거 ① 이격 — 「교통약자의 이동편의 증진법 시행규칙」 **별표1**(이동편의시설의
    #     구조·재질 등에 관한 세부기준) "위험장소 **0.3 m 전면**" · 블록 규격 0.3×0.3 m ·
    #     점형 = **경고**(돌출점 36개) / 선형 = **유도**(돌출선 4줄) 역할 구분.
    #   근거 ② 세로폭 — 「도로안전시설 설치 및 관리지침 : 장애인 안전시설」 6.5.2 2)
    #     (= 국도건설공사 설계실무요령 7.5 가 전재): 점형블록 세로폭 **30~90 cm 범위,
    #     60 cm 표준**(0.30 m 유닛 2매). 같은 지침 6.6.7 가 가 더 구체적이다 —
    #     *"보행 동선에서 **위험물과 마주치게 되는 방향에는 60 cm 폭**으로 점형블록을
    #     설치하고, 보행 동선과 **평행한 방향으로는 30 cm 폭**"*. 이 밴드는 접근 동선을
    #     **정면으로 가로지르므로 60 cm** 가 표준값이다.
    #     구 0.40 m 는 300 mm 모듈의 정수배가 아니라 **시공 불가 치수**였다 — 그것이
    #     이 항목의 실제 결함이다. [웹 검증 2026-08-24]
    #   근거 ③ 밴드 수 — 위험 경계 **1곳당 점형 1밴드**(D82 ⓐ). 이 씬은 1밴드다.
    #   [정정] 구 주석의 "코핑 앞 0.37 m 이격"은 실측 **0.32 m** 였다(코핑 x0 = −0.78,
    #     밴드 동단 −1.10). 이격을 정확히 0.30 으로 줄이지 **않는** 이유는 난간 지주다 —
    #     지주 서측면이 x = −1.09 (x −1.00 · r 0.09) 이므로 밴드 동단을 −1.08 로 밀면
    #     지주를 0.01 m 침범한다. 0.32 m 는 규정 하한을 넘기면서 지주를 피하는 최댓값이다.
    #   [면적] 0.60 × 17.2 = 10.32 m² (구 6.88).
    #   **경고 밴드는 1줄**이며 이 씬은 1줄뿐이다. 한강 둔치 관리통로는 출입 제한이
    #   없는 공공 보행 동선(표지도 `sign_info` 하천구역 안내)이라 별표2 의 "위험한
    #   장소" 조항이 적용된다 — sceneH1 의 **출입금지 점검로**와 갈리는 지점이다.
    nosing=dict(width=0.055, proud=0.012),          # [계획] 노징 12 mm (realism_v1_final §84)
    sign=dict(x=-3.10, y=3.40, yaw=180.0, pole_h=2.10, w=0.62, h=0.62),
    # [규격] 볼라드 h 0.8~1.0 · φ0.10~0.20 · 간격 ~1.5 m · 반사띠 (user_feedback_v5_1 §2)
    #   `ys` 를 명시 열거하는 이유 두 가지:
    #     ① 중앙 |y| < 1.25 를 **비운다** — 실물 볼라드 열은 휠체어 유효폭(≥1.5 m)을 위해
    #        보행 동선 중앙을 비우는 것이 기준이고, 동시에 그것이 카메라 데이텀 스트립
    #        (|y| ≤ 0.90)과의 교차를 **0으로** 만든다(VG-datum).
    #     ② 등간격 격자 금지(v5.1 §2) — 아래 `jitter` 가 위치·yaw 를 흔든다.
    #   `xs` 를 y = −4.20 의 **보차도 경계선과 나란한 열**로 잡는다 — 실제 볼라드 열의
    #   기본형이고, 동시에 ⓐ 피치 1.50 m 를 한 번도 깨지 않으며(LINT-6 하드 규칙)
    #   ⓑ 카메라 데이텀 스트립(|y| ≤ 0.90)을 **한 본도 침범하지 않는다**(VG-datum).
    #   위치 지터는 **두지 않는다** — J-3/J-5(07-30 룰링)가 배치 지터를 폐지했고
    #   `placement_lint` LINT-10 이 그것을 정적 검사한다. 볼라드 피치 1.50 m 는
    #   법정 수치이므로 규칙성이 결함이 아니라 요건이다.
    bollard=dict(y=-4.20, xs=(-14.00, -12.50, -11.00, -9.50, -8.00),
                 r=0.075, h=0.88, band_z=0.66, band_t=0.09),
    delineator=dict(x=-8.05, ys=(-2.05, 2.05), r=0.041, h=0.80),
    gkit=dict(
        # **관리통로만** (x0,y0,x1,y1). ground_kit 은 평면 프로파일이므로 region 의 z 는
        #   상수 하나다 — 잔디 사면(x −10.05…−4.45)까지 넣으면 줄눈·빗물받이가 z=0.45 에
        #   떠 버린다(설계 시 스모크 (2) 전수 AABB 가 `JX_0` dz 0.2725 로 잡아냈다).
        #   진입 보행로(z=0)는 아래 `approach_region` 이 따로 맡는다.
        region=(-2.35, -8.60, -0.80, 8.60),
        # 관리통로 폭 1.55 m 안에 횡줄눈이 하나는 들어오도록 step_x 를 3.0 → 1.5 로 줄인다
        #   (프로파일 기본 3.0 은 0/−3.0 에만 줄눈을 놓아 이 구간에 한 줄도 남지 않는다).
        #   1.6 = unit_cell 0.2 × 8 (U2 게이트: step_x 는 유닛셀의 정수배여야 한다)
        walk_step_x=1.6,
        manholes=[(-1.62, 2.28), (-1.70, -3.85)],
        # 빗물받이 3개. **횡단 트렌치는 두지 않는다** — `plan_ground` 의 하드 게이트
        #   B7(GT-E2)이 낙차 모서리 근방의 대리선(proxy line)을 거부하기 때문이고,
        #   그 거부가 옳다: 림 1.8 m 앞의 긴 직선 밴드는 FA_REALITY 가 말하는
        #   **대리선형 FA** 그 자체다. 배수 단서는 빗물받이(점 요소)로만 조달한다.
        gullies=[(-1.30, 5.60), (-1.34, -5.70), (-1.95, 6.10)],
        approach_region=(-24.0, -8.60, -10.10, 8.60),
        tree_grates=[(-11.80, 4.05), (-18.80, 4.05), (-25.80, 4.05)],
    ),
    shadow=dict(
        # [FA_REALITY §2 4위] 그림자 밴드 캐스터. **양성 씬에도 동일 비율**(§2.0 경보).
        #   시선 통로(|y| ≤ 3.6, x ∈ [−12, 0])는 비워 둔다 — 나무가 낙차를 가리면
        #   VG-06 의 "가림체가 종단 모서리를 소유" 판정이 둔덕이 아니라 수목으로 넘어간다.
        #   남측 가로수 열 `approach_S` — 피치 7.0 m (조례 제7조1가 6~8 m).
        poplars=[(-6.30, -5.60), (-13.30, -5.60), (-20.30, -5.60)],
        poplar_h=9.2,
        lamps=[(-5.05, 4.55), (-10.15, -4.60), (-15.25, 4.50)],
        lamp_h=4.6, lamp_arm=1.05,
    ),
    dress=dict(
        reed_bands=[(-2.32, -8.40, -1.62, -4.30), (-2.32, 4.30, -1.62, 8.40)],
        reed_h=1.05,
        #   벤치 yaw 는 **축값만** 쓴다 — J-3/J-5 지터 폐지(spec §1.2)를
        #   `placement_lint` LINT-7 이 강제한다.
        benches=[(-5.90, 3.15, 270.0), (-7.85, -3.05, 90.0)],
        #   북측 가로수 열 `approach_N` — 피치 7.0 m · 1수종(ash)
        trees=[(-11.80, 4.05), (-18.80, 4.05), (-25.80, 4.05)],
        tree_h=6.4,
        hedge=[(-9.95, -8.40, -9.35, -4.10), (-9.95, 4.10, -9.35, 8.40)],
        # 원경: 대안 아파트 실루엣(placebo 물량군). 높이맵 격자(x ≤ 14) 밖 = 라벨 무관.
        backdrop=[("B0", 30.0, 44.0, -26.0, -8.0, 27.0),
                  ("B1", 33.0, 48.0, -6.0, 12.0, 33.0),
                  ("B2", 31.0, 45.0, 14.0, 30.0, 24.0)],
        far_treeline=[(28.5, -21.0), (28.5, -14.0), (28.5, -7.0),
                      (28.5, 0.0), (28.5, 7.0), (28.5, 14.0), (28.5, 21.0)],
    ),

    # ── 재질 3단 (realism_v1_final §84) ─────────────────────────────────────
    #   지면·구조물 = NegObsGround.mdl 경로(텍스처 3매) / 식생·목재 = MDL 상수색 /
    #   금속·도색·사인·유리·수면 = OmniPBR
    material=dict(
        scale=dict(paving_interlock=1.0, plaza_light=1.80, granite_dark=1.80,
                   grass=1.4, gravel=1.2, concrete_wall=2.0, rock_wall=2.4,
                   stone_flag=1.6, tactile=0.3, wood_dark=1.4),
        # [규격] paving_interlock 1.0 → 블록 장변 0.17 m. 실제 보도블록 200×100.
        grass_tint=(0.42, 0.55, 0.30),      # 여름 잔디. 순백 0 %, 녹색 최대 채널
        walk_tint=(0.72, 0.71, 0.68),       # 화강석 판석 (알베도 0.30 대)
        wall_color=(0.31, 0.31, 0.29), wall_rough=0.62,     # 옹벽 콘크리트 (alb_max 0.34 이하)
        coping_tint=(0.66, 0.65, 0.62),
        riprap_tint=(0.52, 0.51, 0.48),
        water_color=(0.055, 0.085, 0.088), water_rough=0.14,
        # [v7 ruling · scene12] 수면 rough 0.08 → 0.14. 무풍 완전거울("인피니티 풀") 방지.
        # [look 층] 재질 프림 이름이 클래스를 정한다 — `Looks/RailStone` 은 "rail" 토큰
        #   때문에 **metal**(alb_max 0.50)로 분류돼 화강석 동자기둥이 흰 금속 기둥으로
        #   렌더됐다 [측정: 1차 스모크]. `Looks/GraniteBaluster` 로 바꾸면 stone
        #   (alb_max 0.34)으로 떨어지고 텍스처 승격도 석재 계열을 탄다.
        baluster_color=(0.42, 0.415, 0.40), baluster_rough=0.55,
        bollard_color=(0.60, 0.61, 0.62), bollard_metallic=0.55, bollard_rough=0.38,
        rail_metal_color=(0.72, 0.73, 0.75), rail_metal=0.85, rail_metal_rough=0.32,
        nosing_color=(0.42, 0.40, 0.36), nosing_rough=0.70,
        band_color=(0.80, 0.52, 0.05),      # 볼라드 반사띠 = 안전 황색(면적 小 → 고휘도 허용)
        pole_color=(0.24, 0.24, 0.26), pole_metallic=0.6, pole_rough=0.5,
        lamp_color=(0.78, 0.78, 0.75), lamp_rough=0.4,
        wood_color=(0.30, 0.20, 0.12), wood_rough=0.85,
        reed_tint=(0.46, 0.44, 0.29),
        canopy_a=(0.028, 0.050, 0.018), canopy_b=(0.038, 0.064, 0.024),
        canopy_rough=1.0,
        # [v5.1 §4 · 순백 대면적 금지] 0.44 → 0.29. 첫 스모크에서 원경 아파트 매스가
        #   정오 직사광 아래 화면 상단을 **흰 벽**으로 채웠다 [측정: clip 0.057 %, 육안].
        #   look 층의 콘크리트 alb_max 0.34 아래로 내린다.
        backdrop_color=(0.29, 0.29, 0.28), backdrop_rough=0.75,
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
    # 태양 방위: 양버들 열과 가로등주의 그림자가 **보행축을 가로질러** 관리통로에 떨어지도록
    #   잡는다(그림자 밴드 = 낙차의 저역 문법). 과노출 금지(P-1)는 조건 카탈로그가 담당.
    SUN_AZ_OFFSET=158.0,

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
#   `grep KEEP_DRESSING` · `grep PLACEBO_REMOVE` 가 감사면 전부다. 모순 설정은 **FATAL** —
#   자기 뜻을 말하지 못하는 팔이 24컷을 찍고 나중에 지표표에서 발견되는 일을 막는다.
KEEP_DRESSING = bool(SCENE_CONFIG.get("keep_dressing", False))
PLACEBO_REMOVE = bool(SCENE_CONFIG.get("placebo_remove", False))
if KEEP_DRESSING:
    if SCENE_CONFIG.get("hazard_stairs", True):
        raise SystemExit(
            "[FATAL sceneH6] keep_dressing=True 는 hazard_stairs=False 를 요구한다 — "
            "위험이 켜져 있으면 보존할 것이 없고 그 팔은 A팔의 라벨 없는 복제가 된다.")
    if not SCENE_CONFIG.get("cue_scene_dressing", True):
        raise SystemExit(
            "[FATAL sceneH6] keep_dressing=True 와 cue_scene_dressing=False 는 모순이다 — "
            "장식이 바로 이 팔이 보존하려는 대상이다.")
if PLACEBO_REMOVE:
    if not SCENE_CONFIG.get("hazard_stairs", True):
        raise SystemExit(
            "[FATAL sceneH6] placebo_remove=True 는 hazard_stairs=True 를 요구한다 — "
            "플라시보 팔은 위험 ON 상태의 외형 대조군(D35)이다.")
    if KEEP_DRESSING:
        raise SystemExit(
            "[FATAL sceneH6] placebo_remove 와 keep_dressing 은 서로 다른 팔(P·C)이며 "
            "동시에 설정될 수 없다.")
_ARM = ("C_hz0_cue1" if KEEP_DRESSING else
        "P_hz1_placebo" if PLACEBO_REMOVE else
        "hz%d_rail%d_tac%d_mat%d_dress%d" % (
            int(SCENE_CONFIG["hazard_stairs"]), int(SCENE_CONFIG["cue_railing"]),
            int(SCENE_CONFIG["cue_tactile"]), int(SCENE_CONFIG["cue_material_break"]),
            int(SCENE_CONFIG["cue_scene_dressing"])))
print(f"[sceneH6] arm={_ARM} keep_dressing={KEEP_DRESSING} "
      f"placebo_remove={PLACEBO_REMOVE}")


# ===========================================================================
# [C] 경로 상수 · 필요 텍스처 역할
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "sceneH6")

ASSET_ROLES = ["paving_interlock", "plaza_light", "granite_dark", "grass",
               "gravel", "concrete_wall", "rock_wall", "stone_flag",
               "tactile", "wood_dark", "sign_info",
               "hdri", "mdl"]

# 카메라 데이텀 스트립 — `variation_kit.sample_camera` 가 뽑는 (d, y) 의 지지집합.
#   d ∈ LogU[1.2, 12] ⇒ x = −d ∈ [−12.00, −1.20] · y ∈ trunc-N(0, 0.35) 잘림 ±0.90.
#   각 방향으로 0.05 m 여유를 더해 [−12.05, −1.15] × [−0.95, 0.95].
DATUM_STRIP = dict(x0=-12.05, x1=-1.15, y0=-0.95, y1=0.95)

# VG-datum 3층 임계 (ACCOUNTING §4.9-5). `datum_exact` < 1e-6 · `datum_tol` ≤ 0.02 m ·
#   `datum_fail` > 0.02 m(격리). 이 씬의 설계 목표는 **datum_exact** 이며,
#   토글 프림이 스트립 안에 서더라도 상면 융기가 `DATUM_TOL` 이하이면 `datum_tol` 로 보고한다.
DATUM_TOL = 0.02

# 토글되는(= 팔에 따라 사라지는) 빌더가 만드는 프림의 XY 범위와 **지면 위 최대 융기 dz** 선언.
#   `datum_selfcheck()` 가 이 표와 DATUM_STRIP 의 교차를 기계 검사하고, 교차분은 dz 로
#   3층 분류한다. 표를 채우는 것은 손이고 검사하는 것은 기계다 — 손이 빠뜨려도
#   (2) 스테이지 전수 AABB 검사가 같은 판정을 독립으로 다시 낸다.
GATED_ZONES = [
    # (tag, key, x0, x1, y0, y1, dz)
    ("RetainWall",   "hazard_stairs",      -0.80,  -0.33,  -9.60,  9.60, 3.40),
    ("Riprap",       "hazard_stairs",      -0.33,   1.85,  -9.60,  9.60, 1.15),
    ("Water",        "hazard_stairs",       1.20,  26.00, -11.00, 11.00, 0.25),
    ("FarBank",      "hazard_stairs",      26.00,  62.00, -31.00, 31.00, 3.90),
    ("FlatFill",     "hazard_stairs(off)", -0.78,  26.00, -31.00, 31.00, 1.65),
    ("Rail",         "cue_railing",        -1.11,  -0.89,  -9.10,  9.10, 1.10),
    # 점형블록: 카메라 스트립과 x 가 겹친다(코핑 앞 0.30 m 규정 위치가 곧 d≈1.2~1.5 지점).
    #   상면 융기는 proud 0.004 m 이므로 최악 판정은 `datum_tol`(≤0.02) 이고 격리 대상이 아니다.
    #   이것이 VG-datum 이 3층으로 설계된 바로 그 사례다 — 사전 선언하고 렌더 후 실측한다.
    ("Tactile",      "cue_tactile",        -1.70,  -1.10,  -8.70,  8.70, 0.004),
    ("Nosing",       "cue_nosing",         -3.86,  -2.34,  -9.60,  9.60, 0.012),
    ("Sign",         "cue_sign",           -3.45,  -2.75,   3.05,  3.75, 2.10),
    ("Bollard",      "cue_bollard",       -14.08,  -7.92,  -4.28, -4.12, 0.88),
    ("Delineator-S", "cue_delineator",     -8.15,  -7.95,  -2.15, -1.95, 0.80),
    ("Delineator-N", "cue_delineator",     -8.15,  -7.95,   1.95,  2.15, 0.80),
    # ground_kit: 줄눈 0.6 mm · 맨홀 7.7 mm · 트렌치 flush · wear_lane 1.2 mm.
    #   `surface=None` 로 잡초(proud 최대 0.107 m)를 **끈다** — 법1(노후·방치 표현 금지)과
    #   VG-datum 이 같은 방향을 가리키는 드문 경우다.
    ("GKitWalk",     "cue_manhole/slab_joint/drainage",
                                           -2.35,  -0.80,  -8.60,  8.60, 0.008),
    ("GKitApproach", "cue_slab_joint",    -24.00, -10.10,  -8.60,  8.60, 0.008),
    ("TreeGrate",    "cue_tree_grate",    -26.60, -11.00,   3.30,  4.80, 0.004),
    ("Shadow-S",     "cue_shadow_caster", -22.00,  -3.00, -10.00, -2.60, 9.20),
    ("Shadow-N",     "cue_shadow_caster", -18.00,  -3.00,   2.60, 10.00, 9.20),
    ("Dress-S",      "cue_scene_dressing", -24.00,  62.00, -31.00, -1.60, 33.0),
    ("Dress-N",      "cue_scene_dressing", -24.00,  62.00,   1.60, 31.00, 33.0),
    ("Dress-Far",    "cue_scene_dressing",  27.00,  62.00, -31.00, 31.00, 33.0),
]


# ===========================================================================
# [C'] PLACEMENT — `placement_lint.py` 의 기하 무관 선언 블록 (w3_execution_spec §10.4)
# ===========================================================================
#   *"A rule whose datum is undeclared does not silently pass."* 기존 33씬은 이 블록을
#   **0개** 선언해 LINT-1/1b/3/5/9 가 구조적으로 죽어 있었다(`placement_rules_v1.yaml`
#   `known_gaps`). 신규 씬은 그 상태를 승계하지 않는다 — 프림을 하나도 만들지 않는
#   순수 선언이므로 기하·GT·높이맵에 **영향이 0**이다.
PLACEMENT = dict(
    # `walk_edges` 는 **의도적으로 선언하지 않는다.** LINT-5 는 「도로의 구조·시설 기준에
    #   관한 규칙」 제16조의 **보도 유효폭**을 재는 규칙인데, 이 씬의 접근부는 보도가 아니라
    #   제방 진입 **광장**이다. 없는 데이텀을 지어내면 그 규칙은 검사가 아니라 허구가 된다
    #   (규칙 파일 자신의 원칙: *"A rule whose datum is undeclared does not silently pass"* —
    #   미선언은 `nodata` 로 보고되지 거짓 통과가 아니다).
    # 보차도 경계 = 볼라드 열이 서는 선 (PE-7 축 잠금 · PE-1 수목 이격의 기준선)
    kerb_lines=[((-15.0, -4.20), (-7.0, -4.20))],
    # 가구류 정면 방위 — J-3/J-5 지터 폐지(07-30)에 따라 **축값만** 쓴다.
    #   `walk_axis` 0° 가 필요한 이유: `sc.build_sign` 의 `/Panel` 은 월드 좌표로 직접
    #   작도되는 메시라 xformOp 자체가 없다(scene_common.py:4572-4595). 즉 인벤토리에서
    #   읽히는 그 프림의 yaw 는 **구조적으로 0** 이고, 실제 정면 방위는 `/Back` 이 갖는다.
    anchors={
        "plaza_S": dict(face_bearing_deg=90.0, props=["Bench_1"]),
        "plaza_N": dict(face_bearing_deg=270.0, props=["Bench_0"]),
        "rim_info": dict(face_bearing_deg=180.0, props=["Sign/Back"]),
        "walk_axis": dict(face_bearing_deg=0.0, props=["Sign/Panel"]),
    },
    # 가로수 열 — 1열 1수종(S-1) · 피치 7.0 m · 방위 = 연석 방위 0°.
    #   `pts` 는 **전 그루의 좌표**여야 한다 — LINT-2 는 선언된 폴리라인의 인접 간격을
    #   그대로 피치로 읽으므로 양 끝점만 적으면 14 m 로 측정된다(설계 시 실측).
    routes={
        "approach_N": dict(pts=[(-25.80, 4.05), (-18.80, 4.05), (-11.80, 4.05)],
                           species="ash", pitch_m=7.0),
        "approach_S": dict(pts=[(-20.30, -5.60), (-13.30, -5.60), (-6.30, -5.60)],
                           species="poplar", pitch_m=7.0),
    },
)


def build_views():
    """카메라 프리셋: grid_views(gy=0, 보행축 +X) + 미장센 4컷."""
    views = sc.grid_views(0.0)
    # berm_over: 둔덕 마루 너머로 관리통로·난간·수면이 층을 이루는 사면 컷
    views["berm_over"] = dict(eye=[-8.5, -3.6, 3.6], tgt=[1.0, 0.6, -1.4])
    # walk_axis_low: 보행축 정면 저시점 — **이 씬의 연구 변수**(마루가 낙차를 삼키는가)
    views["walk_axis_low"] = dict(eye=[-7.4, 0.0, 0.62], tgt=[3.0, 0.1, -0.5])
    # rim_face: 관리통로 위에서 옹벽 코핑·난간·사석·수면을 수직으로 쌓아 스케일을 읽는 컷
    views["rim_face"] = dict(eye=[-2.05, 1.9, 1.55], tgt=[1.4, -0.4, -2.0])
    # crest_walk: 마루 위 보행 시점 — 낙차가 다시 나타나는 지점(H → V 전이 확인)
    views["crest_walk"] = dict(eye=[-4.15, -0.4, 1.55], tgt=[2.6, 0.2, -1.2])
    return views


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. walk_axis_low (h0.62·d7.4)  — 둔덕 마루가 관리통로·코핑·수면을 통째로 삼키는가
 2. crest_walk                  — 마루에 올라서면 낙차가 다시 보이는가 (H → V 전이)
 3. rim_face                    — 옹벽 2.60 m·사석·수면이 하나의 스케일로 읽히는가
 4. berm_over                   — 억새 띠·난간·표지가 마루 위로 층을 이루는가
 5. cue ON vs OFF               — 단서 토글 시 지형·낙차 기하 **불변**인가
 6. 접지·순백                   — 순백(>0.8) 대면적 없음 · 모든 프림 접지 · Z파이팅 없음
 7. props 규율                  — 볼라드 등간격 금지(±3~8° yaw 지터) · 조형물 0"""


def main():
    # [GT-89] SMOKE 게이트 — Isaac 부팅 **전** 조기 종료 (GPU·GUI 미사용).
    if os.environ.get("NEGOBS_SMOKE", "0") == "1" \
            and os.environ.get("NEGOBS_SMOKE_ASSEMBLE", "0") != "1":
        print("SMOKE_OK %s pre-boot gate (GT-89)" % os.path.basename(__file__))
        _geometry_selfcheck()
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
    UsdGeom.Xform.Define(stage, "/World/SceneH6")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    T = PARAMS["terrain"]
    HZ = PARAMS["hazard"]
    ROOT = "/World/SceneH6"
    YH = T["y_half"]

    def BOX(path, center, size, mtl=None, col=False, rotZ=0.0):
        return sc.add_box(stage, path, center, size, mtl, collider=col, rotZ=rotZ)

    def CYL(path, center, r, h, mtl=None, rotY=0.0, rotX=0.0, col=False):
        return sc.add_cylinder(stage, path, center, r, h, mtl,
                               rotY=rotY, rotX=rotX, collider=col)

    def PBR(path, *args, **kwargs):
        return sc.make_pbr(stage, path, *args, **kwargs)

    # [VG-void] 타일 이음매 여유. 인접 슬래브가 **정확히 같은 x** 에서 맞닿으면
    #   `AabbPrefilter.ground_z` 의 하향 레이가 두 상자의 면을 동시에 스치며 **둘 다
    #   놓치는** 일이 생긴다(설계 시 sceneH7 스모크에서 계단 이음매 3줄 197셀이 void 로
    #   찍혔다). 4 mm 겹침을 주면 겹친 구간에서는 **더 높은 상자가 이긴다** — 경계가
    #   4 mm 이동할 뿐이고 높이맵 격자 피치 50 mm 의 1/12 이라 GT 에 영향이 없다.
    SEAM = 0.004

    def SLAB(path, x0, x1, z_top, mtl, y0=None, y1=None, base=None, col=True,
             seam=True):
        """x0..x1 · y0..y1 의 축정렬 지면 슬래브. 상면이 정확히 z_top 에 온다.

        축정렬 박스만 쓰는 이유는 파일 상단 `rise` 주석에 있다 — 회전 박스의 월드 AABB 는
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
        M["paving"] = PBR(f"{ROOT}/Looks/Paving",
                          sc.tex_path("paving_interlock", "diff"),
                          sc.tex_path("paving_interlock", "nor"),
                          sc.tex_path("paving_interlock", "rough"),
                          sca["paving_interlock"])
        M["granite"] = PBR(f"{ROOT}/Looks/Granite",
                           sc.tex_path("plaza_light", "diff"),
                           sc.tex_path("plaza_light", "nor"),
                           sc.tex_path("plaza_light", "rough"),
                           sca["plaza_light"], tint=mp["walk_tint"])
        M["granite_dark"] = PBR(f"{ROOT}/Looks/GraniteDark",
                                sc.tex_path("granite_dark", "diff"),
                                sc.tex_path("granite_dark", "nor"),
                                sc.tex_path("granite_dark", "rough"),
                                sca["granite_dark"], tint=mp["coping_tint"])
        M["grass"] = PBR(f"{ROOT}/Looks/Grass", sc.tex_path("grass", "diff"),
                         sc.tex_path("grass", "nor"), sc.tex_path("grass", "rough"),
                         sca["grass"], tint=mp["grass_tint"])
        M["gravel"] = PBR(f"{ROOT}/Looks/Gravel", sc.tex_path("gravel", "diff"),
                          sc.tex_path("gravel", "nor"), sc.tex_path("gravel", "rough"),
                          sca["gravel"])
        M["rock"] = PBR(f"{ROOT}/Looks/RockWall", sc.tex_path("rock_wall", "diff"),
                        sc.tex_path("rock_wall", "nor"),
                        sc.tex_path("rock_wall", "rough"),
                        sca["rock_wall"], tint=mp["riprap_tint"])
        M["flag"] = PBR(f"{ROOT}/Looks/Flag", sc.tex_path("stone_flag", "diff"),
                        sc.tex_path("stone_flag", "nor"),
                        sc.tex_path("stone_flag", "rough"), sca["stone_flag"])
        M["tactile"] = sc.tactile_pbr(stage, f"{ROOT}/Looks/Tactile",
                                      scale_m=sca["tactile"])
        M["wood"] = PBR(f"{ROOT}/Looks/WoodDark", sc.tex_path("wood_dark", "diff"),
                        sc.tex_path("wood_dark", "nor"),
                        sc.tex_path("wood_dark", "rough"), sca["wood_dark"])
        # 구조물 콘크리트 — 상수색(look 층이 콘크리트 계열로 텍스처 승격)
        M["wall"] = PBR(f"{ROOT}/Looks/ConcreteWall",
                        diffuse_color=mp["wall_color"],
                        roughness_const=mp["wall_rough"])
        # 금속·도색·수면 = OmniPBR
        M["water"] = PBR(f"{ROOT}/Looks/Water", diffuse_color=mp["water_color"],
                         roughness_const=mp["water_rough"], metallic=0.0)
        M["baluster"] = PBR(f"{ROOT}/Looks/GraniteBaluster",
                            diffuse_color=mp["baluster_color"],
                            roughness_const=mp["baluster_rough"])
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
        # `Looks/Backdrop` 은 look 층에서 **misc**(무처방 상수색)로 떨어진다.
        #   `BgConcrete` 로 바꾸면 concrete 클래스가 되어 알베도 상한 0.34 와 텍스처
        #   승격을 받는다 — 원경 매스가 평평한 흰 판이 되는 것을 막는 표준 경로다.
        M["backdrop"] = PBR(f"{ROOT}/Looks/BgConcrete",
                            diffuse_color=mp["backdrop_color"],
                            roughness_const=mp["backdrop_rough"])
        M["sign"] = PBR(f"{ROOT}/Looks/Sign", sc.tex_path("sign_info", "diff"),
                        uv_mode=True)
        return M

    # -------------------------------------------------------------------
    # ① 경로 + ④ 은닉 — 지형. **hazard_* 밖**. 4팔 전부에서 동일 프림·동일 좌표.
    # -------------------------------------------------------------------
    def build_terrain(M):
        """진입 보행로 → 둔덕 사면 → **BermCrest** → 화강석 3단 → 관리통로.

        `cam.ground_z` 가 이 프림들만으로 결정되므로(단서·위험 프림은 데이텀 스트립 밖),
        VG-datum 은 `datum_exact` 로 통과하도록 **구성상** 되어 있다.
        """
        a, r, c, st, w = T["approach"], T["rise"], T["crest"], T["steps"], T["walk"]

        # (1) 진입 보행로 — 큰 면이므로 ground skin(±10 mm 미세기복)이 붙는다
        SLAB(f"{ROOT}/Ground/Approach", a["x0"], a["x1"], a["z"], M["paving"])

        # (2) 제방 어깨 잔디 사면 — **같은 평면 위의 회전 슬래브 48장** (위 PARAMS 주석)
        #     아래에 z=0 채움 상자를 깔아 사면이 떠 있는 껍데기가 되지 않게 한다.
        SLAB(f"{ROOT}/Ground/BermFill", r["x0"], r["x1"], r["z0"], M["grass"])
        n = int(r["n_seg"])
        seg = (r["x1"] - r["x0"]) / n
        d_seg = (r["z1"] - r["z0"]) / n
        for i in range(n):
            x0 = r["x0"] + i * seg
            sc.build_slope(stage, f"{ROOT}/Ground/BermRise_{i:02d}",
                           x0, r["z0"] + i * d_seg, seg, -d_seg,
                           -YH, YH, r["thick"], M["grass"],
                           margin=0.0, collider=True)

        # (3) **BermCrest** — 이 씬의 은닉체(④). CUE_CLASS `_structural` 등재.
        #     어떤 cue_* 도 이 프림을 참조하지 않는다.
        SLAB(f"{ROOT}/BermCrest", c["x0"], c["x1"], c["z"], M["grass"])

        # (4) 화강석 3단 — 마루에서 관리통로로 내려서는 완경사 계단
        for i in range(st["n"]):
            x0 = st["x0"] + i * st["tread"]
            x1 = x0 + st["tread"]
            z = st["z_top"] - (i + 1) * st["riser"]
            SLAB(f"{ROOT}/Ground/ShoulderStep_{i}", x0, x1, round(z, 4),
                 M["granite_dark"])

        # (5) 호안 상단 관리통로 — `cue_material_break` 의 유일한 대상(재바인딩 전용)
        walk_mtl = M["granite"] if cfg["cue_material_break"] else M["paving"]
        SLAB(f"{ROOT}/Ground/ServiceWalk", w["x0"], w["x1"], w["z"], walk_mtl)
        print(f"[cue] material_break={cfg['cue_material_break']} → ServiceWalk "
              f"= {'화강석 판석(Granite)' if cfg['cue_material_break'] else '인터로킹(Paving)'} "
              "· **프림 집합 불변**(재질 재바인딩 전용) → 높이맵 비트 동일 보증")

    # -------------------------------------------------------------------
    # ② 위험 — hazard_stairs 전속. 여기에는 **단서가 한 개도 없다**(프림 위생 1).
    # -------------------------------------------------------------------
    def build_hazard(M):
        cp, wl = HZ["coping"], HZ["wall"]
        sc.skin_exclude(f"{ROOT}/RetainWall", f"{ROOT}/Riprap", f"{ROOT}/Water")
        # 옹벽 몸체 (콘크리트) — 상면은 갓돌 밑면
        BOX(f"{ROOT}/RetainWall/Body",
            ((wl["x0"] + wl["x1"]) / 2.0, 0.0, (wl["z_top"] + wl["z_bot"]) / 2.0),
            (wl["x1"] - wl["x0"], 2 * YH, wl["z_top"] - wl["z_bot"]),
            M["wall"], col=True)
        # 화강석 갓돌 — 상면 z 가 관리통로와 **정확히 같다**(0.45). 단차 0.
        BOX(f"{ROOT}/RetainWall/Coping",
            ((cp["x0"] + cp["x1"]) / 2.0, 0.0, cp["z_top"] - cp["thick"] / 2.0),
            (cp["x1"] - cp["x0"], 2 * YH, cp["thick"]), M["granite_dark"], col=True)
        # 사석 호안 2단 — 축정렬 계단식. (회전 사면은 AABB 를 평면으로 만든다)
        #   x 양단에 4 mm 이음매 여유 — 위 SEAM 주석과 같은 이유.
        for i, t in enumerate(HZ["riprap"]):
            x0, x1 = t["x0"] - 0.004, t["x1"] + 0.004
            BOX(f"{ROOT}/Riprap/T{i}",
                ((x0 + x1) / 2.0, 0.0,
                 (t["z_top"] + HZ["riprap_base"]) / 2.0),
                (x1 - x0, 2 * YH, t["z_top"] - HZ["riprap_base"]),
                M["rock"], col=True)
        # 수면 — VG-void: 낙차 발자국 전역에 **실제 바닥 프림**. 개방 바닥 0.
        wt = HZ["water"]
        BOX(f"{ROOT}/Water/Surface",
            ((wt["x0"] + wt["x1"]) / 2.0, 0.0, wt["z"] - wt["thick"] / 2.0),
            (wt["x1"] - wt["x0"], 2 * YH + 3.0, wt["thick"]), M["water"])
        fb = HZ["farbank"]
        # 대안(對岸) — 높이맵 격자 동단 x=14.0 **밖**(x ≥ 26)이라 라벨과 무관하다.
        #   수평 폐합용 지형이며 이 씬의 GT 에 한 칸도 기여하지 않는다.
        BOX(f"{ROOT}/FarBank/Bank",
            ((fb["x0"] + fb["x1"]) / 2.0, 0.0, (fb["z"] + fb["base_z"]) / 2.0),
            (fb["x1"] - fb["x0"], 62.0, fb["z"] - fb["base_z"]), M["grass"])
        BOX(f"{ROOT}/FarBank/Revetment",
            (fb["x0"] - 0.9, 0.0, (fb["z"] - 1.5)),
            (1.8, 62.0, 3.4), M["rock"])
        print(f"[hazard] 낙차 = {HZ['coping']['z_top'] - wt['z']:.3f} m "
              f"(코핑 {HZ['coping']['z_top']:+.2f} → 수면 {wt['z']:+.2f}) · "
              f"옹벽 노출면 {HZ['coping']['z_top'] - HZ['riprap'][0]['z_top']:.3f} m")

    def build_flat_fill(M):
        """hazard_stairs=False 대조군 — 관리통로 레벨의 평탄 지면이 낙차 발자국을 채운다.

        이것이 라벨러의 **반사실 보행 가능면 z_off** 다(footprint v2 = z_off − z_on ≥ 0.3).
        채움면의 z 는 관리통로와 **같은 0.45** 여야 하며, 그래야 발자국이 옹벽 낙차 전체가 된다.
        """
        f = HZ["fill"]
        sc.skin_exclude(f"{ROOT}/FlatFill/Far")
        SLAB(f"{ROOT}/FlatFill/Near", f["x0"], 14.5, f["z"], M["paving"],
             base=f["base_z"])
        SLAB(f"{ROOT}/FlatFill/Far", 14.5, f["x1"], f["z"], M["grass"],
             y0=-31.0, y1=31.0, base=f["base_z"])
        print(f"[hazard] OFF — 반사실 보행 가능면 z_off = {f['z']:+.3f} "
              f"(x {f['x0']:+.2f} … {f['x1']:+.1f})")

    # -------------------------------------------------------------------
    # ③ 단서 — **전부 hazard_* 밖의 자립 프림**. 전부 x ≤ −0.78.
    # -------------------------------------------------------------------
    def build_railing(M):
        """화강석 동자기둥 난간 + 스테인리스 2단 횡대. 기둥 yaw ±6° 지터(등간격 금지)."""
        r = PARAMS["rail"]
        n = int(math.floor(2 * r["y_half"] / r["post_pitch"])) + 1
        y0 = -r["y_half"]
        for i in range(n):
            # 동자기둥은 **정렬해 세운다** — 석재 난간의 실제 시공이 그러하고,
            #   J-3/J-5(07-30)가 배치 지터를 폐지했다.
            y = y0 + i * r["post_pitch"]
            BOX(f"{ROOT}/Rail/Post_{i:02d}",
                (r["x"], y, T["walk"]["z"] + r["post_h"] / 2.0),
                (2 * r["post_r"], 2 * r["post_r"], r["post_h"]),
                M["baluster"])
            BOX(f"{ROOT}/Rail/PostCap_{i:02d}",
                (r["x"], y, T["walk"]["z"] + r["post_h"] + r["cap_t"] / 2.0),
                (2 * r["post_r"] + 0.03, 2 * r["post_r"] + 0.03, r["cap_t"]),
                M["granite_dark"])
        for tag, z in (("Top", r["top_z"]), ("Mid", r["mid_z"])):
            CYL(f"{ROOT}/Rail/{tag}Rail", (r["x"], 0.0, z), r["rail_r"],
                2 * r["y_half"] + 0.4, M["rail"], rotX=90.0)
        print(f"[cue] railing ON — 동자기둥 {n}본(피치 {r['post_pitch']} m) "
              f"· 가드선 {r['top_z']:.2f} m "
              f"(유효높이 {r['top_z'] - T['walk']['z']:.2f} m ≥ 1.10 규정)")

    def build_tactile(M):
        t = PARAMS["tactile"]
        sc.build_tactile(stage, f"{ROOT}/Tactile", t["x0"], t["x1"],
                         -t["y_half"], t["y_half"], M["tactile"],
                         z=T["walk"]["z"], proud=t["proud"])
        print(f"[cue] tactile ON — **경고 1밴드** 세로 {t['x1'] - t['x0']:.2f} m "
              f"(0.30 m 유닛 {round((t['x1'] - t['x0']) / 0.30)}매) · 코핑 앞 이격 "
              f"{HZ['coping']['x0'] - t['x1']:.2f} m · proud {t['proud']} m "
              "[규격 교통약자법 시행규칙 별표1 · 국도 실무요령 7.5]")

    def build_nosing(M):
        """화강석 3단의 논슬립 나이징 띠. 낙차 부재가 아니라 **계단 코 처리**다."""
        st, ng = T["steps"], PARAMS["nosing"]
        for i in range(st["n"]):
            x1 = st["x0"] + (i + 1) * st["tread"]
            z = st["z_top"] - (i + 1) * st["riser"]
            BOX(f"{ROOT}/Nosing/Strip_{i}",
                (x1 - ng["width"] / 2.0, 0.0, z + ng["proud"] / 2.0),
                (ng["width"], 2 * YH, ng["proud"]), M["nosing"])
        print(f"[cue] nosing ON — {st['n']}단 · 폭 {ng['width']} m · "
              f"proud {ng['proud'] * 1000:.0f} mm [계획 realism_v1_final §84]")

    def build_sign(M):
        """하천구역 안내표지 1매 — 법2(임의 경고판 금지) 준수: 법정 제식 판만."""
        s = PARAMS["sign"]
        sc.build_sign(stage, f"{ROOT}/Sign", s["x"], s["y"], T["walk"]["z"],
                      s["yaw"], M["sign"], w=s["w"], h=s["h"],
                      pole_h=s["pole_h"], pole_mtl=M["pole"], back_mtl=M["iron"])
        print(f"[cue] sign ON — 하천구역 안내표지 1매 @({s['x']:+.2f},{s['y']:+.2f}) "
              "· 임의 문구 0 (법2)")

    def build_bollards(M):
        """제방 진입 차량 억제 볼라드 열. 격자·등간격 금지 → 위치 지터, 중앙 유효폭 개방."""
        b = PARAMS["bollard"]
        for i, x0 in enumerate(b["xs"]):
            x, y = x0, b["y"]
            # 프림 명명은 `placement_lint` 의 `props.bollard` 규약을 따른다 —
            #   인스턴스 세그먼트 `Bollard_NN` + 하중 실린더 `/Post` + 무시 접미 `/Band`.
            #   그래야 LINT-6 이 높이·직경을 **인벤토리에서 직접 읽어** 검사한다.
            CYL(f"{ROOT}/Bollard_{i:02d}/Post", (x, y, b["h"] / 2.0),
                b["r"], b["h"], M["bollard"])
            CYL(f"{ROOT}/Bollard_{i:02d}/Band", (x, y, b["band_z"]),
                b["r"] + 0.004, b["band_t"], M["band"])
        print(f"[cue] bollard ON — {len(b['xs'])}본 · h {b['h']} m · "
              f"φ{2 * b['r']:.2f} m · 피치 1.50 m · y {b['y']:+.2f} (보차도 경계) "
              "· 반사띠 [규격 교통약자법 시행규칙 별표2 제7호]")

    def build_delineators(M):
        """반사 시선유도봉 — 관리통로 진입부 차량 억제 보조. 기본 OFF(법4)."""
        d = PARAMS["delineator"]
        for i, y in enumerate(d["ys"]):
            CYL(f"{ROOT}/Delineator/D_{i}", (d["x"], y, d["h"] / 2.0),
                d["r"], d["h"], M["band"])
            CYL(f"{ROOT}/Delineator/Band_{i}", (d["x"], y, d["h"] - 0.16),
                d["r"] + 0.003, 0.08, M["lamp"])
        print(f"[cue] delineator ON — {len(d['ys'])}본")

    def build_ground_kit(M):
        """지면 문양 3키 (`cue_manhole`·`cue_tree_grate`·`cue_slab_joint`) + `cue_drainage`.

        전부 **flush**(단차 ≤ 8 mm)이므로 법7(기하 불변)을 지킨다. 함몰 채널은 hazard 기하이지
        `cue_*` 가 아니라는 것이 `cue_drainage` 승격의 전제 조건이었다(FA_REALITY §2 3위).
        """
        g = PARAMS["gkit"]
        M2 = dict(M)
        M2.update(joint=M["granite_dark"], crack=M["granite_dark"],
                  manhole=M["iron"], gully=M["iron"], gutter=M["granite_dark"],
                  gutter_cover=M["iron"], trench=M["iron"], trench_frame=M["iron"],
                  marking=M["lamp"], weed=M["grass"], wear=M["gravel"],
                  stain_dirt=M["gravel"], stain_water=M["gravel"],
                  tree_grate=M["iron"], grate=M["iron"])
        kit = gk.kit_from_scene_common(sc, stage)
        n_prims = 0

        # (a) 관리통로 — 맨홀 · 빗물받이 · 트렌치 · 줄눈
        infra = dict(manhole=len(g["manholes"]) if cfg["cue_manhole"] else 0,
                     gully=len(g["gullies"]) if cfg["cue_drainage"] else 0,
                     gutter_L=0, trench=0)
        sites = dict()
        if cfg["cue_manhole"]:
            sites["manhole"] = [tuple(v) for v in g["manholes"]]
        if cfg["cue_drainage"]:
            sites["gully"] = [tuple(v) for v in g["gullies"]]
        gp = gk.plan_ground(
            "levee_paved", region=tuple(g["region"]), z=T["walk"]["z"], gy=0.0,
            origin=(0.0, 0.0, 0.0), edges=[("levee_rim", HZ["coping"]["x0"])],
            dists=(2, 5, 10), scene="sceneH6", tactile=(),
            # `surface=None` — 잡초/균열/오염 데칼을 끈다. 법1(손상·노후·방치 표현 금지)이
            #   1차 이유이고, 잡초 프림이 proud 0.10 m 까지 자라 카메라 데이텀 스트립을
            #   `datum_fail` 로 밀 수 있다는 것이 2차 이유다.
            overrides=dict(infra=infra, surface=None,
                           pave=dict(step_x=g["walk_step_x"])),
            sites=sites, seed=66)
        if not cfg["cue_slab_joint"]:
            gp["ops"] = [o for o in gp["ops"] if o["name"] != "joints"]
            gp["elements"] = [e for e in gp["elements"] if e["kind"] != "joint"]
        res = gk.apply_ground(kit, f"{ROOT}/GKitWalk", gp, M2,
                              skin_exclude=sc.skin_exclude,
                              scatter=sc.scatter_debris)
        n_prims += res["prims"]

        # (b) 진입 보행로 — 수목보호격자(flush) · 줄눈
        infra2 = dict(manhole=0, gully=0, gutter_L=0, trench=0)
        gp2 = gk.plan_ground(
            "sidewalk_block", region=tuple(g["approach_region"]),
            z=T["approach"]["z"], gy=0.0, origin=(0.0, 0.0, 0.0),
            dists=(2, 5, 10), scene="sceneH6", tactile=(),
            overrides=dict(infra=infra2, surface=None), seed=67)
        if not cfg["cue_slab_joint"]:
            gp2["ops"] = [o for o in gp2["ops"] if o["name"] != "joints"]
            gp2["elements"] = [e for e in gp2["elements"] if e["kind"] != "joint"]
        res2 = gk.apply_ground(kit, f"{ROOT}/GKitApproach", gp2, M2,
                               skin_exclude=sc.skin_exclude,
                               scatter=sc.scatter_debris)
        n_prims += res2["prims"]

        # (c) 수목보호격자 — 빌더가 없으므로 flush 격자를 직접 짓는다(갭 2위 = 전무)
        n_grate = 0
        if cfg["cue_tree_grate"]:
            for i, (gx, gy_) in enumerate(g["tree_grates"]):
                n_grate += _tree_grate(M, f"{ROOT}/TreeGrate_{i}", gx, gy_,
                                       T["approach"]["z"])
        print(f"[cue] ground pattern — manhole={cfg['cue_manhole']}({len(g['manholes'])}) "
              f"tree_grate={cfg['cue_tree_grate']}({n_grate} 프림) "
              f"slab_joint={cfg['cue_slab_joint']} drainage={cfg['cue_drainage']} "
              f"· gkit 프림 {n_prims} · δmax {max(res['gt_delta_max'], res2['gt_delta_max']):.4f} m "
              "(flush — 법7)")
        return n_prims + n_grate

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
        # 수피 개구 (중앙 원형) — 흙이 보이는 부분
        sc.add_disc(stage, f"{path}/Soil", (cx, cy, z - 0.02), 0.22, 0.06,
                    M["gravel"], seg=18)
        return n + 1

    def build_shadow_casters(M):
        """그림자 밴드 캐스터 — 양버들 열 + 가로등주 (v3 신설 `cue_shadow_caster`).

        **양성 씬에도 동일 비율로 배치한다**(RENDER_PLAN_V3 §2.0 부작용 경보). 음성 씬 전용이면
        "그림자 = 안전"이라는 역지름길이 생긴다.
        배치 규칙: 시선 통로 |y| ≤ 3.6 · x ∈ [−12, 0] 은 **비워 둔다** — 수목이 낙차를 가리면
        VG-06 의 모서리 소유가 둔덕에서 수목으로 넘어가 이 씬의 은닉 계열 주장이 깨진다.
        """
        s = PARAMS["shadow"]
        for i, (tx, ty) in enumerate(s["poplars"]):
            gz = _ground_z_ref(tx)
            sc.build_tree(stage, f"{ROOT}/Shadow/Poplar_{i}", tx, ty, gz,
                          M["wood"], M["canopy_a"], M["canopy_b"],
                          trunk_r=0.17, trunk_h=s["poplar_h"] * 0.55,
                          canopy_blobs=11, canopy_spread=1.25,
                          species="poplar")
        for i, (lx, ly) in enumerate(s["lamps"]):
            gz = _ground_z_ref(lx)
            CYL(f"{ROOT}/Shadow/LampPole_{i}", (lx, ly, gz + s["lamp_h"] / 2.0),
                0.075, s["lamp_h"], M["pole"])
            arm_y = ly - math.copysign(s["lamp_arm"] / 2.0, ly)
            CYL(f"{ROOT}/Shadow/LampArm_{i}", (lx, arm_y, gz + s["lamp_h"]),
                0.05, s["lamp_arm"], M["pole"], rotX=90.0)
            BOX(f"{ROOT}/Shadow/LampHead_{i}",
                (lx, ly - math.copysign(s["lamp_arm"], ly), gz + s["lamp_h"] - 0.09),
                (0.46, 0.20, 0.13), M["lamp"])
        print(f"[cue] shadow_caster ON — 양버들 {len(s['poplars'])}주 + "
              f"가로등 {len(s['lamps'])}주 · 시선 통로(|y|≤3.6) 청소됨")

    def build_dressing(M):
        """③ 단서의 환경 성분 — 억새 띠 · 벤치 · 수목 · 관목 띠 · 원경 대안.

        *"주변 환경은 장식이 아니라 단서 ③ 그 자체다"*. 억새 띠는 낙차 이면(수변) 환경 신호이고,
        원경 대안 실루엣은 수평 폐합이다(순백 대면적 금지 → 알베도 0.44).
        """
        d = PARAMS["dress"]
        # 억새 밴드 — 관리통로 배후, 시선 통로 밖(|y| ≥ 4.3)
        for i, (x0, y0, x1, y1) in enumerate(d["reed_bands"]):
            sc.build_hedge(stage, f"{ROOT}/Dress/Reed_{i}", x0, y0, x1, y1,
                           d["reed_h"], mtl=M["reed"], base_z=T["walk"]["z"],
                           rounded=True, crown_max=40)
        # 관목 띠 — 사면 하단
        for i, (x0, y0, x1, y1) in enumerate(d["hedge"]):
            sc.place_hedge_row(stage, f"{ROOT}/Dress/Hedge_{i}", x0, y0, x1, y1,
                               0.85, seed=1660 + i, base_z=0.0,
                               fallback_mtl=M["reed"])
        # 벤치 — 진입 보행로변
        for i, (bx, by, byaw) in enumerate(d["benches"]):
            sc.build_bench(stage, f"{ROOT}/Dress/Bench_{i}", bx, by,
                           _ground_z_ref(bx), M["wood"], yaw=byaw)
        # 가로수 — 진입 보행로(수목보호격자와 같은 좌표)
        for i, (tx, ty) in enumerate(d["trees"]):
            sc.build_tree(stage, f"{ROOT}/Dress/Tree_{i}", tx, ty,
                          _ground_z_ref(tx), M["wood"], M["canopy_a"],
                          M["canopy_b"], trunk_r=0.13,
                          trunk_h=d["tree_h"] * 0.5, canopy_blobs=10,
                          canopy_spread=1.1, species="ash")
        # 원경 대안 아파트 실루엣 — placebo_remove 의 대상 물량군
        if not PLACEBO_REMOVE:
            for tag, x0, x1, y0, y1, hgt in d["backdrop"]:
                BOX(f"{ROOT}/Dress/Backdrop_{tag}",
                    ((x0 + x1) / 2.0, (y0 + y1) / 2.0, hgt / 2.0 + 0.6),
                    (x1 - x0, y1 - y0, hgt), M["backdrop"])
            for i, (tx, ty) in enumerate(d["far_treeline"]):
                sc.build_tree(stage, f"{ROOT}/Dress/FarTree_{i}", tx, ty, 0.6,
                              M["wood"], M["canopy_a"], M["canopy_b"],
                              trunk_r=0.20, trunk_h=5.0, canopy_blobs=9,
                              canopy_spread=1.5, species="poplar", belt=True)
        else:
            print("[placebo] 원경 대안 실루엣 물량군 제거 — 위험·단서는 전부 유지(D35 P팔)")
        print(f"[cue] scene_dressing ON — 억새 {len(d['reed_bands'])}띠 · "
              f"벤치 {len(d['benches'])} · 가로수 {len(d['trees'])} · "
              f"관목 {len(d['hedge'])}띠 · 원경 {0 if PLACEBO_REMOVE else len(d['backdrop'])}동")

    def _ground_z_ref(x):
        """지형 종단면의 해석적 z(x). 배치 전용(높이맵은 AABB 가 따로 측정한다)."""
        a, r, c, st, w = (T["approach"], T["rise"], T["crest"], T["steps"],
                          T["walk"])
        if x <= r["x0"]:
            return a["z"]
        if x <= r["x1"]:
            f = (x - r["x0"]) / (r["x1"] - r["x0"])
            return r["z0"] + (r["z1"] - r["z0"]) * f
        if x <= c["x1"]:
            return c["z"]
        if x < st["x0"] + st["n"] * st["tread"]:
            i = min(st["n"] - 1, max(0, int((x - st["x0"]) / st["tread"])))
            return st["z_top"] - (i + 1) * st["riser"]
        return w["z"]

    # -------------------------------------------------------------------
    # 자기검사 — 조립 직후, 렌더 전
    # -------------------------------------------------------------------
    def datum_selfcheck():
        """VG-datum 사전검사 · 프림 위생 검사 · VG-void 발자국 검사.

        (1) `GATED_ZONES` 의 어떤 토글 구역도 카메라 데이텀 스트립과 겹치지 않을 것
        (2) 스테이지 전수 AABB 로 (1) 을 재확인 — 손이 표를 빠뜨려도 기계가 잡는다
        (3) 낙차 발자국 x ∈ [rim, 14.0] 에 바닥 프림이 빈틈없이 있을 것 (VG-void (b))
        (4) 단서 프림이 낙차 발자국 위에 0개일 것 (VG-01 실효 조건)
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
                       "/Delineator", "/GKitWalk", "/GKitApproach", "/TreeGrate",
                       "/Shadow", "/Dress", "/RetainWall", "/Riprap", "/Water",
                       "/FarBank", "/FlatFill")
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
            # 스트립 안에서 실제로 `ground_z` 를 움직일 수 있는가 = 지면 위 융기량.
            #   지면 기준면은 그 x 에서의 해석적 종단면 z(x).
            x_ref = min(max(0.5 * (mn[0] + mx[0]), ds["x0"]), ds["x1"])
            dz = float(mx[2]) - _ground_z_ref(x_ref)
            (tol_hits if dz <= DATUM_TOL else hits).append((p, round(dz, 4)))
        if hits:
            ok = False
        print(f"[selfcheck] (2) 토글 프림 {n_scan}개 전수 AABB → 스트립 교차 "
              f"{len(hits) + len(tol_hits)}건 (datum_tol {len(tol_hits)} · "
              f"datum_fail {len(hits)})"
              + (f" FAIL={hits[:6]}" if hits else " · OK"))

        # (3) VG-void — 발자국 전역 바닥 커버리지 (해석적 종단면 검사)
        rim = HZ["coping"]["x1"]
        segs = ([(rim, HZ["riprap"][0]["x1"]), (HZ["riprap"][0]["x1"],
                                                HZ["riprap"][1]["x1"]),
                 (HZ["water"]["x0"], 14.0)] if cfg["hazard_stairs"]
                else [(HZ["fill"]["x0"], 14.0)])
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
                     "/Delineator", "/GKitWalk", "/GKitApproach", "/TreeGrate",
                     "/Shadow", "/Dress")
        fp_x0 = HZ["coping"]["x1"]
        over = []
        for prim in stage.Traverse():
            p = str(prim.GetPath())
            if not p.startswith(ROOT) or not prim.IsA(UsdGeom.Gprim):
                continue
            tail = p[len(ROOT):]
            if not any(tail.startswith(g) for g in cue_roots):
                continue
            if tail.startswith("/Dress/Backdrop") or tail.startswith("/Dress/FarTree"):
                continue                     # 원경(x ≥ 26) — 높이맵 격자 밖
            try:
                b = bbc.ComputeWorldBound(prim).ComputeAlignedRange()
            except Exception:
                continue
            if b.IsEmpty():
                continue
            mn, mx = b.GetMin(), b.GetMax()
            if mx[0] > fp_x0 and mn[0] < 14.0 and mx[1] > -8.0 and mn[1] < 8.0:
                over.append(p)
        if over:
            ok = False
        print(f"[selfcheck] (4) 단서 프림 × 발자국(x ≥ {fp_x0:+.2f}) 교차 "
              f"{len(over)}건" + (f" {over[:6]}" if over else " · OK "
                                  "→ `cells_raw`·`polar_gt` 는 cue_* 에 구성상 불변"))

        # (5) H 수율 설계 재계산 — 종단면이 바뀌면 여기서 즉시 드러난다
        cx, cz = T["crest"]["x1"], T["crest"]["z"]
        w_z = HZ["water"]["z"] if cfg["hazard_stairs"] else T["walk"]["z"]
        s_int = (w_z - cz) / (14.0 - cx)
        s_rim = (T["walk"]["z"] - cz) / (fp_x0 - cx)
        print(f"[selfcheck] (5) 은닉 기하 — 마루 모서리 ({cx:+.2f}, {cz:.2f}) · "
              f"내부 은닉 s ≥ {s_int:+.4f} · 림 은닉 s ≥ {s_rim:+.4f} "
              f"· 실효 구속 = 내부")
        for dd in (6.0, 7.0, 9.0, 12.0):
            hmax = _h_max(dd)
            print(f"              d={dd:5.1f}  z(-d)={_ground_z_ref(-dd):.3f}  "
                  f"h_max={hmax:.3f}  H밴드[0.25,1.0] 통과율 "
                  f"{min(1.0, max(0.0, (hmax - 0.25) / 0.75)):.2f}")

        print(f"[selfcheck] sceneH6 {'통과' if ok else '실패'}")
        return ok

    # -------------------------------------------------------------------
    # 조립
    # -------------------------------------------------------------------
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()

    build_terrain(M)                                   # ① 경로 + ④ 은닉 (팔 불변)
    if cfg["hazard_stairs"]:                           # ② 위험
        build_hazard(M)
    else:
        build_flat_fill(M)

    # ③ 단서 — **어느 것도 hazard 분기 안에 있지 않다** (프림 위생 3 · s14 파라펫 교훈)
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
        #   이 씬의 장식은 전부 z ≥ 0 의 상부 지면에 앵커되므로 채움면 위에 그대로 선다 —
        #   sceneC2 가 겪은 "하부 앵커 드레싱이 사라지며 ground_z 가 움직인" 사고가
        #   **구조적으로 불가능**하다(GATED_ZONES 의 Dress 행이 데이텀과 교차 0).
        build_dressing(M)

    if not datum_selfcheck():
        raise SystemExit("sceneH6 self-check 실패")

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    if smoke_mode:
        n = sum(1 for _ in stage.Traverse())
        print(f"[SMOKE] sceneH6 조립 완료 · 프림 {n}개 · 조기 종료")
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
            fp = os.path.join(LOOKCHECK_DIR, f"sceneH6_{ts}.png")
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
    T = PARAMS["terrain"]
    a, r, c, st, w = T["approach"], T["rise"], T["crest"], T["steps"], T["walk"]
    if x <= r["x0"]:
        return a["z"]
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

    s_int : 마루 모서리를 스치는 시선이 **높이맵 격자 동단 x = 14.0** 의 수면에 닿기
            직전까지 허용되는 기울기. 이보다 가파르게 내려가면 수면 픽셀이 생기고
            `raw_vis.int_px > 0` 이 되어 strict-H 가 깨진다.
    s_rim : 같은 시선이 낙차 림(화강석 갓돌 상면)에 닿는 기울기.
            **[측정 260823_v3p5_h67probe] 이쪽이 실효 구속이다** — 파일 상단 참조.
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

    `crit="rim"`(기본) = 실측이 지목한 실효 구속 · `crit="int"` = 내부 조건(상한 모형).
    L ≤ 0 이면 카메라가 마루를 이미 지났다는 뜻이므로 은닉은 성립하지 않는다(−inf).
    """
    cx, cz, s_int, s_rim = _crest_slope()
    L = d + cx
    if L <= 1e-6:
        return float("-inf")
    return cz - _profile_z(-d) - (s_rim if crit == "rim" else s_int) * L


def _band_yield(d_lo, d_hi, h_lo, h_hi, n=800, crit="rim"):
    """d ~ LogU[d_lo, d_hi] · h ~ U[h_lo, h_hi] 에서 strict-H 가 되는 프레임 비율."""
    tot = 0.0
    lo, hi = math.log(d_lo), math.log(d_hi)
    for i in range(n):
        d = math.exp(lo + (hi - lo) * (i + 0.5) / n)
        hm = _h_max(d, crit)
        tot += min(1.0, max(0.0, (hm - h_lo) / (h_hi - h_lo)))
    return tot / n


def _geometry_selfcheck():
    """부팅 전 스모크가 부르는 CPU 검사. 종단면 연속성 · 낙차 · 은닉 기하 · 데이텀."""
    T, HZ = PARAMS["terrain"], PARAMS["hazard"]
    ok = True

    def chk(tag, cond, msg=""):
        nonlocal ok
        ok = ok and bool(cond)
        print(f"  [{'PASS' if cond else 'FAIL'}] {tag}" + (f" — {msg}" if msg else ""))

    print("=" * 70)
    print("sceneH6_berm_levee2 — CPU 자기검사 (pxr·GPU 불필요)")
    print("=" * 70)

    # 종단면 연속성: 0.05 m(= 높이맵 격자 피치) 간격의 인접 표고차가 계단 라이즈를
    #   넘지 않을 것. 넘으면 보행 불가능한 단차이거나 미신고 낙차다.
    prev, worst, worst_x = None, 0.0, None
    x = -12.0
    while x <= -0.80 + 1e-9:
        z = _profile_z(x)
        if prev is not None and abs(z - prev) > worst:
            worst, worst_x = abs(z - prev), x
        prev = z
        x = round(x + 0.05, 4)
    chk("종단면 연속 (0.05 m 격자)", worst <= T["steps"]["riser"] + 1e-6,
        f"최대 단차 {worst:.4f} m @x={worst_x} ≤ 라이즈 {T['steps']['riser']:.4f}")

    drop = HZ["coping"]["z_top"] - HZ["water"]["z"]
    chk("낙차 2.5–3.0 m", 2.5 <= drop <= 3.0, f"{drop:.3f} m")
    chk("관리통로 = 코핑 상면 동일 z",
        abs(T["walk"]["z"] - HZ["coping"]["z_top"]) < 1e-9,
        f"walk {T['walk']['z']} · coping {HZ['coping']['z_top']}")
    chk("반사실 채움면 = 관리통로 레벨",
        abs(HZ["fill"]["z"] - T["walk"]["z"]) < 1e-9, f"{HZ['fill']['z']}")

    fp_x0 = HZ["coping"]["x1"]
    chk("발자국 근단이 d=12 폴라 격자(12 m) 안", 12.0 + fp_x0 < 12.0,
        f"근단 x={fp_x0:+.2f} → d=12 에서 거리 {12.0 + fp_x0:.2f} m < 12.0")

    cx, cz, s_int, s_rim = _crest_slope()
    print(f"  [info] 마루 모서리 ({cx:+.2f}, {cz:.2f}) · 내부 은닉 s ≥ {s_int:+.4f} "
          f"· 림 은닉 s ≥ {s_rim:+.4f}")
    for dd in (2.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 12.0):
        hi_, hr_ = _h_max(dd, "int"), _h_max(dd, "rim")
        print(f"         d={dd:5.1f}  z(-d)={_profile_z(-dd):6.3f}  "
              f"h_max 내부={hi_:7.3f} 림={hr_:7.3f}  H밴드 통과율(림) "
              f"{min(1.0, max(0.0, (hr_ - 0.25) / 0.75)):.2f}  base(림) "
              f"{min(1.0, max(0.0, (hr_ - 0.25) / 1.65)):.2f}")
    p_base = _band_yield(1.2, 12.0, 0.25, 1.90)
    p_h = _band_yield(6.0, 12.0, 0.25, 1.00)
    p_h_int = _band_yield(6.0, 12.0, 0.25, 1.00, crit="int")
    exp_h = 24 * p_base + 48 * p_h
    print(f"  [info] 설계 수율(림 모형) base {p_base:.3f} (계획 가정 0.20) · "
          f"H {p_h:.3f} (계획 가정 0.60) · 내부 모형 H {p_h_int:.3f}")
    print(f"  [info] → A팔 72컷 기대 strict-H {exp_h:.1f} (계획 §3.5 기대 33.6) · "
          "실측 H밴드 7/8 = 0.875 [260823_v3p5_h67probe_A]")
    chk("설계 수율이 계획 기대치 이상", exp_h >= 33.6, f"{exp_h:.1f} vs 33.6")
    chk("퇴화 아님 (base 밴드에 V 프레임이 남는다)", p_base <= 0.75,
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

    print(f"\n  ⇒ sceneH6 CPU 자기검사 {'통과' if ok else '실패'}")
    print("=" * 70)
    return ok


if __name__ == "__main__":
    main()
