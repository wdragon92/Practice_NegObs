# -*- coding: utf-8 -*-
"""
negobs_look_check_v1.py — NegObs 룩 체크 v1: 자연 초지 + 침식 흙 도랑 (Isaac Sim 4.5)

지시서: Docs/negobs_look_check_v1_instructions.md
목표  : 실사에 가까운 "자연 초지 + 도랑형 낙차" 씬을 GUI로 띄우고
        뷰포트 자유 비행으로 자연스러움을 눈으로 판정 (렌더 전용, 물리 없음).

실행 (GUI 룩 체크 — 기본):
    unset PYTHONPATH VIRTUAL_ENV
    conda activate env_isaaclab
    export PYTHONNOUSERSITE=1
    python negobs_look_check_v1.py

자동 캡처 모드 (headless 검증용 — 개발 파이프라인 전용):
    NEGOBS_CAPTURE=1 python negobs_look_check_v1.py
      NEGOBS_CAPTURE_DIR  : 저장 폴더 (기본 look_check/auto)
      NEGOBS_CAPTURE_MODE : rt | pt | both (기본 rt)
      NEGOBS_VIEWS        : 쉼표로 뷰 이름 필터 (기본 전부)
      NEGOBS_SKIES        : noon,dawn 필터 (기본 전부)

구조:
    [A] PARAMS / DERIVED  — 모든 치수·강도 (지시서 §8 스켈레톤)
    [B] 순수 numpy 지형 생성 (Isaac 비의존 — selftest가 이 파일을 import해 계측)
    [C] Isaac 씬 조립 + 키 조작 + 메인 루프 (__main__에서만 실행)
"""

import os
import sys
import math
import datetime

import numpy as np

try:
    from scipy.spatial import cKDTree  # 있으면 사용, 없으면 세그먼트 거리 벡터화 폴백
    _HAVE_KDTREE = True
except Exception:  # pragma: no cover
    _HAVE_KDTREE = False

# ===========================================================================
# [A] PARAMS — 지시서 §8 스켈레톤 그대로 + 렌더 확장
# ===========================================================================
PARAMS = dict(
    terrain=dict(size=30.0, cell=0.05, base_amp=0.3, base_wavelength=12.0,
                 micro_amp=0.02, micro_wavelength=0.3, seed=42),
    ditch=dict(length=14.0, depth=1.2, depth_jitter=0.2,
               top_width=2.2, bottom_width=0.7,
               # 판정 A1(r3): 중앙 4~5m 준직선 → 파장 6→5m(사양 5~8m 하한) +
               # 옥타브 gain 상향(build_terrain)으로 중앙 구간 굽이 강화
               # (실측: 4m 창 직선 잔차 0.12~0.28 → 0.33~0.48m, 제로크로싱
               #  파장 6.2m 사양 유지, 진폭은 _norm_amp로 ±1.0m 고정)
               meander_amp=1.0, meander_wavelength=5.0,
               # 판정 A5: 립 라운딩 상한(0.2m)으로 — 볼록 곡률이 초지면에서 시작
               lip_round=0.2, lip_noise_amp=0.12, lip_noise_wavelength=0.5,
               collapse_zones=2),
    material=dict(
        # 판정 B4(r3): TOP이 이끼 카펫으로 읽힘 → 타일 축소(4.5→2.6m)로
        # 근접 디테일 밀도 상향. 반복은 macro 변조·패치 혼합·desat이 파괴.
        top_tile=2.6, wall_tile=2.5, bottom_tile=2.2,
        # 판정 B3(r3): 립 밖 나지 대역 축소 — 경계 노이즈 진폭 하향(§4.1
        # 0.2~0.4m 대역은 DERIVED.blend_noise_tw로 유지)
        boundary_dither=0.3, bottom_depth_ratio=0.85,
        # §4.4: 반복 무늬 완화용 투영 회전 오프셋 [deg]
        top_rotate=0.0, wall_rotate=17.0, bottom_rotate=31.0,
        # A/B 판정 B6(젖은 광택 절제): wet08 승자 — 곱 0.85→0.8. 움푹한 젖은
        # 자리만 넓고 부드러운 하이라이트로 반들거리고 마른 둔덕은 무광(4.5점).
        # 0.65는 띠 전체에 연속 은빛 유광막('유약 도자기' 방향)이라 기각(3점).
        # (§4.4 하한 0.6 금지·균일 하향 = 플라스틱 광 금지 유지)
        bottom_rough_mult=0.8,
        bottom_rough_noise=0.18,       # roughness ± 변조 진폭
        bottom_rough_noise_wl=1.3,     # 변조 파장 [m]
        bottom_specular=0.35,
        # 마른 흙벽 무광화 — rough = floor + (1-floor)*tex
        wall_rough_floor=0.18,
        # 판정 B1/B8(치명/경미): 파장 10~20m 저주파 albedo 명도·채도 변조
        macro_amp=dict(top=0.13, wall=0.12, bottom=0.08),
        macro_wavelength=dict(top=14.0, wall=5.0, bottom=5.0),
        # 판정 B8(r3): 흰-보라 잔돌 스페클 → 밝은 픽셀 채도 억제 (TOP만)
        desat_bright=dict(top=0.35, wall=0.0, bottom=0.0),
        # 판정 B1 ③: 90° 회전 오프셋 패치 혼합(암색 블롭 반복 파괴) 마스크 파장
        patch_wavelength=dict(top=4.7, wall=2.6, bottom=2.1),
        # 판정 A9/B3(치명): 경계 대역 픽셀 크로스페이드의 프랙탈화 노이즈
        blend_edge_noise=0.5, blend_edge_wl=0.09,
        bump_factor=1.0,
        # 판정 B2(r4→r5): triplanar 축 전환 대역 스트리크 파쇄 ① — 투영
        # 가중치를 월드 고주파 노이즈로 디더링 (NegObsGround.mdl). r5 판정:
        # 0.45/0.15m 패치가 입자 스케일보다 커 파쇄 불충분 → 강도 0.7,
        # 파장 0.06m(입자 스케일)로 강화.
        tri_dither=0.7, tri_dither_wavelength=0.06,
        # 판정 B2(r5) ②: 투영 가중 지수 |n|^4→^6 — 축 전환 크로스페이드
        # 대역 자체를 협소화 (스미어가 생기는 폭을 줄임)
        tri_exp=6.0,
        # 판정 B2(r4) ③: 역할별 노멀맵 강도 — 벽·바닥의 고주파 입자성 복원
        # (전이 대역에서 소실되던 입자 대비를 노멀 셰이딩으로 되살린다)
        bump_role=dict(top=1.0, wall=1.35, bottom=1.15)),
    light=dict(hdri_main="qwantani_noon_puresky", hdri_alt="qwantani_dawn_puresky",
               dome_rotation_step=15.0, dome_intensity=1000.0,
               # 판정 C-공통1(r4): noon HDRI 수평선 밝기가 방위 의존(태양쪽
               # tex az 216°에서 0.544, 반대쪽 87°에서 0.206 — EXR 실측).
               # overview 배경 방위가 어두운 섹터에 걸려 '하늘>양지' 위계가
               # 붕괴 → noon 돔만 Z회전해 밝은 섹터를 배경으로. RT 스윕
               # (0,±90,±113,135,180,-80~-160) 실측: -105~-113에서 수평선 대역
               # 118→166으로 최대, 진짜 하늘(지평 0° 직상)은 ~226으로 양지
               # 지형(171)을 상회 → 위계 복원. 잔여 회청 띠는 지평 '아래'
               # 돔 지면 영역(30m 유한 지형 너머 원경 헤이즈)으로 확인됨.
               noon_dome_rot=-110.0,
               # 판정 C-noon1(r5): HDRI 태양 디스크는 4k에서 유효 직경 ~0.5°로
               # 실측 정상이나, RTX 돔 라이트 샘플링이 태양을 크게 블러해 캐스트
               # 섀도 반그림자가 10~20cm(과대)로 퍼짐 → 판정 처방대로 noon은
               # ① 돔 텍스처에서 태양 디스크를 서컴솔라 휘도로 캡(런타임 파생
               #    EXR _lookfix 생성) + ② HDRI 태양 방위·고도(elev 49.79°,
               #    tex az 216.2°)에 정합한 명시적 DistantLight(0.53°)로 대체.
               # 강도: 초기 추정은 제거된 태양의 수직 입사 irradiance(EXR 적분
               # 7.371)×dome_intensity(1000)=7370. RT A/B 실측(태양=0 렌더로
               # 하늘 성분 분리 후, 전 라운드 렌더의 양지 초지 휘도 151.9와
               # 일치 조건)으로 2회 반복 보정 → 2450 (실측 156.8, +3% 이내).
               # 색 = 태양 디스크 평균색.
               noon_sun_enable=True, noon_sun_elev=49.79,
               noon_sun_intensity=2450.0,
               noon_sun_color=(1.0, 0.969, 0.935),
               # 판정 C-공통1(r5): overview 회청 띠의 실체는 돔의 지평 '아래'
               # 지면 영역(원경). 프로브 실측으로 R=-110에서 태양 섹터가 이미
               # overview 배경 방위(월드 az 33.5°)에 와 있어 요 회전 여지가
               # 소진 → 판정 대안('수평선 대역이 균일하게 밝은 HDRI로 교체')을
               # 같은 HDRI에서 파생: 지평 아래 -18°~0° 대역을 인접 하늘
               # (elev 0.5~3.5°) 밝기로 리프트(원경 헤이즈) — 전 방위에서
               # '하늘>양지' 위계가 성립한다 (아래 _ensure_noon_lookfix).
               #
               # 돔 태양의 월드 방위 매핑 (기둥 그림자 프로브 실측):
               #   DistantLight 월드 태양 az = rotZ - 90
               #   돔 태양 rotZ = 돔 Z회전 R + 233.5  (noon/dawn 공통 —
               #   두 HDRI의 태양 tex az가 215~216°로 사실상 동일)
               hdri_sun_rotz_offset=233.5,
               # 판정 C-dawn1/2: dawn HDRI 태양이 너무 약해(무지향 평광) §5 허용대로
               # 저고도·난색 보조 DistantLight를 dawn 프리셋에만 켠다. 돔은 낮춰
               # 새벽 특유의 어스름 앰비언트 + 긴 그림자 대비를 만든다.
               # 판정 C-noon1(r5, dawn 블롭): dawn 돔의 광원은 직경 수십°의
               # 확산 글로(각 10° 내 에너지 4.2%)라 캡이 무의미 — 대신 보조
               # 태양 방위를 임의값(-60°)에서 글로 중심(rotZ 오프셋 233.5)으로
               # 정합해, 립 캐스트 섀도가 '초연질 블롭 + 방위 안 맞는 경질
               # 그림자' 2중이 아니라 같은 방향의 읽히는 그림자로 겹치게 한다.
               # 고도도 글로 중심 실측(8.2°)으로 정합.
               dawn_dome_intensity=400.0,
               dawn_sun_enable=True, dawn_sun_elev=8.2,
               dawn_sun_intensity=7000.0, dawn_sun_color=(1.0, 0.62, 0.35)),
    # 판정 C-noon1(r4) 보조: maxBounces 6→8 — 벽 기저부 오목 포켓 안
    # 간접(필) 라이트를 보강해 하늘광 차폐 암부의 바닥을 끌어올린다.
    render=dict(pt_total_spp=512, pt_max_bounces=8),
)

