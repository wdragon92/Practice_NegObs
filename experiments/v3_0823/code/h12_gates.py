#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""h12_gates.py — sceneH1 / sceneH2 (**test-ext**) 4팔 프로브의 VG 게이트 일괄 판정.

`h67_yield.py` 가 **A팔 단독**(수율·VG-datum(A,C)·VG-10·VG-08·VG-void)을 보는 데 반해,
이 스크립트는 **test-ext 가 요구하는 4팔 완비**(계획 §3.1) 위에서만 성립하는 게이트를 본다:

    VG-01   A/B 위험-GT 동일성      heightmap 바이트 · 셀 단위 3층 · `polar_gt` 비트
    VG-02   C/D 전 칸 음성          heightmap 직접 대조(C↔D · A↔C) + 라벨 `polar_gt`
    VG-datum (A,B,C,D)              팔별 |Δ cam.ground_z| 3층 · 쌍 생존율
    VG-10   포즈 게이트             6키 < 1e-6 · 전 팔 × 전 컷
    VG-08   세그 사이드카           존재 + **컷별 마스크가 실제로 다른가**(§7.6 권고 4)
    VG-06   모서리 소속             A팔 strict-H 프레임의 ID 마스크에서
                                    가림체 px > 0 · 낙차 구조물 px = 0
    VG-07   (A,C) 광학차 로그       쌍별 픽셀 차 통계 + 분포 (D58 층화의 입력)
    WHITE   순백 대면적 (산출층)     **공식 = frac(min-channel > 0.8)** [D85 채택]
                                    구 `frac(max>0.8)` 은 deprecated 로 한 번 더 인쇄
    paired-H                        A·B 가 **둘 다** strict-H 인 프레임 수 (§3.2 하한 12)

사용
    PY=/home/vislab/miniconda3/envs/env_seg/bin/python
    $PY experiments/v3_0823/code/h12_gates.py \
        --root dataset --stamp 260823_v3p5_h12probe --split test \
        --labels-ac experiments/v3_0823/annotations/h12_ac_labels.json \
        --labels-bd experiments/v3_0823/annotations/h12_bd_labels.json \
        --out experiments/v3_0823/h12_gates.json

    # WHITE 지표만 (라벨 불요 · A팔 png 만 읽는다 — h67 계열 2팔 라운드에도 쓴다)
    $PY experiments/v3_0823/code/h12_gates.py --white-only \
        --root dataset --stamp 260823_v3p5_h67reg --split val --scenes sceneH7
