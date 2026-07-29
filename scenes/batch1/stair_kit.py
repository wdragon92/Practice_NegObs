# -*- coding: utf-8 -*-
"""
stair_kit.py — 한국 법정 계단 부재 키트 (계단참 · 광폭계단 중간난간 · 손잡이)

Isaac Sim 4.5 / USD 절차적 생성용. **좌표계 Z-up · 단위 m.**
법령 원문 치수는 mm/cm 단위이므로 모든 상수를 이 파일 상단에서 **m 로 1회만**
환산하고, 이후 코드에서는 mm 리터럴을 쓰지 않는다(환산 실수 차단).

--------------------------------------------------------------------------
왜 이 파일이 필요한가 — 조사가 확정한 P0 위반 3건
--------------------------------------------------------------------------
`Docs/surveys/korean_pedestrian_geometry.md` §2 / `_dimension_index.md`
"미적용" 표가 지목한, **전부 법정 의무인데 33씬에 없는 것**:

  P0-1  광폭 계단 중간난간 : 너비 3 m **초과** 계단은 3 m 이내마다 중간난간.
        면제는 (단높이 ≤150 mm **그리고** 단너비 ≥300 mm) 둘 다 만족할 때뿐.
        ※ "또는" 이 아니다. 이 파일의 `mid_rail_lines()` 가 유일한 판정 지점.
  P0-2  계단참 : 높이 3 m 마다(주택단지 2 m 마다), 깊이 ≥1.20 m.
        긴 직통 계단은 "한국에 존재할 수 없는 계단" 이다.
  P0-3  옥외계단 규격 : 단높이 ≤200 mm · 단너비 ≥240 mm — **실내보다 가파르다.**
        실내 기준(단높이 ≤180)으로 만든 옥외 계단은 너무 완만하다.

--------------------------------------------------------------------------
설계 규약 (프로젝트 공통)
--------------------------------------------------------------------------
· **scene_common 을 import 하지 않는다.** USD 프림을 만드는 함수는 생성 헬퍼
  (`add_box` / `add_cylinder`)를 **인자로 주입**받는다. 주입 시그니처는
  scene_common 의 것과 동일하다:
      add_box(stage, path, center, size, mtl=None, collider=False)
      add_cylinder(stage, path, center, radius, height, mtl=None,
                   rotY=0.0, rotX=0.0, collider=False)
· **RNG 결정적.** 이 모듈은 난수를 전혀 쓰지 않는다(`hash()` 도 쓰지 않는다).
  지터가 필요하면 호출측에서 `random.Random(seed)` 로 만들어 인자로 넘길 것.
· **근거 없는 수치 금지.** 색인에 없는 값은 `[추정]` / `[근거 없음]` 을 달았다.
· 계단 하강 관례는 scene_common `_stair_steps` 와 동일:
  **x0 에서 +X 방향으로 하강**, 상단 지면 z = z_top, i 번째 단 디딤면 =
  z_top − riser·(i+1), 디딤면 x 구간 = [x0+i·tread, x0+(i+1)·tread].

--------------------------------------------------------------------------
GT (낙차 라벨) 총론 — 각 함수 docstring 의 `GT:` 줄도 반드시 읽을 것
--------------------------------------------------------------------------
이 연구의 핵심 단서는 **계단코(nosing) 선**이다. 이 파일의 부재 중
  · **중간난간 · 손잡이** 는 계단면 *위*에 서는 수직/사선 부재라 낙차 기하
    z(x,y) 를 바꾸지 않는다 → **GT 불변**. (자기폐색·그림자만 바뀐다.)
  · **계단참** 은 z(x) 프로파일 자체를 바꾼다 → **GT 변경**. 총 낙차는
    보존되지만 run 이 (계단참 깊이 × 개수) 만큼 길어지고, 참 상면은 국지
    낙차 0 인 평지 띠가 되며 **참 전연이 새 낙차 에지**로 추가된다.
    → 계단참을 넣은 씬은 기존 낙차/뎁스 GT 캐시를 반드시 무효화해야 한다.
"""

import math

__all__ = [
    "K", "stair_landings", "build_stair_landing", "mid_rail_lines",
    "build_handrail", "check_stair_compliance", "flight_nosing_lines",
]

# 부동소수 비교 허용오차. 법정 임계(3.000 m, 0.150 m …)를 정확히 맞춘 씬이
# 많아서(scene16 폭 3.0, scene14 riser 0.15) 이 값이 판정을 좌우한다.
TOL = 1e-9


