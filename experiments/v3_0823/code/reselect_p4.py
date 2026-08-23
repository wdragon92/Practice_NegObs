#!/usr/bin/env python3
"""
reselect_p4.py — P-4 재선택 드라이버 (CPU 전용).

하는 일
  0) 분모 원장 재검산  : 두 정의 x 두 매니페스트 x 4 split  (결함 ③ 실측)
  1) sigma 잣대 재검증 : eval_v2corr/rescore_tables.json 에서 직접 (산문 인용 금지)
  2) 게이트 VG-const 실측  : per_frame_val.csv(val 288) + per_frame_off.csv(test off 408)
  3) 재선택            : 각 런 metrics.csv 에 구식/신식 점수 적용 -> 에폭 argmax 비교
  4) 사전등록 민감도   : lam in {0.5,1,2} x a in {0.5,1}
  5) 교정 GT val 재계산: 출하 체크포인트의 val 지표를 교정 매니페스트로 다시 계산

산출: experiments/v3_0823/logs/p4_reselect.json  (+ stdout 요약)
"""
from __future__ import annotations

import csv
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import selection_v3 as SV  # noqa: E402

R = "/home/vislab/Desktop/work_sy/Practice_NegObs"
MAN_OLD = f"{R}/experiments/dayrun_0820/dataset_manifest_v2_full.json"
MAN_COR = f"{R}/experiments/v3_0823/dataset_manifest_v2corr.json"
SPLIT = f"{R}/experiments/dayrun_0820/split_v2_full.json"
V2RUNS = f"{R}/experiments/dayrun_0820/runs/v2"
NMRUNS = f"{R}/experiments/weekend_0823/newmodels/runs"
RESCORE = f"{R}/experiments/v3_0823/eval_v2corr/rescore_tables.json"
OUT = f"{R}/experiments/v3_0823/logs/p4_reselect.json"

CELLS = ["A1", "B1", "C1", "D1", "E1", "A2", "B2", "C2", "D2", "E2",
         "A3a", "B3a", "C3a", "D3a", "E3a", "A3b", "B3b", "C3b", "D3b", "E3b"]

# 재선택 대상: v2 본표 resnet34 6런 (rgb/depth x 3시드) + b2 3런(아티팩트 허용 시)
V2_MAIN = [f"{i}_s{s}" for i in ("rgb", "depth") for s in (42, 43, 44)]
V2_B2 = [f"b2_s{s}" for s in (42, 43, 44)]
CONTROLS = [f"{m}_s{s}" for m in ("resnet50", "tu-convnext_tiny") for s in (42, 43, 44)]

LAM_GRID = [0.5, 1.0, 2.0]
A_GRID = [0.5, 1.0]


def load_manifest(p):
    return json.load(open(p))["frames"]


# ---------------------------------------------------------------- 0) 분모 원장
def denom_ledger():
    sp = json.load(open(SPLIT))
    s2k = {s: k for k, v in sp.items() for s in v}
    out = {}
    for name, path in (("old", MAN_OLD), ("corrected", MAN_COR)):
        fr = load_manifest(path)
        per = {}
        for k in ("train", "val", "test", "hold"):
            recs = [r for r in fr if s2k.get(r["scene_id"]) == k]
            n_b = sum(1 for r in recs if SV.is_hazard_h(r))
            n_a = sum(1 for r in recs if SV._is_hazard_h_legacy_A(r))
            per[k] = {"n_frames": len(recs), "defB_canonical": n_b,
                      "defA_legacy": n_a, "divergence": n_b - n_a}
        per["corpus_total"] = {k: sum(per[s][k] for s in ("train", "val", "test", "hold"))
                               for k in ("n_frames", "defB_canonical", "defA_legacy",
                                         "divergence")}
        out[name] = per
    return out


# ---------------------------------------------------------------- 1) sigma 잣대
def sigma_yardstick():
    d = json.load(open(RESCORE))
    keep = ["cell_f1", "frame_det_rate", "frame_recall_V", "frame_recall_E",
            "frame_recall_H", "frame_fa_off", "cell_fpr_off", "cell_recall",
            "cell_precision", "frame_recall_H_weak"]
    out = {}
    for m, blk in d["by_model"].items():
        out[m] = {k: {"mean": blk["corrected"][k]["mean"],
                      "sigma": blk["corrected"][k]["sigma"],
                      "per_seed": blk["corrected"][k]["per_seed"]}
                  for k in keep if k in blk["corrected"]}
    return out


