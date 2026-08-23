#!/usr/bin/env python3
"""
p4_selftest.py — 게이트 G-P4-3: 정본 구현체 `selection_v3.py`가 등록된 규약을 **실제로 강제하는가**.

검사 5건
  T1  무시 마스크 없음 -> 실데이터에서 스칼라 경로와 항등 (v2 재현 검증이 규약에 영향받지 않음)
  T2  무시 마스크가 H 분모/분자에서 프레임을 실제로 뺀다
  T3  무시 마스크가 FA 항 분자에서 FP를 실제로 뺀다
  T4  FA 모집단 제한(FA_D 상당)이 FA 항만 바꾸고 F1/H를 안 바꾼다
  T5  상수출력 -> VG-1 거부 -> S = -inf
  T6  미등록 FA 모집단 이름 -> 하드 실패
"""
from __future__ import annotations

import csv
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import selection_v3 as SV  # noqa: E402

R = "/home/vislab/Desktop/work_sy/Practice_NegObs"
CELLS = ["A1", "B1", "C1", "D1", "E1", "A2", "B2", "C2", "D2", "E2",
         "A3a", "B3a", "C3a", "D3a", "E3a", "A3b", "B3b", "C3b", "D3b", "E3b"]
RUN, EP = "rgb_s42", 9          # 출하 선택 에폭 (config.json::best_epoch)


def load_val_dump(run):
    p = f"{R}/experiments/dayrun_0820/runs/v2/{run}/eval_test/per_frame_val.csv"
    rows = list(csv.DictReader(open(p)))
    prob = np.array([[float(r["p_" + c]) for c in CELLS] for r in rows])
    gt = np.array([[int(r["g_" + c]) for c in CELLS] for r in rows])
    tier = np.array([r["tier"] for r in rows])
    arm = np.array([r["toggle_state"] for r in rows])
    return prob, gt, tier, arm


def main():
    ok = True
    prob, gt, tier, arm = load_val_dump(RUN)
    row = [r for r in csv.DictReader(
        open(f"{R}/experiments/dayrun_0820/runs/v2/{RUN}/metrics.csv"))
        if int(r["epoch"]) == EP][0]

    # ---- T1 항등 -----------------------------------------------------------
    r0 = SV.compute_selection(prob, gt, tier, 0.5)
    t1 = (abs(r0["f1"] - float(row["val_f1"])) < 1e-6
          and abs(r0["fa"] - float(row["val_fpr"])) < 1e-6
          and r0["n_H"] == 6 and r0["h_hits"] == 6
          and abs(r0["S"] - SV.sel_score_v3(r0["f1"], r0["h_hits"], r0["n_H"], r0["fa"])) < 1e-12)
    print(f"T1 ignore=None 항등            : {'PASS' if t1 else 'FAIL'}  "
          f"f1={r0['f1']:.6f}(csv {float(row['val_f1']):.6f}) "
          f"fa={r0['fa']:.6f}(csv {float(row['val_fpr']):.6f}) n_H={r0['n_H']} h={r0['h_hits']}")
    ok &= t1

    # ---- T2 H 분모에서 프레임이 빠지는가 -----------------------------------
    ig = np.zeros_like(gt, dtype=bool)
    hsel = (tier == "H") & (gt > 0.5).any(1)
    idx = np.where(hsel)[0][:2]                 # H 프레임 2장의 양성 칸을 전부 마스크
    for i in idx:
        ig[i] = (gt[i] > 0.5)
    r2 = SV.compute_selection(prob, gt, tier, 0.5, ignore=ig)
    t2 = (r2["n_H"] == r0["n_H"] - 2)
    print(f"T2 마스크 -> H 분모 축소        : {'PASS' if t2 else 'FAIL'}  "
          f"n_H {r0['n_H']} -> {r2['n_H']} (기대 {r0['n_H'] - 2})")
    ok &= t2

    # ---- T3 마스크된 FP 가 FA 에 안 들어가는가 -----------------------------
    fp_mask = (prob >= 0.5) & (gt <= 0.5)
    ig3 = np.zeros_like(gt, dtype=bool)
    ig3[fp_mask] = True                          # 모든 FP 를 마스크
    r3 = SV.compute_selection(prob, gt, tier, 0.5, ignore=ig3)
    t3 = r3["fa"] < 1e-12 and r0["fa"] > 1e-3
    print(f"T3 마스크 -> FA 분자 제거       : {'PASS' if t3 else 'FAIL'}  "
          f"fa {r0['fa']:.6f} -> {r3['fa']:.6e}")
    ok &= t3

    # ---- T4 FA 모집단 제한 -------------------------------------------------
    fa_cells = np.repeat((arm == "off")[:, None], 20, axis=1)   # v2 의 D팔 상당 근사
    r4 = SV.compute_selection(prob, gt, tier, 0.5, fa_cells=fa_cells,
                              fa_population="v3_D_arm_cells")
    t4 = (abs(r4["f1"] - r0["f1"]) < 1e-12 and r4["n_H"] == r0["n_H"]
          and abs(r4["fa"] - r0["fa"]) > 1e-6 and r4["n_fa_cells"] < r0["n_fa_cells"])
    print(f"T4 FA 모집단 제한은 FA만 바꾼다 : {'PASS' if t4 else 'FAIL'}  "
          f"fa {r0['fa']:.6f}(n={r0['n_fa_cells']}) -> {r4['fa']:.6f}(n={r4['n_fa_cells']}), "
          f"f1/H 불변={abs(r4['f1'] - r0['f1']) < 1e-12}")
    ok &= t4

    # ---- T5 상수출력 -> VG-1 거부 ------------------------------------------
    const = np.full_like(prob, 0.5014) + np.random.default_rng(0).normal(0, 1e-6, prob.shape)
    r5 = SV.compute_selection(const, gt, tier, 0.5)
    t5 = (not r5["vg1_pass"]) and r5["S"] == float("-inf")
    print(f"T5 상수출력 -> VG-1 거부        : {'PASS' if t5 else 'FAIL'}  "
          f"spread={r5['spread']:.2e} (<{SV.VG1_SPREAD_MIN:g}) S={r5['S']}")
    ok &= t5

    # ---- T6 미등록 모집단 -> 하드 실패 -------------------------------------
    try:
        SV.compute_selection(prob, gt, tier, 0.5, fa_population="아무거나")
        t6 = False
    except AssertionError:
        t6 = True
    print(f"T6 미등록 FA 모집단 -> 하드실패 : {'PASS' if t6 else 'FAIL'}")
    ok &= t6

    print(f"\nG-P4-3 = {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
