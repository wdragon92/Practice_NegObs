# ctrl_dressing — the appearance-preserving OFF arm (C2 track, DECISIONS **D25**)

**Question.** `sceneC2`'s off arm fires on 21/24 frames at p ≈ 0.8–0.98 with no drop anywhere in
the walking surface (DIAG_V1 §3.2: largest descent 16 mm = 5.5 % of the 0.30 m threshold), and
`sceneN3` behaves the same way by design. But the off arm of both scenes also deleted the scene's
*dressing* — C2's leaf mound and its one railing line, N3's mural — so those frames cannot be
quoted as "same picture, hazard removed". This round renders an off arm that removes **only the
hazard geometry** and leaves the dressing where the on arm put it, so the false-alarm rate can be
read as a dressing response or not, with the twin pose held byte-identical.

Scope: two scenes, one arm, 48 cuts, a new directory. Nothing existing is written to.

---

## One command

```bash
bash experiments/nightrun_0820/ctrl_dressing/run_ctrl_dressing.sh && \
bash experiments/nightrun_0820/ctrl_dressing/run_ctrl_eval.sh
```

The first needs the GPU (`flock /tmp/negobs_gpu.lock`, one hold per scene invocation, ≈6–8 min of
GPU time); the second takes one short GPU hold per seed for inference and is CPU for the rest.
Both resume: completed cuts and completed steps are no-ops.

Before the render (already done once, re-run only if the frozen rounds legitimately change):

```bash
python3 experiments/nightrun_0820/ctrl_dressing/hash_gate.py snapshot   # CPU, ~1 s
```

---

## The scene patch (opt-in, `keep_dressing`)

`SCENE_CONFIG["keep_dressing"]`, absent/False by default, in
`scenes/batch1/sceneC2_leaf_stairs.py` and `scenes/batch1/sceneN3_trompe_loeil.py`. With the flag
absent **both existing arms are byte-identical to their pre-patch selves** — every new expression
is written as `X if KEEP_DRESSING else <the old value>` and the whole audit surface is
`grep KEEP_DRESSING`. The flag is legal only with the hazard key False; a contradictory config
raises `SystemExit` at module scope, before Isaac boots, so the arm can never render 24 cuts and
be discovered later in a metrics table.

**sceneC2** — removed: the 14-step stair, its coping, the descending side slopes and the −2.24 m
lower ground, replaced by a flat continuation of the approach at z = 0 built from the *same* prim
vocabulary, materials and mowing bands (`build_terrain(M, flat=True)`). Kept, at their on-arm
transforms: leaf mounds A/B/C, the two side drifts, the leaf-bank end sections, the ~1 800-instance
leaf scatter (now laid on the fill instead of on the deleted stair profile) and the one railing
line. Everything the on arm anchors to the lower ground (far trees, far hedges, ridges; the park
props and the lower-walk joints already did this) rides the fill at z = 0, so nothing sinks.

*The railing keeps its on-arm transform, which means it descends into the fill and is swallowed
by it at x ≈ 2.2 m.* That is the intended stimulus, not a defect: the railing is the scene's only
surviving drop cue (module docstring), and the control asks what the model does when the cue is
present and the drop is not.

**sceneN3** — this scene has no hazard geometry at all: every prim is planar and the "drop" is
1 mm of paint, so "remove only the hazard geometry" removes nothing and the arm is structurally
the on arm carrying the off label. That is deliberate: it isolates the painted-cue/dressing
response, and it doubles as a **null control** for the twin machinery (its twin Δ should be ≈ 0).
The scene prints this in full whenever the flag is on.

## The datum argument (the D17/D20 trap, and why the new poses pair exactly)

The camera's ground reference is `gz = pre.ground_z(-s["d"], s["y"])` and the eye is
`(-d, y, gz + h_rel)` (`run_data_render.py`:458, 497). `ground_z` is a downward ray from z = 60 m
against **prim AABBs** (`variation_kit.py`:781–785), so it returns the top of the highest AABB
covering that column. The sampler draws `d ∈ [1.2, 12] m` (log-uniform) and `|y| ≤ 0.90 m`
(truncated normal) — `CAM_DIST`, `variation_kit.py`:574–581 — so **every camera in this corpus
stands at x = −d < 0**: strictly upstream of the drop edge, inside the walk corridor.

In that strip the new arm builds *the same statements* as the on arm: `UpperPath` (skin-excluded,
top exactly 0.000), the upper lawns (which stop at |y| ≥ 1.62 and never cross the corridor),
`LeafMound_A` (AABB top 0.130 over x ∈ [−3.20, −0.10]) and the ground-kit joints. Hence
`ground_z(−d, y)` returns exactly the on arm's value for every draw — measured on the main round:
0.130 for the 12 cuts with d ≤ 3.20 and 0.000 for the 12 with d > 3.20 — and with the same seed
(20260819) driving `d/h_rel/yaw/pitch/roll/hfov`, the entire `cam` dict is identical.

What the **old** off arm did instead: `build_flat_fill` lays lawn slabs spanning |y| ≤ 40 m, i.e.
straight through the walk corridor, and those slabs take the ground displacement skin (+16 mm).
That slab — not the deleted mound — is what set the old arm's `ground_z` to 0.0163/0.0164 m on
all 24 cuts and excluded sceneC2 from the twin analysis entirely (D20, DIAG_V1 §3.3). The new
branch therefore does **not** call `build_flat_fill`.

