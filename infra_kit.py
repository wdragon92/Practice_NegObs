# -*- coding: utf-8 -*-
"""infra_kit.py — 배수·노면·옹벽 상세 절차적 생성 키트 (Isaac Sim 4.5 / USD)

작성 2026-07-29 · 대상: NegObs 33씬 (본편 21 + 배치1 12)

## 왜 이 파일이 있는가 (측정된 사실)

1. **배수 요소가 33씬 전부 0건이다.**
   `cue_arrangement_survey.md` §4.3① — `배수/빗물/측구/우수/drain/gutter/manhole/집수`
   전수 grep 결과 본편 21씬에 **하나도 없다**. 실제 한국 보도·도로에서
   빗물받이는 직선부 20~25 m 간격으로 **반드시** 있고(국도건설공사 설계실무요령
   3.배수공 파), L형 측구는 차도 가장자리에 연속으로 있다(동 3.배수공 2)).
   이것이 없으면 "포장은 있는데 물이 어디로도 안 가는 무대"다.

2. **scene13 은 주차장법 시행규칙 §6①5다가 의무화한 램프 양측 연석이 통째로 없다.**
   (h 10~15 cm, 양쪽 벽면으로부터 30 cm 이상 지점) — 미관 문제가 아니라
   **낙차선이 하나 더 있어야 하는데 없는 것**이라 연구 라벨에 직접 걸린다.

3. 측구·빗물받이·맨홀은 노면의 **선형 단서**이고 그 자체로 소형 낙차다.
   본 연구(RGB 맥락단서 → 비가시 낙차 추정)의 입력 신호에 직결된다.

## 규약 (전 함수 공통)

- **좌표계 Z-up, 단위 m.**
- **RNG 100 % 결정적** — `hash()` 절대 금지(PYTHONHASHSEED 로 프로세스마다
  달라진다. 실제로 터진 버그다). `zlib.crc32` → `random.Random(seed)` 만 쓴다.
- **`scene_common` 을 import 하지 않는다.** 프리미티브 헬퍼는 `Kit` 로 주입받는다
  (순환 참조 방지). `kit_from_scene_common(sc, stage)` 는 **이미 import 된 모듈
  객체를 인자로 받는 것**이지 import 가 아니다.
- **줄눈·이음은 별도 프림 폭증 없이** 처리한다. 측구 줄눈은 "베이스 슬래브 +
  패널" 2층 구조의 **패널 간 틈**(실제 지오메트리 홈), 옹벽 수축이음은 1 mm 돌출
  암색 스트립(음각 대용)이다. 각 함수 docstring 에 **미터당/개당 프림 수** 명시.
- 근거 없는 수치는 지어내지 않는다. 색인(`Docs/surveys/_dimension_index.md`)에
  없으면 `[추정]` / `[근거 없음]` 표기 + 근거 서술.
- 각 함수 docstring 의 **`GT:` 줄**이 그 함수가 만드는 것이 GT 낙차로
  카운트되는지를 규정한다. 통합 담당자는 이 줄만 읽어도 라벨 영향을 알 수 있다.

## GT 낙차 영향 요약 (이 줄만 봐도 됨)

| 함수 | GT 낙차 생성 | 비고 |
|---|---|---|
| `build_gutter_L`        | **아니오** | 단 연석 노출고가 `width*cross_slope`(≈18~30 mm) 만큼 커진다 → 연석 GT 재계산 |
| `build_gully`           | `lid=True` 아니오 / **`lid=False` 예** | 무개구 시 낙차 = `body_h`(0.64 m) |
| `build_manhole`         | `lid=True` 아니오 / **`lid=False` 예** | flush ±10 mm 는 minor step 미만 |
| `build_ramp_curb`       | **예** | 연석 상면 → 차로면 = `height`(0.10~0.15 m). **낙차선 신설** |
| `build_road_marking`    | 아니오 | 도색 두께 ≤4 mm. 스케일 앵커 전용 |
| `build_retaining_wall_details` | 아니오(기본) | `cope_flush=False` 로 두면 옹벽 상단 GT 가 `cope_h` 만큼 **증가** |
| `build_tactile_pair`    | 아니오 | 돌기 5~6 mm |

## 사용 예

```python
import infra_kit as ik
kit = ik.kit_from_scene_common(sc, stage)          # sc = 이미 import 된 scene_common
ik.build_gutter_L(kit, f"{ROOT}/Gutter", 0.0, -4.0, 60.0, -4.0,
                  top_z=0.0, mtl=M["concrete"])
for x in ik.gully_positions(0.0, 60.0, sag_points=(23.5,)):
    ik.build_gully(kit, f"{ROOT}/Gully_{x:.0f}", x, -3.75, 0.0, M["steel"])
```

Isaac 없이 프림 수·기하만 검산: `python3 infra_kit.py`
"""

from __future__ import annotations

import math
import random
import zlib

__all__ = [
    "Kit", "kit_from_scene_common", "dry_kit",
    "det_seed", "det_rng",
    "INFRA_DIMENSIONS", "TACTILE_YELLOW",
    "build_gutter_L", "gully_positions", "build_gully", "build_manhole",
    "build_ramp_curb", "build_road_marking", "wall_joint_positions",
    "build_retaining_wall_details", "build_tactile_pair",
]


# ===========================================================================
# [0] 치수 원장 — 코드에 박히는 모든 수치의 출처를 여기 한 곳에 모은다.
#     값을 바꾸려면 **먼저 이 표의 근거를 갱신**하라. 표에 없는 수치를 함수
#     기본값으로 넣는 것을 금지한다(지어낸 값 방지).
# ===========================================================================
INFRA_DIMENSIONS = {
    # ── L형 측구 ────────────────────────────────────────────────────────
    "gutter_L_width":       (0.30, "확인", "국도건설공사 설계실무요령 3.배수공 2) 형식-1 도면 (300/500)"),
    "gutter_L_width_alt":   (0.50, "확인", "동 (형식-1 대안 폭)"),
    "gutter_L_thick":       (0.20, "확인", "동 (두께 200)"),
    "gutter_contraction":   (6.00, "확인", "동 ※ 수축줄눈 간격 6 m (형식-1,2,4,5)"),
    "gutter_expansion":     (20.0, "확인", "동 ※ 신축이음재(스치로폴) 간격 20 m (형식-3 은 12 m)"),
    "gutter_floor_grade":   (0.06, "추정", "원문은 바닥경사 4~10 % 범위. 6 % 는 그 중앙값 [추정]"),
    "gutter_groove_w":      (0.008, "추정", "L형 측구 줄눈 폭 원문 없음. 옹벽 수축이음 6~8 mm 준용 [추정]"),
    "gutter_groove_d":      (0.014, "추정", "동. 옹벽 수축이음 깊이 12~16 mm 준용 [추정]"),
    # ── 빗물받이 ────────────────────────────────────────────────────────
    "grate_across":         (0.40, "확인", "국도 실무요령 수량내역서 집수정용 스틸그레이팅 400×500×50"),
    "grate_along":          (0.50, "확인", "동"),
    "grate_thick":          (0.05, "확인", "동"),
    "gully_body_across":    (0.410, "추정", "업계 통용 410×510×H640. 원문 미확인 [추정]"),
    "gully_body_along":     (0.510, "추정", "동 [추정]"),
    "gully_body_h":         (0.640, "추정", "동 [추정]"),
    "gully_spacing":        (22.0, "확인", "동 3.배수공 파: 직선부 20~25 m. 22 는 그 중앙"),
    "gully_spacing_max":    (25.0, "확인", "동 (상한)"),
    # ── 맨홀 ────────────────────────────────────────────────────────────
    "manhole_d_648":        (0.648, "확인", "KS D 4040 인증제품 / 국도 실무요령 3.17 (차도 회주철·보도 칼라 공통)"),
    "manhole_d_766":        (0.766, "확인", "동 (옵션)"),
    "manhole_d_918":        (0.918, "확인", "동 (옵션)"),
    "manhole_thick":        (0.110, "확인", "동 110t"),
    "manhole_flush_tol":    (0.010, "확인", "노면과 동일면 ±10 mm (임무 지시 / 실무 ±10~20 mm)"),
    "manhole_frame_w":      (0.045, "추정", "틀 링 폭. 원문 없음 [추정]"),
    # ── 주차장 램프 연석 ─────────────────────────────────────────────────
    "ramp_curb_h_min":      (0.10, "확인", "주차장법 시행규칙 §6①5다 — 높이 10~15 cm"),
    "ramp_curb_h_max":      (0.15, "확인", "동"),
    "ramp_curb_offset":     (0.30, "확인", "동 — 양쪽 벽면으로부터 30 cm 이상 지점"),
    # ── 노면표시 ────────────────────────────────────────────────────────
    "stall_w":              (2.50, "확인", "주차장법 시행규칙 §3 일반형 2.5×5.0 (확장형 2.6×5.2)"),
    "stall_l":              (5.00, "확인", "동"),
    "crosswalk_stripe":     (0.45, "확인", "도로교통법 시행규칙 별표6 노면표시 / scene_composition_audit §(6)"),
    "crosswalk_gap":        (0.45, "확인", "동"),
    "marking_line_w":       (0.15, "추정", "주차구획 실선 두께. 통상 10~15 cm, 원문 미확인 [추정]"),
    "marking_proud":        (0.003, "추정", "도색 두께. 원문 없음 [추정]. 4 mm 이하면 낙차 아님"),
    # ── 옹벽 ────────────────────────────────────────────────────────────
    "weep_d":               (0.100, "확인", "도로설계요령 3권 8-7편 옹벽 6 — 직경 100 mm 정도"),
    "weep_spacing":         (4.00, "확인", "동 — 약 4 m 간격, 부벽 사이 최소 1개"),
    "weep_area":            (3.00, "확인", "건축법 시행규칙 §25 — 3 ㎡마다 1개 이상"),
    "weep_z":               (0.35, "추정", "설치 높이. 지표+300~500 mm [추정] (원문 없음)"),
    "wall_contraction":     (9.00, "확인", "도로설계요령 8-7편 6(다) — 홈 6~8 × 깊이 12~16 mm, 9 m 이하"),
    "wall_groove_w":        (0.007, "확인", "동 (6~8 mm 의 중앙)"),
    "wall_groove_d":        (0.014, "확인", "동 (12~16 mm 의 중앙)"),
    "wall_exp_gravity":     (10.0, "확인", "동 (라) — 중력식 10 m 이하"),
    "wall_exp_cantilever":  (17.5, "확인", "동 (라) — 캔틸레버·부벽식 15~20 m 의 중앙"),
    "wall_cope_over":       (0.04, "추정", "갓돌 좌우 내밀기 30~50 mm [추정] (국내 규정 부재 확인)"),
    # ── 점자블록 ────────────────────────────────────────────────────────
    "tactile_tile":         (0.300, "확인", "교통약자법 시행규칙 별표1 — 300×300"),
    "tactile_dot_n":        (36, "확인", "동 — 점형 36점"),
    "tactile_dot_h":        (0.006, "확인", "동 — h 6±1 mm"),
    "tactile_bar_n":        (4, "확인", "동 — 선형 4선"),
    "tactile_bar_h":        (0.005, "확인", "동 — h 5±1 mm"),
}

