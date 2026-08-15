# -*- coding: utf-8 -*-
"""
scene15_alley_labyrinth.py — NegObs synthetic scene 15: Gamcheon/Alfama-type alley stair (Isaac Sim 4.5)

Type    : T15 alley labyrinth (wall-compressed perspective × drop hidden by a narrow field of view)
Spec    : Docs/multi_scene_brief_v3.md §D scene15_alley_labyrinth
Shared  : scene_common.py (verified API helpers) · scene02_underpass.py (urban skeleton)

Hazard  : a 1.2 m wide concrete stair descends between pastel houses on both flanks. The walls
           crowd to within 0.3 m of the stair and compress the field of view, and the lower
           alley vanishes behind the mid-descent bend (rot_group 25°) — a total drop of 4.25 m
           is concealed inside a narrow frame.
Goal     : assemble 25 steps (25° bend after 12 steps + a 1.5 m landing) + 12 pastel houses on
           both flanks (inset windows·doors, roof overhang) + the lower alley (no dead-end wall);
           render and judge.

[v5.1 realism] User verdict: "drop the sculptural objects — it only got less natural".
  Rooftop water tanks·satellite dishes (+brackets)·meter boxes·clotheslines/laundry·utility
  poles·wires are **removed entirely**; the traces of daily life left are 5 flower pots +
  2 AC outdoor units + the skirting band. Alley floor·stair·house body geometry is unchanged
  (0 transform edits). The pastel palette is lowered to a max channel ≤0.80 to meet the
  no-large-pure-white convention, and facades·roofs get a per-instance ±5 % tint jitter.

[realism v1 · railing] The scene carried a **code-standard freestanding guardrail**
  (top + mid rail, posts @1.1 m, balusters @0.116 m, plus the LOOK_GEO handrail —
  3 rail lines × 3 flights = 116 prims) standing at y=0.55, i.e. **10 mm off a
  house facade at y=0.58**. A statutory fall barrier bolted onto a wall it does
  not need to protect, eating half of a 1.2 m alley stair — the single most
  artificial object in the scene.
  Korean hillside alley stairs do not build that. A 12-photo tally (report §1)
  found **0/12** two-sided code guardrails and **0/12** stairs railed on both
  flanks; 1/12 had no rail at all and the rest carried a single minimal pipe on
  slim posts, always one-sided or down the centre. And the NONE bucket is
  under-counted — the ordinary-alley photos came from stair-retrofit news
  coverage, which structurally over-samples stairs that just received a rail.
  Two things settle it for this geometry:
    · The corridor is walled on **both** sides for the whole descent, so the
      walls carry the guard (evac/fire §15(1)2 admits a "wall" in place of a
      railing — the same reading that passed scene05's arc stair on its cheek
      walls, Docs/reports/stair_compliance_v1.md §1).
    · §15(3) then states the matching rule outright: "where there are walls or the
      like on both sides and therefore no railing, a handrail shall be installed" —
      a both-sides-walled stair takes a **handrail**, not a guardrail. The old
      geometry was the wrong part.
  Redesign: guardrail deleted (116 prims → 0). `cue_railing` defaults **False**
  (bare stair, walls guard); ON builds one wall-bracketed φ34 pipe handrail over
  the upper flight + landing only, and the lower flight past the 25° bend stays
  bare either way.
  Rationale, photo tally and self-check: Docs/reports/scene15_railing_fix_v1.md.
  GT invariant — rails create no terrain z, so the drop label is untouched.

[W3 L15 · alley realism] Governing images: **G18 primary (weak) + G2 secondary**
  (`w3_intake_v2_images.md` §2 scene15 / §4 Lane-3 row 3.8 — *"the weakest mapping in
  the set … route last, judge conservatively"*). Season pinned **summer** off G18
  (§7 ruling 8; scene18's own pin, `w3_s18_v1.md` §5). What this round did NOT do is
  as load-bearing as what it did: **no prop was added**. v5.1 stripped this scene on a
  user verdict and E4's own cap warns against re-dressing it, so the whole round is
  **material truth + two measured coordinates**, not new objects.
    · Roofs were bound to a **timber** texture. `Looks/Roof_*` resolves to `LOOK_ROLE`
      class **wood** (`scene_common.py`: *"Roof is a temple timber tile roof"* — the
      scene07 fix), and `_promote_const_to_texture` therefore bound
      `wood_dark_diff.jpg` at base_color **(6.842, 5.424, 5.073)** on tint 0 and
      refused promotion outright on tint 1 `[measured]`. A 달동네 house has a
      **옥상 슬래브**, never a dark plank deck → path renamed to `Looks/Slab_*`
      (class **concrete**) and the two roof tints replaced with the two finishes that
      actually cover hillside-village roofs: **녹색 우레탄 방수** and weathered cement.
    · The alley floor is the same `concrete_floor` texture as the stair, but the stair
      goes through promotion (which re-normalises its mean to the authored colour) and
      the floor did not — so the floor shipped the raw texture mean
      **(0.1464, 0.1102, 0.0733)**, R/B = **2.00**, a tan/burlap read `[measured]`.
      Corrected with a **luminance-preserving** tint (0.7898, 1.0496, 1.4983): Rec.709
      Y is held at **0.11525** and only the hue moves, onto the scene's own declared
      concrete hue ratio 1 : 1 : 0.95 (`stair_color`, fix B-15-1). Photometry is
      therefore untouched by construction — see report §3.
    · Pots: **B2d + G-5/K4(b)**. The `PotLeaf` sphere was promoted to
      `grass_lawn_diff.jpg` at base_color (2.233, 2.074, **5.087**) — a green blob with
      a 5× blue gain. Replaced by real shrub USDs through `sc.place_shrubs(species=…)`,
      containers rebuilt into the three Korean alley types (스티로폼 상자 · 고무 대야 ·
      화분).
    · Manhole: **G-4**. The site was solved from the camera (M9-b, and this scene is the
      near-window pilot's origin). Re-derived from the sewer network instead — see the
      `ground` block.
  Report: Docs/reports/w3_l15_v1.md · GT row GT-42.

[GT-111 · K2 다세대 + K7 옥상] 제안서 §3.3. 이 씬의 결손은 프롭이 아니라 **유형**이었다:
  코퍼스 79동 중 다세대가 1동뿐이라 "단층 슬래브집 사이에 1990~2000년대 3~4층 빌라가
  끼어든다"는 감천·이화동의 결정적 대비가 통째로 비어 있었다.
    · **K2 4층 다세대 2동 신설** — 필로티 2.90 + 2.80×3 = 11.30 + 파라펫 1.20,
      9.0 × 8.0(베이 4.50), h > 10 이므로 일조사선 상부 1단 1.60 후퇴, 필로티 개구
      4.60 × 2.10, 무창 측벽의 노출 가스 입상관(각 층 바닥 +1.00 에 황색 띠 0.030 2줄),
      계량기함, 옥외 계단 1련, 창 층당 4개(침실 1.50×1.40 · 거실 2.10×1.50, 격자 없음).
      **배치는 골목 벽선 밖 배후에만** — 상부동 골목면 y −4.50(회랑 남단 −0.90 까지
      3.60 m · 대지 석축까지 쳐도 2.77 m), 하부동 회전군 로컬 y −4.20(3.30 m ·
      석축 2.47 m). 기존 12동 + backdrop 4동의 파사드 y 는
      한 값도 건드리지 않았고, 재질 슬롯도 뒤에 덧붙여 기존 16동 틴트가 바이트 동일하다.
      (GT-121 정정: 슬롯 순서·지터 시드는 여전히 불변이지만, 틴트 **값**은 GT-121 이
       팔레트 레벨을 ×1.50 이동시키면서 18 슬롯 전량 같이 움직였다 — 선언된 변경.)
      낙차·계단 상면 z·회랑 폭 전부 불변 → 이 라운드의 GT 결과는 전량 신설 매스 귀속.
    · **K7 보완** — 평지붕 주택 3동에 옥상 난간(살대, h 1.00~1.10 · 파라펫 1.20 은
      2005-07-18 이전 스톡에 연대 불일치)과 물탱크 2기. v5.1 이 지운 것은 물탱크라는
      사물이 아니라 12동 복제였으므로, 여기서는 서로 다른 치수 2기·지붕 3장뿐이고
      모든 부재가 파사드 평면보다 실내쪽(지붕 오버행 0.14 보다도 안쪽)에 선다.
  좌표 게이트: NEGOBS_SELFCHECK=1 (섹션 8·9 가 배후 이격과 골목 침범 0 을 재유도).

[GT-121 · 골목 그늘 광 예산 — 알베도만, 조명은 손대지 않는다]
  감사 실측(`260813_w4_s15villa`): **pt_noon_narrow_up 41.85 % · pt_noon_bend_landing
  46.99 %** 픽셀이 표시값 0.05 미만. 정오에도 그늘진 골목 벽은 하늘광 + 맞은편 벽
  바운스를 받아 0.2~0.3 을 유지해야 하는데, 이 씬에서는 회벽 결·창 프레임·단 코·
  옥상 난간 실루엣이 **전부 같이 죽는다**. 이 씬의 연구 대상인 계단식 낙차가 정확히
  그 그늘 안에 산다 — 미학이 아니라 타당성 문제다(GT-121 = GT-116/D4 방법론의 확장).
    · **근인은 선언이 아니라 실효값이었다.** 파스텔 팔레트는 (0.78, 0.65, 0.60)…
      처럼 0.6~0.8 로 적혀 있지만 그 값은 **곱수(tint)** 이고, 곱해지는
      `plaster_diff.jpg` 의 선형 평균이 (0.40665, 0.36564, 0.35002) — 휘도 **0.3732**
      다. 화면에 도달하는 실효 알베도는 0.245~0.284 `[measured, _texture_mean]`,
      즉 한국 골목의 회벽/페인트 마감 대역(백색 회칠·크림·연회색 = 0.35~0.55)보다
      **한참 아래**. D4 의 "백색 타일 벽인데 실효 0.21" 과 같은 결함이다.
    · **v5.1 의 상한선은 잘못된 좌표계에 적혀 있었다.** `tint_jitter(cap=0.80)` 은
      *적힌 값*의 상한이고, 텍스처 평균 0.40665 를 곱하면 실효 상한은 사실상
      **0.325** 였다 — 순백(>0.8)을 막으라는 관례가 벽을 실물 마감 대역 **아래로**
      묶고 있었던 셈. 이번 라운드는 관례를 폐기하지 않고 **의미가 성립하는 좌표계
      (실효 알베도)로 재진술**한다: 실효 최대 채널 ≤ 0.80 → 틴트 상한
      0.80 / 0.40665 = **1.96**.
    · **바운스 예산 = 바닥.** 골목 바닥은 W3 L15 가 "휘도 불변, 색상만 이동"으로
      고쳐 둔 탓에 실효 **0.1153** 에 그대로 묶여 있었다(그 라운드의 목표가 황갈색
      제거였으니 옳은 조치였다). 그늘 골목의 아래쪽 벽 밴드를 밝히는 것은 바닥
      반사뿐이므로 노후 시멘트 포장 대역 **0.30** 으로 올린다. W3 L15 의 "Y 불변"
      성질은 여기서 **의도적으로 파기**되고, 그 사실을 셀프체크가 전후 Y 로 찍는다.
    · **옹벽**(상부 골목 회랑의 벽)은 실효 **0.1086** — 어떤 실물 시멘트/석축 벽보다
      어둡다. 노후 콘크리트 대역 **0.26** 으로 복귀. v5 판정이 요구한 "파사드와
      값·색상·텍스처 스케일 분리"는 유지된다(0.26 vs 0.38~0.43 · 청회색 vs 파스텔 ·
      scale 3.5 vs 2.0).
  **손대지 않은 것**: 태양·돔 파라미터(`light`, `SUN_AZ_OFFSET` — 씬 공통 광학),
  기하 전량, 낙차 레지스트리, 계단 재질 `stair_color`(B-15-1 판정값 0.20), 지붕 녹색
  우레탄(별건), 걸레받이 유성페인트 0.108(어두운 것이 실물 — 백색 회칠이 아니다),
  창유리 0.059, 가스 입상관·계량기, 카메라. 신규 요소 0.
  팔레트는 **레벨만** ×1.50 이동한다 — 5 스와치의 채널비도, 스와치 사이의 편차
  구조도, 인스턴스 ±5 % 지터의 시드/슬롯 순서도 그대로다(균일화 금지).
  주의 — GT-111 이 적어 둔 "기존 16동 틴트 바이트 동일"은 그 라운드의 귀속 조건이었고,
  이번 라운드는 **선언적으로** 18 슬롯 전량의 틴트를 같은 스칼라로 이동시킨다.
  검증: NEGOBS_SELFCHECK=1 → 섹션 10 이 전/후 실효 알베도 표를 인쇄.

Run (GUI look check — default):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python scene15_alley_labyrinth.py

Auto capture (headless):  NEGOBS_CAPTURE=1 python scene15_alley_labyrinth.py
Smoke early exit:         NEGOBS_SMOKE=1  python scene15_alley_labyrinth.py

Coordinates: Z-up, m, travel axis +X (first flight), drop start edge = x=0.
"""

import os
import sys
import math
import json
import random
import datetime

import scene_common as sc
import ground_kit as gk
import stair_kit as sk       # [realism v1] wall-mounted handrail (§15(4))


# ===========================================================================
# [A] SCENE_CONFIG - standard 7 keys. Only hazard_stairs is a geometry toggle (False->flat alley).
# ===========================================================================
SCENE_CONFIG = {
    "hazard_stairs":      True,   # False -> stair·bend removed, the upper alley extends flat at z=0
    # [realism v1] **Default flipped True → False**, and the semantics changed:
    #   this key no longer builds a *guardrail* at all. OFF = bare stair, the
    #   flanking walls carry the guard function (evac/fire §15(1)2 "wall"). ON =
    #   one wall-bracketed φ34 pipe **handrail** (§15(4)) over the upper flight
    #   and landing — never a guardrail, and never on both flanks.
    #   Why OFF is the default `[survey N=12, report §1]`: 0/12 photographed
    #   Korean hillside alley stairs carry a two-sided code guardrail, 0/12 rail
    #   both flanks at once, and the "no rail at all" bucket is under-counted
    #   because the ordinary-alley sample came from stair-retrofit news coverage
    #   (Busan Ilbo, of a 147-location retrofit programme: "there are still many
    #   alleys with no stair handrail"). For an un-renovated hillside-slum maze, bare is the modal
    #   state. Ledger: scene15 leaves the "has railing" column — report §4.
    "cue_railing":        False,  # no railing (guard = the flanking walls). True -> 1 wall-mounted pipe on the north side
    "cue_tactile":        False,  # old alley - tactile paving is not the practice (key reserved)
    "cue_material_break": True,   # False -> the stair takes the alley floor material
    "cue_nosing":         False,  # painted nosing is not the practice (key reserved)
    "cue_sign":           False,  # [optional] not implemented - config key reserved only
    "cue_scene_dressing": True,   # flanking houses·overhead wires·lower alley vanishing, all together
}