# ===========================================================================
# [0] 법정 상수 — mm/cm 원문 → m 환산은 여기서 1회만
# ===========================================================================
class K:
    """법정 치수 상수 (단위 m). 각 값의 조문 근거를 주석에 남긴다.

    출처: 「건축물의 피난·방화구조 등의 기준에 관한 규칙」 §15 (이하 피난방화)
          「주택건설기준 등에 관한 규정」 §16·§18 (이하 주택기준)
          Docs/surveys/korean_pedestrian_geometry.md §2, §6.2
          Docs/surveys/_dimension_index.md "미적용" 표
    """

    # --- 계단참 (피난방화 §15①1 / 주택기준 §16②1) ---
    LANDING_MAX_RISE = 3.00          # 3 m 초과 계단 → 3 m 이내마다 참
    LANDING_MAX_RISE_HOUSING = 2.00  # 주택단지 안 건축물·옥외계단
    LANDING_MAX_RISE_ENTRY = 2.50    # 각 동 출입구 계단(1층 한정)
    LANDING_DEPTH_MIN = 1.20         # "유효너비 120 cm" = 진행방향 깊이

    # --- 광폭계단 중간난간 (피난방화 §15①3) ---
    MIDRAIL_MAX_SPAN = 3.00          # "너비 3 m 를 넘는" → 3 m 이내마다
    MIDRAIL_EXEMPT_RISER = 0.150     # 단서: 단높이 ≤15 cm  **그리고**
    MIDRAIL_EXEMPT_TREAD = 0.300     #       단너비 ≥30 cm  둘 다일 때만 면제

    # --- 양옆 난간 (피난방화 §15①2) ---
    RAIL_REQUIRED_DROP = 1.00        # 높이 1 m 를 넘는 계단·계단참 → 양옆 난간
    #   → 낙차 ≤1.00 m(= 옥외 riser 0.20 기준 5단, riser 0.15 기준 6단) 계단은
    #     **난간 의무가 없다.** 무난간 씬을 정당화하는 근거이기도 하다.

    # --- 계단 단면 (주택기준 §16①) ---
    OUTDOOR_RISER_MAX = 0.200        # 건축물의 옥외계단 — 실내보다 가파르다
    OUTDOOR_TREAD_MIN = 0.240
    OUTDOOR_WIDTH_MIN = 0.900
    COMMON_RISER_MAX = 0.180         # 공동으로 사용하는 계단
    COMMON_TREAD_MIN = 0.260
    COMMON_WIDTH_MIN = 1.200

    # --- 손잡이 (피난방화 §15④) ---
    HANDRAIL_DIA_MIN = 0.032         # 최대지름 3.2 cm 이상
    HANDRAIL_DIA_MAX = 0.038         #          3.8 cm 이하
    HANDRAIL_H = 0.850               # 계단으로부터 85 cm
    HANDRAIL_WALL_GAP = 0.050        # 벽등으로부터 5 cm 이상 이격
    HANDRAIL_EXT_MIN = 0.300         # 끝나는 수평부분에서 바깥쪽 30 cm 이상

    # --- 관례/추정 (법정 아님 — 반드시 태그와 함께 쓸 것) ---
    HANDRAIL_POST_SPACING = 1.20     # `[근거 없음]` 손잡이 지주 간격 규정 없음.
    #   난간 지주 2.0 m(메쉬휀스 2.08 준용, _dimension_index)와 달리 손잡이는
    #   더 촘촘한 것이 관행 → 1.2 m `[추정]`.
    LANDING_CROSS_SLOPE = 0.02       # `[추정]` 보도 횡단경사 1/25 준용(1~2 %)
    NOSING_BAND_W = 0.050            # 논슬립 폭 — 법정 수치 없음.
    #   KS F 4527 호칭수 50 mm + 건축공사 표준시방서 관행 `[확인-비법정]`