# 점자블록 색은 법령이 "노란색"만 규정하고 색좌표를 주지 않는다 `[근거 없음]`.
# 아래 RGB 는 현장 관행 황색의 근사값 `[추정]`. v5.1 §4(순백 금지)와 무관.
TACTILE_YELLOW = (0.86, 0.66, 0.10)


# ===========================================================================
# [1] 결정적 RNG — hash() 금지. zlib.crc32 만 쓴다.
#     (scene_common._ground_skin 이 같은 이유로 crc32 로 교체된 전례가 있다)
# ===========================================================================
def det_seed(*keys):
    """좌표/문자열 키에서 **프로세스 독립**인 32bit 시드.

    float 은 0.1 mm 단위로 양자화해 문자열화한다 — repr 흔들림으로 시드가
    바뀌는 것을 막는다. Python 내장 `hash()` 는 PYTHONHASHSEED 로 매 실행
    무작위화되므로 **절대 쓰지 않는다**.
    """
    parts = []
    for k in keys:
        if isinstance(k, str):
            parts.append(k)
        elif isinstance(k, (int,)) and not isinstance(k, bool):
            parts.append("i%d" % k)
        else:
            parts.append("f%.4f" % float(k))
    return zlib.crc32("|".join(parts).encode("utf-8")) & 0xFFFFFFFF


def det_rng(*keys):
    """결정적 `random.Random`. 같은 키 → 항상 같은 수열."""
    return random.Random(det_seed(*keys))


# ===========================================================================
# [2] Kit — 프리미티브 헬퍼 주입 컨테이너
#
#     scene_common 을 import 하면 씬 ↔ 키트 순환 참조가 생긴다(씬은 이미
#     scene_common 을 import 한다). 그래서 **호출자가 헬퍼를 넘긴다.**
#     기대 시그니처는 각 씬 파일에 이미 존재하는 로컬 클로저와 동일하다:
#
#       box  (path, center, size, mtl=None, col=False)
#       cyl  (path, center, r, h, mtl=None, rotY=0.0, rotX=0.0, col=False)
#       obox (path, center, size, mtl=None, rotz=0.0, rotx=0.0, col=False)
#       slope(path, x0, z0, run, drop, y0, y1, thick, mtl, margin=0.3, col=True)
#
#     obox/slope 는 선택이다. 없는데 회전/경사가 필요하면 명확한 예외를 던진다
#     (조용한 오배치보다 낫다).
# ===========================================================================
class Kit:
    """프리미티브 헬퍼 묶음. 모든 build_* 함수의 첫 인자."""

    def __init__(self, box, cyl=None, obox=None, slope=None, stage=None):
        self.box = box
        self.cyl = cyl
        self.obox = obox
        self.slope = slope
        self.stage = stage
        self.prims = []                       # 생성 경로 로그(검산·프림 수 집계)

    # -- 내부 공통 진입점 ------------------------------------------------
    def B(self, path, center, size, mtl=None, rotz=0.0, rotx=0.0, col=False):
        """회전 유무를 알아서 가르는 박스. rot 이 0 이면 축평행 box 를 쓴다."""
        self.prims.append(path)
        if abs(rotz) < 1e-9 and abs(rotx) < 1e-9:
            return self.box(path, center, size, mtl, col)
        if self.obox is None:
            raise ValueError(
                "infra_kit: 회전 박스가 필요한데 Kit(obox=...) 가 없다. "
                "scene_common._oriented_box 를 주입하거나 회전을 0 으로 두라. "
                f"(path={path}, rotz={rotz}, rotx={rotx})")
        return self.obox(path, center, size, mtl, rotz, rotx, col)

    def C(self, path, center, r, h, mtl=None, rotY=0.0, rotX=0.0, col=False):
        self.prims.append(path)
        if self.cyl is None:
            raise ValueError(
                f"infra_kit: 실린더 헬퍼가 없다. Kit(cyl=...) 주입 필요. ({path})")
        return self.cyl(path, center, r, h, mtl, rotY, rotX, col)

    def S(self, path, x0, z0, run, drop, y0, y1, thick, mtl,
          margin=0.0, col=True):
        self.prims.append(path)
        if self.slope is None:
            raise ValueError(
                f"infra_kit: 경사 슬래브 헬퍼가 없다. Kit(slope=...) 주입 필요. ({path})")
        return self.slope(path, x0, z0, run, drop, y0, y1, thick, mtl,
                          margin, col)

    def count_since(self, mark):
        return len(self.prims) - mark

    def mark(self):
        return len(self.prims)


def kit_from_scene_common(sc, stage):
    """이미 import 된 `scene_common` 모듈 객체(`sc`)에서 Kit 을 만든다.

    **이 함수는 import 를 하지 않는다** — 호출자가 넘긴 모듈 객체를 쓸 뿐이다.
    씬에서:  `kit = infra_kit.kit_from_scene_common(sc, stage)`
    """
    def _box(path, center, size, mtl=None, col=False):
        return sc.add_box(stage, path, center, size, mtl, collider=col)

    def _cyl(path, center, r, h, mtl=None, rotY=0.0, rotX=0.0, col=False):
        return sc.add_cylinder(stage, path, center, r, h, mtl,
                               rotY=rotY, rotX=rotX, collider=col)

    def _obox(path, center, size, mtl=None, rotz=0.0, rotx=0.0, col=False):
        return sc._oriented_box(stage, path, center, size, mtl,
                                collider=col, rotz=rotz, rotx=rotx)

    def _slope(path, x0, z0, run, drop, y0, y1, thick, mtl,
               margin=0.0, col=True):
        return sc.build_slope(stage, path, x0, z0, run, drop, y0, y1,
                              thick, mtl, margin=margin, collider=col)

    return Kit(_box, _cyl, _obox, _slope, stage=stage)


def dry_kit():
    """Isaac 없이 프림 수·좌표만 기록하는 더미 Kit (검산·유닛테스트용)."""
    def _rec(kind):
        def f(path, *a, **kw):
            return ("dry", kind, path, a, kw)
        return f
    return Kit(_rec("box"), _rec("cyl"), _rec("obox"), _rec("slope"))


# ===========================================================================
# [3] 선 기하 공용 (측구·표시·옹벽이 공유)
# ===========================================================================
def _line_frame(x0, y0, x1, y1):
    """선분 → (길이, 방위각[deg], 진행단위벡터, 좌법선). 길이 0 이면 예외."""
    dx, dy = float(x1) - float(x0), float(y1) - float(y0)
    L = math.hypot(dx, dy)
    if L < 1e-9:
        raise ValueError("infra_kit: 길이 0 인 선분은 만들 수 없다.")
    a = math.atan2(dy, dx)
    return L, math.degrees(a), (math.cos(a), math.sin(a)), (-math.sin(a),
                                                            math.cos(a))


def _bay_joints(length, expansion, contraction):
    """줄눈 위치 계산의 **단일 진실원** (측구·옹벽 공용). 반환 `[(s, kind), ...]`.

    ### 왜 "간격 6 m / 20 m 를 그냥 나열"하면 안 되는가
    6 과 20 은 공약수가 없다. 단순 나열하면 18 m 와 20 m 처럼 **2 m 짜리 자투리
    패널**이 생긴다. 실제 시공에서 그런 조각은 나오지 않는다 — 시공자는
    **신축이음으로 먼저 베이를 나누고, 각 베이를 규정 간격 이하로 등분**한다.

    그래서 이 함수는 2단계로 푼다.
      ① 신축이음: `n_bay = ceil(L / expansion)` → 베이 길이 `L/n_bay`
         (규정은 "이하"이므로 등분 결과는 항상 규정을 만족한다)
      ② 수축줄눈: 각 베이를 `ceil(bay / contraction)` 등분

    L=60·신축 20·수축 6 → 베이 20 m 3개, 각 베이 4등분 = **패널 5.0 m 균일**
    (5.0 ≤ 6 규정 만족, 자투리 0). 이 균일 리듬이 곧 실루엣 단서다.

    `expansion` 또는 `contraction` 에 0/None 을 주면 그 종류를 생략한다.
    """
    L = float(length)
    out = []
    n_bay = (max(1, int(math.ceil(L / float(expansion) - 1e-9)))
             if expansion and expansion > 0 else 1)
    bay = L / n_bay
    for i in range(n_bay):
        a = bay * i
        if i > 0:
            out.append((a, "expansion"))
        if contraction and contraction > 0:
            n_p = max(1, int(math.ceil(bay / float(contraction) - 1e-9)))
            for j in range(1, n_p):
                out.append((a + bay * j / n_p, "contraction"))
    out.sort(key=lambda t: t[0])
    return out


