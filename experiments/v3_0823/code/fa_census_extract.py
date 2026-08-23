#!/usr/bin/env python3
"""
CPU-2 / FA CENSUS  --  step 1: extract FA events from the 9 frozen recipe-v2 runs.

An FA event is the triple (checkpoint, frame, cell) with score >= tau_op and GT == 0.
Two strata are kept SEPARATE (never pooled) per ACCOUNTING.md 3.1 / 2-3:

  OFF     : off-arm frames.  GT is all-zero by construction, so every fired cell
            is an FA.  Denominator = 408 frames * 20 cells = 8160 cells.
  ON_NEG  : on-arm frames, cells whose GT == 0.  INCLUDES the 81 none_in_fov
            frames (all 20 cells GT-negative), which fall out of every published
            denominator -- ACCOUNTING.md 2-3 "denominator hole".
            Denominator = count of GT-negative cells over the 408 on-arm frames.

Outputs (all under experiments/v3_0823/):
  fa_events_raw.csv    one row per (model, seed, stratum, frame_id, cell)
  logs/fa_recount.json reconciliation of the recount vs each run's published
                       metrics.json (frame_fa_off / cell_fpr_off / cell_fpr_on_neg)

No GPU.  Reads only per_frame_on.csv / per_frame_off.csv, which already carry
per-cell scores (p_*) and per-cell GT (g_*) for all 20 cells.
"""
import csv
import json
import os
import sys

ROOT = "/home/vislab/Desktop/work_sy/Practice_NegObs"
RUNS = os.path.join(ROOT, "experiments/dayrun_0820/runs/v2")
OUT = os.path.join(ROOT, "experiments/v3_0823")
MANIFEST = os.path.join(ROOT, "experiments/dayrun_0820/dataset_manifest_v2_full.json")
GRIDSPEC = os.path.join(ROOT, "experiments/mainrun_0819/code/labeling/gridspec_v1.json")

MODELS = ["rgb", "depth", "b2"]
SEEDS = [42, 43, 44]

# Secondary / appendix architectures.  Same grid (PROVISIONAL-GRID-V1), same
# tau_op = 0.5, byte-identical per_frame.csv header -> free to census, no GPU.
NEW = os.path.join(ROOT, "experiments/weekend_0823/newmodels/runs")
APPENDIX = [("resnet50", s, os.path.join(NEW, f"resnet50_s{s}")) for s in SEEDS] + \
           [("convnext_tiny", s, os.path.join(NEW, f"tu-convnext_tiny_s{s}")) for s in SEEDS]


def load_grid():
    g = json.load(open(GRIDSPEC))
    # cell_index = band*5 + sector  (labeler.py:  grid["cell_index"])
    assert g["cell_index"] == "band*5+sector", g["cell_index"]
    cells = []
    for bi, b in enumerate(g["band_names"]):
        for si, s in enumerate(g["sector_names"]):
            cells.append(dict(idx=bi * g["n_sectors"] + si, cell=f"{s}{b}",
                              sector=s, band=b, band_i=bi, sector_i=si))
    assert len(cells) == 20
    return g, cells