# ===========================================================================
# [1] 계단참 계획 — 순수 계산 (USD 무관 · 단위 테스트 가능)
# ===========================================================================
def stair_landings(total_drop, riser, tread,
                   max_rise=K.LANDING_MAX_RISE,
                   landing_depth=K.LANDING_DEPTH_MIN,
                   x0=0.0, z_top=0.0):
    """총 낙차를 법정 주기로 쪼개 **flight / 계단참 분할 계획**을 반환한다.

    피난방화 §15①1 : 높이 3 m 를 넘는 계단에는 3 m 이내마다 유효너비 1.2 m
    이상의 계단참. 주택단지 안 건축물·옥외계단은 `max_rise=2.0`(주택기준
    §16②1), 각 동 출입구 계단 1층은 `max_rise=2.5`.

    좌표 관례는 scene_common `_stair_steps` 와 동일: (x0, z_top) 에서
    **+X 로 하강**. 계단참 상면은 그 직전 flight 마지막 디딤면과 **동일 z**
    (= 마지막 디딤면이 landing_depth 만큼 연장된 형태)이므로 참을 넣어도
    **단코 선의 z 사다리는 그대로 보존**된다.

    인자
      total_drop    : 총 낙차 [m] (양수)
      riser         : 단높이 [m]
      tread         : 단너비 [m]
      max_rise      : flight 1개가 감당할 수 있는 최대 상승/하강 [m]
      landing_depth : 계단참 깊이(진행방향) [m]. 1.20 미만이면 경고 기록
      x0, z_top     : 계단 시작점

    반환 dict
      n_steps       : 총 단 수(=round(total_drop/riser))
      riser_eff     : total_drop/n_steps — 실제 균등 단높이
      n_flights     : flight 개수
      n_landings    : 계단참 개수 (= n_flights − 1)
      flights       : [{i, n_steps, x0, x1, z_top, z_bot, rise, run}]
      landings      : [{i, x0, x1, z, depth}]
      total_run     : 계단참 포함 전체 X 길이
      run_delta     : 계단참 때문에 늘어난 run (= n_landings × landing_depth)
      compliant     : 이 계획 자체가 법정 주기·깊이를 만족하는가
      notes         : 문자열 경고 목록

    분배 규칙(결정적 — 난수 없음): flight 당 최대 단 수
    m = floor(max_rise/riser) 로 n_flights = ceil(n_steps/m) 를 구한 뒤,
    나머지를 **앞쪽 flight 부터 1단씩** 배분한다. 같은 입력이면 항상 같은 출력.

    GT: **낙차 라벨을 바꾼다.** 총 낙차는 보존되지만 (a) run 이 run_delta 만큼
        길어져 z(x) 프로파일이 평행이동·연장되고, (b) 참 상면 폭
        landing_depth 구간은 **국지 낙차 0 인 평지 띠**가 되며, (c) 참 전연이
        **새로운 낙차 에지**(잔여 낙차 = 하류 flight 합)로 추가된다.
        → 이 계획을 적용한 씬은 기존 낙차/뎁스 GT 를 재생성해야 한다.
        (중간난간·손잡이와 달리 계단참만이 GT 를 건드리는 부재다.)
    """
    total_drop = float(total_drop)
    riser = float(riser)
    tread = float(tread)
    notes = []

    if riser <= TOL:
        raise ValueError("riser must be > 0 (m)")
    if tread <= TOL:
        raise ValueError("tread must be > 0 (m)")
    if total_drop < 0.0:
        raise ValueError("total_drop must be >= 0 (m)")
    if max_rise <= TOL:
        raise ValueError("max_rise must be > 0 (m)")

    n_steps = int(round(total_drop / riser))
    if n_steps < 1:
        n_steps = 1
    riser_eff = total_drop / n_steps
    if abs(riser_eff - riser) > 1e-6:
        notes.append(
            "total_drop/riser 가 정수가 아니다 → riser_eff %.4f 로 균등화"
            % riser_eff)

    if landing_depth < K.LANDING_DEPTH_MIN - TOL:
        notes.append(
            "계단참 깊이 %.3f < 법정 최소 %.2f m (피난방화 §15①1)"
            % (landing_depth, K.LANDING_DEPTH_MIN))

    # flight 당 최대 단 수 — 참 없이 감당 가능한 상승분
    m = int(math.floor(max_rise / riser_eff + TOL))
    if m < 1:
        m = 1
        notes.append(
            "단높이 %.3f 가 max_rise %.2f 보다 크다 → flight 당 1단으로 강제"
            % (riser_eff, max_rise))

    n_flights = int(math.ceil(float(n_steps) / m - TOL))
    if n_flights < 1:
        n_flights = 1

    base, rem = divmod(n_steps, n_flights)
    counts = [base + (1 if i < rem else 0) for i in range(n_flights)]

    flights = []
    landings = []
    x = float(x0)
    z = float(z_top)
    for i, c in enumerate(counts):
        run = c * tread
        rise = c * riser_eff
        flights.append(dict(i=i, n_steps=c, x0=x, x1=x + run,
                            z_top=z, z_bot=z - rise, rise=rise, run=run))
        x += run
        z -= rise
        if i < n_flights - 1:
            landings.append(dict(i=i, x0=x, x1=x + landing_depth,
                                 z=z, depth=float(landing_depth)))
            x += landing_depth

    max_flight_rise = max(f["rise"] for f in flights)
    compliant = (max_flight_rise <= max_rise + 1e-6
                 and landing_depth >= K.LANDING_DEPTH_MIN - TOL)

    return dict(
        total_drop=total_drop, riser=riser, riser_eff=riser_eff, tread=tread,
        n_steps=n_steps, n_flights=n_flights, n_landings=len(landings),
        flights=flights, landings=landings,
        max_rise=float(max_rise), landing_depth=float(landing_depth),
        max_flight_rise=max_flight_rise,
        total_run=x - float(x0),
        run_delta=len(landings) * float(landing_depth),
        z_bottom=z, compliant=compliant, notes=notes,
    )


def flight_nosing_lines(plan):
    """계획(plan)에서 **단코 선의 (x, z) 목록**만 뽑는다. GT 검산용.

    각 원소 = (x_nose, z_tread) : 그 단 디딤면의 +X 끝(=단코)과 디딤면 z.
    계단참 전연도 하나의 단코로 포함된다(참 전연 = 새 낙차 에지).

    GT: 생성 함수가 아니다(프림 무생성). 계단참 도입 전후의 낙차 에지 집합을
        **diff 해서 GT 변경 범위를 산출**하는 데 쓴다.
    """
    lines = []
    for f in plan["flights"]:
        for k in range(1, f["n_steps"] + 1):
            lines.append((f["x0"] + k * plan["tread"],
                          f["z_top"] - k * plan["riser_eff"]))
    for l in plan["landings"]:
        lines.append((l["x1"], l["z"]))
    lines.sort(key=lambda t: t[0])
    return lines


# ===========================================================================
# [2] 계단참 판 생성
# ===========================================================================
def build_stair_landing(stage, path, landing, y0, y1, base_z, mtl,
                        add_box, collider=True, edge_lip=0.0):
    """`stair_landings()` 가 반환한 landing dict 1개를 솔리드 판으로 만든다.

    인자
      landing  : {"x0","x1","z","depth"} — stair_landings() 산출물 원소
      y0, y1   : 계단 폭(Y). 법정 요건 "해당 계단의 유효폭 이상"(주택기준
                 §16②1)이므로 **계단 폭과 동일하게** 주는 것이 기본이다.
      base_z   : 판 밑면 z (계단 솔리드 base_z 와 맞출 것 — 부유 방지)
      mtl      : 재질 (호출측 make_pbr 산출물)
      add_box  : scene_common.add_box 와 동일 시그니처의 주입 헬퍼
      edge_lip : 참 전연을 +X 로 더 내미는 양 [m]. 0 이면 계획 그대로.
                 `[근거 없음]` — 참 전연 물끊기/코 돌출 규정 없음. 기본 0.

    배수 구배는 **의도적으로 넣지 않았다.** 계단참 전용 구배 규정은 없고
    보도 횡단경사 1/25 준용은 `[추정]`(K.LANDING_CROSS_SLOPE)이다. 구배를
    주려면 회전 가능한 박스 헬퍼(scene_common `_oriented_box`)를 따로
    주입해야 하므로, 이 함수는 **수평 판**만 만든다.

    반환: add_box 가 반환한 프림.

    GT: 이 판의 **상면(z)** 은 국지 낙차 0 인 평지, **+X 전연**은 새 낙차
        에지가 된다(그 아래 flight 낙차 전부가 이 에지에 걸린다).
        판 상면은 직전 flight 마지막 디딤면과 동일 z 이므로 **상류 단코 선의
        z 사다리는 불변**이고, 새로 생기는 것은 "긴 디딤면 1개"뿐이다.
        이 성질 덕에 계단참 삽입이 단코 실루엣 단서를 파괴하지 않는다.
    """
    x0 = float(landing["x0"])
    x1 = float(landing["x1"]) + float(edge_lip)
    z_top = float(landing["z"])
    cx = (x0 + x1) / 2.0
    cy = (float(y0) + float(y1)) / 2.0
    hz = z_top - float(base_z)
    if hz <= 0.0:
        raise ValueError("landing z (%.3f) must be above base_z (%.3f)"
                         % (z_top, base_z))
    return add_box(stage, path, (cx, cy, z_top - hz / 2.0),
                   (x1 - x0, abs(float(y1) - float(y0)), hz),
                   mtl, collider=collider)


