# -*- coding: utf-8 -*-
"""
batch1_common.py — NegObs 배치1(12씬) 전용 공통 레이어 (ctx2 현실성 교정)

목적 : 배치1 씬에서만 쓰는 현실성 헬퍼를 모아 둔다. **scene_common.py 는 절대
       수정하지 않는다**(본편 21씬 팀과 파일 소유 충돌 회피). 추후 공용화는
       감독 간 합의 후 scene_common 으로 승격한다.

수록 :
  [1] build_bollard_v51 — 교통약자의 이동편의 증진법 시행규칙 별표2 규격 볼라드
      (h0.90·φ0.12 + 상단 백색 반사띠 + 전면 0.3 m 점형블록). 간격 1.5 m 는
      호출측(씬 PARAMS)에서 보장한다.
      · 기존 sc.build_bollard 는 **대체하지 않는다**(본편 씬이 계속 사용).
  [2] bollard_v51_aabbs — 위 볼라드의 검산용 AABB 목록(그림자·매몰 검산).
  [3] det_rng / jit_yaw / jit_pos / jit_tint — 좌표 해시 결정적 지터
      (v5.1 §3 배치 비정형 · §4 재질 틴트 지터). 같은 좌표 → 항상 같은 값이라
      재실행·재렌더 간 씬이 흔들리지 않는다.

근거 : Docs/surveys/batch1_geophysics_realism_survey.md §4·§6
       Docs/audit_v4/user_feedback_v5_1.md 전역 규약 §2·§3·§4

좌표계: Z-up, m. 전 함수 Isaac 불요(순수 계산) — 단 build_* 는 pxr 필요.
"""

import math
import random as _random

import scene_common as sc


# ===========================================================================
# [0] 볼라드 v5.1 규격 상수 (시행규칙 별표2)
#     높이 0.8~1.0 m / 지름 0.1~0.2 m / 간격 1.5 m 내외 / 밝은 반사띠 /
#     전면 0.3 m 점형블록. 아래는 그 대역의 중앙값 채택.
# ===========================================================================
BOLLARD_V51 = dict(
    radius=0.06,          # φ0.12 (규격 0.10~0.20 하한 인접 — 스테인리스 관행)
    height=0.90,          # 규격 0.80~1.00 중앙
    band_z0=0.78,         # 반사띠 하단 (상단부)
    band_z1=0.86,         # 반사띠 상단
    band_proud=0.002,     # 몸통 반경 + 2 mm (띠가 살짝 돌출)
    tactile_depth=0.30,   # 전면 점형블록 소판 깊이(전면 방향) — "전면 0.3 m"
    tactile_width=0.40,   # 소판 폭(측방)
    spacing=1.5,          # 간격 1.5 m 내외 (호출측 배열이 지킬 값)
)

# 재질 기본색 (씬이 mtl 을 넘기지 않을 때만 사용)
_BODY_RGB = (0.78, 0.80, 0.83)      # 스테인리스 헤어라인
_BAND_RGB = (0.88, 0.88, 0.86)      # 밝은 백색 반사띠 — 소면적이므로 허용
_TACT_RGB = (0.80, 0.66, 0.14)      # 점형블록 황색 — 텍스처 부재 시 폴백만
# [W2 · ground_kit §12.5-3] Tactile paving was authored as a FLAT constant
# colour, so the 36 statutory dots cast no shading at all and the batch1 pads
# read as 0.003 % of frame (55 px) — "breaks the convention AND is invisible".
# The `tactile_yellow_diff/nor` pair has been registered in `scene_common.TEX`
# all along and was simply never bound. Wire it here; the role name stays
# `tactile` / the files stay `tactile_yellow_*` because ground_kit and the
# vegetation agent both address them by that name.
#   texture [measured — assets/veg_manifest_w2.json]: 1024 px, 36 dots (6x6),
#   pitch 50.0 mm, first-column centre 26.4 mm, linear albedo 0.4504
#   (under the 0.55 clamp of ground_kit §12.5-4, so no extra tint is applied).
#   [W2-C · B7 결재 2026-07-29] Dot diameter 38.1 -> **25 mm nominal**
#   (area-equivalent 25.7 measured). The spec table fixes count / pitch /
#   height only; 38.1 was 1.5~1.7x the common 22~25 mm base and pushed the
#   dot-area share to 45.9 %, working AGAINST §12.5-4's luminance-step goal.
#   Now 20.8 %. Source constant lives in the generator, not here:
#   `assets/scene01/download_scene01_assets.py::TACTILE_DOT_D_MM`.
#   Geometry (relief height 6 mm) is untouched either way.
_TACT_TILE_M = 0.30                 # one statutory pad = 0.30 x 0.30 m
_TACT_ROUGH = 0.70