# ===========================================================================
# [4] L형 측구
# ===========================================================================
def build_gutter_L(kit, prefix, x0, y0, x1, y1, top_z, mtl,
                   width=0.30, thick=0.20, cross_slope=0.06,
                   road_side="left", contraction=6.0, expansion=20.0,
                   groove_w=0.008, expansion_w=0.020, groove_d=0.014,
                   panel_mtl=None, collider=True, jitter=0.0,
                   seed_tag="gutter"):
    """**L형 측구** — 차도 가장자리를 따라 연속하는 콘크리트 배수 띠.

    현재 33씬 단면에서 **통째로 누락**된 요소다(`cue_arrangement_survey` §4.3①).
    실제 한국 도로 단면 순서는 `아스팔트 → L형 측구 → 연석(사다리꼴) → 보도블록`
    인데(같은 조사 §3.6), 우리 씬은 "아스팔트 → 연석 박스 → 보도"로 측구가 없다.

    ### 치수 근거
    - 폭 **300 / 500**, 두께 **200** — 국도건설공사 설계실무요령 3.배수공 2)
      형식-1 단면 도면 판독 `[확인]`
    - **수축줄눈 6 m · 신축이음 20 m** — 동 원문 ※ 항 `[확인]`
      (형식-3 만 신축 12 m). **이 줄눈 리듬이 실루엣의 반복 단서**다.
      실제 위치는 `_bay_joints()` 규약대로 **신축 베이를 먼저 나누고 그 안을
      6 m 이하로 등분**한다(60 m → 패널 5.0 m 균일). 단순 나열 시 생기는
      2 m 자투리 패널을 피하기 위함이다.
    - 바닥경사 4~10 % → 기본 6 % `[추정 — 범위 중앙]`
    - 줄눈 홈 폭·깊이는 L형 측구 원문에 없다 → 옹벽 수축이음(6~8 × 12~16 mm)
      준용 `[추정]`

    ### 인자
    - `(x0,y0)-(x1,y1)`: **연석측 가장자리 선**(측구의 높은 쪽이 아니라 낮은 쪽).
      측구 팬은 여기서 `road_side` 방향으로 `width` 만큼 뻗는다.
    - `top_z`: **차도측(바깥) 상단 모서리 z** — 아스팔트와 flush.
      연석측 모서리는 `top_z - width*sin(atan(cross_slope))` 로 낮아진다.
    - `road_side`: 진행방향 기준 `"left"`(+법선) / `"right"`(−법선).
    - `jitter`: 줄눈 위치 지터 [m]. 기본 0 (줄눈은 실제로 정확히 등간격이다 —
      §3.4 의 지터 권고는 볼라드·수목 같은 **배치물**에 대한 것이지 시공 줄눈이
      아니다). 마감 불량 재현이 필요할 때만 0.02~0.05 를 준다.

    ### 프림 수
    베이스 슬래브 **1** + 패널 `ceil(L/6)+ (L/20)` 개.
    → **≈ 0.18~0.20 프림/m** (100 m 측구 = 19~21 프림).
    줄눈은 **별도 프림이 아니라 패널 사이의 실제 틈**이다(폭 8 mm, 깊이 14 mm).
    베이스 슬래브 상면이 홈 바닥 역할을 하므로 감산(boolean) 없이 진짜 음각이 된다.

    GT: **낙차 생성 없음.** 측구 자체 단차는 `width*cross_slope` ≈ 18 mm(폭 300)
        ~ 30 mm(폭 500) 로 minor-step 임계(0.10 m) 미만이다. **단** 이 함수를
        연석 앞에 넣으면 연석 노출고가 그만큼 커진다 →
        `연석 GT 낙차 = curb_h + width*cross_slope` 로 **재계산할 것**.
        (반환값 `drop_at_curb` 를 그대로 쓰면 된다.)

    반환: dict(base, panels[], joints[(s,kind)], drop_at_curb, z_curb_edge,
               z_road_edge, prim_count)
    """
    if road_side not in ("left", "right"):
        raise ValueError("road_side 는 'left' 또는 'right'.")
    if width <= 0 or thick <= groove_d:
        raise ValueError("width>0, thick>groove_d 이어야 한다.")

    m0 = kit.mark()
    L, yaw, (ux, uy), (nx, ny) = _line_frame(x0, y0, x1, y1)
    side = 1.0 if road_side == "left" else -1.0
    off = side * width / 2.0                    # 연석선 → 팬 중심선

    t = math.atan(float(cross_slope))           # 횡단 경사각
    # 로컬 +Y 가 올라가는 방향이 rotX(+). 차도측이 높아야 하므로:
    #   road_side='left'  → 차도 = 로컬 +Y → rotx = +t
    #   road_side='right' → 차도 = 로컬 −Y → rotx = −t
    rotx = math.degrees(t) * side
    dz_half = (width / 2.0) * abs(math.sin(t))
    z_top_center = float(top_z) - dz_half       # 팬 상면 중심 z
    z_road_edge = float(top_z)
    z_curb_edge = float(top_z) - width * abs(math.sin(t))
    cos_t = math.cos(t)

    # ── 줄눈 위치 (연석선 시작점 기준 호장 s) — `_bay_joints` 규약 참조 ──
    joints = _bay_joints(L, expansion, contraction)
    if jitter and jitter > 0.0:
        jj = []
        for s, k in joints:
            r = det_rng(seed_tag, prefix, s, k)
            jj.append((min(max(s + r.uniform(-jitter, jitter), 0.05), L - 0.05), k))
        joints = sorted(jj, key=lambda q: q[0])

    def _center(s_mid):
        px = float(x0) + ux * s_mid + nx * off
        py = float(y0) + uy * s_mid + ny * off
        return px, py

    # ── 베이스 슬래브 1장 (상면 = 줄눈 홈 바닥) ─────────────────────────
    base_t = float(thick) - float(groove_d)
    bx, by = _center(L / 2.0)
    base_top = z_top_center - groove_d
    kit.B(f"{prefix}/Base", (bx, by, base_top - base_t / 2.0 * cos_t),
          (L, width, base_t), mtl, rotz=yaw, rotx=rotx, col=collider)

    # ── 패널 (줄눈 사이) — 패널 간 틈이 곧 줄눈 홈 ────────────────────────
    panel_mtl = mtl if panel_mtl is None else panel_mtl
    bounds = [0.0] + [s for s, _ in joints] + [L]
    kinds = ["end"] + [k for _, k in joints] + ["end"]
    panels = []
    for i in range(len(bounds) - 1):
        a, b = bounds[i], bounds[i + 1]
        wa = 0.0 if kinds[i] == "end" else (
            expansion_w if kinds[i] == "expansion" else groove_w)
        wb = 0.0 if kinds[i + 1] == "end" else (
            expansion_w if kinds[i + 1] == "expansion" else groove_w)
        pa, pb = a + wa / 2.0, b - wb / 2.0
        plen = pb - pa
        if plen <= 0.02:                       # 지나치게 짧은 조각은 생략
            continue
        px, py = _center((pa + pb) / 2.0)
        path = f"{prefix}/Panel_{i:02d}"
        kit.B(path, (px, py, z_top_center - groove_d / 2.0 * cos_t),
              (plen, width, groove_d), panel_mtl, rotz=yaw, rotx=rotx,
              col=False)                        # 얇은 패널엔 콜라이더 불필요
        panels.append(path)

    return dict(base=f"{prefix}/Base", panels=panels, joints=joints,
                length=L, yaw_deg=yaw,
                drop_at_curb=width * abs(math.sin(t)),
                z_curb_edge=z_curb_edge, z_road_edge=z_road_edge,
                prim_count=kit.count_since(m0))


# ===========================================================================
# [5] 빗물받이 — 배치 규칙 + 본체
# ===========================================================================
def gully_positions(x0, x1, spacing=22.0, sag_points=(), curve_points=(),
                    max_spacing=25.0, jitter=0.0, seed_tag="gully",
                    with_kind=False):
    """**빗물받이 배치 규칙**을 구현한다. 좌표 리스트를 돌려준다.

    국도건설공사 설계실무요령 3.배수공(수량산출 요령) 파 원문 `[확인]`:

    > 우수받이는 표면수가 원활히 집수될 수 있도록 **하향경사 변곡점, 우수가
    > 고이는 오목한 곳, 도로모서리 커브 시·종점에는 반드시 설치**하며,
    > **직선부의 경우 20~25 m 간격**으로 설치한다.

    즉 규칙은 두 층이다.
      ① **필수 지점** — `sag_points`(오목부·하향경사 변곡점) + `curve_points`
         (커브 시·종점). 여기는 무조건 하나 놓는다.
      ② **직선부 보간** — 필수 지점 사이를 20~25 m 를 넘지 않게 채운다.

    (참고: 하수도시설기준 계열은 연석선 따라 10~30 m 를 말한다 —
     `cue_arrangement_survey` §1.2. 도로 설계요령의 20~25 m 가 더 좁은
     구간이므로 이쪽을 채택했다. 10 m 급으로 촘촘히 하고 싶으면
     `spacing=12.0, max_spacing=15.0` 을 명시적으로 넘겨라.)

    - `spacing`: 목표 간격(기본 22 = 20~25 의 중앙)
    - `max_spacing`: **절대 상한**(기본 25). 보간 결과가 이를 넘으면 개수를 늘린다.
    - `jitter`: 직선부 보간점에만 걸리는 결정적 지터 [m]. 필수 지점은 흔들지
      않는다(기능 지점이므로). 기본 0.
    - `with_kind=True`: `[(x, "sag"|"curve"|"straight"), ...]` 로 반환.

    프림 수 0 (좌표만 계산). GT: 해당 없음.
    """
    a, b = (float(x0), float(x1)) if x1 >= x0 else (float(x1), float(x0))
    span = b - a
    if span <= 1e-6:
        return []
    if spacing <= 0 or max_spacing <= 0:
        raise ValueError("spacing / max_spacing 는 양수여야 한다.")

    anchors = []
    for p in sag_points:
        if a - 1e-6 <= p <= b + 1e-6:
            anchors.append((float(p), "sag"))
    for p in curve_points:
        if a - 1e-6 <= p <= b + 1e-6:
            if all(abs(p - q) > 1e-6 for q, _ in anchors):
                anchors.append((float(p), "curve"))
    anchors.sort(key=lambda t: t[0])

    out = list(anchors)
    bounds = [a] + [p for p, _ in anchors] + [b]
    for i in range(len(bounds) - 1):
        s0, s1 = bounds[i], bounds[i + 1]
        seg = s1 - s0
        if seg <= 1e-6:
            continue
        n = max(0, int(round(seg / spacing)) - 1)
        while seg / (n + 1) > max_spacing + 1e-9:
            n += 1
        for k in range(n):
            x = s0 + seg * (k + 1) / (n + 1)
            if jitter and jitter > 0.0:
                r = det_rng(seed_tag, x, i, k)
                x = min(max(x + r.uniform(-jitter, jitter), a), b)
            out.append((x, "straight"))

    out.sort(key=lambda t: t[0])
    return out if with_kind else [p for p, _ in out]


def _ring4(kit, prefix, cx, cy, z_top, inner_x, inner_y, w, t, mtl,
           yaw_deg=0.0, col=False):
    """개구 둘레 **4변 링**(프림 4). 솔리드 판으로 덮으면 개구가 막히므로,
    무개구·슬랫 모드에서는 반드시 이 링을 쓴다. 로컬 X=`across`, Y=`along`."""
    a = math.radians(float(yaw_deg))
    ca, sa = math.cos(a), math.sin(a)
    ox, oy = (inner_x + w) / 2.0, (inner_y + w) / 2.0
    specs = (("Xn", -ox, 0.0, w, inner_y + 2 * w),
             ("Xp", +ox, 0.0, w, inner_y + 2 * w),
             ("Yn", 0.0, -oy, inner_x, w),
             ("Yp", 0.0, +oy, inner_x, w))
    out = []
    for tag, lx, ly, sx, sy in specs:
        wx = float(cx) + lx * ca - ly * sa
        wy = float(cy) + lx * sa + ly * ca
        p = f"{prefix}/Frame_{tag}"
        kit.B(p, (wx, wy, float(z_top) - float(t) / 2.0), (sx, sy, float(t)),
              mtl, rotz=float(yaw_deg), col=col)
        out.append(p)
    return out


