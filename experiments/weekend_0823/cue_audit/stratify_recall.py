#!/usr/bin/env python3
"""
CPU-1 / WEEKEND_BRIEF_0823 §6.1 task 2 — stratified re-aggregation of H recall.

Reads h_cue_table.csv (this dir) + the frozen v2 per-frame eval CSVs and re-aggregates
frame_recall_H over cue strata. No retraining, no re-inference, headline numbers untouched.

frame recall = any GT-positive cell has p >= tau_op (0.5)  -- identical to the definition
behind SEED_TABLE.md `frame_recall_H`; the reproduction check in main() asserts it.
"""
import csv, json, os, statistics, collections

ROOT = "/home/vislab/Desktop/work_sy/Practice_NegObs"
OUT = os.path.join(ROOT, "experiments/weekend_0823/cue_audit")
RUNS = os.path.join(ROOT, "experiments/dayrun_0820/runs/v2")
MODELS = ["rgb", "depth", "b2"]
SEEDS = [42, 43, 44]
TAU = 0.5
CELLS = ["A1", "B1", "C1", "D1", "E1", "A2", "B2", "C2", "D2", "E2",
         "A3a", "B3a", "C3a", "D3a", "E3a", "A3b", "B3b", "C3b", "D3b", "E3b"]
BAND = ["1"] * 5 + ["2"] * 5 + ["3a"] * 5 + ["3b"] * 5


def load_preds(model, seed):
    """frame_id -> (hit, hit_3b_only, n_pos, n_pos_fired)"""
    out = {}
    for fn in ("per_frame_on.csv", "per_frame_val.csv"):
        p = os.path.join(RUNS, "%s_s%d" % (model, seed), "eval_test", fn)
        for r in csv.DictReader(open(p)):
            if r["tier"] != "H":
                continue
            hit = 0
            hit3b = 0
            npos = 0
            nfire = 0
            for i, c in enumerate(CELLS):
                if r["g_" + c] == "1":
                    npos += 1
                    fired = float(r["p_" + c]) >= TAU
                    if fired:
                        nfire += 1
                        hit = 1
                        if BAND[i] == "3b":
                            hit3b = 1
            out[r["frame_id"]] = (hit, hit3b, npos, nfire)
    return out


def agg(frames, preds):
    """frame recall over a frame-id list."""
    if not frames:
        return None
    return sum(preds[f][0] for f in frames if f in preds) / \
        max(1, sum(1 for f in frames if f in preds))


def cellrec(frames, preds):
    npos = sum(preds[f][2] for f in frames if f in preds)
    nfire = sum(preds[f][3] for f in frames if f in preds)
    return nfire / npos if npos else None


def mr(vals):
    """mean +- range/2, matching SEED_TABLE convention."""
    vals = [v for v in vals if v is not None]
    if not vals:
        return None, None
    return sum(vals) / len(vals), (max(vals) - min(vals)) / 2.0


def fmt(m, r):
    return "n/a" if m is None else "%.3f ± %.3f" % (m, r)