def tactile_mtl(stage, path, scale_m=None):
    """Tactile-paving material for batch1 call sites.

    Thin alias over `scene_common.tactile_pbr` so there is exactly ONE place
    that decides how tactile paving is shaded. Path token stays `...Tactile`,
    which `_look_spec` maps to class `paint` (inviolable: OmniPBR, no MDL
    promotion, no detail normal, bevel 0).
    """
    return sc.tactile_pbr(stage, path,
                          _TACT_TILE_M if scale_m is None else scale_m,
                          roughness=_TACT_ROUGH)


def _norm_front(front_dir):
    """front_dir 를 축정렬 단위벡터로 정규화. (±1,0)/(0,±1) 를 기대하되
    임의 벡터도 지배 축으로 스냅한다(점형블록이 축정렬 박스라서)."""
    fx, fy = float(front_dir[0]), float(front_dir[1])
    if abs(fx) >= abs(fy):
        return (1.0 if fx >= 0.0 else -1.0), 0.0
    return 0.0, (1.0 if fy >= 0.0 else -1.0)


def build_bollard_v51(stage, prefix, cx, cy, base_z, yaw_todo_none=None,
                      mtl_body=None, mtl_band=None, mtl_tactile=None,
                      front_dir=(1.0, 0.0), radius=None, height=None,
                      tactile=True, band=True, spec=None):
    """[v5.1 규격] 기능 시설물 볼라드 1본.

      prefix       : 프림 그룹 경로 (하위에 /Body, /Band, /Tactile 생성)
      cx, cy       : 중심 평면 좌표
      base_z       : 설치면 z (몸통 밑면)
      yaw_todo_none: 예약(원통 대칭이라 무의미). 호출부 가독성용 위치 인자.
      mtl_body/band/tactile : None 이면 prefix 하위에 기본 재질 생성
      front_dir    : 점형블록을 놓을 **전면** 방향. (±1,0) or (0,±1).
                     보도-차도 접점이면 **보도측**을 향하게 준다(보행자 유도).
      radius/height: None 이면 BOLLARD_V51 규격값
      tactile/band : 개별 토글 (grazing 뷰 폐색 우려 시 씬에서 끔)
      spec         : BOLLARD_V51 덮어쓸 dict (선택)

    반환: dict(body=..., band=..., tactile=...) 프림(없으면 None).
    """
    from pxr import UsdGeom

    S = dict(BOLLARD_V51)
    if spec:
        S.update(spec)
    r = float(S["radius"] if radius is None else radius)
    h = float(S["height"] if height is None else height)
    cx, cy, base_z = float(cx), float(cy), float(base_z)

    UsdGeom.Xform.Define(stage, prefix)

    if mtl_body is None:
        mtl_body = sc.make_pbr(stage, prefix + "/MtlBody",
                               diffuse_color=_BODY_RGB,
                               metallic=0.85, roughness_const=0.34)
    if mtl_band is None and band:
        mtl_band = sc.make_pbr(stage, prefix + "/MtlBand",
                               diffuse_color=_BAND_RGB,
                               metallic=0.0, roughness_const=0.30)
    if mtl_tactile is None and tactile:
        mtl_tactile = tactile_mtl(stage, prefix + "/MtlTactile")

    out = dict(body=None, band=None, tactile=None)

    # ── 몸통: 실린더 r·h, 밑면 base_z ──
    out["body"] = sc.add_cylinder(stage, prefix + "/Body",
                                  (cx, cy, base_z + h / 2.0), r, h,
                                  mtl_body, collider=True)

    # ── 상단 반사띠: z base_z+0.78 .. +0.86 (h0.9 기준 상단부), r+2 mm ──
    if band:
        z0 = base_z + float(S["band_z0"]) * (h / 0.90)
        z1 = base_z + float(S["band_z1"]) * (h / 0.90)
        out["band"] = sc.add_cylinder(stage, prefix + "/Band",
                                      (cx, cy, (z0 + z1) / 2.0),
                                      r + float(S["band_proud"]), z1 - z0,
                                      mtl_band)

    # ── 전면 점형블록 소판 (깊이 0.3 × 폭 0.4), 몸통 전면에 flush ──
    if tactile:
        fx, fy = _norm_front(front_dir)
        d, w = float(S["tactile_depth"]), float(S["tactile_width"])
        n0 = r                     # 근단: 몸통 표면(flush)
        n1 = r + d                 # 원단
        if fx != 0.0:
            x0, x1 = cx + fx * n0, cx + fx * n1
            y0, y1 = cy - w / 2.0, cy + w / 2.0
        else:
            x0, x1 = cx - w / 2.0, cx + w / 2.0
            y0, y1 = cy + fy * n0, cy + fy * n1
        out["tactile"] = sc.build_tactile(stage, prefix + "/Tactile",
                                          min(x0, x1), max(x0, x1),
                                          min(y0, y1), max(y0, y1),
                                          mtl_tactile, z=base_z)
    return out


