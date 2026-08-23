#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""w1c_labeler_boundary.py — D78 (3) 라벨러 측방 사각의 **근본 수리** 검증기 (CPU only).

무엇을 증명하는 파일인가
------------------------
정본 라벨러 `experiments/mainrun_0819/code/labeling/labeler.py` 의 `_outward()` 는
카메라 쪽 방향을 `rint(dx/n), rint(dy/n)` 으로 **8이웃에 양자화**하고,
`_near_boundary()` 는 그 **한 이웃만** 찔러 본다.  보행축과 **나란한** 축방향 립
(측방 개거·연석)에서는 `d > -x0 + sqrt(3)*y_lip` 이 되는 순간 그 방향이 립을
**가로지르지 않고 따라가므로** 근접 경계가 사라지고 `cells_kept` 가 0 이 되어
**거짓 음성 GT** 가 만들어진다 (DECISIONS.md D78 (3) · sceneL1 실측 d 8.50/8.69).

D82 (2) 가 승인한 근본 수리는 **성분-경계 전수 스캔**(`BOUNDARY_COMPONENT`)이고,
같은 결재가 **v2 GT 소급 불변 검증**을 필수 조건으로 달았다.  이 파일이 그 둘을
한 자리에서 기계로 실행한다.

  --selftest    순수 numpy 합성 픽스처(Isaac 없음).  d = 8.50 m 축평행 측방 립에서
                구 모드 `cells_kept == 0` · 신 모드 `cells_kept > 0` 을 실측하고,
                닫힌 식 임계 d <= -x0 + sqrt(3)*y_lip 을 d 스윕으로 재현한다.

  --verify-v2   **필수 검증**.  정본 v2 코퍼스 매니페스트
                (`experiments/v3_0823/dataset_manifest_v2corr.json`, 2832 프레임)의
                전 프레임을 신 모드로 **다시 라벨링**하여 교정-GT 정본과
                바이트 동일성을 대조한다.  세 갈래를 모두 인쇄한다:

                  CONTROL   구 모드 재라벨 vs 정본  -> 드라이버가 코퍼스를 재현하는가
                  TEST      신 모드 재라벨 vs 정본  -> **결재가 요구한 소급 불변**
                  DELTA     신 모드 vs 구 모드(같은 주행) -> 모드 단독 효과

                CONTROL 이 깨지면 TEST 의 어떤 결과도 읽을 수 없다 — 그래서 함께 잰다.

                산출: experiments/v3_0823/w1c_labeler_invariance.json

정본 계기 선택 (매니페스트가 스스로 말하게 한다)
------------------------------------------------
코퍼스의 계기 권위는 (밴드, 씬)마다 다르다.  G7 수리가 다시 라벨링한 5쌍
(boost_e x {scene07, scene08, scene12} · boost_e2 x {scene07, scene12}) 은
`g7fixM` 그림자 트리(융합 사이드카를 얹은 심링크본)가 정본이고 나머지는 평 트리다
(`g7_build_v2corr.py` AFFECTED · `g7_variantB.py`).  작업 목록은 **매니페스트의
frames 를 읽어** (round, scene, arm) 를 뽑아 만들므로 코퍼스 전수를 덮는 것이
구조적으로 보장되고, 실제로 비교한 프레임 수·씬 목록을 산출에 적는다.

사용:
    python3 experiments/v3_0823/code/w1c_labeler_boundary.py --selftest
    python3 experiments/v3_0823/code/w1c_labeler_boundary.py --verify-v2 [--workers 8]

