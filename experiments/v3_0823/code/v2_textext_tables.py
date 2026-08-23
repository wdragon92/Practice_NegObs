#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v2_textext_tables.py — v2 체크포인트 zero-shot 재채점의 **계기판 표 생성** (CPU 전용)

ACCOUNTING §2-8 이 명령한 "진짜 before" 를 계기판 ①·③ 의 형식으로 인쇄한다.
입력은 `rescore_v3textext.sh` 가 남긴 확률 덤프뿐이다(재추론 없음).

  eval_v3textext/<run>/per_frame.csv       (A,C) 패스 — on=A · off=C
  eval_v3textext/<run>/bd/per_frame.csv    (B,D) 패스 — on=B · off=D

**규약 준수 (전부 원장에서 읽어온 정의다)**

  · 쌍 = **(A,C)** — AC §2-2 세대 통일. v2 공표 44.7 %/0 % 는 (A,D) 라 인용 금지.
  · C팔 GT = **사양 상수(전 칸 음성)** — AC-INSTR-1 C3-2. 매니페스트에 실린 라벨러
    `polar_gt` 행은 **쓰지 않는다**. (본 표는 두 권위가 일치함을 함께 인쇄한다.)
  · **sceneH3 는 "완전 은닉" 층** (D87 ①) — 풀링된 twin-conditional recall 에
    **절대 넣지 않고** 자기 행에서 Δp 분포로만 보고한다.
  · 운용점 = τ_op 0.5(참고) + **FA-정합 이중축** (PREREG §2 공통 격자)
      프레임축 `frame_fa_off` 목표 .359/.200/.100/.050
      칸축     `cell_fpr_off` 목표 0.046732/0.026035/0.013017/0.006509 (MAP-C)
    **정합 기준 팔 = D팔** (MILESTONE §6.2-2). τ 는 정확분위에서 취해
    **목표 이하 최대 달성률**을 준다.
  · σ = 표본표준편차 **ddof=1**, n=3 시드 (PREREG §3.2). b2 팔은 σ 기반 주장에서 제외.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
CODE = os.path.join(REPO, "experiments", "mainrun_0819", "code")
sys.path.insert(0, CODE)
import gridspec  # noqa: E402

V3 = os.path.join(REPO, "experiments", "v3_0823")
EV = os.path.join(V3, "eval_v3textext")

RUNS = ["rgb_s42", "rgb_s43", "rgb_s44",
        "depth_s42", "depth_s43", "depth_s44",
        "b2_s42", "b2_s43", "b2_s44"]
ARMS = {"rgb": ["rgb_s42", "rgb_s43", "rgb_s44"],
        "depth": ["depth_s42", "depth_s43", "depth_s44"],
        "b2": ["b2_s42", "b2_s43", "b2_s44"]}
TAU_STAR = {"rgb_s42": 0.63, "rgb_s43": 0.71, "rgb_s44": 0.31,
            "depth_s42": 0.36, "depth_s43": 0.21, "depth_s44": 0.60,
            "b2_s42": 0.45, "b2_s43": 0.45, "b2_s44": 0.45}

FRAME_TARGETS = [0.359, 0.200, 0.100, 0.050]
CELL_TARGETS = [0.046732, 0.026035, 0.013017, 0.006509]

H_POOL = ["sceneH1", "sceneH2"]          # paired-H 풀링 층 (D87 ①)
H_HIDDEN = "sceneH3"                     # 완전 은닉 층 — 자기 행
NCUE = ["sceneN9", "sceneN11"]
LAT = "sceneL1"


# ------------------------------------------------------------------ io
def read_pf(path, grid):
    """per_frame.csv -> dict. frame_id = '<band>/<arm>/<scene>/<file>' (4토막)."""
    key, tier, tog, P, G, scene = [], [], [], [], [], []
    with open(path) as f:
        rd = csv.DictReader(f)
        cells = [c[2:] for c in (rd.fieldnames or []) if c.startswith("p_")]
        if list(grid.cell_ids) != cells:
            raise SystemExit(f"[fatal] {path}: 칸 목록 불일치 {cells[:3]}… vs "
                             f"{grid.cell_ids[:3]}…")
        for r in rd:
            band, arm, sc, fn = r["frame_id"].split("/", 3)
            key.append((band, sc, fn))
            scene.append(r["scene_id"]); tier.append(r["tier"]); tog.append(r["toggle_state"])
            P.append([float(r[f"p_{c}"]) for c in cells])
            G.append([float(r[f"g_{c}"]) for c in cells])
    return dict(key=key, scene=np.array(scene), tier=np.array(tier), toggle=np.array(tog),
                probs=np.asarray(P, float), gt=np.asarray(G, float))


