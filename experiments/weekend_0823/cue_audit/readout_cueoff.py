#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""readout_cueoff.py — the CUE-OFF paired read-out.

Reads the `per_frame.csv` dumps eval_polar.py wrote for every
(label set x round stem x arm x scene x model x seed) and produces:

  * H recall per arm  (frame recall on strict-H frames, tau_op = 0.5)
  * twin-conditional H recall, in the two twin definitions PREREG sec.4.1 fixes
        twin=C    the same cut's arm C (no hazard, ALL cues kept)   <- primary
        twin=off  the canonical hazard-off round                    <- secondary
  * the paired deltas  D(A,B1)  D(A,B2)  D(A,P)
  * B1 - B2 = the guard's standalone contribution (PREREG sec.4.4, H3)
  * arm C's false-alarm rate (H2)
  * THE PRE-REGISTERED DECISION RULE, printed WITH the numbers:
        cue evidence : (D_cue - D_placebo) >= 0.15  AND  3/3 seeds same sign
        shortcut     :  D_cue < 0.10               AND  3/3 seeds same sign
        otherwise    :  UNDECIDED -- table only

Everything is computed on PAIRED frames: a frame contributes only if it is
strict-H in BOTH arms of the pair (PREREG sec.4.2).  Frames that migrated H->E are
counted and reported, never silently dropped.