# ===========================================================================
# [3] 광폭 계단 중간난간 위치 — P0-1 의 유일한 판정 지점
# ===========================================================================
def mid_rail_lines(y0, y1, max_span=K.MIDRAIL_MAX_SPAN,
                   riser=None, tread=None):
    """계단 폭에 따라 **중간난간이 들어갈 y 좌표 리스트**를 반환한다.

    피난방화 §15①3 원문:
      "너비가 3미터를 넘는 계단에는 계단의 중간에 너비 3미터 이내마다 난간을
       설치할 것. 다만, 계단의 **단높이가 15센티미터 이하이고**, 계단의
       **단너비가 30센티미터 이상인 경우**에는 그러하지 아니하다."

    ★ 면제 조건은 **AND** 다. riser ≤ 0.150 **그리고** tread ≥ 0.300 을
      둘 다 만족할 때만 면제. 어느 한쪽만 만족하면 중간난간은 여전히 의무다.
      (riser/tread 중 하나라도 None 이면 면제 판정을 하지 않는다 = 보수적)

    ★ 임계는 **초과**(>)다. 폭이 정확히 3.000 m 면 "3 m 를 넘는" 이 아니므로
      의무가 발생하지 않는다. scene16/17 이 정확히 이 경계에 있다.

    인자
      y0, y1   : 계단 폭 구간(순서 무관)
      max_span : 난간 간 최대 간격 [m]
      riser    : 단높이 [m] (면제 판정용, None 이면 면제 미적용)
      tread    : 단너비 [m] (면제 판정용, None 이면 면제 미적용)

    반환: y 좌표 리스트(오름차순). 의무 없음 → 빈 리스트.
          간격은 폭을 ceil(폭/max_span) 등분한 **균등 분할**(결정적).
          예) 폭 12 m → [ -3, 0, +3 ] 형태의 3열(각 span 3.0).

    GT: **낙차 라벨 불변.** 중간난간은 계단면 위에 서는 수직 부재라 z(x,y)
        지형을 건드리지 않는다. 다만 낙차 방향(+X)으로 길게 뻗은 선형
        구조물이라 단코 선을 세로로 가르고 자기폐색·그림자를 만든다 →
        RGB 맥락단서 정보량은 크게 늘고, 낙차 GT 는 그대로다.
    """
    a, b = float(y0), float(y1)
    lo, hi = (a, b) if a <= b else (b, a)
    width = hi - lo

    if riser is not None and tread is not None:
        exempt = (float(riser) <= K.MIDRAIL_EXEMPT_RISER + TOL
                  and float(tread) >= K.MIDRAIL_EXEMPT_TREAD - TOL)
        if exempt:
            return []

    if width <= float(max_span) + TOL:      # "넘는" = 초과. 3.000 은 미해당
        return []

    n_bays = int(math.ceil(width / float(max_span) - TOL))
    return [lo + width * k / float(n_bays) for k in range(1, n_bays)]