def _deep_update(dst, src):
    for k, v in src.items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            _deep_update(dst[k], v)
        else:
            dst[k] = v


# 개발 파이프라인용 파라미터 오버라이드 (A/B 렌더 비교 — 기본 실행엔 영향 없음)
#   NEGOBS_PARAMS_OVERRIDE='{"material":{"top_tile":4.5}}' python negobs_look_check_v1.py
_ov = os.environ.get("NEGOBS_PARAMS_OVERRIDE", "")
if _ov:
    import json as _json
    _deep_update(PARAMS, _json.loads(_ov))
    print(f"[PARAMS] override 적용: {_ov}")

# 사양 수치에서 파생되는 2차 상수 (§3.2 문장 수치의 코드화)
DERIVED = dict(
    # 판정 A-4(r3, dawn overview): 말단 새들 V노치 각짐 → 페이드를 넓히고
    # 양끝 C2 연속(quintic)으로 실루엣 라운딩
    end_taper_len=2.3,        # 도랑 양끝 깊이 페이드 길이 [m]
    base_gain=0.62,            # 베이스 프랙탈 옥타브 감쇠 — 판정 A8: 중간 파장(6m,3m)
    #                            진폭을 키워 지평선 실루엣에 요철 부여 (최장 파장 12m 유지)
    depth_mod_wavelength=5.0,  # 깊이 ±20% 변조 파장 [m] ("서서히")
    width_mod_wavelength=6.0,  # 폭 ±20% 변조 파장 [m]
    # 판정 A1(r3): 사행 옥타브 감쇠 — 0.35→0.5로 2옥타브(2.5m) 비중을 올려
    # 중앙 구간에 뚜렷한 굽이 추가 (value-noise 성분 중첩안은 이 seed에서
    # 제로크로싱이 2회로 줄어 파장 실측 16m로 사양 이탈 → 기각)
    meander_gain=0.5,
    bottom_u_amp=0.08,         # U형 바닥: 가장자리가 중앙보다 높은 양 [m]
    bottom_bump_amp=0.04,      # 바닥 요철 ±진폭 [m] → 피크투피크 5~10cm
    bottom_bump_wavelength=0.35,
    # 판정 A6: 붕괴 존재감 강화 — 폭을 1.5~2m 상한 쪽으로, widen을 키워 붕괴부
    # 둑 경사를 35~45°로 완만화. 두 지점 파라미터를 서로 다르게 (복붙 금지).
    collapse_widths=[1.6, 2.0],    # 붕괴 구간 폭 [m] (사양 1~2m)
    collapse_lip_drops=[0.16, 0.19],  # 립 낮아짐 [m] (실측 0.1~0.2m가 되게)
    collapse_widens=[1.2, 1.6],    # 붕괴 구간 상단반폭 증가 → 둑 경사 완만화 [m]
    # 판정 A9/B3(치명): 경계는 face 이진 분류가 아니라 정점 blend 필드
    # (0.7m 저주파 + 0.15m 고주파 노이즈로 중심선 wiggle) → MDL이 primvar를
    # 읽어 픽셀 크로스페이드. 아래는 노이즈 파장·혼합비 (lo:hf).
    dither_wavelength=0.7,     # 경계 디더 저주파(얼룩) 파장 [m]
    dither_hf_wavelength=0.15,  # 경계 디더 고주파 파장 [m] (셀 0.05m의 3배)
    dither_weights=(0.55, 0.45),
    # blend 필드 형상: 경계 중심선 wiggle 진폭 + 크로스페이드 ramp 폭
    # 판정 B3(r3): 나지 스카프 과대 → wiggle 0.27→0.24로 하향.
    # (widen의 XY 가우시안화로 medial-axis 잔차 인플레가 사라져 밴드
    #  실측이 정직해짐 — 0.24에서 실측 ~0.23m, §4.1 스펙 0.2~0.4m 유지)
    blend_noise_tw=0.24,   # TOP/WALL wiggle [m] (이진 밴드 실측 0.2~0.4 유지)
    blend_ramp_tw=0.30,    # TOP/WALL 크로스페이드 폭 [m]
    blend_noise_wb=0.13,   # WALL/BOTTOM wiggle [depth-ratio 단위]
    blend_ramp_wb=0.30,    # WALL/BOTTOM ramp [depth-ratio 단위]
    subset_eps=0.02,       # 순수/전이 서브셋 분류 여유
    ditch_mask_eps=0.02,       # 도랑 마스크 최소 카빙 깊이 [m]
    centerline_step=0.01,      # 중심선 폴리라인 샘플 간격 [m]
    # 판정 B2(r4→r5) ② 지오메트리 측: 경사 30~68° 대역(투영 축 전환 대역)에
    # 고주파 미세 요철을 가산 — 노멀이 입자 스케일로 흔들려 결맞은 섬유상
    # 스트리크가 파쇄된다 (MDL tri_dither와 상보, §3.1 미세 거칠기의 국소 강화).
    # r5: 파장 0.22→0.16m — 능선부 노멀 결맞음을 더 짧은 스케일로 파쇄.
    wall_hf_amp=0.022,             # ±진폭 [m]
    wall_hf_wavelength=0.16,       # 파장 [m]
    slope_band=(28.0, 38.0, 58.0, 68.0),   # 경사 대역 사다리꼴 마스크 [deg]
    # 판정 C-noon1(r4): 벽 기저부(depth_ratio 0.45~0.95) 중주파 요철 —
    # 저주파 오목 포켓이 하늘광 차폐로 만드는 '매끈한 달걀형 암부'의 윤곽을
    # 실제 흙벽 파임처럼 파쇄 (바닥 자체 5~10cm 요철 사양 대역과는 분리).
    wall_mid_amp=0.035,
    wall_mid_wavelength=0.65,
    wall_mid_band=(0.45, 0.60, 0.85, 0.95),  # depth_ratio 사다리꼴 마스크
)

_HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(_HERE, "assets")
LOOKCHECK_DIR = os.path.join(_HERE, "look_check")

TEXTURES = dict(
    top=dict(diff="aerial_grass_rock_diff_4k.jpg",
             nor="aerial_grass_rock_nor_dx_4k.jpg",
             rough="aerial_grass_rock_rough_4k.jpg"),
    wall=dict(diff="brown_mud_dry_diff_4k.jpg",
              nor="brown_mud_dry_nor_dx_4k.jpg",
              rough="brown_mud_dry_rough_4k.jpg"),
    bottom=dict(diff="brown_mud_03_diff_4k.jpg",
                nor="brown_mud_03_nor_dx_4k.jpg",
                rough="brown_mud_03_rough_4k.jpg"),
)
HDRI_FILES = dict(noon="qwantani_noon_puresky_4k.exr",
                  dawn="qwantani_dawn_puresky_4k.exr")
MDL_FILE = "NegObsGround.mdl"      # 경계 크로스페이드/반복 파괴용 커스텀 MDL


# ===========================================================================
# [B] 순수 numpy 지형 생성 (지시서 §3, §4.1)
#     — Isaac 비의존. terrain_dev/selftest.py 가 이 파일을 import해 검증한다.
# ===========================================================================
def _cubic(t):
    return t * t * (3.0 - 2.0 * t)


def _quintic(t):
    return t * t * t * (t * (t * 6.0 - 15.0) + 10.0)


def _value_noise_2d(X, Y, wavelength, rng):
    """격자 래티스 균등난수 + 퀸틱 보간. 반환 대략 [-1, 1]."""
    x0 = X.min() - wavelength
    y0 = Y.min() - wavelength
    gx = (X - x0) / wavelength
    gy = (Y - y0) / wavelength
    nx = int(np.floor(gx.max())) + 3
    ny = int(np.floor(gy.max())) + 3
    lat = rng.uniform(-1.0, 1.0, size=(ny, nx))
    i = gx.astype(np.int64)
    j = gy.astype(np.int64)
    fx = gx - i
    fy = gy - j
    u = _quintic(fx)
    v = _quintic(fy)
    n00 = lat[j, i]
    n10 = lat[j, i + 1]
    n01 = lat[j + 1, i]
    n11 = lat[j + 1, i + 1]
    return (n00 * (1 - u) + n10 * u) * (1 - v) + (n01 * (1 - u) + n11 * u) * v


def _value_noise_1d(x, wavelength, rng):
    x0 = x.min() - wavelength
    g = (x - x0) / wavelength
    nx = int(np.floor(g.max())) + 3
    lat = rng.uniform(-1.0, 1.0, size=nx)
    i = g.astype(np.int64)
    f = g - i
    u = _quintic(f)
    return lat[i] * (1 - u) + lat[i + 1] * u


def _fractal_2d(X, Y, wavelength, octaves, rng, gain=0.5, lacunarity=2.0):
    out = np.zeros_like(X, dtype=np.float64)
    amp, wl, tot = 1.0, wavelength, 0.0
    for _ in range(octaves):
        out += amp * _value_noise_2d(X, Y, wl, rng)
        tot += amp
        amp *= gain
        wl /= lacunarity
    return out / tot


def _fractal_1d(x, wavelength, octaves, rng, gain=0.5, lacunarity=2.0):
    out = np.zeros_like(x, dtype=np.float64)
    amp, wl, tot = 1.0, wavelength, 0.0
    for _ in range(octaves):
        out += amp * _value_noise_1d(x, wl, rng)
        tot += amp
        amp *= gain
        wl /= lacunarity
    return out / tot


def _norm_amp(a, amp):
    """최대 절대값이 amp가 되도록 스케일 (진폭 사양을 실측으로 보장)."""
    m = np.abs(a).max()
    return a * (amp / m) if m > 1e-12 else a


def _norm_amp_interior(a, amp, mask):
    """관심 구간(mask) 안 최대 절대값이 amp가 되도록 스케일 후 ±amp 클립."""
    m = np.abs(a[mask]).max()
    if m < 1e-12:
        return a
    return np.clip(a * (amp / m), -amp, amp)