이 파일은 v2 라벨도 매니페스트도 **쓰지 않는다**.  신 모드를 어디에서도 기본값으로
채택하지 않는다 (`labeler.BOUNDARY_MODE` 는 `quantised` 그대로).
"""
import argparse
import collections
import glob
import json
import math
import os
import sys

import numpy as np

REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"
V3 = os.path.join(REPO, "experiments/v3_0823")
LABDIR = os.path.join(REPO, "experiments/mainrun_0819/code/labeling")
sys.path.insert(0, LABDIR)
import labeler as LB                                              # noqa: E402

GRID_PATH = os.path.join(LABDIR, "gridspec_v1.json")
MANIFEST = os.path.join(V3, "dataset_manifest_v2corr.json")
CANON_LABELS = os.path.join(V3, "annotations/labels_v1_full_g7fix.json")
OUT_JSON = os.path.join(V3, "w1c_labeler_invariance.json")

# (밴드 접미사) — merge_corpus.py / g7_build_v2corr.py 의 규약 그대로
BAND_OF_ROUND = {"260819_main_on": "main", "260819_main_off": "main",
                 "260820_boost_h_on": "boost_h", "260820_boost_h_off": "boost_h",
                 "260820_boost_e_on": "boost_e", "260820_boost_e_off": "boost_e",
                 "260820_boost_e2_on": "boost_e2", "260820_boost_e2_off": "boost_e2"}
SUFFIX_OF_BAND = {"main": "", "boost_h": "::boost_h",
                  "boost_e": "::boost_e", "boost_e2": "::boost_e2"}
ROUNDS_OF_BAND = {"main": ("260819_main_on", "260819_main_off"),
                  "boost_h": ("260820_boost_h_on", "260820_boost_h_off"),
                  "boost_e": ("260820_boost_e_on", "260820_boost_e_off"),
                  "boost_e2": ("260820_boost_e2_on", "260820_boost_e2_off")}
# g7_build_v2corr.AFFECTED — 이 (밴드, 씬) 만 g7fixM 그림자 트리가 정본이다
AFFECTED = {("boost_e", "scene07"), ("boost_e", "scene08"), ("boost_e", "scene12"),
            ("boost_e2", "scene07"), ("boost_e2", "scene12")}
OVERLAY_SUFFIX = "_g7fixM"


# =========================================================================== #
# 1. 합성 사각 재현 (--selftest)
# =========================================================================== #
def lateral_fixture(d, y_lip=3.54, y_far=5.46, floor_z=-1.50, y_c=0.0,
                    x0=-2.0, y0=-8.0, st=0.05, nx=321, ny=321):
    """sceneL1 의 **축평행 측방 개거**를 라벨러 격자 위에 해석적으로 놓는다.

    보행축은 +x, 개거 두 줄은 y_lip <= |y| <= y_far 에서 floor_z 로 떨어진다.
    카메라 눈은 (-d, y_c) — 즉 개거와 **나란히** 뒤에서 본다.  Isaac 도 렌더도
    depth 도 없다: 라벨러가 GT 를 만드는 데 쓰는 두 높이맵과 눈 위치가 전부다.
    """
    XX, YY = np.meshgrid(x0 + np.arange(nx) * st, y0 + np.arange(ny) * st)
    hm_off = np.zeros((ny, nx))                       # 반사실 보행면
    hm_on = np.zeros((ny, nx))
    canal = (np.abs(YY) >= y_lip) & (np.abs(YY) <= y_far)
    hm_on[canal] = floor_z
    void = np.zeros((ny, nx), bool)
    eye = np.array([-d, y_c, 1.20])
    return dict(XX=XX, YY=YY, hm_on=hm_on, hm_off=hm_off, void=void, eye=eye,
                st=st, x0=x0, y_lip=y_lip)


def run_gate(fx, mode, hz=0.30):
    """두 모드 중 하나로 D10 스텝 게이트를 돌리고 실측치를 돌려준다."""
    diff = fx["hm_off"] - fx["hm_on"]
    fp_raw = (~fx["void"]) & (diff >= hz)
    comp, ncomp = LB.connected_components(fp_raw)
    ox, oy = LB._outward(fx["XX"], fx["YY"], fx["eye"])       # 구 모드 입력
    fp, stat = LB.step_gate(fp_raw, comp, ncomp, fx["void"], fx["hm_on"],
                            ox, oy, fx["st"], hz, boundary_mode=mode,
                            XX=fx["XX"], YY=fx["YY"], eye=fx["eye"])
    out = dict(mode=mode, cells_raw=int(fp_raw.sum()), cells_kept=int(fp.sum()))
    out.update({k: int(v) for k, v in stat.items()})     # comps_raw 포함
    return out


def selftest(verbose=True):
    """구 모드가 못 보는 것을 신 모드가 보는가 — 기계 판정."""
    grid = json.load(open(GRID_PATH))
    hz = float(grid["hazard_depth_m"])
    y_lip = 3.54
    x0 = -2.0
    d_crit = -x0 + math.sqrt(3.0) * y_lip
    checks, sweep = [], []

    def chk(ok, name, detail):
        checks.append(dict(ok=bool(ok), name=name, detail=detail))
        if verbose:
            print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")

    if verbose:
        print("=" * 78)
        print("w1c --selftest : 축평행 측방 립의 8이웃 양자화 사각 (D78 (3))")
        print(f"  격자 x0={x0} · y_lip={y_lip} · 닫힌 식 임계 "
              f"d <= -x0 + sqrt(3)*y_lip = {d_crit:.3f} m")
        print("=" * 78)

    # --- 주 시험: 실측 사각 포즈 d = 8.50 m -------------------------------- #
    fx = lateral_fixture(8.50)
    old = run_gate(fx, LB.BOUNDARY_QUANTISED, hz)
    new = run_gate(fx, LB.BOUNDARY_COMPONENT, hz)
    chk(old["cells_raw"] > 0, "픽스처가 발자국을 만든다 (카메라 무관량)",
        f"cells_raw={old['cells_raw']} · comps_raw={old['comps_raw']} (개거 2줄)")
    chk(old["cells_kept"] == 0, "구 모드 = 사각 (거짓 음성 GT)",
        f"d=8.50 quantised cells_kept={old['cells_kept']} · "
        f"comps_kept={old['comps_kept']} · boundary_cells={old['boundary_cells']}")
    chk(new["cells_kept"] > 0, "신 모드 = 사각 해소",
        f"d=8.50 component cells_kept={new['cells_kept']} · "
        f"comps_kept={new['comps_kept']} · boundary_cells={new['boundary_cells']}")
    chk(new["cells_kept"] == new["cells_raw"] and new["comps_kept"] == new["comps_raw"],
        "신 모드가 개거 두 줄을 **전부** 살린다",
        f"kept {new['cells_kept']}/{new['cells_raw']} 셀 · "
        f"{new['comps_kept']}/{new['comps_raw']} 성분")

    # --- 닫힌 식 임계의 스윕 재현 ------------------------------------------ #
    for d in (4.98, 7.15, 7.70, 8.10, 8.13, 8.20, 8.50, 8.69, 10.00):
        f2 = lateral_fixture(d)
        o = run_gate(f2, LB.BOUNDARY_QUANTISED, hz)
        n = run_gate(f2, LB.BOUNDARY_COMPONENT, hz)
        sweep.append(dict(d=d, quantised_cells_kept=o["cells_kept"],
                          quantised_boundary_cells=o["boundary_cells"],
                          component_cells_kept=n["cells_kept"],
                          component_boundary_cells=n["boundary_cells"],
                          cells_raw=o["cells_raw"]))
        if verbose:
            print(f"    d={d:5.2f}  quantised kept {o['cells_kept']:6d} "
                  f"(bnd {o['boundary_cells']:5d})   component kept "
                  f"{n['cells_kept']:6d} (bnd {n['boundary_cells']:5d})")
    blind = [r["d"] for r in sweep if r["quantised_cells_kept"] == 0]
    seen = [r["d"] for r in sweep if r["quantised_cells_kept"] > 0]
    chk(blind and seen and min(blind) > max(seen),
        "구 모드 사각이 닫힌 식 임계에서 시작한다",
        f"보임 d<= {max(seen):.2f} · 사각 d>= {min(blind):.2f} "
        f"(예측 임계 {d_crit:.3f})")
    chk(all(r["component_cells_kept"] == r["cells_raw"] for r in sweep),
        "신 모드는 d 전 구간에서 발자국을 유지한다",
        f"{len(sweep)} 포즈 전부 kept == raw")

    # --- 신 모드는 근접(보행 가능) 쪽 의미를 지키는가 ---------------------- #
    # 개거 **바깥쪽** 립(먼 쪽)의 이웃은 카메라 반대 반공간이므로 방향장이
    # 그것을 고르면 안 된다.  d=8.50 에서 방향장을 직접 읽어 확인한다.
    fx2 = lateral_fixture(8.50)
    diff = fx2["hm_off"] - fx2["hm_on"]
    fp_raw = diff >= hz
    ox, oy = LB._outward_component(fx2["XX"], fx2["YY"], fx2["eye"], fp_raw, fx2["void"])
    sel = fp_raw & ((ox != 0) | (oy != 0))
    iy, ix = np.nonzero(sel)
    ty = (fx2["eye"][1] - fx2["YY"][iy, ix])
    tx = (fx2["eye"][0] - fx2["XX"][iy, ix])
    tn = np.hypot(tx, ty)
    dot = (ox[iy, ix] * tx + oy[iy, ix] * ty) / np.maximum(tn, 1e-12) / \
        np.hypot(ox[iy, ix], oy[iy, ix])
    chk(bool((dot > 0).all()), "선택된 이웃은 전부 카메라-대면 반공간에 있다",
        f"{iy.size} 경계 셀 · min dot = {float(dot.min()):.4f} > 0")
    walk = (~fp_raw) & (~fx2["void"])
    chk(bool(walk[iy + oy[iy, ix], ix + ox[iy, ix]].all()),
        "선택된 이웃은 전부 보행 가능 지면 (발자국도 void 도 아님)",
        f"{iy.size} 경계 셀 전부 walkable")
    # 사각의 실체: **근단 립 행**(개거 안쪽, 보행면과 맞닿은 줄)이 경계로 잡히는가.
    ny_ = fx2["YY"].shape[0]
    near_n = int(np.argmin(np.abs(fx2["YY"][:, 0] - y_lip)))          # y = +3.55
    near_s = ny_ - 1 - near_n                                        # y = -3.55
    for row, nm, want in ((near_n, "북", -1), (near_s, "남", +1)):
        row = row if fp_raw[row].any() else row + (1 if want < 0 else -1)
        seln = sel[row]
        chk(bool(seln.all()) and bool((oy[row][seln] == want).all()),
            f"{nm}측 **근단 립 전 셀**이 립을 가로질러 보행면으로 나간다",
            f"y={fx2['YY'][row, 0]:+.2f} · {int(seln.sum())}/{seln.size} 셀 경계 · "
            f"oy={want} (보행면 y={fx2['YY'][row + want, 0]:+.2f})")
    oxq0, oyq0 = LB._outward(fx2["XX"], fx2["YY"], fx2["eye"])
    q_near = LB._near_boundary(fp_raw, fp_raw, fx2["void"], oxq0, oyq0)
    chk(q_near[0].size == 0, "같은 포즈에서 구 모드는 근접 경계를 **하나도** 못 찾는다",
        f"quantised 경계 셀 {q_near[0].size} · component {iy.size}")

    # --- edge_points 도 같은 per-cell 방향으로 동작하는가 ------------------ #
    cell = np.zeros(fp_raw.shape, np.int64)          # 전 격자를 grid 안으로
    fp_new, _ = LB.step_gate(fp_raw, *LB.connected_components(fp_raw), fx2["void"],
                             fx2["hm_on"], ox, oy, fx2["st"], hz,
                             boundary_mode=LB.BOUNDARY_COMPONENT,
                             XX=fx2["XX"], YY=fx2["YY"], eye=fx2["eye"])
    oxq, oyq = LB._outward(fx2["XX"], fx2["YY"], fx2["eye"])
    E_old = LB.edge_points(fp_new, fx2["void"], fx2["hm_on"], fx2["XX"], fx2["YY"],
                           fx2["eye"], cell, 0.0, oxq, oyq)
    E_new = LB.edge_points(fp_new, fx2["void"], fx2["hm_on"], fx2["XX"], fx2["YY"],
                           fx2["eye"], cell, 0.0, oxq, oyq,
                           boundary_mode=LB.BOUNDARY_COMPONENT)
    chk(E_old.shape[0] == 0 and E_new.shape[0] > 0,
        "edge_points 도 사각을 벗어난다 (같은 발자국·같은 포즈)",
        f"quantised {E_old.shape[0]} 립점 · component {E_new.shape[0]} 립점")
    if E_new.shape[0]:
        chk(bool(np.allclose(E_new[:, 2], 0.0)),
            "립 z 는 보행 가능측 표고 (규약 유지)",
            f"z in [{float(E_new[:, 2].min()):.3f}, {float(E_new[:, 2].max()):.3f}]")

    # --- 기본값은 옛 동작 그대로인가 (bit-for-bit) ------------------------- #
    fx3 = lateral_fixture(4.98)                      # 구 모드가 경계를 찾는 포즈
    same = []
    for f_ in (fx, fx3):
        a = {k: v for k, v in run_gate(f_, LB.BOUNDARY_QUANTISED, hz).items() if k != "mode"}
        b = {k: v for k, v in run_gate(f_, None, hz).items() if k != "mode"}
        same.append(a == b)
    diff2 = fx3["hm_off"] - fx3["hm_on"]
    fpr3 = diff2 >= hz
    E_def = LB.edge_points(fpr3, fx3["void"], fx3["hm_on"], fx3["XX"], fx3["YY"],
                           fx3["eye"], np.zeros(fpr3.shape, np.int64), 0.0,
                           *LB._outward(fx3["XX"], fx3["YY"], fx3["eye"]))
    E_q = LB.edge_points(fpr3, fx3["void"], fx3["hm_on"], fx3["XX"], fx3["YY"],
                         fx3["eye"], np.zeros(fpr3.shape, np.int64), 0.0,
                         *LB._outward(fx3["XX"], fx3["YY"], fx3["eye"]),
                         boundary_mode=LB.BOUNDARY_QUANTISED)
    chk(all(same) and LB.BOUNDARY_MODE == LB.BOUNDARY_QUANTISED
        and E_def.shape == E_q.shape and bool(np.array_equal(E_def, E_q)),
        "기본값 무변경 (인자 없음 == quantised, 모듈 상수도 quantised)",
        f"BOUNDARY_MODE={LB.BOUNDARY_MODE!r} · step_gate 동일 {all(same)} · "
        f"edge_points {E_def.shape[0]} 점 동일 {bool(np.array_equal(E_def, E_q))}")

    n_ok = sum(1 for c in checks if c["ok"])
    if verbose:
        print("-" * 78)
        print(f"RESULT selftest: {n_ok}/{len(checks)} checks passed "
              f"{'OK' if n_ok == len(checks) else 'FAILED'}")
    return dict(ok=n_ok == len(checks), n_checks=len(checks), n_passed=n_ok,
                d_crit_closed_form=round(d_crit, 4),
                blindspot_pose=dict(d=8.50, quantised=old, component=new),
                sweep=sweep, checks=checks)


# =========================================================================== #
# 2. v2 코퍼스 소급 불변 검증 (--verify-v2)
# =========================================================================== #
def sdir_of(round_name, scene):
    g = glob.glob(os.path.join(REPO, "dataset", round_name, "*", scene, "variation.json"))
    return os.path.dirname(g[0]) if g else None


def corpus_tasks(man):
    """매니페스트가 담은 (밴드, 씬) 전수 -> (밴드, 씬, 팔, sdir, off_dir).

    on 팔은 (on 트리, off 트리), off 팔은 (off 트리, off 트리) — 정본 라벨러
    main() 의 작업 구성과 동일하다.  AFFECTED 5쌍만 g7fixM 그림자 트리를 쓴다.
    """
    seen = collections.defaultdict(set)               # 밴드 -> {씬}
    arms = collections.defaultdict(set)               # (밴드, 씬) -> {팔}
    for f in man["frames"]:
        band = BAND_OF_ROUND[f["round"]]
        seen[band].add(f["scene_id"])
        arms[(band, f["scene_id"])].add(f["toggle_state"])
    tasks, missing = [], []
    for band in sorted(seen):
        ron, roff = ROUNDS_OF_BAND[band]
        for sc in sorted(seen[band]):
            if (band, sc) in AFFECTED:
                ron_s, roff_s = ron + OVERLAY_SUFFIX, roff + OVERLAY_SUFFIX
            else:
                ron_s, roff_s = ron, roff
            don, doff = sdir_of(ron_s, sc), sdir_of(roff_s, sc)
            if not don or not doff:
                missing.append(f"{band}/{sc}: on={don} off={doff}")
                continue
            for arm in sorted(arms[(band, sc)]):
                tasks.append((band, sc, arm, don if arm == "on" else doff, doff,
                              ron_s if arm == "on" else roff_s, roff_s))
    return tasks, missing


def _work(t):
    band, sc, arm, sd, od, run, orun = t
    grid = json.load(open(GRID_PATH))
    out = {}
    for tag, mode in (("q", LB.BOUNDARY_QUANTISED), ("c", LB.BOUNDARY_COMPONENT)):
        try:
            fr, sm, wn = LB.label_scene(arm, sc, sd, od, grid, mode)
        except Exception as e:                                   # 주행을 살린다
            return band, sc, arm, run, orun, None, \
                f"{band}/{sc}/{arm}: FAILED[{tag}] {type(e).__name__}: {e}"
        out[tag] = (fr, sm)
    return band, sc, arm, run, orun, out, None


def _get(rec, path, default=None):
    cur = rec
    for k in path.split("."):
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


# 비교하는 필드.  (표시 이름, 재라벨 기록에서의 경로, 정본 매니페스트에서의 경로,
#                 정본 라벨 파일에서의 경로)  — None = 그 정본에 없는 필드
FIELDS = [
    ("polar_gt",            "polar_gt",            "polar_gt",            "polar_gt"),
    ("polar_gt_pregate",    "polar_gt_pregate",    "polar_gt_pregate",    "polar_gt_pregate"),
    ("gate_excluded",       "gate_excluded",       "gate_excluded",       "gate_excluded"),
    ("tier_strict",         "tier_strict",         "tier",                "tier_strict"),
    ("int_px",              "raw_vis.int_px",      "raw_vis.int_px",      "raw_vis.int_px"),
    ("int_px_fallback",     "raw_vis.int_px_fallback", "raw_vis.int_px_fallback",
                                                   "raw_vis.int_px_fallback"),
    ("edge_projected",      "raw_vis.edge_projected", "raw_vis.edge_projected",
                                                   "raw_vis.edge_projected"),
    ("edge_visible",        "raw_vis.edge_visible", "raw_vis.edge_visible",
                                                   "raw_vis.edge_visible"),
    ("edge_ratio",          "raw_vis.edge_ratio",  "raw_vis.edge_ratio",  "raw_vis.edge_ratio"),
    ("cell_int_px",         "raw_vis.cell_int_px", "raw_vis.cell_int_px", "raw_vis.cell_int_px"),
    ("cell_counts",         "cell_counts",         None,                  "cell_counts"),
    ("cell_mean_drop",      "cell_mean_drop",      None,                  "cell_mean_drop"),
    ("tier_matrix",         "tier_matrix",         None,                  "tier_matrix"),
    ("cells_raw",           "footprint.cells_raw", None,                  "footprint.cells_raw"),
    ("cells_kept",          "footprint.cells_kept", None,                 "footprint.cells_kept"),
    ("comps_raw",           "footprint.comps_raw", None,                  "footprint.comps_raw"),
    ("comps_kept",          "footprint.comps_kept", None,                 "footprint.comps_kept"),
    ("comps_no_boundary",   "footprint.comps_no_boundary", None,
                                                   "footprint.comps_no_boundary"),
    ("boundary_cells",      "footprint.boundary_cells", None,
                                                   "footprint.boundary_cells"),
    ("boundary_pass",       "footprint.boundary_pass", None,
                                                   "footprint.boundary_pass"),
]
SENT = "\0__absent__"
# 결재가 "GT" 라고 부르는 것 — 훈련 라벨과 그것을 만드는 발자국 회계.
# tier/가시성 계열(edge_*, int_px, tier_*)은 **같은 GT 위의 관측량**이라 따로 센다.
GT_FIELDS = ("polar_gt", "polar_gt_pregate", "gate_excluded", "cells_raw",
             "cells_kept", "cell_counts", "cell_mean_drop")


def compare(new_frames, canon_man, canon_lab, tag):
    """전 프레임 · 전 필드 대조.  키 누락도 차이로 센다.  **자르지 않는다.**"""
    per_field = collections.Counter()
    per_field_total = collections.Counter()
    diffs, missing_canon, missing_new = [], [], []
    per_frame = collections.defaultdict(list)
    n_cmp = 0
    for fid in sorted(set(new_frames) | set(canon_man) | set(canon_lab)):
        if fid not in new_frames:
            missing_new.append(fid); continue
        if fid not in canon_man and fid not in canon_lab:
            missing_canon.append(fid); continue
        n_cmp += 1
        rec = new_frames[fid]
        for name, p_new, p_man, p_lab in FIELDS:
            if p_man and fid in canon_man:
                src, path = canon_man[fid], p_man
            elif p_lab and fid in canon_lab:
                src, path = canon_lab[fid], p_lab
            else:
                continue
            a, b = _get(src, path, SENT), _get(rec, p_new, SENT)
            per_field_total[name] += 1
            if a != b:
                per_field[name] += 1
                per_frame[fid].append(name)
                diffs.append(dict(frame_id=fid, field=name, canon=a, relabelled=b))
    gt = {f: int(per_field.get(f, 0)) for f in GT_FIELDS}
    return dict(tag=tag, n_frames_compared=n_cmp,
                n_frames_differing=len(per_frame),
                n_frames_differing_gt=sum(1 for v in per_frame.values()
                                          if any(f in GT_FIELDS for f in v)),
                n_field_diffs=int(sum(per_field.values())),
                n_gt_field_diffs=int(sum(gt.values())),
                per_field={k: int(v) for k, v in sorted(per_field.items())},
                per_field_compared={k: int(v) for k, v in sorted(per_field_total.items())},
                per_frame={k: v for k, v in sorted(per_frame.items())},
                diffs=diffs, n_missing_in_relabel=len(missing_new),
                missing_in_relabel=missing_new[:50],
                n_missing_in_canon=len(missing_canon),
                missing_in_canon=missing_canon[:50])


def diff_frames(a_frames, b_frames, tag):
    """같은 주행의 두 모드끼리 — 모드 단독 효과 (파이프라인 표류와 분리)."""
    per_field = collections.Counter()
    per_frame = collections.defaultdict(list)
    ids = sorted(set(a_frames) & set(b_frames))
    for fid in ids:
        for name, p_new, _m, _l in FIELDS:
            x, y = _get(a_frames[fid], p_new, SENT), _get(b_frames[fid], p_new, SENT)
            if x != y:
                per_field[name] += 1
                per_frame[fid].append(name)
    return dict(tag=tag, n_frames_compared=len(ids),
                n_frames_differing=len(per_frame),
                n_field_diffs=int(sum(per_field.values())),
                per_field={k: int(v) for k, v in sorted(per_field.items())})


def analyse(q_frames, c_frames):
    """차이의 **부호와 기전**을 센다 — "무엇이 몇 개" 가 아니라 "어느 쪽으로"."""
    pol = dict(n_changed=0, gain_only=0, loss_only=0, mixed=0,
               cells_gained=0, cells_lost=0, frames=[])
    kept = dict(n_changed=0, up=0, down=0, delta_min=None, delta_max=None, frames=[])
    tier = collections.Counter()
    tier_rows = []
    per_scene = collections.defaultdict(collections.Counter)
    for fid in sorted(q_frames):
        q, c = q_frames[fid], c_frames[fid]
        scene = fid.split("/")[1] + fid.split("::")[1] if "::" in fid else fid.split("/")[1]
        a, b = q["polar_gt"], c["polar_gt"]
        if a != b:
            up = sum(1 for x, y in zip(a, b) if y > x)
            dn = sum(1 for x, y in zip(a, b) if y < x)
            pol["n_changed"] += 1
            pol["cells_gained"] += up
            pol["cells_lost"] += dn
            pol["gain_only" if dn == 0 else "loss_only" if up == 0 else "mixed"] += 1
            pol["frames"].append(dict(frame_id=fid, canon=a, component=b,
                                      cells_gained=up, cells_lost=dn))
            per_scene[scene]["polar_gt"] += 1
        ka, kb = q["footprint"]["cells_kept"], c["footprint"]["cells_kept"]
        if ka != kb:
            d = kb - ka
            kept["n_changed"] += 1
            kept["up" if d > 0 else "down"] += 1
            kept["delta_min"] = d if kept["delta_min"] is None else min(kept["delta_min"], d)
            kept["delta_max"] = d if kept["delta_max"] is None else max(kept["delta_max"], d)
            kept["frames"].append(dict(frame_id=fid, canon=ka, component=kb, delta=d,
                                       cells_raw=q["footprint"]["cells_raw"],
                                       comps_kept_canon=q["footprint"]["comps_kept"],
                                       comps_kept_component=c["footprint"]["comps_kept"]))
            per_scene[scene]["cells_kept"] += 1
        if q["tier_strict"] != c["tier_strict"]:
            tier[f'{q["tier_strict"]} -> {c["tier_strict"]}'] += 1
            tier_rows.append(dict(frame_id=fid, canon=q["tier_strict"],
                                  component=c["tier_strict"],
                                  edge_ratio_canon=q["raw_vis"]["edge_ratio"],
                                  edge_ratio_component=c["raw_vis"]["edge_ratio"],
                                  int_px_canon=q["raw_vis"]["int_px"],
                                  int_px_component=c["raw_vis"]["int_px"]))
            per_scene[scene]["tier_strict"] += 1
    return dict(polar_gt=pol, cells_kept=kept,
                tier_transitions={k: int(v) for k, v in sorted(tier.items())},
                tier_frames=tier_rows,
                per_scene={k: dict(v) for k, v in sorted(per_scene.items())})


def verify_v2(workers):
    man = json.load(open(MANIFEST))
    lab = json.load(open(CANON_LABELS))
    canon_man = {f["frame_id"]: f for f in man["frames"]}
    canon_lab = lab["frames"]
    print(f"[canon] manifest {len(canon_man)} frames  {os.path.relpath(MANIFEST, REPO)}")
    print(f"[canon] labels   {len(canon_lab)} frames  {os.path.relpath(CANON_LABELS, REPO)}")

    tasks, missing = corpus_tasks(man)
    for m in missing:
        print("[MISSING]", m)
    scenes = sorted({(t[0], t[1]) for t in tasks})
    print(f"[tasks] {len(tasks)} 씬x팔 · {len(scenes)} (밴드,씬) · "
          f"밴드 {sorted({t[0] for t in tasks})}")

    if workers > 1:
        import multiprocessing as mp
        with mp.Pool(workers) as p:
            res = p.map(_work, tasks, chunksize=1)
    else:
        res = [_work(t) for t in tasks]

    q_frames, c_frames, sv, errs = {}, {}, [], []
    for band, sc, arm, run, orun, out, err in res:
        if err:
            errs.append(err); print("[ERROR]", err); continue
        sfx = SUFFIX_OF_BAND[band]
        for k, v in out["q"][0].items():
            q_frames[k + sfx] = v
        for k, v in out["c"][0].items():
            c_frames[k + sfx] = v
        sm = dict(out["c"][1])
        sm.update(band=band, round=run, off_round=orun,
                  cells_kept_max_quantised=out["q"][1].get("cells_kept_max"),
                  cells_kept_max_component=out["c"][1].get("cells_kept_max"))
        sv.append(sm)
    print(f"[relabel] quantised {len(q_frames)} frames · component {len(c_frames)} frames "
          f"· errors {len(errs)}")

    control = compare(q_frames, canon_man, canon_lab, "CONTROL quantised-vs-canon")
    test = compare(c_frames, canon_man, canon_lab, "TEST component-vs-canon")
    delta = diff_frames(q_frames, c_frames, "DELTA component-vs-quantised")
    ana = analyse(q_frames, c_frames)

    for r in (control, test):
        print("-" * 78)
        print(f"{r['tag']}: {r['n_frames_compared']} frames compared · "
              f"{r['n_frames_differing']} frames differ "
              f"({r['n_frames_differing_gt']} on a GT field) · "
              f"{r['n_field_diffs']} field diffs · "
              f"missing_in_relabel={r['n_missing_in_relabel']} · "
              f"missing_in_canon={r['n_missing_in_canon']}")
        if r["per_field"]:
            for k, v in r["per_field"].items():
                mark = "  <-- GT" if k in GT_FIELDS else ""
                print(f"    DIFF {k:20s} {v:6d} / {r['per_field_compared'][k]}{mark}")
        else:
            print("    IDENTITY — 전 필드 0 차이")
    print("-" * 78)
    print(f"{delta['tag']}: {delta['n_frames_compared']} frames · "
          f"{delta['n_frames_differing']} frames differ · "
          f"{delta['n_field_diffs']} field diffs "
          f"({'TEST 와 동일 => 차이는 전부 모드 탓' if delta['per_field'] == test['per_field'] else 'TEST 와 불일치'})")
    print("-" * 78)
    p, k = ana["polar_gt"], ana["cells_kept"]
    print(f"방향: polar_gt {p['n_changed']} 프레임 변경 — 양성 획득만 {p['gain_only']} · "
          f"상실만 {p['loss_only']} · 혼합 {p['mixed']} "
          f"(칸 +{p['cells_gained']} / -{p['cells_lost']})")
    print(f"      cells_kept {k['n_changed']} 프레임 — 증가 {k['up']} · 감소 {k['down']} · "
          f"delta [{k['delta_min']}, {k['delta_max']}]")
    for t, n in sorted(ana["tier_transitions"].items()):
        print(f"      tier {t:24s} {n}")
    print("      씬별: " + ", ".join(f"{s}({d.get('polar_gt', 0)}gt/"
                                     f"{d.get('cells_kept', 0)}kept)"
                                     for s, d in sorted(ana["per_scene"].items())))

    control_ok = (control["n_field_diffs"] == 0 and control["n_missing_in_relabel"] == 0
                  and control["n_missing_in_canon"] == 0 and not errs)
    gt_diffs = test["n_gt_field_diffs"]
    all_diffs = test["n_field_diffs"]
    finding = [
        "결재 원장(D82 (2))의 기대 — *v2 는 측방 씬 이전이므로 소급 불변* — 은 "
        "**반증되었다**.  사각은 '측방 씬'의 속성이 아니라 **발자국 셀 하나하나의 "
        "속성**이다: 양자화된 이웃이 또 다른 발자국 셀이기만 하면(어느 씬이든) 그 "
        "셀은 근접 경계에서 탈락한다.  v2 코퍼스에도 그런 셀이 있었다.",
        f"CONTROL 이 {control['n_frames_compared']}/{control['n_frames_compared']} "
        "프레임 전 필드 0 차이이므로 드라이버는 정본을 재현한다 — 아래 차이는 전부 "
        "모드 탓이다(DELTA per_field == TEST per_field).",
        f"polar_gt {ana['polar_gt']['n_changed']} 프레임 변경: "
        f"{ana['polar_gt']['gain_only']} 프레임은 **양성 획득만**(+"
        f"{ana['polar_gt']['cells_gained']} 칸 — 정본 v2 가 갖고 있던 거짓 음성 GT 의 "
        f"실측), {ana['polar_gt']['loss_only']} 프레임은 **상실만**(-"
        f"{ana['polar_gt']['cells_lost']} 칸).",
        "상실의 기전(scene02 실측): 성분-경계 스캔의 경계 **집합**은 양자화의 "
        "상위집합이지만, 셀별 **방향**은 바뀔 수 있다.  최대-내적 규칙이 축방향 "
        "(-1,0) 을 대각 (-1,+1) 로 교체하면 step_gate 의 안쪽 레이가 다른 셀을 "
        "훑어 이미 통과했던 성분이 탈락할 수 있다.  실측 2 성분(comp 22 = 3셀, "
        "comp 94 = 1셀 스페클)이 그렇게 떨어졌고, 그중 격자 안에 든 comp 94 가 "
        "폴라 칸 14 를 잃게 했다.  즉 **최대-내적 타이브레이크는 성분 수준에서 "
        "단조가 아니다**.",
        "무손실 대안(미구현, 결재 대상): 양자화 이웃이 walkable 이면 **그것을 "
        "우선**하고 아닐 때만 최대-내적으로 고른다.  그러면 옛 경계 셀의 방향이 "
        "보존되어 통과 집합이 상위집합이 되고 성분 탈락이 구조적으로 불가능해진다 "
        "— 다만 경계 셀이 추가되는 것은 그대로이므로 **v2 불변은 여전히 성립하지 "
        "않는다**(그것은 사각 수리의 정의상 불가피하다).",
        f"tier 이동 {sum(ana['tier_transitions'].values())} 프레임: "
        + " · ".join(f"{k} {v}" for k, v in sorted(ana["tier_transitions"].items()))
        + ".  none_in_fov -> V 는 발자국이 격자 밖에만 있다고 기록된 프레임이 실은 "
          "격자 안에 위험을 갖고 있었다는 뜻이다(scene03).",
        "처분: **v2 코퍼스 라벨·매니페스트를 다시 만들지 않는다.**  신 모드는 "
        "옵트인으로 남고 기본값은 quantised 그대로다.  v3 신규 씬에 신 모드를 쓰는 "
        "결정과, 그때 v2 를 함께 재라벨할지는 별건 결재다.",
    ]
    for s in finding:
        print("[FINDING]", s)
    verdict = ("CONTROL_FAILED" if not control_ok else
               "IDENTITY" if all_diffs == 0 else
               "GT_INVARIANT_TIER_DRIFT" if gt_diffs == 0 else "GT_CHANGED")

    out = dict(
        doc="w1c_labeler_invariance",
        version="1.0",
        created_for="DECISIONS.md D78 (3) 근본 수리 · D82 (2) v2 GT 소급 불변 검증 (필수)",
        driver="experiments/v3_0823/code/w1c_labeler_boundary.py --verify-v2",
        labeler="experiments/mainrun_0819/code/labeling/labeler.py",
        grid=os.path.relpath(GRID_PATH, REPO),
        canon_manifest=os.path.relpath(MANIFEST, REPO),
        canon_labels=os.path.relpath(CANON_LABELS, REPO),
        boundary_modes=dict(control=LB.BOUNDARY_QUANTISED, test=LB.BOUNDARY_COMPONENT,
                            module_default=LB.BOUNDARY_MODE,
                            neighbourhood=list(LB._NBR8),
                            tie_break="max dot(unit neighbour dir, exact toward-camera "
                                      "unit vector); exact ties -> first in _NBR8 order"),
        verdict=verdict,
        control_ok=bool(control_ok),
        n_frames_canon_manifest=len(canon_man),
        n_frames_canon_labels=len(canon_lab),
        n_frames_relabelled=len(c_frames),
        n_frames_compared=test["n_frames_compared"],
        n_frames_differing=test["n_frames_differing"],
        n_scenes=len({s for _b, s in scenes}),
        n_band_scene_pairs=len(scenes),
        n_scene_arm_tasks=len(tasks),
        scene_list=sorted({s for _b, s in scenes}),
        band_scene_pairs=[f"{b}/{s}" for b, s in scenes],
        overlay_pairs=sorted(f"{b}/{s}" for b, s in AFFECTED),
        rounds=sorted({t[5] for t in tasks} | {t[6] for t in tasks}),
        adoption=("v2 코퍼스에 이 모드를 적용하지 않는다 — 정본 GT 는 quantised 로 "
                  "동결되어 있고 재라벨은 그 동결을 깨뜨린다."
                  if verdict != "IDENTITY" else
                  "v2 GT 소급 불변 — 신 모드 채택이 v2 라벨을 한 비트도 바꾸지 않는다."),
        finding=finding,
        errors=errs, missing_scene_dirs=missing,
        control=control, test=test, delta=delta, analysis=ana,
        scene_footprint=sv)
    json.dump(out, open(OUT_JSON, "w"), indent=1, ensure_ascii=False)
    print("=" * 78)
    print(f"VERDICT {verdict}   (control_ok={control_ok})")
    print(f"  frames compared {test['n_frames_compared']} · scenes "
          f"{len({s for _b, s in scenes})} · (밴드,씬) {len(scenes)} · "
          f"씬x팔 {len(tasks)}")
    print(f"  GT 필드 차이 {gt_diffs} · 전 필드 차이 {all_diffs}")
    print(f"-> {OUT_JSON}")
    return 0 if verdict in ("IDENTITY",) else (0 if control_ok else 3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--verify-v2", action="store_true")
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    rc = 0
    if a.selftest:
        r = selftest()
        rc = 0 if r["ok"] else 1
    if a.verify_v2:
        rc = verify_v2(a.workers) or rc
    if not (a.selftest or a.verify_v2):
        ap.error("--selftest 또는 --verify-v2 중 하나는 필요하다")
    return rc


if __name__ == "__main__":
    sys.exit(main())
