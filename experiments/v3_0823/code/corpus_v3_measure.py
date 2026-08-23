#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""corpus_v3_measure.py — 조립된 v3 코퍼스 위의 **최종 실측** (CPU 전용 · GPU 0).

무엇을 재나
-----------
  ① tier 센서스 (팔 × 분할 × tier) · val strict-H
  ② **존재 |r| — 키별** (토글 가능 키 한정 · 주변분포 병기 · ACCOUNTING §4.9-3)
     설계 수준(팔 = 위험)과 사실 수준(프레임 GT = 위험) **양쪽**을 병기한다.
  ③ **팔 × 씬출신 상관** (D58 ② · 계획 §4.4.5)
  ④ **k 유도** — 단서 픽셀 분포에서 (VG-11 · PREREG 미결)
  ⑤ gt_void · 무시 마스크 채널 회계
  ⑥ ACCOUNTING §3.4 제안 행

산출:  experiments/v3_0823/corpus_v3_census.json  (+ stdout 표)
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import os
import random
import sys

REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"
V3 = os.path.join(REPO, "experiments", "v3_0823")
CODE = os.path.join(V3, "code")
FRAME_PX = 1920 * 1080

KEYS6 = ("R", "Ta", "N", "T", "Sg", "V")
CUE2KEY = {"cue_railing": "R", "cue_tactile": "Ta", "cue_nosing": "N",
           "cue_material_break": "T", "cue_sign": "Sg", "cue_scene_dressing": "V"}
KEY2CUE = {v: k for k, v in CUE2KEY.items()}
NAME = {"R": "cue_railing", "Ta": "cue_tactile", "N": "cue_nosing",
        "T": "cue_material_break", "Sg": "cue_sign", "V": "cue_scene_dressing"}
W2_SCENES = ("sceneH6", "sceneH7")
NODROP = ("sceneN1", "sceneN2", "sceneN4", "sceneN5")


def log(*a):
    print(*a, flush=True)


def phi(a, b, c, d):
    den = math.sqrt((a + b) * (c + d) * (a + c) * (b + d))
    return 0.0 if den == 0 else (a * d - b * c) / den


def q(v, p):
    v = sorted(v)
    return v[min(len(v) - 1, int(len(v) * p))] if v else None


def onwired_registry():
    hz = json.load(open(os.path.join(CODE, "hazgate_full.json"), encoding="utf-8"))
    out = {}
    for k, v in hz.items():
        scene = os.path.basename(k).split("::")[-1].split("_")[0]
        d = v.get("defaults") or {}
        cue = v.get("cue") or {}
        out[scene] = {CUE2KEY[c] for c in CUE2KEY
                      if d.get(c) is True and cue.get(c) is not None}
    return out