def main():
    rows = list(csv.DictReader(open(os.path.join(OUT, "h_cue_table.csv"))))
    preds = {(m, s): load_preds(m, s) for m in MODELS for s in SEEDS}

    # -- reproduction check against the frozen headline -------------------------
    test = [r for r in rows if r["split"] == "test"]
    tf = [r["frame_id"] for r in test]
    print("== reproduction check (test H, n=%d) ==" % len(tf))
    for m in MODELS:
        vals = [agg(tf, preds[(m, s)]) for s in SEEDS]
        ref = []
        for s in SEEDS:
            j = json.load(open(os.path.join(RUNS, "%s_s%d" % (m, s),
                                            "eval_test", "metrics.json")))
            ref.append(j["point"]["op"]["frame_recall_H"])
        ok = all(abs(a - b) < 1e-9 for a, b in zip(vals, ref))
        print("  %-6s recomputed %s | metrics.json %s | MATCH=%s"
              % (m, [round(v, 4) for v in vals], [round(v, 4) for v in ref], ok))
        assert ok, "frame_recall_H reproduction failed for " + m

    report = []
    W = report.append

    def block(title, strata, note=""):
        W("\n### " + title)
        if note:
            W("\n" + note)
        W("")
        W("| stratum | n | " + " | ".join(
            "%s %s" % (m, x) for m in MODELS for x in ("mean±r/2", "per seed")) + " |")
        W("|---|---|" + "---|" * (2 * len(MODELS)))
        for name, frames in strata:
            cells = []
            for m in MODELS:
                vals = [agg(frames, preds[(m, s)]) for s in SEEDS]
                mm, rr = mr(vals)
                cells.append(fmt(mm, rr))
                cells.append("/".join("%.3f" % v if v is not None else "-" for v in vals))
            W("| %s | %d | %s |" % (name, len(frames), " | ".join(cells)))

    def ids(pred, pool=None):
        pool = pool if pool is not None else rows
        return [r["frame_id"] for r in pool if pred(r)]

    W("# H_RECALL_STRATIFIED — auto-generated numbers (do not hand-edit)")
    W("\nSource: `h_cue_table.csv` + `experiments/dayrun_0820/runs/v2/*/eval_test/per_frame_{on,val}.csv`.")
    W("τ_op = 0.5. `mean ± range/2` over seeds {42,43,44} — seed spread, **not** a CI.")

    block("1. HEADLINE — cued-H vs bare-H (test split, 7 test scenes, n=96)",
          [("cued-H (>=1 cue visible)", ids(lambda r: r["split"] == "test" and r["cls"] == "cued-H")),
           ("bare-H (0 cues visible)", ids(lambda r: r["split"] == "test" and r["cls"] == "bare-H")),
           ("all test H (= headline)", tf)])

    block("2. dose-response ladder (test)",
          [("cue_count=%d" % k, ids(lambda r, k=k: r["split"] == "test" and int(r["cue_count"]) == k))
           for k in sorted({int(r["cue_count"]) for r in test})])

    block("3. within-scene14 (the only test scene holding both strata)",
          [("scene14 cued-H", ids(lambda r: r["scene"] == "scene14" and r["cls"] == "cued-H")),
           ("scene14 bare-H", ids(lambda r: r["scene"] == "scene14" and r["cls"] == "bare-H")),
           ("scene15 (all cued)", ids(lambda r: r["scene"] == "scene15"))])

    block("4. guard-vocabulary cut (test) — railing_or_guard in frame or not",
          [("railing visible", ids(lambda r: r["split"] == "test" and r["cue_railing_or_guard"] == "1")),
           ("railing absent", ids(lambda r: r["split"] == "test" and r["cue_railing_or_guard"] == "0"))])

    block("5. cue family cuts (test)",
          [("direct-depth cue >=1", ids(lambda r: r["split"] == "test" and int(r["fam_direct_depth"]) > 0)),
           ("direct-depth cue 0", ids(lambda r: r["split"] == "test" and int(r["fam_direct_depth"]) == 0)),
           ("installed cue >=1", ids(lambda r: r["split"] == "test" and int(r["fam_installed"]) > 0)),
           ("installed cue 0", ids(lambda r: r["split"] == "test" and int(r["fam_installed"]) == 0))])

    block("6. viewpoint preset (test) — the confound A control",
          [(p, ids(lambda r, p=p: r["split"] == "test" and r["preset"] == p))
           for p in sorted({r["preset"] for r in test})])

    block("7. band-fixed subset (test, frames whose GT positives are 3b only)",
          [("3b-only cued-H", ids(lambda r: r["split"] == "test" and r["gt_bands"] == "3b" and r["cls"] == "cued-H")),
           ("3b-only bare-H", ids(lambda r: r["split"] == "test" and r["gt_bands"] == "3b" and r["cls"] == "bare-H")),
           ("3a+3b cued-H", ids(lambda r: r["split"] == "test" and r["gt_bands"] == "3a+3b"))])

    block("8. val reference (scene20, n=6 — below the n>=10 preregistered floor)",
          [("scene20 cued-H", ids(lambda r: r["scene"] == "scene20"))])

    # cell recall table for the headline strata
    W("\n### 9. cell recall on the same strata (test) — secondary metric")
    W("")
    W("| stratum | n frames | pos cells | " + " | ".join(MODELS) + " |")
    W("|---|---|---|" + "---|" * len(MODELS))
    for name, frames in [("cued-H", ids(lambda r: r["split"] == "test" and r["cls"] == "cued-H")),
                         ("bare-H", ids(lambda r: r["split"] == "test" and r["cls"] == "bare-H"))]:
        npos = sum(preds[("rgb", 42)][f][2] for f in frames)
        cells = []
        for m in MODELS:
            vals = [cellrec(frames, preds[(m, s)]) for s in SEEDS]
            mm, rr = mr(vals)
            cells.append(fmt(mm, rr))
        W("| %s | %d | %d | %s |" % (name, len(frames), npos, " | ".join(cells)))

    # ---- 10. the confound-controlled comparison: scene fixed AND band fixed ----
    block("10. scene14 with the GT band ALSO fixed (confound A + B controlled)",
          [("s14 3b-only cued-H", ids(lambda r: r["scene"] == "scene14" and r["gt_bands"] == "3b" and r["cls"] == "cued-H")),
           ("s14 3b-only bare-H", ids(lambda r: r["scene"] == "scene14" and r["gt_bands"] == "3b" and r["cls"] == "bare-H")),
           ("s14 3a+3b cued-H (near band also positive)",
            ids(lambda r: r["scene"] == "scene14" and r["gt_bands"] == "3a+3b"))],
          note="The bare-H stratum is 3b-only by construction, so this is the only "
               "comparison in which neither scene identity nor GT band differs between arms.")

    # ---- 11. paired seed-wise deltas (the preregistered sign test) ----
    W("\n### 11. paired seed-wise Δ = R_cued − R_bare (preregistered sign test)")
    W("")
    W("| comparison | model | Δ s42 | Δ s43 | Δ s44 | mean Δ | range/2 | signs agree? |")
    W("|---|---|---|---|---|---|---|---|")
    comps = [
        ("test cued vs bare (n 87/9)",
         ids(lambda r: r["split"] == "test" and r["cls"] == "cued-H"),
         ids(lambda r: r["split"] == "test" and r["cls"] == "bare-H")),
        ("scene14 cued vs bare (n 51/9)",
         ids(lambda r: r["scene"] == "scene14" and r["cls"] == "cued-H"),
         ids(lambda r: r["scene"] == "scene14" and r["cls"] == "bare-H")),
        ("scene14 3b-only cued vs bare (n 30/9)",
         ids(lambda r: r["scene"] == "scene14" and r["gt_bands"] == "3b" and r["cls"] == "cued-H"),
         ids(lambda r: r["scene"] == "scene14" and r["gt_bands"] == "3b" and r["cls"] == "bare-H")),
    ]
    for name, A, B in comps:
        for m in MODELS:
            d = [agg(A, preds[(m, s)]) - agg(B, preds[(m, s)]) for s in SEEDS]
            same = all(x > 0 for x in d) or all(x < 0 for x in d)
            W("| %s | %s | %+.3f | %+.3f | %+.3f | %+.3f | %.3f | %s |"
              % (name, m, d[0], d[1], d[2], sum(d) / 3.0,
                 (max(d) - min(d)) / 2.0, "YES" if same else "**NO**"))

    txt = "\n".join(report) + "\n"
    open(os.path.join(OUT, "H_RECALL_STRATIFIED.md"), "w").write(txt)
    print(txt)


if __name__ == "__main__":
    main()