"""
from __future__ import annotations

import argparse
import collections
import glob
import hashlib
import io
import json
import math
import os
import sys
import zipfile

import numpy as np

ARMS = ("A", "B", "C", "D")

# 씬별 프림 경로 접두어 — **루트 앵커 매칭**을 쓴다.
#   SCENE_H67_BUILD §3.4 경고: 부분문자열 매칭(`"/Lower"`)은 `…/Walk/Lower` 와
#   `…/Lower/Floor` 를 섞는다. 아래는 전부 `/World/<Scene>/` 로 시작하는 앵커다.
PRIMS = {
    "sceneH1": dict(
        # 가림체 = **둔덕이라는 하나의 지형체**다. 마루 슬래브(`BermCrest`)만 세면
        #   피치가 깊은 프레임에서 마루 능선이 화각 위로 밀려나 0 px 이 되고, 실제로
        #   시선을 막고 있는 사면(`Ground/BermRise*`)이 집계에서 빠진다
        #   [실측 260823_v3p5_h12probe_A cut 0001]. 사면과 마루는 같은 성토체다.
        occluder=["/World/SceneH1/BermCrest", "/World/SceneH1/Ground/BermRise",
                  "/World/SceneH1/Ground/BermFill"],
        hazard=["/World/SceneH1/RetainWall/", "/World/SceneH1/Revet/",
                "/World/SceneH1/Bed/", "/World/SceneH1/Water/"],
        cue=["/World/SceneH1/Rail/", "/World/SceneH1/Tactile",
             "/World/SceneH1/TactileCrest", "/World/SceneH1/Nosing/",
             "/World/SceneH1/Sign/", "/World/SceneH1/Bollard_",
             "/World/SceneH1/Delineator/", "/World/SceneH1/GKitCrown",
             "/World/SceneH1/GKitWalk", "/World/SceneH1/GKitRamp",
             "/World/SceneH1/TreeGrate_", "/World/SceneH1/Shadow/",
             "/World/SceneH1/Dress/"],
    ),
    "sceneH2": dict(
        occluder=["/World/SceneH2/LandingSlab"],
        hazard=["/World/SceneH2/Stair/", "/World/SceneH2/MidLanding/",
                "/World/SceneH2/LowerPlaza/"],
        # 낙차 구조물이 **아닌** 맥락 프림. 선큰 광장을 마감하는 강의동은 4팔 공통
        #   구조물이고, H 프레임에서 그 **기단이 광장 레벨보다 낮게 보이는 것**은
        #   낙차 기하의 노출이 아니라 *맥락 단서*다(이 연구가 세려는 바로 그 신호).
        #   VG-06 판정에는 넣지 않고 화면 기여만 별도로 인쇄한다.
        context=["/World/SceneH2/Building/"],
        cue=["/World/SceneH2/RailS/", "/World/SceneH2/RailN/",
             "/World/SceneH2/Tactile", "/World/SceneH2/NosingInlay/",
             "/World/SceneH2/NosingTerrace/", "/World/SceneH2/Sign/",
             "/World/SceneH2/Bollard_", "/World/SceneH2/Planter/",
             "/World/SceneH2/GKit", "/World/SceneH2/TreeGrate_",
             "/World/SceneH2/Shadow/", "/World/SceneH2/Dress/"],
    ),
    # ── 3차 빌더 런 (RENDER_PLAN_V3 §8 결재 1 A안 순서의 다음 두 씬) ───────────
    "sceneH3": dict(
        # 가림체 = **석축 L자 솔리드 하나**다. `Along`(회랑 북벽)과 `Flank`(계단실
        #   서벽)는 같은 성토 옹벽체이고 그 교선이 이 씬의 은닉 모서리이므로 접두어를
        #   `BendWall` 하나로 잡는다(갓돌 `AlongCap`·`FlankCap` 포함).
        occluder=["/World/SceneH3/BendWall"],
        hazard=["/World/SceneH3/Stair/", "/World/SceneH3/Lower/"],
        # 낙차 구조물이 **아닌** 맥락 프림 — 계단실을 마감하는 담장·동측 석축은 4팔
        #   공통 구조물이다. VG-06 판정에는 넣지 않고 화면 기여만 별도 인쇄한다.
        context=["/World/SceneH3/WallS/", "/World/SceneH3/WallE/",
                 "/World/SceneH3/Bank/"],
        cue=["/World/SceneH3/HandrailW/", "/World/SceneH3/HandrailE/",
             "/World/SceneH3/Mirror/", "/World/SceneH3/Tactile",
             "/World/SceneH3/NosingWalk/", "/World/SceneH3/NosingStair/",
             "/World/SceneH3/Sign/", "/World/SceneH3/Bollard_",
             "/World/SceneH3/GKitWalk", "/World/SceneH3/TreeGrate_",
             "/World/SceneH3/Shadow/", "/World/SceneH3/Dress/"],
    ),
    # ── W2-lite (훈련측 **val** 공급 · 계획 §3.5) ────────────────────────────
    #   H6 = H1 의 형제(둔덕형) · H7 = H3 의 형제(복도 굴절형). 접두어는 **루트 앵커**이며
    #   프림 인벤토리는 `.idseg.npz` 의 `idToLabels` 실측으로 대조했다(2026-08-24).
    "sceneH6": dict(
        # H1 과 같은 이유로 마루(`BermCrest`)만 세지 않고 **성토체 전체**를 잡는다 —
        #   사면(`Ground/BermRise_*` 48개)·성토(`Ground/BermFill`)가 같은 둔덕이다.
        occluder=["/World/SceneH6/BermCrest", "/World/SceneH6/Ground/BermRise",
                  "/World/SceneH6/Ground/BermFill"],
        # 낙차 구조물 = SCENE_H67_BUILD §4 가 VG-06 실측에 쓴 그 세 접두어.
        hazard=["/World/SceneH6/RetainWall/", "/World/SceneH6/Riprap/",
                "/World/SceneH6/Water/"],
        # 대안(對岸) 제방은 4팔 공통 구조물이고 낙차 기하가 아니다 — 화면 기여만 인쇄.
        context=["/World/SceneH6/FarBank/"],
        cue=["/World/SceneH6/Rail/", "/World/SceneH6/Tactile",
             "/World/SceneH6/Nosing/", "/World/SceneH6/Sign/",
             "/World/SceneH6/Bollard_", "/World/SceneH6/Delineator/",
             "/World/SceneH6/GKitWalk", "/World/SceneH6/GKitApproach",
             "/World/SceneH6/TreeGrate_", "/World/SceneH6/Shadow/",
             "/World/SceneH6/Dress/"],
    ),
    "sceneH7": dict(
        # 가림체 = 굴절 옹벽 L자 솔리드 (`Along`·`AlongCap`·`Flank`·`FlankCap`).
        occluder=["/World/SceneH7/BendWall"],
        # **루트 앵커 필수** — `/World/SceneH7/Lower/` 는 하부 통로(낙차)이고
        #   `/World/SceneH7/Walk/Lower` 는 상부 보도 하단 구간(구조물)이다.
        #   부분문자열 `"/Lower"` 를 쓰면 둘이 섞인다 (SCENE_H67_BUILD §3.4 경고).
        hazard=["/World/SceneH7/Stair/", "/World/SceneH7/Lower/"],
        context=["/World/SceneH7/WallN/", "/World/SceneH7/WallE/",
                 "/World/SceneH7/Bank/", "/World/SceneH7/Walk/"],
        cue=["/World/SceneH7/HandrailW/", "/World/SceneH7/HandrailE/",
             "/World/SceneH7/LevelRail/", "/World/SceneH7/Tactile",
             "/World/SceneH7/NosingWalk/", "/World/SceneH7/NosingStair/",
             "/World/SceneH7/Sign/", "/World/SceneH7/Bollard_",
             "/World/SceneH7/GKitWalk", "/World/SceneH7/TreeGrate_",
             "/World/SceneH7/Shadow/", "/World/SceneH7/Dress/"],
    ),
    # **측방 씬** — 가림체가 없다. VG-06 의 "가림체가 종단 모서리를 소유한다"는
    #   판정은 이 씬에 대해 **적용되지 않으며**(계획 §2.3 은 은닉을 요구하지 않는다),
    #   대신 `gate_sectors` 가 폴라 GT 의 섹터 분포를 잰다. `lateral=True` 가 그 전환이다.
    "sceneL1": dict(
        lateral=True,
        occluder=[],
        hazard=["/World/SceneL1/CanalS/", "/World/SceneL1/CanalN/"],
        cue=["/World/SceneL1/RailS/", "/World/SceneL1/RailN/",
             "/World/SceneL1/Tactile", "/World/SceneL1/Nosing/",
             "/World/SceneL1/Sign/", "/World/SceneL1/Bollard_",
             "/World/SceneL1/Delineator/", "/World/SceneL1/GKitPlaza",
             "/World/SceneL1/GKitWalk", "/World/SceneL1/TreeGrate_",
             "/World/SceneL1/Shadow/", "/World/SceneL1/Dress/"],
    ),
    # ── 4차 빌더 런 · **N-cue 씬 (④-a 함정 표본)** ────────────────────────────
    #   판정 기준이 H 씬·측방 씬과 또 다르다. 이 씬들에는 **낙차가 없으므로**
    #     · VG-06(모서리 소속)은 적용 대상이 아니다 — 가림체도 낙차 구조물도 없다
    #     · strict-H·paired-H 는 정의상 0 이고 그것이 정상이다
    #   대신 판정층은 세 가지다 (`ncue=True` 가 그 전환이다):
    #     (a) `gate_allneg`   전 팔·전 프레임 GT 올-음성 + **`cells_raw` = 0**
    #     (b) `gate_cue_px`   단서 클래스별 픽셀 분포 (DZ §12-5 k 게이트의 데이터 원천)
    #     (c) `gate_vg07(C,D)` 단서 ON↔OFF 광학차 (계기판 ③ 용량-반응 입력)
    #   `hazard` 키는 **함정 기하**(낙차가 아님)를 가리킨다 — 측정만 하고 판정하지 않는다.
    "sceneN9": dict(
        ncue=True,
        occluder=[],
        # 함정 기하 = 승강장 경계 연석 0.200 m (임계 0.30 미만). 낙차 아님.
        hazard=["/World/SceneN9/Road/", "/World/SceneN9/Curb/",
                "/World/SceneN9/RoadFlush/"],
        cue=["/World/SceneN9/Tactile/", "/World/SceneN9/Fence/",
             "/World/SceneN9/Nosing/", "/World/SceneN9/Sign/",
             "/World/SceneN9/Bollard_", "/World/SceneN9/Marking/",
             "/World/SceneN9/GKitWalk", "/World/SceneN9/GKitPlat",
             "/World/SceneN9/TreeGrate_", "/World/SceneN9/Shadow/",
             "/World/SceneN9/Dress/"],
        # **§12-5 k 게이트의 클래스 분해** — 어떤 단서가 화면을 차지하는가.
        cue_groups=dict(
            tactile=["/World/SceneN9/Tactile/"],
            fence=["/World/SceneN9/Fence/"],
            sign=["/World/SceneN9/Sign/"],
            bollard=["/World/SceneN9/Bollard_"],
            road_marking=["/World/SceneN9/Marking/"],
            ground_pattern=["/World/SceneN9/GKitWalk", "/World/SceneN9/GKitPlat",
                            "/World/SceneN9/TreeGrate_"],
            shadow_caster=["/World/SceneN9/Shadow/"],
            dressing=["/World/SceneN9/Dress/"],
        ),
    ),
    "sceneN11": dict(
        ncue=True,
        occluder=[],
        # 함정 기하 = 연속 식재대 토양면 −0.150 m (임계 0.30 미만). 낙차 아님.
        hazard=["/World/SceneN11/Bed/", "/World/SceneN11/BedFill/"],
        cue=["/World/SceneN11/GKitMall", "/World/SceneN11/Joint/",
             "/World/SceneN11/TreeGrate_", "/World/SceneN11/Tactile",
             "/World/SceneN11/Bollard_", "/World/SceneN11/Sign/",
             "/World/SceneN11/Fence/", "/World/SceneN11/Nosing/",
             "/World/SceneN11/Marking/", "/World/SceneN11/Shadow/",
             "/World/SceneN11/Dress/"],
        # L10 삼중주를 **세 성분으로 분해**한다 — 계획 §2.4 가 요구한
        #   *"한 프레임에 서로 다른 세 종류 FA"* 를 픽셀로 검증하기 위해서다.
        cue_groups=dict(
            trio_manhole_joint=["/World/SceneN11/GKitMall"],
            trio_tree_grate=["/World/SceneN11/TreeGrate_"],
            trio_exp_joint=["/World/SceneN11/Joint/"],
            tactile=["/World/SceneN11/Tactile"],
            bollard=["/World/SceneN11/Bollard_"],
            sign=["/World/SceneN11/Sign/"],
            road_marking=["/World/SceneN11/Marking/"],
            shadow_caster=["/World/SceneN11/Shadow/"],
            dressing=["/World/SceneN11/Dress/"],
        ),
    ),
}

# gridspec_v1 — 섹터·밴드 이름표. `labeler.polar_cells` 가 `cell = band*5 + sector` 로
#   싣고, 섹터 인덱스 0..4 는 A..E 이며 **A = 화면 왼쪽 = +방위각**이다.
SECTOR_NAMES = ("A", "B", "C", "D", "E")
BAND_NAMES = ("1", "2", "3a", "3b")
LATERAL_SECTORS = ("A", "E")

LABELER_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))),
    "experiments", "mainrun_0819", "code", "labeling")

HAZ_DEPTH = 0.30           # gridspec_v1 hazard_depth_m
DATUM_TOL = 0.02           # VG-datum 3층 임계 (ACCOUNTING §4.9-5)
POSE_KEYS = ("d", "h_rel", "yaw", "pitch", "roll", "hfov")

# --------------------------------------------------------------------------- #
# WHITE — v5.1 §4 "순백(>0.8) 대면적 금지" 의 **픽셀층 지표**
# --------------------------------------------------------------------------- #
# **공식 지표는 `frac(min-channel > 0.8)` 이다** [D85 채택 · REG_AUDIT §6.1].
#
#   구 지표 `frac(max-channel > 0.8)` 은 **한 채널만** 0.8 을 넘으면 센다. KS 규정색
#   황색 점자블록은 RGB ≈ (0.85, 0.79, 0.14) 이라 **정의상 항상 걸린다** — 즉 규정이
#   지시한 색을 규약 위반으로 오분류한다. sceneL1 이 정확히 그렇게 걸렸다:
#   `frac(max>0.8)` 중앙값 0.1487 인데 점자블록 픽셀 2,235,340 중 **전 채널 > 0.8 인
#   픽셀은 0개**였다(REG_AUDIT §6 픽셀 귀속 실측).
#   "순백"의 옳은 정의는 **무채색 고휘도 = 전 채널 > 0.8** 이고, 그 판정식이
#   `min-channel > 0.8` 이다. `scripts/regression_check.py` 의 `WHITE_LEVEL`(=204/255,
#   `full.min(-1)` 위에서 잰다)이 이미 같은 정의를 쓰고 있었다 — 이 스크립트가
#   코퍼스 지표를 그쪽에 맞춘 것이지 새 지표를 만든 것이 아니다.
#
# **알베도 규약으로는 못 막는다**: `paving_interlock` 은 `alb_max 0.34` 클램프
#   대상인데도 정오 직사광 + 톤매핑을 거치면 화면에서 순백으로 날아간다(sceneH7
#   `M["paving"]` 실측). ⇒ 측정·게이팅은 **알베도 층이 아니라 픽셀 층**이다.
#
# 산출층이다(판정층 아님). 사전 등록된 임계가 없으므로 `verdict` 에 들어가지 않고,
#   절대값이 아니라 **개정 전후의 이동**이 판단 재료다(regression_check 의 WHITE 와 같은 규율).
WHITE_T = 0.8              # 채널값 임계 (0..1). 204/255 = 0.8 과 같은 자리
WHITE_SKY_CUT = 3          # 하늘 배제용 상단 1/3 컷 — regression_check `[h // 3:]` 와 동일


# --------------------------------------------------------------------------- #
# 입출력 헬퍼
# --------------------------------------------------------------------------- #
def arm_dir(root, stamp, arm, split, scene):
    return os.path.join(root, f"{stamp}_{arm}", split, scene)


def load_variation(d):
    p = os.path.join(d, "variation.json")
    return json.load(open(p, encoding="utf-8")) if os.path.isfile(p) else None


def cuts_of(var):
    c = var["cuts"]
    return list(c.values()) if isinstance(c, dict) else list(c)


def blake(b, n=8):
    return hashlib.blake2b(b, digest_size=n).hexdigest()


def file_hash(p):
    return blake(open(p, "rb").read()) if os.path.isfile(p) else None


def load_hm(d):
    p = os.path.join(d, "heightmap.npy")
    m = os.path.join(d, "heightmap_meta.json")
    if not os.path.isfile(p):
        return None, None, None
    return (np.load(p), json.load(open(m, encoding="utf-8"))
            if os.path.isfile(m) else None, file_hash(p))


def load_idseg(path):
    """`.idseg.npz` → (uint 마스크, {id: prim_path})."""
    z = np.load(path, allow_pickle=True)
    arr = z["idseg"]
    lab = z["idToLabels"]
    if lab.dtype.kind in "SU" or lab.shape == ():
        lab = json.loads(str(lab.item()) if lab.shape == () else str(lab))
    else:
        lab = json.loads(lab.tobytes().decode("utf-8"))
    return arr, {int(k): v for k, v in lab.items() if str(k).lstrip("-").isdigit()}


def px_by_prefix(arr, id2p, prefixes):
    """접두어 목록에 걸리는 프림 id 들의 픽셀 수 합."""
    ids = [i for i, p in id2p.items()
           if any(str(p).startswith(pref) for pref in prefixes)]
    if not ids:
        return 0
    return int(np.isin(arr, np.asarray(ids, dtype=arr.dtype)).sum())


# --------------------------------------------------------------------------- #
# 게이트
# --------------------------------------------------------------------------- #
def gate_vg01(dA, dB, dC, ta=None, tb=None):
    """VG-01 — A/B 위험-GT 동일성. **3층 보고**(본 런이 계획에 제안하는 확장).

    계획 §6.1 의 문면은 `heightmap.npy` **바이트 동일**이다. 그러나 이 판정은 실행 불가능한
    상한이다 — 높이맵은 **수직 레이의 최초 히트**이므로, 격자 안에 서는 단서 프림이
    하나라도 있으면(맨홀 7.7 mm · 줄눈 3 mm 은 물론이고 **갈대 군락 1.35 m · 가로수**까지)
    B팔에서 그 셀의 z 는 지면으로 되돌아간다. 실측 [260823_v3p5_h12probe]: sceneH1 의
    A↔B 는 4,144셀 · max |Δz| **1.42 m** 로 다르다 — 전부 갈대 군락(x −2.42…−1.70)이고
    **낙차 발자국 밖**이다.

    게이트의 목적은 *위험 GT 동일성*이지 *높이맵 동일성*이 아니다. VG-datum 이 이미 채택한
    3층 보고를 같은 논리로 적용하되, **결정층은 "발자국 안"** 으로 잡는다:
        hm_exact       — 바이트 동일
        hm_tol_offprint — 다른 셀이 있으나 **전부 낙차 발자국 밖** → polar_gt 불변
        hm_fail        — 발자국 **안**에서 z 가 움직였다 → 그 키는 구조물(토글 금지)
    발자국은 A↔C 트윈에서 정의한다(`z_C − z_A ≥ hazard_depth`).

    **3차 빌더 런의 정정 — 4층으로 늘린다.** sceneH3 R0 실측에서 `hm_fail`(발자국 안
    611/5122 셀 · max |Δz| 1.259 m)이 나왔는데, 범인은 구조물이 아니라 **낙차 위에 떠 있는
    벽면 계단 손잡이**였다. 손잡이는 A팔에 있고 B팔에서 사라지므로 그 셀의 높이맵 z 가
    "손잡이 상단 → 계단 상면"으로 내려간다. 그러나 **그 셀은 여전히 발자국이다** —
    낙차가 0.3 m 아래로 사라지는 것이 아니라 그 위에 있던 얇은 관이 없어질 뿐이다.
    실측이 그것을 증명한다 `[260823_v3p5_h3l1probe · sceneH3]`:
        **`polar_gt` 가 16프레임 전부 A↔B 비트 동일** · tier 분포도 동일(H 12 · none_in_fov 4)
        발자국 `cells_kept` A 5120–5121 / B 5130 (0.2 % 차)
        `max_diff` A **2.363 m** vs B **1.800 m**(= 10단 × 0.18, 진짜 낙차)
    모델이 배우는 GT 는 20칸 `polar_gt` 이지 원시 높이맵이 아니므로, **결정층은 `polar_gt`**
    여야 한다. 셀 z 가 움직였으나 `polar_gt` 가 전 프레임 동일한 경우를 `hm_gt_equal` 로
    분리한다 — 이것은 SCENE_TEXT_BUILD §9 가 확정한 네 결함과 **같은 구조**의 다섯 번째
    사례다(*게이트를 어느 양에 대해 세는가*).
    """
    zA, mA, hA = load_hm(dA)
    zB, mB, hB = load_hm(dB)
    zC, _, _ = load_hm(dC)
    if zA is None or zB is None:
        return dict(ok=False, note="heightmap 없음")
    same_bytes = (hA == hB)
    fin = np.isfinite(zA) & np.isfinite(zB)
    diff = np.where(fin, np.abs(zA - zB), 0.0)
    n_diff = int((diff > 0).sum())
    dmax = float(diff.max()) if diff.size else 0.0
    void_same = bool((~np.isfinite(zA) == ~np.isfinite(zB)).all())
    if zC is not None:
        f3 = fin & np.isfinite(zC)
        fp = f3 & ((zC - zA) >= HAZ_DEPTH)
    else:
        fp = np.zeros_like(diff, dtype=bool)
    n_fp = int(fp.sum())
    n_diff_fp = int(((diff > 0) & fp).sum())
    dmax_fp = float(diff[fp].max()) if n_fp else 0.0
    # ── 4층 판정: `polar_gt` 동일성이 결정층이다 ────────────────────────────
    gt_n = gt_same = None
    if ta and tb:
        common = sorted(set(ta) & set(tb))
        gt_n = len(common)
        gt_same = sum(1 for f in common
                      if ta[f].get("polar_gt") == tb[f].get("polar_gt"))
    gt_equal = (gt_n is not None and gt_n > 0 and gt_same == gt_n)
    tier = ("hm_exact" if same_bytes else
            "hm_tol_offprint" if n_diff_fp == 0 else
            "hm_gt_equal" if gt_equal else "hm_fail")
    return dict(ok=(tier != "hm_fail") and void_same, tier=tier,
                bytes_equal=bool(same_bytes), n_cells_diff=n_diff,
                max_abs_dz=round(dmax, 6),
                n_footprint_cells=n_fp, n_cells_diff_in_footprint=n_diff_fp,
                max_abs_dz_in_footprint=round(dmax_fp, 6),
                polar_gt_frames=gt_n, polar_gt_equal_frames=gt_same,
                void_mask_equal=void_same,
                meta_equal=bool(mA == mB), hash_A=hA, hash_B=hB)


def gate_vg02(dA, dC, dD):
    """VG-02 — C/D 전 칸 음성. 라벨러를 거치지 않고 **높이맵으로 직접** 반증한다.

    (i) **낙차 발자국 영역 안에서** C↔D 가 같을 것 — 두 팔 모두 그 영역이 반사실 채움면이다.
        발자국 **밖**의 C↔D 차이는 위험이 아니라 **장식**이다(C = keep_dressing 유지 팔,
        D = 전 단서 제거 팔). 실측 [260823_v3p5_h12probe] sceneH1: 갈대 군락이 격자 안에
        서므로 무제한 비교는 4천 셀·1.42 m 를 낸다 — 그것을 위험으로 읽으면 오판이다.
    (ii) A 대비 **C 가 더 낮은** 칸이 없을 것 (C 에만 있는 잔존 위험 = 제작 실패).
         A·C 는 둘 다 장식을 갖는 팔이라 이 비교는 장식에 오염되지 않는다.
    (iii) 참고로 A↔C 발자국 규모를 인쇄 — 이것이 실제 GT 다.

    **3차 빌더 런의 정정 — C↔D 비교는 부호를 가려야 한다.** sceneH3 R0 에서 발자국 안
    C↔D 가 **126셀** 나왔는데, C 는 `keep_dressing` 팔이라 **D 보다 프림이 많다**.
    126셀 전부 `z_C − z_D ≥ 0.30`, 즉 **C 가 더 높은** 셀이었다 — 낙차 위 0.90 m 에 떠 있는
    벽면 손잡이다. *"위로 솟은 부재"는 낙차가 아니다.* 절대값 비교(`|z_C − z_D|`)는 그
    구분을 못 한다. ⇒ 판정층을 **`z_D − z_C ≥ depth`(C 에 구멍이 있다)** 하나로 좁히고,
    반대 부호는 `cells_C_above_D`(= 보존된 장식·단서)로 따로 인쇄한다. C ≥ D 는
    `keep_dressing` 의 정의상 항상 참이어야 하므로 `cells_C_below_D > 0` 이야말로
    진짜 이상이다.
    """
    zA, _, _ = load_hm(dA)
    zC, _, _ = load_hm(dC)
    zD, _, _ = load_hm(dD)
    if zA is None or zC is None or zD is None:
        return dict(ok=False, note="heightmap 없음")
    f = np.isfinite(zA) & np.isfinite(zC) & np.isfinite(zD)
    fp = f & ((zC - zA) >= HAZ_DEPTH)
    cd_all = int((f & (np.abs(zC - zD) >= HAZ_DEPTH)).sum())
    cd_fp = int((fp & (np.abs(zC - zD) >= HAZ_DEPTH)).sum())
    # 부호 분해 — `below` 만이 "C 에 구멍" 이고 `above` 는 보존된 장식·단서다.
    cd_fp_below = int((fp & ((zD - zC) >= HAZ_DEPTH)).sum())
    cd_fp_above = int((fp & ((zC - zD) >= HAZ_DEPTH)).sum())
    resid = int((f & ((zA - zC) >= HAZ_DEPTH)).sum())
    return dict(ok=(cd_fp_below == 0 and resid == 0),
                cells_C_below_D_in_footprint=cd_fp_below,
                cells_C_above_D_in_footprint=cd_fp_above,
                cells_C_vs_D_in_footprint=cd_fp, cells_C_vs_D_all=cd_all,
                cells_resid_hazard_in_C=resid, cells_footprint_A=int(fp.sum()))


def gate_datum_pose(var_by_arm):
    """VG-datum(3층) + VG-10(포즈 6키) — 전 팔을 A팔 기준으로 본다."""
    out = {}
    base = {c["file"]: c for c in cuts_of(var_by_arm["A"])}
    for arm in ARMS[1:]:
        if arm not in var_by_arm:
            continue
        cur = {c["file"]: c for c in cuts_of(var_by_arm[arm])}
        ex = tol = fail = 0
        worst = 0.0
        pose_bad = []
        for f, c in base.items():
            if f not in cur:
                continue
            dz = abs(c["cam"]["ground_z"] - cur[f]["cam"]["ground_z"])
            worst = max(worst, dz)
            if dz < 1e-6:
                ex += 1
            elif dz <= DATUM_TOL:
                tol += 1
            else:
                fail += 1
            for k in POSE_KEYS:
                if abs(c["cam"][k] - cur[f]["cam"][k]) > 1e-6:
                    pose_bad.append((f, k))
        n = ex + tol + fail
        out[arm] = dict(n_pairs=n, datum_exact=ex, datum_tol=tol,
                        datum_fail=fail,
                        survival=round((ex + tol) / n, 4) if n else 0.0,
                        max_abs_dz=round(worst, 6),
                        pose_mismatch=len(pose_bad),
                        pose_examples=pose_bad[:3],
                        ok=(fail == 0 and not pose_bad and n > 0))
    return out


def gate_vg08(d, var):
    """VG-08 — 세그 사이드카 존재 + **컷별 마스크가 실제로 다른가**.

    현행 정의(`.idseg.npz` 존재 + `idseg_fetch ≠ "empty"`)는 SCENE_H67_BUILD §7 의
    stale-frame 결함을 통과시킨다. §7.6 권고 4 를 여기서 이행한다.
    """
    cuts = cuts_of(var)
    files = [os.path.join(d, os.path.splitext(c["file"])[0] + ".idseg.npz")
             for c in cuts]
    have = [p for p in files if os.path.isfile(p)]
    hashes = {file_hash(p) for p in have}
    nids = sorted({c.get("idseg_n_ids") for c in cuts if c.get("idseg_n_ids")})
    fetch = sorted({c.get("idseg_fetch") for c in cuts})
    # **기준은 컷 수가 아니라 서로 다른 카메라 포즈 수다.** 이 라운드는 조건 2종(L0·L5)을
    #   같은 시드·같은 카메라 인덱스로 찍으므로 포즈가 조건 간 **동일**하고, ID 마스크는
    #   조명에 의존하지 않는다 ⇒ 8컷 · 4포즈면 고유 해시 4개가 **정상**이다.
    #   컷 수로 비교하면 정상 라운드를 stale 로 오판한다(설계 시 실측).
    poses = {tuple(round(c["cam"][k], 9) for k in POSE_KEYS) for c in cuts}
    fresh = (len(hashes) == len(poses)) and len(have) > 0
    return dict(ok=(len(have) == len(cuts) and fresh),
                n_cuts=len(cuts), n_idseg=len(have), n_poses=len(poses),
                n_distinct_hashes=len(hashes), fetch=fetch,
                n_ids_distinct=len(nids), per_cut_fresh=fresh)


def gate_vg_void(d):
    m = os.path.join(d, "heightmap_meta.json")
    if not os.path.isfile(m):
        return dict(ok=False, note="meta 없음")
    j = json.load(open(m, encoding="utf-8"))
    cov = j["n_finite"] / j["n_total"]
    return dict(ok=(cov >= 1.0), coverage=round(cov, 6),
                n_finite=j["n_finite"], n_total=j["n_total"],
                z_min=j.get("z_min"), z_max=j.get("z_max"))


def _grid_mask(d, fn, var_cuts):
    """그 컷의 깊이맵을 역투영해 **높이맵 격자 안**에 떨어지는 픽셀 마스크를 만든다.

    왜 필요한가 — 계획 §6.1 의 VG-06 은 *"**낙차 림·내부** 기여 0 px"* 이고, "낙차 림·내부"는
    **라벨이 다루는 영역**(높이맵 격자 x ∈ [−2,14] · |y| ≤ 8) 안의 낙차다. 그런데 낙차 프림은
    격자 밖까지 이어진다 — sceneH1 의 수면은 x = 26 까지 간다. 림 조건이 실효 구속인
    프레임에서는 마루를 스치는 시선이 격자 **밖**(x ≳ 19)에서 수면 아래로 내려가므로
    **격자 밖 수면이 보인다**. 그것은 strict-H 를 깨지 않는데(`int_px` 는 발자국 셀만 센다)
    ID 마스크 전수 집계로는 "낙차 구조물 가시"로 잡힌다 [실측 260823_v3p5_h12probe_A
    sceneH1: H 6프레임 중 2프레임]. ⇒ VG-06 도 라벨과 **같은 영역**에서 세야 한다.
    """
    dep_p = os.path.join(d, os.path.splitext(fn)[0] + ".depth.npy")
    cut = next((c for c in var_cuts if c["file"] == fn), None)
    if cut is None or not os.path.isfile(dep_p):
        return None
    try:
        sys.path.insert(0, LABELER_DIR)
        import labeler as lb
    except Exception:
        return None
    dep = np.load(dep_p).astype(np.float64)
    eye = np.asarray(cut["cam"]["eye"], dtype=np.float64)
    P, good = lb.unproject(dep, eye, cut["cam"], 1)
    g = lb.HM_DEFAULT
    x1 = g["x0"] + 321 * g["step"]
    y1 = g["y0"] + 321 * g["step"]
    return (good & (P[..., 0] >= g["x0"]) & (P[..., 0] <= x1)
            & (P[..., 1] >= g["y0"]) & (P[..., 1] <= y1))


def gate_vg06(d, scene, h_files, var_cuts=()):
    """VG-06 — A팔 strict-H 프레임 각각에서 모서리 소속을 ID 마스크로 검사.

    판정층은 **격자 안 낙차 구조물 0 px**이며, 격자 무제한 집계도 함께 인쇄한다.
    """
    cfg = PRIMS[scene]
    rows = []
    for fn in h_files:
        p = os.path.join(d, os.path.splitext(fn)[0] + ".idseg.npz")
        if not os.path.isfile(p):
            rows.append(dict(file=fn, note="idseg 없음"))
            continue
        arr, id2p = load_idseg(p)
        gm = _grid_mask(d, fn, var_cuts)
        haz_all = px_by_prefix(arr, id2p, cfg["hazard"])
        if gm is not None and gm.shape == arr.shape:
            hid = [i for i, pp in id2p.items()
                   if any(str(pp).startswith(x) for x in cfg["hazard"])]
            haz_grid = (int(np.isin(arr, np.asarray(hid, dtype=arr.dtype)).astype(bool)
                            .__and__(gm).sum()) if hid else 0)
        else:
            haz_grid = haz_all
        rows.append(dict(file=fn,
                         occluder_px=px_by_prefix(arr, id2p, cfg["occluder"]),
                         hazard_px_in_grid=haz_grid, hazard_px_all=haz_all,
                         cue_px=px_by_prefix(arr, id2p, cfg["cue"]),
                         context_px=px_by_prefix(arr, id2p,
                                                 cfg.get("context") or []),
                         n_ids=int(len(np.unique(arr)))))
    good = [r for r in rows if "occluder_px" in r]
    # **측방 씬은 은닉 씬이 아니다.** 계획 §2.3 은 sceneL1 에 가림체를 요구하지 않고
    #   낙차가 보이는 것이 정상이다 — 그 씬에 "가림체 px > 0 · 낙차 px = 0" 을 걸면
    #   정상 씬을 실패로 읽는다(SCENE_TEXT_BUILD §9 가 확정한 결함 4건과 같은 구조:
    #   *게이트를 어디에서 어떤 씬에 대해 세는가*). `lateral=True` 면 측정만 하고
    #   판정은 `gate_sectors` 로 넘긴다.
    if cfg.get("lateral") or cfg.get("ncue"):
        # **N-cue 씬에는 가림체도 낙차 구조물도 없다.** "가림체 px > 0 · 낙차 px = 0"
        #   을 걸면 정상 씬을 실패로 읽는다(SCENE_TEXT_BUILD §9 가 확정한 결함 4건과
        #   같은 구조). 측정만 하고 판정은 `gate_allneg` · `gate_cue_px` 로 넘긴다.
        ok = bool(good)
    else:
        ok = bool(good) and all(r["occluder_px"] > 0 and r["hazard_px_in_grid"] == 0
                                for r in good)
    return dict(ok=ok, lateral=bool(cfg.get("lateral")),
                ncue=bool(cfg.get("ncue")), n_frames=len(rows),
                n_occluder_pos=sum(1 for r in good if r["occluder_px"] > 0),
                n_hazard_pos=sum(1 for r in good if r["hazard_px_in_grid"] > 0),
                n_hazard_pos_all=sum(1 for r in good if r["hazard_px_all"] > 0),
                cue_px_min=min([r["cue_px"] for r in good], default=None),
                cue_px_max=max([r["cue_px"] for r in good], default=None),
                context_px_max=max([r["context_px"] for r in good], default=0),
                frames=rows)


def gate_sectors(tiers, var_cuts):
    """**측방 씬 전용 게이트** — 라벨 `polar_gt` 의 **섹터 분포**를 잰다.

    계획 §2.3 이 sceneL1 을 세우게 한 이유가 이 표다: *"현 test 에 측방 씬이 0개라
    섹터 분해능(5→10)·밴드 세분을 '실용 정보량' 기준으로 재론할 측정 기반이 원리적으로
    없다"* `[승용 결재 1 룰링]`. 그 측정 기반이란 **위험 질량이 실제로 어느 섹터에
    실리는가**의 실측 분포이고, 이 함수가 그것을 라벨에서 직접 읽는다.

    `polar_gt` 는 20원소(4밴드 × 5섹터, `cell = band*5 + sector`)의 0/1 벡터다.
    두 층으로 집계한다 —
      pos_rate[s]    프레임 수준: 그 섹터의 셀이 **하나라도** 양성인 프레임 비율
      cell_share[s]  셀 수준: 양성 셀 총수 중 그 섹터의 몫
    그리고 밴드×섹터 20칸 표를 그대로 인쇄한다(밴드 세분 재론의 입력).

    판정 기준(사전 등록):
      (a) 측방 A·E 의 셀 점유율 합이 B·D 합보다 클 것        ← "위험 질량이 A·E 에 집중"
      (b) A 와 E 가 **둘 다** 프레임 양성률 ≥ 0.50 일 것      ← 양측 개거를 세운 이유
      (c) 격자 밖(`none_in_fov`) 프레임 비율이 0.10 이하일 것 ← 밴드가 격자를 벗어나지 않음
    """
    n = 0
    pos = {s: 0 for s in SECTOR_NAMES}
    cells = {s: 0 for s in SECTOR_NAMES}
    grid = [[0] * 5 for _ in range(4)]
    n_cells_tot = 0
    n_none = 0
    per_frame = []
    for fn, v in sorted(tiers.items()):
        gt = v.get("polar_gt")
        if not gt:
            continue
        n += 1
        if v.get("tier_strict") == "none_in_fov":
            n_none += 1
        seen = set()
        k = 0
        for b in range(4):
            for s in range(5):
                if gt[b * 5 + s]:
                    grid[b][s] += 1
                    cells[SECTOR_NAMES[s]] += 1
                    n_cells_tot += 1
                    seen.add(SECTOR_NAMES[s])
                    k += 1
        for s in seen:
            pos[s] += 1
        cam = next((c["cam"] for c in var_cuts if c["file"] == fn), None)
        per_frame.append(dict(
            file=fn, tier=v.get("tier_strict"), n_cells=k,
            sectors="".join(sorted(seen)),
            d=round(cam["d"], 3) if cam else None,
            h=round(cam["h_rel"], 3) if cam else None,
            yaw=round(cam["yaw"], 3) if cam else None))
    if not n:
        return dict(ok=False, note="polar_gt 없음")
    pr = {s: round(pos[s] / n, 4) for s in SECTOR_NAMES}
    cs = {s: round(cells[s] / n_cells_tot, 4) if n_cells_tot else 0.0
          for s in SECTOR_NAMES}
    lat = cs["A"] + cs["E"]
    mid = cs["B"] + cs["D"]
    ok = (lat > mid
          and min(pr["A"], pr["E"]) >= 0.50
          and (n_none / n) <= 0.10)
    return dict(ok=ok, n_frames=n, n_cells_total=n_cells_tot,
                cells_per_frame=round(n_cells_tot / n, 3),
                pos_rate=pr, cell_share=cs,
                lateral_share=round(lat, 4), mid_share=round(mid, 4),
                center_share=cs["C"],
                none_in_fov=round(n_none / n, 4),
                band_sector=dict(bands=list(BAND_NAMES),
                                 sectors=list(SECTOR_NAMES), counts=grid),
                frames=per_frame)


def gate_allneg(tiers, arm_tag, cells_raw_src=None):
    """**N-cue 판정층 (a)** — 그 팔의 전 프레임 GT 가 정말 올-음성인가.

    계획 §1.0 이 등록한 사실 판정 규칙: *"위험 있음 = 교정 GT 폴라 그리드에 **양성 칸
    ≥ 1**"*. N-cue 씬은 그 반대를 주장하므로, 주장의 반증 가능한 형태는 **네 층**이다:

      L1 `polar_gt`          전 20칸 0 (훈련 GT)
      L2 `polar_gt_pregate`  전 20칸 0 (**스텝 게이트 이전**의 GT)
      L3 `tier_strict`       `none_in_fov` (게이트 후 사유 — VG-14 가 분리를 요구한 그 값)
      L4 **`cells_raw`**     발자국 원시 셀 수 = 0 (**카메라 무관량**)

    **L4 가 결정적이다.** SCENE_TEXT_BUILD §12-9.3 이 확정한 D78 계기 결함(라벨러
    `step_gate` 의 `_outward` 8이웃 양자화가 **축방향 측방 위험**을 `d ≤ −x₀ + √3·y_lip`
    밖에서 못 본다)은 `cells_kept` 를 0 으로 만든다. 즉 `cells_kept = 0` 만 보고
    "음성"이라고 하면 **사각과 진짜 음성이 구별되지 않는다**. `cells_raw` 는 카메라가
    등장하기 전에 계산되는 양(`hm_off − hm_on ≥ 0.30` 셀 수)이므로 사각의 영향을 받지
    않는다. N-cue 씬의 두 함정(N9 연석 0.200 m · N11 식재대 0.150 m)은 둘 다 보행축과
    **나란한** 축방향 선이라 정확히 그 사각의 대상이고, 그래서 이 구분이 필수다.

    또한 `max_diff`(발자국 후보의 최대 표고차)를 인쇄한다 — **"재 봤더니 임계 미만"**
    이라는 기계 증거이며, 함정 깊이의 실측치다.
    """
    rows, tiers_ct = [], collections.Counter()
    n_gt_pos = n_pre_pos = 0
    cells_raw = set()
    max_diff = []
    for fn, v in sorted(tiers.items()):
        gt = v.get("polar_gt") or []
        pre = v.get("polar_gt_pregate") or []
        t = v.get("tier_strict")
        fp = v.get("footprint") or {}
        tiers_ct[t] += 1
        if any(gt):
            n_gt_pos += 1
        if any(pre):
            n_pre_pos += 1
        if fp.get("cells_raw") is not None:
            cells_raw.add(int(fp["cells_raw"]))
        if fp.get("max_diff") is not None:
            max_diff.append(float(fp["max_diff"]))
        rows.append(dict(file=fn, tier=t, n_gt=int(sum(gt)),
                         n_gt_pregate=int(sum(pre)),
                         cells_raw=fp.get("cells_raw"),
                         cells_kept=fp.get("cells_kept"),
                         max_diff=fp.get("max_diff")))
    n = len(rows)
    md = dict(min=round(min(max_diff), 4), max=round(max(max_diff), 4)) if max_diff else None
    ok = (n > 0 and n_gt_pos == 0 and n_pre_pos == 0
          and cells_raw == {0}
          and (md is None or md["max"] < HAZ_DEPTH))
    return dict(ok=ok, arm=arm_tag, n_frames=n,
                n_frames_gt_positive=n_gt_pos,
                n_frames_pregate_positive=n_pre_pos,
                cells_raw=sorted(cells_raw), max_diff=md,
                tiers=dict(tiers_ct),
                all_none_in_fov=(set(tiers_ct) == {"none_in_fov"}),
                frames=rows[:64])


def gate_grid_depth(d, walk_z=0.0):
    """**N-cue 판정층 (a) 보강** — 팔별 **높이맵 직접** 최저점 회계.

    라벨러의 판정은 (on, off) **쌍**에 의존한다. 그러나 ④-a 함정의 주장 —
    *"이 씬의 격자 안 어디에도 0.30 m 이상의 하강이 없다"* — 은 **팔 하나만으로도**
    반증 가능해야 한다. 그래서 `heightmap.npy` 를 직접 읽어 보행면(`walk_z`) 대비
    최저 셀 깊이를 잰다. 네 팔 전부에서 `depth < 0.30` 이면, 어떤 쌍짓기를 하든
    발자국이 생길 수 없다.

    `n_below` 는 임계 이상 내려간 셀 수 — 0 이어야 한다.
    """
    z, meta, _h = load_hm(d)
    if z is None:
        return dict(ok=False, note="heightmap 없음")
    fin = np.isfinite(z)
    if not fin.any():
        return dict(ok=False, note="유한 셀 0")
    zmin = float(z[fin].min())
    depth = walk_z - zmin
    n_below = int((fin & (walk_z - z >= HAZ_DEPTH)).sum())
    # 보행면 자체도 실측으로 확인한다 — 최빈 z(0.01 m 빈)가 walk_z 와 같아야 한다.
    q = np.round(z[fin] / 0.01).astype(np.int64)
    vals, cnt = np.unique(q, return_counts=True)
    mode_z = float(vals[int(cnt.argmax())] * 0.01)
    return dict(ok=(n_below == 0 and depth < HAZ_DEPTH),
                z_min=round(zmin, 4), z_max=round(float(z[fin].max()), 4),
                walk_z=walk_z, depth_below_walk=round(depth, 4),
                margin_to_threshold=round(HAZ_DEPTH - depth, 4),
                n_cells_below_threshold=n_below,
                mode_z=round(mode_z, 4),
                coverage=round(float(fin.mean()), 6))


def gate_cue_px(d, scene, var, grid_only=True):
    """**N-cue 판정층 (b)** — strict 세그 마스크의 **단서 클래스별 픽셀 분포**.

    계획 §1.0: *"단서 있음 = **ID 마스크의 cue 프림 픽셀 ≥ k**(k 는 VG-11 로 사전 고정)"*.
    이 함수는 **k 를 정하지 않는다** — k 고정은 VG-11 의 소관이고 결과를 본 뒤 움직이면
    무효다(ACCOUNTING §3.4-1). 여기서 하는 일은 그 판정이 소비할 **분포를 산출**하는 것뿐이며,
    그래서 임계 판정 없이 분위수와 클래스 분해를 인쇄한다.

    `grid_only=True` 면 **높이맵 격자 안**의 픽셀만 센다(VG-06 이 §9.4 에서 확정한 것과
    같은 규율: *게이트는 라벨이 다루는 영역에서 세야 한다*). 격자 무제한 값도 병기한다.
    """
    cfg = PRIMS[scene]
    groups = cfg.get("cue_groups") or dict(cue=cfg["cue"])
    cuts = cuts_of(var)
    rows = []
    for c in cuts:
        fn = c["file"]
        p = os.path.join(d, os.path.splitext(fn)[0] + ".idseg.npz")
        if not os.path.isfile(p):
            continue
        arr, id2p = load_idseg(p)
        gm = _grid_mask(d, fn, cuts) if grid_only else None
        row = dict(file=fn, d=round(c["cam"]["d"], 3),
                   h=round(c["cam"]["h_rel"], 3), total_px=int(arr.size))
        tot_all = tot_grid = 0
        for g, prefs in sorted(groups.items()):
            ids = [i for i, pp in id2p.items()
                   if any(str(pp).startswith(x) for x in prefs)]
            if not ids:
                row[g] = 0
                row[g + "_grid"] = 0
                continue
            m = np.isin(arr, np.asarray(ids, dtype=arr.dtype))
            n_all = int(m.sum())
            n_grid = int((m & gm).sum()) if (gm is not None and gm.shape == arr.shape) else n_all
            row[g] = n_all
            row[g + "_grid"] = n_grid
            tot_all += n_all
            tot_grid += n_grid
        row["cue_total"] = tot_all
        row["cue_total_grid"] = tot_grid
        row["cue_frac"] = round(tot_all / arr.size, 6)
        rows.append(row)
    if not rows:
        return dict(ok=False, note="idseg 없음")

    def q(vals):
        a = np.asarray(sorted(vals), dtype=np.float64)
        return dict(min=int(a.min()), p25=int(np.percentile(a, 25)),
                    p50=int(np.percentile(a, 50)), p75=int(np.percentile(a, 75)),
                    max=int(a.max()), mean=round(float(a.mean()), 1))
    per_group = {g: q([r[g] for r in rows]) for g in sorted(groups)}
    per_group_grid = {g: q([r[g + "_grid"] for r in rows]) for g in sorted(groups)}
    n_present = {g: int(sum(1 for r in rows if r[g] > 0)) for g in sorted(groups)}
    n_present_grid = {g: int(sum(1 for r in rows if r[g + "_grid"] > 0))
                      for g in sorted(groups)}
    tot = q([r["cue_total"] for r in rows])
    tot_g = q([r["cue_total_grid"] for r in rows])
    return dict(ok=True, n_frames=len(rows), n_groups=len(groups),
                cue_total=tot, cue_total_grid=tot_g,
                cue_frac_p50=round(float(np.median([r["cue_frac"] for r in rows])), 6),
                per_group=per_group, per_group_grid=per_group_grid,
                n_frames_with_group=n_present,
                n_frames_with_group_in_grid=n_present_grid,
                frames=rows[:64])


def gate_vg07(dA, dC, files):
    """VG-07 — 쌍별 (A,C) 광학차 로그.

    계획 §6.1: *"쌍마다 광학 변화량 기록. ≈0 쌍은 '정보량 0' 으로 층화하고 무벌점"*.
    D58 의 **영정보 층화**가 이 분포를 입력으로 받는다. 통계 3종을 낸다:
      mean_abs   — 그레이스케일 |ΔI| 평균 (0–255)
      frac_gt8   — |ΔI| > 8 인 픽셀 비율 (양자화·디노이즈 잡음 위)
      frac_gt32  — |ΔI| > 32 인 픽셀 비율 (구조적 변화)
    """
    try:
        from PIL import Image
    except Exception as e:                      # pragma: no cover
        return dict(ok=False, note=f"PIL 없음: {e}")
    rows = []
    for fn in files:
        pa, pc = os.path.join(dA, fn), os.path.join(dC, fn)
        if not (os.path.isfile(pa) and os.path.isfile(pc)):
            continue
        a = np.asarray(Image.open(pa).convert("L"), dtype=np.int16)
        c = np.asarray(Image.open(pc).convert("L"), dtype=np.int16)
        if a.shape != c.shape:
            continue
        dd = np.abs(a - c)
        rows.append(dict(file=fn, mean_abs=round(float(dd.mean()), 4),
                         frac_gt8=round(float((dd > 8).mean()), 6),
                         frac_gt32=round(float((dd > 32).mean()), 6)))
    if not rows:
        return dict(ok=False, note="쌍 없음")
    ma = np.array([r["mean_abs"] for r in rows])
    f8 = np.array([r["frac_gt8"] for r in rows])
    return dict(ok=True, n_pairs=len(rows),
                mean_abs=dict(min=round(float(ma.min()), 4),
                              p50=round(float(np.median(ma)), 4),
                              max=round(float(ma.max()), 4),
                              mean=round(float(ma.mean()), 4)),
                frac_gt8=dict(min=round(float(f8.min()), 6),
                              p50=round(float(np.median(f8)), 6),
                              max=round(float(f8.max()), 6)),
                # "정보량 0" 층 = 화면이 사실상 안 변한 쌍 (frac_gt8 < 0.001)
                n_zero_info=int((f8 < 0.001).sum()),
                pairs=rows)


def gate_white(d, files):
    """WHITE — 순백 대면적 지표 (v5.1 §4 · D85 채택).

    **공식**  `white`      = frac(min-channel > 0.8)  — 전 프레임
              `white_gnd`  = 같은 식을 **하단 2/3** 에서 (하늘 배제. regression_check
                             `WHITE_LEVEL` 과 정의·측정면이 모두 같다)
    **폐기예정** `white_max_deprecated` = frac(max-channel > 0.8)
              — 포화 황색(KS 규정색 점자블록)을 순백으로 오분류한다. **마지막으로
                한 번 더 인쇄**하고 다음 개정에서 뺀다(REG_AUDIT §6.1 · 부록 A).

    프레임별로 재고 씬 단위로 min / p50 / max 를 낸다. 판정층이 아니라 산출층이다.
    """
    try:
        from PIL import Image
    except Exception as e:                      # pragma: no cover
        return dict(ok=False, note=f"PIL 없음: {e}")
    rows = []
    for fn in files:
        p = os.path.join(d, fn)
        if not os.path.isfile(p):
            continue
        a = np.asarray(Image.open(p).convert("RGB"), dtype=np.float32) / 255.0
        h = a.shape[0]
        mn, mx = a.min(-1), a.max(-1)
        rows.append(dict(
            file=fn,
            white=round(float((mn > WHITE_T).mean()), 6),
            white_gnd=round(float((mn[h // WHITE_SKY_CUT:] > WHITE_T).mean()), 6),
            white_max_deprecated=round(float((mx > WHITE_T).mean()), 6),
            mean=round(float(255.0 * a.mean()), 2),
        ))
    if not rows:
        return dict(ok=False, note="프레임 없음")

    def q(key):
        v = np.array([r[key] for r in rows], dtype=np.float64)
        return dict(min=round(float(v.min()), 6),
                    p50=round(float(np.median(v)), 6),
                    max=round(float(v.max()), 6))

    return dict(ok=True, n_frames=len(rows), metric="frac(min-channel > 0.8)",
                threshold=WHITE_T,
                white=q("white"), white_gnd=q("white_gnd"),
                white_max_deprecated=q("white_max_deprecated"),
                mean=q("mean"), frames=rows[:64])


# --------------------------------------------------------------------------- #
def load_tiers(labels_path, arm_tag="on"):
    """labeler 산출 JSON → {scene: {file: tier}}."""
    if not labels_path or not os.path.isfile(labels_path):
        return {}
    L = json.load(open(labels_path, encoding="utf-8"))
    out = collections.defaultdict(dict)
    for k, v in L["frames"].items():
        arm, scene, fn = k.split("/", 2)
        if arm != arm_tag:
            continue
        out[scene][fn] = v
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="dataset")
    ap.add_argument("--stamp", default="260823_v3p5_h12probe")
    ap.add_argument("--split", default="test")
    ap.add_argument("--scenes", default="sceneH1,sceneH2")
    ap.add_argument("--labels-ac", default="")
    ap.add_argument("--labels-bd", default="")
    # ── N-cue 전용 (④-a 함정 표본) — **역쌍 라벨** ────────────────────────────
    #   (C,A) 와 (D,B). 두 팔의 GT 는 정의상 음성이지만(계획 §1.0), N-cue 씬에서는
    #   "네 팔 전부 올-음성"이 **판정층**이므로 C·D 팔도 프레임 단위 `polar_gt` 행을
    #   가져야 한다. 역쌍(`on = C`, `off = A`)을 돌리면 `z_A − z_C ≥ 0.30` 셀 수를
    #   세게 되는데, 그것은 *"C 팔에 A 팔보다 0.30 m 낮은 칸이 있는가"* = VG-02 (ii)
    #   와 같은 질문이고, 함정 씬에서는 부호가 반대라 항상 0 이어야 한다.
    ap.add_argument("--labels-ca", default="")
    ap.add_argument("--labels-db", default="")
    ap.add_argument("--walk-z", type=float, default=0.0,
                    help="N-cue 최저점 회계의 보행면 기준 z (기본 0.0)")
    ap.add_argument("--out", default="")
    # WHITE 지표만 낸다. 라벨도 B·D 팔도 필요 없으므로 h67 계열(A·C 2팔, split=val)
    #   라운드에도 그대로 쓸 수 있다 — 지표 구현을 한 곳에만 둔다.
    ap.add_argument("--white-only", action="store_true")
    a = ap.parse_args(argv)

    if a.white_only:
        rep = dict(stamp=a.stamp, split=a.split, metric="frac(min-channel > 0.8)",
                   scenes={})
        for scene in [s for s in a.scenes.split(",") if s]:
            dA = arm_dir(a.root, a.stamp, "A", a.split, scene)
            var = load_variation(dA)
            if not var:
                print(f"[{scene}] A팔 없음 ({dA}) — 건너뜀")
                continue
            g = gate_white(dA, sorted({c["file"] for c in cuts_of(var)}))
            rep["scenes"][scene] = g
            if not g.get("ok"):
                print(f"[{scene}] WHITE — {g.get('note')}")
                continue
            w, wg, dep = g["white"], g["white_gnd"], g["white_max_deprecated"]
            print(f"[{scene}] {a.stamp}_A/{a.split} · n={g['n_frames']}")
            print(f"  **공식 frac(min>0.8)** p50 {w['p50']:.4f} · "
                  f"min {w['min']:.4f} · max {w['max']:.4f}")
            print(f"  하단2/3(하늘 배제)     p50 {wg['p50']:.4f} · "
                  f"max {wg['max']:.4f}")
            print(f"  [deprecated] frac(max>0.8) p50 {dep['p50']:.4f} · "
                  f"max {dep['max']:.4f}")
            print(f"  mean p50 {g['mean']['p50']}")
        if a.out:
            os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
            json.dump(rep, open(a.out, "w", encoding="utf-8"),
                      ensure_ascii=False, indent=1)
            print(f"\n[out] {a.out}")
        return 0

    tiers_a = load_tiers(a.labels_ac, "on")
    tiers_b = load_tiers(a.labels_bd, "on")
    tiers_c = load_tiers(a.labels_ca, "on")
    tiers_d = load_tiers(a.labels_db, "on")

    report = dict(stamp=a.stamp, split=a.split, scenes={})
    all_ok = True
    for scene in [s for s in a.scenes.split(",") if s]:
        d = {arm: arm_dir(a.root, a.stamp, arm, a.split, scene) for arm in ARMS}
        var = {arm: load_variation(p) for arm, p in d.items()}
        var = {k: v for k, v in var.items() if v}
        if "A" not in var:
            print(f"[{scene}] A팔 없음 — 건너뜀")
            all_ok = False
            continue

        sec = {}
        ta0 = tiers_a.get(scene, {})
        tb0 = tiers_b.get(scene, {})
        sec["VG-01"] = gate_vg01(d["A"], d["B"], d["C"], ta0, tb0)
        sec["VG-02"] = gate_vg02(d["A"], d["C"], d["D"])
        sec["VG-datum/10"] = gate_datum_pose(var)
        sec["VG-08"] = {arm: gate_vg08(d[arm], var[arm]) for arm in var}
        sec["VG-void"] = {arm: gate_vg_void(d[arm]) for arm in var}

        # strict-H 프레임 목록 (A팔) · paired-H
        ta, tb = ta0, tb0
        h_a = [f for f, v in ta.items() if v["tier_strict"] == "H"]
        h_b = [f for f, v in tb.items() if v["tier_strict"] == "H"]
        paired = sorted(set(h_a) & set(h_b))
        sec["tier_A"] = dict(collections.Counter(
            v["tier_strict"] for v in ta.values()))
        sec["tier_B"] = dict(collections.Counter(
            v["tier_strict"] for v in tb.values()))
        sec["paired_H"] = dict(n_A=len(h_a), n_B=len(h_b), n_paired=len(paired),
                               n_frames=len(ta), files=paired)

        ncue = bool(PRIMS.get(scene, {}).get("ncue"))
        if ncue:
            # ── (a) 전 팔 GT 올-음성 ────────────────────────────────────────
            sec["ALLNEG"] = {}
            for tag, tt in (("A", ta0), ("B", tb0),
                            ("C", tiers_c.get(scene, {})),
                            ("D", tiers_d.get(scene, {}))):
                if tt:
                    sec["ALLNEG"][tag] = gate_allneg(tt, tag)
            sec["GRID-DEPTH"] = {arm: gate_grid_depth(d[arm], a.walk_z)
                                 for arm in var}
            # ── (b) 단서 픽셀 분포 (DZ §12-5 k 게이트의 데이터 원천) ─────────
            sec["CUE-PX"] = {arm: gate_cue_px(d[arm], scene, var[arm])
                             for arm in var}
            # ── (c) (C,D) 광학차 = **단서 ON↔OFF** = 계기판 ③ 용량-반응 입력 ──
            files_cd = sorted({c["file"] for c in cuts_of(var["A"])})
            sec["VG-07-CD"] = gate_vg07(d.get("C", ""), d.get("D", ""), files_cd)

        lateral = bool(PRIMS.get(scene, {}).get("lateral"))
        # 측방 씬은 strict-H 프레임이 드물다(가림체가 없으니 정상이다). VG-06 의 ID 마스크
        #   측정은 **전 프레임**에 대해 돌려야 정보가 남는다.
        vg06_files = sorted(h_a) if not (lateral or ncue) else sorted(ta)
        sec["VG-06"] = gate_vg06(d["A"], scene, vg06_files, cuts_of(var["A"]))
        files = sorted({c["file"] for c in cuts_of(var["A"])})
        sec["VG-07"] = gate_vg07(d["A"], d["C"], files)
        # A팔 = 단서·위험 전부 ON = 룩이 가장 밝은 팔이다. 순백 지표는 여기서 잰다.
        sec["WHITE"] = gate_white(d["A"], files)
        if lateral:
            sec["SECTOR-A"] = gate_sectors(ta, cuts_of(var["A"]))
            sec["SECTOR-B"] = gate_sectors(tb, cuts_of(var.get("B") or var["A"]))

        report["scenes"][scene] = sec

        # ── 인쇄 ────────────────────────────────────────────────────────────
        print("=" * 78)
        print(f"[{scene}] 4팔 게이트 — {a.stamp}_{{A,B,C,D}}/{a.split}")
        print("=" * 78)
        g = sec["VG-01"]
        print(f"  VG-01  A/B GT 동일성 : {g.get('tier')} · 바이트동일="
              f"{g.get('bytes_equal')} · 다른 셀 {g.get('n_cells_diff')} "
              f"(max|Δz| {g.get('max_abs_dz')} m) · **발자국 안 다른 셀 "
              f"{g.get('n_cells_diff_in_footprint')}/{g.get('n_footprint_cells')} "
              f"(max|Δz| {g.get('max_abs_dz_in_footprint')} m)** · void 마스크 동일="
              f"{g.get('void_mask_equal')} · **polar_gt 동일 "
              f"{g.get('polar_gt_equal_frames')}/{g.get('polar_gt_frames')} 프레임** → "
              f"{'통과' if g.get('ok') else '**미달**'}")
        print(f"         hash A={g.get('hash_A')} B={g.get('hash_B')}")
        g = sec["VG-02"]
        print(f"  VG-02  C/D 음성      : **발자국 안 C가 D보다 낮은 셀 "
              f"{g.get('cells_C_below_D_in_footprint')}** (C가 높은 셀 "
              f"{g.get('cells_C_above_D_in_footprint')} = 보존된 장식·단서 · "
              f"무제한 {g.get('cells_C_vs_D_all')}) · C 잔존위험셀 "
              f"{g.get('cells_resid_hazard_in_C')} · (참고 A↔C 발자국 "
              f"{g.get('cells_footprint_A')} 셀) → "
              f"{'통과' if g.get('ok') else '**미달**'}")
        for arm, r in sec["VG-datum/10"].items():
            print(f"  VG-datum A↔{arm}    : exact {r['datum_exact']} · tol "
                  f"{r['datum_tol']} · fail {r['datum_fail']} · 생존율 "
                  f"{r['survival']:.4f} · max|Δgz| {r['max_abs_dz']:.6f} m · "
                  f"VG-10 불일치 {r['pose_mismatch']}")
        for arm, r in sec["VG-08"].items():
            print(f"  VG-08  {arm}팔 세그   : {r['n_idseg']}/{r['n_cuts']}컷 · "
                  f"고유 포즈 {r['n_poses']} · 고유 마스크 해시 "
                  f"{r['n_distinct_hashes']} · fetch {r['fetch']} · "
                  f"포즈별 신선 {r['per_cut_fresh']}")
        for arm, r in sec["VG-void"].items():
            print(f"  VG-void {arm}팔      : 커버리지 {r.get('coverage')} "
                  f"({r.get('n_finite')}/{r.get('n_total')})")
        print(f"  tier  A팔 {sec['tier_A']} · B팔 {sec['tier_B']}")
        p = sec["paired_H"]
        print(f"  paired-H            : A {p['n_A']} · B {p['n_B']} · "
              f"**둘 다 H = {p['n_paired']}** / {p['n_frames']}컷")
        g = sec["VG-06"]
        print(f"  VG-06  모서리 소속   : {'전' if lateral else 'H'} 프레임 "
              f"{g['n_frames']} · 가림체>0 "
              f"{g['n_occluder_pos']} · **격자 안 낙차 구조물>0 {g['n_hazard_pos']}** "
              f"(격자 무제한 {g.get('n_hazard_pos_all')}) · "
              f"단서 px {g['cue_px_min']}–{g['cue_px_max']} · 맥락 px 최대 "
              f"{g.get('context_px_max')} → "
              + ("**측정만** (측방 씬 — 은닉 요구 없음, 계획 §2.3)" if lateral
                 else ('통과' if g['ok'] else '**미달**')))
        for tag, arm in (("SECTOR-A", "A팔"), ("SECTOR-B", "B팔")):
            g = sec.get(tag)
            if not g or not g.get("n_frames"):
                continue
            print(f"  섹터 분포 {arm}      : n={g['n_frames']} · 프레임당 양성셀 "
                  f"{g['cells_per_frame']}/20 · none_in_fov {g['none_in_fov']}")
            print("      양성률  " + " · ".join(
                f"{k} {v:.3f}" for k, v in g["pos_rate"].items()))
            print("      셀점유  " + " · ".join(
                f"{k} {v:.3f}" for k, v in g["cell_share"].items())
                + f"  ⇒ **측방 A+E {g['lateral_share']:.3f}** vs 중간 B+D "
                  f"{g['mid_share']:.3f} vs 정면 C {g['center_share']:.3f}"
                + f" → {'통과' if g['ok'] else '**미달**'}")
            bs = g["band_sector"]
            print("      밴드×섹터 (양성 프레임 수)   " + "   ".join(bs["sectors"]))
            for bi, bn in enumerate(bs["bands"]):
                print(f"        밴드 {bn:<3s} " + " ".join(
                    f"{c:3d}" for c in bs["counts"][bi]))
        g = sec["VG-07"]
        if g.get("ok"):
            print(f"  VG-07  (A,C) 광학차  : n={g['n_pairs']} · mean|ΔI| "
                  f"min {g['mean_abs']['min']} / p50 {g['mean_abs']['p50']} / "
                  f"max {g['mean_abs']['max']} · frac>8 p50 "
                  f"{g['frac_gt8']['p50']} · **정보량 0 쌍 {g['n_zero_info']}**")
        g = sec["WHITE"]
        if g.get("ok"):
            w, wg = g["white"], g["white_gnd"]
            print(f"  WHITE  순백 대면적   : n={g['n_frames']} · **공식 "
                  f"frac(min>0.8) p50 {w['p50']:.4f}** (min {w['min']:.4f} / "
                  f"max {w['max']:.4f}) · 하단2/3 p50 {wg['p50']:.4f} "
                  f"(max {wg['max']:.4f}) · mean p50 {g['mean']['p50']}")
            dep = g["white_max_deprecated"]
            print(f"         [deprecated] 구 지표 frac(max>0.8) p50 "
                  f"{dep['p50']:.4f} / max {dep['max']:.4f} — 포화 황색을 순백으로 "
                  f"오분류한다. 참고용 마지막 인쇄 (REG_AUDIT §6.1)")
        elif g.get("note"):
            print(f"  WHITE  순백 대면적   : {g['note']}")

        if ncue:
            print("  " + "-" * 74)
            print("  **N-cue 판정층** (④-a 함정 표본 · 계획 §2.4)")
            for tag in ("A", "B", "C", "D"):
                r = sec["ALLNEG"].get(tag)
                if not r:
                    continue
                md = r.get("max_diff") or {}
                print(f"  (a) ALL-NEG {tag}팔   : n={r['n_frames']} · GT 양성 프레임 "
                      f"**{r['n_frames_gt_positive']}** · pre-gate 양성 "
                      f"**{r['n_frames_pregate_positive']}** · **cells_raw "
                      f"{r['cells_raw']}** · max_diff "
                      f"{md.get('min')}–{md.get('max')} m (< {HAZ_DEPTH}) · tier "
                      f"{r['tiers']} → {'통과' if r['ok'] else '**미달**'}")
            for arm, r in sorted(sec["GRID-DEPTH"].items()):
                if r.get("note"):
                    print(f"  (a) 격자깊이 {arm}팔  : {r['note']}")
                    continue
                print(f"  (a) 격자깊이 {arm}팔  : z ∈ [{r['z_min']}, {r['z_max']}] · "
                      f"보행면(mode {r['mode_z']}) 대비 최저 **{r['depth_below_walk']} m** "
                      f"(여유 {r['margin_to_threshold']}) · 임계 이상 셀 "
                      f"**{r['n_cells_below_threshold']}** · 커버리지 {r['coverage']} → "
                      f"{'통과' if r['ok'] else '**미달**'}")
            for arm in ("A", "B", "C", "D"):
                r = sec["CUE-PX"].get(arm)
                if not r or not r.get("ok"):
                    continue
                t, tg = r["cue_total"], r["cue_total_grid"]
                print(f"  (b) 단서 픽셀 {arm}팔 : n={r['n_frames']} · **전체** "
                      f"min {t['min']} / p25 {t['p25']} / p50 {t['p50']} / "
                      f"p75 {t['p75']} / max {t['max']} (화면 비율 p50 "
                      f"{r['cue_frac_p50']}) · **격자 안** p50 {tg['p50']} "
                      f"(min {tg['min']} / max {tg['max']})")
                print("      클래스별 p50(전체/격자안, 등장 프레임): " + " · ".join(
                    f"{g_} {r['per_group'][g_]['p50']}/"
                    f"{r['per_group_grid'][g_]['p50']}"
                    f"({r['n_frames_with_group'][g_]})"
                    for g_ in sorted(r["per_group"])))
            g = sec["VG-07-CD"]
            if g.get("ok"):
                print(f"  (c) **(C,D) 광학차** : n={g['n_pairs']} · mean|ΔI| "
                      f"min {g['mean_abs']['min']} / p50 {g['mean_abs']['p50']} / "
                      f"max {g['mean_abs']['max']} · frac>8 p50 "
                      f"{g['frac_gt8']['p50']} · 정보량 0 쌍 {g['n_zero_info']} "
                      "← 계기판 ③ 용량-반응 입력 (단서 ON↔OFF)")
            else:
                print(f"  (c) (C,D) 광학차     : {g.get('note')}")
            print("  " + "-" * 74)

        base_ok = [sec["VG-01"].get("ok"), sec["VG-02"].get("ok")]
        if not ncue:
            base_ok.append(sec["VG-06"].get("ok"))
        ok = all(base_ok
                 + [r["ok"] for r in sec["VG-datum/10"].values()]
                 + [r["ok"] for r in sec["VG-08"].values()]
                 + [r.get("ok", False) for r in sec["VG-void"].values()]
                 # 측방 씬은 섹터 게이트가 **판정층**이다(VG-06 은 측정층으로 내려간다).
                 + ([sec["SECTOR-A"].get("ok", False)] if lateral else [])
                 # N-cue 씬은 (a) 올-음성 + 격자깊이가 판정층이고, (b)(c) 는 산출층이다
                 #   (분포·광학차에는 사전 등록된 임계가 없다 — k 는 VG-11 소관).
                 + ([r["ok"] for r in sec["ALLNEG"].values()]
                    + [r.get("ok", False) for r in sec["GRID-DEPTH"].values()]
                    if ncue else []))
        sec["verdict"] = "통과" if ok else "미달 항목 있음"
        all_ok = all_ok and ok
        print(f"  ⇒ {scene} 종합: {sec['verdict']}")

    if a.out:
        os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
        json.dump(report, open(a.out, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print(f"\n[out] {a.out}")
    print("\n" + "=" * 78)
    print("종합 판정: " + ("통과" if all_ok else "미달 항목 있음"))
    print("=" * 78)
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
