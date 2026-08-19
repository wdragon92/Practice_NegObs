# GT labeling stack — order of commands

```bash
export PYTHONNOUSERSITE=1; PY=/home/vislab/miniconda3/envs/env_seg/bin/python
cd experiments/mainrun_0819/code/labeling
E=/home/vislab/Desktop/work_sy/Practice_NegObs/experiments/mainrun_0819
D=/home/vislab/Desktop/work_sy/Practice_NegObs/dataset

$PY synth_test.py                                                                  # 0. must be 52/52 green
$PY verify_reprojection.py --scene-dir $D/260819_patchprobe_on/train/<scene> --n 3  # 1. camera convention probe
$PY fuse_heightmap.py --on-round $D/260819_main_on --off-round $D/260819_main_off \
      --scenes scene02,scene07,scene08,scene12,scene16 --workers 6                 # 1b. depth-fusion heightmaps
                                                                                   #     for AABB-blind scenes only
                                                                                   #     (scene08: on-arm sidecar then deleted
                                                                                   #      -> aabb ON / fused OFF, see below)
$PY labeler.py --on-round $D/260819_main_on --off-round $D/260819_main_off \
      --grid gridspec_v0.json --out $E/annotations/labels_v0.json --workers 8      # 2. polar GT + tiers
$PY build_manifest.py --labels $E/annotations/labels_v0.json \
      --on-round $D/260819_main_on --off-round $D/260819_main_off \
      --out $E/dataset_manifest_v1.json                                            # 3. manifest
$PY gates.py --manifest $E/dataset_manifest_v1.json --labels $E/annotations/labels_v0.json \
      --out $E/GATES_REPORT.md --audit-dir $E/audit_samples                        # 4. gates + 30 overlays
                                                                                   #    also writes annotations/hold_scenes.json
$PY ../make_split.py --manifest $E/dataset_manifest_v1.json --out $E/split_v1.json \
      --report $E/SPLIT_PROPOSAL.md --exclude-scenes @$E/annotations/hold_scenes.json  # 5. split, minus held scenes
```

Camera math follows `../../CAM_CONVENTION.md` §2/§6 verbatim (= `variation_kit.dir_of` +
`look_at_rows`); step 1 confirmed it on real renders at 0.0001 m.

**Step 1b is not run for every scene.** The default heightmap is the top-down AABB ray
(`heightmap.npy`), which is complete but reads the first thing under the sky — a roof, a deck,
or a prim the hazard toggle only made invisible. `fuse_heightmap.py` re-measures a scene from
its own depth sidecars and writes `heightmap_fused.npy` beside (never over) the AABB pair;
`labeler.load_heightmap` prefers the fused file **per arm** wherever it exists and records the
choice as `hm_source` in `scene_footprint`. Fusion sees only what a camera saw, so it is the
right instrument only where the AABB is demonstrably wrong — the file's docstring carries the
per-arm rule and this round's measurements. Deleting the sidecars (`--remove`) puts a scene
back on the AABB with no other change.

**A mixed pairing (`aabb` one arm, `fused` the other) needs its own audit**, because the two
instruments do not read the same surface everywhere: the AABB ray goes through water to the bed,
depth fusion stops at the water surface, and neither sees under a roof the same way. Before
adopting one, check (a) the median `|fused − aabb|` per arm over the cells both fill, and (b) that
the cell owning `max_diff` is not a structure top — re-measure it straight off the rendered depth
of both arms and confirm no camera sees a surface far *below* the map value there. `scene08` passes
both (aabb ON / fused OFF); `scene12` and `scene16` fail them and use `fused/fused` on both arms.

Everything is keyed by sceneID (the repo `<split>/` level is ignored). All grid constants live
in `gridspec_v0.json` (`PROVISIONAL-GRID-V0`) — edit it and rerun steps 2–4 to re-derive.
`tier_strict` uses tau_int=50 / tau_edge=0.05; the full 9-combo sweep is in `tier_matrix`
and in the GATES_REPORT tau table.

