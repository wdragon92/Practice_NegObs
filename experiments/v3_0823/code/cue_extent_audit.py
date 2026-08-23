#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cue_extent_audit.py — CUE-EXTENT AUDIT (사용자 룰링 **D82 ⓒ**).

무엇인가
--------
존재 \|r\|(`build_render_plan.py:444 per_key()` · ACCOUNTING §4.9-3)의 **면적판**이다.
존재판은 "그 씬/팔에 단서가 **있느냐 없느냐**"의 2×2 φ를 잰다. 이 감사는 같은 물음을
**연속량**으로 바꾼다 — "위험이 있는 프레임이 **단서 픽셀을 더 많이** 갖고 있느냐".
전자가 0이어도 후자가 클 수 있고, 그러면 모델은 *단서 밀도*라는 새 지름길을 배운다.

  존재 |r| : hazard(0/1)  ×  cue_present(0/1)      → φ (2×2)
  면적 r   : hazard(0/1)  ×  cue_area_px(연속)      → **점이연 상관 r_pb**
  개수 r   : hazard(0/1)  ×  cue_obj_count(연속)    → r_pb

측정기
------
컷별 ID 마스크 사이드카 `.idseg.npz`(`instance_id_segmentation`)가 프림 경로를 그대로
돌려준다(P-5 세그 스모크 실증 · W1B2 §2.2). 프레임마다 프림 경로별 픽셀 수를 세고,
프림을 **단서 키**에 귀속시켜 합산한다.

귀속(attribution)은 세 겹이고 **각 겹의 출처를 프림 단위로 기록**한다.
  ① `declared`  — 신규 씬(H1·H2·H3·H6·H7·L1·N9·N11)의 `GATED_ZONES` 표
                  `(tag, cue_key, …)`. 렌더 **전**에 손으로 선언되고 씬 자체의
                  `datum_selfcheck()`가 기계 검사하는 표다. 가장 강한 근거.
  ② `empirical` — **팔 차분**. 같은 씬·시드·밴드·조건·포즈에서 A팔과 B팔은 설정만
                  다르다. 프림을 지우는 일만 하므로 `visible(A,i) \ visible(B,i)`는
                  **정확히** 그 프레임에서 B레버가 지운 단서 프림이다(제거는 가림을
                  풀 뿐 만들지 않는다). 렉시컬 추측이 필요 없다.
  ③ `lexical`   — `prims2.json`(CUE_COVERAGE §부록 · 가드 본문 + 호출된 `build_*`
                  본문의 프림 경로)에서 뽑은 컴포넌트 접두사 + 전역 토큰 사전.
                  ①②가 닿지 못하는 자리(레버가 아닌 키·A팔만 있는 씬)를 메운다.

**T키(`cue_material_break`)는 원리적으로 면적 계기의 사각지대다.** 32씬 중 24씬에서
프림을 만들거나 지우지 않고 **재질 바인딩만** 바꾼다(CUE_COVERAGE §0-3 헤드라인 5).
ID 마스크는 기하·카메라만의 함수라 재질 재바인딩에 **불변**이다(W1B2 §2.2 ③).
따라서 T의 면적 r은 **정의상 0**이며, 존재판의 "상수 키"와 같은 자리에 **면적-불가시
키**로 별도 인쇄한다. 숨기지 않고 인쇄하는 것이 §4.9-3 규약의 정신이다.

모집단
------
P1 **as-built v3 훈련 코퍼스** — 디스크에 **strict** 사이드카가 실재하는 컷만.
   A팔 : 정본 A 라운드에 설치된 백필 696컷 (W1B2 §2.3 · 격리 5유닛 120컷 제외)
   B팔 : 12씬 `…lib_B2*` + 3씬 `…lib_B*` (W1B2 §7 코퍼스 매니페스트 지시)
   D팔 : `…lib_D*` 912컷 − **stale 152컷**(`idseg_fetch == "t0"` · W1D §2.2)
   C팔 : **미렌더**(사용자 결재 대기 · W1B_REPORT §9 C-1) → 표에 PENDING 으로 남긴다
P2 **신규 씬 프로브** — 2×2 전 팔이 strict 로 존재한다(H1·H2·H3·L1·N9·N11) +
   H6·H7 은 (A,C) 쌍만.

산출
----
  experiments/v3_0823/cue_extent_audit.json     기계 산출 (전 표의 원천)
  experiments/v3_0823/logs/cue_extent_frames.json   프레임 단위 캐시 (재분석용)
  experiments/v3_0823/logs/cue_extent_attrib.json   귀속 원장 (프림 단위 출처)

사용
----
  python3 experiments/v3_0823/code/cue_extent_audit.py --stage all
  python3 experiments/v3_0823/code/cue_extent_audit.py --stage analyze   # 캐시 재사용
  python3 experiments/v3_0823/code/cue_extent_audit.py --regen-hook      # N9/N11·C 웨이브 갱신

