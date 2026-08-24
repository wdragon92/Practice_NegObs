#!/usr/bin/env python3
"""v3a_select.py — v3-A 체크포인트 선택 집계 + **v2 재현 회귀 가드**.

두 부분으로 나뉜다. 둘은 **서로 다른 대상에 대한 서로 다른 판정선**이므로
(PREREG §3.3) 같은 표에 섞지 않는다.

  [A] 회귀 가드 — 선택 코드를 **v2 15런**에 겨누면 P4_SELECTION 이 등재한 P-4 판정
      (`logs/p4_reselect.json::reselect[run].primary.epoch`)을 **그대로 재현**하는가.
      재현 실패 = 선택 코드가 웨이브 중 변형됐다는 뜻이므로 v3 판정 전체가 무효다.
      v2 규약 그대로 쓴다: n_H = 6 · FA 모집단 `v2_all_val_cells` · 마스크 없음 ·
      게이트는 소급 가능한 대리 게이트 `VG-const-p` (확률 덤프가 없으므로).

  [B] v3-A 선택 — 각 런의 metrics.csv 에 기록된 선택식 성분으로 점수를 **재계산**하고
      (훈련 루프가 온라인으로 고른 에폭과 대조), 선택 에폭 · VG-const 판정 ·
      성분 · 벽시계를 인쇄한다. FA 모집단 `v3_D_arm_cells` · 마스크 적용 · 정본 VG-const
      (val 전 프레임 확률 spread) — 훈련 중 매 에폭 로깅된 실측값을 쓴다.

산출: experiments/v3_0823/logs/v3a_selection.json + stdout 표
"""
from __future__ import annotations

import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import selection_v3 as SV  # noqa: E402

R = "/home/vislab/Desktop/work_sy/Practice_NegObs"
V2RUNS = f"{R}/experiments/dayrun_0820/runs/v2"
NMRUNS = f"{R}/experiments/weekend_0823/newmodels/runs"
LEDGER = f"{R}/experiments/v3_0823/logs/p4_reselect.json"
V3RUNS = f"{R}/experiments/v3_0823/runs/v3a"
OUT = f"{R}/experiments/v3_0823/logs/v3a_selection.json"

V3_MAIN = ["rgb_s42", "rgb_s43", "rgb_s44"]
V3_ISOLATED = ["rgb_s42_aux"]


# ───────────────────────────────────────────── [A] v2 재현 회귀 가드
def guard_v2(n_h: int = 6) -> dict:
    led = json.load(open(LEDGER))["reselect"]
    rows, n_ok = [], 0
    for run, ref in led.items():
        d = f"{V2RUNS}/{run}" if os.path.isdir(f"{V2RUNS}/{run}") else f"{NMRUNS}/{run}"
        eps = []
        with open(f"{d}/metrics.csv") as f:
            for r in csv.DictReader(f):
                e = {k: (int(r[k]) if k == "epoch" else float(r[k]))
                     for k in ("epoch", "val_f1", "val_recall", "val_fpr", "val_h_recall")}
                e["h_hits"] = round(e["val_h_recall"] * n_h)
                gate = SV.vgconstp_pass(e["val_f1"], e["val_recall"], e["val_fpr"])
                s = SV.sel_score_v3(e["val_f1"], e["h_hits"], n_h, e["val_fpr"])
                e["_s"] = s if gate else float("-inf")
                eps.append(e)
        got = SV.select_epoch(eps, "_s")
        got_ep = got["epoch"] if got else None
        exp_ep = ref["primary"]["epoch"]
        exp_sc = ref["primary"]["score"]
        ok = (got_ep == exp_ep) and (got is not None and abs(got["_s"] - exp_sc) < 1e-9)
        n_ok += ok
        rows.append({"run": run, "expected_epoch": exp_ep, "got_epoch": got_ep,
                     "expected_score": exp_sc, "got_score": (got["_s"] if got else None),
                     "old_epoch": ref["old"]["epoch"], "match": ok})
    return {"n_runs": len(rows), "n_match": n_ok, "all_match": n_ok == len(rows),
            "n_h": n_h, "fa_population": SV.FA_POPULATION_DEFAULT_V2,
            "gate": "VG-const-p (소급 대리 게이트 — 에폭별 확률 덤프 부재)",
            "formula": SV.FORMULA_ID, "rows": rows}