def _nearest_centerline(points, cx, cy, s_arc):
    """각 점에서 조밀 폴리라인 샘플까지 최단거리 d와 호길이 s (§3.3-2).

    샘플 간격 1cm이므로 점-샘플 최근접 == 점-세그먼트 거리 (오차 << 격자 5cm).
    """
    if _HAVE_KDTREE:
        tree = cKDTree(np.column_stack([cx, cy]))
        d, idx = tree.query(points, workers=-1)
        return d, s_arc[idx]

    # --- 폴백: 폴리라인을 0.1m 세그먼트로 데시메이트 후 점-세그먼트 거리 ---
    step = 10
    ax, ay = cx[:-step:step], cy[:-step:step]
    bx, by = cx[step::step], cy[step::step]
    sa = s_arc[:-step:step]
    ex, ey = bx - ax, by - ay
    ee = ex * ex + ey * ey
    d_out = np.empty(len(points))
    s_out = np.empty(len(points))
    chunk = 20000
    for k in range(0, len(points), chunk):
        px = points[k:k + chunk, 0][:, None]
        py = points[k:k + chunk, 1][:, None]
        t = np.clip(((px - ax) * ex + (py - ay) * ey) / ee, 0.0, 1.0)
        qx = ax + t * ex
        qy = ay + t * ey
        dist2 = (px - qx) ** 2 + (py - qy) ** 2
        j = np.argmin(dist2, axis=1)
        r = np.arange(len(j))
        d_out[k:k + chunk] = np.sqrt(dist2[r, j])
        s_out[k:k + chunk] = sa[j] + t[r, j] * np.sqrt(ee[j])
    return d_out, s_out


def _profile_consts(dp):
    """둥근 어깨 사다리꼴 프로파일 상수.

    span: 프로파일 반폭 (상단반폭 + lip_round — 라운딩이 초지면까지 확장)
    kl  : 립(초지) 쪽 포물선 코너 정규화 폭, kb: 바닥 쪽 코너 폭
    m   : 중앙 선형 구간 기울기 (적분이 1이 되도록)
    """
    span = 0.5 * (dp["top_width"] - dp["bottom_width"]) + dp["lip_round"]
    kl = min(0.45, 2.0 * dp["lip_round"] / span)
    kb = min(0.30, dp["lip_round"] / span)
    m = 1.0 / (1.0 - 0.5 * kb - 0.5 * kl)
    return kb, kl, m


def profile_S(t, dp=None):
    """단면 보간 함수 S(t): t=0(바닥반폭)→0, t=1(상단반폭+lip_round)→1.

    판정 A2/A5: cubic/quintic smoothstep은 중앙 기울기(1.5~1.875)가 커서
    유효 벽각이 ~70°에 달해 정면에서 '수직 컷뱅크'로 읽혔다. 선형 중앙
    (기울기 m≈1.45 → 벽각 ≈60°, 사양 55~60°) + 양끝 포물선 코너(C1)로
    교체하고, 립 코너는 lip_round의 2배 폭으로 초지면까지 볼록하게 잇는다.
    """
    if dp is None:
        dp = PARAMS["ditch"]
    kb, kl, m = _profile_consts(dp)
    t = np.clip(np.asarray(t, dtype=np.float64), 0.0, 1.0)
    S = np.where(t <= kb, m * t * t / (2.0 * kb),
                 np.where(t < 1.0 - kl, m * (t - 0.5 * kb),
                          1.0 - m * (1.0 - t) ** 2 / (2.0 * kl)))
    return np.clip(S, 0.0, 1.0)


def _diag_mask(shape):
    """셀 (i,j)의 대각선 분할 방향 체커보드 마스크 — True면 / 분할, False면 \\ 분할.

    판정 A9/B3: 전 셀이 같은 대각선으로 갈리면 재질 경계가 '동일 방향 직각삼각형
    톱니'로 정렬·반복된다. 셀마다 분할 방향을 번갈아 톱니 방향성을 소거한다.
    """
    ii, jj = np.meshgrid(np.arange(shape[0]), np.arange(shape[1]), indexing="ij")
    return ((ii + jj) % 2).astype(bool)


def _face_mean(F):
    """정점 필드 F(n,n) → 삼각형별 정점 평균 (n-1,n-1,2).

    셀 (i,j) 정점: v00=F[i,j], v10=F[i,j+1], v01=F[i+1,j], v11=F[i+1,j+1]
    \\ 분할: tri A = (v00, v10, v11), tri B = (v00, v11, v01)
    / 분할 : tri A = (v00, v10, v01), tri B = (v10, v11, v01)  — 모두 CCW.
    ※ 메시 faceVertexIndices 생성(_build_face_indices)과 순서가 일치해야 함.
    """
    v00 = F[:-1, :-1]
    v10 = F[:-1, 1:]
    v01 = F[1:, :-1]
    v11 = F[1:, 1:]
    m = _diag_mask(v00.shape)
    out = np.empty(v00.shape + (2,), dtype=np.float64)
    out[..., 0] = (v00 + v10 + np.where(m, v01, v11)) / 3.0
    out[..., 1] = (np.where(m, v10, v00) + v11 + v01) / 3.0
    return out


def _face_minmax(F):
    """정점 필드 F(n,n) → 삼각형별 정점 최소/최대 (min, max 각 (n-1,n-1,2)).

    삼각형 코너 구성·순서는 _face_mean/_build_face_indices와 동일.
    """
    v00 = F[:-1, :-1]
    v10 = F[:-1, 1:]
    v01 = F[1:, :-1]
    v11 = F[1:, 1:]
    m = _diag_mask(v00.shape)
    a3 = np.where(m, v01, v11)
    b1 = np.where(m, v10, v00)
    fmin = np.empty(v00.shape + (2,), dtype=np.float64)
    fmax = np.empty(v00.shape + (2,), dtype=np.float64)
    fmin[..., 0] = np.minimum(np.minimum(v00, v10), a3)
    fmax[..., 0] = np.maximum(np.maximum(v00, v10), a3)
    fmin[..., 1] = np.minimum(np.minimum(b1, v11), v01)
    fmax[..., 1] = np.maximum(np.maximum(b1, v11), v01)
    return fmin, fmax


def _build_face_indices(n):
    """(n-1,n-1,2,3) 삼각형 인덱스 — _face_mean과 동일한 면 순서/와인딩(CCW).

    셀별 대각선 방향은 _diag_mask 체커보드(경계 톱니 정렬 방지)와 일치.
    """
    ii, jj = np.meshgrid(np.arange(n - 1), np.arange(n - 1), indexing="ij")
    v00 = ii * n + jj
    v10 = ii * n + jj + 1
    v01 = (ii + 1) * n + jj
    v11 = (ii + 1) * n + jj + 1
    m = _diag_mask(v00.shape)
    tri_a = np.stack([v00, v10, np.where(m, v01, v11)], axis=-1)
    tri_b = np.stack([np.where(m, v10, v00), v11, v01], axis=-1)
    return np.stack([tri_a, tri_b], axis=2)          # (n-1, n-1, 2, 3)


def smooth_vertex_normals(X, Y, Z):
    """스무스 정점 노멀: 인접 삼각형 노멀의 면적 가중 평균 (§3.1).

    삼각형 에지 외적은 크기가 2*면적이므로 그대로 누적하면 면적 가중이 된다.
    """
    n = X.shape[0]
    P = np.stack([X, Y, Z], axis=-1).reshape(-1, 3)
    ii, jj = np.meshgrid(np.arange(n - 1), np.arange(n - 1), indexing="ij")
    m = _diag_mask((n - 1, n - 1)).ravel()
    v00 = (ii * n + jj).ravel()
    v10 = (ii * n + jj + 1).ravel()
    v01 = ((ii + 1) * n + jj).ravel()
    v11 = ((ii + 1) * n + jj + 1).ravel()

    acc = np.zeros_like(P)
    # 셀별 대각선 방향(_diag_mask)과 일치하는 삼각형 구성
    for a, b, c in ((v00, v10, np.where(m, v01, v11)),
                    (np.where(m, v10, v00), v11, v01)):
        fn = np.cross(P[b] - P[a], P[c] - P[a])  # 크기 = 2*면적, 위쪽(+z) 방향
        np.add.at(acc, a, fn)
        np.add.at(acc, b, fn)
        np.add.at(acc, c, fn)
    norm = np.linalg.norm(acc, axis=1, keepdims=True)
    acc /= np.maximum(norm, 1e-12)
    return acc.reshape(n, n, 3)


