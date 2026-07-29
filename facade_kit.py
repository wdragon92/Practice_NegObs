# -*- coding: utf-8 -*-
"""facade_kit — 한국 도시 건물 **저층부(0~5 m)** 절차적 생성 키트.

근거 문서
---------
* `Docs/surveys/korean_urban_backdrop.md` (2026-07-28) — 우선순위 1~8,
  §3.3 저층부 · §3.4 외피 부착물 · §6.1 빠른참조 파라미터 표 · §5 씬 유형별 구성표
* `Docs/surveys/_dimension_index.md` — 확정 실측 치수 색인

왜 이 모듈이 필요한가 (측정된 사실 — 조사 §1.1·§1.3)
--------------------------------------------------
33씬 창 프림 **4,050개**. 판정 1순위 시점은 카메라 h0.3 m · pitch −10° · vFOV 36°
이므로 프레임 상단은 지평 위 **+8.0°** 뿐이다. 거리 d 에서 프레임에 들어오는
최고 높이 `z = 0.3 + d·tan(8°) ≈ 0.3 + 0.14·d`:

    d=10 m → 1.7 m · d=20 m → 3.1 m · d=34 m → 5.1 m · d=90 m → 12.9 m

→ **창의 약 88 %가 프레임 밖**이다(프림의 19 %를 안 보이는 곳에 쓰고 있다).
정작 화면을 채우는 지상 0~5 m 에는 셸 박스 한 면 말고 아무것도 없다.
이 모듈은 그 예산을 저층부로 옮기기 위한 것이다.

설계 규약
---------
1. **좌표계 Z-up, 단위 m.**
2. **scene_common 을 import 하지 않는다**(순환 참조 회피). 프리미티브 헬퍼는
   `Kit` 컨테이너로 **주입**받는다. `pxr` 만 함수 내부에서 지연 import 한다.
3. **RNG 100 % 결정적** — 내장 `hash()` 금지(PYTHONHASHSEED 로 프로세스마다
   바뀐다. 이 프로젝트에서 실제로 터진 버그다). `zlib.crc32` + `random.Random`.
4. **스케일 앵커 불가침** — 문 높이 2.10 · 실외기 0.80×0.55×0.30 ·
   난간 1.20 · 계단 단높이 0.15~0.18 · 소방 ∇ 0.20 은 **물리량 자체가 단서**다.
   절대 랜덤화하지 않는다. 개체차가 필요한 곳은 `_jit()` 로 **±8 % 이내**만.
   (과거에 수고를 uniform(1.45,1.85) 로 뭉개 단서를 지운 사고가 있었다.)
5. 모든 신규 기하는 **호출부에서 `LOOK_GEO` 게이트 안에서만** 불려야 한다
   (A/B 대조군 보존). 이 모듈의 함수 자체는 게이트를 모른다 — 알 필요가 없다.
6. 근거 없는 수치는 docstring 에 `[추정]`/`[지식]`/`[근거없음]` 표기 + 이유.

프림 예산 (동당) — 창 상한 절감분 2,500~3,000 보다 반드시 작아야 한다
-------------------------------------------------------------------
| 함수                      | 동당 프림              | 대표값(파사드 20 m, 5층) |
|---------------------------|------------------------|--------------------------|
| `build_plinth`            | **1**                  | 1                        |
| `build_shopfront`         | 2·bays + 3~5           | bays=4 → 11              |
| `build_aircon_units`      | 3/대 (bracket·pipe 끄면 1) | 4대 → 12             |
| `build_signage`           | 1 + n_proj             | n_proj=2 → 3             |
| `build_balcony_stack`     | 2 × bays × floors      | 2 bay × 3층 → 12         |
| `build_downpipe_run`      | 2·n_pipes + gas(2~2+2F)| n=2, gas A → 6           |
| `build_fire_access_marks` | 1/층·스테이션 (얇은 쿼드) | 3                     |
| **합계(상가형 1동)**      | —                      | **약 36**                |
| **합계(아파트형 1동)**    | —                      | **약 22**                |

도시 배경 건물이 라이브러리 전체에서 약 60동이므로 전량 적용해도
**36 × 60 ≈ 2,160 프림 < 창 상한 절감분 2,500~3,000**. 순 프림은 줄어든다.
"""

import math
import random
import zlib

__all__ = [
    "Kit", "Facade", "facade_from_bd",
    "frame_ceiling", "lod_tier", "floor_levels", "window_rows_visible",
    "build_plinth", "build_shopfront", "build_aircon_units", "build_signage",
    "build_balcony_stack", "build_downpipe_run", "build_fire_access_marks",
]

# ===========================================================================
# [0] 스케일 앵커 상수 — **랜덤화 금지**
# ===========================================================================
# 값 옆의 등급 표기는 조사 §6.1 을 따른다.
#   법정 = 법령 조문 확인 · 확실 = 표준/카탈로그 실측 · [추정] · [지식]
DOOR_H = 2.10            # 법정: 피난·방화구조 규칙 §16 반자높이 2.1 (기존 규약과 동일)
RAIL_H = 1.20            # 법정: 건축법 시행령 §40 — 노대·옥상 난간 1.2 이상
BALUSTER_GAP = 0.10      # 법정: 「발코니 등의 구조변경절차 및 설치기준」 0.10 이하
BALCONY_DEPTH = 1.50     # 법정: 건축법 시행령 §119 ①3 나목 — 노대 공제 1.5 m
SLAB_T = 0.21            # 법정: 주택건설기준 규정 §14의2 1호 — 슬래브 210 mm 이상
AC_W, AC_H, AC_D = 0.80, 0.55, 0.30   # [추정] 삼성 AR08HVAD1WK 0.720×0.548×0.265 +
                                      # LG SQ06EZAU 0.660×0.459×0.276 의 포괄값