# ───────────────────────────────────────────── [B] v3-A 선택
def select_v3(run: str) -> dict:
    d = f"{V3RUNS}/{run}"
    if not os.path.isfile(f"{d}/metrics.csv"):
        return {"run": run, "status": "MISSING"}
    cfg = json.load(open(f"{d}/config.json")) if os.path.isfile(f"{d}/config.json") else {}
    eps = []
    with open(f"{d}/metrics.csv") as f:
        for r in csv.DictReader(f):
            e = {"epoch": int(r["epoch"]),
                 "f1": float(r["sel_f1"]), "fa": float(r["sel_fa"]),
                 "h_hits": int(r["sel_h_hits"]), "n_H": int(r["sel_n_H"]),
                 "beta": float(r["sel_beta"]), "H_hat": float(r["sel_H_hat"]),
                 "spread": float(r["val_spread"]),
                 "vgconst_pass": bool(int(r["vgconst_pass"])),
                 "val_f1": float(r["val_f1"]), "val_fpr": float(r["val_fpr"]),
                 "val_h_recall": float(r["val_h_recall"]),
                 "frame_fa_d": float(r["val_frame_fa_d"]),
                 "sec": float(r["sec"]),
                 "logged_S": (None if r["sel_score"] == "-inf" else float(r["sel_score"]))}
            # 정본 재계산 (metrics.csv 의 성분 -> selection_v3 단일 진입점의 산식)
            s = SV.sel_score_v3(e["f1"], e["h_hits"], e["n_H"], e["fa"])
            gate = SV.vgconst_pass(e["spread"])
            e["recomputed_S"] = s
            e["_s"] = s if gate else float("-inf")
            e["gate_recomputed"] = gate
            eps.append(e)
    best = SV.select_epoch(eps, "_s")
    n_pass = sum(1 for e in eps if e["gate_recomputed"])
    # 온라인 선택(훈련 루프)과의 대조
    online_ep = (cfg.get("v3_registered", {}).get("selected") or {}).get("epoch")
    repro_err = max((abs(e["recomputed_S"] - e["logged_S"])
                     for e in eps if e["logged_S"] is not None), default=0.0)
    out = {"run": run,
           "status": ("TRAINING_FAILED" if os.path.isfile(f"{d}/TRAINING_FAILED")
                      else ("DONE" if os.path.isfile(f"{d}/DONE") else "RUNNING")),
           "n_epochs": len(eps), "stop_reason": cfg.get("stop_reason"),
           "wall_sec": cfg.get("wall_sec"), "steps": cfg.get("steps"),
           "epoch_sec_median": sorted(e["sec"] for e in eps)[len(eps) // 2] if eps else None,
           "vgconst": {"threshold": SV.VGCONST_SPREAD_MIN, "stage": SV.VGCONST_STAGE,
                       "n_pass": n_pass, "n_epochs": len(eps),
                       "verdict": "PASS" if n_pass else "REJECT->TRAINING_FAILED",
                       "spread_min": min((e["spread"] for e in eps), default=None),
                       "spread_max": max((e["spread"] for e in eps), default=None),
                       "spread_at_selected": best["spread"] if best else None},
           "selected": None if best is None else {
               "epoch": best["epoch"], "S": best["_s"],
               "components": {"f1": best["f1"], "H_hat": best["H_hat"], "fa": best["fa"],
                              "h_hits": best["h_hits"], "n_H": best["n_H"],
                              "beta": best["beta"],
                              "term_f1": (1 - best["beta"]) * best["f1"],
                              "term_H": best["beta"] * best["H_hat"],
                              "term_FA": -SV.LAMBDA_FA * best["fa"]},
               "val_unmasked": {"val_f1": best["val_f1"], "val_fpr": best["val_fpr"],
                                "val_h_recall": best["val_h_recall"],
                                "val_frame_fa_d": best["frame_fa_d"]}},
           "online_selected_epoch": online_ep,
           "online_matches_recompute": (best is not None and online_ep == best["epoch"]),
           "max_score_repro_err": repro_err,
           "vg1ep_flag": bool(best is not None and best["epoch"] <= 1),
           "n_val_H_effective": (cfg.get("v3_registered", {})
                                 .get("R3_selection", {}).get("n_val_H_effective")),
           "beta_effective": (cfg.get("v3_registered", {})
                              .get("R3_selection", {}).get("beta_effective")),
           "fa_population": (cfg.get("v3_registered", {})
                             .get("R3_selection", {}).get("selection_fa_population")),
           }
    return out


def main():
    g = guard_v2()
    print("=" * 84)
    print("[A] v2 재현 회귀 가드 — 선택 코드가 P-4 판정을 재현하는가")
    print(f"    n_H={g['n_h']} · FA 모집단 {g['fa_population']} · 게이트 {g['gate']}")
    print(f"    {g['formula']}")
    print("-" * 84)
    print(f"    {'run':24s} {'구식':>5s} {'P-4 기대':>9s} {'재현':>6s}  판정")
    for r in g["rows"]:
        print(f"    {r['run']:24s} {r['old_epoch']:5d} {r['expected_epoch']:9d} "
              f"{r['got_epoch']:6d}  {'OK' if r['match'] else '**MISMATCH**'}")
    print(f"    => {g['n_match']}/{g['n_runs']} 재현 "
          f"{'✅ PASS' if g['all_match'] else '❌ FAIL — v3 판정 무효'}")

    print("\n" + "=" * 84)
    print("[B] v3-A 선택 (FA 모집단 v3_D_arm_cells · 마스크 적용 · 정본 VG-const)")
    print("-" * 84)
    runs = {}
    for run in V3_MAIN + V3_ISOLATED:
        runs[run] = select_v3(run)
        r = runs[run]
        if r.get("status") == "MISSING":
            print(f"    {run:14s} (미산출)")
            continue
        sel = r["selected"]
        tag = " [격리]" if run in V3_ISOLATED else ""
        print(f"    {run:14s}{tag} status={r['status']} epochs={r['n_epochs']} "
              f"stop={r['stop_reason']} wall={(r['wall_sec'] or 0) / 60:.1f}min")
        if sel:
            c = sel["components"]
            print(f"       선택 ep {sel['epoch']}  S={sel['S']:.6f} = "
                  f"(1-β){c['f1']:.4f}→{c['term_f1']:.4f} + β·Ĥ {c['H_hat']:.4f}→"
                  f"{c['term_H']:.4f} − λ·FPR {c['fa']:.4f}→{c['term_FA']:.4f}")
            print(f"       β={c['beta']:.4f} (n_H={c['n_H']}, h={c['h_hits']}) · "
                  f"VG-const {r['vgconst']['verdict']} "
                  f"({r['vgconst']['n_pass']}/{r['vgconst']['n_epochs']} 에폭, "
                  f"선택 에폭 spread={r['vgconst']['spread_at_selected']:.4e} "
                  f"≥ {SV.VGCONST_SPREAD_MIN}) · VG-1ep {'⚠' if r['vg1ep_flag'] else 'n/a'}")
            print(f"       온라인 선택 재현 {'OK' if r['online_matches_recompute'] else '**MISMATCH**'}"
                  f" · 점수 재현 오차 max {r['max_score_repro_err']:.3e}")

    res = {"guard_v2_reproduction": g, "v3a": runs,
           "note": "PREREG §3.3 — [A]와 [B]는 서로 다른 판정선이다. 교차 인용은 §6-10 위반."}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(res, f, indent=2, ensure_ascii=False)
    print(f"\n원장 -> {OUT}")
    return 0 if g["all_match"] else 1


if __name__ == "__main__":
    sys.exit(main())
