#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_corpus_v3.py — **v3 훈련 코퍼스 조립** (CPU 전용 · GPU 0 · 정본 픽셀 무접촉).

무엇을 만드나
-------------
  experiments/v3_0823/dataset_manifest_v3.json   훈련·검증 매니페스트 (편입분만)
  experiments/v3_0823/split_v3.json              씬 단위 분할 (polar_dataset 계약)
  experiments/v3_0823/corpus_v3_quarantine.json  **격리 원장** (제외분 전수 · 사유 포함)
  experiments/v3_0823/corpus_v3_census.json      회계 (팔×분할×tier·단서·무시마스크)

권위 (뒤가 이긴다)
------------------
  RENDER_PLAN_V3.md → 웨이브 보고서(W1D/W1B/W1B2_SEGFILL/W1C/W3/W2_H67)
  → DECISIONS D74–D89 → ACCOUNTING §2/§4

모집단 (Q1-안2 as-built)
------------------------
  기존 라이브러리 22씬 (train 19 + val 3 — `split_v2_full.json` 이 정본 분할)
    A  = 정본 재활용 `260819_main_on` + `260820_boost_{h,e,e2}_on` (낙차 18씬 · 816)
    B  = `260826_v3w1_lib_B2*` (T레버 12씬) + `260826_v3w1_lib_B*` (나머지 3씬) = 648
         · s03/s04/s10 은 레버 0 이라 **미렌더** (D74 ⑤ · 168컷 부재)
    C  = `260827_v3w1_lib_C*` (낙차 18씬 · 816) + 무낙차 4씬 on팔 재활용 (96) = 912
    D  = `260826_v3w1_lib_D*` (22씬 · 912) — **구off 재활용 아님**(D74 ①③ 신규 렌더)
  신규 훈련 씬 2 (val)
    sceneH6 · sceneH7 = `260824_v3w2_h67{base,h,h2}_{A,B,C,D}` = 480

GT 세대 — **하나만 쓴다**
-------------------------
  A : 교정 GT 정본 `dataset_manifest_v2corr.json` (z_off = 구off 계기)
  B : **A 트윈의 교정 GT를 상속**. 근거 = VG-01 (`polar_gt` 비트 동일 648/648 · 576/576).
      게이트 라벨(z_off = D팔)을 그대로 쓰면 코퍼스에 **두 세대의 GT**가 들어온다
      (실측 27프레임 상이) — W1C-1 이 라벨러 수리에서 막은 바로 그 위험이다.
  C·D : **사양 상수 전음성** (AC-INSTR-1 C3-2 · ACCOUNTING §4.10). 라벨러 출력 미채택.
  H6·H7 A/B : `w2_{band}_{ac,bd}_labels.json` (A/B `polar_gt`·tier 실측 동일)

CPU 전용. Isaac 미기동. git 명령 미사용. 정본 씬·라벨 파일 무수정.
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import math
import os
import sys

import numpy as np

REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"

# 0827 reorg: dataset/ is grouped (dataset/<group>/<round>) and a round is
# found by NAME, never by a flat path. See Docs/reorg_0827/S3_report.md.
sys.path.insert(0, REPO)                              # noqa: E402
from variation_kit import round_dir_or_flat   # noqa: E402
V3 = os.path.join(REPO, "experiments", "v3_0823")
ANN = os.path.join(V3, "annotations")
LOGS = os.path.join(V3, "logs")
CODE = os.path.join(V3, "code")
DATA = os.path.join(REPO, "dataset")
DAY = os.path.join(REPO, "experiments", "dayrun_0820")
LABDIR = os.path.join(REPO, "experiments", "mainrun_0819", "code", "labeling")
sys.path.insert(0, LABDIR)

FRAME_PX = 1920 * 1080

# --------------------------------------------------------------------------
# 등록부 — 선언적
# --------------------------------------------------------------------------
A_ROUNDS = {"base": "260819_main_on", "h": "260820_boost_h_on",
            "e": "260820_boost_e_on", "e2": "260820_boost_e2_on"}
B_ROUNDS = {"base": "260826_v3w1_lib_B", "h": "260826_v3w1_lib_B_h",
            "e": "260826_v3w1_lib_B_e", "e2": "260826_v3w1_lib_B_e2"}
B2_ROUNDS = {"base": "260826_v3w1_lib_B2", "h": "260826_v3w1_lib_B2_h",
             "e": "260826_v3w1_lib_B2_e", "e2": "260826_v3w1_lib_B2_e2"}
B3_ROUNDS = {"base": "260827_v3w1_lib_B3", "h": "260827_v3w1_lib_B3_h",
             "e": "260827_v3w1_lib_B3_e", "e2": "260827_v3w1_lib_B3_e2"}
C_ROUNDS = {"base": "260827_v3w1_lib_C", "h": "260827_v3w1_lib_C_h",
            "e": "260827_v3w1_lib_C_e", "e2": "260827_v3w1_lib_C_e2"}
D_ROUNDS = {"base": "260826_v3w1_lib_D", "h": "260826_v3w1_lib_D_h",
            "e": "260826_v3w1_lib_D_e", "e2": "260826_v3w1_lib_D_e2"}
W2_ROUNDS = {"w2base": "260824_v3w2_h67base", "w2h": "260824_v3w2_h67h",
             "w2h2": "260824_v3w2_h67h2"}
W2_SCENES = ("sceneH6", "sceneH7")
# W1B2 §7 — 이 12씬의 B팔 정본은 B2 트리
B2_SCENES = set("scene02 scene08 scene09 scene12 scene16 scene17 scene20 "
                "scene21 sceneC1 sceneC4 sceneD1 sceneD3".split())