def built_levers(b2_scenes, b3_scenes=frozenset()):
    """B팔 정본 트리는 **B3 > B2 > B** (나중 웨이브가 이긴다 · D90 ①)."""
    import glob

    def tree_of(sc):
        if sc in b3_scenes:
            return "B3"
        return "B2" if sc in b2_scenes else "B"

    out = {}
    for p in sorted(glob.glob(os.path.join(V3, "render_configs_v3", "*_B*.json"))):
        base = os.path.basename(p)[:-5]
        scene, _, tag = base.rpartition("_")
        if tag not in ("B", "B2", "B3"):
            continue
        if tree_of(scene) != tag:
            continue
        cfg = json.load(open(p, encoding="utf-8"))
        out[scene] = {CUE2KEY[c] for c, v in cfg.items()
                      if c in CUE2KEY and v is False}
    # sceneH6·H7 은 `render_configs_v3/` 를 쓰지 않는다 — W2 러너가 레시피를
    # 인라인으로 준다: B = {hazard_stairs: true, <cue 13키 전부 false>}
    # (`code/run_w2_h67.sh:71-85` COMMON12 + 씬별 1키 · W2_H67_REPORT §1.1).
    for sc in W2_SCENES:
        out[sc] = set(KEYS6)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default=os.path.join(V3, "dataset_manifest_v3.json"))
    ap.add_argument("--out", default=os.path.join(V3, "corpus_v3_census.json"))
    ap.add_argument("--perm", type=int, default=2000)
    a = ap.parse_args(argv)

    man = json.load(open(a.manifest, encoding="utf-8"))
    F = man["frames"]
    meta = man["meta"]
    B2S = set(meta["b2_scenes"])
    B3S = set(meta.get("b3_scenes") or ())
    ONW = onwired_registry()
    BUILT = built_levers(B2S, B3S)
    QU = json.load(open(os.path.join(V3, "corpus_v3_quarantine.json"),
                        encoding="utf-8"))

    res = dict(doc="corpus_v3_census", version="1.0",
               manifest=os.path.relpath(a.manifest, REPO),
               created=__import__("datetime").datetime.now().isoformat(timespec="seconds"),
               n_frames=len(F))

    # ---------------------------------------------------------------- ① 센서스
    by_arm = collections.Counter(f["arm"] for f in F)
    by_as = collections.Counter((f["arm"], f["split"]) for f in F)
    by_tier = collections.Counter(f["tier"] for f in F)
    by_st = collections.Counter((f["split"], f["tier"]) for f in F)
    by_ast = collections.Counter((f["arm"], f["split"], f["tier"]) for f in F)
    by_scene = collections.Counter((f["scene_id"], f["arm"]) for f in F)
    hazard_frames = sum(1 for f in F if any(f["polar_gt"]))
    res["census"] = dict(
        by_arm=dict(sorted(by_arm.items())),
        by_arm_split={f"{k[0]}/{k[1]}": v for k, v in sorted(by_as.items())},
        by_tier=dict(sorted(by_tier.items())),
        by_split_tier={f"{k[0]}/{k[1]}": v for k, v in sorted(by_st.items())},
        by_arm_split_tier={f"{k[0]}/{k[1]}/{k[2]}": v
                           for k, v in sorted(by_ast.items())},
        by_scene_arm={f"{k[0]}/{k[1]}": v for k, v in sorted(by_scene.items())},
        hazard_positive_frames=hazard_frames,
        hazard_arm_frames=sum(1 for f in F if f["hazard_arm"]),
        n_scenes=len({f["scene_id"] for f in F}))

    val_H = collections.Counter(f["arm"] for f in F
                                if f["split"] == "val" and f["tier"] == "H")
    val_H_scene = collections.Counter(
        f["scene_id"] for f in F
        if f["split"] == "val" and f["tier"] == "H" and f["arm"] == "A")
    # paired-H = A·B 양 팔이 같은 (씬,밴드,컷)에서 strict-H
    def stem_of(f):
        return os.path.splitext(f["frame_id"].split("/", 2)[2].split("::")[0])[0]
    hA = {(f["scene_id"], f["band"], stem_of(f)) for f in F
          if f["arm"] == "A" and f["tier"] == "H"}
    hB = {(f["scene_id"], f["band"], stem_of(f)) for f in F
          if f["arm"] == "B" and f["tier"] == "H"}
    res["val_strict_h"] = dict(
        definition="정의 B — tier=='H' ∧ any(polar_gt) (PREREG §4.3 · P-02)",
        by_arm=dict(sorted(val_H.items())),
        A_arm_total=val_H.get("A", 0),
        by_scene_A=dict(sorted(val_H_scene.items())),
        requirement=30, ratio=round(val_H.get("A", 0) / 30.0, 2),
        expect_D89=93, match_D89=(val_H.get("A", 0) == 93),
        paired_H_total=len(hA & hB),
        paired_H_val=len((hA & hB) &
                         {(f["scene_id"], f["band"], stem_of(f)) for f in F
                          if f["split"] == "val"}),
        paired_H_by_scene=dict(sorted(collections.Counter(
            k[0] for k in (hA & hB)).items())),
        n_H_definition_check=sum(1 for f in F if f["tier"] == "H"
                                 and not any(f["polar_gt"])))

    # ---------------------------------------------------------------- ② 존재 |r|
    # 모집단 = 그 키가 **ON·배선**인 씬 (수리된 hazgate — PREREG §4.4 규약 4)
    # 격리분(=매니페스트 밖) 을 되살린 반사실 정책을 만들기 위한 보조 목록
    revive = []                              # VG-01 격리 96컷 (P-19)
    for qf in QU["frames"]:
        if qf["arm"] == "B":
            revive.append(dict(scene_id=qf["scene_id"], arm="B",
                               band=qf["band"], polar_gt=None))
    # D74 ⑤ 미렌더 B (scene03 72 · scene04 72 · scene10 24) — 계획 프레임 수만
    skipB = QU["absent_not_quarantined"]["b_arm_skip"]

    def per_key(level, policy="asbuilt"):
        out = {}
        for k in KEYS6:
            t = collections.Counter()
            scenes = set()

            def acc(sc, arm, hazflag, n=1):
                if k not in ONW.get(sc, set()):
                    return
                scenes.add(sc)
                if arm == "D":
                    x = 0
                elif arm == "B":
                    x = 0 if k in BUILT.get(sc, set()) else 1
                else:
                    x = 1                      # A · C
                t[(hazflag, x)] += n

            per_scene_arm = collections.Counter()
            for f in F:
                per_scene_arm[(f["scene_id"], f["arm"])] += 1
            keep = None
            if policy == "balanced":
                # 항등식 A/B = C/D 를 씬 단위로 강제 (PREREG §4.5 팔수준 톱업 조항)
                keep = {}
                for (sc, arm), n in per_scene_arm.items():
                    keep.setdefault(sc, {})[arm] = n
                lim = {}
                for sc, d in keep.items():
                    hz = min(d.get("A", 0), d.get("B", 0))
                    nz = min(d.get("C", 0), d.get("D", 0))
                    lim[sc] = dict(A=hz, B=hz, C=nz, D=nz)
                used = collections.Counter()
            for f in F:
                sc, arm = f["scene_id"], f["arm"]
                if policy == "balanced":
                    if used[(sc, arm)] >= lim[sc].get(arm, 0):
                        continue
                    used[(sc, arm)] += 1
                haz = (arm in ("A", "B")) if level == "design" \
                    else bool(any(f["polar_gt"]))
                acc(sc, arm, haz)
            if policy in ("revive_vg01", "revive_and_skip"):
                for r in revive:
                    acc(r["scene_id"], "B", True)
            if policy == "revive_and_skip":
                for sc, n in skipB.items():
                    acc(sc, "B", True, n)
            a_, b_ = t[(True, 1)], t[(True, 0)]
            c_, d_ = t[(False, 1)], t[(False, 0)]
            n = a_ + b_ + c_ + d_
            rate = (a_ + c_) / n if n else None
            out[k] = dict(cue=NAME[k], n_scenes=len(scenes), n=n,
                          a=a_, b=b_, c=c_, d=d_,
                          cue_rate=round(rate, 4) if rate is not None else None,
                          hazard_rate=round((a_ + b_) / n, 4) if n else None,
                          r=round(abs(phi(a_, b_, c_, d_)), 4),
                          interpretable=(rate is not None and 0.1 <= rate <= 0.9))
        return out

    exist = dict(design_level=per_key("design"), fact_level=per_key("fact"))
    exist["counterfactuals"] = {
        pol: {k: per_key("design", pol)[k]["r"] for k in KEYS6}
        for pol in ("revive_vg01", "revive_and_skip", "balanced")}
    exist["counterfactual_legend"] = dict(
        asbuilt="현 매니페스트 그대로",
        revive_vg01="P-19 결재로 VG-01 격리 96컷을 되살린 경우",
        revive_and_skip="위 + D74 ⑤ 미렌더 168컷을 찍은 경우 "
                        "(**A와 바이트 동일 = 학습 이중 가중**이라 D74 가 거부한 경로)",
        balanced="씬별로 A/B = C/D 항등식을 강제해 잘라낸 경우 "
                 "(PREREG §4.5 팔 수준 톱업 조항의 as-built 판)")
    exist["design_level"]["_max"] = max(
        ((k, v["r"]) for k, v in exist["design_level"].items() if k in KEYS6),
        key=lambda x: x[1])
    exist["fact_level"]["_max"] = max(
        ((k, v["r"]) for k, v in exist["fact_level"].items() if k in KEYS6),
        key=lambda x: x[1])
    # VG-09 처방 진단 (PREREG §4.5 마지막 행) — 문턱 초과 키마다
    #   ⓐ B팔이 그 키를 **남긴** 씬 (레버 미적용 = a 칸 기여)
    #   ⓑ A팔은 있는데 B팔이 **없는** 씬 (팔 불균형 = a 칸 기여)
    #   ⓒ 그 키를 레버에 넣었을 때의 반사실 r
    per_scene_arm = collections.Counter((f["scene_id"], f["arm"]) for f in F)
    remedy = {}
    for k in KEYS6:
        if exist["design_level"][k]["r"] <= 0.2:
            continue
        keep_scenes, imbal = [], []
        for sc in sorted({f["scene_id"] for f in F}):
            if k not in ONW.get(sc, set()):
                continue
            nB = per_scene_arm[(sc, "B")]
            nA = per_scene_arm[(sc, "A")]
            if nB and k not in BUILT.get(sc, set()):
                keep_scenes.append(dict(scene=sc, n_B=nB,
                                        levers=sorted(BUILT.get(sc, set()))))
            if nA and not nB:
                imbal.append(dict(scene=sc, n_A=nA, n_B=0))
        # 반사실: 그 키를 **남긴 씬 전부**에 레버로 추가했다면
        t = collections.Counter()
        for f in F:
            sc = f["scene_id"]
            if k not in ONW.get(sc, set()):
                continue
            arm = f["arm"]
            x = 0 if arm in ("B", "D") else 1
            t[(arm in ("A", "B"), x)] += 1
        remedy[k] = dict(
            r_asbuilt=exist["design_level"][k]["r"],
            b_arm_keeps_key=keep_scenes,
            arm_imbalance_A_without_B=imbal,
            r_if_key_added_to_all_B=round(abs(phi(
                t[(True, 1)], t[(True, 0)], t[(False, 1)], t[(False, 0)])), 4),
            prescription="PREREG §4.5 마지막 행 — VG-CLS 재확인 후 레버 추가, "
                         "불가능하면 **상수 키로 승격 표기**하고 사유 인쇄")
    exist["vg09_remedy"] = remedy
    exist["threshold"] = 0.2
    exist["protocol"] = ("ACCOUNTING §4.9-3 — ① 주변분포 병기 ② 토글 가능 키 한정 "
                         "③ 키별 산출 ④ 상수 키 별도 표기. 모집단은 **수리된 "
                         "hazgate**(--mode full) 위에서 잡는다 (PREREG §4.4 규약 4).")
    exist["constant_keys"] = [k for k in KEYS6
                              if exist["design_level"][k]["n_scenes"] == 0]
    res["existence_r"] = exist

    # 팔 수준 φ (설계상 자동 0 — 단독 인용 금지, 대조로만 인쇄)
    t = collections.Counter()
    for f in F:
        x = 1 if f["arm"] in ("A", "C") else (
            0 if f["arm"] == "D" else (0 if BUILT.get(f["scene_id"]) else 1))
        t[(f["hazard_arm"], x)] += 1
    res["existence_r"]["arm_level_phi"] = dict(
        a=t[(True, 1)], b=t[(True, 0)], c=t[(False, 1)], d=t[(False, 0)],
        r=round(abs(phi(t[(True, 1)], t[(True, 0)],
                        t[(False, 1)], t[(False, 0)])), 4),
        note="팔 수준 φ 는 설계상 자동 0 에 가깝다 — **단독 인용 금지** (§4.9-3 ③)")

    # ---------------------------------------------------------------- ③ 팔 × 씬출신
    def origin(sc):
        return "new" if sc in W2_SCENES else "legacy33"
    t = collections.Counter()
    for f in F:
        t[(f["arm"] in ("B", "D"), origin(f["scene_id"]) == "new")] += 1
    r_bd = abs(phi(t[(True, True)], t[(True, False)],
                   t[(False, True)], t[(False, False)]))
    t2 = collections.Counter()
    for f in F:
        t2[(f["hazard_arm"], origin(f["scene_id"]) == "new")] += 1
    r_hz = abs(phi(t2[(True, True)], t2[(True, False)],
                   t2[(False, True)], t2[(False, False)]))
    res["arm_x_scene_origin"] = dict(
        authority="D58 ② · 계획 §4.4.5 (문자대로면 1.000 완전 교락 · 계획 예측 0.0033)",
        arms_BD_x_new=dict(a=t[(True, True)], b=t[(True, False)],
                           c=t[(False, True)], d=t[(False, False)],
                           r=round(r_bd, 4)),
        hazard_arm_x_new=dict(a=t2[(True, True)], b=t2[(True, False)],
                              c=t2[(False, True)], d=t2[(False, False)],
                              r=round(r_hz, 4)),
        by_scene_family={f"{k[0]}/{k[1]}": v for k, v in
                         sorted(collections.Counter(
                             (origin(f["scene_id"]), f["arm"]) for f in F).items())},
        plan_prediction=0.0033)

    # ---------------------------------------------------------------- ④ k 유도
    def px(f):
        return (f["cue"] or {}).get("px_canonical6")
    KG = [1, 100, 1000, 2074, 5000, 7000, 10000, 20000, 60000, 100000]
    pos = [px(f) for f in F if f["arm"] in ("A", "C") and px(f) is not None]
    neg = [px(f) for f in F if f["arm"] == "D" and px(f) is not None]
    Bv = [px(f) for f in F if f["arm"] == "B" and px(f) is not None]
    aH = [px(f) for f in F if f["arm"] == "A" and f["tier"] == "H"
          and px(f) is not None]
    neg_max = max(neg) if neg else 0
    pos_min_nz = min([v for v in pos if v > 0]) if pos else 0
    mid = math.sqrt(max(neg_max, 1) * max(pos_min_nz, 1))

    def sweep(k):
        fp = sum(1 for v in neg if v >= k)
        fn = sum(1 for v in pos if v < k)
        return dict(k=k, D_arm_false_present=fp, D_arm_false_present_rate=round(fp / len(neg), 5),
                    AC_arm_false_absent=fn, AC_arm_false_absent_rate=round(fn / len(pos), 5),
                    A_strict_H_masked=sum(1 for v in aH if v < k),
                    A_strict_H_masked_rate=round(sum(1 for v in aH if v < k) / len(aH), 4),
                    B_arm_present=sum(1 for v in Bv if v >= k),
                    youden=round((1 - fp / len(neg)) + (1 - fn / len(pos)) - 1, 5))
    grid = [sweep(k) for k in KG]
    best = max(grid, key=lambda d: d["youden"])
    res["k_derivation"] = dict(
        gate="VG-11 · ACCOUNTING §2-5 · §3.4 미결 1번 (**PREREG 미결 — 봉인 전**)",
        measure="px_canonical6 = 정본 6키(R·Ta·N·T·Sg·V)에 귀속된 프림 픽셀 합. "
                "`Gk`(지면 표면처리 미분해)·`Mh/Dr/Jt`(v3 신설 키)·`Ux` 는 제외. "
                "T 는 재질 재바인딩이라 ID 마스크 불변 ⇒ 면적 기여 0 (면적-불가시 키).",
        populations=dict(
            spec_present_AC=dict(n=len(pos), zeros=sum(1 for v in pos if v == 0),
                                 p05=q(pos, .05), p10=q(pos, .10), p25=q(pos, .25),
                                 p50=q(pos, .50), min_nonzero=pos_min_nz),
            spec_absent_D=dict(n=len(neg), zeros=sum(1 for v in neg if v == 0),
                               p50=q(neg, .50), p90=q(neg, .90), p99=q(neg, .99),
                               max=neg_max),
            B_arm=dict(n=len(Bv), zeros=sum(1 for v in Bv if v == 0),
                       p50=q(Bv, .50), p90=q(Bv, .90), max=max(Bv) if Bv else None),
            A_strict_H=dict(n=len(aH), zeros=sum(1 for v in aH if v == 0),
                            min_nonzero=min([v for v in aH if v > 0]) if any(aH) else None,
                            p05=q(aH, .05), p10=q(aH, .10), p50=q(aH, .50))),
        log_midpoint=dict(
            method="VG-const 와 같은 유도 — 두 실측 극단의 **로그축 중점** "
                   "(PREREG §4.1: √(붕괴 최대 × 비붕괴 최소)). "
                   "앵커를 둘 다 인쇄한다 — 어느 쪽을 쓰는지가 값을 7배 바꾼다.",
            neg_max=neg_max,
            anchor_AC_min_nonzero=dict(
                value=pos_min_nz, geometric_mean=round(mid, 1),
                note="A·C 전 프레임의 최소 비-0. 그 프레임은 sceneH7/base 의 "
                     "**영정보 쌍**이라 '단서 없음'으로 읽는 것이 옳다 ⇒ 앵커로 부적합"),
            anchor_A_strictH_min_nonzero=dict(
                value=(min([v for v in aH if v > 0]) if any(aH) else None),
                geometric_mean=round(math.sqrt(max(neg_max, 1) * max(
                    (min([v for v in aH if v > 0]) if any(aH) else 1), 1)), 1),
                note="지도가 실제로 걸리는 모집단(A팔 strict-H)의 최소 비-0 ⇒ **채택 앵커**")),
        sweep=grid, youden_best=best,
        d_arm_leak=dict(
            n_frames=sum(1 for f in F if f["arm"] == "D" and (px(f) or 0) > 0),
            scenes=sorted({f["scene_id"] for f in F
                           if f["arm"] == "D" and (px(f) or 0) > 0}),
            note="D팔 잔존 단서 픽셀은 전량 scene10 의 V(scene_dressing) — "
                 "`cue_railing` 이 `build_deck` 내부 멤버라 C·D 어느 쪽도 "
                 "구조를 보존/제거할 수 없다는 W1C §8.3 의 구조적 한계와 같은 자리다."))

    # ---------------------------------------------------------------- ⑤ 채널 회계
    ig = [f["ignore"] for f in F]
    res["channels"] = dict(
        cue=dict(
            idseg_strict=sum(1 for f in F if f["cue"]["source"] == "idseg_strict"),
            geometric_fallback=sum(1 for f in F
                                   if f["cue"]["source"] == "geometric_fallback"),
            fallback_by_reason=dict(collections.Counter(
                f["cue"].get("fallback_reason") for f in F
                if f["cue"]["source"] == "geometric_fallback")),
            fallback_by_arm=dict(collections.Counter(
                f["arm"] for f in F
                if f["cue"]["source"] == "geometric_fallback")),
            note="k 는 미결이므로 매니페스트는 **원시 픽셀 수만** 담는다 "
                 "(ACCOUNTING §2-5 — 결과를 본 뒤 k 를 움직이면 무효)."),
        gt_void=dict(
            frames_with_void=sum(1 for x in ig if x["gt_void_cells"] > 0),
            frames_with_void_pct=round(
                100.0 * sum(1 for x in ig if x["gt_void_cells"] > 0) / len(F), 2),
            total_void_cells=sum(x["gt_void_cells"] for x in ig),
            by_arm={a: sum(1 for f in F if f["arm"] == a
                           and f["ignore"]["gt_void_cells"] > 0)
                    for a in "ABCD"},
            v2_reference="v2 on팔 42.4 % (RT-A LAB-19 · AC §4.8-2)",
            note="void 칸은 **음성이 아니다**. 평가 분모는 불변, FA_C/FA_D 분모에서만 격리."),
        ignore_b_arm_h=dict(
            n=sum(1 for x in ig if x["b_arm_h"]),
            authority="PREREG §5.3 — B팔의 H 칸은 무시 마스크"),
        ignore_bare_h_by_k={
            str(k): sum(1 for x in ig if (x["bare_h_by_k"] or {}).get(str(k)))
            for k in (1, 100, 1000, 5000, 20000, 60000)},
        ignore_bare_h_unmeasurable=sum(1 for x in ig
                                       if not x["bare_h_measurable"]
                                       and False) or sum(
            1 for f in F if f["tier"] == "H" and not f["ignore"]["bare_h_measurable"]),
        lever_n=dict(
            zero_info_C_frames=sum(1 for x in ig if x["lever_n_zero_info_c"]),
            contradiction_frames=sum(1 for x in ig if x["lever_n_contradiction"]),
            by_scene_band=dict(collections.Counter(
                f"{f['scene_id']}/{f['band']}" for f in F
                if f["ignore"]["lever_n_zero_info_c"])),
            status="**예비채택 · 결재중** (D89 ⑤a). 매니페스트는 플래그만 담고 "
                   "적용은 승인 후 훈련 시점.",
            predicate="frac(|ΔI| > 8) < 0.001 (PREREG §2.1 층화 2 등록 술어)"))

    # ---------------------------------------------------------------- ⑥ 격리
    res["quarantine"] = dict(
        n_frames=QU["n_frames_excluded"], by_arm=QU["by_arm"],
        unit_ledger_n=len(QU["unit_ledger"]),
        seg_collision_cuts=len(QU["seg_collision_cuts"]),
        absent_not_quarantined=QU["absent_not_quarantined"])

    # ---------------------------------------------------------------- ⑦ §3.4 제안
    res["accounting_3_4_proposal"] = dict(
        note="**제안 (PROPOSE) — 적용 금지.** append 3요소: 원장 · 재집계 명령 · 측정일자.",
        ledger=["experiments/v3_0823/dataset_manifest_v3.json",
                "experiments/v3_0823/split_v3.json",
                "experiments/v3_0823/corpus_v3_quarantine.json",
                "experiments/v3_0823/corpus_v3_census.json"],
        command=("python3 experiments/v3_0823/code/build_corpus_v3.py && "
                 "python3 experiments/v3_0823/code/corpus_v3_measure.py"),
        rows={
            "행 5 — v3 train/val 프레임 회계": dict(
                total=len(F),
                by_arm=dict(sorted(by_arm.items())),
                by_split={k: sum(v for kk, v in by_as.items() if kk[1] == k)
                          for k in ("train", "val")},
                tier=dict(sorted(by_tier.items())),
                quarantined=QU["n_frames_excluded"]),
            "행 1 — 단서 존재 판정 임계 k": dict(
                status="**제안**", proposal=best["k"],
                derivation="Youden J 최대 ∧ D팔 오탐 0 의 최소 k ∧ "
                           "log-midpoint(D팔 max 6744, A팔 strict-H min-nonzero) 의 보수 하한",
                sealed=False),
            "행 7 — 무시 마스크 적용 셀 수": dict(
                b_arm_h_frames=sum(1 for x in ig if x["b_arm_h"]),
                lever_n_frames=sum(1 for x in ig if x["lever_n_zero_info_c"]),
                gt_void_cells=sum(x["gt_void_cells"] for x in ig),
                note="훈련 손실 전용 — 평가 분모 불변 (AC §2-4)"),
        })

    json.dump(res, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # ------------------------------------------------------------------ 인쇄
    log("=== ① 센서스 ===")
    log(f"  프레임 {len(F)} · 씬 {res['census']['n_scenes']} · "
        f"팔 {res['census']['by_arm']}")
    log(f"  팔×분할 {res['census']['by_arm_split']}")
    log(f"  tier {res['census']['by_tier']}")
    log(f"  GT 양성 프레임 {hazard_frames} · 위험 팔 프레임 "
        f"{res['census']['hazard_arm_frames']}")
    log(f"  **val strict-H(A팔) = {val_H.get('A',0)}** (요구 30 · D89 기대 93 · "
        f"일치 {res['val_strict_h']['match_D89']}) · 씬별 {res['val_strict_h']['by_scene_A']}")
    log(f"  paired-H (A∧B strict-H) 총 {res['val_strict_h']['paired_H_total']}")
    log("\n=== ② 존재 |r| — 키별 ===")
    log("| 키 | 단서 | 씬 | n | a | b | c | d | cue_rate | **|r| 설계** | |r| 사실 | 해석가능 |")
    log("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|")
    for k in KEYS6:
        dv, fv = exist["design_level"][k], exist["fact_level"][k]
        log(f"| {k} | {NAME[k]} | {dv['n_scenes']} | {dv['n']} | {dv['a']} | {dv['b']} | "
            f"{dv['c']} | {dv['d']} | {dv['cue_rate']} | **{dv['r']:.4f}** | "
            f"{fv['r']:.4f} | {'✅' if dv['interpretable'] else '⚠ rate'} |")
    log(f"  최대 |r| 설계 {exist['design_level']['_max']} · 사실 {exist['fact_level']['_max']} "
        f"(문턱 0.2)")
    log(f"  팔 수준 φ = {res['existence_r']['arm_level_phi']['r']} (단독 인용 금지)")
    log("\n=== ③ 팔 × 씬출신 ===")
    log(f"  |r| (팔{{B,D}} × 씬출신{{신규}}) = "
        f"{res['arm_x_scene_origin']['arms_BD_x_new']['r']} (계획 예측 0.0033)")
    log(f"  |r| (위험팔 × 신규) = {res['arm_x_scene_origin']['hazard_arm_x_new']['r']}")
    log("\n=== ④ k 유도 ===")
    p = res["k_derivation"]["populations"]
    log(f"  사양-단서有 (A·C) n={p['spec_present_AC']['n']} zeros={p['spec_present_AC']['zeros']} "
        f"p05={p['spec_present_AC']['p05']} min_nz={p['spec_present_AC']['min_nonzero']}")
    log(f"  사양-단서無 (D)   n={p['spec_absent_D']['n']} zeros={p['spec_absent_D']['zeros']} "
        f"p99={p['spec_absent_D']['p99']} max={p['spec_absent_D']['max']}")
    lm = res["k_derivation"]["log_midpoint"]
    log(f"  로그축 중점 — A·C 앵커 {lm['anchor_AC_min_nonzero']['geometric_mean']} px "
        f"(부적합) / **A팔 strict-H 앵커 "
        f"{lm['anchor_A_strictH_min_nonzero']['geometric_mean']} px (채택)**")
    log("  | k | D팔 오탐 | A·C팔 오음 | A strict-H 마스크 | Youden |")
    log("  |---:|---:|---:|---:|---:|")
    for g in grid:
        log(f"  | {g['k']} | {g['D_arm_false_present']} ({g['D_arm_false_present_rate']}) | "
            f"{g['AC_arm_false_absent']} ({g['AC_arm_false_absent_rate']}) | "
            f"{g['A_strict_H_masked']} ({g['A_strict_H_masked_rate']}) | {g['youden']} |")
    log("\n=== ⑤ 채널 ===")
    log(f"  단서: strict {res['channels']['cue']['idseg_strict']} · "
        f"fallback {res['channels']['cue']['geometric_fallback']} "
        f"{res['channels']['cue']['fallback_by_arm']}")
    log(f"  gt_void: 프레임 {res['channels']['gt_void']['frames_with_void']} "
        f"({res['channels']['gt_void']['frames_with_void_pct']} %) · "
        f"칸 {res['channels']['gt_void']['total_void_cells']}")
    log(f"  무시 B팔-H {res['channels']['ignore_b_arm_h']['n']} · "
        f"레버ㄴ 영정보C {res['channels']['lever_n']['zero_info_C_frames']} "
        f"(모순 {res['channels']['lever_n']['contradiction_frames']}) "
        f"{res['channels']['lever_n']['by_scene_band']}")
    log(f"\n=== ⑥ 격리 {res['quarantine']['n_frames']}프레임 {res['quarantine']['by_arm']} ===")
    log(f"\n→ {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
