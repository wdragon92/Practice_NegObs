#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""readout_cueoff.py — the CUE-OFF paired read-out (A2 instrument, v2).

v1 of this file produced `CUEOFF_RESULT.md`.  That file is preserved.  This
version implements PREREG amendment **A2** (D49), which is a POST-HOC correction
of the instrument, not of the hypotheses: every threshold, every primary-leg
choice and every arm assignment from `PREREG_CUEOFF.md` + A1 is unchanged.  What
changed is how the code counts.

A2-1  same_sign((0,0,0)) is no longer True.
      v1 folded "the metric did not move at all" into "3/3 seeds agree on a
      direction".  Zero is not a direction.  A2 defines
          SAME-SIGN  : >= 1 non-zero delta AND all non-zero deltas share a sign
          NO-EFFECT  : every delta is exactly 0
      and gives NO-EFFECT its own verdict label, printed with the one-sided 95%
      upper bound on a per-frame flip probability given 0 flips in n paired
      frames,  p95 = 1 - 0.05**(1/n).  Seeds do not enlarge n: the three seeds
      look at the SAME n frames, so pooling them would be a fake sample.

A2-2  paired-H < 10 VOIDS the verdict, not only the table row.
      v1 stamped `VOID` on the table row and then printed a verdict underneath
      it (R5 D-1: 12 verdict blocks, 4 of them positive SHORTCUT calls, on a
      scene the pre-registration had already disqualified).

A2-3  the lineage-off false-alarm FLOOR is published next to arm C's FA.
      It was already inside every `per_frame.csv` as the `toggle_state == off`
      rows and never printed.  Without it "FA = 1.000" is unauditable; with it
      the scene12 contrast reads .028 -> 1.000.  In the `twin` label set the
      off rows ARE arm C, so the floor is constitutively equal to the FA and is
      suppressed instead of printed as if it meant something.

A2-4  PRIMARY is keyed by (scene, round stem), not by scene.
      The two scene12 bands are different rounds with different masses; v1
      hard-coded one band's numbers into both captions (R5 D-5).

A2-5  placebo admissibility is quoted from RENDERED pixel mass
      (`RENDER_MASS_SUMMARY.csv`, threshold >=32/255 on the judged frames),
      not from the AABB silhouette upper bounds of `pixel_mass.py`.  All four
      of the pre-registration's admissibility grades were wrong, three of them
      in the anti-conservative direction (R4 F1).

A2-6  scene20's placebo is ADMISSIBLE.  PREREG sec.3.3 excluded it on the
      finding that scene20's mesa furniture measures 0 px -- which is TRUE and
      still true (verified corner-by-corner: every piece sits at x <= -5.4 with
      the two judged eyes at x = -5.10 / -6.72 looking down +X, so it is behind
      or beside the camera).  But the arm that was actually rendered does not
      remove furniture: `scene20_diagonal_oblique.py` under `placebo_remove`
      removes backdrop blocks E1/E2, which sec.3.3's own table measures at
      240 k px.  The rendered removal is 157,834 px >=32/255 on the 6 judged
      frames = 0.909x arm B2's rendered mass, the best-matched cue/placebo pair
      in the study.  This is declared post-hoc and flagged in every verdict it
      touches.

A2-7  byte-identical label-set blocks are folded, with the reason stated.