# DECISIONS **D90 ①** — 세그 3차 판정(`w1d_seg3.json`)이 장식으로 해제한 레버를
# 더해 다시 찍은 5씬. 이 씬의 B팔 정본은 **B3 트리**이며 B2/B 트리를 대체한다
# (프레임 수·씬×밴드 분포는 동일 — 레시피만 상위집합이다).
B3_SCENES = set("scene01 scene09 scene21 sceneC1 sceneC4".split())


def b_tree_of(scene):
    """그 씬의 **B팔 정본 트리**. B3 > B2 > B (나중 웨이브가 이긴다)."""
    if scene in B3_SCENES:
        return "B3"
    return "B2" if scene in B2_SCENES else "B"


# 계획 §1.0 — v2 on팔이 그대로 C팔 (A팔이라는 말이 성립하지 않는다)
NODROP = ("sceneN1", "sceneN2", "sceneN4", "sceneN5")
# D74 ⑤ — 레버 0 이라 B ≡ A 바이트 동일 ⇒ 미렌더
B_SKIP = {"scene03": 72, "scene04": 72, "scene10": 24}
BAND_TOKEN = {"boost_h": "h", "boost_e": "e", "boost_e2": "e2"}
KEYS6 = ("R", "Ta", "N", "T", "Sg", "V")
CUE2KEY = {"cue_railing": "R", "cue_tactile": "Ta", "cue_nosing": "N",
           "cue_material_break": "T", "cue_sign": "Sg", "cue_scene_dressing": "V"}
KEY2CUE = {v: k for k, v in CUE2KEY.items()}


def log(*a):
    print(*a, flush=True)


def split_key(k):
    """`on/scene09/L0__…__0000.png::boost_e` → ('on','scene09','L0__…__0000','e')"""
    band = "base"
    if "::" in k:
        k, tok = k.split("::", 1)
        band = BAND_TOKEN.get(tok, tok)
    side, scene, fn = k.split("/", 2)
    return side, scene, os.path.splitext(fn)[0], band


# --------------------------------------------------------------------------
# 1. 격리 원장 — 웨이브 보고서의 **기계 산출**에서 읽는다 (손으로 옮기지 않는다)
# --------------------------------------------------------------------------
def load_quarantines(admit_seg3=False):
    """(scope, arm, scene, band, stem) → dict(reason, authority, ledger)"""
    Q = collections.defaultdict(list)          # (arm,scene,band,stem) → [entry]
    unit = []                                  # 단위(씬×밴드) 수준 기록

    def add(arm, scene, band, stem, scope, reason, authority, ledger):
        Q[(arm, scene, band, stem)].append(dict(
            scope=scope, reason=reason, authority=authority, ledger=ledger))

    # --- W1-D · VG-datum datum_fail 15컷 (D팔) ----------------------------
    wd = json.load(open(os.path.join(V3, "w1d_verify.json"), encoding="utf-8"))
    for row in wd["vg_datum"]["drift"]:
        if row.get("verdict") != "datum_fail":
            continue
        for fc in row.get("fail_cuts", []):
            add("D", row["scene"], row["band"], os.path.splitext(fc["file"])[0],
                "train_exclude",
                f"VG-datum datum_fail |Δground_z|={fc['d_ground_z']} m > 0.02 "
                f"(카메라 데이텀 스트립 프림 제거로 눈높이 붕괴 — 트윈 무효)",
                "W1D_REPORT §3 · §8 (사용 가능 컷 897/912)", "w1d_verify.json")
        unit.append(dict(arm="D", scene=row["scene"], band=row["band"],
                         scope="pair_quarantine", n_cuts=len(row.get("fail_cuts", [])),
                         reason="VG-datum 쌍 격리", authority="W1D_REPORT §3"))

    # --- W1-C · VG-datum (A,C) datum_fail (C팔) ---------------------------
    wc = json.load(open(os.path.join(V3, "w1c_datum.json"), encoding="utf-8"))
    for row in wc["rows"]:
        cam = row.get("camera") or {}
        if cam.get("verdict") != "datum_fail":
            continue
        for fc in cam.get("fail_cuts", []):
            add("C", row["scene"], row["band"], os.path.splitext(fc["file"])[0],
                "train_exclude",
                f"VG-datum (A,C) datum_fail |Δground_z|={fc['d_ground_z']} m > 0.02",
                "W1C_REPORT §8.2 (컷 생존 813/816)", "w1c_datum.json")
        unit.append(dict(arm="C", scene=row["scene"], band=row["band"],
                         scope="pair_quarantine", n_cuts=len(cam.get("fail_cuts", [])),
                         reason="VG-datum (A,C) 쌍 격리", authority="W1C_REPORT §8.2"))

    # --- W1-B / W1-B2 · VG-01 격리 (씬×밴드) ------------------------------
    #     프레임 층 `polar_gt` 는 비트 동일이므로 라벨 손실은 0. 그러나 W1B §9.0 이
    #     "격리 4 씬×밴드 = 96컷을 제외한 552컷이 무조건부"라 적었으므로 **기본은 제외**
    #     하고 P-19(W1B-2) 결재로 되살릴 수 있게 태그를 남긴다.
    for vf, tag in (("w1b_verify.json", "B"), ("w1b2_verify.json", "B2"),
                    ("w1b3_verify.json", "B3")):
        if not os.path.exists(os.path.join(V3, vf)):
            continue
        d = json.load(open(os.path.join(V3, vf), encoding="utf-8"))
        qkey = ("quarantine_if_seg3_admitted"
                if (admit_seg3 and "quarantine_if_seg3_admitted" in d["vg_01"])
                else "quarantine")
        for q in d["vg_01"].get(qkey, []):
            sc, bd = (q["scene"], q["band"]) if isinstance(q, dict) else q.split("/")
            if b_tree_of(sc) != tag:
                continue
            unit.append(dict(arm="B", scene=sc, band=bd, scope="train_exclude_unit",
                             reason="VG-01 씬층 격리 (융합 계기 시점 의존 / 원인 키 미규명)",
                             authority=f"{vf} vg_01.{qkey} · W1B §9.0 · P-19",
                             revivable="P-19 (W1B-2) 결재 시 복원 — `polar_gt` 는 비트 동일"))
    # --- VG-08 포즈 간 충돌 (세그만 격리) ----------------------------------
    for vf, tag in (("w1b_verify.json", "B"), ("w1b2_verify.json", "B2"),
                    ("w1b3_verify.json", "B3")):
        if not os.path.exists(os.path.join(V3, vf)):
            continue
        d = json.load(open(os.path.join(V3, vf), encoding="utf-8"))
        for f in d["vg_08"].get("failures", []):
            if b_tree_of(f["scene"]) != tag:
                continue
            unit.append(dict(arm="B", scene=f["scene"], band=f["band"],
                             scope="seg_exclude_unit",
                             n_collisions=f.get("n_pose_collisions"),
                             reason="VG-08 포즈 간 마스크 충돌(결정론적 stale) — "
                                    "세그 기반 채널만 무효, 라벨·기하는 정상",
                             authority="W1B_REPORT §5.2 · W1B2 §1.5",
                             ledger=vf))
    return Q, unit