AC_WALL_GAP = 0.10       # 확실: 제조사 설치 이격(뒷면 0.10~0.15)
FIRE_TRI_D = 0.20        # 법정: 피난·방화구조 규칙 §18의2 — 붉은 역삼각형 지름 0.20 이상
FIRE_SILL_MAX = 0.80     # 법정: 진입창 하단 높이 바닥에서 0.80 이내
FIRE_SPACING = 40.0      # 법정: 벽면 수평거리 40 m 이내마다 1개소 추가
GRANITE_T = 0.030        # 확실: 건축공사 표준시방서 석공사 — 건식 화강석 30 mm
SIGN_BAND_PROUD = 0.30   # 법정: 가로형간판 돌출 0.30 이내(서울)
SIGN_PROJ_OUT = 1.00     # 법정: 돌출간판 돌출폭 1.00 이내(서울, 심의 1.2)
SIGN_PROJ_T = 0.30       # 법정: 돌출간판 두께 0.30 이내(서울)
SIGN_PROJ_BOTTOM = 3.00  # 법정: 지면~하단 3.0 이상(인도 없으면 4.0)
STAIR_RISER = 0.16       # 법정 범위: 규칙 §15 단높이 0.15~0.18(0.15 이하면 중간난간 면제)
STAIR_TREAD = 0.32       # 법정: 규칙 §15 단너비 0.30 이상
GAS_BAND_W = 0.030       # 법정: KGS FU551 2.5.7.2 — 황색띠 폭 30 mm
GAS_BAND_Z = 1.00        # 법정: 각 층 바닥 +1 m
GAS_VALVE_Z = (1.60, 2.00)   # 확실: LH 도시가스 시방서 — 입상 주밸브 바닥 +1.6~2.0
DOWNPIPE_DN100 = 0.114   # 확실: KDS 31 30 35 DN100 → 외경 약 0.114
CAM_H = 0.30             # 판정 1순위 시점(grid_views)
CAM_PITCH = -10.0
CAM_VFOV = 36.0          # fixlog_W4 §155 · W5 §66 — v6 렌더 역산치

# 색(참고용 — 재질은 호출부가 만든다)
GAS_YELLOW = (0.86, 0.72, 0.10)   # 법정: KGS FU551 지상배관 황색
FIRE_RED = (0.72, 0.09, 0.08)     # 법정: 진입창 붉은 역삼각형


# ===========================================================================
# [1] 결정적 RNG — hash() 금지
# ===========================================================================
def _rng(*keys):
    """결정적 `random.Random`. 내장 `hash()` 는 PYTHONHASHSEED 로 프로세스마다
    바뀌므로 **절대 쓰지 않는다**(이 프로젝트에서 실제로 터진 버그).
    crc32 는 표준 라이브러리 고정 다항식이라 실행·플랫폼 무관하게 동일하다."""
    s = "|".join(str(k) for k in keys)
    return random.Random(zlib.crc32(s.encode("utf-8")) & 0xFFFFFFFF)


def _jit(rng, v, frac=0.08):
    """개체차 지터. **상한 ±8 % 고정** — 스케일 앵커를 뭉개지 않기 위한 하드 캡.
    frac 을 0.08 초과로 넘기면 0.08 로 잘린다(사고 재발 방지)."""
    f = min(abs(float(frac)), 0.08)
    return float(v) * (1.0 + rng.uniform(-f, f))


# ===========================================================================
# [2] 헬퍼 주입 컨테이너 · 파사드 좌표계
# ===========================================================================
class Kit:
    """scene_common 프리미티브 헬퍼 주입 컨테이너 (순환 import 회피).

    사용 예 (scene_common.build_building 안에서)::

        import facade_kit as fk
        K = fk.Kit(add_box, add_cylinder, _oriented_box)

    시그니처는 scene_common 현행 것을 그대로 기대한다::

        add_box(stage, path, center, size, mtl=None, collider=False)
        add_cylinder(stage, path, center, radius, height, mtl=None,
                     rotY=0.0, rotX=0.0, collider=False)
        oriented_box(stage, path, center, size, mtl=None, collider=False,
                     rotz=0.0, rotx=0.0)        # 선택 — 없으면 add_box 로 대체
    """

    def __init__(self, add_box, add_cylinder=None, oriented_box=None):
        if not callable(add_box):
            raise TypeError("Kit: add_box 는 호출 가능해야 한다")
        self.add_box = add_box
        self.add_cylinder = add_cylinder
        self.oriented_box = oriented_box

    def box(self, stage, path, center, size, mtl=None, collider=False):
        return self.add_box(stage, path, center, size, mtl, collider)

    def cyl(self, stage, path, center, radius, height, mtl=None, **kw):
        """add_cylinder 미주입 시 같은 부피의 박스로 대체(프림 수 동일)."""
        if self.add_cylinder is None:
            d = 2.0 * float(radius)
            return self.add_box(stage, path, center, (d, d, float(height)), mtl)
        return self.add_cylinder(stage, path, center, radius, height, mtl, **kw)


class Facade:
    """파사드 1면의 로컬 좌표계. 모든 빌더가 축 무관하게 동작하도록 하는 어댑터.

      axis_y=True  → 벽은 평면 y = `plane`, 가로(u) 는 **월드 X**
      axis_y=False → 벽은 평면 x = `plane`, 가로(u) 는 **월드 Y**
      fdir (+1/−1) : 벽 바깥을 향하는 방향(월드 축 부호). bd["face_dir"] 그대로.
      u0,u1        : 가로 범위(월드). base_z : 건물 기단 월드 z.

    `out` 은 **벽면에서 바깥으로 나간 거리(항상 양수)** 를 뜻한다. fdir 부호는
    Facade 가 흡수하므로 호출부·빌더는 부호를 신경 쓰지 않는다.
    """

    def __init__(self, plane, fdir, u0, u1, base_z=0.0, axis_y=True,
                 depth_ref=None):
        self.plane = float(plane)
        self.fdir = 1.0 if float(fdir) >= 0 else -1.0
        self.u0 = float(min(u0, u1))
        self.u1 = float(max(u0, u1))
        self.base_z = float(base_z)
        self.axis_y = bool(axis_y)
        # depth_ref: 파사드에 수직인 건물 안길이(옵션, 기단 wrap 계산용)
        self.depth_ref = depth_ref

    # -- 기하 변환 -------------------------------------------------------
    @property
    def width(self):
        return self.u1 - self.u0

    @property
    def mid(self):
        return 0.5 * (self.u0 + self.u1)

    def world(self, u, out, z):
        """(가로 u, 벽 바깥 거리 out, 높이 z) → 월드 (x, y, z)."""
        p = self.plane + self.fdir * float(out)
        if self.axis_y:
            return (float(u), p, float(z))
        return (p, float(u), float(z))

    def size(self, w_u, d_out, h):
        """(가로 폭, 벽 법선 방향 두께, 높이) → 월드 size 3튜플."""
        if self.axis_y:
            return (float(w_u), float(d_out), float(h))
        return (float(d_out), float(w_u), float(h))

    def tangent(self):
        """가로(u) 방향 월드 단위벡터 (x, y)."""
        return (1.0, 0.0) if self.axis_y else (0.0, 1.0)

    def normal(self):
        """벽 바깥 방향 월드 단위벡터 (x, y)."""
        return (0.0, self.fdir) if self.axis_y else (self.fdir, 0.0)


