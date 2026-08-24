#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verdict_core.py — test-core 헤드라인 표 (교정 GT · v2 | v3-A 공통 잣대 · CPU 전용)

무대 = `split_v2_full.json::test` (7씬) · 정답지 = **교정 GT(정본 B)** `dataset_manifest_v2corr.json`
— **양측 공히** (PREREG §1.1 · AC §2-1 · ab_table_shells R-2). test-core 는
**헤드라인 표와 FA-정합 전용**이며 계기판이 아니다 (AC §2-9 · PREREG §6-11).

계측기는 등록된 것을 그대로 쓴다 — `redteam/evl12_cell_axis.py` 의 `load_run` ·
`tau_for_rate` · `measure` 를 **import** 한다(복제 금지). 바뀌는 것은 런 목록뿐이다.

σ 는 **ddof=1** (PREREG §3.2). evl12 원본의 `range/2` 는 legacy 표기이므로 두 값을
같은 표에 넣지 않고 ddof=1 만 판정에 쓴다.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
V3 = os.path.join(REPO, "experiments", "v3_0823")
sys.path.insert(0, os.path.join(V3, "redteam"))
sys.path.insert(0, os.path.join(REPO, "experiments", "mainrun_0819", "code"))

import evl12_cell_axis as E12   # noqa: E402  — 등록된 test-core 계측기

FRAME_TARGETS = [0.359, 0.200, 0.100, 0.050]
CELL_TARGETS = [0.046732, 0.026035, 0.013017, 0.006509]   # PREREG §2.1 (MAP-C · 봉인)
V2_DIR = os.path.join(V3, "eval_v2corr")
V3_DIR = os.path.join(V3, "eval_v3a_core")
V2_RUNS = ["rgb_s42", "rgb_s43", "rgb_s44"]
V3_RUNS = ["rgb_s42", "rgb_s43", "rgb_s44"]
V3_AUX = ["rgb_s42_aux"]


def load(base, run):
    d = os.path.join(base, run)
    import csv
    rows = {}
    for tag in ("on", "off"):
        with open(os.path.join(d, f"per_frame_{tag}.csv")) as f:
            rows[tag] = list(csv.DictReader(f))
    cells = [c[2:] for c in rows["on"][0] if c.startswith("p_")]
    out = {}
    for tag in ("on", "off"):
        R = rows[tag]
        out[tag] = dict(
            frame_id=[r["frame_id"] for r in R],
            tier=np.array([r["tier"] for r in R]),
            prob=np.array([[float(r["p_" + c]) for c in cells] for r in R]),
            gt=np.array([[float(r["g_" + c]) for c in cells] for r in R]) > 0.5)
    out["cells"] = cells
    return out


def measure_full(run, tau):
    """E12.measure + 헤드라인 표가 요구하는 전 tier 열."""
    m = dict(E12.measure(run, tau))
    on, off = run["on"], run["off"]
    pon, gon = on["prob"] >= tau, on["gt"]
    poff = off["prob"] >= tau
    tp = int((pon & gon).sum()); fp = int((pon & ~gon).sum()); fn = int((~pon & gon).sum())
    fp += int(poff.sum())                      # off팔 발화는 전부 위양성
    m["cell_f1"] = (2 * tp / (2 * tp + fp + fn)) if (2 * tp + fp + fn) else float("nan")
    m["cell_precision"] = (tp / (tp + fp)) if (tp + fp) else float("nan")
    m["cell_recall"] = (tp / (tp + fn)) if (tp + fn) else float("nan")
    haz = gon.any(1)
    m["frame_det_rate"] = float((pon & gon).any(1)[haz].mean()) if haz.any() else float("nan")
    m["n_haz_frames"] = int(haz.sum())
    m["n_pos_cells"] = int(gon.sum())
    m["tau"] = float(tau)
    for t in ("V", "E", "H"):
        m[f"n_{t}"] = int((haz & (on["tier"] == t)).sum())
    return m


def agg(vals):
    v = np.asarray([x for x in vals if x is not None and np.isfinite(x)], float)
    if not len(v):
        return dict(mean=None, sd=None, n=0)
    return dict(mean=float(v.mean()), sd=(float(v.std(ddof=1)) if len(v) > 1 else 0.0),
                n=int(len(v)), vals=[float(x) for x in v])


def side(base, runs, label):
    R = {r: load(base, r) for r in runs}
    r0 = R[runs[0]]
    assert r0["off"]["gt"].sum() == 0, "off arm GT not all-zero"
    counts = dict(n_on=len(r0["on"]["frame_id"]), n_off=len(r0["off"]["frame_id"]),
                  n_cells=len(r0["cells"]),
                  n_haz=int(r0["on"]["gt"].any(1).sum()),
                  n_pos_cells=int(r0["on"]["gt"].sum()),
                  tier={k: int(v) for k, v in
                        zip(*[list(x) for x in np.unique(r0["on"]["tier"],
                                                         return_counts=True)])})
    ops = [dict(name="tau_op", axis="ref", target=None)]
    ops += [dict(name=f"F@{t:.3f}", axis="frame", target=t) for t in FRAME_TARGETS]
    ops += [dict(name=f"C@{t:.6f}", axis="cell", target=t) for t in CELL_TARGETS]
    rows = []
    for op in ops:
        per = {}
        for r in runs:
            run = R[r]
            if op["axis"] == "ref":
                tau = 0.5
            elif op["axis"] == "frame":
                tau = E12.tau_for_rate(run["off"]["prob"].max(1), op["target"])
            else:
                tau = E12.tau_for_rate(run["off"]["prob"], op["target"])
            per[r] = measure_full(run, tau)
        e = dict(op)
        keys = [k for k in per[runs[0]] if isinstance(per[runs[0]][k], (int, float))]
        for k in keys:
            e[k] = agg([per[r][k] for r in runs])
        # 시드 합산 추정량 (PREREG §2.1 P-08 — 추정량 명시 의무)
        fired = sum(int((R[r]["off"]["prob"] >= per[r]["tau"]).any(1).sum()) for r in runs)
        cells = sum(int((R[r]["off"]["prob"] >= per[r]["tau"]).sum()) for r in runs)
        e["cells_per_fa_frame_pooled"] = (cells / fired) if fired else None
        e["per_run"] = per
        rows.append(e)
    return dict(label=label, base=base, runs=runs, counts=counts, ops=rows)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(V3, "verdict_core.json"))
    a = ap.parse_args(argv)
    v2 = side(V2_DIR, V2_RUNS, "v2 (eval_v2corr · 재채점)")
    v3 = side(V3_DIR, V3_RUNS, "v3-A")
    aux = side(V3_DIR, V3_AUX, "v3-A aux [격리·진단]")
    print(f"[core] v2 counts {v2['counts']}")
    print(f"[core] v3 counts {v3['counts']}")
    doc = dict(doc="test-core 헤드라인 — 교정 GT(정본 B) 위 v2 | v3-A 공통 잣대",
               stage="split_v2_full.json::test · dataset_manifest_v2corr.json",
               instrument="redteam/evl12_cell_axis.py (load/tau_for_rate/measure) — import 재사용",
               sigma="ddof=1 (PREREG §3.2). evl12 원본의 range/2 는 legacy 표기 — 병용 금지.",
               frame_targets=FRAME_TARGETS, cell_targets=CELL_TARGETS,
               v2=v2, v3=v3, v3_aux_isolated=aux)
    json.dump(doc, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"[out] {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