def build_gully(kit, prefix, cx, cy, top_z, grate_mtl, pit_mtl=None,
                frame_mtl=None, along=0.50, across=0.40, grate_t=0.05,
                body_along=0.510, body_across=0.410, body_h=0.640,
                yaw_deg=0.0, lid=True, frame=True, frame_w=0.06,
                slats=0, wall_t=0.05, seat=0.002, collider=True):
    """**빗물받이(우수받이) + 그레이팅.**

    ### 치수 근거
    - **그레이팅 400 × 500 × 50** — 국도건설공사 설계실무요령 수량내역서
      "집수정용 스틸그레이팅" `[확인]`. 장변형 400×995×50 을 쓰려면
      `along=0.995`.
    - **본체 410 × 510 × H640** — 업계 통용값. **원문 미확인 `[추정]`**.
      (조사 §3.3: 빗물받이 본체 40×50/40×100/40×150 cm 는 2차 자료에만 있고
      원문 미확인 `[미검증]`. 그래서 그레이팅 400 에서 역산한 **내폭 400**
      + 벽두께를 더한 410×510 을 채택했다. 「도로 배수시설 설계 및 관리지침
      2025.02」가 1차 근거일 가능성이 높으나 취득 실패 — 조사 §9 막힌 경로.)
    - 배치는 `gully_positions()` 참조.

    ### 배치 규칙 (호출자 책임이지만 여기 적어 둔다)
    연석 **바로 안쪽(차도측)**. L형 측구를 함께 쓰면 측구 팬 안에 앉힌다.
    `along` 축이 연석선과 평행이다(`yaw_deg` 로 연석 방위에 맞춘다).

    ### 3개 모드와 프림 수
    | 모드 | 구성 | 프림 |
    |---|---|---|
    | `lid=True, slats=0` **(기본)** | 틀 솔리드 1 + 그레이팅 솔리드 1 | **2** |
    | `lid=True, slats=n` (근접뷰) | 피트 1 + 틀 링 4 + 슬랫 n | **5+n** |
    | `lid=False` (무개구) | 피트 벽 4 + 바닥 1 + 틀 링 4 | **9** |

    기본 모드에서 피트를 만들지 않는 이유: 솔리드 그레이팅이 덮으므로 **절대
    보이지 않는다**. 프림 1개도 공짜가 아니다. 격자는 재질(노멀/알베도)로 낸다.
    슬랫 모드에서는 틀을 **솔리드 판이 아니라 4변 링**으로 만든다 — 솔리드 판을
    쓰면 슬롯 아래가 막혀 격자가 검게 읽히지 않는다.
    `seat=0.002`: 틀 상면을 그레이팅보다 2 mm 낮춘다. 두 면을 같은 z 에 두면
    **동일평면 z-fighting** 이 난다(실제 제품도 뚜껑이 틀 안에 앉으므로 물리적으로도 맞다).

    GT: `lid=True` → **낙차 아님**(포장면과 flush, 편의증진법 별표1 1-라(3)
        "접근로와 동일한 높이"). `lid=False` → **낙차 = `body_h`(0.64 m)** 이며
        GT 라벨 대상이다. 무개구 모드는 벽 4장 + 바닥으로 **실제로 뚫린 상자**를
        만들므로 낙차 기하가 진짜다. 무개구 빗물받이는 실재하지만(조사 §1.3g
        "뚜껑없이 바닥이 그대로 노출되는 측구가 많이 설치") 도심 씬에서는 예외로 쓸 것.
    """
    m0 = kit.mark()
    z = float(top_z)
    pmtl = pit_mtl if pit_mtl is not None else grate_mtl
    fmtl = frame_mtl if frame_mtl is not None else grate_mtl
    prims = {}

    if lid and not slats:
        # ── 기본: 틀 솔리드(2 mm 낮음) + 그레이팅 솔리드(flush) ──────────
        if frame:
            prims["frame"] = f"{prefix}/Frame"
            kit.B(prims["frame"],
                  (float(cx), float(cy),
                   z - seat - (grate_t + 0.03) / 2.0),
                  (across + 2 * frame_w, along + 2 * frame_w, grate_t + 0.03),
                  fmtl, rotz=yaw_deg, col=collider)
        prims["grate"] = f"{prefix}/Grate"
        kit.B(prims["grate"], (float(cx), float(cy), z - grate_t / 2.0),
              (across, along, grate_t), grate_mtl, rotz=yaw_deg, col=collider)

    elif lid:
        # ── 슬랫 모드: 피트가 보여야 하므로 틀은 링 ──────────────────────
        prims["pit"] = f"{prefix}/Pit"
        kit.B(prims["pit"],
              (float(cx), float(cy), z - grate_t - body_h / 2.0),
              (body_across, body_along, body_h), pmtl, rotz=yaw_deg, col=False)
        if frame:
            prims["frame"] = _ring4(kit, prefix, cx, cy, z - seat,
                                    across, along, frame_w, grate_t + 0.03,
                                    fmtl, yaw_deg, collider)
        bar_w = across / (2.0 * int(slats) + 1.0)      # 슬랫폭 = 슬롯폭
        a = math.radians(float(yaw_deg))
        bars = []
        for i in range(int(slats)):
            u = -across / 2.0 + bar_w * (2 * i + 1.5)
            p = f"{prefix}/Slat_{i:02d}"
            kit.B(p, (cx + u * math.cos(a), cy + u * math.sin(a),
                      z - grate_t / 2.0),
                  (bar_w, along, grate_t), grate_mtl, rotz=yaw_deg, col=False)
            bars.append(p)
        prims["slats"] = bars

    else:
        # ── 무개구: 진짜 뚫린 상자 (벽 4 + 바닥 1) ──────────────────────
        a = math.radians(float(yaw_deg))
        ca, sa = math.cos(a), math.sin(a)
        ox = (body_across + wall_t) / 2.0
        oy = (body_along + wall_t) / 2.0
        walls = []
        for tag, lx, ly, sx, sy in (
                ("Xn", -ox, 0.0, wall_t, body_along + 2 * wall_t),
                ("Xp", +ox, 0.0, wall_t, body_along + 2 * wall_t),
                ("Yn", 0.0, -oy, body_across, wall_t),
                ("Yp", 0.0, +oy, body_across, wall_t)):
            p = f"{prefix}/Wall_{tag}"
            kit.B(p, (cx + lx * ca - ly * sa, cy + lx * sa + ly * ca,
                      z - body_h / 2.0), (sx, sy, body_h), pmtl,
                  rotz=yaw_deg, col=collider)
            walls.append(p)
        prims["walls"] = walls
        prims["floor"] = f"{prefix}/Floor"
        kit.B(prims["floor"], (float(cx), float(cy), z - body_h - wall_t / 2.0),
              (body_across + 2 * wall_t, body_along + 2 * wall_t, wall_t),
              pmtl, rotz=yaw_deg, col=collider)
        if frame:
            prims["frame"] = _ring4(kit, prefix, cx, cy, z, across, along,
                                    frame_w, grate_t + 0.03, fmtl, yaw_deg,
                                    collider)

    return dict(prims=prims, gt_drop=(0.0 if lid else float(body_h)),
                is_gt_hazard=(not lid), prim_count=kit.count_since(m0))


# ===========================================================================
# [6] 맨홀
# ===========================================================================
def build_manhole(kit, prefix, cx, cy, top_z, lid_mtl, frame_mtl=None,
                  d_frame=0.648, d_lid=None, frame_w=0.045, thick=0.110,
                  lid_t=0.055, flush_tol=0.010, proud=None, seat=0.002,
                  lid=True, pit_depth=1.20, pit_mtl=None, boss=False,
                  collider=True, seed_tag="manhole"):
    """**맨홀 뚜껑 + 틀.** 차도·보도 공통.

    ### 치수 근거와 **문서 간 충돌 고지**
    - `_dimension_index.md`: "맨홀뚜껑 **틀 외경 φ648**(차도·보도 공통) /
      φ766 / φ918 · 두께 110t — KS D 4040 인증제품" `[확인]`
    - `korean_pedestrian_geometry.md` §3.2: 국도 실무요령 수량내역서는
      "맨홀뚜껑 차도용 **회주철 ø648**, 보도용 칼라 ø648" 이라 적고, 같은 문서가
      "프레임 외곽 포함 약 **φ760~780** `[추정]`" 이라고 덧붙인다.
    → 즉 **648 이 뚜껑인지 틀 외경인지 두 문서가 갈린다.** 본 함수는 색인 쪽
      해석(**틀 외경 648**)을 기본값으로 삼고, 뚜껑을 `d_frame - 2*frame_w`
      (= φ558)로 잡는다. 648 을 **뚜껑**으로 읽는 해석을 쓰려면
      `build_manhole(..., d_frame=0.765, d_lid=0.648)` 로 명시 호출하라.
      `frame_w=0.045` 는 `[추정]`(틀 링 폭 원문 없음).
    - 두께 **110t** `[확인]`. `lid_t` 는 뚜껑 단독 두께 `[추정]`.
    - 옵션 지름: **φ766 / φ918** `[확인]`.

    ### flush
    "노면과 동일면 ±10 mm". `proud=None` 이면 좌표 기반 결정적 난수로
    `U(-flush_tol, +flush_tol)` 를 뽑는다 — 여러 개를 깔았을 때 전부 정확히
    같은 높이면 오히려 CG 로 읽힌다(조사 §3.1 시공 허용오차).

    `seat=0.002`: 틀 상면을 뚜껑보다 2 mm 낮춘다. 같은 z 로 두면 두 원판이
    **동일평면 z-fighting** 을 낸다(실물도 뚜껑이 틀 턱에 앉으므로 물리적으로 맞다).

    ### 프림 수
    기본 **2**(틀 1 + 뚜껑 1). `boss=True` → 3. `lid=False` → **1**.
    맨홀 하나 = 원형 디스크 1~2장. 조사 §7 P1-7 이 "비용 대비 효과 최고"라 평가.

    ### `lid=False` 는 **근사**다 — 읽고 쓸 것
    Cube/Cylinder 조합으로는 **원형 관통 구멍을 만들 수 없다**(감산 불가).
    이 모드는 상면이 `top_z` 인 **암색 원통**(심연 근사) 1개만 놓는다.
    위에서 내려다보면 열린 맨홀로 읽히지만, **스침각(h0.3 로봇 시점)에서는
    평면 원판으로 읽힌다.** 낙차 라벨이 걸린 진짜 개구가 필요하면
    ① 각형이어도 되면 `build_gully(lid=False)`(벽 4 + 바닥 = 진짜 뚫린 상자)를
    쓰거나 ② 호출자가 포장 슬래브를 개구 주위로 분할해 짓고 이 원통을
    수직 벽면으로 쓸 것. sceneD2(바닥 개구부)가 후자의 선례다.

    GT: `lid=True` → **낙차 아님**(±10 mm 는 minor-step 임계 0.10 m 미만).
        `lid=False` → **낙차 = `pit_depth`** 이며 GT 라벨 대상(산안규칙 §43
        무방호 개구부 재현). 단 위 근사 한계를 확인하고 쓸 것. 기본은 닫힘.
    """
    m0 = kit.mark()
    if proud is None:
        proud = det_rng(seed_tag, prefix, cx, cy).uniform(-flush_tol, flush_tol)
    proud = float(proud)
    if d_lid is None:
        d_lid = max(0.05, float(d_frame) - 2.0 * float(frame_w))
    z0 = float(top_z) + proud
    prims = {}

    if lid:
        # 틀(링) — 두께 110t. 상면은 뚜껑보다 `seat` 만큼 낮다(z-fighting 회피).
        prims["frame"] = f"{prefix}/Frame"
        kit.C(prims["frame"],
              (float(cx), float(cy), z0 - float(seat) - float(thick) / 2.0),
              float(d_frame) / 2.0, float(thick),
              frame_mtl if frame_mtl is not None else lid_mtl, col=collider)
        prims["lid"] = f"{prefix}/Lid"
        kit.C(prims["lid"], (float(cx), float(cy), z0 - float(lid_t) / 2.0),
              float(d_lid) / 2.0, float(lid_t), lid_mtl, col=collider)
        if boss:
            # 중앙 개폐 보스 — 근접뷰에서 뚜껑이 판때기로 안 읽히게 하는 최소 요소.
            prims["boss"] = f"{prefix}/Boss"
            kit.C(prims["boss"], (float(cx), float(cy), z0 + 0.004),
                  0.045, 0.010, lid_mtl, col=False)
    else:
        # 무개구 근사 — 상면 = 노면. 틀을 놓으면 구멍을 도로 덮으므로 놓지 않는다.
        prims["pit"] = f"{prefix}/Pit"
        kit.C(prims["pit"],
              (float(cx), float(cy), z0 - float(pit_depth) / 2.0),
              float(d_lid) / 2.0, float(pit_depth),
              pit_mtl if pit_mtl is not None else lid_mtl, col=False)

    return dict(prims=prims, proud=proud, d_lid=float(d_lid),
                gt_drop=(0.0 if lid else float(pit_depth)),
                is_gt_hazard=(not lid), prim_count=kit.count_since(m0))