def main():
    grid, cells = load_grid()
    cell_ids = [c["cell"] for c in cells]
    by_cell = {c["cell"]: c for c in cells}

    man = {f["frame_id"]: f for f in json.load(open(MANIFEST))["frames"]}

    appendix = "--appendix" in sys.argv
    todo = ([(m, s, os.path.join(RUNS, f"{m}_s{s}")) for m in MODELS for s in SEEDS]
            if not appendix else APPENDIX)

    events = []
    recon = {}

    if True:
        for model, seed, run_dir in todo:
            run = f"{model}_s{seed}"
            ev_dir = os.path.join(run_dir, "eval_test")
            mj = json.load(open(os.path.join(ev_dir, "metrics.json")))
            tau = float(mj["tau_op"])
            pub = mj["point"]["op"]

            n_off_frames = 0
            n_off_fired_frames = 0
            n_off_fired_cells = 0
            n_off_cells = 0
            n_on_neg_cells = 0
            n_on_neg_fired = 0
            n_on_frames = 0
            # sanity: off-arm GT must be all zero
            off_gt_nonzero = 0

            # the appendix runs ship only the combined per_frame.csv; split it on
            # toggle_state so both paths feed the identical counter below
            def arm_rows(arm):
                p = os.path.join(ev_dir, f"per_frame_{arm}.csv")
                if os.path.exists(p):
                    return list(csv.DictReader(open(p)))
                return [r for r in csv.DictReader(
                    open(os.path.join(ev_dir, "per_frame.csv")))
                    if r["toggle_state"] == arm]

            for arm in ("off", "on"):
                for r in arm_rows(arm):
                    fid = r["frame_id"]
                    tier = r["tier"]
                    scene = r["scene_id"]
                    mf = man[fid]
                    fired_any = False
                    for cid in cell_ids:
                        p = float(r["p_" + cid])
                        g = int(r["g_" + cid])
                        if arm == "off":
                            n_off_cells += 1
                            if g != 0:
                                off_gt_nonzero += 1
                            if p >= tau:
                                fired_any = True
                                n_off_fired_cells += 1
                        else:
                            if g == 0:
                                n_on_neg_cells += 1
                                if p >= tau:
                                    n_on_neg_fired += 1
                        is_fa = (p >= tau) and (g == 0)
                        if is_fa:
                            c = by_cell[cid]
                            events.append(dict(
                                model=model, seed=seed, run=run,
                                stratum="OFF" if arm == "off" else "ON_NEG",
                                frame_id=fid, scene_id=scene, tier=tier,
                                cell=cid, cell_idx=c["idx"],
                                sector=c["sector"], band=c["band"],
                                score=round(p, 6),
                                cam_pitch=mf["cam"]["pitch"], cam_yaw=mf["cam"]["yaw"],
                                cam_hfov=mf["cam"]["hfov"], cam_d=mf["cam"]["d"],
                                cell_int_px=mf["raw_vis"]["cell_int_px"][c["idx"]],
                            ))
                    if arm == "off":
                        n_off_frames += 1
                        if fired_any:
                            n_off_fired_frames += 1
                    else:
                        n_on_frames += 1

            rc = dict(
                tau_op=tau,
                n_off_frames=n_off_frames, n_on_frames=n_on_frames,
                off_gt_nonzero_cells=off_gt_nonzero,
                n_off_cells=n_off_cells,
                n_on_neg_cells=n_on_neg_cells,
                recount_frame_fa_off=n_off_fired_frames / n_off_frames,
                pub_frame_fa_off=pub["frame_fa_off"],
                recount_cell_fpr_off=n_off_fired_cells / n_off_cells,
                pub_cell_fpr_off=pub["cell_fpr_off"],
                recount_cell_fpr_on_neg=n_on_neg_fired / n_on_neg_cells,
                pub_cell_fpr_on_neg=pub["cell_fpr_on_neg"],
                n_off_fired_frames=n_off_fired_frames,
                n_off_fired_cells=n_off_fired_cells,
                n_on_neg_fired=n_on_neg_fired,
            )
            for k in ("frame_fa_off", "cell_fpr_off", "cell_fpr_on_neg"):
                rc["delta_" + k] = rc["recount_" + k] - rc["pub_" + k]
                rc["match_" + k] = abs(rc["delta_" + k]) < 1e-9
            recon[run] = rc
            print(f"{run:10s} tau={tau} "
                  f"frame_fa_off {rc['recount_frame_fa_off']:.6f} vs pub {rc['pub_frame_fa_off']:.6f} "
                  f"{'OK' if rc['match_frame_fa_off'] else 'MISMATCH'} | "
                  f"cell_fpr_off {rc['recount_cell_fpr_off']:.6f} vs {rc['pub_cell_fpr_off']:.6f} "
                  f"{'OK' if rc['match_cell_fpr_off'] else 'MISMATCH'} | "
                  f"on_neg {rc['recount_cell_fpr_on_neg']:.6f} vs {rc['pub_cell_fpr_on_neg']:.6f} "
                  f"{'OK' if rc['match_cell_fpr_on_neg'] else 'MISMATCH'} | "
                  f"events off={rc['n_off_fired_cells']} onneg={rc['n_on_neg_fired']}")

    os.makedirs(os.path.join(OUT, "logs"), exist_ok=True)
    tag = "_appendix" if appendix else ""
    fields = list(events[0].keys())
    with open(os.path.join(OUT, f"fa_events{tag}_raw.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(events)
    json.dump(recon, open(os.path.join(OUT, f"logs/fa_recount{tag}.json"), "w"), indent=2)
    print(f"\ntotal events {len(events)} -> {OUT}/fa_events{tag}_raw.csv")

    # denominator table (identical across runs -- assert it)
    d = {r["n_on_neg_cells"] for r in recon.values()}
    print("on-arm GT-negative cell denominators across runs:", d)


if __name__ == "__main__":
    sys.exit(main())