def build_terrain(params=PARAMS):
    """지시서 §3 사양의 하이트필드 + §4.1 면 분류를 생성 (반환 키는 docstring 참고).

    반환 dict 주요 키:
      xs, ys, X, Y, heights, carve(=local_depth), ditch_mask, depth_ratio,
      face_class(0=TOP 1=WALL 2=BOTTOM, 디더링 적용), normals(스무스 정점 노멀),
      centerline, collapse, d_field, s_field, wt_field, taper_field, depth_s_field
    """
    tp, dp, mp = params["terrain"], params["ditch"], params["material"]
    dv = DERIVED
    rng = np.random.default_rng(tp["seed"])
    # 자식 rng를 고정 순서로 분배 → seed 재현성 보장
    (r_base, r_micro, r_meander, r_dmod, r_wmod,
     r_lip, r_bump, r_dith1, r_dith2, r_cz) = rng.spawn(10)

    # --- 격자 ---
    n = int(round(tp["size"] / tp["cell"])) + 1          # 601
    half = tp["size"] / 2.0
    xs = np.linspace(-half, half, n)
    ys = np.linspace(-half, half, n)
    X, Y = np.meshgrid(xs, ys)                            # [행=y, 열=x]

    # --- §3.1 베이스 초지: 저주파 기복 3옥타브 + 미세 거칠기 ---
    # gain을 올려 중간 파장(6m/3m) 옥타브 비중 강화 (판정 A8: 지평선 실루엣 요철)
    base_low = _norm_amp(_fractal_2d(X, Y, tp["base_wavelength"], 3, r_base,
                                     gain=dv["base_gain"]),
                         tp["base_amp"])
    micro = _norm_amp(_fractal_2d(X, Y, tp["micro_wavelength"], 2, r_micro),
                      tp["micro_amp"])
    base_h = base_low + micro

    # --- §3.3-1 사행 중심선 폴리라인 (직선 금지) ---
    # 판정 A1(r3): 파장 5m(사양 하한) + gain 0.5로 중앙 구간에도 뚜렷한
    # 굽이가 생기게. 진폭은 _norm_amp가 사양 ±1.0m로 재정규화.
    L = dp["length"]
    u = np.arange(0.0, L + 1e-9, dv["centerline_step"])
    meander = _fractal_1d(u, dp["meander_wavelength"], 2, r_meander,
                          gain=dv["meander_gain"])
    cy_line = _norm_amp(meander - meander.mean(), dp["meander_amp"])
    cx_line = u - L / 2.0
    seg = np.hypot(np.diff(cx_line), np.diff(cy_line))
    s_arc = np.concatenate([[0.0], np.cumsum(seg)])
    L_arc = float(s_arc[-1])

    # 양끝 페이드 (도랑이 지면으로 자연스럽게 소멸)
    # 판정 A-4(r3): cubic→quintic (양끝 2차미분 0) — 말단 새들이 만드는
    # V노치 실루엣의 각진 꺾임을 둥글린다.
    tl = dv["end_taper_len"]
    taper_arr = _quintic(np.clip(s_arc / tl, 0, 1)) * \
        _quintic(np.clip((L_arc - s_arc) / tl, 0, 1))
    interior_m = (s_arc > tl) & (s_arc < L_arc - tl)

    # --- station별 속성: 깊이·폭 ±20% 변조 (§3.2 균일 단면 금지) ---
    dmod = 1.0 + _norm_amp_interior(
        _fractal_1d(s_arc, dv["depth_mod_wavelength"], 2, r_dmod),
        dp["depth_jitter"], interior_m)
    wmod = 1.0 + _norm_amp_interior(
        _fractal_1d(s_arc, dv["width_mod_wavelength"], 2, r_wmod),
        dp["depth_jitter"], interior_m)
    depth_arr = dp["depth"] * dmod
    wt_arr = 0.5 * dp["top_width"] * wmod
    wb_arr = 0.5 * dp["bottom_width"] * wmod

    # --- 붕괴 지점 2곳 (§3.2) : 중앙 30~70% 구간에 배치 ---
    # 판정 A6: 두 지점의 폭·립낙차·완만화를 서로 다르게 (복붙 금지)
    ncz = int(dp["collapse_zones"])
    fracs = np.linspace(0.32, 0.68, ncz) + r_cz.uniform(-0.04, 0.04, ncz)
    cz_centers = fracs * L_arc
    cz_sides = np.where(r_cz.random(ncz) < 0.5, -1.0, 1.0)  # 붕괴가 난 둑 쪽
    cz_w = (dv["collapse_widths"] * ncz)[:ncz]            # FWHM = 붕괴 구간 폭
    cz_drop = (dv["collapse_lip_drops"] * ncz)[:ncz]
    cz_widen = (dv["collapse_widens"] * ncz)[:ncz]
    cz_sig = [w / 2.355 for w in cz_w]
    c_list = [np.exp(-0.5 * ((s_arc - c0) / sg) ** 2)
              for c0, sg in zip(cz_centers, cz_sig)]
    # 립 라인 위의 완만화 프로파일 (계측·selftest용 — 립 라인을 따라가면
    # XY 가우시안 widen과 동일한 형태가 된다)
    widen_arr = sum(c * w for c, w in zip(c_list, cz_widen))
    widen_mean = float(np.mean(cz_widen))
    # selftest 호환: collapse_c * widen(평균) == Σ c_i * widen_i 가 되게 저장
    c_arr = widen_arr / widen_mean

    # 붕괴 립 중심 XY — widen·lip drop 가우시안의 중심.
    # s 기반 widen 필드는 사행 medial axis에서 최근접 station이 점프해
    # 재질 경계 잔차(디더 밴드 계측)에 0.4m 초과 아티팩트를 만들므로
    # (판정 A1 사행 강화 후 표면화), drop과 마찬가지로 XY 공간 가우시안 사용.
    cz_xy = []
    for c0, side, wdn in zip(cz_centers, cz_sides, cz_widen):
        k = int(np.clip(np.searchsorted(s_arc, c0), 1, len(s_arc) - 2))
        tx = cx_line[k + 1] - cx_line[k - 1]
        ty = cy_line[k + 1] - cy_line[k - 1]
        tn = np.hypot(tx, ty)
        nx_, ny_ = -ty / tn, tx / tn
        wt_c = wt_arr[k] + wdn
        cz_xy.append((float(cx_line[k] + side * wt_c * nx_),
                      float(cy_line[k] + side * wt_c * ny_)))

    # --- §3.3-2 각 격자점 → 중심선 최단거리 d, 호길이 s ---
    pts = np.column_stack([X.ravel(), Y.ravel()])
    d_flat, s_flat = _nearest_centerline(pts, cx_line, cy_line, s_arc)
    d = d_flat.reshape(n, n)
    s_field = s_flat.reshape(n, n)

    # station 속성을 격자점에 보간 (1cm 샘플이므로 최근접 인덱싱으로 충분)
    idx = np.clip(np.searchsorted(s_arc, s_flat), 0, len(s_arc) - 1)
    depth_f = depth_arr[idx].reshape(n, n)
    wt_f0 = wt_arr[idx].reshape(n, n)
    wb_f = wb_arr[idx].reshape(n, n)
    taper_f = taper_arr[idx].reshape(n, n)
    # 붕괴 완만화: XY 가우시안 (붕괴가 난 둑 쪽만 물러남 — s 필드 점프 없음)
    widen_f = np.zeros_like(X)
    for (px, py), sg, wdn in zip(cz_xy, cz_sig, cz_widen):
        widen_f += wdn * np.exp(
            -0.5 * ((X - px) ** 2 + (Y - py) ** 2) / sg ** 2)

    # --- §3.3-4 립 고주파 노이즈: 위치별 2D 노이즈를 상단반폭에 가산 ---
    lip_n = _norm_amp(_fractal_2d(X, Y, dp["lip_noise_wavelength"], 2, r_lip),
                      dp["lip_noise_amp"])
    # 붕괴 구간은 상단반폭 확대 → 둑 경사 완만화 (지점별 widen)
    wt_f = wt_f0 + lip_n + widen_f
    wt_f = np.maximum(wt_f, wb_f + 0.15)

    # --- §3.3-3 사다리꼴 프로파일 + 립 라운딩 (판정 A2/A5: profile_S 참조) ---
    # 프로파일 반폭을 lip_round만큼 초지 쪽으로 확장 → 립의 볼록 곡률이
    # 초지면에서 시작 (한 줄 크리스 제거). 유효 벽각은 선형 중앙 구간 ≈60°.
    span_f = np.maximum(wt_f + dp["lip_round"] - wb_f, 0.2)
    t = np.clip((d - wb_f) / span_f, 0.0, 1.0)
    S = profile_S(t, dp)

    # --- §3.2 바닥: 중앙이 살짝 낮은 U형 + 5~10cm 요철 ---
    u_shape = dv["bottom_u_amp"] * np.clip(d / np.maximum(wb_f, 1e-6), 0, 1) ** 2
    bump = _norm_amp(_fractal_2d(X, Y, dv["bottom_bump_wavelength"], 2, r_bump),
                     dv["bottom_bump_amp"])

    carve = taper_f * ((1.0 - S) * (depth_f - u_shape) + bump * (1.0 - S))

    # 붕괴 지점: 한쪽 둑의 립 지점(cz_xy)을 중심으로 한 월드공간 2D 가우시안
    # 함몰 (립이 0.1~0.2m 낮아진 둑 슬럼프) — widen과 동일한 XY 중심 공유.
    for (px, py), sg, drop in zip(cz_xy, cz_sig, cz_drop):
        r2 = (X - px) ** 2 + (Y - py) ** 2
        carve += taper_f * drop * np.exp(-0.5 * r2 / sg ** 2)
    carve = np.maximum(carve, 0.0)

    # --- §3.3-5 최종 높이 = 베이스 − 카빙 ---
    heights = base_h - carve

    ditch_mask = carve > dv["ditch_mask_eps"]
    depth_ratio = carve / np.maximum(depth_f * taper_f, 1e-6)

    # --- 판정 B2/C-noon1(r4): 벽 요철 2대역 가산 ---
    # rng.spawn은 카운터 기반이라 기존 spawn(10) 뒤 추가 분배도 재현 결정적.
    r_wallhf, r_wallmid = rng.spawn(2)

    def _trap_mask(x, a, b, c, d):
        """사다리꼴 smooth 마스크: a→b 상승, c→d 하강 (양끝 C1)."""
        return _cubic(np.clip((x - a) / (b - a), 0.0, 1.0)) * \
            _cubic(np.clip((d - x) / (d - c), 0.0, 1.0))

    # (1) 경사 전이 대역 고주파 요철 — triplanar 축 전환 스트리크 파쇄
    gy_, gx_ = np.gradient(heights, tp["cell"])
    slope_deg = np.degrees(np.arctan(np.hypot(gx_, gy_)))
    band_hi = _trap_mask(slope_deg, *dv["slope_band"])
    hf = _norm_amp(_fractal_2d(X, Y, dv["wall_hf_wavelength"], 2, r_wallhf),
                   1.0)
    # (2) 벽 기저부 중주파 요철 — 저주파 오목 포켓의 달걀 윤곽 파쇄
    band_base = _trap_mask(depth_ratio, *dv["wall_mid_band"]) * ditch_mask
    midn = _norm_amp(
        _fractal_2d(X, Y, dv["wall_mid_wavelength"], 2, r_wallmid), 1.0)
    heights = heights + taper_f * (dv["wall_hf_amp"] * band_hi * hf +
                                   dv["wall_mid_amp"] * band_base * midn)

    # --- §4.1 면 분류 + 경계 디더링 (판정 A9/B3 치명 대응: 정점 blend 필드) ---
    # face 이진 분류만으로는 5cm 삼각형 톱니가 경계에 노출된다. 대신 정점
    # blend 필드(q_tw: 0=초지↔1=벽흙, q_wb: 0=벽흙↔1=젖은진흙)를 만들어
    # ① primvar로 메시에 실어 경계 대역 전용 블렌드 재질이 픽셀 단위
    #    크로스페이드 (NegObsGround.mdl), ② 0.5 임계 이진화로 §4.1의 3분류
    #    face_class(계측·검증용)도 종전과 동일하게 유지한다.
    # 경계 중심선은 저주파(0.7m)+고주파(0.15m) 노이즈로 wiggle → 얼룩덜룩.
    def _mix_noise(rng_):
        r_lo, r_hf = rng_.spawn(2)
        lo = _norm_amp(_fractal_2d(X, Y, dv["dither_wavelength"], 2, r_lo), 1.0)
        hf = _norm_amp(_value_noise_2d(X, Y, dv["dither_hf_wavelength"], r_hf),
                       1.0)
        w_lo, w_hf = dv["dither_weights"]
        return (w_lo * lo + w_hf * hf) / (w_lo + w_hf)

    n1 = _mix_noise(r_dith1)
    n2 = _mix_noise(r_dith2)

    # TOP/WALL: 거리 도메인 — 중심선 wiggle ±blend_noise_tw, ramp blend_ramp_tw
    q_tw = np.clip(0.5 + ((wt_f - d) - dv["blend_noise_tw"] * n1)
                   / dv["blend_ramp_tw"], 0.0, 1.0)
    # 양끝 테이퍼: 도랑이 소멸하는 구간은 초지로 페이드
    q_tw *= np.clip((taper_f - 0.10 - 0.08 * n1) / 0.08, 0.0, 1.0)
    # WALL/BOTTOM: 깊이비 도메인 — 임계 0.85에 wiggle, ramp는 ratio 단위
    q_wb = np.clip(0.5 + ((depth_ratio - mp["bottom_depth_ratio"])
                          - dv["blend_noise_wb"] * n2)
                   / dv["blend_ramp_wb"], 0.0, 1.0)

    face_d = _face_mean(d)
    face_wt = _face_mean(wt_f)
    face_wb = _face_mean(wb_f)
    face_s = _face_mean(s_field)
    face_q_tw = _face_mean(q_tw)
    face_q_wb = _face_mean(q_wb)

    in_ditch = face_q_tw > 0.5
    is_bottom = face_q_wb > 0.5
    face_class = np.zeros(face_d.shape, dtype=np.int8)    # 0 = TOP
    face_class[in_ditch] = 1                              # 1 = WALL
    face_class[in_ditch & is_bottom] = 2                  # 2 = BOTTOM

    # 렌더용 5분할: 순수 3영역 + 전이 대역 2개 (blend 재질 바인딩 대상)
    eps = dv["subset_eps"]
    tw_min, tw_max = _face_minmax(q_tw)
    wb_min, wb_max = _face_minmax(q_wb)
    wallside = tw_min >= 1.0 - eps
    face_subset = np.zeros(face_q_tw.shape, dtype=np.int8)          # 0 TOP
    face_subset[(tw_max > eps) & ~wallside] = 3                     # TRANS_TW
    face_subset[wallside] = 1                                       # WALL
    face_subset[wallside & (wb_max > eps) & (wb_min < 1.0 - eps)] = 4  # T_WB
    face_subset[wallside & (wb_min >= 1.0 - eps)] = 2               # BOTTOM

    # --- 스무스 정점 노멀 ---
    normals = smooth_vertex_normals(X, Y, heights)

    return dict(
        xs=xs, ys=ys, X=X, Y=Y,
        heights=heights, base_low=base_low, micro=micro,
        carve=carve, local_depth=carve,
        ditch_mask=ditch_mask, depth_ratio=depth_ratio,
        face_class=face_class, face_d=face_d, face_wt=face_wt,
        face_wb=face_wb, face_s=face_s,
        face_subset=face_subset,
        vertex_blend_tw=q_tw, vertex_blend_wb=q_wb,
        normals=normals,
        centerline=dict(x=cx_line, y=cy_line, s=s_arc,
                        depth_s=depth_arr, w_top_half=wt_arr,
                        w_bot_half=wb_arr, taper=taper_arr,
                        collapse_c=c_arr, arc_length=L_arc),
        collapse=dict(centers_s=cz_centers.tolist(),
                      centers_xy=cz_xy, sides=cz_sides.tolist(),
                      # selftest 호환: width(최대)·widen(평균)은 스칼라 유지,
                      # 지점별 값은 *_per_zone 리스트로 제공
                      width=float(max(cz_w)), widths_per_zone=list(cz_w),
                      lip_drop_per_zone=list(cz_drop),
                      widen=widen_mean, widen_per_zone=list(cz_widen)),
        d_field=d, s_field=s_field,
        wt_field=wt_f, taper_field=taper_f, depth_s_field=depth_f,
        params=params, derived=dv,
    )