def arm_view(d, want):
    """한 팔만 뽑아 key -> row index 로 준다."""
    idx = [i for i, t in enumerate(d["toggle"]) if t == want]
    return {d["key"][i]: i for i in idx}, idx


# ------------------------------------------------------------------ operating points
def tau_for_target(stat, target):
    """`stat >= tau` 의 비율이 목표 **이하이면서 최대**가 되는 정확분위 tau.

    stat = D팔 통계량 (프레임축: 프레임별 최대확률 · 칸축: 전 칸 확률).
    후보는 관측값 자체 + max 초과값 1개. rate 는 tau 에 대해 단조 감소하므로,
    목표 이하가 되는 **가장 작은** 후보가 곧 '목표 이하 최대 달성률'을 준다.
    """
    s = np.sort(np.unique(np.asarray(stat, float)))
    cands = np.concatenate([s, [s[-1] + 1e-9]])
    n = len(stat)
    for t in cands:
        rate = float((np.asarray(stat) >= t).sum()) / n
        if rate <= target + 1e-15:
            return float(t), rate
    return float(cands[-1]), 0.0


# ------------------------------------------------------------------ metrics
def twin_block(ac, don_idx, doff_map, sel_keys, tau):
    """한 층·한 운용점의 twin-conditional recall (프레임축 + 칸축).

    · 프레임축 분모 = A팔 중 **그리드 내 양성 칸 ≥ 1** 인 프레임 (PREREG §2.1)
    · twin 발화 = A 에서 발화한 GT-양성 칸 중 **같은 칸이 C 에서는 미발화**인 것이 존재
    · 칸축 분모 = A팔 양성 칸 총수
    """
    n_haz = n_det = n_twin = 0
    n_pos = n_hit = n_twinhit = 0
    for k in sel_keys:
        ia = don_idx[k]
        ic = doff_map.get(k)
        pos = ac["gt"][ia] > 0.5
        if not pos.any() or ic is None:
            continue
        pa, pc = ac["probs"][ia], ac["probs"][ic]
        fire_a = pa >= tau
        fire_c = pc >= tau
        n_haz += 1
        n_pos += int(pos.sum())
        hit = pos & fire_a
        twin = hit & ~fire_c
        n_hit += int(hit.sum()); n_twinhit += int(twin.sum())
        if hit.any():
            n_det += 1
        if twin.any():
            n_twin += 1
    r = lambda a, b: (float(a) / b if b else float("nan"))   # noqa: E731
    return dict(n_frames=n_haz, n_pos_cells=n_pos,
                frame_recall=r(n_det, n_haz), frame_recall_twin=r(n_twin, n_haz),
                cell_recall=r(n_hit, n_pos), cell_recall_twin=r(n_twinhit, n_pos),
                n_det=n_det, n_twin=n_twin, n_hit=n_hit, n_twinhit=n_twinhit)


def dp_block(ac, don_idx, doff_map, sel_keys):
    """완전 은닉 층의 보고량 — Δp 분포 (D87 ①: '올바른 모델은 A/C 동등 발화')."""
    ds, df = [], []
    for k in sel_keys:
        ia = don_idx[k]; ic = doff_map.get(k)
        if ic is None:
            continue
        pos = ac["gt"][ia] > 0.5
        pa, pc = ac["probs"][ia], ac["probs"][ic]
        if pos.any():
            ds.append(float(pa[pos].max() - pc[pos].max()))
        df.append(float(pa.max() - pc.max()))

    def stats(v):
        if not v:
            return dict(n=0)
        a = np.asarray(v, float)
        return dict(n=len(a), mean=float(a.mean()), p50=float(np.median(a)),
                    p25=float(np.percentile(a, 25)), p75=float(np.percentile(a, 75)),
                    min=float(a.min()), max=float(a.max()),
                    mean_abs=float(np.abs(a).mean()),
                    frac_gt0=float((a > 0).mean()),
                    frac_abs_le_05=float((np.abs(a) <= 0.05).mean()))
    return dict(delta_score=stats(ds), delta_frame=stats(df))