def collide_stems(round_dir, scene):
    """한 유닛 안에서 **다른 포즈가 같은 마스크 바이트**를 쓰는 컷을 집어낸다."""
    import hashlib
    vf = os.path.join(round_dir, "*", scene, "variation.json")
    hits = glob.glob(vf)
    if not hits:
        return set()
    sdir = os.path.dirname(hits[0])
    var = json.load(open(hits[0], encoding="utf-8"))
    cuts = var["cuts"]
    cuts = list(cuts.values()) if isinstance(cuts, dict) else cuts
    by_hash = collections.defaultdict(list)
    for c in cuts:
        stem = os.path.splitext(c["file"])[0]
        p = os.path.join(sdir, stem + ".idseg.npz")
        if not os.path.isfile(p):
            continue
        h = hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]
        cam = c["cam"]
        pose = tuple(round(float(cam.get(k) or 0.0), 4)
                     for k in ("d", "h_rel", "yaw", "pitch", "roll", "hfov"))
        by_hash[h].append((stem, pose))
    bad = set()
    for h, items in by_hash.items():
        if len({p for _, p in items}) > 1:      # 다른 포즈가 같은 마스크
            bad.update(s for s, _ in items)
    return bad


# --------------------------------------------------------------------------
# 2. GT 원천
# --------------------------------------------------------------------------
def load_gt():
    man = json.load(open(os.path.join(V3, "dataset_manifest_v2corr.json"),
                         encoding="utf-8"))
    A = {}
    for f in man["frames"]:
        if f.get("toggle_state") != "on":
            continue
        _s, scene, stem, band = split_key(f["frame_id"])
        A[(scene, band, stem)] = f
    labs = {}
    for fn in ("w1b_A.json", "w1b_B.json", "w1b2_A.json", "w1b2_B.json",
               "w1b3_A.json", "w1b3_B.json"):
        pth = os.path.join(ANN, fn)
        labs[fn] = (json.load(open(pth, encoding="utf-8"))["frames"]
                    if os.path.exists(pth) else {})
    w2 = {}
    for band, tag in (("w2base", "base"), ("w2h", "h"), ("w2h2", "h2")):
        for pair in ("ac", "bd"):
            p = os.path.join(ANN, f"w2_{tag}_{pair}_labels.json")
            if os.path.exists(p):
                w2[(band, pair)] = json.load(open(p, encoding="utf-8"))["frames"]
    return A, labs, w2, man["meta"]


# --------------------------------------------------------------------------
# 3. gt_void — **칸별** void (RT-A LAB-19 · 계획 §6.4)
# --------------------------------------------------------------------------
def build_void_index(units, grid):
    """(round, scene) 마다 높이맵을 한 번 읽어 컷별 칸-void 벡터를 만든다."""
    import labeler as LB
    ncell = LB.n_cells(grid)
    out = {}
    for rnd, scene in sorted(units):
        hits = glob.glob(os.path.join(round_dir_or_flat(rnd), "*", scene, "variation.json"))
        if not hits:
            continue
        sdir = os.path.dirname(hits[0])
        try:
            hm, geo, src = LB.load_heightmap(sdir)
        except Exception as e:                     # 높이맵 부재 = 기록만
            out[(rnd, scene)] = ("no_heightmap", str(e))
            continue
        x0, y0, st = geo
        ny, nx = hm.shape
        XX, YY = np.meshgrid(x0 + np.arange(nx) * st, y0 + np.arange(ny) * st)
        void = ~np.isfinite(hm)
        var = json.load(open(hits[0], encoding="utf-8"))
        cuts = var["cuts"]
        cuts = list(cuts.values()) if isinstance(cuts, dict) else cuts
        per = {}
        for c in cuts:
            cam = c["cam"]
            eye = np.asarray(cam["eye"], dtype=np.float64)
            cell, _ = LB.polar_cells(XX, YY, eye, cam["yaw"], grid)
            ing = cell >= 0
            vc = np.bincount(cell[void & ing], minlength=ncell)[:ncell]
            per[os.path.splitext(c["file"])[0]] = dict(
                gt_void=[int(v > 0) for v in vc],
                void_cells_px=[int(v) for v in vc],
                void_in_grid=int((void & ing).sum()),
                grid_cells=int(ing.sum()), hm_source=src)
        out[(rnd, scene)] = per
    return out


