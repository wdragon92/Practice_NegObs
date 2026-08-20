# GATES_REPORT — PROVISIONAL-GRID-V1

manifest: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/dataset_manifest_v2.json`  (1584 frames)
grid: `PROVISIONAL-GRID-V1`  (4 bands × 5 sectors = 20 cells, band edges [0.0, 2.0, 5.0, 8.0, 12.0] m)
gt_source: `derived-heightmapdiff-gridv1-PROVISIONAL`  tier_source: `derived-depth-v0-strict`
footprint: `v2-diff-stepgate`  cam convention: `CAM_CONVENTION.md sec.2/sec.6 == variation_kit.dir_of + look_at_rows (driver code, HEAD 8c814db); VERIFIED on 260819_patchprobe_on/scene04, median |z_recon - ground_z| = 0.0001 m`
gate policy: `train-on-gated; pregate preserved per D14`

## ⛔ PROVISIONAL-HOLD — 아침 결재 대상 (D14④ + D17)

**4 scene(s) HELD OUT of train/val/test: `sceneD4`, `scene11` (D17 mislabel-risk), `scene13` (D17 mislabel-risk), `scene19` (D17 mislabel-risk)**

D14④ (`sceneD4`) — batch-1 non-stair drop scene(s) whose hazard-ON arm carries ZERO positive frames after the D10 step gate: a suspected over-exclusion, not a designed hard negative. Held so a possibly-wrong all-negative scene cannot distort the headline test metric; the adopt/revert ruling is the morning's.
D17 mislabel-risk (`scene11`, `scene13`, `scene19`) — hand-listed scene(s) whose hazard-ON labels are suspected WRONG, not merely absent; training on them would teach that a real edge is safe. This list is an input, not a measurement — gates.py cannot detect a mislabel. Source: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/annotations/extra_holds.json`.
Machine-readable: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/annotations/hold_scenes.json`  →  `make_split.py --exclude-scenes @/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/annotations/hold_scenes.json`
Reverting the gate needs no re-derivation: swap `polar_gt` <-> `polar_gt_pregate` (see STEP-GATE EXCLUSIONS below).

## G1 required fields — PASS
excluded frames: 0

## G2 toggle sanity — PASS (with 4 scene(s) on PROVISIONAL-HOLD) (1 explained zero, D19⑤)
off-arm frames with residual footprint: 0 (scenes flagged: none)
on-arm scenes with ZERO positive frames (UNEXPLAINED — these fail the gate): none
hard-negative scenes at zero (expected, excluded from the gate): ['sceneN1', 'sceneN2', 'sceneN3', 'sceneN4', 'sceneN5']
EXPLAINED zero (D19⑤ — annotated, stays in its split, excluded from the failure list): ['scene06']
- `scene06` — out-of-FOV (D17) — the hazard lies outside every cut's frustum (both arms' 0.1-percentile z = -0.14 m, twin max_diff 0.0003 m); the label is correct, the scene simply never shows the drop
PROVISIONAL-HOLD scenes at zero (D14(4), held out of every split instead of failing the gate): ['sceneD4']
PROVISIONAL-HOLD scenes added by hand (D17 mislabel-risk), held out of every split for the same reason: ['scene11', 'scene13', 'scene19']
> residual off-arm footprint = the hazard toggle left geometry behind; REPORTED, nothing deleted.

## footprint v2 per-scene summary (D10 twin-diff + step gate)

| scene | arm | comps raw | comps kept | fp cells raw | fp cells kept | max diff (m) | void on/off |
|---|---|---|---|---|---|---|---|
| scene01 | off | 0 | 0 | 0 | 0 | 0.0 | 0/0 |
| scene01 | on | 1 | 1 | 75866 | 75866 | 0.6 | 0/0 |
| scene02 | off | 0 | 0 | 0 | 0 | 0.0 | 55024/55024 |
| scene02 | on | 230 | 123–127 | 807 | 636–651 | 3.433 | 62484/55024 |
| scene03 | off | 0 | 0 | 0 | 0 | 0.0 | 219/219 |
| scene03 | on | 22 | 3 | 67695 | 64592 | 3.2035 | 551/219 |
| scene04 | off | 0 | 0 | 0 | 0 | 0.0 | 0/0 |
| scene04 | on | 3 | 3 | 53543 | 53543 | 1.4501 | 85/0 |
| scene05 | off | 0 | 0 | 0 | 0 | 0.0 | 0/0 |
| scene05 | on | 1 | 1 | 49155 | 49155 | 1.207 | 0/0 |
| scene06 | off | 0 | 0 | 0 | 0 | 0.0 | 0/0 |
| scene06 | on | 0 | 0 | 0 | 0 | 0.0003 | 0/0 |
| scene07 | off | 0 | 0 | 0 | 0 | 0.0 | 19789/19789 |
| scene07 | on | 385 | 41–47 | 18874 | 9925–9943 | 6.0044 | 73001/19789 |
| scene08 | off | 0 | 0 | 0 | 0 | 0.0 | 24272/24272 |
| scene08 | on | 301 | 37–43 | 66547 | 64903–64966 | 4.5066 | 0/24272 |
| scene09 | off | 0 | 0 | 0 | 0 | 0.0 | 0/0 |
| scene09 | on | 1 | 1 | 87954 | 87954 | 5.2065 | 0/0 |
| scene10 | off | 0 | 0 | 0 | 0 | 0.0 | 0/0 |
| scene10 | on | 1 | 1 | 11225 | 11225 | 4.05 | 0/0 |
| scene11 | off | 0 | 0 | 0 | 0 | 0.0 | 0/0 |
| scene11 | on | 0 | 0 | 0 | 0 | 0.0005 | 0/0 |
| scene12 | off | 0 | 0 | 0 | 0 | 0.0 | 18524/18524 |
| scene12 | on | 301 | 2 | 33605 | 32797 | 1.3618 | 25958/18524 |
| scene13 | off | 0 | 0 | 0 | 0 | 0.0 | 123/123 |
| scene13 | on | 0 | 0 | 0 | 0 | 0.0 | 0/123 |
| scene14 | off | 0 | 0 | 0 | 0 | 0.0 | 33600/33600 |
| scene14 | on | 1 | 1 | 54213 | 54213 | 4.23 | 0/33600 |
| scene15 | off | 0 | 0 | 0 | 0 | 0.0 | 0/0 |
| scene15 | on | 1 | 1 | 2750 | 2750 | 2.21 | 0/0 |
| scene16 | off | 0 | 0 | 0 | 0 | 0.0 | 29588/29588 |
| scene16 | on | 12 | 1–4 | 10325 | 4768–4771 | 3.8959 | 41852/29588 |
| scene17 | off | 0 | 0 | 0 | 0 | 0.0 | 0/0 |
| scene17 | on | 2 | 2 | 65833 | 65833 | 3.2 | 177/0 |
| scene18 | off | 0 | 0 | 0 | 0 | 0.0 | 0/0 |
| scene18 | on | 2 | 2 | 88179 | 88179 | 2.56 | 321/0 |
| scene19 | off | 0 | 0 | 0 | 0 | 0.0 | 0/0 |
| scene19 | on | 0 | 0 | 0 | 0 | 0.0591 | 0/0 |
| scene20 | off | 0 | 0 | 0 | 0 | 0.0 | 0/0 |
| scene20 | on | 1 | 1 | 60659 | 60659 | 2.15 | 0/0 |
| scene21 | off | 0 | 0 | 0 | 0 | 0.0 | 0/0 |
| scene21 | on | 6 | 6 | 14456 | 14456 | 2.75 | 0/0 |
| sceneC1 | off | 0 | 0 | 0 | 0 | 0.0 | 0/0 |
| sceneC1 | on | 1 | 1 | 68846 | 68846 | 2.042 | 0/0 |
| sceneC2 | off | 0 | 0 | 0 | 0 | 0.0 | 0/0 |
| sceneC2 | on | 1 | 1 | 63140 | 63140 | 2.2584 | 0/0 |
| sceneC4 | off | 0 | 0 | 0 | 0 | 0.0 | 0/0 |
| sceneC4 | on | 1 | 1 | 67482 | 67482 | 2.102 | 0/0 |
| sceneD1 | off | 0 | 0 | 0 | 0 | 0.0 | 0/0 |
| sceneD1 | on | 1 | 1 | 94647 | 94647 | 1.2 | 0/0 |
| sceneD2 | off | 0 | 0 | 0 | 0 | 0.0 | 0/0 |
| sceneD2 | on | 1 | 1 | 1160 | 1160 | 2.9836 | 0/0 |
| sceneD3 | off | 0 | 0 | 0 | 0 | 0.0 | 0/0 |
| sceneD3 | on | 1 | 1 | 2520 | 2520 | 0.8 | 0/0 |
| sceneD4 | off | 0 | 0 | 0 | 0 | 0.0 | 0/0 |
| sceneD4 | on | 0 | 0 | 0 | 0 | 0.0 | 0/0 |
| sceneN1 | off | 0 | 0 | 0 | 0 | 0.0 | 0/0 |
| sceneN1 | on | 0 | 0 | 0 | 0 | 0.0 | 0/0 |
| sceneN2 | off | 0 | 0 | 0 | 0 | 0.0 | 0/0 |
| sceneN2 | on | 0 | 0 | 0 | 0 | 0.0 | 0/0 |
| sceneN3 | off | 0 | 0 | 0 | 0 | 0.0 | 0/0 |
| sceneN3 | on | 0 | 0 | 0 | 0 | 0.0 | 0/0 |
| sceneN4 | off | 0 | 0 | 0 | 0 | 0.0 | 0/0 |
| sceneN4 | on | 0 | 0 | 0 | 0 | 0.2055 | 0/0 |
| sceneN5 | off | 0 | 0 | 0 | 0 | 0.0 | 0/0 |
| sceneN5 | on | 0 | 0 | 0 | 0 | 0.0 | 0/0 |
> comps/cells kept are given as min–max over the scene's cuts: the step gate reads the near boundary, which is camera-dependent. Raw columns are camera-independent scene geometry.

### slope / illusion hard-negative check

| scene | expectation | observed | verdict |
|---|---|---|---|
| sceneN4 | 0 cells AFTER step gate | raw 0 cells / 0 comps -> kept 0 cells / 0 comps | OK |
| sceneN1 | 0 cells RAW | raw 0 cells / 0 comps (max diff 0.0) | OK |
| sceneN2 | 0 cells RAW | raw 0 cells / 0 comps (max diff 0.0) | OK |
| sceneN3 | 0 cells RAW | raw 0 cells / 0 comps (max diff 0.0) | OK |
| sceneN5 | 0 cells RAW | raw 0 cells / 0 comps (max diff 0.0) | OK |
> FLAG lines are REPORTED, not fatal: they say the twin-diff footprint disagrees with the hard-negative design, which is a morning judgement call (re-render vs. re-tune the step gate), not an automatic reject.

## STEP-GATE EXCLUSIONS (D14)

| scene | arm | hm cells raw | hm cells kept | hm cells excluded | frames w/ gate_excluded | excluded GT cells (sum) |
|---|---|---|---|---|---|---|
| scene01 | off | 0 | 0 | 0 | 0/24 | 0 |
| scene01 | on | 75866 | 75866 | 0 | 0/24 | 0 |
| scene02 | off | 0 | 0 | 0 | 0/24 | 0 |
| scene02 | on | 807 | 636–651 | 156–171 | 3/24 | 3 |
| scene03 | off | 0 | 0 | 0 | 0/24 | 0 |
| scene03 | on | 67695 | 64592 | 3103 | 21/24 | 60 |
| scene04 | off | 0 | 0 | 0 | 0/24 | 0 |
| scene04 | on | 53543 | 53543 | 0 | 0/24 | 0 |
| scene05 | off | 0 | 0 | 0 | 0/24 | 0 |
| scene05 | on | 49155 | 49155 | 0 | 0/24 | 0 |
| scene06 | off | 0 | 0 | 0 | 0/24 | 0 |
| scene06 | on | 0 | 0 | 0 | 0/24 | 0 |
| scene07 | off | 0 | 0 | 0 | 0/24 | 0 |
| scene07 | on | 18874 | 9925–9943 | 8931–8949 | 24/24 | 84 |
| scene08 | off | 0 | 0 | 0 | 0/24 | 0 |
| scene08 | on | 66547 | 64903–64966 | 1581–1644 | 0/24 | 0 |
| scene09 | off | 0 | 0 | 0 | 0/24 | 0 |
| scene09 | on | 87954 | 87954 | 0 | 0/24 | 0 |
| scene10 | off | 0 | 0 | 0 | 0/24 | 0 |
| scene10 | on | 11225 | 11225 | 0 | 0/24 | 0 |
| scene11 | off | 0 | 0 | 0 | 0/24 | 0 |
| scene11 | on | 0 | 0 | 0 | 0/24 | 0 |
| scene12 | off | 0 | 0 | 0 | 0/24 | 0 |
| scene12 | on | 33605 | 32797 | 808 | 0/24 | 0 |
| scene13 | off | 0 | 0 | 0 | 0/24 | 0 |
| scene13 | on | 0 | 0 | 0 | 0/24 | 0 |
| scene14 | off | 0 | 0 | 0 | 0/24 | 0 |
| scene14 | on | 54213 | 54213 | 0 | 0/24 | 0 |
| scene15 | off | 0 | 0 | 0 | 0/24 | 0 |
| scene15 | on | 2750 | 2750 | 0 | 0/24 | 0 |
| scene16 | off | 0 | 0 | 0 | 0/24 | 0 |
| scene16 | on | 10325 | 4768–4771 | 5554–5557 | 0/24 | 0 |
| scene17 | off | 0 | 0 | 0 | 0/24 | 0 |
| scene17 | on | 65833 | 65833 | 0 | 0/24 | 0 |
| scene18 | off | 0 | 0 | 0 | 0/24 | 0 |
| scene18 | on | 88179 | 88179 | 0 | 0/24 | 0 |
| scene19 | off | 0 | 0 | 0 | 0/24 | 0 |
| scene19 | on | 0 | 0 | 0 | 0/24 | 0 |
| scene20 | off | 0 | 0 | 0 | 0/24 | 0 |
| scene20 | on | 60659 | 60659 | 0 | 0/24 | 0 |
| scene21 | off | 0 | 0 | 0 | 0/24 | 0 |
| scene21 | on | 14456 | 14456 | 0 | 0/24 | 0 |
| sceneC1 | off | 0 | 0 | 0 | 0/24 | 0 |
| sceneC1 | on | 68846 | 68846 | 0 | 0/24 | 0 |
| sceneC2 | off | 0 | 0 | 0 | 0/24 | 0 |
| sceneC2 | on | 63140 | 63140 | 0 | 0/24 | 0 |
| sceneC4 | off | 0 | 0 | 0 | 0/24 | 0 |
| sceneC4 | on | 67482 | 67482 | 0 | 0/24 | 0 |
| sceneD1 | off | 0 | 0 | 0 | 0/24 | 0 |
| sceneD1 | on | 94647 | 94647 | 0 | 0/24 | 0 |
| sceneD2 | off | 0 | 0 | 0 | 0/24 | 0 |
| sceneD2 | on | 1160 | 1160 | 0 | 0/24 | 0 |
| sceneD3 | off | 0 | 0 | 0 | 0/24 | 0 |
| sceneD3 | on | 2520 | 2520 | 0 | 0/24 | 0 |
| sceneD4 | off | 0 | 0 | 0 | 0/24 | 0 |
| sceneD4 | on | 0 | 0 | 0 | 0/24 | 0 |
| sceneN1 | off | 0 | 0 | 0 | 0/24 | 0 |
| sceneN1 | on | 0 | 0 | 0 | 0/24 | 0 |
| sceneN2 | off | 0 | 0 | 0 | 0/24 | 0 |
| sceneN2 | on | 0 | 0 | 0 | 0/24 | 0 |
| sceneN3 | off | 0 | 0 | 0 | 0/24 | 0 |
| sceneN3 | on | 0 | 0 | 0 | 0/24 | 0 |
| sceneN4 | off | 0 | 0 | 0 | 0/24 | 0 |
| sceneN4 | on | 0 | 0 | 0 | 0/24 | 0 |
| sceneN5 | off | 0 | 0 | 0 | 0/24 | 0 |
| sceneN5 | on | 0 | 0 | 0 | 0/24 | 0 |
| **total** | | | | | **48/1584** | **147** |

> hm cells kept/excluded are min–max over the scene's cuts (the gate reads the camera-facing near boundary, so it is per-cut); raw is camera-independent. `gate_excluded` = polar cells positive in `polar_gt_pregate` but not in the trained `polar_gt`. Per D14 the pre-gate label is preserved on every frame, so reverting the gate is a field swap (`polar_gt` <-> `polar_gt_pregate`), not a re-derivation.

## G3 strict-H distribution — PASS
totals: {'off': 792, 'V': 438, 'E': 36, 'none_in_fov': 261, 'H_weak': 12, 'H': 45}

| scene | H | H_weak | V | E | none_in_fov | off |
|---|---|---|---|---|---|---|
| scene01 | 0 | 0 | 24 | 0 | 0 | 24 |
| scene02 | 0 | 0 | 15 | 9 | 0 | 24 |
| scene03 | 0 | 0 | 18 | 0 | 6 | 24 |
| scene04 | 0 | 0 | 24 | 0 | 0 | 24 |
| scene05 | 0 | 0 | 24 | 0 | 0 | 24 |
| scene06 | 0 | 0 | 0 | 0 | 24 | 24 |
| scene07 | 0 | 0 | 21 | 0 | 3 | 24 |
| scene08 | 0 | 3 | 21 | 0 | 0 | 24 |
| scene09 | 15 | 3 | 6 | 0 | 0 | 24 |
| scene10 | 0 | 0 | 15 | 0 | 9 | 24 |
| scene11 | 0 | 0 | 0 | 0 | 24 | 24 |
| scene12 | 0 | 0 | 24 | 0 | 0 | 24 |
| scene13 | 0 | 0 | 0 | 0 | 24 | 24 |
| scene14 | 18 | 0 | 6 | 0 | 0 | 24 |
| scene15 | 3 | 0 | 21 | 0 | 0 | 24 |
| scene16 | 0 | 0 | 24 | 0 | 0 | 24 |
| scene17 | 9 | 3 | 12 | 0 | 0 | 24 |
| scene18 | 0 | 0 | 15 | 9 | 0 | 24 |
| scene19 | 0 | 0 | 0 | 0 | 24 | 24 |
| scene20 | 0 | 0 | 21 | 0 | 3 | 24 |
| scene21 | 0 | 0 | 21 | 3 | 0 | 24 |
| sceneC1 | 0 | 3 | 21 | 0 | 0 | 24 |
| sceneC2 | 0 | 0 | 24 | 0 | 0 | 24 |
| sceneC4 | 0 | 0 | 24 | 0 | 0 | 24 |
| sceneD1 | 0 | 0 | 24 | 0 | 0 | 24 |
| sceneD2 | 0 | 0 | 15 | 9 | 0 | 24 |
| sceneD3 | 0 | 0 | 18 | 6 | 0 | 24 |
| sceneD4 | 0 | 0 | 0 | 0 | 24 | 24 |
| sceneN1 | 0 | 0 | 0 | 0 | 24 | 24 |
| sceneN2 | 0 | 0 | 0 | 0 | 24 | 24 |
| sceneN3 | 0 | 0 | 0 | 0 | 24 | 24 |
| sceneN4 | 0 | 0 | 0 | 0 | 24 | 24 |
| sceneN5 | 0 | 0 | 0 | 0 | 24 | 24 |

## G5 V-tier depth/GT agreement — REFERENCE (below the 0.80 reference line; D19⑤: excluded from the verdict)
V frames scored: 438   mean agreement: 0.515  (reference line >= 0.80, NOT a pass/fail bar)
> fraction of GT-positive cells holding >=1 reprojected below-ground pixel.

| band | agreement | positive cells |
|---|---|---|
| 1 (0.0-2.0 m) | 0.029 | 309 |
| 2 (2.0-5.0 m) | 0.475 | 948 |
| 3a (5.0-8.0 m) | 0.595 | 1332 |
| 3b (8.0-12.0 m) | 0.696 | 1659 |
> **D19⑤ — this is a reference metric, not a gate.** A near band scoring low is expected geometry, not a labeling fault: a drop's floor right behind the lip sits in the camera's view shadow, so its cell is GT-positive with no visible below-ground surface. The pooled mean therefore tracks how much of the corpus is near-band, not how good the labels are; it is reported per band and excluded from the verdict. Judge it band by band.

## tau sensitivity (tier distribution, on-arm frames)

| tau_int | tau_edge | V | E | H | H_weak | none_in_fov |
|---|---|---|---|---|---|---|
| 1 | 0.02 | 453 | 33 | 45 | 0 | 261 |
| 1 | 0.05 | 453 | 33 | 45 | 0 | 261 |
| 1 | 0.1 | 453 | 33 | 45 | 0 | 261 |
| 50 | 0.02 | 438 | 36 | 45 | 12 | 261 |
| 50 | 0.05 | 438 | 36 | 45 | 12 | 261 |
| 50 | 0.1 | 438 | 36 | 45 | 12 | 261 |
| 200 | 0.02 | 417 | 42 | 45 | 27 | 261 |
| 200 | 0.05 | 417 | 42 | 45 | 27 | 261 |
| 200 | 0.1 | 417 | 42 | 45 | 27 | 261 |

## G4 audit overlays — 18/10 written
dir: `/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/dayrun_0820/audit_samples`
tier mix: {'V': 13, 'E': 5}
D19 split-band quota (frames positive in exactly ONE of the refined band pair — the only view that audits the new boundary): 4/4
  - `3a` positive, `3b` NOT: 2 taken of 12 such frame(s) in the whole labeled set
  - `3b` positive, `3a` NOT: 2 taken of 135 such frame(s) in the whole labeled set
D12 far-E quota (tier E and cam.d > 8.0 m): 5/4
depth-fusion rescue quota (on-arm frames of ['scene02', 'scene07', 'scene08', 'scene12', 'scene16'] rescued scene(s), 2 each): 10
stale overlays from earlier derivations removed: 0

## max_diff vs documented drop (D15)

documented drop = `Docs/reports/dropoff_cue_matrix_v1.md §1.2` headline value per scene; measured = the on-arm twin-diff `max_diff` of this run; source = which heightmap instrument the on-arm map came from (`aabb` = top-down `AabbPrefilter.ground_z`, `fused` = `fuse_heightmap.py` depth fusion).
band = measured / documented within [50%, 150%].

| scene | documented drop (m) | measured max_diff (m) | ratio | source (on/off) | verdict |
|---|---|---|---|---|---|
| scene01 | 0.6 | 0.6 | 1.00× | aabb/aabb | OK |
| scene02 | 3.38 | 3.433 | 1.02× | fused/fused | OK |
| scene03 | 3.2 | 3.2035 | 1.00× | aabb/aabb | OK |
| scene04 | 1.45 | 1.4501 | 1.00× | aabb/aabb | OK |
| scene05 | 0.398 | 1.207 | 3.03× | aabb/aabb | OK on the row's other drop (1.6 m, 0.75×) — 보울 립 0.398 m 위에 무대 −1.2/−1.6 m |
| scene06 | 5.005 | 0.0003 | 0.00× | aabb/aabb | EXPLAINED ZERO (D19⑤) — out-of-FOV (D17) |
| scene07 | 4.2 | 6.0044 | 1.43× | fused/fused | OK _(row also lists 6.0 m: 1.00×)_ |
| scene08 | 4.5 | 4.5066 | 1.00× | aabb/fused | OK |
| scene09 | 5.5 | 5.2065 | 0.95× | aabb/aabb | OK |
| scene10 | 6.6 | 4.05 | 0.61× | aabb/aabb | OK _(row also lists 2.3 m: 1.76×)_ |
| scene11 | 5.505 | 0.0005 | 0.00× | aabb/aabb | HOLD (D17 mislabel-risk) — held out of every split |
| scene12 | 1.8 | 1.3618 | 0.76× | fused/fused | OK _(row also lists 1.36 m: 1.00×)_ |
| scene13 | 3.96 | 0.0 | 0.00× | aabb/aabb | HOLD (D17 mislabel-risk) — held out of every split |
| scene14 | 6.0 | 4.23 | 0.71× | aabb/aabb | OK |
| scene15 | 4.25 | 2.21 | 0.52× | aabb/aabb | OK |
| scene16 | 3.0 | 3.8959 | 1.30× | fused/fused | OK _(row also lists 0.15 m: 25.97×)_ |
| scene17 | 3.2 | 3.2 | 1.00× | aabb/aabb | OK |
| scene18 | 2.56 | 2.56 | 1.00× | aabb/aabb | OK |
| scene19 | 1.8 | 0.0591 | 0.03× | aabb/aabb | HOLD (D17 mislabel-risk) — held out of every split _(row also lists 1.95 m: 0.03×)_ |
| scene20 | 2.1 | 2.15 | 1.02× | aabb/aabb | OK |
| scene21 | 2.7 | 2.75 | 1.02× | aabb/aabb | OK |
| sceneC1 | 2.04 | 2.042 | 1.00× | aabb/aabb | OK |
| sceneC2 | 2.24 | 2.2584 | 1.01× | aabb/aabb | OK |
| sceneC4 | 2.1 | 2.102 | 1.00× | aabb/aabb | OK |
| sceneD1 | 1.2 | 1.2 | 1.00× | aabb/aabb | OK |
| sceneD2 | 3.0 | 2.9836 | 0.99× | aabb/aabb | OK |
| sceneD3 | 0.8 | 0.8 | 1.00× | aabb/aabb | OK |
| sceneD4 | 1.15 | 0.0 | 0.00× | aabb/aabb | HOLD (D14④ — held out of every split) |
> N-scenes (sceneN1–N5) are hard negatives with no design-table drop and are omitted: zero IS their expected measurement (see the hard-negative check above).

## VERDICT

| gate | role | result | note |
|---|---|---|---|
| G1 required fields | binding | PASS | 0 frame(s) excluded |
| G2 toggle sanity | binding | PASS | 0 off-arm residual, 0 unexplained zero-positive scene(s), 1 explained, 4 held |
| G3 strict-H distribution | binding | PASS | 45 strict-H frames |
| G5 V-tier depth/GT agreement | **reference** | below the reference line | mean 0.515 vs reference line 0.80 |
| G4 audit overlays | binding | PASS | 18/10 overlays written |

**ALL BINDING GATES PASS**

> D19⑤ verdict rule: only the binding gates (G1 required fields, G2 toggle sanity, G3 strict-H distribution, G4 audit overlays) decide PASS/FAIL. G5 is a reference metric about view-shadow geometry and cannot fail a run. G2 counts a zero-positive scene as a failure only when the zero is UNEXPLAINED; scenes with a recorded physical explanation (`EXPLAINED_ZERO`) and scenes on PROVISIONAL-HOLD are reported on their own lines instead.