The rule is applied per scene and per label set.  Scene pooling is refused
(R2 P2, Simpson): scene14:scene15 = 60:36 already burned this project once.
"""
import argparse
import csv
import glob
import itertools
import json
import os
import re
import sys

REPO = "/home/vislab/Desktop/work_sy/Practice_NegObs"
AUDIT = os.path.join(REPO, "experiments/weekend_0823/cue_audit")

TAU = 0.5
THR_CUE = 0.15          # (D_cue - D_placebo) >= this  -> cue evidence
THR_SHORTCUT = 0.10     # D_cue < this                 -> shortcut
MIN_PAIRED_H = 10       # PREREG sec.4.5-3
MDE = 0.10              # PREREG sec.4.3, minimum detectable effect

# PREREG sec.4.3: which B arm is the PRIMARY D_cue for each scene, and whether the
# placebo contrast is admissible at all.
PRIMARY = {
    "scene12": dict(b="B2", placebo=True,
                    caveat="GT = the declared-degenerate 50-cell footprint in the "
                           "`lineage` set (PREREG amendment A1.1); placebo is 12-30x "
                           "the guard's pixel mass = conservative. D(A,B1) is "
                           "SECONDARY and anti-conservative."),
    "scene17": dict(b="B1", placebo=True,
                    caveat="primary placebo-corrected leg (A1.2-2). Footprint 65,833 "
                           "cells, no sidecar oracle, placebo ~18x the cue mass = "
                           "strongly conservative."),
    "scene20": dict(b="B2", placebo=False,
                    caveat="NO admissible placebo (PREREG sec.3.3): every piece of mesa "
                           "furniture measures 0 px in 6/6 H frames. Reported "
                           "EXPLORATORY; contributes via B2 surgery and arm-C FA."),
}


# --------------------------------------------------------------------------- io
def read_per_frame(path):
    """{frame_id: (tier, toggle, [p], [g])} for THIS ARM'S OWN frames only.

    `build_manifest.py` writes both rounds it was given, so a manifest built with
    `--off-round <arm C>` (the `twin` label set) also carries arm C's frames under
    `toggle_state == "off"`.  Those belong to a different arm and must never be
    pooled with the arm under test -- they would land in the false-alarm
    population of every arm at once.  The arm's own frames are the `on` ones;
    the rest are dropped here, at the only place that reads the CSV, so nothing
    downstream can re-introduce them.
    """
    out = {}
    with open(path) as f:
        rd = csv.DictReader(f)
        cells = [c[2:] for c in (rd.fieldnames or []) if c.startswith("p_")]
        for r in rd:
            if r["toggle_state"] != "on":
                continue
            out[r["frame_id"]] = (
                r["tier"], r["toggle_state"],
                [float(r["p_" + c]) for c in cells],
                [int(r["g_" + c]) for c in cells])
    return out


def max_on_gt(p, g):
    """Highest probability over the GT-POSITIVE cells (nan when GT is empty)."""
    v = [pi for pi, gi in zip(p, g) if gi]
    return max(v) if v else float("nan")


def max_any(p):
    return max(p) if p else float("nan")


def scan(root, sets):
    """{(set, stem, arm, scene, model, seed): per_frame dict}"""
    D = {}
    pat = os.path.join(root, "*", "*", "*", "*", "per_frame.csv")
    for p in sorted(glob.glob(pat)):
        rel = os.path.relpath(p, root).split(os.sep)
        if len(rel) != 5:
            continue
        st, stem_arm, scene, ms, _ = rel
        if st not in sets:
            continue
        m = re.match(r"^(.*)_(A|B1|B2|P|C)$", stem_arm)
        mm = re.match(r"^(.*)_s(\d+)$", ms)
        if not m or not mm:
            continue
        D[(st, m.group(1), m.group(2), scene, mm.group(1), int(mm.group(2)))] = \
            read_per_frame(p)
    return D


# --------------------------------------------------------------------------- stats
def paired_h(a, b):
    """frame ids that are strict-H in BOTH arms, plus the migration census."""
    both, mig = [], {}
    for fid, (ta, _, _, _) in a.items():
        rb = b.get(fid)
        if rb is None:
            continue
        tb = rb[0]
        if ta == "H" and tb == "H":
            both.append(fid)
        elif ta == "H" and tb != "H":
            mig[f"H->{tb}"] = mig.get(f"H->{tb}", 0) + 1
    return sorted(both), mig


def recall_H(d, fids):
    if not fids:
        return float("nan")
    hit = 0
    for fid in fids:
        _, _, p, g = d[fid]
        v = max_on_gt(p, g)
        if v == v and v >= TAU:
            hit += 1
    return hit / len(fids)


def recall_H_twin(d, twin, fids):
    """twin-contingent hit = [max_on_gt >= tau] AND [max_twin_gt < tau]  (R2 F2).

    `max_twin_gt` is read on the SAME GT cells of the same frame in the twin arm,
    so it asks "does this pose fire even when the hazard is gone".
    """
    if not fids or twin is None:
        return float("nan")
    hit = n = 0
    for fid in fids:
        rt = twin.get(fid)
        if rt is None:
            continue
        n += 1
        _, _, p, g = d[fid]
        _, _, pt, _ = rt
        v, vt = max_on_gt(p, g), max_on_gt(pt, g)
        if v == v and v >= TAU and not (vt == vt and vt >= TAU):
            hit += 1
    return hit / n if n else float("nan")


def fa_rate(d):
    """fraction of all-negative-GT frames where ANY cell fires (arm C = H2)."""
    n = hit = 0
    for fid, (_, _, p, g) in d.items():
        if any(g):
            continue
        n += 1
        if max_any(p) >= TAU:
            hit += 1
    return (hit / n if n else float("nan")), n


def same_sign(vals):
    v = [x for x in vals if x == x]
    if len(v) < 2:
        return False
    return all(x > 0 for x in v) or all(x < 0 for x in v) or all(x == 0 for x in v)


def verdict(d_cue, d_pla, n_seeds_needed=3):
    """The PRE-REGISTERED rule, verbatim.  Returns (label, explanation)."""
    dc = [x for x in d_cue if x == x]
    dp = [x for x in d_pla if x == x] if d_pla is not None else None
    if len(dc) < n_seeds_needed:
        return "UNDECIDED", f"only {len(dc)}/{n_seeds_needed} seeds available"
    mean_c = sum(dc) / len(dc)
    if not same_sign(dc):
        return "UNDECIDED", (f"seed signs disagree ({', '.join(f'{x:+.3f}' for x in dc)}) "
                             f"-- PREREG sec.4.5-4")
    if dp is None:
        if mean_c < THR_SHORTCUT:
            return "SHORTCUT", (f"D_cue {mean_c:+.3f} < {THR_SHORTCUT} and 3/3 same sign "
                                f"(no placebo available -- exploratory)")
        return "UNDECIDED", (f"D_cue {mean_c:+.3f} but no admissible placebo, so the "
                             f"cue-evidence branch cannot be evaluated")
    mean_p = sum(dp) / len(dp) if dp else float("nan")
    corr = mean_c - mean_p
    if corr >= THR_CUE and same_sign(dc):
        return "CUE EVIDENCE", (f"(D_cue {mean_c:+.3f}) - (D_placebo {mean_p:+.3f}) = "
                                f"{corr:+.3f} >= {THR_CUE} and 3/3 same sign")
    if mean_c < THR_SHORTCUT and same_sign(dc):
        return "SHORTCUT", (f"D_cue {mean_c:+.3f} < {THR_SHORTCUT} and 3/3 same sign "
                            f"(placebo-corrected {corr:+.3f})")
    return "UNDECIDED", (f"(D_cue {mean_c:+.3f}) - (D_placebo {mean_p:+.3f}) = {corr:+.3f}: "
                         f"between {THR_SHORTCUT} and {THR_CUE}")


# --------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--eval-root", default=os.path.join(AUDIT, "eval"))
    ap.add_argument("--sets", default="lineage,twin")
    ap.add_argument("--models", default="rgb,depth,b2")
    ap.add_argument("--out", default=os.path.join(AUDIT, "CUEOFF_RESULT.md"))
    a = ap.parse_args()
    sets = [s for s in a.sets.split(",") if s]
    models = [m for m in a.models.split(",") if m]
    D = scan(a.eval_root, sets)
    if not D:
        print(f"[readout] nothing under {a.eval_root} -- run eval_cueoff.sh phases 1,2 first")
        return 0
    keys = sorted({(k[0], k[1], k[3]) for k in D})
    seeds = sorted({k[5] for k in D})

    L = ["# CUEOFF_RESULT — CUE-OFF intervention read-out", "",
         "Pre-registration: `PREREG_CUEOFF.md` (+ amendment A1). "
         "Every threshold below was fixed before the first cut was rendered; "
         "this file only substitutes numbers into it.", "",
         f"tau_op **{TAU}** · seeds `{seeds}` · retraining **0** · "
         f"frozen `runs/v2/{{rgb,depth,b2}}_s{{42,43,44}}/best.pt`", "",
         "```",
         "PRE-REGISTERED DECISION RULE (D36 / R2 sec.5.3-3)",
         "  D_cue     = recall_H(A) - recall_H(B)",
         "  D_placebo = recall_H(A) - recall_H(P)",
         f"  CUE EVIDENCE : (D_cue - D_placebo) >= {THR_CUE}  AND  3/3 seeds same sign",
         f"  SHORTCUT     :  D_cue < {THR_SHORTCUT}          AND  3/3 seeds same sign",
         "  otherwise    :  UNDECIDED -- table only",
         f"  paired-H must be >= {MIN_PAIRED_H}; effects below {MDE} are not interpreted",
         "```", ""]

    for st, stem, scene in keys:
        prim = PRIMARY.get(scene, dict(b="B1", placebo=True, caveat=""))
        L += [f"## {scene} · stem `{stem}` · label set `{st}`", "",
              f"> **Primary D_cue = D(A, {prim['b']})** · placebo "
              f"{'ADMISSIBLE' if prim['placebo'] else '**NOT ADMISSIBLE**'}  ",
              f"> {prim['caveat']}", ""]
        armd = {}
        for arm in ("A", "B2", "B1", "P", "C"):
            for m, s in itertools.product(models, seeds):
                k = (st, stem, arm, scene, m, s)
                if k in D:
                    armd[(arm, m, s)] = D[k]
        if not any(k[0] == "A" for k in armd):
            L += ["_arm A absent -- nothing to compare._", ""]
            continue

        # ---- arm C false alarms (H2) ------------------------------------
        L += ["### arm C — false alarms on the cue vocabulary alone (H2)", "",
              "| model | " + " | ".join(f"s{s}" for s in seeds) + " | mean | n frames |",
              "|---|" + "---|" * (len(seeds) + 2)]
        for m in models:
            row, nn = [], 0
            for s in seeds:
                d = armd.get(("C", m, s))
                if d is None:
                    row.append(float("nan"))
                    continue
                f, nn = fa_rate(d)
                row.append(f)
            fin = [x for x in row if x == x]
            L.append(f"| {m} | " + " | ".join("—" if x != x else f"{x:.3f}" for x in row)
                     + f" | {'—' if not fin else f'{sum(fin)/len(fin):.3f}'} | {nn} |")
        L += ["", "_H2 accepted at FA >= 0.40 (PREREG sec.4.4); compare sceneC2 new-off "
              "FA .681._", ""]

        # ---- H recall + deltas ------------------------------------------
        for m in models:
            L += [f"### {m} — paired strict-H recall and deltas", ""]
            rows = []
            deltas = {}
            for arm in ("B2", "B1", "P"):
                if not any(k[0] == arm for k in armd):
                    continue
                dcue, dtwin_c, ra, rb, npair, migs = [], [], [], [], [], {}
                for s in seeds:
                    da, db = armd.get(("A", m, s)), armd.get((arm, m, s))
                    if da is None or db is None:
                        continue
                    fids, mig = paired_h(da, db)
                    for k, v in mig.items():
                        migs[k] = migs.get(k, 0) + v
                    npair.append(len(fids))
                    r_a, r_b = recall_H(da, fids), recall_H(db, fids)
                    ra.append(r_a)
                    rb.append(r_b)
                    dcue.append(r_a - r_b)
                    tc = armd.get(("C", m, s))
                    if tc is not None:
                        dtwin_c.append(recall_H_twin(da, tc, fids)
                                       - recall_H_twin(db, tc, fids))
                deltas[arm] = (dcue, dtwin_c)
                n = npair[0] if npair else 0
                flag = ""
                if n < MIN_PAIRED_H:
                    flag = f" **VOID (paired-H {n} < {MIN_PAIRED_H}, PREREG sec.4.5-3)**"
                rows.append(
                    f"| A vs {arm} | {n} | "
                    + " | ".join(f"{x:.3f}" for x in ra) + " | "
                    + " | ".join(f"{x:.3f}" for x in rb) + " | "
                    + " | ".join(f"{x:+.3f}" for x in dcue) + " | "
                    + (f"{sum(dcue)/len(dcue):+.3f}" if dcue else "—") + " | "
                    + ("yes" if same_sign(dcue) else "**no**") + " | "
                    + (f"{dict(migs)}" if migs else "none") + flag + " |")
            if rows:
                L += ["| pair | paired-H | " + " | ".join(f"R_A s{s}" for s in seeds)
                      + " | " + " | ".join(f"R_B s{s}" for s in seeds)
                      + " | " + " | ".join(f"D s{s}" for s in seeds)
                      + " | mean D | same sign | tier migration |",
                      "|---|---|" + "---|" * (3 * len(seeds) + 3)] + rows + [""]

            # ---- B1 - B2 = the guard's standalone contribution (H3) -------
            if "B1" in deltas and "B2" in deltas:
                g = [x - y for x, y in zip(deltas["B1"][0], deltas["B2"][0])]
                tot = deltas["B1"][0]
                share = (sum(deltas["B2"][0]) / sum(tot)) if sum(tot) else float("nan")
                L += [f"**H3 guard standalone** — D(A,B1) - D(A,B2) = "
                      + ", ".join(f"{x:+.3f}" for x in g)
                      + f" · guard share of the full cue effect = "
                      + ("—" if share != share else f"{100*share:.0f}%"), ""]

            # ---- THE RULE --------------------------------------------------
            b = prim["b"]
            if b in deltas:
                dp = deltas["P"][0] if (prim["placebo"] and "P" in deltas) else None
                lab, why = verdict(deltas[b][0], dp)
                L += [f"> ### VERDICT ({m}, primary D_cue = D(A,{b})"
                      + (", placebo-corrected" if dp is not None else ", NO placebo")
                      + f"): **{lab}**", f"> {why}", ""]
                if deltas[b][1]:
                    lab2, why2 = verdict(deltas[b][1],
                                         deltas["P"][1] if dp is not None else None)
                    L += [f"> twin-conditional (twin = arm C, R2 P3 primary metric): "
                          f"**{lab2}** — {why2}", ""]
                    if lab2 != lab:
                        L += ["> **The twin-conditional verdict DISAGREES with the raw "
                              "recall verdict. PREREG sec.4.4 says the twin-conditional "
                              "reading wins the body text and the raw one goes to the "
                              "appendix.**", ""]
            if "B1" in deltas and b != "B1":
                dp = deltas["P"][0] if (prim["placebo"] and "P" in deltas) else None
                lab, why = verdict(deltas["B1"][0], dp)
                L += [f"_secondary D_cue = D(A,B1): **{lab}** — {why}"
                      + ("  (placebo UNDER-matches B1's pixel mass ~3.2x -> "
                         "anti-conservative; not promoted to decisive, PREREG sec.3.1)"
                         if scene == "scene12" else "") + "_", ""]

    with open(a.out, "w") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))
    print(f"\n-> {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