## footprint v2 (D10) — what the GT is measured against

```
footprint_raw = { z_off(x,y) - z_on(x,y) >= gridspec.hazard_depth_m }     # twin heightmap diff
footprint     = components of footprint_raw whose NEAR boundary (the cell face pointing at the
                camera, walkable on the far side) sees z_on fall >= hazard_depth within
                STEP_RUN_M = 1.0 m of inward run                          # step gate
```

* The **hazard-off arm is the counterfactual walkable surface**, so ground that merely slopes
  away from the camera never enters the footprint. The retired v0 rule measured against the
  cut's own `cam.ground_z`, which turned any far downslope (N4's ramp, the s03/s04/s17
  embankments) into false positives. `approach_z` is still emitted per frame, for reference only.
* The step gate separates *fall* from *slope*: stairs (0.15–0.18 m risers) and vertical drops
  clear it, a ramp reaching −1.0 m over 8 m never does. It is applied per connected component
  and per cut (the near boundary is camera-dependent); `footprint.comps_raw/comps_kept` and
  `footprint.boundary_pass/boundary_cells` in `labels_v0.json` show its work.
* `int_px` counts reprojected pixels that land in the footprint **and** sit `INTERIOR_MARGIN_M`
  below `z_off` at that cell (nearest-cell lookup). Where `z_off` is void the cut's own
  `approach_z` is used instead and those pixels are counted apart as `raw_vis.int_px_fallback`.
* **Both arms of a scene are required.** An on-arm scene whose off twin has not rendered yet is
  SKIPPED with a warning rather than labelled against a guess — rerun step 2 once the twin lands.
* NaN in *either* arm excludes the cell from the footprint and from the lip walkable side; the
  per-frame `void_stats` now carries `void_off_*` and `void_either_*` alongside the on-arm counts.

The three tuned constants (`INTERIOR_MARGIN_M` 0.15 / `RIM_TOL_M` 0.35 / `LIP_MAX_PTS` 200) live
in one CONSTANTS block at the top of `labeler.py` with their D11 rationales; nothing repeats them
as inline literals. They are echoed into `labels_v0.json["meta"]` for provenance.

## D14 — the step gate is reversible, and doubtful scenes are held

The gate is **provisional**. Nothing it removes is thrown away, and no scene it silently zeroes
gets to reach the headline metric before a human has ruled on it.

### Preserved fields (per frame, in both `labels_v0.json` and `dataset_manifest_v1.json`)

| field | meaning |
|---|---|
| `polar_gt` | **the training GT — unchanged.** 15 cells from the GATED footprint |
| `polar_gt_pregate` | the same 15-cell wedge test run on the RAW footprint, i.e. before the step gate |
| `gate_excluded` | `{"cells": [...], "n": N}` — cells positive in `polar_gt_pregate` but not in `polar_gt` |
| `footprint.hm_cells_excluded` | heightmap cells the gate dropped on this cut (`cells_raw − cells_kept`) |