# ===========================================================================
# [4] 손잡이 (핸드레일) — φ32~38 · h850 · 끝단 수평 연장 ≥300
# ===========================================================================
def build_handrail(stage, prefix, y, x_top, run, drop, mtl, add_cylinder,
                   z_top=0.0, height=K.HANDRAIL_H, dia=0.034,
                   ext_top=K.HANDRAIL_EXT_MIN, ext_bot=K.HANDRAIL_EXT_MIN,
                   post_r=0.020, post_spacing=K.HANDRAIL_POST_SPACING,
                   ground_fn=None, wall_y=None, wall_side=1.0,
                   wall_gap=K.HANDRAIL_WALL_GAP, bracket_r=0.012,
                   strict=True):
    """법정 규격 손잡이 1선. 피난방화 §15④.

      1. 최대지름 **32~38 mm** 원형/타원 단면      → `dia`
      2. 벽등으로부터 **≥50 mm** 이격, 계단으로부터 높이 **850 mm** → `wall_gap`, `height`
      3. 계단이 끝나는 수평부분에서 바깥쪽으로 **≥300 mm** → `ext_top`, `ext_bot`

    ★ 끝단 수평 연장이 이 부재의 **실루엣상 한국적 특징**이다. 경사 레일이
      계단 끝에서 그냥 끊기지 않고, 상·하단 각각 평지 위로 30 cm 이상
      수평으로 더 나간 뒤 끝난다. 원경에서 "ㄱ자 꺾임 2개"로 읽힌다.

    기하 (scene_common 하강 관례와 동일)
      x_top          : 경사 시작 x (여기서 z=z_top)
      run, drop      : 경사 구간 수평길이·낙차 → 경사 끝 x_top+run, z_top−drop
      상단 수평 연장 : x_top−ext_top .. x_top,        z = z_top − drop·0 + height
      하단 수평 연장 : x_top+run .. x_top+run+ext_bot, z = z_top − drop + height
      높이 기준면    : **단코 연결선**(디딤면 코를 이은 사선). 조문의
                       "계단으로부터의 높이"를 이렇게 해석한다 `[추정]` —
                       조문이 측정 기준면을 명시하지 않는다 `[근거 없음]`.

    벽부착 모드 : `wall_y` 를 주면 y 는 무시되고
      y_rail = wall_y + wall_side × (wall_gap + dia/2)
    로 계산되며, 지주(post) 대신 **브래킷**(짧은 Y축 실린더)을 건다.
    `wall_y=None` 이면 자립 모드로 지주를 세운다.

    지주 간격 `post_spacing` 기본 1.2 m 는 `[근거 없음]`(손잡이 지주 간격을
    규정한 조문 없음) — 난간 지주 2.0 m 보다 촘촘한 관행 `[추정]`.

    strict=True 면 법정 하한 위반 시 ValueError. False 면 경고만 담아 반환.

    반환 dict: {"prims": [...], "y": 실제 레일 y, "warnings": [...],
                "x_start": 최상단 x, "x_end": 최하단 x}

    GT: **낙차 라벨 불변.** 손잡이는 지형 z 를 만들지 않는다. 끝단 수평 연장
        구간은 계단 밖 평지(낙차 0 영역) 위에 떠 있으므로 낙차 마스크에
        어떤 화소도 추가하지 않는다. 실루엣·그림자만 바뀐다.
    """
    warns = []
    dia = float(dia)
    if not (K.HANDRAIL_DIA_MIN - TOL <= dia <= K.HANDRAIL_DIA_MAX + TOL):
        msg = ("손잡이 지름 %.4f m 가 법정 φ%.3f~%.3f 밖 (피난방화 §15④1)"
               % (dia, K.HANDRAIL_DIA_MIN, K.HANDRAIL_DIA_MAX))
        if strict:
            raise ValueError(msg)
        warns.append(msg)
    for nm, v in (("ext_top", ext_top), ("ext_bot", ext_bot)):
        if float(v) < K.HANDRAIL_EXT_MIN - TOL:
            msg = ("%s %.3f m < 법정 수평 연장 %.2f m (피난방화 §15④3)"
                   % (nm, float(v), K.HANDRAIL_EXT_MIN))
            if strict:
                raise ValueError(msg)
            warns.append(msg)
    if float(wall_gap) < K.HANDRAIL_WALL_GAP - TOL and wall_y is not None:
        msg = ("벽 이격 %.3f m < 법정 %.2f m (피난방화 §15④2)"
               % (float(wall_gap), K.HANDRAIL_WALL_GAP))
        if strict:
            raise ValueError(msg)
        warns.append(msg)

    r = dia / 2.0
    run = float(run)
    drop = float(drop)
    x_top = float(x_top)
    z_top = float(z_top)
    height = float(height)
    ext_top = float(ext_top)
    ext_bot = float(ext_bot)

    if wall_y is None:
        y_rail = float(y)
    else:
        y_rail = float(wall_y) + float(wall_side) * (float(wall_gap) + r)

    x_start = x_top - ext_top
    x_slope_end = x_top + run
    x_end = x_slope_end + ext_bot
    z_rail_top = z_top + height              # 상단 수평부 레일 중심 z
    z_rail_bot = z_top - drop + height       # 하단 수평부 레일 중심 z

    prims = []

    # (a) 상단 수평 연장 — Cylinder 축(Z)을 X 로 눕힌다(rotY=90)
    if ext_top > TOL:
        prims.append(add_cylinder(
            stage, "%s/ExtTop" % prefix,
            ((x_start + x_top) / 2.0, y_rail, z_rail_top),
            r, ext_top, mtl, rotY=90.0))

    # (b) 경사부
    if run > TOL or drop > TOL:
        L = math.hypot(run, drop)
        ang = math.degrees(math.atan2(drop, run))
        prims.append(add_cylinder(
            stage, "%s/Slope" % prefix,
            (x_top + run / 2.0, y_rail, z_rail_top - drop / 2.0),
            r, L, mtl, rotY=90.0 + ang))

    # (c) 하단 수평 연장
    if ext_bot > TOL:
        prims.append(add_cylinder(
            stage, "%s/ExtBot" % prefix,
            ((x_slope_end + x_end) / 2.0, y_rail, z_rail_bot),
            r, ext_bot, mtl, rotY=90.0))

    # (d) 지지 — 자립이면 지주, 벽부착이면 브래킷
    def _nose_z(x):
        """단코 연결선 z (레일 높이 기준면)."""
        if x <= x_top:
            return z_top
        if x >= x_slope_end:
            return z_top - drop
        return z_top - drop * (x - x_top) / run if run > TOL else z_top - drop

    def _rail_z(x):
        return _nose_z(x) + height

    gz_fn = ground_fn if ground_fn is not None else _nose_z

    n_sup = int(math.floor((x_end - x_start) / float(post_spacing) + TOL)) + 1
    for i in range(n_sup):
        xp = x_start + i * float(post_spacing)
        if xp > x_end + TOL:
            break
        rz = _rail_z(xp)
        if wall_y is None:
            gz = float(gz_fn(xp))
            h = rz - gz
            if h > 1e-3:
                prims.append(add_cylinder(
                    stage, "%s/Post_%d" % (prefix, i),
                    (xp, y_rail, gz + h / 2.0), post_r, h, mtl))
        else:
            arm = abs(y_rail - float(wall_y))
            if arm > 1e-3:
                prims.append(add_cylinder(
                    stage, "%s/Brk_%d" % (prefix, i),
                    (xp, (y_rail + float(wall_y)) / 2.0, rz),
                    bracket_r, arm, mtl, rotX=90.0))

    return dict(prims=prims, y=y_rail, warnings=warns,
                x_start=x_start, x_end=x_end,
                z_top_rail=z_rail_top, z_bot_rail=z_rail_bot)