def facade_from_bd(bd):
    """기존 `build_building` 의 `bd` 딕셔너리에서 Facade 를 만든다.
    씬 파일 무수정 통합의 핵심 어댑터 — 키는 전부 현행 것만 읽는다."""
    axis_y = bd.get("axis", "y") == "y"
    base = float(bd.get("base_z", 0.0))
    if axis_y:
        return Facade(bd["facade_y"], bd["face_dir"], bd["x0"], bd["x1"],
                      base, True, depth_ref=abs(bd["y1"] - bd["y0"]))
    return Facade(bd["facade_x"], bd["face_dir"], bd["y0"], bd["y1"],
                  base, False, depth_ref=abs(bd["x1"] - bd["x0"]))


# ===========================================================================
# [3] 판정 카메라 가시 상한 — 창 프림 예산의 근거
# ===========================================================================
def frame_ceiling(dist_m, cam_h=CAM_H, cam_pitch_deg=CAM_PITCH,
                  vfov_deg=CAM_VFOV):
    """판정 카메라 프레임 **상단 모서리**가 거리 dist_m 에서 닿는 세계 z[m].

    프레임 상단 앙각 = pitch + vFOV/2 = (−10°) + 18° = **지평 위 +8.0°**
      → `z = cam_h + dist·tan(8°) ≈ cam_h + 0.1405·dist`
    검산(조사 §1.3 표와 일치): d=10→1.71 · 20→3.11 · 34→5.08 · 50→7.32 · 90→12.94

    출처: `Docs/audit_v4/fixlog_W4.md` §155 · `fixlog_W5.md` §66 (v6 렌더 역산 vFOV 36°),
          `grid_views(heights=(0.3,0.9,1.8), pitch=-10)`.
    프림 0.
    """
    up_deg = float(cam_pitch_deg) + float(vfov_deg) / 2.0
    return float(cam_h) + float(dist_m) * math.tan(math.radians(up_deg))


def lod_tier(dist_m):
    """조사 §6 LOD 표의 구간 이름. "near"(<20) / "mid"(20~40) / "far"(40~80)
    / "silhouette"(>80). 프림 0."""
    d = float(dist_m)
    if d < 20.0:
        return "near"
    if d < 40.0:
        return "mid"
    if d <= 80.0:
        return "far"
    return "silhouette"


def floor_levels(n_floors, floor_h=2.80, ground_h=None, base_z=0.0):
    """각 층 **바닥 z** 리스트(길이 n_floors+1, 마지막 원소 = 최상층 천장/옥상).

    조사 §3.1 의 필수 규칙 — 현행 `fstep = h / floors` 등간격은 폐기 대상이다
    (전 층 등간격이 지금 "CG로 읽히는" 큰 축)::

        z[0] = base_z
        z[1] = base_z + ground_h        # 1층만 다른 층고
        z[i] = z[1] + (i-1)*floor_h

    기본값 근거: 아파트 기준층 층고 **2.80~2.85**(확실 — 한국PM),
    근생 1층 3.9~4.2 · 2층 이상 3.3 은 **[추정]**(1차 출처 미확보).
    ground_h=None 이면 기준층과 동일(= 현행 동작 보존).
    프림 0.
    """
    n = max(1, int(n_floors))
    fh = float(floor_h)
    gh = fh if ground_h is None else float(ground_h)
    z = [float(base_z), float(base_z) + gh]
    for _ in range(n - 1):
        z.append(z[-1] + fh)
    return z[:n + 1]


def window_rows_visible(dist_m, floor_h, n_floors, ground_h=None, base_z=0.0,
                        cam_h=CAM_H, cam_pitch_deg=CAM_PITCH,
                        vfov_deg=CAM_VFOV, sill_up=0.90, margin_m=1.0,
                        near_dist=40.0, min_rows=1, cam_ground_z=0.0):
    """그 건물에서 **실제로 창을 만들 층수**(상한). 최소 1층은 보장.

    조사 §4 의 프림 예산 재배분 규칙::

        if 거리 > 40 m : 창은 z_sill ≤ (cam_h + d·tan 8°) 인 층에만 생성
        else           : 전 층 생성 + 저층부 상세

    - `sill_up` : 층 바닥에서 창 하단까지(기본 0.90 — 창대 일반높이 [추정];
      소방관 진입창 하단은 법정 0.80 이내이므로 그보다 약간 위로 잡았다).
    - `margin_m`: 프레임 상단 여유. 컷오프 층이 프레임 경계에서 잘려 보이는
      것을 막는 안전 여유 [추정 — 시각 안전마진, 근거 문서에 수치 없음].
    - `cam_ground_z`: 카메라가 선 지반의 월드 z(건물 base_z 와 다를 때만 지정).

    반환: 1 ≤ rows ≤ n_floors 인 int. 프림 0.

    절감 실측 (33씬 `buildings`/`far_buildings` AST 파싱 + 거리 = |파사드 평면|
    근사. 현행 창 합계 4,173 — 조사 §1.1 의 4,050 과 파싱 차이 범위 내)::

        near_dist=40, min_rows=1  (조사 §4 문자 그대로)  → 3,075  (−1,098)
        near_dist=20, min_rows=2  (권장 절충)            → 2,000  (−2,173)
        near_dist=0,  min_rows=2  (물리 그대로)          → 1,830  (−2,343)

    **권장은 near_dist=20, min_rows=2.** 조사가 예고한 2,500~3,000 절감에
    근접하면서, 20 m 이내 근접 건물은 전 층을 남겨 근접 시점 안전마진을 둔다.
    min_rows=2 는 최저 2개 층을 보장해 저층부 상세가 "창 없는 벽"에 붙는 것을 막는다.
    """
    n = max(1, int(n_floors))
    if float(dist_m) <= float(near_dist):
        return n
    ceil_z = frame_ceiling(dist_m, cam_h, cam_pitch_deg, vfov_deg) \
        + float(cam_ground_z) + float(margin_m)
    lv = floor_levels(n, floor_h, ground_h, base_z)
    rows = 0
    for f in range(n):
        if lv[f] + float(sill_up) <= ceil_z:
            rows += 1
        else:
            break
    return max(int(min_rows), min(rows, n))