Everything is still computed on PAIRED frames (strict-H in BOTH arms), still
per scene and per label set, and scene pooling is still refused (R2 P2).
"""
import argparse
import csv
import glob
import itertools
import json
import math
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

# PREREG sec.4.3 primary-leg lock, keyed by (scene, round stem) -- A2-4.
# `placebo` is the ADMISSIBILITY of the placebo correction for that leg.
PRIMARY = {
    ("scene12", "260823_cueoff"): dict(
        b="B2", placebo=True,
        caveat="GT = the declared-degenerate 50-cell footprint in the `lineage` "
               "set (PREREG A1.1; G7 puts the same frames at 50,278 cells in the "
               "`twin` set, 1006x). Band `boost_e`."),
    ("scene12", "260823_cueoff2"): dict(
        b="B2", placebo=True,
        caveat="GT = the declared-degenerate 50-cell footprint in the `lineage` "
               "set (PREREG A1.1). Band `boost_e2` -- a DIFFERENT round from "
               "`260823_cueoff`, with its own masses; v1 printed boost_e's "
               "constants here (R5 D-5)."),
    ("scene17", "260823_cueoff"): dict(
        b="B1", placebo=True,
        caveat="A1.2-2 primary placebo-corrected leg. Footprint 65,833 cells, no "
               "sidecar oracle. B2 does not exist (no railing in this scene)."),
    ("scene20", "260823_cueoff"): dict(
        b="B2", placebo=True,
        caveat="A2-6: placebo RESTORED (post-hoc). PREREG sec.3.3 excluded it on a "
               "furniture measurement that is correct but describes objects arm P "
               "does not remove; the rendered arm P removes backdrop E1/E2."),
    ("scene20", "260823_cueoff_s20fix"): dict(
        b="B2", placebo=True,
        caveat="A2-6 repair round: same arms, more cams, H-yield camera band. "
               "Placebo admissible on the rendered-mass grade."),
}
DEFAULT_PRIMARY = dict(b="B1", placebo=True, caveat="")


# --------------------------------------------------------------------------- io
def read_per_frame(path, toggle="on"):
    """{frame_id: (tier, toggle, [p], [g])} for one toggle_state of one arm.

    `build_manifest.py` writes both rounds it was given, so the CSV also carries
    the OFF round under `toggle_state == "off"`.  Those frames belong to a
    different world and must never be pooled with the arm under test -- but they
    are exactly the false-alarm FLOOR that A2-3 publishes, so this function can
    be asked for them explicitly instead of dropping them unconditionally.
    """
    out = {}
    with open(path) as f:
        rd = csv.DictReader(f)
        cells = [c[2:] for c in (rd.fieldnames or []) if c.startswith("p_")]
        for r in rd:
            if r["toggle_state"] != toggle:
                continue
            out[r["frame_id"]] = (
                r["tier"], r["toggle_state"],
                [float(r["p_" + c]) for c in cells],
                [int(r["g_" + c]) for c in cells])
    return out


def max_on_gt(p, g):
    v = [pi for pi, gi in zip(p, g) if gi]
    return max(v) if v else float("nan")


def max_any(p):
    return max(p) if p else float("nan")


def scan(root, sets):
    """{(set, stem, arm, scene, model, seed): (on_frames, off_frames)}"""
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
            (read_per_frame(p, "on"), read_per_frame(p, "off"))
    return D


def load_render_mass(path=None):
    """{(scene, stem, pair, pop): pct>=32} from the real-render measurement."""
    path = path or os.path.join(AUDIT, "RENDER_MASS_SUMMARY.csv")
    out = {}
    if not os.path.isfile(path):
        return out
    with open(path) as f:
        for r in csv.DictReader(f):
            out[(r["scene"], r["stem"], r["pair"], r["pop"])] = (
                float(r["pct_ge32"]), float(r["pct_ge8"]), int(r["n"]))
    return out


def admissibility(ratio):
    """A2-5 grade ladder.  Conservative means the placebo removes AT LEAST as
    much light as the manipulation it is controlling for."""
    if ratio != ratio:
        return "UNMEASURED"
    if ratio >= 1.25:
        return "CONSERVATIVE"
    if ratio >= 0.80:
        return "MATCHED"
    if ratio >= 0.25:
        return "ANTI-CONSERVATIVE"
    return "SEVERELY ANTI-CONSERVATIVE"


# --------------------------------------------------------------------------- stats
def paired_h(a, b):
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
        elif ta != "H" and tb == "H":
            mig[f"{ta}->H"] = mig.get(f"{ta}->H", 0) + 1
    return sorted(both), mig


def recall_H(d, fids, gt=None):
    """Frame recall on the judged frames.

    `gt` overrides the arm's own GT vector (A2-13).  With gt=None each arm is
    scored on its own sheet, which is what the pre-registration assumes and what
    G2 is supposed to guarantee.  When G2's byte-identity clause fails ON THE
    JUDGED FRAMES the two arms are on different sheets and the difference is not
    a paired comparison; §4.5-2 VOIDS that pair, and the re-scored number below
    is reported only as the declared secondary reading.
    """
    if not fids:
        return float("nan")
    hit = 0
    for fid in fids:
        _, _, p, g = d[fid]
        v = max_on_gt(p, gt[fid] if gt is not None else g)
        if v == v and v >= TAU:
            hit += 1
    return hit / len(fids)


def gt_agreement(a, b, fids):
    """(n_differing, gt_of_A, gt_of_INTERSECTION) over the judged frames."""
    ndiff = 0
    ga, gi = {}, {}
    for fid in fids:
        _, _, _, x = a[fid]
        _, _, _, y = b[fid]
        if x != y:
            ndiff += 1
        ga[fid] = x
        gi[fid] = [1 if (u and v) else 0 for u, v in zip(x, y)]
    return ndiff, ga, gi


def recall_H_twin(d, twin, fids):
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
    n = hit = 0
    for fid, (_, _, p, g) in d.items():
        if any(g):
            continue
        n += 1
        if max_any(p) >= TAU:
            hit += 1
    return (hit / n if n else float("nan")), n


def sign_class(vals):
    """A2-1.  `SAME-SIGN k/n nz` / `NO-EFFECT` / `MIXED` / `EMPTY`.

    The non-zero count is carried in the label on purpose.  Under A2-1 both
    (+0.667, 0.000, 0.000) and (+1.000, +0.667, +0.667) are same-sign, but only
    the second is three seeds agreeing; the first is one seed moving and two
    seeds flat.  The pre-registered rule does not distinguish them, so the rule
    is applied unchanged and the distinction is PRINTED -- folding it away
    silently is the same mistake v1 made in the other direction with (0, 0, 0).
    """
    v = [x for x in vals if x == x]
    if not v:
        return "EMPTY"
    nz = [x for x in v if x != 0.0]
    if not nz:
        return "NO-EFFECT"
    if all(x > 0 for x in nz) or all(x < 0 for x in nz):
        return f"SAME-SIGN {len(nz)}/{len(v)}nz"
    return "MIXED"


def zero_flip_bound(n):
    """One-sided 95% upper bound on a per-frame flip rate given 0/n flips."""
    if not n:
        return float("nan")
    return 1.0 - 0.05 ** (1.0 / n)


def verdict(d_cue, d_pla, n_paired, n_seeds_needed=3):
    """The pre-registered rule with the A2 counting corrections applied."""
    dc = [x for x in d_cue if x == x]
    dp = [x for x in d_pla if x == x] if d_pla is not None else None
    if n_paired < MIN_PAIRED_H:
        return "VOID", (f"paired-H {n_paired} < {MIN_PAIRED_H} -- PREREG sec.4.5-3 "
                        f"says this scene is NOT JUDGED. No verdict is issued "
                        f"(A2-2; v1 issued one anyway).")
    if len(dc) < n_seeds_needed:
        return "UNDECIDED", f"only {len(dc)}/{n_seeds_needed} seeds available"
    cls = sign_class(dc)
    mean_c = sum(dc) / len(dc)
    p95 = zero_flip_bound(n_paired)
    if cls == "NO-EFFECT":
        return "NO-EFFECT", (
            f"D_cue = (" + ", ".join(f"{x:+.3f}" for x in dc) + ") -- the metric "
            f"did not move on a single frame in any seed. 0 flips in {n_paired} "
            f"paired frames bounds the per-frame flip rate at p95 = {p95:.3f} "
            f"(one-sided 95%). The pre-registered SHORTCUT threshold is "
            f"{THR_SHORTCUT}"
            + (f", which this bound DOES NOT RESOLVE ({p95:.3f} > {THR_SHORTCUT}): "
               f"H0-consistent but under-powered."
               if p95 > THR_SHORTCUT else
               f", which this bound DOES resolve ({p95:.3f} <= {THR_SHORTCUT}).")
            + " Seeds do not enlarge n -- all three read the same frames.")
    nz = len([x for x in dc if x != 0.0])
    weak = ("" if nz >= len(dc) else
            f" CAUTION: only {nz}/{len(dc)} seeds moved at all; the rest are "
            f"exactly 0, so same-sign here is a weaker statement than three "
            f"seeds agreeing (A2-1).")
    if cls == "MIXED":
        return "UNDECIDED", (f"seed signs disagree ({', '.join(f'{x:+.3f}' for x in dc)}) "
                             f"-- PREREG sec.4.5-4")
    if dp is None:
        if mean_c < THR_SHORTCUT:
            return "SHORTCUT", (f"D_cue {mean_c:+.3f} < {THR_SHORTCUT}, non-zero and "
                                f"same-sign ({cls}; no placebo -- exploratory)." + weak)
        return "UNDECIDED", (f"D_cue {mean_c:+.3f} but no admissible placebo, so the "
                             f"cue-evidence branch cannot be evaluated")
    mean_p = sum(dp) / len(dp) if dp else float("nan")
    corr = mean_c - mean_p
    if corr >= THR_CUE:
        return "CUE EVIDENCE", (f"(D_cue {mean_c:+.3f}) - (D_placebo {mean_p:+.3f}) = "
                                f"{corr:+.3f} >= {THR_CUE}, D_cue non-zero and "
                                f"same-sign ({cls})." + weak)
    if mean_c < THR_SHORTCUT:
        return "SHORTCUT", (f"D_cue {mean_c:+.3f} < {THR_SHORTCUT}, non-zero and "
                            f"same-sign ({cls}; placebo-corrected {corr:+.3f})." + weak)
    return "UNDECIDED", (f"(D_cue {mean_c:+.3f}) - (D_placebo {mean_p:+.3f}) = {corr:+.3f}: "
                         f"between {THR_SHORTCUT} and {THR_CUE}")


# --------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--eval-root", default=os.path.join(AUDIT, "eval"))
    ap.add_argument("--sets", default="lineage,twin")
    ap.add_argument("--models", default="rgb,depth,b2")
    ap.add_argument("--out", default=os.path.join(AUDIT, "READOUT_V2.md"))
    ap.add_argument("--census", default=os.path.join(AUDIT, "VERDICT_CENSUS_v2.csv"))
    a = ap.parse_args()
    sets = [s for s in a.sets.split(",") if s]
    models = [m for m in a.models.split(",") if m]
    D = scan(a.eval_root, sets)
    if not D:
        print(f"[readout] nothing under {a.eval_root} -- run eval_cueoff.sh phases 1,2 first")
        return 0
    MASS = load_render_mass()
    keys = sorted({(k[0], k[1], k[3]) for k in D})
    seeds = sorted({k[5] for k in D})
    census = []

    L = ["# READOUT_V2 — CUE-OFF intervention read-out under PREREG amendment A2", "",
         "**Machine-generated.** `CUEOFF_RESULT.md` (v1) is preserved unchanged; the "
         "authored re-adjudication is `CUEOFF_RESULT_v2.md`. Hypotheses, arms, "
         "thresholds and primary-leg locks are exactly those of `PREREG_CUEOFF.md` "
         "+ A1. A2 changes only how the code counts, and every change is a "
         "post-hoc correction made after the results were seen -- declared as such "
         "here and in every verdict it touches.", "",
         f"tau_op **{TAU}** · seeds `{seeds}` · retraining **0** · "
         f"frozen `runs/v2/{{rgb,depth,b2}}_s{{42,43,44}}/best.pt`", "",
         "```",
         "PRE-REGISTERED DECISION RULE (D36 / R2 sec.5.3-3), A2 COUNTING",
         "  D_cue     = recall_H(A) - recall_H(B)",
         "  D_placebo = recall_H(A) - recall_H(P)",
         f"  VOID         :  paired-H < {MIN_PAIRED_H}      -- no verdict at all (A2-2)",
         "  NO-EFFECT    :  every seed's D_cue == 0  -- own category, power bound printed (A2-1)",
         f"  CUE EVIDENCE : (D_cue - D_placebo) >= {THR_CUE}  AND  same-sign, >=1 non-zero",
         f"  SHORTCUT     :  D_cue < {THR_SHORTCUT}          AND  same-sign, >=1 non-zero",
         "  otherwise    :  UNDECIDED -- table only",
         "```", ""]

    # ---------------------------------------------------------------- dedup map
    # A2-7: fold blocks that are byte-identical between label sets.
    sig = {}
    for st, stem, scene in keys:
        h = []
        for arm in ("A", "B2", "B1", "P", "C"):
            for m, s in itertools.product(models, seeds):
                k = (st, stem, arm, scene, m, s)
                if k in D:
                    on, _ = D[k]
                    h.append((arm, m, s, tuple(sorted(
                        (f, t, tuple(p), tuple(g)) for f, (t, _, p, g) in on.items()))))
        sig.setdefault((stem, scene, tuple(h)), []).append(st)
    dup_of = {}
    for (stem, scene, _), sts in sig.items():
        if len(sts) > 1:
            for extra in sorted(sts)[1:]:
                dup_of[(extra, stem, scene)] = sorted(sts)[0]

    for st, stem, scene in keys:
        prim = PRIMARY.get((scene, stem), DEFAULT_PRIMARY)
        pop = "paired"
        rm = {arm: MASS.get((scene, stem, f"A_vs_{arm}", pop)) for arm in ("B1", "B2", "P")}
        ratios = {}
        for arm in ("B1", "B2"):
            if rm.get(arm) and rm.get("P") and rm[arm][0]:
                ratios[arm] = rm["P"][0] / rm[arm][0]
        L += [f"## {scene} · stem `{stem}` · label set `{st}`", ""]
        if (st, stem, scene) in dup_of:
            L += [f"> **FOLDED (A2-7).** Every judged number in this block is "
                  f"byte-identical to `{scene} · {stem} · {dup_of[(st, stem, scene)]}` "
                  f"above: the two label sets tier and score these frames "
                  f"identically, so this is not an independent replication and "
                  f"must not be counted as one.", ""]
        L += [f"> **Primary D_cue = D(A, {prim['b']})** · placebo "
              f"{'ADMISSIBLE' if prim['placebo'] else '**NOT ADMISSIBLE**'}  ",
              f"> {prim['caveat']}  "]
        if rm.get("P"):
            mline = ("> **Rendered mass on the judged frames (A2-5, >=32/255):** "
                     + " · ".join(f"A-vs-{arm} {rm[arm][0]:.2f}% of frame"
                                  for arm in ("B1", "B2", "P") if rm.get(arm)))
            if ratios:
                mline += ("  \n> **Placebo/cue ratio:** "
                          + " · ".join(f"P/{arm} = {r:.3f} -> **{admissibility(r)}**"
                                       for arm, r in sorted(ratios.items())))
            L += [mline, ""]
        else:
            L += ["", ""]

        armd, armoff = {}, {}
        for arm in ("A", "B2", "B1", "P", "C"):
            for m, s in itertools.product(models, seeds):
                k = (st, stem, arm, scene, m, s)
                if k in D:
                    armd[(arm, m, s)], armoff[(arm, m, s)] = D[k]
        if not any(k[0] == "A" for k in armd):
            L += ["_arm A absent -- nothing to compare._", ""]
            continue

        # ---- arm C false alarms (H2) WITH the lineage-off floor (A2-3) ----
        L += ["### arm C — false alarms, against the lineage-off FLOOR (H2)", "",
              "| model | FA(off) s42/43/44 | FA(off) mean | FA(C) s42/43/44 | "
              "FA(C) mean | delta | n frames |",
              "|---|---|---|---|---|---|---|"]
        for m in models:
            fc, ff, nn = [], [], 0
            for s in seeds:
                d = armd.get(("C", m, s))
                o = armoff.get(("C", m, s))
                fc.append(fa_rate(d)[0] if d is not None else float("nan"))
                if d is not None:
                    nn = fa_rate(d)[1]
                ff.append(fa_rate(o)[0] if o else float("nan"))
            mc = [x for x in fc if x == x]
            mf = [x for x in ff if x == x]
            fl = "—" if st == "twin" else (
                " / ".join("—" if x != x else f"{x:.3f}" for x in ff))
            flm = "—" if st == "twin" or not mf else f"{sum(mf)/len(mf):.3f}"
            dl = ("—" if st == "twin" or not (mc and mf)
                  else f"**{sum(mc)/len(mc) - sum(mf)/len(mf):+.3f}**")
            L.append(f"| {m} | {fl} | {flm} | "
                     + " / ".join("—" if x != x else f"{x:.3f}" for x in fc)
                     + f" | {'—' if not mc else f'{sum(mc)/len(mc):.3f}'} | {dl} | {nn} |")
        if st == "twin":
            L += ["", "_FA(off) suppressed: in the `twin` label set the OFF round IS "
                  "arm C, so the floor would be the same number as the FA (A2-3)._"]
        else:
            L += ["", "_FA(off) = the lineage hazard-off round (hazard off AND dressing "
                  "off) evaluated on the same cuts -- the true baseline for arm C. "
                  "It has been inside `per_frame.csv` since 06:03 and was never "
                  "printed (R4 F7)._"]
        h2, warn = [], []
        for m in models:
            v = [fa_rate(armd[("C", m, s)])[0] for s in seeds if ("C", m, s) in armd]
            f = [fa_rate(armoff[("C", m, s)])[0] for s in seeds
                 if armoff.get(("C", m, s))] if st != "twin" else []
            if not v:
                continue
            mv = sum(v) / len(v)
            mf = (sum(f) / len(f)) if f else float("nan")
            h2.append((m, mv, mf))
            if mv >= 0.40 and mf == mf and (mv - mf) < 0.15:
                warn.append(f"{m}: FA {mv:.3f} clears the 0.40 bar, but the "
                            f"hazard-off FLOOR is already {mf:.3f} -- the arm-C "
                            f"excess is only {mv - mf:+.3f}. Read as a property of "
                            f"the seed/scene, not of arm C")
        acc = any(x[1] >= 0.40 for x in h2)
        L += ["", f"**H2 verdict for {scene}/{stem}/{st}** (PREREG sec.4.4 accepts at "
              f"FA >= 0.40): "
              + " · ".join(f"{m} {v:.3f}" + (f" (floor {fl:.3f}, excess {v-fl:+.3f})"
                                             if fl == fl else "")
                           for m, v, fl in h2)
              + " -> " + ("**ACCEPTED**" if acc else "**REJECTED**")
              + ". (v1 printed the 0.40 baseline under every table and never issued "
                "the verdict -- R5 D-8.)"]
        if warn:
            L += ["", "> **H2 CAVEAT (A2-3):** " + " · ".join(warn) + "."]
        L += [""]

        # ---- H recall + deltas ------------------------------------------
        for m in models:
            L += [f"### {m} — paired strict-H recall and deltas", ""]
            rows = []
            deltas, npairs, gt_note = {}, {}, {}
            for arm in ("B2", "B1", "P"):
                if not any(k[0] == arm for k in armd):
                    continue
                dcue, dtwin_c, ra, rb, npair, migs = [], [], [], [], [], {}
                d_agt, d_int, gtbad = [], [], 0
                for s in seeds:
                    da, db = armd.get(("A", m, s)), armd.get((arm, m, s))
                    if da is None or db is None:
                        continue
                    fids, mig = paired_h(da, db)
                    for k, v in mig.items():
                        migs[k] = migs.get(k, 0) + v
                    npair.append(len(fids))
                    nd, g_a, g_i = gt_agreement(da, db, fids)
                    gtbad = max(gtbad, nd)
                    r_a, r_b = recall_H(da, fids), recall_H(db, fids)
                    ra.append(r_a)
                    rb.append(r_b)
                    dcue.append(r_a - r_b)
                    if nd:
                        d_agt.append(recall_H(da, fids, g_a) - recall_H(db, fids, g_a))
                        d_int.append(recall_H(da, fids, g_i) - recall_H(db, fids, g_i))
                    tc = armd.get(("C", m, s))
                    if tc is not None:
                        dtwin_c.append(recall_H_twin(da, tc, fids)
                                       - recall_H_twin(db, tc, fids))
                gt_note[arm] = (gtbad, d_agt, d_int)
                deltas[arm] = (dcue, dtwin_c)
                n = npair[0] if npair else 0
                npairs[arm] = n
                flag = ""
                if n < MIN_PAIRED_H:
                    flag = f" **VOID (paired-H {n} < {MIN_PAIRED_H}, PREREG sec.4.5-3)**"
                if gt_note.get(arm, (0,))[0]:
                    flag += (f" **VOID (polar_gt differs on {gt_note[arm][0]}/{n} "
                             f"JUDGED frames, PREREG sec.4.5-2 / A2-13)**")
                rows.append(
                    f"| A vs {arm} | {n} | "
                    + " | ".join(f"{x:.3f}" for x in ra) + " | "
                    + " | ".join(f"{x:.3f}" for x in rb) + " | "
                    + " | ".join(f"{x:+.3f}" for x in dcue) + " | "
                    + (f"{sum(dcue)/len(dcue):+.3f}" if dcue else "—") + " | "
                    + sign_class(dcue) + " | "
                    + (f"{dict(migs)}" if migs else "none (G4-verified)") + flag + " |")
            if rows:
                L += ["| pair | paired-H | " + " | ".join(f"R_A s{s}" for s in seeds)
                      + " | " + " | ".join(f"R_B s{s}" for s in seeds)
                      + " | " + " | ".join(f"D s{s}" for s in seeds)
                      + " | mean D | sign class | tier migration |",
                      "|---|---|" + "---|" * (3 * len(seeds) + 3)] + rows + [""]

            if "B1" in deltas and "B2" in deltas:
                g = [x - y for x, y in zip(deltas["B1"][0], deltas["B2"][0])]
                tot = sum(deltas["B1"][0])
                share = (sum(deltas["B2"][0]) / tot) if abs(tot) >= 0.05 else float("nan")
                why_no = None
                if share != share:
                    why_no = ("|sum D_B1| < 0.05 -- a share of a near-zero "
                              "denominator is not a share")
                elif sign_class(deltas["B1"][0]) == "MIXED":
                    why_no = ("D(A,B1) changes sign across seeds, so its sum is not a "
                              "magnitude and cannot be a denominator")
                elif not (0.0 <= share <= 1.0):
                    why_no = (f"the ratio is {100*share:.0f}%, outside [0, 100] -- "
                              f"removing the guard alone moved the metric MORE than "
                              f"removing every cue, which is not a share of anything")
                L += [f"**H3 guard standalone** — D(A,B1) - D(A,B2) = "
                      + ", ".join(f"{x:+.3f}" for x in g)
                      + " · guard share of the full cue effect = "
                      + (f"— ({why_no} -- R5 D-6)" if why_no else f"{100*share:.0f}%"), ""]

            # ---- THE RULE --------------------------------------------------
            b = prim["b"]
            if b in deltas:
                dp = deltas["P"][0] if (prim["placebo"] and "P" in deltas) else None
                n = npairs.get(b, 0)
                nd, d_agt, d_int = gt_note.get(b, (0, [], []))
                if nd:
                    lab, why = "VOID", (
                        f"polar_gt differs between arm A and arm {b} on {nd}/{n} of "
                        f"the JUDGED frames -- the two arms are scored on different "
                        f"sheets, so recall_H(A) - recall_H({b}) is not a paired "
                        f"comparison. PREREG sec.4.5-2 does not judge this scene. "
                        f"(A2-13, ruled before any model was run on this round.)")
                else:
                    lab, why = verdict(deltas[b][0], dp, n)
                L += [f"> ### VERDICT ({m}, primary D_cue = D(A,{b})"
                      + (", placebo-corrected" if dp is not None else ", NO placebo")
                      + f"): **{lab}**", f"> {why}", ""]
                census.append(dict(label_set=st, stem=stem, scene=scene, model=m,
                                   leg="primary", pair=f"A_vs_{b}", n_paired=n,
                                   verdict=lab, folded=bool((st, stem, scene) in dup_of),
                                   d_cue_mean=round(sum(deltas[b][0])/len(deltas[b][0]), 4)
                                   if deltas[b][0] else None,
                                   sign_class=sign_class(deltas[b][0]),
                                   placebo_ratio=round(ratios.get(b, float('nan')), 3)
                                   if b in ratios else None,
                                   placebo_grade=admissibility(ratios.get(b, float('nan')))))
                if nd and d_agt:
                    dpm = (sum(dp) / len(dp)) if dp else float("nan")
                    l_a, _ = verdict(d_agt, dp, n)
                    l_i, _ = verdict(d_int, dp, n)
                    L += ["> **SECONDARY / EXPLORATORY (A2-13-2), re-scored on ARM A's "
                          "GT so both arms share one sheet — NOT promotable to a "
                          "primary verdict, whatever it shows:**  ",
                          "> D_cue = " + ", ".join(f"{x:+.3f}" for x in d_agt)
                          + f" (mean {sum(d_agt)/len(d_agt):+.3f}, {sign_class(d_agt)})"
                          + (f" · D_placebo mean {dpm:+.3f} · corrected "
                             f"{sum(d_agt)/len(d_agt) - dpm:+.3f}" if dpm == dpm else "")
                          + f" · rule would say **{l_a}**  ",
                          "> SENSITIVITY (A2-13-3), INTERSECTION GT: D_cue = "
                          + ", ".join(f"{x:+.3f}" for x in d_int)
                          + f" (mean {sum(d_int)/len(d_int):+.3f}, {sign_class(d_int)})"
                          + (f" · corrected {sum(d_int)/len(d_int) - dpm:+.3f}"
                             if dpm == dpm else "")
                          + f" · rule would say **{l_i}**", ""]
                if deltas[b][1]:
                    if nd:
                        lab2, why2 = "VOID", (
                            f"same sec.4.5-2 breach as the primary reading: the "
                            f"twin-conditional metric is scored on each arm's own GT "
                            f"cells too, so it inherits the two-scoresheet problem. "
                            f"Raw value, reported but NOT a verdict: D = "
                            + ", ".join(f"{x:+.3f}" for x in deltas[b][1])
                            + f" (mean {sum(deltas[b][1])/len(deltas[b][1]):+.3f}).")
                    else:
                        lab2, why2 = verdict(deltas[b][1],
                                             deltas["P"][1] if dp is not None else None, n)
                    L += [f"> twin-conditional (twin = arm C, R2 P3 primary metric): "
                          f"**{lab2}** — {why2}", ""]
                    census.append(dict(label_set=st, stem=stem, scene=scene, model=m,
                                       leg="primary-twinconditional", pair=f"A_vs_{b}",
                                       n_paired=n, verdict=lab2,
                                       folded=bool((st, stem, scene) in dup_of),
                                       d_cue_mean=round(sum(deltas[b][1])/len(deltas[b][1]), 4)
                                       if deltas[b][1] else None,
                                       sign_class=sign_class(deltas[b][1]),
                                       placebo_ratio=None, placebo_grade=""))
                    if lab2 != lab and "VOID" not in (lab, lab2):
                        L += ["> **The twin-conditional verdict DISAGREES with the raw "
                              "recall verdict. PREREG sec.4.4 says the twin-conditional "
                              "reading wins the body text and the raw one goes to the "
                              "appendix.**", ""]
            if "B1" in deltas and b != "B1":
                dp = deltas["P"][0] if (prim["placebo"] and "P" in deltas) else None
                n = npairs.get("B1", 0)
                nd1 = gt_note.get("B1", (0,))[0]
                if nd1:
                    lab, why = "VOID", (f"polar_gt differs on {nd1}/{n} judged frames "
                                        f"-- PREREG sec.4.5-2 / A2-13")
                else:
                    lab, why = verdict(deltas["B1"][0], dp, n)
                extra = ""
                if "B1" in ratios:
                    extra = (f"  (placebo/cue ratio {ratios['B1']:.3f} = "
                             f"{admissibility(ratios['B1'])}; PREREG sec.3.1 forbids "
                             f"promoting this leg to decisive evidence)")
                L += [f"_secondary D_cue = D(A,B1): **{lab}** — {why}{extra}_", ""]
                census.append(dict(label_set=st, stem=stem, scene=scene, model=m,
                                   leg="secondary", pair="A_vs_B1", n_paired=n,
                                   verdict=lab, folded=bool((st, stem, scene) in dup_of),
                                   d_cue_mean=round(sum(deltas["B1"][0])/len(deltas["B1"][0]), 4)
                                   if deltas["B1"][0] else None,
                                   sign_class=sign_class(deltas["B1"][0]),
                                   placebo_ratio=round(ratios.get("B1", float('nan')), 3)
                                   if "B1" in ratios else None,
                                   placebo_grade=admissibility(ratios.get("B1", float('nan')))))

    # ------------------------------------------------------------- census
    def tally(rows):
        c = {}
        for r in rows:
            c[r["verdict"]] = c.get(r["verdict"], 0) + 1
        return c

    prim_rows = [r for r in census if r["leg"] == "primary"]
    L += ["", "## Verdict census (A2 counting)", "",
          "| population | CUE EVIDENCE | SHORTCUT | NO-EFFECT | UNDECIDED | VOID | n |",
          "|---|---|---|---|---|---|---|"]
    for name, rows in (("primary, all blocks", prim_rows),
                       ("primary, folded blocks removed",
                        [r for r in prim_rows if not r["folded"]]),
                       ("primary, non-VOID only",
                        [r for r in prim_rows if r["verdict"] != "VOID"]),
                       ("secondary (promotion forbidden)",
                        [r for r in census if r["leg"] == "secondary"]),
                       ("twin-conditional",
                        [r for r in census if r["leg"] == "primary-twinconditional"])):
        c = tally(rows)
        L.append(f"| {name} | {c.get('CUE EVIDENCE', 0)} | {c.get('SHORTCUT', 0)} | "
                 f"{c.get('NO-EFFECT', 0)} | {c.get('UNDECIDED', 0)} | "
                 f"{c.get('VOID', 0)} | {len(rows)} |")
    L += ["", "_v1 reported 5 SHORTCUT verdicts in the primary lineage leg. All five "
          "were exactly (0.000, 0.000, 0.000) and reached SHORTCUT only through "
          "`same_sign((0,0,0)) == True`. Under A2-1 they are NO-EFFECT with an "
          "explicit power bound; under A2-2 the scene20 ones are VOID as well._", ""]

    with open(a.out, "w") as f:
        f.write("\n".join(L) + "\n")
    if census:
        with open(a.census, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(census[0]))
            w.writeheader()
            w.writerows(census)
    print("\n".join(L[-14:]))
    print(f"\n-> {a.out}\n-> {a.census}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