# ===========================================================================
# [7] 주차장 램프 양측 연석  ★ scene13 필수
# ===========================================================================
def build_ramp_curb(kit, prefix, profile, y_neg, y_pos, mtl,
                    height=0.12, width=0.30, sides="both", embed=0.10,
                    margin=0.0, collider=True, seg_len=None,
                    z_fn=None):
    """**주차장 진입 램프 양측 연석.** scene13 의 누락 부재이자 범용 함수.

    ### 법정 근거 `[확인]`
    **주차장법 시행규칙 제6조 제1항 제5호 다목** —
    경사로에는 **양쪽 벽면으로부터 30 cm 이상 지점에 높이 10~15 cm 의 연석**을
    설치해야 하며, **연석 부분은 차로의 너비에 포함되는 것으로 본다**.
    (`cue_arrangement_survey` §1.3(c) / §4.5 우선순위 12)

    → 즉 연석은 벽에 붙여 치고, 그 **차로측 면이 벽면에서 30 cm** 인 형태가
      규정을 만족하는 표준 해석이다. 그래서 `width` 기본값을 **0.30** 으로 두고
      벽면에 접하게 놓는다. 벽에서 띄우려면 `width` 를 줄이고 `y_neg/y_pos` 를
      직접 조정하라.

    ### 왜 중요한가 (연구 직결)
    scene13 은 램프 경사(17 % / 완화 8.5 %)를 법정값과 정확히 맞췄으면서
    **이 연석만 통째로 빠졌다**. 미관이 아니라 **램프 내부에 낙차선이 하나 더
    있어야 하는데 없는 것**이다. 차로면에서 연석 상면까지 0.10~0.15 m —
    minor-step 임계 근처의, 저고도 시점에서 가장 헷갈리는 크기다.

    ### 인자
    - `profile`: `[(x0, z0, run, drop), ...]` — **scene13 `ramp_profile()` 반환
      형식 그대로**. `z0` 는 세그 시작점의 **노면 z**, `+X` 로 `drop` 만큼 하강.
    - `y_neg`, `y_pos`: 양쪽 **벽 내면** y 좌표(각각 −Y측 / +Y측).
    - `sides`: `"both" | "neg" | "pos"`.
    - `embed`: 연석을 노면 아래로 묻는 깊이(슬래브와의 이격/z-fighting 방지).
    - `seg_len`, `z_fn`: `kit.slope` 가 없을 때의 **폴백**. `z_fn(x)->z` 를 주면
      `seg_len`(기본 1.0 m) 단위 계단형 박스로 근사한다. 이 경우 프림이 크게
      늘어나므로 `kit.slope` 주입을 권장한다.

    ### 프림 수
    `kit.slope` 사용 시 **세그먼트 수 × 측면 수** = scene13 이면 3 × 2 = **6**.
    폴백 시 `(길이/seg_len) × 측면 수` (30 m 램프·1 m 분할 = 60) — 10배다.

    GT: **낙차선을 새로 만든다.** 연석 상면 → 차로 노면 = `height`(0.10~0.15 m).
        램프 전 구간을 따라가는 **연속 선형 낙차**이며, 램프 노면 자체의 경사
        낙차와는 별개 라벨이다. scene13 의 GT 갱신이 필요하다.
    """
    if sides not in ("both", "neg", "pos"):
        raise ValueError("sides 는 'both' | 'neg' | 'pos'.")
    if not (0.09 <= height <= 0.16):
        raise ValueError(
            f"ramp_curb height={height} 는 법정 10~15 cm 범위 밖이다. "
            "의도적 규정 미달이면 이 검사를 우회하지 말고 씬 주석에 명시하라.")
    m0 = kit.mark()

    lanes = []
    if sides in ("both", "neg"):
        lanes.append(("N", float(y_neg), float(y_neg) + float(width)))
    if sides in ("both", "pos"):
        lanes.append(("P", float(y_pos) - float(width), float(y_pos)))

    paths = []
    thick = float(height) + float(embed)
    use_slope = kit.slope is not None
    for tag, ya, yb in lanes:
        if use_slope:
            for i, (sx, sz, run, drop) in enumerate(profile, 1):
                p = f"{prefix}/Curb_{tag}{i}"
                # build_slope 는 '상면 평면'을 (x0,z0)→(x0+run, z0−drop) 로 잡고
                # thick 만큼 아래로 두께를 준다. 연석 상면 = 노면 + height.
                kit.S(p, float(sx), float(sz) + float(height),
                      float(run), float(drop), ya, yb, thick, mtl,
                      margin=margin, col=collider)
                paths.append(p)
        else:
            if z_fn is None:
                raise ValueError(
                    "kit.slope 도 z_fn 도 없다. scene_common.build_slope 를 "
                    "Kit(slope=...) 로 주입하거나 z_fn 을 넘겨라.")
            step = float(seg_len or 1.0)
            xa = float(profile[0][0])
            xb = float(profile[-1][0]) + float(profile[-1][2])
            n = max(1, int(math.ceil((xb - xa) / step)))
            for i in range(n):
                x_a = xa + step * i
                x_b = min(xa + step * (i + 1), xb)
                zc = 0.5 * (z_fn(x_a) + z_fn(x_b))
                p = f"{prefix}/Curb_{tag}{i:03d}"
                kit.B(p, ((x_a + x_b) / 2.0, (ya + yb) / 2.0,
                          zc + height - thick / 2.0),
                      (x_b - x_a, yb - ya, thick), mtl, col=collider)
                paths.append(p)

    return dict(prims=paths, gt_drop=float(height), is_gt_hazard=True,
                sides=[t for t, _, _ in lanes], prim_count=kit.count_since(m0))


# ===========================================================================
# [8] 노면표시 — 스케일 앵커
# ===========================================================================
def build_road_marking(kit, prefix, kind, mtl, x0, y0, z=0.0,
                       yaw_deg=0.0, proud=0.003, collider=False,
                       # kind="parking"
                       n=1, stall_w=2.50, stall_l=5.00, line_w=0.15,
                       closed=False,
                       # kind="crosswalk"
                       band_w=4.00, walk_len=8.00,
                       stripe_w=0.45, gap_w=0.45,
                       # kind="line"
                       length=3.00):
    """**노면표시** — 주차구획 / 횡단보도 / 일반 선.

    ### 왜 이것이 v5.2 §6("비움이 기본값")을 통과하는가
    `scene_composition_audit.md` §(5)(6) 의 지적 —
    README 가 맥락 단서로 **"스케일 앵커"** 를 명시했는데 **데이터셋에 앵커가
    0건**이다. 모델이 크기를 고정할 기준이 없다. 그리고 노면표시는 장식이 아니라
    **기능 필수물**이다(주차구획 없는 주차장, 횡단보도 도색 없는 횡단보도는
    존재하지 않는다). 같은 감사가 "주차구획 도색 · 횡단보도 도색 · 출입문 ·
    맨홀 4종만 넣어도 스케일 오독의 절반이 잡힌다"고 결론했다.

    ### 치수 근거
    - **주차구획 2.50 × 5.00 m** (확장형 2.60 × 5.20) — 주차장법 시행규칙 §3
      `[확인 · 법정]` (`korean_urban_backdrop` §치수표)
    - **횡단보도 폭 45 cm · 간격 45 cm** — 도로교통법 시행규칙 별표6 노면표시
      `[확인]` (`scene_composition_audit` §(6) 앵커표)
    - 실선 두께 `line_w=0.15` 는 **`[추정]`**(통상 10~15 cm, 원문 미확인).
    - 도색 두께 `proud=0.003` 은 **`[추정]`**(규정 없음). 4 mm 이하로 유지할 것 —
      그 이상이면 minor-step 논쟁이 생긴다.

    ### 기하 규약
    로컬 프레임에서 `+X` 가 "길이 방향", `+Y` 가 "폭 방향"이고, 전체를
    `(x0,y0)` 기준으로 `yaw_deg` 만큼 회전시킨다.
    - `parking`: `(x0,y0)` = 구획 열의 **첫 구획 안쪽 모서리**. 구획은 +X 로
      `n` 개 배열되고 깊이(`stall_l`)는 +Y 방향. 분할선 `n+1` + 안쪽 끝선 1
      (+ `closed=True` 면 바깥 끝선 1).
    - `crosswalk`: `(x0,y0)` = 띠의 시작 모서리. 진행방향(+X) 총폭 `band_w`,
      횡단 길이(+Y) `walk_len`. 스트라이프는 +Y 로 길게 눕는다.
    - `line`: `(x0,y0)` 에서 +X 로 `length`, 폭 `line_w` 단선.

    ### 프림 수
    - `parking`: **n + 2** (closed 면 n + 3). 5구획 = 7 프림.
    - `crosswalk`: `floor((band_w+gap)/(stripe+gap))` — 폭 4 m·45/45 = **4~5**.
    - `line`: **1**.

    GT: **낙차 아님** (도색 두께 ≤4 mm). 순수 스케일 앵커 + 선형 단서.
    """
    m0 = kit.mark()
    a = math.radians(float(yaw_deg))
    ca, sa = math.cos(a), math.sin(a)
    zc = float(z) + float(proud) / 2.0

    def put(tag, lx, ly, sx, sy):
        """로컬 중심(lx,ly)·크기(sx,sy) → 회전 배치."""
        wx = float(x0) + lx * ca - ly * sa
        wy = float(y0) + lx * sa + ly * ca
        p = f"{prefix}/{tag}"
        kit.B(p, (wx, wy, zc), (sx, sy, float(proud)), mtl,
              rotz=float(yaw_deg), col=collider)
        return p

    paths = []
    if kind == "parking":
        n = int(n)
        if n < 1:
            raise ValueError("parking: n >= 1")
        total = n * float(stall_w)
        for i in range(n + 1):                       # 분할선(구획 경계)
            paths.append(put(f"Div_{i:02d}", i * stall_w, stall_l / 2.0,
                             line_w, stall_l))
        paths.append(put("Back", total / 2.0, stall_l, total, line_w))
        if closed:
            paths.append(put("Front", total / 2.0, 0.0, total, line_w))
        info = dict(n_stall=n, stall=(float(stall_w), float(stall_l)))

    elif kind == "crosswalk":
        pitch = float(stripe_w) + float(gap_w)
        n_s = int(math.floor((float(band_w) + float(gap_w)) / pitch + 1e-9))
        if n_s < 1:
            raise ValueError("crosswalk: band_w 가 스트라이프 1개보다 좁다.")
        # 남는 여백을 양끝에 균등 배분 → 띠가 한쪽으로 쏠리지 않는다.
        used = n_s * pitch - float(gap_w)
        pad = (float(band_w) - used) / 2.0
        for i in range(n_s):
            lx = pad + stripe_w / 2.0 + i * pitch
            paths.append(put(f"Stripe_{i:02d}", lx, walk_len / 2.0,
                             stripe_w, walk_len))
        info = dict(n_stripe=n_s, pitch=pitch, walk_len=float(walk_len))

    elif kind == "line":
        paths.append(put("Line", float(length) / 2.0, 0.0,
                         float(length), float(line_w)))
        info = dict(length=float(length), width=float(line_w))

    else:
        raise ValueError("kind 는 'parking' | 'crosswalk' | 'line'.")

    return dict(prims=paths, kind=kind, gt_drop=0.0, is_gt_hazard=False,
                prim_count=kit.count_since(m0), **info)


