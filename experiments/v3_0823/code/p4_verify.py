#!/usr/bin/env python3
"""
p4_verify.py — P-4 재현 검증 집계 (ACCOUNTING §2-7).

비교 대상 (전부 **교정 GT · test-core 816 · tau_op 0.5**):
  구식 선택 = 출하 best.pt          -> eval_v2corr/<run>/metrics.json (= rescore_tables 원장)
  신식 선택 = 재선택 에폭 ckpt      -> reselect/eval/<run>_ep<new>/metrics.json
  교차검산  = 재훈련 구에폭 ckpt    -> reselect/eval/<run>_ep<old>/metrics.json
              (출하와 같아야 한다 = 재훈련이 원 런을 재현했다는 증거, 게이트 G-P4-2)

합격 기준(§2-7): 델타가 **모델별 시드 sigma 이내**. sigma 는 산문이 아니라
  eval_v2corr/rescore_tables.json::by_model[model].corrected[metric].sigma 에서 직접 읽는다.
"""
from __future__ import annotations

import json
import os
import sys

R = "/home/vislab/Desktop/work_sy/Practice_NegObs"
V3 = f"{R}/experiments/v3_0823"
RESCORE = f"{V3}/eval_v2corr/rescore_tables.json"
RESEL = f"{V3}/logs/p4_reselect.json"
EVDIR = f"{V3}/reselect/eval"
OUT = f"{V3}/logs/p4_verify.json"

METRICS = ["cell_f1", "cell_recall", "cell_precision", "frame_det_rate",
           "frame_recall_V", "frame_recall_E", "frame_recall_H",
           "frame_fa_off", "cell_fpr_off"]
MODELS = {"rgb": ["rgb_s42", "rgb_s43", "rgb_s44"],
          "depth": ["depth_s42", "depth_s43", "depth_s44"],
          "b2": ["b2_s42", "b2_s43", "b2_s44"]}


def load_op(path):
    if not os.path.exists(path):
        return None
    return json.load(open(path))["point"]["op"]


# ---------------------------------------------------------------------------
# FA-정합 진단 (**판정 기준이 아니라 기전 진단** — 사전등록된 합격 기준은 tau_op 0.5 · sigma)
# 규칙은 weekend_0823/newmodels/fa_matched.py 와 **동일**:
#   tau = off팔 프레임최대확률의 정확분위수 / frame recall = 양성 칸 하나라도 p >= tau
# 이유: 프로젝트 자체 규약이 "모든 recall 주장은 FA-정합 병기가 법"(DZ:189 · ACCOUNTING §4.9-2)이다.
# 서로 FA가 4배 다른 두 체크포인트를 tau 고정점에서만 비교하면 그 규약을 어긴다.
# ---------------------------------------------------------------------------
import csv                                                            # noqa: E402
FA_TARGETS = [0.359, 0.20, 0.10, 0.05]


def _load_pf(path):
    import numpy as np
    rows = list(csv.DictReader(open(path)))
    cells = [k[2:] for k in rows[0] if k.startswith("p_")]
    return [dict(tier=r["tier"], toggle=r["toggle_state"],
                 p=np.array([float(r["p_" + c]) for c in cells]),
                 g=np.array([int(float(r["g_" + c])) for c in cells])) for r in rows]


def _tau_for_fa_exact(off_max, target):
    import numpy as np
    n = len(off_max)
    s = np.sort(off_max)[::-1]
    k = int(np.floor(target * n + 1e-9))
    if k >= n:
        return 0.0, 1.0
    tau = np.nextafter(s[k], np.inf)
    return float(tau), float((off_max >= tau).mean())


def fa_matched_curve(per_frame_csv):
    import numpy as np
    rows = _load_pf(per_frame_csv)
    off_max = np.array([r["p"].max() for r in rows if r["toggle"] == "off"])
    out = {}
    for t in FA_TARGETS:
        tau, fa = _tau_for_fa_exact(off_max, t)
        rec = {}
        for tier in ("V", "E", "H"):
            sel = [r for r in rows if r["tier"] == tier and r["g"].sum() > 0]
            if sel:
                mx = np.array([r["p"][r["g"] == 1].max() for r in sel])
                rec[tier] = float((mx >= tau).mean())
        rec["tau"] = tau
        rec["fa_actual"] = fa
        out[f"{t:g}"] = rec
    return out