# ===========================================================================
# [4] 우선순위 1 — 기단(基壇) 화강석 띠
# ===========================================================================
def build_plinth(K, stage, prefix, x0, x1, y0, y1, base_z, mtl,
                 height=1.10, proud=0.025, wrap=True, fac=None):
    """기단 석재 띠 (지상 0 ~ 약 1.2 m). **동당 프림 1개.**

    조사 우선순위 **1위** — h0.3 프레임 하단부를 직접 채우는데 현행은 셸 텍스처
    1장뿐이다. 프림 대비 효과가 라이브러리 전체에서 가장 크다.

    치수 근거
      · 석재 판 두께 **0.030** (확실 — 건축공사 표준시방서 석공사 /
        한국패시브건축협회 「외벽 화강석 두께」. 벽용 최소 0.020 이나 건식
        고정방식상 0.030)
      · 파사드면 대비 돌출 0.02~0.03 `[지식]` → 기본 `proud=0.025`
      · **붙임 높이는 `[근거없음]`** — 법정 기준이 없는 설계 재량 사항이다.
        조사가 제시한 두 패턴 중 창대 하단형 **0.9~1.2 m** 를 기본값으로 잡았다
        `[추정]`. 1층 전체형(3.0~3.6)을 원하면 height 로 넘길 것.
      · 상단 물끊기(드립) 홈은 출처 확보됐으나 치수 `[근거없음]` →
        **구현하지 않는다**(폭 0.01 급이라 판정 거리에서 픽셀 이하).

    wrap=True: 건물 풋프린트 전체를 감싸는 박스 1개(4면 동시, 프림 1).
    wrap=False: `fac` 로 준 파사드 1면만(프림 1). 셸과 z-fighting 을 피하려고
    항상 `proud` 만큼 바깥으로 나간다.

    재질: 화강석 버너구이(짙은 회색). 기존 `granite_dark` 텍스처 재사용 가능.
    재질 경로 이름에 "granite"/"stone" 이 들어가면 룩 레이어가 stone 역할로
    분류한다(scene_common `_LOOK_RULES`).
    """
    h = max(0.05, float(height))
    p = float(proud)
    zc = float(base_z) + h / 2.0
    if wrap or fac is None:
        cx = 0.5 * (float(x0) + float(x1))
        cy = 0.5 * (float(y0) + float(y1))
        sx = abs(float(x1) - float(x0)) + 2.0 * p
        sy = abs(float(y1) - float(y0)) + 2.0 * p
        return [K.box(stage, f"{prefix}/PlinthStone", (cx, cy, zc),
                      (sx, sy, h), mtl)]
    c = fac.world(fac.mid, p / 2.0, zc)
    s = fac.size(fac.width + 2.0 * p, p, h)
    return [K.box(stage, f"{prefix}/PlinthStone", c, s, mtl)]