# ===========================================================================
# [9] 옹벽 상세
# ===========================================================================
def wall_joint_positions(length, wall_type="cantilever", contraction=9.0):
    """옹벽 이음 위치 계산. 반환 `(contraction[], expansion[])` — 벽 시작 기준 m.

    도로설계요령 3권 8-7편 옹벽 6. 구조세목 `[확인]`:
      - **수축이음** 홈 폭 6~8 mm · 깊이 12~16 mm, **9 m 이하** 간격
      - **신축이음** 중력식 **≤10 m** / 캔틸레버·부벽식 **15~20 m**,
        신축이음에서는 **철근이 끊긴다** → 전단면 관통 슬릿

    `wall_type`: `"gravity"`(10 m) | `"cantilever"`(17.5 m = 15~20 중앙) |
    `"counterfort"`(캔틸레버와 동일 간격. 단 부벽식은 수평철근이 많아
    **수축이음을 생략해도 좋다**고 원문이 명시 → `contraction` 을 0 으로 넘겨라).

    위치는 `_bay_joints()` 규약(신축 베이 등분 → 베이 내 수축 등분)을 따른다.
    규정이 전부 "이하"이므로 등분 결과는 항상 규정을 만족하며, 자투리 패널이
    생기지 않는다. L20·캔틸레버 → 신축 [10.0], 수축 [5.0, 15.0].

    프림 수 0. GT: 해당 없음.
    """
    exp_pitch = {"gravity": 10.0,
                 "cantilever": 17.5,
                 "counterfort": 17.5}.get(wall_type)
    if exp_pitch is None:
        raise ValueError("wall_type 은 'gravity'|'cantilever'|'counterfort'.")
    js = _bay_joints(length, exp_pitch, contraction)
    con = [s for s, k in js if k == "contraction"]
    exp = [s for s, k in js if k == "expansion"]
    return con, exp


def build_retaining_wall_details(kit, prefix, x0, x1, face_y, z_ground, z_top,
                                 mtl_dark, mtl_cope=None,
                                 axis="x", normal_sign=1.0, wall_t=0.35,
                                 weep_d=0.100, weep_mode="linear",
                                 weep_spacing=4.0, weep_area=3.0,
                                 weep_z=0.35, weep_depth=0.12,
                                 wall_type="cantilever", contraction=9.0,
                                 groove_w=0.007, groove_d=0.014,
                                 expansion_w=0.020, joints=True,
                                 coping=True, cope_h=0.10, cope_over=0.04,
                                 cope_flush=True, stain=False,
                                 stain_h=0.60, stain_w=0.09,
                                 collider=False, seed_tag="rwall"):
    """**옹벽 상세** — 배수공 · 신축/수축이음 · 갓돌. 벽체 자체는 만들지 않는다.

    현재 33씬의 옹벽은 **민짜 벽**이다. 실제 한국 옹벽의 시각 정체성은
    ① 규칙적으로 뚫린 배수공 열 ② 이음이 만드는 **수직선 리듬** ③ 배수공
    아래로 흘러내린 백화·녹물 — 이 세 가지다(`korean_pedestrian_geometry` §4.1~4.2).

    ### 치수 근거
    - **배수공 φ100 mm, 약 4 m 간격**, 부벽 사이 최소 1개 —
      도로설계요령 3권 8-7편 옹벽 6 `[확인]`
    - 대안: **3 ㎡마다 1개 이상** — 건축법 시행규칙 §25 `[확인]`.
      `weep_mode="grid"` 가 이것이다. 정사각 격자로 풀면 피치 √3 ≈ **1.73 m**
      `[추정 — 격자 형태는 규정에 없음]`
    - 배수공 **설치 높이 지표+300~500 mm** `[추정]` (원문 없음 — 조사 §8 목록 13번)
    - **수축이음** 홈 6~8 × 깊이 12~16 mm, **≤9 m** `[확인]`
    - **신축이음** 중력식 ≤10 m / 캔틸레버 15~20 m `[확인]`
    - **갓돌 내밀기 좌우 30~50 mm** `[추정]` (국내 규정 부재를 확인함)

    ### 이음의 표현 방식 — 프림 폭증 없이
    - **수축이음(6~8 mm)**: 벽면에 **1 mm 돌출한 암색 스트립**. 감산(boolean)이
      없는 파이프라인에서 6 mm 음각을 만들려면 벽을 쪼개야 하는데, 그 비용이
      효과보다 크다. 원거리·중거리에서 이 스트립은 홈과 동일하게 **수직 암선**
      으로 읽힌다. 근접 그레이징 뷰에서는 양각으로 보일 수 있으므로,
      근접 씬이라면 `joints=False` 로 끄고 노멀맵으로 처리하라(원 조사도
      "수축이음은 노멀맵으로 충분"이라 판정).
    - **신축이음(전단면 관통)**: 원 조사가 "**지오메트리로 벽을 분절**"하라고
      명시했다. 이 함수는 벽체를 만들지 않으므로 **위치만 반환**한다
      (`wall_joint_positions()`). 호출자가 그 위치에서 벽 패널을 나눠 짓고,
      틈에 이 함수가 놓는 폭 20 mm 암색 스트립이 들어가면 완성된다.

    ### 인자
    - `axis="x"`: 벽이 X 를 따라 뻗고, 노출면 법선은 `normal_sign * (+Y)`.
      `axis="y"` 면 벽이 Y 를 따라 뻗고 법선은 `normal_sign * (+X)`.
      (축평행 벽만 지원한다 — `add_cylinder` 가 rotZ 를 받지 않아 임의 방위의
      수평 원통을 만들 수 없기 때문. 사선 옹벽은 회전 그룹 안에서 호출하라.)
    - `face_y`: 노출면의 좌표(axis="x" 면 y, axis="y" 면 x).
    - `wall_t`: 벽 두께. 갓돌 폭 계산에만 쓴다.
    - `cope_flush=True`: **갓돌 상면 = `z_top`**(벽체를 `cope_h` 만큼 낮춰 짓는
      전제). GT 낙차가 변하지 않는다 — **기본값**.
      `False` 면 `z_top` 위에 얹어 **낙차가 `cope_h` 만큼 커진다**.
    - `stain`: 배수공 아래 백화·녹물 자국(암색 세로 띠). 조사 §4.2 는 이것을
      "낙차 위치 바로 위 벽면의 강력한 RGB 맥락단서"로 지목한다. 기본 OFF
      (룩 레이어로 처리하는 편이 옳고, 켜면 프림이 배수공 수만큼 는다).

    ### 프림 수
    `weep_mode="linear"`: 배수공 `L/4` 개 (+`stain` 시 동수).
    `weep_mode="grid"`  : `(L/1.73) × (H_eff/1.73)` 개 — **급증한다.**
                          H 5 m·L 20 m 면 11×2 = 22개. 3 ㎡ 규정을 꼭 써야 할
                          때만 켤 것.
    이음 스트립: 수축 `L/9` + 신축 `L/10~17.5`.
    갓돌: **1**.
    → 20 m·H5 m 캔틸레버 옹벽 표준 호출 = 5 + 2 + 1 + 1 = **9 프림**
      (**0.45 프림/m**).

    GT: **낙차를 만들지 않는다.** 옹벽 상단 낙차 = `z_top − 전면 지표 z` 로
        이미 존재하며 이 함수는 그 벽면을 장식할 뿐이다. **단** `cope_flush=False`
        이면 상단이 `cope_h` 만큼 올라가 **GT 낙차가 증가**한다 —
        반환값 `gt_delta` 를 확인하고 씬의 GT 를 갱신하라.
        참고: 옹벽 상단에는 **추락방지 난간의 법정 의무가 없다**
        (`cue_arrangement_survey` §1.3(d)) — 난간을 자동으로 붙이지 않는 이유다.
    """
    if axis not in ("x", "y"):
        raise ValueError("axis 는 'x' 또는 'y'.")
    if z_top <= z_ground:
        raise ValueError("z_top > z_ground 이어야 한다.")
    m0 = kit.mark()
    ns = 1.0 if float(normal_sign) >= 0 else -1.0
    a, b = (float(x0), float(x1)) if x1 >= x0 else (float(x1), float(x0))
    L = b - a
    H = float(z_top) - float(z_ground)
    fy = float(face_y)

    def place(tag, s, zc, size_along, size_out, size_up, mtl,
              out_center=None, col=False):
        """벽 좌표계(s=벽을 따라, out=법선방향, up=z) → 월드 배치."""
        oc = fy + ns * (0.001 - size_out / 2.0) if out_center is None else out_center
        if axis == "x":
            c = (a + s, oc, zc)
            sz = (size_along, size_out, size_up)
        else:
            c = (oc, a + s, zc)
            sz = (size_out, size_along, size_up)
        p = f"{prefix}/{tag}"
        kit.B(p, c, sz, mtl, col=col)
        return p

    prims = {"weep": [], "contraction": [], "expansion": [], "stain": []}

    # ── 배수공 ──────────────────────────────────────────────────────────
    r = float(weep_d) / 2.0
    hole_out = fy + ns * (0.001 - float(weep_depth) / 2.0)   # 외단 = 면 +1 mm
    rotY, rotX = (0.0, 90.0) if axis == "x" else (90.0, 0.0)
    if weep_mode == "linear":
        rows = [float(z_ground) + float(weep_z)]
        pitch = float(weep_spacing)
    elif weep_mode == "grid":
        pitch = math.sqrt(float(weep_area))                  # 3 ㎡ → 1.73 m
        nrow = max(1, int(math.floor((H - float(weep_z)) / pitch)) + 1)
        rows = [float(z_ground) + float(weep_z) + pitch * k for k in range(nrow)
                if float(z_ground) + float(weep_z) + pitch * k < float(z_top) - 0.15]
    else:
        raise ValueError("weep_mode 는 'linear' 또는 'grid'.")

    ncol = max(1, int(math.floor(L / pitch)))
    pad = (L - pitch * (ncol - 1)) / 2.0
    for ri, zc in enumerate(rows):
        for ci in range(ncol):
            s = pad + pitch * ci
            cen = (a + s, hole_out, zc) if axis == "x" else (hole_out, a + s, zc)
            p = f"{prefix}/Weep_{ri}_{ci:02d}"
            kit.C(p, cen, r, float(weep_depth), mtl_dark,
                  rotY=rotY, rotX=rotX, col=False)
            prims["weep"].append(p)
            if stain:
                # 배수공 하류 수직 얼룩 — 조사 §5 [추정] 11번(50~200 mm × 0.3~1.5 m)
                jr = det_rng(seed_tag, prefix, s, zc, "stain")
                hh = float(stain_h) * jr.uniform(0.7, 1.3)
                zz = max(float(z_ground) + hh / 2.0, zc - hh / 2.0)
                prims["stain"].append(
                    place(f"Stain_{ri}_{ci:02d}", s, zz,
                          float(stain_w), 0.012, hh, mtl_dark))

    # ── 이음 ────────────────────────────────────────────────────────────
    con, exp = wall_joint_positions(L, wall_type, contraction if joints else 0.0)
    if joints:
        for i, s in enumerate(con):
            prims["contraction"].append(
                place(f"JC_{i:02d}", s, (float(z_ground) + float(z_top)) / 2.0,
                      float(groove_w), max(0.02, float(groove_d)), H, mtl_dark))
        for i, s in enumerate(exp):
            prims["expansion"].append(
                place(f"JE_{i:02d}", s, (float(z_ground) + float(z_top)) / 2.0,
                      float(expansion_w), 0.03, H, mtl_dark))

    # ── 갓돌(코핑) ──────────────────────────────────────────────────────
    gt_delta = 0.0
    if coping:
        cw = float(wall_t) + 2.0 * float(cope_over)
        zc = (float(z_top) - float(cope_h) / 2.0 if cope_flush
              else float(z_top) + float(cope_h) / 2.0)
        oc = fy - ns * (float(wall_t) / 2.0 - float(cope_over) * 0.0)
        prims["cope"] = place("Cope", L / 2.0, zc, L, cw, float(cope_h),
                              mtl_cope if mtl_cope is not None else mtl_dark,
                              out_center=oc, col=collider)
        if not cope_flush:
            gt_delta = float(cope_h)

    return dict(prims=prims, contraction=con, expansion=exp,
                weep_pitch=pitch, n_weep=len(prims["weep"]),
                gt_drop=H + gt_delta, gt_delta=gt_delta, is_gt_hazard=False,
                prim_count=kit.count_since(m0))