Scene level, in `labels_v0.json["scene_footprint"]`: `hm_cells_raw`, `hm_cells_excluded_min/max`
(min–max over the scene's cuts — the gate reads the camera-facing near boundary, so it is per-cut),
`n_frames_gate_excluded`, `gt_cells_excluded_sum`. Manifest `meta.gate_policy` states the contract:
`train-on-gated; pregate preserved per D14`. `polar_gt ⊆ polar_gt_pregate` holds by construction
(the kept footprint is a subset of the raw one), so `gate_excluded` is exactly the difference.

Cost: one extra wedge/bincount pass per cut, no extra IO.

### Morning revert = a field swap, NOT a re-derivation

If the morning ruling reverts the step gate, do **not** re-run the labeler. In
`dataset_manifest_v1.json` swap the two fields per frame (`polar_gt` ← `polar_gt_pregate`, keeping
the old `polar_gt` under `polar_gt_pregate` if you want the round trip), update
`meta.gate_policy`, and retrain. Everything the gate removed is already on disk — that is the whole
point of the pair. Adopting the gate needs no action at all.

### PROVISIONAL-HOLD flow (D14④)

```
annotations/extra_holds.json  ── D17 hand-written ["sceneXX", ...] ─┐
gates.py  ──G2: on-arm scene with ZERO positive frames?             │
            ├─ scene is N1–N5      → expected hard negative, listed, gate unaffected
            ├─ scene is D1–D4      → PROVISIONAL-HOLD: banner at the TOP of GATES_REPORT.md
            │                        + annotations/hold_scenes.json  (G2 still PASSes)
            └─ any other scene     → G2 FAILs, exactly as before    │
                                          hold_scenes.json = D14 holds ∪ extra_holds ←┘
make_split.py --exclude-scenes @annotations/hold_scenes.json
            → held scenes go to NO split (not train, not val, not test), are dropped from the
              eligible pool and from the global tier histogram the test set is matched against,
              and are reported under "PROVISIONAL-HOLD (아침 결재 대상)" + PROOF-10.
```

`hold_scenes.json` is **always** written (an empty `[]` when nothing is held), so its absence means
gates.py did not run — not that nothing is held. It defaults to `<manifest dir>/annotations/`;
`--hold-out` overrides it. Why D1–D4 hold instead of fail: these are the batch-1 non-stair drops
whose gate behaviour D13 promised to verify. All-negative there is a *suspected over-exclusion*,
not a design outcome, and holding the scene out already removes the contamination G2 guards
against — so the run continues unattended and the adopt/revert call stays the morning's.
`--exclude-scenes` also takes a plain comma list.

### D17 extra holds — the same list, a different reason

`--extra-holds` (default `annotations/extra_holds.json`, a JSON array of scene ids; also accepts an
inline comma list, or `none` to ignore the file) merges hand-listed scenes into the very same
PROVISIONAL-HOLD output. D14 holds a scene because a *measurement* looks wrong; D17 holds one
because a *label* is suspected wrong — a toggle that moves the camera's own ground plane, or a near
boundary outside the fused coverage. Training on those would teach that a real edge is safe, which
is worse than not training on the scene at all. gates.py cannot detect this, so the judgement is an
input file, tagged `(D17 mislabel-risk)` in the banner, in the G2 block and in the D15 verdict
column. Ids that match no scene in the manifest are ignored and named in a `**WARNING**` line.
Because a held scene leaves every split it cannot contaminate one, so — exactly as under D14④ — it
also stops counting as a G2 zero-positive failure.

## GATES_REPORT additions (D12)

* **footprint v2 per-scene summary** — comps and cells before/after the step gate, per arm, plus
  max twin-diff depth. Followed by an explicit hard-negative list: `sceneN4` must be 0 cells
  AFTER the gate, `sceneN1/N2/N3/N5` must be 0 cells RAW. Mismatches print `**FLAG**` lines —
  reported, not fatal (morning judgement: re-render vs. re-tune the gate).
* **audit stratification** — the 30 overlays now reserve >= 4 slots for tier-E frames at
  `cam.d > 8.0 m` before the usual V/E/H/off round robin; if the labeled set holds fewer, all of
  them are taken and a `**WARNING**` line says so.
* G2's "on-arm scenes with ZERO positive frames" check excludes the declared hard negatives
  (N1–N5): zero GT is their design (D9 note ④), and under v2 sceneN4 finally reaches it.
* **STEP-GATE EXCLUSIONS (D14)** — one row per scene/arm: hm cells raw / kept / excluded, how many
  of the scene's frames lost at least one GT cell, and the total GT cells excluded. Copy this table
  into STATUS.md (D14③). `gates.py` also prints its totals and the hold list to stdout.