# ---------------------------------------------------------------- 2) VG-const 실측
def read_pf(path):
    rows = []
    with open(path) as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows


def spread_from_csv(path, arm_filter=None):
    if not os.path.exists(path):
        return None
    rows = read_pf(path)
    if arm_filter:
        rows = [r for r in rows if arm_filter(r)]
    if not rows:
        return None
    probs = [[float(r["p_" + c]) for c in CELLS] for r in rows]
    per_frame_max = [max(p) for p in probs]
    # 칸별 표준편차 평균 (FA_MATCHED 의 두번째 통계량 — 교차확인용)
    n = len(probs)
    cellstd = []
    for j in range(len(CELLS)):
        col = [p[j] for p in probs]
        mu = sum(col) / n
        cellstd.append(math.sqrt(sum((x - mu) ** 2 for x in col) / n))
    return {"n": n,
            "off_max_min": min(per_frame_max), "off_max_med": sorted(per_frame_max)[n // 2],
            "off_max_max": max(per_frame_max),
            "spread": SV.output_spread(probs),
            "cell_std_mean": sum(cellstd) / len(cellstd)}


def gate_measurements():
    out = {}
    for run in V2_MAIN + V2_B2 + CONTROLS:
        base = f"{V2RUNS}/{run}/eval_test" if os.path.isdir(f"{V2RUNS}/{run}") \
            else f"{NMRUNS}/{run}/eval_test"
        rec = {}
        # (a) 정본 게이트 무대 = val 전 프레임 (selection_v3.VGCONST_STAGE)
        rec["val_all"] = spread_from_csv(f"{base}/per_frame_val.csv")
        # (b) 반례 기록용 = val 의 위험-없는 팔만 (퇴화 무대 — depth_s43 실측이 근거)
        rec["val_off"] = spread_from_csv(f"{base}/per_frame_val.csv",
                                         lambda r: r["toggle_state"] == "off")
        # (b) 대장이 기록한 무대 = test off팔 (FA_MATCHED 재검증)
        pf_off = f"{base}/per_frame_off.csv"
        if os.path.exists(pf_off):
            rec["test_off"] = spread_from_csv(pf_off)
        else:
            rec["test_off"] = spread_from_csv(f"{base}/per_frame.csv",
                                              lambda r: r["toggle_state"] == "off")
        for k in ("val_off", "val_all", "test_off"):
            if rec[k]:
                rec[k]["vgconst_pass"] = SV.vgconst_pass(rec[k]["spread"])
        out[run] = rec
    return out


# ---------------------------------------------------------------- 3) 재선택
def reselect(run, n_h):
    d = f"{V2RUNS}/{run}" if os.path.isdir(f"{V2RUNS}/{run}") else f"{NMRUNS}/{run}"
    cfg = json.load(open(f"{d}/config.json"))
    rows = []
    with open(f"{d}/metrics.csv") as f:
        for r in csv.DictReader(f):
            e = {k: (int(r[k]) if k == "epoch" else float(r[k]))
                 for k in ("epoch", "val_f1", "val_recall", "val_fpr",
                           "val_h_recall", "sel_score")}
            # h(적중 H 프레임 수) 복원 — 정수여야 한다(검산)
            hf = e["val_h_recall"] * n_h
            e["h_hits"] = round(hf)
            e["h_int_err"] = abs(hf - e["h_hits"])
            e["sel_old"] = SV.sel_score_v2(e["val_f1"], e["val_h_recall"])[0]
            e["sel_old_logged_err"] = abs(e["sel_old"] - e["sel_score"])
            e["vgconstp"] = SV.vgconstp_pass(e["val_f1"], e["val_recall"], e["val_fpr"])
            rows.append(e)
    res = {"run": run, "n_epochs": len(rows), "n_val_strict_h_cfg": cfg.get("n_val_strict_h"),
           "best_epoch_cfg": cfg.get("best_epoch"),
           "best_sel_cfg": cfg.get("best_sel_score"),
           "max_h_int_err": max(r["h_int_err"] for r in rows),
           "max_sel_old_repro_err": max(r["sel_old_logged_err"] for r in rows)}
    old = SV.select_epoch(rows, "sel_old")
    res["old"] = {"epoch": old["epoch"], "score": old["sel_old"],
                  "val_f1": old["val_f1"], "val_h_recall": old["val_h_recall"],
                  "val_fpr": old["val_fpr"]}
    res["old_matches_cfg"] = (old["epoch"] == cfg.get("best_epoch"))
    res["grid"] = {}
    for lam in LAM_GRID:
        for a in A_GRID:
            for r in rows:
                base = SV.sel_score_v3(r["val_f1"], r["h_hits"], n_h, r["val_fpr"],
                                       lam=lam, a=a)
                r["_s"] = base if r["vgconstp"] else float("-inf")
            new = SV.select_epoch(rows, "_s")
            res["grid"][f"lam{lam:g}_a{a:g}"] = {
                "epoch": new["epoch"] if new else None,
                "score": new["_s"] if new else None,
                "val_f1": new["val_f1"] if new else None,
                "val_h_recall": new["val_h_recall"] if new else None,
                "val_fpr": new["val_fpr"] if new else None,
                "same_as_old": (new["epoch"] == old["epoch"]) if new else False,
                "is_last_epoch": (new["epoch"] == rows[-1]["epoch"]) if new else False,
            }
    res["primary"] = res["grid"][f"lam{SV.LAMBDA_FA:g}_a{SV.LAPLACE_A:g}"]
    res["epochs"] = [{k: r[k] for k in ("epoch", "val_f1", "val_recall", "val_fpr",
                                        "val_h_recall", "h_hits", "sel_old", "vgconstp")}
                     for r in rows]
    return res


# ---------------------------------------------------------- 5) 교정 GT val 재계산
def val_under_corrected(run, n_h_cor):
    d = f"{V2RUNS}/{run}" if os.path.isdir(f"{V2RUNS}/{run}") else f"{NMRUNS}/{run}"
    p = f"{d}/eval_test/per_frame_val.csv"
    if not os.path.exists(p):
        return None
    cor = {r["frame_id"]: r for r in load_manifest(MAN_COR)}
    rows = read_pf(p)
    tp = fp = fn = tn = 0
    hsel, hdet = 0, 0
    tp_o = fp_o = fn_o = tn_o = 0
    for r in rows:
        rec = cor.get(r["frame_id"])
        if rec is None:
            return {"error": f"frame_id 미매칭: {r['frame_id']}"}
        g = [int(v) for v in rec["polar_gt"]]
        g_old = [int(r["g_" + c]) for c in CELLS]
        p_ = [float(r["p_" + c]) for c in CELLS]
        pred = [x >= 0.5 for x in p_]
        for j in range(20):
            if pred[j] and g[j]:
                tp += 1
            elif pred[j] and not g[j]:
                fp += 1
            elif (not pred[j]) and g[j]:
                fn += 1
            else:
                tn += 1
            if pred[j] and g_old[j]:
                tp_o += 1
            elif pred[j] and not g_old[j]:
                fp_o += 1
            elif (not pred[j]) and g_old[j]:
                fn_o += 1
            else:
                tn_o += 1
        if SV.is_hazard_h(rec):
            hsel += 1
            if any(pred[j] and g[j] for j in range(20)):
                hdet += 1
    f1 = 2 * tp / max(2 * tp + fp + fn, 1e-9)
    fpr = fp / max(fp + tn, 1e-9)
    f1o = 2 * tp_o / max(2 * tp_o + fp_o + fn_o, 1e-9)
    fpro = fp_o / max(fp_o + tn_o, 1e-9)
    return {"n_val": len(rows), "n_H_corrected": hsel, "h_hits_corrected": hdet,
            "val_f1_corrected": f1, "val_fpr_corrected": fpr,
            "val_f1_oldGT_recomputed": f1o, "val_fpr_oldGT_recomputed": fpro,
            "sel_new_corrected": SV.sel_score_v3(f1, hdet, hsel, fpr),
            "sel_new_oldGT": SV.sel_score_v3(f1o, hdet, n_h_cor, fpro),
            "sel_old_corrected": SV.sel_score_v2(f1, hdet / max(hsel, 1))[0]}


def main():
    out = {"formula": SV.FORMULA_ID, "h_def": SV.H_DEF_ID,
           "vgconst_threshold": SV.VGCONST_SPREAD_MIN, "vgconst_source": SV.VGCONST_SOURCE,
           "lam": SV.LAMBDA_FA, "a": SV.LAPLACE_A, "n0": SV.N0_HALF_TRUST}
    out["denominator_ledger"] = denom_ledger()
    n_h_val = out["denominator_ledger"]["corrected"]["val"]["defB_canonical"]
    out["n_val_H_canonical"] = n_h_val
    out["sigma"] = sigma_yardstick()
    out["gate"] = gate_measurements()
    out["reselect"] = {}
    for run in V2_MAIN + V2_B2 + CONTROLS:
        out["reselect"][run] = reselect(run, n_h_val)
    out["val_corrected"] = {r: val_under_corrected(r, n_h_val)
                            for r in V2_MAIN + V2_B2}
    # 무결성 게이트 G-P4-1: per_frame_val.csv(=출하 best.pt 의 val 덤프) 가
    # metrics.csv 의 선택 에폭 행과 같은 수치를 내야 한다 -> 재선택 입력의 신뢰성 담보
    gp = {}
    for run in V2_MAIN + V2_B2:
        d = f"{V2RUNS}/{run}"
        ep = out["reselect"][run]["best_epoch_cfg"]
        row = [r for r in csv.DictReader(open(f"{d}/metrics.csv")) if int(r["epoch"]) == ep][0]
        v = out["val_corrected"][run]
        gp[run] = {"epoch": ep,
                   "d_f1": abs(float(row["val_f1"]) - v["val_f1_oldGT_recomputed"]),
                   "d_fpr": abs(float(row["val_fpr"]) - v["val_fpr_oldGT_recomputed"])}
        gp[run]["pass"] = gp[run]["d_f1"] < 1e-4 and gp[run]["d_fpr"] < 1e-4
    out["gate_GP41"] = gp

    # ---- 6) "전부 발화"가 이길 수 있는가 (§2.4 표의 원장) --------------------
    #   전부발화: 전 칸 예측 양성 -> recall=1, fpr=1, F1 = 2p/(1+p) (p = val 양성 칸 비율)
    sp = json.load(open(SPLIT))
    fire = {}
    for nm, path in (("old_gt", MAN_OLD), ("corrected_gt", MAN_COR)):
        fr = [r for r in load_manifest(path) if r["scene_id"] in sp["val"]]
        pos = sum(sum(int(v) for v in r["polar_gt"]) for r in fr)
        p = pos / (20 * len(fr))
        f1f = 2 * p / (1 + p)
        fire[nm] = {"val_pos_cell_rate": p, "allfire_f1": f1f,
                    "S_old_allfire": SV.sel_score_v2(f1f, 1.0)[0],
                    "S_new_allfire_nH6": SV.sel_score_v3(f1f, 6, 6, 1.0),
                    "S_new_allfire_nH30": SV.sel_score_v3(f1f, 30, 30, 1.0),
                    "S_new_allsilent": SV.sel_score_v3(0.0, 0, n_h_val, 0.0)}
    so_ref = fire["old_gt"]["S_old_allfire"]
    sn_ref = fire["old_gt"]["S_new_allfire_nH6"]
    beaten = {"per_run": {}, "total_epochs": 0, "old_beaten": 0, "new_beaten": 0}
    for run, d in out["reselect"].items():
        eps = d["epochs"]
        ro = sum(1 for e in eps if SV.sel_score_v2(e["val_f1"], e["val_h_recall"])[0] < so_ref)
        rn = sum(1 for e in eps
                 if SV.sel_score_v3(e["val_f1"], e["h_hits"], n_h_val, e["val_fpr"]) < sn_ref)
        beaten["per_run"][run] = {"n_epochs": len(eps), "old_beaten": ro, "new_beaten": rn}
        beaten["total_epochs"] += len(eps)
        beaten["old_beaten"] += ro
        beaten["new_beaten"] += rn
    out["allfire"] = {"reference": fire, "epochs_beaten_by_allfire": beaten}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, "w"), ensure_ascii=False, indent=1)

    # ---- stdout 요약
    dl = out["denominator_ledger"]
    print("### 0. 분모 원장 (결함 ③)")
    for man in ("old", "corrected"):
        print(f"  {man:9s} " + " ".join(
            f"{k}: B={dl[man][k]['defB_canonical']}/A={dl[man][k]['defA_legacy']}"
            f"(d{dl[man][k]['divergence']:+d})" for k in ("train", "val", "test", "hold")))
    print(f"  -> 정본 val H 분모 n_H = {n_h_val}")
    print("\n### 2. VG-const 게이트 실측 (spread; 정본무대=val_all, 임계 %.g)" % SV.VGCONST_SPREAD_MIN)
    print(f"  {'run':22s} {'val_all*':>10s} {'val_off':>10s} {'test_off':>10s}  {'VGc':>6s}")
    for run, g in out["gate"].items():
        f = lambda k: (f"{g[k]['spread']:.3e}" if g[k] else "n/a")
        pv = (g["val_all"]["vgconst_pass"] if g["val_all"] else None)
        print(f"  {run:22s} {f('val_all'):>10s} {f('val_off'):>10s} {f('test_off'):>10s}  {str(pv):>6s}")
    print("\n### 3. 재선택 (primary lam=1 a=1)")
    print(f"  {'run':22s} {'ep_old':>6s} {'ep_new':>6s} {'same':>5s} {'cfg_ok':>6s} "
          f"{'h_int_err':>10s} {'oldrepro_err':>12s}")
    for run, r in out["reselect"].items():
        pr = r["primary"]
        print(f"  {run:22s} {r['old']['epoch']:>6d} {str(pr['epoch']):>6s} "
              f"{str(pr['same_as_old']):>5s} {str(r['old_matches_cfg']):>6s} "
              f"{r['max_h_int_err']:>10.2e} {r['max_sel_old_repro_err']:>12.2e}")
    print("\n### 4. 사전등록 민감도 (선택 에폭)")
    keys = [f"lam{l:g}_a{a:g}" for l in LAM_GRID for a in A_GRID]
    print(f"  {'run':22s} {'old':>4s} " + " ".join(f"{k:>12s}" for k in keys))
    for run, r in out["reselect"].items():
        print(f"  {run:22s} {r['old']['epoch']:>4d} "
              + " ".join(f"{str(r['grid'][k]['epoch']):>12s}" for k in keys))
    print("\n### 5. 교정 GT val 재계산 (출하 체크포인트)")
    print(f"  {'run':12s} {'nH_cor':>6s} {'h_hits':>6s} {'f1_cor':>8s} {'fpr_cor':>8s} "
          f"{'f1_oldGT':>9s} {'fpr_oldGT':>9s}")
    for run, v in out["val_corrected"].items():
        if not v or "error" in v:
            print(f"  {run:12s} {v}")
            continue
        print(f"  {run:12s} {v['n_H_corrected']:>6d} {v['h_hits_corrected']:>6d} "
              f"{v['val_f1_corrected']:>8.4f} {v['val_fpr_corrected']:>8.4f} "
              f"{v['val_f1_oldGT_recomputed']:>9.4f} {v['val_fpr_oldGT_recomputed']:>9.4f}")
    fb = out["allfire"]["epochs_beaten_by_allfire"]
    fr_ = out["allfire"]["reference"]["old_gt"]
    print(f"\n### 6. '전부 발화'가 이기는 에폭 (val 양성칸비율 {fr_['val_pos_cell_rate']:.4f})")
    print(f"  all-fire 점수: 구식 {fr_['S_old_allfire']:.4f} | 신식(n_H=6) "
          f"{fr_['S_new_allfire_nH6']:.4f} | 신식(n_H=30) {fr_['S_new_allfire_nH30']:.4f} "
          f"| 신식 전무발화 {fr_['S_new_allsilent']:.4f}")
    print(f"  총 {fb['total_epochs']}에폭 중 -> 구식 {fb['old_beaten']} "
          f"({fb['old_beaten'] / fb['total_epochs']:.1%}) · 신식 {fb['new_beaten']} "
          f"({fb['new_beaten'] / fb['total_epochs']:.1%})")

    ok = all(v["pass"] for v in out["gate_GP41"].values())
    print(f"\n### G-P4-1 무결성 (per_frame_val.csv <-> metrics.csv 선택에폭 행): "
          f"{sum(v['pass'] for v in out['gate_GP41'].values())}/{len(out['gate_GP41'])} "
          f"통과 -> {'PASS' if ok else 'FAIL'}")
    print(f"\n[write] {OUT}")


if __name__ == "__main__":
    main()