# ===========================================================================
# [10] 점자블록 (점형 / 선형)  — ※ 이 프로젝트는 기본 OFF
# ===========================================================================
def build_tactile_pair(kit, prefix, kind, x0, y0, x1, y1, mtl, z=0.0,
                       relief="normal", walk_axis="x", tile=0.300,
                       dot_h=0.006, bar_h=0.005, n_dot=36, n_bar=4,
                       base_t=0.060, collider=False, seed_tag="tactile"):
    """**점형/선형 점자블록.**

    ### ⚠ 기본 호출 금지 — v5.2 규약
    이 프로젝트는 **점자블록이 기본 OFF** 다(v5.2 §7). 이유는 미관이 아니라
    **현실 빈도**다 — `cue_arrangement_survey` §2.3 실측: 낙차가 있는데
    점자블록이 없는 경우가 흔하고, 반대로 **낙차가 없는데 점자블록이 있는 경우가
    설치 사유의 대다수**다(P(낙차 없음 | 점형블록) = 0.65~0.80 `[추정]`).
    본편 21씬은 `cue_tactile` 토글로 전부 꺼져 있고, 그 결과 우연히
    P(낙차|점형블록)=0.375 가 목표 구간(0.20~0.35)에 근접해 있다.
    **이 함수는 제공만 한다. 기본 씬 빌드에서 호출하지 말 것.**
    `cue_tactile=True` 변주(단서 소거 실험)에서만 켠다.

    ### 치수 근거 `[확인 — 교통약자법 시행규칙 별표1]`
    - 블록 **300 × 300**
    - **점형 36점, 돌기 높이 6±1 mm**
    - **선형 4선, 돌기 높이 5±1 mm**
    - **노란색**(색좌표는 규정 없음 `[근거 없음]` → `TACTILE_YELLOW` 는 `[추정]`)
    - 배치(국도 실무요령 7.5 `[확인]`): 점형 세로폭 **30~90 cm, 60 cm 표준**
      = 2줄. 선형은 60 cm(2줄), 연속 직선 유도만 30 cm(1줄).
      선형 돌기 방향은 **보행 진행 방향과 평행**.

    ### relief
    - `"normal"` (**기본**): 돌기를 만들지 않고 판만 깐다(돌기는 노멀/알베도).
      기존 `scene_common.build_tactile` 과 동일 전략. 프림 **1**.
    - `"geom"`: 실제 돌기.
      · `kind="bar"` → 돌기가 **진행방향으로 연속하는 선**이라 매우 싸다.
        프림 = `1 + round(폭/0.3)*4`. 0.6 m 띠 = **9 프림**.
      · `kind="dot"` → 300 mm 타일당 36점. 0.6×3.0 m 띠 = 2×10 타일 × 36 =
        **721 프림**. 근접 1개소 이상에는 쓰지 말 것(함수가 경고를 반환한다).

    ### 인자
    - `kind`: `"dot"`(점형) | `"bar"`(선형)
    - `walk_axis`: 보행 진행 방향(`"x"`/`"y"`). 선형 돌기가 이 축과 평행해진다.

    GT: **낙차 아님** (돌기 5~6 mm). 낙차와의 상관을 만드는 **단서**일 뿐이며,
        켤 경우 §2.5 의 4분면 비율이 흔들린다 — 켜기 전에 조건부 확률을 다시 세라.
    """
    if kind not in ("dot", "bar"):
        raise ValueError("kind 는 'dot' 또는 'bar'.")
    if relief not in ("normal", "geom"):
        raise ValueError("relief 는 'normal' 또는 'geom'.")
    if walk_axis not in ("x", "y"):
        raise ValueError("walk_axis 는 'x' 또는 'y'.")
    m0 = kit.mark()

    xa, xb = (float(x0), float(x1)) if x1 >= x0 else (float(x1), float(x0))
    ya, yb = (float(y0), float(y1)) if y1 >= y0 else (float(y1), float(y0))
    sx, sy = xb - xa, yb - ya
    if sx <= 0 or sy <= 0:
        raise ValueError("점자블록 밴드의 폭·길이가 0 이다.")
    h = float(dot_h if kind == "dot" else bar_h)
    z_top = float(z) + h
    z_bot = float(z) - float(base_t)

    base = f"{prefix}/Base"
    kit.B(base, ((xa + xb) / 2.0, (ya + yb) / 2.0, (z_top + z_bot) / 2.0),
          (sx, sy, z_top - z_bot), mtl, col=collider)

    warn = None
    nubs = []
    if relief == "geom":
        if kind == "bar":
            # 선형: 돌기는 진행방향으로 연속. 300 mm 당 4선 → 피치 75 mm.
            across = sy if walk_axis == "x" else sx
            n_line = max(1, int(round(across / float(tile)))) * int(n_bar)
            pitch = across / n_line
            bw = pitch * 0.45                       # 돌기폭 ≈ 피치의 45 % [추정]
            for i in range(n_line):
                u = (pitch * (i + 0.5))
                if walk_axis == "x":
                    c = ((xa + xb) / 2.0, ya + u, z_top - h / 2.0)
                    s = (sx, bw, h)
                else:
                    c = (xa + u, (ya + yb) / 2.0, z_top - h / 2.0)
                    s = (bw, sy, h)
                p = f"{prefix}/Bar_{i:02d}"
                kit.B(p, c, s, mtl, col=False)
                nubs.append(p)
        else:
            # 점형: 타일당 36점(6×6). 프림이 폭증하므로 경고를 반환한다.
            g = int(round(math.sqrt(float(n_dot))))     # 6
            ntx = max(1, int(round(sx / float(tile))))
            nty = max(1, int(round(sy / float(tile))))
            est = ntx * nty * g * g
            if est > 400:
                warn = (f"tactile dot geom: 예상 돌기 프림 {est} 개. "
                        "근접뷰 1개소 외에는 relief='normal' 을 쓸 것.")
            tw, th = sx / ntx, sy / nty
            rad = min(tw, th) / float(g) * 0.35        # 돌기 반경 [추정]
            for ti in range(ntx):
                for tj in range(nty):
                    for i in range(g):
                        for j in range(g):
                            px = xa + tw * (ti + (i + 0.5) / g)
                            py = ya + th * (tj + (j + 0.5) / g)
                            p = f"{prefix}/Dot_{ti}_{tj}_{i}{j}"
                            kit.C(p, (px, py, z_top - h / 2.0), rad, h,
                                  mtl, col=False)
                            nubs.append(p)

    return dict(base=base, nubs=nubs, kind=kind, relief=relief,
                nub_h=h, warning=warn, gt_drop=0.0, is_gt_hazard=False,
                prim_count=kit.count_since(m0), default_enabled=False)