# ===========================================================================
# [5] 적합성 판정
# ===========================================================================
def _v(code, sev, rule, expected, actual, msg):
    return dict(code=code, severity=sev, rule=rule,
                expected=expected, actual=actual, msg=msg)


def check_stair_compliance(riser, tread, width, total_drop, outdoor=True,
                           has_rail=None, n_mid_rails=0, n_landings=0,
                           landing_depth=None, housing_complex=False,
                           handrail=None, label="", note=""):
    """계단 제원 1건을 법정 요건과 대조해 **위반 목록 dict** 를 반환한다.

    인자
      riser, tread  : 단높이·단너비 [m]. 불균등이면 (최대 riser, 최소 tread)
                      = **가장 불리한 값**을 넣을 것.
      width         : 계단 유효폭 [m]
      total_drop    : 총 낙차 [m]
      outdoor       : True → 옥외계단 기준(riser ≤0.20 / tread ≥0.24 / 폭 ≥0.90)
                      False → 공동사용 계단 기준(≤0.18 / ≥0.26 / ≥1.20)
      has_rail      : "both" | "one" | "none" | True | False | None(불명)
      n_mid_rails   : 현재 씬에 있는 **중간**난간 열 수(측면 난간은 제외)
      n_landings    : 현재 씬에 있는 **중간** 계단참 수(상·하단 평지는 제외)
      landing_depth : 현재 계단참 깊이 [m] (None → 판정 생략)
      housing_complex : 주택단지 안 건축물·옥외계단 → 참 주기 2 m
      handrail      : {"dia":…, "h":…, "ext":…} 또는 None(판정 생략)

    반환 dict — 진단표 1행을 그대로 만들 수 있는 필드 구성.
      req_landings / have_landings / req_mid_rails / have_mid_rails /
      mid_rail_exempt / outdoor_ok / rail_required / violations / ok / p0

    GT: **판정 전용. 프림을 만들지 않으므로 낙차 라벨과 무관하다.**
        단, 이 함수가 P0-2(계단참) 위반을 낸 씬은 시정 시 GT 가 바뀐다
        (stair_landings 의 GT: 줄 참조). 그 구분이 진단표의 핵심이다.
    """
    riser = float(riser)
    tread = float(tread)
    width = float(width)
    total_drop = float(total_drop)
    V = []

    # --- 단면 규격 (P0-3) ---
    r_max = K.OUTDOOR_RISER_MAX if outdoor else K.COMMON_RISER_MAX
    t_min = K.OUTDOOR_TREAD_MIN if outdoor else K.COMMON_TREAD_MIN
    w_min = K.OUTDOOR_WIDTH_MIN if outdoor else K.COMMON_WIDTH_MIN
    kind = "옥외계단" if outdoor else "공동사용 계단"

    if riser > r_max + TOL:
        V.append(_v("D1", "P0", "주택기준 §16①",
                    "단높이 ≤%.3f" % r_max, "%.3f" % riser,
                    "%s 단높이 초과 (%.3f > %.3f)" % (kind, riser, r_max)))
    if tread < t_min - TOL:
        V.append(_v("D2", "P0", "주택기준 §16①",
                    "단너비 ≥%.3f" % t_min, "%.3f" % tread,
                    "%s 단너비 미달 (%.3f < %.3f)" % (kind, tread, t_min)))
    if width < w_min - TOL:
        V.append(_v("D3", "P1", "주택기준 §16①",
                    "유효폭 ≥%.3f" % w_min, "%.3f" % width,
                    "%s 유효폭 미달 (%.3f < %.3f)" % (kind, width, w_min)))
    outdoor_ok = not any(x["code"] in ("D1", "D2", "D3") for x in V)

    # --- 계단참 (P0-2) ---
    max_rise = (K.LANDING_MAX_RISE_HOUSING if housing_complex
                else K.LANDING_MAX_RISE)
    if total_drop > max_rise + TOL:
        req_landings = int(math.ceil(total_drop / max_rise - TOL)) - 1
    else:
        req_landings = 0
    if n_landings < req_landings:
        V.append(_v("L1", "P0", "피난방화 §15①1 / 주택기준 §16②1",
                    "계단참 %d 개(%.1f m 마다)" % (req_landings, max_rise),
                    "%d 개" % n_landings,
                    "계단참 %d 개 부족 — 낙차 %.2f m 직통은 한국에 존재할 수 "
                    "없는 계단" % (req_landings - n_landings, total_drop)))
    if (landing_depth is not None and n_landings > 0
            and float(landing_depth) < K.LANDING_DEPTH_MIN - TOL):
        V.append(_v("L2", "P1", "피난방화 §15①1",
                    "깊이 ≥%.2f" % K.LANDING_DEPTH_MIN,
                    "%.3f" % float(landing_depth),
                    "계단참 깊이 미달"))

    # --- 광폭 중간난간 (P0-1) ---
    lines = mid_rail_lines(-width / 2.0, width / 2.0,
                           riser=riser, tread=tread)
    exempt = (riser <= K.MIDRAIL_EXEMPT_RISER + TOL
              and tread >= K.MIDRAIL_EXEMPT_TREAD - TOL)
    req_mid = len(lines)
    if n_mid_rails < req_mid:
        V.append(_v("R1", "P0", "피난방화 §15①3",
                    "중간난간 %d 열(3 m 이내마다)" % req_mid,
                    "%d 열" % n_mid_rails,
                    "폭 %.2f m 광폭계단 중간난간 %d 열 부족 "
                    "(면제조건 riser≤0.15 AND tread≥0.30 미충족)"
                    % (width, req_mid - n_mid_rails)))

    # --- 양옆 난간 (임계: 높이 1 m 초과) ---
    rail_required = total_drop > K.RAIL_REQUIRED_DROP + TOL
    hr = has_rail
    if hr is True:
        hr = "both"
    elif hr is False:
        hr = "none"
    if rail_required and hr in ("none", "one"):
        V.append(_v("R2", "P1", "피난방화 §15①2",
                    "양옆 난간(벽 포함)", hr,
                    "낙차 %.2f m > 1 m — 양옆 난간 의무 "
                    "(교통약자법은 편측 허용이나 건축법 계열은 양옆)"
                    % total_drop))

    # --- 손잡이 규격 ---
    if handrail:
        d = handrail.get("dia")
        h = handrail.get("h")
        e = handrail.get("ext")
        if d is not None and not (K.HANDRAIL_DIA_MIN - TOL <= float(d)
                                  <= K.HANDRAIL_DIA_MAX + TOL):
            V.append(_v("H1", "P1", "피난방화 §15④1",
                        "φ0.032~0.038", "%.3f" % float(d), "손잡이 지름 이탈"))
        if h is not None and abs(float(h) - K.HANDRAIL_H) > 0.05:
            V.append(_v("H2", "P1", "피난방화 §15④2",
                        "h=0.850", "%.3f" % float(h), "손잡이 높이 이탈"))
        if e is not None and float(e) < K.HANDRAIL_EXT_MIN - TOL:
            V.append(_v("H3", "P1", "피난방화 §15④3",
                        "수평연장 ≥0.300", "%.3f" % float(e),
                        "끝단 수평 연장 미달"))

    p0 = sum(1 for x in V if x["severity"] == "P0")
    return dict(
        label=label, note=note,
        riser=riser, tread=tread, width=width, total_drop=total_drop,
        outdoor=outdoor, housing_complex=housing_complex,
        req_landings=req_landings, have_landings=int(n_landings),
        req_mid_rails=req_mid, have_mid_rails=int(n_mid_rails),
        mid_rail_lines=lines, mid_rail_exempt=exempt,
        outdoor_ok=outdoor_ok, rail_required=rail_required, has_rail=hr,
        violations=V, ok=(len(V) == 0), p0=p0, n_violations=len(V),
    )