def main():
    rt = json.load(open(RESCORE))
    rs = json.load(open(RESEL))
    sig = {m: {k: rt["by_model"][m]["corrected"][k]["sigma"] for k in METRICS} for m in MODELS}
    out = {"sigma": sig, "runs": {}, "models": {}, "gates": {}}

    per_run_new = {}
    for model, runs in MODELS.items():
        for run in runs:
            old_ep = rs["reselect"][run]["old"]["epoch"]
            new_ep = rs["reselect"][run]["primary"]["epoch"]
            shipped = {k: rt["runs"][run]["corrected"][k] for k in METRICS}
            rec = {"model": model, "epoch_old": old_ep, "epoch_new": new_ep,
                   "changed": old_ep != new_ep, "shipped": shipped}
            if old_ep == new_ep:
                rec["new"] = shipped
                rec["source_new"] = "동일 에폭 -> 출하 산출물 재사용 (eval_v2corr)"
                rec["delta"] = {k: 0.0 for k in METRICS}
            else:
                newm = load_op(f"{EVDIR}/{run}_ep{new_ep}/metrics.json")
                reprom = load_op(f"{EVDIR}/{run}_ep{old_ep}/metrics.json")
                rcp = f"{V3}/reselect/{run}_repro/REPRO_CHECK.json"
                rc0 = json.load(open(rcp)) if os.path.exists(rcp) else None
                if newm is None:
                    rec["new"] = None
                    rec["metrics_csv_repro"] = rc0
                    rec["source_new"] = (
                        "UNRECOVERABLE — 재훈련이 원 런을 재현하지 못함(비결정론). "
                        "해당 에폭의 가중치는 복구 불가 -> 검증 대상에서 제외"
                        if (rc0 and rc0.get("identical") is False)
                        else "MISSING — 재훈련/채점 미완")
                    rec["verdict"] = ("UNRECOVERABLE"
                                      if (rc0 and rc0.get("identical") is False) else "MISSING")
                    out["runs"][run] = rec
                    continue
                rec["new"] = {k: newm[k] for k in METRICS}
                rec["source_new"] = f"reselect/eval/{run}_ep{new_ep}"
                rec["delta"] = {k: rec["new"][k] - shipped[k] for k in METRICS}
                if reprom is not None:
                    rec["repro_old_epoch"] = {k: reprom[k] for k in METRICS}
                    rec["repro_max_abs_diff"] = max(abs(reprom[k] - shipped[k]) for k in METRICS)
                    rec["G_P4_2_pass"] = rec["repro_max_abs_diff"] < 1e-9
                rc = json.load(open(f"{V3}/reselect/{run}_repro/REPRO_CHECK.json")) \
                    if os.path.exists(f"{V3}/reselect/{run}_repro/REPRO_CHECK.json") else None
                rec["metrics_csv_repro"] = rc
            rec["over_sigma"] = {k: (abs(rec["delta"][k]) > sig[model][k]) for k in METRICS}
            rec["n_over_sigma"] = sum(rec["over_sigma"].values())
            rec["verdict"] = "PASS" if rec["n_over_sigma"] == 0 else "FAIL"
            rec["ratio"] = {k: (abs(rec["delta"][k]) / sig[model][k] if sig[model][k] > 0
                                else (0.0 if rec["delta"][k] == 0 else float("inf")))
                            for k in METRICS}
            out["runs"][run] = rec
            per_run_new[run] = rec["new"]

    for model, runs in MODELS.items():
        if any(per_run_new.get(r) is None for r in runs):
            out["models"][model] = {
                "verdict": "UNRECOVERABLE" if any(
                    out["runs"][r].get("verdict") == "UNRECOVERABLE" for r in runs)
                else "INCOMPLETE",
                "reason": {r: out["runs"][r].get("source_new") for r in runs
                           if per_run_new.get(r) is None}}
            continue
        oldmean = {k: sum(out["runs"][r]["shipped"][k] for r in runs) / 3 for k in METRICS}
        newmean = {k: sum(per_run_new[r][k] for r in runs) / 3 for k in METRICS}
        d = {k: newmean[k] - oldmean[k] for k in METRICS}
        ov = {k: abs(d[k]) > sig[model][k] for k in METRICS}
        out["models"][model] = {
            "old_mean": oldmean, "new_mean": newmean, "delta": d,
            "ratio": {k: (abs(d[k]) / sig[model][k] if sig[model][k] > 0
                          else (0.0 if d[k] == 0 else float("inf"))) for k in METRICS},
            "over_sigma": ov, "n_over_sigma": sum(ov.values()),
            "verdict": "PASS" if sum(ov.values()) == 0 else "FAIL"}

    out["gates"]["G_P4_2_retrain_reproduces_shipped"] = {
        r: out["runs"][r].get("G_P4_2_pass") for r in out["runs"]
        if out["runs"][r]["changed"]}

    # FA-정합 진단 (선택이 바뀐 런만)
    out["fa_matched"] = {}
    for run, rec in out["runs"].items():
        if not rec["changed"] or rec.get("new") is None:
            continue
        old_pf = f"{V3}/eval_v2corr/{run}/per_frame.csv"
        new_pf = f"{EVDIR}/{run}_ep{rec['epoch_new']}/per_frame.csv"
        if not (os.path.exists(old_pf) and os.path.exists(new_pf)):
            continue
        co, cn = fa_matched_curve(old_pf), fa_matched_curve(new_pf)
        out["fa_matched"][run] = {
            "old": co, "new": cn,
            "delta_H": {k: cn[k]["H"] - co[k]["H"] for k in co},
            "delta_V": {k: cn[k]["V"] - co[k]["V"] for k in co}}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, "w"), ensure_ascii=False, indent=1)

    print("### 런별 (교정 GT · test-core · tau_op 0.5)")
    hdr = f"{'run':10s} {'ep_old':>6s} {'ep_new':>6s} " + " ".join(f"{m[:11]:>12s}" for m in METRICS)
    print(hdr)
    for run, rec in out["runs"].items():
        if rec.get("new") is None:
            print(f"{run:10s} {rec['epoch_old']:>6d} {str(rec['epoch_new']):>6s}  <MISSING>")
            continue
        line = f"{run:10s} {rec['epoch_old']:>6d} {rec['epoch_new']:>6d} " + " ".join(
            f"{rec['delta'][k]:>+12.4f}" for k in METRICS)
        print(line + f"  -> {rec['verdict']} ({rec['n_over_sigma']} over)")
    print("\n### 델타/sigma 비")
    for run, rec in out["runs"].items():
        if rec.get("new") is None or not rec["changed"]:
            continue
        print(f"{run:10s} " + " ".join(f"{k}={rec['ratio'][k]:.2f}s" for k in METRICS))
    print("\n### 모델 평균 (3시드)")
    for m, v in out["models"].items():
        if "delta" not in v:
            print(f"{m:6s} {v['verdict']}  {v.get('reason', '')}"); continue
        print(f"{m:6s} " + " ".join(f"{v['delta'][k]:>+9.4f}" for k in METRICS)
              + f"  -> {v['verdict']}")
    print("\n### G-P4-2 (재훈련이 출하 체크포인트를 재현했는가)")
    for r, p in out["gates"]["G_P4_2_retrain_reproduces_shipped"].items():
        rec = out["runs"][r]
        print(f"  {r:10s} max|d|={rec.get('repro_max_abs_diff')} -> {p}  "
              f"metrics.csv identical={(rec.get('metrics_csv_repro') or {}).get('identical')}")
    print("\n### FA-정합 진단 (판정 기준 아님 — 기전 진단)")
    for run, fm in out.get("fa_matched", {}).items():
        print(f"  {run}: " + "  ".join(
            f"FA{k}: H {fm['old'][k]['H']:.3f}->{fm['new'][k]['H']:.3f}"
            f"({fm['delta_H'][k]:+.3f})" for k in fm["old"]))
    print(f"\n[write] {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