# ===========================================================================
# [11] 자기검산 — Isaac 불요. `python3 infra_kit.py`
# ===========================================================================
def _selfcheck():
    ok = True

    def chk(label, cond, detail=""):
        nonlocal ok
        mark = "OK " if cond else "FAIL"
        if not cond:
            ok = False
        print(f"  [{mark}] {label}{('  — ' + detail) if detail else ''}")

    print("=" * 74)
    print("infra_kit — 기하·프림수 자기검산 (Isaac 부팅 없음)")
    print("=" * 74)

    # ── 결정성 ──────────────────────────────────────────────────────────
    print("\n[0] 결정적 RNG")
    s1 = det_seed("a", 1.23456, 7)
    s2 = det_seed("a", 1.23456, 7)
    chk("det_seed 재현", s1 == s2, f"{s1}")
    chk("det_rng 재현",
        det_rng("k", 2.0).random() == det_rng("k", 2.0).random())

    # ── L형 측구 ────────────────────────────────────────────────────────
    print("\n[1] build_gutter_L — 60 m 직선")
    k = dry_kit()
    g = build_gutter_L(k, "/W/Gutter", 0.0, -4.0, 60.0, -4.0, 0.0, None)
    per_m = g["prim_count"] / g["length"]
    print(f"      프림 {g['prim_count']} / 길이 {g['length']:.1f} m "
          f"= {per_m:.3f} 프림/m")
    print(f"      줄눈 {len(g['joints'])} 개: "
          + ", ".join(f"{s:.0f}({kd[:3]})" for s, kd in g["joints"]))
    chk("줄눈 11개 (신축 2 + 수축 9)", len(g["joints"]) == 11)
    chk("20/40 은 신축이음",
        all(kd == "expansion" for s, kd in g["joints"] if abs(s % 20.0) < 1e-6))
    _pl = [g["joints"][0][0]] + [g["joints"][i + 1][0] - g["joints"][i][0]
                                 for i in range(len(g["joints"]) - 1)]
    chk("패널 전부 5.0 m 균일 (자투리 없음)",
        max(_pl) - min(_pl) < 1e-9 and abs(_pl[0] - 5.0) < 1e-9,
        f"{min(_pl):.2f}~{max(_pl):.2f} m")
    chk("수축 패널 ≤ 6 m 규정", max(_pl) <= 6.0 + 1e-9)
    chk("프림/m ≤ 0.25", per_m <= 0.25, f"{per_m:.3f}")
    chk("연석측 낙차 ≈ 18 mm", abs(g["drop_at_curb"] - 0.0180) < 0.002,
        f"{g['drop_at_curb'] * 1000:.1f} mm")
    chk("연석측 모서리가 차도측보다 낮다", g["z_curb_edge"] < g["z_road_edge"])

    # ── 빗물받이 배치 ───────────────────────────────────────────────────
    print("\n[2] gully_positions — 0~100 m, 오목부 37 m, 커브 12·64 m")
    ps = gully_positions(0.0, 100.0, sag_points=(37.0,),
                         curve_points=(12.0, 64.0), with_kind=True)
    print("      " + ", ".join(f"{p:.1f}{kd[0]}" for p, kd in ps))
    xs = [p for p, _ in ps]
    gaps = [xs[i + 1] - xs[i] for i in range(len(xs) - 1)]
    chk("필수 지점 포함", all(v in xs for v in (37.0, 12.0, 64.0)))
    chk("모든 간격 ≤ 25 m", max(gaps) <= 25.0 + 1e-9, f"max {max(gaps):.2f}")
    chk("시작~첫 받이 ≤ 25 m", xs[0] <= 25.0 + 1e-9)
    chk("끝~마지막 ≤ 25 m", 100.0 - xs[-1] <= 25.0 + 1e-9)
    ps2 = gully_positions(0.0, 100.0, sag_points=(37.0,),
                          curve_points=(12.0, 64.0), jitter=0.4)
    ps3 = gully_positions(0.0, 100.0, sag_points=(37.0,),
                          curve_points=(12.0, 64.0), jitter=0.4)
    chk("지터도 결정적", ps2 == ps3)

    # ── 빗물받이 본체 ───────────────────────────────────────────────────
    print("\n[3] build_gully")
    k = dry_kit()
    r1 = build_gully(k, "/W/Gully_A", 22.0, -3.75, 0.0, None)
    chk("기본(솔리드) = 2 프림", r1["prim_count"] == 2, str(r1["prim_count"]))
    chk("기본 = GT 낙차 아님", not r1["is_gt_hazard"])
    k = dry_kit()
    r2 = build_gully(k, "/W/Gully_B", 44.0, -3.75, 0.0, None, lid=False)
    chk("무개구 = GT 0.64 m", r2["is_gt_hazard"] and abs(r2["gt_drop"] - 0.64) < 1e-9)
    chk("무개구 = 벽4+바닥1+링4 = 9 프림", r2["prim_count"] == 9,
        str(r2["prim_count"]))
    k = dry_kit()
    r3 = build_gully(k, "/W/Gully_C", 0.0, 0.0, 0.0, None, slats=10)
    chk("슬랫 10 = 피트1+링4+슬랫10 = 15 프림", r3["prim_count"] == 15,
        str(r3["prim_count"]))

    # ── 맨홀 ────────────────────────────────────────────────────────────
    print("\n[4] build_manhole")
    k = dry_kit()
    m1 = build_manhole(k, "/W/MH_A", 3.0, 1.0, 0.0, None)
    m2 = build_manhole(k, "/W/MH_B", 9.0, 1.0, 0.0, None)
    chk("2 프림", m1["prim_count"] == 2, str(m1["prim_count"]))
    chk("flush ±10 mm", abs(m1["proud"]) <= 0.010,
        f"{m1['proud'] * 1000:+.1f} mm")
    chk("개체마다 다른 오차", abs(m1["proud"] - m2["proud"]) > 1e-6,
        f"{m1['proud'] * 1000:+.1f} vs {m2['proud'] * 1000:+.1f} mm")
    k2 = dry_kit()
    m1b = build_manhole(k2, "/W/MH_A", 3.0, 1.0, 0.0, None)
    chk("재실행 동일", abs(m1["proud"] - m1b["proud"]) < 1e-12)
    chk("뚜껑 φ558 (틀 648 해석)", abs(m1["d_lid"] - 0.558) < 1e-9,
        f"{m1['d_lid'] * 1000:.0f} mm")
    k3 = dry_kit()
    m3 = build_manhole(k3, "/W/MH_C", 3.0, 1.0, 0.0, None, lid=False)
    chk("무개구 근사 = 1 프림", m3["prim_count"] == 1, str(m3["prim_count"]))
    chk("무개구 = GT 1.20 m", m3["is_gt_hazard"] and abs(m3["gt_drop"] - 1.2) < 1e-9)

    # ── 램프 연석 ───────────────────────────────────────────────────────
    print("\n[5] build_ramp_curb — scene13 램프 프로파일")
    prof = [(0.0, 0.0, 3.60, 0.306),
            (3.60, -0.306, 23.29, 3.348),
            (26.89, -3.654, 3.60, 0.306)]
    k = dry_kit()
    rc = build_ramp_curb(k, "/W/RampCurb", prof, y_neg=-3.0, y_pos=3.0,
                         mtl=None)
    chk("3 세그 × 2 측 = 6 프림", rc["prim_count"] == 6, str(rc["prim_count"]))
    chk("GT 낙차 0.12 m 신설", rc["is_gt_hazard"] and abs(rc["gt_drop"] - 0.12) < 1e-9)
    bad = False
    try:
        build_ramp_curb(dry_kit(), "/W/X", prof, -3.0, 3.0, None, height=0.25)
    except ValueError:
        bad = True
    chk("법정 범위 밖 높이 거부", bad)

    # ── 노면표시 ────────────────────────────────────────────────────────
    print("\n[6] build_road_marking")
    k = dry_kit()
    pk = build_road_marking(k, "/W/Stall", "parking", None, 0.0, 0.0, n=5)
    chk("주차 5구획 = 7 프림", pk["prim_count"] == 7, str(pk["prim_count"]))
    chk("구획 2.5×5.0", pk["stall"] == (2.5, 5.0))
    k = dry_kit()
    cw = build_road_marking(k, "/W/CW", "crosswalk", None, 0.0, 0.0,
                            band_w=4.0, walk_len=8.0)
    chk("횡단보도 폭 4 m → 스트라이프 4", cw["n_stripe"] == 4, str(cw["n_stripe"]))
    chk("피치 0.90 m", abs(cw["pitch"] - 0.90) < 1e-9)
    k = dry_kit()
    ln = build_road_marking(k, "/W/L", "line", None, 0.0, 0.0, length=6.0,
                            yaw_deg=31.0)
    chk("사선 단선 = 1 프림", ln["prim_count"] == 1)

    # ── 옹벽 ────────────────────────────────────────────────────────────
    print("\n[7] build_retaining_wall_details — L20 × H5 캔틸레버")
    con, exp = wall_joint_positions(20.0, "cantilever")
    chk("신축 1개(베이 10 m ≤ 15~20)", exp == [10.0], str(exp))
    chk("수축 2개·간격 5 m ≤ 9 m", con == [5.0, 15.0], str(con))
    con2, exp2 = wall_joint_positions(20.0, "gravity")
    chk("중력식 신축 10 m ≤ 10 m", exp2 == [10.0], str(exp2))
    chk("자투리 패널 없음", con2 == [5.0, 15.0], str(con2))
    con3, exp3 = wall_joint_positions(60.0, "counterfort", contraction=0.0)
    chk("부벽식 수축 생략 가능", con3 == [] and len(exp3) == 3, str(exp3))
    k = dry_kit()
    w = build_retaining_wall_details(k, "/W/RW", 0.0, 20.0, face_y=2.0,
                                     z_ground=0.0, z_top=5.0, mtl_dark=None)
    print(f"      프림 {w['prim_count']} (배수공 {w['n_weep']}, "
          f"수축 {len(w['contraction'])}, 신축 {len(w['expansion'])}, 갓돌 1)")
    chk("배수공 4 m 간격 5개", w["n_weep"] == 5, str(w["n_weep"]))
    chk("프림/m ≤ 0.5", w["prim_count"] / 20.0 <= 0.5,
        f"{w['prim_count'] / 20.0:.2f}")
    chk("cope_flush 기본 → GT 불변", abs(w["gt_delta"]) < 1e-12)
    k = dry_kit()
    w2 = build_retaining_wall_details(k, "/W/RW2", 0.0, 20.0, face_y=2.0,
                                      z_ground=0.0, z_top=5.0, mtl_dark=None,
                                      cope_flush=False)
    chk("cope_flush=False → GT +0.10", abs(w2["gt_delta"] - 0.10) < 1e-9)
    k = dry_kit()
    w3 = build_retaining_wall_details(k, "/W/RW3", 0.0, 20.0, face_y=2.0,
                                      z_ground=0.0, z_top=5.0, mtl_dark=None,
                                      weep_mode="grid")
    print(f"      grid 모드(3 ㎡/개): 배수공 {w3['n_weep']} 개, "
          f"피치 {w3['weep_pitch']:.2f} m")
    chk("grid 피치 √3", abs(w3["weep_pitch"] - math.sqrt(3.0)) < 1e-9)
    chk("grid 가 linear 보다 많다", w3["n_weep"] > w["n_weep"])

    # ── 점자블록 ────────────────────────────────────────────────────────
    print("\n[8] build_tactile_pair (기본 OFF 함수)")
    k = dry_kit()
    t1 = build_tactile_pair(k, "/W/TacA", "bar", 0.0, 0.0, 5.0, 0.6, None,
                            relief="geom", walk_axis="x")
    chk("선형 geom = 1 + 8 = 9 프림", t1["prim_count"] == 9, str(t1["prim_count"]))
    chk("선형 돌기 5 mm", abs(t1["nub_h"] - 0.005) < 1e-9)
    k = dry_kit()
    t2 = build_tactile_pair(k, "/W/TacB", "dot", 0.0, 0.0, 0.6, 0.6, None,
                            relief="normal")
    chk("점형 normal = 1 프림", t2["prim_count"] == 1)
    chk("점형 돌기 6 mm", abs(t2["nub_h"] - 0.006) < 1e-9)
    chk("기본 비활성 표기", t2["default_enabled"] is False)
    k = dry_kit()
    t3 = build_tactile_pair(k, "/W/TacC", "dot", 0.0, 0.0, 0.6, 3.0, None,
                            relief="geom")
    chk("점형 geom 폭증 경고", t3["warning"] is not None,
        f"{t3['prim_count']} 프림")

    # ── GT 요약 ─────────────────────────────────────────────────────────
    print("\n[9] GT 낙차 영향 요약")
    for label, val in (
            ("build_gutter_L        ", "낙차 아님 (단 연석 노출고 +18~30 mm)"),
            ("build_gully(lid=True) ", "낙차 아님"),
            ("build_gully(lid=False)", "★ GT 0.64 m"),
            ("build_manhole(lid=T)  ", "낙차 아님 (flush ±10 mm)"),
            ("build_manhole(lid=F)  ", "★ GT = pit_depth"),
            ("build_ramp_curb       ", "★ GT 0.10~0.15 m — 낙차선 신설"),
            ("build_road_marking    ", "낙차 아님 (스케일 앵커)"),
            ("build_retaining_...   ", "낙차 아님 (cope_flush=False 면 +cope_h)"),
            ("build_tactile_pair    ", "낙차 아님")):
        print(f"      {label} : {val}")

    print("\n" + "=" * 74)
    print("검산 결과: " + ("전 항목 통과" if ok else "★ 실패 항목 있음"))
    print("=" * 74)
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    sys.exit(_selfcheck())