def fa_block(d, idx, tau, scenes=None):
    """한 팔의 FA — 프레임축(어느 칸이든 발화) + 칸축(전 칸). GT 는 사양 상수 0."""
    if scenes is not None:
        idx = [i for i in idx if d["scene"][i] in scenes]
    if not idx:
        return dict(n_frames=0, n_cells=0, frame_fa=float("nan"), cell_fpr=float("nan"))
    P = d["probs"][idx]
    fire = P >= tau
    return dict(n_frames=len(idx), n_cells=int(P.size),
                frame_fa=float(fire.any(1).mean()), cell_fpr=float(fire.mean()),
                n_fire_cells=int(fire.sum()), n_fire_frames=int(fire.any(1).sum()))


def sector_block(d, idx, tau, grid, use_gt=False):
    """섹터별 발화(또는 GT 양성) — 프레임 양성률 + 칸 점유율."""
    sec = np.asarray(grid.sector_of)
    P = d["probs"][idx]
    M = (d["gt"][idx] > 0.5) if use_gt else (P >= tau)
    out, tot = {}, float(M.sum())
    for s, name in enumerate(grid.sector_names):
        m = M[:, sec == s]
        out[name] = dict(frame_rate=float(m.any(1).mean()),
                         cell_share=(float(m.sum()) / tot if tot else float("nan")),
                         n_cells=int(m.sum()))
    out["_total_cells"] = int(M.sum())
    out["_n_frames"] = len(idx)
    return out


