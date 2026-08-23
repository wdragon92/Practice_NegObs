# GATES_CUEOFF — 2026-08-23 05:24:12  ·  **v1 · RECONSTRUCTED, NOT THE ORIGINAL BYTES**

> ## ⚠ PROVENANCE NOTICE — read before using this file as evidence
>
> **The original file was destroyed by accident during the A2 repair session
> (2026-08-23 ~07:33).** `gates_cueoff.py`'s `--out` defaults to this path, and one
> diagnostic re-run of the patched battery was launched without `--out`, overwriting
> the 05:24:12 record in place. There was no backup and this repository is not under
> version control.
>
> **What is below is a reconstruction, not a recovery.** It is transcribed from the
> file as read at 2026-08-23 07:0x, before the overwrite, in the same session that
> then destroyed it. It is independently corroborated by `redteam/R4_cueoff.md` §F5,
> which quotes the same note lines and the same `FAIL 8` count from the original file
> at 07:00, and by `redteam/R5_qc.md`. Treat it as a faithful transcript with a
> single custodian and no cryptographic chain — which is weaker than the original was,
> and the weakening is our fault.
>
> The accidental overwrite output (the patched battery's post-stage run at ~07:33) was
> not discarded: it is kept at
> `scratchpad/GATES_overwritten_by_accident.md` outside the audit directory.
>
> **The current gate record is `GATES_CUEOFF_v2.md`**, produced by the A2 battery over
> all three rounds including `260823_cueoff_s20fix`. This file exists only so that what
> v1 reported — and did not report — stays legible.
>
> **What this file proves, and it is the point of keeping it:** at 05:24:12 the battery
> reported 8 failures, all of them the `heightmap.npy` clause of G2, and reported G4,
> G5 and G2's `polar_gt` clause as *skipped for want of labels*. The evaluation chain
> then ran to completion and `CUEOFF_RESULT.md` printed `tier migration | none` on
> every row — a G4 output, from a gate that had not run. The cause was not the
> 27-minute gap between this run and the label files, as R4 F5 inferred; it was
> `load_labels()` looking for a filename the labeller never writes (see A2-8).

---

stage `post` · rounds `['260823_cueoff2_A', '260823_cueoff2_B1', '260823_cueoff2_B2', '260823_cueoff2_C', '260823_cueoff2_P', '260823_cueoff_A', '260823_cueoff_B1', '260823_cueoff_B2', '260823_cueoff_C', '260823_cueoff_P']`

**FAIL 8**

## Failures

- **G2** — 260823_cueoff scene12 B1 vs A: heightmap.npy differs -- a cue_* toggle moved the hazard geometry. REGULATION BREACH.
- **G2** — 260823_cueoff scene20 B1 vs A: heightmap.npy differs -- a cue_* toggle moved the hazard geometry. REGULATION BREACH.
- **G2** — 260823_cueoff scene12 B2 vs A: heightmap.npy differs -- a cue_* toggle moved the hazard geometry. REGULATION BREACH.
- **G2** — 260823_cueoff scene20 B2 vs A: heightmap.npy differs -- a cue_* toggle moved the hazard geometry. REGULATION BREACH.
- **G2** — 260823_cueoff scene12 P vs A: heightmap.npy differs -- a cue_* toggle moved the hazard geometry. REGULATION BREACH.
- **G2** — 260823_cueoff2 scene12 B1 vs A: heightmap.npy differs -- a cue_* toggle moved the hazard geometry. REGULATION BREACH.
- **G2** — 260823_cueoff2 scene12 B2 vs A: heightmap.npy differs -- a cue_* toggle moved the hazard geometry. REGULATION BREACH.
- **G2** — 260823_cueoff2 scene12 P vs A: heightmap.npy differs -- a cue_* toggle moved the hazard geometry. REGULATION BREACH.

## Notes

- G2: 260823_cueoff scene12 B1 vs A: labels absent -- polar_gt check deferred
- G2: 260823_cueoff scene17 B1 vs A: labels absent -- polar_gt check deferred
- G2: 260823_cueoff scene20 B1 vs A: labels absent -- polar_gt check deferred
- G2: 260823_cueoff scene12 B2 vs A: labels absent -- polar_gt check deferred
- G2: 260823_cueoff scene20 B2 vs A: labels absent -- polar_gt check deferred
- G2: 260823_cueoff scene12 P vs A: labels absent -- polar_gt check deferred
- G2: 260823_cueoff scene17 P vs A: labels absent -- polar_gt check deferred
- G2: 260823_cueoff scene20 P vs A: labels absent -- polar_gt check deferred
- G2: 260823_cueoff2 scene12 B1 vs A: labels absent -- polar_gt check deferred
- G2: 260823_cueoff2 scene12 B2 vs A: labels absent -- polar_gt check deferred
- G2: 260823_cueoff2 scene12 P vs A: labels absent -- polar_gt check deferred
- G4: labels for 260823_cueoff_A absent -- skipped
- G4: labels for 260823_cueoff_B1 absent -- skipped
- G4: labels for 260823_cueoff_B2 absent -- skipped
- G4: labels for 260823_cueoff_C absent -- skipped
- G4: labels for 260823_cueoff_P absent -- skipped
- G4: labels for 260823_cueoff2_A absent -- skipped
- G4: labels for 260823_cueoff2_B1 absent -- skipped
- G4: labels for 260823_cueoff2_B2 absent -- skipped
- G4: labels for 260823_cueoff2_C absent -- skipped
- G4: labels for 260823_cueoff2_P absent -- skipped
- G5: labels for 260823_cueoff_C absent -- skipped
- G5: labels for 260823_cueoff2_C absent -- skipped
- G7: no label file yet -- run eval_cueoff.sh phase 1