# ===========================================================================
# [6] 자기검사 — GPU/USD 없이 순수 계산만 검증
# ===========================================================================
def _selfcheck():
    ok = 0

    # (1) 면제는 AND 다 — 이 4가지가 이 파일의 존재 이유
    assert mid_rail_lines(-6, 6, riser=0.150, tread=0.300) == []      # 둘 다 O
    assert mid_rail_lines(-6, 6, riser=0.160, tread=0.340) != []      # riser X
    assert mid_rail_lines(-6, 6, riser=0.150, tread=0.280) != []      # tread X
    assert mid_rail_lines(-6, 6, riser=0.173, tread=0.300) != []      # riser X
    ok += 4

    # (2) 임계는 "초과". 폭 3.000 은 의무 없음, 3.001 은 의무 발생
    assert mid_rail_lines(-1.5, 1.5, riser=0.17, tread=0.30) == []
    assert len(mid_rail_lines(0.0, 3.001, riser=0.17, tread=0.30)) == 1
    # 폭 12 → 3열, 간격 3.0
    L = mid_rail_lines(-6, 6, riser=0.17, tread=0.30)
    assert len(L) == 3 and abs(L[0] - (-3.0)) < 1e-9 and abs(L[1]) < 1e-9
    # 폭 10 → 3열 (ceil(10/3)=4 bay, span 2.5)
    assert len(mid_rail_lines(-5, 5, riser=0.20, tread=0.34)) == 3
    ok += 4

    # (3) 계단참: 3 m 이하면 없음, 초과하면 균등 분할
    p = stair_landings(3.0, 0.15, 0.30)
    assert p["n_landings"] == 0 and p["n_flights"] == 1
    p = stair_landings(6.0, 0.15, 0.34)          # scene14 제원
    assert p["n_steps"] == 40 and p["n_flights"] == 2 and p["n_landings"] == 1
    assert p["max_flight_rise"] <= K.LANDING_MAX_RISE + 1e-9
    assert abs(p["run_delta"] - 1.20) < 1e-9
    assert abs(p["z_bottom"] + 6.0) < 1e-9       # 총 낙차 보존
    p = stair_landings(6.12, 0.17, 0.34)         # scene09 제원(균등 근사)
    assert p["n_flights"] == 3 and p["n_landings"] == 2
    assert all(f["rise"] <= K.LANDING_MAX_RISE + 1e-9 for f in p["flights"])
    # 주택단지 2 m 주기
    p2 = stair_landings(6.0, 0.15, 0.34,
                        max_rise=K.LANDING_MAX_RISE_HOUSING)
    assert p2["n_flights"] == 4 and p2["n_landings"] == 3
    assert p2["max_flight_rise"] <= K.LANDING_MAX_RISE_HOUSING + 1e-9
    ok += 4

    # (4) 계획의 기하 연속성 — flight 끝 z == 다음 참 z == 다음 flight 시작 z
    p = stair_landings(9.0, 0.18, 0.30)
    for i, l in enumerate(p["landings"]):
        assert abs(p["flights"][i]["z_bot"] - l["z"]) < 1e-9
        assert abs(p["flights"][i + 1]["z_top"] - l["z"]) < 1e-9
        assert abs(p["flights"][i]["x1"] - l["x0"]) < 1e-9
        assert abs(p["flights"][i + 1]["x0"] - l["x1"]) < 1e-9
    assert abs(p["total_run"] - (p["n_steps"] * 0.30
                                 + p["n_landings"] * 1.20)) < 1e-9
    ok += 1

    # (5) 단코 선 — 계단참 도입은 단 수를 바꾸지 않는다(GT 총 에지 수 보존 +참)
    a = stair_landings(2.4, 0.15, 0.30)
    b = stair_landings(6.0, 0.15, 0.30)
    assert len(flight_nosing_lines(a)) == a["n_steps"]
    assert len(flight_nosing_lines(b)) == b["n_steps"] + b["n_landings"]
    ok += 1

    # (6) 적합성 판정
    r = check_stair_compliance(0.15, 0.38, 11.0, 0.60, outdoor=True,
                               has_rail="both", n_mid_rails=1)
    assert r["ok"] and r["req_mid_rails"] == 0 and r["mid_rail_exempt"]
    r = check_stair_compliance(0.173, 0.30, 4.0, 4.498, outdoor=True,
                               has_rail="both")
    assert r["req_landings"] == 1 and r["req_mid_rails"] == 1 and r["p0"] == 2
    r = check_stair_compliance(0.40, 0.85, 8.0, 1.20, outdoor=True)
    assert any(x["code"] == "D1" for x in r["violations"])
    r = check_stair_compliance(0.18, 0.30, 2.0, 0.90, outdoor=True,
                               has_rail="none")
    assert r["ok"], "낙차 0.90 ≤ 1 m → 난간 의무 없음"
    r = check_stair_compliance(0.18, 0.30, 2.0, 1.10, outdoor=True,
                               has_rail="none")
    assert any(x["code"] == "R2" for x in r["violations"])
    # 실내(공동사용) 기준에서는 riser 0.19 가 위반
    assert not check_stair_compliance(0.19, 0.30, 2.0, 0.5,
                                      outdoor=False)["outdoor_ok"]
    assert check_stair_compliance(0.19, 0.30, 2.0, 0.5,
                                  outdoor=True)["outdoor_ok"]
    ok += 6

    # (7) 손잡이 규격 검증 (프림 생성 없이 strict 예외만)
    made = []

    def _fake_cyl(stage, path, center, radius, height, mtl=None,
                  rotY=0.0, rotX=0.0, collider=False):
        made.append((path, center, radius, height, rotY))
        return path

    h = build_handrail(None, "/S/HR", 1.5, 0.0, 6.4, 3.2, None, _fake_cyl)
    names = [m[0] for m in made]
    assert "/S/HR/ExtTop" in names and "/S/HR/ExtBot" in names
    assert abs(dict((m[0], m[3]) for m in made)["/S/HR/ExtTop"] - 0.30) < 1e-9
    assert abs(h["z_top_rail"] - 0.85) < 1e-9
    assert abs(h["z_bot_rail"] - (-3.2 + 0.85)) < 1e-9
    for bad in (dict(dia=0.050), dict(ext_top=0.10)):
        try:
            build_handrail(None, "/S/X", 0.0, 0.0, 1.0, 0.5, None,
                           _fake_cyl, **bad)
            raise AssertionError("strict 위반이 통과했다: %r" % bad)
        except ValueError:
            pass
    # 벽부착: 이격 + 반지름만큼 벽에서 떨어진다
    hw = build_handrail(None, "/S/W", 0.0, 0.0, 3.0, 1.5, None, _fake_cyl,
                        wall_y=2.0, wall_side=-1.0, dia=0.036)
    assert abs(hw["y"] - (2.0 - (0.050 + 0.018))) < 1e-9
    ok += 3

    # (8) 계단참 판 — add_box 주입 검증
    boxes = []

    def _fake_box(stage, path, center, size, mtl=None, collider=False):
        boxes.append((path, center, size))
        return path

    plan = stair_landings(6.0, 0.15, 0.34)
    build_stair_landing(None, "/S/Land_0", plan["landings"][0],
                        -2.5, 2.5, -7.0, None, _fake_box)
    (_, ctr, siz) = boxes[0]
    assert abs(siz[0] - 1.20) < 1e-9 and abs(siz[1] - 5.0) < 1e-9
    assert abs(ctr[2] + (7.0 + 3.0) / 2.0) < 1e-9   # 상면 −3.0, 밑면 −7.0
    ok += 1

    print("stair_kit selfcheck: %d 그룹 통과 (USD/GPU 미사용)" % ok)
    return True


if __name__ == "__main__":
    _selfcheck()