# ------------------------------------------------------------------ per run
def run_tables(run, grid):
    ac = read_pf(os.path.join(EV, run, "per_frame.csv"), grid)
    bd = read_pf(os.path.join(EV, run, "bd", "per_frame.csv"), grid)
    A_map, A_idx = arm_view(ac, "on")
    C_map, C_idx = arm_view(ac, "off")
    B_map, B_idx = arm_view(bd, "on")
    D_map, D_idx = arm_view(bd, "off")

    # --- 층 정의 -------------------------------------------------------------
    # paired-H = A·B 가 **둘 다** strict-H (W3_REPORT §4.2 / PREREG_CUEOFF §4.2)
    Btier = {k: bd["tier"][i] for k, i in B_map.items()}
    paired_h = [k for k, i in A_map.items()
                if ac["tier"][i] == "H" and Btier.get(k) == "H"]
    by_scene = defaultdict(list)
    for k in paired_h:
        by_scene[k[1]].append(k)
    pool_keys = sorted([k for k in paired_h if k[1] in H_POOL])
    hid_keys = sorted([k for k in paired_h if k[1] == H_HIDDEN])
    # 완전 은닉 층은 H3 의 **전 A팔 프레임**(양성 칸 보유분)으로도 함께 본다
    hid_all = sorted([k for k, i in A_map.items()
                      if k[1] == H_HIDDEN and (ac["gt"][i] > 0.5).any()])
    all_haz = sorted([k for k, i in A_map.items() if (ac["gt"][i] > 0.5).any()])
    pool_all = sorted([k for k in all_haz if k[1] in H_POOL])

    # --- 운용점 --------------------------------------------------------------
    d_frame_stat = bd["probs"][D_idx].max(1)
    d_cell_stat = bd["probs"][D_idx].ravel()
    ops = [dict(name="tau_op", axis="ref", target=None, tau=0.5),
           dict(name="tau_star", axis="ref", target=None, tau=TAU_STAR[run])]
    for t in FRAME_TARGETS:
        tau, ach = tau_for_target(d_frame_stat, t)
        ops.append(dict(name=f"F@{t:.3f}", axis="frame", target=t, tau=tau, achieved=ach))
    for t in CELL_TARGETS:
        tau, ach = tau_for_target(d_cell_stat, t)
        ops.append(dict(name=f"C@{t:.6f}", axis="cell", target=t, tau=tau, achieved=ach))

    out = dict(run=run, tau_star=TAU_STAR[run],
               counts=dict(n_A=len(A_idx), n_B=len(B_idx), n_C=len(C_idx), n_D=len(D_idx),
                           n_haz_A=len(all_haz), n_pos_cells_A=int((ac["gt"][A_idx] > 0.5).sum()),
                           paired_H=len(paired_h),
                           paired_H_by_scene={s: len(v) for s, v in sorted(by_scene.items())},
                           n_pool_pairedH=len(pool_keys), n_hidden_pairedH=len(hid_keys),
                           n_hidden_all_haz=len(hid_all),
                           C_gt_positive_cells=int((ac["gt"][C_idx] > 0.5).sum()),
                           D_gt_positive_cells=int((bd["gt"][D_idx] > 0.5).sum())),
               ops=[])

    for op in ops:
        tau = op["tau"]
        row = dict(op)
        row["dash1"] = dict(
            pooled_pairedH=twin_block(ac, A_map, C_map, pool_keys, tau),
            pooled_allhaz_H1H2=twin_block(ac, A_map, C_map, pool_all, tau),
            hidden_H3_pairedH=twin_block(ac, A_map, C_map, hid_keys, tau),
            hidden_H3_allhaz=twin_block(ac, A_map, C_map, hid_all, tau),
            all_haz=twin_block(ac, A_map, C_map, all_haz, tau),
            by_scene={s: twin_block(ac, A_map, C_map, sorted(v), tau)
                      for s, v in sorted(by_scene.items())},
        )
        fa_c = fa_block(ac, C_idx, tau)
        fa_d = fa_block(bd, D_idx, tau)
        row["dash3"] = dict(
            FA_C=fa_c, FA_D=fa_d,
            diff_frame=fa_c["frame_fa"] - fa_d["frame_fa"],
            diff_cell=fa_c["cell_fpr"] - fa_d["cell_fpr"],
            by_scene={s: dict(FA_C=fa_block(ac, C_idx, tau, {s}),
                              FA_D=fa_block(bd, D_idx, tau, {s}))
                      for s in sorted(set(ac["scene"][C_idx]))},
            group=dict(
                ncue=dict(FA_C=fa_block(ac, C_idx, tau, set(NCUE)),
                          FA_D=fa_block(bd, D_idx, tau, set(NCUE))),
                hscenes=dict(FA_C=fa_block(ac, C_idx, tau, set(H_POOL + [H_HIDDEN])),
                             FA_D=fa_block(bd, D_idx, tau, set(H_POOL + [H_HIDDEN]))),
                lat=dict(FA_C=fa_block(ac, C_idx, tau, {LAT}),
                         FA_D=fa_block(bd, D_idx, tau, {LAT})),
            ),
        )
        l1_A = [i for i in A_idx if ac["scene"][i] == LAT]
        l1_C = [i for i in C_idx if ac["scene"][i] == LAT]
        l1_D = [i for i in D_idx if bd["scene"][i] == LAT]
        row["l1"] = dict(fire_A=sector_block(ac, l1_A, tau, grid),
                         fire_C=sector_block(ac, l1_C, tau, grid),
                         fire_D=sector_block(bd, l1_D, tau, grid))
        out["ops"].append(row)

    # Δp 는 운용점 무관 (확률 자체의 분포)
    out["hidden_dp"] = dict(pairedH=dp_block(ac, A_map, C_map, hid_keys),
                            all_haz=dp_block(ac, A_map, C_map, hid_all))
    out["pool_dp"] = dp_block(ac, A_map, C_map, pool_keys)
    l1_A = [i for i in A_idx if ac["scene"][i] == LAT]
    out["l1_hazard_gt"] = sector_block(ac, l1_A, 0.5, grid, use_gt=True)
    return out


