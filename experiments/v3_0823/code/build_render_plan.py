#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_render_plan.py — emit experiments/v3_0823/render_plan_v3.json and print
every table RENDER_PLAN_V3.md quotes, so the document and the machine-readable
matrix can never drift.

CPU only. Reads: experiments/v3_0823/dataset_manifest_v2corr.json (corrected GT,
G7_RELABEL §0 canon B) for the A-arm frame accounting. Writes exactly one file.

    python3 experiments/v3_0823/code/build_render_plan.py
"""
from __future__ import annotations

import collections
import json
import math
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
OUT = os.path.join(REPO, "experiments", "v3_0823", "render_plan_v3.json")
MANIFEST = os.path.join(REPO, "experiments", "v3_0823",
                        "dataset_manifest_v2corr.json")

# --- measured render constants ----------------------------------------------
# s/cut is WALL and GPU-serialised (flock), pooled over 136 clean 24-cut
# invocations of 260819_main + 260820_boost. See RENDER_PLAN_V3.md §4.1.
S_PER_CUT_MEAN, S_PER_CUT_P90 = 5.84, 7.65
MB_PER_CUT = 8.75          # rgb png 4.1 + depth npy 4.15 + idseg npz 0.05

# ===========================================================================
# 1. existing 33-scene library
# ===========================================================================
# rounds an on-arm frame of this scene exists in (= what a new arm must twin)
BOOST_H = {"scene14", "scene15", "scene09", "scene17"}
BOOST_E = {"scene05", "scene07", "scene14", "scene15", "scene18", "sceneC4",
           "scene20", "sceneC1", "scene09", "scene17", "scene03", "scene04",
           "scene12", "scene08"}
BOOST_E2 = {"scene05", "scene03", "scene04", "scene20", "scene12", "scene18",
            "sceneC4", "scene07"}

SPLIT = {  # split_v2_full.json, via CUE_COVERAGE.md §1.2
    "scene01": "train", "scene02": "train", "scene03": "train",
    "scene04": "train", "scene05": "test-core", "scene06": "train",
    "scene07": "test-core", "scene08": "val", "scene09": "train",
    "scene10": "train", "scene11": "hold", "scene12": "train",
    "scene13": "hold", "scene14": "test-core", "scene15": "test-core",
    "scene16": "train", "scene17": "train", "scene18": "test-core",
    "scene19": "hold", "scene20": "val", "scene21": "train",
    "sceneC1": "train", "sceneC2": "test-core", "sceneC4": "train",
    "sceneD1": "train", "sceneD2": "train", "sceneD3": "val",
    "sceneD4": "hold", "sceneN1": "train", "sceneN2": "train",
    "sceneN3": "test-core", "sceneN4": "train", "sceneN5": "train",
}
# CUE_COVERAGE.md §2.1 "C팔 결속" column
BOND = {
    "scene01": "free", "scene02": "HZ", "scene03": "HZ", "scene04": "free",
    "scene05": "HZpart", "scene06": "HZpart", "scene07": "HZ",
    "scene08": "HZpart", "scene09": "free", "scene10": "HZpart",
    "scene11": "HZpart", "scene12": "HZpart", "scene13": "HZpart",
    "scene14": "HZpart", "scene15": "HZpart", "scene16": "HZpart",
    "scene17": "HZpart", "scene18": "HZpart", "scene19": "HZpart",
    "scene20": "HZpart", "scene21": "HZpart", "sceneC1": "HZpart",
    "sceneC2": "free", "sceneC4": "HZpart", "sceneD1": "HZpart",
    "sceneD2": "HZpart", "sceneD3": "HZpart", "sceneD4": "HZpart",
    "sceneN1": "free", "sceneN2": "HZpart", "sceneN3": "free",
    "sceneN4": "free", "sceneN5": "free",
}
# CUE_COVERAGE.md §2.2-(4): cue_material_break rebinds material only (no prim
# created/deleted) => heightmap bit-identity is guaranteed by construction.
MATERIAL_ONLY = {
    "scene01", "scene02", "scene03", "scene04", "scene07", "scene08",
    "scene09", "scene10", "scene12", "scene13", "scene14", "scene15",
    "scene16", "scene17", "scene20", "scene21", "sceneC1", "sceneC2",
    "sceneC4", "sceneD1", "sceneD2", "sceneD3", "sceneN3", "sceneN4",
}
# scenes with no drop at all (CUE_COVERAGE §1.2 "무낙차")
NO_DROP = {"sceneN1", "sceneN2", "sceneN3", "sceneN4", "sceneN5"}
# CUE_COVERAGE.md §3-(b): already adjudicated DECORATIVE by two-arm labeller
ADJUDICATED_DECOR = {
    "scene12": ["cue_railing", "cue_scene_dressing"],
    "scene17": ["cue_scene_dressing", "cue_material_break"],
}
ZONE = {  # 생활권 유형 — OVERNIGHT_BRIEF_0819_v3.md:110
    "scene01": "캠퍼스", "scene02": "보도", "scene03": "제방·수변",
    "scene04": "제방·수변", "scene06": "보도", "scene08": "보도",
    "scene09": "제방·수변", "scene10": "캠퍼스", "scene12": "제방·수변",
    "scene16": "캠퍼스", "scene17": "제방·수변", "scene20": "보도",
    "scene21": "보도", "sceneC1": "캠퍼스", "sceneC4": "캠퍼스",
    "sceneD1": "보도", "sceneD2": "보도", "sceneD3": "농로",
    "sceneN1": "보도", "sceneN2": "보도", "sceneN4": "보도", "sceneN5": "보도",
}

CONDS = ["L0", "L5", "L7"]          # production trio, gate-forced
CAMS = 8
BANDS = {                            # camera (d,h) bands; run_data_render.py:604
    "base": None,
    "H": {"d_min": 6, "d_max": 12, "h_min": 0.25, "h_max": 1.0},
    "E": {"d_min": 6, "d_max": 12, "h_min": 1.2, "h_max": 1.9},
    "E2": {"d_min": 4, "d_max": 9, "h_min": 0.3, "h_max": 0.9},
    "LAT": {"d_min": 3, "d_max": 10, "h_min": 0.4, "h_max": 1.4},
}


def existing_bands(s):
    b = ["base"]
    if s in BOOST_H:
        b.append("H")
    if s in BOOST_E:
        b.append("E")
    if s in BOOST_E2:
        b.append("E2")
    return b


# ===========================================================================
# 2. new scenes
# ===========================================================================
# arms: 4 = A/B/C/D · 2 = C/D only (no plausible hazard sibling at that site)
NEW = [
    # --- test-ext (eval only, 4 arms complete, DZ §12-9) --------------------
    dict(key="sceneH1_berm_levee", role="test-ext", zone="제방·수변",
         family="paired-H 둔덕형", bands=["base", "H"], arms=4, wave="A",
         conceal="제방 어깨 둔덕 마루가 하천측 낙차 개구를 가림",
         ladder=None, edge_owner="둔덕 마루(BermCrest) 솔리드"),
    dict(key="sceneH2_landing_campus", role="test-ext", zone="캠퍼스",
         family="paired-H 계단참형", bands=["base", "H"], arms=4, wave="A",
         conceal="중간 계단참 상단 코가 하행 단 전체를 가림",
         ladder=None, edge_owner="계단참 상단 슬래브(LandingSlab)"),
    dict(key="sceneH3_bend_walk", role="test-ext", zone="보도",
         family="paired-H 복도 굴절형", bands=["base", "H"], arms=4, wave="A",
         conceal="옹벽 굴절 모서리가 굴절 너머 하행 계단을 가림",
         ladder=None, edge_owner="굴절 옹벽 모서리(BendWall)"),
    dict(key="sceneH4_berm_farm", role="test-ext", zone="농로",
         family="paired-H 둔덕형", bands=["base", "H"], arms=4, wave="B",
         conceal="논둑 마루가 배수로 낙차를 가림",
         ladder=None, edge_owner="논둑 마루(LeveeCrest)"),
    dict(key="sceneL1_lateral_canal", role="test-ext", zone="제방·수변",
         family="측방 위험", bands=["base", "LAT"], arms=4, wave="A",
         conceal="측방(섹터 A/E) 수로 — 정면 시야 밖 위험",
         ladder=None, edge_owner="측방 제방 어깨"),
    dict(key="sceneL2_lateral_ditch", role="test-ext", zone="농로",
         family="측방 위험", bands=["base", "LAT"], arms=4, wave="C",
         conceal="측방 배수구", ladder=None, edge_owner="갓길 노견"),
    dict(key="sceneN9_busstop_tactile", role="test-ext", zone="보도",
         family="N-cue ★3", bands=["base", "base2"], arms=4, wave="A",
         conceal=None, ladder="L6 정류장 경고블록", edge_owner=None),
    dict(key="sceneN11_ground_pattern", role="test-ext", zone="보도",
         family="N-cue ★4", bands=["base", "base2"], arms=4, wave="A",
         conceal=None, ladder="L10 지면문양 삼중주(맨홀+수목격자+신축이음)",
         edge_owner=None),
    dict(key="sceneN12_weak_stack", role="test-ext", zone="보도",
         family="N-cue ★5", bands=["base", "base2"], arms=4, wave="B",
         conceal=None, ladder="L12 약단서 중첩(볼록거울+시선유도봉+그림자)",
         edge_owner=None),
    # --- new TRAINING scenes ------------------------------------------------
    dict(key="sceneH5_landing_campus2", role="train", zone="캠퍼스",
         family="paired-H 계단참형", bands=["base", "H"], arms=4, wave="B",
         conceal="계단참", ladder=None, edge_owner="계단참 상단 슬래브"),
    dict(key="sceneH6_berm_levee2", role="val", zone="제방·수변",
         family="paired-H 둔덕형", bands=["base", "H", "H2"], arms=4, wave="A",
         conceal="제방 둔덕", ladder=None, edge_owner="둔덕 마루",
         note="val strict-H ≥ 30 공급원 (DZ §4.3-3 선택지표 수리의 전제)"),
    dict(key="sceneE1_farrim_levee", role="train", zone="제방·수변",
         family="E 원거리", bands=["base", "E"], arms=4, wave="B",
         conceal=None, ladder=None, edge_owner=None),
    dict(key="sceneE2_farrim_walk", role="val", zone="보도",
         family="E 원거리", bands=["base", "E"], arms=4, wave="C",
         conceal=None, ladder=None, edge_owner=None),
    dict(key="sceneN6_planter_rail", role="train", zone="캠퍼스",
         family="N-cue ★1", bands=["base", "base2"], arms=4, wave="B",
         conceal=None, ladder="L1 화단 난간", edge_owner=None),
    dict(key="sceneN7_bollard_row", role="train", zone="보도",
         family="N-cue ★1", bands=["base", "base2"], arms=2, wave="C",
         conceal=None, ladder="L2 볼라드 열", edge_owner=None),
    dict(key="sceneN8_curbramp_tactile", role="train", zone="보도",
         family="N-cue ★3", bands=["base", "base2"], arms=4, wave="B",
         conceal=None, ladder="L5 턱낮춤+점형블록", edge_owner=None),
    dict(key="sceneN10_level_handrail", role="val", zone="캠퍼스",
         family="N-cue ★3", bands=["base", "base2"], arms=2, wave="C",
         conceal=None, ladder="L7 평지 복도 손잡이", edge_owner=None),
    # --- diagnostic only (NOT trained, DZ §12-8 부칙 1) ---------------------
    dict(key="sceneC2r_leaf_redesign", role="diag", zone="캠퍼스",
         family="sceneC2 재설계", bands=["base", "POSE"], arms=2, wave="C",
         conceal=None, ladder=None, edge_owner=None,
         note="경사 통계 정규화 + 포즈 다양화. 진단·대조 전용, 훈련 미편입"),
]


# ===========================================================================
# 3. build the matrix
# ===========================================================================
def load_a_arm():
    """(frames_by_scene, hazpos_by_scene) from the corrected-GT manifest."""
    mf = json.load(open(MANIFEST, encoding="utf-8"))
    fr = mf["frames"] if isinstance(mf, dict) else mf
    n, hz = collections.Counter(), collections.Counter()
    for f in fr:
        if f["tier"] == "off":
            continue
        n[f["scene_id"]] += 1
        if f["tier"] != "none_in_fov":
            hz[f["scene_id"]] += 1
    return n, hz


def main():
    a_frames, a_hazpos = load_a_arm()
    train_lib = sorted([s for s, sp in SPLIT.items() if sp in ("train", "val")])
    scenes, cuts = [], collections.Counter()

    for s in train_lib:
        n = a_frames[s]
        bands = existing_bands(s)
        assert n == 24 * len(bands), (s, n, bands)
        drop = s not in NO_DROP
        b_ok = drop and s in MATERIAL_ONLY
        port = BOND[s] != "free"
        d_reuse = BOND[s] == "HZ"          # 구off scope == cue_* scope candidate
        arms = {}
        on_rounds = (["260819_main_on"] +
                     [f"260820_boost_{b.lower()}_on" for b in bands
                      if b != "base"])
        if not drop:
            # 무낙차 씬: the existing ON arm IS a C arm by fact (cue present,
            # no drop anywhere) — its `hazard_*` key builds a TRAP, not a drop.
            # Nothing to remove, so no new C render; only D is missing.
            arms["C"] = dict(source="reuse", new_cuts=0, frames=n,
                             rounds=on_rounds,
                             recipe={"hazard": False, "cue": True},
                             note="무낙차 씬 — v2 on팔이 그대로 C팔")
            arms["D"] = dict(source="new", new_cuts=n, frames=n,
                             rounds=["260826_v3w1_lib_D"],
                             recipe={"hazard": False, "cue": False})
            for k, v in arms.items():
                cuts[f"w1_{k}"] += v["new_cuts"]
            scenes.append(dict(
                scene=s, origin="existing", role=SPLIT[s], zone=ZONE.get(s),
                drop_bearing=False, bond=BOND[s], bands=bands, conds=CONDS,
                cams=CAMS, a_frames=0, a_hazard_pos_frames=0,
                keep_dressing_port=False, b_lever_clean=False, arms=arms))
            continue
        arms["A"] = dict(source="reuse", new_cuts=0, frames=n,
                         rounds=on_rounds,
                         recipe={"hazard": True, "cue": True})
        if b_ok:
            lev = ["cue_material_break"]
            lev += [c for c in ADJUDICATED_DECOR.get(s, [])
                    if c != "cue_material_break"]
            arms["B"] = dict(source="new", new_cuts=n, frames=n,
                             rounds=["260826_v3w1_lib_B"], lever=lev,
                             recipe={"hazard": True, "cue": False})
        arms["C"] = dict(source="new", new_cuts=n, frames=n,
                         rounds=["260826_v3w1_lib_C"],
                         needs_keep_dressing_port=port,
                         recipe={"hazard": False, "cue": True,
                                 "keep_dressing": True})
        arms["D"] = dict(source="new", new_cuts=0 if d_reuse else n, frames=n,
                         rounds=(["260819_main_off"] if d_reuse
                                 else ["260826_v3w1_lib_D"]),
                         guoff_reuse_candidate=d_reuse,
                         gate="VG-04" if d_reuse else None,
                         recipe={"hazard": False, "cue": False})
        for k, v in arms.items():
            cuts[f"w1_{k}"] += v["new_cuts"]
        scenes.append(dict(
            scene=s, origin="existing", role=SPLIT[s], zone=ZONE.get(s),
            drop_bearing=drop, bond=BOND[s], bands=bands, conds=CONDS,
            cams=CAMS, a_frames=n, a_hazard_pos_frames=a_hazpos[s],
            keep_dressing_port=port, b_lever_clean=b_ok, arms=arms))

    for d in NEW:
        nb = len(d["bands"])
        per_arm = 24 * nb
        arms = {}
        names = ["A", "B", "C", "D"] if d["arms"] == 4 else ["C", "D"]
        if d["key"].startswith("sceneC2r"):
            names = ["A", "C"]
        wv = {"A": "w3" if d["role"] == "test-ext" else "w2",
              "B": "w3" if d["role"] == "test-ext" else "w2"}
        stem = ("260830_v3w3_ext" if d["role"] == "test-ext"
                else "260831_v3w4_diag" if d["role"] == "diag"
                else "260828_v3w2_new")
        for k in names:
            arms[k] = dict(source="new", new_cuts=per_arm, frames=per_arm,
                           rounds=[f"{stem}_{k}"],
                           recipe={"hazard": k in ("A", "B"),
                                   "cue": k in ("A", "C")})
            tag = ("w3" if d["role"] == "test-ext"
                   else "w4" if d["role"] == "diag" else "w2")
            cuts[f"{tag}_{k}"] += per_arm
        scenes.append(dict(
            scene=d["key"], origin="new", role=d["role"], zone=d["zone"],
            family=d["family"], drop_bearing=d["arms"] == 4 or "H" in d["key"],
            bands=d["bands"], conds=CONDS, cams=CAMS,
            wave=d["wave"], ladder=d.get("ladder"),
            concealment=d.get("conceal"), edge_owner=d.get("edge_owner"),
            note=d.get("note"), a_frames=per_arm if "A" in names else 0,
            keep_dressing_port=False, b_lever_clean=True, arms=arms))

    # --- classification probe (VG-CLS) -------------------------------------
    # high-priority (scene x cue) pairs of CUE_COVERAGE §3-(b) restricted to the
    # 22 library scenes this plan actually toggles. 4 cams x 1 cond x 2 arms.
    CLS_PAIRS = [
        ("scene01", "cue_railing"), ("scene02", "cue_railing"),
        ("scene06", "cue_railing"), ("scene08", "cue_railing"),
        ("scene10", "cue_railing"), ("scene16", "cue_railing"),
        ("scene21", "cue_railing"), ("sceneC1", "cue_railing"),
        ("sceneC4", "cue_railing"),
        ("scene02", "cue_nosing"), ("scene16", "cue_nosing"),
        ("scene21", "cue_nosing"), ("sceneC1", "cue_nosing"),
        ("sceneD1", "cue_nosing"),
        ("sceneC1", "cue_tactile"), ("sceneC4", "cue_tactile"),
        ("scene06", "cue_material_break"), ("sceneN1", "cue_material_break"),
        ("sceneN2", "cue_material_break"), ("sceneN5", "cue_material_break"),
    ]
    cls_cuts = len(CLS_PAIRS) * 2 * 4
    cuts["w0_cls"] = cls_cuts

    # ===================================================================
    # 4. |r| — frame-level cue x hazard contingency over the TRAINING corpus
    # ===================================================================
    tr = [s for s in scenes if s["role"] in ("train", "val")]
    cell = collections.Counter()
    for s in tr:
        for k, v in s["arms"].items():
            cell[k] += v["frames"]
    A, B, C, D = cell["A"], cell["B"], cell["C"], cell["D"]

    def phi(a, b, c, d):
        den = math.sqrt((a + b) * (c + d) * (a + c) * (b + d))
        return 0.0 if den == 0 else (a * d - b * c) / den

    r_recipe = phi(A, B, C, D)

    # --- FACT level. The 2x2 label the metric uses is the RENDERED FACT, not
    # the recipe name: a frame whose drop never lands in the 12 m polar grid is
    # hazard-ABSENT however its arm is named, so it belongs in the C (from A) or
    # D (from B) column. rho = P(hazard out of grid | hazard arm); measured on
    # the library's own corrected GT, assumed for new scenes.
    RHO_NEW = 0.10
    fA = fB = fC = fD = 0.0
    for s in tr:
        for k, v in s["arms"].items():
            f = v["frames"]
            if k in ("A", "B"):
                if s["origin"] == "existing":
                    hit = s["a_hazard_pos_frames"]      # A and B share GT (VG-01)
                    miss = f - hit
                else:
                    hit, miss = f * (1 - RHO_NEW), f * RHO_NEW
                if k == "A":
                    fA += hit
                    fC += miss
                else:
                    fB += hit
                    fD += miss
            elif k == "C":
                fC += f
            else:
                fD += f
    r_fact = phi(fA, fB, fC, fD)

    # sensitivity: cue-visibility asymmetry delta between the hazard half (A)
    # and the no-hazard half (C). mu = P(cue on screen | cue-on arm).
    MU = 0.75
    sens = []
    for dlt in (0.0, 0.05, 0.10, 0.20, 0.30, 0.35, 0.40):
        a2 = fA * MU
        b2 = fB + fA * (1 - MU)
        c2 = fC * (MU - dlt)
        d2 = fD + fC * (1 - MU + dlt)
        sens.append(dict(delta=dlt, r=round(abs(phi(a2, b2, c2, d2)), 4)))

    # arm x scene-origin correlation (D58 (2) 부칙: new confound watch)
    ex = [s for s in tr if s["origin"] == "existing"]
    nw = [s for s in tr if s["origin"] == "new"]

    def bd(lst):
        f = collections.Counter()
        for s in lst:
            for k, v in s["arms"].items():
                f["BD" if k in ("B", "D") else "AC"] += v["frames"]
        return f["BD"], f["AC"]
    ex_bd, ex_ac = bd(ex)
    nw_bd, nw_ac = bd(nw)
    r_origin = phi(ex_bd, ex_ac, nw_bd, nw_ac)
    # counterfactual: D58 Q1 read LITERALLY (B/D only from new scenes)
    r_origin_literal = phi(0, ex_ac, nw_bd, 0)

    total_new_cuts = sum(cuts.values())
    plan = dict(
        doc="render_plan_v3", version="1.0", date="2026-08-23", task="v3 P-5",
        governing=["experiments/mainrun_0819/DECISIONS.md D58",
                   "Docs/experiment/V3_DESIGN_0823.md §4, §12",
                   "experiments/v3_0823/ACCOUNTING.md §2, §4",
                   "experiments/v3_0823/CUE_COVERAGE.md",
                   "experiments/v3_0823/FA_REALITY.md §3"],
        conds=CONDS, cams=CAMS, bands=BANDS,
        gt_canon="experiments/v3_0823/dataset_manifest_v2corr.json (G7_RELABEL §0, 정본 B)",
        test_core_excluded=[s for s, sp in SPLIT.items() if sp == "test-core"],
        hold_excluded=[s for s, sp in SPLIT.items() if sp == "hold"],
        classification_probe=dict(pairs=CLS_PAIRS, cams=4, conds=["L0"],
                                  arms=2, cuts=cls_cuts, gate="VG-CLS"),
        scenes=scenes,
        cuts_by_wave_arm=dict(sorted(cuts.items())),
        totals=dict(
            new_cuts=total_new_cuts,
            reused_frames=sum(v["frames"] for s in scenes
                              for k, v in s["arms"].items()
                              if v["source"] == "reuse" or v["new_cuts"] == 0),
            training_frames=A + B + C + D,
            arms=dict(A=A, B=B, C=C, D=D),
            gpu_h_mean=round(total_new_cuts * S_PER_CUT_MEAN / 3600, 2),
            gpu_h_p90=round(total_new_cuts * S_PER_CUT_P90 / 3600, 2),
            disk_gb=round(total_new_cuts * MB_PER_CUT / 1024, 1)),
        correlation=dict(
            definition="6-key manipulable cue set {R,Ta,N,T,Sg,V}; frame-level "
                       "cue = idseg cue-prim pixels >= k (VG-11); frame-level "
                       "hazard = >=1 positive cell in corrected polar GT",
            target="|r| <= 0.2 (DZ §4.1)",
            predicted_recipe_level=round(abs(r_recipe), 4),
            predicted_frame_level=round(abs(r_fact), 4),
            frame_level_cells=dict(A=round(fA), B=round(fB),
                                   C=round(fC), D=round(fD)),
            rho_new_scene_assumed=0.10,
            sensitivity_to_cue_visibility_asymmetry=sens,
            arm_x_scene_origin=round(abs(r_origin), 4),
            arm_x_scene_origin_if_D58Q1_read_literally=round(
                abs(r_origin_literal), 4)),
        smoke=dict(round="260823_v3p5_segsmoke_A", scene="scene01",
                   annotator="instance_id_segmentation", result="PASS",
                   idseg_fetch="t0", n_ids_visible=100, idToLabels=491,
                   npz_bytes=48438, shape=[1080, 1920], dtype="uint16"),
    )
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=1)

    # ---------------- report -------------------------------------------
    print(f"wrote {os.path.relpath(OUT, REPO)}")
    print(f"\nscenes: {len(scenes)} "
          f"(existing {len([s for s in scenes if s['origin']=='existing'])} · "
          f"new {len([s for s in scenes if s['origin']=='new'])})")
    print(f"keep_dressing ports needed: "
          f"{sum(1 for s in scenes if s.get('keep_dressing_port'))}")
    print(f"구off->D reuse candidates: "
          f"{[s['scene'] for s in scenes if s['arms'].get('D',{}).get('guoff_reuse_candidate')]}")
    print("\ncuts by wave/arm:")
    for k, v in sorted(cuts.items()):
        print(f"   {k:10s} {v:6d}")
    print(f"   {'TOTAL':10s} {total_new_cuts:6d} new cuts")
    print(f"\nGPU-h  mean {plan['totals']['gpu_h_mean']}  "
          f"p90 {plan['totals']['gpu_h_p90']}   "
          f"disk {plan['totals']['disk_gb']} GB")
    print(f"\ntraining arms  A {A} · B {B} · C {C} · D {D}  "
          f"(= {A+B+C+D} frames, reuse {A} of them)")
    g = math.gcd(math.gcd(A, B), math.gcd(C, D))
    print(f"ratio A:B:C:D = {A/B:.2f} : 1.00 : {C/B:.2f} : {D/B:.2f}   "
          f"(DZ draft 3:2:3:2 = 1.50:1.00:1.50:1.00); gcd {g}")
    print(f"orthogonality identity  A/B = {A/B:.4f}  vs  C/D = {C/D:.4f}")
    print(f"\npredicted |r| (recipe level)      = {abs(r_recipe):.4f}")
    print(f"predicted |r| (FRAME/fact level)  = {abs(r_fact):.4f}"
          f"   cells A {fA:.0f} B {fB:.0f} C {fC:.0f} D {fD:.0f}")
    print("sensitivity to A/C cue-visibility asymmetry delta:")
    for row in sens:
        print(f"   delta {row['delta']:.2f} -> |r| {row['r']:.4f}"
              + ("   <-- target 0.2 breached" if row["r"] > 0.2 else ""))
    print(f"\narm x scene-origin |r|            = {abs(r_origin):.4f}")
    print(f"same, if D58 Q1 read literally    = {abs(r_origin_literal):.4f}"
          f"   (B/D from new scenes ONLY)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