# ===========================================================================
# [5] 우선순위 2 — 1층 상가 파사드
# ===========================================================================
def build_shopfront(K, stage, prefix, fac, mtl_glass, mtl_frame,
                    mtl_stone=None, ground_h=4.00, bay_w=5.00,
                    opening_h=2.60, kick_h=0.25, inset=0.12,
                    shutter_box=True, steps=1, door_bay=None,
                    max_bays=6, seed=0):
    """1층 상가 파사드: 개구 + 걸레받이 + 셔터박스 + 출입계단.
    **동당 프림 = 2·bays + 3~5** (bays=4 → 11~13, bays 상한 `max_bays`).

    조사 우선순위 **2위** — 0~3 m 는 h0.3 프레임의 대부분이다.

    치수 근거
      · 점포 간구(bay) 폭 4~6 m `[지식]` → 기본 5.0
      · 유리 개구 높이 **2.4~2.8**, 하단 걸레받이 0.15~0.30 `[지식]`
      · 출입문 폭 0.9~1.2 · 높이 **2.10** `[추정 — 옥상 대피공간 출입구 유효너비
        0.9 이상(건축법)에서 유추]`. **2.10 은 스케일 앵커라 랜덤화 금지.**
      · 출입 계단 1~2단, 단높이 **0.15~0.18**, 단너비 **0.30 이상**
        (법정 — 피난·방화구조 규칙 §15. 0.15 이하 + 0.30 이상이면 중간난간 면제)
      · 계단 난간은 **높이 1 m 초과** 시에만 의무(규칙 §15) → 1~2단(≤0.36)은
        난간 없음이 옳다. 프림도 아낀다.
      · 셔터박스 높이 0.25~0.40, 가이드레일 폭 0.06~0.08 `[추정 — 제조사 도면이
        DWG 내부에만 있어 미취득]` → 기본 0.32. 가이드레일은 bay 당 2개가 되어
        프림이 두 배가 되므로 **구현하지 않는다**(판정 거리에서 60 mm 는 소실).

    개구는 `inset` 만큼 벽 **안쪽**으로 들어간다(현행 window inset 규약과 동일 부호).
    걸레받이·셔터박스는 벽면보다 약간 바깥으로 나와 그림자 선을 만든다.
    """
    rng = _rng(prefix, "shopfront", seed)
    prims = []
    W = fac.width
    if W < 1.5:
        return prims
    nb = max(1, min(int(max_bays), int(round(W / max(2.0, float(bay_w))))))
    bw = W / nb
    z0 = fac.base_z
    gh = float(ground_h)

    # 출입 계단 (문 앞) — 먼저 만들어 개구 하단 기준면을 정한다
    ns = max(0, min(2, int(steps)))
    step_top = z0
    di = (nb // 2) if door_bay is None else max(0, min(nb - 1, int(door_bay)))
    du = fac.u0 + (di + 0.5) * bw
    dw = 1.00                                   # 문 폭 [추정] 0.9~1.2 중앙값
    for s in range(ns):
        # 단높이는 법정 범위(0.15~0.18) 안에서만 개체차를 준다 — 앵커 보존
        r = 0.15 + rng.random() * 0.03
        zt = step_top + r
        tread = STAIR_TREAD * (ns - s)          # 아래 단일수록 깊게(계단코 중첩)
        prims.append(K.box(
            stage, f"{prefix}/ShopStep_{s}",
            fac.world(du, tread / 2.0, (step_top + zt) / 2.0),
            fac.size(dw + 0.80, tread, r + 0.02),
            mtl_stone if mtl_stone is not None else mtl_frame))
        step_top = zt

    kb = float(kick_h)
    op_h = float(opening_h)
    op_z0 = z0 + kb
    op_z1 = min(op_z0 + op_h, z0 + gh - 0.45)   # 슬래브·간판 띠 자리 확보
    op_h = max(1.2, op_z1 - op_z0)

    for b in range(nb):
        u = fac.u0 + (b + 0.5) * bw
        gw = max(0.6, bw - 0.40)                # 간구 − 0.40 (기둥·프레임 몫)
        # 걸레받이(kick plate) — 석재/금속 띠
        prims.append(K.box(
            stage, f"{prefix}/ShopKick_{b}",
            fac.world(u, 0.03, z0 + kb / 2.0),
            fac.size(bw, 0.06, kb),
            mtl_stone if mtl_stone is not None else mtl_frame))
        # 유리 개구 — 벽 안쪽으로 inset
        prims.append(K.box(
            stage, f"{prefix}/ShopGlass_{b}",
            fac.world(u, -float(inset), (op_z0 + op_z1) / 2.0),
            fac.size(gw, 0.04, op_h), mtl_glass))

    # 출입문 — **높이 2.10 스케일 앵커**. 랜덤화하지 않는다.
    prims.append(K.box(
        stage, f"{prefix}/ShopDoor",
        fac.world(du, -float(inset) + 0.02, step_top + DOOR_H / 2.0),
        fac.size(dw, 0.06, DOOR_H), mtl_frame))

    # 셔터박스 — 개구 상단 인방
    if shutter_box:
        sb_h = 0.32                             # [추정] 0.25~0.40
        prims.append(K.box(
            stage, f"{prefix}/ShutterBox",
            fac.world(fac.mid, 0.09, op_z1 + sb_h / 2.0),
            fac.size(W - 0.20, 0.18, sb_h), mtl_frame))
    return prims


# ===========================================================================
# [6] 우선순위 3 — 에어컨 실외기 (한국 식별 최대 단서)
# ===========================================================================
def build_aircon_units(K, stage, prefix, fac, mtl_body, mtl_bracket=None,
                       levels=None, mode="perfloor", per_level=2,
                       eaves_z=2.30, count=None, bracket=True, pipe=True,
                       max_units=14, u_margin=0.8, z_max=6.0, seed=0):
    """에어컨 실외기 + 벽 거치대 + 냉매배관. **대당 프림 3개**
    (bracket=False, pipe=False 로 낮추면 대당 1개).

    조사 우선순위 **3위** — "한국 건물"과 "제네릭 서양 건물"을 가르는 **최대 단서**.
    설치 높이 1.5~2.6 m 가 **로봇 눈높이 정면**이라 판정 프레임 점유가 크다.
    현행 라이브러리 전체에서 실외기는 scene15 의 주택 2동에 1대씩뿐이다.

    치수 근거 (**전부 스케일 앵커 — 랜덤화 금지, 개체차는 ±8 % 이내**)
      · 삼성 벽걸이 AR08HVAD1WK 실외기 **0.720 × 0.548 × 0.265** (출처: 삼성전자)
      · LG 스탠드형 SQ06EZAU 실외기 **0.660 × 0.459 × 0.276** (출처: LG전자 2차)
      · → 모델링 대표값 **0.80 (W) × 0.55 (H) × 0.30 (D)** `[추정 — 위 둘의 포괄값]`
      · 벽면 이격(뒷면) **0.10~0.15** (출처 동일) → `AC_WALL_GAP = 0.10`
      · 벽 거치대: 고강도 알루미늄 앵글, 시판 폭 **800 / 900** 계열 (출처: 유성몰)
      · 거치대 설치 높이(하단) = 각 층 바닥 +0.2~0.6 `[추정]`
      · 밀도: 세대당 1~2대, 상가는 1층 처마 아래 열 지어 다수 `[지식]`

    mode
      "perfloor" : `levels`(= `floor_levels()` 결과) 의 각 층 바닥 +0.35 에
                   `per_level` 대. 다세대·아파트용.
      "eaves"    : 1층 처마 아래 한 줄(`eaves_z` 하단, 기본 2.30). 상가용 `[지식]`.

    ※ 2021년 건축법 시행령 §119 ①3 라목 개정으로 **신축**은 실외기를 발코니 안
      전용공간(1 m² 이하)에 넣는 추세다. 그러나 기존 다세대·상가 스톡(= 우리 씬
      배경의 대다수)은 여전히 외벽 노출이다. 노후 건물에만 켜면 시대 표현이 된다.
    """
    rng = _rng(prefix, "ac", seed)
    prims = []
    W = fac.width
    if W < 2.0:
        return prims

    slots = []
    if mode == "eaves":
        n = int(count) if count else max(2, int(W / 2.4))
        n = min(n, int(max_units))
        for i in range(n):
            u = fac.u0 + u_margin + (i + 0.5) * (W - 2 * u_margin) / max(1, n)
            slots.append((u, float(eaves_z)))
    else:
        lv = list(levels) if levels else [fac.base_z + 1.6]
        if len(lv) > 1:
            lv = lv[:-1]                        # 마지막은 옥상 슬래브
        # **눈높이 구간(층 바닥 ≤ base_z + z_max, 기본 6 m)만 생성한다.**
        # 그 위는 d≤40 m 에서 판정 프레임 밖이라(§1.3) 프림 낭비다.
        # 상가처럼 1층 층고가 4 m 면 1~2층만 남아 동당 12 프림 이하가 된다.
        lv = [z for z in lv if z <= fac.base_z + float(z_max)] or lv[:1]
        for f, zf in enumerate(lv):
            for k in range(max(1, int(per_level))):
                if len(slots) >= int(max_units):
                    break
                u = fac.u0 + u_margin + (k + 0.5) * \
                    (W - 2 * u_margin) / max(1, int(per_level))
                # 층당 좌우 배치에 결정적 미세 오프셋(줄 맞춰 늘어선 인상 회피)
                u += rng.uniform(-0.35, 0.35)
                slots.append((u, zf + 0.35))    # [추정] 층 바닥 +0.2~0.6

    for i, (u, zb) in enumerate(slots):
        w = _jit(rng, AC_W)                     # ±8 % 이내 개체차만
        hgt = _jit(rng, AC_H)
        dep = _jit(rng, AC_D)
        out_c = AC_WALL_GAP + dep / 2.0
        prims.append(K.box(
            stage, f"{prefix}/AcUnit_{i}",
            fac.world(u, out_c, zb + hgt / 2.0),
            fac.size(w, dep, hgt), mtl_body))
        if bracket:
            # 벽 거치 앵글 — 시판 폭 800/900 계열(출처: 유성몰)
            prims.append(K.box(
                stage, f"{prefix}/AcBracket_{i}",
                fac.world(u, (AC_WALL_GAP + dep) / 2.0, zb - 0.03),
                fac.size(w + 0.10, AC_WALL_GAP + dep, 0.06),
                mtl_bracket if mtl_bracket is not None else mtl_body))
        if pipe:
            # 냉매·드레인 배관 커버 — 벽에 붙어 아래로 내려간다.
            # 표준 배관 길이는 벽걸이 5 m / 스탠드 8 m (출처: LG 설치가이드)이나
            # 노출 구간 길이는 `[추정]` — 실외기 하단에서 0.9 m 만 표현한다.
            prims.append(K.cyl(
                stage, f"{prefix}/AcPipe_{i}",
                fac.world(u + w / 2.0 + 0.07, 0.05, zb - 0.45),
                0.028, 0.90,
                mtl_bracket if mtl_bracket is not None else mtl_body))
    return prims


# ===========================================================================
# [7] 우선순위 4 — 간판 (가로형 · 돌출형)
# ===========================================================================
def build_signage(K, stage, prefix, fac, mtl_panel, mtl_frame=None,
                  band_z=None, band_h=0.80, band_len_max=10.0,
                  n_projecting=2, proj_seg_h=1.20, proj_gap=0.22,
                  sidewalk=True, corner="u1", seed=0):
    """가로형(벽면) 간판 띠 + 돌출간판 **수직 스택**.
    **동당 프림 = 1 + n_projecting** (기본 3).

    조사 우선순위 **4위** — 저층부 실루엣을 가장 크게 바꾼다.
    수치가 **법령으로 고정**돼 있어 이 문서에서 신뢰도 최고 항목이다.
    (출처: 옥외광고물법 시행령 + **서울특별시 옥외광고물 조례**.
     씬이 서울 배경이므로 서울 조례값을 쓴다 — 인천·의성은 값이 다르다.)

    가로형(벽면 이용) 간판 — 법정
      · 개수 1업소 1개 · 가로 길이 건물 폭 이내, **최대 10 m**
      · 세로 폭 건물 높이의 1/2 초과 불가 (창문 부착 시 판류형 **0.80**)
      · **돌출 폭 0.30 이내**(특례 0.40, 전광류 1.80)

    돌출간판 — 법정(서울)
      · 지면~하단 **3.0 이상**(인도 없으면 **4.0**, 의료·약국·미용 2.0)
      · 돌출 폭 **1.00 이내**(심의 1.2) · 두께 **0.30 이내**(심의 0.5)
      · 세로 길이 **3.5 이내** · 벽면과의 간격 **0.30 이내**
      · 1업소 1개, 복수 업소는 **일직선 정렬** ← 이 정렬이 한국 상가 가로의
        가장 강한 시각 서명이다. 그래서 스택 u 좌표를 공유한다.
      · `proj_seg_h` 기본 1.20 은 다업소 스택 시 1개 세로 길이 `[추정]`
        (법정 상한 3.5 를 넘지 않도록 내부에서 클램프).

    band_z=None 이면 1층 개구 상단 자리 z ≈ base_z + 3.30 `[추정]`.
    corner: "u1"(가로 최대 끝) / "u0" — 돌출 스택을 놓을 파사드 모서리.
    """
    rng = _rng(prefix, "sign", seed)
    prims = []
    W = fac.width
    if W < 2.0:
        return prims

    # --- 가로형 띠 (법정: 최대 10 m, 돌출 0.30 이내) ---------------------
    bz = (fac.base_z + 3.30) if band_z is None else float(band_z)
    bh = min(float(band_h), 0.80)
    blen = min(W - 0.40, float(band_len_max))
    if blen > 0.8:
        prims.append(K.box(
            stage, f"{prefix}/SignBand",
            fac.world(fac.mid, SIGN_BAND_PROUD / 2.0, bz + bh / 2.0),
            fac.size(blen, SIGN_BAND_PROUD, bh), mtl_panel))

    # --- 돌출간판 수직 스택 (일직선 정렬) --------------------------------
    n = max(0, int(n_projecting))
    if n:
        # 벽면 간격 0.30 이내 → 근단 out=0.10, 원단 out=1.00
        near_out, far_out = 0.10, SIGN_PROJ_OUT
        d = far_out - near_out
        u = (fac.u1 - 0.70) if corner == "u1" else (fac.u0 + 0.70)
        z = fac.base_z + (SIGN_PROJ_BOTTOM if sidewalk else 4.00)
        seg = min(float(proj_seg_h), 3.50)      # 법정 세로 3.5 이내
        for i in range(n):
            h_i = _jit(rng, seg)                # ±8 % 이내 개체차
            prims.append(K.box(
                stage, f"{prefix}/SignProj_{i}",
                fac.world(u, near_out + d / 2.0, z + h_i / 2.0),
                fac.size(SIGN_PROJ_T, d, h_i),  # 가로=두께 0.30, 벽법선=돌출
                mtl_frame if mtl_frame is not None else mtl_panel))
            z += h_i + float(proj_gap)
    return prims


# ===========================================================================
# [8] 우선순위 5 — 발코니 슬래브 + 난간 (아파트를 아파트로 만든다)
# ===========================================================================
def build_balcony_stack(K, stage, prefix, fac, levels, mtl_slab, mtl_rail,
                        bay_w=9.00, core_every=3, depth=BALCONY_DEPTH,
                        slab_t=SLAB_T, rail_h=RAIL_H, start_floor=1,
                        max_floors=None, balusters=False,
                        baluster_r=0.010, seed=0):
    """발코니 슬래브 + 난간 스택. **동당 프림 = 2 × (사용 베이 수) × (층수)**
    (balusters=True 면 베이·층당 살 개수가 더해진다 — 기본 False).

    조사 우선순위 **5위**이자 중요한 사실: **현행 창 격자보다 프림이 싸다.**
    (현행 = 층 × ncols 창 + 층당 SillBand. 발코니 = 층 × 세대 × 2.
     bay 9 m 는 col_step 2.5 m 의 3.6배라 프림이 1/1.8 로 준다.)

    치수 근거
      · 발코니 깊이 **1.50** (화단 설치 시 최대 2.00) — **법정**:
        건축법 시행령 §119 ①3 나목(노대 공제 = 외벽 접한 길이 × 1.5)
      · 난간 높이 **1.20 이상** — **법정**: 건축법 시행령 §40
      · 난간살 간격 **0.10 이하** — **법정**: 「발코니 등의 구조변경절차 및 설치기준」
      · 슬래브 두께 **0.21 이상** — **법정**: 주택건설기준 규정 §14의2 1호
      · 세대 파사드 폭 8~12 m, 세대 사이 계단실/EV 코어 폭 2.5~3.5 m `[지식]`
        → **코어 베이가 파사드 리듬을 끊는 결정적 요소**이며 현행에는 없다.
          `core_every=3` = 3베이마다 1베이를 코어로 비운다.

    **난간 1.20 은 스케일 앵커라 랜덤화 금지.** 깊이·슬래브만 ±8 % 이내 개체차.
    `levels` 는 `floor_levels()` 결과(층 바닥 z 리스트)를 그대로 넘긴다.
    `max_floors` 로 `window_rows_visible()` 상한을 그대로 물려줄 수 있다.
    """
    rng = _rng(prefix, "balcony", seed)
    prims = []
    W = fac.width
    if W < 3.0 or not levels:
        return prims
    nb = max(1, int(round(W / max(3.0, float(bay_w)))))
    bw = W / nb
    lv = list(levels)[:-1]                      # 마지막은 옥상 슬래브
    f0 = max(0, int(start_floor))
    if max_floors is not None:
        lv = lv[:max(1, int(max_floors))]
    dep = _jit(rng, float(depth))
    st = max(0.10, float(slab_t))
    rh = float(rail_h)                          # 앵커 — 지터 없음

    for f in range(f0, len(lv)):
        zf = lv[f]
        for b in range(nb):
            if core_every and (b % int(core_every)) == int(core_every) - 1:
                continue                        # 계단실/EV 코어 베이 — 발코니 없음
            u = fac.u0 + (b + 0.5) * bw
            # 슬래브 — 상면이 층 바닥과 플러시
            prims.append(K.box(
                stage, f"{prefix}/BalconySlab_{f}_{b}",
                fac.world(u, dep / 2.0, zf - st / 2.0),
                fac.size(bw - 0.30, dep, st), mtl_slab))
            # 난간 — 높이 1.20(법정 최소). 슬래브 바깥 끝에 선다.
            prims.append(K.box(
                stage, f"{prefix}/BalconyRail_{f}_{b}",
                fac.world(u, dep - 0.04, zf + rh / 2.0),
                fac.size(bw - 0.30, 0.06, rh), mtl_rail))
            if balusters:
                # 법정 안목 0.10 이하 — 실물은 예외 없이 촘촘하다.
                # 프림이 베이당 (bw-0.3)/0.12 ≈ 70개로 폭증하므로 **근접
                # 건물(<20 m)에만** 켤 것.
                pitch = 2.0 * float(baluster_r) + BALUSTER_GAP
                x = u - (bw - 0.30) / 2.0 + pitch * 0.5
                k = 0
                while x < u + (bw - 0.30) / 2.0:
                    prims.append(K.cyl(
                        stage, f"{prefix}/BalconyBal_{f}_{b}_{k}",
                        fac.world(x, dep - 0.04, zf + rh / 2.0),
                        float(baluster_r), rh, mtl_rail))
                    x += pitch
                    k += 1
    return prims


# ===========================================================================
# [9] 우선순위 6 — 우수관 수직선 + 노출 가스배관
# ===========================================================================
def build_downpipe_run(K, stage, prefix, fac, top_z, mtl_pipe,
                       n_pipes=2, dn=DOWNPIPE_DN100, wall_gap=0.05,
                       elbow=True, gas=False, gas_levels=None,
                       mtl_gas=None, mtl_band=None, gas_variant="A",
                       gas_u=None, seed=0):
    """우수관(세로 홈통) 수직선 + 외벽 노출 가스배관.
    **동당 프림 = 2·n_pipes + 가스(변형 A: 2 / 변형 B: 2 + 2×층수)**
    (기본 n_pipes=2, gas=True, 변형 A → **6개**).

    조사 우선순위 **6위** — 프림 1~3개로 파사드 평면성을 깬다.
    파사드 모서리의 **수직선 1본**이 실루엣 기여 대비 가장 싸다.

    우수관 근거
      · 관경 vs 지붕 수평투영면적(강우 100 mm/h): **DN 50 → 67 m² ·
        DN 100 → 427 m² · DN 150 → 1,254 m²**
        (출처: **KDS 31 30 35 : 2016** 우수배수설비 설계기준)
      · 총 길이 3 m 미만 지관은 DN 75 가능 · 수평지관 기울기 1/100 이상 (출처 동일)
      · 산정 시 **외벽면적의 1/2을 지붕면적에 포함**, 안전계수 1.5 (출처 동일)
      · → 모델링 권장 다세대·상가 **DN 100(외경 0.114)** `[추정 — 위 표에서 유도]`
      · 설치 간격 파사드 모서리 + 8~12 m 마다 1본 `[추정]`
      · 벽면 이격 0.05(밴드 고정) `[지식]` · 하단 지면 +0.3 에서 90° 엘보 `[추정]`
      · 재질·색은 `[추정]` (KDS 원문 재질 규정 미취득) — 회색 PVC 가정

    가스배관 근거 — **KGS FU551 2.5.7.2** (한국 특유. 확인 완료)
      · **지상배관 표면색 = 황색**(부식방지도장 후)
      · **황색 대체 표시**: 건축물 내·외벽 노출 지상배관은 바닥(2층 이상은 각 층
        바닥)에서 **1 m 높이에 폭 0.030 m 황색 띠 2중** 표시 시 황색 도장 면제
      · 세대 내부 배관경 **0.020** (출처: LH 도시가스 설비공사 시방서 201206_54510)
      · 공용 입상관 0.032~0.040 `[추정]`
      · **입상배관 주밸브 설치높이 바닥에서 1.6~2.0 m** (출처 동일)
        → **로봇 눈높이(0.3~1.8 m) 정면**이라 효과가 크다
      · 배관 고정장치 간격은 `[근거없음]`(시행규칙 별표7 PDF 추출 실패) → 미구현

    gas_variant
      "A" : 입상관 전체 황색 도장. 노후 다세대에서 매우 흔함 `[지식]`. 프림 2.
      "B" : 회색 도장 + 각 층 바닥 +1.00 에 폭 0.030 황색 띠 2줄 (**법정 대체표시**).
            프림 2 + 2×층수. `mtl_band` 를 반드시 넘길 것.
    """
    rng = _rng(prefix, "downpipe", seed)
    prims = []
    W = fac.width
    z0 = fac.base_z
    zt = float(top_z)
    if zt - z0 < 1.0:
        return prims
    r = max(0.02, float(dn) / 2.0)
    out_c = float(wall_gap) + r

    n = max(1, int(n_pipes))
    for i in range(n):
        # 모서리 우선 배치(조사: 파사드 모서리 + 8~12 m 마다 1본 [추정])
        if n == 1:
            u = fac.u1 - 0.45
        else:
            u = fac.u0 + 0.45 + i * (W - 0.90) / (n - 1)
        h = zt - z0 - 0.30
        prims.append(K.cyl(
            stage, f"{prefix}/Downpipe_{i}",
            fac.world(u, out_c, z0 + 0.30 + h / 2.0), r, h, mtl_pipe))
        if elbow:
            # 지면 +0.3 에서 90° 엘보로 배출 [추정]
            prims.append(K.box(
                stage, f"{prefix}/DownpipeElbow_{i}",
                fac.world(u, out_c + 0.06, z0 + 0.18),
                fac.size(2 * r, 2 * r + 0.12, 0.26), mtl_pipe))

    if not gas:
        return prims

    mg = mtl_gas if mtl_gas is not None else mtl_pipe
    gu = fac.u0 + 0.95 if gas_u is None else float(gas_u)
    gr = 0.018                                  # 공용 입상관 0.032~0.040 [추정]
    gh = zt - z0 - 0.10
    prims.append(K.cyl(
        stage, f"{prefix}/GasRiser",
        fac.world(gu, 0.06 + gr, z0 + gh / 2.0), gr, gh, mg))
    # 입상 주밸브 — 바닥 +1.6~2.0 (확실). 눈높이 정면.
    vz = z0 + rng.uniform(*GAS_VALVE_Z)
    prims.append(K.box(
        stage, f"{prefix}/GasValve",
        fac.world(gu, 0.06 + gr, vz),
        fac.size(0.16, 2 * gr + 0.10, 0.14), mg))

    if str(gas_variant).upper() == "B" and gas_levels:
        # 법정 대체표시: 각 층 바닥 +1.00 에 폭 0.030 황색 띠 **2줄**.
        # 띠 간격은 별도 규정 없음 → 0.06 [추정] (조사 권장 0.05~0.10).
        mb = mtl_band if mtl_band is not None else mg
        for f, zf in enumerate(list(gas_levels)[:-1] or list(gas_levels)):
            for k in range(2):
                prims.append(K.box(
                    stage, f"{prefix}/GasBand_{f}_{k}",
                    fac.world(gu, 0.06 + gr,
                              zf + GAS_BAND_Z + k * 0.06),
                    fac.size(2 * gr + 0.01, 2 * gr + 0.01, GAS_BAND_W), mb))
    return prims


# ===========================================================================
# [10] 우선순위 7.5 — 소방관 진입창 붉은 역삼각형 데칼 (가장 값싼 한국 신호)
# ===========================================================================
def _bind(prim, mtl):
    if mtl is not None:
        from pxr import UsdShade
        UsdShade.MaterialBindingAPI.Apply(prim).Bind(mtl)


def build_fire_access_marks(stage, prefix, fac, levels, mtl_decal,
                            tri_d=FIRE_TRI_D, spacing_m=FIRE_SPACING,
                            floor_min=2, floor_max=11, sill_up=FIRE_SILL_MAX,
                            win_h=1.20, out=0.010, max_floors=None,
                            hit_mark=False):
    """**소방관 진입창 붉은 역삼각형(∇) 데칼.**
    **동당 프림 = (스테이션 수) × (표시 층수)** — 얇은 삼각 쿼드 1개/개소.
    우리 건물 대부분은 파사드 폭 40 m 미만이라 스테이션 1개소, 표시 2~4층 →
    **동당 2~4 프림**. 가장 값싼 한국 신호다.

    조사 우선순위 **7.5** — 2~11층 건축물에 **법정 의무**라 실제로 100 % 있다.
    현재 라이브러리에는 0개.

    법정 근거: 건축물의 피난·방화구조 등의 기준에 관한 규칙 **제18조의2**
      · 설치: 각 층마다 1개소 이상, 벽면 **수평거리 40 m 이내마다 추가**
      · 창 크기: 폭 **0.9 이상**, 높이 **1.2 이상**(2024.8.26 개정 1.0 이상)
      · 창 하단 높이: 실내 바닥에서 **0.8 이내**(난간 있는 노대는 1.2 이내)
      · **표시: 창 중앙에 지름 0.20 이상 붉은 역삼각형(∇)** — 야간 반사
      · 타격지점: 모서리에 지름 0.03 이상 원형 표시
        → `hit_mark=True` 로만 생성. 0.03 은 판정 거리(≥10 m)에서 픽셀 이하라
          기본은 **끈다**(프림 절약).

    기하: 원 지름 `tri_d` 에 내접하는 정삼각형, **꼭짓점이 아래**를 향한다.
    벽면에서 `out`(기본 0.010) 만큼 띄운 3정점 Mesh — z-fighting 회피용 최소값.
    `subdivisionScheme="none"` 을 **명시 저작**한다(USD 기본 catmullClark 가
    삼각형을 둥글게 당겨 ∇ 형태를 무너뜨린다 — build_sign 과 같은 이유).
    doubleSided=True 로 두어 winding 방향 버그를 원천 차단한다(프림 수 동일).

    재질: 붉은 상수색(`FIRE_RED`) 권장. 재질 경로에 "sign"/"placard" 계열
    토큰을 넣으면 룩 레이어가 sign 역할로 분류해 상수색을 보존한다
    (v5.1 §4 — 표지·도색의 상수색 불가침).
    """
    from pxr import UsdGeom, Gf

    prims = []
    if not levels:
        return prims
    W = fac.width
    R = max(0.03, float(tri_d) / 2.0)
    lv = list(levels)[:-1] if len(levels) > 1 else list(levels)
    if max_floors is not None:
        lv = lv[:max(1, int(max_floors))]

    n_st = max(1, int(math.ceil(W / float(spacing_m))))

    for s in range(n_st):
        u = fac.u0 + (s + 0.5) * (W / n_st)
        for f, zf in enumerate(lv):
            fl = f + 1                          # 1-based 층 번호
            if fl < int(floor_min) or fl > int(floor_max):
                continue
            # 창 중앙 z = 층 바닥 + 하단높이(0.8 법정 상한) + 창 높이/2
            zc = zf + float(sill_up) + float(win_h) / 2.0
            # 정삼각형(꼭짓점 아래): 각도 −90°, 30°, 150°
            pts = []
            for ang in (-90.0, 30.0, 150.0):
                a = math.radians(ang)
                du, dz = R * math.cos(a), R * math.sin(a)
                pts.append(Gf.Vec3f(*[float(v) for v in
                                      fac.world(u + du, out, zc + dz)]))
            path = f"{prefix}/FireMark_{s}_{fl}"
            mesh = UsdGeom.Mesh.Define(stage, path)
            mesh.CreatePointsAttr(pts)
            mesh.CreateFaceVertexCountsAttr([3])
            mesh.CreateFaceVertexIndicesAttr([0, 1, 2])
            mesh.CreateSubdivisionSchemeAttr("none")
            mesh.CreateDoubleSidedAttr(True)
            # extent 는 수동 계산한다. UsdGeom.PointBased.ComputeExtent 는
            # 바인딩 버전마다 정적/인스턴스 시그니처가 갈려 안전하지 않다.
            mesh.CreateExtentAttr([
                Gf.Vec3f(*[min(p[i] for p in pts) for i in range(3)]),
                Gf.Vec3f(*[max(p[i] for p in pts) for i in range(3)])])
            _bind(mesh.GetPrim(), mtl_decal)
            prims.append(mesh)

            if hit_mark:
                # 타격지점 원형 지름 0.03 (법정) — 모서리(우상단) 근처
                hp = []
                for ang in (0.0, 120.0, 240.0):
                    a = math.radians(ang)
                    du, dz = 0.015 * math.cos(a), 0.015 * math.sin(a)
                    hp.append(Gf.Vec3f(*[float(v) for v in fac.world(
                        u + 0.35 + du, out, zc + R + 0.10 + dz)]))
                hm = UsdGeom.Mesh.Define(stage, f"{prefix}/FireHit_{s}_{fl}")
                hm.CreatePointsAttr(hp)
                hm.CreateFaceVertexCountsAttr([3])
                hm.CreateFaceVertexIndicesAttr([0, 1, 2])
                hm.CreateSubdivisionSchemeAttr("none")
                hm.CreateDoubleSidedAttr(True)
                _bind(hm.GetPrim(), mtl_decal)
                prims.append(hm)
    return prims