def bilinear_sample(F, xs, ys, px, py):
    """정점 필드 F(행=y, 열=x)를 (px, py)에서 쌍선형 보간."""
    cell = xs[1] - xs[0]
    gx = np.clip((np.asarray(px) - xs[0]) / cell, 0, len(xs) - 1.001)
    gy = np.clip((np.asarray(py) - ys[0]) / cell, 0, len(ys) - 1.001)
    i0 = gx.astype(np.int64)
    j0 = gy.astype(np.int64)
    fx = gx - i0
    fy = gy - j0
    f00 = F[j0, i0]
    f10 = F[j0, i0 + 1]
    f01 = F[j0 + 1, i0]
    f11 = F[j0 + 1, i0 + 1]
    return (f00 * (1 - fx) + f10 * fx) * (1 - fy) + \
           (f01 * (1 - fx) + f11 * fx) * fy


# ===========================================================================
# [C] Isaac Sim 씬 조립 + 메인 루프 (__main__ 전용)
# ===========================================================================
BANNER = """\
[조작] 우클릭+WASD 비행 · 우클릭+스크롤 속도 · P 패스트레이싱 토글 · S 스크린샷 · L 하늘 전환 · [ ] 태양 방위
[체크리스트]
 1. 높이 2m 정면    — 도랑이 실제 사진처럼 읽히는가
 2. 높이 0.5m·8~10m — 낙차가 시야에서 자연스럽게 사라지는가 (grazing angle 은닉)
 3. 립 라인         — 직선 티 없이 물어뜯긴 불규칙성이 보이는가
 4. 재질            — 타일 반복 무늬 / 벽면 늘어남 / 경계선 부자연 없는가
 5. 그림자          — noon과 dawn(L키)에서 도랑 안 음영이 자연스러운가
 6. 근접 0.3m       — 노멀 디테일이 살아 있는가"""


def _check_assets():
    """§4.2: 로컬 에셋 존재 확인. 없으면 필요 목록 출력 후 종료."""
    missing = []
    for role, files in TEXTURES.items():
        for kind, fn in files.items():
            p = os.path.join(ASSETS_DIR, fn)
            if not os.path.isfile(p):
                missing.append((role, kind, fn))
    for sky, fn in HDRI_FILES.items():
        p = os.path.join(ASSETS_DIR, fn)
        if not os.path.isfile(p):
            missing.append((sky, "hdri", fn))
    if not os.path.isfile(os.path.join(ASSETS_DIR, MDL_FILE)):
        missing.append(("material", "mdl", MDL_FILE))
    if missing:
        print("=" * 64)
        print("[에러] assets/ 에 다음 파일이 없습니다. ")
        print("  python assets/download_assets.py 를 실행하거나 수동 배치 후 재실행:")
        for role, kind, fn in missing:
            print(f"  - [{role}/{kind}] {fn}")
        print("=" * 64)
        sys.exit(1)


def _ensure_noon_lookfix(src_path):
    """noon HDRI 파생본(_lookfix.exr) 생성/캐시 — 판정 C-noon1/C-공통1(r5).

    ① 태양 디스크(각반경 1.5°)를 서컴솔라 링(1.5~2.5°) p90 휘도로 캡:
       RTX 돔 샘플링의 태양 블러가 만드는 초연질 달걀형 캐스트 섀도 제거.
       제거된 직달 성분은 HDRI 태양 방향에 정합한 DistantLight(0.53°)가 대체.
    ② 지평 아래 -18°~0° 대역을 인접 하늘(elev 0.5~3.5°) 휘도로 리프트:
       overview 배경의 회청색 띠(돔 지면 영역)를 원경 헤이즈로 교체 —
       전 방위에서 '하늘 ≥ 수평선 대역 > 양지 지형' 위계 성립.
    실패 시(예: cv2 부재) 원본 경로를 그대로 반환 (경고만).
    """
    out_path = src_path[:-4] + "_lookfix.exr"
    try:
        if (os.path.isfile(out_path)
                and os.path.getmtime(out_path) >= os.path.getmtime(src_path)):
            return out_path
        os.environ.setdefault("OPENCV_IO_ENABLE_OPENEXR", "1")
        import cv2
        rgb = cv2.imread(src_path, cv2.IMREAD_UNCHANGED)[..., ::-1]
        rgb = rgb.astype(np.float64)
        h, w = rgb.shape[:2]
        lum = (0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1]
               + 0.0722 * rgb[..., 2])
        iy, ix = np.unravel_index(np.argmax(lum), lum.shape)
        vv = (np.arange(h) + 0.5) / h
        th = np.pi * vv
        ph = 2.0 * np.pi * (np.arange(w) + 0.5) / w
        st, ct = np.sin(th)[:, None], np.cos(th)[:, None]
        dx = st * np.cos(ph)[None, :]
        dy = st * np.sin(ph)[None, :]
        dz = np.broadcast_to(ct, (h, w))
        s = np.array([dx[iy, ix], dy[iy, ix], dz[iy, ix]])
        ang = np.degrees(np.arccos(
            np.clip(dx * s[0] + dy * s[1] + dz * s[2], -1.0, 1.0)))
        ring = (ang > 1.5) & (ang < 2.5)
        cap = np.percentile(lum[ring], 90)
        mask = (ang < 1.5) & (lum > cap)
        scl = np.ones_like(lum)
        scl[mask] = cap / lum[mask]
        out = rgb * scl[..., None]
        # ② 지평 아래 헤이즈 리프트 (열별 인접 하늘 색, 방위로 스무딩)
        elev = 90.0 - 180.0 * vv
        ref = out[(elev > 0.5) & (elev < 3.5)].mean(axis=0)      # (w, 3)
        k = np.ones(129) / 129.0
        ref = np.stack(
            [np.convolve(np.r_[ref[-64:, c], ref[:, c], ref[:64, c]],
                         k, mode="same")[64:-64] for c in range(3)], axis=-1)
        t = np.clip((elev + 24.0) / 6.0, 0.0, 1.0) * (elev < 0.0)
        lift = np.maximum(out, ref[None, :, :])
        out += (lift - out) * t[:, None, None]
        # RTX 돔 로더 호환: PolyHaven 원본과 같은 half-float + ZIP 압축으로 기록
        cv2.imwrite(out_path, out[..., ::-1].astype(np.float32),
                    [cv2.IMWRITE_EXR_TYPE, cv2.IMWRITE_EXR_TYPE_HALF,
                     cv2.IMWRITE_EXR_COMPRESSION, cv2.IMWRITE_EXR_COMPRESSION_ZIP])
        print(f"[HDRI] noon lookfix 생성 (태양 캡 {int(mask.sum())}px, "
              f"cap L={cap:.2f}): {out_path}")
        return out_path
    except Exception as e:                       # pragma: no cover
        print(f"[HDRI][경고] lookfix 생성 실패({e}) — 원본 사용")
        return src_path