# --------------------------------------------------------------------------
# 4. 단서 채널 — strict 세그의 **원시 픽셀 수** (k 는 PREREG 미결이므로 봉인 안 함)
# --------------------------------------------------------------------------
def load_cue_index():
    p = os.path.join(LOGS, "cue_extent_frames.json")
    d = json.load(open(p, encoding="utf-8"))
    idx = {}
    for r in d["corpus"]:
        idx[(r["arm"], r["scene"], r["band"], r["stem"])] = r
    return idx, d["accounting"]


def onwired_registry():
    """수리된 hazgate(`--mode full`)의 ON·배선 키 — PREREG §4.4 |r| 규약 4."""
    hz = json.load(open(os.path.join(CODE, "hazgate_full.json"), encoding="utf-8"))
    out = {}
    for k, v in hz.items():
        scene = os.path.basename(k).split("::")[-1].split("_")[0]
        d = v.get("defaults") or {}
        cue = v.get("cue") or {}
        out[scene] = {CUE2KEY[c] for c in CUE2KEY
                      if d.get(c) is True and cue.get(c) is not None}
    return out


def built_levers():
    """실제로 찍은 B/B2/B3 설정 파일에서 **꺼진 키**를 읽는다 (최종 사실)."""
    out = {}
    for p in sorted(glob.glob(os.path.join(V3, "render_configs_v3", "*_B*.json"))):
        base = os.path.basename(p)[:-5]
        scene, _, tag = base.rpartition("_")
        if tag not in ("B", "B2", "B3"):
            continue
        if b_tree_of(scene) != tag:
            continue
        cfg = json.load(open(p, encoding="utf-8"))
        out[scene] = {CUE2KEY[c] for c, v in cfg.items()
                      if c in CUE2KEY and v is False}
    return out


# --------------------------------------------------------------------------
# 4b. (A,C) 광학차 — **등록된 술어** frac(|ΔI| > 8) < 0.001 (PREREG §2.1 층화 2)
#     W1C 의 unit 요약은 `mean|ΔI| < 0.5` 라는 **다른 술어**를 썼다. 층화 규약은
#     사전 등록된 쪽이므로 여기서 컷 단위로 다시 잰다(캐시).
# --------------------------------------------------------------------------
def _optical_one(job):
    from PIL import Image
    a_path, c_path = job
    try:
        A = np.asarray(Image.open(a_path).convert("L"), dtype=np.int16)[::2, ::2]
        C = np.asarray(Image.open(c_path).convert("L"), dtype=np.int16)[::2, ::2]
    except Exception as e:
        return None, str(e)
    d = np.abs(A - C)
    return dict(mean_abs=round(float(d.mean()), 4),
                frac_gt8=round(float((d > 8).mean()), 6),
                frac_gt32=round(float((d > 32).mean()), 6)), None


def optical_ac_index(pairs, workers=12):
    """pairs: {(scene,band,stem): (a_png, c_png)} → 같은 키의 광학차."""
    cache_p = os.path.join(LOGS, "corpus_v3_optical_ac.json")
    cache = {}
    if os.path.exists(cache_p):
        cache = json.load(open(cache_p, encoding="utf-8")).get("pairs", {})
    todo = {k: v for k, v in pairs.items() if "|".join(k) not in cache}
    if todo:
        from concurrent.futures import ProcessPoolExecutor
        keys = list(todo)
        log(f"[optical] (A,C) {len(keys)}쌍 측정 …")
        with ProcessPoolExecutor(max_workers=workers) as ex:
            for k, (r, err) in zip(keys, ex.map(_optical_one,
                                                [todo[k] for k in keys],
                                                chunksize=8)):
                if r:
                    cache["|".join(k)] = r
        json.dump(dict(doc="corpus_v3_optical_ac",
                       predicate="frac(|dI|>8) < 0.001 → zero_info (PREREG §2.1)",
                       subsample="2x2 stride, grayscale", pairs=cache),
                  open(cache_p, "w", encoding="utf-8"), ensure_ascii=False)
    return {tuple(k.split("|")): v for k, v in cache.items()}