**CPU 전용 · Isaac 미기동 · GPU 미사용 · git 명령 미사용 · 정본 파일 무수정.**
"""
import argparse
import ast
import collections
import glob
import json
import math
import os
import random
import re
import sys
import time

import numpy as np

REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"
V3 = os.path.join(REPO, "experiments/v3_0823")
CODE = os.path.join(V3, "code")
LOGS = os.path.join(V3, "logs")
ANN = os.path.join(V3, "annotations")
DATA = os.path.join(REPO, "dataset")

FRAME_PX = 1920 * 1080  # 2,073,600
# strict 경로가 남기는 fetch 태그. `t0` 는 첫 컷 마스크 복제(=stale) 이므로 제외한다
# (W1D §2.2 · SCENE_H67_BUILD §7).
STRICT_FETCH = {"orch", "orch_forced"}

KEYS6 = ("R", "Ta", "N", "T", "Sg", "V")
CUE2KEY = {"cue_railing": "R", "cue_tactile": "Ta", "cue_nosing": "N",
           "cue_material_break": "T", "cue_sign": "Sg", "cue_scene_dressing": "V"}
# v3 신설/승격 키 — 신규 씬에만 있다. 헤드라인 6키와 분리해 부록으로 인쇄한다.
CUE2KEY_EXT = {"cue_shadow_caster": "Sh", "cue_manhole": "Mh", "cue_tree_grate": "Tg",
               "cue_slab_joint": "Jt", "cue_drainage": "Dr", "cue_bollard": "Bo",
               "cue_delineator": "De", "cue_road_marking": "Rm",
               "cue_convex_mirror": "Cm"}
ALLKEY = dict(CUE2KEY)
ALLKEY.update(CUE2KEY_EXT)
KEY2CUE = {v: k for k, v in ALLKEY.items()}
KEYNAME = {"R": "railing", "Ta": "tactile", "N": "nosing", "T": "material_break",
           "Sg": "sign", "V": "scene_dressing", "Sh": "shadow_caster",
           "Mh": "manhole", "Tg": "tree_grate", "Jt": "slab_joint",
           "Dr": "drainage", "Bo": "bollard", "De": "delineator",
           "Rm": "road_marking", "Cm": "convex_mirror",
           "Gk": "ground_pattern(미분해)",
           "Ux": "cue-확정·키미상(팔 차분만)"}
# `GKit*` 네임스페이스는 여러 키가 한 접두사를 공유한다(예: sceneH1 `GKitCrown` =
# manhole/slab_joint/drainage). 하위 세그먼트로 갈라 보고, 갈리지 않으면 `Gk`로 둔다.
GKIT_SUB = [("Manhole", "Mh"), ("Gully", "Dr"), ("Trench", "Dr"), ("Gutter", "Dr"),
            ("Drain", "Dr"), ("Grate", "Tg"), ("Joint", "Jt"), ("JX_", "Jt"),
            ("Crack", "Jt"), ("Groove", "Jt")]
# 마모대·얼룩·패치 같은 **지면 표면처리**는 어느 cue_* 키에도 1:1 대응하지 않는다.
# 장식(V)으로 밀어 넣으면 지면이 단서로 둔갑하므로 `Gk`(미분해)에 남긴다.

# --------------------------------------------------------------------------
# 라운드 등록부 — 선언적. 새 라운드는 여기만 고치면 된다(`--regen-hook` 참조).
# --------------------------------------------------------------------------
A_ROUNDS = [("260819_main_on", "base"), ("260820_boost_h_on", "h"),
            ("260820_boost_e_on", "e"), ("260820_boost_e2_on", "e2")]
B_ROUNDS = [("260826_v3w1_lib_B", "base"), ("260826_v3w1_lib_B_h", "h"),
            ("260826_v3w1_lib_B_e", "e"), ("260826_v3w1_lib_B_e2", "e2")]
B2_ROUNDS = [("260826_v3w1_lib_B2", "base"), ("260826_v3w1_lib_B2_h", "h"),
             ("260826_v3w1_lib_B2_e", "e"), ("260826_v3w1_lib_B2_e2", "e2")]
# [08-24 · D90 ①] 세그 3차 판정이 해제한 레버를 더해 다시 찍은 5씬 = B3 트리.
B3_ROUNDS = [("260827_v3w1_lib_B3", "base"), ("260827_v3w1_lib_B3_h", "h"),
             ("260827_v3w1_lib_B3_e", "e"), ("260827_v3w1_lib_B3_e2", "e2")]
D_ROUNDS = [("260826_v3w1_lib_D", "base"), ("260826_v3w1_lib_D_h", "h"),
            ("260826_v3w1_lib_D_e", "e"), ("260826_v3w1_lib_D_e2", "e2")]
# [08-24 · 코퍼스 v3 조립] C 웨이브가 착지했다(W1C_REPORT §8.2 — 816/816컷 · fetch=orch
# 816/816 · `.idseg.STALE` 0). D83 ②가 "미렌더 → PENDING"으로 남긴 칸이 실물로 채워진다.
C_ROUNDS = [("260827_v3w1_lib_C", "base"), ("260827_v3w1_lib_C_h", "h"),
            ("260827_v3w1_lib_C_e", "e"), ("260827_v3w1_lib_C_e2", "e2")]
# W2 (sceneH6·H7 — **훈련측 val 공급 씬**). 훈련 코퍼스의 일부이므로 P1 에 들어간다.
# 밴드 토큰이 라운드명에 있다(W2 §1.2 — 같은 디렉터리를 쓰면 세그가 재생성되지 않는다).
W2_ROUNDS = [("260824_v3w2_h67base", "w2base"), ("260824_v3w2_h67h", "w2h"),
             ("260824_v3w2_h67h2", "w2h2")]
W2_SCENES = ("sceneH6", "sceneH7")
# W1B2 §7 코퍼스 매니페스트 지시 — 이 12씬의 B팔 정본은 B2 트리다.
B2_SCENES = set("scene02 scene08 scene09 scene12 scene16 scene17 scene20 "
                "scene21 sceneC1 sceneC4 sceneD1 sceneD3".split())
# D90 ① — 이 5씬의 B팔 정본은 **B3 트리**다 (B3 > B2 > B).
B3_SCENES = set("scene01 scene09 scene21 sceneC1 sceneC4".split())


def b_tree_of(scene):
    if scene in B3_SCENES:
        return "B3"
    return "B2" if scene in B2_SCENES else "B"
# 무낙차 4씬 — v2 on팔이 그대로 C팔이다(계획 §1.0 첫 항목). A팔이라는 말이 성립하지 않는다.
NODROP_SCENES = ("sceneN1", "sceneN2", "sceneN4", "sceneN5")

# P2 신규 씬 프로브 — (스탬프, 씬들, {팔: 라벨파일·side})
# [08-24] **as-built 본렌더(W3)로 교체.** 구 `260823_v3p5_*rev` 프로브는 (ㄱ) 씬 파일
# 수정 시각을 팔 사이에 걸친 라운드가 있고(D87 ② VG-ver) (ㄴ) 규정 감사 수정 전 기하다.
# W3 본렌더는 6씬 전부 버전 일치 확인 · 게이트 48/48 (W3_REPORT §2·§3).
PROBE_PRIMARY = [
    dict(stamp="260824_v3w3_extbase", scenes=["sceneH1", "sceneH2", "sceneH3"], group="h12",
         labels={"A": ("w3_base_ac_labels.json", "on"), "C": ("w3_base_ac_labels.json", "off"),
                 "B": ("w3_base_bd_labels.json", "on"), "D": ("w3_base_bd_labels.json", "off")}),
    dict(stamp="260824_v3w3_extbase", scenes=["sceneL1"], group="l1b",
         labels={"A": ("w3_base_ac_labels.json", "on"), "C": ("w3_base_ac_labels.json", "off"),
                 "B": ("w3_base_bd_labels.json", "on"), "D": ("w3_base_bd_labels.json", "off")}),
    dict(stamp="260824_v3w3_extbase", scenes=["sceneN9", "sceneN11"], group="n911",
         labels={"A": ("w3_base_ac_labels.json", "on"), "C": ("w3_base_ac_labels.json", "off"),
                 "B": ("w3_base_bd_labels.json", "on"), "D": ("w3_base_bd_labels.json", "off")}),
    dict(stamp="260824_v3w3_exth", scenes=["sceneH1", "sceneH2", "sceneH3"], group="h3",
         labels={"A": ("w3_h_ac_labels.json", "on"), "C": ("w3_h_ac_labels.json", "off"),
                 "B": ("w3_h_bd_labels.json", "on"), "D": ("w3_h_bd_labels.json", "off")}),
    dict(stamp="260824_v3w3_extlat", scenes=["sceneL1"], group="l1",
         labels={"A": ("w3_lat_ac_labels.json", "on"), "C": ("w3_lat_ac_labels.json", "off"),
                 "B": ("w3_lat_bd_labels.json", "on"), "D": ("w3_lat_bd_labels.json", "off")}),
    dict(stamp="260824_v3w3_extb2", scenes=["sceneN9", "sceneN11"], group="n911b2",
         labels={"A": ("w3_b2_ac_labels.json", "on"), "C": ("w3_b2_ac_labels.json", "off"),
                 "B": ("w3_b2_bd_labels.json", "on"), "D": ("w3_b2_bd_labels.json", "off")}),
]
P2_PRIMARY_GROUPS = ("h12", "h3", "l1", "l1b", "n911", "n911b2")
P2_NCUE_GROUPS = ("n911", "n911b2")
# H6·H7 은 W2 본렌더에서 4팔 완비됐다 → **P1(훈련 코퍼스)** 로 이동. P2 프로브 항목은 비운다.
PROBE_H67 = []
# 부차(기록만 · 헤드라인 비산입): 개정 전 라운드와 2차 draw
PROBE_SECONDARY = [
    dict(stamp="260823_v3p5_h12probe", scenes=["sceneH1", "sceneH2"], group="h12_r0",
         labels={"A": ("h12_r0_ac_labels.json", "on"), "C": ("h12_r0_ac_labels.json", "off"),
                 "B": ("h12_r0_bd_labels.json", "on"), "D": ("h12_r0_bd_labels.json", "off")}),
    dict(stamp="260823_v3p5_n911rev", scenes=["sceneN9", "sceneN11"], group="n911_rev",
         labels={"A": ("n911_rev_ac_labels.json", "on"), "C": ("n911_rev_ac_labels.json", "off"),
                 "B": ("n911_rev_bd_labels.json", "on"), "D": ("n911_rev_bd_labels.json", "off")}),
    dict(stamp="260823_v3p5_n911rev2", scenes=["sceneN9", "sceneN11"], group="n911_rev2",
         labels={"A": ("n911_rev2_ac_labels.json", "on"), "C": ("n911_rev2_ac_labels.json", "off"),
                 "B": ("n911_rev2_bd_labels.json", "on"), "D": ("n911_rev2_bd_labels.json", "off")}),
    # `260823_v3p5_n911b2_*` 는 **본 감사 실행 시점에 렌더 중**이었다(다른 에이전트의
    # 2차 draw). 반쯤 쓰인 트리 위에서 판정하지 않는다 — 등록부에서 뺀다.
]

SCENE_DIRS = ["scenes/main", "scenes/batch1", "scenes/probe"]
KITFILES = {"scene_common.py", "batch1_common.py", "probe_common.py", "building_kit.py",
            "facade_kit.py", "ground_kit.py", "infra_kit.py", "props_kit.py",
            "stair_kit.py", "urban_kit.py", "variation_kit.py"}

# --------------------------------------------------------------------------
# 전역 토큰 사전 (③ lexical) — 33 정본 씬의 명명 관례.
#   근거: `prims2.json` 가드 본문 프림 + CUE_COVERAGE §2 의 제거 대상 프림 열.
#   **접두사**로만 쓰고, 매칭은 프림 경로의 세그먼트 단위다.
#   과잉 매칭 위험이 있는 토큰(구조물과 이름을 공유하는 것)은 넣지 않았다 —
#   그런 자리는 ②(팔 차분)가 잡는다.
# --------------------------------------------------------------------------
LEX_TOKENS = {
    "R":  ["Rail", "Handrail", "Balus", "Newel", "Guardrail", "PerimRail",
           "StairRail", "DeckRail", "OpenRail", "BayRail", "EndRail", "LogRail",
           "WallPipe", "RailPost", "GBGrp", "FlankGrp"],
    "Ta": ["Tactile", "WarnBand", "TactileWarn", "TactileGuide", "TactileDots",
           "TactileHigh", "TactileLow", "TactileHead", "TactileCrest"],
    "N":  ["Nosing", "Nose_", "NoseGrp", "NosingStrip", "CascadeNosing"],
    "Sg": ["Sign", "SignBack", "SignInfo", "SignPost", "KmSign", "DockSign",
           "EntrySign", "BusSign", "RouteBoard", "Lectern"],
    "V":  ["Planter", "Bench", "LowBench", "ArenaBench", "PlazaBench", "ShelterBench",
           "Bin_", "Bollard", "LowBollard", "Streetlight", "Lamp", "LightT",
           "Tree_", "TreeX", "LawnTree", "StreetTree", "FarTree", "TerraceTree",
           "Shrub", "Hedge", "FarHedge", "Reed", "Grass", "Lawn", "Soil",
           "Backdrop", "Building_", "CityBlock", "FarBuilding", "House_", "Villa",
           "Warehouse", "Shed_", "Container", "Carton", "Pallet", "BagPallet",
           "ToolBox", "Reel_", "FormPanel", "Pile_", "PileToe", "Mound",
           "Fountain", "Monument", "Flagpole", "Gate", "EntryCanopy", "Tower_",
           "Shelter", "BusPole", "Litter", "Pot_", "PotPlant", "Curb", "Cap_",
           "Bridge", "BikeRoad", "BikeLine", "Viaduct", "Fence", "FenceCap",
           "Mailbox", "Driveway_Skin", "Pump_", "GreenStrip", "Lane_",
           "Facade", "Column_", "Lintel", "Cornice", "Door_", "Skirt_",
           "Belt_", "Band_", "Diag", "AccessRamp", "GuideStrip", "Dress"],
    "Sh": ["Shadow"],
    "Mh": ["Manhole"],
    "Tg": ["TreeGrate"],
    "Jt": ["Joint", "JX_", "Joints"],
    "Dr": ["Gully", "Trench", "Gutter", "Drain"],
    "Bo": ["Bollard"],
    "De": ["Delineator"],
    "Rm": ["Marking", "RoadDash", "RoadEdge", "CenterLine", "Dash_", "Lane_"],
    "Cm": ["Mirror", "ConvexMirror"],
}
# 절대 단서로 귀속하지 않는 토큰 (구조물 · 지면 · 위험 기하)
LEX_BLOCK = ["Ground", "Plate_", "Bank_", "Step", "Stair", "Tread", "Riser",
             "Landing", "Deck", "Slab", "Wall", "Retain", "Revet", "Berm",
             "Water", "Bed", "Apron", "Plaza", "Path", "Walk", "Road",
             "Corridor", "Ramp", "Flight", "Parapet", "Cope", "Kerb", "Lip",
             "Pier", "Abut", "Sky", "Dome", "Terrain", "Fill", "Crest"]

# --------------------------------------------------------------------------
# 유틸
# --------------------------------------------------------------------------


def log(*a):
    print(*a, flush=True)


def scene_root_of(prim):
    """`/World/Scene01/Rail_0/Post_1` → ('Scene01', ['Rail_0','Post_1'])."""
    seg = [s for s in prim.split("/") if s]
    if not seg:
        return None, []
    if seg[0] == "World":
        seg = seg[1:]
    if not seg:
        return None, []
    return seg[0], seg[1:]


def root_comp(prim):
    """프림의 **씬 하위 최상위 컴포넌트** 이름. 단서 '개체'의 단위로 쓴다."""
    _, rest = scene_root_of(prim)
    return rest[0] if rest else None


def group_of(comp):
    """`Reed_2_35` → `Reed`, `Rail_0` → `Rail`. 설치 '군' 단위."""
    if comp is None:
        return None
    return re.sub(r"(_[0-9]+)+$", "", comp)


# --------------------------------------------------------------------------
# STAGE attrib — 프림 → 단서 키 귀속 원장
# --------------------------------------------------------------------------
def _scene_files():
    out = {}
    for d in SCENE_DIRS:
        dd = os.path.join(REPO, d)
        if not os.path.isdir(dd):
            continue
        for fn in sorted(os.listdir(dd)):
            if not fn.endswith(".py") or fn in KITFILES:
                continue
            p = os.path.join(dd, fn)
            if os.path.islink(p):
                continue
            m = re.match(r"(scene\w+?)_", fn)
            if not m:
                continue
            out.setdefault(m.group(1), p)
    return out


def parse_declared(path):
    """신규 씬의 `GATED_ZONES` + `CUE_CLASS` 를 읽는다 (AST · import 없음)."""
    src = open(path, encoding="utf-8", errors="replace").read()
    tree = ast.parse(src)
    gz, cue_class, cfg = [], {}, {}
    for n in ast.walk(tree):
        if not isinstance(n, ast.Assign):
            continue
        for t in n.targets:
            if not isinstance(t, ast.Name):
                continue
            if t.id == "GATED_ZONES" and isinstance(n.value, (ast.List, ast.Tuple)):
                for el in n.value.elts:
                    if not isinstance(el, (ast.Tuple, ast.List)) or len(el.elts) < 2:
                        continue
                    try:
                        tag = ast.literal_eval(el.elts[0])
                        key = ast.literal_eval(el.elts[1])
                    except Exception:
                        continue
                    if isinstance(tag, str) and isinstance(key, str):
                        gz.append((tag, key))
            elif t.id == "CUE_CLASS" and isinstance(n.value, ast.Dict):
                for k, v in zip(n.value.keys, n.value.values):
                    try:
                        ks = ast.literal_eval(k)
                        vs = ast.literal_eval(v)
                    except Exception:
                        continue
                    cue_class[ks] = vs
            elif t.id == "SCENE_CONFIG" and isinstance(n.value, ast.Dict):
                for k, v in zip(n.value.keys, n.value.values):
                    try:
                        ks = ast.literal_eval(k)
                        vs = ast.literal_eval(v)
                    except Exception:
                        continue
                    cfg[ks] = vs
    return gz, cue_class, cfg


def declared_prefixes(gz):
    """GATED_ZONES `(tag,key)` → {key: [prefix,…]}. `Dress-S`→`Dress` 처럼
    방위 접미사를 떼고 프림 네임스페이스 루트만 남긴다."""
    out = collections.defaultdict(set)
    for tag, key in gz:
        base = re.sub(r"-(S|N|E|W|Far|Near|C)$", "", tag)
        if key.startswith("hazard"):
            continue
        keys = []
        if "/" in key:  # e.g. "cue_manhole/slab_joint/drainage"
            head, rest = key.split("/", 1)
            keys.append(head)
            for r in rest.split("/"):
                keys.append("cue_" + r if not r.startswith("cue_") else r)
        else:
            keys.append(key)
        for k in keys:
            kk = ALLKEY.get(k)
            if kk:
                out[kk].add(base)
    return {k: sorted(v) for k, v in out.items()}


def lexical_prefixes_from_prims2(entry):
    """`prims2.json` 항목 → {key: [컴포넌트 접두사,…]}."""
    out = collections.defaultdict(set)
    for cue, v in entry.get("keys", {}).items():
        kk = ALLKEY.get(cue)
        if not kk or not v.get("declared"):
            continue
        for g in v.get("guards", []):
            for s in g.get("prims", []):
                if len(s) > 80 or s.count(" ") > 2:
                    continue                      # 로그 문자열
                s2 = s.replace("{base}", "").replace("{prefix}", "")
                parts = [p for p in s2.split("/") if p]
                cand = None
                for p in parts:
                    if p in ("World", "Looks") or re.fullmatch(r"Scene\w+", p):
                        continue
                    cand = p
                    break
                if cand is None:
                    continue
                cand = re.sub(r"\{[^}]*\}", "", cand)
                if len(cand) < 3:
                    continue
                out[kk].add(cand)
    return {k: sorted(v) for k, v in out.items()}


def _comps_of(f):
    try:
        z = np.load(f, allow_pickle=True)
        lab = json.loads(str(z["idToLabels"]))
        a = z["idseg"]
        ids = np.unique(a)
        out = set()
        for i in ids:
            p = lab.get(str(i))
            if p:
                c = root_comp(p)
                if c:
                    out.add(c)
        return out
    except Exception:
        return set()


def d_arm_survivors(workers=12):
    """D팔(전 cue OFF + 위험 OFF)에서도 보이는 컴포넌트 = 어떤 cue 토글도 만들지
    않는 프림. 전역 토큰 사전의 과잉 매칭을 잘라내는 기계 근거다."""
    from concurrent.futures import ProcessPoolExecutor
    jobs = collections.defaultdict(list)
    for rnd, _b in D_ROUNDS:
        for f in glob.glob(os.path.join(DATA, rnd, "*", "*", "*.idseg.npz")):
            jobs[os.path.basename(os.path.dirname(f))].append(f)
    for sp in PROBE_PRIMARY + PROBE_SECONDARY:
        for sc in sp["scenes"]:
            for f in glob.glob(os.path.join(DATA, f"{sp['stamp']}_D", "*", sc,
                                            "*.idseg.npz")):
                jobs[sc].append(f)
    flat, owner = [], []
    for sc, fs in sorted(jobs.items()):
        for f in fs:
            flat.append(f)
            owner.append(sc)
    out = collections.defaultdict(set)
    if not flat:
        return out
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for sc, comps in zip(owner, ex.map(_comps_of, flat, chunksize=8)):
            out[sc] |= comps
    return out


def _armdiff_one(pair):
    """(A파일, B파일) → {상대 프림경로: 제거된 픽셀}. B가 지운 것만 남는다.

    **루트가 아니라 전체 상대경로**로 기록한다. 네임스페이스가 섞인 씬이 있기
    때문이다 — scene20 은 장식(`Diag/Litter_Plaza`)을 위험 기하(`Diag/UpperWedge`)와
    **같은 `Diag` 루트 아래** 둔다. 루트로 기록하면 계단 쐐기 70만 px 가 장식으로
    둔갑한다(실측으로 잡은 오류다).
    """
    fa, fb = pair
    try:
        pa, _ = _load_prim_areas(fa)
        pb, _ = _load_prim_areas(fb)
    except Exception:
        return {}
    sb = set(pb)
    out = {}
    for p, c in pa.items():
        if p in sb:
            continue
        _r, rest = scene_root_of(p)
        if rest:
            rel = "/".join(rest)
            out[rel] = out.get(rel, 0) + c
    return out


def _pair_index():
    A, B = {}, {}
    for rnd, band in A_ROUNDS:
        for f in glob.glob(os.path.join(DATA, rnd, "*", "*", "*.idseg.npz")):
            A[(os.path.basename(os.path.dirname(f)), band, os.path.basename(f))] = f
    for rounds, tg in ((B_ROUNDS, "B"), (B2_ROUNDS, "B2"), (B3_ROUNDS, "B3")):
        for rnd, band in rounds:
            for f in glob.glob(os.path.join(DATA, rnd, "*", "*", "*.idseg.npz")):
                sc = os.path.basename(os.path.dirname(f))
                if b_tree_of(sc) != tg:
                    continue
                B[(sc, band, os.path.basename(f))] = f
    # 신규 씬 프로브: A팔 vs B팔 (전 cue OFF) — 전 단서 집합이 그대로 나온다
    for sp in PROBE_PRIMARY:
        for sc in sp["scenes"]:
            for f in glob.glob(os.path.join(DATA, f"{sp['stamp']}_A", "*", sc,
                                            "*.idseg.npz")):
                A[(sc, sp["group"], os.path.basename(f))] = f
            for f in glob.glob(os.path.join(DATA, f"{sp['stamp']}_B", "*", sc,
                                            "*.idseg.npz")):
                B[(sc, sp["group"], os.path.basename(f))] = f
    return A, B


def empirical_removed(workers=12, per_unit=8):
    """**팔 차분** — `visible(A,i) \\ visible(B,i)`.

    A팔과 B팔은 같은 씬·시드·밴드·조건·포즈에서 **설정만** 다르고 B는 프림을 지우는
    일만 한다. 제거는 가림을 풀 뿐 새 프림을 만들지 않으므로, 그 차집합은 **정확히**
    그 프레임에서 B레버가 지운 단서 프림이다. 렉시컬 추측이 필요 없는 유일한 근거다.
    """
    from concurrent.futures import ProcessPoolExecutor
    A, B = _pair_index()
    common = sorted(set(A) & set(B))
    byunit = collections.defaultdict(list)
    for k in common:
        byunit[(k[0], k[1])].append(k)
    pairs, owner = [], []
    for (sc, band), ks in sorted(byunit.items()):
        for k in ks[:per_unit]:
            pairs.append((A[k], B[k]))
            owner.append(sc)
    out = collections.defaultdict(collections.Counter)
    nf = collections.Counter()
    if not pairs:
        return out, nf
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for sc, d in zip(owner, ex.map(_armdiff_one, pairs, chunksize=4)):
            nf[sc] += 1
            for r, c in d.items():
                out[sc][r] += c
    return out, nf


PROBE_SCENES = {sc for sp in PROBE_PRIMARY + PROBE_SECONDARY for sc in sp["scenes"]}


def b_arm_survivors(workers=12):
    """B팔(단서 레버 OFF · 위험 ON)에서도 보이는 컴포넌트."""
    from concurrent.futures import ProcessPoolExecutor
    jobs = collections.defaultdict(list)
    for rounds, tg in ((B_ROUNDS, "B"), (B2_ROUNDS, "B2"), (B3_ROUNDS, "B3")):
        for rnd, _b in rounds:
            for f in glob.glob(os.path.join(DATA, rnd, "*", "*", "*.idseg.npz")):
                sc = os.path.basename(os.path.dirname(f))
                if b_tree_of(sc) != tg:
                    continue
                jobs[sc].append(f)
    for sp in PROBE_PRIMARY:
        for sc in sp["scenes"]:
            jobs[sc] += glob.glob(os.path.join(DATA, f"{sp['stamp']}_B", "*", sc,
                                               "*.idseg.npz"))
    flat, owner = [], []
    for sc, fs in sorted(jobs.items()):
        for f in fs:
            flat.append(f)
            owner.append(sc)
    out = collections.defaultdict(set)
    if not flat:
        return out
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for sc, comps in zip(owner, ex.map(_comps_of, flat, chunksize=8)):
            out[sc] |= comps
    return out


def _lever_keys(scene):
    """그 씬의 B팔 레버(꺼진 cue 키) — 실제로 찍은 설정 파일이 최종 사실이다."""
    for suf in ("_B3", "_B2", "_B"):
        p = os.path.join(V3, "render_configs_v3", f"{scene}{suf}.json")
        if os.path.exists(p):
            if b_tree_of(scene) != suf[1:]:
                continue
            cfg = json.load(open(p, encoding="utf-8"))
            return [ALLKEY[k] for k, v in cfg.items()
                    if k in ALLKEY and v is False]
    # 프로브 씬은 B팔이 전 cue OFF 다
    return None


def build_attrib(force=False):
    """귀속 원장을 만든다. 네 겹의 근거를 프림 단위로 남긴다."""
    t0 = time.time()
    scenes = _scene_files()
    prims2 = json.load(open(os.path.join(CODE, "prims2.json"), encoding="utf-8"))
    p2_by_scene = {}
    for k, e in prims2.items():
        m = re.match(r".*::(scene\w+?)_", k)
        if m and k.startswith(("main::", "batch1::")):
            p2_by_scene[m.group(1)] = e

    out = {"doc": "cue_extent_attrib", "version": "1.0",
           "authority": "DECISIONS D82 ⓒ · ACCOUNTING §4.9-3",
           "generated": time.strftime("%Y-%m-%dT%H:%M:%S"), "scenes": {}}

    for sc, path in sorted(scenes.items()):
        gz, cue_class, cfg = parse_declared(path)
        rec = {"file": os.path.relpath(path, REPO),
               "has_gated_zones": bool(gz),
               "has_cue_class": bool(cue_class),
               "cue_keys_declared": sorted(ALLKEY[k] for k in cfg
                                           if k in ALLKEY),
               "defaults": {k: cfg[k] for k in sorted(cfg) if k in ALLKEY},
               "prefix": {}, "prefix_src": {}}
        pref = collections.defaultdict(set)
        src = collections.defaultdict(dict)
        if gz:
            for k, v in declared_prefixes(gz).items():
                for p in v:
                    pref[k].add(p)
                    src[k][p] = "declared"
        e2 = p2_by_scene.get(sc)
        if e2:
            for k, v in lexical_prefixes_from_prims2(e2).items():
                for p in v:
                    if p in pref[k]:
                        continue
                    pref[k].add(p)
                    src[k].setdefault(p, "lexical:prims2")
        # 전역 토큰 사전은 그 씬이 **선언한 키에 한해서만** 연다.
        declared_keys = {ALLKEY[k] for k in cfg if k in ALLKEY}
        if not declared_keys:                       # SCENE_CONFIG 를 못 읽은 경우
            declared_keys = set(pref)
        for k, toks in LEX_TOKENS.items():
            if k not in declared_keys:
                continue
            for tkn in toks:
                if tkn in pref[k]:
                    continue
                pref[k].add(tkn)
                src[k].setdefault(tkn, "lexical:global")
        rec["prefix"] = {k: sorted(v) for k, v in pref.items() if v}
        rec["prefix_src"] = {k: src[k] for k in rec["prefix"]}
        out["scenes"][sc] = rec

    # ---- ⓑ D팔 생존 컴포넌트 (전 cue OFF + 위험 OFF 인데도 남아 있는 것) -----
    surv = d_arm_survivors()
    for sc, comps in surv.items():
        if sc in out["scenes"]:
            out["scenes"][sc]["d_arm_survivors"] = sorted(comps)
    out["d_arm_survivor_scenes"] = len(surv)

    # ---- ⓒ' B팔 생존 + 레버 모순 --------------------------------------------
    #   B레버가 키 k 를 껐는데 그 컴포넌트가 **B팔에 그대로 보인다**면 그것은
    #   k 가 만드는 프림이 아니다(예: scene20 의 `Diag/*` = 대각 계단 = 위험 기하인데
    #   `prims2` 가 장식 가드 본문에서 잘못 주워 왔다). 렉시컬층만 강등한다.
    bsurv = b_arm_survivors()
    for sc, rec in out["scenes"].items():
        if sc in bsurv:
            rec["b_arm_survivors"] = sorted(bsurv[sc])
        lv = _lever_keys(sc)
        if lv is None and sc in PROBE_SCENES:
            # 프로브 씬의 B팔은 그 씬이 가진 cue 키를 **전부** 끈다
            lv = sorted({ALLKEY[k] for k in rec.get("defaults", {}) if k in ALLKEY})
        rec["b_lever"] = lv

    # ---- ④ 경험층: 팔 차분이 실제로 지운 컴포넌트 (정확 일치 · 강등 면제) -----
    emp, nf = empirical_removed()
    n_emp = n_ux = 0
    for sc, cnt in emp.items():
        rec = out["scenes"].get(sc)
        if rec is None:
            continue
        lev = rec.get("b_lever")
        # 레버에서 T(면적 무변)를 뺀 나머지. 하나면 그 키로 확정할 수 있다.
        levk = [k for k in (lev or []) if k != "T"]
        pref = {k: set(v) for k, v in rec["prefix"].items()}
        srcm = {k: dict(v) for k, v in rec["prefix_src"].items()}
        att_local = Attributor({"scenes": {sc: rec}})
        emp_led = {}
        for comp, px in cnt.most_common():
            if comp.split("/")[0].startswith("GKit"):
                # `GKit*` 는 하위 세그먼트로 키가 갈린다(ⓓ). 루트 정확일치를 걸면
                # 그 분해를 덮어써 전부 `Gk` 가 되므로 등록하지 않는다.
                emp_led[comp] = dict(px_per_frame=round(px / max(1, nf[sc]), 1),
                                     key="(GKit 하위 분해)", how="gkit-subresolved")
                continue
            k = att_local.key_of(sc, f"/World/X/{comp}")
            how = "lexical-agrees"
            if k is None:
                if levk and len(levk) == 1:
                    k, how = levk[0], "lever-unique"
                else:
                    k, how = "Ux", "unresolved"
                    n_ux += 1
            pref.setdefault(k, set()).add("=" + comp)      # `=` 접두 = 정확 일치
            srcm.setdefault(k, {})["=" + comp] = "empirical:armdiff"
            emp_led[comp] = dict(px_per_frame=round(px / max(1, nf[sc]), 1),
                                 key=k, how=how)
            n_emp += 1
        rec["prefix"] = {k: sorted(v) for k, v in pref.items() if v}
        rec["prefix_src"] = srcm
        rec["empirical_removed"] = emp_led
        rec["empirical_pairs"] = nf[sc]
    # ---- 강등 원장 (정적 재구성 — 어떤 렉시컬 접두사가 왜 죽었는가) ----------
    dem = {}
    for sc, rec in out["scenes"].items():
        surv = set(rec.get("d_arm_survivors", ()))
        bsurv = set(rec.get("b_arm_survivors", ()))
        lever = set(rec.get("b_lever") or ())
        rows = []
        for k, prefs in rec.get("prefix", {}).items():
            for pp in prefs:
                if pp.startswith("="):
                    continue
                src_ = rec.get("prefix_src", {}).get(k, {}).get(pp, "lexical:global")
                if src_ in Attributor.EXEMPT:
                    continue
                for c in sorted(surv):
                    if c.startswith(pp):
                        rows.append(dict(comp=c, key=k, prefix=pp, src=src_,
                                         rule="D팔 생존"))
                if k in lever:
                    for c in sorted(bsurv):
                        if c.startswith(pp):
                            rows.append(dict(comp=c, key=k, prefix=pp, src=src_,
                                             rule=f"레버 모순({k})"))
        if rows:
            dem[sc] = rows
    out["demotions"] = dem
    out["n_demotions"] = sum(len(v) for v in dem.values())
    out["empirical_components"] = n_emp
    out["empirical_unresolved"] = n_ux
    out["empirical_scenes"] = len([s for s in out["scenes"].values()
                                   if s.get("empirical_removed")])

    os.makedirs(LOGS, exist_ok=True)
    p = os.path.join(LOGS, "cue_extent_attrib.json")
    json.dump(out, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    log(f"[attrib] {len(out['scenes'])} scenes · declared={sum(1 for v in out['scenes'].values() if v['has_gated_zones'])}"
        f" · {time.time()-t0:.1f}s → {os.path.relpath(p, REPO)}")
    return out


class Attributor:
    """프림 경로 → 단서 키. 우선순위는 **구체적인 키 먼저, V(장식)는 마지막**.

    안전장치 넷.
      ⓐ **정확 일치 우선** — `=Comp` 형태(경험층·팔 차분)는 최우선이고 강등되지 않는다.
      ⓑ `LEX_BLOCK`(구조물·지면·위험 기하 토큰)과 충돌하면, **더 긴 단서 접두사가
        이겼을 때만** 귀속한다(`StairRail_N` 은 `Stair`(block)보다 `StairRail`(cue)이
        길어서 난간으로 간다 · `StairTread` 는 block 이 이겨 구조물로 남는다).
      ⓒ **D팔 생존 강등** — 렉시컬층(`prims2`·전역토큰)으로만 잡힌 컴포넌트가 그 씬의
        **D팔(전 cue OFF + 위험 OFF)에도 살아 있으면** 어떤 cue 토글도 만들지 않는
        프림이다. 단서로 세지 않고 강등 원장에 남긴다(예: sceneC1 의 `Snow*` 지면).
        선언(`declared`)과 경험(`empirical:armdiff`)은 면제.
      ⓓ `GKit*` 네임스페이스는 하위 세그먼트로 키를 가르고, 갈리지 않으면 `Gk`.
    """
    ORDER = ["Ta", "N", "R", "Sg", "Cm", "De", "Bo", "Tg", "Mh", "Dr", "Jt",
             "Rm", "Sh", "V", "Ux"]
    EXEMPT = ("declared", "empirical:armdiff")

    def __init__(self, attrib):
        self.attrib = attrib["scenes"]
        self._cache = {}
        self.demoted = collections.Counter()

    def _rules(self, scene):
        r = self._cache.get(scene)
        if r is None:
            rec = self.attrib.get(scene, {})
            pref = rec.get("prefix", {})
            src = rec.get("prefix_src", {})
            exact, rules = [], []
            for k in self.ORDER:
                for p in pref.get(k, ()):
                    s = src.get(k, {}).get(p, "lexical:global")
                    if p.startswith("="):
                        exact.append((k, p[1:], s))
                    else:
                        rules.append((k, p, s))
            surv = set(rec.get("d_arm_survivors", ()))
            bsurv = set(rec.get("b_arm_survivors", ()))
            lever = set(rec.get("b_lever") or ())
            self._cache[scene] = r = (exact, rules, surv, bsurv, lever)
        return r

    def key_of(self, scene, prim):
        _, rest = scene_root_of(prim)
        if not rest:
            return None
        exact, rules, surv, bsurv, lever = self._rules(scene)
        root = rest[0]
        rel = "/".join(rest)
        for k, comp, _s in exact:                      # ⓐ 경험층 정확 일치(전체 경로)
            if rel == comp:
                return k
        if root.startswith("GKit"):                    # ⓓ
            for seg in rest[1:]:
                for tok, kk in GKIT_SUB:
                    if seg.startswith(tok):
                        return kk
            return "Gk"
        for depth, seg in enumerate(rest):
            blk = max((len(b) for b in LEX_BLOCK if seg.startswith(b)), default=0)
            best = None
            for k, p, s in rules:
                if not seg.startswith(p):
                    continue
                if depth == 0 and len(p) <= blk:
                    continue                           # ⓑ block 이 이긴다
                # 강등 판정은 **루트 수준 매칭에만** 적용한다. 생존 집합이 루트
                # 단위라서, 더 깊은 세그먼트에서 잡힌 구체적 매칭
                # (`EastExit/Nosing/Nose_20`)까지 죽이면 안 된다.
                if depth == 0 and s not in self.EXEMPT and root in surv:
                    self.demoted[f"{scene}/{root}|D"] += 1
                    continue                           # ⓒ D팔 생존 강등
                if depth == 0 and s not in self.EXEMPT and k in lever \
                        and root in bsurv:
                    self.demoted[f"{scene}/{root}|lever:{k}"] += 1
                    continue                           # ⓒ' 레버 모순 강등
                if best is None or len(p) > len(best[1]):
                    best = (k, p)
            if best is not None:
                return best[0]
            if depth >= 2:
                break
        return None


# --------------------------------------------------------------------------
# STAGE scan — 프레임별 단서 면적/개수
# --------------------------------------------------------------------------
def _load_prim_areas(f):
    z = np.load(f, allow_pickle=True)
    a = z["idseg"]
    lab = json.loads(str(z["idToLabels"]))
    ids, cnt = np.unique(a, return_counts=True)
    out = {}
    for i, c in zip(ids, cnt):
        p = lab.get(str(i))
        if p is None:
            continue
        out[p] = out.get(p, 0) + int(c)
    return out, int(a.size)


_G = {}


def _init_worker(attrib):
    _G["att"] = Attributor(attrib)
    ns = {}
    for sc, rec in attrib["scenes"].items():
        v = set()
        for k, prefs in rec.get("prefix", {}).items():
            for pp in prefs:
                if rec.get("prefix_src", {}).get(k, {}).get(pp) == "declared":
                    v.add(pp)
        if v:
            ns[sc] = v
    _G["ns"] = ns


def _obj_id(scene, prim, ns):
    """단서 **개체**의 식별자.

    두 세대의 명명 관례가 다르다 — 정본 33씬은 설치물을 씬 루트에 직접 놓고
    (`Bench_4`·`Rail_0`), 신규 씬은 cue 네임스페이스 아래에 모은다
    (`Dress/Bench_0`·`Rail/TopRail`). 네임스페이스 세대에서는 **한 단 더** 내려가야
    같은 것을 센다. `ns` = 그 씬이 `GATED_ZONES` 로 선언한 네임스페이스 집합.
    """
    _, rest = scene_root_of(prim)
    if not rest:
        return None
    if rest[0] in ns or rest[0].startswith("GKit"):
        return "/".join(rest[:2])
    return rest[0]


def _scan_one(job):
    """job = (path, scene, arm, band, round, split, stem)"""
    path, scene, arm, band, rnd, split, stem = job
    att = _G["att"]
    ns = _G["ns"].get(scene, set())
    try:
        areas, npx = _load_prim_areas(path)
    except Exception as e:                                    # noqa: BLE001
        return dict(err=str(e), path=path)
    per_key = collections.Counter()
    objs = collections.defaultdict(set)
    prims = {}
    for p, c in areas.items():
        k = att.key_of(scene, p)
        if k is None:
            continue
        per_key[k] += c
        objs[k].add(_obj_id(scene, p, ns))
        prims[p] = c
    tot = int(sum(per_key.values()))
    allobj = set()
    for v in objs.values():
        allobj |= v
    return dict(path=os.path.relpath(path, REPO), scene=scene, arm=arm, band=band,
                round=rnd, split=split, stem=stem, npx=npx,
                area=dict(per_key), area_total=tot,
                n_obj=len(allobj),
                n_grp=len({group_of(c) for c in allobj}),
                n_obj_key={k: len(v) for k, v in objs.items()},
                prims={p: c for p, c in sorted(prims.items(), key=lambda x: -x[1])[:15]})


def _stale_map_w1d():
    """W1-D stale 152컷: `variation.json` 의 `idseg_fetch == 't0'` 로 기계 판정."""
    stale = set()
    for rnd, _band in D_ROUNDS:
        for vf in glob.glob(os.path.join(DATA, rnd, "*", "*", "variation.json")):
            try:
                d = json.load(open(vf, encoding="utf-8"))
            except Exception:
                continue
            sc = d.get("scene")
            for c in d.get("cuts", []):
                if c.get("idseg_fetch") == "t0":
                    stale.add((rnd, sc, os.path.splitext(c["file"])[0]))
    return stale


def _backfill_ok():
    """A팔 백필: 설치 원장이 있고 `idseg_fetch=='orch'` 인 컷만 채택."""
    ok = set()
    ledger = []
    for rnd, _b in A_ROUNDS:
        for lf in glob.glob(os.path.join(DATA, rnd, "*", "*", "idseg_backfill.json")):
            try:
                d = json.load(open(lf, encoding="utf-8"))
            except Exception:
                continue
            sc = d.get("scene")
            ledger.append(dict(round=rnd, scene=sc, band=d.get("band"),
                               n=len(d.get("cuts", []))))
            for c in d.get("cuts", []):
                if c.get("idseg_fetch") in STRICT_FETCH:
                    ok.add((rnd, sc, os.path.splitext(c["file"])[0]))
    return ok, ledger


def _probe_strict_map(stamps):
    """프로브 라운드: `variation.json` 이 `idseg_fetch=='orch'` 인 컷만."""
    ok, bad = set(), 0
    for st in stamps:
        for vf in glob.glob(os.path.join(DATA, st, "*", "*", "variation.json")):
            try:
                d = json.load(open(vf, encoding="utf-8"))
            except Exception:
                continue
            sc = d.get("scene")
            rnd = vf.split(os.sep)[-4]
            for c in d.get("cuts", []):
                stem = os.path.splitext(c["file"])[0]
                if c.get("idseg_fetch") in STRICT_FETCH:
                    ok.add((rnd, sc, stem))
                else:
                    bad += 1
    return ok, bad


# ---- 라벨 색인 ------------------------------------------------------------
BAND_TOKEN = {"boost_h": "h", "boost_e": "e", "boost_e2": "e2"}


def _split_key(k):
    """`on/scene09/L0__s20260820__0000.png::boost_e` → ('on','scene09','L0__…','e')"""
    band = "base"
    if "::" in k:
        k, tok = k.split("::", 1)
        band = BAND_TOKEN.get(tok, tok)
    side, scene, fn = k.split("/", 2)
    return side, scene, os.path.splitext(fn)[0], band


def _haz(rec):
    pg = rec.get("polar_gt") or []
    return 1 if any(pg) else 0


def build_label_index():
    """(arm, scene, band, stem) → dict(hazard, n_cells, tier, src)."""
    idx, prov = {}, []

    # ---- A팔: 교정 GT 정본 -------------------------------------------------
    man = json.load(open(os.path.join(V3, "dataset_manifest_v2corr.json"),
                        encoding="utf-8"))
    nA = 0
    for f in man["frames"]:
        if f.get("toggle_state") != "on":
            continue
        _s, scene, stem, band = _split_key(f["frame_id"])
        idx[("A", scene, band, stem)] = dict(
            hazard=_haz(f), n_cells=int(sum(f.get("polar_gt") or [])),
            tier=f.get("tier"), src="dataset_manifest_v2corr.json")
        nA += 1
    prov.append(dict(arm="A", file="dataset_manifest_v2corr.json", n=nA,
                     note="교정 GT 정본(v2corr) · on 측"))

    # ---- B팔: W1-B / W1-B2 게이트 라벨 ------------------------------------
    for fn, tag in (("w1b_B.json", "B"), ("w1b2_B.json", "B2"),
                    ("w1b3_B.json", "B3")):
        if not os.path.exists(os.path.join(ANN, fn)):
            continue
        d = json.load(open(os.path.join(ANN, fn), encoding="utf-8"))
        n = 0
        for k, v in d["frames"].items():
            side, scene, stem, band = _split_key(k)
            if side != "on":
                continue
            # B2 씬은 B2 라벨이, 나머지는 B 라벨이 정본.
            if b_tree_of(scene) != tag:
                continue
            idx[("B", scene, band, stem)] = dict(
                hazard=_haz(v), n_cells=int(sum(v.get("polar_gt") or [])),
                tier=v.get("tier_strict"), src=fn)
            n += 1
        prov.append(dict(arm="B", file=fn, n=n,
                         note="z_off = D팔 (cue-대칭) · W1B §8.3"))

    # ---- D팔: base 밴드은 실측 라벨, h/e/e2 는 VG-02 전음성 근거 ------------
    d = json.load(open(os.path.join(ANN, "w1d_base.json"), encoding="utf-8"))
    n = 0
    for k, v in d["frames"].items():
        side, scene, stem, band = _split_key(k)
        if side != "on":
            continue
        idx[("D", scene, band, stem)] = dict(
            hazard=_haz(v), n_cells=int(sum(v.get("polar_gt") or [])),
            tier=v.get("tier_strict"), src="w1d_base.json")
        n += 1
    prov.append(dict(arm="D", file="w1d_base.json", n=n,
                     note="on 측 = D팔 base 라운드 (off = 260819_main_off)"))

    # ---- C팔: **사양 상수 전음성** (AC-INSTR-1 C3-2) -----------------------
    # 라벨러 출력을 쓰지 않는다. C 의 polar_gt 는 0 으로 고정이고 그 자리에 어떤
    # 라벨러 행도 들어가지 않는다(W1C_REPORT §3.2 · ACCOUNTING §4.10).
    # 여기서는 hazard=0 만 필요하므로 디스크의 컷 목록에서 직접 색인을 만든다.
    nC = 0
    for rnd, band in C_ROUNDS:
        for vf in glob.glob(os.path.join(DATA, rnd, "*", "*", "variation.json")):
            try:
                d = json.load(open(vf, encoding="utf-8"))
            except Exception:
                continue
            sc = d.get("scene")
            for c in d.get("cuts", []):
                stem = os.path.splitext(c["file"])[0]
                idx[("C", sc, band, stem)] = dict(
                    hazard=0, n_cells=0, tier="none_in_fov",
                    src="spec_constant_all_negative (AC-INSTR-1 C3-2)")
                nC += 1
    # 무낙차 4씬 — v2 on팔이 그대로 C팔 (계획 §1.0). 재활용분이므로 A 라운드에 산다.
    for f in man["frames"]:
        if f.get("toggle_state") != "on":
            continue
        _s, scene, stem, band = _split_key(f["frame_id"])
        if scene in NODROP_SCENES:
            idx[("C", scene, band, stem)] = dict(
                hazard=_haz(f), n_cells=int(sum(f.get("polar_gt") or [])),
                tier=f.get("tier"),
                src="dataset_manifest_v2corr.json (무낙차 on팔 = C팔 재활용)")
            nC += 1
    prov.append(dict(arm="C", file="(spec constant + v2corr 무낙차 재활용)", n=nC,
                     note="C GT = 사양 상수 전음성 · 라벨러 출력 미채택 (C3-2)"))

    # ---- W2 (sceneH6·H7) — 훈련측 val 씬. 4팔 전부 P1 에 들어간다 ---------
    for tag, band in (("base", "w2base"), ("h", "w2h"), ("h2", "w2h2")):
        for pair, (on_arm, off_arm) in (("ac", ("A", "C")), ("bd", ("B", "D"))):
            p = os.path.join(ANN, f"w2_{tag}_{pair}_labels.json")
            if not os.path.exists(p):
                continue
            d = json.load(open(p, encoding="utf-8"))
            n = 0
            for k, v in d["frames"].items():
                side, scene, stem, _b = _split_key(k)
                arm = on_arm if side == "on" else off_arm
                if arm in ("C", "D"):        # 사양 상수 (W2 §3.5 로 반증 실패)
                    idx[(arm, scene, band, stem)] = dict(
                        hazard=0, n_cells=0, tier="none_in_fov",
                        src="spec_constant_all_negative (AC-INSTR-1 C3-2)")
                else:
                    idx[(arm, scene, band, stem)] = dict(
                        hazard=_haz(v), n_cells=int(sum(v.get("polar_gt") or [])),
                        tier=v.get("tier_strict"), src=f"w2_{tag}_{pair}_labels.json")
                n += 1
            prov.append(dict(arm=f"{on_arm}/{off_arm}", file=f"w2_{tag}_{pair}_labels.json",
                             n=n, note=f"W2 sceneH6·H7 · band={band}"))
    return idx, prov


def build_probe_label_index(specs):
    idx, prov = {}, []
    for sp in specs:
        for arm, (fn, side) in sp["labels"].items():
            p = os.path.join(ANN, fn)
            if not os.path.exists(p):
                prov.append(dict(group=sp["group"], arm=arm, file=fn, n=0,
                                 note="MISSING"))
                continue
            d = json.load(open(p, encoding="utf-8"))
            n = 0
            for k, v in d["frames"].items():
                s, scene, stem, band = _split_key(k)
                if s != side or scene not in sp["scenes"]:
                    continue
                idx[(sp["group"], arm, scene, stem)] = dict(
                    hazard=_haz(v), n_cells=int(sum(v.get("polar_gt") or [])),
                    tier=v.get("tier_strict"), src=fn)
                n += 1
            prov.append(dict(group=sp["group"], arm=arm, file=fn, side=side, n=n))
    return idx, prov


def collect_jobs():
    """스캔 대상 목록 + 제외 회계."""
    jobs, acct = [], collections.Counter()
    bf_ok, bf_ledger = _backfill_ok()
    stale = _stale_map_w1d()

    def add(path, scene, arm, band, rnd, group=None):
        split = path.split(os.sep)[-3]
        stem = os.path.basename(path)[: -len(".idseg.npz")]
        jobs.append((path, scene, arm, band, rnd, split, stem))

    # A팔
    for rnd, band in A_ROUNDS:
        for f in sorted(glob.glob(os.path.join(DATA, rnd, "*", "*", "*.idseg.npz"))):
            sc = os.path.basename(os.path.dirname(f))
            stem = os.path.basename(f)[: -len(".idseg.npz")]
            if (rnd, sc, stem) not in bf_ok:
                acct["A_skip_not_in_backfill_ledger"] += 1
                continue
            add(f, sc, "A", band, rnd)
            acct["A"] += 1
    # B팔 (B2 우선 · W1B2 §7)
    for rounds, tag in ((B3_ROUNDS, "B3"), (B2_ROUNDS, "B2"), (B_ROUNDS, "B")):
        for rnd, band in rounds:
            for f in sorted(glob.glob(os.path.join(DATA, rnd, "*", "*", "*.idseg.npz"))):
                sc = os.path.basename(os.path.dirname(f))
                if b_tree_of(sc) != tag:
                    acct[f"{tag}_skip_not_canonical"] += 1
                    continue
                add(f, sc, "B", band, rnd)
                acct["B"] += 1
    # C팔 (W1-C · 전 컷 fetch=orch)
    for rnd, band in C_ROUNDS:
        for f in sorted(glob.glob(os.path.join(DATA, rnd, "*", "*", "*.idseg.npz"))):
            sc = os.path.basename(os.path.dirname(f))
            add(f, sc, "C", band, rnd)
            acct["C"] += 1
    # D팔 (stale 제외)
    for rnd, band in D_ROUNDS:
        for f in sorted(glob.glob(os.path.join(DATA, rnd, "*", "*", "*.idseg.npz"))):
            sc = os.path.basename(os.path.dirname(f))
            stem = os.path.basename(f)[: -len(".idseg.npz")]
            if (rnd, sc, stem) in stale:
                acct["D_skip_stale"] += 1
                continue
            add(f, sc, "D", band, rnd)
            acct["D"] += 1
    # W2 (sceneH6·H7 · 4팔) — 훈련 코퍼스 val 공급 씬
    for stamp, band in W2_ROUNDS:
        for arm in "ABCD":
            rnd = f"{stamp}_{arm}"
            for f in sorted(glob.glob(os.path.join(DATA, rnd, "*", "*", "*.idseg.npz"))):
                sc = os.path.basename(os.path.dirname(f))
                if sc not in W2_SCENES:
                    continue
                add(f, sc, arm, band, rnd)
                acct[f"W2_{arm}"] += 1
    return jobs, acct, bf_ledger, len(stale)


def collect_probe_jobs(specs):
    jobs = []
    stamps = set()
    for sp in specs:
        if "arms" in sp:
            for a in sp["arms"]:
                stamps.add(f"{sp['stamp']}_{a}")
        else:
            for a in "ABCD":
                stamps.add(f"{sp['stamp']}_{a}")
    ok, nbad = _probe_strict_map(stamps)
    for sp in specs:
        arms = list(sp["arms"]) if "arms" in sp else ["A", "B", "C", "D"]
        for a in arms:
            rnd = f"{sp['stamp']}_{a}"
            for sc in sp["scenes"]:
                for f in sorted(glob.glob(os.path.join(DATA, rnd, "*", sc, "*.idseg.npz"))):
                    stem = os.path.basename(f)[: -len(".idseg.npz")]
                    if (rnd, sc, stem) not in ok:
                        continue
                    split = f.split(os.sep)[-3]
                    jobs.append((f, sc, a, sp["group"], rnd, split, stem))
    return jobs, nbad


def volatile_rounds(paths, window_s=1800):
    """스캔 직전 `window_s` 안에 쓰인 라운드 = **렌더 중일 수 있다**. 기록만 한다."""
    now = time.time()
    latest = {}
    for p in paths:
        rnd = p.split(os.sep)[-4] if os.sep in p else p
        try:
            m = os.path.getmtime(p)
        except OSError:
            continue
        if m > latest.get(rnd, 0):
            latest[rnd] = m
    return {r: time.strftime("%F %T", time.localtime(m))
            for r, m in sorted(latest.items()) if now - m < window_s}


def run_scan(attrib, workers=12):
    from concurrent.futures import ProcessPoolExecutor
    t0 = time.time()
    jobs, acct, bf_ledger, n_stale = collect_jobs()
    pjobs, n_probe_bad = collect_probe_jobs(PROBE_PRIMARY + PROBE_H67 + PROBE_SECONDARY)
    log(f"[scan] corpus jobs={len(jobs)} · probe jobs={len(pjobs)} · workers={workers}")
    res, pres = [], []
    with ProcessPoolExecutor(max_workers=workers,
                             initializer=_init_worker, initargs=(attrib,)) as ex:
        for i, r in enumerate(ex.map(_scan_one, jobs, chunksize=8)):
            res.append(r)
            if (i + 1) % 500 == 0:
                log(f"   corpus {i+1}/{len(jobs)}  {time.time()-t0:.0f}s")
        for i, r in enumerate(ex.map(_scan_one, pjobs, chunksize=8)):
            pres.append(r)
            if (i + 1) % 200 == 0:
                log(f"   probe  {i+1}/{len(pjobs)}  {time.time()-t0:.0f}s")
    vol = volatile_rounds([j[0] for j in jobs + pjobs])
    if vol:
        log(f"   [warn] 최근 30분 안에 쓰인 라운드(렌더 중일 수 있음): {vol}")
    errs = [r for r in res + pres if "err" in r]
    out = dict(doc="cue_extent_frames", version="1.0",
               generated=time.strftime("%Y-%m-%dT%H:%M:%S"),
               accounting=dict(acct), n_stale_w1d=n_stale,
               backfill_ledger=bf_ledger, n_probe_nonstrict=n_probe_bad,
               errors=errs[:20], n_errors=len(errs), volatile_rounds=vol,
               corpus=[r for r in res if "err" not in r],
               probe=[r for r in pres if "err" not in r])
    os.makedirs(LOGS, exist_ok=True)
    p = os.path.join(LOGS, "cue_extent_frames.json")
    json.dump(out, open(p, "w", encoding="utf-8"), ensure_ascii=False)
    log(f"[scan] done {time.time()-t0:.0f}s · corpus={len(out['corpus'])} "
        f"probe={len(out['probe'])} errors={len(errs)} → {os.path.relpath(p, REPO)}")
    return out


# --------------------------------------------------------------------------
# 통계
# --------------------------------------------------------------------------
def pearson(x, y):
    n = len(x)
    if n < 3:
        return None
    mx, my = sum(x) / n, sum(y) / n
    sx = math.sqrt(sum((a - mx) ** 2 for a in x))
    sy = math.sqrt(sum((b - my) ** 2 for b in y))
    if sx == 0 or sy == 0:
        return None
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy)


def point_biserial(g, v):
    """g: 0/1 리스트, v: 연속. 점이연 = 0/1 과의 피어슨 (동일 정의)."""
    return pearson([float(a) for a in g], [float(b) for b in v])


def cliffs_delta(a, b):
    """분포무관 효과크기. |δ| 0.147/0.33/0.474 = small/medium/large (Romano 2006)."""
    if not a or not b:
        return None
    a = sorted(a)
    b = sorted(b)
    import bisect
    gt = lt = 0
    for x in b:
        gt += bisect.bisect_left(a, x)          # a < x
        lt += len(a) - bisect.bisect_right(a, x)  # a > x
    # δ = P(a>b) − P(a<b)
    n = len(a) * len(b)
    return (lt - gt) / n


def perm_null(g, v, n=2000, seed=20260824, clusters=None):
    """귀무 |r| 분포. clusters 가 주어지면 **클러스터(씬) 내 셔플** —
    씬 구성이 만드는 구조는 유지하고 위험-면적 결속만 끊는다."""
    rng = random.Random(seed)
    base = point_biserial(g, v)
    out = []
    if clusters is None:
        gg = list(g)
        for _ in range(n):
            rng.shuffle(gg)
            r = point_biserial(gg, v)
            if r is not None:
                out.append(abs(r))
    else:
        byc = collections.defaultdict(list)
        for i, c in enumerate(clusters):
            byc[c].append(i)
        gg = list(g)
        for _ in range(n):
            for c, ix in byc.items():
                vals = [g[i] for i in ix]
                rng.shuffle(vals)
                for i, val in zip(ix, vals):
                    gg[i] = val
            r = point_biserial(gg, v)
            if r is not None:
                out.append(abs(r))
    out.sort()
    if not out:
        return None
    def q(p):
        return out[min(len(out) - 1, int(p * len(out)))]
    p_emp = (sum(1 for x in out if x >= abs(base or 0.0)) + 1) / (len(out) + 1) \
        if base is not None else None
    return dict(n=len(out), q50=round(q(0.50), 4), q95=round(q(0.95), 4),
                q99=round(q(0.99), 4), max=round(out[-1], 4), p_emp=round(p_emp, 4)
                if p_emp is not None else None)


def describe(v):
    if not v:
        return dict(n=0)
    s = sorted(v)
    n = len(s)
    mean = sum(s) / n
    sd = math.sqrt(sum((x - mean) ** 2 for x in s) / (n - 1)) if n > 1 else 0.0
    def q(p):
        return s[min(n - 1, int(p * n))]
    return dict(n=n, mean=round(mean, 2), sd=round(sd, 2), p10=round(q(0.10), 2),
                med=round(q(0.50), 2), p90=round(q(0.90), 2), max=round(s[-1], 2))


# --------------------------------------------------------------------------
# STAGE analyze
# --------------------------------------------------------------------------
def analyze(frames, attrib, args):
    t0 = time.time()
    labidx, labprov = build_label_index()
    plabidx, plabprov = build_probe_label_index(
        PROBE_PRIMARY + PROBE_H67 + PROBE_SECONDARY)

    # ---- 프레임 레코드에 GT 를 붙인다 -------------------------------------
    rows, unlabeled = [], collections.Counter()
    n_vg02 = 0
    for r in frames["corpus"]:
        L = labidx.get((r["arm"], r["scene"], r["band"], r["stem"]))
        if L is None and r["arm"] == "D":
            # W1-D 의 h/e/e2 밴드는 라벨링되지 않았다(w1d_label.sh 주석). 그러나
            # **VG-02 가 4라운드 38/38 유닛 전부 all-negative** 임을 실측했다
            # (w1d_verify.json:vg_02.n_all_negative = 38). D팔은 위험 기하가 없으므로
            # 위험 라벨은 0이다 — 그 실측을 출처로 명시해 채운다.
            L = dict(hazard=0, n_cells=0, tier="off",
                     src="VG-02 all-negative 38/38 (w1d_verify.json)")
            n_vg02 += 1
        if L is None:
            unlabeled[(r["arm"], r["band"])] += 1
            continue
        rr = dict(r)
        rr.update(hazard=L["hazard"], n_cells=L["n_cells"], tier=L["tier"],
                  gt_src=L["src"], pop="P1")
        rows.append(rr)
    prows = []
    for r in frames["probe"]:
        grp = r["band"]                      # probe 잡에서 band 자리에 group 을 넣었다
        L = plabidx.get((grp, r["arm"], r["scene"], r["stem"]))
        if L is None:
            unlabeled[("probe:" + grp, r["arm"])] += 1
            continue
        rr = dict(r)
        rr.update(group=grp, hazard=L["hazard"], n_cells=L["n_cells"],
                  tier=L["tier"], gt_src=L["src"], pop="P2")
        prows.append(rr)

    def area_frac(r, key=None):
        if key is None:
            return r["area_total"] / FRAME_PX * 100.0
        return r["area"].get(key, 0) / FRAME_PX * 100.0

    res = dict(
        doc="cue_extent_audit", version="1.0",
        authority="DECISIONS D82 ⓒ (룩체크 R7) · ACCOUNTING §4.9-3 (|r| 보고 규약)",
        generated=time.strftime("%Y-%m-%dT%H:%M:%S"),
        frame_px=FRAME_PX,
        instrument=dict(
            source=".idseg.npz (instance_id_segmentation · 프림 경로 디코드)",
            area_unit="픽셀 · 프레임 대비 % 병기",
            attribution="declared(GATED_ZONES) > empirical(팔 차분) > lexical(prims2+전역토큰)",
            blind_keys=["T"],
            blind_reason="cue_material_break 는 24/32 씬에서 재질 재바인딩 전용 — "
                         "프림 집합 불변이므로 ID 마스크가 원리적으로 볼 수 없다 "
                         "(CUE_COVERAGE §0-3 · W1B2 §2.2 ③)."),
        scan_accounting=frames["accounting"],
        n_stale_w1d_excluded=frames["n_stale_w1d"],
        label_provenance=labprov, probe_label_provenance=plabprov,
        unlabeled=dict((str(k), v) for k, v in unlabeled.items()),
        d_arm_label_by_vg02=n_vg02,
    )

    # ======================================================================
    # 1. 헤드라인 — as-built 코퍼스 위 점이연 r
    # ======================================================================
    keys_present = sorted({k for r in rows for k in r["area"]},
                          key=lambda k: list(Attributor.ORDER).index(k)
                          if k in Attributor.ORDER else 99)
    g = [r["hazard"] for r in rows]
    scl = [r["scene"] for r in rows]
    tot = [area_frac(r) for r in rows]
    cnt = [r["n_obj"] for r in rows]
    grp = [r["n_grp"] for r in rows]

    marg = dict(n=len(rows),
                hazard_present=sum(g), hazard_absent=len(g) - sum(g),
                p_hazard=round(sum(g) / len(g), 4) if rows else None,
                by_arm=dict(collections.Counter(r["arm"] for r in rows)),
                by_arm_hazard={f"{a}:{h}": n for (a, h), n in
                               sorted(collections.Counter(
                                   (r["arm"], r["hazard"]) for r in rows).items())},
                n_scenes=len({r["scene"] for r in rows}),
                arms_missing=[])

    def stat_block(vals, label, do_perm=True):
        r = point_biserial(g, vals)
        a = [v for v, h in zip(vals, g) if h == 1]
        b = [v for v, h in zip(vals, g) if h == 0]
        d = dict(metric=label, r_pb=round(r, 4) if r is not None else None,
                 abs_r=round(abs(r), 4) if r is not None else None,
                 cliffs_delta=round(cliffs_delta(a, b), 4)
                 if (a and b) else None,
                 hazard=describe(a), no_hazard=describe(b))
        if do_perm and a and b:
            d["null_within_scene"] = perm_null(g, vals, n=args.perm, clusters=scl)
            d["null_free"] = perm_null(g, vals, n=args.perm, clusters=None)
        return d

    head = dict(
        marginals=marg,
        total_area_pct=stat_block(tot, "cue_area_total (% of frame)"),
        obj_count=stat_block(cnt, "cue_obj_count (distinct prim roots)"),
        grp_count=stat_block(grp, "cue_group_count (installations)"),
        per_key={}, constant_keys=[], blind_keys=[])

    for k in keys_present:
        vals = [area_frac(r, k) for r in rows]
        # 그 키를 **선언한 씬**만 모집단으로 (§4.9-3 ②: 토글 가능 키 한정의 면적판)
        cue = KEY2CUE.get(k)
        if cue is None:                       # `Gk` = GKit 미분해 버킷
            sel = [i for i, r in enumerate(rows) if r["area"].get(k)]
        else:
            sel = [i for i, r in enumerate(rows)
                   if cue in attrib["scenes"].get(r["scene"], {}).get("defaults", {})]
        if len(sel) < 30 or max(vals[i] for i in sel) == 0:
            head["constant_keys"].append(dict(
                key=k, cue=KEYNAME[k], n_frames=len(sel),
                reason="면적 상수 0 (프림 미생성 또는 씬 부족)"))
            continue
        gs = [g[i] for i in sel]
        vs = [vals[i] for i in sel]
        ss = [scl[i] for i in sel]
        r = point_biserial(gs, vs)
        a = [v for v, h in zip(vs, gs) if h == 1]
        b = [v for v, h in zip(vs, gs) if h == 0]
        head["per_key"][k] = dict(
            cue=KEYNAME[k], n=len(sel),
            n_scenes=len({rows[i]["scene"] for i in sel}),
            r_pb=round(r, 4) if r is not None else None,
            abs_r=round(abs(r), 4) if r is not None else None,
            cliffs_delta=round(cliffs_delta(a, b), 4) if (a and b) else None,
            hazard=describe(a), no_hazard=describe(b),
            null_within_scene=perm_null(gs, vs, n=args.perm, clusters=ss)
            if (a and b) else None)
    head["blind_keys"] = [dict(
        key="T", cue="material_break",
        reason="재질 재바인딩 전용 — ID 마스크 불변. 면적 r 은 정의상 0이며 "
               "이 계기로는 측정 불가. 존재 |r| 쪽 값(W1-B2 0.0692)이 유일한 근거다.")]
    res["headline_P1"] = head

    # ---- P1 하위 모집단 — D83 과 사과 대 사과로 읽기 위한 분해 -------------
    # D83 ①의 0.4135 는 "라이브러리 22씬 · C팔 0" 상태의 수치다. C 가 들어온 뒤의
    # 같은 모집단(P1a)과, H6·H7 까지 포함한 실제 훈련 코퍼스(P1b=전체)를 나란히 낸다.
    def _sub(sel_rows, label, note):
        if len(sel_rows) < 30:
            return dict(label=label, n=len(sel_rows), note=note + " (n<30 · 미산출)")
        gg = [r["hazard"] for r in sel_rows]
        vv = [area_frac(r) for r in sel_rows]
        ss = [r["scene"] for r in sel_rows]
        rr = point_biserial(gg, vv)
        a = [v for v, h in zip(vv, gg) if h == 1]
        b = [v for v, h in zip(vv, gg) if h == 0]
        return dict(label=label, note=note, n=len(sel_rows),
                    n_scenes=len(set(ss)), hazard_present=sum(gg),
                    by_arm=dict(collections.Counter(r["arm"] for r in sel_rows)),
                    r_pb=round(rr, 4) if rr is not None else None,
                    abs_r=round(abs(rr), 4) if rr is not None else None,
                    cliffs_delta=round(cliffs_delta(a, b), 4) if (a and b) else None,
                    hazard=describe(a), no_hazard=describe(b),
                    null_within_scene=perm_null(gg, vv, n=args.perm, clusters=ss)
                    if (a and b) else None)

    lib = [r for r in rows if r["scene"] not in W2_SCENES]
    res["headline_P1_sub"] = dict(
        P1a_lib_22scenes=_sub(lib, "P1a · 기존 라이브러리 22씬 (A/B/C/D)",
                              "D83 ①의 0.4135 와 같은 씬 모집단 · C팔이 실물로 들어왔다"),
        P1a_lib_noC=_sub([r for r in lib if r["arm"] != "C"],
                         "P1a⁻ · 같은 씬 · C팔 제외 (D83 재현 대조)",
                         "D83 측정 당시 상태의 재현 — 0.4135 가 나와야 한다"),
        P1b_full=_sub(rows, "P1b · v3 훈련 코퍼스 전체 (라이브러리 + H6·H7)",
                      "실제로 학습에 들어가는 모집단"),
        d83_reference=dict(as_built_then=0.4135, kappa_projection_then=0.1495,
                           null_q99_then=0.1009,
                           source="CUE_EXTENT_AUDIT.md 승용 요약 1·2 (D83 ①)"))

    # 팔 수준 대조 (설계 수준 위험 = 팔) — 프레임 GT 와 나란히 인쇄
    garm = [1 if r["arm"] in ("A", "B") else 0 for r in rows]
    r_arm = point_biserial(garm, tot)
    res["headline_P1"]["arm_level_check"] = dict(
        note="설계 수준(팔) 위험 × 총 단서 면적 — 프레임 GT 판정과 나란히 읽는다",
        r_pb=round(r_arm, 4) if r_arm is not None else None,
        by_arm={a: describe([area_frac(r) for r in rows if r["arm"] == a])
                for a in sorted({r["arm"] for r in rows})})

    # ======================================================================
    # 2. 밀도 대칭 — 위험 씬 A팔 vs N-cue 씬 cue팔 vs 신규 H 씬
    # ======================================================================
    def famof(sc):
        if sc in ("sceneN9", "sceneN11"):
            return "N-cue(new)"
        if sc.startswith("sceneN"):
            return "N-cue(legacy)"
        if sc in ("sceneH1", "sceneH2", "sceneH3", "sceneH6", "sceneH7"):
            return "H(new)"
        if sc == "sceneL1":
            return "L(new)"
        return "H(legacy-33)"

    sym = dict(note="cue 팔 = 단서가 살아 있는 팔. 위험 씬은 A팔, N-cue 씬은 "
                    "A·C 두 팔 모두 사실상 C팔(단서 有·위험 無 — run_n911_probe.sh §팔 사상)",
               groups={})
    buckets = collections.defaultdict(list)
    for r in rows:
        if r["arm"] == "A":
            buckets[("P1 A팔", famof(r["scene"]))].append(area_frac(r))
    for r in prows:
        if r["group"] in ("h12_r0", "n911_rev", "n911_rev2"):
            continue                          # 부차 라운드는 헤드라인 비산입
        if r["arm"] in ("A", "C"):
            buckets[(f"P2 {r['arm']}팔", famof(r["scene"]))].append(area_frac(r))
    for (lab, fam), v in sorted(buckets.items()):
        sym["groups"][f"{lab} · {fam}"] = describe(v)
    # 핵심 대조 두 개
    hazA = [area_frac(r) for r in prows
            if r["arm"] == "A" and famof(r["scene"]) == "H(new)"
            and r["group"] not in ("h12_r0",)]
    ncueA = [area_frac(r) for r in prows
             if r["arm"] in ("A", "C") and famof(r["scene"]) == "N-cue(new)"
             and r["group"] in P2_NCUE_GROUPS]
    legA = [area_frac(r) for r in rows if r["arm"] == "A"]
    sym["contrast"] = {}
    if hazA and ncueA:
        sym["contrast"]["Hnew_A_vs_Ncue_cuearm"] = dict(
            H=describe(hazA), N=describe(ncueA),
            ratio_mean=round((sum(hazA) / len(hazA)) / max(1e-9, sum(ncueA) / len(ncueA)), 3),
            cliffs_delta=round(cliffs_delta(hazA, ncueA), 4))
    if legA and ncueA:
        sym["contrast"]["legacy33_A_vs_Ncue_cuearm"] = dict(
            legacy=describe(legA), N=describe(ncueA),
            ratio_mean=round((sum(legA) / len(legA)) / max(1e-9, sum(ncueA) / len(ncueA)), 3),
            cliffs_delta=round(cliffs_delta(legA, ncueA), 4))
    if legA and hazA:
        sym["contrast"]["legacy33_A_vs_Hnew_A"] = dict(
            legacy=describe(legA), Hnew=describe(hazA),
            ratio_mean=round((sum(legA) / len(legA)) / max(1e-9, sum(hazA) / len(hazA)), 3),
            cliffs_delta=round(cliffs_delta(legA, hazA), 4))
    sym["pending"] = ["[08-24 해소] C 웨이브 착지 — C팔 816컷이 P1 에 들어왔다 (W1C §8.2)",
                      "[08-24 해소] P2 프로브를 W3 본렌더 as-built 로 교체 (D87)",
                      "[08-24] H6·H7 은 P2 프로브가 아니라 P1(훈련 코퍼스 val)로 이동 (W2)",
                      "B안 대기 3씬(H4·L2·N12) 미렌더 — 착지 시 --regen-hook"]
    res["density_symmetry"] = sym

    # P2 자체의 2×2 점이연 (신규 씬만 · 전 팔 존재)
    p2 = [r for r in prows if r["group"] in P2_PRIMARY_GROUPS]
    if p2:
        g2 = [r["hazard"] for r in p2]
        v2 = [area_frac(r) for r in p2]
        s2 = [r["scene"] for r in p2]
        rr = point_biserial(g2, v2)
        res["headline_P2"] = dict(
            n=len(p2), n_scenes=len({r["scene"] for r in p2}),
            hazard_present=sum(g2),
            by_arm=dict(collections.Counter(r["arm"] for r in p2)),
            r_pb=round(rr, 4) if rr is not None else None,
            abs_r=round(abs(rr), 4) if rr is not None else None,
            hazard=describe([v for v, h in zip(v2, g2) if h == 1]),
            no_hazard=describe([v for v, h in zip(v2, g2) if h == 0]),
            null_within_scene=perm_null(g2, v2, n=args.perm, clusters=s2))

    # ======================================================================
    # 3. 씬별 표 + 이상치
    # ======================================================================
    PRIMARY_G = P2_PRIMARY_GROUPS
    per_scene = {}
    bysc = collections.defaultdict(list)
    for r in rows:
        bysc[(r["scene"], r["arm"], "")].append(r)
    for r in prows:
        # P2 는 **라운드 세대별로 분리**한다 — rev/rev2/rev3·probe 를 한 칸에 섞으면
        # 같은 씬의 서로 다른 빌드가 평균돼 출처가 사라진다.
        bysc[(r["scene"], r["arm"], r["group"])].append(r)
    for (sc, arm, grp), rs in sorted(bysc.items()):
        d = dict(scene=sc, arm=arm, group=grp or None, family=famof(sc), n=len(rs),
                 pop=rs[0]["pop"],
                 primary=(not grp) or (grp in PRIMARY_G),
                 hazard_frames=sum(x["hazard"] for x in rs),
                 area_pct=describe([area_frac(x) for x in rs]),
                 obj=describe([float(x["n_obj"]) for x in rs]),
                 by_key={k: round(sum(x["area"].get(k, 0) for x in rs)
                                  / len(rs) / FRAME_PX * 100.0, 4)
                         for k in sorted({k for x in rs for k in x["area"]})})
        per_scene[f"{sc}|{arm}" + (f"|{grp}" if grp else "")] = d
    res["per_scene"] = per_scene

    # 이상치 — 같은 family·arm 안에서 로버스트 z (MAD)
    out_flags = []
    fam_arm = collections.defaultdict(list)
    for k, d in per_scene.items():
        if not d.get("primary"):
            continue                       # 부차 라운드는 이상치 판정에 넣지 않는다
        fam_arm[(d["family"], d["arm"])].append((k, d["area_pct"]["mean"]))
    for (fam, arm), items in sorted(fam_arm.items()):
        if len(items) < 4:
            continue
        vals = sorted(v for _, v in items)
        med = vals[len(vals) // 2]
        mad = sorted(abs(v - med) for v in vals)[len(vals) // 2]
        scale = 1.4826 * mad if mad > 0 else None
        for k, v in items:
            z = (v - med) / scale if scale else None
            if z is not None and abs(z) >= 3.5:
                out_flags.append(dict(key=k, family=fam, arm=arm, mean_area_pct=v,
                                      family_median=round(med, 3),
                                      robust_z=round(z, 2),
                                      direction="high" if z > 0 else "low"))
    res["outliers"] = dict(
        rule="같은 (family, arm) 안에서 씬 평균 단서면적의 로버스트 z = "
             "(x−median)/(1.4826·MAD), |z| ≥ 3.5",
        n=len(out_flags), flags=sorted(out_flags, key=lambda d: -abs(d["robust_z"])))

    # ======================================================================
    # 3b. 드라이버 분해 — 씬 하나를 빼면 헤드라인 r 이 얼마나 움직이는가
    # ======================================================================
    base_r = point_biserial(g, tot)
    drv = []
    for sc in sorted({r["scene"] for r in rows}):
        ix = [i for i, r in enumerate(rows) if r["scene"] != sc]
        if len({g[i] for i in ix}) < 2:
            continue
        rr = point_biserial([g[i] for i in ix], [tot[i] for i in ix])
        if rr is None:
            continue
        drv.append(dict(scene=sc, r_without=round(rr, 4),
                        delta=round(rr - base_r, 4),
                        n=len(rows) - len(ix)))
    drv.sort(key=lambda d: d["delta"])
    res["drivers"] = dict(
        base_r=round(base_r, 4),
        note="씬 하나를 모집단에서 뺐을 때의 r. delta 가 크게 **음수**면 그 씬이 "
             "상관을 만들고 있다(빼면 r 이 내려간다).",
        top_makers=drv[:8], top_dampers=drv[-5:])

    # 합본 (P1 + P2 primary) — 두 모집단이 서로 반대 방향으로 당긴다
    comb = rows + [r for r in prows
                   if r["group"] in P2_PRIMARY_GROUPS]
    gc = [r["hazard"] for r in comb]
    vc = [area_frac(r) for r in comb]
    sc_ = [r["scene"] for r in comb]
    rc = point_biserial(gc, vc)
    res["combined_P1P2"] = dict(
        n=len(comb), hazard_present=sum(gc),
        r_pb=round(rc, 4) if rc is not None else None,
        hazard=describe([v for v, h in zip(vc, gc) if h == 1]),
        no_hazard=describe([v for v, h in zip(vc, gc) if h == 0]),
        null_within_scene=perm_null(gc, vc, n=args.perm, clusters=sc_),
        note="P1(정본 33씬 · C 결측)은 +방향, P2(신규 씬 · 2×2 완비)는 −방향이다. "
             "합본은 두 힘의 현재 합력이지 어느 한쪽의 설계 진단이 아니다.")

    # ======================================================================
    # 3c. C 웨이브 **착지 검증** — 투영이 맞았는가 (구 3c "투영" 절의 후속)
    # ======================================================================
    #   [08-24] C팔이 실물로 들어왔다(816컷). 이 절은 더 이상 투영이 아니라
    #   **투영 대 실측의 대조**다. 남은 투영은 아직 세그가 없는 자리
    #   (무낙차 4씬 C 재활용 96컷 · 격리분)뿐이다.
    kA = [area_frac(r) for r in prows if r["arm"] == "A"
          and r["group"] in P2_PRIMARY_GROUPS]
    kC = [area_frac(r) for r in prows if r["arm"] == "C"
          and r["group"] in P2_PRIMARY_GROUPS]
    # 코퍼스 자체에서 잰 κ (라이브러리 22씬 · 같은 씬의 A팔·C팔)
    cA = collections.defaultdict(list)
    cC = collections.defaultdict(list)
    for r in rows:
        if r["scene"] in W2_SCENES:
            continue
        if r["arm"] == "A":
            cA[r["scene"]].append(area_frac(r))
        elif r["arm"] == "C":
            cC[r["scene"]].append(area_frac(r))
    both = sorted(set(cA) & set(cC))
    kappa_corpus = None
    kappa_by_scene = {}
    if both:
        mA = sum(sum(cA[s]) for s in both) / max(1, sum(len(cA[s]) for s in both))
        mC = sum(sum(cC[s]) for s in both) / max(1, sum(len(cC[s]) for s in both))
        kappa_corpus = mC / max(1e-9, mA)
        for s in both:
            a = sum(cA[s]) / len(cA[s])
            c = sum(cC[s]) / len(cC[s])
            kappa_by_scene[s] = dict(A_mean=round(a, 3), C_mean=round(c, 3),
                                     kappa=round(c / max(1e-9, a), 4))
    kappa = (sum(kC) / len(kC)) / max(1e-9, sum(kA) / len(kA)) if (kA and kC) else None
    plan = json.load(open(os.path.join(V3, "render_plan_v3.json"), encoding="utf-8"))
    cplan = {s["scene"]: s.get("arms", {}).get("C", {}).get("frames", 0)
             for s in plan["scenes"]}
    proj_g, proj_v, proj_s = list(g), list(tot), list(scl)
    n_syn = 0
    if kappa:
        byscene = collections.defaultdict(list)
        for r in rows:
            if r["arm"] == "A":
                byscene[r["scene"]].append(area_frac(r))
        have_C = collections.Counter(r["scene"] for r in rows if r["arm"] == "C")
        for sc, vals in byscene.items():
            want = cplan.get(sc, 0) - have_C.get(sc, 0)   # **결측분만** 채운다
            if want <= 0 or not vals:
                continue
            for i in range(want):
                proj_g.append(0)
                proj_v.append(vals[i % len(vals)] * kappa)
                proj_s.append(sc)
                n_syn += 1
    rproj = point_biserial(proj_g, proj_v) if n_syn else None
    # 투영 위에서 다시 드라이버를 뽑는다 — C가 착지한 뒤 남는 잔차의 정체.
    drv2 = []
    if rproj is not None:
        for sc in sorted(set(proj_s)):
            ix = [i for i, x in enumerate(proj_s) if x != sc]
            if len({proj_g[i] for i in ix}) < 2:
                continue
            rr = point_biserial([proj_g[i] for i in ix], [proj_v[i] for i in ix])
            if rr is not None:
                drv2.append(dict(scene=sc, r_without=round(rr, 4),
                                 delta=round(rr - rproj, 4)))
        drv2.sort(key=lambda d: d["delta"])
    # 팔 균형 진단: 씬별 A/B/D 프레임 수가 어긋난 곳이 잔차를 만든다.
    armn = collections.defaultdict(collections.Counter)
    for r in rows:
        armn[r["scene"]][r["arm"]] += 1
    imbal = []
    for sc, c in sorted(armn.items()):
        a, b = c.get("A", 0), c.get("B", 0)
        if a != b:
            imbal.append(dict(scene=sc, A=a, B=b, D=c.get("D", 0),
                              C_planned=cplan.get(sc, 0), dAB=a - b))
    res["c_wave_landing"] = dict(
        status="[08-24] C팔 착지 — 이 절은 투영이 아니라 **투영 대 실측 대조**다",
        d83_projection=dict(r_pb_projected_then=0.1495, kappa_then=1.0022,
                            basis="D83 ① · CUE_EXTENT_AUDIT 승용 요약 2"),
        kappa_corpus=round(kappa_corpus, 4) if kappa_corpus else None,
        kappa_corpus_basis=f"라이브러리 {len(both)}씬 · 같은 씬의 A팔 대 C팔 평균 면적비 (실측)",
        kappa_by_scene=kappa_by_scene,
        assumption="잔여 투영: 아직 세그가 없는 C 자리(무낙차 4씬 재활용)만 A×κ 로 채운다",
        kappa=round(kappa, 4) if kappa else None,
        kappa_basis=f"P2 신규 씬 실측 A팔 n={len(kA)} · C팔 n={len(kC)} "
                    "(같은 씬·같은 포즈, 위험 토글만 다름)",
        c_frames_planned=sum(v for k, v in cplan.items()
                             if k in {r['scene'] for r in rows}),
        c_frames_synthesised=n_syn,
        r_pb_projected=round(rproj, 4) if rproj is not None else None,
        r_pb_asbuilt=round(point_biserial(g, tot), 4),
        null_q99_asbuilt=(head["total_area_pct"].get("null_within_scene") or {}).get("q99"),
        residual_drivers=drv2[:6],
        arm_imbalance=imbal,
        arm_imbalance_note="A팔만 있고 B팔이 없는 씬(D74 ⑤ 스킵분)과 그 반대는 "
                           "위험 축과 단서 축을 씬 수준에서 다시 결속시킨다 — "
                           "C가 착지해도 남는 잔차의 주된 정체다.")

    # ======================================================================
    # 4. 문턱 제안 — 측정된 귀무 분포에서 유도한다 (자의 금지)
    # ======================================================================
    nul = head["total_area_pct"].get("null_within_scene") or {}
    nulf = head["total_area_pct"].get("null_free") or {}
    res["threshold_proposal"] = dict(
        statistic="|r_pb| (frame-level hazard × cue_area_total %) — 존재 |r| 과 같은 "
                  "모집단 구성(as-built A/B/C/D), 같은 병기 규약(§4.9-3)",
        derivation=(
            "문턱을 손으로 정하지 않는다. 위험 라벨을 **씬 안에서** 셔플한 귀무를 "
            f"{args.perm}회 만들어 |r_pb| 의 분포를 측정하고, 그 **q99** 를 문턱으로 "
            "제안한다. 씬 내 셔플은 씬 구성·카메라 밴드가 만드는 구조를 유지한 채 "
            "위험-면적 결속만 끊으므로, 이 문턱을 넘는 값은 '씬 구성으로 설명되지 "
            "않는 계통적 초과'다."),
        null_within_scene=nul, null_free=nulf,
        proposed_threshold=nul.get("q99"),
        proposed_threshold_free=nulf.get("q99"),
        effect_size_floor=dict(
            statistic="|Cliff's δ|", value=0.147,
            basis="Romano 2006 small-effect 경계 — r 이 문턱을 넘어도 δ 가 이 아래면 "
                  "'통계적으로 보이나 실질적으로 작다'로 분류"),
        secondary_gate=dict(
            statistic="mean(area | hazard) / mean(area | no-hazard)",
            note="비율은 부호와 크기를 한 눈에 준다. 문턱값은 측정 후 §4 에 기재."))

    # ======================================================================
    # 5. 계기 타당성 — 팔 차분(경험적)과 렉시컬 귀속의 대조
    # ======================================================================
    res["instrument_validation"] = validate_attrib(attrib, args)

    res["elapsed_s"] = round(time.time() - t0, 1)
    return res, rows, prows


def validate_attrib(attrib, args):
    """②(팔 차분)로 ③(렉시컬)을 검산한다 — **홀드아웃**으로.

    같은 (씬, 밴드, 컷)에서 A팔과 B팔의 가시 프림 집합을 뺀다. B는 프림을 지우는
    일만 하므로 그 차집합은 **정확히** B레버가 지운 단서 프림이다.

    주의: 경험층(④)이 바로 그 차분에서 만들어졌으므로 전 규칙으로 재는 recall 은
    **정의상 1.0** 이고 정보가 없다. 그래서 여기서는 경험층을 **떼어낸** 귀속기로
    잰다 — 즉 "렉시컬 추측만으로 어디까지 갔는가"의 정직한 수치다. 이 값이 낮다는
    사실 자체가 경험층이 필요했던 이유의 증거다.
    """
    lex_only = {"doc": attrib.get("doc"), "scenes": {}}
    for sc, rec in attrib["scenes"].items():
        r2 = dict(rec)
        r2["prefix"] = {k: [p for p in v if not p.startswith("=")]
                        for k, v in rec.get("prefix", {}).items()}
        r2["prefix"] = {k: v for k, v in r2["prefix"].items() if v}
        lex_only["scenes"][sc] = r2
    att = Attributor(lex_only)
    A = {}
    for rnd, band in A_ROUNDS:
        for f in glob.glob(os.path.join(DATA, rnd, "*", "*", "*.idseg.npz")):
            sc = os.path.basename(os.path.dirname(f))
            A[(sc, band, os.path.basename(f))] = f
    B = {}
    for rounds, tg in ((B_ROUNDS, "B"), (B2_ROUNDS, "B2"), (B3_ROUNDS, "B3")):
        for rnd, band in rounds:
            for f in glob.glob(os.path.join(DATA, rnd, "*", "*", "*.idseg.npz")):
                sc = os.path.basename(os.path.dirname(f))
                if b_tree_of(sc) != tg:
                    continue
                B[(sc, band, os.path.basename(f))] = f
    common = sorted(set(A) & set(B))
    if args.val_limit:
        bysc = collections.defaultdict(list)
        for k in common:
            bysc[k[0]].append(k)
        common = []
        for sc, ks in bysc.items():
            common += ks[: args.val_limit]
    per_scene = collections.defaultdict(lambda: dict(
        n=0, removed_px=0, removed_px_caught=0, removed_prims=0,
        removed_prims_caught=0, missed=collections.Counter()))
    for sc, band, fn in common:
        try:
            pa, _ = _load_prim_areas(A[(sc, band, fn)])
            pb, _ = _load_prim_areas(B[(sc, band, fn)])
        except Exception:
            continue
        sb = set(pb)
        d = per_scene[sc]
        d["n"] += 1
        for p, c in pa.items():
            if p in sb:
                continue
            d["removed_px"] += c
            d["removed_prims"] += 1
            if att.key_of(sc, p) is not None:
                d["removed_px_caught"] += c
                d["removed_prims_caught"] += 1
            else:
                d["missed"][root_comp(p)] += c
    out = {}
    tot_px = tot_ok = 0
    for sc, d in sorted(per_scene.items()):
        if d["removed_px"] == 0:
            out[sc] = dict(n_pairs=d["n"], removed_px=0,
                           note="이 씬은 B레버가 지운 프림이 그 포즈들에서 보이지 않았다 "
                                "(면적 0 — 검산 불가)")
            continue
        tot_px += d["removed_px"]
        tot_ok += d["removed_px_caught"]
        out[sc] = dict(n_pairs=d["n"],
                       removed_px_per_frame=round(d["removed_px"] / d["n"], 1),
                       px_recall=round(d["removed_px_caught"] / d["removed_px"], 4),
                       prim_recall=round(d["removed_prims_caught"] /
                                         max(1, d["removed_prims"]), 4),
                       top_missed=[(k, round(v / d["n"], 1))
                                   for k, v in d["missed"].most_common(6)])
    return dict(
        method="visible(A,i) \\ visible(B,i) = 그 프레임에서 B레버가 지운 단서 프림 "
               "(제거는 가림을 풀 뿐 만들지 않으므로 정확하다)",
        measured_with="렉시컬층만 (경험층 제거 · 홀드아웃)",
        n_pairs=len(common), scenes=len(out),
        overall_px_recall_lexical_only=round(tot_ok / tot_px, 4) if tot_px else None,
        note="최종 귀속기는 여기에 경험층(정확 일치)을 얹으므로 이 차분 위에서의 "
             "recall 은 1.000 이다 — 그 1.000 은 자기참조라 인쇄하지 않는다.",
        per_scene=out)


# --------------------------------------------------------------------------
# 표 인쇄
# --------------------------------------------------------------------------
def print_tables(res):
    h = res["headline_P1"]
    m = h["marginals"]
    log("\n=== §1 헤드라인 — as-built v3 코퍼스 (P1) ===")
    log(f"  n={m['n']}  위험 프레임 {m['hazard_present']} / 무위험 {m['hazard_absent']}"
        f"  p_hazard={m['p_hazard']}  씬 {m['n_scenes']}  팔 {m['by_arm']}")
    for lab in ("total_area_pct", "obj_count", "grp_count"):
        d = h[lab]
        log("  %-38s r_pb=%s  δ=%s  H mean=%s / N mean=%s" % (
            d["metric"], d["r_pb"], d["cliffs_delta"],
            d["hazard"].get("mean"), d["no_hazard"].get("mean")))
        if d.get("null_within_scene"):
            n = d["null_within_scene"]
            log(f"       귀무(씬내셔플) q95={n['q95']} q99={n['q99']} p={n['p_emp']}")
    log("  --- 키별 ---")
    for k, d in h["per_key"].items():
        n = d.get("null_within_scene") or {}
        log("   %-3s %-16s n=%-5s 씬%-3s r=%-8s δ=%-8s H=%-9s N=%-9s q99=%s" % (
            k, d["cue"], d["n"], d["n_scenes"], d["r_pb"], d["cliffs_delta"],
            d["hazard"].get("mean"), d["no_hazard"].get("mean"), n.get("q99")))
    for c in h["constant_keys"]:
        log(f"   [상수] {c['key']} {c['cue']} — {c['reason']}")
    for c in h["blind_keys"]:
        log(f"   [면적-불가시] {c['key']} {c['cue']} — {c['reason'][:60]}…")
    a = h["arm_level_check"]
    log(f"  팔 수준 대조 r_pb={a['r_pb']}  " +
        "  ".join(f"{k}:{v['mean']}" for k, v in a["by_arm"].items()))

    if "headline_P2" in res:
        d = res["headline_P2"]
        log(f"\n=== §1b 신규 씬 프로브 (P2) === n={d['n']} 씬{d['n_scenes']} "
            f"r_pb={d['r_pb']} H={d['hazard']['mean']} N={d['no_hazard']['mean']} "
            f"q99={(d.get('null_within_scene') or {}).get('q99')}")

    log("\n=== §2 밀도 대칭 ===")
    for k, v in res["density_symmetry"]["groups"].items():
        log(f"  {k:<34} n={v['n']:<5} mean={v.get('mean')} med={v.get('med')} p90={v.get('p90')}")
    for k, v in res["density_symmetry"].get("contrast", {}).items():
        log(f"  대조 {k}: ratio={v['ratio_mean']} δ={v['cliffs_delta']}")

    log("\n=== §3 이상치 ===")
    for f in res["outliers"]["flags"][:15]:
        log(f"  {f['key']:<22} {f['family']:<14} mean={f['mean_area_pct']:<8} "
            f"med={f['family_median']:<8} z={f['robust_z']} {f['direction']}")

    c = res.get("c_wave_landing") or {}
    if c.get("r_pb_projected") is not None:
        log(f"\n=== §3c C 웨이브 투영 === κ={c['kappa']} · 합성 C {c['c_frames_synthesised']}프레임 "
            f"→ r_pb {c['r_pb_asbuilt']} ⇒ **{c['r_pb_projected']}** (문턱 {c['null_q99_asbuilt']})")
        log("   잔차 드라이버: " + ", ".join(
            f"{x['scene']}({x['delta']})" for x in c.get("residual_drivers", [])))
        log("   팔 불균형: " + ", ".join(
            f"{x['scene']} A{x['A']}/B{x['B']}/D{x['D']}" for x in c.get("arm_imbalance", [])))
    cb = res.get("combined_P1P2") or {}
    if cb:
        log(f"\n=== §1c 합본(P1+P2) === n={cb['n']} r_pb={cb['r_pb']} "
            f"q99={(cb.get('null_within_scene') or {}).get('q99')}")
    dv = res.get("drivers") or {}
    if dv:
        log("\n=== §3b 드라이버 (빼면 r 이 내려가는 씬 = 상관 제조기) ===")
        for x in dv["top_makers"][:5]:
            log(f"   -{x['scene']:<10} r_without={x['r_without']} Δ={x['delta']}")
        for x in dv["top_dampers"][-3:]:
            log(f"   +{x['scene']:<10} r_without={x['r_without']} Δ={x['delta']}")
    t = res["threshold_proposal"]
    log(f"\n=== §4 문턱 제안 === 귀무 q95={t['null_within_scene'].get('q95')} "
        f"q99={t['null_within_scene'].get('q99')} → 제안 문턱 |r_pb| > {t['proposed_threshold']}")

    v = res["instrument_validation"]
    log(f"\n=== §5 계기 검산(홀드아웃) === 팔 차분쌍 {v['n_pairs']} · "
        f"렉시컬 단독 픽셀 recall {v['overall_px_recall_lexical_only']}")
    for sc, d in sorted(v["per_scene"].items()):
        if "px_recall" in d:
            log(f"   {sc:<10} px_recall={d['px_recall']:<8} "
                f"removed={d['removed_px_per_frame']} px/frame  "
                f"missed={d['top_missed'][:3]}")


# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage", default="all",
                    choices=["attrib", "scan", "analyze", "all"])
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--perm", type=int, default=2000,
                    help="치환 귀무 반복수 (문턱 유도의 정밀도)")
    ap.add_argument("--val-limit", type=int, default=0,
                    help="계기 검산에서 씬당 쌍 수 상한 (0=전량)")
    ap.add_argument("--regen-hook", action="store_true",
                    help="N9/N11 재렌더·C 웨이브 착지 후 전면 갱신 "
                         "(등록부 자동 점검 + 캐시 무효화 + 전 단계 재실행)")
    ap.add_argument("--out", default=os.path.join(V3, "cue_extent_audit.json"))
    args = ap.parse_args()

    if args.regen_hook:
        log("=== --regen-hook : 등록부 대비 디스크 실태 점검 ===")
        news, seen = [], set()
        now = time.time()

        def note(d, tag):
            b = os.path.basename(d)
            if b in seen:
                return
            fs = glob.glob(os.path.join(d, "*", "*", "*.idseg.npz"))
            if not fs:
                return
            seen.add(b)
            hot = max((os.path.getmtime(f) for f in fs), default=0)
            news.append((b, len(fs), tag +
                         (" · **쓰기 중일 수 있음**" if now - hot < 1800 else "")))

        # C 웨이브 (W1C_REPORT: 트리 `260827_v3w1_lib_C*`)
        for pat in ("*_v3w1_lib_C*", "*_v3w1c_*", "*cwave*"):
            for d in sorted(glob.glob(os.path.join(DATA, pat))):
                note(d, "C 웨이브 후보")
        # 규정 감사 재렌더 (REG_AUDIT: `*reg_{A,B,C,D}`)
        for d in sorted(glob.glob(os.path.join(DATA, "*reg_[ABCD]"))):
            note(d, "규정 감사 확정 라운드 — P2 를 여기로 갈아타야 한다")
        # 그 밖의 미등록 프로브 라운드
        known = {s["stamp"] for s in PROBE_PRIMARY + PROBE_SECONDARY} | \
                {s["stamp"] for s in PROBE_H67}
        for d in sorted(glob.glob(os.path.join(DATA, "*_v3p5_*"))):
            stamp = re.sub(r"_[ABCD]$", "", os.path.basename(d))
            if stamp in known or stamp.endswith(("smoke", "near")):
                continue
            note(d, "미등록 프로브 라운드")
        if news:
            log("  ** 등록부에 없는 라운드 발견 — cue_extent_audit.py 의 "
                "PROBE_PRIMARY / CORPUS 등록부에 추가하고 다시 돌려라:")
            for a, b, c in news:
                log(f"     {a:<38} idseg={b:<5} {c}")
        else:
            log("  등록부와 디스크 일치 — 신규 라운드 없음.")
        for f in ("cue_extent_frames.json", "cue_extent_attrib.json"):
            p = os.path.join(LOGS, f)
            if os.path.exists(p):
                os.rename(p, p + ".bak")
                log(f"  캐시 무효화: {f} → {f}.bak")
        args.stage = "all"

    attrib = None
    ap_ = os.path.join(LOGS, "cue_extent_attrib.json")
    if args.stage in ("attrib", "all") or not os.path.exists(ap_):
        attrib = build_attrib()
    else:
        attrib = json.load(open(ap_, encoding="utf-8"))
    if args.stage == "attrib":
        return

    fp = os.path.join(LOGS, "cue_extent_frames.json")
    if args.stage in ("scan", "all") or not os.path.exists(fp):
        frames = run_scan(attrib, workers=args.workers)
    else:
        frames = json.load(open(fp, encoding="utf-8"))
    if args.stage == "scan":
        return

    res, rows, prows = analyze(frames, attrib, args)
    json.dump(res, open(args.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print_tables(res)
    log(f"\n→ {os.path.relpath(args.out, REPO)}  ({res['elapsed_s']}s)")


if __name__ == "__main__":
    main()