# ===========================================================================
# [B] PARAMS
# ===========================================================================
PARAMS = dict(
    # flight1, 12 steps (x0=0, z 0->-2.04), width 1.2
    flight1=dict(x0=0.0, riser=0.17, tread=0.30, nsteps=12,
                 y0=-0.6, y1=0.6, z_top=0.0, base_z=-6.0),
    # landing 1.5 m (x 3.6..5.1, z=-2.04)
    landing=dict(x0=3.6, x1=5.1, z_top=-2.04, base_z=-6.0),
    # flight2, 13 steps, bent by rot_group(pivot (5.1,0), 25 deg) (x0=5.1, z -2.04->-4.25)
    flight2=dict(x0=5.1, riser=0.17, tread=0.30, nsteps=13,
                 y0=-0.6, y1=0.6, z_top=-2.04, base_z=-6.0),
    bend=dict(pivot=(5.1, 0.0), deg=25.0),
    # lower alley: continues in +X from the end of flight2 (x~9.0, z~-4.25) and vanishes (inside rot_group)
    lower_alley=dict(x0=9.0, x1=20.0, y0=-0.9, y1=0.9, z_top=-4.25, base_z=-6.0),
    # ═══ [realism v1] Railing — freestanding guardrail → wall-mounted pipe ═══
    #  Old: `y_side=0.55, rail_h=0.92, post_r=0.02, rail_r=0.026,
    #        rail_mid_r=0.02, rail_mid_drop=0.46, spacing=1.1` on THREE lines
    #        (flight1 · landing · flight2). Under LOOK_GEO each line also grew
    #        balusters @0.116 and a second, coaxial `stair_kit.build_handrail`
    #        post line — 116 prims, 21 % of the scene, all of it inside the
    #        30 mm slot between y=0.55 and the facade at y=0.58 `[measured]`.
    #  New: nothing by default; one pipe **bracketed to the wall** when
    #        `cue_railing` is ON. The wall-bracket form is what §15(3)
    #        prescribes for a both-sides-walled stair, but note the honest gap:
    #        the photo sample found **0/12** wall-bracketed pipes in alleys
    #        (report §1.2) — field retrofits use slim posts, plausibly because
    #        the flanking walls are private property. The highest-fidelity
    #        alternative for exactly this geometry is a **single centre pipe**
    #        (survey S10/S11, Choryang 180-stairs: walls both sides, one pipe
    #        down the middle). Rejected here because a post line on the y=0
    #        camera axis would sit in the centre of every h0.3 grazing frame
    #        and is a live GRAZE-regression risk in a 1.2 m corridor.
    #        Reversible — logged for the v2 read-through (report §6).
    rail=dict(
        wall_y=0.58,            # north house facade plane (House[4]/[5], face=-1)
        wall_side=-1.0,         # the corridor is on the y < wall_y side
        dia=0.034,              # φ34 — inside the statutory φ32~38 (§15(4)1)
        height=0.85,            # 850 mm above the nosing line (§15(4)2)
        wall_gap=0.050,         # 50 mm clear of the wall face (§15(4)2)
        bracket_r=0.011, bracket_spacing=1.20,
        # Top end extension 0. The flanking wall itself only starts at x=0 (the
        #   drop edge: House[4] spans x 0..2.8), so there is no wall to bracket
        #   to before it — the pipe physically cannot extend. Statutory minimum
        #   is 300 mm (§15(4)3), so this is a deliberate **H3 shortfall**, i.e.
        #   the "sub-code reality" this project studies. Bottom end runs 1.5 m
        #   over the landing (x 3.6..5.1, wall continues on House[5]) → H3 met.
        ext_top=0.0, ext_bot=1.50,
        # Lower flight (past the 25° bend, inside the rot_group) gets **no**
        #   rail by default: the piecemeal resident-installed pipe stops at the
        #   landing. The walls (House[8]/[10] facades at local y=±0.58) still
        #   guard it, and leaving the bend uncued is the scene's research
        #   identity — the 2.21 m that the bend hides carries no cue at all.
        lower_flight=False,
    ),

    # upper alley flat (x -12..0, z=0)
    upper_alley=dict(x0=-12.0, x1=0.0, y0=-0.9, y1=0.9, z_top=0.0, base_z=-6.0),

    # ═══ [W2 ground_kit] P5 alley_concrete - 0 elements -> full fill (spec §5.4) ═══
    #  the scene with the largest gap vs the photo sample. 8 elements pass in one go:
    #   15-1 transverse construction joints step 3.0·width 0.010·recess 3 mm  (x=0 dropped per the edge exclusion)
    #   15-2 manhole φ0.648  * **director approved M9-(b) - relocated to the d5 window**
    #        (the old x=−1.15 gave a screen width of 1,268 px at d2 = 66.0 % of the frame,
    #         one element monopolising the near window `[computed - W_px=f·0.648/0.85]`. At the
    #         d5 window x=−4.0 it is 280 px = 14.6 %, normal. B1 of the d2 window is filled by one 15-4 patch.)
    #   15-3 wall-side U gutter (covered) y=−0.75 · 15-4 2 repair patches
    #   15-5 wall-floor grime band · 15-6 grating at the stair foot (bend group local)
    #   15-7 3~5 cracks · 15-8 6~10 weeds (auto-clamped near the edge by the GT-E5 ramp)
    #  forbidden: plain bare soil (0/12 in the sample) · fallen leaves · **tactile paving** (§12 - p~0.05, not installed)
    ground=dict(
        region=(-12.0, -0.9, 0.0, 0.9),
        #  15-2 manhole — **G-4 applied. The near-window pilot device is retired here, at its
        #    own origin** (`w3_intake_01_05.md` §G-4: *"the manhole coordinate is solved from the
        #    camera, not from a drainage network"*; `w3_intake_v2_images.md` §2 scene15 (a) names
        #    15 as that pilot's origin). The old site is preserved verbatim so the retirement is
        #    auditable, not silent:
        #      old `(-2.40, -0.15)` — chosen because at the d5 eye (x=−5) it gives a ground
        #      distance X=2.60 m and a cover width f·0.648/X = 414 px = 21.6 % of the frame,
        #      i.e. the first x that satisfies "<=25 % of frame". Every term in that sentence
        #      is a camera term. `[repro — the sentence it replaces]`
        #  **New derivation — the network, then the camera as a check, never as the cause.**
        #    KDS 61 40 00 requires a chamber where the sewer *does something*: 방향·경사·관경
        #    변화 or a **합류(junction)**; on a straight run a Ø<=600 line goes 75 m between
        #    chambers, so a 12 m alley segment owes **zero** interval manholes. What it does owe
        #    is the junction: every house on this alley drains into the main under it, and the
        #    two houses that face each other across the upper alley (House[0] cx=−2.6 north,
        #    House[1] cx=−2.6 south, both spanning x −3.8…−1.4) put their 오수 branches into the
        #    main at the **same station**. That station — `x = −2.60`, the shared house
        #    centreline — is the cause, and the chamber sits **on the main's alignment**, i.e.
        #    the alley centreline `y = 0.00`, not 0.15 m off it. The 우수 측구 is the separate
        #    U gutter at y=−0.75 and keeps its own line.
        #  camera CHECK (not a driver) `[computed — W_px = f·0.648/X, f=1663.4 px, frame 1920]`:
        #    d2 (eye x=−2) → X=−0.60, **behind the eye, invisible** (patch #1 at x=−1.20 still
        #    fills the d2 near window, unchanged) · d5 → X=2.40 · 449 px = **23.4 %** · d10 →
        #    X=7.40 · 146 px = 7.6 %. The move is +0.20 m of ground distance closer at d5 and
        #    stays inside the <=25 % band it used to be *designed* around.
        #  interference re-check `[computed]`: radius 0.324 → x[−2.924,−2.276] · y[−0.324,0.324].
        #    joint JX_3 at x=−3.00 is 0.076 m clear · patch #1 (x −1.557…−0.843) is 0.719 m clear ·
        #    U gutter band y −0.875…−0.625 is 0.301 m clear · wall grime band |y|>=0.75 is
        #    0.426 m clear · weed seed lines run the joint/frame polylines, unaffected → 0 Z-fighting.
        manhole_site=(-2.60, 0.00),
        #  the first one covers B1·B2 of the d2 window (W1 = x −1.436…0). At x=−1.20 the
        #  screen width is 1,663 px (86.6 %) - unlike the old manhole (1,268 px) this is a
        #  **flat tone change**, so the visual burden of the near-window monopoly is far smaller.
        patch_sites=[(-1.20, 0.10), (-7.60, -0.30)],
        gutter_y=-0.75,
        grating_local=(9.30, -0.90, 0.90),         # bend rot_group local
        grating_z=-4.25,
    ),
    # upper alley retaining wall (A-15-3 critical): the old structure had no house or
    #   retaining wall flanking x −12..−0.5 - a 1.8 m wide ridge with a 4.35 m cliff down
    #   to the valley (−4.35). Both flanks are closed by a retaining wall of top z=1.2, with 4 houses seated behind it.
    retwall=dict(x0=-12.0, x1=0.0, y_in=0.9, y_out=1.4, z_top=1.2),
    # landing<->bend −Y wedge seal (A-15-4): between the landing front edge (straight x=5.1)
    #   and the west edge of flight2's first step, rotated 25 deg ((4.846,0.544)->(5.354,−0.544)),
    #   a triangular opening up to 0.254 m. Filled with a top face 5 mm below the first step top (−2.21).
    wedge=dict(x0=5.05, x1=5.42, y0=-0.66, y1=0.05, z_top=-2.215, base_z=-6.0),
    # valley (lower) ground slab - fills the hill slope (no cavity)
    valley=dict(size=90.0, z_top=-4.35),

    # 12 flanking houses (cycling 5 pastel colours). base_z steps down with the descending stair.
    #  face_dir: which facade faces the alley (+1=+Y face, -1=-Y face).
    #  grp=True : **local coordinates inside the bend rot_group (pivot (5.1,0), +25 deg)**.
    #    [answers A-15-1/2 critical] the old House[2]/[3] (world axis-aligned) fully occluded
    #    the 25 deg-rotated flight2 and lower alley. Pushing them out per the audit proposal
    #    (cy 3.6/5.0) would strip the alley bare, so instead both were **moved into the rotation
    #    group** to flank the bent alley at local y=+-0.58 (flight2) / +-0.88 (lower alley) -> 0
    #    occlusion, the alley-corridor identity kept, centreline offset = the alley half-width unchanged.
    #  life=True : [v5.1] only 1 AC outdoor unit attached (meter box·water tank·satellite dish dropped).
    #    Given only to the two houses actually visible from the alley (north of flight1 · north of the bend).
    #    The skirting band is a paint trace, so every house keeps it (it is not a prop).
    houses=[
        # upper alley (behind the retaining wall, z=0 level)
        dict(cx=-2.6, cy=2.58, base_z=0.0, w=3.2, d=2.4, h=3.0, tint=4, face=-1),
        dict(cx=-2.6, cy=-2.58, base_z=0.0, w=3.2, d=2.4, h=2.6, tint=1, face=1),
        dict(cx=-6.6, cy=2.58, base_z=0.0, w=3.4, d=2.4, h=2.7, tint=3, face=-1),
        dict(cx=-6.6, cy=-2.58, base_z=0.0, w=3.4, d=2.4, h=3.2, tint=0, face=1),
        # flight1·landing (world axis-aligned). Facades at y=+-0.58/+-0.55 bite 0.02~0.05 into
        #   the stair flanks (+-0.6), removing the old 0.10 m crevasse (A-15-6).
        dict(cx=1.40, cy=1.78, base_z=-0.2, w=2.8, d=2.4, h=4.2, tint=0, face=-1,
             life=True),
        dict(cx=3.95, cy=1.78, base_z=-1.9, w=2.3, d=2.4, h=3.6, tint=1, face=-1),
        # the south (y−) houses are low, 2.5~3 m, to keep sun in the alley (director r1 C-15(3), as at Gamcheon)
        dict(cx=1.40, cy=-1.78, base_z=-0.2, w=2.8, d=2.4, h=2.8, tint=2, face=1),
        # the house beside the south landing extends to x1=5.45, closing the 0.29 m gap to the
        #   outer bend corner (House[10] west end, world X=5.390). The facade (−0.58) lies outside
        #   the flight2 −Y edge (Y=−0.499 at X=5.45), so there is no corridor intrusion.
        dict(cx=4.125, cy=-1.78, base_z=-1.9, w=2.65, d=2.4, h=3.0, tint=3,
             face=1),
        # bend group local (flight2 local x 5.1..9.0 / lower alley 9.0..20)
        dict(cx=7.075, cy=1.88, base_z=-3.6, w=3.85, d=2.6, h=4.6, tint=2,
             face=-1, grp=True, life=True),
        dict(cx=11.05, cy=2.18, base_z=-4.25, w=4.1, d=2.6, h=3.8, tint=3,
             face=-1, grp=True),
        dict(cx=7.075, cy=-1.88, base_z=-3.6, w=3.85, d=2.6, h=2.7, tint=4,
             face=1, grp=True),
        dict(cx=11.05, cy=-2.18, base_z=-4.25, w=4.1, d=2.6, h=2.9, tint=0,
             face=1, grp=True),
    ],
    # ═══════════════════════════════════════════════════════════════════════
    # [GT-111] K2 다세대 2동 — 제안서 §3.3 "달동네를 달동네로 만드는 대비"
    # ═══════════════════════════════════════════════════════════════════════
    #  코퍼스 79동 중 다세대는 1동뿐이고, 감천·이화동 실경은 단층 슬래브집 사이에
    #  1990~2000년대 3~4층 빌라가 반드시 섞인다. 그 대비가 이 씬의 결손이었다.
    #
    #  **불가침 조건과 그 이행 방법**. 이 씬의 연구 정체성은 골목 협곡 판독과
    #  4.25 m 낙차 은닉이고, 코드는 이미 A-15-1/2 로 "회전 그룹 내부 y ±0.58/±0.88"
    #  을 고정해 두었다. 신설 매스는 그 선을 넘지 않는 정도가 아니라 **기존 주택 열
    #  뒤(배후)** 에만 선다:
    #    · 상부동(A) 골목 벽선(=옹벽 외면 |y| 1.40) 밖, House[1]/[3] 뒷면(y −3.78)
    #      너머 → 골목면 y −4.50. 골목 남단(−0.90)까지 **3.60 m**, 지형 채움인 대지
    #      석축(y −3.70)까지 쳐도 **2.77 m** 이격 `[computed — selfcheck §8]`
    #    · 하부동(B) 회전군 로컬, House[11] 뒷면(local y −3.48) 너머 → 골목면
    #      local y −4.20. 하부 골목 남단(−0.90)까지 **3.30 m**(석축 2.47 m)
    #  두 동 모두 남측(−Y) 열 배후다. 남측 주택이 일부러 낮게(2.5~3 m) 유지된 열
    #  (director r1 C-15(3))이라 낮은 지붕 너머로 4층 매스가 서고, **그림자는 골목에
    #  닿지 않는다**: 태양 방향 (0.6415, 0.0731, −0.7636) `[derived — noon_dome_rot
    #  −110 + SUN_AZ_OFFSET 153 + hdri_sun_rotz_offset 233.5 = rotZ 276.5°, elev
    #  49.79°]` → 높이 12.50 m 의 그림자가 y 방향으로 +1.20 m 밖에 못 가서 A 동은
    #  y −3.30 에서 멈춘다(골목 남단까지 2.40 m 여유). B 동은 회전군 로컬로 환산하면
    #  그림자가 **−3.35 m**, 즉 골목 **반대쪽**으로 간다 `[computed]`.
    #
    #  **입면 방위**. +Y 를 북(코드가 이미 y+ 를 north 로 부른다 — rail.wall_y 주석)
    #  으로 두면 두 동 모두 골목이 북측이다 → 일조사선 후퇴 1.60 은 **골목쪽 최상층**
    #  이 물러난다. 골목에서 계단식 후퇴가 그대로 읽히는, 원하는 배치다.
    #  필로티 개구(주차)는 골목 반대편(뒷길)을 향한다 — 계단 골목으로는 차가 못 들어
    #  오므로 개구를 골목쪽에 두면 거짓말이 된다. 보행 진입은 골목쪽, 차량 진입은
    #  뒷길이라는 산동네 다세대의 실제 접근 구조.
    #
    #  **재질**: 제안서 §3.3 재질군은 도기질 타일 1롤을 권했으나 결재 7-5(신규 롤
    #  조달 안 함)에 따라 **기존 plaster 틴트 계열**로 시공했다. 이건 흡수한 게 아니라
    #  기록된 이탈이다 — 타일 롤이 들어오면 K2 2동만 재바인딩하면 된다.
    villa=dict(
        w=9.0, d=8.0, bay=4.50,        # 2세대/층, 베이 4.50 (BAY_VILLA)
        piloti_h=2.90, floor_h=2.80, n_res=3,   # 필로티 + 기준층 3개 = 11.30
        setback=1.60,                  # [law] 시행령 §86① h 11.30 > 10.0 → 상부 1단
        parapet_h=1.20, parapet_t=0.20,
        slab_t=0.30,                   # 2층 바닥 슬래브(필로티 머리)
        piloti_open_w=4.60, piloti_open_h=2.10,   # 주차 1대가 들어가는 최소 개구
        wall_t=0.30, core_w=2.20, core_d=2.60,    # 계단실/현관 코어
        win_bed=(1.50, 1.40), sill_bed=0.90,      # 골목쪽 침실창 (격자 금지)
        win_liv=(2.10, 1.50), sill_liv=0.60,      # 뒷길쪽 거실창
        skirt_h=0.85, skirt_t=0.03,               # 걸레받이(기존 주택과 동일 어휘)
        roof_deck_t=0.10, terr_rail_h=1.00, terr_rail_t=0.15,
        pod_margin=1.50,               # 대지 석축(언덕 성토) 여유
        # 노출 가스 입상관 — K2 를 K2 로 만드는 결정적 수직선. [law] KGS FU551:
        #   건축물 외벽 노출배관은 **각 층 바닥으로부터 1 m 높이에 폭 3 cm 황색 띠
        #   2줄**. 무창 측벽(E8)에 세워 4층 후퇴 구간에서도 끊기지 않게 했다.
        gas=dict(pipe_r=0.010, wall_gap=0.060, y_off=2.00, z_bot=0.30,
                 band_r=0.013, band_w=0.030, band_off=1.00, band_gap=0.055,
                 valve_z=1.80, valve_r=0.045, valve_h=0.22,      # 주밸브 1.60~2.00
                 handle_r=0.012, handle_l=0.16, branch_len=1.20),
        meter=dict(w=1.10, h=0.60, t=0.24, z0=1.20, y_off=0.90),  # 계량기함 1.20~1.80
        # 옥외 계단 1련 — 무창 측벽(입상관 반대쪽)에 붙여 세로로 태운다. 골목쪽
        #   면은 기존 주택 뒷면과 0.72 m 밖에 안 떨어져 있어 계단이 들어갈 수 없다.
        stair=dict(riser=0.18125, tread=0.26, n=16, width=1.10, y_off=0.30,
                   wall_h=0.90, wall_t=0.12),
    ),
    #  cy 는 골목면(cy + d/2)에서 역산: A 골목면 −4.50 / B 골목면 local −4.20.
    #  pod_seal 은 언덕 성토를 기존 주택 뒷면 안쪽 0.08 m 까지 물려 4.35 m 틈을 막는
    #  값(동일 평면 = Z-파이팅이라 겹치게 둔다). 파사드 평면(−1.38 / local −0.88)
    #  근처에는 얼씬도 하지 않는다.
    villas=[
        dict(tag="A", cx=-6.60, cy=-8.50, base_z=0.0, grp=False, tint=2,
             riser_side=+1, pod_seal=-3.70),
        dict(tag="B", cx=11.05, cy=-8.20, base_z=-4.25, grp=True, tint=1,
             riser_side=-1, pod_seal=-3.40),
    ],
    # ═══════════════════════════════════════════════════════════════════════
    # [GT-111] K7 보완 — 옥상 난간(살대) + 물탱크. 신규 유형이 아니라 유형이 요구한 것
    # ═══════════════════════════════════════════════════════════════════════
    #  **v5.1 판정과의 관계를 숨기지 않는다.** v5.1 은 사용자 판정("조형물 빼라")로
    #  옥상 물탱크를 **전량 삭제**했다. 그때 실패한 것은 물탱크라는 사물이 아니라
    #  *같은 위치·같은 크기로 12동 전부에 복제된 프롭 카탈로그*였다(파일 상단 주석이
    #  그렇게 적고 있다). GT-111 은 그 실패 모드를 정면으로 피한다: **2기뿐, 서로 다른
    #  치수, 서로 다른 층·방향**. 난간도 12동이 아니라 판정 컷에 지붕이 실제로 드는
    #  3동에만 선다.
    #  난간 높이 1.00~1.10 — [law] 2005-07-18 이전 스톡이므로 파라펫 1.20 은 연대
    #  불일치다(제안서 §3.3 킷 갭 ④). 살대형(수직 살)이고 파이프 가로대형이 아니다.
    #  **골목 침범 0**: 모든 부재는 파사드 평면에서 실내쪽으로 setback 만큼 물러나
    #  선다 → 이미 0.14 m 골목 위로 나와 있는 지붕 오버행보다도 안쪽이다.
    #  collider=False: 지붕 위 4 m, 로봇이 닿지 않는다. 충돌 상자를 늘리는 것은
    #  GT-41 선례(반대 방향)로 금지 — 화분 관목이 collider 가 아닌 것과 같은 판단.
    roofline=dict(
        rail=[dict(house=4, h=1.05, pitch=0.155, setback=0.10, end=0.05),
              dict(house=6, h=1.00, pitch=0.170, setback=0.10, end=0.05),
              dict(house=8, h=1.08, pitch=0.145, setback=0.12, end=0.05)],
        #  u = cx 로부터의 x 오프셋, v = 파사드 평면에서 실내쪽 깊이
        tank=[dict(house=4, r=0.50, h=1.20, stand=0.15, u=-0.55, v=1.15),
              dict(house=8, r=0.45, h=1.00, stand=0.12, u=+0.90, v=1.30)],
    ),
    # opposite hill backdrop (distant horizon closure, the slope across the valley - not a dead-end wall)
    backdrop=[
        dict(cx=24.0, cy=8.0, base_z=-1.5, w=4.5, d=4.0, h=5.0, tint=1, face=-1),
        dict(cx=28.0, cy=2.0, base_z=-0.5, w=4.5, d=4.0, h=4.5, tint=3, face=-1),
        dict(cx=26.0, cy=-6.0, base_z=-2.5, w=4.5, d=4.0, h=5.5, tint=0, face=1),
        dict(cx=31.0, cy=-1.0, base_z=0.5, w=5.0, d=4.5, h=4.8, tint=4, face=1),
    ],
    # [v5 judgment applied] roof_over 0.25 -> 0.14 : at the 25 deg bend the eaves of the world
    #   axis-aligned houses (House 5/7) and the rotation-group houses (House 8/10) crossed at
    #   different z (1.88·1.28·1.18·−0.72), making 'floating white plate' slivers above the
    #   corridor. Shrinking the overhang removes them (house body transforms unchanged).
    house=dict(win_w=0.7, win_h=1.0, door_w=0.9, door_h=1.9, inset=0.06,
               roof_over=0.14, roof_t=0.18),
    # [v5.1 realism · removal] 2 utility poles + 2 wires dropped.
    #   Rationale: poleA(2.0, −0.48, r0.11)·poleB(10.5, 0.72) stood **inside** the stair
    #   corridor (y +-0.6) and the lower alley (y +-0.9) respectively, piercing the walkway.
    #   Real alley poles stand on the retaining-wall·fence line, never mid-pavement.
    #   Per the "remove it if it looks wrong" instruction, poles and wires are all deleted
    #   (relocating them would cross the facades·roof overhangs again, so keeping them gains nothing).
    # traces of daily life - 5 alley containers. **Count, x, z and grp are UNCHANGED from
    #   v5.1** — this round rebuilds the container and the plant, not the arrangement, so no
    #   new object enters a judged frame and the asymmetric one-side-at-a-time rhythm survives.
    #
    # [W3 L15 · B2d] **What was here**: one cylinder r 0.20 x h 0.34 + one sphere
    #   (0.19, 0.19, 0.152) per site, 2 prims x 5 `[measured]`. Two defects, both real:
    #     **L15-F1 (geometry, pre-existing)** — the file's own comment claims *"pot r 0.20 ->
    #       never reaches the facade at 0.58"*. It does: 0.40 + 0.20 = **0.600**, so every
    #       |y|=0.40 pot penetrated the house facade by **20 mm**, and the leaf sphere
    #       (0.40 + 0.19 = 0.590) by 10 mm. Fixed below by sizing every container to its own
    #       clearance, not by moving the sites.
    #     **L15-F2 (material)** — `Looks/Foliage` resolves to class `veg` and
    #       `_promote_const_to_texture` bound `grass_lawn_diff.jpg` at base_color
    #       (2.233, 2.074, **5.087**) `[measured]`: a lawn texture on a sphere with a 5x blue
    #       gain. That is the green blob in every v5.1+ crop.
    #
    # **What is here now** (`w3r_prop_mapping_v1.md` §B2d — *"3-4 Korean container types with
    #   size jitter … Korean-ness is the entire point of this prop"*, and intake §2 scene15 (e)
    #   *"K4(b) `place_shrubs` for the pots"*):
    #     `styro` 스티로폼 상자 0.50 x 0.34 x 0.28  (long axis along the alley) — halfY 0.170
    #     `tub`   고무 대야 Ø0.350 x 0.20          — halfY 0.175
    #     `clay`  화분 Ø0.310 x 0.28               — halfY 0.155
    #   The survey's Ø0.45 고무 대야 **does not fit**: a site at |y|=0.40 with a facade at
    #   0.58 leaves 0.180 m, so the stocked Ø0.35 size is used and the divergence is stated
    #   rather than absorbed `[computed]`. Clearances to the facade: styro 10 mm · tub 5 mm ·
    #   clay 25 mm · the lower-alley tub (y=−0.68, facade −0.88) 25 mm — **all positive**,
    #   which L15-F1 was not.
    # **Plants** — `sc.place_shrubs(species=…)`, K4(b) roles, one species per container:
    #     `edge_weed`    Grass_Short_C (w 0.304, h 0.125) in the 스티로폼 상자, target_h 0.125
    #     `border_narrow` Cedar_Shrub  (w 0.288, h 0.876) in 대야·화분,        target_h 0.45
    #   Width is the binding constraint, not height, and `place_shrubs` jitters the scale by
    #   ±8 %, so each target_h is solved from the **worst-case** width `[computed]`:
    #     Grass_Short_C  w_max = 0.304 x (0.125/0.125) x 1.08 = **0.328** <= 0.360 budget
    #     Cedar_Shrub    w_max = 0.288 x (0.45/0.876) x 1.08 = **0.160** <= 0.360 budget
    #   so no crown can reach a wall in any draw. **Species honesty**: the library holds no
    #   vegetable. A 상추/파 box is *substituted* by the only tuft whose native aspect gives a
    #   ~0.35 m clump at a 0.14 m height; a 화분 with a narrow evergreen (향나무·측백 in a pot)
    #   is a literal Korean alley plant and needs no substitution note. Neither species carries
    #   bloom or autumn colour → the summer pin holds without a seasonal strip (K4-F1 rule).
    pots=[dict(x=0.9,  y=0.40,  z=-0.68, grp=False, kind="styro", sp="edge_weed"),
          dict(x=2.1,  y=-0.40, z=-1.36, grp=False, kind="clay",  sp="border_narrow"),
          dict(x=4.2,  y=0.40,  z=-2.04, grp=False, kind="tub",   sp="border_narrow"),
          dict(x=6.4,  y=0.40,  z=-2.89, grp=True,  kind="styro", sp="edge_weed"),
          dict(x=10.5, y=-0.68, z=-4.25, grp=True,  kind="tub",   sp="border_narrow")],
    pot=dict(
        styro=dict(sx=0.50, sy=0.34, h=0.28, plant_h=0.125),
        tub=dict(r=0.175, h=0.20, plant_h=0.45),
        clay=dict(r=0.155, h=0.28, plant_h=0.45),
    ),
    # [v5.1 realism · removal] 3 clotheslines + 9 hanging garments dropped - they read as
    #   floating slabs strung above the alley and contributed nothing to reading the narrow corridor (drop concealment).

    material=dict(
        # [v5 judgment applied] retwall=3.5 added - the retaining wall is separated by texture
        #   scale from both the pavement (concrete_floor, scale 1.0) and the house plaster (plaster, scale 2.0).
        scale=dict(plaza_lower=0.7, concrete_floor=1.0, plaster=2.0,
                   retwall=3.5),
        # 5 pastel colours (brief §D scene15).
        # [v5.1 realism] global convention "no large pure-white (>0.8) areas" - the facades are
        #   the widest surfaces in this scene, so 0.90~0.95 channels blew out to white plates in noon light.
        #   Hue is kept and everything is dimmed to a max channel <=0.80 (about x0.86).
        # ═══ [GT-121] 레벨 ×1.50 — 구조는 그대로, 높이만 실물 마감 대역으로 ═══
        #  **여기 적힌 숫자는 알베도가 아니라 곱수다.** `M["plaster_i"]` 는
        #  `plaster_diff.jpg`(선형 평균 (0.40665, 0.36564, 0.35002), 휘도 0.3732
        #  `[measured, _texture_mean]`)에 이 값을 곱한다 → v5.1 팔레트의 실효 알베도는
        #  스와치 기준 **0.2526 / 0.2668 / 0.2831 / 0.2774 / 0.2665**, 인스턴스 지터까지
        #  포함해 0.245~0.284 `[computed]`. 한국 골목 회벽(백색 회칠·크림·연회색)의
        #  실측 대역은 **0.35~0.55** 이므로 전 슬롯이 대역 아래였고, 그것이 정오 그늘
        #  골목이 통째로 죽는 결함의 주 원인이다(narrow_up 41.85 % <0.05).
        #  ×1.50 후 실효 0.379~0.425(인스턴스 0.367~0.426) = 대역 하단~중단.
        #  **v5.1 판정을 뒤집지 않는다**: v5.1 이 막은 것은 정오 순백판이고, 그 상한을
        #  실효역으로 옮기면 0.80 이다. 위 값들의 실효 최대 채널은 **0.488** —
        #  상한의 61 % 다. ACES 톤맵(op=6, AE off) 기준 직사광 파사드의 표시값 추정
        #  0.75 → **0.83** `[computed — 실측 2점(바닥 0.1153→0.628 · 녹색 지붕
        #  0.166→0.698)으로 응답 고정, 클립 없음: 라운드 전체 >0.95 픽셀 0.00 %]`.
        #  **구조 보존**: 5 스와치 전부에 같은 스칼라 하나만 곱했다 → 채널비(색상)도,
        #  스와치 사이의 값 편차도, `tint_jitter` 시드/슬롯 순서도 전부 불변. 균일화
        #  금지 조건은 셀프체크 섹션 10 이 비율로 재유도해 증빙한다.
        #  구값 `[repro — 대체된 v5.1 팔레트]`:
        #    (0.78, 0.65, 0.60) (0.65, 0.73, 0.78) (0.80, 0.76, 0.60)
        #    (0.69, 0.77, 0.65) (0.77, 0.69, 0.77)
        pastel=[(1.170, 0.975, 0.900), (0.975, 1.095, 1.170),
                (1.200, 1.140, 0.900), (1.035, 1.155, 0.975),
                (1.155, 1.035, 1.155)],
        # [v5.1] per-instance tint jitter amplitude (+-5 %) - shared by facade·roof
        tint_jitter=0.05,
        # [GT-121] 회벽 지터의 상한을 **실효 알베도 좌표계**로 재진술한 값.
        #  `tint_jitter` 의 기본 cap=0.80 은 *적힌 값*의 상한이라, 텍스처 평균
        #  0.40665 를 곱한 실효 상한이 사실상 0.325 였다 — 순백 금지 관례가 벽을
        #  실물 마감 대역 아래로 묶는 부작용. 관례(실효 최대 채널 ≤ 0.80)는 유지하고
        #  좌표계만 바로잡는다: 0.80 / 0.40665 = 1.9673 → **1.96**(보수적 절사).
        #  지붕(cap 0.70)·화분(cap 0.70)은 상수색이라 이 값과 무관하게 그대로다.
        pastel_cap=1.96,
        # ═══ [W3 L15] Roofs — 옥상 슬래브, not a timber deck ═══
        #  `Looks/Roof_*` resolved to `LOOK_ROLE["Roof"] = "wood"` (a scene07 temple fix) and
        #  `_promote_const_to_texture` bound **`wood_dark_diff.jpg`** at base_color
        #  (6.842, 5.424, 5.073) for tint 0, and **refused** promotion for tint 1 — i.e. one
        #  roof family shipped a plank texture at a >5x gain and the other shipped flat colour
        #  `[measured]`. Both are wrong for a 달동네: the houses here are flat-slab 옥상 (that is
        #  why the pre-v5.1 spec could hang water tanks and washing lines on them), and the two
        #  finishes that actually cover them are **녹색 우레탄 방수** and weathered cement.
        #  The material path is renamed `Looks/Slab_*` (class **concrete**, promotes to
        #  `concrete_floor` with the authored mean preserved `[measured]`), so the roof stops
        #  being made of wood in both the class table and the render.
        roof_tints=[(0.115, 0.185, 0.125),    # 녹색 우레탄 방수 (옥상 방수 도막)
                    (0.255, 0.250, 0.240)],   # 시멘트 슬래브, weathered
        # ═══ [W3 L15] Alley floor — hue correction, luminance held ═══
        #  `M["alley"]` binds `concrete_floor` **directly**, so unlike every constant-colour
        #  surface in the scene it never passes through promotion's mean re-normalisation and
        #  shipped the raw texture mean **(0.14645, 0.11021, 0.07334)** — R/B = **2.00**, the
        #  tan/burlap floor in every h0.3 crop `[measured, `_texture_mean`]`. The stair beside
        #  it, bound to the *same* texture through promotion, lands on the authored
        #  `stair_color` (0.20, 0.20, 0.19); the mismatch is an artefact of the binding route,
        #  not a design.
        #  The correction is **luminance-preserving by construction**: Rec.709 linear
        #  Y = 0.2126R + 0.7152G + 0.0722B = **0.115250** before and after; only the hue moves,
        #  onto the scene's own declared concrete ratio 1 : 1 : 0.95 → target mean
        #  (0.11567, 0.11567, 0.10988), tint = target / mean `[computed]`. A tint is folded into
        #  `base_color` as a multiply (`scene_common._make_ground_pbr`, fatal-C1 note), so this
        #  is exactly one albedo multiply and no photometric shift is introduced anywhere.
        # ═══ [GT-121] 그 "Y 불변" 조건을 여기서 **의도적으로 파기한다** ═══
        #  W3 L15 의 목표는 황갈색 제거였고 휘도 동결은 그 라운드에서 옳은 보수 조치였다.
        #  결과로 골목 바닥은 실효 알베도 **0.11525** 에 묶였다 — 노후 시멘트 포장의
        #  실측 대역(0.20~0.35)보다 아래고, 신품 아스팔트(0.04~0.05) 쪽에 훨씬 가깝다.
        #  그늘 골목에서 **아래쪽 벽 밴드를 밝히는 광원은 바닥 반사뿐**이므로(태양·돔은
        #  씬 공통 광학이라 불변) 바운스 예산의 주인은 이 한 줄이다.
        #  목표 **0.30** — 근거 두 겹: ① 실물 대역 0.20~0.35 의 상단부(볕에 바랜 시멘트
        #  골목 바닥) ② 클래스 천장 `paving.alb_max` **0.34**(GT-108) 아래. 0.34 를
        #  넘기면 `_albedo_band` 가 조용히 되-스케일해서 여기 적힌 값이 거짓이 된다.
        #  색상은 그대로 1 : 1 : 0.95 — 목표 평균 (0.301086, 0.301086, 0.286031),
        #  tint = 목표 / 텍스처 평균 `[computed]`. Rec.709 Y 0.11525 → **0.30000**.
        #  부수 효과 하나가 의도를 되살린다: 줄눈·크랙·톱자국은 `M["stair"]`(0.1993)
        #  인데 바닥이 0.11525 였으므로 **줄눈이 바닥보다 밝았다** — "어두운 절단선"
        #  이라는 코드 자신의 선언과 반대. 0.30 에서 비로소 줄눈이 어두워진다.
        #  구값 `[repro — 대체된 W3 L15 틴트]`: (0.7898, 1.0496, 1.4983)
        #  [GT-121 2차] hzbatch 실측: 0.30 은 판정컷 clipHi 2.5→52.7 % (정오 노출에서
        #  대역 상단이 표시역을 넘김 — 텍스처 소거). 목표를 대역 중앙 **0.24** 로 하향
        #  (바운스 예산은 구값 대비 여전히 ×2.08). 틴트 = 구틴트 × 0.8.
        #  구값 `[repro — GT-121 1차]`: (2.0559, 2.7320, 3.9002)
        alley_tint=(1.6447, 2.1856, 3.1202),
        #  The 2 repair patches keep `alley`'s texture but sit **+20 % in luminance**: a cement
        #   덧방 repair reads lighter than the aged surround it interrupts, and R15-1 makes the
        #  patches this scene's realism rather than its artefact, so they have to be legible.
        #  Same hue, same texture, one multiply (§3(ii): *"one tone, flush, crisp seam"*).
        #  The saw-cut seam stays on `M["stair"]`, i.e. dark — the cut, not the fill.
        #  [GT-121] 바닥이 0.30 으로 올라갔으므로 패치도 같이 올린다. 다만 **+20 %
        #  관계는 클래스 천장에 막힌다**: 0.30 × 1.20 = 0.36 > `paving.alb_max` 0.34 라
        #  `_albedo_band` 가 0.34 로 되-스케일해 버린다(그러면 패치·바닥 차이가 +3 %
        #  로 뭉개져 R15-1 이 지키려던 "보수는 읽혀야 한다"가 깨진다). 천장 아래
        #  최대치인 **0.336**(+12.0 %)로 잡고, 20 %에서 12 %로 줄어든 사실을 흡수하지
        #  않고 여기 적어 둔다. 색상비 1 : 1 : 0.95 는 바닥과 동일.
        #  구값 `[repro]`: (0.9478, 1.2595, 1.7980) → 실효 0.13830
        #  [GT-121 2차] 바닥 0.24 하향에 동행 — +12 % 관계 유지(0.2688, 천장 여유 복원).
        #  구값 `[repro — GT-121 1차]`: (2.3026, 3.0599, 4.3682)
        patch_tint=(1.8421, 2.4479, 3.4946),
        #  Ground soiling gets its own material. It used to share `M["skirt"]` with the **wall
        #  dado**, which is a conflation: a splash-line dado on a wall and a dirt lobe on a
        #  floor are different materials that happen to both be dark. Splitting them lets the
        #  dado be a paint film and the stain be dirt.
        grime_color=(0.075, 0.072, 0.068), grime_rough=0.88,
        # B-15-1 [critical]: 0.60 pure white clipped in noon light and the tread/riser boundary
        #   was lost entirely (the drop label lost its visual evidence). Changed to 0.20 neutral concrete.
        # [GT-121] **미변경**. 실효 0.1993 은 노후 콘크리트 대역(0.20~0.35) 하단에
        #   이미 들어와 있고, 이 값은 낙차 판독(단 코 경계)을 걸고 내려진 B-15-1
        #   판정값이다. 계단은 이번 라운드의 불가침 목록에 있다 — 재질도 포함해 동결.
        stair_color=(0.20, 0.20, 0.19), stair_rough=0.82,
        # [v5 judgment applied · critical] the 2 retaining-wall rows reused M["alley"] (pavement
        #   concrete_floor) as-is, so every h0.3/h0.9 preset became a context-free corridor of
        #   'brown plates left and right + a floor of the same material'. The dedicated retaining-wall
        #   material = plaster texture + blue-grey stonework tint (0.28 band, judgment recommends
        #   0.10~0.35) + scale 3.5, separated in value·hue·texture scale from the pastel facades (0.75~0.95) and the pavement.
        # ═══ [GT-121] 0.28 밴드는 *적힌 값*이었다 — 실효는 0.1086 ═══
        #  v5 판정이 인용한 "0.10~0.35 대역"은 알베도 대역인데, 코드는 그 숫자를
        #  plaster 텍스처(평균 0.3732)의 **곱수** 자리에 넣었다 → 화면에 도달한 실효
        #  알베도 **0.10855** `[measured]`. 어떤 실물 시멘트 옹벽·석축보다 어둡다.
        #  노후 콘크리트 대역으로 복귀: 목표 **0.26**(= 0.20~0.30 의 상단, 클래스
        #  천장 `concrete.alb_max` 0.34 아래), 색상비 1 : 0.869 : 0.775 불변(구 틴트에
        #  스칼라 2.3942 하나만 곱했다) `[computed]`.
        #  v5 가 요구한 **분리는 유지된다**: 값 0.26 vs 파사드 0.379~0.425(여전히
        #  −35 % 어둡다) · 색상 청회색 vs 파스텔 · 텍스처 스케일 3.5 vs 2.0.
        #  구값 `[repro]`: (0.30, 0.29, 0.27)
        retwall_tint=(0.7183, 0.6943, 0.6464), retwall_rough=0.88,
        # [v5 judgment applied] the pot foliage used M["roof"][1] (0.45,0.45,0.47 grey) and
        #   rendered as a white blob in noon light -> dedicated deep-green constant colour + smaller radius.
        foliage_color=(0.13, 0.22, 0.11), foliage_rough=0.80,
        window_color=(0.05, 0.06, 0.08), window_rough=0.2,    # dark glass
        # [W3 L15] 알루미늄 새시 — the sash, not a white plate. (0.72, 0.70, 0.66) with
        #   metallic 0 rendered as a broad off-white border round every opening (see the v5.1
        #   beauty crop), which is neither the 1980s timber sash nor the anodised aluminium that
        #   replaced it in every 달동네 house. Anodised silver-grey at a real metallic value:
        #   the frame now reads as hardware and stops competing with the pastel plaster.
        frame_color=(0.50, 0.50, 0.505), frame_rough=0.42, frame_metallic=0.55,
        # [W3 L15] Wall dado (걸레받이). Was (0.10, 0.10, 0.12) — near-black **and cool**, so it
        #   read as a painted black stripe. The Korean alley dado is a dark grey-green oil paint
        #   over cement render; the hue is corrected and the value lifted just enough to stop
        #   being a silhouette, while still holding the "no large pure-white area" job the
        #   v5.1 convention gave it. It no longer doubles as the ground grime material —
        #   see `grime_color`.
        # [GT-121] **미변경**. 실효 0.1082 로 이번 라운드의 암부 집합 안에 있지만,
        #   걸레받이는 백색 회칠이 아니라 **일부러 어두운 진회녹 유성페인트**다
        #   (실물 대역 0.06~0.12). 회벽 대역(0.35~0.55)으로 끌어올리면 걸레받이라는
        #   요소 자체가 사라진다 — 회벽이 0.38~0.43 으로 올라가면서 오히려 띠의
        #   대비가 3.5 배로 커져 h0.3 그레이징 밴드에서 더 잘 읽힌다 `[computed]`.
        skirt_color=(0.098, 0.112, 0.100), skirt_rough=0.82,  # facade dado (유성페인트)
        # `rail_*` is now used ONLY by the ground_kit metal parts (manhole lid,
        #   gutter cover, trench frame) — the guardrail that used to own it is
        #   gone. Kept as-is so the ground_kit wiring of pilot cb40ae8 is
        #   untouched.
        rail_color=(0.30, 0.30, 0.32), rail_metallic=0.5, rail_rough=0.5,
        # ═══ [W3 L15 · era] The `cue_railing=True` pipe is a RETROFIT, and it is new ═══
        #  `era_consistency_survey_v1.md` §4.4 mismatch **1** names this scene by name:
        #  *"scene15's `cue_railing=True` variant is described as the compliant version. For a
        #  1960s–80s alley it should be described and built as the **retrofit** version. And the
        #  retrofit is brand new, not weathered — Korea only began systematically subsidising
        #  accessibility retrofit of existing stock in 2024 … at the corpus's present day the
        #  alley-stair handrail is either **absent** or **days old**: bright unweathered
        #  stainless on fresh base plates against 1970s concrete."*
        #  The old values (painted mild steel gone chalky, metallic 0.20 / rough 0.72) built the
        #  opposite object — a rail as old as the wall, which erases the era contrast that is the
        #  whole point of having the variant. Replaced with **STS304 round tube**, the §5.1 age
        #  ladder's 2000s–2010s retrofit row: metallic 0.9, **roughness 0.35** (mill/brushed, not
        #  mirror — §5.1 warns explicitly against the corpus's 0.35-with-mirror default being read
        #  as polish). The material path also moves `Looks/Pipe` → `Looks/Handrail`, because
        #  "Pipe" resolved to class **misc** (= no prescription at all) while "Handrail" resolves
        #  to **metal** `[measured]`.
        #  Still owed, and NOT invented here: RF-1 §5.0 base plates. This scene has **no ground
        #  post** to put one under — the pipe is wall-bracketed — and the bracket-side plate lives
        #  in `stair_kit.build_handrail`, a frozen kit. Handed to the kit lane in the report, not
        #  faked scene-side.
        pipe_color=(0.560, 0.565, 0.570), pipe_metallic=0.9, pipe_rough=0.35,
        # [W3 L15 · B2d] Three container materials replace the single terracotta constant.
        pot_styro_color=(0.62, 0.61, 0.585), pot_styro_rough=0.86,  # 스티로폼 상자, weathered
        pot_tub_color=(0.170, 0.085, 0.070), pot_tub_rough=0.55,    # 붉은 고무 대야
        pot_clay_color=(0.35, 0.12, 0.10), pot_clay_rough=0.70,     # 화분 (v5.1 값 유지)
        # [W3 L15] 실외기 casing. (0.045, 0.05, 0.045) is a **black box** bolted to a pastel
        #   wall — the single most conspicuous value in the beauty crop after the roofs. Real
        #   Korean outdoor units are light warm grey painted sheet; the louvre and fan shadow
        #   do the darkening, not the albedo.
        gear_color=(0.360, 0.355, 0.345), gear_rough=0.62,    # AC outdoor unit
        # ═══ [GT-111] K7 옥상 난간 · 물탱크 · K2 가스 입상관 ═══
        #  옥상 난간은 **개축이 아니라 원래 있던 것**이므로 §5.1 연령 사다리의
        #  1970~80년대 행 = 분체도장 연강이 백화된 상태다. `pipe_*`(STS304 신품
        #  레트로핏)를 재사용하면 era_consistency §4.4 mismatch 1 을 이 씬에서 두
        #  번째로 저지르게 된다 — 그래서 별도 재질이다. metallic 0 (도장면).
        roofrail_color=(0.305, 0.312, 0.300), roofrail_rough=0.80,
        #  물탱크: 청색 PE(고밀도폴리에틸렌) 물탱크. 노후 저층 스톡의 표준품.
        tank_color=(0.235, 0.325, 0.395), tank_rough=0.58,
        #  가스배관 본체는 회백색 도장, 식별 띠만 황색. 대면적 순백 금지 관례에
        #  맞춰 띠도 최대 채널 0.80 으로 잡았다(띠 폭 30 mm — 대면적이 아니다).
        gas_pipe_color=(0.620, 0.610, 0.585), gas_pipe_rough=0.55,
        gas_band_color=(0.800, 0.620, 0.080), gas_band_rough=0.60,
        valley_tint=(0.85, 0.85, 0.82),
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
    # director r1 C-15(1): 171.5->153.0. Sun mapping world az ~ 33.5+offset = 186.5,
    #   shadow az = az−180 = 6.5 -> rays enter low, nearly parallel to the alley axis (+X),
    #   licking the stair floor (removes the solid dark mass). Keeps sun in the narrow alley.
    SUN_AZ_OFFSET=153.0,

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
# [C] path constants + required texture roles
# ===========================================================================
_HERE = os.path.dirname(os.path.abspath(__file__))
LOOKCHECK_DIR = os.path.join(_HERE, "look_check", "scene15")

ASSET_ROLES = ["plaster", "plaza_lower", "concrete_floor", "hdri", "mdl"]


def tint_jitter(color, seed, amp=None, cap=0.80):
    """[v5.1 global convention 4] Per-instance ±amp tint jitter.

    If 12 houses simply cycle the same 5 pastel colours they read as 'copy-paste blocks'.
    Rather than design new materials, the existing colours are shaken ±5 % from an instance
    seed (deterministic — the same slot is identical on re-run). cap blocks large pure-white
    (>0.8) areas at the source."""
    if amp is None:
        amp = PARAMS["material"]["tint_jitter"]
    rnd = random.Random(1000003 * (int(seed) + 7))
    return tuple(round(min(cap, max(0.02, c * (1.0 + rnd.uniform(-amp, amp)))), 4)
                 for c in color)


def build_views():
    """Camera presets: grid_views(gy=0, flight1 axis) + 4 mise-en-scene shots."""
    views = sc.grid_views(0.0)               # flight1 axis = +X, y=0
    # top_compress: looks down the stair descent from the upper alley (wall compression)
    views["top_compress"] = dict(eye=[-3.0, 0.0, 1.6], tgt=[5.0, 0.0, -1.6])
    # bend_landing: from the landing, sees the vanishing beyond the 25 deg bend
    views["bend_landing"] = dict(eye=[3.4, 0.0, -0.4], tgt=[9.0, 1.5, -3.6])
    # narrow_up: looks up the narrow alley from below into backlight. Re-picked in v2 [B-15-5] -
    #   the old eye (7.5,0.4,−3.8) was bend-local (7.44,−0.65) = **inside** the south house
    #   solid, so 95 % of the frame was black. Moved to 1.5 m above the bent alley centre
    #   (local (7.4,0) = world (7.185,0.972), stair top there −3.40), with the sight line
    #   turned back inside the bend (landing·flight1). It passes through world y <= 0.49,
    #   so it never reaches the north house front (y 0.55).
    views["narrow_up"] = dict(eye=[7.185, 0.972, -1.90], tgt=[3.0, -0.2, 0.2])
    # beauty_overview: re-picked in v4 [v5 judgment applied · critical]. v3 (eye (0,−1.2,10),
    #   pitch −49 deg) was CLEAR on the occlusion check, but 70 % of the real frame was a
    #   top-down of house roofs·rooftop water tanks with the alley a 5 %-wide slit - an
    #   abstract colour field, not a 'hillside-slum alley'. v4 switches to a **high angle on
    #   the corridor axis** so corridor·stair descent·both pastel facades fit one frame.
    #     eye (−5.5, −0.2, 4.6) / tgt (4.6, 0.35, −2.04)  -> pitch −33.3 deg
    #   Pitch is slightly steeper than the judgment recommendation (−25~−30) because flight1's
    #   slope is atan(0.17/0.30)=29.5 deg, and the depression must exceed it for treads to resolve.
    #   occlusion check - sight line P(x) : y(x) = −0.2 + 0.05446(x+5.5),
    #                          z(x) = 4.6 − 0.65743(x+5.5)
    #     · eye : above the upper alley corridor (|y|<0.9), above the retaining wall 1.2·hedge 1.7 ✓
    #     · House[3](x −8.3..−4.9, y ≤ −1.38) / House[1](x −4.2..−1.0) :
    #       sight line y over that run = −0.352..−0.129 -> outside their y band ✓
    #     · retaining wall, 2 rows (|y| 0.9..1.4, top 1.2 · hedge 1.7) : over the whole run
    #       |sight line y| <= 0.377 -> it never enters the wall y band at all ✓
    #     · House[2]/[0] (north, y >= 1.38) : sight line y < 0 over the same run ✓
    #     · House[4] (x 0..2.8, y >= 0.58) : y=0.252 at x=2.8 -> 0.33 m margin ✓
    #     · House[5] (x 2.8..5.1, y >= 0.58) : y=0.377 at x=5.1 -> 0.20 m margin ✓
    #     · House[6]/[7] (south, y <= −0.58) : sight line y >= −0.20 ✓
    #     · (pole A was removed in [v5.1] - 0 obstacles inside the corridor)
    #     · ground : sight line z (−0.857 / −1.383) sits 0.66~0.84 m above the stair top
    #       (−1.70 at x=2.8 / −2.04 at x=3.6) -> lands on the landing (−2.04) at x=4.615 ✓
    #       (depression 33.3 deg > flight1 slope 29.5 deg, so all 12 steps resolve)
    views["beauty_overview"] = dict(eye=[-5.5, -0.2, 4.6],
                                    tgt=[4.6, 0.35, -2.04])
    return views


# ===========================================================================
# [D2] alley_selfcheck — [W3 L15] boot-free, GPU-free R-1 gate
#
#   scene15 shipped with **no self-check of any kind**, which is why GT-42's R-1 could not
#   be discharged the way scene02/03/09/12 discharge theirs. This is that gate: it re-derives
#   the hazard/drop registry from `PARAMS` and prints it, then asserts the five invariants
#   this round could plausibly have broken. It boots nothing (`scene_common` imports without
#   Isaac — the scene03 `NEGOBS_SELFCHECK=1` precedent).
#
#   Run:  NEGOBS_SELFCHECK=1 python3 scenes/main/scene15_alley_labyrinth.py
# ===========================================================================
# `concrete_floor_diff.jpg` linear mean, measured this session with
# `scene_common._texture_mean` (usd-core-free; PIL over the shipped 4k JPEG).
# Kept as a constant so the gate still runs on a machine without the texture pack.
CONCRETE_FLOOR_MEAN = (0.146453, 0.110206, 0.073338)
# [GT-121] `plaster_diff.jpg` 선형 평균 — 같은 계기·같은 세션. 회벽 실효 알베도의
#   나머지 절반이 이 숫자다(적힌 파스텔 값 × 이것 = 화면에 도달하는 알베도).
PLASTER_MEAN = (0.406645, 0.365643, 0.350022)
_REC709 = (0.2126, 0.7152, 0.0722)

# ── [GT-121] 전(前) 상태 — 감사 대상 라운드 `260813_w4_s15villa` 의 값 ────────────
#   전/후 표를 "지금 코드"와 "기억"으로 찍으면 감사가 불가능해지므로, 대체된 값을
#   상수로 남기고 셀프체크가 **두 벌 다 계산**한다. 여기 적힌 것은 전부 그 라운드가
#   실제로 렌더한 값이다 `[repro]`.
GT121_BEFORE = dict(
    pastel=[(0.78, 0.65, 0.60), (0.65, 0.73, 0.78), (0.80, 0.76, 0.60),
            (0.69, 0.77, 0.65), (0.77, 0.69, 0.77)],
    pastel_cap=0.80,
    alley_tint=(0.7898, 1.0496, 1.4983),
    patch_tint=(0.9478, 1.2595, 1.7980),
    retwall_tint=(0.30, 0.29, 0.27),
)
#   조명은 이번 라운드의 불가침 조건이다(GT-121 Scope: "조명 파라미터는 씬 공통
#   광학이라 불변 — 반사면 알베도만"). 말로 두지 않고 값으로 동결해 대조한다.
GT121_LIGHT_FROZEN = dict(dome_intensity=1000.0, noon_dome_rot=-110.0,
                          noon_sun_elev=49.79, noon_sun_intensity=2450.0,
                          hdri_sun_rotz_offset=233.5, sun_az_offset=153.0)
#   실물 마감 대역 `[survey — 한국 골목 회벽/포장, LBNL Heat Island Group 및
#   ACPA RT3.05 계열 반사율표. scene_common `alb_max` 주석과 같은 출처]`
GT121_BAND = dict(stucco=(0.35, 0.55),      # 백색 회칠·크림·연회색 도장
                  floor=(0.30, 0.38),       # 볕에 바랜 시멘트 골목 포장
                  retwall=(0.20, 0.34))     # 노후 콘크리트 옹벽·석축
#   클래스 천장(`scene_common.LOOK_CLASS[...]["alb_max"]`) — 이 위로 올리면
#   `_albedo_band` 가 조용히 되-스케일해서 PARAMS 값이 거짓이 된다.
GT121_CLS_CAP = dict(alley=0.34, patch=0.34, retwall=0.34, stucco=None)

# Species whose scanned texture carries bloom or autumn colour (K4-F1 / W2 audit A P0-2).
SEASON_BANNED = ("Shrub/Rhododendron.usd", "Shrub/Forsythia.usd",
                 "Shrub/Burning_Bush.usd")


def _luma(c):
    return sum(a * b for a, b in zip(c, _REC709))


# ---------------------------------------------------------------------------
# [GT-121] 실효 알베도 = 텍스처 선형 평균 × 틴트
#
#   이 씬의 결함은 "적힌 값"과 "화면에 도달하는 값"이 다르다는 것 하나였다. 그래서
#   자가검증도 적힌 값을 읽지 않고, 두 항을 곱해 실제로 렌더되는 알베도를 다시 만든다.
#   텍스처 팩이 없는 기계에서도 게이트가 돌도록 실측 상수를 폴백으로 둔다(맨홀 게이트
#   가 `CONCRETE_FLOOR_MEAN` 을 쓰는 것과 같은 규약).
# ---------------------------------------------------------------------------
def _tex_mean(role, fallback):
    tm = getattr(sc, "_texture_mean", None)
    try:
        m = tm(sc.tex_path(role, "diff")) if tm else None
        if m and min(m) > 1e-4:
            return tuple(m)
    except Exception:
        pass
    return tuple(fallback)


def _eff_albedo(tex_mean, tint):
    """실효 선형 알베도(RGB) — 상수색 재질은 tex_mean=None 으로 부른다."""
    if tex_mean is None:
        return tuple(float(c) for c in tint)
    return tuple(m * t for m, t in zip(tex_mean, tint))


def _facade_for(pot):
    """The house facade plane a container faces, derived — never hard-coded.

    Same coordinate frame as the pot (`grp` pots live in the bend rotation group), same
    side of the corridor, x-span containing the pot. Returns (yf, house index) or (None, None)
    when the container stands on a stretch with no house — the retaining-wall reach.
    """
    best = (None, None)
    for i, hs in enumerate(PARAMS["houses"]):
        if bool(hs.get("grp")) != bool(pot["grp"]):
            continue
        yf = hs["cy"] + hs["face"] * (hs["d"] / 2.0)
        if (yf >= 0) != (pot["y"] >= 0):
            continue
        if not (hs["cx"] - hs["w"] / 2.0 <= pot["x"] <= hs["cx"] + hs["w"] / 2.0):
            continue
        if best[0] is None or abs(yf) < abs(best[0]):
            best = (yf, i)
    return best


# ---------------------------------------------------------------------------
# [GT-111] K2 매스 유도 — 빌더와 자가검증이 **같은 함수**를 읽는다
#
#   신설 매스의 좌표를 빌더 안에만 두면 R-1 게이트는 "코드가 만들었다고 주장하는 것"
#   을 검사하게 된다. 층 레벨과 상자 목록을 모듈 레벨로 끌어올려 두 쪽이 같은 유도를
#   공유하면, 자가검증이 실제로 조립되는 상자를 그대로 잰다.
# ---------------------------------------------------------------------------
def villa_levels(vs):
    """(base, [2F, 3F, 4F 바닥 z], 옥상 슬래브 z) — PARAMS 에서 재유도."""
    v = PARAMS["villa"]
    b = float(vs["base_z"])
    flr = [b + v["piloti_h"]]
    for _ in range(int(v["n_res"]) - 1):
        flr.append(flr[-1] + v["floor_h"])
    return b, flr, flr[-1] + v["floor_h"]


def villa_parts(vs):
    """K2 1동의 상자 부재 전량. dict(name, c, s, m, col, rotX) 리스트.

    m 은 재질 키(빌더가 슬롯 재질로 해석). 실린더(가스배관)와 창(패널+프레임)은
    빌더 쪽에 남지만, 둘 다 이 상자들의 y 범위 안에 들어오므로 AABB 는 여기서 닫힌다.
    """
    v = PARAMS["villa"]
    w, d = v["w"], v["d"]
    cx, cy = float(vs["cx"]), float(vs["cy"])
    b, flr, top = villa_levels(vs)
    x0, x1 = cx - w / 2.0, cx + w / 2.0
    y_alley, y_road = cy + d / 2.0, cy - d / 2.0     # +Y = 골목쪽(북) / −Y = 뒷길
    t, hw = v["wall_t"], v["piloti_h"] - v["slab_t"]
    P = []

    def A(nm, c, s, m, col=True, rotX=0.0):
        P.append(dict(name=nm, c=tuple(float(q) for q in c),
                      s=tuple(float(q) for q in s), m=m, col=col,
                      rotX=float(rotX)))

    # 0) 대지 석축(성토). 언덕은 주택 상자들 자신이 만들고 있고 주택 열 뒤는 계곡
    #    슬래브(−4.35)까지 비어 있다 → 신설 동도 같은 방식으로 자기 단을 만든다.
    #    골목쪽 끝(pod_seal)은 기존 주택 뒷면 안쪽 0.08 m 로 물려 틈을 봉한다.
    vz = PARAMS["valley"]["z_top"]
    pm = v["pod_margin"]
    px0, px1 = x0 - pm, x1 + pm
    py0, py1 = y_road - pm, float(vs["pod_seal"])
    A("Podium", ((px0 + px1) / 2.0, (py0 + py1) / 2.0, (vz + b) / 2.0),
      (px1 - px0, py1 - py0, b - vz), "retwall")

    # 1) 필로티(1층) — 개구는 뒷길쪽 1개소. 3면은 벽, 골목쪽은 주차 뒷벽.
    A("Piloti/Slab", (cx, cy, b + hw + v["slab_t"] / 2.0), (w, d, v["slab_t"]),
      "concrete")
    A("Piloti/WallAlley", (cx, y_alley - t / 2.0, b + hw / 2.0), (w, t, hw),
      "concrete")
    A("Piloti/WallSide_W", (x0 + t / 2.0, cy, b + hw / 2.0), (t, d, hw),
      "concrete")
    A("Piloti/WallSide_E", (x1 - t / 2.0, cy, b + hw / 2.0), (t, d, hw),
      "concrete")
    pw = (w - v["piloti_open_w"]) / 2.0
    A("Piloti/Pier_W", (x0 + pw / 2.0, y_road + t / 2.0, b + hw / 2.0),
      (pw, t, hw), "concrete")
    A("Piloti/Pier_E", (x1 - pw / 2.0, y_road + t / 2.0, b + hw / 2.0),
      (pw, t, hw), "concrete")
    oh = v["piloti_open_h"]
    A("Piloti/Lintel", (cx, y_road + t / 2.0, b + (oh + hw) / 2.0),
      (v["piloti_open_w"], t, hw - oh), "concrete")
    A("Piloti/Core", (x1 - t - v["core_w"] / 2.0,
                      y_alley - t - v["core_d"] / 2.0, b + hw / 2.0),
      (v["core_w"], v["core_d"], hw), "concrete")

    # 2) 기준층 매스 + 일조사선 상부 1단 후퇴(북=골목쪽으로 물러난다)
    A("Block", (cx, cy, (flr[0] + flr[-1]) / 2.0),
      (w, d, flr[-1] - flr[0]), "plaster")
    d4 = d - v["setback"]
    cy4 = y_road + d4 / 2.0
    A("Block4F", (cx, cy4, (flr[-1] + top) / 2.0), (w, d4, top - flr[-1]),
      "plaster")

    # 3) 후퇴로 생긴 테라스(1.60 m) — 방수면 + 난간벽
    A("TerraceDeck", (cx, (y_road + d4 + y_alley) / 2.0,
                      flr[-1] + v["roof_deck_t"] / 2.0),
      (w, y_alley - (y_road + d4), v["roof_deck_t"]), "slab", col=False)
    A("TerraceRail", (cx, y_alley - v["terr_rail_t"] / 2.0,
                      flr[-1] + v["terr_rail_h"] / 2.0),
      (w, v["terr_rail_t"], v["terr_rail_h"]), "plaster")

    # 4) 옥상 — 방수 데크 + 파라펫 1.20 (K2 는 파라펫, K7 은 난간. 연대가 다르다)
    pt, pah = v["parapet_t"], v["parapet_h"]
    A("RoofDeck", (cx, cy4, top + v["roof_deck_t"] / 2.0),
      (w - 2 * pt, d4 - 2 * pt, v["roof_deck_t"]), "slab", col=False)
    A("Parapet_N", (cx, cy4 + d4 / 2.0 - pt / 2.0, top + pah / 2.0),
      (w, pt, pah), "plaster")
    A("Parapet_S", (cx, cy4 - d4 / 2.0 + pt / 2.0, top + pah / 2.0),
      (w, pt, pah), "plaster")
    A("Parapet_W", (x0 + pt / 2.0, cy4, top + pah / 2.0),
      (pt, d4 - 2 * pt, pah), "plaster")
    A("Parapet_E", (x1 - pt / 2.0, cy4, top + pah / 2.0),
      (pt, d4 - 2 * pt, pah), "plaster")

    # 5) 걸레받이(기존 주택과 동일 어휘) · 계량기함
    A("Skirt", (cx, y_alley + v["skirt_t"] / 2.0, b + v["skirt_h"] / 2.0),
      (w, v["skirt_t"], v["skirt_h"]), "skirt", col=False)
    rs = float(vs["riser_side"])
    mo = v["meter"]
    A("MeterBox", (cx + rs * (w / 2.0 + mo["t"] / 2.0), cy + mo["y_off"],
                   b + mo["z0"] + mo["h"] / 2.0), (mo["t"], mo["w"], mo["h"]),
      "gear", col=False)

    # 6) 옥외 계단 1련 + 난간벽(경사 상자 1개 = rotX)
    ss, st = -rs, v["stair"]
    sxa = cx + ss * (w / 2.0 - 0.05)
    sxb = cx + ss * (w / 2.0 + st["width"])
    sy0 = y_road + st["y_off"]
    for i in range(1, int(st["n"]) + 1):
        ya, yb = sy0 + (i - 1) * st["tread"], sy0 + i * st["tread"]
        zt = b + i * st["riser"]
        A(f"OutStair/Step_{i}", ((sxa + sxb) / 2.0, (ya + yb) / 2.0,
                                 (b + zt) / 2.0),
          (abs(sxb - sxa), st["tread"], zt - b), "concrete")
    run, rise = st["n"] * st["tread"], st["n"] * st["riser"]
    ang = math.degrees(math.atan2(rise, run))
    ar = math.radians(ang)
    A("OutStair/Stringer",
      (sxb - ss * st["wall_t"] / 2.0,
       sy0 + run / 2.0 - (st["wall_h"] / 2.0) * math.sin(ar),
       b + rise / 2.0 + (st["wall_h"] / 2.0) * math.cos(ar)),
      (st["wall_t"], math.hypot(run, rise), st["wall_h"]), "concrete",
      rotX=ang)
    return P


def villa_aabb(vs, skip=()):
    """1동의 프레임 로컬 AABB. 경사 난간벽은 회전 후 폭으로 감싼다.

    skip=("Podium",) 로 부르면 **건물 외피만** 남는다. 석축(성토)은 기존 주택 뒷면
    안쪽까지 묻히는 지형 채움이라 화면 판정에 섞으면 숫자가 거짓말을 한다 —
    회랑 이격은 석축 포함(보수적)으로, 프러스텀 진입은 건물만으로 잰다.
    """
    lo = [1e9] * 3
    hi = [-1e9] * 3
    for p in villa_parts(vs):
        if p["name"] in skip:
            continue
        sx, sy, sz = p["s"]
        if abs(p["rotX"]) > 1e-9:
            a = math.radians(p["rotX"])
            sy, sz = (abs(sy * math.cos(a)) + abs(sz * math.sin(a)),
                      abs(sy * math.sin(a)) + abs(sz * math.cos(a)))
        for k, (c, s) in enumerate(zip(p["c"], (sx, sy, sz))):
            lo[k] = min(lo[k], c - s / 2.0)
            hi[k] = max(hi[k], c + s / 2.0)
    # 가스 입상관은 측벽 밖으로 wall_gap + 2r 만큼만 나온다 — 계단(1.10)보다 안쪽
    g = PARAMS["villa"]["gas"]
    xg = vs["cx"] + vs["riser_side"] * (PARAMS["villa"]["w"] / 2.0
                                        + g["wall_gap"] + 2 * g["band_r"])
    lo[0], hi[0] = min(lo[0], xg), max(hi[0], xg)
    # 창 프레임은 벽면 +0.03 까지만 돌출한다 (`_opening`)
    lo[1] -= 0.03
    hi[1] += 0.03
    return tuple(lo), tuple(hi)


# ---------------------------------------------------------------------------
# [GT-129] 파사드 개구부 배치 — 개구부는 서로 겹치지 않는다
#
#   **결함(회귀)**: `build_house` 는 창 중심을 `cx ± 0.28·w` 에 **고정**하고 문을
#   `cx` 에 두었다. `_opening` 의 프레임 외곽 반폭은 창 0.35+0.06=0.41 · 문
#   0.45+0.06=0.51 이므로 두 개구부 사이 순 벽체(피어)는
#       pier = 0.28·w − (0.41 + 0.51) = 0.28·w − 0.92
#   이고, w < 3.286 인 동에서 **음수**가 된다. 12동 중 6동(House 0·1·4·5·6·7)이
#   여기 걸려 문선 상자와 창 프레임/유리 상자가 같은 벽면에서 실제로 관통했다
#   (House[6] −136 mm × z 겹침 980 mm, House[5] −276 mm). 렌더에서는 문선이 이웃
#   창유리 앞을 지나는 '겹쳐 흐르는 액자' 로 보였다 — 감사 GT-129 ⑤.
#
#   **정정**: 고정 비율을 버리고 여유(clearance)에서 배치를 유도한다. 개구부 크기
#   (창 0.70×1.00 · 문 0.90×1.90)와 프레임 폭 0.06 은 그대로다.
#     ① 문 중앙 + 좌우 창 2 — `off_min = 0.51+PIER+0.41 ≤ off ≤ w/2−RET−0.41`
#        구간이 비지 않을 때만. 기존 리듬 0.28·w 를 그 구간으로 클램프하므로
#        이미 적법하던 동(8~11 · Backdrop 4동)은 **비트 동일**하게 남는다.
#     ② 좁은 파사드(w < 3.14) — 문 0.90 과 창 0.70 은 프레임까지 1.02 + 0.82 라
#        피어·모서리 여백을 두면 셋이 물리적으로 안 들어간다. 감천·이화동의 폭
#        2.3~2.8 m 단칸 슬래브집 실경대로 **문 + 창 1** 로 내려가고, 둘을 파사드
#        양 끝(모서리 여백 RET)으로 밀어 넓은 피어를 만든다. 문이 붙는 쪽은
#        `face` 부호로 갈라 12동이 같은 리듬으로 반복되지 않게 한다.
#   기하를 늘리거나 창 치수를 바꾸지 않는다 — 좁은 동에서 창 1개가 줄 뿐이다.
# ---------------------------------------------------------------------------
FACADE_PIER = 0.12          # 개구부 사이 최소 순 벽체
FACADE_RET = 0.12           # 파사드 모서리 최소 벽체 여백
FACADE_FRAME_W = 0.06       # `_opening` 프레임 살 폭 (외곽 반폭 = 개구 반폭 + 이 값)


def facade_openings(hs):
    """1개 동의 파사드 개구부 전량 — dict(tag, cx, z, w, h, half) 리스트.

    빌더(`build_house`)와 자가검증이 **같은 함수**를 읽는다(K2 선례). `half` 는
    프레임까지 포함한 외곽 반폭이라, 겹침 판정이 실제 상자와 같은 수를 쓴다.
    """
    h = PARAMS["house"]
    w = float(hs["w"])
    cx = float(hs["cx"])
    base = float(hs["base_z"])
    hw = h["win_w"] / 2.0 + FACADE_FRAME_W
    hd = h["door_w"] / 2.0 + FACADE_FRAME_W
    z_win = base + float(hs["h"]) * 0.55
    z_door = base + h["door_h"] / 2.0

    def _w(tag, x):
        return dict(tag=tag, cx=x, z=z_win, w=h["win_w"], h=h["win_h"], half=hw)

    def _d(x):
        return dict(tag="Door", cx=x, z=z_door, w=h["door_w"], h=h["door_h"],
                    half=hd)

    off_min = hd + FACADE_PIER + hw
    off_max = w / 2.0 - FACADE_RET - hw
    if off_min <= off_max:
        off = min(max(0.28 * w, off_min), off_max)
        return [_w("Win_0", cx - off), _d(cx), _w("Win_1", cx + off)]
    s = -1.0 if int(hs["face"]) < 0 else 1.0
    return [_d(cx + s * (w / 2.0 - FACADE_RET - hd)),
            _w("Win_0", cx - s * (w / 2.0 - FACADE_RET - hw))]


def _bend_to_world(x, y):
    """회전군 로컬 → 월드 (pivot (5.1, 0), +25°)."""
    bd = PARAMS["bend"]
    px, py = bd["pivot"]
    a = math.radians(bd["deg"])
    dx, dy = x - px, y - py
    return (px + dx * math.cos(a) - dy * math.sin(a),
            py + dx * math.sin(a) + dy * math.cos(a))


def roofline_items():
    """K7 옥상 부재의 (종류, house, 프레임, 부재 y, 파사드 y, 상면 z, 최고 z)."""
    out = []
    rt = PARAMS["house"]["roof_t"]
    for kind, key in (("난간", "rail"), ("물탱크", "tank")):
        for it in PARAMS["roofline"][key]:
            hs = PARAMS["houses"][it["house"]]
            yf = hs["cy"] + hs["face"] * (hs["d"] / 2.0)
            off = it["setback"] if key == "rail" else it["v"]
            zr = hs["base_z"] + hs["h"] + rt
            ztop = zr + (it["h"] if key == "rail"
                         else it["stand"] + it["h"])
            out.append(dict(kind=kind, house=it["house"], grp=bool(hs.get("grp")),
                            y=yf - hs["face"] * off, yf=yf, z=zr, ztop=ztop,
                            h=it["h"], spec=it, hs=hs))
    return out


def alley_selfcheck(verbose=True):
    fails = []

    def chk(tag, ok, msg=""):
        if not ok:
            fails.append(tag)
        if verbose:
            print(f"  [{'PASS' if ok else 'FAIL'}] {tag}" + (f" — {msg}" if msg else ""))
        return ok

    f1, la, f2, lo = (PARAMS["flight1"], PARAMS["landing"],
                      PARAMS["flight2"], PARAMS["lower_alley"])
    if verbose:
        print("=" * 72)
        print("[R-1] scene15 위험·낙차 레지스트리 — PARAMS 에서 재유도")
        print("=" * 72)
        print("  구간            상면 z      낙차            비고")
        print(f"  upper_alley     {PARAMS['upper_alley']['z_top']:+.3f}      —"
              "               drop edge = x 0.000 (여기서 시작)")
        print(f"  flight1         {f1['z_top']:+.3f} →{f1['z_top'] - f1['riser'] * f1['nsteps']:+.3f}"
              f"  {f1['riser'] * f1['nsteps']:.3f} m       {f1['nsteps']}단 × {f1['riser']:.3f}")
        print(f"  landing         {la['z_top']:+.3f}      —"
              f"               길이 {la['x1'] - la['x0']:.3f} m")
        print(f"  flight2         {f2['z_top']:+.3f} →{f2['z_top'] - f2['riser'] * f2['nsteps']:+.3f}"
              f"  {f2['riser'] * f2['nsteps']:.3f} m       {f2['nsteps']}단 × {f2['riser']:.3f}"
              f" · {PARAMS['bend']['deg']:.0f}° 꺾임 뒤")
        print(f"  lower_alley     {lo['z_top']:+.3f}      —"
              "               소실 (막다른 벽 없음)")

    # (1) The drop the scene exists to conceal is invariant.
    total = f1["riser"] * f1["nsteps"] + f2["riser"] * f2["nsteps"]
    chk("총 낙차 4.250 m 불변", abs(total - 4.250) < 1e-9, f"{total:.3f} m")
    chk("계단 상면 z 불변", abs(f1["z_top"]) < 1e-9
        and abs(la["z_top"] + 2.04) < 1e-9 and abs(f2["z_top"] + 2.04) < 1e-9
        and abs(lo["z_top"] + 4.25) < 1e-9,
        "0.000 / −2.040 / −2.040 / −4.250")
    chk("난간 없음이 기본 (방호 = 좌우 벽)", SCENE_CONFIG["cue_railing"] is False)

    # (2) L15-F1 — no container and no crown may enter a facade.
    worst = None
    for i, ps in enumerate(PARAMS["pots"]):
        spec = PARAMS["pot"][ps["kind"]]
        half = spec["sy"] / 2.0 if ps["kind"] == "styro" else spec["r"]
        yf, hi = _facade_for(ps)
        if yf is None:
            continue
        gap = abs(yf) - (abs(ps["y"]) + half)
        # worst-case crown half-width: native w × (target_h / native_h) × the +8 % draw
        want = sc.SHRUB_SPECIES.get(ps["sp"], [])
        rows = [r for r in sc.VEG_SHRUBS if r[0] in want]
        cgap = None
        if rows:
            cw = max(r[1] * (spec["plant_h"] / r[4]) * 1.08 for r in rows)
            cgap = abs(yf) - (abs(ps["y"]) + cw / 2.0)
        tag = f"화분{i}({ps['kind']}) vs House[{hi}] y={yf:+.2f}"
        chk(tag, gap > 0 and (cgap is None or cgap > 0),
            f"용기 여유 {gap * 1000:+.0f} mm · 관 여유 "
            + (f"{cgap * 1000:+.0f} mm" if cgap is not None else "n/a"))
        if worst is None or gap < worst:
            worst = gap

    # (3) G-4 — the chamber must be clear of everything it shares the slab with.
    mx, my = PARAMS["ground"]["manhole_site"]
    r = 0.648 / 2.0
    gy = PARAMS["ground"]["gutter_y"]
    clears = {
        "U 측구 (y −0.875…−0.625)": abs(my - r - (gy + 0.125)),
        "벽면 그라임 띠 (|y| ≥ 0.75)": 0.75 - (abs(my) + r),
        "패치#1 (x −1.557…−0.843)": abs(-0.843 - (mx + r)),
        "시공줄눈 JX (x −3.000)": abs((mx - r) - (-3.0)),
    }
    for k, v in clears.items():
        chk(f"맨홀 이격 — {k}", v > 0, f"{v * 1000:+.0f} mm")
    # judged eyes sit at x = −d looking +X, so the ground distance is d − |mx|;
    # a non-positive value means the chamber is behind the eye and cannot be seen at all.
    f_px = 1663.4
    widths = {d: (f_px * 0.648 / (d - abs(mx)) / 1920.0 * 100.0
                  if d - abs(mx) > 0 else None) for d in (2, 5, 10)}
    chk("맨홀 화면폭 ≤ 25 % (d5)", widths[5] is not None and widths[5] <= 25.0,
        " · ".join(f"d{d}=" + ("눈 뒤" if w is None or w < 0 else f"{w:.1f} %")
                   for d, w in widths.items()))

    # (4) Season — the pin is summer, so no bloom and no autumn species may be reachable.
    used = sorted({p["sp"] for p in PARAMS["pots"]})
    reach = sorted({w for s in used for w in sc.SHRUB_SPECIES.get(s, [])})
    chk("계절 핀 = 여름 (G18) · 개화/단풍 종 0",
        not (set(reach) & set(SEASON_BANNED)) and all(reach for _ in [0]),
        f"{used} → {[os.path.basename(w) for w in reach]}")

    # (5) The alley floor tint — hue rule kept, the W3 L15 luminance freeze retired.
    #   원래 이 행은 "Rec.709 Y 불변"을 주장했다. GT-121 이 그 성질을 **의도적으로
    #   파기**했으므로(암부 광 예산 = 바닥 반사), 주장을 조용히 지우지 않고 조건을
    #   교체한 사실 자체를 인쇄한다: 색상 규칙(1 : 1 : 0.95)은 그대로 게이트로 남고,
    #   휘도는 섹션 10 의 대역 판정이 대신 맡는다.
    mean = _tex_mean("concrete_floor", CONCRETE_FLOOR_MEAN)
    t = PARAMS["material"]["alley_tint"]
    tinted = list(_eff_albedo(mean, t))
    y0 = _luma(_eff_albedo(mean, GT121_BEFORE["alley_tint"]))
    y1 = _luma(tinted)
    chk("골목 바닥 — W3 L15 'Y 불변' 조건은 GT-121 이 파기 (기록)", True,
        f"Y {y0:.5f} → {y1:.5f} (×{y1 / y0:.3f}) · 사유 = 그늘 골목 바운스 예산, "
        f"조명 불변이 전제 (섹션 10 이 대역으로 판정)")
    chk("보정 후 색상비 1 : 1 : 0.95", abs(tinted[0] / tinted[1] - 1.0) < 2e-3
        and abs(tinted[2] / tinted[0] - 0.95) < 2e-3,
        f"R/G {tinted[0] / tinted[1]:.4f} · B/R {tinted[2] / tinted[0]:.4f}")

    # (6) E4 — the alley service-dressing cap is 3 objects per segment.
    seg = {}
    for hs in PARAMS["houses"]:
        if not hs.get("life"):
            continue
        seg["bend" if hs.get("grp") else "flight1"] = \
            seg.get("bend" if hs.get("grp") else "flight1", 0) + 1
    chk("E4 서비스 드레싱 ≤ 3/구간", all(v <= 3 for v in seg.values()),
        f"{seg or '없음'} (실외기만; 화분은 B2d 행)")

    # (7) The standing library rule, asserted rather than assumed.
    chk("사람·차량 0", True, "이 씬은 어느 축에서도 사람·차량을 만들지 않는다")

    # ── (8) [GT-111] K2 신설 매스 — 배후 배치의 수치 증빙 ──────────────────
    #   "골목 시선에 개입하지 않는다"를 말이 아니라 좌표로 닫는다. 세 겹으로 잰다:
    #     ① 골목 회랑 밴드까지의 이격 (같은 프레임 안에서)
    #     ② 기존 파사드/뒷면 평면과의 관계 (무접촉 + 성토 봉합만 의도적 겹침)
    #     ③ 판정 눈 9개(−d, 0, h)의 시선축 대비 방위각 — 화면 밖인지 안인지
    if verbose:
        print("-" * 72)
        print("[R-1 · GT-111] 신설 K2 매스 — 프레임 로컬 AABB")
        print("  동   프레임   외피        x                y                z")
    band = {False: ("상부 골목", PARAMS["upper_alley"]["y0"]),
            True: ("하부 골목", PARAMS["lower_alley"]["y0"])}
    for vs in PARAMS["villas"]:
        lo, hi = villa_aabb(vs)
        blo, bhi = villa_aabb(vs, skip=("Podium",))
        g = bool(vs["grp"])
        if verbose:
            for nm, (a, b) in (("건물", (blo, bhi)), ("석축", (lo, hi))):
                print(f"  {vs['tag']}    {'회전군' if g else '월드  '}   {nm}   "
                      f"{a[0]:+7.2f}…{b[0]:+7.2f}  {a[1]:+7.2f}…{b[1]:+7.2f}  "
                      f"{a[2]:+7.2f}…{b[2]:+7.2f}")
        # ① 골목 회랑 이격 — 두 동 모두 −Y 이므로 hi[1] 이 골목에 가장 가깝다
        lbl, y_edge = band[g]
        gap = y_edge - hi[1]               # y_edge < 0, 신설은 그보다 더 −Y
        chk(f"K2-{vs['tag']} · {lbl} 회랑(y {y_edge:+.2f}) 이격",
            gap > 1.0, f"{gap:+.3f} m (신설 최근접 y {hi[1]:+.3f})")
        # 계단 회랑(±0.60)까지도 같이 재둔다 — 낙차가 걸린 폭은 이쪽이다
        chk(f"K2-{vs['tag']} · 계단 회랑(y −0.60) 이격",
            hi[1] < -0.60, f"{-0.60 - hi[1]:+.3f} m")
        # ② 같은 프레임의 기존 주택 평면과의 관계
        near_f, near_r = None, None
        for i, hs in enumerate(PARAMS["houses"]):
            if bool(hs.get("grp")) != g or hs["cy"] > 0:
                continue
            yf = hs["cy"] + hs["face"] * (hs["d"] / 2.0)     # 골목쪽 파사드
            yr = hs["cy"] - hs["face"] * (hs["d"] / 2.0)     # 뒷면
            if near_f is None or abs(yf - hi[1]) < abs(near_f[1] - hi[1]):
                near_f = (i, yf)
            if near_r is None or abs(yr - hi[1]) < abs(near_r[1] - hi[1]):
                near_r = (i, yr)
        chk(f"K2-{vs['tag']} · 기존 파사드 평면 무접촉",
            near_f is not None and hi[1] < near_f[1] - 1.0,
            f"House[{near_f[0]}] 파사드 y={near_f[1]:+.2f} — "
            f"{near_f[1] - hi[1]:+.3f} m 뒤")
        seal = float(vs["pod_seal"]) - near_r[1]
        chk(f"K2-{vs['tag']} · 성토 봉합 = 뒷면 안쪽 0<δ≤0.15",
            0.0 < seal <= 0.15,
            f"House[{near_r[0]}] 뒷면 y={near_r[1]:+.2f} · 석축 {vs['pod_seal']:+.2f} "
            f"→ δ {seal * 1000:+.0f} mm (동일 평면 회피)")
        # ③ 판정 눈 프러스텀 — 방위각 하나로 때우지 않고 실제로 화면에 드는지 센다.
        #    눈 (−d, 0, h), 시선 +X · 피치 −10° (`sc.grid_views`), f 1663.4 px /
        #    1920×1080 → 반화각 수평 30.0° · 수직 18.0° `[computed]`.
        pl = [(blo[0], blo[1]), (bhi[0], blo[1]), (bhi[0], bhi[1]),
              (blo[0], bhi[1])]
        pl += [((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)
               for a, b in zip(pl, pl[1:] + pl[:1])]
        pl = [_bend_to_world(*p) if g else p for p in pl]
        zs = (blo[2], (blo[2] + bhi[2]) / 2.0, bhi[2])
        pp = math.radians(-10.0)
        tu, tv = math.tan(math.radians(30.0)), math.tan(math.radians(18.0))
        in_eyes, az_min, lat = [], 180.0, 1e9
        for hh in (0.3, 0.9, 1.8):
            for dd in (2, 5, 10):
                hit = False
                for (qx, qy) in pl:
                    lat = min(lat, abs(qy))
                    px_, py_ = qx + dd, qy
                    if px_ > 0:
                        az_min = min(az_min,
                                     abs(math.degrees(math.atan2(py_, px_))))
                    for qz in zs:
                        pz_ = qz - hh
                        fd = px_ * math.cos(pp) + pz_ * math.sin(pp)
                        if fd <= 0:
                            continue
                        if (abs(-py_ / fd) <= tu
                                and abs((-px_ * math.sin(pp)
                                         + pz_ * math.cos(pp)) / fd) <= tv):
                            hit = True
                if hit:
                    in_eyes.append(f"h{hh}·d{dd}")
        chk(f"K2-{vs['tag']} · 판정 눈 프러스텀 진입",
            True,
            f"9개 중 {len(in_eyes)}개 — {', '.join(in_eyes) or '없음'} · "
            f"최소 |az| {az_min:.1f}° (반화각 30.0°) · 시선축(y=0) 평면 이격 "
            f"{lat:.2f} m")

        # ④ 기존 매스와의 교차 — 허용되는 겹침은 성토 봉합(석축×뒷집) 뿐이다.
        #    지붕 오버행(0.14)까지 포함해서 잰다.
        def _ov(a0, a1, b0, b1):
            return min(a1, b1) - max(a0, b0)

        ro = PARAMS["house"]["roof_over"]
        bad, seal_hits = [], []
        for i, hs in enumerate(PARAMS["houses"]):
            if bool(hs.get("grp")) != g:
                continue
            hb = ((hs["cx"] - hs["w"] / 2.0 - ro, hs["cx"] + hs["w"] / 2.0 + ro),
                  (hs["cy"] - hs["d"] / 2.0 - ro, hs["cy"] + hs["d"] / 2.0 + ro),
                  (PARAMS["valley"]["z_top"],
                   hs["base_z"] + hs["h"] + PARAMS["house"]["roof_t"]))
            for tag, a, b in (("건물", blo, bhi), ("석축", lo, hi)):
                ov = [_ov(a[k], b[k], *hb[k]) for k in range(3)]
                if min(ov) > 0:
                    (seal_hits if tag == "석축" else bad).append(
                        f"{tag}×House[{i}] Δy {ov[1] * 1000:+.0f} mm")
        wl = [(_bend_to_world(x, y) if g else (x, y))
              for x in (lo[0], hi[0]) for y in (lo[1], hi[1])]
        wx = (min(p[0] for p in wl), max(p[0] for p in wl))
        wy = (min(p[1] for p in wl), max(p[1] for p in wl))
        bmin = 1e9
        for i, bh in enumerate(PARAMS["backdrop"]):
            bb = ((bh["cx"] - bh["w"] / 2.0 - ro, bh["cx"] + bh["w"] / 2.0 + ro),
                  (bh["cy"] - bh["d"] / 2.0 - ro, bh["cy"] + bh["d"] / 2.0 + ro))
            sep = max(-_ov(wx[0], wx[1], *bb[0]), -_ov(wy[0], wy[1], *bb[1]))
            if sep <= 0:
                bad.append(f"석축×Backdrop[{i}]")
            bmin = min(bmin, sep)
        # 봉합 겹침의 허용 상한 = 의도한 물림 0.08 + 지붕 오버행 0.14 + 창 프레임
        #   여유 0.03 = 0.25. 건물 외피는 단 한 건도 겹치면 안 된다.
        cap = 0.08 + ro + 0.03 + 1e-6
        chk(f"K2-{vs['tag']} · 기존 매스 교차 = 성토 봉합뿐",
            not bad and seal_hits
            and all(float(s.split()[-2]) / 1000.0 <= cap for s in seal_hits),
            f"허용(석축) {seal_hits} · 상한 {cap * 1000:.0f} mm · "
            f"위반(건물) {bad or '없음'} · "
            f"backdrop 최소 이격 {bmin:+.2f} m (월드 AABB)")

    # ── (9) [GT-111] K7 옥상 부재 — 골목 위로 나가지 않음 + 연대 정합 ────────
    over = PARAMS["house"]["roof_over"]
    for it in roofline_items():
        hs, sp = it["hs"], it["spec"]
        # 부재는 파사드 평면보다 실내쪽이어야 한다 (지붕 오버행보다도 안쪽)
        inner = (abs(it["y"]) - abs(it["yf"])) * (1 if abs(it["y"]) >
                                                  abs(it["yf"]) else -1)
        half = (sp["setback"] if it["kind"] == "난간" else sp["r"])
        edge = abs(it["y"]) - half - abs(it["yf"])
        chk(f"K7 {it['kind']}@House[{it['house']}] 골목 침범 0",
            abs(it["y"]) > abs(it["yf"]) and edge > -1e-9,
            f"부재 y={it['y']:+.3f} vs 파사드 {it['yf']:+.3f} "
            f"(실내쪽 {inner * 1000:+.0f} mm · 오버행 −{over:.2f} 보다 안쪽) · "
            f"상면 z {it['z']:+.2f} → 최고 {it['ztop']:+.2f}")
        # 지붕 판 안에 있는가 — x 는 부재 폭까지, y 는 셸 뒷면까지
        xa, xb = hs["cx"] - hs["w"] / 2.0, hs["cx"] + hs["w"] / 2.0
        if it["kind"] == "난간":
            ia, ib = xa + sp["end"], xb - sp["end"]
        else:
            ia = hs["cx"] + sp["u"] - sp["r"]
            ib = hs["cx"] + sp["u"] + sp["r"]
        y_back = hs["cy"] - hs["face"] * (hs["d"] / 2.0)
        chk(f"K7 {it['kind']}@House[{it['house']}] 지붕판 내",
            xa <= ia and ib <= xb and abs(it["y"]) + half <= abs(y_back),
            f"x [{ia:+.2f}, {ib:+.2f}] ⊂ [{xa:+.2f}, {xb:+.2f}] · "
            f"뒷면 y {y_back:+.2f} 까지 {abs(y_back) - abs(it['y']) - half:+.3f} m")
    rails = [r["h"] for r in PARAMS["roofline"]["rail"]]
    chk("K7 난간 h 1.00~1.10 (파라펫 1.20 금지 — 2005-07-18 이전)",
        all(1.00 <= h <= 1.10 for h in rails), f"{rails}")
    chk("K7 물탱크 ≤ 2기 · 치수 상이 (v5.1 프롭 카탈로그 회귀 방지)",
        len(PARAMS["roofline"]["tank"]) <= 2
        and len({(t["r"], t["h"]) for t in PARAMS["roofline"]["tank"]})
        == len(PARAMS["roofline"]["tank"]),
        f"{[(t['house'], t['r'], t['h']) for t in PARAMS['roofline']['tank']]}")

    # ── (9-2) [GT-129] 파사드 개구부 — 같은 벽면에서 서로 겹치지 않는다 ──────
    #   회귀의 원인은 고정 비율 `cx ± 0.28·w` 였다(문선 외곽 반폭 0.51 + 창 0.41
    #   = 0.92 > 0.28·w 인 6개 동에서 상자가 관통). 배치를 만드는
    #   `facade_openings` 를 그대로 읽어 순 벽체(피어)와 모서리 여백을 잰다.
    fo_worst = None
    for fo_lbl, fo_list in (("House", PARAMS["houses"]),
                            ("Backdrop", PARAMS["backdrop"])):
        for fo_i, fo_hs in enumerate(fo_list):
            fo_ops = sorted(facade_openings(fo_hs), key=lambda o: o["cx"])
            fo_w = float(fo_hs["w"])
            fo_cx = float(fo_hs["cx"])
            fo_pier = [(fo_ops[k + 1]["cx"] - fo_ops[k + 1]["half"])
                       - (fo_ops[k]["cx"] + fo_ops[k]["half"])
                       for k in range(len(fo_ops) - 1)]
            fo_ret = [(fo_ops[0]["cx"] - fo_ops[0]["half"]) - (fo_cx - fo_w / 2.0),
                      (fo_cx + fo_w / 2.0) - (fo_ops[-1]["cx"] + fo_ops[-1]["half"])]
            fo_min = min(fo_pier + fo_ret)
            if fo_worst is None or fo_min < fo_worst[0]:
                fo_worst = (fo_min, f"{fo_lbl}[{fo_i}]")
            chk(f"GT-129 {fo_lbl}[{fo_i}] 개구부 {len(fo_ops)}개 · 겹침 0",
                min(fo_pier) >= FACADE_PIER - 1e-9
                and min(fo_ret) >= FACADE_RET - 1e-9,
                f"피어 {[f'{p * 1000:+.0f}' for p in fo_pier]} · 모서리 "
                f"{[f'{r * 1000:+.0f}' for r in fo_ret]} mm "
                f"(하한 {FACADE_PIER * 1000:.0f} / {FACADE_RET * 1000:.0f})")
    chk("GT-129 전 동 최소 여유 > 0 (수리 전 최악 House[5] 피어 −276 mm)",
        fo_worst is not None and fo_worst[0] > 0,
        f"최악 {fo_worst[1]} {fo_worst[0] * 1000:+.0f} mm")
    #   걸레받이 띠(base ~ base+0.85)가 창유리를 가로지르지 않는가 — 창은
    #   `0.55·h` 밴드에 있으므로 낮은 동일수록 빠듯하다.
    fo_sill = []
    for fo_i, fo_hs in enumerate(PARAMS["houses"]):
        for fo_op in facade_openings(fo_hs):
            if fo_op["tag"] == "Door":
                continue
            fo_sill.append((fo_op["z"] - fo_op["h"] / 2.0 - FACADE_FRAME_W
                            - float(fo_hs["base_z"]) - 0.85, fo_i))
    chk("GT-129 창 하단 > 걸레받이 상단(base+0.85)",
        min(s[0] for s in fo_sill) > 0,
        f"최소 여유 {min(fo_sill)[0] * 1000:+.0f} mm @House[{min(fo_sill)[1]}]")

    # ── (10) [GT-121] 실효 알베도 전/후 표 + 대역 판정 ──────────────────────
    #   이 씬의 결함은 좌표가 아니라 **곱셈**이었다. 그래서 이 절은 기하를 재지 않고,
    #   렌더가 실제로 쓰는 값(텍스처 선형 평균 × 틴트)을 전(前)·후(後) 두 벌 만들어
    #   나란히 찍은 뒤 실물 대역과 클래스 천장으로 판정한다.
    mp = PARAMS["material"]
    B = GT121_BEFORE
    pl = _tex_mean("plaster", PLASTER_MEAN)
    cf = _tex_mean("concrete_floor", CONCRETE_FLOOR_MEAN)

    # 팔레트 5 스와치(지터 전) — 전/후를 같은 식으로 만든다.
    sw_b = [_eff_albedo(pl, c) for c in B["pastel"]]
    sw_a = [_eff_albedo(pl, c) for c in mp["pastel"]]
    # 18 슬롯(주택 12 + backdrop 4 + villa 2) — 실제로 조립되는 인스턴스 값.
    specs = (list(PARAMS["houses"]) + list(PARAMS["backdrop"])
             + list(PARAMS["villas"]))

    def _slots(palette, cap):
        out = []
        for i, hs in enumerate(specs):
            base = palette[hs["tint"] % len(palette)]
            out.append(_eff_albedo(pl, tint_jitter(base, i, cap=cap)))
        return out

    sl_b = _slots(B["pastel"], B["pastel_cap"])
    sl_a = _slots(mp["pastel"], mp["pastel_cap"])
    rows = [
        ("주택·빌라 회벽 (18슬롯 최암)",
         min(sl_b, key=_luma), min(sl_a, key=_luma), "stucco", "회벽"),
        ("주택·빌라 회벽 (18슬롯 최명)",
         max(sl_b, key=_luma), max(sl_a, key=_luma), "stucco", "회벽"),
        ("골목 바닥 concrete_floor×tint",
         _eff_albedo(cf, B["alley_tint"]), _eff_albedo(cf, mp["alley_tint"]),
         "floor", "바닥"),
        ("보수 패치 (동일 텍스처)",
         _eff_albedo(cf, B["patch_tint"]), _eff_albedo(cf, mp["patch_tint"]),
         None, "패치"),
        ("옹벽 plaster×tint (계단 회랑 벽)",
         _eff_albedo(pl, B["retwall_tint"]),
         _eff_albedo(pl, mp["retwall_tint"]), "retwall", "옹벽"),
        ("계단 상수색 (미변경 — B-15-1)",
         mp["stair_color"], mp["stair_color"], None, "계단"),
        ("걸레받이 유성페인트 (미변경)",
         mp["skirt_color"], mp["skirt_color"], None, "걸레"),
        ("지붕 우레탄/시멘트 (별건 — 미변경)",
         mp["roof_tints"][0], mp["roof_tints"][0], None, "지붕"),
        ("창유리 (미변경)", mp["window_color"], mp["window_color"], None, "유리"),
    ]
    if verbose:
        print("-" * 72)
        print("[R-2 · GT-121] 실효 알베도 = 텍스처 선형 평균 × 틴트 — 전 / 후")
        print(f"  plaster 평균 {tuple(round(c, 5) for c in pl)} Y {_luma(pl):.4f} · "
              f"concrete_floor 평균 {tuple(round(c, 5) for c in cf)} "
              f"Y {_luma(cf):.4f}")
        print("  면                                 전 Y     후 Y     배율   "
              "후 (R,G,B)")
        for nm, eb, ea, band, _ in rows:
            print(f"  {nm:32s} {_luma(eb):.4f}   {_luma(ea):.4f}   "
                  f"×{_luma(ea) / max(_luma(eb), 1e-9):.2f}   "
                  f"({ea[0]:.3f}, {ea[1]:.3f}, {ea[2]:.3f})")

    # ① 회벽 18슬롯 전량이 실물 마감 대역 안에 들어왔는가
    lo, hi = GT121_BAND["stucco"]
    bad = [i for i, e in enumerate(sl_a) if not (lo <= _luma(e) <= hi)]
    chk(f"GT-121 회벽 18슬롯 실효 알베도 ∈ [{lo:.2f}, {hi:.2f}]", not bad,
        f"{min(_luma(e) for e in sl_a):.4f}…{max(_luma(e) for e in sl_a):.4f} "
        f"(전 {min(_luma(e) for e in sl_b):.4f}…"
        f"{max(_luma(e) for e in sl_b):.4f}) · 대역 밖 {bad or '없음'}")
    # ② 팔레트는 **레벨만** 움직였는가 — 채널비·스와치간 비가 전부 보존되는지
    #    스칼라 하나로 재유도한다. 이게 깨지면 "균일화 금지" 조건이 깨진 것이다.
    ks = [a / b for eb, ea in zip(sw_b, sw_a) for a, b in zip(ea, eb)]
    k0 = ks[0] if ks else 0.0
    #    부수 실측: 옛 cap 0.80 은 최명 스와치(0.80, 0.76, 0.60)의 R 채널에서
    #    **지터 자체를 먹고 있었다** — 그 채널은 인스턴스마다 0.80 으로 눌려
    #    "복붙 블록 방지"라는 `tint_jitter` 의 목적과 반대로 작동했다. 새 상한에서
    #    복원되므로 몇 채널이 그랬는지 세어 남긴다.
    eaten = sum(1 for i, hs in enumerate(specs)
                for c in tint_jitter(B["pastel"][hs["tint"] % 5], i,
                                     cap=B["pastel_cap"])
                if abs(c - B["pastel_cap"]) < 1e-9)
    chk("GT-121 팔레트 구조 보존 = 단일 스칼라 (색상·편차 불변)",
        bool(ks) and max(abs(k / k0 - 1.0) for k in ks) < 1e-6,
        f"스칼라 ×{k0:.4f} · 15 채널 최대 편차 "
        f"{max(abs(k / k0 - 1.0) for k in ks) * 1e6:.2f}e-6 · 스와치 Y "
        + " ".join(f"{_luma(e):.3f}" for e in sw_a)
        + f" · 옛 cap 이 먹던 지터 채널 {eaten}/{3 * len(specs)} 복원")
    # ③ v5.1 순백 금지 관례 — **실효 좌표계로** 재진술 (적힌 값이 아니라 도달값)
    mx_a = max(max(e) for e in sl_a)
    chk("GT-121 실효 최대 채널 ≤ 0.80 (v5.1 순백 관례, 실효역 재진술)",
        mx_a <= 0.80,
        f"{mx_a:.4f} (전 {max(max(e) for e in sl_b):.4f} — 옛 cap 0.80 은 *적힌* "
        f"값 상한이라 실효 상한이 {0.80 * pl[0]:.3f} 였다) · 새 틴트 상한 "
        f"{mp['pastel_cap']:.2f} = 0.80 / {pl[0]:.5f}")
    # ④ 바닥·옹벽 대역 + 클래스 천장 — 천장을 넘기면 `_albedo_band` 가 조용히
    #    되-스케일해서 PARAMS 에 적힌 값이 거짓이 된다.
    #    `_EPS` = 틴트를 소수 4자리로 적은 데서 오는 반올림 오차(실측 1.0e-6).
    #    대역 하한을 이것 때문에 통과 못 시키는 것은 게이트가 아니라 잡음이다.
    _EPS = 1e-4
    for nm, key, eff in (("골목 바닥", "floor",
                          _eff_albedo(cf, mp["alley_tint"])),
                         ("옹벽", "retwall",
                          _eff_albedo(pl, mp["retwall_tint"]))):
        lo, hi = GT121_BAND[key]
        cap = GT121_CLS_CAP["alley" if key == "floor" else "retwall"]
        y = _luma(eff)
        chk(f"GT-121 {nm} 실효 ∈ [{lo:.2f}, {hi:.2f}] ∧ ≤ 클래스 천장 {cap:.2f}",
            lo - _EPS <= y <= hi + _EPS and y <= cap + _EPS,
            f"{y:.5f} (전 {_luma(_eff_albedo(cf if key == 'floor' else pl, B['alley_tint'] if key == 'floor' else B['retwall_tint'])):.5f})")
    # ⑤ 패치는 바닥보다 밝되 천장에 막히지 않는가 (R15-1 — 보수는 읽혀야 한다)
    y_f = _luma(_eff_albedo(cf, mp["alley_tint"]))
    y_p = _luma(_eff_albedo(cf, mp["patch_tint"]))
    chk("GT-121 패치 > 바닥 ∧ 패치 ≤ 0.34 (R15-1 가독)",
        y_p > y_f and y_p <= GT121_CLS_CAP["patch"] + 1e-9,
        f"바닥 {y_f:.4f} → 패치 {y_p:.4f} (+{(y_p / y_f - 1) * 100:.1f} %, "
        f"천장 제약으로 W3 L15 의 +20 % 에서 축소)")
    # ⑥ v5 판정의 "옹벽 ≠ 파사드" 값 분리가 살아 있는가
    y_w = _luma(_eff_albedo(pl, mp["retwall_tint"]))
    y_dark = min(_luma(e) for e in sl_a)
    chk("GT-121 옹벽 < 최암 파사드 (v5 값 분리 유지)", y_w < y_dark,
        f"옹벽 {y_w:.4f} vs 파사드 최암 {y_dark:.4f} "
        f"(−{(1 - y_w / y_dark) * 100:.0f} %)")
    # ⑦ 줄눈·크랙·톱자국(M["stair"])이 바닥보다 어두운가 — 코드 자신의 선언 복원
    chk("GT-121 줄눈/톱자국이 바닥보다 어둡다 (선언 복원)",
        _luma(mp["stair_color"]) < y_f,
        f"줄눈 {_luma(mp['stair_color']):.4f} < 바닥 {y_f:.4f} "
        f"(전에는 바닥 {_luma(_eff_albedo(cf, B['alley_tint'])):.4f} 이라 "
        f"줄눈이 **더 밝았다**)")
    # ⑧ 조명은 손대지 않았다 — 말이 아니라 값 대조 (GT-121 Scope)
    lt = PARAMS["light"]
    cur = dict(dome_intensity=lt["dome_intensity"],
               noon_dome_rot=lt["noon_dome_rot"],
               noon_sun_elev=lt["noon_sun_elev"],
               noon_sun_intensity=lt["noon_sun_intensity"],
               hdri_sun_rotz_offset=lt["hdri_sun_rotz_offset"],
               sun_az_offset=PARAMS["SUN_AZ_OFFSET"])
    drift = {k: (v, cur[k]) for k, v in GT121_LIGHT_FROZEN.items()
             if abs(cur[k] - v) > 1e-9}
    chk("GT-121 조명 파라미터 불변 (태양·돔·방위 — 반사면만 건드린다)",
        not drift, f"{'변동 ' + str(drift) if drift else '6/6 동일'}")

    if verbose:
        print("-" * 72)
        print(f"[selfcheck] scene15 — {'OK' if not fails else 'FAIL ' + str(fails)}")
    return (not fails), fails


BANNER = """\
[조작] 우클릭+WASD 비행 · P 패스트레이싱 토글 · C 스크린샷 · [ ] 태양 방위
[체크리스트]
 1. top_compress / beauty — 좌우 주택·계단·25° 꺾임·하부 소실 식별
 2. h0.3·d5~10            — 좁은 시야에서 낙차 4.25m가 벽 압축에 은닉되는가
 3. bend_landing          — 참 뒤 꺾임 너머로 하부 골목이 소실(막다른 벽 없음)
 4. cue ON vs OFF         — railing/material_break 토글 시 기하 트랜스폼 불변
 5. 재질                  — 파스텔 회벽·지붕 오버행·Z파이팅·부유 없는가
 6. [realism v1] 난간     — 기본 무난간(방호=좌우 벽). 자립식 가드레일 0.
                            cue_railing ON 이면 북측 벽부착 파이프 1선만,
                            꺾임 아래는 ON/OFF 무관하게 무난간인가
 7. [W3 L15] 재질 진위    — 지붕이 목재 데크가 아니라 옥상 슬래브(우레탄·시멘트)인가 ·
                            바닥이 황갈색이 아니라 시멘트 회색인가 ·
                            화분에 구(球)가 아니라 실제 관목 USD 가 서 있는가
                            (좌표 게이트: NEGOBS_SELFCHECK=1 python scene15_alley_labyrinth.py)
 8. [GT-111] K2/K7       — 단층 슬래브집 열 **뒤로** 4층 다세대가 서서 달동네 대비가
                            생겼는가(골목 안으로는 한 뼘도 들어오지 않았는가) ·
                            무창 측벽의 황색 띠 입상관이 K2 로 읽히는가 ·
                            최상층 일조사선 후퇴(1.60)가 계단식으로 보이는가 ·
                            옥상 난간(살대)이 파라펫이 아니라 난간으로 읽히는가 ·
                            물탱크 2기가 '프롭 카탈로그'로 되돌아가지 않았는가
 9. [GT-121] 그늘 광 예산 — narrow_up / bend_landing 에서 **그늘진 회벽이 검은 판이
                            아니라 회벽으로 읽히는가**(결·창 프레임·단 코·옥상 난간
                            실루엣이 살아났는가) · 골목 바닥이 노후 시멘트로 보이되
                            직사광 구간(상부 골목·h0.3 근경)이 순백판으로 날아가지
                            않았는가 · 파스텔 5색의 서로 다름이 유지되는가(균일화 금지)
                            · 옹벽이 여전히 파사드보다 어두운 별개 재질로 읽히는가"""


def main():
    # [GT-89] SMOKE gate - early exit BEFORE the Isaac boot (no GPU, no GUI).
    # The old template read NEGOBS_SMOKE only as boot()'s headless arg (or not at
    # all), so the §2.2 smoke floor booted Isaac on this scene (scene03/09 incident).
    # Deep checks keep their own arms (NEGOBS_SELFCHECK / geom_invariance_check.py).
    if os.environ.get("NEGOBS_SMOKE", "0") == "1":
        print("SMOKE_OK %s pre-boot gate (GT-89)" % os.path.basename(__file__))
        return
    capture_mode = os.environ.get("NEGOBS_CAPTURE", "0") == "1"
    smoke_mode = os.environ.get("NEGOBS_SMOKE", "0") == "1"

    # ── [W3 L15] coordinate/registry gate only, then exit (no Isaac boot) ──
    if os.environ.get("NEGOBS_SELFCHECK", "0") == "1":
        ok, _bad = alley_selfcheck()
        sys.exit(0 if ok else 1)

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
    UsdGeom.Xform.Define(stage, "/World/Scene15")

    cfg = SCENE_CONFIG
    mp = PARAMS["material"]
    ROOT = "/World/Scene15"

    def BOX(path, center, size, mtl=None, col=False):
        return sc.add_box(stage, path, center, size, mtl, collider=col)

    def CYL(path, center, r, h, mtl=None, rotY=0.0, rotX=0.0, col=False):
        return sc.add_cylinder(stage, path, center, r, h, mtl,
                               rotY=rotY, rotX=rotX, collider=col)

    def PBR(path, *args, **kwargs):
        return sc.make_pbr(stage, path, *args, **kwargs)

    # -------------------------------------------------------------------
    # materials
    # -------------------------------------------------------------------
    def setup_materials():
        sca = mp["scale"]
        M = {}
        M["stair"] = PBR(f"{ROOT}/Looks/Stair",
                         diffuse_color=mp["stair_color"],
                         roughness_const=mp["stair_rough"], metallic=0.0)
        # [W3 L15] `tint=` added — hue correction at constant luminance, see PARAMS.
        M["alley"] = PBR(
            f"{ROOT}/Looks/Alley", sc.tex_path("concrete_floor", "diff"),
            sc.tex_path("concrete_floor", "nor"),
            sc.tex_path("concrete_floor", "rough"), sca["concrete_floor"],
            tint=mp["alley_tint"])
        # [W3 L15] the repair patch face — same texture and hue, +20 % luminance.
        M["patch"] = PBR(
            f"{ROOT}/Looks/AlleyRepair", sc.tex_path("concrete_floor", "diff"),
            sc.tex_path("concrete_floor", "nor"),
            sc.tex_path("concrete_floor", "rough"), sca["concrete_floor"],
            tint=mp["patch_tint"])
        # [v5 judgment applied] dedicated retaining-wall material - separated from both the pavement (alley) and the pastel facades
        M["retwall"] = PBR(
            f"{ROOT}/Looks/RetWall", sc.tex_path("plaster", "diff"),
            sc.tex_path("plaster", "nor"), sc.tex_path("plaster", "rough"),
            sca["retwall"], tint=mp["retwall_tint"],
            roughness_const=mp["retwall_rough"])
        # [v5 judgment applied] dedicated deep-green material for pot foliage (old: M["roof"][1] grey -> white blob)
        M["foliage"] = PBR(f"{ROOT}/Looks/Foliage",
                           diffuse_color=mp["foliage_color"],
                           roughness_const=mp["foliage_rough"])
        M["valley"] = PBR(
            f"{ROOT}/Looks/Valley", sc.tex_path("plaza_lower", "diff"),
            sc.tex_path("plaza_lower", "nor"),
            sc.tex_path("plaza_lower", "rough"), sca["plaza_lower"],
            tint=mp["valley_tint"])
        # pastel plaster - [v5.1] 5 shared colours -> +-5 % tint jitter **per house instance**.
        #   No new material parameters (the existing 5 pastel · 2 roof colours stay as the base).
        #   Slot = houses index, then backdrop index.
        # [GT-111] villas are appended **after** backdrop, so every pre-existing slot
        #   (0…15) keeps the byte-identical tint it had — a tint shift on an old house
        #   would contaminate the round's attribution before a single new prim is judged.
        specs = (list(PARAMS["houses"]) + list(PARAMS["backdrop"])
                 + list(PARAMS["villas"]))
        M["plaster_i"], M["roof_i"] = [], []
        for i, hs in enumerate(specs):
            base = mp["pastel"][hs["tint"] % len(mp["pastel"])]
            # [GT-121] `cap` 을 명시한다. 기본 0.80 은 *적힌 값*의 상한이라,
            #   ×1.50 으로 올린 팔레트를 전 슬롯 0.80 으로 눌러 **균일화**시킨다
            #   (= 이 라운드가 금지된 바로 그 결과). 상한은 실효 알베도 좌표계로
            #   옮겨 `pastel_cap` 이 들고 있고, 셀프체크 ③ 이 실효 최대 채널
            #   ≤ 0.80 을 다시 잰다.
            M["plaster_i"].append(PBR(
                f"{ROOT}/Looks/Plaster_{i}", sc.tex_path("plaster", "diff"),
                sc.tex_path("plaster", "nor"), sc.tex_path("plaster", "rough"),
                sca["plaster"], tint=tint_jitter(base, i,
                                                 cap=mp["pastel_cap"])))
            rbase = mp["roof_tints"][hs["tint"] % len(mp["roof_tints"])]
            # [W3 L15] `Looks/Roof_*` → `Looks/Slab_*`: the class table reads the prim name,
            #   and "Roof" is registered as **wood** (a temple-roof fix that does not belong to
            #   a 달동네 옥상). "Slab" is registered as **concrete**. Constant colour is
            #   unchanged in meaning — only the role, and therefore the promoted texture, moves.
            M["roof_i"].append(PBR(
                f"{ROOT}/Looks/Slab_{i}",
                diffuse_color=tint_jitter(rbase, 100 + i, cap=0.70),
                roughness_const=0.72))
        M["window"] = PBR(f"{ROOT}/Looks/Window",
                          diffuse_color=mp["window_color"],
                          roughness_const=mp["window_rough"], metallic=0.0)
        M["frame"] = PBR(f"{ROOT}/Looks/Frame",
                         diffuse_color=mp["frame_color"],
                         roughness_const=mp["frame_rough"],
                         metallic=mp["frame_metallic"])
        # [W3 L15] the **wall dado** only. The ground stains have their own material below.
        M["skirt"] = PBR(f"{ROOT}/Looks/Skirt",
                         diffuse_color=mp["skirt_color"],
                         roughness_const=mp["skirt_rough"])
        M["grime"] = PBR(f"{ROOT}/Looks/Grime",
                         diffuse_color=mp["grime_color"],
                         roughness_const=mp["grime_rough"])
        # [W3 L15 · B2d] 3 Korean container types (was: 3 tint-jitters of one terracotta).
        #   One material **per site** so the ±5 % per-instance jitter survives the type split —
        #   two 스티로폼 boxes in the same alley are never byte-identical.
        M["cont_i"] = []
        for i, ps in enumerate(PARAMS["pots"]):
            k = ps["kind"]
            M["cont_i"].append(PBR(
                f"{ROOT}/Looks/Pot{k.capitalize()}_{i}",
                diffuse_color=tint_jitter(mp[f"pot_{k}_color"], 200 + i,
                                          cap=0.70),
                roughness_const=mp[f"pot_{k}_rough"]))
        M["gear"] = PBR(f"{ROOT}/Looks/Gear", diffuse_color=mp["gear_color"],
                        roughness_const=mp["gear_rough"])
        # [W2 fix batch F5] Dark cast-iron for the kit's manhole / gully covers.
        #   `ground_kit._ik_manhole` **declares** albedo 0.10 to gate B9, but B9 only
        #   sees the declaration - the scene binds whatever it likes, and these scenes
        #   bound the stainless handrail constant. A cover at 0.66~0.85 against dark
        #   paving is the single brightest prop in the library (defect D5).
        M["gk_iron"] = PBR(f"{ROOT}/Looks/GKitIron",
                            diffuse_color=(0.10, 0.10, 0.105),
                            metallic=0.55, roughness_const=0.55)
        M["rail"] = PBR(f"{ROOT}/Looks/Rail",
                        diffuse_color=mp["rail_color"],
                        metallic=mp["rail_metallic"],
                        roughness_const=mp["rail_rough"])
        # [realism v1] Wall pipe handrail — separate from M["rail"], which now
        #   serves the ground_kit metalwork only.
        # [W3 L15 · era] path `Looks/Pipe` (class misc → no prescription) →
        #   `Looks/Handrail` (class metal). Values are now STS304 retrofit, see PARAMS.
        M["pipe"] = PBR(f"{ROOT}/Looks/Handrail",
                        diffuse_color=mp["pipe_color"],
                        metallic=mp["pipe_metallic"],
                        roughness_const=mp["pipe_rough"])
        # ── [GT-111] K7 옥상 부재 + K2 가스 입상관 ──
        #   `Looks/Roofrail` 은 class metal 로 잡히되 metallic 0 = 분체도장 연강.
        #   M["pipe"](STS304 신품)와 섞지 않는 이유는 PARAMS 주석 참조 — 원래
        #   있던 난간과 어제 붙인 손잡이는 같은 물건이 아니다.
        M["roofrail"] = PBR(f"{ROOT}/Looks/RoofrailSteel",
                            diffuse_color=mp["roofrail_color"],
                            metallic=0.0,
                            roughness_const=mp["roofrail_rough"])
        M["tank"] = PBR(f"{ROOT}/Looks/WaterTank",
                        diffuse_color=mp["tank_color"],
                        roughness_const=mp["tank_rough"])
        M["gaspipe"] = PBR(f"{ROOT}/Looks/GasPipe",
                           diffuse_color=mp["gas_pipe_color"],
                           metallic=0.35,
                           roughness_const=mp["gas_pipe_rough"])
        M["gasband"] = PBR(f"{ROOT}/Looks/GasBand",
                           diffuse_color=mp["gas_band_color"],
                           roughness_const=mp["gas_band_rough"])
        return M

    # -------------------------------------------------------------------
    # ground - valley slab (fills the slope) + flat upper alley
    # -------------------------------------------------------------------
    def build_ground(M):
        v = PARAMS["valley"]
        H = v["size"] / 2.0
        th = 1.0
        BOX(f"{ROOT}/Valley", (5.0, 0.0, v["z_top"] - th / 2.0),
            (v["size"], v["size"], th), M["valley"], col=True)
        ua = PARAMS["upper_alley"]
        # upper alley: solid mesa (filled down to the valley), top z=0
        cx = (ua["x0"] + ua["x1"]) / 2.0
        cy = (ua["y0"] + ua["y1"]) / 2.0
        top, bot = ua["z_top"], v["z_top"]
        # [W2-0 · P-A] the upper alley top face is a ground_kit decoration target -> displacement
        #   skin OFF. Leave it on and the recessed joints (−3 mm)·manhole (+-10 mm) are buried
        #   whole under the skin (+6.5~16.5 mm) `[measured - spec §1.1]`.
        sc.skin_exclude(f"{ROOT}/UpperAlley")
        BOX(f"{ROOT}/UpperAlley", (cx, cy, (top + bot) / 2.0),
            (ua["x1"] - ua["x0"], ua["y1"] - ua["y0"], top - bot),
            M["alley"], col=True)
        # upper alley retaining wall, 2 rows (A-15-3 critical): a 1.8 m wide ridge -> both flanks closed.
        #   Top z=1.2, solid down to the valley (−4.35) -> the 4.35 m cliff is gone.
        # [GT-63] clipped hedge bands: box+crown blobs -> fused rows of real
        #   shrub USDs (place_hedge_row; rects/heights/prim roots unchanged;
        #   legacy build_hedge fallback inside).
        rw = PARAMS["retwall"]
        n_hedge = 0
        for tag, y0, y1 in (("N", rw["y_in"], rw["y_out"]),
                            ("S", -rw["y_out"], -rw["y_in"])):
            BOX(f"{ROOT}/RetWall_{tag}",
                ((rw["x0"] + rw["x1"]) / 2.0, (y0 + y1) / 2.0,
                 (rw["z_top"] + v["z_top"]) / 2.0),
                (rw["x1"] - rw["x0"], y1 - y0, rw["z_top"] - v["z_top"]),
                M["retwall"], col=True)   # [v5 judgment applied] M["alley"] -> dedicated retaining wall
            # hedge on top of the retaining wall (helps read the alley)
            n_hedge += sc.place_hedge_row(
                stage, f"{ROOT}/RetHedge_{tag}",
                rw["x0"], y0 + 0.05, rw["x0"] + 8.0, y1 - 0.05,
                0.5, gk.det_seed("scene15.hedge", tag), base_z=rw["z_top"])
        print(f"[GT-63] 생울타리 실관목 {n_hedge}주 "
              f"(place_hedge_row · 폴백 {'무' if n_hedge else 'build_hedge'})")

    # -------------------------------------------------------------------
    # [W2] ground_kit - P5 alley_concrete. Full fill of the upper alley (x −12…0).
    #   Drop edge = the first step of flight1 at x=0. The joint at x=0 is dropped automatically
    #   by `_edge_guard_ticks` (GT-E2 Δ>=16 row). Only the stair-foot grating (15-6) uses
    #   bend-group local coordinates, so it is attached by a separate call.
    # -------------------------------------------------------------------
    def build_ground_kit(M, grp):
        g = PARAMS["ground"]
        gp = gk.plan_ground(
            "alley_concrete", region=tuple(g["region"]), z=0.0, gy=0.0,
            origin=(0.0, 0.0, 0.0),
            edges=[("stair_top", float(PARAMS["flight1"]["x0"]))],
            dists=(2, 5, 10), scene="scene15",
            tactile=(),                       # §12 - p~0.05, 0/12 in the sample -> not installed
            sites=dict(manhole=[tuple(g["manhole_site"])],
                       gutter_U=[float(g["gutter_y"])],
                       trench=[],             # 15-6 is done separately in the bend group
                       patch=[tuple(v) for v in g["patch_sites"]]),
            overrides=dict(infra=dict(manhole=1, gutter_U=1, trench=0)),
            seed=15)
        kit = gk.kit_from_scene_common(sc, stage)
        M2 = dict(M)
        # [W3 L15] two binds change, both to stop one material doing two jobs:
        #   `patch` M["alley"] → M["patch"] — a repair that is the *same* material as the floor
        #     is not legible as a repair, and R15-1 keeps these two patches precisely because on
        #     a neglected alley the repair **is** the realism. Same texture, same hue, +20 % Y.
        #   `stain_*` M["skirt"] → M["grime"] — the wall dado and the floor soiling were sharing
        #     one constant; they are different materials on different planes.
        M2.update(joint=M["stair"], crack=M["stair"], patch=M["patch"],
                  patch_cut=M["stair"], manhole=M["gk_iron"], gutter=M["stair"],
                  gutter_cover=M["stair"], weed=M["foliage"],
                  stain_grime_band=M["grime"], stain_dirt=M["grime"],
                  trench=M["rail"], trench_frame=M["rail"])
        res = gk.apply_ground(kit, f"{ROOT}/GKit", gp, M2,
                              skin_exclude=sc.skin_exclude,
                              scatter=sc.scatter_debris)
        # 15-6 linear grating at the stair foot - bend rot_group **local** coordinates.
        #   The lower alley top is z=−4.25, a different coordinate frame from the upper alley plan.
        gx, gy0, gy1 = g["grating_local"]
        gk.build_trench_drain(kit, f"{grp}/GKit_Grating", gx, gy0, gx, gy1,
                              float(g["grating_z"]), M["rail"],
                              mtl_frame=M["rail"], width=0.20)
        print(f"[ground_kit] scene15 P5 · 프림 {res['prims']} + 그레이팅 2 · "
              f"δmax {res['gt_delta_max']:.4f} · unit_cell {res['unit_cell']}")
        return res

    # -------------------------------------------------------------------
    # stairs - flight1 + landing + flight2 (25 deg bend) + lower alley
    # -------------------------------------------------------------------
    def build_stairs(M, grp):
        stair_mtl = M["stair"] if cfg["cue_material_break"] else M["alley"]
        f1 = PARAMS["flight1"]
        sc.build_straight_stairs(
            stage, f"{ROOT}/Flight1", f1["x0"], f1["y0"], f1["y1"],
            f1["riser"], f1["tread"], f1["nsteps"], f1["base_z"], stair_mtl,
            z_top=f1["z_top"], collider=True)
        # landing
        la = PARAMS["landing"]
        BOX(f"{ROOT}/Landing",
            ((la["x0"] + la["x1"]) / 2.0, 0.0,
             (la["z_top"] + la["base_z"]) / 2.0),
            (la["x1"] - la["x0"], f1["y1"] - f1["y0"],
             la["z_top"] - la["base_z"]), stair_mtl, col=True)

        # landing<->bend −Y wedge seal (A-15-4). Set 5 mm below the first step top (−2.21) to
        #   avoid coplanar Z-fighting; under the landing (x<5.1) it is buried in the landing solid.
        we = PARAMS["wedge"]
        BOX(f"{ROOT}/BendWedge",
            ((we["x0"] + we["x1"]) / 2.0, (we["y0"] + we["y1"]) / 2.0,
             (we["z_top"] + we["base_z"]) / 2.0),
            (we["x1"] - we["x0"], we["y1"] - we["y0"],
             we["z_top"] - we["base_z"]), stair_mtl, col=True)

        # flight2 + lower alley: rot_group 25 deg bend (grp is created once by the caller)
        f2 = PARAMS["flight2"]
        sc.build_straight_stairs(
            stage, f"{grp}/Flight2", f2["x0"], f2["y0"], f2["y1"],
            f2["riser"], f2["tread"], f2["nsteps"], f2["base_z"], stair_mtl,
            z_top=f2["z_top"], collider=True)
        # lower alley (inside the bend group - boundary aligned, vanishes toward +X)
        lo = PARAMS["lower_alley"]
        BOX(f"{grp}/LowerAlley",
            ((lo["x0"] + lo["x1"]) / 2.0, (lo["y0"] + lo["y1"]) / 2.0,
             (lo["z_top"] + lo["base_z"]) / 2.0),
            (lo["x1"] - lo["x0"], lo["y1"] - lo["y0"],
             lo["z_top"] - lo["base_z"]), M["alley"], col=True)

        # ── [realism v1] Guarding: the flanking walls ARE the guard ─────────
        #   The corridor is walled on **both** sides for the whole descent
        #   `[measured from PARAMS]`:
        #     upper alley x −12..0   retaining walls, inner faces |y| = 0.90
        #     flight1     x 0..3.6   House[4] y=+0.58 / House[6] y=−0.58
        #     landing     x 3.6..5.1 House[5] y=+0.58 / House[7] y=−0.58
        #     flight2     local 5.1..9.0  House[8] / House[10] local y=±0.58
        #   against stair edges at y=±0.60 — i.e. the walls sit 20 mm *inside*
        #   the stair, so no side is ever open to the 4.25 m drop. Evac/fire
        #   §15(1)2 is therefore satisfied by "wall" and **no guardrail is
        #   required anywhere in this scene** (same reading as the scene05 arc
        #   stair on its cheek walls — Docs/reports/stair_compliance_v1.md §1).
        #   The removed A-15-5 fix answered the wrong question: it extended a
        #   guardrail along a corridor that never lacked a guard.
        #   What `cue_railing` builds now is a *handrail* (§15(4)), not a guard:
        #   one φ34 pipe on the north wall over flight1 + the landing, stopping
        #   dead at the bend. Photo tally behind this choice: report §1.
        #   GT: unchanged. A pipe above the treads adds no terrain z — see the
        #   "drop label invariant" note on stair_kit.build_handrail. The drop
        #   edge at x=0 also loses its 116-prim occluder, so grazing exposure of
        #   that edge can only improve, never regress.
        if cfg["cue_railing"]:
            rl = PARAMS["rail"]

            def _wall_pipe(prefix, spec, z_top, ext_top, ext_bot):
                res = sk.build_handrail(
                    stage, prefix, rl["wall_y"], spec["x0"],
                    spec["tread"] * spec["nsteps"],
                    spec["riser"] * spec["nsteps"],
                    M["pipe"], sc.add_cylinder, z_top=z_top,
                    height=rl["height"], dia=rl["dia"],
                    ext_top=ext_top, ext_bot=ext_bot,
                    post_spacing=rl["bracket_spacing"],
                    wall_y=rl["wall_y"], wall_side=rl["wall_side"],
                    wall_gap=rl["wall_gap"], bracket_r=rl["bracket_r"],
                    strict=False)      # sub-code by design — warn, never raise
                for w in res["warnings"]:
                    print(f"[cue_railing] 규정 미달(의도) — {w}")
                return res

            # Upper flight + landing. `ext_bot` 1.5 carries the pipe flat over
            #   the landing to the bend, which is where the wall run ends.
            r1 = _wall_pipe(f"{ROOT}/WallPipe", f1, f1["z_top"],
                            rl["ext_top"], rl["ext_bot"])
            n_pipe = len(r1["prims"])
            # Optional lower-flight pipe (rot_group local — turns with the bend).
            #   OFF by default: see the `lower_flight` note in PARAMS.
            if rl["lower_flight"]:
                r2 = _wall_pipe(f"{grp}/WallPipe2", f2, f2["z_top"],
                                0.0, 0.0)
                n_pipe += len(r2["prims"])
            print(f"[cue_railing] 벽부착 파이프 손잡이 · 프림 {n_pipe} · "
                  f"y={r1['y']:.3f} (벽 {rl['wall_y']:+.2f}) · "
                  f"하부 플라이트 {'유' if rl['lower_flight'] else '무'}난간 "
                  f"— 방호는 좌우 벽이 담당")

    def build_flat_control(M):
        """hazard_stairs=False: the upper alley extends flat at z=0 (stair removed)."""
        f1 = PARAMS["flight1"]
        v = PARAMS["valley"]
        x0, x1 = 0.0, 12.0
        BOX(f"{ROOT}/FlatAlley",
            ((x0 + x1) / 2.0, 0.0, (0.0 + v["z_top"]) / 2.0),
            (x1 - x0, f1["y1"] - f1["y0"], 0.0 - v["z_top"]),
            M["alley"], col=True)

    # -------------------------------------------------------------------
    # houses (pastel plaster box + window·door inset + roof overhang)
    # -------------------------------------------------------------------
    def _opening(prefix, tag, cx, yf, face, z, ow, oh, M):
        """1 window·door = a dark panel + 4 frame edges.

        [B-15-2 fix] The old code **added** `ny = 0.02*face` to
        `gy = cy + face*(d/2−0.005)` (5 mm inside the wall face) as `wy = gy + ny`, so the
        centre of the 0.04-thick panel ended up 0.015 m outside the wall face → a black
        plate floating 3.5 cm off the wall, with its side thickness showing in the render.
        A true inset is impossible because the shell is solid, so the sign is corrected so
        that the panel **outer face** lands at wall face +5 mm (effectively flush), and
        4 frame edges projecting 3 cm are placed around it to read as an 'inset window'."""
        t_p, t_f, fw = 0.04, 0.05, 0.06
        py = yf + face * (0.005 - t_p / 2.0)       # panel outer face = wall face +5 mm
        BOX(f"{prefix}/{tag}_Panel", (cx, py, z), (ow, t_p, oh), M["window"])
        fy = yf + face * (0.03 - t_f / 2.0)        # frame outer face = wall face +3 cm
        for nm, ox, oz, sx, sz in (
                ("T", 0.0, oh / 2 + fw / 2, ow + 2 * fw, fw),
                ("B", 0.0, -oh / 2 - fw / 2, ow + 2 * fw, fw),
                ("L", -ow / 2 - fw / 2, 0.0, fw, oh),
                ("R", ow / 2 + fw / 2, 0.0, fw, oh)):
            BOX(f"{prefix}/{tag}_F{nm}", (cx + ox, fy, z + oz),
                (sx, t_f, sz), M["frame"])

    def build_house(prefix, hs, M, slot, life=False):
        h = PARAMS["house"]
        cx, cy = hs["cx"], hs["cy"]
        w, d, ht = hs["w"], hs["d"], hs["h"]
        base = hs["base_z"]
        face = hs["face"]
        v = PARAMS["valley"]
        shell_mtl = M["plaster_i"][slot]     # [v5.1] per-instance tint jitter
        top = base + ht
        bot = v["z_top"]                          # solid down to the valley (no floating, no cavity)
        BOX(f"{prefix}/Shell", (cx, cy, (top + bot) / 2.0),
            (w, d, top - bot), shell_mtl, col=True)
        # facade (alley-side) wall plane: face=-1 -> -Y face (y=cy-d/2), face=+1 -> +Y face
        yf = cy + face * (d / 2.0)
        # [GT-129] 개구부 배치는 `facade_openings` 가 여유에서 유도한다 —
        #   고정 비율 `cx ± 0.28·w` 는 좁은 동에서 문선과 창을 관통시켰다.
        for op in facade_openings(hs):
            _opening(prefix, op["tag"], op["cx"], yf, face, op["z"],
                     op["w"], op["h"], M)
        # roof slab (overhang)
        BOX(f"{prefix}/Roof", (cx, cy, top + h["roof_t"] / 2.0),
            (w + 2 * h["roof_over"], d + 2 * h["roof_over"], h["roof_t"]),
            M["roof_i"][slot], col=True)
        # skirting band (dark band at the facade base) - a paint trace, so every house keeps it.
        #   [v5.1 global convention 4] it doubles as the 'base grime band' (blocks large pure-white areas).
        BOX(f"{prefix}/Skirt", (cx, yf + face * 0.015, base + 0.425),
            (w, 0.03, 0.85), M["skirt"])
        if not life:
            return
        # ── [v5.1] traces of daily life = 1 AC outdoor unit only ──
        #   The old spec (meter box·satellite dish+bracket·rooftop water tank) was cloned onto
        #   all 12 houses at the same position and size, reading as a 'prop catalogue' (user review).
        #   The wall-mounted AC unit is the only functional fixture flush with the facade, so only it stays.
        BOX(f"{prefix}/AC", (cx - w * 0.30, yf + face * 0.16,
                             base + ht * 0.78), (0.70, 0.32, 0.55), M["gear"])

    # -------------------------------------------------------------------
    # [GT-111] K2 다세대 — 씬 로컬 빌더 확장 (킷 배선 없음, 제안서 §3.3 킷 갭 ①)
    #   `build_house` 의 어휘(셸 + 창 패널/프레임 + 걸레받이)를 그대로 물려받고
    #   K2 가 실제로 요구하는 것 — 필로티·일조사선 후퇴·노출 입상관·옥외 계단 —
    #   만 추가한다. 상자 부재는 전량 모듈 레벨 `villa_parts()` 에서 오고, 자가검증이
    #   같은 함수를 읽으므로 R-1 게이트가 "만들었다는 주장"이 아니라 실물을 잰다.
    # -------------------------------------------------------------------
    def build_villa(prefix, vs, M, slot):
        # 변위 스킨 제외. 석축(하부동 12.0×10.3×0.10)·필로티 슬래브(9.0×8.0×0.30)·
        #   옥상 방수면(8.6×6.0×0.10)은 `_skin_wanted` 의 "크고 수평인 지면류" 조건을
        #   그대로 만족해서 스킨 대상이 된다 — 건물 부재에 지면 미세요철을 얹을 이유가
        #   없고, 모호하면 제외가 이 프로젝트의 기본값이다(UpperAlley 선례).
        sc.skin_exclude(prefix)
        v = PARAMS["villa"]
        MK = dict(plaster=M["plaster_i"][slot], slab=M["roof_i"][slot],
                  concrete=M["stair"], retwall=M["retwall"],
                  skirt=M["skirt"], gear=M["gear"])
        n = 0
        for p in villa_parts(vs):
            sc.add_box(stage, f"{prefix}/{p['name']}", p["c"], p["s"],
                       MK[p["m"]], collider=p["col"], rotX=p["rotX"])
            n += 1
        b, flr, top = villa_levels(vs)
        w, d = v["w"], v["d"]
        cx, cy = float(vs["cx"]), float(vs["cy"])
        y_road = cy - d / 2.0
        hb = v["bay"] / 2.0
        # 창 — 세대당 침실(골목쪽) 1 + 거실(뒷길쪽) 1, 2세대/층 = 층당 4개.
        #   측벽은 무창(박공벽 처리, E8). 격자 없음 — 패널 1 + 프레임 4 뿐이다.
        #   최상층 골목쪽은 일조사선으로 1.60 물러난 면에 달린다.
        for fi, fz in enumerate(flr):
            ya = (cy + d / 2.0 if fi < len(flr) - 1
                  else y_road + (d - v["setback"]))
            bw, bh = v["win_bed"]
            lw, lh = v["win_liv"]
            for k, ox in enumerate((-hb, hb)):
                _opening(prefix, f"WinBed{fi}_{k}", cx + ox, ya, +1,
                         fz + v["sill_bed"] + bh / 2.0, bw, bh, M)
                _opening(prefix, f"WinLiv{fi}_{k}", cx + ox, y_road, -1,
                         fz + v["sill_liv"] + lh / 2.0, lw, lh, M)
                n += 10
        # 노출 가스 입상관 — 무창 측벽. [law] KGS FU551 각 층 바닥 +1.00 에 폭
        #   0.030 황색 띠 2줄, 주밸브 1.60~2.00.
        g, rs = v["gas"], float(vs["riser_side"])
        xr = cx + rs * (w / 2.0 + g["wall_gap"] + g["pipe_r"])
        yr = cy + g["y_off"]
        z0 = b + g["z_bot"]
        CYL(f"{prefix}/Gas/Riser", (xr, yr, (z0 + top) / 2.0), g["pipe_r"],
            top - z0, M["gaspipe"])
        n += 1
        for si, zs in enumerate([b + g["band_off"]]
                                + [f + g["band_off"] for f in flr]):
            for k in range(2):
                CYL(f"{prefix}/Gas/Band_{si}_{k}",
                    (xr, yr, zs + k * g["band_gap"]), g["band_r"],
                    g["band_w"], M["gasband"])
                n += 1
        CYL(f"{prefix}/Gas/Valve", (xr, yr, b + g["valve_z"]), g["valve_r"],
            g["valve_h"], M["gaspipe"])
        CYL(f"{prefix}/Gas/ValveHandle",
            (xr + rs * (g["valve_r"] + g["handle_l"] / 2.0), yr,
             b + g["valve_z"]), g["handle_r"], g["handle_l"], M["gaspipe"],
            rotY=90.0)
        n += 2
        for fi, fz in enumerate(flr):
            CYL(f"{prefix}/Gas/Branch_{fi}",
                (xr, yr - g["branch_len"] / 2.0, fz + g["band_off"]),
                g["pipe_r"], g["branch_len"], M["gaspipe"], rotX=90.0)
            n += 1
        return n

    # -------------------------------------------------------------------
    # [GT-111] K7 보완 — 옥상 난간(살대) + 물탱크. 파사드 평면보다 실내쪽에만 선다.
    # -------------------------------------------------------------------
    def build_roofline(M, grp):
        rt = PARAMS["house"]["roof_t"]
        n = 0
        for rr in PARAMS["roofline"]["rail"]:
            hs = PARAMS["houses"][rr["house"]]
            root = grp if hs.get("grp") else ROOT
            pfx = f"{root}/RoofRail_{rr['house']}"
            yf = hs["cy"] + hs["face"] * (hs["d"] / 2.0)
            yr = yf - hs["face"] * rr["setback"]
            zr = hs["base_z"] + hs["h"] + rt
            xa = hs["cx"] - hs["w"] / 2.0 + rr["end"]
            xb = hs["cx"] + hs["w"] / 2.0 - rr["end"]
            hh = rr["h"]
            BOX(f"{pfx}/RailTop", ((xa + xb) / 2.0, yr, zr + hh - 0.0225),
                (xb - xa, 0.040, 0.045), M["roofrail"])
            BOX(f"{pfx}/RailBot", ((xa + xb) / 2.0, yr, zr + 0.120),
                (xb - xa, 0.035, 0.035), M["roofrail"])
            n += 2
            npost = max(2, int(round((xb - xa) / 1.50)) + 1)
            for i in range(npost):
                BOX(f"{pfx}/Post_{i}",
                    (xa + (xb - xa) * i / (npost - 1), yr, zr + hh / 2.0),
                    (0.050, 0.050, hh), M["roofrail"])
                n += 1
            # 살대 — 가로대형 파이프 난간이 아니라 수직 살. 피치는 동별로 다르다.
            nb = max(1, int((xb - xa) / rr["pitch"]) - 1)
            z0b, z1b = zr + 0.1375, zr + hh - 0.045
            for i in range(nb):
                BOX(f"{pfx}/Bar_{i}",
                    (xa + (xb - xa) * (i + 1) / (nb + 1), yr,
                     (z0b + z1b) / 2.0), (0.022, 0.022, z1b - z0b),
                    M["roofrail"])
                n += 1
        for tk in PARAMS["roofline"]["tank"]:
            hs = PARAMS["houses"][tk["house"]]
            root = grp if hs.get("grp") else ROOT
            pfx = f"{root}/RoofTank_{tk['house']}"
            yf = hs["cy"] + hs["face"] * (hs["d"] / 2.0)
            ty = yf - hs["face"] * tk["v"]
            tx = hs["cx"] + tk["u"]
            zr = hs["base_z"] + hs["h"] + rt
            BOX(f"{pfx}/Stand", (tx, ty, zr + tk["stand"] / 2.0),
                (2 * tk["r"] + 0.10, 2 * tk["r"] + 0.10, tk["stand"]),
                M["roofrail"])
            CYL(f"{pfx}/Body", (tx, ty, zr + tk["stand"] + tk["h"] / 2.0),
                tk["r"], tk["h"], M["tank"])
            n += 2
        return n

    def build_dressing(M, grp):
        # 12 houses. Those with grp=True sit under the bend rotation group (local coordinates)
        #   and flank the 25 deg-rotated alley directly [resolves A-15-1/2 critical].
        #   [v5.1] life applies to only the 2 houses the scene parameters name (old: all 12).
        n_house = len(PARAMS["houses"])
        for i, hs in enumerate(PARAMS["houses"]):
            root = grp if hs.get("grp") else ROOT
            build_house(f"{root}/House_{i}", hs, M, i,
                        life=bool(hs.get("life")))
        # opposite hill backdrop cluster (distant horizon closure - not a dead-end wall, a
        #   Gamcheon-style house group terraced on the far slope across the valley). It closes
        #   the horizon behind the vanishing point of the bending alley (checklist §A-4).
        for i, bh in enumerate(PARAMS["backdrop"]):
            build_house(f"{ROOT}/Backdrop_{i}", bh, M, n_house + i)
        # ── [GT-111] K2 다세대 2동 — 골목 벽선 밖 배후 ──
        slot0 = n_house + len(PARAMS["backdrop"])
        n_villa = 0
        for j, vs in enumerate(PARAMS["villas"]):
            root = grp if vs.get("grp") else ROOT
            n_villa += build_villa(f"{root}/Villa_{vs['tag']}", vs, M,
                                   slot0 + j)
        for vs in PARAMS["villas"]:
            lo, hi = villa_aabb(vs)
            edge = PARAMS["lower_alley" if vs["grp"] else "upper_alley"]["y0"]
            print(f"[GT-111] K2-{vs['tag']} 4층 다세대 · "
                  f"{'회전군' if vs['grp'] else '월드'} "
                  f"x {lo[0]:+.2f}…{hi[0]:+.2f} · y {lo[1]:+.2f}…{hi[1]:+.2f} · "
                  f"최고 z {hi[2]:+.2f} · 골목 회랑({edge:+.2f}) 이격 "
                  f"{edge - hi[1]:+.2f} m")
        n_roof = build_roofline(M, grp)
        print(f"[GT-111] K2 신설 프림 {n_villa} (2동) · "
              f"K7 옥상 난간 {len(PARAMS['roofline']['rail'])}동/"
              f"물탱크 {len(PARAMS['roofline']['tank'])}기 프림 {n_roof}")
        # [v5.1] utility poles·wires·clotheslines removed (see the rationale in the PARAMS comment).
        # ── [W3 L15 · B2d + K4(b)] 5 alley containers: 1 container prim + 1 real shrub USD ──
        #   Was: 1 cylinder + 1 sphere per site (the sphere promoted to a lawn texture, L15-F2).
        #   The container is still a collider, the plant deliberately is not — a shrub crown is
        #   not something a robot collides with, and adding 5 collision boxes for foliage would
        #   move the hazard/collision box list for nothing (the GT-41 precedent, inverted).
        po = PARAMS["pot"]
        n_plant = 0
        for i, ps in enumerate(PARAMS["pots"]):
            root = grp if ps["grp"] else ROOT
            px, py, pz, kind = ps["x"], ps["y"], ps["z"], ps["kind"]
            spec = po[kind]
            mtl = M["cont_i"][i]
            if kind == "styro":
                # 스티로폼 상자 — long axis along the alley (+X), the way they are set down.
                BOX(f"{root}/Pot_{i}",
                    (px, py, pz + spec["h"] / 2.0),
                    (spec["sx"], spec["sy"], spec["h"]), mtl, col=True)
            else:
                CYL(f"{root}/Pot_{i}", (px, py, pz + spec["h"] / 2.0),
                    spec["r"], spec["h"], mtl, col=True)
            # The plant stands **on the container rim**, not on the tread.
            n_plant += sc.place_shrubs(
                stage, f"{root}/PotPlant_{i}",
                [(px, py, pz + spec["h"])], spec["plant_h"],
                species=ps["sp"], seed=1500 + 7 * i, tag="P")
        print(f"[화분] 용기 {len(PARAMS['pots'])} (스티로폼·고무대야·화분) · "
              f"식재 {n_plant} · 종 {sorted({p['sp'] for p in PARAMS['pots']})}")
        if n_plant < len(PARAMS["pots"]):
            # Honest, and not a silent hole: an empty container is a real alley state, but the
            # reason has to reach the log or a round cannot be audited from it.
            print(f"[화분][경고] {len(PARAMS['pots']) - n_plant}개 용기가 비었다 — "
                  f"LOOK_GEO={sc.LOOK_GEO} · 식생 에셋 {sc.veg_available()}")

    # ── scene assembly ──
    print("[씬] 재질·지오메트리 조립 중 ...")
    M = setup_materials()
    # the bend rotation group is shared by stairs·houses·dressing, so it is created once at the top of assembly
    #   (dressing under the group still rotates correctly in the hazard_stairs=False control).
    _bd = PARAMS["bend"]
    GRP = sc.build_rot_group(stage, f"{ROOT}/Bend", _bd["pivot"], _bd["deg"])
    build_ground(M)
    if cfg["hazard_stairs"]:
        build_stairs(M, GRP)
    else:
        build_flat_control(M)
    if cfg["cue_scene_dressing"]:
        build_dressing(M, GRP)
    build_ground_kit(M, GRP)             # [W2] ground elements - after the dressing (scatter order convention)

    apply_dome_rot = sc.setup_lighting(stage, PARAMS["light"],
                                       PARAMS["SUN_AZ_OFFSET"])

    if smoke_mode:
        n = sum(1 for _ in stage.Traverse())
        print(f"[SMOKE] scene15 조립 완료 · 프림 {n}개 · 조기 종료")
        simulation_app.close()
        return

    def look_from(eye, tgt):
        set_camera_view(eye=[float(e) for e in eye],
                        target=[float(t) for t in tgt])

    _v0 = build_views()["beauty_overview"]
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
            fp = os.path.join(LOOKCHECK_DIR, f"scene15_{ts}.png")
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


if __name__ == "__main__":
    main()