# ------------------------------------------------------------------ aggregate
def agg(vals):
    v = [x for x in vals if x is not None and np.isfinite(x)]
    if not v:
        return dict(mean=float("nan"), sd=float("nan"), n=0)
    a = np.asarray(v, float)
    return dict(mean=float(a.mean()),
                sd=float(a.std(ddof=1)) if len(a) > 1 else 0.0,
                n=len(a), vals=[float(x) for x in a])


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(V3, "v2_textext_tables.json"))
    a = ap.parse_args(argv)
    grid = gridspec.load("gridspec_v1.json")
    print(f"[grid] {grid.summary()}")

    per_run = {}
    for r in RUNS:
        p = os.path.join(EV, r, "per_frame.csv")
        if not os.path.isfile(p):
            print(f"  [miss] {r}"); continue
        per_run[r] = run_tables(r, grid)
        c = per_run[r]["counts"]
        print(f"  [ok] {r}: A {c['n_A']} · haz {c['n_haz_A']} · paired-H {c['paired_H']} "
              f"{c['paired_H_by_scene']} · C/D GT+ {c['C_gt_positive_cells']}/"
              f"{c['D_gt_positive_cells']}")

    # 팔별 3시드 집계
    summary = {}
    for arm, runs in ARMS.items():
        rs = [per_run[r] for r in runs if r in per_run]
        if not rs:
            continue
        n_ops = len(rs[0]["ops"])
        rows = []
        for i in range(n_ops):
            o0 = rs[0]["ops"][i]
            e = dict(name=o0["name"], axis=o0["axis"], target=o0["target"],
                     tau=agg([r["ops"][i]["tau"] for r in rs]))
            for lbl, path in (("pooled", ("dash1", "pooled_pairedH")),
                              ("hidden", ("dash1", "hidden_H3_pairedH")),
                              ("allhaz", ("dash1", "all_haz"))):
                for m in ("frame_recall", "frame_recall_twin",
                          "cell_recall", "cell_recall_twin"):
                    e[f"{lbl}_{m}"] = agg([r["ops"][i][path[0]][path[1]][m] for r in rs])
            for m, path in (("FA_C_frame", ("FA_C", "frame_fa")),
                            ("FA_C_cell", ("FA_C", "cell_fpr")),
                            ("FA_D_frame", ("FA_D", "frame_fa")),
                            ("FA_D_cell", ("FA_D", "cell_fpr"))):
                e[m] = agg([r["ops"][i]["dash3"][path[0]][path[1]] for r in rs])
            e["FA_diff_frame"] = agg([r["ops"][i]["dash3"]["diff_frame"] for r in rs])
            e["FA_diff_cell"] = agg([r["ops"][i]["dash3"]["diff_cell"] for r in rs])
            for g in ("ncue", "hscenes", "lat"):
                for arm2 in ("FA_C", "FA_D"):
                    e[f"{g}_{arm2}_frame"] = agg(
                        [r["ops"][i]["dash3"]["group"][g][arm2]["frame_fa"] for r in rs])
                    e[f"{g}_{arm2}_cell"] = agg(
                        [r["ops"][i]["dash3"]["group"][g][arm2]["cell_fpr"] for r in rs])
            e["l1"] = {}
            for s in grid.sector_names:
                for w in ("fire_A", "fire_C", "fire_D"):
                    e["l1"][f"{w}_{s}_frame"] = agg(
                        [r["ops"][i]["l1"][w][s]["frame_rate"] for r in rs])
                    e["l1"][f"{w}_{s}_share"] = agg(
                        [r["ops"][i]["l1"][w][s]["cell_share"] for r in rs])
            rows.append(e)
        summary[arm] = dict(runs=[r["run"] for r in rs], ops=rows,
                            hidden_dp=dict(
                                delta_score_mean=agg([r["hidden_dp"]["pairedH"]["delta_score"]
                                                      .get("mean") for r in rs]),
                                delta_score_p50=agg([r["hidden_dp"]["pairedH"]["delta_score"]
                                                     .get("p50") for r in rs]),
                                delta_score_meanabs=agg([r["hidden_dp"]["pairedH"]["delta_score"]
                                                         .get("mean_abs") for r in rs]),
                                delta_frame_mean=agg([r["hidden_dp"]["pairedH"]["delta_frame"]
                                                      .get("mean") for r in rs]),
                                delta_frame_meanabs=agg([r["hidden_dp"]["pairedH"]["delta_frame"]
                                                         .get("mean_abs") for r in rs]),
                                frac_abs_le_05=agg([r["hidden_dp"]["pairedH"]["delta_score"]
                                                    .get("frac_abs_le_05") for r in rs]),
                            ),
                            pool_dp=dict(
                                delta_score_mean=agg([r["pool_dp"]["delta_score"].get("mean")
                                                      for r in rs]),
                                delta_score_p50=agg([r["pool_dp"]["delta_score"].get("p50")
                                                     for r in rs]),
                            ))

    doc = dict(doc="v2 zero-shot on test-ext — 계기판 ①/③ + L1 섹터 (ACCOUNTING §2-8)",
               grid=grid.as_dict(), frame_targets=FRAME_TARGETS, cell_targets=CELL_TARGETS,
               fa_reference_arm="D", pair="(A,C)",
               c_gt_authority="spec-constant all-negative (AC-INSTR-1 C3-2)",
               per_run=per_run, summary=summary)
    json.dump(doc, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"[out] {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