Consequence: the new pairs match at tolerance 0, not at D20's 0.15 m. The eval still runs
`--tol 0.15` on both arms so the old/new comparison is like for like.

## The gate

`hash_gate.py verify` (run automatically at the end of the render script and again as step 0 of
the eval script) must exit 0 before any number is quoted:

| check | what it asserts |
|---|---|
| immutability | every file of `260819_main_{on,off}` and `260820_boost_*` has its recorded size + mtime_ns, a 41–167-file sha256 sample per round matches, and no file was added or removed |
| twin pose | for all 24 cuts of each scene the full `cam` dict of the ctrl round equals the on arm's, `ground_z` and `eye` included; seed is 20260819 |
| C2 geometry | camera datum strip (x < 0, \|y\| ≤ 0.90) equals the on arm to 1e-6 · the rest of x < 0 differs only in the coping band (\|y\| ≥ 1.28, x ≥ −0.25) · mound-B footprint equals the on arm · a bump ≥ 0.05 m survives at the crest · every cell of the on arm's footprint is above −0.30 m and, inside the walked strip, within 0.05 m of the datum · no cell below −0.30 m anywhere · max local drop in a 1.0 m window < 0.30 m |
| N3 geometry | the height map equals the on arm's exactly (nothing structural changed) |

Validated on CPU before the render: the rules **fail** on the old off arm (4 of 8 C2 rows, the
N3 row) and **pass** on an analytically reconstructed new arm.

Height-map semantics worth remembering when reading the log: it is AABB-based, so the mound-B
columns read **+0.200 m** (the plate's declared crest, its AABB top) in *both* arms, while the
analytic leaf surface at x = 0 is +0.084 m. The gate asserts equality with the on arm rather than
a literal 0.084.

## The evaluation

`run_ctrl_eval.sh`: labeler v2 over the pair (`--on-round 260819_main_on --off-round
260820_ctrloff --scenes sceneC2,sceneN3`; `scene_dirs` keys by scene and ignores the split
subdirectory, so the two rounds' different layouts — C2 under `val/`, N3 under `train/` — do not
matter) → `build_manifest` → `sync_on_arm.py` (reports and then restores the published ON-arm
labels, so both off arms are scored against the same on arm) → RGB **v2, seeds 42/43/44**
(`experiments/dayrun_0820/runs/v2/rgb_s{42,43,44}/best.pt`; both scenes are *test* scenes in
`split_v2_full.json`, so this is out of sample) → `split_per_frame` → `twin_analysis --tol 0.15`
→ `ctrl_table.py`.

The **old** off arm is not re-inferred: its rows are filtered out of the frozen
`runs/v2/rgb_s*/eval_test/per_frame.csv` and fed back through `eval_polar --per-frame-a`, which
reuses the published probabilities and still produces the full metric bundle on CPU.

Reference numbers already recomputed from the frozen rows (seed 42, τ = 0.5, these two scenes
only) so the new table has something to land against:

| scene | old-off FA_frame | cells/frame | mean max p | twin Δ_frame | Δ_score |
|---|---|---|---|---|---|
| sceneC2 | 0.208 | 0.25 | 0.228 | 0.476 | 0.481 |
| sceneN3 | 1.000 | 5.00 | 0.915 | 0.031 | n/a (hard negative: no GT-positive cell) |

## Files

| file | role |
|---|---|
| `run_ctrl_dressing.sh` | the round: preflight (patch present · config valid · `NEGOBS_SMOKE` parse gate) → flocked render of 48 cuts into `dataset/260820_ctrloff/` → hash gate |
| `hash_gate.py` | `snapshot` / `verify`; renders nothing; exit 0 = evaluation may proceed |
| `run_ctrl_eval.sh` | gate → label → manifest → 3-seed eval → twin → table |
| `sync_on_arm.py` | freezes the ON-arm labels in the control manifest, reporting any drift |
| `ctrl_table.py` | writes `CTRL_TABLE.md` + `ctrl_numbers.json` (old vs new, per scene, per seed) |
| `render_configs/scene{C2,N3}_ctrloff.json` | `{"hazard_stairs": false, "keep_dressing": true}` |
| `baseline_frozen_rounds.json` | the pre-render immutability snapshot (10 rounds, 7 099 files) |
| `logs/` | `render.log`, `eval.log` |

## Risks and stop rules

* **60-minute rule** (brief §4 C2 fallback). If the render or the gate is not through in 60 min,
  stop, record the cause, and carry the track to the next day cycle. Nothing here is required by
  the headline table.
* If the gate fails, do **not** evaluate. A failing datum row means the poses no longer pair and
  the whole point of the round is gone.
* The new arm differs from the old one in three ways at once (mound + railing restored, leaf
  scatter laid on the fill rather than sunk under it, lower dressing riding the fill instead of
  sunk 2.24 m). The table therefore measures "dressing preserved" as a package, not any one of
  the three. Say so when the number is quoted.
* `sceneN3`'s new off arm is structurally the on arm. Its FA number is meaningful; its twin Δ is
  a null control and must not be read as evidence of anything about hazards.
* Both scenes are in `test`, so this cannot contaminate training; but the round is also **not**
  part of `_v2_full` and must not be merged into it.