# --------------------------------------------------------------------------
# 5. 조립
# --------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(V3, "dataset_manifest_v3.json"))
    ap.add_argument("--split-out", default=os.path.join(V3, "split_v3.json"))
    ap.add_argument("--revive-vg01", action="store_true",
                    help="P-19 결재 시 — VG-01 격리 96컷을 훈련에 되살린다")
    ap.add_argument("--admit-seg3", action="store_true",
                    help="D90 ① 결재 시 — VG-01 `T2-seg` 자격 유닛(polar_gt 비트 동일 · "
                         "cells_raw 갈림 · 순증 · 추가 레버 전부 세그 3차 해제)을 "
                         "격리에서 뺀다. 기본은 **비발동(보수적 격리)**.")
    args = ap.parse_args(argv)

    import labeler as LB
    grid = json.load(open(os.path.join(LABDIR, "gridspec_v1.json"), encoding="utf-8"))
    ncell = LB.n_cells(grid)

    split2 = json.load(open(os.path.join(DAY, "split_v2_full.json"), encoding="utf-8"))
    LIB_TRAIN = list(split2["train"])
    LIB_VAL = list(split2["val"])
    LIB = LIB_TRAIN + LIB_VAL
    assert len(LIB) == 22, LIB
    split_of = {s: "train" for s in LIB_TRAIN}
    split_of.update({s: "val" for s in LIB_VAL})
    split_of.update({s: "val" for s in W2_SCENES})

    A_GT, LABS, W2L, v2meta = load_gt()
    Q, QUNIT = load_quarantines(args.admit_seg3)
    CUE, cue_acct = load_cue_index()
    ONW = onwired_registry()
    BUILT = built_levers()

    # ---- VG-08 충돌 컷 실측 (유닛 원장은 씬×밴드까지만 있다) ---------------
    seg_bad = set()
    for u in QUNIT:
        if u["scope"] != "seg_exclude_unit":
            continue
        rounds = {"B3": B3_ROUNDS, "B2": B2_ROUNDS,
                  "B": B_ROUNDS}[b_tree_of(u["scene"])]
        rd = rounds.get(u["band"])
        if not rd:
            continue
        for stem in collide_stems(round_dir_or_flat(rd), u["scene"]):
            seg_bad.add(("B", u["scene"], u["band"], stem))
    vg01_units = {(u["scene"], u["band"]) for u in QUNIT
                  if u["scope"] == "train_exclude_unit"}
    # D팔 stale 152컷 (idseg_fetch == "t0" · W1D §2.2) — 세그만 격리
    n_dstale = 0
    for band, rnd in D_ROUNDS.items():
        for vf in glob.glob(os.path.join(round_dir_or_flat(rnd), "*", "*", "variation.json")):
            var = json.load(open(vf, encoding="utf-8"))
            sc = var.get("scene")
            cuts = var["cuts"]
            cuts = list(cuts.values()) if isinstance(cuts, dict) else cuts
            for c in cuts:
                if c.get("idseg_fetch") == "t0":
                    seg_bad.add(("D", sc, band, os.path.splitext(c["file"])[0]))
                    n_dstale += 1
    QUNIT.append(dict(arm="D", scope="seg_exclude_cuts", n_cuts=n_dstale,
                      reason="idseg_fetch == 't0' (첫 컷 마스크 복제 = stale). "
                             "D팔은 단서·위험 무라 세그 비하중이었으나 코퍼스에서는 "
                             "단서 채널이 기하 fallback 으로 내려간다",
                      authority="W1D_REPORT §2.2 · D73 ①", ledger="variation.json"))
    # A팔 백필 미설치 유닛 (W1B2 §2.4 · 5유닛 120컷)
    bf_units = set()
    for band, rnd in A_ROUNDS.items():
        for lf in glob.glob(os.path.join(round_dir_or_flat(rnd), "*", "*", "idseg_backfill.json")):
            d = json.load(open(lf, encoding="utf-8"))
            bf_units.add((d.get("scene"), band))

    # ---- 프레임 목록 (팔별) -----------------------------------------------
    rows = []          # 편입분
    quar = []          # 제외분 (전수 · 사유)

    def scene_of(p):
        return os.path.basename(os.path.dirname(p))

    def pngs(round_dir, scene=None):
        pat = os.path.join(round_dir_or_flat(round_dir), "*", scene or "*", "*.png")
        return sorted(p for p in glob.glob(pat) if not p.endswith(".depth.png"))

    # variation.json 캐시 (cam·cond)
    varcache = {}

    def cutinfo(round_dir, scene, stem):
        key = (round_dir, scene)
        if key not in varcache:
            hits = glob.glob(os.path.join(round_dir_or_flat(round_dir), "*", scene, "variation.json"))
            m = {}
            if hits:
                var = json.load(open(hits[0], encoding="utf-8"))
                cuts = var["cuts"]
                cuts = list(cuts.values()) if isinstance(cuts, dict) else cuts
                for c in cuts:
                    m[os.path.splitext(c["file"])[0]] = c
            varcache[key] = m
        return varcache[key].get(stem)

    CAM_KEYS = ("d", "h_rel", "yaw", "pitch", "roll", "hfov", "ground_z")

    def emit(arm, scene, band, stem, rnd, rgb, gt, tier, extra):
        """편입 후보 1건 — 격리 판정은 여기서 한다."""
        qs = list(Q.get((arm, scene, band, stem), []))
        if arm == "B" and (scene, band) in vg01_units and not args.revive_vg01:
            qs.append(dict(scope="train_exclude",
                           reason="VG-01 씬층 격리 (씬×밴드 단위)",
                           authority="W1B §9.0 · P-19", ledger="w1b*_verify.json"))
        seg_q = (arm, scene, band, stem) in seg_bad
        fid = f"{arm}/{scene}/{stem}.png" + ("" if band == "base" else f"::{band}")
        rec = dict(frame_id=fid, scene_id=scene, arm=arm, band=band, round=rnd,
                   toggle_state=arm, split=split_of[scene], rgb=rgb, gt=gt,
                   tier=tier, seg_quarantined=seg_q, extra=extra, stem=stem)
        hard = [q for q in qs if q["scope"] == "train_exclude"]
        if hard:
            quar.append(dict(frame_id=fid, scene_id=scene, arm=arm, band=band,
                             round=rnd, split=split_of[scene], reasons=qs))
            return None
        rec["flags"] = [q for q in qs if q["scope"] != "train_exclude"]
        rows.append(rec)
        return rec

    # ---------- A팔 ----------
    for band, rnd in A_ROUNDS.items():
        for p in pngs(rnd):
            sc = scene_of(p)
            if sc not in LIB or sc in NODROP:
                continue
            stem = os.path.basename(p)[:-4]
            g = A_GT.get((sc, band, stem))
            if g is None:
                continue
            emit("A", sc, band, stem, rnd, p, g["polar_gt"], g["tier"],
                 dict(src="dataset_manifest_v2corr.json", rec=g))
    # ---------- B팔 ----------
    for rounds, tag in ((B3_ROUNDS, "B3"), (B2_ROUNDS, "B2"), (B_ROUNDS, "B")):
        for band, rnd in rounds.items():
            for p in pngs(rnd):
                sc = scene_of(p)
                if sc not in LIB:
                    continue
                if b_tree_of(sc) != tag:
                    continue
                stem = os.path.basename(p)[:-4]
                g = A_GT.get((sc, band, stem))
                if g is None:
                    continue
                lab = LABS[{"B3": "w1b3_B.json", "B2": "w1b2_B.json",
                            "B": "w1b_B.json"}[tag]]
                lk = f"on/{sc}/{stem}.png" + ("" if band == "base"
                                              else f"::boost_{band}")
                lv = lab.get(lk) or {}
                emit("B", sc, band, stem, rnd, p, g["polar_gt"], g["tier"],
                     dict(src=f"A-twin v2corr (VG-01 polar_gt 동일) · lever={tag}",
                          rec=g, arm_local=lv))
    # ---------- C팔 ----------
    for band, rnd in C_ROUNDS.items():
        for p in pngs(rnd):
            sc = scene_of(p)
            if sc not in LIB:
                continue
            stem = os.path.basename(p)[:-4]
            emit("C", sc, band, stem, rnd, p, [0] * ncell, "off",
                 dict(src="spec_constant_all_negative (AC-INSTR-1 C3-2)"))
    #        무낙차 4씬 — v2 on팔 재활용
    for sc in NODROP:
        for band, rnd in A_ROUNDS.items():
            for p in pngs(rnd, sc):
                stem = os.path.basename(p)[:-4]
                g = A_GT.get((sc, band, stem))
                if g is None:
                    continue
                assert not any(g["polar_gt"]), (sc, stem)
                emit("C", sc, band, stem, rnd, p, [0] * ncell, g["tier"],
                     dict(src="v2corr on팔 재활용 (무낙차 = C팔, 계획 §1.0) · "
                              "GT 는 실측 전음성 = 사양 상수와 일치", rec=g))
    # ---------- D팔 ----------
    for band, rnd in D_ROUNDS.items():
        for p in pngs(rnd):
            sc = scene_of(p)
            if sc not in LIB:
                continue
            stem = os.path.basename(p)[:-4]
            emit("D", sc, band, stem, rnd, p, [0] * ncell, "off",
                 dict(src="spec_constant_all_negative (VG-02 all-negative 38/38)"))
    # ---------- W2 (sceneH6 · H7) ----------
    for band, stamp in W2_ROUNDS.items():
        for arm in "ABCD":
            rnd = f"{stamp}_{arm}"
            for p in pngs(rnd):
                sc = scene_of(p)
                if sc not in W2_SCENES:
                    continue
                stem = os.path.basename(p)[:-4]
                pair = "ac" if arm in ("A", "C") else "bd"
                side = "on" if arm in ("A", "B") else "off"
                lv = (W2L.get((band, pair)) or {}).get(f"{side}/{sc}/{stem}.png")
                if arm in ("A", "B"):
                    if lv is None:
                        continue
                    src = f"w2_{ {'w2base':'base','w2h':'h','w2h2':'h2'}[band] }_{pair}_labels.json"
                    if arm == "B":
                        av = (W2L.get((band, "ac")) or {}).get(f"on/{sc}/{stem}.png")
                        gt = (av or lv)["polar_gt"]
                        tier = (av or lv)["tier_strict"]
                        src += " (A트윈 상속 · VG-01 24/24×5)"
                    else:
                        gt, tier = lv["polar_gt"], lv["tier_strict"]
                    emit(arm, sc, band, stem, rnd, p, gt, tier,
                         dict(src=src, rec=lv))
                else:
                    emit(arm, sc, band, stem, rnd, p, [0] * ncell, "off",
                         dict(src="spec_constant_all_negative (W2 §3.5 10/10 전음성)",
                              rec=lv))

    log(f"[corpus] 편입 후보 {len(rows)} · 격리 {len(quar)}")

    # ---- (A,C) 광학차 — 등록 술어로 컷 단위 측정 ---------------------------
    a_by = {}
    for r in rows:
        if r["arm"] == "A":
            a_by[(r["scene_id"], r["band"], r["stem"])] = r["rgb"]
    pairs = {}
    for r in rows:
        if r["arm"] != "C":
            continue
        k = (r["scene_id"], r["band"], r["stem"])
        if k in a_by:
            pairs[k] = (a_by[k], r["rgb"])
    OPT = optical_ac_index(pairs)
    zero_info = {k for k, v in OPT.items() if v["frac_gt8"] < 0.001}
    log(f"[optical] 쌍 {len(OPT)} · 영정보 {len(zero_info)} "
        f"(술어 frac(|ΔI|>8) < 0.001)")

    # ---- gt_void (칸별) ----------------------------------------------------
    units = {(r["round"], r["scene_id"]) for r in rows}
    log(f"[void] {len(units)} 유닛 스캔 …")
    VOID = build_void_index(units, grid)

    # ---- 프레임 레코드 확정 ------------------------------------------------
    frames = []
    n_seg = n_fb = 0
    for r in rows:
        sc, band, stem, arm = r["scene_id"], r["band"], r["stem"], r["arm"]
        ex = r["extra"]
        base = ex.get("rec") or {}
        c = cutinfo(r["round"], sc, stem)
        cam = {k: (c["cam"].get(k) if c else base.get("cam", {}).get(k))
               for k in CAM_KEYS}
        dep = os.path.splitext(r["rgb"])[0] + ".depth.npy"
        seg = os.path.splitext(r["rgb"])[0] + ".idseg.npz"
        # 단서 채널
        ci = CUE.get((arm, sc, band, stem))
        seg_ok = (ci is not None) and os.path.isfile(seg) and not r["seg_quarantined"]
        if seg_ok:
            n_seg += 1
            byk = {k: int(v) for k, v in ci["area"].items()}
            # **정본 6키만**이 §12-5 의 "단서"다. `Gk`(지면 표면처리 미분해)·
            # `Mh/Dr/Jt`(신설 키)·`Ux` 는 토글 가능 6키가 아니므로 분리해 인쇄한다.
            # T(material_break)는 재질 재바인딩이라 ID 마스크가 원리적으로 못 본다
            # ⇒ 면적 기여 0 (CUE_EXTENT_AUDIT §0.3).
            cue = dict(source="idseg_strict", measured=True,
                       px_total=int(ci["area_total"]),
                       px_canonical6=int(sum(byk.get(k, 0) for k in KEYS6)),
                       px_by_key=byk,
                       frac_total=round(ci["area_total"] / FRAME_PX, 8),
                       n_obj=int(ci["n_obj"]), n_grp=int(ci["n_grp"]))
        else:
            n_fb += 1
            onw = ONW.get(sc, set())
            rm = BUILT.get(sc, set())
            if arm in ("A", "C"):
                geom = 1 if onw else 0
            elif arm == "D":
                geom = 0
            else:                                   # B — 잔존 상수 단서가 있다
                geom = 1 if (onw - rm) else 0
            cue = dict(source="geometric_fallback", measured=False,
                       px_total=None, px_canonical6=None, px_by_key=None,
                       frac_total=None,
                       fallback_present=geom,
                       fallback_basis="ON·배선 cue 키(수리된 hazgate) ∧ 그 팔의 "
                                      "레시피가 그 키를 끄지 않았다",
                       fallback_reason=("seg_quarantined" if r["seg_quarantined"]
                                        else "no_strict_idseg"))
        # void
        vv = VOID.get((r["round"], sc))
        if isinstance(vv, dict) and stem in vv:
            v = vv[stem]
        else:
            v = dict(gt_void=[0] * ncell, void_cells_px=[0] * ncell,
                     void_in_grid=0, grid_cells=None, hm_source=None)
        rec = dict(
            frame_id=r["frame_id"], scene_id=sc, round=r["round"],
            toggle_state=arm, arm=arm, band=band, split=r["split"],
            rgb=os.path.abspath(r["rgb"]),
            depth=os.path.abspath(dep) if os.path.isfile(dep) else None,
            idseg=os.path.abspath(seg) if os.path.isfile(seg) else None,
            idseg_trusted=bool(seg_ok),
            polar_gt=list(r["gt"]),
            polar_gt_pregate=(list(r["gt"]) if arm in ("C", "D")
                              else list(base.get("polar_gt_pregate") or r["gt"])),
            gate_excluded=base.get("gate_excluded", dict(cells=[], n=0)),
            raw_vis=base.get("raw_vis"),
            tier=r["tier"], tier_arm_local=(ex.get("arm_local") or {}).get("tier_strict")
            or (ex.get("rec") or {}).get("tier_strict"),
            tier_source=v2meta.get("tier_source"), gt_source=ex["src"],
            hazard_arm=(arm in ("A", "B")),
            cam=cam, cond=(c or {}).get("cond") or base.get("cond"),
            gt_void=v["gt_void"], void_cells_px=v["void_cells_px"],
            void_in_grid=v["void_in_grid"], hm_source=v["hm_source"],
            cue=cue, flags=r["flags"], notes="")
        ok = (sc, band, stem)
        if arm in ("A", "C") and ok in OPT:
            rec["optical_ac"] = dict(OPT[ok], zero_info=bool(ok in zero_info),
                                     predicate="frac(|dI|>8) < 0.001 (PREREG §2.1)")
        frames.append(rec)

    # ---- 무시 마스크 채널 --------------------------------------------------
    #  ① bare-H (DZ §5.1 · PREREG §5.3) — 단서 0 인 strict-H. k 미결이므로
    #     **후보 k 격자별로** 판정해 둔다(적용은 훈련 시점, k 봉인 후).
    #  ② B팔 H (PREREG §5.3 "B팔의 H 칸은 무시 마스크")
    #  ③ 레버 ㄴ (D89 ⑤a) — 영정보 (A,C) 쌍의 C팔. **예비채택·결재중**.
    K_GRID = [1, 100, 1000, 5000, 20000, 60000]
    # A팔 트윈이 GT 양성인 영정보 쌍만이 D89 ⑤a 가 말한 "같은 그림에 반대 라벨"이다.
    a_pos = {(f["scene_id"], f["band"], os.path.splitext(
        f["frame_id"].split("/", 2)[2].split("::")[0])[0])
        for f in frames if f["arm"] == "A" and any(f["polar_gt"])}
    for f in frames:
        stem = os.path.splitext(f["frame_id"].split("/", 2)[2].split("::")[0])[0]
        key = (f["scene_id"], f["band"], stem)
        ig = {}
        px = (f["cue"] or {}).get("px_canonical6")
        ig["b_arm_h"] = bool(f["arm"] == "B" and f["tier"] == "H")
        ig["bare_h_by_k"] = ({str(k): bool(f["tier"] == "H" and px < k)
                              for k in K_GRID} if px is not None else None)
        ig["bare_h_measurable"] = px is not None
        ig["lever_n_zero_info_c"] = bool(f["arm"] == "C" and key in zero_info)
        ig["lever_n_contradiction"] = bool(f["arm"] == "C" and key in zero_info
                                           and key in a_pos)
        ig["gt_void_cells"] = int(sum(f["gt_void"]))
        f["ignore"] = ig

    meta = dict(
        doc="dataset_manifest_v3", version="1.1",
        version_note="1.1 = v3 코퍼스 + W1-B3 레버 추가분(D90 ①). 1.0 대비 프레임 수·분할·GT 세대는 불변이고 5씬의 B팔 라운드만 B3 트리로 바뀐다.",
        created=__import__("datetime").datetime.now().isoformat(timespec="seconds"),
        authority="RENDER_PLAN_V3.md → 웨이브 보고서 → DECISIONS D74–D89 → ACCOUNTING §2/§4",
        grid_version=grid["version"], n_cells=ncell,
        gt_source="A: 교정 GT 정본(v2corr) · B: A트윈 상속(VG-01) · "
                  "C/D: 사양 상수 전음성(AC-INSTR-1 C3-2)",
        tier_source=v2meta.get("tier_source"),
        footprint=v2meta.get("footprint"), gate_policy=v2meta.get("gate_policy"),
        split_source="experiments/dayrun_0820/split_v2_full.json (+ sceneH6·H7 = val)",
        rounds=dict(A=A_ROUNDS, B=B_ROUNDS, B2=B2_ROUNDS, B3=B3_ROUNDS,
                    C=C_ROUNDS, D=D_ROUNDS, W2=W2_ROUNDS),
        b2_scenes=sorted(B2_SCENES), b3_scenes=sorted(B3_SCENES),
        admit_seg3=bool(args.admit_seg3), revive_vg01=bool(args.revive_vg01),
        b_tree_rule="B3 > B2 > B — 나중 웨이브가 그 씬의 B팔 정본이다. "
                    "B3 = DECISIONS D90 ① 레버 추가 재렌더(세그 3차 "
                    "`w1d_seg3.json` 해제분 · 씬×밴드 분포 불변).",
        nodrop_c_reuse=list(NODROP),
        b_skip_d74=B_SKIP,
        n_frames=len(frames), n_quarantined=len(quar),
        cue_channel="원시 cue 픽셀 수만 저장 — **k 는 PREREG 미결**이므로 "
                    "cue_present 이진값을 매니페스트가 정하지 않는다 (ACCOUNTING §2-5).",
        ignore_channels=dict(
            b_arm_h="PREREG §5.3 — B팔의 H 칸은 무시 마스크",
            bare_h_by_k="DZ §5.1 맨-가림 H. k 후보 격자 " + str(K_GRID),
            lever_n_zero_info_c="D89 ⑤a 레버 ㄴ — **예비채택·결재중**, 적용은 승인 후",
            gt_void_cells="RT-A LAB-19 — void 칸은 음성이 아니다"),
        scope="훈련·검증 전용. test-core 7씬과 test-ext(W3)는 이 파일에 없다.",
        test_core="experiments/dayrun_0820/split_v2_full.json::test (평가 전용 · 교정 GT)",
        test_ext="experiments/v3_0823/dataset_manifest_v3_textext.json (W3 · 중복 생성 금지)",
        cue_scan_accounting=cue_acct)

    json.dump(dict(meta=meta, frames=frames), open(args.out, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    log(f"[corpus] → {args.out}  ({len(frames)} 프레임)")

    sp = dict(train=sorted(LIB_TRAIN), val=sorted(LIB_VAL + list(W2_SCENES)),
              test=sorted(split2["test"]), hold=sorted(split2["hold"]))
    json.dump(sp, open(args.split_out, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    log(f"[corpus] → {args.split_out}")

    qout = dict(doc="corpus_v3_quarantine", version="1.1",
                created=meta["created"],
                rule="격리는 벌점이 아니며 **인쇄 누락만이 위반**이다 (AC-INSTR-1 C3-7).",
                n_frames_excluded=len(quar),
                by_scope=dict(collections.Counter(
                    q["reasons"][0]["scope"] for q in quar)),
                by_arm=dict(collections.Counter(q["arm"] for q in quar)),
                unit_ledger=QUNIT, frames=quar,
                seg_collision_cuts=sorted(f"{a}/{s}/{b}/{t}"
                                          for a, s, b, t in seg_bad),
                absent_not_quarantined=dict(
                    b_arm_skip=B_SKIP,
                    reason="D74 ⑤ — 레버 0 이라 B ≡ A 바이트 동일. 중복 프레임은 "
                           "학습 이중 가중이므로 **찍지 않았다**. 격리가 아니라 부재."))
    qp = os.path.join(V3, "corpus_v3_quarantine.json")
    json.dump(qout, open(qp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    log(f"[corpus] → {qp}  (격리 {len(quar)}프레임)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