def bollard_v51_aabbs(name, cx, cy, base_z=0.0, front_dir=(1.0, 0.0),
                      radius=None, height=None, tactile=True, spec=None):
    """검산용 AABB 목록 → [(name, xa, xb, ya, yb, z_top), ...].
    씬의 dressing_aabbs()/dresscheck() 가 그대로 쓸 수 있는 5-튜플 규약.
    점형블록은 z_top = base_z + 0.004 (사실상 플러시)."""
    S = dict(BOLLARD_V51)
    if spec:
        S.update(spec)
    r = float(S["radius"] if radius is None else radius)
    h = float(S["height"] if height is None else height)
    rb = r + float(S["band_proud"])
    cx, cy, base_z = float(cx), float(cy), float(base_z)
    out = [(name, cx - rb, cx + rb, cy - rb, cy + rb, base_z + h)]
    if tactile:
        fx, fy = _norm_front(front_dir)
        d, w = float(S["tactile_depth"]), float(S["tactile_width"])
        if fx != 0.0:
            xs = sorted((cx + fx * r, cx + fx * (r + d)))
            ys = (cy - w / 2.0, cy + w / 2.0)
        else:
            xs = (cx - w / 2.0, cx + w / 2.0)
            ys = sorted((cy + fy * r, cy + fy * (r + d)))
        out.append((name + "_Tac", xs[0], xs[1], ys[0], ys[1],
                    base_z + 0.004))
    return out


def bollard_line(x0, y0, x1, y1, spacing=None, include_end=True):
    """(x0,y0)→(x1,y1) 선분을 간격 spacing(기본 1.5 m)에 **가장 가깝게** 균등
    분할한 볼라드 중심 좌표 리스트. 실제 간격 = 길이/(n-1) 로 1.5 m 내외.
    반환: [(x, y), ...] (n ≥ 2)."""
    sp = float(BOLLARD_V51["spacing"] if spacing is None else spacing)
    L = math.hypot(x1 - x0, y1 - y0)
    n = max(2, int(round(L / sp)) + 1)
    pts = []
    m = n if include_end else n - 1
    for i in range(m):
        t = i / float(n - 1)
        pts.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
    return pts


# ===========================================================================
# [3] 결정적 지터 (v5.1 §3 배치 비정형 · §4 틴트 지터)
#     좌표(+태그) 해시를 시드로 쓴다 → 같은 씬을 몇 번 돌려도 동일 결과.
#     build_tree(v2) 와 동일한 해시 상수를 써서 스타일 일관 유지.
# ===========================================================================
def det_rng(*keys):
    """좌표/문자열 키 목록에서 결정적 random.Random 생성."""
    seed = 0x9E3779B9
    for k in keys:
        if isinstance(k, str):
            hk = 0
            for ch in k:
                hk = (hk * 131 + ord(ch)) & 0xFFFFFFFF
        else:
            hk = int(round(float(k) * 100.0)) & 0xFFFFFFFF
        seed = (seed * 73856093) ^ (hk * 19349663)
        seed &= 0xFFFFFFFF
    return _random.Random(seed)


def jit_yaw(cx, cy, tag="", lo=3.0, hi=8.0, base=0.0):
    """축평행 배치 해소용 yaw 지터(도). |Δ| ∈ [lo, hi], 부호 랜덤."""
    r = det_rng(cx, cy, tag, "yaw")
    d = r.uniform(lo, hi) * (1.0 if r.random() < 0.5 else -1.0)
    return float(base) + d


def jit_pos(cx, cy, tag="", amp=0.20):
    """등간격 해소용 위치 지터. 반환 (dx, dy), |d| ≤ amp (등방)."""
    r = det_rng(cx, cy, tag, "pos")
    a = r.uniform(0.0, 2.0 * math.pi)
    m = amp * math.sqrt(r.uniform(0.15, 1.0))
    return m * math.cos(a), m * math.sin(a)


def jit_scalar(cx, cy, tag="", lo=-1.0, hi=1.0):
    """임의 스칼라 지터 (길이·각도 등)."""
    return det_rng(cx, cy, tag, "sc").uniform(float(lo), float(hi))


def jit_tint(rgb, cx, cy, tag="", amp=0.05, cap=None):
    """인스턴스별 ±amp(기본 5%) 틴트 지터.
    공통 밝기 배율 1±amp + 채널별 ±amp/2 → 색상이 미세하게 갈린다.
    cap: 채널 상한. **기본 None** — 이 함수는 make_pbr 의 `tint`(텍스처
      곱 배율, 보통 0.8~1.0)에도 쓰이므로 무조건 0.8 로 자르면 색이 죽는다.
      **diffuse_color(알베도)** 를 지터할 때만 cap=0.80 을 명시해
      v5.1 §4 "순백(>0.8) 대면적 신규 생성 금지"를 지킬 것."""
    r = det_rng(cx, cy, tag, "tint")
    g = 1.0 + r.uniform(-amp, amp)
    out = []
    for c in rgb:
        v = float(c) * g * (1.0 + r.uniform(-amp / 2.0, amp / 2.0))
        v = max(0.0, v)
        if cap is not None:
            v = min(float(cap), v)
        out.append(v)
    return tuple(out)