def main():
    capture_mode = os.environ.get("NEGOBS_CAPTURE", "0") == "1"
    _check_assets()

    # ── 1단계: Isaac Sim 부팅 (SimulationApp이 무조건 먼저 — v9 검증 블록) ──
    from isaacsim import SimulationApp
    simulation_app = SimulationApp(
        {"headless": capture_mode, "width": 1920, "height": 1080})

    import carb
    import carb.input
    import omni.usd
    import omni.appwindow
    from pxr import Usd, UsdGeom, UsdShade, UsdLux, Sdf, Gf, Vt
    from omni.kit.viewport.utility import get_active_viewport, \
        capture_viewport_to_file
    from isaacsim.core.utils.viewports import set_camera_view

    settings = carb.settings.get_settings()
    settings.set("/rtx/post/dlss/execMode", 2)     # v9 검증값: DLSS Quality
    settings.set("/rtx/post/aa/op", 3)             # §6: DLSS AA

    # 판정(캡처 위생): 뷰포트 그리드·축 가이드가 렌더에 찍히지 않게 전부 끔.
    # displayOptions=0 → grid/axis/outline 등 오버레이 일괄 비활성 (씬 지오메트리
    # 렌더에는 영향 없음 — 가이드 전용 비트마스크).
    settings.set("/app/viewport/grid/enabled", False)
    settings.set("/persistent/app/viewport/displayOptions", 0)
    settings.set("/app/viewport/show/grid", False)
    settings.set("/app/viewport/outline/enabled", False)

    stage = omni.usd.get_context().get_stage()

    # ── 스테이지 단위 확인 (§1) ──
    mpu = UsdGeom.GetStageMetersPerUnit(stage)
    if abs(mpu - 1.0) > 1e-9:
        print(f"[경고] metersPerUnit={mpu} → 1.0(미터)으로 설정")
        UsdGeom.SetStageMetersPerUnit(stage, 1.0)
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)

    UsdGeom.Xform.Define(stage, "/World")

    # ── 2단계: 지형 생성 (numpy) → USD 메시 ──
    print("[지형] 하이트필드 생성 중 ...")
    tr = build_terrain(PARAMS)
    n = tr["heights"].shape[0]
    pts = np.stack([tr["X"], tr["Y"], tr["heights"]],
                   axis=-1).reshape(-1, 3).astype(np.float32)
    tris = _build_face_indices(n)                     # _face_mean과 동일 순서
    indices = tris.reshape(-1).astype(np.int32)
    nfaces = tris.shape[0] * tris.shape[1] * tris.shape[2]
    normals = tr["normals"].reshape(-1, 3).astype(np.float32)

    mesh = UsdGeom.Mesh.Define(stage, "/World/Terrain")
    try:
        mesh.GetPointsAttr().Set(Vt.Vec3fArray.FromNumpy(pts))
        mesh.GetFaceVertexIndicesAttr().Set(Vt.IntArray.FromNumpy(indices))
        mesh.GetFaceVertexCountsAttr().Set(
            Vt.IntArray.FromNumpy(np.full(nfaces, 3, dtype=np.int32)))
        mesh.GetNormalsAttr().Set(Vt.Vec3fArray.FromNumpy(normals))
    except AttributeError:                             # 구버전 USD 폴백
        mesh.GetPointsAttr().Set(Vt.Vec3fArray([Gf.Vec3f(*p) for p in pts]))
        mesh.GetFaceVertexIndicesAttr().Set(Vt.IntArray(indices.tolist()))
        mesh.GetFaceVertexCountsAttr().Set(Vt.IntArray([3] * nfaces))
        mesh.GetNormalsAttr().Set(Vt.Vec3fArray([Gf.Vec3f(*v) for v in normals]))
    mesh.SetNormalsInterpolation(UsdGeom.Tokens.vertex)
    mesh.CreateSubdivisionSchemeAttr(UsdGeom.Tokens.none)   # §3.1: 직접 노멀
    mesh.CreateDoubleSidedAttr(True)
    lo = pts.min(axis=0)
    hi = pts.max(axis=0)
    mesh.CreateExtentAttr(Vt.Vec3fArray(
        [Gf.Vec3f(*lo.tolist()), Gf.Vec3f(*hi.tolist())]))
    print(f"[지형] 정점 {len(pts):,} / 삼각형 {nfaces:,}")

    # ── 판정 A9/B3: 경계 크로스페이드용 정점 primvar (MDL scene data) ──
    pv_api = UsdGeom.PrimvarsAPI(mesh)
    for pv_name, arr in (("blend_tw", tr["vertex_blend_tw"]),
                         ("blend_wb", tr["vertex_blend_wb"])):
        pv = pv_api.CreatePrimvar(pv_name, Sdf.ValueTypeNames.FloatArray,
                                  UsdGeom.Tokens.vertex)
        flat = arr.reshape(-1).astype(np.float32)
        try:
            pv.Set(Vt.FloatArray.FromNumpy(flat))
        except AttributeError:
            pv.Set(Vt.FloatArray(flat.tolist()))

    # ── §4.1: GeomSubset — 순수 3영역 + 전이 대역 2개 (familyName='materialBind')
    # 전이 대역은 blend 재질이 primvar 크로스페이드를 수행 → 경계 톱니 제거.
    sub_flat = tr["face_subset"].reshape(-1)
    subset_prims = {}
    for k, name in ((0, "TOP"), (1, "WALL"), (2, "BOTTOM"),
                    (3, "TRANS_TW"), (4, "TRANS_WB")):
        idx = np.where(sub_flat == k)[0].astype(np.int32)
        try:
            vt_idx = Vt.IntArray.FromNumpy(idx)
        except AttributeError:
            vt_idx = Vt.IntArray(idx.tolist())
        sub = UsdGeom.Subset.CreateGeomSubset(
            mesh, name, UsdGeom.Tokens.face, vt_idx,
            UsdShade.Tokens.materialBind)
        subset_prims[name] = sub.GetPrim()
        print(f"[재질영역] {name}: {len(idx):,} faces "
              f"({len(idx) / len(sub_flat) * 100:.1f}%)")

    # ── §4.3+판정 B1/B2/B3/B6: NegObsGround.mdl (OmniPBR 호환 확장 재질) ──
    # 판정 B2(r3 치명): OmniPBR project_uvw(월드 큐빅)는 축 선택이 하드
    # 스위치라 55~60° 벽의 대각 방위에서 텍스처가 낙하 방향으로 늘어남 →
    # MDL 내부를 노멀 가중 triplanar 소프트 블렌딩으로 교체 (§4.3의 목적인
    # 'UV 없이 경사 벽면 늘어남 방지'를 실제로 달성하는 구현).
    # 순수 영역도 같은 MDL을 쓰므로(투영·노이즈 phase 공유) 전이 대역의
    # w=0/1 끝단이 이웃 순수 재질과 픽셀 단위로 일치한다.
    mp = PARAMS["material"]
    mdl_path = os.path.join(ASSETS_DIR, MDL_FILE)

    ROLE_SETUP = dict(     # 역할별 (tile, rotate, floor, mult, spec, rough_noise)
        top=dict(tile=mp["top_tile"], rotate=mp["top_rotate"],
                 floor=0.0, mult=1.0, spec=0.5, rnoise=0.0, rnoise_wl=1.2),
        wall=dict(tile=mp["wall_tile"], rotate=mp["wall_rotate"],
                  floor=mp["wall_rough_floor"],
                  mult=1.0 - mp["wall_rough_floor"],
                  spec=0.5, rnoise=0.0, rnoise_wl=1.2),
        bottom=dict(tile=mp["bottom_tile"], rotate=mp["bottom_rotate"],
                    floor=0.0, mult=mp["bottom_rough_mult"],
                    spec=mp["bottom_specular"],
                    rnoise=mp["bottom_rough_noise"],
                    rnoise_wl=mp["bottom_rough_noise_wl"]),
    )
    for _role in ROLE_SETUP:
        ROLE_SETUP[_role]["desat"] = mp["desat_bright"][_role]
        ROLE_SETUP[_role]["bump"] = mp["bump_role"][_role]

    def _set_layer_inputs(sh, suffix, role):
        """텍스처 세트 a/b 입력 일괄 설정 — 역할(top/wall/bottom) 파라미터."""
        cfg = ROLE_SETUP[role]
        tex = TEXTURES[role]
        for in_name, fn, cs in (
                (f"diffuse_texture_{suffix}", tex["diff"], "auto"),
                (f"normalmap_texture_{suffix}", tex["nor"], "raw"),
                (f"roughness_texture_{suffix}", tex["rough"], "raw")):
            i = sh.CreateInput(in_name, Sdf.ValueTypeNames.Asset)
            i.Set(os.path.join(ASSETS_DIR, fn))
            try:
                i.GetAttr().SetColorSpace(cs)
            except Exception:
                pass
        s = 1.0 / float(cfg["tile"])   # texture_scale = 타일링 횟수 = 1/T[m]
        F = Sdf.ValueTypeNames.Float
        sh.CreateInput(f"texture_scale_{suffix}",
                       Sdf.ValueTypeNames.Float2).Set(Gf.Vec2f(s, s))
        sh.CreateInput(f"texture_rotate_{suffix}", F).Set(float(cfg["rotate"]))
        sh.CreateInput(f"rough_floor_{suffix}", F).Set(float(cfg["floor"]))
        sh.CreateInput(f"rough_mult_{suffix}", F).Set(float(cfg["mult"]))
        sh.CreateInput(f"specular_level_{suffix}", F).Set(float(cfg["spec"]))
        sh.CreateInput(f"rough_noise_{suffix}", F).Set(float(cfg["rnoise"]))
        sh.CreateInput(f"rough_noise_wavelength_{suffix}", F).Set(
            float(cfg["rnoise_wl"]))
        # 반복 파괴: 90° 패치 혼합 마스크 파장 + 저주파 macro albedo 변조
        sh.CreateInput(f"patch_wavelength_{suffix}", F).Set(
            float(mp["patch_wavelength"][role]))
        sh.CreateInput(f"macro_amp_{suffix}", F).Set(
            float(mp["macro_amp"][role]))
        sh.CreateInput(f"macro_wavelength_{suffix}", F).Set(
            float(mp["macro_wavelength"][role]))
        # 판정 B8(r3): 밝은 스페클(잔돌) 채도 억제
        sh.CreateInput(f"desat_bright_{suffix}", F).Set(float(cfg["desat"]))
        # 판정 B2(r4) ③: 역할별 노멀맵 강도 — 전이 대역 입자 대비 복원
        sh.CreateInput(f"bump_factor_{suffix}", F).Set(float(cfg["bump"]))

    def make_ground(path, role_a, role_b=None, blend_primvar=""):
        mtl = UsdShade.Material.Define(stage, path)
        sh = UsdShade.Shader.Define(stage, path + "/Shader")
        sh.CreateImplementationSourceAttr(UsdShade.Tokens.sourceAsset)
        sh.SetSourceAsset(Sdf.AssetPath(mdl_path), "mdl")
        sh.SetSourceAssetSubIdentifier("NegObsGround", "mdl")
        F = Sdf.ValueTypeNames.Float
        _set_layer_inputs(sh, "a", role_a)
        if role_b is not None:
            _set_layer_inputs(sh, "b", role_b)
            sh.CreateInput("use_blend", Sdf.ValueTypeNames.Bool).Set(True)
            # MDL 제약(C331: data_lookup 이름은 const)으로 primvar는 bool 선택
            sh.CreateInput("blend_use_wb", Sdf.ValueTypeNames.Bool).Set(
                blend_primvar == "blend_wb")
            sh.CreateInput("blend_default", F).Set(0.5)
            sh.CreateInput("blend_edge_noise", F).Set(
                float(mp["blend_edge_noise"]))
            sh.CreateInput("blend_edge_wavelength", F).Set(
                float(mp["blend_edge_wl"]))
        sh.CreateInput("bump_factor", F).Set(float(mp["bump_factor"]))
        # 판정 B2(r4/r5) ①: triplanar 축 전환 대역 가중치 디더링 + 가중 지수
        sh.CreateInput("tri_dither", F).Set(float(mp["tri_dither"]))
        sh.CreateInput("tri_dither_wavelength", F).Set(
            float(mp["tri_dither_wavelength"]))
        sh.CreateInput("tri_weight_exp", F).Set(float(mp["tri_exp"]))
        # PolyHaven _nor_dx = DirectX 규약 → flip_tangent_v=true (기본값) 유지
        for out_name in ("surface", "displacement", "volume"):
            mtl.CreateOutput(f"mdl:{out_name}",
                             Sdf.ValueTypeNames.Token).ConnectToSource(
                sh.ConnectableAPI(), "out")
        return mtl

    # ── 판정 C-noon1 분리 진단: NEGOBS_CLAY=1 → 백색 무광(클레이) 오버라이드 ──
    # 알베도·노멀맵·러프니스 텍스처를 전부 끈 회백색 무광 재질로 전체를 덮어
    # 달걀형 암부 블롭이 텍스처/노멀맵 원인인지(사라짐) 지오메트리 음영
    # 원인인지(남음)를 분리한다. 진단 전용 — 기본 실행 경로에는 영향 없음.
    clay_mode = os.environ.get("NEGOBS_CLAY", "0") == "1"

    mat_top = make_ground("/World/Looks/MatTop", "top")
    mat_wall = make_ground("/World/Looks/MatWall", "wall")
    mat_bottom = make_ground("/World/Looks/MatBottom", "bottom")
    mat_tw = make_ground("/World/Looks/MatTransTW", "top", "wall", "blend_tw")
    mat_wb = make_ground("/World/Looks/MatTransWB", "wall", "bottom",
                         "blend_wb")
    for name, mtl in (("TOP", mat_top), ("WALL", mat_wall),
                      ("BOTTOM", mat_bottom), ("TRANS_TW", mat_tw),
                      ("TRANS_WB", mat_wb)):
        UsdShade.MaterialBindingAPI.Apply(subset_prims[name]).Bind(mtl)
    UsdShade.MaterialBindingAPI.Apply(mesh.GetPrim()).Bind(mat_top)  # 폴백

    if clay_mode:
        omnipbr_path = os.path.expanduser(
            "~/miniconda3/envs/env_isaaclab/lib/python3.10/site-packages/"
            "omni/mdl/core/Base/OmniPBR.mdl")
        mtl_c = UsdShade.Material.Define(stage, "/World/Looks/MatClay")
        shc = UsdShade.Shader.Define(stage, "/World/Looks/MatClay/Shader")
        shc.CreateImplementationSourceAttr(UsdShade.Tokens.sourceAsset)
        shc.SetSourceAsset(Sdf.AssetPath(omnipbr_path), "mdl")
        shc.SetSourceAssetSubIdentifier("OmniPBR", "mdl")
        shc.CreateInput("diffuse_color_constant",
                        Sdf.ValueTypeNames.Color3f).Set(
            Gf.Vec3f(0.75, 0.75, 0.75))
        shc.CreateInput("reflection_roughness_constant",
                        Sdf.ValueTypeNames.Float).Set(0.9)
        for out_name in ("surface", "displacement", "volume"):
            mtl_c.CreateOutput(f"mdl:{out_name}",
                               Sdf.ValueTypeNames.Token).ConnectToSource(
                shc.ConnectableAPI(), "out")
        for prim in list(subset_prims.values()) + [mesh.GetPrim()]:
            UsdShade.MaterialBindingAPI.Apply(prim).Bind(mtl_c)
        print("[진단] CLAY 모드: 텍스처·노멀맵 없는 백색 무광 재질로 오버라이드")

    # ── §5: DomeLight + HDRI ──
    lp = PARAMS["light"]
    dome = UsdLux.DomeLight.Define(stage, "/World/DomeLight")
    dome_int_attr = dome.CreateIntensityAttr(float(lp["dome_intensity"]))
    dome.CreateTextureFormatAttr("latlong")
    tex_attr = dome.CreateTextureFileAttr()
    hdri_paths = {k: os.path.join(ASSETS_DIR, v) for k, v in HDRI_FILES.items()}
    # 판정 C-noon1/C-공통1(r5): noon 돔은 태양 캡 + 지평 아래 헤이즈 리프트
    # 파생본을 사용 (직달 태양은 아래 NoonSun DistantLight가 담당)
    hdri_paths["noon"] = _ensure_noon_lookfix(hdri_paths["noon"])
    # 판정 C-공통1 규명(렌더 프로브로 확인): RTX 돔은 Z-up 스테이지에서 이미
    # 극축이 +Z로 올바르며 추가 회전 불필요(rotateX=0). 이전 캡처의 '남색/백색
    # 배경'은 하늘이 아니라 뷰포트 무한 그리드 오버레이 평면이 배경을 덮은 것
    # → 위 displayOptions=0 으로 해결됨.
    xf_dome = UsdGeom.Xformable(dome.GetPrim())
    rot_op = xf_dome.AddRotateZOp()                # 태양 방위 ([ / ] 키)
    rot_op.Set(0.0)

    # 판정 C-공통1(r4): overview 배경 방위(월드 az≈33°)의 HDRI 수평선 대역이
    # 어두운 섹터(실측 tex az≈87°에서 0.206, 태양쪽 216°에서 0.544)라
    # '하늘>양지' 위계가 붕괴 → noon 돔을 Z회전해 밝은 수평선 섹터(태양 방위
    # 산란광)를 overview 배경 방위로 돌린다. dawn은 문제 없음 → 회전 0 유지.
    sky_base_rot = dict(noon=float(lp.get("noon_dome_rot", 0.0)), dawn=0.0)
    dome_user_rot = [0.0]                          # [ / ] 키 사용자 오프셋

    # 판정 C-noon1(r5): 두 하늘 모두 HDRI 태양 방향에 정합한 보조 태양.
    #  - noon: 돔에서 캡으로 제거된 태양 디스크를 대체 (0.53° → 경질 그림자)
    #  - dawn: 확산 글로 중심에 정합 (초연질 블롭 위에 읽히는 그림자를 겹침)
    # rotZ = 돔 회전 R + hdri_sun_rotz_offset (기둥 그림자 프로브 실측 상수)
    def _make_sun(path, elev, intensity, color3):
        sun = UsdLux.DistantLight.Define(stage, path)
        sun.CreateAngleAttr(0.53)
        sun.CreateIntensityAttr(float(intensity))
        sun.CreateColorAttr(Gf.Vec3f(*[float(c) for c in color3]))
        xf = UsdGeom.Xformable(sun.GetPrim())
        rz = xf.AddRotateZOp()
        rz.Set(0.0)
        xf.AddRotateXOp().Set(90.0 - float(elev))   # 지평선 위 고도
        return rz, UsdGeom.Imageable(sun.GetPrim())

    sun_rz, sun_img, sun_on = {}, {}, {}
    sun_rz["noon"], sun_img["noon"] = _make_sun(
        "/World/NoonSun", lp["noon_sun_elev"], lp["noon_sun_intensity"],
        lp["noon_sun_color"])
    sun_on["noon"] = bool(lp.get("noon_sun_enable", True))
    sun_rz["dawn"], sun_img["dawn"] = _make_sun(
        "/World/DawnSun", lp["dawn_sun_elev"], lp["dawn_sun_intensity"],
        lp["dawn_sun_color"])
    sun_on["dawn"] = bool(lp.get("dawn_sun_enable", True))

    def apply_dome_rot(sky):
        rot = sky_base_rot[sky] + dome_user_rot[0]
        rot_op.Set(rot)
        # 보조 태양은 돔과 함께 회전 (글로/그림자 방위 일치 유지)
        for k in sun_rz:
            sun_rz[k].Set(rot + float(lp["hdri_sun_rotz_offset"]))

    def set_sky(name):
        nonlocal cur_sky
        cur_sky = name
        apply_dome_rot(name)
        p = hdri_paths[name]
        print(f"[하늘] {name}: {os.path.basename(p)} "
              f"(exists={os.path.isfile(p)}, "
              f"{os.path.getsize(p) / 1e6:.1f}MB)" if os.path.isfile(p)
              else f"[하늘][경고] {name}: {p} 없음!")
        tex_attr.Set(p)
        dome_int_attr.Set(float(lp["dawn_dome_intensity"] if name == "dawn"
                                else lp["dome_intensity"]))
        for k in sun_img:
            if k == name and sun_on[k]:
                sun_img[k].MakeVisible()
            else:
                sun_img[k].MakeInvisible()

    cur_sky = "noon"
    set_sky(cur_sky)

    # ── §6: 시작 카메라 — 도랑 중앙 6m 밖, 높이 1.2m, 피치 -8° ──
    cl = tr["centerline"]
    mid = len(cl["x"]) // 2
    dcx, dcy = float(cl["x"][mid]), float(cl["y"][mid])

    def ground_z(px, py):
        return float(bilinear_sample(tr["heights"], tr["xs"], tr["ys"], px, py))

    def look_from(eye, pitch_deg=None, target=None):
        if target is None:
            p = math.radians(pitch_deg)
            target = [eye[0], eye[1] + 5.0 * math.cos(p),
                      eye[2] + 5.0 * math.sin(p)]
        set_camera_view(eye=list(eye), target=list(target))

    eye0 = [dcx, dcy - 6.0, ground_z(dcx, dcy - 6.0) + 1.2]
    look_from(eye0, pitch_deg=-8.0)

    # ── §6: 렌더 모드 토글 상태 ──
    pt_spp = int(PARAMS["render"]["pt_total_spp"])

    def set_render_mode(mode):
        if mode == "PathTracing":
            settings.set("/rtx/pathtracing/spp", 1)
            settings.set("/rtx/pathtracing/totalSpp", pt_spp)
            settings.set("/rtx/pathtracing/optixDenoiser/enabled", True)
            # 판정 C-noon1: 최심부 그늘 순흑 방지 — 간접광 바운스 상향
            settings.set("/rtx/pathtracing/maxBounces",
                         int(PARAMS["render"]["pt_max_bounces"]))
            settings.set("/rtx/rendermode", "PathTracing")
        else:
            settings.set("/rtx/rendermode", "RaytracedLighting")

    os.makedirs(LOOKCHECK_DIR, exist_ok=True)

    def capture(path):
        vp = get_active_viewport()
        capture_viewport_to_file(vp, file_path=path)

    # ===================================================================
    # 자동 캡처 모드 (headless 검증 파이프라인 전용)
    # ===================================================================
    if capture_mode:
        out_dir = os.environ.get("NEGOBS_CAPTURE_DIR",
                                 os.path.join(LOOKCHECK_DIR, "auto"))
        os.makedirs(out_dir, exist_ok=True)
        mode_sel = os.environ.get("NEGOBS_CAPTURE_MODE", "rt")
        modes = ["rt", "pt"] if mode_sel == "both" else [mode_sel]

        # 뷰 정의 — §7 체크리스트의 6개 시점 대응
        g_c = ground_z(dcx, dcy)                 # 도랑 중앙(카빙 후) 높이
        g_edge = ground_z(dcx, dcy - 3.0)        # 도랑 앞 초지 높이
        wt_mid = float(cl["w_top_half"][mid])
        # 립 위 시점(도랑 종방향으로 바라보기)용 station
        k1 = int(np.searchsorted(cl["s"], 0.30 * cl["arc_length"]))
        k2 = int(np.searchsorted(cl["s"], 0.62 * cl["arc_length"]))
        p1 = (float(cl["x"][k1]), float(cl["y"][k1]))
        p2 = (float(cl["x"][k2]), float(cl["y"][k2]))
        cz1 = tr["collapse"]["centers_xy"][0]

        def v_eye_tgt(eye, tgt):
            return dict(eye=[float(e) for e in eye], tgt=[float(t) for t in tgt])

        VIEWS = dict(
            start=v_eye_tgt(
                [dcx, dcy - 6.0, ground_z(dcx, dcy - 6.0) + 1.2],
                [dcx, dcy - 6.0 + 5.0 * math.cos(math.radians(8)),
                 ground_z(dcx, dcy - 6.0) + 1.2 - 5.0 * math.sin(math.radians(8))]),
            front_2m=v_eye_tgt(
                [dcx, dcy - 5.0, g_edge + 2.0], [dcx, dcy, g_c + 0.3]),
            grazing_05=v_eye_tgt(
                [dcx, dcy - 9.0, ground_z(dcx, dcy - 9.0) + 0.5],
                [dcx, dcy + 2.0, ground_z(dcx, dcy - 9.0) + 0.35]),
            lip_along=v_eye_tgt(
                [p1[0], p1[1] - (wt_mid + 0.4), ground_z(p1[0], p1[1] - (wt_mid + 0.4)) + 1.1],
                [p2[0], p2[1], ground_z(p2[0], p2[1]) - 0.3]),
            collapse_zone=v_eye_tgt(
                [cz1[0], cz1[1] - 3.0, ground_z(cz1[0], cz1[1] - 3.0) + 1.6],
                [cz1[0], cz1[1], ground_z(cz1[0], cz1[1])]),
            inside_wall=v_eye_tgt(
                [dcx, dcy - 0.7, g_c + 0.6], [dcx, dcy + 0.9, g_c + 0.5]),
            closeup_03=v_eye_tgt(
                [dcx, dcy - wt_mid - 0.25, ground_z(dcx, dcy - wt_mid) + 0.35],
                [dcx, dcy - wt_mid + 0.15, ground_z(dcx, dcy - wt_mid) - 0.15]),
            top_material=v_eye_tgt(
                [dcx - 3.0, dcy - 4.0, ground_z(dcx - 3.0, dcy - 4.0) + 1.5],
                [dcx - 3.0, dcy - 2.8, ground_z(dcx - 3.0, dcy - 2.8)]),
            # 판정 C-공통1(r3): 부감 피치를 낮춰(-26°→약 -15°) 지평 부근의
            # 밝은 하늘 대역이 프레임 상단에 들어오게 구도 조정
            overview=v_eye_tgt(
                [dcx - 10.0, dcy - 8.0, g_edge + 5.5],
                [dcx + 4.0, dcy + 1.0, g_c + 2.2]),
            topdown=v_eye_tgt(
                [dcx, dcy - 0.5, g_edge + 17.0], [dcx, dcy, g_c]),
        )
        DAWN_VIEWS = ["front_2m", "grazing_05", "inside_wall", "overview"]

        view_f = os.environ.get("NEGOBS_VIEWS", "")
        if view_f:
            keep = {v.strip() for v in view_f.split(",") if v.strip()}
            VIEWS = {k: v for k, v in VIEWS.items() if k in keep}
            DAWN_VIEWS = [v for v in DAWN_VIEWS if v in keep]
        sky_f = os.environ.get("NEGOBS_SKIES", "noon,dawn")
        skies = [s.strip() for s in sky_f.split(",") if s.strip()]

        manifest = []
        print(f"[캡처] 모드={modes} 하늘={skies} 뷰={list(VIEWS)}")
        for _ in range(30):                       # 초기 로딩 워밍업
            simulation_app.update()

        for mode in modes:
            set_render_mode("PathTracing" if mode == "pt" else "RaytracedLighting")
            warm = int(os.environ.get(
                "NEGOBS_WARMUP", str(pt_spp + 60 if mode == "pt" else 90)))
            # 돔 회전 스윕 (개발 파이프라인 전용 — C-공통1 후보 검증)
            sweep_env = os.environ.get("NEGOBS_DOME_SWEEP", "")
            sweep = ([float(r) for r in sweep_env.split(",") if r.strip()]
                     if sweep_env else [None])
            for sky in skies:
                set_sky(sky)
                names = list(VIEWS) if sky == "noon" else \
                    [v for v in DAWN_VIEWS if v in VIEWS]
                for rot, vname in ((r, v) for r in sweep for v in names):
                    suffix = "" if rot is None else f"_rot{int(rot):+d}"
                    if rot is not None:
                        dome_user_rot[0] = rot        # 보조 태양도 함께 회전
                        apply_dome_rot(sky)
                    v = VIEWS[vname]
                    look_from(v["eye"], target=v["tgt"])
                    for _ in range(warm):
                        simulation_app.update()
                    fp = os.path.join(out_dir,
                                      f"{mode}_{sky}_{vname}{suffix}.png")
                    capture(fp)
                    # 캡처는 비동기 → 파일이 생기고 크기가 안정될 때까지 대기
                    ok, prev_sz = False, -1
                    for _ in range(40):
                        simulation_app.update()
                        if os.path.isfile(fp):
                            sz = os.path.getsize(fp)
                            if sz > 0 and sz == prev_sz:
                                ok = True
                                break
                            prev_sz = sz
                    manifest.append(dict(file=fp, mode=mode, sky=sky,
                                         view=vname, ok=ok))
                    print(f"[캡처] {os.path.basename(fp)} "
                          f"{'OK' if ok else 'FAIL'}")
        # manifest는 조각 실행(하늘/모드 분할) 간 병합 — 같은 file 항목은 갱신
        import json
        mf_path = os.path.join(out_dir, "manifest.json")
        prev = dict(views={}, shots=[])
        if os.path.isfile(mf_path):
            try:
                with open(mf_path) as f:
                    prev = json.load(f)
            except Exception:
                pass
        shots = {s["file"]: s for s in prev.get("shots", [])}
        for s in manifest:
            shots[s["file"]] = s
        prev.get("views", {}).update({k: v for k, v in VIEWS.items()})
        with open(mf_path, "w") as f:
            json.dump(dict(views=prev.get("views", VIEWS),
                           shots=list(shots.values())),
                      f, indent=2, ensure_ascii=False)
        simulation_app.close()
        return

    # ===================================================================
    # GUI 룩 체크 모드 (기본)
    # ===================================================================
    input_iface = carb.input.acquire_input_interface()
    appwindow = omni.appwindow.get_default_app_window()
    K = carb.input.KeyboardInput
    rot_step = float(PARAMS["light"]["dome_rotation_step"])

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
                print(f"[렌더] PathTracing (totalSpp={pt_spp}) — 멈춰 서서 볼 때 권장")
        elif event.input == K.S:
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            fp = os.path.join(LOOKCHECK_DIR, f"negobs_{ts}.png")
            capture(fp)
            print(f"[캡처] {fp}")
        elif event.input == K.L:
            set_sky("dawn" if cur_sky == "noon" else "noon")
            print(f"[하늘] {cur_sky} "
                  f"({'낮은 태양·긴 그림자' if cur_sky == 'dawn' else '맑은 한낮'})")
        elif event.input == K.LEFT_BRACKET:
            dome_user_rot[0] -= rot_step
            apply_dome_rot(cur_sky)
            print(f"[태양 방위] 오프셋 {dome_user_rot[0]:+.0f}°")
        elif event.input == K.RIGHT_BRACKET:
            dome_user_rot[0] += rot_step
            apply_dome_rot(cur_sky)
            print(f"[태양 방위] 오프셋 {dome_user_rot[0]:+.0f}°")
        return True

    keyboard_sub = input_iface.subscribe_to_keyboard_events(
        appwindow.get_keyboard(), on_key)

    print("=" * 64)
    print(BANNER)
    print("-" * 64)
    print("패스 트레이싱은 멈춰 서서 볼 때, 이동은 실시간 모드 권장")
    print("※ 키가 안 먹으면 Isaac Sim 창을 한 번 클릭해서 포커스를 줘!")
    print("=" * 64)

    # §6 메인 루프 — 렌더 전용 (물리·World 없음)
    while simulation_app.is_running():
        simulation_app.update()

    input_iface.unsubscribe_to_keyboard_events(
        appwindow.get_keyboard(), keyboard_sub)
    simulation_app.close()


if __name__ == "__main__":
    main()
